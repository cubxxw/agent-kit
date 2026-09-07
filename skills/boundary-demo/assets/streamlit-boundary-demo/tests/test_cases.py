from pathlib import Path

from boundary_demo.cases import load_cases


ROOT = Path(__file__).resolve().parents[1]


def test_template_contains_normal_edge_and_failure_cases() -> None:
    cases = load_cases(ROOT / "cases")
    assert {case["case_type"] for case in cases} == {"normal", "edge", "failure"}
    assert all(case["source"] == "synthetic" for case in cases)
    assert all(case["split"] == "discovery" for case in cases)
    assert all(case["review"]["status"] == "unreviewed" for case in cases)


def test_local_streamlit_config_enables_rerun_and_loopback() -> None:
    config = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    assert "runOnSave = true" in config
    assert 'address = "127.0.0.1"' in config
