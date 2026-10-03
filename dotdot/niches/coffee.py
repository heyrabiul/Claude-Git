"""Coffee & Tea niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "coffee"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ---------------------------------------------------------------- helpers

def ea(cx, cy, rx, ry, t0, t1, n=40):
    """Elliptical arc."""
    return [(cx + rx * math.cos(t0 + (t1 - t0) * i / n), cy + ry * math.sin(t0 + (t1 - t0) * i / n)) for i in range(n + 1)]


def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def steam(x, y0, h=1.2, amp=0.15, waves=1.25, n=30, phase=0.0):
    return [(x + amp * math.sin(phase + TAU * waves * i / n), y0 + h * i / n) for i in range(n + 1)]


def _left_ctrl(cx, top, bot, w, bw, belly):
    h = top - bot
    return (cx - w, top), (cx - w, top - h * belly), (cx - bw - (w - bw) * 0.35, bot), (cx - bw, bot)


def cup_body(cx, top, bot, w, bw, belly=0.55, n=24):
    """Open cup bowl from the left rim point down and up to the right rim point."""
    left = cubic(*_left_ctrl(cx, top, bot, w, bw, belly), n)
    return chain(left, mirror_x(left, cx)[::-1])


def body_x(cx, top, bot, w, bw, t, belly=0.55, side=1):
    x, y = bez(*_left_ctrl(cx, top, bot, w, bw, belly), t)
    return (2 * cx - x if side > 0 else x), y


def handle(p1, p2, d, t=0.3, side=1):
    """C handle between two attach points on a cup's side."""
    (x1, y1), (x2, y2) = p1, p2
    s = side
    outer = cubic((x1, y1), (x1 + s * d, y1 + 0.3), (x2 + s * d * 0.9, y2 - 0.15), (x2, y2))
    inner = cubic((x1 - s * 0.02, y1 - t), (x1 + s * (d - t * 1.7), y1 - t + 0.15),
                  (x2 + s * (d * 0.9 - t * 1.6), y2 + t * 0.7), (x2 + s * 0.02, y2 + t))
    return [outer, inner]


def half_w(body, cx, y):
    """Half width of an (open, symmetric-ish) cup outline at height y, or None."""
    best = None
    for (x0, y0), (x1, y1) in zip(body, body[1:]):
        if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
            x = x0 + (x1 - x0) * (y - y0) / (y1 - y0)
            if x >= cx and (best is None or x - cx > best):
                best = x - cx
    return best


def saucer(cx, cy, rx, ry, gap=None, body=None):
    """Saucer drawn behind a cup: the back rim stops where it meets the cup."""
    th = math.acos(max(-0.99, min(0.99, (gap or 0.0) / rx)))
    if body is not None:
        th = math.pi / 2
        for i in range(91):
            t = math.pi / 2 * i / 90
            x, y = rx * math.cos(t), cy + ry * math.sin(t)
            hw = half_w(body, cx, y)
            if hw is not None and abs(x) <= hw + 0.02:
                th = t
                break
    return [ea(cx, cy, rx, ry, th, -math.pi - th, 70),
            ea(cx, cy - ry * 0.2, rx * 0.62, ry * 0.5, -0.25, -math.pi + 0.25, 36)]


def teacup(cx, bot, w=1.5, h=1.4, bw=0.75, side=1, with_saucer=True, sr=None, rim=True):
    top = bot + h
    out = [cup_body(cx, top, bot, w, bw)]
    if rim:
        out.append(ellipse(cx, top, w, w * 0.2, 90))
    a = body_x(cx, top, bot, w, bw, 0.12, side=side)
    b = body_x(cx, top, bot, w, bw, 0.62, side=side)
    out += handle(a, b, 0.75 * w / 1.5, 0.26 * w / 1.5, side)
    if with_saucer:
        sr = sr or w * 1.55
        out += saucer(cx, bot - 0.08, sr, sr * 0.24, body=out[0])
    return out


def bean(cx, cy, r, rot=0.0):
    out = ellipse(cx, cy, r, r * 0.68, 30, rot=rot)
    crease = [(-0.8 * r + 1.6 * r * i / 16, 0.16 * r * math.sin(TAU * i / 16)) for i in range(17)]
    return [out, transform(crease, cx, cy, rot=rot)]


def leaf(p0, p1, bulge=0.3, vein=True):
    out = [lens(p0, p1, bulge, 20)]
    if vein:
        out.append([p0, ((p0[0] * 0.15 + p1[0] * 0.85), (p0[1] * 0.15 + p1[1] * 0.85))])
    return out


def tilt(parts, dx=0.0, dy=0.0, s=1.0, rot=0.0):
    return [transform(p, dx, dy, s, rot) for p in parts]


def teapot_body(top_w, bot_w, top, bot, belly_w, n=30):
    left = cubic((-top_w, top), (-belly_w, top - 0.2), (-belly_w * 1.05, bot + 0.3), (-bot_w, bot), n)
    return chain(left, mirror_x(left)[::-1])


# ---------------------------------------------------------------- coffee cups

def resample(pts, n):
    """n points evenly spaced along a polyline."""
    d = [0.0]
    for a, b in zip(pts, pts[1:]):
        d.append(d[-1] + math.dist(a, b))
    out, j = [], 0
    for k in range(n):
        t = d[-1] * k / n
        while d[j + 1] < t:
            j += 1
        f = (t - d[j]) / ((d[j + 1] - d[j]) or 1)
        out.append((pts[j][0] + (pts[j + 1][0] - pts[j][0]) * f, pts[j][1] + (pts[j + 1][1] - pts[j][1]) * f))
    return out


def croissant(cx, cy, s=1.0):
    """Crescent croissant: a tapered band along an arc with rolled seams."""
    a0, a1, R = math.radians(15), math.radians(165), 1.7
    center = arc(0, -1.3, R, a0, a1, 40)
    wf = lambda t: 0.3 + 1.0 * math.sin(math.pi * t)
    out = [tube(center, wf)]
    for t in (0.22, 0.38, 0.62, 0.78):
        a = a0 + (a1 - a0) * t
        w = wf(t) / 2 * 0.95
        p0 = ((R - w) * math.cos(a), -1.3 + (R - w) * math.sin(a))
        p1 = ((R + w) * math.cos(a), -1.3 + (R + w) * math.sin(a))
        mid = (R * math.cos(a + (0.12 if t < 0.5 else -0.12)), -1.3 + R * math.sin(a + (0.12 if t < 0.5 else -0.12)))
        out.append(quad(p0, mid, p1, 10))
    return [transform(p, cx, cy, s) for p in out]


@design("coffee_latte_heart", T)
def latte_heart(rng):
    top, bot, w, bw = 0.9, -1.4, 2.1, 1.1
    rim = ellipse(0, top, w, 0.75, 120)
    inner = ellipse(0, top, w - 0.22, 0.58, 110)
    b = cup_body(0, top, bot, w, bw, 0.4)
    hd = handle((2.05, 0.35), (1.55, -0.85), 0.95, 0.32)
    h1 = transform(heart(0, 0, 1, 90), 0, top + 0.12, sx=0.95, sy=0.48)
    h2 = transform(heart(0, 0, 1, 70), 0, top + 0.08, sx=0.5, sy=0.26)
    tail = [(0, top - 0.42), (0.05, top - 0.55)]
    s = saucer(0, bot - 0.1, 3.0, 0.8, body=b)
    return make("Latte with Heart Art", [rim, inner, b, h1, h2] + hd + s)


@design("coffee_cappuccino", T)
def cappuccino(rng):
    bot = -1.6
    parts = teacup(0, bot, w=1.8, h=2.0, bw=1.0, sr=3.0)
    top = bot + 2.0
    foam = []
    for x0, x1, h in [(-1.8, -0.9, 0.55), (-0.9, 0.1, 0.85), (0.1, 1.0, 0.75), (1.0, 1.8, 0.5)]:
        foam += ea((x0 + x1) / 2, top, (x1 - x0) / 2, h, math.pi, 0, 16)[:-1]
    foam.append((1.8, top))
    cocoa = [star(-0.4, 0.8, 0.18, 5), star(0.55, 0.75, 0.16, 5)]
    st = [steam(x, 1.7, 1.2, 0.15, 1.2, phase=p) for x, p in [(-0.6, 0), (0.1, 1.5), (0.8, 3)]]
    spoon = [ellipse(2.25, -1.95, 0.35, 0.15, 20, rot=0.1), [(1.9, -2.0), (0.9, -2.15)]]
    return make("Foamy Cappuccino", parts + [foam] + cocoa + st + spoon)


@design("coffee_espresso_shot", T)
def espresso_shot(rng):
    top, bot = 0.5, -1.3
    cup = chain([(-1.0, top)], cubic((-1.0, top), (-1.0, -0.6), (-0.9, bot), (-0.6, bot), 20), [(0.6, bot)],
                cubic((0.6, bot), (0.9, bot), (1.0, -0.6), (1.0, top), 20))
    rim = ellipse(0, top, 1.0, 0.25, 60)
    crema = ellipse(0, top - 0.05, 0.82, 0.17, 50)
    hd = handle((0.98, 0.15), (0.92, -0.7), 0.7, 0.24)
    s = saucer(0, bot - 0.08, 2.1, 0.5, body=cup)
    spoon = [ellipse(1.75, -1.55, 0.32, 0.13, 20, rot=-0.15), [(1.45, -1.5), (0.6, -1.25)]]
    cubes = [poly((-2.6, -1.9), (-1.9, -1.9), (-1.9, -1.2), (-2.6, -1.2)), poly((-2.6, -1.2), (-2.3, -0.95), (-1.6, -0.95), (-1.9, -1.2), closed=False),
             [(-1.6, -0.95), (-1.6, -1.65), (-1.9, -1.9)]]
    st = [steam(-0.3, 0.9, 1.4, 0.18, 1.3), steam(0.3, 1.0, 1.2, 0.15, 1.2, phase=2)]
    return make("Espresso in a Demitasse", [cup, rim, crema] + hd + s + spoon + cubes + st)


@design("coffee_mug_steam", T)
def mug_steam(rng):
    top, bot, w = 0.9, -2.4, 1.6
    body = chain([(-w, top)], [(-w, bot + 0.4)], quad((-w, bot + 0.4), (-w, bot), (-w + 0.4, bot), 10), [(w - 0.4, bot)],
                 quad((w - 0.4, bot), (w, bot), (w, bot + 0.4), 10), [(w, top)])
    rim = ellipse(0, top, w, 0.35, 90)
    coffee = ea(0, top - 0.05, w - 0.15, 0.22, math.pi, 2 * math.pi, 40)
    hd = [chain([(w, 0.4)], cubic((w, 0.4), (3.0, 0.5), (3.0, -1.9), (w, -1.7), 30)),
          chain([(w, 0.0)], cubic((w, 0.0), (2.5, 0.0), (2.5, -1.3), (w, -1.3), 30))]
    h = heart(0, -0.7, 0.75)
    st = [steam(-0.6, 1.4, 1.5, 0.22, 1.0, phase=0.5), steam(0.0, 1.5, 1.6, 0.22, 1.0, phase=2.5), steam(0.6, 1.4, 1.5, 0.22, 1.0, phase=4)]
    return make("Steaming Coffee Mug", [body, rim, coffee, h] + hd + st)


@design("coffee_takeaway", T)
def takeaway(rng):
    cup = poly((-1.3, 1.4), (-1.0, -2.8), (1.0, -2.8), (1.3, 1.4), closed=False)
    lid = [rrect(-1.55, 1.4, 1.55, 1.8, 0.15), poly((-1.35, 1.8), (-1.2, 2.3), (1.2, 2.3), (1.35, 1.8), closed=False),
           rrect(-0.35, 2.05, 0.35, 2.2, 0.07)]
    sleeve = poly((-1.24, 0.6), (-1.11, -1.2), (1.11, -1.2), (1.24, 0.6))
    logo = bean(0, -0.3, 0.45, 0.5)
    st = [steam(-0.3, 2.6, 1.0, 0.15, 1.0), steam(0.4, 2.6, 0.9, 0.15, 1.0, phase=2)]
    return make("Takeaway Coffee Cup", [cup, sleeve] + lid + logo + st)


@design("coffee_iced_glass", T)
def iced_glass(rng):
    glass = poly((-1.3, 2.0), (-1.05, -2.6), (1.05, -2.6), (1.3, 2.0), closed=False)
    rim = ellipse(0, 2.0, 1.3, 0.25, 70)
    base = ea(0, -2.6, 1.05, 0.2, math.pi, 2 * math.pi, 30)
    level = wave(-1.25, 1.25, 1.2, 0.06, 2, 40)
    milk = wave(-1.17, 1.17, -0.4, 0.15, 1.5, 40)
    cubes = [tilt([rrect(-0.4, -0.4, 0.4, 0.4, 0.08)], x, y, 1.0, r)[0] for x, y, r in [(-0.5, 1.0, 0.3), (0.45, 0.7, -0.4), (-0.3, 0.1, 0.8)]]
    straw = [poly((0.55, -1.8), (1.5, 3.0), (1.75, 2.95), (0.8, -1.8), closed=False)]
    drops = [lens((x, y), (x, y - 0.35), 0.4, 8) for x, y in [(-1.0, -1.0), (1.05, -1.5), (-0.9, -1.9)]]
    return make("Iced Coffee with Straw", [glass, rim, base, level, milk] + cubes + straw + drops)


@design("coffee_frappe", T)
def frappe(rng):
    cup = poly((-1.2, 0.6), (-0.95, -2.8), (0.95, -2.8), (1.2, 0.6), closed=False)
    ring = rrect(-1.35, 0.5, 1.35, 0.8, 0.12)
    dome = arc(0, 0.8, 1.3, 0, math.pi, 50)
    cream = [chain(arc(-0.65, 1.1, 0.35, 0, math.pi, 12)), chain(arc(0.05, 1.15, 0.38, 0, math.pi, 12)), chain(arc(0.7, 1.1, 0.32, 0, math.pi, 12)),
             arc(-0.3, 1.55, 0.33, 0, math.pi, 12), arc(0.35, 1.55, 0.3, 0, math.pi, 12)]
    drizzle = [zigzag(-1.05, 1.05, -0.4, 0.2, 4), zigzag(-0.95, 0.95, -1.6, 0.2, 4)]
    straw = [poly((0.15, 1.6), (0.9, 3.0), (1.2, 2.85), (0.45, 1.5), closed=False)]
    return make("Frappe with Whipped Cream", [cup, ring, dome] + cream + drizzle + straw)


# dropped: the Desserts book already has a croissant
def croissant_breakfast(rng):
    cup = teacup(1.4, 0.2, w=1.2, h=1.2, bw=0.6, sr=1.9)
    plate = [ellipse(-1.2, -1.5, 2.0, 0.6, 90), ellipse(-1.2, -1.5, 1.45, 0.4, 70)]
    c = croissant(-1.2, -1.15, 0.95)
    st = [steam(1.1, 1.8, 1.0, 0.13, 1.1), steam(1.7, 1.8, 1.0, 0.13, 1.1, phase=2)]
    return make("Coffee and Croissant", cup + plate + c + st)


@design("coffee_book_glasses", T)
def book_glasses(rng):
    pages_l = chain([(-3.0, -1.6)], quad((-3.0, -1.6), (-1.5, -1.2), (0, -1.7), 20), [(0, 0.2)], quad((0, 0.2), (-1.5, 0.7), (-3.0, 0.3), 20), [(-3.0, -1.6)])
    pages_r = mirror_x(pages_l)
    cover = chain([(-3.1, 0.15)], [(-3.1, -1.85)], quad((-3.1, -1.85), (-1.5, -1.45), (0, -1.95), 20), quad((0, -1.95), (1.5, -1.45), (3.1, -1.85), 20), [(3.1, 0.15)])
    lines = [quad((-2.7, y), (-1.5, y + 0.38), (-0.3, y - 0.05), 12) for y in (-0.05, -0.45, -0.85)] + \
            [quad((0.3, y - 0.05), (1.5, y + 0.38), (2.7, y), 12) for y in (-0.05, -0.45, -0.85)]
    glasses = [ellipse(-1.1, -1.05, 0.55, 0.38, 30), ellipse(0.2, -1.05, 0.55, 0.38, 30), quad((-0.55, -0.95), (-0.45, -0.75), (-0.35, -0.95), 6),
               [(-1.65, -0.95), (-2.4, -0.55)]]
    cup = teacup(1.6, 0.6, w=1.0, h=1.0, bw=0.5, sr=1.5)
    st = [steam(1.4, 2.0, 0.9, 0.12, 1.1), steam(1.85, 2.0, 0.9, 0.12, 1.1, phase=2)]
    return make("Coffee with a Good Book", [pages_l, pages_r, cover] + lines + glasses + cup + st)


@design("coffee_rosetta_top", T)
def rosetta_top(rng):
    plate = [circle(0, 0, 2.9, 140), circle(0, 0, 2.2, 120)]
    cup = [circle(0, 0, 1.9, 120), circle(0, 0, 1.65, 110)]
    hd = [rrect(1.85, -0.3, 2.9, 0.3, 0.28)]
    stem = [(0, -1.4), (0, 1.35)]
    leaves = []
    for k in range(7):
        y = -1.15 + 0.38 * k
        w = 1.1 * math.sin(math.pi * (k + 1) / 8.2) + 0.1
        leaves.append(quad((-w, y + 0.12 * w), (0, y - 0.25), (w, y + 0.12 * w), 16))
    top = heart(0, 1.15, 0.3, 40)
    spoon = [ellipse(-2.5, -1.4, 0.3, 0.18, 16, rot=0.6), [(-2.3, -1.25), (-1.95, -0.85)]]
    return make("Rosetta Latte Art", plate + cup + hd + [stem, top] + leaves + spoon)


@design("coffee_cafe_table", T)
def cafe_table(rng):
    table = [ellipse(0, 0, 2.0, 0.45, 90), ea(0, -0.12, 2.0, 0.45, math.pi, 2 * math.pi, 40), [(-0.1, -0.57), (-0.1, -2.4)], [(0.1, -0.57), (0.1, -2.4)],
             poly((-0.9, -2.8), (-0.1, -2.4), (0.1, -2.4), (0.9, -2.8), closed=False)]
    cups = teacup(-0.8, 0.0, w=0.45, h=0.5, bw=0.25, sr=0.7, side=-1) + teacup(0.8, 0.0, w=0.45, h=0.5, bw=0.25, sr=0.7)
    chairs = []
    for s in (-1, 1):
        chair = [tube([(-2.85, -1.0), (-2.95, 0.4), (-3.15, 1.3)], 0.22),
                 rect(-2.95, -1.12, -1.95, -0.92), [(-2.9, -1.12), (-3.05, -2.8)], [(-2.0, -1.12), (-1.9, -2.8)],
                 ellipse(-2.6, 0.2, 0.25, 0.45, 20, rot=-0.15), [(-2.98, -2.0), (-1.95, -2.0)]]
        chairs += chair if s < 0 else mirror_all(chair)
    st = [steam(-0.8, 0.7, 0.8, 0.1, 1.0), steam(0.8, 0.7, 0.8, 0.1, 1.0, phase=2)]
    return make("Cafe Table for Two", table + cups + chairs + st)


@design("coffee_mug_beans", T)
def mug_with_beans(rng):
    mug = [chain([(-1.6, 1.2)], [(-1.4, -2.0)], quad((-1.4, -2.0), (-1.4, -2.4), (-1.0, -2.4), 8), [(1.0, -2.4)], quad((1.0, -2.4), (1.4, -2.4), (1.4, -2.0), 8), [(1.6, 1.2)]),
           ellipse(0, 1.2, 1.6, 0.35, 80)]
    hd = [chain([(-1.55, 0.6)], cubic((-1.55, 0.6), (-2.7, 0.7), (-2.7, -1.5), (-1.45, -1.4), 24)),
          chain([(-1.53, 0.25)], cubic((-1.53, 0.25), (-2.25, 0.25), (-2.25, -1.05), (-1.47, -1.05), 24))]
    foam = [ea(0, 1.15, 1.42, 0.22, math.pi, 2 * math.pi, 40)]
    beans = []
    for x, y, r, a in [(1.9, -2.0, 0.42, 0.4), (2.6, -1.6, 0.38, -0.6), (2.3, -2.55, 0.35, 1.2), (-2.4, -2.4, 0.4, -0.3), (0.0, -0.4, 0.55, 0.8)]:
        beans += bean(x, y, r, a)
    st = [steam(-0.5, 1.7, 1.2, 0.18, 1.0), steam(0.4, 1.7, 1.3, 0.18, 1.0, phase=2)]
    return make("Mug with Coffee Beans", mug + hd + foam + beans + st)


# ---------------------------------------------------------------- brewers

@design("coffee_french_press", T)
def french_press(rng):
    glass = rect(-1.3, -2.3, 1.3, 1.6)
    bands = [rect(-1.45, -2.6, 1.45, -2.0), rect(-1.45, 1.4, 1.45, 1.75)]
    lid = [quad((-1.35, 1.75), (0, 2.5), (1.35, 1.75), 20), [(-0.1, 2.12), (-0.1, 2.9)], [(0.1, 2.12), (0.1, 2.9)], circle(0, 3.1, 0.25, 20)]
    feet = [ea(x, -2.6, 0.25, 0.2, math.pi, 2 * math.pi, 8) for x in (-1.0, 1.0)]
    hd = [chain([(1.45, 1.2)], [(2.4, 1.2)], quad((2.4, 1.2), (2.7, 1.2), (2.7, 0.9), 6), [(2.7, -1.4)], quad((2.7, -1.4), (2.7, -1.7), (2.4, -1.7), 6), [(1.45, -1.7)]),
          poly((1.45, 0.8), (2.25, 0.8), (2.25, -1.3), (1.45, -1.3), closed=False)]
    level = wave(-1.3, 1.3, 0.5, 0.06, 2.5, 40)
    plate = [[(-1.3, 1.0), (1.3, 1.0)], [(0, 1.4), (0, 1.0)]]
    spout = poly((-1.45, 1.75), (-1.75, 1.95), (-1.45, 1.4), closed=False)
    grounds = [circle(x, y, 0.1, 8) for x, y in [(-0.8, -1.8), (-0.2, -1.6), (0.5, -1.9), (0.9, -1.5), (0.2, -1.2), (-0.7, -1.1)]]
    return make("French Press", [glass, level, spout] + bands + lid + feet + hd + plate + grounds)


@design("coffee_moka_pot", T)
def moka_pot(rng):
    lower = poly((-1.5, -2.8), (1.5, -2.8), (0.9, -0.4), (-0.9, -0.4))
    upper = poly((-0.9, -0.2), (0.9, -0.2), (1.4, 2.0), (-1.4, 2.0))
    waist = rect(-0.95, -0.4, 0.95, -0.2)
    facets = [[(-0.6, -2.8), (-0.35, -0.4)], [(0.6, -2.8), (0.35, -0.4)], [(-0.35, -0.2), (-0.55, 2.0)], [(0.35, -0.2), (0.55, 2.0)]]
    lid = [poly((-1.45, 2.0), (-1.05, 2.5), (1.05, 2.5), (1.45, 2.0), closed=False), rrect(-0.25, 2.5, 0.25, 2.85, 0.1)]
    spout = poly((-1.4, 2.0), (-2.0, 2.3), (-1.35, 1.6), closed=False)
    hd = [poly((1.2, 1.7), (2.6, 1.9), (2.4, 0.3), (1.0, 0.6), closed=False), poly((1.3, 1.35), (2.2, 1.5), (2.05, 0.75), (1.1, 0.95), closed=False)]
    valve = [circle(-0.55, -1.6, 0.2, 16)]
    flame = [poly((-1.0, -2.95), (-0.7, -3.4), (-0.4, -2.95), closed=False), poly((-0.3, -2.95), (0, -3.5), (0.3, -2.95), closed=False), poly((0.4, -2.95), (0.7, -3.4), (1.0, -2.95), closed=False)]
    st = [steam(-1.9, 2.5, 0.9, 0.12, 1.0)]
    return make("Stovetop Moka Pot", [lower, upper, waist, spout] + facets + lid + hd + valve + flame + st)


@design("coffee_chemex", T)
def chemex(rng):
    left = chain(cubic((-1.2, 2.6), (-1.0, 1.5), (-0.4, 0.6), (-0.4, 0.2), 20), cubic((-0.4, 0.2), (-0.4, -0.3), (-1.9, -1.0), (-1.9, -2.2), 20),
                 quad((-1.9, -2.2), (-1.9, -2.8), (-1.2, -2.8), 8))
    body = chain(left, mirror_x(left)[::-1])
    rim = ellipse(0, 2.6, 1.2, 0.2, 50)
    spout = [[(-1.2, 2.6), (-1.35, 2.75)]]
    collar = poly((-0.75, 1.0), (-0.5, 0.0), (0.5, 0.0), (0.75, 1.0))
    grain = [quad((-0.55, 0.75), (0, 0.65), (0.55, 0.75), 8), quad((-0.5, 0.3), (0, 0.2), (0.5, 0.3), 8)]
    tie = [[(0.55, 0.5), (1.4, 0.2), (1.5, -0.5)], circle(1.5, -0.65, 0.15, 12)]
    filt = [poly((-1.15, 2.6), (-1.45, 3.1), (1.45, 3.1), (1.15, 2.6), closed=False), [(-0.2, 3.1), (0.2, 2.6)]]
    level = wave(-1.6, 1.6, -1.2, 0.07, 2, 40)
    return make("Chemex Hourglass Brewer", [body, rim, collar, level] + spout + grain + tie + filt)


@design("coffee_pour_over", T)
def pour_over(rng):
    mug = [chain([(-1.6, -0.4)], [(-1.6, -2.8)], [(0.6, -2.8)], [(0.6, -0.4)]), ellipse(-0.5, -0.4, 1.1, 0.25, 50),
           chain([(0.6, -0.9)], cubic((0.6, -0.9), (1.5, -0.9), (1.5, -2.3), (0.6, -2.2), 20))]
    dripper = [poly((-1.4, -0.25), (-2.1, 1.1), (1.1, 1.1), (0.4, -0.25)), ellipse(-0.5, 1.1, 1.6, 0.22, 60), [(-1.1, 0.0), (-1.2, 0.9)], [(0.1, 0.0), (0.2, 0.9)]]
    kb = chain([(1.0, 1.4)], [(1.2, 2.9)], quad((1.2, 2.9), (2.1, 3.3), (3.0, 2.9), 12), [(3.2, 1.4)], [(1.0, 1.4)])
    lid = [quad((1.25, 2.9), (2.1, 3.05), (2.95, 2.9), 10), circle(2.1, 3.35, 0.13, 10)]
    neck = [tube(cubic((1.1, 1.75), (0.2, 1.4), (-0.1, 2.6), (-0.7, 2.75), 24), 0.2)]
    hd = [chain([(3.1, 2.6)], quad((3.1, 2.6), (3.9, 2.4), (3.15, 1.6), 12)), chain([(3.12, 2.3)], quad((3.12, 2.3), (3.5, 2.15), (3.15, 1.85), 8))]
    stream = [[(-0.8, 2.6), (-0.6, 1.3)]]
    return make("Pour-Over with Gooseneck Kettle", mug + dripper + [kb] + lid + neck + hd + stream)


@design("coffee_siphon", T)
def siphon(rng):
    upper = chain([(-0.25, 0.2)], [(-0.25, 0.9)], cubic((-0.25, 0.9), (-1.1, 1.0), (-1.1, 2.7), (-0.9, 2.9), 20), [(0.9, 2.9)],
                  cubic((0.9, 2.9), (1.1, 2.7), (1.1, 1.0), (0.25, 0.9), 20), [(0.25, 0.2)])
    rim = ellipse(0, 2.9, 0.9, 0.15, 40)
    lower = [circle(0, -1.0, 1.25, 90)]
    neck = [rect(-0.45, 0.05, 0.45, 0.3)]
    stand = [[(1.9, -3.0), (1.9, 2.2)], [(1.9, 1.5), (1.0, 1.5)], [(1.9, -0.3), (1.2, -0.3)], rrect(-2.4, -3.2, 2.4, -2.95, 0.1)]
    burner = [rect(-0.5, -2.95, 0.5, -2.5), poly((-0.15, -2.5), (0, -2.25), (0.15, -2.5), closed=False)]
    level = wave(-1.15, 1.15, -1.3, 0.05, 2, 40)
    bubbles = [circle(x, y, 0.12, 10) for x, y in [(-0.4, -1.7), (0.3, -1.9), (0.5, -1.5), (-0.1, -1.55)]]
    return make("Siphon Coffee Brewer", [upper, rim, level] + lower + neck + stand + burner + bubbles)


@design("coffee_espresso_machine", T)
def espresso_machine(rng):
    body = rrect(-2.6, -2.6, 2.6, 2.0, 0.3)
    tray = [rect(-2.4, 2.0, 2.4, 2.25), [(-2.4, 2.25), (-2.4, 2.6), (2.4, 2.6), (2.4, 2.25)]]
    cups_top = [rrect(-1.9, 2.25, -1.3, 2.75, 0.1), rrect(-1.1, 2.25, -0.5, 2.75, 0.1)]
    head = [rrect(-0.6, 0.6, 0.6, 1.0, 0.1), rect(-0.5, 0.35, 0.5, 0.6), [(0.5, 0.48), (2.0, 0.6)], [(0.5, 0.38), (2.0, 0.42)],
            ellipse(2.1, 0.51, 0.15, 0.12, 10)]
    gauge = [circle(-1.55, 1.1, 0.5, 40), [(-1.55, 1.1), (-1.25, 1.35)]]
    knobs = [circle(1.4, 1.2, 0.22, 16), circle(1.95, 1.2, 0.22, 16)]
    wand = [[(-2.2, 0.2), (-2.2, -1.2)], [(-2.0, 0.2), (-2.0, -1.2)], [(-2.2, 0.2), (-2.0, 0.2)]]
    drip = [rect(-1.4, -2.6, 1.4, -2.2)] + [[(x, -2.6), (x, -2.2)] for x in (-0.7, 0.0, 0.7)]
    cup = [cup_body(0, -1.2, -2.2, 0.55, 0.35), ellipse(0, -1.2, 0.55, 0.12, 30), chain([(0.52, -1.5)], quad((0.52, -1.5), (0.95, -1.6), (0.45, -1.95), 8))]
    streams = [[(-0.15, 0.35), (-0.15, -1.15)], [(0.15, 0.35), (0.15, -1.15)]]
    return make("Espresso Machine", [body] + tray + cups_top + head + gauge + knobs + wand + drip + cup + streams)


@design("coffee_hand_grinder", T)
def hand_grinder(rng):
    box = rect(-1.6, -2.8, 1.6, 0.4)
    top = poly((-1.8, 0.4), (1.8, 0.4), (1.6, 0.7), (-1.6, 0.7))
    drawer = [rect(-1.1, -2.2, 1.1, -1.0), circle(0, -1.6, 0.15, 12)]
    hopper = [chain([(-1.2, 0.7)], cubic((-1.2, 0.7), (-1.3, 1.4), (-0.6, 1.5), (-0.4, 1.6), 16), [(0.4, 1.6)], cubic((0.4, 1.6), (0.6, 1.5), (1.3, 1.4), (1.2, 0.7), 16)),
              ellipse(0, 1.6, 0.4, 0.1, 20)]
    shaft = [[(0, 1.6), (0, 2.2)]]
    crank = [poly((0, 2.2), (2.2, 2.7), (2.2, 2.55), (0, 2.05), closed=False), rrect(2.05, 2.7, 2.35, 3.4, 0.14), circle(0, 2.2, 0.15, 12)]
    grain = [wave(-1.5, 1.5, y, 0.08, 1.5, 30) for y in (-0.2, -0.6)] + [wave(-1.5, -1.2, -2.5, 0.04, 0.5, 6)]
    beans = []
    for x, y, a in [(-2.4, -2.5, 0.3), (2.3, -2.6, -0.5), (2.6, -2.0, 1.0)]:
        beans += bean(x, y, 0.3, a)
    return make("Hand-Crank Coffee Grinder", [box, top] + drawer + hopper + shaft + crank + grain + beans)


@design("coffee_cezve", T)
def cezve(rng):
    pot = chain([(-1.6, 1.0)], [(-1.2, 0.6)], cubic((-1.2, 0.6), (-1.7, -0.6), (-1.8, -2.0), (-1.3, -2.2), 20), [(0.7, -2.2)],
                cubic((0.7, -2.2), (1.2, -2.0), (1.1, -0.6), (0.6, 0.6), 20), [(1.0, 1.0)])
    rim = ellipse(-0.3, 1.0, 1.3, 0.2, 50)
    spout = [[(-1.6, 1.0), (-1.95, 1.2), (-1.6, 0.8)]]
    hd = [tube([(0.85, 0.15), (3.1, 1.9)], 0.3)]
    foam = wave(-1.45, 0.85, 0.85, 0.05, 3, 30)
    pattern = [zigzag(-1.6, 1.0, -1.6, 0.15, 6)]
    cup = [cup_body(2.0, -1.4, -2.6, 0.65, 0.45), ellipse(2.0, -1.4, 0.65, 0.13, 30), ea(2.0, -2.65, 1.0, 0.25, math.pi + 0.3, 2 * math.pi - 0.3, 20)]
    st = [steam(-0.6, 1.4, 1.2, 0.15, 1.2), steam(0.0, 1.4, 1.1, 0.15, 1.2, phase=2)]
    return make("Turkish Coffee Cezve", [pot, rim, foam] + spout + hd + pattern + cup + st)


@design("coffee_phin", T)
def phin(rng):
    glass = poly((-1.3, 0.8), (-1.1, -2.8), (1.1, -2.8), (1.3, 0.8), closed=False)
    rim = ellipse(0, 0.8, 1.3, 0.2, 60)
    milk = wave(-1.17, 1.17, -1.7, 0.05, 1.5, 30)
    coffee = wave(-1.25, 1.25, 0.1, 0.04, 2, 30)
    plate = ellipse(0, 0.95, 1.7, 0.3, 70)
    chamber = [poly((-0.9, 1.0), (-1.0, 2.5), (1.0, 2.5), (0.9, 1.0), closed=False), ellipse(0, 2.5, 1.0, 0.18, 40)]
    lid = [chain([(-1.05, 2.6)], quad((-1.05, 2.6), (0, 3.2), (1.05, 2.6), 16)), rrect(-0.2, 2.95, 0.2, 3.3, 0.08)]
    holes = [circle(x, 1.95, 0.08, 8) for x in (-0.5, 0.0, 0.5)]
    drips = [lens((x, y), (x, y - 0.3), 0.4, 8) for x, y in [(-0.2, 0.6), (0.25, 0.4)]]
    spoon = [[(1.2, -0.6), (2.4, 1.8)], ellipse(2.5, 2.0, 0.15, 0.25, 12, rot=-0.45)]
    return make("Vietnamese Phin Filter", [glass, rim, milk, coffee, plate] + chamber + lid + holes + drips + spoon)


@design("coffee_percolator", T)
def percolator(rng):
    body = chain([(-1.0, 1.8)], cubic((-1.0, 1.8), (-1.3, 0.5), (-1.6, -1.5), (-1.5, -2.6), 24), [(1.5, -2.6)],
                 cubic((1.5, -2.6), (1.6, -1.5), (1.3, 0.5), (1.0, 1.8), 24), [(-1.0, 1.8)])
    lid = [quad((-1.0, 1.8), (0, 2.4), (1.0, 1.8), 16), chain([(-0.3, 2.25)], arc(0, 2.6, 0.38, math.pi + 0.7, -0.7, 20)[::-1][::-1]), ]
    knob = [chain(arc(0, 2.65, 0.38, -0.65, math.pi + 0.65, 24))]
    spout = [chain([(-1.25, 0.2)], cubic((-1.25, 0.2), (-2.0, 0.4), (-1.9, 1.5), (-2.5, 2.0), 16), [(-2.25, 2.1)], cubic((-2.25, 2.1), (-1.6, 1.6), (-1.6, 1.4), (-1.05, 1.4), 16))]
    hd = [chain([(1.05, 1.5)], [(2.4, 1.5)], [(2.6, 0.0)], [(2.0, -1.8)], [(1.45, -1.8)]),
          chain([(1.15, 1.1)], [(2.05, 1.1)], [(2.15, 0.0)], [(1.75, -1.4)], [(1.4, -1.4)])]
    bands = [quad((-1.3, -0.4), (0, -0.55), (1.3, -0.4), 16), quad((-1.5, -2.2), (0, -2.35), (1.5, -2.2), 16)]
    st = [steam(-2.4, 2.4, 0.8, 0.12, 1.0)]
    return make("Stovetop Percolator", [body] + lid + knob + spout + hd + bands + st)


@design("coffee_drip_machine", T)
def drip_machine(rng):
    back = chain([(-2.5, -2.8)], [(-2.5, 2.6)], [(1.2, 2.6)], [(1.2, 1.4)], [(-1.4, 1.4)], [(-1.4, -2.2)], [(1.6, -2.2)], [(1.6, -2.8)], [(-2.5, -2.8)])
    reservoir = [rect(-2.3, -1.6, -1.6, 1.2), wave(-2.3, -1.6, 0.0, 0.04, 1, 10)]
    basket = [poly((-1.2, 1.4), (-0.8, 0.6), (0.6, 0.6), (1.0, 1.4), closed=False), [(0.6, 0.9), (1.8, 1.1)]]
    carafe = [chain([(-1.1, 0.3)], [(-1.2, -0.3)], cubic((-1.2, -0.3), (-1.6, -1.0), (-1.4, -2.2), (-0.6, -2.2), 16), [(0.6, -2.2)],
                    cubic((0.6, -2.2), (1.4, -2.2), (1.6, -1.0), (1.2, -0.3), 16), [(1.1, 0.3)], [(-1.1, 0.3)]),
              [(-1.2, -0.3), (1.2, -0.3)],
              chain([(1.3, -0.5)], [(2.2, -0.5)], [(2.2, -1.7)], [(1.4, -1.7)])]
    level = wave(-1.4, 1.4, -1.2, 0.05, 2, 30)
    buttons = [circle(-2.0, -2.5, 0.13, 10), circle(0.0, -2.5, 0.13, 10), rect(0.5, -2.62, 1.3, -2.38)]
    return make("Drip Coffee Maker", [back, level] + reservoir + basket + carafe + buttons)


@design("coffee_cold_brew_jar", T)
def cold_brew(rng):
    jar = chain([(-1.3, 1.8)], [(-1.3, 1.5)], quad((-1.3, 1.5), (-1.8, 1.2), (-1.8, 0.6), 10), [(-1.8, -2.4)], quad((-1.8, -2.4), (-1.8, -2.8), (-1.4, -2.8), 8),
                [(1.4, -2.8)], quad((1.4, -2.8), (1.8, -2.8), (1.8, -2.4), 8), [(1.8, 0.6)], quad((1.8, 0.6), (1.8, 1.2), (1.3, 1.5), 10), [(1.3, 1.8)])
    lid = [rect(-1.4, 1.8, 1.4, 2.4)] + [[(x, 1.85), (x, 2.35)] for x in (-0.9, -0.3, 0.3, 0.9)]
    level = wave(-1.8, 1.8, 0.8, 0.06, 2, 40)
    label = [rrect(-1.2, -1.8, 1.2, -0.2, 0.2)] + bean(0, -1.0, 0.45, 0.4)
    cubes = [tilt([rrect(-0.35, -0.35, 0.35, 0.35, 0.08)], x, y, 1.0, r)[0] for x, y, r in [(-1.0, 0.3, 0.3), (-0.1, 0.4, -0.4)]]
    straw = [poly((0.8, -0.4), (1.7, 3.3), (1.95, 3.25), (1.05, -0.4), closed=False)]
    return make("Cold Brew Mason Jar", [jar, level] + lid + label + cubes + straw)


@design("coffee_milk_frother", T)
def milk_frother(rng):
    jug = chain([(-1.5, 0.8)], [(-2.2, 1.3)], [(-1.3, 0.5)], quad((-1.3, 0.5), (-1.6, -1.0), (-1.4, -2.6), 16), [(1.2, -2.6)],
                quad((1.2, -2.6), (1.4, -1.0), (1.2, 0.8), 16))
    rim = [quad((-1.5, 0.8), (0, 0.6), (1.2, 0.8), 16), quad((-1.5, 0.8), (0, 1.0), (1.2, 0.8), 16)]
    hd = [chain([(1.25, 0.4)], [(2.1, 0.4)], [(2.1, -1.8)], [(1.3, -1.8)]), chain([(1.3, 0.1)], [(1.8, 0.1)], [(1.8, -1.5)], [(1.35, -1.5)])]
    wand = [[(0.3, 3.3), (-0.1, 0.0)], [(0.55, 3.3), (0.15, 0.0)], rrect(-0.2, 3.1, 1.2, 3.5, 0.15)]
    milk = wave(-1.35, 1.25, 0.2, 0.08, 2.5, 30)
    swirl = [spiral(-0.6, -0.4, 0.1, 0.45, 1.4, 60), spiral(0.6, -1.3, 0.1, 0.4, 1.3, 60)]
    st = [steam(-0.8, 1.0, 1.4, 0.18, 1.0), steam(0.9, 1.0, 1.3, 0.18, 1.0, phase=2)]
    return make("Milk Frothing Pitcher", [jug, milk] + rim + hd + wand + swirl + st)


@design("coffee_thermos", T)
def thermos(rng):
    body = rrect(-1.0, -2.8, 1.0, 1.4, 0.4)
    neck = [rect(-0.8, 1.4, 0.8, 1.9)]
    cup_lid = [poly((-1.05, 1.9), (-1.2, 3.0), (1.2, 3.0), (1.05, 1.9)), [(-1.12, 2.5), (1.12, 2.5)]]
    bands = [[(-1.0, 0.6), (1.0, 0.6)], [(-1.0, -2.0), (1.0, -2.0)]]
    logo = bean(0, -0.7, 0.55, 0.6)
    cup = [poly((1.6, -0.6), (1.8, -2.8), (2.9, -2.8), (3.1, -0.6), closed=False), ellipse(2.35, -0.6, 0.75, 0.15, 30)]
    st = [steam(2.2, -0.3, 1.2, 0.15, 1.1), steam(2.6, -0.3, 1.1, 0.15, 1.1, phase=2)]
    return make("Travel Coffee Flask", [body] + neck + cup_lid + bands + logo + cup + st)


# ---------------------------------------------------------------- beans & farm

@design("coffee_bean_pile", T)
def bean_pile(rng):
    out = []
    pts = [(-2.0, -2.2, 0.0), (-0.9, -2.3, 0.6), (0.2, -2.25, -0.4), (1.3, -2.3, 0.3), (2.3, -2.15, -0.8),
           (-1.5, -1.3, 1.1), (-0.4, -1.35, -0.2), (0.75, -1.3, 0.7), (1.85, -1.3, -0.3),
           (-0.95, -0.4, -0.6), (0.15, -0.4, 0.2), (1.25, -0.45, 1.3), (-0.4, 0.5, 0.9), (0.7, 0.45, -0.5), (0.15, 1.35, 0.1)]
    for x, y, a in pts:
        out += bean(x, y, 0.55, a)
    scoop = [chain(ea(-2.0, 1.5, 0.9, 0.4, 0, -math.pi, 20), arc(-2.0, 1.5, 0.9, math.pi, 2 * math.pi, 20)), ellipse(-2.0, 1.5, 0.9, 0.4, 40), tube([(-1.15, 1.2), (0.5, 2.6)], 0.25)]
    sc_beans = bean(-2.3, 1.55, 0.25, 0.4) + bean(-1.75, 1.6, 0.25, -0.5)
    return make("Pile of Roasted Coffee Beans", out + scoop + sc_beans)


@design("coffee_plant_branch", T)
def plant_branch(rng):
    stem = [quad((-3.0, -2.6), (-0.5, -0.2), (2.8, 2.6), 30), quad((-2.9, -2.65), (-0.4, -0.3), (2.85, 2.55), 30)]
    out = stem
    for t, side in [(0.15, 1), (0.3, -1), (0.48, 1), (0.66, -1), (0.85, 1)]:
        x, y = -3.0 + 5.8 * t, -2.6 + 5.2 * t
        d = side
        out += leaf((x, y), (x - 1.6 * d * 0.4 - 0.4, y + 1.5 * d), 0.28)
    berries = []
    for cx, cy in [(-1.4, -1.6), (0.2, -0.2), (1.7, 1.4)]:
        for dx, dy in [(0.0, -0.45), (0.45, -0.25), (-0.4, -0.2), (0.25, -0.75), (-0.2, -0.7)]:
            berries.append(circle(cx + dx + 0.3, cy + dy, 0.24, 20))
    tips = [circle(cx + dx + 0.3, cy + dy - 0.14, 0.05, 6) for cx, cy in [(-1.4, -1.6), (0.2, -0.2), (1.7, 1.4)] for dx, dy in [(0.0, -0.45)]]
    return make("Coffee Branch with Cherries", out + berries + tips)


@design("coffee_cherry_section", T)
def cherry_section(rng):
    skin = circle(0, 0, 2.2, 140)
    pulp = circle(0, 0, 1.8, 120)
    beans_ = [chain(ea(-0.05, 0, 0.9, 1.4, math.pi / 2, 3 * math.pi / 2, 30), [(-0.05, 1.4)]),
              chain(ea(0.05, 0, 0.9, 1.4, math.pi / 2, -math.pi / 2, 30), [(0.05, 1.4)])]
    creases = [quad((-0.45, 1.0), (-0.75, 0), (-0.45, -1.0), 12), quad((0.45, 1.0), (0.75, 0), (0.45, -1.0), 12)]
    stem = [quad((0, 2.2), (0.3, 2.7), (1.0, 2.9), 10)]
    lf = leaf((1.0, 2.9), (2.9, 2.0), 0.3)
    whole = [circle(2.4, -2.0, 0.6, 40), circle(-2.4, -2.1, 0.55, 40), circle(2.45, -2.4, 0.1, 8), circle(-2.4, -2.5, 0.1, 8)]
    return make("Coffee Cherry Cross-Section", [skin, pulp] + beans_ + creases + stem + lf + whole)


@design("coffee_sack", T)
def coffee_sack(rng):
    sack = chain([(-1.9, 1.2)], cubic((-1.9, 1.2), (-2.5, 0.0), (-2.6, -2.2), (-2.0, -2.8), 20), [(2.0, -2.8)],
                 cubic((2.0, -2.8), (2.6, -2.2), (2.5, 0.0), (1.9, 1.2), 20))
    fold = [chain([(-1.9, 1.2)], quad((-1.9, 1.2), (-2.3, 1.7), (-1.7, 1.9), 8), quad((-1.7, 1.9), (0, 1.6), (1.7, 1.9), 16), quad((1.7, 1.9), (2.3, 1.7), (1.9, 1.2), 8)),
            quad((-1.9, 1.2), (0, 0.95), (1.9, 1.2), 16)]
    heap = [chain(arc(-1.0, 1.75, 0.5, 0.3, math.pi - 0.3, 10)), arc(0.0, 1.85, 0.55, 0.3, math.pi - 0.3, 10), arc(1.0, 1.75, 0.5, 0.3, math.pi - 0.3, 10)]
    beans_top = bean(-1.0, 2.1, 0.25, 0.3) + bean(0.1, 2.3, 0.25, -0.4) + bean(0.95, 2.05, 0.25, 0.9)
    stamp = [circle(0, -0.8, 1.0, 60), circle(0, -0.8, 0.8, 50)] + bean(0, -0.8, 0.45, 0.7)
    stripes = [quad((-2.4, -2.1), (0, -2.3), (2.4, -2.1), 20)]
    spilled = bean(2.6, -2.6, 0.3, 0.5) + bean(-2.7, -2.5, 0.3, -0.4)
    return make("Burlap Sack of Coffee", [sack] + fold + heap + beans_top + stamp + stripes + spilled)


@design("coffee_bean_heart", T)
def bean_heart(rng):
    out = []
    pts = resample(heart(0, 0.3, 2.6, 400), 24)
    for i, (x, y) in enumerate(pts):
        nx, ny = pts[(i + 1) % len(pts)]
        a = math.atan2(ny - y, nx - x)
        out += bean(x, y, 0.36, a)
    for x, y, a in [(-1.1, 0.6, 0.4), (1.1, 0.6, -0.4), (0, 0.0, 1.5), (-0.7, -0.8, 0.8), (0.7, -0.8, -0.8), (0, -1.6, 0.2)]:
        out += bean(x, y, 0.4, a)
    return make("Heart of Coffee Beans", out)


# ---------------------------------------------------------------- teapots

@design("coffee_tetsubin", T)
def tetsubin(rng):
    body = chain([(-1.3, 0.8)], cubic((-1.3, 0.8), (-2.5, 0.6), (-2.6, -1.8), (-1.6, -2.2), 24), [(1.6, -2.2)],
                 cubic((1.6, -2.2), (2.6, -1.8), (2.5, 0.6), (1.3, 0.8), 24), [(-1.3, 0.8)])
    lid = [chain([(-1.0, 0.8)], quad((-1.0, 0.8), (0, 1.3), (1.0, 0.8), 16)), circle(0, 1.3, 0.22, 16)]
    hd = [chain([(-1.6, 0.6)], [(-1.4, 1.1)], cubic((-1.4, 1.1), (-1.4, 3.0), (1.4, 3.0), (1.4, 1.1), 30), [(1.6, 0.6)]),
          cubic((-1.15, 1.1), (-1.15, 2.7), (1.15, 2.7), (1.15, 1.1), 30)]
    spout = [chain([(-2.2, -0.4)], [(-3.0, 0.3)], [(-2.85, 0.45)], [(-2.0, 0.05)])]
    knobs = []
    for row, y in enumerate((0.25, -0.35, -0.95, -1.5)):
        w = 1.9 - 0.15 * abs(row - 1)
        n = 6 - (row % 2)
        for i in range(n):
            x = -w + 2 * w * (i + 0.5) / n
            knobs.append(circle(x, y, 0.15, 12))
    trivet = [ellipse(0, -2.4, 2.4, 0.3, 60)]
    return make("Cast Iron Tetsubin Teapot", [body, spout[0]] + lid + hd + knobs + trivet)


@design("coffee_porcelain_teapot", T)
def porcelain_teapot(rng):
    body = chain([(-1.3, 1.0)], cubic((-1.3, 1.0), (-2.6, 0.6), (-2.5, -1.9), (-1.3, -2.1), 24), [(1.3, -2.1)],
                 cubic((1.3, -2.1), (2.5, -1.9), (2.6, 0.6), (1.3, 1.0), 24))
    rim = ellipse(0, 1.0, 1.3, 0.22, 50)
    lid = [chain([(-1.1, 1.05)], cubic((-1.1, 1.05), (-1.0, 1.8), (1.0, 1.8), (1.1, 1.05), 20)), circle(0, 1.95, 0.25, 16)]
    foot = [poly((-1.2, -2.1), (-1.4, -2.5), (1.4, -2.5), (1.2, -2.1), closed=False)]
    spout = [chain(cubic((-2.1, -0.9), (-2.7, -1.0), (-2.9, 0.6), (-3.3, 1.2), 20), [(-3.05, 1.35)],
                   cubic((-3.05, 1.35), (-2.7, 0.8), (-2.6, -0.2), (-2.2, -0.2), 20))]
    hd = [chain([(2.25, 0.3)], cubic((2.25, 0.3), (3.4, 0.7), (3.4, -1.6), (2.15, -1.4), 24)),
          chain([(2.3, 0.0)], cubic((2.3, 0.0), (3.0, 0.15), (3.0, -1.2), (2.25, -1.1), 24))]
    roses = []
    for cx, cy in [(-0.6, -0.6), (0.7, -0.4)]:
        roses += [spiral(cx, cy, 0.05, 0.4, 2.0, 60), lens((cx + 0.3, cy - 0.35), (cx + 0.85, cy - 0.7), 0.3, 10)]
    band = [quad((-1.95, 0.3), (0, 0.0), (1.95, 0.3), 24)]
    return make("English Porcelain Teapot", [body, rim] + lid + foot + spout + hd + roses + band)


@design("coffee_moroccan_teapot", T)
def moroccan_teapot(rng):
    body = chain([(-0.5, 0.6)], cubic((-0.5, 0.6), (-0.6, -0.2), (-1.7, -0.6), (-1.6, -1.6), 20), quad((-1.6, -1.6), (-1.5, -2.2), (-0.9, -2.2), 8),
                 [(0.9, -2.2)], quad((0.9, -2.2), (1.5, -2.2), (1.6, -1.6), 8), cubic((1.6, -1.6), (1.7, -0.6), (0.6, -0.2), (0.5, 0.6), 20))
    neck = [rect(-0.6, 0.6, 0.6, 0.8)]
    lid = [chain([(-0.6, 0.8)], cubic((-0.6, 0.8), (-0.7, 1.6), (-0.1, 1.7), (0, 2.3), 16), cubic((0, 2.3), (0.1, 1.7), (0.7, 1.6), (0.6, 0.8), 16)),
           circle(0, 2.45, 0.15, 12)]
    feet = [poly((-1.0, -2.2), (-0.9, -2.5), (-0.5, -2.5), (-0.4, -2.2), closed=False), poly((0.4, -2.2), (0.5, -2.5), (0.9, -2.5), (1.0, -2.2), closed=False)]
    spout = [chain(cubic((-1.5, -1.3), (-2.3, -1.2), (-2.3, 0.5), (-3.0, 1.6), 20),
                   [(-2.85, 1.7)], cubic((-2.85, 1.7), (-2.0, 0.6), (-2.1, -0.8), (-1.4, -0.9), 20))]
    hd = [chain([(0.55, 0.5)], cubic((0.55, 0.5), (2.6, 1.0), (2.6, -1.0), (1.6, -1.4), 24)),
          chain([(0.75, 0.2)], cubic((0.75, 0.2), (2.15, 0.6), (2.15, -0.8), (1.6, -1.05), 24))]
    deco = [zigzag(-1.3, 1.3, -1.0, 0.15, 6), quad((-1.5, -1.5), (0, -1.7), (1.5, -1.5), 16)]
    glasses = []
    for x in (-2.3, 2.4):
        glasses += [poly((x - 0.45, -1.4), (x - 0.35, -2.5), (x + 0.35, -2.5), (x + 0.45, -1.4), closed=False), ellipse(x, -1.4, 0.45, 0.1, 20),
                    zigzag(x - 0.4, x + 0.4, -2.0, 0.1, 3)]
    mint = leaf((-1.9, -1.35), (-1.7, -0.7), 0.35)
    return make("Moroccan Mint Teapot", [body] + neck + lid + feet + spout + hd + deco + glasses + mint)


@design("coffee_yixing_teapot", T)
def yixing(rng):
    body = chain([(-1.3, 0.6)], cubic((-1.3, 0.6), (-2.4, 0.5), (-2.4, -1.4), (-1.6, -1.6), 20), [(1.6, -1.6)],
                 cubic((1.6, -1.6), (2.4, -1.4), (2.4, 0.5), (1.3, 0.6), 20))
    rim = ellipse(0, 0.6, 1.3, 0.2, 50)
    lid = [ea(0, 0.75, 1.2, 0.25, 0, math.pi, 30), circle(0, 1.2, 0.28, 20)]
    feet = [rect(-1.5, -1.9, 1.5, -1.6)]
    spout = [poly((-2.1, -0.5), (-3.0, 0.4), (-2.85, 0.6), (-1.95, 0.0), closed=False)]
    hd = [chain([(2.05, 0.2)], cubic((2.05, 0.2), (3.1, 0.6), (3.1, -1.4), (2.05, -1.0), 24)),
          chain([(2.15, -0.1)], cubic((2.15, -0.1), (2.75, 0.1), (2.75, -0.9), (2.12, -0.75), 24))]
    seal = [rrect(-0.45, -1.1, 0.45, -0.3, 0.08), [(-0.2, -0.5), (0.2, -0.5)], [(0, -0.5), (0, -0.95)]]
    cups = []
    for x in (-2.0, 0.0, 2.0):
        cups += [cup_body(x, -2.2, -3.0, 0.55, 0.35), ellipse(x, -2.2, 0.55, 0.1, 24)]
    return make("Clay Yixing Teapot", [body, rim] + lid + feet + spout + hd + seal + cups)


@design("coffee_glass_teapot", T)
def glass_teapot(rng):
    body = [circle(0, -0.4, 2.0, 120)]
    lid = [ea(0, 1.5, 0.8, 0.18, math.pi, 2 * math.pi, 20), chain([(-0.8, 1.5)], quad((-0.8, 1.5), (0, 2.1), (0.8, 1.5), 12)), circle(0, 2.1, 0.2, 14)]
    spout = [poly((-1.75, -0.6), (-3.0, 0.9), (-2.85, 1.1), (-1.6, 0.2), closed=False)]
    hd = [chain([(1.6, 0.8)], cubic((1.6, 0.8), (3.2, 1.0), (3.2, -1.6), (1.7, -1.4), 20)),
          chain([(1.75, 0.45)], cubic((1.75, 0.45), (2.7, 0.5), (2.7, -1.1), (1.85, -1.05), 20))]
    flower = [circle(0, -0.6, 0.35, 24)] + [lens((0.35 * math.cos(a), -0.6 + 0.35 * math.sin(a)), (1.2 * math.cos(a), -0.6 + 1.2 * math.sin(a)), 0.3, 12)
                                            for a in [math.radians(15 + 30 * k) for k in range(6)]]
    stem = [(0, -0.95), (0, -2.0)]
    level = wave(-1.95, 1.95, 0.3, 0.05, 2, 40)
    warmer = [rect(-1.3, -2.9, 1.3, -2.35), ellipse(0, -2.35, 1.3, 0.12, 30), poly((-0.1, -2.6), (0, -2.45), (0.1, -2.6), closed=False)]
    return make("Glass Teapot with Blooming Tea", body + lid + spout + hd + flower + [stem, level] + warmer)


@design("coffee_kettle_stove", T)
def kettle_stove(rng):
    body = chain([(-1.0, 1.0)], cubic((-1.0, 1.0), (-2.3, 0.6), (-2.6, -1.0), (-2.2, -1.4), 20), [(2.2, -1.4)],
                 cubic((2.2, -1.4), (2.6, -1.0), (2.3, 0.6), (1.0, 1.0), 20), [(-1.0, 1.0)])
    lid = [chain([(-0.7, 1.05)], quad((-0.7, 1.05), (0, 1.5), (0.7, 1.05), 12)), circle(0, 1.6, 0.18, 12)]
    hd = [chain([(-1.2, 0.85)], cubic((-1.2, 0.85), (-1.2, 2.9), (1.2, 2.9), (1.2, 0.85), 30)), cubic((-0.9, 0.95), (-0.9, 2.5), (0.9, 2.5), (0.9, 0.95), 30)]
    spout = [chain([(-1.9, -0.3)], [(-2.9, 0.8)], [(-2.65, 1.0)], [(-1.75, 0.3)]), poly((-2.95, 0.8), (-3.2, 0.95), (-2.75, 1.25), (-2.62, 1.03), closed=False)]
    whistle = [steam(-2.9, 1.3, 1.2, 0.18, 1.0), steam(-2.4, 1.4, 1.0, 0.15, 1.0, phase=2)]
    grate = [[(-3.0, -1.5), (3.0, -1.5)], [(-2.6, -1.5), (-2.6, -2.3)], [(2.6, -1.5), (2.6, -2.3)], rect(-3.2, -2.9, 3.2, -2.3)]
    flames = []
    for x in (-1.6, -0.8, 0.0, 0.8, 1.6):
        flames.append(chain(quad((x - 0.25, -2.3), (x - 0.3, -1.9), (x, -1.6), 8), quad((x, -1.6), (x + 0.3, -1.9), (x + 0.25, -2.3), 8)))
    knobs = [circle(x, -2.6, 0.18, 12) for x in (-2.2, 2.2)]
    return make("Whistling Kettle on the Stove", [body] + lid + hd + spout + whistle + grate + flames + knobs)


@design("coffee_samovar", T)
def samovar(rng):
    urn = chain([(-1.0, 1.2)], cubic((-1.0, 1.2), (-2.1, 0.8), (-2.1, -1.2), (-0.8, -1.5), 20), [(0.8, -1.5)],
                cubic((0.8, -1.5), (2.1, -1.2), (2.1, 0.8), (1.0, 1.2), 20), [(-1.0, 1.2)])
    base = [poly((-0.6, -1.5), (-0.4, -2.1), (0.4, -2.1), (0.6, -1.5), closed=False), rect(-1.4, -2.4, 1.4, -2.1)] + \
           [poly((x - 0.2, -2.4), (x, -2.8), (x + 0.2, -2.4), closed=False) for x in (-1.1, 1.1)]
    crown = [rect(-0.5, 1.2, 0.5, 1.5)]
    pot = [chain([(-0.7, 1.5)], cubic((-0.7, 1.5), (-1.2, 1.7), (-1.1, 2.4), (-0.5, 2.5), 12), [(0.5, 2.5)], cubic((0.5, 2.5), (1.1, 2.4), (1.2, 1.7), (0.7, 1.5), 12)),
           arc(0, 2.5, 0.4, 0, math.pi, 12), circle(0, 3.0, 0.12, 8), poly((-1.0, 2.0), (-1.6, 2.4), (-1.0, 2.25), closed=False)]
    handles = [chain([(-1.85, 0.4)], [(-2.6, 0.6)], [(-2.6, -0.2)], [(-1.95, -0.3)]), chain([(1.85, 0.4)], [(2.6, 0.6)], [(2.6, -0.2)], [(1.95, -0.3)])]
    tap = [chain([(-0.2, -0.6)], [(-0.2, -0.9)], [(-0.8, -0.95)], [(-1.0, -1.3)], [(-0.75, -1.35)], [(-0.6, -1.15)], [(0.2, -1.1)], [(0.2, -0.6)]),
           circle(0, -0.45, 0.2, 14)]
    bands = [quad((-1.55, 0.6), (0, 0.4), (1.55, 0.6), 16), quad((-1.6, -0.9), (0, -1.1), (1.6, -0.9), 16)]
    medals = [circle(x, 0.0, 0.18, 12) for x in (-1.1, 1.1)]
    return make("Russian Samovar", [urn] + base + crown + pot + handles + tap + bands + medals)


@design("coffee_tea_cosy", T)
def tea_cosy(rng):
    cosy = chain([(-2.4, -2.0)], cubic((-2.4, -2.0), (-2.6, 1.6), (2.6, 1.6), (2.4, -2.0), 40))
    rib = [[(-2.4, -2.0), (2.4, -2.0)], wave(-2.38, 2.38, -1.6, 0.08, 6, 60)]
    cables = []
    for x in (-1.2, 0.0, 1.2):
        cables.append([(x + 0.18 * math.sin(TAU * i / 12 * 2.5), -1.4 + 2.2 * i / 12) for i in range(13)])
        cables.append([(x - 0.18 * math.sin(TAU * i / 12 * 2.5), -1.4 + 2.2 * i / 12) for i in range(13)])
    pom = [circle(0, 1.55, 0.45, 30)] + [[(0.3 * math.cos(a), 1.55 + 0.3 * math.sin(a)), (0.6 * math.cos(a), 1.55 + 0.6 * math.sin(a))] for a in [k * TAU / 8 for k in range(8)]]
    spout = [poly((-2.45, -0.8), (-3.2, 0.2), (-3.0, 0.35), (-2.35, -0.3), closed=False)]
    hd = [chain([(2.4, -0.2)], cubic((2.4, -0.2), (3.3, 0.0), (3.3, -1.4), (2.42, -1.4), 16))]
    tray = [ellipse(0, -2.2, 3.0, 0.35, 80)]
    return make("Knitted Tea Cosy", [cosy] + rib + cables + pom + spout + hd + tray)


@design("coffee_kyusu", T)
def kyusu(rng):
    body = chain([(-1.0, 0.8)], cubic((-1.0, 0.8), (-2.1, 0.6), (-2.1, -1.4), (-1.0, -1.5), 20), [(1.0, -1.5)],
                 cubic((1.0, -1.5), (2.1, -1.4), (2.1, 0.6), (1.0, 0.8), 20), [(-1.0, 0.8)])
    lid = [chain([(-0.8, 0.85)], quad((-0.8, 0.85), (0, 1.3), (0.8, 0.85), 12)), rrect(-0.2, 1.2, 0.2, 1.5, 0.08)]
    spout = [poly((-1.8, -0.6), (-2.8, 0.4), (-2.6, 0.55), (-1.65, -0.05), closed=False)]
    side = [tube([(1.4, -0.1), (3.1, 1.3)], 0.45)]
    leaves = [quad((-1.2, -0.7), (0, -0.2), (1.2, -0.7), 12)] + leaf((-0.2, -1.0), (0.7, -0.45), 0.3)
    cups = []
    for x in (-1.7, 1.2):
        cups += [rect(x - 0.5, -2.9, x + 0.5, -1.8), ellipse(x, -1.8, 0.5, 0.1, 24), [(x - 0.5, -2.2), (x + 0.5, -2.2)]]
    return make("Japanese Kyusu and Teacups", [body] + lid + spout + side + leaves + cups)


# ---------------------------------------------------------------- tea scenes

@design("coffee_teacup_stack", T)
def teacup_stack(rng):
    out = []
    for k, (dx, b) in enumerate([(0.0, -2.6), (0.25, -1.1), (-0.15, 0.4)]):
        out += teacup(dx, b, w=1.35, h=1.1, bw=0.7, sr=2.0 - 0.1 * k, side=1 if k % 2 == 0 else -1)
    deco = [zigzag(-0.95, 0.95, -2.0, 0.12, 5), wave(-0.75, 1.25, -0.5, 0.1, 3, 30), zigzag(-1.1, 0.8, 1.0, 0.12, 5)]
    return make("Stack of Teacups", out + deco)


@design("coffee_teabag_cup", T)
def teabag_cup(rng):
    cup = teacup(-0.3, -2.0, w=1.9, h=2.2, bw=1.1, sr=2.9)
    string = [[(0.6, 0.15), (1.6, 0.25)], [(1.6, 0.25), (2.0, -1.0)]]
    tag = [rect(1.65, -1.95, 2.45, -1.0), heart(2.05, -1.4, 0.25, 40)]
    bag = []
    tea = ea(-0.3, 0.2, 1.7, 0.26, math.pi + 0.15, 2 * math.pi - 0.15, 30)
    st = [steam(-1.0, 0.8, 1.5, 0.2, 1.0), steam(-0.3, 0.8, 1.7, 0.2, 1.0, phase=2), steam(0.4, 0.8, 1.5, 0.2, 1.0, phase=4)]
    return make("Tea Bag in a Cup", cup + string + tag + bag + [tea] + st)


@design("coffee_tea_sprig", T)
def tea_sprig(rng):
    stem = [quad((0.2, -3.0), (0.0, 0.0), (0.4, 2.8), 30)]

    def serrated(p0, p1, bulge):
        base = lens(p0, p1, bulge, 30)
        out = []
        for i, (x, y) in enumerate(base):
            out.append((x, y))
        cx, cy = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        teeth = []
        for i in range(len(base)):
            x, y = base[i]
            f = 1.0 + (0.06 if i % 2 else 0.0)
            teeth.append((cx + (x - cx) * f, cy + (y - cy) * f))
        return [teeth, [p0, ((p0[0] + p1[0] * 4) / 5, (p0[1] + p1[1] * 4) / 5)]]
    parts = stem
    parts += serrated((0.05, -1.6), (-2.5, -0.6), 0.28) + serrated((0.08, -0.6), (2.6, 0.2), 0.28) + serrated((0.12, 0.6), (-2.2, 1.6), 0.26)
    parts += serrated((0.25, 1.6), (1.9, 2.6), 0.26)
    bud = [lens((0.4, 2.8), (0.45, 3.6), 0.25, 14)]
    flower = [circle(1.6, -2.0, 0.3, 20)] + [lens((1.6 + 0.3 * math.cos(a), -2.0 + 0.3 * math.sin(a)), (1.6 + 1.0 * math.cos(a), -2.0 + 1.0 * math.sin(a)), 0.45, 12)
                                             for a in [math.radians(90 + 72 * k) for k in range(5)]]
    fstem = [[(1.2, -1.5), (0.18, -1.2)]]
    return make("Tea Plant Sprig", parts + bud + flower + fstem)


@design("coffee_matcha", T)
def matcha(rng):
    bowl = [ellipse(-0.8, 0.2, 2.0, 0.45, 90), chain([(-2.8, 0.2)], cubic((-2.8, 0.2), (-2.8, -1.8), (-1.6, -2.1), (-0.8, -2.1), 20),
                                                     cubic((-0.8, -2.1), (0.0, -2.1), (1.2, -1.8), (1.2, 0.2), 20))]
    foot = [poly((-1.6, -2.05), (-1.5, -2.4), (-0.1, -2.4), (0.0, -2.05), closed=False)]
    foam = [wave(-2.5, 0.9, 0.15, 0.06, 4, 40)] + [circle(x, y, 0.1, 8) for x, y in [(-1.6, 0.3), (-0.6, 0.12), (0.3, 0.3)]]
    whisk = [chain([(1.9, -2.4)], cubic((1.9, -2.4), (1.3, -1.8), (1.4, -0.6), (1.9, -0.4), 16), [(2.5, -0.4)], cubic((2.5, -0.4), (3.0, -0.6), (3.1, -1.8), (2.5, -2.4), 16), [(1.9, -2.4)]),
             rect(1.95, -0.4, 2.45, 1.8)] + [[(2.2 + 0.18 * k, -0.4), (2.2 + 0.4 * k, -2.25)] for k in (-1.5, -0.5, 0.5, 1.5)]
    scoop = [tube([(-2.9, 1.6), (0.4, 2.6)], 0.25), ellipse(0.55, 2.6, 0.35, 0.18, 16, rot=0.3)]
    return make("Matcha Bowl and Whisk", bowl + foot + foam + whisk + scoop)


@design("coffee_tea_tin", T)
def tea_tin(rng):
    tin = [chain([(-1.5, 1.4)], [(-1.5, -2.6)]), chain([(1.5, 1.4)], [(1.5, -2.6)]), ea(0, -2.6, 1.5, 0.35, math.pi, 2 * math.pi, 40)]
    lid = [ellipse(0, 2.0, 1.6, 0.38, 60), chain([(-1.6, 2.0)], [(-1.6, 1.45)]), chain([(1.6, 2.0)], [(1.6, 1.45)]), ea(0, 1.45, 1.6, 0.38, math.pi, 2 * math.pi, 40),
           ellipse(0, 2.05, 0.4, 0.1, 20)]
    label = [rrect(-1.2, -1.8, 1.2, 0.6, 0.2)] + leaf((-0.6, -1.3), (0.4, 0.1), 0.3) + leaf((0.0, -1.3), (0.9, -0.3), 0.3)
    loose = []
    for x, y, a in [(-2.5, -2.4, 0.5), (2.3, -2.2, -0.6), (2.7, -2.7, 1.2), (-2.2, -2.85, -0.2)]:
        loose += leaf((x - 0.35 * math.cos(a), y - 0.35 * math.sin(a)), (x + 0.35 * math.cos(a), y + 0.35 * math.sin(a)), 0.3, vein=False)
    spoon = [ellipse(2.3, -1.3, 0.35, 0.22, 18), [(2.3, -1.08), (2.6, 0.6)]]
    return make("Loose Leaf Tea Tin", tin + lid + label + loose + spoon)


@design("coffee_chai_carrier", T)
def chai_carrier(rng):
    out = []
    for x in (-2.1, -0.7, 0.7, 2.1):
        out += [poly((x - 0.55, 0.3), (x - 0.4, -2.0), (x + 0.4, -2.0), (x + 0.55, 0.3), closed=False), ellipse(x, 0.3, 0.55, 0.12, 24),
                wave(x - 0.5, x + 0.5, -0.1, 0.05, 1, 10), [(x - 0.47, -0.8), (x + 0.47, -0.8)]]
    frame = [rect(-2.9, -2.3, 2.9, -2.0), [(-2.9, -2.0), (-2.9, -0.6), (2.9, -0.6), (2.9, -2.0)], [(0, -0.6), (0, 2.0)],
             ellipse(0, 2.4, 0.5, 0.4, 24)]
    st = [steam(x, 0.6, 1.0, 0.12, 1.0, phase=x) for x in (-2.1, -0.7, 0.7, 2.1)]
    return make("Chai Glasses in a Carrier", out + frame + st)


@design("coffee_bubble_tea", T)
def bubble_tea(rng):
    cup = poly((-1.4, 1.2), (-1.1, -2.8), (1.1, -2.8), (1.4, 1.2), closed=False)
    seal = [ellipse(0, 1.2, 1.4, 0.3, 60)]
    straw = [poly((-0.05, -2.0), (0.7, 3.2), (1.2, 3.1), (0.45, -2.0), closed=False), [(0.66, 2.9), (1.16, 2.8)]]
    pearls = [circle(x, y, 0.2, 14) for x, y in [(-0.75, -2.45), (-0.3, -2.5), (0.6, -2.45), (0.9, -2.1), (-0.85, -2.0), (-0.45, -2.05), (0.65, -1.8), (-0.6, -1.6)]]
    level = wave(-1.32, 1.32, 0.3, 0.05, 2, 30)
    cubes = [tilt([rrect(-0.3, -0.3, 0.3, 0.3, 0.06)], x, y, 1.0, r)[0] for x, y, r in [(-0.7, -0.2, 0.3), (0.85, -0.5, -0.3)]]
    band = []
    return make("Bubble Tea with Pearls", [cup, level] + seal + straw + pearls + cubes + band)


@design("coffee_afternoon_tea", T)
def afternoon_tea(rng):
    pole = [[(0, -2.8), (0, 2.6)], circle(0, 2.85, 0.25, 16)]
    plates = []
    for y, r in [(-2.4, 2.8), (-0.6, 2.2), (1.2, 1.6)]:
        plates += [ellipse(0, y, r, 0.3, 80)]
    sandwiches = [poly((-2.3, -2.3), (-1.0, -2.3), (-1.65, -1.5)), poly((-0.8, -2.3), (0.5, -2.3), (-0.15, -1.5)), poly((0.8, -2.3), (2.1, -2.3), (1.45, -1.5))]
    scones = []
    for x in (-1.3, 1.1):
        scones += [chain([(x - 0.55, -0.5)], cubic((x - 0.55, -0.5), (x - 0.6, 0.2), (x + 0.6, 0.2), (x + 0.55, -0.5), 16), [(x - 0.55, -0.5)]),
                   quad((x - 0.55, -0.25), (x, -0.15), (x + 0.55, -0.25), 8)]
    cakes = []
    for x in (-0.95, 0.85):
        cakes += [rect(x - 0.35, 1.25, x + 0.35, 1.7), arc(x, 1.7, 0.35, 0, math.pi, 10), circle(x, 2.15, 0.1, 8)]
    return make("Afternoon Tea Stand", pole + plates + sandwiches + scones + cakes)


@design("coffee_honey_jar", T)
def honey_jar(rng):
    jar = chain([(-1.2, 1.0)], cubic((-1.2, 1.0), (-2.2, 0.6), (-2.2, -2.4), (-1.0, -2.6), 20), [(1.0, -2.6)],
                cubic((1.0, -2.6), (2.2, -2.4), (2.2, 0.6), (1.2, 1.0), 20))
    lid = [rect(-1.3, 1.0, 1.3, 1.4), ellipse(0, 1.6, 1.4, 0.3, 50), [(-1.4, 1.6), (-1.3, 1.4)], [(1.4, 1.6), (1.3, 1.4)]]
    drip = [chain([(-1.25, 1.0)], [(-1.25, 0.3)], arc(-1.1, 0.3, 0.15, math.pi, 2 * math.pi, 8), [(-0.95, 1.0)])]
    label = [rrect(-1.3, -1.6, 1.3, -0.2, 0.25)]
    hexes = [poly(*[(x + 0.3 * math.cos(a), y + 0.3 * math.sin(a)) for a in [k * TAU / 6 for k in range(6)]]) for x, y in [(-0.5, -0.9), (0.0, -0.6), (0.5, -0.9)]]
    dipper = [tube([(0.75, 2.0), (2.9, 3.1)], 0.2), ellipse(0.3, 1.75, 0.5, 0.36, 24, rot=0.5),
              transform([(-0.45, 0), (0.45, 0)], 0.3, 1.75, rot=0.5 + math.pi / 2), transform([(-0.38, 0), (0.38, 0)], 0.15, 1.82, rot=0.5 + math.pi / 2),
              transform([(-0.38, 0), (0.38, 0)], 0.45, 1.68, rot=0.5 + math.pi / 2)]
    grooves = []
    cup = teacup(2.4, -2.6, w=0.7, h=0.8, bw=0.4, sr=1.0)
    return make("Honey Jar with Dipper", [jar] + lid + drip + label + hexes + dipper + grooves + cup)


@design("coffee_tea_lemon", T)
def tea_lemon(rng):
    cup = [chain([(-1.6, 1.0)], [(-1.4, -2.0)], quad((-1.4, -2.0), (-1.35, -2.4), (-0.9, -2.4), 8), [(0.9, -2.4)], quad((0.9, -2.4), (1.35, -2.4), (1.4, -2.0), 8), [(1.6, 1.0)]),
           ellipse(0, 1.0, 1.6, 0.3, 70)]
    tea = wave(-1.55, 1.55, 0.5, 0.05, 2, 30)
    hd = handle((1.57, 0.4), (1.45, -1.6), 1.1, 0.35)
    slice_ = [circle(-1.5, 1.3, 0.85, 50), circle(-1.5, 1.3, 0.68, 40)] + \
             [[(-1.5, 1.3), (-1.5 + 0.66 * math.cos(a), 1.3 + 0.66 * math.sin(a))] for a in [k * TAU / 8 for k in range(8)]]
    wedge = [chain(arc(1.9, -2.6, 0.9, 0.0, math.pi, 24), [(2.8, -2.6)]), arc(1.9, -2.6, 0.72, 0.15, math.pi - 0.15, 20)]
    plate = [ea(0, -2.5, 3.0, 0.45, 0.1, -math.pi - 0.1, 60)]
    st = [steam(0.2, 1.5, 1.2, 0.15, 1.1), steam(0.8, 1.5, 1.1, 0.15, 1.1, phase=2)]
    return make("Tea with Lemon Slice", cup + [tea] + hd + slice_ + wedge + plate + st)


@design("coffee_tea_tray", T)
def tea_tray(rng):
    tray = [poly((-3.0, -2.8), (3.0, -2.8), (2.4, -0.8), (-2.4, -0.8)), poly((-2.85, -2.6), (2.85, -2.6), (2.3, -0.95), (-2.3, -0.95))]
    handles = [ellipse(-3.05, -1.8, 0.2, 0.45, 16), ellipse(3.05, -1.8, 0.2, 0.45, 16)]
    pot = [chain([(-0.6, 1.0)], cubic((-0.6, 1.0), (-1.6, 0.8), (-1.6, -1.1), (-0.8, -1.4), 16), [(0.8, -1.4)], cubic((0.8, -1.4), (1.6, -1.1), (1.6, 0.8), (0.6, 1.0), 16)),
           chain([(-0.5, 1.0)], quad((-0.5, 1.0), (0, 1.4), (0.5, 1.0), 10)), circle(0, 1.5, 0.13, 10),
           poly((-1.4, -0.4), (-2.2, 0.6), (-2.05, 0.75), (-1.3, 0.1), closed=False),
           chain([(1.35, 0.4)], cubic((1.35, 0.4), (2.1, 0.5), (2.1, -0.8), (1.35, -0.8), 16))]
    cups = teacup(-1.6, -2.2, w=0.6, h=0.55, bw=0.32, sr=0.85, side=-1) + teacup(1.7, -2.2, w=0.6, h=0.55, bw=0.32, sr=0.85)
    sugar = [rrect(-0.35, -2.4, 0.35, -1.85, 0.12), ellipse(0, -1.85, 0.35, 0.08, 16)]
    return make("Tea Set on a Tray", tray + handles + pot + cups + sugar)


@design("coffee_gaiwan", T)
def gaiwan(rng):
    saucer_ = [ellipse(0, -1.8, 2.8, 0.55, 100), ea(0, -1.95, 2.8, 0.55, math.pi, 2 * math.pi, 50)]
    bowl = [cup_body(0, 0.4, -1.6, 1.7, 0.7, 0.5), ellipse(0, 0.4, 1.8, 0.28, 60)]
    lid = [chain([(-1.7, 0.45)], cubic((-1.7, 0.45), (-1.4, 1.5), (1.4, 1.5), (1.7, 0.45), 24)), rect(-0.3, 1.2, 0.3, 1.55), ellipse(0, 1.55, 0.4, 0.1, 20)]
    clouds = [spiral(-0.8, -0.5, 0.05, 0.3, 1.3, 40), spiral(0.0, -0.75, 0.05, 0.3, 1.3, 40), spiral(0.8, -0.5, 0.05, 0.3, 1.3, 40), wave(-1.0, 1.0, 0.9, 0.06, 3, 30)]
    leaves = leaf((-2.6, 1.6), (-1.6, 2.3), 0.3) + leaf((-2.4, 2.4), (-1.4, 2.8), 0.3)
    st = [steam(1.6, 1.0, 1.4, 0.15, 1.2), steam(2.2, 0.8, 1.3, 0.15, 1.2, phase=2)]
    return make("Chinese Gaiwan Lidded Cup", saucer_ + bowl + lid + clouds + leaves + st)


@design("coffee_sugar_creamer", T)
def sugar_creamer(rng):
    bowl = [cup_body(-1.4, 0.0, -1.8, 1.3, 0.7), ellipse(-1.4, 0.0, 1.3, 0.25, 50),
            cubic((-2.5, 0.08), (-2.4, 0.9), (-0.4, 0.9), (-0.3, 0.08), 20), circle(-1.4, 0.95, 0.2, 14)]
    ears = [chain([(-2.65, -0.3)], cubic((-2.65, -0.3), (-3.3, -0.3), (-3.2, -1.0), (-2.45, -1.0), 12)),
            chain([(-0.15, -0.3)], cubic((-0.15, -0.3), (0.5, -0.3), (0.4, -1.0), (-0.35, -1.0), 12))]
    jug = [chain([(0.9, 0.6)], [(0.6, 0.85)], [(1.0, 0.4)], cubic((1.0, 0.4), (0.7, -0.6), (0.9, -1.8), (1.5, -1.8), 16), [(2.3, -1.8)],
                 cubic((2.3, -1.8), (2.9, -1.8), (3.0, -0.6), (2.6, 0.5), 16)), quad((0.9, 0.6), (1.8, 0.45), (2.6, 0.5), 12),
           chain([(2.7, 0.0)], cubic((2.7, 0.0), (3.4, 0.0), (3.4, -1.3), (2.85, -1.3), 12))]
    cubes = [rect(-0.4, -2.6, 0.2, -2.0), rect(-1.15, -2.6, -0.55, -2.0)]
    tray = [[(-3.2, -2.6), (3.2, -2.6)]]
    tongs = []
    return make("Sugar Bowl and Creamer", bowl + ears + jug + cubes + tray + tongs)


@design("coffee_infuser", T)
def infuser(rng):
    cup = teacup(0.0, -2.4, w=1.8, h=1.9, bw=1.0, sr=2.8, side=-1)
    tea = ea(0, -0.5, 1.6, 0.25, math.pi + 0.15, 2 * math.pi - 0.15, 30)
    ball = [circle(0.4, 1.0, 0.8, 60), [(-0.4, 1.0), (1.2, 1.0)]] + [circle(0.4 + dx, 1.0 + dy, 0.09, 8) for dx, dy in [(-0.35, 0.35), (0.0, 0.5), (0.35, 0.35), (-0.35, -0.35), (0.0, -0.5), (0.35, -0.35)]]
    hang = [[(0.4, 1.8), (0.8, 2.4), (1.4, 2.9)], rect(1.4, 2.4, 2.2, 3.2)]
    drips = [lens((x, y), (x, y - 0.35), 0.4, 8) for x, y in [(0.1, 0.05), (0.7, -0.05)]]
    st = [steam(-1.1, -0.1, 1.2, 0.15, 1.0), steam(-0.6, 0.0, 1.0, 0.15, 1.0, phase=2)]
    return make("Tea Infuser Ball", cup + [tea] + ball + hang + drips + st)


@design("coffee_tea_terraces", T)
def tea_terraces(rng):
    out = [poly((-3.2, 1.9), (-2.0, 3.1), (-1.2, 2.5), (0.0, 3.3), (1.0, 2.6), (1.6, 2.9), (3.2, 2.0), closed=False)]
    rows = [(1.3, 0.8), (0.2, 0.8), (-0.9, 0.8), (-2.0, 0.6)]
    for k, (y, bend) in enumerate(rows):
        x0 = -3.2
        edge = quad((x0, y), (0.0, y + bend), (3.2, y), 40)
        if k == 3:
            edge = [p for p in edge if p[0] <= 0.8]
        out.append(edge)
        out.append([(x, yy - 0.25) for x, yy in edge])
        m = max(4, int((edge[-1][0] - edge[0][0]) / 0.5))
        idx = [round(i * (len(edge) - 1) / m) for i in range(m + 1)]
        bumps = []
        for a_, b_ in zip(idx, idx[1:]):
            a, b = edge[a_], edge[b_]
            ang = math.atan2(b[1] - a[1], b[0] - a[0])
            half = math.dist(a, b) / 2
            bumps += [((a[0] + b[0]) / 2 + half * math.cos(t) * math.cos(ang) - 0.38 * math.sin(t) * math.sin(ang),
                       (a[1] + b[1]) / 2 + half * math.cos(t) * math.sin(ang) + 0.38 * math.sin(t) * math.cos(ang)) for t in [math.pi - math.pi * i / 10 for i in range(10)]]
        bumps.append(edge[-1])
        out.append(bumps)
    basket = [poly((1.2, -1.9), (1.5, -3.2), (2.9, -3.2), (3.2, -1.9)), [(1.3, -2.35), (3.1, -2.35)], [(1.4, -2.8), (3.0, -2.8)]]
    tl = leaf((1.6, -1.9), (1.3, -1.1), 0.3) + leaf((2.2, -1.9), (2.3, -1.0), 0.3) + leaf((2.8, -1.9), (3.2, -1.15), 0.3)
    return make("Tea Terraces in the Mountains", out + basket + tl)


@design("coffee_shop_front", T)
def shop_front(rng):
    wall = rect(-3.0, -2.8, 3.0, 1.6)
    roof = [rect(-3.2, 1.6, 3.2, 2.0), rrect(-1.6, 2.0, 1.6, 2.9, 0.2)]
    sign_cup = [cup_body(0, 2.75, 2.2, 0.35, 0.22), ellipse(0, 2.75, 0.35, 0.08, 16), chain([(0.33, 2.6)], quad((0.33, 2.6), (0.65, 2.45), (0.28, 2.35), 6))]
    sign_st = [steam(-0.4, 2.3, 0.4, 0.06, 1.0), steam(0.45, 2.3, 0.4, 0.06, 1.0)]
    awn = []
    n = 8
    for i in range(n):
        x0 = -3.0 + 6.0 * i / n
        x1 = x0 + 6.0 / n
        awn.append(chain([(x0, 1.4)], [(x0 - 0.1, 0.6)], arc((x0 + x1) / 2 - 0.1, 0.6, (x1 - x0) / 2, math.pi, 2 * math.pi, 8)))
    awn.append([(-3.0, 1.4), (3.0, 1.4)])
    awn.append([(2.25, 1.4), (2.15, 0.6)])
    window = [rect(-2.6, -1.8, 0.0, 0.0), [(-1.3, -1.8), (-1.3, 0.0)]]
    door = [rect(0.6, -2.8, 2.4, 0.2), rect(0.9, -1.0, 2.1, -0.1), circle(0.9, -1.5, 0.08, 8)]
    win_cup = [cup_body(-0.65, -0.6, -1.4, 0.4, 0.25), ellipse(-0.65, -0.6, 0.4, 0.08, 16)]
    win_beans = bean(-2.0, -1.0, 0.35, 0.5)
    sill = [rect(-2.8, -2.05, 0.2, -1.8)]
    return make("Coffee Shop Storefront", [wall] + roof + sign_cup + sign_st + awn + window + door + win_cup + win_beans + sill)


@design("coffee_chalkboard", T)
def chalkboard(rng):
    legs = [[(-2.4, -2.9), (-1.6, 2.6)], [(2.4, -2.9), (1.6, 2.6)], [(-1.6, 2.6), (1.6, 2.6)]]
    board = [poly((-1.95, -2.1), (-1.35, 2.2), (1.35, 2.2), (1.95, -2.1))]
    cup = [cup_body(0, 1.0, -0.2, 0.75, 0.45), ellipse(0, 1.0, 0.75, 0.15, 30), chain([(0.72, 0.75)], cubic((0.72, 0.75), (1.25, 0.75), (1.2, 0.05), (0.6, 0.1), 12))]
    st = [steam(-0.2, 1.3, 0.6, 0.08, 1.0), steam(0.25, 1.3, 0.6, 0.08, 1.0, phase=2)]
    menu = [wave(-1.3, 0.6, -0.65, 0.06, 3, 30), wave(-1.4, 0.3, -1.15, 0.06, 3, 30), wave(-1.45, 0.8, -1.65, 0.06, 3, 30)]
    prices = [circle(1.1, -0.65, 0.12, 10), circle(1.1, -1.15, 0.12, 10), circle(1.2, -1.65, 0.12, 10)]
    stars_ = [star(-1.1, 1.6, 0.25), star(1.1, 1.6, 0.25)]
    return make("Cafe Chalkboard Sign", legs + board + cup + st + menu + prices + stars_)


@design("coffee_tamper_portafilter", T)
def tamper(rng):
    basket = [chain([(-1.6, 0.0)], [(-1.4, -1.0)], [(1.4, -1.0)], [(1.6, 0.0)]), ellipse(0, 0.0, 1.6, 0.3, 60)]
    ring = [ea(0, -0.25, 1.65, 0.3, math.pi, 2 * math.pi, 30)]
    handle_ = [tube([(1.5, -0.5), (3.2, -1.3)], 0.5)]
    spouts = [poly((-0.5, -1.0), (-0.4, -1.6), (-0.1, -1.6), (0.0, -1.0), closed=False), poly((0.0, -1.0), (0.1, -1.6), (0.4, -1.6), (0.5, -1.0), closed=False)]
    tamper_ = [rect(-1.3, 0.6, 1.3, 1.1), ea(0, 1.1, 1.3, 0.2, 0, math.pi, 30)]
    top = [(0.74 * math.cos(t), 2.85 + 0.74 * math.sin(t)) for t in [math.radians(200) - math.radians(220) * i / 30 for i in range(31)]]
    knob = [chain(cubic((-0.3, 1.27), (-0.4, 1.8), (-0.9, 2.2), top[0], 12), top, cubic(top[-1], (0.9, 2.2), (0.4, 1.8), (0.3, 1.27), 12))]
    grounds = [circle(-2.4, -2.4, 0.12, 8), circle(-2.0, -2.6, 0.12, 8), circle(2.2, -2.6, 0.12, 8)]
    cup = [cup_body(0, -2.0, -2.8, 0.6, 0.4), ellipse(0, -2.0, 0.6, 0.12, 20)]
    return make("Tamper and Portafilter", basket + ring + handle_ + spouts + tamper_ + knob + grounds + cup)


@design("coffee_harvest_basket", T)
def harvest_basket(rng):
    basket = chain([(-2.4, 0.0)], [(-1.8, -2.6)], [(1.8, -2.6)], [(2.4, 0.0)])
    rim = [rrect(-2.6, -0.1, 2.6, 0.3, 0.15)]
    weave = [quad((-2.25, y), (0, y - 0.2), (2.25, y), 16) for y in (-0.7, -1.3, -1.9)] + [[(x, -0.1), (x * 0.75, -2.6)] for x in (-1.2, 0.0, 1.2)]
    cherries = []
    for x, y in [(-1.9, 0.6), (-1.35, 0.95), (-0.8, 0.6), (-0.4, 1.15), (0.1, 0.65), (0.55, 1.1), (1.0, 0.6), (1.5, 0.95), (1.95, 0.55), (-0.9, 1.6), (0.1, 1.65), (0.95, 1.55)]:
        cherries.append(circle(x, y, 0.3, 20))
    branch = [quad((-1.0, 1.9), (0.0, 2.6), (1.6, 2.4), 16)] + leaf((-1.0, 1.9), (-2.8, 2.7), 0.28) + leaf((0.4, 2.4), (-0.6, 3.2), 0.3) + leaf((1.6, 2.4), (3.0, 3.0), 0.28)
    loose = [circle(2.8, -2.4, 0.28, 18), circle(-2.8, -2.4, 0.28, 18)]
    return make("Basket of Coffee Cherries", [basket] + rim + weave + cherries + branch + loose)
