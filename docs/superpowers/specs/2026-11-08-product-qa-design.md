# Reusable simulator test-account entry

The user approved a shared launcher and reusable skill for three native apps,
on the workstation and managed Mac. Capir and all other apps are excluded.
Account data operations are authorized only in the designated testing accounts.

Implement a standard-library Python launcher driven by private per-machine
profiles. Profiles bind simulator UUID, installed bundle, backend origin,
expected account UUID/email, credential keychain reference and UI navigation.
Read passwords only at runtime; enter them through the real UI using stdin,
never arguments, launch environments, receipts or screenshots. Server login
and session readback must agree with the pinned identity. Revoke only the
launcher's temporary verification session. Keep the native session for reuse.

`doctor` checks configuration and tools. `check` proves credentials.
`open` selects/boots the registered simulator, launches the installed app,
opens its account surface, reuses or completes real UI login, and verifies the
visible identity before returning to the requested page. A foreign identity
fails closed. No account creation/reset, application rebuilding, fixture auth,
simulator deletion or private data copying is implicit in these commands.

Opt-in per-machine launchd monitoring runs once per boot of registered QA
simulators. It opens the last selected project (an explicit configured default
on first use), never changes unregistered devices, skips active builds and
uses the same machine-wide simulator lock. Provide pause/resume and disable
operations so deliberate sign-out tests and other tasks remain possible.
The monitor must record bounded sanitized failures and retry after a bounded
cooldown rather than repeatedly submitting bad credentials.

Use AXe selectors, not fixed coordinates. Reuse installed valid builds and
the existing simulator session policy. Generic code and examples can be public;
machine paths, actual origins/identities and credentials cannot enter Git.
Install the skill for existing Codex/Claude discovery without replacing foreign
skills. Install matching launchers/configurations on both hosts.

Acceptance: unit tests cover origin/identity refusal, temporary-session cleanup,
password transport, duplicate watcher events, pause/busy behavior and redaction.
On both hosts, prove cold real UI login, warm reuse, relaunch and automatic
registered-simulator boot behavior for all three profiles, reporting actual
limitations separately. Roamorrow's rejected password must be resolved against
its intended backend before claiming completion. No release/upload is in scope.
