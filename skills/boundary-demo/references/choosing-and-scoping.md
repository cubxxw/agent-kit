# Choosing and scoping a boundary demo

The best demo maximizes decision-changing evidence while minimizing build and
cleanup cost.

## Decision contract

Use this compact contract:

```text
Question: Should/does X behave as A or B in situation Y?
Alternatives: A / B[/ C]
Decision-changing evidence: ...
Smallest failure: ...
Timebox: ...
Stop when: ...
Out of scope: ...
```

Reject questions such as “Can we build the whole workflow?” They contain too
many decisions. Split at the first uncertain ownership, state transition,
external boundary, or user choice.

## Pick the medium

| Uncertainty | Cheapest faithful probe | What must remain real |
|---|---|---|
| State, policy, or data shape | CLI or Streamlit | State transitions and invalid paths |
| Python/data/LLM workflow | Streamlit | Domain logic, representative cases, trace |
| Third-party integration | Streamlit plus fake adapter | The adapter contract and failure semantics |
| Information hierarchy or interaction | Two or three variants | Same task, content, and cases across variants |
| DOM/CSS/browser timing | Existing Web surface plus browser testing | Actual rendered browser behavior |
| Native/mobile/platform capability | Target platform spike | The platform boundary under question |

Fidelity belongs at the uncertain boundary. Everything outside it should be
fake, static, or omitted.

## Stop rules

- If there is no runnable probe within 60–90 minutes, narrow the decision.
- If auth, deployment, a general data layer, or production error handling is
  growing without being the experimental variable, stop.
- If every outcome can be interpreted as success, rewrite the decision
  contract before adding code.
- If a real side effect is required, state the exact system, data, authority,
  reversal plan, and stopping condition before enabling it.

The prototype may be rich enough to expose the boundary, but it must not gain
features merely to feel complete.
