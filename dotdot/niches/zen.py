"""Zen Patterns niche: mandalas, calm scenes and ornamental patterns."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "zen"
R = math.radians


def make(title, parts, hints=()):
    return Design(title, [p for p in parts if len(p) >= 2], list(hints), T)


# ---------------------------------------------------------------- helpers

def ring(shape, n, phase=0.0, cx=0.0, cy=0.0):
    """`n` copies of `shape` (drawn around the origin) rotated about (cx, cy)."""
    return [transform(shape, dx=cx, dy=cy, rot=phase + k * TAU / n) for k in range(n)]


def petal(r0, r1, w, pointed=True, n=18):
    """Petal along +x from radius r0 (half-width w) to a tip at r1; open base."""
    L = r1 - r0
    if pointed:
        half = cubic((r0, -w), (r0 + L * 0.45, -w * 1.7), (r1 - L * 0.22, -w * 0.55), (r1, 0), n)
    else:
        half = cubic((r0, -w), (r0 + L * 0.55, -w * 1.55), (r1, -w * 1.05), (r1, 0), n)
    return chain(half, [(x, -y) for x, y in half[::-1]])


def smooth(pts, n=8, closed=False):
    """Catmull-Rom curve through the points."""
    P = list(pts)
    if closed and P[0] == P[-1]:
        P = P[:-1]
    m = len(P)
    segs = m if closed else m - 1
    out = []
    for i in range(segs):
        p0 = P[i - 1] if (closed or i > 0) else P[0]
        p1, p2 = P[i], P[(i + 1) % m]
        p3 = P[(i + 2) % m] if (closed or i + 2 < m) else P[-1]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(P[0] if closed else P[-1])
    return out


def densify(pts, step=0.03):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        k = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k) for i in range(1, k + 1)]
    return out


def inside(p, shape):
    x, y = p
    c = False
    for (x0, y0), (x1, y1) in zip(shape, shape[1:] + shape[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            c = not c
    return c


def keep_runs(pts, keep, step=0.03):
    out, cur = [], []
    for p in densify(pts, step):
        if keep(p):
            cur.append(p)
        else:
            if len(cur) > 1:
                out.append(cur)
            cur = []
    if len(cur) > 1:
        out.append(cur)
    return out


def hide(strokes, *shapes):
    """Remove the parts of strokes lying inside any of the closed shapes."""
    out = []
    for s in strokes:
        out += keep_runs(s, lambda p: not any(inside(p, sh) for sh in shapes))
    return out


def in_circle(strokes, r, cx=0.0, cy=0.0):
    out = []
    for s in strokes:
        out += keep_runs(s, lambda p: math.hypot(p[0] - cx, p[1] - cy) < r)
    return out


def ngon(cx, cy, r, n, rot=0.0):
    return [(cx + r * math.cos(rot + TAU * k / n), cy + r * math.sin(rot + TAU * k / n)) for k in range(n + 1)]


def teardrop(r0, r1, w, n=20):
    """Drop shape along +x: round end at r1, point at r0."""
    c = r1 - w
    return chain([(r0, 0)], quad((r0, 0), (c - w * 0.3, -w * 1.15), (c, -w), n // 2),
                 arc(c, 0, w, -math.pi / 2, math.pi / 2, n), quad((c, w), (c - w * 0.3, w * 1.15), (r0, 0), n // 2))


def feather_shape(L, w, barbs=3):
    """Feather along +x from 0 to L: vane outline, shaft and a few barb lines."""
    vane = chain(cubic((L * 0.12, 0), (L * 0.3, w * 1.2), (L * 0.85, w * 0.9), (L, 0), 20),
                 cubic((L, 0), (L * 0.85, -w * 0.9), (L * 0.3, -w * 1.2), (L * 0.12, 0), 20))
    shaft = [(0, 0), (L * 0.92, 0)]
    out = [vane, shaft]
    for k in range(barbs):
        x = L * (0.35 + 0.18 * k)
        out.append([(x + 0.12 * L, w * 0.75 - 0.18 * w * k), (x, 0), (x + 0.12 * L, -w * 0.75 + 0.18 * w * k)])
    return out


def leaf_shape(L, w, veins=2):
    """Leaf along +x from 0 to L with midrib and side veins."""
    out = [lens((0, 0), (L, 0), w / L), [(0, 0), (L * 0.85, 0)]]
    for k in range(veins):
        x = L * (0.3 + 0.25 * k)
        out += [[(x, 0), (x + L * 0.15, w * 0.55)], [(x, 0), (x + L * 0.15, -w * 0.55)]]
    return out


def person_path(pts, n=6):
    return smooth(pts, n, closed=True)


# ---------------------------------------------------------------- mandalas

@design("zen_lotus_mandala", T)
def lotus_mandala(rng):
    out = [circle(0, 0, 0.35, 30), circle(0, 0, 0.6, 40)]
    out += ring(petal(0.6, 1.55, 0.2), 8, R(90))
    out += ring(petal(0.75, 1.3, 0.09), 8, R(90))
    out += [circle(0, 0, 1.75, 100)]
    out += ring(petal(1.75, 2.75, 0.32), 8, R(90) + TAU / 16)
    out += ring(petal(1.75, 2.45, 0.22), 8, R(90))
    out += ring(petal(1.95, 2.45, 0.12), 8, R(90) + TAU / 16)
    hints = [eye(3.0 * math.cos(a), 3.0 * math.sin(a), 0.08) for a in [R(90) + TAU * (k + 0.5) / 8 for k in range(8)]]
    return make("Lotus Petal Mandala", out, hints)


@design("zen_star_mandala", T)
def star_mandala(rng):
    out = [star(0, 0, 1.0, 8, 0.5), circle(0, 0, 0.3, 24), circle(0, 0, 1.2, 80)]
    out.append(star(0, 0, 2.15, 16, 0.6, rot=TAU / 32))
    out.append(circle(0, 0, 2.35, 120))
    out += ring([(2.35, -0.3), (3.1, 0), (2.35, 0.3)], 8, R(90))
    out += ring([(2.35, -0.18), (2.75, 0), (2.35, 0.18)], 8, R(90) + TAU / 16)
    hints = [eye(0.7 * math.cos(a), 0.7 * math.sin(a), 0.06) for a in [R(90) + TAU * k / 8 for k in range(8)]]
    return make("Eight-Point Star Mandala", out, hints)


@design("zen_floral_rosette", T)
def floral_rosette(rng):
    out = [circle(0, 0, 0.3, 24)]
    out += ring(petal(0.3, 1.15, 0.28, pointed=False), 6, R(90))
    out += ring(petal(0.45, 0.95, 0.12, pointed=False), 6, R(90))
    out += [circle(0, 0, 1.3, 90)]
    out += ring(petal(1.3, 2.2, 0.3, pointed=False), 12, R(90) + TAU / 24)
    out += [polar(lambda t: 2.45 + 0.2 * abs(math.cos(12 * t)), n=900, rot=R(90))]
    out += ring(circle(2.85, 0, 0.12, 12), 12, R(90) + TAU / 24)
    return make("Floral Rosette", out)


@design("zen_hexagon_mandala", T)
def hexagon_mandala(rng):
    out = [ngon(0, 0, 0.4, 6, R(90)), ngon(0, 0, 0.85, 6, 0), ngon(0, 0, 1.35, 6, R(90))]
    for k in range(6):
        a = R(90) + TAU * k / 6
        b = a + TAU / 12
        out.append(transform(poly((1.35, 0), (1.95, -0.4), (2.65, 0), (1.95, 0.4)), rot=a))
        out.append(transform(circle(1.95, 0, 0.14, 12), rot=a))
        out.append(transform(circle(1.75, 0, 0.17, 14), rot=b))
        out.append(transform(poly((2.25, -0.28), (2.65, 0), (2.25, 0.28)), rot=b))
    out.append(circle(0, 0, 2.95, 160))
    return make("Hexagon Mandala", out)


@design("zen_sun_mandala", T)
def sun_mandala(rng):
    out = [circle(0, 0, 0.3, 24), circle(0, 0, 0.75, 50), circle(0, 0, 1.15, 70)]
    out += ring(petal(0.3, 0.75, 0.08), 8, R(90))
    out.append(polar(lambda t: 1.15 + 0.18 * abs(math.sin(12 * t)), n=900))
    rays = []
    for k in range(12):
        a = R(90) + TAU * k / 12
        rays.append(transform(chain(cubic((1.45, -0.22), (1.9, -0.35), (2.2, 0.2), (2.9, 0.0), 16),
                                    cubic((2.9, 0.0), (2.3, 0.45), (1.9, 0.05), (1.45, 0.22), 16)), rot=a))
        b = a + TAU / 24
        rays.append(transform([(1.45, -0.12), (2.1, 0), (1.45, 0.12)], rot=b))
    out += rays
    out.append(circle(0, 0, 1.45, 90))
    return make("Radiant Sun Mandala", out)


@design("zen_leaf_mandala", T)
def leaf_mandala(rng):
    out = [circle(0, 0, 0.3, 24)]
    for k in range(6):
        out += [transform(s, rot=R(90) + TAU * k / 6) for s in leaf_shape(1.2, 0.36, 1)]
        out = [s if i < 1 else s for i, s in enumerate(out)]
    out = [out[0]] + [transform(s, dx=0, dy=0) for s in out[1:]]
    out = [out[0]] + [[(x * 1.0, y * 1.0) for x, y in s] for s in out[1:]]
    out.append(circle(0, 0, 1.45, 90))
    for k in range(12):
        a = R(90) + TAU * (k + 0.5) / 12
        out += [transform(s, dx=1.45 * math.cos(a), dy=1.45 * math.sin(a), rot=a) for s in leaf_shape(1.35, 0.4, 2)]
    out.append(circle(0, 0, 3.0, 160))
    hints = [eye(2.55 * math.cos(a), 2.55 * math.sin(a), 0.07) for a in [R(90) + TAU * k / 12 for k in range(12)]]
    return make("Leaf Mandala", out, hints)


@design("zen_feather_mandala", T)
def feather_mandala(rng):
    out = [circle(0, 0, 0.45, 30), circle(0, 0, 0.75, 50)]
    for k in range(10):
        a = R(90) + TAU * k / 10
        out += [transform(s, dx=0.75 * math.cos(a), dy=0.75 * math.sin(a), rot=a) for s in feather_shape(2.2, 0.36, 3)]
    out += ring(circle(0.6, 0, 0.07, 8), 10, R(90) + TAU / 20)
    return make("Feather Mandala", out, [eye(0, 0, 0.12)])


@design("zen_teardrop_mandala", T)
def teardrop_mandala(rng):
    out = [circle(0, 0, 0.5, 36)]
    out += ring(teardrop(0.5, 1.4, 0.32), 8, R(90))
    out += ring(circle(1.1, 0, 0.14, 12), 8, R(90))
    out.append(circle(0, 0, 1.6, 100))
    out += ring(teardrop(1.6, 2.6, 0.28), 12, R(90) + TAU / 24)
    out += ring(teardrop(1.6, 2.05, 0.12), 12, R(90))
    out.append(polar(lambda t: 2.85 + 0.15 * math.cos(24 * t), n=900, rot=R(90)))
    return make("Teardrop Mandala", out)


@design("zen_arch_mandala", T)
def arch_mandala(rng):
    out = [circle(0, 0, 0.35, 24)]
    out += ring(chain(arc(0.35, 0, 0.0001, 0, 0, 1)), 1)
    out = [circle(0, 0, 0.35, 24)]
    for r0, n, rr in [(0.35, 6, 0.55), (1.3, 12, 0.52), (2.2, 18, 0.55)]:
        # n arches standing on circle r0, each a semicircle-ish bump with an inner arch
        out.append(polar(lambda t, r0=r0, n=n, rr=rr: r0 + rr * abs(math.sin(n * t / 2)) ** 0.6, n=900, rot=R(90)))
        out.append(polar(lambda t, r0=r0, n=n, rr=rr: r0 + rr * 0.55 * abs(math.sin(n * t / 2)) ** 0.6, n=900, rot=R(90)))
        out.append(circle(0, 0, r0 + rr + 0.1, 140))
    return make("Rainbow Arch Mandala", out)


@design("zen_square_mandala", T)
def square_mandala(rng):
    out = [rect(-2.9, -2.9, 2.9, 2.9), rect(-2.55, -2.55, 2.55, 2.55)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            out.append(circle(2.72 * sx, 2.72 * sy, 0.12, 12))
    # gates on each side
    for k in range(4):
        out.append(transform(poly((2.55, -0.6), (2.15, -0.6), (2.15, 0.6), (2.55, 0.6), closed=False), rot=TAU * k / 4))
    out.append(circle(0, 0, 2.0, 120))
    out += ring(petal(1.15, 2.0, 0.28, pointed=False), 8, 0)
    out.append(circle(0, 0, 1.15, 80))
    out.append(ngon(0, 0, 1.0, 4, R(45)))
    out.append(ngon(0, 0, 0.7, 4, 0))
    out.append(circle(0, 0, 0.3, 24))
    return make("Square Gate Mandala", out)


@design("zen_swirl_mandala", T)
def swirl_mandala(rng):
    def comma(r0, r1, w, bend):
        pts = [(r0 + (r1 - r0) * i / 20, bend * math.sin(math.pi * i / 20 * 0.9)) for i in range(21)]
        return tube(pts, lambda t: w * (1 - t) ** 0.7 + 0.02)
    out = [circle(0, 0, 0.35, 24)]
    out += ring(comma(0.4, 1.4, 0.4, 0.45), 8, R(90))
    out.append(circle(0, 0, 1.6, 100))
    out += ring(comma(1.7, 2.8, 0.36, 0.4), 12, R(90) + 0.1)
    out.append(circle(0, 0, 3.0, 160))
    return make("Whirling Pinwheel Mandala", out)


@design("zen_dot_mandala", T)
def dot_mandala(rng):
    out = [circle(0, 0, 0.4, 30)]
    for rr, n, cr in [(0.85, 6, 0.25), (1.55, 12, 0.24), (2.25, 16, 0.27), (2.95, 24, 0.2)]:
        out += [circle(rr * math.cos(R(90) + TAU * k / n), rr * math.sin(R(90) + TAU * k / n), cr, 18) for k in range(n)]
    out += [circle(0, 0, 1.2, 80), circle(0, 0, 1.9, 110), circle(0, 0, 2.6, 140)]
    hints = [eye(0, 0, 0.12)] + [eye(1.55 * math.cos(R(90) + TAU * k / 12), 1.55 * math.sin(R(90) + TAU * k / 12), 0.06) for k in range(12)]
    return make("Dot Painting Mandala", out, hints)


@design("zen_moon_mandala", T)
def moon_mandala(rng):
    out = [circle(0, 0, 0.65, 50)]
    out += ring([(0.8, -0.12), (1.25, 0), (0.8, 0.12)], 12, R(90))
    out.append(circle(0, 0, 1.45, 90))
    for k in range(8):
        a = R(90) + TAU * k / 8
        cx, cy = 2.25 * math.cos(a), 2.25 * math.sin(a)
        out.append(circle(cx, cy, 0.48, 36))
        f = k / 8
        if 0 < k < 8 and k != 4:
            # terminator of the phase: an ellipse arc inside the disc
            rx = 0.48 * math.cos(math.pi * f * 2) if k != 0 else 0.48
            out.append([(cx + rx * math.sin(t) * (1 if k < 4 else -1), cy + 0.48 * math.cos(t)) for t in [math.pi * i / 20 for i in range(21)]])
    out.append(circle(0, 0, 3.0, 160))
    return make("Moon Phase Mandala", out, [eye(2.25 * math.cos(R(90) + math.pi), 2.25 * math.sin(R(90) + math.pi), 0.2)])


@design("zen_paisley_mandala", T)
def paisley_mandala(rng):
    out = [circle(0, 0, 0.4, 30), circle(0, 0, 0.8, 50)]
    for k in range(6):
        a = TAU * k / 6
        sh = boteh(1.0)
        inner = transform(boteh(1.0), dy=0.12, s=0.5)
        dot = circle(0, 0.0, 0.14, 12)
        for p in (sh, inner, dot):
            out.append(transform(transform(p, dy=1.45), rot=a))
    out.append(circle(0, 0, 3.15, 170))
    out += ring(circle(2.55, 0, 0.13, 10), 6, TAU / 12 + 0.25)
    return make("Paisley Ring Mandala", out)


@design("zen_lace_mandala", T)
def lace_mandala(rng):
    out = [circle(0, 0, 0.3, 24), polar(lambda t: 0.7 + 0.2 * math.cos(6 * t), n=400)]
    out.append(circle(0, 0, 1.1, 70))
    # loops like crochet chains
    out += ring(ellipse(1.55, 0, 0.42, 0.22, 24), 10, R(90))
    out.append(circle(0, 0, 2.05, 120))
    out += ring(chain(arc(2.05, 0, 0.0, 0, 0, 1)), 1)[0:0]
    out.append(polar(lambda t: 2.35 + 0.35 * abs(math.cos(10 * t)), n=1200, rot=R(90)))
    out += ring(circle(2.5, 0, 0.12, 10), 20, R(90) + TAU / 40)
    return make("Crochet Lace Doily", out)


@design("zen_triangle_mandala", T)
def triangle_mandala(rng):
    out = []
    for k, rr in enumerate([0.34, 0.68, 1.36, 2.72]):
        out.append(ngon(0, 0, rr, 3, R(90) + (math.pi if k % 2 else 0)))
        out.append(circle(0, 0, rr, 160))
    out += ring(petal(2.72, 3.25, 0.2), 12, R(90))
    out += ring(circle(1.85, 0, 0.3, 20), 3, R(-90))
    out += ring(circle(0.95, 0, 0.14, 12), 3, R(90))
    return make("Nested Triangle Mandala", out)


@design("zen_seigaiha_waves", T)
def seigaiha(rng):
    Rr, out = 0.75, []
    centers = []
    for row in range(12):
        y = 3.3 - row * 0.6
        off = 0 if row % 2 == 0 else Rr * 0.95
        for col in range(-4, 5):
            centers.append((col * 1.425 + off, y))
    W, H = 3.0, 2.8
    for i, (cx, cy) in enumerate(centers):
        front = [c for c in centers[i + 1:] if c[1] < cy - 1e-6 and abs(c[0] - cx) < 2 * Rr and cy - c[1] < 2 * Rr]
        for rr in (Rr, Rr * 0.66, Rr * 0.33):
            pts = arc(cx, cy, rr, 0, math.pi, 40)
            out += keep_runs(pts, lambda p: all(math.hypot(p[0] - fx, p[1] - fy) > Rr for fx, fy in front) and abs(p[0]) < W and abs(p[1]) < H)
    out.append(rect(-W, -H, W, H))
    return make("Seigaiha Wave Pattern", out)


@design("zen_asanoha_pattern", T)
def asanoha(rng):
    s = 1.3
    h = s * math.sqrt(3) / 2
    segs = []
    for j in range(-4, 5):
        for i in range(-5, 6):
            x0 = i * s + (j % 2) * s / 2
            y0 = j * h
            a, b, c = (x0, y0), (x0 + s, y0), (x0 + s / 2, y0 + h)
            d = (x0 + s * 1.5, y0 + h)
            for tri in ((a, b, c), (b, d, c)):
                g = ((tri[0][0] + tri[1][0] + tri[2][0]) / 3, (tri[0][1] + tri[1][1] + tri[2][1]) / 3)
                for v in tri:
                    segs.append([v, g])
            segs.append([a, b])
            segs.append([a, c])
            segs.append([b, c])
    out = in_circle(segs, 2.9)
    out.append(circle(0, 0, 2.9, 180))
    return make("Asanoha Hemp Leaf Pattern", out)


@design("zen_paisley_motif", T)
def paisley_motif(rng):
    big = transform(boteh(1.0), dy=-0.9, s=2.3)
    mid = transform(boteh(1.0), dx=0.05, dy=-0.7, s=1.55)
    out = [big, mid]
    out += [circle(0.0, -0.95, 0.25, 18)] + ring(petal(0.25, 0.75, 0.14, pointed=False), 6, R(90), 0.0, -0.95)
    out += [lens((-0.15, 0.2), (0.25, 1.0), 0.3), lens((0.55, 1.45), (0.85, 2.15), 0.3)]
    for k in range(14):
        u = k / 14
        # dots following the outside of the big paisley
        p = big[int(u * (len(big) - 1))]
        q = big[min(len(big) - 1, int(u * (len(big) - 1)) + 1)]
        dx, dy = q[0] - p[0], q[1] - p[1]
        L = math.hypot(dx, dy) or 1
        out.append(circle(p[0] + 0.35 * dy / L, p[1] - 0.35 * dx / L, 0.11, 10))
    return make("Paisley Motif", out)


@design("zen_art_deco_fan", T)
def art_deco_fan(rng):
    out = []
    cx, cy = 0, -2.2
    for rr in (1.0, 2.2, 3.4):
        out.append(arc(cx, cy, rr, 0, math.pi, 80))
    out.append(rrect(-3.6, cy - 0.45, 3.6, cy, 0.1))
    for k in range(1, 12):
        a = math.pi * k / 12
        out.append([(cx + 1.0 * math.cos(a), cy + 1.0 * math.sin(a)), (cx + 2.2 * math.cos(a), cy + 2.2 * math.sin(a))])
    for k in range(1, 8):
        a = math.pi * k / 8
        out.append([(cx + 2.2 * math.cos(a), cy + 2.2 * math.sin(a)), (cx + 3.4 * math.cos(a), cy + 3.4 * math.sin(a))])
    for k in range(8):
        a = math.pi * (k + 0.5) / 8
        out.append(circle(cx + 2.8 * math.cos(a), cy + 2.8 * math.sin(a), 0.15, 12))
        out.append(transform([(3.45, -0.15), (3.85, 0), (3.45, 0.15)], dx=cx, dy=cy, rot=a))
    out += [arc(cx, cy, 0.55, 0, math.pi, 30)]
    return make("Art Deco Fan", out)


@design("zen_moroccan_tile", T)
def moroccan_tile(rng):
    def lantern(cx, cy, s):
        pts = []
        for k in range(4):
            a = TAU * k / 4
            pts += arc(cx + 0.55 * s * math.cos(a), cy + 0.55 * s * math.sin(a), 0.45 * s, a - 1.6, a + 1.6, 16)
        pts.append(pts[0])
        return pts
    g = 2.05
    out = []
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            out.append(lantern(i * g, j * g, 0.95))
            out.append(circle(i * g, j * g, 0.3, 20))
    for i in (-0.5, 0.5):
        for j in (-0.5, 0.5):
            out.append(star(i * g, j * g, 0.42, 4, 0.4, rot=R(45)))
    out.append(rect(-3.25, -3.25, 3.25, 3.25))
    return make("Moroccan Quatrefoil Tile", out)


@design("zen_islamic_star_tile", T)
def islamic_star(rng):
    pts = [(2.2 * math.cos(R(90) + TAU * k * 5 / 12), 2.2 * math.sin(R(90) + TAU * k * 5 / 12)) for k in range(13)]
    out = [pts, circle(0, 0, 2.45, 140), ngon(0, 0, 0.95, 12, R(90) + TAU / 24), circle(0, 0, 0.22, 14)]
    out += ring(petal(0.22, 0.72, 0.13, pointed=False), 6, R(90))
    out.append(rect(-3.0, -3.0, 3.0, 3.0))
    for sx in (-1, 1):
        for sy in (-1, 1):
            out += keep_runs(arc(3.0 * sx, 3.0 * sy, 0.9, 0, TAU, 80), lambda p: abs(p[0]) <= 2.99 and abs(p[1]) <= 2.99)
    return make("Islamic Twelve-Point Star Tile", out)


@design("zen_circle_labyrinth", T)
def labyrinth(rng):
    out = []
    radii = [0.5, 0.95, 1.4, 1.85, 2.3, 2.75]
    gaps = [R(90), R(270), R(90), R(270), R(90), R(270)]
    g = 0.22
    for rr, gp in zip(radii, gaps):
        da = g / rr
        out.append(arc(0, 0, rr, gp + da, gp + TAU - da, 120))
    # radial walls between rings, offset from the gaps
    walls = [(0, R(180)), (1, R(0)), (2, R(180)), (3, R(0)), (4, R(180)), (1, R(200)), (3, R(160))]
    for i, a in walls:
        r0, r1 = radii[i], radii[i + 1]
        out.append([(r0 * math.cos(a), r0 * math.sin(a)), (r1 * math.cos(a), r1 * math.sin(a))])
    return make("Circular Labyrinth", out, [eye(0, 0, 0.15)])


@design("zen_spiral_sun", T)
def spiral_sun(rng):
    out = [spiral(0, 0, 0.05, 1.05, 3.5, 300), circle(0, 0, 1.3, 80)]
    for k in range(14):
        a = R(90) + TAU * k / 14
        flame = chain(cubic((1.3, -0.25), (1.8, -0.3), (2.4, -0.1), (3.0, 0.45), 16), cubic((3.0, 0.45), (2.4, 0.2), (1.9, 0.25), (1.3, 0.25), 16))
        out.append(transform(flame, rot=a))
    return make("Spiral Sun", out)


# dropped: the subject repeats another book
def dreamcatcher(rng):
    cy = 1.0
    out = [circle(0, cy, 1.9, 120), circle(0, cy, 1.7, 110)]
    n = 8
    rr = 1.7
    prev = [(rr * math.cos(R(90) + TAU * k / n), cy + rr * math.sin(R(90) + TAU * k / n)) for k in range(n)]
    for lvl in range(3):
        nxt = []
        rr *= 0.62
        for k in range(n):
            a = R(90) + TAU * (k + 0.5 * (lvl + 1)) / n
            nxt.append((rr * math.cos(a), cy + rr * math.sin(a)))
        web = []
        for k in range(n):
            web += [prev[k], nxt[k]]
        web.append(prev[0])
        out.append(web)
        prev = nxt
    out.append(circle(0, cy, 0.25, 16))
    for x, L in [(-1.2, 1.8), (0, 2.2), (1.2, 1.8)]:
        top = (x, cy - math.sqrt(max(0, 1.9 ** 2 - x * x)))
        out.append([top, (x, top[1] - 0.6)])
        out.append(circle(x, top[1] - 0.75, 0.15, 12))
        out += [transform(s, dx=x, dy=top[1] - 0.9, rot=R(-90)) for s in feather_shape(L - 0.3, 0.32, 2)]
    out.append([(0, cy + 1.9), (0, cy + 2.4)])
    out.append(circle(0, cy + 2.55, 0.15, 12))
    return make("Dreamcatcher with Feathers", out)


@design("zen_zentangle_feather", T)
def zentangle_feather(rng):
    spine = cubic((0.9, -3.2), (0.3, -1.0), (-0.1, 1.2), (-1.0, 3.2), 80)

    def at(t, off):
        i = min(len(spine) - 2, int(t * (len(spine) - 1)))
        (x0, y0), (x1, y1) = spine[i], spine[i + 1]
        L = math.hypot(x1 - x0, y1 - y0)
        return (x0 - off * (y1 - y0) / L, y0 + off * (x1 - x0) / L)

    def wl(t):
        u = (t - 0.25) / 0.75
        if u <= 0:
            return 0.0
        return 1.05 * min(1, u / 0.15) ** 0.6 * math.sqrt(max(0.0, 1 - u ** 3))

    notch_l, notch_r = 0.55, 0.45

    def edge(sgn, scale, notch):
        pts = []
        for i in range(81):
            t = 0.25 + 0.75 * i / 80
            w = wl(t) * scale
            if abs(t - notch) < 0.035:
                w *= 0.55 + 0.45 * abs(t - notch) / 0.035
            pts.append(at(t, sgn * w))
        return pts
    left = edge(1, 1.0, notch_l)
    right = edge(-1, 0.75, notch_r)
    out = [spine, left, right]
    # fluffy down at the base
    for sgn in (1, -1):
        for k, t in enumerate((0.17, 0.21, 0.25)):
            p = at(t, 0)
            q = at(t + 0.06, sgn * (0.75 - 0.15 * k))
            r = at(t + 0.02, sgn * (1.0 - 0.15 * k))
            out.append(quad(p, q, r, 10))
    # bands following the barbs
    for t in (0.36, 0.66, 0.8):
        out.append([at(t, 0), at(t + 0.06, 0.98 * wl(t + 0.06))])
    for t in (0.33, 0.6, 0.78):
        out.append([at(t, 0), at(t + 0.06, -0.73 * wl(t + 0.06))])
    # simple fills
    out += [circle(*at(0.36, 0.55), 0.13, 12), circle(*at(0.4, 0.3), 0.11, 10), circle(*at(0.43, 0.7), 0.11, 10)]
    out += [[at(0.5, 0.15), at(0.47, 0.4), at(0.5, 0.65), at(0.47, 0.85)], [at(0.6, 0.15), at(0.57, 0.4), at(0.6, 0.65)]]
    out += [lens(at(0.74, 0.12), at(0.77, 0.75), 0.25)]
    out += [circle(*at(0.88, 0.3), 0.12, 10)]
    out += [lens(at(0.4, -0.12), at(0.45, -0.6), 0.25), [at(0.52, -0.15), at(0.55, -0.35), at(0.52, -0.55)]]
    out += [circle(*at(0.69, -0.35), 0.13, 12), circle(*at(0.87, -0.2), 0.1, 10)]
    return make("Zentangle Feather", out)


def in_shape(strokes, shape):
    out = []
    for s in strokes:
        out += keep_runs(s, lambda p: inside(p, shape))
    return out


@design("zen_zentangle_leaf", T)
def zentangle_leaf(rng):
    side = smooth([(0, -2.6), (1.1, -1.9), (1.55, -0.4), (1.3, 1.2), (0.6, 2.4), (0, 3.2)], 10)
    outline = chain(side, mirror_x(side)[::-1])
    stem = [(0, -3.3), (0, 2.9)]
    veins = []
    for y in (-1.9, -0.8, 0.3, 1.4):
        veins += [quad((0, y), (0.8, y + 0.35), (1.8, y + 1.5), 12), quad((0, y), (-0.8, y + 0.35), (-1.8, y + 1.5), 12)]
    out = [outline, stem] + in_shape(veins, outline)
    for sg in (1, -1):
        out += [circle(sg * 0.5, -1.65, 0.14, 12), circle(sg * 0.95, -1.5, 0.14, 12), circle(sg * 0.75, -1.15, 0.12, 10)]
        out += [[(sg * 0.3, -0.35), (sg * 0.55, 0.0), (sg * 0.8, -0.3), (sg * 1.05, 0.05), (sg * 1.25, -0.15)]]
        out += [arc(sg * 0.65, 0.95, 0.25, 0, math.pi, 12), arc(sg * 0.65, 0.95, 0.45, 0.15, math.pi - 0.15, 14)]
        out += [lens((sg * 0.25, 2.0), (sg * 0.7, 2.25), 0.3)]
    return make("Zentangle Leaf", out)


@design("zen_flower_of_life", T)
def flower_of_life(rng):
    d = 0.72
    centers = [(0, 0)]
    for k in range(6):
        a = R(90) + TAU * k / 6
        centers.append((d * math.cos(a), d * math.sin(a)))
        centers.append((2 * d * math.cos(a), 2 * d * math.sin(a)))
        b = a + TAU / 12
        centers.append((d * math.sqrt(3) * math.cos(b), d * math.sqrt(3) * math.sin(b)))
    out = [circle(x, y, d, 60) for x, y in centers]
    out += [circle(0, 0, 3 * d, 160), circle(0, 0, 3 * d + 0.3, 170)]
    return make("Flower of Life", out)


@design("zen_metatrons_cube", T)
def metatron(rng):
    d = 1.25
    pts = [(0, 0)]
    inner = [(d * math.cos(R(90) + TAU * k / 6), d * math.sin(R(90) + TAU * k / 6)) for k in range(6)]
    outer = [(2 * d * math.cos(R(90) + TAU * k / 6), 2 * d * math.sin(R(90) + TAU * k / 6)) for k in range(6)]
    out = [circle(x, y, 0.32, 20) for x, y in [(0, 0)] + inner + outer]
    segs = []
    allp = [(0, 0)] + inner + outer
    for i in range(len(allp)):
        for j in range(i + 1, len(allp)):
            segs.append((allp[i], allp[j]))
    # keep only edges of the classic figure: outer hexagon, inner hexagon, spokes, outer triangles, outer-to-inner links
    keep = []
    for k in range(6):
        keep.append((outer[k], outer[(k + 1) % 6]))
        keep.append((inner[k], inner[(k + 1) % 6]))
        keep.append((outer[k], outer[(k + 2) % 6]))
        keep.append((outer[k], inner[(k + 1) % 6]))
        keep.append((outer[k], inner[(k - 1) % 6]))
        keep.append(((0, 0), outer[k]))
    lines = []
    for a, b in keep:
        lines += hide([[a, b]], *[circle(x, y, 0.32, 20) for x, y in allp])
    return make("Metatron's Cube", out + lines)


@design("zen_tree_of_life", T)
def tree_of_life(rng):
    out = [circle(0, 0, 3.0, 180)]
    trunk = cubic((-0.35, -1.4), (-0.25, -0.6), (-0.25, 0.0), (-0.15, 0.4), 12)
    half = [trunk]
    leaves = []
    for a, bend in [(R(20), 0.45), (R(50), 0.3), (R(78), 0.12)]:
        end = (2.95 * math.cos(a), 2.95 * math.sin(a))
        mid = (0.5 * end[0] + 0.1, 0.4 + 0.5 * (end[1] - 0.4) - bend)
        br = quad((0.15, 0.4), mid, end, 20)
        half.append(br)
        for k, u in enumerate((0.3, 0.48, 0.66, 0.84)):
            i = int(u * 20)
            p, q = br[i], br[i + 1]
            ang = math.atan2(q[1] - p[1], q[0] - p[0]) + (0.75 if k % 2 == 0 else -0.75)
            leaves.append(lens(p, (p[0] + 0.6 * math.cos(ang), p[1] + 0.6 * math.sin(ang)), 0.3))
    for a in (R(-25), R(-55), R(-80)):
        end = (2.95 * math.cos(a), 2.95 * math.sin(a))
        half.append(quad((0.35, -1.4), (end[0] * 0.4 + 0.1, -1.5), end, 16))
    out += half + [mirror_x(s) for s in half[1:]] + [mirror_x(trunk)]
    out += in_circle(leaves + [mirror_x(l) for l in leaves], 2.9)
    out.append([(0, 0.45), (0, 2.95)])
    out += [lens((0, 1.2), (0.55, 1.5), 0.3), lens((0, 1.75), (-0.55, 2.05), 0.3), lens((0, 2.3), (0.5, 2.55), 0.3)]
    return make("Tree of Life Circle", out)


@design("zen_mountain_sunrise", T)
def mountain_sunrise(rng):
    back = [(-3.2, -0.6), (-2.1, 1.4), (-1.0, 0.25), (-0.5, 0.55), (0.1, 0.0), (1.4, 1.7), (2.3, 0.7), (3.2, 1.1), (3.2, -0.6)]
    sun = [arc(-0.3, 0.25, 0.85, 0, math.pi, 50)]
    sun += [[(-0.3 + 1.1 * math.cos(a), 0.25 + 1.1 * math.sin(a)), (-0.3 + 1.55 * math.cos(a), 0.25 + 1.55 * math.sin(a))]
            for a in [math.pi * (k + 0.5) / 8 for k in range(8)]]
    front_l = smooth([(-3.2, -0.2), (-2.4, 0.15), (-1.4, -0.1), (-0.6, -0.6)], 8)
    front_r = smooth([(0.4, -0.6), (1.5, 0.05), (2.5, -0.15), (3.2, 0.1)], 8)
    fl = chain(front_l, [(-3.2, -0.6)])
    fr = chain(front_r, [(3.2, -0.6)])
    out = hide(sun, poly(*back))
    out += hide([back[:-1]], fl, fr)
    out += [front_l, front_r, [(-3.2, -0.6), (3.2, -0.6)]]
    out.append(poly((1.05, 1.25), (1.4, 1.7), (1.8, 1.2), (1.55, 1.35), (1.35, 1.15), (1.2, 1.35), closed=True))
    out.append(poly((-2.4, 1.0), (-2.1, 1.4), (-1.75, 1.0), (-1.95, 1.1), (-2.1, 0.9), (-2.25, 1.1), closed=True))
    for j, half in enumerate([1.0, 0.75, 0.5, 0.3]):
        y = -1.0 - 0.38 * j
        out.append([(-0.3 - half, y), (-0.3 + half, y)])
    out += [[(-2.8, -1.3), (-1.9, -1.3)], [(1.4, -1.5), (2.6, -1.5)], [(-2.4, -2.1), (-1.4, -2.1)], [(1.0, -2.3), (1.9, -2.3)]]
    cloud = chain(arc(-2.0, 2.2, 0.35, math.pi, 0, 12), arc(-1.45, 2.35, 0.4, math.pi, 0, 12), arc(-0.9, 2.2, 0.3, math.pi, 0, 12))
    cloud.append(cloud[0])
    cloud2 = chain(arc(1.7, 2.6, 0.28, math.pi, 0, 10), arc(2.2, 2.7, 0.32, math.pi, 0, 10), arc(2.65, 2.6, 0.22, math.pi, 0, 10))
    cloud2.append(cloud2[0])
    out += [cloud, cloud2]
    return make("Mountain Sunrise Calm", out)


# dropped: the subject repeats another book
def crescent_moon(rng):
    outer = arc(0, 0, 2.6, R(55), R(305), 120)
    p0, p1 = outer[0], outer[-1]
    inner = quad(p1, (0.0, 0.0), p0, 40)
    inner = cubic(p1, (0.0, -1.6), (0.0, 1.6), p0, 40)
    moon = chain(outer, inner)
    bands = []
    for rr in (2.2, 1.8):
        bands += in_shape([arc(0, 0, rr, R(60), R(300), 100)], moon)
    stars = [star(1.7, 1.4, 0.45, 5, 0.45), star(2.4, -0.4, 0.3, 5, 0.45), star(1.2, -1.8, 0.35, 5, 0.45), star(2.5, 2.4, 0.25, 5, 0.45)]
    strings = [[(1.7, 1.85), (1.7, 3.0)], [(2.5, 2.65), (2.5, 3.0)]]
    dots = [circle(-1.95, 0.0, 0.15, 12), circle(-1.75, 1.0, 0.15, 12), circle(-1.75, -1.0, 0.15, 12), circle(-1.3, 1.75, 0.15, 12), circle(-1.3, -1.75, 0.15, 12)]
    return make("Crescent Moon and Hanging Stars", [moon] + bands + stars + strings + dots)


@design("zen_starburst", T)
def starburst(rng):
    out = [circle(0, 0, 0.6, 40), circle(0, 0, 0.9, 50)]
    pts = []
    for k in range(48):
        a = R(90) + TAU * k / 48
        rr = [3.0, 1.4, 2.2, 1.4][k % 4]
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    pts.append(pts[0])
    out.append(pts)
    out += ring([(0.9, 0), (1.4, 0)], 12, R(90))[0:0]
    for k in range(12):
        a = R(90) + TAU * k / 12
        out.append([(0.9 * math.cos(a), 0.9 * math.sin(a)), (1.25 * math.cos(a), 1.25 * math.sin(a))])
    return make("Mid-Century Starburst", out)


@design("zen_peacock_fan", T)
def peacock_fan(rng):
    out = []
    for k in range(7):
        a = R(30) + math.pi * 2 / 3 * k / 6
        ex, ey = 2.5 * math.cos(a), -2.6 + 2.5 * math.sin(a) + 0.3
        stem = [(0, -2.6), (ex - 0.6 * math.cos(a), ey - 0.6 * math.sin(a))]
        eye_o = ellipse(ex, ey, 0.6, 0.42, 36, rot=a)
        eye_m = ellipse(ex + 0.06 * math.cos(a), ey + 0.06 * math.sin(a), 0.36, 0.26, 28, rot=a)
        out += [stem, eye_o, eye_m]
        for side in (-1, 1):
            b = a + side * 0.22
            out.append(quad((1.0 * math.cos(a), -2.6 + 1.0 * math.sin(a)), (1.9 * math.cos(b), -2.6 + 1.9 * math.sin(b)),
                            (ex + 0.5 * math.cos(a + side * 1.3), ey + 0.5 * math.sin(a + side * 1.3)), 10))
    hints = []
    for k in range(7):
        a = R(30) + math.pi * 2 / 3 * k / 6
        hints.append(eye(2.5 * math.cos(a) + 0.08 * math.cos(a), -2.3 + 2.5 * math.sin(a) + 0.08 * math.sin(a), 0.12))
    out.append(arc(0, -2.6, 0.4, 0, math.pi, 16))
    return make("Peacock Feather Fan", out, hints)


@design("zen_kaleidoscope", T)
def kaleidoscope(rng):
    out = [ngon(0, 0, 3.0, 6, R(90))]
    for k in range(6):
        a = R(90) + TAU * k / 6
        out.append(transform(poly((0.5, 0), (1.3, 0.35), (2.0, 0), (1.3, -0.35)), rot=a))
        out.append(transform(circle(2.45, 0, 0.22, 16), rot=a))
        b = a + TAU / 12
        out.append(transform(poly((1.25, -0.22), (1.75, 0), (1.25, 0.22), (1.05, 0)), rot=b))
        out.append(transform(poly((2.05, -0.35), (2.45, 0), (2.05, 0.35)), rot=b))
    out.append(ngon(0, 0, 0.5, 6, 0))
    out.append(circle(0, 0, 0.22, 14))
    return make("Kaleidoscope Pattern", out)


@design("zen_gothic_rosette", T)
def rosette(rng):
    out = [circle(0, 0, 3.0, 180), circle(0, 0, 2.7, 170), circle(0, 0, 0.8, 50)]
    out += ring(circle(0.45, 0, 0.18, 12), 6, R(90))
    for k in range(12):
        a = R(90) + TAU * k / 12
        lancet = chain([(0.95, -0.25), (2.05, -0.25)], quad((2.05, -0.25), (2.55, -0.1), (2.55, 0.0), 6), quad((2.55, 0.0), (2.55, 0.1), (2.05, 0.25), 6),
                       [(0.95, 0.25)], quad((0.95, 0.25), (0.85, 0.0), (0.95, -0.25), 4))
        out.append(transform(lancet, rot=a))
        out.append(transform(circle(1.9, 0, 0.1, 8), rot=a)[0:0] or transform([(1.15, 0), (2.0, 0)], rot=a))
    return make("Circular Rosette Window", out)


@design("zen_folding_fan_waves", T)
def folding_fan(rng):
    cx, cy = 0, -2.2
    r0, r1 = 0.9, 3.6
    a0, a1 = R(20), R(160)
    out = [arc(cx, cy, r1, a0, a1, 80), arc(cx, cy, r0, a0, a1, 30)]
    n = 14
    for k in range(n + 1):
        a = a0 + (a1 - a0) * k / n
        out.append([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))])
    out += [[(cx, cy - 0.2), (cx + r0 * math.cos(a), cy + r0 * math.sin(a))] for a in (a0, a1)]
    out.append(circle(cx, cy - 0.2, 0.15, 12))
    # wave pattern band across the leaf
    fan_area = chain(arc(cx, cy, r1, a0, a1, 60), arc(cx, cy, r0, a1, a0, 30))
    waves = []
    for rr in (1.75, 2.75):
        waves.append([(cx + (rr + 0.14 * math.sin(7 * t)) * math.cos(t), cy + (rr + 0.18 * math.sin(10 * t)) * math.sin(t)) for t in [a0 + (a1 - a0) * i / 200 for i in range(201)]])
    out = out[:2] + hide(out[2:], *[]) + in_shape(waves, fan_area)
    out = [s for s in out]
    tassel = [[(cx, cy - 0.35), (cx, cy - 0.8)], poly((cx - 0.15, cy - 0.8), (cx + 0.15, cy - 0.8), (cx + 0.25, cy - 1.4), (cx - 0.25, cy - 1.4))]
    return make("Folding Fan with Waves", out + tassel)


# ---------------------------------------------------------------- calm scenes and symbols

@design("zen_meditating_figure", T)
def meditating(rng):
    half = [(0.0, 1.05), (0.22, 1.05), (0.25, 0.85), (0.8, 0.7), (1.05, 0.35), (1.15, -0.4), (1.45, -0.95), (1.85, -1.15), (2.35, -1.3),
            (2.55, -1.55), (2.3, -1.85), (1.3, -2.0), (0.0, -1.95)]
    sil = smooth(half + [(-x, y) for x, y in half[::-1][1:-1]], 6, closed=True)
    head = ellipse(0, 1.65, 0.48, 0.58, 40)
    bun = circle(0, 2.35, 0.2, 16)
    holes = [smooth([(0.55, 0.35), (0.85, 0.15), (0.95, -0.45), (0.75, -0.8), (0.55, -0.5), (0.5, 0.0)], 6, closed=True)]
    holes.append(mirror_x(holes[0]))
    hands = [ellipse(1.75, -1.1, 0.28, 0.16, 16, rot=-0.3), mirror_x(ellipse(1.75, -1.1, 0.28, 0.16, 16, rot=-0.3))]
    legs = [cubic((-2.3, -1.6), (-1.0, -1.35), (0.5, -1.6), (1.2, -1.85), 20), cubic((2.3, -1.6), (1.3, -1.45), (0.4, -1.5), (-0.2, -1.65), 12)]
    feet = [ellipse(1.3, -1.6, 0.3, 0.13, 16, rot=0.1), ellipse(-1.2, -1.75, 0.3, 0.12, 14, rot=-0.1)]
    aura = arc(0, 0.6, 2.9, R(-15), R(195), 120)
    cushion = ellipse(0, -2.3, 2.7, 0.35, 60)
    lotus = [lens((0, 2.75), (0, 3.4), 0.3), lens((-0.3, 2.75), (-0.65, 3.2), 0.3), lens((0.3, 2.75), (0.65, 3.2), 0.3)]
    return make("Meditation in Lotus Pose", [sil, head, bun, aura] + holes + hands + legs + [cushion] + lotus[0:0])


@design("zen_enso_circle", T)
def enso(rng):
    pts = [(2.3 * math.cos(t), 2.3 * math.sin(t)) for t in [R(-60) + R(330) * i / 120 for i in range(121)]]
    stroke = tube(pts, lambda t: 0.08 + 0.42 * math.sin(math.pi * min(1, t * 1.15)) ** 0.7)
    seal = [rrect(2.0, -2.9, 2.7, -2.2, 0.08), rrect(2.15, -2.75, 2.55, -2.35, 0.04)]
    splash = [circle(1.55, -1.6, 0.1, 10), circle(1.85, -1.5, 0.07, 8)]
    return make("Enso Brush Circle", [stroke] + seal + splash[0:1])


@design("zen_yin_yang", T)
def yin_yang(rng):
    out = [circle(0, 0, 2.0, 140), chain(arc(0, 1.0, 1.0, R(90), R(270), 40), arc(0, -1.0, 1.0, R(90), R(-90), 40))]
    out += [circle(0, 1.0, 0.3, 20), circle(0, -1.0, 0.3, 20)]
    out.append(circle(0, 0, 2.3, 150))
    out += ring(chain(cubic((2.3, 0), (2.7, 0.1), (2.9, 0.35), (2.6, 0.5), 10), cubic((2.6, 0.5), (2.4, 0.5), (2.45, 0.3), (2.6, 0.3), 6)), 12)
    return make("Yin Yang Balance", out, [eye(0, -1.0, 0.25)])


@design("zen_rock_garden", T)
def rock_garden(rng):
    W, H = 3.2, 2.4
    rocks = [((-1.5, 0.6), 0.55, 0.4), ((1.3, -0.7), 0.7, 0.5), ((1.9, 1.4), 0.3, 0.22)]
    rock_shapes = []
    rings_ = []
    for (x, y), rx, ry in rocks:
        sh = smooth([(x - rx, y - ry * 0.6), (x - rx * 0.6, y + ry * 0.7), (x + rx * 0.1, y + ry), (x + rx * 0.8, y + ry * 0.4),
                     (x + rx, y - ry * 0.5), (x, y - ry), (x - rx, y - ry * 0.6)], 6, closed=True)
        rock_shapes.append(sh)
        for k in (1, 2, 3):
            rings_.append(ellipse(x, y, rx + 0.28 * k, ry + 0.28 * k, 80))
    ring_zones = [ellipse(x, y, rx + 0.28 * 3 + 0.12, ry + 0.28 * 3 + 0.12, 80) for (x, y), rx, ry in rocks]
    lines = []
    y = -H + 0.3
    while y < H - 0.15:
        lines.append(wave(-W, W, y, 0.05, 3, 120))
        y += 0.32
    out = hide(lines, *ring_zones)
    out += hide(rings_, *rock_shapes)
    out = [s for s in out if all(abs(p[0]) <= W and abs(p[1]) <= H for p in s)] + [s2 for s in [] for s2 in s]
    clipped = []
    for s in hide(rings_, *rock_shapes):
        clipped += keep_runs(s, lambda p: abs(p[0]) < W - 0.05 and abs(p[1]) < H - 0.05)
    out = hide(lines, *ring_zones) + clipped + rock_shapes + [rect(-W, -H, W, H), rect(-W - 0.25, -H - 0.25, W + 0.25, H + 0.25)]
    return make("Raked Zen Rock Garden", out)


@design("zen_balanced_cairn", T)
def cairn(rng):
    stones = [(0, -1.9, 1.5, 0.55), (0.1, -0.95, 1.2, 0.42), (-0.05, -0.15, 0.95, 0.38), (0.05, 0.55, 0.72, 0.32), (0.0, 1.13, 0.5, 0.26), (0.02, 1.58, 0.3, 0.19)]
    out = []
    for x, y, rx, ry in stones:
        out.append(smooth([(x - rx, y), (x - rx * 0.7, y + ry * 0.95), (x + rx * 0.3, y + ry), (x + rx, y + ry * 0.2), (x + rx * 0.7, y - ry * 0.9),
                           (x - rx * 0.4, y - ry), (x - rx, y)], 8, closed=True))
    out += [wave(-3.2, 3.2, -2.55, 0.06, 4), wave(-2.6, 2.6, -2.9, 0.05, 3)]
    out = hide(out[:-2], ) + out[-2:]
    out = [out[0]] + out[1:]
    out += hide([wave(-3.2, 3.2, -2.55, 0.06, 4)], out[0])[0:0]
    birds_ = [quad((-2.6, 2.1), (-2.35, 2.35), (-2.1, 2.1), 6) + quad((-2.1, 2.1), (-1.85, 2.35), (-1.6, 2.1), 6)[1:]]
    sun = [circle(2.2, 2.0, 0.55, 40)]
    return make("Balanced Stone Cairn", hide(out, ) + birds_ + sun)


def bamboo_stalk(x, y0, y1, w, nodes):
    pts = [(x + 0.08 * math.sin(i / 10), y0 + (y1 - y0) * i / 30) for i in range(31)]
    out = [tube(pts, w, cap=False)]
    for k in range(1, nodes):
        yy = y0 + (y1 - y0) * k / nodes
        xx = x + 0.08 * math.sin(30 * k / nodes / 10)
        out.append(quad((xx - w / 2, yy), (xx, yy + 0.08), (xx + w / 2, yy), 6))
    return out


@design("zen_bamboo_grove", T)
def bamboo(rng):
    out = []
    for x, w, n, y1 in [(-2.2, 0.38, 5, 3.0), (-0.9, 0.48, 6, 3.2), (0.5, 0.42, 5, 3.0), (1.8, 0.34, 4, 2.6), (2.8, 0.3, 4, 3.1)]:
        out += bamboo_stalk(x, -3.0, y1, w, n)
    leaves = []
    for (x, y, d) in [(-2.0, 1.4, 1), (-0.7, 2.2, -1), (0.7, 0.6, 1), (1.95, 1.8, -1), (-0.65, -0.4, 1), (2.9, 0.2, -1)]:
        tip = (x + 0.9 * d, y + 0.35)
        twig = [(x, y), (x + 0.35 * d, y + 0.1)]
        leaves += [twig, lens((x + 0.35 * d, y + 0.1), (x + 1.3 * d, y + 0.5), 0.2), lens((x + 0.35 * d, y + 0.1), (x + 1.25 * d, y - 0.35), 0.2)]
    stalk_shapes = [s for s in out if len(s) > 30]
    return make("Bamboo Grove", out + hide(leaves, *stalk_shapes))


def koi(spine, W):
    def wid(t):
        if t < 0.2:
            return W * math.sqrt(t / 0.2)
        return W * (1 - 0.8 * ((t - 0.2) / 0.8) ** 1.2)
    n = len(spine)
    left, right, norms = [], [], []
    for i, (x, y) in enumerate(spine):
        a, b = spine[max(0, i - 1)], spine[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        nx, ny = -dy / L, dx / L
        norms.append((nx, ny))
        w = wid(i / (n - 1)) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    body = chain(left, right[::-1], [left[0]])
    tx, ty = spine[-1]
    px, py = spine[-3]
    a = math.atan2(ty - py, tx - px)
    tail = [lens((tx, ty), (tx + 1.2 * W * math.cos(a + 0.5), ty + 1.2 * W * math.sin(a + 0.5)), 0.32),
            lens((tx, ty), (tx + 1.2 * W * math.cos(a - 0.5), ty + 1.2 * W * math.sin(a - 0.5)), 0.32)]
    i = int(0.28 * (n - 1))
    (x, y), (nx, ny) = spine[i], norms[i]
    b = math.atan2(spine[i + 1][1] - y, spine[i + 1][0] - x)
    fins = []
    for sgn in (1, -1):
        base = (x + sgn * nx * W * 0.4, y + sgn * ny * W * 0.4)
        fins.append(lens(base, (base[0] + 0.6 * W * math.cos(b + sgn * 2.2), base[1] + 0.6 * W * math.sin(b + sgn * 2.2)), 0.35))
    j = int(0.5 * (n - 1))
    spots = [ellipse(spine[j][0], spine[j][1], 0.28 * W, 0.18 * W, 18, rot=b), ellipse(spine[int(0.25 * (n - 1))][0], spine[int(0.25 * (n - 1))][1], 0.2 * W, 0.14 * W, 14, rot=b)]
    k = int(0.07 * (n - 1))
    hints = [eye(spine[k][0] + sgn * norms[k][0] * W * 0.3, spine[k][1] + sgn * norms[k][1] * W * 0.3, 0.05) for sgn in (1, -1)]
    return [body] + hide(tail + fins, body) + spots, hints


@design("zen_koi_pond", T)
def koi_pond(rng):
    s1 = [(1.65 * math.cos(t), 1.65 * math.sin(t)) for t in [R(105) + R(125) * i / 30 for i in range(31)]]
    s2 = [(-x, -y) for x, y in s1]
    f1, h1 = koi(s1, 0.72)
    f2, h2 = koi(s2, 0.72)
    pads = []
    for x, y, r in [(2.4, 2.2, 0.6), (-2.4, -2.1, 0.65), (2.6, -2.3, 0.45)]:
        pads.append(chain(arc(x, y, r, R(20), R(340), 40), [(x, y)], [(x + r * math.cos(R(20)), y + r * math.sin(R(20)))]))
    ripples = [circle(0, 0, 0.3, 20), circle(0, 0, 0.6, 30)]
    blossom = [circle(-2.4, 2.2, 0.15, 12)] + ring(petal(0.15, 0.5, 0.12, pointed=False), 5, R(90), -2.4, 2.2)
    return make("Koi Pond", f1 + f2 + pads + ripples + blossom, h1 + h2)


@design("zen_incense_smoke", T)
def incense(rng):
    bowl = chain(arc(0, -1.9, 1.3, R(190), R(350), 40))
    bowl = chain([(-1.35, -1.9)], cubic((-1.35, -1.9), (-1.3, -2.8), (1.3, -2.8), (1.35, -1.9), 30), [(-1.35, -1.9)])
    rim = ellipse(0, -1.9, 1.35, 0.25, 50)
    foot = poly((-0.6, -2.6), (-0.75, -2.95), (0.75, -2.95), (0.6, -2.6), closed=False)
    stick = tube([(0.0, -1.85), (0.3, 0.3)], 0.12)
    ember = circle(0.3, 0.35, 0.09, 10)
    smoke = [smooth([(0.3, 0.5), (0.1, 1.0), (0.6, 1.5), (0.2, 2.1), (-0.5, 2.3), (-0.6, 1.8), (-0.2, 1.7), (-0.25, 2.0)], 8),
             smooth([(0.35, 0.5), (0.65, 1.0), (0.35, 1.6), (0.9, 2.3), (1.5, 2.5), (1.6, 2.0), (1.25, 2.0), (1.3, 2.2)], 8),
             smooth([(0.2, 2.4), (0.4, 2.8), (0.0, 3.1), (-0.3, 3.0)], 8)]
    return make("Incense Stick and Smoke Swirls", [bowl, rim, foot, stick] + smoke, [ember])


@design("zen_singing_bowl", T)
def singing_bowl(rng):
    rim = ellipse(0, 0.2, 2.0, 0.45, 70)
    inner = ellipse(0, 0.2, 1.75, 0.33, 60)
    body = chain([(-2.0, 0.2)], cubic((-2.0, 0.2), (-2.0, -1.7), (2.0, -1.7), (2.0, 0.2), 40))
    bands = in_shape([cubic((-2.0, -0.2), (-1.9, -0.6), (1.9, -0.6), (2.0, -0.2), 30)], chain(body, [(-2.0, 0.2)]))
    band = [cubic((-1.97, -0.25), (-1.6, -0.75), (1.6, -0.75), (1.97, -0.25), 30)]
    cushion = smooth([(-2.4, -1.4), (-1.6, -1.15), (0, -1.1), (1.6, -1.15), (2.4, -1.4), (2.6, -1.8), (2.0, -2.15), (0, -2.2), (-2.0, -2.15), (-2.6, -1.8)], 6, closed=True)
    cushion = hide([cushion], chain(body, [(-2.0, 0.2)]))
    mallet = [tube([(1.2, -2.6), (3.1, -1.6)], 0.2), rrect(-0.0, -0.0, 0.0, 0.0, 0)[0:0]]
    waves = [arc(0, 0.2, 2.5, R(60), R(120), 20), arc(0, 0.2, 2.85, R(55), R(125), 24), arc(0, 0.2, 3.2, R(50), R(130), 28)]
    return make("Singing Bowl", [rim, inner, body] + band + cushion + mallet[:1] + waves)


# dropped: the subject repeats another book
def paper_lantern(rng):
    out = [rrect(-0.9, 2.0, 0.9, 2.4, 0.08), rrect(-0.9, -2.4, 0.9, -2.0, 0.08)]
    sil = chain(cubic((-0.85, 2.0), (-2.6, 1.3), (-2.6, -1.3), (-0.85, -2.0), 30))
    out += [sil, mirror_x(sil)]
    for k in range(1, 8):
        y = 2.0 - 4.0 * k / 8
        t = k / 8
        # width of the lantern at height y
        xw = 0.85 + (2.6 - 0.85) * 0.75 * math.sin(math.pi * t) * 1.05
        out.append(quad((-xw + 0.05, y), (0, y - 0.12), (xw - 0.05, y), 12))
    out = out[:4] + in_shape(out[4:], chain(sil, mirror_x(sil)[::-1]))
    out += [[(0, 2.4), (0, 3.1)], circle(0, 3.2, 0.12, 10), [(0, -2.4), (0, -2.75)], poly((-0.25, -2.75), (0.25, -2.75), (0.35, -3.3), (-0.35, -3.3))]
    mon = [circle(0, 0, 0.7, 40), circle(0, 0, 0.25, 16)]
    out = hide(out, circle(0, 0, 0.7, 40)) + mon
    return make("Japanese Paper Lantern", out)


@design("zen_tree_pose", T)
def tree_pose(rng):
    right = [(0.0, 3.0), (0.25, 2.75), (0.95, 2.05), (1.05, 1.8), (0.85, 1.15), (0.7, 0.85), (0.55, 0.45), (0.45, -0.2), (0.55, -0.65),
             (1.05, -0.62), (1.5, -0.75), (1.6, -0.97), (1.42, -1.17), (0.6, -1.32), (0.2, -1.3), (0.06, -1.45), (0.04, -1.95), (0.0, -2.7),
             (0.12, -2.95)]
    left = [(-0.6, -2.98), (-0.38, -2.75), (-0.36, -1.9), (-0.42, -1.0), (-0.5, -0.6), (-0.45, -0.2), (-0.55, 0.45), (-0.7, 0.85),
            (-0.85, 1.15), (-1.05, 1.8), (-0.95, 2.05), (-0.25, 2.75)]
    sil = smooth(right + left, 5, closed=True)
    hole = smooth([(0.6, -0.86), (1.25, -0.92), (0.65, -1.12)], 4, closed=True)
    arm_in = smooth([(0.0, 2.72), (0.72, 1.95), (0.55, 1.15), (0.2, 0.98), (-0.2, 0.98), (-0.55, 1.15), (-0.72, 1.95), (0.0, 2.72)], 6, closed=True)
    head = ellipse(0, 1.45, 0.3, 0.36, 30)
    mat = rrect(-2.6, -3.3, 2.6, -3.05, 0.1)
    return make("Yoga Tree Pose", [sil, hole, arm_in, head, mat])


@design("zen_warrior_pose", T)
def warrior_pose(rng):
    top = [(-3.0, 1.0), (-0.6, 1.05), (-0.25, 1.15), (0.25, 1.15), (0.6, 1.05), (3.0, 1.0), (3.05, 0.85), (0.6, 0.78), (0.42, 0.3), (0.35, -0.3),
           (0.45, -0.7), (1.0, -0.75), (1.65, -0.85), (1.75, -1.2), (1.7, -2.4), (2.1, -2.5), (2.1, -2.7), (1.4, -2.7), (1.35, -2.3),
           (1.35, -1.25), (0.55, -1.2), (0.05, -1.1), (-0.6, -1.7), (-1.6, -2.55), (-1.4, -2.75), (-2.3, -2.75), (-2.05, -2.45),
           (-0.95, -1.5), (-0.45, -0.75), (-0.4, -0.3), (-0.42, 0.3), (-0.6, 0.78), (-3.05, 0.85)]
    sil = smooth(top, 4, closed=True)
    head = ellipse(0.0, 1.62, 0.3, 0.36, 30)
    neck = [[(-0.12, 1.15), (-0.12, 1.28)], [(0.12, 1.15), (0.12, 1.28)]]
    mat = rrect(-3.0, -3.1, 3.0, -2.85, 0.1)
    return make("Yoga Warrior Pose", [sil, head, mat] + neck)


@design("zen_water_ripples", T)
def water_ripples(rng):
    drop = chain(quad((0, 2.9), (0.05, 2.4), (0.4, 1.85), 10), arc(0, 1.7, 0.42, R(20), R(-200), 20),
                 quad((-0.4, 1.85), (-0.05, 2.4), (0, 2.9), 10))
    rip = [ellipse(0, -1.4, 0.45 * k, 0.15 * k, 60 + 10 * k) for k in range(1, 7)]
    splash = [lens((0, -1.3), (0, -0.7), 0.25), lens((-0.25, -1.3), (-0.6, -0.85), 0.25), lens((0.25, -1.3), (0.6, -0.85), 0.25)]
    return make("Water Drop Ripples", [drop] + rip + hide(splash, ellipse(0, -1.4, 0.45, 0.15, 30)))


@design("zen_stone_lantern", T)
def stone_lantern(rng):
    out = [poly((-1.4, -2.9), (1.4, -2.9), (1.2, -2.5), (-1.2, -2.5)),
           rect(-0.35, -2.5, 0.35, -0.9),
           poly((-1.1, -0.9), (1.1, -0.9), (0.8, -0.55), (-0.8, -0.55)),
           rect(-0.75, -0.55, 0.75, 0.75),
           rect(-0.35, -0.3, 0.35, 0.45),
           poly((-1.9, 0.75), (1.9, 0.75), (0.6, 1.5), (-0.6, 1.5)),
           chain([(-1.9, 0.75)], quad((-1.9, 0.75), (-2.1, 0.8), (-2.15, 1.05), 6)),
           chain([(1.9, 0.75)], quad((1.9, 0.75), (2.1, 0.8), (2.15, 1.05), 6)),
           circle(0, 1.75, 0.3, 20), lens((0, 2.0), (0, 2.6), 0.3)]
    out += [[(-0.8, -0.55 + 0.0), (-0.8, -0.55)][0:0]]
    moss = [wave(-3.0, 3.0, -2.9, 0.0, 1, 2)]
    stones = [ellipse(-2.3, -2.75, 0.45, 0.22, 20), ellipse(2.3, -2.75, 0.55, 0.25, 20)]
    glow = [arc(0, 0.1, 1.2, R(-30), R(30), 8)[0:0]]
    return make("Stone Garden Lantern", out + moss + stones, [eye(0, 0.08, 0.12)])


@design("zen_koru_fern", T)
def koru(rng):
    def fiddle(ox, oy, s, flip=1):
        C = (1.0, 1.3)
        sp = []
        for i in range(81):
            u = i / 80
            th = math.pi - u * 3.3 * math.pi
            r = 1.2 * math.exp(-2.0 * u)
            sp.append((C[0] + r * math.cos(th), C[1] + r * math.sin(th)))
        stem = cubic((-0.6, -3.0), (-0.5, -1.5), (-0.2, 0.3), (-0.2, 1.3), 30)
        line = chain(stem, sp)
        n = len(line)
        shape = tube(line, lambda t: 0.34 * (1 - 0.75 * t))
        leaves = []
        for k, u in enumerate((0.05, 0.11, 0.17, 0.23)):
            i = int(u * (n - 1))
            (x, y), (x2, y2) = line[i], line[i + 1]
            a = math.atan2(y2 - y, x2 - x)
            L = 0.9 - 0.12 * k
            for sgn in (1, -1):
                base = (x + sgn * 0.17 * math.cos(a + sgn * math.pi / 2) * 1, y + 0.17 * math.sin(a + sgn * math.pi / 2))
                base = (x + 0.15 * math.cos(a + sgn * math.pi / 2), y + 0.15 * math.sin(a + sgn * math.pi / 2))
                tip = (base[0] + L * math.cos(a + sgn * 1.0), base[1] + L * math.sin(a + sgn * 1.0))
                leaves.append(lens(base, tip, 0.25))
        parts = [shape] + hide(leaves, shape)
        return [transform([(flip * x, y) for x, y in p], dx=ox, dy=oy, s=s) for p in parts]
    out = fiddle(0.4, 0.0, 1.0) + fiddle(-1.7, -1.2, 0.6, flip=-1)
    out.append(wave(-3.2, 3.2, -3.0, 0.05, 4))
    return make("Unfurling Fern Fiddlehead", out)


def boteh(s=1.0):
    """Paisley (boteh) teardrop with curled tip, round end at the origin."""
    pts = [(0.0, -0.55), (0.5, -0.3), (0.55, 0.25), (0.3, 0.8), (0.35, 1.2), (0.6, 1.35), (0.55, 1.6), (0.15, 1.5), (-0.25, 1.05),
           (-0.5, 0.4), (-0.45, -0.25)]
    return transform(smooth(pts, 8, closed=True), s=s)


@design("zen_shippo_circles", T)
def shippo(rng):
    s = 2.0
    r = s / math.sqrt(2)
    W = 3.0
    circles = []
    for i in range(-3, 4):
        for j in range(-3, 4):
            circles.append(circle(i * s, j * s, r, 60))
            circles.append(circle((i + 0.5) * s, (j + 0.5) * s, r, 60))
    out = []
    for c in circles:
        out += keep_runs(c, lambda p: abs(p[0]) < W - 0.02 and abs(p[1]) < W - 0.02)
    out += [circle(i * s, j * s, 0.22, 14) for i in (-1, 0, 1) for j in (-1, 0, 1)]
    out.append(rect(-W, -W, W, W))
    return make("Shippo Interlocking Circles", out)


@design("zen_bamboo_fountain", T)
def bamboo_fountain(rng):
    basin = smooth([(-1.9, -0.6), (-1.6, -2.4), (0.0, -2.75), (1.7, -2.4), (2.0, -0.6)], 10)
    top = ellipse(0.05, -0.6, 1.95, 0.45, 70)
    water = ellipse(0.05, -0.62, 1.5, 0.28, 60)
    ripple = ellipse(0.05, -0.62, 0.7, 0.13, 30)
    post = tube([(-2.6, -2.9), (-2.6, 1.6)], 0.45, cap=True)
    pipe = tube([(-2.6, 1.3), (-0.8, 1.0)], 0.32, cap=True)
    nodes = [[(-2.83, -1.4), (-2.37, -1.4)], [(-2.83, 0.3), (-2.37, 0.3)], [(-1.6, 1.29), (-1.65, 0.97)]]
    stream = [cubic((-0.75, 1.0), (-0.4, 0.95), (-0.3, 0.4), (-0.3, -0.45), 14), cubic((-0.75, 0.85), (-0.55, 0.8), (-0.5, 0.4), (-0.5, -0.5), 14)]
    ladle = []
    pebbles = [ellipse(x, -2.95, rx, 0.18, 16) for x, rx in [(2.2, 0.35), (2.85, 0.25), (-1.6, 0.25)]]
    out = [basin, top, water, ripple, pipe] + hide([post], pipe) + nodes + hide(stream, ripple) + ladle + pebbles
    return make("Bamboo Water Fountain", out)
