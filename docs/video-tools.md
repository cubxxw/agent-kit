# YouTube scripts and local video rendering

The optional `video` profile contains `youtube-script`, its upstream successor
`youtube-script-writer`, and the four official HyperFrames core skills:
`hyperframes`, `hyperframes-cli`, `hyperframes-registry`, and `media-use`.
It is included in `top`, and does not expand `full-stack`.

This profile deliberately has no management-skill dependency: adding video tools
must not replace a management skill already owned by CC Switch or another host.
Keep each existing skill's installation owner.

## Install

```sh
./bin/agent-kit doctor --strict
./bin/agent-kit plan --profile video --tool core --json
./bin/agent-kit install --profile video --tool core
./bin/agent-kit status --profile video --tool core
```

`core` installs discovery links for local Codex and Claude Code. Start a fresh
session after installation. In Claude Code invoke `/youtube-script-writer` or
`/hyperframes`; in Codex select the named skill or use `$youtube-script-writer`
and `$hyperframes` in the request.

`youtube-script` is retained for the requested legacy name. The upstream root
skill marks it deprecated in favour of `youtube-script-writer`; prefer the
successor for new scripts. The legacy skill also includes an upstream
ContentGoldMine promotional footer. Neither skill includes executable code.

The CLI is a separate installation. This integration was checked with
`hyperframes@0.8.216` on Node.js 22. Install using an existing package manager:

```sh
pnpm add --global hyperframes@0.8.216 --ignore-scripts
hyperframes --version
hyperframes telemetry disable
hyperframes doctor --json
```

Local rendering also needs FFmpeg, FFprobe, and Chrome. Follow the bundled
`hyperframes-cli/references/doctor-browser.md` for native binaries and explicit
paths. Missing optional Docker, voice, or cloud services do not prevent a
local HTML render. Check the individual FFmpeg, FFprobe, and browser entries.

## Verify one small task

First verify the host's actual skill selector or discovery API, separately
from the filesystem links. Then create a short synthetic composition in an
isolated directory, with only local assets and one render worker:

```sh
HYPERFRAMES_SKIP_SKILLS=1 hyperframes init ./video-smoke --skip-skills
cd video-smoke
HYPERFRAMES_SKIP_SKILLS=1 hyperframes check --json
HYPERFRAMES_SKIP_SKILLS=1 hyperframes render --quality draft --workers 1 --output smoke.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height -of json smoke.mp4
```

Inspect a decoded frame as well as the duration. A local smoke render verifies
the installed toolchain; it does not establish voice, cloud, paid media,
publication, or arbitrary production-project compatibility.

## Ownership and external services

Update these vendored skills through Agent Kit's pinned-source review. Avoid
`hyperframes skills update` against Agent Kit-owned links; standalone upstream
installers can refresh a different distribution. Use `--skip-skills` or
`HYPERFRAMES_SKIP_SKILLS=1` when scaffolding a test so its setup leaves skill
ownership intact.

The scripts are invoked explicitly, not by skill discovery. Media generation
can select configured external providers and consume their quotas. Install
authority does not authorize provider calls, voice cloning, uploads, feedback
messages, or publishing. The current `media-use/scripts/resolve.mjs` is a legacy
monorepo shim; use the documented `hyperframes media-use resolve` CLI entrypoint.
Disable telemetry with the CLI setting or `HYPERFRAMES_NO_TELEMETRY=1` /
`DO_NOT_TRACK=1` when running isolated checks.
