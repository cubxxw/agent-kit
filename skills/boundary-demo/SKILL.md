---
name: boundary-demo
description: Build a disposable, observable demo that answers one uncertain system-boundary, state, integration, or experience decision and preserves reusable case/eval evidence. Use when asked for a demo, prototype, sandbox, spike, boundary explorer, integration simulator, or UI comparison before production implementation. Do not use to ship production features.
---

# Boundary Demo

Build the smallest probe that can change one decision. The deliverable is
evidence, not a miniature product.

## Start with one decision contract

Before implementation, write down:

- one question with at least two plausible answers;
- the evidence that would change the decision;
- the smallest observable failure;
- a timebox and stop rule;
- what is explicitly out of scope.

If these cannot be stated, ask one concise question. Do not expand into a full
product specification. Read
[references/choosing-and-scoping.md](references/choosing-and-scoping.md) when
the right probe or medium is unclear.

## Choose exactly one mode

- **Boundary:** contracts, ownership, external services, failures, retries, or
  side effects. Default integrations to deterministic fake or read-only
  adapters.
- **Logic:** state machines, data shapes, policies, or transitions. Keep the
  runner independent of the UI.
- **Taste:** interaction or information hierarchy is the uncertainty. Compare
  two or three materially different variants against the same cases; read
  [references/taste-comparison.md](references/taste-comparison.md).

Do not run all modes by default. Choose the medium after the mode:

- Prefer Streamlit for Python, data, LLM, state, trace, and human-review probes.
- Prefer a CLI when the question is pure state or business logic and a browser
  adds no evidence.
- Use an existing Web surface when DOM, CSS, responsive behavior, browser
  events, or page context is itself under test.

## Build an observable probe

Make input, relevant state before and after, trace, output, and failure visible.
Seed at least one normal, one edge, and one failure case. Keep four evidence
classes separate:

1. observed fact;
2. automated verdict;
3. human choice;
4. AI hypothesis.

An automated pass never promotes a discovery case to regression or Gold.
Only the user can confirm the expected behavior or taste choice.

For a new Streamlit probe, initialize the bundled example:

```sh
python <SKILL_DIR>/scripts/init_demo.py <TARGET_DIR> \
  --question "<ONE DECISION QUESTION>"
```

Then follow [references/streamlit-runtime.md](references/streamlit-runtime.md).
The scaffold uses a project-local configuration with automatic reruns and
loopback binding. Never modify a global Streamlit configuration.

## Test the boundary, not the disposable shell

- Use ordinary pytest for contracts, state transitions, fake adapters, and
  evaluation.
- Use Streamlit `AppTest` for widgets, Session State, Run/Reset, and rendered
  outcomes.
- Use Playwright or another browser harness only when actual DOM, CSS,
  JavaScript, screenshots, resize, or browser timing is part of the decision.

Read [references/cases-and-review.md](references/cases-and-review.md) for the
case lifecycle and P0/P1 review gate.

## Authority and side effects

- A starter must not contain a working real adapter.
- Real network access, credentials, login state, deployment, or external
  mutation requires explicit scope for that run.
- File-save reruns and widget reruns must not repeat side effects. Put adapter
  calls only behind an explicit Run/Submit event, never at module import or page
  render time.
- Redact secrets and personal data from inputs, traces, screenshots, and
  exported receipts.
- Do not copy private project or Brain cases into a public repository.

## Finish at the decision

Return `supported`, `rejected`, or `inconclusive`, with the decisive cases and
remaining uncertainty. Preserve the decision contract, confirmed regression
cases, and accepted interface/contract. The UI shell, captures, and exploratory
traces are disposable.

Never delete the probe or promote code into production without explicit user
authorization. When the decision is accepted, hand the contract and cases to
the production project or Product Foundry; rewrite production code under that
project's quality gates.
