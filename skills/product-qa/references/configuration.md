# Machine configuration

Requires macOS, Xcode Simulator tools, AXe, Python 3.9+, an unlocked user
keychain and a GUI login session for boot monitoring. Use an existing simulator
and build; the launcher does not build, erase or create devices.

Store `$HOME/.config/agent-qa/projects.json` with mode 600. Top-level fields:
`schema_version: 1`, `axe` (executable), `default_project`, `projects` (name to
profile), optional `state_dir` and `lock_file`. Keep the default machine-wide
lock at `/tmp/ios-automation.xcodebuild.lock` when sharing existing iOS tooling.

Each profile contains `kind` (`leafhour`, `tormie`, `supabase`), `server` (one
HTTPS origin), `email`, `expected_user_id`, `bundle_id`, `simulator_id`,
`credential: {service, account}`, `watch_boot`, optional `bypass_proxy`,
`launch_args`, `launch_env`, `default_screen`, `native_binding`, and `ui`. Supabase needs its
public client `anon_key`. Never place a service-role key in this file.

`native_binding` pins the reviewed `origin` and a SHA-256 digest of the installed
app tree (including debug dylibs, frameworks and configuration). Review the
source/build's backend selection before pinning it. A replacement build fails
closed until that review is repeated and its fingerprint is updated. Tormie
and Supabase additionally require the appropriate native server environment
override to match the pinned origin. Hash verification precedes keychain reads.

The `ui` contract has selectors for `email_field`, `password_field`, `submit`;
navigation lists `account_steps`, `after_login_steps`, `leave_account_steps`;
required `identity_anchor` for the authenticated account surface (a scoped form
or its unique sign-out button), optional `before_login_steps`, `email_placeholder`, `login_probe_timeout`, and
`screens` (page name to steps). Selectors use stable `id`, exact `label`, and/or
`type`. Steps have `action: tap|wait|wait_gone|gesture`, `selector`, optional `timeout`, and
`optional` for taps. Identity proof excludes editable fields.

Identity text must be exact static text in the account scope, or share a
non-application container with its authenticated sign-out control. Editable
descendants and login suggestion buttons never establish native identity.

On a remote Mac, SSH and the logged-in GUI can have different keychain security
sessions even for the same Unix user. Set `gui_bridge: true` and install with
`scripts/install.py --gui` to submit SSH `open`/`check` operations to a GUI
LaunchAgent. Its private request queue contains operation names only, never
passwords. Corrupt requests are quarantined; results are sanitized. The GUI
session's dedicated credential must be provisioned through a trusted pipe.
Do not solve an SSH keychain failure with plaintext credential files.

Pin identities after authenticated readback from the intended backend. A fresh
machine needs the dedicated test password installed in its own keychain over a
trusted channel. Never pass that password in argv or transfer an entire keychain.
Use per-origin credential references when projects have different credentials.

Install command: `python3 <skill-dir>/scripts/install.py`.
After real acceptance, enable monitoring with the same command plus `--watch`.
Disable by booting out `gui/<uid>/com.agent-kit.product-qa`; `pause` is the normal
temporary control. The monitor only handles configured `watch_boot` devices.
Foreground entry updates the last selected project. Successful boot events are
persisted, so restarting launchd does not steal the foreground during a test.

The CLI uses the native app's durable session. It never injects fake sessions
or passwords through launch arguments/environments. For intentional credential
failure tests, pause monitoring first. Network and credential failures remain
visible; the monitor retries at most three times per boot, five minutes apart.
