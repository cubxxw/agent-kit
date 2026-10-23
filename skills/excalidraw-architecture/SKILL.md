---
name: excalidraw-architecture
description: Create, revise, render, and review editable Excalidraw diagrams for collaborative whiteboarding, open-ended architecture exploration, workshops, narrative maps, hand-drawn technical communication, and polished SVG/PNG handoff. Use for Excalidraw files, live human editing, evolving structure, alternatives and unknowns, or requests to improve diagram layout, connectors, hierarchy, and visual quality. Also use when choosing between Excalidraw and Archify; route formal, validated, repository-backed, interactive, or Before/Delta/After technical documentation to Archify.
---

# Excalidraw Architecture

Create diagrams that explain a decision or route, not decorated inventories.

## Choose the medium

Read [tool-choice.md](references/tool-choice.md) whenever the request could fit
both Excalidraw and Archify.

- Use Excalidraw when the artifact must help people think together: the
  structure is still moving, alternatives and questions matter, live editing
  is central, or hand-drawn language usefully avoids false precision.
- Use Archify when the artifact must freeze an inspectable technical claim:
  typed topology, repository evidence, architecture deltas, multiple reading
  depths, route exploration, deterministic validation, or formal delivery.
- Use both in sequence when discovery is genuinely needed: explore in
  Excalidraw, freeze the accepted facts and question, then author fresh typed
  Archify IR. Never convert the sketch geometry mechanically.

If a strict offline or zero-external-request artifact is required, prefer the
local Excalidraw export unless the Archify delivery has been explicitly made
offline-safe.

## Choose the working mode

- **Workshop mode:** expose competing routes, assumptions, questions, and
  decision points. Keep uncertainty visible and leave room for people to move
  the scene. Optimize for conversation, not final polish.
- **Delivery mode:** copy the accepted structure into a clean scene, remove
  abandoned branches, freeze connector semantics, and run the full render and
  screenshot gate below.

Do not mix a messy workshop history and a final architecture claim in one
canvas. Preserve the workshop source separately when its reasoning history is
valuable.

## Deliverables

Unless the user narrows the request, deliver:

1. editable `.excalidraw`;
2. reviewable `.svg` and `.png`;
3. a one-paragraph reading guide;
4. the final scene opened in Excalidraw when browser delivery is useful.

In workshop mode, the editable `.excalidraw` is mandatory; rendered outputs
are optional unless the user needs an async review snapshot.

Use solid strokes for V1/current scope and dashed strokes for later scope. Add a
visible legend. Do not reuse dashed strokes for uncertainty in the same
architecture diagram.

## Workflow

1. **Read before drawing.** Inspect the source notes, repository, existing
   architecture, and audience. Write down the one question the diagram answers.
   In workshop mode, also name the decision that remains open.
2. **Freeze semantics.** Separate current, later, external, derived, and
   authoritative components. Identify the main route, feedback route, trust
   boundary, and forbidden shortcuts.
3. **Choose one composition.**
   - Product story: left to right, 3-5 stages, outcome loop below.
   - System architecture: top to bottom layers, primary runtime left to right.
   - Lifecycle: circular only when the final state truly feeds the first.
   - Topology: hub and spoke only when one authority actually coordinates peers.
4. **Sketch hierarchy.** Use 5-9 primary groups. Give the primary route the
   shortest visual path. Put details inside labeled bands, not nested cards.
5. **Build the scene.** Follow
   [visual-system.md](references/visual-system.md) and
   [json-contract.md](references/json-contract.md). Mark scope-bearing elements
   with `customData.phase: "v1"` or `"later"`.
6. **Render and validate.**

   Run these commands from this skill directory:

   ```bash
   node scripts/render-excalidraw.mjs \
     path/to/diagram.excalidraw --png path/to/diagram.png
   node scripts/validate-excalidraw.mjs \
     path/to/diagram.excalidraw --png path/to/diagram.png
   ```

   SVG export requires only Node.js. PNG export also requires ImageMagick;
   macOS uses Quick Look when available and other systems render through
   ImageMagick directly.

7. **View the full-resolution PNG.** Fix clipping, collisions, weak hierarchy,
   bad wrapping, crowded arrows, excess whitespace, and route ambiguity. Render
   again after every meaningful edit.
8. **Audit the meaning.** Trace every important arrow. Confirm that readers
   cannot mistake a derived view for a source of truth or a proposal for an
   executed action.

## Drawing Rules

- Prefer one strong visual argument over a grid of equal boxes.
- Show overview, section boundaries, and concrete nodes at distinct zoom levels.
- Keep connector labels short; put explanations beside the route, not on it.
- Route connectors behind nodes and into edges. Avoid crossing text or entering
  arbitrary box corners.
- Reserve accent color for one decision, write boundary, or critical transition.
- Default to `roughness: 1`; use `0` only for dense technical regions and `2`
  only for a deliberately rough annotation.
- Default text to Excalifont (`fontFamily: 5`), which uses Xiaolai as the
  current Excalidraw CJK hand-drawn fallback. Use Nunito (`6`) when dense
  technical copy needs a quieter voice.
- Use font sizes `36 / 28 / 20 / 16 / 14`; never finish with body text below 14.
- Keep titles to one line and bodies to three short lines where possible.
- Use color plus labels and stroke style; never rely on color alone.
- Add icons only when they identify a real platform or service faster than text.
- Do not use gradients, shadows, decorative blobs, or ornamental arrows.

## Completion Gate

Finish only when:

- the audience and diagram question are obvious on first scan;
- workshop unknowns cannot be mistaken for accepted facts;
- V1 and later scope are distinguishable without color;
- every important route has a direction and valid endpoints;
- no text is clipped, overlapping, or too small at export size;
- contrast is at least 4.5:1 for normal text;
- all nodes, bindings, IDs, and phase styles pass the validator;
- the PNG has been visually inspected, not merely generated;
- the editable source and rendered outputs describe the same frozen scene.
