"""Winter Wonderland niche, part 2 (pictures 10-53; snow and cold, not Christmas)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "winter"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


def smooth(pts, n=8, closed=False):
    """Catmull-Rom curve through the given points."""
    P = list(pts)
    P = [P[-1]] + P + [P[0], P[1]] if closed else [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[j] + (p2[j] - p0[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (3 * p1[j] - p0[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(P[-2])
    return out


def ell_arc(cx, cy, rx, ry, a0, a1, n=60):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / n), cy + ry * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def snow(y, x0=-3.2, x1=3.2, amp=0.08, waves=3):
    return wave(x0, x1, y, amp, waves, 80)


def flake(cx, cy, r):
    """Small six-armed snowflake."""
    out = []
    for k in range(3):
        a = k * math.pi / 3
        out.append([(cx - r * math.cos(a), cy - r * math.sin(a)), (cx + r * math.cos(a), cy + r * math.sin(a))])
    return out


def flakes(pts):
    out = []
    for x, y, r in pts:
        out += flake(x, y, r)
    return out


def mound(x0, x1, y, h, n=30):
    return quad((x0, y), ((x0 + x1) / 2, y + 2 * h), (x1, y), n)


def pine(x, y, h, w):
    """Simple snowy pine silhouette standing on (x, y)."""
    tiers = []
    for k in range(3):
        b = y + 0.15 * h + k * 0.27 * h
        ww = w * (1 - 0.25 * k)
        tiers.append(poly((x - ww, b), (x, b + 0.45 * h), (x + ww, b), closed=False))
    return tiers + [[(x - 0.08 * w, y), (x - 0.08 * w, y + 0.15 * h)], [(x + 0.08 * w, y), (x + 0.08 * w, y + 0.15 * h)]]


def mountains(y, pts):
    return poly(*[(pts[0][0], y)] + pts + [(pts[-1][0], y)], closed=False)


def balls(cx, specs, cut=None):
    """Stacked snowballs, bottom first; each hides the part of the one below it.
    `cut` = y above which the top ball is not drawn (where a hat sits)."""
    out = []
    for i, (cy, r) in enumerate(specs):
        if i + 1 < len(specs):
            cy2, r2 = specs[i + 1]
            d = cy2 - cy
            y = (d * d + r * r - r2 * r2) / (2 * d)
            a0 = math.atan2(y, math.sqrt(max(1e-9, r * r - y * y)))
            out.append(arc(cx, cy, r, math.pi - a0, 2 * math.pi + a0, 90))
        elif cut is not None:
            a0 = math.asin(max(-1.0, min(1.0, (cut - cy) / r)))
            out.append(arc(cx, cy, r, math.pi - a0, 2 * math.pi + a0, 80))
        else:
            out.append(circle(cx, cy, r, 80))
    return out


def snowman(cx, gy, s, hat="top", n=3):
    """Snowman standing on ground y=gy.  Returns strokes, hints, head (x, y, r)."""
    if n == 3:
        rs = [1.25 * s, 0.92 * s, 0.68 * s]
    else:
        rs = [1.15 * s, 0.75 * s]
    specs, y = [], gy
    for k, r in enumerate(rs):
        cy = y + r if k == 0 else y + r * 0.78
        specs.append((cy, r))
        y = cy + r * (0.78 if k == 0 else 0.8)
    hy, hr = specs[-1]
    cut = hy + 0.62 * hr if hat else None
    out = balls(cx, specs, cut)
    hints = [eye(cx - 0.3 * hr, hy + 0.2 * hr, 0.1 * s), eye(cx + 0.3 * hr, hy + 0.2 * hr, 0.1 * s)]
    out.append(poly((cx, hy - 0.02 * hr), (cx + 1.15 * hr, hy - 0.22 * hr), (cx, hy - 0.3 * hr), closed=False))
    out.append(arc(cx, hy - 0.05 * hr, 0.55 * hr, math.radians(225), math.radians(315), 10))
    if hat == "top":
        yb = cut
        out += [rrect(cx - 0.95 * hr, yb - 0.05 * s, cx + 0.95 * hr, yb + 0.15 * s, 0.06 * s),
                poly((cx - 0.6 * hr, yb + 0.15 * s), (cx - 0.6 * hr, yb + 1.1 * hr), (cx + 0.6 * hr, yb + 1.1 * hr), (cx + 0.6 * hr, yb + 0.15 * s), closed=False),
                [(cx - 0.6 * hr, yb + 0.45 * hr), (cx + 0.6 * hr, yb + 0.45 * hr)]]
    elif hat == "beanie":
        yb = cut
        w = math.sqrt(hr * hr - (yb - hy) ** 2)
        out += [rrect(cx - w - 0.08 * s, yb - 0.08 * s, cx + w + 0.08 * s, yb + 0.22 * s, 0.08 * s),
                chain(arc(cx, yb + 0.22 * s, w, 0, math.pi, 24)), circle(cx, yb + 0.22 * s + w + 0.18 * s, 0.2 * s, 16)]
    body_y, body_r = specs[-2]
    for k in range(3 if n == 3 else 2):
        out.append(circle(cx, body_y + body_r * (0.45 - 0.42 * k), 0.1 * s, 10))
    return out, hints, (cx, hy, hr), specs


def twig_arm(p0, p1, fingers=True):
    out = [[p0, p1]]
    if fingers:
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        a = math.atan2(dy, dx)
        L = math.hypot(dx, dy) * 0.25
        for da in (-0.6, 0.6):
            out.append([p1, (p1[0] + L * math.cos(a + da), p1[1] + L * math.sin(a + da))])
        m = (p0[0] + 0.7 * dx, p0[1] + 0.7 * dy)
        out.append([m, (m[0] + L * math.cos(a + 0.8), m[1] + L * math.sin(a + 0.8))])
    return out


# ------------------------------------------------------------ snowmen

@design("winter_waving_snowman", T)
def waving_snowman(rng):
    sm, h, (hx, hy, hr), specs = snowman(0, -2.7, 1.0, "top")
    by, br = specs[1]
    scarf = [tube(quad((-0.62, by + 0.62), (0, by + 0.42), (0.62, by + 0.62), 16), 0.28, cap=True),
             tube([(0.35, by + 0.5), (0.55, by - 0.35)], 0.3, cap=True)]
    fringe = [[(0.42 + 0.1 * k, by - 0.5), (0.42 + 0.1 * k, by - 0.75)] for k in range(3)]
    arms = twig_arm((0.85, by + 0.2), (1.9, by + 1.3)) + twig_arm((-0.85, by + 0.1), (-2.1, by - 0.4))
    ground = [snow(-2.7), mound(-3.2, -1.6, -2.7, 0.25), mound(1.6, 3.2, -2.7, 0.2)]
    sky = flakes([(-2.4, 2.4, 0.22), (2.3, 2.6, 0.25), (-1.8, 1.0, 0.18), (2.7, 0.6, 0.18)])
    return make("Waving Snowman", sm + scarf + fringe + arms + ground + sky, h)


@design("winter_broom_snowman", T)
def broom_snowman(rng):
    sm, h, (hx, hy, hr), specs = snowman(0.4, -2.7, 1.05, "beanie")
    by, br = specs[1]
    handle = tube([(-1.75, -1.6), (-1.2, 2.4)], 0.16, cap=True)
    bristles = poly((-1.95, -1.55), (-2.6, -2.7), (-1.2, -2.7), (-1.55, -1.6))
    bind = [[(-2.05, -1.75), (-1.47, -1.83)], [(-2.15, -1.95), (-1.42, -2.05)]]
    straws = [[(-1.75 + 0.05 * k, -2.1), (-2.2 + 0.25 * k, -2.65)] for k in range(1, 4)]
    arms = twig_arm((-0.5, by + 0.2), (-1.4, by + 0.5), False) + twig_arm((1.35, by + 0.15), (2.5, by + 0.6))
    birdy = smooth([(2.15, by + 0.66), (2.25, by + 0.95), (2.5, by + 1.05), (2.75, by + 0.9), (3.1, by + 0.95), (2.85, by + 0.7), (2.5, by + 0.62)], 6, True)
    ground = [snow(-2.7), mound(1.7, 3.2, -2.7, 0.25)]
    sky = flakes([(-2.6, 2.6, 0.22), (2.5, 2.3, 0.25), (-0.3, 3.0, 0.15)])
    return make("Snowman with a Broom", sm + [handle, bristles, birdy] + bind + straws + arms + ground + sky,
                h + [eye(2.45, by + 0.9, 0.05)])


@design("winter_snow_family", T)
def snow_family(rng):
    a, ha, _, sa = snowman(-1.9, -2.6, 0.85, "top")
    b, hb, _, sb = snowman(0.55, -2.6, 0.75, "beanie", n=2)
    c, hc, _, sc = snowman(2.35, -2.6, 0.5, "beanie", n=2)
    arms = twig_arm((-1.1, sa[1][0] + 0.1), (-0.3, sa[1][0] + 0.6), False) + twig_arm((-2.7, sa[1][0]), (-3.3, sa[1][0] + 0.5))
    arms += twig_arm((1.1, sb[0][0] + 0.25), (1.85, sb[0][0] + 0.2), False) + twig_arm((0.0, sb[0][0] + 0.3), (-0.4, sb[0][0] + 0.7), False)
    ground = [snow(-2.6)]
    sky = flakes([(0.6, 2.8, 0.2), (2.6, 1.6, 0.22), (-0.5, 1.8, 0.15)])
    return make("Snowman Family", a + b + c + arms + ground + sky, ha + hb + hc)


# ------------------------------------------------------------ clothing

@design("winter_mittens", T)
def mittens(rng):
    def mitt(dx, flip):
        out = smooth([(-0.95, -1.3), (-1.05, 0.4), (-0.75, 1.55), (0.05, 1.95), (0.75, 1.5), (0.95, 0.4), (1.0, 0.0), (1.55, 0.5), (1.85, 0.25),
                      (1.6, -0.45), (0.95, -0.9), (0.95, -1.3)], 8)
        cuff = rrect(-1.15, -2.3, 1.15, -1.3, 0.15)
        ribs = [[(x, -2.3), (x, -1.3)] for x in (-0.7, -0.25, 0.2, 0.65)]
        hrt = heart(0, 0.35, 0.45)
        thumb = quad((0.95, -0.1), (1.15, -0.5), (0.95, -0.85), 8)
        parts = [out, cuff, hrt, thumb] + ribs
        parts = [[(-x, y) for x, y in p] if flip else p for p in parts]
        return [transform(p, dx=dx, s=0.95) for p in parts]
    string = cubic((-1.4, -2.2), (-1.0, -3.4), (1.0, -3.4), (1.4, -2.2), 30)
    return make("Mittens on a String", mitt(-1.45, True) + mitt(1.45, False) + [string] + flakes([(0, 1.5, 0.3), (0, 2.6, 0.2)]))


def band(center, w, cuts=()):
    """Outline of a band plus cross lines at the given fractions."""
    out = [tube(center, w, cap=True)]
    n = len(center)
    for f in cuts:
        i = max(1, min(n - 2, int(f * (n - 1))))
        a, b = center[i - 1], center[i + 1]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L * w / 2, dx / L * w / 2
        x, y = center[i]
        out.append([(x + nx, y + ny), (x - nx, y - ny)])
    return out


@design("winter_scarf", T)
def scarf(rng):
    c = chain(cubic((-1.2, -2.3), (-1.4, 0.0), (-1.3, 1.5), (-0.6, 2.2), 30), cubic((-0.6, 2.2), (0.0, 2.7), (0.8, 2.2), (1.0, 1.4), 16),
              cubic((1.0, 1.4), (1.3, 0.0), (0.6, -1.0), (1.4, -2.0), 30))
    parts = band(c, 0.95, (0.06, 0.1, 0.14, 0.27, 0.31, 0.68, 0.72, 0.86, 0.9, 0.94))
    fr = []
    for end, side in ((c[0], -1), (c[-1], 1)):
        a = c[1] if side < 0 else c[-2]
        dx, dy = end[0] - a[0], end[1] - a[1]
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        for k in range(-3, 4):
            px, py = end[0] - uy * 0.13 * k, end[1] + ux * 0.13 * k
            fr.append([(px, py), (px + ux * 0.45, py + uy * 0.45)])
    hook = [circle(0.1, 2.85, 0.15, 12), [(0.1, 3.0), (0.1, 3.3)]]
    return make("Knitted Scarf", parts + fr + hook)


@design("winter_earmuffs", T)
def earmuffs(rng):
    bandc = arc(0, -0.2, 2.1, math.radians(8), math.radians(172), 50)
    head = tube(bandc, 0.4, cap=True)
    muffs = []
    for s in (-1, 1):
        muffs.append(polar(lambda t: 1.0 + 0.07 * math.sin(14 * t), cx=s * 2.0, cy=-0.9, n=220))
        muffs.append(circle(s * 2.0, -0.9, 0.62, 50))
    sl = [arc(-2.0, -0.9, 0.4, math.radians(100), math.radians(160), 8), arc(2.0, -0.9, 0.4, math.radians(100), math.radians(160), 8)]
    deco = flake(0, 1.0, 0.45) + flakes([(-0.9, -2.4, 0.25), (0.9, -2.6, 0.2)])
    return make("Fluffy Earmuffs", [head] + muffs + sl + deco)


@design("winter_snow_boots", T)
def snow_boots(rng):
    def boot(dx, dy, s):
        body = chain([(-0.9, 2.0), (-0.95, -1.1)], quad((-0.95, -1.1), (-1.0, -1.6), (-0.6, -1.6), 8), [(1.6, -1.6)],
                     quad((1.6, -1.6), (2.2, -1.5), (2.0, -0.8), 10), quad((2.0, -0.8), (1.6, -0.3), (0.6, -0.3), 12), [(0.6, 2.0)])
        fur = chain(smooth([(-1.15, 1.8), (-1.2, 2.3), (-0.8, 2.6), (-0.3, 2.45), (0.2, 2.65), (0.7, 2.4), (0.85, 1.85), (0.4, 1.65), (-0.2, 1.75), (-0.7, 1.65)], 6, True))
        sole = [[(-0.97, -1.25), (2.05, -1.25)]]
        tread = zigzag(-0.7, 1.7, -1.75, 0.1, 9)
        laces = [[(0.6, y), (0.05, y + 0.15)] for y in (-0.1, 0.4, 0.9, 1.4)]
        toe = [quad((0.9, -0.55), (1.5, -0.5), (1.8, -0.95), 8)]
        return [transform(p, dx=dx, dy=dy, s=s) for p in [body, fur, tread] + sole + laces + toe]
    snow_ = [snow(-2.65), mound(-3.2, -1.8, -2.65, 0.2)]
    return make("Snow Boots", boot(-1.85, 0.0, 0.95) + boot(1.45, 0.0, 0.95) + snow_ + flakes([(2.4, 2.4, 0.25), (-2.5, 2.6, 0.2)]))


@design("winter_sweater", T)
def sweater(rng):
    out = chain([(-1.6, -2.4)], [(-1.6, 0.9)], [(-2.35, -1.6)], [(-3.05, -1.3)], [(-2.0, 1.9)], [(-0.7, 2.3)],
                quad((-0.7, 2.3), (0, 1.7), (0.7, 2.3), 12), [(2.0, 1.9), (3.05, -1.3), (2.35, -1.6), (1.6, 0.9), (1.6, -2.4), (-1.6, -2.4)])
    hem = [[(-1.6, -1.95), (1.6, -1.95)]] + [[(x, -2.4), (x, -1.95)] for x in (-1.2, -0.8, -0.4, 0.0, 0.4, 0.8, 1.2)]
    cuffs = [[(-2.85, -1.0), (-2.15, -1.35)], [(2.85, -1.0), (2.15, -1.35)]]
    collar = quad((-0.7, 2.3), (0, 1.35), (0.7, 2.3), 14)
    zz = [zigzag(-1.6, 1.6, 0.9, 0.15, 8), zigzag(-1.6, 1.6, -1.45, 0.15, 8)]
    lines_ = [[(-1.6, 1.15), (1.6, 1.15)], [(-1.6, 0.65), (1.6, 0.65)], [(-1.6, -1.2), (1.6, -1.2)], [(-1.6, -1.7), (1.6, -1.7)]]
    centre = flake(0, -0.25, 0.6) + [poly(*[(0.25 * math.cos(k * math.pi / 3), -0.25 + 0.25 * math.sin(k * math.pi / 3)) for k in range(6)])]
    side_ = [heart(-1.0, -0.3, 0.25), heart(1.0, -0.3, 0.25)]
    return make("Knitted Sweater", [out, collar] + hem + cuffs + zz + lines_ + centre + side_)


# ------------------------------------------------------------ winter sport

@design("winter_skis", T)
def skis(rng):
    def ski(rot):
        s = chain([(-0.22, -3.0), (0.22, -3.0), (0.22, 2.6)], arc(-0.18, 2.6, 0.4, 0, math.pi * 0.75, 10), [(-0.22, 2.6), (-0.22, -3.0)])
        bind = [rrect(-0.32, -0.6, 0.32, 0.2, 0.08), [(-0.22, 0.55), (0.22, 0.55)]]
        return [transform(p, rot=rot) for p in [s] + bind]
    def pole(rot, dx):
        p = [[(0, -2.6), (0, 2.4)], rrect(-0.15, 2.4, 0.15, 3.1, 0.08), circle(0, -2.1, 0.35, 24), [(-0.35, -2.1), (0.35, -2.1)],
             arc(0, 3.1, 0.3, math.pi * 0.2, math.pi * 0.8, 8)]
        return [transform(q, rot=rot, dx=dx) for q in p]
    snow_ = [mound(-3.2, 3.2, -2.8, 0.3, 60)]
    return make("Skis and Poles", ski(0.4) + ski(-0.4) + pole(0.15, -1.9) + pole(-0.15, 1.9) + snow_ + flakes([(0, 2.6, 0.25)]))


@design("winter_snowboarder", T)
def snowboarder(rng):
    slope = [[(-3.2, 0.2), (3.2, -2.6)]]
    board = lens((-1.7, 0.1), (1.6, -0.9), 0.08, 30)
    legs_ = [tube([(-0.7, -0.15), (-0.5, 0.55), (0.05, 0.9)], 0.38, cap=False), tube([(0.7, -0.55), (0.8, 0.25), (0.3, 0.9)], 0.38, cap=False)]
    torso = tube([(0.15, 0.85), (-0.1, 1.95)], 0.75, cap=True)
    head = circle(-0.2, 2.55, 0.4, 30)
    helmet = [arc(-0.2, 2.55, 0.48, math.radians(10), math.radians(170), 16), rrect(-0.55, 2.45, 0.2, 2.75, 0.1)]
    arms = [tube([(-0.25, 1.75), (-1.1, 1.45), (-1.9, 1.8)], 0.28, cap=True), tube([(0.05, 1.75), (0.95, 2.05), (1.75, 2.6)], 0.28, cap=True)]
    gloves = [circle(-2.0, 1.85, 0.18, 12), circle(1.85, 2.7, 0.18, 12)]
    spray = [circle(-2.2, 0.6, 0.15, 12), circle(-2.5, 0.2, 0.12, 10), circle(-2.0, 0.95, 0.1, 10), circle(-2.7, 0.75, 0.1, 10)]
    trees = pine(2.4, -1.85, 1.6, 0.55)
    return make("Snowboarder", slope + [board, torso, head] + helmet + legs_ + arms + gloves + spray + trees + flakes([(1.2, 3.2, 0.2)]))


@design("winter_ice_skater", T)
def ice_skater(rng):
    stand = tube([(0.2, -2.0), (0.25, -0.4)], 0.32, cap=False)
    back_leg = tube([(0.0, -0.3), (-1.2, 0.05), (-2.3, 0.45)], 0.3, cap=False)
    torso = tube([(0.35, -0.2), (1.0, 0.9)], 0.6, cap=True)
    head = circle(1.35, 1.45, 0.36, 30)
    bun = circle(1.15, 1.9, 0.18, 14)
    arms = [tube([(1.0, 0.75), (1.8, 0.9), (2.6, 1.35)], 0.2, cap=True), tube([(0.75, 0.75), (0.1, 1.4), (-0.4, 2.2)], 0.2, cap=True)]
    skirt = chain([(0.0, 0.2)], quad((0.0, 0.2), (-0.65, -0.2), (-0.7, -0.8), 10), wave(-0.7, 1.1, -0.8, 0.07, 3, 24)[1:],
                  quad((1.1, -0.8), (1.05, -0.2), (0.75, 0.2), 10))
    boot1 = [poly((0.05, -2.0), (0.0, -2.45), (0.75, -2.45), (0.5, -2.15), (0.4, -2.0), closed=False), [(-0.15, -2.75), (0.9, -2.75)],
             [(0.1, -2.45), (0.1, -2.75)], [(0.6, -2.45), (0.6, -2.75)]]
    boot2 = [poly((-2.25, 0.25), (-2.45, 0.7), (-2.95, 0.55), (-2.85, 0.15), closed=False), [(-3.0, -0.1), (-2.2, 0.1)],
             [(-2.85, 0.15), (-2.88, -0.05)], [(-2.35, 0.3), (-2.4, 0.06)]]
    ice = [[(-3.2, -2.75), (-0.4, -2.75)], [(1.3, -2.75), (3.2, -2.75)]]
    trail = [ell_arc(-1.6, -2.3, 1.2, 0.22, 0.4, 2 * math.pi - 0.1, 50)]
    return make("Figure Skater", [stand, back_leg, torso, head, bun, skirt] + arms + boot1 + boot2 + ice + trail +
                flakes([(2.5, 2.6, 0.22), (-2.4, 2.5, 0.2)]))


@design("winter_sledding", T)
def sledding(rng):
    hill = [[(-3.2, 1.0), (3.2, -2.2)]]
    rot = -math.atan2(3.2, 6.4)
    sled_ = chain([(-1.8, 0.0), (1.4, 0.0)], arc(1.4, 0.35, 0.35, -math.pi / 2, math.pi / 2, 10), arc(1.4, 0.45, 0.25, math.pi / 2, math.pi * 1.6, 8))
    deck = [[(-1.8, 0.0), (-1.8, 0.25), (1.2, 0.25)]]
    kid = [smooth([(-1.55, 0.3), (-1.5, 1.2), (-1.1, 1.65), (-0.6, 1.35), (-0.55, 0.3)], 6, True), circle(-0.9, 2.05, 0.4, 30),
           chain(arc(-0.9, 2.15, 0.42, math.radians(10), math.radians(170), 16)), circle(-1.05, 2.75, 0.15, 12),
           smooth([(-0.55, 0.75), (0.4, 0.75), (0.7, 0.95), (0.95, 0.85), (0.9, 0.3), (-0.55, 0.3)], 6, True),
           tube([(-0.85, 1.25), (0.0, 1.05), (0.9, 0.75)], 0.22, cap=True)]
    beanie_cuff = [[(-1.32, 2.15), (-0.48, 2.15)]]
    scarf = tube(chain([(-1.25, 1.55)], cubic((-1.25, 1.55), (-1.8, 1.6), (-2.0, 2.0), (-2.6, 1.9), 16)), 0.22, cap=True)
    rope = [quad((0.9, 0.75), (1.3, 0.9), (1.55, 0.7), 8)]
    parts = [transform(p, rot=rot, dx=0.2, dy=-0.2) for p in [sled_, scarf] + deck + kid + beanie_cuff + rope]
    trees = pine(-2.3, 0.75, 1.6, 0.55) + pine(2.4, -2.0, 1.2, 0.45)
    lines_ = [[(-3.0, 0.3), (-2.2, -0.1)], [(-2.6, -0.4), (-1.8, -0.8)]]
    return make("Sledding Down the Hill", hill + parts + trees + lines_ + flakes([(1.2, 2.6, 0.22), (2.6, 1.4, 0.2)]))


@design("winter_snowshoes", T)
def snowshoes(rng):
    def shoe(rot, dx):
        rx, ry = 0.95, 1.9
        frame = chain(ell_arc(0, 0.3, rx, ry, -math.pi / 2 + 0.55, 3 * math.pi / 2 - 0.55, 70), [(0, -2.6)],
                      [(rx * math.cos(-math.pi / 2 + 0.55), 0.3 + ry * math.sin(-math.pi / 2 + 0.55))])
        inner = ellipse(0, 0.3, rx - 0.18, ry - 0.18, 70)
        lace = []
        for k in range(-2, 3):
            x = 0.3 * k
            ys = math.sqrt(max(0, 1 - (x / (rx - 0.18)) ** 2)) * (ry - 0.18)
            lace.append([(x, 0.3 - ys), (x, 0.3 + ys)])
        for k in range(-4, 5):
            y = 0.3 + 0.35 * k
            xs = math.sqrt(max(0, 1 - ((y - 0.3) / (ry - 0.18)) ** 2)) * (rx - 0.18)
            if xs > 0.1:
                lace.append([(-xs, y), (xs, y)])
        strap = rrect(-0.55, 0.0, 0.55, 0.5, 0.12)
        tail = [[(0, -1.6), (0, -2.6)]]
        return [transform(p, rot=rot, dx=dx) for p in [frame, inner, strap] + lace + tail]
    snow_ = [snow(-2.9, amp=0.06)]
    return make("Pair of Snowshoes", shoe(0.25, -1.3) + shoe(-0.25, 1.3) + snow_)


# ------------------------------------------------------------ outdoor scenes

@design("winter_ice_fishing", T)
def ice_fishing(rng):
    hut = rect(-2.8, -1.4, -0.4, 0.8)
    roof = poly((-3.1, 0.7), (-0.1, 1.3), (-0.1, 1.6), (-3.1, 1.0))
    snow_roof = smooth([(-3.1, 1.0), (-2.4, 1.3), (-1.4, 1.4), (-0.6, 1.7), (-0.1, 1.6)], 6)
    door = rect(-1.4, -1.4, -0.7, 0.2)
    window = [rect(-2.4, -0.4, -1.8, 0.3), [(-2.1, -0.4), (-2.1, 0.3)]]
    pipe = [rect(-2.5, 1.2, -2.2, 2.0), circle(-2.0, 2.4, 0.18, 14), circle(-1.7, 2.8, 0.24, 16)]
    hole = [ellipse(1.6, -2.0, 0.8, 0.28, 40), ell_arc(1.6, -2.0, 0.55, 0.16, math.pi, 2 * math.pi, 16)]
    rod = [[(0.3, -2.3), (1.0, 0.7)], quad((1.0, 0.7), (1.5, -0.4), (1.6, -1.95), 20), rrect(0.18, -2.55, 0.52, -1.85, 0.08)]
    fish = [lens((2.5, -2.6), (3.3, -2.55), 0.28), poly((2.5, -2.6), (2.25, -2.4), (2.25, -2.8))]
    ice = [[(-3.2, -1.4), (-2.9, -1.4)], [(-0.4, -1.4), (3.4, -1.4)], [(-2.4, -2.1), (-1.6, -2.5), (-0.9, -2.45)]]
    trees = pine(2.3, -1.4, 1.5, 0.45) + pine(3.1, -1.4, 1.9, 0.5)
    return make("Ice Fishing Hut", [hut, roof, snow_roof, door] + window + pipe + hole + rod + fish + ice + trees, [eye(3.1, -2.52, 0.05)])


@design("winter_frozen_pond", T)
def frozen_pond(rng):
    pond = ellipse(0, -1.4, 3.0, 1.2, 140)
    trail = [[(math.sin(t) * 1.4, -1.4 + math.sin(2 * t) * 0.45) for t in [k * 2 * math.pi / 80 for k in range(81)]]]
    cracks = [[(1.6, -0.9), (2.0, -1.2), (1.9, -1.6)], [(2.0, -1.2), (2.5, -1.3)], [(-2.2, -1.9), (-1.8, -1.6), (-1.9, -1.3)]]
    cattails = []
    for x, h in ((-2.9, 1.4), (-2.6, 1.8), (-2.3, 1.2)):
        cattails += [[(x, -1.0), (x, -1.0 + h)], rrect(x - 0.1, -1.0 + h - 0.6, x + 0.1, -1.0 + h - 0.05, 0.1)]
    cattails.append(lens((-2.75, -0.9), (-1.9, 0.3), 0.12))
    trees = pine(0.2, -0.15, 2.4, 0.7) + pine(1.8, -0.2, 2.0, 0.6)
    return make("Frozen Pond", [pond] + trail + cracks + cattails + trees + flakes([(-0.8, 2.6, 0.22), (2.8, 2.4, 0.22), (-2.2, 2.2, 0.18)]))


@design("winter_snow_shovel", T)
def snow_shovel(rng):
    shaft = tube([(0.0, -0.5), (0.0, 2.4)], 0.26, cap=False)
    grip = [rrect(-0.6, 2.4, 0.6, 3.2, 0.25), rrect(-0.35, 2.6, 0.35, 2.95, 0.12)]
    blade = chain([(-1.1, -0.5), (1.1, -0.5)], quad((1.1, -0.5), (1.6, -1.4), (1.55, -2.5), 12), quad((1.55, -2.5), (0, -2.3), (-1.55, -2.5), 16),
                  quad((-1.55, -2.5), (-1.6, -1.4), (-1.1, -0.5), 12))
    lip = quad((-1.35, -2.15), (0, -1.95), (1.35, -2.15), 16)
    ribs = [[(-0.5, -0.6), (-0.6, -1.9)], [(0.5, -0.6), (0.6, -1.9)]]
    collar = rrect(-0.3, -0.7, 0.3, 0.0, 0.08)
    pile = smooth([(-3.2, -2.8), (-2.9, -1.7), (-2.2, -1.3), (-1.6, -1.6)], 8)
    pile2 = smooth([(1.7, -1.8), (2.3, -1.3), (2.9, -1.6), (3.2, -2.8)], 8)
    ground = [snow(-2.8)]
    return make("Snow Shovel", [shaft, blade, lip, collar, pile, pile2] + grip + ribs + ground +
                flakes([(1.8, 1.0, 0.22), (2.4, 2.4, 0.25), (-1.8, 2.2, 0.2), (-2.4, 0.4, 0.2)]))


@design("winter_snowball_fort", T)
def snowball_fort(rng):
    blocks = []
    rows = [(-2.4, -1.5, 6, 0.0), (-1.5, -0.6, 5, 0.5), (-0.6, 0.3, 4, 1.0)]
    for y0, y1, n, off in rows:
        w = 5.4 / 6
        for k in range(n):
            x = -2.7 + off * w + k * w
            blocks.append(rrect(x + 0.03, y0, x + w - 0.03, y1 - 0.04, 0.15))
    pole = [[(1.2, 0.3), (1.2, 2.9)], poly((1.2, 2.9), (2.3, 2.55), (1.2, 2.2), closed=False)]
    pile = []
    for row, (y, xs) in enumerate([(-2.55, (2.3, 2.85, 3.4)), (-2.07, (2.57, 3.12)), (-1.59, (2.85,))]):
        for x in xs:
            pile.append(circle(x - 0.2, y, 0.27, 24))
    ground = [snow(-2.85)]
    return make("Snowball Fort", blocks + pole + pile + ground + flakes([(-2.0, 2.2, 0.25), (-0.3, 2.8, 0.2), (2.8, 1.0, 0.2)]))


@design("winter_snow_angel", T)
def snow_angel(rng):
    head = circle(0, 2.05, 0.55, 40)
    wl = arc(-0.35, 0.95, 2.2, math.radians(80), math.radians(205), 40)
    sk = arc(0, 0.6, 2.7, math.radians(242), math.radians(298), 30)
    left = chain([(-0.32, 1.55)], wl, [(-0.6, 0.35)], [(2.7 * math.cos(math.radians(242)), 0.6 + 2.7 * math.sin(math.radians(242)))])
    outline = chain(left, sk, mirror_x(left)[::-1])
    feathers = [arc(-0.35, 0.95, r, math.radians(105), math.radians(195), 20) for r in (1.4, 1.8)] + \
               [arc(0.35, 0.95, r, math.radians(-15), math.radians(75), 20) for r in (1.4, 1.8)]
    legs_ = [quad((-0.2, -0.2), (-0.35, -1.0), (-0.6, -1.7), 8), quad((0.2, -0.2), (0.35, -1.0), (0.6, -1.7), 8)]
    prints = [ellipse(x, y, 0.16, 0.3, 14) for x, y in [(2.4, -2.6), (2.75, -2.05), (2.45, -1.5)]]
    return make("Snow Angel", [head, outline] + feathers + legs_ + prints + flakes([(-2.6, 2.7, 0.22), (2.5, 2.6, 0.25), (-2.7, -2.3, 0.2)]))


@design("winter_icicles", T)
def icicles(rng):
    roof = rect(-3.2, 1.0, 3.2, 1.5)
    snow_top = smooth([(-3.3, 1.5), (-2.7, 2.0), (-1.6, 1.85), (-0.6, 2.15), (0.6, 1.9), (1.6, 2.15), (2.6, 1.85), (3.3, 1.5)], 8)
    lens_ = [(-2.9, 1.2), (-2.4, 0.6), (-1.95, 1.6), (-1.4, 0.9), (-0.9, 2.0), (-0.35, 1.1), (0.15, 1.5), (0.7, 0.7), (1.2, 1.8),
             (1.75, 1.0), (2.3, 1.4), (2.8, 0.8)]
    ics = []
    for x, L in lens_:
        w = 0.17 if L > 1 else 0.13
        ics.append(chain([(x - w, 1.0)], quad((x - w, 1.0), (x - w * 0.3, 1.0 - L * 0.7), (x, 1.0 - L), 10),
                         quad((x, 1.0 - L), (x + w * 0.3, 1.0 - L * 0.7), (x + w, 1.0), 10)))
    wall = [[(-3.2, -2.8), (3.2, -2.8)]]
    window = [rect(-1.0, -2.4, 1.0, -0.7), [(0, -2.4), (0, -0.7)], [(-1.0, -1.55), (1.0, -1.55)], rect(-1.2, -2.6, 1.2, -2.4)]
    drops = [chain(quad((x, -0.25), (x - 0.12, -0.45), (x, -0.55), 6), quad((x, -0.55), (x + 0.12, -0.45), (x, -0.25), 6)) for x in (-0.9, 1.75)]
    siding = [[(-3.2, y), (-1.4, y)] for y in (-0.6, -1.4, -2.2)] + [[(1.4, y), (3.2, y)] for y in (-0.6, -1.4, -2.2)]
    return make("Icicles on the Roof", [roof, snow_top] + ics + wall + window + siding + drops)


@design("winter_frosted_window", T)
def frosted_window(rng):
    frame = rect(-2.4, -2.2, 2.4, 2.6)
    inner = rect(-2.1, -1.9, 2.1, 2.3)
    bars = [[(0, -1.9), (0, 2.3)], [(-2.1, 0.2), (2.1, 0.2)]]
    sill = rrect(-2.9, -2.6, 2.9, -2.2, 0.1)
    frost = []
    for cx, cy, sx, sy in [(-2.1, 2.3, 1, -1), (2.1, 2.3, -1, -1), (-2.1, -1.9, 1, 1), (2.1, -1.9, -1, 1)]:
        for a, L in ((0.25, 1.4), (0.75, 1.1), (1.25, 1.3)):
            dx, dy = sx * math.cos(a), sy * math.sin(a)
            main = [(cx, cy), (cx + dx * L, cy + dy * L)]
            frost.append(main)
            for f in (0.35, 0.65):
                px, py = cx + dx * L * f, cy + dy * L * f
                for side in (-1, 1):
                    b = math.atan2(dy, dx) + side * 0.6
                    frost.append([(px, py), (px + 0.3 * math.cos(b), py + 0.3 * math.sin(b))])
    curl = [spiral(1.0, -0.6, 0.05, 0.35, 1.5, 40), spiral(-1.0, 1.2, 0.05, 0.35, 1.5, 40, rot=2.0)]
    snow_sill = smooth([(-2.9, -2.2), (-2.2, -1.95), (-1.4, -2.05), (-0.6, -1.9), (0.0, -2.05)], 6)
    return make("Frosted Window", [frame, inner, sill, snow_sill] + bars + frost + curl)


@design("winter_lantern", T)
def lantern(rng):
    body = rect(-1.0, -1.6, 1.0, 1.0)
    posts = [[(-0.55, -1.6), (-0.55, 1.0)], [(0.55, -1.6), (0.55, 1.0)]]
    cap = poly((-1.3, 1.0), (-0.5, 1.9), (0.5, 1.9), (1.3, 1.0))
    top = rect(-0.35, 1.9, 0.35, 2.2)
    ring = arc(0, 2.6, 0.45, math.radians(-50), math.radians(230), 24)
    base = rect(-1.3, -2.0, 1.3, -1.6)
    candle = rect(-0.25, -1.6, 0.25, -0.5)
    flame = chain(quad((0, 0.35), (-0.3, -0.1), (0, -0.4), 10), quad((0, -0.4), (0.3, -0.1), (0, 0.35), 10))
    snow_cap = smooth([(-1.35, 0.95), (-1.2, 1.25), (-0.6, 1.3), (0.0, 1.45), (0.7, 1.25), (1.35, 0.95)], 6)
    ground = [mound(-3.2, 3.2, -2.6, 0.3, 50), snow(-2.95)]
    pines_ = pine(-2.5, -2.3, 2.6, 0.7) + pine(2.5, -2.3, 2.2, 0.6)
    return make("Lantern in the Snow", [body, cap, top, ring, base, candle, flame, snow_cap] + posts + ground + pines_ +
                flakes([(-1.6, 2.6, 0.2), (1.6, 2.8, 0.2)]))


@design("winter_chalet", T)
def chalet(rng):
    mts = [mountains(0.5, [(-3.3, 0.5), (-2.0, 2.6), (-1.0, 1.4), (0.4, 3.2), (1.8, 1.4), (2.6, 2.2), (3.3, 1.2)])]
    caps = [poly((-2.45, 2.05), (-2.0, 2.6), (-1.55, 2.05), (-1.85, 2.2), (-2.0, 2.0), (-2.2, 2.2)),
            poly((-0.15, 2.6), (0.4, 3.2), (0.95, 2.6), (0.6, 2.75), (0.4, 2.55), (0.15, 2.75))]
    roof = poly((-2.5, -1.1), (0, 1.8), (2.5, -1.1), (2.1, -1.1), (0, 1.3), (-2.1, -1.1))
    walls = rect(-1.8, -2.6, 1.8, -1.1)
    gable = poly((-1.7, -1.1), (0, 0.9), (1.7, -1.1), closed=False)
    balcony = [rect(-1.5, -1.25, 1.5, -1.05)] + [[(x, -1.05), (x, -0.55)] for x in (-1.2, -0.6, 0.0, 0.6, 1.2)] + [[(-1.3, -0.55), (1.3, -0.55)]]
    window = [poly((-0.5, -0.5), (0, 0.15), (0.5, -0.5)), [(0, -0.5), (0, 0.15)]]
    door = rect(-0.4, -2.6, 0.4, -1.5)
    wins = [rect(-1.5, -2.2, -0.8, -1.6), rect(0.8, -2.2, 1.5, -1.6)]
    trees = pine(-2.7, -2.6, 1.8, 0.55) + pine(2.7, -2.6, 1.6, 0.5)
    ground = [snow(-2.6)]
    return make("Mountain Chalet", mts + caps + [roof, walls, gable, door] + balcony + window + wins + trees + ground)


@design("winter_ski_lift", T)
def ski_lift(rng):
    cable = [[(-3.3, 2.8), (3.3, 1.8)]]
    x, y = 0.4, 2.8 - (0.4 + 3.3) * 1.0 / 6.6
    grip = [rrect(x - 0.3, y - 0.12, x + 0.3, y + 0.15, 0.08)]
    hanger = [[(x - 0.06, y - 0.12), (x - 0.06, y - 1.2)], [(x + 0.06, y - 0.12), (x + 0.06, y - 1.2)]]
    frame = [[(x - 1.6, y - 1.2), (x + 1.6, y - 1.2)], [(x - 1.6, y - 1.2), (x - 1.6, y - 2.9)], [(x + 1.6, y - 1.2), (x + 1.6, y - 2.9)]]
    back = rrect(x - 1.45, y - 2.6, x + 1.45, y - 1.6, 0.12)
    slats = [[(x - 1.45, y - 1.95), (x + 1.45, y - 1.95)], [(x - 1.45, y - 2.27), (x + 1.45, y - 2.27)]]
    seat = rrect(x - 1.75, y - 3.05, x + 1.75, y - 2.75, 0.12)
    bar = [poly((x - 1.6, y - 1.5), (x - 1.0, y - 1.5), (x - 1.0, y - 3.7), (x + 1.0, y - 3.7), (x + 1.0, y - 1.5), (x + 1.6, y - 1.5), closed=False),
           [(x - 1.0, y - 3.7), (x - 1.0, y - 3.9)], [(x + 1.0, y - 3.7), (x + 1.0, y - 3.9)], [(x - 1.4, y - 3.9), (x + 1.4, y - 3.9)]]
    tower = [rect(-3.0, -3.0, -2.7, 2.65), [(-3.4, 2.65), (-2.2, 2.65)], [(-3.3, -3.0), (-2.4, -3.0)]]
    mts = [quad((-2.7, -2.4), (1.0, -1.5), (3.3, -3.0), 30)]
    trees = pine(2.6, -2.8, 1.3, 0.45) + pine(-1.8, -2.6, 1.1, 0.4)
    return make("Ski Lift Chair", cable + grip + hanger + frame + [back, seat] + slats + bar + tower + mts + trees + flakes([(2.4, 2.8, 0.22), (2.8, 0.4, 0.2)]))


@design("winter_snowplow", T)
def snowplow(rng):
    body = poly((-2.6, -1.2), (-2.6, -0.1), (-0.8, -0.1), (-0.8, 1.6), (0.9, 1.6), (1.5, 0.3), (2.3, 0.2), (2.3, -1.2))
    window = poly((-0.5, 0.4), (-0.5, 1.3), (0.75, 1.3), (1.15, 0.4))
    door_line = [[(0.6, -1.0), (0.6, 0.4)]]
    bed = [[(-2.6, 0.4), (-0.8, 0.4)], [(-2.6, -0.1), (-2.6, 0.4)]]
    light = [rrect(0.0, 1.6, 0.4, 1.9, 0.1), [(0.2, 2.0), (0.2, 2.3)], [(-0.15, 1.95), (-0.4, 2.15)], [(0.55, 1.95), (0.8, 2.15)]]
    wheels = [circle(-1.6, -1.35, 0.6, 40), circle(-1.6, -1.35, 0.25, 20), circle(1.3, -1.35, 0.6, 40), circle(1.3, -1.35, 0.25, 20)]
    blade = chain([(2.6, -2.0), (3.3, -2.0)], quad((3.3, -2.0), (2.85, -0.6), (3.4, 0.6), 16), [(2.9, 0.6)], quad((2.9, 0.6), (2.5, -0.6), (2.6, -2.0), 16))
    arm = [[(2.3, -0.6), (2.75, -0.6)], [(2.3, -0.9), (2.7, -1.2)]]
    pile = smooth([(3.3, -2.0), (3.6, -1.5), (3.6, -1.0), (3.35, -0.6)], 6)
    ground = [[(-3.2, -2.0), (2.6, -2.0)]]
    return make("Snowplow Truck", [body, window, blade, pile] + door_line + bed + light + wheels + arm + ground +
                flakes([(-2.2, 2.4, 0.22), (-1.2, 2.8, 0.18), (2.6, 2.4, 0.22)]))


@design("winter_snowy_bridge", T)
def snowy_bridge(rng):
    deck = arc(0, -3.0, 3.6, math.radians(35), math.radians(145), 50)
    deck2 = arc(0, -3.0, 3.3, math.radians(33), math.radians(147), 50)
    rail = arc(0, -2.2, 3.6, math.radians(40), math.radians(140), 50)
    posts = []
    for a in (45, 65, 90, 115, 135):
        t = math.radians(a)
        posts.append([(3.6 * math.cos(t), -3.0 + 3.6 * math.sin(t)), (3.6 * math.cos(t), -2.2 + 3.6 * math.sin(t))])
    snow_ = smooth([(-2.6, 1.22), (-1.6, 1.55), (-0.6, 1.62), (0.4, 1.7), (1.4, 1.48), (2.6, 1.22)], 8)
    stream = [[(-3.3, -1.5), (-2.0, -1.5)], [(2.0, -1.5), (3.3, -1.5)], [(-3.3, -2.6), (3.3, -2.6)], wave(-1.6, 1.6, -2.0, 0.06, 3, 40)]
    banks = [quad((-3.3, -0.5), (-2.4, -0.4), (-2.0, -1.5), 12), quad((3.3, -0.5), (2.4, -0.4), (2.0, -1.5), 12)]
    trees = pine(-2.6, -0.45, 2.2, 0.55) + pine(2.6, -0.45, 2.6, 0.65)
    return make("Snowy Footbridge", [deck, deck2, rail, snow_] + posts + stream + banks + trees + flakes([(0, 2.8, 0.25), (-1.4, 2.4, 0.18)]))


@design("winter_northern_lights", T)
def northern_lights(rng):
    bands = [wave(-3.3, 3.3, 1.6, 0.35, 1.3, 80), wave(-3.3, 3.3, 2.3, 0.4, 1.1, 80), wave(-3.3, 3.3, 0.9, 0.3, 1.5, 80)]
    rays = []
    for x in [-3.0 + 0.6 * k for k in range(11)]:
        y1 = 2.3 + 0.4 * math.sin(2 * math.pi * 1.1 * (x + 3.3) / 6.6)
        y0 = 0.9 + 0.3 * math.sin(2 * math.pi * 1.5 * (x + 3.3) / 6.6)
        rays.append([(x, y0 + 0.1), (x, y1 - 0.1)])
    cabin = [rect(-0.8, -2.6, 0.8, -1.4), poly((-1.1, -1.5), (0, -0.6), (1.1, -1.5)), rect(-0.35, -2.2, 0.15, -1.75), rect(0.4, -1.0, 0.65, -0.55)]
    hills = [quad((-3.3, -1.6), (-1.6, -0.8), (-0.9, -1.6), 20), quad((0.9, -1.6), (1.8, -0.6), (3.3, -1.2), 20)]
    trees = pine(-2.3, -2.6, 1.9, 0.5) + pine(2.0, -2.6, 2.2, 0.6) + pine(-1.4, -2.6, 1.3, 0.4)
    st = [star(x, y, 0.18, 4, 0.35) for x, y in [(-2.7, 2.9), (0.4, 3.1), (2.8, 3.0)]]
    return make("Northern Lights", bands + rays + cabin + hills + trees + st + [snow(-2.6)])


@design("winter_ice_castle", T)
def ice_castle(rng):
    wall = poly((-1.6, -2.6), (-1.6, 0.4), (1.6, 0.4), (1.6, -2.6), closed=False)
    crenel = [poly(*[(x, 0.4), (x, 0.7), (x + 0.35, 0.7), (x + 0.35, 0.4)], closed=False) for x in (-1.35, -0.6, 0.25, 1.0)]
    gate = chain([(-0.55, -2.6), (-0.55, -1.5)], arc(0, -1.5, 0.55, math.pi, 0, 16), [(0.55, -2.6)])
    towers = []
    for x, h in ((-2.2, 1.6), (2.2, 1.6), (0, 2.1)):
        w = 0.6 if x else 0.7
        if x == 0:
            towers += [poly((-w, 0.4), (-w, 1.6), (w, 1.6), (w, 0.4), closed=False), poly((-w - 0.15, 1.6), (0, 3.2), (w + 0.15, 1.6))]
        else:
            towers += [rect(x - w, -2.6, x + w, 1.2), poly((x - w - 0.15, 1.2), (x, 2.7), (x + w + 0.15, 1.2))]
    windows = [chain([(x - 0.18, y), (x - 0.18, y + 0.35)], arc(x, y + 0.35, 0.18, math.pi, 0, 8), [(x + 0.18, y)], [(x - 0.18, y)])
               for x, y in [(-2.2, -0.2), (2.2, -0.2), (0, 0.8)]]
    blocks = [[(-1.6, -0.4), (-0.55, -0.4)], [(0.55, -0.4), (1.6, -0.4)], [(-1.6, -1.2), (-0.55, -1.2)], [(0.55, -1.2), (1.6, -1.2)],
              [(-1.1, -0.4), (-1.1, 0.4)], [(1.1, -0.4), (1.1, 0.4)], [(-1.0, -1.2), (-1.0, -0.4)], [(1.0, -1.2), (1.0, -0.4)]]
    ics = [poly((x - 0.08, 0.4), (x, 0.0), (x + 0.08, 0.4), closed=False) for x in (-1.2, -0.3, 0.6)]
    shine = [star(x, y, 0.22, 4, 0.3) for x, y in [(-3.0, 2.6), (3.0, 2.8), (1.4, 2.6)]]
    ground = [snow(-2.6)]
    return make("Ice Castle", [wall, gate] + crenel + towers + windows + blocks + ics + shine + ground)


@design("winter_bird_feeder", T)
def bird_feeder(rng):
    pole = [[(-0.1, -2.7), (-0.1, -0.2)], [(0.1, -2.7), (0.1, -0.2)]]
    tray = rect(-1.4, -0.4, 1.4, -0.2)
    house = poly((-1.0, -0.2), (-1.0, 1.0), (1.0, 1.0), (1.0, -0.2), closed=False)
    roof = poly((-1.5, 0.9), (0, 2.0), (1.5, 0.9))
    snow_roof = smooth([(-1.6, 0.85), (-1.2, 1.35), (-0.6, 1.75), (0, 2.25), (0.6, 1.75), (1.2, 1.35), (1.6, 0.85)], 6)
    hole = circle(0, 0.45, 0.28, 20)
    def chickadee(x, y, s, flip):
        b = smooth([(0.55, 0.15), (0.5, 0.5), (0.2, 0.7), (-0.2, 0.55), (-0.5, 0.2), (-1.0, 0.05), (-0.95, -0.1), (-0.4, -0.2), (0.0, -0.35), (0.4, -0.2)], 6, True)
        cap = quad((0.47, 0.42), (0.1, 0.35), (-0.15, 0.57), 8)
        beak = poly((0.53, 0.3), (0.75, 0.25), (0.53, 0.18), closed=False)
        wing = lens((-0.25, 0.25), (-0.85, 0.0), 0.25)
        parts = [b, cap, beak, wing, [(0.0, -0.33), (0.0, -0.5)]]
        if flip:
            parts = mirror_all(parts)
        return [transform(p, dx=x, dy=y, s=s) for p in parts]
    birds = chickadee(-2.0, -0.05, 1.0, False) + chickadee(2.0, -0.05, 1.0, True)
    flyer = chickadee(-2.0, 2.2, 0.8, False)
    ground = [mound(-3.2, 3.2, -2.7, 0.25, 50)]
    return make("Bird Feeder in Winter", pole + [tray, house, roof, snow_roof, hole] + birds + flyer + ground,
                [eye(-1.75, 0.38, 0.05), eye(1.75, 0.38, 0.05), eye(-1.8, 2.5, 0.045)])


# ------------------------------------------------------------ cosy indoors

@design("winter_fireplace", T)
def fireplace(rng):
    outer = rect(-2.6, -2.6, 2.6, 1.2)
    mantel = rrect(-3.1, 1.2, 3.1, 1.55, 0.08)
    opening = chain([(-1.5, -2.6), (-1.5, -0.4)], arc(0, -0.4, 1.5, math.pi, 0, 30), [(1.5, -2.6)])
    hearth = rect(-3.0, -2.9, 3.0, -2.6)
    bricks = [[(-2.6, y), (-1.5, y)] for y in (-1.8, -1.0, -0.2, 0.6)] + [[(1.5, y), (2.6, y)] for y in (-1.8, -1.0, -0.2, 0.6)] + \
             [[(-2.05, y), (-2.05, y + 0.8)] for y in (-2.6, -1.0)] + [[(2.05, y), (2.05, y + 0.8)] for y in (-2.6, -1.0)] + \
             [[(-2.3, y), (-2.3, y + 0.8)] for y in (-1.8, -0.2)] + [[(2.3, y), (2.3, y + 0.8)] for y in (-1.8, -0.2)]
    logs = [transform(rrect(-1.1, -0.18, 1.1, 0.18, 0.18), dx=0, dy=-2.2, rot=0.18), transform(rrect(-1.1, -0.18, 1.1, 0.18, 0.18), dx=0, dy=-2.2, rot=-0.18)]
    flames = [chain(quad((-0.9, -1.9), (-1.0, -1.0), (-0.5, -0.6), 10), quad((-0.5, -0.6), (-0.6, -1.2), (-0.25, -1.4), 8),
                    quad((-0.25, -1.4), (-0.3, -0.4), (0.15, 0.2), 10), quad((0.15, 0.2), (0.1, -0.8), (0.45, -1.1), 8),
                    quad((0.45, -1.1), (0.55, -0.7), (0.8, -0.5), 8), quad((0.8, -0.5), (1.1, -1.3), (0.9, -1.9), 8))]
    inner_flame = chain(quad((-0.3, -1.9), (-0.4, -1.4), (-0.05, -1.0), 8), quad((-0.05, -1.0), (0.3, -1.5), (0.25, -1.9), 8))
    clock = [circle(0, 2.2, 0.55, 30), rect(-0.6, 1.55, 0.6, 1.75), [(0, 2.2), (0, 2.55)], [(0, 2.2), (0.25, 2.1)]]
    jars = [rrect(-2.4, 1.55, -1.9, 2.3, 0.1), rrect(-1.7, 1.55, -1.3, 2.05, 0.1), rrect(1.6, 1.55, 2.4, 2.0, 0.12),
            lens((1.8, 2.0), (1.5, 2.8), 0.3), lens((2.0, 2.0), (2.1, 2.9), 0.3), lens((2.2, 2.0), (2.7, 2.6), 0.3)]
    return make("Cozy Fireplace", [outer, mantel, opening, hearth, inner_flame] + bricks + logs + flames + clock + jars)


@design("winter_soup", T)
def soup(rng):
    bowl = chain([(-2.4, 0.0)], cubic((-2.4, 0.0), (-2.3, -2.0), (2.3, -2.0), (2.4, 0.0), 40))
    rim = ellipse(0, 0.0, 2.4, 0.5, 80)
    soup_ = ell_arc(0, -0.05, 2.1, 0.35, math.pi * 1.05, math.pi * 1.95, 30)
    foot = [quad((-0.9, -1.45), (0, -1.75), (0.9, -1.45), 10), [(-0.9, -1.45), (-1.0, -1.85)], [(0.9, -1.45), (1.0, -1.85)], [(-1.0, -1.85), (1.0, -1.85)]]
    chunks = [circle(x, y, 0.13, 10) for x, y in [(-1.0, 0.05), (-0.3, -0.15), (0.6, 0.1), (1.2, -0.12)]]
    spoon = [tube([(0.9, 0.05), (2.6, 2.0)], 0.2, cap=True)]
    steam = [smooth([(x, 0.7), (x - 0.25, 1.2), (x + 0.2, 1.7), (x - 0.15, 2.3), (x + 0.1, 2.8)], 6) for x in (-1.0, -0.2, 0.6)]
    plate = ellipse(0, -1.9, 3.0, 0.55, 80)
    return make("Bowl of Hot Soup", [bowl, rim, soup_, plate] + foot + chunks + spoon + steam)


@design("winter_teapot", T)
def teapot(rng):
    pot = smooth([(-1.1, 1.0), (-1.8, 0.4), (-1.9, -0.6), (-1.3, -1.4), (0.3, -1.4), (0.9, -0.6), (0.8, 0.4), (0.1, 1.0)], 8)
    pot = chain(pot, [(-1.1, 1.0)])
    lid = [chain([(-1.1, 1.0)], quad((-1.1, 1.0), (-0.5, 1.7), (0.1, 1.0), 14)), circle(-0.5, 1.55, 0.18, 12)]
    spout = chain([(-1.85, -0.4)], cubic((-1.85, -0.4), (-2.6, -0.5), (-2.6, 0.5), (-3.1, 0.9), 16),
                  [(-3.0, 1.1)], cubic((-3.0, 1.1), (-2.4, 0.9), (-2.4, 0.0), (-1.8, 0.1), 16))
    handle = chain(cubic((0.8, 0.3), (1.6, 0.6), (1.6, -0.9), (0.85, -0.9), 16))
    handle2 = chain(cubic((0.82, 0.0), (1.25, 0.1), (1.25, -0.6), (0.88, -0.6), 12))
    band = quad((-1.85, -0.2), (-0.5, -0.45), (0.85, -0.2), 16)
    flower = flake(-0.5, -0.85, 0.3)
    cup = [chain([(1.3, -1.4)], quad((1.3, -1.4), (1.35, -2.5), (2.15, -2.5), 10), quad((2.15, -2.5), (2.95, -2.5), (3.0, -1.4), 10)),
           ellipse(2.15, -1.4, 0.85, 0.18, 30), arc(3.05, -1.85, 0.3, -math.pi / 2, math.pi / 2, 10),
           ellipse(2.15, -2.55, 1.15, 0.2, 30)]
    steam = [smooth([(x, -1.0), (x - 0.15, -0.6), (x + 0.15, -0.2), (x, 0.2)], 6) for x in (1.9, 2.4)]
    tray = [[(-2.6, -1.42), (1.1, -1.42)]]
    return make("Teapot and Teacup", [pot, spout, handle, handle2, band] + lid + flower + cup + steam + tray)


@design("winter_woodpile", T)
def woodpile(rng):
    logs = []
    for row, (y, n) in enumerate([(-2.2, 5), (-1.4, 4), (-0.6, 3)]):
        for k in range(n):
            x = -2.4 + 0.8 * (k + 0.5 * row)
            logs.append(circle(x, y, 0.4, 30))
            logs.append(circle(x, y, 0.2, 18))
    roof = [poly((-3.0, 0.4), (-0.3, 1.0), (-0.3, 0.75), (-3.0, 0.15)), [(-2.8, 0.2), (-2.8, -2.6)], [(-0.45, 0.8), (-0.45, -2.6)]]
    snow_roof = smooth([(-3.0, 0.4), (-2.3, 0.75), (-1.4, 0.8), (-0.8, 1.05), (-0.3, 1.0)], 6)
    stump = [ellipse(1.9, -1.2, 0.9, 0.3, 40), [(1.0, -1.2), (1.0, -2.6)], [(2.8, -1.2), (2.8, -2.6)], ell_arc(1.9, -1.2, 0.5, 0.15, 0, 2 * math.pi, 20)]
    axe = [tube([(2.0, -1.0), (2.7, 1.6)], 0.18, cap=True), poly((1.6, -1.25), (2.35, -1.0), (2.45, -0.25), (1.75, -0.55), (1.45, -0.95))]
    chips = [poly((0.5, -2.6), (0.75, -2.45), (0.9, -2.6)), poly((3.0, -2.6), (3.2, -2.4), (3.35, -2.6))]
    ground = [snow(-2.6)]
    return make("Woodpile and Axe", logs + roof + [snow_roof] + stump + axe + chips + ground)


@design("winter_pine_cones", T)
def pine_cones(rng):
    branch = tube(quad((-3.2, 2.0), (0, 2.8), (3.2, 1.6), 30), lambda t: 0.3 - 0.15 * t, cap=True)
    needles = []
    for k in range(9):
        t = 0.06 + 0.11 * k
        x, y = (1 - t) ** 2 * -3.2 + 2 * (1 - t) * t * 0 + t * t * 3.2, (1 - t) ** 2 * 2.0 + 2 * (1 - t) * t * 2.8 + t * t * 1.6
        for a in (60, 90, 120, 240, 270, 300):
            L = 0.55
            needles.append([(x, y), (x + L * math.cos(math.radians(a + 20)), y + L * math.sin(math.radians(a + 20)))])
    cones = []
    for cx, cy, s in ((-1.0, 0.2, 1.0), (1.5, -0.2, 0.85)):
        out = ellipse(cx, cy - 0.4 * s, 0.85 * s, 1.5 * s, 60)
        cones.append(out)
        for r in range(5):
            yy = cy - 0.4 * s + (1.1 - 0.5 * r) * s
            w = 0.85 * s * math.sqrt(max(0, 1 - ((yy - (cy - 0.4 * s)) / (1.5 * s)) ** 2))
            n = 3 if r % 2 == 0 else 2
            for k in range(n):
                x0 = cx - w + (2 * w) * k / n
                x1 = cx - w + (2 * w) * (k + 1) / n
                cones.append(arc((x0 + x1) / 2, yy, (x1 - x0) / 2, math.pi, 2 * math.pi, 8))
        cones.append([(cx, cy + 1.1 * s), (cx + 0.05, 2.2 + 0.1 * (cx < 0))])
        cones.append(smooth([(cx - 0.75 * s, cy + 0.55 * s), (cx - 0.4 * s, cy + 0.95 * s), (cx, cy + 1.15 * s), (cx + 0.4 * s, cy + 0.95 * s), (cx + 0.75 * s, cy + 0.55 * s)], 6))
    snow_b = smooth([(-3.0, 2.25), (-1.8, 2.65), (-0.6, 2.75), (0.6, 2.75), (1.8, 2.4), (3.0, 1.85)], 8)
    return make("Snowy Pine Cones", [branch, snow_b] + needles + cones + flakes([(-2.6, -1.8, 0.25), (0.4, -2.4, 0.2), (2.8, -1.4, 0.22)]))


@design("winter_falling_snowflakes", T)
def falling_snowflakes(rng):
    out = []
    # big fern-like flake
    for k in range(6):
        a = math.pi / 2 + k * math.pi / 3
        ca, sa = math.cos(a), math.sin(a)
        out.append(tube([(0.55 * ca, 0.55 * sa), (2.1 * ca, 2.1 * sa)], 0.22, cap=True))
        for d in (1.0, 1.5):
            for s in (-1, 1):
                b = a + s * 0.7
                out.append([(d * ca, d * sa), (d * ca + 0.5 * math.cos(b), d * sa + 0.5 * math.sin(b))])
        out.append(poly((2.1 * ca, 2.1 * sa), ((2.1 * ca + 0.3 * math.cos(a + 0.6)), (2.1 * sa + 0.3 * math.sin(a + 0.6))),
                        (2.5 * ca, 2.5 * sa), ((2.1 * ca + 0.3 * math.cos(a - 0.6)), (2.1 * sa + 0.3 * math.sin(a - 0.6)))))
    out.append(poly(*[(0.55 * math.cos(math.pi / 2 + k * math.pi / 3), 0.55 * math.sin(math.pi / 2 + k * math.pi / 3)) for k in range(6)]))
    out.append(star(0, 0, 0.35, 6, 0.5))
    # two small plate flakes
    for cx, cy in ((-2.4, 2.5), (2.5, -2.4)):
        out.append(poly(*[(cx + 0.55 * math.cos(k * math.pi / 3), cy + 0.55 * math.sin(k * math.pi / 3)) for k in range(6)]))
        for k in range(6):
            a = k * math.pi / 3
            out.append([(cx + 0.55 * math.cos(a), cy + 0.55 * math.sin(a)), (cx + 0.9 * math.cos(a), cy + 0.9 * math.sin(a))])
    out += flakes([(2.5, 2.4, 0.3), (-2.5, -2.4, 0.3)])
    return make("Falling Snowflakes", out)


# ------------------------------------------------------------ animals

@design("winter_cardinal", T)
def cardinal(rng):
    body = smooth([(-2.1, 1.05), (-1.55, 1.3), (-1.35, 1.65), (-0.9, 2.2), (-0.55, 2.75), (-0.45, 2.1), (-0.25, 1.7), (0.4, 1.15), (1.1, 0.5),
                   (2.0, -0.4), (2.7, -1.15), (2.4, -1.4), (1.6, -0.8), (0.9, -0.55), (0.0, -0.45), (-0.9, 0.0), (-1.35, 0.55), (-1.6, 0.9)], 8, True)
    mask = smooth([(-1.62, 1.4), (-1.15, 1.55), (-1.0, 1.1), (-1.35, 0.7), (-1.62, 0.95)], 6)
    beak = [[(-2.1, 1.05), (-1.62, 1.1)]]
    wing = smooth([(-0.6, 1.0), (0.2, 1.05), (1.0, 0.45), (1.6, -0.3), (0.8, -0.2), (-0.2, 0.15)], 8, True)
    feathers = [[(0.3, 0.5), (1.0, 0.0)], [(0.0, 0.7), (0.7, 0.3)]]
    branch = tube(quad((-3.2, -1.3), (0, -0.7), (3.2, -1.7), 30), 0.3, cap=True)
    twig = [quad((-2.2, -1.1), (-2.6, -1.9), (-3.0, -2.4), 10), quad((1.6, -1.25), (2.2, -2.0), (2.9, -2.3), 10)]
    snow_b = smooth([(-3.1, -1.12), (-2.5, -0.75), (-1.6, -0.7), (-0.8, -0.85), (-0.35, -0.72)], 6)
    snow_b2 = smooth([(0.9, -0.88), (1.6, -0.75), (2.4, -1.05), (3.1, -1.5)], 6)
    feet = [[(-0.3, -0.45), (-0.4, -0.85)], [(0.2, -0.5), (0.15, -0.9)]]
    return make("Red Cardinal on a Snowy Branch", [body, mask, wing, branch, snow_b, snow_b2] + beak + feathers + twig + feet +
                flakes([(1.8, 2.4, 0.25), (2.7, 1.2, 0.2), (-2.6, -2.6, 0.2)]), [eye(-1.25, 1.35, 0.08)])


@design("winter_snowy_owl", T)
def snowy_owl(rng):
    half = [(0, 2.75), (0.9, 2.6), (1.45, 1.95), (1.35, 1.1), (1.65, 0.0), (1.5, -1.2), (0.85, -1.95), (0, -2.1)]
    body = smooth(half + [(-x, y) for x, y in half[-2:0:-1]], 8, True)
    discs = [circle(-0.55, 1.6, 0.6, 36), circle(0.55, 1.6, 0.6, 36)]
    eyes_ = [circle(-0.55, 1.6, 0.3, 20), circle(0.55, 1.6, 0.3, 20)]
    beak = poly((-0.15, 1.2), (0, 0.85), (0.15, 1.2))
    wings = [smooth([(1.35, 1.0), (1.0, 0.0), (0.95, -1.0), (0.6, -1.85)], 6), smooth([(-1.35, 1.0), (-1.0, 0.0), (-0.95, -1.0), (-0.6, -1.85)], 6)]
    spots = []
    for x, y in [(-0.4, 0.3), (0.3, 0.1), (-0.1, -0.5), (0.5, -0.9), (-0.55, -1.1), (0.0, -1.5), (1.25, 0.2), (-1.25, 0.2), (1.25, -0.8), (-1.25, -0.8)]:
        spots.append(poly((x - 0.15, y + 0.08), (x, y - 0.05), (x + 0.15, y + 0.08), closed=False))
    branch = tube([(-3.2, -2.3), (3.2, -2.1)], 0.35, cap=True)
    talons = [[(x, -2.05), (x + dx, -2.35)] for x in (-0.55, 0.45) for dx in (-0.12, 0.05, 0.2)]
    snow_b = smooth([(-3.1, -2.12), (-2.2, -1.85), (-1.3, -1.95)], 6)
    snow_b2 = smooth([(1.2, -1.95), (2.2, -1.75), (3.1, -1.92)], 6)
    return make("Snowy Owl in Winter", [body, beak, branch, snow_b, snow_b2] + discs + eyes_ + wings + spots + talons +
                flakes([(-2.5, 2.4, 0.25), (2.5, 2.6, 0.22), (2.7, 0.6, 0.18)]), [eye(-0.55, 1.6, 0.14), eye(0.55, 1.6, 0.14)])


@design("winter_polar_bear", T)
def polar_bear(rng):
    body = smooth([(3.0, 0.55), (2.6, 0.85), (2.2, 1.15), (1.95, 1.45), (1.7, 1.3), (1.2, 1.25), (0.0, 1.55), (-1.5, 1.5), (-2.4, 1.2),
                   (-2.8, 0.6), (-2.6, -0.4), (-2.55, -1.4), (-2.6, -1.75), (-1.8, -1.8), (-1.75, -1.3), (-1.4, -0.5), (-0.5, -0.45),
                   (0.6, -0.5), (0.8, -1.0), (0.75, -1.75), (1.6, -1.8), (1.55, -1.2), (1.8, -0.3), (2.2, 0.2), (2.7, 0.35)], 8, True)
    far = [smooth([(-1.3, -0.5), (-1.2, -1.2), (-1.15, -1.65)], 6), [(-1.15, -1.65), (-0.6, -1.65)], smooth([(-0.65, -1.65), (-0.6, -1.0), (-0.5, -0.5)], 6),
           smooth([(0.35, -0.5), (0.2, -1.2), (0.1, -1.65)], 6), [(0.1, -1.65), (0.6, -1.65)]]
    far = [smooth([(-1.0, -0.48), (-0.95, -1.2), (-1.05, -1.7), (-0.4, -1.72), (-0.45, -1.0), (-0.3, -0.48)], 6),
           smooth([(0.1, -0.5), (0.05, -1.2), (-0.05, -1.7), (0.55, -1.72)], 6)]
    ear = arc(1.85, 1.38, 0.18, math.radians(-20), math.radians(200), 10)
    nose = ellipse(2.95, 0.6, 0.12, 0.09, 12)
    mouth = [quad((2.9, 0.42), (2.7, 0.3), (2.5, 0.36), 6)]
    toes = [[(x, -1.8), (x, -1.62)] for x in (1.0, 1.25, -2.3, -2.05)]
    floe = poly((-3.3, -1.8), (3.3, -1.8), (3.0, -2.35), (-3.0, -2.35))
    water = [snow(-2.7, amp=0.08, waves=6)]
    cracks = [[(-1.0, -1.8), (-0.8, -2.35)], [(2.0, -1.8), (2.2, -2.35)]]
    return make("Polar Bear on the Ice", [body, ear, nose, floe] + far + mouth + toes + water + cracks + flakes([(-1.5, 2.6, 0.25), (1.0, 2.8, 0.2), (2.8, 2.2, 0.2)]),
                [eye(2.35, 0.9, 0.08)])


@design("winter_penguin", T)
def penguin(rng):
    half = [(0, 2.7), (0.65, 2.5), (0.85, 1.85), (1.0, 1.0), (1.35, -0.3), (1.25, -1.5), (0.7, -2.15), (0, -2.25)]
    body = smooth(half + [(-x, y) for x, y in half[-2:0:-1]], 8, True)
    belly = smooth([(-0.45, 1.45), (-0.8, 0.4), (-0.95, -0.9), (-0.55, -1.85), (0, -1.95), (0.55, -1.85), (0.95, -0.9), (0.8, 0.4), (0.45, 1.45),
                    (0.0, 1.6)], 8, True)
    face = [arc(-0.3, 1.9, 0.3, math.radians(180), math.radians(330), 10), arc(0.3, 1.9, 0.3, math.radians(210), math.radians(360), 10)]
    beak = poly((-0.2, 1.6), (0, 1.15), (0.2, 1.6))
    flips = [smooth([(-1.0, 1.0), (-1.6, 0.2), (-1.9, -0.8), (-1.25, -0.3)], 6), smooth([(1.0, 1.0), (1.6, 0.2), (1.9, -0.8), (1.25, -0.3)], 6)]
    feet = [ellipse(-0.5, -2.3, 0.45, 0.15, 20), ellipse(0.5, -2.3, 0.45, 0.15, 20)]
    floe = poly((-2.8, -2.45), (2.6, -2.45), (2.2, -2.85), (-2.4, -2.85))
    water = [wave(-3.3, -2.7, -2.7, 0.06, 1, 10), wave(2.5, 3.3, -2.7, 0.06, 1, 10)]
    return make("Penguin on an Ice Floe", [body, belly, beak, floe] + face + flips + feet + water +
                flakes([(-2.5, 2.4, 0.25), (2.5, 2.6, 0.25), (-2.3, 0.4, 0.18), (2.4, 0.8, 0.2)]), [eye(-0.35, 1.95, 0.1), eye(0.35, 1.95, 0.1)])


@design("winter_arctic_fox", T)
def arctic_fox(rng):
    body = smooth([(-2.1, 1.55), (-1.6, 1.85), (-1.2, 2.1), (-1.05, 2.9), (-0.65, 2.3), (-0.35, 2.85), (-0.2, 2.0), (0.15, 1.3), (0.8, 0.5),
                   (1.3, -0.4), (1.3, -1.3), (0.9, -1.6), (-0.1, -1.6), (-0.5, -1.5), (-0.7, -0.3), (-0.95, 0.6), (-1.25, 1.15), (-1.7, 1.3)], 8, True)
    tail = smooth([(1.15, -0.9), (2.1, -0.8), (2.6, -1.4), (2.3, -2.0), (1.0, -2.25), (-0.8, -2.2), (-2.0, -1.9), (-2.3, -1.5), (-1.6, -1.55),
                   (-0.4, -1.75), (0.8, -1.6)], 8)
    tail_tip = [quad((-1.5, -2.05), (-1.3, -1.8), (-1.45, -1.55), 8)]
    legs_ = [[(-0.55, -0.4), (-0.6, -1.55)], [(-0.2, -0.5), (-0.25, -1.55)]]
    ears = [lens((-1.1, 2.15), (-1.0, 2.7), 0.18), lens((-0.5, 2.15), (-0.38, 2.65), 0.18)]
    nose = ellipse(-2.05, 1.55, 0.1, 0.08, 10)
    mouth = [quad((-1.95, 1.4), (-1.75, 1.3), (-1.55, 1.38), 6)]
    fur = [[(0.4, 0.2), (0.6, 0.0)], [(0.7, -0.6), (0.95, -0.8)], [(-1.0, 0.9), (-0.8, 0.75)]]
    ground = [snow(-2.5)]
    return make("Arctic Fox", [body, tail, nose] + tail_tip + legs_ + ears + mouth + fur + ground +
                flakes([(1.6, 2.4, 0.25), (2.6, 1.2, 0.22), (0.6, 2.8, 0.18)]), [eye(-1.35, 1.75, 0.08)])


@design("winter_snowshoe_hare", T)
def snowshoe_hare(rng):
    body = smooth([(2.05, 0.85), (1.85, 1.35), (1.3, 1.6), (0.8, 1.4), (0.3, 1.0), (-0.8, 0.8), (-1.6, 0.2), (-1.9, -0.6), (-1.7, -1.3),
                   (-1.4, -1.65), (0.5, -1.75), (0.75, -1.55), (0.3, -1.35), (0.9, -1.45), (1.25, -1.5), (1.15, -1.1), (1.1, -0.2),
                   (1.5, 0.4), (1.9, 0.6)], 8, True)
    ears = [lens((1.15, 1.5), (0.3, 3.1), 0.17), lens((0.85, 1.4), (-0.25, 2.8), 0.17)]
    ear_in = [[(1.0, 1.75), (0.45, 2.75)]]
    haunch = arc(-0.8, -0.6, 0.85, math.radians(20), math.radians(200), 20)
    tail = circle(-1.95, -0.45, 0.3, 30)
    nose = ellipse(2.02, 0.92, 0.07, 0.06, 8)
    whiskers = [[(2.0, 0.8), (2.6, 0.95)], [(2.0, 0.75), (2.55, 0.6)]]
    ground = [snow(-1.75, amp=0.06), mound(-3.2, -1.0, -1.75, 0.25)]
    tracks = [ellipse(x, y, 0.13, 0.28, 12) for x, y in [(1.8, -2.4), (2.2, -2.3), (2.75, -2.7), (2.75, -2.15)]]
    trees = pine(-3.0, -1.75, 2.4, 0.55)
    return make("Snowshoe Hare", [body, tail, nose, haunch] + ears + ear_in + whiskers + ground + tracks + trees + flakes([(2.5, 2.5, 0.22)]),
                [eye(1.45, 1.15, 0.09)])


@design("winter_moose", T)
def moose(rng):
    body = smooth([(-2.9, 0.0), (-3.0, 0.35), (-2.6, 0.75), (-2.0, 1.2), (-1.6, 1.4), (-1.1, 1.5), (-0.6, 1.95), (0.8, 1.55), (2.2, 1.45),
                   (2.6, 1.0), (2.6, 0.3), (2.35, -0.3), (2.45, -1.1), (2.4, -2.35), (2.1, -2.4), (2.1, -1.2), (1.85, -0.5), (1.6, -0.35),
                   (0.6, -0.35), (-0.6, -0.35), (-0.8, -0.6), (-0.75, -1.3), (-0.85, -1.6), (-0.85, -2.35), (-1.15, -2.4), (-1.2, -1.5),
                   (-1.15, -0.6), (-1.4, 0.15), (-1.7, -0.35), (-1.9, -0.05), (-2.2, 0.1), (-2.6, -0.1)], 8, True)
    far = [smooth([(1.3, -0.4), (1.1, -1.2), (0.75, -2.3), (1.0, -2.35)], 6), smooth([(-0.2, -0.4), (0.05, -1.3), (0.55, -2.3), (0.3, -2.35)], 6)]
    antler = poly((-1.7, 1.45), (-1.95, 1.95), (-2.4, 2.0), (-2.85, 2.05), (-3.25, 2.25), (-3.0, 2.38), (-3.2, 2.7), (-2.88, 2.62), (-2.9, 3.0),
                  (-2.62, 2.78), (-2.5, 3.15), (-2.3, 2.82), (-2.1, 3.12), (-2.0, 2.72), (-1.75, 2.95), (-1.75, 2.48), (-1.52, 2.55),
                  (-1.6, 2.1), (-1.5, 1.6))
    antler2 = poly((-1.4, 1.55), (-1.2, 2.0), (-0.85, 2.3), (-0.75, 2.75), (-1.0, 2.6), (-1.05, 2.95), (-1.25, 2.65), (-1.45, 2.85),
                   (-1.45, 2.4), (-1.3, 2.05), closed=False)
    ear = lens((-1.45, 1.35), (-0.95, 1.7), 0.25)
    palm_line = [quad((-2.7, 2.2), (-2.3, 2.45), (-1.85, 2.3), 10)]
    nostril = [ellipse(-2.85, 0.3, 0.08, 0.05, 8)]
    mouth = [quad((-2.95, 0.05), (-2.7, -0.05), (-2.5, 0.0), 6)]
    hooves = [[(2.25, -2.4), (2.25, -2.2)], [(-1.0, -2.4), (-1.0, -2.2)]]
    ground = [snow(-2.45)]
    trees = pine(3.0, -2.45, 2.6, 0.5)
    return make("Moose in the Snow", [body, antler, antler2, ear] + palm_line + far + nostril + mouth + hooves + ground + trees +
                flakes([(0.6, 2.8, 0.22), (2.0, 2.4, 0.2)]), [eye(-2.0, 0.95, 0.08)])


@design("winter_deer", T)
def deer(rng):
    body = smooth([(2.6, 1.5), (2.45, 1.28), (2.0, 1.22), (1.55, 0.85), (1.35, 0.3), (1.25, -0.15), (1.2, -0.6), (1.1, -1.3), (1.15, -2.35),
                   (1.2, -2.45), (0.95, -2.45), (0.93, -1.35), (0.9, -0.7), (0.5, -0.45), (-0.3, -0.4), (-0.9, -0.45), (-1.05, -0.75),
                   (-1.2, -1.35), (-1.05, -2.35), (-1.0, -2.45), (-1.27, -2.45), (-1.33, -1.6), (-1.55, -1.25), (-1.7, -0.6), (-1.85, 0.2),
                   (-2.05, 0.45), (-1.8, 0.6), (-1.0, 0.65), (0.6, 0.65), (1.1, 1.2), (1.6, 1.75), (1.85, 1.88), (2.15, 1.8)], 8, True)
    far = [smooth([(0.55, -0.45), (0.3, -1.3), (-0.05, -2.35), (0.17, -2.42)], 6), smooth([(-0.55, -0.45), (-0.3, -1.3), (0.2, -2.35), (0.42, -2.42)], 6)]
    ears = [lens((1.65, 1.85), (1.1, 2.35), 0.3)]
    antlers = [smooth([(1.85, 1.88), (1.8, 2.5), (1.5, 3.0), (1.0, 3.2)], 6), [(1.8, 2.45), (2.2, 2.9)], [(1.6, 2.85), (1.65, 3.3)],
               smooth([(2.05, 1.83), (2.2, 2.3), (2.5, 2.6)], 6)]
    nose = [ellipse(2.55, 1.45, 0.07, 0.06, 8)]
    tail_ = [[(-1.95, 0.5), (-1.75, 0.3)]]
    ground = [snow(-2.5)]
    trees = pine(-2.6, -2.5, 3.0, 0.7) + pine(2.7, -2.5, 2.0, 0.5)
    return make("Deer in a Snowy Forest", [body] + far + ears + antlers + nose + tail_ + ground + trees + flakes([(0.0, 2.6, 0.22), (-1.2, 1.8, 0.18)]),
                [eye(2.05, 1.6, 0.07)])


@design("winter_husky", T)
def husky(rng):
    head = smooth([(0, 0.55), (0.75, 0.8), (1.15, 1.4), (1.2, 2.1), (1.3, 3.2), (0.65, 2.65), (0, 2.75), (-0.65, 2.65), (-1.3, 3.2), (-1.2, 2.1),
                   (-1.15, 1.4), (-0.75, 0.8)], 8, True)
    mask = smooth([(-1.1, 1.5), (-0.65, 1.35), (-0.25, 1.75), (0, 2.45), (0.25, 1.75), (0.65, 1.35), (1.1, 1.5)], 6)
    ear_in = [lens((-1.0, 2.35), (-1.15, 2.95), 0.18), lens((1.0, 2.35), (1.15, 2.95), 0.18)]
    muzzle = smooth([(-0.4, 1.3), (-0.45, 0.9), (0, 0.7), (0.45, 0.9), (0.4, 1.3)], 6)
    nose = ellipse(0, 1.25, 0.2, 0.13, 14)
    mouth = [[(0, 1.12), (0, 0.95)], arc(-0.15, 0.95, 0.15, math.pi, 2 * math.pi, 6), arc(0.15, 0.95, 0.15, math.pi, 2 * math.pi, 6)]
    bodyl = smooth([(-0.75, 0.8), (-1.2, -0.2), (-1.4, -1.0), (-2.0, -1.6), (-2.1, -2.3), (-1.6, -2.5), (-0.6, -2.5)], 8)
    bodyr = mirror_x(bodyl)
    legs_ = [[(-0.6, -2.5), (-0.55, -0.6)], [(0.6, -2.5), (0.55, -0.6)], [(-0.1, -2.5), (-0.1, -1.4)], [(0.1, -2.5), (0.1, -1.4)]]
    legs_ = [smooth([(-0.75, -0.3), (-0.6, -1.4), (-0.65, -2.5)], 6), smooth([(0.75, -0.3), (0.6, -1.4), (0.65, -2.5)], 6),
             [(0.0, -2.5), (0.0, -1.2)]]
    chest = [smooth([(-0.4, 0.55), (0, -0.3), (0.4, 0.55)], 6)]
    tail = smooth([(1.95, -2.2), (2.8, -1.7), (2.9, -0.6), (2.5, -0.2), (2.35, -0.9), (2.25, -1.5), (1.85, -1.75)], 8)
    snow_ = [snow(-2.5, amp=0.06)]
    return make("Husky in the Snow", [head, mask, muzzle, nose, bodyl, bodyr, tail] + ear_in + mouth + legs_ + chest + snow_ +
                flakes([(-2.5, 2.5, 0.25), (2.5, 2.4, 0.22), (-2.6, 0.6, 0.2)]), [eye(-0.45, 1.75, 0.11), eye(0.45, 1.75, 0.11)])


def run_dog(x, y, s):
    b = smooth([(1.0, 0.55), (0.8, 0.68), (0.62, 0.8), (0.52, 1.15), (0.36, 0.86), (0.2, 0.72), (-0.3, 0.58), (-0.85, 0.58), (-1.0, 0.62),
                (-1.25, 0.95), (-1.0, 1.12), (-0.88, 0.85), (-0.98, 0.45), (-1.2, 0.05), (-1.65, -0.4), (-1.55, -0.5), (-1.0, -0.15),
                (-0.75, 0.08), (-0.2, 0.12), (0.35, 0.05), (0.75, -0.25), (1.15, -0.4), (1.2, -0.28), (0.85, -0.02), (0.72, 0.3),
                (0.82, 0.45), (0.98, 0.48)], 6, True)
    far_legs = [smooth([(-0.55, 0.1), (-0.8, -0.2), (-1.15, -0.5), (-1.05, -0.55)], 6), smooth([(0.2, 0.08), (0.5, -0.3), (0.85, -0.5), (0.95, -0.45)], 6)]
    harness = [[(-0.2, 0.6), (0.05, 0.12)], [(-0.75, 0.58), (-0.6, 0.1)]]
    parts = [b] + far_legs + harness
    return [transform(p, dx=x, dy=y, s=s) for p in parts], (x + (0.0) * s, y + 0.35 * s), (x + 0.8 * s, y + 0.75 * s)


@design("winter_dog_sled", T)
def dog_sled(rng):
    runner = chain([(-3.9, -1.9), (-1.3, -1.9)], arc(-1.3, -1.6, 0.3, -math.pi / 2, math.pi / 2, 10), [(-1.5, -1.3)])
    bed = [rrect(-3.0, -1.35, -1.3, -1.15, 0.06)]
    stanch = [[(-2.7, -1.9), (-2.7, -1.35)], [(-1.7, -1.9), (-1.7, -1.35)], [(-3.0, -1.9), (-3.0, 0.1)], [(-3.0, -0.4), (-1.6, -1.15)]]
    bag = [rrect(-2.85, -1.15, -1.95, -0.6, 0.2)]
    head = circle(-3.65, 1.75, 0.3, 24)
    hood = arc(-3.65, 1.75, 0.45, math.radians(-40), math.radians(220), 20)
    coat = poly((-3.95, 1.3), (-3.35, 1.3), (-3.1, -0.4), (-4.2, -0.4))
    zip_ = [[(-3.65, 1.3), (-3.65, -0.4)]]
    legs_ = [tube([(-3.95, -0.4), (-3.85, -1.85)], 0.3, cap=False), tube([(-3.45, -0.4), (-3.4, -1.85)], 0.3, cap=False)]
    arm = tube([(-3.45, 1.1), (-3.1, 0.5), (-3.0, 0.15)], 0.24, cap=True)
    d1, h1, n1 = run_dog(1.0, -1.45, 1.4)
    line = [[(-1.3, -1.45), h1]]
    ground = [[(-4.3, -2.05), (2.8, -2.05)], snow(-2.6, x0=-4.3, x1=2.8)]
    hills = [mountains(0.6, [(-1.2, 0.6), (0.0, 2.2), (0.8, 1.4), (1.8, 2.8), (2.8, 1.0)])]
    trees = pine(-1.8, 0.0, 1.4, 0.45)
    return make("Husky Pulling a Sled", [runner, head, hood, coat, arm] + zip_ + bed + stanch + bag + legs_ + d1 + line + ground + hills + trees +
                flakes([(-2.2, 2.6, 0.22), (-0.8, 3.0, 0.2)]), [eye(n1[0] - 0.1, n1[1] - 0.05, 0.06)])
