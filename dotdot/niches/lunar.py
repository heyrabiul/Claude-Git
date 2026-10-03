"""Lunar New Year niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "lunar"


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


def path_len(s):
    return sum(math.dist(a, b) for a, b in zip(s, s[1:]))


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


def layered(*groups):
    """Each group is (strokes, cover_shapes); earlier groups are in FRONT."""
    out, covers = [], []
    for strokes, cov in groups:
        out += hide(strokes, *covers) if covers else list(strokes)
        covers += list(cov)
    return out


# ------------------------------------------------------------------ pieces

def spline(pts, closed=True, n=10):
    """Smooth curve through points; a point given as (x, y, 1) is a sharp corner."""
    P = [(p[0], p[1]) for p in pts]
    sharp = [len(p) > 2 for p in pts]
    m = len(P)
    out = []
    for i in (range(m) if closed else range(m - 1)):
        p1, p2 = P[i], P[(i + 1) % m]
        p0 = P[i - 1] if (closed or i > 0) else p1
        p3 = P[(i + 2) % m] if (closed or i + 2 < m) else p2
        if sharp[i]:
            p0 = p1
        if sharp[(i + 1) % m]:
            p3 = p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        seg = cubic(p1, c1, c2, p2, n)
        out += seg if not out else seg[1:]
    if closed:
        out[-1] = out[0]
    return out


def tf(strokes, dx=0.0, dy=0.0, s=1.0, rot=0.0, flip=False):
    out = []
    for st in strokes:
        if flip:
            st = [(-x, y) for x, y in st]
        out.append(transform(st, dx, dy, s, rot))
    return out


def crescent(cx, cy, r, rot=0.0, depth=0.45):
    outer = arc(cx, cy, r, rot - 1.15, rot + 1.15, 16)
    inner = quad(outer[-1], (cx + depth * r * math.cos(rot), cy + depth * r * math.sin(rot)), outer[0], 12)
    return chain(outer, inner[1:])


def blossom(cx, cy, r, rot=0.0, centre=True):
    """Five round petals (plum / peach blossom); returns (strokes, outline)."""
    petals = [circle(cx + 0.55 * r * math.cos(rot + math.pi / 2 + k * TAU / 5),
                     cy + 0.55 * r * math.sin(rot + math.pi / 2 + k * TAU / 5), 0.48 * r, 24) for k in range(5)]
    outline = union(*petals)
    out = list(outline)
    if centre:
        out.append(circle(cx, cy, 0.22 * r, 14))
    shape = max(outline, key=len)
    return out, [shape]


def coin(cx, cy, r, ring=True):
    out = [circle(cx, cy, r, 60), rect(cx - 0.22 * r, cy - 0.22 * r, cx + 0.22 * r, cy + 0.22 * r)]
    if ring:
        out.append(circle(cx, cy, 0.78 * r, 50))
        out.append(rect(cx - 0.36 * r, cy - 0.36 * r, cx + 0.36 * r, cy + 0.36 * r))
    return out


def tassel(x, y, L=1.0, w=0.35):
    """Knot + tassel hanging from (x, y)."""
    knot = poly((x, y), (x + 0.16, y - 0.16), (x, y - 0.32), (x - 0.16, y - 0.16))
    top = y - 0.32
    cap = rect(x - 0.13, top - 0.22, x + 0.13, top)
    t0 = top - 0.22
    fringe = poly((x - 0.13, t0), (x - w / 2, t0 - L), (x + w / 2, t0 - L), (x + 0.13, t0), closed=False)
    strands = [[(x + dx * 0.5, t0 - 0.1), (x + dx, t0 - L)] for dx in (-w / 4, w / 4)]
    return [knot, cap, fringe] + strands


def lantern(cx, cy, rx, ry, ribs=3, tas=True, tl=1.0):
    """Round red lantern; returns (strokes, cover)."""
    body = ellipse(cx, cy, rx, ry, 90)
    out = [body]
    for k in range(1, ribs + 1):
        f = k / (ribs + 1)
        for sg in (-1, 1):
            out.append([(cx + sg * f * rx * math.cos(t), cy + ry * math.sin(t)) for t in
                        [-math.pi / 2 + math.pi * i / 30 for i in range(31)]])
    cw = 0.42 * rx
    ch = 0.16 * ry + 0.06
    top = rect(cx - cw, cy + ry - 0.06, cx + cw, cy + ry + ch)
    bot = rect(cx - cw, cy - ry - ch, cx + cw, cy - ry + 0.06)
    out = hide(out, top, bot) + [top, bot]
    if tas:
        out += tassel(cx, cy - ry - ch, tl, 0.5 * cw + 0.15)
    return out, [body, top, bot]


def flame_cloud(cx, cy, s=1.0, flip=False):
    """Auspicious cloud scroll (xiangyun)."""
    pts = chain(arc(0.0, 0.0, 0.5, math.pi, 2.2 * math.pi, 18),
                arc(0.55, 0.2, 0.42, math.pi * 1.25, 2.6 * math.pi, 18)[1:])
    base = [[(-0.5, 0.0), (-0.5, -0.35), (1.05, -0.35)]]
    curl = [spiral(0.0, 0.0, 0.05, 0.3, 1.0, 30), spiral(0.55, 0.2, 0.05, 0.25, 1.0, 26)]
    return tf([pts] + base + curl, cx, cy, s, flip=flip)


def roof(x0, x1, y, h, tiles=True, ridge=True):
    """Chinese tiled roof with up-turned eaves; returns (strokes, cover)."""
    w = x1 - x0
    eave = chain(quad((x0 - 0.35, y + 0.35), (x0 - 0.05, y), (x0 + 0.35, y), 10), [(x1 - 0.35, y)],
                 quad((x1 - 0.35, y), (x1 + 0.05, y), (x1 + 0.35, y + 0.35), 10))
    top_l = (x0 + 0.18 * w, y + h)
    top_r = (x1 - 0.18 * w, y + h)
    side_l = quad((x0 - 0.35, y + 0.35), (x0 + 0.12 * w, y + 0.35 * h), top_l, 12)
    side_r = quad(top_r, (x1 - 0.12 * w, y + 0.35 * h), (x1 + 0.35, y + 0.35), 12)
    outline = chain(eave, list(reversed(side_r)), [top_l], list(reversed(side_l)))
    out = [outline]
    if ridge:
        rid = chain(quad((top_l[0] - 0.3, y + h + 0.3), (top_l[0] - 0.05, y + h + 0.12), (top_l[0] + 0.1, y + h + 0.12), 6),
                    [(top_r[0] - 0.1, y + h + 0.12)],
                    quad((top_r[0] - 0.1, y + h + 0.12), (top_r[0] + 0.05, y + h + 0.12), (top_r[0] + 0.3, y + h + 0.3), 6))
        out.append(chain([(top_l[0], y + h)], rid, [(top_r[0], y + h)]))
    if tiles:
        n = max(3, int(w / 0.32))
        lines = [[(x0 + w * (k + 0.5) / n, y - 0.1), (x0 + w * (k + 0.5) / n + (x0 + w * (k + 0.5) / n - (x0 + x1) / 2) * 0.25, y + h + 0.1)]
                 for k in range(n)]
        out += keep(lines, outline)
    return out, [outline]


def offset(cl, d):
    """Points of a centre line shifted sideways by d (or d(t))."""
    df = d if callable(d) else (lambda t: d)
    n = len(cl)
    out = []
    for i, (x, y) in enumerate(cl):
        a, b = cl[max(0, i - 1)], cl[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        w = df(i / (n - 1))
        out.append((x - dy / L * w, y + dx / L * w))
    return out


def dragon_head(s=1.0):
    """Festival dragon head facing right, neck at the origin; returns (strokes, cover)."""
    head = spline([(0, 0.5, 1), (0.35, 0.85), (0.85, 0.9), (1.3, 0.72), (1.65, 0.62, 1), (1.6, 0.35), (1.15, 0.2, 1),
                   (1.55, -0.1, 1), (1.4, -0.35), (0.7, -0.45), (0.0, -0.4, 1)])
    teeth = zigzag(1.18, 1.5, 0.12, 0.07, 3)
    horns = [tube(cubic((0.45, 0.85), (0.3, 1.3), (-0.1, 1.5), (-0.5, 1.55), 14), lambda t: 0.22 * (1 - t) + 0.04),
             tube(cubic((0.75, 0.88), (0.7, 1.35), (0.45, 1.65), (0.15, 1.8), 14), lambda t: 0.22 * (1 - t) + 0.04)]
    brow = quad((0.55, 0.78), (0.85, 0.95), (1.1, 0.75), 8)
    eye_ = circle(0.85, 0.6, 0.15, 16)
    whisk = [cubic((1.55, 0.5), (2.0, 0.6), (2.0, 1.1), (2.4, 1.1), 16), cubic((1.4, -0.3), (1.9, -0.5), (2.0, -0.9), (2.4, -0.8), 16)]
    beard = poly((0.4, -0.42), (0.55, -0.85), (0.75, -0.45), (0.9, -0.8), (1.05, -0.42), closed=False)
    nose = circle(1.45, 0.62, 0.08, 10)
    out = layered((hide([head], *horns[:0]) + [teeth, brow, eye_, nose], [head]), (horns + whisk + [beard], horns))
    return tf(out, s=s), tf([head], s=s)


@design("lunar_dragon_dance", T)
def dragon_dance(rng):
    xs = [-3.0 + 4.5 * i / 70 for i in range(71)]
    cl = [(x, 1.0 + 0.5 * math.sin(1.7 * x + 0.9)) for x in xs]
    wf = lambda t: 0.35 + 0.35 * t
    body = tube(cl, wf)
    fin = []
    for i in range(2, 69, 3):
        a = offset(cl, lambda t: wf(t) / 2)[i]
        b = offset(cl, lambda t: wf(t) / 2 + 0.25)[i + 1]
        c = offset(cl, lambda t: wf(t) / 2)[min(70, i + 3)]
        fin += [a, b, c]
    fin = [fin]
    belly = [offset(cl, lambda t: -wf(t) * 0.18)[3:-2]]
    bands = [[offset(cl, lambda t: wf(t) / 2)[i], offset(cl, lambda t: -wf(t) / 2)[i]] for i in range(10, 70, 12)]
    hx, hy = cl[-1]
    hs, hc = dragon_head(1.25)
    hs = tf(hs, hx - 0.05, hy - 0.15)
    hc = tf(hc, hx - 0.05, hy - 0.15)
    tail = poly((-3.0, 1.0 + 0.5 * math.sin(-5.1 + 0.9) + 0.15), (-3.6, 1.6), (-3.3, 1.0), (-3.7, 0.6), (-3.0, 0.75), closed=False)
    dragon = layered((hs, hc), ([body] + fin + belly + bands + [tail], [body]))
    # performers holding poles
    people, poles = [], []
    for k, px in enumerate([-2.3, -0.75, 0.8]):
        i = min(range(71), key=lambda j: abs(cl[j][0] - px))
        by = cl[i][1] - wf(i / 70) / 2
        poles.append([(px, by), (px, -0.45)])
        people += performer(px, -0.45, k % 2 == 0)
    pearl = circle(3.3, 0.45, 0.45, 30)
    pearl_d = [spiral(3.3, 0.45, 0.05, 0.32, 1.3, 40)] + [[(3.3 + 0.55 * math.cos(a), 0.45 + 0.55 * math.sin(a)), (3.3 + 0.8 * math.cos(a), 0.45 + 0.8 * math.sin(a))] for a in (0.4, 1.2, 2.0, 2.8)]
    poles.append([(3.3, 0.0), (3.3, -0.45)])
    people += performer(3.3, -0.45, True)
    ground = [[(-3.8, -3.05), (3.9, -3.05)]]
    return make("Dragon Dance Parade", hide(dragon, pearl) + [pearl] + pearl_d + hide(poles, *[]) + people + ground)


def performer(x, hy, stride):
    """Little dancer holding a pole overhead, hands at (x, hy)."""
    head = circle(x, hy - 0.62, 0.22, 20)
    hair = arc(x, hy - 0.62, 0.22, 0.2, math.pi - 0.2, 10)
    tunic = spline([(x - 0.3, hy - 0.92), (x + 0.3, hy - 0.92), (x + 0.38, hy - 1.15, 1), (x + 0.34, hy - 1.8, 1),
                    (x - 0.34, hy - 1.8, 1), (x - 0.38, hy - 1.15, 1)])
    belt = [[(x - 0.36, hy - 1.5), (x + 0.36, hy - 1.5)]]
    arms = [tube([(x - 0.33, hy - 1.0), (x - 0.5, hy - 0.55), (x - 0.06, hy - 0.05)], 0.17),
            tube([(x + 0.33, hy - 1.0), (x + 0.5, hy - 0.55), (x + 0.06, hy + 0.2)], 0.17)]
    d = 0.12 if stride else -0.05
    legs = [tube([(x - 0.18, hy - 1.8), (x - 0.5 - d, hy - 2.15), (x - 0.45 - d, hy - 2.5)], 0.22),
            tube([(x + 0.18, hy - 1.8), (x + 0.5 - d, hy - 2.15), (x + 0.45 - d, hy - 2.5)], 0.22)]
    shoes = [ellipse(x - 0.55 - d, hy - 2.6, 0.24, 0.1, 14), ellipse(x + 0.55 - d, hy - 2.6, 0.24, 0.1, 14)]
    return layered((arms, arms), ([head, hair, tunic] + belt, [head, tunic]), (legs + shoes, []))


@design("lunar_lion_head", T)
def lion_head(rng):
    head = [((2.5 + 0.13 * abs(math.cos(11 * t))) * math.cos(t), 0.2 + (2.2 + 0.13 * abs(math.cos(11 * t))) * math.sin(t))
            for t in [TAU * i / 400 for i in range(401)]]
    face = ellipse(0, 0.15, 2.0, 1.75, 120)
    mirror_ = [circle(0, 1.35, 0.32, 24), circle(0, 1.35, 0.18, 16)]
    horn = spline([(-0.25, 1.7), (-0.2, 2.45), (0, 2.75, 1), (0.2, 2.45), (0.25, 1.7)], closed=False)
    eyes_ = [circle(sg * 0.85, 0.5, 0.45, 40) for sg in (-1, 1)]
    lids = [arc(sg * 0.85, 0.5, 0.62, 0.3, math.pi - 0.3, 20) for sg in (-1, 1)]
    lashes = [[(sg * 0.85 + 0.62 * math.cos(a), 0.5 + 0.62 * math.sin(a)), (sg * 0.85 + 0.85 * math.cos(a), 0.5 + 0.85 * math.sin(a))]
              for sg in (-1, 1) for a in (0.7, 1.2, 1.7, 2.2)]
    nose = ellipse(0, -0.25, 0.5, 0.32, 40)
    nostrils = [circle(-0.2, -0.3, 0.08, 10), circle(0.2, -0.3, 0.08, 10)]
    mouth = chain([(-1.5, -0.75)], quad((-1.5, -0.75), (0, -0.55), (1.5, -0.75), 20), cubic((1.5, -0.75), (1.4, -2.0), (-1.4, -2.0), (-1.5, -0.75), 30))
    teeth = zigzag(-1.2, 1.2, -0.88, 0.12, 7)
    tongue = chain(arc(0, -1.75, 0.55, 0.15, math.pi - 0.15, 16))
    ears = [lens((sg * 2.25, 1.05), (sg * 3.1, 1.8), 0.45) for sg in (-1, 1)]
    cheeks = [crescent(sg * 1.45, -0.25, 0.32, math.pi / 2 - sg * 0.6) for sg in (-1, 1)]
    beard = [cubic((x, -2.0), (x - 0.15, -2.4), (x + 0.15, -2.6), (x, -3.0), 12) for x in (-0.8, -0.4, 0.0, 0.4, 0.8)]
    beard = hide(beard, mouth)
    out = layered(([face] + mirror_ + eyes_ + lids + lashes + [nose] + nostrils + [mouth, teeth, tongue] + cheeks, [face]),
                  ([head, horn], [head]), (ears, ears)) + beard
    return make("Lion Dance Head", out, [eye(sg * 0.85, 0.45, 0.18) for sg in (-1, 1)])


def lion_side(r=0.0):
    """Dancing lion seen from the side, facing right, feet at y=0; r raises the head."""
    hx, hy = 1.25, 2.05 + r
    head = [(hx + (1.25 + 0.09 * abs(math.cos(9 * t))) * math.cos(t), hy + (1.0 + 0.09 * abs(math.cos(9 * t))) * math.sin(t))
            for t in [TAU * i / 300 for i in range(301)]]
    face = ellipse(hx + 0.2, hy - 0.05, 0.95, 0.75, 60)
    eye_ = circle(hx + 0.35, hy + 0.25, 0.26, 20)
    lid = arc(hx + 0.35, hy + 0.25, 0.4, 0.2, 2.9, 14)
    horn = spline([(hx - 0.2, hy + 0.95), (hx - 0.15, hy + 1.4), (hx + 0.0, hy + 1.65, 1), (hx + 0.15, hy + 1.4), (hx + 0.2, hy + 0.98)], closed=False)
    mirror_ = [circle(hx - 0.45, hy + 0.3, 0.2, 16)]
    mouth = chain([(hx + 0.15, hy - 0.35)], quad((hx + 0.15, hy - 0.35), (hx + 0.8, hy - 0.15), (hx + 1.35, hy - 0.3), 10),
                  quad((hx + 1.35, hy - 0.3), (hx + 1.0, hy - 0.95), (hx + 0.15, hy - 0.35), 12))
    teeth = zigzag(hx + 0.45, hx + 1.1, hy - 0.33, 0.06, 3)
    nose = circle(hx + 1.05, hy + 0.0, 0.12, 12)
    teeth_s = [teeth]
    fur = []
    beard = [cubic((x, hy - 0.95), (x - 0.15, hy - 1.3), (x + 0.15, hy - 1.45), (x, hy - 1.75), 10) for x in (hx - 0.2, hx + 0.2, hx + 0.6)]
    body = spline([(0.3, 2.0 + r), (-0.6, 2.05), (-1.6, 1.75), (-1.95, 1.1), (-1.85, 0.75, 1), (0.8, 0.75, 1), (0.8, 1.5)])
    fringe = zigzag(-1.75, 0.7, 0.85, 0.08, 8)
    scales = keep([arc(x, y, 0.32, math.pi, TAU, 10) for x in (-1.3, -0.7, -0.1) for y in (1.35, 1.75)], body)
    legs = []
    for x0 in (-1.5, -0.95, 0.0, 0.5):
        legs.append(leg(x0, x0 + 0.4, 0.78, 0.15))
        legs.append(ellipse(x0 + 0.32, 0.08, 0.34, 0.13, 16))
    tail = spline([(-1.85, 1.35), (-2.4, 1.85), (-2.6, 1.5, 1), (-2.3, 1.25), (-2.5, 0.95, 1), (-1.9, 1.0)], closed=False)
    return layered(([face, eye_, lid, mouth, teeth, nose] + mirror_, [face]), ([head], [head]), (beard, []), ([horn], [chain(horn, [horn[0]])]),
                   ([body, fringe] + scales + [tail], [body]), (legs, []))


@design("lunar_lion_pair", T)
def lion_pair(rng):
    a = tf(lion_side(0.7), -2.0, -2.4, 0.72)
    b = tf(lion_side(0.0), 2.0, -2.4, 0.72, flip=True)
    ball = [circle(0, 2.6, 0.42, 30), [(-0.42, 2.6), (0.42, 2.6)], [(0, 2.18), (0, 3.02)]]
    ribbons = [cubic((0.0, 2.18), (-0.3, 1.8), (0.3, 1.5), (0.0, 1.1), 14)]
    ground = [[(-3.6, -2.45), (3.6, -2.45)]]
    return make("Pair of Dancing Lions", a + b + ball + ribbons + ground,
                [eye(-2.0 + 1.6 * 0.72, -2.4 + 3.0 * 0.72, 0.1), eye(2.0 - 1.6 * 0.72, -2.4 + 2.3 * 0.72, 0.1)])


@design("lunar_lantern_string", T)
def lantern_string(rng):
    rope = quad((-3.6, 2.6), (0, 1.0), (3.6, 2.6), 60)
    out = [rope]
    for k, x in enumerate([-2.6, -1.3, 0.0, 1.3, 2.6]):
        ry_ = (1 - ((x / 3.6) ** 2)) * 0.8
        y_rope = 2.6 - 0.8 * (1 - (x / 3.6) ** 2) * 1.0
        drop = 0.45 + 0.35 * (k % 2)
        cy = y_rope - drop - 0.6
        s, _ = lantern(x, cy, 0.55, 0.48, 2, True, 0.7)
        out += s + [[(x, y_rope), (x, cy + 0.48 + 0.14)]]
    bows = [poly((x, 2.6), (x - 0.25, 2.8), (x - 0.25, 2.4)) for x in (-3.6,)] + [poly((3.6, 2.6), (3.85, 2.8), (3.85, 2.4))]
    return make("String of Red Lanterns", out + bows)


@design("lunar_round_lantern", T)
def round_lantern(rng):
    s, cov = lantern(0, 0.3, 2.3, 1.85, 3, True, 1.3)
    medal = circle(0, 0.3, 0.75, 50)
    bs, bc = blossom(0, 0.3, 0.6)
    s = hide(s, medal) + [medal] + bs
    hook = [[(0, 2.33), (0, 3.0)], arc(0, 3.15, 0.15, -math.pi / 2, 1.2 * math.pi, 12)]
    return make("Round Red Lantern with Tassel", s + hook)


@design("lunar_lantern_festival", T)
def lantern_festival(rng):
    r1, c1 = roof(-3.4, -0.6, -0.4, 0.9)
    r2, c2 = roof(0.4, 3.4, -0.9, 0.9)
    w1 = [[(-3.0, -0.4), (-3.0, -3.0)], [(-1.0, -0.4), (-1.0, -3.0)]] + [rect(-2.6, -1.6, -2.0, -0.9), rect(-1.7, -3.0, -1.2, -1.7)]
    w2 = [[(0.8, -0.9), (0.8, -3.0)], [(3.0, -0.9), (3.0, -3.0)]] + [rect(1.4, -3.0, 2.2, -1.7), [(1.8, -3.0), (1.8, -1.7)], rect(2.4, -2.0, 2.8, -1.4)]
    houses = layered((r1, c1), (r2, c2), (w1 + w2, []))
    rope = quad((-3.0, 0.95), (-0.2, 0.0), (2.9, 0.2), 40)
    out = houses + [rope]
    for x in (-2.3, -1.3, -0.3, 0.7, 1.8):
        t = min(range(41), key=lambda j: abs(rope[j][0] - x))
        y = rope[t][1]
        ls, lc = lantern(x, y - 0.45, 0.32, 0.28, 1, True, 0.25)
        out = hide(out, *lc) + ls + [[(x, y), (x, y - 0.17 + 0.0)]]
    moon = circle(2.2, 2.4, 0.75, 60)
    floating = []
    for x, y, sc in [(-2.6, 2.6, 0.32), (-1.3, 2.0, 0.28), (-0.1, 2.75, 0.3), (0.9, 1.7, 0.26)]:
        ls, _ = lantern(x, y, sc * 1.1, sc, 1, False)
        floating += ls
    return make("Lantern Festival Night", out + [moon] + floating + stars_at([(-3.2, 1.4), (1.3, 3.0), (3.3, 1.2)]))


def stars_at(pts, r=0.15):
    return [star(x, y, r, 5, 0.45) for x, y in pts]


@design("lunar_palace_lantern", T)
def palace_lantern(rng):
    out = []
    # crown and base: hexagonal frame seen from the front
    crown = poly((-1.9, 1.9), (1.9, 1.9), (1.4, 2.5), (-1.4, 2.5))
    crown_t = poly((-1.0, 2.5), (1.0, 2.5), (0.6, 2.85), (-0.6, 2.85))
    base = poly((-1.9, -1.9), (1.9, -1.9), (1.4, -2.4), (-1.4, -2.4))
    hooks = [quad((-1.9, 1.9), (-2.3, 2.0), (-2.4, 2.4), 8), quad((1.9, 1.9), (2.3, 2.0), (2.4, 2.4), 8),
             quad((-1.9, -1.9), (-2.3, -1.8), (-2.4, -1.4), 8), quad((1.9, -1.9), (2.3, -1.8), (2.4, -1.4), 8)]
    panels = [rect(-1.0, -1.9, 1.0, 1.9), rect(-1.75, -1.9, -1.0, 1.9), rect(1.0, -1.9, 1.75, 1.9)]
    inner = [rect(-0.8, -1.6, 0.8, 1.6), rect(-1.58, -1.6, -1.17, 1.6), rect(1.17, -1.6, 1.58, 1.6)]
    bs, _ = blossom(0, 0.55, 0.55)
    bs2, _ = blossom(-0.25, -0.75, 0.38, 0.4)
    branch = [cubic((0.7, -1.4), (0.2, -1.0), (0.4, 0.0), (-0.2, 0.2), 16)]
    branch = hide(branch, *[s for s in bs + bs2 if len(s) > 20])
    side_dec = [lens((x, -0.8), (x, 0.8), 0.35) for x in (-1.375, 1.375)]
    hang = [[(0, 2.85), (0, 3.4)]]
    tass = []
    for x in (-2.4, 2.4):
        tass += tassel(x, -1.4, 0.8, 0.35)
    tass += tassel(0, -2.4, 0.6, 0.4)
    top_tass = []
    for x in (-2.4, 2.4):
        top_tass += [[(x, 2.4), (x, 2.0)]] + tassel(x, 2.0, 0.5, 0.3)
    out = [crown, crown_t, base] + hooks + panels + inner + bs + bs2 + branch + side_dec + hang + tass
    return make("Hexagonal Palace Lantern", hide(out, *[]) )


def sky_lantern(cx, cy, s):
    body = chain([(-0.55, -0.9)], quad((-0.55, -0.9), (-0.8, 0.4), (-0.6, 0.9), 12), quad((-0.6, 0.9), (0, 1.15), (0.6, 0.9), 10),
                 quad((0.6, 0.9), (0.8, 0.4), (0.55, -0.9), 12))
    rim = ellipse(0, -0.9, 0.55, 0.14, 24)
    seams = [quad((-0.2, -0.95), (-0.28, 0.3), (-0.2, 1.08), 10), quad((0.2, -0.95), (0.28, 0.3), (0.2, 1.08), 10)]
    fl = lens((0, -1.05), (0, -0.55), 0.35)
    return tf([body, rim, fl] + seams, cx, cy, s)


@design("lunar_sky_lanterns", T)
def sky_lanterns(rng):
    out = []
    for x, y, s in [(-1.6, 1.0, 1.25), (1.0, 1.8, 1.0), (2.4, -0.2, 0.8), (-0.2, -0.6, 0.7), (-2.9, 2.6, 0.5), (0.0, 3.2, 0.45), (2.9, 2.9, 0.4)]:
        out += sky_lantern(x, y, s)
    hills = [chain(quad((-3.6, -2.2), (-2.4, -1.2), (-1.0, -2.0), 20), quad((-1.0, -2.0), (0.6, -1.1), (2.0, -2.0), 20),
                   quad((2.0, -2.0), (3.0, -1.5), (3.6, -1.9), 10))]
    water = [wave(-3.6, 3.6, -2.7, 0.06, 7, 140), wave(-3.0, 3.0, -3.2, 0.06, 6, 120)]
    pag = rect(-2.0, -1.75, -1.6, -1.35)
    return make("Sky Lanterns Rising", out + hills + water + stars_at([(-3.2, 0.3), (1.8, 3.4), (3.3, 1.2), (-0.9, 3.0)]))


def envelope(cx, cy, w, h, rot, motif=0):
    o = rect(-w / 2, -h / 2, w / 2, h / 2)
    flap = [[(-w / 2, h / 2 - 0.05), (0, h / 2 - 0.55 * w / 2 - 0.15), (w / 2, h / 2 - 0.05)]]
    c = circle(0, h * 0.02, 0.33 * w, 40)
    if motif == 0:
        m, _ = blossom(0, h * 0.02, 0.25 * w)
    else:
        m = coin(0, h * 0.02, 0.24 * w, False)
    border = rrect(-w / 2 + 0.14, -h / 2 + 0.14, w / 2 - 0.14, h / 2 - 0.14, 0.05)
    clouds = flame_cloud(0, -h / 2 + 0.55, 0.35)
    parts = [o] + hide(flap, c) + [c] + m + hide([border], c) + hide(clouds, c)
    return tf(parts, cx, cy, 1, rot), transform(o, cx, cy, 1, rot)


@design("lunar_red_envelopes", T)
def red_envelopes(rng):
    a, ac = envelope(-0.95, 0.3, 2.3, 3.6, 0.22, 1)
    b, bc = envelope(0.95, 0.0, 2.3, 3.6, -0.15, 0)
    coins = []
    covers = []
    for x, y, r in [(-0.6, -2.6, 0.55), (0.6, -2.75, 0.5), (1.8, -2.45, 0.45)]:
        c = coin(x, y, r)
        coins += hide(c, *covers)
        covers.append(circle(x, y, r, 40))
    return make("Red Envelopes", layered((coins, covers), (b, [bc]), (a, [ac])))


# dropped: the Fourth of July book has firecrackers
def firecrackers(rng):
    out, covers = [], []
    ys = [1.6 - 0.42 * k for k in range(10)]
    for k, y in enumerate(reversed(ys)):
        for sg in (-1, 1):
            ang = sg * 0.55 - math.pi / 2 * 0 + (0 if sg > 0 else math.pi)
            ca, sa = math.cos(-0.45 * 1), 0
            L, w = 1.15, 0.36
            body = rrect(0.05, -w / 2, L, w / 2, 0.06)
            bands = [[(0.3, -w / 2), (0.3, w / 2)], [(L - 0.25, -w / 2), (L - 0.25, w / 2)]]
            parts = [body] + bands
            rot = -0.5 if sg > 0 else math.pi + 0.5
            parts = tf(parts, 0, y, 1, rot)
            out += hide(parts, *covers)
            covers.append(parts[0])
    rope = hide([[(0, 2.0), (0, -2.4)]], *covers)
    knot = poly((0, 2.6), (0.4, 2.2), (0, 1.8), (-0.4, 2.2))
    loop = arc(0, 2.9, 0.3, -math.pi / 2 + 0.6, 1.5 * math.pi - 0.6, 14)
    inner_k = poly((0, 2.4), (0.2, 2.2), (0, 2.0), (-0.2, 2.2))
    bang = []
    for cx, cy, r in [(0.3, -2.9, 0.55), (-1.1, -2.5, 0.35), (1.3, -2.3, 0.3)]:
        bang.append(star(cx, cy, r, 8, 0.5))
    sparks = [[(0.3 + 0.75 * math.cos(a), -2.9 + 0.75 * math.sin(a)), (0.3 + 1.0 * math.cos(a), -2.9 + 1.0 * math.sin(a))]
              for a in (0.2, 0.9, 2.3, 3.0, 3.7)]
    return make("Hanging Firecracker String", out + hide(rope, knot) + [knot, inner_k, loop] + bang + sparks)


def burst(cx, cy, r, k=12, dots=True):
    out = []
    for i in range(k):
        a = TAU * i / k
        out.append([(cx + 0.3 * r * math.cos(a), cy + 0.3 * r * math.sin(a)), (cx + r * math.cos(a), cy + r * math.sin(a))])
        if dots:
            out.append(circle(cx + 1.15 * r * math.cos(a), cy + 1.15 * r * math.sin(a), 0.07 * r + 0.02, 10))
    return out


@design("lunar_fireworks_rooftops", T)
def fireworks_rooftops(rng):
    r1, c1 = roof(-3.4, 0.2, -1.4, 1.1)
    r2, c2 = roof(0.9, 3.4, -0.8, 1.0)
    walls = [[(-3.0, -1.4), (-3.0, -3.0)], [(-0.2, -1.4), (-0.2, -3.0)], [(1.2, -0.8), (1.2, -3.0)], [(3.1, -0.8), (3.1, -3.0)],
             rect(-2.4, -3.0, -1.6, -2.0), rect(-1.2, -2.4, -0.6, -1.9), rect(1.8, -2.2, 2.6, -1.5)]
    lan = []
    for x, y in [(-2.9, -1.4), (-0.3, -1.4), (1.3, -0.8), (3.0, -0.8)]:
        ls, _ = lantern(x, y - 0.55, 0.22, 0.2, 1, True, 0.2)
        lan += ls + [[(x, y), (x, y - 0.33)]]
    houses = layered((r1, c1), (r2, c2), (walls, []))
    fw = burst(-1.6, 1.8, 1.1, 14) + burst(1.5, 2.3, 0.9, 12) + burst(2.6, 0.6, 0.55, 10, False) + burst(-3.0, 0.4, 0.5, 8, False)
    trails = [quad((-1.4, -0.5), (-1.7, 0.2), (-1.6, 0.5), 10)]
    return make("Fireworks over Tiled Rooftops", houses + lan + fw + trails)


def branchy(pts, w0, w1):
    cl = spline(pts, closed=False, n=12)
    return tube(cl, lambda t: w0 + (w1 - w0) * t, cap=False), cl


@design("lunar_plum_blossom", T)
def plum_blossom(rng):
    main, mcl = branchy([(-3.4, -2.6), (-2.2, -1.4), (-1.4, -1.6), (-0.2, -0.3), (0.6, 0.1), (1.6, 1.4), (2.8, 2.2)], 0.45, 0.08)
    b1, _ = branchy([(-1.4, -1.55), (-1.6, -0.4), (-1.0, 0.6), (-1.3, 1.8)], 0.22, 0.05)
    b2, _ = branchy([(0.6, 0.1), (1.6, -0.4), (2.6, -0.3), (3.2, -1.0)], 0.2, 0.05)
    b3, _ = branchy([(-2.2, -1.4), (-2.9, -0.6), (-2.8, 0.4)], 0.18, 0.05)
    flowers, covers = [], []
    for x, y, r, a in [(-1.0, 0.65, 0.55, 0.2), (0.0, -0.1, 0.6, -0.3), (1.65, 1.35, 0.55, 0.5), (2.6, -0.3, 0.5, 0.0),
                       (-2.85, 0.35, 0.45, 0.3), (-1.3, 1.85, 0.42, 0.1), (1.2, -0.25, 0.4, 0.8), (2.75, 2.15, 0.38, 0.1)]:
        fs, fc = blossom(x, y, r, a)
        stam = [[(x + 0.12 * r * math.cos(t), y + 0.12 * r * math.sin(t)), (x + 0.45 * r * math.cos(t), y + 0.45 * r * math.sin(t))] for t in (0.3, 1.5, 2.7, 3.9, 5.1)]
        flowers += hide(fs + stam, *covers)
        covers += fc
    buds = []
    for x, y in [(-0.5, -0.85), (0.9, 0.55), (2.2, 1.9), (-2.4, -0.6), (3.15, -0.95), (-1.55, -0.1)]:
        buds.append(circle(x, y, 0.17, 14))
        covers.append(circle(x, y, 0.17, 14))
    moon = circle(1.4, 2.0, 1.4, 90)
    stems = hide([main, b1, b2, b3], *covers)
    return make("Plum Blossom Branch", flowers + buds + stems + hide([moon], *covers, main, b1, b2, b3))


def leaf(p0, p1, bulge=0.32, vein=True):
    l = lens(p0, p1, bulge)
    return [l, [p0, ((p0[0] + 3 * p1[0]) / 4, (p0[1] + 3 * p1[1]) / 4)]] if vein else [l]


def mandarin(cx, cy, r, top=True):
    body = ellipse(cx, cy, r, 0.88 * r, 70)
    det = []
    if top:
        det = [star(cx, cy + 0.6 * r, 0.16 * r + 0.05, 5, 0.45)]
    shine = [arc(cx, cy, 0.75 * r, 1.9, 2.6, 8)]
    return [body] + det + shine, [body]


@design("lunar_mandarins", T)
def mandarins(rng):
    items = []
    for cx, cy, r in [(-1.2, -1.2, 1.15), (1.15, -1.25, 1.1), (0.0, 0.35, 1.15)]:
        items.append(mandarin(cx, cy, r))
    out = layered(items[2], items[0], items[1])
    lv = leaf((0.1, 1.3), (1.6, 2.4), 0.3) + leaf((-0.1, 1.3), (-1.7, 2.0), 0.3) + leaf((-1.6, -0.3), (-2.9, 0.4), 0.3)
    stem = [[(0.0, 1.25), (0.05, 1.5)]]
    plate = ellipse(0, -2.35, 3.2, 0.55, 90)
    plate_in = ellipse(0, -2.3, 2.5, 0.32, 80)
    covers = [items[0][1][0], items[1][1][0], items[2][1][0]]
    return make("Mandarin Oranges with Leaves", out + hide(lv, *covers) + stem + hide([plate, plate_in], *covers))


@design("lunar_kumquat_tree", T)
def kumquat_tree(rng):
    pot = chain([(-1.5, -1.2)], quad((-1.6, -2.6), (-1.0, -3.0), (0, -3.0), 12), quad((0, -3.0), (1.0, -3.0), (1.6, -2.6), 12)[1:], [(1.5, -1.2)])
    rim = rrect(-1.75, -1.25, 1.75, -0.95, 0.1)
    potband = keep([wave(-2, 2, -2.0, 0.12, 4, 80)], chain(pot, [pot[0]]))
    feet = [rect(-1.0, -3.2, -0.6, -3.0), rect(0.6, -3.2, 1.0, -3.0)]
    trunk = [[(-0.15, -0.95), (-0.25, 0.2)], [(0.15, -0.95), (0.25, 0.2)]]
    blobs = [circle(x, y, r, 40) for x, y, r in [(-1.3, 0.9, 0.95), (-0.4, 1.7, 1.0), (0.8, 1.6, 0.95), (1.4, 0.7, 0.85), (0.1, 0.6, 0.9)]]
    canopy = union(*blobs)
    fruits, covers = [], []
    for x, y in [(-1.6, 0.6), (-0.9, 1.3), (-0.2, 2.2), (0.6, 1.9), (1.3, 1.2), (1.6, 0.4), (0.2, 0.7), (-0.6, 0.2), (0.9, 0.3), (-1.2, 1.6), (0.3, 1.4)]:
        fruits.append(circle(x, y, 0.2, 14))
        covers.append(fruits[-1])
    lvs = []
    for x, y, a in [(-1.25, 1.1, 0.5), (-0.4, 1.95, -0.6), (0.85, 2.15, 0.7), (1.25, 0.85, -0.4), (-0.25, 0.85, 0.9), (0.55, 0.45, -1.0), (-1.75, 1.2, 2.2)]:
        lvs += leaf((x, y), (x + 0.5 * math.cos(a), y + 0.5 * math.sin(a)), 0.3, False)
    env = [rect(1.75, -0.55, 2.35, 0.35), [(1.75, 0.15), (2.05, -0.05), (2.35, 0.15)], [(2.05, 0.35), (1.9, 0.75)]]
    env2 = [rect(-2.55, -0.25, -1.95, 0.65), [(-2.55, 0.45), (-2.25, 0.25), (-1.95, 0.45)], [(-2.25, 0.65), (-1.95, 0.95)]]
    inner = keep(fruits + hide(lvs, *covers), *canopy)
    return make("Potted Kumquat Tree", canopy + inner + hide(trunk, rim) + [pot, rim] + potband + feet + env + env2)


@design("lunar_peach_blossom_vase", T)
def peach_blossom_vase(rng):
    vase = spline([(-0.35, 0.0, 1), (-0.45, -0.3), (-1.3, -0.9), (-1.4, -1.9), (-0.8, -3.0, 1), (0.8, -3.0, 1), (1.4, -1.9), (1.3, -0.9), (0.45, -0.3), (0.35, 0.0, 1)])
    lip = rrect(-0.55, -0.05, 0.55, 0.2, 0.06)
    deco = keep([wave(-2, 2, -1.3, 0.15, 3, 60), [(-2, -2.5), (2, -2.5)], [(-2, -0.75), (2, -0.75)]], vase)
    clouds = keep(flame_cloud(-0.45, -2.0, 0.45) + flame_cloud(0.35, -2.05, 0.45, True), vase)
    br = []
    for pts in [[(0, 0.15), (-0.5, 1.2), (-1.6, 2.0), (-2.6, 2.4)], [(0.1, 0.15), (0.6, 1.4), (0.4, 2.4), (0.9, 3.2)],
                [(0.15, 0.15), (1.2, 0.9), (2.2, 1.0), (3.0, 1.8)], [(-0.4, 1.1), (-1.4, 0.8), (-2.4, 1.1)]]:
        b, _ = branchy(pts, 0.14, 0.05)
        br.append(b)
    flowers, covers = [], []
    for x, y, r in [(-1.6, 2.0, 0.42), (-2.6, 2.45, 0.35), (0.45, 2.45, 0.42), (0.95, 3.2, 0.32), (2.2, 1.05, 0.42), (3.0, 1.8, 0.35),
                    (-2.35, 1.1, 0.36), (-0.6, 1.3, 0.3), (1.2, 0.95, 0.3)]:
        fs, fc = blossom(x, y, r, x)
        fs = [fs[0]] + [lens((x, y), (x + 0.5 * r * math.cos(a), y + 0.5 * r * math.sin(a)), 0.25) for a in (0.3, 1.55, 2.8, 4.05, 5.3)] if len(fs) > 1 else fs
        flowers += hide(fs, *covers)
        covers += fc
    out = flowers + hide(br, *covers, vase, lip) + [vase, lip] + hide(deco + clouds, *[])
    return make("Peach Blossoms in a Vase", out)


def ingot(cx, cy, s):
    bowl = chain(quad((-1.9, 0.55), (-1.4, -0.9), (0, -0.95), 18), quad((0, -0.95), (1.4, -0.9), (1.9, 0.55), 18))
    wing_l = chain(quad((-1.9, 0.55), (-2.3, 0.95), (-2.05, 1.2), 8), quad((-2.05, 1.2), (-1.3, 0.75), (-0.8, 0.55), 10))
    wing_r = mirror_x(wing_l)
    rim_front = quad((-1.9, 0.55), (0, 0.15), (1.9, 0.55), 20)
    dome = chain([(-0.8, 0.55)], cubic((-0.8, 0.55), (-0.85, 1.5), (0.85, 1.5), (0.8, 0.55), 24))
    back = hide([quad((-1.3, 0.75), (0, 1.0), (1.3, 0.75), 20)], chain(dome, [dome[0]]))
    out = [wing_l, wing_r, bowl, rim_front, dome] + back
    shine = [arc(0, 0.85, 0.45, 2.0, 2.8, 8), quad((-1.2, -0.35), (-0.6, -0.65), (0.0, -0.65), 10)]
    cover = chain(bowl, wing_r[::-1], wing_l)
    return tf(out + shine, cx, cy, s), transform(cover, cx, cy, s)


@design("lunar_gold_ingot", T)
def gold_ingot(rng):
    big, bc = ingot(0, 0.2, 1.5)
    small1, s1 = ingot(-2.1, -2.0, 0.6)
    small2, s2 = ingot(2.1, -2.0, 0.6)
    coins_ = []
    for x, y in [(0.0, -2.4), (-0.85, -2.6), (0.85, -2.6)]:
        coins_ += coin(x, y, 0.42, False)
    rays = [[(2.0 * math.cos(a), 0.9 + 2.0 * math.sin(a)), (2.6 * math.cos(a), 0.9 + 2.6 * math.sin(a))] for a in (0.35, 0.95, 1.57, 2.19, 2.79)]
    spark = stars_at([(-2.8, 2.0), (2.9, 1.9), (-2.2, 2.9)], 0.22)
    return make("Gold Ingot Yuanbao", layered((big, [bc]), (small1 + small2 + coins_, [s1, s2]), (rays, [])) + spark)


@design("lunar_lucky_coins", T)
def lucky_coins(rng):
    out = []
    ys = [1.6, 0.0, -1.6]
    cov = []
    for y in ys:
        c = coin(0, y, 0.85)
        marks = [lens((0.0, y + 0.3), (0.0, y + 0.62), 0.3), lens((0.0, y - 0.3), (0.0, y - 0.62), 0.3),
                 lens((0.3, y), (0.62, y), 0.3), lens((-0.3, y), (-0.62, y), 0.3)]
        out += c + marks
        cov.append(rect(-0.19, y - 0.19, 0.19, y + 0.19))
    string = [[(-0.06, 3.0), (-0.06, -2.6)], [(0.06, 3.0), (0.06, -2.6)]]
    string = hide(string, *[circle(0, y, 0.85, 40) for y in ys])
    string += [[(-0.06, y - 0.19), (-0.06, y + 0.19)] for y in ys] * 0
    knot = poly((0, 2.9), (0.35, 2.55), (0, 2.2), (-0.35, 2.55))
    loop = arc(0, 3.35, 0.35, -math.pi / 2 + 0.5, 1.5 * math.pi - 0.5, 14)
    tas = tassel(0, -2.55, 0.9, 0.5)
    side = []
    for x0 in (-2.2, 2.2):
        side += coin(x0, 0.8, 0.6, False) + coin(x0, -0.8, 0.6, False)
    return make("Lucky Coins on a Red String", out + hide(string, knot) + [knot, loop] + tas + side)


@design("lunar_papercut_window", T)
def papercut_window(rng):
    frame = rect(-3.1, -3.1, 3.1, 3.1)
    frame_in = rect(-2.8, -2.8, 2.8, 2.8)
    disc = circle(0, 0, 2.3, 120)
    lattice = []
    for v in (-1.4, 1.4):
        lattice += [[(v, -2.8), (v, 2.8)], [(-2.8, v), (2.8, v)]]
    lattice = hide(lattice, disc)
    cut = []
    edge = polar(lambda t: 2.05 + 0.12 * math.cos(16 * t), n=400)
    cut.append(edge)
    for k in range(8):
        a = k * TAU / 8
        cut.append(transform(lens((0.75, 0), (1.75, 0), 0.32), 0, 0, 1, a))
        cut.append(transform(crescent(1.45, 0, 0.32, math.pi), 0, 0, 1, a + TAU / 16))
    bs, _ = blossom(0, 0, 0.62)
    cut += bs
    ring = circle(0, 0, 0.62, 40)
    teeth = [transform([(0.62, 0), (0.78, 0.0)], 0, 0, 1, k * TAU / 16) for k in range(16)]
    corner = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            corner += [transform(crescent(0, 0, 0.35, math.pi / 4), 2.45 * sx, 2.45 * sy, 1, math.atan2(sy, sx) - math.pi / 4)]
    return make("Paper-Cut Window Flower", [frame, frame_in, disc] + lattice + cut + teeth + corner)


@design("lunar_chinese_knot", T)
def chinese_knot(rng):
    S = 1.25
    def R(p):
        return ((p[0] - p[1]) / math.sqrt(2) * S, (p[0] + p[1]) / math.sqrt(2) * S + 0.3)
    out = []
    g = [-1.2, -0.6, 0.0, 0.6, 1.2]
    for v in g:
        out.append([R((v, -1.35)), R((v, 1.35))])
        out.append([R((-1.35, v)), R((1.35, v))])
    out = [list(s) for s in out]
    border = [R(p) for p in [(-1.35, -1.35), (1.35, -1.35), (1.35, 1.35), (-1.35, 1.35), (-1.35, -1.35)]]
    loops = []
    for v in (-0.9, 0.0, 0.9):
        for side in range(4):
            pts = arc(1.35, v, 0.28, -math.pi / 2, math.pi / 2, 12)
            if side == 1:
                pts = [(-x, y) for x, y in pts]
            elif side == 2:
                pts = [(y, x) for x, y in pts]
            elif side == 3:
                pts = [(y, -x) for x, y in pts]
            loops.append([R(p) for p in pts])
    top = R((1.35, 1.35))
    bot = R((-1.35, -1.35))
    hang = [[top, (top[0], top[1] + 0.5)], arc(top[0], top[1] + 0.75, 0.25, -math.pi / 2 + 0.5, 1.5 * math.pi - 0.5, 12)]
    bead = circle(bot[0], bot[1] - 0.3, 0.22, 16)
    tas = tassel(bot[0], bot[1] - 0.55, 1.0, 0.7)
    side = [[R((1.35, -1.35)), (R((1.35, -1.35))[0] + 0.5, R((1.35, -1.35))[1] - 0.5)],
            [R((-1.35, 1.35)), (R((-1.35, 1.35))[0] - 0.5, R((-1.35, 1.35))[1] - 0.5)]]
    side_t = tassel(side[0][1][0], side[0][1][1], 0.6, 0.4) + tassel(side[1][1][0], side[1][1][1], 0.6, 0.4)
    return make("Chinese Knot Ornament", out + [border] + loops + hang + [[bot, (bot[0], bot[1] - 0.08)], bead] + tas + side + side_t)


@design("lunar_festival_drum", T)
def festival_drum(rng):
    top = ellipse(0, 1.2, 1.9, 0.55, 90)
    body = chain([(-1.9, 1.2)], cubic((-2.3, 0.4), (-2.3, -1.0), (-1.9, -1.6), (-1.9, -1.6), 16)[1:],
                 arc(0, -1.6, 1.9, math.pi, TAU, 40)[1:] if False else [(-1.9, -1.6)])
    side_l = cubic((-1.9, 1.2), (-2.35, 0.4), (-2.35, -0.9), (-1.9, -1.6), 20)
    side_r = mirror_x(side_l)
    bottom = [(1.9 * math.cos(t), -1.6 + 0.55 * math.sin(t)) for t in [math.pi + math.pi * i / 40 for i in range(41)]]
    studs = [circle(2.08 * math.cos(t) * 0.98, 0.85 + 0.55 * math.sin(t) * 0.95 - 0.1, 0.07, 8) for t in [math.pi + math.pi * (i + 0.5) / 9 for i in range(9)]]
    studs += [circle(2.05 * math.cos(t) * 0.97, -1.25 + 0.55 * math.sin(t), 0.07, 8) for t in [math.pi + math.pi * (i + 0.5) / 9 for i in range(9)]]
    band = [bs for bs in []]
    bs, _ = blossom(0, -0.2, 0.55)
    medal = circle(0, -0.2, 0.75, 40)
    clouds = flame_cloud(-1.35, -0.4, 0.35) + flame_cloud(1.35, -0.4, 0.35, True)
    stand = [[(-1.6, -1.9), (-2.4, -3.0)], [(1.6, -1.9), (2.4, -3.0)], [(-1.2, -2.05), (-1.6, -3.0)], [(1.2, -2.05), (1.6, -3.0)],
             [(-2.15, -2.65), (2.15, -2.65)]]
    stand = hide(stand, chain(side_l, bottom, side_r[::-1]))
    sticks = [tube([(0.4, 1.4), (2.6, 2.9)], 0.16), tube([(-0.4, 1.45), (-2.5, 2.8)], 0.16)]
    knobs = [circle(0.35, 1.37, 0.17, 12), circle(-0.35, 1.42, 0.17, 12)]
    drum = [top, side_l, side_r, bottom] + studs + [medal] + bs + clouds
    return make("Festival Drum with Sticks", layered((knobs, knobs), (sticks, sticks), (drum, [chain(side_l, bottom, side_r[::-1]), top]), (stand, [])))


@design("lunar_gong", T)
def gong(rng):
    posts = [rect(-2.9, -3.0, -2.5, 2.2), rect(2.5, -3.0, 2.9, 2.2)]
    beam = chain(quad((-3.5, 2.75), (-3.1, 2.2), (-2.6, 2.2), 8), [(2.6, 2.2)], quad((2.6, 2.2), (3.1, 2.2), (3.5, 2.75), 8),
                 quad((3.5, 2.75), (3.0, 2.6), (2.6, 2.65), 6), [(-2.6, 2.65)], quad((-2.6, 2.65), (-3.0, 2.6), (-3.5, 2.75), 6))
    feet = [rect(-3.3, -3.2, -2.1, -2.9), rect(2.1, -3.2, 3.3, -2.9)]
    G = circle(0, -0.2, 2.0, 120)
    rim = circle(0, -0.2, 1.75, 110)
    boss = [circle(0, -0.2, 0.55, 40), circle(0, -0.2, 0.3, 24)]
    rings = [arc(0, -0.2, 1.2, 0.3, 1.3, 12), arc(0, -0.2, 1.2, 3.5, 4.4, 12)]
    cords = [[(-0.9, 1.6), (-1.3, 2.2)], [(0.9, 1.6), (1.3, 2.2)]]
    mallet = [tube([(1.6, -2.9), (3.0, -1.4)], 0.16), ellipse(3.15, -1.2, 0.35, 0.3, 24)]
    mallet = hide(mallet[:1], mallet[1]) + mallet[1:]
    ribbon = [cubic((-2.5, 1.9), (-1.9, 1.4), (-1.4, 1.95), (-0.9, 1.6), 12)]
    return make("Bronze Gong on a Stand", hide([beam] + posts + feet, G) + [G, rim] + boss + rings + hide(cords, G) + hide(mallet, *[]))


def bowl_side(cx, cy, w, h, food=None):
    rim = ellipse(cx, cy, w, 0.28 * w, 50)
    body = chain([(cx - w, cy)], quad((cx - w, cy - h), (cx, cy - h * 1.1), (cx + w, cy), 20))
    foot = [[(cx - 0.35 * w, cy - h * 0.82), (cx - 0.3 * w, cy - h * 1.0), (cx + 0.3 * w, cy - h * 1.0), (cx + 0.35 * w, cy - h * 0.82)]]
    out = [rim, body] + foot
    return out, [chain(rim), chain(body, [(cx - w, cy)])]


@design("lunar_reunion_dinner", T)
def reunion_dinner(rng):
    table = ellipse(0, -0.6, 3.4, 1.5, 140)
    edge = [(3.4 * math.cos(t), -0.6 + 1.5 * math.sin(t) - 0.35) for t in [math.pi + math.pi * i / 60 for i in range(61)]]
    sides = [[(-3.4, -0.6), (-3.4, -0.95)], [(3.4, -0.6), (3.4, -0.95)]]
    cloth = [chain([(-3.4, -0.95)], [(-3.3, -2.3)], [(3.3, -2.3)], [(3.4, -0.95)])]
    lazy = ellipse(0, -0.55, 1.6, 0.65, 90)
    fish = spline([(-0.9, -0.5), (-0.4, -0.25), (0.35, -0.3), (0.6, -0.5, 1), (0.95, -0.25, 1), (0.85, -0.55), (0.95, -0.8, 1), (0.6, -0.6, 1),
                   (0.3, -0.75), (-0.4, -0.8)])
    platter = ellipse(0, -0.52, 1.25, 0.45, 60)
    dishes = []
    for x, y in [(-2.3, -0.15), (2.3, -0.15), (-1.9, -1.45), (1.9, -1.45), (0.0, 0.5), (0, -1.65)]:
        dishes += [ellipse(x, y, 0.55, 0.22, 30)]
    chopsticks = [[(-2.6, -1.9), (-1.6, -1.5)], [(-2.55, -2.0), (-1.55, -1.6)], [(2.6, -1.9), (1.6, -1.5)], [(2.55, -2.0), (1.55, -1.6)]]
    lans = []
    for x in (-2.0, 0.0, 2.0):
        ls, _ = lantern(x, 2.3, 0.45, 0.4, 1, True, 0.3)
        lans += ls + [[(x, 2.84), (x, 3.3)]]
    steam = [cubic((x, 0.05), (x - 0.15, 0.3), (x + 0.15, 0.5), (x, 0.75), 10) for x in (-0.3, 0.3)]
    eye_ = circle(-0.55, -0.5, 0.06, 8)
    gill = [quad((-0.4, -0.35), (-0.3, -0.52), (-0.4, -0.72), 8)]
    out = [table] + hide([edge] + sides + cloth, table) + [lazy, platter, fish] + gill + dishes + chopsticks + lans + steam
    return make("Family Reunion Dinner Table", out, [eye(-0.62, -0.5, 0.06)])


@design("lunar_hot_pot", T)
def hot_pot(rng):
    rim = ellipse(0, 0.4, 2.5, 0.85, 120)
    rim_in = ellipse(0, 0.4, 2.2, 0.7, 110)
    body = chain([(-2.5, 0.4)], cubic((-2.5, -0.6), (-2.2, -1.3), (-1.5, -1.4), (0, -1.45), 20), cubic((0, -1.45), (1.5, -1.4), (2.2, -1.3), (2.5, -0.6), 20)[1:], [(2.5, 0.4)])
    divider = [(2.2 * 0.95 * math.cos(t) * 0.0 + x, y) for x, y in []]
    split = cubic((-2.15, 0.25), (-0.8, 0.95), (0.8, -0.15), (2.15, 0.55), 30)
    handles = [arc(-2.75, 0.0, 0.4, math.pi / 2, 1.5 * math.pi, 12), arc(2.75, 0.0, 0.4, -math.pi / 2, math.pi / 2, 12)]
    bubbles = [circle(x, y, r, 14) for x, y, r in [(-1.4, 0.45, 0.15), (-0.9, 0.7, 0.12), (1.0, 0.15, 0.15), (1.5, 0.45, 0.12), (0.5, 0.0, 0.1)]]
    peppers = [lens((-1.6, 0.85), (-1.0, 0.95), 0.3), lens((1.2, 0.85), (1.7, 0.7), 0.3)]
    burner = [rect(-1.8, -2.4, 1.8, -1.6), rect(-1.4, -2.6, 1.4, -2.4), circle(1.2, -2.0, 0.2, 14)]
    flames = [lens((x, -1.6), (x, -1.15), 0.35) for x in (-0.9, -0.3, 0.3, 0.9)]
    chop = [[(0.4, 0.6), (2.2, 3.0)], [(0.65, 0.55), (2.5, 2.9)]]
    meat = lens((0.3, 0.9), (1.3, 1.5), 0.3)
    plates = [ellipse(-2.5, -2.7, 0.9, 0.3, 30), ellipse(2.6, -2.7, 0.9, 0.3, 30)]
    food = [lens((-3.0, -2.6), (-2.2, -2.4), 0.3), lens((-2.7, -2.75), (-1.9, -2.55), 0.3), circle(2.3, -2.55, 0.18, 12), circle(2.75, -2.55, 0.18, 12)]
    steam = [cubic((x, 1.3), (x - 0.2, 1.7), (x + 0.2, 2.0), (x, 2.4), 12) for x in (-1.4, -0.6)]
    pot = [rim, rim_in, body] + handles
    inside = keep([split] + bubbles + peppers, rim_in)
    out = layered(([meat] + chop, [meat]), (pot + inside, [rim, chain(body)]), (burner + flames + plates + food, plates[:0])) + steam
    return make("Bubbling Hot Pot", out)


def spring_roll(cx, cy, L, r, rot):
    body = rrect(-L / 2, -r, L / 2, r, r * 0.9)
    wraps = [quad((x, -r), (x + 0.2, 0), (x, r), 8) for x in (-L * 0.25, L * 0.05, L * 0.3)]
    return tf([body] + wraps, cx, cy, 1, rot), transform(body, cx, cy, 1, rot)


@design("lunar_spring_rolls", T)
def spring_rolls(rng):
    plate = ellipse(0, -0.6, 3.4, 1.8, 120)
    plate_in = ellipse(0, -0.6, 2.7, 1.35, 110)
    groups = []
    for cx, cy, rot in [(-0.6, 0.15, 0.25), (0.6, 0.05, -0.15), (-0.9, -0.75, -0.1), (0.4, -0.85, 0.2), (-0.2, -1.6, 0.05)]:
        s, c = spring_roll(cx, cy, 2.2, 0.38, rot)
        groups.append((s, [c]))
    rolls = layered(*groups)
    covs = [g[1][0] for g in groups]
    dip = [ellipse(2.4, 1.5, 0.75, 0.3, 30), chain([(1.65, 1.5)], quad((1.75, 0.9), (2.4, 0.85), (3.05, 1.0), 12), [(3.15, 1.5)])]
    dip_in = ellipse(2.4, 1.5, 0.55, 0.18, 24)
    chop = [[(-3.2, 1.2), (0.0, 2.6)], [(-3.0, 1.0), (0.2, 2.35)]]
    lettuce = hide([chain(wave(-2.6, -1.3, -1.5, 0.12, 3, 40), [(-1.6, -1.0), (-2.4, -1.0), (-2.6, -1.5)])], *covs)
    return make("Plate of Spring Rolls", hide([plate, plate_in], *covs) + rolls + lettuce + hide(dip + [dip_in], plate) + hide(chop, *dip))


def chopsticks_pair(x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * 0.22, dx / L * 0.22
    return [tube([(x0, y0), (x1, y1)], lambda t: 0.16 - 0.07 * t), tube([(x0 + nx, y0 + ny), (x1 + nx * 2.2, y1 + ny * 2.2)], lambda t: 0.16 - 0.07 * t)]


@design("lunar_nian_gao", T)
def nian_gao(rng):
    top = ellipse(-0.3, 0.6, 2.2, 0.8, 120)
    sides = [[(-2.5, 0.6), (-2.5, -0.6)], [(1.9, 0.6), (1.9, -0.6)]]
    bottom = [(-0.3 + 2.2 * math.cos(t), -0.6 + 0.8 * math.sin(t)) for t in [math.pi + math.pi * i / 50 for i in range(51)]]
    stamp = [circle(-0.3, 0.6, 0.6, 40)]
    bs, _ = blossom(-0.3, 0.6, 0.45)
    stamp = [ellipse(-0.3, 0.6, 0.75, 0.38, 40)] + tf(bs, -0.3, 0.6 - 0.6 * 0.0, 1) * 0
    flower_top = [transform(p, 0, 0, 1) for p in [[(x, 0.6 + 0.28 * math.sin(a)) for x, a in []]]]
    stamp = [ellipse(-0.3, 0.6, 0.8, 0.35, 40)] + [ellipse(-0.3 + 0.45 * math.cos(a), 0.6 + 0.18 * math.sin(a), 0.22, 0.1, 14) for a in [k * TAU / 6 for k in range(6)]]
    dates = [ellipse(x, y, 0.22, 0.12, 14) for x, y in [(-1.6, 0.6), (1.0, 0.6), (-0.3, 1.15), (-0.3, 0.05)]]
    plate = ellipse(-0.2, -0.8, 3.3, 1.0, 120)
    sl = [poly((1.9, -1.3), (3.1, -1.1), (3.2, -1.5), (2.0, -1.75)), [(1.9, -1.3), (1.95, -0.95), (3.15, -0.75), (3.1, -1.1)], [(3.15, -0.75), (3.2, -1.5)]]
    knife = [poly((-3.4, 2.2), (-1.0, 2.9), (-1.0, 2.6), closed=True), rrect(-1.0, 2.55, 0.4, 2.95, 0.15)]
    cake = [top] + sides + [bottom] + stamp + dates
    cov = [chain(top), chain([(-2.5, 0.6)], bottom, [(1.9, 0.6)])]
    return make("Nian Gao New Year Cake", layered((cake, [poly((-2.5, 0.6), (1.9, 0.6), (1.9, -0.6), (-2.5, -0.6))] + cov[:1]), (sl, [sl[0]]), ([plate], [])) + chopsticks_pair(-3.3, 2.0, 0.2, 2.8))


@design("lunar_tangyuan", T)
def tangyuan(rng):
    rim = ellipse(0, 0.0, 2.8, 0.9, 120)
    soup = ellipse(0, -0.05, 2.5, 0.72, 110)
    body = chain(cubic((-2.8, 0.0), (-2.8, -1.8), (-1.5, -2.4), (0, -2.4), 20), cubic((0, -2.4), (1.5, -2.4), (2.8, -1.8), (2.8, 0.0), 20)[1:])
    foot = [[(-1.0, -2.3), (-1.1, -2.7), (1.1, -2.7), (1.0, -2.3)]]
    balls, cov = [], []
    for x, y, r in [(-1.2, 0.0, 0.5), (0.0, 0.25, 0.52), (1.15, -0.05, 0.5), (-0.45, -0.35, 0.48), (0.65, -0.4, 0.48)]:
        balls.append((([circle(x, y, r, 30), arc(x, y, 0.65 * r, 1.9, 2.7, 8)]), [circle(x, y, r, 30)]))
    bl = layered(*balls[::-1])
    bl = keep(bl, chain(ellipse(0, 0.0, 2.8, 2.0, 100)))
    spoon = [chain(arc(2.2, 0.7, 0.5, math.pi * 0.2, math.pi * 1.2, 14)), tube([(2.6, 0.95), (3.6, 2.3)], 0.25)]
    deco = keep([wave(-3, 3, -1.2, 0.15, 5, 100)], chain(body, [(-2.8, 0.0)]))
    steam = [cubic((x, 0.9), (x - 0.2, 1.4), (x + 0.2, 1.8), (x, 2.4), 12) for x in (-0.8, 0.0, 0.8)]
    out = layered((spoon, [chain(spoon[0]), spoon[1]]), (bl, []), ([rim, soup, body] + foot + deco, [])) + steam
    return make("Bowl of Sweet Tangyuan", out)


@design("lunar_steamed_fish", T)
def steamed_fish(rng):
    platter = ellipse(0, 0, 3.6, 2.0, 140)
    inner = ellipse(0, 0, 3.1, 1.6, 130)
    body = spline([(-2.2, 0.05, 1), (-1.6, 0.55), (-0.5, 0.85), (0.8, 0.75), (1.8, 0.35), (2.2, 0.1, 1), (2.85, 0.6, 1), (2.65, 0.0), (2.85, -0.6, 1),
                   (2.2, -0.1, 1), (1.8, -0.4), (0.8, -0.75), (-0.5, -0.8), (-1.6, -0.5)])
    head_line = quad((-1.3, 0.62), (-1.0, 0.0), (-1.3, -0.58), 12)
    mouth = [[(-2.2, 0.05), (-1.95, 0.0)]]
    fins = [poly((-0.2, 0.83), (0.4, 1.3), (1.2, 0.68), closed=False), poly((0.2, -0.78), (0.6, -1.15), (1.1, -0.68), closed=False)]
    fins += [lens((-0.8, -0.2), (-0.2, -0.55), 0.3)]
    scales = keep([arc(x, y, 0.3, 0.5 * math.pi, 1.5 * math.pi, 8) for x in (0.0, 0.5, 1.0, 1.5) for y in (-0.3, 0.2)], body)
    tailr = [[(2.3, 0.05), (2.75, 0.3)], [(2.3, -0.05), (2.75, -0.3)]]
    scal = [lens((x, y), (x + 0.7, y + 0.25), 0.18) for x, y in [(-0.6, 0.25), (0.2, 0.35), (0.5, -0.2), (1.2, 0.1), (-0.2, -0.35)]]
    ginger = [rect(x - 0.12, y - 0.06, x + 0.12, y + 0.06) for x, y in []]
    garn = [lens((-2.9, -0.6), (-2.3, -1.2), 0.35), lens((-2.4, 1.15), (-1.8, 1.35), 0.35), circle(2.6, 1.1, 0.18, 12), circle(2.3, -1.2, 0.18, 12)]
    out = layered((scal, scal), ([body, head_line] + mouth + scales + tailr, [body]), (fins, []), ([platter, inner] + garn, []))
    return make("Whole Steamed Fish Platter", out, [eye(-1.65, 0.25, 0.1)])


@design("lunar_child_lantern", T)
def child_lantern(rng):
    head = circle(-0.6, 1.3, 0.85, 60)
    buns = [circle(-1.3, 2.12, 0.3, 24), circle(0.1, 2.12, 0.3, 24)]
    bun_ties = [spiral(-1.3, 2.12, 0.04, 0.2, 1.3, 30), spiral(0.1, 2.12, 0.04, 0.2, 1.3, 30, rot=math.pi)]
    hair = arc(-0.6, 1.3, 0.85, 0.35, math.pi - 0.35, 20)
    fringe = [quad((0.22, 1.55), (-0.6, 1.2), (-1.42, 1.55), 16), [(-0.6, 2.15), (-0.62, 1.95)]]
    cheeks = [circle(-1.05, 0.95, 0.14, 10), circle(-0.15, 0.95, 0.14, 10)]
    smile = arc(-0.6, 1.05, 0.25, 1.15 * math.pi, 1.85 * math.pi, 10)
    jacket = spline([(-1.15, 0.5), (-0.05, 0.5), (0.55, 0.0), (0.85, -1.5, 1), (-2.05, -1.5, 1), (-1.75, 0.0)])
    collar = [rrect(-0.95, 0.35, -0.25, 0.6, 0.1)]
    placket = [[(-0.6, 0.35), (-0.6, -1.5)]]
    knots = [[(x, y), (x + 0.3, y)] for x in (-0.75,) for y in (0.0, -0.5, -1.0)]
    knot_b = [circle(-0.45, y, 0.07, 8) for y in (0.0, -0.5, -1.0)]
    cuffs = [[(0.62, -0.95), (0.9, -0.85)]]
    hem = [[(-2.05, -1.5), (0.85, -1.5)]]
    pants = [rect(-1.45, -2.6, -0.75, -1.5), rect(-0.45, -2.6, 0.25, -1.5)]
    shoes = [ellipse(-1.15, -2.72, 0.48, 0.18, 20), ellipse(-0.05, -2.72, 0.48, 0.18, 20)]
    arm = tube([(0.4, 0.0), (1.1, -0.2), (1.35, 0.4)], 0.42)
    hand = circle(1.4, 0.6, 0.22, 16)
    stick = [[(1.4, 0.55), (1.6, 2.6)], [(1.6, 2.6), (2.3, 2.4)]]
    ls, lc = lantern(2.3, 1.15, 0.85, 0.75, 2, True, 0.55)
    string = [[(2.3, 2.4), (2.3, 2.0)]]
    flower_ = blossom(1.6, -0.9, 0.0)[0] * 0
    child = layered(([hand], [hand]), ([arm], [arm]), ([head, hair] + fringe + cheeks + [smile], [head]),
                    (buns + bun_ties, buns), ([jacket] + collar + placket + knots + knot_b + hem, [jacket]), (pants + shoes, []))
    return make("Child in Festive Clothes with a Lantern", child + hide(stick, hand) + ls + string,
                [eye(-0.9, 1.3, 0.09), eye(-0.3, 1.3, 0.09)])


@design("lunar_moon_gate", T)
def moon_gate(rng):
    wall = rect(-3.4, -2.6, 3.4, 1.9)
    hole = circle(0, -0.2, 2.0, 140)
    hole2 = circle(0, -0.2, 2.25, 140)
    cap, cc = roof(-3.4, 3.4, 1.9, 0.6, tiles=True, ridge=False)
    bricks = []
    for y in (-1.8, -1.0, -0.2, 0.6, 1.4):
        bricks.append([(-3.4, y), (3.4, y)])
    bricks = hide(bricks, hole2)
    pond = ellipse(0.4, -1.75, 1.3, 0.3, 50)
    rock = spline([(-1.55, -1.95), (-1.6, -1.2), (-1.2, -0.3), (-0.9, -0.9), (-0.7, -0.5), (-0.6, -1.95, 1)])
    rock_h = [circle(-1.15, -0.95, 0.12, 10)]
    tree = [[(1.0, -1.6), (0.9, -0.6), (1.4, 0.4)], [(0.95, -1.0), (0.4, -0.2)]]
    leaves = [ellipse(x, y, 0.5, 0.25, 20) for x, y in [(1.4, 0.75), (0.85, 1.05), (0.25, 0.1), (1.6, 0.25)]]
    inside = keep(layered((leaves, leaves), ([rock] + rock_h + tree + [pond], [rock]), ([[(-2.1, -1.95), (2.1, -1.95)]], [])), hole)
    steps = [rect(-1.6, -2.95, 1.6, -2.6), rect(-2.0, -3.3, 2.0, -2.95)]
    lan = []
    for x in (-2.75, 2.75):
        ls, _ = lantern(x, 0.6, 0.38, 0.33, 1, True, 0.3)
        lan += ls + [[(x, 1.9), (x, 1.07)]]
    bam = []
    out = cap + hide([wall] + bricks, *cc) + hide([hole, hole2], *[]) + inside + steps
    out = hide(out, *[ellipse(x, 0.6, 0.38, 0.33, 30) for x in (-2.75, 2.75)], *[rect(x - 0.3, -0.25, x + 0.3, 0.6) for x in (-2.75, 2.75)]) + lan
    return make("Moon Gate Garden Doorway", out)


@design("lunar_arched_bridge", T)
def arched_bridge(rng):
    R = 1.8
    arch = arc(0, -1.2, R, 0, math.pi, 60)
    refl = arc(0, -1.2, R, math.pi, TAU, 60)
    deck_top = chain([(-3.6, -0.4)], quad((-2.2, 0.2), (0, 1.4), (2.2, 0.2), 30), [(3.6, -0.4)])
    deck_top = chain([(-3.6, -0.7)], quad((-3.6, -0.7), (0, 1.6), (3.6, -0.7), 40))
    deck_bot = quad((-3.3, -1.2), (0, 1.2), (3.3, -1.2), 40)
    rail = quad((-3.4, -0.1), (0, 2.3), (3.4, -0.1), 40)
    posts = []
    for t in [i / 8 for i in range(9)]:
        x = -3.4 + 6.8 * t
        y1 = (1 - t) ** 2 * -0.1 + 2 * (1 - t) * t * 2.3 + t * t * -0.1
        x0 = -3.6 + 7.2 * t
        y0 = (1 - t) ** 2 * -0.7 + 2 * (1 - t) * t * 1.6 + t * t * -0.7
        posts.append([(x0, y0), (x, y1)])
    water = [wave(-3.8, -1.9, -1.2, 0.05, 2, 30), wave(1.9, 3.8, -1.2, 0.05, 2, 30), wave(-3.6, 3.6, -3.2, 0.06, 6, 120)]
    stones = keep([[(-3, y), (3, y)] for y in (-0.6,)], chain(deck_top, deck_bot[::-1]))
    lan = []
    for t in (0.25, 0.75):
        x = -3.4 + 6.8 * t
        y = (1 - t) ** 2 * -0.1 + 2 * (1 - t) * t * 2.3 + t * t * -0.1
        ls, _ = lantern(x, y + 0.75, 0.3, 0.27, 1, False)
        lan += ls + [[(x, y), (x, y + 0.36)]]
    willow = [circle(2.6, 2.7, 0.5, 40), chain(quad((-3.6, 0.6), (-3.0, 1.6), (-2.4, 0.9), 12), quad((-2.4, 0.9), (-2.0, 1.4), (-1.6, 0.9), 10))]
    out = [deck_top, deck_bot, rail] + posts + hide([arch], *[]) + [refl] + water + lan + willow
    return make("Arched Bridge with Lanterns", out)


@design("lunar_tanghulu", T)
def tanghulu(rng):
    out = []
    for k, (x0, y0, ang) in enumerate([(-1.4, -2.8, 0.25), (0.0, -3.0, 0.0), (1.4, -2.8, -0.25)]):
        dx, dy = math.sin(-ang), math.cos(ang)
        balls = []
        for j in range(6):
            cx, cy = x0 + dx * (1.6 + 0.62 * j), y0 + dy * (1.6 + 0.62 * j)
            balls.append(circle(cx, cy, 0.36, 30))
        b = union(*balls)
        shine = [arc(x0 + dx * (1.6 + 0.62 * j), y0 + dy * (1.6 + 0.62 * j), 0.22, 1.9, 2.7, 6) for j in range(6)]
        dimples = [arc(x0 + dx * (1.6 + 0.62 * j), y0 + dy * (1.6 + 0.62 * j), 0.36, 0.6, 1.2, 6) for j in range(6)] * 0
        stick = hide([[(x0, y0), (x0 + dx * 5.4, y0 + dy * 5.4)]], *balls)
        out += b + shine + stick
    drips = []
    return make("Candied Hawthorn Skewers", out)


@design("lunar_sesame_balls", T)
def sesame_balls(rng):
    plate = ellipse(0, -1.2, 3.4, 1.2, 120)
    plate_in = ellipse(0, -1.15, 2.6, 0.8, 110)
    groups = []
    for x, y, r in [(0.0, 0.9, 0.95), (-1.1, -0.2, 0.95), (1.1, -0.2, 0.95), (-2.0, -1.0, 0.85), (0.0, -1.1, 0.95), (2.0, -1.0, 0.85)]:
        c = circle(x, y, r, 50)
        seeds = [ellipse(x + 0.6 * r * math.cos(a) * f, y + 0.6 * r * math.sin(a) * f, 0.1, 0.05, 8, rot=a)
                 for a, f in [(0.3, 1.0), (1.4, 0.9), (2.4, 1.0), (3.5, 0.8), (4.5, 1.0), (5.5, 0.85), (0.9, 0.35), (3.0, 0.4)]]
        groups.append(([c] + seeds, [c]))
    balls = layered(*groups[::-1])
    cov = [g[1][0] for g in groups]
    steam = [cubic((x, 2.0), (x - 0.2, 2.4), (x + 0.2, 2.7), (x, 3.1), 12) for x in (-0.5, 0.5)]
    return make("Plate of Sesame Balls", balls + hide([plate, plate_in], *cov) + steam)


@design("lunar_couplet_door", T)
def couplet_door(rng):
    r_, rc = roof(-2.6, 2.6, 2.2, 0.8)
    frame = rect(-1.6, -2.6, 1.6, 2.0)
    doors = [rect(-1.45, -2.6, 0.0, 1.85), rect(0.0, -2.6, 1.45, 1.85)]
    panels = [rect(-1.25, -0.2, -0.2, 1.6), rect(0.2, -0.2, 1.25, 1.6), rect(-1.25, -2.4, -0.2, -0.5), rect(0.2, -2.4, 1.25, -0.5)]
    studs = [circle(x, y, 0.08, 8) for x in (-1.0, -0.5, 0.5, 1.0) for y in (1.3, 0.85)]
    knockers = []
    for x in (-0.35, 0.35):
        knockers += [circle(x, -0.35, 0.22, 16), circle(x, -0.62, 0.28, 20)]
    scrolls = [rect(-2.4, -2.2, -1.8, 1.6), rect(1.8, -2.2, 2.4, 1.6), rect(-1.2, 2.05, 1.2, 2.55)]
    scroll_in = [rect(-2.3, -2.05, -1.9, 1.45), rect(1.9, -2.05, 2.3, 1.45)]
    diamond = [poly((0, 1.95), (0.2, 1.75), (0, 1.55), (-0.2, 1.75))] * 0
    fu_sq = [poly((x, 0.9), (x + 0.35, 0.55), (x, 0.2), (x - 0.35, 0.55)) for x in (-0.72, 0.72)]
    steps = [rect(-2.0, -2.95, 2.0, -2.6), rect(-2.4, -3.3, 2.4, -2.95)]
    pillars = [rect(-2.6, -2.6, -2.45, 2.2), rect(2.45, -2.6, 2.6, 2.2)]
    lan = []
    for x in (-3.15, 3.15):
        ls, _ = lantern(x, 1.0, 0.45, 0.4, 1, True, 0.35)
        lan += ls + [[(x, 2.4), (x, 1.53)]]
    out = r_ + hide([frame] + doors + panels + studs + scrolls + scroll_in + fu_sq + pillars + knockers, *rc) + steps + lan
    out = hide(out[:0], *[]) + hide(r_, *[]) + hide([frame] + doors, *knockers[1::2]) + hide(panels + studs, *fu_sq, *knockers[1::2]) + fu_sq + knockers + scrolls + scroll_in + pillars + steps + lan
    return make("Front Door with Blank Couplet Banners", out)


@design("lunar_candy_tray", T)
def candy_tray(rng):
    def octo(r, cy=0.0, sy=0.62):
        return [(r * math.cos(a), cy + sy * r * math.sin(a)) for a in [math.pi / 8 + k * TAU / 8 for k in range(9)]]
    top = octo(3.0)
    inner = octo(2.75)
    centre = octo(0.95)
    walls = [[inner[k], ((centre[k][0]), centre[k][1])] for k in range(8)]
    side = [[top[k], (top[k][0], top[k][1] - 0.5)] for k in (3, 4, 5, 6, 7, 0)]
    bottom = [(p[0], p[1] - 0.5) for p in top[3:8]] + [(top[0][0], top[0][1] - 0.5)]
    cent_fill = []
    for x, y in [(-0.35, 0.1), (0.35, 0.1), (0, -0.25), (0, 0.38)]:
        cent_fill.append(circle(x, y, 0.22, 14))
    sweets = []
    seg_c = [((inner[k][0] + inner[k + 1][0] + centre[k][0] + centre[k + 1][0]) / 4, (inner[k][1] + inner[k + 1][1] + centre[k][1] + centre[k + 1][1]) / 4) for k in range(8)]
    for k, (x, y) in enumerate(seg_c):
        kind = k % 4
        if kind == 0:
            sweets += [rrect(x - 0.4, y - 0.12, x + 0.4, y + 0.12, 0.1), poly((x - 0.4, y), (x - 0.6, y + 0.15), (x - 0.6, y - 0.15)), poly((x + 0.4, y), (x + 0.6, y + 0.15), (x + 0.6, y - 0.15))]
        elif kind == 1:
            sweets += [ellipse(x - 0.2, y, 0.16, 0.1, 10), ellipse(x + 0.2, y + 0.05, 0.16, 0.1, 10), ellipse(x, y - 0.2, 0.16, 0.1, 10)]
        elif kind == 2:
            sweets += [circle(x - 0.22, y, 0.18, 12), circle(x + 0.22, y, 0.18, 12)]
        else:
            sweets += [lens((x - 0.35, y - 0.1), (x + 0.35, y + 0.1), 0.25)]
    lid = [chain(arc(0, 2.6, 2.4, 0.15, math.pi - 0.15, 40)), [(-2.37, 2.96), (2.37, 2.96)]]
    lid_bs, _ = blossom(0, 3.5, 0.45)
    out = [top, inner, centre] + walls + side + [bottom] + cent_fill + sweets
    loose = []
    for x, y, r in [(-2.6, -2.6, 0.2), (2.4, -2.7, -0.3)]:
        loose += tf([rrect(-0.4, -0.15, 0.4, 0.15, 0.12), poly((-0.4, 0), (-0.65, 0.2), (-0.65, -0.2)), poly((0.4, 0), (0.65, 0.2), (0.65, -0.2))], x, y, 1, r)
    loose += [ellipse(0.0, -2.75, 0.2, 0.12, 10), ellipse(0.5, -2.85, 0.2, 0.12, 10), ellipse(-0.5, -2.85, 0.2, 0.12, 10)]
    return make("Tray of Togetherness", out + loose)


@design("lunar_lotus_lanterns", T)
def lotus_lanterns(rng):
    out = []
    covers = []
    for cx, cy, s in [(0.0, -1.0, 1.25), (-2.2, 0.4, 0.8), (2.2, 0.2, 0.85), (-0.6, 1.4, 0.6), (1.2, 1.9, 0.5)]:
        petals = []
        for a, L in [(-1.2, 1.0), (-0.6, 1.25), (0.0, 1.45), (0.6, 1.25), (1.2, 1.0)]:
            petals.append(transform(lens((0, 0), (0, L), 0.28), cx, cy, s, a * 0.9))
        base = transform(ellipse(0, 0, 1.0, 0.28, 30), cx, cy, s)
        flame = transform(lens((0, 0.9), (0, 1.5), 0.32), cx, cy, s)
        grp = layered(([flame], [flame]), (petals[2:3], petals[2:3]), (petals[1:2] + petals[3:4], petals[1:2] + petals[3:4]),
                      (petals[0:1] + petals[4:5], petals[0:1] + petals[4:5]), ([base], [base]))
        ripples = [transform(ellipse(0, -0.1, 1.5, 0.35, 40), cx, cy, s)]
        grp += hide(ripples, base, *petals)
        out += hide(grp, *covers)
        covers += petals + [base, ripples[0]]
    moon = hide([circle(2.4, 2.8, 0.6, 40)], *covers)
    return make("Lotus Lanterns on the Water", out + moon)


@design("lunar_rabbit_lantern", T)
def rabbit_lantern(rng):
    body = spline([(-2.2, 0.0), (-1.6, 1.2), (0.0, 1.6), (1.2, 1.4), (1.9, 1.9), (2.6, 1.6), (2.9, 0.9), (2.5, 0.4), (1.7, 0.1), (1.4, -0.6), (0.0, -0.9), (-1.6, -0.7)])
    ears = [lens((1.8, 1.85), (1.1, 3.4), 0.22), lens((2.1, 1.9), (2.2, 3.5), 0.22)]
    ear_in = [lens((1.65, 2.25), (1.25, 3.05), 0.15), lens((2.12, 2.3), (2.18, 3.15), 0.15)]
    tail = circle(-2.25, 0.35, 0.35, 20)
    ribs = keep([quad((x, 2), (x - 0.3, 0.3), (x, -1.5), 12) for x in (-1.2, -0.3, 0.6)], body)
    flower_ = blossom(0.0, 0.35, 0.45)[0]
    nose = circle(2.88, 0.95, 0.07, 8)
    wheels = []
    for x in (-1.2, 1.0):
        wheels += [circle(x, -1.6, 0.6, 40), circle(x, -1.6, 0.12, 10)] + [[(x + 0.12 * math.cos(a), -1.6 + 0.12 * math.sin(a)), (x + 0.6 * math.cos(a), -1.6 + 0.6 * math.sin(a))] for a in [k * math.pi / 3 for k in range(6)]]
    axle = [[(-1.2, -1.6), (1.0, -1.6)], [(-0.1, -0.9), (-0.1, -1.6)]]
    string = [quad((-2.0, -0.4), (-3.0, -1.2), (-3.4, -2.6), 10)]
    out = layered((ears[:1] + ear_in[:1], ears[:1]), (ears[1:] + ear_in[1:], ears[1:]), ([body, nose] + ribs + flower_, [body]), ([tail], [tail]), (wheels, wheels[::14]), (axle + string, []))
    return make("Rabbit Lantern on Wheels", out, [eye(2.25, 1.3, 0.1)])


@design("lunar_brush_inkstone", T)
def brush_inkstone(rng):
    stone = rrect(-3.0, -2.4, 0.4, -0.2, 0.4)
    well = ellipse(-1.3, -1.3, 1.25, 0.75, 60)
    pool = ellipse(-1.3, -0.65, 0.7, 0.25, 30)
    clouds = flame_cloud(-2.3, -0.65, 0.3) + flame_cloud(-0.25, -0.65, 0.3, True)
    paper = poly((0.8, -2.8), (3.6, -2.4), (3.4, 0.6), (0.7, 0.2))
    seal = rect(2.6, -2.15, 3.1, -1.65)
    seal_in = rect(2.7, -2.05, 3.0, -1.75)
    brush_h = tube([(-2.4, 0.6), (1.4, 3.1)], 0.32)
    ferrule = transform(rect(-0.25, -0.2, 0.25, 0.2), -2.6, 0.47, 1, math.atan2(2.5, 3.8))
    tip = transform(spline([(0.0, 0.2), (-0.6, 0.3), (-1.3, 0.0, 1), (-0.6, -0.3), (0.0, -0.2)], closed=True), -2.75, 0.37, 1, math.atan2(2.5, 3.8))
    hang = [circle(1.6, 3.25, 0.17, 12)]
    rest = [chain(arc(-0.8, 2.0, 0.35, math.pi, TAU, 10), arc(0.0, 2.0, 0.35, math.pi, TAU, 10)[1:], arc(0.8, 2.0, 0.35, math.pi, TAU, 10)[1:])] * 0
    ink_stick = rrect(-3.0, 1.4, -2.3, 3.2, 0.08)
    stick_d = [rect(-2.85, 2.6, -2.45, 3.0)]
    out = layered(([tip, ferrule] + hang, [tip, ferrule]), ([brush_h], [brush_h]), ([ink_stick] + stick_d, [ink_stick]),
                  ([stone, well, pool] + clouds, [stone]), ([paper, seal, seal_in], []))
    return make("Calligraphy Brush and Ink Stone", out)


@design("lunar_paifang", T)
def paifang(rng):
    r1, c1 = roof(-1.1, 1.1, 1.9, 0.75)
    r2, c2 = roof(-3.4, -1.6, 1.0, 0.6)
    r3, c3 = roof(1.6, 3.4, 1.0, 0.6)
    pillars = [rect(x - 0.18, -2.8, x + 0.18, 1.0) for x in (-3.0, -1.2, 1.2, 3.0)]
    beams = [rect(-3.2, 0.55, 3.2, 1.0), rect(-1.4, 1.3, 1.4, 1.9), rect(-3.2, -0.2, -1.2, 0.15), rect(1.2, -0.2, 3.2, 0.15)]
    plaque = rect(-0.6, 1.4, 0.6, 1.8)
    bases = [rect(x - 0.35, -3.1, x + 0.35, -2.6) for x in (-3.0, -1.2, 1.2, 3.0)]
    lan = []
    for x in (-2.1, 0.0, 2.1):
        ls, _ = lantern(x, -0.75 if x else -0.2, 0.36, 0.32, 1, True, 0.3)
        lan += ls + [[(x, 0.55 if x == 0 else -0.2), (x, (-0.75 if x else -0.2) + 0.47)]] if x == 0 else ls + [[(x, -0.2), (x, -0.2)]]
    lan = []
    for x, top in [(-2.1, -0.2), (0.0, 0.55), (2.1, -0.2)]:
        cy = top - 0.85
        ls, _ = lantern(x, cy, 0.36, 0.32, 1, True, 0.3)
        lan += ls + [[(x, top), (x, cy + 0.32 + 0.11)]]
    path = [[(-1.0, -3.1), (-2.2, -3.4)], [(1.0, -3.1), (2.2, -3.4)]]
    struct = layered((r1, c1), (r2 + r3, c2 + c3), ([plaque] + beams, beams), (pillars + bases, []))
    return make("Paifang Archway with Lanterns", struct + lan)


@design("lunar_narcissus", T)
def narcissus(rng):
    bowl = chain([(-2.6, -1.0)], quad((-2.4, -2.6), (0, -2.7), (2.4, -2.6), 20)[0:1], quad((-2.6, -1.0), (-2.3, -2.7), (0, -2.7), 20), quad((0, -2.7), (2.3, -2.7), (2.6, -1.0), 20)[1:])
    rim = ellipse(0, -1.0, 2.6, 0.4, 80)
    pebbles = keep([circle(x, -1.0 + dy, 0.2, 12) for x, dy in [(-1.9, 0.05), (-1.4, -0.12), (1.5, -0.08), (2.0, 0.08), (1.1, 0.12)]], rim)
    bulbs, bc = [], []
    for x in (-0.8, 0.3):
        b = spline([(x - 0.15, -0.3), (x - 0.55, -0.7), (x - 0.5, -1.2, 1), (x + 0.5, -1.2, 1), (x + 0.55, -0.7), (x + 0.15, -0.3)], closed=False)
        bulbs.append(b)
        bc.append(chain(b, [b[0]]))
    leaves = []
    for x0, x1, top in [(-1.0, -2.2, 1.6), (-0.7, -1.4, 2.6), (-0.6, -0.5, 1.2), (0.2, 0.9, 2.3), (0.4, 1.9, 1.5), (0.1, -0.1, 1.9)]:
        leaves.append(tube(quad((x0, -0.6), (x0, top * 0.5), (x1, top), 14), lambda t: 0.28 * (1 - 0.6 * t)))
    flowers, fc = [], []
    for cx, cy, r in [(-1.0, 2.2, 0.55), (0.2, 2.9, 0.55), (1.2, 2.2, 0.5), (-1.9, 1.5, 0.45)]:
        pet = [lens((cx, cy), (cx + r * math.cos(a), cy + r * math.sin(a)), 0.35) for a in [math.pi / 2 + k * TAU / 6 for k in range(6)]]
        cup = circle(cx, cy, 0.24 * r + 0.06, 16)
        flowers += hide(union(*pet), cup) + [cup, circle(cx, cy, 0.1, 8)]
        fc += pet
    stems = [quad((x0, -0.5), (x0 + 0.1, 0.8), (cx, cy), 10) for x0, cx, cy in [(-0.85, -1.0, 2.2), (0.3, 0.2, 2.9), (0.4, 1.2, 2.2), (-0.9, -1.9, 1.5)]]
    out = layered((flowers, fc), (leaves + stems, leaves), (bulbs, bc), (pebbles + [rim, bowl], []))
    return make("Narcissus Bulbs in a Bowl", out)


@design("lunar_treasure_bowl", T)
def treasure_bowl(rng):
    rim = ellipse(0, 0.0, 2.7, 0.7, 120)
    body = chain([(-2.7, 0.0)], cubic((-2.7, -1.6), (-1.6, -2.4), (0, -2.4), (0, -2.4), 4)[:1], cubic((-2.7, 0.0), (-2.6, -1.8), (-1.4, -2.4), (0, -2.4), 20), cubic((0, -2.4), (1.4, -2.4), (2.6, -1.8), (2.7, 0.0), 20)[1:])
    foot = [[(-1.1, -2.3), (-1.3, -2.8), (1.3, -2.8), (1.1, -2.3)]]
    deco = keep(flame_cloud(-1.3, -1.2, 0.5) + flame_cloud(1.3, -1.2, 0.5, True) + [wave(-3, 3, -0.6, 0.1, 6, 100)], chain(body, [(-2.7, 0.0)]))
    medal = circle(0, -1.3, 0.55, 30)
    deco = hide(deco, medal) + [medal] + blossom(0, -1.3, 0.4)[0]
    pile = []
    items = []
    i1, c1 = ingot(-0.1, 1.05, 0.75)
    i2, c2 = ingot(-1.4, 0.45, 0.55)
    i3, c3 = ingot(1.35, 0.5, 0.55)
    coinsl = []
    cc = []
    for x, y, r in [(0.9, 1.65, 0.38), (-1.2, 1.5, 0.35), (2.0, 1.3, 0.3), (0.4, 0.3, 0.32)]:
        coinsl.append((coin(x, y, r, False), [circle(x, y, r, 30)]))
    glow = [[(3.2 * math.cos(a), 1.2 + 2.0 * math.sin(a)), (3.6 * math.cos(a), 1.2 + 2.4 * math.sin(a))] for a in (0.5, 1.0, 1.57, 2.14, 2.64)]
    front = layered(coinsl[3], (i1, [c1]), coinsl[0], coinsl[1], coinsl[2], (i2, [c2]), (i3, [c3]))
    cov_all = [c1, c2, c3] + [c[1][0] for c in coinsl]
    rim_front = [(2.7 * math.cos(t), 0.7 * math.sin(t)) for t in [math.pi + math.pi * i / 60 for i in range(61)]]
    rim_back = [(2.7 * math.cos(t), 0.7 * math.sin(t)) for t in [math.pi * i / 60 for i in range(61)]]
    bowl_front = chain(rim_front, body[::-1][:1])
    pile_vis = hide(front, poly((-3, 0), (3, 0), (3, -3), (-3, -3)) if False else [])
    pile_vis = hide(front, chain(rim_front[::-1], body[1:]))
    out = pile_vis + hide([rim_back], *cov_all) + [rim_front, body] + foot + deco + glow
    return make("Treasure Bowl Overflowing with Gold", out)


# ------------------------------------------------------------------ zodiac paper-cuts

def medallion(animal, hint_pts, deco="cloud"):
    """Paper-cut zodiac medallion: scalloped ring + animal fitted inside."""
    outer = polar(lambda t: 2.95 + 0.12 * math.cos(12 * t), n=480)
    ring = circle(0, 0, 2.55, 160)
    petals = [transform(lens((2.62, 0), (2.92, 0), 0.4), 0, 0, 1, k * TAU / 24 + TAU / 48) for k in range(24)]
    xs = [p[0] for s in animal for p in s]
    ys = [p[1] for s in animal for p in s]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    sc = min(4.3 / w, 3.1 / h)
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    dy = 0.25
    a = [[((x - cx) * sc, (y - cy) * sc + dy) for x, y in s] for s in animal]
    hints = [eye((x - cx) * sc, (y - cy) * sc + dy, 0.1) for x, y in hint_pts]
    low = (min(ys) - cy) * sc + dy
    extra = []
    if deco == "cloud":
        extra = flame_cloud(-1.1, low - 0.55, 0.42) + flame_cloud(0.9, low - 0.55, 0.42, True)
    elif deco == "wave":
        extra = [wave(-1.7, 1.7, low - 0.35, 0.12, 4, 80), wave(-1.4, 1.4, low - 0.75, 0.12, 3, 60)]
    elif deco == "blossom":
        for x in (-1.0, 0.0, 1.0):
            extra += blossom(x, low - 0.55, 0.32)[0]
    elif deco == "grass":
        extra = [zigzag(-1.8, 1.8, low - 0.25, 0.15, 9)]
    extra = keep(extra, circle(0, 0, 2.4, 100))
    top = []
    for x in (-1.0, 1.0):
        top += crescent(x * 1.0, 2.05, 0.22, -math.pi / 2 + x * 0.4) and [crescent(x * 1.0, 2.05, 0.22, -math.pi / 2)]
    top = keep(top, circle(0, 0, 2.45, 100))
    return [outer, ring] + petals + a + extra, hints


def Z(name, title, animal, hint_pts, deco):
    def fn(rng):
        st, hi = medallion(animal(), hint_pts, deco)
        return make(title, st, hi)
    design(name, T)(fn)


def rat():
    body = spline([(2.0, 0.0, 1), (1.5, 0.35), (1.1, 0.65), (0.2, 1.0), (-0.8, 0.95), (-1.5, 0.5), (-1.6, -0.1), (-1.2, -0.6),
                   (-1.35, -0.85, 1), (-0.6, -0.85, 1), (-0.5, -0.62), (0.4, -0.62), (0.55, -0.85, 1), (1.1, -0.85, 1), (1.0, -0.5), (1.4, -0.3)])
    ear = circle(0.85, 0.85, 0.38, 24)
    ear_in = circle(0.85, 0.9, 0.2, 16)
    tail = cubic((-1.55, -0.25), (-2.6, -0.6), (-2.7, 0.6), (-2.1, 0.9), 20)
    wh = [[(1.75, 0.1), (2.3, 0.35)], [(1.75, 0.0), (2.35, -0.1)]]
    cuts = [crescent(-0.6, 0.15, 0.45, math.pi / 2), crescent(0.3, 0.2, 0.32, math.pi / 2), spiral(-1.05, -0.2, 0.05, 0.3, 1.2, 30)]
    nose = circle(1.98, 0.02, 0.07, 8)
    return layered(([body, nose] + cuts, [body]), ([ear, ear_in], [ear]), ([tail] + wh, []))


def ox():
    body = spline([(-1.9, 0.6), (-0.6, 0.85), (0.6, 1.05), (1.1, 0.9), (1.6, 0.8), (2.0, 0.25), (2.15, -0.3), (2.0, -0.55, 1), (1.6, -0.4),
                   (1.2, -0.3), (0.9, -0.6), (0.8, -0.75), (0.8, -1.5, 1), (0.45, -1.5, 1), (0.42, -0.9), (-0.8, -0.9), (-1.0, -1.5, 1),
                   (-1.35, -1.5, 1), (-1.5, -0.9), (-1.9, -0.3)])
    horns = [tube(cubic((1.45, 0.78), (1.3, 1.2), (1.6, 1.5), (2.05, 1.55), 14), lambda t: 0.3 * (1 - t) + 0.04)]
    ear = lens((1.3, 0.65), (0.75, 0.45), 0.35)
    tail = [cubic((-1.9, 0.45), (-2.2, 0.0), (-2.1, -0.5), (-2.2, -0.85), 12), lens((-2.2, -0.8), (-2.25, -1.25), 0.4)]
    nose = [circle(2.0, -0.32, 0.08, 8)]
    cuts = [crescent(-0.5, 0.1, 0.45, math.pi / 2), crescent(0.4, 0.2, 0.4, math.pi / 2), [(0.45, -1.3), (0.8, -1.3)], [(-1.35, -1.3), (-1.0, -1.3)]]
    return layered((horns, horns), ([body] + nose + cuts, [body]), ([ear], [ear]), (tail, []))


def tiger():
    body = spline([(2.2, 0.35, 1), (2.15, 0.7), (1.8, 1.05), (1.65, 1.38, 1), (1.42, 1.07, 1), (1.15, 0.95), (0.0, 0.75), (-1.3, 0.8),
                   (-1.7, 0.55), (-1.75, 0.0), (-1.5, -0.6), (-1.55, -1.3, 1), (-1.1, -1.3, 1), (-1.05, -0.6), (0.4, -0.55), (0.6, -1.3, 1),
                   (1.05, -1.3, 1), (1.0, -0.5), (1.4, -0.1), (1.9, -0.05), (2.1, 0.1)])
    tail = tube(cubic((-1.65, 0.55), (-2.4, 0.5), (-2.5, 1.3), (-2.0, 1.55), 16), 0.2)
    stripes = keep([[(x, 1.2), (x + 0.15, 0.25)] for x in (-1.3, -0.85, -0.4, 0.05, 0.5)] + [[(x, -0.7), (x - 0.1, -0.15)] for x in (-0.6, -0.1)] +
                   [[(1.55, 0.95), (1.7, 0.7)], [(1.35, 0.9), (1.45, 0.6)]], body)
    nose = [circle(2.15, 0.38, 0.07, 8)]
    wh = [[(2.05, 0.2), (2.55, 0.3)], [(2.05, 0.12), (2.5, -0.05)]]
    return layered(([body] + stripes + nose, [body]), ([tail], [tail]), (wh, []))


def rabbit():
    body = spline([(1.6, 0.6, 1), (1.5, 0.95), (1.1, 1.15), (0.7, 0.95), (0.0, 0.6), (-1.0, 0.3), (-1.5, -0.3), (-1.4, -0.9),
                   (-1.0, -1.2), (0.3, -1.25, 1), (0.6, -1.12), (0.4, -1.0), (0.75, -1.22, 1), (1.05, -1.15), (0.95, -0.85), (0.9, -0.2),
                   (1.1, 0.25), (1.45, 0.38)])
    ears = [lens((0.8, 1.0), (-0.4, 2.5), 0.22), lens((1.0, 1.05), (0.5, 2.65), 0.22)]
    tail = circle(-1.55, -0.35, 0.3, 20)
    cuts = [crescent(-0.4, -0.35, 0.55, math.pi / 2), lens((0.15, 1.35), (-0.15, 1.9), 0.25), [(1.6, 0.6), (1.75, 0.5)]]
    return layered(([body] + cuts[:1], [body]), (ears[1:], ears[1:]), (ears[:1], ears[:1]), ([tail], [tail]))


def zdragon():
    cl = [(x, 0.6 * math.sin(1.6 * x + 0.4)) for x in [-2.4 + 3.6 * i / 50 for i in range(51)]]
    wf = lambda t: 0.25 + 0.3 * t
    body = tube(cl, wf)
    fin = []
    up = offset(cl, lambda t: wf(t) / 2)
    up2 = offset(cl, lambda t: wf(t) / 2 + 0.22)
    for i in range(2, 48, 3):
        fin += [up[i], up2[i + 1], up[i + 2]]
    hs, hc = dragon_head(0.85)
    hx, hy = cl[-1]
    hs = tf(hs, hx - 0.05, hy - 0.1)
    hc = tf(hc, hx - 0.05, hy - 0.1)
    legs = []
    for i in (14, 38):
        x, y = cl[i]
        legs.append(tube([(x, y - 0.1), (x + 0.2, y - 0.7), (x + 0.5, y - 0.9)], 0.18))
        legs.append(poly((x + 0.5, y - 0.75), (x + 0.75, y - 0.85), (x + 0.6, y - 1.0), (x + 0.75, y - 1.15), closed=False))
    belly = [offset(cl, lambda t: -wf(t) * 0.2)[2:-2]]
    tail = poly((cl[0][0], cl[0][1] + 0.1), (cl[0][0] - 0.5, cl[0][1] + 0.5), (cl[0][0] - 0.3, cl[0][1]), (cl[0][0] - 0.5, cl[0][1] - 0.4), (cl[0][0], cl[0][1] - 0.1), closed=False)
    return layered((hs, hc), ([body, fin] + belly + [tail], [body]), (legs, []))


def snake():
    cl = chain(cubic((-2.2, -0.9), (-1.2, -1.5), (0.0, -0.3), (0.8, -0.6), 30), cubic((0.8, -0.6), (1.8, -1.0), (2.0, 0.3), (1.0, 0.4), 30)[1:],
               cubic((1.0, 0.4), (0.0, 0.5), (0.0, 1.4), (1.0, 1.4), 30)[1:])
    wf = lambda t: 0.12 + 0.4 * min(1.0, t * 1.5) * (1 - 0.3 * max(0.0, t - 0.8) / 0.2)
    body = tube(cl, wf)
    head = spline([(0.9, 1.6), (1.4, 1.75), (1.9, 1.6, 1), (1.85, 1.35), (1.4, 1.15), (0.9, 1.2)])
    tongue = [[(1.9, 1.48), (2.25, 1.5), (2.4, 1.65)], [(2.25, 1.5), (2.4, 1.38)]]
    diamonds = []
    for i in range(10, len(cl) - 6, 7):
        x, y = cl[i]
        a, b = cl[i - 1], cl[i + 1]
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        r = wf(i / (len(cl) - 1)) * 0.38
        diamonds.append(transform(poly((-r * 1.4, 0), (0, r), (r * 1.4, 0), (0, -r)), x, y, 1, ang))
    return layered(([head], [head]), ([body] + diamonds, [body]), (tongue, []))


def horse():
    body = spline([(2.1, 0.85, 1), (2.05, 0.6), (1.6, 0.65), (1.15, 0.35), (1.0, -0.15), (1.3, -0.4), (1.9, -0.5), (2.05, -0.65, 1),
                   (1.95, -0.78, 1), (1.25, -0.62), (0.75, -0.45), (-0.2, -0.5), (-0.9, -0.45), (-1.5, -0.9), (-2.0, -1.2), (-2.15, -1.1, 1),
                   (-2.05, -0.95, 1), (-1.6, -0.62), (-1.35, -0.05), (-1.3, 0.35), (-0.4, 0.35), (0.5, 0.6), (1.0, 1.2), (1.35, 1.45),
                   (1.4, 1.75, 1), (1.55, 1.45, 1), (1.8, 1.25)])
    leg2 = tube([(0.75, -0.4), (1.0, -0.95), (0.6, -1.15)], 0.24)
    leg3 = tube([(-0.9, -0.4), (-0.6, -1.0), (-0.95, -1.3)], 0.24)
    mane = [chain(*[[(0.55 + 0.85 * t + 0.05, 0.75 + 0.75 * t), (0.4 + 0.85 * t, 0.85 + 0.75 * t + 0.25)] for t in [i / 6 for i in range(7)]])]
    tail = [lens((-1.35, 0.25), (-2.4, 0.5), 0.3), lens((-1.35, 0.15), (-2.3, -0.2), 0.3)]
    nost = [circle(1.95, 0.72, 0.06, 8)]
    return layered(([body] + nost, [body]), (tail + mane, tail), ([leg2, leg3], []))


def goat():
    body = spline([(2.0, 0.55, 1), (1.95, 0.8), (1.6, 1.15), (1.3, 1.05), (1.0, 0.6), (-1.4, 0.5), (-1.7, 0.8, 1), (-1.75, 0.45, 1),
                   (-1.65, 0.0), (-1.5, -0.5), (-1.5, -1.4, 1), (-1.25, -1.4, 1), (-1.2, -0.6), (0.5, -0.55), (0.7, -1.4, 1), (0.95, -1.4, 1),
                   (1.0, -0.4), (1.2, 0.0), (1.5, 0.4), (1.6, -0.1, 1), (1.85, 0.3), (1.95, 0.42)])
    horn = tube(cubic((1.45, 1.1), (1.2, 1.7), (0.4, 1.8), (0.5, 1.1), 18), lambda t: 0.26 * (1 - 0.8 * t))
    ear = lens((1.3, 0.95), (0.75, 0.75), 0.35)
    fleece = keep([arc(x, y, 0.28, 0.0, math.pi, 8) for x in (-1.0, -0.4, 0.2) for y in (0.05, -0.35)], body)
    return layered(([horn], [horn]), ([ear], [ear]), ([body] + fleece, [body]))


def monkey():
    head = circle(0, 1.3, 0.75, 50)
    ears = [circle(-0.8, 1.35, 0.3, 20), circle(0.8, 1.35, 0.3, 20)]
    face = union(circle(-0.25, 1.4, 0.32, 24), circle(0.25, 1.4, 0.32, 24), ellipse(0, 0.98, 0.45, 0.32, 24))
    body = ellipse(0, -0.35, 0.85, 1.05, 60)
    peach = spline([(0, -0.05), (0.55, -0.35), (0.5, -0.9), (0, -1.05), (-0.5, -0.9), (-0.55, -0.35)])
    peach_l = [lens((0.0, -0.05), (0.45, 0.25), 0.35), quad((0, -0.05), (0.1, -0.5), (0, -1.0), 8)]
    arms = [tube([(-0.75, 0.2), (-1.1, -0.4), (-0.45, -0.6)], 0.3), tube([(0.75, 0.2), (1.1, -0.4), (0.45, -0.6)], 0.3)]
    legs = [tube([(-0.55, -1.15), (-1.15, -1.25), (-0.8, -1.55)], 0.32), tube([(0.55, -1.15), (1.15, -1.25), (0.8, -1.55)], 0.32)]
    tail = [spiral(1.55, -1.0, 0.05, 0.5, 1.2, 60, rot=math.pi)]
    tail_base = [quad((0.8, -1.0), (1.4, -1.5), (1.55 - 0.5 * math.cos(0.0), -1.0 + 0.0), 10)]
    mouth = arc(0, 1.0, 0.2, 1.2 * math.pi, 1.8 * math.pi, 8)
    nost = [circle(-0.07, 1.12, 0.04, 6), circle(0.07, 1.12, 0.04, 6)]
    return layered(([peach] + peach_l, [peach]), (arms, arms), (face + [mouth], face), ([head], [head]), (ears, ears), ([body], [body]), (legs + tail, legs))


def rooster():
    body = spline([(2.0, 1.0, 1), (1.6, 1.1), (1.35, 1.3), (1.05, 1.15), (0.8, 0.6), (0.2, 0.3), (-0.4, 0.5), (-0.7, 0.0), (-0.5, -0.6),
                   (0.2, -0.9), (1.0, -0.5), (1.3, 0.2), (1.45, 0.75), (1.6, 0.9), (1.95, 0.95)])
    comb = chain(arc(1.05, 1.3, 0.16, math.pi * 0.9, 0.1, 8), arc(1.33, 1.42, 0.16, math.pi * 0.9, 0.1, 8)[1:], arc(1.6, 1.32, 0.15, math.pi * 0.9, -0.2, 8)[1:])
    wattle = lens((1.7, 0.92), (1.65, 0.5), 0.45)
    feathers = []
    for (p0, p1, c1, c2) in [((-0.4, 0.45), (-1.7, 1.7), (-0.6, 1.6), (-1.4, 1.1)), ((-0.5, 0.3), (-2.1, 0.9), (-1.0, 1.2), (-1.6, 0.5)),
                              ((-0.6, 0.15), (-2.0, -0.1), (-1.3, 0.6), (-1.5, -0.3)), ((-0.6, 0.0), (-1.6, -0.8), (-1.2, -0.1), (-1.0, -0.8))]:
        feathers.append(chain(quad(p0, c1, p1, 14), quad(p1, c2, p0, 14)[1:]))
    wing = lens((0.0, 0.0), (0.9, -0.3), 0.35)
    wing2 = [quad((0.2, -0.05), (0.5, -0.25), (0.8, -0.25), 8)]
    legs = [[(0.15, -0.88), (0.1, -1.5), (-0.2, -1.65)], [(0.1, -1.5), (0.35, -1.65)], [(0.55, -0.8), (0.6, -1.5), (0.3, -1.65)], [(0.6, -1.5), (0.85, -1.65)]]
    hackle = [quad((0.85, 0.75), (1.0, 0.45), (0.95, 0.15), 6), quad((1.05, 0.85), (1.2, 0.55), (1.15, 0.25), 6)]
    return layered(([comb, wattle], [comb, wattle]), ([body, wing] + wing2 + hackle, [body]), (feathers, feathers), (legs, []))


def dog():
    body = spline([(2.1, 0.7, 1), (2.0, 0.95), (1.6, 1.05), (1.45, 1.55, 1), (1.2, 1.1, 1), (0.9, 0.85), (-1.3, 0.5), (-1.55, 0.3),
                   (-1.5, -0.4), (-1.45, -1.3, 1), (-1.2, -1.3, 1), (-1.1, -0.5), (0.4, -0.45), (0.6, -1.3, 1), (0.85, -1.3, 1),
                   (0.95, -0.3), (1.2, 0.15), (1.5, 0.45), (1.95, 0.55)])
    tail = tube(cubic((-1.3, 0.45), (-1.9, 0.9), (-1.6, 1.6), (-0.95, 1.25), 18), lambda t: 0.3 * (1 - 0.6 * t))
    ear_in = lens((1.35, 1.15), (1.43, 1.42), 0.3)
    collar = keep([[(0.85, 1.0), (1.15, 0.2)], [(1.05, 1.0), (1.35, 0.2)]], body)
    nose = circle(2.08, 0.82, 0.08, 8)
    cuts = [crescent(-0.4, 0.0, 0.45, math.pi / 2)]
    return layered(([body, ear_in, nose] + collar + cuts, [body]), ([tail], [tail]))


def pig():
    body = spline([(2.0, 0.4, 1), (2.0, -0.05, 1), (1.6, -0.2), (1.3, -0.4), (1.1, -0.7), (1.1, -1.25, 1), (0.75, -1.25, 1), (0.75, -0.85),
                   (-0.6, -0.85), (-0.8, -1.25, 1), (-1.15, -1.25, 1), (-1.25, -0.7), (-1.7, -0.1), (-1.5, 0.6), (-0.3, 0.9), (1.2, 0.8),
                   (1.6, 0.65)])
    snout = ellipse(2.0, 0.18, 0.12, 0.24, 16)
    nost = [circle(2.0, 0.27, 0.04, 6), circle(2.0, 0.09, 0.04, 6)]
    ear = poly((0.95, 0.82), (1.35, 1.35), (1.45, 0.75))
    tail = [spiral(-1.95, 0.25, 0.05, 0.25, 1.5, 40)]
    tail_b = [[(-1.68, 0.1), (-1.95 + 0.25, 0.25)]]
    cuts = [crescent(-0.3, 0.05, 0.5, math.pi / 2), crescent(0.6, 0.15, 0.35, math.pi / 2)]
    return layered(([ear], [ear]), ([body, snout] + nost + cuts, [body]), (tail + tail_b, []))


Z("lunar_year_rat", "Year of the Rat Paper-Cut", rat, [(1.3, 0.4)], "blossom")
Z("lunar_year_ox", "Year of the Ox Paper-Cut", ox, [(1.75, 0.3)], "grass")
Z("lunar_year_tiger", "Year of the Tiger Paper-Cut", tiger, [(1.75, 0.65)], "cloud")
Z("lunar_year_rabbit", "Year of the Rabbit Paper-Cut", rabbit, [(1.2, 0.75)], "grass")
Z("lunar_year_dragon", "Year of the Dragon Paper-Cut", zdragon, [], "cloud")
Z("lunar_year_snake", "Year of the Snake Paper-Cut", snake, [(1.45, 1.5)], "blossom")
Z("lunar_year_horse", "Year of the Horse Paper-Cut", horse, [(1.6, 1.15)], "cloud")
Z("lunar_year_goat", "Year of the Goat Paper-Cut", goat, [(1.6, 0.85)], "grass")
Z("lunar_year_monkey", "Year of the Monkey Paper-Cut", monkey, [(-0.25, 1.42), (0.25, 1.42)], "cloud")
Z("lunar_year_rooster", "Year of the Rooster Paper-Cut", rooster, [(1.5, 1.05)], "grass")
Z("lunar_year_dog", "Year of the Dog Paper-Cut", dog, [(1.65, 0.85)], "blossom")
Z("lunar_year_pig", "Year of the Pig Paper-Cut", pig, [(1.45, 0.4)], "blossom")


@design("lunar_pellet_drum", T)
def pellet_drum(rng):
    face = circle(0, 1.0, 1.6, 100)
    face_in = circle(0, 1.0, 1.35, 90)
    side = [[(-1.6, 1.0), (-1.6, 0.75)], [(1.6, 1.0), (1.6, 0.75)]]
    bs, bc = blossom(0, 1.0, 0.75)
    studs = [circle(1.48 * math.cos(a), 1.0 + 1.48 * math.sin(a), 0.06, 6) for a in [k * TAU / 16 for k in range(16)]]
    handle = tube([(0, -0.6), (0, -3.2)], 0.35)
    stem = [[(-0.12, -0.6), (-0.12, -0.45)], [(0.12, -0.6), (0.12, -0.45)]]
    knob = ellipse(0, -3.3, 0.3, 0.15, 14)
    strings = [quad((-1.6, 1.0), (-2.1, 0.6), (-2.5, 0.0), 10), quad((1.6, 1.0), (2.1, 0.6), (2.5, 0.0), 10)]
    beads = [circle(-2.55, -0.2, 0.25, 18), circle(2.55, -0.2, 0.25, 18)]
    tas = tassel(0, -3.45, 0.7, 0.4)
    rings = [[(-0.2, y), (0.2, y)] for y in (-1.2, -2.6)]
    motion = [arc(0, 1.0, 2.3, a0, a0 + 0.35, 8) for a0 in (0.3, 2.5)]
    lower = []
    return make("Pellet Drum Toy", hide([face] + side + lower, *[]) + [face_in] + bs + studs + [handle] + rings + [knob] + strings + beads + tas + motion)


@design("lunar_fortune_pouch", T)
def fortune_pouch(rng):
    bag = spline([(-0.9, 0.9), (-1.4, 0.3), (-2.1, -0.8), (-2.0, -2.2), (-1.0, -2.8), (1.0, -2.8), (2.0, -2.2), (2.1, -0.8), (1.4, 0.3), (0.9, 0.9)], closed=False)
    ruffle = chain(quad((-0.9, 0.9), (-1.6, 1.6), (-1.3, 2.2), 10), quad((-1.3, 2.2), (-0.6, 1.7), (0.0, 2.3), 10)[1:],
                   quad((0.0, 2.3), (0.6, 1.7), (1.3, 2.2), 10)[1:], quad((1.3, 2.2), (1.6, 1.6), (0.9, 0.9), 10)[1:])
    gather = [[(-0.9, 0.9), (0.9, 0.9)], [(-1.0, 0.65), (1.0, 0.65)]]
    folds = [quad((-0.6, 0.65), (-0.8, 0.0), (-0.75, -0.4), 8), quad((0.6, 0.65), (0.8, 0.0), (0.75, -0.4), 8)]
    medal = circle(0, -1.3, 0.9, 50)
    bs, _ = blossom(0, -1.3, 0.7)
    cloudz = flame_cloud(-1.45, -2.15, 0.3) + flame_cloud(1.25, -2.15, 0.3, True)
    cord = [cubic((0.9, 0.78), (2.0, 0.9), (2.4, 1.6), (2.0, 2.2), 14)]
    t1 = tassel(2.0, 2.2, 0.7, 0.4)
    t1 = tf(t1, 0, 0)
    coins_ = coin(-2.6, -2.6, 0.45, False) + coin(-1.95, -3.0, 0.4, False)
    out = [bag, ruffle] + gather + folds + hide(bs, *[]) + [medal] + cloudz
    return make("Embroidered Fortune Pouch", hide(out, *[circle(-2.6, -2.6, 0.45, 30), circle(-1.95, -3.0, 0.4, 30)]) + coins_ + cord + [[(2.0, 2.2), (2.0, 2.2)]] * 0 + tassel(2.0, 2.25, 0.7, 0.4))
