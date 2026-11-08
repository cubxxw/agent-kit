# Product QA Entry Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans inline. The user has approved execution and the two-host scope.

**Goal:** Open three registered native test apps already authenticated on either Mac.
**Architecture:** A private profile directory configures one generic Python launcher, AXe UI driver and launchd boot monitor. Existing app authentication remains authoritative.
**Tech Stack:** Python standard library, AXe, simctl, macOS Keychain, launchd.
**Spec:** `docs/superpowers/specs/2026-11-08-product-qa-design.md`

## Global Constraints

- Three approved apps only; no Capir, releases or privileged account changes in the reusable launcher.
- Secrets never enter Git, command arguments, launch environments or evidence.
- Retain native sessions and unrelated devices/worktrees; pin server and account identity.
- Reuse the machine-wide simulator lock and refuse competing builds.

## Review Focus

- Wrong backend redirects or a foreign cached identity must never receive credentials/data operations.
- A failed readback must still revoke the launcher's new verification session.
- A watchdog restart must not repeat a boot event or steal the foreground mid-test.
- Credential submission must not expose secrets through arguments or failure output.
- Monitor and foreground entry must serialize with existing build/test tooling.

### Task 1: Shared entry and auth contracts

Files: `tests/test_product_qa.py`, `skills/product-qa/scripts/agent_qa.py`.
- [ ] Add failing behavioral tests for pinned identity/origin, session cleanup, secret stdin, watcher persistence/pause, and shared-lock ownership.
- [ ] Run red tests; implement the narrow profile/auth/UI/monitor interfaces; run full repository tests.

### Task 2: Machine installation and app profiles

Files: `skills/product-qa/scripts/install.py`, `skills/product-qa/SKILL.md`, safe profile example, `catalog.json`.
- [ ] Test installer conflict refusal and launchd opt-in; implement installation without overwriting foreign skills.
- [ ] Configure workstation and managed Mac with private profile/credential references; copy AXe runtime only to the managed machine; resolve the intended test credentials.
- [ ] Verify UI login and reuse against each existing native build; repair only demonstrated profile/navigation defects.

### Task 3: Automatic boot and durable discovery

- [ ] Enable boot monitoring only for approved registered devices; exercise real shutdown/boot and inspect sanitized receipts.
- [ ] Add local project entry guidance and skill discovery on both machines.
- [ ] Run creator validation, full suite, doctor and public scan; request a fresh whole-branch review, fix important findings, commit and publish this tooling branch.

## Execution ledger

- Baseline: 41 repository tests pass; catalog doctor has no findings. Main checkout was clean; work is on its own feature branch.
- Managed host: SSH verified against its existing known host, existing primary simulator reused. Native UI tooling and dedicated password need installation.
- Runtime evidence: SSH and GUI keychain sessions differ on the managed host; GUI status is unlocked while SSH status is locked. Add a private launchd request bridge rather than weakening credential storage.
- Review fixes: pin the entire native app tree and reviewed origin before credential access; scope exact static identity to the authenticated account surface; clean up malformed successful auth responses; recheck monitor state inside the shared lock.
- Workstation primary simulator keeps its UUID/data and is renamed to the standard iPhone model label required by the existing shared session helper. No device was created or erased.
