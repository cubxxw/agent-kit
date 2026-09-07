from __future__ import annotations

from copy import deepcopy
from typing import Any

from .adapters import Adapter, AdapterRejected, AdapterTimeout
from .contracts import RunResult, TraceEvent


def run_case(case: dict[str, Any], adapter: Adapter) -> RunResult:
    case_id = str(case["id"])
    given = case["given"]
    request = deepcopy(given["input"])
    initial_state = deepcopy(given["initial_state"])
    state = deepcopy(initial_state)
    trace: list[TraceEvent] = []

    def record(name: str, detail: str) -> None:
        trace.append(TraceEvent(len(trace) + 1, name, detail))

    record("input.received", f"case={case_id}")
    request_id = request.get("request_id")
    payload = request.get("payload")
    authorized = request.get("authorized")
    run_id = f"{case_id}:{request_id or 'invalid'}"

    if not isinstance(request_id, str) or not request_id.strip():
        state["status"] = "invalid_input"
        record("input.invalid", "request_id is required")
        return _result(
            run_id,
            case_id,
            "invalid_input",
            request,
            initial_state,
            state,
            {"status": "invalid_input", "committed": False, "retryable": False},
            trace,
            adapter,
        )
    if not isinstance(payload, str) or not payload.strip():
        state["status"] = "invalid_input"
        record("input.invalid", "payload is required")
        return _result(
            run_id,
            case_id,
            "invalid_input",
            request,
            initial_state,
            state,
            {"status": "invalid_input", "committed": False, "retryable": False},
            trace,
            adapter,
        )
    if not isinstance(authorized, bool):
        state["status"] = "invalid_input"
        record("input.invalid", "authorized must be boolean")
        return _result(
            run_id,
            case_id,
            "invalid_input",
            request,
            initial_state,
            state,
            {"status": "invalid_input", "committed": False, "retryable": False},
            trace,
            adapter,
        )

    record("input.validated", f"request_id={request_id}")
    if not authorized:
        state["status"] = "policy_rejected"
        record("policy.denied", "explicit authorization is absent")
        return _result(
            run_id,
            case_id,
            "policy_rejected",
            request,
            initial_state,
            state,
            {"status": "policy_rejected", "committed": False, "retryable": False},
            trace,
            adapter,
        )

    state["status"] = "dispatching"
    record("policy.allowed", "explicit authorization is present")
    record("adapter.called", "fake adapter invoked once")
    try:
        response = adapter.dispatch(request)
    except AdapterTimeout:
        state["status"] = "retryable_error"
        record("adapter.timeout", "downstream outcome is unknown")
        return _result(
            run_id,
            case_id,
            "handled_error",
            request,
            initial_state,
            state,
            {"status": "handled_error", "committed": False, "retryable": True},
            trace,
            adapter,
        )
    except AdapterRejected:
        state["status"] = "downstream_rejected"
        record("adapter.rejected", "downstream explicitly rejected the request")
        return _result(
            run_id,
            case_id,
            "handled_error",
            request,
            initial_state,
            state,
            {"status": "handled_error", "committed": False, "retryable": False},
            trace,
            adapter,
        )

    state["status"] = "completed"
    state.setdefault("commits", []).append(response["receipt_id"])
    record("write.committed", "fake downstream confirmed the commit")
    return _result(
        run_id,
        case_id,
        "completed",
        request,
        initial_state,
        state,
        {"status": "completed", "committed": True, "retryable": False},
        trace,
        adapter,
    )


def _result(
    run_id: str,
    case_id: str,
    result_status: str,
    request: dict[str, Any],
    initial_state: dict[str, Any],
    final_state: dict[str, Any],
    output: dict[str, Any],
    trace: list[TraceEvent],
    adapter: Adapter,
) -> RunResult:
    return RunResult(
        run_id=run_id,
        case_id=case_id,
        result_status=result_status,
        input=deepcopy(request),
        initial_state=deepcopy(initial_state),
        final_state=deepcopy(final_state),
        output=deepcopy(output),
        trace=tuple(trace),
        adapter_calls=tuple(deepcopy(adapter.calls)),
    )
