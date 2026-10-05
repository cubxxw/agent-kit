# Contribute a workflow someone can use

Start with the task and expected result. A useful contribution solves a
repeated problem, has a clear boundary, and gives another person a way to
check the outcome. A popular skill collection alone is not an adoption case.

## Propose the smallest addition

Use an issue or pull request to explain the input, output, dependencies, and
one realistic success or failure example. Distinguish a runnable template
from a method with observed project results. Synthetic examples must be
labeled; do not invent experiences, metrics, or user confirmation.

For a template that works without skill routing, use `examples/`. For a
repeatable agent workflow, use a named directory in `skills/`. Keep framework
manuals and already-provided host capabilities out of the default catalog.

## Keep the catalog coherent

- Register an accepted skill in `catalog.json` and the narrowest profile.
- Keep optional domains out of `full-stack`; `top`/`all` intentionally cover
  all accepted skills.
- Explain the adoption decision in `docs/skill-selection.md`.
- For third-party code, record the full commit and subtree SHA, preserve its
  license, and review every executable file and dependency change.
- Preserve a vendored skill's bytes; host-specific integration belongs in
  first-party guidance or adapters.

## Verify the actual behavior

Run the repository gates:

```sh
python3 -m unittest discover -s tests -v
./bin/agent-kit doctor --strict
python3 skills/ui-ux-pro-max/scripts/validate_data.py
```

Use the skill-authoring validator for changed first-party skills. Test an
installation change in temporary host directories; never require a reviewer
to overwrite their real environment. An agent-facing workflow needs a small
forward task with observable results, beyond a Markdown or schema check.

Report the tested platform, source revision, checks run, and remaining
limitations. Six filesystem adapters do not prove successful use in six
running agents. Keep credentials, personal notes, real private traces, and
machine-local installation metadata out of the contribution.

Docs-only contributions need link and semantic review. Avoid tests that only
assert that documentation contains the wording you just wrote.
