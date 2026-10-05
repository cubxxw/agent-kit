# Use Agent Kit through CC Switch

Agent Kit supplies the reviewed workflow files. CC Switch owns their local
installation, updates, backups, and distribution when you choose this route.
You do not need to add a second native installer over the same skills.

## Add the repository

In CC Switch's Skills repository management, add:

```text
Owner: cubxxw
Repository: agent-kit
Branch: main
Subdirectory: skills
```

Select the skills for your task from [the profile table](../../README.md#choose-skills-by-task).
Profiles belong to Agent Kit's native installer; a repository browser may show
individual skills instead. Match those names instead of assuming CC Switch
applies `catalog.json` profiles. Keep your existing CC Switch storage location.

## Verify the content and the host

1. Record the Agent Kit source commit shown by the manager or available from
   its repository checkout. A same-named skill is not necessarily that version.
2. Locate the installed skill directory using the manager's UI or the host's
   skill discovery. Inspect its files and link destinations, without reading
   credentials, the CC Switch database, or private sessions.
3. When a source checkout is available, compare the installed directory with
   the corresponding `skills/<name>` directory. A read-only comparison is:

   ```sh
   diff -qr <checkout>/skills/<name> <installed-skill-directory>
   ```

   A difference is evidence to investigate, not permission to overwrite a
   local customization. Do not describe an unknown version as verified.
4. Follow [first-run.md](../first-run.md) to verify discovery in the current
   host and complete one small task.

Return three separate results: content/version match, host discovery, and
task outcome. If CC Switch exposes no exact source revision, report that
limit; do not invent a pin from the skill name.

## Understand native status

The native installer calls a link outside its checkout `foreign-link`, even
when CC Switch correctly installed that skill. This is an ownership boundary,
not a verdict that the skill is unusable or unsafe. It can also report
`missing` in its default directory while a host discovers a manager-installed
skill somewhere else.

Use the manager's update and removal controls for manager-owned skills. A move
to native ownership is a separate migration: compare content, agree on which
version to keep, back up through the existing owner, then preview the new
installation. Never use `--replace-managed` to bypass another manager.

Provider credentials, models, MCP runtime state, sessions, and cloud-sync
contents remain local to CC Switch. Agent Kit distributes public capability
files; it does not synchronize that private runtime state.
