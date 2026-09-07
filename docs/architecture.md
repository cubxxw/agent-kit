# Architecture

## One source, many discovery views

```text
agent-kit/
├── catalog.json
└── skills/                    every accepted, discoverable skill
          │
          ├── ~/.claude/skills/<name>          Claude Code
          ├── ~/.agents/skills/<name>          Codex
          ├── ~/.qwen/skills/<name>            Qwen Code
          ├── ~/.config/opencode/skills/<name> OpenCode
          ├── ~/.pi/agent/skills/<name>        Pi
          └── ~/.openclaw/skills/<name>        OpenClaw
```

The repository is the canonical layer. Agent-specific directories are
discovery adapters, not storage. First-party and reviewed third-party skills
share the discoverable `skills/` container; `catalog.json` records ownership,
license, source path, commit pin, and tree pin.

Keeping accepted skills under `skills/` also makes the same repository
discoverable by CC Switch custom repositories and the open `skills` CLI.

## Installed catalog versus broad radar

`catalog.json` controls installed capabilities. The `top` profile is the
curated-complete view of broadly useful, fully audited skills; `all` remains a
compatibility alias.

`docs/top-skills.md` is a non-installing discovery layer. It can index many
official, specialist, and community sources without adding their descriptions
to every agent, expanding update surface, or transferring trust from a
repository to every nested skill.

## Design stack: direction, evidence, preflight

The design profile separates three jobs that should not be collapsed:

```text
deepen-design
  product truth → binary directions → architectures → rendered comparison
        ↓
ui-ux-pro-max
  searchable patterns, palettes, UX guidance, and stack constraints
        ↓
design-taste-frontend
  anti-slop and implementation preflight
```

The first layer is first-party because no third-party rule set can infer the
user’s ownable product argument by itself. Vendored skills remain byte-stable
and independently updatable.

## Boundary demo: decision before product

`boundary-demo` is a first-party orchestration skill, not a second Streamlit
manual and not a miniature Product Foundry:

```text
one uncertain decision
  → boundary | logic | taste probe
  → smallest suitable medium
  → normal + edge + failure cases
  → observed run + automated verdict + human choice
  → supported | rejected | inconclusive
  → accepted contract/cases may enter a production project
```

For Python, data, LLM, state, or human-review probes, the bundled initializer
creates a local Streamlit shell with fake adapters, pytest, AppTest,
`server.runOnSave = true`, and loopback binding. It locates Streamlit's own
version-matched `developing-with-streamlit` skill at runtime instead of copying
framework guidance into Agent Kit.

The shell and exploratory captures are disposable. Confirmed contracts and
regression cases are durable. Public Agent Kit assets remain synthetic; real
inputs, private Brain facts, traces, screenshots, and judgments stay in their
authorized project or evidence store. Product Foundry begins only after a
decision is accepted and rewrites production code under production gates.

## Portability boundary

| Layer | Strategy |
|---|---|
| Skills | One Agent Skills-compatible source |
| Durable instructions | One Markdown baseline, merged with repo instructions |
| Hook logic | Shared executable, agent-specific JSON adapter |
| MCP | Shared intent and environment-variable names, rendered per host |
| Auth, models, approvals, state | Never synchronized |

Agent hosts have different configuration schemas. Pretending those schemas
are identical would create a fragile abstraction. The shared layer stops at
portable intent; thin adapters preserve host semantics.

CC Switch is an optional local runtime layer for provider, key, model, MCP,
session, backup, and cross-application switching. Agent Kit never imports that
private state into Git.

## Conflict model

The installer recognizes four states:

- `linked`: already points to the catalog source;
- `missing`: safe to create;
- `managed-drift`: points elsewhere inside this checkout and can be repaired
  only with `--replace-managed`;
- `foreign-link` or `conflict`: stop without changing anything.

There is no general force flag.

## Public boundary

The repository-local hooks inspect pending shell and file-edit operations for
obvious credential material. The repository scanner checks tracked and
untracked publishable files for:

- common token and private-key shapes;
- secret-bearing filenames;
- absolute personal home paths;
- symlinks that escape the repository;
- unexpectedly large text artifacts.

This is defense in depth, not a substitute for GitHub secret scanning or human
review.

Upstream drift compares the pinned directory tree SHA, not the upstream
repository head. Unrelated changes in a large skill repository do not create
false alerts.

## Server bootstrap

`scripts/bootstrap.sh` performs only fast-forward updates. It stops on:

- a missing dependency;
- a non-repository destination;
- a dirty checkout;
- a validation failure;
- an installation conflict.

This makes repeated server provisioning safe and predictable.

`AGENT_KIT_PROFILE` selects catalog scope. `AGENT_KIT_TOOL` selects `core`,
`all`, or one native host. The default remains the minimal `base` profile on
the `core` Claude Code + Codex targets.
