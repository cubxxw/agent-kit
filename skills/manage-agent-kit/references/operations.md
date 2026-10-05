# Operations

## Select a useful result

Identify the current host and task. Use `developer` for unspecified coding
work, `design` for direction and frontend work, `prototyping` for one uncertain
decision, or `writing` for Threads drafting. `base` contains only management.
Use `full-stack` or all hosts only when that combined setup is intended.

Inspect skill paths and link destinations to identify an existing manager.
CC Switch-owned skills stay on its distribution/update route. Do not install
native links over them or move the user's storage directory by default.

## Native installation

Use a supplied checkout, or clone Agent Kit to `$HOME/.agent-kit`. An existing
checkout must have the expected origin, be clean, and be on the intended
branch before a fast-forward update. Preserve dirty or surprising state.

From the checkout:

```sh
./bin/agent-kit doctor --strict
./bin/agent-kit plan --profile <profile> --tool <host> --json
```

The plan changes nothing. `ready: false` and exit 2 report all known conflicts.
Each action also records `resolved_destination`; installation rejects a parent
directory alias that changes that physical target after the preview.
Invalid requests may return an error on stderr instead of JSON. Explain the
selected skills, current owner, and next action for each conflict.

If the requested setup authorizes the ready plan:

```sh
./bin/agent-kit install --profile <profile> --tool <host>
./bin/agent-kit status --profile <profile> --tool <host>
./bin/agent-kit doctor --strict
python3 -m unittest discover -s tests -v
```

Use `--replace-managed` on plan and install only for stale links inside this
checkout. For copied or foreign skills, compare versions, preserve the
existing one, and request a migration choice only when needed. There is no
general force flag. Execution-time errors can leave partial progress; report
the listed completed targets and re-plan before retrying.

The server helper `scripts/bootstrap.sh` checks origin and branch, requires a
clean checkout, prints a plan, and then installs. Set `AGENT_KIT_PROFILE` and
`AGENT_KIT_TOOL`; its default `base/core` is deliberately minimal.

## Directory map

| Host | Target | Default discovery directory |
|---|---|---|
| Claude Code | `claude` | `~/.claude/skills` |
| Codex | `codex` | `~/.agents/skills` |
| Qwen Code | `qwen` | `~/.qwen/skills` |
| OpenCode | `opencode` | `~/.config/opencode/skills` |
| Pi | `pi` | `~/.pi/agent/skills` |
| OpenClaw | `openclaw` | `~/.openclaw/skills` |

`core` means Claude Code + Codex; `all` means all six. Each directory can be
overridden with `AGENT_KIT_<HOST>_SKILLS_DIR` for an explicitly chosen path or
an isolated test. A missing default path does not prove that a host lacks a
manager-installed skill in another supported location.

Other hosts can discover named skills through the open skills CLI. Browse
before choosing, and use one distribution manager per destination:

```sh
npm exec --yes --package=skills@1.5.21 -- skills add cubxxw/agent-kit --list
```

## CC Switch installation

Add the skill repository with owner `cubxxw`, name `agent-kit`, branch `main`,
and subdirectory `skills`. Select the names in the chosen catalog profile;
do not assume the manager applies native profile inheritance automatically.

Record the source revision if the manager exposes it. When a source checkout
is available, compare the installed skill with `skills/<name>` read-only.
Report content differences or an unknown revision; do not overwrite custom
content. A native `foreign-link` means another owner, not failed installation.
Use CC Switch for removal and updates when it owns those files.

## Verify discovery and one task

In a fresh local session, use Claude Code's skill command menu or Codex's
skill selector to verify the selected skill is actually exposed. Reading a
file by explicit path does not prove discovery. If it is absent, report the
file check separately and follow the host's troubleshooting path.

Then run a small task and record its output. The repository's
[`docs/first-run.md`](https://github.com/cubxxw/agent-kit/blob/main/docs/first-run.md)
gives a synthetic order-retry exercise. Report content/link verification,
host discovery, and task result separately. Do not describe a fake adapter
as proof of a real service's behavior.

## Configuration and removal

`config/` contains optional fragments, never replacements for user settings.
Merge only the portable intent the user requests; credentials and actual
environment values remain local. Do not copy the CC Switch database,
providers, auth state, sessions, or cloud-sync contents into Git.

For native links, preview removal before applying it:

```sh
./bin/agent-kit uninstall --profile <profile> --tool <host> --dry-run
./bin/agent-kit uninstall --profile <profile> --tool <host>
```

Removal affects links resolving to the selected checkout and catalog source.
Unrecognized or stale links are preserved; inspect and report them rather
than promising that every historical installation was cleaned up.
