# Skill selection ledger

Evaluated on 2026-08-05. This ledger records why the active catalog stays
small.

## Adopted

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
  `The Decision Window`, retained a challenger, and required rendered D3
  comparison before code.

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
- Reason: broad behavioral framework overlaps the existing gstack, Codex
  workflows, and repository-specific instructions. Installing both would
  increase triggering conflicts and context cost.

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
