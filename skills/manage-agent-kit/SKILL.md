---
name: manage-agent-kit
description: Audit, initialize, upgrade, synchronize, discover, and safely curate a shared Agent Skills repository across Claude Code, Codex, Qwen Code, OpenCode, Pi, OpenClaw, and compatible hosts. Use when setting up a machine or server, finding top GitHub skills, checking skill or upstream drift, adding or updating a skill, integrating CC Switch, resolving cross-agent installation conflicts, or reviewing whether agent configuration is safe to publish.
---

# Manage Agent Kit

Treat the checked-out `agent-kit` repository as the reviewed source. Native
installs receive symlink views; an existing manager such as CC Switch can own
distribution instead. Choose one installation owner for each skill.

## Start with evidence

1. Identify the user's task, current host, and existing skill owner from
   runtime evidence and link destinations. Do not read private runtime state.
2. Inspect `catalog.json` and choose the smallest useful profile. For
   unspecified coding work use `developer`, on the current host only.
3. Read [references/operations.md](references/operations.md) for the selected
   installation path. If CC Switch owns the skills, preserve that owner.
4. For a native checkout run `doctor --strict`, then
   `plan --profile <profile> --tool <host> --json`. Explain the result the user
   will get and every conflict before applying the authorized setup.

Do not silently replace a real directory or a symlink owned by another tool.
Report the exact conflict and preserve it.

## Install or repair links

Use the smallest applicable profile:

- `base`: only this management skill.
- `developer`: source-grounded engineering and agent infrastructure.
- `design`: recursive direction branching, UI/UX evidence, and frontend
  preflight.
- `prototyping`: one uncertain decision, tested with observable cases.
- `writing`: optional first-person Threads drafting and confirmed publishing.
- `full-stack`: explicitly combine the three engineering profiles.
- `top`: every accepted skill, including optional writing; choose explicitly.
- `all`: compatibility alias for `top`.

Preview first:

```sh
./bin/agent-kit plan --profile <profile> --tool <host> --json
```

The plan is read-only and includes `ready`, `actions`, and `conflicts`.
With conflicts, return the complete explanation and the next action. Known
conflicts block the whole install before any link is created. Then install
the selected profile and verify host discovery and one small task using
the repository's first-run guide. A same-named file or symlink is not task
success. Use `--replace-managed` only for stale symlinks that already
point into this checkout. It must never replace copied files or foreign links.

## Curate a new skill

Read the checkout’s
[`docs/top-skills.md`](https://github.com/cubxxw/agent-kit/blob/main/docs/top-skills.md)
before broad discovery. It separates adopted, on-demand, and discovery-only
sources.

Accept a skill only when all gates pass:

1. It solves a repeated, current task with clear marginal value.
2. It does not duplicate a host-provided or already installed capability.
3. Its source is attributable, actively maintained, and pinned to a full
   commit SHA.
4. Its redistribution license is explicit. Do not vendor an unlicensed skill.
5. Read every executable file and inspect network, credential, and destructive
   behavior.
6. Add it to `catalog.json` and the narrowest profile.
7. Run the creator validator when first-party skill instructions change.
8. Run the repository tests, `doctor --strict`, and the public safety scan.
9. Install it into the intended hosts and verify every link resolves to the
   same target.

Record rejected or deferred candidates in `docs/skill-selection.md`; this keeps
the catalog small without losing the research.

## Discover top skills

Treat rankings and awesome lists as candidate generators:

1. Search official or product-owned repositories first.
2. Use GitHub activity and `skills.sh` installs only as discovery signals.
3. Identify the narrow skill directory that matches a repeated current need.
4. Compare its triggers against the installed catalog.
5. Return an adoption, on-demand, watch, or reject decision with evidence.
6. Update `docs/top-skills.md` without installing anything unless the full
   curation gate passes.

Never bulk-install a pack because it is popular, official, or listed in the
radar.

## Update a vendored skill

Run `scripts/check_upstreams.py`. If an update exists:

1. Review upstream commits between the pinned and proposed SHAs.
2. Run `scripts/update_vendor.py <skill> --ref <reviewed-full-sha>`.
3. Review the entire vendor diff, especially scripts and dependencies.
4. Re-run all validation and security gates.

Never auto-merge upstream skill changes.

## Public boundary

Never commit credentials, auth state, transcripts, memories, machine-local
overrides, private Brain content, or absolute personal home paths. Public
templates may name environment variables but may not contain their values.

Keep model choice, OAuth state, API tokens, and per-machine approvals local.
Only portable instructions, skills, hook logic, safe templates, source pins,
and license evidence belong here.

## Completion criteria

For the selected installation path, finish only when:

- repository validation passes;
- no public-boundary finding remains;
- native links resolve to the reviewed checkout, or manager-owned content
  matches its recorded version without overwriting local customizations;
- the current host discovers a selected skill and its first-task result is
  recorded separately from file verification;
- conflicts, deferred candidates, radar status, and upstream pins are explicit.
