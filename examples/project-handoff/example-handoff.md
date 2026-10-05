# Example: prevent duplicate demo adapter calls

This entire task is synthetic. It illustrates a handoff shape; no repository
changes or successful test runs are asserted by this example.

## Goal and accepted constraints

The hypothetical user wants a local experiment where submitting a form calls
a deterministic fake adapter once. Saving a file or changing a widget must
not call that adapter. The task is a probe, not a production application.

## Current state and evidence

- The proposed starter is in a project-local `probe/` directory.
- No implementation or branch state has been inspected in this example.
- A proposed form submit handler is still a proposal; inspect it before use.
- No tests have run. In particular, an adapter call-count expectation is not
  evidence of an observed run.
- Preserve any unrelated working-tree changes found when resuming.

## Decisions and unknowns

- Accepted task constraint: use fake data and a fake adapter for this probe.
- AI proposal: keep the adapter call inside an explicit form submission.
- Unknown: does the actual runtime repeat the call after a file-triggered
  rerun? This is the question the experiment must answer.

## Next action and verification

Inspect the actual entrypoint, then add a failure case that demonstrates
whether one submission causes more than one adapter call. Compare a
submission, a widget-only rerun, and a file-triggered rerun. Record input,
call count, and relevant runtime version. Stop with an inconclusive result
if the available test environment cannot reproduce the rerun behavior.

## Authority and data boundary

The hypothetical authorization covers a local synthetic experiment. It does
not authorize installing global skills, using real credentials, calling an
external service, or publishing the probe. Any actual handoff must reference
the real user's instructions rather than inheriting this fictional authority.
