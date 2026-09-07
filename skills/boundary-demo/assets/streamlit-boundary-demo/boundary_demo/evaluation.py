from __future__ import annotations

from typing import Any

from .contracts import Evaluation, RunResult


def evaluate(case: dict[str, Any], result: RunResult) -> Evaluation:
    expected = case["expect"]
    mismatches: list[str] = []

    if expected.get("result_status") != result.result_status:
        mismatches.append(
            f"result_status: expected {expected.get('result_status')!r}, "
            f"observed {result.result_status!r}"
        )
    _check_subset(expected.get("output_subset", {}), result.output, "output", mismatches)
    _check_subset(
        expected.get("final_state_subset", {}),
        result.final_state,
        "final_state",
        mismatches,
    )

    trace_names = {event.name for event in result.trace}
    for name in expected.get("trace_required", []):
        if name not in trace_names:
            mismatches.append(f"trace missing required event {name!r}")
    for name in expected.get("trace_forbidden", []):
        if name in trace_names:
            mismatches.append(f"trace contains forbidden event {name!r}")

    call_count = expected.get("adapter_calls")
    if call_count is not None and call_count != len(result.adapter_calls):
        mismatches.append(
            f"adapter_calls: expected {call_count}, observed {len(result.adapter_calls)}"
        )
    return Evaluation("pass" if not mismatches else "fail", tuple(mismatches))


def _check_subset(
    expected: Any,
    observed: Any,
    path: str,
    mismatches: list[str],
) -> None:
    if isinstance(expected, dict):
        if not isinstance(observed, dict):
            mismatches.append(f"{path}: expected mapping, observed {type(observed).__name__}")
            return
        for key, value in expected.items():
            if key not in observed:
                mismatches.append(f"{path}.{key}: missing")
            else:
                _check_subset(value, observed[key], f"{path}.{key}", mismatches)
        return
    if expected != observed:
        mismatches.append(f"{path}: expected {expected!r}, observed {observed!r}")
