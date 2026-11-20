---
name: paper-brush
description: Draw flat cut-paper illustrations (portraits, avatars, characters, scenes, icons) as deterministic code, no image model. Use for a set in one paper look or to add pictures matching one.
---

# Paper brush（纸艺画笔）

A deterministic renderer for **flat cut-paper illustration**: every picture is a short stack of coloured paper shapes,
each cut along a pen-tool path. Same drawing file in, same pixels out, so a set stays consistent and any shape can be
nudged by editing a few numbers. Any aspect, paper colour and size.

**Engine setup, once per project:** the renderer ships as a code block in `references/engine.md`. Copy it out with a
command, never by retyping it: `awk '/^```python$/{f=1;next} /^```$/{f=0} f' references/engine.md > DIR/paper.py`, with DIR
the project's art folder (or a scratch folder); the same command turns `references/example_drawings.md` into a drawings
file to start from. Run it with `python3 paper.py ...` (needs `numpy` and `opencv-python`). The commands below assume
that file. If `paper.py` already exists there, reuse it.

## The look (keep to it)

Read `references/style.md` before drawing. In short: few large shapes; few nodes with long arcs; real corners
marked as corners; 2–3 tones per material (base, shadow, sometimes a light); shadows are clean shapes clipped inside
their parent, often with one hard edge and one fading edge; no outlines around shapes; lines only where a pen line
would be (brows, lashes, a mouth, a fold) and always tapered; blush is the only blur; warm off-white paper and a
fine even grain over everything.

## Workflow

1. **Set up a drawings file** in the project (e.g. `Tools/art/drawings.py`) holding `DRAWINGS = {"name": {...}}`.
   The format is in the docstring of `paper.py` (`python3 paper.py` with no arguments prints it). Start from
   the drawings file in `references/example_drawings.md`.
2. **Pick an authoring grid** and, if you have one, a reference picture (a sketch, a painting, an approved image) laid
   on that grid. Read node coordinates off it at a known scale; a tiny lambda like `h = lambda *p: [(x/2, y/2, *r) for x, y, *r in p]`
   converts from the reference's pixels.
3. **Rough the shapes from a mask** if useful: make a black/white mask of a region (colour threshold, hand mask) and run
   `python3 paper.py nodes MASK.png [scale]` — it prints nodes with corners already found. Then thin and tidy them
   by hand; the hand pass is what makes it look cut, not traced.
4. **Render**: `python3 paper.py path/to/drawings.py OUT_DIR [name …]` → `OUT_DIR/<name>.png`.
5. **Look, compare, adjust.** Put the result next to the reference (or the approved set) at the size it will be seen,
   e.g. `ffmpeg -i a.png -i b.png -filter_complex hstack cmp.png`, and open it. Fix one thing at a time: a node, a tone,
   a clip. Expect several rounds; commit when the owner approves.
6. **Deliver** at the project's size and format (downscale with Lanczos; JPEG q≈88 or PNG). Images stay ≤ 2K.
   If the project watermarks its art, seal after approval, before shipping.

## Matching an existing set

When new pictures must join a set that already has a look (more avatars beside approved ones), the order is
**rules first, then draw, then iterate**:

1. **Study the references and write the rules down.** Zoom in and measure: how edges are built, tones per material,
   where shade shapes sit and how thin they are, feature sizes and positions on the head's axes, how much of the
   frame the head takes, paper colour and grain.
2. **Calibrate**: redraw one reference with the brush, put it beside the original, adjust until they match.
3. **Lift the parts** that carry the style (eyes, brows, ear inners) from the references:
   `python3 paper.py lift REF.png X Y [tol] --eyes x1,y1,x2,y2` prints the flat shape under pixel
   X,Y as nodes on that head's axes. Overlay to check; move the seed if it lands on skin.
4. **Draw over the source**: `python3 paper.py grid SOURCE.jpg grid.png` gives a gridded copy
   (lines every 20 px, labels every 100) to read coordinates off. Few nodes per shape: a face about 16, a hair mass 20–40.
5. **Mix-in test before showing anyone**: interleave the new pictures with the references in one grid at thumbnail
   size (about 480 px). If a new one can be picked out, it is not done. Then check each at full size beside its
   closest reference.

What does not work: shapes from imagination (every face comes out the same); tracing a realistic painting by colour
(copies its lumps); auto-vectorising references (blotchy); copying feature positions straight off a realistic face
(the mouth sits too low and the face reads long and old); shade shapes taken from a painting's dark areas (stains).

Typical face placement on the head's axes (measure your own set): brows about y −0.8, parallel to the eye line;
nose a short hook on the far side, x −0.3 to −0.65, y 0.45 to 1.15; mouth about 1.1 units wide at y 1.6 to 1.8,
nearly parallel to the eyes, both ends at about the same height (a raised end reads as a smirk); chin y 2.8 to 3.1.
Give every character its own hair silhouette, eye and brow shape, and palette, or the set drifts toward one face.
For tight curls, plaits and wool use `scallop()`; for knit collars `ribs()`; for lenses and buttons `oval()`
(`from paper import scallop, ribs, oval`).

## Faces: reusable parts

For a matching set of faces, give each drawing `"eyes": ((x, y), (x, y))`. That defines the head's own axes (x along
the eye line, y down the face, unit = half the eye distance), so features can be written once and set on any head:

- `{"head": True, "stroke": [...], "w": 0.12, "color": ...}` — nodes in head units (width too).
- `{"part": ("setname", "eye_l"), "fill": ..., "scale": 1.1, "shift": (0, 0.05), "turn": 4}` — a part from a
  `parts.py` placed **beside the drawings file**: `PARTS = {"setname": {"eye_l": {"nodes": [...]}, ...}}`, nodes
  in head units. Lift parts once from approved pictures (trace a part's mask with `nodes`, convert to head units),
  then every new face reuses them, which keeps the set looking like one hand.
- `"mirror": True` turns a face to look the other way without redrawing it.

## Gotchas

- Shapes paint in order; a `"clip"` only sees shapes already painted under that `"name"`.
- Several layers with the same `"name"` add up (union), handy for a body made of two pieces.
- `"fade"` points are in grid coordinates: strong at the first, gone at the second.
- `"soft"` is in grid units; keep it for blush and glows only.
- Drawings can `from paper import flow, scallop, ribs, oval`: the engine folder is on the path.
- Don't let a drawing drift into many tiny shapes or outlines; if a detail needs a line, ask whether a second tone
  shape would say it better.
