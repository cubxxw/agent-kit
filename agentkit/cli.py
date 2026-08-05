from __future__ import annotations

import argparse
import sys

from .core import (
    AgentKitError,
    SUPPORTED_TOOLS,
    install_links,
    installation_status,
    scan_public_tree,
    uninstall_links,
    validate_catalog,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-kit",
        description="Manage one canonical Agent Skills library across coding agents.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    tool_choices = ("core", "all", *SUPPORTED_TOOLS)

    install = subparsers.add_parser(
        "install", help="Link a profile into one or more agents"
    )
    install.add_argument("--profile", default="base")
    install.add_argument("--tool", choices=tool_choices, default="core")
    install.add_argument("--dry-run", action="store_true")
    install.add_argument(
        "--replace-managed",
        action="store_true",
        help="Replace only stale symlinks that already point into this repository.",
    )

    uninstall = subparsers.add_parser(
        "uninstall", help="Remove links owned by this checkout"
    )
    uninstall.add_argument("--profile", default="base")
    uninstall.add_argument("--tool", choices=tool_choices, default="core")
    uninstall.add_argument("--dry-run", action="store_true")

    status = subparsers.add_parser("status", help="Show link state for a profile")
    status.add_argument("--profile", default="base")
    status.add_argument("--tool", choices=tool_choices, default="core")

    doctor = subparsers.add_parser(
        "doctor", help="Validate the catalog and public repository boundary"
    )
    doctor.add_argument(
        "--strict", action="store_true", help="Treat warnings as failures"
    )

    subparsers.add_parser("scan", help="Scan tracked files for public-repo hazards")
    return parser


def print_findings(findings: list) -> None:
    if not findings:
        print("OK    no findings")
        return
    for finding in findings:
        print(finding.render())


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "install":
            for message in install_links(
                args.profile,
                args.tool,
                dry_run=args.dry_run,
                replace_managed=args.replace_managed,
            ):
                print(message)
            return 0
        if args.command == "uninstall":
            for message in uninstall_links(
                args.profile, args.tool, dry_run=args.dry_run
            ):
                print(message)
            return 0
        if args.command == "status":
            for row in installation_status(args.profile, args.tool):
                print(row)
            return 0
        if args.command == "scan":
            findings = scan_public_tree()
            print_findings(findings)
            return 1 if any(item.level == "error" for item in findings) else 0
        if args.command == "doctor":
            findings = validate_catalog() + scan_public_tree()
            print_findings(findings)
            errors = any(item.level == "error" for item in findings)
            warnings = any(item.level == "warn" for item in findings)
            return 1 if errors or (args.strict and warnings) else 0
    except AgentKitError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
