from __future__ import annotations

import subprocess
import sys
import json
import plistlib
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skills/product-qa/scripts/install.py"


class ProductQAInstallTests(unittest.TestCase):
    def config(self, home):
        d={"schema_version":1,"state_dir":str(home/"custom-state"),"projects":{"example":{"kind":"tormie","server":"https://qa.example.invalid","email":"qa@example.invalid","expected_user_id":"b0eac527-cd5d-4b2c-9326-7ac44b8e925a","simulator_id":"c13bb6b9-b688-4d88-8b20-eaf15f72cd50","bundle_id":"com.example.qa","credential":{"service":"com.example.qa","account":"qa@example.invalid"}}}}
        p=home/".config/agent-qa/projects.json";p.parent.mkdir(parents=True);p.write_text(json.dumps(d));p.chmod(0o600)
        return d

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

    def test_gui_install_watches_configured_state_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp);config=self.config(home)
            subprocess.run([sys.executable,str(SCRIPT),"--home",tmp,"--gui","--no-load"],capture_output=True,check=True)
            p=home/"Library/LaunchAgents/com.agent-kit.product-qa-requests.plist"
            self.assertEqual([str(Path(config["state_dir"])/"requests")],plistlib.loads(p.read_bytes())["QueueDirectories"])

    def test_visible_ui_jobs_use_app_resource_classification(self):
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp);self.config(home)
            subprocess.run([sys.executable,str(SCRIPT),"--home",tmp,"--watch","--gui","--no-load"],capture_output=True,check=True)
            for name in ("com.agent-kit.product-qa.plist","com.agent-kit.product-qa-requests.plist"):
                data=plistlib.loads((home/"Library/LaunchAgents"/name).read_bytes())
                self.assertEqual("Interactive",data["ProcessType"])

    def test_gui_install_preserves_a_foreign_label_with_the_same_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp);self.config(home)
            p=home/"Library/LaunchAgents/com.agent-kit.product-qa-requests.plist";p.parent.mkdir(parents=True)
            old={"Label":"com.example.other-job","ProgramArguments":[sys.executable,str(SCRIPT.with_name("agent_qa.py"))]};p.write_bytes(plistlib.dumps(old))
            r=subprocess.run([sys.executable,str(SCRIPT),"--home",tmp,"--gui","--no-load"],capture_output=True)
            self.assertNotEqual(0,r.returncode)
            self.assertEqual(old,plistlib.loads(p.read_bytes()))


if __name__ == "__main__": unittest.main()
