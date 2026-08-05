# Operations

## Fresh machine

```sh
git clone https://github.com/cubxxw/agent-kit.git "$HOME/.agent-kit"
cd "$HOME/.agent-kit"
./bin/agent-kit doctor --strict
./bin/agent-kit install --profile developer --tool all
./bin/agent-kit status --profile developer --tool all
```

The non-interactive equivalent is `scripts/bootstrap.sh`. Set
`AGENT_KIT_PROFILE=developer` when the machine needs the developer profile.

## Existing machine

Run a dry-run before installing. The installer intentionally stops on copied
skills or foreign symlinks. Resolve each conflict manually:

1. Compare the existing skill with the catalog source.
2. Keep the existing skill if it is intentionally different.
3. Move it to a dated backup outside the discovery directory if adopting the
   catalog version.
4. Re-run the installer without a force flag.

## Directory map

| Agent | User skill directory |
|---|---|
| Codex | `~/.agents/skills` |
| Claude Code | `~/.claude/skills` |

Both hosts support symlinked skill directories. Do not use `~/.codex/skills`
as the canonical location for new shared skills.

## Public configuration

Use `config/shared-instructions.md` as a portable baseline, not as a replacement
for repository-specific instructions. The files under `config/claude/` and
`config/codex/` are safe fragments; merge them into local settings rather than
overwriting existing configuration.

MCP templates contain environment-variable names only. Authentication and
actual values remain local.

## Removal

```sh
./bin/agent-kit uninstall --profile developer --tool all --dry-run
./bin/agent-kit uninstall --profile developer --tool all
```

Removal deletes only symlinks that resolve to the current checkout.
