# Operations

## Fresh machine

```sh
git clone https://github.com/cubxxw/agent-kit.git "$HOME/.agent-kit"
cd "$HOME/.agent-kit"
./bin/agent-kit doctor --strict
./bin/agent-kit install --profile full-stack --tool core --dry-run
./bin/agent-kit install --profile full-stack --tool core
./bin/agent-kit status --profile full-stack --tool core
```

The non-interactive equivalent is `scripts/bootstrap.sh`. Set
`AGENT_KIT_PROFILE` and `AGENT_KIT_TOOL` when the machine needs a
non-default profile or host set.

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
| Claude Code | `~/.claude/skills` |
| Codex | `~/.agents/skills` |
| Qwen Code | `~/.qwen/skills` |
| OpenCode | `~/.config/opencode/skills` |
| Pi | `~/.pi/agent/skills` |
| OpenClaw | `~/.openclaw/skills` |

Use `--tool core` for Claude Code + Codex, one host name for the current
runtime, and `--tool all` only when all six discovery views are intentional.
The repository remains canonical regardless of the discovery directory.

For other hosts, browse and install through the open skills CLI:

```sh
npm exec --yes --package=skills@1.5.21 -- skills add cubxxw/agent-kit --list
npm exec --yes --package=skills@1.5.21 -- \
  skills add cubxxw/agent-kit --global --agent <agent-id> --skill '*' --yes
```

Do not install Node.js or a package manager without user authorization.

## Public configuration

Use `config/shared-instructions.md` as a portable baseline, not as a replacement
for repository-specific instructions. The files under `config/claude/` and
`config/codex/` are safe fragments; merge them into local settings rather than
overwriting existing configuration.

MCP templates contain environment-variable names only. Authentication and
actual values remain local.

## CC Switch

Use CC Switch for local provider, key, model, MCP, prompt, session, backup, and
cross-app runtime state. Add the Agent Kit custom skill repository with owner
`cubxxw`, name `agent-kit`, branch `main`, and subdirectory `skills`.

Prefer `~/.agents/skills` as its source storage plus symlink distribution when
one canonical local skill tree is desired. Never commit the CC Switch database,
provider records, auth state, or cloud-sync contents.

## Removal

```sh
./bin/agent-kit uninstall --profile full-stack --tool core --dry-run
./bin/agent-kit uninstall --profile full-stack --tool core
```

Removal deletes only symlinks that resolve to the current checkout.
