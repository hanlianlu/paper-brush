---
name: paper-brush
description: Draw flat cut-paper illustrations (portraits, avatars, characters, simple scenes, icons) as code — pen-tool paths with long arcs and crisp corners, flat fills, a second tone with one hard edge and one fade, tapered lines, a soft blush, warm paper ground and fine paper grain; no outlines, no gradients, no AI image model. Use when a project needs a set of illustrations in one consistent hand-made paper look, needs to redraw or extend such a set (e.g. more avatars matching approved ones), or asks for the "paper brush" / 纸艺画笔 / 剪纸风 style.
---

# Paper brush（纸艺画笔）

A deterministic renderer for **flat cut-paper illustration**: every picture is a short stack of coloured paper shapes,
each cut along a pen-tool path. Same drawing file in, same pixels out, so a set stays consistent and any shape can be
nudged by editing a few numbers. Engine: `scripts/paper.py` (numpy + OpenCV, run with `uv run`); any aspect,
paper colour and size.

## The look (keep to it)

Read `references/style.md` before drawing. In short: few large shapes; few nodes with long arcs; real corners
marked as corners; 2–3 tones per material (base, shadow, sometimes a light); shadows are clean shapes clipped inside
their parent, often with one hard edge and one fading edge; no outlines around shapes; lines only where a pen line
would be (brows, lashes, a mouth, a fold) and always tapered; blush is the only blur; warm off-white paper and a
fine even grain over everything.

## Workflow

1. **Set up a drawings file** in the project (e.g. `Tools/art/drawings.py`) holding `DRAWINGS = {"name": {...}}`.
   The format is in the docstring of `scripts/paper.py` (`uv run <skill dir>/scripts/paper.py` with no
   arguments prints it). Copy `references/example_drawings.py` as a starting point.
2. **Pick an authoring grid** and, if you have one, a reference picture (a sketch, a painting, an approved image) laid
   on that grid. Read node coordinates off it at a known scale; a tiny lambda like `h = lambda *p: [(x/2, y/2, *r) for x, y, *r in p]`
   converts from the reference's pixels.
3. **Rough the shapes from a mask** if useful: make a black/white mask of a region (colour threshold, hand mask) and run
   `uv run <skill dir>/scripts/paper.py nodes MASK.png [scale]` — it prints nodes with corners already found. Then thin and tidy them
   by hand; the hand pass is what makes it look cut, not traced.
4. **Render**: `uv run <skill dir>/scripts/paper.py path/to/drawings.py OUT_DIR [name …]` → `OUT_DIR/<name>.png`.
5. **Look, compare, adjust.** Put the result next to the reference (or the approved set) at the size it will be seen,
   e.g. `ffmpeg -i a.png -i b.png -filter_complex hstack cmp.png`, and open it. Fix one thing at a time: a node, a tone,
   a clip. Expect several rounds; commit when the owner approves.
6. **Deliver** at the project's size and format (downscale with Lanczos; JPEG q≈88 or PNG). Images stay ≤ 2K.
   If the project watermarks its art, seal after approval, before shipping.

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
- Drawings can `from paper import flow` to build helpers (curl scallops, plait bumps): the engine folder is on the path.
- Don't let a drawing drift into many tiny shapes or outlines; if a detail needs a line, ask whether a second tone
  shape would say it better.
