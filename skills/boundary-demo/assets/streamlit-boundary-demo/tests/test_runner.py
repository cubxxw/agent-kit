from copy import deepcopy
from pathlib import Path

from boundary_demo.adapters import FakeAdapter
from boundary_demo.cases import load_cases
from boundary_demo.evaluation import evaluate
from boundary_demo.runner import run_case


ROOT = Path(__file__).resolve().parents[1]


def test_all_seed_cases_pass_without_mutating_the_case() -> None:
    for case in load_cases(ROOT / "cases"):
        original = deepcopy(case)
        adapter = FakeAdapter(case["given"]["adapter"]["scenario"])
        result = run_case(case, adapter)
        assert evaluate(case, result).verdict == "pass"
        assert case == original


def test_invalid_input_never_calls_adapter() -> None:
    case = deepcopy(load_cases(ROOT / "cases")[0])
    case["given"]["input"]["payload"] = ""
    adapter = FakeAdapter("success")
    result = run_case(case, adapter)
    assert result.result_status == "invalid_input"
    assert result.adapter_calls == ()
    assert "write.committed" not in {event.name for event in result.trace}


def test_timeout_never_claims_a_commit() -> None:
    case = next(
        case
        for case in load_cases(ROOT / "cases")
        if case["id"] == "failure-timeout"
    )
    result = run_case(case, FakeAdapter("timeout"))
    assert result.output["committed"] is False
    assert result.final_state["commits"] == []
    assert "write.committed" not in {event.name for event in result.trace}


def test_serialized_adapter_calls_are_detached() -> None:
    case = next(
        case
        for case in load_cases(ROOT / "cases")
        if case["id"] == "normal-authorized"
    )
    result = run_case(case, FakeAdapter("success"))
    serialized = result.to_dict()
    serialized["adapter_calls"][0]["payload"] = "changed"
    assert result.adapter_calls[0]["payload"] == "synthetic example"
