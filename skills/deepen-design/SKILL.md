---
name: deepen-design
description: Recursively turn generic or polished-but-forgettable landing pages, portfolios, and product-marketing surfaces into ownable design directions. Use when the user says a design is boring, generic, mediocre, shallow, templated, lacks taste or depth, asks for top-tier repeated refinement, or when a high-stakes design task needs divergent concepts before implementation. Orchestrates binary direction branching, visual evidence, pairwise critique, backtracking, and staged implementation; treats design-taste-frontend as a final anti-slop check rather than a direction generator.
---

# Deepen Design

Create a more ownable design, not merely a more decorated one.

Read [references/recursive-tree.md](references/recursive-tree.md) before work.
If the user is reacting to an unsatisfying prior result, also read
[references/failure-patterns.md](references/failure-patterns.md).

## Core distinction

Granularity has levels:

1. product truth and desired belief;
2. brand theorem and narrative metaphor;
3. page architecture and tempo;
4. section composition and interaction;
5. component language;
6. typography, color, spacing, borders, shadows, and motion polish.

Always descend in this order. A larger token set, more shadows, or more
micro-interactions is not deeper design when levels 1-4 remain unchanged.

## Start from rendered evidence

For an existing interface:

1. Preserve the current implementation and user changes.
2. Capture the current desktop and mobile first viewport.
3. Inspect at least two later sections and one meaningful interaction.
4. State what is objectively working.
5. State why the page is forgettable in five seconds.
6. Separate functional gates from taste judgments.

Treat “still mediocre” as a failed design test. Do not defend an earlier score
or continue the same direction by default.

## Build a bounded binary tree

At each direction-changing node, create exactly two materially different
branches. A valid branch changes the visual argument, information structure, or
signature interaction. A palette swap is not a branch.

Use beam search:

- expand two branches;
- make both visible at the cheapest useful fidelity;
- compare them pairwise;
- keep the strongest branch and one credible challenger;
- descend one level;
- backtrack when both children inherit the same weakness.

Do not construct every possible leaf. Spend depth on consequential decisions,
not combinatorial volume.

## Required depth gates

### Depth 0: product invariant

Write:

- the visitor;
- the moment of tension;
- what they should understand, feel, and do;
- the product truth that competitors cannot honestly claim in the same way.

Do not implement until this is specific.

### Depth 1: two brand theorems

Create two one-sentence positions with different implications. Each must yield:

- a narrative metaphor;
- a spatial grammar;
- a content priority;
- one signature mechanic;
- one explicit anti-reference: what this direction must not resemble.

Search three to five current, relevant references when external research is
available. Extract mechanisms, not a style collage. No candidate may copy one
reference’s complete visual identity.

### Depth 2: two architectures

For the leading theorem, branch the page into two different journeys. Define
the job, layout family, tempo, contrast event, proof, and exit action for every
section.

Reject an architecture when:

- most sections repeat “large heading + paragraph + image/card”;
- the product proof is interchangeable with a generic SaaS screenshot;
- removing the logo makes the category or brand unrecognizable;
- the only visible distinction is palette or typography.

### Depth 3: visual prototypes

Render both surviving directions before full implementation. Prefer:

- two first-viewport prototypes;
- one representative mid-page section for each;
- desktop first, then a mobile collapse check.

Compare screenshots side by side. Do not select from prose alone.

If the user is available and the directions encode genuinely different taste,
ask one concise fork question. If the user requested autonomy, choose from the
evidence and preserve the challenger.

### Depth 4: system and implementation

Only now define:

- type roles and scale;
- palette and contrast;
- asset language;
- grid, spacing, and shape rules;
- motion semantics;
- component primitives.

Use `ui-ux-pro-max` for relevant design-system data when available. Use
`design-taste-frontend` after direction selection as a preflight linter. Its
rules may reject clichés, but they may not choose the concept.

### Depth 5: micro-detail

Tune borders, shadows, material, hover, optical spacing, and performance only
after the direction and architecture gates pass.

Every micro change must name the parent decision it reinforces. Remove it when
it does not alter hierarchy, meaning, feedback, or material coherence.

## Evaluate the right thing

Keep two separate ledgers.

**Functional gate**

- product truth;
- responsive behavior;
- accessibility;
- performance;
- code and test health.

These are pass/fail constraints. They do not prove taste.

**Design judgment**

- five-second comprehension;
- logo-off ownability;
- visual recall after a delay;
- category-template distance;
- product-mechanic visibility;
- contrast and tempo across the whole page;
- user preference.

Use pairwise evidence from the reference workflow. Do not award an absolute
95/100 or 98/100 from a self-authored rubric. If the user says the result is
generic, the distinctiveness claim has failed regardless of Lighthouse.

## Finish with evidence

Return:

1. the explored tree and where it backtracked;
2. the winning direction and surviving challenger;
3. before/A/B screenshots or equivalent visual evidence;
4. the three largest visible changes, ordered by depth;
5. functional gate results;
6. unresolved taste or product decisions.

Do not describe micro-detail volume as the main outcome. The outcome is a
recognizable design argument that survives without the logo.
