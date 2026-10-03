"""Summer Beach niche, part 2 (pictures 10-53)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "beach"


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


def sea(y, x0=-3.2, x1=3.2, amp=0.1, waves=5):
    return wave(x0, x1, y, amp, waves, 100)


def ell_arc(cx, cy, rx, ry, a0, a1, n=60):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / n), cy + ry * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def clip_ellipse(p, q, cx, cy, rx, ry):
    """The part of segment p-q inside an axis-aligned ellipse (or None)."""
    ax, ay = (p[0] - cx) / rx, (p[1] - cy) / ry
    bx, by = (q[0] - cx) / rx, (q[1] - cy) / ry
    dx, dy = bx - ax, by - ay
    A, B, C = dx * dx + dy * dy, 2 * (ax * dx + ay * dy), ax * ax + ay * ay - 1
    disc = B * B - 4 * A * C
    if disc <= 0:
        return None
    s = math.sqrt(disc)
    t0, t1 = max(0.0, (-B - s) / (2 * A)), min(1.0, (-B + s) / (2 * A))
    if t1 - t0 < 0.05:
        return None
    return [(p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t) for t in (t0, t1)]


def frond(x, y, ang, L, droop=0.5, w=0.22):
    """A palm leaf from (x, y) at angle `ang`, drooping at the tip."""
    tip = (x + L * math.cos(ang), y + L * math.sin(ang) - droop * abs(math.cos(ang)))
    return lens((x, y), tip, w)


def gull(x, y, s):
    return chain(quad((x - s, y + 0.25 * s), (x - 0.5 * s, y + 0.5 * s), (x, y)), quad((x, y), (x + 0.5 * s, y + 0.5 * s), (x + s, y + 0.25 * s)))


def small_star(cx, cy, r, rot=0.0):
    return polar(lambda t: r * (0.55 + 0.45 * math.cos(5 * (t - math.pi / 2 - rot)) ** 2 * (1 if math.cos(5 * (t - math.pi / 2 - rot)) > 0 else 0.0)),
                 cx=cx, cy=cy, n=120)


@design("beach_deck_chair", T)
def deck_chair(rng):
    top = rrect(-1.7, 2.3, 1.7, 2.65, 0.12)
    left = cubic((-1.4, 2.3), (-1.5, 1.2), (-1.7, 0.2), (-1.6, -0.6), 30)
    bottom = quad((-1.6, -0.6), (0, -1.1), (1.6, -0.6), 30)
    canvas_ = chain(left, bottom, mirror_x(left)[::-1])
    stripes = [quad((f * 1.4, 2.3), (f * 1.62, 0.8), (f * 1.6, -0.6 - 0.45 * (1 - f * f)), 20) for f in (-0.6, -0.2, 0.2, 0.6)]
    rails = [tube([(-1.65, 2.3), (-1.95, -1.2)], 0.2, cap=False), tube([(1.65, 2.3), (1.95, -1.2)], 0.2, cap=False)]
    bar = rrect(-2.2, -1.45, 2.2, -1.2, 0.08)
    legs = [tube([(-1.98, -1.45), (-2.2, -2.6)], 0.2, cap=False), tube([(1.98, -1.45), (2.2, -2.6)], 0.2, cap=False)]
    back_legs = [[(-1.2, -1.45), (-0.9, -2.3)], [(1.2, -1.45), (0.9, -2.3)]]
    sand = [sea(-2.65, amp=0.06, waves=4)]
    shell = [arc(2.8, -2.6, 0.3, 0, math.pi, 12)]
    return make("Striped Deck Chair", [top, canvas_, bar] + stripes + rails + legs + back_legs + sand + shell)


def palm(x0, lean, h=4.0, top_w=0.3):
    base = (x0, -2.6)
    topp = (x0 + lean, -2.6 + h)
    ctr = cubic(base, (x0, -1.0), (x0 + lean * 0.6, 0.0), topp, 30)
    trunk = tube(ctr, lambda t: 0.5 - 0.5 * t * (0.5 - top_w) / 0.5 if top_w < 0.5 else 0.5, cap=False)
    rings = []
    for t in (0.2, 0.4, 0.6, 0.8):
        i = int(t * 30)
        x, y = ctr[i]
        w = (0.5 - t * (0.5 - top_w)) / 2
        rings.append(quad((x - w, y), (x, y - 0.12), (x + w, y), 8))
    return [trunk] + rings, topp


@design("beach_hammock", T)
def hammock(rng):
    lt, ltop = palm(-2.4, 0.3)
    rt, rtop = palm(2.4, -0.3)
    leaves = []
    for (x, y), side in ((ltop, -1), (rtop, 1)):
        for a in (20, 60, 100, 140, 170):
            ang = math.radians(a if side > 0 else 180 - a)
            leaves.append(frond(x, y, ang, 1.5, 0.6, 0.18))
    bed_top = quad((-1.6, 0.3), (0, -0.9), (1.6, 0.3), 40)
    bed_bot = quad((-1.6, 0.3), (0, -1.9), (1.6, 0.3), 40)
    ropes = [[(-2.15, 0.6), (-1.6, 0.3)], [(2.15, 0.6), (1.6, 0.3)]]
    net = [[(x, -0.3 - 0.4 * (1 - (x / 1.6) ** 2) + 0.1), (x, -0.3 - 1.05 * (1 - (x / 1.6) ** 2) + 0.05)] for x in (-0.8, 0.0, 0.8)]
    pillow = ellipse(-0.95, -0.25, 0.4, 0.2, 24, rot=-0.5)
    sand = [sea(-2.6, amp=0.06, waves=4)]
    return make("Hammock Between Palms", lt + rt + leaves + [bed_top, bed_bot, pillow] + ropes + net + sand)


@design("beach_lifeguard_tower", T)
def lifeguard_tower(rng):
    hut = rect(-1.4, 0.4, 1.4, 2.0)
    roof = poly((-1.9, 2.0), (0, 2.8), (1.9, 2.0))
    window = rect(-1.0, 1.0, 0.2, 1.7)
    cross = poly((0.75, 0.9), (0.95, 0.9), (0.95, 1.15), (1.2, 1.15), (1.2, 1.35), (0.95, 1.35), (0.95, 1.6), (0.75, 1.6), (0.75, 1.35),
                 (0.5, 1.35), (0.5, 1.15), (0.75, 1.15))
    deck = rect(-2.0, 0.1, 2.0, 0.4)
    rail = [[(-2.0, 0.4), (-2.0, 1.1), (-1.4, 1.1)], [(-1.7, 0.4), (-1.7, 1.1)], [(2.0, 0.4), (2.0, 1.1), (1.4, 1.1)], [(1.7, 0.4), (1.7, 1.1)]]
    legs = [tube([(-1.7, 0.1), (-2.3, -2.6)], 0.22, cap=False), tube([(1.7, 0.1), (2.3, -2.6)], 0.22, cap=False)]
    braces = [[(-1.9, -0.8), (-0.75, -0.8)], [(1.9, -0.8), (0.75, -0.8)]]
    ladder = [[(-0.5, 0.1), (-0.8, -2.6)], [(0.5, 0.1), (0.8, -2.6)]] + \
             [[(-0.5 - 0.3 * f, 0.1 - 2.7 * f), (0.5 + 0.3 * f, 0.1 - 2.7 * f)] for f in (0.18, 0.38, 0.58, 0.78)]
    flag = [[(0, 2.8), (0, 3.5)], poly((0, 3.5), (0.8, 3.25), (0, 3.0), closed=False)]
    ring = [circle(2.75, -0.6, 0.45, 30), circle(2.75, -0.6, 0.22, 20)]
    sand = [sea(-2.6, amp=0.06, waves=5)]
    return make("Lifeguard Tower", [hut, roof, window, cross, deck] + rail + legs + braces + ladder + flag + ring + sand)


@design("beach_lighthouse", T)
def lighthouse(rng):
    tower = poly((-0.95, -1.4), (-0.6, 1.4), (0.6, 1.4), (0.95, -1.4), closed=False)
    bands = [[(-0.95 + 0.35 * f, -1.4 + 2.8 * f), (0.95 - 0.35 * f, -1.4 + 2.8 * f)] for f in (0.25, 0.5, 0.75)]
    gallery = rect(-0.95, 1.4, 0.95, 1.65)
    lantern = rect(-0.5, 1.65, 0.5, 2.4)
    panes = [[(0, 1.65), (0, 2.4)]]
    dome = chain(arc(0, 2.4, 0.6, 0, math.pi, 20))
    finial = [[(0, 3.0), (0, 3.3)]]
    beams = [poly((0.6, 2.25), (3.0, 2.8), (3.0, 1.7), (0.6, 1.85), closed=False), poly((-0.6, 2.25), (-3.0, 2.8), (-3.0, 1.7), (-0.6, 1.85), closed=False)]
    door = chain([(-0.3, -1.4), (-0.3, -0.9)], arc(0, -0.9, 0.3, math.pi, 0, 10), [(0.3, -1.4)])
    window = circle(0, 0.6, 0.18, 14)
    rocks = chain([(-3.2, -1.9)], arc(-2.5, -1.9, 0.7, math.pi, 0.3, 14), arc(-1.3, -1.6, 0.7, 2.6, 0.2, 14), arc(0, -1.5, 0.75, 2.8, 0.35, 14),
                  arc(1.3, -1.6, 0.7, 2.9, 0.4, 14), arc(2.5, -1.9, 0.7, 2.6, 0, 14), [(3.2, -1.9)])
    water = [sea(-2.4, waves=6), sea(-2.9, waves=5, amp=0.08)]
    birds = [gull(-1.8, 0.4, 0.4), gull(-2.6, 0.9, 0.3)]
    return make("Lighthouse on the Shore", [tower, gallery, lantern, dome, door, window, rocks] + bands + panes + finial + beams + water + birds)


@design("beach_sailboat", T)
def sailboat(rng):
    hull = chain([(-2.6, -0.6), (2.8, -0.6)], quad((2.8, -0.6), (2.2, -1.7), (1.4, -1.8), 12), [(-1.6, -1.8)],
                 quad((-1.6, -1.8), (-2.3, -1.5), (-2.6, -0.6), 12))
    stripe = [[(-2.4, -1.05), (2.55, -1.05)]]
    mast = [(0, -0.6), (0, 3.2)]
    main = chain([(0.15, 3.0)], quad((0.15, 3.0), (1.5, 1.4), (2.3, -0.35), 30), [(0.15, -0.35), (0.15, 3.0)])
    jib = chain([(-0.15, 2.7)], quad((-0.15, 2.7), (-1.2, 1.2), (-2.2, -0.35), 30), [(-0.15, -0.35), (-0.15, 2.7)])
    flag = poly((0, 3.2), (0.6, 3.0), (0, 2.85), closed=False)
    ports = [circle(x, -1.4, 0.16, 14) for x in (-1.0, 0.0, 1.0)]
    seams = [[(0.15, 1.9), (1.45, 1.2)], [(0.15, 0.8), (1.95, 0.35)]]
    water = [sea(-2.0, waves=6), sea(-2.6, waves=5, amp=0.08)]
    sun = [circle(-2.4, 2.6, 0.45, 30)]
    return make("Sailboat at Sea", [hull, mast, main, jib, flag] + stripe + ports + seams + water + sun)


@design("beach_kayak", T)
def kayak(rng):
    rot = math.atan2(1.0, 3.0)
    hull = lens((-3.0, -1.0), (3.0, 1.0), 0.11, 40)
    ridge = [[(-3.0, -1.0), (-0.75 * math.cos(rot), -0.75 * math.sin(rot))], [(0.75 * math.cos(rot), 0.75 * math.sin(rot)), (3.0, 1.0)]]
    cockpit = [ellipse(0, 0, 0.75, 0.38, 40, rot=rot), ellipse(0, 0, 0.55, 0.24, 30, rot=rot)]
    shaft = tube([(-1.4, 2.2), (1.4, -2.2)], 0.14, cap=True)
    blades = [lens((-1.35, 2.12), (-1.95, 3.05), 0.28), lens((1.35, -2.12), (1.95, -3.05), 0.28)]
    water = [wave(-3.2, -1.2, -2.2, 0.08, 2, 40), wave(0.4, 3.2, 2.3, 0.08, 3, 40), wave(1.8, 3.2, -0.9, 0.08, 1.5, 30),
             wave(-3.2, -1.8, 0.6, 0.08, 1.5, 30)]
    return make("Kayak and Paddle", [hull, shaft] + ridge + cockpit + blades + water)


@design("beach_crab", T)
def crab(rng):
    body = smooth([(-1.7, -0.5), (-1.4, 0.3), (0, 0.6), (1.4, 0.3), (1.7, -0.5), (1.2, -1.2), (0, -1.4), (-1.2, -1.2)], 10, True)
    stalks = [[(-0.5, 0.55), (-0.6, 1.3)], [(0.5, 0.55), (0.6, 1.3)]]
    eyes_ = [circle(-0.6, 1.55, 0.27, 24), circle(0.6, 1.55, 0.27, 24)]
    smile = arc(0, -0.2, 0.55, math.radians(200), math.radians(340), 16)
    arms = [tube([(-1.5, 0.1), (-2.1, 0.6), (-2.3, 1.2)], 0.3, cap=False), tube([(1.5, 0.1), (2.1, 0.6), (2.3, 1.2)], 0.3, cap=False)]
    claws = []
    for s in (-1, 1):
        claws.append(chain(arc(s * 2.3, 1.75, 0.6, -math.pi / 2 - 0.3, math.pi / 2 + 0.2, 24) if s > 0 else
                           arc(-2.3, 1.75, 0.6, math.pi / 2 - 0.2, 1.5 * math.pi + 0.3, 24)))
        claws.append(poly((s * 2.3, 1.75), (s * 2.0, 2.3), (s * 2.55, 1.9), closed=False))
    legs_ = []
    for s in (-1, 1):
        for k, (y, dy) in enumerate([(-0.4, -0.3), (-0.75, -0.6), (-1.05, -0.95)]):
            x0 = s * (1.55 - 0.15 * k)
            legs_.append(tube([(x0, y), (s * (2.3 - 0.1 * k), y + 0.1), (s * (2.7 - 0.2 * k), y + dy - 0.6)], 0.2, cap=False))
    sand = [sea(-2.6, amp=0.06, waves=4)]
    return make("Smiling Beach Crab", [body, smile] + stalks + eyes_ + arms + claws + legs_ + sand,
                [eye(-0.6, 1.55, 0.12), eye(0.6, 1.55, 0.12)])


@design("beach_starfish", T)
def starfish(rng):
    def r(t):
        c = math.cos(5 * (t - math.pi / 2))
        return 0.95 + 1.55 * ((c + 1) / 2) ** 2.2
    body = polar(r, n=300)
    bumps = []
    for k in range(5):
        a = math.pi / 2 + k * 2 * math.pi / 5
        for d in (0.75, 1.3, 1.85):
            bumps.append(circle(d * math.cos(a), d * math.sin(a), 0.15 - 0.02 * (d > 1.5), 12))
    centre = circle(0, 0, 0.3, 20)
    sand = [sea(-2.9, amp=0.06, waves=4)]
    shell = [arc(-2.6, -2.9, 0.35, 0, math.pi, 12), arc(2.5, -2.9, 0.25, 0, math.pi, 10)]
    return make("Starfish on the Sand", [body, centre] + bumps + sand + shell)


def scallop(cx, cy, s, rot=0.0):
    out = []
    edge = [(1.4 * s * math.cos(t) * (1 + 0.04 * math.cos(14 * t)), 1.4 * s * math.sin(t) * (1 + 0.04 * math.cos(14 * t)))
            for t in [math.radians(15 + 150 * i / 90) for i in range(91)]]
    fan = chain([(0.25 * s, 0.0)], edge, [(-0.25 * s, 0.0)])
    ears = poly((-0.25 * s, 0.0), (-0.55 * s, -0.25 * s), (0.55 * s, -0.25 * s), (0.25 * s, 0.0), closed=False)
    ribs = [[(0, 0.05 * s), (1.3 * s * math.cos(math.radians(a)), 1.3 * s * math.sin(math.radians(a)))] for a in (40, 65, 90, 115, 140)]
    for p in [fan, ears] + ribs:
        out.append(transform(p, dx=cx, dy=cy, rot=rot))
    return out


@design("beach_seashells", T)
def seashells(rng):
    sc = scallop(-1.5, 0.5, 1.1, 0.15)
    # turret shell
    tur = smooth([(1.2, -0.3), (0.8, 0.6), (1.2, 1.6), (1.55, 2.8), (1.9, 1.6), (2.4, 0.6), (2.2, -0.3)], 8, True)
    whorls = [quad((1.0 + 0.1 * k, 0.3 + 0.55 * k), (1.6, 0.05 + 0.55 * k), (2.3 - 0.15 * k, 0.6 + 0.55 * k), 12) for k in range(4)]
    mouth = ellipse(1.65, -0.05, 0.35, 0.2, 20)
    # clam
    clam = smooth([(-1.3, -2.7), (-2.3, -2.2), (-2.5, -1.4), (-1.9, -0.7), (-1.3, -0.6), (-0.7, -0.7), (-0.1, -1.4), (-0.3, -2.2)], 8, True)
    clam_rings = [smooth([(-1.3 - 0.95 * f, -2.45 + 0.25 * (1 - f)), (-1.3 - 0.9 * f, -1.5 - 0.0 * f), (-1.3, -2.55 + 1.8 * f),
                          (-1.3 + 0.9 * f, -1.5), (-1.3 + 0.95 * f, -2.45 + 0.25 * (1 - f))], 8) for f in (0.45, 0.75)]
    clam_rings = [ell_arc(-1.3, -2.55, 0.95 * f, 1.75 * f, math.radians(10), math.radians(170), 24) for f in (0.5, 0.78)]
    hinge = [ell_arc(-1.3, -2.75, 0.3, 0.15, 0, math.pi, 8)]
    # cowrie
    cow = ellipse(1.5, -1.8, 1.0, 0.65, 50, rot=0.2)
    slit = transform(zigzag(-0.7, 0.7, 0, 0.08, 8), dx=1.5, dy=-1.8, rot=0.2)
    return make("Seashell Collection", sc + [tur, mouth, clam, cow, slit] + whorls + clam_rings + hinge)


@design("beach_conch", T)
def conch(rng):
    out = smooth([(-2.9, 1.5), (-2.0, 1.9), (-1.4, 2.3), (-0.8, 2.1), (-0.3, 2.6), (0.3, 2.3), (0.9, 2.8), (1.5, 2.3), (2.4, 2.0),
                  (2.9, 1.2), (2.8, 0.0), (2.4, -1.2), (1.6, -1.8), (0.6, -2.2), (-0.4, -2.9), (-0.6, -2.4), (-0.6, -1.6),
                  (-1.4, -0.6), (-2.2, 0.4)], 8, True)
    aperture = smooth([(0.6, 1.6), (1.8, 1.4), (2.2, 0.2), (1.7, -1.1), (0.5, -1.6), (0.2, -0.4)], 8, True)
    lip = smooth([(0.3, 1.9), (2.2, 1.7), (2.55, 0.2), (2.0, -1.4)], 8)
    spire = [quad((-2.0, 1.85), (-1.9, 1.2), (-1.2, 1.0), 12), quad((-1.4, 2.25), (-1.0, 1.5), (-0.3, 1.4), 12),
             quad((-0.3, 2.55), (0.0, 1.8), (0.55, 1.65), 12)]
    knobs = [quad((-0.6, 0.9), (-0.2, 0.3), (-0.4, -0.5), 12), quad((-1.2, 0.6), (-0.9, 0.0), (-1.0, -0.5), 12)]
    sand = [sea(-3.0, amp=0.06, waves=4)]
    return make("Conch Shell", [out, aperture, lip] + spire + knobs + sand)


@design("beach_seagull", T)
def seagull(rng):
    body = smooth([(2.7, 0.0), (2.1, 0.22), (1.7, 0.6), (1.2, 0.55), (0.6, 0.55), (0.0, 1.2), (-0.8, 2.0), (-1.7, 2.6), (-2.7, 3.0),
                   (-1.8, 2.1), (-1.0, 1.1), (-0.8, 0.5), (-1.7, 0.4), (-2.6, 0.35), (-2.7, -0.05), (-1.8, -0.15),
                   (-0.6, -0.45), (0.6, -0.45), (1.5, -0.2), (2.1, -0.05)], 8, True)
    far_wing = smooth([(0.5, 0.4), (0.2, -0.6), (-0.4, -1.4), (-1.2, -2.0), (-0.9, -1.1), (-0.4, -0.45)], 8)
    feathers = [[(-2.25, 2.6), (-1.85, 2.4)], [(-2.0, 2.25), (-1.6, 2.05)]]
    beak = [[(2.1, 0.08), (2.6, 0.0)]]
    water = [sea(-2.4, waves=6), sea(-2.9, waves=5, amp=0.08)]
    sun = [arc(2.2, -2.4, 0.8, 0, math.pi, 24)]
    other = [gull(1.6, 2.4, 0.5), gull(2.6, 1.6, 0.35)]
    return make("Seagull in Flight", [body, far_wing] + feathers + beak + water + sun + other, [eye(1.55, 0.35, 0.08)])


@design("beach_pelican", T)
def pelican(rng):
    body = smooth([(-2.2, 0.0), (-1.4, 0.9), (-0.3, 1.2), (0.3, 1.6), (0.25, 2.4), (0.6, 2.95), (1.1, 2.95), (2.0, 2.65), (2.9, 2.35),
                   (2.75, 2.15), (2.2, 1.6), (1.6, 1.2), (1.1, 1.25), (0.95, 1.5), (1.1, 0.8), (0.9, -0.1), (0.2, -0.4), (-0.8, -0.4),
                   (-1.6, -0.3)], 8, True)
    bill = [quad((1.15, 2.6), (2.0, 2.35), (2.8, 2.24), 12)]
    wing = smooth([(-1.9, 0.1), (-1.2, 0.75), (-0.2, 0.9), (0.4, 0.4), (-0.2, -0.05), (-1.2, -0.1)], 8, True)
    legs_ = [[(-0.2, -0.4), (-0.25, -0.95)], [(0.4, -0.35), (0.45, -0.95)]]
    post = [rect(-0.8, -3.0, 0.8, -1.05), ellipse(0, -1.0, 0.8, 0.12, 30)]
    grain = [quad((-0.4, -1.4), (-0.3, -2.1), (-0.45, -2.8), 10), quad((0.35, -1.5), (0.45, -2.2), (0.3, -2.9), 10)]
    water = [sea(-2.5, -3.2, -0.9, waves=1.5), sea(-2.5, 0.9, 3.2, waves=1.5), sea(-2.95, -3.2, -0.9, waves=1.5, amp=0.08), sea(-2.95, 0.9, 3.2, waves=1.5, amp=0.08)]
    return make("Pelican on a Wharf Post", [body, wing] + bill + legs_ + post + grain + water, [eye(0.75, 2.6, 0.09)])


@design("beach_sun_hat", T)
def sun_hat(rng):
    t0 = math.acos(1.4 / 3.0)
    brim = [(3.0 * math.cos(t) * (1 + 0.025 * math.sin(9 * t)), -0.4 + 1.1 * math.sin(t)) for t in
            [math.pi - t0 + (math.pi + 2 * t0) * i / 120 for i in range(121)]]
    crown = chain(cubic((-1.4, 0.55), (-1.6, 2.6), (1.6, 2.6), (1.4, 0.55), 50))
    band = [quad((-1.45, 1.1), (0, 0.85), (1.45, 1.1), 24), quad((-1.42, 0.55), (0, 0.3), (1.42, 0.55), 24)]
    bow = [lens((1.0, 0.75), (2.0, 1.5), 0.3), lens((1.0, 0.75), (2.1, 0.6), 0.3), circle(1.0, 0.75, 0.16, 12)]
    tails = [quad((1.0, 0.6), (1.4, -0.1), (1.2, -0.8), 12)]
    weave = [ell_arc(0, -0.4, 2.3, 0.8, math.pi + 0.15, 2 * math.pi - 0.15, 50), ell_arc(0, -0.4, 1.8, 0.62, math.pi + 0.15, 2 * math.pi - 0.15, 40)]
    flower = [circle(-0.6, 0.72, 0.13, 12)] + [transform(lens((0, 0), (0.42, 0), 0.4), dx=-0.6, dy=0.72, rot=k * 2 * math.pi / 5 + 0.3) for k in range(5)]
    return make("Straw Sun Hat", [brim, crown] + band + bow + tails + weave + flower)


@design("beach_cooler", T)
def cooler(rng):
    box = rrect(-2.4, -2.2, 1.6, 0.4, 0.25)
    lid = rrect(-2.6, 0.4, 1.8, 1.2, 0.25)
    handle = [poly((-1.6, 1.2), (-1.6, 2.1), (0.8, 2.1), (0.8, 1.2), closed=False), poly((-1.3, 1.2), (-1.3, 1.8), (0.5, 1.8), (0.5, 1.2), closed=False)]
    side = [rrect(-2.6, -0.6, -2.4, 0.0, 0.05), rrect(1.6, -0.6, 1.8, 0.0, 0.05)]
    label = rrect(-1.6, -1.4, 0.8, -0.3, 0.15)
    sun = [circle(-0.4, -0.85, 0.25, 18)] + [[(-0.4 + 0.35 * math.cos(a), -0.85 + 0.35 * math.sin(a)), (-0.4 + 0.5 * math.cos(a), -0.85 + 0.5 * math.sin(a))]
                                             for a in [k * math.pi / 4 for k in range(8)]]
    plug = circle(1.2, -1.9, 0.15, 12)
    bottle = chain([(2.1, -2.2), (2.1, -0.3)], quad((2.1, -0.3), (2.1, 0.2), (2.35, 0.6), 8), [(2.35, 1.2), (2.65, 1.2), (2.65, 0.6)],
                   quad((2.65, 0.6), (2.9, 0.2), (2.9, -0.3), 8), [(2.9, -2.2), (2.1, -2.2)])
    blabel = rect(2.1, -1.5, 2.9, -0.7)
    cap = rect(2.3, 1.2, 2.7, 1.45)
    sand = [sea(-2.25, amp=0.05, waves=5)]
    return make("Picnic Cooler", [box, lid, label, plug, bottle, blabel, cap] + handle + side + sun + sand)


@design("beach_ice_cream_cart", T)
def ice_cream_cart(rng):
    box = rrect(-2.4, -1.2, 1.4, 0.6, 0.2)
    lids = [ellipse(-1.4, 0.75, 0.55, 0.15, 24), ellipse(0.4, 0.75, 0.55, 0.15, 24)]
    wheel = [circle(-1.2, -1.75, 0.65, 50), circle(-1.2, -1.75, 0.15, 12)] + \
            [[(-1.2 + 0.15 * math.cos(a), -1.75 + 0.15 * math.sin(a)), (-1.2 + 0.65 * math.cos(a), -1.75 + 0.65 * math.sin(a))] for a in [k * math.pi / 3 for k in range(6)]]
    stand = [[(1.0, -1.2), (1.0, -2.4)], [(0.7, -2.4), (1.3, -2.4)]]
    handle = [[(1.4, 0.2), (2.6, 0.7)], rrect(2.5, 0.5, 3.1, 0.95, 0.15)]
    pole = [(-0.5, 0.6), (-0.5, 1.6)]
    scallops = chain(*[arc(-2.2 + 0.85 * k, 1.6, 0.425, math.pi, 2 * math.pi, 10) for k in range(4)])
    canopy = chain(scallops, quad((1.18, 1.6), (-0.5, 3.6), (-2.62, 1.6), 40))
    ribs = [quad((-0.5, 2.6), (x * 0.6 - 0.2, 2.1), (x, 1.6), 10) for x in (-1.775, -0.925, -0.075, 0.775)]
    cone = [poly((-0.9, -0.95), (-0.5, -0.1), (-1.3, -0.1)), arc(-0.9, -0.1, 0.4, 0, math.pi, 12)]
    stripe = [[(-2.4, -0.5), (-1.5, -0.5)], [(-0.3, -0.5), (1.4, -0.5)]]
    ground = [sea(-2.45, amp=0.05, waves=5)]
    return make("Ice Cream Cart", [box, canopy, pole] + lids + wheel + stand + handle + ribs + cone + stripe + ground)


@design("beach_popsicle", T)
def popsicle(rng):
    drips = smooth([(1.3, -1.0), (1.0, -1.25), (0.8, -1.7), (0.55, -1.25), (0.0, -1.1), (-0.45, -1.3), (-0.65, -1.9), (-0.85, -1.3), (-1.3, -1.0)], 6)
    bite = arc(1.25, 2.0, 0.5, math.radians(180), math.radians(290), 14)
    ice = chain(drips, [(-1.3, -1.0), (-1.3, 1.6)], arc(0, 1.6, 1.3, math.pi, math.radians(70), 30), bite, [(1.3, 1.55), (1.3, -1.0)])
    stick = chain([(-0.3, -1.25), (-0.3, -2.6)], arc(0, -2.6, 0.3, math.pi, 2 * math.pi, 10), [(0.3, -1.2)])
    stripes = [quad((-1.3, y), (0, y + 0.35), (1.3, y), 16) for y in (-0.2, 0.6)]
    drops = [chain(quad((x, y + 0.35), (x - 0.18, y), (x, y - 0.1), 8), quad((x, y - 0.1), (x + 0.18, y), (x, y + 0.35), 8)) for x, y in [(-0.65, -2.5), (0.8, -2.25)]]
    puddle = [ellipse(0.2, -3.0, 1.4, 0.18, 40)]
    sun = [circle(2.5, 2.6, 0.4, 24)] + [[(2.5 + 0.55 * math.cos(a), 2.6 + 0.55 * math.sin(a)), (2.5 + 0.8 * math.cos(a), 2.6 + 0.8 * math.sin(a))] for a in [k * math.pi / 4 for k in range(8)]]
    return make("Melting Popsicle", [ice, stick] + stripes + drops + puddle + sun)


@design("beach_coconut_drink", T)
def coconut_drink(rng):
    t0 = math.asin(1.4 / 1.9)
    shell = arc(0, -0.8, 1.9, math.pi - t0, 2 * math.pi + t0, 80)
    opening = ellipse(0, 0.6, 1.28, 0.32, 50)
    hair = [[(x, y), (x + 0.15, y - 0.25)] for x, y in [(-1.3, -0.2), (-0.6, -0.6), (0.4, -0.3), (1.1, -0.9), (-1.0, -1.6), (0.2, -1.5), (0.9, -2.0), (-0.3, -2.3)]]
    straw = tube(chain([(0.4, 0.6), (1.0, 2.4)], quad((1.0, 2.4), (1.15, 2.85), (1.7, 2.9), 8)), 0.22, cap=True)
    umb = chain([(-2.4, 2.0)], quad((-2.4, 2.0), (-1.4, 3.3), (-0.4, 2.0), 20), zigzag(-0.4, -2.4, 2.0, 0.08, 5))
    stick = [(-1.4, 2.0), (-0.6, 0.55)]
    slice_ = [arc(-1.4, 0.95, 0.6, math.radians(200), math.radians(340), 14), [(-1.96, 0.75), (-0.84, 0.75)]]
    leaves = [lens((0, -2.7), (-2.6, -2.3), 0.15), lens((0, -2.7), (2.6, -2.4), 0.15)]
    return make("Coconut Drink", [shell, opening, straw, umb, stick] + hair + slice_ + leaves)


@design("beach_pineapple", T)
def pineapple(rng):
    cx, cy, rx, ry = 0, -0.8, 1.55, 2.05
    body = ellipse(cx, cy, rx, ry, 120)
    lat = []
    for k in range(-5, 6):
        o = 0.75 * k
        for sgn in (1, -1):
            seg = clip_ellipse((o - 4, cy - 4 * sgn), (o + 4, cy + 4 * sgn), cx, cy, rx * 0.97, ry * 0.97)
            if seg:
                lat.append(seg)
    crown = []
    for a, L in [(90, 2.0), (65, 1.7), (115, 1.7), (40, 1.3), (140, 1.3)]:
        ang = math.radians(a)
        crown.append(lens((0.3 * math.cos(ang), 1.2), (0.3 * math.cos(ang) + L * math.cos(ang), 1.2 + L * math.sin(ang)), 0.14))
    sand = [sea(-3.0, amp=0.05, waves=4)]
    return make("Tropical Pineapple", [body] + lat + crown + sand)


@design("beach_watermelon", T)
def watermelon(rng):
    rind = chain(arc(0, -1.2, 3.0, math.pi, 0, 80)[::-1], [(-3.0, -1.2)])
    inner = arc(0, -1.2, 2.65, 0.02, math.pi - 0.02, 70)
    flesh = arc(0, -1.2, 2.4, 0.02, math.pi - 0.02, 70)
    base = [(-3.0, -1.2), (3.0, -1.2)]
    seeds = []
    for r, angs in [(1.0, (60, 120)), (1.6, (35, 70, 110, 145)), (2.0, (20, 50, 90, 130, 160))]:
        for a in angs:
            x, y = r * math.cos(math.radians(a)), -1.2 + r * math.sin(math.radians(a))
            seeds.append(ellipse(x, y, 0.1, 0.18, 14, rot=math.radians(a - 90)))
    sand = [sea(-1.6, amp=0.05, waves=5)]
    return make("Watermelon Slice", [rind, inner, flesh, base] + seeds + sand)


@design("beach_snorkel_mask", T)
def snorkel_mask(rng):
    frame = smooth([(-2.4, 0.6), (-2.2, 1.6), (-1.2, 1.9), (0, 1.75), (1.2, 1.9), (2.2, 1.6), (2.4, 0.6), (2.0, -0.6), (1.0, -1.0),
                    (0.45, -0.7), (0, -1.2), (-0.45, -0.7), (-1.0, -1.0), (-2.0, -0.6)], 8, True)
    glass = [smooth([(-2.0, 0.6), (-1.85, 1.35), (-1.0, 1.5), (-0.3, 1.3), (-0.25, 0.2), (-0.9, -0.5), (-1.7, -0.3)], 8, True)]
    glass.append(mirror_x(glass[0]))
    shine = [[(-1.6, 1.0), (-1.1, 0.4)], [(0.6, 1.0), (1.1, 0.4)]]
    straps = [quad((-2.4, 0.8), (-3.0, 0.9), (-3.2, 0.0), 12), quad((-2.3, 0.2), (-2.9, 0.3), (-3.2, -0.6), 12)]
    sn = chain([(2.85, 3.0), (2.85, -1.6)], arc(2.25, -1.6, 0.6, 0, -math.pi / 2, 10), [(1.6, -2.2)])
    snorkel = tube(sn, 0.36, cap=True)
    mouth = rrect(1.25, -2.55, 1.6, -1.85, 0.1)
    bands = [[(2.67, 2.5), (3.03, 2.5)], [(2.67, 2.1), (3.03, 2.1)]]
    bubbles = [circle(-1.6, 2.6, 0.2, 14), circle(-1.0, 3.0, 0.15, 12), circle(-2.1, 3.1, 0.12, 12)]
    return make("Snorkel and Mask", [frame, snorkel, mouth] + glass + shine + straps + bands + bubbles)


@design("beach_swim_fins", T)
def swim_fins(rng):
    def fin(dx, rot):
        out = smooth([(0, 2.7), (0.6, 2.45), (0.7, 1.4), (0.75, 0.4), (1.1, -0.8), (1.35, -2.5), (0.7, -2.25), (0, -2.6), (-0.7, -2.25),
                      (-1.35, -2.5), (-1.1, -0.8), (-0.75, 0.4), (-0.7, 1.4), (-0.6, 2.45)], 8, True)
        opening = ellipse(0, 2.05, 0.38, 0.22, 24)
        pocket = quad((-0.72, 0.6), (0, -0.2), (0.72, 0.6), 16)
        ribs = [quad((x * 0.5, -0.1), (x * 0.9, -1.2), (x, -2.2), 12) for x in (-0.85, 0.0, 0.85)]
        return [transform(p, dx=dx, rot=rot, s=0.95) for p in [out, opening, pocket] + ribs]
    bubbles = [circle(0, 2.6, 0.22, 16), circle(0.3, 2.0, 0.15, 12), circle(-0.25, 1.6, 0.12, 12)]
    return make("Swim Fins", fin(-1.6, 0.12) + fin(1.6, -0.12) + bubbles)


@design("beach_swim_ring", T)
def swim_ring(rng):
    outer = ellipse(0, 0, 2.7, 2.0, 140)
    inner = ellipse(0, 0.2, 1.15, 0.7, 70)
    stripes = []
    for a in (40, 110, 200, 290):
        t = math.radians(a)
        stripes.append(quad((1.2 * math.cos(t), 0.2 + 0.73 * math.sin(t)), (1.9 * math.cos(t + 0.1), 1.4 * math.sin(t + 0.1)),
                            (2.68 * math.cos(t), 1.98 * math.sin(t)), 12))
    for a in (65, 135, 225, 315):
        t = math.radians(a)
        stripes.append(quad((1.2 * math.cos(t), 0.2 + 0.73 * math.sin(t)), (1.9 * math.cos(t + 0.1), 1.4 * math.sin(t + 0.1)),
                            (2.68 * math.cos(t), 1.98 * math.sin(t)), 12))
    shine = [ell_arc(0, 0, 2.3, 1.65, math.radians(120), math.radians(160), 12)]
    valve = [rrect(2.5, -0.15, 2.95, 0.15, 0.06)]
    water = [sea(-2.4, waves=6), sea(-2.85, waves=5, amp=0.08)]
    return make("Inflatable Swim Ring", [outer, inner] + stripes + shine + valve + water)


@design("beach_flamingo_float", T)
def flamingo_float(rng):
    outer = ellipse(0.4, -1.2, 2.5, 1.05, 120)
    inner = ellipse(0.5, -1.05, 1.2, 0.42, 60)
    neck = tube(cubic((-1.5, -0.9), (-2.6, 0.8), (-0.6, 1.1), (-1.2, 2.3), 30), lambda t: 0.6 - 0.2 * t, cap=False)
    head = smooth([(-1.55, 2.3), (-1.55, 2.75), (-1.1, 3.05), (-0.5, 2.9), (-0.2, 2.6), (-0.05, 2.1), (-0.3, 2.3), (-0.75, 2.4), (-0.95, 2.25)], 8)
    beak_line = [(-0.48, 2.85), (-0.42, 2.48)]
    tail = [lens((2.7, -0.9), (3.4, 0.2), 0.3), lens((2.6, -1.0), (3.6, -0.5), 0.3)]
    wing = [lens((-0.2, -1.95), (1.8, -1.7), 0.18)]
    water = [wave(-3.4, -2.0, -2.3, 0.08, 1.5, 30), wave(2.8, 3.6, -2.0, 0.08, 1, 20), sea(-2.85, -3.4, 3.6, waves=6)]
    return make("Flamingo Pool Float", [outer, inner, neck, head, beak_line] + tail + wing + water, [eye(-0.95, 2.7, 0.1)])


@design("beach_surfer", T)
def surfer(rng):
    curl = chain(cubic((-3.2, -1.5), (-3.4, 1.0), (-2.4, 2.9), (-1.0, 2.7), 30), cubic((-1.0, 2.7), (-0.4, 2.6), (-0.6, 1.6), (-1.3, 1.6), 16))
    curl_in = spiral(-1.6, 1.95, 0.05, 0.45, 1.0, 40, rot=-0.6)
    face = cubic((-1.5, 1.45), (-1.6, 0.4), (-1.4, -0.6), (-0.9, -1.3), 20)
    lines_ = [cubic((-2.7, -1.4), (-2.9, 0.6), (-2.2, 2.2), (-1.3, 2.35), 24)]
    board = lens((-1.0, -1.15), (2.8, -0.45), 0.1, 30)
    dx = 0.6
    legs_ = [tube([(-0.3 + dx, -0.9), (-0.25 + dx, -0.25), (0.25 + dx, 0.3)], 0.32, cap=False),
             tube([(1.1 + dx, -0.62), (0.95 + dx, -0.05), (0.45 + dx, 0.3)], 0.32, cap=False)]
    torso = tube([(0.35 + dx, 0.25), (0.45 + dx, 1.4)], 0.6, cap=True)
    head = circle(0.6 + dx, 1.95, 0.33, 30)
    arms = [tube([(0.25 + dx, 1.25), (-0.4 + dx, 1.0), (-1.0 + dx, 1.35)], 0.24, cap=True), tube([(0.6 + dx, 1.25), (1.3 + dx, 1.05), (1.9 + dx, 1.4)], 0.24, cap=True)]
    water = [wave(-0.9, 3.2, -1.5, 0.1, 3, 60), sea(-2.2, waves=6), sea(-2.8, waves=5, amp=0.08)]
    spray = [circle(-0.6, -0.4, 0.12, 10), circle(-0.3, -0.1, 0.1, 10), circle(-0.8, 0.1, 0.1, 10)]
    return make("Surfer Riding a Wave", [curl, curl_in, face, board, torso, head] + lines_ + legs_ + arms + water + spray)


@design("beach_big_wave", T)
def big_wave(rng):
    outer = chain(cubic((3.2, -2.4), (3.4, 0.6), (2.4, 2.9), (0.2, 2.8), 40), cubic((0.2, 2.8), (-1.4, 2.7), (-2.2, 1.6), (-1.5, 0.8), 30))
    curl = spiral(-0.6, 1.5, 0.1, 0.85, 1.15, 70, rot=math.pi + 0.2)
    face = cubic((-1.4, 0.65), (-0.6, -0.4), (-1.8, -1.8), (-3.2, -2.1), 30)
    inner = [cubic((2.4, -2.4), (2.6, 0.4), (1.8, 2.1), (0.3, 2.15), 30), cubic((1.6, -2.4), (1.8, 0.0), (1.4, 1.2), (0.6, 1.5), 24)]
    foam = []
    for k in range(6):
        t = 0.15 + 0.13 * k
        p = cubic((3.2, -2.4), (3.4, 0.6), (2.4, 2.9), (0.2, 2.8), 40)[int(t * 40)]
        foam.append(arc(p[0] + 0.15, p[1] + 0.15, 0.22, math.radians(-40), math.radians(150), 10))
    sea_ = [sea(-2.4, -3.2, 3.2, waves=4, amp=0.08), sea(-2.9, waves=6, amp=0.08)]
    drops = [circle(-2.4, 2.4, 0.16, 12), circle(-2.8, 1.9, 0.12, 10), circle(-1.9, 2.9, 0.12, 10)]
    return make("Curling Ocean Wave", [outer, curl, face] + inner + foam + sea_ + drops)


@design("beach_huts", T)
def beach_huts(rng):
    out = []
    for k, x in enumerate((-2.4, -0.8, 0.8, 2.4)):
        h = 1.6 + 0.25 * (k % 2)
        out.append(rect(x - 0.7, -1.4, x + 0.7, -1.4 + h))
        out.append(poly((x - 0.85, -1.4 + h), (x, -0.4 + h), (x + 0.85, -1.4 + h)))
        out.append(rect(x - 0.35, -1.4, x + 0.35, -0.2))
        out.append(circle(x, -0.6 + h, 0.16, 12))
        if k % 2 == 0:
            out += [[(xx, -1.4 + 0.0), (xx, -1.4 + h)] for xx in (x - 0.52, x + 0.52)]
        else:
            out += [[(x - 0.7, -1.4 + y), (x - 0.35, -1.4 + y)] for y in (0.3, 0.6, 0.9)] + [[(x + 0.35, -1.4 + y), (x + 0.7, -1.4 + y)] for y in (0.3, 0.6, 0.9)]
    deck = [rect(-3.3, -1.75, 3.3, -1.4)] + [[(x, -1.75), (x, -1.4)] for x in (-2.2, -1.1, 0.0, 1.1, 2.2)]
    posts = [[(x, -1.75), (x, -2.4)] for x in (-3.0, -1.0, 1.0, 3.0)]
    sand = [sea(-2.4, amp=0.06, waves=5)]
    birds = [gull(-1.6, 2.4, 0.35), gull(1.4, 2.7, 0.3)]
    return make("Row of Beach Huts", out + deck + posts + sand + birds)


@design("beach_pier", T)
def pier(rng):
    deck = rect(-3.4, 0.0, 2.4, 0.35)
    rails = [[(-3.4, 1.0), (2.4, 1.0)]] + [[(x, 0.35), (x, 1.0)] for x in (-3.0, -2.0, -1.0, 0.0, 1.0, 2.0)]
    piles = [rect(x - 0.1, -2.2, x + 0.1, 0.0) for x in (-2.6, -1.4, -0.2, 1.0, 2.2)]
    braces = [[(-2.5, -0.2), (-1.5, -1.2)], [(-1.3, -0.2), (-0.3, -1.2)], [(-0.1, -0.2), (0.9, -1.2)], [(1.1, -0.2), (2.1, -1.2)]]
    shack = [rect(0.6, 1.0, 2.2, 2.2), poly((0.4, 2.2), (1.4, 2.9), (2.4, 2.2)), rect(1.1, 1.0, 1.6, 1.8)]
    lamp = [[(-2.0, 1.0), (-2.0, 2.4)], poly((-2.25, 2.4), (-1.75, 2.4), (-1.85, 2.8), (-2.15, 2.8))]
    water = [sea(-1.5, -3.4, 3.2, waves=7, amp=0.08), sea(-2.4, waves=6, amp=0.08)]
    gulls = [gull(-0.6, 2.6, 0.4), gull(2.9, 3.0, 0.3)]
    return make("Wooden Pier", [deck] + rails + piles + braces + shack + lamp + water + gulls)


@design("beach_kite", T)
def beach_kite(rng):
    kite = poly((0.6, 3.0), (2.0, 1.5), (0.6, -0.6), (-0.8, 1.5))
    spars = [[(0.6, 3.0), (0.6, -0.6)], [(-0.8, 1.5), (2.0, 1.5)]]
    tail = cubic((0.6, -0.6), (1.6, -1.4), (-0.2, -1.9), (0.8, -2.8), 40)
    bows = []
    for i in (12, 24, 34):
        x, y = tail[i]
        bows += [poly((x, y), (x - 0.35, y + 0.2), (x - 0.35, y - 0.2)), poly((x, y), (x + 0.35, y + 0.2), (x + 0.35, y - 0.2))]
    string = quad((0.6, 1.5), (-1.4, 0.2), (-2.4, -1.9), 30)
    dune = [quad((-3.4, -2.2), (-2.0, -1.4), (-0.6, -2.4), 30), sea(-2.8, amp=0.06, waves=4)]
    grass = [quad((x, -2.0), (x + dx * 0.3, -1.4), (x + dx, -0.9), 8) for x, dx in [(-2.9, -0.3), (-2.7, 0.1), (-2.5, 0.4)]]
    cloud = chain([(-3.2, 2.0)], arc(-2.8, 2.2, 0.35, math.radians(150), math.radians(30), 10), arc(-2.2, 2.4, 0.45, math.radians(150), math.radians(20), 10),
                  arc(-1.65, 2.15, 0.3, math.radians(120), 0, 8), [(-1.35, 2.0), (-3.2, 2.0)])
    return make("Kite at the Beach", [kite, tail, string, cloud] + spars + bows + dune + grass)


@design("beach_turtle_hatchling", T)
def turtle_hatchling(rng):
    shell = ellipse(0, 0, 1.2, 1.5, 80)
    scutes = [poly(*[(0.36 * math.cos(math.pi / 6 + k * math.pi / 3), y + 0.36 * math.sin(math.pi / 6 + k * math.pi / 3)) for k in range(6)])
              for y in (-0.72, 0.0, 0.72)]
    side = [[(0.32, 0.18), (1.1, 0.5)], [(-0.32, 0.18), (-1.1, 0.5)], [(0.32, -0.54), (1.1, -0.6)], [(-0.32, -0.54), (-1.1, -0.6)]]
    head = smooth([(-0.35, 1.4), (-0.45, 1.9), (0, 2.35), (0.45, 1.9), (0.35, 1.4)], 8)
    flips = [lens((-1.0, 0.8), (-2.4, 1.4), 0.2), lens((1.0, 0.8), (2.4, 0.3), 0.2), lens((-0.8, -1.1), (-1.5, -1.8), 0.25),
             lens((0.8, -1.1), (1.4, -1.9), 0.25)]
    tail = poly((-0.15, -1.48), (0, -1.85), (0.15, -1.48), closed=False)
    eggs = [ellipse(-2.3, -2.2, 0.42, 0.52, 30), ellipse(-1.6, -2.4, 0.38, 0.47, 30),
            chain([(1.85, -2.15)], arc(2.35, -2.15, 0.5, math.pi, 2 * math.pi, 24), zigzag(2.85, 1.85, -2.05, 0.1, 3))]
    sand = [sea(-2.85, amp=0.05, waves=4)]
    sea_ = [sea(2.9, waves=5, amp=0.1), sea(2.5, -3.2, -0.6, waves=2, amp=0.08), sea(2.5, 0.6, 3.2, waves=2, amp=0.08)]
    return make("Sea Turtle Hatchling", [shell, head, tail] + scutes + side + flips + eggs + sand + sea_,
                [eye(-0.18, 1.95, 0.07), eye(0.18, 1.95, 0.07)])


@design("beach_dolphin", T)
def dolphin(rng):
    body = smooth([(3.0, 0.0), (2.5, 0.15), (2.1, 0.6), (1.0, 0.85), (0.4, 0.9), (-0.3, 1.8), (-0.45, 0.75), (-1.4, 0.45), (-2.3, 0.15),
                   (-3.1, 0.8), (-2.75, 0.0), (-3.1, -0.75), (-2.3, -0.15), (-1.0, -0.5), (0.6, -0.7), (1.8, -0.45), (2.4, -0.15)], 8, True)
    fin = lens((0.6, -0.55), (-0.2, -1.4), 0.25)
    mouth = [(2.45, -0.02), (2.0, -0.15)]
    parts = [transform(p, rot=0.45, dy=0.4) for p in (body, fin, mouth)]
    splash = [quad((x, -2.2), (x + 0.2 * s, -1.6), (x + 0.5 * s, -1.4), 8) for x, s in [(-1.8, -1), (-1.3, -1), (-2.3, -1)]]
    drops = [circle(-0.9, -1.4, 0.12, 10), circle(-2.6, -1.3, 0.12, 10), circle(-1.4, -0.9, 0.1, 10)]
    water = [sea(-2.3, waves=6), sea(-2.85, waves=5, amp=0.08)]
    e = transform([(2.1, 0.3)], rot=0.45, dy=0.4)[0]
    return make("Leaping Beach Dolphin", parts + splash + drops + water, [eye(e[0], e[1], 0.09)])


@design("beach_message_bottle", T)
def message_bottle(rng):
    b = chain([(-2.2, -0.75)], arc(-2.2, 0.0, 0.75, -math.pi / 2, -math.pi * 1.5, 20), [(0.6, 0.75)], quad((0.6, 0.75), (1.1, 0.75), (1.4, 0.32), 10),
              [(2.4, 0.32), (2.4, -0.32), (1.4, -0.32)], quad((1.4, -0.32), (1.1, -0.75), (0.6, -0.75), 10), [(-2.2, -0.75)])
    lip = [[(2.1, 0.32), (2.1, -0.32)]]
    cork = rect(2.4, -0.25, 2.9, 0.25)
    scroll = [rect(-1.6, -0.45, 0.2, 0.45), ellipse(-1.6, 0.0, 0.15, 0.45, 20), ellipse(0.2, 0.0, 0.15, 0.45, 20)]
    ribbon = [[(-0.75, -0.45), (-0.75, 0.45)], [(-0.6, -0.45), (-0.6, 0.45)]]
    parts = [transform(p, rot=0.3, dy=0.2) for p in [b, cork] + lip + scroll + ribbon]
    sand = [sea(-1.7, amp=0.06, waves=4)]
    surf = [sea(2.4, waves=5, amp=0.12), sea(1.9, -3.2, -0.2, waves=2, amp=0.08)]
    shell = [arc(-2.4, -2.4, 0.4, 0, math.pi, 12), [(-2.8, -2.4), (-2.0, -2.4)]]
    star_ = [star(2.3, -2.3, 0.4, 5, 0.45)]
    return make("Message in a Bottle", parts + sand + surf + shell + star_)


@design("beach_tiki_hut", T)
def tiki_hut(rng):
    roof = chain([(-3.0, 0.6), (0, 2.9), (3.0, 0.6)])
    fringe = chain([(-3.0, 0.6)], zigzag(-3.0, 3.0, 0.45, 0.18, 12)[1:], [(3.0, 0.6)])
    thatch = [[(-1.5, 1.75), (-1.9, 0.75)], [(0, 2.9), (0, 0.75)], [(1.5, 1.75), (1.9, 0.75)], [(-0.75, 2.3), (-0.95, 0.75)], [(0.75, 2.3), (0.95, 0.75)]]
    posts = [rect(-2.6, -1.1, -2.3, 0.3), rect(2.3, -1.1, 2.6, 0.3)]
    counter = [rect(-2.8, -1.1, 2.8, -0.85), rect(-2.4, -2.6, 2.4, -1.1)]
    slats = [[(x, -2.6), (x, -1.1)] for x in (-1.6, -0.8, 0.0, 0.8, 1.6)]
    sign = [rrect(-1.0, -0.2, 1.0, 0.25, 0.1), [(-0.6, 0.25), (-0.6, 0.45)], [(0.6, 0.25), (0.6, 0.45)]]
    drinks = [poly((-1.8, -0.85), (-1.9, -0.25), (-1.4, -0.25), (-1.5, -0.85)), [(-1.55, -0.25), (-1.3, 0.2)],
              poly((1.5, -0.85), (1.4, -0.25), (1.9, -0.25), (1.8, -0.85))]
    sand = [sea(-2.75, amp=0.05, waves=5)]
    return make("Tiki Bar Hut", [roof, fringe] + thatch + posts + counter + slats + sign + drinks + sand)


@design("beach_volleyball", T)
def volleyball(rng):
    posts = [rect(-3.0, -2.4, -2.75, 1.8), rect(2.75, -2.4, 3.0, 1.8)]
    net = [rect(-2.75, 0.2, 2.75, 1.4), [(-2.75, 1.2), (2.75, 1.2)]]
    mesh = [[(x, 0.2), (x, 1.2)] for x in [-2.75 + 0.55 * k for k in range(1, 10)]] + [[(-2.75, 0.7), (2.75, 0.7)]]
    ball = circle(0.8, 2.55, 0.65, 50)
    panels = [arc(0.8 - 0.9, 2.55, 0.9, -0.75, 0.75, 14), arc(0.8 + 0.9, 2.55, 0.9, math.pi - 0.75, math.pi + 0.75, 14),
              arc(0.8, 2.55 + 1.0, 1.0, math.radians(235), math.radians(305), 12)]
    motion = [[(-0.4, 2.2), (-1.4, 1.8)], [(-0.3, 2.6), (-1.5, 2.4)]]
    sand = [sea(-2.4, amp=0.06, waves=5), sea(-2.9, amp=0.05, waves=3, x0=-2.0, x1=2.0)]
    ropes = [[(-2.75, 1.4), (-3.4, -2.4)], [(2.75, 1.4), (3.4, -2.4)]]
    return make("Beach Volleyball", posts + net + mesh + [ball] + panels + motion + sand + ropes)


@design("beach_sunscreen", T)
def sunscreen(rng):
    bottle = chain([(-1.2, 1.4)], quad((-1.2, 1.4), (-1.5, -0.5), (-1.3, -2.4), 20), [(1.3, -2.4)], quad((1.3, -2.4), (1.5, -0.5), (1.2, 1.4), 20), [(-1.2, 1.4)])
    cap = rrect(-0.9, 1.4, 0.9, 2.3, 0.15)
    flip = [poly((-0.5, 2.3), (-0.5, 2.6), (0.4, 2.6), (0.6, 2.3), closed=False)]
    label = rrect(-0.95, -1.6, 0.95, 0.6, 0.2)
    sun = [circle(0, -0.4, 0.4, 24)] + [poly(((0.5) * math.cos(a - 0.15), -0.4 + 0.5 * math.sin(a - 0.15)), (0.75 * math.cos(a), -0.4 + 0.75 * math.sin(a)),
                                              (0.5 * math.cos(a + 0.15), -0.4 + 0.5 * math.sin(a + 0.15)), closed=False) for a in [k * math.pi / 4 for k in range(8)]]
    sand = [sea(-2.45, amp=0.05, waves=5)]
    glasses = [ellipse(2.05, -2.05, 0.38, 0.3, 24), ellipse(2.95, -2.05, 0.38, 0.3, 24), arc(2.5, -2.0, 0.12, 0.3, math.pi - 0.3, 6),
               [(1.67, -1.95), (1.45, -1.7)]]
    return make("Sunscreen Bottle", [bottle, cap, label] + flip + sun + sand + glasses)


@design("beach_towel", T)
def beach_towel(rng):
    def P(u, v):  # towel plane in perspective: u in [0,1] across, v in [0,1] along
        x0 = -2.8 + 0.8 * v
        x1 = 2.8 - 0.8 * v
        return (x0 + (x1 - x0) * u, -2.0 + 3.6 * v)
    towel = [P(0, 0), P(1, 0), P(1, 1), P(0, 1), P(0, 0)]
    stripes = [[P(u, 0), P(u, 1)] for u in (0.2, 0.3, 0.7, 0.8)]
    fringe = [[P(u, 0), (P(u, 0)[0], -2.35)] for u in [k / 12 for k in range(1, 12)]]
    book = [poly((-0.9, -0.2), (0, -0.4), (0.9, -0.2), (0.9, 0.9), (0, 0.7), (-0.9, 0.9)), [(0, -0.4), (0, 0.7)]]
    lines_ = [[(-0.7, y), (-0.15, y - 0.12)] for y in (0.55, 0.3, 0.05)] + [[(0.15, y - 0.12), (0.7, y)] for y in (0.55, 0.3, 0.05)]
    glasses = [circle(-1.3, 1.6, 0.3, 20), circle(-0.55, 1.6, 0.3, 20), arc(-0.925, 1.62, 0.1, 0.2, math.pi - 0.2, 6)]
    sand = [sea(-2.7, amp=0.05, waves=5)]
    return make("Beach Towel with Book", [towel] + book + stripes + fringe + lines_ + glasses + sand)


@design("beach_happy_sun", T)
def happy_sun(rng):
    face = circle(0, 0, 1.6, 120)
    rays = []
    for k in range(12):
        a = k * math.pi / 6
        if k % 2:
            rays.append(poly((1.85 * math.cos(a - 0.12), 1.85 * math.sin(a - 0.12)), (2.9 * math.cos(a), 2.9 * math.sin(a)),
                             (1.85 * math.cos(a + 0.12), 1.85 * math.sin(a + 0.12)), closed=False))
        else:
            rays.append([((1.85 + 0.9 * i / 20) * math.cos(a + 0.1 * math.sin(i * math.pi / 5)), (1.85 + 0.9 * i / 20) * math.sin(a + 0.1 * math.sin(i * math.pi / 5)))
                         for i in range(21)])
    glasses = [rrect(-1.25, 0.05, -0.15, 0.75, 0.25), rrect(0.15, 0.05, 1.25, 0.75, 0.25), arc(0, 0.5, 0.18, 0.3, math.pi - 0.3, 6),
               [(-1.25, 0.6), (-1.55, 0.75)], [(1.25, 0.6), (1.55, 0.75)]]
    smile = arc(0, -0.2, 0.8, math.radians(210), math.radians(330), 20)
    cheeks = [circle(-1.0, -0.45, 0.18, 12), circle(1.0, -0.45, 0.18, 12)]
    return make("Sun Wearing Sunglasses", [face, smile] + rays + glasses + cheeks)


@design("beach_tote_bag", T)
def tote_bag(rng):
    bag = poly((-2.0, 0.8), (2.0, 0.8), (1.6, -2.6), (-1.6, -2.6))
    handles = [chain(quad((-1.3, 0.8), (-1.2, 2.6), (-0.3, 0.8), 20)), chain(quad((0.3, 0.8), (1.2, 2.6), (1.3, 0.8), 20))]
    stripes = [[(-2.0 + 0.4 * f, 0.8 - 3.4 * f), (2.0 - 0.4 * f, 0.8 - 3.4 * f)] for f in (0.12, 0.2)]
    towel = chain(quad((-1.6, 0.8), (-1.5, 1.6), (-0.8, 1.7), 10), quad((-0.8, 1.7), (-0.4, 1.4), (-0.3, 0.8), 10))
    towel_lines = [[(-1.4, 0.9), (-1.25, 1.45)], [(-1.05, 0.9), (-0.95, 1.55)]]
    bottle = [rect(0.6, 0.8, 1.2, 1.8), rect(0.7, 1.8, 1.1, 2.05)]
    st = small_star(0, -1.2, 1.1)
    st_c = circle(0, -1.2, 0.18, 12)
    return make("Beach Tote Bag", [bag, towel, st, st_c] + handles + stripes + towel_lines + bottle)


@design("beach_ice_cream_cone", T)
def ice_cream_cone(rng):
    cone = poly((-1.2, 0.2), (0, -2.9), (1.2, 0.2))
    lat = []
    for k in range(-3, 4):
        for s in (1, -1):
            p, q = (k * 0.5 - 2.0 * s, 0.2 - 4), (k * 0.5 + 2.0 * s, 0.2 + 4)
            # clip to triangle by sampling
            pts = [(p[0] + (q[0] - p[0]) * i / 400, p[1] + (q[1] - p[1]) * i / 400) for i in range(401)]
            inside = [pt for pt in pts if pt[1] < 0.15 and pt[1] > -2.8 and abs(pt[0]) < 1.15 * (pt[1] + 2.9) / 3.1]
            if len(inside) > 20:
                lat.append([inside[0], inside[-1]])
    scoop1 = chain([(-1.35, 0.25)], smooth([(-1.35, 0.25), (-1.6, 0.9), (-1.0, 1.7), (0, 1.8), (1.0, 1.7), (1.6, 0.9), (1.35, 0.25)], 8),
                   smooth([(1.35, 0.25), (1.0, 0.0), (0.7, -0.5), (0.4, 0.0), (-0.3, 0.05), (-0.7, -0.3), (-1.0, 0.05), (-1.35, 0.25)], 6))
    scoop2 = smooth([(-1.05, 1.75), (-1.2, 2.4), (-0.6, 3.1), (0.3, 3.2), (1.0, 2.8), (1.15, 2.1), (0.95, 1.75)], 8)
    cherry = [circle(0.2, 3.5, 0.3, 20), quad((0.25, 3.8), (0.4, 4.2), (0.8, 4.3), 8)]
    sprinkles = [[(x, y), (x + 0.15, y + 0.1)] for x, y in [(-0.6, 2.4), (0.3, 2.6), (0.5, 2.0), (-0.3, 1.0), (0.7, 1.1), (-0.9, 0.9)]]
    return make("Beach Ice Cream Cone", [cone, scoop1, scoop2] + lat + cherry + sprinkles)


@design("beach_footprints", T)
def footprints(rng):
    def foot(x, y, rot, left):
        sole = smooth([(0, 0.7), (0.32, 0.5), (0.3, 0.0), (0.2, -0.4), (0.1, -0.7), (-0.15, -0.7), (-0.25, -0.3), (-0.2, 0.1), (-0.3, 0.5)], 8, True)
        toes = [circle(-0.24 + 0.15 * k, 0.9 - 0.05 * abs(k - 1), 0.13 - 0.015 * k, 12) for k in range(4)]
        out = [sole] + toes
        if left:
            out = mirror_all(out)
        return [transform(p, dx=x, dy=y, rot=rot, s=0.78) for p in out]
    fp = []
    for k in range(4):
        side = 0.33 if k % 2 else -0.33
        x, y = -2.3 + 0.7 * k + 0.88 * side, -2.4 + 1.28 * k - 0.48 * side
        fp += foot(x, y, -0.5, k % 2 == 0)
    sea_ = [sea(2.2, waves=5, amp=0.12), sea(2.8, waves=4, amp=0.1)]
    st = star(2.0, -1.2, 0.6, 5, 0.45, rot=0.2)
    shell = scallop(1.0, -2.8, 0.45, 0.0)
    return make("Footprints in the Sand", fp + sea_ + [st] + shell)


@design("beach_tide_pool", T)
def tide_pool(rng):
    pts = []
    for k in range(18):
        a = k * 2 * math.pi / 18
        r = 1.0 + (0.08 if k % 2 else -0.04)
        pts.append((3.0 * r * math.cos(a), 0.15 + 2.2 * r * math.sin(a)))
    rocks = smooth(pts, 6, True)
    pool = smooth([(-2.4, -0.2), (-2.0, 0.8), (-1.0, 1.1), (0.2, 0.9), (1.6, 1.2), (2.3, 0.6), (2.3, -0.5), (1.6, -1.2), (0.4, -1.5),
                   (-1.0, -1.3), (-2.0, -1.0)], 8, True)
    st = star(-1.1, -0.2, 0.65, 5, 0.42, 0.3)
    anem = [circle(1.2, -0.2, 0.25, 16)] + [lens((1.2 + 0.25 * math.cos(a), -0.2 + 0.25 * math.sin(a)), (1.2 + 0.62 * math.cos(a), -0.2 + 0.62 * math.sin(a)), 0.25)
                                             for a in [k * math.pi / 4 for k in range(8)]]
    fish = [lens((-0.2, 0.55), (0.6, 0.55), 0.3), poly((-0.2, 0.55), (-0.45, 0.75), (-0.45, 0.35))]
    snail = [spiral(2.0, 1.9, 0.04, 0.32, 2, 40), [(1.65, 1.6), (2.4, 1.6)]]
    pebbles = [ellipse(-0.3, -0.95, 0.25, 0.12, 14), ellipse(0.25, -1.1, 0.18, 0.1, 12)]
    return make("Rocky Tide Pool", [rocks, pool, st] + anem + fish + snail + pebbles)


@design("beach_rowboat", T)
def rowboat(rng):
    hull = chain([(-2.8, 0.2)], quad((-2.8, 0.2), (-2.2, -1.5), (-0.4, -1.6), 20), [(1.6, -1.6)], quad((1.6, -1.6), (2.8, -1.2), (3.1, 0.5), 20))
    rim = chain(quad((-2.8, 0.2), (0.0, -0.1), (3.1, 0.5), 30))
    rim2 = quad((-2.6, 0.0), (0.0, -0.35), (2.95, 0.25), 30)
    planks = [quad((-2.6, -0.5), (0.0, -1.0), (2.9, -0.4), 30), quad((-2.3, -1.1), (0.0, -1.35), (2.4, -1.0), 30)][:1]
    oar = [tube([(-1.0, 0.1), (1.4, 2.3)], 0.14, True), lens((1.3, 2.2), (2.1, 3.0), 0.25)]
    seat = [[(-0.6, 0.0), (-0.6, 0.35)], [(0.8, 0.1), (0.8, 0.45)]]
    rope = cubic((-2.8, 0.2), (-3.2, -0.6), (-3.0, -1.4), (-2.6, -2.2), 20)
    anchor_ring = circle(-2.6, -2.35, 0.15, 12)
    sand = [sea(-1.75, x0=-1.6, x1=3.2, amp=0.05, waves=3), sea(-2.8, amp=0.05, waves=4)]
    water = [sea(2.0, -3.2, -1.2, waves=2, amp=0.1), sea(1.5, -3.2, -1.9, waves=1.5, amp=0.08)]
    return make("Rowboat on the Shore", [hull, rim, rim2, rope, anchor_ring] + planks + oar + seat + sand + water)


@design("beach_jet_ski", T)
def jet_ski(rng):
    hull = chain([(-2.7, -0.2), (-2.5, -1.0), (0.9, -1.0)], quad((0.9, -1.0), (2.4, -0.7), (3.1, 0.35), 12), [(1.9, 0.35), (-2.7, -0.2)])
    cowl = smooth([(0.2, 0.25), (0.9, 0.9), (1.8, 1.0), (2.6, 0.7), (3.05, 0.35)], 8)
    seat = rrect(-2.3, -0.1, 0.4, 0.4, 0.2)
    seat = transform(seat, rot=0.08, dx=0.0, dy=0.0)
    stripe = [[(-2.55, -0.6), (1.6, -0.6)]]
    column = tube([(1.1, 0.9), (0.75, 1.75)], 0.22, cap=False)
    bars = [rrect(0.3, 1.75, 1.3, 1.95, 0.08)]
    vent = [[(2.0, 0.3), (2.4, 0.6)]]
    spray = [quad((-2.6, -0.9), (-3.3, -0.2), (-3.2, 0.7), 10), quad((-2.6, -0.6), (-2.95, -0.1), (-2.85, 0.45), 10)]
    drops = [circle(-3.0, 1.1, 0.12, 10), circle(-2.6, 0.95, 0.1, 10), circle(-3.4, 1.15, 0.1, 10)]
    water = [sea(-1.25, waves=6, amp=0.12), sea(-2.0, waves=5, amp=0.1), sea(-2.7, waves=4, amp=0.08)]
    return make("Jet Ski", [hull, cowl, seat, column] + stripe + bars + vent + spray + drops + water)


@design("beach_tropical_island", T)
def tropical_island(rng):
    sunset = arc(0, -0.6, 2.0, 0, math.pi, 60)
    rays = [[(2.3 * math.cos(a), -0.6 + 2.3 * math.sin(a)), (2.9 * math.cos(a), -0.6 + 2.9 * math.sin(a))] for a in [math.radians(d) for d in (15, 40, 65, 90, 115, 140, 165)]]
    island = chain([(-3.0, -0.6)], quad((-3.0, -0.6), (-1.6, 0.3), (-0.6, -0.6), 20))
    tr = tube(quad((-1.9, -0.25), (-1.9, 0.9), (-1.3, 1.9), 20), lambda t: 0.3 - 0.12 * t, cap=False)
    leaves = [frond(-1.3, 1.9, math.radians(a), 1.1, 0.4, 0.2) for a in (15, 60, 110, 160, 200)]
    horizon = [[(-0.6, -0.6), (3.2, -0.6)]]
    reflect = [[(-1.0 + 0.3 * k, -1.1 - 0.4 * k), (1.0 - 0.3 * k, -1.1 - 0.4 * k)] for k in range(3)]
    water = [sea(-2.6, waves=6, amp=0.08)]
    birds = [gull(1.3, 2.2, 0.35), gull(2.2, 1.6, 0.25)]
    return make("Tropical Island Sunset", [sunset, island, tr] + rays + leaves + horizon + reflect + water + birds)


@design("beach_hermit_crab", T)
def hermit_crab(rng):
    shell = smooth([(-2.4, -0.6), (-2.6, 0.6), (-1.8, 1.8), (-0.4, 2.3), (0.9, 1.6), (1.1, 0.4), (0.8, -0.6)], 8)
    shell = chain(shell, [(-2.4, -0.6)])  # open bottom closed by a straight edge
    sp = spiral(-0.8, 0.9, 0.1, 1.1, 1.6, 90, rot=0.3)
    body = smooth([(0.7, -0.6), (1.1, 0.0), (1.8, 0.2), (2.2, -0.3), (1.9, -0.9), (1.0, -1.0)], 8)
    stalks = [[(1.7, 0.15), (1.8, 1.0)], [(2.0, 0.0), (2.4, 0.8)]]
    eyes_ = [circle(1.8, 1.2, 0.2, 16), circle(2.45, 1.0, 0.2, 16)]
    claw = [lens((2.0, -0.6), (3.0, -0.3), 0.3), lens((2.0, -0.7), (2.9, -1.0), 0.2)]
    legs_ = [[(x, -0.9), (x + 0.5, -1.4), (x + 0.6, -2.15)] for x in (0.9, 1.4, 1.9)]
    sand = [sea(-2.2, amp=0.06, waves=4)]
    return make("Hermit Crab in a Shell", [shell, sp, body] + stalks + eyes_ + claw + legs_ + sand, [eye(1.8, 1.2, 0.09), eye(2.45, 1.0, 0.09)])
