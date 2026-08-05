#!/usr/bin/env python3
"""Refresh one vendored skill from a reviewed upstream commit."""

from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "catalog.json"


def request(url: str) -> bytes:
    headers = {"User-Agent": "cubxxw-agent-kit"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(
        urllib.request.Request(url, headers=headers), timeout=60
    ) as response:
        return response.read()


def latest_sha(repository: str, track: str) -> str:
    data = json.loads(
        request(f"https://api.github.com/repos/{repository}/commits/{track}")
    )
    return data["sha"]


def ensure_clean(destination: Path) -> None:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--", str(destination.relative_to(ROOT))],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    if result.stdout.strip():
        raise SystemExit(
            f"Refusing to replace locally modified vendor directory: {destination}"
        )


def extract_subtree(archive: bytes, source_path: str, destination: Path) -> None:
    source_parts = PurePosixPath(source_path).parts
    matched = 0
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        for info in bundle.infolist():
            parts = PurePosixPath(info.filename).parts
            if len(parts) <= len(source_parts):
                continue
            if tuple(parts[1 : 1 + len(source_parts)]) != source_parts:
                continue
            remainder = parts[1 + len(source_parts) :]
            if not remainder or info.is_dir():
                continue
            if any(part in ("", ".", "..") for part in remainder):
                raise SystemExit("Unsafe path in upstream archive")
            target = destination.joinpath(*remainder)
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(info) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
            matched += 1
    if matched == 0 or not (destination / "SKILL.md").is_file():
        raise SystemExit(f"No valid skill found at upstream path '{source_path}'")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill")
    parser.add_argument(
        "--ref", help="Reviewed full commit SHA; defaults to the tracked branch head"
    )
    args = parser.parse_args()

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    entry = next(
        (item for item in catalog["skills"] if item["name"] == args.skill), None
    )
    if not entry or entry.get("source", {}).get("type") != "vendored":
        raise SystemExit(f"'{args.skill}' is not a vendored skill")

    source = entry["source"]
    ref = args.ref or latest_sha(source["repository"], source.get("track", "main"))
    if len(ref) != 40 or any(char not in "0123456789abcdef" for char in ref):
        raise SystemExit("Vendor ref must be a full lowercase commit SHA")

    destination = (ROOT / entry["path"]).resolve()
    ensure_clean(destination)
    archive = request(
        f"https://api.github.com/repos/{source['repository']}/zipball/{ref}"
    )
    with tempfile.TemporaryDirectory(prefix="agent-kit-vendor-") as tmp:
        staged = Path(tmp) / entry["name"]
        staged.mkdir()
        extract_subtree(archive, source["path"], staged)
        if not (staged / "LICENSE.txt").is_file():
            raise SystemExit("Upstream skill has no LICENSE.txt; refusing to vendor")
        shutil.rmtree(destination)
        shutil.copytree(staged, destination)

    source["ref"] = ref
    CATALOG_PATH.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Updated {entry['name']} to {ref}")
    print("Run ./bin/agent-kit doctor --strict and review the diff before committing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
