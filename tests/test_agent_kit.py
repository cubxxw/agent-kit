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
                first = install_links("base")
                second = install_links("base")
                codex = base / "codex" / "manage-agent-kit"
                claude = base / "claude" / "manage-agent-kit"
                self.assertTrue(codex.is_symlink())
                self.assertTrue(claude.is_symlink())
                self.assertEqual(codex.resolve(), claude.resolve())
                self.assertTrue(any("linked" in line for line in first))
                self.assertTrue(all("already linked" in line for line in second))

                uninstall_links("base")
                self.assertFalse(codex.exists())
                self.assertFalse(claude.exists())

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
                    install_links("base")
            self.assertTrue(conflict.is_dir())

    def test_scanner_detects_generated_token_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "publish.txt"
            candidate.write_text("sk-" + ("x" * 30), encoding="utf-8")
            findings = scan_public_tree([candidate])
            self.assertTrue(any("API key" in item.message for item in findings))

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
