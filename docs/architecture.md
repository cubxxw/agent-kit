# Architecture

## One source, two discovery views

```text
agent-kit/
├── catalog.json
├── skills/                    first-party skills
└── vendor/                    reviewed, pinned third-party skills
          │
          ├── ~/.agents/skills/<name>   (Codex symlink)
          └── ~/.claude/skills/<name>   (Claude Code symlink)
```

The repository is the canonical layer. Agent-specific directories are
discovery adapters, not storage.

## Portability boundary

| Layer | Strategy |
|---|---|
| Skills | One Agent Skills-compatible source |
| Durable instructions | One Markdown baseline, merged with repo instructions |
| Hook logic | Shared executable, agent-specific JSON adapter |
| MCP | Shared intent and environment-variable names, rendered per host |
| Auth, models, approvals, state | Never synchronized |

Codex and Claude Code have different configuration schemas. Pretending those
schemas are identical would create a fragile abstraction. The shared layer
stops at portable intent; thin adapters preserve host semantics.

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
