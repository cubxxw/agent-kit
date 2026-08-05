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
