"""Kitchen & Cooking niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "kitchen"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


def place(pts, x, y, ang=0.0, s=1.0):
    """Rotate (radians) and scale a local drawing about its origin, then move it to (x, y)."""
    return transform(pts, x, y, s, ang)


def clip_out(pts, inside):
    """Split a polyline into the runs whose points are not hidden (inside(p) false)."""
    out, cur = [], []
    for p in pts:
        if inside(p):
            if len(cur) > 1:
                out.append(cur)
            cur = []
        else:
            cur.append(p)
    if len(cur) > 1:
        out.append(cur)
    return out


def in_circle(cx, cy, r):
    return lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2 < r * r


def in_ellipse(cx, cy, rx, ry):
    return lambda p: ((p[0] - cx) / rx) ** 2 + ((p[1] - cy) / ry) ** 2 < 1


def in_rect(x0, y0, x1, y1):
    return lambda p: x0 < p[0] < x1 and y0 < p[1] < y1


def steam(x, y, h=1.0, amp=0.15, n=24):
    return [(x + amp * math.sin(TAU * 1.25 * i / n), y + h * i / n) for i in range(n + 1)]


def scallop(cx, cy, rx, ry, a0, a1, bumps, depth=0.12, n=160):
    """Elliptical arc with puffy bumps (chef's hat, bread crust, clouds of flour)."""
    pts = []
    for i in range(n + 1):
        t = a0 + (a1 - a0) * i / n
        k = 1 + depth * abs(math.sin(bumps * math.pi * i / n))
        pts.append((cx + rx * k * math.cos(t), cy + ry * k * math.sin(t)))
    return pts


def blob(cx, cy, r, wob=0.1, ph=0.0, n=90):
    return [(cx + r * (1 + wob * math.sin(3 * t + ph) + 0.6 * wob * math.sin(5 * t + 2 * ph)) * math.cos(t),
             cy + r * (1 + wob * math.sin(3 * t + ph) + 0.6 * wob * math.sin(5 * t + 2 * ph)) * math.sin(t))
            for t in [TAU * i / n for i in range(n + 1)]]


def profile(half):
    """Closed symmetric outline from a right-half profile listed top to bottom."""
    return chain(half, [(-x, y) for x, y in reversed(half)], [half[0]])


def bowl_side(cx, top, w, depth, n=40):
    """U-shaped bowl side view (open at the top)."""
    return cubic((cx - w, top), (cx - w, top - depth * 1.3), (cx + w, top - depth * 1.3), (cx + w, top), n)


def leaf(x, y, L, ang, bulge=0.3):
    return lens((x, y), (x + L * math.cos(ang), y + L * math.sin(ang)), bulge, 14)


def flame(cx, y, w, h, lean=0.0):
    return chain(cubic((cx - w, y), (cx - w * 1.1, y + h * 0.5), (cx + lean - w * 0.2, y + h * 0.7), (cx + lean, y + h), 14),
                 cubic((cx + lean, y + h), (cx + w * 0.4, y + h * 0.6), (cx + w * 1.1, y + h * 0.4), (cx + w, y), 14), [(cx - w, y)])


# ---------------------------------------------------------------- chefs ----

@design("kitchen_chef_hat", T)
def chef_hat(rng):
    band = rrect(-1.6, -2.8, 1.6, -1.2, 0.15)
    s = scallop(0, 0.5, 2.4, 2.0, math.radians(200), math.radians(-20), 5, 0.13)
    puff = chain([(-1.6, -1.2)], quad((-1.6, -1.2), (s[0][0] + 0.1, -1.0), s[0], 10), s,
                 quad(s[-1], (s[-1][0] - 0.1, -1.0), (1.6, -1.2), 10))
    pleats = [quad((x, -1.2), (x * 1.15, -0.3), (x * 1.25, 0.7), 12) for x in (-0.8, 0.0, 0.8)]
    folds = [arc(-0.9, 1.5, 0.55, math.radians(200), math.radians(320), 12), arc(0.9, 1.5, 0.55, math.radians(220), math.radians(340), 12),
             arc(0.0, 2.0, 0.5, math.radians(210), math.radians(330), 12)]
    stitch = [[(-1.6, -1.6), (1.6, -1.6)], [(-1.6, -2.4), (1.6, -2.4)]]
    emblem = [[(-0.45, -2.25), (0.45, -1.75)], [(0.45, -2.25), (-0.45, -1.75)], circle(0.5, -1.72, 0.12, 10), ellipse(-0.5, -1.7, 0.1, 0.16, 10)]
    return make("Chef's Toque", [band, puff] + pleats + folds + stitch + emblem)


@design("kitchen_chef_portrait", T)
def chef_portrait(rng):
    face = ellipse(0, -0.4, 1.25, 1.5, 100)
    band = rrect(-1.35, 0.85, 1.35, 1.55, 0.1)
    s = scallop(0, 2.2, 1.9, 1.0, math.radians(195), math.radians(-15), 4, 0.15)
    puff = chain([(-1.3, 1.55)], s, [(1.3, 1.55)])
    ears = [arc(-1.25, -0.3, 0.3, math.radians(100), math.radians(260), 12), arc(1.25, -0.3, 0.3, math.radians(-80), math.radians(80), 12)]
    brows = [arc(-0.5, 0.15, 0.35, math.radians(40), math.radians(140), 10), arc(0.5, 0.15, 0.35, math.radians(40), math.radians(140), 10)]
    nose = quad((-0.05, -0.1), (0.35, -0.55), (-0.1, -0.6), 12)
    stache = chain(cubic((0, -0.7), (-0.4, -0.5), (-0.9, -0.75), (-1.25, -0.4), 16), arc(-1.1, -0.45, 0.15, math.radians(170), math.radians(-60), 8),
                   cubic((-1.05, -0.58), (-1.0, -1.05), (-0.35, -1.05), (0, -0.85), 16))
    smile = arc(0, -0.95, 0.4, math.radians(220), math.radians(320), 12)
    jacket = chain([(-3.0, -3.0)], quad((-3.0, -3.0), (-2.8, -2.0), (-1.0, -1.85), 16), [(1.0, -1.85)], quad((1.0, -1.85), (2.8, -2.0), (3.0, -3.0), 16))
    scarf = [poly((-0.7, -1.75), (0.7, -1.75), (0, -2.4)), poly((0, -2.4), (-0.35, -3.0), (0.35, -3.0))]
    buttons = [circle(x, y, 0.13, 10) for x in (-1.2, 1.2) for y in (-2.3, -2.8)]
    return make("Chef with a Curly Moustache", [face, band, puff, nose, stache, mirror_x(stache), smile, jacket] + ears + brows + scarf + buttons,
                [eye(-0.45, -0.15, 0.12), eye(0.45, -0.15, 0.12)])


# ---------------------------------------------------------------- pans -----

@design("kitchen_frying_pan_eggs", T)
def frying_pan_eggs(rng):
    pan = circle(-0.6, 0, 2.3, 140)
    inner = circle(-0.6, 0, 2.0, 130)
    handle = chain([(1.65, 0.32)], [(3.6, 0.42)], arc(3.6, 0, 0.42, math.pi / 2, -math.pi / 2, 12), [(1.65, -0.32)])
    hole = rrect(2.9, -0.15, 3.6, 0.15, 0.15)
    eggs = [blob(-1.3, 0.6, 0.85, 0.1), circle(-1.25, 0.65, 0.33, 30), blob(0.15, -0.6, 0.8, 0.12, 1.0), circle(0.2, -0.55, 0.32, 30)]
    bacon = tube(wave(-1.8, -0.2, -1.05, 0.12, 2, 40), 0.35)
    shine = arc(-0.6, 0, 2.15, 2.0, 2.7, 16)
    return make("Frying Pan with Two Eggs", [pan, inner, handle, hole, bacon, shine] + eggs, [eye(-1.35, 0.75, 0.1), eye(0.1, -0.45, 0.1)])


@design("kitchen_saucepan", T)
def saucepan(rng):
    body = chain([(-2.0, 0.5)], [(-2.0, -1.5)], quad((-2.0, -1.5), (-2.0, -2.0), (-1.5, -2.0), 8), [(1.5, -2.0)],
                 quad((1.5, -2.0), (2.0, -2.0), (2.0, -1.5), 8), [(2.0, 0.5)])
    rim = rrect(-2.2, 0.5, 2.2, 0.8, 0.1)
    lid = quad((-2.05, 0.8), (0, 2.1), (2.05, 0.8), 30)
    knob = chain([(-0.2, 1.45)], [(-0.4, 1.85)], arc(0, 1.85, 0.4, math.pi, 0, 12), [(0.2, 1.45)])
    handle = chain([(2.2, 0.0)], [(3.5, 0.55)], arc(3.55, 0.35, 0.22, math.radians(70), math.radians(-110), 10), [(2.2, -0.45)])
    hole = circle(3.35, 0.3, 0.1, 10)
    shine = [[(-1.6, -0.2), (-1.6, -1.4)], [(-1.25, 0.1), (-1.25, -0.6)]]
    bubbles = [steam(-0.9, 2.0, 0.8), steam(0.9, 2.0, 0.8)]
    return make("Saucepan with a Lid", [body, rim, lid, knob, handle, hole] + shine + bubbles)


@design("kitchen_stock_pot", T)
def stock_pot(rng):
    body = chain([(-2.1, 0.6)], [(-2.1, -2.3)], quad((-2.1, -2.3), (-2.1, -2.7), (-1.7, -2.7), 8), [(1.7, -2.7)],
                 quad((1.7, -2.7), (2.1, -2.7), (2.1, -2.3), 8), [(2.1, 0.6)])
    rim = ellipse(0, 0.6, 2.1, 0.35, 100)
    soup = clip_out(ellipse(0, 0.55, 1.85, 0.25, 90), in_rect(0.25, 0.3, 0.9, 0.9))
    handles = [arc(-2.1, -0.1, 0.45, math.radians(90), math.radians(270), 14), arc(2.1, -0.1, 0.45, math.radians(-90), math.radians(90), 14)]
    ladle = [tube([(0.45, 0.45), (1.5, 2.2), (1.9, 2.75)], 0.22), arc(2.05, 2.55, 0.3, math.radians(120), math.radians(-60), 10)]
    stripe = [[(-2.1, -0.5), (2.1, -0.5)], [(-2.1, -0.7), (2.1, -0.7)]]
    st = [steam(-1.2, 1.1, 1.3, 0.2), steam(-0.3, 1.2, 1.5, 0.2)]
    veg = [circle(-1.0, 0.55, 0.12, 10), circle(1.2, 0.6, 0.12, 10)]
    return make("Steaming Stock Pot with Ladle", [body, rim] + soup + handles + ladle + stripe + st + veg)


@design("kitchen_wok", T)
def wok(rng):
    bowl = chain([(-2.6, 0.4)], cubic((-2.6, 0.4), (-2.4, -1.6), (2.4, -1.6), (2.6, 0.4), 40))
    rim = ellipse(0, 0.4, 2.6, 0.35, 120)
    grip = place(rrect(0, -0.25, 1.8, 0.25, 0.2), -2.7, 0.75, math.radians(160))
    stem = [[(-2.45, 0.45), (-2.75, 0.62)]]
    loop = arc(2.75, 0.3, 0.25, math.radians(120), math.radians(-120), 10)
    food = [rrect(-1.4, 1.2, -0.9, 1.6, 0.1), circle(0.2, 1.9, 0.25, 16), lens((0.8, 1.1), (1.5, 1.4), 0.3, 10),
            place(rrect(-0.3, -0.15, 0.3, 0.15, 0.07), -0.4, 2.5, 0.6), circle(1.2, 2.4, 0.2, 14), lens((-2.0, 2.0), (-1.4, 2.3), 0.3, 10)]
    motion = [arc(0, -0.2, 2.0, math.radians(60), math.radians(120), 12), arc(0, -0.4, 2.6, math.radians(65), math.radians(115), 12)]
    fire = [flame(x, -2.4, 0.3, h) for x, h in [(-1.2, 0.9), (-0.4, 1.1), (0.4, 1.1), (1.2, 0.9)]]
    ring = [[(-1.8, -2.4), (1.8, -2.4)]]
    return make("Wok Stir-Fry over Flames", [bowl, rim, grip, loop] + stem + food + motion + fire + ring)


@design("kitchen_grill_pan_steak", T)
def grill_pan_steak(rng):
    pan = rrect(-2.6, -2.2, 1.6, 2.0, 0.4)
    inner = rrect(-2.35, -1.95, 1.35, 1.75, 0.3)
    handle = chain([(1.6, 0.25)], [(3.4, 0.35)], arc(3.4, 0.0, 0.35, math.pi / 2, -math.pi / 2, 10), [(1.6, -0.25)])
    hole = rrect(2.8, -0.12, 3.4, 0.12, 0.12)
    steaks, tests, extra = [], [], []
    for (cx, cy), rx, ry, a in [((-1.25, 0.75), 0.95, 0.7, 0.35), ((-0.15, -0.85), 1.05, 0.72, -0.25)]:
        c, s = math.cos(a), math.sin(a)

        def P(x, y, cx=cx, cy=cy, c=c, s=s):
            return (cx + x * c - y * s, cy + x * s + y * c)
        steaks.append([P(rx * (1 + 0.07 * math.sin(3 * t)) * math.cos(t), ry * (1 + 0.07 * math.sin(3 * t)) * math.sin(t)) for t in [TAU * i / 80 for i in range(81)]])
        extra.append([P(0.8 * rx * math.cos(t), 0.75 * ry * math.sin(t)) for t in [0.4 + 2.3 * i / 20 for i in range(21)]])
        extra += [[P(-0.45 + 0.45 * k - 0.25, -0.4), P(-0.45 + 0.45 * k + 0.25, 0.35)] for k in range(3)]

        def inside(p, cx=cx, cy=cy, c=c, s=s, rx=rx, ry=ry):
            dx, dy = p[0] - cx, p[1] - cy
            return ((dx * c + dy * s) / (rx * 1.12)) ** 2 + ((-dx * s + dy * c) / (ry * 1.12)) ** 2 < 1
        tests.append(inside)
    ridges = []
    for k in range(-5, 5):
        y = 0.38 * k + 0.1
        ridges += clip_out([(-2.35 + 0.05 * i, y) for i in range(75)], lambda p: any(t(p) for t in tests))
    sprig = [[(0.3, 1.0), (1.1, 1.5)]] + [leaf(0.3 + 0.25 * k, 1.0 + 0.16 * k, 0.4, a, 0.3) for k in range(4) for a in (1.6, -0.5)][1:]
    return make("Grill Pan with Two Steaks", [pan, inner, handle, hole] + steaks + extra + ridges + sprig)


def _in_steak(p):
    x, y = p
    return ((x + 0.65) / 1.45) ** 2 + ((y - 0.05) / 1.55) ** 2 < 1.05


# ---------------------------------------------------------------- knives ---

@design("kitchen_knife_block", T)
def knife_block(rng):
    block = poly((-2.4, -2.6), (1.6, -2.6), (1.6, -1.6), (-1.4, 0.8), (-2.4, 0.8))
    feet = [rect(-2.2, -2.8, -1.6, -2.6), rect(0.8, -2.8, 1.4, -2.6)]
    ang = math.radians(-39)
    handles, hints = [], []
    for k, (t, L) in enumerate([(0.12, 1.5), (0.3, 1.9), (0.48, 1.7), (0.66, 1.9), (0.84, 1.4)]):
        x, y = 1.6 - 3.0 * t, -1.6 + 2.4 * t
        handles.append(place(rrect(-0.22, 0.05, 0.22, L, 0.18), x, y, ang))
        handles.append(place([(-0.26, 0.05), (0.26, 0.05)], x, y, ang))
        for f in (0.4, 0.8):
            hx, hy = place([(0, L * f)], x, y, ang)[0]
            hints.append(eye(hx, hy, 0.07))
    grain = [wave(-2.2, -0.2, y, 0.08, 1.5, 30) for y in (-2.1, -1.5, -0.9)]
    loose = [poly((-2.8, -3.2), (0.2, -3.2), (0.2, -2.95), closed=False)]
    knife = chain([(0.2, -2.95)], quad((0.2, -2.95), (-1.6, -2.85), (-2.8, -3.2), 20))
    handle = rrect(0.2, -3.3, 2.0, -2.85, 0.15)
    return make("Knife Block Set", [block, knife, handle] + feet + handles + grain + loose, hints + [eye(0.8, -3.07, 0.07), eye(1.5, -3.07, 0.07)])


@design("kitchen_cutting_board", T)
def cutting_board(rng):
    board = chain([(1.8, 0.45)], [(1.8, 1.1)], arc(1.5, 1.1, 0.3, 0, math.pi / 2, 6), [(-2.5, 1.4)], arc(-2.5, 1.1, 0.3, math.pi / 2, math.pi, 6),
                  [(-2.8, -1.5)], arc(-2.5, -1.5, 0.3, math.pi, 1.5 * math.pi, 6), [(1.5, -1.8)], arc(1.5, -1.5, 0.3, -math.pi / 2, 0, 6), [(1.8, -0.45)],
                  [(2.6, -0.45)], arc(2.6, 0, 0.45, -math.pi / 2, math.pi / 2, 12), [(1.8, 0.45)])
    hole = circle(2.65, 0, 0.18, 14)
    blade = chain([(-2.2, 0.75)], quad((-2.2, 0.75), (-1.0, -0.15), (0.6, -0.2), 20), [(0.6, 0.55)], [(-2.2, 0.75)])
    handle = rrect(0.6, -0.15, 2.1, 0.45, 0.2)
    bolster = [[(0.85, -0.15), (0.85, 0.45)]]
    slices = []
    for x, y, r in [(-1.8, -0.9, 0.42), (-0.9, -1.1, 0.4), (0.0, -1.05, 0.38), (0.9, -1.15, 0.36)]:
        slices += [circle(x, y, r, 26), circle(x, y, r * 0.45, 16)]
    return make("Cutting Board and Chef's Knife", [board, hole, blade, handle] + bolster + slices, [eye(1.35, 0.15, 0.07), eye(1.75, 0.15, 0.07)])


# ---------------------------------------------------------------- baking ---

def whisk(x, y, ang, L=2.4, w=0.85, handle=1.6):
    loops = [rrect(-0.16, -handle, 0.16, 0, 0.12)]
    for f in (0.3, 0.65, 1.0):
        ww = w * f
        loops.append(chain(cubic((0, 0), (ww * 0.4, 0.5), (ww * 1.2, L * 0.85), (0, L), 20),
                           cubic((0, L), (-ww * 1.2, L * 0.85), (-ww * 0.4, 0.5), (0, 0), 20)))
    return [place(p, x, y, ang) for p in loops]


@design("kitchen_whisk_bowl", T)
def whisk_bowl(rng):
    bowl = chain([(-2.8, -0.2)], cubic((-2.8, -0.2), (-2.6, -2.6), (2.6, -2.6), (2.8, -0.2), 40))
    rim = ellipse(0, -0.2, 2.8, 0.45, 120)
    batter = clip_out(ellipse(0, -0.3, 2.45, 0.32, 110), lambda p: abs(p[0] - 0.25) < 0.5 and p[1] > -0.3)
    base = [[(-1.2, -2.0), (-1.4, -2.4), (1.4, -2.4), (1.2, -2.0)]]
    w = whisk(0.75, 0.55, math.radians(150), 1.9, 0.75, 2.0)
    loops = [s for p in w[1:] for s in clip_out(p, lambda q: q[1] < -0.25)]
    drops = [lens((2.6, 1.8), (2.6, 1.3), 0.35, 10), lens((-2.4, 1.0), (-2.4, 0.6), 0.35, 10), lens((-1.9, 1.9), (-1.9, 1.5), 0.35, 10)]
    return make("Whisk in a Mixing Bowl", [bowl, rim, w[0]] + batter + base + loops + drops)


@design("kitchen_rolling_pin", T)
def rolling_pin(rng):
    dough = blob(0, -0.8, 2.6, 0.06, 0.5, 120)
    dough = [(x, -0.8 + (y + 0.8) * 0.75) for x, y in dough]
    cut = [star(-1.3, -1.0, 0.55, 5, 0.45), heart(0.1, -1.45, 0.45), circle(1.35, -0.9, 0.45, 30), circle(-0.2, -0.2, 0.4, 30)]
    pin = [place(rrect(-1.7, -0.42, 1.7, 0.42, 0.15), 0.2, 1.6, 0.18),
           place(chain([(-1.7, 0.18)], [(-2.6, 0.18)], arc(-2.6, 0, 0.18, math.pi / 2, 1.5 * math.pi, 8), [(-1.7, -0.18)]), 0.2, 1.6, 0.18),
           place(chain([(1.7, 0.18)], [(2.6, 0.18)], arc(2.6, 0, 0.18, math.pi / 2, -math.pi / 2, 8), [(1.7, -0.18)]), 0.2, 1.6, 0.18)]
    grain = [place([(-1.3, 0.1), (1.3, 0.1)], 0.2, 1.6, 0.18)]
    cutter = [place(heart(0, 0, 0.45), 2.3, -2.5, 0.3)]
    return make("Rolling Pin and Cookie Dough", [dough] + cut + pin + grain + cutter, [eye(x, y, 0.07) for x, y in [(-2.6, 0.6), (-2.2, 0.9), (2.7, 0.3), (-2.9, -2.3), (2.5, 0.75)]])


@design("kitchen_stand_mixer", T)
def stand_mixer(rng):
    base = rrect(-2.7, -2.9, 2.3, -2.35, 0.2)
    column = [cubic((-2.45, -2.35), (-2.2, -1.0), (-2.6, -0.2), (-2.4, 0.35), 20),
              cubic((-1.25, -2.35), (-1.05, -1.2), (-1.35, -0.3), (-1.0, 0.35), 20)]
    head = rrect(-2.8, 0.35, 2.4, 1.85, 0.7)
    nose = [circle(1.95, 1.1, 0.28, 18), [(1.3, 0.35), (1.3, 1.85)]]
    lever = [rrect(-1.9, 1.85, -1.3, 2.1, 0.1)]
    bowl = chain([(-0.5, -0.35)], cubic((-0.5, -0.35), (-0.4, -2.6), (2.0, -2.6), (2.1, -0.35), 30), [(-0.5, -0.35)])
    rim = [rrect(-0.6, -0.35, 2.2, -0.15, 0.08)]
    bowl_handle = arc(2.2, -1.0, 0.35, math.radians(80), math.radians(-80), 10)
    shaft = [[(0.75, 0.35), (0.75, -0.15)]]
    beater = clip_out(lens((0.75, -0.2), (0.75, -1.6), 0.25, 14), lambda p: p[1] > -0.35)
    feet = [rect(-2.4, -3.05, -1.9, -2.9), rect(1.4, -3.05, 1.9, -2.9)]
    sheen = [arc(-0.2, 1.1, 0.5, math.radians(110), math.radians(200), 8)]
    return make("Stand Mixer", [base, head, bowl, bowl_handle] + column + nose + lever + rim + shaft + beater + feet + sheen)


@design("kitchen_hand_mixer", T)
def hand_mixer(rng):
    body = chain([(-2.6, 0.3)], [(-2.6, 1.0)], quad((-2.6, 1.0), (-2.6, 1.4), (-2.1, 1.4), 6), [(1.2, 1.4)], arc(1.2, 0.6, 0.8, math.pi / 2, -math.pi / 2, 16),
                 [(-2.1, -0.2)], quad((-2.1, -0.2), (-2.6, -0.2), (-2.6, 0.3), 6))
    grip = chain([(-2.2, 1.4)], cubic((-2.2, 1.4), (-2.4, 2.8), (0.6, 2.9), (0.6, 1.4), 24))
    grip_in = chain([(-1.6, 1.4)], cubic((-1.6, 1.4), (-1.6, 2.2), (0.0, 2.2), (0.0, 1.4), 20))
    button = rrect(-1.3, 2.45, -0.5, 2.7, 0.1)
    vents = [[(x, 0.1), (x, 0.9)] for x in (-1.8, -1.5, -1.2)]
    beaters = []
    for x in (-0.4, 0.6):
        beaters += [[(x, -0.2), (x, -1.2)], lens((x, -1.2), (x, -2.9), 0.28, 16), [(x, -1.25), (x, -2.85)]]
    cord = chain([(-2.6, 0.6)], [(-2.9, 0.6)],
                 [(-2.95 + 0.18 * math.sin(TAU * 2.5 * i / 40), 0.6 - 2.6 * i / 40) for i in range(41)])
    logo = circle(0.9, 0.6, 0.35, 20)
    return make("Electric Hand Mixer", [body, grip, grip_in, button, cord, logo] + vents + beaters)


@design("kitchen_toaster", T)
def toaster(rng):
    body = rrect(-2.5, -2.3, 2.5, 0.9, 0.7)
    toasts = []
    for x0 in (-1.6, 0.2):
        x1 = x0 + 1.4
        t = chain([(x0, 0.9)], [(x0, 1.8)], arc(x0 + 0.3, 1.9, 0.32, math.radians(200), math.radians(80), 10),
                  arc(x0 + 0.7, 2.25, 0.3, math.radians(150), math.radians(30), 10), arc(x1 - 0.3, 1.9, 0.32, math.radians(100), math.radians(-20), 10),
                  [(x1, 1.8)], [(x1, 0.9)])
        crust = chain([(x0 + 0.15, 0.9)], [(x0 + 0.15, 1.75)], quad((x0 + 0.15, 1.75), (x0 + 0.7, 2.4), (x1 - 0.15, 1.75), 16), [(x1 - 0.15, 0.9)])
        toasts += [t, crust]
    lever = [rrect(2.5, -0.6, 2.95, -0.3, 0.1), [(2.5, 0.5), (2.5, -1.5)]]
    dial = [circle(1.6, -1.3, 0.35, 24), [(1.6, -1.3), (1.75, -1.05)]]
    band = [[(-2.4, -0.4), (2.4, -0.4)]]
    feet = [rrect(-2.0, -2.6, -1.4, -2.3, 0.1), rrect(1.4, -2.6, 2.0, -2.3, 0.1)]
    shine = [arc(-1.3, -1.0, 0.8, math.radians(140), math.radians(220), 10)]
    st = [steam(-0.9, 2.5, 0.7, 0.12), steam(0.9, 2.5, 0.7, 0.12)]
    return make("Pop-Up Toaster with Toast", [body] + toasts + lever + dial + band + feet + shine + st)


# ---------------------------------------------------------------- appliances

@design("kitchen_microwave", T)
def microwave(rng):
    box = rrect(-3.0, -1.8, 3.0, 1.8, 0.25)
    door = rrect(-2.8, -1.6, 1.3, 1.6, 0.15)
    win = rrect(-2.45, -1.25, 0.6, 1.25, 0.2)
    handle = [rrect(0.85, -1.1, 1.05, 1.1, 0.08)]
    plate = ellipse(-0.9, -0.85, 1.25, 0.25, 50)
    dish = chain([(-1.7, -0.75)], bowl_side(-0.9, -0.1, 0.85, 0.5, 20), [(-0.05, -0.1)])
    dish_rim = ellipse(-0.9, -0.1, 0.85, 0.18, 40)
    st = [steam(-1.3, 0.15, 0.8, 0.12), steam(-0.6, 0.15, 0.8, 0.12)]
    display = rrect(1.55, 0.9, 2.75, 1.4, 0.08)
    keys = [rrect(1.55 + 0.42 * c, 0.35 - 0.38 * r, 1.85 + 0.42 * c, 0.6 - 0.38 * r, 0.05) for c in range(3) for r in range(4)]
    start = rrect(1.55, -1.45, 2.75, -1.1, 0.1)
    feet = [rect(-2.6, -2.0, -2.0, -1.8), rect(2.0, -2.0, 2.6, -1.8)]
    return make("Microwave Oven", [box, door, win, plate, dish, dish_rim, display, start] + handle + st + keys + feet)


@design("kitchen_range_stove", T)
def range_stove(rng):
    body = rect(-2.4, -2.8, 2.4, 0.4)
    back = rect(-2.4, 0.4, 2.4, 0.7)
    strip = [[(-2.4, -0.15), (2.4, -0.15)]]
    knobs = [circle(x, 0.13, 0.17, 14) for x in (-1.9, -1.3, 1.3, 1.9)]
    clock = rrect(-0.6, -0.05, 0.6, 0.3, 0.07)
    door = rrect(-2.1, -2.5, 2.1, -0.45, 0.12)
    bar = rrect(-1.6, -0.8, 1.6, -0.62, 0.08)
    win = rrect(-1.5, -2.1, 1.5, -1.05, 0.12)
    rack = [[(-1.4, -1.7), (1.4, -1.7)]]
    feet = [rect(-2.3, -3.0, -1.9, -2.8), rect(1.9, -3.0, 2.3, -2.8)]
    pan = [chain([(-2.2, 0.7)], [(-2.0, 1.15)], [(-0.4, 1.15)], [(-0.2, 0.7)]), [(-2.0, 1.0), (-2.9, 1.25)]]
    pot = [chain([(0.4, 0.7)], [(0.4, 1.9)], [(2.0, 1.9)], [(2.0, 0.7)]), rrect(0.3, 1.9, 2.1, 2.05, 0.05),
           arc(0.4, 1.4, 0.2, math.pi / 2, 1.5 * math.pi, 6), arc(2.0, 1.4, 0.2, -math.pi / 2, math.pi / 2, 6)]
    st = [steam(0.9, 2.15, 0.8, 0.12), steam(1.5, 2.15, 0.8, 0.12)]
    return make("Kitchen Range with Oven", [body, back, clock, door, bar, win] + strip + knobs + rack + feet + pan + pot + st)


@design("kitchen_open_fridge", T)
def open_fridge(rng):
    body = rrect(-2.0, -3.0, 1.0, 3.0, 0.2)
    inner = rect(-1.8, -2.8, 0.8, 2.8)
    shelves = [[(-1.8, y), (0.8, y)] for y in (1.5, 0.3, -0.9)]
    crisper = rrect(-1.7, -2.7, 0.7, -1.9, 0.1)
    crisp_h = [[(-0.7, -2.1), (-0.3, -2.1)]]
    milk = chain([(-1.6, 0.3)], [(-1.6, 1.0)], [(-1.35, 1.3)], [(-1.1, 1.0)], [(-1.1, 0.3)])
    milk2 = [[(-1.6, 1.0), (-1.1, 1.0)]]
    bottle = chain([(-0.6, 0.3)], [(-0.6, 0.85)], quad((-0.6, 0.85), (-0.6, 1.05), (-0.45, 1.15), 6), [(-0.45, 1.35)], [(-0.25, 1.35)], [(-0.25, 1.15)],
                   quad((-0.25, 1.15), (-0.1, 1.05), (-0.1, 0.85), 6), [(-0.1, 0.3)])
    jar = [rrect(0.1, 0.3, 0.65, 0.85, 0.1), rect(0.05, 0.85, 0.7, 1.0)]
    eggs = [ellipse(x, -0.62, 0.17, 0.25, 14) for x in (-1.5, -1.1, -0.7)]
    cake = [poly((0.0, -0.9), (0.65, -0.9), (0.65, -0.35), (0.0, -0.55))]
    freezer = [rrect(-1.6, 1.7, 0.6, 2.6, 0.1)]
    door = poly((1.0, 3.0), (2.9, 2.5), (2.9, -2.5), (1.0, -3.0))
    bins = [[(1.15, y + 0.3), (2.75, y - 0.1)] for y in (1.0, -0.4, -1.8)]
    dbottles = [poly((1.4, 1.27), (1.4, 1.9), (1.55, 2.1), (1.7, 1.9), (1.7, 1.2), closed=False),
                poly((2.0, 1.15), (2.0, 1.8), (2.15, 2.0), (2.3, 1.8), (2.3, 1.08), closed=False),
                poly((1.4, -0.13), (1.4, 0.4), (1.7, 0.4), (1.7, -0.2), closed=False)]
    handle = [rrect(2.6, -0.6, 2.75, 0.6, 0.06)]
    return make("Open Refrigerator", [body, inner, crisper, milk, bottle, door] + shelves + crisp_h + milk2 + jar + eggs + cake + freezer + bins + dbottles + handle)


@design("kitchen_scale", T)
def kitchen_scale(rng):
    body = chain([(-1.5, 0.2)], [(-1.9, -2.6)], quad((-1.9, -2.6), (-1.9, -2.9), (-1.6, -2.9), 6), [(1.6, -2.9)], quad((1.6, -2.9), (1.9, -2.9), (1.9, -2.6), 6),
                 [(1.5, 0.2)], [(-1.5, 0.2)])
    dial = [circle(0, -1.3, 1.15, 70), circle(0, -1.3, 0.95, 60)]
    ticks = [[(0.95 * math.cos(a), -1.3 + 0.95 * math.sin(a)), (0.72 * math.cos(a), -1.3 + 0.72 * math.sin(a))] for a in [math.pi / 2 - k * TAU / 12 for k in range(12)]]
    needle = [poly((0, -1.3), (0.45, -0.7), closed=False)]
    stem = rect(-0.25, 0.2, 0.25, 0.6)
    plat = ellipse(0, 0.75, 2.0, 0.2, 80)
    bowl = chain([(-1.6, 2.4)], cubic((-1.6, 2.4), (-1.5, 0.75), (1.5, 0.75), (1.6, 2.4), 30))
    rim = ellipse(0, 2.4, 1.6, 0.25, 70)
    flour = clip_out(scallop(0, 2.4, 1.2, 0.6, 0.25, math.pi - 0.25, 4, 0.1, 50), lambda p: p[1] < 2.35)
    return make("Kitchen Scale with Flour Bowl", [body, stem, plat, bowl, rim] + dial + ticks + needle + flour, [eye(0, -1.3, 0.1)])


@design("kitchen_measuring_cups", T)
def measuring_cups(rng):
    out = []
    for x, w, h in [(-2.0, 1.0, 1.4), (-0.15, 0.85, 1.2), (1.4, 0.68, 1.0), (2.6, 0.5, 0.8)]:
        top = -1.0 + h
        cup = chain([(x - w, top)], [(x - w * 0.8, -2.2)], quad((x - w * 0.8, -2.2), (x - w * 0.8, -2.5), (x - w * 0.5, -2.5), 6), [(x + w * 0.5, -2.5)],
                    quad((x + w * 0.5, -2.5), (x + w * 0.8, -2.5), (x + w * 0.8, -2.2), 6), [(x + w, top)])
        rim = ellipse(x, top, w, 0.2 * w, 40)
        L = 1.2 + 0.4 * w
        hd = place(chain([(0, 0.12)], [(L, 0.15)], arc(L, 0, 0.15, math.pi / 2, -math.pi / 2, 6), [(0, -0.12)]), x + w * 0.9, top, math.radians(55))
        hole = place(circle(L - 0.12, 0, 0.08, 8), x + w * 0.9, top, math.radians(55))
        mark = [[(x - w * 0.5, top - h * 0.45), (x - w * 0.15, top - h * 0.45)]]
        out += [cup, rim, hd, hole] + mark
    return make("Nested Measuring Cups", out)


@design("kitchen_measuring_spoons", T)
def measuring_spoons(rng):
    ring = circle(0, 2.4, 0.4, 30)
    out = [ring]
    for ang, r in [(-48, 0.72), (-17, 0.62), (15, 0.52), (45, 0.44)]:
        a = math.radians(ang)
        L = 3.6
        spoon = chain([(0.1, 0)], [(0.14, -L + r * 1.6)], arc(0, -L + r * 0.4, r, math.radians(80), math.radians(-260), 30)[1:-1], [(-0.14, -L + r * 1.6)], [(-0.1, 0)],
                      arc(0, 0, 0.1, math.pi, 0, 6))
        out.append(place(spoon, 0, 2.05, a))
        out.append(place(ellipse(0, -L + r * 0.4, r * 0.65, r * 0.55, 24), 0, 2.05, a))
    return make("Measuring Spoons on a Ring", out)


@design("kitchen_utensil_crock", T)
def utensil_crock(rng):
    crock = chain([(-1.5, 0.0)], cubic((-1.5, 0.0), (-1.9, -1.0), (-1.7, -2.6), (-1.3, -2.8), 20), [(1.3, -2.8)],
                  cubic((1.3, -2.8), (1.7, -2.6), (1.9, -1.0), (1.5, 0.0), 20))
    lip = rrect(-1.65, 0.0, 1.65, 0.3, 0.12)
    bands = [cubic((-1.75, -0.9), (-0.6, -1.0), (0.6, -1.0), (1.75, -0.9), 20), cubic((-1.75, -1.2), (-0.6, -1.3), (0.6, -1.3), (1.75, -1.2), 20)]
    heart_ = heart(0, -1.95, 0.4)
    # spatula / turner
    turner = [place(rrect(-0.1, 0.0, 0.1, 1.8, 0.08), -1.0, 0.3, 0.35), place(rrect(-0.45, 1.8, 0.45, 2.9, 0.15), -1.0, 0.3, 0.35)]
    turner += [place([(dx, 2.05), (dx, 2.65)], -1.0, 0.3, 0.35) for dx in (-0.2, 0.0, 0.2)]
    # wooden spoon
    spoon = [place(chain([(-0.09, 0.0)], [(-0.09, 1.9)], arc(0, 2.35, 0.38, math.radians(-110), math.radians(290), 30), [(0.09, 1.9)], [(0.09, 0.0)]), -0.25, 0.3, 0.08)]
    # whisk
    wk = whisk(0.5, 1.7, -0.12, 1.4, 0.55, 1.4)
    wk = [place(rrect(-0.16, -1.4, 0.16, 0, 0.12), 0.5, 1.7, -0.12)] + wk[1:]
    # ladle (hanging bowl at the top)
    ladle = [place(chain([(-0.09, 0.0)], [(-0.09, 2.2)], arc(0, 2.3, 0.1, math.pi, 0, 6), [(0.09, 2.2)], [(0.09, 0.0)]), 1.1, 0.3, -0.35),
             place(chain(arc(0.45, 2.3, 0.45, math.pi, 2 * math.pi, 16), [(-0.0, 2.3)]), 1.1, 0.3, -0.35)]
    return make("Utensil Crock with Spatulas", [crock, lip, heart_] + bands + turner + spoon + wk + ladle)


@design("kitchen_box_grater", T)
def box_grater(rng):
    front = poly((-1.6, -2.8), (0.8, -2.8), (0.5, 1.6), (-1.3, 1.6))
    side = poly((0.8, -2.8), (2.0, -2.2), (1.6, 1.9), (0.5, 1.6), closed=False)
    top = poly((-1.3, 1.6), (-0.4, 1.9), (1.6, 1.9), closed=False)
    handle = chain([(-0.7, 1.75)], [(-0.7, 2.6)], quad((-0.7, 2.6), (0.15, 3.3), (1.0, 2.6), 16), [(1.0, 1.8)])
    holes = []
    for r in range(6):
        y = -2.3 + 0.6 * r
        frac = (y + 2.8) / 4.4
        xl, xr = -1.6 + 0.3 * frac, 0.8 - 0.3 * frac
        n = 4
        for c in range(n):
            x = xl + 0.35 + (xr - xl - 0.7) * c / (n - 1)
            holes.append(lens((x - 0.17, y - 0.1), (x + 0.17, y + 0.1), 0.35, 8))
    big = [circle(1.4 - 0.08 * k, -1.6 + 0.85 * k, 0.2, 14) for k in range(4)]
    cheese = poly((-3.0, -2.8), (-1.8, -2.8), (-1.8, -2.0), (-3.0, -2.5))
    shreds = [quad((x, -2.8), (x + 0.15, -2.6), (x + 0.3, -2.75), 6) for x in (1.0, 1.5, 2.0)]
    return make("Box Cheese Grater", [front, side, top, handle, cheese] + holes + big + shreds + [circle(-2.3, -2.5, 0.12, 10)])


@design("kitchen_colander", T)
def colander(rng):
    bowl = chain([(-2.6, 0.6)], cubic((-2.6, 0.6), (-2.5, -1.9), (2.5, -1.9), (2.6, 0.6), 40))
    rim = ellipse(0, 0.6, 2.6, 0.45, 120)
    inner = ellipse(0, 0.6, 2.3, 0.33, 100)
    foot = chain([(-1.3, -1.25)], [(-1.5, -2.0)], [(1.5, -2.0)], [(1.3, -1.25)])
    handles = [chain([(-2.6, 0.5)], [(-3.2, 0.7)], [(-3.2, 0.3)], [(-2.55, 0.1)]), chain([(2.6, 0.5)], [(3.2, 0.7)], [(3.2, 0.3)], [(2.55, 0.1)])]
    holes = []
    for y, xs in [(-0.05, 7), (-0.6, 6), (-1.05, 4)]:
        half = 2.2 if y > -0.3 else (1.8 if y > -0.8 else 1.15)
        for k in range(xs):
            holes.append(circle(-half + 2 * half * k / (xs - 1), y, 0.13, 10))
    pasta = [quad((-1.6, 0.65), (-0.9, 1.4), (-0.2, 0.6), 12), quad((-0.6, 0.62), (0.2, 1.6), (1.0, 0.62), 12), quad((0.4, 0.6), (1.2, 1.3), (1.8, 0.65), 12)]
    drops = [lens((x, -2.25), (x, -2.6), 0.4, 8) for x in (-0.8, 0.0, 0.8)]
    st = [steam(-0.6, 1.6, 1.0, 0.15), steam(0.6, 1.7, 1.0, 0.15)]
    return make("Colander Draining Pasta", [bowl, rim, inner, foot] + handles + holes + pasta + drops + st)


@design("kitchen_salt_pepper", T)
def salt_pepper(rng):
    half = chain([(0.0, 2.55)], [(0.3, 2.55)], quad((0.3, 2.55), (0.75, 2.5), (0.75, 2.1), 8), [(0.55, 1.95)], [(0.45, 1.7)],
                 cubic((0.45, 1.7), (1.05, 1.0), (1.05, 0.0), (0.6, -0.8), 20), cubic((0.6, -0.8), (0.45, -1.4), (0.6, -2.0), (0.9, -2.4), 12), [(0.9, -2.8)], [(0.0, -2.8)])
    mill_shape = [(x + 1.3, y) for x, y in profile(half)]
    knob = circle(1.3, 2.75, 0.2, 16)
    mill_lines = [[(0.75, 1.95), (1.85, 1.95)], [(0.4, -2.4), (2.2, -2.4)], [(0.75, -0.8), (1.85, -0.8)]]
    salt = profile([(0.0, 0.9), (0.55, 0.8), (0.9, 0.35), (0.95, 0.0), (0.95, -2.7), (0.0, -2.8)])
    salt = [(x - 1.4, y) for x, y in salt]
    neck = [[(-2.33, 0.0), (-0.47, 0.0)], [(-2.33, -0.25), (-0.47, -0.25)]]
    grains = [circle(x, y, 0.08, 8) for x, y in [(-1.8, -1.2), (-1.0, -1.6), (-1.5, -2.1), (-1.2, -0.8)]]
    holes = [eye(-1.4 + dx, 0.55 + dy, 0.06) for dx, dy in [(-0.3, -0.05), (0.0, 0.05), (0.3, -0.05)]]
    pep = [eye(x, -2.95, 0.07) for x in (0.0, 0.4, 2.6)]
    return make("Salt Shaker and Pepper Mill", [mill_shape, knob, salt] + mill_lines + neck + grains, holes + pep)


@design("kitchen_spice_rack", T)
def spice_rack(rng):
    sides = [chain([(-2.9, -2.8)], [(-2.9, 2.2)], arc(-2.6, 2.2, 0.3, math.pi, 0, 8), [(-2.3, -2.8)], [(-2.9, -2.8)]),
             chain([(2.3, -2.8)], [(2.3, 2.2)], arc(2.6, 2.2, 0.3, math.pi, 0, 8), [(2.9, -2.8)], [(2.3, -2.8)])]
    shelves = [rect(-2.3, -2.8, 2.3, -2.5), rect(-2.3, -0.2, 2.3, 0.1)]
    rails = [[(-2.3, -1.6), (2.3, -1.6)], [(-2.3, 1.0), (2.3, 1.0)]]
    out = sides + shelves + rails
    marks = [lambda x, y: star(x, y, 0.22, 5, 0.45), lambda x, y: heart(x, y, 0.2), lambda x, y: lens((x - 0.2, y - 0.1), (x + 0.2, y + 0.1), 0.35, 8),
             lambda x, y: circle(x, y, 0.18, 12)]
    for row, yb in enumerate((-2.5, 0.1)):
        for k in range(4):
            x = -1.65 + 1.1 * k
            out.append(rrect(x - 0.42, yb, x + 0.42, yb + 1.6, 0.12))
            out.append(rrect(x - 0.38, yb + 1.6, x + 0.38, yb + 2.0, 0.06))
            out.append(rect(x - 0.32, yb + 0.25, x + 0.32, yb + 0.9))
            out.append(marks[(k + row) % 4](x, yb + 0.58))
    return make("Wall Spice Rack", out)


@design("kitchen_mortar_pestle", T)
def mortar_pestle(rng):
    bowl = chain([(-2.2, 0.4)], cubic((-2.2, 0.4), (-2.2, -1.8), (-1.0, -2.0), (-0.9, -2.1), 20), [(-1.2, -2.7)], [(1.2, -2.7)], [(0.9, -2.1)],
                 cubic((0.9, -2.1), (1.0, -2.0), (2.2, -1.8), (2.2, 0.4), 20))
    rim = ellipse(0, 0.4, 2.2, 0.45, 100)
    inner = clip_out(ellipse(0, 0.4, 1.85, 0.32, 90), in_rect(-0.1, 0.0, 1.2, 1.0))
    pestle = place(chain([(-0.28, 0.0)], [(-0.4, 2.9)], arc(0, 2.9, 0.4, math.pi, 0, 12), [(0.28, 0.0)]), 0.5, 0.15, -0.45)
    tip = place(arc(0, 0.0, 0.28, math.pi, 2 * math.pi, 8), 0.5, 0.15, -0.45)
    tip = clip_out(tip, lambda p: p[1] < 0.3)
    leaves = [leaf(-2.9, -2.6, 0.9, 0.5), leaf(-2.6, -2.7, 0.8, 1.4), leaf(2.2, -2.7, 0.9, 1.9)]
    corns = [circle(x, y, 0.13, 10) for x, y in [(2.5, -2.4), (2.8, -2.0), (2.9, -2.6), (-1.4, 0.45), (-0.9, 0.55)]]
    return make("Mortar and Pestle with Herbs", [bowl, rim, pestle] + inner + tip + leaves + corns)


@design("kitchen_apron", T)
def apron(rng):
    rail = rrect(-2.8, 2.55, 2.8, 2.85, 0.1)
    peg = [circle(0, 2.4, 0.18, 12)]
    body = chain([(-0.8, 1.2)], [(0.8, 1.2)], quad((0.8, 1.2), (0.9, 0.2), (1.6, 0.0), 12), [(1.9, -2.5)], quad((1.9, -2.5), (1.9, -2.8), (1.6, -2.8), 6),
                 [(-1.6, -2.8)], quad((-1.6, -2.8), (-1.9, -2.8), (-1.9, -2.5), 6), [(-1.6, 0.0)], quad((-1.6, 0.0), (-0.9, 0.2), (-0.8, 1.2), 12))
    strap = [chain([(-0.6, 1.2)], quad((-0.6, 1.2), (-0.4, 2.3), (0, 2.25), 12)), chain([(0.6, 1.2)], quad((0.6, 1.2), (0.4, 2.3), (0, 2.25), 12))]
    ties = [[(-1.6, -0.05)] + [(-1.8 - 0.12 * math.sin(TAU * i / 20), -0.05 - 1.6 * i / 20) for i in range(1, 21)],
            [(1.6, -0.05)] + [(1.8 + 0.12 * math.sin(TAU * i / 20), -0.05 - 1.6 * i / 20) for i in range(1, 21)]]
    waist = [[(-1.6, 0.0), (1.6, 0.0)], [(-1.62, -0.25), (1.62, -0.25)]]
    pocket = [rrect(-1.2, -1.9, 1.2, -0.8, 0.1), [(0, -1.9), (0, -0.8)]]
    spoon = [[(-0.85, -0.8), (-0.85, 0.3)], ellipse(-0.85, 0.55, 0.2, 0.3, 16)]
    heart_ = [heart(0, 0.6, 0.35)]
    return make("Apron on a Peg", [rail, body] + peg + strap + ties + waist + pocket + spoon + heart_)


def mitt():
    return chain([(-0.8, -1.4)], [(-0.85, 0.7)], arc(0.0, 0.7, 0.85, math.pi, 0.1, 20), [(0.82, 0.2)],
                 cubic((0.82, 0.2), (1.1, 0.6), (1.6, 0.6), (1.45, 0.1), 10), cubic((1.45, 0.1), (1.3, -0.4), (0.9, -0.6), (0.8, -0.9), 10), [(0.8, -1.4)])


@design("kitchen_oven_mitts", T)
def oven_mitts(rng):
    out = []
    for x, a, flip in [(-1.55, 0.15, True), (1.55, -0.15, False)]:
        m = mitt()
        cuff = rrect(-0.95, -2.0, 0.95, -1.4, 0.12)
        loop = arc(0, -2.2, 0.2, 0, TAU, 10)
        quilt = [[(-0.6, -1.1), (0.6, 0.1)], [(-0.6, -0.3), (0.3, 0.6)], [(0.6, -1.1), (-0.6, 0.1)], [(0.6, -0.3), (-0.3, 0.6)]]
        parts = [m, cuff, loop] + quilt
        if flip:
            parts = mirror_all(parts)
        out += [place(p, x, 0.3, a, 1.25) for p in parts]
    return make("Pair of Quilted Oven Mitts", out)


@design("kitchen_recipe_book", T)
def recipe_book(rng):
    left = chain([(0, -2.2)], quad((0, -2.2), (-1.4, -1.8), (-2.9, -2.3), 14), [(-2.9, 1.9)], quad((-2.9, 1.9), (-1.4, 2.4), (0, 2.0), 14))
    right = mirror_x(left)
    spine = [[(0, 2.0), (0, -2.2)]]
    cover = chain([(-2.9, -2.3)], [(-3.0, -2.5)], quad((-3.0, -2.5), (-1.4, -2.0), (0, -2.4), 14), quad((0, -2.4), (1.4, -2.0), (3.0, -2.5), 14), [(2.9, -2.3)])
    lines = []
    for k in range(6):
        y = 0.5 - 0.42 * k
        lines.append([(-2.5, y), (-0.4 - (0.6 if k % 3 == 2 else 0), y)])
    for k in range(8):
        y = 1.5 - 0.42 * k
        lines.append([(0.4, y), (2.5 - (0.7 if k % 4 == 3 else 0), y)])
    pic = [chain([(-2.2, 1.05)], bowl_side(-1.45, 1.05, 0.75, 0.45, 16), [(-0.7, 1.05)]), ellipse(-1.45, 1.05, 0.75, 0.13, 30), steam(-1.7, 1.25, 0.5, 0.08), steam(-1.2, 1.25, 0.5, 0.08)]
    ribbon = [poly((0.15, -2.25), (0.15, -3.1), (0.35, -2.9), (0.55, -3.1), (0.55, -2.25), closed=False)]
    return make("Open Recipe Book", [left, right, cover] + spine + lines + pic + ribbon)


# ---------------------------------------------------------------- dishes ---

@design("kitchen_pizza_cutter", T)
def pizza_cutter(rng):
    crust = circle(-0.4, 0, 2.6, 160)
    inner = circle(-0.4, 0, 2.2, 140)
    cuts = [[(-0.4 + 2.6 * math.cos(a), 2.6 * math.sin(a)), (-0.4 - 2.6 * math.cos(a), -2.6 * math.sin(a))] for a in (0.3, 0.3 + math.pi / 3, 0.3 + 2 * math.pi / 3)]
    pep = []
    for k in range(6):
        a = 0.3 + math.pi / 6 + k * math.pi / 3
        pep.append(circle(-0.4 + 1.35 * math.cos(a), 1.35 * math.sin(a), 0.33, 22))
    olives = [circle(-0.4 + 0.65 * math.cos(a), 0.65 * math.sin(a), 0.15, 12) for a in (0.0, 2.1, 4.2)]
    basil = [leaf(-0.4 + 1.8 * math.cos(a), 1.8 * math.sin(a), 0.45, a + 2.0) for a in (1.3, 3.2, 5.3)]
    wheel = [circle(2.5, -2.0, 0.7, 40), circle(2.5, -2.0, 0.15, 10)]
    handle = [place(rrect(-0.2, 0.0, 0.2, 1.8, 0.18), 2.5, -2.0, math.radians(-55)), place(poly((-0.2, 0.0), (0.2, 0.0), (0.12, 0.5), (-0.12, 0.5)), 2.5, -2.0, math.radians(-55))]
    return make("Pepperoni Pizza with Cutter", [crust, inner] + cuts + pep + olives + basil + wheel + handle)


@design("kitchen_spaghetti_meatballs", T)
def spaghetti_meatballs(rng):
    plate = ellipse(0, -1.3, 3.0, 1.2, 140)
    well = ellipse(0, -1.2, 2.2, 0.8, 110)
    mound = chain([(-2.0, -1.3)], cubic((-2.0, -1.3), (-2.2, 0.6), (2.2, 0.6), (2.0, -1.3), 40))
    balls = [(-0.8, 0.45), (0.6, 0.55), (-0.1, 1.05)]
    noodles = []
    for k in range(5):
        y = -1.1 + 0.35 * k
        w = 1.9 - 0.3 * k
        n = [(x, y + 0.08 * math.sin(6 * x + k)) for x in [-w + 2 * w * i / 40 for i in range(41)]]
        noodles += clip_out(n, lambda p: any((p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2 < 0.52 ** 2 for c in balls) or (p[0] - 1.45) ** 2 + (p[1] + 0.6) ** 2 < 0.45 ** 2)
    sauce = [quad((-0.6, 0.05), (0.0, -0.2), (0.4, 0.15), 8)]
    basil = [leaf(-0.2, 1.4, 0.6, 1.2), leaf(-0.1, 1.45, 0.55, 0.3)]
    fork_local = [rrect(-0.13, 0.0, 0.13, 2.4, 0.12), poly((-0.13, 0.0), (0.13, 0.0), (0.32, -0.35), (-0.32, -0.35))] + \
        [[(x, -0.35), (x, -0.85)] for x in (-0.28, -0.09, 0.09, 0.28)]
    fork = [place(p, 1.75, 0.2, -0.45) for p in fork_local]
    swirl = [spiral(1.45, -0.6, 0.1, 0.42, 2.5, 60)]
    return make("Spaghetti and Meatballs", [plate, well, mound] + [circle(x, y, 0.5, 30) for x, y in balls] + noodles + sauce + basil + fork + swirl)


@design("kitchen_pasta_machine", T)
def pasta_machine(rng):
    body = rect(-1.5, -0.5, 1.5, 1.3)
    plates = [rrect(-1.75, -0.7, -1.5, 1.5, 0.08), rrect(1.5, -0.7, 1.75, 1.5, 0.08)]
    sheet_in = chain([(-1.2, 1.3)], [(-0.7, 2.9)], [(-0.7 + 2.4 * i / 24, 2.9 + 0.1 * math.sin(TAU * i / 12)) for i in range(25)], [(1.2, 1.3)])
    sheet_out = chain([(-1.2, -0.5)], [(-1.25, -1.4)], [(-1.35, -2.9)], [(-1.35 + 2.7 * i / 24, -2.9 + 0.1 * math.sin(TAU * i / 12)) for i in range(25)],
                      [(1.25, -1.4)], [(1.2, -0.5)])
    cuts = [[(x, -0.7), (x, -2.75)] for x in (-0.8, -0.3, 0.2, 0.7)]
    table = []
    for y in (-1.4, -1.7):
        table += clip_out([(-3.0 + 6.0 * i / 120, y) for i in range(121)], lambda p: abs(p[0]) < 1.33)
    crank = [circle(1.95, 0.4, 0.2, 12), tube([(2.1, 0.55), (2.75, 1.7)], 0.22), rrect(2.55, 1.7, 2.95, 2.7, 0.18)]
    dial = [circle(-2.05, 0.6, 0.3, 20), [(-2.05, 0.6), (-2.05, 0.9)]]
    gap = [[(-1.2, 1.0), (1.2, 1.0)], [(-1.2, -0.2), (1.2, -0.2)]]
    return make("Pasta Machine Rolling Dough", [body, sheet_in, sheet_out] + plates + cuts + table + crank + dial + gap,
                [eye(x, y, 0.07) for x in (-1.62, 1.62) for y in (-0.45, 1.25)])


@design("kitchen_sushi", T)
def sushi(rng):
    board = rrect(-3.0, -1.6, 3.0, -0.9, 0.15)
    feet = [rect(-2.4, -2.1, -1.8, -1.6), rect(1.8, -2.1, 2.4, -1.6)]
    rolls = []
    for x in (-2.1, -1.0, 0.1):
        rolls += [chain([(x - 0.5, -0.9)], [(x - 0.5, -0.2)], [(x + 0.5, -0.2)], [(x + 0.5, -0.9)]), ellipse(x, -0.2, 0.5, 0.25, 30), ellipse(x, -0.2, 0.36, 0.17, 26),
                  ellipse(x, -0.2, 0.14, 0.08, 12)]
    nigiri = []
    for x in (1.35, 2.45):
        nigiri += [chain([(x - 0.5, -0.9)], cubic((x - 0.5, -0.9), (x - 0.7, -0.4), (x + 0.7, -0.4), (x + 0.5, -0.9), 16)),
                   chain(cubic((x - 0.65, -0.55), (x - 0.5, 0.2), (x + 0.5, 0.2), (x + 0.65, -0.55), 16), quad((x + 0.65, -0.55), (x, -0.35), (x - 0.65, -0.55), 10))]
        nigiri += [quad((x - 0.25, -0.35), (x - 0.1, -0.0), (x + 0.05, 0.05), 6), quad((x + 0.1, -0.35), (x + 0.25, -0.05), (x + 0.4, -0.05), 6)]
    sticks = [[(-2.8, 1.75), (2.8, 0.6)], [(-2.8, 2.15), (2.8, 0.75)], [(-2.8, 1.75), (-2.8, 2.15)]]
    rest = rrect(1.6, 0.5, 2.3, 0.75, 0.12)
    wasabi = [spiral(-2.4, 0.55, 0.05, 0.3, 1.5, 40)]
    ginger = [lens((-1.0, 0.6), (-0.3, 0.9), 0.35, 10), lens((-0.6, 0.55), (0.1, 0.75), 0.35, 10)]
    return make("Sushi Rolls with Chopsticks", [board, rest] + feet + rolls + nigiri + sticks + wasabi + ginger)


@design("kitchen_tacos", T)
def tacos(rng):
    out, hints = [], []
    for cx, a in [(-1.5, 0.12), (1.5, -0.12)]:
        r = 1.4
        shell = chain(arc(0, 0, r, 0, math.pi, 50), [(r, 0)])
        inner = arc(0, 0, r - 0.22, 0.12, math.pi - 0.12, 40)
        frill = [((r + 0.14 + 0.11 * math.sin(16 * t)) * math.cos(t), (r + 0.14 + 0.11 * math.sin(16 * t)) * math.sin(t)) for t in [0.22 + (math.pi - 0.44) * i / 60 for i in range(61)]]
        bits = [place(rect(-0.15, -0.15, 0.15, 0.15), (r + 0.5) * math.cos(t), (r + 0.5) * math.sin(t), t) for t in (0.6, 1.25, 1.9, 2.55)]
        cheese = [place([(0, 0), (0.35, 0)], (r + 0.35) * math.cos(t), (r + 0.35) * math.sin(t), t + 1.2) for t in (0.95, 1.6, 2.25)]
        out += [place(p, cx, -0.9, a) for p in [shell, inner, frill] + bits + cheese]
        hints += [eye(*place([(dx, dy)], cx, -0.9, a)[0], 0.06) for dx, dy in [(-0.7, 0.3), (-0.2, 0.75), (0.35, 0.35), (0.75, 0.6), (0.0, 0.2), (-0.35, 0.45)]]
    plate = clip_out(ellipse(0, -1.3, 3.2, 0.9, 140), lambda p: p[1] > -0.95)
    rim = clip_out(ellipse(0, -1.3, 2.7, 0.62, 120), lambda p: p[1] > -0.95)
    return make("Plate of Two Tacos", plate + rim + out, hints)


@design("kitchen_burger", T)
def burger(rng):
    top = chain([(-2.4, 0.6)], cubic((-2.4, 0.6), (-2.4, 2.9), (2.4, 2.9), (2.4, 0.6), 40), [(-2.4, 0.6)])
    seeds = [lens((x - 0.12, y), (x + 0.12, y + 0.08), 0.5, 6) for x, y in [(-1.4, 1.5), (-0.6, 2.0), (0.3, 2.1), (1.2, 1.7), (-0.2, 1.4), (0.8, 1.1), (-1.0, 0.95), (1.7, 1.0)]]
    lettuce = chain([(-2.6, 0.55)], [(-2.6 + 5.2 * i / 40, 0.45 + 0.15 * math.sin(i * 1.6)) for i in range(41)][1:])
    tomato = rrect(-2.3, -0.05, 2.3, 0.3, 0.15)
    cheese = chain([(-2.5, -0.1)], [(2.5, -0.1)], [(2.2, -0.55)], [(1.6, -0.35)], [(1.3, -0.9)], [(1.0, -0.35)], [(-0.6, -0.35)], [(-0.9, -0.8)], [(-1.2, -0.35)], [(-2.2, -0.35)], [(-2.5, -0.1)])
    patty = chain([(-2.4, -0.35)], [(-2.4, -1.15)], [(2.4, -1.15)], [(2.4, -0.35)])
    grill = [[(x, -0.7), (x + 0.3, -0.95)] for x in (-1.8, -0.3, 0.3, 1.8)]
    bottom = rrect(-2.3, -2.1, 2.3, -1.15, 0.4)
    pick = [[(0.3, 2.45), (0.3, 3.3)], poly((0.3, 3.3), (1.0, 3.1), (0.3, 2.9))]
    return make("Stacked Cheeseburger", [top, lettuce, tomato, cheese, patty, bottom] + seeds + grill + pick)


@design("kitchen_sub_sandwich", T)
def sub_sandwich(rng):
    board = rrect(-3.2, -2.2, 3.2, -1.85, 0.1)
    bun = rrect(-3.0, -1.85, 3.0, -0.95, 0.4)
    meat = tube(wave(-2.9, 2.9, -0.7, 0.06, 6, 120), 0.4)
    cheese = zigzag(-2.8, 2.8, -0.25, 0.17, 8)
    tomato = [arc(x, -0.05, 0.3, 0, math.pi, 10) for x in (-2.1, -1.05, 0.0, 1.05, 2.1)]
    lettuce = [(-3.1 + 6.2 * i / 90, 0.4 + 0.1 * math.sin(i * 1.3)) for i in range(91)]
    top = chain([(-3.0, 0.55)], cubic((-3.0, 0.55), (-3.0, 2.1), (3.0, 2.1), (3.0, 0.55), 50), [(-3.0, 0.55)])
    seeds = [lens((x - 0.13, y), (x + 0.13, y + 0.06), 0.5, 6) for x, y in [(-2.0, 1.1), (-1.0, 1.45), (0.2, 1.5), (1.3, 1.35), (2.2, 1.0), (-0.4, 1.0), (0.8, 0.95)]]
    picks = [[(-1.5, 1.4), (-1.5, 2.5)], [(1.5, 1.4), (1.5, 2.5)], circle(-1.5, 2.7, 0.22, 16), circle(1.5, 2.7, 0.22, 16)]
    return make("Submarine Sandwich", [board, bun, meat, cheese, top] + tomato + [lettuce] + seeds + picks)


@design("kitchen_ramen", T)
def ramen(rng):
    bowl = chain([(-2.8, 0.0)], cubic((-2.8, 0.0), (-2.7, -2.4), (2.7, -2.4), (2.8, 0.0), 40))
    rim = ellipse(0, 0.0, 2.8, 0.55, 120)
    broth = ellipse(0, -0.05, 2.5, 0.42, 110)
    foot = [[(-1.0, -1.75), (-1.1, -2.2), (1.1, -2.2), (1.0, -1.75)]]
    band = [zigzag(-2.4, 2.4, -0.9, 0.15, 10)]
    egg = [ellipse(-1.4, 0.15, 0.55, 0.35, 30), circle(-1.4, 0.15, 0.18, 14)]
    nori = rect(1.0, -0.1, 1.7, 1.2)
    naruto = [circle(0.2, 0.15, 0.35, 20), spiral(0.2, 0.15, 0.03, 0.22, 1.5, 30)]
    sticks = [[(-0.6, 0.1), (1.6, 3.0)], [(-0.2, 0.05), (2.0, 2.9)]]
    lift = [cubic((-0.45 + 0.2 * k, 0.25), (-0.6 + 0.2 * k, 1.0), (0.4 + 0.2 * k, 1.4), (0.35 + 0.2 * k, 1.75), 16) for k in range(3)]
    rings = [circle(x, y, 0.13, 10) for x, y in [(-0.8, -0.2), (1.4, -0.25), (2.0, 0.0)]]
    st = [steam(-2.0, 0.7, 1.2, 0.18), steam(-1.3, 0.8, 1.2, 0.18)]
    return make("Ramen Noodle Bowl", [bowl, rim, broth, nori] + foot + band + egg + naruto + sticks + lift + rings + st)


@design("kitchen_bread_loaf", T)
def bread_loaf(rng):
    board = rrect(-3.0, -2.5, 2.9, -1.9, 0.2)
    loaf_body = chain([(-2.7, -1.9)], [(-2.7, -0.5)], [(0.3, -0.5)], [(0.3, -1.9)])
    loaf_top = chain([(-2.7, -0.5)], [(-2.95, -0.5)], cubic((-2.95, -0.5), (-3.1, 1.2), (0.5, 1.2), (0.55, -0.5), 30), [(0.3, -0.5)])
    slashes = [quad((x - 0.35, y - 0.2), (x, y + 0.15), (x + 0.35, y - 0.1), 10) for x, y in [(-2.0, 0.05), (-1.2, 0.35), (-0.4, 0.3)]]

    def tomb(x0, x1, top, inset=0.0):
        return chain([(x0 + inset, -1.9 + inset)], [(x0 + inset, -0.4)], cubic((x0 + inset, -0.4), (x0 - 0.2 + inset, top), (x1 + 0.2 - inset, top), (x1 - inset, -0.4), 20),
                     [(x1 - inset, -1.9 + inset)], [(x0 + inset, -1.9 + inset)])
    s1 = tomb(0.7, 2.1, 0.8)
    s1i = tomb(0.7, 2.1, 0.55, 0.17)
    s2 = clip_out(tomb(1.4, 2.8, 1.0), lambda p: 0.68 < p[0] < 2.12 and p[1] < 0.3 + 0.2 * (1 - abs(p[0] - 1.4) / 0.7))
    holes = [eye(x, y, 0.07) for x, y in [(1.1, -0.8), (1.5, -1.3), (1.7, -0.5), (1.2, -1.6), (1.8, -1.0)]]
    knife = [poly((-2.8, 2.2), (0.4, 1.7), (0.4, 1.4), (-2.6, 1.8)), rrect(0.4, 1.35, 2.0, 1.75, 0.15)]
    return make("Bread Loaf on a Board", [board, loaf_body, loaf_top, s1, s1i] + s2 + slashes + knife, holes)


@design("kitchen_baguette_basket", T)
def baguette_basket(rng):
    basket = chain([(-2.0, 0.0)], [(-1.6, -2.8)], [(1.6, -2.8)], [(2.0, 0.0)])
    rim = rrect(-2.2, -0.1, 2.2, 0.3, 0.15)
    weave = []
    for k in range(4):
        y = -0.6 - 0.55 * k
        half = 2.0 - 0.4 * (-y / 2.8)
        weave.append(wave(-half, half, y, 0.1, 6, 60))
    bag = []
    for x, a, L in [(-1.2, 0.35, 4.2), (-0.3, 0.1, 4.8), (0.6, -0.15, 4.5), (1.4, -0.4, 4.0)]:
        c = [(x - math.sin(-a) * 0 + t * math.sin(-a), -1.0 + t * math.cos(a)) for t in [L * i / 20 for i in range(21)]]
        c = [(x - t * math.sin(a), -1.0 + t * math.cos(a)) for t in [L * i / 20 for i in range(21)]]
        b = tube(c, lambda t: 0.62 * min(1.0, 4 * (1 - t) + 0.25, 4 * t + 0.25))
        b = clip_out(b, lambda p: p[1] < 0.3)
        bag += b
        for f in (0.55, 0.7, 0.85):
            px, py = c[int(f * 20)]
            if py > 0.4:
                bag.append([(px - 0.2 * math.cos(a) - 0.1 * math.sin(a) * 0, py - 0.12), (px + 0.2 * math.cos(a), py + 0.12)])
    return make("Basket of Baguettes", [basket, rim] + weave + bag)


@design("kitchen_pretzel", T)
def pretzel(rng):
    c = chain(cubic((-1.9, -1.4), (-0.6, -1.1), (0.4, 0.0), (1.0, 0.8), 24), cubic((1.0, 0.8), (1.6, 1.7), (2.9, 1.3), (2.7, 0.0), 24),
              cubic((2.7, 0.0), (2.5, -1.8), (1.0, -2.5), (0, -2.5), 24), cubic((0, -2.5), (-1.0, -2.5), (-2.5, -1.8), (-2.7, 0.0), 24),
              cubic((-2.7, 0.0), (-2.9, 1.3), (-1.6, 1.7), (-1.0, 0.8), 24), cubic((-1.0, 0.8), (-0.4, 0.0), (0.6, -1.1), (1.9, -1.4), 24))
    p = tube(c, 0.62)
    salt = [eye(x, y, 0.09) for x, y in [(1.9, 1.15), (2.6, 0.6), (-2.0, 1.2), (-2.6, 0.5), (0.0, -2.45), (-1.3, -2.2), (1.3, -2.25), (2.3, -1.2), (-2.3, -1.3)]]
    paper = [zigzag(-3.0, 3.0, -3.0, 0.12, 15)]
    return make("Big Soft Pretzel", [p] + paper, salt)


@design("kitchen_cheese_board", T)
def cheese_board(rng):
    board = chain([(2.2, -0.3)], [(2.2, 0.8)], arc(1.8, 0.8, 0.4, 0, math.pi / 2, 6), [(-2.6, 1.2)],
                  arc(-2.6, 0.8, 0.4, math.pi / 2, math.pi, 6), [(-3.0, -2.4)], arc(-2.6, -2.4, 0.4, math.pi, 1.5 * math.pi, 6), [(1.8, -2.8)],
                  arc(1.8, -2.4, 0.4, -1.5 * math.pi + 2 * math.pi, 2 * math.pi, 6), [(2.2, -1.3)], [(2.9, -1.3)], arc(2.9, -0.8, 0.5, -math.pi / 2, math.pi / 2, 10), [(2.2, -0.3)])
    wedge_top = poly((-2.6, -0.2), (-0.4, 0.5), (-0.4, -0.2), closed=False)
    wedge = poly((-2.6, -0.2), (-2.6, -1.4), (-0.4, -1.4), (-0.4, 0.5), closed=False)
    wedge2 = [[(-2.6, -0.2), (-0.4, -0.2)]]
    holes = [circle(-1.9, -0.75, 0.2, 14), circle(-1.0, -1.0, 0.16, 12), circle(-1.2, -0.5, 0.12, 10), ellipse(-1.6, -0.03, 0.2, 0.08, 12)]
    brie = [chain(arc(0.9, -0.3, 1.0, math.radians(110), math.radians(340), 40)), [(0.9, -0.3), (0.56, 0.64)], [(0.9, -0.3), (1.84, -0.64)],
            chain(arc(0.9, -0.55, 1.0, math.radians(180), math.radians(340), 30)), [(-0.1, -0.3), (-0.1, -0.55)]]
    crackers = [circle(-2.2, -2.0, 0.4, 24), circle(-1.4, -2.1, 0.4, 24), circle(-0.6, -2.15, 0.4, 24)]
    dots = [eye(x + dx, y + dy, 0.05) for x, y in [(-2.2, -2.0), (-1.4, -2.1), (-0.6, -2.15)] for dx, dy in [(-0.15, 0.1), (0.15, 0.1), (0.0, -0.15)]]
    knife = [poly((0.4, -2.55), (1.9, -2.3), (1.9, -2.6)), rrect(-0.5, -2.65, 0.4, -2.35, 0.12)]
    olives = [ellipse(1.4, 0.75, 0.22, 0.16, 12), ellipse(0.9, 0.85, 0.22, 0.16, 12)]
    return make("Cheese Board with Crackers", [board, wedge_top, wedge] + wedge2 + holes + brie + crackers + knife + olives, dots)


@design("kitchen_roast_chicken", T)
def roast_chicken(rng):
    tests = []
    legs = []
    for s in (-1, 1):
        d = lens((s * 0.55, -1.15), (s * 1.6, 0.35), 0.33, 20)
        legs += [d, [(s * 1.55, 0.3), (s * 2.0, 0.95)], poly((s * 1.85, 0.9), (s * 1.75, 1.25), (s * 1.93, 1.15), (s * 2.0, 1.4), (s * 2.1, 1.15), (s * 2.25, 1.2), (s * 2.17, 0.88))]
        tests.append(lambda p, d=d: _in_poly(p, d))
    body = clip_out(ellipse(0, -0.5, 2.25, 1.35, 120), lambda p: any(t(p) for t in tests) or p[1] < -1.25)
    body.append(clip_out([(-2.0 + 4.0 * i / 60, -1.25) for i in range(61)], lambda p: any(t(p) for t in tests)))
    body = [b for part in body for b in (part if isinstance(part[0], list) else [part])]
    hide = tests + [lambda p: (p[0] / 2.25) ** 2 + ((p[1] + 0.5) / 1.35) ** 2 < 1 and p[1] > -1.25]
    platter = clip_out(ellipse(0, -1.6, 3.0, 1.1, 140), lambda p: any(t(p) for t in hide))
    rim = clip_out(ellipse(0, -1.6, 2.6, 0.85, 120), lambda p: any(t(p) for t in hide))
    breast = [quad((0, 0.85), (0.2, -0.2), (0, -1.25), 16)]
    garnish = [leaf(-2.5, -1.6, 0.6, 2.8), leaf(-2.3, -2.05, 0.6, 3.6), leaf(2.5, -1.6, 0.6, 0.35), leaf(2.3, -2.05, 0.6, -0.45),
               ellipse(-0.7, -2.15, 0.3, 0.2, 14), ellipse(0.0, -2.25, 0.3, 0.2, 14), ellipse(0.7, -2.15, 0.3, 0.2, 14)]
    st = [steam(-0.5, 1.15, 1.0, 0.15), steam(0.5, 1.15, 1.0, 0.15)]
    return make("Roast Chicken on a Platter", body + platter + rim + legs + breast + garnish + st)


@design("kitchen_bbq_kebabs", T)
def bbq_kebabs(rng):
    kettle = chain([(-2.4, 0.0)], cubic((-2.4, 0.0), (-2.3, -2.0), (2.3, -2.0), (2.4, 0.0), 40))
    grate = rrect(-2.6, -0.05, 2.6, 0.15, 0.08)
    legs = [[(-1.2, -1.4), (-1.9, -3.0)], [(1.2, -1.4), (1.9, -3.0)], [(0.0, -1.5), (0.0, -3.0)]]
    wheel = [circle(-1.9, -3.0, 0.25, 14), circle(1.9, -3.0, 0.25, 14)]
    shelf = [[(-1.55, -2.2), (1.55, -2.2)]]
    vent = [circle(0, -0.9, 0.25, 14), [(-0.5, -0.4), (0.5, -0.4)]]
    handles = [rrect(-3.0, -0.4, -2.4, -0.2, 0.08), rrect(2.4, -0.4, 3.0, -0.2, 0.08)]
    out = [kettle, grate] + legs + wheel + shelf + vent + handles
    for k, y in enumerate((0.55, 1.25, 1.95)):
        x0, x1 = -2.6, 2.4
        out.append([(x0 + 0.4, y), (x1, y)])
        out.append(circle(x0 + 0.2, y, 0.2, 12))
        for j in range(5):
            x = -1.8 + 0.85 * j + 0.15 * k
            if (j + k) % 2:
                out.append(rrect(x - 0.28, y - 0.28, x + 0.28, y + 0.28, 0.08))
            else:
                out.append(circle(x, y, 0.3, 16))
    st = [steam(-1.4, 2.4, 0.7, 0.15), steam(1.4, 2.4, 0.7, 0.15)]
    return make("Kettle Grill with Kebabs", out + st)


# dropped: the Easter book has an egg carton
def egg_carton(rng):
    lid = poly((-2.9, -0.2), (-2.6, 2.4), (2.6, 2.4), (2.9, -0.2), closed=False)
    lid_in = rrect(-1.4, 1.0, 1.4, 1.9, 0.15)
    tray = chain([(-3.0, -0.2)], [(3.0, -0.2)], [(2.88, -1.75)], [p for k in reversed(range(6)) for p in arc(-2.4 + 0.96 * k, -1.75, 0.48, 0, -math.pi, 12)], [(-3.0, -0.2)])
    eggs = []
    back = []
    for k in range(6):
        x = -2.4 + 0.96 * k
        back += clip_out(ellipse(x + 0.1, 0.25, 0.4, 0.55, 30), lambda p: p[1] < -0.2)
    for k in range(6):
        x = -2.4 + 0.96 * k
        eggs += clip_out(ellipse(x, -0.05, 0.42, 0.58, 30), lambda p: p[1] < -0.2)
    back = [s for b in back for s in clip_out(b, lambda p: p[1] < -0.2 or any(((p[0] - (-2.4 + 0.96 * k)) / 0.42) ** 2 + ((p[1] + 0.05) / 0.58) ** 2 < 1 for k in range(6)))]
    return make("Carton of Eggs", [lid, lid_in, tray] + eggs + back + [heart(0, 1.45, 0.3)])


@design("kitchen_pizza_oven", T)
def pizza_oven(rng):
    base = rect(-2.8, -2.9, 2.8, -1.2)
    base_bricks = [[(-2.8, -2.05), (2.8, -2.05)]] + [[(x, -1.2), (x, -2.05)] for x in (-1.6, -0.4, 0.8, 2.0)] + [[(x, -2.05), (x, -2.9)] for x in (-2.2, -1.0, 0.2, 1.4)]
    dome = arc(0, -1.2, 2.6, 0, math.pi, 80)
    mouth = chain([(-1.1, -1.2)], [(-1.1, -0.5)], arc(0, -0.5, 1.1, math.pi, 0, 30), [(1.1, -1.2)])
    voussoirs = []
    for k in range(9):
        a = math.pi - k * math.pi / 8
        voussoirs.append([(1.1 * math.cos(a), -0.5 + 1.1 * math.sin(a)), (1.5 * math.cos(a), -0.5 + 1.5 * math.sin(a))])
    arch2 = arc(0, -0.5, 1.5, math.pi, 0, 30)
    chimney = [chain([(-0.35, 1.38)], [(-0.35, 2.3)], [(0.35, 2.3)], [(0.35, 1.38)]), rect(-0.5, 2.3, 0.5, 2.5)]
    smoke = [steam(0.0, 2.6, 0.6, 0.2)]
    fire = [flame(-0.5, -1.2, 0.25, 0.8, 0.05), flame(0.0, -1.2, 0.28, 1.1), flame(0.5, -1.2, 0.25, 0.75, -0.05)]
    return make("Wood-Fired Pizza Oven", [base, dome, mouth, arch2] + base_bricks + voussoirs + chimney + smoke + fire)


@design("kitchen_sink", T)
def kitchen_sink(rng):
    counter = rect(-3.0, -0.6, 3.0, -0.2)
    cab = rect(-2.8, -2.9, 2.8, -0.6)
    doors = [rrect(-2.6, -2.7, -0.1, -0.8, 0.08), rrect(0.1, -2.7, 2.6, -0.8, 0.08)]
    knobs = [circle(-0.4, -1.4, 0.12, 10), circle(0.4, -1.4, 0.12, 10)]
    tap = [chain([(-0.15, -0.2)], [(-0.15, 1.8)], arc(0.45, 1.8, 0.6, math.pi, 0, 20), [(1.05, 1.5)]),
           chain([(0.15, -0.2)], [(0.15, 1.8)], arc(0.45, 1.8, 0.3, math.pi, 0, 14), [(0.75, 1.5)]), [(0.75, 1.5), (1.05, 1.5)],
           rrect(-0.35, -0.2, 0.35, 0.2, 0.08), [(0.15, 0.6), (0.65, 0.95)], circle(0.72, 1.0, 0.1, 8)]
    drop = [lens((0.9, 1.25), (0.9, 0.85), 0.35, 8)]
    plates = [arc(-1.6, -0.2, 1.0, 0.2, math.pi - 0.2, 24), arc(-1.45, -0.2, 0.8, 0.25, math.pi - 0.25, 20), arc(-1.3, -0.2, 0.55, 0.3, math.pi - 0.3, 16)]
    pot = [rect(1.4, -0.2, 2.5, 0.5), [(2.5, 0.4), (3.0, 0.65)]]
    soap = [rrect(-2.9, -0.2, -2.4, 0.7, 0.12), [(-2.65, 0.7), (-2.65, 1.0), (-2.4, 1.0)]]
    bubbles = [circle(x, y, r, 14) for x, y, r in [(1.6, 0.9, 0.2), (2.0, 1.2, 0.25), (2.3, 0.8, 0.15), (-2.0, 1.2, 0.18)]]
    return make("Kitchen Sink with Dishes", [counter, cab] + doors + knobs + tap + drop + plates + pot + soap + bubbles)


@design("kitchen_dish_rack", T)
def dish_rack(rng):
    tray = chain([(-3.0, -2.0)], [(-2.8, -2.6)], [(2.8, -2.6)], [(3.0, -2.0)], [(-3.0, -2.0)])
    rail = [[(-2.8, -1.4), (2.8, -1.4)]]
    posts = [[(-2.8, -2.0), (-2.8, -0.6)], [(2.8, -2.0), (2.8, -0.6)], [(-2.8, -0.6), (-1.0, -0.6)]]
    plates = []
    centers = [(-2.2, -0.5), (-1.6, -0.5), (-1.0, -0.5)]
    for i, (x, y) in enumerate(centers):
        c = circle(x, y, 1.3, 90)
        front = [in_circle(cx, cy, 1.3) for cx, cy in centers[i + 1:]]
        plates += clip_out(c, lambda p, f=front: any(t(p) for t in f) or p[1] < -2.0)
    rim = clip_out(circle(-1.0, -0.5, 0.85, 60), lambda p: p[1] < -2.0)
    cutlery = [rect(0.3, -2.0, 1.3, -0.8)]
    forks = [[(0.55, -0.8), (0.55, 0.6)], [(0.45, 0.6), (0.45, 1.1)], [(0.55, 0.6), (0.55, 1.1)], [(0.65, 0.6), (0.65, 1.1)],
             [(1.0, -0.8), (1.0, 0.5)], ellipse(1.0, 0.8, 0.2, 0.32, 14)]
    glass = [poly((1.7, -2.0), (2.7, -2.0), (2.85, 0.4), (1.55, 0.4)), [(1.62, -0.3), (2.78, -0.3)]]
    drops = [lens((x, -2.75), (x, -3.05), 0.4, 6) for x in (-1.5, 0.5)]
    return make("Dish Drying Rack", [tray] + rim + rail + posts[:2] + plates + cutlery + forks + glass + drops)


@design("kitchen_pantry_shelf", T)
def pantry_shelf(rng):
    shelves = [rect(-3.0, -2.6, 3.0, -2.35), rect(-3.0, 0.25, 3.0, 0.5)]
    brackets = [poly((-2.4, -2.6), (-2.4, -3.1), (-1.9, -2.6), closed=False), poly((2.4, -2.6), (2.4, -3.1), (1.9, -2.6), closed=False),
                poly((-2.4, 0.25), (-2.4, -0.25), (-1.9, 0.25), closed=False), poly((2.4, 0.25), (2.4, -0.25), (1.9, 0.25), closed=False)]
    # lower shelf
    mason = [rrect(-2.8, -2.35, -1.4, -0.6, 0.25), rect(-2.7, -0.6, -1.5, -0.3), [(-2.7, -0.45), (-1.5, -0.45)]]
    beans = [circle(-2.1 + dx, -1.9 + dy, 0.17, 10) for dx, dy in [(-0.35, 0), (0.0, 0), (0.35, 0), (-0.2, 0.35), (0.2, 0.35), (-0.35, 0.7), (0.05, 0.7), (0.4, 0.68), (-0.15, 1.05)]]
    spag = [rrect(-1.1, -2.35, -0.3, 0.0, 0.15), rect(-1.15, 0.0, -0.25, 0.2)] + [[(x, -2.2), (x + 0.05, -0.2)] for x in (-0.9, -0.7, -0.5)]
    swing = [chain([(0.0, -2.35)], [(0.0, -1.0)], quad((0.0, -1.0), (0.0, -0.6), (0.6, -0.6), 8), quad((0.6, -0.6), (1.2, -0.6), (1.2, -1.0), 8), [(1.2, -2.35)], [(0.0, -2.35)]),
             ellipse(0.6, -0.5, 0.45, 0.12, 20), [(0.1, -0.85), (-0.05, -0.4)], rect(0.25, -1.9, 0.95, -1.3)]
    cookie = [rrect(1.5, -2.35, 2.8, -0.9, 0.2), rect(1.45, -0.9, 2.85, -0.7), circle(2.15, -0.55, 0.15, 10), circle(1.85, -1.8, 0.25, 14), circle(2.4, -1.4, 0.25, 14)]
    # upper shelf
    tall = [rrect(-2.7, 0.5, -1.7, 2.6, 0.2), rrect(-2.6, 2.6, -1.8, 2.85, 0.08), rect(-2.5, 1.2, -1.9, 1.9)]
    honey = [chain([(-1.3, 0.5)], [(-1.4, 1.5)], quad((-1.4, 1.5), (-0.85, 1.9), (-0.3, 1.5), 10), [(-0.4, 0.5)], [(-1.3, 0.5)]),
             rect(-1.1, 1.75, -0.6, 2.0), poly((-1.4, 1.5), (-1.1, 1.3), (-0.85, 1.5), (-0.6, 1.3), (-0.3, 1.5), closed=False)]
    oil = [chain([(0.0, 0.5)], [(0.0, 1.5)], quad((0.0, 1.5), (0.0, 1.9), (0.25, 2.0), 6), [(0.25, 2.5)], [(0.45, 2.5)], [(0.45, 2.0)],
                 quad((0.45, 2.0), (0.7, 1.9), (0.7, 1.5), 6), [(0.7, 0.5)]), rect(0.22, 2.5, 0.48, 2.7), leaf(0.2, 0.9, 0.35, 1.0)]
    flour = [chain([(1.1, 0.5)], [(1.1, 1.7)], [(1.25, 2.1)], [(2.75, 2.1)], [(2.9, 1.7)], [(2.9, 0.5)]), zigzag(1.25, 2.75, 2.1, 0.08, 5),
             [(1.1, 1.7), (2.9, 1.7)], rect(1.5, 0.8, 2.5, 1.4)]
    return make("Pantry Shelf with Jars", shelves + brackets + mason + beans + spag + swing + cookie + tall + honey + oil + flour)


@design("kitchen_pressure_cooker", T)
def pressure_cooker(rng):
    body = chain([(-2.0, 0.2)], [(-2.0, -2.2)], quad((-2.0, -2.2), (-2.0, -2.6), (-1.6, -2.6), 6), [(1.6, -2.6)], quad((1.6, -2.6), (2.0, -2.6), (2.0, -2.2), 6), [(2.0, 0.2)])
    lid = chain([(-2.2, 0.2)], quad((-2.2, 0.2), (-2.2, 1.0), (-1.4, 1.1), 10), [(1.4, 1.1)], quad((1.4, 1.1), (2.2, 1.0), (2.2, 0.2), 10), [(-2.2, 0.2)])
    ridge = [[(-2.0, 0.0), (2.0, 0.0)]]
    handle_top = chain([(-0.2, 1.1)], [(-0.2, 1.3)], [(3.4, 1.3)], arc(3.4, 1.05, 0.25, math.pi / 2, -math.pi / 2, 8), [(1.7, 0.8)])
    handle_bot = chain([(2.0, -0.2)], [(3.4, -0.2)], arc(3.4, -0.45, 0.25, math.pi / 2, -math.pi / 2, 8), [(2.0, -0.7)])
    side = [arc(-2.0, -0.4, 0.4, math.pi / 2, 1.5 * math.pi, 10)]
    valve = [rect(-1.2, 1.1, -0.8, 1.6), circle(-1.0, 1.85, 0.25, 16)]
    gauge = [circle(0.6, 1.5, 0.2, 14)]
    jets = [[(-1.05, 2.2), (-1.3, 2.9)], [(-0.95, 2.2), (-0.7, 2.9)], steam(-1.0, 2.2, 0.8, 0.1)]
    label = [rrect(-1.2, -1.6, 1.2, -0.7, 0.15), [(-0.7, -1.15), (0.7, -1.15)]]
    return make("Pressure Cooker Whistling", [body, lid, handle_top, handle_bot] + ridge + side + valve + gauge + jets + label)


@design("kitchen_rice_cooker", T)
def rice_cooker(rng):
    body = chain([(-2.5, 0.35)], [(-2.5, -1.9)], quad((-2.5, -1.9), (-2.5, -2.4), (-2.0, -2.4), 8), [(1.0, -2.4)], quad((1.0, -2.4), (1.5, -2.4), (1.5, -1.9), 8), [(1.5, 0.35)])
    lid_rim = rrect(-2.65, 0.3, 1.65, 0.55, 0.1)
    lid = chain([(-2.4, 0.55)], cubic((-2.4, 0.55), (-2.3, 2.0), (1.3, 2.0), (1.4, 0.55), 30))
    handle = chain([(-1.1, 1.55)], [(-1.1, 2.1)], [(0.1, 2.1)], [(0.1, 1.6)])
    vent = circle(0.75, 1.2, 0.15, 10)
    panel = rrect(-1.6, -1.6, 0.6, -0.4, 0.2)
    btn = [circle(-1.0, -1.0, 0.22, 14), rrect(-0.5, -0.85, 0.3, -0.55, 0.08), [(-0.5, -1.2), (0.3, -1.2)]]
    feet = [rrect(-2.2, -2.7, -1.6, -2.4, 0.08), rrect(0.6, -2.7, 1.2, -2.4, 0.08)]
    st = [steam(0.75, 1.5, 1.0, 0.15)]
    bowl = [chain([(1.75, -1.3)], bowl_side(2.4, -1.3, 0.65, 0.7, 16), [(3.05, -1.3)], [(1.75, -1.3)]), rrect(2.05, -2.3, 2.75, -2.1, 0.05)]
    rice = scallop(2.4, -1.3, 0.62, 0.6, 0.0, math.pi, 4, 0.1, 30)
    sticks = [[(1.9, -0.2), (3.0, 0.9)], [(2.1, -0.3), (3.1, 0.7)]]
    return make("Rice Cooker and Rice Bowl", [body, lid_rim, lid, handle, vent, panel, rice] + btn + feet + st + bowl + sticks)


@design("kitchen_food_processor", T)
def food_processor(rng):
    base = chain([(-1.8, -0.8)], [(-2.1, -2.6)], [(2.1, -2.6)], [(1.8, -0.8)], [(-1.8, -0.8)])
    btns = [rrect(-1.3, -2.0, -0.5, -1.6, 0.1), rrect(0.5, -2.0, 1.3, -1.6, 0.1), circle(0, -1.8, 0.25, 14)]
    jar = chain([(-1.6, -0.8)], [(-1.8, 1.6)], [(1.8, 1.6)], [(1.6, -0.8)])
    lid = rrect(-1.95, 1.6, 1.95, 1.95, 0.1)
    tube_ = rect(-0.6, 1.95, 0.4, 2.7)
    pusher = [rect(-0.5, 2.7, 0.3, 3.0), rrect(-0.7, 3.0, 0.5, 3.2, 0.08)]
    handle = chain([(1.75, 1.2)], [(2.6, 1.2)], [(2.6, -0.3)], [(1.65, -0.3)])
    handle_in = chain([(1.72, 0.8)], [(2.2, 0.8)], [(2.2, 0.1)], [(1.68, 0.1)])
    shaft = [[(0, -0.8), (0, 0.6)], rrect(-0.15, 0.6, 0.15, 0.8, 0.05)]
    blade = [chain(quad((0, -0.1), (-0.8, 0.1), (-1.25, -0.25), 10), quad((-1.25, -0.25), (-0.6, -0.25), (0, -0.3), 10)),
             chain(quad((0, 0.25), (0.8, 0.45), (1.25, 0.1), 10), quad((1.25, 0.1), (0.6, 0.1), (0, 0.05), 10))]
    return make("Food Processor", [base, jar, lid, tube_, handle, handle_in] + btns + pusher + shaft + blade)


@design("kitchen_egg_timer", T)
def egg_timer(rng):
    egg = [(1.6 * math.sin(t) * (1 - 0.12 * math.cos(t)), 2.0 * math.cos(t) + 0.4) for t in [TAU * i / 120 for i in range(121)]]
    split = clip_out([(x, 0.6) for x in [-1.8 + 3.6 * i / 40 for i in range(41)]], lambda p: abs(p[0]) > 1.55)
    ticks = [[(-1.2 + 0.3 * k, 0.6), (-1.2 + 0.3 * k, 0.85 if k % 2 == 0 else 0.75)] for k in range(9)]
    arrow = [poly((0, 0.6), (-0.15, 0.3), (0.15, 0.3))]
    stand = [ellipse(0, -1.65, 1.1, 0.2, 40)]
    cups = []
    for x in (-2.4, 2.4):
        cups += clip_out(ellipse(x, -0.9, 0.42, 0.58, 30), lambda p: p[1] < -1.25)
        cups += [chain([(x - 0.55, -1.25)], bowl_side(x, -1.25, 0.55, 0.55, 14), [(x + 0.55, -1.25)], [(x - 0.55, -1.25)]),
                 [(x - 0.12, -1.78), (x - 0.12, -2.35)], [(x + 0.12, -1.78), (x + 0.12, -2.35)], ellipse(x, -2.45, 0.45, 0.12, 20)]
    return make("Egg Timer and Boiled Eggs", [egg] + split + ticks + arrow + stand + cups)


@design("kitchen_herb_window", T)
def herb_window(rng):
    frame = rect(-2.4, -1.0, 2.4, 2.8)
    inner = rect(-2.15, -0.8, 2.15, 2.55)
    mull = [[(0, -0.8), (0, 2.55)], [(-2.15, 0.9), (2.15, 0.9)]]
    rod = [[(-2.8, 3.3), (2.8, 3.3)], circle(-2.95, 3.3, 0.15, 12), circle(2.95, 3.3, 0.15, 12)]
    val = chain([(-2.7, 3.3)], [(-2.7, 2.9)], *[arc(-2.7 + 0.6 * (k + 0.5), 2.9, 0.3, math.pi, 2 * math.pi, 8) for k in range(9)], [(2.7, 2.9)], [(2.7, 3.3)])
    sill = rrect(-2.8, -2.9, 2.8, -2.6, 0.08)
    pots = []
    for x in (-1.6, 0.0, 1.6):
        pots += [chain([(x - 0.55, -1.55)], [(x - 0.42, -2.6)], [(x + 0.42, -2.6)], [(x + 0.55, -1.55)]), rrect(x - 0.65, -1.55, x + 0.65, -1.2, 0.06)]
    basil = [leaf(-1.6, -1.2, 0.8, math.radians(a), 0.35) for a in (60, 100, 140)] + [leaf(-1.6, -0.6, 0.6, math.radians(a), 0.35) for a in (75, 115)]
    rosemary = [[(0.0 + dx, -1.2), (0.0 + dx * 2.2, 0.6)] for dx in (-0.25, 0.0, 0.25)]
    for dx in (-0.25, 0.0, 0.25):
        for f in (0.3, 0.55, 0.8):
            x, y = dx + dx * 1.2 * f, -1.2 + 1.8 * f
            rosemary += [leaf(x, y, 0.3, math.radians(140), 0.3), leaf(x, y, 0.3, math.radians(40), 0.3)]
    chives = [quad((1.6 + d * 0.1, -1.2), (1.6 + d * 0.3, -0.3), (1.6 + d * 0.5, 0.4), 10) for d in (-2, -1, 0, 1, 2)]
    return make("Kitchen Window Herb Garden", [frame, inner, sill, val] + rod + mull + pots + basil + rosemary + chives)


@design("kitchen_dumpling_steamer", T)
def dumpling_steamer(rng):
    lid = [ellipse(1.4, 1.7, 1.5, 0.4, 60), chain([(-0.1, 1.7)], quad((-0.1, 1.7), (1.4, 3.0), (2.9, 1.7), 20)), rrect(1.0, 2.25, 1.8, 2.5, 0.1)]
    lid_lines = [quad((0.4, 1.95), (1.4, 2.7), (2.4, 1.95), 14)]
    basket = chain([(-2.6, -0.4)], [(-2.6, -2.2)], cubic((-2.6, -2.2), (-2.6, -2.9), (2.6, -2.9), (2.6, -2.2), 30), [(2.6, -0.4)])
    rim = ellipse(0, -0.4, 2.6, 0.55, 100)
    weave = [cubic((-2.6, y), (-2.6, y - 0.6), (2.6, y - 0.6), (2.6, y), 30) for y in (-1.2, -1.8)]
    dump = []
    for x, y in [(-1.4, -0.2), (0.0, -0.05), (1.4, -0.2)]:
        d = chain([(x - 0.7, y)], cubic((x - 0.7, y), (x - 0.6, y + 0.9), (x + 0.6, y + 0.9), (x + 0.7, y), 20), [(x - 0.7, y)])
        pleats = [quad((x + dx, y + 0.6), (x + dx * 1.2, y + 0.4), (x + dx * 1.4, y + 0.25), 6) for dx in (-0.3, 0.0, 0.3)]
        dump += [d] + pleats
    sticks = [[(-3.0, 1.6), (-0.8, 0.9)], [(-3.0, 1.85), (-0.7, 1.15)]]
    sauce = [ellipse(-2.0, 2.4, 0.7, 0.25, 30), ellipse(-2.0, 2.4, 0.5, 0.15, 24)]
    st = [steam(-1.0, 0.8, 0.8, 0.12), steam(0.6, 0.9, 0.8, 0.12)]
    return make("Dumplings in a Bamboo Steamer", [basket, rim] + lid + lid_lines + weave + dump + sticks + sauce + st)


@design("kitchen_meat_grinder", T)
def meat_grinder(rng):
    barrel = rrect(-1.8, -0.4, 1.4, 0.8, 0.3)
    hopper = chain([(-0.9, 0.8)], [(-1.5, 2.2)], [(1.1, 2.2)], [(0.5, 0.8)])
    hopper_rim = ellipse(-0.2, 2.2, 1.3, 0.25, 50)
    face = [ellipse(-1.9, 0.2, 0.3, 0.7, 30)]
    holes = [eye(-1.9, 0.2 + dy, 0.06) for dy in (-0.4, -0.15, 0.1, 0.35)]
    crank = [rrect(1.4, 0.05, 1.8, 0.35, 0.1), [(1.8, 0.2), (2.4, 0.2)], [(2.4, 0.2), (2.6, 1.9)], rrect(2.4, 1.9, 2.9, 2.8, 0.2)]
    crank = [rrect(1.4, 0.0, 1.7, 0.4, 0.08), tube([(1.7, 0.2), (2.4, 0.2), (2.6, 1.9)], 0.22), rrect(2.4, 1.9, 2.85, 2.8, 0.2)]
    stem = [rect(-0.5, -1.4, 0.1, -0.4)]
    table = [[(-3.0, -1.4), (3.0, -1.4)], [(-3.0, -1.8), (3.0, -1.8)]]
    screw = [chain([(0.3, -1.4)], [(0.3, -2.4)], [(-0.7, -2.4)], [(-0.7, -1.8)]), [(-0.2, -2.4), (-0.2, -2.9)], rrect(-0.6, -3.05, 0.2, -2.85, 0.08)]
    mince = [quad((-2.0, 0.0 + 0.2 * k), (-2.6, -0.3 + 0.2 * k), (-2.5 + 0.15 * k, -1.3), 10) for k in range(3)]
    return make("Hand-Crank Meat Grinder", [barrel, hopper, hopper_rim] + face + crank + stem + table + screw + mince, holes)


def _in_poly(p, pts):
    """Even-odd point-in-polygon test."""
    x, y = p
    inside = False
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside
