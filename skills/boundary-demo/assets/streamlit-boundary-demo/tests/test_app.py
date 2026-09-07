from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


def test_run_and_reset_are_explicit() -> None:
    app = AppTest.from_file(ROOT / "streamlit_app.py", default_timeout=10).run()
    assert not app.exception
    assert not app.success

    app.button(key="run_case").click().run()
    assert not app.exception
    assert app.success[0].value == "Automated checks passed"
    assert "not a Gold case" in app.warning[0].value

    app.text_area(key="human_notes").input("This changed my decision.").run()
    assert (
        app.session_state["last_receipt"]["human_choice"]["rationale"]
        == "This changed my decision."
    )

    app.button(key="reset_case").click().run()
    assert not app.exception
    assert not app.success
    assert "human_notes" not in app.session_state


def test_failure_case_is_visible_and_passes_declared_checks() -> None:
    app = AppTest.from_file(ROOT / "streamlit_app.py", default_timeout=10).run()
    app.selectbox(key="case_id").select("failure-timeout").run()
    app.button(key="run_case").click().run()
    assert not app.exception
    assert app.success[0].value == "Automated checks passed"
    assert app.json


def test_changing_case_clears_human_notes() -> None:
    app = AppTest.from_file(ROOT / "streamlit_app.py", default_timeout=10).run()
    app.button(key="run_case").click().run()
    app.text_area(key="human_notes").input("Only for the normal case.").run()
    app.selectbox(key="case_id").select("failure-timeout").run()
    assert not app.exception
    assert "human_notes" not in app.session_state
