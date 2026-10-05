<div align="center">

<h1>agent-kit</h1>

<p><strong>Useful engineering workflows that travel between coding agents.</strong></p>

<p>Compare design directions, test an uncertain boundary, or hand a project to
another agent—with reviewed skills and a reproducible setup.</p>

[![Verify](https://github.com/cubxxw/agent-kit/actions/workflows/verify.yml/badge.svg)](https://github.com/cubxxw/agent-kit/actions/workflows/verify.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-0f766e.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-111827.svg)](https://agentskills.io/specification)

[Configure my current agent](#configure-your-current-agent) ·
[Try one task](#try-one-task) ·
[中文](README.zh-CN.md)

</div>

Agent Kit keeps reusable instructions and their supporting files in one
versioned checkout. Choose the skills for the work in front of you; keep
credentials, sessions, and private memory in the tools that already own them.

## Configure your current agent

Paste this into your shell-capable coding agent:

```text
Read https://github.com/cubxxw/agent-kit/blob/main/docs/bootstrap.md and configure Agent Kit for my current agent and task. Choose the smallest useful profile, preserve my existing setup, show the complete plan before applying it, and verify one usable skill. If another manager owns my skills, use its integration path and explain any action I need to take.
```

The agent detects its host, chooses a small profile, reads the complete change
plan, and reports what it verified. Start with `developer` for general
engineering, or choose a task-specific profile below.

**Already using [CC Switch](https://github.com/farion1231/cc-switch)?** Add Agent
Kit as a skill repository and let CC Switch distribute your selected skills.
Use the [CC Switch guide](docs/integrations/cc-switch.md); you do not need to
stack the native installer on the same skill directories.

## Try one task

Pick the result you need. The [first-run guide](docs/first-run.md) walks through
a complete local exercise in Claude Code or Codex.

| Your task | What you get | Start with |
|---|---|---|
| Find a design direction | Two visibly different directions, a comparison, and the product decisions behind them | `design` → `deepen-design` |
| Test one uncertain boundary | A runnable probe, normal/edge/failure cases, and a decision tied to the evidence | `prototyping` → `boundary-demo` |
| Move a project between agents | A handoff file with current state, decisions, checks, and the next action | [Project handoff template](examples/project-handoff/) |

For an existing homepage, try:

```text
Use deepen-design to compare two materially different homepage directions for this project. Start from its audience and product truth, preserve the current implementation, and show before/A/B visual evidence. Stop before full implementation so I can choose a direction.
```

For a contained experiment, try:

```text
Use boundary-demo to compare retrying an order submission with and without an idempotency key. Use a deterministic fake adapter in a new local folder, with normal, repeated-request, and timeout-after-commit cases. Show state and trace, then stop at supported, rejected, or inconclusive. Keep it a disposable experiment.
```

For a project handoff, start with the template in
[`examples/project-handoff/`](examples/project-handoff/). Give the next agent
the project and that file. This is an explicit handoff; Agent Kit does not
automatically synchronize agent memories or session history.

## Install a small profile yourself

Use this route if you want Agent Kit to manage native skill links. You need
Git, Python 3, and an installed coding agent. This example targets Codex only;
replace `codex` with `claude` for Claude Code.

```sh
git clone https://github.com/cubxxw/agent-kit.git "$HOME/.agent-kit"
cd "$HOME/.agent-kit"

./bin/agent-kit doctor --strict
./bin/agent-kit plan --profile developer --tool codex --json
./bin/agent-kit install --profile developer --tool codex --dry-run
./bin/agent-kit install --profile developer --tool codex
./bin/agent-kit status --profile developer --tool codex
```

Read the plan before installing. It returns `ready`, `actions`, and
`conflicts`, including each source and destination. It changes no directories
and exits with status `2` when conflicts block the plan. Preserve existing
directories and foreign links; do not force past a conflict.

Installation has three checks: files link to the intended checkout, the host
discovers the skills, and a real task produces the expected result. `status`
covers the first check. Follow [first run](docs/first-run.md) for the other two.

## Choose skills by task

| Profile | Included skills | Use it for |
|---|---|---|
| `developer` | `manage-agent-kit`, `mcp-builder`, `source-driven-development` | General engineering and agent integrations |
| `design` | `manage-agent-kit`, `deepen-design`, `ui-ux-pro-max`, `design-taste-frontend` | Design direction, UI evidence, and frontend preflight |
| `prototyping` | `manage-agent-kit`, `boundary-demo` | One uncertain contract, state transition, or interaction |
| `writing` | `manage-agent-kit`, `threads-oral-notes` | Optional Threads oral-note workflow |
| `base` | `manage-agent-kit` only | Managing the setup; it adds no task skills |

Existing broader installs remain available: `full-stack` combines `developer`,
`design`, and `prototyping`; `top` adds the optional writing workflow; `all`
is a compatibility alias for `top`. Choose these deliberately, after a small
profile has proved useful. [`catalog.json`](catalog.json) is the source of truth
for profiles, accepted skills, upstream pins, and licenses.

## Compatible hosts and other installers

The native installer provides discovery paths for these six hosts. This is
compatibility coverage, not a claim that every host has been tested end to end.
Verify discovery and a task in the host you actually use.

| Host | `--tool` | Default skill directory |
|---|---|---|
| Claude Code | `claude` | `~/.claude/skills` |
| Codex | `codex` | `~/.agents/skills` |
| Qwen Code | `qwen` | `~/.qwen/skills` |
| OpenCode | `opencode` | `~/.config/opencode/skills` |
| Pi | `pi` | `~/.pi/agent/skills` |
| OpenClaw | `openclaw` | `~/.openclaw/skills` |

`--tool core` selects Claude Code and Codex. Use `--tool all` only when you
intend to create views for all six. Native links point to one canonical
checkout; updating that checkout changes what its managed hosts read.

For another host, the open [`skills` CLI](https://github.com/vercel-labs/skills)
can discover Agent Kit's `skills/` tree. Browse first and select named skills:

```sh
npm exec --yes --package=skills@1.5.21 -- skills add cubxxw/agent-kit --list
```

Use one distribution manager for each destination. The
[Top Skills Radar](docs/top-skills.md) is for discovery; it installs nothing.

## Keep runtime state local

This public repository contains skills, safe instructions, templates, reviewed
hook code, and source pins. API keys, tokens, authentication, providers, models,
sessions, private memory, and machine overrides stay local. CC Switch can
continue to manage that local runtime state.

[`config/`](config/) contains examples to merge consciously. Neither an example
nor bootstrap authorizes replacing an existing host config. The native
installer refuses existing directories and foreign links. Upgrades require a
clean checkout and fast-forward only.

## Maintain and verify

```sh
./bin/agent-kit doctor --strict
python3 -m unittest discover -s tests -v
./bin/agent-kit status --profile developer --tool codex
./scripts/check_upstreams.py
./bin/agent-kit uninstall --profile developer --tool codex --dry-run
```

For unattended provisioning, use [`scripts/bootstrap.sh`](scripts/bootstrap.sh)
with `AGENT_KIT_PROFILE` and `AGENT_KIT_TOOL`. Review the
[bootstrap protocol](docs/bootstrap.md) and [maintenance runbook](docs/maintenance.md).

[Architecture](docs/architecture.md) · [Engineering practices](docs/best-practices.md) ·
[Selection ledger](docs/skill-selection.md) · [Quality review](docs/quality.md) ·
[Contributing](CONTRIBUTING.md) · [Security policy](SECURITY.md) ·
[Third-party notices](THIRD_PARTY_NOTICES.md)

## License

First-party code and documentation are MIT licensed. Vendored skills retain
their upstream licenses and attribution; see
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
