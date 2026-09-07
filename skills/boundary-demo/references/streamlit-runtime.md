# Streamlit runtime contract

Use Streamlit as a control surface after the decision and medium are chosen,
not as the reason a demo exists.

## Use an isolated project interpreter

Do not rely on a machine's system Python or globally installed Streamlit. For a
new scaffold:

```sh
cd <DEMO_DIR>
uv lock
uv sync --extra test
```

Run every Streamlit and test command through that project:

```sh
uv run python -m pytest
uv run streamlit run streamlit_app.py
```

The generated `uv.lock` records the resolved version for that experiment.

## Load official version-matched guidance

Streamlit 1.57+ includes development guidance in its installed package, and
1.60+ includes the discovery meta-skill. Locate the bundled skill through the
demo interpreter:

```sh
uv run python -c 'from pathlib import Path; import streamlit; root=Path(streamlit.__path__[0]); print(root / ".agents/skills/developing-with-streamlit/SKILL.md")'
```

Read that `SKILL.md` and only the references relevant to the current probe. If
the path does not exist, use the official Streamlit documentation for the
installed version or upgrade the isolated demo environment. Do not silently
run `streamlit skills` because it creates host discovery links that may collide
with the user's canonical skill manager.

## Local rerun and network boundary

For a new demo, keep this in the demo root:

```toml
[server]
runOnSave = true
address = "127.0.0.1"
```

Start Streamlit from that root so the local config is effective. For a probe
embedded in an existing project, merge only these keys without overwriting
theme, port, CORS, XSRF, or other settings. When safe merging is uncertain,
leave the file unchanged and pass `--server.runOnSave true
--server.address 127.0.0.1` to the launch command.

`runOnSave` causes a script rerun, not frontend hot-module replacement. Keep
domain state explicit and keep adapter calls behind `st.form_submit_button` or
another explicit submit action. `st.session_state` may hold UI selections and
the previous result; it must not become the hidden domain model.

## Test selection

- Pure functions, contracts, and state transitions: pytest.
- Streamlit elements, widget interaction, Run/Reset, and Session State:
  `st.testing.v1.AppTest` under pytest.
- DOM, custom JavaScript, CSS, chart/dataframe selection, resize, or visual
  screenshots: browser testing, only when those behaviors matter.

Use native Streamlit elements by default. Do not spend the experiment budget
on custom CSS or components unless the visual mechanism is the decision.

## Sources

- [Canonical Streamlit skill](https://github.com/streamlit/streamlit/tree/develop/lib/streamlit/.agents/skills/developing-with-streamlit)
- [Streamlit configuration](https://docs.streamlit.io/develop/api-reference/configuration/config.toml)
- [AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest)
