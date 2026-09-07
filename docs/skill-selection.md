# Skill selection ledger

Evaluated on 2026-09-07. This ledger records why the active catalog stays
small.

## Adopted

### First-party `boundary-demo`

- Source: `cubxxw/agent-kit`, designed from repeated needs to test system
  boundaries without prematurely building a product.
- Decision: install in the narrow `prototyping` profile; make `full-stack` and
  `top` extend it. Keeping a separate profile lets servers and production-only
  hosts omit the workflow.
- Role: turn exactly one uncertain boundary, logic, or taste decision into the
  smallest observable probe, with normal, edge, and failure cases and a
  `supported`, `rejected`, or `inconclusive` result.
- Durable boundary: contracts, confirmed regression cases, and decision
  evidence may survive; the UI shell and exploratory traces are disposable.
  Automated verdicts never become human-confirmed or Gold cases by themselves.
- Safety: the Streamlit starter binds to loopback, keeps adapter calls behind an
  explicit submit, ships only deterministic fake adapters and synthetic cases,
  and stores rerun/UI state separately from domain state.
- Verification: the initializer is refusal-safe for nonempty targets; the
  portable engine, pytest cases, Streamlit AppTest flow, runtime skill lookup,
  project-local `runOnSave`, and loopback config are exercised in an isolated
  Streamlit 1.63.0 environment.
- Review: independent decision/architecture, case/eval, and curation reviewers
  found no unresolved P0. Their P1 requests—runtime-pinned official guidance,
  explicit case authority, one-call/zero-call assertions, failure traces,
  public/private separation, and a narrow profile—are encoded in tests and
  documentation.

#### Upstream ideas used without vendoring

- Streamlit `developing-with-streamlit`: runtime-loaded from the installed
  distribution. Reviewed at `d8dbd3c436d02a78ed6deb49adc323262e74c807`
  (Apache-2.0); Streamlit 1.63.0 contains the canonical skill. Agent Kit does
  not run `streamlit skills`, because that mutates global discovery links.
- `helderberto/agent-skills` `prototype`: reference-only at
  `deceebdd5d9706edc8d75d088a13f3a1f0c4fac5` (MIT). Kept its one-question,
  one-command, expose-state, and discard-or-absorb principles; rejected its
  blanket prohibition on tests because case/eval accumulation is the purpose.
- `obra/superpowers` `brainstorming`: not installed, reviewed at
  `b36e0829c6d0140e93cfef2ca599b1b07d4a7797` (MIT). Its broad mandatory
  triggers, hard approval/plan-writing loop, and companion process surfaces
  conflict with a timeboxed evidence probe.
- Anthropic `frontend-design` and `webapp-testing`: reference-only, reviewed at
  `41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f` (per-skill Apache-2.0). Use the
  former only for a taste-mode visual question and the latter only when DOM,
  CSS, JavaScript, screenshots, resize, or browser timing is evidence. The
  browser helper's shell and portability choices keep it out of the default
  starter.

### First-party `deepen-design`

- Source: `cubxxw/agent-kit`, created from a real rejected design iteration.
- Decision: installed before the two third-party design skills in the
  `design`, `full-stack`, and `top` profiles.
- Why: a polished Talent Signal iteration passed build, accessibility,
  responsive, performance, and self-authored 98/100 checks but remained
  visually generic. The execution changed hundreds of CSS lines while keeping
  the same product argument and page grammar.
- Role: force product invariant → two brand theorems → two architectures →
  rendered A/B directions → system → micro-detail. It uses bounded binary
  branching, pairwise evidence, a surviving challenger, and backtracking.
- Boundary: it does not replace UI/UX data or frontend preflight. It decides
  direction before those tools constrain implementation.
- Forward test: two context-isolated, read-only Agents received only the Skill
  and raw tasks. The generic B2B case rejected another polish pass and produced
  two product-derived directions. The real Talent Signal regression
  backtracked from D5 to D0-D2, chose `The Redline` over
  `The Decision Window`, retained a challenger, rendered two D3 compositions,
  and selected the split evidence ledger before code. The production result
  made clause removal retract dependent state and revise the proposed action
  while keeping fact confirmation separate from external-action approval.

### Anthropic `mcp-builder`

- Source: `anthropics/skills`, `skills/mcp-builder`
- Decision: vendored and installed in the `developer` profile.
- Why: directly supports repeated work on agent infrastructure, MCP services,
  API integration, evaluation, and deployment design.
- Trust: first-party Anthropic source, explicit per-skill Apache-2.0 license,
  pinned full commit.
- Cost: includes executable evaluation helpers, so upstream changes always
  require manual review.

### Addy Osmani `source-driven-development`

- Source: `addyosmani/agent-skills`, `skills/source-driven-development`
- Decision: vendored and installed in the `developer` profile.
- Why: official documentation changes faster than model memory; this workflow
  makes version detection, authoritative sources, citations, and explicit
  “unverified” findings repeatable.
- Trust: MIT license, pinned full commit and subtree, no executable files.
- Scope choice: adopted this standalone, low-overlap skill instead of the
  complete lifecycle pack.

### Next Level Builder `ui-ux-pro-max`

- Source: `nextlevelbuilder/ui-ux-pro-max-skill`,
  `.claude/skills/ui-ux-pro-max`
- Decision: vendored and installed in the `design` and `full-stack` profiles.
- Why: repeated value for UI structure, design-system generation,
  accessibility, responsive behavior, stack-specific guidance, and
  pre-delivery review.
- Trust: MIT license, pinned full commit and subtree. Reviewed all four runtime
  Python files; they use the standard library, make no network or subprocess
  calls, and write only during explicit design-system persistence.
- Verification: upstream data validator and representative search commands are
  part of the release gate.

### Leonxlnx `design-taste-frontend`

- Source: `Leonxlnx/taste-skill`, `skills/taste-skill`
- Decision: vendored and installed in the `design`, `full-stack`, and `top`
  profiles.
- Why: adds brief inference, anti-template frontend judgment, redesign audit,
  accessibility/motion guardrails, and a mechanical preflight. It complements
  the searchable UI/UX data in `ui-ux-pro-max`.
- Scope: landing pages, portfolios, and redesigns only; the upstream skill
  explicitly excludes dashboards, data tables, and multi-step product UI.
- Trust: MIT license, full commit and subtree pins, no executable files, and
  vendored content byte-matches upstream.
- Independent scan: NVIDIA SkillSpector 2.5.3 static mode returned `SAFE`,
  risk score 18, with 100% file coverage. Three unpinned `npx` references were
  accepted as documented supply-chain cautions; package installation still
  requires user/repository authority and reviewed versions. Two other findings
  were contextual false positives (`Do not ask the user to edit this file` and
  MIT license wording).
- Stability: upstream calls v2 experimental, so Agent Kit pins it and never
  auto-updates it.
- Real-use correction: treat it as an anti-slop preflight, not a generative
  design authority. Its negative rules removed obvious clichés but did not
  force divergent concepts, visual A/B evidence, or product-derived
  ownability. The first-party `deepen-design` workflow now supplies that
  missing layer without changing the byte-preserved upstream skill.

## Top Skills Radar

[`top-skills.md`](top-skills.md) keeps broad discovery separate from the
installed catalog. Official product sources, specialist community packs,
directories, and security tooling can all be indexed without expanding global
triggering or supply-chain surface.

## Companion integration

### `farion1231/cc-switch`

- Decision: integrate by documented boundary; do not vendor.
- Why: it is the right local UI for provider, endpoint, model, MCP, prompt,
  session, backup, and skill distribution state.
- Integration: add `cubxxw/agent-kit`, branch `main`, subdirectory `skills` as
  a custom skill repository; prefer `~/.agents/skills` plus symlink sync.
- Boundary: keys, auth, provider choices, local database, and cloud-sync state
  remain outside this public repository.

## Deferred

### Vercel `react-best-practices`

- Decision: watch, do not vendor yet.
- Value: strong React and Next.js performance guidance from Vercel Engineering.
- Reason: useful but overlaps existing frontend skills; the upstream README
  declares MIT while the repository currently lacks a standalone license file.
  Revisit when license packaging is unambiguous or the marginal need rises.

### Trail of Bits `agentic-actions-auditor`

- Decision: watch.
- Value: unusually strong security review for agentic GitHub Actions.
- Reason: excellent but narrow for the current workload, and CC-BY-SA-4.0
  creates additional redistribution obligations. Use directly for a relevant
  audit before considering catalog adoption.

### `obra/superpowers`

- Decision: do not add to the shared catalog.
- Value: mature end-to-end engineering workflows.
- Reason: broad `MUST` triggers, approval-heavy brainstorming and plan-writing,
  and companion visual/process-server surfaces overlap existing Codex and
  repository workflows. Installing it beside a one-question, timeboxed demo
  skill would increase trigger conflicts, context cost, and cleanup surface.

### Full `addyosmani/agent-skills` pack

- Decision: do not mirror the full pack.
- Value: unusually strong lifecycle coverage, verification discipline, and
  progressive disclosure.
- Reason: several workflows overlap host-provided review, testing, security,
  Git, and planning skills. Some standalone installs also omit shared
  repository-level references. Adopt narrow skills only when their marginal
  value is clear.

### OpenAI host and curated skills

- Decision: keep host-managed.
- Reason: Codex already supplies system and plugin skills with their matching
  tools. Vendoring them would lose host-managed updates and several depend on
  Codex-specific connectors that Claude Code does not share.

### Large GitHub and `skills.sh` collections

- Decision: discovery only unless a named subtree passes the full gate.
- Sources reviewed include official OpenAI, Anthropic, Vercel, Microsoft,
  Hugging Face, NVIDIA, .NET, Supabase, Firebase, Prisma, and Remotion packs;
  Matt Pocock, Superpowers, Trail of Bits, Baoyu, Marketing Skills, scientific
  and diagram collections; and the skills.sh, GitHub Awesome Copilot,
  VoltAgent, and Composio directories.
- Reason: repository reputation and install counts cannot transfer trust to
  every nested skill. Broad packs also multiply trigger overlap and update
  cost.

### Brain creation skills

- Decision: keep repository-scoped.
- Reason: Brain already exposes one canonical `.claude/skills` tree to Codex
  through `.agents/skills`. Several workflows encode private repository
  boundaries and should not become global or public by default.

## Selection principle

Popularity is a discovery signal, not an acceptance gate. License clarity,
current repeated use, compatibility, security, and non-overlap decide adoption.
