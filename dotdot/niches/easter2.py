"""Easter niche, part 2 (pictures 9-58)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math
import random

T = "easter"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ------------------------------------------------------------------ occlusion
# hide() removes the parts of strokes that fall inside "cover" shapes, so a
# front object can sit over a back one without lines crossing it; keep() is
# the opposite (clip a pattern to the inside of a shape); union() merges
# overlapping closed shapes into one silhouette.

def _inside(p, pg):
    x, y = p
    c = False
    n = len(pg)
    for i in range(n):
        x1, y1 = pg[i]
        x2, y2 = pg[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def _dense(s, step=0.04):
    out = [s[0]]
    for a, b in zip(s, s[1:]):
        k = max(1, int(math.dist(a, b) / step))
        for i in range(1, k + 1):
            out.append((a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k))
    return out


def _bbox(pg):
    xs = [p[0] for p in pg]
    ys = [p[1] for p in pg]
    return min(xs), min(ys), max(xs), max(ys)


def _clip(strokes, covers, keep_in=False):
    cv = [(c, _bbox(c)) for c in covers if len(c) > 2]

    def gone(p):
        hit = any(b[0] <= p[0] <= b[2] and b[1] <= p[1] <= b[3] and _inside(p, c) for c, b in cv)
        return hit != keep_in

    def edge(a, b):
        for _ in range(14):
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            if gone(m):
                b = m
            else:
                a = m
        return a

    out = []
    for s in strokes:
        if len(s) < 2:
            continue
        closed = math.dist(s[0], s[-1]) < 1e-9
        d = _dense(s)
        fl = [gone(p) for p in d]
        if not any(fl):
            out.append(list(s))
            continue
        segs, cur = [], []
        for i, p in enumerate(d):
            if fl[i]:
                if cur:
                    cur.append(edge(d[i - 1], p))
                    segs.append(cur)
                    cur = []
            else:
                if not cur and i > 0:
                    cur = [edge(p, d[i - 1])]
                cur.append(p)
        if cur:
            segs.append(cur)
        if closed and len(segs) > 1 and not fl[0] and not fl[-1]:
            segs[0] = segs[-1] + segs[0][1:]
            segs.pop()
        out += [g for g in segs if len(g) > 1 and path_len(g) > 0.06]
    return out


def path_len(s):
    return sum(math.dist(a, b) for a, b in zip(s, s[1:]))


def hide(strokes, *covers):
    return _clip(strokes, covers)


def keep(strokes, *covers):
    return _clip(strokes, covers, True)


def join(strokes, tol=0.03):
    segs = [list(s) for s in strokes if len(s) > 1]
    out = []
    while segs:
        cur = segs.pop(0)
        changed = True
        while changed and math.dist(cur[0], cur[-1]) > tol:
            changed = False
            for i, s in enumerate(segs):
                if math.dist(cur[-1], s[0]) < tol:
                    cur = cur + s[1:]
                elif math.dist(cur[-1], s[-1]) < tol:
                    cur = cur + s[::-1][1:]
                elif math.dist(cur[0], s[-1]) < tol:
                    cur = s + cur[1:]
                elif math.dist(cur[0], s[0]) < tol:
                    cur = s[::-1] + cur[1:]
                else:
                    continue
                segs.pop(i)
                changed = True
                break
        if len(cur) > 2 and math.dist(cur[0], cur[-1]) < tol:
            cur[-1] = cur[0]
        out.append(cur)
    return out


def union(*shapes):
    out = []
    for i, s in enumerate(shapes):
        out += hide([s], *[o for j, o in enumerate(shapes) if j != i])
    return join(out)


# ------------------------------------------------------------------ pieces

def egg(cx, cy, w, h=None, rot=0.0, n=110):
    h = 1.3 * w if h is None else h
    pts = [(w * math.cos(t) * (1 - 0.13 * math.sin(t)), h * math.sin(t)) for t in [TAU * i / n for i in range(n + 1)]]
    return transform(pts, cx, cy, rot=rot)


def pattern(E, cx, cy, rot, specs):
    """Bands across an egg (local y), clipped to its outline."""
    out = []
    span = 4.0
    for kind, y, amp, per in specs:
        k = max(2, int(round(2 * span / per)))
        if kind == "zig":
            s = zigzag(-span, span, y, amp, k)
        elif kind == "wave":
            s = wave(-span, span, y, amp, k, 24 * k)
        elif kind == "scallop":
            s = chain(*[arc(-span + per * (j + 0.5), y, per / 2, math.pi, 2 * math.pi, 8) for j in range(k)])
        else:
            s = [(-span, y), (span, y)]
        out.append(transform(s, cx, cy, rot=rot))
    return keep(out, E)


def spots(cx, cy, rot, pts, r=0.12):
    return [transform(circle(x, y, r, 14), cx, cy, rot=rot) for x, y in pts]


def bunny_head(cx, cy, s=1.0, ears=((-0.42, -0.8, 2.5), (0.42, 0.8, 2.5)), face=True, whiskers=True):
    head = ellipse(cx, cy, 1.0 * s, 0.86 * s, 90)
    out, covers = [], [head]
    for bx, tx, ty in ears:
        b = (cx + bx * s, cy + 0.5 * s)
        tip = (cx + tx * s, cy + ty * s)
        e = lens(b, tip, 0.2)
        covers.append(e)
        out += hide([e], head)
        p0 = (b[0] + (tip[0] - b[0]) * 0.3, b[1] + (tip[1] - b[1]) * 0.3)
        p1 = (b[0] + (tip[0] - b[0]) * 0.85, b[1] + (tip[1] - b[1]) * 0.85)
        out.append(lens(p0, p1, 0.12))
    out.append(head)
    hints = []
    if face:
        out.append(poly((cx - 0.15 * s, cy - 0.05 * s), (cx + 0.15 * s, cy - 0.05 * s), (cx, cy - 0.22 * s)))
        out.append(chain(arc(cx - 0.15 * s, cy - 0.3 * s, 0.15 * s, -0.9 * math.pi, 0, 10)[::-1][::-1],
                         [(cx, cy - 0.22 * s)]))
        out.append(arc(cx + 0.15 * s, cy - 0.3 * s, 0.15 * s, math.pi, 1.9 * math.pi, 10))
        if whiskers:
            for sg in (-1, 1):
                out.append([(cx + sg * 0.35 * s, cy - 0.12 * s), (cx + sg * 1.25 * s, cy - 0.0 * s)])
                out.append([(cx + sg * 0.35 * s, cy - 0.22 * s), (cx + sg * 1.2 * s, cy - 0.4 * s)])
        hints = [eye(cx - 0.38 * s, cy + 0.22 * s, 0.12 * s), eye(cx + 0.38 * s, cy + 0.22 * s, 0.12 * s)]
    return out, hints, covers


def flower(cx, cy, r, k=5, rot=0.0):
    c = circle(cx, cy, 0.3 * r, 20)
    petals = [lens((cx, cy), (cx + r * math.cos(a), cy + r * math.sin(a)), 0.32)
              for a in [rot + math.pi / 2 + j * TAU / k for j in range(k)]]
    return hide(petals, c) + [c], petals + [c]


def tulip(cx, cy, s=1.0, rot=0.0):
    cup = chain(cubic((-0.5, 0.55), (-0.68, -0.05), (-0.4, -0.6), (0, -0.6), 16),
                cubic((0, -0.6), (0.4, -0.6), (0.68, -0.05), (0.5, 0.55), 16),
                [(0.25, 0.22), (0, 0.72), (-0.25, 0.22), (-0.5, 0.55)])
    mid = chain(quad((-0.25, 0.22), (-0.22, -0.35), (0, -0.42), 10), quad((0, -0.42), (0.22, -0.35), (0.25, 0.22), 10))
    return [transform(p, cx, cy, s, rot) for p in (cup, mid)], transform(cup, cx, cy, s, rot)


def lily(x, y, s=1.0, rot=0.0):
    """Trumpet lily, base at (x, y), opening along +x: three pointed petals."""
    out = chain([(0, 0.12)], quad((0, 0.12), (0.8, 0.15), (1.4, 0.35), 10), quad((1.4, 0.35), (1.9, 0.6), (2.35, 1.1), 10),
                quad((2.35, 1.1), (2.1, 0.65), (2.08, 0.38), 6), quad((2.08, 0.38), (2.55, 0.35), (2.85, 0.02), 8),
                quad((2.85, 0.02), (2.5, -0.3), (2.08, -0.38), 8), quad((2.08, -0.38), (2.1, -0.65), (2.35, -1.1), 6),
                quad((2.35, -1.1), (1.9, -0.6), (1.4, -0.35), 10), quad((1.4, -0.35), (0.8, -0.15), (0, -0.12), 10), [(0, 0.12)])
    ribs = [quad((1.5, 0.22), (1.95, 0.45), (2.25, 0.95), 8), quad((1.5, -0.22), (1.95, -0.45), (2.25, -0.95), 8)]
    stam = [[(2.2, 0.12), (3.0, 0.5)], [(2.25, -0.08), (3.05, -0.38)]]
    anth = [ellipse(3.08, 0.54, 0.16, 0.08, 10, rot=0.45), ellipse(3.13, -0.42, 0.16, 0.08, 10, rot=-0.45)]
    shape = [transform(p, x, y, s, rot) for p in [out] + ribs + stam + anth]
    return shape, transform(out, x, y, s, rot)


def butterfly(cx, cy, s=1.0, rot=0.0):
    up = chain(cubic((0, 0), (0.3, 1.2), (1.4, 1.35), (1.25, 0.5), 20), quad((1.25, 0.5), (0.9, 0.0), (0, 0), 10))
    lo = chain(cubic((0, 0), (0.9, -0.1), (1.15, -0.9), (0.65, -1.05), 16), quad((0.65, -1.05), (0.15, -0.85), (0, 0), 10))
    body = ellipse(0, -0.1, 0.13, 0.65, 24)
    wings = [up, lo, mirror_x(up), mirror_x(lo)]
    marks = [circle(0.75, 0.75, 0.2, 14), circle(-0.75, 0.75, 0.2, 14), circle(0.55, -0.55, 0.14, 12), circle(-0.55, -0.55, 0.14, 12)]
    ant = [quad((0, 0.5), (0.1, 1.0), (0.4, 1.2), 8), quad((0, 0.5), (-0.1, 1.0), (-0.4, 1.2), 8)]
    parts = hide(wings, body) + [body] + marks + ant
    return [transform(p, cx, cy, s, rot) for p in parts], [transform(w, cx, cy, s, rot) for w in wings + [body]]


def chick(cx, cy, s=1.0, feet=True):
    body = ellipse(cx, cy, 1.0 * s, 0.9 * s, 80)
    head = circle(cx, cy + 1.05 * s, 0.62 * s, 60)
    out = union(body, head)
    wings = [lens((cx - 0.8 * s, cy + 0.1 * s), (cx - 1.45 * s, cy + 0.55 * s), 0.3),
             lens((cx + 0.8 * s, cy + 0.1 * s), (cx + 1.45 * s, cy + 0.55 * s), 0.3)]
    out += hide(wings, body)
    out.append(poly((cx - 0.18 * s, cy + 0.92 * s), (cx, cy + 1.02 * s), (cx + 0.18 * s, cy + 0.92 * s), (cx, cy + 0.68 * s)))
    out += [quad((cx, cy + 1.65 * s), (cx - 0.15 * s, cy + 2.0 * s), (cx + 0.15 * s, cy + 2.05 * s), 8),
            quad((cx + 0.05 * s, cy + 1.65 * s), (cx + 0.25 * s, cy + 1.9 * s), (cx + 0.45 * s, cy + 1.85 * s), 8)]
    if feet:
        for fx in (-0.35, 0.35):
            x0, y0 = cx + fx * s, cy - 0.88 * s
            out.append([(x0 - 0.3 * s, y0 - 0.3 * s), (x0, y0), (x0 + 0.3 * s, y0 - 0.3 * s)])
            out.append([(x0, y0), (x0, y0 - 0.38 * s)])
    hints = [eye(cx - 0.25 * s, cy + 1.15 * s, 0.09 * s), eye(cx + 0.25 * s, cy + 1.15 * s, 0.09 * s)]
    return out, hints, [body, head] + wings


def tuft(x, y, s=1.0):
    return [(x - 0.35 * s, y), (x - 0.25 * s, y + 0.4 * s), (x - 0.12 * s, y + 0.05 * s), (x, y + 0.55 * s),
            (x + 0.12 * s, y + 0.05 * s), (x + 0.27 * s, y + 0.42 * s), (x + 0.35 * s, y)]


def bean(cx, cy, rot=0.0, s=1.0):
    pts = [(0.32 * s * math.cos(t), 0.15 * s * math.sin(t) + 0.12 * s * math.cos(t) ** 2) for t in [TAU * i / 40 for i in range(41)]]
    return transform(pts, cx, cy, rot=rot)


def carrot_shape(x0, y0, x1, y1, w=0.5):
    """Carrot from shoulder (x0, y0) to tip (x1, y1); returns (outline, lines)."""
    L = math.hypot(x1 - x0, y1 - y0)
    a = math.atan2(y1 - y0, x1 - x0)
    body = chain(quad((0, w / 2), (0.55 * L, w * 0.35), (L, 0), 16), quad((L, 0), (0.55 * L, -w * 0.35), (0, -w / 2), 16),
                 arc(0, 0, w / 2, -math.pi / 2, -1.5 * math.pi, 10))
    lines = [[(f * L, w * 0.42 * (1 - f)), (f * L + 0.1, w * 0.1 * (1 - f))] for f in (0.25, 0.5, 0.72)]
    leaves = [lens((-w / 2 + 0.05, 0), (-w / 2 - 0.9 * w * 2, k * w * 1.1), 0.22) for k in (-1, 0, 1)]
    return ([transform(body, x0, y0, rot=a)], [transform(l, x0, y0, rot=a) for l in lines], [transform(l, x0, y0, rot=a) for l in leaves])


# ------------------------------------------------------------------ designs

@design("easter_bunny_hugging_egg", T)
def bunny_hugging_egg(rng):
    hs, hh, hc = bunny_head(0, 1.55, 0.95)
    body = ellipse(0, -0.95, 1.6, 1.55, 120)
    E = egg(0, -1.15, 1.1, 1.4)
    pat = pattern(E, 0, -1.15, 0, [("zig", 0.2, 0.15, 0.4), ("wave", -0.5, 0.1, 0.6)]) + \
        spots(0, -1.15, 0, [(-0.4, 0.75), (0, 0.85), (0.4, 0.75), (-0.5, -0.95), (0, -1.0), (0.5, -0.95)])
    paws = [ellipse(-0.98, -0.55, 0.38, 0.26, 30, rot=-0.5), ellipse(0.98, -0.55, 0.38, 0.26, 30, rot=0.5)]
    feet = hide([ellipse(-1.05, -2.45, 0.65, 0.3, 40), ellipse(1.05, -2.45, 0.65, 0.3, 40)], E)
    out = hide([body], *hc, E, *feet) + hide([E] + pat, *paws) + paws + feet + hs
    return make("Bunny Hugging an Egg", out, hh)


@design("easter_bunny_behind_egg", T)
def bunny_behind_egg(rng):
    E = egg(-0.4, -0.6, 2.0, 2.5)
    pat = pattern(E, -0.4, -0.6, 0, [("zig", 0.9, 0.2, 0.5), ("line", 0.55, 0, 1), ("line", 1.25, 0, 1),
                                      ("scallop", -0.45, 0, 0.6), ("wave", -1.4, 0.15, 0.8)])
    pat += spots(-0.4, -0.6, 0, [(-1.0, 0.1), (-0.3, 0.1), (0.4, 0.1), (1.1, 0.1), (-0.7, 1.8), (0.0, 1.95), (0.7, 1.8)], 0.15)
    hs, hh, hc = bunny_head(1.55, 1.55, 0.85, ears=((-0.42, -0.6, 2.5), (0.42, 0.9, 2.4)))
    paw = ellipse(0.95, 0.75, 0.32, 0.22, 24, rot=0.6)
    out = hide(hs, E) + hide([E] + pat, paw) + [paw] + [tuft(-2.6, -3.1, 1.0), tuft(1.6, -3.1, 0.9), tuft(2.5, -3.1, 1.1)]
    hh = [h for h in hh if not any(_inside(p, E) for p in h)]
    return make("Bunny Peeking Behind a Giant Egg", out, hh)


@design("easter_chocolate_bunny", T)
def chocolate_bunny(rng):
    body = ellipse(0.4, -0.7, 1.35, 1.75, 100)
    head = ellipse(-0.45, 1.25, 0.95, 0.8, 80, rot=0.15)
    haunch = ellipse(0.9, -1.55, 1.2, 0.95, 80)
    tail = circle(2.05, -1.2, 0.38, 30)
    ear1 = lens((-0.25, 1.8), (0.45, 3.9), 0.2)
    ear2 = lens((0.25, 1.75), (1.45, 3.55), 0.2)
    foot = ellipse(-0.35, -2.45, 0.85, 0.28, 50)
    out = union(body, head, haunch, tail, ear2, foot, ear1)
    bite = polar(lambda t: 0.45 + 0.05 * math.sin(9 * t), cx=0.72, cy=3.62, n=120)
    out = hide(out, bite) + keep([bite], ear1)
    out += keep([ellipse(0.9, -1.55, 1.2, 0.95, 80)], body)
    out += [lens((-0.15, 2.2), (0.3, 3.3), 0.12), quad((-0.9, -2.45), (-1.0, -2.3), (-1.15, -2.42), 6),
            quad((-0.65, -2.45), (-0.75, -2.3), (-0.9, -2.42), 6)]
    out.append(ellipse(-0.75, -0.55, 0.28, 0.6, 30, rot=-0.2))
    out.append(poly((-1.38, 1.1), (-1.2, 1.15), (-1.25, 0.98)))
    ribbon = keep([quad((-1.5, 0.75), (-0.3, 0.35), (1.2, 0.75), 20), quad((-1.5, 0.45), (-0.3, 0.05), (1.2, 0.45), 20)], body, head)
    bow = [lens((0.25, 0.35), (-0.35, 0.95), 0.42), lens((0.25, 0.35), (0.9, 0.95), 0.42), circle(0.25, 0.35, 0.14, 12)]
    bow_tails = [poly((0.18, 0.22), (-0.15, -0.5), (0.05, -0.4), (0.22, -0.55), (0.32, 0.22), closed=False)]
    out = out + hide(ribbon, *bow) + hide(bow[:2], bow[2]) + [bow[2]] + hide(bow_tails, *bow)
    shine = [arc(0.4, -0.7, 1.05, 0.2, 0.9, 12)]
    base = hide([ellipse(0.2, -2.75, 2.6, 0.32, 80)], foot, haunch, body)
    return make("Chocolate Bunny with a Bite", out + shine + base, [eye(-0.7, 1.45, 0.11)])


@design("easter_egg_hunt", T)
def egg_hunt(rng):
    ground = [(-3.3, -1.6), (3.3, -1.6)]
    canopy = [circle(-2.7, 1.5, 0.8, 50), circle(-2.0, 2.2, 0.9, 50), circle(-1.2, 1.6, 0.8, 50), circle(-2.0, 1.1, 0.7, 40)]
    tree = union(*canopy)
    trunk = hide([[(-2.45, -1.6), (-2.3, 1.0)], [(-1.75, -1.6), (-1.85, 1.0)]], *canopy)
    hole = ellipse(-2.07, -0.4, 0.28, 0.4, 24)
    egg1 = egg(-2.07, -0.45, 0.18, 0.24)
    bush_c = [circle(1.6, -1.0, 0.75, 40), circle(2.5, -0.9, 0.8, 40), circle(2.05, -0.25, 0.75, 40)]
    bush = hide(union(*bush_c), poly((-4, -1.6), (4, -1.6), (4, -4), (-4, -4)))
    peek = egg(1.0, -1.05, 0.35, 0.47, 0.3)
    peek = hide([peek] + pattern(peek, 1.0, -1.05, 0.3, [("zig", 0.05, 0.08, 0.2)]), *bush_c)
    eggs = []
    for x, y, r, k in [(-0.6, -2.3, 0.3, "zig"), (0.7, -2.6, -0.25, "wave"), (2.4, -2.4, 0.1, "line"), (-2.5, -2.6, -0.2, "wave")]:
        E = egg(x, y, 0.38, 0.5, r)
        eggs.append(E)
        eggs += pattern(E, x, y, r, [(k, 0.0, 0.08, 0.25), ("line", 0.25, 0, 1)])
    grass = [tuft(x, -2.95, 0.9) for x in (-3.0, -1.6, 0.0, 1.6, 3.0)]
    bx = -0.3
    basket = chain([(bx - 0.9, -0.75)], quad((bx - 0.85, -1.6), (bx, -1.6), (bx + 0.85, -1.6), 12), [(bx + 0.9, -0.75), (bx - 0.9, -0.75)])
    handle = arc(bx, -0.75, 0.75, 0, math.pi, 24)
    beggs = hide([egg(bx - 0.4, -0.6, 0.25, 0.32, 0.3), egg(bx + 0.05, -0.5, 0.25, 0.32), egg(bx + 0.45, -0.6, 0.25, 0.32, -0.3)], basket)
    weave = keep([[(bx - 1, -1.0), (bx + 1, -1.0)], [(bx - 1, -1.3), (bx + 1, -1.3)]], basket)
    sun = [circle(1.4, 2.2, 0.55, 40)] + [[(1.4 + 0.75 * math.cos(a), 2.2 + 0.75 * math.sin(a)), (1.4 + 1.05 * math.cos(a), 2.2 + 1.05 * math.sin(a))]
                                         for a in [k * TAU / 10 for k in range(10)]]
    out = tree + trunk + [hole, egg1] + bush + peek + eggs + grass + [basket, handle] + beggs + weave + sun
    out += hide([ground], *bush_c, basket)
    return make("Easter Egg Hunt", out)


@design("easter_egg_in_cup", T)
def egg_in_cup(rng):
    E = egg(0, 0.95, 1.3, 1.7)
    pat = pattern(E, 0, 0.95, 0, [("zig", 0.45, 0.18, 0.45), ("line", 0.75, 0, 1), ("line", 0.15, 0, 1)])
    pat += spots(0, 0.95, 0, [(-0.5, 1.15), (0.0, 1.3), (0.5, 1.15), (-0.25, 1.65), (0.25, 1.65)], 0.13)
    cup = chain(cubic((-1.5, 0.3), (-1.5, -1.0), (-0.6, -1.4), (-0.3, -1.45), 20), [(-0.3, -1.9)],
                quad((-0.3, -1.9), (-1.4, -2.0), (-1.5, -2.5), 12), [(1.5, -2.5)], quad((1.5, -2.5), (1.4, -2.0), (0.3, -1.9), 12),
                [(0.3, -1.45)], cubic((0.3, -1.45), (0.6, -1.4), (1.5, -1.0), (1.5, 0.3), 20), [(-1.5, 0.3)])
    deco = keep([wave(-1.8, 1.8, -0.35, 0.12, 4, 80), [(-1.8, 0.0), (1.8, 0.0)]], cup)
    hearts = [circle(x, -0.85, 0.12, 12) for x in (-0.6, 0.0, 0.6)]
    spoon = [tube([(2.0, -2.5), (2.6, 0.4)], 0.22), ellipse(2.7, 1.05, 0.35, 0.6, 30, rot=-0.2)]
    spoon = hide(spoon[:1], spoon[1]) + spoon[1:]
    return make("Egg in an Egg Cup", hide([E] + pat, cup) + [cup] + deco + hearts + spoon)


@design("easter_jeweled_egg", T)
def jeweled_egg(rng):
    E = egg(0, 0.9, 1.3, 1.75)
    bands = pattern(E, 0, 0.9, 0, [("line", 0.65, 0, 1), ("line", 0.4, 0, 1), ("line", -0.4, 0, 1), ("line", -0.65, 0, 1)])
    lattice = []
    for k in range(-4, 5):
        lattice += [[(0.45 * k - 1.0, -0.4 + 0.9), (0.45 * k + 1.0, 0.4 + 0.9)], [(0.45 * k + 1.0, -0.4 + 0.9), (0.45 * k - 1.0, 0.4 + 0.9)]]
    band_reg = poly((-3, 0.9 - 0.4), (3, 0.9 - 0.4), (3, 1.3), (-3, 1.3))
    lattice = keep(keep(lattice, band_reg), E)
    jewels = [circle(x, 0.9 + 0.525, 0.09, 10) for x in (-0.8, -0.4, 0.0, 0.4, 0.8)] + [circle(x, 0.9 - 0.525, 0.09, 10) for x in (-0.8, -0.4, 0.0, 0.4, 0.8)]
    swirls = keep([arc(x, 2.0, 0.35, math.pi, 2 * math.pi, 12) for x in (-0.7, 0.0, 0.7)] +
                  [arc(x, -0.2, 0.35, 0, math.pi, 12) for x in (-0.7, 0.0, 0.7)], E)
    gem = [poly((0, 2.25), (0.2, 1.95), (0, 1.65), (-0.2, 1.95)), poly((0, -0.05), (0.2, -0.35), (0, -0.65), (-0.2, -0.35))]
    finial = [circle(0, 2.85, 0.2, 18), star(0, 3.35, 0.32, 5, 0.45)]
    cupw = chain(arc(0, -0.75, 0.75, math.radians(200), math.radians(340), 20))
    cupw = [chain(cupw, [(0.4, -1.25), (-0.4, -1.25), cupw[0]])]
    stem = [poly((-0.25, -1.25), (-0.15, -1.9), (0.15, -1.9), (0.25, -1.25), closed=False)]
    legs = [tube(cubic((-0.15, -1.9), (-0.6, -1.9), (-1.2, -2.1), (-1.5, -2.6), 16), 0.18),
            tube(cubic((0.15, -1.9), (0.6, -1.9), (1.2, -2.1), (1.5, -2.6), 16), 0.18)]
    base = ellipse(0, -2.75, 2.0, 0.3, 80)
    out = hide([E] + bands + lattice + jewels + swirls + gem, *cupw) + cupw + stem + hide(legs, base) + [base] + finial
    return make("Jeweled Egg on a Stand", out)


@design("easter_jelly_bean_egg", T)
def jelly_bean_egg(rng):
    w, h = 1.6, 2.0
    lower = [(w * math.cos(t) * (1 - 0.13 * math.sin(t)), h * math.sin(t)) for t in [-math.pi * i / 60 for i in range(61)]]
    shell = chain(zigzag(-w, w, 0.0, 0.18, 7), [(w, 0.0)], lower, [(-w, 0.0)])
    shell = transform(shell, -0.6, -1.0)
    beans = []
    R = random.Random(3)
    for (x, y) in [(-1.6, -0.6), (-1.0, -0.4), (-0.4, -0.35), (0.2, -0.45), (0.7, -0.6), (-1.3, 0.0), (-0.7, 0.15),
                   (-0.1, 0.1), (0.4, -0.05), (-1.0, 0.6), (-0.35, 0.6), (-0.65, 1.05)]:
        beans.append(bean(x, y, R.uniform(-1.2, 1.2)))
    beans = hide(beans, shell)
    top = transform(chain(zigzag(-w, w, 0.0, 0.18, 7)[::-1], [(-w, 0.0)],
                          [(w * math.cos(t) * (1 - 0.13 * math.sin(t)), 0.75 * h * math.sin(t)) for t in [math.pi - math.pi * i / 60 for i in range(61)]]),
                    1.9, 1.2, s=0.75, rot=-0.5)
    loose = [bean(1.4, -2.7, 0.6), bean(2.2, -2.4, -0.9), bean(2.6, -1.6, 0.3), bean(-2.6, -2.8, 1.0)]
    stripes = keep([transform(wave(-3, 3, y, 0.1, 6, 120), -0.6, -1.0) for y in (-0.6, -1.2)], shell)
    dots = [circle(x, -2.45, 0.13, 12) for x in (-1.1, -0.6, -0.1)]
    return make("Egg Full of Jelly Beans", [shell] + beans + [top] + loose + stripes + dots + [[(-3.0, -3.1), (3.0, -3.1)]])


@design("easter_duckling", T)
def duckling(rng):
    body = ellipse(0.3, -0.6, 1.7, 1.15, 100)
    tail = ellipse(1.85, 0.0, 0.6, 0.25, 30, rot=0.7)
    head = circle(-1.0, 1.05, 0.85, 70)
    out = union(body, tail, head)
    bill = ellipse(-2.0, 0.85, 0.55, 0.22, 30, rot=-0.08)
    out = hide(out, bill) + [bill, [(-2.5, 0.83), (-1.75, 0.82)]]
    out += [quad((-1.0, 1.85), (-1.15, 2.3), (-0.8, 2.4), 8), quad((-0.85, 1.85), (-0.6, 2.2), (-0.35, 2.15), 8)]
    wing = chain(cubic((-0.2, -0.2), (0.4, 0.6), (1.3, 0.3), (1.65, -0.3), 20), cubic((1.65, -0.3), (1.0, -0.65), (0.3, -0.7), (-0.2, -0.2), 20))
    out += [wing, quad((1.0, -0.4), (1.3, -0.25), (1.6, -0.3), 6), quad((0.7, -0.5), (1.1, -0.45), (1.4, -0.5), 6)]
    for x in (-0.1, 0.7):
        out.append([(x, -1.68), (x, -2.35)])
        out.append(poly((x, -2.35), (x - 0.75, -2.5), (x - 0.6, -2.65), (x - 0.35, -2.55), (x - 0.2, -2.68), (x + 0.15, -2.5)))
    E = egg(2.3, -1.9, 0.5, 0.65, -0.2)
    out += [E] + pattern(E, 2.3, -1.9, -0.2, [("zig", 0.1, 0.12, 0.3), ("line", -0.25, 0, 1)])
    fl, _ = flower(-2.3, -1.6, 0.5)
    out += fl + [[(-2.3, -1.75), (-2.3, -2.7)], tuft(-1.5, -2.8, 0.7), tuft(1.3, -2.8, 0.7)]
    return make("Fluffy Duckling", out, [eye(-1.2, 1.25, 0.11)])


@design("easter_chicks_in_nest", T)
def chicks_in_nest(rng):
    nest = chain(cubic((-3.0, -0.2), (-2.6, -2.8), (2.6, -2.8), (3.0, -0.2), 40), wave(3.0, -3.0, -0.2, 0.1, 9, 120))
    out, hints, covers = [], [], []
    for x, y, r in [(0, 0.75, 0.95), (-1.65, 0.25, 0.85), (1.65, 0.25, 0.85)]:
        head = circle(x, y, r, 70)
        parts = [head, poly((x - 0.28, y - 0.05), (x + 0.28, y - 0.05), (x, y + 0.22)), poly((x - 0.22, y - 0.18), (x + 0.22, y - 0.18), (x, y - 0.5)),
                 quad((x, y + r - 0.05), (x - 0.2, y + r + 0.35), (x + 0.15, y + r + 0.4), 8),
                 quad((x + 0.05, y + r - 0.05), (x + 0.3, y + r + 0.25), (x + 0.5, y + r + 0.2), 8)]
        wings = [lens((x - 0.7 * r, y - 0.55 * r), (x - 1.25 * r, y - 0.05 * r), 0.3), lens((x + 0.7 * r, y - 0.55 * r), (x + 1.25 * r, y - 0.05 * r), 0.3)]
        parts += hide(wings, head)
        out = hide(out, head, *wings) + parts
        hints += [eye(x - 0.32 * r, y + 0.35 * r, 0.1), eye(x + 0.32 * r, y + 0.35 * r, 0.1)]
    twigs = keep([quad((-3, -0.6 - 0.45 * k), (0, -1.0 - 0.45 * k + 0.2 * (k % 2)), (3, -0.5 - 0.45 * k), 20) for k in range(4)] +
                 [[(-2.4 + 0.9 * k, -0.4), (-2.0 + 0.9 * k, -2.3)] for k in range(6)], nest)
    out = hide(out, nest) + [nest] + twigs
    return make("Three Chicks in a Nest", out, hints)


@design("easter_tulip_pot", T)
def tulip_pot(rng):
    out, covers = [], []
    for x, y, r in [(-1.15, 1.5, 0.3), (0.0, 2.3, 0.0), (1.15, 1.45, -0.3)]:
        sh, c = tulip(x, y, 1.0, r)
        covers.append(c)
        out += sh
        bx, by = x + 0.6 * math.sin(r), y - 0.6 * math.cos(r)
        out.append(quad((bx, by), (bx * 0.4, (by - 0.6) / 2), (x * 0.25, -0.6), 14))
    leaves = [lens((-0.3, -0.6), (-2.3, 0.6), 0.18), lens((0.3, -0.6), (2.3, 0.5), 0.18), lens((-0.1, -0.6), (-0.9, 1.0), 0.15)]
    out = hide(out, *leaves) + leaves
    rim = rect(-1.5, -1.0, 1.5, -0.45)
    pot = poly((-1.3, -1.0), (1.3, -1.0), (1.0, -2.9), (-1.0, -2.9))
    out = hide(out, rim, pot) + [rim, pot]
    E = egg(0, -1.95, 0.42, 0.55)
    out += [E] + pattern(E, 0, -1.95, 0, [("zig", 0.0, 0.1, 0.22)])
    out += [heart(-0.75, -1.9, 0.18), heart(0.75, -1.9, 0.18)]
    return make("Tulips in a Flower Pot", out)


@design("easter_lilies", T)
def easter_lilies(rng):
    out, covers = [], []
    for x, y, r in [(-0.45, -0.2, 2.35), (0.45, -0.4, 0.75), (0.0, 0.25, math.pi / 2 + 0.05)]:
        sh, c = lily(x, y, 1.0, r)
        out = hide(out, c) + sh
        covers.append(c)
    stems = [quad((-0.45, -0.2), (-0.3, -1.5), (-0.1, -2.9), 14), quad((0.45, -0.4), (0.25, -1.5), (0.1, -2.9), 14),
             quad((0.0, 0.25), (0.05, -1.3), (0.0, -2.9), 14)]
    bud = [lens((0.05, -1.1), (1.6, -0.2), 0.16)]
    leaves = [lens((-0.1, -2.2), (-2.4, -1.0), 0.14), lens((0.1, -2.4), (2.3, -1.5), 0.14), lens((-0.05, -1.5), (-1.7, 0.0), 0.12)]
    bow = [lens((0.0, -2.0), (-0.85, -1.6), 0.42), lens((0.0, -2.0), (0.85, -1.6), 0.42), circle(0, -2.0, 0.13, 12)]
    tails = [poly((-0.08, -2.1), (-0.5, -2.85), (-0.22, -2.8), closed=False), poly((0.08, -2.1), (0.5, -2.85), (0.22, -2.8), closed=False)]
    out += hide(stems + bud, *covers, *leaves, *bow) + hide(leaves, *covers, *bow) + hide(bow[:2], bow[2]) + [bow[2]] + hide(tails, *bow)
    return make("Easter Lily Bouquet", out)


@design("easter_egg_wreath", T)
def egg_wreath(rng):
    ring = [circle(0, 0, 2.4, 160), circle(0, 0, 1.45, 120)]
    vines = [arc(0, 0, r, a, a + 1.1, 24) for r, a0 in [(1.7, 0.2), (1.95, 0.8), (2.2, 0.4)] for a in [a0 + k * TAU / 4 for k in range(4)]]
    covers, items = [], []
    for k, a in enumerate([90, 30, 150, -15, 195]):
        ar = math.radians(a)
        x, y = 1.95 * math.cos(ar), 1.95 * math.sin(ar)
        E = egg(x, y, 0.45, 0.6, ar - math.pi / 2)
        kind = ["zig", "wave", "line", "zig", "wave"][k]
        items += [E] + pattern(E, x, y, ar - math.pi / 2, [(kind, 0.05, 0.1, 0.25), ("line", 0.3, 0, 1)])
        covers.append(E)
    for a in [60, 120, 0, 180, 255, 285]:
        ar = math.radians(a)
        f, c = flower(1.95 * math.cos(ar), 1.95 * math.sin(ar), 0.42, 5, ar)
        items += f
        covers += c
    bow = [lens((0, -2.2), (-1.0, -1.7), 0.42), lens((0, -2.2), (1.0, -1.7), 0.42), circle(0, -2.2, 0.17, 14)]
    tails = [poly((-0.1, -2.35), (-0.7, -3.3), (-0.3, -3.2), (0.0, -2.4), closed=False), poly((0.1, -2.35), (0.7, -3.3), (0.3, -3.2), (0.0, -2.4), closed=False)]
    out = hide(ring + vines, *covers, *bow) + hide(items, *bow) + hide(bow[:2], bow[2]) + [bow[2]] + hide(tails, *bow)
    return make("Easter Egg Wreath", out)


@design("easter_wheelbarrow", T)
def wheelbarrow(rng):
    tub = poly((-2.3, 0.0), (1.6, 0.0), (1.1, -1.3), (-1.7, -1.3))
    wheel = [circle(1.75, -1.75, 0.8, 70), circle(1.75, -1.75, 0.18, 14)]
    spokes = [[(1.75 + 0.18 * math.cos(a), -1.75 + 0.18 * math.sin(a)), (1.75 + 0.8 * math.cos(a), -1.75 + 0.8 * math.sin(a))] for a in [k * TAU / 8 for k in range(8)]]
    handle = tube([(1.75, -1.75), (-1.0, -0.8), (-3.2, -0.15)], 0.16)
    legs = [tube([(-1.1, -1.0), (-1.3, -2.5)], 0.16), [(-1.6, -2.55), (-1.0, -2.55)]]
    planks = keep([[(-3, -0.45), (3, -0.45)], [(-3, -0.9), (3, -0.9)]], tub)
    eggs = []
    covers = [tub]
    spots_ = [(-1.7, 0.25, 0.3), (-0.95, 0.15, -0.2), (-0.2, 0.2, 0.15), (0.6, 0.15, -0.3), (1.2, 0.25, 0.2),
              (-1.3, 0.85, -0.25), (-0.55, 0.95, 0.2), (0.25, 0.9, -0.1), (0.95, 0.85, 0.35), (-0.15, 1.55, 0.0)]
    kinds = ["zig", "wave", "line", "zig", "wave"]
    for k, (x, y, r) in enumerate(spots_[::-1]):
        E = egg(x, y, 0.38, 0.5, r)
        new = [E] + pattern(E, x, y, r, [(kinds[k % 5], 0.05, 0.08, 0.22)])
        eggs = hide(eggs, E) + new
    eggs = hide(eggs, tub)
    out = [tub] + planks + hide(wheel + spokes, tub) + hide([handle], tub, wheel[0]) + hide(legs, tub) + eggs
    out += hide([[(-3.2, -2.55), (3.2, -2.55)]], wheel[0])
    return make("Wheelbarrow Full of Eggs", out)


@design("easter_lamb_flower_crown", T)
def lamb_flower_crown(rng):
    wool = polar(lambda t: 2.25 + 0.12 * math.sin(15 * t), cx=0, cy=-0.35, n=400)
    wool = [(x, -0.35 + (y + 0.35) * 0.95) for x, y in wool]
    face = chain(cubic((-0.95, 1.0), (-1.1, -0.6), (-0.6, -1.6), (0, -1.6), 20), cubic((0, -1.6), (0.6, -1.6), (1.1, -0.6), (0.95, 1.0), 20),
                 quad((0.95, 1.0), (0, 1.5), (-0.95, 1.0), 16))
    ears = [lens((-0.9, 0.6), (-2.6, 0.2), 0.3), lens((0.9, 0.6), (2.6, 0.2), 0.3)]
    inner = [lens((-1.15, 0.52), (-2.35, 0.25), 0.15), lens((1.15, 0.52), (2.35, 0.25), 0.15)]
    covers, crown = [], []
    for k in range(7):
        a = math.radians(160 - 140 * k / 6)
        x, y = 1.25 * math.cos(a), 0.6 + 1.0 * math.sin(a)
        f, c = flower(x, y, 0.42 if k % 2 == 0 else 0.34, 5, a)
        crown = hide(crown, *c) + f
        covers += c
    leaves = []
    nose = [chain(quad((-0.35, -0.9), (0, -1.15), (0.35, -0.9), 8)), [(0, -1.12), (0, -1.3)], arc(-0.15, -1.3, 0.15, 0, -math.pi * 0.9, 8),
            arc(0.15, -1.3, 0.15, math.pi, 1.9 * math.pi, 8)]
    nostrils = [ellipse(-0.18, -0.8, 0.1, 0.06, 8), ellipse(0.18, -0.8, 0.1, 0.06, 8)]
    out = hide([wool], face, *ears, *covers) + hide(ears + inner, face, *covers) + hide([face], *covers) + crown + leaves + nose + nostrils
    return make("Lamb with a Flower Crown", out, [eye(-0.42, -0.05, 0.13), eye(0.42, -0.05, 0.13)])


@design("easter_dye_cups", T)
def dye_cups(rng):
    out = []
    covers = []
    for k, x in enumerate((-2.1, 0.0, 2.1)):
        cup = rrect(x - 0.85, -2.7, x + 0.85, -0.6, 0.2)
        handle = [arc(x + 0.85, -1.55, 0.45, -1.4, 1.4, 16), arc(x + 0.85, -1.55, 0.25, -1.3, 1.3, 12)]
        liquid = keep([wave(x - 1, x + 1, -0.95, 0.06, 3, 40)], cup)
        out += [cup] + handle + liquid
        covers.append(cup)
    E1 = egg(-2.1, -0.6, 0.48, 0.62, 0.15)
    wire = [arc(-2.1, -0.6, 0.6, math.radians(200), math.radians(340), 16), [(-1.55, -0.85), (-0.9, 0.6)], circle(-0.82, 0.78, 0.18, 12)]
    out += hide([E1] + pattern(E1, -2.1, -0.6, 0.15, [("zig", 0.15, 0.1, 0.25)]) + wire, covers[0])
    E2 = egg(0, 0.15, 0.5, 0.65)
    spoon = [arc(0, 0.15, 0.65, math.radians(195), math.radians(345), 16), [(0.62, -0.02), (1.0, -1.0)]]
    out += [E2] + pattern(E2, 0, 0.15, 0, [("line", 0.15, 0, 1), ("line", -0.15, 0, 1)]) + hide(spoon, covers[1])
    out += [poly((0.0, -0.6), (-0.08, -0.4), (0.0, -0.3), (0.08, -0.4)), poly((0.2, -0.55), (0.14, -0.38), (0.2, -0.3), (0.26, -0.38))]
    rack = [rrect(-2.8, 1.7, 2.8, 1.95, 0.1)]
    for x, kind in [(-1.9, "wave"), (-0.65, "zig"), (0.65, "scallop"), (1.9, "zig")]:
        E = egg(x, 2.55, 0.42, 0.56)
        rack += hide([E] + pattern(E, x, 2.55, 0, [(kind, 0.0, 0.1, 0.25), ("line", 0.3, 0, 1)]), rack[0])
    bubbles = [circle(2.0, -0.4, 0.12, 10), circle(2.3, -0.2, 0.15, 12), circle(1.85, -0.1, 0.1, 10)]
    return make("Egg Dyeing Cups", out + rack + bubbles)


@design("easter_hot_cross_buns", T)
def hot_cross_buns(rng):
    def bun(cx, cy, r):
        o = chain(arc(cx, cy, r, 0, math.pi, 40), quad((cx - r, cy), (cx, cy - 0.3 * r), (cx + r, cy), 14))
        o = [(x, cy + (y - cy) * 0.8) if y > cy else (x, y) for x, y in o]
        icing_h = tube(quad((cx - r, cy + 0.32 * r), (cx, cy + 0.6 * r), (cx + r, cy + 0.32 * r), 16), 0.16)
        icing_v = tube(quad((cx - 0.05 * r, cy - 0.1 * r), (cx - 0.08 * r, cy + 0.5 * r), (cx, cy + 0.8 * r), 12), 0.16)
        ic = keep(hide([icing_v], icing_h) + [icing_h], o)
        return [o] + ic, o
    plate = [ellipse(0, -1.7, 3.2, 1.05, 140), ellipse(0, -1.7, 2.6, 0.75, 120)]
    a, ca = bun(-1.25, -1.1, 1.05)
    b, cb = bun(1.25, -1.1, 1.05)
    c, cc = bun(0.0, -1.85, 1.2)
    d, cd = bun(0.0, -0.45, 0.95)
    out = hide(d, ca, cb, cc) + hide(a, cc) + hide(b, cc) + c
    out = hide(plate, ca, cb, cc, cd) + out
    steam = [[(x + 0.15 * math.sin(4 * t), 0.6 + t * 1.6) for t in [i / 20 for i in range(21)]] for x in (-1.2, 0.0, 1.2)]
    steam = hide(steam, cd)
    return make("Hot Cross Buns", out + steam)


@design("easter_layer_cake", T)
def layer_cake(rng):
    top = ellipse(0, 0.6, 2.0, 0.45, 100)
    sides = [[(-2.0, 0.6), (-2.0, -1.6)], [(2.0, 0.6), (2.0, -1.6)], arc(0, -1.6, 2.0, math.pi, 2 * math.pi, 50)]
    sides = [[(x, -1.6 + (y + 1.6) * 0.225 / 1) if False else (x, y) for x, y in s] for s in sides]
    sides[2] = [(x, -1.6 + (y + 1.6) * 0.225) for x, y in sides[2]]
    drip = []
    for i in range(61):
        t = math.pi + math.pi * i / 60
        x = 2.0 * math.cos(t)
        y = 0.6 + 0.45 * math.sin(t)
        d = 0.25 + 0.35 * max(0.0, math.sin(7 * (t - math.pi))) ** 2
        drip.append((x, y - d))
    layer = [[(x, -0.55 + 0.45 * math.sin(math.pi + math.pi * i / 50)) for i, x in enumerate([2.0 * math.cos(math.pi + math.pi * i / 50) for i in range(51)])]]
    nest = [ellipse(0, 0.75, 1.05, 0.32, 60), ellipse(0, 0.8, 0.8, 0.2, 50)]
    eggs = []
    for x, y, r in [(-0.45, 1.25, 0.25), (0.45, 1.25, -0.25), (0.0, 1.45, 0.0)]:
        E = egg(x, y, 0.32, 0.42, r)
        eggs = hide(eggs, E) + [E] + pattern(E, x, y, r, [("zig", 0.0, 0.07, 0.18)])
    nest = hide(nest, *[egg(x, y, 0.32, 0.42, r) for x, y, r in [(-0.45, 1.25, 0.25), (0.45, 1.25, -0.25), (0.0, 1.45, 0.0)]])
    carrots = []
    for x in (-1.2, 0.0, 1.2):
        b, l, lv = carrot_shape(x, -0.95, x, -1.65, 0.28)
        carrots += b + hide(lv, *b)
    plate = [ellipse(0, -1.75, 2.7, 0.4, 100)]
    plate = hide(plate, poly((-2.0, -1.6), (2.0, -1.6), *[(2.0 * math.cos(t), -1.6 + 0.45 * 0.225 * math.sin(t) * 4.4) for t in [2 * math.pi - math.pi * i / 30 for i in range(31)]]))
    stand = [poly((-0.35, -2.15), (-0.5, -2.75), (0.5, -2.75), (0.35, -2.15), closed=False), ellipse(0, -2.85, 1.3, 0.2, 50)]
    out = [top] + hide(sides + layer, poly(*drip, (2.0, 0.6), (-2.0, 0.6))) + [drip] + hide(nest + eggs, ) + carrots + plate + stand
    return make("Easter Layer Cake", out)


@design("easter_bonnet_lady", T)
def bonnet_lady(rng):
    face = ellipse(0, 0.1, 1.05, 1.3, 90)
    brim = [(0.0 + (2.35 + 0.07 * math.sin(26 * t)) * math.cos(t), 0.3 + (2.35 + 0.07 * math.sin(26 * t)) * math.sin(t))
            for t in [math.radians(-35 + 250 * i / 200) for i in range(201)]]
    inner = arc(0, 0.3, 1.75, math.radians(-30), math.radians(210), 80)
    out = [brim, inner, [brim[0], inner[0]], [brim[-1], inner[-1]]]
    hair = chain(*[arc(-0.75 + 0.3 * k, 1.05, 0.17, 0, math.pi, 8) for k in range(6)])
    covers = []
    for x, y, r in [(-1.5, 1.7, 0.45), (-0.55, 2.35, 0.5), (0.55, 2.35, 0.45), (1.5, 1.7, 0.5), (2.0, 0.6, 0.4)]:
        f, c = flower(x, y, r)
        out = hide(out, *c) + f
        covers += c
    leaves = hide([lens((-1.05, 2.2), (-1.3, 2.75), 0.3), lens((1.05, 2.2), (1.35, 2.65), 0.3)], *covers)
    out = hide(out, face) + leaves + [face] + keep([hair], face)
    lids = [arc(-0.4, 0.3, 0.2, math.pi * 1.1, math.pi * 1.9, 8), arc(0.4, 0.3, 0.2, math.pi * 1.1, math.pi * 1.9, 8)]
    smile = arc(0, -0.25, 0.35, math.pi * 1.2, math.pi * 1.8, 10)
    cheeks = [circle(-0.6, -0.15, 0.17, 12), circle(0.6, -0.15, 0.17, 12)]
    nose = quad((0.02, 0.15), (0.12, -0.05), (-0.05, -0.05), 6)
    bow = [lens((0, -1.45), (-0.9, -1.0), 0.45), lens((0, -1.45), (0.9, -1.0), 0.45), circle(0, -1.45, 0.15, 12)]
    ties = [quad((-1.5, -0.95), (-0.9, -1.45), (-0.12, -1.42), 10), quad((1.5, -0.95), (0.9, -1.45), (0.12, -1.42), 10)]
    tails = [poly((-0.1, -1.6), (-0.6, -2.4), (-0.3, -2.35), (-0.02, -1.62), closed=False), poly((0.1, -1.6), (0.6, -2.4), (0.3, -2.35), (0.02, -1.62), closed=False)]
    neck = [[(-0.42, -1.1), (-0.42, -1.6)], [(0.42, -1.1), (0.42, -1.6)]]
    shoulders = [quad((-0.42, -1.6), (-1.6, -1.7), (-2.3, -2.8), 12), quad((0.42, -1.6), (1.6, -1.7), (2.3, -2.8), 12)]
    collar = [quad((-0.6, -1.65), (-0.5, -2.2), (0, -2.05), 8), quad((0.6, -1.65), (0.5, -2.2), (0, -2.05), 8)]
    out = hide(out, *bow) + hide(ties + neck + shoulders + collar + tails, *bow, face) + hide(bow[:2], bow[2]) + [bow[2]]
    return make("Lady in an Easter Bonnet", out + lids + [smile, nose] + cheeks)


@design("easter_bunny_teacup", T)
def bunny_teacup(rng):
    rim = ellipse(0, 0, 2.0, 0.42, 100)
    front = chain([(2.0, 0.0)], [(2.0 * math.cos(t), 0.42 * math.sin(t)) for t in [-math.pi * i / 40 for i in range(41)]],
                  cubic((-2.0, 0.0), (-2.0, -1.8), (-1.0, -2.2), (0, -2.2), 20), cubic((0, -2.2), (1.0, -2.2), (2.0, -1.8), (2.0, 0.0), 20))
    bowl = chain(cubic((-2.0, 0.0), (-2.0, -1.8), (-1.0, -2.2), (0, -2.2), 20), cubic((0, -2.2), (1.0, -2.2), (2.0, -1.8), (2.0, 0.0), 20))
    hs, hh, hc = bunny_head(0, 1.25, 0.95, ears=((-0.42, -0.7, 2.5), (0.42, 1.9, 1.5)))
    body = ellipse(0, 0.0, 1.05, 0.9, 60)
    paws = [ellipse(-0.6, -0.2, 0.38, 0.26, 20), ellipse(0.6, -0.2, 0.38, 0.26, 20)]
    out = hs + hide([body], *hc, front, *paws) + paws + hide([rim], body, *hc, *paws) + hide([bowl], *paws)
    handle = hide([arc(2.0, -0.95, 0.65, -1.45, 1.45, 20), arc(2.0, -0.95, 0.35, -1.35, 1.35, 16)], front)
    saucer = hide([ellipse(0, -2.25, 3.0, 0.5, 120), ellipse(0, -2.3, 2.0, 0.3, 80)], front)
    deco = keep([wave(-2.2, 2.2, -0.75, 0.12, 5, 120)], front) + [heart(x, -1.3, 0.2) for x in (-1.0, 0.0, 1.0)]
    deco = hide(deco, *paws)
    return make("Bunny in a Teacup", out + handle + saucer + deco, hh)


@design("easter_basket_bike", T)
def basket_bike(rng):
    out = []
    for x in (-1.9, 1.9):
        out += [circle(x, -1.5, 1.15, 90), circle(x, -1.5, 0.95, 80), circle(x, -1.5, 0.12, 10)]
        out += [[(x + 0.12 * math.cos(a), -1.5 + 0.12 * math.sin(a)), (x + 0.95 * math.cos(a), -1.5 + 0.95 * math.sin(a))] for a in [k * TAU / 8 + 0.2 for k in range(8)]]
    crank = (-0.15, -1.5)
    frame = [[(-1.9, -1.5), crank, (-0.7, 0.2), (-1.9, -1.5)], [crank, (1.3, 0.25)], [(-0.55, 0.0), (1.3, 0.25)], [(1.2, 0.6), (1.9, -1.5)]]
    out += frame + [circle(crank[0], crank[1], 0.3, 24), [(crank[0] + 0.1, crank[1] - 0.28), (0.25, -2.0)], rect(0.05, -2.12, 0.55, -1.95)]
    out += [[(-0.7, 0.2), (-0.8, 0.5)], chain(quad((-1.3, 0.62), (-0.8, 0.45), (-0.3, 0.68), 8), quad((-0.3, 0.68), (-0.8, 0.85), (-1.3, 0.62), 8))]
    out += [[(1.2, 0.6), (1.1, 1.1)], quad((1.1, 1.1), (0.8, 1.25), (0.45, 1.1), 8)]
    basket = poly((1.4, 0.35), (3.2, 0.35), (3.0, 1.35), (1.55, 1.35))
    weave = keep([[(1, 0.68), (4, 0.68)], [(1, 1.0), (4, 1.0)]] + [[(x, 0.3), (x + 0.05, 1.4)] for x in (1.9, 2.3, 2.7)], basket)
    items = []
    for x, y, r in [(1.85, 1.6, 0.3), (2.35, 1.75, 0.0), (2.85, 1.6, -0.3)]:
        E = egg(x, y, 0.3, 0.4, r)
        items = hide(items, E) + [E] + pattern(E, x, y, r, [("zig", 0.0, 0.07, 0.2)])
    for x, y, r in [(1.6, 2.6, 0.35), (3.1, 2.5, -0.35)]:
        sh, c = tulip(x, y, 0.55, r)
        items = hide(items, c) + sh + [quad((x + 0.3 * math.sin(r), y - 0.35), ((x + 2.4) / 2, 1.9), (2.4, 1.4), 8)]
    items = hide(items, basket)
    out = hide(out, basket) + [basket] + weave + items + [[(1.25, 0.6), (1.5, 0.75)], [(1.55, -0.3), (1.5, 0.35)]]
    out.append(hide([[(-3.3, -2.65), (3.4, -2.65)]], )[0])
    return make("Bicycle with an Easter Basket", out)


@design("easter_butterfly_egg", T)
def butterfly_egg(rng):
    E = egg(-0.3, -0.3, 1.9, 2.45)
    pat = pattern(E, -0.3, -0.3, 0, [("line", 0.35, 0, 1), ("line", -0.35, 0, 1), ("scallop", 1.3, 0, 0.55), ("zig", -1.25, 0.18, 0.45)])
    fls = []
    for x in (-1.4, -0.3, 0.8):
        f, _ = flower(x, -0.3, 0.3)
        fls += f
    dots = spots(-0.3, -0.3, 0, [(-0.6, 1.85), (0.0, 2.0), (0.6, 1.85), (-0.4, -1.85), (0.4, -1.85)], 0.13)
    b1, c1 = butterfly(1.15, 1.8, 0.95, -0.3)
    b2, c2 = butterfly(2.4, -1.6, 0.6, 0.4)
    out = hide([E] + pat + fls + dots, *c1) + b1 + b2
    return make("Butterflies on a Painted Egg", out)


@design("easter_resting_lamb", T)
def resting_lamb(rng):
    fleece = [(2.4 * math.cos(t) * (1 + 0.05 * math.sin(14 * t)), -1.1 + 1.25 * math.sin(t) * (1 + 0.06 * math.sin(14 * t))) for t in [TAU * i / 400 for i in range(401)]]
    head = ellipse(0, 0.45, 0.78, 0.98, 70)
    topknot = chain(*[arc(-0.5 + 0.25 * k, 1.35 + 0.1 * math.sin(k * 1.4), 0.17, 0, math.pi, 8) for k in range(5)])
    ears = [lens((-0.65, 0.85), (-1.75, 0.55), 0.3), lens((0.65, 0.85), (1.75, 0.55), 0.3)]
    nose = [poly((-0.15, -0.05), (0.15, -0.05), (0.0, -0.2)), [(0, -0.2), (0, -0.32)], arc(-0.12, -0.32, 0.12, 0, -math.pi, 8), arc(0.12, -0.32, 0.12, math.pi, 2 * math.pi, 8)]
    bow = [lens((0, -0.7), (-0.75, -0.35), 0.45), lens((0, -0.7), (0.75, -0.35), 0.45), circle(0, -0.7, 0.13, 12)]
    bell = [chain(arc(0, -1.15, 0.32, 0, math.pi, 16), [(-0.38, -1.35), (0.38, -1.35), (0.32, -1.15)]), circle(0, -1.45, 0.1, 10)]
    hooves = [rrect(-1.25, -2.55, -0.55, -2.1, 0.15), rrect(0.55, -2.55, 1.25, -2.1, 0.15)]
    covers = [head] + ears + bow + bell[:1] + hooves
    out = hide([fleece], *covers) + hide(ears, head) + [head] + keep([topknot], head) + nose + hide(bow[:2], bow[2]) + [bow[2]] + bell + hooves
    curls = keep([arc(x, y, 0.2, 0.3, 4.5, 10) for x, y in [(-1.8, -1.2), (-1.4, -1.8), (1.5, -1.5), (1.9, -0.9), (-1.9, -0.5), (1.3, -0.4)]], fleece)
    grass = hide([zigzag(-3.2, 3.2, -2.6, 0.18, 18)], fleece, *hooves)
    f1, _ = flower(-2.8, -1.4, 0.4)
    f2, _ = flower(2.8, -1.6, 0.4)
    return make("Little Lamb Resting", out + curls + grass + f1 + f2, [eye(-0.3, 0.45, 0.1), eye(0.3, 0.45, 0.1)])


@design("easter_cross_lilies", T)
def cross_lilies(rng):
    cross = poly((-0.3, -1.3), (0.3, -1.3), (0.3, 1.3), (1.3, 1.3), (1.3, 1.9), (0.3, 1.9), (0.3, 2.9), (-0.3, 2.9), (-0.3, 1.9),
                 (-1.3, 1.9), (-1.3, 1.3), (-0.3, 1.3))
    hill_c = chain(quad((-3.3, -1.7), (0, -0.7), (3.3, -1.7), 40))
    ground = poly(*hill_c, (3.3, -4), (-3.3, -4))
    rays = [[(0 + 1.9 * math.cos(a), 1.6 + 1.9 * math.sin(a)), (0 + 2.9 * math.cos(a), 1.6 + 2.9 * math.sin(a))] for a in [k * TAU / 16 for k in range(16)]]
    halo = circle(0, 1.6, 1.6, 100)
    out = hide([halo] + rays, cross, ground) + [cross] + hide([hill_c], cross)
    covers = []
    for x, y, r in [(-0.55, -2.3, 2.45), (0.55, -2.3, 0.69)]:
        sh, c = lily(x, y, 0.85, r)
        out = hide(out, c) + sh
        covers.append(c)
    stems = hide([quad((-0.55, -2.3), (-0.4, -2.8), (-0.15, -3.1), 10), quad((0.55, -2.3), (0.4, -2.8), (0.15, -3.1), 10)], *covers)
    leaves = hide([lens((-0.1, -3.1), (-2.6, -3.0), 0.15), lens((0.1, -3.1), (2.6, -3.0), 0.15)], *covers)
    return make("Easter Cross with Lilies", out + stems + leaves)


@design("easter_egg_tree", T)
def egg_tree(rng):
    pot = poly((-1.0, -1.9), (1.0, -1.9), (0.75, -3.0), (-0.75, -3.0))
    rim = rect(-1.15, -1.9, 1.15, -1.55)
    trunk = tube([(0, -1.55), (0.05, -0.3), (-0.1, 0.6)], lambda t: 0.32 - 0.15 * t, cap=False)
    branches = [quad((-0.1, 0.6), (-0.9, 1.4), (-2.3, 2.1), 14), quad((-0.1, 0.6), (0.2, 1.6), (0.0, 2.9), 14), quad((0.0, 0.0), (1.2, 0.6), (2.5, 1.5), 14),
                quad((-0.05, -0.2), (-1.3, 0.1), (-2.6, 0.4), 14), quad((0.1, 1.5), (0.8, 2.0), (1.5, 2.7), 12), quad((-0.9, 1.4), (-1.1, 2.1), (-0.9, 2.8), 10),
                quad((1.2, 0.65), (1.4, 1.3), (1.2, 1.9), 10)]
    eggs = []
    for (x, y), kind in zip([(-2.0, 1.95), (-0.9, 2.55), (0.0, 2.45), (1.3, 2.4), (2.1, 1.2), (1.25, 1.65), (-1.8, 0.3), (-1.1, 1.3), (0.9, 0.5), (-2.6, 0.35)],
                            ["zig", "wave", "line", "zig", "wave", "line", "zig", "wave", "zig", "line"]):
        top = y - 0.3
        E = egg(x, top - 0.45, 0.28, 0.37)
        eggs += [[(x, y), (x, top - 0.08)], E] + pattern(E, x, top - 0.45, 0, [(kind, 0.0, 0.06, 0.16)])
    out = [pot] + hide([rim], ) + hide([trunk] + branches, rim) + eggs
    out += keep([wave(-2, 2, -2.45, 0.1, 6, 80)], pot)
    bow = [lens((0.95, -1.75), (1.6, -1.35), 0.4), lens((0.95, -1.75), (1.6, -2.15), 0.4)]
    return make("Easter Egg Tree", hide(out, *bow) + bow)


@design("easter_carrot_patch", T)
def carrot_patch(rng):
    pickets = []
    for k in range(10):
        x = -3.0 + 0.66 * k
        pickets.append(poly((x - 0.22, -0.3), (x + 0.22, -0.3), (x + 0.22, 1.2), (x, 1.5), (x - 0.22, 1.2)))
    rails = hide([[(-3.3, 0.2), (3.3, 0.2)], [(-3.3, 0.85), (3.3, 0.85)]], *pickets)
    rows = []
    covers = []
    for y, xs in [(-0.9, (-2.2, -0.75, 0.7, 2.15)), (-2.0, (-1.45, 0.0, 1.45))]:
        for x in xs:
            top = arc(x, y, 0.32, 0, math.pi, 12)
            leaves = [lens((x, y + 0.3), (x + dx, y + 1.0), 0.22) for dx in (-0.4, 0.0, 0.4)]
            mound = quad((x - 0.65, y - 0.05), (x, y + 0.2), (x + 0.65, y - 0.05), 10)
            rows += [top] + hide(leaves, top) + [mound]
            covers += [poly(*top)] + leaves
    out = hide(pickets + rails, *covers) + rows
    b, l, lv = carrot_shape(-1.6, -2.9, 1.2, -2.6, 0.5)
    out = hide(out, *b, *lv) + b + l + hide(lv, *b)
    sun = [circle(2.45, 2.4, 0.5, 40)] + [[(2.45 + 0.65 * math.cos(a), 2.4 + 0.65 * math.sin(a)), (2.45 + 0.95 * math.cos(a), 2.4 + 0.95 * math.sin(a))] for a in [k * TAU / 10 for k in range(10)]]
    return make("Carrot Patch by the Fence", out + sun)


@design("easter_bunny_family", T)
def bunny_family(rng):
    out, covers = [], []
    for cx, s in [(2.25, 0.55), (0.75, 0.78), (-1.4, 1.0)]:
        by = -2.7
        body = ellipse(cx, by + 1.1 * s, 1.05 * s, 1.15 * s, 70)
        head = circle(cx, by + 2.55 * s, 0.7 * s, 50)
        ears = [lens((cx - 0.3 * s, by + 3.0 * s), (cx - 0.6 * s, by + 4.4 * s), 0.22), lens((cx + 0.3 * s, by + 3.0 * s), (cx + 0.65 * s, by + 4.35 * s), 0.22)]
        sil = union(body, head, *ears)
        tail = circle(cx, by + 0.45 * s, 0.32 * s, 24)
        feet = [ellipse(cx - 0.55 * s, by + 0.05 * s, 0.32 * s, 0.17 * s, 16), ellipse(cx + 0.55 * s, by + 0.05 * s, 0.32 * s, 0.17 * s, 16)]
        mine = sil + [tail] + hide(feet, tail)
        out = hide(out, body, head, *ears, *feet) + mine
        covers += [body, head] + ears + feet
    horizon = hide([wave(-3.3, 3.3, -0.9, 0.12, 2, 120)], *covers)
    sun = circle(2.3, 1.7, 0.6, 50)
    rays = [[(2.3 + 0.8 * math.cos(a), 1.7 + 0.8 * math.sin(a)), (2.3 + 1.1 * math.cos(a), 1.7 + 1.1 * math.sin(a))] for a in [k * TAU / 10 for k in range(10)]]
    out += hide([sun] + rays, *covers) + horizon
    out += [tuft(-3.0, -2.7, 0.8), tuft(3.0, -2.7, 0.7), [(-3.3, -2.7), (3.3, -2.7)]]
    out = hide(out[:-1], ) + hide([out[-1]], *covers)
    return make("Bunny Family at Sunrise", out)


@design("easter_sleeping_bunny", T)
def sleeping_bunny(rng):
    body = ellipse(0.4, -0.6, 2.1, 1.1, 120)
    head = ellipse(-1.5, -0.35, 0.95, 0.8, 70)
    haunch = ellipse(1.3, -0.8, 1.1, 0.9, 60)
    tail = circle(2.45, -0.35, 0.35, 24)
    ear = lens((-1.35, 0.25), (1.2, 0.75), 0.13)
    paw = ellipse(-1.4, -1.55, 0.6, 0.2, 24)
    sil = union(body, head, haunch, tail, paw)
    out = hide(sil, ear) + [ear, lens((-0.8, 0.38), (0.8, 0.65), 0.07)] + keep([ellipse(1.3, -0.8, 1.1, 0.9, 60)], body)
    out += [arc(-1.7, -0.15, 0.2, math.pi * 1.1, math.pi * 1.9, 10), poly((-2.48, -0.32), (-2.32, -0.28), (-2.38, -0.45))]
    out += [[(-2.35, -0.5), (-3.0, -0.45)], [(-2.35, -0.55), (-2.95, -0.75)]]
    cushion = rrect(-3.2, -2.4, 3.2, -1.45, 0.45)
    out += hide([cushion, [(-3.2, -1.95), (3.2, -1.95)]], body, head, haunch, paw)
    zs = [poly((x, y), (x + s, y), (x, y - s), (x + s, y - s), closed=False) for x, y, s in [(-2.0, 1.2, 0.35), (-1.4, 1.85, 0.45), (-0.6, 2.6, 0.55)]]
    moon = chain(arc(2.2, 2.2, 0.75, math.radians(60), math.radians(300), 30), arc(2.55, 2.2, 0.6, math.radians(270), math.radians(90), 30)[::-1][::-1])
    moon = [arc(2.2, 2.2, 0.75, math.radians(60), math.radians(300), 30), arc(2.62, 2.2, 0.62, math.radians(240), math.radians(120), 24)]
    stars = [star(0.9, 2.6, 0.25), star(3.0, 0.9, 0.2)]
    return make("Sleeping Bunny", out + zs + moon + stars)


@design("easter_egg_cottage", T)
def egg_cottage(rng):
    E = egg(0, 0, 2.0, 2.6)
    ground_y = -2.45
    eave = [(-2.4, 1.0), (2.4, 1.0)]
    roof_reg = poly((-3, 1.0), (3, 1.0), (3, 3), (-3, 3))
    shingles = keep(keep([chain(*[arc(-3 + 0.5 * (j + 0.5) + (0.25 if r % 2 else 0), y, 0.25, math.pi, 2 * math.pi, 8) for j in range(12)]) for r, y in enumerate([1.55, 2.05])], E), roof_reg)
    eave = hide([eave], ) + []
    eave_l = [(-2.25, 0.95), (-2.25, 1.15), (2.25, 1.15), (2.25, 0.95), (-2.25, 0.95)]
    chim = rect(0.75, 1.9, 1.15, 3.0)
    smoke = [circle(1.2, 3.3, 0.18, 14), circle(1.5, 3.6, 0.22, 16), circle(1.9, 3.85, 0.26, 18)]
    door = chain([(-0.45, ground_y), (-0.45, -1.4)], arc(0, -1.4, 0.45, math.pi, 0, 20), [(0.45, ground_y)])
    knob = circle(0.25, -1.9, 0.08, 10)
    wins = []
    for x, y in [(-1.15, -0.3), (1.15, -0.3)]:
        wins += [circle(x, y, 0.42, 40), [(x - 0.42, y), (x + 0.42, y)], [(x, y - 0.42), (x, y + 0.42)], rect(x - 0.5, y - 0.75, x + 0.5, y - 0.5)]
    top_win = [heart(0, 0.45, 0.35)]
    house = hide([E], chim, poly(*eave_l), poly((-3, ground_y), (3, ground_y), (3, -4), (-3, -4)))
    out = house + shingles + [eave_l, chim] + smoke + hide([door], ) + [knob] + wins + top_win
    out = hide(out, poly(*eave_l))[:0] + out
    path = [quad((-0.45, ground_y), (-0.8, -2.8), (-1.3, -3.2), 8), quad((0.45, ground_y), (0.8, -2.8), (1.3, -3.2), 8)]
    flowers = []
    for x in (-2.4, -1.6, 1.6, 2.4):
        f, _ = flower(x, -1.95, 0.32)
        flowers += f + [[(x, -2.27), (x, ground_y)]]
    ground = [[(-3.0, ground_y), (-0.45, ground_y)], [(0.45, ground_y), (3.0, ground_y)]]
    return make("Egg-Shaped Cottage", hide(out, poly(*eave_l))[:0] + out + path + flowers + ground)


@design("easter_chick_car", T)
def chick_car(rng):
    car = chain(zigzag(-2.6, 2.6, -0.15, 0.17, 9), [(2.6 * math.cos(t), -0.3 + 1.35 * math.sin(t)) for t in [-math.pi * i / 60 for i in range(61)]])
    car.append(car[0])
    wheels, wc = [], []
    for x in (-1.5, 1.5):
        w = circle(x, -1.6, 0.68, 50)
        wc.append(w)
        wheels += [w, circle(x, -1.6, 0.25, 16)]
    ch, hh, cc = chick(-0.2, 0.55, 0.9, feet=False)
    ch = hide(ch, car)
    steer = hide([ellipse(1.15, 0.2, 0.15, 0.42, 20, rot=0.25), [(1.15, -0.1), (1.5, -0.3)]], car, *cc)
    spots_ = [circle(x, y, 0.22, 16) for x, y in [(-2.1, -0.55), (-0.5, -0.75), (0.5, -0.75), (2.1, -0.55)]]
    light = ellipse(2.5, -0.65, 0.16, 0.28, 14)
    puffs = [circle(-2.95, -1.0, 0.22, 14), circle(-3.4, -0.75, 0.3, 18), circle(-3.4, -1.3, 0.18, 12)]
    speed = [[(-3.6, 0.3), (-2.7, 0.3)], [(-3.8, -0.2), (-2.9, -0.2)]]
    ground = hide([[(-3.8, -2.28), (3.0, -2.28)]], *wc)
    return make("Chick Driving an Eggshell Car", hide([car] + spots_, *wc) + wheels + ch + steer + [light] + puffs + speed + ground, hh)


@design("easter_jelly_bean_jar", T)
def jelly_bean_jar(rng):
    jar = rrect(-1.7, -2.9, 1.7, 1.0, 0.55)
    neck = rect(-1.25, 1.0, 1.25, 1.35)
    lid = rrect(-1.45, 1.35, 1.45, 2.1, 0.15)
    ribs = [[(x, 1.4), (x, 2.05)] for x in (-1.0, -0.5, 0.0, 0.5, 1.0)]
    label = egg(0, -0.95, 0.95, 1.2)
    R = random.Random(11)
    beans = []
    for row in range(8):
        y = -2.55 + 0.45 * row
        for col in range(6):
            x = -1.35 + 0.55 * col + (0.27 if row % 2 else 0)
            if x > 1.4:
                continue
            beans.append(bean(x, y, R.uniform(-1.5, 1.5), 0.95))
    beans = hide(keep(beans, jar), label)
    beans = [b for b in beans if path_len(b) > 0.5]
    hs, hh, hc = bunny_head(0, -1.35, 0.42, face=False)
    bow = [lens((0, 1.18), (-1.0, 1.55), 0.4), lens((0, 1.18), (1.0, 1.55), 0.4), circle(0, 1.18, 0.13, 12)]
    tails = [poly((-0.08, 1.06), (-0.5, 0.35), (-0.25, 0.4), closed=False), poly((0.08, 1.06), (0.5, 0.35), (0.25, 0.4), closed=False)]
    out = [jar] + hide([neck], *bow) + [lid] + ribs + beans + [label] + hs + hide(bow[:2], bow[2]) + [bow[2]] + hide(tails, *bow)
    out = hide(out[:1], *tails) + out[1:]
    return make("Jar of Jelly Beans", out)


@design("easter_egg_garland", T)
def egg_garland(rng):
    out = []
    kinds = ["zig", "wave", "scallop", "line", "zig", "wave", "scallop"]
    for row, (y0, sag, n) in enumerate([(2.9, 1.0, 6), (0.4, 1.0, 5)]):
        string = quad((-3.3, y0), (0, y0 - 2 * sag), (3.3, y0), 60)
        covers = []
        items = []
        for k in range(n):
            t = (k + 0.5) / n
            i = int(t * 60)
            x, y = string[i]
            if row == 0:
                E = egg(x, y - 0.62, 0.45, 0.6)
                items += [E] + pattern(E, x, y - 0.62, 0, [(kinds[k], 0.0, 0.1, 0.25), ("line", 0.3, 0, 1), ("line", -0.3, 0, 1)])
                covers.append(E)
            else:
                hs, hh, hc = bunny_head(x, y - 0.75, 0.42, face=False)
                items += hs + [ellipse(x, y - 0.95, 0.15, 0.1, 10)]
                covers += hc
        out += hide([string], *covers) + items
        out += [circle(-3.3, y0, 0.12, 10), circle(3.3, y0, 0.12, 10)]
    return make("Easter Egg Garland", out)


@design("easter_hen_on_nest", T)
def hen_on_nest(rng):
    body = ellipse(0.4, 0.0, 2.0, 1.3, 120)
    neck = ellipse(-1.05, 0.75, 0.6, 0.95, 50, rot=0.45)
    head = circle(-1.45, 1.5, 0.62, 50)
    tail = poly((1.6, 0.8), (2.15, 2.1), (2.35, 1.35), (2.85, 1.85), (2.75, 1.0), (3.1, 1.2), (2.4, 0.0))
    out = union(body, neck, head, tail)
    comb = chain(*[arc(-1.8 + 0.27 * k, 2.1 + 0.08 * k, 0.15, math.pi, 0, 8) for k in range(4)])
    beak = poly((-2.0, 1.6), (-2.4, 1.45), (-2.0, 1.3))
    wattle = chain(quad((-1.95, 1.3), (-2.15, 0.8), (-1.85, 0.85), 8), quad((-1.85, 0.85), (-1.75, 1.05), (-1.8, 1.25), 6))
    out = hide(out, beak) + [beak, comb, wattle]
    wing = chain(cubic((-0.3, 0.6), (0.6, 1.0), (1.8, 0.5), (1.9, -0.3), 20), [(1.4, -0.15), (1.5, -0.6), (1.0, -0.35), (1.0, -0.8)], quad((1.0, -0.8), (0.0, -0.5), (-0.3, 0.6), 14))
    feathers = [quad((2.15, 2.0), (2.2, 1.2), (2.3, 0.4), 8), quad((2.8, 1.75), (2.6, 1.0), (2.4, 0.4), 8)]
    out += [wing] + feathers
    nest_top = wave(3.0, -2.8, -0.7, 0.1, 8, 100)
    nest = chain(nest_top, cubic((-2.8, -0.7), (-2.6, -2.9), (2.8, -2.9), (3.0, -0.7), 30))
    eggs = []
    ec = []
    for x, y, r in [(-1.8, -0.75, 0.4), (-0.9, -0.85, 0.15), (2.0, -0.8, -0.3)]:
        E = egg(x, y, 0.45, 0.6, r)
        eggs += [E] + pattern(E, x, y, r, [("zig", 0.05, 0.1, 0.25)])
        ec.append(E)
    out = hide(out, nest, *ec) + hide(eggs, nest) + [nest]
    twigs = keep([quad((-3, -1.1 - 0.45 * k), (0, -1.4 - 0.45 * k), (3, -1.0 - 0.45 * k), 20) for k in range(3)] +
                 [[(-2.0 + 0.8 * k, -0.8), (-1.6 + 0.8 * k, -2.4)] for k in range(6)], nest)
    return make("Mother Hen on Her Nest", out + twigs, [eye(-1.55, 1.6, 0.1)])


@design("easter_daffodils", T)
def daffodils(rng):
    def daffodil(cx, cy, r):
        trumpet = polar(lambda t: 0.42 * r * (1 + 0.08 * math.sin(12 * t)), cx=cx, cy=cy, n=120)
        pet = [lens((cx, cy), (cx + r * math.cos(a), cy + r * math.sin(a)), 0.3) for a in [math.pi / 2 + k * TAU / 6 for k in range(6)]]
        return hide(union(*pet), trumpet) + [trumpet, circle(cx, cy, 0.18 * r, 14)], [trumpet] + pet
    out, covers = [], []
    for x, y, r in [(0.1, 0.55, 0.8), (-1.3, 1.75, 1.0), (1.25, 2.0, 1.05)]:
        f, c = daffodil(x, y, r)
        out = hide(out, *c) + f
        covers += c
    stems = [quad((-1.3, 1.3), (-0.9, 0.0), (-0.3, -0.7), 12), quad((1.25, 1.55), (0.9, 0.2), (0.3, -0.7), 12), [(0.1, 0.2), (0.0, -0.7)]]
    leaves = [lens((-0.2, -0.7), (-2.5, 0.3), 0.12), lens((0.2, -0.7), (2.6, 0.4), 0.12), lens((-0.1, -0.7), (-1.0, 0.8), 0.1)]
    out = hide(stems, *covers) + hide(leaves, *covers) + out
    rim = rect(-1.4, -1.15, 1.4, -0.65)
    pot = poly((-1.2, -1.15), (1.2, -1.15), (0.9, -2.9), (-0.9, -2.9))
    out = hide(out, rim, pot) + [rim, pot] + keep([zigzag(-2, 2, -2.0, 0.15, 10)], pot)
    return make("Daffodils in a Pot", out)


@design("easter_postage_stamp", T)
def postage_stamp(rng):
    x0, y0, x1, y1 = -2.3, -2.9, 2.3, 2.9
    edge = []
    nx, ny = 9, 11
    r = 0.13
    for k in range(nx):
        a = x0 + (x1 - x0) * (k + 0.5) / nx
        edge += [(a - r - 0.08, y0)] + arc(a, y0, r, math.pi, 0, 6) + [(a + r + 0.08, y0)]
    for k in range(ny):
        a = y0 + (y1 - y0) * (k + 0.5) / ny
        edge += [(x1, a - r - 0.08)] + arc(x1, a, r, -math.pi / 2, -1.5 * math.pi, 6) + [(x1, a + r + 0.08)]
    for k in range(nx):
        a = x1 - (x1 - x0) * (k + 0.5) / nx
        edge += [(a + r + 0.08, y1)] + arc(a, y1, r, 0, -math.pi, 6) + [(a - r - 0.08, y1)]
    for k in range(ny):
        a = y1 - (y1 - y0) * (k + 0.5) / ny
        edge += [(x0, a + r + 0.08)] + arc(x0, a, r, math.pi / 2, -math.pi / 2, 6) + [(x0, a - r - 0.08)]
    edge.append(edge[0])
    frame = rect(-1.85, -2.45, 1.85, 2.45)
    body = ellipse(0.3, -0.95, 0.95, 1.05, 70)
    head = ellipse(-0.35, 0.4, 0.62, 0.55, 50, rot=0.15)
    haunch = ellipse(0.65, -1.5, 0.8, 0.6, 50)
    tail = circle(1.35, -1.15, 0.25, 20)
    ear1 = lens((-0.25, 0.85), (0.15, 2.2), 0.2)
    ear2 = lens((0.05, 0.8), (0.95, 1.95), 0.2)
    foot = ellipse(-0.25, -1.95, 0.55, 0.18, 30)
    bun = union(body, head, haunch, tail, ear1, ear2, foot)
    E = egg(-1.2, -1.75, 0.32, 0.42, 0.2)
    sun = [arc(1.6, 2.45, 0.6, math.pi, 1.5 * math.pi, 12)]
    grass = [zigzag(-1.85, 1.85, -2.2, 0.1, 12)]
    mark = [circle(1.9, 1.9, 0.75, 50)] + [wave(0.3, 3.1, 1.9 + dy, 0.08, 3, 40) for dy in (-0.3, 0.0, 0.3)]
    mark = [mark[0]] + hide(mark[1:], mark[0]) + keep(mark[1:], mark[0])
    inner = hide([edge, frame] + bun + [E] + pattern(E, -1.2, -1.75, 0.2, [("zig", 0.0, 0.06, 0.16)]) + sun + grass, *mark[:1])
    return make("Easter Bunny Postage Stamp", inner + [mark[0]] + mark[1:], [eye(-0.55, 0.5, 0.07)])


@design("easter_hopping_bunny", T)
def hopping_bunny(rng):
    body = ellipse(0.2, 0.3, 1.7, 0.95, 100, rot=0.22)
    head = ellipse(-1.65, 1.0, 0.78, 0.66, 60, rot=0.2)
    hind = ellipse(1.65, -0.55, 1.15, 0.33, 40, rot=-0.55)
    front = ellipse(-1.35, -0.55, 0.7, 0.2, 30, rot=1.0)
    tail = circle(1.85, 0.85, 0.35, 24)
    ears = [lens((-1.4, 1.5), (0.4, 2.6), 0.18), lens((-1.2, 1.4), (0.75, 2.1), 0.18)]
    out = union(body, head, hind, front, tail, *ears)
    out += [lens((-0.9, 1.7), (0.1, 2.35), 0.1), poly((-2.42, 0.95), (-2.28, 1.02), (-2.3, 0.85))]
    out += keep([ellipse(1.2, -0.1, 0.9, 0.7, 50)], body)
    out += [[(-2.35, 0.8), (-3.0, 0.9)], [(-2.35, 0.75), (-2.95, 0.5)]]
    motion = [arc(2.9, -1.1, 0.5, 2.0, 3.6, 10), arc(3.2, -0.9, 0.8, 2.0, 3.6, 12)]
    ground = [[(-3.4, -2.4), (3.4, -2.4)]]
    arcpath = [quad((3.0, -2.3), (2.0, 1.5), (0.9, 2.6), 20)][:0]
    eggs = []
    for x, r, k in [(-2.6, 0.2, "zig"), (-0.6, -0.2, "wave"), (1.5, 0.1, "line")]:
        E = egg(x, -1.85, 0.4, 0.52, r)
        eggs += [E] + pattern(E, x, -1.85, r, [(k, 0.0, 0.08, 0.22), ("line", 0.25, 0, 1)])
    return make("Hopping Bunny", out + motion + ground + eggs + [tuft(0.5, -2.4, 0.6), tuft(2.7, -2.4, 0.6)], [eye(-1.75, 1.15, 0.1)])


@design("easter_bunny_painter", T)
def bunny_painter(rng):
    hs, hh, hc = bunny_head(-1.4, 1.1, 0.8, ears=((-0.42, -0.9, 2.4), (0.42, 0.55, 2.5)))
    body = ellipse(-1.4, -1.0, 1.05, 1.35, 80)
    feet = [ellipse(-2.05, -2.4, 0.5, 0.22, 24), ellipse(-0.75, -2.4, 0.5, 0.22, 24)]
    arm = tube(quad((-0.7, -0.4), (0.0, -0.1), (0.35, 0.3), 10), 0.38)
    paw = circle(0.4, 0.35, 0.22, 16)
    brush = [tube([(0.2, 0.0), (1.0, 1.0)], 0.12), poly((1.0, 1.0), (1.05, 1.25), (1.3, 1.45), (1.35, 1.15), (1.1, 1.0))]
    out = hide([body], *hc, *feet, arm, paw) + hs + feet + hide([arm], paw) + hide(brush, paw) + [paw]
    E = egg(2.1, 0.3, 1.05, 1.4)
    stripes = keep(pattern(E, 2.1, 0.3, 0, [("zig", 0.6, 0.15, 0.35), ("line", 0.25, 0, 1), ("wave", -0.15, 0.1, 0.5), ("line", -0.6, 0, 1)]),
                   poly((2.1, -3), (2.1, 3), (0, 3), (0, -3)))
    stand = [ellipse(2.1, -1.2, 0.7, 0.2, 30), poly((1.55, -1.25), (1.4, -2.5), (2.8, -2.5), (2.65, -1.25), closed=False)]
    egg_vis = hide([E] + stripes, *brush, paw)
    stand = hide(stand, E)
    pots = []
    for x in (-0.15, 0.75):
        pots += [rrect(x - 0.35, -2.6, x + 0.35, -1.95, 0.1), ellipse(x, -1.95, 0.35, 0.1, 16)]
    drip = [poly((1.12, 0.9), (1.05, 0.65), (1.15, 0.55), (1.22, 0.65), closed=True)]
    return make("Bunny Painting an Easter Egg", out + egg_vis + stand + pots + [[(-3.0, -2.62), (3.2, -2.62)]], hh)


@design("easter_chick_shell_hat", T)
def chick_shell_hat(rng):
    body = circle(0, -0.6, 1.8, 120)
    w, h = 1.15, 1.45
    hat = chain(zigzag(-w * 0.98, w * 0.98, 0.0, 0.16, 6), [(w * math.cos(t) * (1 - 0.13 * math.sin(t)), h * math.sin(t)) for t in [math.pi * i / 50 for i in range(51)]][::-1][::-1])
    upper = [(w * math.cos(t) * (1 - 0.13 * math.sin(t)), h * math.sin(t)) for t in [math.pi * i / 50 for i in range(51)]]
    hat = chain(upper, zigzag(-w, w, 0.05, 0.16, 6)[::-1][::-1][::-1] if False else zigzag(-w, w, 0.05, 0.16, 6))
    hat = transform(hat + [hat[0]], 0.15, 1.05, rot=-0.18)
    wings = [lens((-1.6, -0.3), (-2.6, 0.7), 0.32), lens((1.6, -0.3), (2.6, 0.7), 0.32)]
    beak = [poly((-0.25, -0.05), (0, 0.1), (0.25, -0.05), (0, -0.4)), [(-0.25, -0.05), (0.25, -0.05)]]
    cheeks = [circle(-0.85, -0.25, 0.2, 14), circle(0.85, -0.25, 0.2, 14)]
    feet = []
    for fx in (-0.6, 0.6):
        feet += [[(fx - 0.45, -2.75), (fx, -2.35), (fx + 0.45, -2.75)], [(fx, -2.35), (fx, -2.85)]]
    out = hide([body], hat) + [hat] + hide(wings, body) + beak + cheeks + hide(feet, body)
    out += pattern(hat, 0.15, 1.05, -0.18, [("line", 0.9, 0, 1)]) + spots(0.15, 1.05, -0.18, [(-0.5, 0.45), (0.1, 0.55), (0.6, 0.4)], 0.12)
    for x in (-2.5, 2.5):
        f, _ = flower(x, -1.9, 0.42)
        out += f + [[(x, -2.25), (x, -2.85)]]
    return make("Chick Wearing an Eggshell Hat", out + [[(-3.2, -2.85), (3.2, -2.85)]], [eye(-0.5, 0.35, 0.13), eye(0.5, 0.35, 0.13)])


@design("easter_sugar_cookies", T)
def sugar_cookies(rng):
    tray = [rrect(-3.2, -2.4, 3.2, 2.4, 0.35), rrect(-3.0, -2.2, 3.0, 2.2, 0.25)]
    out = list(tray)
    E = egg(-2.0, 1.1, 0.68, 0.9)
    out += [E, egg(-2.0, 1.1, 0.53, 0.75)] + pattern(egg(-2.0, 1.1, 0.53, 0.75), -2.0, 1.1, 0, [("zig", 0.0, 0.12, 0.3)])
    hs, hh, hc = bunny_head(0.0, 0.75, 0.55, ears=((-0.42, -0.6, 2.3), (0.42, 0.6, 2.3)), whiskers=False)
    out += hs
    ch, ch_h, cc = chick(2.05, 0.65, 0.5)
    out += ch
    b, l, lv = carrot_shape(-1.75, -0.7, -2.45, -1.85, 0.45)
    out += b + l + hide(lv, *b)
    f = [polar(lambda t: 0.85 + 0.15 * math.cos(5 * t), cx=0.0, cy=-1.15, n=120), circle(0.0, -1.15, 0.3, 20)]
    out += f + [polar(lambda t: 0.65 + 0.12 * math.cos(5 * t), cx=0.0, cy=-1.15, n=120)]
    bf, _ = butterfly(2.05, -1.1, 0.55, 0.0)
    out += bf
    return make("Easter Sugar Cookies", out, hh + ch_h)


@design("easter_pysanka", T)
def pysanka(rng):
    W, H = 2.1, 2.8
    E = egg(0, 0, W, H)
    belt = pattern(E, 0, 0, 0, [("line", 0.4, 0, 1), ("line", -0.4, 0, 1), ("line", 0.55, 0, 1), ("line", -0.55, 0, 1), ("zig", 0.0, 0.3, 0.6)])
    rose = [star(0, 1.45, 0.75, 8, 0.55), circle(0, 1.45, 0.25, 20), circle(0, 1.45, 0.9, 60)]
    sun = [circle(0, -1.45, 0.55, 40)] + [[(0.62 * math.cos(a), -1.45 + 0.62 * math.sin(a)), (0.95 * math.cos(a), -1.45 + 0.95 * math.sin(a))] for a in [k * TAU / 12 for k in range(12)]]
    curls = keep([spiral(sx * 1.35, 1.3, 0.05, 0.35, 1.6, 50) for sx in (-1, 1)] + [spiral(sx * 1.35, -1.3, 0.05, 0.35, 1.6, 50) for sx in (-1, 1)], E)
    tri = keep([poly((sx * 1.3, 0.62), (sx * 1.0, 1.0), (sx * 1.6, 1.0)) for sx in (-1, 1)], E)[:0]
    dots = [circle(x, y, 0.1, 10) for x, y in [(0, 2.55), (0, -2.55), (-0.75, 2.25), (0.75, 2.25), (-0.75, -2.25), (0.75, -2.25)]]
    return make("Pysanka Folk Egg", [E] + belt + rose + sun + curls + tri + dots)


@design("easter_ribbon_egg", T)
def ribbon_egg(rng):
    E = egg(0, -0.4, 1.85, 2.4)
    vband = keep([quad((-0.3, 2.2), (-0.45, -0.4), (-0.3, -3.0), 20), quad((0.3, 2.2), (0.45, -0.4), (0.3, -3.0), 20)], E)
    hband = keep([quad((-2.2, -0.05), (0, -0.35), (2.2, -0.05), 20), quad((-2.2, -0.7), (0, -1.0), (2.2, -0.7), 20)], E)
    hreg = poly(*quad((-2.2, -0.05), (0, -0.35), (2.2, -0.05), 20), *quad((2.2, -0.7), (0, -1.0), (-2.2, -0.7), 20))
    vband = hide(vband, hreg)
    bow = [lens((0, 2.1), (-1.4, 2.85), 0.42), lens((0, 2.1), (1.4, 2.85), 0.42), ellipse(0, 2.1, 0.25, 0.2, 16)]
    tails = [poly((-0.1, 1.95), (-0.9, 1.0), (-0.6, 0.95), (-0.05, 1.85), closed=False), poly((0.1, 1.95), (0.9, 1.0), (0.6, 0.95), (0.05, 1.85), closed=False)]
    dots = [circle(x, y, 0.17, 14) for x, y in [(-1.0, 0.8), (1.0, 0.8), (-1.2, -1.7), (1.2, -1.7), (-0.9, 1.6), (0.9, 1.6), (-0.8, -2.4), (0.8, -2.4), (-1.35, 0.0), (1.35, 0.0)]]
    out = hide([E] + vband + hband + dots, *bow, *tails) + hide(tails, *bow) + hide(bow[:2], bow[2]) + [bow[2]]
    return make("Egg Wrapped with a Ribbon Bow", out)


@design("easter_egg_spoon_race", T)
def egg_spoon_race(rng):
    handle = tube([(-2.8, -2.7), (0.35, 0.55)], lambda t: 0.36 - 0.12 * t)
    bowl = ellipse(0.95, 1.15, 1.05, 0.6, 60, rot=0.6)
    lower = transform([(1.05 * math.cos(t), 0.6 * math.sin(t)) for t in [math.pi + math.pi * i / 30 for i in range(31)]], 0.95, 1.15, rot=0.6)
    lower = lower + [lower[0]]
    inner = transform([(0.85 * math.cos(t), 0.42 * math.sin(t)) for t in [TAU * i / 50 for i in range(51)]], 0.95, 1.15, rot=0.6)
    E = egg(0.95, 1.85, 0.62, 0.82, -0.25)
    pat = pattern(E, 0.95, 1.85, -0.25, [("zig", 0.0, 0.12, 0.3), ("line", 0.35, 0, 1), ("line", -0.35, 0, 1)])
    egg_vis = hide([E] + pat, lower)
    out = hide([handle], bowl) + hide([bowl, inner], E) + egg_vis
    motion = [[(2.0 + 0.3 * k, 2.9 - 0.3 * k), (2.7 + 0.3 * k, 3.4 - 0.3 * k)] for k in range(3)]
    ros_c = (1.9, -1.5)
    ros = [polar(lambda t: 0.85 + 0.08 * math.sin(16 * t), cx=ros_c[0], cy=ros_c[1], n=200), circle(ros_c[0], ros_c[1], 0.6, 50), star(ros_c[0], ros_c[1], 0.45)]
    tails = [poly((1.6, -2.25), (1.3, -3.2), (1.6, -3.0), (1.85, -3.25), (2.0, -2.35), closed=False), poly((2.2, -2.25), (2.5, -3.2), (2.2, -3.0), closed=False)]
    tails = hide(tails, ros[0])
    return make("Egg and Spoon Race", out + motion + ros + tails)


@design("easter_bunny_in_basket", T)
def bunny_in_basket(rng):
    basket = chain([(-2.6, -0.3)], cubic((-2.6, -0.3), (-2.4, -2.8), (2.4, -2.8), (2.6, -0.3), 30), [(-2.6, -0.3)])
    rim = tube(quad((-2.75, -0.3), (0, -0.55), (2.75, -0.3), 30), 0.35)
    handle = [arc(0, -0.3, 2.45, 0.05, math.pi - 0.05, 60), arc(0, -0.3, 2.2, 0.06, math.pi - 0.06, 60)]
    hs, hh, hc = bunny_head(0, 0.9, 0.95)
    body = ellipse(0, -0.3, 1.1, 0.8, 50)
    paws = [ellipse(-0.75, -0.25, 0.32, 0.24, 20), ellipse(0.75, -0.25, 0.32, 0.24, 20)]
    eggs = []
    ec = []
    for x, y, r in [(-1.75, 0.1, 0.35), (1.8, 0.05, -0.3), (1.25, 0.0, 0.0)]:
        E = egg(x, y, 0.38, 0.5, r)
        eggs = hide(eggs, E) + [E] + pattern(E, x, y, r, [("zig", 0.0, 0.08, 0.22)])
        ec.append(E)
    weave = []
    for row in range(3):
        y = -1.0 - 0.5 * row
        for k in range(8):
            x = -2.5 + 0.65 * k + (0.32 if row % 2 else 0)
            weave.append(arc(x, y, 0.32, math.pi * 1.1, math.pi * 1.9, 8))
    weave = keep(weave, basket)
    grass = zigzag(-2.4, 2.4, -0.05, 0.15, 14)
    out = hide(handle, *hc, *ec) + hide(hs, rim, *paws) + hide([body], *hc, rim, basket, *paws) + paws
    out += hide(eggs, rim) + hide([grass], *hc, body, *ec, rim, *paws) + [rim] + hide([basket], rim) + hide(weave, rim)
    return make("Bunny Popping Out of a Basket", out, hh)


@design("easter_bunny_carrot", T)
def bunny_carrot(rng):
    hs, hh, hc = bunny_head(0, 0.85, 1.25, ears=((-0.42, -0.7, 2.3), (0.42, 0.75, 2.3)))
    cheeks = [circle(-0.65, 0.4, 0.2, 14), circle(0.65, 0.4, 0.2, 14)]
    body = ellipse(0, -1.9, 2.1, 1.4, 90)
    b, l, lv = carrot_shape(-1.5, -2.6, 0.55, 0.15, 0.7)
    carrot_c = b[0]
    bite = polar(lambda t: 0.35 + 0.04 * math.sin(7 * t), cx=0.6, cy=0.25, n=60)
    edge = keep([bite], carrot_c)
    paws = [ellipse(-0.05, -0.75, 0.42, 0.3, 24, rot=0.85), ellipse(-0.75, -1.45, 0.42, 0.3, 24, rot=0.85)]
    crumbs = [circle(1.3, -0.25, 0.08, 8), circle(1.55, 0.0, 0.07, 8), circle(1.45, -0.55, 0.06, 8)]
    carrot = hide(hide(b, bite) + l + edge, *paws) + hide(lv, carrot_c, *paws)
    out = hide([body], *hc, carrot_c, *paws, *lv) + hide(hs, carrot_c) + carrot + paws + hide(cheeks, carrot_c)
    return make("Bunny Munching a Carrot", out + crumbs, hh)


@design("easter_burrow_bunny", T)
def burrow_bunny(rng):
    hole = ellipse(0, -1.2, 1.7, 0.5, 80)
    front_reg = poly(*[(1.7 * math.cos(t), -1.2 + 0.5 * math.sin(t)) for t in [-math.pi * i / 40 for i in range(41)]], (-1.7, -4), (1.7, -4))
    mound = chain(cubic((-3.3, -1.0), (-2.3, -0.9), (-2.4, 0.0), (0, -0.0), 20), cubic((0, -0.0), (2.4, 0.0), (2.3, -0.9), (3.3, -1.0), 20))
    hs, hh, hc = bunny_head(0, 1.15, 0.85, ears=((-0.42, -0.9, 2.4), (0.42, 0.8, 2.5)))
    body = ellipse(0, -0.55, 1.0, 1.05, 60)
    paws = [ellipse(-0.75, -1.25, 0.35, 0.22, 20), ellipse(0.75, -1.25, 0.35, 0.22, 20)]
    out = hs + hide([body], *hc, front_reg, *paws) + paws + hide([hole], body, *paws) + hide([mound], *hc, body)
    dirt = [circle(-2.0, -1.3, 0.15, 10), circle(2.1, -1.35, 0.13, 10), circle(-1.9, -1.0, 0.1, 8)]
    eggs = []
    for x, y, r, k in [(-2.4, -2.3, 0.3, "zig"), (2.3, -2.4, -0.3, "wave"), (0.0, -2.6, 0.05, "line")]:
        E = egg(x, y, 0.42, 0.55, r)
        eggs += [E] + pattern(E, x, y, r, [(k, 0.0, 0.08, 0.22), ("line", 0.25, 0, 1)])
    fls = []
    for x in (-2.7, 2.7):
        f, c = flower(x, 0.6, 0.45)
        fls += f + hide([[(x, 0.25), (x, -0.95)]], *c)
    return make("Bunny Popping Out of Its Burrow", out + dirt + eggs + fls, hh)


@design("easter_dapper_bunny", T)
def dapper_bunny(rng):
    hs, hh, hc = bunny_head(0, 0.55, 1.15, ears=((-0.42, -0.95, 2.6), (0.42, 0.95, 2.6)))
    brim = ellipse(0, 1.42, 1.25, 0.24, 50)
    crown = poly((-0.75, 1.45), (-0.85, 2.85), (0.85, 2.85), (0.75, 1.45))
    band = keep([[(-1, 1.75), (1, 1.75)], [(-1, 2.0), (1, 2.0)]], crown)
    hat = [brim, crown] + band
    fl, fc = flower(0.55, 1.88, 0.3)
    hs = hide(hs, brim, crown)
    monocle = [circle(0.44, 0.8, 0.32, 30), quad((0.72, 0.65), (1.1, -0.2), (0.9, -0.9), 10)]
    bow = [poly((0, -0.75), (-0.7, -0.45), (-0.7, -1.15)), poly((0, -0.75), (0.7, -0.45), (0.7, -1.15)), circle(0, -0.75, 0.15, 12)]
    collar = [poly((-0.5, -0.6), (-0.95, -1.35), (-0.25, -1.05), closed=False), poly((0.5, -0.6), (0.95, -1.35), (0.25, -1.05), closed=False)]
    coat = [quad((-0.6, -0.5), (-2.2, -0.9), (-2.6, -2.9), 12), quad((0.6, -0.5), (2.2, -0.9), (2.6, -2.9), 12),
            [(-1.2, -0.85), (-0.2, -2.9)], [(1.2, -0.85), (0.2, -2.9)]]
    buttons = [circle(0, -1.85, 0.1, 10), circle(0, -2.4, 0.1, 10)]
    lapel_flower, lc = flower(-1.3, -1.35, 0.32)
    out = hs + hide(hat, *fc) + fl + hide([brim], crown)[:0] + hide(monocle, ) + hide(bow[:2], bow[2]) + [bow[2]] + hide(collar + coat, *bow, *lc) + buttons + lapel_flower
    out = [s for s in out if s is not None]
    hh = [hh[0], hh[1]]
    return make("Dapper Bunny in a Top Hat", hide(out, ) , hh)


@design("easter_chapel", T)
def chapel(rng):
    walls = rect(-1.7, -2.6, 1.7, 0.3)
    roof = poly((-2.1, 0.3), (0, 1.75), (2.1, 0.3))
    tower = rect(-0.5, 0.8, 0.5, 2.5)
    spire = poly((-0.65, 2.5), (0, 3.7), (0.65, 2.5))
    cross = [[(0, 3.7), (0, 4.3)], [(-0.22, 4.08), (0.22, 4.08)]]
    bell_win = chain([(-0.25, 1.6)], arc(0, 1.95, 0.25, math.pi, 0, 12)[0:], [(0.25, 1.6), (-0.25, 1.6)])
    bell = [chain(arc(0, 1.95, 0.13, 0, math.pi, 8), [(-0.17, 1.72), (0.17, 1.72), (0.13, 1.95)])]
    door = chain([(-0.45, -2.6), (-0.45, -1.5)], arc(0, -1.5, 0.45, math.pi, 0, 16), [(0.45, -2.6)])
    door_l = [[(0, -2.6), (0, -1.05)]]
    rose = [circle(0, -0.35, 0.38, 30)] + [[(0, -0.35), (0.38 * math.cos(a), -0.35 + 0.38 * math.sin(a))] for a in [k * TAU / 8 for k in range(8)]]
    wins = []
    for x in (-1.1, 1.1):
        wins += [chain([(x - 0.25, -1.9), (x - 0.25, -1.0)], arc(x, -1.0, 0.25, math.pi, 0, 10), [(x + 0.25, -1.9), (x - 0.25, -1.9)]), [(x, -1.9), (x, -0.75)]]
    sun = hide([circle(2.4, 2.5, 0.6, 40)] + [[(2.4 + 0.75 * math.cos(a), 2.5 + 0.75 * math.sin(a)), (2.4 + 1.05 * math.cos(a), 2.5 + 1.05 * math.sin(a))] for a in [k * TAU / 10 for k in range(10)]], )
    path = [quad((-0.45, -2.6), (-0.9, -3.0), (-1.5, -3.4), 8), quad((0.45, -2.6), (0.9, -3.0), (1.5, -3.4), 8)]
    tl = []
    for x in (-2.6, -2.1, 2.1, 2.6):
        sh, c = tulip(x, -1.95, 0.45)
        tl += sh + [[(x, -2.22), (x, -2.6)]]
    ground = [[(-3.0, -2.6), (-0.45, -2.6)], [(0.45, -2.6), (3.0, -2.6)]]
    out = [hide([walls], )[0]] + [roof] + hide([tower], roof) + [spire] + cross + [bell_win] + bell + [door] + door_l + rose + wins + sun + path + tl + ground
    return make("Little Chapel on Easter Morning", hide(out, ) )


@design("easter_pussy_willow", T)
def pussy_willow(rng):
    vase = chain([(-0.45, -0.3)], cubic((-0.45, -0.3), (-0.4, -0.9), (-1.4, -1.2), (-1.3, -2.2), 16), quad((-1.3, -2.2), (-1.2, -2.9), (0, -2.9), 10),
                 quad((0, -2.9), (1.2, -2.9), (1.3, -2.2), 10), cubic((1.3, -2.2), (1.4, -1.2), (0.4, -0.9), (0.45, -0.3), 16))
    lip = ellipse(0, -0.3, 0.6, 0.15, 30)
    branches = [cubic((-0.1, -0.3), (-0.3, 1.0), (-1.2, 2.0), (-1.9, 3.3), 40), cubic((0.0, -0.3), (0.0, 1.2), (0.2, 2.5), (0.2, 3.6), 40),
                cubic((0.1, -0.3), (0.4, 0.8), (1.4, 1.8), (2.1, 3.0), 40), cubic((-0.05, 0.6), (-0.8, 0.9), (-1.8, 1.0), (-2.5, 1.5), 30),
                cubic((0.05, 0.5), (0.9, 0.6), (1.8, 0.7), (2.6, 1.2), 30)]
    buds = []
    for br in branches:
        n = len(br) - 1
        for k, f in enumerate([0.3, 0.42, 0.54, 0.66, 0.78, 0.9, 1.0]):
            i = min(n, int(f * n))
            j = max(0, i - 1)
            a = math.atan2(br[i][1] - br[j][1], br[i][0] - br[j][0])
            side = 1 if k % 2 else -1
            off = a + side * 0.6 if f < 1.0 else a
            cx, cy = br[i][0] + 0.2 * math.cos(off), br[i][1] + 0.2 * math.sin(off)
            buds.append(ellipse(cx, cy, 0.28, 0.15, 18, rot=off))
    branches = hide(branches, *buds, lip, vase)
    bow = [lens((0.0, -0.8), (-0.85, -0.45), 0.42), lens((0.0, -0.8), (0.85, -0.45), 0.42), circle(0, -0.8, 0.12, 10)]
    tails = [poly((-0.08, -0.9), (-0.45, -1.6), (-0.2, -1.55), closed=False), poly((0.08, -0.9), (0.45, -1.6), (0.2, -1.55), closed=False)]
    vd = keep([wave(-2, 2, -2.2, 0.1, 6, 80)], vase)
    out = branches + buds + [hide([vase], *bow, *tails)][0] + [lip] + hide(bow[:2], bow[2]) + [bow[2]] + hide(tails, *bow) + vd
    return make("Pussy Willow Branches", out)


@design("easter_egg_carton", T)
def egg_carton(rng):
    base = [(-3.0, -1.2)]
    for cx in (-2.0, 0.0, 2.0):
        base += quad((cx - 1.0, -1.2), (cx, -2.0), (cx + 1.0, -1.2), 14)[1:]
    base += [(3.0, -2.5)]
    for cx in (2.0, 0.0, -2.0):
        base += quad((cx + 1.0, -2.5), (cx, -3.2), (cx - 1.0, -2.5), 14)[0 if cx == 2.0 else 1:]
    base += [(-3.0, -1.2)]
    divs = [[(-1.0, -1.2), (-1.0, -2.5)], [(1.0, -1.2), (1.0, -2.5)]]
    lid = [(-3.0, -0.9), (-2.85, 1.25)]
    for cx in (-1.9, 0.0, 1.9):
        lid += arc(cx, 1.25, 0.95, math.pi, 0, 16)[1:]
    lid += [(3.0, -0.9), (-3.0, -0.9)]
    lid_line = [(-2.75, 0.95), (2.75, 0.95)]
    kinds = [("zig", 0.0), ("wave", 0.1), ("scallop", 0.2), ("line", 0.0), ("zig", -0.1), ("wave", 0.25)]
    eggs, ecov = [], []
    for k, (x, y) in enumerate([(-1.9, 0.1), (0.0, 0.15), (1.9, 0.1), (-2.0, -0.85), (0.0, -0.8), (2.0, -0.85)]):
        E = egg(x, y, 0.68, 0.9)
        kind, yy = kinds[k]
        new = [E] + pattern(E, x, y, 0, [(kind, yy, 0.12, 0.3), ("line", yy + 0.35, 0, 1), ("line", yy - 0.35, 0, 1)])
        eggs = hide(eggs, E) + new
        ecov.append(E)
    out = hide([lid, lid_line], *ecov, base) + hide(eggs, base) + [base] + divs
    return make("Carton of Painted Eggs", out)


@design("easter_bunny_balloons", T)
def bunny_balloons(rng):
    hs, hh, hc = bunny_head(-0.6, -0.2, 0.7, ears=((-0.42, -0.8, 2.4), (0.42, 0.6, 2.5)))
    body = ellipse(-0.6, -1.85, 0.85, 0.95, 60)
    arm = tube(quad((-0.05, -1.4), (0.5, -1.0), (0.8, -0.6), 10), 0.3)
    paw = circle(0.85, -0.55, 0.2, 14)
    feet = [ellipse(-1.15, -2.8, 0.45, 0.2, 20), ellipse(-0.05, -2.8, 0.45, 0.2, 20)]
    out = hs + hide([body], *hc, *feet, arm) + feet + hide([arm], paw) + [paw]
    belly = keep([ellipse(-0.6, -1.95, 0.5, 0.6, 30)], body)
    bal = []
    bc = []
    for x, y, r, kind in [(-0.3, 2.3, 0.15, "zig"), (1.25, 2.1, -0.2, "wave"), (2.4, 1.0, -0.4, "scallop")]:
        E = egg(x, y, 0.62, 0.82, r)
        bot = (x + 0.82 * math.sin(r), y - 0.82 * math.cos(r))
        knot = poly(bot, (bot[0] - 0.12, bot[1] - 0.18), (bot[0] + 0.12, bot[1] - 0.18))
        string = quad((bot[0], bot[1] - 0.18), ((bot[0] + 0.85) / 2 + 0.2, (bot[1] - 0.55) / 2), (0.85, -0.4), 14)
        bal = hide(bal, E) + [E, knot, string] + pattern(E, x, y, r, [(kind, 0.0, 0.12, 0.3), ("line", 0.4, 0, 1)])
        bc.append(E)
    bal = hide(bal, *hc, paw)
    shines = [arc(x - 0.2, y + 0.2, 0.35, 1.8, 2.6, 6) for x, y in [(-0.3, 2.3), (1.25, 2.1), (2.4, 1.0)]][:0]
    return make("Bunny with Egg Balloons", out + belly + bal + [[(-2.2, -3.0), (1.6, -3.0)]], hh)


@design("easter_walking_egg", T)
def walking_egg(rng):
    w, h = 1.5, 1.95
    E = egg(0, 0.0, w, h)
    hole = [(w * math.cos(t) * (1 - 0.13 * math.sin(t)), h * math.sin(t)) for t in [math.pi * 0.25 + math.pi * 0.5 * i / 30 for i in range(31)]]
    crack = zigzag(-0.95, 0.95, 1.5, 0.15, 5)
    top_reg = poly(*crack, (2, 3), (-2, 3))
    shell = hide([E], top_reg) + [crack]
    ch_head = circle(0, 1.95, 0.7, 50)
    ch = hide([ch_head], poly(*crack, (2, -3), (-2, -3)))
    beak = poly((0.5, 2.0), (0.95, 1.9), (0.5, 1.75))
    tuft_ = [quad((0, 2.6), (-0.1, 3.0), (0.2, 3.05), 8), quad((0.1, 2.6), (0.35, 2.9), (0.55, 2.85), 8)]
    shell_cap = transform(chain(arc(0, 0, 0.75, 0.15, math.pi - 0.15, 20), zigzag(-0.72, 0.72, 0.15, 0.12, 4)[::-1]), -0.1, 2.55, rot=0.35)
    shell_cap.append(shell_cap[0])
    ch = hide(ch + tuft_, shell_cap)
    feet = []
    for x, dx in [(-0.55, -0.3), (0.55, 0.35)]:
        feet += [[(x, -1.9), (x + dx * 0.4, -2.55)],
                 [(x + dx * 0.4 - 0.4, -2.75), (x + dx * 0.4, -2.55), (x + dx * 0.4 + 0.45, -2.7)], [(x + dx * 0.4, -2.55), (x + dx * 0.4 + 0.1, -2.9)]]
    feet = hide(feet, E)
    wings = [lens((-1.35, 0.2), (-2.2, 0.8), 0.3), lens((1.35, 0.2), (2.2, 0.8), 0.3)]
    wings = hide(wings, E)
    holes = [ellipse(-1.25, 0.25, 0.25, 0.35, 16)[:0]]
    pat = pattern(E, 0, 0, 0, [("zig", 0.2, 0.15, 0.4), ("wave", -0.5, 0.1, 0.6)]) + spots(0, 0, 0, [(-0.5, -1.15), (0.0, -1.3), (0.5, -1.15)], 0.13)
    pat = hide(pat, top_reg)
    motion = [[(-2.6, -1.0), (-1.9, -1.0)], [(-2.8, -1.5), (-2.0, -1.5)], [(-2.6, -2.0), (-1.95, -2.0)]]
    return make("Walking Egg with Chick Feet", shell + ch + [beak] + [shell_cap] + feet + wings + pat + motion + [[(-3.0, -2.9), (3.0, -2.9)]], [eye(0.25, 2.1, 0.1)])
