"""Camping & Outdoors niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "camping"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ---------------------------------------------------------------- helpers

def stars(pts):
    return [star(x, y, r) for x, y, r in pts]


def crescent(cx, cy, r, d):
    th = math.acos(d / (2 * r))
    return chain(arc(cx, cy, r, th, TAU - th, 40), arc(cx + d, cy, r, math.pi + th, math.pi - th, 30))


def earc(cx, cy, rx, ry, a0, a1, n=40, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    out = []
    for i in range(n + 1):
        t = a0 + (a1 - a0) * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def pine(cx, by, h, w, tiers=3):
    """Closed pine-tree silhouette with a short trunk."""
    tw, th = max(0.1, w * 0.08), h * 0.12
    ys = [by + th + (h - th) * 0.78 * i / tiers for i in range(tiers)]
    halves = [w / 2 * (1 - 0.5 * i / tiers) for i in range(tiers)]
    left = [(cx - tw, by), (cx - tw, ys[0])]
    for i in range(tiers):
        left.append((cx - halves[i], ys[i]))
        if i + 1 < tiers:
            left.append((cx - halves[i + 1] * 0.45, ys[i + 1]))
    left.append((cx, by + h))
    right = [(2 * cx - x, y) for x, y in reversed(left)]
    return chain(left, right[1:], [left[0]])


def flame(cx, by, w, h):
    return chain(cubic((cx - w / 2, by), (cx - w * 0.75, by + h * 0.45), (cx - w * 0.1, by + h * 0.55), (cx, by + h), 16),
                 cubic((cx, by + h), (cx + w * 0.15, by + h * 0.55), (cx + w * 0.75, by + h * 0.45), (cx + w / 2, by), 16),
                 quad((cx + w / 2, by), (cx, by - w * 0.35), (cx - w / 2, by), 10))


def log_end(p0, p1, w):
    """Side view of a log from p0 to p1 with an end-grain ring at p1."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    rot = math.atan2(dy, dx)
    body = [(p1[0] + nx, p1[1] + ny), (p0[0] + nx, p0[1] + ny)] + \
        earc(p0[0], p0[1], w * 0.22, w / 2, math.pi / 2, 3 * math.pi / 2, 12, rot) + [(p1[0] - nx, p1[1] - ny)]
    end = ellipse(p1[0], p1[1], w * 0.22, w / 2, 24, rot=rot)
    return [body, end]


def grass(x, y, s=0.3):
    return poly((x - s, y), (x - s * 0.5, y + s * 1.2), (x, y), (x + s * 0.3, y + s * 1.4), (x + s * 0.6, y), closed=False)


def stone(cx, cy, rx, ry):
    return [(cx + rx * math.cos(t) * (1 + 0.08 * math.sin(3 * t + cx)), cy + ry * math.sin(t) * (1 + 0.08 * math.cos(2 * t + cy)))
            for t in [TAU * i / 30 for i in range(31)]]


def peg(x, y):
    return [(x, y + 0.2), (x - 0.12, y - 0.3)]


def flame_group(cx, by, s=1.0):
    return [flame(cx, by, 0.9 * s, 1.5 * s), flame(cx - 0.55 * s, by, 0.55 * s, 0.9 * s), flame(cx + 0.55 * s, by, 0.55 * s, 1.0 * s)]


def crossed_logs(cx, by, s=1.0):
    out = []
    out += log_end((cx + 1.3 * s, by - 0.15 * s), (cx - 1.4 * s, by + 0.25 * s), 0.38 * s)
    out += log_end((cx - 1.3 * s, by - 0.15 * s), (cx + 1.4 * s, by + 0.25 * s), 0.38 * s)
    return out


# ---------------------------------------------------------------- tents

@design("camping_dome_tent", T)
def dome_tent(rng):
    gy = -1.7
    shell = chain(cubic((-2.7, gy), (-2.6, 0.6), (-1.3, 1.5), (0, 1.55), 30), cubic((0, 1.55), (1.3, 1.5), (2.6, 0.6), (2.7, gy), 30))
    seams = [cubic((-1.9, gy), (-1.8, 0.6), (-0.8, 1.45), (0, 1.55), 24), cubic((1.9, gy), (1.8, 0.6), (0.8, 1.45), (0, 1.55), 24)]
    door = chain(cubic((-1.1, gy), (-1.1, 0.0), (-0.6, 0.85), (0, 0.9), 20), cubic((0, 0.9), (0.6, 0.85), (1.1, 0.0), (1.1, gy), 20))
    zip_ = [(0, 0.9), (0, gy)]
    pull = [circle(0.15, -0.3, 0.12, 10)]
    ground = [(-3.6, gy), (3.6, gy)]
    guys = [[(-2.45, -0.3), (-3.3, gy)], [(2.45, -0.3), (3.3, gy)]]
    pegs = [peg(-3.3, gy), peg(3.3, gy)]
    sky = stars([(-2.6, 2.6, 0.22), (-1.2, 2.9, 0.18), (0.4, 2.5, 0.25), (1.6, 3.0, 0.17), (3.0, 2.4, 0.2), (-3.2, 1.3, 0.15)])
    moon = [crescent(2.2, 1.6, 0.55, 0.35)]
    tufts = [grass(-2.2, gy, 0.25), grass(2.0, gy, 0.25), grass(-0.5, gy, 0.2)]
    return make("Dome Tent Under the Stars", [shell, door, zip_, ground] + seams + pull + guys + pegs + sky + moon + tufts)


@design("camping_a_frame_tent", T)
def a_frame_tent(rng):
    A, B, C = (-3.0, -1.7), (-1.2, 1.0), (0.6, -1.7)
    B2, C2 = (2.2, 1.7), (3.2, -0.9)
    front = poly(A, B, C)
    side = poly(B, B2, C2, C, closed=False)
    seam = [((B[0] + B2[0]) / 2, (B[1] + B2[1]) / 2), ((C[0] + C2[0]) / 2, (C[1] + C2[1]) / 2)]
    D, E = (-1.95, -1.7), (-0.45, -1.7)
    flapL = quad(B, (-2.4, -0.5), D, 16)
    flapR = quad(B, (-0.1, -0.5), E, 16)
    edges = [[B, (-1.75, -1.7)], [B, (-0.65, -1.7)]]
    ties = [ellipse(-2.05, -0.55, 0.12, 0.2, 10), ellipse(-0.3, -0.55, 0.12, 0.2, 10)]
    poles = [[B, (B[0], B[1] + 0.45)], [B2, (B2[0], B2[1] + 0.45)]]
    guys = [[(B[0], B[1] + 0.45), (-2.8, -2.4)], [(B2[0], B2[1] + 0.45), (3.6, 0.0)]]
    pegs = [peg(-2.8, -2.4), peg(3.6, 0.0), peg(0.9, -2.5), peg(2.6, -2.0)]
    window = poly((0.9, 0.4), (1.6, 0.6), (1.75, 0.0), (1.05, -0.2))
    tufts = [grass(-3.3, -1.75, 0.25), grass(1.2, -1.95, 0.25), grass(-0.1, -2.3, 0.2), grass(3.2, -1.2, 0.22)]
    return make("A-Frame Ridge Tent", [front, side, seam, flapL, flapR, window] + edges + ties + poles + guys + pegs[:2] + tufts)


@design("camping_open_tent", T)
def open_tent(rng):
    gy = -1.9
    shell = chain(cubic((-3.0, gy), (-3.0, 1.0), (-1.6, 2.1), (0, 2.1), 30), cubic((0, 2.1), (1.6, 2.1), (3.0, 1.0), (3.0, gy), 30))
    door = chain(cubic((-2.0, gy), (-2.0, 0.5), (-1.1, 1.2), (0, 1.2), 24), cubic((0, 1.2), (1.1, 1.2), (2.0, 0.5), (2.0, gy), 24))
    roll = [rrect(-1.1, 1.32, 1.1, 1.72, 0.2), [(-0.5, 1.2), (-0.5, 1.32)], [(0.5, 1.2), (0.5, 1.32)]]
    bag = poly((-0.75, -0.3), (0.75, -0.3), (1.4, gy), (-1.4, gy))
    pillow = rrect(-0.7, -0.25, 0.7, 0.3, 0.18)
    fold = poly((-1.12, -1.05), (1.15, -1.25), (1.27, -1.55), (-1.25, -1.35), closed=False)
    zip_ = [(0.5, -0.3), (0.95, -1.15)]
    ground = [(-3.6, gy), (3.6, gy)]
    guys = [[(-2.8, 0.0), (-3.5, gy)], [(2.8, 0.0), (3.5, gy)]]
    boots = [stone(2.6, -1.75, 0.3, 0.15), grass(-2.5, gy, 0.25)]
    return make("Open Tent with a Sleeping Bag", [shell, door, bag, pillow, fold, zip_, ground] + roll + guys + boots)


@design("camping_bell_tent", T)
def bell_tent(rng):
    wall = poly((-2.4, -0.6), (-2.4, -1.7), (2.4, -1.7), (2.4, -0.6), closed=False)
    roof = chain(quad((-2.7, -0.6), (-1.0, 0.2), (0, 1.7), 16), quad((0, 1.7), (1.0, 0.2), (2.7, -0.6), 16))
    hem = wave(-2.7, 2.7, -0.6, 0.08, 9, 90)
    spike = [[(0, 1.7), (0, 2.3)], circle(0, 2.42, 0.12, 10)]
    seams = [quad((0, 1.7), (-0.8, 0.3), (-1.2, -0.55), 12), quad((0, 1.7), (0.8, 0.3), (1.2, -0.55), 12)]
    door = [poly((-0.9, -1.7), (0, 0.3), (0.9, -1.7), closed=False)]
    flaps = [quad((0, 0.3), (-1.6, -0.6), (-1.05, -1.7), 14), quad((0, 0.3), (1.6, -0.6), (1.05, -1.7), 14)]
    guys = [[(-2.7, -0.6), (-3.5, -1.7)], [(2.7, -0.6), (3.5, -1.7)], [(-1.8, -0.35), (-3.0, -2.4)], [(1.8, -0.35), (3.0, -2.4)]]
    pegs = [peg(-3.5, -1.7), peg(3.5, -1.7), peg(-3.0, -2.4), peg(3.0, -2.4)]
    flag = [poly((0, 2.3), (0, 2.95), (0.7, 2.75), (0, 2.55), closed=False)]
    ground = [(-3.2, -1.7), (3.2, -1.7)]
    return make("Canvas Bell Tent", [wall, roof, hem, ground] + spike + seams + door + flaps + guys + pegs + flag)


@design("camping_teepee_tent", T)
def teepee_tent(rng):
    gy = -2.0
    poles = [[(-2.3, gy), (0.55, 2.3)], [(2.3, gy), (-0.55, 2.3)], [(-0.12, 1.6), (-0.3, 2.6)], [(0.12, 1.6), (0.3, 2.6)]]
    hem = [(-2.3, gy), (2.3, gy)]
    door = chain(cubic((-0.8, gy), (-0.8, -0.8), (-0.4, -0.35), (0, -0.35), 14), cubic((0, -0.35), (0.4, -0.35), (0.8, -0.8), (0.8, gy), 14))
    flap = quad((0.55, -0.6), (1.5, -1.0), (1.25, gy), 12)

    def ex(y):
        return 2.3 * (1.6 - y) / 3.6

    band = []
    y0, y1 = -1.2, -0.75
    for side in (-1, 1):
        xa, xb = (ex(y0) - 0.05, 1.0) if side > 0 else (-(ex(y0) - 0.05), -1.0)
        band.append(zigzag(min(xa, xb), max(xa, xb), (y0 + y1) / 2, 0.2, 3))
    top_band = zigzag(-ex(0.75) + 0.05, ex(0.75) - 0.05, 0.75, 0.15, 3)
    smoke = [cubic((0.4, 2.7), (0.9, 2.9), (0.2, 3.1), (0.8, 3.4), 16)]
    tufts = [grass(-2.8, gy, 0.25), grass(2.8, gy, 0.25)]
    sky = stars([(-2.4, 2.4, 0.22), (2.3, 2.6, 0.18), (-1.4, 3.0, 0.16)])
    return make("Canvas Teepee Tent", [hem, door, flap, top_band] + poles + band + smoke + tufts + sky)


@design("camping_hammock_tent", T)
def hammock_tent(rng):
    trunks = [[(-3.1, -2.6), (-3.05, 1.6)], [(-2.55, -2.6), (-2.6, 1.6)], [(3.1, -2.6), (3.05, 1.6)], [(2.55, -2.6), (2.6, 1.6)]]
    crowns = [polar(lambda t: 1.0 + 0.09 * math.sin(9 * t), cx=x, cy=2.3, n=140) for x in (-2.85, 2.85)]
    ridge = [(-2.6, 0.9), (2.6, 0.9)]
    tarp = poly((-2.2, 0.9), (-1.8, -0.05), (1.8, -0.05), (2.2, 0.9), closed=False)
    tarp_mid = [(0, 0.9), (0, -0.05)]
    straps = [[(-2.6, 0.2), (-1.7, -0.6)], [(2.6, 0.2), (1.7, -0.6)]]
    body = chain(quad((-1.7, -0.6), (0, -1.0), (1.7, -0.6), 20), quad((1.7, -0.6), (0, -2.1), (-1.7, -0.6), 20))
    net = quad((-1.5, -0.65), (0, -0.2), (1.5, -0.65), 16)
    tarp_guys = [[(-1.8, -0.05), (-2.3, -2.6)], [(1.8, -0.05), (2.3, -2.6)]]
    ground = [[(-3.6, -2.6), (-3.1, -2.6)], [(-2.55, -2.6), (2.55, -2.6)], [(3.1, -2.6), (3.6, -2.6)]]
    pack = [rrect(-1.2, -2.6, -0.4, -1.6, 0.25), [(-1.2, -2.1), (-0.4, -2.1)]]
    return make("Hammock Tent Between Trees", [ridge, tarp, tarp_mid, body, net] + trunks + crowns + straps + tarp_guys + ground + pack)


# ---------------------------------------------------------------- gear

@design("camping_backpack", T)
def backpack(rng):
    body = chain([(-1.4, 1.0), (-1.4, -2.1)], arc(-0.9, -2.1, 0.5, math.pi, 1.5 * math.pi, 8),
                 arc(0.9, -2.1, 0.5, 1.5 * math.pi, 2 * math.pi, 8), [(1.4, 1.0)])
    lid = chain(cubic((-1.5, 0.9), (-1.6, 2.2), (1.6, 2.2), (1.5, 0.9), 30), [(-1.5, 0.9)])
    pad = [chain([(-1.9, 2.75), (1.9, 2.75)], earc(1.9, 2.3, 0.22, 0.45, math.pi / 2, -math.pi / 2, 12), [(-1.9, 1.85)]),
           ellipse(-1.9, 2.3, 0.22, 0.45, 24), spiral(-1.9, 2.3, 0.05, 0.32, 1.6, 40)]
    pad_straps = [[(-1.0, 1.84), (-1.0, 2.76)], [(1.0, 1.84), (1.0, 2.76)]]
    pocket = rrect(-1.0, -2.3, 1.0, -0.6, 0.35)
    pocket_zip = quad((-0.8, -0.85), (0, -0.75), (0.8, -0.85), 10)
    straps = [rect(-0.8, -0.6, -0.5, 0.9), rect(0.5, -0.6, 0.8, 0.9)]
    buckles = [rect(-0.9, -0.1, -0.4, 0.25), rect(0.4, -0.1, 0.9, 0.25)]
    bottle = [rrect(1.5, -1.9, 2.1, -0.4, 0.2), rect(1.62, -0.4, 1.98, -0.1)]
    mesh = [[(1.4, -1.2), (2.15, -1.2)]]
    biner = [chain(arc(-1.75, -0.15, 0.22, 0, math.pi, 10), [(-1.97, -0.6)], arc(-1.75, -0.6, 0.22, math.pi, 2 * math.pi, 10), [(-1.53, -0.15)])]
    mug = [rrect(-2.3, -1.7, -1.3, -0.9, 0.12), arc(-2.3, -1.3, 0.3, math.pi / 2, 1.5 * math.pi, 10)]
    return make("Loaded Hiking Backpack", [body, lid, pocket, pocket_zip] + pad + pad_straps + straps + buckles + bottle + mesh + biner + mug)


@design("camping_hiking_boot", T)
def hiking_boot(rng):
    lugs = []
    x = 2.0
    while x > -2.3:
        lugs += [(x, -1.8), (x, -1.98), (x - 0.25, -1.98), (x - 0.25, -1.8), (x - 0.4, -1.8)]
        x -= 0.4
    outline = chain([(-2.4, -1.8)], [(2.0, -1.8)], quad((2.0, -1.8), (2.95, -1.75), (2.85, -1.0), 10),
                    cubic((2.85, -1.0), (2.75, -0.4), (1.6, -0.2), (0.8, 0.0), 14), [(-0.2, 1.9)],
                    quad((-0.2, 1.9), (-0.15, 2.4), (-0.6, 2.2), 8), quad((-0.6, 2.2), (-1.3, 1.7), (-2.1, 2.05), 12),
                    cubic((-2.1, 2.05), (-2.3, 1.0), (-2.6, -0.8), (-2.4, -1.8), 16))
    sole = [lugs[::-1][0:1] and chain([(2.0, -1.8)], lugs, [(-2.4, -1.8)])]
    mid = [(-2.47, -1.35), (2.86, -1.35)]
    toe = quad((1.5, -1.35), (1.75, -0.6), (2.82, -0.9), 12)
    heel = quad((-2.48, -0.5), (-1.5, -0.45), (-1.3, -1.35), 12)
    back_edge = [(0.0, -0.15), (-0.95, 1.85)]
    laces = []
    for i in range(5):
        t0, t1 = i / 5, (i + 0.5) / 5
        fx = lambda t: (0.8 - 1.0 * t, 0.0 + 1.9 * t)
        bx = lambda t: (0.0 - 0.95 * t, -0.15 + 2.0 * t)
        laces.append([bx(t0 + 0.05), fx(t1)])
        laces.append([fx(t0 + 0.05), bx(t1)])
    loop = [ellipse(-2.25, 2.25, 0.15, 0.3, 14, rot=0.3)]
    return make("Lace-Up Hiking Boot", [outline, mid, toe, heel, back_edge] + sole + laces + loop)


@design("camping_trekking_poles", T)
def trekking_poles(rng):
    out = []
    for s in (1, -1):
        p0, p1 = (-2.0 * s, -2.8), (1.6 * s, 2.6)
        def at(t):
            return (p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t)
        out.append(tube([at(0.04), at(0.45)], 0.18))
        out.append(tube([at(0.45), at(0.8)], 0.26))
        out.append(tube([at(0.43), at(0.47)], 0.36))
        out.append(tube([at(0.8), at(0.98)], 0.42))
        tip = at(0.0)
        out.append([at(0.04), tip])
        bx, by = at(0.12)
        out.append(ellipse(bx, by, 0.35, 0.12, 20, rot=0.0))
        gx, gy = at(0.98)
        out.append(ellipse(gx - 0.15 * s, gy + 0.3, 0.2, 0.45, 20, rot=-0.5 * s))
    hat = [chain(quad((-1.5, -2.4), (0, -2.8), (1.5, -2.4), 14), quad((1.5, -2.4), (0, -2.0), (-1.5, -2.4), 14)),
           chain([(-0.85, -2.2)], quad((-0.85, -2.2), (-0.8, -1.3), (0, -1.3), 10), quad((0, -1.3), (0.8, -1.3), (0.85, -2.2), 10)),
           quad((-0.86, -1.95), (0, -2.1), (0.86, -1.95), 10)]
    return make("Trekking Poles and Bucket Hat", out + hat)


@design("camping_compass_map", T)
def compass_map(rng):
    top = [(-3.2, 2.2), (-1.1, 2.5), (1.0, 2.2), (3.1, 2.5)]
    bot = [(-3.2, -2.2), (-1.1, -1.9), (1.0, -2.2), (3.1, -1.9)]
    sheet = chain(top, bot[::-1], [top[0]])
    folds = [[top[1], bot[1]], [top[2], bot[2]]]
    contours = [polar(lambda t, k=k: (0.35 + 0.3 * k) * (1 + 0.15 * math.sin(3 * t + k)), cx=-2.2, cy=1.0, n=60) for k in range(3)]
    lake = polar(lambda t: 0.45 * (1 + 0.2 * math.sin(2 * t)), cx=-0.2, cy=-1.1, n=50)
    trail = cubic((-2.9, -1.6), (-1.8, -1.2), (-1.2, 0.0), (-0.4, 0.6), 30)
    xmark = [[(-0.6, 1.2), (-0.2, 1.6)], [(-0.6, 1.6), (-0.2, 1.2)]]
    tent = [poly((0.2, 0.2), (0.5, 0.75), (0.8, 0.2))]
    rot, cx, cy = 0.15, 2.05, 0.15

    def tr(pts):
        return transform(pts, dx=cx, dy=cy, rot=rot)

    plate = tr(rrect(-0.8, -1.6, 0.8, 1.6, 0.25))
    bezel = tr(circle(0, -0.3, 0.68, 50))
    inner = tr(circle(0, -0.3, 0.45, 40))
    needle = tr(poly((0, 0.1), (0.13, -0.3), (0, -0.7), (-0.13, -0.3)))
    arrow = tr(poly((-0.25, 0.75), (0, 1.3), (0.25, 0.75)))
    ticks = [tr([(-0.8, y), (-0.6, y)]) for y in (-1.3, -1.0, -0.7, -0.4, -0.1, 0.2)]
    hole = tr(circle(0.45, 1.1, 0.12, 10))
    return make("Compass on a Trail Map", [sheet, lake, trail, plate, bezel, inner, needle, arrow, hole] + folds + contours + xmark + tent + ticks)


@design("camping_pocket_knife", T)
def pocket_knife(rng):
    body = rrect(-2.2, -0.6, 1.6, 0.6, 0.55)
    cross = poly((-0.6, -0.1), (-0.4, -0.1), (-0.4, -0.3), (-0.2, -0.3), (-0.2, -0.1), (0.0, -0.1), (0.0, 0.1), (-0.2, 0.1),
                 (-0.2, 0.3), (-0.4, 0.3), (-0.4, 0.1), (-0.6, 0.1))
    blade = chain([(0.9, 0.58)], quad((1.6, 1.0), (2.6, 1.6), (3.3, 2.3), 14)[0:1] + [(3.3, 2.3)],
                  quad((3.3, 2.3), (2.2, 1.0), (1.4, 0.45), 14))
    nick = arc(1.65, 1.08, 0.12, -0.6, 2.5, 8)
    small = chain([(-1.5, 0.58)], [(-2.8, 1.5)], quad((-2.8, 1.5), (-2.4, 1.0), (-1.9, 0.6), 10))
    opener = chain([(1.0, -0.58), (2.4, -1.2), (2.65, -1.05), (2.55, -1.45), (2.2, -1.5)], quad((2.2, -1.5), (1.6, -1.0), (1.3, -0.6), 8))
    coil = []
    for i in range(41):
        t = i / 40
        bx, by = -1.6 + (-2.9 + 1.6) * t, -0.75 + (-2.4 + 0.75) * t
        coil.append((bx + 0.22 * math.sin(TAU * 3.5 * t) * 0.79, by - 0.22 * math.sin(TAU * 3.5 * t) * 0.61))
    ring = [circle(-2.55, 0.0, 0.38, 30)]
    return make("Multi-Blade Pocket Knife", [body, cross, blade, nick, small, opener, coil] + ring)


@design("camping_two_burner_stove", T)
def two_burner_stove(rng):
    front = rect(-2.6, -1.6, 2.6, -0.3)
    top = poly((-2.6, -0.3), (-2.2, 0.2), (3.0, 0.2), (2.6, -0.3), closed=False)
    side = poly((2.6, -1.6), (3.0, -1.1), (3.0, 0.2), closed=False)
    lid = poly((-2.2, 0.2), (-2.2, 2.4), (3.0, 2.4), (3.0, 0.2), closed=False)
    knobs = [circle(-1.7, -0.95, 0.28, 20), circle(1.7, -0.95, 0.28, 20), [(-1.7, -0.95), (-1.7, -0.7)], [(1.7, -0.95), (1.7, -0.7)]]
    plate = rrect(-0.8, -1.25, 0.8, -0.65, 0.12)
    pot = [chain([(-2.0, 1.2), (-2.0, 0.25)], quad((-2.0, 0.05), (-1.2, -0.05), (-0.4, 0.05), 8)[0:1], quad((-2.0, 0.05), (-1.2, -0.05), (-0.4, 0.05), 8), [(-0.4, 1.2)]),
           rrect(-2.12, 1.2, -0.28, 1.4, 0.08), rrect(-1.4, 1.4, -1.0, 1.55, 0.06),
           arc(-2.12, 0.85, 0.2, math.pi / 2, 1.5 * math.pi, 8), arc(-0.28, 0.85, 0.2, -math.pi / 2, math.pi / 2, 8)]
    steam = [cubic((x, 1.7), (x - 0.25, 1.95), (x + 0.25, 2.05), (x, 2.3), 12) for x in (-1.6, -0.9)]
    kettle = [chain([(0.6, 0.1), (2.3, 0.1)], quad((2.3, 0.1), (2.3, 1.0), (1.9, 1.2), 10), [(0.95, 1.2)], quad((0.95, 1.2), (0.55, 1.0), (0.6, 0.1), 10)),
              ellipse(1.42, 1.25, 0.5, 0.1, 20), circle(1.42, 1.45, 0.13, 10),
              tube([(0.68, 0.45), (0.25, 0.8), (0.0, 1.2)], lambda t: 0.3 - 0.15 * t),
              arc(1.42, 1.25, 0.75, 0.15, math.pi - 0.15, 20)]
    tank = [chain([(3.15, -1.6), (3.15, -0.6)], quad((3.15, -0.25), (3.4, -0.2), (3.65, -0.25), 6)[0:1], quad((3.15, -0.3), (3.4, -0.15), (3.65, -0.3), 6), [(3.65, -1.6), (3.15, -1.6)]),
            [(3.0, -0.6), (3.15, -0.6)]]
    feet = [rect(-2.5, -1.8, -2.1, -1.6), rect(2.1, -1.8, 2.5, -1.6)]
    return make("Two-Burner Camp Stove", [front, top, side, lid, plate] + knobs + pot + steam + kettle + tank + feet)


@design("camping_percolator", T)
def percolator(rng):
    body = poly((-2.0, 1.0), (-2.4, -2.2), (-0.2, -2.2), (-0.6, 1.0), closed=False)
    lid = chain([(-2.0, 1.0)], quad((-2.05, 1.0), (-1.3, 1.95), (-0.55, 1.0), 16)[1:], [(-2.0, 1.0)])
    knob = circle(-1.3, 1.75, 0.28, 20)
    knob_in = circle(-1.3, 1.75, 0.12, 10)
    spout = tube([(-2.1, -0.6), (-2.6, -0.1), (-2.9, 0.75)], lambda t: 0.45 - 0.2 * t, cap=False)
    handle = tube([(-0.6, 0.6), (0.15, 0.35), (0.15, -1.2), (-0.35, -1.6)], 0.28)
    band = [(-2.27, -1.7), (-0.33, -1.7)]
    mug = [ellipse(1.75, -0.45, 0.95, 0.24, 40), chain([(0.8, -0.45), (0.88, -2.0)], quad((0.88, -2.0), (1.75, -2.35), (2.62, -2.0), 12), [(2.7, -0.45)]),
           ellipse(1.75, -0.48, 0.8, 0.16, 30),
           tube([(2.66, -0.8), (3.3, -0.85), (3.3, -1.6), (2.62, -1.65)], 0.22, cap=False)]
    spots = [circle(x, y, 0.13, 10) for x, y in [(1.2, -1.1), (2.1, -1.4), (1.6, -1.8), (2.3, -0.9)]]
    steam = [cubic((x, -0.2), (x - 0.3, 0.3), (x + 0.3, 0.6), (x, 1.1), 16) for x in (1.35, 2.05)]
    ground = [(-3.2, -2.2), (3.4, -2.2)]
    return make("Camp Percolator and Enamel Mug", [body, lid, knob, knob_in, spout, handle, band, ground] + mug + spots + steam)


# dropped: the subject repeats another book
def skillet_breakfast(rng):
    pan = [ellipse(-0.4, 0.4, 2.1, 1.25, 80), ellipse(-0.4, 0.45, 1.8, 1.0, 70)]
    handle = [tube([(1.6, 0.75), (3.3, 1.5)], 0.42), circle(3.0, 1.37, 0.1, 10)]
    whites = [polar(lambda t: 0.62 * (1 + 0.12 * math.sin(4 * t) + 0.06 * math.cos(7 * t)), cx=cx, cy=cy, n=60) for cx, cy in [(-1.2, 0.6), (0.2, 0.75)]]
    yolks = [circle(-1.15, 0.6, 0.25, 20), circle(0.25, 0.75, 0.25, 20)]
    bacon = [tube(wave(-1.4, 0.4, 0.0, 0.1, 2, 30), 0.3), tube(wave(-1.2, 0.6, -0.45, 0.1, 2, 30), 0.3)]
    grate = [[(-3.2, -1.0), (3.2, -1.0)], [(-3.0, -1.0), (-3.0, -2.6)], [(3.0, -1.0), (3.0, -2.6)]]
    fire = flame_group(-0.5, -2.2, 0.75)
    logs = crossed_logs(-0.5, -2.45, 0.9)
    return make("Skillet Breakfast over the Fire", pan + whites + yolks + bacon + grate + fire + logs + [handle[0], handle[1]])


@design("camping_dutch_oven", T)
def dutch_oven(rng):
    body = chain([(-2.0, 0.3), (-2.0, -0.9)], quad((-2.0, -0.9), (0, -1.9), (2.0, -0.9), 20), [(2.0, 0.3)])
    rim = ellipse(0, 0.35, 2.15, 0.35, 60)
    lid_lip = earc(0, 0.6, 2.0, 0.3, math.pi, 0, 30)
    lid_top = ellipse(0, 0.6, 2.0, 0.3, 60)
    loop = arc(0, 0.65, 0.3, 0, math.pi, 10)
    coals = [stone(x, y, 0.3, 0.17) for x, y in [(-1.2, 0.6), (1.1, 0.55), (-0.5, 0.75), (0.6, 0.78)]]
    bail = earc(0, 0.0, 2.15, 1.5, 0.05, math.pi - 0.05, 40)
    ears = [circle(-2.15, 0.0, 0.12, 10), circle(2.15, 0.0, 0.12, 10)]
    legs = [rect(-1.3, -2.05, -1.0, -1.5), rect(1.0, -2.05, 1.3, -1.5), rect(-0.15, -2.15, 0.15, -1.75)]
    bed = [stone(x, y, rx, 0.22) for x, y, rx in [(-2.6, -2.25, 0.4), (-1.8, -2.4, 0.4), (-0.75, -2.45, 0.45), (0.55, -2.45, 0.45), (1.65, -2.4, 0.4), (2.55, -2.25, 0.4)]]
    heat = [cubic((x, 1.0), (x - 0.25, 1.35), (x + 0.25, 1.6), (x, 2.0), 12) for x in (-0.9, 0.0, 0.9)]
    return make("Dutch Oven on Hot Coals", [body, rim, lid_lip, lid_top, loop, bail] + coals + ears + legs + bed + heat)


@design("camping_tripod_pot", T)
def tripod_pot(rng):
    legs = [[(-2.6, -2.5), (0.3, 2.95)], [(2.6, -2.5), (-0.3, 2.95)]]
    lash = zigzag(-0.25, 0.25, 2.4, 0.12, 3)
    chain_ = [(0, 2.3), (0, 1.25)]
    hook = arc(0, 1.1, 0.15, math.pi / 2, -math.pi, 10)
    rim = ellipse(0, 0.0, 1.15, 0.28, 50)
    body = chain([(-1.15, 0.0)], cubic((-1.15, -0.8), (-0.9, -1.25), (0.9, -1.25), (1.15, 0.0), 30)[1:-1], [(1.15, 0.0)])
    bail = earc(0, 0.0, 1.15, 0.95, 0.0, math.pi, 30)
    steam = [cubic((x, 0.4), (x - 0.25, 0.6), (x + 0.25, 0.7), (x, 0.95), 10) for x in (-0.5, 0.5)]
    fire = flame_group(0, -2.2, 0.6)
    ring = [stone(x, -2.45, 0.38, 0.24) for x in (-2.0, -1.2, -0.4, 0.4, 1.2, 2.0)]
    return make("Cooking Pot on a Tripod", [lash, chain_, hook, rim, body, bail] + legs + steam + fire + ring)


@design("camping_propane_lantern", T)
def propane_lantern(rng):
    tank = chain([(-0.35, -0.4)], quad((-0.35, -0.4), (-0.8, -0.45), (-0.8, -0.95), 8),
                 [(-0.8, -2.8), (0.8, -2.8), (0.8, -0.95)], quad((0.8, -0.95), (0.8, -0.45), (0.35, -0.4), 8))
    bands = [[(-0.8, -2.5), (0.8, -2.5)], [(-0.8, -1.1), (0.8, -1.1)]]
    base = rrect(-1.1, -0.4, 1.1, 0.05, 0.12)
    knob = [circle(1.45, -0.18, 0.25, 16), [(1.1, -0.18), (1.2, -0.18)]]
    glass = chain(cubic((-0.9, 0.05), (-1.4, 0.8), (-1.4, 1.6), (-0.95, 2.2), 20), [(0.95, 2.2)], cubic((0.95, 2.2), (1.4, 1.6), (1.4, 0.8), (0.9, 0.05), 20))
    mantles = [lens((-0.45, 1.6), (-0.45, 0.65), 0.28), lens((0.45, 1.6), (0.45, 0.65), 0.28)]
    tubes_ = [[(-0.45, 1.6), (-0.45, 1.85), (0.45, 1.85), (0.45, 1.6)], [(0, 1.85), (0, 0.05)]]
    cap = chain([(-1.25, 2.2)], earc(0, 2.2, 1.25, 0.55, math.pi, 0, 30), [(-1.25, 2.2)])
    vents = [ellipse(x, 2.45, 0.15, 0.08, 10) for x in (-0.6, 0.0, 0.6)]
    nut = rect(-0.2, 2.75, 0.2, 2.95)
    bail = quad((-1.15, 2.35), (0, 4.6), (1.15, 2.35), 30)
    branch = [tube(cubic((-3.2, 3.3), (-1.5, 3.7), (1.0, 3.5), (3.2, 3.9), 30), 0.35), quad((1.6, 3.75), (2.1, 4.3), (2.6, 4.4), 10)]
    return make("Propane Lantern Hanging from a Branch", [tank, base, glass, cap, nut, bail] + bands + knob + mantles + tubes_ + vents + branch)


@design("camping_flashlight", T)
def flashlight(rng):
    a = math.radians(45)
    def tr(pts):
        return transform(pts, dx=-1.9, dy=-1.9, rot=a)
    body = tr(rrect(-1.4, -0.32, 1.0, 0.32, 0.12))
    head = tr(poly((1.0, -0.32), (1.7, -0.6), (1.7, 0.6), (1.0, 0.32), closed=False))
    lens_ = tr(ellipse(1.7, 0.0, 0.15, 0.6, 24))
    rings = [tr([(x, -0.32), (x, 0.32)]) for x in (-1.0, -0.7, -0.4)]
    button = tr(rrect(0.2, 0.32, 0.6, 0.48, 0.06))
    loop = tr(arc(-1.4, 0.0, 0.3, math.pi / 2, 1.5 * math.pi, 10))
    beam = [tr([(1.75, 0.65), (5.6, 2.4)]), tr([(1.75, -0.65), (5.6, -2.4)]), tr(earc(5.6, 0.0, 0.6, 2.4, -math.pi / 2, math.pi / 2, 30))]
    moth = [lens((1.1, 1.0), (1.8, 1.6), 0.3), lens((1.1, 1.0), (1.85, 0.5), 0.3), ellipse(1.1, 1.0, 0.1, 0.22, 10, rot=0.6)]
    sky = stars([(-2.3, 2.6, 0.25), (-0.8, 2.9, 0.18), (2.8, -1.6, 0.22), (-2.9, 0.4, 0.17), (1.6, -2.8, 0.17)])
    return make("Flashlight Beam at Night", [body, head, lens_, button, loop] + rings + beam + moth + sky)


@design("camping_headlamp", T)
def headlamp(rng):
    gap = math.asin(0.95 / 2.4)
    band = [earc(0, 0.0, 2.4, 1.0, -math.pi / 2 + gap, 1.5 * math.pi - gap, 70),
            earc(0, 0.0, 2.05, 0.7, -math.pi / 2 + math.asin(0.95 / 2.05), 1.5 * math.pi - math.asin(0.95 / 2.05), 60)]
    strap = tube(earc(0, 0.2, 2.2, 2.3, 0.08, math.pi - 0.08, 40), 0.32, cap=False)
    housing = rrect(-0.95, -1.7, 0.95, -0.35, 0.35)
    lens_ = [circle(0, -1.02, 0.45, 30), circle(0, -1.02, 0.25, 20)]
    button = rrect(-0.3, -0.35, 0.3, -0.18, 0.06)
    battery = rrect(-0.6, 0.6, 0.6, 1.35, 0.15)
    rays = [[(0.6 * math.cos(t), -1.02 + 0.6 * math.sin(t)), (1.3 * math.cos(t), -1.02 + 1.3 * math.sin(t))] for t in (-2.4, -2.0, -1.57, -1.14, -0.74)]
    return make("Headlamp", band + [strap, housing, button, battery] + lens_ + rays)


@design("camping_mummy_sleeping_bag", T)
def mummy_bag(rng):
    def w(y):
        return 0.75 + (y + 2.7) / 3.9 * 0.65

    left = [(-w(y), y) for y in [1.2 - 3.9 * i / 30 for i in range(31)]]
    right = [(w(y), y) for y in [-2.7 + 3.9 * i / 30 for i in range(31)]]
    outline = chain(left, arc(0, -2.7, 0.75, math.pi, 2 * math.pi, 16), right,
                    cubic((1.4, 1.2), (1.5, 2.4), (0.8, 2.95), (0, 2.95), 16), cubic((0, 2.95), (-0.8, 2.95), (-1.5, 2.4), (-1.4, 1.2), 16))
    face = ellipse(0, 1.85, 0.62, 0.48, 40)
    hood_ring = ellipse(0, 1.85, 0.92, 0.75, 50)
    baffles = [quad((-w(y), y), (0, y - 0.25), (w(y), y), 16) for y in (-2.1, -1.5, -0.9, -0.3, 0.3)]
    zip_ = [(0.55, 1.15), (0.85, -0.6)]
    pull = rrect(0.78, -0.95, 1.0, -0.6, 0.06)
    cords = [[(-0.3, 1.1), (-0.4, 0.75)], [(0.3, 1.1), (0.4, 0.75)], circle(-0.42, 0.62, 0.13, 10), circle(0.42, 0.62, 0.13, 10)]
    return make("Mummy Sleeping Bag", [outline, face, hood_ring, zip_, pull] + baffles + cords)


@design("camping_folding_chair", T)
def folding_chair(rng):
    back_posts = [[(-1.35, 2.6), (-1.35, -2.0)], [(1.35, 2.6), (1.35, -2.0)]]
    front_legs = [[(-1.8, 0.6), (-1.8, -2.4)], [(1.8, 0.6), (1.8, -2.4)]]
    backrest = chain(quad((-1.35, 2.35), (0, 2.05), (1.35, 2.35), 14), [(1.35, 0.0)], quad((1.35, 0.0), (0, -0.35), (-1.35, 0.0), 14), [(-1.35, 2.35)])
    seat = quad((-1.8, -0.35), (0, -0.9), (1.8, -0.35), 16)
    x_front = [[(-1.8, -0.6), (1.8, -2.2)], [(1.8, -0.6), (-1.8, -2.2)]]
    arms = [rrect(-2.05, 0.6, -1.25, 0.85, 0.1), rrect(1.25, 0.6, 2.05, 0.85, 0.1)]
    cup = [poly((2.05, 0.75), (2.75, 0.75), (2.6, 0.1), (2.2, 0.1)), ellipse(2.4, 1.05, 0.25, 0.08, 14), [(2.15, 0.75), (2.15, 1.05)], [(2.65, 0.75), (2.65, 1.05)]]
    feet = [ellipse(x, -2.45, 0.2, 0.07, 10) for x in (-1.8, 1.8)] + [ellipse(x, -2.05, 0.18, 0.06, 10) for x in (-1.35, 1.35)]
    pocket = [rrect(-0.8, 0.4, 0.8, 1.2, 0.15)]
    return make("Folding Camp Chair", back_posts + front_legs + [backrest, seat] + x_front + arms + cup + feet + pocket)


@design("camping_trail_signpost", T)
def trail_signpost(rng):
    post = [[(-0.25, 1.65), (-0.25, 2.3), (0, 2.55), (0.25, 2.3), (0.25, 1.65)],
            [(-0.25, 0.6), (-0.25, 0.85)], [(0.25, 0.6), (0.25, 0.85)],
            [(-0.25, -0.45), (-0.25, -0.2)], [(0.25, -0.45), (0.25, -0.2)],
            [(-0.25, -1.25), (-0.25, -2.4)], [(0.25, -1.25), (0.25, -2.4)]]
    b1 = poly((-0.6, 0.85), (2.5, 0.85), (3.0, 1.25), (2.5, 1.65), (-0.6, 1.65))
    b2 = poly((0.6, -0.2), (-2.5, -0.2), (-3.0, 0.2), (-2.5, 0.6), (0.6, 0.6))
    b3 = poly((-0.6, -1.25), (2.1, -1.25), (2.6, -0.85), (2.1, -0.45), (-0.6, -0.45))
    tent = poly((1.2, 1.0), (1.55, 1.5), (1.9, 1.0))
    mtn = poly((-2.2, -0.05), (-1.8, 0.45), (-1.55, 0.2), (-1.3, 0.45), (-0.9, -0.05), closed=False)
    water = wave(0.8, 1.8, -0.85, 0.1, 2, 30)
    nails = [circle(x, y, 0.07, 8) for x, y in [(0.0, 1.25), (0.0, 0.2), (0.0, -0.85)]]
    ground = [(-3.0, -2.4), (3.0, -2.4)]
    rocks = [stone(-0.9, -2.15, 0.45, 0.25), stone(0.9, -2.2, 0.35, 0.2)]
    tufts = [grass(-2.2, -2.4), grass(1.9, -2.4), grass(-1.6, -2.4, 0.2)]
    return make("Trail Signpost with Arrows", post + [b1, b2, b3, tent, mtn, water, ground] + nails + rocks + tufts)


# ---------------------------------------------------------------- scenery

@design("camping_mountain_pines", T)
def mountain_pines(rng):
    ridge = [(-3.5, -0.5), (-1.6, 2.2), (-0.6, 1.0), (0.2, 1.6), (1.6, 2.8), (3.5, -0.3)]
    snow = [poly((-2.2, 1.35), (-1.9, 1.15), (-1.7, 1.4), (-1.45, 1.1), (-1.2, 1.4), (-1.05, 1.35), closed=False),
            poly((0.95, 2.05), (1.2, 1.8), (1.45, 2.05), (1.7, 1.75), (2.0, 2.0), (2.15, 2.15), closed=False)]
    trees = [pine(x, -2.8, h, h * 0.45) for x, h in [(-3.0, 2.6), (-2.2, 2.0), (2.3, 2.2), (3.1, 2.8)]]
    trail = [cubic((-1.1, -2.8), (-0.4, -1.8), (0.6, -1.3), (0.2, -0.5), 24), cubic((1.1, -2.8), (0.6, -1.9), (1.0, -1.2), (0.35, -0.5), 24)]
    ground = [[(-3.6, -2.8), (3.6, -2.8)]]
    birds = [chain(arc(x - 0.15, y, 0.15, 0.3, math.pi - 0.3, 6), arc(x + 0.15, y, 0.15, 0.3, math.pi - 0.3, 6)[::-1]) for x, y in [(-0.4, 2.6), (0.2, 2.9)]]
    return make("Mountain Peaks and Pine Forest", [ridge] + snow + trees + trail + ground + birds)


@design("camping_waterfall", T)
def waterfall(rng):
    left = [(-3.5, 2.3), (-2.4, 2.4), (-1.6, 2.0), (-0.85, 2.0), (-0.95, 1.0), (-1.1, 0.2), (-0.9, -0.6), (-1.2, -1.2), (-3.5, -1.0)]
    right = [(3.5, 2.6), (2.2, 2.5), (1.4, 2.1), (0.85, 2.0), (0.95, 0.9), (1.15, 0.1), (0.95, -0.7), (1.3, -1.2), (3.5, -1.1)]
    river = [quad((-0.85, 2.0), (-0.6, 2.6), (-1.0, 3.1), 10), quad((0.85, 2.0), (0.7, 2.6), (1.0, 3.1), 10)]
    lines = []
    for x in (-0.5, -0.1, 0.3, 0.65):
        lines.append([(x + 0.06 * math.sin(3 * y), y) for y in [2.0 - 3.1 * i / 30 for i in range(31)]])
    splash = chain(arc(-0.75, -1.2, 0.35, 0.2, math.pi, 8), arc(-0.15, -1.15, 0.35, 0.3, math.pi - 0.3, 8)[::-1][::-1],
                   arc(0.45, -1.2, 0.4, 0, math.pi - 0.2, 8)[::-1][::-1])
    pool = ellipse(0, -1.95, 3.0, 0.75, 80)
    ripples = [earc(0, -1.95, 2.0, 0.42, math.pi + 0.3, TAU - 0.3, 30), earc(0, -1.95, 1.0, 0.2, math.pi + 0.2, TAU - 0.2, 20)]
    rocks = [stone(-2.3, -1.6, 0.5, 0.3), stone(2.2, -2.1, 0.45, 0.28)]
    trees = [pine(-2.8, 2.36, 1.1, 0.6), pine(2.8, 2.55, 0.9, 0.5), pine(-1.9, 2.25, 0.8, 0.45)]
    return make("Forest Waterfall", [left, right, splash, pool] + river + lines + ripples + rocks + trees)


@design("camping_rope_bridge", T)
def rope_bridge(rng):
    lc = [(-3.6, 0.6), (-2.4, 0.6), (-2.2, -0.3), (-2.6, -1.0), (-2.1, -1.8), (-2.5, -2.8)]
    rc = [(3.6, 0.6), (2.4, 0.6), (2.3, -0.4), (2.6, -1.2), (2.1, -2.0), (2.4, -2.8)]

    def sag(x, y0, d):
        return y0 - d * (1 - (x / 2.4) ** 2)

    xs = [-2.4 + 4.8 * i / 40 for i in range(41)]
    deck_top = [(x, sag(x, 0.6, 1.0)) for x in xs]
    deck_bot = [(x, sag(x, 0.6, 1.0) - 0.25) for x in xs]
    rail = [(x, sag(x, 2.0, 0.9)) for x in xs]
    planks = [[(x, sag(x, 0.6, 1.0)), (x, sag(x, 0.6, 1.0) - 0.25)] for x in [-2.4 + 0.4 * k for k in range(1, 12)]]
    hangers = [[(x, sag(x, 2.0, 0.9)), (x, sag(x, 0.6, 1.0))] for x in (-1.6, -0.8, 0.0, 0.8, 1.6)]
    posts = [rect(-2.6, 0.6, -2.3, 2.15), rect(2.3, 0.6, 2.6, 2.15)]
    river = [wave(-2.3, 2.2, -2.5, 0.1, 3, 40), wave(-1.6, 1.6, -2.15, 0.08, 2, 30)]
    trees = [pine(-3.1, 0.6, 1.7, 0.8), pine(3.15, 0.6, 1.5, 0.7)]
    return make("Rope Bridge over a Gorge", [lc, rc, deck_top, deck_bot, rail] + planks + hangers + posts + river + trees)


@design("camping_lean_to", T)
def lean_to(rng):
    gy = -1.8
    beam = log_end((-2.8, 1.65), (1.05, 1.65), 0.4)
    post = rect(-2.6, gy, -2.3, 1.45)
    side = poly((0.85, 1.45), (3.1, 0.3), (3.1, -1.25), (0.85, gy), closed=False)
    side_logs = []
    for k in range(1, 7):
        t = k / 7
        y0 = gy + (1.45 - gy) * t
        y1 = -1.25 + (0.3 + 1.25) * t
        side_logs.append([(1.05, y0 + 0.05 * (1 - t)), (3.1, y1)])
    ends = [circle(0.95, gy + (1.45 - gy) * k / 7, 0.16, 12) for k in range(1, 7)]
    back = [[(-2.3, 0.0), (0.85, 0.0)]] + [[(-2.3, y), (0.85, y)] for y in (-0.45, -0.9, -1.35)]
    rafters = [[(-2.3, 1.45), (-1.9, 0.0)], [(-0.7, 1.45), (-0.5, 0.0)], [(0.85, 1.45), (0.85, 1.45)]]
    ground = [(-3.4, gy), (3.6, gy)]
    ring = [stone(x, -2.55, 0.32, 0.2) for x in (-1.6, -0.9, -0.2, 0.5)]
    fire = [flame(-0.55, -2.4, 0.5, 0.75)]
    trees = [pine(-3.2, gy, 2.6, 0.9)]
    return make("Log Lean-To Shelter", [post, side, ground] + beam + side_logs + ends + back + rafters[:2] + ring + fire + trees)


@design("camping_ranger_station", T)
def ranger_station(rng):
    gy = -2.0
    walls = rect(-2.3, gy, 1.7, 0.3)
    roof = poly((-2.7, 0.3), (2.1, 0.3), (1.5, 1.6), (-2.1, 1.6))
    eave = [(-2.7, 0.3), (-2.7, 0.15), (2.1, 0.15), (2.1, 0.3)]
    door = [rect(-0.5, gy, 0.3, -0.5), circle(0.15, -1.25, 0.06, 8)]
    wins = []
    for x0 in (-1.9, 0.75):
        wins += [rect(x0, -1.2, x0 + 0.75, -0.35), [(x0 + 0.375, -1.2), (x0 + 0.375, -0.35)], [(x0, -0.775), (x0 + 0.75, -0.775)]]
    sign = [rect(-0.9, 0.55, 0.7, 1.25), poly((-0.6, 0.7), (-0.25, 1.1), (0.0, 0.85), (0.2, 1.05), (0.45, 0.7), closed=False)]
    chimney = rect(-1.8, 1.6, -1.3, 2.3)
    steps = [rect(-0.7, gy - 0.25, 0.5, gy), rect(-0.9, gy - 0.5, 0.7, gy - 0.25)]
    pole = [[(2.6, gy), (2.6, 2.9)], circle(2.6, 3.0, 0.1, 8)]
    flag = [chain([(2.6, 2.85)], wave(2.6, 3.6, 2.6, 0.08, 1.5, 20)[1:], [(3.6, 2.0)], wave(2.6, 3.6, 2.0, 0.08, 1.5, 20)[::-1], [(2.6, 2.85)])]
    flag = [chain([(2.6, 2.85)], [(x, y + 0.25) for x, y in wave(2.6, 3.6, 2.6, 0.08, 1.5, 20)][1:], [(3.6, 2.15)],
                  [(x, y - 0.45) for x, y in wave(2.6, 3.6, 2.6, 0.08, 1.5, 20)][::-1])]
    trees = [pine(-3.1, gy, 2.8, 1.0), pine(3.3, gy, 1.6, 0.7)]
    ground = [(-3.6, gy - 0.5), (3.6, gy - 0.5)]
    return make("Ranger Station", [walls, roof, eave, chimney, ground] + door + wins + sign + steps + pole + flag + trees)


@design("camping_lookout_tower", T)
def lookout_tower(rng):
    levels = [-2.8, -1.6, -0.4, 0.8]

    def hw(y):
        return 1.8 - (y + 2.8) / 3.6 * 0.9

    legs = [[(-hw(-2.8), -2.8), (-hw(0.8), 0.8)], [(hw(-2.8), -2.8), (hw(0.8), 0.8)]]
    braces = []
    for a, b in zip(levels[:-1], levels[1:]):
        braces += [[(-hw(a), a), (hw(b), b)], [(hw(a), a), (-hw(b), b)], [(-hw(b), b), (hw(b), b)]]
    deck = rect(-1.6, 0.8, 1.6, 1.0)
    cabin = rect(-1.2, 1.0, 1.2, 2.1)
    wins = [] + [rect(-1.0, 1.35, -0.15, 1.95), rect(0.15, 1.35, 1.0, 1.95)]
    rail = [[(-1.6, 1.0), (-1.6, 1.3), (-1.2, 1.3)], [(1.6, 1.0), (1.6, 1.3), (1.2, 1.3)]]
    roof = poly((-1.55, 2.1), (0, 2.85), (1.55, 2.1))
    rod = [(0, 2.85), (0, 3.3)]
    trees = [pine(-3.0, -2.8, 2.2, 0.9), pine(3.0, -2.8, 2.6, 1.0), pine(-2.2, -2.8, 1.4, 0.6)]
    ground = [(-3.6, -2.8), (3.6, -2.8)]
    return make("Fire Lookout Tower", legs + braces + [deck, cabin, roof, rod, ground] + wins + rail + trees)


@design("camping_binoculars", T)
def binoculars(rng):
    out = []
    for s in (-1, 1):
        cx = 1.25 * s
        out.append(chain([(cx - 0.95, -1.4), (cx - 0.65, 1.3), (cx + 0.65, 1.3), (cx + 0.95, -1.4)]))
        out.append(circle(cx, -1.6, 1.0, 60))
        out.append(circle(cx, -1.6, 0.72, 50))
        out.append(rrect(cx - 0.5, 1.3, cx + 0.5, 2.1, 0.15))
        out.append([(cx - 0.5, 1.6), (cx + 0.5, 1.6)])
        out.append(arc(cx - 0.25, -1.35, 0.3, 1.8, 2.8, 8))
    bridge = rrect(-0.35, 0.2, 0.35, 1.2, 0.12)
    wheel = [ellipse(0, 1.45, 0.35, 0.18, 20)]
    strap = [cubic((-2.2, -0.2), (-3.2, 0.3), (-3.3, -2.2), (-2.6, -2.9), 30), cubic((2.2, -0.2), (3.2, 0.3), (3.3, -2.2), (2.6, -2.9), 30),
             quad((-2.6, -2.9), (0, -3.6), (2.6, -2.9), 20)]
    return make("Pair of Binoculars", out + [bridge] + wheel + strap)


def bear_print(cx, cy, s, rot=0.0):
    pad = chain(cubic((-0.6, 0.0), (-0.7, -0.7), (0.7, -0.7), (0.6, 0.0), 16), quad((0.6, 0.0), (0.0, 0.35), (-0.6, 0.0), 10))
    toes = [ellipse(x, y, 0.15, 0.2, 14) for x, y in [(-0.62, 0.42), (-0.32, 0.62), (0.0, 0.7), (0.32, 0.62), (0.62, 0.42)]]
    claws = [[(x, y + 0.24), (x * 1.15, y + 0.45)] for x, y in [(-0.62, 0.42), (-0.32, 0.62), (0.0, 0.7), (0.32, 0.62), (0.62, 0.42)]]
    return [transform(p, dx=cx, dy=cy, s=s, rot=rot) for p in [pad] + toes + claws]


@design("camping_bear_canister", T)
def bear_canister(rng):
    top = ellipse(-0.6, 1.2, 1.3, 0.35, 50)
    lid = ellipse(-0.6, 1.2, 0.8, 0.2, 40)
    slots = [[(-1.0, 1.2), (-0.2, 1.2)]]
    body = chain([(-1.9, 1.2), (-1.9, -1.8)], earc(-0.6, -1.8, 1.3, 0.35, math.pi, TAU, 30), [(0.7, 1.2)])
    ridges = [earc(-0.6, y, 1.3, 0.35, math.pi, TAU, 30) for y in (0.6, -0.6)]
    grips = [rect(-1.0, -0.2, -0.2, 0.2)]
    prints = bear_print(1.9, -1.8, 0.75, 0.3) + bear_print(2.1, 1.0, 0.65, 0.1)
    ground = [(-3.0, -2.4), (0.6, -2.4)]
    return make("Bear Canister and Paw Prints", [top, lid, body] + slots + ridges + grips + prints + [ground])


# dropped: the subject repeats another book
def big_dipper(rng):
    pts = [(-2.8, 2.6), (-1.9, 2.2), (-1.1, 1.9), (-0.3, 1.5), (-0.2, 0.7), (1.0, 0.6), (1.2, 1.5)]
    sts = stars([(x, y, 0.22) for x, y in pts])
    lines = []
    for a, b in list(zip(pts, pts[1:])) + [(pts[6], pts[3])]:
        d = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
        lines.append([(a[0] + 0.3 * ux, a[1] + 0.3 * uy), (b[0] - 0.3 * ux, b[1] - 0.3 * uy)])
    moon = [crescent(2.5, 2.4, 0.6, 0.38)]
    hill = cubic((-3.6, -1.6), (-1.0, -0.6), (1.0, -1.6), (3.6, -1.0), 50)
    tents = [poly((-2.4, -1.15), (-1.6, 0.0), (-0.8, -1.15), closed=False), [(-1.6, 0.0), (-1.6, -1.15)],
             poly((0.4, -1.2), (1.1, -0.2), (1.8, -1.2), closed=False), [(1.1, -0.2), (1.1, -1.2)]]
    trees = [pine(-3.1, -1.3, 1.6, 0.7), pine(2.9, -1.1, 1.8, 0.8)]
    fire = flame_group(-0.35, -2.1, 0.45) + crossed_logs(-0.35, -2.3, 0.45)
    extra = stars([(2.0, 1.2, 0.15), (-2.9, 0.8, 0.15), (0.3, 2.8, 0.15)])
    return make("Big Dipper over the Campsite", sts + lines + moon + [hill] + tents + trees + fire + extra)


@design("camping_sunrise_lake", T)
def sunrise_lake(rng):
    hz = -0.3
    sun = arc(0, hz, 1.1, 0, math.pi, 40)
    rays = [[(1.4 * math.cos(a), hz + 1.4 * math.sin(a)), (2.0 * math.cos(a), hz + 2.0 * math.sin(a))] for a in [math.pi * k / 8 for k in range(1, 8)]]
    mtnL = [(-3.5, hz), (-2.6, 1.0), (-2.0, 0.4), (-1.4, 0.9), (-1.0, hz)]
    mtnR = [(1.0, hz), (1.8, 1.2), (2.3, 0.6), (2.9, 1.5), (3.5, hz)]
    shore = [[(-3.5, hz), (-1.0, hz)], [(1.0, hz), (3.5, hz)], [(-1.0, hz), (1.0, hz)]]
    refl = [[(-w, y), (w, y)] for w, y in [(1.0, -0.6), (0.7, -0.9), (0.85, -1.2), (0.45, -1.5), (0.6, -1.8)]]
    trees = [pine(-3.0, -2.8, 2.4, 0.9), pine(-2.2, -2.8, 1.7, 0.7), pine(2.6, -2.8, 2.2, 0.85)]
    bank = [cubic((-3.6, -2.8), (-1.0, -2.3), (1.0, -2.5), (3.6, -2.8), 30)]
    return make("Sunrise over a Mountain Lake", [sun, mtnL, mtnR] + rays + shore + refl + trees + bank)


# ---------------------------------------------------------------- activities

@design("camping_rock_climber", T)
def rock_climber(rng):
    cliff = [(-1.6, -3.0), (-1.3, -1.8), (-1.8, -0.6), (-1.2, 0.6), (-1.6, 1.8), (-1.1, 3.0)]
    cracks = [poly((2.0, 2.6), (1.7, 1.6), (2.1, 0.8), closed=False), poly((-0.4, -1.0), (-0.1, -2.0), (-0.5, -2.8), closed=False)]
    head = circle(0.6, 1.5, 0.35, 30)
    helmet = [(0.25, 1.58), (0.95, 1.58)]
    torso = tube([(0.6, 1.05), (0.45, -0.15)], 0.6)
    arms = [tube([(0.8, 0.9), (1.2, 1.6), (1.4, 2.3)], 0.24), tube([(0.35, 0.9), (-0.1, 1.4), (-0.25, 2.0)], 0.24)]
    legs = [tube([(0.6, -0.2), (1.3, -0.55), (1.15, -1.45)], 0.3), tube([(0.3, -0.2), (-0.25, -0.9), (0.05, -1.6)], 0.3)]
    holds = [stone(1.45, 2.45, 0.22, 0.14), stone(-0.3, 2.15, 0.2, 0.13), stone(1.25, -1.62, 0.26, 0.14), stone(0.1, -1.78, 0.24, 0.13)]
    harness = ellipse(0.45, -0.15, 0.36, 0.14, 20)
    rope = cubic((0.45, -0.3), (0.2, -1.2), (-0.6, -1.0), (-0.8, -2.0), 24)
    draw = [rrect(-0.95, -2.3, -0.65, -1.95, 0.1)]
    rope2 = cubic((-0.8, -2.3), (-0.8, -2.6), (-1.2, -2.7), (-1.4, -3.0), 10)
    bolts = [circle(1.9, -0.6, 0.12, 8), circle(-0.9, 1.0, 0.12, 8)]
    sun = [circle(-2.7, 2.3, 0.5, 30)]
    birds = [chain(arc(-2.65, 0.8, 0.15, 0.3, math.pi - 0.3, 6), arc(-2.35, 0.8, 0.15, 0.3, math.pi - 0.3, 6)[::-1])]
    return make("Rock Climber on the Cliff", [cliff, head, helmet, torso, harness, rope, rope2] + cracks + arms + legs + holds + draw + bolts + sun + birds,
                [eye(0.75, 1.42, 0.06)])


@design("camping_rope_carabiners", T)
def rope_carabiners(rng):
    cx, cy = -1.0, 0.4
    centre = chain(spiral(cx, cy, 0.6, 2.2, 3.5, 320), cubic((cx - 2.2, cy), (cx - 2.2, cy - 1.2), (cx - 1.4, cy - 2.4), (cx + 0.2, cy - 2.9), 24))
    rope = tube(centre, 0.24)
    whip = [[(cx + 0.0, cy - 2.95), (cx - 0.06, cy - 2.6)]]

    def biner(bx, by, s, rot):
        def shape(o):
            return chain(arc(0.1, 0.8, 0.62 - o, 0.0, math.pi, 16), [(-0.52 + o, -0.6)], arc(-0.05, -0.6, 0.47 - o, math.pi, TAU, 12), [(0.72 - o, 0.8)])
        gate = [[(0.48, 0.55), (0.72, 0.55)], [(0.3, -0.45), (0.5, -0.4)]]
        return [transform(p, dx=bx, dy=by, s=s, rot=rot) for p in [shape(0.0), shape(0.2)] + gate]

    biners = biner(2.3, 1.2, 1.25, -0.2) + biner(2.4, -1.6, 1.25, 0.3)
    return make("Climbing Rope and Carabiners", [rope] + whip + biners)


@design("camping_mountain_bike", T)
def mountain_bike(rng):
    wy = -1.0
    out = []
    for cx in (-1.9, 1.9):
        knobs = 22
        pts = []
        for k in range(knobs):
            a0 = TAU * k / knobs
            pts += arc(cx, wy, 1.15, a0, a0 + TAU / knobs * 0.6, 3) + arc(cx, wy, 1.03, a0 + TAU / knobs * 0.6, a0 + TAU / knobs, 3)
        pts.append(pts[0])
        out += [pts, circle(cx, wy, 0.78, 40), circle(cx, wy, 0.14, 10)]
        out += [[(cx + 0.14 * math.cos(a), wy + 0.14 * math.sin(a)), (cx + 0.78 * math.cos(a), wy + 0.78 * math.sin(a))] for a in [k * TAU / 6 for k in range(6)]]
    bb, seat, ht, hb = (-0.1, -1.05), (-0.6, 0.55), (1.0, 0.75), (1.15, 0.3)
    out += [tube([seat, ht], 0.22), tube([bb, hb], 0.28), tube([bb, seat], 0.2)]
    out += [[bb, (-1.9, wy)], [seat, (-1.9, wy)]]
    out += [tube([(1.12, 0.35), (1.55, -0.4)], 0.26), [(1.55, -0.4), (1.9, wy)], [(1.45, -0.35), (1.8, wy)]]
    out += [[ht, (1.1, 1.3)], [(0.75, 1.3), (1.45, 1.45)], rrect(1.4, 1.35, 1.75, 1.55, 0.08)]
    out += [[seat, (-0.72, 1.05)], chain(quad((-1.2, 1.1), (-0.7, 1.35), (-0.25, 1.15), 10), quad((-0.25, 1.15), (-0.7, 1.0), (-1.2, 1.1), 10))]
    out += [circle(bb[0], bb[1], 0.35, 24), [bb, (0.25, -1.6)], rrect(0.1, -1.72, 0.55, -1.58, 0.05)]
    out += [cubic((-3.6, -2.2), (-1.5, -2.0), (1.5, -2.3), (3.6, -2.0), 40)]
    out += [stone(-3.1, -1.95, 0.35, 0.2), stone(3.1, -1.85, 0.3, 0.18)]
    out += [pine(-2.9, 0.4, 2.2, 0.8), pine(3.0, 0.5, 1.8, 0.7)]
    return make("Mountain Bike on the Trail", out)


@design("camping_hiker", T)
def hiker(rng):
    head = circle(0.35, 1.95, 0.38, 30)
    hat = [chain(quad((-0.25, 2.12), (0.35, 2.0), (1.0, 2.15), 10)), chain([(0.0, 2.1)], quad((0.0, 2.55), (0.4, 2.65), (0.7, 2.1), 10))]
    torso = tube([(0.3, 1.5), (0.1, 0.0)], 0.7)
    pack = [rrect(-1.25, -0.1, -0.15, 1.75, 0.3), rect(-1.1, 0.1, -0.3, 0.7)]
    roll = [rrect(-1.35, 1.75, -0.05, 2.15, 0.2)]
    arm = tube([(0.45, 1.25), (0.85, 0.5), (1.35, 0.65)], 0.24)
    pole = [(1.35, 0.95), (1.95, -2.3)]
    legs = [tube([(0.25, 0.0), (0.85, -0.95), (1.05, -2.0)], 0.32), tube([(0.0, 0.0), (-0.35, -1.1), (-0.8, -1.95)], 0.32)]
    boots = [rrect(0.85, -2.3, 1.55, -1.95, 0.12), rrect(-1.2, -2.25, -0.5, -1.9, 0.12)]
    ground = [(-3.4, -2.3), (3.4, -2.3)]
    peaks = poly((-3.4, -0.6), (-2.6, 0.6), (-2.0, 0.0), (-1.6, 0.4), closed=False)
    peaks2 = poly((2.0, -0.2), (2.7, 1.2), (3.4, 0.2), closed=False)
    sun = [circle(2.5, 2.4, 0.45, 30)]
    return make("Hiker with a Backpack", [head, torso, arm, ground, peaks, peaks2] + hat + pack + roll + [pole] + legs + boots + sun,
                [eye(0.55, 1.95, 0.06)])


@design("camping_campsite_table", T)
def campsite_table(rng):
    top = poly((-2.8, 0.0), (0.4, 0.0), (1.4, 0.8), (-1.8, 0.8))
    top2 = poly((-2.8, 0.0), (-2.8, -0.2), (0.4, -0.2), (1.4, 0.6), (1.4, 0.8), closed=False)
    bench_f = poly((-3.1, -0.9), (0.1, -0.9), (0.1, -1.1), (-3.1, -1.1))
    legs = [[(-2.4, -0.2), (-2.9, -2.0)], [(-2.4, -0.2), (-1.9, -2.0)], [(0.0, -0.2), (-0.5, -2.0)], [(0.0, -0.2), (0.5, -2.0)]]
    lantern = [rect(-1.0, 0.45, -0.5, 0.6), poly((-0.95, 0.6), (-1.05, 1.3), (-0.45, 1.3), (-0.55, 0.6)), poly((-1.1, 1.3), (-0.75, 1.6), (-0.4, 1.3)), arc(-0.75, 1.6, 0.2, 0, math.pi, 8)]
    ring = [stone(2.3 + 0.95 * math.cos(a), -1.8 + 0.42 * math.sin(a), 0.26, 0.17) for a in [k * TAU / 9 for k in range(9)]]
    fire = [flame(2.3, -1.85, 0.4, 0.7)]
    tent = [chain(cubic((0.9, 1.6), (1.0, 2.8), (2.8, 2.8), (2.9, 1.6), 24)), [(0.9, 1.6), (2.9, 1.6)], quad((1.5, 1.6), (1.9, 2.4), (2.3, 1.6), 10)]
    trees = [pine(-3.0, 1.0, 2.0, 0.8)]
    return make("Campsite with a Picnic Table", [top, top2, bench_f] + legs + lantern + ring + fire + tent + trees)


@design("camping_canteen", T)
def canteen(rng):
    body = circle(0, 0.2, 1.8, 90)
    seam = circle(0, 0.2, 1.45, 80)
    neck = [rect(-0.3, 2.0, 0.3, 2.35)]
    cap = rrect(-0.42, 2.35, 0.42, 2.75, 0.1)
    strap = tube(earc(0, 1.0, 1.85, 2.2, 0.0, math.pi, 40), 0.32, cap=False)
    lugs = [rect(-1.95, 0.85, -1.75, 1.15), rect(1.75, 0.85, 1.95, 1.15)]
    chain_ = [quad((0.42, 2.55), (1.0, 2.2), (0.9, 1.75), 10)]
    cup = [poly((2.0, -1.3), (2.15, -2.6), (3.25, -2.6), (3.4, -1.3)), ellipse(2.7, -1.3, 0.7, 0.15, 20), arc(2.0, -1.9, 0.35, math.pi / 2, 1.5 * math.pi, 10)]
    stitch = [arc(0, 0.2, 1.1, 0.4, 2.7, 20)]
    return make("Canteen and Tin Cup", [body, seam, cap, strap] + neck + lugs + chain_ + cup + stitch)


@design("camping_multitool", T)
def multitool(rng):
    jaw = [chain([(-0.45, 1.3)], quad((-0.45, 2.2), (-0.1, 2.9), (0.0, 3.0), 10), quad((0.0, 3.0), (0.1, 2.9), (0.45, 2.2), 10), [(0.45, 1.3)]),
           [(0.0, 3.0), (0.0, 1.9)], circle(0, 1.3, 0.22, 16)]
    teeth = []
    hl = [tube([(-0.35, 1.0), (-1.6, -2.6)], 0.7)]
    hr = [tube([(0.35, 1.0), (1.6, -2.6)], 0.7)]
    rivets = [circle(-1.4, -2.0, 0.1, 8), circle(1.4, -2.0, 0.1, 8), circle(-0.62, 0.1, 0.1, 8), circle(0.62, 0.1, 0.1, 8)]
    blade = chain([(-1.25, -2.15)], [(-3.0, -1.4)], quad((-3.0, -1.4), (-2.2, -2.2), (-1.5, -2.5), 10))
    driver = [(1.85, -2.25), (3.0, -1.5), (3.15, -1.75), (2.05, -2.55)]
    saw = []
    return make("Folding Multitool Pliers", jaw + hl[:1] + hr + rivets + [blade, driver] + teeth + saw)


@design("camping_survival_tin", T)
def survival_tin(rng):
    base = [rrect(-3.0, -2.6, 3.0, -0.1, 0.4), rrect(-2.75, -2.35, 2.75, -0.35, 0.3)]
    lid = [rrect(-3.0, 0.1, 3.0, 2.6, 0.4), rrect(-2.75, 0.35, 2.75, 2.35, 0.3)]
    hinge = [[(-2.0, -0.1), (-2.0, 0.1)], [(2.0, -0.1), (2.0, 0.1)]]
    whistle = [rrect(-2.4, -1.1, -1.0, -0.6, 0.22), rect(-1.0, -0.98, -0.6, -0.72), circle(-2.6, -0.85, 0.15, 10), rect(-1.9, -0.6, -1.5, -0.45)]
    matches = [rect(-2.4, -2.1, -0.9, -1.4)] + [[(-2.2, -1.4), (-2.2, -1.25)], circle(-2.2, -1.13, 0.12, 8), [(-1.7, -1.4), (-1.7, -1.25)], circle(-1.7, -1.13, 0.12, 8)]
    compass = [circle(0.0, -1.3, 0.6, 30), circle(0.0, -1.3, 0.42, 26), poly((0, -0.95), (0.1, -1.3), (0, -1.65), (-0.1, -1.3))]
    striker = [rrect(1.0, -0.9, 2.4, -0.65, 0.1), rrect(1.0, -2.0, 2.4, -1.6, 0.1), circle(2.55, -0.78, 0.12, 8)]
    bandage = [rrect(1.0, -1.45, 2.4, -1.1, 0.15)]
    mirror = [rrect(-2.2, 0.7, 0.4, 2.0, 0.15), star(-1.4, 1.5, 0.3, 4, 0.35)]
    candle = [rect(1.0, 0.7, 1.4, 1.6), quad((1.2, 1.6), (1.05, 1.9), (1.2, 2.1), 6), quad((1.2, 1.6), (1.35, 1.9), (1.2, 2.1), 6)]
    wire = [spiral(2.1, 1.35, 0.15, 0.5, 2.0, 50)]
    return make("Survival Kit Tin", base + lid + hinge + whistle + matches + compass + striker + bandage + mirror + candle + wire)


@design("camping_park_patch", T)
def park_patch(rng):
    def shield(s):
        pts = chain(arc(0, 1.0 * s, 2.3 * s, math.radians(25), math.radians(155), 30),
                    quad((-2.08 * s, 1.97 * s), (-2.3 * s, -1.2 * s), (0, -2.9 * s), 20)[1:],
                    quad((0, -2.9 * s), (2.3 * s, -1.2 * s), (2.08 * s, 1.97 * s), 20))
        return pts + [pts[0]]

    outer = shield(1.0)
    inner = [transform(shield(0.88), dy=0.08)]
    mtn = poly((-1.7, -0.3), (-0.8, 1.2), (-0.3, 0.5), (0.4, 1.7), (1.7, -0.3), closed=False)
    snow = poly((0.05, 1.2), (0.25, 1.05), (0.45, 1.25), (0.65, 1.05), (0.75, 1.2), closed=False)
    sun = arc(-0.9, 1.6, 0.45, 0, TAU, 30)
    tree = [pine(-1.1, -1.6, 1.5, 0.7)]
    river = [cubic((0.2, -0.3), (0.6, -0.9), (-0.2, -1.3), (0.4, -2.2), 20), cubic((0.9, -0.3), (1.2, -0.9), (0.5, -1.4), (0.9, -2.0), 20)]
    banner = []
    return make("Embroidered National Park Patch", [outer, mtn, snow, sun] + inner + tree + river + banner)


@design("camping_trail_mix", T)
def trail_mix(rng):
    band = [rect(-1.5, 1.6, 1.5, 2.3), [(-1.5, 1.95), (1.5, 1.95)]]
    jar = chain([(-1.3, 1.6)], quad((-1.3, 1.6), (-1.85, 1.3), (-1.85, 0.8), 8),
                [(-1.85, -2.2)], arc(-1.45, -2.2, 0.4, math.pi, 1.5 * math.pi, 6),
                arc(1.45, -2.2, 0.4, 1.5 * math.pi, TAU, 6), [(1.85, 0.8)], quad((1.85, 0.8), (1.85, 1.3), (1.3, 1.6), 8))
    fill = quad((-1.85, 0.6), (0, 0.9), (1.85, 0.6), 16)

    def peanut(cx, cy, rot):
        return transform(polar(lambda t: 0.3 * (1 + 0.35 * math.cos(2 * t)), n=40), dx=cx, dy=cy, s=1.0, rot=rot)

    items = [peanut(-1.0, -0.2, 0.3), peanut(0.6, -1.4, -0.4), peanut(-0.4, -2.0, 1.2), peanut(1.1, 0.2, 0.8),
             circle(0.2, -0.3, 0.25, 16), circle(-1.2, -1.3, 0.25, 16), circle(1.2, -0.7, 0.25, 16), circle(-0.1, -1.1, 0.25, 16),
             lens((-0.8, 0.15), (-0.2, 0.45), 0.3), lens((0.3, -2.3), (0.9, -2.0), 0.3), lens((-1.5, -2.1), (-0.95, -2.4), 0.3),
             stone(0.7, -0.2, 0.22, 0.17), stone(-0.6, -0.7, 0.22, 0.17), stone(0.4, -0.7, 0.2, 0.16), stone(-0.9, -2.0 + 0.6, 0.2, 0.15)]
    spill = [peanut(2.6, -2.4, 0.4), circle(2.3, -1.8, 0.25, 16), lens((-3.0, -2.5), (-2.3, -2.3), 0.3), circle(-2.5, -1.9, 0.25, 16)]
    ground = [(-3.3, -2.65), (3.3, -2.65)]
    return make("Jar of Trail Mix", band + [jar, fill, ground] + items + spill)


@design("camping_summit_flag", T)
def summit_flag(rng):
    mtn = poly((-3.5, -2.6), (-1.2, 0.6), (-0.6, 0.2), (0, 1.6), (1.4, -0.2), (2.0, 0.2), (3.5, -2.6), closed=False)
    snow = poly((-0.55, 0.85), (-0.25, 0.55), (0.0, 0.8), (0.3, 0.5), (0.55, 0.85), (0.75, 0.75), closed=False)
    pole = [(0, 1.6), (0, 3.2)]
    flag = chain([(0, 3.2)], [(x, y + 0.2) for x, y in wave(0, 1.6, 3.0, 0.1, 1.2, 20)][1:], [(1.6, 2.4)],
                 [(x, y - 0.6) for x, y in wave(0, 1.6, 3.0, 0.1, 1.2, 20)][::-1])
    axe = [[(-0.6, 1.0), (-1.0, 2.5)], poly((-1.6, 2.35), (-0.4, 2.7), (-0.35, 2.55), (-1.55, 2.25)), [(-1.6, 2.35), (-1.75, 2.15)]]
    clouds = [chain(arc(x - 0.4, y, 0.32, math.pi, math.pi / 2 - 0.3, 10), arc(x + 0.1, y + 0.15, 0.4, math.pi - 0.4, 0.3, 10),
                    arc(x + 0.55, y, 0.3, math.pi / 2, 0, 8), [(x - 0.72, y)]) for x, y in [(-2.5, 1.5), (2.4, 1.3)]]
    ridge2 = [cubic((-1.2, 0.6), (-1.0, -0.5), (-0.4, -1.2), (-0.2, -2.6), 20), cubic((1.4, -0.2), (1.0, -1.0), (1.3, -1.8), (1.0, -2.6), 20)]
    return make("Summit Flag and Ice Axe", [mtn, snow, pole, flag] + axe + clouds + ridge2)


@design("camping_teardrop_trailer", T)
def teardrop_trailer(rng):
    gy = -1.6
    body = chain(cubic((-2.6, -0.8), (-3.0, 1.2), (-1.2, 1.5), (0.0, 1.5), 24), cubic((0.0, 1.5), (1.6, 1.5), (2.8, 0.8), (2.6, -0.8), 24),
                 [(1.0, -0.8)], arc(0.2, -0.8, 0.8, 0, math.pi, 16), [(-2.6, -0.8)])
    trim = chain(cubic((-2.35, -0.6), (-2.7, 1.0), (-1.1, 1.25), (0.0, 1.25), 24), cubic((0.0, 1.25), (1.4, 1.25), (2.5, 0.7), (2.35, -0.6), 24))
    door = rrect(-1.6, -0.6, -0.4, 0.95, 0.4)
    win = ellipse(-1.0, 0.5, 0.35, 0.25, 20)
    handle = [(-0.55, 0.0), (-0.55, 0.2)]
    wheel = [circle(0.2, -1.0, 0.6, 40), circle(0.2, -1.0, 0.3, 24)]
    tongue = [[(-2.6, -0.6), (-3.6, -0.9)], [(-2.6, -0.8), (-3.6, -0.9)], circle(-3.6, -0.9, 0.12, 10)]
    jack = [rect(-3.15, -1.45, -2.95, -0.75), ellipse(-3.05, -1.5, 0.2, 0.06, 10)]
    light = [ellipse(2.6, -0.4, 0.1, 0.2, 10)]
    ground = [(-3.6, gy), (3.6, gy)]
    return make("Teardrop Camping Trailer", [body, trim, door, win, handle, ground] + wheel + tongue + jack + light)


@design("camping_outhouse", T)
def outhouse(rng):
    walls = poly((-1.5, -2.4), (-1.5, 1.35), (1.5, 1.75), (1.5, -2.4), closed=False)
    roof = poly((-1.85, 1.25), (1.85, 1.75), (1.85, 2.05), (-1.85, 1.55))
    door = rect(-1.0, -2.35, 1.0, 1.0)
    moon = crescent(-0.1, 0.45, 0.32, 0.2)
    braces = [[(-1.0, -1.8), (1.0, -1.8)], [(-1.0, 0.0), (1.0, 0.0)], [(-1.0, -1.8), (1.0, 0.0)]]
    knob = circle(0.75, -0.9, 0.08, 8)
    boards = [[(-1.25, -2.4), (-1.25, 1.38)], [(1.25, -2.4), (1.25, 1.72)]]
    ground = [(-3.0, -2.4), (3.0, -2.4)]
    tp = [ellipse(2.25, -1.0, 0.3, 0.35, 20), ellipse(2.25, -1.0, 0.1, 0.12, 10), [(1.5, -0.65), (2.25, -0.65)]]
    flowers = [grass(-2.2, -2.4), grass(2.2, -2.4), grass(-2.7, -2.4, 0.2)]
    trees = [pine(-2.8, -2.4, 2.8, 1.0)]
    return make("Outhouse with a Crescent Moon", [walls, roof, door, moon, knob, ground] + braces + boards + tp + flowers + trees)


@design("camping_mess_kit", T)
def mess_kit(rng):
    rim = ellipse(-1.0, 0.6, 1.5, 0.38, 60)
    inner = ellipse(-1.0, 0.6, 1.15, 0.27, 50)
    body = chain([(-2.5, 0.6), (-2.5, -1.4)], earc(-1.0, -1.4, 1.5, 0.38, math.pi, TAU, 30), [(0.5, 0.6)])
    handle = [poly((-2.5, 0.2), (-3.4, 0.25), (-3.4, -0.1), (-2.5, -0.1), closed=False)]
    pan = [ellipse(1.6, -1.0, 1.1, 0.45, 50, rot=0.25), ellipse(1.6, -1.0, 0.85, 0.32, 40, rot=0.25)]
    pan_handle = tube([(2.6, -0.6), (3.4, 0.2)], 0.25)
    cup = []
    spork = [transform(chain(cubic((0, 0), (-0.5, 0.0), (-0.5, 1.0), (-0.25, 1.2), 12), [(-0.15, 1.0), (-0.05, 1.2), (0.05, 1.0), (0.15, 1.2), (0.25, 1.2)],
                             cubic((0.25, 1.2), (0.5, 1.0), (0.5, 0.0), (0, 0), 12)), dx=0.6, dy=1.0, rot=-0.5),
             transform(rrect(-0.1, -1.6, 0.1, 0.0, 0.08), dx=0.6, dy=1.0, rot=-0.5)]
    steam = [cubic((x, 1.1), (x - 0.25, 1.4), (x + 0.25, 1.6), (x, 1.9), 10) for x in (-1.5, -0.7)]
    return make("Camp Mess Kit and Spork", [rim, inner, body, pan_handle] + handle + pan + spork + steam + cup)


@design("camping_bow_saw", T)
def bow_saw(rng):
    bucks = []
    for cx in (-1.8, 1.8):
        bucks += [[(cx - 0.8, -2.6), (cx + 0.5, 0.4)], [(cx + 0.8, -2.6), (cx - 0.5, 0.4)]]
    log = log_end((-3.2, -0.6), (3.0, -0.6), 0.8)
    rings = [ellipse(3.0, -0.6, 0.09, 0.2, 12)]
    cut = [(0.4, -0.2), (0.25, -0.65)]
    bow = tube(earc(0.6, 0.4, 1.7, 2.3, 0.0, math.pi, 40), 0.22, cap=True)
    blade = zigzag(-1.1, 2.3, 0.3, 0.07, 12)
    handle_ = [rrect(2.15, 0.05, 2.5, 0.7, 0.1)]
    dust = [stone(0.3, -2.5, 0.5, 0.12), stone(-0.3, -2.6, 0.3, 0.08)]
    ground = [(-3.3, -2.6), (3.3, -2.6)]
    return make("Bow Saw on a Sawbuck Log", bucks + log + rings + [cut, bow, blade, ground] + handle_ + dust)


# dropped: the subject repeats another book
def rock_cairn(rng):
    rocks = []
    y = -2.4
    for rx, ry, dx in [(1.5, 0.5, 0.0), (1.2, 0.45, 0.15), (1.0, 0.4, -0.1), (0.8, 0.36, 0.1), (0.6, 0.3, -0.05), (0.42, 0.25, 0.05)]:
        rocks.append(stone(dx, y + ry, rx, ry))
        y += 2 * ry - 0.02
    mtn = poly((-3.5, 0.0), (-2.4, 1.6), (-1.6, 0.8), closed=False)
    mtn2 = poly((1.4, 0.6), (2.5, 2.2), (3.5, 0.6), closed=False)
    ground = [[(-3.5, -2.4), (-1.5, -2.4)], [(1.5, -2.4), (3.5, -2.4)]]
    tufts = [grass(-2.4, -2.4), grass(2.3, -2.4), grass(-1.9, -2.4, 0.2)]
    sun = [circle(-1.2, 2.5, 0.4, 24)]
    birds = [chain(arc(x - 0.15, yy, 0.15, 0.3, math.pi - 0.3, 6), arc(x + 0.15, yy, 0.15, 0.3, math.pi - 0.3, 6)[::-1]) for x, yy in [(0.9, 2.4), (1.6, 2.8)]]
    return make("Rock Cairn on the Trail", rocks + [mtn, mtn2] + ground + tufts + sun + birds)


@design("camping_kitchen_station", T)
def kitchen_station(rng):
    top = rect(-3.0, -0.3, 3.0, 0.0)
    legs = [[(-2.8, -0.3), (-2.2, -2.6)], [(-2.2, -0.3), (-2.8, -2.6)], [(2.8, -0.3), (2.2, -2.6)], [(2.2, -0.3), (2.8, -2.6)]]
    jug = [rrect(-2.7, 0.0, -1.3, 1.9, 0.2), rrect(-2.35, 1.9, -1.65, 2.2, 0.08),
           rect(-1.3, 0.35, -1.0, 0.55), rect(-1.15, 0.15, -1.05, 0.35)]
    jug_handle = []
    basin = [chain([(-0.6, 0.9)], quad((-0.6, 0.9), (-0.4, 0.0), (0.6, 0.0), 10), quad((0.6, 0.0), (1.6, 0.0), (1.8, 0.9), 10)),
             ellipse(0.6, 0.9, 1.2, 0.2, 40)]
    board = [rrect(1.9, 0.0, 2.9, 0.15, 0.05), lens((2.0, 0.35), (2.9, 0.55), 0.25)]
    towel = [poly((-0.6, -0.3), (-0.55, -1.6), (0.65, -1.6), (0.6, -0.3), closed=False), [(-0.55, -1.3), (0.65, -1.3)]]
    bucket = []
    return make("Camp Kitchen Station", [top] + legs + jug + basin + board + towel + bucket + jug_handle)


@design("camping_stakes_mallet", T)
def stakes_mallet(rng):
    head = transform(rrect(-1.1, -0.45, 1.1, 0.45, 0.25), dx=-0.6, dy=1.6, rot=0.35)
    face = [transform([(x, -0.45), (x, 0.45)], dx=-0.6, dy=1.6, rot=0.35) for x in (-0.75, 0.75)]
    handle = tube([(-0.45, 1.1), (0.8, -2.4)], 0.32)
    grip = [tube([(0.37, -1.2), (0.85, -2.55)], 0.42)]
    stakes = []
    for k, (x, rot) in enumerate([(1.8, 0.1), (2.6, -0.08)]):
        stakes.append(transform(poly((-0.15, 1.6), (0.15, 1.6), (0.12, -0.9), (0.0, -1.5), (-0.12, -0.9)), dx=x, dy=0.2, rot=rot))
        stakes.append(transform(quad((-0.15, 1.6), (-0.15, 2.0), (0.35, 2.0), 8), dx=x, dy=0.2, rot=rot))
    ystake = [poly((-2.4, 1.4), (-2.0, 1.4), (-2.1, -1.2), (-2.25, -1.8), (-2.35, -1.2)), [(-2.2, 1.4), (-2.18, -0.8)]]
    cord = [spiral(-2.2, -2.3, 0.15, 0.6, 1.5, 40)]
    return make("Tent Stakes and Mallet", [head, handle] + face + grip + stakes + ystake + cord)


@design("camping_cave", T)
def cave(rng):
    hill = [(-3.6, -2.3), (-3.2, -0.6), (-2.6, 0.6), (-1.6, 1.6), (-0.4, 2.1), (0.8, 2.0), (1.9, 1.4), (2.8, 0.4), (3.3, -0.8), (3.6, -2.3)]
    m = cubic((-1.8, -2.3), (-2.0, 1.3), (2.0, 1.3), (1.8, -2.3), 60)
    mouth = m[:16]
    for k in range(16, 44, 4):
        a, b = m[k], m[k + 4]
        mouth += [a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 0.5)]
    mouth += m[44:]
    mites = [poly((-1.1, -2.3), (-0.9, -1.7), (-0.7, -2.3), closed=False), poly((0.8, -2.3), (1.0, -1.85), (1.2, -2.3), closed=False)]
    strata = [cubic((-3.0, -0.2), (-2.6, 0.0), (-2.3, -0.3), (-2.0, -0.1), 10), cubic((2.2, 0.6), (2.5, 0.4), (2.8, 0.6), (3.1, 0.3), 10),
              cubic((-1.2, 1.5), (-0.8, 1.7), (-0.4, 1.5), (0.0, 1.7), 10)]
    path = [cubic((-0.6, -2.3), (-0.5, -2.9), (-1.0, -3.0), (-1.2, -3.3), 10), cubic((0.6, -2.3), (0.8, -2.9), (1.2, -3.0), (1.6, -3.3), 10)]
    lantern = [rect(-0.2, -2.0, 0.2, -1.4), arc(0, -1.4, 0.2, 0, math.pi, 8), [(-0.25, -2.0), (0.25, -2.0)]]
    rocks = [stone(-2.6, -2.1, 0.45, 0.25), stone(2.6, -2.0, 0.5, 0.3)]
    trees = [pine(0.9, 2.0, 1.2, 0.55), pine(-2.1, 1.1, 0.9, 0.45)]
    ground = [[(-3.6, -2.3), (-1.8, -2.3)], [(1.8, -2.3), (3.6, -2.3)]]
    return make("Cave Entrance with Stalactites", [hill, mouth] + mites + strata + path + lantern + rocks + trees + ground)


@design("camping_water_pump", T)
def water_pump(rng):
    pad = rect(-2.4, -2.6, 2.6, -2.25)
    base = rect(-0.75, -2.25, 0.75, -1.95)
    body = poly((-0.45, -1.95), (-0.45, 1.2), (0.45, 1.2), (0.45, -1.95), closed=False)
    bands = [[(-0.45, -1.4), (0.45, -1.4)], [(-0.45, 0.2), (0.45, 0.2)]]
    cap = chain([(-0.6, 1.2), (0.6, 1.2)], arc(0, 1.2, 0.6, 0, math.pi, 16))
    spout = tube([(0.45, 0.65), (1.2, 0.5), (1.55, 0.1)], 0.32)
    drops = [chain([(x, y + 0.3)] + arc(x, y, 0.12, 0.0, -math.pi, 12)[::-1][::-1], [(x, y + 0.3)])
             for x, y in [(1.6, -0.45), (1.6, -1.0)]]
    pivot = [circle(-0.3, 1.95, 0.12, 10), [(-0.3, 1.83), (-0.1, 1.6)]]
    handle = tube([(0.2, 1.75), (-2.7, 2.9)], 0.24)
    grip = tube([(-2.5, 2.82), (-3.2, 3.1)], 0.36)
    bucket = [poly((0.95, -1.0), (1.15, -2.25), (2.35, -2.25), (2.55, -1.0)), ellipse(1.75, -1.0, 0.8, 0.15, 24),
              earc(1.75, -1.1, 0.85, 0.7, 0.0, math.pi, 20), [(1.03, -1.45), (2.47, -1.45)]]
    ground = [(-3.4, -2.6), (3.4, -2.6)]
    tufts = [grass(-2.9, -2.6), grass(3.0, -2.6)]
    return make("Campground Water Pump", [pad, base, body, cap, spout, handle, grip, ground] + bands + drops + pivot + bucket + tufts)


@design("camping_moonlit_forest", T)
def moonlit_forest(rng):
    moon = [circle(0.2, 1.9, 1.0, 60), circle(-0.1, 2.2, 0.22, 14), circle(0.55, 1.6, 0.3, 16), circle(0.4, 2.45, 0.15, 10)]
    trees = [pine(x, -2.6, h, w) for x, h, w in [(-3.0, 4.4, 1.2), (-1.8, 3.0, 1.1), (-0.65, 2.5, 1.0), (0.6, 2.2, 0.95), (1.8, 3.2, 1.1), (3.0, 4.2, 1.2)]]
    ground = [(-3.6, -2.6), (3.6, -2.6)]
    sky = stars([(-2.0, 2.4, 0.18), (1.8, 2.8, 0.2), (-1.2, 1.4, 0.14), (2.3, 1.6, 0.15)])
    return make("Moonlit Pine Forest", moon + trees + [ground] + sky)


@design("camping_ranger_hat", T)
def ranger_hat(rng):
    t0 = math.acos(1.4 / 3.0)
    brim = earc(0, -0.6, 3.0, 0.85, math.pi - t0, t0 + TAU, 80)
    crown = chain([(-1.4, -0.4)], cubic((-1.4, -0.4), (-1.5, 0.9), (-0.7, 1.9), (0, 2.2), 20)[1:], cubic((0, 2.2), (0.7, 1.9), (1.5, 0.9), (1.4, -0.4), 20)[1:])
    base = quad((-1.4, -0.4), (0, -0.85), (1.4, -0.4), 16)
    band = quad((-1.43, -0.05), (0, -0.5), (1.43, -0.05), 16)
    pinch = [quad((0, 2.2), (-0.15, 1.5), (-0.55, 0.9), 10), quad((0, 2.2), (0.15, 1.5), (0.55, 0.9), 10)]
    dents = [quad((-1.0, 1.3), (-0.75, 0.9), (-0.85, 0.4), 8), quad((1.0, 1.3), (0.75, 0.9), (0.85, 0.4), 8)]
    acorns = [ellipse(1.1, -0.65, 0.12, 0.17, 10), ellipse(1.35, -0.75, 0.12, 0.17, 10)]
    strap = [quad((1.2, -0.55), (1.4, -1.1), (1.0, -1.3), 8)]
    return make("Park Ranger Campaign Hat", [brim, crown, base, band] + pinch + dents + acorns + strap)


@design("camping_clothesline", T)
def clothesline(rng):
    trunks = [[(-3.2, -2.6), (-3.15, 1.4)], [(-2.7, -2.6), (-2.75, 1.4)], [(3.2, -2.6), (3.15, 1.4)], [(2.7, -2.6), (2.75, 1.4)]]
    crowns = [polar(lambda t: 0.9 + 0.08 * math.sin(9 * t), cx=x, cy=2.1, n=120) for x in (-2.95, 2.95)]

    def ly(x):
        return 0.9 - 0.5 * (1 - (x / 2.75) ** 2)

    line = [(x, ly(x)) for x in [-2.75 + 5.5 * i / 40 for i in range(41)]]
    sock = []
    for cx, flip in [(-1.9, 1), (-1.2, -1)]:
        s = [(cx - 0.22, ly(cx - 0.22)), (cx - 0.22, ly(cx) - 1.1), (cx - 0.22 + 0.0, ly(cx) - 1.35), (cx + 0.55 * flip, ly(cx) - 1.35),
             (cx + 0.55 * flip, ly(cx) - 1.05), (cx + 0.22, ly(cx) - 1.0), (cx + 0.22, ly(cx + 0.22))]
        if flip < 0:
            s = [(2 * cx - x, y) for x, y in s]
        sock.append(s)
        sock.append([(cx - 0.22, ly(cx) - 0.3), (cx + 0.22, ly(cx) - 0.3)])
    shirt = [(-0.3, ly(-0.3)), (-0.75, ly(-0.3) - 0.5), (-0.5, ly(-0.3) - 0.75), (-0.3, ly(-0.3) - 0.55), (-0.3, -1.6), (0.9, -1.6), (0.9, ly(0.9) - 0.55),
             (1.1, ly(0.9) - 0.75), (1.35, ly(0.9) - 0.5), (0.9, ly(0.9))]
    neck = quad((0.1, ly(0.1)), (0.3, ly(0.3) - 0.3), (0.5, ly(0.5)), 8)
    towel = [(1.6, ly(1.6)), (1.6, -1.4), (2.4, -1.4), (2.4, ly(2.4))]
    stripes = [[(1.6, -1.0), (2.4, -1.0)]]
    pins = [rect(x - 0.06, ly(x) - 0.1, x + 0.06, ly(x) + 0.25) for x in (-1.9, -1.2, 0.3, 2.0)]
    ground = [(-3.6, -2.6), (3.6, -2.6)]
    return make("Camp Clothesline Drying Socks", trunks + crowns + [line, shirt, neck, towel, ground] + sock + stripes[:1] + pins)
