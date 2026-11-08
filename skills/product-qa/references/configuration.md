# Machine configuration

Requires macOS, Xcode Simulator tools, AXe, Python 3.9+, an unlocked user
keychain and a GUI login session for boot monitoring. Daily `open` reuses its
registered device/build and never creates or erases devices. Initial setup can
register a dedicated QA simulator so other projects cannot replace its apps.

Each private profile can provide `build: {project, scheme, configuration,
entitlements, generate_spec, prepare_commands, package_cache}`; the optional entitlement path preserves the product's existing
capabilities while adding the required linked keychain identity.
`agent-qa build <project> --reviewed-origin <origin>` obtains a registered storage
artifact and runs Xcode inside the existing simulator session helper, using two
jobs and standard Simulator entitlement handling without an Apple publishing
identity. Source copies and logs remain private. The build must produce the
registered bundle identifier.
An optional verified `package_cache` selects system Git and the project’s committed
resolved versions, skips updates, and reuses its binary artifact cache. Verify
any task-scoped official mirror environment against those exact pins first;
never change global Git routing or substitute package versions.
Canonical resource commands (explicit argv lists) and XcodeGen run inside the
owned build session; the existing generated project is backed up first. Build
cancellation asks the reservation owner to clean up rather than killing that
owner while descendants may still run. Custom lock paths are forwarded to the
session helper.

Reuse a reviewed build with `agent-qa prepare <project> --app <source.app>
--reviewed-origin <origin>`. Only matching Simulator bundles with linked keychain
identity metadata are accepted. Preparation verifies the existing signature and
installs a private copy without rewriting its entitlements. Repeat after source
build changes. This refreshes the fingerprint without silently trusting an
unexpected installed app. Simulator entitlement metadata belongs in Mach-O
`__TEXT,__entitlements`/`__TEXT,__ents_der`, distinct from the host signature;
see [Swift Build's entitlement checks](https://github.com/swiftlang/swift-build/blob/main/Sources/SwiftBuildTestSupport/CoreQualificationTester.swift).

Store `$HOME/.config/agent-qa/projects.json` with mode 600. Top-level fields:
`schema_version: 1`, `axe` (executable), `default_project`, `projects` (name to
profile), optional `state_dir` and `lock_file`. Keep the default machine-wide
lock at `/tmp/ios-automation.xcodebuild.lock` when sharing existing iOS tooling.
`allow_other_booted_devices: true` permits targeting the registered device while
leaving other booted devices untouched; it does not bypass the shared lock or
active builds. Read-only Xcode version/SDK probes do not count as active builds.
An explicit `allow_other_simulator_tests: true` allows only already-built tests
targeting different, explicit simulator UUIDs; it never bypasses the lock,
same-device tests, compilation or archiving. `build_simulator_id` can select
the ordinary shared build device separately from the dedicated interactive QA
device. Run `agent-qa close` before such a heavy build; only registered QA devices
are shut down and their data is retained.

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
or a unique authenticated account control), optional `before_login_steps`, `email_placeholder`, `login_probe_timeout`, and
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

The launchd UI jobs use the app resource class (`ProcessType: Interactive`):
they drive visible native UI, while Background throttling can starve Simulator
and keychain requests on a loaded shared Mac. They do not run native builds.

Native fingerprints use version 2, with explicit entry types, path/content
boundaries and directory-link targets. After upgrading from the earlier
format, revalidate and repin each reviewed installed build before opening it.
GUI requests bind to the normalized private configuration. Admission and
completion records prevent a worker restart from replaying an old open;
inspect interrupted native state and issue a new foreground request instead.
An interrupted boot attempt also requires a foreground open; recorded failures
retain bounded retries. `pause` waits for an admitted automatic UI operation
before confirming that automatic login is paused.

For a fresh Agent Kit machine, bootstrap its `base` management profile first.
On existing workstations, preserve the management skill's current owner and
install only `qa` for this capability.
