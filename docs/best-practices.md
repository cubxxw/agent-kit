# Engineering guide

Reviewed on 2026-08-05. Product behavior and agent discovery paths can change;
source links are included so compatibility claims can be rechecked.

## What the research changed

The first version of Agent Kit solved one problem well: Codex and Claude Code
could share one canonical skill tree. The broader research showed that a
durable personal agent system needs three separate layers:

| Layer | Responsibility | Chosen mechanism |
|---|---|---|
| Public capability | Portable skills, instructions, hooks, source and license evidence | Agent Kit |
| Private runtime | Providers, endpoints, keys, models, MCP state, sessions, backups | CC Switch or host-native config |
| Distribution | Put the same skill tree where each host discovers it | Native links for six hosts; open `skills` CLI for long-tail agents |

Collapsing these layers would make the public repository dangerous or make
runtime switching brittle. The boundary is the design.

## Practices that survive model changes

### 1. Verification before scale

Boris Cherny’s original workflow thread treats a feedback loop as the highest
leverage quality improvement. The durable version is broader than any one
agent: define what observable evidence proves the task, give the agent access
to that evidence, and require it before completion.

Agent Kit applies this through tests, `doctor --strict`, link status, data
validation, and a final evidence report. Parallel agents, scheduled loops, or
auto-accept modes come after one execution path is verifiable.

### 2. Context minimalism with progressive disclosure

The later Boris collection moves from large resident prompts toward a minimal
system prompt plus a way to fetch context. Addy Osmani’s skills use the same
shape: a small triggering `SKILL.md`, detailed references loaded only when
needed, and scripts for deterministic work.

Agent Kit therefore keeps the universal handoff to one sentence. The detailed
protocol lives in `docs/bootstrap.md`; operational variants stay in the
management skill’s references.

### 3. Turn corrections into infrastructure

A correction in chat fixes one run. A test, lint rule, hook, script,
instruction, or skill removes a class of repeated failure. Agent Kit records
selection policy in `catalog.json`, secret constraints in the public guard,
installation behavior in code, and acceptance in tests.

The preferred escalation is:

```text
one-off reminder → durable instruction → reusable skill → deterministic check
```

Move right only when the task repeats and the mechanism adds real marginal
value.

### 4. Preview, preserve, and make recovery obvious

Boris’s `/checkup` pattern is useful because it reports first, confirms scope,
and keeps changes reversible. CC Switch similarly uses a single source,
backups, content hashes, and symlink/copy distribution.

Agent Kit applies that discipline by:

- requiring a dry-run before install;
- refusing copied directories and foreign links;
- fast-forwarding only a clean checkout;
- exposing `managed-drift` separately from an unknown conflict;
- uninstalling only links owned by the current checkout.

### 5. Curate instead of hoarding

More skills increase trigger overlap, context cost, update work, and
supply-chain surface. A skill enters the catalog only when:

1. it solves a repeated current task;
2. the capability is not already provided by the host or catalog;
3. the source and license are explicit;
4. the accepted directory is pinned by full commit and tree SHA;
5. every executable is reviewed;
6. it fits a narrow profile;
7. its own checks and the repository gates pass.

That is why Agent Kit adopts selected standalone skills rather than mirroring
every popular pack.

Breadth belongs in a radar, not the global prompt. The
[`Top Skills Radar`](top-skills.md) can index official, specialist, and
community sources without installing them. The `top` profile contains only
the narrow set that passed every gate.

## Lessons adopted from the named projects

### CC Switch

Source: [farion1231/cc-switch](https://github.com/farion1231/cc-switch)

Adopted:

- one source of truth with per-host distribution;
- user-selectable symlink or copy semantics;
- backup and recovery as first-class behavior;
- content-hash update detection;
- a custom repository pointed at `cubxxw/agent-kit`, branch `main`,
  subdirectory `skills`.

Boundary retained:

- CC Switch is the better home for private provider, key, model, MCP, and
  session state;
- Agent Kit remains safe to publish and suitable for server bootstrap.

### UI UX Pro Max

Source:
[nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)

Adopted at commit `4d140cf8ff6842de13213c7214eff3810371beb2`:

- `ui-ux-pro-max`, a local standard-library search and design-system skill;
- its accessibility, interaction, responsive, and pre-delivery gates;
- its universal Agent Skills-compatible structure.

Review result:

- MIT license preserved;
- four runtime Python files reviewed;
- no network calls, subprocess execution, or third-party runtime dependency;
- persistence writes only under an explicit output directory and sanitizes
  project/page path segments;
- upstream data validation passes.

### Addy Osmani’s Agent Skills

Source: [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)

Adopted at commit `bdf76c7c6b7b3b3e01bb15c9fdc42ac5351855c1`:

- `source-driven-development`, because current official documentation is a
  distinct and repeated need with low overlap;
- the principles “process, not prose,” progressive disclosure, explicit
  verification, and dependency discipline.

Deferred:

- the full lifecycle pack. It is high quality, but installing every skill
  would overlap host-provided review, testing, security, and Git workflows;
- skills that depend on repository-level shared references when a standalone
  install would omit those references.

### Taste Skill

Source: [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)

Adopted at commit `e988add20dab0fa97d7a76781c48961c8184288e`:

- `design-taste-frontend` for landing pages, portfolios, and redesigns;
- brief inference before aesthetic choice;
- explicit variance, motion, and density controls;
- audit-first redesign behavior and a mechanical preflight.

Boundary retained:

- the upstream v2 is experimental and remains fully pinned;
- it is not a dashboard or dense product-UI skill;
- it is an anti-slop linter, not proof of an ownable design direction;
- its unpinned dependency examples are advisory only and do not grant package
  installation authority;
- the 1,206-line body loads only when its narrow trigger matches.

Review result:

- MIT license preserved and no executable files;
- vendored `SKILL.md` byte-matches the pinned upstream subtree;
- NVIDIA SkillSpector 2.5.3 static scan returned `SAFE`, score 18, with
  findings manually triaged.

### Recursive design depth

Source: real use of the adopted design stack on
[getyak/talent-signal](https://github.com/getyak/talent-signal).

Observed:

- build, responsive, accessibility, and Lighthouse evidence proved functional
  quality but not visual distinction;
- a self-authored 98/100 rubric overstated brand specificity;
- the refinement spent most of its visible effort on borders, shadows,
  background treatments, typography values, and hover motion while keeping the
  same direction;
- a negative-rule skill can replace obvious AI slop with a different,
  polished template.

Encoded as infrastructure:

- first-party `deepen-design` runs before the design data and preflight skills;
- every consequential design fork has two materially different branches;
- page direction is selected from rendered A/B evidence, not prose;
- functional gates and design judgment use separate ledgers;
- user rejection invalidates a distinctiveness claim and triggers
  backtracking, not another micro-detail pass.

Production evidence:

- `The Redline` beat `The Decision Window` at the brand-theorem fork;
- one governed conversation beat a persistent recruiter workbench at the
  architecture fork;
- a split evidence ledger beat transcript-with-margin-decisions after both
  compositions were rendered at desktop and mobile sizes;
- the implemented interaction made source removal retract the unsupported
  relationship state and revise the next action;
- lint, typecheck, 43 tests, documentation checks, and the production build
  passed independently of the design selection.

The result is evidence that the workflow can reach production safely. It is not
an absolute taste score or a substitute for future user preference.

### Open skills CLI

Source: [vercel-labs/skills](https://github.com/vercel-labs/skills)

Adopted:

- the root `skills/<name>/SKILL.md` discovery convention;
- symlink as the preferred one-source distribution method;
- a compatibility bridge for Claude Code, Codex, Qwen Code, OpenCode, Pi,
  OpenClaw, and many additional hosts.

## Time-sensitive advice

The [How Boris Uses Claude Code](https://howborisusesclaudecode.com/) site is
a useful, fan-maintained chronology, not a product specification. Its own
timeline demonstrates why operational advice needs dates:

- explicit Plan mode was central for earlier models, while later models made
  implicit planning and auto modes more useful;
- growing instruction files once felt like compounding knowledge, then
  `/checkup` exposed unused skills and large recurring context cost;
- later guidance emphasizes judgment, interfaces, progressive disclosure,
  richer references, and verification.

The stable rule is not “always plan” or “never plan.” Expose expensive,
high-blast-radius decisions before editing; skip ceremony for small,
established changes. Keep permissions proportional to risk and always retain
an observable verification path.

For a source-checked synthesis that separates Plan and Auto modes, worktrees,
goals, loops, and persistent routines, see
[Claude Code Playbook: 10 Configurations for Reliable Agent Workflows](https://cubxxw.com/ai-agent/posts/claude-code-boris-121-tips-playbook/).

## Review sources

- [Boris Cherny’s January 2026 thread](https://x.com/bcherny/status/2007179832300581177)
- [How Boris Uses Claude Code](https://howborisusesclaudecode.com/)
- [CC Switch skills manual](https://github.com/farion1231/cc-switch/blob/main/docs/user-manual/en/3-extensions/3.3-skills.md)
- [UI UX Pro Max README](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
- [Addy Osmani Agent Skills README](https://github.com/addyosmani/agent-skills)
- [Open skills CLI](https://github.com/vercel-labs/skills)
- [Top Skills Radar](top-skills.md)
- [Taste Skill](https://github.com/Leonxlnx/taste-skill)
- [NVIDIA SkillSpector](https://github.com/NVIDIA/SkillSpector)
- [Agent Skills specification](https://agentskills.io/specification)
