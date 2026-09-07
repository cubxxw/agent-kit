#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_ROOT / "assets" / "streamlit-boundary-demo"
TEXT_SUFFIXES = {".md", ".py", ".toml", ".json"}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "boundary-demo"


def initialize(target: Path, *, name: str, question: str) -> None:
    if not name.strip():
        raise ValueError("Demo name must not be blank")
    if not question.strip():
        raise ValueError("Decision question must not be blank")
    target = target.expanduser().absolute()
    if target == Path(target.anchor) or target == Path.home():
        raise ValueError("Refusing to scaffold into a filesystem root or home directory")
    if target.exists() or target.is_symlink():
        raise ValueError(f"Target already exists: {target}")

    replacements = {
        "{{DEMO_NAME}}": name,
        "{{DEMO_NAME_PY}}": json.dumps(name, ensure_ascii=False),
        "{{PACKAGE_NAME}}": slugify(name),
        "{{QUESTION}}": question,
        "{{QUESTION_PY}}": json.dumps(question, ensure_ascii=False),
    }
    token_pattern = re.compile("|".join(re.escape(token) for token in replacements))
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=f".{target.name}-staging-", dir=target.parent
    ) as staging_parent:
        staging = Path(staging_parent) / "scaffold"
        shutil.copytree(
            TEMPLATE,
            staging,
            ignore=shutil.ignore_patterns("__pycache__", "*.py[cod]", ".DS_Store"),
        )
        for candidate in staging.rglob("*"):
            if not candidate.is_file() or candidate.suffix not in TEXT_SUFFIXES:
                continue
            content = candidate.read_text(encoding="utf-8")
            content = token_pattern.sub(
                lambda match: replacements[match.group(0)], content
            )
            candidate.write_text(content, encoding="utf-8")

        if target.exists() or target.is_symlink():
            raise ValueError(f"Target appeared during initialization: {target}")
        staging.rename(target)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create an isolated, case-driven Streamlit boundary demo."
    )
    parser.add_argument("target", type=Path)
    parser.add_argument("--question", required=True)
    parser.add_argument("--name")
    args = parser.parse_args()

    name = args.name or args.target.name.replace("-", " ").title()
    try:
        initialize(args.target, name=name, question=args.question)
    except ValueError as exc:
        parser.error(str(exc))

    resolved = args.target.expanduser().resolve(strict=False)
    print(f"Created boundary demo at {resolved}")
    print("Next: run `uv lock`, `uv sync --extra test`, and `uv run python -m pytest`.")
    print("Start it from the demo root with `uv run streamlit run streamlit_app.py`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
