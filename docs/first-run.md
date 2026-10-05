# First run: prove a skill works

A successful first run ends with a useful task result. Check three things
separately: the files are installed, your agent discovers the skill, and the
skill produces the evidence you asked for.

This exercise uses `prototyping` to test an order-retry contract with a fake
adapter. It needs no real service or credentials. For general engineering,
start with `developer`; for a homepage direction, choose `design` and use the
[README task prompt](../README.md#try-one-task).

## Match the first task to your installed profile

If you selected the default `developer` profile, do not follow the
`boundary-demo` installation exercise below. It belongs to `prototyping`.
Check `source-driven-development` in the host's skill selector instead:
Claude Code's `/` menu or Codex's skill selector in a fresh local session.
Then invoke that skill with this read-only task:

```text
Use source-driven-development to check whether the json module in my installed
Python version accepts trailing commas. Detect the Python version, read the
matching official documentation, and run two standard-library-only probes:
one valid JSON object and the same object with a trailing comma. Report the
version, observed output or error, and the supporting source. Do not install
dependencies or change this project. Mark any unverified source claim.
```

Expected result: valid JSON is decoded; the trailing-comma input is rejected.
The output cites the official source and distinguishes its wording from the
local observation. Record file verification, host discovery, and the actual
probe result separately. This small check needs no account or project setup.

For `design`, verify `deepen-design` in the selector and use the README's
direction-comparison task. For `writing`, verify `threads-oral-notes`, then
ask it to turn a short idea into a draft only. You should receive a length-
checked post and topic choice; drafting needs no publishing credentials and
does not authorize posting. Do not install `prototyping` just to complete a
different profile's first check.

## Choose one installation route

If CC Switch already manages your skills, use the
[CC Switch integration guide](integrations/cc-switch.md) to select and distribute
`manage-agent-kit` and `boundary-demo`. Then skip the native installation steps
below and continue with host discovery. Check its distributed files in CC
Switch; Agent Kit `status` is for Agent Kit's native links.

Otherwise, let your current agent follow the [bootstrap protocol](bootstrap.md),
or use the native steps below. You need Git, Python 3, and Claude Code or Codex
installed and usable. Do not install another distribution manager over the same
destination.

## Prepare the canonical checkout

For a new setup:

```sh
git clone https://github.com/cubxxw/agent-kit.git "$HOME/.agent-kit"
cd "$HOME/.agent-kit"
./bin/agent-kit doctor --strict
```

If that path already exists, follow the checkout checks in
[bootstrap](bootstrap.md#establish-the-source). Preserve a dirty,
diverged, or unrelated checkout and report its state. Do not run the clone over
it or discard local changes.

Expected result: the strict doctor passes. A failure here is a repository
validation issue; resolve it before installation.

## First run in Claude Code

### Verify the files

From the Agent Kit checkout:

```sh
./bin/agent-kit plan --profile prototyping --tool claude --json
./bin/agent-kit install --profile prototyping --tool claude --dry-run
```

Read the complete plan. Expect `ready: true`, an empty `conflicts` array, and
actions for `manage-agent-kit` and `boundary-demo` pointing into
`~/.claude/skills`. The plan changes nothing. Exit status `2` means it is not
ready; preserve the conflicting path and report it.

If the plan is ready:

```sh
./bin/agent-kit install --profile prototyping --tool claude
./bin/agent-kit status --profile prototyping --tool claude
```

Expected result: both destinations are managed symlinks to this checkout.
Running the install again should preserve those links.

### Verify host discovery

Start a fresh local Claude Code session in a separate working folder. Type `/`
and check that `boundary-demo` appears in its command menu. Personal skills load
from `~/.claude/skills`, including symlinked folders. This exercise uses local
Claude Code; its machine-local skills are not automatically available to cloud
sessions. See [Claude Code's official skill documentation](https://code.claude.com/docs/en/skills).

If the skill does not appear, stop at “files installed, discovery unverified.”
Check the link target and `SKILL.md`, then the host's settings and official
troubleshooting guidance. Do not claim discovery because the agent can read a
file you explicitly pointed it to.

### Run the task

Send this at the start of a message:

```text
/boundary-demo In a new local folder, compare order submission retries with and without an idempotency key. Use a deterministic fake adapter and a CLI. The question is: after a timeout and retry, which contract prevents duplicate orders? Include a normal submission, a repeated request with the same key, and a timeout after the first order was committed. Show before/after state and a trace. Keep real services and my existing project out of scope. Stop with supported, rejected, or inconclusive and the cases that justify it.
```

The `/boundary-demo` form invokes this skill directly. Judge the result using
the task checks below.

## First run in Codex

### Verify the files

From the Agent Kit checkout:

```sh
./bin/agent-kit plan --profile prototyping --tool codex --json
./bin/agent-kit install --profile prototyping --tool codex --dry-run
```

Read the complete plan. Expect `ready: true`, an empty `conflicts` array, and
actions for `manage-agent-kit` and `boundary-demo` pointing into
`~/.agents/skills`. Exit status `2` blocks installation; report the conflicting
path without replacing it.

If the plan is ready:

```sh
./bin/agent-kit install --profile prototyping --tool codex
./bin/agent-kit status --profile prototyping --tool codex
```

Expected result: both destinations are managed symlinks to this checkout.
The files check is complete; host discovery still needs a separate check.

### Verify host discovery

Open a fresh local Codex session in a separate working folder. In Codex CLI or
the IDE extension, use `/skills` or type `$` to find `boundary-demo`. In another
surface, use its skill selector or ask which skills are exposed in the current
session. Codex reads user skills from `~/.agents/skills` and supports symlinked
folders; if a new skill does not appear, restart Codex. See
[OpenAI's official skill documentation](https://learn.chatgpt.com/docs/build-skills).

Expected result: `boundary-demo` is in the host's available skill list. If it is
absent, record “files installed, discovery unverified” and inspect the link,
manifest, and enabled-skill settings. Reading a file by path proves file access,
not host discovery.

### Run the task

Select `boundary-demo` in the host's skill selector, or in Codex CLI / the IDE
extension send:

```text
$boundary-demo In a new local folder, compare order submission retries with and without an idempotency key. Use a deterministic fake adapter and a CLI. The question is: after a timeout and retry, which contract prevents duplicate orders? Include a normal submission, a repeated request with the same key, and a timeout after the first order was committed. Show before/after state and a trace. Keep real services and my existing project out of scope. Stop with supported, rejected, or inconclusive and the cases that justify it.
```

Judge the result using the task checks below.

## Verify the task result

The result should give you:

- A local probe you can run, with launch and test commands.
- A normal, edge, and failure case with visible state and execution trace.
- A `supported`, `rejected`, or `inconclusive` decision tied to those cases.
- The assumptions and remaining uncertainty in the fake adapter's contract.

Run the returned commands and inspect the decisive case. A passing fake adapter
test establishes the modeled contract; it does not establish how a real order
provider behaves. An unsupported or inconclusive decision can still be a useful
first run if the evidence explains why.

Record the three checks separately:

```text
Host and version:
Distribution route and selected profile/skills:
Files: pass / fail / unverified — evidence
Host discovery: pass / fail / unverified — evidence
Task result: pass / fail / unverified — output and decisive case
Conflicts or next action:
```

For a native install, finish with the repository checks:

```sh
./bin/agent-kit doctor --strict
python3 -m unittest discover -s tests -v
```

When all three checks have evidence, repeat with your own boundary question or
use the [project handoff template](../examples/project-handoff/) to let another
agent continue from the verified result.
