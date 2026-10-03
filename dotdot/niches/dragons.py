"""Dragons & Mythical Creatures niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "dragons"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ------------------------------------------------------------ helpers

def smooth(pts, closed=False, n=8):
    """Smooth curve through the given points.

    A point written as (x, y, 1) is a sharp corner (the curve is not
    rounded there)."""
    P = [(p[0], p[1]) for p in pts]
    sharp = [len(p) > 2 and p[2] for p in pts]
    if closed:
        if math.dist(P[0], P[-1]) < 1e-9:
            P, sharp = P[:-1], sharp[:-1]
    m = len(P)

    def tangent(i, side):
        if sharp[i] or (not closed and (i == 0 or i == m - 1)):
            j = i + 1 if side > 0 else i - 1
            if not closed and (j < 0 or j >= m):
                j = i - 1 if side > 0 else i + 1
                d = (P[i][0] - P[j][0], P[i][1] - P[j][1])
            else:
                j %= m
                d = (P[j][0] - P[i][0], P[j][1] - P[i][1]) if side > 0 else (P[i][0] - P[j][0], P[i][1] - P[j][1])
        else:
            a, b = P[(i - 1) % m], P[(i + 1) % m]
            d = (b[0] - a[0], b[1] - a[1])
        L = math.hypot(*d) or 1.0
        return d[0] / L, d[1] / L

    out = []
    segs = m if closed else m - 1
    for i in range(segs):
        a, b = P[i], P[(i + 1) % m]
        L = math.dist(a, b)
        t0, t1 = tangent(i, 1), tangent((i + 1) % m, -1)
        c1 = (a[0] + t0[0] * L / 3, a[1] + t0[1] * L / 3)
        c2 = (b[0] - t1[0] * L / 3, b[1] - t1[1] * L / 3)
        k = max(2, int(n * L / 0.5) + 2)
        seg = cubic(a, c1, c2, b, k)
        out.extend(seg if not out else seg[1:])
    return out


def S(*pts, n=8):
    """Open smooth curve."""
    return smooth(pts, False, n)


def C(*pts, n=8):
    """Closed smooth curve."""
    return smooth(pts, True, n)


def tf(strokes, dx=0.0, dy=0.0, s=1.0, rot=0.0):
    return [transform(p, dx=dx, dy=dy, s=s, rot=rot) for p in strokes]


def flip(strokes, axis=0.0):
    return [mirror_x(p, axis) for p in strokes]


def sides(center, wfn):
    """Edges of a band along `center`: (below/right side base->tip, above/left side tip->base)."""
    t = tube(center, wfn, cap=False)
    n = len(center)
    left, right = t[:n], t[n:]
    return right[::-1], left[::-1]


def band(center, wfn):
    """Closed outline of a tapering band (tail, serpent body)."""
    return tube(center, wfn, cap=True)


def taper(w0, w1=0.0):
    return lambda t: w0 + (w1 - w0) * t


def bat_wing(dx, dy, s=1.0, rot=0.0, mirror=False):
    """Dragon wing rooted at (dx, dy), rising up and to the right."""
    W = (1.0, 1.8)
    tips = [(2.6, 2.9), (3.1, 1.6), (2.8, 0.5), (1.9, -0.2)]
    R = (0.6, -0.35)
    edge = [S((0.0, 0.0), (0.4, 1.0), W), S(W, (1.9, 2.55), tips[0])]
    pts = tips + [R]
    memb = []
    for a, b in zip(pts, pts[1:]):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        vx, vy = W[0] - mx, W[1] - my
        L = math.hypot(vx, vy)
        memb.append(quad(a, (mx + vx / L * 0.35, my + vy / L * 0.35), b, 12))
    outline = chain(*edge, *memb)
    fingers = [S(W, ((W[0] + t[0]) / 2 + 0.05, (W[1] + t[1]) / 2 + 0.1), t) for t in tips[1:]]
    claw = [poly((W[0] - 0.05, W[1] + 0.05), (W[0] - 0.2, W[1] + 0.35), (W[0] + 0.12, W[1] + 0.12), closed=False)]
    parts = [outline] + fingers + claw
    if mirror:
        parts = [mirror_x(p) for p in parts]
    return [transform(p, dx=dx, dy=dy, s=s, rot=rot) for p in parts]


def spikes(path, n, h, b=None, t0=0.1, t1=0.9, side=1):
    """Open triangular spikes standing on a path (to the left of its direction)."""
    L = [0.0]
    for p, q in zip(path, path[1:]):
        L.append(L[-1] + math.dist(p, q))
    out = []
    for k in range(n):
        tt = t0 + (t1 - t0) * (k + 0.5) / n
        target = tt * L[-1]
        i = max(1, min(len(path) - 1, next((j for j, v in enumerate(L) if v >= target), len(path) - 1)))
        p, q = path[i - 1], path[i]
        dx, dy = q[0] - p[0], q[1] - p[1]
        d = math.hypot(dx, dy) or 1.0
        ux, uy = dx / d, dy / d
        nx, ny = -uy * side, ux * side
        f = (target - L[i - 1]) / d if d else 0
        cx, cy = p[0] + dx * f, p[1] + dy * f
        bb = b or h * 0.9
        hh = h(tt) if callable(h) else h
        out.append([(cx - ux * bb / 2, cy - uy * bb / 2), (cx + nx * hh + ux * hh * 0.25, cy + ny * hh + uy * hh * 0.25), (cx + ux * bb / 2, cy + uy * bb / 2)])
    return out


def flame(x, y, length, width, rot=0.0):
    """Flame tongue starting at (x, y) and pointing along angle rot."""
    L, W = length, width
    up = [(0.0, W * 0.12), (L * 0.25, W * 0.45), (L * 0.35, W * 0.3), (L * 0.55, W * 0.55), (L * 0.65, W * 0.3), (L * 0.85, W * 0.4), (L, 0.0, 1)]
    dn = [(L * 0.8, -W * 0.3), (L * 0.6, -W * 0.15), (L * 0.45, -W * 0.5), (L * 0.3, -W * 0.25), (L * 0.15, -W * 0.35), (0.0, -W * 0.1)]
    outer = S(*up, *dn)
    inner = S((L * 0.08, 0.0), (L * 0.3, W * 0.18), (L * 0.5, W * 0.05), (L * 0.62, 0.0, 1), (L * 0.45, -W * 0.12), (L * 0.25, -W * 0.1), (L * 0.08, 0.0))
    return [transform(p, dx=x, dy=y, rot=rot) for p in (outer, inner)]


def claws(x, y, n=3, w=0.2, h=0.18, dirx=-1):
    """Toes/claws along the ground starting at x going in dirx."""
    pts = [(x, y + h)]
    for k in range(n):
        pts += [(x + dirx * (k * w + w * 0.5), y, 1), (x + dirx * (k + 1) * w, y + h * 0.6, 1)]
    return pts


def scales_rows(cx, cy, w, h, rows, cols, r):
    out = []
    for i in range(rows):
        for j in range(cols):
            x = cx - w / 2 + (j + 0.5 * (i % 2)) * w / cols
            y = cy + h / 2 - i * h / rows
            out.append(arc(x, y, r, math.pi * 1.05, math.pi * 1.95, 8))
    return out


def coin(x, y, r):
    return [ellipse(x, y, r, r * 0.35, 30)]


def feather_wing(dx, dy, s=1.0, rot=0.0, mirror=False, feathers=6):
    """Feathered wing; its root is at (dx, dy) and it sweeps up and right."""
    lead = [(0.0, 0.0), (0.35, 0.75), (1.1, 1.55), (2.1, 2.15), (2.9, 2.35)]
    tips = [(2.9, 2.35), (2.75, 1.65), (2.4, 1.05), (1.9, 0.55), (1.3, 0.12), (0.7, -0.18), (0.15, -0.3)][:feathers + 1]
    edge = []
    for a, b in zip(tips, tips[1:]):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        vx, vy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(vx, vy)
        edge.append(quad(a, (mx - vy / L * 0.3, my + vx / L * 0.3), b, 10))
    outline = chain(S(*lead), *edge, [(0.0, 0.0)])
    inner = S((0.3, 0.35), (0.9, 0.85), (1.6, 1.35), (2.3, 1.85), (2.7, 2.05))
    lines = [[(0.3 + 2.4 * t, 0.35 + 1.7 * t), tips[k]] for k, t in zip(range(1, len(tips) - 1), (0.9, 0.72, 0.5, 0.3, 0.12))]
    parts = [outline, inner] + lines
    if mirror:
        parts = [mirror_x(p) for p in parts]
    return [transform(p, dx=dx, dy=dy, s=s, rot=rot) for p in parts]


# ------------------------------------------------------------ dragons

def dragon_side():
    """Four-legged dragon facing left with an open mouth.  Returns (strokes, eye)."""
    head = [(-1.3, 2.12), (-1.6, 1.98), (-2.1, 1.78), (-2.38, 1.62, 1), (-2.12, 1.47), (-1.72, 1.4, 1), (-2.18, 1.12, 1), (-1.75, 0.96),
            (-1.35, 0.95), (-1.15, 0.55), (-1.2, 0.0), (-1.3, -0.45), (-1.42, -0.8), (-1.5, -1.3), (-1.6, -1.55)]
    fore = claws(-1.6, -1.85, 3, 0.2, 0.18, -1)
    fore = [(-1.62, -1.62), (-1.95, -1.85, 1), (-1.78, -1.68, 1), (-1.62, -1.86, 1), (-1.45, -1.7, 1), (-1.28, -1.86, 1), (-1.15, -1.55),
            (-1.02, -1.05), (-0.85, -0.68), (-0.3, -0.85), (0.4, -0.85), (0.62, -0.98), (0.55, -1.4), (0.62, -1.62),
            (0.32, -1.86, 1), (0.5, -1.7, 1), (0.66, -1.86, 1), (0.84, -1.7, 1), (1.02, -1.86, 1), (1.16, -1.5), (1.35, -1.1), (1.42, -0.62)]
    tail_c = [(1.45, -0.25), (2.1, -0.55), (2.7, -0.65), (3.15, -0.35), (3.25, 0.15), (3.05, 0.5)]
    below, above = sides(S(*tail_c, n=6), taper(0.75, 0.1))
    back = [(1.3, 0.2), (0.9, 0.38), (0.2, 0.45), (-0.5, 0.42), (-0.8, 0.75), (-0.85, 1.35), (-1.05, 1.95)]
    outline = chain(S(*head, *fore), below, above, S(*back, head[0]))
    tip = poly((3.0, 0.48), (2.75, 0.75), (3.05, 1.15), (3.3, 0.75), (3.12, 0.52), closed=False)
    horns = [lens((-1.35, 2.08), (-0.75, 2.65), 0.18, 12), lens((-1.15, 2.0), (-0.6, 2.3), 0.16, 10)]
    teeth = [zigzag(-2.1, -1.8, 1.44, 0.05, 3), zigzag(-2.05, -1.8, 1.13, 0.05, 2)]
    nostril = [S((-2.15, 1.7), (-2.05, 1.66))]
    brow = [S((-1.95, 1.95), (-1.7, 2.02), (-1.5, 1.95))]
    plates = [S((-1.18 - 0.02 * k, 0.75 - 0.35 * k), (-0.95, 0.72 - 0.35 * k - 0.05)) for k in range(4)]
    belly = [S((-0.75, -0.6), (-0.1, -0.65), (0.5, -0.6))]
    sp = spikes(S(*back[::-1], n=6), 6, 0.25)
    wing = bat_wing(-0.4, 0.45, 0.85, 0.15)
    far_wing = [transform(p, dx=-0.75, dy=0.6, s=0.65, rot=0.45) for p in bat_wing(0, 0)[:1]]
    return [outline, tip] + horns + teeth + nostril + brow + plates + belly + sp + wing + far_wing, (-1.68, 1.75)


@design("dragons_fire_breathing", T)
def fire_breathing(rng):
    d, e = dragon_side()
    fire = flame(-2.35, 1.3, 1.6, 0.9, math.radians(195))
    ground = [S((-3.0, -1.88), (0.0, -1.86), (3.4, -1.9))]
    rocks = [S((-3.0, -1.88), (-2.7, -1.5), (-2.3, -1.88)), S((2.2, -1.9), (2.5, -1.6), (2.9, -1.9))]
    return make("Fire-Breathing Dragon", d + fire + ground + rocks, [eye(*e, 0.07)])


@design("dragons_perched_rock", T)
def perched_rock(rng):
    body = S((-0.55, 2.6), (-0.95, 2.62), (-1.6, 2.42), (-2.05, 2.25, 1), (-1.95, 2.05), (-1.6, 1.98), (-1.2, 1.88), (-0.95, 1.7),
             (-1.05, 1.3), (-1.15, 0.6), (-1.1, 0.1), (-1.2, -0.55), (-1.5, -0.95, 1), (-1.3, -0.82, 1), (-1.15, -1.0, 1), (-1.0, -0.82, 1),
             (-0.85, -0.98, 1), (-0.75, -0.6), (-0.65, 0.2), (-0.5, -0.4), (-0.6, -0.95, 1), (-0.4, -0.82, 1), (-0.25, -1.0, 1),
             (-0.1, -0.82, 1), (0.05, -0.98, 1), (0.6, -0.95), (0.95, -0.6))
    tail_c = S((0.95, -0.75), (1.55, -1.3), (1.8, -2.1), (1.5, -2.8), (0.9, -2.9), (0.6, -2.55), n=6)
    below, above = sides(tail_c, taper(0.55, 0.08))
    back = S((1.05, -0.25), (1.0, 0.5), (0.6, 1.2), (0.1, 1.6), (-0.25, 2.0), (-0.35, 2.35), (-0.55, 2.6))
    outline = chain(body, below, above, back)
    haunch = [S((-0.5, -0.4), (-0.15, 0.3), (0.5, 0.2), (0.75, -0.4), (0.6, -0.95))]
    wing = bat_wing(0.05, 1.35, 0.75, 0.25)
    horns = [lens((-0.6, 2.55), (0.0, 3.2), 0.18, 12), lens((-0.45, 2.45), (0.2, 2.75), 0.16, 10)]
    sp = spikes(back[::-1], 5, 0.22, t0=0.15, t1=0.6)
    plates = [S((-1.05 - 0.01 * k, 1.4 - 0.4 * k), (-0.8, 1.35 - 0.4 * k)) for k in range(3)]
    mouth = [S((-1.95, 2.12), (-1.5, 2.1), (-1.25, 2.15))]
    nost = [S((-1.85, 2.35), (-1.75, 2.32))]
    rock = [S((-2.6, -2.9), (-2.5, -1.8), (-2.0, -1.1), (-1.0, -0.95), (0.3, -0.98), (1.2, -1.15), (2.0, -1.6), (2.5, -2.3), (2.6, -2.9)),
            S((-1.7, -1.6), (-1.2, -2.0), (-1.3, -2.5)), S((0.6, -1.6), (0.3, -2.1))]
    moon = [circle(-2.3, 0.9, 0.55, 40)]
    return make("Dragon Perched on a Rock", [outline] + haunch + wing + horns + sp + plates + mouth + nost + rock + moon, [eye(-1.15, 2.3, 0.07)])


@design("dragons_sleeping_treasure", T)
def sleeping_treasure(rng):
    path = S((-1.0, -1.85), (0.4, -2.3), (1.9, -1.7), (2.55, -0.2), (2.0, 1.2), (0.5, 1.9), (-1.0, 1.75), (-2.1, 0.9), (-2.5, -0.4),
             (-2.15, -1.4), (-1.5, -1.6), n=6)
    w = lambda t: 1.05 - 0.95 * t ** 1.3
    body = band(path, w)
    head = C((-1.0, -1.45), (-1.6, -1.35), (-2.4, -1.65), (-2.75, -1.95, 1), (-2.5, -2.25), (-1.8, -2.4), (-1.1, -2.35))
    eye_ = [arc(-1.85, -1.75, 0.2, math.pi + 0.3, TAU - 0.3, 8)]
    nostril = [S((-2.55, -1.95), (-2.45, -1.9))]
    horns_ = [lens((-1.3, -1.45), (-0.7, -0.95), 0.18, 10)]
    sp = spikes(tube(path, w, cap=False)[len(path):][::-1], 9, 0.25, t0=0.12, t1=0.75, side=-1)
    chest = [rect(-1.0, -0.6, 0.9, 0.4), [(-1.0, 0.0), (0.9, 0.0)], rect(-0.15, -0.25, 0.15, 0.1),
             S((-1.0, 0.4), (-0.05, 1.0), (0.9, 0.4))]
    coins = coin(-1.4, -0.75, 0.3) + coin(1.3, -0.7, 0.3) + coin(1.1, -1.05, 0.25) + coin(-1.25, 0.5, 0.25) + coin(1.35, 0.6, 0.28)
    gems = [star(0.0, 1.25, 0.2, 4, 0.5), lens((-1.7, 0.1), (-1.5, 0.4), 0.5, 8)]
    zs = [poly((-3.0, -0.5), (-2.75, -0.5), (-3.0, -0.75), (-2.75, -0.75), closed=False), poly((-3.3, 0.0), (-3.0, 0.0), (-3.3, -0.3), (-3.0, -0.3), closed=False)]
    return make("Dragon Asleep on Its Treasure", [body, head] + eye_ + nostril + horns_ + sp + chest + coins + gems + zs)


@design("dragons_head_portrait", T)
def head_portrait(rng):
    head = S((2.6, -2.8), (1.6, -1.2), (1.2, -0.6), (0.4, -0.65), (-0.6, -0.35), (-1.6, 0.0), (-2.4, 0.25), (-2.6, 0.55, 1),
             (-2.15, 0.6), (-1.4, 0.55, 1), (-2.3, 1.0, 1), (-2.4, 1.3), (-2.0, 1.45), (-1.2, 1.6), (-0.4, 1.95), (0.3, 2.0),
             (0.9, 1.6), (1.6, 1.0), (2.3, 0.0), (2.9, -1.3), (3.2, -2.8))
    teeth = [zigzag(-2.1, -1.5, 0.92, 0.07, 4), zigzag(-2.2, -1.5, 0.52, 0.06, 4)]
    tongue = [S((-1.45, 0.75), (-1.9, 0.72), (-2.5, 0.85), (-2.8, 0.7))]
    nostril = [S((-2.1, 1.35), (-1.9, 1.25), (-1.95, 1.15))]
    brow = [S((-1.1, 1.65), (-0.4, 1.4), (0.1, 1.55))]
    eye_ = [lens((-0.55, 1.15), (0.15, 1.2), 0.3, 14)]
    horns = [S((0.0, 1.95), (0.8, 2.9), (2.0, 3.4), (2.9, 3.2)), S((0.6, 1.75), (1.4, 2.55), (2.9, 3.2)),
             S((0.95, 1.4), (1.8, 1.9), (2.6, 1.85)), S((1.3, 1.1), (2.0, 1.55), (2.6, 1.85))]
    frill = [poly((1.6, 1.0), (2.6, 1.0), (2.0, 0.5), (2.9, 0.1), (2.3, -0.25), closed=False)]
    jaw = [S((-1.4, 0.55), (-0.6, 0.35), (0.3, 0.05), (1.0, -0.2))]
    ridges = [S((-0.6, -0.35), (-0.4, -0.65)), S((0.15, -0.5), (0.25, -0.85))]
    neck_plates = [S((1.25 + 0.3 * k, -0.9 - 0.45 * k), (1.75 + 0.25 * k, -0.8 - 0.4 * k)) for k in range(4)]
    scales = [arc(x, y, 0.22, math.pi * 1.1, math.pi * 1.9, 8) for x, y in [(0.6, 0.9), (1.1, 0.6), (0.9, 0.2), (1.6, -0.1), (2.0, -0.7), (2.4, -1.4)]]
    return make("Dragon Head Portrait", [head] + teeth + tongue + nostril + brow + eye_ + horns + frill + jaw + ridges + neck_plates + scales,
                [lens((-0.24, 0.95), (-0.18, 1.4), 0.3, 8)])


@design("dragons_eastern_serpent", T)
def eastern_serpent(rng):
    path = [(-1.2 + 0.0 * i, 0.0) for i in range(1)]
    path = S((-1.3, 1.0), (-0.3, 0.2), (0.6, 1.0), (1.4, 1.9), (2.4, 1.3), (2.4, 0.0), (1.4, -0.8), (0.2, -1.2), (-1.0, -1.7),
             (-1.6, -2.4), (-1.0, -2.9), (0.0, -2.6), n=6)
    w = lambda t: 0.85 - 0.7 * t
    body = band(path, w)
    head = C((-1.3, 1.35), (-1.75, 1.6), (-2.4, 1.55), (-2.9, 1.45, 1), (-2.85, 1.2), (-2.4, 1.1, 1), (-2.8, 0.85, 1), (-2.3, 0.65),
             (-1.6, 0.7), (-1.0, 0.65))
    antlers = [S((-1.6, 1.6), (-1.3, 2.3), (-0.9, 2.7)), S((-1.4, 2.1), (-1.0, 2.15)), S((-1.4, 1.5), (-0.8, 1.9), (-0.35, 2.35)),
               S((-0.9, 1.95), (-0.6, 1.85))]
    whiskers = [S((-2.7, 1.3), (-3.2, 1.8), (-3.6, 1.7), (-3.9, 2.1)), S((-2.6, 0.75), (-3.1, 0.3), (-3.5, 0.45), (-3.8, 0.0))]
    mane = [poly((-1.0, 1.35), (-0.55, 1.6), (-0.6, 1.15), (-0.1, 1.2), (-0.35, 0.8), closed=False)]
    teeth = [zigzag(-2.75, -2.45, 1.12, 0.05, 2)]
    sp = spikes(tube(path, w, cap=False)[:len(path)], 12, 0.22, t0=0.1, t1=0.85)
    belly = [S(*[(x, y) for x, y in tube(path, lambda t: w(t) * 0.45, cap=False)[len(path):]][::-1][2:-6])]
    legs = []
    for x, y, s_ in [(0.2, 0.2, 1), (2.2, 1.0, -1), (1.2, -1.3, 1), (-0.9, -2.3, 1)]:
        legs.append(S((x, y), (x - 0.3 * s_, y - 0.45), (x - 0.15 * s_, y - 0.75)))
        legs.append(poly((x - 0.35 * s_, y - 0.75), (x - 0.15 * s_, y - 0.95), (x + 0.0, y - 0.72), (x + 0.15 * s_, y - 0.9), (x + 0.1 * s_, y - 0.65), closed=False))
    pearl = [circle(2.6, 2.7, 0.4, 30)] + flame(2.6, 3.05, 0.6, 0.4, math.radians(90))[:1]
    tail_tuft = [poly((0.0, -2.6), (0.4, -2.3), (0.25, -2.6), (0.55, -2.75), (0.05, -2.8), closed=False)]
    clouds = [S((-3.5, -1.0), (-3.0, -0.6), (-2.5, -1.0), (-2.2, -0.7)), spiral(-3.0, -1.4, 0.05, 0.35, 1.1)]
    return make("Eastern Serpent Dragon", [body, head] + antlers + whiskers + mane + teeth + sp + legs + pearl + tail_tuft + clouds,
                [eye(-1.75, 1.25, 0.08)])


@design("dragons_baby_hatching", T)
def baby_hatching(rng):
    shell = S((-2.0, 0.0), (-2.1, -1.2), (-1.4, -2.4), (0.0, -2.75), (1.4, -2.4), (2.1, -1.2), (2.0, 0.0))
    crack = [zigzag(-2.0, 2.0, 0.0, 0.3, 6)]
    head = C((0.0, 2.9), (-0.9, 2.7), (-1.5, 2.1), (-1.85, 1.45, 1), (-1.55, 1.15), (-0.9, 1.05), (-0.6, 0.6), (-0.3, 0.3),
             (0.6, 0.3), (1.0, 0.8), (1.3, 1.6), (1.1, 2.4), (0.6, 2.8))
    head = S((-0.9, -0.05), (-0.85, 0.6), (-1.3, 0.95), (-1.85, 1.15), (-2.0, 1.45, 1), (-1.7, 1.75), (-1.2, 2.1), (-0.5, 2.5),
             (0.3, 2.5), (0.95, 2.0), (1.1, 1.2), (0.9, 0.5), (1.0, -0.05))
    mouth = [S((-1.95, 1.4), (-1.4, 1.2), (-1.0, 1.35))]
    nost = [S((-1.75, 1.65), (-1.65, 1.6))]
    eye_ = [circle(-0.35, 1.75, 0.38, 30)]
    horns = [lens((0.2, 2.45), (0.45, 3.1), 0.25, 10), lens((0.7, 2.25), (1.15, 2.75), 0.25, 10)]
    belly = [S((-0.6, 0.6), (-0.1, 0.45), (0.5, 0.55))]
    arms = [S((-1.3, -0.05), (-1.6, 0.5), (-1.35, 0.85)), poly((-1.5, 0.75), (-1.55, 1.0), (-1.35, 0.85), (-1.3, 1.05), (-1.2, 0.8), closed=False),
            S((1.35, -0.05), (1.65, 0.5), (1.4, 0.85)), poly((1.55, 0.75), (1.6, 1.0), (1.4, 0.85), (1.35, 1.05), (1.25, 0.8), closed=False)]
    wing = [S((1.0, 1.6), (1.7, 2.3), (2.3, 2.2), (2.1, 1.75), (2.35, 1.4), (1.9, 1.25), (1.1, 1.2))]
    pieces = [poly((-2.8, -2.2), (-2.4, -1.8), (-2.2, -2.4)), poly((2.4, -2.5), (2.9, -2.2), (2.7, -2.75)), poly((-0.4, 3.1), (-0.1, 3.4), (0.1, 3.0))]
    spots = [ellipse(-0.9, -1.2, 0.3, 0.2, 20), ellipse(0.7, -1.6, 0.35, 0.22, 20), ellipse(1.3, -0.6, 0.2, 0.15, 16)]
    return make("Baby Dragon Hatching", [shell, head] + crack + mouth + nost + eye_ + horns + belly + arms + wing + pieces + spots,
                [eye(-0.3, 1.8, 0.18)])


@design("dragons_egg_nest", T)
def egg_nest(rng):
    egg = C((0.0, 2.9), (-1.2, 2.3), (-1.75, 0.8), (-1.6, -0.6), (-0.9, -1.4), (0.0, -1.55), (0.9, -1.4), (1.6, -0.6), (1.75, 0.8), (1.2, 2.3))
    rim = lambda x: -1.0 + 0.5 * (x / 2.9) ** 2
    i0 = max(range(len(egg)), key=lambda i: egg[i][1])
    egg = egg[i0:] + egg[1:i0 + 1]
    egg = [p for p in egg if p[1] > rim(p[0]) + 0.02]
    sc = []
    for i, y in enumerate([2.2, 1.6, 1.0, 0.4, -0.2]):
        half = 1.6 * math.sqrt(max(0.0, 1 - ((y - 0.65) / 2.3) ** 2)) - 0.2
        n = max(1, int(half * 2 / 0.6))
        for j in range(n):
            x = -half + (j + 0.5 + 0.5 * (i % 2)) * (2 * half / n)
            if abs(x) < half:
                sc.append(arc(x, y, 0.3, math.pi * 1.1, math.pi * 1.9, 8))
    nest = [S((-2.9, -0.5), (-2.7, -1.5), (-1.9, -2.3), (-0.6, -2.65), (0.6, -2.65), (1.9, -2.3), (2.7, -1.5), (2.9, -0.5)),
            S((-2.9, -0.5), (-2.2, -0.85), (-1.4, -0.75), (-0.7, -1.0), (0.0, -0.9), (0.7, -1.05), (1.4, -0.8), (2.2, -0.9), (2.9, -0.5))]
    twigs = [S((-3.3, -0.9), (-2.0, -1.4), (-0.4, -1.5), (1.0, -1.3), (2.4, -1.6), (3.3, -1.3)),
             S((-3.0, -1.8), (-1.6, -1.9), (0.2, -2.2), (1.8, -1.9), (3.1, -2.1)),
             S((-2.3, -2.4), (-0.6, -2.2), (1.2, -2.5), (2.2, -2.7)), S((-2.6, -1.0), (-1.4, -2.1), (-0.9, -2.9)),
             S((2.5, -0.95), (1.3, -1.9), (0.9, -2.9)), S((-0.3, -1.1), (0.4, -1.9), (0.3, -2.5)), [(-3.2, -0.2), (-2.6, -0.75)], [(3.2, -0.1), (2.6, -0.7)]]
    glow = [S((-2.3, 1.7), (-2.0, 2.0)), S((2.3, 1.7), (2.0, 2.0)), S((-2.5, 0.8), (-2.1, 0.85)), S((2.5, 0.8), (2.1, 0.85)),
            S((0.0, 3.2), (0.0, 3.6))]
    return make("Dragon Egg in a Nest", [egg] + sc + nest + twigs + glow)


@design("dragons_flying_front", T)
def flying_front(rng):
    half = S((0.0, 2.95), (0.35, 2.8), (0.45, 2.3), (0.3, 1.8), (0.32, 1.2), (0.6, 0.6), (0.75, -0.3), (0.55, -1.2), (0.2, -1.8),
             (0.15, -2.6), (0.0, -3.2))
    body = chain(mirror_x(half)[::-1], half[1:])
    wing = S((0.5, 0.9), (1.2, 1.6), (2.0, 2.6), (2.8, 3.1), (3.4, 3.2, 1))
    mem = [quad((3.4, 3.2), (3.0, 2.3), (3.6, 1.6), 12), quad((3.6, 1.6), (2.8, 1.2), (3.2, 0.2), 12), quad((3.2, 0.2), (2.3, 0.3), (2.5, -0.7), 12),
           quad((2.5, -0.7), (1.6, -0.2), (0.7, -0.4), 12)]
    fingers = [S((2.0, 2.6), (2.9, 2.0), (3.6, 1.6)), S((2.0, 2.6), (2.6, 1.3), (3.2, 0.2)), S((2.0, 2.6), (2.2, 1.0), (2.5, -0.7))]
    w = [chain(wing, *mem)] + fingers
    horns = [lens((0.22, 2.75), (0.75, 3.4), 0.18, 10)]
    legs = [S((0.6, -1.0), (1.0, -1.5), (0.9, -2.0)), poly((0.75, -2.0), (0.8, -2.25), (0.95, -2.05), (1.1, -2.25), (1.05, -1.95), closed=False)]
    arms = [S((0.6, 0.2), (0.95, -0.1), (0.85, -0.45))]
    plates = [S((-0.4 + 0.02 * k, 0.9 - 0.45 * k), (0.4 - 0.02 * k, 0.9 - 0.45 * k)) for k in range(4)]
    half_parts = w + horns + legs + arms
    tail_tip = [poly((0.0, -3.2), (-0.3, -3.5), (0.0, -3.9), (0.3, -3.5), closed=True)]
    nost = [S((-0.15, 2.0), (-0.1, 1.9)), S((0.15, 2.0), (0.1, 1.9))]
    return make("Dragon Flying with Wings Spread", [body] + half_parts + [mirror_x(p) for p in half_parts] + plates + tail_tip + nost,
                [eye(-0.22, 2.45, 0.07), eye(0.22, 2.45, 0.07)])


def neck_head(base, mid, tip, w0=0.55, w1=0.38, open_mouth=False, rot_deg=180.0):
    """A dragon neck from base through mid to tip ending in a head pointing along rot_deg."""
    c = S(base, mid, tip, n=6)
    below, above = sides(c, taper(w0, w1))
    a = math.radians(rot_deg)
    hx, hy = tip

    def H(px, py):
        return (hx + px * math.cos(a) - py * math.sin(a), hy + px * math.sin(a) + py * math.cos(a))
    k = 1.35
    if open_mouth:
        hd = [(0.0, -0.19), (0.45, -0.24), (0.95, -0.36, 1), (0.85, -0.22), (0.45, -0.06, 1), (1.2, 0.0, 1), (1.18, 0.12), (0.8, 0.2),
              (0.5, 0.3), (0.3, 0.32), (0.05, 0.3)]
        teeth = [zigzag(0.6 * k, 1.05 * k, -0.02 * k, 0.03 * k, 3)]
    else:
        hd = [(0.0, -0.19), (0.45, -0.22), (0.95, -0.16), (1.2, -0.02, 1), (1.12, 0.12), (0.8, 0.2), (0.5, 0.3), (0.3, 0.32), (0.05, 0.3)]
        teeth = [S((1.15, -0.02), (0.75, -0.05), (0.5, -0.02))]
    hd = [H(p[0] * k, p[1] * k) + tuple(p[2:]) for p in hd]
    head = S(*hd)
    horn_ = [H(0.25 * k, 0.31 * k), H(-0.2 * k, 0.6 * k), H(0.1 * k, 0.3 * k)]
    horn_ = [horn_, [H(0.0, 0.3 * k), H(-0.35 * k, 0.4 * k), H(-0.05 * k, 0.22 * k)]]
    for tz in teeth:
        horn_.append([H(px, py) for px, py in tz])
    eyep = H(0.55 * k, 0.17 * k)
    return chain(below, head, above), horn_, eyep


@design("dragons_two_headed", T)
def two_headed(rng):
    body = S((-0.9, 0.6), (-1.2, 0.0), (-1.25, -0.6), (-1.4, -1.6), (-1.75, -1.95, 1), (-1.55, -1.8, 1), (-1.4, -1.98, 1), (-1.22, -1.8, 1),
             (-1.05, -1.98, 1), (-0.95, -1.5), (-0.8, -0.9), (-0.2, -1.0), (0.5, -0.95), (0.7, -1.4), (0.75, -1.6), (0.45, -1.95, 1),
             (0.65, -1.8, 1), (0.82, -1.98, 1), (1.0, -1.8, 1), (1.18, -1.98, 1), (1.25, -1.5), (1.4, -0.9))
    tail_c = S((1.45, -0.55), (2.1, -0.9), (2.7, -0.7), (3.0, -0.1), (2.75, 0.4), n=6)
    below, above = sides(tail_c, taper(0.7, 0.08))
    back = S((1.2, 0.3), (0.5, 0.55), (-0.1, 0.65))
    outline = chain(body, below, above, back)
    n1, h1, e1 = neck_head((-0.35, 0.55), (-0.8, 1.6), (-1.6, 2.3), 0.6, 0.38, True, 175)
    n2, h2, e2 = neck_head((-0.05, 0.6), (0.2, 1.8), (-0.1, 2.9), 0.55, 0.36, False, 140)
    wing = bat_wing(0.5, 0.55, 0.75, 0.0)
    sp = spikes(above, 6, 0.2, t0=0.2, t1=0.95)
    return make("Two-Headed Dragon", [outline, n1, n2] + h1 + h2 + wing + sp, [eye(*e1, 0.06), eye(*e2, 0.06)])


@design("dragons_sea_serpent", T)
def sea_serpent(rng):
    humps = []
    for cx, r in [(-0.2, 0.9), (1.5, 0.75), (2.85, 0.5)]:
        humps.append(arc(cx, -0.6, r, 0, math.pi, 40))
        humps.append(arc(cx, -0.6, r - 0.45 if r > 0.6 else r - 0.3, 0, math.pi, 30))
    neck = S((-2.2, -0.6), (-2.0, 0.6), (-1.6, 1.6), (-1.9, 2.3), (-2.4, 2.4))
    neck2 = S((-1.4, -0.6), (-1.35, 0.5), (-1.0, 1.6), (-1.15, 2.5), (-1.6, 2.95), (-2.3, 2.85), (-2.9, 2.65, 1), (-2.85, 2.4), (-2.4, 2.4))
    fin = [poly((-1.05, 2.55), (-0.5, 2.6), (-0.95, 2.15), (-0.45, 2.0), (-1.0, 1.75), (-0.4, 1.4), (-1.15, 1.1), closed=False)]
    tail = [poly((3.35, -0.6), (3.6, 0.3), (3.45, -0.15), (3.95, 0.2), (3.35, -0.6), closed=False)]
    sp = spikes(arc(-0.2, -0.6, 0.9, math.pi, 0, 30), 4, 0.25) + spikes(arc(1.5, -0.6, 0.75, math.pi, 0, 30), 3, 0.22)
    waves = [S((-3.2, -0.6), (-2.7, -0.4), (-2.2, -0.6)), S((-1.4, -0.6), (-1.2, -0.45), (-1.1, -0.6)), S((0.7, -0.6), (0.73, -0.5), (0.75, -0.6)),
             S((2.25, -0.6), (2.3, -0.5), (2.35, -0.6)), wave(-3.2, 4.0, -1.4, 0.12, 6), wave(-2.6, 3.4, -2.2, 0.12, 5)]
    mouth = [S((-2.85, 2.5), (-2.4, 2.55))]
    return make("Sea Serpent Rising from the Waves", [neck, neck2] + humps + fin + tail + sp + waves + mouth, [eye(-2.05, 2.7, 0.07)])


# ------------------------------------------------------------ four-legged beasts

def beast(head, tail_center=None, tail_w=0.3, hind="paw"):
    """Lion-like body facing left; `head` is a point list from the back of
    the neck round the face to the throat.  Returns outline + far legs."""
    fore = [(-1.75, 0.0), (-1.6, -0.45), (-1.55, -0.9), (-1.5, -1.6), (-1.85, -1.8), (-1.9, -2.05, 1), (-1.2, -2.05, 1),
            (-1.22, -1.75), (-1.2, -1.0), (-1.0, -0.6), (-0.3, -0.75), (0.5, -0.7), (0.75, -0.85), (0.7, -1.3), (0.8, -1.6)]
    if hind == "hoof":
        rear = [(0.82, -1.8), (0.72, -2.05, 1), (1.1, -2.05, 1), (1.12, -1.8), (1.2, -1.4), (1.35, -1.0), (1.5, -0.5), (1.55, 0.1)]
    else:
        rear = [(0.55, -1.8), (0.5, -2.05, 1), (1.15, -2.05, 1), (1.15, -1.75), (1.2, -1.4), (1.35, -1.0), (1.5, -0.5), (1.55, 0.1)]
    back = [(1.3, 0.4), (0.3, 0.35), (-0.8, 0.5), (-1.1, 0.9)]
    if tail_center:
        below, above = sides(S(*tail_center, n=6), taper(tail_w, tail_w * 0.6))
        out = chain(S(*head, *fore, *rear[:-1]), below, above, S(*rear[-1:], *back, head[0]))
        outline = out
    else:
        outline = C(*head, *fore, *rear, *back)
    far = [S((-0.95, -0.7), (-0.9, -1.2), (-0.85, -1.75), (-1.0, -2.0, 1), (-0.45, -2.0, 1), (-0.55, -1.75), (-0.55, -1.2), (-0.6, -0.75)),
           S((0.35, -0.72), (0.4, -1.3), (0.35, -1.75), (0.2, -2.0, 1), (0.5, -2.0, 1))]
    return [outline] + far


def lion_tail(x0=1.5, y0=0.0):
    t = S((x0, y0), (2.1, 0.0), (2.4, 0.6), (2.3, 1.3), (2.6, 1.8), n=6)
    tuft = lens((2.6, 1.75), (2.75, 2.45), 0.35, 12)
    return [t, tuft]


@design("dragons_griffin", T)
def griffin(rng):
    head = [(-1.1, 0.9), (-1.0, 1.6), (-1.3, 2.25), (-1.75, 2.45), (-2.2, 2.3), (-2.55, 2.0), (-2.65, 1.65, 1), (-2.4, 1.75),
            (-2.15, 1.7), (-2.3, 1.5), (-2.1, 1.3), (-1.75, 1.3), (-1.6, 0.9)]
    b = beast(head, None)
    beak = [S((-2.15, 1.7), (-1.85, 1.62))]
    ear_tufts = [poly((-1.2, 2.2), (-0.9, 2.75), (-1.0, 2.15), closed=False)]
    feathers = [S((-1.55, 1.2), (-1.4, 0.95), (-1.25, 1.15), (-1.1, 0.9)), S((-1.6, 0.5), (-1.45, 0.3), (-1.3, 0.5), (-1.15, 0.3))]
    talon = [poly((-1.88, -1.95), (-2.1, -2.05), (-1.9, -2.05), closed=False)]
    w = feather_wing(-0.6, 0.45, 1.05, 0.15)
    tail = lion_tail()
    return make("Griffin with Eagle Head and Lion Body", b + beak + ear_tufts + feathers + talon + w + tail, [eye(-1.75, 1.95, 0.08)])


@design("dragons_hippogriff", T)
def hippogriff(rng):
    head = [(-1.1, 0.9), (-1.0, 1.6), (-1.3, 2.25), (-1.75, 2.45), (-2.2, 2.3), (-2.55, 2.0), (-2.65, 1.65, 1), (-2.4, 1.75),
            (-2.15, 1.7), (-2.3, 1.5), (-2.1, 1.3), (-1.75, 1.3), (-1.6, 0.9)]
    b = beast(head, None, hind="hoof")
    beak = [S((-2.15, 1.7), (-1.85, 1.62))]
    crest = [poly((-1.35, 2.35), (-0.85, 2.5), (-1.05, 2.1), (-0.65, 2.05), (-0.95, 1.75), closed=False)]
    w = feather_wing(-0.6, 0.45, 1.1, -0.1)
    tail = [S((1.5, 0.1), (2.1, 0.0), (2.4, -0.6), (2.3, -1.3), (2.55, -1.8)), S((1.55, -0.15), (1.95, -0.6), (1.9, -1.2), (2.1, -1.7)),
            S((2.1, 0.0), (2.6, -0.35), (2.75, -1.0), (2.65, -1.5))]
    ground = [S((-3.0, -2.08), (0.0, -2.06), (3.0, -2.1))]
    hooves = [[(-1.88, -1.85), (-1.2, -1.85)]]
    return make("Hippogriff Spreading Its Wings", b + beak + crest + w + tail + ground, [eye(-1.75, 1.95, 0.08)])


def lion_head():
    return [(-1.1, 0.9), (-1.2, 1.4), (-1.55, 1.68), (-2.05, 1.62), (-2.45, 1.35), (-2.65, 1.0), (-2.6, 0.75), (-2.3, 0.55),
            (-2.0, 0.5), (-1.75, 0.42), (-1.6, 0.2)]


def mane_around(cx, cy, r0, r1, n, a0=0.0, a1=TAU):
    pts = []
    for k in range(n + 1):
        a = a0 + (a1 - a0) * k / n
        rr = r1 if k % 2 else r0
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return S(*pts, n=4)


@design("dragons_chimera", T)
def chimera(rng):
    b = beast(lion_head(), None)
    mane = [mane_around(-1.75, 0.95, 1.0, 1.3, 16, math.radians(-110), math.radians(150))]
    face = [S((-2.6, 0.8), (-2.35, 0.72), (-2.15, 0.8)), S((-2.55, 1.05), (-2.45, 1.0))]
    goat = [S((0.0, 0.38), (-0.05, 1.2), (-0.2, 1.75), (-0.55, 2.2), (-0.95, 2.0), (-1.3, 1.65), (-1.35, 1.45), (-1.1, 1.4),
                  (-0.8, 1.5), (-0.6, 1.3), (-0.5, 0.45)),
            S((-0.45, 2.15), (-0.1, 2.75), (0.45, 2.85), (0.75, 2.4), (0.6, 2.05)), S((-0.3, 1.95), (0.1, 2.45), (0.45, 2.45)),
            poly((-1.15, 1.42), (-1.15, 0.95), (-0.95, 1.4), closed=False), lens((-0.75, 2.0), (-0.95, 2.4), 0.3, 8)]
    snake = S((1.5, 0.0), (2.2, 0.2), (2.4, 0.9), (2.0, 1.5), (2.3, 2.1), (2.8, 2.1), n=6)
    sb, sa = sides(snake, taper(0.3, 0.22))
    snake_body = chain(sb, S((2.8, 1.98), (3.1, 2.0), (3.25, 2.18, 1), (3.0, 2.35), (2.8, 2.22)), sa)
    tongue = [poly((3.25, 2.18), (3.5, 2.25), (3.6, 2.15), (3.5, 2.22), (3.6, 2.3), closed=False)]
    ground = [S((-3.0, -2.08), (0.0, -2.06), (3.0, -2.1))]
    return make("Chimera: Lion, Goat and Serpent", b + mane + face + goat + [snake_body] + tongue + ground,
                [eye(-2.1, 1.2, 0.07), eye(-0.65, 2.05, 0.06), eye(3.0, 2.2, 0.05)])


@design("dragons_manticore", T)
def manticore(rng):
    b = beast(lion_head(), None)
    mane = [mane_around(-1.75, 0.95, 1.0, 1.3, 16, math.radians(-110), math.radians(150))]
    face = [S((-2.6, 0.8), (-2.35, 0.72), (-2.15, 0.8)), zigzag(-2.55, -2.2, 0.68, 0.05, 3)]
    tail_c = S((1.5, 0.0), (2.2, 0.4), (2.6, 1.3), (2.3, 2.2), (1.5, 2.6), (0.8, 2.3), n=6)
    tb, ta = sides(tail_c, taper(0.35, 0.18))
    tail = chain(tb, ta)
    segs = [S(p, q) for p, q in zip(tube(tail_c, taper(0.35, 0.18), cap=False)[:len(tail_c)][6::8], tube(tail_c, taper(0.35, 0.18), cap=False)[len(tail_c):][::-1][6::8])]
    sting = [poly((0.85, 2.15), (0.4, 1.7), (0.75, 2.45), closed=False)]
    w = bat_wing(-0.5, 0.45, 0.7, 0.2)
    ground = [S((-3.0, -2.08), (0.0, -2.06), (3.0, -2.1))]
    return make("Manticore with a Scorpion Tail", b + mane + face + [tail] + segs + sting + w + ground, [eye(-2.1, 1.2, 0.07)])


@design("dragons_sphinx", T)
def sphinx(rng):
    # lying lion body with a human head and folded wings
    body = S((-1.4, 0.4), (-1.55, -0.3), (-1.7, -0.9), (-2.6, -1.05), (-3.0, -1.25, 1), (-2.95, -1.55, 1), (-1.4, -1.55),
             (0.5, -1.55), (1.8, -1.5), (2.4, -1.1), (2.5, -0.4), (2.1, 0.1), (1.0, 0.25), (-0.4, 0.35), (-0.8, 0.6))
    paw2 = [S((-1.2, -1.2), (-2.4, -1.25), (-2.75, -1.35), (-2.7, -1.55))]
    haunch = [S((0.9, -0.2), (1.6, -0.05), (2.0, -0.6), (1.7, -1.2), (0.9, -1.35), (0.6, -1.55))]
    head = C((-1.15, 2.55), (-1.6, 2.4), (-1.85, 2.0), (-1.85, 1.55), (-1.95, 1.4), (-1.75, 1.3), (-1.7, 1.05), (-1.45, 0.85),
             (-1.15, 0.95), (-0.95, 1.4), (-0.85, 2.0))
    headdress = [S((-1.2, 2.6), (-0.6, 2.4), (-0.5, 1.6), (-0.3, 0.6)), S((-0.9, 2.0), (-0.75, 1.3), (-0.95, 0.75)),
                 S((-1.85, 2.0), (-1.95, 2.35), (-1.6, 2.6))]
    w = feather_wing(-0.4, 0.3, 0.95, 0.1)
    tail = [S((2.45, -1.0), (3.0, -1.3), (3.2, -0.8), (3.0, -0.4)), poly((2.9, -0.55), (3.1, -0.1), (3.2, -0.45), closed=False)]
    base = [rect(-3.3, -2.3, 3.4, -1.55), [(-3.3, -1.9), (3.4, -1.9)]]
    return make("Winged Sphinx", [body, head] + paw2 + haunch + headdress + w + tail + base, [eye(-1.55, 1.75, 0.06)])


@design("dragons_wyvern", T)
def wyvern(rng):
    # two-legged dragon with wing-arms, perched on a branch, facing left
    body = S((-1.0, 1.0), (-1.2, 0.4), (-1.1, -0.3), (-0.8, -0.8), (-0.6, -1.05), (-0.75, -1.45), (-0.65, -1.75),
             (-1.0, -1.95, 1), (-0.8, -1.82, 1), (-0.62, -1.98, 1), (-0.45, -1.82, 1), (-0.28, -1.98, 1), (-0.25, -1.6), (-0.1, -1.1),
             (0.3, -0.95))
    tail_c = S((0.3, -0.7), (1.0, -1.1), (1.8, -1.6), (2.5, -2.4), (3.0, -2.6), n=6)
    tb, ta = sides(tail_c, taper(0.6, 0.06))
    back = S((0.6, -0.35), (0.4, 0.4), (-0.1, 1.0), (-0.4, 1.6))
    n1, h1, e1 = neck_head((-0.7, 1.2), (-0.8, 1.9), (-1.4, 2.4), 0.6, 0.4, True, 190)
    outline = chain(body, tb, ta, back)
    w = bat_wing(-0.3, 1.0, 1.0, 0.1)
    far = [transform(p, dx=-0.7, dy=1.0, s=0.7, rot=0.5) for p in bat_wing(0, 0)[:1]]
    branch = [S((-3.0, -2.0), (-1.0, -1.95), (0.5, -2.05), (1.4, -2.2)), S((-3.0, -2.35), (-1.0, -2.3), (0.5, -2.4), (1.4, -2.5)),
              S((-2.0, -2.0), (-2.4, -1.4), (-2.6, -1.1)), lens((-2.6, -1.1), (-3.1, -0.7), 0.4, 10)]
    belly = [S((-1.0, 0.6), (-0.75, 0.55)), S((-0.98, 0.1), (-0.7, 0.05)), S((-0.88, -0.4), (-0.6, -0.45))]
    return make("Wyvern on a Branch", [outline, n1] + h1 + w + far + branch + belly, [eye(*e1, 0.06)])


@design("dragons_hydra", T)
def hydra(rng):
    body = C((-1.6, -0.2), (-1.8, -1.0), (-1.7, -1.6), (-2.1, -1.95, 1), (-1.9, -1.8, 1), (-1.7, -1.98, 1), (-1.5, -1.8, 1), (-1.3, -1.98, 1),
             (-1.15, -1.5), (-0.5, -1.6), (0.6, -1.6), (0.9, -1.98, 1), (1.1, -1.8, 1), (1.3, -1.98, 1), (1.5, -1.8, 1), (1.7, -1.98, 1),
             (1.7, -1.4), (2.3, -1.6), (2.9, -1.4), (3.1, -0.9), (2.6, -1.05), (1.9, -0.6), (1.5, 0.1), (0.5, 0.35), (-0.6, 0.3))
    necks, heads, eyes_ = [], [], []
    for base, mid, tip, rot, op in [((-1.4, 0.0), (-2.2, 0.8), (-2.6, 1.6), 150, True), ((-0.9, 0.25), (-1.4, 1.5), (-1.3, 2.6), 120, False),
                                     ((-0.3, 0.35), (-0.2, 1.8), (0.2, 3.1), 95, True), ((0.3, 0.35), (0.9, 1.6), (1.1, 2.6), 65, False),
                                     ((0.9, 0.3), (1.9, 0.8), (2.5, 1.5), 35, True)]:
        nk, hh, ee = neck_head(base, mid, tip, 0.48, 0.32, op, rot)
        necks.append(nk)
        heads += hh
        eyes_.append(ee)
    ground = [S((-3.0, -2.0), (0.0, -1.98), (3.2, -2.0))]
    necks += spikes(S((1.5, 0.1), (1.9, -0.6), (2.6, -1.05), (3.1, -0.9), n=6)[::-1], 4, 0.2, side=1)
    return make("Many-Headed Hydra", [body] + necks + heads + ground, [eye(*e, 0.05) for e in eyes_])


@design("dragons_phoenix", T)
def phoenix(rng):
    body = C((-0.2, 1.75), (-0.55, 1.62), (-0.95, 1.55, 1), (-0.55, 1.38), (-0.4, 1.0), (-0.6, 0.3), (-0.45, -0.4), (0.0, -0.85),
             (0.45, -0.4), (0.6, 0.3), (0.4, 1.0), (0.3, 1.5), (0.1, 1.72))
    crest = [S((0.0, 1.72), (0.2, 2.3), (0.05, 2.75)), S((0.15, 1.68), (0.6, 2.2), (0.75, 2.6)), S((0.25, 1.6), (0.9, 1.85), (1.15, 2.15))]
    crest += [lens((0.05, 2.75), (-0.1, 3.1), 0.4, 8), lens((0.75, 2.6), (0.75, 2.95), 0.4, 8), lens((1.15, 2.15), (1.4, 2.4), 0.4, 8)]
    wl = feather_wing(0.35, 0.6, 1.05, 0.15)
    wr = [mirror_x(p) for p in feather_wing(0.35, 0.6, 1.05, 0.15)]
    tail = []
    for k, (ex, ey) in enumerate([(-2.3, -2.5), (-1.0, -3.1), (0.3, -3.3), (1.5, -3.0), (2.6, -2.3)]):
        c = S((0.0, -0.8), (ex * 0.35, -1.6), (ex * 0.75, ey * 0.8), (ex, ey), n=6)
        tail.append(band(c, lambda t: 0.08 + 0.35 * math.sin(math.pi * min(1.0, t * 1.1)) * (1 - 0.3 * t)))
    flames = [S((-1.6, -1.2), (-1.9, -0.7), (-1.6, -0.2)), S((1.7, -1.1), (2.0, -0.6), (1.75, -0.1)), S((-0.2, -2.0), (0.0, -1.6))]
    beak = [S((-0.95, 1.55), (-0.5, 1.5))]
    return make("Phoenix Rising from the Flames", [body] + crest + wl + wr + tail + flames + beak, [eye(-0.25, 1.48, 0.06)])


@design("dragons_centaur", T)
def centaur(rng):
    horse = C((-1.0, 0.4), (-1.25, -0.1), (-1.3, -0.5), (-1.25, -1.0), (-1.25, -1.6), (-1.35, -1.85, 1), (-1.0, -1.85, 1), (-1.0, -1.6),
              (-0.98, -1.05), (-0.85, -0.7), (-0.2, -0.82), (0.7, -0.8), (1.0, -0.95), (0.95, -1.35), (1.0, -1.6), (0.9, -1.85, 1),
              (1.25, -1.85, 1), (1.27, -1.6), (1.4, -1.25), (1.55, -0.85), (1.7, -0.3), (1.65, 0.15), (1.4, 0.4), (0.4, 0.35),
              (-0.4, 0.45))
    far = [S((-0.7, -0.78), (-0.65, -1.2), (-0.62, -1.6), (-0.7, -1.83, 1), (-0.38, -1.83, 1), (-0.36, -1.6), (-0.38, -0.8)),
           S((0.5, -0.8), (0.58, -1.2), (0.55, -1.6), (0.48, -1.83, 1), (0.78, -1.83, 1))]
    torso = S((-0.95, 0.35), (-1.05, 1.0), (-1.1, 1.6), (-1.35, 1.9), (-1.25, 2.05), (-0.85, 2.05), (-0.6, 2.1), (-0.3, 2.05),
              (-0.15, 1.95), (-0.25, 1.4), (-0.35, 0.8), (-0.4, 0.45))
    head = C((-0.72, 2.95), (-0.95, 2.85), (-1.0, 2.55), (-0.92, 2.32), (-0.7, 2.2), (-0.5, 2.35), (-0.45, 2.65), (-0.5, 2.9))
    hair = [S((-0.95, 2.85), (-0.7, 3.05), (-0.45, 2.85), (-0.35, 2.5), (-0.3, 2.25))]
    neck = [[(-0.82, 2.22), (-0.8, 2.08)], [(-0.6, 2.22), (-0.58, 2.1)]]
    arm_back = [S((-0.25, 1.95), (0.1, 1.9), (0.45, 2.05)), S((-0.25, 1.8), (0.1, 1.72), (0.45, 1.85))]
    arm_front = [S((-1.3, 1.95), (-1.85, 1.95), (-2.3, 2.1)), S((-1.25, 1.75), (-1.8, 1.75), (-2.3, 1.9))]
    bow = [S((-2.35, 3.2), (-2.75, 2.0), (-2.35, 0.8)), [(-2.35, 3.2), (0.45, 1.95)], [(-2.35, 0.8), (0.45, 1.95)]]
    arrow = [[(-2.9, 2.0), (0.6, 1.95)], poly((-2.9, 2.0), (-2.7, 2.12), (-2.7, 1.88))]
    tail = [S((1.65, 0.0), (2.2, -0.1), (2.4, -0.7), (2.3, -1.4), (2.5, -1.8)), S((1.68, -0.25), (2.0, -0.7), (1.95, -1.3), (2.1, -1.7))]
    belt = [S((-1.0, 0.65), (-0.65, 0.6), (-0.38, 0.62))]
    ground = [S((-3.0, -1.88), (0.0, -1.86), (3.0, -1.9))]
    return make("Centaur Archer", [horse, torso, head] + far + hair + neck + arm_back + arm_front + bow + arrow + tail + belt + ground,
                [eye(-0.85, 2.6, 0.05)])


# ------------------------------------------------------------ humanoid creatures

def resample(pts, step):
    out = [pts[0]]
    acc = 0.0
    for a, b in zip(pts, pts[1:]):
        d = math.dist(a, b)
        while acc + d >= step:
            t = (step - acc) / d
            a = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            out.append(a)
            d = math.dist(a, b)
            acc = 0.0
        acc += d
    out.append(pts[-1])
    return out


def jag(pts, amp, every=2, step=0.24):
    """Roughen an outline (fur) by pushing every other point outward."""
    pts = resample(pts, step)
    out = []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        if i % every == 0 or i == 0 or i == n - 1:
            out.append((x, y))
            continue
        a, b = pts[i - 1], pts[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        out.append((x + dy / L * amp, y - dx / L * amp))
    return out


def humanoid(sx=1.0, sy=1.0, neck_w=0.35, neck_y=1.6, club=None):
    """Front-view body below the head (closed outline, mirrored halves)."""
    half = [(neck_w, neck_y), (0.75, 1.48), (1.2, 1.35), (1.55, 0.8), (1.7, 0.0), (1.75, -0.7), (1.88, -1.0), (1.65, -1.22),
            (1.45, -0.95), (1.38, -0.25), (1.25, 0.4), (1.0, 0.65), (0.95, 0.0), (0.92, -0.6), (1.0, -0.9), (0.95, -1.8),
            (0.88, -2.5), (1.22, -2.72), (1.22, -2.95, 1), (0.25, -2.95, 1), (0.3, -2.5), (0.25, -1.6), (0.0, -1.15, 1)]
    half = [(p[0] * sx, p[1] * sy) + tuple(p[2:]) for p in half]
    right = S(*half, n=6)
    left = [(-x, y) for x, y in right[::-1]]
    return chain(left, right[1:])


def loincloth(sx=1.0, sy=1.0):
    return [poly((-0.95 * sx, -0.75 * sy), (0.95 * sx, -0.75 * sy), (0.6 * sx, -1.5 * sy), (0.15 * sx, -1.25 * sy), (-0.3 * sx, -1.55 * sy),
                 (-0.9 * sx, -1.3 * sy), closed=False), [(-0.93 * sx, -0.6 * sy), (0.93 * sx, -0.6 * sy)]]


@design("dragons_minotaur", T)
def minotaur(rng):
    body = humanoid(1.15, 1.0, 0.5)
    head = C((0.0, 1.55), (-0.45, 1.65), (-0.7, 2.1), (-0.75, 2.6), (-0.55, 3.0), (0.0, 3.1), (0.55, 3.0), (0.75, 2.6), (0.7, 2.1), (0.45, 1.65))
    muzzle = [ellipse(0.0, 1.95, 0.55, 0.35, 30), S((-0.3, 2.05), (-0.18, 1.95), (-0.25, 1.83)), S((0.3, 2.05), (0.18, 1.95), (0.25, 1.83)),
              arc(0.0, 1.62, 0.2, math.radians(200), math.radians(340), 12)]
    horns = [S((-0.6, 2.85), (-1.3, 2.9), (-1.75, 3.3), (-1.7, 3.8), (-1.45, 3.4), (-1.2, 3.15), (-0.7, 3.05)),
             S((0.6, 2.85), (1.3, 2.9), (1.75, 3.3), (1.7, 3.8), (1.45, 3.4), (1.2, 3.15), (0.7, 3.05))]
    ears = [lens((-0.72, 2.5), (-1.3, 2.35), 0.3, 10), lens((0.72, 2.5), (1.3, 2.35), 0.3, 10)]
    chest = [S((-0.7, 1.0), (-0.35, 0.75), (0.0, 0.95)), S((0.0, 0.95), (0.35, 0.75), (0.7, 1.0))]
    axe = [[(2.15, -2.0), (2.15, 2.6)], [(2.35, -2.0), (2.35, 2.6)], S((2.35, 2.4), (3.0, 2.8), (3.2, 2.0), (3.0, 1.3), (2.35, 1.6)),
           S((2.15, 2.4), (1.6, 2.7), (1.5, 2.0), (1.6, 1.4), (2.15, 1.6))]
    return make("Mighty Minotaur", [body, head] + muzzle + horns + ears + chest + loincloth(1.15) + axe,
                [eye(-0.35, 2.45, 0.08), eye(0.35, 2.45, 0.08)])


@design("dragons_cyclops", T)
def cyclops(rng):
    body = humanoid(1.25, 1.0, 0.5)
    head = C((0.0, 1.5), (-0.7, 1.7), (-0.95, 2.3), (-0.85, 2.95), (-0.4, 3.3), (0.4, 3.3), (0.85, 2.95), (0.95, 2.3), (0.7, 1.7))
    big_eye = [ellipse(0.0, 2.6, 0.45, 0.32, 30), S((-0.55, 3.0), (0.0, 3.1), (0.55, 3.0))]
    mouth = [S((-0.45, 1.95), (0.0, 1.8), (0.45, 1.95)), zigzag(-0.35, 0.35, 1.88, 0.05, 3)]
    nose = [S((-0.1, 2.35), (-0.15, 2.15), (0.1, 2.12))]
    ears = [arc(-0.95, 2.4, 0.22, math.pi / 2, 1.5 * math.pi, 10), arc(0.95, 2.4, 0.22, -math.pi / 2, math.pi / 2, 10)]
    club = [S((-2.15, -1.2), (-2.3, 0.5), (-2.55, 2.0), (-2.4, 2.6), (-1.85, 2.6), (-1.75, 2.0), (-1.95, 0.5), (-1.9, -1.2)),
            circle(-2.3, 2.1, 0.08, 8), circle(-2.0, 1.4, 0.08, 8)]
    pelt = [S((-1.25, 1.4), (-0.4, 0.4), (0.3, -0.3), (1.15, -0.65))]
    return make("One-Eyed Cyclops", [body, head] + big_eye + mouth + nose + ears + club + pelt + loincloth(1.25),
                [circle(0.0, 2.6, 0.14, 14)])


@design("dragons_ogre", T)
def ogre(rng):
    body = humanoid(1.4, 0.95, 0.55)
    belly = [ellipse(0.0, 0.0, 1.0, 0.85, 50)]
    head = C((0.0, 1.45), (-0.8, 1.6), (-1.0, 2.2), (-0.8, 2.75), (0.0, 2.95), (0.8, 2.75), (1.0, 2.2), (0.8, 1.6))
    ears = [S((-0.95, 2.4), (-1.5, 2.6), (-1.35, 2.15), (-0.98, 2.05)), S((0.95, 2.4), (1.5, 2.6), (1.35, 2.15), (0.98, 2.05))]
    nose = [S((-0.15, 2.35), (-0.3, 2.05), (0.0, 1.95), (0.3, 2.05), (0.15, 2.35))]
    mouth = [S((-0.55, 1.75), (0.0, 1.65), (0.55, 1.75)), poly((-0.35, 1.7), (-0.3, 2.0), (-0.22, 1.68), closed=False),
             poly((0.22, 1.68), (0.3, 2.0), (0.35, 1.7), closed=False)]
    brow = [S((-0.6, 2.6), (-0.3, 2.5)), S((0.3, 2.5), (0.6, 2.6))]
    club = [S((1.9, -1.05), (2.05, 0.5), (2.3, 2.2), (2.6, 2.7), (2.9, 2.4), (2.7, 1.9), (2.4, 0.5), (2.2, -1.05)), circle(2.55, 2.2, 0.08, 8)]
    patches = [rect(-0.95, -1.0, -0.45, -0.55)]
    return make("Grumpy Ogre with a Club", [body, head] + belly + ears + nose + mouth + brow + club + patches + loincloth(1.4, 0.95),
                [eye(-0.35, 2.35, 0.07), eye(0.35, 2.35, 0.07)])


@design("dragons_yeti", T)
def yeti(rng):
    body = jag(humanoid(1.35, 1.0, 0.6), 0.14)
    face = C((0.0, 1.65), (-0.55, 1.85), (-0.65, 2.35), (-0.45, 2.75), (0.0, 2.85), (0.45, 2.75), (0.65, 2.35), (0.55, 1.85))
    head = jag(C((0.0, 1.45), (-0.95, 1.7), (-1.05, 2.5), (-0.7, 3.2), (0.0, 3.4), (0.7, 3.2), (1.05, 2.5), (0.95, 1.7), n=10), 0.12)
    mouth = [S((-0.3, 2.0), (0.0, 1.9), (0.3, 2.0)), poly((-0.2, 1.97), (-0.15, 1.82), (-0.1, 1.95), closed=False),
             poly((0.1, 1.95), (0.15, 1.82), (0.2, 1.97), closed=False)]
    nose = [S((-0.12, 2.3), (0.0, 2.2), (0.12, 2.3))]
    brow = [S((-0.5, 2.62), (-0.15, 2.55)), S((0.15, 2.55), (0.5, 2.62))]
    peaks = [poly((-3.6, -2.95), (-2.6, -0.6), (-2.2, -1.3), (-1.75, -0.4), closed=False), poly((1.8, -0.5), (2.6, 0.6), (3.6, -2.95), closed=False),
             poly((-2.95, -1.4), (-2.6, -1.0), (-2.3, -1.6), closed=False)]
    flakes = [star(x, y, 0.15, 6, 0.3) for x, y in [(-2.8, 2.6), (2.6, 2.4), (-2.2, 1.0), (2.8, 1.4), (-3.2, 0.3)]]
    return make("Abominable Snow Yeti", [body, head, face] + mouth + nose + brow + peaks + flakes,
                [eye(-0.28, 2.42, 0.07), eye(0.28, 2.42, 0.07)])


@design("dragons_stone_golem", T)
def stone_golem(rng):
    torso = poly((-1.2, 1.6), (1.2, 1.6), (1.4, 0.2), (0.9, -0.7), (-0.9, -0.7), (-1.4, 0.2))
    head = poly((-0.55, 1.6), (-0.6, 2.4), (-0.3, 2.75), (0.35, 2.75), (0.6, 2.35), (0.55, 1.6))
    arms = [poly((-1.25, 1.5), (-2.1, 1.3), (-2.3, 0.3), (-1.4, 0.4)), poly((-2.3, 0.25), (-2.5, -0.9), (-1.8, -1.0), (-1.6, 0.3)),
            poly((-2.6, -0.95), (-2.7, -1.7), (-1.7, -1.75), (-1.75, -1.0)),
            poly((1.25, 1.5), (2.1, 1.3), (2.3, 0.3), (1.4, 0.4)), poly((2.3, 0.25), (2.5, -0.9), (1.8, -1.0), (1.6, 0.3)),
            poly((2.6, -0.95), (2.7, -1.7), (1.7, -1.75), (1.75, -1.0))]
    legs = [poly((-0.9, -0.7), (-1.1, -1.8), (-0.3, -1.85), (-0.15, -0.7)), poly((-1.15, -1.85), (-1.3, -2.9), (-0.1, -2.9), (-0.3, -1.9)),
            poly((0.9, -0.7), (1.1, -1.8), (0.3, -1.85), (0.15, -0.7)), poly((1.15, -1.85), (1.3, -2.9), (0.1, -2.9), (0.3, -1.9))]
    cracks = [S((-0.8, 1.2), (-0.4, 0.8), (-0.6, 0.3)), S((0.5, 0.9), (0.8, 0.4), (0.6, -0.2)), S((-0.3, 2.6), (-0.1, 2.45))]
    rune = [poly((0.0, 0.7), (-0.3, 0.2), (0.0, -0.3), (0.3, 0.2))]
    moss = [S((-1.2, 1.6), (-0.9, 1.75), (-0.6, 1.6)), S((0.6, 1.6), (0.9, 1.78), (1.2, 1.6))]
    return make("Ancient Stone Golem", [torso, head] + arms + legs + cracks + rune + moss,
                [poly((-0.38, 2.15), (-0.12, 2.15), (-0.25, 2.0)), poly((0.12, 2.15), (0.38, 2.15), (0.25, 2.0))])


@design("dragons_goblin", T)
def goblin(rng):
    body = humanoid(0.95, 0.75, 0.3)
    head = C((0.0, 1.15), (-0.6, 1.3), (-0.8, 1.8), (-0.65, 2.3), (0.0, 2.5), (0.65, 2.3), (0.8, 1.8), (0.6, 1.3))
    ears = [poly((-0.75, 2.0), (-1.9, 2.45), (-0.8, 1.6)), poly((0.75, 2.0), (1.9, 2.45), (0.8, 1.6))]
    nose = [S((-0.1, 2.0), (0.05, 1.55), (0.3, 1.45), (0.12, 1.7))]
    grin = [S((-0.45, 1.4), (0.0, 1.25), (0.45, 1.4)), poly((-0.2, 1.33), (-0.15, 1.2), (-0.1, 1.31), closed=False)]
    vest = [poly((-0.3, 1.18), (-0.55, -0.5), (-0.85, -0.55), closed=False), poly((0.3, 1.18), (0.55, -0.5), (0.85, -0.55), closed=False)]
    belt = [[(-0.88, -0.45), (0.88, -0.45)], rect(-0.15, -0.6, 0.15, -0.3)]
    lantern = [[(1.7, -0.75), (1.7, -1.05)], rrect(1.45, -1.75, 1.95, -1.05, 0.08), lens((1.7, -1.6), (1.7, -1.2), 0.3, 8)]
    sack = [S((-1.6, -0.6), (-2.3, -0.9), (-2.5, -1.8), (-1.9, -2.2), (-1.3, -1.9), (-1.4, -1.0), (-1.6, -0.6))]
    return make("Mischievous Goblin", [body, head] + ears + nose + grin + vest + belt + lantern + sack,
                [eye(-0.3, 1.85, 0.08), eye(0.3, 1.85, 0.08)])


# ------------------------------------------------------------ more mythical beasts

def dog_head(dx, dy, s=1.0, rot=0.0, snarl=False):
    pts = [(0.35, 0.55), (-0.1, 0.6), (-0.55, 0.45), (-1.05, 0.25), (-1.15, 0.05, 1), (-0.95, -0.1), (-0.5, -0.12) if not snarl else (-0.6, -0.05),
           (-0.95, -0.25) if snarl else (-0.75, -0.2), (-0.55, -0.35), (-0.1, -0.35), (0.35, -0.2)]
    head = S(*pts)
    ear = poly((0.0, 0.55), (0.2, 1.05), (0.4, 0.45), closed=False)
    nose = [ellipse(-1.05, 0.15, 0.1, 0.07, 10)]
    extra = [zigzag(-0.9, -0.6, -0.08, 0.04, 3)] if snarl else []
    parts = [head, ear] + nose + extra
    return [transform(p, dx=dx, dy=dy, s=s, rot=rot) for p in parts], transform([(-0.45, 0.25)], dx=dx, dy=dy, s=s, rot=rot)[0]


@design("dragons_cerberus", T)
def cerberus(rng):
    body = C((-1.3, 0.3), (-1.55, -0.3), (-1.5, -0.8), (-1.45, -1.6), (-1.75, -1.85), (-1.8, -2.05, 1), (-1.15, -2.05, 1), (-1.15, -1.7),
             (-1.1, -1.0), (-0.95, -0.7), (-0.2, -0.85), (0.6, -0.8), (0.8, -1.0), (0.75, -1.5), (0.6, -1.8), (0.55, -2.05, 1),
             (1.2, -2.05, 1), (1.15, -1.7), (1.3, -1.3), (1.5, -0.8), (1.6, -0.1), (1.35, 0.3), (0.4, 0.4), (-0.6, 0.5))
    far = [S((-0.85, -0.8), (-0.8, -1.4), (-0.85, -1.75), (-1.0, -2.0, 1), (-0.45, -2.0, 1), (-0.55, -1.75), (-0.5, -1.2), (-0.5, -0.82))]
    H = [(-1.55, 0.95, 0.9, 0.15, True, False), (-0.45, 1.55, 0.9, -0.05, False, False), (0.55, 1.0, 0.85, 0.0, True, True)]
    heads, eyes_, necks = [], [], []
    for dx, dy, s_, rot, sn, m in H:
        h, e = dog_head(dx, dy, s_, rot, sn)
        a, b = transform([(0.2, -0.3), (-0.45, -0.32)], dx=dx, dy=dy, s=s_, rot=rot)
        if m:
            h = [mirror_x(p, dx) for p in h]
            e = (2 * dx - e[0], e[1])
            a, b = (2 * dx - a[0], a[1]), (2 * dx - b[0], b[1])
        heads += h
        eyes_.append(e)
        necks += [S(a, (a[0] + 0.05, 0.4)), S(b, (b[0] + 0.1, 0.35))]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 0.25
        necks.append(zigzag(min(a[0], b[0]) + 0.05, max(a[0], b[0]) + 0.1, my, 0.07, 3))
    h1, h2, h3 = heads, [], []
    e1, e2, e3 = eyes_
    collars = []
    tail = [S((1.55, 0.0), (2.2, 0.4), (2.5, 1.1), (2.3, 1.6)), S((1.6, -0.25), (2.35, 0.2), (2.7, 0.9), (2.3, 1.6))]
    ground = [S((-3.0, -2.08), (0.0, -2.06), (3.0, -2.1))]
    return make("Cerberus the Three-Headed Hound", [body] + far + necks + h1 + h2 + h3 + collars + tail + ground,
                [eye(*e1, 0.06), eye(*e2, 0.06), eye(*e3, 0.06)])


@design("dragons_kitsune", T)
def kitsune(rng):
    body = C((-0.9, 2.15), (-1.05, 2.7, 1), (-1.25, 2.05), (-1.6, 1.75), (-2.0, 1.45, 1), (-1.6, 1.25), (-1.2, 1.15), (-1.0, 0.6),
             (-1.2, -0.3), (-1.25, -1.2), (-1.55, -1.55), (-1.55, -1.75, 1), (-0.9, -1.75, 1), (-0.85, -1.3), (-0.6, -1.0), (-0.3, -1.4),
             (-0.6, -1.75, 1), (0.6, -1.75, 1), (0.8, -1.2), (0.65, -0.3), (0.2, 0.5), (-0.35, 1.2), (-0.55, 1.85), (-0.6, 2.55, 1))
    tails = []
    for k in range(9):
        a = math.radians(-30 + k * 15)
        r0, r1 = 0.6, 3.1
        base = (0.55 + r0 * math.cos(a), -1.0 + r0 * math.sin(a))
        mid = (0.55 + 1.7 * math.cos(a + 0.2), -1.0 + 1.7 * math.sin(a + 0.2))
        tip = (0.55 + r1 * math.cos(a - 0.12), -1.0 + r1 * math.sin(a - 0.12))
        c = S(base, mid, tip, n=6)
        wf = lambda t: 0.1 + 0.62 * math.sin(math.pi * t) ** 0.5 * (1 - 0.75 * t)
        tails.append(band(c, wf) if k in (0, 8) else tube(c, wf, cap=False)[:len(c)])
        e = tube(c, wf, cap=False)
        n = len(c)
        j = int(n * 0.8)
        if k not in (0, 8):
            tails.append(S(*e[2 * n - 1 - int(n * 0.45):]))
        tails.append(S(e[j], c[min(n - 1, j + 2)], e[2 * n - 1 - j]))
    ear_in = [poly((-0.95, 2.2), (-1.05, 2.5), (-1.15, 2.1), closed=False)]
    chest = [S((-1.1, 0.9), (-0.85, 0.5), (-1.05, 0.2), (-0.8, -0.1))]
    flames = [lens((-2.3, 2.6), (-2.3, 3.2), 0.4, 10), lens((-2.7, 2.2), (-2.75, 2.65), 0.4, 8)]
    return make("Nine-Tailed Kitsune Fox", [body] + tails + ear_in + chest + flames, [eye(-1.35, 1.75, 0.07)])


@design("dragons_qilin", T)
def qilin(rng):
    head = [(-1.1, 0.9), (-1.05, 1.55), (-1.4, 2.0), (-1.9, 2.05), (-2.4, 1.8), (-2.7, 1.5, 1), (-2.45, 1.38), (-2.1, 1.38),
            (-2.4, 1.15), (-2.1, 1.0), (-1.75, 0.95), (-1.6, 0.55)]
    b = beast(head, None, hind="hoof")
    antler = [S((-1.45, 1.95), (-1.3, 2.6), (-0.9, 3.0)), S((-1.35, 2.4), (-1.75, 2.75)), S((-1.2, 1.95), (-0.85, 2.4), (-0.4, 2.6))]
    whisk = [S((-2.6, 1.45), (-3.0, 1.75), (-3.3, 1.6)), S((-2.4, 1.1), (-2.8, 0.85), (-3.1, 1.0))]
    mane = [poly((-1.15, 1.7), (-0.6, 1.8), (-0.85, 1.4), (-0.3, 1.35), (-0.7, 1.0), (-0.2, 0.85), (-0.75, 0.6), closed=False)]
    scales = scales_rows(0.0, -0.05, 2.2, 0.6, 2, 6, 0.2)
    flames = [lens((-1.45, -0.95), (-1.85, -0.35), 0.35, 10), lens((-0.75, -0.95), (-1.0, -0.4), 0.35, 10), lens((1.05, -1.0), (1.5, -0.5), 0.35, 10)]
    tail = [S((1.5, 0.1), (2.1, 0.5), (2.3, 1.2)), lens((2.3, 1.2), (2.7, 2.1), 0.35, 12), lens((2.2, 1.4), (2.15, 2.2), 0.3, 10)]
    clouds = [spiral(-2.7, -1.6, 0.05, 0.4, 1.2), spiral(2.6, -1.5, 0.05, 0.35, 1.2), S((-3.1, -2.1), (-2.3, -2.1), (-1.8, -1.9)),
              S((2.1, -2.1), (2.9, -2.1), (3.2, -1.85))]
    return make("Qilin with Antlers and Scales", b + antler + whisk + mane + scales + flames + tail + clouds, [eye(-1.85, 1.65, 0.07)])


@design("dragons_roc", T)
def roc(rng):
    body = C((-2.1, 1.8), (-2.5, 1.7), (-2.95, 1.4, 1), (-2.65, 1.3), (-2.3, 1.15), (-1.8, 0.75), (-1.2, 0.2), (-0.4, -0.1), (0.5, -0.1),
             (1.3, 0.1), (2.8, 0.6, 1), (2.45, 0.32), (2.95, 0.12, 1), (2.4, -0.02), (2.75, -0.35, 1), (1.4, 0.4), (0.4, 0.75), (-0.8, 1.05),
             (-1.6, 1.5))
    beak = [S((-2.65, 1.3), (-2.4, 1.38), (-2.2, 1.45))]
    wing_up = [S((-0.8, 0.75), (-0.6, 1.8), (0.0, 2.8), (1.0, 3.4), (2.3, 3.6, 1)),
               S((2.3, 3.6), (1.9, 3.05), (2.5, 2.9, 1), (1.7, 2.45), (2.2, 2.2, 1), (1.4, 1.85), (1.7, 1.45, 1), (1.0, 1.25), (0.8, 0.7))]
    wing_dn = [S((-0.4, 0.3), (-0.6, -0.6), (-0.3, -1.4), (0.3, -1.9, 1)), S((0.3, -1.9), (0.4, -1.3), (0.8, -1.5, 1), (0.8, -0.9),
                                                                              (1.2, -1.0, 1), (1.0, -0.4), (0.9, 0.2))]
    feathers = [S((-0.3, 1.2), (0.5, 2.0), (1.4, 2.9)), S((-0.4, -0.4), (0.2, -0.9))]
    talons = [S((-0.2, -0.08), (-0.3, -0.35), (-0.45, -0.5)), S((0.4, -0.1), (0.45, -0.4), (0.3, -0.55)),
              poly((-0.6, -0.42), (-0.45, -0.5), (-0.5, -0.65), closed=False), poly((0.4, -0.45), (0.3, -0.55), (0.42, -0.7), closed=False)]
    boulder = [C((-0.6, -0.5), (0.2, -0.45), (0.8, -0.8), (0.9, -1.4), (0.4, -1.8), (-0.4, -1.75), (-0.9, -1.3), (-0.85, -0.8))]
    boulder = [C((-0.45, -0.45), (0.3, -0.4), (0.95, -0.75), (1.0, -1.35), (0.5, -1.75), (-0.3, -1.7), (-0.75, -1.25), (-0.7, -0.75))]
    mountains = [poly((-3.4, -3.0), (-2.4, -1.6), (-1.9, -2.2), (-1.0, -1.2), (0.0, -2.4), (1.0, -1.7), (1.9, -2.5), (2.6, -1.9), (3.4, -3.0), closed=False)]
    return make("Giant Roc Soaring over Mountains", [body] + beak + wing_up + feathers + talons + boulder + mountains,
                [eye(-2.35, 1.42, 0.06)])


@design("dragons_troll_bridge", T)
def troll_bridge(rng):
    bridge = [S((-3.4, 0.6), (3.4, 0.6)), S((-3.4, 1.1), (3.4, 1.1)), chain([(-3.4, -2.6)], [(-2.2, -2.6)], arc(0.0, -2.6, 2.2, math.pi, 0, 50),
                                                                         [(3.4, -2.6)])]
    stones = [[(x, 0.6), (x, 1.1)] for x in (-2.6, -1.4, -0.2, 1.0, 2.2)] + [S((-2.6, -1.0), (-3.4, -1.0)), S((2.6, -1.0), (3.4, -1.0)),
                                                                           S((-2.9, -1.0), (-2.9, 0.6)), S((2.9, -1.0), (2.9, 0.6))]
    head = C((0.0, 0.25), (-0.75, 0.1), (-1.0, -0.4), (-0.95, -1.0), (-0.6, -1.4), (0.0, -1.5), (0.6, -1.4), (0.95, -1.0), (1.0, -0.4), (0.75, 0.1))
    nose = [S((-0.15, -0.35), (-0.35, -0.85), (-0.1, -1.05), (0.2, -0.95), (0.15, -0.4))]
    mouth = [S((-0.55, -1.15), (0.0, -1.25), (0.55, -1.15)), poly((-0.4, -1.18), (-0.35, -0.98), (-0.28, -1.2), closed=False)]
    ears = [S((-0.95, -0.45), (-1.5, -0.2), (-1.35, -0.8), (-0.98, -0.75)), S((0.95, -0.45), (1.5, -0.2), (1.35, -0.8), (0.98, -0.75))]
    hair = [S((-0.5, 0.15), (-0.7, 0.45), (-0.3, 0.4)), S((0.1, 0.25), (0.2, 0.55), (0.45, 0.2))]
    hands = [S((-1.6, -1.0), (-1.8, -0.4), (-1.5, -0.2), (-1.3, -0.5), (-1.2, -1.1)), S((1.6, -1.0), (1.8, -0.4), (1.5, -0.2), (1.3, -0.5), (1.2, -1.1))]
    water = [wave(-3.4, -2.3, -2.9, 0.06, 2, 20), wave(-1.6, 1.6, -2.9, 0.06, 4, 40), wave(2.3, 3.4, -2.9, 0.06, 2, 20)]
    goat = [S((-3.0, 1.1), (-2.9, 1.6), (-2.5, 1.75), (-2.0, 1.7), (-1.9, 1.1)), S((-3.0, 1.6), (-3.3, 1.9), (-3.15, 2.2)),
            poly((-3.1, 2.15), (-3.0, 2.5), (-2.95, 2.15), closed=False)]
    return make("Troll Hiding under the Bridge", bridge + stones + [head] + nose + mouth + ears + hair + hands + water + goat,
                [eye(-0.42, -0.45, 0.08), eye(0.42, -0.45, 0.08)])


@design("dragons_loch_ness", T)
def loch_ness(rng):
    neck = S((-1.5, -0.6), (-1.6, 0.6), (-1.3, 1.6), (-1.5, 2.2), (-2.0, 2.4), (-2.6, 2.3), (-2.75, 2.1, 1), (-2.35, 1.95), (-2.0, 1.85),
             (-1.9, 1.5), (-2.1, 0.6), (-2.2, -0.6))
    humps = [arc(0.0, -0.6, 0.65, 0, math.pi, 30), arc(1.6, -0.6, 0.5, 0, math.pi, 30), S((2.6, -0.6), (2.9, -0.1), (3.3, 0.0), (3.0, -0.6))]
    flipper = [S((-0.5, -0.6), (-0.9, -0.2), (-0.7, -0.6))]
    water = [wave(-3.3, 3.5, -0.6, 0.05, 9), wave(-2.6, 2.8, -1.4, 0.08, 6), wave(-3.2, 3.2, -2.2, 0.08, 6)]
    hills = [S((-3.4, 0.2), (-2.6, 0.9), (-2.2, 0.6)), S((0.4, 0.6), (1.4, 1.6), (2.4, 1.1), (3.4, 1.8))]
    castle = [poly((1.6, 1.4), (1.6, 2.3), (1.75, 2.3), (1.75, 2.15), (1.9, 2.15), (1.9, 2.3), (2.05, 2.3), (2.05, 1.25), closed=False),
              poly((2.05, 1.6), (2.6, 1.6), (2.6, 1.3), closed=False), rect(1.75, 1.75, 1.9, 2.0)]
    mouth = [S((-2.7, 2.15), (-2.3, 2.05))]
    return make("Loch Ness Monster", [neck] + humps + flipper + water + hills + castle + mouth, [eye(-2.15, 2.15, 0.07)])


@design("dragons_fire_salamander", T)
def fire_salamander(rng):
    half = S((0.0, 2.65), (0.28, 2.5), (0.42, 2.05), (0.32, 1.62), (0.48, 1.2), (0.55, 0.4), (0.48, -0.4), (0.28, -0.95))
    tail_c = S((0.0, -0.8), (0.55, -1.7), (0.3, -2.5), (-0.5, -2.85), (-1.3, -2.6), (-1.7, -2.0), n=6)
    tb, ta = sides(tail_c, taper(0.56, 0.06))
    left = [(-x, y) for x, y in half]
    outline = chain(left[::-1], half[1:])
    tail = chain(tb, ta)
    legs = []
    for sgn in (1, -1):
        for (a0, a1, a2) in [((0.42, 1.15), (1.05, 1.35), (1.25, 1.95)), ((0.45, -0.3), (1.1, -0.45), (1.25, -1.05))]:
            c = S((a0[0] * sgn, a0[1]), (a1[0] * sgn, a1[1]), (a2[0] * sgn, a2[1]), n=6)
            legs.append(tube(c, taper(0.32, 0.22), cap=False))
            tx, ty = a2[0] * sgn, a2[1]
            dy = 1 if a2[1] > a1[1] else -1
            for k in (-1, 0, 1):
                legs.append([(tx + 0.1 * k * sgn, ty + 0.05 * dy), (tx + 0.3 * k * sgn + 0.05 * sgn, ty + 0.38 * dy)])
    spots = [ellipse(x, y, 0.13, 0.09, 12) for x, y in [(-0.2, 1.0), (0.18, 0.5), (-0.15, -0.1), (0.2, -0.55), (0.3, -1.6), (-0.3, -2.45)]]
    fire = []
    for x, h in [(-2.8, 1.6), (-2.0, 2.2), (2.0, 2.0), (2.8, 1.5)]:
        fire.append(S((x - 0.4, -2.9), (x - 0.5, -2.2), (x - 0.15, -2.9 + h * 0.55), (x, -2.9 + h, 1), (x + 0.2, -2.9 + h * 0.5),
                      (x + 0.5, -2.2), (x + 0.4, -2.9)))
    sparks = [lens((-2.3, 1.2), (-2.4, 1.6), 0.4, 8), lens((2.4, 1.0), (2.5, 1.4), 0.4, 8), lens((-1.6, 2.4), (-1.65, 2.8), 0.4, 8)]
    return make("Fire Salamander among the Flames", [outline, tail] + legs + spots + fire + sparks,
                [eye(-0.22, 2.15, 0.07), eye(0.22, 2.15, 0.07)])


@design("dragons_cockatrice", T)
def cockatrice(rng):
    body = S((-1.0, 1.6), (-1.35, 1.5), (-1.75, 1.35, 1), (-1.35, 1.2), (-1.1, 1.0), (-1.15, 0.5), (-1.3, -0.2), (-1.0, -0.8), (-0.3, -1.1),
             (0.4, -1.0))
    tail_c = S((0.3, -0.75), (1.2, -1.0), (2.0, -1.6), (2.6, -2.3), (2.3, -2.8), (1.6, -2.6), n=6)
    tb, ta = sides(tail_c, taper(0.55, 0.08))
    back = S((0.7, -0.35), (0.3, 0.3), (-0.35, 0.9), (-0.55, 1.5), (-1.0, 1.6))
    outline = chain(body, tb, ta, back)
    comb = [S((-1.0, 1.6), (-1.1, 1.95), (-0.85, 1.85), (-0.75, 2.15), (-0.55, 1.95), (-0.4, 2.1), (-0.4, 1.7), (-0.55, 1.5))]
    wattle = [lens((-1.3, 1.2), (-1.25, 0.7), 0.4, 10)]
    wing = bat_wing(-0.2, 0.6, 0.8, 0.15)
    legs = [S((-0.6, -1.08), (-0.65, -1.7), (-0.6, -2.3)), S((-0.3, -1.1), (-0.25, -1.7), (-0.3, -2.3)),
            poly((-0.95, -2.5), (-0.6, -2.3), (-0.3, -2.5), closed=False), poly((-0.6, -2.3), (-0.55, -2.55), closed=False),
            poly((-0.65, -2.45), (-0.3, -2.3), (-0.05, -2.45), closed=False)]
    tip = [poly((1.6, -2.6), (1.25, -2.4), (1.35, -2.8), closed=False)]
    scales = [arc(x, y, 0.2, math.pi * 1.1, math.pi * 1.9, 8) for x, y in [(1.1, -1.0), (1.6, -1.35), (2.05, -1.8)]]
    ground = [S((-2.0, -2.55), (0.5, -2.55))]
    return make("Cockatrice: Rooster-Headed Dragon", [outline] + comb + wattle + wing + legs + tip + scales + ground, [eye(-1.15, 1.42, 0.06)])


@design("dragons_basilisk", T)
def basilisk(rng):
    c = S((-1.0, 1.4), (-0.6, 0.5), (0.5, -0.1), (1.6, -0.6), (1.9, -1.6), (1.0, -2.3), (-0.6, -2.2), (-1.8, -1.8), (-2.6, -2.2),
          (-2.8, -2.8), n=6)
    b, a = sides(c, taper(0.85, 0.06))
    head = S((-0.95, 1.8), (-1.6, 2.0), (-2.2, 1.95), (-2.65, 1.75, 1), (-2.3, 1.55), (-1.9, 1.5), (-2.35, 1.3, 1), (-1.9, 1.05), (-1.3, 0.95))
    hp = [(-0.95, 1.8), (-1.6, 2.0), (-2.2, 1.95), (-2.65, 1.75, 1), (-2.3, 1.55), (-1.9, 1.5), (-2.35, 1.3, 1), (-1.9, 1.05), (-1.3, 0.95)]
    if a[-1][1] < b[0][1]:
        hp = hp[::-1]
    outline = chain(b, a, S(a[-1], *hp, b[0]))
    crown = [poly((-1.6, 2.0), (-1.5, 2.6), (-1.25, 2.2), (-1.0, 2.75), (-0.8, 2.15), (-0.5, 2.55), (-0.55, 1.85), closed=False)]
    fangs = [poly((-2.2, 1.55), (-2.15, 1.35), (-2.05, 1.53), closed=False)]
    tongue = [poly((-2.3, 1.42), (-2.85, 1.45), (-3.05, 1.3), (-2.9, 1.45), (-3.05, 1.6), closed=False)]
    belly = [S(*tube(c, taper(0.85 * 0.45, 0.03), cap=False)[:len(c)][4:-8])]
    sc = []
    for k in range(6, len(c) - 12, 9):
        p, q = tube(c, taper(0.85, 0.06), cap=False)[k], tube(c, taper(0.85 * 0.45, 0.03), cap=False)[k]
        sc.append([p, q])
    rocks = [S((-3.2, -2.9), (-2.4, -2.95), (-1.6, -2.85)), S((1.0, -2.9), (2.2, -2.95), (3.0, -2.8))]
    return make("Crowned Basilisk Serpent", [outline] + crown + fangs + tongue + belly + sc + rocks, [eye(-1.6, 1.7, 0.08)])


@design("dragons_medusa", T)
def medusa(rng):
    face = C((0.0, 1.3), (-0.75, 1.15), (-1.05, 0.5), (-1.0, -0.4), (-0.6, -1.2), (0.0, -1.5), (0.6, -1.2), (1.0, -0.4), (1.05, 0.5), (0.75, 1.15))
    eyes_ = [lens((-0.65, 0.25), (-0.15, 0.25), 0.3, 12), lens((0.15, 0.25), (0.65, 0.25), 0.3, 12)]
    brows = [S((-0.7, 0.55), (-0.4, 0.65), (-0.15, 0.5)), S((0.15, 0.5), (0.4, 0.65), (0.7, 0.55))]
    nose = [S((0.0, 0.15), (-0.08, -0.35), (0.1, -0.42))]
    lips = [S((-0.35, -0.8), (0.0, -0.72), (0.35, -0.8)), S((-0.35, -0.8), (0.0, -0.95), (0.35, -0.8))]
    neck = [S((-0.45, -1.35), (-0.5, -2.2), (-1.4, -2.6)), S((0.45, -1.35), (0.5, -2.2), (1.4, -2.6))]
    snakes = []
    hints = []
    for k in range(9):
        a = math.radians(15 + k * 18.75)
        bx, by = 0.95 * math.cos(a), 0.4 + 0.95 * math.sin(a)
        ex, ey = 2.6 * math.cos(a), 0.6 + 2.4 * math.sin(a)
        mx, my = (bx + ex) / 2 + 0.35 * math.sin(a * 3), (by + ey) / 2 + 0.3 * math.cos(a * 2)
        ang0 = math.atan2(ey - by, ex - bx)
        nx, ny = -math.sin(ang0), math.cos(ang0)
        L = math.dist((bx, by), (ex, ey))
        cpts = []
        for i in range(5):
            t = i / 4
            off = 0.28 * math.sin(math.pi * 2 * t + k) * (0.3 + t)
            cpts.append((bx + (ex - bx) * t + nx * off, by + (ey - by) * t + ny * off))
        c = S(*cpts, n=6)
        snakes.append(tube(c, taper(0.28, 0.2), cap=False))
        ang = math.atan2(c[-1][1] - c[-4][1], c[-1][0] - c[-4][0])
        ux, uy = math.cos(ang), math.sin(ang)
        px, py = -uy, ux
        hx, hy = c[-1]
        snakes.append(S((hx + px * 0.1, hy + py * 0.1), (hx + px * 0.2 + ux * 0.2, hy + py * 0.2 + uy * 0.2), (hx + ux * 0.55, hy + uy * 0.55, 1),
                        (hx - px * 0.2 + ux * 0.2, hy - py * 0.2 + uy * 0.2), (hx - px * 0.1, hy - py * 0.1)))
        tx, ty = hx + ux * 0.55, hy + uy * 0.55
        snakes.append(poly((tx, ty), (tx + ux * 0.2, ty + uy * 0.2), (tx + ux * 0.32 + px * 0.08, ty + uy * 0.32 + py * 0.08), closed=False))
        hints.append(eye(hx + ux * 0.22 + px * 0.08, hy + uy * 0.22 + py * 0.08, 0.04))
    return make("Medusa with Serpent Hair", [face] + eyes_ + brows + nose + lips + neck + snakes,
                [eye(-0.4, 0.25, 0.08), eye(0.4, 0.25, 0.08)] + hints)


@design("dragons_harpy", T)
def harpy(rng):
    head = C((0.0, 2.9), (-0.4, 2.75), (-0.5, 2.3), (-0.35, 1.9), (0.0, 1.75), (0.35, 1.9), (0.5, 2.3), (0.4, 2.75))
    hair = [S((-0.4, 2.75), (-0.75, 2.3), (-0.7, 1.7), (-0.95, 1.2)), S((0.4, 2.75), (0.75, 2.3), (0.7, 1.7), (0.95, 1.2)),
            S((-0.35, 2.85), (0.0, 2.6), (0.35, 2.85))]
    torso = S((-0.2, 1.75), (-0.5, 1.4), (-0.55, 0.6), (-0.45, -0.3), (0.0, -0.6), (0.45, -0.3), (0.55, 0.6), (0.5, 1.4), (0.2, 1.75))
    feathers_body = [S((-0.45, 0.0), (-0.2, -0.25), (0.0, 0.0), (0.2, -0.25), (0.45, 0.0)), S((-0.35, -0.35), (0.0, -0.15), (0.35, -0.35))]
    wl = feather_wing(0.45, 1.2, 1.0, 0.0)
    wr = [mirror_x(p) for p in feather_wing(0.45, 1.2, 1.0, 0.0)]
    legs = [S((-0.25, -0.55), (-0.35, -1.2), (-0.3, -1.8)), S((0.25, -0.55), (0.35, -1.2), (0.3, -1.8))]
    talons = [poly((-0.65, -2.0), (-0.3, -1.8), (-0.4, -2.1), closed=False), poly((-0.3, -1.8), (-0.05, -2.05), closed=False),
              poly((0.65, -2.0), (0.3, -1.8), (0.4, -2.1), closed=False), poly((0.3, -1.8), (0.05, -2.05), closed=False)]
    tail = [S((-0.3, -0.55), (-0.6, -1.4), (-0.4, -1.5)), S((0.3, -0.55), (0.6, -1.4), (0.4, -1.5))]
    branch = [S((-2.8, -2.05), (0.0, -2.0), (2.8, -2.1)), S((-2.8, -2.35), (0.0, -2.3), (2.8, -2.4)), lens((2.2, -2.0), (2.8, -1.5), 0.4, 10)]
    return make("Harpy Perched on a Branch", [head, torso] + hair + feathers_body + wl + wr + legs + talons + tail + branch,
                [eye(-0.18, 2.35, 0.06), eye(0.18, 2.35, 0.06)])


@design("dragons_thunderbird", T)
def thunderbird(rng):
    body = C((0.0, 2.2), (-0.35, 2.05), (-0.9, 2.0, 1), (-0.4, 1.8), (-0.35, 1.2), (-0.55, 0.3), (-0.4, -0.6), (0.0, -0.9), (0.4, -0.6),
             (0.55, 0.3), (0.35, 1.2), (0.38, 1.85))
    half_wing = S((0.4, 1.2), (1.2, 1.9), (2.0, 2.5), (3.0, 2.8, 1), (2.6, 2.2), (3.2, 1.9, 1), (2.6, 1.55), (3.1, 1.15, 1), (2.3, 1.0),
                  (2.6, 0.5, 1), (1.7, 0.55), (1.8, 0.0, 1), (1.0, 0.3), (0.5, 0.2))
    tail = S((-0.35, -0.75), (-0.9, -1.8), (-0.45, -1.6), (-0.3, -2.1), (0.0, -1.7), (0.3, -2.1), (0.45, -1.6), (0.9, -1.8), (0.35, -0.75))
    pattern = [poly((-0.2, 1.0), (0.0, 0.6), (0.2, 1.0)), poly((-0.25, 0.2), (0.0, -0.2), (0.25, 0.2)), S((1.0, 1.4), (1.8, 1.8), (2.4, 2.1)),
               S((-1.0, 1.4), (-1.8, 1.8), (-2.4, 2.1))]
    bolts = [poly((-2.6, 0.2), (-2.2, -0.6), (-2.5, -0.6), (-2.0, -1.6), closed=False), poly((2.6, 0.2), (2.2, -0.6), (2.5, -0.6), (2.0, -1.6), closed=False),
             poly((-1.6, -0.6), (-1.3, -1.2), (-1.55, -1.2), (-1.2, -2.0), closed=False), poly((1.6, -0.6), (1.3, -1.2), (1.55, -1.2), (1.2, -2.0), closed=False)]
    clouds = [S((-3.2, 2.9), (-2.6, 3.3), (-2.0, 2.9), (-1.4, 3.3)), S((1.4, 3.3), (2.0, 2.9), (2.6, 3.3), (3.2, 2.9))]
    return make("Thunderbird with Lightning", [body, half_wing, mirror_x(half_wing), tail] + pattern + bolts + clouds, [eye(-0.12, 1.9, 0.06)])


# ------------------------------------------------------------ dragon scenes and close-ups

def flying_dragon_side(wing_rot=0.3):
    """Dragon in flight seen from the side, facing left, legs tucked."""
    body = S((-1.25, 0.85), (-1.5, 0.7), (-2.0, 0.55), (-2.35, 0.45, 1), (-2.1, 0.3), (-1.7, 0.28, 1), (-2.15, 0.08, 1), (-1.75, -0.05),
             (-1.35, 0.0), (-1.0, -0.15), (-0.5, -0.45), (0.3, -0.55), (0.9, -0.4))
    tail_c = S((0.9, -0.15), (1.7, -0.3), (2.4, 0.1), (2.9, 0.6), (3.4, 0.6), n=6)
    tb, ta = sides(tail_c, taper(0.6, 0.07))
    back = S((0.8, 0.25), (0.0, 0.3), (-0.6, 0.45), (-0.95, 0.75), (-1.25, 0.85))
    outline = chain(body, tb, ta, back)
    tip = [poly((3.35, 0.58), (3.55, 0.85), (3.85, 0.6), (3.55, 0.35), (3.38, 0.5), closed=False)]
    horns = [lens((-1.3, 0.8), (-0.75, 1.25), 0.18, 10), lens((-1.15, 0.75), (-0.6, 0.95), 0.16, 8)]
    legs = [S((-0.4, -0.45), (-0.55, -0.85), (-0.25, -1.05)), poly((-0.3, -1.0), (-0.45, -1.25), (-0.2, -1.1), (-0.15, -1.3), (-0.05, -1.05), closed=False),
            S((0.6, -0.5), (0.9, -0.95), (1.3, -1.0)), poly((1.2, -0.92), (1.5, -1.15), (1.35, -0.95), (1.55, -0.9), (1.3, -0.85), closed=False)]
    w_up = bat_wing(-0.4, 0.4, 0.95, wing_rot)
    w_far = [transform(p, dx=-0.7, dy=0.4, s=0.75, rot=wing_rot + 0.3) for p in bat_wing(0, 0)[:1]] if wing_rot > 0 else []
    sp = spikes(ta, 7, 0.18, t0=0.1, t1=0.6)
    belly = [S((-1.3, 0.0), (-0.6, -0.3), (0.3, -0.38))]
    teeth = [zigzag(-2.05, -1.8, 0.27, 0.04, 3)]
    return [outline] + tip + horns + legs + w_up + w_far + sp + belly + teeth, (-1.75, 0.55)


@design("dragons_over_mountains", T)
def over_mountains(rng):
    d, e = flying_dragon_side()
    d = tf(d, dy=1.2, s=0.85)
    e = (e[0] * 0.85, e[1] * 0.85 + 1.2)
    mountains = [poly((-3.4, -2.8), (-2.4, -0.9), (-1.9, -1.5), (-0.9, 0.0), (0.2, -1.6), (1.1, -0.7), (2.0, -1.8), (2.8, -1.0), (3.6, -2.8), closed=False),
                 poly((-1.3, -0.55), (-0.9, -0.3), (-0.6, -0.55), closed=False), poly((0.85, -0.95), (1.1, -0.75), (1.3, -0.95), closed=False)]
    pines = [poly((x - 0.25, -2.8), (x, -2.1), (x + 0.25, -2.8), closed=False) for x in (-2.6, -2.1, 1.6, 2.2, 2.8)]
    sun = [circle(2.6, 2.6, 0.5, 30)]
    birds = [S((-2.8, 2.6), (-2.6, 2.75), (-2.4, 2.6), (-2.2, 2.75), (-2.0, 2.6))]
    return make("Dragon Flying over the Mountains", d + mountains + pines + sun + birds, [eye(*e, 0.06)])


@design("dragons_rider", T)
def rider(rng):
    d, e = flying_dragon_side(-0.12)
    x = -0.75
    saddle = [S((x - 0.4, 0.55), (x - 0.25, 0.8), (x + 0.2, 0.8), (x + 0.35, 0.4))]
    rider_ = [circle(x, 1.75, 0.25, 20), poly((x - 0.15, 1.5), (x - 0.25, 0.8), (x + 0.25, 0.8), (x + 0.15, 1.5), closed=False),
              S((x - 0.12, 1.35), (x - 0.5, 1.1), (x - 0.75, 1.0)), S((x, 0.8), (x - 0.15, 0.35), (x + 0.05, 0.2)),
              S((x + 0.1, 1.45), (x + 0.5, 1.75), (x + 0.75, 2.4)), [(x + 0.75, 2.4), (x + 0.75, 2.9)], poly((x + 0.75, 2.9), (x + 1.25, 2.75), (x + 0.75, 2.6), closed=False)]
    reins = [S((x - 0.75, 1.0), (-1.4, 0.75), (-1.7, 0.42))]
    hair = [S((x - 0.2, 1.95), (x + 0.15, 2.05), (x + 0.4, 1.8))]
    clouds = [S((-3.0, -1.6), (-2.5, -1.2), (-2.0, -1.6), (-1.5, -1.2), (-1.0, -1.6)), S((1.2, -2.0), (1.7, -1.6), (2.2, -2.0), (2.7, -1.6))]
    return make("Dragon Rider in the Sky", d + saddle + rider_ + reins + hair + clouds, [eye(*e, 0.06)])


@design("dragons_tower", T)
def tower(rng):
    tw = [poly((0.6, -3.0), (0.75, 1.0), (2.45, 1.0), (2.6, -3.0), closed=False), rect(0.5, 1.0, 2.7, 1.4),
          poly((0.5, 1.4), (0.5, 1.75), (0.85, 1.75), (0.85, 1.55), (1.25, 1.55), (1.25, 1.75), (1.65, 1.75), (1.65, 1.55), (2.0, 1.55),
               (2.0, 1.75), (2.35, 1.75), (2.35, 1.55), (2.7, 1.55), (2.7, 1.4), closed=False),
          chain([(1.35, -0.2)], arc(1.6, 0.15, 0.25, math.pi, 0, 10), [(1.85, -0.2)], [(1.35, -0.2)])]
    bricks = [[(0.65, y), (2.55, y)] for y in (-2.2, -1.2)] + [[(1.3, -2.2), (1.3, -1.2)], [(1.9, -1.2), (1.9, -0.6)], [(1.0, -3.0), (1.0, -2.2)],
                                                          [(2.1, -3.0), (2.1, -2.2)]]
    neck = S((1.5, 1.75), (0.8, 2.6), (0.1, 3.0), (-0.6, 2.9))
    neck2 = S((2.1, 1.75), (1.5, 2.9), (0.6, 3.5), (-0.3, 3.5), (-0.95, 3.35))
    head = S((-0.6, 2.9), (-1.2, 2.85), (-1.7, 2.95, 1), (-1.5, 3.15), (-1.2, 3.25), (-0.95, 3.35))
    horns = [lens((-0.55, 3.45), (0.1, 4.0), 0.18, 10)]
    claws_ = [S((0.5, 1.4), (0.2, 1.1), (0.25, 0.8)), S((0.25, 0.8), (0.45, 1.0)), S((0.25, 0.8), (0.1, 0.95))]
    w = bat_wing(2.3, 1.9, 0.75, -0.2)
    tail = S((2.65, -1.0), (3.1, -0.5), (3.0, 0.2), (2.75, 0.5))
    sp = spikes(neck2, 5, 0.18, t0=0.1, t1=0.7)
    ground = [S((-3.0, -3.0), (3.4, -3.0))]
    smoke = [spiral(-2.3, 3.3, 0.05, 0.35, 1.2), spiral(-2.9, 2.6, 0.05, 0.28, 1.2)]
    return make("Dragon Guarding a Castle Tower", tw + bricks + [neck, neck2, head, tail] + horns + claws_ + w + sp + ground + smoke,
                [eye(-1.05, 3.05, 0.06)])


@design("dragons_eye_closeup", T)
def eye_closeup(rng):
    lid_top = S((-3.0, 0.0), (-1.6, 1.5), (0.0, 1.9), (1.6, 1.5), (3.0, 0.0))
    lid_bot = S((-3.0, 0.0), (-1.6, -1.3), (0.0, -1.6), (1.6, -1.3), (3.0, 0.0))
    iris = [circle(0.0, 0.1, 1.35, 90)]
    pupil = [lens((0.0, -1.15), (0.0, 1.35), 0.15, 20)]
    rays = [[(1.4 * math.cos(a) * 0.55, 0.1 + 1.35 * math.sin(a) * 0.55), (1.3 * math.cos(a), 0.1 + 1.3 * math.sin(a))]
            for a in [k * TAU / 16 for k in range(16)] if abs(math.cos(a)) > 0.25]
    brow = [S((-3.2, 0.6), (-1.6, 2.4), (0.0, 2.85), (1.6, 2.5), (3.2, 1.0))]
    scales = [arc(x, y, 0.32, math.pi * 1.1, math.pi * 1.9, 8) for x, y in
              [(-2.4, 2.4), (-1.6, 2.95), (-0.6, 3.2), (0.6, 3.25), (1.6, 3.0), (2.5, 2.5), (-2.0, -1.9), (-0.9, -2.3), (0.4, -2.4), (1.6, -2.1),
               (-2.6, -1.2), (2.6, -1.2)]]
    spikes_ = [poly((-3.2, 0.6), (-3.8, 1.3), (-3.15, 1.1), closed=False), poly((3.2, 1.0), (3.9, 1.6), (3.3, 1.5), closed=False)]
    shine = [circle(-0.6, 0.65, 0.22, 16)]
    return make("Dragon Eye Close-Up", [lid_top, lid_bot] + iris + pupil + rays + brow + scales + spikes_ + shine)


# dropped: weaker picture
def claw_orb(rng):
    orb = [circle(0.0, 1.0, 1.6, 100)]
    swirl = [spiral(0.0, 1.0, 0.1, 1.1, 1.6), star(-0.75, 1.7, 0.25), sparkle_(0.8, 0.3, 0.25)]
    fingers = []
    for a0, a1 in [(252, 178), (288, 362)]:
        c = [(1.98 * math.cos(math.radians(a0 + (a1 - a0) * i / 30)), 1.0 + 1.98 * math.sin(math.radians(a0 + (a1 - a0) * i / 30))) for i in range(31)]
        fingers.append(tube(c, taper(0.62, 0.42), cap=False))
        ex, ey = c[-1]
        d = 1 if a1 > a0 else -1
        ang = math.radians(a1 + 90 * d)
        ux, uy = math.cos(ang), math.sin(ang)
        px, py = -uy, ux
        fingers.append(S((ex + px * 0.21, ey + py * 0.21), (ex + ux * 0.45, ey + uy * 0.45), (ex + ux * 0.75 - px * 0.35, ey + uy * 0.75 - py * 0.35, 1),
                         (ex + ux * 0.3 - px * 0.15, ey + uy * 0.3 - py * 0.15), (ex - px * 0.21, ey - py * 0.21)))
    palm = [S((-0.95, -0.85), (-1.1, -1.6), (-0.9, -2.9)), S((0.95, -0.85), (1.1, -1.6), (0.9, -2.9)), S((-0.95, -0.85), (0.0, -0.75), (0.95, -0.85))]
    front = [tube(S((-0.35, -1.2), (-0.45, -0.75), (-0.4, -0.45), n=6), 0.45, cap=False), tube(S((0.35, -1.2), (0.45, -0.75), (0.4, -0.45), n=6), 0.45, cap=False)]
    tips = [S((-0.62, -0.45), (-0.5, -0.1), (-0.35, 0.05, 1), (-0.3, -0.25), (-0.17, -0.45)), S((0.62, -0.45), (0.5, -0.1), (0.35, 0.05, 1), (0.3, -0.25), (0.17, -0.45))]
    scales = [arc(x, y, 0.22, math.pi * 1.1, math.pi * 1.9, 8) for x, y in [(-0.45, -1.7), (0.35, -1.75), (0.0, -2.3), (-0.5, -2.5), (0.5, -2.45)]]
    return make("Dragon Claw Holding a Magic Orb", orb + swirl + fingers + palm + front + tips + scales)


def sparkle_(cx, cy, r):
    k = 0.28
    return poly((cx, cy + r), (cx + r * k, cy + r * k), (cx + r, cy), (cx + r * k, cy - r * k), (cx, cy - r),
                (cx - r * k, cy - r * k), (cx - r, cy), (cx - r * k, cy + r * k))


@design("dragons_ouroboros", T)
def ouroboros(rng):
    R = 2.0
    pts = [(R * math.cos(a), R * math.sin(a)) for a in [math.radians(70 - 330 * i / 120) for i in range(121)]]
    c = pts
    w = lambda t: 0.7 - 0.55 * t
    body = band(c, w)
    _, hparts, ep = neck_head((0.9, 1.6), (0.8, 1.75), c[0], 0.7, 0.7, True, 160)
    a = math.radians(160)
    k = 1.35

    def H(px, py):
        return (c[0][0] + px * math.cos(a) - py * math.sin(a), c[0][1] + px * math.sin(a) + py * math.cos(a))
    hd = [(0.0, -0.32), (0.45, -0.3), (0.95, -0.42, 1), (0.85, -0.22), (0.45, -0.06, 1), (1.2, 0.0, 1), (1.18, 0.12), (0.8, 0.2),
          (0.5, 0.3), (0.3, 0.36), (0.0, 0.32)]
    head = S(*[H(p[0] * k, p[1] * k) + tuple(p[2:]) for p in hd])
    sp = spikes(tube(c, w, cap=False)[:len(c)], 14, 0.25, t0=0.08, t1=0.9)
    inner = [circle(0.0, 0.0, 0.6, 40), star(0.0, 0.0, 0.45, 6, 0.5)]
    return make("Ouroboros Dragon Biting Its Tail", [body, head] + hparts + sp + inner, [eye(*ep, 0.07)])


# ------------------------------------------------------------ myths from around the world

@design("dragons_fenrir", T)
def fenrir(rng):
    body = S((-1.0, 0.6), (-1.3, 1.3), (-1.55, 1.7), (-1.55, 2.3, 1), (-1.85, 1.85), (-2.3, 1.75), (-2.9, 1.5), (-3.05, 1.3, 1), (-2.85, 1.15),
             (-2.4, 1.05), (-2.85, 0.85, 1), (-2.4, 0.65), (-1.95, 0.6), (-1.75, 0.2), (-1.85, -0.4), (-1.75, -1.6), (-2.05, -1.85),
             (-2.1, -2.05, 1), (-1.45, -2.05, 1), (-1.42, -1.6), (-1.3, -0.7), (-0.4, -0.8), (0.6, -0.75), (0.85, -1.2), (0.7, -1.7),
             (0.55, -2.05, 1), (1.2, -2.05, 1), (1.2, -1.7), (1.4, -1.1), (1.65, -0.5), (1.7, 0.1), (1.4, 0.45), (0.2, 0.5), (-0.5, 0.65),
             (-1.0, 1.15))
    body = jag(body, 0.12, step=0.28)
    ear2 = [poly((-1.25, 1.35), (-1.1, 2.1), (-0.9, 1.3), closed=False)]
    teeth = [zigzag(-2.8, -2.35, 1.0, 0.06, 3)]
    nose = [ellipse(-2.95, 1.38, 0.1, 0.07, 10)]
    tail = jag(S((1.65, -0.1), (2.3, 0.0), (2.8, 0.5), (2.9, 1.2), (2.6, 1.6), (2.4, 1.0), (2.1, 0.5), (1.6, 0.3)), 0.1, step=0.28)
    links = []
    for k in range(7):
        t = (k + 0.5) / 7
        x, y = -1.5 + (-2.9 + 1.5) * t, 0.2 + (-2.0 - 0.2) * t
        ang = math.atan2(-2.2, -1.4)
        links.append(ellipse(x, y, 0.2, 0.11 if k % 2 == 0 else 0.05, 14, rot=ang))
    links.append(S((-3.1, -2.1), (-2.9, -1.85), (-2.7, -2.1)))
    collar = [S((-1.95, 0.55), (-1.55, 0.3), (-1.1, 0.5)), S((-1.95, 0.35), (-1.55, 0.1), (-1.1, 0.3))]
    rock = [S((-3.3, -2.1), (0.0, -2.08), (3.0, -2.1)), S((1.5, -2.08), (1.8, -1.3), (2.4, -1.1), (2.9, -1.6), (3.1, -2.1))]
    moon = [circle(2.4, 2.6, 0.5, 30)]
    return make("Fenrir the Giant Wolf in Chains", [body, tail] + ear2 + teeth + nose + links + collar + rock + moon,
                [eye(-2.15, 1.45, 0.07)])


@design("dragons_satyr", T)
def satyr(rng):
    head = C((0.0, 2.75), (-0.42, 2.6), (-0.5, 2.15), (-0.35, 1.75), (0.0, 1.6), (0.35, 1.75), (0.5, 2.15), (0.42, 2.6))
    curls = [S((-0.42, 2.6), (-0.6, 2.9), (-0.25, 3.0), (0.0, 2.85), (0.25, 3.0), (0.6, 2.9), (0.42, 2.6))]
    horns = [S((-0.25, 2.85), (-0.55, 3.35), (-0.9, 3.35), (-0.75, 3.1)), S((0.25, 2.85), (0.55, 3.35), (0.9, 3.35), (0.75, 3.1))]
    ears = [lens((-0.48, 2.25), (-0.95, 2.45), 0.3, 8), lens((0.48, 2.25), (0.95, 2.45), 0.3, 8)]
    beard = [S((-0.35, 1.8), (-0.2, 1.4), (0.0, 1.3), (0.2, 1.4), (0.35, 1.8))]
    smile = [S((-0.15, 1.85), (0.0, 1.78), (0.15, 1.85))]
    torso = S((-0.2, 1.55), (-0.85, 1.3), (-0.95, 0.4), (-0.75, -0.3), (0.75, -0.3), (0.95, 0.4), (0.85, 1.3), (0.2, 1.55))
    legs = jag(S((-0.8, -0.3), (-1.05, -0.9), (-0.95, -1.4), (-0.6, -1.7), (-0.8, -2.4), (-1.0, -2.65, 1), (-0.55, -2.75, 1), (-0.35, -2.4),
                 (-0.3, -1.8), (-0.4, -1.2), (0.0, -0.9), (0.4, -1.2), (0.3, -1.8), (0.35, -2.4), (0.55, -2.75, 1), (1.0, -2.65, 1),
                 (0.8, -2.4), (0.6, -1.7), (0.95, -1.4), (1.05, -0.9), (0.8, -0.3)), 0.08, step=0.26)
    hooves = [[(-0.98, -2.48), (-0.45, -2.55)], [(0.45, -2.55), (0.98, -2.48)]]
    arms = [S((-0.8, 1.2), (-1.1, 0.6), (-0.7, 0.85), (-0.35, 1.1)), S((0.8, 1.2), (1.1, 0.6), (0.7, 0.85), (0.4, 1.1))]
    pipes = [poly((-0.5, 1.2), (0.5, 1.2), (0.5, 0.95), (0.25, 0.4), (-0.5, 0.4), closed=True)] + [[(x, 1.2), (x, 0.4 + 0.3 * (x + 0.5))] for x in (-0.25, 0.0, 0.25)]
    notes = [S((1.4, 2.0), (1.4, 2.6), (1.7, 2.5)), circle(1.3, 1.95, 0.1, 10), S((-1.6, 2.2), (-1.6, 2.8), (-1.3, 2.7)), circle(-1.7, 2.15, 0.1, 10)]
    tail = [S((0.6, -0.7), (1.3, -0.4), (1.5, 0.0))]
    return make("Satyr Playing the Pan Pipes", [head, torso, legs] + curls + horns + ears + beard + smile + hooves + arms + pipes + notes + tail,
                [eye(-0.18, 2.2, 0.06), eye(0.18, 2.2, 0.06)])


@design("dragons_kappa", T)
def kappa(rng):
    head = C((0.0, 2.3), (-0.95, 2.1), (-1.15, 1.3), (-0.9, 0.6), (0.0, 0.4), (0.9, 0.6), (1.15, 1.3), (0.95, 2.1))
    dish = [ellipse(0.0, 2.3, 0.6, 0.18, 30), wave(-0.4, 0.4, 2.3, 0.03, 2, 20)]
    hair = [zigzag(-1.0, -0.55, 2.05, 0.12, 2), zigzag(0.55, 1.0, 2.05, 0.12, 2)]
    beak = [S((-0.55, 1.0), (0.0, 0.7), (0.55, 1.0), (0.0, 1.15), (-0.55, 1.0))]
    body = S((-0.7, 0.55), (-1.0, -0.3), (-0.85, -1.2), (0.0, -1.5), (0.85, -1.2), (1.0, -0.3), (0.7, 0.55))
    shell = [S((1.0, 0.2), (1.5, -0.3), (1.5, -1.0), (1.1, -1.4))]
    belly = [S((-0.5, 0.2), (-0.6, -0.5), (-0.4, -1.1), (0.4, -1.1), (0.6, -0.5), (0.5, 0.2)), [(-0.55, -0.3), (0.55, -0.3)], [(-0.5, -0.75), (0.5, -0.75)]]
    arms = [S((-0.9, 0.2), (-1.6, -0.2), (-1.8, -0.7)), S((0.9, 0.2), (1.7, 0.4), (2.0, 0.9))]
    hands = [poly((-1.95, -0.65), (-2.05, -0.95), (-1.8, -0.85), (-1.75, -1.1), (-1.6, -0.75), closed=False),
             poly((1.9, 0.95), (2.0, 1.25), (2.1, 0.9), (2.35, 1.0), (2.1, 0.75), closed=False)]
    legs = [S((-0.5, -1.4), (-0.6, -2.1), (-0.95, -2.35)), S((0.5, -1.4), (0.6, -2.1), (0.95, -2.35)),
            poly((-1.3, -2.35), (-0.4, -2.35), closed=False), poly((1.3, -2.35), (0.4, -2.35), closed=False)]
    cucumber = [rrect(1.85, 1.1, 2.25, 2.4, 0.2), circle(2.0, 1.6, 0.05, 6), circle(2.1, 2.0, 0.05, 6)]
    pond = [ellipse(0.0, -2.5, 3.0, 0.45, 70), lens((-2.4, -2.5), (-1.8, -2.4), 0.4, 8)]
    reeds = [S((-2.8, -2.3), (-2.9, -1.0)), ellipse(-2.9, -0.8, 0.08, 0.25, 12), S((2.8, -2.3), (2.75, -1.2))]
    return make("Kappa the River Imp", [head, body] + dish + hair + beak + shell + belly + arms + hands + legs + cucumber + pond + reeds,
                [eye(-0.45, 1.45, 0.1), eye(0.45, 1.45, 0.1)])


@design("dragons_dragon_turtle", T)
def dragon_turtle(rng):
    shell = S((-2.0, -0.3), (-1.8, 0.8), (-0.8, 1.55), (0.6, 1.6), (1.8, 1.0), (2.3, -0.3))
    rim = [S((-2.2, -0.3), (0.0, -0.55), (2.5, -0.3)), S((-2.2, -0.3), (-2.0, -0.6), (0.0, -0.85), (2.3, -0.6), (2.5, -0.3))]
    plates = [poly((-0.6, 0.2), (-0.35, 0.95), (0.4, 0.95), (0.65, 0.2), (0.4, -0.45), (-0.35, -0.45)),
              [(-0.35, 0.95), (-0.8, 1.5)], [(0.4, 0.95), (0.7, 1.55)], [(0.65, 0.2), (1.9, 0.6)], [(-0.6, 0.2), (-1.85, 0.5)],
              [(0.4, -0.45), (1.3, -0.62)], [(-0.35, -0.45), (-1.1, -0.65)]]
    spikes_ = spikes(S((-1.8, 0.8), (-0.8, 1.55), (0.6, 1.6), (1.8, 1.0), n=6), 6, 0.3)
    neck = S((-2.0, -0.45), (-2.5, 0.2), (-2.65, 0.9))
    neck2 = S((-2.0, -0.75), (-2.85, -0.3), (-3.15, 0.45))
    head = S((-2.65, 0.9), (-2.75, 1.25), (-3.2, 1.35), (-3.7, 1.15, 1), (-3.45, 0.95), (-3.15, 0.9), (-3.55, 0.65, 1), (-3.15, 0.45))
    whisk = [S((-3.65, 1.05), (-4.0, 1.35), (-4.2, 1.2)), S((-3.5, 0.62), (-3.9, 0.3), (-4.1, 0.45))]
    horns = [lens((-2.9, 1.3), (-2.4, 1.85), 0.18, 10)]
    legs = [S((-1.6, -0.85), (-1.8, -1.6), (-2.2, -1.75), (-1.2, -1.75), (-1.2, -0.85)), S((1.2, -0.85), (1.3, -1.6), (0.9, -1.75), (1.9, -1.75), (1.8, -0.85))]
    tail = [S((2.4, -0.45), (3.0, -0.3), (3.3, 0.1), (3.1, 0.4)), S((2.4, -0.65), (3.1, -0.6), (3.5, -0.1), (3.1, 0.4))]
    waves = [wave(-4.2, 3.8, -2.3, 0.12, 7)]
    return make("Dragon Turtle", [shell, neck, neck2, head] + rim + plates + spikes_ + whisk + horns + legs + tail + waves,
                [eye(-3.15, 1.12, 0.06)])


@design("dragons_baby_sitting", T)
def baby_sitting(rng):
    head = C((0.0, 2.6), (-0.85, 2.45), (-1.2, 1.9), (-1.05, 1.3), (-0.6, 1.0), (0.6, 1.0), (1.05, 1.3), (1.2, 1.9), (0.85, 2.45))
    snout = [S((-0.3, 1.5), (-0.22, 1.4), (-0.3, 1.32)), S((0.3, 1.5), (0.22, 1.4), (0.3, 1.32)), S((-0.35, 1.15), (0.0, 1.08), (0.35, 1.15))]
    horns = [lens((-0.5, 2.5), (-0.75, 3.1), 0.3, 10), lens((0.5, 2.5), (0.75, 3.1), 0.3, 10)]
    ears = [poly((-1.12, 2.15), (-1.65, 2.35), (-1.2, 1.9), (-1.6, 1.85), (-1.18, 1.65), closed=False),
            poly((1.12, 2.15), (1.65, 2.35), (1.2, 1.9), (1.6, 1.85), (1.18, 1.65), closed=False)]
    body = S((-0.7, 1.05), (-1.2, 0.3), (-1.35, -0.9), (-1.0, -1.7), (1.0, -1.7), (1.35, -0.9), (1.2, 0.3), (0.7, 1.05))
    belly = [ellipse(0.0, -0.55, 0.75, 0.95, 40)] + [S((-0.65 + 0.06 * abs(k), y), (0.65 - 0.06 * abs(k), y)) for k, y in zip(range(-1, 2), (-0.1, -0.55, -1.0))]
    arms = [S((-1.05, 0.4), (-0.75, -0.1), (-0.4, 0.0)), S((1.05, 0.4), (0.75, -0.1), (0.4, 0.0))]
    feet = [ellipse(-0.75, -1.85, 0.5, 0.28, 24), ellipse(0.75, -1.85, 0.5, 0.28, 24)]
    toes = [[(-1.0 + 0.25 * k, -1.65), (-1.0 + 0.25 * k, -1.75)] for k in range(3)] + [[(0.5 + 0.25 * k, -1.65), (0.5 + 0.25 * k, -1.75)] for k in range(3)]
    wings = [S((-1.15, 0.6), (-1.9, 1.3), (-2.4, 1.1), (-2.2, 0.75), (-2.5, 0.45), (-2.0, 0.3), (-1.25, 0.15)),
             S((1.15, 0.6), (1.9, 1.3), (2.4, 1.1), (2.2, 0.75), (2.5, 0.45), (2.0, 0.3), (1.25, 0.15))]
    tail = [S((1.0, -1.6), (1.9, -1.9), (2.5, -1.5), (2.6, -1.0)), poly((2.45, -1.05), (2.6, -0.6), (2.85, -1.0), closed=False)]
    cheeks = [poly((-0.3, 2.62), (0.0, 2.95), (0.3, 2.62), closed=False)]
    return make("Cute Baby Dragon Sitting", [head, body] + snout + horns + ears + belly + arms + feet + toes + wings + tail + cheeks,
                [eye(-0.45, 1.95, 0.14), eye(0.45, 1.95, 0.14)])


@design("dragons_jackalope", T)
def jackalope(rng):
    body = C((-1.0, 0.9), (-1.6, 0.85), (-2.0, 0.55), (-2.1, 0.2), (-1.85, 0.0), (-1.5, -0.05), (-1.3, -0.4), (-1.35, -1.5), (-1.6, -1.75, 1),
             (-0.9, -1.75, 1), (-0.95, -1.2), (-0.6, -1.4), (0.6, -1.4), (0.3, -1.75, 1), (1.7, -1.75, 1), (1.6, -1.3), (1.75, -0.5),
             (1.5, 0.2), (0.6, 0.45), (-0.4, 0.4))
    ears = [lens((-1.0, 0.85), (-0.2, 2.2), 0.18, 16), lens((-1.2, 0.9), (-0.85, 2.3), 0.18, 16)]
    antlers = [S((-1.45, 0.95), (-1.6, 1.8), (-1.3, 2.6), (-1.0, 3.0)), S((-1.55, 1.6), (-2.0, 2.0), (-2.2, 2.5)),
               S((-1.4, 2.35), (-1.8, 2.8)), S((-1.25, 0.95), (-1.0, 1.6), (-0.4, 2.6) if False else (-0.5, 1.95)),
               S((-0.7, 1.75), (-0.5, 2.35))]
    antlers = [S((-1.45, 0.95), (-1.75, 1.7), (-1.6, 2.5), (-1.3, 3.0)), S((-1.7, 1.55), (-2.2, 1.95), (-2.4, 2.45)),
               S((-1.65, 2.3), (-2.0, 2.75)), S((-1.3, 0.95), (-1.15, 1.6), (-1.35, 2.2)), S((-1.2, 1.55), (-0.85, 1.95))]
    ears = [lens((-0.95, 0.85), (0.1, 1.75), 0.2, 16)]
    tail = [circle(1.85, -0.2, 0.3, 20)]
    leg = [S((0.5, -0.2), (1.1, 0.0), (1.4, -0.6), (1.2, -1.3))]
    nose = [S((-2.05, 0.3), (-1.95, 0.22))]
    whisk = [[(-1.95, 0.15), (-2.5, 0.25)], [(-1.95, 0.1), (-2.45, -0.05)]]
    grass = [zigzag(-3.0, 3.0, -1.85, 0.12, 18)]
    cactus = [S((2.4, -1.75), (2.4, 0.8), (2.7, 1.0), (3.0, 0.8), (3.0, -1.75)), S((3.0, 0.0), (3.4, 0.0), (3.4, 0.6)), S((2.4, -0.4), (2.1, -0.4), (2.1, 0.2))]
    return make("Jackalope with Antlers", [body] + ears + antlers + tail + leg + nose + whisk + grass + cactus, [eye(-1.55, 0.5, 0.07)])


@design("dragons_gargoyle", T)
def gargoyle(rng):
    head = C((0.0, 1.8), (-0.75, 1.6), (-0.95, 1.0), (-0.75, 0.4), (-0.3, 0.15), (0.3, 0.15), (0.75, 0.4), (0.95, 1.0), (0.75, 1.6))
    horns = [S((-0.6, 1.65), (-1.0, 2.3), (-0.8, 2.8)), S((-0.35, 1.75), (-0.65, 2.35), (-0.8, 2.8)),
             S((0.6, 1.65), (1.0, 2.3), (0.8, 2.8)), S((0.35, 1.75), (0.65, 2.35), (0.8, 2.8))]
    ears = [poly((-0.9, 1.2), (-1.5, 1.5), (-0.95, 0.85), closed=False), poly((0.9, 1.2), (1.5, 1.5), (0.95, 0.85), closed=False)]
    brow = [S((-0.6, 1.25), (-0.3, 1.1), (-0.1, 1.2)), S((0.1, 1.2), (0.3, 1.1), (0.6, 1.25))]
    mouth = [S((-0.45, 0.45), (0.0, 0.35), (0.45, 0.45)), poly((-0.3, 0.42), (-0.25, 0.65), (-0.18, 0.4), closed=False),
             poly((0.18, 0.4), (0.25, 0.65), (0.3, 0.42), closed=False)]
    nose = [S((-0.15, 0.95), (-0.25, 0.7), (0.25, 0.7), (0.15, 0.95))]
    body = S((-0.6, 0.25), (-1.3, 0.0), (-1.55, -0.8), (-1.35, -1.6), (-1.6, -1.95), (1.6, -1.95), (1.35, -1.6), (1.55, -0.8), (1.3, 0.0), (0.6, 0.25))
    knees = [S((-1.35, -1.6), (-0.9, -0.9), (-0.4, -1.1), (-0.3, -1.95)), S((1.35, -1.6), (0.9, -0.9), (0.4, -1.1), (0.3, -1.95))]
    arms = [S((-1.2, -0.1), (-0.9, -0.9)), S((1.2, -0.1), (0.9, -0.9))]
    claws_ = [poly((-1.0, -0.9), (-0.95, -1.15), (-0.8, -0.95), (-0.7, -1.15), (-0.65, -0.9), closed=False),
              poly((1.0, -0.9), (0.95, -1.15), (0.8, -0.95), (0.7, -1.15), (0.65, -0.9), closed=False)]
    wings = [S((-1.3, -0.1), (-2.0, 1.2), (-2.6, 2.0), (-3.0, 1.2, 1), (-2.6, 0.9), (-2.85, 0.2, 1), (-2.3, 0.0), (-2.5, -0.7, 1), (-1.55, -0.6))]
    wings.append(mirror_x(wings[0]))
    ledge = [rect(-2.6, -2.5, 2.6, -1.95), [(-2.6, -2.2), (2.6, -2.2)], [(-1.3, -2.5), (-1.3, -2.2)], [(0.6, -2.2), (0.6, -1.95)]]
    return make("Stone Gargoyle on a Ledge", [head, body] + horns + ears + brow + mouth + nose + knees + arms + claws_ + wings + ledge,
                [eye(-0.35, 1.0, 0.08), eye(0.35, 1.0, 0.08)])


# dropped: weaker picture
def sleipnir(rng):
    body = C((-2.0, 2.2), (-2.35, 2.02), (-2.75, 1.45), (-2.97, 1.12), (-2.92, 0.95), (-2.65, 0.86), (-2.2, 1.12), (-1.95, 1.42),
             (-1.75, 1.55), (-1.72, 0.9), (-1.85, 0.2), (-1.72, -0.3), (-1.55, -0.6), (-1.5, -1.1), (-1.5, -1.45), (-1.5, -2.05),
             (-1.6, -2.45, 1), (-1.25, -2.45, 1), (-1.25, -2.05), (-1.23, -1.45), (-1.2, -1.1), (-1.1, -0.82), (-0.5, -0.88), (0.4, -0.86),
             (0.95, -0.66), (1.2, -1.0), (1.25, -1.45), (1.3, -2.05), (1.22, -2.45, 1), (1.6, -2.45, 1), (1.58, -2.05), (1.6, -1.4),
             (1.75, -0.95), (1.86, -0.35), (1.86, 0.15), (1.6, 0.5), (1.2, 0.6), (0.2, 0.45), (-0.8, 0.65), (-1.2, 1.15), (-1.6, 1.85))
    legs = []
    for x0 in (-1.05, -0.72, -0.39, 0.15, 0.48, 0.81):
        legs.append(S((x0, -0.87), (x0 + 0.02, -1.45), (x0, -2.05), (x0 - 0.06, -2.42, 1), (x0 + 0.24, -2.42, 1),
                      (x0 + 0.24, -2.05), (x0 + 0.24, -1.45), (x0 + 0.27, -0.87)))
    mane = [poly((-1.85, 2.25), (-1.4, 2.1), (-1.55, 1.8), (-1.05, 1.6), (-1.25, 1.3), (-0.75, 1.1), (-0.95, 0.8), closed=False)]
    ear = [poly((-2.05, 2.15), (-1.85, 2.65), (-1.75, 2.1), closed=False)]
    tail = [S((1.7, 0.45), (2.3, 0.35), (2.5, -0.25), (2.3, -0.95), (2.6, -1.55)), S((1.84, 0.2), (2.05, -0.2), (1.95, -0.8), (2.15, -1.35))]
    runes = [poly((-0.5, 0.0), (-0.3, 0.3), (-0.1, 0.0), (-0.3, -0.3)), [(0.2, 0.25), (0.2, -0.3)], [(0.2, 0.25), (0.45, 0.0)], [(0.2, 0.0), (0.45, -0.25)]]
    ground = [S((-3.0, -2.47), (0.0, -2.45), (3.0, -2.48))]
    return make("Sleipnir the Eight-Legged Steed", [body] + legs + mane + ear + tail + runes + ground, [eye(-2.3, 1.72, 0.08)])


# dropped: weaker picture
def world_tree(rng):
    trunk = [S((-0.7, -2.0), (-0.5, -0.8), (-0.6, 0.3), (-1.4, 1.0), (-2.4, 1.3)), S((0.7, -2.0), (0.5, -0.8), (0.6, 0.3), (1.4, 1.0), (2.4, 1.2)),
             S((-0.6, 0.3), (-0.3, 1.0), (-0.7, 1.9)), S((0.6, 0.3), (0.3, 1.1), (0.6, 2.0)), S((-0.3, 1.0), (0.0, 1.6), (0.3, 1.1))]
    crown = [polar(lambda t: 2.2 + 0.18 * math.sin(9 * t) + 0.25 * math.sin(t) * 0.0, cx=0.0, cy=1.9, n=220, t0=math.radians(-15), t1=math.radians(195))]
    crown = [polar(lambda t: 2.3 + 0.18 * math.sin(9 * t), cx=0.0, cy=1.7, n=240, t0=math.radians(-10), t1=math.radians(190)),
             S((-2.27, 1.3), (-1.5, 0.95), (-0.9, 1.2)), S((2.27, 1.3), (1.5, 0.9), (0.9, 1.2))]
    roots = [S((-0.7, -2.0), (-1.5, -2.4), (-2.6, -2.5)), S((0.7, -2.0), (1.5, -2.4), (2.6, -2.5)), S((-0.3, -2.0), (-0.5, -2.6), (-1.0, -3.0)),
             S((0.3, -2.0), (0.5, -2.6), (1.0, -3.0)), S((0.0, -2.0), (0.0, -2.9))]
    eagle = [S((-0.4, 3.9), (0.0, 4.2), (0.4, 3.9)), S((-1.0, 4.15), (-0.5, 3.95)), S((1.0, 4.15), (0.5, 3.95))]
    serpent = [S((-2.6, -2.8), (-2.0, -2.95), (-1.4, -2.8), (-0.8, -3.15), (-0.2, -3.25)), S((0.2, -3.25), (0.8, -3.15), (1.4, -2.8), (2.0, -2.95), (2.6, -2.8))]
    leaves = [lens((x, y), (x + 0.3, y + 0.3), 0.4, 8) for x, y in [(-1.5, 2.5), (0.0, 3.0), (1.3, 2.4), (-0.6, 2.0), (0.8, 1.9)]]
    knot = [circle(0.0, -1.0, 0.25, 16)]
    squirrel = [ellipse(1.0, 0.0, 0.2, 0.3, 16), spiral(1.3, 0.25, 0.05, 0.28, 1.0)]
    return make("Yggdrasil the World Tree", trunk + crown + roots + eagle + serpent + leaves + knot + squirrel)


# dropped: weaker picture
def lamassu(rng):
    head = [(-1.1, 0.9), (-1.15, 1.5), (-1.35, 1.88), (-1.95, 1.88), (-2.0, 1.55), (-2.25, 1.32, 1), (-2.05, 1.25), (-2.12, 1.12),
            (-2.0, 1.02), (-2.15, 0.85), (-2.25, 0.4), (-2.0, 0.05, 1), (-1.75, 0.15)]
    b = beast(head, None, hind="hoof")
    crown = [poly((-2.0, 1.88), (-2.0, 2.45), (-1.3, 2.45), (-1.3, 1.88), closed=False), [(-2.0, 2.15), (-1.3, 2.15)]]
    beard = [zigzag(-2.1, -1.6, 0.75, 0.06, 3), zigzag(-2.1, -1.7, 0.4, 0.06, 3)]
    beard_lines = [S((-1.95, 1.0), (-1.75, 1.05), (-1.6, 0.95))]
    hair = [S((-1.3, 1.9), (-0.95, 1.5), (-1.05, 1.0)), S((-1.2, 1.6), (-0.85, 1.15))]
    w = feather_wing(-0.6, 0.45, 1.1, -0.15)
    tail = [S((1.55, 0.0), (2.0, -0.3), (2.1, -0.9)), lens((2.1, -0.9), (2.2, -1.5), 0.35, 10)]
    base = [rect(-3.0, -2.5, 3.0, -2.05)]
    return make("Lamassu: Winged Bull Guardian", b + crown + beard + beard_lines + hair + w + tail + base, [eye(-1.8, 1.52, 0.06)])


@design("dragons_front_face", T)
def front_face(rng):
    half = S((0.0, 2.1), (0.6, 2.0), (1.05, 1.6), (1.25, 1.0), (1.05, 0.2), (0.85, -0.6), (0.9, -1.4), (0.7, -2.05), (0.0, -2.25))
    face = chain(mirror_x(half)[::-1], half[1:])
    hp = [S((0.6, 1.95), (1.2, 2.6), (1.8, 3.1), (2.3, 3.2)), S((1.0, 1.65), (1.6, 2.3), (2.3, 3.2)),
          poly((1.25, 1.1), (2.2, 1.5), (1.55, 0.9), (2.4, 0.6), (1.45, 0.4), (2.2, -0.1), (1.2, 0.0), closed=False),
          lens((0.35, 0.95), (1.0, 0.85), 0.32, 14), S((0.25, 1.35), (0.65, 1.5), (1.05, 1.3)),
          S((0.25, -1.3), (0.4, -1.5), (0.3, -1.7)), poly((0.55, -1.95), (0.5, -2.35), (0.4, -1.98), closed=False)]
    mid = [S((0.0, 1.9), (0.0, 0.6)), [(-0.2, 1.7), (0.0, 1.85), (0.2, 1.7)], [(-0.2, 1.3), (0.0, 1.45), (0.2, 1.3)], [(-0.2, 0.9), (0.0, 1.05), (0.2, 0.9)],
           S((-0.6, -2.05), (0.0, -2.0), (0.6, -2.05))]
    whisk = [S((0.85, -1.2), (1.6, -1.4), (2.2, -1.1), (2.6, -1.5)), S((-0.85, -1.2), (-1.6, -1.4), (-2.2, -1.1), (-2.6, -1.5))]
    return make("Dragon Face Front View", [face] + hp + [mirror_x(p) for p in hp] + mid + whisk,
                [lens((0.62, 0.72), (0.66, 1.08), 0.35, 8), lens((-0.62, 0.72), (-0.66, 1.08), 0.35, 8)])
