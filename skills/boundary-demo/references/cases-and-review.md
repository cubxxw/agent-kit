# Cases, evidence, and review

## Case lifecycle

Keep these dimensions independent:

- `case_type`: `normal`, `edge`, or `failure` describes the stimulus.
- `source`: `synthetic` or `real` describes provenance.
- `split`: `discovery`, `regression`, or `holdout` describes lifecycle.
- `review.status`: `unreviewed`, `confirmed`, or `rejected` records human
  authority.

A case begins as `discovery`. A successful automated check produces an
automated verdict, not a human choice. Promote it to `regression` only after the
user confirms its expectation. Do not promote a case to Gold automatically.

V0 checks should remain intentionally small:

- explicit result status;
- recursive output/state subset;
- required trace events;
- forbidden trace events;
- expected adapter call count.

Do not create an executable expression DSL for expected results.

## Evidence receipt

Return and preserve:

```text
Decision: supported | rejected | inconclusive
Observed facts: what the run actually emitted
Automated verdicts: which declared checks passed or failed
Human choice: confirmed decision and rationale, or “unreviewed”
AI hypotheses: possible mechanisms, clearly labeled
Decisive cases: IDs and provenance
Remaining uncertainty: what the probe could not establish
```

Public templates contain synthetic cases only. Real inputs, private traces,
screenshots, credentials, and personal judgments stay in the authorized
project or private evidence store.

## Independent review panel

When the user requests multi-agent review or the boundary is high-risk, ask
independent read-only reviewers to examine different lenses without giving
them a preferred answer:

1. **Decision reviewer:** Is there one falsifiable question, discriminating
   evidence, and a real stop rule?
2. **Boundary reviewer:** Are state ownership, side effects, failures,
   authorization, and public/private boundaries explicit?
3. **Eval reviewer:** Do normal, edge, and failure cases exercise the claimed
   boundary, including forbidden effects?
4. **Taste reviewer:** Add only when experience is the experimental variable;
   compare variants pairwise against the same task and cases.

If the host cannot delegate, run the same lenses sequentially. Review evidence,
not reviewer votes.

## Severity gate

**P0 — invalid or unsafe experiment**

- the probe answers multiple decisions or cannot falsify its preferred answer;
- a rerun can repeat a real side effect;
- a real adapter, credential, public bind, or deployment is enabled by default;
- the failure case does not prove the forbidden side effect stayed absent;
- domain state is hidden in UI session state;
- private evidence can enter a public artifact;
- AI or an automated pass promotes a case or taste judgment without the user.

**P1 — materially weaker learning or reproducibility**

- missing provenance, reset behavior, deterministic fake, or visible trace;
- only the happy path is easy to run;
- version/runtime selection is ambiguous;
- a visual comparison changes multiple uncontrolled variables;
- cleanup loses the decision or confirmed cases;
- documentation and executable behavior disagree.

Do not declare the demo ready with unresolved P0. Resolve P1 or record an
explicitly accepted exception with its impact and owner.
