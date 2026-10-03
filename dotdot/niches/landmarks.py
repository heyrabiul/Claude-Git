"""World Landmarks niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "landmarks"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ---------------------------------------------------------------- helpers

def ground(x0=-3.3, x1=3.3, y=-3.0):
    return [(x0, y), (x1, y)]


def arch(x0, x1, y0, y1, closed=False, n=12):
    """Round-topped opening rising from (x0, y0) over to (x1, y0)."""
    r = (x1 - x0) / 2
    pts = chain([(x0, y0)], arc(x0 + r, y1 - r, r, math.pi, 0, n), [(x1, y0)])
    return pts + [pts[0]] if closed else pts


def gothic(x0, x1, y0, y1, closed=False, n=8):
    """Pointed (gothic) arch opening."""
    w = x1 - x0
    ys = y1 - 0.866 * w
    pts = chain([(x0, y0)], arc(x1, ys, w, math.pi, 2 * math.pi / 3, n), arc(x0, ys, w, math.pi / 3, 0, n), [(x1, y0)])
    return pts + [pts[0]] if closed else pts


def onion(cx, y0, hw, h, bulge=1.3):
    """Onion dome from (cx-hw, y0) over the tip (cx, y0+h) to (cx+hw, y0)."""
    left = chain(cubic((cx - hw, y0), (cx - hw * bulge, y0 + 0.12 * h), (cx - hw * bulge, y0 + 0.45 * h), (cx - hw * 0.55, y0 + 0.66 * h), 14),
                 cubic((cx - hw * 0.55, y0 + 0.66 * h), (cx - hw * 0.15, y0 + 0.8 * h), (cx - 0.02, y0 + 0.9 * h), (cx, y0 + h), 10))
    return chain(left, mirror_x(left, cx)[::-1])


def dome(cx, y0, r, n=30):
    return arc(cx, y0, r, math.pi, 0, n)


def merlons(x0, x1, y, h, n):
    """Battlement top line from (x0, y+h) to (x1, ...) with n merlons."""
    w = (x1 - x0) / (2 * n - 1)
    pts = []
    for k in range(2 * n - 1):
        yy = y + h if k % 2 == 0 else y
        pts += [(x0 + k * w, yy), (x0 + (k + 1) * w, yy)]
    return pts


def tree(cx, y0, s=1.0):
    """Round deciduous tree."""
    top = chain([(cx - 0.08 * s, y0), (cx - 0.08 * s, y0 + 0.5 * s)],
                arc(cx - 0.3 * s, y0 + 0.75 * s, 0.3 * s, -1.3, 2.4, 10), arc(cx, y0 + 1.1 * s, 0.35 * s, 2.0, 0.6, 10),
                arc(cx + 0.3 * s, y0 + 0.75 * s, 0.3 * s, 0.9, -1.8, 10), [(cx + 0.08 * s, y0 + 0.5 * s), (cx + 0.08 * s, y0)])
    return top


def cypress(cx, y0, h, w=0.35):
    return lens((cx, y0), (cx, y0 + h), w / h)


def cloud(cx, cy, s=1.0):
    return chain([(cx - 0.9 * s, cy)], arc(cx - 0.5 * s, cy, 0.4 * s, math.pi, 0.3, 10), arc(cx + 0.05 * s, cy + 0.15 * s, 0.45 * s, 2.6, 0.2, 10),
                 arc(cx + 0.55 * s, cy, 0.35 * s, 1.6, 0, 8), [(cx - 0.9 * s, cy)])


def waves(x0, x1, ys, amp=0.06, per=1.0):
    return [wave(x0 + 0.2 * k, x1 - 0.2 * k, y, amp, (x1 - x0) / per, 80) for k, y in enumerate(ys)]


def windows(x0, x1, y0, y1, nx, ny, fw=0.5, fh=0.55):
    out = []
    cw, ch = (x1 - x0) / nx, (y1 - y0) / ny
    for i in range(nx):
        for j in range(ny):
            cx, cy = x0 + cw * (i + 0.5), y0 + ch * (j + 0.5)
            out.append(rect(cx - cw * fw / 2, cy - ch * fh / 2, cx + cw * fw / 2, cy + ch * fh / 2))
    return out


# ---------------------------------------------------------------- Europe

@design("landmarks_eiffel_tower", T)
def eiffel_tower(rng):
    s1 = cubic((-2.4, -3.0), (-1.7, -2.1), (-1.3, -1.4), (-1.15, -0.9), 16)
    archl = cubic((-1.45, -3.0), (-1.2, -1.55), (1.2, -1.55), (1.45, -3.0), 30)
    lat1 = [s1[3], archl[3], s1[7], archl[7], s1[11], archl[10]]
    sec2 = cubic((-1.0, -0.6), (-0.8, 0.0), (-0.65, 0.5), (-0.58, 0.95), 12)
    sec3 = cubic((-0.45, 1.15), (-0.3, 1.8), (-0.18, 2.3), (-0.13, 2.7), 14)

    def hw(y):
        return 0.45 + (0.13 - 0.45) * (y - 1.15) / 1.55
    zig = [((-1) ** k * (hw(1.2 + 0.3 * k) - 0.05), 1.2 + 0.3 * k) for k in range(6)]
    parts = [s1, mirror_x(s1), archl, lat1, mirror_x(lat1), sec2, mirror_x(sec2), sec3, mirror_x(sec3), zig,
             rect(-1.6, -0.9, 1.6, -0.6), [(-1.6, -0.75), (1.6, -0.75)],
             [(-0.95, -0.6), (0.0, 0.2), (0.95, -0.6)], [(-0.6, 0.95), (0.0, 0.2), (0.6, 0.95)],
             rect(-0.8, 0.95, 0.8, 1.15), rect(-0.24, 2.7, 0.24, 2.95),
             chain(arc(0, 2.95, 0.16, 0, math.pi, 8)), [(0, 3.11), (0, 3.7)], ground(-3.2, 3.2),
             tree(-3.0, -3.0, 0.9), tree(3.0, -3.0, 0.9)]
    return make("The Eiffel Tower, Paris", parts)


@design("landmarks_big_ben", T)
def big_ben(rng):
    cx = -1.5
    shaft = [[(cx - 0.6, -3.0), (cx - 0.6, 0.8)], [(cx + 0.6, -3.0), (cx + 0.6, 0.8)]]
    panels = [[(cx + dx, -2.6), (cx + dx, 0.6)] for dx in (-0.2, 0.2)]
    wins = [gothic(cx - 0.5, cx - 0.3, yy, yy + 0.45, True) for yy in (-2.2, -1.2, -0.2)] + \
           [gothic(cx + 0.3, cx + 0.5, yy, yy + 0.45, True) for yy in (-2.2, -1.2, -0.2)]
    stage = rect(cx - 0.85, 0.8, cx + 0.85, 2.5)
    face = [circle(cx, 1.65, 0.72, 60), circle(cx, 1.65, 0.55, 48)]
    ticks = [[(cx + 0.55 * math.cos(a), 1.65 + 0.55 * math.sin(a)), (cx + 0.72 * math.cos(a), 1.65 + 0.72 * math.sin(a))]
             for a in [k * TAU / 12 for k in range(12)]]
    hands = [[(cx, 1.65), (cx, 2.05)], [(cx, 1.65), (cx + 0.3, 1.5)]]
    belfry = [rect(cx - 0.7, 2.5, cx + 0.7, 3.1)] + [gothic(cx + dx - 0.15, cx + dx + 0.15, 2.6, 3.0) for dx in (-0.4, 0.0, 0.4)]
    roof = [poly((cx - 0.75, 3.1), (cx - 0.35, 3.9), (cx + 0.35, 3.9), (cx + 0.75, 3.1), closed=False), rect(cx - 0.35, 3.9, cx + 0.35, 4.15),
            poly((cx - 0.35, 4.15), (cx, 4.9), (cx + 0.35, 4.15), closed=False), [(cx, 4.9), (cx, 5.3)], [(cx - 0.15, 5.15), (cx + 0.15, 5.15)]]
    pins = [poly((cx + s * 0.85, 2.5), (cx + s * 0.95, 3.2), (cx + s * 0.75, 2.5), closed=False) for s in (-1, 1)]
    hall = chain([(cx + 0.6, -1.2)], merlons(cx + 0.6, 2.2, -1.2, 0.2, 8), [(2.2, -1.2)])
    hall_side = [[(2.2, -1.2), (2.2, -3.0)]]
    hall_wins = [gothic(x, x + 0.25, -2.6, -2.0, True) for x in (-0.6, -0.1, 0.4, 0.9, 1.4, 1.85)] + \
                [gothic(x, x + 0.25, -1.85, -1.4, True) for x in (-0.6, -0.1, 0.4, 0.9, 1.4, 1.85)]
    tower2 = [poly((2.2, -3.0), (2.2, 0.3), (2.6, 1.3), (3.0, 0.3), (3.0, -3.0), closed=False), [(2.2, 0.3), (3.0, 0.3)],
              gothic(2.45, 2.75, -0.8, 0.0, True), gothic(2.45, 2.75, -2.2, -1.4, True)]
    return make("Big Ben, London", shaft + panels + wins + [stage] + face + ticks + hands + belfry + roof + pins + [hall] + hall_side + hall_wins + tower2
                + [ground(-3.0, 3.2)])


@design("landmarks_tower_bridge", T)
def tower_bridge(rng):
    parts = []
    for c in (-1.4, 1.4):
        parts += [poly((c - 0.7, -2.0), (c - 0.6, -2.3), (c + 0.6, -2.3), (c + 0.7, -2.0), closed=False),
                  [(c - 0.5, -2.0), (c - 0.5, 1.6)], [(c + 0.5, -2.0), (c + 0.5, 1.6)],
                  rect(c - 0.68, -2.0, c - 0.5, 2.0), rect(c + 0.5, -2.0, c + 0.68, 2.0),
                  poly((c - 0.72, 2.0), (c - 0.59, 2.45), (c - 0.46, 2.0), closed=False), poly((c + 0.46, 2.0), (c + 0.59, 2.45), (c + 0.72, 2.0), closed=False),
                  poly((c - 0.5, 1.6), (c, 2.7), (c + 0.5, 1.6), closed=False), [(c, 2.7), (c, 3.0)],
                  gothic(c - 0.3, c + 0.3, -1.0, 0.0), gothic(c - 0.3, c - 0.05, 0.5, 1.2, True), gothic(c + 0.05, c + 0.3, 0.5, 1.2, True)]
    deck = [[(-0.9, -0.8), (0.9, -0.8)], [(-0.9, -1.05), (0.9, -1.05)], [(-3.4, -0.8), (-2.08, -0.8)], [(-3.4, -1.05), (-2.08, -1.05)],
            [(2.08, -0.8), (3.4, -0.8)], [(2.08, -1.05), (3.4, -1.05)]]
    walk = [rect(-0.9, 1.0, 0.9, 1.4), [(-0.9, 1.0)] + [(-0.9 + 0.3 * k, 1.4 if k % 2 else 1.0) for k in range(1, 7)]]
    chains_ = []
    for s in (-1, 1):
        c1 = quad((s * 2.08, 1.0), (s * 2.6, -0.3), (s * 3.4, -0.6), 16)
        chains_ += [c1] + [[(s * x, quad((2.08, 1.0), (2.6, -0.3), (3.4, -0.6), 16)[i][1]), (s * x, -0.8)]
                           for i, x in [(4, quad((2.08, 1.0), (2.6, -0.3), (3.4, -0.6), 16)[4][0]),
                                        (8, quad((2.08, 1.0), (2.6, -0.3), (3.4, -0.6), 16)[8][0])]]
    water = waves(-3.4, 3.4, [-2.6, -3.0], 0.06, 0.7)
    return make("Tower Bridge, London", parts + deck + walk + chains_ + water)


@design("landmarks_leaning_tower_pisa", T)
def pisa(rng):
    parts = [[(-0.8, 0.0), (-0.8, 5.0)], [(0.8, 0.0), (0.8, 5.0)], [(-0.95, 0.0), (0.95, 0.0)]]
    parts += [gothic(-0.75 + 0.3 * k, -0.55 + 0.3 * k, 0.1, 0.7) for k in range(5)]
    cols = [-0.8 + 0.32 * k for k in range(6)]
    y = 0.9
    for s in range(6):
        parts.append([(-0.92, y), (0.92, y)])
        ys = y + 0.45
        parts.append(chain(*[arc((cols[k] + cols[k + 1]) / 2, ys, 0.16, math.pi, 0, 8) for k in range(5)]))
        parts += [[(x, y), (x, ys)] for x in cols[1:-1]]
        y += 0.7
    parts.append([(-0.92, y), (0.92, y)])
    parts += [[(-0.55, y), (-0.55, y + 0.6)], [(0.55, y), (0.55, y + 0.6)], [(-0.65, y + 0.6), (0.65, y + 0.6)]]
    parts += [arch(-0.45 + 0.32 * k, -0.25 + 0.32 * k, y + 0.05, y + 0.5) for k in range(3)]
    parts.append(arc(0, y + 0.6, 0.3, 0, math.pi, 10))
    parts = [transform(p, dy=-3.0, rot=-0.09) for p in parts]
    parts += [ground(-3.0, 3.0, -3.0), tree(-2.3, -3.0, 1.3), tree(2.4, -3.0, 1.0), cloud(-2.0, 1.8, 0.8), cloud(2.2, 0.6, 0.7)]
    return make("Leaning Tower of Pisa", parts)


@design("landmarks_colosseum", T)
def colosseum(rng):
    prof = [(0.6, 1.8), (0.9, 1.4), (1.3, 1.25), (1.7, 0.5), (2.2, 0.25), (2.6, -0.2), (3.2, -0.45)]

    def top_at(x):
        if x <= prof[0][0]:
            return 1.8
        for (xa, ya), (xb, yb) in zip(prof, prof[1:]):
            if xa <= x <= xb:
                return ya + (yb - ya) * (x - xa) / (xb - xa)
        return prof[-1][1]

    outline = chain([(-3.2, -2.0), (-3.2, 1.8)], prof, [(3.2, -2.0)])
    cols = [3.2 * math.sin(-1.4 + 2.8 * k / 12) / math.sin(1.4) for k in range(13)]
    parts = [outline, ground(-3.5, 3.5, -2.0)]
    tiers = [(-2.0, -0.9), (-0.9, 0.2), (0.2, 1.2)]
    for i, (yb, yt) in enumerate(tiers):
        if i:
            xe = max(x for x in [k * 0.02 - 3.2 for k in range(321)] if top_at(x) >= yb + 0.02)
            parts.append([(-3.2, yb), (xe, yb)])
        for a, b in zip(cols, cols[1:]):
            g = (b - a) * 0.18
            if top_at(b) > yt - 0.05:
                parts.append(arch(a + g, b - g, yb + 0.12, yt - 0.18, True, 8))
    parts.append([(-3.2, 1.2), (0.6, 1.2)])
    parts += [rect(x - 0.12, 1.4, x + 0.12, 1.6) for x in cols[1:6]]
    parts += [cloud(-2.0, 2.8, 0.8), cloud(2.0, 2.3, 0.6)]
    return make("The Colosseum, Rome", parts)


@design("landmarks_parthenon", T)
def parthenon(rng):
    rock = chain([(-3.4, -3.0), (-3.1, -2.4), (-2.6, -2.2)], [(2.6, -2.2), (3.0, -2.5), (3.4, -3.0)])
    steps = [rect(-2.8, -2.2, 2.8, -1.95), rect(-2.65, -1.95, 2.65, -1.7)]
    xs = [-2.4 + 4.8 * k / 7 for k in range(8)]
    cols = []
    for x in xs:
        cols += [poly((x - 0.2, -1.7), (x - 0.16, 0.6), (x + 0.16, 0.6), (x + 0.2, -1.7), closed=False),
                 rect(x - 0.25, 0.6, x + 0.25, 0.75), [(x, -1.6), (x, 0.5)]]
    ent = [rect(-2.75, 0.75, 2.75, 1.25), rect(-2.75, 1.25, 2.75, 1.7)]
    trig = [[(x, 1.3), (x, 1.65)] for x in [-2.5 + 0.5 * k for k in range(11)]]
    ped = [poly((-2.9, 1.7), (2.9, 1.7), (0.0, 2.7)), poly((-2.3, 1.85), (2.3, 1.85), (0.0, 2.55))]
    ruin = [poly((1.6, 2.55), (1.9, 2.2), (2.2, 2.1), closed=False)]
    return make("The Parthenon, Athens", [rock] + steps + cols + ent + trig + ped + ruin + [cloud(-2.3, 3.2, 0.7)])


@design("landmarks_arc_de_triomphe", T)
def arc_triomphe(rng):
    body = rect(-2.2, -2.8, 2.2, 1.6)
    main = arch(-0.85, 0.85, -2.8, 0.6, n=20)
    volt = arc(0, -0.25, 1.1, 0.05, math.pi - 0.05, 20)
    panels = [rect(-2.0, -1.6, -1.15, 0.1), rect(1.15, -1.6, 2.0, 0.1), rect(-2.0, 0.35, -1.15, 1.0), rect(1.15, 0.35, 2.0, 1.0)]
    figs = []
    for c in (-1.575, 1.575):
        figs += [circle(c, -0.35, 0.13, 12), poly((c - 0.25, -1.45), (c - 0.1, -0.5), (c + 0.1, -0.5), (c + 0.25, -1.45), closed=False),
                 [(c - 0.1, -0.7), (c - 0.3, -0.2)]]
    cornice = [rect(-2.35, 1.6, 2.35, 1.85), rect(-2.2, 1.85, 2.2, 2.6), rect(-2.3, 2.6, 2.3, 2.75)]
    frieze = [[(-2.2, 1.35), (2.2, 1.35)]]
    shields = [circle(-1.8 + 0.6 * k, 2.22, 0.15, 14) for k in range(7)]
    flag = [[(0, 0.4), (0, -1.4)], rect(-0.55, -1.4, 0.55, 0.1)] + [[(x, -1.4), (x, 0.1)] for x in (-0.18, 0.18)]
    plaza = [ground(-3.3, 3.3, -2.8), [(-3.3, -3.2), (3.3, -3.2)], tree(-2.9, -2.8, 1.1), tree(2.9, -2.8, 1.1)]
    return make("Arc de Triomphe, Paris", [body, main, volt] + panels + figs + cornice + frieze + shields + flag + plaza)


@design("landmarks_brandenburg_gate", T)
def brandenburg(rng):
    parts = [ground(-3.4, 3.4, -2.8), rect(-3.0, -2.8, 3.0, -2.6)]
    for x in (-2.5, -1.5, -0.5, 0.5, 1.5, 2.5):
        parts += [rect(x - 0.2, -2.6, x + 0.2, 0.3), [(x, -2.5), (x, 0.2)], rect(x - 0.28, 0.3, x + 0.28, 0.45)]
    parts += [rect(-3.0, 0.45, 3.0, 0.9), rect(-3.1, 0.9, 3.1, 1.3)]
    parts += [[(x, 0.95), (x, 1.25)] for x in [-2.75 + 0.5 * k for k in range(12)]]
    parts += [rect(-2.0, 1.3, 2.0, 1.85), rect(-1.2, 1.85, 1.2, 2.1)]
    parts[-1] = rect(-1.7, 1.85, 1.7, 2.1)
    horse = [(0.25, 0.0), (0.28, 0.5), (0.18, 0.95), (0.05, 1.1), (-0.02, 0.98), (-0.35, 0.75), (-0.42, 0.62), (-0.15, 0.6), (-0.12, 0.45),
             (-0.25, 0.3), (-0.2, 0.0)]
    leg_ = [(-0.2, 0.22), (-0.45, 0.18), (-0.5, 0.02)]
    q, hints = [], []
    for x, sg in ((-1.35, 1), (-0.75, 1), (0.75, -1), (1.35, -1)):
        q += [transform(horse, dx=x, dy=2.1, s=0.85, sx=0.85 * sg), transform(leg_, dx=x, dy=2.1, s=0.85, sx=0.85 * sg)]
        hints.append(eye(x - sg * 0.12, 2.1 + 0.8 * 0.85, 0.04))
    q += [poly((-0.35, 2.1), (-0.3, 2.5), (0.3, 2.5), (0.35, 2.1), closed=False), circle(0, 3.2, 0.13, 12),
          poly((-0.18, 2.5), (-0.1, 3.05), (0.1, 3.05), (0.18, 2.5), closed=False), [(0.1, 2.95), (0.35, 3.3)], [(0.38, 2.5), (0.38, 3.9)],
          circle(0.38, 4.05, 0.15, 12), [(0.28, 3.75), (0.48, 3.75)]]
    return make("Brandenburg Gate, Berlin", parts + q, hints)


@design("landmarks_st_basils", T)
def st_basils(rng):
    parts = [ground(-3.3, 3.3, -2.9), rect(-3.0, -2.9, 3.0, -1.4)]
    parts += [arch(-2.7 + 0.6 * k, -2.4 + 0.6 * k, -2.9, -1.8) for k in range(10)]
    # central tent tower
    parts += [[(-0.45, -1.4), (-0.45, 1.5)], [(0.45, -1.4), (0.45, 1.5)], [(-0.55, 1.5), (0.55, 1.5)],
              poly((-0.5, 1.5), (-0.1, 3.4), (0.1, 3.4), (0.5, 1.5), closed=False), [(-0.1, 3.4), (0.1, 3.4)],
              onion(0, 3.4, 0.15, 0.5), [(0, 3.9), (0, 4.3)], [(-0.12, 4.15), (0.12, 4.15)]]
    parts += [arc(x, 1.2, 0.15, 0, math.pi, 6) for x in (-0.3, 0.0, 0.3)]
    parts += [[(-0.38 + 0.25 * k, 1.9 + 0.0), (-0.2 + 0.1 * k, 3.2)] for k in range(4)]
    for cx, yb, hw, h in [(-1.4, 0.6, 0.55, 1.4), (1.4, 0.85, 0.58, 1.45), (-2.45, -0.3, 0.42, 1.1), (2.45, -0.15, 0.42, 1.1)]:
        dw = hw * 0.65
        parts += [[(cx - dw, -1.4), (cx - dw, yb)], [(cx + dw, -1.4), (cx + dw, yb)], [(cx - dw - 0.05, yb), (cx + dw + 0.05, yb)],
                  onion(cx, yb, hw * 0.75, h), [(cx, yb + h), (cx, yb + h + 0.35)], [(cx - 0.1, yb + h + 0.22), (cx + 0.1, yb + h + 0.22)]]
        parts.append(cubic((cx - hw * 0.6, yb + 0.05), (cx - hw * 0.1, yb + 0.4 * h), (cx + hw * 0.6, yb + 0.35 * h), (cx + 0.05, yb + 0.85 * h), 12))
        parts.append(cubic((cx - hw * 0.1, yb + 0.02), (cx + hw * 0.6, yb + 0.2 * h), (cx + hw * 0.8, yb + 0.45 * h), (cx + hw * 0.25, yb + 0.72 * h), 12))
        parts += [arc(cx + dx, yb - 0.45, dw / 2, 0, math.pi, 6) for dx in (-dw / 2, dw / 2)]
    return make("St. Basil's Cathedral, Moscow", parts)


@design("landmarks_sagrada_familia", T)
def sagrada(rng):
    parts = [ground(-3.2, 3.2, -3.0)]

    def spire(cx, y0, hw, h):
        left = cubic((cx - hw, y0), (cx - hw, y0 + h * 0.55), (cx - hw * 0.65, y0 + h * 0.92), (cx, y0 + h), 20)
        out = [chain(left, mirror_x(left, cx)[::-1])]
        for j in range(int(h / 0.45)):
            yy = y0 + 0.4 + 0.45 * j
            if yy > y0 + h * 0.8:
                break
            w = hw * (1 - ((yy - y0) / h) ** 3) * 0.55
            out.append([(cx - w, yy), (cx + w, yy + 0.15)])
        out += [circle(cx, y0 + h + 0.2, 0.18, 14), [(cx, y0 + h + 0.38), (cx, y0 + h + 0.6)], [(cx - 0.15, y0 + h + 0.5), (cx + 0.15, y0 + h + 0.5)]]
        return out

    for cx, h in [(-2.0, 3.4), (-0.85, 4.3), (0.85, 4.3), (2.0, 3.4)]:
        parts += spire(cx, -0.6, 0.38, h)
    parts += spire(0.0, 0.5, 0.25, 4.0)
    parts += [rect(-2.7, -3.0, 2.7, -0.6)]
    parts += [gothic(-0.6, 0.6, -3.0, -0.8, n=10), gothic(-2.2, -1.2, -3.0, -1.1, n=10), gothic(1.2, 2.2, -3.0, -1.1, n=10)]
    parts += [circle(0, -1.7, 0.25, 16), [(0, -3.0), (0, -2.2)]]
    parts += [wave(-2.7, 2.7, -0.75, 0.08, 12)]
    return make("Sagrada Familia, Barcelona", parts)


@design("landmarks_neuschwanstein", T)
def neuschwanstein(rng):
    parts = []
    cliff = chain([(-3.4, -3.2), (-3.0, -2.2), (-2.4, -1.7), (-1.6, -1.6)], [(1.8, -1.6), (2.4, -1.9), (2.8, -2.6), (3.4, -3.2)])
    parts.append(cliff)

    def tower(cx, y0, hw, ytop, rh):
        out = [[(cx - hw, y0), (cx - hw, ytop)], [(cx + hw, y0), (cx + hw, ytop)],
               poly((cx - hw - 0.08, ytop), (cx, ytop + rh), (cx + hw + 0.08, ytop), closed=False), [(cx - hw - 0.08, ytop), (cx + hw + 0.08, ytop)],
               [(cx, ytop + rh), (cx, ytop + rh + 0.25)]]
        out.append(arch(cx - 0.08, cx + 0.08, ytop - 0.6, ytop - 0.25, True, 6))
        return out

    # main hall block
    parts += [poly((-1.3, -1.6), (-1.3, 0.9), (0.6, 0.9), (0.6, -1.6), closed=False), poly((-1.4, 0.9), (-0.35, 1.9), (0.7, 0.9), closed=False)]
    parts += windows(-1.2, 0.5, -1.4, 0.6, 4, 3, 0.4, 0.5)
    parts += tower(-0.3, 0.9, 0.12, 2.5, 0.6)[1:]
    parts += tower(1.1, -1.6, 0.42, 1.6, 1.3)
    parts += tower(-1.75, -1.6, 0.35, 0.8, 1.0)
    parts += tower(2.0, -1.6, 0.25, 0.2, 0.8)
    parts += tower(-2.55, -1.75, 0.22, -0.2, 0.7)
    parts += windows(0.7, 1.5, -1.3, 1.0, 2, 3, 0.35, 0.45)
    parts += [rect(-2.4, -1.65, -2.1, -0.9), rect(1.55, -1.6, 1.75, -0.5)]
    trees_ = []
    for k, x in enumerate([-3.1, -2.6, -2.0, -1.3, -0.6, 0.1, 0.8, 1.5, 2.2, 2.9]):
        yb = -3.2 + 0.0
        trees_.append(poly((x - 0.3, yb), (x, yb + 0.9 + 0.2 * (k % 3)), (x + 0.3, yb), closed=False))
    return make("Neuschwanstein Castle, Bavaria", parts + trees_ + [cloud(-2.3, 2.4, 0.8)])


@design("landmarks_kinderdijk_windmills", T)
def windmills(rng):
    parts = [ground(-3.4, 3.4, -1.6)]

    def mill(cx, y0, s):
        out = [poly((cx - 0.6 * s, y0), (cx - 0.35 * s, y0 + 2.0 * s), (cx + 0.35 * s, y0 + 2.0 * s), (cx + 0.6 * s, y0), closed=False),
               chain(arc(cx, y0 + 2.0 * s, 0.4 * s, math.pi + 0.15, -0.15, 10)), arch(cx - 0.15 * s, cx + 0.15 * s, y0, y0 + 0.5 * s),
               [(cx - 0.75 * s, y0 + 0.7 * s), (cx + 0.75 * s, y0 + 0.7 * s)]]
        hub = (cx, y0 + 2.05 * s)
        for a in (0.5, 0.5 + math.pi / 2, 0.5 + math.pi, 0.5 + 1.5 * math.pi):
            ca, sa = math.cos(a), math.sin(a)
            tip = (hub[0] + 1.8 * s * ca, hub[1] + 1.8 * s * sa)
            out.append([hub, tip])
            r0, r1 = 0.4 * s, 1.8 * s
            w = 0.3 * s
            out.append(poly((hub[0] + r0 * ca, hub[1] + r0 * sa), (hub[0] + r0 * ca - w * sa, hub[1] + r0 * sa + w * ca),
                            (hub[0] + r1 * ca - w * sa, hub[1] + r1 * sa + w * ca), (hub[0] + r1 * ca, hub[1] + r1 * sa), closed=False))
        out.append(circle(hub[0], hub[1], 0.1 * s, 10))
        return out

    parts += mill(-1.6, -1.6, 1.0) + mill(1.8, -1.0, 0.65)
    canal = [[(-3.4, -2.2), (3.4, -2.2)]] + waves(-3.0, 3.0, [-2.6, -3.0], 0.05, 0.6)
    reeds = [[(x, -1.6), (x + 0.1 * math.sin(x * 5), -1.2)] for x in (2.6, 2.8, 3.0, -3.1, -2.9)]
    return make("Windmills of Kinderdijk", parts + canal + reeds)


@design("landmarks_london_eye", T)
def london_eye(rng):
    c, R = (0.0, 0.6), 2.6
    parts = [circle(c[0], c[1], R, 120), circle(c[0], c[1], R - 0.25, 110), circle(c[0], c[1], 0.25, 16)]
    for k in range(16):
        a = k * TAU / 16
        parts.append([(c[0] + 0.25 * math.cos(a), c[1] + 0.25 * math.sin(a)), (c[0] + (R - 0.25) * math.cos(a), c[1] + (R - 0.25) * math.sin(a))])
        parts.append(ellipse(c[0] + (R + 0.18) * math.cos(a), c[1] + (R + 0.18) * math.sin(a), 0.2, 0.13, 14))
    parts += [[(c[0], c[1]), (-1.6, -2.4)], [(c[0], c[1]), (-0.9, -2.4)], [(-2.0, -2.4), (2.6, -2.4)]]
    parts += [[(-3.2, -2.4), (-2.0, -2.4)]] + waves(-3.2, 3.2, [-2.75, -3.1], 0.05, 0.7)
    parts += [cloud(-2.6, 3.1, 0.6), cloud(2.7, 2.9, 0.5)]
    return make("The London Eye", parts)


@design("landmarks_rialto_bridge", T)
def rialto(rng):
    parts = []
    span = arc(0, -3.6, 3.1, math.radians(15), math.radians(165), 40)
    parts += [span, [(-3.4, -2.6), (-2.95, -2.6)], [(2.95, -2.6), (3.4, -2.6)]]
    parts += [poly((-3.4, -1.9), (0, -0.55), (3.4, -1.9), closed=False), poly((-3.4, -1.55), (0, -0.2), (3.4, -1.55), closed=False)]
    # arcade with portico
    for s in (-1, 1):
        for k in range(3):
            x0 = s * (0.75 + 0.5 * k)
            x1 = x0 + s * 0.35
            yb = -0.2 - 1.35 * (abs(x0) + 0.2) / 3.4
            parts.append(arch(min(x0, x1), max(x0, x1), yb, yb + 0.55, False, 6))
    parts += [rect(-0.55, -0.35, 0.55, 0.5), arch(-0.25, 0.25, -0.35, 0.2), poly((-0.7, 0.5), (0, 0.95), (0.7, 0.5))]
    # gondola
    g = chain(cubic((-2.6, -2.9), (-1.6, -3.3), (0.2, -3.3), (1.2, -2.9), 20), [(1.4, -2.6), (1.45, -2.75), (1.3, -2.85)])
    gondola = [chain([(-2.85, -2.45)], g), [(-2.85, -2.45), (-2.6, -2.9)], [(-2.7, -2.75), (1.2, -2.9)]]
    man = [circle(-1.4, -1.7, 0.13, 12), poly((-1.55, -2.85), (-1.5, -1.85), (-1.3, -1.85), (-1.25, -2.85), closed=False), [(-1.35, -2.0), (-0.6, -1.7)],
           [(-0.6, -1.7), (0.2, -3.3)]]
    water = waves(-3.4, 3.4, [-3.4, -3.75], 0.05, 0.6)
    return make("Rialto Bridge, Venice", parts + gondola + man + water + [[(-3.4, -2.6), (-3.4, -1.9)], [(3.4, -2.6), (3.4, -1.9)]])


# dropped: image rights of this landmark are actively enforced for commercial use
def louvre(rng):
    apex, L, R = (0.0, 1.6), (-2.3, -1.8), (2.3, -1.8)
    parts = [poly(L, apex, R)]
    for k in range(1, 8):
        t = k / 8
        b = (L[0] + 4.6 * t, -1.8)
        parts.append([b, (R[0] + (apex[0] - R[0]) * (1 - t), R[1] + (apex[1] - R[1]) * (1 - t))])
        parts.append([b, (L[0] + (apex[0] - L[0]) * t, L[1] + (apex[1] - L[1]) * t)])
    parts += [arch(-0.35, 0.35, -1.8, -1.0)]
    parts += [rect(-3.4, -1.0, -2.5, 1.3), rect(2.5, -1.0, 3.4, 1.3), poly((-3.4, 1.3), (-2.95, 1.9), (-2.5, 1.3), closed=False),
              poly((2.5, 1.3), (2.95, 1.9), (3.4, 1.3), closed=False)]
    parts += windows(-3.4, -2.5, -0.9, 1.2, 2, 3, 0.4, 0.5) + windows(2.5, 3.4, -0.9, 1.2, 2, 3, 0.4, 0.5)
    parts += [ground(-3.4, 3.4, -1.8), [(-3.4, -1.0), (-2.5, -1.0)]]
    pool = [poly((-3.2, -2.2), (-1.0, -2.2), (-1.3, -3.0), (-3.4, -3.0)), poly((3.2, -2.2), (1.0, -2.2), (1.3, -3.0), (3.4, -3.0))]
    return make("Louvre Pyramid, Paris", parts + pool + [circle(-1.9, -2.55, 0.12, 10), circle(2.2, -2.6, 0.12, 10)])


# ---------------------------------------------------------------- Americas & Africa

def x_at(pts, y):
    """x where a polyline first crosses height y (linear interpolation)."""
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        if (ya - y) * (yb - y) <= 0 and ya != yb:
            return xa + (xb - xa) * (y - ya) / (yb - ya)
    return pts[-1][0]


def y_at(pts, x):
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        if (xa - x) * (xb - x) <= 0 and xa != xb:
            return ya + (yb - ya) * (x - xa) / (xb - xa)
    return pts[-1][1]


def palm(cx, y0, h, lean=0.3):
    top = (cx + lean, y0 + h)
    trunk = [cubic((cx - 0.08, y0), (cx - 0.05, y0 + h * 0.5), (top[0] - 0.1, top[1] - 0.3), (top[0] - 0.05, top[1]), 12),
             cubic((cx + 0.08, y0), (cx + 0.1, y0 + h * 0.5), (top[0] + 0.05, top[1] - 0.3), (top[0] + 0.05, top[1]), 12)]
    fronds = [lens(top, (top[0] + 0.9 * math.cos(a), top[1] + 0.9 * math.sin(a) - 0.25 * abs(math.cos(a))), 0.18)
              for a in (0.2, 0.9, 1.6, 2.3, 2.95)]
    return trunk + fronds


@design("landmarks_taj_mahal", T)
def taj_mahal(rng):
    parts = [rect(-3.2, -2.6, 3.2, -2.25), poly((-1.15, -2.25), (-1.15, 0.75), (1.15, 0.75), (1.15, -2.25), closed=False),
             poly((-0.8, -2.25), (-0.8, 0.55), (0.8, 0.55), (0.8, -2.25), closed=False), gothic(-0.55, 0.55, -2.25, 0.3, n=12)]
    for s in (-1, 1):
        parts += [[(s * 1.15, 0.3), (s * 1.85, 0.3), (s * 1.85, -2.25)],
                  gothic(min(s * 1.3, s * 1.7), max(s * 1.3, s * 1.7), -2.0, -1.2, True), gothic(min(s * 1.3, s * 1.7), max(s * 1.3, s * 1.7), -0.85, -0.05, True),
                  [(s * 1.25, 0.3), (s * 1.25, 0.7)], [(s * 1.75, 0.3), (s * 1.75, 0.7)], [(s * 1.18, 0.7), (s * 1.82, 0.7)], onion(s * 1.5, 0.7, 0.28, 0.65)]
        x = s * 2.65
        parts += [poly((x - 0.22, -2.25), (x - 0.16, 1.4), (x + 0.16, 1.4), (x + 0.22, -2.25), closed=False)]
        parts += [[(x - 0.32, yy), (x + 0.32, yy)] for yy in (-1.0, 0.25, 1.4)]
        parts += [[(x - 0.14, 1.4), (x - 0.14, 1.7)], [(x + 0.14, 1.4), (x + 0.14, 1.7)], [(x - 0.22, 1.7), (x + 0.22, 1.7)], onion(x, 1.7, 0.2, 0.5)]
        parts += [cypress(s * 1.4, -3.4, 0.85, 0.3), cypress(s * 2.1, -3.45, 1.0, 0.32)]
    parts += [rect(-0.75, 0.75, 0.75, 1.1), onion(0, 1.1, 0.85, 1.9, 1.25), [(0, 3.0), (0, 3.45)], circle(0, 3.2, 0.07, 8)]
    parts += [poly((-0.45, -2.6), (-0.8, -3.5), closed=False), poly((0.45, -2.6), (0.8, -3.5), closed=False)]
    return make("Taj Mahal, Agra", parts)


@design("landmarks_pyramids_giza", T)
def pyramids(rng):
    def pyr(xl, xr, ax, ay, fx, y):
        return [poly((xl, y), (ax, ay), (xr, y), closed=False), [(ax, ay), (fx, y - 0.25)], [(xl, y), (fx, y - 0.25), (xr, y)]]

    parts = pyr(0.0, 3.4, 1.6, 2.4, 2.0, -1.3) + pyr(-2.3, 0.0, -1.0, 1.2, -0.7, -1.3) + pyr(-3.4, -2.3, -2.85, 0.1, -2.7, -1.3)
    sphinx = chain(quad((-2.2, -2.6), (-2.3, -2.0), (-1.8, -1.95), 8), [(-0.1, -1.95), (0.0, -1.4)], quad((0.0, -1.4), (0.05, -1.15), (0.35, -1.15), 6),
                   [(0.55, -1.35), (0.55, -1.75), (0.42, -1.95), (0.5, -2.25), (1.3, -2.3), (1.3, -2.6)])
    parts += [sphinx, [(0.18, -1.35), (0.22, -1.9)], [(-1.4, -2.6), (-1.3, -2.2), (-0.9, -2.2)], [(-3.4, -2.6), (3.4, -2.6)]]
    parts += [circle(-2.4, 2.3, 0.45, 30)]
    parts += palm(2.6, -2.6, 1.6, 0.2)
    parts += [wave(-3.4, -0.8, -3.1, 0.06, 1.5, 40)]
    return make("Great Pyramids and the Sphinx", parts, [eye(0.42, -1.45, 0.05)])


@design("landmarks_sphinx_head", T)
def sphinx_head(rng):
    left = chain([(-0.95, -2.5), (-1.5, -2.5)], cubic((-1.5, -2.5), (-1.7, -1.5), (-2.0, -0.6), (-1.85, 0.3), 16),
                 cubic((-1.85, 0.3), (-1.7, 1.3), (-1.2, 2.15), (0, 2.2), 16))
    outline = chain(left, mirror_x(left)[::-1])
    face = chain([(-0.85, 1.05), (-0.88, 0.2)], cubic((-0.88, 0.2), (-0.85, -0.6), (-0.5, -1.2), (0, -1.3), 12))
    flap = cubic((-0.88, 0.2), (-1.05, -0.6), (-1.0, -1.5), (-0.95, -2.5), 16)
    parts = [outline, chain(face, mirror_x(face)[::-1]), flap, mirror_x(flap), quad((-0.85, 1.05), (0, 1.3), (0.85, 1.05), 16)]
    oleft = left[2:]
    for y in (-2.1, -1.6, -1.1, -0.6, -0.1):
        xo, xi = x_at(oleft, y), x_at(flap, y)
        parts += [[(xo, y), (xi, y)], [(-xo, y), (-xi, y)]]
    parts += [quad((-1.45, 1.35), (0, 1.85), (1.45, 1.35), 16), quad((-1.05, 1.8), (0, 2.1), (1.05, 1.8), 12)]
    parts += [lens((-0.62, 0.45), (-0.15, 0.45), 0.25), lens((0.15, 0.45), (0.62, 0.45), 0.25),
              quad((-0.68, 0.72), (-0.4, 0.88), (-0.1, 0.72), 8), quad((0.1, 0.72), (0.4, 0.88), (0.68, 0.72), 8),
              [(-0.06, 0.55), (-0.15, -0.2)], [(0.06, 0.55), (0.15, -0.2)], quad((-0.28, -0.22), (0, -0.4), (0.28, -0.22), 8),
              quad((-0.38, -0.62), (0, -0.52), (0.38, -0.62), 10), quad((-0.26, -0.78), (0, -0.9), (0.26, -0.78), 8),
              lens((0, 1.12), (0, 1.55), 0.25), [(-1.5, -2.5), (-3.0, -3.1)], [(1.5, -2.5), (3.0, -3.1)], [(-0.55, -1.05), (-0.6, -2.5)], [(0.55, -1.05), (0.6, -2.5)]]
    return make("Great Sphinx Close-Up", parts, [eye(-0.38, 0.45, 0.09), eye(0.38, 0.45, 0.09)])


# dropped: image rights of this landmark are actively enforced for commercial use
def opera_house(rng):
    b = -0.9

    def front(base, tip):
        return [(base, b), tip]

    def on_front(base, tip, y):
        return (base + (tip[0] - base) * (y - b) / (tip[1] - b), y)

    A = [(-2.7, (-3.05, 0.4)), (-2.1, (-2.45, 1.3)), (-1.3, (-1.65, 2.2))]
    B = [(2.8, (3.1, 0.3)), (2.2, (2.5, 1.1)), (1.4, (1.75, 1.85))]
    parts = []
    for grp, sgn, end in ((A, 1, 0.1), (B, -1, 0.45)):
        for i, (base, tip) in enumerate(grp):
            parts.append(front(base, tip))
            if i < len(grp) - 1:
                nb, nt = grp[i + 1]
                yy = b + (tip[1] - b) * 0.35
                p = on_front(nb, nt, yy)
                parts.append(quad(tip, (tip[0] + sgn * 0.55, tip[1]), p, 14))
            else:
                parts.append(cubic(tip, (tip[0] + sgn * 1.15, tip[1]), (end - sgn * 0.1, 0.4), (end, b), 20))
            parts.append(quad(tip, (tip[0] + sgn * 0.25, tip[1] - 0.6), (base + sgn * 0.25, b), 10))
    parts += [rect(-3.3, -1.6, 3.3, b)]
    parts += [[(-0.6, -1.6), (-0.4, -1.2), (0.8, -1.2), (1.0, -1.6)]]
    parts += waves(-3.4, 3.4, [-2.1, -2.6, -3.1], 0.06, 0.6)
    return make("Sydney Opera House", parts + [cloud(0.2, 2.6, 0.7)])


@design("landmarks_golden_gate_bridge", T)
def golden_gate(rng):
    parts = [[(-3.5, -0.8), (3.5, -0.8)], [(-3.5, -1.05), (3.5, -1.05)]]
    for c in (-1.6, 1.6):
        parts += [poly((c - 0.42, -0.8), (c - 0.4, 2.6), (c - 0.22, 2.6), (c - 0.22, -0.8), closed=False),
                  poly((c + 0.22, -0.8), (c + 0.22, 2.6), (c + 0.4, 2.6), (c + 0.42, -0.8), closed=False),
                  [(c - 0.42, -1.05), (c - 0.44, -2.0)], [(c - 0.22, -1.05), (c - 0.22, -2.0)], [(c + 0.22, -1.05), (c + 0.22, -2.0)], [(c + 0.42, -1.05), (c + 0.44, -2.0)],
                  rect(c - 0.6, -2.3, c + 0.6, -2.0)]
        parts += [rect(c - 0.22, y, c + 0.22, y + 0.25) for y in (0.2, 1.0, 1.8)] + [rect(c - 0.48, 2.6, c + 0.48, 2.75)]
    main = [(x, -0.6 + 3.15 * (x / 1.6) ** 2) for x in [-1.6 + 3.2 * i / 40 for i in range(41)]]
    side = quad((-1.6, 2.6), (-2.4, 0.4), (-3.5, -0.6), 16)
    parts += [main, side, mirror_x(side)]
    for x in [-1.3 + 0.26 * k for k in range(11)]:
        parts.append([(x, -0.6 + 3.15 * (x / 1.6) ** 2), (x, -0.8)])
    for x in (2.2, 2.75, 3.2):
        yy = y_at(mirror_x(side)[::-1], x)
        parts += [[(x, yy), (x, -0.8)], [(-x, yy), (-x, -0.8)]]
    parts += waves(-3.5, 3.5, [-2.6, -3.0], 0.06, 0.7)
    parts += [chain([(1.9, -1.9)], cubic((2.3, -1.2), (2.7, -0.4), (3.0, -0.4), (3.5, -0.3), 12))]
    parts.pop()
    return make("Golden Gate Bridge, San Francisco", parts + [cloud(-2.6, 2.6, 0.6), cloud(0.0, 2.9, 0.5)])


@design("landmarks_empire_state", T)
def empire_state(rng):
    L = [(-1.7, -3.0), (-1.7, -2.2), (-1.35, -2.2), (-1.35, 1.5), (-1.0, 1.5), (-1.0, 2.0), (-0.7, 2.0), (-0.7, 2.35), (-0.42, 2.35), (-0.42, 2.9),
         (-0.3, 2.9), (-0.25, 3.5)]
    top = arc(0, 3.5, 0.25, math.pi, 0, 10)
    parts = [chain(L, top, mirror_x(L)[::-1]), [(0, 3.75), (0, 4.6)], [(-0.3, 3.2), (0.3, 3.2)]]
    parts += [[(x, -2.0), (x, 1.35)] for x in (-0.9, -0.45, 0.0, 0.45, 0.9)]
    parts += [[(x, 1.6), (x, 2.2)] for x in (-0.5, 0.0, 0.5)]
    parts += [rect(-0.35, -3.0, 0.35, -2.4), [(-1.7, -2.4), (-0.35, -2.4)], [(0.35, -2.4), (1.7, -2.4)]]
    parts += [poly((-3.3, -3.0), (-3.3, -0.4), (-2.0, -0.4), (-2.0, -3.0), closed=False)] + windows(-3.3, -2.0, -2.8, -0.6, 3, 5, 0.45, 0.5)
    parts += [poly((2.0, -3.0), (2.0, -1.2), (2.65, -0.5), (3.3, -1.2), (3.3, -3.0), closed=False)] + windows(2.0, 3.3, -2.8, -1.3, 3, 4, 0.45, 0.5)
    parts += [ground(-3.4, 3.4), cloud(-2.4, 2.4, 0.7), cloud(2.3, 1.4, 0.6)]
    return make("Empire State Building, New York", parts)


# dropped: image rights of this landmark are actively enforced for commercial use
def space_needle(rng):
    lo = cubic((-1.4, -3.0), (-0.3, -1.2), (-0.25, 0.0), (-0.75, 1.55), 20)
    li = cubic((-0.9, -3.0), (-0.12, -1.3), (-0.1, 0.0), (-0.45, 1.55), 20)
    L = [(-0.45, 1.55), (-1.8, 2.0), (-1.8, 2.12), (-1.25, 2.2), (-1.25, 2.55), (-0.3, 3.0), (-0.12, 3.1)]
    parts = [lo, li, mirror_x(lo), mirror_x(li), chain(L, mirror_x(L)[::-1]), [(-1.25, 2.2), (1.25, 2.2)], [(-1.8, 2.0), (1.8, 2.0)],
             [(0, 3.1), (0, 4.2)], [(-0.75, 1.55), (-0.45, 1.55)], [(0.45, 1.55), (0.75, 1.55)]]
    parts += [[(x, 2.2), (x, 2.55)] for x in (-0.9, -0.45, 0.0, 0.45, 0.9)]
    parts += [[(-0.1, -3.0), (-0.1, 1.5)], [(0.1, -3.0), (0.1, 1.5)]]
    parts += [rect(-0.55, -1.75, 0.55, -1.5)]
    parts += [ground(-3.4, 3.4), chain(quad((1.1, -1.3), (2.0, 0.3), (2.4, 0.4), 10), quad((2.4, 0.4), (2.8, 0.3), (3.4, -0.9), 10)),
              poly((1.95, 0.0), (2.15, -0.15), (2.35, 0.05), (2.6, -0.2), (2.8, 0.05), closed=False), tree(-2.6, -3.0, 1.1), tree(2.7, -3.0, 0.9)]
    return make("Space Needle, Seattle", parts)


@design("landmarks_burj_khalifa", T)
def burj_khalifa(rng):
    L = [(-1.6, -3.0), (-1.6, -1.8), (-1.2, -1.8), (-1.2, -0.6), (-0.9, -0.6), (-0.9, 0.4), (-0.65, 0.4), (-0.65, 1.3), (-0.45, 1.3), (-0.45, 2.1),
         (-0.28, 2.1), (-0.28, 2.8), (-0.15, 2.8), (0.0, 4.6)]
    R = [(1.6, -3.0), (1.6, -2.3), (1.25, -2.3), (1.25, -1.2), (0.95, -1.2), (0.95, -0.1), (0.7, -0.1), (0.7, 0.9), (0.5, 0.9), (0.5, 1.7), (0.3, 1.7),
         (0.3, 2.5), (0.15, 2.5), (0.0, 4.6)]
    parts = [chain(L, R[::-1]), [(-0.25, -2.8), (-0.2, 2.0)], [(0.25, -2.8), (0.2, 2.0)]]
    parts += [[(-1.4, -2.9), (-1.4, -2.0)], [(1.4, -2.9), (1.4, -2.4)], [(-1.05, -1.6), (-1.05, -0.8)], [(1.1, -2.1), (1.1, -1.4)]]
    city = [rect(-3.3, -3.0, -2.7, -1.6), rect(-2.6, -3.0, -1.9, -2.2), rect(1.9, -3.0, 2.5, -1.4), rect(2.6, -3.0, 3.3, -2.1)]
    city += windows(-3.3, -2.7, -2.9, -1.7, 2, 3, 0.45, 0.45) + windows(1.9, 2.5, -2.9, -1.5, 2, 3, 0.45, 0.45)
    parts += city + [ground(-3.4, 3.4), cloud(-2.3, 1.6, 0.7), cloud(2.2, 2.6, 0.6)]
    return make("Burj Khalifa, Dubai", parts)


@design("landmarks_petronas_towers", T)
def petronas(rng):
    parts = [ground(-3.4, 3.4)]
    for c in (-1.4, 1.4):
        tiers = [(-3.0, 0.9, 0.62), (0.9, 1.6, 0.5), (1.6, 2.15, 0.4), (2.15, 2.55, 0.3), (2.55, 2.85, 0.2)]
        L = []
        for y0, y1, w in tiers:
            L += [(c - w, y0), (c - w, y1)]
        Lr = [(2 * c - x, y) for x, y in L]
        parts.append(chain(L, [(c - 0.08, 2.85), (c, 4.3), (c + 0.08, 2.85)], Lr[::-1]))
        parts += [[(c + dx, -2.8), (c + dx, 0.75)] for dx in (-0.3, 0.0, 0.3)]
        parts += [[(c - 0.15, yy), (c + 0.15, yy)] for yy in (3.2, 3.6)]
        parts += [[(c - w + 0.1, y1 - 0.15), (c + w - 0.1, y1 - 0.15)] for y0, y1, w in tiers[:3]]
    parts += [rect(-0.78, 0.35, 0.78, 0.65), [(-0.3, 0.35), (-0.78, -0.4)], [(0.3, 0.35), (0.78, -0.4)]]
    parts += [[(-0.6, 0.5), (0.6, 0.5)]]
    parts += [tree(-2.8, -3.0, 0.9), tree(2.8, -3.0, 0.9), tree(0.0, -3.0, 0.8)]
    return make("Petronas Twin Towers, Kuala Lumpur", parts)


@design("landmarks_cn_tower", T)
def cn_tower(rng):
    L = [(-0.5, -3.0), (-0.15, 1.4), (-0.75, 1.55), (-0.95, 1.8), (-0.75, 2.05), (-0.3, 2.15), (-0.12, 2.2), (-0.1, 2.9)]
    parts = [chain(L, mirror_x(L)[::-1]), [(0, -2.8), (0, 1.3)], [(-0.95, 1.8), (0.95, 1.8)], ellipse(0, 3.0, 0.28, 0.12, 20),
             [(0, 3.12), (0, 4.5)], [(-0.28, 3.0), (0.28, 3.0)]]
    parts.pop()
    city = [rect(-3.3, -3.0, -2.6, -0.9), rect(-2.5, -3.0, -1.75, -1.7), rect(-1.65, -3.0, -0.9, -0.5)]
    city += windows(-3.3, -2.6, -2.8, -1.1, 2, 4, 0.4, 0.45) + windows(-1.65, -0.9, -2.8, -0.7, 2, 5, 0.4, 0.45) + windows(-2.5, -1.75, -2.8, -1.8, 2, 2, 0.4, 0.45)
    dome = [chain([(0.85, -3.0), (0.85, -2.2)], arc(1.75, -2.2, 0.9, math.pi, 0, 24), [(2.65, -3.0)]),
            arc(1.75, -2.2, 0.6, 0.6, math.pi - 0.6, 14), [(0.85, -2.2), (2.65, -2.2)]]
    city += dome + [rect(2.75, -3.0, 3.3, -0.6)] + windows(2.75, 3.3, -2.8, -0.8, 1, 5, 0.4, 0.45)
    return make("CN Tower, Toronto", parts + city + [ground(-3.4, 3.4), cloud(-2.3, 2.2, 0.7), cloud(2.2, 2.9, 0.6)])


# dropped: image rights of this landmark are actively enforced for commercial use
def christ_redeemer(rng):
    L = [(-0.12, 1.52), (-0.35, 1.48), (-2.8, 1.42), (-2.95, 1.3), (-2.8, 1.18), (-1.7, 1.15)]
    L = chain(L, cubic((-1.7, 1.15), (-1.3, 0.7), (-0.9, 0.5), (-0.55, 0.55), 12), cubic((-0.55, 0.55), (-0.5, -0.2), (-0.45, -0.6), (-0.5, -1.0), 10),
              [(0, -1.0)])
    parts = [chain(L, mirror_x(L)[::-1]), ellipse(0, 1.85, 0.24, 0.32, 24),
             cubic((-0.1, 2.15), (-0.38, 2.0), (-0.36, 1.6), (-0.3, 1.5), 8), cubic((0.1, 2.15), (0.38, 2.0), (0.36, 1.6), (0.3, 1.5), 8),
             [(-0.15, 1.2), (-0.2, -0.95)], [(0.2, 1.2), (0.25, -0.95)], quad((-0.5, 0.3), (0, 0.15), (0.5, 0.3), 10),
             [(-2.75, 1.42), (-2.75, 1.18)], [(2.75, 1.42), (2.75, 1.18)], [(-1.75, 1.43), (-1.7, 1.15)], [(1.75, 1.43), (1.7, 1.15)],
             rect(-0.65, -1.35, 0.65, -1.0), rect(-0.85, -1.75, 0.85, -1.35)]
    mount = chain([(-3.4, -3.3)], cubic((-3.4, -3.3), (-2.0, -2.6), (-1.4, -2.0), (-0.95, -1.75), 16), [(0.95, -1.75)],
                  cubic((0.95, -1.75), (1.5, -2.2), (2.4, -2.6), (3.4, -3.0), 16))
    parts += [mount, [(-0.6, -1.75), (-0.9, -2.6), (-0.6, -3.2)], [(0.7, -1.75), (1.1, -2.5)]]
    parts += [cloud(-2.3, -0.6, 0.8), cloud(2.4, -0.2, 0.7), cloud(-2.0, 2.6, 0.5)]
    return make("Christ the Redeemer, Rio", parts)


@design("landmarks_machu_picchu", T)
def machu_picchu(rng):
    peak = chain([(-0.3, -0.7)], cubic((-0.3, -0.7), (0.4, 0.8), (0.6, 2.6), (1.2, 2.8), 20), cubic((1.2, 2.8), (1.8, 2.6), (2.0, 1.0), (3.4, 0.2), 20))
    back = chain(quad((-3.4, 0.4), (-2.6, 1.7), (-1.7, 0.9), 12), quad((-1.7, 0.9), (-1.0, 0.3), (-0.55, -0.15), 8))
    parts = [peak, back, [(0.9, 2.2), (1.1, 1.6)], [(1.6, 2.1), (1.5, 1.4)]]
    for x in (-2.7, -1.8, -0.2, 0.9, 2.0):
        y = -1.15
        parts += [poly((x - 0.35, y), (x - 0.35, y + 0.45), (x, y + 0.8), (x + 0.35, y + 0.45), (x + 0.35, y), closed=False),
                  poly((x - 0.1, y), (x - 0.07, y + 0.35), (x + 0.07, y + 0.35), (x + 0.1, y), closed=False)]
    parts += [[(-3.4, -1.15), (3.4, -1.15)], [(-3.4, -0.7), (-3.05, -0.7)], [(1.35, -0.7), (1.55, -0.7)], [(2.45, -0.7), (3.4, -0.7)]]
    for k in range(5):
        y, x = -1.55 - 0.35 * k, -0.6 + 0.45 * k
        parts += [[(-3.4, y), (x, y), (x, y - 0.35)]]
    parts.append([(-3.4, -3.3), (1.2, -3.3)])
    llama = [ellipse(2.3, -2.3, 0.55, 0.28, 30), [(2.7, -2.15), (2.82, -1.3)], [(2.52, -2.05), (2.62, -1.3)], ellipse(2.82, -1.22, 0.24, 0.13, 16),
             [(2.66, -1.12), (2.6, -0.88)], [(2.76, -1.12), (2.76, -0.88)]]
    llama += [[(x, -2.5), (x, -3.0)] for x in (1.95, 2.1, 2.5, 2.65)] + [[(1.75, -2.25), (1.6, -2.4)]]
    return make("Machu Picchu, Peru", parts + llama, [eye(2.88, -1.18, 0.04)])


@design("landmarks_chichen_itza", T)
def chichen_itza(rng):
    parts = [ground(-3.4, 3.4, -2.6)]
    L = []
    for k in range(9):
        y0, y1, w = -2.6 + 0.33 * k, -2.6 + 0.33 * (k + 1), 3.0 - 0.17 * k
        L += [(-w, y0), (-w + 0.06, y1), (-(w - 0.17), y1)]
        xs = 0.75 - 0.25 * (y1 + 2.6) / 2.97
        parts += [[(-(w - 0.06), y1), (-xs, y1)], [(w - 0.06, y1), (xs, y1)]]
    parts += [L, mirror_x(L)]
    parts += [[(-0.75, -2.6), (-0.5, 0.37)], [(0.75, -2.6), (0.5, 0.37)], [(-0.58, -2.6), (-0.38, 0.37)], [(0.58, -2.6), (0.38, 0.37)]]
    parts += [[(-0.38 - 0.2 * (1 - t), -2.6 + 2.97 * t), (0.38 + 0.2 * (1 - t), -2.6 + 2.97 * t)] for t in [k / 12 for k in range(1, 12)]]
    parts += [poly((-0.95, 0.37), (-0.95, 1.4), (0.95, 1.4), (0.95, 0.37), closed=False), rect(-1.05, 1.4, 1.05, 1.65), rect(-0.7, 1.65, 0.7, 1.85)]
    parts += [rect(-0.7, 0.37, -0.42, 1.0), rect(-0.16, 0.37, 0.16, 1.05), rect(0.42, 0.37, 0.7, 1.0)]
    parts += [ellipse(-0.95, -2.45, 0.22, 0.14, 16), ellipse(0.95, -2.45, 0.22, 0.14, 16)]
    parts += [cloud(-2.3, 2.6, 0.7), cloud(2.4, 2.2, 0.6)] + palm(-3.0, -2.6, 1.3, -0.2) + palm(3.0, -2.6, 1.2, 0.2)
    return make("Chichen Itza Pyramid, Mexico", parts, [eye(-1.03, -2.42, 0.04), eye(0.87, -2.42, 0.04)])


@design("landmarks_moai_head", T)
def moai_head(rng):
    out = chain([(-1.4, -3.0)], cubic((-1.4, -3.0), (-1.4, -2.2), (-1.5, -1.6), (-1.55, -1.2), 8), [(-1.95, -1.0)],
                cubic((-1.95, -1.0), (-2.0, -0.8), (-1.9, -0.65), (-1.8, -0.55), 6), [(-1.88, -0.4), (-1.75, -0.25), (-1.88, -0.12), (-1.7, 0.05), (-2.15, 0.15)],
                cubic((-2.15, 0.15), (-2.25, 0.3), (-2.1, 0.5), (-1.95, 0.9), 8), [(-1.75, 1.55), (-1.98, 1.75), (-1.85, 2.0), (-1.75, 2.6), (-1.6, 2.72), (0.7, 2.75)],
                cubic((0.7, 2.75), (1.0, 2.4), (1.0, 1.2), (0.9, 0.3), 14), cubic((0.9, 0.3), (0.8, -0.4), (0.7, -1.0), (0.9, -1.6), 10), [(1.4, -2.2), (1.5, -3.0)])
    parts = [out, lens((0.15, 1.5), (0.35, -0.4), 0.18), cubic((0.25, 1.3), (0.4, 0.9), (0.4, 0.2), (0.3, -0.2), 8),
             quad((-1.9, 1.7), (-1.3, 1.78), (-1.0, 1.4), 10), quad((-1.75, 1.5), (-1.45, 1.1), (-1.15, 1.2), 8), ellipse(-1.9, 0.27, 0.16, 0.08, 14),
             [(-1.8, -0.25), (-1.25, -0.2)], quad((-1.5, -1.15), (-0.5, -1.0), (0.05, -0.4), 12),
             cubic((0.6, -1.7), (0.2, -2.0), (-0.1, -2.3), (-0.9, -2.45), 12)]
    parts += [[(-0.9 + 0.22 * k, -2.45 + 0.02 * k), (-1.0 + 0.22 * k, -2.85)] for k in range(4)]
    parts += [ground(-3.4, 3.4), [(1.9, -1.4), (3.4, -1.4)], cloud(2.4, 2.2, 0.7), cloud(-2.9, 2.9, 0.4)]
    small = [poly((2.4, -3.0), (2.45, -2.4), (2.4, -1.85), (2.55, -1.75), (2.95, -1.75), (2.95, -2.3), (3.0, -3.0), closed=False),
             [(2.48, -2.0), (2.62, -2.0)], [(2.45, -2.3), (2.6, -2.3)]]
    return make("Easter Island Moai Profile", parts + small)


@design("landmarks_moai_row", T)
def moai_row(rng):
    def moai(cx, y0, s, hat):
        L = [(-0.5, 0.0), (-0.45, 0.8), (-0.42, 0.85), (-0.38, 2.1)]
        top = quad((-0.38, 2.1), (0, 2.22), (0.38, 2.1), 8)
        parts = [chain(L, top, mirror_x(L)[::-1]), [(-0.42, 1.75), (-0.52, 1.7), (-0.52, 1.05), (-0.42, 1.0)], [(0.42, 1.75), (0.52, 1.7), (0.52, 1.05), (0.42, 1.0)],
                 [(-0.33, 1.72), (0.33, 1.72)], poly((-0.08, 1.72), (-0.2, 1.22), (0.2, 1.22), (0.08, 1.72), closed=False), [(-0.2, 1.02), (0.2, 1.02)],
                 [(-0.38, 0.85), (0.38, 0.85)], cubic((-0.45, 0.72), (-0.35, 0.3), (-0.15, 0.25), (-0.02, 0.22), 8), cubic((0.45, 0.72), (0.35, 0.3), (0.15, 0.25), (0.02, 0.22), 8)]
        if hat:
            parts.append(rrect(-0.32, 2.2, 0.32, 2.55, 0.1))
        return [transform(p, dx=cx, dy=y0, s=s) for p in parts]

    parts = [rect(-3.3, -1.6, 3.3, -1.0), [(-3.4, -2.2), (3.4, -2.2)]]
    parts += [[(x, -1.6), (x, -1.0)] for x in (-2.0, -0.7, 0.6, 1.9)] + [[(-3.3, -1.3), (-2.0, -1.3)], [(0.6, -1.3), (1.9, -1.3)]]
    for k, (cx, s, hat) in enumerate([(-2.6, 1.05, False), (-1.3, 1.15, True), (0.0, 1.1, False), (1.3, 1.2, False), (2.6, 1.05, True)]):
        parts += moai(cx, -1.0, s, hat)
    parts += [cloud(-2.0, 2.9, 0.6), cloud(1.6, 3.1, 0.5), wave(-3.4, 3.4, -2.7, 0.06, 6, 80), wave(-3.0, 3.0, -3.1, 0.06, 5, 70)]
    return make("Row of Moai on Easter Island", parts)


@design("landmarks_stonehenge", T)
def stonehenge(rng):
    def up(x0, x1, y0, y1):
        return poly((x0, y1), (x0 - 0.04, y0 + 0.5), (x0 + 0.02, y0), (x1 - 0.02, y0), (x1 + 0.04, y0 + 0.4), (x1, y1), closed=False)

    def stone(x0, x1, y0, y1):
        return poly((x0, y0), (x0 - 0.04, y1 - 0.15), (x0 + 0.12, y1), (x1 - 0.06, y1 + 0.04), (x1 + 0.03, y1 - 0.2), (x1 + 0.04, y0), closed=False)

    def lintel(xa, xb, y):
        return poly((xa - 0.1, y), (xa - 0.06, y + 0.4), (xb + 0.04, y + 0.43), (xb + 0.1, y + 0.03))

    parts = [up(-1.1, -0.45, -2.6, 0.0), up(0.45, 1.1, -2.6, 0.0), lintel(-1.1, 1.1, 0.0)]
    parts += [up(-3.1, -2.65, -1.0, 0.6), up(-2.35, -1.9, -1.0, 0.6), lintel(-3.1, -1.9, 0.6), up(1.9, 2.35, -1.0, 0.6), up(2.65, 3.1, -1.0, 0.6), lintel(1.9, 3.1, 0.6)]
    parts += [stone(-1.65, -1.3, -1.0, 0.1), stone(1.3, 1.65, -1.0, 0.2)]
    parts += [poly((1.4, -2.6), (1.35, -2.25), (3.0, -2.15), (3.2, -2.6), closed=False), poly((-3.0, -2.6), (-2.9, -2.0), (-2.4, -1.95), (-2.3, -2.6), closed=False)]
    parts += [[(-3.4, -2.6), (-3.0, -2.6)], [(-2.3, -2.6), (-1.1, -2.6)], [(1.1, -2.6), (1.4, -2.6)], [(3.2, -2.6), (3.4, -2.6)],
              [(-3.4, -1.0), (-3.1, -1.0)], [(-1.9, -1.0), (-1.65, -1.0)], [(-1.3, -1.0), (-1.1, -1.0)], [(1.1, -1.0), (1.3, -1.0)], [(1.65, -1.0), (1.9, -1.0)],
              [(3.1, -1.0), (3.4, -1.0)]]
    parts += [chain(quad((-3.4, 1.5), (-1.5, 1.8), (-0.6, 1.5), 12), [(0.6, 1.5)], quad((0.6, 1.5), (1.6, 1.8), (3.4, 1.45), 12)), arc(0, 1.5, 0.6, 0, math.pi, 20)]
    parts += [[(0.85 * math.cos(a), 1.5 + 0.85 * math.sin(a)), (1.25 * math.cos(a), 1.5 + 1.25 * math.sin(a))] for a in [math.pi * k / 6 for k in range(1, 6)]]
    parts += [[(x - 0.1, -3.1), (x, -2.85), (x + 0.1, -3.1)] for x in (-2.6, -1.4, 0.2, 1.8, 2.9)]
    return make("Stonehenge at Sunrise", parts)


@design("landmarks_great_wall", T)
def great_wall(rng):
    path = chain(cubic((-3.4, -1.9), (-2.4, -1.4), (-1.9, 0.4), (-1.1, 0.4), 30), cubic((-1.1, 0.4), (-0.3, 0.4), (0.0, -0.6), (0.6, -0.5), 30),
                 cubic((0.6, -0.5), (1.4, -0.4), (1.6, 1.3), (2.3, 1.35), 30), cubic((2.3, 1.35), (2.8, 1.4), (3.0, 1.0), (3.4, 0.95), 14))

    def h(x):
        return 0.75 - 0.35 * (x + 3.4) / 6.8

    towers = [(-2.4, 0.42), (0.6, 0.36), (2.6, 0.3)]
    edges = [-3.4]
    for tx, w in towers:
        edges += [tx - w, tx + w]
    edges.append(3.4)
    parts = []
    for a, b in zip(edges[::2], edges[1::2]):
        n = max(2, int(round((b - a) / 0.1)))
        xs = [a + (b - a) * i / n for i in range(n + 1)]
        parts.append([(x, y_at(path, x)) for x in xs])
        parts.append([(x, y_at(path, x) + h(x) * 0.5) for x in xs])
        topl = []
        for x in xs:
            y = y_at(path, x) + h(x)
            tooth = 0.32 * h(x) if int(round((x + 3.4) / 0.1)) % 4 < 2 else 0.0
            if topl:
                topl.append((x, topl[-1][1]))
            topl.append((x, y + tooth))
        parts.append(topl)
    for tx, w in towers:
        yb = min(y_at(path, tx - w), y_at(path, tx + w)) - 0.05
        H = 2.3 * h(tx)
        parts.append(chain([(tx - w, yb), (tx - w, yb + H)], merlons(tx - w, tx + w, yb + H, 0.3 * h(tx), 3), [(tx + w, yb + H), (tx + w, yb)]))
        parts.append(arch(tx - w * 0.35, tx + w * 0.35, yb + H * 0.4, yb + H * 0.78, True, 6))
        parts.append([(tx - w, yb + H * 0.88), (tx + w, yb + H * 0.88)])
    hills = [cubic((-1.5, 0.3), (-1.4, -1.0), (-2.0, -2.0), (-2.6, -3.2), 14), cubic((-0.6, 0.15), (-0.4, -1.2), (-0.6, -2.4), (-0.3, -3.2), 14),
             cubic((1.6, 0.9), (1.4, -0.4), (1.1, -1.8), (1.3, -3.2), 14), cubic((2.9, 1.15), (3.0, 0.0), (2.8, -1.6), (3.1, -3.2), 14)]
    peaks = chain(quad((-3.4, 1.2), (-2.9, 2.0), (-2.4, 2.4), 6), quad((-2.4, 2.4), (-1.9, 1.6), (-1.4, 1.8), 6), quad((-1.4, 1.8), (-0.8, 3.0), (-0.2, 2.9), 8),
                  quad((-0.2, 2.9), (0.4, 2.0), (0.9, 2.2), 6), quad((0.9, 2.2), (1.5, 3.2), (2.2, 3.3), 8), quad((2.2, 3.3), (2.8, 2.6), (3.4, 2.9), 6))
    parts += hills + [peaks, cypress(-1.6, -3.0, 1.0, 0.32), cypress(2.2, -2.6, 1.0, 0.32), cypress(-3.0, -3.1, 0.8, 0.3)]
    return make("Great Wall of China", parts)


@design("landmarks_forbidden_city", T)
def forbidden_city(rng):
    parts = [ground(-3.4, 3.4, -2.8), poly((-3.2, -2.8), (-3.0, -0.6), (3.0, -0.6), (3.2, -2.8), closed=False), [(-3.0, -0.6), (3.0, -0.6)]]
    parts += [arch(-0.4, 0.4, -2.8, -1.5), arch(-1.35, -0.85, -2.8, -1.8), arch(0.85, 1.35, -2.8, -1.8), arch(-2.25, -1.85, -2.8, -2.05), arch(1.85, 2.25, -2.8, -2.05)]
    parts += [rect(-2.9, -0.6, 2.9, -0.35)] + [[(x, -0.6), (x, -0.35)] for x in [-2.5 + 0.5 * k for k in range(11)]]
    parts += [[(x, -0.35), (x, 0.45)] for x in [-2.0 + 0.5 * k for k in range(9)]] + [[(-2.4, -0.35), (-2.4, 0.45)], [(2.4, -0.35), (2.4, 0.45)]]

    def roof(y, tipw, eave, topy, ridgew):
        L = chain(quad((-tipw, y + 0.3), (-eave, y), (-eave + 0.5, y), 8))
        under = chain(L, mirror_x(L)[::-1])
        top = chain(quad(under[-1], (ridgew + 0.5, y + 0.35), (ridgew, topy), 10), [(-ridgew, topy)],
                    quad((-ridgew, topy), (-ridgew - 0.5, y + 0.35), under[0], 10))
        return [under, top]

    parts += roof(0.45, 3.4, 3.0, 1.15, 2.2)
    parts += [[(-1.9, 1.15), (-1.9, 1.75)], [(1.9, 1.15), (1.9, 1.75)], rect(-1.6, 1.25, 1.6, 1.62)] + [[(x, 1.25), (x, 1.62)] for x in (-0.8, 0.0, 0.8)]
    parts += roof(1.75, 3.0, 2.6, 2.6, 1.7)
    parts += [poly((1.7, 2.6), (1.85, 2.9), (1.6, 2.78), closed=False), poly((-1.7, 2.6), (-1.85, 2.9), (-1.6, 2.78), closed=False)]
    parts += [[(x, 1.85), (x, 2.5)] for x in (-1.2, -0.6, 0.0, 0.6, 1.2)] + [[(x, 0.6), (x, 1.05)] for x in (-1.8, -1.2, -0.6, 0.0, 0.6, 1.2, 1.8)]
    return make("Forbidden City Gate, Beijing", parts)


@design("landmarks_japanese_pagoda", T)
def pagoda(rng):
    parts = [rect(-1.7, -3.0, 1.7, -2.7), ground(-3.4, 3.4, -3.0)]
    y = -2.7
    for i in range(5):
        ww, rw = 1.05 - 0.13 * i, 2.3 - 0.27 * i
        wh = 0.85 if i == 0 else 0.5
        parts += [[(-ww, y), (-ww, y + wh)], [(ww, y), (ww, y + wh)]]
        if i == 0:
            parts.append(rect(-0.3, y, 0.3, y + 0.6))
        else:
            parts.append(rect(-0.2, y + 0.1, 0.2, y + 0.38))
        y += wh
        L = quad((-rw, y + 0.28), (-rw + 0.25, y), (-rw + 0.65, y), 8)
        under = chain(L, mirror_x(L)[::-1])
        top = chain(quad(under[-1], (rw * 0.55, y + 0.15), (rw * 0.45, y + 0.42), 8), [(-rw * 0.45, y + 0.42)],
                    quad((-rw * 0.45, y + 0.42), (-rw * 0.55, y + 0.15), under[0], 8))
        parts += [under, top]
        y += 0.42
    parts += [[(0, y), (0, y + 1.6)]] + [[(-0.2, y + 0.25 + 0.25 * k), (0.2, y + 0.25 + 0.25 * k)] for k in range(5)] + [lens((0, y + 1.6), (0, y + 2.0), 0.35)]
    parts += [cloud(-2.4, 2.4, 0.6), cloud(2.4, 1.2, 0.5), tree(-2.8, -3.0, 1.0), tree(2.8, -3.0, 0.9)]
    return make("Five-Storey Japanese Pagoda", parts)


@design("landmarks_mount_fuji", T)
def mount_fuji(rng):
    ls = cubic((-3.4, 0.05), (-1.6, 0.2), (-0.4, 1.0), (0.1, 1.9), 24)
    rs = cubic((1.5, 1.92), (2.0, 0.8), (2.8, -0.4), (3.4, -0.8), 24)
    parts = [chain(ls, [(0.4, 1.98), (0.6, 1.86), (0.85, 2.0), (1.1, 1.9)], rs)]
    xl, xr = x_at(ls, 0.8), x_at(rs, 0.8)
    n = 8
    snow = [(xl, 0.8)] + [(xl + (xr - xl) * k / n, 0.8 + (-0.3 if k % 2 else 0.05)) for k in range(1, n)] + [(xr, 0.8)]
    parts.append(snow)
    parts += [circle(2.6, 2.7, 0.5, 30)]
    tor = []
    for x in (-2.75, -1.25):
        tor += [rect(x - 0.13, -3.0, x + 0.13, -0.85), rect(x - 0.13, -0.6, x + 0.13, -0.2)]
    kasagi = chain(quad((-0.55, 0.42), (-1.0, 0.22), (-1.5, 0.22), 8), [(-2.5, 0.22)], quad((-2.5, 0.22), (-3.0, 0.22), (-3.45, 0.42), 8),
                   quad((-3.45, 0.42), (-3.1, 0.0), (-2.6, 0.0), 6), [(-1.4, 0.0)], quad((-1.4, 0.0), (-0.9, 0.0), (-0.55, 0.42), 6))
    tor += [kasagi, rect(-3.1, -0.2, -0.9, 0.0), rect(-3.2, -0.85, -0.8, -0.6), rect(-2.1, -0.6, -1.9, -0.2)]
    parts += [transform(p, dx=-0.6, dy=-0.66, s=0.8) for p in tor]
    parts += [[(-3.4, -3.06), (-0.3, -3.06)]] + waves(0.0, 3.4, [-1.6, -2.1, -2.6], 0.05, 0.6)
    parts += [poly((-1.2, 2.4), (-1.0, 2.55), (-0.8, 2.4), closed=False), poly((-0.6, 2.7), (-0.42, 2.82), (-0.24, 2.7), closed=False)]
    return make("Mount Fuji with Torii Gate", parts)


# ---------------------------------------------------------------- occlusion helpers

def _inside(pt, pg):
    x, y = pt
    c = False
    for (x1, y1), (x2, y2) in zip(pg, pg[1:] + pg[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def _dense(pts, step=0.03):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(1, n + 1)]
    return out


def hide(strokes, covers):
    """Remove the parts of `strokes` lying inside any of the `covers` polygons."""
    out = []
    for s in strokes:
        run = []
        for p in _dense(s):
            if any(_inside(p, c) for c in covers):
                if len(run) > 1:
                    out.append(run)
                run = []
            else:
                run.append(p)
        if len(run) > 1:
            out.append(run)
    return out


def eave_roof(y, tipw, eave, topy, ridgew, cx=0.0, lift=0.3):
    """Chinese/Japanese roof with upturned tips: underside + top outline."""
    L = quad((cx - tipw, y + lift), (cx - eave, y), (cx - eave + 0.5, y), 8)
    under = chain(L, mirror_x(L, cx)[::-1])
    top = chain(quad(under[-1], (cx + ridgew + 0.5, y + 0.35), (cx + ridgew, topy), 10), [(cx - ridgew, topy)],
                quad((cx - ridgew, topy), (cx - ridgew - 0.5, y + 0.35), under[0], 10))
    return [under, top]


def pine(cx, y0, s=1.0):
    out = [[(cx - 0.07 * s, y0), (cx - 0.05 * s, y0 + 1.2 * s)], [(cx + 0.07 * s, y0), (cx + 0.05 * s, y0 + 1.2 * s)]]
    out += [ellipse(cx + dx * s, y0 + dy * s, 0.45 * s, 0.17 * s, 24) for dx, dy in ((-0.35, 0.7), (0.4, 1.0), (-0.1, 1.35))]
    return out


# ---------------------------------------------------------------- more landmarks

@design("landmarks_petra_treasury", T)
def petra(rng):
    cliffL = chain([(-3.4, -3.0)], cubic((-3.0, -1.5), (-3.3, 0.5), (-2.9, 1.8), (-3.1, 3.3), 20))
    parts = [cliffL, mirror_x(cliffL), [(-3.1, 3.3), (-2.0, 3.0), (-0.8, 3.35), (0.6, 3.15), (2.0, 3.35), (3.1, 3.3)],
             [(-3.4, -3.0), (3.4, -3.0)], rect(-2.5, -3.0, 2.5, -2.75)]
    for x in (-2.1, -1.3, -0.5, 0.5, 1.3, 2.1):
        parts += [[(x - 0.14, -2.75), (x - 0.14, -0.7)], [(x + 0.14, -2.75), (x + 0.14, -0.7)], rect(x - 0.2, -0.7, x + 0.2, -0.5)]
    parts += [rect(-2.55, -0.5, 2.55, -0.1), poly((-1.6, -0.1), (0, 0.6), (1.6, -0.1), closed=False), poly((-1.2, 0.0), (0, 0.42), (1.2, 0.0), closed=False)]
    parts += [rect(-0.3, -2.75, 0.3, -1.3)]
    for s in (-1, 1):
        parts += [[(s * 2.4, 0.6), (s * 2.4, 1.9)], [(s * 1.25, 0.6), (s * 1.25, 1.9)], [(s * 1.82, 0.6), (s * 1.82, 1.9)],
                  [(s * 2.55, 0.6), (s * 1.1, 0.6)], [(s * 2.55, 1.9), (s * 1.1, 1.9)], [(s * 2.55, 1.9), (s * 2.55, 2.15), (s * 1.1, 2.5)]]
    parts += [[(-0.75, 0.6), (0.75, 0.6)], [(-0.65, 0.6), (-0.65, 1.9)], [(0.65, 0.6), (0.65, 1.9)], [(-0.22, 0.6), (-0.22, 1.9)], [(0.22, 0.6), (0.22, 1.9)],
              rect(-0.8, 1.9, 0.8, 2.15), poly((-0.75, 2.15), (0, 2.6), (0.75, 2.15), closed=False),
              chain(quad((-0.12, 2.6), (-0.3, 2.85), (-0.12, 3.05), 6), [(0.12, 3.05)], quad((0.12, 3.05), (0.3, 2.85), (0.12, 2.6), 6))]
    parts += [ellipse(-1.75, 1.25, 0.15, 0.3, 14), ellipse(1.75, 1.25, 0.15, 0.3, 14)]
    return make("Petra Treasury, Jordan", parts)


@design("landmarks_angkor_wat", T)
def angkor_wat(rng):
    def bud(cx, y0, w, h):
        left = cubic((cx - w, y0), (cx - w * 1.15, y0 + h * 0.5), (cx - w * 0.55, y0 + h * 0.85), (cx, y0 + h), 24)
        out = [chain(left, mirror_x(left, cx)[::-1])]
        for k in range(1, int(h / 0.35)):
            y = y0 + 0.35 * k
            if y > y0 + h * 0.85:
                break
            xl = x_at(left, y)
            out.append([(xl, y), (2 * cx - xl, y)])
        return out + [[(cx, y0 + h), (cx, y0 + h + 0.25)]]

    parts = [rect(-3.3, -1.6, 3.3, -0.95), poly((-3.4, -0.95), (-3.0, -0.6), (3.0, -0.6), (3.4, -0.95), closed=False)]
    parts += [rect(-2.9 + 0.5 * k, -1.5, -2.65 + 0.5 * k, -1.1) for k in range(12)]
    parts += [rect(-1.9, -0.6, 1.9, -0.1), rect(-1.2, -0.1, 1.2, 0.3)]
    parts += bud(0, 0.3, 0.55, 2.4) + bud(-1.5, -0.1, 0.38, 1.6) + bud(1.5, -0.1, 0.38, 1.6) + bud(-2.6, -0.6, 0.3, 1.2) + bud(2.6, -0.6, 0.3, 1.2)
    parts += [[(-3.4, -1.6), (3.4, -1.6)]] + waves(-3.2, 3.2, [-2.1, -2.6], 0.05, 0.6)
    parts += waves(-3.0, 3.0, [-3.1], 0.05, 0.6)
    return make("Angkor Wat, Cambodia", parts)


@design("landmarks_hagia_sophia", T)
def hagia_sophia(rng):
    parts = [ground(-3.4, 3.4, -2.8), rect(-1.9, -2.8, 1.9, 0.0)]
    parts += [arch(x, x + 0.35, -2.3, -1.4, True, 8) for x in (-1.6, -0.9, 0.55, 1.25)] + [arch(-0.35, 0.35, -2.8, -1.6)]
    parts += [arch(x, x + 0.3, -1.0, -0.4, True, 8) for x in (-1.55, -0.95, -0.15, 0.65, 1.25)]
    parts += [arc(-1.3, 0.0, 0.6, math.pi, math.pi / 2, 10), arc(1.3, 0.0, 0.6, 0, math.pi / 2, 10)]
    parts += [rect(-1.3, 0.6, 1.3, 1.1)] + [arch(-1.15 + 0.32 * k, -0.97 + 0.32 * k, 0.7, 1.0) for k in range(8)]
    parts += [arc(0, 1.1, 1.3, 0, math.pi, 40), [(0, 2.4), (0, 2.85)], arc(0, 2.95, 0.12, -0.6, math.pi + 0.6, 8)]
    for x in (-3.0, -2.3, 2.3, 3.0):
        parts += [poly((x - 0.15, -2.8), (x - 0.12, 1.5), (x + 0.12, 1.5), (x + 0.15, -2.8), closed=False), [(x - 0.25, 0.2), (x + 0.25, 0.2)],
                  [(x - 0.22, 1.5), (x + 0.22, 1.5)], poly((x - 0.13, 1.5), (x, 2.7), (x + 0.13, 1.5), closed=False)]
    return make("Hagia Sophia, Istanbul", parts + [cloud(-2.0, 3.0, 0.5)])


@design("landmarks_gateway_arch", T)
def gateway_arch(rng):
    def cat(w, H, base):
        c = 1.4
        return [(x, base + H * (1 - (math.cosh(x / c) - 1) / (math.cosh(w / c) - 1))) for x in [-w + 2 * w * i / 60 for i in range(61)]]

    parts = [cat(2.7, 5.2, -2.6), cat(2.25, 4.75, -2.6)]
    parts += [[(-2.7, -2.6), (-2.25, -2.6)], [(2.25, -2.6), (2.7, -2.6)]]
    parts += [rect(-0.8, -2.6, 0.8, -1.6), rect(-0.95, -1.6, 0.95, -1.45), rect(-0.35, -1.45, 0.35, -1.05), dome(0, -1.05, 0.35, 12), [(0, -0.7), (0, -0.4)]]
    parts += [arch(-0.15, 0.15, -2.6, -2.1), rect(-0.6, -2.2, -0.4, -1.8), rect(0.4, -2.2, 0.6, -1.8)]
    parts += [[(-3.4, -2.6), (-2.7, -2.6)], [(-2.25, -2.6), (-0.8, -2.6)], [(0.8, -2.6), (2.25, -2.6)], [(2.7, -2.6), (3.4, -2.6)]]
    parts += waves(-3.4, 3.4, [-3.0, -3.35], 0.05, 0.6) + [tree(-1.5, -2.6, 0.8), tree(1.5, -2.6, 0.8), tree(-3.1, -2.6, 0.9), tree(3.1, -2.6, 0.9)]
    return make("Gateway Arch, St. Louis", parts + [cloud(-2.3, 2.2, 0.6), cloud(2.4, 1.4, 0.55)])


@design("landmarks_mount_rushmore", T)
def mount_rushmore(rng):
    parts, hints = [], []

    def face(cx, cy, s, glasses=False, beard=False):
        out = [ellipse(cx, cy, 0.52 * s, 0.75 * s, 50)]
        out += [quad((cx - 0.38 * s, cy + 0.22 * s), (cx - 0.2 * s, cy + 0.35 * s), (cx - 0.05 * s, cy + 0.22 * s), 6),
                quad((cx + 0.05 * s, cy + 0.22 * s), (cx + 0.2 * s, cy + 0.35 * s), (cx + 0.38 * s, cy + 0.22 * s), 6),
                lens((cx - 0.33 * s, cy + 0.08 * s), (cx - 0.08 * s, cy + 0.08 * s), 0.25), lens((cx + 0.08 * s, cy + 0.08 * s), (cx + 0.33 * s, cy + 0.08 * s), 0.25),
                [(cx, cy + 0.15 * s), (cx - 0.08 * s, cy - 0.25 * s), (cx + 0.08 * s, cy - 0.27 * s)], [(cx - 0.18 * s, cy - 0.45 * s), (cx + 0.18 * s, cy - 0.45 * s)],
                [(cx - 0.3 * s, cy - 0.68 * s), (cx - 0.3 * s, cy - 1.15 * s)], [(cx + 0.3 * s, cy - 0.68 * s), (cx + 0.3 * s, cy - 1.15 * s)],
                quad((cx - 0.45 * s, cy + 0.42 * s), (cx, cy + 0.75 * s), (cx + 0.45 * s, cy + 0.42 * s), 10)]
        if glasses:
            out += [circle(cx - 0.2 * s, cy + 0.08 * s, 0.15 * s, 14), circle(cx + 0.2 * s, cy + 0.08 * s, 0.15 * s, 14),
                    quad((cx - 0.25 * s, cy - 0.32 * s), (cx, cy - 0.25 * s), (cx + 0.25 * s, cy - 0.32 * s), 6)]
        if beard:
            out += [quad((cx - 0.48 * s, cy - 0.25 * s), (cx, cy - 1.05 * s), (cx + 0.48 * s, cy - 0.25 * s), 14)]
        hints.extend([eye(cx - 0.2 * s, cy + 0.08 * s, 0.04), eye(cx + 0.2 * s, cy + 0.08 * s, 0.04)])
        return out

    parts += face(-2.1, 0.45, 1.2) + face(-0.9, 0.95, 1.0) + face(0.2, 0.35, 0.9, glasses=True) + face(1.5, 0.45, 1.15, beard=True)
    rock = [(-3.4, -1.2), (-3.2, 0.8), (-2.8, 1.5), (-2.0, 1.9), (-1.3, 2.3), (-0.4, 2.2), (0.3, 1.6), (1.0, 1.75), (1.8, 1.65), (2.5, 1.2), (3.0, 0.6), (3.4, -0.6)]
    parts += [rock, cubic((-3.4, -1.6), (-1.5, -1.0), (0.8, -1.3), (3.4, -1.0), 30)]
    parts += [ellipse(-2.6, -1.85, 0.3, 0.15, 14), ellipse(-0.4, -1.75, 0.25, 0.12, 14), ellipse(2.0, -1.65, 0.3, 0.14, 14)]
    for x in (-3.0, -2.2, -1.4, -0.6, 0.2, 1.0, 1.8, 2.6, 3.2):
        h = 0.9 + 0.3 * ((x * 7) % 1.0)
        parts.append(poly((x - 0.3, -3.1), (x, -3.1 + h), (x + 0.3, -3.1), closed=False))
    return make("Mount Rushmore", parts, hints)


@design("landmarks_tokyo_tower", T)
def tokyo_tower(rng):
    leg = cubic((-2.0, -2.2), (-1.4, -1.4), (-0.8, -0.6), (-0.6, 0.0), 14)
    upper = cubic((-0.45, 0.55), (-0.35, 1.3), (-0.2, 2.0), (-0.16, 2.45), 12)
    parts = [leg, mirror_x(leg), upper, mirror_x(upper), arc(0, -2.2, 0.8, 0, math.pi, 16),
             rect(-0.9, 0.0, 0.9, 0.55), [(-0.9, 0.28), (0.9, 0.28)], rect(-0.32, 2.45, 0.32, 2.75), [(0, 2.75), (0, 4.2)],
             [(-0.12, 3.3), (0.12, 3.3)], [(-0.1, 3.8), (0.1, 3.8)]]
    for y in (-1.5, -0.8):
        xl = x_at(leg, y)
        parts.append([(xl, y), (-xl, y)])
    zx = [(x_at(leg, y) if k % 2 == 0 else -x_at(leg, y), y) for k, y in enumerate([-1.5, -1.15, -0.8, -0.4, 0.0])]
    parts.append(zx)
    for y in (1.0, 1.5, 2.0):
        xl = x_at(upper, y)
        parts.append([(xl, y), (-xl, y)])
    parts.append([(x_at(upper, 0.6), 0.6), (-x_at(upper, 1.0), 1.0), (x_at(upper, 1.5), 1.5), (-x_at(upper, 2.0), 2.0), (x_at(upper, 2.4), 2.4)])
    parts += [rect(-3.0, -3.0, 3.0, -2.2)] + windows(-3.0, -0.8, -2.95, -2.25, 4, 1, 0.5, 0.5) + windows(0.8, 3.0, -2.95, -2.25, 4, 1, 0.5, 0.5)
    parts += [ground(-3.4, 3.4), cloud(-2.3, 2.2, 0.7), cloud(2.3, 1.2, 0.6)]
    return make("Tokyo Tower", parts)


@design("landmarks_lotus_temple", T)
def lotus_temple(rng):
    def petal(bl, br, tip, b=0.35):
        dl = (tip[0] - bl[0], tip[1] - bl[1])
        dr = (tip[0] - br[0], tip[1] - br[1])
        left = cubic(bl, (bl[0] + dl[0] * 0.3 - dl[1] * b, bl[1] + dl[1] * 0.3 + dl[0] * b), (tip[0] - dl[0] * 0.25 - dl[1] * b * 0.6, tip[1] - dl[1] * 0.25 + dl[0] * b * 0.6), tip, 18)
        right = cubic(tip, (tip[0] - dr[0] * 0.25 + dr[1] * b * 0.6, tip[1] - dr[1] * 0.25 - dr[0] * b * 0.6), (br[0] + dr[0] * 0.3 + dr[1] * b, br[1] + dr[1] * 0.3 - dr[0] * b), br, 18)
        return chain(left, right)

    y = -0.6
    layers = [[petal((-0.6, y), (0.6, y), (0, 2.9)), petal((-1.5, y), (-0.2, y), (-1.0, 2.4)), petal((0.2, y), (1.5, y), (1.0, 2.4))],
              [petal((-1.1, y), (0.1, y), (-0.5, 1.8), 0.3), petal((-0.1, y), (1.1, y), (0.5, 1.8), 0.3), petal((-2.2, y), (-0.9, y), (-1.75, 1.4), 0.3),
               petal((0.9, y), (2.2, y), (1.75, 1.4), 0.3)],
              [petal((-0.7, y), (0.7, y), (0, 0.9), 0.3), petal((-1.6, y), (-0.4, y), (-1.3, 0.75), 0.3), petal((0.4, y), (1.6, y), (1.3, 0.75), 0.3),
               petal((-2.6, y), (-1.3, y), (-2.4, 0.5), 0.3), petal((1.3, y), (2.6, y), (2.4, 0.5), 0.3),
               petal((-3.3, y), (-2.2, y), (-3.3, 0.0), 0.25), petal((2.2, y), (3.3, y), (3.3, 0.0), 0.25)]]
    parts = []
    for lay in layers:
        covers = [p + [p[0]] for p in lay]
        parts = hide(parts, covers) + lay
    parts += [rect(-3.4, -1.0, 3.4, -0.6), rect(-3.0, -1.4, 3.0, -1.0), [(-0.6, -1.4), (-0.9, -2.4)], [(0.6, -1.4), (0.9, -2.4)],
              [(-0.75, -1.9), (0.75, -1.9)], [(-3.4, -2.4), (3.4, -2.4)]]
    parts += [poly((-3.2, -2.6), (-1.2, -2.6), (-1.4, -3.2), (-3.4, -3.2)), poly((3.2, -2.6), (1.2, -2.6), (1.4, -3.2), (3.4, -3.2))]
    return make("Lotus Temple, New Delhi", parts)


@design("landmarks_alhambra_lions", T)
def alhambra(rng):
    back = [[(-3.4, -2.0), (3.4, -2.0)]]
    xs = [-3.2 + 1.28 * k for k in range(6)]
    for a, b in zip(xs, xs[1:]):
        cx, r = (a + b) / 2, (b - a) / 2 - 0.12
        pts = [(cx + (r - 0.07 * abs(math.sin(7 * t))) * math.cos(t), 0.4 + (r - 0.07 * abs(math.sin(7 * t))) * math.sin(t))
               for t in [math.pi * i / 70 for i in range(71)]]
        back.append(chain([(cx + r, -2.0)], [(cx + r, 0.4)], pts[1:], [(cx - r, -2.0)]))
    back += [[(x, -2.0), (x, 0.55)] for x in xs[1:-1]] + [rect(x - 0.18, 0.55, x + 0.18, 0.75) for x in xs[1:-1]]
    back += [[(-3.4, 1.3), (3.4, 1.3)], [(-3.4, 2.2), (3.4, 2.2)]]
    back += [[(-3.2 + 0.4 * k, 1.3), (-3.0 + 0.4 * k, 1.75), (-3.2 + 0.4 * k, 2.2)] for k in range(17)]
    back += [[(-3.4, 2.2), (-3.2, 2.6), (3.2, 2.6), (3.4, 2.2)]] + [[(x, 2.2), (x + 0.1, 2.6)] for x in [-2.8 + 0.5 * k for k in range(12)]]
    basin = ellipse(0, -1.35, 1.4, 0.3, 50)
    ped = poly((-0.35, -1.6), (-0.3, -2.3), (0.3, -2.3), (0.35, -1.6))
    bowl = ellipse(0, -0.6, 0.5, 0.12, 30)
    cover = [basin, ped, [(-1.4, -1.4), (-0.3, -2.4), (0.3, -2.4), (1.4, -1.4), (1.4, -1.0), (-1.4, -1.0)],
             [(-0.6, -0.65), (0.6, -0.65), (0.6, 0.2), (-0.6, 0.2)]]
    lions = []
    for x in (-1.6, -0.75, 0.75, 1.6):
        lions += [star(x, -2.35, 0.3, 9, 0.75), circle(x, -2.38, 0.17, 14), [(x - 0.05, -2.45), (x, -2.5), (x + 0.05, -2.45)]]
        cover.append(star(x, -2.35, 0.3, 9, 0.75))
    parts = hide(back, cover) + [basin, ped, bowl, [(-0.1, -1.05), (-0.1, -0.72)], [(0.1, -1.05), (0.1, -0.72)],
                                 quad((0, -0.48), (-0.3, 0.2), (-0.6, -0.6), 8), quad((0, -0.48), (0.3, 0.2), (0.6, -0.6), 8), [(0, -0.48), (0, 0.1)]] + lions
    parts += [[(-3.4, -2.6), (-1.85, -2.6)], [(1.85, -2.6), (3.4, -2.6)], [(-1.35, -2.6), (-1.0, -2.6)], [(1.0, -2.6), (1.35, -2.6)], [(-0.5, -2.6), (0.5, -2.6)]]
    return make("Court of the Lions, Alhambra", parts)


@design("landmarks_kremlin_tower", T)
def kremlin(rng):
    def swallow(x0, x1, y, h, n):
        w = (x1 - x0) / n
        pts = [(x0, y)]
        for k in range(n):
            a = x0 + k * w + 0.1 * w
            b = a + 0.6 * w
            pts += [(a, y), (a, y + h), ((a + b) / 2, y + h - 0.18), (b, y + h), (b, y)]
        return pts + [(x1, y)]

    parts = [ground(-3.4, 3.4), [(-3.4, -3.0), (-3.4, -1.4)], [(3.4, -3.0), (3.4, -1.4)],
             swallow(-3.4, -0.9, -1.4, 0.45, 4), swallow(0.9, 3.4, -1.4, 0.45, 4)]
    parts += [poly((-0.9, -3.0), (-0.9, -0.2), (0.9, -0.2), (0.9, -3.0), closed=False), arch(-0.45, 0.45, -3.0, -1.5)]
    parts += [poly((-0.75, -0.2), (-0.75, 1.0), (0.75, 1.0), (0.75, -0.2), closed=False), circle(0, 0.4, 0.45, 36), circle(0, 0.4, 0.33, 30),
              [(0, 0.4), (0, 0.68)], [(0, 0.4), (0.2, 0.3)]]
    for s in (-1, 1):
        parts += [poly((s * 0.9, -0.2), (s * 0.9, 0.15), (s * 0.82, 0.55), (s * 0.74, 0.15), closed=False),
                  poly((s * 0.75, 1.0), (s * 0.75, 1.3), (s * 0.66, 1.65), (s * 0.57, 1.3), closed=False)]
    parts += [poly((-0.55, 1.0), (-0.55, 1.85), (0.55, 1.85), (0.55, 1.0), closed=False)] + [arch(x - 0.12, x + 0.12, 1.15, 1.7) for x in (-0.25, 0.25)]
    parts += [[(-0.65, 1.85), (0.65, 1.85)], poly((-0.55, 1.85), (-0.06, 3.35), (0.06, 3.35), (0.55, 1.85), closed=False), [(0, 3.35), (0, 3.45)],
              star(0, 3.8, 0.38, 5, 0.42), [(-0.3, 2.35), (0.3, 2.35)], [(-0.2, 2.75), (0.2, 2.75)]]
    parts += [[(-2.8, -2.0), (-1.6, -2.0)], [(1.6, -2.0), (2.8, -2.0)]]
    return make("Kremlin Spasskaya Tower, Moscow", parts + [cloud(-2.3, 2.4, 0.6), cloud(2.3, 1.6, 0.55)])


@design("landmarks_niagara_falls", T)
def niagara(rng):
    brink = [(x, 0.15 + 0.5 * math.cos(x / 3.4 * math.pi / 2) ** 2) for x in [-3.0 + 6.0 * i / 50 for i in range(51)]]
    parts = [brink, [(-3.4, 0.5), (-3.0, y_at(brink, -3.0)), (-3.2, -0.6), (-3.05, -1.1)], [(3.4, 0.5), (3.0, y_at(brink, 3.0)), (3.2, -0.6), (3.05, -1.1)]]
    for x in [-2.7 + 0.45 * k for k in range(13)]:
        y0 = y_at(brink, x)
        parts.append(cubic((x, y0), (x + 0.05, y0 - 0.8), (x - 0.05, -0.6), (x + 0.02, -1.2), 10))
    parts += [cloud(-2.5, -1.3, 0.8), cloud(-0.9, -1.25, 0.9), cloud(0.8, -1.3, 0.85), cloud(2.5, -1.25, 0.8)]
    parts += [wave(-3.0, 3.0, 1.2, 0.05, 6, 80), wave(-2.6, 2.6, 1.7, 0.05, 5, 70)]
    parts += [[(-3.4, 2.2), (-2.0, 2.2)], [(2.0, 2.3), (3.4, 2.3)], tree(-2.6, 2.2, 0.8), tree(2.7, 2.3, 0.8)]
    boat = [poly((-1.0, -2.3), (-0.7, -2.7), (1.1, -2.7), (1.5, -2.25)),
            rect(-0.6, -2.3, 0.9, -1.9), rect(-0.35, -1.9, 0.6, -1.65)] + windows(-0.6, 0.9, -2.25, -1.95, 4, 1, 0.5, 0.6)
    parts += boat + waves(-3.4, 3.4, [-2.9, -3.3], 0.05, 0.6)
    return make("Niagara Falls", parts)


@design("landmarks_grand_canyon", T)
def grand_canyon(rng):
    far = [(-3.4, 1.4), (-2.4, 1.4), (-2.3, 1.55), (-0.6, 1.55), (-0.5, 1.4), (1.4, 1.4), (1.5, 1.6), (3.4, 1.6)]
    b1 = [(-2.4, -0.2), (-1.9, 0.5), (-1.7, 0.6), (-1.6, 1.1), (-0.4, 1.1), (-0.25, 0.6), (0.1, 0.45), (0.4, -0.2)]
    b2 = [(0.7, -0.4), (1.1, 0.3), (1.3, 0.4), (1.45, 0.9), (2.0, 0.95), (2.15, 0.4), (2.6, 0.2), (2.9, -0.4)]
    left = [(-3.4, 0.2), (-2.6, 0.2), (-2.4, -0.6), (-2.0, -0.8), (-1.8, -1.6), (-1.2, -1.9), (-1.0, -2.6), (-0.6, -2.8), (-0.5, -3.3)]
    right = [(3.4, -0.4), (2.6, -0.5), (2.4, -1.2), (1.9, -1.4), (1.7, -2.2), (1.1, -2.5), (0.7, -2.8), (0.8, -3.3)]
    parts = [far, b1, b2, left, right, [(-1.65, 0.75), (-0.3, 0.75)], [(1.25, 0.6), (2.1, 0.6)], [(-2.0, 0.2), (0.15, 0.2)], [(1.0, 0.0), (2.75, 0.0)]]
    parts += [[(-3.4, -0.6), (-2.4, -0.6)], [(-3.4, -1.6), (-1.8, -1.6)], [(-3.4, -2.6), (-1.0, -2.6)],
              [(3.4, -1.2), (2.4, -1.2)], [(3.4, -2.2), (1.7, -2.2)]]
    parts += [wave(-0.55, 0.75, -3.0, 0.05, 1.5, 20)]
    parts += [circle(2.5, 2.6, 0.45, 30), poly((-1.6, 2.6), (-1.3, 2.75), (-1.0, 2.6), closed=False), poly((-0.8, 2.3), (-0.55, 2.42), (-0.3, 2.3), closed=False)]
    return make("Grand Canyon, Arizona", parts)


@design("landmarks_golden_pavilion", T)
def golden_pavilion(rng):
    parts = [[(-3.4, -1.4), (3.4, -1.4)]]
    parts += [[(-2.0, -1.4), (-2.0, -0.55)], [(2.0, -1.4), (2.0, -0.55)]] + [[(x, -1.4), (x, -0.55)] for x in (-1.2, -0.4, 0.4, 1.2)]
    parts += [[(-2.0, -1.0), (2.0, -1.0)]]
    parts += eave_roof(-0.55, 2.7, 2.4, -0.1, 1.6)
    parts += [[(-1.6, -0.1), (-1.6, 0.7)], [(1.6, -0.1), (1.6, 0.7)], [(-1.8, 0.15), (1.8, 0.15)]] + [[(x, -0.1), (x, 0.15)] for x in (-1.2, -0.6, 0.0, 0.6, 1.2)]
    parts += [rect(-1.2, 0.25, -0.3, 0.6), rect(0.3, 0.25, 1.2, 0.6)]
    parts += eave_roof(0.7, 2.3, 2.0, 1.1, 1.0)
    parts += [[(-1.0, 1.1), (-1.0, 1.75)], [(1.0, 1.1), (1.0, 1.75)], gothic(-0.7, -0.25, 1.2, 1.65, True), gothic(0.25, 0.7, 1.2, 1.65, True)]
    parts += eave_roof(1.75, 1.8, 1.5, 2.55, 0.12)
    parts += [poly((-0.05, 2.55), (-0.2, 2.75), (-0.05, 2.7), (0.0, 2.95), (0.1, 2.75), (0.3, 2.8), (0.12, 2.55), closed=False)]
    parts += [[(-2.6, -1.9), (2.6, -1.9)], [(-2.0, -2.3), (2.0, -2.3)], [(-1.4, -2.7), (1.4, -2.7)], [(-0.6, -3.1), (0.6, -3.1)]]
    parts += pine(-2.9, -1.4, 1.1) + pine(2.9, -1.4, 0.9) + [ellipse(2.4, -2.6, 0.5, 0.2, 20), ellipse(-2.6, -2.9, 0.4, 0.15, 16)]
    return make("Golden Pavilion, Kyoto", parts)


@design("landmarks_hoover_dam", T)
def hoover_dam(rng):
    top = quad((-2.0, 1.0), (0.0, 0.7), (2.2, 1.1), 30)
    base = quad((-1.3, -1.7), (0.0, -2.0), (1.4, -1.7), 30)
    parts = [top, base, [(-2.0, 1.0), (-1.3, -1.7)], [(2.2, 1.1), (1.4, -1.7)], quad((-2.0, 1.2), (0.0, 0.9), (2.2, 1.3), 30)]
    for t in (0.25, 0.5, 0.75):
        xl, yl = -2.0 + 0.7 * t, 1.0 - 2.7 * t
        xr, yr = 2.2 - 0.8 * t, 1.1 - 2.8 * t
        parts.append(quad((xl, yl), (0.0, (yl + yr) / 2 - 0.3), (xr, yr), 24))
    for x in (-1.2, -0.4, 0.5, 1.3):
        parts += [rect(x - 0.15, 1.2, x + 0.15, 1.75), arc(x, 1.75, 0.15, 0, math.pi, 8)]
    parts += [rect(-1.6, -2.6, 1.7, -1.95)] + windows(-1.6, 1.7, -2.5, -2.05, 6, 1, 0.45, 0.55)
    wallL = [(-3.4, 2.4), (-2.6, 2.2), (-2.3, 1.4), (-2.0, 1.0), (-1.7, -0.6), (-1.5, -1.4), (-1.9, -2.0), (-2.2, -2.7), (-2.0, -3.3)]
    wallR = [(3.4, 2.5), (2.8, 2.3), (2.5, 1.6), (2.2, 1.1), (1.9, -0.4), (1.6, -1.4), (2.0, -2.0), (2.4, -2.8), (2.2, -3.3)]
    parts += [wallL, wallR, [(-3.4, 0.4), (-2.8, 0.9)], [(3.4, 0.2), (2.8, 0.6)], [(-3.4, -1.6), (-2.6, -1.2)], [(3.4, -1.6), (2.7, -1.0)]]
    parts += [wave(-2.3, 2.5, 2.0, 0.05, 4, 50), wave(-1.9, 2.0, -2.95, 0.05, 3, 40)]
    return make("Hoover Dam, Nevada", parts)


@design("landmarks_chrysler_building", T)
def chrysler(rng):
    L = [(-1.0, -3.0), (-1.0, 0.6), (-0.75, 0.6), (-0.75, 1.2)]
    parts = [L, mirror_x(L)]
    rs = [0.75, 0.62, 0.5, 0.38, 0.27]
    ys = [1.2, 1.6, 1.95, 2.28, 2.58]
    for k, (r, y) in enumerate(zip(rs, ys)):
        parts.append(arc(0, y, r, 0, math.pi, 24))
        if k + 1 < len(rs):
            parts += [[(r, y), (rs[k + 1], ys[k + 1])], [(-r, y), (-rs[k + 1], ys[k + 1])]]
        for a in (0.45, 0.95, 1.57, 2.19, 2.69):
            parts.append(poly((r * 0.85 * math.cos(a), y + r * 0.85 * math.sin(a)), (r * 0.55 * math.cos(a - 0.12), y + r * 0.55 * math.sin(a - 0.12)),
                              (r * 0.55 * math.cos(a + 0.12), y + r * 0.55 * math.sin(a + 0.12))) if r > 0.45 else [])
    parts = [p for p in parts if p]
    parts += [[(-0.27, 2.58), (-0.06, 3.0)], [(0.27, 2.58), (0.06, 3.0)], [(-0.06, 3.0), (0, 4.3), (0.06, 3.0)]]
    parts += [[(x, -2.6), (x, 0.4)] for x in (-0.6, -0.2, 0.2, 0.6)] + [rect(-0.3, -3.0, 0.3, -2.6)]
    parts += [lens((-1.0, 0.6), (-1.45, 0.55), 0.3), lens((1.0, 0.6), (1.45, 0.55), 0.3)]
    parts += [rect(-3.2, -3.0, -1.8, -0.9), rect(1.8, -3.0, 3.2, -1.6), poly((-1.75, -3.0), (-1.75, -1.6), (-1.15, -1.6), (-1.15, -3.0), closed=False)]
    parts += windows(-3.2, -1.8, -2.9, -1.0, 3, 4, 0.45, 0.45) + windows(1.8, 3.2, -2.9, -1.7, 3, 3, 0.45, 0.45)
    parts += [ground(-3.4, 3.4), cloud(-2.3, 2.3, 0.7), cloud(2.3, 1.3, 0.6)]
    return make("Chrysler Building, New York", parts)


@design("landmarks_notre_dame", T)
def notre_dame(rng):
    parts = [ground(-3.4, 3.4, -3.0), [(-0.4, 1.2), (-0.3, 3.4), (-0.2, 1.2)]]
    parts = [parts[0], [(0, 1.2), (0, 3.6)], [(-0.25, 1.2), (0, 2.0), (0.25, 1.2)]]
    for s in (-1, 1):
        x0, x1 = sorted((s * 0.95, s * 2.4))
        parts += [rect(x0, -3.0, x1, 2.2), merlons(x0, x1, 2.2, 0.15, 4)[1:-1]]
        cx = (x0 + x1) / 2
        parts += [gothic(cx - 0.45, cx - 0.08, 0.7, 1.9, True), gothic(cx + 0.08, cx + 0.45, 0.7, 1.9, True), gothic(cx - 0.45, cx + 0.45, -3.0, -1.3, n=10)]
        parts += [circle(cx, 0.15, 0.25, 18)]
    parts += [[(-0.95, 1.2), (0.95, 1.2)], [(-0.95, 1.0), (0.95, 1.0)]] + [[(x, 1.0), (x, 1.2)] for x in (-0.6, -0.2, 0.2, 0.6)]
    parts += [circle(0, 0.25, 0.65, 50), circle(0, 0.25, 0.22, 20)]
    parts += [[(0.22 * math.cos(a), 0.25 + 0.22 * math.sin(a)), (0.65 * math.cos(a), 0.25 + 0.65 * math.sin(a))] for a in [k * TAU / 12 for k in range(12)]]
    parts += [[(-2.4, -0.8), (2.4, -0.8)], [(-2.4, -0.45), (2.4, -0.45)]] + [arch(-2.25 + 0.4 * k, -2.05 + 0.4 * k, -0.8, -0.5) for k in range(12)]
    parts += [gothic(-0.65, 0.65, -3.0, -1.1, n=10), gothic(-0.45, 0.45, -3.0, -1.5, n=8)]
    return make("Notre-Dame Cathedral, Paris", parts)


@design("landmarks_uluru", T)
def uluru(rng):
    rock = chain(cubic((-3.3, -1.2), (-3.1, -0.3), (-2.8, 0.6), (-2.2, 0.75), 12), cubic((-2.2, 0.75), (-1.0, 1.05), (1.0, 0.95), (2.4, 0.6), 30),
                 cubic((2.4, 0.6), (2.9, 0.4), (3.2, -0.4), (3.35, -1.2), 12))
    parts = [rock, [(-3.4, -1.2), (3.4, -1.2)]]
    for x in (-2.2, -1.5, -0.8, -0.1, 0.6, 1.3, 2.0, 2.6):
        yt = y_at(rock, x) - 0.12
        parts.append(cubic((x, yt), (x - 0.15, yt - 0.5), (x + 0.15, -0.6), (x - 0.05, -1.05), 10))
    parts += [ellipse(-1.2, -0.35, 0.25, 0.15, 16), ellipse(1.7, -0.5, 0.2, 0.12, 14)]
    parts += [circle(2.4, 2.3, 0.55, 36)] + [[(2.4 + 0.75 * math.cos(a), 2.3 + 0.75 * math.sin(a)), (2.4 + 1.05 * math.cos(a), 2.3 + 1.05 * math.sin(a))]
                                            for a in [k * TAU / 10 for k in range(10)]]
    for x, y in ((-2.8, -2.0), (-1.5, -2.6), (0.0, -1.9), (1.4, -2.7), (2.7, -2.1), (-0.6, -3.1)):
        parts.append([(x - 0.3, y + 0.15), (x - 0.1, y - 0.15), (x, y + 0.25), (x + 0.1, y - 0.15), (x + 0.3, y + 0.15)])
    parts += [cloud(-2.2, 2.3, 0.6)]
    return make("Uluru, Australia", parts)


@design("landmarks_sacre_coeur", T)
def sacre_coeur(rng):
    def ovo(cx, y0, w, h):
        left = cubic((cx - w, y0), (cx - w * 1.15, y0 + h * 0.6), (cx - w * 0.45, y0 + h), (cx, y0 + h), 20)
        return chain(left, mirror_x(left, cx)[::-1])

    parts = [rect(-0.85, 0.4, 0.85, 1.2)] + [[(x, 0.4), (x, 1.2)] for x in (-0.55, -0.2, 0.2, 0.55)]
    parts += [ovo(0, 1.2, 0.85, 1.4), rect(-0.18, 2.6, 0.18, 3.0), ovo(0, 3.0, 0.2, 0.3), [(0, 3.3), (0, 3.65)], [(-0.12, 3.5), (0.12, 3.5)]]
    parts += [rect(-1.3, -1.6, 1.3, 0.4), rect(-1.4, 0.4, 1.4, 0.5)]
    parts.remove(parts[-1])
    parts += [arch(x - 0.28, x + 0.28, -1.6, -0.5) for x in (-0.75, 0.0, 0.75)] + [[(-1.3, -0.2), (1.3, -0.2)]]
    parts += [arch(x - 0.12, x + 0.12, 0.0, 0.3, True, 6) for x in (-0.8, -0.4, 0.0, 0.4, 0.8)]
    for s in (-1, 1):
        cx = s * 1.75
        parts += [poly((cx - 0.45, -1.6), (cx - 0.45, 0.2), (cx + 0.45, 0.2), (cx + 0.45, -1.6), closed=False), ovo(cx, 0.2, 0.42, 0.7),
                  [(cx, 0.9), (cx, 1.15)], arch(cx - 0.15, cx + 0.15, -1.0, -0.3, True, 6)]
    parts += [poly((2.3, -1.6), (2.3, 1.8), (3.0, 1.8), (3.0, -1.6), closed=False), ovo(2.65, 1.8, 0.35, 0.6), [(2.65, 2.4), (2.65, 2.7)],
              arch(2.5, 2.8, 0.9, 1.5, True, 6)]
    parts += [[(-3.0, -1.6), (3.2, -1.6)], [(-1.0, -1.6), (-1.6, -3.2)], [(1.0, -1.6), (1.6, -3.2)]]
    parts += [[(-1.0 - 0.6 * t, -1.6 - 1.6 * t), (1.0 + 0.6 * t, -1.6 - 1.6 * t)] for t in (0.25, 0.5, 0.75)]
    parts += [tree(-2.7, -3.0, 1.2), tree(2.8, -3.0, 1.0)]
    return make("Sacre-Coeur Basilica, Montmartre", parts)


@design("landmarks_temple_of_heaven", T)
def temple_of_heaven(rng):
    parts = []
    for k, (w, y0) in enumerate([(3.2, -3.0), (2.6, -2.55), (2.0, -2.1)]):
        parts += [rect(-w, y0, w, y0 + 0.45)] + [[(x, y0 + 0.2), (x, y0 + 0.45)] for x in [-w + 0.4 * i for i in range(1, int(2 * w / 0.4))]]
    parts += [[(-1.5, -1.65), (-1.5, -0.6)], [(1.5, -1.65), (1.5, -0.6)]] + [[(x, -1.65), (x, -0.6)] for x in (-0.9, -0.3, 0.3, 0.9)]
    parts += [quad((-1.5, -0.95), (0, -0.85), (1.5, -0.95), 12)]
    parts += eave_roof(-0.6, 2.4, 2.1, -0.15, 1.15)
    parts += [[(-1.1, -0.15), (-1.1, 0.4)], [(1.1, -0.15), (1.1, 0.4)]] + [[(x, -0.15), (x, 0.4)] for x in (-0.5, 0.0, 0.5)]
    parts += eave_roof(0.4, 1.9, 1.65, 0.85, 0.75)
    parts += [[(-0.75, 0.85), (-0.75, 1.35)], [(0.75, 0.85), (0.75, 1.35)]] + [[(x, 0.85), (x, 1.35)] for x in (-0.25, 0.25)]
    L = chain(quad((-1.45, 1.65), (-1.2, 1.35), (-0.9, 1.35), 8))
    parts += [chain(L, mirror_x(L)[::-1]), chain(quad(L[0], (-0.8, 1.9), (-0.1, 2.75), 14), quad((0.1, 2.75), (0.8, 1.9), (1.45, 1.65), 14))]
    parts += [[(-0.1, 2.75), (0.1, 2.75)], circle(0, 2.95, 0.2, 16), [(0, 3.15), (0, 3.4)]]
    parts += [cloud(-2.4, 2.4, 0.6), cloud(2.4, 2.0, 0.55)]
    return make("Temple of Heaven, Beijing", parts)


@design("landmarks_st_peters", T)
def st_peters(rng):
    left = cubic((-1.2, 1.3), (-1.25, 2.3), (-0.6, 2.9), (0, 2.95), 20)
    back = [rect(-1.3, 0.5, 1.3, 1.3)] + [[(x, 0.5), (x, 1.3)] for x in (-1.0, -0.6, -0.2, 0.2, 0.6, 1.0)]
    back += [chain(left, mirror_x(left)[::-1]), rect(-0.2, 2.93, 0.2, 3.3), arc(0, 3.3, 0.2, 0, math.pi, 8), [(0, 3.5), (0, 3.85)], [(-0.12, 3.72), (0.12, 3.72)]]
    back += [cubic((-0.6, 1.3), (-0.6, 2.1), (-0.35, 2.7), (-0.2, 2.9), 10), cubic((0.6, 1.3), (0.6, 2.1), (0.35, 2.7), (0.2, 2.9), 10)]
    for s in (-1, 1):
        back += [rect(s * 2.0 - 0.25, 0.2, s * 2.0 + 0.25, 0.55), dome(s * 2.0, 0.55, 0.3, 12), [(s * 2.0, 0.85), (s * 2.0, 1.1)]]
    front = [rect(-2.6, -1.8, 2.6, 0.2), rect(-2.7, 0.2, 2.7, 0.45), poly((-0.9, 0.45), (0, 0.95), (0.9, 0.45), closed=False)]
    front += [[(x, -1.8), (x, 0.1)] for x in (-2.3, -1.5, -0.9, -0.3, 0.3, 0.9, 1.5, 2.3)]
    front += [arch(x - 0.2, x + 0.2, -1.8, -1.0) for x in (-1.9, -0.6, 0.6, 1.9)] + [arch(-0.17, 0.17, -1.8, -1.1)]
    front += [[(-2.6, -0.5), (2.6, -0.5)]] + [rect(x - 0.15, -0.35, x + 0.15, -0.05) for x in (-1.9, -1.2, 1.2, 1.9)]
    front += [circle(x, 0.6, 0.07, 8) for x in (-2.4, -1.8, -1.2, 1.2, 1.8, 2.4)]
    parts = back + front
    obel = [poly((-0.16, -3.0), (-0.1, -0.6), (0, -0.4), (0.1, -0.6), (0.16, -3.0)), rect(-0.35, -3.0, 0.35, -2.6)]
    parts = hide(parts, [obel[0], obel[1]]) + obel
    parts += [[(-3.4, -1.8), (-2.6, -1.8)], [(2.6, -1.8), (3.4, -1.8)]]
    for s in (-1, 1):
        parts += [cubic((s * 2.6, -1.8), (s * 2.9, -2.2), (s * 3.2, -2.6), (s * 3.4, -2.8), 10), cubic((s * 2.0, -1.8), (s * 2.3, -2.5), (s * 2.7, -2.9), (s * 3.3, -3.2), 10)]
    parts += [ground(-2.0, 2.0, -3.2)]
    return make("St. Peter's Basilica, Vatican", parts)


@design("landmarks_sugarloaf_mountain", T)
def sugarloaf(rng):
    big = chain(cubic((0.2, -1.4), (0.8, 0.6), (1.4, 2.4), (2.2, 2.5), 24), cubic((2.2, 2.5), (3.0, 2.5), (3.3, 0.5), (3.4, -0.6), 20))
    small = chain(cubic((-3.4, -0.6), (-3.0, 0.4), (-2.4, 0.8), (-1.8, 0.75), 14), cubic((-1.8, 0.75), (-1.2, 0.7), (-0.8, -0.2), (-0.4, -1.4), 14))
    parts = [big, small, [(-1.8, 0.75), (2.2, 2.5)], [(-1.8, 0.62), (2.2, 2.37)]]
    t = 0.45
    cx, cy = -1.8 + 4.0 * t, 0.75 + 1.75 * t
    parts += [[(cx, cy), (cx, cy - 0.35)], rrect(cx - 0.4, cy - 1.0, cx + 0.4, cy - 0.35, 0.1), rect(cx - 0.28, cy - 0.85, cx + 0.28, cy - 0.55)]
    parts += [rect(-2.05, 0.75, -1.55, 1.05), rect(1.95, 2.5, 2.45, 2.8)]
    parts += [[(-3.4, -1.4), (3.4, -1.4)]] + waves(-3.2, 3.2, [-1.9, -2.4, -2.9], 0.05, 0.6)
    sail = [poly((-2.4, -2.2), (-1.4, -2.2), (-1.55, -2.45), (-2.25, -2.45)), poly((-1.9, -2.15), (-1.9, -1.2), (-1.4, -2.15))]
    parts += sail + [cloud(-2.0, 2.4, 0.6), poly((0.0, 2.9), (0.2, 3.05), (0.4, 2.9), closed=False)]
    parts += [[(0.6, -0.2), (1.0, 0.3)], [(2.9, 1.0), (3.0, 0.2)]]
    return make("Sugarloaf Mountain Cable Car, Rio", parts)
