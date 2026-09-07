from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import streamlit as st

from boundary_demo.adapters import FakeAdapter
from boundary_demo.cases import load_cases
from boundary_demo.evaluation import evaluate
from boundary_demo.runner import run_case


ROOT = Path(__file__).resolve().parent
DEMO_NAME = {{DEMO_NAME_PY}}
QUESTION = {{QUESTION_PY}}
CASES = load_cases(ROOT / "cases")
CASE_BY_ID = {case["id"]: case for case in CASES}

st.set_page_config(page_title=DEMO_NAME, page_icon=":material/science:")
st.title(DEMO_NAME, icon=":material/science:")
st.caption("Disposable boundary experiment · fake adapters only · local loopback")
st.subheader("Decision question")
st.write(QUESTION)

selected_id = st.selectbox(
    "Case",
    options=list(CASE_BY_ID),
    format_func=lambda case_id: f"{CASE_BY_ID[case_id]['case_type']} · {case_id}",
    key="case_id",
)
selected = CASE_BY_ID[selected_id]

if st.session_state.get("loaded_case_id") != selected_id:
    st.session_state.loaded_case_id = selected_id
    st.session_state.request_id = selected["given"]["input"]["request_id"]
    st.session_state.payload = selected["given"]["input"]["payload"]
    st.session_state.authorized = selected["given"]["input"]["authorized"]
    st.session_state.scenario = selected["given"]["adapter"]["scenario"]
    st.session_state.pop("last_receipt", None)

st.write(selected["purpose"])
with st.form("case_form"):
    st.text_input("Request ID", key="request_id")
    st.text_area("Payload", key="payload")
    st.checkbox("Explicitly authorized", key="authorized")
    st.selectbox(
        "Fake adapter scenario",
        options=["success", "timeout", "reject"],
        key="scenario",
    )
    submitted = st.form_submit_button(
        "Run case", icon=":material/play_arrow:", key="run_case"
    )

if st.button("Reset result", icon=":material/refresh:", key="reset_case"):
    st.session_state.pop("last_receipt", None)

if submitted:
    working_case = deepcopy(selected)
    working_case["given"]["input"] = {
        "request_id": st.session_state.request_id,
        "payload": st.session_state.payload,
        "authorized": st.session_state.authorized,
    }
    working_case["given"]["adapter"] = {"scenario": st.session_state.scenario}
    adapter = FakeAdapter(st.session_state.scenario)
    result = run_case(working_case, adapter)
    check = evaluate(working_case, result)
    st.session_state.last_receipt = {
        "case": {
            "id": working_case["id"],
            "case_type": working_case["case_type"],
            "source": working_case["source"],
            "split": working_case["split"],
            "review": working_case["review"],
        },
        "observed_fact": result.to_dict(),
        "automated_verdict": check.to_dict(),
        "human_choice": {"status": "unreviewed", "rationale": None},
        "ai_hypothesis": None,
    }

receipt = st.session_state.get("last_receipt")
if receipt:
    verdict = receipt["automated_verdict"]["verdict"]
    if verdict == "pass":
        st.success("Automated checks passed")
    else:
        st.error("Automated checks failed")
    st.warning("Human review is still unreviewed; this is not a Gold case.")

    observed = receipt["observed_fact"]
    st.subheader("Input")
    st.json(observed["input"])
    st.subheader("State before and after")
    st.json({"before": observed["initial_state"], "after": observed["final_state"]})
    st.subheader("Trace")
    st.json(observed["trace"])
    st.subheader("Output and checks")
    st.json(
        {
            "output": observed["output"],
            "adapter_calls": observed["adapter_calls"],
            "automated_verdict": receipt["automated_verdict"],
        }
    )
    st.text_area(
        "Human decision notes",
        placeholder="What changed or confirmed your decision? Not saved automatically.",
        key="human_notes",
    )
    st.download_button(
        "Download evidence receipt",
        data=json.dumps(receipt, ensure_ascii=False, indent=2),
        file_name=f"{observed['case_id']}-receipt.json",
        mime="application/json",
        icon=":material/download:",
    )
