from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_TYPES = {"normal", "edge", "failure"}


def load_cases(directory: Path, *, require_triplet: bool = True) -> list[dict[str, Any]]:
    cases = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(directory.glob("*.json"))
    ]
    if not cases:
        raise ValueError(f"No JSON cases found in {directory}")
    ids: set[str] = set()
    for case in cases:
        validate_case(case)
        if case["id"] in ids:
            raise ValueError(f"Duplicate case id: {case['id']}")
        ids.add(case["id"])
    if require_triplet:
        missing = REQUIRED_TYPES - {case["case_type"] for case in cases}
        if missing:
            raise ValueError(f"Missing required case types: {', '.join(sorted(missing))}")
    return cases


def validate_case(case: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "id",
        "case_type",
        "source",
        "split",
        "purpose",
        "given",
        "expect",
        "review",
    }
    missing = required - case.keys()
    if missing:
        raise ValueError(f"Case missing fields: {', '.join(sorted(missing))}")
    if case["schema_version"] != 1:
        raise ValueError("Unsupported case schema_version")
    if case["case_type"] not in REQUIRED_TYPES:
        raise ValueError(f"Unsupported case_type: {case['case_type']}")
    if case["source"] not in {"synthetic", "real"}:
        raise ValueError(f"Unsupported source: {case['source']}")
    if case["split"] not in {"discovery", "regression", "holdout"}:
        raise ValueError(f"Unsupported split: {case['split']}")
    review_status = case["review"].get("status")
    if review_status not in {"unreviewed", "confirmed", "rejected"}:
        raise ValueError("Unsupported review.status")
    if case["split"] == "regression" and review_status != "confirmed":
        raise ValueError("regression cases require confirmed review.status")
    if not isinstance(case["given"].get("input"), dict):
        raise ValueError("given.input must be a mapping")
    if not isinstance(case["given"].get("initial_state"), dict):
        raise ValueError("given.initial_state must be a mapping")
    if case["given"].get("adapter", {}).get("scenario") not in {
        "success",
        "timeout",
        "reject",
    }:
        raise ValueError("given.adapter.scenario must use the deterministic fake")
