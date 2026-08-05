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
