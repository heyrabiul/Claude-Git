"""Boats & Ships niche, part 2."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "ships"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


def R(d):
    return math.radians(d)


def sea(y=-1.6, x0=-3.6, x1=3.6, amp=0.12, waves=6):
    return wave(x0, x1, y, amp, waves, 120)


def span(pts, y):
    """Horizontal chord of a closed outline at height y -> [(xmin, y), (xmax, y)]."""
    xs = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
            xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
    return [(min(xs), y), (max(xs), y)] if len(xs) >= 2 else []


def vspan(pts, x):
    ys = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if (x0 - x) * (x1 - x) <= 0 and x0 != x1:
            ys.append(y0 + (x - x0) * (y1 - y0) / (x1 - x0))
    return [(x, min(ys)), (x, max(ys))] if len(ys) >= 2 else []


def portholes(x0, x1, y, n, r=0.12):
    return [circle(x0 + (x1 - x0) * k / max(1, n - 1), y, r, 14) for k in range(n)]


def windows(x0, x1, y0, y1, n, gap=0.12):
    w = (x1 - x0 - gap * (n - 1)) / n
    return [rect(x0 + k * (w + gap), y0, x0 + k * (w + gap) + w, y1) for k in range(n)]


def gull(x, y, s):
    return chain(quad((x - s, y), (x - s / 2, y + s * 0.6), (x, y), 8), quad((x, y), (x + s / 2, y + s * 0.6), (x + s, y), 8))


def flag(x, y, w=0.5, h=0.3):
    return poly((x, y), (x + w, y - h / 2), (x, y - h), closed=False)


def person(x, y, s=1.0, hat=None):
    """Simple seated/standing upper body: head at (x, y)."""
    out = [circle(x, y, 0.2 * s, 16), poly((x - 0.22 * s, y - 0.22 * s), (x - 0.3 * s, y - 0.8 * s), (x + 0.3 * s, y - 0.8 * s), (x + 0.22 * s, y - 0.22 * s), closed=False)]
    if hat == "brim":
        out.append(ellipse(x, y + 0.15 * s, 0.35 * s, 0.07 * s, 16))
    elif hat == "cone":
        out.append(poly((x - 0.42 * s, y + 0.08 * s), (x, y + 0.45 * s), (x + 0.42 * s, y + 0.08 * s)))
    return out


def sq_sail(x, yb, yt, w, bulge=0.22):
    """Square sail hanging from a yard: straight top, bellied bottom."""
    return chain([(x - w, yt), (x + w, yt), (x + 1.08 * w, yb)], quad((x + 1.08 * w, yb), (x, yb - bulge), (x - 1.08 * w, yb), 14), [(x - w, yt)])


# --------------------------------------------------------------- sailing craft


@design("ships_sloop", T)
def sloop(rng):
    hull = chain([(-2.6, -0.6), (2.9, -0.4)], cubic((2.9, -0.4), (2.2, -1.3), (-1.0, -1.45), (-2.5, -1.1), 24), [(-2.6, -0.6)])
    stripe = quad((-2.5, -0.85), (0, -1.0), (2.6, -0.65))
    mast = [(-0.2, -0.55), (-0.2, 3.3)]
    main = chain([(-0.35, 3.1)], quad((-0.35, 3.1), (-1.5, 1.4), (-2.4, -0.15), 20), [(-0.35, -0.15), (-0.35, 3.1)])
    jib = chain([(-0.05, 2.9)], quad((-0.05, 2.9), (1.9, 1.5), (2.65, -0.25), 20), [(-0.05, -0.2), (-0.05, 2.9)])
    boom = [(-0.2, -0.3), (-2.6, -0.3)]
    battens = [span(main, y) for y in (0.6, 1.4, 2.2)]
    fl = flag(-0.2, 3.3)
    sun = circle(2.6, 2.6, 0.5, 30)
    return make("Sloop Under Sail", [hull, stripe, mast, main, jib, boom, fl, sun, sea(-1.3), sea(-1.9, amp=0.1, waves=5),
                                     gull(1.4, 3.0, 0.3), gull(2.0, 3.4, 0.25)] + battens)


@design("ships_clipper", T)
def clipper(rng):
    hull = chain([(-3.0, -0.3), (2.8, -0.3)], quad((2.8, -0.3), (2.5, -1.4), (1.5, -1.5), 14), [(-2.6, -1.5), (-3.0, -0.3)])
    sprit = [(2.8, -0.3), (3.9, 0.4)]
    ports = portholes(-2.3, 2.0, -0.9, 9, 0.11)
    masts, sails = [], []
    for x, h, w in [(-1.8, 3.4, 0.8), (0.1, 3.9, 0.9), (1.9, 3.3, 0.75)]:
        masts.append([(x, -0.3), (x, h)])
        tiers = [(0.15, 1.1), (1.25, 2.05), (2.2, 2.85)] + ([(2.95, 3.45)] if h > 3.5 else [])
        for k, (yb, yt) in enumerate(tiers):
            sails.append(sq_sail(x, yb, yt, w * (1 - 0.13 * k), 0.15))
        sails.append(flag(x, h, 0.45, 0.25))
    jibs = [poly((1.95, 2.9), (3.8, 0.45), (2.1, 0.4)), poly((2.0, 3.2), (3.4, 2.0), (2.6, 1.7), closed=False)]
    rail = [quad((-3.0, -0.3), (0, -0.45), (2.8, -0.3))]
    return make("Clipper Ship", [hull, sprit] + ports + masts + sails + jibs + [sea(-1.6), sea(-2.2, amp=0.1, waves=5)])


@design("ships_viking", T)
def viking(rng):
    hull = chain(cubic((-3.0, 0.5), (-2.4, -1.4), (2.4, -1.4), (3.0, 0.5), 50), quad((3.0, 0.5), (0, -0.6), (-3.0, 0.5), 50))
    prow = chain([(3.0, 0.5)], cubic((3.0, 0.5), (3.6, 1.3), (2.9, 1.9), (3.25, 2.4), 20), [(3.75, 2.45), (3.8, 2.22), (3.45, 2.12), (3.55, 1.9), (3.3, 1.95)],
                 cubic((3.3, 1.95), (3.2, 1.5), (3.3, 1.1), (2.8, 0.4), 16))
    stern = spiral(-3.0, 1.15, 0.05, 0.6, 1.15, 50, rot=R(250))
    shields = []
    for k in range(7):
        x = -2.1 + 0.7 * k
        y = -0.15 - 0.15 * math.cos(math.pi * (x / 3.0)) * 0
        y = 0.5 - 1.1 * (1 - (x / 3.0) ** 2) * 0.55 - 0.05
        shields += [circle(x, y, 0.28, 20), circle(x, y, 0.08, 10)]
    mast = [(0, 0.0), (0, 3.6)]
    sail = chain([(-1.6, 3.3), (1.6, 3.3), (1.8, 1.0)], quad((1.8, 1.0), (0, 0.7), (-1.8, 1.0), 20), [(-1.6, 3.3)])
    stripes = [vspan(sail, x) for x in (-1.0, -0.4, 0.4, 1.0)]
    oars = [[(x, -0.75), (x - 0.5, -1.7)] for x in (-1.8, -1.1, -0.4, 0.3, 1.0, 1.7)]
    return make("Viking Longship", [hull, prow, stern, mast, sail, sea(-1.5)] + shields + stripes + oars, [eye(3.5, 2.3, 0.05)])


@design("ships_junk", T)
def junk(rng):
    hull = poly((-3.3, 0.7), (-2.9, -0.2), (2.6, -0.2), (3.1, 0.3), (2.5, -1.1), (-2.6, -1.1))
    rail = [(-2.9, -0.2), (-3.1, 0.7)]
    cabin = rect(-2.6, -0.2, -1.4, 0.5)
    sails, masts = [], []
    for x, yb, yt, w in [(-1.5, 0.2, 3.3, 1.5), (0.6, 0.0, 3.8, 1.6), (2.3, 0.2, 2.6, 0.9)]:
        masts.append([(x, -0.2), (x, yt + 0.3)])
        s = chain([(x - 0.3 * w, yb), (x - 0.15 * w, yt)], quad((x - 0.15 * w, yt), (x + 0.3 * w, yt + 0.35), (x + 0.65 * w, yt + 0.05), 12),
                  quad((x + 0.65 * w, yt + 0.05), (x + 1.15 * w, (yt + yb) / 2), (x + w, yb), 20), [(x - 0.3 * w, yb)])
        sails.append(s)
        n = 5 if w > 1 else 3
        for k in range(1, n):
            sp = span(s, yb + (yt - yb) * k / n)
            if sp:
                sails.append(sp)
    eye_ = circle(2.3, -0.55, 0.18, 16)
    return make("Chinese Junk", [hull, rail, cabin, eye_, sea(-1.4), sea(-2.0, amp=0.1, waves=5)] + masts + sails)


@design("ships_dhow", T)
def dhow(rng):
    hull = chain([(-2.8, 0.2), (3.3, 0.5)], quad((3.3, 0.5), (2.4, -1.2), (0.8, -1.3), 16), [(-2.2, -1.3), (-2.8, 0.2)])
    rail = quad((-2.7, -0.05), (0.4, -0.3), (3.1, 0.3))
    stern = rect(-2.8, 0.2, -2.0, 0.6)
    mast = [(0.4, -0.2), (0.6, 2.4)]
    yard = [(-2.8, 0.6), (3.0, 4.0)]
    sail = chain([(-2.6, 0.75)], [(2.85, 3.85)], quad((2.85, 3.85), (2.4, 1.0), (0.9, -0.05), 24), [(-2.6, 0.75)])
    seams = [[(-1.2 + 1.0 * k, 1.4 + 0.6 * k), (-0.6 + 0.7 * k, 0.4 + 0.25 * k)] for k in range(3)]
    return make("Arabian Dhow", [hull, rail, stern, mast, yard, sail, sea(-1.5), sea(-2.1, amp=0.1, waves=5), gull(-2.6, 3.0, 0.3)] + seams)


@design("ships_catamaran", T)
def catamaran(rng):
    front = chain([(-3.0, -0.6), (3.2, -0.6)], quad((3.2, -0.6), (2.6, -1.25), (1.6, -1.3), 12), [(-2.8, -1.3), (-3.0, -0.6)])
    back = poly((-2.7, -0.6), (-2.5, -0.25), (3.3, -0.25), (3.2, -0.6), closed=False)
    beam = [rect(-1.6, -0.25, 1.6, -0.05)]
    mast = [(0.0, -0.05), (0.0, 4.2)]
    main = chain([(-0.15, 4.0), (-1.2, 3.9)], quad((-1.2, 3.9), (-2.1, 1.6), (-2.3, 0.15), 20), [(-0.15, 0.15), (-0.15, 4.0)])
    battens = [span(main, y) for y in (0.9, 1.7, 2.5, 3.3)]
    jib = poly((0.15, 3.3), (2.9, -0.1), (0.15, 0.15))
    windows_ = [poly((-1.8, -0.9), (1.4, -0.9), (1.2, -0.75), (-1.6, -0.75))]
    return make("Sailing Catamaran", [front, back, mast, main, jib, sea(-1.5), sea(-2.1, amp=0.1, waves=5)] + beam + battens + windows_)


@design("ships_dinghy", T)
def dinghy(rng):
    hull = poly((-2.2, -0.4), (2.0, -0.2), (1.8, -1.0), (-1.9, -1.1))
    rail = [(-2.2, -0.55), (2.0, -0.35)]
    mast = [(1.2, -0.3), (1.2, 3.3)]
    sail = poly((1.05, 3.1), (-1.6, 3.6), (-1.4, 0.1), (1.05, 0.1))
    sprit = [(1.2, 0.4), (-1.55, 3.55)]
    sailor = [circle(-2.7, 0.6, 0.25, 18), tube([(-2.6, 0.35), (-1.8, -0.35)], 0.35), [(-1.8, -0.35), (-1.0, -0.55)], [(-2.5, 0.2), (-1.6, 0.0)]]
    cap = arc(-2.7, 0.6, 0.3, R(0), R(180), 10)
    number = [circle(-0.3, 1.9, 0.5, 30)]
    return make("Sailing Dinghy", [hull, rail, mast, sail, sprit, cap, sea(-1.2), sea(-1.8, amp=0.1, waves=5)] + sailor + number)


@design("ships_windsurfer", T)
def windsurfer(rng):
    board = chain(quad((-3.2, -1.2), (0, -1.55), (3.0, -1.15), 30), quad((3.0, -1.15), (3.3, -0.95), (2.9, -0.9), 6), [(-3.1, -0.95), (-3.2, -1.2)])
    mast = [(0.6, -1.0), (1.4, 3.4)]
    sail = chain([(1.4, 3.4)], quad((1.4, 3.4), (-1.6, 2.4), (-1.9, -0.5), 30), [(0.65, -0.95)])
    boom = [ellipse(-0.3, 0.9, 1.5, 0.15, 40, rot=R(-8))]
    panels = [[(1.15, 2.0), (-1.25, 1.95)], [(0.8, 0.4), (-1.7, 0.6)]]
    rider = [circle(1.6, 1.6, 0.25, 18), tube([(1.65, 1.3), (1.9, 0.1)], 0.4), tube([(1.85, 0.0), (1.4, -0.95)], 0.2), tube([(1.95, 0.0), (2.3, -0.95)], 0.2),
             [(1.65, 1.1), (1.0, 0.95)], [(1.75, 0.8), (0.7, 0.8)]]
    spray = [quad((3.1, -1.0), (3.5, -0.2), (3.8, -0.6)), quad((-3.2, -1.1), (-3.6, -0.6), (-3.8, -1.0))]
    return make("Windsurfer", [board, mast, sail, sea(-1.6), sea(-2.2, amp=0.1, waves=5)] + boom + panels + rider + spray)


@design("ships_outrigger", T)
def outrigger(rng):
    hull = chain(quad((-3.4, -0.2), (0, -1.3), (3.4, -0.2), 30), quad((3.4, -0.2), (0, -0.45), (-3.4, -0.2), 30))
    ama = chain(quad((-2.6, 0.3), (-0.6, 0.05), (1.4, 0.3), 20), quad((1.4, 0.3), (-0.6, 0.6), (-2.6, 0.3), 20))
    iakos = [quad((-1.8, -0.5), (-2.0, 0.2), (-1.7, 0.4)), quad((0.6, -0.55), (0.4, 0.2), (0.7, 0.42))]
    spars = [quad((1.3, -0.4), (0.0, 1.4), (-0.4, 3.4), 24), quad((1.3, -0.4), (2.6, 1.0), (3.4, 2.9), 24)]
    top = quad((-0.4, 3.4), (1.3, 1.9), (3.4, 2.9), 24)
    mast = [(1.3, -0.5), (1.6, 1.4)]
    paddler = person(-1.0, 0.45, 0.8, hat="brim") + [[(-1.2, 0.1), (-2.2, -1.4)], lens((-2.2, -1.4), (-2.5, -1.9), 0.35)]
    return make("Outrigger Canoe", [hull, ama, mast, top, sea(-1.3), sea(-1.9, amp=0.1, waves=5)] + iakos + spars + paddler)


@design("ships_raft", T)
def raft(rng):
    logs = [rrect(-3.0, -1.0 + 0.0, 3.0, -0.6, 0.2), rrect(-3.2, -0.6, 2.8, -0.2, 0.2)]
    ends = [circle(-3.0, -0.8, 0.2, 16)]
    ties = [[(x, -1.0), (x + 0.15, -0.2)] for x in (-2.2, 0.0, 2.0)]
    mast = [(0.0, -0.2), (0.0, 3.4)]
    sail = chain([(-1.4, 3.1), (1.4, 3.1), (1.5, 0.8)], quad((1.5, 0.8), (0, 0.55), (-1.5, 0.8), 14), [(-1.4, 3.1)])
    patches = [rect(-0.9, 2.0, -0.3, 2.6), rect(0.4, 1.0, 1.0, 1.5)]
    yards = [[(-1.6, 3.1), (1.6, 3.1)], [(-1.7, 0.75), (1.7, 0.75)]]
    stays = [[(0.0, 3.4), (-2.8, -0.2)], [(0.0, 3.4), (2.6, -0.2)]]
    paddle = [[(2.4, 0.6), (3.4, -1.3)], lens((3.4, -1.3), (3.7, -1.9), 0.35)]
    box = rect(-2.6, -0.2, -1.8, 0.4)
    return make("Log Raft", logs + ends + ties + [mast, sail] + patches + yards + stays + paddle + [box, sea(-1.2), sea(-1.8, amp=0.1, waves=5)])


# --------------------------------------------------------------- paddle & oar


@design("ships_gondola", T)
def gondola(rng):
    hull = chain(cubic((-3.5, 0.9), (-2.4, -0.9), (2.0, -1.0), (3.3, 1.5), 50), cubic((3.3, 1.5), (2.3, -0.1), (-2.2, -0.15), (-3.5, 0.9), 50))
    ferro = [poly((3.3, 1.5), (3.6, 1.5), (3.5, 2.3), (3.25, 2.3), closed=False)] + [[(3.5, y), (3.75, y)] for y in (1.65, 1.85, 2.05)]
    seat = [rrect(-0.6, -0.25, 0.8, 0.35, 0.15), [(-0.6, 0.35), (-0.6, 0.8)]]
    g = [circle(-2.2, 2.0, 0.22, 16), ellipse(-2.2, 2.2, 0.4, 0.07, 16), rect(-2.45, 0.8, -1.95, 1.75)] + [[(-2.45, y), (-1.95, y)] for y in (1.0, 1.25, 1.5)] + \
        [[(-2.35, 0.8), (-2.4, -0.05)], [(-2.05, 0.8), (-2.0, -0.05)]]
    oar = [[(-1.95, 1.5), (-1.6, 1.5)], [(-1.6, 1.5), (-0.6, -1.4)], lens((-0.6, -1.4), (-0.4, -2.0), 0.3), [(-2.45, 1.5), (-1.6, 1.6)]]
    poles = [[(x, -1.8), (x, 2.0)] for x in (1.7, 2.1)] + [circle(x, 2.1, 0.12, 10) for x in (1.7, 2.1)]
    return make("Venetian Gondola", [hull, sea(-1.2), sea(-1.8, amp=0.1, waves=5)] + ferro + seat + g + oar + poles)


@design("ships_kayak", T)
def kayak(rng):
    hull = chain(quad((-3.5, -0.4), (0, -1.3), (3.5, -0.4), 40), quad((3.5, -0.4), (0, 0.05), (-3.5, -0.4), 40))
    rim = ellipse(-0.1, -0.12, 0.8, 0.18, 30)
    body = poly((-0.5, -0.1), (-0.45, 1.0), (0.4, 1.0), (0.35, -0.1), closed=False)
    vest = [[(-0.45, 0.6), (0.4, 0.6)], [(0, 1.0), (0, 0.1)]]
    head = circle(-0.05, 1.4, 0.32, 24)
    helmet = chain(arc(-0.05, 1.45, 0.4, R(-10), R(190), 16))
    paddle = [[(-2.3, -0.6), (2.0, 2.1)], lens((-2.3, -0.6), (-2.9, -1.0), 0.3), lens((2.0, 2.1), (2.6, 2.5), 0.3)]
    arms = [[(-0.45, 0.85), (-0.7, 0.4)], [(0.4, 0.85), (0.9, 1.0)]]
    splash = [quad((-2.6, -1.1), (-3.0, -0.6), (-3.2, -1.0)), quad((-2.2, -1.1), (-2.2, -0.6), (-1.8, -0.8))]
    return make("Sea Kayak", [hull, rim, body, head, helmet, sea(-0.9), sea(-1.6, amp=0.1, waves=5)] + vest + paddle + arms + splash)


@design("ships_rowing_eight", T)
def rowing_eight(rng):
    hull = chain(quad((-3.8, -0.3), (0, -0.75), (3.8, -0.3), 40), quad((3.8, -0.3), (0, -0.15), (-3.8, -0.3), 40))
    rowers, oars = [], []
    for k in range(8):
        x = -2.6 + 0.65 * k
        rowers += [circle(x, 0.55, 0.15, 12), [(x, 0.4), (x - 0.12, -0.2)]]
        if k % 2:
            oars.append([(x - 0.05, 0.05), (x - 0.75, -1.2)])
        else:
            oars.append([(x - 0.05, 0.05), (x + 0.35, -1.25)])
        oars.append(lens(oars[-1][1], (oars[-1][1][0] + (0.15 if k % 2 == 0 else -0.25), oars[-1][1][1] - 0.35), 0.3))
    cox = [circle(2.9, 0.25, 0.15, 12), [(2.9, 0.1), (2.85, -0.25)]]
    return make("Rowing Eight", [hull, sea(-1.0, amp=0.08, waves=8), sea(-1.9, amp=0.1, waves=6)] + rowers + oars + cox)


@design("ships_dragon_boat", T)
def dragon_boat(rng):
    hull = chain(quad((-3.2, 0.1), (0, -1.1), (3.0, -0.1), 40), [(-3.2, 0.1)])
    head = chain([(3.0, -0.1)], cubic((3.0, -0.1), (3.5, 0.6), (3.0, 1.0), (3.3, 1.4), 16), [(3.9, 1.3), (3.95, 1.05), (3.6, 1.0), (3.75, 0.75), (3.35, 0.7)],
                 quad((3.35, 0.7), (3.3, 0.2), (2.8, -0.2), 10))
    horns = [[(3.35, 1.4), (3.1, 1.9)], [(3.5, 1.38), (3.45, 1.9)]]
    tail = chain([(-3.2, 0.1)], cubic((-3.2, 0.1), (-3.5, 0.6), (-3.8, 0.8), (-3.5, 1.4), 16), [(-3.3, 1.0), (-3.0, 0.9)], quad((-3.0, 0.9), (-3.0, 0.3), (-2.7, -0.15), 10))
    scales = [arc(x, -0.55, 0.2, R(180), R(360), 8) for x in (-2.0, -1.4, -0.8, -0.2, 0.4, 1.0, 1.6)]
    crew = []
    for k in range(6):
        x = -2.0 + 0.7 * k
        crew += person(x, 0.65, 0.65)
        crew += [[(x + 0.15, 0.35), (x - 0.4, -1.3)], lens((x - 0.4, -1.3), (x - 0.5, -1.7), 0.35)]
    drum = [rect(2.15, -0.1, 2.65, 0.35)] + person(2.6, 0.85, 0.6)
    steer = person(-2.7, 1.0, 0.65) + [[(-2.7, 0.6), (-3.6, -1.0)]]
    return make("Dragon Boat Race", [hull, head, tail, sea(-1.3), sea(-1.9, amp=0.1, waves=5)] + horns + scales + crew + drum + steer, [eye(3.55, 1.2, 0.06)])


@design("ships_sampan", T)
def sampan(rng):
    hull = chain(quad((-3.3, 0.4), (-1.0, -1.2), (3.0, -0.6), 40), [(3.3, 0.0)], quad((3.3, 0.0), (0, -0.25), (-3.3, 0.4), 30))
    roof = chain([(-1.6, -0.35)], arc(0.0, -0.35, 1.6, math.pi, 0, 30), [(1.6, -0.35)])
    roof2 = arc(0.0, -0.35, 1.35, math.pi, 0, 26)
    ribs = [[(1.35 * math.cos(a), -0.35 + 1.35 * math.sin(a)), (1.6 * math.cos(a), -0.35 + 1.6 * math.sin(a))] for a in (R(30), R(60), R(90), R(120), R(150))]
    weave = [quad((-1.2, 0.2 + 0.35 * k), (0, 0.32 + 0.35 * k), (1.2, 0.2 + 0.35 * k)) for k in range(2)]
    boatman = person(-2.5, 1.6, 1.0, hat="cone") + [[(-2.65, 0.8), (-2.7, 0.0)], [(-2.35, 0.8), (-2.3, 0.05)]]
    oar = [[(-2.2, 1.2), (-3.6, -1.2)], lens((-3.6, -1.2), (-3.8, -1.7), 0.35)]
    return make("Sampan", [hull, roof, roof2, sea(-1.0), sea(-1.6, amp=0.1, waves=5)] + ribs + weave + boatman + oar)


@design("ships_swan_boat", T)
def swan_boat(rng):
    body = chain([(1.5, 0.0)], cubic((1.5, 0.0), (2.0, -1.4), (-2.0, -1.6), (-3.0, -0.2), 40), [(-2.6, 0.4), (-3.1, 0.9), (-2.2, 0.6)],
                 quad((-2.2, 0.6), (-1.0, 0.0), (0.8, 0.2), 12))
    neck = chain([(0.8, 0.2)], cubic((0.8, 0.2), (1.6, 1.6), (0.6, 2.4), (1.2, 3.0), 30), arc(1.5, 2.95, 0.3, R(180), R(10), 12), [(2.3, 2.75), (1.8, 2.75)],
                 cubic((1.75, 2.8), (1.0, 2.6), (2.1, 1.4), (1.5, 0.0), 30))
    wing = chain([(-1.9, 0.5)], quad((-1.9, 0.5), (-1.0, 1.6), (0.4, 0.9), 16), quad((0.4, 0.9), (-0.4, -0.4), (-1.6, -0.3), 16), [(-1.9, 0.5)])
    feathers = [quad((-1.5, 0.3), (-0.8, 0.8), (-0.1, 0.6)), quad((-1.2, -0.05), (-0.6, 0.35), (0.0, 0.3))]
    seat = [person(-0.6, 1.5, 0.9)[0], person(-0.6, 1.5, 0.9)[1]]
    reeds = [[(3.0, -1.4), (3.1, 0.8)], [(3.3, -1.4), (3.5, 0.4)], ellipse(3.1, 1.0, 0.1, 0.3, 12), ellipse(3.52, 0.6, 0.1, 0.28, 12)]
    return make("Swan Pedal Boat", [body, neck, wing, sea(-1.2, amp=0.08), sea(-1.8, amp=0.08, waves=5)] + feathers + seat + reeds, [eye(1.6, 2.95, 0.06)])


@design("ships_paddleboard", T)
def paddleboard(rng):
    board = chain(quad((-3.0, -1.2), (0, -1.45), (3.2, -1.15), 30), quad((3.2, -1.15), (3.4, -1.0), (3.0, -0.95), 6), [(-3.0, -0.95), (-3.0, -1.2)])
    head = circle(0.2, 2.5, 0.3, 24)
    hair = chain(arc(0.2, 2.5, 0.36, R(10), R(200), 14), [(-0.25, 2.1)])
    torso = poly((-0.05, 2.15), (-0.2, 1.0), (0.55, 1.0), (0.45, 2.15), closed=False)
    legs_ = [tube([(0.0, 1.0), (-0.25, -0.95)], 0.28), tube([(0.45, 1.0), (0.75, -0.95)], 0.28)]
    arms = [[(0.45, 2.0), (1.2, 2.3)], [(-0.05, 2.0), (0.9, 1.2)]]
    paddle = [[(1.3, 2.7), (2.2, -1.3)], lens((2.2, -1.3), (2.35, -2.0), 0.3), [(1.15, 2.75), (1.45, 2.65)]]
    sun = [arc(-2.0, -1.6, 1.2, R(0), R(180), 30)] + [[(-2.0 + 1.4 * math.cos(R(a)), -1.6 + 1.4 * math.sin(R(a))), (-2.0 + 1.8 * math.cos(R(a)), -1.6 + 1.8 * math.sin(R(a)))] for a in (30, 60, 90, 120, 150)]
    return make("Stand-Up Paddleboard", [board, head, hair, torso, sea(-1.6), sea(-2.2, amp=0.1, waves=5)] + legs_ + arms + paddle + sun)


# --------------------------------------------------------------- working boats


@design("ships_trawler", T)
def trawler(rng):
    hull = chain([(-3.0, -0.2), (2.4, 0.0), (3.1, 0.7)], quad((3.1, 0.7), (2.8, -1.3), (1.6, -1.4), 14), [(-2.6, -1.4), (-3.0, -0.2)])
    house = [rect(0.4, 0.0, 2.0, 1.3), poly((0.3, 1.3), (2.1, 1.3), (1.9, 1.55), (0.5, 1.55))] + windows(0.6, 1.8, 0.65, 1.05, 3)
    mast = [(1.0, 1.55), (1.0, 3.2)]
    booms = [[(1.0, 2.9), (-2.8, 1.6)], [(1.0, 2.9), (3.4, 2.0)]]
    gantry = poly((-2.8, -0.15), (-2.5, 1.8), (-1.9, 1.8), (-1.6, -0.1), closed=False)
    net = [poly((-2.2, 1.6), (-3.4, -1.5), (-1.8, -1.5)), [(-2.6, 0.6), (-2.1, 0.6)], [(-3.0, -0.4), (-2.0, -0.4)], [(-2.6, 0.6), (-2.5, -1.5)], [(-2.3, 1.0), (-2.2, -1.5)]]
    drum = [circle(-0.8, 0.3, 0.32, 20), circle(-0.8, 0.3, 0.12, 10)]
    ports = portholes(-1.8, 1.8, -0.75, 5, 0.12)
    return make("Fishing Trawler", [hull, gantry, sea(-1.6), sea(-2.2, amp=0.1, waves=5), gull(-0.4, 3.0, 0.3), gull(2.4, 3.4, 0.28)] + house + [mast] + booms + net + drum + ports)


@design("ships_lobster_boat", T)
def lobster_boat(rng):
    hull = chain([(-3.2, -0.3), (2.2, -0.1)], quad((2.2, -0.1), (3.3, 0.5), (3.2, 0.3), 6), quad((3.2, 0.3), (2.6, -1.3), (1.4, -1.35), 14), [(-3.0, -1.35), (-3.2, -0.3)])
    cabin = [poly((0.6, -0.1), (0.7, 1.2), (2.0, 1.2), (2.3, -0.05), closed=False), poly((0.5, 1.2), (2.2, 1.2), (2.1, 1.4), (0.6, 1.4))] + windows(0.85, 2.0, 0.6, 1.0, 2)
    traps = []
    for x0, y0 in [(-2.9, -0.3), (-1.9, -0.3), (-2.4, 0.4)]:
        traps.append(rect(x0, y0, x0 + 0.95, y0 + 0.7))
        traps += [[(x0 + 0.95 * f, y0), (x0 + 0.95 * f, y0 + 0.7)] for f in (0.33, 0.66)] + [[(x0, y0 + 0.35), (x0 + 0.95, y0 + 0.35)]]
    buoys = []
    for x, y in [(-0.6, 0.8), (-0.1, 0.6)]:
        b = ellipse(x, y, 0.18, 0.4, 20)
        buoys += [b, span(b, y + 0.1), [(x, y + 0.4), (x, y + 0.65)]]
    mast = [(1.3, 1.4), (1.3, 2.5)]
    radar = rect(1.0, 2.5, 1.6, 2.65)
    stripe = quad((-3.1, -0.65), (0, -0.55), (2.8, -0.4))
    return make("Lobster Boat", [hull, stripe, sea(-1.6), sea(-2.2, amp=0.1, waves=5), radar] + cabin + traps + buoys + [mast])


@design("ships_container_ship", T)
def container_ship(rng):
    hull = chain([(-3.6, -0.2), (3.0, -0.2)], quad((3.0, -0.2), (3.8, -1.0), (3.2, -1.45), 12), [(-3.3, -1.45), (-3.6, -0.2)])
    bulb = arc(3.15, -1.25, 0.3, R(-80), R(80), 10)
    bridge = [rect(-3.3, -0.2, -2.3, 1.9), rect(-3.5, 1.9, -2.1, 2.2)] + windows(-3.2, -2.4, 1.4, 1.7, 3)
    funnel = poly((-2.9, 2.2), (-2.85, 2.8), (-2.45, 2.8), (-2.4, 2.2), closed=False)
    boxes = []
    for col in range(8):
        x0 = -2.05 + col * 0.62
        h = [3, 4, 4, 3, 4, 3, 2, 2][col]
        for r in range(h):
            boxes.append(rect(x0, -0.2 + 0.45 * r, x0 + 0.58, 0.25 + 0.45 * r))
            boxes.append([(x0 + 0.29, -0.15 + 0.45 * r), (x0 + 0.29, 0.2 + 0.45 * r)])
    return make("Container Ship", [hull, bulb, funnel, sea(-1.6), sea(-2.2, amp=0.1, waves=5)] + bridge + boxes)


@design("ships_gas_tanker", T)
def gas_tanker(rng):
    hull = chain([(-3.6, -0.3), (3.2, -0.3)], quad((3.2, -0.3), (3.8, -1.1), (3.2, -1.5), 12), [(-3.3, -1.5), (-3.6, -0.3)])
    domes = []
    for k in range(4):
        x = -1.5 + 1.3 * k
        domes += [arc(x, -0.3, 0.62, 0, math.pi, 30), [(x - 0.62, -0.05), (x + 0.62, -0.05)]]
    deck = [(-2.2, 0.05), (3.0, 0.05)]
    bridge = [rect(-3.4, -0.3, -2.4, 1.6), rect(-3.6, 1.6, -2.2, 1.85)] + windows(-3.3, -2.5, 1.1, 1.4, 3)
    funnel = poly((-3.1, 1.85), (-3.05, 2.45), (-2.65, 2.45), (-2.6, 1.85), closed=False)
    stripe = [(-3.5, -0.8), (3.5, -0.8)]
    mast = [[(3.0, -0.3), (3.0, 1.0)], [(2.8, 0.8), (3.2, 0.8)]]
    return make("Gas Tanker", [hull, deck, funnel, stripe, sea(-1.7), sea(-2.3, amp=0.1, waves=5)] + domes + bridge + mast)


@design("ships_ferry", T)
def ferry(rng):
    hull = poly((-3.4, -0.4), (3.4, -0.4), (3.0, -1.4), (-3.0, -1.4))
    deck1 = rect(-3.0, -0.4, 3.0, 0.6)
    opening = rect(-2.6, -0.3, 2.6, 0.5)
    cars = []
    for x in (-2.0, -0.6, 0.8):
        cars += [chain([(x - 0.5, -0.25), (x - 0.5, 0.0), (x - 0.3, 0.0), (x - 0.15, 0.25), (x + 0.3, 0.25), (x + 0.45, 0.0), (x + 0.55, 0.0), (x + 0.55, -0.25), (x - 0.5, -0.25)]),
                 circle(x - 0.25, -0.25, 0.1, 10), circle(x + 0.3, -0.25, 0.1, 10)]
    deck2 = rect(-2.6, 0.6, 2.6, 1.4)
    wins = windows(-2.4, 2.4, 0.85, 1.2, 8)
    wheel = [rect(-0.8, 1.4, 0.8, 2.0)] + windows(-0.6, 0.6, 1.6, 1.85, 3)
    funnel = poly((1.2, 1.4), (1.3, 2.4), (1.9, 2.4), (2.0, 1.4), closed=False)
    lifeboats = [chain([(x - 0.5, 1.5)], quad((x - 0.5, 1.5), (x, 1.25), (x + 0.5, 1.5), 8), [(x - 0.5, 1.5)]) for x in (-2.0,)]
    ports = portholes(-2.6, 2.6, -0.9, 9, 0.1)
    return make("Car Ferry", [hull, deck1, opening, deck2, funnel, sea(-1.6), sea(-2.2, amp=0.1, waves=5)] + cars + wins + wheel + ports)


@design("ships_sternwheeler", T)
def sternwheeler(rng):
    hull = poly((-2.4, -0.6), (3.4, -0.6), (3.0, -1.2), (-2.2, -1.2))
    d1 = [rect(-2.2, -0.6, 2.6, 0.4), [(-2.4, 0.4), (2.8, 0.4)]]
    d2 = [rect(-1.8, 0.4, 2.0, 1.3), [(-2.0, 1.3), (2.2, 1.3)]]
    posts = [[(x, -0.6), (x, 0.4)] for x in (-1.6, -0.8, 0.0, 0.8, 1.6, 2.3)] + [[(x, 0.4), (x, 1.3)] for x in (-1.2, -0.4, 0.4, 1.2)]
    rails = [[(-2.2, -0.2), (2.6, -0.2)], [(-1.8, 0.75), (2.0, 0.75)]]
    pilot = [rect(0.6, 1.3, 1.6, 1.9), poly((0.5, 1.9), (1.1, 2.2), (1.7, 1.9))]
    stacks = []
    for x in (1.9, 2.4):
        stacks += [rect(x - 0.15, 1.3, x + 0.15, 3.3), zigzag(x - 0.3, x + 0.3, 3.4, 0.1, 3)]
    wheel = [chain(arc(-3.0, -0.8, 1.0, R(-70), R(250), 40)), circle(-3.0, -0.8, 0.25, 16)] + \
            [[(-3.0 + 0.25 * math.cos(a), -0.8 + 0.25 * math.sin(a)), (-3.0 + 1.0 * math.cos(a), -0.8 + 1.0 * math.sin(a))] for a in [R(-60 + 40 * k) for k in range(8)]]
    housing = [arc(-3.0, -0.8, 1.2, R(20), R(160), 20)]
    fl = flag(1.1, 2.7, 0.5, 0.3)
    return make("Sternwheeler Riverboat", [hull, fl, [(1.1, 2.2), (1.1, 2.7)], sea(-1.6), sea(-2.2, amp=0.1, waves=5)] + d1 + d2 + posts + rails + pilot + stacks + wheel + housing)


@design("ships_houseboat", T)
def houseboat(rng):
    hull = rrect(-3.2, -1.2, 3.2, -0.6, 0.25)
    deck = [(-3.2, -0.6), (3.2, -0.6)]
    house = rect(-2.0, -0.6, 1.8, 1.0)
    roof = poly((-2.4, 0.9), (-0.1, 2.3), (2.2, 0.9), (-2.4, 0.9))
    door = rect(-0.4, -0.6, 0.3, 0.6)
    win = [rect(-1.6, -0.1, -0.8, 0.5), rect(0.7, -0.1, 1.5, 0.5), circle(-0.1, 1.35, 0.3, 20)]
    panes = [[(-1.2, -0.1), (-1.2, 0.5)], [(1.1, -0.1), (1.1, 0.5)]]
    rail = [[(-3.1, -0.1), (-2.0, -0.1)], [(1.8, -0.1), (3.1, -0.1)]] + [[(x, -0.6), (x, -0.1)] for x in (-3.0, -2.5, 2.2, 2.65, 3.1)]
    chimney = poly((1.0, 1.4), (1.0, 2.1), (1.4, 2.1), (1.4, 1.2), closed=False)
    smoke = [circle(1.3, 2.5, 0.18, 12), circle(1.6, 2.85, 0.24, 14), circle(2.05, 3.15, 0.3, 16)]
    pots = [poly((x - 0.2, -0.6), (x - 0.25, -0.3), (x + 0.25, -0.3), (x + 0.2, -0.6), closed=False) for x in (2.6,)] + [circle(2.6, -0.1, 0.22, 14)]
    return make("Houseboat", [hull, deck, house, roof, door, chimney, sea(-1.4, amp=0.08), sea(-2.0, amp=0.08, waves=5)] + win + panes + rail + smoke + pots)


@design("ships_fireboat", T)
def fireboat(rng):
    hull = chain([(-3.0, -0.6), (2.6, -0.5), (3.2, -0.1)], quad((3.2, -0.1), (2.8, -1.4), (1.6, -1.45), 12), [(-2.8, -1.45), (-3.0, -0.6)])
    house = [rect(-1.8, -0.55, 1.0, 0.6), rect(-1.2, 0.6, 0.6, 1.3)] + windows(-1.0, 0.4, 0.8, 1.1, 3) + portholes(-1.4, 0.6, 0.0, 4, 0.15)
    towers = [rect(1.5, -0.5, 1.75, 1.6), rect(-2.6, -0.6, -2.35, 0.8)]
    nozzles = [poly((1.5, 1.6), (2.0, 2.0), (2.1, 1.85), (1.75, 1.5), closed=False), poly((-2.35, 0.8), (-2.8, 1.2), (-2.9, 1.05), (-2.6, 0.75), closed=False)]
    jets = [quad((2.05, 1.95), (3.2, 4.0), (3.9, 1.0), 30), quad((2.1, 1.85), (3.4, 3.4), (3.6, 0.2), 30),
            quad((-2.85, 1.15), (-3.6, 3.2), (-3.9, 0.5), 30), quad((-2.85, 1.05), (-3.4, 2.4), (-3.7, -0.2), 30)]
    drops = [circle(x, y, 0.08, 8) for x, y in [(3.7, 0.0), (3.9, -0.3), (-3.8, -0.4), (-3.95, -0.1), (3.5, -0.4)]]
    stripe = quad((-2.9, -0.95), (0, -1.0), (2.9, -0.75))
    return make("Fireboat Spraying Water", [hull, stripe, sea(-1.6), sea(-2.2, amp=0.1, waves=5)] + house + towers + nozzles + jets + drops)


@design("ships_coast_guard", T)
def coast_guard(rng):
    hull = chain([(-3.3, -0.4), (2.4, -0.3), (3.3, 0.2)], quad((3.3, 0.2), (2.9, -1.3), (1.6, -1.4), 14), [(-3.1, -1.4), (-3.3, -0.4)])
    stripes = [[(0.6, -1.3), (1.2, -0.3)], [(0.9, -1.3), (1.5, -0.3)], [(1.4, -1.3), (1.75, -0.7)]]
    house = [poly((-2.2, -0.4), (-2.2, 0.8), (0.8, 0.8), (1.4, -0.35), closed=False), poly((-1.6, 0.8), (-1.6, 1.5), (0.4, 1.5), (0.8, 0.8), closed=False)]
    wins = windows(-1.4, 0.3, 1.0, 1.3, 4) + portholes(-1.8, 0.3, 0.2, 4, 0.13)
    mast = [[(-0.6, 1.5), (-0.6, 3.2)], [(-1.1, 2.6), (-0.1, 2.6)], ellipse(-0.6, 3.25, 0.45, 0.1, 20)]
    rescue = [chain([(-3.2, -0.35)], quad((-3.2, -0.35), (-2.7, -0.75), (-2.2, -0.35), 10), [(-3.2, -0.35)])]
    ring = [circle(1.9, 0.3, 0.35, 20), circle(1.9, 0.3, 0.2, 16)]
    return make("Coast Guard Cutter", [hull, sea(-1.6), sea(-2.2, amp=0.1, waves=5)] + stripes + house + wins + mast + rescue + ring)


@design("ships_icebreaker", T)
def icebreaker(rng):
    hull = chain([(-3.4, -0.2), (1.8, -0.2), (3.0, 0.6)], cubic((3.0, 0.6), (2.6, 0.0), (2.4, -0.8), (1.6, -1.2), 14), [(-3.2, -1.2), (-3.4, -0.2)])
    house = [rect(-1.4, -0.2, 1.0, 1.0), rect(-1.0, 1.0, 0.8, 1.7)] + windows(-0.8, 0.6, 1.25, 1.5, 4) + windows(-1.2, 0.8, 0.3, 0.6, 5)
    funnel = poly((-2.6, -0.2), (-2.5, 1.4), (-1.9, 1.4), (-1.8, -0.2), closed=False)
    mast = [[(0.0, 1.7), (0.0, 2.8)], [(-0.4, 2.4), (0.4, 2.4)]]
    stripe = [(-3.3, -0.65), (2.6, -0.65)]
    ice = [poly((1.6, -1.15), (2.3, -0.9), (3.0, -1.0), (3.6, -1.3), closed=False), poly((2.5, -1.3), (3.0, -1.6), (3.6, -1.5), closed=False),
           poly((-3.6, -1.6), (-2.0, -1.5), (-0.6, -1.65), closed=False), poly((0.3, -1.6), (1.4, -1.45), closed=False),
           poly((2.0, -1.4), (2.4, -1.9), (3.0, -1.8), (3.6, -2.0), closed=False)]
    floes = [poly((-3.0, -2.2), (-2.2, -2.0), (-1.6, -2.3), (-2.4, -2.6)), poly((-0.8, -2.0), (0.2, -1.9), (0.6, -2.3), (-0.4, -2.5)),
             poly((1.2, -2.1), (2.0, -2.0), (2.4, -2.4), (1.4, -2.6)), poly((2.8, -2.3), (3.6, -2.2), (3.5, -2.7), (2.9, -2.7))]
    return make("Icebreaker Ship", [hull, funnel, stripe] + house + mast + ice + floes)


@design("ships_lifeboat_davits", T)
def lifeboat_davits(rng):
    side = [[(-3.6, 0.6), (3.6, 0.6)], [(-3.6, 0.3), (3.6, 0.3)]] + portholes(-3.0, 3.0, -1.0, 7, 0.25) + [[(-3.6, -2.4), (3.6, -2.4)]]
    davits = [chain([(x, 0.6), (x, 1.8)], arc(x + 0.6 * s, 1.8, 0.6, math.pi if s > 0 else 0, math.pi / 2, 10), [(x + 1.1 * s, 2.4)]) for x, s in ((-2.6, 1), (2.6, -1))]
    davits = [chain([(-2.6, 0.6), (-2.6, 2.0)], arc(-2.0, 2.0, 0.6, math.pi, math.pi / 2, 10), [(-1.6, 2.6)]),
              chain([(2.6, 0.6), (2.6, 2.0)], arc(2.0, 2.0, 0.6, 0, math.pi / 2, 10), [(1.6, 2.6)])]
    ropes = [[(-1.6, 2.6), (-1.6, 1.85)], [(1.6, 2.6), (1.6, 1.85)]]
    boat = chain([(-2.2, 1.8), (2.2, 1.8)], quad((2.2, 1.8), (1.9, 0.9), (0.8, 0.85), 10), [(-0.8, 0.85)], quad((-0.8, 0.85), (-1.9, 0.9), (-2.2, 1.8), 10))
    cover = chain([(-1.9, 1.8)], quad((-1.9, 1.8), (0, 2.6), (1.9, 1.8), 20))
    stripe = quad((-2.1, 1.45), (0, 1.25), (2.1, 1.45))
    label = rect(-0.6, 1.35, 0.6, 1.7)
    rail = [[(-3.6, 1.2), (-2.8, 1.2)], [(2.8, 1.2), (3.6, 1.2)]] + [[(x, 0.6), (x, 1.2)] for x in (-3.4, -3.0, 3.0, 3.4)]
    return make("Lifeboat on Davits", side + davits + ropes + [boat, cover, stripe, label] + rail)


# --------------------------------------------------------------- big ships


@design("ships_aircraft_carrier", T)
def aircraft_carrier(rng):
    hull = chain([(-3.6, 0.0), (3.8, 0.0), (3.8, -0.2)], quad((3.8, -0.2), (3.0, -1.4), (2.0, -1.4), 12), [(-3.0, -1.4), (-3.4, -0.25), (-3.6, -0.25), (-3.6, 0.0)])
    deck = [(-3.6, -0.25), (3.8, -0.25)]
    island = [poly((0.9, 0.0), (1.0, 1.4), (2.2, 1.4), (2.3, 0.0), closed=False), rect(1.2, 1.4, 2.0, 1.9)] + windows(1.15, 2.05, 1.0, 1.25, 4)
    mast = [[(1.6, 1.9), (1.6, 2.9)], [(1.2, 2.5), (2.0, 2.5)], ellipse(1.6, 3.0, 0.35, 0.1, 16)]

    def jet(x, s):
        return [transform(p, dx=x, dy=0.0, s=s) for p in [
            poly((-0.9, 0.12), (0.7, 0.12), (1.0, 0.25), (0.6, 0.38), (-0.6, 0.38), (-0.9, 0.95), (-1.05, 0.95), (-1.0, 0.12)),
            poly((-0.2, 0.25), (0.25, 0.25), (-0.4, 0.05), closed=False)]]
    planes = jet(-2.4, 0.8) + jet(-0.6, 0.8) + jet(3.0, 0.7)
    num = [rect(-0.2, -1.0, 0.5, -0.5)]
    return make("Aircraft Carrier", [hull, deck, sea(-1.6), sea(-2.2, amp=0.1, waves=5)] + island + mast + planes + num)


@design("ships_battleship", T)
def battleship(rng):
    hull = chain([(-3.6, -0.3), (3.0, -0.3), (3.8, 0.0)], quad((3.8, 0.0), (3.2, -1.3), (2.2, -1.35), 12), [(-3.3, -1.35), (-3.6, -0.3)])
    tower = [rect(-0.9, -0.3, 0.9, 0.6), rect(-0.6, 0.6, 0.6, 1.4), rect(-0.35, 1.4, 0.35, 2.0)] + windows(-0.5, 0.5, 0.9, 1.15, 3)
    mast = [[(0.0, 2.0), (0.0, 3.2)], [(-0.5, 2.7), (0.5, 2.7)]]
    funnel = poly((-1.7, -0.3), (-1.6, 1.3), (-1.0, 1.3), (-0.95, -0.3), closed=False)
    turrets = []
    for x, d in [(-2.6, -1), (1.5, 1), (2.5, 1)]:
        turrets += [chain([(x - 0.45, -0.3)], arc(x, -0.3, 0.45, math.pi, 0, 12)), [(x + d * 0.3, -0.05), (x + d * 1.2, 0.15)], [(x + d * 0.3, -0.18), (x + d * 1.2, 0.02)]]
    ports = portholes(-2.8, 2.6, -0.8, 10, 0.1)
    return make("Battleship", [hull, funnel, sea(-1.6), sea(-2.2, amp=0.1, waves=5)] + tower + mast + turrets + ports)


@design("ships_ocean_liner", T)
def ocean_liner(rng):
    hull = chain([(-3.6, 0.0), (3.4, 0.0), (3.8, 0.4)], quad((3.8, 0.4), (3.3, -1.4), (2.2, -1.45), 14), [(-3.2, -1.45)], quad((-3.2, -1.45), (-3.7, -0.8), (-3.6, 0.0), 8))
    band = [(-3.6, -0.5), (3.6, -0.5)]
    sup = [rect(-2.8, 0.0, 2.6, 0.7)] + portholes(-2.5, 2.3, 0.35, 12, 0.1) + portholes(-3.1, 3.1, -0.25, 15, 0.08)
    funnels = []
    for x in (-1.8, -0.6, 0.6, 1.8):
        funnels += [poly((x - 0.3, 0.7), (x - 0.18, 2.3), (x + 0.32, 2.3), (x + 0.2, 0.7), closed=False), [(x - 0.2, 1.95), (x + 0.3, 1.95)]]
    masts = [[(-3.0, 0.0), (-3.2, 3.0)], [(3.0, 0.4), (3.2, 3.0)], [(-3.2, 3.0), (-1.8, 2.3)], [(3.2, 3.0), (1.8, 2.3)]]
    smoke = [circle(x + 0.4, 2.7, 0.25, 14) for x in (-1.8, -0.6)] + [circle(x + 0.8, 3.0, 0.32, 16) for x in (-1.8, -0.6)]
    return make("Classic Ocean Liner", [hull, band, sea(-1.7), sea(-2.3, amp=0.1, waves=5)] + sup + funnels + masts + smoke)


@design("ships_trireme", T)
def trireme(rng):
    hull = chain([(-3.0, 1.5)], cubic((-3.0, 1.5), (-3.4, 0.3), (-2.8, -0.6), (-2.0, -0.8), 20), [(2.6, -0.8), (3.7, -0.75), (3.7, -0.5), (2.8, -0.45), (3.1, 0.5),
                 (2.8, 0.1), (-2.3, 0.1)], cubic((-2.3, 0.1), (-2.6, 0.4), (-2.8, 1.0), (-2.7, 1.5), 12), [(-3.0, 1.5)])
    eye_ = [lens((2.2, -0.2), (2.65, -0.2), 0.3)]
    oars = []
    for row, y in enumerate((-0.15, -0.45)):
        for k in range(7):
            x = -1.6 + 0.55 * k + 0.25 * row
            oars.append([(x, y), (x - 0.55, -1.75)])
    band = [(-2.2, -0.3), (2.7, -0.3)]
    mast = [(0.0, 0.1), (0.0, 3.4)]
    sail = chain([(-1.5, 3.1), (1.5, 3.1), (1.6, 1.0)], quad((1.6, 1.0), (0, 0.75), (-1.6, 1.0), 16), [(-1.5, 3.1)])
    emblem = circle(0.0, 2.0, 0.5, 30)
    shields = [arc(x, 0.1, 0.22, 0, math.pi, 8) for x in (-1.6, -0.9, 0.9, 1.6)]
    return make("Greek Trireme", [hull, band, mast, sail, emblem, sea(-1.5)] + eye_ + oars + shields)


@design("ships_narrowboat", T)
def narrowboat(rng):
    hull = poly((-3.6, -0.2), (3.4, -0.2), (3.7, 0.3), (3.4, -0.9), (-3.4, -0.9))
    cabin = rect(-2.8, -0.2, 2.6, 0.7)
    roof = [(-2.9, 0.7), (2.7, 0.7)]
    ports = [circle(x, 0.25, 0.17, 14) for x in (-2.2, -1.6, 0.2, 0.8, 1.4)]
    door = rect(-1.15, -0.2, -0.55, 0.55)
    panel = [poly((1.8, 0.05), (2.4, 0.05), (2.4, 0.5), (1.8, 0.5)), star(2.1, 0.27, 0.15)]
    tiller = [[(-3.0, -0.2), (-3.2, 0.6), (-2.6, 0.9)]]
    chimney = rect(1.9, 0.7, 2.1, 1.2)
    pots = []
    for x in (-1.8, -0.2, 0.8):
        pots.append(poly((x - 0.18, 0.7), (x - 0.22, 0.95), (x + 0.22, 0.95), (x + 0.18, 0.7), closed=False))
        pots += [lens((x, 0.95), (x - 0.3, 1.35), 0.3), lens((x, 0.95), (x, 1.45), 0.3), lens((x, 0.95), (x + 0.3, 1.35), 0.3)]
    fenders = [ellipse(x, -0.6, 0.12, 0.22, 12) for x in (-2.2, 0.0, 2.2)]
    bank = [quad((-3.8, 1.8), (0, 2.0), (3.8, 1.8))]
    tree = [chain(circle(-2.6, 2.8, 0.7, 30)), [(-2.6, 2.1), (-2.6, 1.85)], chain(circle(2.8, 2.7, 0.6, 30)), [(2.8, 2.1), (2.8, 1.85)]]
    return make("Canal Narrowboat", [hull, cabin, roof, door, chimney, sea(-1.1, amp=0.06, waves=7)] + ports + panel + tiller + pots + fenders + bank + tree)


@design("ships_speedboat", T)
def speedboat(rng):
    hull = poly((-3.0, -0.6), (-3.0, 0.2), (2.0, 0.6), (3.4, 0.9), (2.6, -0.2), (-2.7, -0.9))
    stripe = [(-2.9, -0.2), (2.9, 0.3)]
    wind = poly((0.2, 0.5), (0.7, 1.1), (1.3, 1.1), (1.5, 0.6), closed=False)
    driver = [circle(-0.4, 1.1, 0.25, 18), poly((-0.65, 0.85), (-0.7, 0.35), (-0.1, 0.4), (-0.15, 0.85), closed=False)]
    motor = poly((-3.0, 0.1), (-3.4, 0.2), (-3.5, -1.0), (-3.2, -1.1), (-3.0, -0.5))
    wake = [quad((-3.6, -1.3), (-1.0, -0.8), (2.6, -0.4)), quad((-3.6, -1.7), (-0.4, -1.4), (2.0, -0.6))]
    spray = [quad((2.2, -0.4), (3.0, 0.4), (3.6, -0.3)), quad((-3.4, -1.1), (-3.8, 0.0), (-4.0, -0.6))] + [circle(x, y, 0.08, 8) for x, y in [(3.4, 0.2), (3.8, -0.1), (-3.9, 0.1)]]
    fl = [[(-2.6, 0.25), (-2.6, 1.2)], flag(-2.6, 1.2, -0.45, 0.3)]
    return make("Speedboat", [hull, wind, motor, sea(-2.2, amp=0.1, waves=5), stripe] + driver + wake + spray + fl)


@design("ships_jet_ski", T)
def jet_ski(rng):
    body = chain([(-2.4, -0.6)], quad((-2.4, -0.6), (0, -1.1), (2.6, -0.4), 20), [(3.0, 0.1)], quad((3.0, 0.1), (2.0, 0.6), (1.0, 0.5), 12), [(0.6, 0.0), (-2.2, 0.0), (-2.4, -0.6)])
    seat = chain([(-1.9, 0.0)], quad((-1.9, 0.0), (-1.2, 0.45), (0.5, 0.25), 12), [(0.6, 0.0)])
    bars = [[(1.0, 0.5), (0.8, 1.3)], [(0.5, 1.35), (1.2, 1.25)]]
    rider = [circle(-0.3, 2.3, 0.3, 20), tube([(-0.35, 2.0), (-0.6, 0.8)], 0.5), tube([(-0.6, 0.8), (0.2, 0.6), (0.5, 0.1)], 0.3), [(-0.25, 1.8), (0.7, 1.35)]]
    visor = arc(-0.3, 2.3, 0.36, R(-30), R(80), 10)
    spray = [quad((-2.4, -0.4), (-3.4, 1.2), (-3.9, -0.4)), quad((-2.4, -0.7), (-3.1, 0.4), (-3.6, -0.9))] + [circle(x, y, 0.09, 8) for x, y in [(-3.6, 0.8), (-3.2, 1.3), (-3.9, 0.3)]]
    stripe = quad((-2.0, -0.35), (0.5, -0.6), (2.6, -0.1))
    return make("Jet Ski", [body, seat, visor, stripe, sea(-1.1), sea(-1.7, amp=0.1, waves=5)] + bars + rider + spray)


@design("ships_hovercraft", T)
def hovercraft(rng):
    skirt = chain([(-3.2, -0.4)], [(x, -1.2 + 0.12 * math.sin(k * math.pi)) for k, x in enumerate([-3.0 + 0.4 * i for i in range(16)])], [(3.2, -0.4)])
    skirt = chain([(-3.2, -0.4)], cubic((-3.2, -0.4), (-3.7, -0.7), (-3.2, -1.3), (-2.6, -1.3), 14),
                  [(2.6, -1.3)], cubic((2.6, -1.3), (3.2, -1.3), (3.7, -0.7), (3.2, -0.4), 14), [(-3.2, -0.4)])
    folds = [[(x, -0.45), (x, -1.25)] for x in (-2.0, -1.0, 0.0, 1.0, 2.0)]
    cabin = chain([(-2.8, -0.4)], [(-2.6, -0.4), (-2.6, 0.5)], quad((-2.6, 0.5), (-2.4, 1.1), (-1.0, 1.1), 10),
                  [(1.6, 1.1)], quad((1.6, 1.1), (2.6, 1.0), (2.9, -0.4), 10))
    wins = windows(-2.2, 1.4, 0.4, 0.8, 6)
    fans = []
    for x in (-1.6, 0.2):
        fans += [rrect(x - 0.15, 1.1, x + 1.25, 2.6, 0.3), circle(x + 0.55, 1.85, 0.5, 30), [(x + 0.55, 1.35), (x + 0.55, 2.35)], [(x + 0.05, 1.85), (x + 1.05, 1.85)]]
    rudders = [poly((-2.0, 1.1), (-2.4, 2.0), (-2.2, 2.0), (-1.8, 1.1), closed=False)]
    spray = [quad((-3.4, -1.3), (-3.9, -0.6), (-4.0, -1.4)), quad((3.4, -1.3), (3.9, -0.6), (4.0, -1.4))]
    return make("Hovercraft", [skirt, cabin, sea(-1.7, amp=0.1, waves=8)] + folds + wins + fans + spray)


@design("ships_pontoon", T)
def pontoon(rng):
    tubes = [rrect(-3.0, -1.2, 2.6, -0.75, 0.22), chain([(2.6, -1.2)], quad((2.6, -1.2), (3.5, -1.0), (2.6, -0.75), 10))]
    deck = rect(-3.1, -0.75, 3.0, -0.55)
    fence = rect(-2.9, -0.55, 2.4, 0.2)
    bars = [[(x, -0.55), (x, 0.2)] for x in (-2.0, -1.0, 0.0, 1.0, 2.0)]
    poles = [[(-2.6, 0.2), (-2.6, 1.6)], [(0.6, 0.2), (0.6, 1.6)]]
    top = chain([(-3.0, 1.5)], quad((-3.0, 1.5), (-1.0, 2.0), (1.0, 1.5), 16), [(0.8, 1.5)])
    top = [chain(quad((-3.0, 1.5), (-1.0, 2.2), (1.0, 1.5), 16), [(-3.0, 1.5)])]
    people = person(-1.6, 0.75, 0.8) + person(-0.5, 0.75, 0.8)
    motor = [poly((-3.1, -0.4), (-3.5, -0.3), (-3.6, -1.5), (-3.3, -1.6), (-3.1, -0.9))]
    seat = [rrect(1.0, 0.2, 2.0, 0.55, 0.12)]
    return make("Pontoon Party Boat", [deck, fence, sea(-1.4, amp=0.08), sea(-2.0, amp=0.08, waves=5)] + tubes + bars + poles + top + people + motor + seat)


# --------------------------------------------------------------- nautical objects


@design("ships_anchor_chain", T)
def anchor_chain(rng):
    shank = rect(-0.2, -2.2, 0.2, 1.6)
    ring = [circle(0, 2.05, 0.45, 30), circle(0, 2.05, 0.25, 20)]
    stock = rrect(-1.6, 1.0, 1.6, 1.35, 0.15)
    arms = [arc(0, -1.0, 2.1, R(195), R(345), 50), arc(0, -1.0, 1.75, R(200), R(340), 44)]
    flukes = [poly((-2.05, -1.55), (-2.6, -0.6), (-1.75, -1.1)), poly((2.05, -1.55), (2.6, -0.6), (1.75, -1.1))]
    crown = poly((-0.35, -2.75), (0, -3.15), (0.35, -2.75), closed=False)
    path = cubic((0.35, 2.3), (1.6, 3.4), (3.4, 2.4), (2.9, -0.4), 100)
    pts = resample(path, 9)
    links = []
    for k in range(1, 10):
        (x0, y0), (x1, y1) = pts[k - 1], pts[k]
        a = math.atan2(y1 - y0, x1 - x0)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        L = math.dist((x0, y0), (x1, y1))
        if k % 2:
            links += [ellipse(cx, cy, 0.62 * L, 0.2, 24, rot=a), ellipse(cx, cy, 0.4 * L, 0.07, 16, rot=a)]
        else:
            links.append(transform(rrect(-0.62 * L, -0.07, 0.62 * L, 0.07, 0.06), dx=cx, dy=cy, rot=a))
    return make("Anchor and Chain", [shank, stock, crown] + ring + arms + flukes + links)


@design("ships_life_ring", T)
def life_ring(rng):
    outer = circle(0, 0, 2.6, 140)
    inner = circle(0, 0, 1.4, 90)
    bands = []
    for a in (45, 135, 225, 315):
        for d in (-12, 12):
            bands.append([(1.4 * math.cos(R(a + d * 1.6)), 1.4 * math.sin(R(a + d * 1.6))), (2.6 * math.cos(R(a + d)), 2.6 * math.sin(R(a + d)))])
    rope = []
    for a in (0, 90, 180, 270):
        p0 = (2.6 * math.cos(R(a - 25)), 2.6 * math.sin(R(a - 25)))
        p1 = (2.6 * math.cos(R(a + 25)), 2.6 * math.sin(R(a + 25)))
        c = (3.4 * math.cos(R(a)), 3.4 * math.sin(R(a)))
        rope.append(quad(p0, c, p1, 16))
    return make("Life Ring", [outer, inner] + bands + rope)


@design("ships_compass_rose", T)
def compass_rose(rng):
    rings = [circle(0, 0, 2.8, 140), circle(0, 0, 2.5, 130)]
    ticks = [[(2.5 * math.cos(R(a)), 2.5 * math.sin(R(a))), (2.8 * math.cos(R(a)), 2.8 * math.sin(R(a)))] for a in range(0, 360, 15) if a % 45]
    big = star(0, 0, 2.4, n=4, inner=0.22)
    small = star(0, 0, 1.6, n=4, inner=0.35, rot=R(45))
    halves = [[(0, 0), (2.4 * math.cos(R(a)), 2.4 * math.sin(R(a)))] for a in (90, 0, 270, 180)]
    hub = circle(0, 0, 0.25, 16)
    N = [[(-0.2, 2.95), (-0.2, 3.45), (0.2, 2.95), (0.2, 3.45)]]
    return make("Compass Rose", rings + ticks + [big, small, hub] + halves + N)


@design("ships_bottle_ship", T)
def bottle_ship(rng):
    bottle = chain([(-3.4, -1.4)], [(1.8, -1.4)], cubic((1.8, -1.4), (2.6, -1.4), (2.6, -0.4), (3.0, -0.4), 16), [(3.4, -0.4), (3.4, 0.4), (3.0, 0.4)],
                   cubic((3.0, 0.4), (2.6, 0.4), (2.6, 1.4), (1.8, 1.4), 16), [(-3.4, 1.4)], cubic((-3.4, 1.4), (-3.75, 1.4), (-3.75, -1.4), (-3.4, -1.4), 16))
    cork = rect(3.4, -0.3, 4.0, 0.3)
    hull = chain([(-2.4, -0.7), (1.0, -0.7)], quad((1.0, -0.7), (0.8, -1.2), (0.3, -1.2), 8), [(-2.0, -1.2), (-2.4, -0.7)])
    masts = [[(-1.5, -0.7), (-1.5, 1.1)], [(0.0, -0.7), (0.0, 1.2)]]
    sails = [sq_sail(-1.5, -0.4, 0.3, 0.45, 0.1), sq_sail(-1.5, 0.4, 0.95, 0.35, 0.08), sq_sail(0.0, -0.4, 0.3, 0.45, 0.1), sq_sail(0.0, 0.4, 1.0, 0.35, 0.08)]
    jib = poly((0.1, 1.0), (1.5, -0.6), (0.1, -0.55))
    waves_ = [wave(-3.5, 1.7, -1.1, 0.06, 6, 80)]
    stand = [poly((-2.8, -1.4), (-2.6, -1.9), (1.0, -1.9), (1.2, -1.4), closed=False), [(-3.0, -1.9), (1.4, -1.9)]]
    shine = [quad((-3.0, 1.05), (-1.5, 1.2), (0.0, 1.1))]
    return make("Ship in a Bottle", [bottle, cork, hull, jib] + masts + sails + waves_ + stand + shine)


@design("ships_ship_bell", T)
def ship_bell(rng):
    bell = chain([(-1.8, -1.6)], cubic((-1.8, -1.6), (-1.0, -1.1), (-1.4, 1.2), (0, 1.3), 30), cubic((0, 1.3), (1.4, 1.2), (1.0, -1.1), (1.8, -1.6), 30), [(-1.8, -1.6)])
    lip = ellipse(0, -1.6, 1.8, 0.3, 50)
    bands = [quad((-1.15, -0.2), (0, -0.1), (1.15, -0.2)), quad((-1.25, -0.6), (0, -0.5), (1.25, -0.6)), quad((-1.0, 0.8), (0, 0.9), (1.0, 0.8))]
    crown = [rect(-0.25, 1.3, 0.25, 1.7), circle(0, 1.95, 0.3, 20)]
    bracket = [poly((-0.4, 2.2), (-0.4, 2.5), (2.8, 2.5), (2.8, 2.2)), poly((2.8, 2.5), (3.2, 2.5), (3.2, -0.6), (2.8, -0.6), (2.8, 1.2), (1.8, 2.2), closed=False)]
    clapper = [[(0, -1.6), (0, -2.1)], circle(0, -2.25, 0.18, 14)]
    lanyard = [cubic((0, -2.4), (-0.4, -2.7), (-0.2, -3.0), (-0.6, -3.3), 14), cubic((0.1, -2.4), (0.4, -2.7), (0.2, -3.0), (0.5, -3.3), 14)]
    text = [[(-0.7, 0.1), (0.7, 0.1)], [(-0.5, 0.35), (0.5, 0.35)]]
    return make("Ship's Bell", [bell, lip] + bands + crown + bracket + clapper + lanyard + text)


@design("ships_porthole_view", T)
def porthole_view(rng):
    outer = circle(0, 0, 3.0, 150)
    rim = circle(0, 0, 2.5, 130)
    glass = circle(0, 0, 2.2, 120)
    bolts = [circle(2.75 * math.cos(R(a)), 2.75 * math.sin(R(a)), 0.13, 12) for a in range(0, 360, 30)]
    horizon = span(glass, -0.4)
    waves_ = [wave(-2.0, 2.0, -1.0, 0.08, 4, 40), wave(-1.6, 1.6, -1.6, 0.08, 3, 30)]
    boat = [poly((0.4, -0.35), (1.6, -0.35), (1.4, -0.6), (0.6, -0.6)), poly((1.0, -0.35), (1.0, 1.0), (1.6, -0.25))]
    sun = arc(-1.0, -0.4, 0.6, 0, math.pi, 20)
    gulls = [gull(-0.4, 1.2, 0.3), gull(0.3, 1.5, 0.25)]
    hinge = [rect(-3.4, -0.3, -3.0, 0.3)]
    return make("Porthole Sea View", [outer, rim, glass, horizon, sun] + bolts + waves_ + boat + gulls + hinge)


@design("ships_sextant", T)
def sextant(rng):
    apex = (0.0, 2.6)
    limb_out = arc(0, 2.6, 4.6, R(240), R(300), 40)
    limb_in = arc(0, 2.6, 4.2, R(240), R(300), 40)
    frame = [chain([apex], [limb_out[0]]), chain([apex], [limb_out[-1]]), limb_out, limb_in]
    ticks = [[(0 + 4.2 * math.cos(R(a)), 2.6 + 4.2 * math.sin(R(a))), (0 + 4.45 * math.cos(R(a)), 2.6 + 4.45 * math.sin(R(a)))] for a in range(244, 300, 4)]
    struts = [[apex, (0, -1.6)], ellipse(0, 0.4, 0.9, 0.6, 30)]
    arm = tube([(0, 2.6), (0.9, -1.9)], 0.22)
    mirror = [rect(-0.35, 2.4, 0.35, 3.0), rect(-1.5, 0.6, -0.9, 1.2)]
    scope = [rrect(-2.6, 1.0, -0.4, 1.35, 0.15), rect(-2.9, 0.95, -2.6, 1.4)]
    handle = [rrect(0.9, 0.0, 1.3, 1.6, 0.18)]
    pivot = circle(0, 2.6, 0.18, 14)
    return make("Brass Sextant", frame + ticks + struts + [arm, pivot] + mirror + scope + handle)


@design("ships_captain_hat", T)
def captain_hat(rng):
    crown = chain([(-2.4, 0.0)], cubic((-2.4, 0.0), (-3.4, 1.2), (-2.2, 2.0), (0, 2.0), 30), cubic((0, 2.0), (2.2, 2.0), (3.4, 1.2), (2.4, 0.0), 30))
    band = [rect(-2.4, -0.8, 2.4, 0.0)]
    visor = chain([(-2.4, -0.8)], cubic((-2.4, -0.8), (-2.0, -2.0), (2.0, -2.0), (2.4, -0.8), 30))
    visor_in = cubic((-2.0, -0.85), (-1.6, -1.6), (1.6, -1.6), (2.0, -0.85), 24)
    cord = [quad((-2.2, -0.4), (0, -0.55), (2.2, -0.4))] + [circle(x, -0.42, 0.15, 12) for x in (-2.2, 2.2)]
    badge = [circle(0, 0.9, 0.5, 30)]
    anc = [[(0, 0.6), (0, 1.25)], arc(0, 0.85, 0.28, R(200), R(340), 10), [(-0.18, 1.15), (0.18, 1.15)]]
    laurel = []
    for a in (250, 220, 190, 160):
        x, y = 0.85 * math.cos(R(a)), 0.9 + 0.85 * math.sin(R(a))
        d = R(a - 70)
        laurel.append(lens((x, y), (x + 0.45 * math.cos(d), y + 0.45 * math.sin(d)), 0.3))
    laurel.append(arc(0, 0.9, 0.85, R(150), R(262), 24))
    laurel += mirror_all(laurel)
    return make("Captain's Hat", [crown, visor, visor_in] + band + cord + badge + anc + laurel)


@design("ships_buoy", T)
def buoy(rng):
    float_ = chain([(-1.6, -1.0)], quad((-1.6, -1.0), (0, -2.0), (1.6, -1.0), 20), [(1.4, -0.4), (-1.4, -0.4), (-1.6, -1.0)])
    tower = [[(-1.0, -0.4), (-0.4, 2.0)], [(1.0, -0.4), (0.4, 2.0)], [(-0.75, 0.6), (0.75, 0.6)], [(-0.55, 1.4), (0.55, 1.4)],
             [(-1.0, -0.4), (0.55, 1.4)], [(1.0, -0.4), (-0.55, 1.4)]]
    bell = chain([(-0.45, 0.65)], cubic((-0.45, 0.65), (-0.3, 0.9), (-0.4, 1.25), (0, 1.25), 10), cubic((0, 1.25), (0.4, 1.25), (0.3, 0.9), (0.45, 0.65), 10), [(-0.45, 0.65)])
    top = [rect(-0.55, 2.0, 0.55, 2.2), rect(-0.3, 2.2, 0.3, 2.7), poly((-0.4, 2.7), (0, 3.0), (0.4, 2.7), (-0.4, 2.7))]
    glow = [[(0.6 * math.cos(R(a)), 2.45 + 0.6 * math.sin(R(a))), (1.1 * math.cos(R(a)), 2.45 + 1.1 * math.sin(R(a)))] for a in (0, 30, 150, 180)]
    num = [[(-0.3, -0.6), (-0.3, -1.3)], [(0.1, -0.6), (0.5, -0.6), (0.1, -1.3)]]
    waves_ = [wave(-3.4, -1.5, -1.2, 0.12, 2, 40), wave(1.5, 3.4, -1.2, 0.12, 2, 40), sea(-2.0), sea(-2.6, amp=0.1, waves=5)]
    return make("Bell Buoy", [float_, bell] + tower + top + glow + num + waves_)


@design("ships_lantern", T)
def lantern(rng):
    base = [rrect(-1.5, -2.6, 1.5, -2.1, 0.15)]
    globe = chain([(-1.0, -2.1)], cubic((-1.0, -2.1), (-1.9, -0.8), (-1.9, 0.8), (-1.0, 1.6), 30), [(1.0, 1.6)], cubic((1.0, 1.6), (1.9, 0.8), (1.9, -0.8), (1.0, -2.1), 30))
    cage = [cubic((0, -2.1), (-0.15, -0.8), (-0.15, 0.8), (0, 1.6), 20), cubic((-0.6, -2.1), (-1.1, -0.8), (-1.1, 0.8), (-0.6, 1.6), 20), cubic((0.6, -2.1), (1.1, -0.8), (1.1, 0.8), (0.6, 1.6), 20)]
    cage += [span(globe, y) for y in (-1.0, 0.6)]
    top = [rect(-1.2, 1.6, 1.2, 1.9), poly((-1.0, 1.9), (-0.4, 2.6), (0.4, 2.6), (1.0, 1.9), closed=False), rect(-0.35, 2.6, 0.35, 2.9)]
    handle = chain(arc(0, 2.9, 0.8, R(180), R(0), 30))
    flame = lens((0.0, -1.3), (0.0, 0.2), 0.3)
    wick = rect(-0.25, -1.7, 0.25, -1.3)
    return make("Ship's Lantern", [globe, flame, wick, handle] + base + cage + top)


@design("ships_harbor", T)
def harbor(rng):
    pier = [rect(-3.6, 0.0, 0.6, 0.35)] + [[(x, 0.0), (x, -1.6)] for x in (-3.2, -2.2, -1.2, -0.2)] + [[(x + 0.2, 0.0), (x + 0.2, -1.6)] for x in (-3.2, -2.2, -1.2, -0.2)]
    bollards = [chain([(-1.85, 0.35), (-1.85, 0.65)], arc(-1.7, 0.65, 0.15, math.pi, 0, 6), [(-1.55, 0.35)])]
    shed = [rect(-3.4, 0.35, -2.0, 1.4), poly((-3.6, 1.3), (-2.7, 2.0), (-1.8, 1.3)), rect(-3.0, 0.35, -2.5, 1.0)]
    crane = [[(-1.0, 0.35), (-0.8, 3.0)], [(-0.4, 0.35), (-0.6, 3.0)], [(-0.9, 3.0), (2.4, 3.0)], [(-0.9, 2.7), (1.4, 3.0)], [(2.0, 3.0), (2.0, 1.4)],
             rect(1.8, 1.0, 2.2, 1.4)] + [[(-0.98, y), (-0.42, y + 0.6)] for y in (0.6, 1.4, 2.2)]
    boat = [chain([(0.8, -0.3), (3.6, -0.3)], quad((3.6, -0.3), (3.3, -1.1), (2.6, -1.1), 10), [(1.2, -1.1), (0.8, -0.3)]), rect(1.4, -0.3, 2.4, 0.5),
            [(2.9, -0.3), (2.9, 1.0)]]
    rope = [quad((-0.0, 0.35), (0.4, -0.2), (0.9, -0.35))]
    waves_ = [sea(-1.5, amp=0.1, waves=7), sea(-2.1, amp=0.1, waves=6)]
    return make("Harbor Dock", pier + bollards + shed + crane + boat + rope + waves_ + [gull(0.6, 2.2, 0.3)])


def resample(pts, k):
    """k+1 points evenly spaced by arc length along pts (both ends included)."""
    d = [0.0]
    for a, b in zip(pts, pts[1:]):
        d.append(d[-1] + math.dist(a, b))
    out, j = [], 0
    for i in range(k + 1):
        s = d[-1] * i / k
        while j < len(d) - 2 and d[j + 1] < s:
            j += 1
        f = (s - d[j]) / ((d[j + 1] - d[j]) or 1)
        out.append((pts[j][0] + f * (pts[j + 1][0] - pts[j][0]), pts[j][1] + f * (pts[j + 1][1] - pts[j][1])))
    return out
