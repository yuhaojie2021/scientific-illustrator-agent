# Agent visual refinement loop

This is a host-agent workflow, not a Python renderer option or an embedded
vision model. The agent views actual Illustrator PNG exports, reasons about
visible defects, changes the source/specification, and renders again. Repeating
one unchanged script three times is not visual refinement.

## Budget and applicability

Default to **3 total review rounds**, including the initial render, for new
artwork and requested visual improvements. User instructions such as "loop 5",
"iterate twice", "one pass only", "quick draft", or "stop" override this budget.
A round is a successful render/export followed by actual visual inspection;
a failed COM operation does not count as a reviewed round. Do not apply this
loop to installation, diagnostics, explanation-only tasks, or faithful replay
of already approved artwork. For live progressive/swarm presentations, refine
and inspect the artwork before running the presentation once; do not repeat
the live performance unless requested.

Complete all 3 reviews by default. A review with no actionable defect may be a
no-change review; do not invent cosmetic edits merely to spend the budget.
Do not call repeated viewing of the same image three independent revisions.
After round 3, deliver the best verified result and disclose remaining issues.
Do not continue indefinitely. A further user request starts a new scoped budget.

## Before rendering

- Record the target document/artboard and authorized layer/group. Preserve
  unrelated artwork. For an existing document, inspect its current state and
  retain the source/spec or a scoped editable backup before replacing artwork.
- Choose observable acceptance criteria from the request: required content,
  reference silhouette/style, topology, label fidelity, readable final size,
  alignment, spacing, palette, and editability. Do not invent scientific data.
- Use one stable scene ID or named group across rounds. Keep versioned specs,
  JSX when applicable, previews and a short `iteration_log.md` in the task's
  output directory. Never write task outputs into the installed skill folder.
  Preserve a recoverable editable version of the best round before revising it;
  a PNG alone cannot restore editable Illustrator objects.

## Three-round procedure

### Round 1: Build and inspect structure

Render the full intended composition, export a whole-figure PNG, and actually
view it with an available image-viewing tool. Check required elements, hierarchy,
reading order, graph topology, text fidelity, and overall reference similarity.
Inspect detailed crops as well when irregular paths, layered planes, labels,
arrows, or dense connections are too small in the whole view. Record concrete
visible problems, their locations, and the next targeted changes.

### Round 2: Correct and inspect layout

Fix the most consequential observed defects, normally 1-3 related changes:
missing/incorrect elements first, then overlap/clipping, then alignment,
spacing, scale, routing or silhouette. Preserve successful parts. Export a new
PNG and view both the composition and changed detail. Compare against round 1
and the reference. Check regressions outside the changed region. Update the log.
If no edit is justified, record the specific checks made and keep the artwork.

### Round 3: Polish and verify

Resolve remaining visible issues such as inconsistent line weights, arrowhead
proportions, gradient direction, jagged contours, font fallback, crowded feature
strips, and uneven colors. Export and view the final full figure and any critical
crop; validate text and observed object counts when the renderer supports it.
If a change worsens the result, restore the best editable round and verify its
preview. Never claim a reverted or unviewed revision is the final artifact.

## Iteration log

A short Markdown record is sufficient; no numerical beauty score is required:

| Round | Actual preview | Observed defects/checks | Changes or no-change reason | Result / remaining issues |
| --- | --- | --- | --- | --- |
| 1 | round_01.png | Specific visible evidence | Planned next correction | ... |
| 2 | round_02.png | Comparison and regression check | Actual corrections | ... |
| 3 | round_03.png | Final whole/detail review | Actual corrections or justified no change | ... |

Record which round was selected and where its editable source is retained.
A no-change round can reference the previous preview explicitly. Reports must
state actual renders, edits and reviews accurately; do not equate 3 reviews
with 3 distinct renders if the artwork was unchanged.

## Failure and delivery

On COM errors, crashes, unexpected active-document changes, missing outputs or
export failure, stop mutations and inspect state. Do not automatically rerun a
possibly applied mutation. Resume only after identifying state/cause and making
a justified correction, within the existing authorization. If visual inspection
is unavailable, report that the loop is incomplete; object counts alone do not
establish visual quality. Do not fabricate observations or declare 3 rounds done.

Keep the user informed at meaningful checkpoints. At delivery briefly report
actual review/repair rounds, the principal improvements, the final preview,
editability verification and any material remaining limitation. Saving or
replacing the user's AI file still follows the user's requested scope; the
review budget does not authorize overwriting unrelated work.
