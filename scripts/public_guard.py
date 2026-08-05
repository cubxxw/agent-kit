#!/usr/bin/env python3
"""Block obvious secret leaks while an agent edits this public repository."""

from __future__ import annotations

import json
import re
import sys


BLOCKED_PATHS = (
    ".env",
    "auth.json",
    "credentials.json",
    ".ssh/",
    ".aws/",
    ".codex/auth.json",
    ".claude.json",
)
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)
KEYCHAIN_COMMANDS = (
    "security find-generic-password",
    "security find-internet-password",
)


def deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


def find_reason(payload: dict) -> str | None:
    tool_input = payload.get("tool_input", {})
    serialized = json.dumps(tool_input, ensure_ascii=False)
    lowered = serialized.lower()

    for path in BLOCKED_PATHS:
        if path.lower() in lowered:
            return f"Public-repo guard blocked access to secret-bearing path: {path}"
    for command in KEYCHAIN_COMMANDS:
        if command in lowered:
            return "Public-repo guard blocked credential extraction from the keychain."
    for pattern in SECRET_PATTERNS:
        if pattern.search(serialized):
            return "Public-repo guard detected content shaped like a credential."
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0
    reason = find_reason(payload)
    if reason:
        deny(reason)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
