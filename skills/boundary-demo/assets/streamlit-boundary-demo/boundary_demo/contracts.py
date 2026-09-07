from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class TraceEvent:
    seq: int
    name: str
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RunResult:
    run_id: str
    case_id: str
    result_status: str
    input: dict[str, Any]
    initial_state: dict[str, Any]
    final_state: dict[str, Any]
    output: dict[str, Any]
    trace: tuple[TraceEvent, ...]
    adapter_calls: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["trace"] = [event.to_dict() for event in self.trace]
        payload["adapter_calls"] = list(payload["adapter_calls"])
        return payload


@dataclass(frozen=True)
class Evaluation:
    verdict: str
    mismatches: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
