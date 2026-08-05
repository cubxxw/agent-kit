from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agentkit.core import (
    AgentKitError,
    install_links,
    load_catalog,
    resolve_profile,
    scan_public_tree,
    uninstall_links,
    validate_catalog,
)
from scripts.public_guard import find_reason


class AgentKitTests(unittest.TestCase):
    def test_catalog_is_valid(self) -> None:
        errors = [item for item in validate_catalog() if item.level == "error"]
        self.assertEqual([], errors)

    def test_install_links_both_agents_to_one_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            env = {
                "AGENT_KIT_CODEX_SKILLS_DIR": str(base / "codex"),
                "AGENT_KIT_CLAUDE_SKILLS_DIR": str(base / "claude"),
            }
            with patch.dict(os.environ, env):
                first = install_links("base", "core")
                second = install_links("base", "core")
                codex = base / "codex" / "manage-agent-kit"
                claude = base / "claude" / "manage-agent-kit"
                self.assertTrue(codex.is_symlink())
                self.assertTrue(claude.is_symlink())
                self.assertEqual(codex.resolve(), claude.resolve())
                self.assertTrue(any("linked" in line for line in first))
                self.assertTrue(all("already linked" in line for line in second))

                uninstall_links("base", "core")
                self.assertFalse(codex.exists())
                self.assertFalse(claude.exists())

    def test_install_links_all_supported_agents_to_one_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            env = {
                "AGENT_KIT_CODEX_SKILLS_DIR": str(base / "codex"),
                "AGENT_KIT_CLAUDE_SKILLS_DIR": str(base / "claude"),
                "AGENT_KIT_QWEN_SKILLS_DIR": str(base / "qwen"),
                "AGENT_KIT_OPENCODE_SKILLS_DIR": str(base / "opencode"),
                "AGENT_KIT_PI_SKILLS_DIR": str(base / "pi"),
                "AGENT_KIT_OPENCLAW_SKILLS_DIR": str(base / "openclaw"),
            }
            with patch.dict(os.environ, env):
                install_links("base", "all")
                destinations = [
                    Path(directory) / "manage-agent-kit" for directory in env.values()
                ]
                self.assertTrue(all(path.is_symlink() for path in destinations))
                self.assertEqual(1, len({path.resolve() for path in destinations}))

    def test_top_profile_contains_every_adopted_skill(self) -> None:
        catalog = load_catalog()
        names = [entry["name"] for entry in catalog["skills"]]
        self.assertEqual(names, resolve_profile(catalog, "top"))
        self.assertEqual(names, resolve_profile(catalog, "all"))

    def test_installer_refuses_existing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            conflict = base / "codex" / "manage-agent-kit"
            conflict.mkdir(parents=True)
            env = {
                "AGENT_KIT_CODEX_SKILLS_DIR": str(base / "codex"),
                "AGENT_KIT_CLAUDE_SKILLS_DIR": str(base / "claude"),
            }
            with patch.dict(os.environ, env):
                with self.assertRaises(AgentKitError):
                    install_links("base", "core")
            self.assertTrue(conflict.is_dir())

    def test_scanner_detects_generated_token_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "publish.txt"
            candidate.write_text("sk-" + ("x" * 30), encoding="utf-8")
            findings = scan_public_tree([candidate])
            self.assertTrue(any("API key" in item.message for item in findings))

    def test_scanner_allows_documented_home_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "example.txt"
            candidate.write_text(
                "Use file:/Users/me/Desktop/example.png in this bad-code sample.",
                encoding="utf-8",
            )
            self.assertEqual([], scan_public_tree([candidate]))

    def test_public_guard_blocks_secret_paths(self) -> None:
        payload = {
            "tool_name": "Bash",
            "tool_input": {"command": "read " + ".env"},
        }
        self.assertIsNotNone(find_reason(payload))
        self.assertIsNone(
            find_reason(
                {
                    "tool_name": "Bash",
                    "tool_input": {"command": "python3 -m unittest"},
                }
            )
        )

    def test_public_guard_emits_cross_host_deny_shape(self) -> None:
        script = Path("scripts/public_guard.py").resolve()
        payload = {
            "tool_name": "apply_patch",
            "tool_input": {"command": "sk-" + ("x" * 30)},
        }
        result = subprocess.run(
            ["python3", str(script)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=True,
        )
        output = json.loads(result.stdout)
        decision = output["hookSpecificOutput"]
        self.assertEqual("PreToolUse", decision["hookEventName"])
        self.assertEqual("deny", decision["permissionDecision"])


if __name__ == "__main__":
    unittest.main()
