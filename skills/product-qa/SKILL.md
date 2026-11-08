---
name: product-qa
description: Open registered native iOS test apps in Simulator with their designated test account, reuse sessions, recover real password login and verify account identity. Use for simulator startup or account-backed UI testing on a configured workstation or remote Mac. Does not publish builds or provision unrelated accounts.
---

# Product QA

Use `agent-qa doctor`, then `agent-qa open <project>` for a configured native
app. The private machine registry lives at `$HOME/.config/agent-qa/projects.json`.
Do not print it: it contains private server and identity configuration. The
password is referenced by OS keychain service/account and is read at runtime.

`agent-qa open` checks the password against the pinned server, confirms its
canonical account UUID/email, revokes only that temporary verification session,
and launches the registered installed build. It uses the real login UI when
needed and verifies the native account page. Keep that app session for further
testing. `--screen <configured-name>` navigates after identity proof. `check`
proves credentials only, not native UI acceptance. `status` reports sanitized
receipts; do not substitute an old receipt for a fresh result.

Run data operations only after both server and native identity checks pass.
The user's current authorization controls whether test data can be changed.
Never use an unresolved or private account as a fallback. Do not copy production
data into examples, logs or test fixtures. A fixture-only app is not a live-login
substitute. Report a rejected credential, missing build or unavailable backend
truthfully rather than resetting accounts or replacing builds implicitly.

Registered boot monitoring is opt-in through `scripts/install.py --watch`.
It runs once per boot and reopens the last selected registered project, or
the configured default. It shares the machine-wide simulator lock, skips active
builds, leaves other devices alone and bounds failure retries. Use
`agent-qa pause` for intentional sign-out tests or competing manual sessions;
`agent-qa resume` restores monitoring. The foreground `open` command remains
available while automatic monitoring is paused.

For machine setup, use [the configuration contract](references/configuration.md).
Install only this skill with Agent Kit's `qa` profile. Machine-local profiles,
runtime receipts and AXe binaries remain outside this public repository.

Acceptance means fresh real UI login, warm reuse, relaunch and an observed boot
monitor run on each requested host. List missing stages separately. This skill
does not authorize a TestFlight upload, release or additional model work.
