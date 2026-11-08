#!/usr/bin/env python3
"""Install the command; --watch opts into registered-simulator boot login."""
from __future__ import annotations

import argparse
import json
import os
import plistlib
import subprocess
import sys
from pathlib import Path

from agent_qa import QAError, load_config


def install(home, watch=False, no_load=False, gui=False):
    home = Path(home).expanduser().resolve()
    source = Path(__file__).resolve().with_name("agent_qa.py")
    command = home / ".local/bin/agent-qa"
    if command.is_symlink():
        if command.resolve() != source:
            raise QAError("existing agent-qa command belongs to another installation")
    elif command.exists():
        raise QAError("existing agent-qa command was preserved")
    if watch or gui:
        config_path = home / ".config/agent-qa/projects.json"
        config = load_config(config_path)
    command.parent.mkdir(parents=True, exist_ok=True)
    source.chmod(source.stat().st_mode | 0o111)
    if not command.is_symlink(): command.symlink_to(source)
    if watch or gui:
        log_dir = home / ".local/state/agent-qa"
        log_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        logs = [log_dir / "monitor.stdout.log", log_dir / "monitor.stderr.log"]
        for log in logs:
            fd = os.open(log, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
            os.close(fd)
            log.chmod(0o600)
        plist = home / "Library/LaunchAgents/com.agent-kit.product-qa.plist"
        plist.parent.mkdir(parents=True, exist_ok=True)
        data = {"Label": "com.agent-kit.product-qa", "ProgramArguments": [sys.executable, str(source), "--config", str(config_path), "watch", "--once"],
                "RunAtLoad": True, "StartInterval": 20, "ProcessType": "Background", "Umask": 0o077,
                "EnvironmentVariables": {"PATH": str(home / ".local/bin") + ":/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"},
                "StandardOutPath": str(logs[0]), "StandardErrorPath": str(logs[1])}
        if watch and plist.exists():
            old = plistlib.loads(plist.read_bytes())
            if old.get("Label") != data["Label"] or old.get("ProgramArguments", [None, None])[1] != str(source):
                raise QAError("existing launch agent belongs to another installation")
        agents = []
        if watch:
            plist.write_bytes(plistlib.dumps(data))
            plist.chmod(0o600)
            agents.append((plist, data["Label"]))
        if gui or config.get("gui_bridge"):
            queue = log_dir / "requests"
            queue.mkdir(mode=0o700, exist_ok=True)
            request_plist = plist.with_name("com.agent-kit.product-qa-requests.plist")
            worker = {**data, "Label": "com.agent-kit.product-qa-requests", "ProgramArguments": [sys.executable, str(source), "--config", str(config_path), "serve"], "QueueDirectories": [str(queue)]}
            worker.pop("StartInterval", None)
            if request_plist.exists():
                old = plistlib.loads(request_plist.read_bytes())
                if old.get("ProgramArguments", [None, None])[1] != str(source): raise QAError("existing GUI request job was preserved")
            request_plist.write_bytes(plistlib.dumps(worker)); request_plist.chmod(0o600)
            agents.append((request_plist, worker["Label"]))
        if not no_load:
            if home != Path.home().resolve(): raise QAError("cannot activate launchd for a different user's home")
            domain = "gui/" + str(os.getuid())
            for target, label in agents:
                subprocess.run(["launchctl", "bootout", domain + "/" + label], capture_output=True)
                result = subprocess.run(["launchctl", "bootstrap", domain, str(target)], capture_output=True)
                if result.returncode: raise QAError("launch agent was written but GUI activation failed")
    return {"command_installed": True, "automatic_boot_login": watch, "gui_request_bridge": gui, "launch_agent_loaded": (watch or gui) and not no_load}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--home", default=str(Path.home()))
    p.add_argument("--watch", action="store_true")
    p.add_argument("--no-load", action="store_true")
    p.add_argument("--gui", action="store_true")
    args = p.parse_args()
    try:
        print(json.dumps(install(args.home, args.watch, args.no_load, args.gui)))
        return 0
    except QAError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__": raise SystemExit(main())
