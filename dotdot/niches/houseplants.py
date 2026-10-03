"""Houseplants & Succulents niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "houseplants"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ---------------------------------------------------------------- small shapes

def earc(cx, cy, rx, ry, a0, a1, n=40, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    out = []
    for i in range(n + 1):
        t = a0 + (a1 - a0) * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def stone(cx, cy, rx, ry):
    return [(cx + rx * math.cos(t) * (1 + 0.08 * math.sin(3 * t + cx)), cy + ry * math.sin(t) * (1 + 0.08 * math.cos(2 * t + cy)))
            for t in [TAU * i / 30 for i in range(31)]]


# ---------------------------------------------------------------- occlusion

def _bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def _inside(pt, pg):
    x, y = pt
    ins = False
    j = len(pg) - 1
    for i in range(len(pg)):
        xi, yi = pg[i]
        xj, yj = pg[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            ins = not ins
        j = i
    return ins


def _dense(pts, step=0.04):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        k = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k) for i in range(1, k + 1)]
    return out


def _plen(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def occlude(strokes, covers):
    """Hide the parts of `strokes` that fall inside any closed cover polygon."""
    boxes = [(_bbox(c), c) for c in covers]
    out = []
    for s in strokes:
        if len(s) < 2:
            continue
        bx = _bbox(s)
        near = [c for b, c in boxes if not (b[2] < bx[0] or b[0] > bx[2] or b[3] < bx[1] or b[1] > bx[3])]
        if not near:
            out.append(s)
            continue
        runs, run = [], []
        for p in _dense(s):
            if any(_inside(p, c) for c in near):
                if len(run) > 1:
                    runs.append(run)
                run = []
            else:
                run.append(p)
        if len(run) > 1:
            runs.append(run)
        closed = math.dist(s[0], s[-1]) < 1e-6
        if closed and len(runs) > 1 and runs[0][0] == s[0] and math.dist(runs[-1][-1], s[-1]) < 1e-6:
            runs[0] = runs[-1] + runs[0][1:]
            runs.pop()
        out += [r for r in runs if _plen(r) > 0.12]
    return out


class Scene:
    """Strokes drawn back to front: each new part may hide what is behind it."""

    def __init__(self):
        self.s = []

    def add(self, strokes, cover=None):
        if cover:
            covers = cover if isinstance(cover[0][0], (list, tuple)) else [cover]
            self.s = occlude(self.s, covers)
        self.s += [list(x) for x in strokes if len(x) > 1]
        return self

    def solid(self, outline, extra=()):
        """Closed outline that hides what is behind it, plus inner detail."""
        return self.add([outline] + list(extra), outline)


def chaikin(pts, iters=3, closed=True):
    for _ in range(iters):
        out = []
        n = len(pts) if closed else len(pts) - 1
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            out += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]), (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        pts = out if closed else [pts[0]] + out + [pts[-1]]
    return pts + [pts[0]] if closed else pts


# ---------------------------------------------------------------- leaves

SIDES = {
    "ovate": lambda: cubic((0, 0), (0.55, 0.12), (0.5, 0.75), (0, 1), 26),
    "heart": lambda: cubic((0, 0), (0.45, -0.3), (0.75, 0.45), (0, 1), 30),
    "lance": lambda: cubic((0, 0), (0.45, 0.15), (0.35, 0.7), (0, 1), 26),
    "sword": lambda: cubic((0, 0), (0.5, 0.1), (0.5, 0.8), (0, 1), 30),
    "obovate": lambda: cubic((0, 0), (0.25, 0.05), (0.7, 0.8), (0, 1), 26),
    "round": lambda: cubic((0, 0), (0.7, -0.05), (0.7, 1.05), (0, 1), 26),
    "arrow": lambda: chain(quad((0, 0), (0.12, -0.1), (0.38, -0.42), 8), cubic((0.38, -0.42), (0.65, -0.1), (0.55, 0.5), (0, 1), 26)),
    "spoon": lambda: chain(cubic((0, 0), (0.35, 0.05), (0.55, 0.7), (0.15, 0.92), 20), [(0, 1.0)]),
}


def place(pts, base, ang, L, W):
    a = math.radians(ang)
    c, s = math.cos(a), math.sin(a)
    return [(base[0] + y * L * c - x * W * s, base[1] + y * L * s + x * W * c) for x, y in pts]


def outline_of(side):
    left = [(-x, y) for x, y in side]
    return side + left[::-1][1:]


def half_width(side, y):
    best = min(side, key=lambda p: abs(p[1] - y))
    return abs(best[0])


def leaf(kind, base, ang, L, W, rib=0.85, veins=0, vlen=0.75):
    """Returns (strokes, outline) for a leaf whose stalk end is `base`."""
    side = SIDES[kind]()
    out = place(outline_of(side), base, ang, L, W)
    parts = [out]
    if rib:
        parts.append(place([(0, 0.02), (0, rib)], base, ang, L, W))
    for k in range(veins):
        y = 0.15 + 0.65 * (k + 0.5) / veins
        for sg in (1, -1):
            parts.append(place([(0, y), (sg * half_width(side, y + 0.12) * vlen, y + 0.13)], base, ang, L, W))
    return parts, out


def monstera_leaf(base, ang, L, W, slits=(11, 17, 23, 29)):
    side = cubic((0, 0), (0.45, -0.3), (0.8, 0.45), (0, 1), 36)
    right = []
    for i, p in enumerate(side):
        if i in slits:
            right.append((p[0] * 0.28, p[1] - 0.07))
        else:
            right.append(p)
    left = [(-x, y) for x, y in right]
    out = place(right + left[::-1][1:], base, ang, L, W)
    rib = place([(0, 0.02), (0, 0.8)], base, ang, L, W)
    return [out, rib], out


def tangent(curve, i):
    a = curve[max(0, i - 1)]
    b = curve[min(len(curve) - 1, i + 1)]
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def leaves_along(curve, idxs, L, W, kind="heart", spread=60, first=1, rib=0.8):
    """Leaves alternating along a vine: list of (strokes, outline)."""
    out = []
    sg = first
    for i in idxs:
        i = min(i, len(curve) - 1)
        out.append(leaf(kind, curve[i], tangent(curve, i) + sg * spread, L, W, rib=rib))
        sg = -sg
    return out


def blade(center, w0, w1=0.02):
    """Curved strap leaf (tapering band with a pointed tip)."""
    return tube(center, lambda t: w0 * (1 - t) + w1 * t)


def rosette_top(cx, cy, rings, rot0=0.0):
    """Top view rosette (echeveria): rings = [(count, r_inner, length, width)] outer first."""
    sc = Scene()
    for k, (n, r0, L, W) in enumerate(rings):
        for i in range(n):
            a = rot0 + (i + 0.5 * k) * 360 / n
            b = (cx + r0 * math.cos(math.radians(a)), cy + r0 * math.sin(math.radians(a)))
            parts, o = leaf("spoon", b, a, L, W, rib=0)
            sc.add(parts, o)
    return sc


# ---------------------------------------------------------------- pots

def pot_terra(cx, top, w, h, rim=0.38):
    r = rect(cx - w / 2, top - rim, cx + w / 2, top)
    b = [(cx - w / 2 + 0.1, top - rim), (cx - w * 0.36, top - h), (cx + w * 0.36, top - h), (cx + w / 2 - 0.1, top - rim)]
    return [r, b], [r, b + [b[0]]]


def pot_round(cx, top, w, h, r=0.3):
    body = rrect(cx - w / 2, top - h, cx + w / 2, top, r)
    return [body, [(cx - w / 2 + 0.02, top - 0.32), (cx + w / 2 - 0.02, top - 0.32)]], [body]


def pot_bowl(cx, top, w, h):
    rim = rect(cx - w / 2, top - 0.25, cx + w / 2, top)
    bowl = chain([(cx - w / 2 + 0.05, top - 0.25)], cubic((cx - w / 2 + 0.05, top - h * 0.8), (cx - w * 0.3, top - h), (cx + w * 0.3, top - h), (cx + w / 2 - 0.05, top - h * 0.8), 24)[1:-1],
                 [(cx + w / 2 - 0.05, top - 0.25)])
    return [rim, bowl], [rim, bowl + [bowl[0]]]


def pot_belly(cx, top, w, h):
    body = chain([(cx - w * 0.4, top)], cubic((cx - w * 0.4, top), (cx - w * 0.65, top - h * 0.5), (cx - w * 0.45, top - h), (cx, top - h), 18)[1:],
                 cubic((cx, top - h), (cx + w * 0.45, top - h), (cx + w * 0.65, top - h * 0.5), (cx + w * 0.4, top), 18)[1:])
    return [body + [body[0]]], [body + [body[0]]]


def add_pot(sc, pot):
    sc.add(pot[0], pot[1])


def soil(cx, y, w):
    return [quad((cx - w / 2, y), (cx, y + 0.18), (cx + w / 2, y), 10)]


def floor(y=-2.9, x0=-3.4, x1=3.4):
    return [(x0, y), (x1, y)]


# ================================================================ designs

@design("houseplants_monstera", T)
def monstera(rng):
    sc = Scene()
    specs = [((0.1, 1.2), 95, 1.9, 2.0), ((-0.7, 0.3), 152, 2.2, 2.3), ((0.75, 0.4), 28, 2.2, 2.3)]
    for b, a, L, W in specs:
        sc.add([cubic((0, -1.0), (0, -0.4), (b[0] * 0.6, b[1] - 0.6), b, 16)])
    for b, a, L, W in specs:
        p, o = monstera_leaf(b, a, L, W)
        sc.add(p, o)
    young = blade([(0.3, -1.0), (0.45, -0.3), (0.55, 0.3), (0.5, 0.75)], 0.22)
    sc.add([young], young)
    add_pot(sc, pot_round(0, -0.95, 2.4, 1.9))
    sc.add([floor()])
    return make("Monstera in a Modern Pot", sc.s)


@design("houseplants_fiddle_leaf_fig", T)
def fiddle_leaf_fig(rng):
    sc = Scene()
    trunk = cubic((0, -1.0), (0.1, 0.3), (-0.2, 1.4), (0.05, 2.8), 30)
    sc.add([tube(trunk, lambda t: 0.22 - 0.12 * t)])
    specs = [(6, 155, 1.3), (9, 25, 1.35), (13, 160, 1.25), (16, 20, 1.25), (20, 150, 1.15), (23, 35, 1.1), (27, 120, 1.0), (29, 65, 1.0)]
    for i, a, L in specs:
        p, o = leaf("obovate", trunk[i], a, L, L * 1.0, veins=3, vlen=0.6)
        sc.add(p, o)
    basket = rrect(-1.2, -2.85, 1.2, -0.95, 0.15)
    weave = [[(-1.2, y), (1.2, y)] for y in (-1.35, -1.75, -2.15, -2.55)]
    ticks = []
    for r, (ya, yb) in enumerate([(-0.95, -1.35), (-1.35, -1.75), (-1.75, -2.15), (-2.15, -2.55), (-2.55, -2.85)]):
        ticks += [[(x + (0.2 if r % 2 else 0), ya), (x + (0.2 if r % 2 else 0), yb)] for x in (-0.8, -0.4, 0.0, 0.4, 0.8)]
    sc.add([basket] + weave + ticks, basket)
    sc.add([floor()])
    return make("Fiddle-Leaf Fig Tree", sc.s)


@design("houseplants_snake_plant", T)
def snake_plant(rng):
    sc = Scene()
    specs = [(-0.75, 106, 3.0, 0.62), (0.75, 76, 3.2, 0.62), (-0.3, 96, 3.9, 0.7), (0.3, 86, 3.6, 0.7), (0.0, 91, 2.6, 0.6), (-1.0, 118, 2.1, 0.55), (1.0, 64, 2.3, 0.55)]
    for x, a, L, W in specs:
        p, o = leaf("sword", (x, -1.1), a, L, W, rib=0)
        band = place([(0.12 * math.sin(10 * y), y) for y in [0.12 + 0.7 * i / 30 for i in range(31)]], (x, -1.1), a, L, W)
        sc.add(p + [band], o)
    pot = rect(-1.3, -2.9, 1.3, -1.0)
    pattern = zigzag(-1.3, 1.3, -1.95, 0.3, 4)
    sc.add([pot, pattern, [(-1.3, -1.3), (1.3, -1.3)]], pot)
    sc.add([floor()])
    return make("Snake Plant in a Square Pot", sc.s)


@design("houseplants_pothos_shelf", T)
def pothos_shelf(rng):
    sc = Scene()
    shelf = rect(-3.3, 0.6, 3.3, 0.85)
    brackets = [poly((x, 0.6), (x, -0.4), (x + 0.6 * sg, 0.6), closed=False) for x, sg in [(-2.6, 1), (2.6, -1)]]
    books = [rect(1.2, 0.85, 1.55, 2.3), rect(1.55, 0.85, 1.95, 2.15), poly((1.95, 0.85), (2.3, 0.85), (2.75, 2.0), (2.4, 2.1)), rrect(2.4, 0.85, 3.2, 1.15, 0.05)]
    sc.add([shelf] + brackets + books)
    vines = [cubic((-1.2, 1.9), (-1.9, 1.3), (-2.0, 0.0), (-2.1, -2.6), 50), cubic((-0.4, 1.9), (-0.5, 0.6), (-0.9, -0.6), (-0.7, -2.0), 50),
             cubic((0.3, 1.9), (0.8, 0.9), (0.4, -0.4), (0.5, -1.3), 40)]
    for v, first in zip(vines, (1, -1, 1)):
        sc.add([v])
        for p, o in leaves_along(v, range(6, len(v), 8), 0.6, 0.65, "heart", 55, first):
            sc.add(p, o)
    for b, a in [((-0.9, 2.1), 130), ((-0.2, 2.15), 90), ((0.3, 2.05), 45)]:
        p, o = leaf("heart", b, a, 0.75, 0.8)
        sc.add(p, o)
    add_pot(sc, pot_terra(-0.45, 2.15, 1.7, 1.3))
    return make("Pothos Trailing from a Shelf", sc.s)


@design("houseplants_string_of_pearls", T)
def string_of_pearls(rng):
    sc = Scene()
    hang = [[(-1.3, 0.75), (0, 3.0)], [(1.3, 0.75), (0, 3.0)], circle(0, 3.15, 0.15, 12), [(0, 3.3), (0, 3.6)]]
    sc.add(hang)
    for x, y in [(-0.9, 0.95), (-0.5, 1.05), (-0.1, 1.1), (0.3, 1.08), (0.7, 1.0), (1.05, 0.9), (-0.7, 1.35), (-0.3, 1.42), (0.1, 1.45), (0.5, 1.38), (-0.1, 1.78), (0.3, 1.72)]:
        c = circle(x, y, 0.17, 14)
        sc.add([c], c)
    rim = rrect(-1.45, 0.45, 1.45, 0.78, 0.08)
    bowl = chain([(-1.35, 0.45)], earc(0, 0.45, 1.35, 1.15, math.pi, TAU, 30)[1:-1], [(1.35, 0.45)])
    sc.add([rim, bowl], [rim, bowl + [bowl[0]]])
    strands = [((-1.3, 0.6), (-1.9, 0.0), -2.6), ((-0.8, 0.5), (-1.1, -0.6), -2.9), ((-0.25, 0.4), (-0.3, -0.9), -1.9),
               ((0.3, 0.4), (0.45, -0.8), -2.4), ((0.85, 0.5), (1.2, -0.4), -3.0), ((1.35, 0.6), (2.0, 0.0), -2.2)]
    for (x0, y0), (cx, cy), yend in strands:
        path = cubic((x0, y0), (cx, cy + 0.6), (cx, cy - 0.3), (cx + 0.15 * math.copysign(1, cx), yend), 120)
        beads, last = [], None
        for p in path:
            if last is None or math.dist(p, last) >= 0.4:
                beads.append(p)
                last = p
        for i, (bx, by) in enumerate(beads):
            c = circle(bx, by, 0.15, 14)
            sc.add([c], c)
            if i + 1 < len(beads):
                nx, ny = beads[i + 1]
                d = math.dist((bx, by), (nx, ny))
                ux, uy = (nx - bx) / d, (ny - by) / d
                sc.add([[(bx + 0.15 * ux, by + 0.15 * uy), (nx - 0.15 * ux, ny - 0.15 * uy)]])
    return make("String of Pearls in a Hanging Bowl", sc.s)


@design("houseplants_macrame_hanger", T)
def macrame_hanger(rng):
    sc = Scene()
    for x0, x1, y1 in [(-0.9, -1.9, -1.6), (0.9, 1.9, -2.2)]:
        v = cubic((x0, 0.35), (x0 * 1.6, 0.2), (x1, -0.6), (x1, y1), 30)
        sc.add([v])
        for p, o in leaves_along(v, range(8, 31, 7), 0.55, 0.6, "heart", 55):
            sc.add(p, o)
    for b, a in [((-0.5, 0.4), 145), ((0.5, 0.4), 35), ((0.0, 0.5), 92), ((-0.85, 0.3), 185), ((0.85, 0.3), -5)]:
        p, o = leaf("heart", b, a, 0.85, 0.85)
        sc.add(p, o)
    pot = chain([(-1.1, 0.35)],
                cubic((-1.1, 0.35), (-1.25, -0.6), (-0.8, -1.35), (0, -1.35), 16)[1:], cubic((0, -1.35), (0.8, -1.35), (1.25, -0.6), (1.1, 0.35), 16)[1:])
    sc.add([pot + [pot[0]]], pot + [pot[0]])
    ring = [circle(0, 3.0, 0.25, 20)]
    knot_top = rrect(-0.2, 2.2, 0.2, 2.65, 0.08)
    cords = [[(-0.12, 2.2), (-1.2, 1.2)], [(-0.05, 2.2), (-0.4, 1.2)], [(0.05, 2.2), (0.4, 1.2)], [(0.12, 2.2), (1.2, 1.2)],
             [(-0.1, 2.65), (-0.1, 2.78)], [(0.1, 2.65), (0.1, 2.78)]]
    knots = [circle(x, 1.1, 0.12, 10) for x in (-1.2, -0.4, 0.4, 1.2)]
    net = [[(-1.2, 1.0), (-1.25, 0.0)], [(-1.25, 0.0), (-0.8, -1.0)], [(-0.4, 1.0), (-0.85, 0.0)],
           [(-0.4, 1.0), (0.0, 0.0)], [(0.4, 1.0), (0.0, 0.0)], [(0.4, 1.0), (0.85, 0.0)], [(1.2, 1.0), (1.25, 0.0)], [(1.25, 0.0), (0.8, -1.0)],
           [(-0.85, 0.0), (-0.8, -1.0)], [(0.85, 0.0), (0.8, -1.0)], [(0.0, 0.0), (-0.3, -1.25)], [(0.0, 0.0), (0.3, -1.25)],
           [(-0.8, -1.0), (-0.15, -1.75)], [(0.8, -1.0), (0.15, -1.75)], [(-0.3, -1.25), (-0.05, -1.75)], [(0.3, -1.25), (0.05, -1.75)]]
    mknots = [circle(x, y, 0.1, 8) for x, y in [(-1.25, 0.0), (-0.85, 0.0), (0.0, 0.0), (0.85, 0.0), (1.25, 0.0)]]
    gather = rrect(-0.25, -2.25, 0.25, -1.75, 0.1)
    tassel = [[(x * 0.4, -2.25), (x, -3.2)] for x in (-0.5, -0.25, 0.0, 0.25, 0.5)]
    sc.add(ring + [knot_top, gather] + cords + knots + net + mknots + tassel)
    return make("Macrame Plant Hanger", sc.s)


@design("houseplants_aloe_vera", T)
def aloe_vera(rng):
    sc = Scene()
    specs = [(170, 2.3, 1.2), (12, 2.3, 1.2), (150, 2.6, 2.2), (32, 2.6, 2.2), (118, 3.0, 3.0), (64, 3.0, 3.0), (95, 3.1, 3.6)]
    for a, L, h in specs:
        r = math.radians(a)
        p0 = (0.25 * math.cos(r), -1.0)
        p3 = (p0[0] + L * math.cos(r), -1.0 + h * 0.95)
        cen = cubic(p0, (p0[0] + 0.3 * math.cos(r), -0.2), (p3[0] - 0.2 * math.cos(r), p3[1] - 0.6), p3, 30)
        b = blade(cen, 0.6)
        spots = [ellipse(cen[i][0], cen[i][1], 0.08, 0.05, 8) for i in (9, 15, 21)]
        sc.add([b], b)
        sc.add([s for s in spots])
    add_pot(sc, pot_terra(0, -0.85, 2.4, 2.0))
    sc.add([floor()])
    return make("Aloe Vera in a Clay Pot", sc.s)


@design("houseplants_echeveria_top", T)
def echeveria_top(rng):
    sc = Scene()
    sc.add([circle(0, 0, 3.0, 120), circle(0, 0, 2.65, 110)])
    ros = rosette_top(0, 0, [(10, 0.9, 1.8, 1.3), (8, 0.55, 1.3, 1.1), (6, 0.25, 0.9, 0.8), (4, 0.05, 0.45, 0.5)], 10)
    sc.add(ros.s, [circle(0, 0, 2.5, 60)])
    return make("Echeveria Rosette from Above", sc.s)


@design("houseplants_jade_plant", T)
def jade_plant(rng):
    sc = Scene()
    trunk = [tube([(0, -1.2), (0.05, -0.3), (-0.1, 0.5)], lambda t: 0.4 - 0.15 * t)]
    branches = [tube([(-0.1, 0.4), (-0.8, 1.2), (-1.4, 1.6)], 0.2), tube([(-0.1, 0.4), (0.6, 1.0), (1.3, 1.5)], 0.2),
                tube([(-0.05, 0.4), (0.0, 1.4), (0.2, 2.2)], 0.18), tube([(0.0, -0.2), (0.9, 0.3), (1.6, 0.4)], 0.18)]
    sc.add(trunk + branches)
    tips = [(-1.4, 1.6), (1.3, 1.5), (0.2, 2.2), (1.6, 0.4), (-0.8, 1.2), (0.6, 1.0)]
    for tx, ty in tips:
        for a in (40, 90, 140, 0, 180):
            e = ellipse(tx + 0.42 * math.cos(math.radians(a)), ty + 0.42 * math.sin(math.radians(a)), 0.22, 0.34, 20, rot=math.radians(a - 90))
            sc.add([e], e)
    add_pot(sc, pot_bowl(0, -0.9, 3.4, 1.7))
    sc.add([floor(-2.65)])
    return make("Jade Plant in a Bowl", sc.s)


@design("houseplants_haworthia", T)
def haworthia(rng):
    sc = Scene()
    specs = [(150, 1.6), (30, 1.6), (130, 2.0), (50, 2.0), (110, 2.3), (70, 2.3), (90, 2.5), (165, 1.2), (15, 1.2)]
    for a, L in specs:
        r = math.radians(a)
        base = (0.2 * math.cos(r), -0.6)
        p, o = leaf("lance", base, a, L, 0.75, rib=0)
        stripes = []
        for t in (0.3, 0.5, 0.7):
            hw = 0.17 * (1 - t) + 0.05
            stripes.append(place([(-hw * 2.2, t), (hw * 2.2, t + 0.03)], base, a, L, 0.75))
        sc.add(p + stripes, o)
    pot = rect(-1.3, -2.5, 1.3, -0.5)
    deco = [poly((-1.3, -1.2), (-0.65, -0.7), (0.0, -1.2), (0.65, -0.7), (1.3, -1.2), closed=False),
            poly((-1.3, -1.8), (-0.65, -2.3), (0.0, -1.8), (0.65, -2.3), (1.3, -1.8), closed=False)]
    sc.add([pot] + deco, pot)
    sc.add([floor(-2.5, -2.8, 2.8)])
    return make("Zebra Haworthia", sc.s)


@design("houseplants_barrel_cactus", T)
def barrel_cactus(rng):
    sc = Scene()
    body = ellipse(0, 0.4, 1.9, 1.7, 100)
    ribs = [earc(0, 0.4, 1.9 * f, 1.7, -math.pi / 2, math.pi / 2, 30) for f in (0.3, 0.7)] + \
        [earc(0, 0.4, 1.9 * f, 1.7, math.pi / 2, 1.5 * math.pi, 30) for f in (0.3, 0.7)]
    sc.add([body] + ribs, body)
    for k, (x, y) in enumerate([(-0.75, 2.05), (0.0, 2.25), (0.75, 2.05)]):
        pet = [lens((x, y), (x + 0.5 * math.cos(math.radians(a)), y + 0.5 * math.sin(math.radians(a))), 0.3) for a in (30, 70, 110, 150)]
        sc.add(pet, None)
        c = circle(x, y, 0.15, 10)
        sc.add([c], c)
    add_pot(sc, pot_terra(0, -1.1, 3.0, 1.7))
    sc.add([floor()])
    hints = [eye(x * 1.9 * f, 0.4 + 1.7 * y, 0.07) for f in (0.3, 0.7) for x, y in [(1, 0.5), (1, 0.0), (1, -0.5), (-1, 0.5), (-1, 0.0), (-1, -0.5)]]
    return make("Golden Barrel Cactus with Flowers", sc.s, hints)


@design("houseplants_saguaro_pot", T)
def saguaro_pot(rng):
    sc = Scene()
    main = chain([(-0.5, -1.0), (-0.5, 2.2)], arc(0, 2.2, 0.5, math.pi, 0, 14), [(0.5, -1.0)])
    arm_l = chain([(-0.5, 0.0), (-1.3, 0.0)], arc(-1.3, 0.4, 0.4, 1.5 * math.pi, math.pi, 8), [(-1.7, 1.4)], arc(-1.4, 1.4, 0.3, math.pi, 0, 10), [(-1.1, 0.42), (-0.5, 0.42)])
    arm_r = chain([(0.5, 0.6), (1.2, 0.6)], arc(1.2, 1.0, 0.4, -0.5 * math.pi, 0, 8), [(1.6, 1.8)], arc(1.3, 1.8, 0.3, 0, math.pi, 10), [(1.0, 1.0), (0.5, 1.0)])
    sc.add([arm_l, arm_r, [(-1.4, 0.6), (-1.4, 1.4)], [(1.3, 1.1), (1.3, 1.8)]])
    sc.add([main + [main[0]], [(-0.17, -1.0), (-0.17, 2.3)], [(0.17, -1.0), (0.17, 2.3)]], main + [main[0]])
    fl = [lens((0, 2.75), (0.5 * math.cos(math.radians(a)), 2.75 + 0.5 * math.sin(math.radians(a))), 0.3) for a in (20, 60, 100, 140, 180)]
    sc.add(fl)
    c = circle(0, 2.75, 0.15, 10)
    sc.add([c], c)
    add_pot(sc, pot_terra(0, -0.8, 2.6, 1.9))
    sc.add([floor()])
    return make("Potted Saguaro Cactus in Bloom", sc.s)


@design("houseplants_prickly_pear", T)
def prickly_pear(rng):
    sc = Scene()
    pads = [(0, -0.2, 1.0, 1.4, 0), (-1.2, 1.6, 0.75, 1.05, 30), (1.1, 1.7, 0.8, 1.1, -25), (-1.8, 3.0, 0.45, 0.6, 15), (0.5, 3.15, 0.5, 0.65, -10)]
    hints = []
    for cx, cy, rx, ry, rot in pads:
        e = ellipse(cx, cy, rx, ry, 60, rot=math.radians(rot))
        sc.add([e], e)
        for fx, fy in [(0.4, 0.4), (-0.4, 0.2), (0.0, -0.3), (0.35, -0.5), (-0.35, -0.6), (0.0, 0.65)]:
            r = math.radians(rot)
            px, py = fx * rx, fy * ry
            hints.append(eye(cx + px * math.cos(r) - py * math.sin(r), cy + px * math.sin(r) + py * math.cos(r), 0.06))
    fruits = [ellipse(-0.75, 2.75, 0.18, 0.28, 14, rot=0.5), ellipse(1.6, 2.85, 0.18, 0.28, 14, rot=-0.4), ellipse(0.0, 1.35, 0.18, 0.28, 14)]
    for f in fruits:
        sc.add([f], f)
    add_pot(sc, pot_terra(0, -1.5, 2.8, 1.5))
    sc.add([floor()])
    return make("Prickly Pear Cactus with Fruit", sc.s, hints)


@design("houseplants_moon_cactus", T)
def moon_cactus(rng):
    sc = Scene()
    stock = rect(-0.45, -0.6, 0.45, 1.0)
    sc.add([stock, [(0, -0.6), (0, 1.0)]], stock)
    ball = polar(lambda t: 1.1 * (1 + 0.06 * math.cos(8 * t)), cx=0, cy=1.9, n=120)
    ribs = [earc(0, 1.9, 1.1 * f, 1.1, -math.pi / 2, math.pi / 2, 20) for f in (0.35, 0.75)] + [earc(0, 1.9, 1.1 * f, 1.1, math.pi / 2, 1.5 * math.pi, 20) for f in (0.35, 0.75)]
    sc.add([ball] + ribs, ball)
    pot = rect(-1.2, -2.6, 1.2, -0.6)
    peb = [stone(x, -0.75, 0.22, 0.12) for x in (-0.8, 0.75)]
    sc.add([pot, [(-1.2, -0.95), (1.2, -0.95)]] + peb, pot)
    sc.add([floor(-2.6, -2.8, 2.8)])
    return make("Grafted Moon Cactus", sc.s)


@design("houseplants_peace_lily", T)
def peace_lily(rng):
    sc = Scene()
    for b, a, L in [((-0.8, 0.0), 160, 1.9), ((0.8, 0.0), 20, 1.9), ((-0.6, 0.6), 130, 2.0), ((0.6, 0.6), 50, 2.0), ((-0.2, 0.9), 105, 1.8), ((0.3, 0.8), 75, 1.9)]:
        sc.add([quad((0, -0.9), (b[0] * 0.3, b[1] - 0.3), b, 8)])
        p, o = leaf("lance", b, a, L, 0.8, veins=0)
        sc.add(p, o)
    for (x, y), tilt in [((-0.9, 2.3), 15), ((0.9, 2.5), -12), ((0.0, 3.0), 0)]:
        sc.add([quad((0, -0.9), (x * 0.4, y * 0.4), (x, y - 0.1), 10)])
        sp, so = leaf("ovate", (x, y - 0.15), 90 + tilt, 1.1, 0.75, rib=0)
        spad = ellipse(x - 0.05 * math.sin(math.radians(tilt)), y + 0.35, 0.09, 0.3, 12, rot=math.radians(tilt))
        sc.add(sp + [spad], so)
    add_pot(sc, pot_round(0, -0.85, 2.5, 2.0))
    sc.add([floor()])
    return make("Peace Lily in Bloom", sc.s)


def orchid_flower(cx, cy, s):
    sc = Scene()
    for a in (90, 210, 330):
        p, o = leaf("ovate", (cx, cy), a, 0.75 * s, 0.55 * s, rib=0)
        sc.add(p, o)
    for sg in (1, -1):
        c = circle(cx + 0.45 * s * sg, cy + 0.05 * s, 0.45 * s, 30)
        sc.add([c], c)
    lip = chain(cubic((cx - 0.2 * s, cy - 0.05 * s), (cx - 0.3 * s, cy - 0.6 * s), (cx + 0.3 * s, cy - 0.6 * s), (cx + 0.2 * s, cy - 0.05 * s), 12))
    col = circle(cx, cy + 0.05 * s, 0.13 * s, 10)
    sc.add([lip + [lip[0]], col], lip + [lip[0]])
    return sc.s, circle(cx, cy, 0.9 * s, 30)


# dropped: the Garden book has this subject
def phalaenopsis(rng):
    sc = Scene()
    spike = chain(cubic((0.1, -0.9), (0.0, 2.0), (0.6, 3.4), (1.6, 3.3), 30), cubic((1.6, 3.3), (2.6, 3.2), (3.2, 2.4), (3.4, 1.0), 30))
    sc.add([spike, [(0.35, -0.9), (0.35, 1.2)], ellipse(0.22, 0.9, 0.2, 0.08, 10)])
    for (x, y), s, (px, py) in [((0.2, 2.0), 1.0, (0.12, 2.0)), ((1.65, 2.6), 0.95, (1.6, 3.3)), ((3.05, 1.75), 0.9, (3.15, 2.5))]:
        sc.add([[(px, py), (x, y + 0.3)]])
        f, cov = orchid_flower(x, y, s)
        sc.add(f, cov)
    bud = ellipse(3.45, 0.8, 0.18, 0.26, 12)
    sc.add([bud], bud)
    for b, a, L in [((-0.6, -0.8), 172, 1.9), ((0.6, -0.8), 8, 1.9), ((0.0, -0.75), 150, 1.6)]:
        p, o = leaf("ovate", b, a, L, 0.85, rib=0.8)
        sc.add(p, o)
    pot = chain([(-1.25, -0.85)], cubic((-1.25, -0.85), (-1.4, -2.2), (-0.9, -2.85), (0, -2.85), 14)[1:], cubic((0, -2.85), (0.9, -2.85), (1.4, -2.2), (1.25, -0.85), 14)[1:])
    sc.add([pot + [pot[0]], quad((-1.3, -1.6), (0, -1.9), (1.3, -1.6), 12)], pot + [pot[0]])
    sc.add([floor()])
    return make("Phalaenopsis Moth Orchid", sc.s)


# dropped: the Garden book has this subject
def bird_of_paradise(rng):
    sc = Scene()
    specs = [((-1.9, 1.3), 140, 2.1), ((1.9, 1.4), 40, 2.0), ((-0.7, 2.0), 110, 2.2), ((0.8, 2.2), 75, 2.0), ((-2.3, 0.0), 175, 1.6)]
    for b, a, L in specs:
        sc.add([tube([(0, -0.8), (b[0] * 0.5, b[1] * 0.5 - 0.3), b], 0.14)])
    for b, a, L in specs:
        side = cubic((0, 0), (0.5, 0.05), (0.5, 0.9), (0, 1), 30)
        right = list(side)
        for i in (10, 18):
            right[i] = (right[i][0] * 0.55, right[i][1] + 0.03)
        o = place(right + [(-x, y) for x, y in side][::-1][1:], b, a, L, 1.05)
        rib = place([(0, 0.0), (0, 0.95)], b, a, L, 1.05)
        sc.add([o, rib], o)
    pot = poly((-1.3, -0.8), (-1.0, -2.9), (1.0, -2.9), (1.3, -0.8))
    sc.add([pot, [(-1.27, -1.05), (1.27, -1.05)]], pot)
    sc.add([floor()])
    return make("Bird of Paradise Floor Plant", sc.s)


@design("houseplants_rubber_plant", T)
def rubber_plant(rng):
    sc = Scene()
    stem = cubic((0, -1.0), (0.1, 0.5), (-0.1, 1.5), (0.0, 2.7), 30)
    sc.add([tube(stem, 0.16)])
    for i, a, L in [(4, 200, 1.5), (8, -20, 1.5), (13, 165, 1.5), (17, 15, 1.45), (22, 140, 1.3), (25, 40, 1.25)]:
        p, o = leaf("ovate", stem[i], a, L, 1.0, veins=0)
        sc.add(p, o)
    sheath = lens((0.0, 2.6), (0.05, 3.4), 0.18)
    sc.add([sheath], sheath)
    pot = pot_belly(0, -0.85, 2.6, 2.0)
    sc.add(pot[0] + [quad((-1.25, -1.4), (0, -1.6), (1.25, -1.4), 10), quad((-1.25, -2.0), (0, -2.2), (1.25, -2.0), 10)], pot[1])
    sc.add([floor()])
    return make("Rubber Plant", sc.s)


@design("houseplants_zz_plant", T)
def zz_plant(rng):
    sc = Scene()
    stems = [cubic((0, -0.9), (-0.3, 0.5), (-1.6, 1.5), (-2.4, 1.6), 40), cubic((0, -0.9), (0.3, 0.5), (1.6, 1.6), (2.4, 1.9), 40),
             cubic((0, -0.9), (-0.1, 1.0), (-0.6, 2.4), (-0.9, 3.1), 40), cubic((0, -0.9), (0.2, 1.0), (0.7, 2.3), (0.9, 3.0), 40)]
    for st in stems:
        sc.add([st])
        for i in range(8, 41, 6):
            for sg in (1, -1):
                p, o = leaf("ovate", st[min(i, 40)], tangent(st, min(i, 40)) + sg * 45, 0.7, 0.45, rib=0.7)
                sc.add(p, o)
    pot = rect(-1.2, -2.8, 1.2, -0.9)
    sc.add([pot, [(-1.2, -1.2), (1.2, -1.2)]], pot)
    sc.add([floor()])
    return make("Glossy ZZ Plant", sc.s)


@design("houseplants_calathea", T)
def calathea(rng):
    sc = Scene()
    for b, a, L, W in [((-1.4, 0.8), 150, 1.8, 1.3), ((1.4, 0.9), 30, 1.8, 1.3), ((-0.6, 1.4), 115, 1.9, 1.3), ((0.7, 1.5), 68, 1.9, 1.3), ((0.0, 1.0), 92, 1.7, 1.2)]:
        sc.add([quad((0, -0.9), (b[0] * 0.2, b[1] * 0.4), b, 10)])
        side = SIDES["ovate"]()
        o = place(outline_of(side), b, a, L, W)
        rib = place([(0, 0.0), (0, 0.92)], b, a, L, W)
        feather = []
        for k in range(5):
            y = 0.15 + 0.14 * k
            hw = half_width(side, y + 0.12)
            for sg in (1, -1):
                feather.append(place([(0, y), (sg * hw * 0.55, y + 0.1)], b, a, L, W))
        inner = place([(x * 0.72, 0.08 + y * 0.82) for x, y in outline_of(side)], b, a, L, W)
        sc.add([o, rib, inner] + feather, o)
    pot = pot_belly(0, -0.85, 2.6, 2.0)
    sc.add(pot[0] + [quad((-1.25, -1.6), (0, -1.75), (1.25, -1.6), 10)], pot[1])
    sc.add([floor()])
    return make("Calathea with Patterned Leaves", sc.s)


@design("houseplants_spider_plant", T)
def spider_plant(rng):
    sc = Scene()
    sc.add([[(-1.3, 0.6), (0, 3.2)], [(1.3, 0.6), (0, 3.2)], circle(0, 3.35, 0.15, 12)])
    for a, L, h in [(160, 2.2, 0.3), (20, 2.2, 0.3), (135, 2.0, 1.2), (45, 2.0, 1.2), (110, 1.6, 1.8), (70, 1.6, 1.8), (175, 2.4, -1.2), (5, 2.4, -1.2)]:
        r = math.radians(a)
        p0 = (0.2 * math.cos(r), 0.65)
        p3 = (p0[0] + L * math.cos(r), 0.65 + h)
        b = blade(cubic(p0, (p0[0] + 0.6 * math.cos(r), 1.4), (p3[0] - 0.2 * math.cos(r), p3[1] + 0.6), p3, 24), 0.28)
        sc.add([b], b)
    pot = chain([(-1.3, 0.65), (-1.3, -0.3)], arc(-0.8, -0.3, 0.5, math.pi, 1.5 * math.pi, 8), arc(0.8, -0.3, 0.5, 1.5 * math.pi, TAU, 8), [(1.3, 0.65)])
    sc.add([pot + [pot[0]], [(-1.3, 0.35), (1.3, 0.35)]], pot + [pot[0]])
    for x0, x1, y1 in [(-0.8, -1.9, -2.3), (0.9, 2.1, -2.0), (0.1, 0.0, -2.8)]:
        run = cubic((x0, -0.7), (x0, -1.3), (x1, -1.0), (x1, y1), 20)
        sc.add([run])
        for a in (40, 90, 140, 200, -20):
            r = math.radians(a)
            b = blade([(x1, y1), (x1 + 0.4 * math.cos(r), y1 + 0.4 * math.sin(r) + 0.1), (x1 + 0.75 * math.cos(r), y1 + 0.7 * math.sin(r))], 0.16)
            sc.add([b], b)
    return make("Hanging Spider Plant with Babies", sc.s)


@design("houseplants_boston_fern", T)
def boston_fern(rng):
    sc = Scene()
    fronds = [(-1.0, 0.2, -3.0, -1.0), (1.0, 0.2, 3.0, -1.0), (-0.8, 1.8, -2.4, 1.2), (0.8, 1.8, 2.4, 1.3), (0.0, 2.2, 0.2, 3.1)]
    for cx1, cy1, x3, y3 in fronds:
        mid = cubic((cx1 * 0.2, -0.3), (cx1, cy1 + 0.4), (x3 * 0.8, y3 + 0.8), (x3, y3), 40)
        sc.add([mid])
        for i in range(5, 38, 4):
            ang = tangent(mid, i)
            s = 0.75 * (1 - 0.55 * i / 40)
            for sg in (1, -1):
                p, o = leaf("lance", mid[i], ang + sg * 60, s, 0.32, rib=0)
                sc.add(p, o)
    urn = chain([(-1.3, -0.3)], cubic((-1.3, -0.3), (-1.4, -1.4), (-0.4, -1.6), (-0.3, -1.9), 14)[1:], [(-0.3, -2.3), (-0.8, -2.5), (-0.8, -2.8), (0.8, -2.8), (0.8, -2.5), (0.3, -2.3), (0.3, -1.9)],
                cubic((0.3, -1.9), (0.4, -1.6), (1.4, -1.4), (1.3, -0.3), 14)[1:])
    rim = rect(-1.45, -0.3, 1.45, 0.0)
    sc.add([rim, urn], [rim, urn + [urn[0]]])
    return make("Boston Fern on an Urn", sc.s)


@design("houseplants_staghorn_fern", T)
def staghorn_fern(rng):
    sc = Scene()
    board = rrect(-2.2, -2.6, 2.2, 1.8, 0.3)
    grain = [cubic((-1.8, -2.2), (-1.6, -0.5), (-1.9, 0.5), (-1.7, 1.4), 16), cubic((1.8, -2.2), (1.7, -0.6), (1.9, 0.4), (1.75, 1.4), 16)]
    wire = [[(-1.5, 1.6), (0, 3.0)], [(1.5, 1.6), (0, 3.0)], circle(0, 3.12, 0.12, 10)]
    sc.add([board] + grain + wire)
    shield = polar(lambda t: 1.0 * (1 + 0.1 * math.sin(5 * t)), cx=0, cy=-0.9, n=90)
    sc.add([shield] + [quad((0, -0.9), (0.2 * math.cos(a), -0.9 + 0.2 * math.sin(a)), (0.85 * math.cos(a), -0.9 + 0.85 * math.sin(a)), 8) for a in (0.5, 1.6, 2.6, 3.8, 5.5)][0:1], shield)

    half = [(0.12, 0.0), (0.22, 0.35), (0.3, 0.6), (0.55, 0.85), (0.85, 1.05), (1.0, 1.25), (0.75, 1.12), (0.5, 1.0), (0.5, 1.3), (0.45, 1.6),
            (0.3, 1.2), (0.22, 0.88), (0.0, 0.8)]
    frond = half + [(-x, y) for x, y in half[::-1][1:-1]]
    for ang, L in [(160, 1.5), (20, 1.5), (125, 1.75), (55, 1.75), (90, 1.6)]:
        a = math.radians(ang)
        o = place(chaikin(frond, 2), (0.25 * math.cos(a), -0.5), ang, L, L * 0.8)
        rib = place([(0, 0.05), (0, 0.6)], (0.25 * math.cos(a), -0.5), ang, L, L * 0.9)
        sc.add([o, rib], o)
    return make("Staghorn Fern Mounted on a Board", sc.s)


@design("houseplants_air_plant_globe", T)
def air_plant_globe(rng):
    sc = Scene()
    globe = circle(0, -0.2, 2.2, 120)
    opening = ellipse(0.15, 1.0, 1.35, 0.55, 50, rot=0.2)
    sand = quad((-1.95, -1.2), (0, -1.0), (1.95, -1.2), 20)
    pebbles = [stone(x, y, 0.28, 0.16) for x, y in [(-1.1, -1.45), (-0.4, -1.55), (0.4, -1.5), (1.1, -1.45), (-0.75, -1.95), (0.1, -2.0), (0.8, -1.95)]]
    sc.add([globe, opening, sand] + pebbles + [[(0, 2.0), (0, 3.4)]])
    for a, L, curl in [(160, 1.3, -0.5), (20, 1.3, 0.5), (130, 1.5, -0.4), (50, 1.5, 0.4), (100, 1.6, -0.3), (80, 1.6, 0.3)]:
        r = math.radians(a)
        p0 = (0, -1.0)
        p3 = (L * math.cos(r), -1.0 + L * math.sin(r))
        cen = cubic(p0, (0.4 * math.cos(r), -0.6), (p3[0] + curl, p3[1] - 0.2), p3, 20)
        b = blade(cen, 0.2)
        sc.add([b], b)
    hook = arc(0, 3.55, 0.15, -math.pi / 2, math.pi, 10)
    return make("Air Plant in a Glass Globe", sc.s + [hook])


@design("houseplants_terrarium", T)
def terrarium(rng):
    sc = Scene()
    jar = chain([(-1.6, 1.6)], [(-1.8, 1.3), (-1.8, -2.4)], arc(-1.4, -2.4, 0.4, math.pi, 1.5 * math.pi, 6), arc(1.4, -2.4, 0.4, 1.5 * math.pi, TAU, 6), [(1.8, 1.3), (1.6, 1.6)])
    lid = [rect(-1.7, 1.6, 1.7, 1.9), chain([(-1.5, 1.9)], earc(0, 1.9, 1.5, 0.7, math.pi, 0, 20)[1:]), circle(0, 2.8, 0.22, 14)]
    layers = [wave(-1.8, 1.8, -1.9, 0.08, 3, 40), wave(-1.8, 1.8, -1.2, 0.1, 2, 40)]
    pebbles = [stone(x, -2.3, 0.22, 0.13) for x in (-1.2, -0.6, 0.0, 0.6, 1.2)]
    sc.add([jar] + lid + layers + pebbles)
    for a in (60, 90, 120, 145, 35):
        r = math.radians(a)
        mid = quad((-0.7, -1.1), (-0.7 + 0.5 * math.cos(r), -1.1 + 0.9 * math.sin(r)), (-0.7 + 1.1 * math.cos(r), -1.1 + 1.2 * math.sin(r)), 12)
        sc.add([mid])
        for i in (4, 7, 10):
            for sg in (1, -1):
                p, o = leaf("lance", mid[i], tangent(mid, i) + sg * 60, 0.3, 0.35, rib=0)
                sc.add(p, o)
    for a in (40, 80, 100, 140, 60, 120):
        p, o = leaf("ovate", (0.9, -1.1), a, 0.6, 0.55, rib=0)
        sc.add(p, o)
    moss = chain(arc(-1.45, -1.15, 0.3, math.pi, 0, 10))
    mound = [chain(arc(1.5, -1.15, 0.28, math.pi, math.pi / 2, 8)), chain(arc(0.15, -1.15, 0.3, math.pi, 0, 10))]
    sc.add([moss] + mound)
    return make("Terrarium Jar Garden", sc.s)


@design("houseplants_ficus_bonsai", T)
def ficus_bonsai(rng):
    sc = Scene()
    win = rect(-2.8, -0.9, 2.8, 3.2)
    mull = [[(0, -0.9), (0, 3.2)], [(-2.8, 1.15), (2.8, 1.15)]]
    sill = rect(-3.3, -1.3, 3.3, -0.9)
    sc.add([win, sill] + mull)
    trunk = tube(cubic((0.2, -0.3), (1.2, 0.4), (-1.0, 0.9), (0.0, 1.8), 30), lambda t: 0.55 - 0.35 * t)
    br = [tube([(-0.15, 0.95), (-1.3, 1.4)], 0.2), tube([(0.1, 1.3), (1.3, 1.9)], 0.2)]
    sc.add([trunk] + br, [trunk] + br)
    for cx, cy, rx, ry in [(-1.5, 1.6, 1.0, 0.5), (1.5, 2.1, 1.0, 0.5), (0.0, 2.3, 1.1, 0.55)]:
        pad = polar(lambda t, rx=rx, ry=ry: 1.0 * (1 + 0.08 * math.sin(9 * t)), n=120)
        pad = [(cx + x * rx, cy + y * ry) for x, y in pad]
        sc.add([pad], pad)
    tray = poly((-1.9, -0.3), (1.9, -0.3), (1.6, -0.75), (-1.6, -0.75))
    feet = [rect(-1.4, -0.9, -1.0, -0.75), rect(1.0, -0.9, 1.4, -0.75)]
    sc.add([tray, [(-1.9, -0.45), (1.9, -0.45)]] + feet, tray)
    return make("Ficus Bonsai on a Windowsill", sc.s)


@design("houseplants_kokedama", T)
def kokedama(rng):
    sc = Scene()
    ball = circle(0, -0.9, 1.4, 120)
    sc.add([[(-1.3, -0.4), (0, 3.6)], [(1.3, -0.4), (0, 3.6)], circle(0, 3.75, 0.15, 10)])
    for b, a, L in [((-1.0, 1.3), 150, 1.2), ((1.0, 1.4), 30, 1.2), ((0.1, 2.0), 95, 1.3), ((-0.5, 1.8), 125, 1.0), ((0.6, 1.9), 62, 1.0)]:
        sc.add([quad((0, 0.4), (b[0] * 0.3, b[1] * 0.7), b, 10)])
        p, o = leaf("heart", b, a, L, 1.0, veins=1, vlen=0.6)
        sc.add(p, o)
    twine = [earc(0, -0.9, 1.4, 0.5, math.pi + 0.05, TAU - 0.05, 40, rot=r) for r in (0.45, -0.45)] + [earc(0, -0.9, 1.4, 0.4, math.pi + 0.05, TAU - 0.05, 40, rot=0.0)]
    sc.add([ball] + twine, ball)
    sc.add([ellipse(0, -2.6, 1.8, 0.32, 50)])
    return make("Kokedama Moss Ball Plant", sc.s)


@design("houseplants_windowsill_herbs", T)
def windowsill_herbs(rng):
    sc = Scene()
    win = poly((-3.2, -0.9), (-3.2, 3.2), (3.2, 3.2), (3.2, -0.9), closed=False)
    mull = [[(0, -0.9), (0, 3.2)]]
    sc.add([win] + mull)
    # basil
    for b, a, L in [((-2.2, -0.1), 150, 0.8), ((-1.6, -0.1), 30, 0.8), ((-2.1, 0.5), 130, 0.75), ((-1.7, 0.5), 50, 0.75), ((-1.9, 1.0), 95, 0.8)]:
        sc.add([[(-1.9, -0.6), b]])
        p, o = leaf("ovate", b, a, L, 0.7, veins=2, vlen=0.5)
        sc.add(p, o)
    # mint
    for b, a in [((0.0, 0.0), 160), ((0.0, 0.0), 20), ((0.0, 0.7), 145), ((0.0, 0.7), 35), ((0.0, 1.3), 120), ((0.0, 1.3), 60), ((0.0, 1.7), 90)]:
        side = SIDES["ovate"]()
        side = [(x * (1 + 0.15 * math.sin(40 * y)), y) for x, y in side]
        o = place(outline_of(side), b, a, 0.65, 0.55)
        sc.add([o, place([(0, 0), (0, 0.8)], b, a, 0.65, 0.55)], o)
    sc.add([[(0.0, -0.6), (0.0, 1.7)]])
    # rosemary
    for x0, x1, top in [(1.6, 1.4, 1.7), (1.9, 2.0, 2.0), (2.2, 2.6, 1.6)]:
        st = [(x0, -0.6), (x1, top)]
        sc.add([st])
        for k in range(1, 8):
            t = k / 8
            px, py = x0 + (x1 - x0) * t, -0.6 + (top + 0.6) * t
            sc.add([[(px, py), (px - 0.3, py + 0.2)], [(px, py), (px + 0.3, py + 0.2)]])
    for cx in (-1.9, 0.0, 1.9):
        add_pot(sc, pot_terra(cx, -0.5, 1.4, 1.2))
        lab = rect(cx + 0.25, -0.5, cx + 0.55, 0.1)
        sc.add([lab], lab)
    sill = rect(-3.4, -2.0, 3.4, -1.7)
    sc.add([sill], sill)
    return make("Herb Pots on a Windowsill", sc.s)


@design("houseplants_ladder_shelf", T)
def ladder_shelf(rng):
    sc = Scene()
    rails = [[(-2.6, -2.9), (-1.6, 3.0)], [(2.6, -2.9), (1.6, 3.0)]]
    shelves = [rect(-2.45, -1.95, 2.45, -1.75), rect(-2.2, -0.15, 2.2, 0.05), rect(-1.95, 1.65, 1.95, 1.85)]
    sc.add(rails + shelves)
    # top: small cactus
    col = chain([(-0.85, 2.3), (-0.85, 3.0)], arc(-0.6, 3.0, 0.25, math.pi, 0, 8), [(-0.35, 2.3)])
    sc.add([col], col)
    add_pot(sc, pot_terra(-0.6, 2.55, 0.9, 0.7, 0.22))
    for a in (30, 60, 90, 120, 150):
        p, o = leaf("ovate", (0.7, 2.6), a, 0.55, 0.45, rib=0)
        sc.add(p, o)
    add_pot(sc, pot_bowl(0.7, 2.6, 1.2, 0.75))
    # middle: trailing plant
    vine = cubic((-0.6, 0.85), (-1.3, 0.6), (-1.3, -0.6), (-1.1, -1.5), 30)
    sc.add([vine])
    for p, o in leaves_along(vine, range(5, 30, 6), 0.45, 0.5, "heart", 55):
        sc.add(p, o)
    for b, a in [((-0.5, 0.95), 140), ((0.0, 1.0), 80)]:
        p, o = leaf("heart", b, a, 0.55, 0.6)
        sc.add(p, o)
    add_pot(sc, pot_round(-0.25, 0.95, 1.2, 0.9, 0.15))
    for b, a in [((1.2, 0.8), 70), ((1.2, 0.8), 110), ((1.2, 0.8), 90)]:
        p, o = leaf("sword", b, a, 0.9, 0.35, rib=0)
        sc.add(p, o)
    add_pot(sc, pot_terra(1.2, 0.8, 0.8, 0.75, 0.2))
    # bottom: big leafy plant
    for b, a in [((-1.2, -0.8), 150), ((-0.5, -0.6), 100), ((0.3, -0.6), 70), ((1.0, -0.8), 30)]:
        p, o = leaf("ovate", b, a, 0.9, 0.7, veins=0)
        sc.add(p, o)
    add_pot(sc, pot_belly(-0.1, -0.75, 1.8, 1.0))
    sc.add([floor()])
    return make("Ladder Shelf of Potted Plants", sc.s)


@design("houseplants_mister_fern", T)
def mister_fern(rng):
    sc = Scene()
    for cx1, cy1, x3, y3 in [(-0.8, 0.8, -2.6, -0.3), (0.3, 1.2, 0.6, 2.6), (-1.5, 1.2, -2.3, 2.2), (0.3, 0.4, 1.2, -0.1)]:
        mid = cubic((-0.8, -0.6), (cx1, cy1), (x3 * 0.8, y3), (x3, y3), 30)
        sc.add([mid])
        for i in range(4, 29, 4):
            s = 0.6 * (1 - 0.5 * i / 30)
            for sg in (1, -1):
                p, o = leaf("lance", mid[i], tangent(mid, i) + sg * 60, s, 0.32, rib=0)
                sc.add(p, o)
    add_pot(sc, pot_terra(-0.8, -0.5, 2.0, 2.3))
    body = chain([(1.7, -2.9)], [(1.7, -0.6)], [(1.85, -0.2), (1.9, 0.3), (2.9, 0.3), (2.95, -0.2), (3.1, -0.6), (3.1, -2.9), (1.7, -2.9)])
    head = poly((1.9, 0.3), (1.95, 0.9), (1.4, 0.9), (1.25, 0.7), (1.9, 0.6), closed=False)
    head2 = poly((1.95, 0.9), (2.9, 0.9), (2.9, 0.3), closed=False)
    trigger = poly((1.9, 0.55), (1.6, 0.2), (1.6, -0.1), (1.85, 0.1), closed=False)
    label = rrect(1.9, -2.2, 2.9, -1.0, 0.1)
    mist = [[(1.15, 0.8), (0.4, 1.3)], [(1.15, 0.75), (0.4, 0.4)], earc(1.15, 0.8, 0.85, 0.5, math.radians(150), math.radians(215), 10)]
    drops = [circle(x, y, 0.07, 8) for x, y in [(0.75, 0.9), (0.6, 0.65), (0.85, 0.6)]]
    sc.add([body, head, head2, trigger, label] + mist + drops)
    sc.add([floor()])
    return make("Misting a Fern with a Spray Bottle", sc.s)


@design("houseplants_repotting", T)
def repotting(rng):
    sc = Scene()
    for b, a, L in [((0.6, 1.0), 140, 1.3), ((0.75, 1.05), 40, 1.3), ((0.6, 1.1), 100, 1.5), ((0.7, 1.1), 72, 1.4), ((0.55, 0.95), 172, 1.0), ((0.8, 0.95), 8, 1.0)]:
        p, o = leaf("ovate", b, a, L, 0.8, veins=0)
        sc.add(p, o)
    ball = ellipse(0.65, 0.4, 1.0, 0.65, 50)
    roots = [cubic((x, -0.15), (x - 0.2, -0.45), (x + 0.2, -0.65), (x - 0.05, -0.95), 10) for x in (0.1, 0.65, 1.2)]
    sc.add([ball] + roots, ball)
    sc.add(soil(0.65, -1.05, 2.4))
    add_pot(sc, pot_terra(0.65, -1.0, 2.7, 1.9))
    rim = rect(-1.0, -0.65, -0.6, 0.65)
    body = poly((-1.0, -0.55), (-2.4, -0.4), (-2.4, 0.4), (-1.0, 0.55), closed=False)
    old = [transform(q, dx=-0.4, dy=-2.95, s=0.75) for q in (rim, body)]
    sc.add(old)
    pile = chain(arc(-2.4, -2.9, 0.9, 0, math.pi, 20))
    trowel = [transform(lens((0, 0), (0, 1.1), 0.3), dx=-2.55, dy=-2.45, rot=0.35), transform(rrect(-0.09, 1.1, 0.09, 1.9, 0.05), dx=-2.55, dy=-2.45, rot=0.35),
              transform(rrect(-0.15, 1.9, 0.15, 2.5, 0.12), dx=-2.55, dy=-2.45, rot=0.35)]
    sc.add([pile])
    sc.add(trowel, trowel[0])
    sc.add([floor(-2.9)])
    return make("Repotting a Houseplant", sc.s)


@design("houseplants_succulent_wreath", T)
def succulent_wreath(rng):
    sc = Scene()
    sc.add([circle(0, -0.3, 2.6, 100), circle(0, -0.3, 1.5, 80)])
    for k in range(8):
        a = math.radians(90 + 45 * k + 22)
        cx, cy = 2.05 * math.cos(a), -0.3 + 2.05 * math.sin(a)
        r = 0.62 if k % 2 == 0 else 0.5
        ros = rosette_top(cx, cy, [(7, r * 0.35, r, r * 0.8), (5, r * 0.1, r * 0.6, r * 0.55)], 20 * k)
        sc.add(ros.s, circle(cx, cy, r * 1.25, 30))
    bow = [lens((0, 2.4), (-0.9, 2.9), 0.35), lens((0, 2.4), (0.9, 2.9), 0.35), circle(0, 2.4, 0.18, 12),
           [(-0.1, 2.25), (-0.5, 1.6)], [(0.1, 2.25), (0.5, 1.6)]]
    sc.add(bow, circle(0, 2.4, 0.3, 12))
    return make("Succulent Wreath", sc.s)


@design("houseplants_teacup_succulents", T)
def teacup_succulents(rng):
    sc = Scene()
    for cx, s in [(-0.8, 1.0), (0.7, 0.85), (0.0, 1.15)]:
        for a in (10, 40, 70, 90, 110, 140, 170):
            p, o = leaf("ovate", (cx, 0.0), a, 0.9 * s, 0.6 * s, rib=0)
            sc.add(p, o)
    cup = chain([(-1.8, 0.1)], cubic((-1.8, 0.1), (-1.8, -1.6), (-0.8, -1.9), (0, -1.9), 16)[1:], cubic((0, -1.9), (0.8, -1.9), (1.8, -1.6), (1.8, 0.1), 16)[1:])
    handle = tube(arc(1.95, -0.6, 0.55, math.pi * 0.55, -math.pi * 0.55, 20), 0.22, cap=False)
    sc.add([handle])
    sc.add([cup, earc(0, 0.1, 1.8, 0.3, math.pi, TAU, 30)], cup + [cup[0]])
    sc.add([earc(0, 0.1, 1.8, 0.3, 0, math.pi, 30)])
    saucer = [ellipse(0, -2.0, 2.9, 0.55, 60), ellipse(0, -2.0, 1.2, 0.22, 40)]
    sc.add(saucer, ellipse(0, -2.0, 2.9, 0.55, 60))
    sc.s = occlude(sc.s, [cup + [cup[0]]]) + [cup] if False else sc.s
    deco = [heart(0, -1.0, 0.25)]
    sc.add(deco)
    return make("Succulents in a Teacup", sc.s)


@design("houseplants_cactus_boot", T)
def cactus_boot(rng):
    sc = Scene()
    col = chain([(-0.4, 0.4), (-0.4, 2.6)], arc(0, 2.6, 0.4, math.pi, 0, 12), [(0.4, 0.4)])
    arm = chain([(0.4, 1.2), (0.9, 1.2)], arc(0.9, 1.55, 0.35, -math.pi / 2, 0, 6), [(1.25, 2.2)], arc(1.0, 2.2, 0.25, 0, math.pi, 8), [(0.75, 1.55), (0.4, 1.55)])
    sc.add([arm], arm + [arm[0]])
    sc.add([col, [(0, 0.4), (0, 2.9)]], col + [col[0]])
    small = chain([(-1.3, 0.4)], ellipse(-0.95, 0.8, 0.45, 0.55, 30))
    sc.add([small], small)
    fl = [lens((0, 3.0), (0.4 * math.cos(math.radians(a)), 3.0 + 0.4 * math.sin(math.radians(a))), 0.3) for a in (30, 90, 150)]
    sc.add(fl)
    boot = chain([(-1.5, 0.5), (-1.4, -1.9)], [(-1.45, -2.55), (1.6, -2.55)],
                 quad((1.6, -2.55), (3.0, -2.5), (2.9, -1.9), 10), quad((2.9, -1.9), (1.5, -1.6), (0.9, -1.0), 10), [(1.1, 0.5)])
    top_ = quad((-1.6, 0.5), (-0.2, 0.25), (1.2, 0.5), 12)
    stitch = [quad((-1.0, 0.0), (-0.2, -0.6), (0.6, 0.0), 12), quad((-1.0, -0.5), (-0.2, -1.1), (0.6, -0.5), 12)]
    heel = rect(-1.45, -2.9, -0.7, -2.55)
    sc.add([boot, top_, heel] + stitch, boot + [boot[0]])
    sc.add([floor(-2.9)])
    return make("Cactus in a Cowboy Boot Planter", sc.s)


def ivy_leaf(base, ang, s):
    lobes = [(90, 0.55), (35, 0.42), (145, 0.42), (-15, 0.3), (195, 0.3)]
    pts = []
    for i in range(121):
        ph = -90 + 360 * i / 120
        r = 0.2 + sum(L * math.exp(-((((ph - a + 180) % 360) - 180) / 22.0) ** 2) for a, L in lobes)
        pts.append((r * math.cos(math.radians(ph)), 0.28 + r * math.sin(math.radians(ph))))
    pts = [(x, max(y, 0.0)) for x, y in pts]
    out = place(pts, base, ang, s * 1.4, s * 1.4)
    return out + [out[0]]


# dropped: the Garden book has this subject
def hanging_ivy(rng):
    sc = Scene()
    sc.add([[(-1.5, 0.9), (0, 3.2)], [(1.5, 0.9), (0, 3.2)], [(0, 0.95), (0, 3.2)], circle(0, 3.35, 0.15, 10)])
    for b, a in [((-0.7, 1.1), 120), ((0.0, 1.2), 90), ((0.7, 1.1), 60), ((-1.1, 1.0), 160), ((1.1, 1.0), 20)]:
        o = ivy_leaf(b, a, 0.75)
        sc.add([o], o)
    basket = chain([(-1.6, 0.9)], earc(0, 0.9, 1.6, 1.5, math.pi, TAU, 40)[1:-1], [(1.6, 0.9)])
    weave = [earc(0, 0.9, 1.6, 1.5 * f, math.pi, TAU, 30) for f in (0.4, 0.7)]
    rim = rrect(-1.75, 0.8, 1.75, 1.05, 0.1)
    sc.add([rim, basket] + weave, [rim, basket + [basket[0]]])
    for x0, x1, y1 in [(-1.5, -2.4, -2.6), (-0.6, -0.9, -2.9), (0.6, 0.8, -2.4), (1.5, 2.4, -2.8)]:
        v = cubic((x0, 0.8), (x0 * 1.3, -0.2), (x1, -1.0), (x1, y1), 40)
        sc.add([v])
        sg = 1
        for i in range(10, 41, 9):
            o = ivy_leaf(v[min(i, 40)], tangent(v, min(i, 40)) + sg * 70, 0.6)
            sc.add([o], o)
            sg = -sg
    return make("Hanging Basket of Ivy", sc.s)


@design("houseplants_parlor_palm", T)
def parlor_palm(rng):
    sc = Scene()
    for x3, y3, sg in [(-2.6, 1.0, -1), (2.6, 1.2, 1), (-1.5, 2.8, -1), (1.4, 3.0, 1), (0.1, 3.4, 1)]:
        mid = cubic((0, 0.6), (x3 * 0.2, y3 * 0.8 + 0.6), (x3 * 0.7, y3 + 0.4), (x3, y3), 40)
        sc.add([mid])
        for i in range(8, 39, 4):
            ang = tangent(mid, i)
            L = 0.75 * (1 - 0.4 * i / 40)
            for s2 in (1, -1):
                a2 = math.radians(ang + s2 * 50 - 25 * (1 if mid[-1][0] > 0 else -1) * 0)
                p = mid[i]
                sc.add([[p, (p[0] + L * math.cos(a2), p[1] + L * math.sin(a2) - 0.15)]])
    pot = poly((-1.0, 0.6), (-0.8, -0.6), (0.8, -0.6), (1.0, 0.6))
    sc.add([pot, [(-0.97, 0.35), (0.97, 0.35)]], pot)
    stand = [rect(-1.2, -0.75, 1.2, -0.6), [(-1.0, -0.75), (-1.6, -2.9)], [(1.0, -0.75), (1.6, -2.9)], [(-0.4, -0.75), (-0.55, -2.9)], [(0.4, -0.75), (0.55, -2.9)],
             [(-1.3, -1.9), (1.3, -1.9)]]
    sc.add(stand)
    sc.add([floor()])
    return make("Parlor Palm on a Plant Stand", sc.s)


@design("houseplants_pilea", T)
def pilea(rng):
    sc = Scene()
    stem = [(0, -0.9), (0.05, 0.6)]
    sc.add([stem])
    hints = []
    for a, L, r in [(160, 1.9, 0.62), (20, 1.9, 0.62), (130, 2.0, 0.58), (50, 2.1, 0.6), (100, 2.2, 0.55), (75, 1.6, 0.5), (190, 1.5, 0.5), (-10, 1.5, 0.5), (115, 1.2, 0.42)]:
        ra = math.radians(a)
        tip = (L * math.cos(ra), 0.5 + L * math.sin(ra))
        sc.add([quad((0.05, 0.5), (tip[0] * 0.5, 0.5 + L * 0.7 * math.sin(ra) + 0.3), tip, 10)])
        c = ellipse(tip[0], tip[1], r, r * 0.9, 40)
        sc.add([c], c)
        hints.append(eye(tip[0], tip[1], 0.06))
    pot = pot_round(0, -0.85, 2.2, 1.7)
    add_pot(sc, pot)
    saucer = rrect(-1.5, -2.85, 1.5, -2.55, 0.12)
    sc.add([saucer], saucer)
    return make("Chinese Money Plant", sc.s, hints)


@design("houseplants_philodendron_pole", T)
def philodendron_pole(rng):
    sc = Scene()
    pole = rect(-0.3, -0.9, 0.3, 3.3)
    texture = [arc(0, y, 0.2, 0.3, 2.8, 6) for y in (-0.3, 0.6, 1.5, 2.4)]
    sc.add([pole] + texture)
    vine = [(0.35 * math.sin(2.2 * y), y) for y in [-0.9 + 4.0 * i / 60 for i in range(61)]]
    sc.add([vine])
    sg = 1
    for i in range(6, 61, 7):
        x, y = vine[i]
        a = 90 + sg * 60
        p, o = leaf("heart", (x, y), a, 1.0 - 0.3 * i / 60, 1.0 - 0.3 * i / 60, veins=1, vlen=0.6)
        sc.add(p, o)
        sg = -sg
    for b, a in [((-0.4, -0.7), 160), ((0.4, -0.7), 20)]:
        p, o = leaf("heart", b, a, 0.9, 0.9)
        sc.add(p, o)
    add_pot(sc, pot_terra(0, -0.75, 2.4, 2.1))
    sc.add([floor()])
    return make("Philodendron on a Moss Pole", sc.s)


@design("houseplants_alocasia", T)
def alocasia(rng):
    sc = Scene()
    specs = [((-1.6, 1.6), 150, 1.9), ((1.5, 1.8), 35, 1.9), ((-0.2, 2.2), 100, 1.7), ((0.4, 0.9), 60, 1.3)]
    for b, a, L in specs:
        sc.add([quad((0, -0.9), (b[0] * 0.3, b[1] * 0.6), b, 12)])
    for b, a, L in specs:
        side = SIDES["arrow"]()
        o = place(outline_of(side), b, a, L, 1.25)
        veins = [place([(0, -0.02), (0, 0.9)], b, a, L, 1.25)]
        for y in (0.15, 0.4, 0.62):
            for sg in (1, -1):
                veins.append(place([(0, y - 0.05), (sg * half_width(side, y + 0.12) * 0.85, y + 0.12)], b, a, L, 1.25))
        for sg in (1, -1):
            veins.append(place([(0, -0.02), (sg * 0.32, -0.36)], b, a, L, 1.25))
        sc.add([o] + veins, o)
    add_pot(sc, pot_round(0, -0.85, 2.3, 2.0, 0.2))
    sc.add([floor()])
    return make("Alocasia Elephant Ear", sc.s)


@design("houseplants_croton", T)
def croton(rng):
    sc = Scene()
    specs = [((-1.0, 0.0), 165), ((1.0, 0.0), 15), ((-0.9, 0.6), 140), ((0.9, 0.6), 40), ((-0.5, 1.2), 120), ((0.5, 1.2), 60), ((0.0, 1.5), 92),
             ((-0.2, 0.4), 105), ((0.3, 0.3), 75)]
    sc.add([[(0, -0.9), (0, 1.5)]] + [[(0, max(-0.6, b[1] - 0.5)), b] for b, a in specs])
    for k, (b, a) in enumerate(specs):
        p, o = leaf("lance", b, a, 1.4, 0.75, veins=2, vlen=0.6)
        spots = [ellipse(*place([(0.08 * (1 if k % 2 else -1), 0.55)], b, a, 1.4, 0.75)[0], 0.09, 0.09, 8)]
        sc.add(p + spots, o)
    add_pot(sc, pot_terra(0, -0.85, 2.4, 2.0))
    sc.add([floor()])
    return make("Colorful Croton Plant", sc.s)


@design("houseplants_dracaena", T)
def dracaena(rng):
    sc = Scene()
    canes = [(-0.45, 1.6), (0.4, 0.6), (0.0, 2.6)]
    for x, top in canes:
        c = rect(x - 0.18, -0.9, x + 0.18, top)
        sc.add([c] + [[(x - 0.18, y), (x + 0.18, y)] for y in [-0.4 + 0.45 * k for k in range(9) if -0.4 + 0.45 * k < top - 0.2]], c)
        for a, L in [(160, 1.4), (20, 1.4), (130, 1.5), (50, 1.5), (100, 1.4), (75, 1.3), (190, 1.0), (-10, 1.0)]:
            r = math.radians(a)
            p0 = (x, top)
            p3 = (x + L * math.cos(r), top + L * math.sin(r) - 0.35)
            b = blade(quad(p0, (x + L * 0.6 * math.cos(r), top + L * 0.8 * math.sin(r) + 0.2), p3, 16), 0.24)
            sc.add([b], b)
    pot = rect(-1.1, -2.9, 1.1, -0.85)
    sc.add([pot, [(-1.1, -1.15), (1.1, -1.15)]], pot)
    return make("Dracaena Cane Plant", sc.s)


@design("houseplants_begonia", T)
def begonia(rng):
    sc = Scene()
    hints = []
    for b, a, L, W in [((-1.0, 0.6), 160, 1.8, 0.9), ((1.0, 0.8), 25, 1.8, 0.9), ((-0.4, 1.4), 125, 1.7, 0.85), ((0.4, 1.5), 60, 1.7, 0.85)]:
        sc.add([quad((0, -0.9), (b[0] * 0.3, b[1] * 0.5), b, 10)])
        side = cubic((0, 0), (0.6, -0.1), (0.7, 0.6), (0, 1), 26)
        other = cubic((0, 0), (0.25, 0.1), (0.35, 0.7), (0, 1), 26)
        o = place(side + [(-x, y) for x, y in other][::-1][1:], b, a, L, W)
        rib = place([(0, 0), (-0.05, 0.85)], b, a, L, W)
        sc.add([o, rib], o)
        for fx, fy in [(0.18, 0.25), (0.25, 0.5), (0.15, 0.72), (-0.12, 0.4), (-0.1, 0.65), (0.32, 0.38)]:
            hints.append(eye(*place([(fx, fy)], b, a, L, W)[0], 0.07))
    for x0, x1, y1 in [(-0.2, -1.4, 2.6), (0.2, 1.3, 2.8)]:
        stalk = quad((0, 1.0), (x0, 2.6), (x1, y1), 12)
        sc.add([stalk])
        for dx, dy in [(-0.4, -0.45), (0.4, -0.45), (0.0, 0.05)]:
            fl = chain([(x1 + dx - 0.15, y1 + dy)],
                       cubic((x1 + dx - 0.15, y1 + dy), (x1 + dx - 0.25, y1 + dy - 0.4), (x1 + dx + 0.25, y1 + dy - 0.4), (x1 + dx + 0.15, y1 + dy), 10), [(x1 + dx - 0.15, y1 + dy)])
            sc.add([fl, [(x1, y1), (x1 + dx, y1 + dy)]], fl)
    add_pot(sc, pot_terra(0, -0.85, 2.3, 2.0))
    sc.add([floor()])
    return make("Polka Dot Begonia", sc.s, hints)


@design("houseplants_african_violet", T)
def african_violet(rng):
    sc = Scene()
    for a in (125, 55, 150, 30, 178, 2):
        r = math.radians(a)
        p, o = leaf("round", (0.3 * math.cos(r), -0.55), a, 1.4, 1.05, rib=0.75, veins=2, vlen=0.55)
        sc.add(p, o)
    for cx, cy, s in [(-0.65, 0.95, 0.95), (0.65, 1.0, 0.95), (0.0, 1.55, 0.95), (0.0, 0.6, 0.85)]:
        petals = []
        for k in range(5):
            a = math.radians(90 + 72 * k)
            petals.append(circle(cx + 0.28 * s * math.cos(a), cy + 0.28 * s * math.sin(a), 0.24 * s, 16))
        sc.add(petals, petals)
        c = circle(cx, cy, 0.11 * s, 10)
        sc.add([c], c)
    add_pot(sc, pot_terra(0, -0.75, 2.2, 1.6))
    saucer = rrect(-1.6, -2.65, 1.6, -2.35, 0.12)
    sc.add([saucer], saucer)
    return make("African Violet in Bloom", sc.s)


@design("houseplants_anthurium", T)
def anthurium(rng):
    sc = Scene()
    for b, a, L in [((-1.2, 0.5), 160, 1.6), ((1.2, 0.6), 20, 1.6), ((-0.4, 1.3), 115, 1.5)]:
        sc.add([quad((0, -0.9), (b[0] * 0.3, b[1] * 0.4), b, 10)])
        p, o = leaf("heart", b, a, L, 1.2, veins=2, vlen=0.6)
        sc.add(p, o)
    for (x, y), rot in [((0.9, 2.2), -0.4), ((-0.9, 2.6), 0.3), ((0.2, 3.0), 0.0)]:
        sc.add([quad((0, -0.9), (x * 0.4, y * 0.5), (x, y - 0.4), 10)])
        h = transform(heart(0, 0, 0.8), dx=x, dy=y, rot=rot)
        sp = transform(ellipse(0.0, 0.55, 0.1, 0.45, 14), dx=x, dy=y, rot=rot - 0.35)
        sc.add([h, sp], h)
    add_pot(sc, pot_round(0, -0.85, 2.3, 2.0))
    sc.add([floor()])
    return make("Anthurium with Heart Blooms", sc.s)


@design("houseplants_string_of_hearts", T)
def string_of_hearts(rng):
    sc = Scene()
    wall_nail = [circle(0, 2.8, 0.1, 8), [(0, 2.8), (-1.4, 1.6)], [(0, 2.8), (1.4, 1.6)]]
    sc.add(wall_nail)
    planter = chain([(-1.6, 1.7), (1.6, 1.7)], earc(0, 1.7, 1.6, 1.9, 0, -math.pi, 40)[1:])
    rim = [(-1.6, 1.45), (1.6, 1.45)]
    for x0, x1, y1 in [(-1.3, -2.4, -2.2), (-0.7, -1.2, -2.9), (-0.1, 0.0, -3.1), (0.5, 0.9, -2.6), (1.1, 2.2, -2.9), (1.45, 2.8, -1.6)]:
        v = cubic((x0, 1.65), (x0 * 1.2, 0.0), (x1, -0.8), (x1, y1), 60)
        sc.add([v])
        for i in range(18, 60, 8):
            x, y = v[i]
            ang = tangent(v, i)
            for sg in (1, -1):
                hx = x + 0.28 * math.cos(math.radians(ang + sg * 90))
                hy = y + 0.28 * math.sin(math.radians(ang + sg * 90))
                h = transform(heart(0, 0, 0.17, 40), dx=hx, dy=hy, rot=math.radians(ang + sg * 90 - 90))
                sc.add([h], h)
    sc.add([planter + [planter[0]], rim], planter + [planter[0]])
    for b, a in [((-0.8, 1.75), 120), ((0.0, 1.8), 90), ((0.8, 1.75), 60)]:
        h = transform(heart(0, 0, 0.22, 40), dx=b[0], dy=b[1] + 0.25, rot=math.radians(a - 90))
        sc.add([h], h)
    return make("String of Hearts in a Wall Planter", sc.s)


@design("houseplants_hoya_hoop", T)
def hoya_hoop(rng):
    sc = Scene()
    hoop = [circle(0, 1.4, 1.7, 100), [(-0.4, -0.95), (-0.4, -0.25)], [(0.4, -0.95), (0.4, -0.25)]]
    sc.add(hoop)
    vine = [(1.7 * math.cos(t) * (1 + 0.12 * math.sin(7 * t)), 1.4 + 1.7 * math.sin(t) * (1 + 0.12 * math.sin(7 * t))) for t in [math.radians(-80 + 280 * i / 80) for i in range(81)]]
    sc.add([vine])
    sg = 1
    for i in range(4, 81, 8):
        p, o = leaf("ovate", vine[i], tangent(vine, i) + sg * 50, 0.7, 0.5, rib=0.7)
        sc.add(p, o)
        sg = -sg
    for cx, cy in [(-1.6, 2.9), (1.9, 2.2), (-2.1, 0.5)]:
        stars_ = []
        for dx, dy in [(0, 0.0), (-0.38, -0.15), (0.38, -0.15), (-0.2, 0.3), (0.2, 0.3), (0.0, -0.38)]:
            s = star(cx + dx, cy + dy, 0.22, 5, 0.45)
            stars_.append(s)
        for s in stars_:
            sc.add([s], s)
    add_pot(sc, pot_terra(0, -0.85, 2.3, 2.0))
    sc.add([floor()])
    return make("Hoya Wax Plant on a Hoop", sc.s)


@design("houseplants_propagation", T)
def propagation(rng):
    sc = Scene()
    board = rect(-3.3, -2.6, 3.3, -2.3)
    sc.add([board])
    for cx, kind in [(-2.0, "heart"), (0.0, "ovate"), (2.0, "lance")]:
        stem = [(cx, -2.0), (cx + 0.1, 0.9)]
        roots = [cubic((cx, -1.0), (cx - 0.3, -1.4), (cx + 0.2, -1.7), (cx - 0.25, -2.05), 12), cubic((cx + 0.02, -1.0), (cx + 0.35, -1.3), (cx + 0.1, -1.6), (cx + 0.4, -2.0), 12)]
        sc.add([stem] + roots)
        for b, a in [((cx + 0.05, 0.3), 140), ((cx + 0.08, 0.6), 40), ((cx + 0.1, 0.9), 95)]:
            p, o = leaf(kind, b, a, 0.9, 0.75 if kind != "lance" else 0.45)
            sc.add(p, o)
        jar = chain([(cx - 0.3, -0.2), (cx - 0.3, -0.6)], quad((cx - 0.3, -0.75), (cx - 0.8, -0.9), (cx - 0.8, -1.2), 6), [(cx - 0.8, -2.2), (cx + 0.8, -2.2), (cx + 0.8, -1.2)], quad((cx + 0.8, -1.2), (cx + 0.8, -0.75), (cx + 0.3, -0.6), 6), [(cx + 0.3, -0.2)])
        water = [(cx - 0.8, -1.0), (cx + 0.8, -1.0)]
        sc.add([jar, water, ellipse(cx, -0.2, 0.3, 0.08, 14)])
    sc.add([[(-3.0, -2.3), (-3.0, 2.6)], [(3.0, -2.3), (3.0, 2.6)], [(-3.0, 2.6), (3.0, 2.6)]])
    return make("Propagation Jars with Roots", sc.s)


@design("houseplants_umbrella_plant", T)
def umbrella_plant(rng):
    sc = Scene()
    win = rect(-2.0, 0.0, 2.0, 3.3)
    mull = [[(0, 0.0), (0, 3.3)], [(-2.0, 1.65), (2.0, 1.65)]]
    curtains = [chain([(-2.0, 3.3), (-3.0, 3.3)], cubic((-3.0, 3.3), (-3.1, 1.0), (-2.8, 0.2), (-3.1, -0.9), 20)[1:], [(-2.5, -0.9)], cubic((-2.5, -0.9), (-2.2, 0.2), (-2.6, 1.6), (-2.0, 3.3), 20)[1:]),
                chain([(2.0, 3.3), (3.0, 3.3)], cubic((3.0, 3.3), (3.1, 1.0), (2.8, 0.2), (3.1, -0.9), 20)[1:], [(2.5, -0.9)], cubic((2.5, -0.9), (2.2, 0.2), (2.6, 1.6), (2.0, 3.3), 20)[1:])]
    sc.add([win] + mull)
    sc.add(curtains, curtains)
    for (x, y), n in [((-0.9, 1.6), 7), ((0.9, 1.8), 7), ((0.0, 2.6), 7)]:
        sc.add([quad((0, -0.6), (x * 0.3, y * 0.5), (x, y), 10)])
        for k in range(n):
            a = 90 + (k - (n - 1) / 2) * 32
            p, o = leaf("lance", (x, y), a, 0.85, 0.45, rib=0.8)
            sc.add(p, o)
    add_pot(sc, pot_terra(0, -0.5, 1.7, 1.2))
    stool = [rrect(-1.4, -1.9, 1.4, -1.65, 0.1), [(-1.1, -1.9), (-1.4, -3.2)], [(1.1, -1.9), (1.4, -3.2)], [(-0.5, -1.9), (-0.55, -3.2)], [(0.5, -1.9), (0.55, -3.2)], [(-1.25, -2.6), (1.25, -2.6)]]
    sc.add(stool)
    return make("Umbrella Plant by the Window", sc.s)


@design("houseplants_mini_cacti_trio", T)
def mini_cacti_trio(rng):
    sc = Scene()
    ball = polar(lambda t: 0.75 * (1 + 0.05 * math.cos(10 * t)), cx=-2.1, cy=0.2, n=100)
    sc.add([ball, earc(-2.1, 0.2, 0.3, 0.75, -1.4, 1.4, 12), earc(-2.1, 0.2, 0.3, 0.75, 1.75, 4.5, 12)], ball)
    fl = star(-2.1, 1.1, 0.3, 6, 0.5)
    sc.add([fl], fl)
    col = chain([(-0.35, -0.4), (-0.35, 1.8)], arc(0, 1.8, 0.35, math.pi, 0, 10), [(0.35, -0.4)])
    arm = chain([(0.35, 0.4), (0.7, 0.4)], arc(0.7, 0.7, 0.3, -math.pi / 2, 0, 6), [(1.0, 1.2)], arc(0.8, 1.2, 0.2, 0, math.pi, 8), [(0.6, 0.75), (0.35, 0.75)])
    sc.add([arm], arm + [arm[0]])
    sc.add([col + [col[0]], [(0, -0.4), (0, 2.0)]], col + [col[0]])
    pads = [ellipse(2.1, 0.3, 0.55, 0.75, 40), ellipse(1.75, 1.3, 0.35, 0.45, 30, rot=0.4), ellipse(2.5, 1.3, 0.35, 0.45, 30, rot=-0.4)]
    for p in pads[1:] + pads[:1]:
        sc.add([p], p)
    for cx in (-2.1, 0.0, 2.1):
        add_pot(sc, pot_terra(cx, -0.4, 1.4, 1.3, 0.3))
    sc.add([floor(-1.7)])
    hints = [eye(x, y, 0.06) for x, y in [(2.0, 0.6), (2.3, 0.1), (1.9, -0.1), (1.75, 1.4), (2.5, 1.45)]]
    return make("Trio of Mini Cacti", sc.s, hints)


@design("houseplants_lithops", T)
def lithops(rng):
    sc = Scene()
    dish = [ellipse(0, -0.2, 3.1, 1.3, 90)]
    sc.add(dish + [chain([(-3.1, -0.2), (-3.0, -1.0)], earc(0, -1.0, 3.0, 1.25, math.pi, TAU, 50)[1:], [(3.1, -0.2)])])
    peb = [stone(x, y, 0.22, 0.13) for x, y in [(-2.5, -0.6), (2.6, 0.2), (1.2, -1.0), (-1.4, -1.0), (-0.9, 0.85), (1.0, 0.85)]]
    sc.add(peb)
    for cx, cy, s in [(-1.55, 0.05, 1.25), (0.15, 0.3, 1.35), (1.75, -0.05, 1.2), (-0.1, -1.0, 1.1)]:
        body = chain([(cx - 0.6 * s, cy - 0.3 * s)], cubic((cx - 0.6 * s, cy - 0.3 * s), (cx - 0.7 * s, cy + 0.8 * s), (cx + 0.7 * s, cy + 0.8 * s), (cx + 0.6 * s, cy - 0.3 * s), 24)[1:])
        base = quad((cx + 0.6 * s, cy - 0.3 * s), (cx, cy - 0.5 * s), (cx - 0.6 * s, cy - 0.3 * s), 10)
        outline = body + base[1:]
        split = [(cx, cy + 0.52 * s), (cx, cy + 0.1 * s)]
        tops = [quad((cx - 0.55 * s, cy + 0.35 * s), (cx - 0.3 * s, cy + 0.15 * s), (cx - 0.05 * s, cy + 0.42 * s), 8),
                quad((cx + 0.05 * s, cy + 0.42 * s), (cx + 0.3 * s, cy + 0.15 * s), (cx + 0.55 * s, cy + 0.35 * s), 8)]
        sc.add([outline, split] + tops, outline)
    return make("Lithops Living Stones", sc.s)


@design("houseplants_venus_flytrap", T)
def venus_flytrap(rng):
    sc = Scene()
    for (bx, by), ang, s in [((-1.3, 1.1), 130, 1.0), ((1.3, 1.2), 50, 1.0), ((0.0, 1.9), 92, 1.1), ((-1.9, 0.0), 165, 0.8), ((1.9, 0.2), 15, 0.8)]:
        sc.add([quad((0, -0.9), (bx * 0.4, by * 0.4), (bx, by), 10)])
        lobes = []
        for sg in (1, -1):
            pts = cubic((0, 0), (0.7 * sg, 0.05), (0.85 * sg, 0.95), (0.15 * sg, 1.1), 16)
            out = place(pts, (bx, by), ang + sg * 18, 1.0 * s, 1.0 * s)
            lobes.append(out)
            lashes = []
            for i in range(3, 17, 2):
                x, y = pts[i]
                n = math.atan2(y - 0.55, x)
                lashes.append(place([(x, y), (x + 0.22 * math.cos(n), y + 0.22 * math.sin(n))], (bx, by), ang + sg * 18, s, s))
            sc.add([out + [out[0]]] + lashes, out + [out[0]])
    moss = wave(-1.3, 1.3, -0.95, 0.08, 4, 40)
    add_pot(sc, pot_terra(0, -0.8, 2.6, 2.0))
    sc.add([moss, floor()])
    return make("Venus Flytrap", sc.s)


@design("houseplants_lucky_bamboo", T)
def lucky_bamboo(rng):
    sc = Scene()
    for x, top in [(-0.6, 2.4), (0.0, 3.1), (0.6, 1.8)]:
        c = rect(x - 0.15, -2.2, x + 0.15, top)
        nodes = [[(x - 0.15, y), (x + 0.15, y)] for y in [-1.2 + 0.9 * k for k in range(6) if -1.2 + 0.9 * k < top - 0.3]]
        sc.add([c] + nodes, c)
        for a in (60, 120):
            p, o = leaf("lance", (x, top - 0.3), a, 0.9, 0.35, rib=0.7)
            sc.add(p, o)
    curl = [(1.4 + 0.5 * math.sin(2.5 * y), y) for y in [-2.2 + 3.6 * i / 60 for i in range(61)]]
    cb = tube(curl, 0.28)
    sc.add([cb], cb)
    p, o = leaf("lance", curl[-1], 100, 0.9, 0.35)
    sc.add(p, o)
    vase = chain([(-1.3, 0.0), (-1.3, -2.9), (1.3 + 0.9, -2.9)][:2], [(1.3, -2.9), (1.3, 0.0)])
    vase = [(-1.6, 0.0), (-1.6, -2.9), (2.2, -2.9), (2.2, 0.0)]
    peb = [stone(x, y, 0.28, 0.17) for x, y in [(-1.2, -2.6), (-0.5, -2.6), (0.2, -2.6), (0.9, -2.6), (1.7, -2.6), (-0.85, -2.2), (0.55, -2.2), (1.3, -2.2)]]
    water = wave(-1.6, 2.2, -0.9, 0.06, 4, 40)
    ribbon = [rect(-0.85, -0.5, 1.75, -0.2)]
    sc.add(ribbon, ribbon[:1])
    sc.add([vase, ellipse(0.3, 0.0, 1.9, 0.2, 40), water] + peb)
    return make("Lucky Bamboo in a Glass Vase", sc.s)


@design("houseplants_money_tree", T)
def money_tree(rng):
    sc = Scene()
    for k in range(3):
        ph = k * TAU / 3
        tr = [(0.3 * math.sin(4 * y + ph), y) for y in [-0.9 + 2.3 * i / 40 for i in range(41)]]
        sc.add([tube(tr, 0.2)])
    for (x, y), a0 in [((-1.5, 2.2), 0), ((1.4, 2.4), 10), ((0.0, 2.9), 5), ((-0.6, 1.7), 15), ((0.8, 1.6), -10)]:
        sc.add([quad((0, 1.4), (x * 0.5, 1.6 + 0.3), (x, y), 10)])
        for k in range(5):
            a = 90 + a0 + (k - 2) * 45
            p, o = leaf("lance", (x, y), a, 0.85, 0.45, rib=0.8)
            sc.add(p, o)
    add_pot(sc, pot_round(0, -0.85, 2.4, 2.0))
    sc.add([floor()])
    return make("Braided Money Tree", sc.s)


@design("houseplants_agave", T)
def agave(rng):
    sc = Scene()
    for a, L, W in [(170, 2.3, 0.85), (10, 2.3, 0.85), (145, 2.6, 0.95), (35, 2.6, 0.95), (115, 2.8, 1.0), (65, 2.8, 1.0), (92, 2.4, 0.9)]:
        r = math.radians(a)
        base = (0.2 * math.cos(r), -0.9)
        side = SIDES["lance"]()
        teeth = []
        for i, (x, y) in enumerate(side):
            teeth.append((x * (1.12 if i % 4 == 2 and 3 < i < 23 else 1.0), y))
        o = place(outline_of(teeth), base, a, L, W)
        spine = place([(0, 1.0), (0, 1.12)], base, a, L, W)
        rib = place([(0, 0.1), (0, 0.8)], base, a, L, W)
        sc.add([o, spine, rib], o)
    pot = pot_bowl(0, -0.8, 3.0, 1.9)
    add_pot(sc, pot)
    sc.add([floor(-2.7)])
    return make("Blue Agave Succulent", sc.s)


@design("houseplants_fishbone_cactus", T)
def fishbone_cactus(rng):
    sc = Scene()
    for x3, y3, c1 in [(-2.6, -2.6, (-2.4, 0.8)), (2.7, -2.3, (2.4, 0.9)), (-1.2, 2.8, (-0.5, 1.6)), (1.3, 3.0, (0.7, 1.7))]:
        mid = cubic((0, -0.7), c1, (x3 * 0.9, y3 * 0.5), (x3, y3), 90)
        L = _plen(mid)
        left, right, acc = [], [], 0.0
        for i, p in enumerate(mid):
            if i:
                acc += math.dist(mid[i - 1], p)
            a = math.radians(tangent(mid, i) + 90)
            fr = (acc / 0.9) % 1.0
            ph = 1 - 4 * abs(fr - 0.5)
            taper = 1.0 if acc < L - 0.3 else max(0.2, (L - acc) / 0.3)
            wl = (0.08 + 0.4 * max(0.0, ph)) * taper
            wr = (0.08 + 0.4 * max(0.0, -ph)) * taper
            left.append((p[0] + wl * math.cos(a), p[1] + wl * math.sin(a)))
            right.append((p[0] - wr * math.cos(a), p[1] - wr * math.sin(a)))
        o = left + right[::-1] + [left[0]]
        sc.add([o, mid[3:-6]], o)
    add_pot(sc, pot_round(0, -0.6, 2.0, 1.6))
    return make("Fishbone Zigzag Cactus", sc.s)


@design("houseplants_ponytail_palm", T)
def ponytail_palm(rng):
    sc = Scene()
    for a in (100, 80, 120, 60, 140, 40, 160, 20):
        r = math.radians(a)
        p0 = (0.15 * math.cos(r), 1.4)
        p1 = (p0[0] + 0.9 * math.cos(r), 2.6)
        p3 = (p0[0] + 2.6 * math.cos(r) + 0.3 * math.copysign(1, math.cos(r)), 2.6 - 3.3 * (1 - abs(math.sin(r))) - 0.8)
        b = blade(cubic(p0, p1, (p3[0], p1[1] + 0.3), p3, 30), 0.18, 0.02)
        sc.add([b], b)
    trunk = chain([(-0.2, 1.4)], cubic((-0.2, 1.4), (-0.25, 0.4), (-1.3, 0.1), (-1.2, -0.7), 20)[1:], [(1.2, -0.7)], cubic((1.2, -0.7), (1.3, 0.1), (0.25, 0.4), (0.2, 1.4), 20)[1:])
    rings = [quad((-0.25, 1.0), (0, 0.9), (0.25, 1.0), 6), quad((-0.7, 0.3), (0, 0.15), (0.7, 0.3), 8), quad((-1.1, -0.3), (0, -0.45), (1.1, -0.3), 8)]
    sc.add([trunk + [trunk[0]]] + rings, trunk + [trunk[0]])
    add_pot(sc, pot_bowl(0, -0.65, 3.2, 1.8))
    sc.add([floor(-2.45)])
    return make("Ponytail Palm", sc.s)
