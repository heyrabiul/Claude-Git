"""Autumn niche, part 2 (pictures 10-55)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "autumn"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ------------------------------------------------------------ helpers

def dense(pts, step=0.04):
    """Resample a polyline so that no segment is longer than `step`."""
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        d = math.dist(a, b)
        k = max(1, int(d / step))
        for i in range(1, k + 1):
            out.append((a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k))
    return out


def clip(pts, keep):
    """Split a polyline into the runs whose points satisfy keep(p)."""
    out, cur = [], []
    for p in dense(pts):
        if keep(p):
            cur.append(p)
        else:
            if len(cur) > 1:
                out.append(cur)
            cur = []
    if len(cur) > 1:
        out.append(cur)
    return out


def outside(circles, margin=0.04):
    return lambda p: all(math.hypot(p[0] - x, p[1] - y) > r + margin for x, y, r in circles)


def inside_poly(pg):
    """Point-in-polygon test for a closed outline."""
    def f(p):
        x, y = p
        c = False
        for (x0, y0), (x1, y1) in zip(pg, pg[1:] + pg[:1]):
            if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
                c = not c
        return c
    return f


def hide(strokes, *outlines):
    """Clip strokes so nothing shows inside any of the given closed outlines."""
    tests = [inside_poly(o) for o in outlines]
    out = []
    for s in strokes:
        out += clip(s, lambda p: not any(t(p) for t in tests))
    return out


def smooth(pts, n=8, closed=False):
    """Catmull-Rom spline through the points."""
    P = list(pts)
    if closed:
        P = P[:-1] if math.dist(P[0], P[-1]) < 1e-9 else P
        ext = [P[-1]] + P + [P[0], P[1]]
        segs = len(P)
    else:
        ext = [P[0]] + P + [P[-1]]
        segs = len(P) - 1
    out = []
    for i in range(segs):
        p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(2)))
    out.append(ext[segs + 1] if not closed else out[0])
    return out


def yat(pts, x):
    """y of a roughly x-monotone polyline at x."""
    for a, b in zip(pts, pts[1:]):
        if min(a[0], b[0]) <= x <= max(a[0], b[0]) and a[0] != b[0]:
            return a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0])
    return pts[-1][1]


_MAPLE_PTS = [(0, 2.0), (0.2, 1.62), (0.42, 1.78), (0.38, 1.35), (0.55, 1.4), (0.4, 1.05), (0.32, 0.88), (0.6, 0.98),
              (0.75, 1.2), (0.95, 1.05), (1.55, 1.25), (1.3, 0.85), (1.5, 0.72), (1.1, 0.5), (0.75, 0.3), (0.55, 0.15),
              (0.75, 0.0), (1.05, -0.3), (0.7, -0.25), (0.35, -0.2), (0.12, -0.05), (0, 0)]
_MAPLE_R = [(0.5 * x, 0.5 * y - 0.2) for x, y in _MAPLE_PTS]


def maple(cx, cy, s, rot=0.0, veins=True):
    """Maple leaf; (cx, cy) is near the base of the blade, tip points along rot (0 = up)."""
    outline = chain(_MAPLE_R, [(-x, y) for x, y in reversed(_MAPLE_R[:-1])])
    parts = [outline, [(0, -0.2), (0.03, -0.62)]]
    if veins:
        parts += [[(0, -0.2), (0, 0.68)], [(0, -0.2), (0.66, 0.36)], [(0, -0.2), (-0.66, 0.36)],
                  [(0, -0.2), (0.44, -0.31)], [(0, -0.2), (-0.44, -0.31)]]
    return [transform(p, dx=cx, dy=cy, s=s, rot=rot) for p in parts]


def oak(cx, cy, s, rot=0.0):
    pts = []
    for i in range(121):
        t = i / 120
        pts.append((0.55 * math.sin(math.pi * t) * (1 + 0.3 * math.sin(10 * math.pi * t)), -1 + 2 * t))
    leaf = chain(pts, mirror_x(pts)[::-1])
    parts = [leaf, [(0, -1), (0.05, -1.35)], [(0, -1), (0, 0.85)]]
    return [transform(p, dx=cx, dy=cy, s=s, rot=rot) for p in parts]


def leaf(x, y, L, ang, bulge=0.33):
    """Simple almond leaf with a midrib, from (x, y) in direction ang."""
    tip = (x + L * math.cos(ang), y + L * math.sin(ang))
    mid = (x + 0.8 * L * math.cos(ang), y + 0.8 * L * math.sin(ang))
    return [lens((x, y), tip, bulge), [(x, y), mid]]


def apple(cx, cy, r, stem=True, leafy=True):
    def rf(t):
        return (1 + 0.05 * math.cos(2 * t) - 0.3 * math.exp(-((t - math.pi / 2) / 0.3) ** 2)
                - 0.1 * math.exp(-((t - 1.5 * math.pi) / 0.35) ** 2))
    out = [[(cx + r * rf(t) * math.cos(t) * (1 - 0.08 * max(0.0, -math.sin(t))), cy + 0.95 * r * rf(t) * math.sin(t))
            for t in [math.pi / 2 + TAU * i / 90 for i in range(91)]]]
    if stem:
        out.append(quad((cx, cy + 0.68 * r), (cx + 0.02 * r, cy + 1.0 * r), (cx + 0.18 * r, cy + 1.25 * r), 8))
    if leafy:
        out.append(lens((cx + 0.08 * r, cy + 1.02 * r), (cx + 0.75 * r, cy + 1.3 * r), 0.35))
    return out


def pumpkin(cx, cy, s, tall=1.0):
    out = [ellipse(cx, cy, 0.62 * s, 1.0 * s * tall, 70)]
    for dx, rx in [(0.5, 0.72), (0.95, 0.62)]:
        half = [(cx + (dx + rx * math.cos(t)) * s, cy + 0.95 * s * tall * math.sin(t)) for t in [-math.pi / 2 + math.pi * i / 40 for i in range(41)]]
        out += [half, mirror_x(half, cx)]
    out.append(poly((cx - 0.12 * s, cy + 0.95 * s * tall), (cx - 0.22 * s, cy + (0.95 * tall + 0.45) * s),
                    (cx + 0.12 * s, cy + (0.95 * tall + 0.5) * s), (cx + 0.15 * s, cy + 0.95 * s * tall), closed=False))
    return out


def pumpkin_outline(cx, cy, s, tall=1.0):
    """Points inside the pumpkin, for clipping things behind it."""
    return lambda p: ((p[0] - cx) / (1.62 * s)) ** 2 + ((p[1] - cy) / (1.0 * s * tall)) ** 2 > 1.05


def acorn(cx, cy, s, rot=0.0):
    nut = chain(cubic((-0.5, 0.0), (-0.58, -0.6), (-0.2, -0.95), (0.0, -1.1), 16),
                cubic((0.0, -1.1), (0.2, -0.95), (0.58, -0.6), (0.5, 0.0), 16))
    cap = chain([(-0.6, 0.0)], arc(0, 0.0, 0.6, math.pi, 0, 24), [(0.6, 0.0)], quad((0.6, 0.0), (0, -0.14), (-0.6, 0.0), 12))
    hatch = [arc(0, -0.5, 0.85, math.radians(70), math.radians(110), 8), arc(0, -0.75, 0.95, math.radians(62), math.radians(118), 10)]
    st = [(0.0, 0.6), (0.12, 0.88)]
    return [transform(p, dx=cx, dy=cy, s=s, rot=rot) for p in [nut, cap, st] + hatch]


def bumpy(cx, cy, rx, ry, k, a=0.13, n=None, rot=0.0):
    """Scalloped cloud / tree-crown outline with k bumps."""
    n = n or k * 14
    pts = []
    for i in range(n + 1):
        t = rot + TAU * i / n
        r = 1 - a * (1 - abs(math.sin(k * (t - rot) / 2)))
        pts.append((cx + rx * r * math.cos(t), cy + ry * r * math.sin(t)))
    return pts


def serrate(pts, amp=0.06):
    """Saw-tooth edge on a closed outline (alternate points pushed outward)."""
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    out = []
    for i, (x, y) in enumerate(pts):
        if i % 2:
            dx, dy = x - cx, y - cy
            L = math.hypot(dx, dy) or 1
            x, y = x + amp * dx / L, y + amp * dy / L
        out.append((x, y))
    out[-1] = out[0]
    return out


def tree(cx, base, h, rx, ry, k=10):
    """Simple round-crowned tree."""
    top = base + h
    trunk = [quad((cx - 0.18 * rx, base), (cx - 0.12 * rx, base + 0.5 * h), (cx - 0.08 * rx, top - 0.3 * ry), 12),
             quad((cx + 0.18 * rx, base), (cx + 0.12 * rx, base + 0.5 * h), (cx + 0.08 * rx, top - 0.3 * ry), 12)]
    crown = bumpy(cx, top + 0.55 * ry, rx, ry, k)
    return trunk + [crown]


def crow(x, y, s):
    return chain(quad((x - s, y + 0.3 * s), (x - 0.5 * s, y + 0.35 * s), (x, y), 8), quad((x, y), (x + 0.5 * s, y + 0.35 * s), (x + s, y + 0.3 * s), 8))


# ------------------------------------------------------------ leaves & trees

@design("autumn_maple_leaf", T)
def maple_leaf(rng):
    big = maple(0, -0.6, 3.2)
    side = []
    for sx in (1, -1):
        for a, b in [((0.0, 0.25), (0.3, 0.55)), ((0.0, 0.12), (0.36, 0.25)), ((0.25, 0.25), (0.25, 0.48))]:
            side.append(transform([(sx * a[0] + sx * 0.12, a[1]), (sx * a[0] + sx * 0.12 + sx * (b[0] - a[0]) * 0.6, b[1])], dy=-0.6, s=3.2))
    drops = [lens((x, y), (x + 0.25, y - 0.35), 0.4) for x, y in [(-2.9, -1.6), (2.6, -1.9)]]
    return make("Sugar Maple Leaf", big + drops)


def ginkgo(cx, cy, s, rot=0.0):
    R = 1.0
    left = [(R * math.cos(a), R * math.sin(a)) for a in [math.radians(150 - 52 * i / 20) for i in range(21)]]
    right = [(R * math.cos(a), R * math.sin(a)) for a in [math.radians(82 - 52 * i / 20) for i in range(21)]]
    left = [(x * (1 + 0.04 * math.sin(i * 1.7)), y * (1 + 0.04 * math.sin(i * 1.7))) for i, (x, y) in enumerate(left)]
    right = [(x * (1 + 0.04 * math.sin(i * 1.3)), y * (1 + 0.04 * math.sin(i * 1.3))) for i, (x, y) in enumerate(right)]
    blade = chain([(0.0, 0.0)], quad((0, 0), (-0.25, 0.25), left[0], 10), left, [(0.0, 0.62)], right,
                  quad(right[-1], (0.25, 0.25), (0, 0), 10))
    veins = [[(0.0, 0.05), (0.75 * math.cos(math.radians(a)), 0.75 * math.sin(math.radians(a)))] for a in (55, 72, 108, 125)]
    stem = quad((0, 0), (0.05, -0.4), (-0.05, -0.75), 10)
    return [transform(p, dx=cx, dy=cy, s=s, rot=rot) for p in [blade, stem] + veins]


@design("autumn_ginkgo_leaves", T)
def ginkgo_leaves(rng):
    out = ginkgo(-0.9, 0.2, 2.4, 0.35) + ginkgo(1.2, -0.6, 2.0, -0.45) + ginkgo(0.3, -2.0, 1.3, 0.0)
    small = ginkgo(-2.5, -2.2, 0.8, 0.9) + ginkgo(2.4, 2.0, 0.8, -1.0)
    return make("Golden Ginkgo Leaves", out + small)


@design("autumn_falling_leaves", T)
def falling_leaves(rng):
    lv = maple(-1.4, 1.0, 1.4, 0.4) + oak(1.6, 1.6, 1.1, -0.7) + ginkgo(1.4, -1.4, 1.2, 0.5)
    birch = serrate(lens((-2.4, -2.4), (-1.0, -1.2), 0.32, 40), 0.07)
    lv += [birch, [(-2.4, -2.4), (-1.3, -1.45)], [(-2.4, -2.4), (-2.7, -2.7)]]
    lv += maple(-0.2, -1.6, 0.6, -0.8)
    gusts = [gust(-3.1, -0.05, 0.4, 0.15, 0.28), gust(-3.2, 2.6, -2.2, 3.0, 0.22)]
    swirl = [spiral(2.6, -2.4, 0.05, 0.5, 1.2)]
    return make("Swirl of Falling Leaves", lv + gusts + swirl)


@design("autumn_leaf_pile_rake", T)
def leaf_pile_rake(rng):
    top = [(x, -2.6 + 1.7 * math.sqrt(max(0.0, 1 - ((x + 0.9) / 2.2) ** 2)) * (1 + 0.06 * abs(math.sin(9 * x))))
           for x in [-3.1 + 4.4 * i / 120 for i in range(121)]]
    pile = top
    ground = [[(-3.4, -2.6), (3.4, -2.6)]]
    inside = maple(-1.6, -1.8, 0.55, 0.3, False) + maple(0.0, -2.1, 0.5, -0.4, False)
    inside += [lens((-2.4, -2.3), (-1.9, -2.0), 0.4), lens((-0.9, -1.0), (-0.4, -0.75), 0.4), lens((-0.6, -2.4), (-0.1, -2.5), 0.4)]
    head = [[(1.25 + 0.06 * k, -1.55), (0.55 + 0.25 * k, -2.55)] for k in range(9)]
    brace = [quad((0.75, -2.15), (1.55, -2.05), (2.35, -2.15), 12)]
    handle = [[(1.47, -1.55), (2.9, 2.8)], [(1.73, -1.55), (3.1, 2.7)]]
    neck = [[(1.25, -1.55), (1.73, -1.55)]]
    falling = maple(-2.3, 1.4, 0.6, 0.6) + maple(0.4, 2.0, 0.55, -0.5) + [lens((-0.8, 0.6), (-0.4, 0.3), 0.4)]
    return make("Leaf Pile and Rake", [pile] + ground + inside + head + brace + handle + neck + falling)


@design("autumn_apple_tree", T)
def apple_tree(rng):
    trunk = [chain(quad((-1.0, -2.6), (-0.4, -2.3), (-0.4, -1.2), 10), quad((-0.4, -1.2), (-0.4, -0.6), (-1.3, 0.4), 10)),
             chain(quad((1.0, -2.6), (0.4, -2.3), (0.4, -1.2), 10), quad((0.4, -1.2), (0.4, -0.5), (1.3, 0.5), 10)),
             [(0.0, -0.9), (0.1, 0.6)]]
    crown = bumpy(0, 1.0, 3.0, 1.9, 16, 0.1)
    apples = []
    for x, y in [(-2.0, 1.2), (-1.0, 2.0), (0.2, 2.2), (1.4, 1.8), (2.2, 0.9), (-1.8, 0.0), (0.9, 0.6), (-0.6, 1.0), (1.8, -0.2), (-0.5, -0.2)]:
        apples.append(circle(x, y, 0.24, 20))
        apples.append([(x, y + 0.24), (x + 0.06, y + 0.4)])
    fallen = [a for x in (-2.2, 1.9, 2.6) for a in apple(x, -2.35, 0.28, leafy=False)]
    grass = [zigzag(-3.2, -1.1, -2.6, 0.08, 9), zigzag(1.1, 3.2, -2.6, 0.08, 9)]
    return make("Apple Tree Laden with Fruit", trunk + [crown] + apples + fallen + grass)


@design("autumn_acorn_twig", T)
def acorn_twig(rng):
    twig = [quad((-3.2, 1.9), (0.0, 0.8), (3.2, 1.6), 30)]
    leaves = oak(-1.3, 2.4, 1.0, 0.6) + oak(1.6, 2.6, 1.05, -0.5) + oak(0.3, 2.9, 0.85, 0.05)
    nuts = acorn(-1.6, 0.1, 1.2, 0.15) + acorn(0.4, -0.7, 1.4, -0.05) + acorn(2.2, 0.2, 1.1, -0.25)
    stems = [[(-1.68, 0.84), (-1.55, 1.25)], [(0.37, 0.15), (0.3, 1.2)], [(2.07, 0.86), (1.9, 1.35)]]
    fallen = acorn(-2.5, -2.3, 0.7, 1.4) + [ellipse(1.8, -2.75, 0.55, 0.18, 24)]
    return make("Acorns on an Oak Twig", twig + leaves + nuts + stems + fallen)


def chestnut(cx, cy, s, rot=0.0):
    body = chain(cubic((-1, -0.4), (-1.1, 0.5), (-0.4, 0.9), (0, 1.15), 20), cubic((0, 1.15), (0.4, 0.9), (1.1, 0.5), (1, -0.4), 20),
                 quad((1, -0.4), (0, -1.0), (-1, -0.4), 16))
    hilum = quad((-0.85, -0.25), (0, -0.55), (0.85, -0.25), 14)
    shine = quad((-0.6, 0.3), (-0.5, 0.7), (-0.15, 0.85), 8)
    tip = [(0, 1.15), (0.05, 1.4)]
    return [transform(p, dx=cx, dy=cy, s=s, rot=rot) for p in [body, hilum, shine, tip]]


@design("autumn_chestnuts", T)
def chestnuts(rng):
    cx, cy, R, ry = -0.9, -0.6, 1.5, 0.4
    bowl = [(cx + (R + (0.35 if i % 2 else 0.0)) * math.cos(a), cy + 0.9 * (R + (0.35 if i % 2 else 0.0)) * math.sin(a))
            for i, a in enumerate([math.pi + math.pi * k / 30 for k in range(31)])]
    n1 = chestnut(cx - 0.5, cy + 0.6, 0.62, 0.25)
    n2 = chestnut(cx + 0.55, cy + 0.62, 0.68, -0.2)
    nuts = hide(n1, n2[0]) + n2
    rim = hide([ellipse(cx, cy, R, ry, 90)], n1[0], n2[0])
    dome = [(2.1 + (0.9 + (0.3 if i % 2 else 0.0)) * math.cos(a), -2.3 + (0.9 + (0.3 if i % 2 else 0.0)) * math.sin(a))
            for i, a in enumerate([math.pi * k / 20 for k in range(21)])]
    dome_base = [quad((1.2, -2.3), (2.1, -2.5), (3.0, -2.3), 12)]
    loose = chestnut(2.5, -0.35, 0.5, 0.4)
    leaflets = []
    for a, L in [(20, 1.6), (55, 1.9), (90, 2.0), (125, 1.9), (160, 1.6)]:
        a = math.radians(a)
        p0 = (0.9 + 0.15 * math.cos(a), 1.3 + 0.15 * math.sin(a))
        p1 = (0.9 + L * math.cos(a), 1.3 + L * math.sin(a))
        leaflets += [serrate(lens(p0, p1, 0.17, 30), 0.06), [p0, (0.9 + 0.85 * L * math.cos(a), 1.3 + 0.85 * L * math.sin(a))]]
    stalk = [quad((0.9, 1.3), (1.3, 0.9), (1.5, 0.5), 8)]
    ground = [[(-3.2, -2.35), (1.0, -2.35)], [(3.2, -2.35), (3.4, -2.35)]]
    return make("Chestnuts and Spiky Husk", [bowl] + nuts + rim + [dome] + dome_base + loose + leaflets + stalk + ground[:1])


@design("autumn_windy_day", T)
def windy_day(rng):
    crown = transform(bumpy(0, 0, 2.0, 1.2, 13, 0.12), dx=0.4, dy=1.3, rot=-0.2)
    trunk = hide([quad((-1.9, -2.6), (-1.6, -0.6), (-0.5, 0.8), 16), quad((-1.2, -2.6), (-1.0, -1.0), (0.2, 0.5), 16),
                  [(-1.15, -0.4), (-1.9, 0.6)]], crown)
    gusts = [gust(-3.4, 2.2, -2.2, 2.7, 0.3), gust(-3.4, 0.0, -2.4, 0.3, 0.25), gust(0.0, -1.0, 2.2, -0.8, 0.3), gust(1.0, 3.0, 2.6, 3.1, 0.25)]
    blown = maple(3.0, 1.4, 0.45, -1.2) + maple(3.2, 0.0, 0.4, -2.0) + maple(1.2, -2.2, 0.4, -0.6) + maple(-0.4, -1.7, 0.35, 0.8, False)
    blown += [lens((2.7, 2.4), (3.1, 2.2), 0.4), lens((2.6, -1.6), (3.0, -1.5), 0.4), lens((-0.6, 3.0), (-0.2, 3.1), 0.4)]
    grass = [poly(*[(x + (0.3 if k % 2 else 0), -2.6 + (0.4 if k % 2 else 0)) for k, x in enumerate([-3.4 + 0.4 * i for i in range(18)])], closed=False)]
    return make("Windy Autumn Day", trunk + [crown] + gusts + blown + grass)


@design("autumn_forest_path", T)
def forest_path(rng):
    path = [cubic((-2.0, -3.0), (-0.6, -1.6), (0.8, -0.6), (-0.1, 0.6), 30), cubic((1.4, -3.0), (2.0, -1.4), (1.1, -0.4), (0.25, 0.6), 30)]
    big = tree(-2.6, -2.8, 3.6, 1.0, 1.0, 10) + tree(2.6, -2.6, 3.4, 1.0, 1.0, 10)
    small = tree(-0.9, 0.5, 0.5, 0.45, 0.45, 8) + tree(1.15, 0.55, 0.55, 0.5, 0.5, 8)
    hills = [quad((-2.42, 0.4), (-1.6, 0.7), (-0.1, 0.6), 16), quad((0.25, 0.6), (1.4, 0.75), (2.42, 0.45), 16)]
    hills = hide(hills, small[2], small[5]) + []
    leaves = [lens((x, y), (x + 0.35, y + 0.1), 0.4) for x, y in [(-0.9, -2.4), (0.5, -1.7), (0.2, -0.5), (0.4, -2.6), (-0.3, -1.4)]]
    falling = maple(-0.5, 2.4, 0.4, 0.4) + maple(0.8, 2.0, 0.35, -0.6) + maple(-1.7, -0.5, 0.35, 1.0)
    ground = maple(-3.2, -2.9, 0.35, 1.4, False) + maple(2.9, -2.8, 0.35, -1.2, False)
    return make("Forest Path in Fall", path + big + small + hills + leaves + falling + ground)


# ------------------------------------------------------------ animals

@design("autumn_owl_hollow", T)
def owl_hollow(rng):
    trunk = [quad((-2.0, -3.0), (-1.7, 0.0), (-2.0, 3.0), 30), quad((2.0, -3.0), (1.7, 0.0), (2.0, 3.0), 30)]
    bark = [quad((-1.6, 2.6), (-1.5, 2.0), (-1.65, 1.5), 8), quad((1.55, -2.0), (1.45, -2.4), (1.6, -2.9), 8), quad((-1.5, -2.2), (-1.4, -2.6), (-1.6, -2.9), 8)]
    hollow = [ellipse(0, 0.2, 1.2, 1.6, 90), ellipse(0, 0.2, 1.42, 1.85, 100)]
    yb = 0.2 - 1.6 * math.sqrt(1 - (0.9 / 1.2) ** 2)
    head = chain([(-0.9, yb), (-0.95, 0.6), (-0.95, 1.3)], quad((-0.95, 1.3), (-0.7, 1.05), (-0.45, 1.0), 6),
                 quad((-0.45, 1.0), (0, 1.15), (0.45, 1.0), 10), quad((0.45, 1.0), (0.7, 1.05), (0.95, 1.3), 6), [(0.95, 0.6), (0.9, yb)])
    eyes_ = [circle(-0.4, 0.45, 0.3, 24), circle(0.4, 0.45, 0.3, 24)]
    beak = poly((-0.12, 0.15), (0, -0.15), (0.12, 0.15))
    wings = [quad((-0.9, 0.0), (-0.45, -0.3), (-0.55, yb + 0.05), 10), quad((0.9, 0.0), (0.45, -0.3), (0.55, yb + 0.05), 10)]
    chest = [arc(x, y, 0.13, math.radians(200), math.radians(340), 6) for x, y in [(-0.2, -0.45), (0.2, -0.45), (0.0, -0.7)]]
    branch = [[(2.0, -1.2), (3.2, -0.8)], [(1.9, -1.55), (3.2, -1.2)]]
    leaves = maple(2.9, -0.65, 0.4, -0.3, False) + leaf(2.5, -1.4, 0.6, -0.8) + maple(-2.6, 2.0, 0.45, 0.5) + maple(2.7, 2.3, 0.4, -0.4)
    return make("Owl in a Tree Hollow", trunk + bark + hollow + [head, beak] + eyes_ + wings + chest + branch + leaves,
                [eye(-0.4, 0.45, 0.12), eye(0.4, 0.45, 0.12)])


@design("autumn_sitting_fox", T)
def sitting_fox(rng):
    half = [(0, 0.62), (-0.3, 0.72), (-0.65, 0.95), (-1.0, 1.0), (-0.9, 1.15), (-1.45, 1.35), (-1.1, 1.5), (-1.15, 1.95),
            (-1.05, 2.95), (-0.45, 2.25)]
    head = chain(half, quad((-0.45, 2.25), (0, 2.42), (0.45, 2.25), 10), [(-x, y) for x, y in reversed(half)])
    ears = [poly((-0.95, 2.1), (-0.98, 2.65), (-0.6, 2.25), closed=False), poly((0.95, 2.1), (0.98, 2.65), (0.6, 2.25), closed=False)]
    nose = ellipse(0, 0.78, 0.15, 0.1, 14)
    muzzle = [quad((-0.75, 1.2), (-0.4, 1.25), (-0.15, 0.85), 8), quad((0.75, 1.2), (0.4, 1.25), (0.15, 0.85), 8)]
    body = [cubic((-0.62, 0.95), (-1.3, 0.2), (-1.6, -1.6), (-1.2, -2.5), 30), cubic((0.62, 0.95), (1.3, 0.2), (1.5, -1.4), (1.25, -2.3), 30)]
    base = [(-1.2, -2.5), (1.3, -2.5)]
    bib = quad((-0.55, 0.85), (0, -0.6), (0.55, 0.85), 16)
    legs = [[(-0.45, -0.4), (-0.45, -2.3)], [(0.45, -0.4), (0.45, -2.3)], [(-0.05, -0.8), (-0.05, -2.3)], [(0.05, -0.8), (0.05, -2.3)]]
    paws = [ellipse(-0.25, -2.35, 0.3, 0.14, 16), ellipse(0.25, -2.35, 0.3, 0.14, 16)]
    tc = cubic((1.25, -2.15), (3.0, -2.6), (3.3, -0.4), (2.2, 0.8), 40)
    tail = tube(tc, lambda t: 0.25 + 0.85 * math.sin(math.pi * min(1.0, t * 1.1)) + 0.05, cap=False)
    tip = quad((tc[33][0] - 0.45, tc[33][1] - 0.1), (tc[33][0] + 0.05, tc[33][1] + 0.15), (tc[33][0] + 0.4, tc[33][1] - 0.25), 8)
    leaves = maple(-2.4, -2.5, 0.5, 0.9, False) + maple(-2.6, 0.8, 0.45, 0.3) + maple(2.4, 2.4, 0.45, -0.5)
    return make("Red Fox Among the Leaves", [head, nose, bib, base, tail, tip] + ears + muzzle + body + legs + paws + leaves,
                [eye(-0.48, 1.55, 0.1), eye(0.48, 1.55, 0.1)])


@design("autumn_stag", T)
def stag(rng):
    body = poly((-2.9, 1.9), (-2.45, 2.25), (-1.95, 2.5), (-1.6, 2.85), (-1.42, 2.55), (-1.45, 2.3), (-1.1, 1.6), (-0.6, 1.0),
                (0.6, 1.1), (1.5, 1.05), (2.2, 0.9), (2.45, 1.05), (2.4, 0.6), (2.25, 0.15), (2.15, -0.4), (2.25, -1.2), (2.2, -2.6),
                (1.98, -2.6), (1.92, -1.3), (1.62, -0.5), (1.3, -0.3), (-0.4, -0.3), (-0.7, -0.5), (-0.75, -2.6), (-0.97, -2.6),
                (-1.05, -0.6), (-1.25, 0.0), (-1.45, 0.6), (-1.75, 1.15), (-2.3, 1.55), (-2.75, 1.68))
    far_legs = [[(-0.3, -0.3), (-0.1, -1.4), (0.15, -2.5), (-0.05, -2.5), (-0.3, -1.4), (-0.5, -0.4)],
                [(1.25, -0.3), (1.05, -1.3), (0.9, -2.5), (1.1, -2.5), (1.3, -1.35), (1.55, -0.55)]]
    beam_l = cubic((-1.75, 2.62), (-2.1, 3.5), (-1.4, 4.3), (-0.5, 4.5), 30)
    beam_r = cubic((-1.55, 2.66), (-1.6, 3.3), (-0.9, 3.9), (-0.1, 3.95), 30)
    tines = [[beam_l[8], (-2.4, 3.5)], [beam_l[15], (-1.95, 4.4)], [beam_l[22], (-1.2, 4.95)],
             [beam_r[10], (-1.15, 3.95)], [beam_r[19], (-0.7, 4.3)]]
    ground = [[(-3.4, -2.6), (3.2, -2.6)]]
    spots = [quad((-0.2, 0.7), (0.6, 0.5), (1.4, 0.75), 10)]
    leaves = maple(2.6, 3.4, 0.5, -0.4) + maple(0.8, 2.9, 0.4, 0.5) + maple(-2.7, -2.4, 0.4, 1.2, False) + maple(2.9, -2.4, 0.4, -1.0, False)
    return make("Stag with Antlers", [body, beam_l, beam_r] + far_legs + tines + ground + spots + leaves, [eye(-2.05, 2.15, 0.08)])


@design("autumn_chipmunk", T)
def chipmunk(rng):
    head = [(1.15 * math.cos(t) * (1 + 0.12 * math.cos(2 * t)), 1.35 + 0.85 * math.sin(t) * (1 - 0.1 * math.sin(t))) for t in [TAU * i / 100 for i in range(101)]]
    ears = [arc(-0.62, 2.12, 0.25, math.radians(10), math.radians(200), 12), arc(0.62, 2.12, 0.25, math.radians(-20), math.radians(170), 12)]
    stripes = [[(0, 2.1), (0, 1.55)], quad((-0.25, 1.62), (-0.6, 1.75), (-0.95, 1.6), 8), quad((0.25, 1.62), (0.6, 1.75), (0.95, 1.6), 8)]
    nose = ellipse(0, 1.15, 0.13, 0.09, 12)
    mouth = [quad((0, 1.06), (-0.12, 0.88), (-0.28, 0.95), 6), quad((0, 1.06), (0.12, 0.88), (0.28, 0.95), 6)]
    whisk = [[(-0.45, 1.1), (-1.0, 1.2)], [(0.45, 1.1), (1.0, 1.2)]]
    body = [cubic((-0.6, 0.62), (-1.4, 0.2), (-1.4, -1.6), (-0.6, -1.85), 30), cubic((0.6, 0.62), (1.4, 0.2), (1.4, -1.6), (0.6, -1.85), 30),
            [(-0.6, -1.85), (0.6, -1.85)]]
    side_stripes = [quad((-1.0, 0.0), (-1.15, -0.7), (-0.95, -1.4), 10), quad((1.0, 0.0), (1.15, -0.7), (0.95, -1.4), 10)]
    nut = acorn(0, -0.25, 0.55)
    paws = [ellipse(-0.42, -0.1, 0.18, 0.13, 12), ellipse(0.42, -0.1, 0.18, 0.13, 12)]
    tc = cubic((1.05, -1.5), (3.0, -1.3), (1.4, 0.9), (2.5, 2.4), 40)
    tail = tube(tc, lambda t: 0.3 + 0.45 * math.sin(math.pi * t) ** 0.7, cap=False)
    log = [rrect(-2.8, -2.95, 2.4, -1.85, 0.2), ellipse(2.4, -2.4, 0.3, 0.55, 30), ellipse(2.4, -2.4, 0.12, 0.25, 16)]
    bark = [[(-2.2, -2.3), (-1.2, -2.3)], [(0.2, -2.55), (1.4, -2.55)]]
    return make("Chipmunk on a Log", [head, nose, tail] + ears + stripes + mouth + whisk + body + side_stripes + nut + paws + log + bark,
                [eye(-0.42, 1.48, 0.1), eye(0.42, 1.48, 0.1)])


@design("autumn_raccoon", T)
def raccoon(rng):
    half = [(0, 0.7), (-0.5, 0.85), (-1.1, 1.15), (-1.8, 1.35), (-1.35, 1.6), (-1.25, 2.05), (-1.15, 2.75), (-0.55, 2.35)]
    head = chain(half, quad((-0.55, 2.35), (0, 2.5), (0.55, 2.35), 10), [(-x, y) for x, y in reversed(half)])
    ears = [poly((-1.05, 2.25), (-1.05, 2.55), (-0.75, 2.35), closed=False), poly((1.05, 2.25), (1.05, 2.55), (0.75, 2.35), closed=False)]
    mask = [chain(quad((-0.12, 1.55), (-0.6, 2.05), (-1.4, 1.5), 14), quad((-1.4, 1.5), (-0.6, 1.05), (-0.12, 1.55), 14))]
    mask.append(mirror_x(mask[0]))
    brows = [quad((-0.25, 1.95), (-0.6, 2.2), (-1.0, 2.0), 8), quad((0.25, 1.95), (0.6, 2.2), (1.0, 2.0), 8)]
    stripe = [[(0, 1.65), (0, 2.35)]]
    nose = ellipse(0, 0.95, 0.18, 0.12, 14)
    body = [cubic((-0.75, 0.95), (-1.6, 0.0), (-1.7, -1.8), (-1.0, -2.4), 30), cubic((0.75, 0.95), (1.6, 0.0), (1.7, -1.8), (1.0, -2.4), 30)]
    base = [(-1.0, -2.4), (1.0, -2.4)]
    belly = ellipse(0, -1.2, 0.75, 1.0, 50)
    hands = [ellipse(-0.6, -0.1, 0.25, 0.15, 14, rot=-0.4), ellipse(0.6, -0.1, 0.25, 0.15, 14, rot=0.4)]
    tc = cubic((-1.2, -2.2), (-3.0, -2.4), (-3.2, -0.4), (-2.4, 0.6), 30)
    tail = tube(tc, 0.7, cap=False)
    rings = []
    tl = tube(tc, 0.7, cap=False)
    m = len(tc)
    for k in (8, 14, 20, 26):
        a, b = tl[k], tl[2 * m - 1 - k]
        rings.append([a, b])
    leaves = maple(2.4, -2.3, 0.5, -0.6, False) + maple(2.5, 1.6, 0.45, -0.3) + maple(-2.6, 2.6, 0.4, 0.4)
    return make("Masked Raccoon", [head, nose, belly, base, tail] + ears + mask + brows + stripe + body + hands + rings + leaves,
                [eye(-0.6, 1.55, 0.12), eye(0.6, 1.55, 0.12)])


def goose(x, y, s, up=True):
    if up:
        top = [(-0.7, 0.2), (-0.3, 0.35), (0.05, 0.85), (0.5, 1.35), (0.62, 1.2), (0.5, 0.65), (0.4, 0.25)]
    else:
        top = [(-0.7, 0.2), (-0.3, 0.2), (0.05, -0.35), (0.45, -0.85), (0.58, -0.7), (0.5, -0.2), (0.4, 0.22)]
    pts = [(-2.0, 0.33), (-1.82, 0.43), (-1.62, 0.38), (-1.2, 0.24)] + top + [(1.0, 0.17), (1.38, 0.12), (1.0, -0.04), (0.4, -0.22),
                                                                             (-0.4, -0.18), (-0.85, 0.02), (-1.25, 0.12), (-1.65, 0.24), (-1.8, 0.25)]
    pts = smooth(pts + [pts[0]], 5, closed=True)
    far = smooth([(-0.4, 0.3), (-0.2, 0.75), (0.1, 1.05), (0.2, 0.95), (0.1, 0.5)], 5) if up else []
    out = [transform(pts, dx=x, dy=y, s=s)]
    if far:
        out.append(transform(far, dx=x, dy=y, s=s))
    return out


@design("autumn_migrating_geese", T)
def migrating_geese(rng):
    geese = []
    for k, (x, y) in enumerate([(-2.0, 2.2), (-0.7, 1.6), (0.6, 1.0), (-0.7, 3.0), (0.6, 3.6), (1.9, 0.4), (1.9, 4.2)]):
        geese += goose(x, y, 0.62, k % 2 == 0)
    sun = arc(1.6, -1.0, 1.0, 0, math.pi, 30)
    hills = [quad((-3.4, -1.3), (-1.4, -0.2), (0.6, -1.0), 30), quad((0.2, -1.0), (2.0, -0.3), (3.4, -1.2), 30)]
    hills = hide(hills, sun + [(0.6, -1.0)])
    lake = [[(-3.4, -1.3), (3.4, -1.3)], [(-2.6, -1.8), (-1.2, -1.8)], [(0.6, -1.7), (2.4, -1.7)], [(-1.0, -2.2), (0.6, -2.2)]]
    reeds = [[(x, -2.9), (x + 0.1, -2.0)] for x in (-3.0, -2.8, -2.55)] + [ellipse(-2.68, -1.7, 0.08, 0.3, 12)]
    t = tree(2.8, -1.3, 1.2, 0.6, 0.7, 8)
    return make("Geese Flying South", geese + [sun] + hills + lake + reeds + t)


@design("autumn_quail", T)
def quail(rng):
    body = chain(cubic((-0.6, 1.0), (-2.0, 1.2), (-2.6, -0.4), (-1.0, -1.2), 30), quad((-1.0, -1.2), (0.8, -1.6), (1.6, -0.4), 20),
                 quad((1.6, -0.4), (1.9, 0.3), (1.35, 0.95), 10))
    head = chain(quad((1.35, 0.95), (1.7, 1.2), (1.75, 1.6), 8), arc(1.25, 1.6, 0.5, 0, math.pi * 0.9, 16), quad((0.76, 1.68), (0.5, 1.2), (-0.6, 1.0), 10))
    beak = poly((1.73, 1.62), (2.05, 1.5), (1.72, 1.42), closed=False)
    plume = chain(quad((1.2, 2.08), (1.3, 2.6), (1.75, 2.8), 10), lens((1.75, 2.8), (2.05, 2.55), 0.6, 10))
    face = quad((1.0, 1.95), (1.05, 1.3), (1.65, 1.15), 10)
    wing = chain(quad((-0.9, 0.6), (0.2, 0.7), (0.6, -0.2), 16), quad((0.6, -0.2), (-0.4, -0.5), (-1.6, 0.0), 14))
    wing_lines = [quad((-1.2, 0.2), (-0.4, 0.05), (0.2, -0.25), 8), quad((-0.9, 0.42), (-0.2, 0.35), (0.4, 0.05), 8)]
    scales = [arc(x, y, 0.15, math.radians(200), math.radians(340), 6) for x, y in [(0.9, -0.5), (0.6, -0.8), (1.2, -0.15), (0.2, -1.05), (0.95, -0.95)]]
    tail = poly((-1.95, 0.5), (-2.7, 0.2), (-2.1, -0.2), closed=False)
    legs = [[(-0.2, -1.38), (-0.25, -2.2)], [(0.5, -1.35), (0.55, -2.2)]] + [[(x, -2.2), (x + d, -2.35)] for x in (-0.25, 0.55) for d in (-0.25, 0.25)]
    grass = [[(x, -2.35), (x + 0.15 * s, -1.6)] for x, s in [(-2.6, 1), (-2.4, -1), (-2.2, 1), (2.2, -1), (2.4, 1), (2.6, -1)]]
    ground = [[(-3.0, -2.35), (3.0, -2.35)]]
    leaves = maple(-2.2, 2.2, 0.45, 0.5) + maple(2.6, 2.5, 0.35, -0.6)
    return make("Plump Quail", [body, head, beak, plume, face, wing, tail] + wing_lines + scales + legs + grass + ground + leaves,
                [eye(1.35, 1.6, 0.09)])


# ------------------------------------------------------------ harvest

@design("autumn_apple_basket", T)
def apple_basket(rng):
    rim = rrect(-2.5, -0.15, 2.5, 0.25, 0.15)
    body = chain([(-2.3, -0.15)], cubic((-2.3, -0.15), (-2.1, -1.8), (-1.8, -2.6), (-1.4, -2.6), 16), [(1.4, -2.6)],
                 cubic((1.4, -2.6), (1.8, -2.6), (2.1, -1.8), (2.3, -0.15), 16))
    weave = [quad((-2.25, y), (0, y - 0.15), (2.25, y), 20) for y in (-0.9, -1.7)]
    weave = [clip(w, lambda p: True)[0] for w in weave]
    weave = [[(x * (1 - 0.06 * k), y) for x, y in w] for k, w in enumerate(weave)]
    ribs = [[(x, -0.15), (x * 0.82, -2.6)] for x in (-1.2, 0.0, 1.2)]
    cents = [(-1.65, 0.55), (-0.55, 0.55), (0.55, 0.55), (1.65, 0.55), (-1.1, 1.42), (0.0, 1.42), (1.1, 1.42)]
    apples = []
    for k, (x, y) in enumerate(cents):
        top = k >= 4
        for p in apple(x, y, 0.5, stem=top, leafy=(k == 5)):
            apples += clip(p, lambda q: q[1] > 0.25)
    handle = clip(arc(0, 0.25, 2.35, 0, math.pi, 80), outside([(x, y, 0.55) for x, y in cents] + [(0.25, 2.2, 0.35)]))
    loose = apple(2.7, -2.15, 0.45)
    return make("Basket of Apples", [rim, body] + weave + ribs + apples + handle + loose)


@design("autumn_apple_wheelbarrow", T)
def apple_wheelbarrow(rng):
    tray = poly((-2.2, 0.2), (1.7, 0.2), (1.1, -1.2), (-1.6, -1.2))
    lip = [[(-2.2, -0.05), (1.6, -0.05)]]
    wheel = [circle(1.5, -1.85, 0.75, 50), circle(1.5, -1.85, 0.15, 12)] + [[(1.5 + 0.15 * math.cos(a), -1.85 + 0.15 * math.sin(a)), (1.5 + 0.7 * math.cos(a), -1.85 + 0.7 * math.sin(a))] for a in [k * math.pi / 3 + 0.3 for k in range(6)]]
    brace = [[(0.9, -1.2), (1.5, -1.7)]]
    handles = [tube([(-1.6, -0.9), (-3.2, -0.2)], 0.2), rrect(-3.5, -0.25, -3.0, 0.05, 0.1)]
    legs = [[(-1.4, -1.2), (-1.55, -2.6)], [(-1.2, -1.2), (-1.3, -2.6)]]
    ground = [[(-3.4, -2.6), (3.2, -2.6)]]
    apples = []
    cents = [(-1.7, 0.42), (-0.85, 0.42), (0.0, 0.42), (0.85, 0.42), (-1.27, 1.17), (-0.42, 1.17), (0.43, 1.17), (0.0, 1.92)]
    for k, (x, y) in enumerate(cents):
        for p in apple(x, y, 0.42, stem=k >= 4, leafy=k == 7):
            apples += clip(p, lambda q: q[1] > 0.2)
    falls = apple(2.7, -2.25, 0.35, leafy=False)
    return make("Wheelbarrow of Apples", [tray] + lip + wheel + brace + handles + legs + ground + apples + falls)


@design("autumn_orchard_ladder", T)
def orchard_ladder(rng):
    lo = quad((-3.4, 1.9), (-0.6, 1.6), (3.2, 2.6), 40)
    branch = [quad((-3.4, 2.4), (-0.6, 2.0), (3.2, 2.9), 40), lo]
    hanging, twigs = [], []
    for x, y in [(-2.4, 0.7), (0.75, 1.0), (1.6, 0.3), (2.6, 1.3)]:
        hanging += apple(x, y, 0.38, leafy=False)
        twigs.append([(x + 0.07, y + 0.47), (x + 0.1, yat(lo, x + 0.1))])
    leaves = leaf(-1.6, yat(lo, -1.6), 0.7, -2.0) + leaf(0.3, yat(lo, 0.3), 0.7, -1.2) + leaf(-2.9, 2.35, 0.6, 2.2) + leaf(2.2, 2.75, 0.6, 1.0) + leaf(-0.6, 2.05, 0.6, 1.4)
    rails = [[(-2.6, -2.6), (-0.7, 1.75)], [(-1.6, -2.6), (0.2, 1.65)]]
    rungs = []
    for k in range(1, 7):
        t = k / 7.3
        rungs.append([(-2.6 + 1.9 * t, -2.6 + 4.35 * t), (-1.6 + 1.8 * t, -2.6 + 4.25 * t)])
    bucket = [poly((0.8, -1.0), (2.8, -1.0), (2.55, -2.6), (1.05, -2.6)), arc(1.8, -1.0, 1.0, 0, math.pi, 30), [(0.9, -1.6), (2.7, -1.6)]]
    pile = []
    for x in (1.2, 1.8, 2.4):
        for p in apple(x, -0.75, 0.3, leafy=False):
            pile += clip(p, lambda q: q[1] > -1.0)
    ground = [[(-3.4, -2.6), (3.4, -2.6)]]
    return make("Orchard Ladder and Apple Bucket", branch + twigs + leaves + hanging + rails + rungs + bucket + pile + ground)


@design("autumn_caramel_apples", T)
def caramel_apples(rng):
    out = []
    for cx, cy, r in [(-1.8, -1.0, 0.95), (0.4, -0.7, 1.15), (2.3, -1.2, 0.8)]:
        a = apple(cx, cy, r, stem=False, leafy=False)[0]
        out.append(a)
        drip = [(cx - r * 0.98 + 2 * r * 0.98 * i / 60, cy + 0.05 * r - 0.25 * r * max(0.0, math.sin(5 * math.pi * i / 60)) ** 3) for i in range(61)]
        out.append(drip)
        out.append(rect(cx - 0.08, cy + 0.68 * r, cx + 0.08, cy + 0.68 * r + 1.4))
        out += [circle(cx + dx * r, cy + dy * r, 0.08, 8) for dx, dy in [(-0.4, 0.4), (0.15, 0.25), (0.5, 0.45), (-0.1, -0.1)]]
    paper = [[(-3.2, -2.2), (3.2, -2.2)]]
    bow = [lens((0.4, 1.4), (-0.1, 1.7), 0.5), lens((0.4, 1.4), (0.9, 1.7), 0.5)]
    return make("Caramel Apples", out + paper + bow)


@design("autumn_corn_ears", T)
def corn_ears(rng):
    L, W = 2.6, 0.95
    def half_w(y):
        t = (y + L) / (2 * L)
        return W * (math.sin(math.pi * (0.08 + 0.84 * t)) ** 0.6) * (1 - 0.25 * t)
    ys = [-L + 2 * L * i / 60 for i in range(61)]
    right = [(half_w(y), y) for y in ys]
    cob = chain([(0, -L - 0.05)], right, [(0, L + 0.05)], [(-x, y) for x, y in reversed(right)], [(0, -L - 0.05)])
    cols = [[(f * half_w(y), y) for y in ys[3:-3]] for f in (-0.6, -0.2, 0.2, 0.6)]
    rows = [quad((-half_w(y), y), (0, y - 0.12), (half_w(y), y), 10) for y in [-L + 0.45 + 0.42 * k for k in range(12)]]
    husks = [lens((0, -L + 0.2), (-2.2, -L - 1.4), 0.25, 30), lens((0, -L + 0.2), (2.0, -L - 1.6), 0.25, 30), lens((0, -L + 0.2), (-0.2, -L - 2.0), 0.18, 30)]
    husk_veins = [[(0, -L + 0.2), (-1.8, -L - 1.15)], [(0, -L + 0.2), (1.65, -L - 1.3)]]
    silk = [cubic((0, L), (-0.4, L + 0.6), (0.3, L + 0.8), (-0.2, L + 1.4), 16), cubic((0.1, L), (0.5, L + 0.5), (0.2, L + 0.9), (0.6, L + 1.2), 16)]
    parts = hide([cob] + cols + rows, *husks) + husks + husk_veins + silk
    parts = [transform(p, dy=0.3, rot=-0.6) for p in parts]
    leaves = maple(-2.6, 2.4, 0.45, 0.5) + maple(2.6, -2.6, 0.4, -0.6)
    return make("Ear of Harvest Corn", parts + leaves)


def corn_shock(x, y, h, w):
    out = [poly((x - w, y), (x - 0.22 * w, y + 0.55 * h), (x - 0.6 * w, y + 0.92 * h), (x - 0.3 * w, y + 0.8 * h), (x - 0.18 * w, y + 1.05 * h),
                (x, y + 0.85 * h), (x + 0.18 * w, y + 1.05 * h), (x + 0.3 * w, y + 0.8 * h), (x + 0.6 * w, y + 0.92 * h),
                (x + 0.22 * w, y + 0.55 * h), (x + w, y))]
    out += [[(x + d * w, y), (x + d * 0.22 * w, y + 0.5 * h)] for d in (-0.55, 0.0, 0.55)]
    out.append(rect(x - 0.24 * w, y + 0.5 * h, x + 0.24 * w, y + 0.58 * h))
    out.append(quad((x + 0.5 * w, y + 0.3 * h), (x + 1.0 * w, y + 0.35 * h), (x + 1.15 * w, y + 0.15 * h), 6))
    return out


@design("autumn_harvest_moon", T)
def harvest_moon(rng):
    moon = circle(0.5, 1.4, 1.7, 120)
    craters = [circle(x, y, r, 20) for x, y, r in [(0.0, 1.9, 0.35), (1.1, 1.0, 0.25), (0.3, 0.6, 0.2), (1.2, 2.2, 0.18)]]
    field = [quad((-3.4, -0.6), (0.0, -0.2), (3.4, -0.7), 30)]
    shocks = corn_shock(-2.2, -0.45, 1.4, 0.7) + corn_shock(2.4, -0.55, 1.2, 0.6) + corn_shock(-0.3, -2.5, 2.0, 1.0)
    rows = [quad((-3.4, y), (0, y + 0.2), (3.4, y), 20) for y in (-1.4, -2.0)]
    rows = [s for r in rows for s in clip(r, lambda p: not (-1.4 < p[0] < 0.8 and p[1] > -2.5))]
    crows = [crow(-2.2, 2.4, 0.35), crow(-1.4, 2.8, 0.28)]
    return make("Harvest Moon over Corn Shocks", [moon] + craters + field + shocks + rows + crows)


@design("autumn_hay_bales", T)
def hay_bales(rng):
    def bale(cx, cy, r, L):
        out = [circle(cx, cy, r, 60), spiral(cx, cy, 0.05, r * 0.85, 2.5, 80)]
        out.append(chain([(cx, cy + r), (cx + L, cy + r)], arc(cx + L, cy, r, math.pi / 2, -math.pi / 2, 20), [(cx, cy - r)]))
        out += [[(cx + 0.45 * L * k, cy + r), (cx + 0.45 * L * k, cy - r)] for k in (1, 2)]
        return out
    a = bale(-1.9, -1.6, 1.0, 0.9)
    b = bale(1.0, -1.95, 0.75, 0.8)
    c = bale(0.4, -0.05, 0.42, 0.4)
    horizon = clip([(-3.4, -0.4), (3.4, -0.4)], lambda p: not (-0.05 < p[0] < 1.25))
    t = tree(2.6, -0.4, 1.4, 0.75, 0.9, 9)
    sun = [circle(-2.4, 2.2, 0.55, 30)]
    birds = [crow(0.0, 2.4, 0.3), crow(0.7, 2.0, 0.25)]
    stubble = [[(x, -2.75), (x + 0.1, -2.5)] for x in (-3.0, -0.6, 2.5, 2.9)]
    return make("Round Hay Bales", a + b + c + horizon + t + sun + birds + stubble)


@design("autumn_pumpkins_gourds", T)
def pumpkins_gourds(rng):
    big = pumpkin(-1.2, -1.2, 1.1)
    small = pumpkin(1.25, -1.75, 0.68, 0.85)
    tall = pumpkin(0.35, -0.3, 0.6, 1.25)
    tall = [s for st_ in tall for s in clip(st_, lambda p: pumpkin_outline(-1.2, -1.2, 1.1)(p) and pumpkin_outline(1.25, -1.75, 0.68, 0.85)(p))]
    gourd = smooth([(2.2, -1.4), (2.35, -1.7), (2.55, -1.9), (2.6, -2.1), (2.9, -2.35), (3.3, -2.2), (3.35, -1.85), (3.05, -1.65),
                    (2.75, -1.6), (2.5, -1.35), (2.35, -1.25), (2.2, -1.4)], 6, closed=True)
    gourd = clip(gourd, pumpkin_outline(1.25, -1.75, 0.68, 0.85))
    leaves = [lens((-1.1, 0.35), (-2.3, 0.9), 0.4), [(-1.1, 0.35), (-2.0, 0.75)], spiral(-0.35, 0.7, 0.05, 0.3, 1.5)]
    ground = [[(-3.2, -2.4), (3.4, -2.4)]]
    return make("Pumpkins and Gourds", big + small + tall + gourd + leaves + ground)


@design("autumn_pumpkin_truck", T)
def pumpkin_truck(rng):
    body = poly((-3.2, -1.2), (-3.2, -0.3), (-2.9, 0.1), (-1.5, 0.3), (-1.2, 1.4), (-0.2, 1.4), (0.0, 0.2), (3.0, 0.2), (3.0, -1.2))
    window = poly((-1.05, 0.4), (-0.85, 1.2), (-0.35, 1.2), (-0.2, 0.4))
    door = [[(-1.35, 0.25), (-1.4, -1.0)], [(-0.05, 0.2), (-0.05, -1.0)], [(-0.5, -0.1), (-0.2, -0.1)]]
    fenders = [arc(-2.0, -1.2, 0.85, 0, math.pi, 24), arc(2.0, -1.2, 0.85, 0, math.pi, 24)]
    wheels = [circle(-2.0, -1.3, 0.65, 40), circle(2.0, -1.3, 0.65, 40), circle(-2.0, -1.3, 0.25, 16), circle(2.0, -1.3, 0.25, 16)]
    light = circle(-3.0, -0.2, 0.15, 10)
    grille = [[(-3.2, -0.6), (-2.85, -0.6)]]
    bed = [[(0.1, -0.3), (3.0, -0.3)]]
    pumps = []
    for x, s in [(0.8, 0.42), (1.75, 0.5), (2.6, 0.38)]:
        for st_ in pumpkin(x, 0.55, s, 0.85):
            pumps += clip(st_, lambda q: q[1] > 0.2)
    ground = [[(-3.4, -1.95), (3.4, -1.95)]]
    leaves = maple(-2.4, 2.4, 0.45, 0.5) + maple(1.0, 2.6, 0.4, -0.4)
    return make("Old Truck with Pumpkins", [body, window, light] + door + fenders + wheels + grille + bed + pumps + ground + leaves)


@design("autumn_cider_press", T)
def cider_press(rng):
    frame = [rect(-2.2, 2.0, 2.2, 2.6), [(-1.9, 2.0), (-1.9, -1.2)], [(-1.5, 2.0), (-1.5, -1.2)], [(1.5, 2.0), (1.5, -1.2)], [(1.9, 2.0), (1.9, -1.2)]]
    thread = [[(-0.15, y), (0.15, y + 0.15)] for y in (1.0, 1.3, 1.6, 1.9)]
    screw_body = [[(-0.15, 0.85), (-0.15, 2.0)], [(0.15, 0.85), (0.15, 2.0)]]
    crank = [[(-1.4, 3.15), (1.4, 3.15)], circle(-1.5, 3.15, 0.12, 10), circle(1.5, 3.15, 0.12, 10), rect(-0.25, 3.0, 0.25, 3.3)]
    plate = rect(-1.15, 0.55, 1.15, 0.85)
    tub = [rect(-1.2, -1.2, 1.2, 0.55)] + [[(x, 0.55), (x, -1.2)] for x in (-0.8, -0.4, 0.0, 0.4, 0.8)] + [[(-1.2, -0.3), (1.2, -0.3)]]
    tray = poly((-2.3, -1.2), (2.3, -1.2), (2.1, -1.7), (-2.1, -1.7))
    spout = [poly((2.1, -1.4), (2.7, -1.6), (2.7, -1.8), closed=False)]
    jug = [chain(quad((2.4, -2.0), (2.1, -2.3), (2.3, -2.9), 8), [(3.1, -2.9)], quad((3.1, -2.9), (3.3, -2.3), (3.0, -2.0), 8)), arc(3.2, -2.45, 0.25, -math.pi / 2, math.pi / 2, 8)]
    stream = [quad((2.7, -1.8), (2.75, -1.9), (2.7, -2.1), 4)]
    legs = [[(-1.9, -1.7), (-1.9, -2.9)], [(1.6, -1.7), (1.6, -2.9)]]
    apples = apple(-2.7, -2.5, 0.35, leafy=False) + apple(-1.0, -2.55, 0.32) + apple(0.2, -2.55, 0.3, leafy=False)
    ground = [[(-3.2, -2.9), (2.0, -2.9)]]
    return make("Apple Cider Press", frame + screw_body + thread + crank + [plate, tray] + tub + spout + jug + stream + legs + apples + ground)


@design("autumn_woodpile", T)
def woodpile(rng):
    logs = []
    r = 0.42
    for row, n in enumerate([5, 4, 3, 2]):
        for k in range(n):
            x = -2.9 + r + r * row + 2 * r * k
            y = -2.6 + r + row * 2 * r * 0.87
            logs += [circle(x, y, r - 0.02, 30), circle(x, y, r * 0.55, 20)]
            logs.append([(x, y), (x + r * 0.45 * math.cos(1 + k + row), y + r * 0.45 * math.sin(1 + k + row))])
    stump = [ellipse(2.0, -1.0, 0.95, 0.3, 50), [(1.05, -1.0), (1.05, -2.6)], [(2.95, -1.0), (2.95, -2.6)], ellipse(2.0, -1.0, 0.5, 0.15, 30)]
    axe_handle = tube([(2.1, -0.95), (2.9, 1.6)], 0.18)
    axe_head = poly((1.65, -1.0), (1.55, -0.35), (2.05, -0.55), (2.25, -0.6), (2.18, -0.95))
    ground = [[(-3.2, -2.6), (3.3, -2.6)]]
    chips = [lens((0.6, -2.5), (0.9, -2.4), 0.3), lens((3.0, -2.5), (3.25, -2.35), 0.3)]
    leaves = maple(-2.4, 1.8, 0.5, 0.3) + maple(0.6, 2.3, 0.45, -0.6) + maple(1.0, 0.6, 0.4, 0.8)
    return make("Firewood Stack and Axe", logs + stump + [axe_handle, axe_head] + ground + chips + leaves)


@design("autumn_mushroom_log", T)
def mushroom_log(rng):
    log = [chain([(2.3, -0.2)], [(-2.6, -0.2)]), [(-2.6, -2.2), (2.3, -2.2)], ellipse(2.3, -1.2, 0.45, 1.0, 50),
           ellipse(2.3, -1.2, 0.25, 0.6, 30), ellipse(2.3, -1.2, 0.08, 0.2, 12)]
    log.append(arc(-2.6, -1.2, 1.0, math.pi / 2, 1.5 * math.pi, 20))
    bark = [quad((-2.2, -0.8), (-1.4, -0.7), (-0.6, -0.85), 10), quad((0.0, -1.6), (0.8, -1.5), (1.5, -1.65), 10), quad((-1.6, -1.8), (-1.0, -1.7), (-0.4, -1.85), 8)]
    shelves = [chain(quad((x - w, y), (x, y - 0.3), (x + w, y), 10), quad((x + w, y), (x, y + 0.08), (x - w, y), 10)) for x, y, w in [(-0.8, -1.25, 0.55), (0.1, -1.0, 0.45), (-1.7, -1.4, 0.4)]]
    shroom = []
    for cx, base, s in [(-1.6, -0.2, 0.8), (-0.6, -0.2, 1.0), (0.9, -0.2, 0.7)]:
        h = 1.0 * s
        cap = chain(arc(cx, base + h, 0.75 * s, 0, math.pi, 24), quad((cx - 0.75 * s, base + h), (cx, base + h - 0.25 * s), (cx + 0.75 * s, base + h), 12))
        stem = [[(cx - 0.17 * s, base + h - 0.12 * s), (cx - 0.2 * s, base)], [(cx + 0.17 * s, base + h - 0.12 * s), (cx + 0.2 * s, base)]]
        shroom += [cap] + stem
    moss = [wave(-2.4, 2.2, -2.35, 0.08, 10)]
    fern = [quad((2.6, -2.2), (3.0, 0.0), (2.6, 1.0), 16)] + [lens((2.75 + 0.05 * k, -1.6 + 0.6 * k), (3.3, -1.3 + 0.6 * k), 0.3) for k in range(4)]
    leaves = maple(-2.6, 1.6, 0.45, 0.4) + maple(0.6, 2.4, 0.4, -0.4)
    return make("Mushrooms on a Mossy Log", log + bark + shelves + shroom + moss + fern + leaves)


# ------------------------------------------------------------ cosy

@design("autumn_spice_latte", T)
def spice_latte(rng):
    cup = poly((-1.4, 1.2), (1.4, 1.2), (1.0, -2.6), (-1.0, -2.6))
    lid = [rrect(-1.6, 1.2, 1.6, 1.6, 0.15), poly((-1.35, 1.6), (-1.2, 2.1), (1.2, 2.1), (1.35, 1.6), closed=False), [(-0.2, 2.1), (-0.15, 2.3), (0.35, 2.3), (0.4, 2.1)]]
    sleeve = [quad((-1.29, 0.2), (0, 0.1), (1.29, 0.2), 16), quad((-1.13, -1.3), (0, -1.4), (1.13, -1.3), 16)]
    icon = maple(0, -0.95, 0.75, 0.0, False)
    steam = [[(x + 0.15 * math.sin(3 * t), 2.6 + t) for t in [i / 20 * 1.0 for i in range(21)]] for x in (-0.5, 0.5)]
    pumpkin_ = pumpkin(2.45, -2.0, 0.5)
    sticks = [rrect(-3.2, -2.6, -1.4, -2.35, 0.1), rrect(-3.0, -2.35, -1.5, -2.1, 0.1)]
    star_anise = [star(-2.4, -1.4, 0.4, 8, 0.4)]
    return make("Pumpkin Spice Latte", [cup] + lid + sleeve + icon + steam + pumpkin_ + sticks + star_anise)


@design("autumn_cozy_sweater", T)
def cozy_sweater(rng):
    half = [(0, 2.3), (-0.6, 2.4), (-1.6, 2.1), (-2.4, 1.2), (-3.1, -1.6), (-2.35, -1.85), (-1.75, -0.2), (-1.7, -2.6), (0, -2.6)]
    body = chain(half, [(-x, y) for x, y in reversed(half[:-1])])
    collar = [quad((-0.6, 2.4), (0, 1.6), (0.6, 2.4), 16), quad((-0.8, 2.35), (0, 1.35), (0.8, 2.35), 16)]
    cuffs = [[(-3.0, -1.25), (-2.25, -1.5)], [(3.0, -1.25), (2.25, -1.5)]]
    hem = [[(-1.7, -2.1), (1.7, -2.1)]] + [[(x, -2.1), (x, -2.6)] for x in [-1.4 + 0.35 * k for k in range(9)]]
    band = [zigzag(-1.72, 1.72, 0.65, 0.2, 9), [(-1.73, 0.95), (1.73, 0.95)], [(-1.72, 0.35), (1.72, 0.35)]]
    motifs = maple(-0.9, -1.3, 0.55, 0.0, False) + maple(0.9, -1.3, 0.55, 0.0, False) + maple(0.0, -0.9, 0.45, 0.0, False)
    sleeves = [[(-1.75, -0.2), (-1.7, 1.75)], [(1.75, -0.2), (1.7, 1.75)]]
    return make("Cozy Knit Sweater", [body] + collar + cuffs + hem + band + motifs + sleeves)


@design("autumn_scarf_yarn", T)
def scarf_yarn(rng):
    c = cubic((-2.6, 2.6), (2.8, 2.2), (-3.2, -0.6), (1.6, -1.6), 60)
    scarf = tube(c, 1.0, cap=False)
    m = len(c)
    ends = [[scarf[0], scarf[-1]], [scarf[m - 1], scarf[m]]]
    stripes = [[scarf[k], scarf[2 * m - 1 - k]] for k in (8, 12, 48, 52)]
    fringe = []
    for (a, b), d in [((scarf[0], scarf[-1]), (-0.6, 0.15)), ((scarf[m - 1], scarf[m]), (0.45, -0.45))]:
        for k in range(6):
            t = (k + 0.5) / 6
            p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            fringe.append([p, (p[0] + d[0], p[1] + d[1])])
    ball = [circle(1.6, 1.1, 1.0, 60)] + [arc(1.6 + 0.4, 1.1 - 0.3, 1.0, math.radians(a0), math.radians(a1), 16) for a0, a1 in [(110, 200)]]
    ball += [quad((0.75, 1.5), (1.6, 1.0), (2.3, 0.4), 12), quad((0.9, 1.8), (1.8, 1.3), (2.5, 0.65), 12), quad((1.2, 2.05), (2.1, 1.6), (2.6, 0.95), 12)]
    needles = [[(0.4, 0.0), (3.2, 2.6)], [(0.6, 2.6), (3.0, -0.2)], circle(3.25, 2.65, 0.12, 10), circle(0.55, 2.66, 0.12, 10)]
    needles = [s for n_ in needles for s in clip(n_, outside([(1.6, 1.1, 1.0)]))]
    strand = [cubic((1.0, 0.3), (0.6, -0.6), (2.4, -1.2), (2.8, -2.4), 30)]
    return make("Knitted Scarf and Yarn", [scarf] + ends + stripes + fringe + ball + needles + strand)


@design("autumn_umbrella_leaves", T)
def umbrella_leaves(rng):
    ribs_x = [-2.6, -1.3, 0.0, 1.3, 2.6]
    canopy = [quad((-2.6, 0.4), (-2.3, 2.4), (0, 2.6), 30), quad((0, 2.6), (2.3, 2.4), (2.6, 0.4), 30)]
    scallops = [quad((ribs_x[k], 0.4), ((ribs_x[k] + ribs_x[k + 1]) / 2, 0.75), (ribs_x[k + 1], 0.4), 12) for k in range(4)]
    ribs = [quad((0, 2.6), (x * 0.6, 1.8), (x, 0.4), 12) for x in (-1.3, 1.3)] + [[(0, 2.6), (0, 0.4)]]
    tip = [[(0, 2.6), (0, 3.0)]]
    shaft = chain([(0, 0.4), (0, -2.0)], arc(-0.35, -2.0, 0.35, 0, -math.pi, 12))
    drops = [lens((x, y), (x, y - 0.45), 0.4) for x, y in [(-2.6, -0.3), (-1.8, -1.4), (2.4, -0.6), (1.6, -1.8), (-2.8, -2.2), (2.8, -2.4)]]
    leaves = maple(-1.0, -1.0, 0.5, 0.6) + maple(1.2, -0.6, 0.45, -0.7) + maple(2.6, 3.0, 0.4, -0.3) + maple(-2.6, 2.8, 0.4, 0.5)
    puddle = [ellipse(0.4, -2.75, 1.6, 0.25, 50)]
    return make("Umbrella in an Autumn Shower", canopy + scallops + ribs + tip + [shaft] + drops + leaves + puddle)


@design("autumn_rainy_window", T)
def rainy_window(rng):
    frame = [rect(-2.2, -1.5, 2.2, 2.7), rect(-2.0, -1.3, 2.0, 2.5), [(0, -1.3), (0, 2.5)], [(-2.0, 0.6), (2.0, 0.6)]]
    sill = rect(-2.7, -1.85, 2.7, -1.5)
    drops = [lens((x, y), (x, y - 0.35), 0.4) for x, y in [(-1.5, 2.1), (-0.6, 1.5), (0.7, 2.2), (1.5, 1.4), (-1.2, 0.1), (0.5, -0.2), (1.4, -0.6), (-0.5, -0.7)]]
    streaks = [[(x, y), (x + 0.05, y - 0.5)] for x, y in [(-1.6, 1.0), (1.0, 0.9), (-0.9, 2.3), (0.3, 0.3)]]
    leaf_ = maple(1.2, 1.7, 0.35, -0.6, False) + maple(-1.0, -0.8, 0.3, 0.5, False)
    curtains = [chain([(-2.2, 2.9), (-3.2, 2.9)], [(-3.2, -1.5)], quad((-3.2, -1.5), (-2.9, -0.4), (-2.3, 0.2), 10)),
                chain([(2.2, 2.9), (3.2, 2.9)], [(3.2, -1.5)], quad((3.2, -1.5), (2.9, -0.4), (2.3, 0.2), 10))]
    rod = [[(-3.4, 3.0), (3.4, 3.0)]]
    pot = poly((-1.9, -1.5), (-1.95, -0.95), (-0.95, -0.95), (-1.0, -1.5))
    plant = leaf(-1.45, -0.95, 0.7, 2.0) + leaf(-1.45, -0.95, 0.7, 1.1) + leaf(-1.45, -0.95, 0.55, 1.55)
    mug = [rrect(0.6, -1.5, 1.4, -0.75, 0.1), arc(1.4, -1.12, 0.22, -math.pi / 2, math.pi / 2, 8)]
    steam = [[(0.85 + 0.08 * math.sin(4 * t), -0.6 + t * 0.5) for t in [i / 10 for i in range(11)]]]
    return make("Rainy Day Window", frame + [sill] + drops + streaks + leaf_ + curtains + rod + [pot] + plant + mug + steam)


@design("autumn_reading_nook", T)
def reading_nook(rng):
    back = chain([(-1.6, 0.0)], [(-1.6, 1.4)], quad((-1.6, 1.4), (-1.6, 2.2), (-0.8, 2.2), 8), [(0.8, 2.2)], quad((0.8, 2.2), (1.6, 2.2), (1.6, 1.4), 8), [(1.6, 0.0)])
    arms = [chain([(-1.6, 0.6)], arc(-1.95, 0.6, 0.35, 0, math.pi, 12), [(-2.3, -1.4), (-1.6, -1.4)]),
            chain([(1.6, 0.6)], arc(1.95, 0.6, 0.35, math.pi, 0, 12), [(2.3, -1.4), (1.6, -1.4)])]
    seat = [rrect(-1.6, -0.6, 1.6, 0.0, 0.15), [(-1.6, -1.4), (1.6, -1.4)], [(-1.6, -0.6), (-1.6, -1.4)], [(1.6, -0.6), (1.6, -1.4)]]
    legs = [[(-2.1, -1.4), (-2.1, -1.9)], [(2.1, -1.4), (2.1, -1.9)]]
    pillow = rrect(-0.7, 0.0, 0.7, 1.1, 0.3)
    book = [poly((-0.9, -0.3), (0, -0.4), (0, -0.05), (-0.9, 0.05)), poly((0.9, -0.3), (0, -0.4), (0, -0.05), (0.9, 0.05))]
    blanket = [chain([(1.2, 2.2)], cubic((1.9, 2.0), (2.6, 0.8), (2.0, -0.3), (2.6, -0.9), 20))] + [[(2.6 - 0.12 * k, -0.9 + 0.08 * k), (2.6 - 0.12 * k, -1.2 + 0.08 * k)] for k in range(4)]
    lamp = [[(-2.9, -1.9), (-2.9, 2.0)], poly((-3.5, 2.0), (-3.2, 2.9), (-2.6, 2.9), (-2.3, 2.0)), ellipse(-2.9, -1.95, 0.4, 0.1, 16)]
    table = [rect(2.5, -0.1, 3.5, 0.1), [(2.6, -0.1), (2.6, -1.9)], [(3.4, -0.1), (3.4, -1.9)]]
    cup = [poly((2.7, 0.1), (2.75, 0.65), (3.25, 0.65), (3.3, 0.1)), arc(3.3, 0.38, 0.17, -math.pi / 2, math.pi / 2, 8)]
    floor = [[(-3.6, -1.95), (3.6, -1.95)]]
    leaves = maple(-0.4, 2.85, 0.4, 0.3, False) + maple(0.6, 2.75, 0.35, -0.4, False)
    return make("Cozy Reading Nook", [back, pillow] + arms + seat + legs + book + blanket + lamp + table + cup + floor + leaves)


@design("autumn_campfire", T)
def campfire(rng):
    flame = chain(cubic((-1.1, -0.9), (-1.7, 0.2), (-0.9, 0.9), (-0.9, 1.6), 16),
                  quad((-0.9, 1.6), (-0.5, 1.0), (-0.3, 1.2), 8), quad((-0.3, 1.2), (-0.2, 2.2), (0.2, 2.8), 10),
                  quad((0.2, 2.8), (0.5, 1.8), (0.6, 1.3), 8), quad((0.6, 1.3), (0.9, 1.6), (1.1, 1.9), 8),
                  cubic((1.1, 1.9), (1.5, 0.8), (1.6, 0.0), (1.1, -0.9), 16))
    inner = chain(quad((-0.45, -0.9), (-0.8, 0.2), (-0.2, 1.0), 12), quad((-0.2, 1.0), (0.1, 0.5), (0.35, 0.9), 8), quad((0.35, 0.9), (0.8, 0.0), (0.45, -0.9), 12))
    logs = [tube([(-2.0, -1.9), (1.9, -0.8)], 0.5)] + clip(tube([(2.0, -1.9), (-1.9, -0.8)], 0.5), lambda p: abs((p[1] - (-1.9)) - (p[0] + 2.0) * 1.1 / 3.9) > 0.27)
    ends = [ellipse(-2.0, -1.9, 0.15, 0.25, 12, rot=0.27), ellipse(2.0, -1.9, 0.15, 0.25, 12, rot=-0.27)]
    stones = [ellipse(x, -2.45, 0.42, 0.28, 24) for x in (-2.6, -1.7, -0.85, 0.0, 0.85, 1.7, 2.6)]
    sticks = [[(-3.4, 2.4), (-0.9, 0.9)], [(3.4, 2.4), (1.2, 1.2)]]
    mallows = [transform(rrect(-0.3, -0.2, 0.3, 0.2, 0.08), dx=-1.25, dy=1.12, rot=-0.54), transform(rrect(-0.3, -0.2, 0.3, 0.2, 0.08), dx=1.55, dy=1.43, rot=0.54)]
    sparks = [star(x, y, 0.15, 4, 0.35) for x, y in [(-1.6, 2.4), (1.4, 2.8), (-0.6, 3.2)]]
    sticks = [s for st_ in sticks for s in clip(st_, outside([(-1.25, 1.12, 0.3), (1.55, 1.43, 0.3)]))]
    return make("Campfire and Marshmallows", [flame, inner] + logs + ends + stones + sticks + mallows + sparks)


@design("autumn_apple_pie_window", T)
def apple_pie_window(rng):
    frame = [rect(-2.4, -0.6, 2.4, 3.0), rect(-2.2, -0.4, 2.2, 2.8), [(0, -0.4), (0, 2.8)], [(-2.2, 1.2), (2.2, 1.2)]]
    sill = rect(-3.0, -1.0, 3.0, -0.6)
    wall = [[(-3.0, -1.0), (-2.6, -2.8)], [(3.0, -1.0), (2.6, -2.8)]]
    dish = poly((-1.7, -0.6), (-1.9, 0.0), (1.9, 0.0), (1.7, -0.6))
    crust = chain(quad((-1.9, 0.0), (0, 1.3), (1.9, 0.0), 30))
    rim = wave(-1.95, 1.95, 0.05, 0.08, 10, 80)
    lattice = []
    for k in range(-2, 3):
        x = 0.6 * k
        lattice.append(clip([(x - 0.4, 0.05), (x + 0.4, 1.1)], lambda p: p[1] < 0.98 * (1.3 * 0.5) * (1 - (p[0] / 1.9) ** 2) * 2 - 0.02 and p[1] > 0.12))
        lattice.append(clip([(x + 0.4, 0.05), (x - 0.4, 1.1)], lambda p: p[1] < 0.98 * (1.3 * 0.5) * (1 - (p[0] / 1.9) ** 2) * 2 - 0.02 and p[1] > 0.12))
    lattice = [s for l_ in lattice for s in l_]
    steam = [[(x + 0.15 * math.sin(4 * t), 0.9 + t) for t in [i / 20 * 1.1 for i in range(21)]] for x in (-0.6, 0.0, 0.6)]
    steam = [s for st_ in steam for s in clip(st_, lambda p: abs(p[1] - 1.2) > 0.06)]
    curtains = [chain([(-2.4, 3.2), (-3.4, 3.2), (-3.4, -0.6)], quad((-3.4, -0.6), (-2.9, 0.4), (-2.5, 1.0), 10)),
                chain([(2.4, 3.2), (3.4, 3.2), (3.4, -0.6)], quad((3.4, -0.6), (2.9, 0.4), (2.5, 1.0), 10))]
    outside_ = maple(-1.3, 1.9, 0.35, 0.4, False) + maple(1.2, 2.2, 0.3, -0.5, False) + maple(1.5, 1.4, 0.25, 0.9, False)
    return make("Apple Pie Cooling on the Sill", frame + [sill, dish, crust, rim] + wall + lattice + steam + curtains + outside_)


@design("autumn_lantern", T)
def lantern(rng):
    base = rrect(-1.3, -2.4, 1.3, -1.4, 0.3)
    globe = chain([(-0.8, -1.4)], cubic((-0.8, -1.4), (-1.6, -0.6), (-1.6, 0.8), (-0.7, 1.4), 20), [(0.7, 1.4)],
                  cubic((0.7, 1.4), (1.6, 0.8), (1.6, -0.6), (0.8, -1.4), 20))
    guards = [quad((-0.6, -1.4), (-1.2, 0.0), (-0.5, 1.4), 12), quad((0.6, -1.4), (1.2, 0.0), (0.5, 1.4), 12)]
    top = [poly((-0.9, 1.4), (-0.6, 2.0), (0.6, 2.0), (0.9, 1.4)), rect(-0.3, 2.0, 0.3, 2.3)]
    bail = [(0.95 * math.cos(t), 1.55 + 1.35 * math.sin(t)) for t in [math.pi * i / 40 for i in range(41)]]
    lugs = [circle(-0.95, 1.55, 0.08, 8), circle(0.95, 1.55, 0.08, 8)]
    flame = lens((0, -0.85), (0, 0.4), 0.3)
    wick = rect(-0.12, -1.1, 0.12, -0.85)
    knob = [[(1.3, -1.9), (1.7, -1.9)], circle(1.85, -1.9, 0.15, 12)]
    leaves = maple(-2.2, -2.4, 0.7, 0.7) + maple(2.3, -2.5, 0.6, -0.8) + acorn(-2.6, 1.0, 0.45, 0.3) + acorn(2.7, 0.6, 0.4, -0.3)
    ground = [[(-3.2, -2.4), (3.2, -2.4)]]
    return make("Glowing Lantern", [base, globe, bail, flame, wick] + lugs + guards + top + knob + leaves + ground)


# ------------------------------------------------------------ places

@design("autumn_toadstool_house", T)
def toadstool_house(rng):
    cap = chain(cubic((-2.9, 0.6), (-2.8, 3.3), (2.8, 3.3), (2.9, 0.6), 50), quad((2.9, 0.6), (0, -0.1), (-2.9, 0.6), 30))
    spots = [circle(x, y, r, 24) for x, y, r in [(-1.6, 1.4, 0.35), (-0.3, 2.2, 0.45), (1.2, 1.7, 0.38), (2.2, 1.0, 0.22), (-2.4, 0.9, 0.2), (0.4, 1.0, 0.25)]]
    stem = [quad((-1.2, 0.2), (-1.5, -1.4), (-1.3, -2.6), 16), quad((1.2, 0.2), (1.5, -1.4), (1.3, -2.6), 16)]
    door = chain([(-0.45, -2.6), (-0.45, -1.3)], arc(0, -1.3, 0.45, math.pi, 0, 14), [(0.45, -2.6)])
    knob = circle(0.25, -1.9, 0.07, 8)
    window = [circle(0.75, -0.55, 0.28, 20), [(0.47, -0.55), (1.03, -0.55)], [(0.75, -0.83), (0.75, -0.27)]]
    window2 = [circle(-0.8, -0.4, 0.22, 16)]
    steps = [ellipse(0, -2.8, 0.7, 0.15, 20), ellipse(0.4, -3.2, 0.5, 0.12, 16)]
    grass = [zigzag(-3.2, -1.4, -2.6, 0.1, 6), zigzag(1.4, 3.2, -2.6, 0.1, 6)]
    small = [chain(arc(-2.3, -2.0, 0.45, 0, math.pi, 12), [(-2.75, -2.0), (-1.85, -2.0)]), [(-2.4, -2.0), (-2.4, -2.6)], [(-2.2, -2.0), (-2.2, -2.6)]]
    leaves = maple(2.4, -1.8, 0.45, -0.5, False) + maple(-2.5, 3.0, 0.35, 0.4)
    return make("Toadstool Cottage", [cap, door, knob] + spots + stem + window + window2 + steps + grass + small + leaves)


@design("autumn_covered_bridge", T)
def covered_bridge(rng):
    end = poly((-2.8, -0.6), (-2.8, 0.9), (-2.1, 1.7), (-1.4, 0.9), (-1.4, -0.6))
    portal = chain([(-2.5, -0.6), (-2.5, 0.4)], arc(-2.1, 0.4, 0.4, math.pi, 0, 12), [(-1.7, -0.6)])
    roof = poly((-2.1, 1.7), (2.6, 1.7), (3.1, 0.9), (-1.4, 0.9), closed=False)
    side = [[(-1.4, -0.6), (3.1, -0.6)], [(3.1, 0.9), (3.1, -0.6)]]
    windows = [rect(x, 0.1, x + 0.5, 0.5) for x in (-0.6, 0.6, 1.8)]
    boards = [[(x, -0.6), (x, -0.05)] for x in (-0.9, 0.0, 0.3, 1.2, 1.5, 2.4, 2.7)]
    banks = [poly((-3.4, -0.6), (-2.6, -1.4), (-2.9, -2.0), closed=False), poly((3.4, -0.6), (2.9, -1.4), (3.2, -2.0), closed=False)]
    water = [wave(-2.2, 2.4, -1.4, 0.06, 4, 60), wave(-1.6, 2.0, -1.9, 0.06, 3, 50), wave(-2.4, 0.4, -2.4, 0.06, 2, 40)]
    trees = tree(-3.55, -0.6, 1.5, 0.55, 0.75, 8) + tree(0.6, 1.7, 0.45, 0.75, 0.65, 8) + tree(2.0, 1.7, 0.3, 0.55, 0.5, 8)
    leaves = maple(2.8, 3.0, 0.4, -0.4) + maple(-1.0, 2.8, 0.35, 0.5)
    return make("Covered Bridge in Autumn", [end, portal, roof] + side + windows + boards + banks + water + trees + leaves)


@design("autumn_red_barn", T)
def red_barn(rng):
    walls = poly((-1.8, -2.4), (-1.8, 0.4), (1.8, 0.4), (1.8, -2.4))
    roof = poly((-2.1, 0.3), (-1.5, 1.6), (0, 2.4), (1.5, 1.6), (2.1, 0.3), closed=False)
    loft = rect(-0.4, 0.8, 0.4, 1.5)
    door = [rect(-1.0, -2.4, 1.0, -0.3), [(-1.0, -2.4), (1.0, -0.3)], [(1.0, -2.4), (-1.0, -0.3)], [(0, -2.4), (0, -0.3)]]
    silo = [chain([(2.0, -2.4), (2.0, 1.3)], arc(2.55, 1.3, 0.55, math.pi, 0, 16), [(3.1, -2.4)])] + [[(2.0, y), (3.1, y)] for y in (-1.0, 0.4)]
    t = tree(-2.7, -2.4, 1.6, 0.75, 1.0, 9)
    fence = [[(-3.4, -1.6), (-2.3, -1.6)], [(-3.4, -2.0), (-2.3, -2.0)]]
    ground = [[(-3.4, -2.4), (3.4, -2.4)]]
    leaves = maple(-0.8, 2.8, 0.35, 0.3) + maple(1.0, 3.0, 0.3, -0.5) + maple(-1.6, -2.9, 0.35, 1.2, False)
    birds = [crow(1.6, 2.8, 0.3)]
    return make("Red Barn and Silo", [walls, roof, loft] + door + silo + t + fence + ground + leaves + birds)


@design("autumn_birdhouse", T)
def birdhouse(rng):
    house = poly((-1.1, -0.6), (-1.1, 1.0), (0, 1.9), (1.1, 1.0), (1.1, -0.6))
    roof = [poly((-1.5, 0.75), (0, 2.25), (1.5, 0.75), closed=False), poly((-1.5, 0.75), (-1.35, 0.6), (0, 1.95), (1.35, 0.6), (1.5, 0.75), closed=False)]
    hole = circle(0, 0.6, 0.32, 24)
    perch = [rrect(-0.08, -0.05, 0.4, 0.05, 0.04)]
    post = [[(-0.2, -0.6), (-0.2, -2.8)], [(0.2, -0.6), (0.2, -2.8)], [(-1.2, -0.6), (1.2, -0.6)]]
    bird = chain(quad((0.6, 2.05), (0.6, 2.6), (1.0, 2.6), 8), quad((1.0, 2.6), (1.3, 2.6), (1.3, 2.4), 6), [(1.55, 2.35), (1.3, 2.3)],
                 quad((1.3, 2.3), (1.4, 1.8), (0.9, 1.45), 8), [(0.6, 1.25)])
    btail = poly((0.6, 1.45), (0.25, 1.15), (0.55, 1.15), closed=False)
    vine = [cubic((0.2, -2.6), (1.4, -2.0), (-1.2, -1.6), (0.2, -1.0), 30)]
    leaves = leaf(0.9, -2.2, 0.55, -0.3) + leaf(-0.6, -1.9, 0.55, 3.0) + leaf(0.7, -1.2, 0.5, 0.4)
    pile = [quad((-2.4, -2.8), (-1.6, -2.2), (-0.8, -2.8), 12), quad((0.8, -2.8), (1.8, -2.1), (2.8, -2.8), 12), [(-3.0, -2.8), (3.0, -2.8)]]
    falling = maple(-2.3, 1.2, 0.5, 0.5) + maple(2.4, 0.2, 0.45, -0.7)
    return make("Birdhouse in Autumn", [house, hole, bird, btail] + roof + perch + post + vine + leaves + pile + falling, [eye(1.05, 2.35, 0.06)])


@design("autumn_porch_chairs", T)
def porch_chairs(rng):
    def chair(cx):
        slats = []
        for k in range(5):
            x0 = cx - 0.75 + 0.3 * k
            slats.append(chain([(x0, 0.0), (x0 - 0.05 * (2 - k), 1.6 + 0.12 * (2 - abs(k - 2)))],
                               arc(x0 - 0.05 * (2 - k) + 0.11, 1.6 + 0.12 * (2 - abs(k - 2)), 0.11, math.pi, 0, 6), [(x0 + 0.22, 0.0)]))
        arm = rect(cx - 1.2, -0.1, cx + 1.2, 0.15)
        seat = poly((cx - 0.85, -0.1), (cx - 0.9, -0.6), (cx + 0.9, -0.6), (cx + 0.85, -0.1), closed=False)
        legs = [[(cx - 1.05, -0.1), (cx - 1.05, -1.8)], [(cx + 1.05, -0.1), (cx + 1.05, -1.8)], [(cx - 0.8, -0.6), (cx - 0.8, -1.8)], [(cx + 0.8, -0.6), (cx + 0.8, -1.8)]]
        return slats + [arm, seat] + legs
    chairs = chair(-1.95) + chair(1.95)
    table = [rect(-0.55, -0.6, 0.55, -0.45), [(-0.4, -0.6), (-0.4, -1.8)], [(0.4, -0.6), (0.4, -1.8)]]
    mugs = [rrect(-0.45, -0.45, -0.1, 0.0, 0.05), rrect(0.1, -0.45, 0.45, 0.0, 0.05)]
    pumps = pumpkin(-3.0, -1.4, 0.35) + pumpkin(3.0, -1.45, 0.3)
    floor = [[(-3.6, -1.8), (3.6, -1.8)], [(-3.6, -2.3), (3.6, -2.3)]]
    railing = []
    leaves = maple(0.0, 1.6, 0.4, 0.2) + maple(-0.6, -2.15, 0.25, 1.4, False) + maple(1.2, -2.12, 0.22, -1.2, False)
    return make("Porch Chairs on a Fall Afternoon", chairs + table + mugs + pumps + floor + railing + leaves)


@design("autumn_bicycle_basket", T)
def bicycle_basket(rng):
    wheels = []
    for cx in (-1.9, 1.9):
        wheels += [circle(cx, -1.4, 1.05, 70), circle(cx, -1.4, 0.95, 70), circle(cx, -1.4, 0.1, 10)]
        wheels += [[(cx + 0.1 * math.cos(a), -1.4 + 0.1 * math.sin(a)), (cx + 0.95 * math.cos(a), -1.4 + 0.95 * math.sin(a))] for a in [k * math.pi / 4 for k in range(8)]]
    bb = (-0.1, -1.4)
    frame = [[(-1.9, -1.4), bb], [bb, (-0.65, 0.5)], [(-0.65, 0.5), (-1.9, -1.4)], [bb, (1.25, 0.4)], [(1.25, 0.4), (1.9, -1.4)],
             [(1.25, 0.4), (1.15, 0.9)]]
    seat = [poly((-1.1, 0.75), (-0.2, 0.75), (-0.5, 0.6), closed=False), [(-0.65, 0.5), (-0.6, 0.66)]]
    bars = [quad((1.15, 0.9), (0.9, 1.1), (0.6, 1.0), 6)]
    crank = [circle(-0.1, -1.4, 0.3, 20), [(-0.1, -1.4), (0.25, -1.9)], rect(0.1, -2.0, 0.45, -1.85)]
    basket = [poly((1.3, 0.55), (2.9, 0.55), (2.7, -0.4), (1.5, -0.4))] + [[(x, 0.55), (x - 0.06 * (x - 2.1), -0.4)] for x in (1.7, 2.1, 2.5)] + [[(1.4, 0.07), (2.8, 0.07)]]
    contents = maple(1.75, 0.6, 0.45, 0.4, False) + maple(2.45, 0.65, 0.4, -0.4, False) + clip(pumpkin(2.1, 0.95, 0.28)[0], lambda p: p[1] > 0.55)
    ground = [[(-3.2, -2.45), (3.2, -2.45)]]
    leaves = maple(-2.4, 1.6, 0.45, 0.5) + maple(-0.6, 2.4, 0.4, -0.3) + maple(0.9, 2.6, 0.35, 0.9)
    return make("Bicycle with a Basket of Leaves", wheels + frame + seat + bars + crank + basket + contents + ground + leaves)


@design("autumn_door_wreath", T)
def door_wreath(rng):
    door = [rect(-1.8, -2.6, 1.8, 2.8), rect(-1.4, -2.2, 1.4, 2.4)]
    knob = circle(1.1, -0.6, 0.12, 12)
    cy, R = 0.9, 1.2
    ring = [circle(0, cy, R, 80)]
    wreath = []
    for k in range(16):
        a = TAU * k / 16
        p = (R * math.cos(a), cy + R * math.sin(a))
        for dr in (0.45, -0.38):
            q = ((R + dr) * math.cos(a + 0.32), cy + (R + dr) * math.sin(a + 0.32))
            wreath.append(lens(p, q, 0.32, 12))
    bow = [lens((0, cy - R), (-0.75, cy - R + 0.35), 0.5), lens((0, cy - R), (0.75, cy - R + 0.35), 0.5),
           poly((-0.08, cy - R - 0.05), (-0.45, cy - R - 0.85), closed=False), poly((0.08, cy - R - 0.05), (0.45, cy - R - 0.85), closed=False)]
    wreath = hide(ring + wreath, *bow[:2])
    acorns = acorn(-0.9, cy + 0.85, 0.3, 0.6) + acorn(0.95, cy + 0.8, 0.3, -0.6)
    acorns = acorns
    step = [rect(-2.4, -3.0, 2.4, -2.6)]
    pumps = pumpkin(-2.75, -1.95, 0.55) + pumpkin(2.65, -2.1, 0.45)
    frame = [[(-2.1, -2.6), (-2.1, 3.1), (2.1, 3.1), (2.1, -2.6)]]
    return make("Welcome Wreath on the Door", door + [knob] + wreath + bow + step + pumps + frame)


@design("autumn_cottage_smoke", T)
def cottage_smoke(rng):
    walls = rect(-1.8, -2.4, 1.8, 0.2)
    roof = poly((-2.3, 0.1), (0, 2.0), (2.3, 0.1), closed=False)
    chimney = [[(1.0, 1.15), (1.0, 2.1), (1.5, 2.1), (1.5, 0.75)]]
    smoke = [circle(1.5, 2.6, 0.3, 20), circle(2.0, 3.0, 0.38, 24), circle(2.7, 3.2, 0.45, 26)]
    door = chain([(-0.35, -2.4), (-0.35, -1.2)], arc(0, -1.2, 0.35, math.pi, 0, 10), [(0.35, -2.4)])
    windows = []
    for x in (-1.15, 1.15):
        windows += [rect(x - 0.4, -1.3, x + 0.4, -0.5), [(x, -1.3), (x, -0.5)], [(x - 0.4, -0.9), (x + 0.4, -0.9)]]
    attic = [circle(0, 0.75, 0.3, 20)]
    path = [quad((-0.35, -2.4), (-0.6, -2.8), (-1.2, -3.1), 8), quad((0.35, -2.4), (0.4, -2.8), (0.2, -3.1), 8)]
    trees = tree(-2.8, -2.4, 1.6, 0.6, 1.0, 8) + tree(2.8, -2.4, 1.2, 0.55, 0.8, 8)
    leaves = maple(-1.4, 2.4, 0.4, 0.4) + maple(0.0, 3.0, 0.35, -0.5)
    return make("Cottage with Chimney Smoke", [walls, roof, door] + chimney + smoke + windows + attic + path + trees + leaves)


@design("autumn_sunflower_field", T)
def sunflower_field(rng):
    out = []
    for cx, cy, R, rot in [(-1.6, 1.0, 1.3, 0.1), (1.0, 1.5, 1.1, -0.15), (2.6, -0.2, 0.75, -0.3)]:
        out += [circle(cx, cy, 0.42 * R, 40), circle(cx, cy, 0.28 * R, 30)]
        n = 14
        for k in range(n):
            a = rot + TAU * k / n
            p0 = (cx + 0.42 * R * math.cos(a), cy + 0.42 * R * math.sin(a))
            p1 = (cx + R * math.cos(a), cy + R * math.sin(a))
            out.append(lens(p0, p1, 0.25, 10))
        stem = quad((cx, cy - R), (cx + 0.1, cy - R - 1.0), (cx - 0.05, -3.0), 16)
        out.append(stem)
    out += [lens((-1.62, -1.6), (-2.7, -1.0), 0.32), lens((1.04, -1.3), (0.0, -0.7), 0.32), lens((2.58, -1.9), (3.3, -1.4), 0.32)]
    hills = [[(-3.4, -3.0), (3.4, -3.0)]]
    out = [s for o in out for s in clip(o, lambda p: True)]
    return make("Sunflowers at Harvest", out + hills)


def gust(x0, y0, x1, y1, r):
    return chain(cubic((x0, y0), (x0 + 0.4 * (x1 - x0), y0 + 0.35), (x0 + 0.6 * (x1 - x0), y1 - 0.35), (x1, y1), 24),
                 spiral(x1, y1 - r, r, 0.3 * r, -0.85, 30, rot=math.pi / 2))
