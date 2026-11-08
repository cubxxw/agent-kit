#!/usr/bin/env python3
"""Private-profile native QA entry. Never prints credentials or raw UI trees."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import http.cookiejar
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
from urllib import error, parse, request


class QAError(Exception):
    pass


def private_json(path, value):
    path = Path(path)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + str(os.getpid()) + ".tmp")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w") as out:
            json.dump(value, out, ensure_ascii=False, indent=2)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def validate_profile(p):
    if any(key in p for key in ("password", "access_token", "refresh_token", "token")):
        raise QAError("plaintext credentials are not allowed in a profile")
    u = parse.urlsplit(p.get("server", ""))
    if u.scheme != "https" or not u.hostname or u.username or u.password or u.query or u.fragment or u.path not in ("", "/"):
        raise QAError("profile must pin one HTTPS server origin without redirects or URL credentials")
    if p.get("kind") not in ("leafhour", "tormie", "supabase"):
        raise QAError("unsupported authentication adapter")
    try:
        uuid.UUID(p["expected_user_id"])
        uuid.UUID(p["simulator_id"])
    except (ValueError, KeyError, TypeError):
        raise QAError("profile needs pinned account and simulator UUIDs") from None
    if not re.fullmatch(r"[^\s@]+@[^\s@]+", p.get("email", "")):
        raise QAError("profile needs a dedicated testing email")
    if not re.fullmatch(r"[A-Za-z0-9.-]+", p.get("bundle_id", "")):
        raise QAError("profile needs an exact installed application identifier")
    if not all(p.get("credential", {}).get(k) for k in ("service", "account")):
        raise QAError("profile needs an OS keychain reference")
    if any("PASSWORD" in k.upper() or "TOKEN" in k.upper() for k in p.get("launch_env", {})):
        raise QAError("launch environments cannot contain passwords or session tokens")
    return p


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class HTTP:
    def __init__(self, p):
        self.origin = p["server"].rstrip("/")
        handlers = [request.HTTPCookieProcessor(http.cookiejar.CookieJar()), NoRedirect()]
        if p.get("bypass_proxy"):
            handlers.append(request.ProxyHandler({}))
        self.opener = request.build_opener(*handlers)

    def __call__(self, path, body=None, headers=None):
        if not path.startswith("/") or path.startswith("//"):
            raise QAError("refusing an unpinned request")
        h = {"Accept": "application/json", **(headers or {})}
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            h["Content-Type"] = "application/json"
        req = request.Request(self.origin + path, data=data, headers=h)
        try:
            with self.opener.open(req, timeout=20) as reply:
                raw = reply.read(200000)
                try:
                    payload = json.loads(raw) if raw else {}
                except ValueError:
                    payload = None
                return reply.status, payload
        except error.HTTPError as exc:
            return exc.code, {}
        except (OSError, ValueError):
            raise QAError("authentication server could not be reached securely") from None


def check_credentials(p, password, transport=None):
    validate_profile(p)
    send = transport or HTTP(p)
    kind = p["kind"]
    if kind == "leafhour":
        login, session, logout = "/api/auth/password", "/api/auth/session", "/api/auth/logout"
        headers = {"Origin": p["server"].rstrip("/")}
        body = {"email": p["email"], "password": password, "client": "ios"}
    elif kind == "tormie":
        login, session, logout = "/api/v1/auth/email/login", "/api/v1/auth/session", "/api/v1/auth/logout"
        headers = {}
        body = {"email": p["email"], "password": password, "client": "native"}
    else:
        login, session, logout = "/auth/v1/token?grant_type=password", "/auth/v1/user", "/auth/v1/logout?scope=local"
        headers = {"apikey": p.get("anon_key", "")}
        if not headers["apikey"]:
            raise QAError("Supabase public client configuration is missing")
        body = {"email": p["email"], "password": password}
    if kind == "leafhour": headers["X-Reader-Owner"] = p["expected_user_id"]
    if kind == "tormie": headers["X-Tormie-User-ID"] = p["expected_user_id"]
    issued = False
    def same(value):
        return isinstance(value, dict) and isinstance(value.get("id"), str) and isinstance(value.get("email"), str) and value["id"].lower() == p["expected_user_id"].lower() and value["email"].lower() == p["email"].lower()
    try:
        status, result = send(login, body, headers)
        issued = status == 200
        if status != 200:
            raise QAError("test password was rejected" if status in (400, 401, 403) else "authentication request failed (HTTP %s)" % status)
        if not isinstance(result, dict): raise QAError("authentication response was malformed")
        user = result.get("user")
        access = result.get("access_token")
        if isinstance(access, str) and access:
            headers["Authorization"] = "Bearer " + access
        if isinstance(user, dict) and isinstance(user.get("id"), str):
            if kind == "leafhour": headers["X-Reader-Owner"] = user["id"]
            if kind == "tormie": headers["X-Tormie-User-ID"] = user["id"]
        if not same(user):
            raise QAError("server identity differs from the pinned test account")
        status, restored = send(session, headers=headers)
        verified = restored if kind == "supabase" else restored.get("user") if isinstance(restored, dict) else None
        if status != 200 or not same(verified):
            raise QAError("server session identity readback failed")
        return {"user_id": p["expected_user_id"], "email": p["email"], "server_identity_verified": True}
    finally:
        if issued:
            try:
                cleanup, _ = send(logout, {}, headers)
                if cleanup not in (200, 204):
                    raise QAError("temporary verification session cleanup failed")
            except QAError:
                raise
            except Exception:
                raise QAError("temporary verification session cleanup could not be confirmed") from None


def keychain_password(p):
    ref = p["credential"]
    result = subprocess.run(["/usr/bin/security", "find-generic-password", "-s", ref["service"], "-a", ref["account"], "-w"], capture_output=True, text=True)
    if result.returncode or not result.stdout:
        raise QAError("dedicated test credential is missing or the keychain is locked")
    return result.stdout.rstrip("\n")


def command(args, *, env=None, timeout=40):
    try:
        result = subprocess.run(args, capture_output=True, text=True, env=env, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        raise QAError("required local tool is unavailable or timed out: " + Path(args[0]).name) from None
    if result.returncode:
        raise QAError("local operation failed: " + Path(args[0]).name + " " + args[1])
    return result.stdout


class UI:
    def __init__(self, device, executable="axe"):
        self.device, self.executable = device, executable

    def tree(self):
        raw = command([self.executable, "describe-ui", "--udid", self.device])
        try:
            value = json.loads(raw)
        except ValueError:
            raise QAError("UI inspection did not return a readable accessibility tree") from None
        items = []
        def visit(node, parents):
            if isinstance(node, dict):
                chain = parents
                if any(k in node for k in ("AXLabel", "AXUniqueId", "type")):
                    index = len(items)
                    items.append({**node, "_path": index, "_parents": parents})
                    chain = parents + [index]
                for child in node.values():
                    if isinstance(child, (list, dict)): visit(child, chain)
            elif isinstance(node, list):
                for child in node: visit(child, parents)
        visit(value, [])
        return items

    @staticmethod
    def matches(item, selector):
        keys = {"id": "AXUniqueId", "label": "AXLabel", "value": "AXValue", "type": "type"}
        return bool(selector) and all(str(item.get(keys.get(k, k), "")) == str(v) for k, v in selector.items())

    def find(self, selector, items=None):
        return next((x for x in (items if items is not None else self.tree()) if self.matches(x, selector)), None)

    def wait(self, selector, timeout=15):
        end = time.monotonic() + timeout
        while True:
            found = self.find(selector)
            if found is not None: return found
            if time.monotonic() >= end: return None
            time.sleep(0.4)

    def tap(self, selector, timeout=10, optional=False):
        end = time.monotonic() + timeout
        item = self.wait(selector, timeout)
        while item is not None and item.get("enabled") is False and time.monotonic() < end:
            time.sleep(0.3)
            item = self.find(selector)
        if item is None or item.get("enabled") is False:
            if optional: return False
            raise QAError("required UI control did not appear: " + str(selector))
        args = [self.executable, "tap", "--udid", self.device]
        for k, v in selector.items():
            args += ["--" + ("element-type" if k == "type" else k), str(v)]
        command(args)
        time.sleep(0.8)
        return True

    def type_secret(self, value):
        try:
            result = subprocess.run([self.executable, "type", "--stdin", "--udid", self.device], input=value, text=True, capture_output=True, timeout=30)
        except (OSError, subprocess.TimeoutExpired):
            raise QAError("secure UI input timed out") from None
        if result.returncode:
            raise QAError("secure UI input failed; tool output was suppressed")

    def fill(self, selector, value, secret=False):
        self.tap(selector)
        command([self.executable, "key-combo", "--modifiers", "227", "--key", "4", "--udid", self.device])
        self.type_secret(value)
        end = time.monotonic() + 8
        while True:
            field = self.find(selector) or {}
            actual = str(field.get("AXValue") or "")
            if actual == value or (secret and len(actual) == len(value) and actual and all(c in "•●*" for c in actual)):
                return
            if time.monotonic() >= end:
                raise QAError("native input field did not confirm secure text entry")
            time.sleep(0.4)

    def steps(self, steps):
        for step in steps:
            action = step["action"]
            if action == "tap":
                self.tap(step["selector"], timeout=step.get("timeout", 6), optional=step.get("optional", False))
            elif action == "wait":
                if self.wait(step["selector"], step.get("timeout", 20)) is None:
                    raise QAError("expected page did not appear")
            elif action == "wait_gone":
                end = time.monotonic() + step.get("timeout", 60)
                while self.find(step["selector"]) is not None:
                    if time.monotonic() >= end:
                        raise QAError("previous UI state did not finish")
                    time.sleep(0.4)
            elif action == "gesture":
                app = next((x for x in self.tree() if x.get("type") == "Application"), {})
                frame = app.get("frame", {})
                command([self.executable, "gesture", step["preset"], "--screen-width", str(int(frame.get("width", 390))), "--screen-height", str(int(frame.get("height", 844))), "--udid", self.device])
                time.sleep(0.5)
            else:
                raise QAError("unsupported UI step")


class WatchState:
    def __init__(self, path):
        self.path = Path(path)
        try: self.data = json.loads(self.path.read_text())
        except (OSError, ValueError): self.data = {}

    def due(self, device, boot, now=None):
        now = time.time() if now is None else now
        previous = self.data.get(device, {})
        if previous.get("boot") != boot: return True
        return not previous.get("success") and previous.get("attempts", 0) < 3 and now - previous.get("at", 0) >= 300

    def record(self, device, boot, success, now=None):
        old = self.data.get(device, {})
        attempts = old.get("attempts", 0) if old.get("boot") == boot else 0
        self.data[device] = {"boot": boot, "success": success, "at": time.time() if now is None else now, "attempts": attempts + 1}
        private_json(self.path, self.data)


class SharedLock:
    def __init__(self, path="/tmp/ios-automation.xcodebuild.lock"):
        self.path = Path(path)
        self.pid = os.getpid()

    def __enter__(self):
        builders = subprocess.run(["/usr/bin/pgrep", "-x", "xcodebuild"], capture_output=True)
        if builders.returncode == 0:
            raise QAError("simulator is busy with an existing build; retry when it finishes")
        result = subprocess.run(["/usr/bin/shlock", "-p", str(self.pid), "-f", str(self.path)], capture_output=True)
        if result.returncode:
            raise QAError("simulator is reserved by another test session")
        return self

    def __exit__(self, *args):
        try:
            if self.path.read_text().strip() == str(self.pid): self.path.unlink()
        except OSError:
            pass


def devices():
    return [d for group in json.loads(command(["xcrun", "simctl", "list", "devices", "available", "-j"]))["devices"].values() for d in group]


def installed_apps(device):
    raw = command(["xcrun", "simctl", "listapps", device])
    try:
        return plistlib.loads(raw.encode())
    except plistlib.InvalidFileException:
        converted = subprocess.run(["/usr/bin/plutil", "-convert", "json", "-o", "-", "-"], input=raw, text=True, capture_output=True)
        if converted.returncode:
            raise QAError("installed application inventory could not be decoded")
        return json.loads(converted.stdout)


def boot_identity(device):
    record = next((d for d in devices() if d["udid"] == device), {})
    if record.get("lastBootedAt"): return record["lastBootedAt"]
    return command(["xcrun", "simctl", "spawn", device, "launchctl", "managerpid"]).strip()


def visible_email(items, email, scope=None):
    if not scope: return False
    anchors = [x["_path"] for x in items if UI.matches(x, scope)]
    if not anchors: return False
    by_path = {x.get("_path"): x for x in items}
    for item in items:
        parents = item.get("_parents", [])
        if item.get("type") != "StaticText": continue
        direct_scope = any(x in parents for x in anchors)
        authenticated_button_scope = any(
            by_path[a].get("type") == "Button" and any(
                x in parents and by_path.get(x, {}).get("type") in ("Group", "ScrollView", "Table", "Sheet", "Form")
                for x in by_path[a].get("_parents", [])
            ) for a in anchors
        )
        if not direct_scope and not authenticated_button_scope: continue
        if any("field" in str(by_path.get(x, {}).get("type", "")).lower() or by_path.get(x, {}).get("type") == "Button" for x in parents): continue
        if str(item.get("AXLabel") or "").strip().casefold() == email.casefold(): return True
    return False


def native_digest(binary):
    binary = Path(binary)
    files = sorted(p for p in binary.parent.rglob("*") if p.is_file()) if binary.parent.suffix == ".app" else [binary]
    digest = hashlib.sha256()
    for path in files:
        digest.update(str(path.relative_to(binary.parent)).encode())
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""): digest.update(chunk)
    return digest.hexdigest()


def verify_native_binding(p, binary):
    binding = p.get("native_binding") or {}
    if binding.get("origin", "").rstrip("/") != p["server"].rstrip("/"):
        raise QAError("native build has no reviewed binding to the pinned server")
    if not re.fullmatch(r"[0-9a-f]{64}", binding.get("sha256", "")):
        raise QAError("native build needs a reviewed executable fingerprint")
    try:
        digest = native_digest(binary)
    except OSError:
        raise QAError("registered native executable is unreadable") from None
    if digest != binding["sha256"]:
        raise QAError("installed app changed; review its backend binding before registering the new build")
    if p["kind"] == "tormie" and p.get("launch_env", {}).get("TORMIE_SERVICE_URL", "").rstrip("/") != p["server"].rstrip("/"):
        raise QAError("native service override differs from the pinned server")
    if p["kind"] == "supabase" and p.get("launch_env", {}).get("SUPABASE_URL", "").rstrip("/") != p["server"].rstrip("/"):
        raise QAError("native auth override differs from the pinned server")


def open_project(config, name, screen=None, _lock_held=False):
    p = validate_profile(config["projects"][name])
    state_dir = Path(config.get("state_dir", Path.home() / ".local/state/agent-qa"))
    lock = contextlib.nullcontext() if _lock_held else SharedLock(config.get("lock_file", "/tmp/ios-automation.xcodebuild.lock"))
    with lock:
        inventory = devices()
        device = next((d for d in inventory if d["udid"] == p["simulator_id"]), None)
        if device is None: raise QAError("registered simulator is unavailable")
        foreign = [d for d in inventory if d["state"] == "Booted" and d["udid"] != device["udid"]]
        if foreign and not config.get("allow_other_booted_devices", False):
            raise QAError("another simulator is already in use; it was left untouched")
        if device["state"] != "Booted": command(["xcrun", "simctl", "boot", device["udid"]])
        command(["xcrun", "simctl", "bootstatus", device["udid"], "-b"], timeout=180)
        apps = installed_apps(device["udid"])
        app = apps.get(p["bundle_id"])
        if not app: raise QAError("registered test app is not installed; no unrelated build was substituted")
        bundle = Path(parse.unquote(parse.urlsplit(app.get("Bundle", "")).path))
        executable = app.get("CFBundleExecutable", "")
        if not bundle.is_absolute() or not re.fullmatch(r"[A-Za-z0-9_.-]+", executable):
            raise QAError("installed native executable identity is missing")
        verify_native_binding(p, bundle / executable)
        route = p["ui"]
        if not route.get("identity_anchor"):
            raise QAError("profile needs an authenticated account-surface scope")
        password = keychain_password(p)
        proof = check_credentials(p, password)
        env = dict(os.environ)
        for k, v in p.get("launch_env", {}).items(): env["SIMCTL_CHILD_" + k] = str(v)
        command(["xcrun", "simctl", "launch", "--terminate-running-process", device["udid"], p["bundle_id"], *p.get("launch_args", [])], env=env)
        ui = UI(device["udid"], config.get("axe", "axe"))
        ui.steps(route.get("account_steps", []))
        entered = False
        email_field = ui.wait(route["email_field"], route.get("login_probe_timeout", 8))
        if email_field is not None:
            value = str(email_field.get("AXValue") or "")
            if value not in ("", p["email"], route.get("email_placeholder", "Email"), "邮箱"):
                raise QAError("login form contains another identity; refusing to replace it silently")
            ui.steps(route.get("before_login_steps", []))
            if value != p["email"]: ui.fill(route["email_field"], p["email"])
            ui.fill(route["password_field"], password, secret=True)
            ui.tap(route["submit"])
            entered = True
            ui.steps([{"action": "wait_gone", "selector": route["email_field"], "timeout": 65}])
            ui.steps(route.get("after_login_steps", []))
        anchor = route.get("identity_anchor")
        if anchor and ui.wait(anchor, 40) is None:
            raise QAError("native authenticated account surface did not appear")
        end = time.monotonic() + 30
        while not visible_email(ui.tree(), p["email"], anchor):
            if time.monotonic() > end:
                raise QAError("native account surface did not prove the configured test email")
            time.sleep(0.5)
        ui.steps(route.get("leave_account_steps", []))
        target = screen or p.get("default_screen", "home")
        if target != "home":
            if target not in route.get("screens", {}): raise QAError("requested page is not configured")
            ui.steps(route["screens"][target])
        result = {"project": name, "simulator_id": device["udid"], "bundle_id": p["bundle_id"],
                  "version": app.get("CFBundleShortVersionString"), "build": app.get("CFBundleVersion"),
                  "server_identity_verified": proof["server_identity_verified"], "native_ui_identity_verified": True,
                  "login": "password_entered" if entered else "session_reused", "screen": target, "at": time.time()}
        private_json(state_dir / (name + ".json"), result)
        selected = WatchState(state_dir / "selected.json")
        selected.data[device["udid"]] = name
        private_json(selected.path, selected.data)
        WatchState(state_dir / "watch.json").record(device["udid"], boot_identity(device["udid"]), True)
        return result


def watch_once(config):
    state_dir = Path(config.get("state_dir", Path.home() / ".local/state/agent-qa"))
    if (state_dir / "paused").exists(): return []
    if subprocess.run(["/usr/bin/pgrep", "-x", "xcodebuild"], capture_output=True).returncode == 0: return []
    results = []
    for device in devices():
        if device["state"] != "Booted": continue
        choices = [name for name, p in config["projects"].items() if p.get("watch_boot") and p["simulator_id"] == device["udid"]]
        if not choices: continue
        try:
            with SharedLock(config.get("lock_file", "/tmp/ios-automation.xcodebuild.lock")):
                if (state_dir / "paused").exists(): continue
                selected = WatchState(state_dir / "selected.json").data
                state = WatchState(state_dir / "watch.json")
                fresh = next((d for d in devices() if d["udid"] == device["udid"]), {})
                if fresh.get("state") != "Booted": continue
                boot = boot_identity(device["udid"])
                if not state.due(device["udid"], boot): continue
                name = selected.get(device["udid"], config.get("default_project", choices[0]))
                if name not in choices: name = choices[0]
                try:
                    result = open_project(config, name, _lock_held=True)
                    results.append(result)
                except QAError as exc:
                    if "busy" in str(exc) or "reserved" in str(exc): continue
                    state.record(device["udid"], boot, False)
                    result = {"project": name, "status": "failed", "error": str(exc), "at": time.time()}
                    private_json(state_dir / "watch-error.json", result)
                    results.append(result)
        except QAError as exc:
            if "busy" in str(exc) or "reserved" in str(exc): continue
            raise
    return results


def load_config(path):
    path = Path(path).expanduser()
    try:
        if path.stat().st_mode & 0o077: raise QAError("private profile must have mode 600")
        config = json.loads(path.read_text())
    except (OSError, ValueError):
        raise QAError("private profile configuration is missing or unreadable") from None
    if config.get("schema_version") != 1 or not config.get("projects"):
        raise QAError("unsupported or empty profile configuration")
    for p in config["projects"].values(): validate_profile(p)
    return config


def gui_request(config, config_path, action, project, screen=None):
    state = Path(config.get("state_dir", Path.home() / ".local/state/agent-qa"))
    request_id = str(uuid.uuid4())
    path = state / "requests" / (request_id + ".json")
    result_path = state / "results" / (request_id + ".json")
    intent = state / "intents" / path.name
    private_json(intent, {"id": request_id, "action": action, "project": project, "screen": screen, "created_at": time.time()})
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.replace(intent, path)
    try:
        command(["launchctl", "kickstart", "gui/%s/com.agent-kit.product-qa-requests" % os.getuid()])
        end = time.monotonic() + 300
        while not result_path.exists():
            if time.monotonic() >= end:
                raise QAError("GUI test job has not finished; inspect its receipt before retrying")
            time.sleep(0.5)
        result = json.loads(result_path.read_text())
        result_path.unlink()
        if not result.get("ok"): raise QAError(result.get("error", "GUI test job failed"))
        return result["result"]
    except QAError:
        # Do not remove an admitted request: it may already be running.
        raise


def serve_requests(config):
    state = Path(config.get("state_dir", Path.home() / ".local/state/agent-qa"))
    queue = state / "requests"
    def reject(path):
        target = state / "rejected"
        target.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.replace(path, target / path.name)
    for path in sorted(queue.iterdir() if queue.exists() else []):
        if not path.name.endswith(".json"):
            reject(path)
            continue
        if path.is_symlink() or path.stat().st_uid != os.getuid() or path.stat().st_mode & 0o077:
            reject(path)
            continue
        try:
            item = json.loads(path.read_text())
        except (OSError, ValueError):
            reject(path)
            continue
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not re.fullmatch(r"[0-9a-f-]{36}", item["id"]) or path.stem != item["id"]:
            reject(path)
            continue
        try:
            if time.time() - item.get("created_at", 0) > 300: raise QAError("GUI test request expired")
            project = item["project"]
            if project not in config["projects"]: raise QAError("unknown registered project")
            if item["action"] == "open": result = open_project(config, project, item.get("screen"))
            elif item["action"] == "check":
                p = config["projects"][project]
                result = {"project": project, **check_credentials(p, keychain_password(p))}
            else: raise QAError("unsupported GUI test request")
            response = {"ok": True, "result": result}
        except QAError as exc:
            response = {"ok": False, "error": str(exc)}
        except Exception:
            response = {"ok": False, "error": "GUI test job failed; no sensitive tool output was retained"}
        private_json(state / "results" / path.name, response)
        path.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=os.environ.get("AGENT_QA_CONFIG", str(Path.home() / ".config/agent-qa/projects.json")))
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor")
    for name in ("open", "check"):
        sub = commands.add_parser(name)
        sub.add_argument("project")
        if name == "open": sub.add_argument("--screen")
    commands.add_parser("watch").add_argument("--once", action="store_true")
    commands.add_parser("serve")
    for name in ("pause", "resume", "status"): commands.add_parser(name)
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        state = Path(config.get("state_dir", Path.home() / ".local/state/agent-qa"))
        if args.command == "doctor":
            missing = [tool for tool in ("xcrun", "security", config.get("axe", "axe")) if not shutil.which(tool)]
            if missing: raise QAError("missing tools: " + ", ".join(missing))
            result = {"status": "configured", "projects": list(config["projects"]), "paused": (state / "paused").exists()}
        elif args.command in ("open", "check") and config.get("gui_bridge") and os.environ.get("SSH_CONNECTION"):
            result = gui_request(config, args.config, args.command, args.project, getattr(args, "screen", None))
        elif args.command == "serve":
            serve_requests(config)
            return 0
        elif args.command == "check":
            p = config["projects"][args.project]
            result = {"project": args.project, **check_credentials(p, keychain_password(p))}
        elif args.command == "open": result = open_project(config, args.project, args.screen)
        elif args.command == "watch":
            result = watch_once(config)
            if not result: return 0
        elif args.command == "pause":
            private_json(state / "paused", {"at": time.time()})
            result = {"automatic_boot_login": "paused"}
        elif args.command == "resume":
            (state / "paused").unlink(missing_ok=True)
            result = {"automatic_boot_login": "enabled"}
        else:
            result = {"paused": (state / "paused").exists(), "receipts": {p.stem: json.loads(p.read_text()) for p in state.glob("*.json") if p.stem in config["projects"] or p.stem == "watch-error"}}
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (QAError, KeyError) as exc:
        message = str(exc) if isinstance(exc, QAError) else "unknown project or incomplete UI configuration"
        print(json.dumps({"status": "failed", "error": message}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
