# Recursive Design Tree

Use this protocol to deepen a design without falling into endless decoration.

## Contents

1. Tree model
2. Node record
3. Pairwise selection
4. Evidence by depth
5. Backtracking and stop rules

## 1. Tree model

```text
D0 product invariant
├─ D1-A brand theorem / metaphor
│  ├─ D2-A1 page architecture
│  └─ D2-A2 page architecture
└─ D1-B brand theorem / metaphor
   ├─ D2-B1 page architecture
   └─ D2-B2 page architecture

Beam after D2: keep the strongest path plus one challenger.

Winner
├─ D3-A first-viewport composition
└─ D3-B first-viewport composition

Selected composition
├─ D4 system decisions
└─ D5 micro-detail
```

The tree is binary at each consequential fork, but bounded globally. Do not
render all leaves at production fidelity.

## 2. Node record

Record every consequential node as:

```markdown
### <depth and name>

- Question:
- Parent invariant:
- Branch A:
- Branch B:
- Evidence needed:
- Expected visible difference:
- Failure signal:
- Winner:
- Why:
- Challenger retained:
- Backtrack condition:
```

Branches must be mutually exclusive enough that a neutral reviewer can tell
which one a screenshot represents.

## 3. Pairwise selection

Compare A against B with relative values from `-2` to `+2`. Do not turn the
result into an absolute quality score.

| Criterion | Weight | Question |
|---|---:|---|
| Ownability | 25 | With the logo hidden, which direction is less interchangeable? |
| Product truth | 25 | Which makes a real product mechanism visible rather than merely claimed? |
| Five-second clarity | 15 | Which makes the visitor, tension, and next action legible faster? |
| Structural distinction | 15 | Which changes composition and tempo rather than only styling? |
| Emotional precision | 10 | Which creates the intended feeling without generic “premium” signals? |
| Feasibility | 5 | Which can be implemented honestly with available assets and time? |
| Accessibility/performance risk | 5 | Which preserves the functional gate with less risk? |

Write one falsifiable reason for every non-zero comparison. “Feels more
premium” is not evidence.

## 4. Evidence by depth

| Depth | Minimum evidence |
|---|---|
| D0 | Product behavior, user tension, current page, existing brand assets |
| D1 | Two brand theorems, 3-5 relevant references, anti-reference for each |
| D2 | Section maps with distinct layout families and proof placement |
| D3 | A/B screenshots: first viewport plus one representative section |
| D4 | Token specimen, real asset sample, meaningful interaction state |
| D5 | Browser comparison, responsive checks, reduced motion, performance |

Do not use Lighthouse, test counts, or implementation volume as evidence at
D1-D3.

## 5. Backtracking and stop rules

Backtrack when:

- both children can share the same screenshot;
- the signature mechanic is decorative rather than tied to product behavior;
- the chosen branch is mostly explained with color, shadow, radius, or font;
- the page still resembles the named anti-reference;
- user feedback rejects the direction.

Stop descending when:

- the next fork would not change a screenshot or meaningful interaction;
- remaining decisions are normal craft execution;
- the user can identify the design and product mechanism after the logo-off
  test;
- functional gates pass and no unresolved high-level decision remains.

Suggested effort distribution:

- D0-D1: 25%
- D2: 25%
- D3: 25%
- D4: 20%
- D5: 5%

If micro-detail consumes the majority of a “make it less generic” task, the
process is upside down.
