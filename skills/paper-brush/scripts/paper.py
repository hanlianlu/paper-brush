#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "opencv-python-headless"]
# ///
"""Paper brush: flat cut-paper illustration, drawn from pen paths.

A picture is a short stack of flat shapes, each drawn like a pen-tool path: a few nodes, long arcs between them, and
corners that stay crisp. Depth comes from a second tone laid on as clean shapes, some with one hard edge and one that
fades, never from outlines or blur. A fine, even paper tooth goes over the finished picture.

A drawing is a dict:

    {"frame": (x0, y0, size) | (x0, y0, w, h),   # the part of your authoring grid that becomes the picture
     "out": 1200,                                # output width in px (height follows the frame's aspect)
     "paper": "#F7ECE0",                         # ground colour (default warm cream)
     "tooth": 2.4,                               # paper grain strength, 0 = none
     "seed": 1,                                  # grain seed
     "mirror": False,                            # flip left-right at the end
     "eyes": ((x, y), (x, y)),                   # optional, for faces: sets the head's own axes (see "head" and "part")
     "layers": [...]}                            # painted in order

A layer is one of

    {"name": "hair", "path": NODES, "fill": "#3A2A20"}                    a shape (its coverage is remembered as "hair")
    {"path": NODES, "fill": "#2A1E18", "clip": "hair"}                    a second tone, kept inside another shape (or a list of them)
    {... "fade": ((x, y), (x, y))}                                        full strength at the first point, gone at the second
    {... "soft": 12}                                                      a breath of colour (blush, glow), edges blurred by this much
    {... "alpha": 0.6}                                                    partial strength
    {"stroke": NODES, "w": (2, 7, 1), "color": "#8A4B3A"}                 a tapered line: widths spread along it (or at "at": (0, .3, 1))
    {"part": ("set", "eye_l"), "fill": "#2A1A14", "scale": 1.1}           a reusable face part from parts.py next to the drawings file
                                                                          (also "turn" degrees, "shift" / "at" in head units)
    {"head": True, "stroke": NODES, ...}                                  nodes on the head's axes: x along the eye line, y down the
                                                                          face, unit = half the eye distance (path works the same)

NODES is a list of (x, y) for a point the curve flows through and (x, y, "c") for a corner. "path" may also be a list
of such lists (several pieces, one layer); pieces listed under "holes" are cut out. Several layers with the same
"name" add up into one mask.

    uv run paper.py DRAWINGS.py OUT_DIR [name ...]      # draws DRAWINGS.py's DRAWINGS dict (or KIDS) to OUT_DIR/<name>.png
    uv run paper.py nodes MASK.png [scale]              # prints pen nodes for the white shape(s) in a mask: a starting point
"""
import importlib.util
import sys
from pathlib import Path

import cv2
import numpy as np

OUT = 1200       # default output width
SS = 2           # drawn at twice the size, then reduced, so every edge is clean
PAPER = (247, 236, 224)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def flow(nodes, closed=True, per=20):
    """The curve through a list of nodes: cubic segments, tangent-continuous at plain nodes, broken at corners."""
    P = np.array([n[:2] for n in nodes], float)
    corner = [len(n) > 2 and n[2] == "c" for n in nodes]
    n = len(P)
    if n < 3:
        return P
    idx = lambda i: i % n if closed else min(max(i, 0), n - 1)
    def tangent(i, towards):
        """Unit direction of travel at node i, for the segment on the side of `towards` (+1 leaving, -1 arriving)."""
        a, b, c = P[idx(i - 1)], P[i], P[idx(i + 1)]
        end = not closed and (i == 0 or i == n - 1)
        if corner[i] or end:
            v = (c - b) if (towards > 0 and not (end and i == n - 1)) else (b - a)
        else:
            d0, d1 = np.linalg.norm(b - a) + 1e-9, np.linalg.norm(c - b) + 1e-9
            v = (b - a) / d0 * d1 + (c - b) / d1 * d0             # leans on the shorter neighbour less
        return v / (np.linalg.norm(v) + 1e-9)
    out = []
    for i in range(n if closed else n - 1):
        j = idx(i + 1)
        a, b = P[i], P[j]
        d = np.linalg.norm(b - a)
        c1, c2 = a + tangent(i, +1) * d / 3, b - tangent(j, -1) * d / 3
        t = np.linspace(0, 1, per, endpoint=False)[:, None]
        out.append((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * c1 + 3 * (1 - t) * t ** 2 * c2 + t ** 3 * b)
    if not closed:
        out.append(P[-1:])
    return np.vstack(out)


def taper(img, pts, color, widths, at=None):
    """A line whose width changes along it (widths at the positions `at`, 0..1), with round ends."""
    pts = np.asarray(pts, float)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    t = np.concatenate([[0], np.cumsum(seg)]) / max(seg.sum(), 1e-9)
    at = np.linspace(0, 1, len(widths)) if at is None else at
    w = np.interp(t, at, widths)
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        d = b - a
        nrm = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-9)
        quad = np.array([a + nrm * w[i] / 2, b + nrm * w[i + 1] / 2, b - nrm * w[i + 1] / 2, a - nrm * w[i] / 2])
        cv2.fillConvexPoly(img, np.round(quad * 16).astype(np.int32), color, cv2.LINE_AA, 4)
        cv2.circle(img, (int(a[0] * 16), int(a[1] * 16)), int(max(w[i], 0.5) * 8), color, -1, cv2.LINE_AA, 4)
    cv2.circle(img, (int(pts[-1][0] * 16), int(pts[-1][1] * 16)), int(max(w[-1], 0.5) * 8), color, -1, cv2.LINE_AA, 4)


class Sheet:
    """The picture being made: grid points go in, paint lands on a canvas twice the final size."""

    def __init__(self, frame, out=OUT, paper=PAPER, parts=None):
        x0, y0, *wh = frame
        fw, fh = (wh[0], wh[0]) if len(wh) == 1 else wh
        self.W, self.H = int(out), int(round(out * fh / fw))
        self.k = self.W * SS / fw                                 # grid unit -> canvas pixel
        self.o = np.array([x0, y0], float)
        self.nw, self.nh = self.W * SS, self.H * SS
        self.canvas = np.empty((self.nh, self.nw, 3), np.float32)
        self.canvas[:] = paper
        self.masks = {}
        self.parts = parts
        self.eyes = None

    def to(self, pts):
        return (np.asarray(pts, float) - self.o) * self.k

    def mask(self, path, holes=()):
        m = np.zeros((self.nh, self.nw), np.uint8)
        pieces = path if isinstance(path[0], list) else [path]
        for piece in pieces:
            cv2.fillPoly(m, [np.round(self.to(flow(piece)) * 16).astype(np.int32)], 255, cv2.LINE_AA, 4)
        for piece in holes:
            cv2.fillPoly(m, [np.round(self.to(flow(piece)) * 16).astype(np.int32)], 0, cv2.LINE_AA, 4)
        return m.astype(np.float32) / 255

    def lay(self, alpha, color):
        a = alpha[..., None]
        self.canvas = self.canvas * (1 - a) + np.array(color, np.float32) * a

    def axes(self):
        el, er = (np.array(v, float) for v in self.eyes)
        c, d = (el + er) / 2, er - el
        u = np.linalg.norm(d) / 2
        return c, u, d / (2 * u), np.array([-d[1], d[0]]) / (2 * u)

    def part(self, layer):
        """A face part from parts.py set on this head: same place on the head's axes, then scaled about its own
        middle and nudged (both in units of half the eye distance)."""
        src, name = layer["part"]
        nodes = self.parts[src][name]["nodes"]
        P = np.array([n[:2] for n in nodes], float)
        kinds = [tuple(n[2:]) for n in nodes]
        mid = P.mean(0)
        sx, sy = layer.get("scale", (1, 1)) if not np.isscalar(layer.get("scale", 1)) else (layer.get("scale", 1),) * 2
        r = np.radians(layer.get("turn", 0))
        Q = (P - mid) * (sx, sy)
        Q = Q @ np.array([[np.cos(r), np.sin(r)], [-np.sin(r), np.cos(r)]]) + mid + np.array(layer.get("shift", (0, 0)))
        if layer.get("at"):
            Q = Q - mid + np.array(layer["at"])
        c, u, ax, ay = self.axes()
        pts = c + u * (Q[:, :1] * ax + Q[:, 1:] * ay)
        return [(p[0], p[1]) + k for p, k in zip(pts, kinds)]

    def on_head(self, pts):
        """Points given on the head's axes -> grid."""
        c, u, ax, ay = self.axes()
        return [tuple(c + u * (p[0] * ax + p[1] * ay)) + tuple(p[2:]) for p in pts]

    def paint(self, layer):
        if "part" in layer:
            layer = dict(layer, path=self.part(layer))
        if layer.get("head"):                                     # nodes written on the head's axes
            key = "stroke" if "stroke" in layer else "path"
            layer = dict(layer, **{key: self.on_head(layer[key])})
            if "w" in layer:
                u = self.axes()[1]
                w = layer["w"]
                layer["w"] = tuple(v * u for v in ((w,) if np.isscalar(w) else w))
        if "stroke" in layer:
            m = np.zeros((self.nh, self.nw), np.uint8)
            w = layer.get("w", 4)
            w = (w,) if np.isscalar(w) else w
            taper(m, self.to(flow(layer["stroke"], closed=False)), 255, [v * self.k for v in w], layer.get("at"))
            a = m.astype(np.float32) / 255
            color = layer["color"]
        else:
            a = self.mask(layer["path"], layer.get("holes", ()))
            color = layer["fill"]
            if layer.get("soft"):
                a = cv2.GaussianBlur(a, (0, 0), layer["soft"] * self.k)
            if layer.get("fade"):                                 # one hard edge, one that dies away
                p, q = (self.to(v) for v in layer["fade"])
                yy, xx = np.mgrid[0:self.nh, 0:self.nw].astype(np.float32)
                t = ((xx - p[0]) * (q[0] - p[0]) + (yy - p[1]) * (q[1] - p[1])) / (np.sum((q - p) ** 2) + 1e-9)
                t = np.clip(t, 0, 1)
                a = a * (1 - t * t * (3 - 2 * t))
        clip = layer.get("clip")
        for name in ([clip] if isinstance(clip, str) else clip or []):
            a = a * self.masks[name]
        a = a * layer.get("alpha", 1.0)
        if layer.get("name"):
            self.masks[layer["name"]] = a if layer["name"] not in self.masks else np.maximum(self.masks[layer["name"]], a)
        self.lay(a, hexrgb(color))

    def finish(self, seed=1, tooth=2.4):
        img = cv2.resize(np.clip(self.canvas, 0, 255), (self.W, self.H), interpolation=cv2.INTER_AREA)
        if tooth:
            rng = np.random.default_rng(seed)                    # paper tooth: fine, even, barely there
            g = cv2.GaussianBlur(rng.normal(0, 1, (self.H, self.W)).astype(np.float32), (0, 0), 0.6)
            img = img + (g / g.std() * tooth)[..., None]
        return np.clip(img, 0, 255).astype(np.uint8)[..., ::-1]


def draw(d, parts=None):
    """One drawing dict -> BGR uint8 image (write it with cv2.imwrite)."""
    paper = hexrgb(d["paper"]) if isinstance(d.get("paper"), str) else d.get("paper", PAPER)
    sheet = Sheet(d["frame"], d.get("out", OUT), paper, parts)
    sheet.eyes = d.get("eyes")
    for layer in d["layers"]:
        sheet.paint(layer)
    img = sheet.finish(d.get("seed", 1), d.get("tooth", 2.4))
    return np.ascontiguousarray(img[:, ::-1]) if d.get("mirror") else img


# ---- from a flat shape to nodes: the starting point for a drawing

def nodes_of(mask, corner_deg=128, span=9, eps=2.2, scale=1.0):
    """The outline of a mask as pen nodes: corners where the edge really turns, and between them only as many
    points as the arc needs. Coordinates are divided by `scale` (mask pixel -> grid)."""
    cs, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in sorted(cs, key=cv2.contourArea, reverse=True):
        c = c[:, 0, :].astype(float)
        if len(c) < 4 * span or cv2.contourArea(c.astype(np.float32)) < 60:
            continue
        sm = cv2.GaussianBlur(np.vstack([c[-span:], c, c[:span]]).astype(np.float32), (1, 5), 0)[span:-span]
        a, b = np.roll(sm, span, axis=0) - sm, np.roll(sm, -span, axis=0) - sm
        ang = np.degrees(np.arccos(np.clip(np.sum(a * b, 1) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1) + 1e-9), -1, 1)))
        corners = [i for i in range(len(c)) if ang[i] < corner_deg and ang[i] == ang[np.arange(i - span, i + span + 1) % len(c)].min()]
        corners = sorted(set(corners))
        plain = not corners
        if plain:
            corners = [0]
        nodes = []
        for u, v in zip(corners, corners[1:] + [corners[0] + len(c)]):
            run = c[np.arange(u, v + 1) % len(c)]
            keep = cv2.approxPolyDP(run.astype(np.float32)[:, None, :], eps, False)[:, 0, :]
            nodes.append((run[0][0], run[0][1]) if plain else (run[0][0], run[0][1], "c"))
            nodes += [(p[0], p[1]) for p in keep[1:-1]]
        out.append([(round(n[0] / scale, 1), round(n[1] / scale, 1)) + tuple(n[2:]) for n in nodes])
    return out


def load(path):
    """Import a drawings file (its folder goes on sys.path, so a parts.py beside it is found)."""
    path = Path(path).resolve()
    sys.path.insert(0, str(Path(__file__).resolve().parent))      # so drawings can `from paper import flow`
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    try:
        parts = __import__("parts").PARTS
    except ImportError:
        parts = None
    return getattr(mod, "DRAWINGS", None) or getattr(mod, "KIDS"), parts


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "nodes":
        m = cv2.imread(a[1], cv2.IMREAD_GRAYSCALE) > 127
        for piece in nodes_of(m, scale=float(a[2]) if len(a) > 2 else 1.0):
            print(piece)
    elif len(a) >= 2:
        drawings, parts = load(a[0])
        dst = Path(a[1])
        dst.mkdir(parents=True, exist_ok=True)
        for name in a[2:] or drawings:
            cv2.imwrite(str(dst / f"{name}.png"), draw(drawings[name], parts))
            print("drew", dst / f"{name}.png")
    else:
        sys.exit(__doc__)
