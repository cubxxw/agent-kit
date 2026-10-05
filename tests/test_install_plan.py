from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agentkit.core import AgentKitError, ROOT, install_links, plan_install_links


TOOLS = ("codex", "claude", "qwen", "opencode", "pi", "openclaw")


class InstallPlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.env = {
            f"AGENT_KIT_{tool.upper()}_SKILLS_DIR": str(self.base / tool)
            for tool in TOOLS
        }
        self.environment = patch.dict(os.environ, self.env)
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(ROOT / "bin" / "agent-kit"), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def json_plan(self, *args: str, ready: bool = True) -> dict:
        result = self.cli("plan", "--profile", "base", "--tool", "all", "--json", *args)
        self.assertEqual(0 if ready else 2, result.returncode, result.stderr)
        self.assertTrue(result.stdout.strip(), "The plan must be returned on stdout")
        plan = json.loads(result.stdout)
        self.assertEqual(ready, plan["ready"])
        return plan

    def test_later_host_conflict_leaves_earlier_hosts_uncreated(self) -> None:
        conflict = self.base / "openclaw" / "manage-agent-kit"
        conflict.mkdir(parents=True)
        marker = conflict / "keep.txt"
        marker.write_text("existing skill", encoding="utf-8")

        with self.assertRaises(AgentKitError):
            install_links("base", "all")

        self.assertEqual("existing skill", marker.read_text(encoding="utf-8"))
        for tool in TOOLS[:-1]:
            self.assertFalse((self.base / tool).exists(), tool)

    def test_json_plan_lists_all_targets_and_multiple_conflicts(self) -> None:
        claude = self.base / "claude" / "manage-agent-kit"
        claude.mkdir(parents=True)
        openclaw = self.base / "openclaw" / "manage-agent-kit"
        openclaw.parent.mkdir()
        openclaw.symlink_to(self.base / "foreign-missing")

        plan = self.json_plan(ready=False)

        self.assertEqual(1, plan["schema_version"])
        self.assertEqual("base", plan["profile"])
        self.assertEqual(list(TOOLS), [row["tool"] for row in plan["actions"]])
        self.assertEqual(["claude", "openclaw"], [row["tool"] for row in plan["conflicts"]])
        self.assertEqual(["conflict", "foreign-link"], [row["state"] for row in plan["conflicts"]])
        self.assertTrue(all(row["action"] == "conflict" for row in plan["conflicts"]))
        self.assertTrue(all(row["reason"] for row in plan["actions"]))
        self.assertTrue(all(row["skill"] == "manage-agent-kit" for row in plan["actions"]))
        self.assertEqual(str(self.base / "codex" / "manage-agent-kit"), plan["actions"][0]["destination"])
        self.assertEqual(str(ROOT / "skills" / "manage-agent-kit"), plan["actions"][0]["source"])
        self.assertFalse((self.base / "codex").exists())
        self.assertTrue(claude.is_dir())
        self.assertTrue(openclaw.is_symlink())

    def test_successful_preview_creates_no_directories(self) -> None:
        plan = self.json_plan()

        self.assertEqual([], plan["conflicts"])
        self.assertEqual(["missing"] * 6, [row["state"] for row in plan["actions"]])
        self.assertEqual(["link"] * 6, [row["action"] for row in plan["actions"]])
        self.assertEqual([], list(self.base.iterdir()))

        result = self.cli("install", "--profile", "base", "--tool", "all", "--dry-run")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual([], list(self.base.iterdir()))

    def test_install_and_repeat_match_the_preview(self) -> None:
        self.json_plan()
        install_links("base", "all")

        for tool in TOOLS:
            destination = self.base / tool / "manage-agent-kit"
            self.assertTrue(destination.is_symlink())
            self.assertEqual(ROOT / "skills" / "manage-agent-kit", destination.resolve())

        plan = self.json_plan()
        self.assertEqual(["linked"] * 6, [row["state"] for row in plan["actions"]])
        self.assertEqual(["noop"] * 6, [row["action"] for row in plan["actions"]])
        repeated = install_links("base", "all")
        self.assertEqual(6, len(repeated))
        self.assertTrue(all("already linked" in message for message in repeated))

    def test_replace_managed_only_replaces_repository_links(self) -> None:
        destination = self.base / "codex" / "manage-agent-kit"
        destination.parent.mkdir()
        previous = ROOT / "skills" / "retired-skill"
        destination.symlink_to(previous)

        blocked = self.json_plan(ready=False)
        self.assertEqual("managed-drift", blocked["conflicts"][0]["state"])
        self.assertIn("--replace-managed", blocked["conflicts"][0]["reason"])
        allowed = self.json_plan("--replace-managed")
        self.assertEqual("replace", allowed["actions"][0]["action"])
        self.assertEqual(str(previous), os.readlink(destination))

        install_links("base", "all", replace_managed=True)
        self.assertEqual(ROOT / "skills" / "manage-agent-kit", destination.resolve())

    def test_replace_managed_refuses_foreign_link_and_real_directory(self) -> None:
        foreign = self.base / "claude" / "manage-agent-kit"
        foreign.parent.mkdir()
        previous = self.base / "outside-repository"
        foreign.symlink_to(previous)
        real = self.base / "openclaw" / "manage-agent-kit"
        real.mkdir(parents=True)

        plan = self.json_plan("--replace-managed", ready=False)
        self.assertEqual(["foreign-link", "conflict"], [row["state"] for row in plan["conflicts"]])
        with self.assertRaises(AgentKitError) as caught:
            install_links("base", "all", replace_managed=True)

        self.assertIn(str(foreign), str(caught.exception))
        self.assertIn(str(real), str(caught.exception))
        self.assertEqual(str(previous), os.readlink(foreign))
        self.assertTrue(real.is_dir())
        for tool in ("codex", "qwen", "opencode", "pi"):
            self.assertFalse((self.base / tool).exists(), tool)

    def test_dry_run_reports_every_conflict_without_changes(self) -> None:
        for tool in ("claude", "openclaw"):
            (self.base / tool / "manage-agent-kit").mkdir(parents=True)

        result = self.cli("install", "--profile", "base", "--tool", "all", "--dry-run")

        self.assertEqual(2, result.returncode)
        self.assertIn(str(self.base / "claude" / "manage-agent-kit"), result.stderr)
        self.assertIn(str(self.base / "openclaw" / "manage-agent-kit"), result.stderr)
        self.assertIn("No changes", result.stderr)
        for tool in ("codex", "qwen", "opencode", "pi"):
            self.assertFalse((self.base / tool).exists(), tool)

    def test_plan_detects_parent_file_before_install_creates_other_hosts(self) -> None:
        blocker = self.base / "openclaw"
        blocker.write_text("keep parent file", encoding="utf-8")

        plan = self.json_plan(ready=False)
        self.assertEqual("parent-conflict", plan["conflicts"][0]["state"])
        with self.assertRaises(AgentKitError):
            install_links("base", "all")

        self.assertEqual("keep parent file", blocker.read_text(encoding="utf-8"))
        for tool in TOOLS[:-1]:
            self.assertFalse((self.base / tool).exists(), tool)

    def test_execution_error_reports_links_completed_before_target_changed(self) -> None:
        changed_target = self.base / "claude" / "manage-agent-kit"

        def plan_then_target_changes(*args: object, **kwargs: object) -> dict:
            plan = plan_install_links(*args, **kwargs)
            changed_target.mkdir(parents=True)
            return plan

        with patch("agentkit.core.plan_install_links", side_effect=plan_then_target_changes):
            try:
                install_links("base", "all")
            except AgentKitError as exc:
                message = str(exc)
            except OSError as exc:
                self.fail(f"Execution errors must report completed and failed paths: {exc}")
            else:
                self.fail("A target changed after preflight, so installation must stop")

        completed = self.base / "codex" / "manage-agent-kit"
        self.assertTrue(completed.is_symlink())
        self.assertTrue(changed_target.is_dir())
        self.assertIn(str(completed), message)
        self.assertIn(str(changed_target), message)
        self.assertIn("rerun plan", message)
        self.assertFalse((self.base / "qwen").exists())

    def test_replacement_rechecks_ownership_before_removing_changed_targets(self) -> None:
        for target_kind in ("foreign-link", "file"):
            with self.subTest(target_kind=target_kind):
                directory = self.base / target_kind
                directory.mkdir()
                destination = directory / "manage-agent-kit"
                destination.symlink_to(ROOT / "skills" / "retired-skill")
                outside = self.base / "foreign-source"

                def plan_then_ownership_changes(*args: object, **kwargs: object) -> dict:
                    plan = plan_install_links(*args, **kwargs)
                    destination.unlink()
                    if target_kind == "foreign-link":
                        destination.symlink_to(outside)
                    else:
                        destination.write_text("new user content", encoding="utf-8")
                    return plan

                with patch.dict(os.environ, {"AGENT_KIT_CODEX_SKILLS_DIR": str(directory)}):
                    with patch("agentkit.core.plan_install_links", side_effect=plan_then_ownership_changes):
                        with self.assertRaises(AgentKitError):
                            install_links("base", "codex", replace_managed=True)

                if target_kind == "foreign-link":
                    self.assertEqual(str(outside), os.readlink(destination))
                else:
                    self.assertFalse(destination.is_symlink())
                    self.assertEqual("new user content", destination.read_text(encoding="utf-8"))

    def test_hosts_sharing_a_directory_install_one_link_without_failure(self) -> None:
        shared = self.base / "shared"
        shared.mkdir()
        alias = self.base / "alias"
        alias.symlink_to(shared, target_is_directory=True)
        with patch.dict(os.environ, {
            "AGENT_KIT_CODEX_SKILLS_DIR": str(shared),
            "AGENT_KIT_CLAUDE_SKILLS_DIR": str(alias),
        }):
            plan = self.json_plan()
            self.assertEqual(["link", "noop"], [row["action"] for row in plan["actions"][:2]])
            self.assertIn("resolved_destination", plan["actions"][0])
            self.assertEqual(
                [str(shared.resolve() / "manage-agent-kit")] * 2,
                [row["resolved_destination"] for row in plan["actions"][:2]],
            )
            self.assertEqual([], list(shared.iterdir()))
            install_links("base", "all")
            repeated = install_links("base", "all")

        self.assertTrue((shared / "manage-agent-kit").is_symlink())
        self.assertEqual((shared / "manage-agent-kit").resolve(), (alias / "manage-agent-kit").resolve())
        self.assertTrue(all("already linked" in message for message in repeated))

    def test_later_incomplete_source_blocks_the_whole_profile(self) -> None:
        catalog = {
            "profiles": {"probe": {"skills": ["manage-agent-kit", "not-present"]}},
            "skills": [
                {"name": "manage-agent-kit", "path": "skills/manage-agent-kit"},
                {"name": "not-present", "path": "skills/not-present"},
            ],
        }
        with patch("agentkit.core.load_catalog", return_value=catalog):
            plan = plan_install_links("probe", "all")
            self.assertFalse(plan["ready"])
            self.assertEqual(12, len(plan["actions"]))
            self.assertEqual(["invalid-source"] * 6, [row["state"] for row in plan["conflicts"]])
            with self.assertRaises(AgentKitError):
                install_links("probe", "all")

        self.assertEqual([], list(self.base.iterdir()))

    def probe_repository(self) -> tuple[Path, Path, dict]:
        repository = self.base / "repository"
        source = repository / "skills" / "probe"
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text("fixture skill", encoding="utf-8")
        catalog = {
            "profiles": {"probe": {"skills": ["probe"]}},
            "skills": [{"name": "probe", "path": "skills/probe"}],
        }
        return repository, source, catalog

    def test_nested_targets_are_blocked_before_a_planned_link_redirects_writes(self) -> None:
        repository, source, catalog = self.probe_repository()
        for outer_tool, nested_tool in (("codex", "claude"), ("claude", "codex")):
            with self.subTest(outer_tool=outer_tool):
                shared = self.base / outer_tool / "shared"
                env = {
                    f"AGENT_KIT_{outer_tool.upper()}_SKILLS_DIR": str(shared),
                    f"AGENT_KIT_{nested_tool.upper()}_SKILLS_DIR": str(shared / "probe" / "nested"),
                }
                with patch.dict(os.environ, env), patch("agentkit.core.ROOT", repository), patch("agentkit.core.load_catalog", return_value=catalog):
                    plan = plan_install_links("probe", "core")
                    self.assertFalse(plan["ready"])
                    self.assertEqual([nested_tool], [row["tool"] for row in plan["conflicts"]])
                    with self.assertRaises(AgentKitError):
                        install_links("probe", "core")

                self.assertFalse(shared.exists())
                self.assertEqual(["SKILL.md"], [path.name for path in source.iterdir()])

    def test_nested_target_through_a_replaced_link_is_blocked(self) -> None:
        repository, source, catalog = self.probe_repository()
        retired = repository / "retired"
        retired.mkdir()
        shared = self.base / "shared"
        shared.mkdir()
        ancestor = shared / "probe"
        ancestor.symlink_to(retired, target_is_directory=True)
        alias = self.base / "shared-alias"
        alias.symlink_to(shared, target_is_directory=True)
        env = {
            "AGENT_KIT_CODEX_SKILLS_DIR": str(shared),
            "AGENT_KIT_CLAUDE_SKILLS_DIR": str(alias / "probe" / "nested"),
        }
        with patch.dict(os.environ, env), patch("agentkit.core.ROOT", repository), patch("agentkit.core.load_catalog", return_value=catalog):
            plan = plan_install_links("probe", "core", replace_managed=True)
            self.assertFalse(plan["ready"])
            self.assertEqual(["claude"], [row["tool"] for row in plan["conflicts"]])
            with self.assertRaises(AgentKitError):
                install_links("probe", "core", replace_managed=True)

        self.assertEqual(str(retired), os.readlink(ancestor))
        self.assertEqual([], list(retired.iterdir()))
        self.assertEqual(["SKILL.md"], [path.name for path in source.iterdir()])

    def test_tool_directory_inside_a_canonical_source_is_never_written(self) -> None:
        repository, source, catalog = self.probe_repository()
        alias = self.base / "source-alias"
        alias.symlink_to(source, target_is_directory=True)
        for directory in (source, source / "nested", alias):
            with self.subTest(directory=directory):
                with patch.dict(os.environ, {"AGENT_KIT_CLAUDE_SKILLS_DIR": str(directory)}), patch("agentkit.core.ROOT", repository), patch("agentkit.core.load_catalog", return_value=catalog):
                    plan = plan_install_links("probe", "core")
                    self.assertFalse(plan["ready"])
                    self.assertEqual(["claude"], [row["tool"] for row in plan["conflicts"]])
                    with self.assertRaises(AgentKitError):
                        install_links("probe", "core")

                self.assertFalse((self.base / "codex").exists())
                self.assertEqual(["SKILL.md"], [path.name for path in source.iterdir()])

    def test_invalid_skill_names_cannot_escape_a_tool_directory(self) -> None:
        repository, source, catalog = self.probe_repository()
        for name in ("../user-area/probe", "p" * 65):
            with self.subTest(name=name):
                catalog["profiles"]["probe"]["skills"] = [name]
                catalog["skills"][0]["name"] = name
                with patch("agentkit.core.ROOT", repository), patch("agentkit.core.load_catalog", return_value=catalog):
                    plan = plan_install_links("probe", "core")
                    self.assertFalse(plan["ready"])
                    self.assertEqual(2, len(plan["conflicts"]))
                    with self.assertRaises(AgentKitError):
                        install_links("probe", "core")

                self.assertFalse((self.base / "codex").exists())
                self.assertFalse((self.base / "claude").exists())
                self.assertFalse((self.base / "user-area").exists())
                self.assertEqual(["SKILL.md"], [path.name for path in source.iterdir()])

    def test_execution_refuses_parent_redirect_after_preflight(self) -> None:
        repository, source, catalog = self.probe_repository()
        for redirect_to_source in (True, False):
            with self.subTest(redirect_to_source=redirect_to_source):
                scenario = self.base / str(redirect_to_source)
                safe = scenario / "safe"
                safe.mkdir(parents=True)
                redirected = source if redirect_to_source else scenario / "other-safe"
                if not redirect_to_source:
                    redirected.mkdir()
                alias = scenario / "alias"
                alias.symlink_to(safe, target_is_directory=True)
                first_host = scenario / "codex"
                env = {
                    "AGENT_KIT_CODEX_SKILLS_DIR": str(first_host),
                    "AGENT_KIT_CLAUDE_SKILLS_DIR": str(alias),
                }

                def plan_then_parent_redirects(*args: object, **kwargs: object) -> dict:
                    plan = plan_install_links(*args, **kwargs)
                    alias.unlink()
                    alias.symlink_to(redirected, target_is_directory=True)
                    return plan

                with patch.dict(os.environ, env), patch("agentkit.core.ROOT", repository), patch("agentkit.core.load_catalog", return_value=catalog):
                    with patch("agentkit.core.plan_install_links", side_effect=plan_then_parent_redirects):
                        with self.assertRaises(AgentKitError) as caught:
                            install_links("probe", "core")

                self.assertTrue((first_host / "probe").is_symlink())
                self.assertIn(str(first_host / "probe"), str(caught.exception))
                self.assertIn(str(alias / "probe"), str(caught.exception))
                self.assertIn("rerun plan", str(caught.exception))
                self.assertEqual([], list(safe.iterdir()))
                self.assertFalse((redirected / "probe").is_symlink())
                self.assertEqual(["SKILL.md"], [path.name for path in source.iterdir()])

    def test_execution_rechecks_catalog_source_boundary_before_writing(self) -> None:
        repository, source, catalog = self.probe_repository()
        directory = repository / "host"
        env = {"AGENT_KIT_CODEX_SKILLS_DIR": str(directory)}

        def plan_then_catalog_source_changes(*args: object, **kwargs: object) -> dict:
            plan = plan_install_links(*args, **kwargs)
            catalog["skills"].append({"name": "new-canonical-source", "path": "host"})
            return plan

        with patch.dict(os.environ, env), patch("agentkit.core.ROOT", repository), patch("agentkit.core.load_catalog", return_value=catalog):
            with patch("agentkit.core.plan_install_links", side_effect=plan_then_catalog_source_changes):
                with self.assertRaises(AgentKitError):
                    install_links("probe", "codex")

        self.assertFalse(directory.exists())
        self.assertEqual(["SKILL.md"], [path.name for path in source.iterdir()])


if __name__ == "__main__":
    unittest.main()
