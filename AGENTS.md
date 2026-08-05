# Agent Kit repository instructions

This is a public repository. Treat every tracked byte as internet-visible.

- Never copy credentials, authentication state, transcripts, memories, private
  notes, or machine-local overrides into this repository.
- Use environment-variable names in examples; never include real values.
- Keep `catalog.json` as the source of truth for accepted skills and upstream
  pins.
- Preserve third-party license files and attribution.
- Do not overwrite an existing user skill directory. The installer must fail
  safely on conflicts.
- Run `python3 -m unittest discover -s tests -v` and
  `./bin/agent-kit doctor --strict` after changes.
- Review executable vendor changes manually before accepting an upstream
  update.
