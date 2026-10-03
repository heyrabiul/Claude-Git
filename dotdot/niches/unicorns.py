"""Unicorns & Fantasy niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "unicorns"


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


def horn(base, tip, w=0.32, twists=4):
    """Spiral unicorn horn from base centre to tip."""
    bx, by = base
    tx, ty = tip
    dx, dy = tx - bx, ty - by
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    out = [poly((bx + nx * w / 2, by + ny * w / 2), (tx, ty), (bx - nx * w / 2, by - ny * w / 2), closed=False)]

    def edge(t, side):
        hw = w / 2 * (1 - t) * side
        return (bx + dx * t + nx * hw, by + dy * t + ny * hw)
    for k in range(1, twists + 1):
        t = k / (twists + 1.3)
        out.append([edge(t - 0.07, 1), edge(t + 0.07, -1)])
    return out


def sparkle(cx, cy, r):
    """Four-point twinkle star."""
    k = 0.28
    return poly((cx, cy + r), (cx + r * k, cy + r * k), (cx + r, cy), (cx + r * k, cy - r * k), (cx, cy - r),
                (cx - r * k, cy - r * k), (cx - r, cy), (cx - r * k, cy + r * k))


def cloud(cx, cy, w, h=None):
    """Puffy cloud with a flat base."""
    h = h or w * 0.45
    x0, x1, yb = cx - w / 2, cx + w / 2, cy - h / 2
    r1, r2, r3 = min(h * 0.45, w * 0.22), min(h * 0.6, w * 0.3), min(h * 0.5, w * 0.24)
    c1 = (x0 + r1, yb + r1)
    c2 = (cx - w * 0.03, yb + h - r2)
    c3 = (x1 - r3, yb + r3)
    return chain(arc(c1[0], c1[1], r1, 1.5 * math.pi, math.pi / 3, 20), arc(c2[0], c2[1], r2, 0.85 * math.pi, 0.18 * math.pi, 26),
                 arc(c3[0], c3[1], r3, 0.6 * math.pi, -0.5 * math.pi, 20), [(c1[0], yb)])


def rainbow(cx, cy, r0, r1, bands=4, a0=0.0, a1=math.pi):
    return [arc(cx, cy, r0 + (r1 - r0) * k / (bands - 1), a0, a1, 70) for k in range(bands)]


def flip(strokes, axis=0.0):
    return [mirror_x(s, axis) for s in strokes]


def tf(strokes, dx=0.0, dy=0.0, s=1.0, rot=0.0):
    return [transform(p, dx=dx, dy=dy, s=s, rot=rot) for p in strokes]


# ------------------------------------------------------------ unicorn bodies

HEAD = [(0.0, 0.0), (-0.35, -0.18), (-0.75, -0.75), (-0.97, -1.08), (-0.92, -1.25), (-0.65, -1.34), (-0.2, -1.08), (0.05, -0.78),
        (0.25, -0.65)]
FORE = {"stand": [(-1.55, -0.6), (-1.5, -1.1), (-1.5, -1.45), (-1.5, -2.05), (-1.53, -2.2), (-1.64, -2.45, 1), (-1.25, -2.45, 1),
                  (-1.25, -2.2), (-1.24, -1.95), (-1.23, -1.45), (-1.2, -1.1), (-1.05, -0.75)],
        "lift": [(-1.6, -0.6), (-1.85, -0.95), (-2.0, -1.25), (-1.78, -1.62), (-1.86, -1.88, 1), (-1.52, -1.95, 1), (-1.5, -1.62),
                 (-1.66, -1.28), (-1.42, -1.0), (-1.05, -0.75)]}
HIND = {"stand": [(1.05, -0.95), (1.0, -1.35), (1.05, -1.6), (1.08, -2.05), (1.06, -2.2), (0.96, -2.45, 1), (1.34, -2.45, 1),
                  (1.34, -2.2), (1.36, -1.95), (1.5, -1.4), (1.62, -0.95)]}
FAR = {"stand": [S((-0.95, -0.85), (-0.88, -1.15), (-0.85, -1.5), (-0.86, -2.05), (-0.9, -2.2), (-1.0, -2.43, 1), (-0.64, -2.43, 1),
                   (-0.6, -2.2), (-0.6, -1.95), (-0.58, -1.45), (-0.6, -0.88)),
                 S((0.55, -0.86), (0.66, -1.2), (0.62, -1.5), (0.68, -2.05), (0.64, -2.2), (0.56, -2.43, 1), (0.9, -2.43, 1), (0.96, -2.2))]}


def unicorn_side(poll=(-2.0, 2.2), rot=0.0, fore="stand", throat_to=(-1.72, 0.9), crest=(-1.2, 1.15), hornlen=1.25, mid=None):
    """Side view unicorn facing left with head turned by `rot` about the
    poll.  Returns (strokes, eye_pos, anchors)."""
    head = transform(HEAD, dx=poll[0], dy=poll[1], rot=rot)
    hb = transform([(-0.3, -0.1)], dx=poll[0], dy=poll[1], rot=rot)[0]
    ht = transform([(-0.3 - 0.6 * hornlen / 1.25, -0.1 + 1.1 * hornlen / 1.25)], dx=poll[0], dy=poll[1], rot=rot)[0]
    ear = transform([(-0.05, -0.05), (0.15, 0.45), (0.25, -0.1)], dx=poll[0], dy=poll[1], rot=rot)
    eyep = transform([(-0.3, -0.48)], dx=poll[0], dy=poll[1], rot=rot)[0]
    mid_crest = mid or ((poll[0] + crest[0]) / 2 + 0.15, (poll[1] + crest[1]) / 2 + 0.1)
    chest = [(-1.85, 0.2)] if throat_to[1] > 0.3 else [(throat_to[0] - 0.05, (throat_to[1] - 0.3) / 2)]
    pts = head + [throat_to] + chest + [(-1.72, -0.3)] + FORE[fore] + [(-0.5, -0.88), (0.4, -0.86), (0.95, -0.66)] + HIND["stand"] + \
        [(1.86, -0.35), (1.86, 0.15), (1.6, 0.5), (1.2, 0.6), (0.2, 0.45), (-0.8, 0.65), crest, mid_crest]
    body = C(*pts)
    out = [body, poly(*ear, closed=False)] + FAR["stand"] + horn(hb, ht, 0.28)
    return out, eyep, {"poll": poll, "crest": crest, "mid": mid_crest, "withers": (-0.8, 0.65), "nose": head[3]}


def tail_locks(x0, y0, dx=1.0, dy=-1.0, k=3):
    out = []
    for i in range(k):
        o = 0.25 * i
        out.append(S((x0, y0 - 0.12 * i), (x0 + dx * (0.45 + o), y0 + dy * 0.1 - 0.1 * i), (x0 + dx * (0.65 + o), y0 + dy * 0.45),
                     (x0 + dx * (0.45 + o * 1.4), y0 + dy * 0.8), (x0 + dx * (0.75 + o * 1.2), y0 + dy * 1.2), (x0 + dx * (0.55 + o), y0 + dy * 1.55)))
    return out


def mane_locks(a, b, k=3, dx=0.5, dy=-0.35, wav=0.18):
    """Wavy mane strands starting along the line a->b."""
    out = []
    for i in range(k):
        t = i / max(1, k - 1)
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        out.append(S((x, y), (x + dx * 0.5 + wav, y + dy * 0.4 + wav), (x + dx, y + dy), (x + dx * 1.4 + wav, y + dy * 1.6),
                     (x + dx * 1.6, y + dy * 2.2)))
    return out


@design("unicorns_standing_proud", T)
def standing_proud(rng):
    u, e, A = unicorn_side()
    mane = [S((-1.85, 2.25), (-1.35, 2.05), (-1.15, 1.55), (-0.75, 1.2), (-0.85, 0.85)),
            S((-1.55, 1.85), (-1.0, 1.7), (-0.65, 1.3), (-0.4, 0.95), (-0.5, 0.6)),
            S((-2.25, 2.15), (-2.15, 1.85), (-2.35, 1.7))]
    tail = [S((1.7, 0.45), (2.3, 0.35), (2.5, -0.25), (2.3, -0.95), (2.6, -1.55), (2.4, -1.95)),
            S((1.84, 0.2), (2.05, -0.2), (1.95, -0.8), (2.15, -1.35), (2.0, -1.75)),
            S((2.3, 0.35), (2.7, -0.15), (2.85, -0.85), (2.7, -1.35))]
    ground = [S((-3.0, -2.55), (-1.0, -2.5), (1.0, -2.5), (3.0, -2.55))]
    return make("Proud Standing Unicorn", u + mane + tail + ground, [eye(*e, 0.08)])


def rearing_unicorn(horned=True):
    body = C((-0.9, 2.75), (-1.25, 2.62), (-1.72, 2.15), (-2.0, 1.85), (-1.96, 1.68), (-1.7, 1.64), (-1.35, 1.84), (-1.1, 1.92),
             (-1.02, 1.5), (-1.12, 1.0), (-1.45, 0.95), (-1.85, 0.88), (-2.0, 0.68), (-1.85, 0.12), (-2.0, -0.12, 1), (-1.66, -0.26, 1),
             (-1.62, 0.05), (-1.7, 0.52), (-1.25, 0.58), (-0.88, 0.36), (-0.3, -0.3), (0.3, -0.82), (0.58, -1.05), (0.48, -1.45),
             (0.36, -1.88), (0.4, -2.35), (0.36, -2.45), (0.24, -2.65, 1), (0.64, -2.65, 1), (0.68, -2.4), (0.72, -2.1), (0.95, -1.85),
             (1.2, -1.4), (1.45, -0.8), (1.45, -0.35), (1.25, 0.05), (0.7, 0.5), (0.1, 1.2), (-0.3, 1.75), (-0.5, 2.3))
    far = [S((-0.9, 0.42), (-1.35, 0.12), (-1.5, -0.2), (-1.25, -0.55), (-1.38, -0.72, 1), (-1.05, -0.86, 1), (-0.98, -0.62),
             (-1.1, -0.25), (-0.68, 0.12)),
           S((0.15, -0.72), (0.02, -1.4), (-0.05, -1.9), (0.02, -2.38), (-0.12, -2.63, 1), (0.24, -2.63, 1))]
    h = horn((-1.15, 2.6), (-1.55, 3.85), 0.28) if horned else []
    ear = poly((-0.98, 2.68), (-0.65, 3.12), (-0.68, 2.6), closed=False)
    mane = [S((-0.75, 2.8), (-0.2, 2.55), (0.05, 2.0), (0.5, 1.6), (0.6, 1.1)),
            S((-0.55, 2.55), (0.0, 2.3), (0.2, 1.75), (0.15, 1.2)),
            S((-0.42, 2.1), (0.15, 2.05), (0.45, 1.6), (0.5, 1.2))]
    tail = [S((1.42, -0.3), (2.0, -0.4), (2.3, -0.95), (2.15, -1.55), (2.5, -2.1)),
            S((1.45, -0.6), (1.75, -1.1), (1.7, -1.6), (1.95, -2.15)),
            S((2.0, -0.4), (2.6, -0.6), (2.85, -1.2), (2.75, -1.7))]
    return [body, ear] + far + h + mane + tail, (-1.35, 2.3)


@design("unicorns_rearing", T)
def rearing(rng):
    u, e = rearing_unicorn()
    ground = [S((-1.6, -2.65), (0.4, -2.68), (2.8, -2.62))]
    return make("Rearing Unicorn", u + ground, [eye(*e, 0.08)])


def galloping_unicorn(horned=True):
    body = C((-1.6, 1.9), (-1.95, 1.78), (-2.55, 1.35), (-2.85, 1.05), (-2.78, 0.88), (-2.5, 0.88), (-2.1, 1.12), (-1.75, 1.22),
             (-1.55, 0.6), (-1.62, 0.05), (-2.2, -0.28), (-2.58, -0.55), (-2.82, -0.95), (-3.0, -1.18, 1), (-2.7, -1.32, 1),
             (-2.6, -1.0), (-2.4, -0.78), (-2.12, -0.62), (-1.7, -0.45), (-1.3, -0.48), (-0.6, -0.62), (0.3, -0.62), (0.92, -0.45),
             (1.15, -0.85), (1.5, -1.25), (1.95, -1.58), (2.4, -1.92), (2.72, -2.25, 1), (2.98, -1.98, 1), (2.5, -1.68),
             (2.15, -1.12), (1.98, -0.4), (1.75, 0.22), (1.3, 0.48), (0.3, 0.38), (-0.8, 0.58), (-1.2, 1.25))
    far = [S((-1.05, -0.5), (-1.35, -0.85), (-1.25, -1.1), (-0.95, -1.3), (-0.9, -1.55, 1), (-0.62, -1.38, 1), (-0.7, -1.15),
             (-1.0, -0.98), (-0.85, -0.6)),
           S((0.65, -0.6), (0.48, -1.1), (0.15, -1.5), (-0.1, -1.72), (-0.35, -1.95, 1), (-0.05, -2.08, 1), (0.25, -1.82),
             (0.6, -1.5), (0.98, -1.05))]
    h = horn((-2.2, 1.78), (-3.1, 2.65), 0.28) if horned else []
    ear = poly((-1.85, 1.86), (-1.55, 2.32), (-1.5, 1.82), closed=False)
    mane = [S((-1.45, 2.0), (-0.85, 1.95), (-0.55, 1.5), (-0.05, 1.3), (0.1, 0.85)),
            S((-1.3, 1.65), (-0.75, 1.45), (-0.45, 0.98), (-0.55, 0.62)),
            S((-1.05, 1.0), (-0.45, 0.85), (-0.1, 0.55), (0.25, 0.48))]
    tail = [S((1.85, 0.15), (2.45, 0.55), (2.95, 0.4), (3.3, 0.75)),
            S((1.95, -0.1), (2.5, 0.05), (2.9, -0.2), (3.35, 0.0)),
            S((2.45, 0.55), (2.85, 0.85), (3.15, 1.25))]
    return [body, ear] + far + h + mane + tail, (-2.15, 1.45)


@design("unicorns_galloping", T)
def galloping(rng):
    u, e = galloping_unicorn()
    dust = [S((-0.6, -2.3), (0.3, -2.4), (1.2, -2.35)), S((-2.4, -2.0), (-1.6, -2.1))]
    return make("Galloping Unicorn", u + dust, [eye(*e, 0.08)])


def lying_unicorn():
    body = C((-1.6, 2.0), (-2.0, 1.86), (-2.45, 1.3), (-2.66, 1.0), (-2.56, 0.84), (-2.3, 0.86), (-1.9, 1.12), (-1.55, 1.2),
             (-1.48, 0.6), (-1.6, 0.0), (-1.75, -0.4), (-2.25, -0.55), (-2.45, -0.75), (-2.5, -0.95, 1), (-2.15, -1.0, 1),
             (-1.4, -1.0), (0.3, -1.0), (1.5, -1.0), (2.0, -0.65), (2.05, 0.0), (1.65, 0.42), (0.5, 0.42), (-0.6, 0.5),
             (-1.0, 0.95), (-1.25, 1.6))
    hind = S((0.55, -0.15), (1.15, 0.12), (1.55, -0.3), (1.35, -0.75), (0.6, -0.82), (0.25, -0.88, 1), (0.3, -1.0, 1))
    h = horn((-2.05, 1.85), (-2.8, 2.95), 0.28)
    ear = poly((-1.82, 1.95), (-1.6, 2.42), (-1.5, 1.9), closed=False)
    mane = [S((-1.45, 2.05), (-0.95, 1.85), (-0.75, 1.35), (-0.35, 1.0), (-0.45, 0.65)),
            S((-1.2, 1.75), (-0.75, 1.55), (-0.6, 1.1), (-0.7, 0.75))]
    tail = [S((2.0, -0.3), (2.6, -0.5), (2.8, -0.95), (2.4, -1.0)), S((2.03, -0.6), (2.35, -0.85), (2.15, -1.0))]
    return [body, hind, ear] + h + mane + tail, (-2.0, 1.45)


@design("unicorns_lying_down", T)
def lying_down(rng):
    u, e = lying_unicorn()
    flowers = []
    for x, y in [(-2.6, -1.6), (-0.6, -1.7), (1.4, -1.65), (2.8, -1.5)]:
        flowers.append(circle(x, y, 0.14, 14))
        for k in range(5):
            a = k * TAU / 5 + 0.3
            flowers.append(lens((x + 0.16 * math.cos(a), y + 0.16 * math.sin(a)), (x + 0.5 * math.cos(a), y + 0.5 * math.sin(a)), 0.38, 10))
    grass = [S((-3.2, -1.0), (-2.6, -1.0)), S((2.05, -1.0), (3.2, -1.0))]
    return make("Unicorn Resting in the Meadow", u + flowers + grass, [eye(*e, 0.08)])


@design("unicorns_grazing", T)
def grazing(rng):
    u, e, A = unicorn_side(poll=(-2.75, -0.85), rot=0.55, throat_to=(-2.15, -1.0), crest=(-1.45, 0.62), hornlen=1.0, mid=(-2.25, 0.15))
    mane = [S((-2.55, -0.55), (-2.2, -0.1), (-1.75, 0.15), (-1.3, 0.35)), S((-2.75, -0.75), (-3.0, -1.0), (-2.9, -1.3))]
    tail = tail_locks(1.75, 0.35, 0.8, -1.2)
    flowers = []
    for x, y, r in [(-2.9, -1.6, 0.3), (-0.2, -1.75, 0.25), (2.4, -2.0, 0.28), (-2.2, -2.1, 0.22)]:
        flowers.append(circle(x, y, r * 0.4, 14))
        for k in range(6):
            a = k * TAU / 6
            flowers.append(lens((x + r * 0.45 * math.cos(a), y + r * 0.45 * math.sin(a)), (x + r * 1.3 * math.cos(a), y + r * 1.3 * math.sin(a)), 0.35, 10))
        flowers.append([(x, y - r * 1.3), (x, -2.5)])
    grass = [zigzag(-3.2, 3.2, -2.55, 0.12, 22)]
    return make("Unicorn Grazing Among Flowers", u + mane + tail + flowers + grass, [eye(*e, 0.08)])


@design("unicorns_walking_mother_foal", T)
def mother_foal(rng):
    u, e, A = unicorn_side(poll=(-2.1, 1.45), rot=0.3, fore="lift", throat_to=(-1.72, 0.6), crest=(-1.3, 1.1))
    mane = mane_locks((-1.9, 1.55), (-1.0, 0.9), 3, dx=0.5, dy=-0.2, wav=0.12)
    tail = tail_locks(1.75, 0.35, 0.8, -1.2)
    f, fe = foal_parts()
    nose = A["nose"]
    dx, dy = nose[0] - 0.3 - 2.2 * 0.62, -2.5 + 2.4 * 0.62
    f = tf(flip(f), dx=dx, dy=dy, s=0.62)
    fe = (dx + 1.65 * 0.62, dy + 1.1 * 0.62)
    hearts = [heart(nose[0] - 0.4, nose[1] + 0.75, 0.25), heart(nose[0] - 0.95, nose[1] + 1.15, 0.17)]
    ground = [S((-4.6, -2.5), (-1.0, -2.5), (3.0, -2.55))]
    return make("Unicorn Mother and Foal", u + mane + tail + f + hearts + ground, [eye(*e, 0.08), eye(*fe, 0.06)])


def foal_parts():
    body = C((-1.3, 1.6), (-1.65, 1.45), (-2.05, 0.95), (-2.2, 0.7), (-2.12, 0.55), (-1.9, 0.55), (-1.55, 0.75), (-1.25, 0.85),
             (-1.15, 0.35), (-1.2, -0.05), (-1.1, -0.35), (-1.08, -1.0), (-1.1, -1.25), (-1.05, -1.9), (-1.15, -2.15, 1), (-0.85, -2.15, 1),
             (-0.83, -1.9), (-0.85, -1.3), (-0.82, -1.0), (-0.75, -0.45), (-0.3, -0.5), (0.35, -0.45), (0.5, -0.6), (0.5, -1.0),
             (0.57, -1.4), (0.6, -1.9), (0.5, -2.15, 1), (0.82, -2.15, 1), (0.85, -1.9), (0.88, -1.4), (1.0, -1.2), (1.05, -0.7),
             (1.15, -0.2), (1.0, 0.2), (0.6, 0.3), (-0.1, 0.2), (-0.6, 0.35), (-0.9, 0.9))
    far = [S((-0.6, -0.48), (-0.55, -1.0), (-0.5, -1.3), (-0.52, -1.9), (-0.62, -2.13, 1), (-0.32, -2.13, 1), (-0.3, -1.9),
             (-0.28, -1.3), (-0.26, -0.5)),
           S((0.2, -0.47), (0.25, -1.0), (0.22, -1.4), (0.25, -1.9), (0.18, -2.13, 1), (0.48, -2.13, 1))]
    h = horn((-1.55, 1.5), (-1.85, 2.05), 0.2, 2)
    ear = poly((-1.3, 1.58), (-1.1, 2.0), (-1.02, 1.5), closed=False)
    mane = [zigzag(-1.15, -0.7, 1.3, 0.1, 3), S((-1.2, 1.5), (-1.15, 1.15), (-1.0, 0.95))]
    mane = [S((-1.18, 1.52), (-0.95, 1.4), (-0.95, 1.15), (-0.75, 1.05), (-0.75, 0.82), (-0.55, 0.7), (-0.55, 0.45))]
    tail = [S((1.05, 0.05), (1.45, 0.0), (1.55, -0.4), (1.4, -0.7)), S((1.12, -0.15), (1.3, -0.45), (1.2, -0.7))]
    return [body, ear] + far + h + mane + tail, (-1.65, 1.1)


@design("unicorns_foal", T)
def foal(rng):
    f, fe = foal_parts()
    bfly = [lens((-2.55, 1.85), (-2.95, 2.3), 0.45, 12), lens((-2.55, 1.85), (-2.15, 2.3), 0.45, 12),
            lens((-2.55, 1.85), (-2.85, 1.55), 0.4, 10), lens((-2.55, 1.85), (-2.25, 1.55), 0.4, 10)]
    daisies = []
    for x, y in [(-2.6, -1.75), (1.6, -1.85), (2.4, -1.25)]:
        daisies.append(circle(x, y, 0.1, 12))
        daisies += [lens((x + 0.12 * math.cos(a), y + 0.12 * math.sin(a)), (x + 0.38 * math.cos(a), y + 0.38 * math.sin(a)), 0.35, 8)
                    for a in [k * TAU / 6 for k in range(6)]]
        daisies.append([(x, y - 0.4), (x, -2.17)])
    ground = [S((-3.0, -2.17), (0.0, -2.15), (3.0, -2.2))]
    return make("Baby Unicorn Foal", f + bfly + daisies + ground, [eye(*fe, 0.09)])


# ------------------------------------------------------------ magical objects

@design("unicorns_magic_wand", T)
def magic_wand(rng):
    st = star(-1.3, 1.3, 1.3, 5, 0.45, rot=0.25)
    inner = star(-1.3, 1.3, 0.75, 5, 0.45, rot=0.25)
    stick = tube([(-0.55, 0.55), (2.6, -2.6)], 0.32)
    bands = [[(1.85 - 0.16, -1.85 - 0.16), (1.85 + 0.16, -1.85 + 0.16)], [(2.1 - 0.16, -2.1 - 0.16), (2.1 + 0.16, -2.1 + 0.16)]]
    trail = [S((-0.2, 2.2), (0.8, 2.6), (1.8, 2.3), (2.7, 2.6)), S((0.1, 1.5), (1.1, 1.75), (2.0, 1.4), (2.9, 1.6))]
    sparks = [sparkle(1.3, 0.5, 0.35), sparkle(2.6, 0.3, 0.25), sparkle(-2.6, -0.6, 0.35), sparkle(-1.2, -1.6, 0.3),
              star(0.2, -0.5, 0.25), star(2.2, 3.2, 0.2), star(-2.7, 2.9, 0.22), circle(-0.4, -2.4, 0.12, 12), circle(0.9, -1.3, 0.1, 10)]
    return make("Magic Wand with Stardust", [st, inner, stick] + bands + trail + sparks)


@design("unicorns_crystal_cluster", T)
def crystal_cluster(rng):
    def crystal(x, w, h, lean):
        tip = (x + lean, -1.6 + h)
        sh = (x - w / 2 + lean * 0.7, -1.6 + h - w * 0.9)
        sh2 = (x + w / 2 + lean * 0.7, -1.6 + h - w * 0.9)
        out = [poly((x - w / 2, -1.6), sh, tip, sh2, (x + w / 2, -1.6), closed=False), [sh, (x + lean * 0.75, -1.6 + h - w * 1.1), sh2],
               [(x + lean * 0.75, -1.6 + h - w * 1.1), tip], [(x + lean * 0.75, -1.6 + h - w * 1.1), (x + 0.05, -1.6)]]
        return out
    parts = crystal(0.0, 1.2, 4.3, 0.0) + crystal(-1.3, 0.9, 2.8, -0.5) + crystal(1.3, 0.9, 3.0, 0.45) + \
        crystal(-2.3, 0.7, 1.6, -0.5) + crystal(2.3, 0.7, 1.7, 0.4)
    rock = [S((-3.0, -1.6), (-2.8, -2.2), (-1.5, -2.5), (0.0, -2.4), (1.6, -2.55), (2.9, -2.2), (3.0, -1.6))]
    sparks = [sparkle(-2.1, 1.6, 0.35), sparkle(1.9, 2.3, 0.3), sparkle(-0.9, 3.0, 0.25), sparkle(2.8, 0.6, 0.2)]
    return make("Glowing Crystal Cluster", parts + rock + sparks)


def mushroom(cx, base, w, h, stem_w, dots=True, tilt=0.0):
    cap_y = base + h
    cap = chain(S((cx - w / 2, cap_y), (cx - w * 0.4, cap_y + w * 0.32), (cx + tilt, cap_y + w * 0.5), (cx + w * 0.4, cap_y + w * 0.32),
                  (cx + w / 2, cap_y)), S((cx + w / 2, cap_y), (cx, cap_y - w * 0.08), (cx - w / 2, cap_y)))
    stem = S((cx - stem_w / 2, cap_y - w * 0.05), (cx - stem_w / 2 - 0.05, base + h * 0.4), (cx - stem_w * 0.6, base),
             (cx + stem_w * 0.6, base), (cx + stem_w / 2 + 0.05, base + h * 0.4), (cx + stem_w / 2, cap_y - w * 0.05))
    out = [cap, stem]
    if dots:
        out += [circle(cx + dx * w, cap_y + dy * w, 0.07 * w + 0.04, 12) for dx, dy in [(-0.25, 0.15), (0.05, 0.32), (0.27, 0.14)]]
    return out


@design("unicorns_enchanted_mushrooms", T)
def enchanted_mushrooms(rng):
    parts = mushroom(-0.6, -2.0, 2.6, 1.8, 0.7) + mushroom(1.6, -2.0, 1.6, 1.1, 0.45, tilt=0.2) + mushroom(-2.4, -2.0, 1.2, 0.75, 0.35)
    glow = [arc(-0.6, -0.15, 1.75, math.radians(20), math.radians(160), 30), arc(1.6, -0.85, 1.1, math.radians(25), math.radians(155), 20)]
    flies = [circle(x, y, 0.08, 10) for x, y in [(-2.6, 1.6), (0.9, 2.6), (2.5, 1.5), (-1.6, 2.7), (2.8, 0.2)]]
    rays = [sparkle(x, y, 0.28) for x, y in [(-2.2, 0.8), (1.8, 2.0), (0.2, 2.9)]]
    grass = [S((-3.1, -2.0), (0.0, -2.05), (3.1, -2.0))] + [poly((x, -2.0), (x + 0.12, -1.55), (x + 0.24, -2.0), closed=False)
                                                         for x in (-3.0, -1.8, 0.6, 2.6)]
    return make("Glowing Enchanted Mushrooms", parts + glow + flies + rays + grass)


@design("unicorns_wishing_well", T)
def wishing_well(rng):
    def lower(y):
        return [(1.8 * math.cos(t), y + 0.45 * math.sin(t)) for t in [math.pi + math.pi * i / 40 for i in range(41)]]
    wall = [[(-1.8, -0.5), (-1.8, -2.4)], [(1.8, -0.5), (1.8, -2.4)], ellipse(0, -0.5, 1.8, 0.45, 60), lower(-2.4)]
    bricks = []
    for row, y in enumerate([-0.5, -1.1, -1.7]):
        if row:
            bricks.append(lower(y))
        for k in range(4):
            x = -1.35 + 0.9 * k + (0.45 if row % 2 else 0.0)
            if abs(x) < 1.6:
                yy = y - 0.45 * math.sqrt(max(0.0, 1 - (x / 1.8) ** 2))
                bricks.append([(x, yy - 0.05), (x, yy - 0.55)])
    posts = [rect(-1.65, -0.5, -1.4, 1.9), rect(1.4, -0.5, 1.65, 1.9)]
    roof = [poly((-2.3, 1.7), (0, 3.0), (2.3, 1.7)), [(-1.9, 1.95), (1.9, 1.95)]]
    axle = [[(-1.4, 1.0), (1.4, 1.0)], circle(1.95, 1.0, 0.3, 20), [(1.95, 1.0), (2.3, 0.7)]]
    rope = [[(0.0, 1.0), (0.0, 0.2)]]
    bucket = [poly((-0.4, 0.2), (0.4, 0.2), (0.3, -0.4), (-0.3, -0.4)), arc(0, 0.2, 0.4, 0, math.pi, 14)]
    sparks = [sparkle(-2.6, 0.5, 0.35), sparkle(2.7, -0.4, 0.3), star(-2.6, 2.6, 0.3), star(2.7, 2.5, 0.25), sparkle(0.9, -0.15, 0.2)]
    return make("Enchanted Wishing Well", wall + bricks + posts + roof + axle + rope + bucket + sparks)


# dropped: the subject repeats another book
def star_potions(rng):
    def flask(cx, r, neck_h, by=-2.4):
        cy = by + r
        body = chain([(cx - 0.22, cy + r + neck_h)], arc(cx, cy, r, math.pi / 2 + 0.22, TAU + math.pi / 2 - 0.22, 60),
                     [(cx + 0.22, cy + r + neck_h)])
        rim = rrect(cx - 0.32, cy + r + neck_h, cx + 0.32, cy + r + neck_h + 0.22, 0.08)
        liquid = wave(cx - r * 0.9, cx + r * 0.9, cy + r * 0.25, 0.07, 2, 30)
        return [body, rim, liquid, star(cx, cy - r * 0.25, r * 0.38)]
    tall = [S((0.75, 1.4), (0.75, 0.2), (1.3, -0.4), (1.3, -2.4)), S((1.75, 1.4), (1.75, 0.2), (1.2, -0.4)),
            ]
    tall = [poly((0.95, 1.6), (0.95, 0.3), (0.45, -0.5), (0.45, -2.4), (2.05, -2.4), (2.05, -0.5), (1.55, 0.3), (1.55, 1.6), closed=False),
            rrect(0.85, 1.6, 1.65, 1.95, 0.1), heart(1.25, -1.35, 0.4), wave(0.5, 2.0, -0.6, 0.06, 2, 30)]
    parts = flask(-1.4, 1.05, 0.7) + tall + flask(2.65, 0.55, 0.35)
    bubbles = [circle(x, y, r, 14) for x, y, r in [(-1.5, 1.6, 0.16), (-1.2, 2.2, 0.12), (-1.55, 2.7, 0.09), (1.3, 2.4, 0.13), (1.1, 2.9, 0.09)]]
    sparks = [sparkle(-2.9, 0.4, 0.3), sparkle(0.0, 2.2, 0.32), sparkle(2.8, 1.0, 0.3)]
    return make("Starlight Potion Bottles", parts + bubbles + sparks)


@design("unicorns_rainbow_clouds", T)
def rainbow_clouds(rng):
    bows = rainbow(0, -0.8, 1.4, 2.9, 5, 0, math.pi)
    clouds = [cloud(-2.3, -1.15, 2.2, 1.1), cloud(2.3, -1.15, 2.2, 1.1)]
    sun = [circle(0, 2.6, 0.45, 30)] + [[(0.6 * math.cos(a), 2.6 + 0.6 * math.sin(a)), (0.85 * math.cos(a), 2.6 + 0.85 * math.sin(a))]
                                        for a in [k * TAU / 10 for k in range(10)]]
    drops = [lens((x, y), (x, y - 0.4), 0.35, 8) for x, y in [(-2.6, -2.0), (-2.0, -2.3), (2.0, -2.0), (2.6, -2.35)]]
    return make("Rainbow Between Two Clouds", bows + clouds + sun + drops)


@design("unicorns_shooting_star", T)
def shooting_star(rng):
    st = star(1.4, 1.4, 1.3, 5, 0.45, rot=-0.3)
    face = [arc(1.0, 1.45, 0.15, 0.3, math.pi - 0.3, 8), arc(1.75, 1.45, 0.15, 0.3, math.pi - 0.3, 8),
            arc(1.38, 1.2, 0.3, math.pi + 0.4, TAU - 0.4, 12)]
    tails = [S((0.4, 1.0), (-0.6, 0.1), (-1.6, -0.9), (-2.8, -2.2)), S((0.6, 0.55), (-0.2, -0.3), (-1.0, -1.3), (-1.8, -2.6)),
             S((0.2, 1.55), (-0.9, 0.9), (-2.0, 0.0), (-3.1, -1.1))]
    sparks = [sparkle(-1.5, 2.0, 0.35), sparkle(2.6, -1.4, 0.4), star(-0.5, -2.1, 0.25), star(-2.7, 1.0, 0.22), star(0.6, -1.0, 0.2)]
    return make("Wishing Shooting Star", [st] + face + tails + sparks)


@design("unicorns_sleepy_moon", T)
def sleepy_moon(rng):
    outer = arc(0, 0, 2.6, math.radians(60), math.radians(300), 80)
    inner = arc(1.25, 0.0, 2.05, math.radians(118), math.radians(242), 60)
    moon = chain(outer, inner[::-1][1:])
    # inner arc must run from outer end back to start: compute explicitly
    p_top = outer[0]
    p_bot = outer[-1]
    inner = S(p_bot, (-0.65, -1.1), (-0.85, 0.0), (-0.65, 1.1), p_top)
    moon = chain(outer, inner)
    face = [arc(-1.55, 0.55, 0.25, math.pi + 0.3, TAU - 0.3, 10), S((-1.65, -0.55), (-1.4, -0.75), (-1.15, -0.6)),
            S((-2.2, 0.25), (-2.05, 0.1))]
    cap = [S((1.3, 2.25), (1.9, 2.9), (2.7, 2.5), (2.9, 1.7)), circle(2.9, 1.5, 0.22, 16)]
    stars_ = [star(2.2, -0.3, 0.35), star(1.4, -1.8, 0.28), star(2.8, -1.4, 0.22), sparkle(0.6, 0.6, 0.3), star(-2.8, 2.6, 0.25)]
    z = [poly((0.2, 2.3), (0.55, 2.3), (0.2, 1.95), (0.55, 1.95), closed=False), poly((0.75, 2.85), (1.0, 2.85), (0.75, 2.6), (1.0, 2.6), closed=False)]
    return make("Sleepy Crescent Moon", [moon] + face + stars_ + z, [])


@design("unicorns_lantern_tree", T)
def lantern_tree(rng):
    trunk = [S((-0.5, -2.6), (-0.35, -1.5), (-0.4, -0.5), (-1.0, 0.3), (-2.0, 0.8)),
             S((0.5, -2.6), (0.35, -1.5), (0.45, -0.5), (1.1, 0.3), (2.2, 0.7)),
             S((-0.4, -0.5), (-0.2, 0.4), (-0.5, 1.4)), S((0.45, -0.5), (0.3, 0.5), (0.6, 1.5))]
    roots = [S((-0.5, -2.6), (-1.1, -2.75)), S((0.5, -2.6), (1.2, -2.75))]
    canopy = [(2.95 * math.cos(t) * (1 + 0.06 * math.sin(9 * t)), 1.85 + 1.15 * math.sin(t) * (1 + 0.08 * math.sin(9 * t)))
              for t in [math.radians(-12 + 204 * i / 200) for i in range(201)]]
    canopy = chain(canopy, S(canopy[-1], (-1.6, 0.85), (-0.5, 1.2), (0.6, 1.3), (1.6, 0.9), canopy[0]))
    lant = []
    for x, y in [(-2.2, 0.75), (1.9, 0.55), (-0.9, 0.4)]:
        lant += [[(x, y + 0.3), (x, y)], rrect(x - 0.25, y - 0.65, x + 0.25, y, 0.08), poly((x - 0.3, y), (x + 0.3, y), (x, y + 0.15)),
                 sparkle(x, y - 0.33, 0.14)]
    flies = [circle(x, y, 0.08, 10) for x, y in [(2.6, -0.6), (-2.6, -0.8), (1.5, -1.8), (-1.7, -1.9)]]
    ground = [S((-3.0, -2.75), (0.0, -2.7), (3.0, -2.75))]
    return make("Fairy Lantern Tree", trunk + roots + [canopy] + lant + flies + ground)


# dropped: the subject repeats another book
def spell_book(rng):
    cover = poly((-3.0, -1.6), (0.0, -2.2), (3.0, -1.6), (3.0, -1.9), (0.0, -2.5), (-3.0, -1.9))
    left = S((0.0, -2.2), (-1.2, -1.6), (-2.8, -1.7), (-2.8, 0.5), (-1.3, 0.6), (0.0, 0.0))
    right = S((0.0, -2.2), (1.2, -1.6), (2.8, -1.7), (2.8, 0.5), (1.3, 0.6), (0.0, 0.0))
    spine = [[(0.0, 0.0), (0.0, -2.2)]]
    lines = [S((-2.4, y), (-1.4, y + 0.05), (-0.4, y - 0.15)) for y in (-0.1, -0.5, -0.9)] + \
        [S((0.4, y - 0.15), (1.4, y + 0.05), (2.4, y)) for y in (-0.1, -0.5)]
    magic = [S((0.0, 0.2), (-0.5, 1.0), (0.3, 1.6), (-0.2, 2.4)), S((0.3, 0.2), (0.9, 0.9), (1.3, 1.8), (2.0, 2.3))]
    sparks = [star(-0.2, 2.75, 0.35), sparkle(2.3, 2.6, 0.32), sparkle(-1.5, 1.5, 0.35), star(1.0, 1.1, 0.22), circle(-0.9, 2.3, 0.1, 10),
              sparkle(1.4, -1.0, 0.28)]
    return make("Open Book of Spells", [cover, left, right] + spine + lines + magic + sparks)


@design("unicorns_gem_heart", T)
def gem_heart(rng):
    outer = poly((0, -2.6), (-2.8, 0.6), (-2.2, 1.9), (-1.2, 2.3), (0, 1.5), (1.2, 2.3), (2.2, 1.9), (2.8, 0.6))
    table = poly((-1.5, 0.9), (-0.9, 1.5), (0, 0.9), (0.9, 1.5), (1.5, 0.9), (0, -0.9))
    facets = [[(-2.8, 0.6), (-1.5, 0.9)], [(-2.2, 1.9), (-1.5, 0.9)], [(-1.2, 2.3), (-0.9, 1.5)], [(0, 1.5), (0, 0.9)],
              [(1.2, 2.3), (0.9, 1.5)], [(2.2, 1.9), (1.5, 0.9)], [(2.8, 0.6), (1.5, 0.9)], [(-1.5, 0.9), (0, -2.6)], [(1.5, 0.9), (0, -2.6)],
              [(0, -0.9), (0, -2.6)]]
    sparks = [sparkle(-2.6, 2.7, 0.35), sparkle(2.7, -1.0, 0.4), sparkle(1.7, 2.9, 0.25)]
    return make("Faceted Gemstone Heart", [outer, table] + facets + sparks)


@design("unicorns_fairy_lantern", T)
def fairy_lantern(rng):
    ring = [circle(0, 2.6, 0.3, 20)]
    cap = [S((-1.3, 1.5), (-0.8, 2.0), (0.0, 2.3), (0.8, 2.0), (1.3, 1.5)), [(-1.45, 1.5), (1.45, 1.5)]]
    frame = [rrect(-1.25, -1.8, 1.25, 1.5, 0.15), rrect(-0.85, -1.4, 0.85, 1.1, 0.4)]
    base = [poly((-1.5, -1.8), (1.5, -1.8), (1.2, -2.3), (-1.2, -2.3)), [(-0.6, -2.3), (-0.5, -2.6), (0.5, -2.6), (0.6, -2.3)]]
    flame = [lens((0, -0.9), (0, 0.6), 0.32, 18), lens((0, -0.8), (0, 0.0), 0.3, 10)]
    candle = [rect(-0.3, -1.4, 0.3, -0.85)]
    sparks = [sparkle(-2.3, 1.0, 0.35), sparkle(2.3, 0.2, 0.3), star(2.2, 2.2, 0.25), star(-2.2, -1.2, 0.22), circle(2.5, -1.5, 0.1, 10)]
    vine = [S((1.25, 1.2), (1.8, 0.9), (1.7, 0.2), (2.0, -0.4)), lens((1.75, 0.6), (2.25, 0.9), 0.4, 10), lens((1.8, -0.1), (2.3, 0.0), 0.4, 10)]
    return make("Glowing Fairy Lantern", ring + cap + frame + base + flame + candle + sparks + vine)


@design("unicorns_mushroom_house", T)
def mushroom_house(rng):
    cap = C((-2.8, 0.6, 1), (-2.5, 1.6), (-1.4, 2.6), (0.0, 2.95), (1.4, 2.6), (2.5, 1.6), (2.8, 0.6, 1), (0.0, 0.3))
    spots = [circle(-1.6, 1.7, 0.35, 20), circle(0.2, 2.35, 0.32, 20), circle(1.7, 1.5, 0.3, 20), circle(-0.6, 1.2, 0.22, 16)]
    stem = S((-1.6, 0.45), (-1.7, -1.0), (-1.9, -2.4), (1.9, -2.4), (1.7, -1.0), (1.6, 0.45))
    door = chain([(-0.5, -2.4)], arc(0, -1.3, 0.5, math.pi, 0, 20), [(0.5, -2.4)])
    knob = circle(0.3, -1.8, 0.07, 10)
    windows = [circle(-1.0, -0.4, 0.35, 24), circle(1.0, -0.4, 0.35, 24), [(-1.35, -0.4), (-0.65, -0.4)], [(0.65, -0.4), (1.35, -0.4)]]
    steps = [S((-0.7, -2.4), (-0.8, -2.65), (0.8, -2.65), (0.7, -2.4))]
    chimney = [poly((1.0, 2.75), (1.0, 3.3), (1.4, 3.3), (1.4, 2.6), closed=False), S((1.2, 3.4), (1.5, 3.7), (1.2, 4.0), (1.5, 4.3))]
    grass = [S((-3.0, -2.4), (-1.9, -2.4)), S((1.9, -2.4), (3.0, -2.4))]
    return make("Fairy Mushroom Cottage", [cap, stem, door, knob] + spots + windows + steps + chimney + grass)


# dropped: the subject repeats another book
def crystal_ball(rng):
    ball = circle(0, 0.8, 2.0, 120)
    shine = [arc(0, 0.8, 1.6, math.radians(110), math.radians(160), 14)]
    stand = [S((-1.3, -1.0), (-1.6, -1.6), (-2.0, -2.0)), S((1.3, -1.0), (1.6, -1.6), (2.0, -2.0)),
             rrect(-2.4, -2.6, 2.4, -2.0, 0.15), [(-1.6, -2.3), (1.6, -2.3)]]
    inside = [star(0.2, 1.2, 0.55), sparkle(-0.8, 0.2, 0.3), sparkle(0.9, 0.0, 0.25), S((-1.3, -0.1), (-0.6, 0.6), (0.4, 0.4), (1.3, 1.0))]
    rays = [sparkle(-2.6, 2.4, 0.35), sparkle(2.6, 2.6, 0.3)]
    return make("Enchanted Crystal Ball on a Stand", [ball] + shine + stand + inside + rays)


@design("unicorns_dreamcatcher", T)
def dreamcatcher(rng):
    hoop = [circle(0, 1.0, 1.9, 120), circle(0, 1.0, 1.7, 110)]
    web = []
    pts = [(1.7 * math.cos(a), 1.0 + 1.7 * math.sin(a)) for a in [k * TAU / 8 + math.pi / 8 for k in range(8)]]
    ring2 = [(0.95 * math.cos(a), 1.0 + 0.95 * math.sin(a)) for a in [k * TAU / 8 for k in range(8)]]
    web.append(chain(*[[pts[k], ring2[(k + 1) % 8]] for k in range(8)], [pts[0]]))
    web.append(circle(0, 1.0, 0.3, 20))
    web += [[ring2[k], (0.3 * math.cos(k * TAU / 8), 1.0 + 0.3 * math.sin(k * TAU / 8))] for k in range(0, 8, 2)]
    feathers = []
    for x, top in [(-1.3, -0.3), (0.0, -0.95), (1.3, -0.3)]:
        feathers += [[(x, top), (x, top - 0.6)], lens((x, top - 0.6), (x, top - 2.0), 0.18, 16), [(x, top - 0.6), (x, top - 2.0)]]
    beads = [circle(x, y, 0.12, 12) for x, y in [(-1.3, -0.55), (0.0, -1.2), (1.3, -0.55)]]
    top = [[(0, 2.9), (0, 3.3)], circle(0, 3.45, 0.15, 12)]
    return make("Dreamcatcher with Feathers", hoop + web + feathers + beads + top)


# dropped: the subject repeats another book
def flower_fairy(rng):
    head = circle(0, 1.75, 0.45, 40)
    hair = [S((-0.45, 1.85), (-0.3, 2.35), (0.3, 2.4), (0.6, 1.9), (0.7, 1.2), (0.45, 0.95))]
    dress = S((-0.25, 1.25), (-0.4, 0.6), (-1.1, -0.9), (-0.4, -0.7), (0.0, -1.0), (0.4, -0.7), (1.1, -0.9), (0.4, 0.6), (0.25, 1.25))
    wings = [lens((-0.2, 0.9), (-2.6, 2.4), 0.3, 24), lens((-0.2, 0.7), (-2.3, -0.4), 0.28, 20),
             lens((0.2, 0.9), (2.6, 2.4), 0.3, 24), lens((0.2, 0.7), (2.3, -0.4), 0.28, 20)]
    arms = [S((-0.3, 1.0), (-0.9, 0.7), (-1.2, 1.1)), S((0.3, 1.0), (0.9, 1.3), (1.3, 1.8))]
    wand = [[(1.3, 1.8), (1.7, 2.4)], star(1.85, 2.65, 0.3)]
    legs = [[(-0.25, -0.85), (-0.35, -1.7)], [(0.25, -0.85), (0.4, -1.7)]]
    flower = [S((-2.2, -2.6), (-1.6, -2.0), (-0.6, -1.85), (0.0, -1.9), (0.6, -1.85), (1.6, -2.0), (2.2, -2.6)),
              S((-0.6, -1.85), (-0.3, -2.3), (0.0, -1.9)), S((0.0, -1.9), (0.3, -2.3), (0.6, -1.85)), [(0.0, -2.6), (0.0, -3.4)]]
    flower = [S((-2.2, -1.75), (-1.2, -2.6), (0.0, -2.75), (1.2, -2.6), (2.2, -1.75)),
              lens((-2.2, -1.75), (-0.3, -2.6), 0.3, 16), lens((2.2, -1.75), (0.3, -2.6), 0.3, 16), [(0.0, -2.75), (0.0, -3.4)]]
    sparks = [sparkle(2.5, 3.0, 0.3), sparkle(-2.4, 3.0, 0.3)]
    crown = [zigzag(-0.35, 0.35, 2.3, 0.1, 3)]
    return make("Little Flower Fairy", [head, dress] + hair + wings + arms + wand + legs + flower + sparks + crown,
                [eye(-0.15, 1.75, 0.06), eye(0.12, 1.75, 0.06)])


@design("unicorns_magic_mirror", T)
def magic_mirror(rng):
    frame = [ellipse(0, 0.6, 1.8, 2.4, 120), ellipse(0, 0.6, 1.45, 2.05, 110)]
    crest = [S((-1.0, 2.75), (-0.6, 3.3), (0.0, 3.05), (0.6, 3.3), (1.0, 2.75)), star(0, 3.55, 0.3)]
    handle = [poly((-0.3, -1.8), (-0.35, -3.0), (0.35, -3.0), (0.3, -1.8), closed=False), ellipse(0, -2.4, 0.42, 0.18, 20)]
    swirls = [spiral(-1.9, -1.0, 0.05, 0.4, 1.2), spiral(1.9, -1.0, 0.05, 0.4, 1.2, rot=math.pi)]
    glass = [sparkle(-0.5, 1.4, 0.35), [(0.4, 1.8), (0.9, 1.0)], [(0.6, 2.0), (0.8, 1.7)], sparkle(0.5, -0.4, 0.25)]
    return make("Enchanted Hand Mirror", frame + crest + handle + swirls + glass)


@design("unicorns_fairy_door", T)
def fairy_door(rng):
    trunk = [S((-2.0, -2.6), (-1.7, -1.0), (-1.8, 1.0), (-2.4, 2.4), (-2.9, 3.0)), S((2.0, -2.6), (1.7, -1.0), (1.8, 1.0), (2.4, 2.4), (2.9, 3.0)),
             S((-1.8, 1.0), (-0.6, 2.4), (-0.4, 3.0)), S((1.8, 1.0), (0.8, 2.3), (0.6, 3.0))]
    roots = [S((-2.0, -2.6), (-2.6, -2.75), (-3.0, -2.7)), S((2.0, -2.6), (2.6, -2.75), (3.0, -2.7))]
    door = [chain([(-0.9, -2.6)], arc(0, -0.6, 0.9, math.pi, 0, 30), [(0.9, -2.6)]), [(0, -2.6), (0, 0.3)], circle(0.3, -1.4, 0.08, 10),
            circle(-0.5, -0.65, 0.15, 12), circle(0.5, -0.65, 0.15, 12)]
    window = [circle(-1.0, 1.2, 0.35, 24), [(-1.35, 1.2), (-0.65, 1.2)], [(-1.0, 0.85), (-1.0, 1.55)]]
    bark = [S((1.2, -1.8), (1.3, -1.0)), S((-1.3, 0.2), (-1.4, -0.6)), S((1.2, 0.6), (1.35, 1.2))]
    path = [S((-0.9, -2.6), (-1.3, -3.2)), S((0.9, -2.6), (1.3, -3.2))]
    mushrooms = mushroom(2.5, -2.72, 0.7, 0.45, 0.2, False) + mushroom(-2.5, -2.72, 0.55, 0.35, 0.16, False)
    lantern = [[(1.2, 0.5), (1.2, 0.2)], rrect(1.0, -0.35, 1.4, 0.2, 0.06)]
    return make("Fairy Door in a Tree", trunk + roots + door + window + bark + path + mushrooms + lantern)


@design("unicorns_star_mobile", T)
def star_mobile(rng):
    bar = [S((-2.6, 1.6), (0.0, 2.0), (2.6, 1.6)), [(0, 2.0), (0, 3.0)], circle(0, 3.15, 0.15, 12)]
    out = bar
    for x, drop, kind in [(-2.4, 1.2, "moon"), (-1.2, 2.2, "star"), (0.0, 1.0, "cloud"), (1.2, 2.4, "star"), (2.4, 1.4, "heart")]:
        y0 = 2.0 - 0.4 * (x / 2.6) ** 2 * 1.0
        out.append([(x, y0), (x, y0 - drop)])
        cy = y0 - drop - 0.55
        if kind == "star":
            out.append(star(x, cy, 0.55))
        elif kind == "moon":
            out.append(chain(arc(x, cy, 0.55, math.radians(60), math.radians(300), 30), S(transform([(0.27, -0.476)], x, cy)[0], (x - 0.05, cy), transform([(0.27, 0.476)], x, cy)[0])))
        elif kind == "cloud":
            out.append(cloud(x, cy + 0.27, 1.1, 0.6))
        else:
            out.append(heart(x, cy - 0.05, 0.42))
    return make("Moon and Stars Nursery Mobile", out)


# ------------------------------------------------------------ more unicorns

def leaping_unicorn(horned=True):
    body = C((-1.5, 2.0), (-1.85, 1.92), (-2.45, 1.55), (-2.8, 1.3), (-2.75, 1.12), (-2.48, 1.1), (-2.05, 1.3), (-1.7, 1.35),
             (-1.55, 0.75), (-1.65, 0.2), (-1.95, -0.15), (-2.05, -0.45), (-1.75, -0.75), (-1.5, -0.98, 1), (-1.3, -0.75, 1),
             (-1.6, -0.5), (-1.7, -0.32), (-1.45, -0.25), (-1.2, -0.35), (-0.5, -0.55), (0.3, -0.55), (0.95, -0.3), (1.2, -0.6),
             (1.6, -0.95), (2.0, -1.15), (2.5, -1.45), (2.8, -1.68, 1), (3.0, -1.38, 1), (2.6, -1.15), (2.25, -0.7), (2.15, -0.2),
             (2.0, 0.2), (1.7, 0.55), (1.2, 0.75), (0.3, 0.6), (-0.75, 0.85), (-1.1, 1.4))
    far = [S((-1.1, -0.4), (-1.45, -0.65), (-1.25, -1.0), (-0.98, -1.17, 1), (-0.85, -0.95, 1), (-1.0, -0.75), (-0.8, -0.5)),
           S((0.9, -0.45), (1.4, -1.1), (1.9, -1.55), (2.35, -1.85), (2.6, -2.1, 1), (2.82, -1.85, 1), (2.4, -1.55))]
    h = horn((-2.05, 1.85), (-2.85, 2.85), 0.28) if horned else []
    ear = poly((-1.72, 1.97), (-1.42, 2.45), (-1.38, 1.92), closed=False)
    mane = [S((-1.35, 2.05), (-0.8, 1.95), (-0.55, 1.5), (-0.1, 1.35), (0.05, 0.9)),
            S((-1.2, 1.6), (-0.7, 1.45), (-0.45, 1.05), (-0.5, 0.75))]
    tail = [S((2.0, 0.15), (2.6, 0.5), (2.95, 0.25), (3.35, 0.55)), S((2.1, -0.1), (2.6, 0.0), (3.0, -0.3), (3.4, -0.15)),
            S((2.6, 0.5), (2.95, 0.85), (3.2, 1.2))]
    return [body, ear] + far + h + mane + tail, (-2.0, 1.55)


def wing(dx, dy, s=1.0, rot=0.0, mirror=False, feathers=6):
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


@design("unicorns_leap_rainbow", T)
def leap_rainbow(rng):
    u, e = leaping_unicorn()
    u = tf(u, dy=1.5, s=0.85)
    e = (e[0] * 0.85, e[1] * 0.85 + 1.5)
    bows = rainbow(0.0, -2.9, 1.9, 3.2, 4, math.radians(8), math.radians(172))
    clouds = [cloud(-3.0, -2.6, 1.8, 0.9), cloud(3.0, -2.6, 1.8, 0.9)]
    sparks = [sparkle(-2.7, 2.6, 0.35), sparkle(2.8, 2.4, 0.3), star(0.2, 2.9, 0.25)]
    return make("Unicorn Leaping over a Rainbow", u + bows + clouds + sparks, [eye(*e, 0.07)])


@design("unicorns_pegasus", T)
def pegasus(rng):
    u, e = leaping_unicorn(horned=False)
    wings = wing(-0.35, 0.75, 1.05, 0.05)
    far_w = [transform(p, dx=-0.9, dy=0.95, s=0.75, rot=0.25) for p in wing(0, 0, 1.0, 0.0)[:1]]
    clouds = [cloud(-1.8, -2.4, 2.4, 1.0), cloud(1.6, -2.7, 2.0, 0.85), cloud(-2.4, 2.9, 1.4, 0.6)]
    return make("Pegasus Soaring through the Clouds", u + wings + far_w + clouds, [eye(*e, 0.08)])


@design("unicorns_alicorn", T)
def alicorn(rng):
    u, e, A = unicorn_side(fore="lift")
    mane = [S((-1.85, 2.25), (-1.35, 2.05), (-1.15, 1.55), (-0.75, 1.2), (-0.85, 0.85)),
            S((-1.55, 1.85), (-1.0, 1.7), (-0.65, 1.3), (-0.4, 0.95), (-0.5, 0.6))]
    tail = tail_locks(1.75, 0.35, 0.8, -1.25)
    wings = wing(-0.35, 0.5, 1.0, 0.25) + [transform(p, dx=-0.75, dy=0.6, s=0.8, rot=0.45) for p in wing(0, 0)[:1]]
    stars_ = [star(-2.8, -0.6, 0.3), star(2.8, 2.8, 0.3), sparkle(-0.2, -1.7, 0.3), sparkle(2.6, -1.2, 0.3)]
    ground = [S((-3.0, -2.5), (0.0, -2.48), (3.0, -2.5))]
    return make("Winged Alicorn", u + mane + tail + wings + stars_ + ground, [eye(*e, 0.08)])


@design("unicorns_enchanted_pool", T)
def enchanted_pool(rng):
    u, e, A = unicorn_side(poll=(-2.75, -0.5), rot=0.75, throat_to=(-2.2, -0.75), crest=(-1.45, 0.62), hornlen=1.0, mid=(-2.3, 0.25))
    mane = [S((-2.6, -0.2), (-2.2, 0.2), (-1.75, 0.4), (-1.3, 0.45)), S((-2.8, -0.42), (-3.1, -0.65), (-3.05, -0.95))]
    tail = tail_locks(1.75, 0.35, 0.8, -1.2)
    pool = [ellipse(-3.05, -2.3, 1.2, 0.35, 60), ellipse(-3.0, -2.25, 0.55, 0.15, 40)]
    lilies = [lens((-3.9, -2.35), (-3.5, -2.25), 0.4, 8)]
    reeds = [S((-4.2, -2.2), (-4.25, -1.2)), S((-4.0, -2.25), (-3.9, -1.4)), ellipse(-4.25, -1.0, 0.07, 0.25, 12)]
    sparks = [sparkle(-3.6, 0.6, 0.35), star(2.6, 2.0, 0.3), sparkle(0.6, 1.8, 0.3), sparkle(-1.6, 1.6, 0.3)]
    ground = [S((-1.55, -2.48), (0.5, -2.48), (3.0, -2.5))]
    return make("Unicorn Drinking from the Enchanted Pool", u + mane + tail + pool + lilies + reeds + sparks + ground, [eye(*e, 0.08)])


@design("unicorns_moonlit_rearing", T)
def moonlit_rearing(rng):
    u, e = rearing_unicorn()
    u = tf(u, dx=0.6, dy=-0.2, s=0.75)
    e = (e[0] * 0.75 + 0.6, e[1] * 0.75 - 0.2)
    m_outer = arc(-1.2, 1.4, 1.7, math.radians(70), math.radians(290), 60)
    moon = chain(m_outer, S(m_outer[-1], (-1.35, 0.6), (-1.6, 1.4), (-1.35, 2.2), m_outer[0]))
    stars_ = [star(x, y, r) for x, y, r in [(2.6, 2.7, 0.3), (1.6, 3.0, 0.2), (-2.8, -0.6, 0.22), (2.9, 1.2, 0.2), (-0.2, 3.1, 0.25)]]
    hill = [S((-3.2, -2.4), (-1.5, -2.0), (0.4, -2.2), (1.8, -2.35), (3.3, -2.0))]
    return make("Unicorn Rearing under the Moon", [moon] + u + stars_ + hill, [eye(*e, 0.07)])


@design("unicorns_portrait", T)
def portrait(rng):
    head = S((1.4, -2.8), (1.1, -1.6), (1.0, -0.5), (1.2, 0.84), (0.72, 0.53), (0.12, -0.19), (-0.96, -0.82), (-1.61, -0.6),
             (-1.73, -0.19), (-1.2, 0.6), (-0.24, 1.97), (0.6, 2.4), (1.6, 1.8), (2.4, 0.4), (2.8, -1.2), (3.0, -2.8))
    chest = S((1.4, -2.8), (2.2, -3.05), (3.0, -2.8))
    nostril = S((-1.35, -0.1), (-1.5, -0.3), (-1.3, -0.45))
    mouth = S((-1.6, -0.55), (-1.3, -0.5), (-1.15, -0.6))
    cheek = S((-0.35, -0.45), (0.25, -0.1), (0.55, 0.45))
    eye_ = [S((-0.45, 1.25), (-0.15, 1.42), (0.2, 1.2)), S((-0.45, 1.25), (-0.12, 1.08), (0.2, 1.2))] + \
        [[(-0.1 + 0.15 * k, 1.42 - 0.03 * k * k), (-0.15 + 0.25 * k, 1.68 - 0.06 * k * k)] for k in range(3)]
    ear = poly((0.4, 2.35), (0.95, 3.35), (1.15, 2.2), closed=False)
    h = horn((-0.15, 2.15), (-1.45, 4.55), 0.62, 5)
    fore = [S((0.4, 2.45), (-0.25, 2.55), (-0.55, 2.0), (-0.3, 1.6)), S((0.55, 2.5), (0.1, 2.3), (0.1, 1.9))]
    locks = []
    for k, (x, y) in enumerate([(0.95, 2.4), (1.6, 1.85), (2.1, 1.1), (2.45, 0.25), (2.7, -0.7)]):
        locks.append(S((x, y), (x + 0.55, y - 0.05), (x + 0.85, y - 0.55), (x + 0.7, y - 1.1), (x + 0.95, y - 1.6)))
    curl = [S((3.2, 0.9), (3.75, 0.3), (3.55, -0.5), (3.85, -1.3), (3.6, -2.0), (3.75, -2.6))]
    return make("Unicorn Portrait with Flowing Mane", [head, chest, nostril, mouth, cheek, ear] + eye_ + h + fore + locks + curl,
                [eye(-0.12, 1.25, 0.12)])


def front_head():
    """Front view unicorn head (right half mirrored)."""
    half = S((0.0, 2.2), (0.9, 1.95), (1.08, 1.2), (1.0, 0.4), (0.72, -0.7), (0.8, -1.45), (0.55, -2.05), (0.0, -2.18))
    face = chain(mirror_x(half)[::-1], half[1:])
    ears = [poly((0.6, 2.02), (1.45, 2.95), (1.12, 1.62), closed=False), poly((0.85, 1.95), (1.28, 2.55), (1.1, 1.85), closed=False)]
    eye_ = [S((0.45, 0.95), (0.75, 1.12), (1.0, 0.92)), S((0.45, 0.95), (0.75, 0.75), (1.0, 0.92))] + \
        [[(0.85, 1.08), (1.15, 1.3)], [(0.95, 1.0), (1.3, 1.1)]]
    nost = [S((0.25, -1.25), (0.45, -1.45), (0.35, -1.7))]
    mouth = [S((-0.3, -1.85), (0.0, -1.95), (0.3, -1.85))]
    half_parts = ears + eye_ + nost
    out = [face] + half_parts + [mirror_x(p) for p in half_parts] + mouth
    return out, [(0.72, 0.94), (-0.72, 0.94)]


@design("unicorns_flower_crown", T)
def flower_crown(rng):
    f, eyes_ = front_head()
    h = horn((0.0, 2.1), (0.0, 4.3), 0.6, 5)
    neck = [S((0.8, -1.0), (1.0, -2.0), (1.35, -3.0)), S((-0.8, -1.0), (-1.0, -2.0), (-1.35, -3.0))]
    mane = [S((-1.0, 1.7), (-1.6, 1.2), (-1.45, 0.3), (-1.85, -0.6), (-1.7, -1.6), (-2.1, -2.6)),
            S((-1.05, 1.0), (-1.3, 0.2), (-1.15, -0.6), (-1.4, -1.5)),
            S((1.0, 1.7), (1.6, 1.2), (1.45, 0.3), (1.85, -0.6), (1.7, -1.6), (2.1, -2.6)),
            S((1.05, 1.0), (1.3, 0.2), (1.15, -0.6), (1.4, -1.5))]
    crown = []
    for x, y, r in [(-0.62, 2.35, 0.4), (0.62, 2.35, 0.4), (-1.55, 1.45, 0.32), (1.55, 1.45, 0.32)]:
        crown.append(circle(x, y, r * 0.35, 14))
        for k in range(5):
            a = k * TAU / 5 + 0.3
            crown.append(lens((x + r * 0.35 * math.cos(a), y + r * 0.35 * math.sin(a)), (x + r * math.cos(a), y + r * math.sin(a)), 0.45, 8))
    leaves = [lens((-1.05, 2.25), (-0.9, 2.75), 0.4, 10), lens((1.05, 2.25), (0.9, 2.75), 0.4, 10)]
    return make("Unicorn with a Flower Crown", f + [h[0]] + h[1:] + neck + mane + crown + leaves, [eye(*p, 0.1) for p in eyes_])


@design("unicorns_castle", T)
def castle_scene(rng):
    u, e, A = unicorn_side(fore="lift")
    tail = tail_locks(1.75, 0.35, 0.8, -1.2)
    mane = [S((-1.85, 2.25), (-1.35, 2.05), (-1.15, 1.55), (-0.75, 1.2), (-0.85, 0.85)), S((-1.55, 1.85), (-1.0, 1.7), (-0.65, 1.3), (-0.5, 0.75))]
    u = tf(u + tail + mane, dx=-1.6, dy=-1.25, s=0.62)
    e = (e[0] * 0.62 - 1.6, e[1] * 0.62 - 1.25)

    def tower(x, w, top, roof_h):
        out = [poly((x - w / 2, -0.6), (x - w / 2, top), (x + w / 2, top), (x + w / 2, -0.6), closed=False),
               poly((x - w / 2 - 0.12, top), (x, top + roof_h), (x + w / 2 + 0.12, top)), [(x, top + roof_h), (x, top + roof_h + 0.45)],
               poly((x, top + roof_h + 0.45), (x + 0.45, top + roof_h + 0.3), (x, top + roof_h + 0.15), closed=False)]
        out.append(chain([(x - 0.13, top - 0.9)], arc(x, top - 0.6, 0.13, math.pi, 0, 8), [(x + 0.13, top - 0.9)], [(x - 0.13, top - 0.9)]))
        return out
    castle = tower(0.6, 0.7, 1.4, 1.1) + tower(2.9, 0.7, 1.3, 1.0) + tower(1.75, 0.9, 2.3, 1.4)
    walls = [poly((0.95, -0.6), (0.95, 0.6), (1.3, 0.6), (1.3, 0.8), (1.5, 0.8), (1.5, 0.6), (2.0, 0.6), (2.0, 0.8), (2.2, 0.8),
                  (2.2, 0.6), (2.55, 0.6), (2.55, -0.6), closed=False)]
    gate = [chain([(1.45, -0.6)], arc(1.75, -0.1, 0.3, math.pi, 0, 12), [(2.05, -0.6)])]
    hill = [S((-3.2, -2.9), (-1.0, -2.85), (0.2, -1.2), (1.5, -0.6), (3.4, -0.7))]
    path = [S((1.6, -0.6), (1.2, -1.4), (0.2, -2.2), (-0.2, -2.9)), S((1.9, -0.6), (1.7, -1.4), (1.1, -2.2), (1.0, -2.9))]
    rb = rainbow(1.75, 0.3, 2.9, 3.4, 2, math.radians(18), math.radians(162))
    return make("Unicorn near the Fairy-Tale Castle", u + castle + walls + gate + hill + path + rb, [eye(*e, 0.06)])


@design("unicorns_snow_globe", T)
def snow_globe(rng):
    u, e, A = unicorn_side()
    tail = tail_locks(1.75, 0.35, 0.8, -1.2)
    mane = [S((-1.85, 2.25), (-1.35, 2.05), (-1.15, 1.55), (-0.75, 1.2), (-0.85, 0.85))]
    u = tf(u + tail + mane, dx=0.0, dy=0.15, s=0.42)
    e = (e[0] * 0.42, e[1] * 0.42 + 0.15)
    globe = [chain(arc(0, 0.2, 2.4, math.radians(-58), math.radians(238), 120))]
    base = [poly((-1.3, -1.85), (-1.9, -3.0), (1.9, -3.0), (1.3, -1.85), closed=False), [(-1.65, -2.5), (1.65, -2.5)],
            S((-1.27, -1.8), (0.0, -1.95), (1.27, -1.8))]
    mound = [S((-1.9, -1.0), (-1.0, -0.85), (0.0, -0.9), (1.0, -0.85), (1.9, -1.0))]
    flakes = []
    for x, y in [(-1.4, 1.6), (1.3, 1.9), (-0.4, 2.1), (1.7, 0.8), (-1.8, 0.4), (0.8, 1.2)]:
        flakes += [[(x - 0.15, y), (x + 0.15, y)], [(x - 0.075, y - 0.13), (x + 0.075, y + 0.13)], [(x - 0.075, y + 0.13), (x + 0.075, y - 0.13)]]
    shine = [arc(0, 0.2, 2.05, math.radians(120), math.radians(160), 12)]
    return make("Unicorn inside a Snow Globe", u + globe + base + mound + flakes + shine, [eye(*e, 0.05)])


@design("unicorns_lake_reflection", T)
def lake_reflection(rng):
    u, e, A = unicorn_side()
    tail = tail_locks(1.75, 0.35, 0.8, -1.2)
    mane = [S((-1.85, 2.25), (-1.35, 2.05), (-1.15, 1.55), (-0.75, 1.2), (-0.85, 0.85)), S((-1.55, 1.85), (-1.0, 1.7), (-0.65, 1.3), (-0.5, 0.75))]
    up = tf(u + tail + mane, dy=1.25, s=0.55)
    e = (e[0] * 0.55, e[1] * 0.55 + 1.25)
    refl = [[(x, -0.4 - y) for x, y in p] for p in up]
    shore = [S((-3.2, -0.2), (-1.5, -0.2), (1.5, -0.2), (3.2, -0.2))]
    ripples = [wave(-2.6, -0.6, -1.9, 0.05, 2, 30), wave(0.4, 2.6, -1.6, 0.05, 2, 30), wave(-1.6, 1.2, -2.25, 0.05, 3, 40)]
    moon = [circle(2.4, 2.3, 0.45, 30), star(-2.6, 2.4, 0.25), star(-0.2, 2.8, 0.2)]
    reeds = [S((-3.0, -0.2), (-3.05, 0.9)), S((-2.8, -0.2), (-2.7, 0.7)), ellipse(-3.05, 1.1, 0.07, 0.25, 12)]
    return make("Unicorn Reflected in a Still Lake", up + refl + shore + ripples + moon + reeds, [eye(*e, 0.06), eye(e[0], -0.4 - e[1], 0.06)])


@design("unicorns_carousel", T)
def carousel(rng):
    u, e = leaping_unicorn()
    u = tf(u, dy=-0.2)
    e = (e[0], e[1] - 0.2)
    pole = [[(0.15, 0.6), (0.15, 3.2)], [(0.45, 0.62), (0.45, 3.2)], [(0.15, -0.55), (0.15, -2.6)], [(0.45, -0.55), (0.45, -2.6)]]
    twist = [[(0.15, y), (0.45, y + 0.25)] for y in (1.0, 1.6, 2.2, 2.8, -1.0, -1.6, -2.2)]
    top = [poly((-0.3, 3.2), (0.9, 3.2), (0.6, 3.5), (0.0, 3.5)), poly((-0.3, -2.6), (0.9, -2.6), (0.6, -2.9), (0.0, -2.9))]
    saddle = [S((-0.35, 0.35), (-0.1, 0.05), (0.6, 0.05), (0.95, 0.55)), S((-0.2, 0.3), (-0.35, 0.65), (-0.15, 0.75)),
              S((0.25, 0.05), (0.2, -0.4)), poly((0.08, -0.4), (0.38, -0.4), (0.38, -0.65), (0.08, -0.65))]
    bridle = [S((-2.05, 1.5), (-1.75, 1.15), (-1.55, 0.75)), [(-2.6, 1.3), (-2.15, 1.55)], S((-2.15, 1.55), (-1.5, 1.6))]
    blanket = [S((-0.6, 0.6), (-0.65, 0.0), (-0.45, -0.4)), S((1.3, 0.75), (1.35, 0.2), (1.15, -0.35))] + \
        [circle(x, y, 0.08, 8) for x, y in [(-0.5, -0.1), (1.25, 0.1)]]
    garland = [S((-1.45, 0.55), (-1.25, 0.25), (-0.95, 0.4), (-0.7, 0.15))]
    return make("Carousel Unicorn on a Golden Pole", u + pole + twist + top + saddle + bridle + blanket + garland, [eye(*e, 0.08)])


@design("unicorns_rocking_horse", T)
def rocking_horse(rng):
    body = C((-1.45, 2.4), (-1.8, 2.25), (-2.45, 1.6), (-2.7, 1.25), (-2.6, 1.05), (-2.3, 1.05), (-1.9, 1.3), (-1.55, 1.3),
             (-1.4, 0.7), (-1.4, 0.35), (-1.0, 0.0), (0.8, 0.0), (1.4, 0.3), (1.55, 0.8), (1.3, 1.05), (0.4, 0.95), (-0.6, 1.05),
             (-0.9, 1.5), (-1.1, 2.1))
    legs = [poly((-1.1, 0.1), (-1.9, -1.55), (-1.6, -1.6), (-0.8, 0.0), closed=False), poly((-0.5, 0.0), (-0.85, -1.75), (-0.55, -1.78), (-0.25, 0.0), closed=False),
            poly((0.5, 0.0), (0.85, -1.78), (1.15, -1.75), (0.8, 0.0), closed=False), poly((1.1, 0.15), (1.95, -1.55), (2.2, -1.45), (1.4, 0.3), closed=False)]
    rocker = [arc(0.0, 3.4, 5.2, math.radians(240), math.radians(300), 60), arc(0.0, 3.4, 5.45, math.radians(242), math.radians(298), 60)]
    rocker = [chain(arc(0.0, 3.4, 5.2, math.radians(238), math.radians(302), 60), arc(0.0, 3.4, 5.5, math.radians(302), math.radians(238), 60), [arc(0.0, 3.4, 5.2, math.radians(238), math.radians(238), 1)[0]])]
    braces = [[(-1.5, -1.95), (1.5, -1.95)]]
    saddle = [S((-0.5, 1.05), (-0.3, 0.6), (0.3, 0.6), (0.6, 1.0)), [(0.05, 0.6), (0.05, -0.2)], rect(-0.1, -0.45, 0.2, -0.2)]
    handle = [[(-1.9, 1.75), (-1.55, 1.95)], circle(-2.0, 1.72, 0.1, 10)]
    h = horn((-1.85, 2.2), (-2.5, 3.3), 0.28)
    ear = poly((-1.5, 2.35), (-1.3, 2.85), (-1.15, 2.3), closed=False)
    mane = [zigzag(-1.3, -0.7, 1.95, 0.12, 4)]
    mane = [poly((-1.25, 2.35), (-0.85, 2.2), (-1.05, 1.9), (-0.6, 1.7), (-0.85, 1.45), (-0.4, 1.25), (-0.6, 1.0), closed=False)]
    tail = [S((1.45, 0.75), (2.0, 0.9), (2.4, 0.4), (2.3, -0.2)), S((1.55, 0.6), (2.0, 0.4), (2.0, -0.2))]
    return make("Wooden Unicorn Rocking Horse", [body, ear] + legs + rocker + braces + saddle + handle + h + mane + tail, [eye(-2.0, 1.85, 0.08)])


@design("unicorns_plush_toy", T)
def plush_toy(rng):
    head = C((-1.3, 1.5), (-1.2, 2.2), (-0.6, 2.6), (0.4, 2.6), (1.05, 2.25), (1.3, 1.5), (1.1, 0.7), (0.75, 0.15), (0.0, 0.0),
             (-0.75, 0.15), (-1.1, 0.7))
    snout = S((-0.75, 0.75), (-0.3, 0.45), (0.3, 0.45), (0.75, 0.75))
    nost = [S((-0.3, 0.85), (-0.38, 0.72), (-0.28, 0.6)), S((0.3, 0.85), (0.38, 0.72), (0.28, 0.6))]
    ears = [lens((-0.95, 2.35), (-1.35, 3.15), 0.3, 12), lens((0.95, 2.35), (1.35, 3.15), 0.3, 12)]
    h = horn((0.0, 2.6), (0.0, 3.75), 0.44, 3)
    fore = [S((-0.35, 2.65), (-0.6, 2.3), (-0.45, 1.95), (-0.75, 1.75)), S((0.3, 2.62), (0.5, 2.3), (0.35, 2.0))]
    locks = [S((-1.2, 2.25), (-1.65, 1.95), (-1.55, 1.4), (-1.85, 0.95), (-1.6, 0.4)), S((-1.25, 1.6), (-1.5, 1.1), (-1.3, 0.55)),
             S((1.2, 2.25), (1.65, 1.95), (1.55, 1.4), (1.85, 0.95), (1.6, 0.4)), S((1.25, 1.6), (1.5, 1.1), (1.3, 0.55))]
    body = S((-0.8, 0.12), (-1.3, -0.6), (-1.6, -1.7), (-1.0, -2.4), (1.0, -2.4), (1.6, -1.7), (1.3, -0.6), (0.8, 0.12))
    fore_legs = [S((-0.55, -0.4), (-0.6, -1.4), (-0.55, -2.05)), S((-0.15, -0.45), (-0.1, -1.4), (-0.15, -2.05)),
                 S((0.15, -0.45), (0.1, -1.4), (0.15, -2.05)), S((0.55, -0.4), (0.6, -1.4), (0.55, -2.05))]
    hooves = [S((-0.6, -2.05), (-0.35, -2.25), (-0.1, -2.05)), S((0.1, -2.05), (0.35, -2.25), (0.6, -2.05))]
    hind = [ellipse(-1.75, -2.15, 0.45, 0.35, 30), ellipse(1.75, -2.15, 0.45, 0.35, 30), ellipse(-1.75, -2.15, 0.22, 0.17, 18),
            ellipse(1.75, -2.15, 0.22, 0.17, 18)]
    bow = [poly((0.0, -0.1), (-0.5, 0.12), (-0.5, -0.32)), poly((0.0, -0.1), (0.5, 0.12), (0.5, -0.32))]
    tail = [S((1.4, -1.0), (2.1, -0.6), (2.5, -1.0), (2.2, -1.5)), S((1.55, -1.3), (2.0, -1.2), (2.3, -1.6))]
    sm = [S((-0.25, 0.25), (0.0, 0.15), (0.25, 0.25))]
    return make("Cuddly Unicorn Plush Toy", [head, snout, body] + nost + ears + h + fore + locks + fore_legs + hooves + hind + bow + tail + sm,
                [eye(-0.55, 1.45, 0.13), eye(0.55, 1.45, 0.13)])


@design("unicorns_horn_closeup", T)
def horn_closeup(rng):
    h = horn((0.0, -1.2), (0.0, 3.4), 1.6, 7)
    base = [S((-1.2, -1.2), (-0.6, -1.45), (0.0, -1.5), (0.6, -1.45), (1.2, -1.2))]
    flowers = []
    for x, y, r in [(-1.6, -1.5, 0.55), (1.6, -1.5, 0.55), (0.0, -2.1, 0.6)]:
        flowers.append(circle(x, y, r * 0.3, 16))
        for k in range(6):
            a = k * TAU / 6 + 0.25
            flowers.append(lens((x + r * 0.32 * math.cos(a), y + r * 0.32 * math.sin(a)), (x + r * math.cos(a), y + r * math.sin(a)), 0.42, 10))
    leaves = [lens((-2.2, -1.2), (-3.0, -0.8), 0.4, 12), lens((2.2, -1.2), (3.0, -0.8), 0.4, 12), lens((-0.9, -2.4), (-1.6, -2.9), 0.4, 10),
              lens((0.9, -2.4), (1.6, -2.9), 0.4, 10)]
    sparks = [sparkle(-1.8, 2.6, 0.45), sparkle(1.7, 1.6, 0.4), sparkle(-1.3, 0.8, 0.3), star(1.4, 3.2, 0.3), sparkle(2.4, -0.1, 0.3)]
    return make("Spiral Unicorn Horn with Sparkles", h + base + flowers + leaves + sparks)


@design("unicorns_constellation", T)
def constellation(rng):
    pts = [(0.2, 1.9), (0.55, 2.8), (0.8, 1.8), (1.8, 0.1), (2.4, -2.6), (0.6, -2.6), (0.4, -0.6), (-0.5, -0.7), (-1.6, -1.2),
           (-2.15, -1.0), (-2.2, -0.55), (-1.2, 0.8), (-0.5, 1.6)]
    line = poly(*pts, closed=True)
    hornl = [[(-0.5, 1.6), (-1.9, 3.3), (0.2, 1.9)]]
    allp = pts + [(-1.9, 3.3)]
    stars_ = [star(x, y, 0.3 if k % 3 == 0 else 0.22, 5, 0.45) for k, (x, y) in enumerate(allp)]
    extra = [star(-2.6, 1.8, 0.15), star(2.6, 2.6, 0.18), star(-2.7, 0.4, 0.12), star(2.8, 1.0, 0.14), circle(1.6, 2.9, 0.06, 8),
             circle(-2.2, -2.6, 0.06, 8), circle(-0.4, -2.4, 0.06, 8)]
    eye_star = [star(-0.55, 0.65, 0.2, 4, 0.4)]
    mane = [S((1.0, 1.6), (1.9, 1.5), (2.5, 0.7)), S((1.6, 0.4), (2.4, 0.0), (2.8, -0.9))]
    return make("Unicorn Star Constellation", [line] + hornl + stars_ + extra + eye_star + mane)


@design("unicorns_sea_unicorn", T)
def sea_unicorn(rng):
    body = C((-1.3, 2.4), (-1.65, 2.25), (-2.15, 1.65), (-2.4, 1.35), (-2.3, 1.18), (-2.05, 1.18), (-1.6, 1.4), (-1.3, 1.45),
             (-1.2, 0.9), (-1.35, 0.3), (-1.8, 0.05), (-2.25, -0.15), (-2.5, -0.4, 1), (-2.15, -0.55, 1), (-1.85, -0.4),
             (-1.4, -0.4), (-0.8, -0.75), (0.0, -1.3), (1.0, -1.55), (1.8, -1.3), (2.3, -0.7), (2.45, 0.0), (2.4, 0.5, 1),
             (3.0, 1.45, 1), (2.6, 1.35), (2.25, 1.15, 1), (1.95, 1.4), (1.55, 1.55, 1), (2.05, 0.5, 1), (1.9, -0.2), (1.5, -0.7),
             (0.9, -0.85), (0.3, -0.5), (-0.1, 0.3), (-0.5, 1.2), (-0.8, 1.8))
    fins = [S((-0.15, 0.1), (0.35, 0.55), (0.7, 0.35), (0.3, -0.3)), S((0.5, -1.4), (0.75, -2.0), (1.2, -1.95), (1.1, -1.55))]
    scales = [arc(x, y, 0.25, math.pi * 1.1, math.pi * 1.9, 8) for x, y in [(-0.6, -0.2), (0.0, -0.6), (0.6, -0.85), (1.2, -0.95),
                                                                            (1.7, -0.75), (-0.2, 0.25)]]
    h = horn((-1.55, 2.3), (-1.95, 3.45), 0.26)
    ear = poly((-1.3, 2.4), (-1.05, 2.8), (-0.95, 2.3), closed=False)
    mane = [S((-1.15, 2.45), (-0.55, 2.2), (-0.45, 1.6), (0.05, 1.3), (0.0, 0.8)), S((-0.95, 2.0), (-0.45, 1.75), (-0.35, 1.2))]
    waves = [S((-3.0, -1.9), (-2.4, -1.6), (-1.8, -1.9), (-1.2, -1.6), (-0.6, -1.9)), S((1.0, -2.3), (1.6, -2.0), (2.2, -2.3), (2.8, -2.0)),
             S((-2.4, -2.7), (-1.6, -2.4), (-0.8, -2.7), (0.0, -2.4), (0.8, -2.7))]
    bubbles = [circle(x, y, r, 14) for x, y, r in [(-2.7, 0.8, 0.15), (-2.9, 1.3, 0.1), (2.7, 2.4, 0.15), (2.4, 2.9, 0.1)]]
    return make("Sea Unicorn with a Fish Tail", [body, ear] + fins + scales + h + mane + waves + bubbles, [eye(-1.65, 1.85, 0.08)])


@design("unicorns_garden_enclosure", T)
def garden_enclosure(rng):
    u, e = lying_unicorn()
    u = tf(flip(u), dy=-0.75, s=0.62)
    e = (-e[0] * 0.62, e[1] * 0.62 - 0.75)
    posts = []
    for k in range(13):
        a = math.pi + math.pi * k / 12
        x, y = 2.9 * math.cos(a), -1.0 + 0.9 * math.sin(a)
        posts.append(poly((x - 0.08, y), (x - 0.08, y + 0.75), (x, y + 0.85), (x + 0.08, y + 0.75), (x + 0.08, y), closed=False))
    rails = [[(2.9 * math.cos(math.pi + math.pi * i / 60), -1.0 + 0.9 * math.sin(math.pi + math.pi * i / 60) + dy) for i in range(61)]
             for dy in (0.25, 0.55)]
    trunk = [S((-2.35, -0.25), (-2.3, 0.6), (-2.5, 1.4)), S((-1.85, -0.25), (-1.9, 0.6), (-1.7, 1.4))]
    crown = [polar(lambda t: 1.15 + 0.13 * math.sin(7 * t), cx=-2.1, cy=2.3, n=160)]
    fruit = [circle(x, y, 0.13, 12) for x, y in [(-2.6, 2.4), (-1.8, 2.8), (-1.5, 2.0), (-2.3, 1.8)]]
    flowers = [star(x, y, 0.2, 6, 0.5) for x, y in [(-2.6, -2.5), (2.5, -2.5), (-1.0, -2.75), (1.0, -2.75), (2.6, 1.6), (0.8, 2.4)]]
    return make("Unicorn in the Enchanted Garden Enclosure", u + posts + rails + trunk + crown + fruit + flowers, [eye(*e, 0.06)])


def swan_neck_head():
    """Unicorn head and arched neck facing right."""
    out = S((-1.6, -2.6), (-1.1, -0.9), (-1.0, 0.6), (-0.6, 1.7), (0.1, 2.25), (0.75, 2.1), (1.2, 1.5), (1.45, 1.15), (1.35, 0.98),
            (1.05, 1.02), (0.7, 1.15), (0.45, 1.1), (0.2, 0.7), (0.1, -0.3), (0.3, -1.5), (0.65, -2.6))
    h = horn((0.55, 2.1), (1.65, 3.05), 0.26)
    ear = poly((0.15, 2.22), (0.05, 2.7), (-0.2, 2.15), closed=False)
    mane = [S((-0.2, 2.15), (-0.75, 1.9), (-1.0, 1.3), (-1.55, 0.9), (-1.45, 0.2)), S((-0.6, 1.65), (-1.3, 1.3), (-1.4, 0.6), (-1.85, 0.1)),
            S((-1.0, 0.2), (-1.5, -0.4), (-1.4, -1.0))]
    return [out] + h + [ear] + mane, (0.62, 1.62)


@design("unicorns_heart_pair", T)
def heart_pair(rng):
    a, e = swan_neck_head()
    left = tf(a, dx=-1.55, s=0.95)
    right = [mirror_x(p) for p in left]
    e1 = (e[0] * 0.95 - 1.55, e[1] * 0.95)
    hearts = [heart(0.0, 0.0, 0.55), heart(0.0, 3.4, 0.3), heart(-0.55, -1.7, 0.22), heart(0.6, -2.2, 0.18)]
    return make("Two Unicorns Forming a Heart", left + right + hearts, [eye(*e1, 0.08), eye(-e1[0], e1[1], 0.08)])


@design("unicorns_headband", T)
def headband(rng):
    band = [arc(0, -1.2, 2.8, math.radians(10), math.radians(170), 80), arc(0, -1.2, 2.45, math.radians(8), math.radians(172), 80)]
    ends = [[transform([(2.8, 0)], rot=math.radians(10))[0], transform([(2.45, 0)], rot=math.radians(8))[0]]]
    ends = [[(2.8 * math.cos(math.radians(10)), -1.2 + 2.8 * math.sin(math.radians(10))), (2.45 * math.cos(math.radians(8)), -1.2 + 2.45 * math.sin(math.radians(8)))],
            [(-2.8 * math.cos(math.radians(10)), -1.2 + 2.8 * math.sin(math.radians(10))), (-2.45 * math.cos(math.radians(8)), -1.2 + 2.45 * math.sin(math.radians(8)))]]
    h = horn((0.0, 1.5), (0.0, 3.9), 0.75, 5)
    ears = [lens((-1.25, 1.1), (-1.9, 2.5), 0.32, 16), lens((-1.3, 1.25), (-1.8, 2.2), 0.18, 10),
            lens((1.25, 1.1), (1.9, 2.5), 0.32, 16), lens((1.3, 1.25), (1.8, 2.2), 0.18, 10)]
    flowers = []
    for x, y, r in [(-0.75, 1.65, 0.38), (0.75, 1.65, 0.38), (-2.05, 0.75, 0.32), (2.05, 0.75, 0.32)]:
        flowers.append(circle(x, y, r * 0.32, 14))
        for k in range(5):
            a = k * TAU / 5 + 0.5
            flowers.append(lens((x + r * 0.34 * math.cos(a), y + r * 0.34 * math.sin(a)), (x + r * math.cos(a), y + r * math.sin(a)), 0.45, 8))
    leaves = [lens((-0.3, 1.25), (-0.75, 0.95), 0.4, 8), lens((0.3, 1.25), (0.75, 0.95), 0.4, 8)]
    ribbons = [S((-2.6, -0.65), (-2.9, -1.4), (-2.5, -2.1), (-2.8, -2.8)), S((-2.4, -0.7), (-2.4, -1.5), (-2.05, -2.2), (-2.2, -2.8)),
               S((2.6, -0.65), (2.9, -1.4), (2.5, -2.1), (2.8, -2.8)), S((2.4, -0.7), (2.4, -1.5), (2.05, -2.2), (2.2, -2.8))]
    return make("Unicorn Costume Headband", band + ends + h + ears + flowers + leaves + ribbons)


@design("unicorns_fairy_rider", T)
def fairy_rider(rng):
    u, e = galloping_unicorn()
    fe = (0.4 + 1.35 * (0.05 - 0.1), 0.45 + 1.35 * (1.98 - 0.55))
    head = circle(0.15, 1.95, 0.3, 24)
    hair = [S((-0.15, 2.05), (-0.45, 1.85), (-0.7, 1.9), (-0.95, 1.65)), S((0.0, 2.25), (-0.45, 2.15), (-0.8, 2.2))]
    torso = S((0.0, 1.65), (-0.1, 1.2), (0.0, 0.55))
    torso = poly((-0.05, 1.65), (-0.25, 0.55), (0.45, 0.55), (0.3, 1.65), closed=False)
    arm = [S((0.0, 1.45), (-0.45, 1.15), (-0.75, 1.2))]
    leg_ = [S((0.0, 0.55), (-0.35, 0.15), (-0.25, -0.35))]
    wings = [lens((0.25, 1.4), (1.3, 2.6), 0.32, 18), lens((0.25, 1.3), (1.35, 0.95), 0.3, 14)]
    crown = [zigzag(-0.05, 0.35, 2.3, 0.08, 2)]
    sparks = [sparkle(-2.4, 3.2, 0.3), sparkle(2.6, 2.4, 0.35), star(1.5, 3.6, 0.25)]
    ground = [S((-1.5, -2.4), (0.0, -2.45), (1.5, -2.4))]
    fairy = [transform(p, dx=0.4 - 0.1 * 1.35, dy=0.45 - 0.55 * 1.35, s=1.35) for p in [head, torso] + hair + arm + leg_ + wings]
    return make("Fairy Riding a Unicorn", u + fairy + sparks + ground, [eye(*e, 0.08), eye(*fe, 0.06)])


@design("unicorns_teacup", T)
def teacup(rng):
    cup = S((-2.2, 0.0), (-2.0, -1.4), (-1.2, -2.2), (1.2, -2.2), (2.0, -1.4), (2.2, 0.0))
    rim = ellipse(0, 0.0, 2.2, 0.4, 80)
    handle = S((2.05, -0.4), (2.9, -0.2), (2.9, -1.0), (1.7, -1.5))
    saucer = [ellipse(0, -2.35, 3.0, 0.45, 80), ellipse(0, -2.3, 1.3, 0.2, 40)]
    head = S((-0.9, -0.1), (-1.1, 0.7), (-1.0, 1.4), (-0.4, 1.85), (0.4, 1.85), (1.0, 1.4), (1.1, 0.7), (0.9, -0.1))
    snout = S((-0.35, 0.05), (0.0, -0.05), (0.35, 0.05))
    nost = [S((-0.3, 0.45), (-0.38, 0.32), (-0.3, 0.2)), S((0.3, 0.45), (0.38, 0.32), (0.3, 0.2))]
    ears = [lens((-0.8, 1.6), (-1.2, 2.4), 0.3, 12), lens((0.8, 1.6), (1.2, 2.4), 0.3, 12)]
    h = horn((0.0, 1.85), (0.0, 2.95), 0.4, 3)
    fore = [S((-0.3, 1.9), (-0.65, 1.55), (-0.5, 1.15), (-0.8, 0.95)), S((0.25, 1.88), (0.55, 1.5), (0.4, 1.2)),
            S((1.0, 1.4), (1.5, 1.0), (1.35, 0.5), (1.6, 0.1)), S((-1.0, 1.4), (-1.5, 1.0), (-1.35, 0.5), (-1.6, 0.1))]
    hooves = []
    lashes = [[(-0.85, 1.15), (-1.05, 1.3)], [(0.85, 1.15), (1.05, 1.3)]]
    dec = [heart(0.0, -1.2, 0.35), heart(-1.25, -1.0, 0.22), heart(1.25, -1.0, 0.22)]
    steam = [sparkle(-2.4, 1.6, 0.3), sparkle(2.4, 1.9, 0.3)]
    return make("Tiny Unicorn in a Teacup", [cup, rim, handle, head, snout] + saucer + nost + ears + h + fore + hooves + lashes + dec + steam,
                [eye(-0.55, 1.05, 0.12), eye(0.55, 1.05, 0.12)])


@design("unicorns_forest_trot", T)
def forest_trot(rng):
    u, e, A = unicorn_side(fore="lift")
    tail = tail_locks(1.75, 0.35, 0.8, -1.2)
    mane = [S((-1.85, 2.25), (-1.35, 2.05), (-1.15, 1.55), (-0.75, 1.2), (-0.85, 0.85)), S((-1.55, 1.85), (-1.0, 1.7), (-0.65, 1.3), (-0.5, 0.75))]
    u = tf(u + tail + mane, dx=0.2, dy=-0.9, s=0.62)
    e = (e[0] * 0.62 + 0.2, e[1] * 0.62 - 0.9)

    def pine(x, base, w, h):
        out = [[(x - 0.12, base), (x - 0.12, base + 0.4)], [(x + 0.12, base), (x + 0.12, base + 0.4)]]
        tiers = 3
        pts = [(x - 0.12, base + 0.4)]
        for k in range(tiers):
            y0 = base + 0.4 + k * h / tiers * 0.9
            ww = w * (1 - k / tiers * 0.7)
            pts += [(x - ww / 2, y0), (x - ww / 4, y0 + h / tiers * 0.85)]
        right = [(2 * x - px, py) for px, py in pts[::-1]]
        out.append(chain(pts, [(x, base + 0.4 + h)], right))
        return out
    trees = pine(-2.7, -2.5, 1.5, 4.2) + pine(2.75, -2.5, 1.4, 4.0) + pine(1.55, -1.0, 0.9, 2.4) + pine(-1.6, -0.9, 0.9, 2.2)
    shrooms = mushroom(-1.8, -2.55, 0.6, 0.4, 0.18, False) + mushroom(2.0, -2.55, 0.5, 0.32, 0.15, False)
    flies = [circle(x, y, 0.07, 8) for x, y in [(-0.5, 1.6), (0.9, 2.3), (0.2, 3.0), (-2.0, 2.6)]]
    ground = [S((-3.4, -2.55), (0.0, -2.48), (3.4, -2.55))]
    return make("Unicorn Trotting through an Enchanted Forest", u + trees + shrooms + flies + ground, [eye(*e, 0.06)])


@design("unicorns_cloud_nap", T)
def cloud_nap(rng):
    cl = cloud(0.0, -1.45, 6.0, 2.0)
    body = S((-0.6, -0.55), (-0.2, 0.35), (0.8, 0.6), (1.8, 0.35), (2.2, -0.3), (2.0, -0.6))
    head = C((-0.5, 0.55), (-0.35, 1.15), (-0.75, 1.4), (-1.5, 1.2), (-2.05, 0.6), (-2.35, 0.1), (-2.2, -0.2), (-1.7, -0.2),
             (-1.1, -0.05), (-0.7, -0.15))
    closed_eye = [arc(-1.05, 0.62, 0.18, math.pi + 0.3, TAU - 0.3, 8), [(-1.1, 0.45), (-1.18, 0.33)], [(-0.95, 0.45), (-0.9, 0.33)]]
    nost = [arc(-2.05, 0.05, 0.08, 0.3, math.pi, 6)]
    ear = lens((-0.55, 1.25), (-0.15, 1.8), 0.3, 12)
    h = horn((-1.2, 1.3), (-1.5, 2.4), 0.26, 3)
    legs = [S((-0.4, -0.6), (-0.9, -0.5), (-1.35, -0.6)), ellipse(-1.5, -0.62, 0.17, 0.12, 12), S((1.5, -0.55), (0.9, -0.55), (0.6, -0.65)),
            ellipse(0.45, -0.66, 0.17, 0.12, 12)]
    mane = [S((-0.4, 1.3), (0.1, 1.0), (0.05, 0.6), (0.45, 0.4)), S((-0.15, 1.45), (0.45, 1.15), (0.55, 0.75))]
    tail = [S((2.1, -0.2), (2.7, 0.1), (2.9, -0.35)), S((2.15, -0.4), (2.55, -0.4))]
    zs = [poly((-2.4, 1.9), (-2.0, 1.9), (-2.4, 1.5), (-2.0, 1.5), closed=False), poly((-2.9, 2.6), (-2.6, 2.6), (-2.9, 2.3), (-2.6, 2.3), closed=False)]
    moon = [chain(arc(2.2, 2.3, 0.65, math.radians(60), math.radians(300), 30), S((2.525, 1.737), (2.2, 2.3), (2.525, 2.863)))]
    stars_ = [star(0.6, 2.6, 0.25), star(-1.2, 3.0, 0.2), star(2.9, 1.0, 0.18)]
    return make("Unicorn Napping on a Cloud", [cl, body, head, ear] + closed_eye + nost + h + legs + mane + tail + zs + moon + stars_)


@design("unicorns_cloud_castle", T)
def cloud_castle(rng):
    base = [cloud(0.0, -1.7, 6.2, 1.8), cloud(-2.3, -2.4, 2.0, 0.8)]

    def tower(x, w, y0, top, roof_h):
        return [poly((x - w / 2, y0), (x - w / 2, top), (x + w / 2, top), (x + w / 2, y0), closed=False),
                poly((x - w / 2 - 0.12, top), (x, top + roof_h), (x + w / 2 + 0.12, top)),
                star(x, top + roof_h + 0.25, 0.2),
                chain([(x - 0.12, top - 0.75)], arc(x, top - 0.45, 0.12, math.pi, 0, 8), [(x + 0.12, top - 0.75)], [(x - 0.12, top - 0.75)])]
    castle = tower(0.0, 1.0, -0.95, 1.6, 1.3) + tower(-1.6, 0.7, -1.0, 0.7, 1.0) + tower(1.6, 0.7, -1.0, 0.7, 1.0)
    walls = [poly((-1.25, -1.0), (-1.25, 0.0), (-0.5, 0.0), closed=False), poly((1.25, -1.0), (1.25, 0.0), (0.5, 0.0), closed=False)]
    door = [chain([(-0.3, -0.95)], arc(0.0, -0.45, 0.3, math.pi, 0, 14), [(0.3, -0.95)])]
    bows = rainbow(0.0, -0.9, 2.5, 3.0, 2, math.radians(15), math.radians(165))
    stars_ = [sparkle(-2.8, 2.6, 0.35), sparkle(2.8, 2.5, 0.3), star(-2.9, 0.8, 0.2), star(2.9, 0.9, 0.22)]
    return make("Castle in the Clouds", base + castle + walls + door + bows + stars_)


@design("unicorns_pixie_jar", T)
def pixie_jar(rng):
    jar = S((-1.2, 1.7), (-1.3, 1.4), (-1.9, 0.9), (-2.0, -0.5), (-1.9, -2.2), (-1.5, -2.6), (1.5, -2.6), (1.9, -2.2), (2.0, -0.5),
            (1.9, 0.9), (1.3, 1.4), (1.2, 1.7))
    lid = [rrect(-1.45, 1.7, 1.45, 2.25, 0.12), [(-1.45, 1.98), (1.45, 1.98)]]
    cloth = [S((-1.3, 2.25), (-0.8, 2.75), (0.0, 2.6), (0.8, 2.85), (1.3, 2.25))]
    label = [rrect(-1.1, -1.6, 1.1, -0.6, 0.2), heart(0.0, -1.1, 0.28)]
    inside = [star(-0.9, 0.5, 0.35), sparkle(0.6, 0.9, 0.35), star(0.9, -0.1, 0.25), sparkle(-0.6, -0.2, 0.25), circle(0.0, 0.3, 0.1, 10),
              circle(1.3, 0.4, 0.08, 8), circle(-1.4, -1.9, 0.08, 8), circle(1.2, -2.0, 0.1, 10), star(0.0, -2.1, 0.25)]
    out = [sparkle(-2.6, 2.0, 0.35), sparkle(2.6, 1.6, 0.3), star(2.4, 3.0, 0.2), star(-2.4, -1.2, 0.2)]
    shine = [S((1.55, 0.3), (1.6, -0.5), (1.5, -1.3))]
    return make("Jar of Pixie Dust", [jar] + lid + cloth + label + inside + out + shine)


@design("unicorns_floating_island", T)
def floating_island(rng):
    top = S((-2.8, 0.0), (-1.5, 0.2), (0.0, 0.1), (1.5, 0.25), (2.8, 0.0))
    rock = S((-2.8, 0.0), (-2.3, -0.8), (-1.6, -1.2), (-1.0, -2.0), (-0.3, -2.3), (0.2, -2.9), (0.6, -2.2), (1.3, -1.7),
             (1.9, -1.0), (2.5, -0.6), (2.8, 0.0))
    cracks = [S((-1.5, -0.4), (-1.1, -0.9), (-1.2, -1.3)), S((0.8, -0.5), (0.5, -1.1), (0.7, -1.6)), S((-0.2, -1.2), (0.1, -1.8))]
    roots = [S((-1.9, -0.9), (-2.1, -1.5), (-1.9, -2.0)), S((1.6, -1.3), (1.9, -1.9))]
    house = [poly((0.6, 0.2), (0.6, 1.2), (2.0, 1.2), (2.0, 0.25), closed=False), poly((0.4, 1.15), (1.3, 2.0), (2.2, 1.15)),
             rect(1.15, 0.22, 1.5, 0.8), circle(1.75, 0.85, 0.15, 12)]
    tree = [S((-1.3, 0.15), (-1.35, 1.1)), S((-1.0, 0.15), (-0.95, 1.1)), polar(lambda t: 0.85 + 0.1 * math.sin(6 * t), cx=-1.15, cy=1.85, n=120)]
    falls = [S((2.3, -0.1), (2.45, -1.0), (2.4, -2.0)), S((2.6, -0.05), (2.75, -1.0), (2.7, -1.8))]
    birds = [S((-2.6, 2.6), (-2.4, 2.75), (-2.2, 2.6), (-2.0, 2.75), (-1.8, 2.6)), S((0.0, 2.8), (0.15, 2.92), (0.3, 2.8), (0.45, 2.92), (0.6, 2.8))]
    clouds = [cloud(-2.3, -2.4, 1.6, 0.6), cloud(2.4, 2.6, 1.4, 0.55)]
    return make("Floating Sky Island", [top, rock] + cracks + roots + house + tree + falls + birds + clouds)


@design("unicorns_moonflower", T)
def moonflower(rng):
    petals = []
    for k in range(7):
        a = math.pi / 2 + k * TAU / 7
        petals.append(lens((0.5 * math.cos(a), 0.9 + 0.5 * math.sin(a)), (1.9 * math.cos(a), 0.9 + 1.9 * math.sin(a)), 0.32, 16))
        petals.append([(0.6 * math.cos(a), 0.9 + 0.6 * math.sin(a)), (1.5 * math.cos(a), 0.9 + 1.5 * math.sin(a))])
    centre = [circle(0.0, 0.9, 0.45, 30), star(0.0, 0.9, 0.3, 5, 0.5)]
    stem = [S((0.0, -1.0), (0.2, -2.0), (-0.1, -3.0))]
    leaves = [lens((0.1, -1.9), (1.6, -1.4), 0.35, 16), lens((0.05, -2.4), (-1.5, -2.1), 0.35, 16)]
    glow = [sparkle(-2.4, 2.4, 0.35), sparkle(2.4, 2.5, 0.3), sparkle(2.3, -0.8, 0.3), sparkle(-2.3, -0.6, 0.25),
            circle(-1.6, 3.0, 0.08, 8), circle(1.5, 3.1, 0.08, 8)]
    moon = [chain(arc(-2.4, -2.2, 0.55, math.radians(60), math.radians(300), 30), S((-2.125, -2.676), (-2.35, -2.2), (-2.125, -1.724)))]
    return make("Glowing Enchanted Moonflower", petals + centre + stem + leaves + glow + moon)


@design("unicorns_stained_glass", T)
def stained_glass(rng):
    a, e = swan_neck_head()
    a = tf(a, dx=-0.2, dy=-0.25, s=0.85)
    e = (e[0] * 0.85 - 0.2, e[1] * 0.85 - 0.25)
    frame = [chain([(-2.4, -2.9)], [(-2.4, 1.2)], arc(0, 1.2, 2.4, math.pi, 0, 50), [(2.4, -2.9)], [(-2.4, -2.9)]),
             chain([(-2.1, -2.6)], [(-2.1, 1.2)], arc(0, 1.2, 2.1, math.pi, 0, 50), [(2.1, -2.6)], [(-2.1, -2.6)])]
    lead = [[(-2.1, 0.4), (-1.35, 0.6)], [(-2.1, -1.2), (-1.5, -1.0)], [(0.55, -0.6), (2.1, -0.2)], [(0.6, -1.8), (2.1, -1.6)],
            [(1.4, 2.5), (1.55, 3.05)], [(-1.2, 2.4), (-1.5, 2.95)], [(1.5, 1.8), (2.1, 1.4)]]
    sun = [arc(1.6, 2.4, 0.4, math.radians(200), math.radians(520), 20)]
    sill = [rect(-2.7, -3.2, 2.7, -2.9)]
    return make("Stained-Glass Unicorn Window", a + frame + lead + sill, [eye(*e, 0.07)])
