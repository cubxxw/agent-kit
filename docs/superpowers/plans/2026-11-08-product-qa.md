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
- [x] Add failing behavioral tests for pinned identity/origin, session cleanup, secret stdin, watcher persistence/pause, and shared-lock ownership.
- [x] Run red tests; implement the narrow profile/auth/UI/monitor interfaces; run full repository tests.

### Task 2: Machine installation and app profiles

Files: `skills/product-qa/scripts/install.py`, `skills/product-qa/SKILL.md`, safe profile example, `catalog.json`.
- [x] Test installer conflict refusal and launchd opt-in; implement installation without overwriting foreign skills.
- [x] Configure workstation and managed Mac with private profile/credential references; install a privately pinned AXe runtime on each machine; resolve the intended test credentials.
- [x] Verify UI login and reuse against each existing native build; repair only demonstrated profile/navigation defects.

### Task 3: Automatic boot and durable discovery

- [x] Enable boot monitoring only for approved registered devices; exercise real shutdown/boot and inspect sanitized receipts.
- [x] Add local project entry guidance and skill discovery on both machines.
- [x] Run creator validation, full suite, doctor and public scan; request a fresh whole-branch review, fix important findings, commit and publish this tooling branch.

## Execution ledger

- Baseline: 41 repository tests pass; catalog doctor has no findings. Main checkout was clean; work is on its own feature branch.
- Managed host: SSH verified against its existing known host. GUI-native credential access, a private AXe runtime and a dedicated QA simulator are installed.
- Runtime evidence: SSH and GUI keychain sessions differ on the managed host; GUI status is unlocked while SSH status is locked. Add a private launchd request bridge rather than weakening credential storage.
- Review fixes: pin the entire native app tree and reviewed origin before credential access; scope exact static identity to the authenticated account surface; clean up malformed successful auth responses; recheck monitor state inside the shared lock.
- Workstation primary simulator keeps its UUID/data and is renamed to the standard iPhone model label required by the existing shared session helper. Its data is retained; dedicated QA devices were subsequently registered on both hosts. No device was erased.
- Live integration confirmed missing linked Simulator entitlements. Native authentication succeeded but session persistence failed. Use Xcode's standard Simulator packaging/linking, validate the resulting Mach-O metadata, preserve its signature, install and repin. Do not insert simulated iOS claims in the host signature. No Apple publishing identity is used.
- Shared-device integration observed an unrelated test replacing the installed app; the fingerprint check blocked further credential entry. Register dedicated QA simulators, retain the ordinary build-session device, and provide explicit QA close before heavy builds. Existing simulator data is preserved.

- Final review: 98 repository tests pass; catalog doctor, skill validation and scoped public-content scan pass. Independent review found no outstanding important issues after account-scope and multiple-destination fixes.
- Native acceptance: Leafhour and Tormie pass real password login, authenticated account readback, warm reuse and conversation-page routing on both hosts. Roamorrow also passes password login, authenticated account readback and conversation routing on both hosts. Boot monitoring was observed on both hosts, including Roamorrow warm reuse after a real device restart.
- SDK integration: a managed-host network failure affected package downloads. Exact committed official dependency mirrors passed full Git object checks; binary artifacts are fetched over their original release URLs and checked against the pinned package manifest before cache reuse.

## Accepted runtime result

| Check | Workstation | Managed Mac |
| --- | --- | --- |
| Leafhour real password login, reuse, account proof, conversation entry | Passed | Passed |
| Tormie real password login, reuse, account proof, conversation entry | Passed | Passed |
| Roamorrow real password login, reuse, account proof, conversation entry | Passed | Passed |
| Registered-device boot monitor, real shutdown/boot | Passed | Passed |
| Private registry, runtime keychain reference, command, skill discovery and durable routing | Installed | Installed |

- No application product-source changes or publishing actions were needed.
- Existing native test data and unrelated work were preserved. Obsolete task-owned app copies and build intermediates were reclaimed; current prepared apps, exact SDK cache, build logs and original generated-project backups remain available.
- The managed host required recovery of an unresponsive Simulator frontend and the registered QA device. UI launch jobs now use the app resource class so background throttling does not starve visible automation. This does not guarantee launch speed under arbitrary host load.
- Native fingerprints were revalidated against the previous reviewed bytes before migration to framed version 2. Queued requests bind to the normalized profile; durable admission/completion records prevent interrupted work from relaunching an active app.
- Account/UI acceptance is separate from third-party provider or model functionality. No external provider authorization, model generation, real-device build, TestFlight or store action was performed.
