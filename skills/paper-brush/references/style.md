# Paper brush — style rules

What makes a picture read as cut paper rather than vector clip-art or a traced painting.

## Shapes
- **Few, large shapes.** A head-and-shoulders portrait is roughly: back hair, body/clothes (2 pieces), neck, face,
  ears, front hair, then tones and features. 15–40 layers, not hundreds.
- **Few nodes, long arcs.** A cheek is 3–5 nodes, not 30. Let `flow` make the curve.
- **Corners are decisions.** Mark `"c"` where scissors would turn: hair tips, collar points, the chin–jaw meeting,
  a sleeve hem. Everywhere else the curve flows through.
- **Overlap rather than butt.** Lay the back piece larger and let the front piece cover it; it hides seams and gives
  the stacked-paper feel.
- **Silhouettes first.** If a shape doesn't read in a flat single colour, more tones won't save it.

## Colour
- **Warm, muted, slightly dusty palette**; no pure black or white. Darkest darks are deep browns/inks
  (e.g. `#2A1A14`), whites are cream (e.g. `#F3EFE6`).
- **2–3 tones per material**: base, shadow (darker, a little warmer/more saturated), occasionally a light.
- **Paper ground** defaults to `#F7ECE0`; keep the background plain.
- Skin: base plus one shadow tone; a blush (`soft`) on the near cheek; the inside of the ears a deeper tone.

## Depth
- Shadows are **clean shapes clipped inside their parent** (`"clip"`): under the chin on the neck, under the hair on
  the forehead, the inside of a hood, a fold in a sleeve.
- Use `"fade"` for a tone with **one hard edge and one that dies away** (a hood's inner shadow, light across hair).
  Never fade both edges.
- No drop shadows, no gradients across a whole shape, no outlines.

## Lines
- Only where a pen line belongs: brows, lash line, mouth, a nostril hint, a crease, plait divisions.
- Always tapered (`"w": (thin, thick, thin)`), in a dark warm colour, never black.

## Faces
- Eyes are simple dark ovals (maybe a tiny highlight); placement and spacing carry the character.
- Nose: a small tone shape or a short tapered line. Mouth: a short curved stroke, small and soft.
- Keep features consistent across a set by reusing parts (see SKILL.md), varying hair, clothes, skin tone, ears,
  accessories (glasses, plaits, collars) for identity.

## Finish
- Rendered at 2× and reduced, so edges are clean but not hard-vector-sharp.
- Paper tooth (`"tooth"`, default 2.4) over everything: fine, even, barely visible. 0 for a clean vector look.
- Check at the real display size; tiny details that vanish there should go.
