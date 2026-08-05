# Boris-style engineering review

Reviewed on 2026-08-05 against the public working principles in
[Boris Cherny’s thread](https://x.com/bcherny/status/2007179832300581177) and
the evolving [How Boris Uses Claude Code](https://howborisusesclaudecode.com/):
verification first, minimal resident context, corrections encoded as
infrastructure, reversible setup changes, and automation that returns evidence.

This is a documented self-review lens, not an endorsement by Boris Cherny.

## Score

Release target: at least 95/100 with observable evidence.

| Dimension | Weight | Evidence | Score |
|---|---:|---|---:|
| Positioning and 60-second onboarding | 15 | One outcome-led hero, one universal handoff sentence, one recommended path | 15 |
| Cross-agent interoperability | 20 | Six native host adapters; open skills CLI and CC Switch discovery from one `skills/` tree | 19 |
| Safety, privacy, and recovery | 20 | Dry-run, conflict refusal, fast-forward-only bootstrap, owned-link uninstall, public guard | 20 |
| Source and supply-chain integrity | 15 | Full commit/tree pins, licenses in every distributed skill, executable review ledger | 14 |
| Verification and evidence loops | 15 | Unit tests, strict doctor, data validation, host status, CI, final report contract | 15 |
| Context economy and maintainability | 10 | Profiles, progressive disclosure, small catalog, weekly subtree drift, dated research | 9 |
| README trust and star-worthiness | 5 | Clear hierarchy, badges, honest support boundaries, useful companion integrations | 5 |
| **Total** | **100** |  | **97** |

## Findings fixed in this revision

1. **The product looked Claude/Codex-only.** Added native Claude Code, Codex,
   Qwen Code, OpenCode, Pi, and OpenClaw targets plus a long-tail distribution
   path.
2. **The bootstrap required the user to translate documentation into a
   prompt.** Added one vendor-neutral sentence and an agent-executable
   completion contract.
3. **Reviewed vendor skills were hidden from ecosystem discovery.** Moved every
   accepted skill under `skills/` while preserving source, tree, and license
   evidence in the catalog.
4. **Private runtime switching and public configuration were easy to blur.**
   Documented Agent Kit + CC Switch as complementary layers.
5. **The catalog lacked a broadly useful source-verification workflow and the
   requested design intelligence.** Added two narrow, reviewed, pinned skills
   rather than mirroring entire upstream packs.
6. **Quality was asserted but not tied to README conversion or the universal
   handoff.** Replaced the old rubric with this evidence-based review.

## Why three points remain open

- Native Windows bootstrap and symlink behavior are not exercised in CI.
- Long-tail host distribution depends on the external open skills CLI and is
  not end-to-end tested for every supported agent.
- Skill-use telemetry and automatic pruning are not implemented; periodic
  cleanup still requires a deliberate review.

The score is valid only while unit tests, the strict doctor, UI/UX data
validation, ecosystem discovery, and CI all pass.
