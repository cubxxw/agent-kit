# Universal bootstrap protocol

This is the stable handoff contract for a coding agent initializing or
upgrading a machine from Agent Kit.

## The one-sentence handoff

```text
Open https://github.com/cubxxw/agent-kit/blob/main/docs/bootstrap.md and follow it end to end to safely initialize or fast-forward upgrade this machine for the current agent; preserve existing configuration and secrets, preview every change, run the verification gates, and report conflicts instead of forcing them.
```

## Completion contract

Finish only when:

- the current host and selected profile are explicit;
- no credential, auth state, private memory, or machine-local value was copied
  into the repository;
- the canonical checkout is clean and current by fast-forward only;
- the strict doctor passes;
- the install was previewed before it was applied;
- existing directories and foreign symlinks were preserved;
- installed links and host discovery were verified;
- the final report lists changes, unchanged state, conflicts, checks, and any
  remaining manual action.

## Protocol

### 1. Identify the host and boundary

Identify the current agent from the runtime, executable, or existing config.
Map it to one native target:

| Host | Target |
|---|---|
| Claude Code | `claude` |
| Codex | `codex` |
| Qwen Code | `qwen` |
| OpenCode | `opencode` |
| Pi | `pi` |
| OpenClaw | `openclaw` |

Do not inspect or copy secret-bearing files to “discover” configuration.
Existing skill directories, settings files, and instruction files are
read-only evidence until the preview has been reviewed.

Default to:

- `base` on a minimal server;
- `developer` for backend, infrastructure, and MCP work;
- `design` for a design-focused environment;
- `full-stack` for a personal development workstation.

### 2. Establish the canonical checkout

Use `${AGENT_KIT_HOME:-$HOME/.agent-kit}`.

- If the path does not exist, clone
  `https://github.com/cubxxw/agent-kit.git`.
- If it is this repository and clean, run `git pull --ff-only`.
- If it is dirty, not a Git repository, on a divergent branch, or has a
  surprising remote, stop and report the exact state.
- Never reset, clean, force-pull, or discard local changes.

### 3. Audit before mutation

From the checkout:

```sh
./bin/agent-kit doctor --strict
./bin/agent-kit status --profile <profile> --tool <target>
./bin/agent-kit install --profile <profile> --tool <target> --dry-run
```

Read every conflict. A real directory or foreign symlink may belong to the
user or another manager. Do not replace it.

### 4. Apply the smallest safe change

If the preview is clean:

```sh
./bin/agent-kit install --profile <profile> --tool <target>
```

Use `--replace-managed` only when the reported conflict is a stale symlink
whose target is already inside this Agent Kit checkout. It is not a general
force flag.

For an agent that is not a native target, use the open skills CLI after
browsing the catalog:

```sh
npm exec --yes --package=skills@1.5.21 -- skills add cubxxw/agent-kit --list
npm exec --yes --package=skills@1.5.21 -- \
  skills add cubxxw/agent-kit --global --agent <agent-id> --skill '*' --yes
```

Do not install Node.js, a package manager, or another system dependency
without the user’s authorization.

### 5. Keep host-specific runtime state local

Never overwrite a host config with a file from `config/`. Merge only the
portable intent the user approves.

- Agent Kit owns public skills, safe instructions, hooks, source pins, and
  templates.
- CC Switch may own local providers, endpoints, keys, models, MCP state,
  sessions, backups, and cross-app runtime switching.
- Environment-variable names may be public; values stay local.

### 6. Close the verification loop

Run:

```sh
./bin/agent-kit doctor --strict
./bin/agent-kit status --profile <profile> --tool <target>
python3 -m unittest discover -s tests -v
```

When `ui-ux-pro-max` is selected, also run:

```sh
python3 skills/ui-ux-pro-max/scripts/validate_data.py
```

Confirm that every managed destination is a symlink to this checkout and that
the current host can discover the selected skills. A passing command without
host discovery is incomplete verification.

### 7. Report evidence

Return this compact record:

```text
Host:
Profile:
Checkout:
Installed/updated:
Preserved unchanged:
Conflicts:
Verification:
Manual next action:
```

Do not claim completion with “looks good.” Include the exact checks and their
outcomes.

## Upgrade path

An upgrade is the same protocol with a current checkout:

1. require a clean worktree;
2. `git pull --ff-only`;
3. run the strict doctor;
4. preview the selected profile and host;
5. repair only Agent Kit-owned stale links;
6. rerun repository, data, and host-discovery checks.

Vendored upstream changes are not pulled transitively. Agent Kit updates them
only after license, executable, diff, and full-SHA review.
