# agent-kit

One public, versioned source for personal Agent Skills and portable agent
configuration. Codex and Claude Code use the same skill files instead of two
copies that drift.

## What it solves

- One canonical `SKILL.md` tree for Codex and Claude Code.
- Safe, idempotent installation on a laptop or a new server.
- Refusal to overwrite existing skills or foreign symlinks.
- Pinned, licensed third-party skills with an explicit review trail.
- Public-repository guards for secrets and machine-local paths.
- Weekly upstream-drift checks and a reviewed vendor-update path.

## Install

```sh
git clone https://github.com/cubxxw/agent-kit.git "$HOME/.agent-kit"
cd "$HOME/.agent-kit"
./bin/agent-kit doctor --strict
./bin/agent-kit install --profile developer --tool all
./bin/agent-kit status --profile developer --tool all
```

For an unattended base setup after cloning:

```sh
AGENT_KIT_PROFILE=developer ./scripts/bootstrap.sh
```

The installer creates these views:

| Host | Discovery directory | Source |
|---|---|---|
| Codex | `~/.agents/skills/<name>` | symlink to this checkout |
| Claude Code | `~/.claude/skills/<name>` | symlink to this checkout |

Both hosts follow skill-directory symlinks. Changes in the checkout therefore
reach both without copying files.

## Profiles

| Profile | Contents | Intended use |
|---|---|---|
| `base` | `manage-agent-kit` | Every machine |
| `developer` | `base` + `mcp-builder` | Coding and agent infrastructure |
| `all` | Every accepted catalog entry | Explicit full install |

`catalog.json` is the source of truth. A small catalog is intentional: a skill
must add current, repeated value and pass license and security review.

## Common operations

```sh
# Preview without writing
./bin/agent-kit install --profile developer --tool all --dry-run

# Validate the public boundary and skill catalog
./bin/agent-kit doctor --strict

# Check whether a vendored source moved
./scripts/check_upstreams.py

# Update only after reviewing an exact upstream commit
./scripts/update_vendor.py mcp-builder --ref <full-reviewed-sha>

# Remove only links owned by this checkout
./bin/agent-kit uninstall --profile developer --tool all
```

## What is shared and what stays local

Shared:

- Agent Skills;
- portable instructions;
- hook logic and safe configuration examples;
- MCP server names, URLs, and required environment-variable names;
- source pins, licenses, and maintenance policy.

Local only:

- API keys, OAuth state, cookies, tokens, and auth files;
- model and billing choices;
- approval decisions and workspace trust;
- transcripts, memories, caches, and private knowledge;
- machine-specific overrides.

The files under `config/` are mergeable examples, not replacements for an
existing `settings.json` or `config.toml`.

## Design basis

The layout follows the [Agent Skills specification](https://agentskills.io/specification).
Codex loads user skills from `~/.agents/skills`; Claude Code loads personal
skills from `~/.claude/skills`. Both support symlinked skill directories.

See [architecture](docs/architecture.md), [maintenance](docs/maintenance.md),
[skill selection](docs/skill-selection.md), and the
[quality gate](docs/quality.md).

## License

First-party code and documentation are MIT licensed. Vendored skills retain
their own licenses; see [third-party notices](THIRD_PARTY_NOTICES.md).
