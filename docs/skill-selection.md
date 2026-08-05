# Skill selection ledger

Evaluated on 2026-08-05. This ledger records why the active catalog stays
small.

## Adopted

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

### Brain creation skills

- Decision: keep repository-scoped.
- Reason: Brain already exposes one canonical `.claude/skills` tree to Codex
  through `.agents/skills`. Several workflows encode private repository
  boundaries and should not become global or public by default.

## Selection principle

Popularity is a discovery signal, not an acceptance gate. License clarity,
current repeated use, compatibility, security, and non-overlap decide adoption.
