from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "catalog.json"
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CORE_TOOLS = ("codex", "claude")
SUPPORTED_TOOLS = ("codex", "claude", "qwen", "opencode", "pi", "openclaw")

SECRET_PATTERNS = (
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("OpenAI-style API key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
    ("Anthropic API key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
)
PRIVATE_PATH_PATTERNS = (
    re.compile(r"/Users/(?P<user>[A-Za-z0-9._-]+)/"),
    re.compile(r"/home/(?P<user>[A-Za-z0-9._-]+)/"),
)
PUBLIC_HOME_PLACEHOLDERS = {
    "example",
    "me",
    "name",
    "user",
    "username",
    "yourname",
}
FORBIDDEN_FILENAMES = {
    ".env",
    ".env.local",
    ".npmrc",
    "auth.json",
    "credentials.json",
    "id_rsa",
    "id_ed25519",
}


class AgentKitError(RuntimeError):
    pass


@dataclass(frozen=True)
class Finding:
    level: str
    path: str
    message: str

    def render(self) -> str:
        return f"{self.level.upper():5} {self.path}: {self.message}"


def load_catalog(path: Path = CATALOG_PATH) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AgentKitError(f"Cannot read catalog: {exc}") from exc


def skill_map(catalog: dict) -> dict[str, dict]:
    return {item["name"]: item for item in catalog.get("skills", [])}


def resolve_profile(catalog: dict, profile: str) -> list[str]:
    profiles = catalog.get("profiles", {})
    if profile not in profiles:
        raise AgentKitError(
            f"Unknown profile '{profile}'. Available: {', '.join(sorted(profiles))}"
        )

    resolved: list[str] = []
    active: set[str] = set()

    def visit(name: str) -> None:
        if name in active:
            raise AgentKitError(f"Profile cycle detected at '{name}'")
        if name not in profiles:
            raise AgentKitError(f"Profile '{profile}' extends missing profile '{name}'")
        active.add(name)
        for parent in profiles[name].get("extends", []):
            visit(parent)
        for skill in profiles[name].get("skills", []):
            if skill not in resolved:
                resolved.append(skill)
        active.remove(name)

    visit(profile)
    return resolved


def tool_directories() -> dict[str, Path]:
    home = Path.home()
    return {
        "codex": Path(
            os.environ.get("AGENT_KIT_CODEX_SKILLS_DIR", home / ".agents" / "skills")
        ).expanduser(),
        "claude": Path(
            os.environ.get(
                "AGENT_KIT_CLAUDE_SKILLS_DIR", home / ".claude" / "skills"
            )
        ).expanduser(),
        "qwen": Path(
            os.environ.get("AGENT_KIT_QWEN_SKILLS_DIR", home / ".qwen" / "skills")
        ).expanduser(),
        "opencode": Path(
            os.environ.get(
                "AGENT_KIT_OPENCODE_SKILLS_DIR",
                home / ".config" / "opencode" / "skills",
            )
        ).expanduser(),
        "pi": Path(
            os.environ.get(
                "AGENT_KIT_PI_SKILLS_DIR", home / ".pi" / "agent" / "skills"
            )
        ).expanduser(),
        "openclaw": Path(
            os.environ.get(
                "AGENT_KIT_OPENCLAW_SKILLS_DIR", home / ".openclaw" / "skills"
            )
        ).expanduser(),
    }


def selected_tools(tool: str) -> dict[str, Path]:
    directories = tool_directories()
    if tool == "all":
        return directories
    if tool == "core":
        return {name: directories[name] for name in CORE_TOOLS}
    if tool not in directories:
        available = ", ".join(("core", "all", *SUPPORTED_TOOLS))
        raise AgentKitError(f"Unsupported tool '{tool}'. Available: {available}")
    return {tool: directories[tool]}


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def link_state(destination: Path, source: Path) -> str:
    if destination.is_symlink():
        current = destination.resolve(strict=False)
        if current == source.resolve():
            return "linked"
        if is_relative_to(current, ROOT.resolve()):
            return "managed-drift"
        return "foreign-link"
    if destination.exists():
        return "conflict"
    return "missing"


def plan_install_links(
    profile: str,
    tool: str = "core",
    *,
    replace_managed: bool = False,
) -> dict:
    """Inspect every selected destination without changing the filesystem."""
    catalog = load_catalog()
    entries = skill_map(catalog)
    directories = selected_tools(tool)
    actions: list[dict] = []
    scheduled: dict[Path, str] = {}

    for name in resolve_profile(catalog, profile):
        source = None
        source_error = ""
        if not SKILL_NAME_RE.fullmatch(name) or len(name) > 64:
            source_error = (
                f"Invalid skill name '{name}'. Fix the catalog: use 1-64 lowercase "
                "letters or digits with single hyphens between words."
            )
        elif name not in entries:
            source_error = f"Profile '{profile}' references unknown skill '{name}'. Fix the catalog."
        else:
            source = (ROOT / entries[name]["path"]).resolve()
            if not is_relative_to(source, ROOT.resolve()):
                source_error = f"Skill source escapes repository: {source}. Fix the catalog."
            elif not (source / "SKILL.md").is_file():
                source_error = f"Skill source is incomplete: {source}. Restore the skill source."

        for tool_name, directory in directories.items():
            destination = directory.absolute() / name
            resolved_destination = None
            if source_error:
                state, action, reason = "invalid-source", "conflict", source_error
            else:
                parent_conflict = next(
                    (
                        parent
                        for parent in (destination.parent, *destination.parent.parents)
                        if (parent.exists() or parent.is_symlink()) and not parent.is_dir()
                    ),
                    None,
                )
                if parent_conflict is not None:
                    state, action = "parent-conflict", "conflict"
                    reason = (
                        f"Parent path {parent_conflict} is not a directory. "
                        "Move it aside explicitly or choose another skills directory."
                    )
                else:
                    resolved_destination = destination.parent.resolve() / destination.name
                    state = link_state(destination, source)
                    if state == "missing":
                        action, reason = "link", "Create a link to the canonical skill source."
                    elif state == "linked":
                        action, reason = "noop", "Already linked to this skill source."
                    elif state == "managed-drift" and replace_managed:
                        action, reason = "replace", "Replace an old symlink into this repository."
                    elif state == "managed-drift":
                        action = "conflict"
                        reason = (
                            "Old symlink points into this repository. Rerun with "
                            "--replace-managed or move it aside explicitly."
                        )
                    else:
                        action = "conflict"
                        reason = (
                            "Symlink points outside this repository. "
                            if state == "foreign-link"
                            else "A real file or directory occupies this destination. "
                        ) + "Move it aside explicitly and rerun the plan."
                    if action in {"link", "replace"}:
                        if resolved_destination in scheduled:
                            action = "noop"
                            reason = (
                                f"Shares this destination with {scheduled[resolved_destination]}; "
                                "that planned link covers this tool."
                            )
                        else:
                            scheduled[resolved_destination] = tool_name
            actions.append(
                {
                    "tool": tool_name,
                    "skill": name,
                    "source": str(source) if source is not None else None,
                    "destination": str(destination),
                    "resolved_destination": str(resolved_destination) if resolved_destination is not None else None,
                    "state": state,
                    "action": action,
                    "reason": reason,
                }
            )

    physical_actions = [
        (
            row,
            Path(row["resolved_destination"]),
        )
        for row in actions
        if row["action"] != "conflict"
    ]
    mutating_targets = {
        location: row
        for row, location in physical_actions
        if row["action"] in {"link", "replace"}
    }
    protected_sources = [(ROOT / entry["path"]).resolve() for entry in entries.values()]
    for row, location in physical_actions:
        if any(is_relative_to(location, source) for source in protected_sources):
            row["state"], row["action"] = "source-conflict", "conflict"
            row["reason"] = (
                "This destination is inside a canonical skill source. "
                "Choose a skills directory outside all canonical skill sources."
            )
            continue
        for parent in Path(row["destination"]).parents:
            parent_location = parent.parent.resolve() / parent.name
            if parent_location in mutating_targets and parent_location != location:
                ancestor = mutating_targets[parent_location]
                row["state"], row["action"] = "nested-target-conflict", "conflict"
                row["reason"] = (
                    f"This destination passes through another planned skill link: "
                    f"{ancestor['destination']}. Choose non-nested skills directories."
                )
                break

    conflicts = [row for row in actions if row["action"] == "conflict"]
    return {
        "schema_version": 1,
        "profile": profile,
        "ready": not conflicts,
        "actions": actions,
        "conflicts": conflicts,
    }


def render_install_plan(plan: dict) -> list[str]:
    rows = [f"Plan for {plan['profile']}: {'ready' if plan['ready'] else 'blocked'}"]
    for row in plan["actions"]:
        rows.append(
            f"{row['tool']}: {row['skill']} [{row['state']}] {row['action']} "
            f"{row['source']} -> {row['destination']}: {row['reason']}"
        )
    rows.append("No changes made.")
    return rows


def install_links(
    profile: str,
    tool: str = "core",
    *,
    dry_run: bool = False,
    replace_managed: bool = False,
) -> list[str]:
    plan = plan_install_links(profile, tool, replace_managed=replace_managed)
    if not plan["ready"]:
        conflicts = [
            f"{row['tool']}: {row['destination']} ({row['state']}): {row['reason']}"
            for row in plan["conflicts"]
        ]
        raise AgentKitError("Installation blocked. No changes made.\n" + "\n".join(conflicts))

    messages: list[str] = []
    completed: list[str] = []
    canonical_sources = [ROOT / entry["path"] for entry in skill_map(load_catalog()).values()]
    prefix = "[dry-run] " if dry_run else ""
    for row in plan["actions"]:
        tool_name, name = row["tool"], row["skill"]
        source, destination = Path(row["source"]), Path(row["destination"])
        if dry_run and row["action"] == "noop":
            messages.append(f"{prefix}{tool_name}: {name} already linked")
            continue
        removed = False
        try:
            if not dry_run:
                resolved_destination = destination.parent.resolve() / destination.name
                if str(resolved_destination) != row["resolved_destination"]:
                    raise AgentKitError(
                        f"Destination path changed since preflight: expected "
                        f"{row['resolved_destination']}, now {resolved_destination}; "
                        "rerun plan before installing"
                    )
                if any(
                    is_relative_to(resolved_destination, boundary.resolve())
                    for boundary in canonical_sources
                ):
                    raise AgentKitError(
                        "Destination is now inside a canonical skill source; "
                        "rerun plan with a skills directory outside all canonical sources"
                    )
                current = link_state(destination, source)
                if current == "linked":
                    messages.append(f"{tool_name}: {name} already linked")
                    continue
                if current != row["state"] or row["action"] == "noop":
                    raise AgentKitError(
                        f"Target changed since preflight ({current}); rerun plan before installing"
                    )
                destination.parent.mkdir(parents=True, exist_ok=True)
                if row["action"] == "replace":
                    destination.unlink()
                    removed = True
                destination.symlink_to(source, target_is_directory=True)
                completed.append(str(destination))
        except (OSError, AgentKitError) as exc:
            changed = "\n".join(completed) or "none"
            removed_note = " The old managed symlink was removed at the failed target." if removed else ""
            raise AgentKitError(
                f"Installation stopped at {destination}: {exc}.{removed_note}\n"
                f"Links completed before the error:\n{changed}\n"
                "Created parent directories may remain. Inspect these paths and rerun plan."
            ) from exc
        messages.append(f"{prefix}{tool_name}: linked {name} -> {source}")
    return messages


def uninstall_links(
    profile: str, tool: str = "core", *, dry_run: bool = False
) -> list[str]:
    catalog = load_catalog()
    entries = skill_map(catalog)
    messages: list[str] = []
    for name in resolve_profile(catalog, profile):
        source = (ROOT / entries[name]["path"]).resolve()
        for tool_name, directory in selected_tools(tool).items():
            destination = directory / name
            if link_state(destination, source) == "linked":
                if not dry_run:
                    destination.unlink()
                prefix = "[dry-run] " if dry_run else ""
                messages.append(f"{prefix}{tool_name}: removed {destination}")
            else:
                messages.append(f"{tool_name}: left {destination} unchanged")
    return messages


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise AgentKitError(f"{path}: missing YAML frontmatter")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise AgentKitError(f"{path}: unterminated YAML frontmatter") from exc
    values: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.match(r"^([a-zA-Z0-9_-]+):\s*(.*)$", line)
        if match:
            values[match.group(1)] = match.group(2).strip().strip("\"'")
    return values


def validate_catalog(catalog: dict | None = None) -> list[Finding]:
    catalog = catalog or load_catalog()
    findings: list[Finding] = []
    if catalog.get("schema_version") != 1:
        findings.append(Finding("error", "catalog.json", "schema_version must be 1"))

    entries = catalog.get("skills")
    if not isinstance(entries, list) or not entries:
        findings.append(Finding("error", "catalog.json", "skills must be non-empty"))
        return findings

    seen: set[str] = set()
    for entry in entries:
        name = entry.get("name", "")
        relpath = entry.get("path", "")
        label = relpath or name or "catalog.json"
        if name in seen:
            findings.append(Finding("error", label, f"duplicate skill '{name}'"))
        seen.add(name)
        if not SKILL_NAME_RE.fullmatch(name) or len(name) > 64:
            findings.append(Finding("error", label, f"invalid skill name '{name}'"))
        path = (ROOT / relpath).resolve()
        if not is_relative_to(path, ROOT.resolve()):
            findings.append(Finding("error", label, "path escapes repository"))
            continue
        skill_file = path / "SKILL.md"
        if not skill_file.is_file():
            findings.append(Finding("error", label, "missing SKILL.md"))
            continue
        try:
            frontmatter = parse_frontmatter(skill_file)
        except (AgentKitError, UnicodeDecodeError) as exc:
            findings.append(Finding("error", label, str(exc)))
            continue
        if frontmatter.get("name") != name:
            findings.append(
                Finding(
                    "error",
                    label,
                    f"frontmatter name '{frontmatter.get('name')}' does not match catalog",
                )
            )
        description = frontmatter.get("description", "")
        if not description or len(description) > 1024:
            findings.append(
                Finding("error", label, "description must contain 1-1024 characters")
            )
        if path.name != name:
            findings.append(
                Finding("error", label, "skill directory must match skill name")
            )

        source = entry.get("source", {})
        if source.get("type") == "vendored":
            ref = source.get("ref", "")
            if not re.fullmatch(r"[0-9a-f]{40}", ref):
                findings.append(
                    Finding("error", label, "vendored source ref must be a full SHA")
                )
            tree_sha = source.get("tree_sha", "")
            if not re.fullmatch(r"[0-9a-f]{40}", tree_sha):
                findings.append(
                    Finding(
                        "error", label, "vendored source tree_sha must be a full SHA"
                    )
                )
            if not (path / "LICENSE.txt").is_file():
                findings.append(
                    Finding("error", label, "vendored skill must carry LICENSE.txt")
                )

    for profile, value in catalog.get("profiles", {}).items():
        try:
            names = resolve_profile(catalog, profile)
        except AgentKitError as exc:
            findings.append(Finding("error", f"profile:{profile}", str(exc)))
            continue
        for name in names:
            if name not in seen:
                findings.append(
                    Finding(
                        "error",
                        f"profile:{profile}",
                        f"references unknown skill '{name}'",
                    )
                )
    return findings


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode == 0:
        candidates = [
            ROOT / os.fsdecode(item)
            for item in result.stdout.split(b"\0")
            if item
        ]
        return [path for path in candidates if path.exists() or path.is_symlink()]
    return [path for path in ROOT.rglob("*") if path.is_file()]


def scan_public_tree(paths: Iterable[Path] | None = None) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths or tracked_files():
        try:
            relative = path.relative_to(ROOT)
        except ValueError:
            relative = path
        if path.name in FORBIDDEN_FILENAMES:
            findings.append(
                Finding("error", str(relative), "forbidden secret-bearing filename")
            )
        if path.is_symlink():
            target = path.resolve(strict=False)
            if not is_relative_to(target, ROOT.resolve()):
                findings.append(
                    Finding("error", str(relative), "symlink escapes repository")
                )
            continue
        try:
            raw = path.read_bytes()
        except OSError as exc:
            findings.append(Finding("error", str(relative), f"cannot read: {exc}"))
            continue
        if b"\0" in raw[:8192]:
            continue
        if len(raw) > 2_000_000:
            findings.append(Finding("warn", str(relative), "text file exceeds 2 MB"))
        text = raw.decode("utf-8", errors="replace")
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(Finding("error", str(relative), f"possible {label}"))
        for pattern in PRIVATE_PATH_PATTERNS:
            matches = [
                match
                for match in pattern.finditer(text)
                if match.group("user").lower() not in PUBLIC_HOME_PLACEHOLDERS
            ]
            if matches:
                findings.append(
                    Finding("error", str(relative), "contains an absolute home path")
                )
    return findings


def installation_status(profile: str, tool: str = "core") -> list[str]:
    catalog = load_catalog()
    entries = skill_map(catalog)
    rows: list[str] = []
    for name in resolve_profile(catalog, profile):
        source = (ROOT / entries[name]["path"]).resolve()
        for tool_name, directory in selected_tools(tool).items():
            destination = directory / name
            rows.append(
                f"{tool_name:6} {name:24} {link_state(destination, source):14} "
                f"{destination}"
            )
    return rows
