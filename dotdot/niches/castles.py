"""Castles & Knights niche (medieval)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
from .landmarks import arch, cloud, gothic, ground, hide, merlons, tree, waves
import math

T = "castles"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ---------------------------------------------------------------- helpers

def paint(layers):
    """Painter's algorithm: layers back to front as (strokes, cover polygons)."""
    out = []
    for strokes, covers in layers:
        if covers:
            out = hide(out, covers)
        out += strokes
    return out


def pennant(x, y, L=0.9, h=0.32, fork=False):
    top = [(x + L * i / 10, y + 0.06 * math.sin(i * 0.9)) for i in range(11)]
    bot = [(x + L * 0.95 * i / 10, y - h + (h * 0.45) * i / 10 + 0.06 * math.sin(i * 0.9)) for i in range(11)]
    tip = [(x + L * 0.7, y - h * 0.4)] if fork else []
    return chain(top, tip, bot[::-1])


def flagpole(x, y, h, L=0.9, fork=False):
    return [[(x, y), (x, y + h)], pennant(x, y + h, L, 0.32, fork)]


def rtower(cx, y0, y1, hw, top="cone", rh=1.0, slit=True, flag=True):
    """Round tower seen from the front; returns (strokes, cover polygon)."""
    out = [[(cx - hw, y0), (cx - hw, y1)], [(cx + hw, y0), (cx + hw, y1)]]
    cover = [(cx - hw, y0), (cx - hw, y1)]
    if top == "cone":
        out.append(poly((cx - hw - 0.12, y1), (cx, y1 + rh), (cx + hw + 0.12, y1)))
        cover += [(cx - hw - 0.12, y1), (cx, y1 + rh), (cx + hw + 0.12, y1)]
        if flag:
            out += flagpole(cx, y1 + rh, 0.45, 0.6)
    else:
        w = hw + 0.12
        n = max(2, round(((2 * w) / 0.22 + 1) / 2))
        out.append(chain([(cx - w, y1)], merlons(cx - w, cx + w, y1 + 0.3, 0.22, n), [(cx + w, y1)], [(cx - w, y1)]))
        cover += [(cx - w, y1), (cx - w, y1 + 0.52), (cx + w, y1 + 0.52), (cx + w, y1)]
    cover += [(cx + hw, y1), (cx + hw, y0)]
    if slit:
        ym = (y0 + y1) / 2
        out.append(arch(cx - 0.08, cx + 0.08, ym - 0.3, ym + 0.3, True, 6))
    return out, cover


def wall(x0, x1, y0, y1, n=None):
    """Crenellated curtain wall; returns (strokes, cover)."""
    n = n or max(2, round(((x1 - x0) / 0.25 + 1) / 2))
    out = [chain([(x0, y0), (x0, y1)], merlons(x0, x1, y1, 0.25, n), [(x1, y1), (x1, y0)])]
    return out, [(x0, y0), (x0, y1 + 0.25), (x1, y1 + 0.25), (x1, y0)]


def heater(cx, cy, w, h):
    """Heater shield outline (top edge at cy + h/2)."""
    top = cy + h / 2
    left = chain([(cx, top + 0.05 * w)], [(cx - w / 2, top)], cubic((cx - w / 2, top), (cx - w / 2, cy - h * 0.15), (cx - w * 0.3, cy - h * 0.35), (cx, cy - h / 2), 20))
    return chain(left, mirror_x(left, cx)[::-1])


def fleur(cx, cy, s):
    mid = lens((cx, cy - 0.1 * s), (cx, cy + 0.9 * s), 0.28)
    side = chain(cubic((cx - 0.08 * s, cy + 0.05 * s), (cx - 0.3 * s, cy + 0.6 * s), (cx - 0.75 * s, cy + 0.45 * s), (cx - 0.6 * s, cy + 0.15 * s), 12),
                 cubic((cx - 0.6 * s, cy + 0.15 * s), (cx - 0.5 * s, cy + 0.0 * s), (cx - 0.35 * s, cy + 0.05 * s), (cx - 0.3 * s, cy + 0.15 * s), 6))
    band = rrect(cx - 0.35 * s, cy - 0.12 * s, cx + 0.35 * s, cy + 0.02 * s, 0.03 * s)
    foot = chain(quad((cx - 0.06 * s, cy - 0.12 * s), (cx - 0.1 * s, cy - 0.45 * s), (cx - 0.35 * s, cy - 0.5 * s), 6), [(cx, cy - 0.6 * s)],
                 quad((cx + 0.35 * s, cy - 0.5 * s), (cx + 0.1 * s, cy - 0.45 * s), (cx + 0.06 * s, cy - 0.12 * s), 6))
    return [mid, side, mirror_x(side, cx), band, foot]


def sword(base, ang, L, gw=0.9, bw=0.22):
    """Longsword: pommel at `base`, pointing along angle `ang`. Returns (strokes, cover)."""
    ux, uy = math.cos(ang), math.sin(ang)
    nx, ny = -uy, ux

    def P(a, b):
        return (base[0] + ux * a + nx * b, base[1] + uy * a + ny * b)

    g0, g1 = 0.2, 0.95
    blade = [P(g1 + 0.12, -bw / 2), P(L - 0.45, -bw / 2), P(L, 0), P(L - 0.45, bw / 2), P(g1 + 0.12, bw / 2)]
    guard = [P(g1, -gw / 2), P(g1 + 0.12, -gw / 2 - 0.05), P(g1 + 0.12, gw / 2 + 0.05), P(g1, gw / 2)]
    grip = [P(g0, -0.08), P(g1, -0.09), P(g1, 0.09), P(g0, 0.08)]
    pom = [P(0.1 + 0.12 * math.cos(t), 0.12 * math.sin(t)) for t in [TAU * i / 16 for i in range(17)]]
    strokes = [blade, poly(*guard), poly(*grip), pom, [P(g1 + 0.3, 0), P(L - 0.6, 0)]]
    strokes += [[P(g0 + 0.25 * k, -0.08), P(g0 + 0.25 * k + 0.12, 0.08)] for k in range(1, 3)]
    return strokes, [blade + [blade[0]], guard, grip, pom]


def stone_blocks(x0, x1, y0, y1, rows=3):
    """A few sparse masonry block outlines for wall texture."""
    out = []
    for r in range(rows):
        y = y0 + (y1 - y0) * (r + 0.5) / rows
        for k in range(2):
            x = x0 + (x1 - x0) * ((r * 0.37 + k * 0.5 + 0.15) % 1.0)
            if x + 0.45 < x1:
                out.append(rect(x, y - 0.12, x + 0.45, y + 0.12))
    return out


# ---------------------------------------------------------------- castles

@design("castles_fairytale_castle", T)
def fairytale_castle(rng):
    layers = []
    s, c = rtower(0, 0.9, 2.1, 0.4, "cone", 1.3)
    layers.append((s + [arch(-0.15, 0.15, 1.3, 1.8, True, 6)], [c]))
    keep = [poly((-0.9, -1.0), (-0.9, 0.9), (0.9, 0.9), (0.9, -1.0), closed=False), poly((-1.0, 0.9), (0, 1.5), (1.0, 0.9), closed=False)]
    keep += [arch(x - 0.15, x + 0.15, -0.6, 0.3, True, 6) for x in (-0.5, 0.0, 0.5)] + [circle(0, 0.6, 0.12, 10)]
    layers.append((keep, [[(-0.9, -1.0), (-0.9, 0.9), (-1.0, 0.9), (0, 1.5), (1.0, 0.9), (0.9, 0.9), (0.9, -1.0)]]))
    for x, y1, hw, rh in ((-1.35, 0.6, 0.33, 1.1), (1.35, 0.9, 0.33, 1.2)):
        s, c = rtower(x, -1.2, y1, hw, "cone", rh)
        layers.append((s, [c]))
    w, c = wall(-2.4, 2.4, -2.8, -1.2)
    layers.append((w + [arch(-0.5, 0.5, -2.8, -1.6), [(-0.5, -2.2), (0.5, -2.2)]] + [[(x, -2.8), (x, -1.75)] for x in (-0.25, 0.0, 0.25)], [c]))
    for x in (-2.6, 2.6):
        s, c = rtower(x, -2.8, 0.0, 0.42, "cone", 1.3)
        layers.append((s, [c]))
    parts = paint(layers)
    parts += [[(-3.4, -2.8), (-0.5, -2.8)], [(0.5, -2.8), (3.4, -2.8)], [(-0.5, -2.8), (-0.9, -3.4)], [(0.5, -2.8), (0.9, -3.4)]]
    parts += [cloud(-2.3, 2.6, 0.6), cloud(2.4, 2.9, 0.5)]
    return make("Fairy-Tale Castle with Turrets", parts)


@design("castles_stone_keep", T)
def stone_keep(rng):
    parts = [chain([(-1.6, -2.6), (-1.6, 1.4)], merlons(-1.6, 1.6, 1.4, 0.25, 7), [(1.6, 1.4), (1.6, -2.6)])]
    for s in (-1, 1):
        x0, x1 = sorted((s * 1.25, s * 1.95))
        parts.append(chain([(x0, 1.4), (x0, 2.0)], merlons(x0, x1, 2.0, 0.22, 2), [(x1, 2.0), (x1, -2.6)]))
        parts += [[(s * 0.5, -2.4), (s * 0.5, 1.3)]]
    parts += [arch(x - 0.13, x + 0.13, y, y + 0.55, True, 6) for x in (-0.95, 0.0, 0.95) for y in (-0.2, 0.7)]
    parts += [arch(-0.22, 0.22, -1.6, -0.9, True, 6)]
    parts += [poly((-1.6, -2.6), (-3.2, -2.6), (-3.2, -2.3), (-1.9, -1.2), (-1.6, -1.2), closed=False), [(-1.9, -1.2), (-1.9, -0.9), (-1.6, -0.9)]]
    parts += [[(-3.2 + 0.32 * k, -2.6 + 0.0), (-3.2 + 0.32 * k, -2.3 + 0.275 * k)] for k in range(1, 5)]
    parts += [arch(-1.45, -1.1, -1.2, -0.5)]
    parts += flagpole(0, 1.65, 1.0, 1.0)
    parts += [ground(-3.4, 3.4, -2.6), tree(2.7, -2.6, 1.2), cloud(-2.5, 2.5, 0.6)]
    return make("Norman Stone Keep", parts)


@design("castles_gatehouse_drawbridge", T)
def gatehouse(rng):
    layers = []
    mid = [chain([(-0.9, -1.6), (-0.9, 1.0)], merlons(-0.9, 0.9, 1.0, 0.25, 4), [(0.9, 1.0), (0.9, -1.6)])]
    mid += [arch(-0.62, 0.62, -1.6, 0.25, n=16)]
    grid = [[(x, -1.3), (x, 0.0)] for x in (-0.35, 0.0, 0.35)] + [[(-0.55, y), (0.55, y)] for y in (-0.9, -0.5, -0.1)]
    grid += [[(x - 0.06, -1.3), (x, -1.45), (x + 0.06, -1.3)] for x in (-0.35, 0.0, 0.35)]
    mid += hide(grid, [[(-0.62, 0.3), (0.62, 0.3), (0.62, 0.6), (-0.62, 0.6)]])
    mid += [rect(-0.35, 0.45, 0.35, 0.85)]
    layers.append((mid, [[(-0.9, -1.6), (-0.9, 1.25), (0.9, 1.25), (0.9, -1.6)]]))
    for x in (-1.65, 1.65):
        s, c = rtower(x, -1.6, 1.4, 0.78, "crenel", slit=False)
        s += [[(x, -0.3), (x, 0.5)], [(x - 0.15, 0.2), (x + 0.15, 0.2)], [(x, -1.2), (x, -0.7)]]
        layers.append((s, [c]))
    parts = paint(layers)
    bridge = [poly((-0.62, -1.6), (-1.0, -3.0), (1.0, -3.0), (0.62, -1.6), closed=False)]
    bridge += [[(-0.62 - 0.38 * t, -1.6 - 1.4 * t), (0.62 + 0.38 * t, -1.6 - 1.4 * t)] for t in (0.2, 0.4, 0.6, 0.8)]
    chains_ = [[(-0.8, -0.2), (-1.0, -3.0)], [(0.8, -0.2), (1.0, -3.0)]]
    moat = [[(-3.4, -1.6), (-0.62, -1.6)], [(0.62, -1.6), (3.4, -1.6)]] + [wave(-3.3, -1.3, y, 0.05, 2.5, 30) for y in (-2.1, -2.6)] + \
           [wave(1.3, 3.3, y, 0.05, 2.5, 30) for y in (-2.1, -2.6)]
    return make("Gatehouse with Drawbridge", parts + bridge + chains_ + moat + [cloud(-2.6, 2.6, 0.5)])


@design("castles_castle_on_hill", T)
def castle_on_hill(rng):
    hill = chain(cubic((-3.4, -2.0), (-2.4, -1.4), (-1.6, 0.4), (-0.8, 0.5), 16), [(1.2, 0.5)], cubic((1.2, 0.5), (2.0, 0.4), (2.6, -1.6), (3.4, -2.2), 16))
    layers = []
    s, c = rtower(0.2, 0.5, 2.0, 0.3, "cone", 0.9)
    layers.append((s, [c]))
    keep = [poly((-0.5, 0.5), (-0.5, 1.4), (0.9, 1.4), (0.9, 0.5), closed=False), poly((-0.6, 1.4), (0.2, 1.9), (1.0, 1.4), closed=False),
            arch(-0.3, -0.1, 0.8, 1.2, True, 6), arch(0.5, 0.7, 0.8, 1.2, True, 6)]
    layers.append((keep, [[(-0.5, 0.5), (-0.5, 1.4), (-0.6, 1.4), (0.2, 1.9), (1.0, 1.4), (0.9, 1.4), (0.9, 0.5)]]))
    for x, y1 in ((-0.8, 1.2), (1.2, 1.1)):
        s, c = rtower(x, 0.5, y1, 0.22, "cone", 0.7, slit=False)
        layers.append((s, [c]))
    w, c = wall(-0.6, 1.0, 0.5, 0.9)
    layers.append((w + [arch(0.05, 0.35, 0.5, 0.8)], [c]))
    parts = paint(layers) + [hill]
    path = [cubic((0.2, 0.5), (-1.5, -0.3), (1.5, -1.0), (-0.6, -1.8), 24), cubic((-0.6, -1.8), (-1.8, -2.3), (0.5, -2.8), (0.0, -3.3), 20)]
    parts += path + [tree(-2.4, -1.4, 0.8), tree(2.2, -1.2, 0.7), tree(-1.2, -0.4, 0.6), tree(1.6, -2.4, 0.9), tree(-2.8, -3.1, 0.9)]
    parts += [cloud(-2.4, 2.3, 0.7), cloud(2.4, 2.8, 0.5), poly((2.0, 1.6), (2.2, 1.75), (2.4, 1.6), closed=False)]
    return make("Castle on a Hilltop", parts)


@design("castles_ruined_castle", T)
def ruined_castle(rng):
    tower = [[(-2.4, -2.6), (-2.4, 1.4)], [(-2.4, 1.4), (-2.2, 1.7), (-2.0, 1.5), (-1.8, 2.0), (-1.5, 1.6), (-1.3, 1.1)], [(-1.3, 1.1), (-1.3, -2.6)]]
    tower += [arch(-2.0, -1.7, 0.2, 0.9, True, 8), arch(-2.0, -1.7, -1.5, -0.8, True, 8)]
    walls = [[(-1.3, -0.4), (-0.9, -0.4), (-0.7, 0.1), (-0.4, 0.0), (-0.2, 0.6), (0.3, 0.6), (0.4, 0.2), (0.8, 0.3), (1.0, -0.6), (1.4, -0.5), (1.6, 0.9),
              (2.0, 1.2), (2.3, 0.7), (2.6, 0.8), (2.8, -2.6)]]
    walls += [gothic(-0.1, 0.4, -1.6, 0.0, True), gothic(1.7, 2.3, -1.4, 0.4, True)]
    rubble = [ellipse(x, y, rx, ry, 16) for x, y, rx, ry in ((-0.6, -2.45, 0.3, 0.15), (0.9, -2.45, 0.35, 0.16), (0.4, -2.5, 0.2, 0.1), (3.1, -2.45, 0.25, 0.14))]
    ivy = [cubic((-2.35, -2.6), (-1.6, -1.6), (-2.3, -0.4), (-1.6, 0.6), 30)]
    leaves = [lens(p, (p[0] + 0.25 * (-1) ** k, p[1] + 0.15), 0.35) for k, p in enumerate(ivy[0][4::5])]
    crows = [poly((x - 0.25, y + 0.1), (x, y), (x + 0.25, y + 0.1), closed=False) for x, y in ((0.6, 2.5), (1.4, 2.8), (-0.4, 2.9))]
    moon = [chain(arc(2.5, 2.5, 0.6, 1.2, 5.1, 24), arc(2.75, 2.6, 0.5, 4.6, 1.6, 20)[::-1])]
    parts = tower + walls + rubble + ivy + leaves + crows + moon + [ground(-3.4, 3.4, -2.6)]
    parts += [[(x - 0.1, -3.1), (x, -2.85), (x + 0.1, -3.1)] for x in (-2.6, -1.0, 0.6, 2.2)]
    return make("Ruined Castle", parts)


@design("castles_watchtower", T)
def watchtower(rng):
    parts = [[(-0.85, -1.8), (-0.75, 1.8)], [(0.85, -1.8), (0.75, 1.8)], [(-1.1, 1.8), (1.1, 1.8)]]
    parts += [[(x, 1.8), (x, 1.55)] for x in (-0.55, -0.2, 0.2, 0.55)] + [[(-0.75, 1.55), (0.75, 1.55)]]
    parts += [chain([(-1.1, 1.8)], merlons(-1.1, 1.1, 2.1, 0.28, 4), [(1.1, 1.8)])]
    parts += [poly((-1.1, 2.4), (0, 3.4), (1.1, 2.4), closed=False)] + flagpole(0, 3.4, 0.45, 0.8, True)
    parts += [arch(-0.1, 0.1, 0.6, 1.2, True, 6), arch(-0.1, 0.1, -0.6, 0.0, True, 6), arch(-0.3, 0.3, -1.8, -0.9)]
    parts += [[(-0.3, -1.8), (-1.0, -2.2)], [(0.3, -1.8), (1.0, -2.2)]]
    rocks = chain([(-3.4, -3.2)], [(-2.6, -2.5), (-1.6, -2.3), (-1.0, -1.8), (1.0, -1.8), (1.7, -2.2), (2.4, -2.1), (3.4, -3.0)])
    parts += [rocks, [(-1.6, -2.3), (-1.4, -2.9)], [(1.7, -2.2), (2.0, -2.8)], [(-0.3, -2.4), (0.4, -2.6)]]
    parts += waves(-3.3, 3.3, [-3.3], 0.05, 0.6) + [cloud(-2.3, 2.2, 0.7), cloud(2.3, 1.2, 0.6)]
    parts += [poly((-2.6, 0.6), (-2.4, 0.75), (-2.2, 0.6), closed=False), poly((2.0, 2.8), (2.2, 2.95), (2.4, 2.8), closed=False)]
    return make("Stone Watchtower on the Rocks", parts)


@design("castles_moated_castle", T)
def moated_castle(rng):
    layers = []
    s, c = rtower(0, 0.0, 1.8, 0.5, "cone", 1.1)
    layers.append((s, [c]))
    w, c = wall(-2.2, 2.2, -1.4, 0.2)
    layers.append((w + [arch(-0.45, 0.45, -1.4, -0.3), [(-0.45, -0.8), (0.45, -0.8)]] + [arch(x - 0.1, x + 0.1, -0.7, -0.2, True, 6) for x in (-1.3, 1.3)], [c]))
    for x in (-2.4, 2.4):
        s, c = rtower(x, -1.4, 0.8, 0.5, "crenel")
        layers.append((s + flagpole(x, 1.32, 0.7, 0.7), [c]))
    parts = paint(layers)
    parts += [[(-3.4, -1.4), (-0.6, -1.4)], [(0.6, -1.4), (3.4, -1.4)], poly((-0.6, -1.4), (-0.75, -2.0), (0.75, -2.0), (0.6, -1.4), closed=False),
              arc(0, -2.4, 0.42, 0, math.pi, 12), [(-0.75, -2.0), (-0.9, -2.4)], [(0.75, -2.0), (0.9, -2.4)]]
    parts += [wave(-3.3, -1.1, y, 0.05, 3, 40) for y in (-1.9, -2.4, -2.9)] + [wave(1.1, 3.3, y, 0.05, 3, 40) for y in (-1.9, -2.4, -2.9)]
    parts += [wave(-0.6, 0.6, -2.9, 0.05, 1.5, 16), cloud(-2.0, 2.6, 0.6), cloud(2.2, 2.9, 0.5)]
    return make("Moated Castle with Stone Bridge", parts)


@design("castles_banners", T)
def castle_banners(rng):
    parts = []
    for x, y1 in ((-1.8, -0.8), (1.6, -1.2)):
        parts += rtower(x, -3.0, y1, 0.55, "crenel", slit=True)[0]
    parts += [ground(-3.4, 3.4), [(-1.8, -0.28), (-1.8, 3.2)], [(1.6, -0.68), (1.6, 2.6)]]
    top = [(x, 3.1 + 0.15 * math.sin(x * 2.2)) for x in [-1.8 + 3.0 * i / 30 for i in range(31)]]
    bot = [(x, 2.0 + 0.15 * math.sin(x * 2.2)) for x in [-1.8 + 3.0 * i / 30 for i in range(31)]]
    parts += [chain(top, [(0.7, 2.55)], bot[::-1]), cubic((-1.2, 2.55), (-0.6, 2.75), (0.0, 2.35), (0.3, 2.55), 12)]
    sq_t = [(1.6 + 1.6 * i / 16, 2.6 + 0.12 * math.sin(i * 0.8)) for i in range(17)]
    sq_b = [(1.6 + 1.6 * i / 16, 1.2 + 0.12 * math.sin(i * 0.8)) for i in range(17)]
    parts += [chain(sq_t, sq_b[::-1]), [sq_t[8], sq_b[8]], [(1.6, 1.9), (3.2, 1.9 + 0.12 * math.sin(16 * 0.8))]]
    st = [(-1.8 + 1.5 * i / 15, 1.8 - 0.4 * i / 15 + 0.12 * math.sin(i * 0.9)) for i in range(16)]
    parts += [chain(st, [(-1.8, 1.3)])]
    parts += [circle(-1.8, 3.3, 0.1, 10), circle(1.6, 2.7, 0.1, 10), cloud(-2.6, 0.4, 0.5), cloud(2.6, 0.2, 0.5)]
    return make("Castle Towers with Banners", parts)


# ---------------------------------------------------------------- helmets & heraldry

@design("castles_great_helm", T)
def great_helm(rng):
    left = chain([(0, 2.05), (-1.4, 1.8)], cubic((-1.4, 1.8), (-1.55, 0.5), (-1.6, -1.2), (-1.4, -2.0), 20), [(0, -2.2)])
    parts = [chain(left, mirror_x(left)[::-1]), quad((-1.42, 1.35), (0, 1.55), (1.42, 1.35), 16)]
    parts += [rect(-1.2, 0.3, -0.25, 0.55), rect(0.25, 0.3, 1.2, 0.55)]
    cross = [(-0.18, 1.3), (0.18, 1.3), (0.18, 0.7), (0.35, 0.7), (0.35, 0.15), (0.18, 0.15), (0.18, -1.7), (-0.18, -1.7), (-0.18, 0.15), (-0.35, 0.15),
             (-0.35, 0.7), (-0.18, 0.7), (-0.18, 1.3)]
    parts += [cross]
    hints = [eye(x, y, 0.06) for x in (-1.05, -0.75, -0.45, 0.45, 0.75, 1.05) for y in (-0.5, -0.9, -1.3)]
    hints += [eye(x, 1.32 + 0.0, 0.05) for x in (-1.1, -0.6, 0.6, 1.1)]
    parts += [[(-1.5, -1.9), (-1.9, -2.4), (1.9, -2.4), (1.5, -1.9)]]
    parts.pop()
    parts += [rrect(-2.2, -2.9, 2.2, -2.4, 0.12)]
    return make("Crusader Great Helm", parts, hints)


@design("castles_plumed_helmet", T)
def plumed_helmet(rng):
    skull = chain([(1.3, -0.6)], cubic((1.3, -0.6), (1.6, 0.8), (0.9, 1.85), (0.0, 1.85), 20), cubic((0.0, 1.85), (-0.8, 1.85), (-1.2, 1.3), (-1.3, 0.7), 14))
    visor = poly((-1.3, 0.7), (-2.15, 0.0), (-1.2, -0.8), closed=False)
    jaw = quad((-1.2, -0.8), (0.2, -1.0), (1.3, -0.6), 14)
    parts = [skull, visor, jaw, lens((-1.75, 0.38), (-0.55, 0.5), 0.12), circle(0.15, 0.15, 0.16, 12),
             cubic((-1.3, 0.7), (-0.8, 0.3), (-0.2, 0.3), (0.0, 0.15), 10), cubic((-1.2, -0.8), (-0.7, -0.3), (-0.2, 0.0), (0.0, 0.1), 10)]
    parts += [[(-1.6 + 0.25 * k, -0.15 - 0.08 * k), (-1.45 + 0.25 * k, -0.3 - 0.08 * k)] for k in range(3)]
    parts += [quad((-1.1 + 0.1 * k, -1.2 - 0.4 * k), (0.2, -1.4 - 0.45 * k), (1.3 + 0.1 * k, -1.0 - 0.4 * k), 14) for k in range(3)]
    parts += [[(-1.2, -0.8), (-1.1, -1.2), (-1.0, -1.6), (-0.9, -2.0)], [(1.3, -0.6), (1.3, -1.0), (1.4, -1.4), (1.5, -1.8)]]
    parts += [rect(0.25, 1.75, 0.55, 2.1)]
    plume = [lens((0.4, 2.0), (2.7, 2.8), 0.17), lens((0.45, 2.0), (3.0, 1.8), 0.15), lens((0.45, 1.95), (2.7, 0.8), 0.15)]
    plume = paint([([plume[2]], []), ([plume[1]], [plume[1]]), ([plume[0]], [plume[0]])])
    parts += plume + [[(0.6, 2.05), (2.5, 2.75)]]
    parts += [quad((0.1, 1.85), (-0.2, 0.9), (-0.1, 0.4), 10)]
    return make("Visored Helmet with Plume", parts)


@design("castles_norman_helmet", T)
def norman_helmet(rng):
    left = cubic((-1.25, 0.4), (-1.3, 1.6), (-0.6, 2.5), (0, 3.0), 20)
    helm = [chain(left, mirror_x(left)[::-1]), quad((-1.3, 0.35), (0, 0.15), (1.3, 0.35), 16), quad((-1.33, 0.75), (0, 0.55), (1.33, 0.75), 16), [(0, 0.55), (0, 2.9)]]
    nasal = poly((-0.14, 0.2), (-0.14, -0.9), (-0.2, -1.15), (0.2, -1.15), (0.14, -0.9), (0.14, 0.2), closed=False)
    coif = chain(cubic((-1.25, 0.4), (-1.6, -0.6), (-1.5, -1.8), (-1.2, -2.4), 16), cubic((-1.2, -2.4), (-2.0, -2.6), (-2.8, -2.9), (-3.0, -3.3), 10))
    face = chain(cubic((-0.85, 0.15), (-0.95, -0.8), (-0.6, -1.9), (0, -2.0), 16))
    beard = chain(cubic((-0.8, -0.8), (-0.9, -1.6), (-0.5, -2.3), (0, -2.4), 14))
    parts = helm + [nasal, coif, mirror_x(coif), face, mirror_x(face), beard, mirror_x(beard)]
    parts += [quad((-0.6, -1.3), (-0.3, -1.15), (-0.05, -1.25), 6), quad((0.05, -1.25), (0.3, -1.15), (0.6, -1.3), 6), quad((-0.25, -1.6), (0, -1.65), (0.25, -1.6), 6)]
    parts += [quad((-0.65, -0.25), (-0.4, -0.15), (-0.2, -0.25), 6), quad((0.2, -0.25), (0.4, -0.15), (0.65, -0.25), 6)]
    parts += [[(-1.2, -2.4), (-0.6, -2.1)], [(1.2, -2.4), (0.6, -2.1)]]
    return make("Norman Warrior's Nasal Helmet", parts, [eye(-0.42, -0.45, 0.08), eye(0.42, -0.45, 0.08)])


@design("castles_quartered_shield", T)
def quartered_shield(rng):
    outer = heater(0, 0, 4.2, 5.4)
    inner = transform(outer, s=0.9, dy=0.05)
    parts = [outer, inner, [(0, 2.45), (0, -2.35)], [(-1.85, 0.45), (1.85, 0.45)]]
    parts += fleur(-0.95, 1.2, 0.95) + fleur(0.95, -1.1, 0.75)
    for k in range(3):
        y = 1.0 + 0.45 * k
        parts.append([(0.25, y), (0.95, y + 0.55), (1.65, y)] if y + 0.55 < 2.4 else [(0.3, y), (0.95, y + 0.4), (1.6, y)])
    for k in range(3):
        y = -1.2 + 0.45 * k
        parts.append([(-1.55, y - 0.3), (-0.95, y + 0.2), (-0.3, y - 0.3)])
    parts += [poly((0.0, 2.4), (-0.25, 2.9), (0.25, 2.9), closed=False)]
    parts.pop()
    return make("Quartered Heraldic Shield", parts)


@design("castles_coat_of_arms", T)
def coat_of_arms(rng):
    sh = heater(0, -0.6, 2.6, 3.2)
    parts = [sh, [(-1.25, -1.6), (0, -0.2), (1.25, -1.6)], [(-1.2, -1.2), (0, 0.15), (1.2, -1.2)]]
    parts += [star(-0.75, 0.45, 0.28, 5, 0.45), star(0.75, 0.45, 0.28, 5, 0.45), star(0, -1.4, 0.32, 5, 0.45)]
    helm = [chain(cubic((-0.55, 1.0), (-0.65, 1.8), (-0.4, 2.15), (0, 2.2), 12),
                  cubic((0, 2.2), (0.4, 2.15), (0.65, 1.8), (0.55, 1.0), 12))]
    helm += [[(x, 1.15), (x, 1.85)] for x in (-0.25, 0.0, 0.25)] + [[(-0.45, 1.55), (0.45, 1.55)]]
    crown = [poly((-0.45, 2.2), (-0.5, 2.6), (-0.25, 2.4), (0, 2.7), (0.25, 2.4), (0.5, 2.6), (0.45, 2.2), closed=False)]
    feathers = [lens((0, 2.65), (-0.5, 3.4), 0.2), lens((0, 2.7), (0, 3.6), 0.2), lens((0, 2.65), (0.5, 3.4), 0.2)]
    mant = []
    for s in (-1, 1):
        m = [cubic((s * 0.5, 1.9), (s * 1.6, 2.2), (s * 2.3, 1.2), (s * 1.9, 0.2), 16), cubic((s * 1.9, 0.2), (s * 2.6, -0.3), (s * 2.5, -1.4), (s * 1.6, -1.6), 14),
             spiral(s * 2.05, -1.05, 0.08, 0.35, 0.9, 30, rot=0 if s > 0 else math.pi), cubic((s * 0.55, 1.4), (s * 1.2, 1.4), (s * 1.6, 0.8), (s * 1.4, 0.1), 12),
             spiral(s * 1.95, 1.0, 0.08, 0.3, 0.9, 30, rot=math.pi / 2)]
        mant += m
    scroll = [cubic((-2.2, -2.3), (-1.0, -2.0), (1.0, -2.0), (2.2, -2.3), 20), cubic((-2.2, -2.8), (-1.0, -2.5), (1.0, -2.5), (2.2, -2.8), 20),
              [(-2.2, -2.3), (-2.6, -2.6), (-2.2, -2.8)], [(2.2, -2.3), (2.6, -2.6), (2.2, -2.8)]]
    parts = paint([(mant, []), (helm + crown + feathers, [helm[0] + [(-0.55, 1.0)]]), (parts, [sh]), (scroll, [scroll[0] + scroll[1][::-1]])])
    return make("Coat of Arms with Crest", parts)


# ---------------------------------------------------------------- weapons

@design("castles_crossed_swords", T)
def crossed_swords(rng):
    s1, c1 = sword((-2.3, -2.6), math.radians(52), 6.0, gw=1.1, bw=0.3)
    s2, c2 = sword((2.3, -2.6), math.radians(128), 6.0, gw=1.1, bw=0.3)
    crown = [poly((-0.6, 2.4), (-0.75, 3.1), (-0.35, 2.75), (0, 3.25), (0.35, 2.75), (0.75, 3.1), (0.6, 2.4)), circle(0, 3.4, 0.12, 10)]
    parts = paint([(s1, []), (s2, c2)]) + crown + [cubic((-2.2, -3.0), (-1.0, -2.7), (1.0, -2.7), (2.2, -3.0), 20), cubic((-2.2, -3.45), (-1.0, -3.15), (1.0, -3.15), (2.2, -3.45), 20),
                                              [(-2.2, -3.0), (-2.6, -3.3), (-2.2, -3.45)], [(2.2, -3.0), (2.6, -3.3), (2.2, -3.45)]]
    return make("Crossed Longswords", parts)


@design("castles_sword_in_stone", T)
def sword_in_stone(rng):
    s, c = sword((0, 2.6), -math.pi / 2, 4.4, gw=1.4, bw=0.32)
    rock = chain(cubic((-2.8, -2.6), (-2.9, -1.6), (-2.2, -0.7), (-1.2, -0.6), 14), [(-0.5, -0.3), (0.3, -0.35)],
                 cubic((0.3, -0.35), (1.4, -0.5), (2.6, -1.0), (2.9, -2.6), 16))
    rc = rock + [(-2.8, -2.6)]
    parts = hide(s, [rc]) + [rock, ground(-3.4, 3.4, -2.6), [(-1.6, -0.9), (-1.2, -1.5), (-1.4, -2.0)], [(1.4, -0.9), (1.0, -1.6)], [(0.2, -1.6), (0.6, -2.2)]]
    parts += [[(0.9 * math.cos(a), 2.0 + 0.9 * math.sin(a)), (1.5 * math.cos(a), 2.0 + 1.5 * math.sin(a))] for a in [math.radians(d) for d in (20, 50, 90, 130, 160)]]
    parts += [[(x - 0.12, -3.1), (x, -2.8), (x + 0.12, -3.1)] for x in (-2.5, -1.4, 1.5, 2.6)]
    return make("Sword in the Stone", parts, [eye(0, 2.5, 0.07)])


@design("castles_axe_and_mace", T)
def axe_and_mace(rng):
    haft = rrect(-0.11, 0.0, 0.11, 5.6, 0.08)
    blade = chain(cubic((-0.11, 5.15), (-0.6, 5.25), (-1.0, 5.55), (-1.3, 5.85), 10), cubic((-1.3, 5.85), (-1.7, 5.0), (-1.7, 4.0), (-1.3, 3.3), 16),
                  cubic((-1.3, 3.3), (-1.0, 3.8), (-0.6, 4.3), (-0.11, 4.35), 10))
    spike = poly((0.11, 4.6), (0.75, 4.75), (0.11, 4.9), closed=False)
    axe_local = [haft, mirror_x(blade), mirror_x(spike), rect(-0.16, 0.4, 0.16, 1.4), poly((-0.11, 5.6), (0, 6.0), (0.11, 5.6), closed=False)]
    axe = [transform(p, dx=-2.2, dy=-2.9, rot=-0.62) for p in axe_local]
    mhaft = rrect(-0.11, 0.0, 0.11, 4.6, 0.08)
    head = []
    for k, dx in enumerate((-0.32, 0.0, 0.32)):
        head.append(chain([(dx * 0.6, 4.45)], cubic((dx * 0.6, 4.45), (dx * 1.9, 4.7), (dx * 1.9, 5.5), (dx * 0.6, 5.75), 12)))
    flanges = [poly((-0.16, 4.45), (-0.62, 4.75), (-0.62, 5.45), (-0.16, 5.75), closed=False), poly((0.16, 4.45), (0.62, 4.75), (0.62, 5.45), (0.16, 5.75), closed=False),
               [(0.0, 4.45), (0.0, 5.75)], [(-0.16, 5.75), (0.16, 5.75)], poly((-0.12, 5.75), (0, 6.15), (0.12, 5.75), closed=False), [(-0.16, 4.45), (0.16, 4.45)]]
    mace_local = [mhaft, rect(-0.16, 0.4, 0.16, 1.4)] + flanges
    mace = [transform(p, dx=2.2, dy=-2.9, rot=0.62) for p in mace_local]
    mcov = [transform(mhaft, dx=2.2, dy=-2.9, rot=0.62), transform([(-0.62, 4.45), (-0.62, 5.75), (0.62, 5.75), (0.62, 4.45)], dx=2.2, dy=-2.9, rot=0.62)]
    parts = paint([(axe, []), (mace, mcov)])
    return make("Battle Axe and Flanged Mace", parts)


@design("castles_crossbow", T)
def crossbow(rng):
    stock = poly((-3.2, -0.55), (-3.0, 0.25), (-1.6, 0.2), (-1.2, 0.12), (2.0, 0.12), (2.2, 0.0), (2.0, -0.15), (-1.0, -0.15), (-1.6, -0.35), (-2.0, -0.6))
    prod = tube([(2.0 - 0.9 * (y / 2.6) ** 2, y) for y in [-2.6 + 5.2 * i / 40 for i in range(41)]], lambda t: 0.28 - 0.14 * abs(2 * t - 1))
    string = [(1.25, 2.55), (-0.4, 0.0), (1.25, -2.55)]
    bolt = [[(-0.4, 0.04), (2.6, 0.04)], poly((2.6, -0.1), (3.0, 0.04), (2.6, 0.18)), lens((-0.4, 0.04), (0.1, 0.3), 0.3), lens((-0.4, 0.04), (0.1, -0.22), 0.3)]
    stirrup = [arc(2.45, 0.0, 0.6, -0.9, 0.9, 14)]
    trig = [quad((-1.0, -0.15), (-0.8, -0.9), (-1.4, -1.6), 10), quad((-1.2, -0.15), (-1.0, -0.8), (-1.5, -1.5), 10)]
    parts = paint([(stirrup, []), ([prod], [prod]), (trig + [stock], [stock]), ([string], []), (bolt, [])])
    parts += [circle(-0.4, 0.0, 0.14, 10)]
    return make("Medieval Crossbow", parts)


@design("castles_catapult", T)
def catapult(rng):
    base = [rect(-2.6, -1.9, 2.0, -1.5)]
    wheels = []
    for x in (-1.9, 1.3):
        wheels += [circle(x, -2.3, 0.65, 40), circle(x, -2.3, 0.14, 12)]
        wheels += [[(x + 0.14 * math.cos(a), -2.3 + 0.14 * math.sin(a)), (x + 0.65 * math.cos(a), -2.3 + 0.65 * math.sin(a))] for a in [k * math.pi / 3 + 0.3 for k in range(6)]]
    frame = [poly((-0.75, -1.5), (-0.55, 0.45), closed=False), poly((0.0, -1.5), (-0.2, 0.45), closed=False), rrect(-0.85, 0.42, 0.1, 0.65, 0.06),
             [(-0.65, -0.6), (1.0, -1.5)]]
    arm = tube([(1.1 - 2.5 * t, -1.3 + 2.4 * t) for t in [i / 12 for i in range(13)]], 0.22)
    cup = [chain(arc(-1.6, 1.35, 0.5, math.radians(130), math.radians(320), 20)), [(-1.92, 1.73), (-1.22, 1.03)]]
    stones = [circle(-1.75, 1.6, 0.2, 16), circle(-1.4, 1.5, 0.16, 14)]
    rope = [ellipse(1.1, -1.3, 0.3, 0.3, 20)]
    base = [rect(-2.6, -1.9, 2.0, -1.5)]
    pile = [circle(2.6, -2.75, 0.25, 16), circle(3.1, -2.75, 0.25, 16), circle(2.85, -2.35, 0.25, 16)]
    parts = paint([(frame, []), ([arm] + cup + stones, [arm]), (rope + base, [rope[0], base[0]]), (wheels, [w for w in wheels[::8]])])
    parts += pile + [ground(-3.4, 3.4, -3.0)]
    return make("Medieval Catapult", parts)


@design("castles_trebuchet", T)
def trebuchet(rng):
    parts = [rect(-2.6, -2.4, 2.6, -2.1)]
    for x in (-1.8, 1.8):
        parts += [circle(x, -2.6, 0.38, 24), circle(x, -2.6, 0.1, 8)]
    parts = paint([(parts[1:], []), ([parts[0]], [parts[0]])])
    frame = [poly((-1.4, -2.1), (-0.12, 1.6), (0.12, 1.6), (1.4, -2.1), closed=False), poly((-1.1, -2.1), (-0.05, 1.3), (0.05, 1.3), (1.1, -2.1), closed=False),
             [(-0.95, -0.8), (0.95, -0.8)], [(-0.82, -1.1), (0.82, -1.1)], circle(0, 1.5, 0.15, 12)]
    piv = (0, 1.5)
    a = math.radians(160)
    long_end = (piv[0] + 3.2 * math.cos(a - math.pi), piv[1] + 3.2 * math.sin(a - math.pi))
    long_end = (piv[0] - 3.0 * math.cos(math.radians(25)), piv[1] - 3.0 * math.sin(math.radians(-25)))
    long_end = (-2.75, 2.75)
    short_end = (1.1, 1.05)
    arm = tube([(long_end[0] + (short_end[0] - long_end[0]) * t, long_end[1] + (short_end[1] - long_end[1]) * t) for t in [i / 20 for i in range(21)]],
               lambda t: 0.12 + 0.12 * t)
    box = [[(1.1, 1.05), (0.9, 0.3)], [(1.1, 1.05), (1.4, 0.3)], rect(0.55, -0.6, 1.75, 0.3)] + [[(x, -0.6), (x, 0.3)] for x in (0.95, 1.35)]
    sling = [[long_end, (-2.95, 1.4)], [(-2.2, 2.6), (-2.6, 1.3)], circle(-2.75, 1.15, 0.28, 18)]
    parts += paint([(frame, []), ([arm] + sling, [arm]), (box, [box[2]])])
    parts += [ground(-3.4, 3.4, -3.0), cloud(2.2, 2.6, 0.6)]
    return make("Trebuchet Siege Engine", parts)


@design("castles_battering_ram", T)
def battering_ram(rng):
    shed = [poly((-2.8, -1.6), (-2.8, 0.2), (-1.6, 1.4), (0.6, 1.4), (1.8, 0.2), (1.8, -1.6), closed=False), [(-2.8, 0.2), (1.8, 0.2)]]
    shed += [quad((-2.6, 0.5), (-0.5, 0.65), (1.6, 0.5), 14), quad((-2.2, 0.9), (-0.5, 1.05), (1.2, 0.9), 14)]
    shed += [[(-2.8, -1.6), (1.8, -1.6)], [(-2.8, -1.25), (1.8, -1.25)]]
    wheels = []
    for x in (-2.2, -0.5, 1.2):
        wheels += [circle(x, -2.2, 0.55, 36), circle(x, -2.2, 0.12, 10)] + [[(x + 0.12 * math.cos(q), -2.2 + 0.12 * math.sin(q)), (x + 0.55 * math.cos(q), -2.2 + 0.55 * math.sin(q))]
                                                                         for q in [k * math.pi / 2 + 0.4 for k in range(4)]]
    log = [rrect(-2.2, -0.75, 2.6, -0.3, 0.15), poly((2.6, -0.85), (3.0, -0.95), (3.3, -0.55), (3.0, -0.15), (2.6, -0.2), closed=False), [(2.6, -0.85), (2.6, -0.2)]]
    log += [[(-1.5, -0.3), (-1.3, 0.2)], [(0.8, -0.3), (0.6, 0.2)]]
    ram_horn = [spiral(2.85, -0.45, 0.05, 0.22, 1.0, 24)]
    parts = paint([(shed, []), (log + ram_horn, [log[0], log[1]]), (wheels, [wheels[0], wheels[7], wheels[14]])])
    parts += [ground(-3.4, 3.4, -2.75)]
    return make("Battering Ram", parts)


@design("castles_siege_tower", T)
def siege_tower(rng):
    body = [poly((-1.6, -2.4), (-1.2, 2.2), (1.2, 2.2), (1.6, -2.4), closed=False)]
    planks = [[(-1.6 + 0.4 * (y + 2.4) / 4.6, y), (1.6 - 0.4 * (y + 2.4) / 4.6, y)] for y in (-2.4, -1.2, 0.0, 1.2)]
    vert = [[(x * (1 - 0.25 * t0), -2.4 + 4.6 * t0) for t0 in (0, 1)] for x in (-0.55, 0.55)]
    vert = [[(-0.55, -2.4), (-0.42, 2.2)], [(0.55, -2.4), (0.42, 2.2)]]
    braces = [[(-1.45, -2.25), (-0.6, -1.25)], [(1.45, -2.25), (0.6, -1.25)], [(-1.4, -1.05), (-0.6, -0.05)], [(1.4, -1.05), (0.6, -0.05)]]
    top = [chain([(-1.3, 2.2)], merlons(-1.3, 1.3, 2.2, 0.3, 5), [(1.3, 2.2)])]
    bridge = [poly((-0.35, 1.3), (-0.6, 2.6), (0.6, 2.6), (0.35, 1.3)), [(-0.4, 1.65), (0.4, 1.65)], [(-0.48, 2.1), (0.48, 2.1)]]
    bridge = [rect(-0.45, 1.35, 0.45, 2.05), [(-0.45, 2.05), (-1.0, 2.9)], [(0.45, 2.05), (1.0, 2.9)]]
    ladder = [[(-0.2, -2.3), (-0.2, -1.3)], [(0.2, -2.3), (0.2, -1.3)]] + [[(-0.2, y), (0.2, y)] for y in (-2.05, -1.75, -1.45)]
    wheels = []
    for x in (-1.1, 1.1):
        wheels += [circle(x, -2.75, 0.4, 24), circle(x, -2.75, 0.1, 8)]
    flag = flagpole(-1.25, 2.5, 0.9, 0.8, True)
    parts = body + planks + vert + braces + top + bridge + ladder + wheels + flag + [ground(-3.4, 3.4, -3.15)]
    parts += [chain([(2.0, -3.15), (2.0, 1.4)], merlons(2.0, 3.4, 1.4, 0.3, 3), [(3.4, 1.4)]), arch(2.5, 2.9, 0.2, 0.9, True, 6)]
    return make("Wooden Siege Tower", parts)


@design("castles_flail_morning_star", T)
def flail(rng):
    hd = tube([(-2.6 + 2.4 * t, -2.8 + 2.4 * t) for t in [i / 10 for i in range(11)]], 0.28)
    ring = circle(-0.1, -0.3, 0.16, 12)
    links = []
    p = (-0.1, -0.14)
    for k in range(5):
        c = (p[0] + 0.0 + 0.04 * k, p[1] + 0.22)
        links.append(ellipse(c[0], c[1] + 0.06, 0.09 if k % 2 else 0.12, 0.17, 12))
        p = (c[0], c[1] + 0.15)
    ballc = (0.2, 1.9)
    ball = [circle(ballc[0], ballc[1], 0.6, 40)]
    spikes = [[(ballc[0] + 0.6 * math.cos(a - 0.18), ballc[1] + 0.6 * math.sin(a - 0.18)), (ballc[0] + 1.0 * math.cos(a), ballc[1] + 1.0 * math.sin(a)),
               (ballc[0] + 0.6 * math.cos(a + 0.18), ballc[1] + 0.6 * math.sin(a + 0.18))] for a in [k * TAU / 9 + 0.1 for k in range(9)]]
    spikes = [s for s, a in zip(spikes, [k * TAU / 9 + 0.1 for k in range(9)]) if not (4.3 < a < 5.1)]
    fl = [hd, ring] + links + ball + spikes + [rect(-2.75, -3.1, -2.35, -2.7)]
    parts = fl
    return make("Medieval Flail", parts)


# ---------------------------------------------------------------- people & horses

def closed(pts):
    return list(pts) + [pts[0]]


@design("castles_knight_in_armour", T)
def knight(rng):
    cape = [chain([(-1.2, 1.3)], cubic((-1.2, 1.3), (-1.6, 0.0), (-1.8, -1.5), (-1.9, -2.8), 14), wave(-1.9, 1.9, -2.8, 0.06, 4, 40),
                  cubic((1.9, -2.8), (1.8, -1.5), (1.6, 0.0), (1.2, 1.3), 14))]
    legs, lc = [], []
    for s in (-1, 1):
        th = tube([(s * 0.32, -0.45), (s * 0.4, -1.0), (s * 0.43, -1.55)], 0.44)
        gr = tube([(s * 0.43, -1.75), (s * 0.44, -2.3), (s * 0.45, -2.78)], 0.38)
        knee = circle(s * 0.43, -1.65, 0.2, 18)
        foot = poly((s * 0.25, -2.75), (s * 0.25, -3.02), (s * 1.0, -3.05), (s * 0.66, -2.75))
        legs += [th, gr, knee, foot]
        lc += [th, gr, knee, foot]
    breast = chain([(-0.55, 1.45)], cubic((-0.55, 1.45), (-0.65, 0.9), (-0.55, 0.4), (-0.45, 0.2), 10), quad((-0.45, 0.2), (0, 0.05), (0.45, 0.2), 10),
                   cubic((0.45, 0.2), (0.55, 0.4), (0.65, 0.9), (0.55, 1.45), 10), [(-0.55, 1.45)])
    f1 = poly((-0.45, 0.2), (-0.56, -0.15), (0.56, -0.15), (0.45, 0.2))
    f2 = poly((-0.56, -0.15), (-0.64, -0.5), (0.64, -0.5), (0.56, -0.15))
    torso = [breast, f1, f2, [(0, 1.4), (0, 0.25)]]
    arms, ac = [], []
    for s in (-1, 1):
        a = tube(cubic((s * 0.95, 1.05), (s * 1.2, 0.4), (s * 0.95, -0.1), (s * 0.35, -0.2), 14), 0.34)
        p = ellipse(s * 0.88, 1.28, 0.45, 0.32, 30)
        arms += [a, p, quad((s * 0.45, 1.12), (s * 0.88, 0.92), (s * 1.3, 1.12), 8), circle(s * 1.1, 0.45, 0.15, 12)]
        ac += [a, p]
    blade = poly((-0.12, -0.55), (-0.12, -2.7), (0, -2.95), (0.12, -2.7), (0.12, -0.55))
    sw = [blade, rect(-0.6, -0.55, 0.6, -0.42), circle(0, 0.08, 0.12, 12), [(0, -0.7), (0, -2.5)]]
    hands = [ellipse(-0.2, -0.22, 0.2, 0.17, 16), ellipse(0.2, -0.22, 0.2, 0.17, 16)]
    gorget = poly((-0.35, 1.75), (-0.55, 1.45), (0.55, 1.45), (0.35, 1.75))
    helm = ellipse(0, 2.25, 0.42, 0.55, 40)
    head = [gorget, helm, lens((-0.3, 2.22), (0.3, 2.22), 0.16), [(0, 2.8), (0, 2.42)], lens((0.1, 2.75), (1.1, 3.35), 0.22), lens((0.0, 2.78), (0.6, 3.6), 0.2)]
    parts = paint([(cape, []), (legs, lc), (torso, [breast, f1, f2]), (arms, ac), (sw, [blade, rect(-0.6, -0.55, 0.6, -0.42), circle(0, 0.08, 0.12, 12)]),
                   (hands, hands), (head, [gorget, helm])])
    parts += [[(-2.4, -3.05), (2.4, -3.05)]]
    return make("Knight in Shining Armour", parts, [eye(x, y, 0.04) for x in (-0.2, 0.2) for y in (1.95, 1.8)])


def caparison_horse(gallop):
    """Horse in a flowing caparison, facing right. Returns (strokes, covers)."""
    body = chain([(1.0, 1.0)], cubic((1.0, 1.0), (0.0, 1.05), (-1.3, 1.05), (-1.8, 0.8), 12), cubic((-1.8, 0.8), (-2.2, 0.5), (-2.2, 0.0), (-2.15, -1.0), 10))
    hem = []
    xs = [-2.15 + 3.7 * k / 9 for k in range(10)]
    for a, b in zip(xs, xs[1:]):
        hem += arc((a + b) / 2, -1.0, (b - a) / 2, math.pi, 2 * math.pi, 8)
    body = chain(body, hem, [(1.55, -1.0)], cubic((1.55, -1.0), (1.65, -0.3), (1.7, 0.3), (1.95, 1.4), 10))
    head = [(1.95, 1.4), (2.15, 1.25), (2.55, 0.95), (2.8, 0.95), (2.88, 1.15), (2.6, 1.5), (2.0, 2.15), (1.85, 2.15)]
    neck_back = cubic((1.85, 2.15), (1.4, 1.75), (1.1, 1.3), (1.0, 1.0), 8)
    outline = chain(body, head, neck_back)
    ears = [poly((1.86, 2.15), (1.82, 2.42), (1.98, 2.17), closed=False)]
    chanfron = [poly((2.0, 2.0), (2.65, 1.35), (2.5, 1.2), (1.9, 1.85), closed=False)]
    crinet = [cubic((1.3, 1.7), (1.5, 1.5), (1.7, 1.3), (1.9, 1.3), 8)]
    emblem = [poly((-0.95, -0.55), (-0.95, 0.15), (-1.3, 0.15), (-1.3, 0.4), (-0.95, 0.4), (-0.95, 0.65), (-0.75, 0.65), (-0.75, 0.4), (-0.4, 0.4), (-0.4, 0.15),
                   (-0.75, 0.15), (-0.75, -0.55))]
    tail = [lens((-2.05, 0.55), (-2.85, -0.7), 0.25)]
    if gallop:
        legc = [[(1.1, -1.0), (1.7, -1.5), (2.2, -1.8)], [(0.8, -1.0), (0.9, -1.6), (0.5, -1.9)], [(-1.4, -1.0), (-1.8, -1.6), (-2.3, -2.0)],
                [(-1.0, -1.0), (-0.7, -1.6), (-0.6, -2.2)]]
    else:
        legc = [[(1.1, -0.9), (1.15, -1.6), (1.2, -2.3)], [(0.6, -0.9), (0.62, -1.6), (0.65, -2.3)], [(-1.2, -0.9), (-1.25, -1.6), (-1.3, -2.3)],
                [(-1.75, -0.9), (-1.8, -1.6), (-1.85, -2.3)]]
    legs = [tube(l, 0.24) for l in legc]
    hooves = [circle(l[-1][0], l[-1][1], 0.15, 12) for l in legc]
    strokes = paint([(legs + hooves + tail, []), ([outline] + ears + chanfron + crinet + emblem, [outline])])
    return strokes, [outline]


@design("castles_jousting_knight", T)
def jousting_knight(rng):
    horse, hc = caparison_horse(True)
    lance = tube([(-1.6 + 5.0 * t, 1.15 + 0.85 * t) for t in [i / 20 for i in range(21)]], lambda t: 0.26 - 0.18 * t)
    vamp = poly((0.35, 1.5), (0.75, 1.15), (0.85, 2.0))
    flag = pennant(2.6, 1.95, 0.8, 0.3, True)
    torso = poly((-0.35, 0.95), (0.45, 0.95), (0.4, 2.15), (-0.3, 2.15))
    helm = rrect(-0.28, 2.15, 0.42, 2.85, 0.12)
    rider = [torso, helm, [(0.1, 2.5), (0.42, 2.5)], lens((-0.1, 2.85), (-1.0, 3.3), 0.25), lens((0.0, 2.85), (-0.5, 3.5), 0.22)]
    legr = tube([(0.05, 1.0), (0.2, 0.3), (0.15, -0.35)], 0.3)
    foot = poly((0.0, -0.35), (0.55, -0.4), (0.5, -0.55), (0.0, -0.5))
    shield = heater(0.05, 1.45, 1.0, 1.3)
    sh = [shield, [(0.05, 2.1), (0.05, 0.8)], [(-0.42, 1.75), (0.52, 1.75)]]
    parts = paint([(horse, []), ([lance, vamp, flag], [lance, vamp]), ([legr, foot] + rider, [torso, helm, legr]), (sh, [shield])])
    parts += [[(-3.4, -2.5), (3.4, -2.5)], [(-3.4, -1.5), (-2.9, -1.5)], [(2.6, -1.5), (3.4, -1.5)]]
    return make("Jousting Knight at the Tournament", parts, [eye(2.3, 1.6, 0.05)])


@design("castles_barded_horse", T)
def barded_horse(rng):
    horse, hc = caparison_horse(False)
    saddle = [chain(quad((-1.0, 1.05), (-1.05, 1.5), (-0.8, 1.5), 6), quad((-0.8, 1.5), (-0.2, 1.1), (0.35, 1.35), 10), quad((0.35, 1.35), (0.5, 1.3), (0.45, 1.05), 4)),
              [(-0.25, 0.95), (-0.25, -0.2)], rrect(-0.45, -0.35, -0.05, -0.2, 0.05)]
    plume = [lens((1.95, 2.2), (1.5, 3.1), 0.3), lens((1.98, 2.2), (2.1, 3.2), 0.28)]
    parts = horse + saddle + plume + [[(-3.0, -2.45), (3.2, -2.45)]]
    parts += [pennant(-2.6, 2.6, 1.2, 0.4, True), [(-2.6, 2.6), (-2.6, -2.45)]]
    return make("Warhorse in Caparison", parts, [eye(2.3, 1.6, 0.05)])


@design("castles_king_on_throne", T)
def king_on_throne(rng):
    throne = [gothic(-1.5, 1.5, -0.3, 3.8, n=24), circle(0, 3.95, 0.15, 12)]
    for s in (-1, 1):
        x0, x1 = sorted((s * 1.5, s * 1.8))
        throne += [rect(x0, -2.4, x1, 2.9), circle(s * 1.65, 3.05, 0.15, 12), rect(min(s * 1.5, s * 1.0), -0.35, max(s * 1.5, s * 1.0), -0.15)]
    throne += [rect(-1.5, -0.9, 1.5, -0.6), rect(-2.4, -3.0, 2.4, -2.7), rect(-2.0, -2.7, 2.0, -2.4), gothic(-0.9, 0.9, 1.0, 3.1)]
    robe = chain([(-0.3, 1.3), (-0.95, 1.1)], cubic((-0.95, 1.1), (-1.3, 0.4), (-1.35, -0.5), (-1.3, -1.0), 10), [(-1.25, -2.3), (1.25, -2.3), (1.3, -1.0)],
                 cubic((1.3, -1.0), (1.35, -0.5), (1.3, 0.4), (0.95, 1.1), 10), [(0.3, 1.3)])
    collar = quad((-0.95, 1.1), (0, 0.55), (0.95, 1.1), 14)
    body = [robe, collar, [(-0.25, 0.75), (-0.4, -2.3)], [(0.25, 0.75), (0.4, -2.3)], quad((-1.3, -0.95), (0, -0.75), (1.3, -0.95), 12),
            ellipse(-0.5, -2.4, 0.3, 0.13, 16), ellipse(0.5, -2.4, 0.3, 0.13, 16)]
    head = circle(0, 1.65, 0.38, 30)
    crown = poly((-0.38, 1.95), (-0.45, 2.55), (-0.22, 2.3), (0, 2.65), (0.22, 2.3), (0.45, 2.55), (0.38, 1.95))
    face = [head, crown, [(-0.38, 2.1), (0.38, 2.1)], chain(quad((-0.36, 1.55), (-0.35, 1.0), (0, 0.9), 8), quad((0, 0.9), (0.35, 1.0), (0.36, 1.55), 8)),
            quad((-0.22, 1.45), (0, 1.38), (0.22, 1.45), 6), [(0, 1.7), (-0.04, 1.52)]]
    rcov = closed(robe)
    sceptre = [[(-0.95, -0.9), (-0.95, 1.7)], circle(-0.95, 1.85, 0.15, 12)] + fleur(-0.95, 2.05, 0.4)
    hand_l = circle(-0.95, -0.05, 0.18, 14)
    orb = [circle(0.95, 0.15, 0.32, 24), [(0.63, 0.15), (1.27, 0.15)], [(0.95, 0.47), (0.95, 0.75)], [(0.82, 0.62), (1.08, 0.62)], ellipse(0.95, -0.25, 0.2, 0.12, 12)]
    parts = paint([(throne, []), (body, [rcov]), (face, [head, crown]), (sceptre + [hand_l], [hand_l]), (orb, [orb[0], orb[4]])])
    hints = [eye(-0.13, 1.75, 0.045), eye(0.13, 1.75, 0.045)] + [eye(x, y, 0.05) for x, y in ((-0.6, 0.98), (-0.3, 0.82), (0.3, 0.82), (0.6, 0.98), (0.0, 0.75))]
    return make("King on his Throne", parts, hints)


@design("castles_queen_portrait", T)
def queen_portrait(rng):
    frame = [ellipse(0, 0, 2.9, 3.3, 120), ellipse(0, 0, 2.55, 2.95, 110)]
    hair = [chain(cubic((-0.1, 1.95), (-1.1, 2.0), (-1.2, 0.6), (-1.0, -0.4), 16), cubic((-1.0, -0.4), (-0.9, -1.2), (-1.3, -1.6), (-1.5, -1.9), 10)),
            chain(cubic((0.1, 1.95), (1.1, 2.0), (1.2, 0.6), (1.0, -0.4), 16), cubic((1.0, -0.4), (0.9, -1.2), (1.3, -1.6), (1.5, -1.9), 10))]
    gown = [chain(cubic((-2.45, -1.6), (-1.6, -0.8), (-0.8, -0.9), (-0.32, -0.55), 12)), chain(cubic((2.45, -1.6), (1.6, -0.8), (0.8, -0.9), (0.32, -0.55), 12)),
            quad((-1.3, -1.05), (0, -2.0), (1.3, -1.05), 16), [(-0.3, -1.85), (-0.5, -2.9)], [(0.3, -1.85), (0.5, -2.9)]]
    neck = [[(-0.3, 0.1), (-0.32, -0.55)], [(0.3, 0.1), (0.32, -0.55)], quad((-0.55, -0.6), (0, -1.05), (0.55, -0.6), 12), lens((0, -1.05), (0, -1.4), 0.4)]
    face = ellipse(0, 0.85, 0.72, 0.95, 50)
    feats = [lens((-0.5, 0.95), (-0.12, 0.95), 0.3), lens((0.12, 0.95), (0.5, 0.95), 0.3), quad((-0.52, 1.18), (-0.3, 1.3), (-0.1, 1.18), 6),
             quad((0.1, 1.18), (0.3, 1.3), (0.52, 1.18), 6), [(0.0, 0.85), (-0.06, 0.55), (0.06, 0.52)], quad((-0.22, 0.3), (0, 0.22), (0.22, 0.3), 6),
             quad((-0.22, 0.3), (0, 0.38), (0.22, 0.3), 6)]
    crown = poly((-0.75, 1.6), (-0.85, 2.4), (-0.45, 2.1), (-0.2, 2.6), (0.0, 2.2), (0.2, 2.6), (0.45, 2.1), (0.85, 2.4), (0.75, 1.6))
    crown_d = [quad((-0.75, 1.85), (0, 1.75), (0.75, 1.85), 10)]
    parts = paint([(frame + hair + gown, []), (neck, []), ([face] + feats, [face]), ([crown] + crown_d, [crown])])
    hints = [eye(-0.31, 0.95, 0.07), eye(0.31, 0.95, 0.07), eye(-0.45, 1.67, 0.05), eye(0, 1.65, 0.06), eye(0.45, 1.67, 0.05)]
    return make("Medieval Queen Portrait", parts, hints)


@design("castles_court_jester", T)
def jester(rng):
    hat = [chain(quad((-0.45, 2.2), (-1.1, 3.0), (-1.55, 1.95), 12), quad((-1.55, 1.95), (-0.9, 2.4), (-0.15, 2.3), 12)),
           chain(quad((0.45, 2.2), (1.1, 3.0), (1.55, 1.95), 12), quad((1.55, 1.95), (0.9, 2.4), (0.15, 2.3), 12)),
           chain(quad((-0.25, 2.3), (-0.2, 3.0), (0.35, 3.4), 10), quad((0.35, 3.4), (0.15, 2.9), (0.25, 2.3), 10)),
           rrect(-0.5, 2.0, 0.5, 2.3, 0.08), circle(-1.6, 1.8, 0.15, 12), circle(1.6, 1.8, 0.15, 12), circle(0.45, 3.5, 0.15, 12)]
    head = [circle(0, 1.6, 0.42, 30), quad((-0.22, 1.42), (0, 1.25), (0.22, 1.42), 8), circle(0, 1.58, 0.07, 8)]
    collar = [[(-1.0, 1.05)] + [p for k in range(5) for p in ((-0.8 + 0.4 * k, 0.6), (-0.6 + 0.4 * k, 1.05))] + [(1.0, 1.05)]]
    collar = [chain([(-1.0, 1.05)], [(-0.8 + 0.4 * k + d, 0.6 if d == 0 else 1.05) for k in range(5) for d in (0, 0.2)][:-1], [(1.0, 1.05)]), [(-1.0, 1.05), (1.0, 1.05)]]
    tunic = poly((-0.8, 0.9), (-0.95, -0.6), (-0.5, -0.85), (0.0, -0.6), (0.5, -0.85), (0.95, -0.6), (0.8, 0.9))
    pat = [[(0, 0.9), (0, -0.6)], poly((-0.45, 0.6), (-0.7, 0.2), (-0.45, -0.2), (-0.2, 0.2)), poly((0.45, 0.3), (0.7, -0.1), (0.45, -0.5), (0.2, -0.1))]
    armL = tube([(-0.75, 0.75), (-1.3, 1.0), (-1.7, 1.45)], 0.3)
    stick = [[(-1.75, 1.1), (-2.05, 2.5)], circle(-2.1, 2.7, 0.22, 16), poly((-2.3, 2.85), (-2.55, 3.15), (-2.1, 2.95), (-1.75, 3.25), (-1.9, 2.85), closed=False)]
    armR = tube([(0.75, 0.75), (1.25, 0.3), (0.9, -0.15)], 0.3)
    legs = []
    for s in (-1, 1):
        legs.append(tube([(s * 0.35, -0.65), (s * 0.45, -1.6), (s * 0.55, -2.5)], 0.34))
        legs.append(chain([(s * 0.38, -2.5), (s * 0.4, -2.75), (s * 1.1, -2.72)], quad((s * 1.1, -2.72), (s * 1.5, -2.65), (s * 1.35, -2.35), 6),
                          [(s * 1.15, -2.45), (s * 0.72, -2.5)]))
        legs.append(circle(s * 1.38, -2.25, 0.1, 8))
    parts = paint([(legs, [legs[0], legs[3]]), ([tunic] + pat, [tunic]), ([armR], [armR]), (stick, []), ([armL], [armL]), (collar, [closed(collar[0])]),
                   (head, [head[0]]), (hat, [closed(h) for h in hat[:3]] + [hat[3]])])
    hints = [eye(-0.15, 1.72, 0.05), eye(0.15, 1.72, 0.05)] + [eye(-0.8 + 0.4 * k, 0.55, 0.06) for k in range(5)]
    return make("Court Jester", parts + [[(-2.6, -2.8), (2.6, -2.8)]], hints)


@design("castles_archer_longbow", T)
def archer(rng):
    quiver = transform(rrect(-0.2, -0.9, 0.2, 0.9, 0.1), dx=-0.45, dy=1.1, rot=-0.35)
    flet = [transform(lens((x, 0.9), (x, 1.45), 0.25), dx=-0.45, dy=1.1, rot=-0.35) for x in (-0.1, 0.12)]
    legs = [tube([(0.25, -0.3), (0.75, -1.5), (0.9, -2.7)], 0.32), tube([(-0.2, -0.3), (-0.6, -1.5), (-0.95, -2.7)], 0.32)]
    boots = [poly((0.75, -2.55), (0.75, -2.95), (1.35, -2.95), (1.1, -2.6)), poly((-1.1, -2.55), (-1.1, -2.95), (-0.5, -2.95), (-0.75, -2.6))]
    tunic = poly((-0.35, 1.45), (0.4, 1.45), (0.55, -0.4), (0.2, -0.25), (0.0, -0.45), (-0.25, -0.25), (-0.55, -0.4))
    belt = [[(-0.45, 0.25), (0.47, 0.25)], [(-0.45, 0.05), (0.47, 0.05)]]
    back_arm = tube([(0.0, 1.3), (-0.6, 1.62), (0.0, 1.68)], 0.22)
    head = circle(0.2, 1.9, 0.3, 24)
    hood = chain(arc(0.2, 1.9, 0.42, 0.25, 2.5, 16), [(-0.7, 1.55), (-0.05, 1.45)])
    front_arm = tube([(0.3, 1.3), (1.2, 1.35), (2.15, 1.38)], 0.22)
    bowc = quad((1.85, 3.1), (2.85, 1.38), (1.85, -0.35), 30)
    bow = tube(bowc, lambda t: 0.08 + 0.1 * (1 - abs(2 * t - 1)))
    string = [bowc[0], (0.0, 1.66), bowc[-1]]
    arrow = [[(0.0, 1.62), (2.75, 1.42)], poly((2.75, 1.32), (3.05, 1.41), (2.76, 1.52)), lens((0.0, 1.62), (0.4, 1.83), 0.3), lens((0.0, 1.62), (0.4, 1.42), 0.3)]
    hand = circle(2.2, 1.38, 0.13, 12)
    parts = paint([([quiver] + flet, []), (legs + boots, legs + boots), ([tunic] + belt, [tunic]), ([back_arm], [back_arm]), ([head, hood], [closed(hood), head]),
                   ([string], []), ([front_arm], [front_arm]), ([bow], [bow]), (arrow, []), ([hand], [hand])])
    parts += [[(-2.6, -2.95), (3.0, -2.95)], cloud(-2.2, 2.5, 0.6)]
    return make("Archer Drawing a Longbow", parts, [eye(0.36, 1.95, 0.05)])


@design("castles_princess_tower", T)
def princess_tower(rng):
    tower = [[(-0.9, -3.0), (-0.9, 1.2)], [(0.9, -3.0), (0.9, 1.2)], poly((-1.1, 1.2), (0, 2.9), (1.1, 1.2))] + flagpole(0, 2.9, 0.45, 0.7, True)
    win = arch(-0.45, 0.45, -0.1, 1.0, True, 12)
    sill = rect(-0.6, -0.25, 0.6, -0.1)
    head = circle(0, 0.35, 0.2, 18)
    hennin = [poly((-0.15, 0.5), (0.35, 1.35), (0.18, 0.45)), cubic((0.35, 1.35), (0.9, 1.1), (1.3, 1.5), (1.8, 1.2), 12), cubic((0.3, 1.25), (0.8, 0.8), (1.2, 1.1), (1.7, 0.95), 12)]
    hennin = [poly((-0.17, 0.45), (0.3, 1.0), (0.17, 0.42)), cubic((0.3, 1.0), (0.8, 0.95), (1.3, 1.35), (1.8, 1.05), 12), cubic((0.27, 0.9), (0.8, 0.6), (1.2, 0.95), (1.7, 0.85), 12)]
    bc = [(0.05 + 0.07 * math.sin(3 * y), y) for y in [-0.05 - 2.2 * i / 30 for i in range(31)]]
    braid = [tube(bc, lambda t: 0.24 - 0.08 * t)] + [[(bc[i][0] - 0.1, bc[i][1] + 0.08), (bc[i][0] + 0.1, bc[i][1] - 0.08)] for i in range(3, 29, 3)]
    braid_cov = [braid[0]]
    ivy = [cubic((-0.9, -3.0), (-0.3, -2.0), (-1.0, -1.0), (-0.5, 0.0), 30)]
    leaves = [lens(p, (p[0] + 0.28 * (-1) ** k, p[1] + 0.12), 0.35) for k, p in enumerate(ivy[0][3::5])]
    win_back = hide([win], [closed(sill)])
    parts = paint([(tower, []), (win_back, []), ([head], [head]), (hennin, []), ([sill], [closed(sill)]),
                   (braid, braid_cov), (ivy + leaves, [])])
    parts += [ground(-3.4, 3.4, -3.0), cloud(-2.3, 2.4, 0.7), cloud(2.4, 2.8, 0.5), tree(2.6, -3.0, 1.0)]
    parts += [circle(-2.4 + 0.3 * k, -2.8 + 0.1 * (k % 2), 0.15, 12) for k in range(4)]
    return make("Princess in the Tower", parts, [eye(-0.07, 0.38, 0.035), eye(0.07, 0.38, 0.035)])


@design("castles_falconer", T)
def falconer(rng):
    cuff = poly((0.35, -1.25), (2.2, -3.0), (0.9, -3.4), (-0.4, -1.4))
    stitch = [[(0.15, -1.6), (1.6, -3.15)], [(1.2, -2.0), (0.6, -2.6)]]
    fist = rrect(-0.75, -1.45, 0.65, -0.7, 0.25)
    knuck = [[(-0.75 + 0.35 * k, -0.7), (-0.75 + 0.35 * k, -0.95)] for k in range(1, 4)]
    back = chain([(-0.25, 2.1)], cubic((-0.25, 2.1), (0.4, 2.05), (0.7, 1.4), (0.75, 0.6), 14), cubic((0.75, 0.6), (0.8, 0.0), (0.85, -0.4), (1.2, -1.6), 12),
                 [(0.85, -1.75)], cubic((0.85, -1.75), (0.6, -1.0), (0.3, -0.7), (0.05, -0.65), 10))
    front = chain([(0.05, -0.65)], cubic((0.05, -0.65), (-0.6, -0.6), (-0.8, 0.4), (-0.6, 1.2), 14), [(-0.85, 1.35), (-0.95, 1.2), (-0.75, 1.45)],
                  cubic((-0.75, 1.45), (-0.75, 1.9), (-0.55, 2.1), (-0.25, 2.1), 10))
    bird = chain(back, front[1:])
    wing = chain(cubic((-0.1, 1.3), (0.6, 1.1), (0.9, -0.2), (1.05, -1.4), 16), cubic((1.05, -1.4), (0.5, -0.6), (0.1, 0.3), (-0.1, 1.3), 14))
    feathers = [cubic((0.1, 0.9), (0.5, 0.6), (0.7, 0.0), (0.85, -0.6), 10), cubic((0.15, 0.4), (0.4, 0.2), (0.55, -0.2), (0.7, -0.6), 10)]
    hood = [chain(arc(-0.4, 1.65, 0.45, -0.3, 2.6, 16)), lens((-0.3, 2.1), (-0.15, 2.6), 0.4), [(-0.75, 1.45), (-0.1, 1.25)]]
    breast = [quad((-0.55, 0.8), (-0.4, 0.7), (-0.3, 0.8), 4), quad((-0.5, 0.2), (-0.35, 0.1), (-0.2, 0.2), 4), quad((-0.35, 0.5), (-0.2, 0.4), (-0.05, 0.5), 4)]
    talons = [[(-0.3, -0.62), (-0.35, -0.85)], [(0.0, -0.65), (0.0, -0.85)]]
    jess = [cubic((-0.2, -0.75), (-0.5, -1.6), (-0.9, -1.9), (-1.1, -2.6), 12), cubic((0.0, -0.75), (-0.2, -1.6), (-0.4, -2.2), (-0.5, -2.8), 12),
            circle(-1.1, -2.75, 0.14, 12), circle(-0.5, -2.95, 0.14, 12)]
    parts = paint([([cuff] + stitch, [cuff]), ([fist] + knuck, [fist]), ([bird] + feathers + breast + talons, [closed(bird)]), ([wing], [wing]), (hood, [closed(hood[0])]),
                   (jess, [])])
    parts += [cloud(-2.3, 2.4, 0.6), cloud(2.2, 1.8, 0.6), poly((1.8, 3.0), (2.1, 3.15), (2.4, 3.0), closed=False)]
    return make("Falcon on a Falconer's Glove", parts)


# ---------------------------------------------------------------- royal treasures

@design("castles_jewelled_crown", T)
def jewelled_crown(rng):
    band = rrect(-2.0, -1.4, 2.0, -0.5, 0.1)
    ermine = rrect(-2.15, -2.0, 2.15, -1.4, 0.25)
    cap = chain(cubic((-1.8, -0.5), (-2.0, 1.2), (-0.8, 1.5), (0, 1.5), 16), cubic((0, 1.5), (0.8, 1.5), (2.0, 1.2), (1.8, -0.5), 16))
    arches = [cubic((-1.9, -0.5), (-2.1, 1.0), (-1.0, 1.7), (0, 1.75), 20), cubic((0, 1.75), (1.0, 1.7), (2.1, 1.0), (1.9, -0.5), 20),
              cubic((-0.5, -0.5), (-0.55, 0.8), (-0.3, 1.6), (0, 1.75), 14), cubic((0.5, -0.5), (0.55, 0.8), (0.3, 1.6), (0, 1.75), 14)]
    arch_cov = [chain(arches[0], arches[1])]
    pts_ = []
    for x in (-1.5, 1.5):
        pts_ += fleur(x, -0.35, 0.55)
    crosses = [poly((-0.15, -0.5), (-0.15, -0.05), (-0.4, -0.05), (-0.4, 0.2), (-0.15, 0.2), (-0.15, 0.45), (0.15, 0.45), (0.15, 0.2), (0.4, 0.2), (0.4, -0.05),
                    (0.15, -0.05), (0.15, -0.5))]
    monde = [circle(0, 2.05, 0.3, 24), [(-0.3, 2.05), (0.3, 2.05)], rect(-0.07, 2.35, 0.07, 2.9), rect(-0.25, 2.55, 0.25, 2.69)]
    jewels = [ellipse(0, -0.95, 0.35, 0.25, 20), ellipse(-1.1, -0.95, 0.22, 0.25, 16), ellipse(1.1, -0.95, 0.22, 0.25, 16), lens((-1.75, -0.95), (-1.5, -0.95), 0.5),
              lens((1.5, -0.95), (1.75, -0.95), 0.5)]
    parts = paint([([cap], []), (arches + monde, arch_cov + [monde[0]]), ([band] + jewels + crosses + pts_, [band]), ([ermine], [ermine])])
    hints = [eye(x, -1.7, 0.07) for x in (-1.6, -0.8, 0.0, 0.8, 1.6)]
    hints += [eye(p[0], p[1], 0.06) for p in arches[0][4:18:4] + arches[1][4:18:4]]
    return make("Jewelled Royal Crown", parts, hints)


@design("castles_sceptre_orb_cushion", T)
def sceptre_orb(rng):
    cush = chain(cubic((-3.0, -0.9), (-1.5, -0.35), (1.5, -0.35), (3.0, -0.9), 20), cubic((3.0, -0.9), (2.6, -1.8), (2.6, -2.3), (3.0, -3.0), 10),
                 cubic((3.0, -3.0), (1.5, -2.6), (-1.5, -2.6), (-3.0, -3.0), 20), cubic((-3.0, -3.0), (-2.6, -2.3), (-2.6, -1.8), (-3.0, -0.9), 10))
    tassels = []
    for x, y, s in ((-3.0, -3.0, -1), (3.0, -3.0, 1), (-3.0, -0.9, -1), (3.0, -0.9, 1)):
        tassels += [circle(x, y, 0.12, 10), poly((x - 0.05, y - 0.1), (x - 0.25 * s - 0.1, y - 0.7), (x + 0.15 - 0.25 * s, y - 0.75)), ]
    seam = [cubic((-2.55, -1.15), (-1.2, -0.75), (1.2, -0.75), (2.55, -1.15), 16)]
    orb = [circle(0.9, 0.55, 1.15, 70), ellipse(0.9, 0.55, 1.15, 0.3, 50), [(0.9, -0.6), (0.9, 1.7)]]
    orbx = [rect(0.78, 1.7, 1.02, 2.65), rect(0.5, 2.05, 1.3, 2.3), circle(0.9, 1.67, 0.12, 10)]
    rod = tube([(-2.9 + 5.2 * t, -1.6 + 0.3 * t) for t in [i / 20 for i in range(21)]], 0.22)
    knobs = [ellipse(-0.5, -1.45, 0.14, 0.22, 12), ellipse(1.2, -1.35, 0.14, 0.22, 12), circle(2.45, -1.3, 0.18, 12)]
    head = [circle(-3.1, -1.6, 0.25, 18)] + [transform(p, dx=-3.4, dy=-1.62, rot=math.pi / 2 + 0.06) for p in fleur(0, 0, 0.6)]
    parts = paint([([cush] + seam + tassels, []), (orb + orbx, [orb[0]] + orbx[:2]), ([rod] + knobs + head, [rod, head[0]] + knobs)])
    return make("Sceptre and Orb on a Cushion", parts, [eye(0.45, 0.95, 0.08), eye(1.4, 0.95, 0.08), eye(0.9, 0.25, 0.08)])


@design("castles_royal_carriage", T)
def royal_carriage(rng):
    body = chain([(-1.6, 1.3)], quad((-1.6, 1.3), (-1.75, -0.2), (-1.4, -0.7), 10), quad((-1.4, -0.7), (0, -1.15), (1.5, -0.7), 14),
                 quad((1.5, -0.7), (1.8, -0.2), (1.6, 1.3), 10), [(-1.6, 1.3)])
    roof = [chain(quad((-1.8, 1.3), (-1.7, 1.6), (-1.3, 1.65), 6), [(1.3, 1.65)], quad((1.3, 1.65), (1.7, 1.6), (1.8, 1.3), 6), [(-1.8, 1.3)])]
    crown = [poly((-0.4, 1.65), (-0.5, 2.15), (-0.25, 1.95), (0, 2.3), (0.25, 1.95), (0.5, 2.15), (0.4, 1.65), closed=False)]
    win = [rrect(-0.55, 0.2, 0.55, 1.1, 0.15), quad((-0.55, 1.0), (-0.3, 0.6), (-0.45, 0.2), 6), quad((0.55, 1.0), (0.3, 0.6), (0.45, 0.2), 6)]
    door = [rrect(-0.75, -0.75, 0.75, 1.2, 0.15), [(0.55, -0.1), (0.7, -0.1)]]
    lamps = [rrect(-2.0, 0.5, -1.75, 0.95, 0.06), rrect(1.75, 0.5, 2.0, 0.95, 0.06)]
    wheels = []
    for cx, cy, r in ((-1.7, -1.9, 0.9), (1.9, -2.1, 0.7)):
        wheels += [circle(cx, cy, r, 50), circle(cx, cy, r - 0.12, 46), circle(cx, cy, 0.14, 10)]
        wheels += [[(cx + 0.14 * math.cos(a), cy + 0.14 * math.sin(a)), (cx + (r - 0.12) * math.cos(a), cy + (r - 0.12) * math.sin(a))] for a in [k * TAU / 10 for k in range(10)]]
    springs = [quad((-1.7, -1.9), (-2.4, -1.0), (-1.4, -0.75), 10), quad((1.9, -2.1), (2.6, -1.0), (1.45, -0.75), 10), [(-1.7, -1.9), (1.9, -2.1)]]
    box = [rect(1.9, 0.1, 2.9, 0.4), [(2.0, 0.1), (2.3, -1.3)], [(2.8, 0.1), (2.6, -1.3)], [(2.3, -1.3), (3.1, -1.3)], rect(2.6, 0.4, 2.8, 1.0)]
    parts = paint([(springs + box, []), ([body] + win + door + lamps, [body]), (roof + crown, []), (wheels, [wheels[0], wheels[13]])])
    parts += [ground(-3.0, 3.4, -2.8)]
    return make("Royal Coach", parts)


@design("castles_medieval_feast", T)
def feast(rng):
    cloth = chain([(-3.2, -0.3), (3.2, -0.3), (3.2, -1.3)], *[arc(3.2 - 0.4 * (k + 0.5), -1.3, 0.2, 0, -math.pi, 6) for k in range(16)], [(-3.2, -0.3)])
    legs = [[(-2.8, -1.5), (-2.8, -2.8)], [(-2.5, -1.5), (-2.5, -2.8)], [(2.8, -1.5), (2.8, -2.8)], [(2.5, -1.5), (2.5, -2.8)], [(-3.4, -2.8), (3.4, -2.8)]]
    platter = ellipse(0, -0.25, 1.6, 0.25, 50)
    pig = chain([(-1.1, -0.2)], cubic((-1.1, -0.2), (-1.3, 0.5), (-0.4, 0.95), (0.5, 0.8), 16),
                cubic((0.5, 0.8), (0.9, 0.75), (1.1, 0.5), (1.25, 0.2), 10), [(1.3, -0.05), (1.0, -0.2)])
    pig = [pig, circle(1.35, 0.15, 0.15, 12), poly((0.75, 0.75), (0.8, 1.0), (0.95, 0.75), closed=False), spiral(-1.2, 0.2, 0.03, 0.12, 1.2, 16),
           [(-0.6, -0.15), (-0.7, -0.4)], [(0.5, -0.15), (0.6, -0.4)]]
    gob = []
    for x in (-2.6, 2.6):
        gob += [chain(quad((x - 0.3, 0.8), (x - 0.3, 0.2), (x, 0.15), 8), quad((x, 0.15), (x + 0.3, 0.2), (x + 0.3, 0.8), 8)), ellipse(x, 0.8, 0.3, 0.08, 16),
                [(x, 0.15), (x, -0.2)], ellipse(x, -0.25, 0.22, 0.06, 12)]
    candle = [rect(-1.95, -0.25, -1.75, 1.3), lens((-1.85, 1.35), (-1.85, 1.8), 0.4), ellipse(-1.85, -0.25, 0.35, 0.08, 14), rect(1.75, -0.25, 1.95, 1.0),
              lens((1.85, 1.05), (1.85, 1.5), 0.4), ellipse(1.85, -0.25, 0.35, 0.08, 14)]
    bread = [ellipse(-3.0, -0.05, 0.3, 0.2, 18)]
    parts = paint([(legs, []), ([cloth], [cloth]), (gob + candle + bread + [platter], []), (pig, [closed(pig[0])])])
    return make("Medieval Banquet Table", parts, [eye(0.95, 0.45, 0.05)])


@design("castles_jewelled_goblet", T)
def goblet(rng):
    rim = ellipse(0, 2.2, 1.35, 0.3, 60)
    bowl = chain(cubic((-1.35, 2.2), (-1.35, 0.6), (-0.6, 0.2), (-0.18, 0.1), 20), cubic((0.18, 0.1), (0.6, 0.2), (1.35, 0.6), (1.35, 2.2), 20))
    band = cubic((-1.3, 1.4), (-0.6, 1.1), (0.6, 1.1), (1.3, 1.4), 20)
    stem = [[(-0.18, 0.1), (-0.15, -0.4)], [(0.18, 0.1), (0.15, -0.4)], ellipse(0, -0.65, 0.42, 0.28, 30), [(-0.15, -0.9), (-0.2, -1.8)], [(0.15, -0.9), (0.2, -1.8)]]
    foot = [chain(quad((-0.2, -1.8), (-0.4, -2.3), (-1.3, -2.5), 10), quad((-1.3, -2.5), (0, -2.85), (1.3, -2.5), 16), quad((1.3, -2.5), (0.4, -2.3), (0.2, -1.8), 10)),
            quad((-1.25, -2.45), (0, -2.2), (1.25, -2.45), 14)]
    gems = [ellipse(0, 0.85, 0.28, 0.2, 18), lens((-0.85, 0.95), (-0.45, 0.85), 0.4), lens((0.45, 0.85), (0.85, 0.95), 0.4), circle(0, -0.65, 0.13, 10)]
    gems += [ellipse(x, 1.7, 0.14, 0.18, 12) for x in (-0.8, -0.27, 0.27, 0.8)]
    sparkle = [star(-1.9, 2.6, 0.3, 4, 0.3), star(1.8, 0.6, 0.25, 4, 0.3)]
    parts = [rim, bowl, band] + stem + foot + gems + sparkle
    return make("Jewelled Goblet", parts)


@design("castles_royal_treasure_chest", T)
def treasure_chest(rng):
    box = rect(-2.2, -2.8, 2.2, -0.4)
    bands = [rect(-1.7, -2.8, -1.35, -0.4), rect(1.35, -2.8, 1.7, -0.4)]
    lock = [poly((-0.35, -0.4), (-0.35, -1.3), (0, -1.55), (0.35, -1.3), (0.35, -0.4)), circle(0, -0.85, 0.1, 8), [(0, -0.95), (0, -1.2)]]
    lid = [poly((-2.2, -0.4), (-2.0, 1.4), (2.0, 1.4), (2.2, -0.4), closed=False), quad((-2.0, 1.4), (0, 2.4), (2.0, 1.4), 20),
           [(-1.55, -0.4), (-1.4, 1.62)], [(1.55, -0.4), (1.4, 1.62)]]
    coins = [ellipse(x, y, 0.3, 0.12, 16) for x, y in ((-1.0, -0.25), (-0.4, -0.15), (0.4, -0.2), (1.0, -0.3), (-0.7, 0.0), (0.7, 0.0))]
    crown = [poly((-0.5, -0.05), (-0.6, 0.6), (-0.25, 0.35), (0, 0.75), (0.25, 0.35), (0.6, 0.6), (0.5, -0.05))]
    pearls = [circle(1.9 + 0.1 * math.sin(k), -0.5 - 0.22 * k, 0.11, 10) for k in range(6)]
    floor = [ellipse(-2.7, -2.9, 0.3, 0.12, 16), ellipse(2.8, -2.95, 0.3, 0.12, 16), ellipse(2.6, -2.7, 0.3, 0.12, 16), star(-2.8, 0.8, 0.3, 4, 0.3), star(2.8, 1.6, 0.3, 4, 0.3)]
    parts = paint([(lid + coins, []), (crown, [crown[0]]), ([box] + bands + lock, [box]), (pearls, pearls)]) + floor + [[(-3.4, -2.8), (3.4, -2.8)]]
    return make("Royal Treasure Chest", parts, [eye(0, 0.25, 0.08)])


# ---------------------------------------------------------------- castle life

@design("castles_castle_well", T)
def castle_well(rng):
    top = ellipse(0, -0.7, 1.7, 0.4, 60)
    sides = [[(-1.7, -0.7), (-1.7, -2.6)], [(1.7, -0.7), (1.7, -2.6)], [(x, -2.6 - 0.4 * math.sqrt(max(0, 1 - (x / 1.7) ** 2))) for x in [-1.7 + 3.4 * i / 40 for i in range(41)]]]
    rows = []
    for r, y in enumerate((-1.2, -1.7, -2.2)):
        rows.append([(x, y - 0.4 * math.sqrt(max(0, 1 - (x / 1.7) ** 2))) for x in [-1.7 + 3.4 * i / 40 for i in range(41)]])
        for k in range(4):
            x = -1.35 + 0.9 * k + (0.45 if r % 2 else 0)
            if abs(x) < 1.6:
                yy = y - 0.4 * math.sqrt(max(0, 1 - (x / 1.7) ** 2))
                rows.append([(x, yy), (x, yy + 0.5)])
    posts = [[(-1.45, -0.6), (-1.45, 1.8)], [(-1.25, -0.75), (-1.25, 1.8)], [(1.45, -0.6), (1.45, 1.8)], [(1.25, -0.75), (1.25, 1.8)]]
    roof = [poly((-2.1, 1.7), (0, 3.0), (2.1, 1.7)), [(-1.05, 1.7), (-0.7, 2.56)], [(0, 1.7), (0, 3.0)], [(1.05, 1.7), (0.7, 2.56)]]
    axle = [rect(-1.25, 0.95, 1.25, 1.15), [(1.45, 1.05), (1.9, 1.05), (1.9, 0.5), (2.2, 0.5)]]
    rope = [[(0.0, 0.95), (0.0, 0.2)]]
    bucket = [poly((-0.4, 0.05), (-0.3, -0.55), (0.3, -0.55), (0.4, 0.05)), arc(0, 0.05, 0.4, 0, math.pi, 10), [(-0.37, -0.15), (0.37, -0.15)]]
    parts = paint([(posts[1::2] + [top], []), (rope + bucket, [bucket[0]]), (sides + rows + posts[0::2] + roof + axle, [])])
    parts += [[(-3.2, -2.75), (-1.7, -2.75)], [(1.7, -2.75), (3.2, -2.75)]]
    parts += [circle(x, -2.55, 0.15, 10) for x in (-2.6, -2.2, 2.3)] + [[(x, -2.75), (x, -2.4)] for x in (-2.6, -2.2, 2.3)]
    return make("Castle Courtyard Well", parts)


@design("castles_blacksmith_anvil", T)
def anvil(rng):
    a = chain([(-0.9, 0.3)], cubic((-0.9, 0.3), (-1.8, 0.3), (-2.6, 0.55), (-3.0, 0.9), 12), cubic((-3.0, 0.9), (-2.4, 0.95), (-1.6, 1.0), (-0.9, 1.0), 10),
              [(1.9, 1.0), (1.9, 0.4), (0.9, 0.3)], quad((0.9, 0.3), (0.5, 0.0), (0.6, -0.6), 8), [(1.2, -0.9), (1.2, -1.1), (-1.2, -1.1), (-1.2, -0.9), (-0.6, -0.6)],
              quad((-0.6, -0.6), (-0.5, 0.0), (-0.9, 0.3), 8))
    stump = [chain([(-1.5, -1.1), (-1.6, -2.8)], [(1.6, -2.8), (1.5, -1.1)]), ellipse(0, -1.1, 1.5, 0.2, 40), [(-0.6, -1.5), (-0.65, -2.4)], [(0.7, -1.6), (0.65, -2.6)]]
    hammer = [transform(rrect(-0.1, 0.0, 0.1, 2.0, 0.06), dx=0.9, dy=1.05, rot=-1.1), transform(rrect(-0.3, -0.25, 0.4, 0.25, 0.06), dx=0.9 + 2.05 * math.cos(-1.1 + math.pi / 2), dy=1.05 + 2.05 * math.sin(-1.1 + math.pi / 2), rot=-1.1)]
    shoe = [[(p[0], 1.0 + (p[1] - 1.0) * 0.4) for p in arc(-0.6, 1.0, 0.45, 0.0, math.pi, 16)]]
    sparks = [[(-0.6 + 0.4 * math.cos(q), 1.4 + 0.4 * math.sin(q)), (-0.6 + 0.9 * math.cos(q), 1.4 + 0.9 * math.sin(q))] for q in (0.6, 1.2, 1.9, 2.5)]
    sparks += [star(-1.8, 2.4, 0.2, 4, 0.35), star(0.2, 2.7, 0.2, 4, 0.35)]
    tongs = [[(2.3, -2.8), (2.6, 0.6), (2.5, 1.2)], [(2.55, -2.8), (2.75, 0.6), (2.75, 1.2)]]
    parts = paint([(tongs, []), (stump, [stump[1] + [(1.6, -2.8), (-1.6, -2.8)]]), ([a], [a]), (shoe + hammer, hammer), (sparks, [])])
    parts += [[(-3.4, -2.8), (3.4, -2.8)]]
    return make("Blacksmith's Anvil and Hammer", parts)


@design("castles_scroll_wax_seal", T)
def scroll_seal(rng):
    sheet = [[(-2.0, 2.2), (-2.1, -1.9)], [(2.0, 2.2), (2.1, -1.9)]]
    top = [rrect(-2.4, 2.2, 2.4, 2.75, 0.27), spiral(2.4, 2.47, 0.04, 0.2, 1.2, 20), spiral(-2.4, 2.47, 0.04, 0.2, 1.2, 20)]
    bot = [rrect(-2.5, -2.45, 2.5, -1.9, 0.27), spiral(2.5, -2.17, 0.04, 0.2, 1.2, 20), spiral(-2.5, -2.17, 0.04, 0.2, 1.2, 20)]
    text = [wave(-1.6, 1.6, 1.6, 0.04, 6, 50), wave(-1.6, 1.2, 1.1, 0.04, 5, 40), wave(-1.6, 1.6, 0.6, 0.04, 6, 50), wave(-1.6, 0.8, 0.1, 0.04, 4, 30),
            wave(-1.6, 1.4, -0.4, 0.04, 5, 40), quad((0.2, -1.0), (0.8, -0.7), (1.6, -1.0), 10)]
    seal = [star(0.0, -1.5, 0.7, 14, 0.88), circle(0, -1.5, 0.45, 30)] + [transform(p, dx=0, dy=-1.55, s=1.0) for p in fleur(0, 0, 0.42)]
    ribbons = [poly((-0.35, -2.0), (-0.75, -3.1), (-0.5, -2.95), (-0.35, -3.2), (-0.05, -2.15)), poly((0.35, -2.0), (0.75, -3.1), (0.5, -2.95), (0.35, -3.2), (0.05, -2.15))]
    parts = paint([(sheet + text, []), (ribbons, ribbons), (seal, [seal[0]]), (top + bot, [top[0], bot[0]])])
    return make("Royal Scroll with Wax Seal", parts)


@design("castles_round_table", T)
def round_table(rng):
    top = ellipse(0, -0.2, 2.8, 1.1, 90)
    edge = [(x, -0.2 - 0.3 - 1.1 * math.sqrt(max(0, 1 - (x / 2.8) ** 2))) for x in [-2.8 + 5.6 * i / 60 for i in range(61)]]
    inner = ellipse(0, -0.2, 0.8, 0.32, 40)
    rays = [[(0.8 * math.cos(a), -0.2 + 0.32 * math.sin(a)), (2.8 * math.cos(a), -0.2 + 1.1 * math.sin(a))] for a in [k * TAU / 12 + 0.26 for k in range(12)]]
    rose = [star(0, -0.2, 0.3, 5, 0.5)]
    tbl = [top, [(-2.8, -0.2), (-2.8, -0.5)], [(2.8, -0.2), (2.8, -0.5)], edge, inner] + rays + rose
    legs = [[(-1.2, -1.5), (-1.3, -2.9)], [(1.2, -1.5), (1.3, -2.9)], [(-0.3, -1.6), (-0.3, -3.0)], [(0.3, -1.6), (0.3, -3.0)]]
    chairs = []
    for x, y in ((-2.3, 0.4), (-1.2, 0.85), (0.0, 1.0), (1.2, 0.85), (2.3, 0.4)):
        chairs.append(chain([(x - 0.35, y - 0.4)], [(x - 0.35, y + 1.2)], arc(x, y + 1.2, 0.35, math.pi, 0, 10), [(x + 0.35, y - 0.4)]))
        chairs.append(gothic(x - 0.18, x + 0.18, y + 0.5, y + 1.25, True, 6))
    parts = paint([(chairs, []), (legs, []), (tbl, [top, edge + [(2.8, -0.2), (-2.8, -0.2)]])])
    sw, sc = sword((-1.4, -0.45), 0.05, 2.8, gw=0.7, bw=0.18)
    parts = hide(parts, sc) + sw
    return make("The Round Table", parts + [[(-3.4, -3.0), (3.4, -3.0)]])


@design("castles_armoured_gauntlet", T)
def gauntlet(rng):
    cuff = chain(cubic((-1.0, -0.9), (-1.2, -1.8), (-1.6, -2.6), (-1.9, -3.2), 10), [(1.9, -3.2)], cubic((1.9, -3.2), (1.6, -2.6), (1.2, -1.8), (1.0, -0.9), 10))
    cuff_lines = [quad((-1.25, -1.9), (0, -2.05), (1.25, -1.9), 14), quad((-1.6, -2.7), (0, -2.85), (1.6, -2.7), 14)]
    back = chain([(-1.05, -0.9)], quad((-1.05, -0.9), (-1.2, 0.3), (-0.95, 0.95), 10), [(1.0, 0.95)],
                 quad((1.0, 0.95), (1.2, 0.0), (1.05, -0.9), 10), [(-1.05, -0.9)])
    lames = [quad((-1.1, y), (0, y + 0.2), (1.1, y), 12) for y in (-0.5, -0.1, 0.35)]
    fingers = []
    for k, (x, ang, L) in enumerate(((-0.75, 0.12, 1.7), (-0.25, 0.03, 1.95), (0.25, -0.03, 1.85), (0.75, -0.12, 1.5))):
        segs = 3
        h = L / segs
        for j in range(segs):
            seg = rrect(-0.22, j * h, 0.22, (j + 1) * h + 0.06, 0.12)
            fingers.append(transform(seg, dx=x, dy=0.95, rot=ang))
    thumb = []
    for j in range(2):
        thumb.append(transform(rrect(-0.24, j * 0.6, 0.24, (j + 1) * 0.6 + 0.06, 0.13), dx=-1.15, dy=-0.4, rot=0.75))
    rivets = [eye(-0.8, -0.7, 0.06), eye(0.8, -0.7, 0.06), eye(0, -2.4, 0.06), eye(-1.2, -2.4, 0.06), eye(1.2, -2.4, 0.06)]
    parts = paint([(thumb, thumb), ([cuff] + cuff_lines, [closed(cuff)]), ([back] + lames, [back]), (fingers, fingers)])
    return make("Armoured Gauntlet", parts, rivets)


@design("castles_dungeon_door", T)
def dungeon_door(rng):
    door = arch(-1.4, 1.4, -2.8, 1.6, True, 30)
    frame = arch(-1.9, 1.9, -2.8, 2.1, False, 30)
    vous = [[(1.4 * math.cos(a), 0.2 + 1.4 * math.sin(a)), (1.9 * math.cos(a), 0.2 + 1.9 * math.sin(a))] for a in [math.pi * k / 7 for k in range(1, 7)]]
    planks = [[(x, -2.8), (x, 0.2 + math.sqrt(max(0, 1.4 ** 2 - x ** 2)))] for x in (-0.7, 0.0, 0.7)]
    straps = [rect(-1.4, y, 1.4, y + 0.25) for y in (-2.2, -0.6)]
    grille = [rect(-0.45, 0.3, 0.45, 1.0)] + [[(x, 0.3), (x, 1.0)] for x in (-0.15, 0.15)]
    ring = [circle(0.95, -1.3, 0.22, 16), circle(0.95, -1.0, 0.07, 8)]
    parts = paint([(planks, []), (straps + grille, straps + [grille[0]]), (ring, [])]) + [door, frame] + vous
    blocks = [rect(-3.3, -2.0, -2.4, -1.5), rect(-3.0, -0.8, -2.1, -0.3), rect(-3.3, 0.6, -2.4, 1.1), rect(2.2, -1.6, 3.1, -1.1), rect(2.5, 0.0, 3.3, 0.5),
              rect(2.1, 1.5, 3.0, 2.0), rect(-1.0, 2.6, 0.0, 3.1), rect(0.4, 2.8, 1.4, 3.3)]
    chainl = [ellipse(-2.75, 2.5 - 0.3 * k, 0.09 if k % 2 else 0.13, 0.18, 12) for k in range(5)] + [chain(arc(-2.75, 0.85, 0.3, math.pi * 0.2, math.pi * 1.8, 16))]
    chainl[-1] = chain(arc(-2.75, 0.75, 0.32, math.pi * 0.6, math.pi * 2.4, 18))
    parts += blocks + chainl + [[(-3.4, -2.8), (3.4, -2.8)]]
    hints = [eye(x, y + 0.125, 0.05) for x in (-1.15, -0.35, 0.35, 1.15) for y in (-2.2, -0.6)]
    return make("Dungeon Door", parts, hints)


@design("castles_torch_sconce", T)
def torch_sconce(rng):
    blocks = []
    for r, y in enumerate([-3.0 + 0.8 * k for k in range(8)]):
        off = 0.6 if r % 2 else 0.0
        blocks.append([(-3.2, y), (3.2, y)])
        blocks += [[(x, y), (x, y + 0.8)] for x in [-2.6 + off + 1.2 * k for k in range(5)] if -3.2 < x < 3.2]
    plate = rrect(-0.35, -2.2, 0.35, -0.8, 0.15)
    arm = [quad((0.0, -1.5), (1.2, -1.6), (1.4, -0.4), 12), quad((0.0, -1.1), (0.9, -1.2), (1.1, -0.4), 12), ellipse(1.25, -0.35, 0.45, 0.12, 20)]
    torch = [poly((1.12, -1.6), (0.95, 0.9), (1.55, 0.9), (1.38, -1.6), closed=False), [(1.12, -1.6), (1.38, -1.6)], rrect(0.85, 0.7, 1.65, 1.15, 0.1)]
    flame = chain(cubic((0.8, 1.15), (0.3, 1.9), (1.0, 2.4), (0.9, 3.2), 14), cubic((0.9, 3.2), (1.4, 2.6), (1.6, 2.9), (1.55, 3.4), 10),
                  cubic((1.55, 3.4), (2.1, 2.6), (2.1, 1.8), (1.7, 1.15), 14))
    inner = lens((1.25, 1.2), (1.2, 2.4), 0.3)
    cover = [plate, rrect(0.85, 0.7, 1.65, 1.15, 0.1), closed(flame), arm[2], [(1.12, -1.6), (0.95, 0.9), (1.55, 0.9), (1.38, -1.6)]]
    parts = hide(blocks, cover) + [plate, flame, inner] + arm + torch
    parts = paint([(hide(blocks, cover), []), ([plate], []), (arm, [arm[2]]), (torch, [torch[2], cover[-1]]), ([flame, inner], [])])
    hints = [eye(0, -1.0, 0.06), eye(0, -2.0, 0.06)]
    return make("Wall Torch in an Iron Sconce", parts, hints)


@design("castles_great_hall_fireplace", T)
def fireplace(rng):
    hood = poly((-2.6, 1.6), (-1.4, 3.4), (1.4, 3.4), (2.6, 1.6), closed=False)
    mantel = [rect(-3.2, 1.2, 3.2, 1.6), [(-2.9, 1.2), (-2.9, -3.0)], [(2.9, 1.2), (2.9, -3.0)]]
    opening = arch(-2.1, 2.1, -3.0, 0.7, n=30)
    vous = [[(2.1 * math.cos(q), -1.4 + 2.1 * math.sin(q)), (2.6 * math.cos(q), -1.4 + 2.6 * math.sin(q))] for q in [math.pi * k / 6 for k in range(1, 6)]]
    vous = [[(x, -1.4 + math.sqrt(4.41 - x * x)), (x * 1.24, -1.4 + 1.24 * math.sqrt(4.41 - x * x))] for x in (-1.8, -1.05, 0.0, 1.05, 1.8)]
    hearth = [[(-2.1, -2.6), (2.1, -2.6)], arc(0, -1.4, 2.55, 0.0, math.pi, 40)]
    logs = [transform(rrect(-1.2, -0.17, 1.2, 0.17, 0.17), dx=0, dy=-2.35, rot=0.12), transform(rrect(-1.2, -0.17, 1.2, 0.17, 0.17), dx=0, dy=-2.35, rot=-0.12)]
    flames = [lens((-0.7, -2.2), (-0.9, -0.9), 0.35), lens((0.0, -2.2), (0.1, -0.4), 0.35), lens((0.7, -2.2), (0.9, -1.0), 0.35), lens((-0.3, -2.1), (-0.35, -1.3), 0.3),
              lens((0.35, -2.1), (0.45, -1.4), 0.3)]
    pot = [chain(arc(0.0, 0.2, 0.6, math.pi * 1.0, math.pi * 2.0, 20)), rrect(-0.75, 0.15, 0.75, 0.35, 0.08), arc(0, 0.35, 0.5, 0.25, math.pi - 0.25, 12),
           [(0, 0.85), (0, 0.7)]]
    candles = []
    for x in (-2.95, 2.95):
        candles += [rect(x - 0.12, 1.6, x + 0.12, 2.3), lens((x, 2.35), (x, 2.75), 0.4), ellipse(x, 1.62, 0.3, 0.07, 12)]
    parts = paint([([hood] + mantel + [opening] + vous + hearth, []), (flames, []), (logs, logs), (pot, [pot[0] + [pot[0][0]]]), (candles, [])])
    parts += [[(-3.4, -3.0), (3.4, -3.0)]]
    return make("Great Hall Fireplace", parts)


@design("castles_stained_glass", T)
def stained_glass(rng):
    outer = gothic(-2.1, 2.1, -2.7, 3.4, True, 30)
    inner = gothic(-1.8, 1.8, -2.5, 3.0, True, 26)
    lanL = gothic(-1.55, -0.15, -2.3, 0.8, True, 12)
    lanR = gothic(0.15, 1.55, -2.3, 0.8, True, 12)
    rose = [circle(0, 1.85, 0.75, 40)] + [circle(0.32 * math.cos(a), 1.85 + 0.32 * math.sin(a), 0.3, 20) for a in [k * math.pi / 2 + math.pi / 4 for k in range(4)]]
    lead = [[(-1.55, y), (-0.15, y)] for y in (-1.6, -0.9)] + [[(0.15, y), (1.55, y)] for y in (-1.6, -0.9)]
    crossL = [poly((-0.95, -0.2), (-0.95, 0.15), (-1.2, 0.15), (-1.2, 0.4), (-0.95, 0.4), (-0.95, 0.6), (-0.75, 0.6), (-0.75, 0.4), (-0.5, 0.4), (-0.5, 0.15),
                   (-0.75, 0.15), (-0.75, -0.2))]
    flower = [circle(0.85, 0.15, 0.15, 12)] + [lens((0.85, 0.15), (0.85 + 0.4 * math.cos(a), 0.15 + 0.4 * math.sin(a)), 0.35) for a in [k * TAU / 5 + 0.3 for k in range(5)]]
    panes = [poly((-1.55, -2.3), (-0.85, -1.6), (-0.15, -2.3), closed=False), poly((0.15, -2.3), (0.85, -1.6), (1.55, -2.3), closed=False),
             poly((-1.55, -0.9), (-0.85, -1.6), (-0.15, -0.9), closed=False), poly((0.15, -0.9), (0.85, -1.6), (1.55, -0.9), closed=False)]
    sill = [rect(-2.4, -3.1, 2.4, -2.7)]
    blocks = [rect(-3.3, -1.0, -2.5, -0.5), rect(-3.3, 1.2, -2.5, 1.7), rect(2.5, -2.0, 3.3, -1.5), rect(2.5, 0.4, 3.3, 0.9), rect(-3.0, 2.6, -2.2, 3.1), rect(2.2, 2.6, 3.0, 3.1)]
    parts = [outer, inner, lanL, lanR] + rose + lead + crossL + flower + panes + sill + blocks
    return make("Stained-Glass Chapel Window", parts)


@design("castles_minstrel_lute", T)
def lute(rng):
    left = cubic((-0.28, 0.2), (-1.6, -0.2), (-1.5, -2.6), (0, -2.7), 24)
    body = chain(left, mirror_x(left)[::-1])
    neck = [rect(-0.28, 0.2, 0.28, 2.6)] + [[(-0.28, y), (0.28, y)] for y in (0.65, 1.1, 1.55, 2.0)]
    peg = [poly((-0.28, 2.6), (0.35, 3.4), (0.85, 3.2), (0.28, 2.6), closed=False)] + [[(0.2 + 0.18 * k, 2.95 + 0.0 * k + 0.12 * k), (0.0 + 0.18 * k, 3.2 + 0.12 * k)] for k in range(3)]
    rose = [circle(0, -0.7, 0.45, 30), star(0, -0.7, 0.35, 6, 0.5)]
    bridge = [rect(-0.45, -2.0, 0.45, -1.85)]
    strings = [[(-0.12, -1.85), (-0.12, 2.6)], [(0.12, -1.85), (0.12, 2.6)]]
    inst = paint([([body] + rose + bridge, []), (strings, bridge), (neck + peg, [neck[0]])])
    inst = [transform(p, dx=-0.6, dy=-0.2, rot=-0.55) for p in inst]
    notes = [ellipse(1.8, 1.0, 0.22, 0.16, 14, rot=0.4), [(1.99, 1.08), (1.99, 2.0)], quad((1.99, 2.0), (2.4, 1.8), (2.35, 1.4), 6),
             ellipse(2.4, 2.2, 0.2, 0.14, 14, rot=0.4), ellipse(3.0, 2.4, 0.2, 0.14, 14, rot=0.4), [(2.57, 2.27), (2.57, 3.0)], [(3.17, 2.47), (3.17, 3.2)],
             [(2.57, 3.0), (3.17, 3.2)]]
    return make("Minstrel's Lute", inst + notes)


@design("castles_tournament_tent", T)
def tournament_tent(rng):
    roof = poly((-2.3, 0.7), (0, 2.8), (2.3, 0.7), closed=False)
    val = chain([(-2.3, 0.7)], *[arc(-2.3 + 0.46 * (k + 0.5), 0.7, 0.23, math.pi, TAU, 6) for k in range(10)], [(2.3, 0.7), (-2.3, 0.7)])
    rlines = [[(0, 2.8), (x, 0.7)] for x in (-1.38, -0.46, 0.46, 1.38)]
    walls = [[(-2.05, 0.45), (-2.3, -2.6)], [(2.05, 0.45), (2.3, -2.6)], [(-2.3, -2.6), (2.3, -2.6)]]
    stripes = [[(x * 0.85, 0.45), (x, -2.6)] for x in (-1.4, 1.4)]
    door = [poly((-0.7, -2.6), (0, 0.45), (0.7, -2.6), closed=False), quad((-0.7, -2.6), (-0.6, -1.3), (-1.0, -1.0), 8), quad((0.7, -2.6), (0.6, -1.3), (1.0, -1.0), 8)]
    door = [quad((-0.05, 0.45), (-0.35, -1.0), (-1.0, -1.2), 10), quad((0.05, 0.45), (0.35, -1.0), (1.0, -1.2), 10), [(-1.0, -1.2), (-0.75, -2.6)], [(1.0, -1.2), (0.75, -2.6)]]
    top = [circle(0, 2.95, 0.15, 12)] + flagpole(0, 3.1, 0.6, 0.9, True)
    ropes = [[(-1.9, 1.1), (-3.2, -2.6)], [(1.9, 1.1), (3.2, -2.6)], [(-3.35, -2.6), (-3.05, -2.6)], [(3.05, -2.6), (3.35, -2.6)]]
    parts = paint([(stripes, []), ([roof] + rlines, []), ([val], [val]), (walls + door + top + ropes, [])])
    parts += [[(-3.4, -2.9), (3.4, -2.9)]]
    return make("Striped Tournament Pavilion", parts)


@design("castles_quill_inkwell", T)
def quill(rng):
    paper = poly((-3.2, -2.9), (-2.4, -1.0), (1.6, -1.0), (2.2, -2.9))
    lines_ = [[(-2.1 - 0.25 * (-1.0 - y) / 1.9, y), (1.3 + 0.3 * (-1.0 - y) / 1.9, y)] for y in (-1.4, -1.8, -2.2, -2.6)]
    well = [chain(quad((-0.9, -1.4), (-1.4, -0.2), (-0.6, 0.2), 10), [(0.6, 0.2)], quad((0.6, 0.2), (1.4, -0.2), (0.9, -1.4), 10), [(-0.9, -1.4)]),
            ellipse(0, 0.35, 0.6, 0.15, 24), [(-0.6, 0.2), (-0.6, 0.35)], [(0.6, 0.2), (0.6, 0.35)]]
    feather = [lens((-0.1, 0.4), (-2.2, 3.3), 0.16), [(0.15, 0.0), (-2.15, 3.2)]]
    barbs = [[(-0.2 - 0.3 * k, 0.75 + 0.42 * k), (-0.45 - 0.3 * k, 0.75 + 0.42 * k + 0.15)] for k in range(4)]
    candle = [rect(1.7, -0.6, 2.2, 1.9), lens((1.95, 1.95), (1.95, 2.6), 0.4), [(1.95, 1.9), (1.95, 2.05)], ellipse(1.95, -0.65, 0.65, 0.18, 24),
              quad((1.7, 1.9), (1.75, 1.4), (1.8, 1.6), 4)]
    parts = paint([([paper] + lines_, []), (well, [well[0], well[1]]), (feather + barbs, [feather[0]]), (candle, [candle[0], candle[3]])])
    return make("Quill, Inkwell and Candle", parts)


@design("castles_herald_trumpet", T)
def herald_trumpet(rng):
    tube_ = rrect(-2.9, 1.0, 1.4, 1.22, 0.1)
    bell = chain(cubic((1.4, 1.22), (2.2, 1.3), (2.7, 1.7), (3.1, 2.1), 12), [(3.1, 0.1)], cubic((3.1, 0.1), (2.7, 0.5), (2.2, 0.9), (1.4, 1.0), 12))
    mouth = [rrect(-3.3, 0.95, -2.9, 1.27, 0.08)]
    knobs = [ellipse(-1.2, 1.11, 0.12, 0.2, 12), ellipse(0.6, 1.11, 0.12, 0.2, 12)]
    banner = poly((-1.7, 1.0), (0.9, 1.0), (0.9, -1.8), (-0.4, -1.3), (-1.7, -1.8))
    deco = fleur(-0.4, -0.45, 0.8)
    tass = [[(-1.7, 1.0), (-2.0, 0.2)], circle(-2.0, 0.08, 0.12, 10), [(0.9, 1.0), (1.2, 0.2)], circle(1.2, 0.08, 0.12, 10)]
    notes = [ellipse(2.9, 2.9, 0.22, 0.16, 14, rot=0.4), [(3.09, 2.98), (3.09, 3.7)], quad((3.09, 3.7), (3.45, 3.5), (3.4, 3.2), 6)]
    parts = paint([([tube_] + mouth + knobs + [bell], []), ([banner] + deco, [banner]), (tass + notes, [])])
    return make("Herald's Trumpet with Banner", parts)


@design("castles_iron_lantern", T)
def lantern(rng):
    ring = circle(0, 2.85, 0.35, 24)
    cap = [poly((-1.1, 1.6), (-0.25, 2.5), (0.25, 2.5), (1.1, 1.6)), [(-1.3, 1.6), (1.3, 1.6)], rect(-0.3, 2.5, 0.3, 2.6)]
    body = [rect(-1.0, -1.6, 1.0, 1.6), [(0, -1.6), (0, 1.6)], [(-1.0, 0.0), (1.0, 0.0)]]
    base = [poly((-1.2, -1.6), (-0.9, -2.2), (0.9, -2.2), (1.2, -1.6)), rect(-0.5, -2.6, 0.5, -2.2)]
    candle = [rect(-0.25, -1.4, 0.25, -0.3), lens((0, -0.3), (0, 0.5), 0.35)]
    hook = [[(0, 3.2), (0, 3.5), (-2.6, 3.5)], [(-2.6, 3.7), (-2.6, 2.8)]]
    glow = [[(1.4 * math.cos(a), -0.1 + 1.4 * math.sin(a)), (1.9 * math.cos(a), -0.1 + 1.9 * math.sin(a))] for a in (0.3, -0.3, math.pi - 0.3, math.pi + 0.3)]
    parts = paint([(candle, []), (body, [])]) + [ring] + cap + base + hook + glow
    hints = [eye(x, 2.0, 0.06) for x in (-0.35, 0.0, 0.35)]
    return make("Iron Castle Lantern", parts, hints)


@design("castles_castle_keys", T)
def castle_keys(rng):
    ring = [circle(0, 2.3, 0.75, 50), circle(0, 2.3, 0.6, 46)]
    keys = []
    for k, (ang, L, kind) in enumerate(((-0.8, 4.0, 0), (0.0, 4.4, 1), (0.8, 3.8, 2))):
        loc = []
        if kind == 0:
            loc += [circle(0, 0, 0.42, 30), circle(0, 0, 0.2, 16)]
        elif kind == 1:
            loc += [poly((0, 0.45), (0.42, 0.0), (0, -0.45), (-0.42, 0.0)), circle(0, 0, 0.15, 12)]
        else:
            loc += [heart(0, -0.05, 0.45), circle(0, 0, 0.12, 10)]
        loc += [rect(-0.1, -L + 0.4, 0.1, -0.45), rect(-0.25, -0.75, 0.25, -0.6), poly((0.1, -L + 0.4), (0.55, -L + 0.4), (0.55, -L + 0.65), (0.35, -L + 0.65),
                                                                                       (0.35, -L + 0.85), (0.55, -L + 0.85), (0.55, -L + 1.05), (0.1, -L + 1.05), closed=False)]
        loc = [transform(p, dx=0, dy=-0.35, s=1.0) for p in loc]
        keys += [transform(p, dx=0.75 * math.sin(ang), dy=2.3 - 0.75 * math.cos(ang), rot=ang) for p in loc]
    parts = paint([(ring, []), (keys, [keys[0], keys[4], keys[8]])])
    return make("Ring of Castle Keys", parts)


@design("castles_battlements", T)
def battlements(rng):
    parts = [chain([(-3.4, -3.0), (-3.4, 0.2)], merlons(-3.4, 3.4, 0.2, 1.2, 4), [(3.4, 0.2), (3.4, -3.0)])]
    w = 6.8 / 7
    for k in range(4):
        x = -3.4 + 2 * k * w + w / 2
        parts.append(poly((x - 0.07, 0.4), (x - 0.07, 0.72), (x - 0.25, 0.72), (x - 0.25, 0.88), (x - 0.07, 0.88), (x - 0.07, 1.2), (x + 0.07, 1.2), (x + 0.07, 0.88),
                          (x + 0.25, 0.88), (x + 0.25, 0.72), (x + 0.07, 0.72), (x + 0.07, 0.4)))
    parts += [[(-3.4, -0.2), (3.4, -0.2)]]
    banner = poly((-0.6, -0.2), (-0.6, -2.4), (0.0, -2.0), (0.6, -2.4), (0.6, -0.2))
    parts += hide([rect(x, y, x + 0.8, y + 0.4) for x, y in ((-3.0, -1.0), (-2.0, -1.9), (-2.9, -2.7), (1.2, -0.9), (2.2, -1.6), (1.4, -2.5), (-1.6, -0.75))],
                  [banner])
    parts += [banner] + [transform(p, dx=0, dy=-1.2, s=1.0) for p in fleur(0, 0, 0.45)]
    land = [cubic((-3.4, 1.9), (-2.0, 2.6), (-1.0, 1.8), (0.4, 2.2), 20), cubic((0.4, 2.2), (1.5, 2.6), (2.5, 1.9), (3.4, 2.3), 16)]
    farcastle = [rect(1.5, 2.3, 1.9, 3.0), poly((1.45, 3.0), (1.7, 3.4), (1.95, 3.0), closed=False), rect(1.9, 2.3, 2.5, 2.7)]
    sky = hide(land + farcastle + [poly((-1.6, 2.8), (-1.4, 2.95), (-1.2, 2.8), closed=False)],
               [[(-3.4 + 2 * k * w, 0.2), (-3.4 + 2 * k * w, 1.45), (-3.4 + (2 * k + 1) * w, 1.45), (-3.4 + (2 * k + 1) * w, 0.2)] for k in range(4)])
    parts += sky + [[(x, -2.9), (x, -1.8)] for x in ()]
    return make("Castle Battlements with Arrow Loops", parts)


@design("castles_iron_chandelier", T)
def chandelier(rng):
    hoop = [ellipse(0, -0.4, 2.6, 0.55, 80), ellipse(0, -0.65, 2.6, 0.55, 80)]
    chains_ = [[(0, 3.3), (-2.0, -0.05)], [(0, 3.3), (2.0, -0.05)], [(0, 3.3), (0, 0.15)], circle(0, 3.45, 0.15, 12)]
    candles = []
    for k in range(7):
        a = math.pi + k * math.pi / 6
        x, y = 2.6 * math.cos(a), -0.4 + 0.55 * math.sin(a)
        candles += [rect(x - 0.13, y, x + 0.13, y + 0.75), lens((x, y + 0.8), (x, y + 1.3), 0.4), ellipse(x, y, 0.25, 0.07, 12)]
    drops = [[(x, -1.2), (x, -1.7)] for x in (-1.6, 0.0, 1.6)] + [lens((x, -1.7), (x, -2.2), 0.35) for x in (-1.6, 0.0, 1.6)]
    parts = paint([(chains_, []), (hoop, []), (candles, [c for c in candles[0::3]]), (drops, [])])
    return make("Wrought-Iron Candle Chandelier", parts)
