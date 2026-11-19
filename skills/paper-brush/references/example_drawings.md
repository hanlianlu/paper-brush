# Example drawings

A minimal drawings file to start from: a head-and-shoulders figure on a 600-unit grid, and a wide banner. Save the
block below as `example_drawings.py` next to `paper.py` (see `engine.md`) and run
`python3 paper.py example_drawings.py out/`. The README's two small examples were drawn from it.

```python
"""A minimal paper-brush drawings file: a head-and-shoulders figure on a 600-unit grid, plus a wide banner.

    python3 paper.py example_drawings.py out/
"""
C = "c"
SKIN, SKIN2, BLUSH = "#E9B48F", "#D6966F", "#E58B78"
HAIR, HAIR2 = "#3B2A22", "#2A1D17"
COAT, COAT2 = "#5E7F63", "#4B6A50"
INK = "#2A1A14"

DRAWINGS = {
    "example": {
        "frame": (0, 0, 600), "out": 1200, "seed": 1,
        "eyes": ((255, 300), (345, 300)),
        "layers": [
            {"name": "hairback", "fill": HAIR, "path": [(150, 280), (180, 150), (300, 100), (420, 150), (450, 280), (440, 420, C), (160, 420, C)]},
            {"name": "body", "fill": COAT, "path": [(120, 600, C), (150, 480), (230, 440, C), (370, 440, C), (450, 480), (480, 600, C)]},
            {"clip": "body", "fill": COAT2, "path": [(120, 600, C), (150, 480), (230, 440, C), (250, 600, C)], "fade": ((200, 520), (280, 520))},
            {"name": "neck", "fill": SKIN, "path": [(265, 380, C), (335, 380, C), (340, 460), (300, 475), (260, 460)]},
            {"clip": "neck", "fill": SKIN2, "path": [(250, 380, C), (350, 380, C), (345, 420), (300, 435), (255, 420)]},
            {"name": "face", "fill": SKIN, "path": [(205, 280), (225, 200), (300, 175), (375, 200), (395, 280), (380, 360), (300, 410, C), (220, 360)]},
            {"fill": BLUSH, "path": [(330, 335), (360, 325), (375, 345), (350, 360)], "soft": 8, "alpha": 0.5},
            {"name": "fringe", "fill": HAIR, "path": [(190, 300, C), (200, 190), (300, 140), (410, 190), (410, 300, C), (380, 225), (330, 245, C), (290, 215), (240, 250, C), (215, 230)]},
            {"clip": "fringe", "fill": HAIR2, "path": [(190, 300), (200, 190), (300, 140), (260, 200), (220, 260)], "fade": ((220, 220), (300, 200))},
            {"head": True, "path": [(-1.0, -0.3), (-0.8, 0), (-1.0, 0.3), (-1.2, 0)], "fill": INK},
            {"head": True, "path": [(1.0, -0.3), (1.2, 0), (1.0, 0.3), (0.8, 0)], "fill": INK},
            {"head": True, "stroke": [(-1.5, -0.75), (-1.0, -0.9), (-0.55, -0.8)], "w": (0.05, 0.14, 0.05), "color": HAIR2},
            {"head": True, "stroke": [(0.55, -0.8), (1.0, -0.9), (1.5, -0.75)], "w": (0.05, 0.14, 0.05), "color": HAIR2},
            {"head": True, "stroke": [(-0.35, 1.45), (0, 1.6), (0.35, 1.45)], "w": (0.04, 0.11, 0.04), "color": "#B9573E"},
        ],
    },
    "banner": {
        "frame": (0, 0, 800, 300), "out": 1600, "paper": "#F3E6D3", "seed": 2,
        "layers": [
            {"name": "hill", "fill": "#9DB28E", "path": [(0, 300, C), (0, 210), (200, 160), (420, 200), (620, 150), (800, 190, C), (800, 300, C)]},
            {"clip": "hill", "fill": "#86A07A", "path": [(0, 300, C), (0, 240), (300, 220), (520, 260), (800, 230, C), (800, 300, C)], "fade": ((400, 300), (400, 220))},
            {"fill": "#E9A86B", "path": [(600, 60), (640, 40), (680, 60), (680, 100), (640, 120), (600, 100)]},
        ],
    },
}
```
