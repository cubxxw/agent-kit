from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skills/product-qa/scripts/install.py"


class ProductQAInstallTests(unittest.TestCase):
    def test_installer_is_available(self):
        self.assertTrue(SCRIPT.is_file(), "machine installer is not implemented")

    def test_foreign_command_is_preserved(self):
        if not SCRIPT.exists(): self.skipTest("installer not implemented")
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            target = home / ".local/bin/agent-qa"
            target.parent.mkdir(parents=True)
            target.write_text("foreign command")
            p = subprocess.run([sys.executable, str(SCRIPT), "--home", tmp], capture_output=True, text=True)
            self.assertNotEqual(0, p.returncode)
            self.assertEqual("foreign command", target.read_text())

    def test_command_install_is_idempotent_and_monitor_is_opt_in(self):
        if not SCRIPT.exists(): self.skipTest("installer not implemented")
        with tempfile.TemporaryDirectory() as tmp:
            for _ in range(2):
                subprocess.run([sys.executable, str(SCRIPT), "--home", tmp], capture_output=True, text=True, check=True)
            home = Path(tmp)
            self.assertTrue((home / ".local/bin/agent-qa").is_symlink())
            self.assertFalse((home / "Library/LaunchAgents/com.agent-kit.product-qa.plist").exists())


if __name__ == "__main__": unittest.main()
