# Editable components and current-document updates

Use `examples/components.py` for matrices, feature strips, graphs and connected
data-flow diagrams. Existing FigureSpec, progressive SVG and swarm entry points
remain supported. Paths below are relative to the skill directory; invoke with
absolute paths when working elsewhere.

## Environment

Read `runtime.local.json` if present and verify that its `executable` still exists.
Use that interpreter for this skill. This local file contains no credentials and
must not be distributed. If absent, check an available Python:

```powershell
python examples/components.py doctor
python examples/components.py doctor --connect --remember
```

`--connect` can start Illustrator. `--remember` writes the interpreter only when
dependency imports, version constraints and COM/JSX health checks pass. Install
missing dependencies into a separate virtual environment using requirements.txt;
do not change global packages. Desktop COM may require execution outside a
restricted sandbox; request the corresponding execution permission rather than
repeatedly retrying a failing call. Connection errors are diagnostics, not proof
that Illustrator is missing.

## Render

```powershell
python examples/components.py render examples/specs/components_demo.json --validate-only
python examples/components.py render examples/specs/components_demo.json --target new --preview C:\work\new-preview.png --report C:\work\new-report.json
python examples/components.py inspect
python examples/components.py render C:\work\scene.json --target active --expected-document "Untitled-1" --preview C:\work\updated-preview.png
```

Use `inspect` to obtain the exact Unicode document name, then pass that name
unchanged. Current-document mode is appropriate when the user requests it.
Neither rendering mode saves or overwrites an AI file. Save only when requested
or when saving is part of the requested deliverable. Preview and report paths
must be fresh. Preview export uses a temporary artboard cropped to artwork
bounds and removes it afterward. Export failure does not roll back a successful
render: inspect the scene before retrying, and do not silently redraw it.

## Scene contract

See `examples/specs/components_demo.json` and `src/models/component_spec.py` for
the complete validated schema. Coordinates are points relative to the active
artboard's top-left, with y increasing downward. New documents use width/height;
active documents retain their artboards.

- Every scene has `scene_id`. A render replaces only the layer named
  `SCI_COMPONENTS:<scene_id>`. Use distinct IDs for independent scenes.
- Every component has an `id`, `type`, `x`, `y`, optional `title`, `font`, and
  `font_size`. Labels preserve one whole block per text frame, including newlines.
- `matrix`: nonempty rectangular `cells` containing `#RRGGBB`; `cell_size`,
  `row_label`, `column_label`. x/y mark the matrix top-left, excluding labels.
- `feature_strip`: `features` color array and `cell_size`.
- `graph`: `nodes` with unique IDs, relative x/y, optional `label`, and optional
  `features` color array; `edges` reference node IDs and can specify `color`.
  Graph x/y is the local origin and title anchor. `node_radius` sets node size.
- `text`: `title` is centered at x/y.
- `links`: each has unique `id`, `source`, `target`, optional `label`. Endpoints
  are recomputed from component bounds. Leave at least 20 pt between bounds.

For updates, edit components by ID in the saved scene JSON, then submit the full
scene with the same scene_id. The renderer rebuilds that scene, rather than
patching individual Illustrator objects. It does not import manual Illustrator
edits back into JSON. Manually edited generated objects will be replaced on the
next update; unrelated layers are preserved. Older drawings without these IDs
require explicit migration and are not adopted automatically.

The replacement is constructed and object/text counts verified before the old
layer is removed. On construction failure the staged layer is removed, retaining
the old layer; this is best-effort recovery, not an application transaction.
Reports distinguish cells, nodes, graph edges, feature cells, text frames and
data-flow arrows. Check warnings and inspect the cropped PNG after rendering.
Current checks include exact text contents, semantic counts, invalid references,
and artboard overflow. Text collision detection and native arrowheads are not
implemented in this entry point: each arrow is an editable grouped line and
triangle. Routes are straight lines, so inspect crossing/overlapping labels.

## Visual refinement rounds

Use the default 3-round host-agent loop in `visual_refinement.md`. Keep the same
scene ID across revisions and fresh preview/report paths for each actual render.
Retain each scene JSON before updating it. Since replacement removes the previous
generated layer, retain the previous spec as an editable recovery source, or a
scoped duplicate when manual JSX objects are used. The CLI does not evaluate
beauty or accept `--loop`; the agent must view PNGs and choose targeted changes.
