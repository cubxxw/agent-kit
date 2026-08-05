# Maintenance

## Weekly

The scheduled `upstream-drift` workflow compares every vendored pin with its
tracked upstream branch. Drift is a review request, not permission to update.

When drift is reported:

1. Read the upstream commits and diff.
2. Decide whether the change has current value.
3. Inspect all executable and dependency changes.
4. Update by full reviewed SHA.
5. Run tests and the strict doctor.
6. Commit the vendor diff and updated pin together.

## Adding a skill

Use this acceptance order:

1. Repeated current task.
2. Clear marginal value over host capabilities and installed skills.
3. Agent Skills-compatible structure.
4. Explicit redistribution license.
5. Stable owner and source.
6. Full commit pin.
7. Manual executable review.
8. Narrow profile placement.
9. Cross-host link verification.

Rejected and deferred candidates belong in `docs/skill-selection.md`, not in
the active catalog.

## Updating this checkout

```sh
git pull --ff-only
./bin/agent-kit doctor --strict
./bin/agent-kit install --profile developer --tool all --replace-managed
```

Never use an update command that discards a dirty checkout.

## Recovery

The installer never overwrites real directories. If a user skill conflicts:

1. compare both versions;
2. keep or back up the existing directory explicitly;
3. re-run the installer.

Uninstall removes only links that resolve to the current checkout.

## Release checklist

- Unit tests pass.
- Skill creator validation passes for first-party skills.
- `doctor --strict` passes.
- Vendor pins are full SHAs.
- Third-party licenses and notices remain present.
- GitHub Actions use full commit pins.
- Repository visibility is public.
- GitHub secret scanning and push protection are enabled.
