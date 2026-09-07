# Top Skills Radar

Reviewed on 2026-09-07. Repositories, licenses, install counts, and skill
contents change; recheck the source before adoption.

## Top is a pipeline, not a dump

Agent Kit uses three layers:

| Layer | Meaning | Update policy |
|---|---|---|
| **Adopted** | Fully reviewed, pinned, licensed, vendored, tested, and safe for the shared profiles | Install through Agent Kit |
| **On demand** | High-signal source with a clear specialist use, but unnecessary as global context | Browse, audit one named skill, then install for the relevant project |
| **Radar** | Useful discovery source or broad framework whose individual entries are not trusted by association | Never bulk-install |

The `top` profile contains every broadly useful skill that passed the full
adoption gate. The radar can be broad because it installs nothing.

## Adopted set

| Skill | Source | Role |
|---|---|---|
| `manage-agent-kit` | `cubxxw/agent-kit` | Safe cross-agent initialization, upgrades, and curation |
| `boundary-demo` | `cubxxw/agent-kit` | One-decision boundary probes with reusable case/eval evidence |
| `deepen-design` | `cubxxw/agent-kit` | Recursive direction branching, pairwise visual critique, and backtracking before polish |
| `mcp-builder` | [`anthropics/skills`](https://github.com/anthropics/skills) | MCP server design and evaluation |
| `source-driven-development` | [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) | Implementation grounded in current official sources |
| `ui-ux-pro-max` | [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | Searchable UI/UX data and stack guidance |
| `design-taste-frontend` | [`Leonxlnx/taste-skill`](https://github.com/Leonxlnx/taste-skill) | Anti-template frontend constraints and final preflight |

`deepen-design` answers “which product-derived direction should exist?”
`ui-ux-pro-max` answers “what patterns, palettes, stacks, and constraints fit?”
`design-taste-frontend` answers “which familiar frontend mistakes remain?”
They are complementary. The latter is a preflight linter, not a substitute for
divergent direction work, and explicitly excludes dense dashboards and
multi-step product UI.

## Official and product-owned sources

Prefer these when the task is already inside the source owner’s domain.
“Official” reduces provenance uncertainty; it does not waive per-skill code,
license, permission, or secret review.

| Source | Best fit | Status |
|---|---|---|
| [`openai/skills`](https://github.com/openai/skills) | Codex-native document, browser, GitHub, and product workflows | Host-managed; do not vendor tool-coupled skills |
| [`streamlit/streamlit`](https://github.com/streamlit/streamlit/tree/develop/lib/streamlit/.agents/skills/developing-with-streamlit) | Version-matched Streamlit layout, state, testing, performance, and template guidance | Load from the probe's installed Streamlit package; do not vendor or create global discovery links |
| [`anthropics/skills`](https://github.com/anthropics/skills) | Claude-compatible documents, frontend, testing, and MCP workflows | Audit per-skill license; `mcp-builder` adopted |
| [`vercel-labs/agent-skills`](https://github.com/vercel-labs/agent-skills) | React/Next.js performance, composition, interface and writing review | Strong on-demand source; avoid installing deployment skills globally |
| [`MicrosoftDocs/Agent-Skills`](https://github.com/MicrosoftDocs/Agent-Skills) | Microsoft Learn and Azure guidance | On demand for Microsoft/Azure work |
| [`microsoft/azure-skills`](https://github.com/microsoft/azure-skills) | Azure planning, cost, reliability, migration, and deployment | On demand; project credentials remain local |
| [`huggingface/skills`](https://github.com/huggingface/skills) | Models, datasets, Spaces, training, evaluation, and Hub operations | Install only the workflow in use |
| [`nvidia/skills`](https://github.com/nvidia/skills) | CUDA, robotics, simulation, RAG, and NVIDIA platform workflows | Official verified catalog; vertical, not global |
| [`dotnet/skills`](https://github.com/dotnet/skills) | .NET and C# engineering | On demand for .NET repositories |
| [`supabase/agent-skills`](https://github.com/supabase/agent-skills) | Supabase and Postgres practices | On demand for Supabase projects |
| [`firebase/agent-skills`](https://github.com/firebase/agent-skills) | Firebase auth, data, hosting, and app hosting | On demand for Firebase projects |
| [`prisma/skills`](https://github.com/prisma/skills) | Prisma setup, client, drivers, and upgrades | On demand for Prisma projects |
| [`remotion-dev/skills`](https://github.com/remotion-dev/skills) | Programmatic video with Remotion | On demand for Remotion work |
| [`larksuite/cli`](https://github.com/larksuite/cli) | Feishu/Lark documents, Base, calendar, mail, and tasks | On demand; requires explicit account-action authority |

## High-signal community sources

These are worth following, but broad behavioral frameworks and large packs
have higher overlap and triggering risk than narrow specialist skills.

| Source | Distinct value | Current decision |
|---|---|---|
| [`mattpocock/skills`](https://github.com/mattpocock/skills) | Grilling, domain language, planning, diagnosis, handoff, and focused engineering workflows | Watch and adopt narrowly; do not install the entire methodology beside overlapping hosts |
| [`obra/superpowers`](https://github.com/obra/superpowers) | Coherent end-to-end development methodology with verification and review loops | Use as its own framework, not mixed into Agent Kit defaults |
| [`helderberto/agent-skills`](https://github.com/helderberto/agent-skills/tree/main/skills/prototype) | A prototype answers one question and can be discarded | Reference only; its blanket no-test rule conflicts with durable case/eval evidence |
| [`frontend-design`](https://github.com/anthropics/skills/tree/main/skills/frontend-design) / [`webapp-testing`](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) | Visual direction and browser verification | Invoke only when taste or real browser behavior is the variable; do not make either the default probe loop |
| [`emilkowalski/skills`](https://github.com/emilkowalski/skills) | Design engineering and motion judgment | On-demand design candidate |
| [`pbakaus/impeccable`](https://github.com/pbakaus/impeccable) | Interface design language and anti-slop review | Watch for overlap with the adopted design stack |
| [`trailofbits/skills`](https://github.com/trailofbits/skills) | Security research and audit workflows | Excellent specialist source; review CC-BY-SA obligations |
| [`coreyhaines31/marketingskills`](https://github.com/coreyhaines31/marketingskills) | CRO, SEO, analytics, copy, and growth | Project-scoped; overlaps Brain’s private content skills |
| [`JimLiu/baoyu-skills`](https://github.com/JimLiu/baoyu-skills) | Chinese content, URL ingestion, transcripts, images, and publishing workflows | Keep Brain-specific installs repository-scoped |
| [`OthmanAdi/planning-with-files`](https://github.com/OthmanAdi/planning-with-files) | Durable file-based planning across compaction and long tasks | Strong candidate when current goal/task state is insufficient |
| [`K-Dense-AI/scientific-agent-skills`](https://github.com/K-Dense-AI/scientific-agent-skills) | Large science and research workflow collection | Vertical; select by scientific task |
| [`tt-a1i/archify`](https://github.com/tt-a1i/archify) | Verifiable animated architecture diagrams | Compare against existing Excalidraw/visualization skills first |
| [`Agents365-ai/drawio-skill`](https://github.com/Agents365-ai/drawio-skill) | Editable Draw.io, C4, UML, BPMN, and network diagrams | On-demand diagram candidate |

## Discovery and security infrastructure

| Source | Use | Trust boundary |
|---|---|---|
| [`skills.sh`](https://skills.sh/) / [`vercel-labs/skills`](https://github.com/vercel-labs/skills) | Search, install-count signal, multi-agent distribution | Ranking is discovery evidence, not a safety verdict |
| [`github/awesome-copilot`](https://github.com/github/awesome-copilot) | GitHub-hosted community examples and instructions | Community entries require individual review |
| [`VoltAgent/awesome-agent-skills`](https://github.com/VoltAgent/awesome-agent-skills) | Broad cross-agent directory | Never bulk-install from an awesome list |
| [`ComposioHQ/awesome-claude-skills`](https://github.com/ComposioHQ/awesome-claude-skills) | Claude-oriented discovery directory | Links may have different or missing licenses |
| [`NVIDIA/SkillSpector`](https://github.com/NVIDIA/SkillSpector) | Static and optional semantic security scan before adoption | Scanner findings need human triage; it does not replace executable review |

## Safe discovery command

Pin the installer used during this review:

```sh
DO_NOT_TRACK=1 npm exec --yes --package=skills@1.5.21 -- \
  skills add <owner/repository> --list
```

Before installing a named candidate:

1. prove a repeated current need;
2. inspect only the selected subtree;
3. resolve its full commit and tree SHA;
4. verify a redistributable license;
5. read every executable and dependency file;
6. scan for network, credential, destructive, and excessive-agency behavior;
7. compare its triggers against installed skills;
8. install into the narrowest profile or keep it project-scoped;
9. preview links, validate host discovery, and return evidence.

Popularity, install counts, an “official” badge, or inclusion in this radar
never authorizes installation or external account actions.
