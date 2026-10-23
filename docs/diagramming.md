# Diagramming: installed package contract

Use `diagramming` for the two complementary media. `full-stack`, `top`, and
`all` also include it; the existing prototyping and optional writing profiles
retain their roles. Node.js 18 or newer is required for diagram commands.
Agent Kit does not install Node or enable host links during repository checks.

## Choose and finish the artifact

Use `excalidraw-architecture` for an evolving workshop, alternatives, or an
editable handoff. Read its tool-choice, visual-system, and JSON references.
The `.excalidraw` source is authoritative. The local renderer supports
rectangles, frames, ellipses, diamonds, arrows, lines, freehand polylines, and
text. It is a simplified SVG preview, not Excalidraw's native rendering engine:
roughness, native arrowhead styles, and font availability may differ. Images
and other unsupported types fail instead of silently disappearing. Open the
source in Excalidraw for native editing and verify its appearance separately.

From the skill directory:

```sh
node scripts/validate-excalidraw.mjs scene.excalidraw
node scripts/render-excalidraw.mjs scene.excalidraw --svg scene.svg
node scripts/render-excalidraw.mjs scene.excalidraw --png scene.png
node scripts/validate-excalidraw.mjs scene.excalidraw --png scene.png
```

SVG needs only Node. PNG additionally needs ImageMagick (`magick`); macOS
uses Quick Look when available. Do not install a missing dependency implicitly.
Validate identifiers, bindings, phase semantics, text size, and contrast, then
inspect the actual PNG for wrapping, clipping, route ambiguity, and collisions.
A validator pass does not establish visual quality or native-editor fidelity.

Use `archify` to formalize accepted facts. Read its schemas, matching example,
and authoring/delivery contracts. Keep facts, proposals, and unknowns distinct;
never infer storage guarantees, cache behavior, latency, or causality from the
shape of a sketch. A hybrid workflow authors fresh typed JSON from accepted
facts rather than copying sketch coordinates.

From the Archify skill directory:

```sh
node bin/archify.mjs doctor
node bin/archify.mjs validate architecture examples/web-app.architecture.json --quality showcase --json
node bin/archify.mjs deliver architecture examples/web-app.architecture.json /tmp/architecture.html --quality showcase --json
```

Choose `architecture`, `workflow`, `sequence`, `dataflow`, or `lifecycle` to
match the question. Acceptance requires the complete nine-check showcase
receipt, zero errors and warnings, plus separate visual review. Report the
specification/artifact hashes and truthful visual-review status. Changes after
validation require a new validation and delivery. Optional live preview binds
to loopback and must be stopped before handoff; do not start it by default.

Generated Archify HTML requests Google Fonts and includes a user-clicked
product link. It is not a zero-request artifact. Use local Excalidraw exports
or explicitly harden and recheck the HTML when strict offline delivery matters.
No diagram content is sent to a generation service by the bundled CLI.

## Reproducible repository checks

```sh
python3 -m unittest discover -s tests -v
./bin/agent-kit doctor --strict
python3 skills/ui-ux-pro-max/scripts/validate_data.py
```

The portable integration suite delivers all five Archify modes with checked
specification/artifact hashes, reproduces the packaged golden HTML, validates
an Excalidraw scene, and exports SVG. It also checks that unsupported scene
content and unsafe SVG attributes cannot replace a previous export, and that
output aliases cannot overwrite the editable input. These checks require no
`node_modules` and do not change real host installation state.

Archify's `archify/` subtree is retained at its catalog pin, byte-for-byte,
with a duplicate `LICENSE.txt` for Agent Kit's license convention. Its bundled
`package.json` also retains upstream development commands. `npm test`, the
website/guide/gallery/release builds, the full golden harness, and some tests
refer to upstream files outside that subtree. Validator regeneration needs
the declared AJV development dependency. These are upstream-development
workflows, not supported standalone package commands. Use the full upstream
repository at the pinned commit if those workflows are needed; do not copy its
website or deployment state into Agent Kit to make them appear available.

Recovery verification on 2026-10-23 ran every bundled `*.test.mjs`: 526 passed
and 57 failed out of 583 tests. Those failures reference omitted upstream
website, release, benchmark, or example files, or the absent AJV build
dependency. This is not a passing full-suite result. The separate core run passed 266 tests with zero failures and excluded the
one upstream-only CLI fixture test. It covers CLI delivery, invalid-input handling, geometry, grids, layout rules,
output alias protection, repository evidence, legends, opening, and loopback
preview. Its one excluded CLI test references the omitted upstream
`examples/archify-repo-grid.architecture.json`; packaged architecture examples
are covered by the portable integration tests instead.
