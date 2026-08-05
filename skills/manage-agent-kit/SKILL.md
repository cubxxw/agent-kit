---
name: manage-agent-kit
description: Audit, initialize, upgrade, synchronize, and safely curate a shared Agent Skills repository across Claude Code, Codex, Qwen Code, OpenCode, Pi, OpenClaw, and compatible hosts. Use when setting up a machine or server, checking skill or upstream drift, adding or updating a skill, integrating CC Switch, resolving cross-agent installation conflicts, or reviewing whether agent configuration is safe to publish.
---

# Manage Agent Kit

Treat the checked-out `agent-kit` repository as the canonical source. Agent
hosts receive views of the same skill directories through symlinks.

## Start with evidence

1. Run `scripts/agent-kit doctor --strict`.
2. Run `scripts/agent-kit status --profile full-stack --tool core`.
3. Inspect `catalog.json` before proposing changes.
4. Read [references/operations.md](references/operations.md) for the relevant
   operation.

Do not silently replace a real directory or a symlink owned by another tool.
Report the exact conflict and preserve it.

## Install or repair links

Use the smallest applicable profile:

- `base`: only this management skill.
- `developer`: source-grounded engineering and agent infrastructure.
- `design`: reviewed UI/UX design intelligence.
- `full-stack`: recommended personal workstation.
- `all`: every accepted catalog entry.

Preview first:

```sh
scripts/agent-kit install --profile full-stack --tool core --dry-run
```

Then install. Use `--replace-managed` only for stale symlinks that already
point into this checkout. It must never replace copied files or foreign links.

## Curate a new skill

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

Finish only when:

- repository validation passes;
- no public-boundary finding remains;
- every selected skill is linked into the intended agent directories;
- all managed links resolve to one canonical source;
- conflicts, deferred candidates, and upstream pins are explicit.
