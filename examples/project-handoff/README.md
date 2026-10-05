# Resume a task in another coding agent

Use a small project-local handoff when switching tools, computers, or sessions.
The next agent should find the current decision and its evidence without
replaying a conversation or guessing whether a proposed change was applied.

This is a standalone template. No skill installation, cloud service, or
memory-sync system is required. It is a starting format to test in your work,
not a claim that every project needs another document.

## Write the handoff

Copy [handoff-template.md](handoff-template.md) into the project location you
choose, or update an existing handoff. Preserve user edits and the original
task scope. Include only the context needed for the next action; link large
designs and source material instead of copying them.

Ask the current agent:

```text
Write a project-local handoff using the Agent Kit handoff template. Record the
current goal, constraints, observed state with evidence, unresolved decisions,
and the next action with its verification. Preserve uncommitted work. Keep
proposals separate from applied changes and tests that actually ran. Do not
include credentials, unrelated private context, or a transcript dump.
```

The [worked example](example-handoff.md) is synthetic. Its unrun checks remain
unrun; fictional evidence must not become a completion claim.

## Resume the task

Give the next agent the project path and handoff:

```text
Read this project's handoff, then inspect the referenced files and current
working state. Tell me the current goal, what is verified, and the first
unresolved decision. Continue the recorded next action within my existing
authorization. If the files disagree with the handoff, report the difference
and use current evidence before changing anything.
```

Judge the handoff by the next agent's behavior: can it identify the next
action, preserve an intentional unfinished change, and distinguish a user
decision from an AI proposal? Record an actual failure if it cannot, then
change the template narrowly. File completeness alone is not evidence that
the handoff reduced explanation or rework.
