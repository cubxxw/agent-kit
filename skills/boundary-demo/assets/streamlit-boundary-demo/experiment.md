# {{DEMO_NAME}}

> Disposable experiment. It is not production code and contains no real
> external adapter.

## Decision contract

- **Question:** {{QUESTION}}
- **Plausible answers:** Record at least two answers before changing the code.
- **Decision-changing evidence:** Name the observation that would make you
  choose a different answer.
- **Smallest failure:** Name the earliest visible signal that disproves the
  current design.
- **Timebox:** 90 minutes to the first runnable evidence.
- **Stop when:** The declared cases distinguish the plausible answers, or the
  result is explicitly inconclusive.
- **Out of scope:** Production auth, deployment, real credentials, real writes,
  and general infrastructure unless one is the boundary under test.

## Run

```sh
uv lock
uv sync --extra test
uv run python -m pytest
uv run streamlit run streamlit_app.py
```

The project-local Streamlit configuration enables rerun-on-save and binds only
to `127.0.0.1`.

## Evidence rule

Automated checks report whether the declared expectation matched the run. They
do not decide that the expectation is correct. Confirm or reject cases in
`decision.md`; only confirmed cases may move from discovery to regression.
