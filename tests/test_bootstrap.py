from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class BootstrapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.source = self.directory / "source"
        self.source.mkdir()
        self.git("init", "-b", "main", cwd=self.source)
        shutil.copytree(ROOT / "agentkit", self.source / "agentkit", ignore=shutil.ignore_patterns("__pycache__"))
        (self.source / "bin").mkdir()
        shutil.copy2(ROOT / "bin" / "agent-kit", self.source / "bin" / "agent-kit")
        skill = self.source / "skills" / "manage-agent-kit"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: manage-agent-kit\ndescription: Manage the fixture setup.\n---\nFixture.\n",
            encoding="utf-8",
        )
        (self.source / "catalog.json").write_text(json.dumps({
            "schema_version": 1,
            "repository": "fixture/agent-kit",
            "profiles": {"base": {"skills": ["manage-agent-kit"]}},
            "skills": [{"name": "manage-agent-kit", "path": "skills/manage-agent-kit",
                        "license": "MIT", "source": {"type": "first-party"}}],
        }), encoding="utf-8")
        self.git("add", ".", cwd=self.source)
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-m", "Fixture", cwd=self.source)
        self.checkout = self.directory / "checkout"
        self.codex = self.directory / "codex"
        self.claude = self.directory / "claude"
        self.environment = dict(os.environ, **{
            "AGENT_KIT_HOME": str(self.checkout),
            "AGENT_KIT_REPOSITORY": str(self.source),
            "AGENT_KIT_BRANCH": "main",
            "AGENT_KIT_PROFILE": "base",
            "AGENT_KIT_TOOL": "core",
            "AGENT_KIT_CODEX_SKILLS_DIR": str(self.codex),
            "AGENT_KIT_CLAUDE_SKILLS_DIR": str(self.claude),
        })

    @staticmethod
    def git(*args: str, cwd: Path) -> None:
        subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)

    def bootstrap(self) -> subprocess.CompletedProcess:
        return subprocess.run(["sh", str(ROOT / "scripts" / "bootstrap.sh")],
                              env=self.environment, capture_output=True, text=True)

    def clone(self) -> None:
        self.git("clone", str(self.source), str(self.checkout), cwd=self.directory)

    def test_existing_checkout_with_unexpected_origin_is_preserved(self) -> None:
        self.clone()
        self.environment["AGENT_KIT_REPOSITORY"] = str(self.directory / "expected-source")
        result = self.bootstrap()
        self.assertNotEqual(0, result.returncode)
        self.assertFalse(self.codex.exists())
        self.assertFalse(self.claude.exists())
        self.assertIn("origin", result.stderr)

    def test_existing_tracking_feature_branch_is_not_used_for_bootstrap(self) -> None:
        self.clone()
        self.git("switch", "-c", "feature", "--track", "origin/main", cwd=self.checkout)
        result = self.bootstrap()
        self.assertNotEqual(0, result.returncode)
        self.assertFalse(self.codex.exists())
        self.assertFalse(self.claude.exists())
        self.assertIn("branch", result.stderr)

    def test_fresh_bootstrap_reports_missing_targets_before_installing(self) -> None:
        result = self.bootstrap()
        self.assertEqual(0, result.returncode, result.stderr)
        start = result.stdout.find("{")
        self.assertGreaterEqual(start, 0, "Bootstrap must print its plan before installation")
        plan, _ = json.JSONDecoder().raw_decode(result.stdout[start:])
        self.assertTrue(plan["ready"])
        self.assertEqual(["missing", "missing"], [row["state"] for row in plan["actions"]])
        expected = self.checkout / "skills" / "manage-agent-kit"
        self.assertEqual(expected.resolve(), (self.codex / "manage-agent-kit").resolve())
        self.assertEqual(expected.resolve(), (self.claude / "manage-agent-kit").resolve())


if __name__ == "__main__":
    unittest.main()
