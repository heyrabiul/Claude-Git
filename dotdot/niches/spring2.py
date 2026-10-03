"""Spring niche, part 2 (pictures 9-55)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
from .autumn2 import bumpy, clip, hide, leaf, smooth, tree, yat
import math

T = "spring"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ------------------------------------------------------------ helpers

def petal(p0, p1, w=0.45, n=14):
    """Broad petal with a rounded tip from p0 (base) to p1 (tip)."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    a = (p0[0] + 0.25 * dx + nx * w * L, p0[1] + 0.25 * dy + ny * w * L)
    b = (p1[0] + nx * 0.75 * w * L - 0.05 * dx, p1[1] + ny * 0.75 * w * L - 0.05 * dy)
    c = (p1[0] - nx * 0.75 * w * L - 0.05 * dx, p1[1] - ny * 0.75 * w * L - 0.05 * dy)
    d = (p0[0] + 0.25 * dx - nx * w * L, p0[1] + 0.25 * dy - ny * w * L)
    return chain(cubic(p0, a, b, p1, n), cubic(p1, c, d, p0, n))


def daisy(cx, cy, r, n=12, rot=0.0, centre=0.28):
    out = [circle(cx, cy, centre * r, 24)]
    for k in range(n):
        a = rot + TAU * k / n
        out.append(lens((cx + centre * r * math.cos(a), cy + centre * r * math.sin(a)), (cx + r * math.cos(a), cy + r * math.sin(a)), 0.22, 10))
    return out


def blossom(cx, cy, r, rot=0.0, n=5):
    """Five rounded petals around a small centre."""
    out = [circle(cx, cy, 0.22 * r, 12)]
    for k in range(n):
        a = rot + math.pi / 2 + TAU * k / n
        out.append(petal((cx + 0.22 * r * math.cos(a), cy + 0.22 * r * math.sin(a)), (cx + r * math.cos(a), cy + r * math.sin(a)), 0.42, 10))
    return out


def blossom_outline(cx, cy, r):
    return circle(cx, cy, r * 0.98, 30)


def tulip(cx, cy, s, rot=0.0):
    L = chain(cubic((0, 0), (-0.6, 0), (-0.68, 0.6), (-0.58, 1.18), 14), quad((-0.58, 1.18), (-0.38, 0.95), (-0.2, 0.92), 8),
              quad((-0.2, 0.92), (-0.06, 1.08), (0, 1.32), 8))
    head = chain(L, mirror_x(L)[::-1])
    inner = [quad((-0.2, 0.92), (-0.12, 0.45), (0.0, 0.2), 8), quad((0.2, 0.92), (0.12, 0.45), (0.0, 0.2), 8)]
    return [transform(p, dx=cx, dy=cy, s=s, rot=rot) for p in [head] + inner]


def cloud(cx, cy, rx, ry, k=7):
    pts = bumpy(cx, cy, rx, ry, k, 0.22)
    return [(x, max(y, cy - 0.45 * ry)) for x, y in pts]


def songbird(x, y, s, flip=False, legs=True, rot=0.0):
    body = smooth([(1.0, 0.62), (0.75, 0.85), (0.4, 0.82), (0.05, 0.55), (-0.5, 0.3), (-1.0, 0.15), (-1.55, 0.18), (-1.5, -0.05),
                   (-0.95, -0.05), (-0.5, -0.3), (0.1, -0.42), (0.65, -0.2), (0.95, 0.2), (1.02, 0.45), (1.0, 0.62)], 5, closed=True)
    beak = poly((1.0, 0.62), (1.38, 0.52), (1.02, 0.45), closed=False)
    wing = smooth([(0.4, 0.42), (0.0, 0.1), (-0.7, -0.05), (-1.15, 0.02), (-0.6, 0.28), (0.0, 0.47), (0.4, 0.42)], 5, closed=True)
    parts = [body, beak, wing]
    if legs:
        parts += [[(0.05, -0.41), (0.0, -0.75)], [(0.35, -0.35), (0.35, -0.75)], [(-0.15, -0.75), (0.15, -0.75)], [(0.2, -0.75), (0.5, -0.75)]]
    sx = -s if flip else s
    out = [transform(p, dx=x, dy=y, sx=sx, sy=s, rot=rot) for p in parts]
    e = transform([(0.72, 0.6)], dx=x, dy=y, sx=sx, sy=s, rot=rot)[0]
    return out, eye(e[0], e[1], 0.07 * s / 0.8 if s < 0.8 else 0.08)


def duck(x, y, s, flip=False):
    body = smooth([(-2.25, 1.15), (-2.3, 1.25), (-1.95, 1.42), (-1.75, 1.75), (-1.4, 1.92), (-1.05, 1.68), (-1.05, 1.1), (-0.4, 0.75), (0.8, 0.75),
                   (1.5, 1.1), (1.75, 1.15), (1.6, 0.6), (1.3, 0.05), (0.0, -0.25), (-1.1, -0.1), (-1.6, 0.4), (-1.55, 0.95),
                   (-1.8, 1.12), (-2.25, 1.15)], 4, closed=True)
    bill = [[(-1.9, 1.45), (-1.82, 1.15)]]
    wing = smooth([(-0.6, 0.6), (0.4, 0.75), (1.2, 0.62), (0.6, 0.18), (-0.4, 0.25), (-0.6, 0.6)], 5, closed=True)
    sx = -s if flip else s
    parts = [transform(p, dx=x, dy=y, sx=sx, sy=s) for p in [body, wing] + bill]
    e = transform([(-1.45, 1.55)], dx=x, dy=y, sx=sx, sy=s)[0]
    return parts, eye(e[0], e[1], max(0.05, 0.08 * s))


def grass(x0, x1, y, h=0.35, n=12):
    pts = []
    for i in range(2 * n + 1):
        x = x0 + (x1 - x0) * i / (2 * n)
        pts.append((x + (0.06 if i % 2 else 0), y + (h * (0.7 + 0.3 * math.sin(i * 1.7)) if i % 2 else 0)))
    return pts


def heart_leaf(x, y, L, ang):
    pts = heart(0, 0, 1.0, 60)
    pts = [(px, -py) for px, py in pts]
    return transform(pts, dx=x + 0.55 * L * math.cos(ang), dy=y + 0.55 * L * math.sin(ang), s=0.6 * L, rot=ang - math.pi / 2)


def boot(x, y, s, flip=False):
    pts = smooth([(-0.55, 2.2), (-0.6, 0.0), (-0.65, -1.2), (-0.6, -1.7), (0.2, -1.7), (1.1, -1.65), (1.35, -1.4), (1.2, -1.1),
                  (0.6, -0.9), (0.45, -0.5), (0.5, 1.0), (0.55, 2.2)], 4)
    pts = [pts[0]] + pts[1:] + [(-0.55, 2.2)]
    sole = [(-0.62, -1.45), (1.32, -1.45)]
    top = [(-0.55, 1.85), (0.55, 1.85)]
    sx = -s if flip else s
    return [transform(p, dx=x, dy=y, sx=sx, sy=s) for p in [pts, sole, top]]


# ------------------------------------------------------------ flowers

@design("spring_tulip_trio", T)
def tulip_trio(rng):
    heads = tulip(-1.5, 0.7, 1.25, 0.25) + tulip(0.2, 1.4, 1.35, -0.05) + tulip(1.8, 0.2, 1.2, -0.3)
    stems = [quad((-1.5, 0.7), (-1.0, -1.2), (-0.6, -2.8), 16), quad((0.2, 1.4), (0.0, -0.8), (-0.1, -2.8), 16), quad((1.8, 0.2), (1.2, -1.4), (0.5, -2.8), 16)]
    leaves = [lens((-0.65, -2.8), (-2.6, -0.6), 0.16, 24), lens((-0.1, -2.8), (1.1, -0.4), 0.14, 24), lens((0.5, -2.8), (2.8, -1.6), 0.16, 24),
              lens((-0.3, -2.8), (-1.4, -0.9), 0.14, 20)]
    leaves = hide(leaves, *[heads[0], heads[3], heads[6]])
    ground = [wave(-3.0, 3.0, -2.85, 0.06, 5, 80)]
    return make("Tulip Trio", heads + stems + leaves + ground)


@design("spring_magnolia", T)
def magnolia(rng):
    branch = [quad((-3.2, -2.6), (-0.6, -1.2), (2.8, -0.2), 30), quad((-3.2, -2.25), (-0.6, -0.9), (2.7, 0.05), 30), [(0.3, -0.6), (0.2, 0.2)], [(0.55, -0.55), (0.5, 0.2)]]
    def flower(cx, cy, s, rot):
        back = [petal((0, 0), (-0.7, 1.7), 0.3), petal((0, 0), (0.7, 1.7), 0.3)]
        front = [petal((0, 0), (-0.45, 1.9), 0.28), petal((0, 0), (0.45, 1.9), 0.28), petal((0, 0), (0, 2.1), 0.27)]
        cup = hide(back, *front[:2]) + hide(front[:2], front[2]) + [front[2]]
        sep = [lens((0, -0.25), (-0.3, 0.35), 0.4), lens((0, -0.25), (0.3, 0.35), 0.4)]
        sep = hide(sep, *front)
        return [transform(p, dx=cx, dy=cy, s=s, rot=rot) for p in cup + sep]
    f = flower(0.35, 0.1, 1.2, 0.0) + flower(-1.8, -1.6, 0.9, 0.5) + flower(2.3, 0.1, 0.8, -0.4)
    buds = [lens((-0.9, -1.0), (-0.7, 0.0), 0.28), lens((1.6, -0.45), (2.0, 0.5), 0.28)]
    petals_ = [lens((x, y), (x + 0.4, y - 0.25), 0.35) for x, y in [(-2.6, 1.4), (2.4, 2.6), (-0.8, 2.8)]]
    branch = hide(branch, *[s for s in f if len(s) > 20])
    return make("Magnolia Blossoms on a Branch", f + branch + buds + petals_)


@design("spring_lilac", T)
def lilac(rng):
    cents = []
    for row in range(7):
        y = 2.8 - 0.62 * row
        half = 1.55 * (1 - row / 7.2) + 0.05
        n = max(1, int(round(2 * half / 0.66)) + 1)
        for k in range(n):
            x = (-half + 2 * half * k / (n - 1)) if n > 1 else 0.0
            x += 0.12 * math.sin(3.1 * row + 1.7 * k)
            cents.append((x, y + 0.08 * math.cos(2.3 * k + row)))
    out = []
    discs = []
    for i, (x, y) in enumerate(cents):
        rot = 0.4 * math.sin(i * 2.1)
        fl = [circle(x, y, 0.07, 8)] + [petal((x + 0.07 * math.cos(a), y + 0.07 * math.sin(a)), (x + 0.4 * math.cos(a), y + 0.4 * math.sin(a)), 0.45, 6)
                                         for a in [rot + math.pi / 4 + k2 * math.pi / 2 for k2 in range(4)]]
        out += hide(fl, *discs)
        discs.append(circle(x, y, 0.4, 16))
    stem = [quad((0.0, -1.0), (0.15, -2.0), (0.0, -3.0), 10)]
    leaves = [heart_leaf(0.05, -2.2, 1.6, math.radians(200)), heart_leaf(0.05, -2.45, 1.5, math.radians(-20))]
    veins = [[(0.05, -2.2), (-1.3, -2.68)], [(0.05, -2.45), (1.33, -2.92)]]
    return make("Lilac Blossom", out + stem + leaves + veins)


@design("spring_iris", T)
def iris(rng):
    std_c = petal((0, 0.6), (0, 2.6), 0.28)
    std_l = petal((-0.1, 0.6), (-1.0, 2.2), 0.28)
    std_r = petal((0.1, 0.6), (1.0, 2.2), 0.28)
    fall_l = petal((-0.1, 0.5), (-1.9, -0.6), 0.32)
    fall_r = petal((0.1, 0.5), (1.9, -0.6), 0.32)
    fall_c = petal((0, 0.5), (0, -1.3), 0.32)
    beards = [quad((0, 0.3), (0.05, -0.2), (0, -0.7), 8), quad((-0.35, 0.35), (-0.8, 0.1), (-1.2, -0.25), 8), quad((0.35, 0.35), (0.8, 0.1), (1.2, -0.25), 8)]
    flower = hide([std_l, std_r], std_c) + [std_c]
    flower = hide(flower + [fall_l, fall_r], fall_c) + [fall_c]
    stem = [[(-0.08, -1.3), (-0.1, -3.0)], [(0.08, -1.3), (0.1, -3.0)]]
    swords = [lens((-0.3, -3.0), (-2.2, 1.2), 0.08, 30), lens((0.3, -3.0), (2.4, 0.6), 0.08, 30), lens((-0.2, -3.0), (-1.2, -0.4), 0.1, 20)]
    swords = hide(swords, fall_l, fall_r, fall_c)
    bud = [lens((-1.9, -1.9), (-2.5, -0.6), 0.25), [(-1.92, -1.85), (-0.7, -3.0)]]
    return make("Bearded Iris", flower + beards + stem + swords + bud)


@design("spring_hyacinth_pot", T)
def hyacinth_pot(rng):
    pot = poly((-1.4, -1.0), (1.4, -1.0), (1.1, -3.0), (-1.1, -3.0))
    rim = rect(-1.6, -1.0, 1.6, -0.5)
    bulb = chain(quad((-0.9, -0.5), (-0.9, 0.2), (-0.15, 0.6), 10), quad((0.15, 0.6), (0.9, 0.2), (0.9, -0.5), 10))
    stalk = [[(-0.12, 0.6), (-0.12, 1.0)], [(0.12, 0.6), (0.12, 1.0)]]
    florets = []
    for row in range(6):
        y = 1.2 + 0.5 * row
        xs = (-0.55, 0.0, 0.55) if row % 2 == 0 else (-0.28, 0.28)
        if row == 5:
            xs = (0.0,)
        for x in xs:
            florets.append(star(x, y, 0.3, 6, 0.55, rot=0.3 * row))
            florets.append(circle(x, y, 0.06, 6))
    leaves = [lens((-0.3, 0.4), (-1.9, 2.4), 0.12, 24), lens((0.3, 0.4), (2.0, 2.2), 0.12, 24), lens((-0.4, 0.3), (-2.3, 0.6), 0.12, 20), lens((0.4, 0.3), (2.3, 0.4), 0.12, 20)]
    leaves = hide(leaves, *florets[::2])
    return make("Hyacinth in a Pot", [pot, rim, bulb] + stalk + florets + leaves)


@design("spring_peony", T)
def peony(rng):
    def ruffle(p0, p1, w):
        pts = petal(p0, p1, w, 24)
        cx, cy = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        out = []
        for i, (x, y) in enumerate(pts):
            d = math.hypot(x - p0[0], y - p0[1]) / math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            k = 0.07 * max(0.0, d - 0.6) * math.sin(i * 1.3) * 3
            out.append((x + k * (x - cx), y + k * (y - cy)))
        out[-1] = out[0]
        return out
    cy = 0.9
    outer = [ruffle((0.5 * math.cos(a), cy + 0.5 * math.sin(a)), (2.5 * math.cos(a), cy + 2.1 * math.sin(a)), 0.42) for a in [math.pi / 2 + TAU * k / 7 for k in range(7)]]
    mid = [ruffle((0.3 * math.cos(a), cy + 0.3 * math.sin(a)), (1.6 * math.cos(a), cy + 1.4 * math.sin(a)), 0.4) for a in [math.pi / 2 + TAU * (k + 0.5) / 6 for k in range(6)]]
    inner = [petal((0, cy - 0.1), (0.6 * math.cos(a), cy + 0.55 * math.sin(a)), 0.5, 10) for a in [math.pi / 2 + TAU * k / 5 for k in range(5)]]
    core = circle(0, cy, 0.22, 16)
    flower = hide(outer, *mid) + hide(mid, *inner) + hide(inner, core) + [core]
    stem = hide([quad((0.0, -1.0), (0.2, -2.0), (0.1, -3.0), 10)], *outer)
    leaves = hide([lens((0.1, -2.2), (-2.6, -1.9), 0.22), lens((0.15, -2.5), (2.6, -2.7), 0.22), [(0.1, -2.2), (-2.2, -1.95)], [(0.15, -2.5), (2.2, -2.68)]], *outer)
    return make("Blooming Peony", flower + stem + leaves)


@design("spring_lily_of_the_valley", T)
def lily_of_the_valley(rng):
    leaves = [lens((-0.6, -3.0), (-2.0, 1.0), 0.26, 40), lens((0.5, -3.0), (2.6, 0.2), 0.24, 40)]
    veins = [quad((-0.6, -3.0), (-1.4, -1.0), (-1.9, 0.7), 12), quad((0.5, -3.0), (1.6, -1.4), (2.45, 0.05), 12)]
    stem = cubic((0.0, -3.0), (-0.4, 1.4), (1.0, 3.0), (3.0, 2.0), 60)
    bells = []
    outl = []
    for idx, s in [(24, 0.9), (31, 0.85), (37, 0.78), (43, 0.7), (49, 0.6), (55, 0.5)]:
        x, y = stem[idx]
        hang = quad((x, y), (x + 0.12, y - 0.15), (x + 0.1, y - 0.4), 6)
        bx, by = x + 0.1, y - 0.4 - 0.45 * s
        top = arc(bx, by, 0.45 * s, 0, math.pi, 14)
        rim = chain([(bx - 0.45 * s, by)], [(bx - 0.55 * s, by - 0.35 * s)], wave(bx - 0.55 * s, bx + 0.55 * s, by - 0.4 * s, 0.07 * s, 3, 18), [(bx + 0.45 * s, by)])
        bells += [hang, chain(top, rim)]
        outl.append(chain(top, rim))
    stem = hide([stem], *leaves)
    return make("Lily of the Valley Bells", leaves + veins + stem + bells)


@design("spring_daisy_jar", T)
def daisy_jar(rng):
    jar = chain([(-0.9, 0.2), (-0.9, -0.1)], quad((-0.9, -0.1), (-1.5, -0.4), (-1.5, -1.0), 8), [(-1.5, -2.6)], quad((-1.5, -2.6), (-1.5, -3.0), (-1.1, -3.0), 6),
                [(1.1, -3.0)], quad((1.1, -3.0), (1.5, -3.0), (1.5, -2.6), 6), [(1.5, -1.0)], quad((1.5, -1.0), (1.5, -0.4), (0.9, -0.1), 8), [(0.9, 0.2)])
    threads = [[(-0.9, 0.0), (0.9, 0.12)], [(-0.9, 0.2), (0.9, 0.2)]]
    water = [wave(-1.5, 1.5, -1.3, 0.05, 3, 40)]
    heads = [(-1.6, 1.8, 0.75), (0.2, 2.4, 0.85), (1.9, 1.5, 0.7), (-0.5, 0.9, 0.55), (1.0, 0.75, 0.5)]
    flowers, stems = [], []
    for k, (x, y, r) in enumerate(heads):
        flowers += daisy(x, y, r, 12, 0.2 * k)
        stems.append(quad((x, y - 0.3 * r), (x * 0.5, -0.5), (x * 0.25, -2.8), 14))
    stems = hide(stems, *[circle(x, y, r * 1.02, 30) for x, y, r in heads])
    lv = leaf(0.4, -0.2, 1.1, 0.3) + leaf(-0.3, -0.1, 1.0, 2.7)
    lv = hide(lv, *[circle(x, y, r * 1.02, 30) for x, y, r in heads])
    return make("Daisies in a Mason Jar", [jar] + threads + water + flowers + stems + lv)


@design("spring_crocuses_snow", T)
def crocuses_snow(rng):
    def crocus(cx, base, h, s, rot):
        cup = chain(cubic((0, 0), (-0.45, 0.05), (-0.5, 0.7), (-0.3, 1.2), 12), quad((-0.3, 1.2), (-0.15, 0.95), (0, 1.3), 8))
        cup = chain(cup, mirror_x(cup)[::-1])
        mid = [quad((-0.15, 0.95), (-0.05, 0.5), (0, 0.15), 8), quad((0.15, 0.95), (0.05, 0.5), (0, 0.15), 8)]
        head = [transform(p, dx=cx, dy=base + h, s=s, rot=rot) for p in [cup] + mid]
        stem = [[(cx - 0.06, base), (cx - 0.06, base + h)], [(cx + 0.06, base), (cx + 0.06, base + h)]]
        blades = [lens((cx, base), (cx - 0.5, base + 0.75 * h), 0.08, 14), lens((cx, base), (cx + 0.55, base + 0.7 * h), 0.08, 14)]
        return head + stem + blades
    out = crocus(-1.9, -1.4, 1.5, 0.9, 0.15) + crocus(-0.4, -1.6, 2.2, 1.0, -0.05) + crocus(1.0, -1.5, 1.4, 0.85, -0.2) + crocus(2.3, -1.7, 0.9, 0.7, -0.3)
    snow = [chain(quad((-3.2, -1.7), (-2.6, -1.1), (-2.0, -1.45), 10), quad((-2.0, -1.45), (-1.1, -1.0), (0.2, -1.6), 12),
                  quad((0.2, -1.6), (1.2, -1.2), (1.9, -1.6), 10), quad((1.9, -1.6), (2.6, -1.3), (3.2, -1.8), 8))]
    out = hide(out, poly((-3.2, -1.7), *snow[0], (3.2, -3.0), (-3.2, -3.0)))
    lumps = [quad((-2.6, -2.4), (-1.8, -2.1), (-1.0, -2.4), 8), quad((0.6, -2.6), (1.4, -2.3), (2.2, -2.6), 8)]
    sun = [circle(2.4, 2.4, 0.5, 30)] + [[(2.4 + 0.7 * math.cos(a), 2.4 + 0.7 * math.sin(a)), (2.4 + 0.95 * math.cos(a), 2.4 + 0.95 * math.sin(a))] for a in [k * math.pi / 4 for k in range(8)]]
    return make("Crocuses in Melting Snow", out + snow + lumps + sun)


@design("spring_pansy_pot", T)
def pansy_pot(rng):
    pot = chain(quad((-1.6, -0.6), (-1.6, -2.4), (-0.9, -3.0), 16), [(0.9, -3.0)], quad((0.9, -3.0), (1.6, -2.4), (1.6, -0.6), 16))
    rim = rrect(-1.9, -0.6, 1.9, -0.1, 0.12)
    def pansy(cx, cy, s, rot):
        back = [petal((0, 0.1), (-0.5, 1.0), 0.45), petal((0, 0.1), (0.5, 1.0), 0.45)]
        side = [petal((0, 0), (-0.95, 0.15), 0.42), petal((0, 0), (0.95, 0.15), 0.42)]
        low = petal((0, 0), (0, -1.0), 0.6)
        parts = hide(back, *side, low) + hide(side, low) + [low]
        face = [[(0, -0.15), (-0.2, -0.5)], [(0, -0.15), (0, -0.55)], [(0, -0.15), (0.2, -0.5)], [(-0.15, 0.0), (-0.5, 0.05)], [(0.15, 0.0), (0.5, 0.05)], circle(0, 0, 0.1, 10)]
        return [transform(p, dx=cx, dy=cy, s=s, rot=rot) for p in parts + face]
    f = pansy(-1.0, 1.0, 1.1, 0.25) + pansy(1.1, 0.8, 1.0, -0.25) + pansy(0.05, 2.2, 0.95, 0.0)
    outlines = [s for s in f if len(s) > 20]
    lv = leaf(-1.2, -0.1, 1.3, 2.75) + leaf(1.2, -0.1, 1.3, 0.4) + leaf(0.1, 0.0, 1.0, 1.35)
    lv = hide(lv, *outlines, rim)
    return make("Pot of Pansies", [pot, rim] + f + lv)


@design("spring_flower_wreath", T)
def flower_wreath(rng):
    R = 2.0
    ring = [circle(0, 0, R, 120)]
    lv = []
    for k in range(18):
        a = TAU * k / 18
        p = (R * math.cos(a), R * math.sin(a))
        for dr in (0.55, -0.45):
            q = ((R + dr) * math.cos(a + 0.28), (R + dr) * math.sin(a + 0.28))
            lv.append(lens(p, q, 0.3, 12))
    flowers = []
    centres = [(R * math.cos(a), R * math.sin(a)) for a in [math.pi / 2 + TAU * k / 6 for k in range(6)]]
    for k, (x, y) in enumerate(centres[1:]):
        flowers += daisy(x, y, 0.6, 10, k) if k % 2 == 0 else blossom(x, y, 0.6, k)
    discs = [circle(x, y, 0.62, 30) for x, y in centres[1:]]
    bow = [petal((0, R + 0.1), (-1.0, R + 0.6), 0.4), petal((0, R + 0.1), (1.0, R + 0.6), 0.4), rrect(-0.2, R - 0.1, 0.2, R + 0.3, 0.08),
           [(-0.15, R - 0.1), (-0.6, R - 1.0)], [(0.15, R - 0.1), (0.6, R - 1.0)]]
    base = hide(ring + lv, *discs, bow[0], bow[1], bow[2])
    return make("Spring Flower Wreath", base + flowers + bow)


# ------------------------------------------------------------ garden & weather

@design("spring_rainbow_clouds", T)
def rainbow_clouds(rng):
    arcs_ = [arc(0, -1.2, r, 0, math.pi, 80) for r in (1.3, 1.65, 2.0, 2.35, 2.7)]
    cl = [cloud(-2.1, -1.0, 1.25, 0.8), cloud(2.1, -1.0, 1.25, 0.8)]
    arcs_ = hide(arcs_, *cl)
    drops = [lens((x, y), (x, y - 0.4), 0.4) for x, y in [(-2.6, -1.6), (-1.9, -2.2), (-1.3, -1.7), (1.4, -1.7), (2.0, -2.3), (2.6, -1.6)]]
    sun = [circle(2.5, 2.3, 0.5, 30)] + [[(2.5 + 0.65 * math.cos(a), 2.3 + 0.65 * math.sin(a)), (2.5 + 0.9 * math.cos(a), 2.3 + 0.9 * math.sin(a))] for a in [k * math.pi / 4 for k in range(8)]]
    birds = [chain(quad((x - 0.3, y + 0.1), (x - 0.15, y + 0.15), (x, y), 6), quad((x, y), (x + 0.15, y + 0.15), (x + 0.3, y + 0.1), 6)) for x, y in [(-2.3, 2.3), (-1.6, 2.7)]]
    return make("Rainbow After the Rain", arcs_ + cl + drops + sun + birds)


@design("spring_umbrella_shower", T)
def umbrella_shower(rng):
    canopy = smooth([(-2.6, 0.2), (-2.3, 1.4), (-1.2, 2.3), (0, 2.55), (1.2, 2.3), (2.3, 1.4), (2.6, 0.2)], 8)
    ribs_x = [-2.6, -1.3, 0.0, 1.3, 2.6]
    scallops = [quad((ribs_x[k], 0.2), ((ribs_x[k] + ribs_x[k + 1]) / 2, 0.6), (ribs_x[k + 1], 0.2), 12) for k in range(4)]
    ribs = [quad((0, 2.55), (x * 0.65, 1.7), (x, 0.2), 12) for x in (-1.3, 1.3)]
    dots = [circle(x, y, 0.22, 16) for x, y in [(-1.6, 1.2), (-0.6, 1.7), (0.6, 1.0), (1.7, 1.4), (-0.7, 0.75)]]
    knob = [circle(0, 2.75, 0.18, 12)]
    shaft = chain([(0, 0.4), (0, -1.6)], arc(0.35, -1.6, 0.35, math.pi, 2 * math.pi, 12))
    parts = [transform(p, rot=0.2, dy=0.3) for p in [canopy] + scallops + ribs + dots + knob + [shaft]]
    drops = [lens((x, y), (x, y - 0.45), 0.4) for x, y in [(-2.9, 2.4), (-2.6, 0.3), (2.8, -0.5), (-2.0, -1.0), (2.4, 0.9), (1.4, -1.6), (-2.9, -2.0)]]
    tulips_ = tulip(-1.2, -2.2, 0.6, 0.1) + tulip(1.5, -2.4, 0.55, -0.15) + [[(-1.2, -2.2), (-1.2, -2.9)], [(1.5, -2.4), (1.5, -2.9)]]
    puddle = [ellipse(0.0, -2.95, 2.2, 0.22, 60)]
    return make("Polka-Dot Umbrella in the Rain", parts + drops + tulips_ + puddle)


@design("spring_watering_can", T)
def watering_can(rng):
    body = rrect(-1.9, -2.3, 0.9, 0.6, 0.2)
    top = ellipse(-0.5, 0.6, 1.4, 0.25, 50)
    handle = tube(arc(-0.5, 0.65, 1.0, 0.25, math.pi - 0.25, 30), 0.22)
    back = arc(-1.9, -0.7, 0.75, math.pi / 2, 1.5 * math.pi, 16)
    spout = tube([(0.85, -1.6), (2.0, -0.2), (2.4, 0.4)], 0.3)
    rose = [ellipse(2.55, 0.62, 0.25, 0.42, 24, rot=-0.6)]
    holes = [circle(2.55 + dx, 0.62 + dy, 0.05, 6) for dx, dy in [(0, 0), (0.1, 0.18), (-0.1, -0.18)]]
    flow = [[(2.7 + 0.25 * k, 0.4 - 0.2 * k), (2.9 + 0.3 * k, -0.8 - 0.25 * k)] for k in range(3)]
    flowers = daisy(2.9, -2.0, 0.45, 9) + [[(2.9, -2.45), (2.9, -2.9)]]
    decor = blossom(-0.5, -0.9, 0.6, 0.0)
    ground = [[(-3.2, -2.9), (3.4, -2.9)]]
    return make("Watering the Spring Flowers", [body, top, handle, back, spout] + rose + holes + flow + flowers + decor + ground)


@design("spring_seed_packets", T)
def seed_packets(rng):
    def packet(cx, cy, rot, kind):
        p = [rect(-1.1, -1.7, 1.1, 1.5), zigzag(-1.1, 1.1, 1.5, 0.08, 8), [(-1.1, 1.15), (1.1, 1.15)], rect(-0.9, -1.0, 0.9, 0.95),
             [(-0.8, -1.3), (0.8, -1.3)]]
        if kind == 0:
            p += tulip(0, -0.3, 0.6) + [[(0, -0.3), (0, -0.95)], lens((0, -0.95), (-0.55, -0.3), 0.2)]
        else:
            p += daisy(0, 0.05, 0.6, 10) + [[(0, -0.12), (0, -0.95)], lens((0, -0.85), (0.5, -0.4), 0.25)]
        return [transform(s, dx=cx, dy=cy, rot=rot) for s in p]
    out = packet(-1.4, 0.6, 0.15, 0) + packet(1.3, 0.3, -0.12, 1)
    seeds = [ellipse(x, y, 0.15, 0.09, 10, rot=r) for x, y in [(-0.4, -2.0), (0.0, -2.3), (0.5, -2.0), (-0.9, -2.5), (0.9, -2.6), (0.3, -2.75)] for r in [x]]
    trowel = [transform(s, dx=-2.2, dy=-2.4, rot=0.25) for s in [chain([(0, 0.2)], quad((0.8, 0.5), (1.6, 0.3), (2.0, 0.0), 10), quad((2.0, 0.0), (1.6, -0.3), (0.8, -0.5), 10), [(0, -0.2), (0, 0.2)]),
                                                                  rrect(-1.2, -0.12, -0.15, 0.12, 0.1), [(-0.15, 0.0), (0.0, 0.0)]]]
    return make("Spring Seed Packets and Trowel", out + seeds + trowel)


@design("spring_garden_gloves", T)
def garden_gloves(rng):
    def glove():
        pts = [(-0.85, -0.3), (-0.85, 0.35)]
        pts += [(-1.35, 0.75)] + arc(-1.42, 0.92, 0.18, math.radians(-60), math.radians(150), 8) + [(-1.0, 1.1), (-0.75, 1.0)]
        fingers = [(-0.55, 1.85), (-0.17, 2.05), (0.21, 1.95), (0.57, 1.6)]
        w = 0.36
        for i, (c, top) in enumerate(fingers):
            base = 1.0 if i == 0 else 1.05
            pts += [(c - w / 2, base if i else 1.0), (c - w / 2, top - w / 2)] + arc(c, top - w / 2, w / 2, math.pi, 0, 8) + [(c + w / 2, 1.05)]
        pts += [(0.82, 0.3), (0.85, -0.3)]
        g = [pts, rect(-1.0, -1.3, 1.0, -0.3), [(-1.0, -0.8), (1.0, -0.8)]]
        g += [[(-0.1, 0.5), (0.3, 0.2)], [(0.4, 0.6), (0.6, 0.2)]]
        return g
    g1 = [transform(s, dx=-1.6, dy=0.4, rot=0.25) for s in glove()]
    g2 = [transform(s, dx=1.6, dy=0.2, rot=-0.25, sx=-1, sy=1) for s in glove()]
    trowel = [chain([(0, 0.25)], quad((0.9, 0.55), (1.8, 0.35), (2.2, 0.0), 10), quad((2.2, 0.0), (1.8, -0.35), (0.9, -0.55), 10), [(0, -0.25), (0, 0.25)]),
              rrect(-1.6, -0.15, -0.2, 0.15, 0.12), [(-0.2, 0.0), (0.0, 0.0)], [(0.3, 0.0), (1.7, 0.0)]]
    trowel = [transform(s, dx=-0.3, dy=-2.4) for s in trowel]
    sprout = [quad((2.6, -2.9), (2.55, -2.3), (2.7, -1.9), 8)] + leaf(2.62, -2.3, 0.6, 2.4) + leaf(2.66, -2.1, 0.6, 0.6)
    ground = [[(-3.2, -2.95), (3.3, -2.95)]]
    return make("Garden Gloves and Trowel", g1 + g2 + trowel + sprout + ground)


@design("spring_flower_wheelbarrow", T)
def flower_wheelbarrow(rng):
    tray = poly((-2.2, 0.0), (1.7, 0.0), (1.1, -1.4), (-1.6, -1.4))
    wheel = [circle(1.5, -2.0, 0.7, 50), circle(1.5, -2.0, 0.15, 12)] + [[(1.5 + 0.15 * math.cos(a), -2.0 + 0.15 * math.sin(a)), (1.5 + 0.65 * math.cos(a), -2.0 + 0.65 * math.sin(a))] for a in [k * math.pi / 3 for k in range(6)]]
    brace = [[(0.9, -1.4), (1.5, -1.85)]]
    handles = [tube([(-1.6, -1.0), (-3.2, -0.3)], 0.2), rrect(-3.5, -0.35, -3.0, -0.05, 0.1)]
    legs = [[(-1.4, -1.4), (-1.5, -2.7)]]
    soil = [wave(-2.1, 1.6, 0.15, 0.08, 6, 50)]
    heads = []
    for k, (x, y, kind) in enumerate([(-1.7, 1.6, 0), (-0.8, 2.3, 1), (0.1, 1.5, 0), (0.9, 2.2, 2), (1.5, 1.2, 1), (-1.1, 0.9, 2)]):
        if kind == 0:
            heads += tulip(x, y - 0.1, 0.55, 0.1 * (k - 2))
        elif kind == 1:
            heads += daisy(x, y + 0.3, 0.5, 10)
        else:
            heads += blossom(x, y + 0.3, 0.45, k)
    stems = [[(x, y - 0.1), (x * 0.8, 0.15)] for x, y in [(-1.7, 1.6), (-0.8, 2.3), (0.1, 1.5), (0.9, 2.2), (1.5, 1.2), (-1.1, 0.9)]]
    stems = hide(stems, *[circle(x, y + 0.3, 0.5, 30) for x, y in [(-0.8, 2.3), (1.5, 1.2), (0.9, 2.2), (-1.1, 0.9)]])
    ground = [[(-3.4, -2.7), (3.2, -2.7)]]
    return make("Wheelbarrow Full of Flowers", [tray] + wheel + brace + handles + legs + soil + heads + stems + ground)


@design("spring_window_box", T)
def window_box(rng):
    frame = [rect(-1.8, -0.6, 1.8, 2.9), rect(-1.6, -0.4, 1.6, 2.7), [(0, -0.4), (0, 2.7)], [(-1.6, 1.15), (1.6, 1.15)]]
    shutters = []
    for x0, x1 in [(-2.9, -1.95), (1.95, 2.9)]:
        shutters += [rect(x0, -0.6, x1, 2.9)] + [[(x0 + 0.1, y), (x1 - 0.1, y)] for y in (-0.1, 0.4, 0.9, 1.4, 1.9, 2.4)]
    box = [poly((-2.3, -0.6), (2.3, -0.6), (2.1, -1.6), (-2.1, -1.6)), [(-2.2, -1.1), (2.2, -1.1)]]
    flowers = (tulip(-1.6, -0.3, 0.55, 0.2) + daisy(-0.7, 0.4, 0.5, 10) + tulip(0.15, -0.2, 0.6) + blossom(0.95, 0.3, 0.45)
               + tulip(1.7, -0.3, 0.5, -0.2))
    stems = [[(-1.6, -0.3), (-1.5, -0.6)], [(-0.7, 0.25), (-0.7, -0.6)], [(0.15, -0.2), (0.15, -0.6)], [(0.95, 0.15), (0.9, -0.6)], [(1.7, -0.3), (1.6, -0.6)]]
    outlines = [s for s in flowers if len(s) > 20]
    frame = hide(frame, *outlines, *[circle(-0.7, 0.4, 0.52, 30), circle(0.95, 0.3, 0.47, 30)])
    ivy = [cubic((-2.0, -1.6), (-2.3, -2.2), (-1.8, -2.6), (-2.1, -3.0), 16), cubic((1.9, -1.6), (2.3, -2.1), (1.8, -2.5), (2.2, -2.9), 16)]
    ivy_leaves = [s for x, y, a in [(-2.12, -2.05, 3.6), (-1.98, -2.55, -0.4), (2.08, -2.0, -0.4), (2.02, -2.5, 3.6)] for s in leaf(x, y, 0.5, a)]
    return make("Window Box in Bloom", frame + shutters + box + flowers + stems + ivy + ivy_leaves)


@design("spring_greenhouse", T)
def greenhouse(rng):
    front = poly((-2.8, -2.4), (-2.8, 0.4), (-1.6, 1.6), (-0.4, 0.4), (-0.4, -2.4))
    door = rect(-2.1, -2.4, -1.1, -0.2)
    fgrid = [[(-1.6, 1.6), (-1.6, -0.2)], [(-2.8, 0.4), (-0.4, 0.4)], [(-2.8, -0.9), (-2.1, -0.9)], [(-1.1, -0.9), (-0.4, -0.9)]]
    roof = poly((-1.6, 1.6), (2.6, 1.6), (3.2, 0.4), (-0.4, 0.4), closed=False)
    side = [[(-0.4, -2.4), (3.2, -2.4)], [(3.2, 0.4), (3.2, -2.4)]]
    panes = [[(x, 0.4), (x, -2.4)] for x in (0.5, 1.4, 2.3)] + [[(-0.4, -0.9), (3.2, -0.9)]] + [[(x - 0.6, 1.6), (x, 0.4)] for x in (0.5, 1.4, 2.3)]
    shelf = [[(-0.2, -1.4), (3.0, -1.4)]]
    pots = []
    for x in (0.1, 0.95, 1.8, 2.65):
        pots += [poly((x - 0.25, -1.4), (x - 0.2, -1.0), (x + 0.2, -1.0), (x + 0.25, -1.4))]
        pots += leaf(x, -1.0, 0.4, 2.0) + leaf(x, -1.0, 0.4, 1.1)
    panes = hide(panes, *[p for p in pots if len(p) == 5 or len(p) > 20])
    path = [quad((-2.1, -2.4), (-2.3, -2.7), (-2.6, -3.0), 6), quad((-1.1, -2.4), (-1.0, -2.7), (-0.8, -3.0), 6)]
    flowers = tulip(-3.15, -2.4, 0.4) + [[(-3.15, -2.4), (-3.15, -2.9)]]
    sun = [circle(1.6, 2.6, 0.45, 30)] + [[(1.6 + 0.6 * math.cos(a), 2.6 + 0.6 * math.sin(a)), (1.6 + 0.85 * math.cos(a), 2.6 + 0.85 * math.sin(a))] for a in [k * math.pi / 4 for k in range(8)]]
    return make("Glass Greenhouse", [front, door, roof] + fgrid + side + panes + shelf + pots + path + flowers + sun)


@design("spring_garden_shed", T)
def garden_shed(rng):
    walls = poly((-2.0, -2.5), (-2.0, 0.6), (0, 2.0), (2.0, 0.6), (2.0, -2.5))
    eaves = poly((-2.4, 0.35), (0, 2.35), (2.4, 0.35), closed=False)
    door = [rect(-0.7, -2.5, 0.7, 0.2), [(-0.7, -0.3), (0.7, -0.3)], [(-0.7, -1.9), (0.7, -1.9)], [(-0.7, -1.9), (0.7, -0.3)]]
    knob = circle(0.45, -1.1, 0.07, 8)
    win = [circle(0, 1.0, 0.35, 24), [(-0.35, 1.0), (0.35, 1.0)], [(0, 0.65), (0, 1.35)]]
    boards = [[(x, -2.5), (x, 0.6 + 0.7 * (2.0 - abs(x)))] for x in (-1.5, -1.0, 1.0, 1.5)]
    shovel = [tube([(2.35, -1.3), (2.95, 0.9)], 0.15), chain(quad((2.2, -1.25), (2.0, -2.2), (2.25, -2.6), 8), quad((2.25, -2.6), (2.6, -2.4), (2.55, -1.35), 8)),
              [(2.2, -1.25), (2.55, -1.35)], rrect(2.75, 0.85, 3.3, 1.05, 0.08)]
    pots = []
    for x, s in [(-2.6, 0.35), (-1.4, 0.3)]:
        pots += [poly((x - s, -2.5), (x - 1.2 * s, -1.9), (x + 1.2 * s, -1.9), (x + s, -2.5))]
    flowers = tulip(-2.6, -1.8, 0.45) + daisy(-1.4, -1.35, 0.35, 8) + [[(-1.4, -1.6), (-1.4, -1.9)], [(-2.6, -1.8), (-2.6, -1.9)]]
    vine = [cubic((-2.0, -2.0), (-2.4, -0.8), (-1.6, 0.2), (-1.4, 1.0), 30)]
    roses = blossom(-2.1, -0.6, 0.3) + blossom(-1.75, 0.3, 0.28)
    vine = hide(vine, circle(-2.1, -0.6, 0.3, 20), circle(-1.75, 0.3, 0.28, 20))
    ground = [[(-3.2, -2.5), (3.4, -2.5)]]
    return make("Garden Shed", [walls, eaves, knob] + door + win + boards + shovel + pots + flowers + vine + roses + ground)


@design("spring_garden_gnome", T)
def garden_gnome(rng):
    hat = smooth([(-1.1, 1.0), (-0.9, 1.9), (-0.4, 2.8), (0.3, 3.3), (0.9, 3.2), (0.6, 2.7), (0.8, 1.9), (1.1, 1.0)], 6)
    brim = quad((-1.15, 1.0), (0, 0.8), (1.15, 1.0), 12)
    nose = circle(0, 0.45, 0.28, 20)
    beard = smooth([(-0.95, 0.5), (-1.2, -0.2), (-0.9, -0.9), (-0.5, -1.35), (0, -1.6), (0.5, -1.35), (0.9, -0.9), (1.2, -0.2), (0.95, 0.5)], 6)
    mustache = [quad((-0.8, 0.3), (-0.4, 0.0), (0, 0.22), 8), quad((0.8, 0.3), (0.4, 0.0), (0, 0.22), 8)]
    body = [quad((-1.1, -0.5), (-1.6, -1.8), (-1.3, -2.4), 12), quad((1.1, -0.5), (1.6, -1.8), (1.3, -2.4), 12)]
    belt = [quad((-1.42, -1.6), (0, -1.75), (1.42, -1.6), 12), quad((-1.4, -1.9), (0, -2.05), (1.4, -1.9), 12), rect(-0.25, -2.0, 0.25, -1.62)]
    belt = hide(belt, beard + [beard[0]])
    boots = [ellipse(-0.7, -2.6, 0.65, 0.25, 24),
             ellipse(0.7, -2.6, 0.65, 0.25, 24)]
    arm = [tube([(1.25, -0.7), (1.9, -0.9), (2.3, -0.4)], 0.35)]
    hand = circle(2.35, -0.25, 0.22, 16)
    flower = blossom(2.5, 1.4, 0.6) + [[(2.4, -0.05), (2.5, 0.8)]]
    mush = [chain(arc(-2.4, -1.6, 0.7, 0, math.pi, 20), quad((-3.1, -1.6), (-2.4, -1.85), (-1.7, -1.6), 10)), [(-2.6, -1.75), (-2.65, -2.7)], [(-2.2, -1.75), (-2.15, -2.7)],
            circle(-2.6, -1.25, 0.12, 10), circle(-2.2, -1.05, 0.1, 10)]
    ground = [[(-3.3, -2.75), (3.0, -2.75)]]
    return make("Garden Gnome with a Flower", [hat, brim, nose, beard, hand] + mustache + body + belt + boots + arm + flower + mush + ground,
                [eye(-0.35, 0.78, 0.08), eye(0.35, 0.78, 0.08)])


@design("spring_flower_cart", T)
def flower_cart(rng):
    box = [rect(-2.4, -1.2, 1.8, 0.0)] + [[(x, -1.2), (x, 0.0)] for x in (-1.35, -0.3, 0.75)]
    wheel = [circle(-1.4, -1.9, 0.9, 60), circle(-1.4, -1.9, 0.15, 12)] + [[(-1.4 + 0.15 * math.cos(a), -1.9 + 0.15 * math.sin(a)), (-1.4 + 0.85 * math.cos(a), -1.9 + 0.85 * math.sin(a))] for a in [k * math.pi / 4 for k in range(8)]]
    box = hide(box, circle(-1.4, -1.9, 0.9, 60))
    leg = [[(1.4, -1.2), (1.4, -2.8)]]
    handle = [[(1.8, -0.4), (3.3, 0.2)], [(1.8, -0.7), (3.3, -0.1)], rrect(3.2, -0.2, 3.6, 0.3, 0.1)]
    buckets = []
    heads = []
    for k, x in enumerate((-1.7, -0.3, 1.1)):
        buckets.append(poly((x - 0.5, 0.0), (x - 0.6, 0.9), (x + 0.6, 0.9), (x + 0.5, 0.0)))
        if k == 0:
            heads += tulip(x - 0.35, 1.3, 0.45, 0.25) + tulip(x + 0.35, 1.4, 0.45, -0.2) + tulip(x, 1.9, 0.45)
            heads += [[(x - 0.35, 1.3), (x - 0.2, 0.9)], [(x + 0.35, 1.4), (x + 0.2, 0.9)], [(x, 1.9), (x, 0.9)]]
        elif k == 1:
            heads += daisy(x - 0.35, 1.6, 0.42, 10) + daisy(x + 0.4, 1.8, 0.42, 10) + daisy(x, 2.5, 0.4, 10)
            heads += hide([[(x - 0.35, 1.6), (x - 0.15, 0.9)], [(x + 0.4, 1.8), (x + 0.15, 0.9)], [(x, 2.5), (x, 0.9)]],
                          circle(x - 0.35, 1.6, 0.43, 20), circle(x + 0.4, 1.8, 0.43, 20), circle(x, 2.5, 0.41, 20))
        else:
            heads += blossom(x - 0.3, 1.5, 0.4) + blossom(x + 0.35, 1.7, 0.4) + blossom(x, 2.35, 0.38)
            heads += hide([[(x - 0.3, 1.5), (x - 0.15, 0.9)], [(x + 0.35, 1.7), (x + 0.15, 0.9)], [(x, 2.35), (x, 0.9)]],
                          circle(x - 0.3, 1.5, 0.4, 20), circle(x + 0.35, 1.7, 0.4, 20), circle(x, 2.35, 0.38, 20))
    ground = [[(-3.2, -2.8), (3.4, -2.8)]]
    return make("Flower Market Cart", box + wheel + leg + handle + buckets + heads + ground)


@design("spring_picnic_blanket", T)
def picnic_blanket(rng):
    blanket = poly((-3.2, -2.8), (3.2, -2.8), (2.2, -0.4), (-2.2, -0.4))
    lines = [[(-3.2 + 6.4 * k / 6, -2.8), (-2.2 + 4.4 * k / 6, -0.4)] for k in range(1, 6)]
    for k in range(1, 4):
        t = k / 4
        y = -2.8 + 2.4 * t
        w = 3.2 - 1.0 * t
        lines.append([(-w, y), (w, y)])
    pitcher = smooth([(-2.0, -1.9), (-2.35, -1.2), (-2.25, -0.4), (-1.95, 0.05), (-2.0, 0.4), (-2.35, 0.55), (-1.6, 0.5), (-1.15, 0.45),
                      (-1.2, 0.05), (-0.95, -0.5), (-0.9, -1.2), (-1.15, -1.9), (-2.0, -1.9)], 5)
    p_handle = arc(-0.95, -0.45, 0.55, math.radians(110), math.radians(-80), 14)
    lemon = [circle(-1.6, -1.0, 0.3, 20)] + [[(-1.6, -1.0), (-1.6 + 0.25 * math.cos(a), -1.0 + 0.25 * math.sin(a))] for a in [k * math.pi / 3 for k in range(6)]]
    glass = [poly((-0.6, -1.4), (-0.7, -0.2), (0.0, -0.2), (-0.1, -1.4)), [(-0.66, -0.5), (-0.04, -0.5)], [(-0.2, -0.2), (0.2, 0.6)]]
    plate = [ellipse(1.3, -1.6, 1.1, 0.4, 50), ellipse(1.3, -1.6, 0.8, 0.27, 40)]
    sandwich = [poly((0.7, -1.5), (1.7, -1.4), (1.1, -0.8)), poly((0.7, -1.5), (0.75, -1.65), (1.75, -1.55), (1.7, -1.4), closed=False)]
    plate = hide(plate, sandwich[0], poly((0.7, -1.5), (0.75, -1.65), (1.75, -1.55), (1.7, -1.4)))
    outl = [pitcher, glass[0], ellipse(1.3, -1.6, 1.1, 0.4, 50)]
    lines = hide(lines + [blanket], *outl)
    tree_ = tree(2.6, -0.4, 1.4, 0.7, 1.0, 9)
    tree_ = hide(tree_, blanket)
    sun = [circle(-2.4, 2.4, 0.45, 30)]
    cl = [cloud(0.0, 2.2, 1.0, 0.6)]
    return make("Picnic on the Grass", lines + [p_handle] + lemon + glass + plate + sandwich + [pitcher] + tree_ + sun + cl)


@design("spring_rain_boot_planters", T)
def rain_boot_planters(rng):
    b1 = boot(-1.5, -0.9, 0.95)
    b2 = boot(1.3, -1.1, 0.9)
    fl = tulip(-1.75, 1.6, 0.6, 0.25) + tulip(-1.0, 1.9, 0.6, -0.1) + daisy(1.0, 1.6, 0.55, 10) + daisy(1.85, 1.15, 0.5, 10)
    stems = [[(-1.75, 1.6), (-1.6, 1.15)], [(-1.0, 1.9), (-1.2, 1.15)], [(1.0, 1.45), (1.2, 0.9)], [(1.85, 1.0), (1.6, 0.9)]]
    stems = hide(stems, circle(1.0, 1.6, 0.56, 20), circle(1.85, 1.15, 0.51, 20))
    lv = leaf(-1.55, 1.15, 0.7, 2.6) + leaf(1.3, 0.9, 0.6, 0.4)
    puddle = [ellipse(0, -2.75, 3.0, 0.3, 80)]
    drops = [lens((x, y), (x, y - 0.4), 0.4) for x, y in [(-2.8, 2.6), (0.2, 3.0), (2.6, 2.8), (2.8, 0.4), (-2.9, 0.0)]]
    return make("Rain Boots Planted with Flowers", b1 + b2 + fl + stems + lv + puddle + drops)


@design("spring_wind_chime", T)
def wind_chime(rng):
    branch = [quad((-3.2, 2.9), (0, 2.5), (3.2, 3.0), 20), quad((-3.2, 2.6), (0, 2.2), (3.2, 2.7), 20)]
    bl = blossom(-2.0, 2.2, 0.4) + blossom(1.6, 2.35, 0.4) + leaf(-1.0, 2.4, 0.6, -0.6) + leaf(2.5, 2.7, 0.6, -0.9)
    hook = [[(0, 2.27), (0, 1.6)]]
    disc = [ellipse(0, 1.4, 1.5, 0.25, 50), [(-1.5, 1.4), (-1.5, 1.2)], [(1.5, 1.4), (1.5, 1.2)], quad((-1.5, 1.2), (0, 0.9), (1.5, 1.2), 20)]
    hook = hide(hook, ellipse(0, 1.4, 1.5, 0.25, 50))
    tubes = []
    for x, L in [(-1.2, 2.4), (-0.6, 2.9), (0.6, 2.7), (1.2, 2.1)]:
        tubes += [[(x, 1.0 + (0.1 if abs(x) > 1 else 0.0)), (x, 0.7)], rrect(x - 0.17, 0.7 - L, x + 0.17, 0.7, 0.08)]
    string = [[(0, 0.92), (0, -0.6)], [(0, -0.8), (0, -1.8)]]
    striker = [ellipse(0, -0.7, 0.45, 0.1, 20)]
    sail = blossom(0, -2.4, 0.6)
    return make("Garden Wind Chime", branch + bl + hook + disc + tubes + string + striker + sail)


# ------------------------------------------------------------ trees & scenes

@design("spring_blossom_tree_bench", T)
def blossom_tree_bench(rng):
    crown = bumpy(0.2, 1.3, 2.9, 1.6, 16, 0.1)
    trunk = [chain(quad((-0.9, -2.6), (-0.4, -2.3), (-0.35, -1.0), 10), quad((-0.35, -1.0), (-0.4, -0.4), (-1.2, 0.3), 10)),
             chain(quad((0.9, -2.6), (0.35, -2.3), (0.35, -1.0), 10), quad((0.35, -1.0), (0.4, -0.3), (1.3, 0.4), 10)), [(0.0, -0.9), (0.1, 0.5)]]
    bl = []
    for k, (x, y) in enumerate([(-2.0, 1.5), (-1.0, 2.2), (0.3, 2.4), (1.6, 2.0), (2.4, 1.0), (-1.6, 0.4), (0.9, 1.0), (-0.4, 1.3), (1.9, -0.1), (-2.4, 0.6)]):
        bl += blossom(x, y, 0.3, k)
    bench_back = [rect(-2.9, -1.7, -1.0, -1.2), rect(-2.9, -1.1, -1.0, -0.8)]
    bench = [rect(-3.0, -2.0, -0.9, -1.8), [(-2.8, -2.0), (-2.8, -2.6)], [(-1.1, -2.0), (-1.1, -2.6)], [(-2.8, -1.8), (-2.8, -0.8)], [(-1.1, -1.8), (-1.1, -0.8)]]
    falling = [lens((x, y), (x + 0.25, y - 0.15), 0.4) for x, y in [(2.0, -1.4), (2.6, -2.2), (1.4, -2.0), (-0.4, -1.7), (3.0, -0.8)]]
    ground = [[(-3.4, -2.6), (3.4, -2.6)]]
    return make("Blossoming Tree and Bench", [crown] + trunk + bl + bench_back + bench + falling + ground)


@design("spring_windmill_tulips", T)
def windmill_tulips(rng):
    tower = poly((-1.0, -0.6), (-0.6, 1.8), (0.6, 1.8), (1.0, -0.6))
    cap = chain([(-0.75, 1.8)], arc(0, 1.8, 0.75, math.pi, 0, 16), [(0.75, 1.8)])
    door = chain([(-0.25, -0.6), (-0.25, -0.1)], arc(0, -0.1, 0.25, math.pi, 0, 8), [(0.25, -0.6)])
    win = [rect(-0.18, 0.7, 0.18, 1.1)]
    hub = (0, 2.0)
    sails = []
    for k in range(4):
        a = 0.35 + k * math.pi / 2
        c, s = math.cos(a), math.sin(a)
        def P(u, v):
            return (hub[0] + u * c - v * s, hub[1] + u * s + v * c)
        sails.append(poly(P(0.5, 0.0), P(2.6, 0.0), P(2.6, 0.55), P(0.5, 0.55)))
        sails.append([P(0.2, 0.0), P(2.6, 0.0)])
        sails += [[P(u, 0.0), P(u, 0.55)] for u in (1.1, 1.7)]
        sails.append([P(0.5, 0.28), P(2.6, 0.28)])
    sails = hide(sails, tower, cap + [(-0.75, 1.8)])
    sails = [s for s in sails]
    hubc = [circle(0, 2.0, 0.15, 12)]
    field = [[(-3.4, -0.6), (3.4, -0.6)]]
    rows = []
    for r, (y, s) in enumerate([(-1.0, 0.25), (-1.6, 0.32), (-2.35, 0.4)]):
        n = 8 - r
        for k in range(n):
            x = -3.0 + 6.0 * (k + 0.5 * (r % 2)) / (n - 0.5)
            rows += tulip(x, y, s)
        rows.append([(-3.4, y - 0.1), (3.4, y - 0.1)])
    rows = [s for s in rows]
    return make("Windmill and Tulip Fields", [tower, cap, door] + win + sails + hubc + field + rows)


@design("spring_kite_flyer", T)
def kite_flyer(rng):
    head = circle(-1.6, -0.2, 0.4, 30)
    hair = [quad((-2.0, -0.1), (-2.3, -0.4), (-2.2, -0.8), 6), arc(-1.6, -0.2, 0.45, math.radians(60), math.radians(190), 12)]
    body = poly((-1.6, -0.6), (-2.1, -1.8), (-1.1, -1.8))
    arms = [[(-1.45, -0.85), (-0.9, -0.3), (-0.6, 0.2)], [(-1.8, -0.9), (-2.4, -1.4)]]
    legs = [[(-1.8, -1.8), (-2.2, -2.5), (-2.6, -2.4)], [(-1.4, -1.8), (-1.2, -2.6), (-0.9, -2.6)]]
    kite = poly((1.8, 3.0), (2.8, 2.0), (2.0, 0.8), (1.0, 1.9))
    spars = [[(1.8, 3.0), (2.0, 0.8)], [(1.0, 1.9), (2.8, 2.0)]]
    tail = cubic((2.0, 0.8), (2.6, 0.0), (1.6, -0.4), (2.6, -1.4), 30)
    bows = [transform(lens((-0.25, 0), (0.25, 0), 0.5, 8), dx=tail[i][0], dy=tail[i][1], rot=0.6) for i in (10, 20)]
    string = [quad((-0.6, 0.2), (0.6, 0.0), (2.0, 0.8), 20)]
    hill = [quad((-3.4, -2.2), (0.0, -2.9), (3.4, -2.0), 30)]
    flowers = daisy(0.6, -2.0, 0.3, 8) + daisy(2.4, -2.2, 0.28, 8)
    cl = [cloud(-1.8, 2.3, 1.0, 0.55), cloud(0.2, 1.4, 0.7, 0.4)]
    return make("Child Flying a Kite", [head, body, kite, tail] + hair + arms + legs + spars + bows + string + hill + flowers + cl,
                [eye(-1.45, -0.15, 0.06)])


@design("spring_sunny_meadow", T)
def sunny_meadow(rng):
    sun = [circle(0, 1.8, 0.8, 50)] + [lens((0.95 * math.cos(a), 1.8 + 0.95 * math.sin(a)), (1.5 * math.cos(a), 1.8 + 1.5 * math.sin(a)), 0.25, 8) for a in [k * TAU / 12 for k in range(12)]]
    hills = [quad((-3.4, -0.3), (-1.4, 0.8), (0.6, -0.4), 30), quad((0.0, -0.4), (2.0, 0.6), (3.4, -0.2), 30)]
    hills = [hide([hills[0]], poly((0.0, -0.4), *hills[1], (3.4, -3), (0, -3)))[0], hills[1]]
    fl = []
    for x, y, r in [(-2.4, -1.3, 0.45), (-1.0, -2.0, 0.55), (0.6, -1.4, 0.4), (2.0, -2.2, 0.5), (2.7, -1.0, 0.35), (-2.7, -2.5, 0.35)]:
        fl += daisy(x, y, r, 10)
        fl.append([(x, y - 0.28 * r), (x, -3.0)])
    fl = [s for s in fl]
    bf = [lens((-1.2, 0.0), (-1.7, 0.4), 0.6), lens((-1.2, 0.0), (-0.7, 0.4), 0.6), [(-1.2, -0.1), (-1.2, 0.2)]]
    return make("Sunny Spring Meadow", sun + hills + fl + bf)


def nest(cx, cy, rx, ry, depth):
    """Front of a twig nest; returns (strokes, outline of the bowl, front rim test)."""
    bowl = chain([(cx - rx, cy)], cubic((cx - rx, cy), (cx - rx, cy - depth), (cx - 0.4 * rx, cy - 1.1 * depth), (cx, cy - 1.1 * depth), 20),
                 cubic((cx, cy - 1.1 * depth), (cx + 0.4 * rx, cy - 1.1 * depth), (cx + rx, cy - depth), (cx + rx, cy), 20))
    rim_front = [(cx + rx * math.cos(t), cy + ry * math.sin(t)) for t in [math.pi + math.pi * i / 40 for i in range(41)]]
    twigs = [quad((cx - 0.9 * rx, cy - (0.3 + 0.25 * k) * depth), (cx, cy - (0.55 + 0.25 * k) * depth), (cx + 0.9 * rx, cy - (0.25 + 0.25 * k) * depth), 16) for k in range(3)]
    twigs += [[(cx - 0.95 * rx, cy - 0.15 * depth), (cx - 1.25 * rx, cy + 0.05)], [(cx + 0.97 * rx, cy - 0.35 * depth), (cx + 1.25 * rx, cy - 0.2 * depth)]]
    twigs = clip(twigs[0], lambda p: True) + twigs[1:]
    out_shape = chain(rim_front[::-1], bowl[1:])
    return [bowl, rim_front] + twigs, out_shape


@design("spring_bird_nest", T)
def bird_nest(rng):
    branch = [quad((-3.4, -2.2), (0.0, -1.6), (3.4, -2.4), 30), quad((-3.4, -2.6), (0.0, -2.0), (3.4, -2.75), 30)]
    parts, shape = nest(0, -0.2, 2.2, 0.5, 1.5)
    eggs = [ellipse(-0.85, 0.15, 0.52, 0.7, 40, rot=0.25), ellipse(0.0, 0.4, 0.52, 0.72, 40), ellipse(0.85, 0.1, 0.52, 0.7, 40, rot=-0.25)]
    eggs = hide([eggs[1]], eggs[0], eggs[2]) + [eggs[0], eggs[2]]
    speck = [circle(x, y, 0.07, 8) for x, y in [(-0.9, 0.35), (-0.7, 0.05), (0.1, 0.7), (-0.1, 0.45), (0.95, 0.3), (0.75, 0.0)]]
    rim_back = [(2.2 * math.cos(t), -0.2 + 0.5 * math.sin(t)) for t in [math.pi * i / 40 for i in range(41)]]
    rim_back = hide([rim_back], ellipse(-0.85, 0.15, 0.52, 0.7, 40, rot=0.25), ellipse(0.0, 0.4, 0.52, 0.72, 40), ellipse(0.85, 0.1, 0.52, 0.7, 40, rot=-0.25))
    eggs = [s for e in eggs for s in clip(e, lambda p: not (abs(p[0]) < 2.2 and p[1] < -0.2 - 0.5 * math.sqrt(max(0.0, 1 - (p[0] / 2.2) ** 2))))]
    branch = hide(branch, shape + [shape[0]])
    lv = leaf(-2.4, -1.95, 1.0, 2.3) + leaf(2.3, -2.05, 1.0, 0.7) + leaf(2.6, -2.2, 0.9, -0.4)
    bl = blossom(-2.4, 1.6, 0.5) + blossom(2.3, 1.9, 0.45, 0.4)
    return make("Bird's Nest with Eggs", parts + eggs + speck + rim_back + branch + lv + bl)


@design("spring_baby_birds", T)
def baby_birds(rng):
    parts, shape = nest(0, -1.2, 2.2, 0.45, 1.4)
    chicks = []
    outl = []
    for x, y, tilt in [(-1.1, -0.6, 0.35), (0.0, -0.35, 0.0), (1.1, -0.65, -0.35)]:
        head = circle(x, y, 0.5, 40)
        up = transform(poly((-0.32, 0.2), (0.0, 1.15), (0.32, 0.2), closed=False), dx=x, dy=y, rot=tilt)
        low = transform(poly((-0.3, 0.15), (0.0, 0.6), (0.3, 0.15), closed=False), dx=x, dy=y, rot=tilt)
        chicks += [head, up, low]
        outl.append(head)
    chicks = hide([chicks[0], chicks[1], chicks[2]], circle(0.0, -0.35, 0.5, 40)) + hide([chicks[6], chicks[7], chicks[8]], circle(0.0, -0.35, 0.5, 40)) + chicks[3:6]
    chicks = [s for c in chicks for s in clip(c, lambda p: not (abs(p[0]) < 2.2 and p[1] < -1.2 - 0.45 * math.sqrt(max(0.0, 1 - (p[0] / 2.2) ** 2))))]
    rim_back = hide([[(2.2 * math.cos(t), -1.2 + 0.45 * math.sin(t)) for t in [math.pi * i / 40 for i in range(41)]]], *outl)
    parent, pe = songbird(1.4, 2.0, 0.85, flip=True, legs=False, rot=-0.15)
    worm = [[(0.15 + 0.12 * math.sin(5 * t), 2.2 - 0.9 * t) for t in [i / 20 for i in range(21)]]]
    hints = [eye(-1.28, -0.5, 0.07), eye(-0.15, -0.25, 0.07), eye(0.95, -0.55, 0.07), pe]
    branch = hide([[(-3.4, -2.3), (3.4, -2.1)], [(-3.4, -2.65), (3.4, -2.45)]], shape + [shape[0]])
    return make("Baby Birds Waiting to Be Fed", parts + chicks + rim_back + parent + worm + branch, hints)


@design("spring_bluebird_blossom", T)
def bluebird_blossom(rng):
    branch = [quad((-3.4, -1.2), (0.0, -0.9), (3.4, 0.2), 30), quad((-3.4, -1.55), (0.0, -1.25), (3.4, -0.1), 30),
              quad((1.5, -0.6), (2.0, 0.6), (2.7, 1.6), 12), quad((1.75, -0.5), (2.2, 0.6), (2.85, 1.45), 12)]
    bird, be = songbird(-0.2, 0.0, 1.35, flip=True)
    outline = bird[0]
    branch = hide(branch, outline)
    bl = []
    for k, (x, y, r) in enumerate([(-2.6, -0.5, 0.5), (-1.8, -2.1, 0.45), (2.9, 1.9, 0.5), (1.6, 1.1, 0.45), (2.7, -0.8, 0.45), (1.1, -1.7, 0.4)]):
        bl += blossom(x, y, r, 0.3 * k)
    bl = hide(bl, outline)
    lv = leaf(-1.0, -1.15, 0.8, -1.9) + leaf(0.6, -0.75, 0.8, 1.6)
    lv = hide(lv, outline)
    buds = [lens((-2.9, 0.3), (-3.1, 1.0), 0.3), [(-2.85, -0.9), (-2.9, 0.3)]]
    return make("Bluebird on a Blossom Branch", bird + branch + bl + lv + buds, [be])


@design("spring_swallows", T)
def swallows(rng):
    wire = [quad((-3.4, -0.2), (0.0, -0.8), (3.4, -0.2), 40)]
    def perched(x, s, flip):
        y = yat(wire[0], x) + 0.6 * s
        b, e = songbird(x, y + 0.15 * s, s, flip=flip, legs=False, rot=0.0)
        sx = -1 if flip else 1
        tail = [transform(poly((-1.45, 0.12), (-2.4, -0.25), (-1.9, 0.0), (-2.3, 0.15), (-1.5, 0.05), closed=False), dx=x, dy=y + 0.15 * s, sx=sx * s, sy=s)]
        feet = [[(x, y - 0.35 * s), (x, yat(wire[0], x))], [(x + 0.3 * s * sx, y - 0.3 * s), (x + 0.3 * s * sx, yat(wire[0], x + 0.3 * s * sx))]]
        return b + tail + feet, e
    a, ea = perched(-1.4, 0.8, False)
    b, eb = perched(1.3, 0.8, True)
    fly = [swallow_flying(0.1, 2.6, 0.65, -1.1), swallow_flying(-2.3, 2.6, 0.45, -0.7)]
    poles = [[(-3.0, -0.3), (-3.0, -3.0)], [(-2.75, -0.35), (-2.75, -3.0)], [(3.0, -0.3), (3.0, -3.0)], [(2.75, -0.35), (2.75, -3.0)]]
    wire = hide(wire, a[0], b[0])
    grass_ = [grass(-3.4, 3.4, -3.0, 0.3, 20)]
    cl = [cloud(2.2, 2.6, 0.9, 0.5)]
    return make("Swallows on a Wire", wire + a + b + fly + poles + grass_ + cl, [ea, eb])


@design("spring_hummingbird", T)
def hummingbird(rng):
    body = smooth([(-0.95, 1.05), (-0.7, 1.38), (-0.3, 1.42), (0.0, 1.2), (0.4, 0.7), (1.0, 0.1), (1.6, -0.55), (1.85, -1.1), (1.45, -0.85),
                   (1.25, -1.15), (0.8, -0.45), (0.2, -0.15), (-0.4, 0.3), (-0.8, 0.7), (-0.95, 1.05)], 5)
    beak = poly((-0.93, 1.1), (-2.2, 1.0), (-0.88, 0.92), closed=False)
    wing1 = smooth([(0.0, 0.85), (0.1, 1.8), (0.6, 2.7), (1.4, 3.1), (1.1, 2.2), (0.7, 1.2), (0.35, 0.65)], 5)
    wing2 = smooth([(0.3, 0.75), (0.9, 1.4), (1.8, 2.2), (2.6, 2.4), (1.9, 1.5), (1.0, 0.7), (0.55, 0.45)], 5)
    wing2 = hide([wing2], wing1 + [wing1[0]])
    feathers = [quad((0.25, 1.4), (0.5, 2.0), (1.0, 2.6), 8), quad((0.45, 1.1), (0.7, 1.7), (1.15, 2.2), 8)]
    throat = quad((-0.85, 0.85), (-0.5, 0.5), (-0.1, 0.55), 8)
    flower = smooth([(-2.2, 1.55), (-2.05, 1.0), (-2.2, 0.45), (-2.5, 0.75), (-3.1, 1.2), (-3.4, 1.7), (-3.1, 1.75), (-2.5, 1.35), (-2.2, 1.55)], 5)
    mouth = ellipse(-2.15, 1.0, 0.13, 0.55, 20)
    beak = hide([beak], mouth)
    stem = [quad((-3.25, 1.75), (-3.0, 2.6), (-2.2, 3.2), 10)]
    flower2 = [transform(s, dx=0.6, dy=-2.1) for s in [smooth([(-2.2, 1.55), (-2.05, 1.0), (-2.2, 0.45), (-2.5, 0.75), (-3.1, 1.2), (-3.4, 1.7), (-3.1, 1.75), (-2.5, 1.35), (-2.2, 1.55)], 5), ellipse(-2.15, 1.0, 0.13, 0.55, 20)]]
    vine = [cubic((-2.2, 3.2), (-1.0, 2.6), (-3.6, -0.2), (-2.65, -0.4), 30)]
    lv = leaf(-2.6, 2.7, 0.8, 2.6) + leaf(-2.9, 0.4, 0.7, -2.5)
    return make("Hummingbird at a Trumpet Flower", [body, wing1, throat, flower, mouth] + beak + wing2 + feathers + stem + flower2 + vine + lv,
                [eye(-0.55, 1.15, 0.08)])


@design("spring_butterfly_flower", T)
def butterfly_flower(rng):
    up = smooth([(0.12, 0.3), (0.7, 1.5), (1.8, 2.05), (2.35, 1.5), (1.9, 0.55), (0.12, 0.0)], 8)
    low = smooth([(0.12, -0.1), (1.3, -0.25), (1.7, -1.05), (1.0, -1.6), (0.4, -1.15), (0.12, -0.4)], 8)
    deco = [circle(1.6, 1.3, 0.3, 20), circle(1.0, -0.85, 0.22, 16), quad((0.35, 0.35), (1.0, 0.9), (1.8, 0.7), 10), circle(0.9, 1.25, 0.15, 12)]
    wings = [up, low] + deco
    wings += [mirror_x(s) for s in wings]
    body = ellipse(0, -0.2, 0.14, 1.0, 30)
    head = circle(0, 0.98, 0.2, 16)
    ant = [cubic((-0.05, 1.15), (-0.2, 1.7), (-0.5, 2.0), (-0.75, 2.1), 12), cubic((0.05, 1.15), (0.2, 1.7), (0.5, 2.0), (0.75, 2.1), 12),
           circle(-0.8, 2.12, 0.08, 8), circle(0.8, 2.12, 0.08, 8)]
    fly = [transform(s, dx=0.9, dy=1.0, s=0.85, rot=-0.25) for s in wings + [body, head] + ant]
    flower = daisy(-1.6, -1.3, 1.1, 10, 0.1, 0.32)
    stem = [quad((-1.6, -1.65), (-1.7, -2.4), (-1.4, -3.0), 8)]
    lv = leaf(-1.62, -2.4, 0.8, 2.6) + leaf(-1.55, -2.6, 0.8, 0.3)
    small = daisy(1.9, -2.2, 0.55, 8) + [[(1.9, -2.38), (1.9, -3.0)]]
    return make("Butterfly over a Daisy", fly + flower + stem + lv + small)


@design("spring_ladybug_leaf", T)
def ladybug_leaf(rng):
    lf = lens((-3.0, -2.4), (3.0, 2.2), 0.28, 60)
    mid = [(-3.0, -2.4), (2.6, 1.9)]
    side = []
    for k in range(1, 6):
        t = k / 6.2
        px, py = -3.0 + 6.0 * t, -2.4 + 4.6 * t
        side += [[(px, py), (px - 0.2, py + 0.9)], [(px, py), (px + 0.7, py - 0.6)]]
    stalk = [(-3.0, -2.4), (-3.4, -2.9)]
    bx, by, rot = 0.4, 0.1, -0.65
    shell = ellipse(bx, by, 1.05, 1.25, 60, rot=rot)
    head = transform(chain(arc(0, 1.2, 0.55, math.radians(-15), math.radians(195), 20)), dx=bx, dy=by, rot=rot)
    split = transform([(0, 1.25), (0, -1.25)], dx=bx, dy=by, rot=rot)
    spots = [transform(circle(x, y, r, 14), dx=bx, dy=by, rot=rot) for x, y, r in [(-0.5, 0.5, 0.2), (0.5, 0.5, 0.2), (-0.55, -0.35, 0.22), (0.55, -0.35, 0.22), (-0.25, -0.9, 0.15), (0.25, -0.9, 0.15)]]
    legs = [transform([(sx * 0.95, y), (sx * 1.35, y - 0.25)], dx=bx, dy=by, rot=rot) for sx in (-1, 1) for y in (0.5, 0.0, -0.5)]
    ant = [transform(quad((sx * 0.2, 1.65), (sx * 0.35, 2.0), (sx * 0.65, 2.1), 6), dx=bx, dy=by, rot=rot) for sx in (-1, 1)]
    bug = [shell, head] + spots + [split]
    leafs = hide([lf] + [mid] + side, shell, head + [head[0]], *legs)
    drops = [chain(arc(x, y, 0.2, math.radians(-30), math.radians(210), 12), [(x, y + 0.45)], [arc(x, y, 0.2, math.radians(-30), 0, 2)[0]]) for x, y in [(-1.6, -1.8), (1.9, 0.0)]]
    return make("Ladybug Resting on a Dewy Leaf", leafs + [stalk] + bug + legs + ant + drops)


@design("spring_bumblebee_flower", T)
def bumblebee_flower(rng):
    fc = (-0.9, -0.7)
    petals_ = [petal((fc[0] + 0.55 * math.cos(a), fc[1] + 0.55 * math.sin(a)), (fc[0] + 2.0 * math.cos(a), fc[1] + 2.0 * math.sin(a)), 0.3, 14) for a in [TAU * k / 8 + 0.2 for k in range(8)]]
    centre = [circle(fc[0], fc[1], 0.55, 30), circle(fc[0], fc[1], 0.3, 20)]
    stem = [quad((fc[0] + 0.2, -2.6), (fc[0] + 0.4, -3.0), (fc[0] + 0.3, -3.3), 6)]
    bx, by = 1.7, 2.0
    body = ellipse(bx, by, 0.85, 0.6, 50, rot=0.2)
    stripes = [s for x in (-0.25, 0.15, 0.5) for s in clip(transform([(x, -0.7), (x, 0.7)], dx=bx, dy=by, rot=0.2), lambda p: ((p[0] - bx) * math.cos(0.2) + (p[1] - by) * math.sin(0.2)) ** 2 / 0.85 ** 2 + (-(p[0] - bx) * math.sin(0.2) + (p[1] - by) * math.cos(0.2)) ** 2 / 0.6 ** 2 < 0.97)]
    head = circle(bx - 0.95, by - 0.2, 0.35, 24)
    wings = [lens((bx - 0.1, by + 0.45), (bx - 0.6, by + 1.6), 0.4), lens((bx + 0.15, by + 0.45), (bx + 0.6, by + 1.5), 0.4)]
    sting = poly((bx + 0.8, by + 0.2), (bx + 1.15, by + 0.2), (bx + 0.82, by + 0.05), closed=False)
    ant = [quad((bx - 1.1, by + 0.1), (bx - 1.3, by + 0.6), (bx - 1.5, by + 0.65), 6), quad((bx - 0.95, by + 0.15), (bx - 1.0, by + 0.6), (bx - 1.15, by + 0.8), 6)]
    path = []
    trail = cubic((bx + 1.1, by - 0.3), (3.6, 0.0), (1.8, -0.4), (2.6, -1.6), 40)
    for i in range(0, 40, 4):
        path.append(trail[i:i + 3])
    head_ok = hide([head], body)
    return make("Bumblebee and Cosmos Flower", petals_ + centre + stem + [body] + stripes + head_ok + wings + [sting] + ant + path,
                [eye(bx - 1.05, by - 0.12, 0.07)])


@design("spring_caterpillar", T)
def caterpillar(rng):
    stem = [quad((-3.4, -2.6), (0.0, -1.2), (3.4, -2.4), 30), quad((-3.4, -2.9), (0.0, -1.5), (3.4, -2.7), 30)]
    path = [(-2.4 + 3.6 * t, -1.35 + 1.6 * math.sin(math.pi * t) ** 1.5) for t in [i / 8 for i in range(9)]]
    segs = [circle(x, y, 0.45, 30) for x, y in path[:-1]]
    hx, hy = path[-1][0] + 0.15, path[-1][1] + 0.35
    head = circle(hx, hy, 0.65, 40)
    out = []
    order = segs + [head]
    for i, s in enumerate(order):
        out += hide([s], *order[i + 1:])
    feet = [[(x, y - 0.45), (x, y - 0.65)] for x, y in path[:-1] if y < -0.6]
    ant = [quad((hx - 0.2, hy + 0.6), (hx - 0.4, hy + 1.1), (hx - 0.6, hy + 1.2), 6), quad((hx + 0.2, hy + 0.6), (hx + 0.35, hy + 1.1), (hx + 0.6, hy + 1.2), 6),
           circle(hx - 0.65, hy + 1.22, 0.1, 8), circle(hx + 0.65, hy + 1.22, 0.1, 8)]
    smile = arc(hx, hy - 0.05, 0.3, math.radians(210), math.radians(330), 8)
    big_leaf = lens((-0.6, -1.65), (-2.8, 1.6), 0.3, 40)
    bite = [arc(-2.4, 0.2, 0.32, math.radians(120), math.radians(300), 10)]
    vein = hide([[(-0.6, -1.65), (-2.6, 1.3)]], *segs)
    big_leaf = hide([big_leaf], *segs)
    stem = hide(stem, *segs)
    lv2 = leaf(2.4, -2.25, 1.0, 0.6)
    return make("Caterpillar on a Stem", out + feet + ant + [smile] + big_leaf + bite + vein + stem + lv2,
                [eye(hx - 0.22, hy + 0.12, 0.08), eye(hx + 0.22, hy + 0.12, 0.08)])


@design("spring_dragonfly_pond", T)
def dragonfly_pond(rng):
    rot = -0.5
    def T_(s):
        return transform(s, dx=0.4, dy=1.0, rot=rot)
    eyes_ = [circle(-0.22, 1.55, 0.25, 20), circle(0.22, 1.55, 0.25, 20)]
    thorax = ellipse(0, 0.9, 0.3, 0.5, 30)
    abdomen = tube([(0, 0.4), (0, -2.6)], lambda t: 0.28 - 0.12 * t)
    rings = [[(-0.12, y), (0.12, y)] for y in (-0.1, -0.6, -1.1, -1.6, -2.1)]
    wings = [lens((0.2, 1.05), (2.6, 1.5), 0.17, 24), lens((0.2, 0.8), (2.4, 0.25), 0.17, 24), lens((-0.2, 1.05), (-2.6, 1.5), 0.17, 24), lens((-0.2, 0.8), (-2.4, 0.25), 0.17, 24)]
    veins = [[(0.3, 1.1), (2.4, 1.48)], [(0.3, 0.78), (2.2, 0.3)], [(-0.3, 1.1), (-2.4, 1.48)], [(-0.3, 0.78), (-2.2, 0.3)]]
    df = [T_(s) for s in eyes_ + [thorax, abdomen] + rings + wings + veins]
    df = hide(df[:3], T_(thorax)) + df[2:]
    water = [wave(-3.4, -0.6, -2.0, 0.05, 3, 40), wave(1.0, 3.4, -2.0, 0.05, 3, 40), wave(-2.4, 2.2, -2.6, 0.05, 4, 50)]
    tails = []
    for x, h in [(2.5, 2.2), (2.9, 1.6), (-2.8, 1.6)]:
        tails += [[(x, -2.0), (x + 0.05, -2.0 + h)], rrect(x - 0.15, -2.0 + h - 0.1, x + 0.2, -2.0 + h + 0.7, 0.15), [(x + 0.03, -2.0 + h + 0.7), (x + 0.03, -2.0 + h + 1.0)]]
    reeds = [lens((2.2, -2.0), (1.6, 0.4), 0.06, 16), lens((-2.5, -2.0), (-2.1, 0.2), 0.06, 16)]
    pad = [poly(*[(0.2 + 0.9 * math.cos(t), -2.25 + 0.3 * math.sin(t)) for t in [math.radians(15) + math.radians(330) * i / 30 for i in range(31)]], (0.2, -2.25))]
    return make("Dragonfly over the Pond", df + water + tails + reeds + pad)


@design("spring_frog_lily_pad", T)
def frog_lily_pad(rng):
    pad = poly(*[(0.0 + 2.8 * math.cos(t), -1.9 + 0.85 * math.sin(t)) for t in [math.radians(-75) + math.radians(330) * i / 60 for i in range(61)]], (0.2, -2.0))
    body = smooth([(-1.0, 0.6), (-1.4, -0.3), (-1.3, -1.4), (0.0, -1.8), (1.3, -1.4), (1.4, -0.3), (1.0, 0.6)], 8)
    head = smooth([(-1.0, 0.6), (-1.5, 1.0), (-1.3, 1.5), (-0.9, 1.75), (-0.5, 1.6), (0.0, 1.55), (0.5, 1.6), (0.9, 1.75), (1.3, 1.5), (1.5, 1.0), (1.0, 0.6)], 6)
    eyes_ = [circle(-0.8, 1.6, 0.42, 30), circle(0.8, 1.6, 0.42, 30)]
    head = hide([head], *eyes_)
    mouth = quad((-1.2, 0.95), (0, 0.55), (1.2, 0.95), 16)
    back_legs = [smooth([(-1.3, -0.6), (-2.2, -0.8), (-2.3, -1.5), (-1.6, -1.8), (-1.1, -1.6)], 6), smooth([(1.3, -0.6), (2.2, -0.8), (2.3, -1.5), (1.6, -1.8), (1.1, -1.6)], 6)]
    feet = [poly((-1.6, -1.8), (-2.3, -2.1), (-1.9, -2.05), (-2.0, -2.25), (-1.5, -1.95), closed=False), poly((1.6, -1.8), (2.3, -2.1), (1.9, -2.05), (2.0, -2.25), (1.5, -1.95), closed=False)]
    arms = [[(-0.5, 0.2), (-0.6, -1.6)], [(0.5, 0.2), (0.6, -1.6)], [(-0.9, -1.75), (-0.6, -1.6), (-0.3, -1.8)], [(0.9, -1.75), (0.6, -1.6), (0.3, -1.8)]]
    frog = [body] + head + eyes_ + [mouth] + back_legs + feet + arms
    frog = hide(frog[:1], *back_legs) + frog[1:]
    pad = hide([pad], body, *back_legs)
    lily = []
    lc = (2.2, 0.3)
    for k in range(7):
        a = math.pi / 2 + (k - 3) * 0.38
        lily.append(lens((lc[0], lc[1] - 0.2), (lc[0] + 1.0 * math.cos(a), lc[1] - 0.2 + 1.0 * math.sin(a)), 0.25, 12))
    lily_pad2 = [ellipse(2.3, -0.1, 0.9, 0.22, 30)]
    lily_pad2 = hide(lily_pad2, *lily)
    ripples = [ellipse(-2.6, 1.6, 0.5, 0.12, 20), ellipse(-2.6, 1.6, 0.9, 0.22, 30)]
    return make("Frog on a Lily Pad", frog + pad + lily + lily_pad2 + ripples, [eye(-0.8, 1.6, 0.15), eye(0.8, 1.6, 0.15)])


@design("spring_duck_ducklings", T)
def duck_ducklings(rng):
    m, me = duck(-0.8, 0.3, 0.95)
    hints = [me]
    out = list(m)
    for x, y in [(1.6, 0.45), (2.7, -0.75), (0.7, -1.7)]:
        d, de = duck(x, y, 0.4)
        out += d
        hints.append(de)
    ripples = [[(-3.2, 0.25), (-2.2, 0.25)], [(-0.3, 0.05), (1.0, 0.05)], quad((0.9, 0.42), (1.6, 0.3), (2.4, 0.42), 8), quad((2.0, -0.78), (2.7, -0.9), (3.4, -0.78), 8),
               quad((0.0, -1.72), (0.7, -1.84), (1.4, -1.72), 8), wave(-3.2, -0.6, -1.2, 0.05, 3, 40), wave(-2.6, 3.2, -2.6, 0.05, 5, 60)]
    reeds = [[(-3.0, 0.25), (-3.1, 2.4)], [(-2.8, 0.25), (-2.6, 2.0)], rrect(-3.25, 1.8, -2.95, 2.6, 0.15)]
    reeds = hide(reeds, *[o for o in out if len(o) > 40])
    return make("Mother Duck and Ducklings", out + ripples + reeds, hints)


@design("spring_meadow_lamb", T)
def lamb(rng):
    body = bumpy(0.5, -0.2, 1.9, 1.15, 16, 0.12)
    head = ellipse(-1.6, 0.55, 0.55, 0.75, 40, rot=0.5)
    tuft = bumpy(-1.35, 1.2, 0.5, 0.32, 6, 0.25)
    ears = [lens((-1.75, 1.05), (-2.6, 0.85), 0.35), lens((-1.15, 1.0), (-0.45, 1.25), 0.35)]
    body_v = hide([body], head + [head[0]], tuft + [tuft[0]])
    ears = hide(ears, tuft + [tuft[0]], head)
    legs = [leg(x - 0.17, x + 0.17, -0.9, -2.5) for x in (-0.7, -0.2, 1.2, 1.7)]
    legs = hide(legs, body)
    nose = [quad((-2.1, 0.0), (-2.0, -0.1), (-1.85, 0.0), 6)]
    tail = bumpy(2.5, 0.2, 0.3, 0.25, 5, 0.25)
    tail = hide([tail], body)
    flowers = daisy(-2.6, -2.2, 0.4, 9) + daisy(2.8, -2.0, 0.35, 9) + [[(-2.6, -2.4), (-2.6, -2.7)], [(2.8, -2.3), (2.8, -2.7)]]
    ground = [grass(-3.2, 3.2, -2.7, 0.25, 20)]
    bf = [lens((2.2, 2.0), (1.7, 2.5), 0.6), lens((2.2, 2.0), (2.7, 2.5), 0.6), [(2.2, 1.9), (2.2, 2.3)]]
    return make("Little Lamb in the Meadow", body_v + [head, tuft] + ears + legs + nose + tail + flowers + ground + bf, [eye(-1.55, 0.6, 0.09)])


@design("spring_foal", T)
def foal(rng):
    body = poly((2.35, 1.55), (2.3, 1.25), (2.0, 1.2), (1.6, 1.45), (1.45, 1.2), (1.15, 0.5), (1.0, 0.0), (1.05, -0.3), (1.0, -1.2), (1.05, -2.55),
                (0.8, -2.55), (0.8, -1.2), (0.75, -0.3), (0.6, -0.35), (-0.6, -0.35), (-0.7, -0.4), (-0.65, -1.2), (-0.75, -2.55), (-1.0, -2.55),
                (-0.95, -1.25), (-1.05, -0.5), (-1.25, 0.0), (-1.3, 0.45), (-1.1, 0.7), (0.2, 0.65), (0.7, 0.8), (1.2, 1.6), (1.5, 2.0),
                (1.45, 2.45), (1.72, 2.12), (1.9, 1.98), (2.3, 1.7))
    far = [[(0.6, -0.35), (0.5, -1.25), (0.45, -2.5), (0.25, -2.5), (0.3, -1.25), (0.4, -0.35)],
           [(-0.45, -0.35), (-0.35, -1.25), (-0.4, -2.5), (-0.2, -2.5), (-0.15, -1.25), (-0.2, -0.35)]]
    mane = [poly(*[(0.75 + 0.75 * t + (0.08 if i % 2 else -0.05), 0.85 + 1.15 * t + (0.12 if i % 2 else 0)) for i, t in enumerate([k / 8 for k in range(9)])], closed=False)]
    tail = [quad((-1.25, 0.4), (-1.8, 0.1), (-1.7, -0.8), 10), quad((-1.25, 0.3), (-1.6, -0.1), (-1.45, -0.7), 10)]
    hooves = [[(0.8, -2.35), (1.05, -2.35)], [(-1.0, -2.35), (-0.75, -2.35)]]
    fence = [[(-3.4, 0.6), (3.4, 0.6)], [(-3.4, -0.2), (3.4, -0.2)]] + [[(x, -2.6), (x, 1.0)] for x in (-3.0, 2.9)]
    outl = body
    fence = hide(fence, outl, *[f + [f[0]] for f in far])
    ground = [[(-3.4, -2.6), (3.4, -2.6)]]
    fl = daisy(-2.2, -2.1, 0.35, 8) + daisy(2.3, -2.2, 0.3, 8) + [[(-2.2, -2.3), (-2.2, -2.6)], [(2.3, -2.4), (2.3, -2.6)]]
    return make("Spring Foal", [body] + far + mane + tail + hooves + fence + ground + fl, [eye(1.92, 1.68, 0.08)])


@design("spring_bunny_dandelions", T)
def bunny_dandelions(rng):
    body = ellipse(0.4, -0.9, 1.45, 1.35, 70)
    head = circle(-0.95, 0.75, 0.78, 50)
    ears = [lens((-0.75, 1.4), (-0.05, 3.2), 0.18, 24), lens((-1.05, 1.45), (-0.9, 3.35), 0.18, 24)]
    inner = [lens((-0.65, 1.7), (-0.15, 2.9), 0.12, 16)]
    ears = hide([ears[1]], ears[0]) + [ears[0]]
    body_v = hide([body], head)
    ears = hide(ears, head)
    tail = bumpy(1.9, -0.9, 0.38, 0.38, 7, 0.25)
    tail = hide([tail], body)
    paw = ellipse(-0.6, -2.05, 0.4, 0.2, 20)
    foot = ellipse(0.6, -2.1, 0.9, 0.22, 30)
    haunch = arc(0.9, -1.0, 0.85, math.radians(60), math.radians(200), 20)
    nose = [ellipse(-1.68, 0.6, 0.1, 0.07, 10), quad((-1.65, 0.5), (-1.5, 0.35), (-1.35, 0.42), 6)]
    whisk = [[(-1.6, 0.55), (-2.3, 0.75)], [(-1.6, 0.5), (-2.3, 0.4)]]
    dand = [circle(2.4, 1.6, 0.6, 40)] + [[(2.4, 1.6), (2.4 + 0.55 * math.cos(a), 1.6 + 0.55 * math.sin(a))] for a in [k * TAU / 12 for k in range(12)]]
    dand += [[(2.4, 1.0), (2.5, -2.4)]]
    seeds = [[(x, y), (x + 0.2, y + 0.2)] for x, y in [(1.4, 2.6), (0.9, 3.0)]]
    flower = daisy(-2.5, -1.4, 0.45, 14) + [[(-2.5, -1.6), (-2.5, -2.4)]]
    ground = [grass(-3.2, 3.2, -2.4, 0.35, 20)]
    return make("Bunny and Dandelions", body_v + [head, paw, foot, haunch] + tail + ears + inner + nose + whisk + dand + seeds + flower + ground,
                [eye(-1.15, 0.95, 0.1)])


@design("spring_snail_rain", T)
def snail_rain(rng):
    shell = circle(0.4, 0.2, 1.35, 70)
    sp = spiral(0.5, 0.15, 0.1, 1.05, 2.3, 120)
    foot = smooth([(2.6, -1.3), (1.6, -1.0), (0.4, -1.1), (-0.9, -1.05), (-1.5, -0.6), (-1.75, 0.2), (-2.1, 0.45), (-2.5, 0.2), (-2.5, -0.5),
                   (-2.2, -1.2), (-1.4, -1.45), (0.5, -1.45), (2.6, -1.3)], 6)
    foot = hide([foot], shell)
    stalks = [quad((-2.1, 0.4), (-2.2, 0.9), (-2.0, 1.4), 8), quad((-2.35, 0.3), (-2.7, 0.8), (-2.85, 1.25), 8), circle(-2.0, 1.5, 0.1, 8), circle(-2.88, 1.35, 0.1, 8)]
    smile = arc(-2.15, -0.15, 0.2, math.radians(200), math.radians(320), 6)
    mush = [chain(arc(2.5, 0.3, 0.75, 0, math.pi, 20), quad((1.75, 0.3), (2.5, 0.05), (3.25, 0.3), 10)), [(2.3, 0.15), (2.3, -1.25)], [(2.7, 0.15), (2.7, -1.3)]]
    mush = hide(mush, shell)
    ground = [[(-3.2, -1.45), (3.4, -1.45)]]
    drops = [lens((x, y), (x, y - 0.45), 0.4) for x, y in [(-2.6, 2.8), (-1.2, 2.4), (0.2, 3.0), (1.6, 2.6), (2.8, 2.2), (-3.0, -2.0), (1.0, -2.3)]]
    grass_ = [grass(-3.2, -1.0, -1.45, 0.3, 8), grass(1.4, 3.4, -1.45, 0.3, 7)]
    puddle = [ellipse(-0.5, -2.4, 1.6, 0.25, 50)]
    return make("Snail after the Rain", [shell, sp] + foot + stalks + [smile] + mush + ground + drops + grass_ + puddle)


@design("spring_resting_fawn", T)
def resting_fawn(rng):
    body = smooth([(-1.1, -0.3), (-0.6, 0.3), (0.4, 0.45), (1.6, 0.3), (2.35, -0.2), (2.45, -0.9), (1.9, -1.4), (0.0, -1.5), (-1.4, -1.45), (-1.6, -0.9), (-1.1, -0.3)], 6)
    neck = [quad((-0.55, 0.25), (-0.8, 0.9), (-1.25, 1.5), 8), quad((-1.15, -0.35), (-1.5, 0.4), (-1.75, 1.1), 8)]
    head = smooth([(-1.15, 1.55), (-1.45, 2.05), (-1.95, 2.15), (-2.55, 1.75), (-2.85, 1.35), (-2.65, 1.15), (-2.2, 1.1), (-1.7, 1.05), (-1.15, 1.55)], 6)
    ears = [lens((-1.5, 2.05), (-0.8, 2.75), 0.32), lens((-1.75, 2.1), (-1.9, 2.95), 0.3)]
    neck = hide(neck, head + [head[0]])
    body_v = hide([body], head + [head[0]])
    nose = circle(-2.8, 1.32, 0.08, 8)
    front_leg = [smooth([(-0.6, -1.0), (-1.6, -1.25), (-2.3, -1.4), (-2.4, -1.6), (-1.6, -1.6), (-0.4, -1.45)], 5)]
    front_leg = hide(front_leg, body)
    body_v = hide(body_v, front_leg[0] + [front_leg[0][0]]) if front_leg else body_v
    haunch = arc(1.5, -0.6, 0.75, math.radians(40), math.radians(200), 16)
    spots = [ellipse(x, y, 0.15, 0.1, 10) for x, y in [(-0.3, 0.05), (0.3, 0.15), (0.9, 0.1), (1.5, 0.0), (0.0, -0.35), (0.6, -0.3), (1.1, -0.45)]]
    tail = [lens((2.35, -0.2), (2.75, 0.15), 0.4)]
    ground = [grass(-3.2, 3.2, -1.65, 0.35, 22)]
    flowers = daisy(-2.6, -2.3, 0.35, 9) + daisy(2.6, -2.4, 0.3, 9) + [[(-2.6, -2.5), (-2.6, -2.9)], [(2.6, -2.55), (2.6, -2.9)]]
    return make("Spotted Fawn Resting", body_v + neck + [head, nose] + ears + front_leg + [haunch] + spots + tail + ground + flowers, [eye(-1.95, 1.65, 0.09)])


def swallow_flying(x, y, s, rot):
    R = [(0, 1.0), (0.22, 0.85), (0.28, 0.5), (1.0, 0.55), (1.8, 0.25), (2.6, -0.5), (1.6, -0.15), (0.9, -0.1), (0.3, -0.2),
         (0.25, -0.7), (0.65, -2.0), (0.3, -1.4), (0.0, -1.05)]
    pts = R + [(-px, py) for px, py in reversed(R[:-1])]
    out = smooth(pts, 3, closed=True)
    return transform(out, dx=x, dy=y, s=s, rot=rot)
