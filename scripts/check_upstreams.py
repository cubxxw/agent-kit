#!/usr/bin/env python3
"""Report whether vendored skills have newer upstream commits."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def github_json(path: str) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "cubxxw-agent-kit",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(f"https://api.github.com/{path}", headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def subtree_sha(repository: str, ref: str, source_path: str) -> str:
    tree = github_json(f"repos/{repository}/git/trees/{ref}?recursive=1")
    for item in tree.get("tree", []):
        if item.get("path") == source_path and item.get("type") == "tree":
            return item["sha"]
    raise KeyError(f"tree not found: {repository}:{source_path}@{ref}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fail-on-drift", action="store_true")
    args = parser.parse_args()

    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    drift = False
    checked = 0
    try:
        for skill in catalog["skills"]:
            source = skill.get("source", {})
            if source.get("type") != "vendored":
                continue
            checked += 1
            track = source.get("track", "main")
            latest_tree = subtree_sha(
                source["repository"], track, source["path"]
            )
            current_tree = source["tree_sha"]
            if latest_tree != current_tree:
                drift = True
                latest_commit = github_json(
                    f"repos/{source['repository']}/commits/{track}"
                )["sha"]
                print(
                    f"UPDATE {skill['name']}: tree {current_tree[:12]} -> "
                    f"{latest_tree[:12]} at {latest_commit[:12]} "
                    f"({source['repository']}:{source['path']})"
                )
            else:
                print(
                    f"OK     {skill['name']}: tree {current_tree[:12]} "
                    f"(pinned at {source['ref'][:12]})"
                )
    except (KeyError, OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        print(f"ERROR  upstream check failed: {exc}", file=sys.stderr)
        return 2

    if checked == 0:
        print("OK     no vendored upstreams")
    return 1 if drift and args.fail_on_drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
