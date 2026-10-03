"""Fruits & Vegetables niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "fruits"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ---------------------------------------------------------------- helpers

def ea(cx, cy, rx, ry, t0, t1, n=40):
    return [(cx + rx * math.cos(t0 + (t1 - t0) * i / n), cy + ry * math.sin(t0 + (t1 - t0) * i / n)) for i in range(n + 1)]


def sym(left, cx=0.0):
    """Close a left half outline (top centre -> bottom centre) by mirroring."""
    return chain(left, mirror_x(left, cx)[::-1])


def tf(parts, dx=0.0, dy=0.0, s=1.0, rot=0.0):
    return [transform(p, dx, dy, s, rot) for p in parts]


def leafv(p0, p1, bulge=0.3, veins=2):
    """Leaf with midrib and side veins."""
    out = [lens(p0, p1, bulge, 20)]
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    out.append([p0, (p0[0] + dx * 0.85, p0[1] + dy * 0.85)])
    for k in range(veins):
        t = 0.3 + 0.4 * k / max(1, veins - 1) if veins > 1 else 0.5
        mx, my = p0[0] + dx * t, p0[1] + dy * t
        off = 2 * t * (1 - t) * bulge * L * 0.7
        for s in (-1, 1):
            out.append([(mx, my), (mx + ux * off * 0.8 + s * nx * off, my + uy * off * 0.8 + s * ny * off)])
    return out


def seed(x, y, a, l=0.25):
    return lens((x, y), (x + l * math.cos(a), y + l * math.sin(a)), 0.35, 8)


def apple_shape(cx=0.0, cy=0.0, s=1.0):
    left = chain(cubic((0, 0.7), (-0.3, 1.05), (-0.8, 1.1), (-1.1, 0.8), 14),
                 cubic((-1.1, 0.8), (-1.45, 0.4), (-1.35, -0.6), (-0.8, -1.0), 14),
                 cubic((-0.8, -1.0), (-0.5, -1.2), (-0.2, -1.05), (0, -0.95), 10))
    return transform(sym(left), cx, cy, s)


def citrus(cx, cy, r, n=8, rind=0.12):
    out = [circle(cx, cy, r, 80), circle(cx, cy, r * (1 - rind), 70)]
    g = 0.07
    for k in range(n):
        a0, a1 = k * TAU / n + g, (k + 1) * TAU / n - g
        am = (a0 + a1) / 2
        p = (cx + r * 0.1 * math.cos(am), cy + r * 0.1 * math.sin(am))
        out.append(chain([p], arc(cx, cy, r * (0.95 - rind), a0 + 0.04, a1 - 0.04, 8), [p]))
    return out


def potato(cx, cy, rx, ry, rot=0.0, seed_=0):
    pts = ellipse(0, 0, rx, ry, 40)
    out = [(x * (1 + 0.05 * math.sin(3 * i / 40 * TAU + seed_)), y * (1 + 0.06 * math.cos(2 * i / 40 * TAU + seed_))) for i, (x, y) in enumerate(pts)]
    out[-1] = out[0]
    return transform(out, cx, cy, rot=rot)


def stem(p0, p1, w=0.18, bend=0.15):
    mx, my = (p0[0] + p1[0]) / 2 + bend, (p0[1] + p1[1]) / 2
    return tube(quad(p0, (mx, my), p1, 10), w)


def berry_cluster(pts, r):
    return [circle(x, y, r, 20) for x, y in pts]


# ---------------------------------------------------------------- fruit

def banana(p0, ctrl, p1, w=0.85):
    c = quad(p0, ctrl, p1, 30)
    out = [tube(c, lambda t: 0.16 + w * math.sin(math.pi * min(1.0, max(0.0, (t - 0.08) / 0.9))) ** 0.8)]
    dx, dy = p1[0] - c[-3][0], p1[1] - c[-3][1]
    L = math.hypot(dx, dy)
    out.append([(p1[0] - dy / L * 0.1, p1[1] + dx / L * 0.1), (p1[0] + dx / L * 0.18 - dy / L * 0.1, p1[1] + dy / L * 0.18 + dx / L * 0.1),
                (p1[0] + dx / L * 0.18 + dy / L * 0.1, p1[1] + dy / L * 0.18 - dx / L * 0.1), (p1[0] + dy / L * 0.1, p1[1] - dx / L * 0.1)])
    return out


def clip_out(pts, circles):
    """Split a polyline, dropping the parts inside any (cx, cy, r) circle."""
    segs, cur = [], []
    for p in pts:
        inside = any(math.hypot(p[0] - cx, p[1] - cy) < r for cx, cy, r in circles)
        if inside:
            if len(cur) > 1:
                segs.append(cur)
            cur = []
        else:
            cur.append(p)
    if len(cur) > 1:
        segs.append(cur)
    return segs


def bumpy(cx, cy, r, n=11, amp=0.12):
    return polar(lambda t: r * (1 + amp * abs(math.sin(n * t / 2))), cx=cx, cy=cy, n=240)


@design("fruits_apple_leaf", T)
def apple_leaf(rng):
    a = apple_shape(0, -0.5, 2.0)
    st = stem((0, 0.9), (0.3, 2.3), 0.2, -0.2)
    lf = leafv((0.35, 1.9), (2.4, 2.6), 0.3, 3)
    shine = [arc(0, -0.5, 1.6, math.radians(140), math.radians(175), 12)]
    return make("Shiny Apple with Leaf", [a, st] + lf + shine)


@design("fruits_apple_halves", T)
def apple_halves(rng):
    whole = apple_shape(2.05, 0.9, 0.9)
    cut = apple_shape(-1.2, -0.7, 1.55)
    flesh = transform(apple_shape(0, 0, 1.0), -1.2, -0.75, 1.36)
    core = [lens((-1.2, 0.2), (-1.2, -1.75), 0.35, 20)]
    seeds = [seed(-1.35, -0.75, math.radians(100), 0.45), seed(-1.05, -0.75, math.radians(80), 0.45)]
    stems = [stem((-1.2, 0.4), (-1.05, 1.3), 0.15), stem((2.05, 1.5), (2.2, 2.3), 0.14)]
    lf = leafv((2.2, 2.15), (3.2, 2.8), 0.3, 2)
    wedge = [chain(arc(1.9, -2.2, 1.0, math.radians(20), math.radians(160), 20), [(1.9, -2.2)], [(1.9 + math.cos(math.radians(20)), -2.2 + math.sin(math.radians(20)))]),
             arc(1.9, -2.2, 0.85, math.radians(25), math.radians(155), 18)]
    return make("Apple Cut in Half", [whole, cut, flesh] + core + seeds + stems + lf + wedge)


@design("fruits_pear", T)
def pear(rng):
    left = chain(cubic((0, 1.6), (-0.35, 1.6), (-0.45, 1.0), (-0.55, 0.5), 12), cubic((-0.55, 0.5), (-0.7, 0.0), (-1.4, -0.3), (-1.35, -1.0), 14),
                 cubic((-1.35, -1.0), (-1.3, -1.8), (-0.4, -1.9), (0, -1.85), 12))
    body = transform(sym(left), 0, -0.6, 1.3)
    st = stem((0, 1.45), (0.35, 2.5), 0.18, -0.2)
    lf = leafv((0.3, 2.2), (2.2, 2.8), 0.3, 2)
    specks = [circle(x, y, 0.1, 8) for x, y in [(-0.8, -1.4), (-0.3, -2.0), (0.6, -1.6), (0.9, -0.9), (-0.9, -0.6), (0.2, -0.3)]]
    shine = [arc(0, -1.7, 1.3, math.radians(150), math.radians(190), 10)]
    return make("Ripe Pear", [body, st] + lf + specks + shine)


@design("fruits_banana_bunch", T)
def banana_bunch(rng):
    out = []
    for ctrl, p1 in [((-1.6, -2.9), (2.6, -1.1)), ((-0.6, -1.9), (2.8, 0.0)), ((0.4, -0.9), (2.8, 1.1))]:
        out += banana((-2.2, 1.9), ctrl, p1, 0.85)
    crown = [tube([(-2.2, 1.9), (-2.4, 2.5), (-2.3, 3.0)], 0.4), ellipse(-2.3, 3.0, 0.2, 0.08, 10)]
    return make("Bunch of Bananas", out + crown)


@design("fruits_grapes", T)
def grapes(rng):
    pts = []
    rows = [(1.2, 5), (0.5, 5), (-0.2, 4), (-0.9, 4), (-1.6, 3), (-2.3, 2), (-2.9, 1)]
    for k, (y, n) in enumerate(rows):
        off = 0.35 if k % 2 else 0.0
        for i in range(n):
            pts.append((-0.7 * (n - 1) / 2 + 0.7 * i + off * 0.3, y))
    berries = berry_cluster(pts, 0.4)
    st = [stem((0.1, 1.55), (0.3, 2.6), 0.18, 0.1)]
    lf = [polar(lambda t: 1.1 + 0.25 * math.cos(5 * t) + 0.1 * math.cos(10 * t), cx=1.9, cy=2.2, n=160), [(1.9, 2.2), (1.9, 1.2)],
          [(1.9, 2.2), (2.8, 2.8)], [(1.9, 2.2), (1.0, 2.8)], [(1.9, 2.2), (2.9, 1.8)]]
    tendril = [spiral(-1.6, 2.4, 0.05, 0.5, 2.0, 80)]
    return make("Bunch of Grapes with Vine Leaf", berries + st + lf + tendril)


@design("fruits_pineapple", T)
def pineapple(rng):
    cx, cy, rx, ry = 0, -1.0, 1.45, 1.9
    body = ellipse(cx, cy, rx, ry, 120)
    grid = []
    for sgn in (1, -1):
        for c in range(-6, 7):
            seg = []
            for i in range(61):
                x = -rx + 2 * rx * i / 60
                y = cy + sgn * x * 1.2 + c * 0.62
                if (x / rx) ** 2 + ((y - cy) / ry) ** 2 < 0.97:
                    seg.append((x, y))
            if len(seg) >= 3:
                grid.append(seg)
    crown = []
    for bx, tip, b in [(-0.4, (-1.7, 1.8), 0.15), (-0.2, (-1.0, 2.7), 0.14), (0.0, (0.0, 3.2), 0.12), (0.2, (1.0, 2.7), 0.14), (0.4, (1.7, 1.8), 0.15),
                       (-0.1, (-0.5, 2.2), 0.14), (0.1, (0.6, 2.3), 0.14)]:
        crown.append(lens((bx, cy + ry - 0.05), tip, b, 14))
    return make("Pineapple with Spiky Crown", [body] + grid + crown[:5])


@design("fruits_watermelon", T)
def watermelon(rng):
    cx, cy, rx, ry = -1.0, 1.0, 2.0, 1.3
    whole = [ellipse(cx, cy, rx, ry, 120)]
    for f in (-0.6, -0.2, 0.2, 0.6):
        whole.append([(cx + rx * f * math.sqrt(max(0, 1 - (y / ry) ** 2)) + 0.1 * math.sin(7 * y), cy + y) for y in [ry * (-0.9 + 1.8 * i / 30) for i in range(31)]])
    ax, ay, R = 1.6, -0.2, 2.6
    slice_ = [chain([(ax, ay)], arc(ax, ay, R, math.radians(-125), math.radians(-55), 30), [(ax, ay)]),
              arc(ax, ay, R - 0.35, math.radians(-122), math.radians(-58), 26)]
    seeds = [seed(ax + r * math.cos(math.radians(a)), ay + r * math.sin(math.radians(a)), math.radians(a), 0.3)
             for r, a in [(1.0, -95), (1.5, -110), (1.5, -78), (1.9, -95), (1.95, -115), (1.95, -72)]]
    return make("Watermelon and Juicy Wedge", whole + slice_ + seeds)


def strawberry(cx, cy, s, rot=0.0):
    left = chain(cubic((0, 0.9), (-0.7, 1.05), (-1.15, 0.75), (-1.05, 0.1), 14), cubic((-1.05, 0.1), (-0.95, -0.7), (-0.3, -1.2), (0, -1.3), 14))
    body = sym(left)
    cal = star(0, 0.95, 0.65, 5, inner=0.3)
    seeds_ = [seed(x, y, math.radians(90), 0.2) for x, y in [(-0.5, 0.35), (0.0, 0.45), (0.5, 0.35), (-0.65, -0.15), (-0.2, -0.05), (0.25, -0.05), (0.65, -0.15),
                                                          (-0.35, -0.6), (0.1, -0.6), (-0.05, -1.0)]]
    st = [(0, 1.0), (0.1, 1.5)]
    return tf([body, cal, st] + seeds_, cx, cy, s, rot)


@design("fruits_strawberries", T)
def strawberries(rng):
    out = strawberry(-1.5, -1.0, 1.2, 0.3) + strawberry(1.3, -0.9, 1.3, -0.25) + strawberry(0.0, 1.3, 0.9, 0.0)
    flower = [circle(2.0, 2.0, 0.25, 16)] + [circle(2.0 + 0.5 * math.cos(a), 2.0 + 0.5 * math.sin(a), 0.3, 18) for a in [math.radians(90 + 72 * k) for k in range(5)]]
    lf = leafv((-1.4, 1.6), (-2.9, 2.6), 0.32, 2)
    return make("Fresh Strawberries", out + flower + lf)


@design("fruits_cherries", T)
def cherries(rng):
    c1, c2 = (-1.1, -1.4), (1.0, -1.1)
    out = [circle(c1[0], c1[1], 1.0, 70), circle(c2[0], c2[1], 1.0, 70)]
    out += [arc(c1[0], c1[1], 0.75, math.radians(110), math.radians(160), 8), arc(c2[0], c2[1], 0.75, math.radians(110), math.radians(160), 8)]
    out += [quad((c1[0], c1[1] + 1.0), (-0.9, 1.0), (0.4, 2.4), 16), quad((c2[0], c2[1] + 1.0), (1.0, 1.0), (0.45, 2.4), 16)]
    out += [arc(c1[0], c1[1] + 1.12, 0.15, math.pi, 2 * math.pi, 6), arc(c2[0], c2[1] + 1.12, 0.15, math.pi, 2 * math.pi, 6)]
    out += leafv((0.45, 2.4), (2.7, 2.0), 0.3, 3)
    return make("Pair of Cherries", out)


@design("fruits_lemon", T)
def lemon(rng):
    body = [transform(parametric(lambda t: (1.6 + 0.35 * math.cos(t) ** 18) * math.cos(t), lambda t: 1.05 * math.sin(t), 0, TAU, 160), -0.9, 0.9, rot=0.35)]
    shine = [transform(arc(0, 0, 0.75, math.radians(100), math.radians(150), 8), -0.9, 0.9, rot=0.35)]
    sl = citrus(1.6, -1.5, 1.3, 8)
    lf = [stem((0.85, 1.6), (1.4, 2.2), 0.12)] + leafv((1.4, 2.2), (3.0, 2.9), 0.3, 2) + leafv((1.4, 2.2), (2.9, 1.3), 0.3, 2)
    wedge = [chain(arc(-1.4, -2.0, 1.0, math.radians(200), math.radians(340), 20)[::-1], [(-1.4, -2.0)], [(-1.4 + math.cos(math.radians(340)), -2.0 + math.sin(math.radians(340)))])]
    return make("Lemon and Lemon Slice", body + shine + sl + lf)


@design("fruits_orange_halved", T)
def orange_halved(rng):
    whole = [circle(-1.3, 1.0, 1.5, 90), star(-1.3, 2.45, 0.22, 5, inner=0.4)]
    lf = leafv((-1.2, 2.5), (0.6, 3.0), 0.32, 2)
    half = citrus(1.0, -1.1, 1.75, 10)
    dimples = [circle(-1.3 + x, 1.0 + y, 0.08, 8) for x, y in [(-0.7, -0.5), (0.4, 0.6), (0.7, -0.6), (-0.3, 0.3)]]
    return make("Orange Halves", whole + lf + half + dimples)


@design("fruits_peach", T)
def peach(rng):
    left = chain(cubic((0, 1.3), (-1.2, 1.9), (-2.1, 0.2), (-1.3, -1.0), 20), cubic((-1.3, -1.0), (-0.8, -1.7), (-0.2, -1.6), (0, -1.55), 12))
    body = transform(sym(left), 0, -0.6, 1.15)
    crease = [quad((0, 0.9), (0.6, -0.4), (0.15, -2.35), 20)]
    st = [stem((0, 0.9), (-0.1, 1.6), 0.18, 0.05)]
    lf = leafv((-0.05, 1.5), (-2.2, 2.5), 0.3, 3) + leafv((0.0, 1.5), (1.6, 2.8), 0.3, 2)
    return make("Fuzzy Peach with Leaves", [body] + crease + st + lf)


@design("fruits_plums", T)
def plums(rng):
    p1 = [ellipse(-1.2, 0.3, 1.3, 1.5, 80, rot=0.2), quad((-1.0, 1.75), (-0.6, 0.3), (-1.4, -1.15), 16)]
    p2 = [ellipse(1.2, 0.5, 1.2, 1.4, 80, rot=-0.15), quad((1.05, 1.9), (1.5, 0.5), (1.3, -0.9), 16)]
    half = [ellipse(0.1, -1.9, 1.6, 0.95, 80), ellipse(0.1, -1.9, 1.4, 0.8, 70), lens((-0.5, -1.9), (0.7, -1.9), 0.4, 16), [(-0.3, -1.9), (0.5, -1.9)]]
    stems = [stem((-1.0, 1.8), (-0.6, 2.7), 0.14, 0.1), stem((1.05, 1.9), (0.8, 2.7), 0.14, -0.1)]
    lf = leafv((-0.6, 2.7), (-2.6, 2.9), 0.3, 2)
    return make("Plums and Plum Half", p1 + p2 + half + stems + lf)


@design("fruits_kiwi", T)
def kiwi(rng):
    whole = [ellipse(-1.3, 1.2, 1.7, 1.15, 90, rot=0.15), ellipse(-2.95, 0.95, 0.12, 0.15, 8)]
    out = whole
    hints = []
    for cx, cy, r in [(1.4, 0.3, 1.4), (-0.6, -1.6, 1.3)]:
        out += [circle(cx, cy, r, 80), circle(cx, cy, r * 0.9, 70), ellipse(cx, cy, r * 0.3, r * 0.22, 30)]
        for k in range(12):
            a = k * TAU / 12
            hints.append(eye(cx + r * 0.42 * math.cos(a), cy + r * 0.42 * math.sin(a), 0.07))
            if k % 2 == 0:
                out.append([(cx + r * 0.55 * math.cos(a + 0.26), cy + r * 0.55 * math.sin(a + 0.26)), (cx + r * 0.82 * math.cos(a + 0.26), cy + r * 0.82 * math.sin(a + 0.26))])
    return make("Kiwi Fruit Slices", out, hints)


@design("fruits_mango", T)
def mango(rng):
    body = chain(cubic((-0.2, 1.7), (1.2, 1.9), (1.9, 0.0), (0.9, -1.4), 20), cubic((0.9, -1.4), (0.5, -1.9), (-0.1, -1.8), (-0.4, -1.6), 10),
                 cubic((-0.4, -1.6), (-1.6, -0.9), (-1.4, 1.5), (-0.2, 1.7), 20))
    m = tf([body, arc(0.2, 0.2, 1.1, math.radians(100), math.radians(150), 8)], -1.1, 0.5, 1.15, -0.5)
    top = transform([(-0.2, 1.7)], -1.1, 0.5, 1.15, -0.5)[0]
    st = [stem(top, (top[0] + 0.1, top[1] + 0.7), 0.15)]
    lf = leafv((top[0] + 0.1, top[1] + 0.6), (top[0] + 2.0, top[1] + 0.9), 0.25, 3)
    skin = [ellipse(1.7, -1.7, 1.25, 1.1, 70)]
    cells = []
    for i in range(-2, 3):
        for j in range(-1, 3):
            x, y = 1.7 + i * 0.5, -1.5 + j * 0.5
            if ((x - 1.7) / 1.1) ** 2 + ((y + 1.7) / 0.95) ** 2 < 0.8:
                cells.append(rrect(x - 0.21, y - 0.21, x + 0.21, y + 0.21, 0.07))
    return make("Mango and Diced Mango Half", m + st + lf + skin + cells)


@design("fruits_papaya", T)
def papaya(rng):
    left = chain(cubic((0, 2.6), (-0.6, 2.6), (-0.9, 1.8), (-1.2, 0.8), 16), cubic((-1.2, 0.8), (-1.8, -0.8), (-1.6, -2.6), (0, -2.6), 20))
    outer = sym(left)
    flesh = transform(outer, 0, -0.05, 0.86)
    cavity = transform(sym(chain(cubic((0, 1.0), (-0.3, 1.0), (-0.45, 0.4), (-0.6, -0.2), 10), cubic((-0.6, -0.2), (-0.9, -1.2), (-0.6, -1.7), (0, -1.7), 12))), 0, -0.2)
    seeds_ = [circle(x, y, 0.15, 12) for x, y in [(0, 0.5), (-0.2, 0.0), (0.2, 0.0), (-0.4, -0.5), (0.0, -0.5), (0.4, -0.5), (-0.4, -1.05), (0.0, -1.05), (0.4, -1.05),
                                                  (-0.2, -1.5), (0.2, -1.5)]]
    st = [rect(-0.15, 2.6, 0.15, 3.0)]
    whole = [ellipse(2.2, -0.8, 0.8, 2.0, 60, rot=-0.1)]
    return make("Papaya Cut Open", [outer, flesh, cavity] + seeds_ + st + whole)


@design("fruits_pomegranate", T)
def pomegranate(rng):
    whole = [circle(-1.2, 0.9, 1.6, 90), poly((-1.6, 2.4), (-1.65, 2.95), (-1.35, 2.7), (-1.2, 3.1), (-1.05, 2.7), (-0.75, 2.95), (-0.8, 2.4), closed=False)]
    face = [ellipse(1.1, -1.4, 1.8, 1.3, 90), ellipse(1.1, -1.4, 1.55, 1.08, 80)]
    rind = [ea(1.1, -1.5, 1.8, 1.4, math.pi + 0.1, 2 * math.pi - 0.1, 30)]
    arils = []
    for y, xs in [(-0.75, (0.4, 0.8, 1.2, 1.6)), (-1.15, (0.0, 0.4, 0.8, 1.2, 1.6, 2.0)), (-1.55, (0.0, 0.4, 0.8, 1.2, 1.6, 2.0)),
                  (-1.95, (0.4, 0.8, 1.2, 1.6))]:
        for x in xs:
            arils.append(circle(x + (0.2 if y in (-1.15, -1.95) else 0) - 0.1, y, 0.18, 12))
    loose = [circle(x, y, 0.18, 12) for x, y in [(-2.3, -2.3), (-1.8, -2.6), (-1.3, -2.25)]]
    return make("Pomegranate Split Open", whole + face + rind + arils + loose)


@design("fruits_figs", T)
def figs(rng):
    left = chain(cubic((0, 1.6), (-0.3, 1.5), (-0.4, 0.9), (-0.7, 0.4), 12), cubic((-0.7, 0.4), (-1.5, -0.4), (-1.2, -1.5), (0, -1.5), 16))
    shape = sym(left)
    whole = [transform(shape, -1.4, 0.6, 1.1), transform(rect(-0.1, 1.6, 0.1, 2.0), -1.4, 0.6, 1.1)]
    whole += [quad((-1.6, 2.0), (-2.1, 0.5), (-1.7, -0.9), 14)]
    half_o = transform(shape, 1.3, -0.6, 1.3)
    half_i = transform(shape, 1.3, -0.65, 1.1)
    pulp = transform(sym(chain(cubic((0, 0.8), (-0.2, 0.7), (-0.3, 0.3), (-0.45, 0.0), 8), cubic((-0.45, 0.0), (-0.9, -0.6), (-0.6, -1.0), (0, -1.0), 10))), 1.3, -0.7, 1.1)
    rays = [[(1.3 + 0.25 * math.cos(a), -1.2 + 0.4 * math.sin(a)), (1.3 + 0.55 * math.cos(a), -1.2 + 0.85 * math.sin(a))] for a in [k * TAU / 10 for k in range(10)]]
    lf = leafv((-1.3, 2.7), (0.6, 2.6), 0.3, 2)
    return make("Figs Whole and Halved", whole + [half_o, half_i, pulp] + rays + lf)


@design("fruits_coconut", T)
def coconut(rng):
    cx, cy, r = -1.3, 1.0, 1.5
    out = [circle(cx, cy, r, 90)] + [circle(cx + x, cy + y, 0.14, 12) for x, y in [(-0.22, 1.18), (0.22, 1.18), (0, 0.9)]]
    for k in (-1, 1):
        out.append(quad((cx + 0.1 * k, cy + 0.8), (cx + 0.75 * k, cy - 0.2), (cx + 0.35 * k, cy - r * 0.95), 14))
        out.append(quad((cx + 0.3 * k, cy + 1.25), (cx + 1.35 * k, cy + 0.2), (cx + 0.85 * k, cy - r * 0.75), 14))
    for hx in (-0.1, 2.15):
        hy = -1.7
        shell = chain(cubic((hx - 1.05, hy), (hx - 1.05, hy - 0.9), (hx - 0.6, hy - 1.25), (hx, hy - 1.25), 14),
                      cubic((hx, hy - 1.25), (hx + 0.6, hy - 1.25), (hx + 1.05, hy - 0.9), (hx + 1.05, hy), 14))
        out += [ellipse(hx, hy, 1.05, 0.4, 60), ellipse(hx, hy, 0.8, 0.28, 50), shell]
        out += [quad((hx - 0.6, hy - 0.5), (hx - 0.5, hy - 0.9), (hx - 0.3, hy - 1.1), 6), quad((hx + 0.6, hy - 0.5), (hx + 0.5, hy - 0.9), (hx + 0.3, hy - 1.1), 6)]
    return make("Coconut and Coconut Halves", out)


@design("fruits_avocado", T)
def avocado(rng):
    left = chain(cubic((0, 1.6), (-0.5, 1.6), (-0.6, 0.9), (-0.8, 0.4), 12), cubic((-0.8, 0.4), (-1.4, -0.4), (-1.3, -1.6), (0, -1.6), 16))
    shape = sym(left)
    out = []
    for cx in (-1.55, 1.55):
        out += [transform(shape, cx, 0, 1.15), transform(shape, cx, -0.04, 1.0)]
    out += [circle(-1.55, -0.65, 0.68, 50), arc(-1.55, -0.65, 0.45, math.radians(110), math.radians(160), 8), ellipse(1.55, -0.65, 0.72, 0.74, 50)]
    lf = leafv((-0.3, 2.3), (2.3, 2.8), 0.25, 2)
    return make("Avocado Halves with Pit", out + lf)


@design("fruits_dragon_fruit", T)
def dragon_fruit(rng):
    cx, cy, rx, ry = -1.0, 0.8, 1.35, 1.8
    out = [ellipse(cx, cy, rx, ry, 100)]
    for th in (-0.2, 0.55, 1.2, 1.94, 2.6, 3.35):
        p0 = (cx + rx * math.cos(th - 0.13), cy + ry * math.sin(th - 0.13))
        p1 = (cx + rx * math.cos(th + 0.13), cy + ry * math.sin(th + 0.13))
        tip = (cx + (rx + 0.6) * math.cos(th + 0.25 * (1 if math.cos(th) > 0 else -1)), cy + (ry + 0.35) * math.sin(th) + 0.45)
        out.append(chain(quad(p0, ((p0[0] + tip[0]) / 2, (p0[1] + tip[1]) / 2 - 0.15), tip, 8), quad(tip, ((p1[0] + tip[0]) / 2, (p1[1] + tip[1]) / 2 + 0.05), p1, 8)))
    for x, y in [(-0.5, 0.3), (0.45, 0.4), (0.0, -0.6), (-0.1, 1.2), (-0.6, -1.2), (0.55, -1.1)]:
        bx, by = cx + x, cy + y
        tipx = bx + (0.35 if x >= 0 else -0.35)
        out.append(chain(quad((bx - 0.2, by - 0.25), (bx - 0.05, by + 0.1), (tipx, by + 0.45), 8), quad((tipx, by + 0.45), (bx + 0.05, by - 0.05), (bx + 0.2, by - 0.25), 8)))
    half = [ellipse(1.5, -1.4, 1.45, 1.15, 80), ellipse(1.5, -1.4, 1.25, 0.95, 70)]
    hints = [eye(1.5 + x, -1.4 + y, 0.07) for x, y in [(-0.8, 0.2), (-0.4, 0.5), (0.0, 0.2), (0.4, 0.5), (0.8, 0.1), (-0.6, -0.3), (-0.2, -0.1), (0.3, -0.3),
                                                      (0.7, -0.5), (-0.3, -0.7), (0.1, -0.65), (-0.9, -0.2), (0.0, 0.7)]]
    return make("Dragon Fruit Whole and Halved", out + half, hints)


@design("fruits_starfruit", T)
def starfruit(rng):
    cx, cy = -0.4, 1.5
    body = parametric(lambda t: 2.3 * math.cos(t), lambda t: (1.0 + 0.08 * math.sin(10 * t) ** 2) * math.sin(t) * (1 - 0.12 * math.cos(t)), 0, TAU, 200)
    ridges = [[(2.15 * x / 20 * 1.0 - 0.0, k * 0.5 * math.sqrt(max(0.0, 1 - (x / 21.5) ** 2)) * (1 - 0.12 * x / 21.5)) for x in range(-20, 21)] for k in (-1, 0, 1)]
    ridges = [[(px * 1.0, py) for px, py in r] for r in ridges]
    st = [[(2.3, 0.0), (2.75, 0.35)], [(-2.3, 0.0), (-2.5, -0.05)]]
    out = tf([body] + ridges + st, cx, cy, 1.0, 0.1)
    for sx, sy, r, rot in [(-1.4, -1.6, 1.3, 0.1), (1.5, -1.4, 1.2, -0.2)]:
        out += [star(sx, sy, r, 5, inner=0.55, rot=rot), star(sx, sy, r * 0.8, 5, inner=0.55, rot=rot)]
        out += [[(sx, sy), (sx + r * 0.4 * math.cos(math.pi / 2 + rot + k * TAU / 5), sy + r * 0.4 * math.sin(math.pi / 2 + rot + k * TAU / 5))] for k in range(5)]
    return make("Starfruit and Star Slices", out)


@design("fruits_passion_fruit", T)
def passion_fruit(rng):
    fx, fy = -1.3, 1.1
    corona = [circle(fx, fy, 0.95, 60)] + [[(fx + 0.45 * math.cos(a), fy + 0.45 * math.sin(a)), (fx + 0.9 * math.cos(a), fy + 0.9 * math.sin(a))] for a in [k * TAU / 20 for k in range(20)]]
    center = [circle(fx, fy, 0.3, 20)] + [[(fx, fy + 0.3), (fx + 0.5 * math.cos(a), fy + 0.3 + 0.5 * math.sin(a))] for a in [math.radians(60), math.radians(90), math.radians(120)]]
    half = [circle(1.5, -1.5, 1.4, 80), circle(1.5, -1.5, 1.15, 70)] + [circle(1.5 + x, -1.5 + y, 0.17, 12) for x, y in [(-0.5, 0.4), (0.0, 0.6), (0.5, 0.4), (-0.6, -0.1), (-0.15, 0.1), (0.3, 0.0), (0.7, -0.2),
                                                                                                       (-0.4, -0.55), (0.1, -0.5), (0.5, -0.7)]]
    whole = [circle(-0.9, -2.0, 0.9, 60), arc(-0.9, -2.0, 0.6, math.radians(110), math.radians(170), 8)]
    return make("Passion Flower and Fruit", _petal_ring(fx, fy) + corona + center + half + whole)


def _petal_ring(fx, fy):
    out = []
    for k in range(10):
        a = k * TAU / 10
        p0 = (fx + 0.95 * math.cos(a - 0.2), fy + 0.95 * math.sin(a - 0.2))
        p1 = (fx + 0.95 * math.cos(a + 0.2), fy + 0.95 * math.sin(a + 0.2))
        tip = (fx + 1.75 * math.cos(a), fy + 1.75 * math.sin(a))
        out.append(chain(quad(p0, (fx + 1.5 * math.cos(a - 0.2), fy + 1.5 * math.sin(a - 0.2)), tip, 8), quad(tip, (fx + 1.5 * math.cos(a + 0.2), fy + 1.5 * math.sin(a + 0.2)), p1, 8)))
    return out


@design("fruits_blueberries", T)
def blueberries(rng):
    twig = [quad((-3.0, 2.2), (-1.0, 1.6), (0.6, 2.6), 20)]
    lfs = leafv((-1.6, 1.85), (-2.6, 3.0), 0.3, 2) + leafv((0.0, 2.15), (1.4, 3.1), 0.3, 2)
    out = twig + lfs
    for x, y, r in [(-1.4, -0.2, 0.75), (0.2, -0.4, 0.8), (1.7, -0.1, 0.7), (-0.6, -1.6, 0.8), (1.0, -1.8, 0.75), (-2.1, -1.7, 0.65), (2.3, -1.9, 0.6)]:
        out += [circle(x, y, r, 50), star(x, y + r * 0.45, r * 0.3, 5, inner=0.45)]
    out += [[(-1.4, 0.55), (-1.4, 1.75)], [(0.2, 0.4), (-0.2, 1.8)]]
    return make("Blueberry Sprig", out)


@design("fruits_raspberries", T)
def raspberries(rng):
    out = []
    for cx, cy, s in [(-1.3, -0.7, 1.0), (1.4, -1.0, 0.85)]:
        outline = chain(arc(0, 0.2, 1.05, math.radians(10), math.radians(170), 20), cubic((-1.03, 0.38), (-1.2, -0.9), (-0.5, -1.6), (0, -1.6), 14),
                        cubic((0, -1.6), (0.5, -1.6), (1.2, -0.9), (1.03, 0.38), 14))
        out.append(transform(outline, cx, cy, s))
        for y, xs in [(0.6, (-0.4, 0.0, 0.4)), (0.25, (-0.6, -0.2, 0.2, 0.6)), (-0.1, (-0.8, -0.4, 0.0, 0.4, 0.8)), (-0.45, (-0.6, -0.2, 0.2, 0.6)),
                      (-0.8, (-0.4, 0.0, 0.4)), (-1.15, (-0.2, 0.2))]:
            for x in xs:
                out.append(circle(cx + x * s, cy + y * s, 0.17 * s, 12))
        out.append(transform(star(0, 0, 0.75, 5, inner=0.3), cx, cy + 1.2 * s, s))
        out.append(transform([(0, 1.2), (0.15, 1.8)], cx, cy, s))
    lf = leafv((-0.2, 1.7), (1.8, 2.7), 0.32, 3)
    return make("Raspberries", out + lf)


@design("fruits_blackberry_bramble", T)
def blackberry(rng):
    cane = quad((-3.2, -2.6), (-0.5, 2.0), (3.0, 1.8), 40)
    thorns = []
    for t in (0.15, 0.3, 0.45, 0.6, 0.75, 0.9):
        i = int(t * 40)
        x, y = cane[i]
        thorns.append(poly((x - 0.1, y), (x - 0.05, y + 0.28), (x + 0.12, y + 0.02), closed=False))
    out = [cane] + thorns
    for cx, cy in [(-1.6, -0.7), (0.6, 0.0), (1.9, 0.7)]:
        pts = [(cx + x, cy + y) for y, xs in [(0.0, (-0.25, 0.25)), (-0.4, (-0.4, 0.0, 0.4)), (-0.8, (-0.4, 0.0, 0.4)), (-1.2, (-0.2, 0.2)), (0.4, (0.0,))] for x in xs]
        out += berry_cluster(pts, 0.21)
    lf = leafv((-0.8, 0.9), (-2.4, 2.4), 0.3, 3) + leafv((1.3, 1.65), (2.6, 3.0), 0.3, 2)
    flower = [circle(2.4, -1.6, 0.25, 16)] + [circle(2.4 + 0.55 * math.cos(a), -1.6 + 0.55 * math.sin(a), 0.32, 18) for a in [math.radians(90 + 72 * k) for k in range(5)]]
    return make("Blackberry Bramble", out + lf + flower)


@design("fruits_lychee", T)
def lychee(rng):
    def bumpy(cx, cy, r):
        return polar(lambda t: r * (1 + 0.035 * math.sin(16 * t)), cx=cx, cy=cy, n=200)
    out = [bumpy(-1.3, 0.6, 1.2)]
    out += [arc(-1.3 + x, 0.6 + y, 0.25, math.radians(200), math.radians(340), 6) for x, y in [(-0.5, 0.3), (0.1, 0.5), (0.6, 0.1), (-0.3, -0.3), (0.3, -0.5), (-0.7, -0.5)]]
    out += [bumpy(1.3, 1.1, 1.0)] + [arc(1.3 + x, 1.1 + y, 0.22, math.radians(200), math.radians(340), 6) for x, y in [(-0.3, 0.3), (0.3, 0.2), (0.0, -0.3), (-0.5, -0.3), (0.5, -0.4)]]
    peeled = [ellipse(0.4, -1.6, 0.95, 1.05, 60), arc(0.4, -1.6, 0.7, math.radians(110), math.radians(160), 8)]
    shell = [chain(ea(0.4, -2.0, 1.25, 0.9, math.pi, 2 * math.pi, 24), zigzag(1.65, -0.85, -2.0, 0.1, 9)[1:])]
    stems = [quad((-1.3, 1.8), (-0.4, 3.0), (0.2, 3.2), 12), quad((1.3, 2.1), (0.9, 2.8), (0.2, 3.2), 12)]
    lf = leafv((0.2, 3.2), (2.6, 2.8), 0.25, 2)
    return make("Lychee Fruits", out + peeled + shell + stems + lf)


@design("fruits_durian", T)
def durian(rng):
    body = [polar(lambda t: (1.0 + 0.12 * abs(math.sin(14 * t))) * math.hypot(2.2 * math.cos(t), 1.9 * math.sin(t)) /
                  math.hypot(math.cos(t), math.sin(t)) / 1.1, cx=0, cy=-0.4, n=400)]
    spikes = []
    for y, n in [(0.6, 5), (-0.2, 6), (-1.0, 6), (-1.8, 5)]:
        w = 2.0 * math.sqrt(max(0.0, 1 - ((y + 0.4) / 1.9) ** 2))
        for i in range(n):
            x = -w + 2 * w * (i + 0.5) / n
            spikes.append(poly((x - 0.18, y - 0.12), (x, y + 0.2), (x + 0.18, y - 0.12), closed=False))
    st = [tube([(0, 1.4), (0.1, 2.0), (0.4, 2.5)], 0.3)]
    return make("Spiky Durian", body + spikes + st)


# ---------------------------------------------------------------- vegetables

def carrot(x0, y0, x1, y1, w):
    L = math.hypot(x1 - x0, y1 - y0)
    center = [(x0 + (x1 - x0) * i / 20, y0 + (y1 - y0) * i / 20) for i in range(21)]
    out = [tube(center, lambda t: w * (1 - t) ** 0.8 + 0.06)]
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    for t, sd in [(0.25, 1), (0.42, -1), (0.6, 1), (0.75, -1)]:
        cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        ww = (w * (1 - t) ** 0.8 + 0.06) / 2
        out.append([(cx + sd * (-uy) * ww, cy + sd * ux * ww), (cx + sd * (-uy) * ww * 0.3 - ux * 0.1, cy + sd * ux * ww * 0.3 - uy * 0.1)])
    return out


@design("fruits_carrots", T)
def carrots(rng):
    out = carrot(-0.6, 0.6, -1.6, -2.9, 1.0) + carrot(0.3, 0.7, 0.4, -2.9, 1.05) + carrot(1.1, 0.6, 2.2, -2.6, 0.95)
    tops = []
    for bx, ang in [(-0.6, 115), (-0.6, 95), (0.3, 100), (0.3, 80), (1.1, 75), (1.1, 55)]:
        a = math.radians(ang)
        tip = (bx + 2.2 * math.cos(a), 0.7 + 2.2 * math.sin(a))
        tops.append([(bx, 0.7), tip])
        for t in (0.4, 0.65, 0.88):
            px, py = bx + 2.2 * t * math.cos(a), 0.7 + 2.2 * t * math.sin(a)
            for s in (-1, 1):
                tops.append(lens((px, py), (px + 0.45 * math.cos(a + s * 0.8), py + 0.45 * math.sin(a + s * 0.8)), 0.3, 6))
    return make("Carrots with Leafy Tops", out + tops)


def florets(cx, cy, rx, ry, n=9, r=0.45):
    """Bumpy cloud outline along the top of an ellipse."""
    pts = []
    for k in range(n):
        a0 = math.pi * k / n
        a1 = math.pi * (k + 1) / n
        p0 = (cx + rx * math.cos(a0), cy + ry * math.sin(a0))
        p1 = (cx + rx * math.cos(a1), cy + ry * math.sin(a1))
        am = (a0 + a1) / 2
        mid = (cx + (rx + r) * math.cos(am), cy + (ry + r) * math.sin(am))
        pts += quad(p0, mid, p1, 10)[:-1]
    pts.append((cx - rx, cy))
    return pts


@design("fruits_broccoli", T)
def broccoli(rng):
    fl = [(0.0, 1.7, 1.25), (-1.6, 0.75, 1.05), (1.6, 0.75, 1.05)]
    out = [bumpy(*fl[0], 12, 0.1)]
    out += clip_out(bumpy(*fl[1], 10, 0.1), [(0.0, 1.7, 1.33)])
    out += clip_out(bumpy(*fl[2], 10, 0.1), [(0.0, 1.7, 1.33)])
    for cx, cy, r in fl:
        for dx, dy in [(-0.35, 0.25), (0.3, 0.3), (-0.05, -0.3)]:
            bx, by, w = cx + dx * r, cy + dy * r, 0.2 * r
            out.append(chain(arc(bx - w, by, w, math.pi, 0, 6), arc(bx + w, by, w, math.pi, 0, 6)))
    trunk = [chain([(-1.3, 0.0)], quad((-1.3, 0.0), (-0.6, -0.2), (-0.55, -1.2), 10), [(-0.7, -2.7)], [(0.7, -2.7)], [(0.55, -1.2)], quad((0.55, -1.2), (0.6, -0.2), (1.3, 0.0), 10)),
             ellipse(0, -2.7, 0.7, 0.18, 24), [(-0.35, -0.4), (-0.3, 0.5)], [(0.35, -0.4), (0.3, 0.5)]]
    return make("Head of Broccoli", out + trunk)


@design("fruits_cauliflower", T)
def cauliflower(rng):
    head = florets(0, 0.6, 2.0, 1.4, 9, 0.45)
    head = chain(head, [(-2.0, 0.6)], quad((-2.0, 0.6), (0, 0.1), (2.0, 0.6), 20))
    curds = [arc(x, y, r, math.radians(20), math.radians(160), 8) for x, y, r in [(-1.0, 1.4, 0.45), (0.0, 1.7, 0.5), (1.0, 1.4, 0.45), (-0.5, 0.8, 0.4), (0.5, 0.8, 0.4)]]
    leaves = []
    for s in (-1, 1):
        lf = chain([(0, -2.6)], cubic((0, -2.6), (s * 1.5, -2.6), (s * 3.0, -1.0), (s * 2.6, 1.0), 20), cubic((s * 2.6, 1.0), (s * 2.2, 0.2), (s * 1.5, 0.0), (s * 1.0, 0.25), 10))
        leaves.append(lf)
        leaves.append(quad((s * 0.2, -2.4), (s * 1.6, -1.6), (s * 2.4, 0.6), 12))
        leaves += [[(s * 0.95, -1.8), (s * 1.3, -0.9)], [(s * 1.6, -1.3), (s * 2.3, -0.8)]]
    front = [chain([(-1.0, 0.3)], quad((-1.0, 0.3), (0, -0.7), (1.0, 0.3), 12)), [(0, -0.3), (0, -2.5)]]
    return make("Cauliflower with Leaves", [head] + curds + leaves + front)


@design("fruits_corn_husk", T)
def corn_husk(rng):
    cob = [ellipse(0, 0.6, 0.9, 2.4, 80)]
    rows = []
    for k in range(-2, 3):
        x = 0.33 * k
        rows.append([(x * math.sqrt(max(0.0, 1 - ((y - 0.6) / 2.4) ** 2)) * 2.4, y) for y in [0.6 - 2.1 + 4.2 * i / 30 for i in range(31)]])
    for k in range(-5, 7):
        y = 0.6 + 0.38 * k
        w = 0.9 * math.sqrt(max(0.0, 1 - ((y - 0.6) / 2.4) ** 2))
        if w > 0.3:
            rows.append(quad((-w, y), (0, y - 0.1), (w, y), 8))
    husks = []
    for s in (-1, 1):
        husks.append(chain([(s * 0.5, -1.5)], cubic((s * 0.5, -1.5), (s * 1.6, -0.6), (s * 2.6, 0.5), (s * 2.8, 2.0), 20), cubic((s * 2.8, 2.0), (s * 2.0, 0.6), (s * 1.6, -1.6), (s * 0.3, -2.8), 20)))
        husks.append(chain([(s * 0.8, -0.8)], cubic((s * 0.8, -0.8), (s * 1.3, -0.4), (s * 1.6, 0.6), (s * 1.6, 1.4), 16), cubic((s * 1.6, 1.4), (s * 1.5, 0.4), (s * 1.2, -0.6), (s * 0.85, -1.2), 12)))
    husks.append(chain([(-0.3, -2.8)], quad((-0.3, -2.8), (0, -3.2), (0.3, -2.8), 8)))
    silk = [quad((x, 2.9), (x + 0.4, 3.3), (x + 0.2 * (1 if x > 0 else -1) + x, 3.7), 8) for x in (-0.3, 0.0, 0.3)]
    return make("Sweet Corn in the Husk", cob + rows + husks + silk)


@design("fruits_pea_pods", T)
def pea_pods(rng):
    pod = [lens((-3.0, -0.6), (2.0, -1.8), 0.3, 40), lens((-2.7, -0.75), (1.7, -1.75), 0.2, 30)]
    peas = [circle(-2.7 + 4.4 * t, -0.75 - 1.0 * t + 0.0, 0.38, 24) for t in (0.15, 0.32, 0.5, 0.68, 0.85)]
    peas = [transform(p, 0, 0.05) for p in peas]
    closed_pod = [lens((-1.6, 1.4), (2.8, 0.8), 0.18, 30), quad((-1.6, 1.4), (0.6, 1.0), (2.8, 0.8), 20)]
    bumps = []
    stem_ = [quad((-1.6, 1.4), (-2.2, 1.8), (-2.0, 2.4), 8), quad((-3.0, -0.6), (-3.2, -0.1), (-2.9, 0.3), 6)]
    tendril = [spiral(-1.0, 2.4, 0.05, 0.45, 2.0, 70)]
    lf = leafv((-2.0, 2.4), (0.4, 2.9), 0.32, 2)
    return make("Pea Pods", pod + peas + closed_pod + bumps + stem_ + tendril + lf)


@design("fruits_bell_peppers", T)
def bell_peppers(rng):
    def pepper(cx, cy, s):
        body = chain(cubic((-0.4, 1.2), (-1.3, 1.5), (-1.6, 0.2), (-1.3, -0.9), 14), quad((-1.3, -0.9), (-1.1, -1.5), (-0.55, -1.25), 8),
                     quad((-0.55, -1.25), (0, -1.6), (0.55, -1.25), 8), quad((0.55, -1.25), (1.1, -1.5), (1.3, -0.9), 8),
                     cubic((1.3, -0.9), (1.6, 0.2), (1.3, 1.5), (0.4, 1.2), 14), quad((0.4, 1.2), (0, 1.0), (-0.4, 1.2), 6))
        lobes = [quad((-0.4, 0.95), (-0.7, 0.0), (-0.55, -1.2), 10), quad((0.4, 0.95), (0.7, 0.0), (0.55, -1.2), 10)]
        st = [tube([(0, 1.05), (0.05, 1.5), (0.4, 1.9)], 0.25), chain(arc(0, 1.15, 0.5, math.radians(200), math.radians(340), 10))]
        return tf([body] + lobes + st, cx, cy, s)
    out = pepper(-1.3, 0.4, 1.2) + pepper(1.6, -0.6, 1.0)
    return make("Bell Peppers", out)


@design("fruits_chili_ristra", T)
def chili_ristra(rng):
    out = []
    for p0, c1, c2, p3, w in [((-2.0, 2.2), (-1.0, 1.0), (-2.6, -1.0), (-1.4, -2.8), 0.85), ((0.0, 2.4), (0.8, 0.8), (-0.6, -1.2), (0.6, -2.9), 0.9),
                              ((2.0, 2.0), (2.6, 0.4), (1.2, -0.6), (2.6, -2.4), 0.8)]:
        c = cubic(p0, c1, c2, p3, 40)
        out.append(tube(c, lambda t: w * (1 - t) ** 0.6 + 0.04))
        out.append(chain(arc(p0[0], p0[1] + 0.05, w / 2 + 0.05, math.radians(200), math.radians(340), 10)))
        out.append(tube([(p0[0], p0[1] + 0.25), (p0[0] + 0.1, p0[1] + 0.7), (p0[0] + 0.45, p0[1] + 0.95)], 0.2))
        out.append(quad((p0[0] - w * 0.2, p0[1] - 0.6), c1, ((c2[0] + p3[0]) / 2 - 0.1, (c2[1] + p3[1]) / 2), 12))
    return make("Red Hot Chili Peppers", out)


@design("fruits_tomato_vine", T)
def tomato_vine(rng):
    vine = [quad((-3.0, 2.6), (0, 2.2), (3.0, 2.8), 30)]
    out = vine
    for x, y, r, sx in [(-2.1, 0.7, 0.9, -2.1), (0.0, 0.6, 0.95, 0.0), (2.1, 0.7, 0.88, 2.1), (-1.05, -1.6, 0.92, -1.05), (1.05, -1.6, 0.9, 1.05)]:
        out += [ellipse(x, y, r * 1.08, r, 60), star(x, y + r * 0.85, r * 0.45, 5, inner=0.3)]
        out.append(quad((x, y + r * 0.95), (sx, (y + 2.4) / 2), (sx * 0.85, 2.38 + 0.02 * sx), 8))
    lf = leafv((-2.6, 2.5), (-3.2, 3.4), 0.3, 1) + leafv((1.6, 2.45), (2.6, 3.3), 0.3, 1)
    return make("Tomatoes on the Vine", out + lf)


@design("fruits_eggplants", T)
def eggplants(rng):
    def egg(cx, cy, s, rot):
        left = chain(cubic((0, 1.6), (-0.6, 1.6), (-0.7, 1.0), (-0.85, 0.3), 12), cubic((-0.85, 0.3), (-1.3, -1.2), (-1.2, -2.2), (0, -2.2), 16))
        body = sym(left)
        cap = chain([(-0.75, 0.9)], [(-0.55, 1.25)], [(-0.3, 1.05)], [(0, 1.45)], [(0.3, 1.05)], [(0.55, 1.25)], [(0.75, 0.9)], quad((0.75, 0.9), (0.6, 1.8), (0, 1.9), 8),
                    quad((0, 1.9), (-0.6, 1.8), (-0.75, 0.9), 8))
        st = tube([(0, 1.9), (0.1, 2.4), (0.35, 2.7)], 0.3)
        shine = arc(0, -0.8, 0.8, math.radians(150), math.radians(200), 8)
        return tf([body, cap, st, shine], cx, cy, s, rot)
    return make("Pair of Eggplants", egg(-1.5, -0.1, 1.05, 0.2) + egg(1.5, 0.0, 1.0, -0.2))


@design("fruits_cucumber", T)
def cucumber(rng):
    body = [rrect(-3.0, 0.3, 2.4, 1.8, 0.75)]
    bumps = [circle(x, y, 0.08, 8) for x, y in [(-2.2, 1.2), (-1.4, 0.8), (-0.6, 1.3), (0.2, 0.8), (1.0, 1.3), (1.8, 0.9), (-1.8, 1.55), (0.6, 1.55)]]
    flower = [star(2.85, 1.05, 0.55, 5, inner=0.4), circle(2.85, 1.05, 0.12, 8)]
    st = [[(-3.0, 1.05), (-3.3, 1.2)]]
    out = body + bumps + flower + st
    for cx, cy, r in [(-1.6, -1.5, 1.2), (1.2, -1.6, 1.1)]:
        out += [circle(cx, cy, r, 70), circle(cx, cy, r * 0.88, 60), ellipse(cx, cy, r * 0.45, r * 0.32, 30)]
        out += [seed(cx + r * 0.3 * math.cos(a), cy + r * 0.22 * math.sin(a), a, 0.2) for a in [k * TAU / 6 + 0.3 for k in range(6)]]
    return make("Cucumber and Slices", out)


@design("fruits_onions", T)
def onions(rng):
    left = chain(cubic((0, 1.8), (-0.2, 1.2), (-1.6, 1.0), (-1.6, -0.2), 16), cubic((-1.6, -0.2), (-1.6, -1.2), (-0.6, -1.5), (0, -1.5), 14))
    whole = [transform(sym(left), -1.2, 0.3, 1.1)]
    whole += [transform(quad((0, 1.7), (-1.0, 0.0), (0, -1.45), 14), -1.2, 0.3, 1.1), transform(quad((0, 1.7), (1.0, 0.0), (0, -1.45), 14), -1.2, 0.3, 1.1)]
    roots = [[(-1.2 + dx, -1.35), (-1.2 + dx * 1.8, -1.9)] for dx in (-0.3, -0.1, 0.1, 0.3)]
    tuft = [quad((-1.2, 2.25), (-1.4, 2.8), (-1.7, 3.1), 6), quad((-1.2, 2.25), (-1.0, 2.8), (-0.8, 3.0), 6)]
    half = [chain(ea(1.5, -1.3, 1.5, 1.4, 0, math.pi, 40), [(2.99, -1.3)])] + [ea(1.5, -1.3, r, r * 0.92, 0, math.pi, 30) for r in (1.15, 0.8, 0.45)]
    half = [chain(ea(1.5, -1.3, 1.5, 1.4, 0, math.pi, 40), [(3.0, -1.3)])] + half[1:]
    base = [[(0.0, -1.3), (3.0, -1.3)], ea(1.5, -1.3, 1.5, 0.3, math.pi, 2 * math.pi, 30)]
    return make("Onions Whole and Sliced", whole + roots + tuft + half + base)


@design("fruits_garlic", T)
def garlic(rng):
    left = chain(cubic((0, 1.2), (-0.3, 0.8), (-1.9, 0.6), (-1.9, -0.6), 16), cubic((-1.9, -0.6), (-1.9, -1.6), (-0.6, -1.8), (0, -1.75), 14))
    bulb = [transform(sym(left), -0.6, 0.4, 1.2)]
    cloves = [transform(quad((0, 1.1), (x, -0.3), (x * 0.4, -1.7), 14), -0.6, 0.4, 1.2) for x in (-1.5, -0.6, 0.6, 1.5)]
    top = [tube([(-0.6, 1.8), (-0.55, 2.6), (-0.3, 3.1)], 0.3)]
    roots = [[(-0.6 + dx, -1.7), (-0.6 + dx * 1.6, -2.3)] for dx in (-0.4, -0.15, 0.15, 0.4)]
    clove = [chain(cubic((2.0, -0.6), (1.0, -1.2), (1.4, -2.6), (2.4, -2.6), 14), cubic((2.4, -2.6), (3.2, -2.5), (3.0, -1.4), (2.0, -0.6), 14)),
             quad((2.0, -0.6), (2.3, -1.6), (2.4, -2.55), 10)]
    return make("Garlic Bulb and Clove", bulb + cloves + top + roots + clove)


@design("fruits_potato_sack", T)
def potato_sack(rng):
    sack = chain([(-2.2, 1.6)], cubic((-2.2, 1.6), (-2.9, 0.0), (-2.8, -2.0), (-2.0, -2.6), 16), [(1.0, -2.6)], cubic((1.0, -2.6), (1.8, -2.0), (1.9, 0.0), (1.2, 1.6), 16))
    fold = [chain([(-2.2, 1.6)], quad((-2.2, 1.6), (-2.7, 2.2), (-1.9, 2.3), 6), quad((-1.9, 2.3), (-0.5, 2.0), (0.9, 2.3), 10), quad((0.9, 2.3), (1.7, 2.1), (1.2, 1.6), 6)),
            quad((-2.2, 1.6), (-0.5, 1.3), (1.2, 1.6), 12)]
    patch = [rect(-1.6, -1.5, 0.2, -0.3)] + [[(-1.6, -1.5), (0.2, -0.3)][0:0]]
    stitches = [[(x, -0.18), (x, -0.42)] for x in (-1.4, -0.9, -0.4, 0.0)]
    pots = [potato(-1.4, 2.2, 0.55, 0.38, 0.2, 1), potato(-0.3, 2.4, 0.6, 0.4, -0.3, 2), potato(0.6, 2.15, 0.5, 0.35, 0.4, 3),
            potato(2.3, -2.3, 0.7, 0.48, 0.3, 4), potato(2.5, -1.2, 0.55, 0.4, -0.5, 5), potato(-2.6, -2.75, 0.55, 0.3, 0.1, 6)]
    eyes = [arc(x, y, 0.1, math.radians(200), math.radians(340), 4) for x, y in [(2.0, -2.2), (2.6, -2.5), (2.4, -1.1), (-0.4, 2.45)]]
    return make("Sack of Potatoes", [sack] + fold + patch + stitches + pots + eyes)


@design("fruits_beetroot", T)
def beetroot(rng):
    root = chain(cubic((0, 0.6), (-1.6, 0.8), (-2.0, -1.0), (-0.6, -1.9), 20), quad((-0.6, -1.9), (-0.1, -2.3), (0.2, -3.1), 8),
                 quad((0.2, -3.1), (0.3, -2.3), (0.6, -1.9), 8), cubic((0.6, -1.9), (2.0, -1.0), (1.6, 0.8), (0, 0.6), 20))
    rings = [arc(0, -0.7, 0.9, math.radians(200), math.radians(250), 8), arc(0, -0.7, 0.9, math.radians(290), math.radians(340), 8)]
    stems = [quad((-0.3, 0.65), (-0.8, 1.5), (-1.6, 2.0), 10), quad((0.0, 0.7), (0.0, 1.6), (0.3, 2.3), 10), quad((0.3, 0.65), (0.9, 1.4), (1.6, 1.8), 10)]
    lfs = leafv((-1.6, 2.0), (-2.8, 3.3), 0.4, 2) + leafv((0.3, 2.3), (0.4, 3.6), 0.4, 2) + leafv((1.6, 1.8), (3.0, 2.6), 0.4, 2)
    return make("Beetroot with Leaves", [root] + rings + stems + lfs)


@design("fruits_radishes", T)
def radishes(rng):
    out = []
    for cx, cy, r, a in [(-2.1, -1.0, 0.72, -0.4), (-0.75, -1.5, 0.75, -0.1), (0.75, -1.5, 0.75, 0.1), (2.1, -1.0, 0.7, 0.4)]:
        body = chain(arc(cx, cy, r, math.radians(-60), math.radians(240), 40),
                     quad((cx + r * math.cos(math.radians(240)), cy + r * math.sin(math.radians(240))), (cx + 0.1, cy - r - 0.3), (cx + 0.6 * math.sin(a), cy - r - 1.0), 8),
                     quad((cx + 0.6 * math.sin(a), cy - r - 1.0), (cx + 0.2, cy - r - 0.2), (cx + r * math.cos(math.radians(-60)), cy + r * math.sin(math.radians(-60))), 8))
        out += [body, arc(cx, cy, r * 0.65, math.radians(120), math.radians(160), 6)]
        out.append(quad((cx, cy + r), (cx * 0.6, cy + r + 0.7), (0.2 + 0.1 * cx, 0.3), 8))
    tie = [rrect(-0.3, 0.3, 0.7, 0.75, 0.1), quad((0.7, 0.55), (1.3, 1.0), (1.2, 0.2), 6)]
    lfs = leafv((0.0, 0.75), (-2.2, 2.8), 0.32, 2) + leafv((0.2, 0.75), (0.0, 3.3), 0.3, 2) + leafv((0.4, 0.75), (2.4, 2.8), 0.32, 2)
    return make("Bunch of Radishes", out + tie + lfs)


def frill(pts, amp=0.09, freq=7.0):
    """Wavy edge along a closed outline (offset along the normal)."""
    out, d = [], 0.0
    n = len(pts)
    for i in range(n):
        a, b = pts[max(0, i - 1)], pts[min(n - 1, i + 1)]
        if i > 0:
            d += math.dist(pts[i - 1], pts[i])
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        o = amp * math.sin(d * freq)
        out.append((pts[i][0] - dy / L * o, pts[i][1] + dx / L * o))
    out[-1] = out[0]
    return out


@design("fruits_cabbage", T)
def cabbage(rng):
    head = [circle(0, 0.0, 1.5, 90)]
    veins = [quad((0, -1.5), (-0.4, -0.2), (-1.1, 1.0), 10), quad((0, -1.5), (0.4, -0.2), (1.1, 1.0), 10), [(0, -1.5), (0, 1.5)]]
    outer = []
    for s in (-1, 1):
        outer.append(chain([(0, -2.6)], cubic((0, -2.6), (s * 2.0, -2.6), (s * 3.0, -1.2), (s * 2.6, 0.6), 20), cubic((s * 2.6, 0.6), (s * 2.3, 1.8), (s * 1.4, 2.2), (s * 0.6, 1.9), 14)))
        outer.append(quad((s * 0.3, -2.4), (s * 1.6, -1.6), (s * 2.0, 0.6), 12))
        outer += [[(s * 1.0, -2.0), (s * 1.7, -1.6)], [(s * 1.5, -0.9), (s * 2.4, -0.5)]]
    top = [chain([(-1.3, 0.8)], cubic((-1.3, 0.8), (-1.6, 2.2), (-0.2, 2.6), (0.4, 1.95), 16))]
    return make("Cabbage Head", head + veins + outer + top)


@design("fruits_lettuce", T)
def lettuce(rng):
    out = []
    for ang, ln, b in [(160, 2.9, 0.42), (125, 3.3, 0.4), (90, 3.0, 0.42), (55, 3.3, 0.4), (20, 2.9, 0.42)]:
        a = math.radians(ang)
        base = (0.25 * math.cos(a), -2.6)
        tip = (base[0] + ln * math.cos(a) * 1.0, base[1] + ln * math.sin(a) * 1.35 + 0.3)
        out.append(frill(lens(base, tip, b, 60), 0.1, 6.0))
        out.append([base, ((base[0] + tip[0] * 3) / 4, (base[1] + tip[1] * 3) / 4)])
    heart_ = [lens((0, -2.6), (0, 0.0), 0.3, 20)]
    return make("Frilly Lettuce", out)


@design("fruits_artichoke", T)
def artichoke(rng):
    out = []
    rows = [(-1.3, 1.8, 4), (-0.3, 2.0, 5), (0.7, 1.7, 4), (1.6, 1.2, 3), (2.3, 0.6, 2)]
    for y, w, n in rows:
        for i in range(n):
            x = -w + 2 * w * (i + 0.5) / n
            hw = w / n * 1.05
            out.append(chain(quad((x - hw, y - 0.5), (x - hw * 0.8, y + 0.3), (x, y + 0.7), 8), quad((x, y + 0.7), (x + hw * 0.8, y + 0.3), (x + hw, y - 0.5), 8)))
    base = [chain([(-1.8, -1.5)], quad((-1.8, -1.5), (-1.2, -2.3), (-0.3, -2.3), 10), [(0.3, -2.3)], quad((0.3, -2.3), (1.2, -2.3), (1.8, -1.5), 10))]
    st = [[(-0.3, -2.3), (-0.35, -3.2)], [(0.3, -2.3), (0.35, -3.2)], ellipse(0, -3.2, 0.35, 0.1, 16)]
    return make("Globe Artichoke", out + base + st)


@design("fruits_asparagus", T)
def asparagus(rng):
    out = []
    for k, x in enumerate((-1.2, -0.6, 0.0, 0.6, 1.2)):
        top = 2.6 - 0.25 * abs(k - 2)
        a = 0.12 * (x)
        x0, x1 = x * 0.6, x * 1.15
        out.append(chain([(x0 - 0.22, -2.8)], [(x1 - 0.2, top - 0.6)], quad((x1 - 0.2, top - 0.6), (x1 - 0.25, top + 0.1), (x1, top + 0.4), 8),
                         quad((x1, top + 0.4), (x1 + 0.25, top + 0.1), (x1 + 0.2, top - 0.6), 8), [(x0 + 0.22, -2.8)]))
        out += [poly((x1 - 0.2, top - 0.6), (x1, top - 0.35), (x1 + 0.2, top - 0.6), closed=False)]
        out += [poly((x1 * 0.85 + x0 * 0.15 - 0.2, y), (x1 * 0.85 + x0 * 0.15, y + 0.2), (x1 * 0.85 + x0 * 0.15 + 0.2, y), closed=False) for y in (top - 1.5,)]
    band = [rrect(-1.25, -1.6, 1.25, -1.1, 0.1)]
    bow = [lens((0.0, -1.35), (1.4, -0.9), 0.3, 10), lens((0.0, -1.35), (1.4, -1.8), 0.3, 10)]
    return make("Asparagus Bundle", out + band + bow)


@design("fruits_cantaloupe", T)
def cantaloupe(rng):
    whole = [circle(-1.1, 0.7, 1.8, 100)]
    net = []
    for k in range(-3, 4):
        x = -1.1 + 0.48 * k
        h = math.sqrt(max(0.0, 1.8 ** 2 - (x + 1.1) ** 2)) * 0.95
        net.append([(x + 0.12 * math.sin(4 * t), 0.7 - h + 2 * h * t) for t in [i / 20 for i in range(21)]])
    for k in range(-3, 4):
        y = 0.7 + 0.48 * k
        w = math.sqrt(max(0.0, 1.8 ** 2 - (y - 0.7) ** 2)) * 0.95
        net.append([(-1.1 - w + 2 * w * t, y + 0.12 * math.sin(5 * t)) for t in [i / 20 for i in range(21)]])
    wedge = [chain(ea(1.4, -1.5, 1.7, 1.1, math.pi, 2 * math.pi, 40), [(-0.3, -1.5)]), ea(1.4, -1.5, 1.45, 0.88, math.pi + 0.05, 2 * math.pi - 0.05, 36),
             ea(1.4, -1.5, 0.9, 0.5, math.pi + 0.1, 2 * math.pi - 0.1, 30)]
    seeds_ = [seed(1.4 + 0.8 * math.cos(a), -1.5 + 0.35 * math.sin(a) - 0.05, a + math.pi / 2, 0.22) for a in [math.pi + 0.5 + 0.55 * k for k in range(4)]]
    return make("Netted Cantaloupe Melon", whole + net + wedge + seeds_)


@design("fruits_zucchini", T)
def zucchini(rng):
    out = []
    for dx, dy, rot, L in [(-0.4, -0.9, 0.55, 2.7), (-0.3, 1.0, 0.75, 2.2)]:
        out += tf([rrect(-L, -0.48, L, 0.48, 0.45), [(-L + 0.4, 0.15), (L - 0.4, 0.15)], [(-L + 0.4, -0.15), (L - 0.4, -0.15)],
                   rect(-L - 0.35, -0.12, -L, 0.12)], dx, dy, 1.0, rot)
    tipx, tipy = transform([(2.7, 0)], -0.4, -0.9, 1.0, 0.55)[0]
    flower = [chain([(tipx - 0.15, tipy - 0.25)], [(tipx + 0.9, tipy + 0.1)], [(tipx + 0.7, tipy + 0.35)], [(tipx + 1.0, tipy + 0.7)], [(tipx + 0.6, tipy + 0.75)],
                    [(tipx + 0.55, tipy + 1.1)], [(tipx + 0.2, tipy + 0.6)], [(tipx - 0.2, tipy + 0.25)])]
    slices = [circle(1.9, -2.3, 0.7, 40), circle(1.9, -2.3, 0.58, 40), circle(1.9, -2.3, 0.22, 20), circle(0.5, -2.5, 0.6, 36), circle(0.5, -2.5, 0.48, 30)]
    return make("Zucchini with Blossom", out + flower + slices)


@design("fruits_brussels_sprouts", T)
def brussels(rng):
    stalk = [chain([(-0.35, -3.0)], [(-0.25, 2.0)]), chain([(0.35, -3.0)], [(0.25, 2.0)])]
    out = stalk
    for k in range(7):
        y = -2.4 + 0.7 * k
        for s in (-1, 1):
            if (k + (s > 0)) % 2:
                continue
            cx = s * 0.85
            r = 0.55 - 0.03 * k
            out += [circle(cx, y, r, 30), quad((cx - s * r * 0.9, y - r * 0.3), (cx, y + 0.1), (cx + s * r * 0.3, y + r * 0.95), 8)]
    top = leafv((0, 2.0), (-2.0, 3.1), 0.35, 2) + leafv((0, 2.0), (2.0, 3.1), 0.35, 2) + leafv((0, 2.0), (0.0, 3.5), 0.3, 1)
    return make("Brussels Sprouts Stalk", out + top)


@design("fruits_banana_peeled", T)
def banana_peeled(rng):
    fruit = chain([(-0.45, 0.0)], cubic((-0.45, 0.0), (-0.5, 1.4), (-0.4, 2.4), (0, 2.8), 16), cubic((0, 2.8), (0.4, 2.4), (0.5, 1.4), (0.45, 0.0), 16))
    peel_body = chain(quad((-0.55, 0.1), (-0.65, -1.4), (-0.25, -2.7), 12), [(0.25, -2.7)],
                      quad((0.25, -2.7), (0.65, -1.4), (0.55, 0.1), 12))
    tip = [rect(-0.2, -3.0, 0.2, -2.7)]
    flaps = []
    for s, ang in [(-1, 1), (1, 1)]:
        flaps.append(chain([(s * 0.55, 0.1)], cubic((s * 0.55, 0.1), (s * 1.6, 0.4), (s * 2.6, -0.4), (s * 2.6, -1.8), 16), [(s * 2.3, -1.9)],
                           cubic((s * 2.3, -1.9), (s * 2.1, -0.6), (s * 1.2, -0.3), (s * 0.5, -0.3), 16)))
    flaps.append(chain([(-0.2, 0.05)], quad((-0.2, 0.05), (0.2, -0.8), (0.1, -1.6), 10), [(0.4, -1.5)], quad((0.4, -1.5), (0.5, -0.6), (0.25, 0.05), 10)))
    return make("Half-Peeled Banana", [fruit, peel_body] + tip + flaps)


@design("fruits_red_currants", T)
def red_currants(rng):
    out = [quad((-2.4, 2.6), (-0.5, 3.0), (1.6, 2.6), 16)]
    for sx, sy, ex, ey, n in [(-1.3, 2.75, -1.7, -2.6, 8), (0.6, 2.75, 0.9, -1.9, 7)]:
        strand = quad((sx, sy), (sx + 0.4, (sy + ey) / 2), (ex, ey), 60)
        berries = []
        for k in range(n):
            px, py = strand[int((k + 0.7) / (n + 0.4) * 60)]
            r = 0.48 - 0.03 * k
            side = 1 if k % 2 else -1
            berries.append((px + side * 0.3, py, r))
        out += clip_out(strand, berries)
        for bx, by, r in berries:
            out += [circle(bx, by, r, 30), arc(bx, by, r * 0.6, math.radians(110), math.radians(160), 5)]
    lf = [polar(lambda t: 0.8 + 0.2 * math.cos(3 * t) + 0.06 * math.cos(9 * t), cx=2.4, cy=1.9, n=160), [(2.4, 1.9), (2.4, 1.2)], [(2.4, 1.9), (3.05, 2.3)],
          [(2.4, 1.9), (1.75, 2.3)], [(1.6, 2.6), (2.0, 2.4)]]
    return make("Strings of Red Currants", out + lf)


@design("fruits_persimmon", T)
def persimmon(rng):
    whole = [polar(lambda t: (abs(math.cos(t)) ** 3 + abs(math.sin(t)) ** 3) ** (-1 / 3), cx=0, cy=0, n=200)]
    whole = [transform(whole[0], -1.2, 0.7, sx=1.8, sy=1.3)]
    cal = []
    for a in (25, 155, 205, 335):
        r = math.radians(a)
        cal.append(lens((-1.2, 1.95), (-1.2 + 1.3 * math.cos(r), 1.95 + 0.5 * math.sin(r)), 0.45, 14))
    st = [rect(-1.32, 1.95, -1.08, 2.5)]
    half = [ellipse(1.5, -1.6, 1.5, 1.15, 80), ellipse(1.5, -1.6, 1.3, 0.95, 70), star(1.5, -1.6, 0.75, 4, inner=0.35, rot=math.pi / 4), circle(1.5, -1.6, 0.15, 10)]
    return make("Persimmon Fruit", whole + cal + st + half)


# ---------------------------------------------------------------- arrangements

@design("fruits_fruit_bowl", T)
def fruit_bowl(rng):
    bowl = [chain([(-2.9, -0.4)], cubic((-2.9, -0.4), (-2.7, -2.0), (-1.2, -2.3), (0, -2.3), 20), cubic((0, -2.3), (1.2, -2.3), (2.7, -2.0), (2.9, -0.4), 20)),
            ellipse(0, -0.4, 2.9, 0.35, 90), poly((-0.9, -2.25), (-1.2, -2.8), (1.2, -2.8), (0.9, -2.25), closed=False)]
    ap = [apple_shape(-1.75, 0.35, 0.7), stem((-1.75, 0.85), (-1.6, 1.4), 0.12), lens((-1.6, 1.3), (-0.9, 1.6), 0.3, 10)]
    pr = [transform(sym(chain(cubic((0, 1.6), (-0.35, 1.6), (-0.45, 1.0), (-0.55, 0.5), 10), cubic((-0.55, 0.5), (-0.7, 0.0), (-1.4, -0.3), (-1.35, -1.0), 12),
                              cubic((-1.35, -1.0), (-1.3, -1.8), (-0.4, -1.9), (0, -1.85), 10))), 1.95, 0.85, 0.7), [(1.95, 1.95), (2.05, 2.35)]]
    ban = banana((-1.0, 2.1), (0.0, 0.9), (1.2, 2.3), 0.5)
    grapes_ = berry_cluster([(x + 0.15, y) for y, xs in [(0.55, (-0.4, 0.1, 0.6)), (0.1, (-0.15, 0.35)), (1.0, (-0.15, 0.35))] for x in xs], 0.25)
    return make("Bowl of Fresh Fruit", bowl + ap + pr + ban + grapes_)


def carrot_top(x, y, w=0.55, lean=0.0):
    out = [chain([(x - w / 2, y - 0.3)], quad((x - w / 2, y - 0.3), (x - w / 2, y + 0.2), (x, y + 0.2), 6), quad((x, y + 0.2), (x + w / 2, y + 0.2), (x + w / 2, y - 0.3), 6))]
    for a in (100 + lean, 75 + lean):
        r = math.radians(a)
        tip = (x + 1.5 * math.cos(r), y + 0.2 + 1.5 * math.sin(r))
        out.append([(x, y + 0.2), tip])
        for t in (0.45, 0.8):
            px, py = x + 1.5 * t * math.cos(r), y + 0.2 + 1.5 * t * math.sin(r)
            for s in (-1, 1):
                out.append(lens((px, py), (px + 0.4 * math.cos(r + s * 0.8), py + 0.4 * math.sin(r + s * 0.8)), 0.3, 6))
    return out


@design("fruits_veg_crate", T)
def veg_crate(rng):
    crate = [rect(-2.8, -2.8, 2.8, -0.2)] + [[(-2.8, y), (2.8, y)] for y in (-1.1, -2.0)] + [[(-2.5, -2.8), (-2.5, -0.2)], [(2.5, -2.8), (2.5, -0.2)]]
    handle_ = [rrect(-0.6, -0.75, 0.6, -0.45, 0.15)]
    cab = [chain(arc(-1.7, 0.4, 0.9, math.radians(-40), math.radians(220), 40)), quad((-1.7, -0.2), (-1.9, 0.5), (-2.3, 1.0), 8), quad((-1.7, -0.2), (-1.5, 0.5), (-1.1, 1.0), 8)]
    toms = [chain(arc(0.0, 0.3, 0.55, math.radians(-30), math.radians(210), 30)), star(0.0, 0.78, 0.28, 5, inner=0.35)]
    carrots_ = carrot_top(1.0, 0.0, 0.5, 10) + carrot_top(1.6, 0.0, 0.5, -10)
    leek = [chain([(2.05, -0.2)], [(2.1, 1.4)], [(2.5, 1.4)], [(2.55, -0.2)]), lens((2.15, 1.4), (1.9, 2.9), 0.2, 10), lens((2.45, 1.4), (2.9, 2.8), 0.2, 10)]
    return make("Crate of Garden Vegetables", crate + handle_ + cab + toms + carrots_ + leek)


@design("fruits_market_stall", T)
def market_stall(rng):
    posts = [[(-2.8, -2.9), (-2.8, 2.0)], [(2.8, -2.9), (2.8, 2.0)]]
    roof = [poly((-3.1, 2.0), (0, 3.1), (3.1, 2.0), closed=False)]
    awn = []
    n = 7
    for i in range(n):
        x0 = -3.1 + 6.2 * i / n
        x1 = x0 + 6.2 / n
        awn.append(chain([(x0, 2.0)], [(x0, 1.6)], arc((x0 + x1) / 2, 1.6, (x1 - x0) / 2, math.pi, 2 * math.pi, 8), [(x1, 2.0)]))
    table = [rect(-2.6, -1.0, 2.6, -0.7), [(-2.4, -1.0), (-2.4, -2.9)], [(2.4, -1.0), (2.4, -2.9)], rect(-2.6, -2.9, 2.6, -2.2)]
    crates = [rect(-2.4, -0.7, -0.9, 0.0), rect(-0.75, -0.7, 0.75, 0.0), rect(0.9, -0.7, 2.4, 0.0)]
    produce = [circle(x, 0.3, 0.3, 20) for x in (-2.0, -1.3)] + [circle(-1.65, 0.75, 0.3, 20)] + \
              [ellipse(x, 0.3, 0.2, 0.42, 16) for x in (-0.4, 0.0, 0.4)] + [tube([(1.1, 0.0), (1.6, 0.8)], 0.3), tube([(1.6, 0.0), (2.2, 0.7)], 0.3)]
    sign = []
    scale_ = [circle(2.2, -1.75, 0.0001, 4)][0:0]
    under = [potato(-1.5, -2.55, 0.4, 0.25, 0.2, 1), potato(-0.6, -2.55, 0.4, 0.25, -0.1, 2), potato(1.3, -2.55, 0.4, 0.25, 0.3, 3)]
    return make("Farmers' Market Stall", posts + roof + awn + table + crates + produce + sign + under + scale_)


@design("fruits_veg_basket", T)
def veg_basket(rng):
    basket = chain([(-2.7, -0.3)], quad((-2.7, -0.3), (-2.6, -2.8), (0, -2.8), 20), quad((0, -2.8), (2.6, -2.8), (2.7, -0.3), 20))
    rim = [rrect(-2.9, -0.45, 2.9, -0.05, 0.15)]
    weave = [quad((-2.6, y), (0, y - 0.25), (2.6, y), 16) for y in (-1.1, -1.8)] + [[(x, -0.45), (x * 0.8, -2.6)] for x in (-1.8, -0.6, 0.6, 1.8)]
    handle_ = [arc(0, -0.2, 2.75, math.radians(8), math.radians(172), 40), arc(0, -0.2, 2.5, math.radians(9), math.radians(171), 40)]
    cab = [chain(arc(-1.3, 0.35, 0.7, math.radians(-25), math.radians(205), 30)), quad((-1.3, -0.05), (-1.5, 0.4), (-1.8, 0.8), 8)]
    tom = [chain(arc(0.15, 0.3, 0.55, math.radians(-30), math.radians(210), 30)), star(0.15, 0.78, 0.28, 5, inner=0.35)]
    car = carrot_top(1.3, -0.05, 0.5, 0)[0:1] + [[(1.3, 0.15), (1.0, 1.0)], [(1.3, 0.15), (1.6, 1.0)], [(1.3, 0.15), (1.3, 1.15)]]
    return make("Basket of Vegetables", [basket] + rim + weave + handle_ + cab + tom + car)
