from __future__ import annotations

import importlib.util
import json
import os
import plistlib
import contextlib
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

SCRIPT = Path(__file__).resolve().parents[1] / "skills/product-qa/scripts/agent_qa.py"


def module():
    spec = importlib.util.spec_from_file_location("product_qa", SCRIPT)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def profile():
    return {"kind": "tormie", "server": "https://qa.example.invalid", "email": "qa@example.invalid",
            "expected_user_id": "b0eac527-cd5d-4b2c-9326-7ac44b8e925a", "bundle_id": "com.example.qa",
            "simulator_id": "c13bb6b9-b688-4d88-8b20-eaf15f72cd50",
            "credential": {"service": "com.example.qa", "account": "qa@example.invalid"}}


class ProductQATests(unittest.TestCase):
    def test_implementation_exists(self):
        self.assertTrue(SCRIPT.is_file(), "shared entry is not implemented")

    def setUp(self):
        if not SCRIPT.exists():
            if self._testMethodName == "test_implementation_exists":
                return
            self.skipTest("implementation not present yet")
        self.qa = module()

    def test_rejects_redirect_origins_and_plaintext_profile_secrets(self):
        for change in ({"server": "https://qa.example.invalid/?token=x"},
                       {"server": "http://qa.example.invalid"}, {"password": "must-not-be-stored"}):
            p = {**profile(), **change}
            with self.assertRaises(self.qa.QAError):
                self.qa.validate_profile(p)

    def test_foreign_identity_is_rejected_and_new_session_is_revoked(self):
        calls = []
        def transport(path, body=None, headers=None):
            calls.append(path)
            if path.endswith("login"):
                return 200, {"user": {"id": profile()["expected_user_id"], "email": "foreign@example.invalid"}, "access_token": "temporary-token"}
            return 200, {}
        with self.assertRaises(self.qa.QAError):
            self.qa.check_credentials(profile(), "transient-secret", transport)
        self.assertEqual(["/api/v1/auth/email/login", "/api/v1/auth/logout"], calls)

    def test_failed_session_readback_is_not_success_and_is_cleaned_up(self):
        calls = []
        user = {"id": profile()["expected_user_id"], "email": profile()["email"]}
        def transport(path, body=None, headers=None):
            calls.append(path)
            if path.endswith("login"): return 200, {"user": user, "access_token": "temporary-token"}
            if path.endswith("session"): return 503, {}
            return 200, {}
        with self.assertRaises(self.qa.QAError):
            self.qa.check_credentials(profile(), "transient-secret", transport)
        self.assertEqual("/api/v1/auth/logout", calls[-1])

    def test_success_receipt_contains_no_secret_or_token(self):
        user = {"id": profile()["expected_user_id"], "email": profile()["email"]}
        def transport(path, body=None, headers=None):
            if path.endswith("login"): return 200, {"user": user, "access_token": "temporary-token"}
            if path.endswith("session"): return 200, {"user": user}
            return 200, {}
        result = self.qa.check_credentials(profile(), "transient-secret", transport)
        self.assertEqual(user["id"], result["user_id"])
        self.assertNotIn("transient-secret", json.dumps(result))
        self.assertNotIn("temporary-token", json.dumps(result))

    def test_ui_password_uses_stdin_and_failure_does_not_echo_tool_output(self):
        commands = []
        def run(args, **kwargs):
            commands.append((args, kwargs))
            class Result:
                returncode = 1
                stdout = "transient-secret"
                stderr = "transient-secret"
            return Result()
        with patch.object(self.qa.subprocess, "run", side_effect=run):
            with self.assertRaises(self.qa.QAError) as caught:
                self.qa.UI("device", "axe").type_secret("transient-secret")
        self.assertNotIn("transient-secret", repr(commands[0][0]))
        self.assertEqual("transient-secret", commands[0][1]["input"])
        self.assertNotIn("transient-secret", str(caught.exception))

    def test_interrupted_boot_is_not_replayed_but_recorded_failure_can_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"watch.json";state=self.qa.WatchState(path)
            state.begin("device","boot",now=100)
            self.assertFalse(self.qa.WatchState(path).due("device","boot",now=1000))
            state.record("device","boot",False,now=200)
            self.assertTrue(self.qa.WatchState(path).due("device","boot",now=600))
            self.assertEqual(1,state.data["device"]["attempts"])

    def test_native_fingerprint_frames_paths_and_file_contents(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=Path(tmp)/"Example.app";app.mkdir();binary=app/"Example";binary.write_bytes(b"binary")
            (app/"a").write_bytes(b"bc");before=self.qa.native_digest(binary)
            (app/"a").unlink();(app/"ab").write_bytes(b"c")
            self.assertNotEqual(before,self.qa.native_digest(binary))

    def test_native_fingerprint_detects_repointed_directory_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=Path(tmp)/"Example.app";app.mkdir();binary=app/"Example";binary.write_bytes(b"binary")
            for name in ("one","two"):(app/name).mkdir();(app/name/"config").write_text(name)
            link=app/"active";link.symlink_to("one",target_is_directory=True);before=self.qa.native_digest(binary)
            link.unlink();link.symlink_to("two",target_is_directory=True)
            self.assertNotEqual(before,self.qa.native_digest(binary))
            link.unlink();link.symlink_to(Path(tmp),target_is_directory=True)
            with self.assertRaises(self.qa.QAError):self.qa.native_digest(binary)

    def test_device_identity_is_case_insensitive_and_foreign_boot_policy_applies(self):
        selected=profile()["simulator_id"]
        self.assertTrue(self.qa.same_device(selected,selected.upper()))
        inventory=[{"udid":selected.upper(),"state":"Booted"},{"udid":"22222222-2222-4222-8222-222222222222","state":"Booted"}]
        with self.assertRaises(self.qa.QAError):self.qa.enforce_device_policy({},inventory,selected)
        self.qa.enforce_device_policy({"allow_other_booted_devices":True},inventory,selected)

    def test_pause_waits_for_admitted_monitor_but_keeps_foreground_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);lock=root/"lock";lock.write_text("123")
            running=Mock(returncode=0,stdout=str(SCRIPT.resolve())+" watch --once")
            with patch.object(self.qa.subprocess,"run",side_effect=[running,Mock(returncode=1,stdout="")]),patch.object(self.qa.time,"sleep") as sleep:
                self.qa.pause_monitor({"lock_file":str(lock)},root)
            sleep.assert_called_once();self.assertTrue((root/"paused").exists())
            with patch.object(self.qa.subprocess,"run",return_value=Mock(returncode=0,stdout=str(SCRIPT.resolve())+" open example")),patch.object(self.qa.time,"sleep") as sleep:
                self.qa.pause_monitor({"lock_file":str(lock)},root)
            sleep.assert_not_called()

    def test_pause_waits_for_watcher_started_through_managed_launcher(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);lock=root/"lock";lock.write_text("123");launcher=root/".local/bin/agent-qa";launcher.parent.mkdir(parents=True);launcher.symlink_to(SCRIPT)
            running=Mock(returncode=0,stdout=str(launcher)+" watch --once")
            with patch.object(self.qa.Path,"home",return_value=root),patch.object(self.qa.subprocess,"run",side_effect=[running,Mock(returncode=1,stdout="")]),patch.object(self.qa.time,"sleep") as sleep:
                self.qa.pause_monitor({"lock_file":str(lock)},root)
            sleep.assert_called_once()

    def test_relative_state_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"config.json";self.qa.private_json(path,{"schema_version":1,"state_dir":"relative","projects":{"example":profile()}})
            with self.assertRaises(self.qa.QAError):self.qa.load_config(path)

    def test_gui_request_binding_rejects_an_alternate_client_configuration(self):
        with tempfile.TemporaryDirectory() as tmp:
            config={"state_dir":tmp,"projects":{"example":profile()}};rid=str(self.qa.uuid.uuid4());p=Path(tmp)/"requests"/(rid+".json")
            self.qa.private_json(p,{"id":rid,"action":"open","project":"example","created_at":self.qa.time.time(),"config_digest":"foreign"})
            with patch.object(self.qa,"open_project") as opened:self.qa.serve_requests(config)
            opened.assert_not_called();self.assertFalse(json.loads((Path(tmp)/"results"/p.name).read_text())["ok"])

    def test_gui_completed_request_is_not_replayed_after_client_consumes_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            config={"state_dir":tmp,"projects":{"example":profile()}};rid=str(self.qa.uuid.uuid4());p=Path(tmp)/"requests"/(rid+".json");item={"id":rid,"action":"open","project":"example","created_at":self.qa.time.time(),"config_digest":self.qa.config_digest(config)}
            self.qa.private_json(p,item)
            with patch.object(self.qa,"open_project",return_value={"project":"example"}) as opened:self.qa.serve_requests(config)
            opened.assert_called_once();(Path(tmp)/"results"/p.name).unlink();self.qa.private_json(p,item)
            with patch.object(self.qa,"open_project") as opened:self.qa.serve_requests(config)
            opened.assert_not_called();self.assertFalse(p.exists())

    def test_watch_state_survives_restarts_and_requires_new_boot(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "watch.json"
            state = self.qa.WatchState(path)
            self.assertTrue(state.due("device", "boot-a", now=100))
            state.record("device", "boot-a", success=True, now=100)
            state = self.qa.WatchState(path)
            self.assertFalse(state.due("device", "boot-a", now=200))
            self.assertTrue(state.due("device", "boot-b", now=201))

    def test_watch_failure_is_bounded_and_cools_down(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = self.qa.WatchState(Path(tmp) / "watch.json")
            state.record("device", "boot-a", success=False, now=100)
            self.assertFalse(state.due("device", "boot-a", now=110))
            self.assertTrue(state.due("device", "boot-a", now=500))
            state.record("device", "boot-a", success=False, now=500)
            state.record("device", "boot-a", success=False, now=900)
            self.assertFalse(state.due("device", "boot-a", now=2000))

    def test_installed_apps_accepts_simctl_plist_not_an_unsupported_json_flag(self):
        raw = plistlib.dumps({"com.example.qa": {"CFBundleVersion": "7"}}).decode()
        with patch.object(self.qa, "command", return_value=raw) as run:
            self.assertEqual("7", self.qa.installed_apps("device")["com.example.qa"]["CFBundleVersion"])
        self.assertEqual(["xcrun", "simctl", "listapps", "device"], run.call_args.args[0])

    def test_malformed_success_response_still_cleans_up(self):
        calls = []
        def transport(path, body=None, headers=None):
            calls.append(path)
            return (200, {"user": ["unexpected"]}) if path.endswith("login") else (200, {})
        with self.assertRaises(self.qa.QAError):
            self.qa.check_credentials(profile(), "transient-secret", transport)
        self.assertEqual("/api/v1/auth/logout", calls[-1])

    def test_login_suggestion_cannot_prove_native_identity(self):
        self.assertFalse(self.qa.visible_email([{"type": "Button", "AXLabel": "Continue as qa@example.invalid"}], "qa@example.invalid"))

    def test_native_identity_must_be_inside_the_authenticated_scope(self):
        items = [{"type": "Group", "AXUniqueId": "account", "_path": 1, "_parents": []},
                 {"type": "StaticText", "AXLabel": "qa@example.invalid", "_path": 2, "_parents": [1]}]
        self.assertTrue(self.qa.visible_email(items, "qa@example.invalid", {"id": "account"}))
        items[1]["_parents"] = []
        self.assertFalse(self.qa.visible_email(items, "qa@example.invalid", {"id": "account"}))

    def test_pinned_native_build_refuses_replacement_before_credential_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "app"
            binary.write_bytes(b"unexpected replacement")
            with self.assertRaises(self.qa.QAError):
                self.qa.verify_native_binding({**profile(), "native_binding": {"sha256": "0" * 64, "origin": profile()["server"]}}, binary)

    def test_debug_dylib_change_invalidates_a_pinned_native_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = Path(tmp) / "Example.app"; app.mkdir()
            binary = app / "Example"; binary.write_bytes(b"fixed loader")
            dylib = app / "Example.debug.dylib"; dylib.write_bytes(b"reviewed code")
            p = {**profile(), "native_binding": {"sha256": self.qa.native_digest(binary), "origin": profile()["server"]}, "launch_env": {"TORMIE_SERVICE_URL": profile()["server"]}}
            self.qa.verify_native_binding(p, binary)
            dylib.write_bytes(b"replacement code")
            with self.assertRaises(self.qa.QAError): self.qa.verify_native_binding(p, binary)

    def test_watcher_rechecks_manual_success_after_lock_acquisition(self):
        with tempfile.TemporaryDirectory() as tmp:
            qa = self.qa
            p = {**profile(), "watch_boot": True}
            config = {"state_dir": tmp, "default_project": "example", "projects": {"example": p}}
            class Lock:
                def __init__(self, *args): pass
                def __enter__(self): qa.WatchState(Path(tmp) / "watch.json").record(p["simulator_id"], "boot-a", True)
                def __exit__(self, *args): pass
            class Completed: returncode = 1
            with patch.object(qa, "SharedLock", Lock), patch.object(qa.subprocess, "run", return_value=Completed()), patch.object(qa, "devices", return_value=[{"udid": p["simulator_id"], "state": "Booted"}]), patch.object(qa, "boot_identity", return_value="boot-a"), patch.object(qa, "open_project") as opened:
                self.assertEqual([], qa.watch_once(config))
                opened.assert_not_called()

    def test_authenticated_button_scope_does_not_include_other_windows(self):
        items = [{"type": "Group", "_path": 1, "_parents": []},
                 {"type": "Button", "AXLabel": "Sign out", "_path": 2, "_parents": [1]},
                 {"type": "StaticText", "AXLabel": "qa@example.invalid", "_path": 3, "_parents": [1]}]
        self.assertTrue(self.qa.visible_email(items, "qa@example.invalid", {"label": "Sign out", "type": "Button"}))
        items[2]["_parents"] = [4]
        self.assertFalse(self.qa.visible_email(items, "qa@example.invalid", {"label": "Sign out", "type": "Button"}))

    def test_foreign_account_email_outranks_expected_email_in_background_content(self):
        items=[{"type":"Group","_path":1,"_parents":[]},{"type":"Group","_path":2,"_parents":[1]},
               {"type":"Button","AXLabel":"Account action","_path":3,"_parents":[1,2]},
               {"type":"StaticText","AXLabel":"private@example.invalid","_path":4,"_parents":[1,2]},
               {"type":"StaticText","AXLabel":"qa@example.invalid","_path":5,"_parents":[1]}]
        self.assertFalse(self.qa.visible_email(items,"qa@example.invalid",{"label":"Account action","type":"Button"}))

    def test_account_container_with_conflicting_static_emails_is_rejected(self):
        items=[{"type":"Group","AXUniqueId":"account","_path":1,"_parents":[]},
               {"type":"StaticText","AXLabel":"private@example.invalid","_path":2,"_parents":[1]},
               {"type":"StaticText","AXLabel":"qa@example.invalid","_path":3,"_parents":[1]}]
        self.assertFalse(self.qa.visible_email(items,"qa@example.invalid",{"id":"account"}))

    def test_gui_worker_only_accepts_registered_actions_and_cleans_its_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            request_id = "a7e89431-ab51-43fe-9c68-c03b2d2a184d"
            path = Path(tmp) / "requests" / (request_id + ".json")
            self.qa.private_json(path, {"id": request_id, "action": "shell", "project": "example", "created_at": self.qa.time.time()})
            self.qa.serve_requests({"state_dir": tmp, "projects": {"example": profile()}})
            result = json.loads((Path(tmp) / "results" / path.name).read_text())
            self.assertFalse(result["ok"])
            self.assertFalse(path.exists())

    def test_gui_worker_quarantines_corrupt_requests_instead_of_restarting_forever(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "requests" / "invalid.json"
            path.parent.mkdir(); path.write_text("invalid json"); path.chmod(0o600)
            self.qa.serve_requests({"state_dir": tmp, "projects": {"example": profile()}})
            self.assertFalse(path.exists())
            self.assertTrue((Path(tmp) / "rejected" / path.name).exists())

    def test_gui_worker_drains_unexpected_queue_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "requests" / "interrupted.json.123.tmp"
            path.parent.mkdir(); path.write_text("partial write"); path.chmod(0o600)
            self.qa.serve_requests({"state_dir": tmp, "projects": {"example": profile()}})
            self.assertFalse(path.exists())
            self.assertTrue((Path(tmp) / "rejected" / path.name).exists())

    def test_wrapped_swiftui_control_is_disambiguated_by_type(self):
        items=[{"AXUniqueId":"avatar","type":"Group"},{"AXUniqueId":"avatar","type":"Button","enabled":True}]
        ui=self.qa.UI("device")
        self.assertEqual("Button",ui.find({"id":"avatar"},items)["type"])
        with patch.object(ui,"tree",return_value=items),patch.object(self.qa,"command") as run,patch.object(self.qa.time,"sleep"):
            ui.tap({"id":"avatar"})
        self.assertIn("--element-type",run.call_args.args[0])
        self.assertIn("Button",run.call_args.args[0])

    def test_first_boot_accessibility_bridge_is_allowed_to_become_ready(self):
        ui=self.qa.UI("device")
        with patch.object(self.qa,"command",side_effect=[self.qa.QAError("accessibility not ready"),'[{"type":"Application","AXLabel":"Example"}]']) as run,patch.object(self.qa.time,"sleep"):
            self.assertEqual("Example",ui.tree()[0]["AXLabel"])
        self.assertEqual(2,run.call_count)

    def test_account_navigation_retries_a_dismissed_startup_menu(self):
        ui=self.qa.UI("device");state={"attempts":0}
        def steps(_):state["attempts"]+=1
        def tree():return [{"AXUniqueId":"account","type":"Group"}] if state["attempts"]>=2 else []
        route={"identity_anchor":{"id":"account"},"email_field":{"id":"email"}}
        with patch.object(ui,"steps",side_effect=steps),patch.object(ui,"tree",side_effect=tree),patch.object(self.qa.time,"sleep"):
            ui.navigate_account([],route)
        self.assertEqual(2,state["attempts"])

    def test_remote_shell_can_discover_user_installed_build_helpers(self):
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp);tool=home/".local/bin/dev-ios-session";tool.parent.mkdir(parents=True);tool.write_text("#!/bin/sh\nexit 0\n");tool.chmod(0o755)
            with patch.object(self.qa.shutil,"which",return_value=None),patch.object(self.qa.Path,"home",return_value=home):
                self.assertEqual(str(tool),self.qa.find_helper("dev-ios-session"))

    def test_project_regeneration_preserves_the_existing_generated_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);project=root/"Example.xcodeproj";project.mkdir();(project/"project.pbxproj").write_text("original project")
            artifact=root/"artifact";artifact.mkdir();spec=root/"project.yml";spec.write_text("name: Example\n")
            def regenerate(args, **kwargs): (project/"project.pbxproj").write_text("regenerated project")
            with patch.object(self.qa,"find_helper",return_value="xcodegen"),patch.object(self.qa,"command",side_effect=regenerate):
                self.qa.generate_project({"project":str(project),"generate_spec":str(spec)},artifact)
            self.assertEqual("original project",(artifact/"original-project.xcodeproj/project.pbxproj").read_text())
            self.assertEqual("regenerated project",(project/"project.pbxproj").read_text())

    def test_registered_package_cache_uses_only_committed_versions(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact=Path(tmp);private=self.qa.private_json
            private(artifact/"build-intent.json",{"project":"example","bundle_id":profile()["bundle_id"],"source_project":"/source/Example.xcodeproj"})
            config={"projects":{"example":{**profile(),"build":{"project":"/source/Example.xcodeproj","scheme":"Example","package_cache":"/verified/packages"}}}}
            with patch.object(self.qa,"find_helper",return_value="session"),patch.object(self.qa.subprocess,"run",return_value=Mock(returncode=0)),patch.object(self.qa,"generate_project"),patch.object(self.qa.subprocess,"call",return_value=0) as call:
                self.qa.perform_native_build(config,"example",artifact)
            args=call.call_args.args[0]
            self.assertIn("-onlyUsePackageVersionsFromResolvedFile",args)
            self.assertIn("-skipPackageUpdates",args)
            self.assertEqual("system",args[args.index("-scmProvider")+1])
            self.assertEqual("/verified/packages",args[args.index("-packageCachePath")+1])

    def test_build_timeout_allows_the_owned_session_to_cleanup(self):
        process=Mock();process.wait.side_effect=[self.qa.subprocess.TimeoutExpired(["session"],1),0]
        with patch.object(self.qa.subprocess,"Popen",return_value=process):
            with self.assertRaises(self.qa.QAError):self.qa.run_native_build(["session"],{},None,1)
        process.terminate.assert_called_once()
        process.kill.assert_not_called()

    def test_build_keeps_reservation_owner_when_cleanup_is_still_pending(self):
        process=Mock();process.wait.side_effect=[self.qa.subprocess.TimeoutExpired(["session"],1),self.qa.subprocess.TimeoutExpired(["session"],30)]
        with patch.object(self.qa.subprocess,"Popen",return_value=process):
            with self.assertRaises(self.qa.QAError):self.qa.run_native_build(["session"],{},None,1)
        process.kill.assert_not_called()

    def test_failed_build_reservation_cannot_regenerate_shared_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);project=root/"Example.xcodeproj";project.mkdir();artifact=root/"artifact";artifact.mkdir()
            config={"projects":{"example":{**profile(),"build":{"project":str(project),"scheme":"Example","generate_spec":str(root/"project.yml")}}},"lock_file":str(root/"custom.lock"),"state_dir":str(root/"state")}
            with patch.object(self.qa,"find_helper",side_effect=lambda n:"/mock/"+n),patch.object(self.qa,"command",return_value=str(artifact)),patch.object(self.qa,"generate_project") as generated,patch.object(self.qa,"run_native_build",return_value=1) as run:
                with self.assertRaises(self.qa.QAError):self.qa.build_project(config,root/"config.json","example",profile()["server"])
            generated.assert_not_called()
            self.assertEqual(config["lock_file"],run.call_args.args[1]["IOS_AUTOMATION_LOCK_FILE"])

    def test_xcode_metadata_probe_is_not_an_active_build(self):
        class Result:
            returncode=0
            def __init__(self,stdout):self.stdout=stdout
        with patch.object(self.qa.subprocess,"run",side_effect=[Result("123\n"),Result("/Applications/Xcode.app/Contents/Developer/usr/bin/xcodebuild -version")]):
            self.assertFalse(self.qa.active_builds())

    def test_real_xcode_test_still_reserves_the_machine(self):
        class Result:
            returncode=0
            def __init__(self,stdout):self.stdout=stdout
        with patch.object(self.qa.subprocess,"run",side_effect=[Result("123\n"),Result("/Applications/Xcode.app/Contents/Developer/usr/bin/xcodebuild test -scheme Example")]):
            self.assertTrue(self.qa.active_builds())

    def test_completed_zombie_xcode_process_does_not_block_entry(self):
        class Result:
            returncode=0
            def __init__(self,stdout):self.stdout=stdout
        with patch.object(self.qa.subprocess,"run",side_effect=[Result("123\n"),Result("Z (xcodebuild)")]):
            self.assertFalse(self.qa.active_builds())

    def test_opt_in_allows_only_other_device_tests_without_building(self):
        class Result:
            returncode=0
            def __init__(self,stdout):self.stdout=stdout
        other="S xcodebuild test-without-building -destination id=22222222-2222-4222-8222-222222222222"
        with patch.object(self.qa.subprocess,"run",side_effect=[Result("123\n"),Result(other)]):
            self.assertFalse(self.qa.active_builds(profile()["simulator_id"],True))
        same="S xcodebuild test-without-building -destination id="+profile()["simulator_id"]
        with patch.object(self.qa.subprocess,"run",side_effect=[Result("123\n"),Result(same)]):
            self.assertTrue(self.qa.active_builds(profile()["simulator_id"],True))
        with patch.object(self.qa.subprocess,"run",side_effect=[Result("123\n"),Result(other.replace("test-without-building","build"))]):
            self.assertTrue(self.qa.active_builds(profile()["simulator_id"],True))

    def test_other_device_opt_in_rejects_a_second_ambiguous_destination(self):
        other="S xcodebuild test-without-building -destination id=22222222-2222-4222-8222-222222222222 -destination platform=iOS Simulator,name=Agent QA"
        with patch.object(self.qa.subprocess,"run",side_effect=[Mock(returncode=0,stdout="123\n"),Mock(returncode=0,stdout=other)]):
            self.assertTrue(self.qa.active_builds(profile()["simulator_id"],True))

    def test_close_only_shuts_down_registered_qa_devices(self):
        selected=profile()["simulator_id"]
        config={"projects":{"example":profile()},"allow_other_simulator_tests":True}
        inventory=[{"udid":selected,"state":"Booted"},{"udid":"22222222-2222-4222-8222-222222222222","state":"Booted"}]
        with patch.object(self.qa,"SharedLock",return_value=contextlib.nullcontext()),patch.object(self.qa,"devices",return_value=inventory),patch.object(self.qa,"command") as run:
            self.qa.close_devices(config)
        run.assert_called_once_with(["xcrun","simctl","shutdown",selected],timeout=120)

    def test_qa_signing_assigns_an_isolated_keychain_group(self):
        original={"keychain-access-groups":["FOREIGN.production"],"com.apple.security.application-groups":["group.example.qa"]}
        result=self.qa.qa_entitlements("com.example.qa",original)
        self.assertEqual("com.example.qa",result["application-identifier"])
        self.assertEqual(["com.example.qa"],result["keychain-access-groups"])
        self.assertNotIn("com.apple.application-identifier",result)
        self.assertNotIn("com.apple.developer.team-identifier",result)
        self.assertEqual(original["com.apple.security.application-groups"],result["com.apple.security.application-groups"])
        self.assertEqual(["FOREIGN.production"],original["keychain-access-groups"])

    def test_prepare_refuses_an_unreviewed_server_before_copying_a_build(self):
        with self.assertRaises(self.qa.QAError):
            self.qa.prepare_build({"projects":{"example":profile()}},Path("unused"),"example",Path("missing.app"),"https://foreign.example.invalid")

    def test_prepare_never_signs_a_physical_device_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            app=Path(tmp)/"Example.app";app.mkdir()
            (app/"Info.plist").write_bytes(plistlib.dumps({"CFBundleIdentifier":"com.example.qa","DTPlatformName":"iphoneos"}))
            with patch.object(self.qa,"command") as run:
                with self.assertRaises(self.qa.QAError):self.qa.prepare_build({"projects":{"example":profile()}},Path(tmp)/"config.json","example",app,profile()["server"])
                run.assert_not_called()

    def test_prepare_cannot_sign_a_link_outside_its_private_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);app=root/"Example.app";app.mkdir()
            (app/"Info.plist").write_bytes(plistlib.dumps({"CFBundleIdentifier":"com.example.qa","DTPlatformName":"iphonesimulator"}))
            external=root/"Foreign.framework";external.mkdir();(external/"keep").write_text("original")
            (app/"Foreign.framework").symlink_to(external,target_is_directory=True)
            with patch.object(self.qa.Path,"home",return_value=root/"home"),patch.object(self.qa,"SharedLock",return_value=contextlib.nullcontext()),patch.object(self.qa,"command") as run:
                with self.assertRaises(self.qa.QAError):self.qa.prepare_build({"projects":{"example":profile()}},root/"config.json","example",app,profile()["server"])
                run.assert_not_called()
            self.assertEqual("original",(external/"keep").read_text())

    def test_simulator_entitlements_are_read_from_linked_macho_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            value={"application-identifier":"com.example.qa","keychain-access-groups":["com.example.qa"]}
            payload=plistlib.dumps(value);length=72+80;offset=32+length
            header=struct.pack("<8I",0xFEEDFACF,0x100000C,0,2,1,length,0,0)
            segment=struct.pack("<II16sQQQQiiII",0x19,length,b"__TEXT",0,4096,0,4096,7,5,1,0)
            section=struct.pack("<16s16sQQIIIIIIII",b"__entitlements",b"__TEXT",offset,len(payload),offset,0,0,0,0,0,0,0)
            path=Path(tmp)/"Example";path.write_bytes(header+segment+section+payload)
            self.assertEqual(value,self.qa.simulated_entitlements(path))


if __name__ == "__main__":
    unittest.main()
