from __future__ import annotations

import importlib.util
import json
import os
import plistlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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


if __name__ == "__main__":
    unittest.main()
