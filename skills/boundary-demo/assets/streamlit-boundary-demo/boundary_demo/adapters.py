from __future__ import annotations

from copy import deepcopy
from typing import Any, Protocol


class AdapterTimeout(RuntimeError):
    pass


class AdapterRejected(RuntimeError):
    pass


class Adapter(Protocol):
    calls: list[dict[str, Any]]

    def dispatch(self, request: dict[str, Any]) -> dict[str, Any]: ...


class FakeAdapter:
    """Deterministic fake. The starter intentionally has no real adapter."""

    def __init__(self, scenario: str = "success") -> None:
        if scenario not in {"success", "timeout", "reject"}:
            raise ValueError(f"Unsupported fake scenario: {scenario}")
        self.scenario = scenario
        self.calls: list[dict[str, Any]] = []

    def dispatch(self, request: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(deepcopy(request))
        if self.scenario == "timeout":
            raise AdapterTimeout("Synthetic downstream timeout")
        if self.scenario == "reject":
            raise AdapterRejected("Synthetic downstream rejection")
        return {"receipt_id": f"fake-{request['request_id']}", "committed": True}
