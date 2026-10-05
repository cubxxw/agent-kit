# Configure Agent Kit for the current agent

This is the setup contract for an agent helping a user adopt Agent Kit.
Choose the user's task and existing installation path before changing anything.

## One-sentence handoff

```text
Read https://github.com/cubxxw/agent-kit/blob/main/docs/bootstrap.md and configure Agent Kit for my current agent and task. Choose the smallest useful profile, preserve my existing setup, show the complete plan before applying it, and verify one usable skill. If another manager owns my skills, use its integration path and explain any action I need to take.
```

## Choose what the user will get

Identify the current host from runtime evidence. Inspect skill directories and
link destinations; do not read credentials or session contents for detection.
Use one host unless the user wants multiple hosts.

| User task | Profile | Result |
|---|---|---|
| General development, source verification, MCP work | `developer` | Source-grounded development and MCP-building guidance |
| Improve a generic landing page or portfolio | `design` | Direction comparison, UI/UX references, implementation preflight |
| Test one uncertain integration or state decision | `prototyping` | A small probe with normal, edge, and failure cases |
| Draft a first-person Threads post | `writing` | A draft to review; publishing still needs the exact draft confirmed |
| Deliberately combine development, design, and experiments | `full-stack` | The three engineering profiles |
| Maintain installation only | `base` | The management skill, without a task workflow |

For unspecified coding work, use `developer`. Do not default to `top` or all
hosts. State the proposed result and profile in one short sentence. Ask only
when the missing task would materially change the choice; preserve choices
already made in the conversation. Project handoff is also available as a
[standalone template](../examples/project-handoff/README.md) without installing
a new skill.

## Choose who owns installation

If CC Switch already distributes the relevant skills, follow
[its integration path](integrations/cc-switch.md). Keep that manager in charge
of updates and removal. Do not run the native installer over its links.

For a user-managed checkout or server, follow the native path below. An
unrecognized copied directory or foreign link is a conflict to report, not
permission to move or replace it. The open skills CLI is another optional
distribution path; it is not an extra installation step for native users.

## Native path

### Establish the source

Use a user-specified checkout, or `${AGENT_KIT_HOME:-$HOME/.agent-kit}`.
Require Git and Python 3; report a missing dependency without installing it
unless the user's setup request already authorizes that installation.

- If absent, clone `https://github.com/cubxxw/agent-kit.git` on `main`.
- If present, verify repository identity, origin, and branch. HTTPS and
  GitHub SSH forms of that same repository are equivalent.
- Require a clean checkout on `main` before fetching and fast-forwarding it.
  Stop on a dirty, detached, divergent, or unexpected checkout. Preserve it.
- Never reset, clean, force-pull, or overwrite local work.

Record the checkout commit. Source versions in `catalog.json` identify the
reviewed third-party content; fetching Agent Kit does not adopt newer upstream
skills transitively.

### Read the whole installation plan

From the checkout, run:

```sh
./bin/agent-kit doctor --strict
./bin/agent-kit plan --profile <profile> --tool <host> --json
```

Native host names are `claude`, `codex`, `qwen`, `opencode`, `pi`, and
`openclaw`. `core` selects Claude Code and Codex; `all` selects all six.

The read-only plan contains `ready`, `actions`, and `conflicts`. Each action
names the skill, tool, source, destination, state, proposed action, and reason.
`resolved_destination` records the physical target at preview time; installation
rechecks it before writing and rejects an observed target change.
Exit code 0 means ready; 2 means a conflict or invalid request. Planning creates
no destination directories or links. Valid profiles with conflicts still
return the complete JSON; invalid input can instead return an error on stderr.

Explain which skills will be added, which are already present, and every
conflict. With `ready: false`, stop before installation and give a specific
next action. If an existing manager owns the links, use its route. If a copied
skill intentionally differs, keep it; migration requires the user's choice.

Use `--replace-managed` only for a stale link already owned by this checkout.
Add the flag to both the plan and install commands. It cannot replace another
manager's link or a real file/directory.

### Apply and check

When the plan is ready and the requested setup authorizes it:

```sh
./bin/agent-kit install --profile <profile> --tool <host>
./bin/agent-kit status --profile <profile> --tool <host>
./bin/agent-kit doctor --strict
python3 -m unittest discover -s tests -v
```

For the design profile, also run the included UI/UX data validator. Verify the
current host discovers one installed skill using [first-run.md](first-run.md),
then complete its small test task. Keep the three results separate: files
installed, host discovery, task outcome. A link check alone is not task success.

Setup manages skills. Files under `config/` are optional examples to discuss
separately; they do not authorize replacing host configuration, installing MCP
servers, choosing a provider, or changing models and credentials.

## Return a useful setup receipt

```text
You can now:
Host and installation owner:
Profile and source commit:
Added / already present:
Conflicts and next action:
File verification:
Host discovery:
First task result:
How to update or remove:
```

Name an unresolved discovery check honestly. Finish only when the selected
installation path is verified, or return the precise blocker and next action.
Do not equate repository tests with a successful task in every supported host.

## Updates and servers

An update repeats source verification, a clean fast-forward, doctor, the full
plan, and host/task checks. The native server helper is `scripts/bootstrap.sh`;
set `AGENT_KIT_PROFILE` and `AGENT_KIT_TOOL` explicitly. It verifies origin and
branch, prints the plan, and stops on conflicts before installing. Its default
is the minimal `base` profile on `core`, not a complete workstation.

`AGENT_KIT_HOME`, `AGENT_KIT_REPOSITORY`, and `AGENT_KIT_BRANCH` can select an
explicitly intended checkout and source. Keep existing CC Switch installations
on their own update path. Review third-party upstream diffs manually before
changing the catalog pins.
