"""Sports niche: balls, gear, athletes in action, trophies and arenas."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "sports"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ---------------------------------------------------------------- helpers

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


def limb(pts, w0, w1=None, cap=True, n=8):
    """Smooth tapered band through the joint points."""
    w1 = w0 if w1 is None else w1
    return tube(smooth(pts, n), lambda t: w0 + (w1 - w0) * t, cap)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def shoe(ankle, toe, s=1.0):
    """Sport shoe as a rounded sole shape from heel to toe."""
    heel = lerp(ankle, toe, -0.28)
    return lens(heel, toe, 0.3 * s, 16)


def body_shape(torso, tw):
    """Torso outline: hips, slimmer waist, broad chest and rounded shoulders."""
    c = smooth(torso, 10)
    n = len(c)
    left, right = [], []
    for i, (x, y) in enumerate(c):
        a = c[max(0, i - 1)]
        b = c[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        t = i / (n - 1)
        w = tw * (0.86 - 0.12 * math.sin(math.pi * min(1.0, t / 0.6)) if t < 0.45 else 0.8 + 0.2 * min(1.0, (t - 0.45) / 0.35)) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    dx, dy = c[-1][0] - c[-2][0], c[-1][1] - c[-2][1]
    L = math.hypot(dx, dy) or 1.0
    top = (c[-1][0] + dx / L * tw * 0.35, c[-1][1] + dy / L * tw * 0.35)
    shoulders = cubic(left[-1], (left[-1][0] + top[0] - c[-1][0], left[-1][1] + top[1] - c[-1][1]),
                      (right[-1][0] + top[0] - c[-1][0], right[-1][1] + top[1] - c[-1][1]), right[-1], 14)
    return left + shoulders[1:] + right[::-1][1:] + [left[0]]


def athlete(head, torso, arms=(), legs=(), hr=0.4, tw=0.95, aw=0.34, lw=0.5, feet=True, hands=True):
    """Figure built from smooth tubes.

    torso: centre line from hip to neck; arms: [shoulder, elbow, hand];
    legs: [hip, knee, ankle, toe]."""
    out = [circle(head[0], head[1], hr, 40), body_shape(torso, tw)]
    for a in arms:
        out.append(limb(a[:3], aw, aw * 0.78, cap=False))
        if hands:
            out.append(circle(a[2][0], a[2][1], aw * 0.62, 14))
    for lg in legs:
        out.append(limb(lg[:3], lw, lw * 0.66, cap=False))
        if feet and len(lg) > 3:
            out.append(shoe(lg[2], lg[3]))
    return out


def densify(pts, step=0.05):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(1, int(L / step))
        out += [lerp(a, b, i / k) for i in range(1, k + 1)]
    return out


def clip_out(pts, holes):
    """Split a polyline, dropping the parts inside any circle (cx, cy, r)."""
    segs, cur = [], []
    for p in densify(pts):
        inside = any(math.hypot(p[0] - cx, p[1] - cy) < r for cx, cy, r in holes)
        if inside:
            if len(cur) > 1:
                segs.append(cur)
            cur = []
        else:
            cur.append(p)
    if len(cur) > 1:
        segs.append(cur)
    return segs


def clip_all(strokes, holes):
    out = []
    for s in strokes:
        out += clip_out(s, holes)
    return out


def side_arc(r, d, R):
    """Arc of a circle centred (-d, 0) radius R that lies inside the circle of radius r at the origin."""
    x = (R * R - r * r - d * d) / (2 * d)
    y = math.sqrt(max(0.0, r * r - x * x))
    a = math.atan2(y, x + d)
    return arc(-d, 0, R, -a, a, 30)


def soccer_pattern(cx, cy, r):
    """Pentagon-and-hexagon panels of a soccer ball."""
    out = [circle(cx, cy, r, 100)]
    R1 = 0.3 * r
    cen = [(cx + R1 * math.cos(math.pi / 2 + k * TAU / 5), cy + R1 * math.sin(math.pi / 2 + k * TAU / 5)) for k in range(5)]
    out.append(cen + [cen[0]])
    P = [(cx + 0.52 * r * math.cos(math.pi / 2 + k * TAU / 5), cy + 0.52 * r * math.sin(math.pi / 2 + k * TAU / 5)) for k in range(5)]
    for k in range(5):
        out.append([cen[k], P[k]])
    for j in range(5):
        b = math.pi / 2 + j * TAU / 5 + TAU / 10
        ox, oy = cx + 0.8 * r * math.cos(b), cy + 0.8 * r * math.sin(b)
        rr = 0.2 * r
        v = [(ox + rr * math.cos(b + m * TAU / 5), oy + rr * 0.8 * math.sin(b + m * TAU / 5)) for m in range(5)]
        v = [(ox + (x - ox) * math.cos(0) , y) for x, y in v]
        out.append(v + [v[0]])
        out.append([P[j], v[3]])
        out.append([P[(j + 1) % 5], v[2]])
        for m in (0, 1, 4):
            a = math.atan2(v[m][1] - cy, v[m][0] - cx)
            out.append([v[m], (cx + r * math.cos(a), cy + r * math.sin(a))])
    return out


def basketball_lines(cx, cy, r, rot=0.0):
    side = side_arc(r, 1.45 * r, 1.12 * r)
    seams = [[(-r, 0), (r, 0)], [(0, -r), (0, r)], side, mirror_x(side)]
    out = [circle(cx, cy, r, 90)]
    out += [transform(s, dx=cx, dy=cy, rot=rot) for s in seams]
    return out


def baseball(cx, cy, r, rot=0.0, stitches=None):
    seam = side_arc(r, 1.35 * r, 0.95 * r)
    out = [circle(cx, cy, r, 60), transform(seam, cx, cy, 1, rot), transform(mirror_x(seam), cx, cy, 1, rot)]
    if stitches or (stitches is None and r >= 0.8):
        for i in range(3, len(seam) - 3, 4):
            x, y = seam[i]
            a = math.atan2(y, x + 1.35 * r)
            for sgn in (1, -1):
                p = [(sgn * (x + 0.12 * math.cos(a + 0.5)), y + 0.12 * math.sin(a + 0.5)), (sgn * (x - 0.12 * math.cos(a - 0.5)), y - 0.12 * math.sin(a - 0.5))]
                out.append(transform(p, cx, cy, 1, rot))
    return out


def tennis_ball(cx, cy, r, rot=0.3):
    seam = side_arc(r, 1.05 * r, 0.72 * r)
    return [circle(cx, cy, r, 60), transform(seam, cx, cy, 1, rot), transform(mirror_x(seam), cx, cy, 1, rot)]


def digit(d, x, y, w, h):
    """Seven-segment numeral drawn as one stroke."""
    A, B, C, D, E, F = (x, y + h), (x + w, y + h), (x + w, y + h / 2), (x + w, y), (x, y), (x, y + h / 2)
    paths = {
        0: [A, B, D, E, A], 1: [(x + w / 2, y + h), (x + w / 2, y)], 2: [A, B, C, F, E, D], 3: [A, B, C, F, C, D, E],
        4: [A, F, C, B, D], 5: [B, A, F, C, D, E], 6: [B, A, E, D, C, F], 7: [A, B, D], 8: [F, A, B, D, E, F, C],
        9: [C, F, A, B, D, E],
    }
    return paths[d]


def ground(x0=-3.2, x1=3.2, y=-2.8):
    return [(x0, y), (x1, y)]


# ---------------------------------------------------------------- soccer

@design("sports_soccer_ball", T)
def soccer_ball(rng):
    ball = soccer_pattern(0, 0.3, 2.4)
    shadow = [ellipse(0, -2.45, 2.0, 0.28, 50)]
    grass = [zigzag(-3.2, 3.2, -2.85, 0.15, 16)]
    return make("Classic Soccer Ball", ball + shadow + grass)


@design("sports_soccer_striker", T)
def soccer_striker(rng):
    fig = athlete((0.35, 2.35), [(-0.05, 0.25), (0.05, 1.2), (0.2, 1.85)],
                  arms=[[(-0.05, 1.7), (-0.85, 1.35), (-1.55, 1.8)], [(0.4, 1.7), (1.05, 1.25), (1.25, 0.55)]],
                  legs=[[(-0.25, 0.3), (-0.45, -0.95), (-0.75, -2.2), (-0.25, -2.4)], [(0.2, 0.3), (1.0, -0.45), (1.9, -1.0), (2.3, -0.75)]])
    shorts = [chain(quad((-0.55, 0.0), (0.0, -0.25), (0.6, 0.0), 10))]
    collar = [arc(0.2, 1.95, 0.25, math.pi + 0.3, 2 * math.pi - 0.3, 8)]
    ball = soccer_pattern(2.7, 0.15, 0.55)
    hair = [arc(0.35, 2.35, 0.42, 0.2, math.pi - 0.2, 14)]
    return make("Soccer Striker Kicking", fig + shorts + collar + ball + hair + [ground(-2.0, 1.2, -2.5)])


@design("sports_goal_net", T)
def goal_net(rng):
    fx0, fx1, fy0, fy1 = -3.0, 3.0, -1.8, 1.4
    bx0, bx1, by1 = -2.3, 2.3, 2.1
    front = [[(fx0, fy0), (fx0, fy1), (fx1, fy1), (fx1, fy0)]]
    back = [[(bx0, -1.2), (bx0, by1), (bx1, by1), (bx1, -1.2)]]
    sides = [[(fx0, fy1), (bx0, by1)], [(fx1, fy1), (bx1, by1)], [(fx0, fy0), (bx0, -1.2)], [(fx1, fy0), (bx1, -1.2)]]
    net = []
    for k in range(1, 9):
        x = bx0 + (bx1 - bx0) * k / 9
        net.append([(x, -1.2), (x, by1)])
    for k in range(1, 6):
        y = -1.2 + (by1 + 1.2) * k / 6
        net.append([(bx0, y), (bx1, y)])
    for k in range(1, 4):
        t = k / 4
        net.append([lerp((fx0, fy1), (fx1, fy1), 0), lerp((fx0, fy1), (bx0, by1), 0)])
    net = net[:-3]
    for k in range(1, 9):
        t = k / 9
        net.append([lerp((fx0, fy1), (fx1, fy1), t), lerp((bx0, by1), (bx1, by1), t)])
    holes = [(0.9, -0.6, 0.85)]
    ball = soccer_pattern(0.9, -0.6, 0.75)
    grass = [[(-3.3, -1.8), (3.3, -1.8)], [(-3.3, -2.6), (3.3, -2.6)]]
    box = [[(-2.2, -1.8), (-2.6, -2.6)], [(2.2, -1.8), (2.6, -2.6)]]
    return make("Ball in the Back of the Net", front + clip_all(back + sides + net, holes) + ball + grass + box)


@design("sports_soccer_cleats", T)
def soccer_cleats(rng):
    def boot(dx, dy, s, rot):
        upper = smooth([(-1.6, -0.3), (-1.65, 0.6), (-1.3, 1.1), (-0.6, 0.9), (0.3, 0.5), (1.3, 0.25), (1.75, -0.05), (1.6, -0.3)], 6)
        sole = [(-1.7, -0.3), (1.65, -0.3)]
        bottom = rrect(-1.7, -0.5, 1.65, -0.3, 0.1)
        studs = [poly((x - 0.14, -0.5), (x - 0.09, -0.78), (x + 0.09, -0.78), (x + 0.14, -0.5), closed=False) for x in (-1.3, -0.8, 0.4, 0.9, 1.35)]
        laces = [[(-0.75 + 0.3 * k, 0.95 - 0.1 * k), (-0.55 + 0.3 * k, 0.6 - 0.1 * k)] for k in range(4)]
        stripe = [quad((-1.0, -0.2), (-0.2, 0.25), (0.3, 0.1), 10), quad((-0.85, -0.2), (-0.1, 0.05), (0.6, -0.2), 10)]
        collar = [quad((-1.55, 0.75), (-1.0, 1.25), (-0.65, 0.95), 8)]
        return [transform(p, dx, dy, s, rot) for p in [upper, sole, bottom, *studs, *laces, *stripe, *collar]]
    ball = soccer_pattern(1.8, 1.9, 0.9)
    return make("Pair of Soccer Cleats", boot(-0.5, 0.4, 1.0, 0.0) + boot(0.4, -1.7, 1.0, 0.0) + ball)


# ---------------------------------------------------------------- basketball

@design("sports_basketball", T)
def basketball(rng):
    ball = basketball_lines(0, 0.6, 2.2, 0.35)
    floor = [[(-3.2, -2.5), (3.2, -2.5)], ellipse(0, -2.5, 1.6, 0.2, 40)]
    motion = [arc(0, 0.6, 2.6, math.radians(120), math.radians(160), 10), arc(0, 0.6, 2.9, math.radians(125), math.radians(150), 8),
              [(-1.3, -2.1), (-1.6, -1.8)], [(1.3, -2.1), (1.6, -1.8)], [(0.0, -2.0), (0.0, -1.7)]]
    return make("Bouncing Basketball", ball + floor + motion)


@design("sports_hoop", T)
def hoop(rng):
    board = [rect(-2.6, 0.4, 2.6, 3.2), rect(-0.8, 1.0, 0.8, 2.2)]
    bracket = [poly((-0.5, 0.4), (-0.3, 0.0), (0.3, 0.0), (0.5, 0.4), closed=False)]
    rim = [ellipse(0, -0.2, 1.1, 0.28, 50)]
    net = [[(-1.1, -0.2), (-0.75, -1.9)], [(1.1, -0.2), (0.75, -1.9)]]
    tops = [-1.1 + 2.2 * k / 6 for k in range(7)]
    bots = [-0.75 + 1.5 * k / 6 for k in range(7)]
    for k in range(6):
        net.append([(tops[k], -0.2 - 0.25 * math.sin(math.pi * k / 6) * 0.9), (bots[k + 1], -1.9)])
        net.append([(tops[k + 1], -0.2 - 0.25 * math.sin(math.pi * (k + 1) / 6) * 0.9), (bots[k], -1.9)])
    net.append([(-0.75, -1.9), (0.75, -1.9)])
    ball = basketball_lines(1.9, -1.6, 0.85, 0.5)
    holes = [(1.9, -1.6, 0.85)]
    return make("Basketball Hoop and Backboard", board + bracket + rim + clip_all(net, holes) + ball)


@design("sports_slam_dunk", T)
def slam_dunk(rng):
    fig = athlete((-0.6, 0.9), [(-0.5, -0.8), (-0.55, 0.0), (-0.55, 0.5)],
                  arms=[[(-0.25, 0.35), (0.3, 1.2), (0.85, 1.85)], [(-0.85, 0.35), (-1.55, 0.6), (-2.0, 1.1)]],
                  legs=[[(-0.7, -0.85), (-0.3, -1.75), (-0.85, -2.4), (-0.45, -2.6)], [(-0.3, -0.85), (-1.1, -1.5), (-1.35, -2.35), (-0.95, -2.5)]])
    jersey = [[(-0.85, -0.8), (-0.15, -0.8)], digit(2, -0.75, -0.55, 0.3, 0.6), digit(3, -0.35, -0.55, 0.3, 0.6)]
    board = [rect(1.0, 1.6, 3.2, 3.4), rect(1.6, 2.0, 2.6, 2.8)]
    rim = [ellipse(1.6, 1.6, 0.6, 0.15, 30)]
    net = [[(1.0, 1.6), (1.25, 0.6)], [(2.2, 1.6), (1.95, 0.6)], [(1.25, 0.6), (1.95, 0.6)], [(1.0, 1.6), (1.95, 0.6)], [(2.2, 1.6), (1.25, 0.6)],
           [(1.6, 1.45), (1.6, 0.6)]]
    ball = basketball_lines(1.25, 2.05, 0.45, 0.4)
    clip = clip_all(net + board, [(1.25, 2.05, 0.45)])
    return make("Slam Dunk", fig + jersey + clip + rim + ball)


@design("sports_hightop_sneaker", T)
def hightop_sneaker(rng):
    upper = smooth([(-2.4, -1.2), (-2.5, 0.6), (-2.3, 2.3), (-1.0, 2.4), (-0.9, 1.0), (0.3, 0.2), (1.9, -0.2), (2.6, -0.6), (2.6, -1.2)], 6)
    sole = [rrect(-2.6, -1.8, 2.75, -1.2, 0.3)]
    tread = [[(x, -1.8), (x + 0.2, -1.6)] for x in (-2.0, -1.3, -0.6, 0.1, 0.8, 1.5, 2.2)]
    toe = [quad((1.0, -1.2), (1.5, -0.3), (2.6, -0.7), 10)]
    laces = [[(-0.9 + 0.35 * k, 2.0 - 0.45 * k), (-0.45 + 0.35 * k, 2.15 - 0.45 * k)] for k in range(4)]
    tongue = [quad((-1.0, 2.4), (-0.7, 2.9), (-0.3, 2.6), 8)]
    star_ = [star(-1.7, 0.2, 0.55, 5, 0.45)]
    ankle = [circle(-1.75, 1.6, 0.18, 12)]
    stitch = [[(-2.4, -0.9), (0.8, -0.9)]]
    return make("High-Top Basketball Sneaker", [upper] + sole + tread + toe + laces + tongue + star_ + ankle + stitch)


# ---------------------------------------------------------------- football

@design("sports_american_football", T)
def american_football(rng):
    rot = 0.45
    body = lens((-3.0, 0), (3.0, 0), 0.42, 60)

    def h(x):
        return 1.26 * (1 - (x / 3.0) ** 2) - 0.02

    seam = [[(-1.1, 0.25), (1.1, 0.25)]]
    laces = [[(x, 0.0), (x, 0.5)] for x in (-0.8, -0.4, 0.0, 0.4, 0.8)]
    stripes = []
    for x in (-2.1, -1.75, 1.75, 2.1):
        b = -0.12 if x < 0 else 0.12
        stripes.append(quad((x, h(x)), (x + b, 0.0), (x, -h(x)), 12))
    parts = [transform(p, rot=rot) for p in [body] + seam + laces + stripes]
    tee = [poly((-0.7, -2.9), (-0.45, -2.1), (0.45, -2.1), (0.7, -2.9), closed=False), [(-1.6, -2.9), (1.6, -2.9)]]
    return make("American Football", parts + tee)


@design("sports_football_helmet", T)
def football_helmet(rng):
    shell = smooth([(1.35, 0.75), (1.0, 1.9), (-0.3, 2.55), (-1.75, 2.05), (-2.5, 0.8), (-2.4, -0.6), (-1.7, -1.3), (-0.7, -1.1),
                    (0.1, -1.5), (0.85, -1.3), (0.95, -0.2), (1.3, 0.35)], 8, True)
    ear = [ellipse(-0.55, -0.05, 0.42, 0.5, 30), circle(-0.55, -0.05, 0.18, 14)]
    stripe = [smooth([(1.2, 1.2), (0.0, 2.25), (-1.5, 1.95), (-2.3, 0.9)], 10), smooth([(1.32, 0.95), (0.0, 1.95), (-1.35, 1.7), (-2.1, 0.75)], 10)]
    rim = [smooth([(-2.4, -0.4), (-1.6, -0.95), (-0.7, -0.8), (0.1, -1.15), (0.75, -1.0)], 8)]
    mask = [poly((1.3, 0.55), (2.45, 0.45), (2.7, -0.55), (2.35, -1.55), (0.85, -1.35), closed=False),
            [(1.0, -0.3), (2.62, -0.25)], [(0.95, -0.85), (2.55, -0.95)], [(1.9, 0.5), (1.85, -1.5)]]
    clips = [rrect(1.05, 0.4, 1.4, 0.7, 0.08), rrect(0.65, -1.5, 1.0, -1.2, 0.08)]
    strap = [smooth([(0.8, -1.4), (0.9, -2.0), (1.6, -2.3), (2.1, -1.65)], 8), ellipse(1.45, -2.05, 0.45, 0.25, 24, rot=0.3)]
    vents = [circle(-1.5, 1.45, 0.14, 10), circle(-1.05, 1.75, 0.14, 10)]
    return make("Football Helmet", [shell] + ear + stripe + rim + mask + clips + strap + vents)


@design("sports_field_goal", T)
def field_goal(rng):
    post = [poly((-0.12, -2.8), (-0.12, 0.0), (-1.8, 0.0), (-1.8, 3.2), (-1.55, 3.2), (-1.55, 0.25), (1.55, 0.25), (1.55, 3.2),
                 (1.8, 3.2), (1.8, 0.0), (0.12, 0.0), (0.12, -2.8), closed=False)]
    pad = [rrect(-0.3, -2.8, 0.3, -1.4, 0.12)]
    flags = [poly((-1.67, 3.2), (-1.67, 3.4), (-1.1, 3.6), (-1.67, 3.8)), poly((1.67, 3.2), (1.67, 3.4), (2.25, 3.6), (1.67, 3.8))]
    ball = [transform(lens((-0.6, 0), (0.6, 0), 0.32, 24), 0.3, 1.8, 1, 0.8), transform([(-0.15, 0.08), (0.2, 0.08)], 0.3, 1.8, 1, 0.8)]
    arcpath = [quad((-3.0, -2.2), (-2.4, 1.6), (-0.3, 1.5), 20)]
    field = [[(-3.2, -2.8), (3.2, -2.8)], [(-3.2, -2.0), (-2.6, -2.8)], [(3.2, -2.0), (2.6, -2.8)]]
    return make("Field Goal Through the Uprights", post + pad + flags + ball + arcpath + field)


@design("sports_quarterback", T)
def quarterback(rng):
    fig = athlete((0.0, 2.2), [(0.1, 0.0), (0.0, 1.0), (0.0, 1.7)], hr=0.45, tw=1.15, aw=0.38, lw=0.55,
                  arms=[[(-0.4, 1.5), (-1.2, 1.7), (-1.6, 2.6)], [(0.4, 1.5), (1.1, 1.1), (1.4, 0.3)]],
                  legs=[[(-0.15, 0.0), (-0.9, -1.2), (-1.4, -2.4), (-0.9, -2.6)], [(0.35, 0.0), (0.9, -1.1), (1.0, -2.5), (1.5, -2.6)]])
    pads = [arc(0.0, 1.35, 0.85, math.radians(15), math.radians(165), 20)]
    mask = [[(0.35, 2.15), (0.65, 2.15)], [(0.35, 1.95), (0.6, 1.95)], [(0.62, 2.3), (0.62, 1.85)]]
    helmet = [arc(0.0, 2.2, 0.55, math.radians(-30), math.radians(200), 20)]
    nums = [digit(1, -0.4, 0.4, 0.3, 0.6), digit(2, -0.0, 0.4, 0.3, 0.6)]
    ball = [transform(lens((-0.4, 0), (0.4, 0), 0.32, 20), -1.7, 2.95, 1, 0.9)]
    pants = [[(-0.35, 0.05), (0.55, 0.05)]]
    return make("Quarterback Throwing a Pass", fig + pads + mask + helmet + nums + ball + pants + [ground(-2.2, 2.2, -2.75)])


# ---------------------------------------------------------------- baseball

@design("sports_bat_ball_glove", T)
def bat_ball_glove(rng):
    bat = [transform(chain(cubic((-3.0, -0.08), (-1.0, -0.1), (0.0, -0.3), (2.8, -0.3), 20), arc(2.8, 0, 0.3, -math.pi / 2, math.pi / 2, 10),
                           cubic((2.8, 0.3), (0.0, 0.3), (-1.0, 0.1), (-3.0, 0.08), 20), [(-3.0, -0.08)]), 0, 0, 1, 0.5),
           transform(ellipse(-3.05, 0, 0.12, 0.25, 16), 0, 0, 1, 0.5)]
    grip = [transform([(-2.4 + 0.25 * k, -0.08), (-2.3 + 0.25 * k, 0.09)], 0, 0, 1, 0.5) for k in range(4)]
    w = 0.25
    pts = [(0.5, -2.3), (1.05, -1.2), (1.05, 0.9)]
    fingers = [(0.8, 0.9, 0.55), (0.3, 1.5, 0.05), (-0.2, 1.75, -0.45), (-0.7, 1.5, -0.95)]
    valleys = []
    for k, (x, tip, nxt) in enumerate(fingers):
        pts += arc(x, tip, w, 0, math.pi, 10)
        if k < 3:
            pts += [(nxt, 0.75)]
            valleys.append([(nxt, 0.75), (nxt + 0.05 * (k - 1), -0.2)])
    pts += [(-0.95, 0.6)] + quad((-0.95, 0.6), (-1.35, 0.3), (-1.75, 0.85), 8) + arc(-1.95, 0.7, 0.25, 0.6, math.pi + 0.3, 8)
    pts += smooth([(-2.2, 0.6), (-2.1, -0.4), (-1.5, -1.5), (-0.8, -2.3)], 6) + [(0.5, -2.3)]
    glove = [transform(p, -0.6, -0.4, 1.0) for p in [pts] + valleys + [
        [(-1.05, 0.35), (-1.65, 0.75)], [(-1.0, 0.0), (-1.95, 0.4)], ellipse(-0.3, -0.75, 0.85, 0.65, 36), [(-1.6, -1.75), (0.75, -1.75)]]]
    ball = baseball(1.7, -1.7, 0.85, 0.3)
    return make("Baseball, Bat and Glove", bat + grip + glove + ball)


@design("sports_baseball_diamond", T)
def baseball_diamond(rng):
    hp = (0.0, -2.6)
    fence = [arc(0, -2.6, 5.3, math.radians(52), math.radians(128), 40)]
    foul = [[hp, (3.2, 1.6)], [hp, (-3.2, 1.6)]]
    infield = [quad((2.0, -0.6), (0.0, 1.8), (-2.0, -0.6), 30)]
    diamond = [[hp, (1.5, -1.1), (0.0, 0.4), (-1.5, -1.1), hp]]
    bases = [poly((1.5, -1.25), (1.65, -1.1), (1.5, -0.95), (1.35, -1.1)), poly((0.0, 0.25), (0.15, 0.4), (0.0, 0.55), (-0.15, 0.4)),
             poly((-1.5, -1.25), (-1.35, -1.1), (-1.5, -0.95), (-1.65, -1.1))]
    plate = [poly((0, -2.75), (0.18, -2.6), (0.18, -2.45), (-0.18, -2.45), (-0.18, -2.6))]
    mound = [circle(0.0, -1.1, 0.35, 24), [(-0.12, -1.1), (0.12, -1.1)]]
    boxes = [rect(-0.65, -2.8, -0.3, -2.3), rect(0.3, -2.8, 0.65, -2.3)]
    board = [rect(-0.8, 2.75, 0.8, 3.4), [(-0.4, 2.45), (-0.4, 2.75)], [(0.4, 2.45), (0.4, 2.75)]]
    return make("Baseball Diamond", fence + foul + infield + diamond + bases + plate + mound + boxes + board)


@design("sports_catcher_mask", T)
def catcher_mask(rng):
    frame = smooth([(0, 2.6), (1.6, 2.2), (2.1, 0.6), (1.6, -1.4), (0.8, -2.2), (0, -2.4), (-0.8, -2.2), (-1.6, -1.4), (-2.1, 0.6), (-1.6, 2.2)], 8, True)
    pad = smooth([(0, 2.2), (1.25, 1.85), (1.7, 0.6), (1.3, -1.1), (0.0, -1.95), (-1.3, -1.1), (-1.7, 0.6), (-1.25, 1.85)], 8, True)
    bars = [[(-1.75, 0.9), (1.75, 0.9)], [(-1.65, -0.2), (1.65, -0.2)], [(-1.25, -1.15), (1.25, -1.15)],
            [(-0.45, 2.15), (-0.45, -1.85)], [(0.45, 2.15), (0.45, -1.85)]]
    throat = [poly((-0.6, -2.35), (-0.5, -3.1), (0.5, -3.1), (0.6, -2.35), closed=False)]
    straps = [[(-2.1, 0.6), (-2.9, 1.0)], [(2.1, 0.6), (2.9, 1.0)], [(-1.8, -0.8), (-2.8, -0.9)], [(1.8, -0.8), (2.8, -0.9)]]
    buckles = [rrect(-3.15, 0.85, -2.85, 1.25, 0.06), rrect(2.85, 0.85, 3.15, 1.25, 0.06)]
    return make("Catcher's Mask", [frame, pad] + bars + throat + straps + buckles)


@design("sports_batter", T)
def batter(rng):
    fig = athlete((0.3, 2.0), [(0.0, -0.1), (0.1, 0.8), (0.25, 1.5)],
                  arms=[[(0.5, 1.35), (1.05, 1.05), (1.5, 1.4)], [(0.0, 1.35), (0.7, 0.8), (1.4, 1.25)]],
                  legs=[[(-0.25, -0.1), (-0.9, -1.2), (-1.3, -2.4), (-0.85, -2.55)], [(0.25, -0.1), (0.95, -1.1), (1.3, -2.4), (1.75, -2.5)]])
    helmet = [chain(arc(0.3, 2.0, 0.47, math.radians(-10), math.radians(190), 20)), [(0.75, 1.95), (1.15, 1.85)], circle(0.15, 1.9, 0.12, 10)]
    bat = [tube([(1.45, 1.35), (0.2, 3.3)], lambda t: 0.12 + 0.18 * t, cap=True)]
    belt = [[(-0.4, 0.1), (0.45, 0.1)]]
    ball = baseball(-2.2, 1.0, 0.4, 0.4)
    speed = [[(-2.75, 1.0), (-3.2, 1.0)], [(-2.7, 1.25), (-3.1, 1.25)], [(-2.7, 0.75), (-3.1, 0.75)]]
    plate = [poly((-0.5, -2.75), (0.0, -2.95), (0.5, -2.75), (0.5, -2.6), (-0.5, -2.6))]
    return make("Batter Ready to Swing", fig + helmet + bat + belt + ball + speed + plate)


@design("sports_pitcher", T)
def pitcher(rng):
    fig = athlete((0.4, 1.9), [(0.0, -0.2), (0.15, 0.6), (0.35, 1.4)],
                  arms=[[(0.6, 1.25), (1.2, 0.8), (1.6, 1.35)], [(0.1, 1.25), (-0.8, 1.6), (-1.6, 2.4)]],
                  legs=[[(0.0, -0.2), (-0.3, -1.4), (-0.4, -2.55), (0.1, -2.65)], [(0.2, -0.2), (1.3, 0.3), (1.15, -0.8), (1.6, -0.9)]])
    cap = [chain(arc(0.4, 2.0, 0.38, 0, math.pi, 14)), [(0.78, 2.0), (1.25, 1.95)]]
    glove = [ellipse(1.75, 1.45, 0.38, 0.45, 24, rot=0.4), [(1.6, 1.25), (1.9, 1.7)]]
    ball = baseball(-1.75, 2.65, 0.28, 0.5)
    belt = [[(-0.35, -0.05), (0.45, -0.05)]]
    mound = [quad((-2.8, -2.65), (0.0, -2.0), (2.8, -2.65), 30), rect(-0.5, -2.45, 0.5, -2.3)]
    nums = [digit(7, 0.0, 0.3, 0.35, 0.6)]
    return make("Pitcher's Windup", fig + cap + glove + ball + belt + mound + nums)


# ---------------------------------------------------------------- racket sports

@design("sports_tennis_racket", T)
def tennis_racket(rng):
    rot = -0.6
    head = ellipse(0, 1.0, 1.35, 1.75, 80)
    inner = ellipse(0, 1.0, 1.15, 1.55, 80)
    strings = []
    for k in range(-3, 4):
        x = 0.33 * k
        h = 1.55 * math.sqrt(max(0, 1 - (x / 1.15) ** 2))
        strings.append([(x, 1.0 - h), (x, 1.0 + h)])
    for k in range(-4, 5):
        y = 0.33 * k
        w = 1.15 * math.sqrt(max(0, 1 - (y / 1.55) ** 2))
        strings.append([(-w, 1.0 + y), (w, 1.0 + y)])
    throat = [poly((-0.6, -0.55), (-0.18, -1.3), (-0.18, -2.0), closed=False), poly((0.6, -0.55), (0.18, -1.3), (0.18, -2.0), closed=False)]
    handle = [rrect(-0.24, -3.4, 0.24, -2.0, 0.1)] + [[(-0.24, -2.2 - 0.3 * k), (0.24, -2.35 - 0.3 * k)] for k in range(4)]
    parts = [transform(p, -0.4, 0.3, 0.95, rot) for p in [head, inner] + strings + throat + handle]
    ball = tennis_ball(2.0, -1.8, 0.75)
    return make("Tennis Racket and Ball", parts + ball)


@design("sports_tennis_serve", T)
def tennis_serve(rng):
    fig = athlete((-0.2, 1.4), [(0.0, -0.6), (-0.1, 0.2), (-0.15, 0.95)],
                  arms=[[(0.1, 0.85), (0.6, 1.6), (0.75, 2.4)], [(-0.4, 0.85), (-1.1, 1.3), (-1.4, 2.0)]],
                  legs=[[(-0.2, -0.6), (-0.6, -1.6), (-0.6, -2.7), (-0.1, -2.8)], [(0.2, -0.6), (0.7, -1.5), (1.4, -2.2), (1.7, -1.95)]])
    skirt = [chain([(-0.45, -0.3)], quad((-0.45, -0.3), (-0.65, -0.75), (-0.6, -1.0), 6), wave(-0.6, 0.6, -1.0, 0.05, 2, 12)[1:],
                   quad((0.6, -1.0), (0.6, -0.75), (0.42, -0.3), 6))]
    head_r = [transform(ellipse(0, 0, 0.45, 0.6, 40), 1.2, 3.0, 1, -0.4), transform([(0, -0.6), (0, -1.2)], 1.2, 3.0, 1, -0.4)]
    strings = [transform([(x, -0.5), (x, 0.5)], 1.2, 3.0, 1, -0.4) for x in (-0.2, 0.0, 0.2)] + \
              [transform([(-0.38, y), (0.38, y)], 1.2, 3.0, 1, -0.4) for y in (-0.25, 0.0, 0.25)]
    ball = [circle(-1.5, 2.85, 0.3, 24), arc(-1.85, 2.85, 0.3, -0.9, 0.9, 10)]
    visor = [[(-0.5, 1.6), (0.25, 1.6)], [(0.15, 1.55), (0.55, 1.45)]]
    pony = [lens((-0.5, 1.55), (-1.0, 1.0), 0.3, 12)]
    court = [[(-3.0, -2.9), (3.0, -2.9)], [(-3.0, -2.5), (-2.3, -2.5)]]
    return make("Tennis Player Serving", fig + skirt + head_r + strings + ball + visor + pony + court)


@design("sports_badminton", T)
def badminton(rng):
    # shuttlecock
    cork = chain(arc(0, 0, 0.55, math.pi, 2 * math.pi, 20))
    cone = [[(-0.55, 0.0), (-1.4, 2.4)], [(0.55, 0.0), (1.4, 2.4)], ellipse(0, 2.4, 1.4, 0.35, 50), ellipse(0, 0.0, 0.55, 0.14, 20)]
    ribs = [[(x * 0.35, 0.05), (x, 2.08 if abs(x) < 1.2 else 2.2)] for x in (-0.95, -0.5, 0.0, 0.5, 0.95)]
    band = [ellipse(0, 0.85, 0.85, 0.2, 30)]
    shuttle = [transform(p, -1.3, -0.6, 0.9, 0.5) for p in [cork] + cone + ribs + band]
    # racket
    rot = -0.5
    head = ellipse(0, 1.6, 0.9, 1.15, 60)
    strings = [[(x, 1.6 - 1.1 * math.sqrt(1 - (x / 0.9) ** 2)), (x, 1.6 + 1.1 * math.sqrt(1 - (x / 0.9) ** 2))] for x in (-0.6, -0.3, 0.0, 0.3, 0.6)]
    strings += [[(-0.88 * math.sqrt(1 - (y / 1.15) ** 2), 1.6 + y), (0.88 * math.sqrt(1 - (y / 1.15) ** 2), 1.6 + y)] for y in (-0.8, -0.4, 0.0, 0.4, 0.8)]
    shaft = [[(-0.06, 0.45), (-0.06, -1.6)], [(0.06, 0.45), (0.06, -1.6)]]
    handle = [rrect(-0.2, -3.0, 0.2, -1.6, 0.1), [(-0.2, -2.0), (0.2, -2.2)], [(-0.2, -2.4), (0.2, -2.6)]]
    racket = [transform(p, 1.6, 0.2, 0.95, rot) for p in [head] + strings + shaft + handle]
    return make("Badminton Shuttlecock and Racket", shuttle + racket)


@design("sports_ping_pong", T)
def ping_pong(rng):
    def paddle(dx, dy, rot):
        blade = circle(0, 0.8, 1.35, 70)
        rub = circle(0, 0.8, 1.15, 70)
        hdl = chain([(-0.3, -0.45)], quad((-0.3, -0.45), (-0.3, -1.2), (-0.32, -2.0), 8), arc(0, -2.0, 0.32, math.pi, 2 * math.pi, 10),
                    quad((0.32, -2.0), (0.3, -1.2), (0.3, -0.45), 8))
        seam = [[(-0.3, -0.75), (0.3, -0.75)]]
        return [transform(p, dx, dy, 1, rot) for p in [blade, rub, hdl] + seam]
    ball = [circle(-0.2, 2.6, 0.32, 30)]
    bounce = [quad((0.1, 2.75), (1.2, 3.5), (2.2, 2.6), 14)]
    return make("Ping Pong Paddles", paddle(-1.3, 0.2, 0.45) + paddle(1.3, 0.2, -0.45) + ball + bounce)


# ---------------------------------------------------------------- golf

def dimples(cx, cy, r, d=0.17, gap=0.5):
    out = []
    for i in range(-6, 7):
        for j in range(-6, 7):
            x = cx + gap * (i + 0.5 * (j % 2))
            y = cy + gap * 0.87 * j
            if math.hypot(x - cx, y - cy) < r - 0.32:
                out.append(circle(x, y, d, 12))
    return out


@design("sports_golf_tee", T)
def golf_tee(rng):
    ball = [circle(0.6, 0.7, 1.7, 90)] + dimples(0.6, 0.7, 1.7)
    tee = [poly((-0.05, -0.95), (0.4, -1.3), (0.45, -2.35), closed=False), poly((1.25, -0.95), (0.8, -1.3), (0.75, -2.35), closed=False),
           arc(0.6, -0.95, 0.65, math.pi, 2 * math.pi, 14)]
    grass = [chain([(-3.2, -2.35), (0.45, -2.35)]), [(0.75, -2.35), (3.2, -2.35)]] + \
            [poly((x - 0.15, -2.35), (x, -2.0), (x + 0.15, -2.35), closed=False) for x in (-2.6, -1.8, -0.9, 1.6, 2.5)]
    head = smooth([(-3.3, -2.25), (-1.7, -2.25), (-1.45, -1.75), (-1.7, -1.15), (-2.7, -1.05), (-3.35, -1.5)], 8, True)
    grooves = [[(-1.75, -2.05), (-1.55, -1.5)], [(-1.85, -2.05), (-1.65, -1.4)]]
    shaft = [tube([(-2.8, -1.1), (-3.2, 3.0)], 0.14, cap=False)]
    return make("Golf Ball on a Tee", ball + tee + grass + [head] + grooves + shaft)


@design("sports_golf_green", T)
def golf_green(rng):
    green = [ellipse(0, -1.6, 3.0, 1.0, 90), ellipse(0, -1.6, 3.3, 1.25, 90)]
    hole = [ellipse(0.4, -1.75, 0.38, 0.13, 24)]
    pole = [tube([(0.4, -1.75), (0.4, 2.9)], 0.13, cap=False)]
    flag = chain(wave(0.47, 2.7, 2.9, 0.12, 1, 20), [(2.7, 1.6)], wave(2.7, 0.47, 1.6, 0.12, 1, 20)[1:])
    nums = [digit(1, 1.15, 1.85, 0.3, 0.8), digit(8, 1.6, 1.85, 0.45, 0.8)]
    ball = [circle(1.5, -1.95, 0.22, 16)]
    bunker = [lens((-3.0, -0.25), (-1.4, -0.35), 0.18)]
    return make("Flagstick on the Putting Green", green + hole + pole + [flag] + nums + ball + bunker)


@design("sports_golf_bag", T)
def golf_bag(rng):
    body = chain([(-0.9, 1.2), (-0.95, -2.4)], arc(0, -2.4, 0.95, math.pi, 2 * math.pi, 16)[1:], [(0.95, -2.4), (0.9, 1.2)])
    rim = [ellipse(0, 1.2, 0.95, 0.3, 40), arc(0, 0.75, 0.93, math.pi + 0.15, 2 * math.pi - 0.15, 16)]
    pocket = [rrect(-0.6, -1.9, 0.6, -0.3, 0.2), [(-0.6, -0.65), (0.6, -0.65)], rrect(-0.15, -0.55, 0.15, -0.4, 0.05)]
    band = [arc(0, -2.0, 0.93, math.pi + 0.15, 2 * math.pi - 0.15, 16)]
    strap = [cubic((0.9, 0.6), (2.2, 0.4), (2.2, -1.6), (0.95, -1.8), 20), cubic((0.92, 0.3), (1.8, 0.2), (1.85, -1.3), (0.95, -1.5), 20)]
    legs = [[(-0.9, 0.6), (-1.8, -2.9)], [(-0.75, 0.2), (-1.4, -3.0)]]
    clubs = []
    # wood headcovers
    for x, h, rr in ((-0.5, 2.6, 0.45), (0.15, 2.9, 0.42)):
        clubs.append(chain([(x - 0.18, 1.3), (x - 0.2, h - rr * 0.6)], arc(x, h, rr, math.radians(240), math.radians(-60) + TAU, 30), [(x + 0.2, 1.3)]))
        clubs.append(circle(x, h + rr + 0.12, 0.15, 12))
    # irons
    for x, ang in ((0.55, 0.2), (0.75, -0.15)):
        top = (x + 0.6 * math.sin(ang) + 0.1, 2.3)
        clubs.append([(x, 1.3), top])
        clubs.append(poly(top, (top[0] + 0.55, top[1] + 0.1), (top[0] + 0.6, top[1] + 0.4), (top[0] - 0.05, top[1] + 0.25)))
    # putter
    clubs.append([(-0.75, 1.3), (-1.1, 3.0)])
    clubs.append(rrect(-1.75, 2.95, -0.95, 3.2, 0.08))
    return make("Golf Bag Full of Clubs", [body] + rim + pocket + band + strap + legs + clubs)


@design("sports_golfer", T)
def golfer(rng):
    fig = athlete((0.0, 1.75), [(0.0, -0.3), (0.05, 0.5), (0.05, 1.2)],
                  arms=[[(0.45, 1.0), (0.85, 1.5), (1.0, 2.35)], [(-0.35, 1.0), (0.3, 1.25), (0.95, 2.2)]],
                  legs=[[(-0.25, -0.3), (-0.6, -1.4), (-0.75, -2.6), (-0.2, -2.7)], [(0.25, -0.3), (0.25, -1.4), (-0.15, -2.4), (0.05, -2.75)]])
    cap = [chain(arc(0.0, 1.85, 0.42, 0.1, math.pi - 0.1, 14)), [(-0.42, 1.9), (-0.85, 1.8)]]
    club = clip_all([tube([(1.0, 2.35), (-2.3, 1.6)], 0.12, cap=False)], [(0.0, 1.75, 0.45)]) + [rrect(-2.75, 1.2, -2.05, 1.7, 0.15)]
    collar = [[(-0.1, 1.25), (0.2, 1.05), (0.5, 1.25)]]
    belt = [[(-0.45, -0.1), (0.45, -0.1)]]
    flight = [quad((2.0, 1.5), (2.6, 3.0), (3.1, 2.5), 12), circle(3.1, 2.5, 0.15, 12)]
    fairway = [[(-3.2, -2.75), (3.2, -2.75)], [(-3.2, -2.1), (-1.6, -2.1)], [(1.4, -2.1), (3.2, -2.1)]]
    return make("Golfer's Follow-Through", fig + cap + club + collar + belt + flight + fairway)


# ---------------------------------------------------------------- bowling & hockey

def pin(cx, cy, s, rot=0.0):
    half = smooth([(0.0, 0.0), (0.4, 0.05), (0.62, 0.7), (0.62, 1.35), (0.38, 2.05), (0.24, 2.45), (0.3, 2.85), (0.22, 3.15), (0.0, 3.25)], 6)
    outline = half + mirror_x(half)[::-1][1:]
    stripes = [[(-0.27, 2.25), (0.27, 2.25)], [(-0.25, 2.55), (0.26, 2.55)]]
    return [transform(p, cx, cy, s, rot) for p in [outline] + stripes]


@design("sports_bowling_strike", T)
def bowling_strike(rng):
    pins = pin(0.5, -2.7, 1.1, 0.0) + pin(1.8, -2.6, 1.05, -0.5) + pin(-0.9, -0.1, 0.95, 0.9)
    ball = [circle(-2.2, -1.65, 1.05, 70), circle(-2.55, -1.2, 0.2, 12), circle(-2.05, -1.05, 0.2, 12), circle(-2.25, -1.6, 0.22, 12)]
    lane = [[(-3.3, -2.7), (3.3, -2.7)]]
    motion = [[(-3.4, -0.9), (-3.0, -0.9)], [(-3.5, -1.5), (-3.1, -1.5)], [(-3.4, -2.1), (-3.0, -2.1)]]
    bursts = [[(1.2 + 0.7 * math.cos(a), 1.3 + 0.7 * math.sin(a)), (1.2 + 1.05 * math.cos(a), 1.3 + 1.05 * math.sin(a))] for a in (0.2, 0.9, 1.6, 2.3)]
    return make("Bowling Strike", pins + ball + lane + motion + bursts)


@design("sports_hockey_sticks", T)
def hockey_sticks(rng):
    def stick():
        shaft = tube([(0.0, 3.2), (0.0, -1.9)], 0.3, cap=True)
        blade = chain([(-0.15, -1.9)], quad((-0.15, -2.6), (0.2, -2.75), (1.6, -2.65), 10), quad((1.6, -2.65), (1.85, -2.6), (1.8, -2.25), 6),
                      quad((1.8, -2.25), (0.6, -2.25), (0.15, -1.9), 10))
        tape = [[(0.4, -2.3), (0.45, -2.68)], [(0.8, -2.27), (0.85, -2.68)], [(1.2, -2.26), (1.25, -2.67)]]
        grip = [[(-0.15, 2.5), (0.15, 2.5)], [(-0.15, 2.2), (0.15, 2.2)]]
        return [shaft, blade] + tape + grip
    s1 = [transform(p, -0.2, 0.2, 1, 0.42) for p in stick()]
    s2 = [transform(mirror_x(p), 0.2, 0.2, 1, -0.42) for p in stick()]
    puck = [ellipse(0, -2.3, 0.9, 0.3, 40), chain([(-0.9, -2.3), (-0.9, -2.65)], ellipse(0, -2.65, 0.9, 0.3, 40)[60:101] if False else
            [(-0.9 * math.cos(t), -2.65 - 0.3 * math.sin(t)) for t in [math.pi * i / 30 for i in range(31)]], [(0.9, -2.3)])]
    return make("Crossed Hockey Sticks and Puck", s1 + s2 + puck)


@design("sports_goalie_mask", T)
def goalie_mask(rng):
    shell = smooth([(0, 2.9), (1.4, 2.5), (2.0, 1.0), (1.9, -0.6), (1.3, -1.8), (0.5, -2.8), (-0.5, -2.8), (-1.3, -1.8), (-1.9, -0.6), (-2.0, 1.0),
                    (-1.4, 2.5)], 8, True)
    opening = smooth([(0, 0.95), (0.9, 0.8), (1.3, 0.1), (1.1, -0.9), (0.55, -1.9), (-0.55, -1.9), (-1.1, -0.9), (-1.3, 0.1), (-0.9, 0.8)], 8, True)
    cage = [[(-1.3, 0.2), (1.3, 0.2)], [(-1.15, -0.65), (1.15, -0.65)], [(-0.8, -1.4), (0.8, -1.4)],
            [(-0.45, 0.88), (-0.35, -1.9)], [(0.45, 0.88), (0.35, -1.9)]]
    stars = [star(-1.1, 1.75, 0.5, 5, 0.45), star(1.1, 1.75, 0.5, 5, 0.45)]
    vents = [rrect(-0.15, 2.2, 0.15, 2.7, 0.1)]
    straps = [[(-2.0, 1.0), (-2.9, 1.3)], [(2.0, 1.0), (2.9, 1.3)], [(-1.9, -0.6), (-2.8, -0.8)], [(1.9, -0.6), (2.8, -0.8)]]
    return make("Hockey Goalie Mask with Cage", [shell, opening] + cage + stars + vents + straps)


@design("sports_hockey_player", T)
def hockey_player(rng):
    fig = athlete((-0.2, 1.6), [(0.1, -0.3), (-0.1, 0.5), (-0.2, 1.1)], tw=1.2,
                  arms=[[(0.2, 0.95), (0.8, 0.5), (1.4, 0.3)], [(-0.5, 0.9), (0.2, 0.3), (0.9, -0.2)]],
                  legs=[[(-0.2, -0.3), (-1.0, -1.1), (-1.6, -2.1)], [(0.35, -0.3), (0.9, -1.3), (0.7, -2.3)]], feet=False)
    helmet = [chain(arc(-0.2, 1.65, 0.48, -0.2, math.pi + 0.2, 20)), [(0.25, 1.5), (0.6, 1.35)], [(0.25, 1.25), (0.6, 1.2)]]
    skates = []
    for (ax, ay), rot in (((-1.6, -2.1), 0.5), ((0.7, -2.3), 0.0)):
        boot = poly((-0.25, 0.25), (-0.3, -0.25), (0.6, -0.25), (0.55, -0.05), (0.15, 0.05), (0.15, 0.25), closed=False)
        blade = [(-0.35, -0.45), (0.65, -0.45)]
        posts = [[(-0.2, -0.25), (-0.2, -0.45)], [(0.45, -0.25), (0.45, -0.45)]]
        skates += [transform(p, ax, ay, 1, rot) for p in [boot, blade] + posts]
    stick = [tube([(1.5, 0.35), (2.4, -2.0)], 0.18, cap=True), chain([(2.33, -2.0)], quad((2.3, -2.55), (2.8, -2.6), (3.3, -2.5), 8),
                                                                       [(3.3, -2.2), (2.5, -2.15)])]
    puck = [ellipse(3.0, -2.95, 0.35, 0.12, 16)]
    nums = [digit(9, -0.4, 0.0, 0.3, 0.55), digit(9, 0.0, 0.0, 0.3, 0.55)]
    ice = [[(-3.0, -3.1), (3.3, -3.1)]]
    spray = [circle(-2.4, -2.6, 0.15, 10), circle(-2.8, -2.3, 0.12, 10), circle(-2.5, -2.1, 0.1, 10)]
    return make("Hockey Player Slapshot", fig + helmet + skates + stick + puck + nums + ice + spray)


# ---------------------------------------------------------------- boxing & gym

def glove(rot=0.0, dx=0.0, dy=0.0, s=1.0):
    fist = smooth([(-0.75, -1.2), (-0.85, -0.3), (-1.0, 0.6), (-0.8, 1.6), (0.0, 2.15), (0.85, 1.85), (1.15, 0.8), (1.0, -0.3), (0.75, -1.2)], 8)
    thumb = smooth([(-0.85, -0.25), (-1.45, 0.2), (-1.45, 0.9), (-1.0, 1.0)], 6)
    crease = [quad((-0.95, 0.65), (-0.2, 0.9), (0.4, 0.5), 8)]
    cuff = [rrect(-0.85, -2.6, 0.85, -1.2, 0.15), [(-0.85, -1.5), (0.85, -1.5)]]
    laces = [[(-0.25, -1.6), (0.25, -2.0)], [(0.25, -1.6), (-0.25, -2.0)], [(-0.25, -2.0), (0.25, -2.4)], [(0.25, -2.0), (-0.25, -2.4)]]
    return [transform(p, dx, dy, s, rot) for p in [fist, thumb] + crease + cuff + laces]


@design("sports_boxing_gloves", T)
def boxing_gloves(rng):
    g1 = glove(-0.22, 1.55, 0.3, 1.05)
    g2 = [mirror_x(p) for p in g1]
    laces = [cubic((-1.1, -2.2), (-0.6, -2.9), (-0.2, -2.6), (0.0, -2.2), 14), cubic((1.1, -2.2), (0.6, -2.9), (0.2, -2.6), (0.0, -2.2), 14),
             cubic((0.0, -2.2), (-0.3, -2.8), (-0.4, -3.1), (-0.2, -3.5), 10), cubic((0.0, -2.2), (0.3, -2.8), (0.4, -3.1), (0.25, -3.5), 10)]
    return make("Pair of Boxing Gloves", g1 + g2 + laces)


@design("sports_heavy_bag", T)
def heavy_bag(rng):
    bag = [rrect(0.6, -1.9, 2.6, 1.9, 0.5), [(0.65, 1.3), (2.55, 1.3)], [(0.65, -1.3), (2.55, -1.3)]]
    chains = [[(0.9, 1.9), (1.6, 3.1)], [(2.3, 1.9), (1.6, 3.1)], [(1.6, 3.1), (1.6, 3.6)], [(-1.0, 3.6), (3.2, 3.6)]]
    chains += [ellipse(1.25 + 0.7 * (k / 3) * 0, 2.5, 0.0, 0.0, 4) for k in range(0)]
    fig = athlete((-1.4, 1.6), [(-1.6, -0.3), (-1.55, 0.5), (-1.45, 1.1)],
                  arms=[[(-1.15, 0.9), (-0.4, 0.95), (0.3, 1.0)], [(-1.75, 0.9), (-1.55, 0.3), (-1.2, 0.85)]],
                  legs=[[(-1.8, -0.3), (-2.4, -1.4), (-2.9, -2.5), (-2.4, -2.6)], [(-1.3, -0.3), (-0.8, -1.4), (-0.75, -2.5), (-0.25, -2.6)]],
                  hands=False)
    gloves = [circle(0.32, 1.0, 0.4, 20), circle(-1.15, 0.95, 0.4, 20)]
    head_gear = [arc(-1.4, 1.6, 0.5, -0.5, math.pi + 0.5, 20)]
    trunks = [chain([(-2.1, 0.05)], [(-1.0, 0.05)]), poly((-2.15, -0.2), (-2.2, -0.8), (-1.6, -0.6), (-1.0, -0.8), (-1.0, -0.2), closed=False)]
    floor = [[(-3.3, -2.7), (3.0, -2.7)]]
    return make("Boxer at the Heavy Bag", clip_all(bag, [(0.32, 1.0, 0.4)]) + chains + fig + gloves + head_gear + trunks + floor)


def plates(x, y, side):
    out = []
    for k, (w, h) in enumerate(((0.35, 1.5), (0.3, 1.2), (0.25, 0.9))):
        x0 = x + side * sum(v for v, _ in ((0.35, 0), (0.3, 0), (0.25, 0))[:k])
        out.append(rrect(min(x0, x0 + side * w), y - h, max(x0, x0 + side * w), y + h, 0.1))
    return out


@design("sports_weightlifter", T)
def weightlifter(rng):
    half = athlete((0.0, 1.55), [(0.0, -0.4), (0.0, 0.4), (0.0, 1.1)], tw=1.25, aw=0.4, lw=0.6,
                   arms=[[(0.45, 0.95), (1.1, 1.7), (1.4, 2.6)]],
                   legs=[[(0.3, -0.45), (1.1, -1.4), (1.25, -2.6), (1.7, -2.7)]])
    left = [mirror_x(p) for p in half[2:]]
    bar = [[(-3.0, 2.68), (3.0, 2.68)], [(-3.0, 2.52), (3.0, 2.52)]]
    pl = []
    for side in (1, -1):
        for k, (x, h) in enumerate(((1.95, 1.05), (2.3, 0.85), (2.62, 0.65))):
            pl.append(rrect(side * x - 0.16, 2.6 - h, side * x + 0.16, 2.6 + h, 0.1)) if side > 0 else \
                pl.append(rrect(side * x - 0.16, 2.6 - h, side * x + 0.16, 2.6 + h, 0.1))
    belt = [rect(-0.55, -0.45, 0.55, -0.1)]
    singlet = [[(-0.35, 1.0), (0.0, 0.6), (0.35, 1.0)]]
    platform = [rect(-3.2, -3.0, 3.2, -2.75)]
    return make("Weightlifter with Barbell Overhead", clip_all(bar, [(1.4, 2.6, 0.22), (-1.4, 2.6, 0.22)]) + half + left + pl + belt + singlet + platform)


@design("sports_kettlebell", T)
def kettlebell(rng):
    bell = chain(arc(-1.2, -0.9, 1.5, math.radians(-60), math.radians(240), 70), [(-0.45, -2.2)])
    handle = [chain(arc(-1.2, 0.85, 1.0, math.radians(-15), math.radians(195), 30), arc(-1.2, 0.85, 0.65, math.radians(195), math.radians(-15), 26)[::-1][::-1][:0],
                    arc(-1.2, 0.85, 0.65, math.radians(195), math.radians(-15), 26), [(-1.2 + 1.0 * math.cos(math.radians(-15)), 0.85 + 1.0 * math.sin(math.radians(-15)))])]
    nums = [digit(1, -1.75, -1.4, 0.4, 0.9), digit(6, -1.1, -1.4, 0.45, 0.9)]
    def dumbbell(cx, cy, rot):
        parts = [rect(-1.5, -0.75, -0.65, 0.75), rect(0.65, -0.75, 1.5, 0.75), rect(-0.65, -0.15, 0.65, 0.15),
                 [(-1.5, 0.45), (-0.65, 0.45)], [(-1.5, -0.45), (-0.65, -0.45)], [(0.65, 0.45), (1.5, 0.45)], [(0.65, -0.45), (1.5, -0.45)]]
        return [transform(p, cx, cy, 1, rot) for p in parts]
    floor = [[(-3.2, -2.2), (3.3, -2.2)]]
    return make("Kettlebell and Dumbbells", [bell] + handle + nums + dumbbell(1.9, -1.45, 0.0) + dumbbell(1.9, 0.55, 0.0) + floor)


# ---------------------------------------------------------------- track & field

@design("sports_running_shoe", T)
def running_shoe(rng):
    upper = smooth([(-2.7, -0.6), (-2.75, 0.6), (-2.35, 1.35), (-1.6, 1.25), (-0.6, 1.4), (0.6, 0.9), (1.8, 0.4), (2.8, 0.05), (3.0, -0.6)], 8)
    sole = chain(smooth([(-2.8, -0.6), (-2.9, -1.2), (-2.4, -1.45), (0.0, -1.4), (2.2, -1.3), (3.05, -0.9), (3.0, -0.6)], 8))
    midline = [smooth([(-2.85, -0.85), (0.0, -0.95), (2.9, -0.75)], 10)]
    tread = [[(x, -1.42), (x + 0.15, -1.2)] for x in (-2.2, -1.6, -1.0, -0.4, 0.2, 0.8, 1.4, 2.0)]
    tab = [smooth([(-2.55, 1.3), (-2.85, 1.85), (-2.45, 1.95), (-2.25, 1.35)], 6)]
    laces = [[(-0.9 + 0.42 * k, 1.25 - 0.2 * k), (-0.6 + 0.42 * k, 1.0 - 0.2 * k)] for k in range(4)]
    eyelet = [smooth([(-1.2, 1.25), (-0.4, 1.0), (0.6, 0.55), (1.0, 0.45)], 6)]
    stripes = [smooth([(-1.9, -0.6), (-0.9, 0.3), (0.3, 0.2)], 6), smooth([(-1.3, -0.6), (-0.4, 0.05), (0.9, -0.05)], 6)]
    heel = [quad((-2.7, 0.2), (-1.9, 0.2), (-1.8, -0.6), 8)]
    toe = [quad((1.9, -0.6), (2.0, 0.0), (2.6, 0.12), 8)]
    return make("Lightweight Running Shoe", [upper, sole] + midline + tread + tab + laces + eyelet + stripes + heel + toe)


@design("sports_finish_tape", T)
def finish_tape(rng):
    fig = athlete((0.0, 2.25), [(0.0, -0.1), (0.0, 0.8), (0.0, 1.65)], tw=1.05,
                  arms=[[(0.42, 1.5), (1.15, 2.1), (1.45, 2.95)], [(-0.42, 1.5), (-1.15, 2.1), (-1.45, 2.95)]],
                  legs=[[(-0.25, -0.1), (-0.4, -1.4), (-0.45, -2.65), (-0.75, -2.8)], [(0.25, -0.1), (0.6, -1.15), (0.4, -2.1), (0.7, -2.3)]])
    bib = [rect(-0.35, 0.45, 0.35, 1.05), digit(1, -0.1, 0.55, 0.2, 0.4)]
    tape = [quad((-3.1, 0.75), (-1.6, 0.85), (-0.5, 1.15), 14), quad((-3.1, 0.55), (-1.6, 0.6), (-0.5, 0.9), 14),
            quad((0.5, 1.15), (1.6, 0.85), (3.1, 0.75), 14), quad((0.5, 0.9), (1.6, 0.6), (3.1, 0.55), 14)]
    posts = [[(-3.2, -2.8), (-3.2, 1.6)], [(-3.05, -2.8), (-3.05, 1.6)], [(3.2, -2.8), (3.2, 1.6)], [(3.05, -2.8), (3.05, 1.6)]]
    track = [[(-3.4, -2.8), (3.4, -2.8)], [(-2.2, -2.8), (-2.6, -2.2)], [(2.2, -2.8), (2.6, -2.2)]]
    cheer = [[(-2.1, 2.4), (-2.5, 2.7)], [(-2.0, 2.0), (-2.6, 2.0)], [(2.1, 2.4), (2.5, 2.7)], [(2.0, 2.0), (2.6, 2.0)]]
    return make("Runner Breaking the Finish Tape", fig + bib + tape + posts + track + cheer)


@design("sports_hurdler", T)
def hurdler(rng):
    fig = athlete((1.35, 2.35), [(0.0, 0.85), (0.5, 1.45), (0.95, 1.95)],
                  arms=[[(0.95, 1.8), (1.7, 1.55), (2.4, 1.35)], [(0.7, 1.9), (0.1, 1.5), (-0.4, 1.05)]],
                  legs=[[(0.1, 0.75), (1.2, 0.75), (2.3, 0.7), (2.55, 1.1)], [(-0.1, 0.85), (-0.55, 0.45), (-1.65, 0.75), (-2.05, 0.95)]])
    hurdle = [rrect(-0.4, -0.2, 1.8, 0.2, 0.08), [(-0.25, -0.2), (-0.25, -2.6)], [(-0.1, -0.2), (-0.1, -2.6)], [(1.5, -0.2), (1.5, -2.6)],
              [(1.65, -0.2), (1.65, -2.6)], [(-0.7, -2.6), (0.3, -2.6)], [(1.1, -2.6), (2.1, -2.6)]]
    track = [[(-3.2, -2.6), (-0.7, -2.6)], [(2.1, -2.6), (3.2, -2.6)], [(-3.2, -2.0), (-1.0, -2.0)], [(2.4, -2.0), (3.2, -2.0)]]
    return make("Hurdler Clearing a Hurdle", fig + hurdle + track)


@design("sports_relay", T)
def relay(rng):
    r1 = athlete((-1.55, 2.0), [(-1.95, 0.0), (-1.75, 0.8), (-1.6, 1.5)], tw=0.85, lw=0.45, aw=0.3,
                 arms=[[(-1.45, 1.3), (-0.75, 1.0), (-0.1, 1.0)], [(-1.85, 1.3), (-2.5, 0.85), (-2.65, 1.45)]],
                 legs=[[(-1.8, 0.0), (-1.0, -0.8), (-1.25, -1.85), (-0.8, -2.0)], [(-2.1, 0.0), (-2.55, -0.95), (-3.25, -0.7), (-3.4, -1.1)]])
    r2 = athlete((1.75, 2.0), [(1.45, 0.0), (1.6, 0.8), (1.8, 1.5)], tw=0.85, lw=0.45, aw=0.3,
                 arms=[[(1.55, 1.3), (0.95, 0.9), (0.35, 0.95)], [(2.0, 1.3), (2.6, 1.6), (2.8, 2.3)]],
                 legs=[[(1.7, 0.0), (2.45, -0.75), (2.35, -1.85), (2.8, -1.95)], [(1.3, 0.0), (0.9, -0.95), (0.2, -0.75), (0.1, -1.15)]])
    baton = [transform(rrect(-0.45, -0.12, 0.45, 0.12, 0.1), 0.15, 1.0, 1, 0.0)]
    track = [[(-3.4, -2.15), (3.4, -2.15)], [(-3.4, -2.75), (3.4, -2.75)]]
    return make("Relay Baton Handoff", r1 + r2 + baton + track)


@design("sports_javelin", T)
def javelin(rng):
    fig = athlete((1.05, 2.1), [(0.1, 0.0), (0.4, 0.85), (0.75, 1.6)],
                  arms=[[(0.45, 1.4), (-0.5, 1.35), (-1.45, 1.27)], [(0.95, 1.4), (1.5, 1.15), (2.1, 1.0)]],
                  legs=[[(0.3, -0.05), (1.2, -1.0), (1.9, -2.3), (2.35, -2.35)], [(-0.05, 0.0), (-0.75, -1.1), (-1.6, -2.2), (-1.3, -2.55)]])
    spear = [transform(lens((-2.9, 0), (2.9, 0), 0.025, 24), -0.3, 1.45, 1, 0.16)]
    shorts = [[(-0.25, 0.25), (0.55, 0.15)]]
    field = [[(-3.2, -2.55), (3.2, -2.55)], [(2.6, -2.55), (3.0, -1.9)], [(-3.2, -1.95), (-2.0, -1.95)]]
    return make("Javelin Thrower", fig + clip_all(spear, [(-1.45, 1.27, 0.21)]) + shorts + field)


# ---------------------------------------------------------------- trophies and timing

@design("sports_trophy_cup", T)
def trophy_cup(rng):
    bowl = chain([(-1.7, 2.6)], cubic((-1.7, 2.6), (-1.7, 0.6), (-0.9, -0.2), (-0.3, -0.45), 24), [(0.3, -0.45)],
                 cubic((0.3, -0.45), (0.9, -0.2), (1.7, 0.6), (1.7, 2.6), 24))
    lip = [ellipse(0, 2.6, 1.7, 0.3, 60)]
    handles = []
    for sgn in (1, -1):
        handles.append(mirror_x(smooth([(-1.6, 2.1), (-2.5, 2.2), (-2.6, 1.3), (-1.9, 0.6), (-1.35, 0.6)], 8), 0) if sgn > 0 else
                       smooth([(-1.6, 2.1), (-2.5, 2.2), (-2.6, 1.3), (-1.9, 0.6), (-1.35, 0.6)], 8))
        handles.append(mirror_x(smooth([(-1.62, 1.75), (-2.2, 1.8), (-2.25, 1.35), (-1.8, 0.9), (-1.45, 0.9)], 8), 0) if sgn > 0 else
                       smooth([(-1.62, 1.75), (-2.2, 1.8), (-2.25, 1.35), (-1.8, 0.9), (-1.45, 0.9)], 8))
    stem = [poly((-0.3, -0.45), (-0.2, -1.3), closed=False), poly((0.3, -0.45), (0.2, -1.3), closed=False),
            ellipse(0, -1.4, 0.45, 0.12, 20), poly((-0.35, -1.45), (-0.8, -2.1), (0.8, -2.1), (0.35, -1.45), closed=False)]
    base = [rect(-1.4, -2.9, 1.4, -2.1), rect(-0.9, -2.7, 0.9, -2.3)]
    st = [star(0, 1.4, 0.75, 5, 0.42)]
    return make("Championship Trophy Cup", [bowl] + lip + handles + stem + base + st)


@design("sports_gold_medal", T)
def gold_medal(rng):
    ribbon = [poly((-2.0, 3.4), (-1.0, 3.4), (0.3, 0.1), (-0.6, -0.1)), poly((2.0, 3.4), (1.0, 3.4), (-0.3, 0.1), (0.6, -0.1))]
    stripe = [[(-1.5, 3.4), (-0.15, 0.0)], [(1.5, 3.4), (0.15, 0.0)]]
    loop = [rrect(-0.35, -0.3, 0.35, 0.15, 0.12)]
    disc = [circle(0, -1.6, 1.4, 80), circle(0, -1.6, 1.1, 70)]
    st = [star(0, -1.6, 0.6, 5, 0.42)]
    laurel = []
    for k in range(5):
        a = math.radians(200 + 22 * k)
        p0 = (0.85 * math.cos(a), -1.6 + 0.85 * math.sin(a))
        p1 = (0.85 * math.cos(a + 0.35) + 0.0, -1.6 + 0.85 * math.sin(a + 0.35))
        laurel.append(lens(p0, p1, 0.3, 8))
        laurel.append(mirror_x(lens(p0, p1, 0.3, 8)))
    return make("Gold Medal on a Ribbon", clip_all(ribbon + stripe, [(0, -1.6, 1.4)]) + loop + disc + st + laurel)


@design("sports_podium", T)
def podium(rng):
    blocks = [rect(-1.0, -2.6, 1.0, 0.0), rect(-3.0, -2.6, -1.0, -0.9), rect(1.0, -2.6, 3.0, -1.6)]
    nums = [digit(1, -0.25, -1.9, 0.5, 1.2), digit(2, -2.25, -2.2, 0.5, 0.9), digit(3, 1.75, -2.3, 0.5, 0.7)]
    cup = [chain([(-0.7, 2.3)], cubic((-0.7, 2.3), (-0.7, 1.3), (-0.3, 1.0), (0.0, 1.0), 14), cubic((0.0, 1.0), (0.3, 1.0), (0.7, 1.3), (0.7, 2.3), 14), [(-0.7, 2.3)]),
           [(0.0, 1.0), (0.0, 0.5)], rect(-0.45, 0.0, 0.45, 0.45), arc(-0.75, 1.85, 0.3, math.pi / 2, 3 * math.pi / 2, 10),
           arc(0.75, 1.85, 0.3, -math.pi / 2, math.pi / 2, 10)]
    stars = [star(-2.0, 0.2, 0.5, 5, 0.45), star(2.0, -0.6, 0.45, 5, 0.45), star(-1.5, 2.6, 0.3, 5, 0.45), star(1.6, 2.4, 0.35, 5, 0.45)]
    return make("Winners' Podium", blocks + nums + cup + stars)


@design("sports_stopwatch", T)
def stopwatch(rng):
    case = [circle(0, -0.4, 2.5, 100), circle(0, -0.4, 2.15, 100)]
    crown = [rect(-0.25, 2.1, 0.25, 2.6), rrect(-0.6, 2.6, 0.6, 3.0, 0.12)]
    side = [transform(rect(-0.2, 0, 0.2, 0.45), dx=2.5 * math.cos(math.radians(45)), dy=-0.4 + 2.5 * math.sin(math.radians(45)) - 0.05, rot=-math.pi / 4)]
    ticks = []
    for k in range(12):
        a = k * TAU / 12
        L = 0.4 if k % 3 == 0 else 0.22
        ticks.append([(2.0 * math.sin(a), -0.4 + 2.0 * math.cos(a)), ((2.0 - L) * math.sin(a), -0.4 + (2.0 - L) * math.cos(a))])
    sub = [circle(0, -1.3, 0.5, 30), [(0, -1.3), (0.3, -1.0)]]
    hand = [poly((0, -0.4), (1.3, 0.9), closed=False), circle(0, -0.4, 0.15, 12)]
    motion = [arc(0, -0.4, 2.85, math.radians(110), math.radians(150), 10), arc(0, -0.4, 3.15, math.radians(115), math.radians(140), 8)]
    return make("Racing Stopwatch", case + crown + side + ticks + sub + hand + motion)


@design("sports_whistle", T)
def whistle(rng):
    body = chain(arc(-0.6, -0.6, 1.4, math.radians(90), math.radians(360), 50), [(2.9, -0.6), (2.9, 0.8), (-0.6, 0.8)])
    slot = [poly((0.3, 0.8), (0.5, 1.25), (1.1, 1.25), (1.1, 0.8), closed=False)]
    mouth = [rect(2.9, -0.35, 3.3, 0.55)]
    pea = [circle(-0.6, -0.6, 0.6, 30)]
    ring = [circle(-1.7, 0.9, 0.35, 20)]
    lanyard = [cubic((-1.85, 1.2), (-2.6, 2.6), (-1.0, 3.4), (0.4, 3.4), 24), cubic((-1.5, 1.2), (-1.9, 2.4), (-0.6, 3.0), (0.4, 3.0), 24),
               cubic((0.4, 3.4), (1.8, 3.4), (2.6, 2.9), (2.9, 2.0), 16), cubic((0.4, 3.0), (1.6, 3.0), (2.2, 2.6), (2.5, 2.0), 16)]
    return make("Coach's Whistle on a Lanyard", [body] + slot + mouth + pea + ring + lanyard)


def arrowline(pts):
    p1, p0 = pts[-1], pts[-2]
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    head = [(p1[0] + 0.28 * math.cos(a + 2.6), p1[1] + 0.28 * math.sin(a + 2.6)), p1, (p1[0] + 0.28 * math.cos(a - 2.6), p1[1] + 0.28 * math.sin(a - 2.6))]
    return [pts, head]


@design("sports_playbook", T)
def playbook(rng):
    board = [rrect(-2.4, -3.2, 2.4, 2.9, 0.25), rect(-2.05, -2.9, 2.05, 2.4)]
    clip = [rrect(-0.9, 2.3, 0.9, 3.0, 0.15), rrect(-0.4, 2.85, 0.4, 3.3, 0.15)]
    os_ = [circle(x, -1.6, 0.22, 14) for x in (-1.4, -0.7, 0.0, 0.7, 1.4)] + [circle(0, -2.3, 0.22, 14)]
    xs = []
    for x, y in ((-1.4, 0.3), (-0.5, -0.4), (0.5, -0.4), (1.4, 0.3), (0.0, 1.2)):
        xs += [[(x - 0.2, y - 0.2), (x + 0.2, y + 0.2)], [(x - 0.2, y + 0.2), (x + 0.2, y - 0.2)]]
    plays = arrowline(quad((-1.4, -1.35), (-1.6, 0.5), (-0.9, 1.6), 10)) + arrowline(quad((1.4, -1.35), (1.8, 0.0), (1.1, 1.8), 10)) + \
        arrowline([(0.0, -1.35), (0.0, -0.9), (-0.9, 0.6)])
    line = [[(-1.9, -1.15), (1.9, -1.15)]]
    return make("Coach's Playbook Clipboard", board + clip + os_ + xs + plays + line)


@design("sports_scoreboard", T)
def scoreboard(rng):
    frame = [rect(-3.2, -1.2, 3.2, 2.4), rect(-3.0, -1.0, 3.0, 2.2)]
    panels = [rect(-2.8, -0.8, -0.9, 0.9), rect(0.9, -0.8, 2.8, 0.9), rect(-0.6, 1.0, 0.6, 2.0), rect(-0.7, -0.8, 0.7, 0.4)]
    home = [digit(2, -2.6, -0.6, 0.6, 1.3), digit(1, -1.6, -0.6, 0.4, 1.3)]
    guest = [digit(1, 1.05, -0.6, 0.4, 1.3), digit(7, 1.95, -0.6, 0.6, 1.3)]
    period = [digit(4, -0.25, 1.15, 0.5, 0.7)]
    clock = [digit(3, -0.55, -0.6, 0.4, 0.75), digit(5, 0.15, -0.6, 0.4, 0.75)]
    lights = [circle(-2.4 + 0.6 * k, 2.85, 0.22, 14) for k in range(9)]
    roof = [rect(-2.8, 2.4, 2.8, 3.3)]
    posts = [rect(-2.2, -3.0, -1.8, -1.2), rect(1.8, -3.0, 2.2, -1.2), [(-3.2, -3.0), (3.2, -3.0)]]
    stars = [star(-1.85, 1.55, 0.35, 5, 0.45), star(1.85, 1.55, 0.35, 5, 0.45)]
    return make("Stadium Scoreboard", frame + panels + home + guest + period + clock + lights + roof + posts + stars)


@design("sports_stadium", T)
def stadium(rng):
    outer = [ellipse(0, -0.5, 3.3, 1.9, 120), ellipse(0, -0.5, 2.8, 1.45, 120), ellipse(0, -0.5, 2.3, 1.05, 120)]
    wall = [[(-3.3, -0.5), (-3.3, -1.5)], [(3.3, -0.5), (3.3, -1.5)], ellipse(0, -1.5, 3.3, 1.9, 120)[60:121]]
    field = [poly((-1.7, -0.95), (1.7, -0.95), (1.4, 0.05), (-1.4, 0.05)), [(0, -0.95), (0, 0.05)], ellipse(0, -0.45, 0.4, 0.2, 24)]
    arches = [[(x, -1.5 - 1.9 * math.sqrt(max(0, 1 - (x / 3.3) ** 2)) + 0.0), (x, -0.5 - 1.9 * math.sqrt(max(0, 1 - (x / 3.3) ** 2)))]
              for x in (-2.6, -1.8, -0.9, 0.0, 0.9, 1.8, 2.6)]
    towers = []
    for sx in (-2.6, 2.6):
        towers += [[(sx - 0.1, 0.6), (sx - 0.1, 2.3)], [(sx + 0.1, 0.6), (sx + 0.1, 2.3)], rect(sx - 0.55, 2.3, sx + 0.55, 3.1),
                   [(sx - 0.55, 2.7), (sx + 0.55, 2.7)], [(sx, 2.3), (sx, 3.1)]]
    flags = [poly((0, 1.4), (0, 2.3), (0.6, 2.1), (0, 1.9), closed=False)]
    return make("Floodlit Stadium", outer + wall + field + arches + towers + flags)


# ---------------------------------------------------------------- wheels

def bike(r=1.0, spokes=8, drops=True, wheelbase=3.2):
    """Side-view bicycle facing right; returns strokes and key points."""
    A, B = (-wheelbase / 2, 0.0), (wheelbase / 2, 0.0)
    BB = (-0.25, -0.1)
    S = (-0.75, 1.35)
    H, Hb = (1.05, 1.35), (1.15, 0.95)
    out = []
    for c in (A, B):
        out += [circle(c[0], c[1], r, 60), circle(c[0], c[1], r * 0.86, 56), circle(c[0], c[1], 0.12, 10)]
        for k in range(spokes):
            a = k * TAU / spokes
            out.append([(c[0] + 0.12 * math.cos(a), c[1] + 0.12 * math.sin(a)), (c[0] + 0.86 * r * math.cos(a + 0.3), c[1] + 0.86 * r * math.sin(a + 0.3))])
    out += [[A, BB, S, A], [BB, Hb, H], [S, H], [Hb, B], circle(BB[0], BB[1], 0.28, 20)]
    seat_top = (S[0] - 0.1, S[1] + 0.35)
    out += [[S, seat_top], lens((seat_top[0] - 0.45, seat_top[1] + 0.05), (seat_top[0] + 0.35, seat_top[1] + 0.02), 0.22, 10)]
    stem = (H[0] + 0.25, H[1] + 0.25)
    out.append([H, stem])
    if drops:
        out.append(chain([stem, (stem[0] + 0.35, stem[1])], arc(stem[0] + 0.35, stem[1] - 0.3, 0.3, math.pi / 2, -math.pi / 2, 10), [(stem[0] + 0.15, stem[1] - 0.6)]))
        bar = (stem[0] + 0.5, stem[1] - 0.1)
    else:
        out.append([(stem[0] - 0.3, stem[1] + 0.45), stem])
        out.append([(stem[0] - 0.55, stem[1] + 0.5), (stem[0] - 0.05, stem[1] + 0.4)])
        bar = (stem[0] - 0.3, stem[1] + 0.45)
    return out, dict(BB=BB, S=seat_top, bar=bar, A=A, B=B)


@design("sports_road_cyclist", T)
def road_cyclist(rng):
    parts, k = bike()
    BB = k["BB"]
    p1 = (BB[0] + 0.45 * math.cos(0.4), BB[1] + 0.45 * math.sin(0.4))
    p2 = (BB[0] - 0.45 * math.cos(0.4), BB[1] - 0.45 * math.sin(0.4))
    crank = [[p1, p2], rrect(p1[0] - 0.2, p1[1] - 0.06, p1[0] + 0.2, p1[1] + 0.06, 0.03)]
    hip = (k["S"][0] - 0.05, k["S"][1] + 0.3)
    fig = athlete((1.55, 2.45), [hip, (0.3, 2.3), (1.1, 2.3)], tw=0.75, aw=0.26, lw=0.42, hr=0.36,
                  arms=[[(1.05, 2.2), (1.45, 1.75), (k["bar"][0], k["bar"][1])]],
                  legs=[[hip, (0.45, 1.2), p1, (p1[0] + 0.35, p1[1] - 0.05)], [hip, (-0.1, 0.6), p2, (p2[0] + 0.35, p2[1] - 0.05)]])
    helmet = [chain(lens((1.0, 2.55), (2.05, 2.65), 0.3, 14)), [(1.75, 2.45), (2.0, 2.4)]]
    road = [[(-3.2, -1.0), (3.2, -1.0)]]
    wind = [[(-3.3, 1.6), (-2.5, 1.6)], [(-3.5, 2.1), (-2.3, 2.1)], [(-3.2, 2.6), (-2.6, 2.6)]]
    return make("Road Racing Cyclist", parts + crank + fig + helmet + road + wind)


@design("sports_bmx_jump", T)
def bmx_jump(rng):
    parts, k = bike(r=0.8, spokes=6, drops=False, wheelbase=2.6)
    BB = k["BB"]
    p1 = (BB[0] + 0.4, BB[1] + 0.05)
    p2 = (BB[0] - 0.4, BB[1] - 0.05)
    hip = (-0.6, 2.0)
    fig = athlete((0.55, 3.15), [hip, (-0.25, 2.4), (0.25, 2.8)], tw=0.8, aw=0.28, lw=0.42, hr=0.38,
                  arms=[[(0.35, 2.7), (0.7, 2.25), k["bar"]]],
                  legs=[[hip, (0.25, 1.1), p1, (p1[0] + 0.35, p1[1])], [hip, (-0.9, 0.9), p2, (p2[0] + 0.35, p2[1])]])
    helmet = [arc(0.55, 3.15, 0.48, -0.3, math.pi + 0.3, 20), [(0.9, 2.95), (1.15, 2.85)]]
    rot = 0.3
    rider = [transform(p, 0.6, 0.6, 1, rot) for p in parts + [[p1, p2]] + fig + helmet]
    ramp = [quad((-3.4, -2.6), (-2.2, -2.5), (-1.5, -1.0), 16), [(-1.5, -1.0), (-1.5, -2.6)], [(-3.4, -2.6), (3.4, -2.6)]]
    dust = [circle(-1.9, -0.5, 0.15, 10), circle(-2.3, -0.3, 0.12, 10), circle(-2.1, 0.0, 0.1, 10)]
    trail = [[(-2.4, 1.0), (-1.7, 1.3)], [(-2.6, 0.4), (-1.9, 0.7)]]
    return make("BMX Rider Catching Air", rider + ramp + dust + trail)


@design("sports_skateboard", T)
def skateboard(rng):
    deck = smooth([(-3.0, 0.0), (-2.6, 0.75), (0.0, 0.85), (2.6, 0.75), (3.0, 0.0), (2.6, -0.75), (0.0, -0.85), (-2.6, -0.75)], 10, True)
    trucks = [[(-1.9, -0.35), (-1.9, 0.35)], [(1.9, -0.35), (1.9, 0.35)], [(-2.1, -0.35), (-2.1, 0.35)], [(2.1, -0.35), (2.1, 0.35)]]
    flame = [star(0, 0, 0.6, 5, 0.45)]
    top = [transform(p, 0, 1.4, 1, 0.12) for p in [deck] + trucks + flame]
    side = [chain(quad((-3.0, -1.0), (-2.7, -1.6), (-2.2, -1.65), 8), [(2.2, -1.65)], quad((2.2, -1.65), (2.7, -1.6), (3.0, -1.0), 8)),
            chain(quad((-3.0, -1.15), (-2.65, -1.85), (-2.2, -1.85), 8), [(2.2, -1.85)], quad((2.2, -1.85), (2.65, -1.85), (3.0, -1.15), 8)),
            [(-3.0, -1.0), (-3.0, -1.15)], [(3.0, -1.0), (3.0, -1.15)]]
    for x in (-1.9, 1.9):
        side += [poly((x - 0.35, -1.85), (x - 0.2, -2.15), (x + 0.2, -2.15), (x + 0.35, -1.85), closed=False),
                 circle(x - 0.35, -2.45, 0.35, 24), circle(x + 0.35, -2.45, 0.35, 24), circle(x - 0.35, -2.45, 0.13, 10), circle(x + 0.35, -2.45, 0.13, 10)]
    return make("Skateboard Deck and Wheels", top + side)


@design("sports_skater_ollie", T)
def skater_ollie(rng):
    fig = athlete((0.3, 2.3), [(0.0, 0.6), (0.15, 1.3), (0.25, 1.85)],
                  arms=[[(0.5, 1.7), (1.3, 1.9), (2.0, 2.4)], [(0.0, 1.7), (-0.8, 1.6), (-1.5, 2.1)]],
                  legs=[[(0.2, 0.55), (1.0, 0.3), (0.85, -0.5), (1.25, -0.4)], [(-0.2, 0.55), (-0.6, -0.15), (-0.9, -0.6), (-0.55, -0.85)]])
    cap = [chain(arc(0.3, 2.35, 0.42, 0.0, math.pi, 14)), [(-0.12, 2.35), (-0.55, 2.3)]]
    rot = 0.3
    deck = chain(quad((-1.6, 0.2), (-1.45, -0.05), (-1.2, -0.05), 6), [(1.2, -0.05)], quad((1.2, -0.05), (1.45, -0.05), (1.6, 0.25), 6),
                 [(1.6, 0.25), (1.55, 0.38)], quad((1.55, 0.38), (1.4, 0.13), (1.2, 0.13), 6), [(-1.2, 0.13)], quad((-1.2, 0.13), (-1.45, 0.13), (-1.6, 0.2), 6))
    wheels = [circle(-0.9, -0.3, 0.2, 14), circle(0.9, -0.3, 0.2, 14), [(-1.05, -0.05), (-0.9, -0.2), (-0.75, -0.05)], [(0.75, -0.05), (0.9, -0.2), (1.05, -0.05)]]
    board = [transform(p, 0.05, -1.0, 1, rot) for p in [deck] + wheels]
    ground = [[(-3.2, -2.7), (3.2, -2.7)]]
    pop = [arc(-1.5, -2.2, 0.4, math.pi / 2, math.pi, 6), arc(-1.5, -2.2, 0.75, math.pi / 2 + 0.2, math.pi - 0.2, 6), [(-1.6, -2.5), (-2.1, -2.6)]]
    shadow = [ellipse(0.0, -2.7, 1.3, 0.12, 30)]
    return make("Skateboarder Doing an Ollie", fig + cap + board + ground + shadow + pop)


@design("sports_roller_skate", T)
def roller_skate(rng):
    boot = smooth([(-1.7, -0.6), (-1.85, 0.8), (-1.6, 2.6), (-0.4, 2.7), (-0.35, 1.6), (0.3, 0.6), (1.4, 0.2), (2.2, -0.05), (2.3, -0.6)], 8)
    sole = [rrect(-1.9, -0.95, 2.4, -0.6, 0.12)]
    heel = [rect(-1.8, -1.25, -0.9, -0.95)]
    plate = [rect(-1.4, -1.35, 1.9, -1.2)]
    wheels = []
    for x in (-1.05, 1.5):
        wheels += [circle(x, -1.95, 0.6, 36), circle(x, -1.95, 0.25, 18)]
    stop = [poly((2.2, -0.95), (2.5, -1.4), (2.95, -1.3), (2.75, -0.85), closed=False)]
    laces = [[(-0.75 + 0.27 * k, 2.15 - 0.42 * k), (-0.3 + 0.27 * k, 1.95 - 0.42 * k)] for k in range(4)]
    cuff = [[(-1.8, 2.2), (-0.38, 2.25)]]
    stripe = [smooth([(-1.75, 0.3), (-0.6, 0.3), (0.3, -0.25)], 8), smooth([(-1.7, 0.05), (-0.6, 0.05), (0.0, -0.3)], 8)]
    return make("Retro Roller Skate", [boot] + sole + heel + plate + wheels + stop + laces + cuff + stripe)


# ---------------------------------------------------------------- water

@design("sports_swimmer", T)
def swimmer(rng):
    torso = limb([(-1.2, -0.35), (0.0, -0.2), (1.0, 0.05)], 0.75, 0.95)
    head = [circle(1.6, 0.15, 0.42, 30), arc(1.6, 0.15, 0.48, -0.3, math.pi * 0.85, 16), ellipse(1.75, 0.2, 0.2, 0.12, 14)]
    reach = limb([(1.1, -0.1), (2.2, -0.15), (3.0, -0.35)], 0.3, 0.24, cap=False)
    recover = limb([(0.6, 0.3), (0.1, 1.3), (1.05, 1.75)], 0.3, 0.24, cap=False)
    hands = [circle(3.05, -0.38, 0.17, 12), circle(1.15, 1.8, 0.17, 12)]
    legs = [limb([(-1.2, -0.25), (-2.2, 0.0), (-3.0, 0.3)], 0.4, 0.26, cap=False), limb([(-1.2, -0.5), (-2.2, -0.7), (-3.0, -0.95)], 0.4, 0.26, cap=False)]
    feet = [lens((-3.0, 0.3), (-3.5, 0.45), 0.4, 8), lens((-3.0, -0.95), (-3.5, -1.1), 0.4, 8)]
    water = [wave(-3.6, -2.5, -0.2, 0.08, 1, 20), wave(-0.5, 0.4, 0.45, 0.08, 1, 16), wave(2.2, 3.6, 0.25, 0.08, 1.5, 24),
             wave(-3.4, 3.4, -1.6, 0.1, 4, 80)]
    splash = [circle(-3.2, 0.9, 0.15, 10), circle(-2.8, 1.2, 0.12, 10), circle(-3.5, -0.35, 0.12, 10), circle(2.0, 2.0, 0.13, 10), circle(1.6, 2.3, 0.1, 10)]
    rope = [ellipse(-3.0 + 0.75 * k, -2.5, 0.32, 0.22, 20) for k in range(9)]
    return make("Freestyle Swimmer", [torso, reach, recover] + head + hands + legs + feet + water + splash + rope)


@design("sports_diver", T)
def diver(rng):
    fig = athlete((0.0, 1.6), [(0.0, -0.4), (0.0, 0.4), (0.0, 1.1)],
                  arms=[[(0.3, 1.0), (0.3, 2.2), (0.08, 3.25)], [(-0.3, 1.0), (-0.3, 2.2), (-0.08, 3.25)]],
                  legs=[[(0.18, -0.4), (0.17, -1.6), (0.12, -2.7), (0.08, -3.2)], [(-0.18, -0.4), (-0.17, -1.6), (-0.12, -2.7), (-0.08, -3.2)]])
    body = [transform(p, 0.55, 0.55, 0.75, math.pi + 0.5) for p in fig]
    board = [rrect(-3.4, 2.75, -1.2, 2.95, 0.08), poly((-3.4, 2.75), (-3.0, 2.2), (-2.6, 2.2), (-2.6, 2.75), closed=False),
             [(-3.0, 2.2), (-3.0, -1.6)], [(-2.6, 2.2), (-2.6, -1.6)]]
    pool = [wave(-3.4, 3.4, -1.6, 0.08, 4, 80), [(-3.4, -2.9), (3.4, -2.9)], [(-3.4, -1.6), (-3.4, -2.9)], [(3.4, -1.6), (3.4, -2.9)]]
    tiles = [[(x, -2.9), (x, -2.4)] for x in (-2.4, -1.2, 0.0, 1.2, 2.4)]
    splash = [arc(1.75, -1.6, 0.5, 0.3, math.pi - 0.3, 10), arc(1.75, -1.6, 0.9, 0.5, math.pi - 0.5, 12)]
    return make("Diver Plunging Into the Pool", body + board + pool + tiles + splash)


# ---------------------------------------------------------------- target sports

def stuck_arrow(tip, ang, L, dart=False):
    """Arrow (or dart) stuck in a target, tail pointing along angle `ang`."""
    if dart:
        parts = [[(0, 0), (0.35, 0)], rrect(0.35, -0.13, 1.15, 0.13, 0.1), [(1.15, 0), (1.45, 0)],
                 poly((1.35, 0), (1.7, 0.4), (2.1, 0.4), (1.95, 0)), poly((1.35, 0), (1.7, -0.4), (2.1, -0.4), (1.95, 0))]
    else:
        parts = [[(0, 0), (L, 0)], poly((L - 0.65, 0), (L - 0.45, 0.28), (L + 0.05, 0.28), (L, 0)),
                 poly((L - 0.65, 0), (L - 0.45, -0.28), (L + 0.05, -0.28), (L, 0))]
    return [transform(p, tip[0], tip[1], 1, ang) for p in parts]


@design("sports_archery_target", T)
def archery_target(rng):
    cx, cy = -0.3, 0.6
    rings = [circle(cx, cy, r, 90) for r in (2.4, 1.95, 1.5, 1.05, 0.6, 0.25)]
    legs = [[(cx - 1.2, cy - 2.1), (cx - 1.9, -3.0)], [(cx + 1.2, cy - 2.1), (cx + 1.9, -3.0)], [(cx, cy - 2.4), (cx + 0.3, -3.0)]]
    arrows, holes = [], []
    for hx, hy in ((cx + 0.1, cy + 0.15), (cx - 0.75, cy + 0.85), (cx + 0.6, cy - 0.7)):
        arrows += stuck_arrow((hx, hy), -0.35, 2.2)
        holes += [(hx + t * math.cos(-0.35), hy + t * math.sin(-0.35), 0.3) for t in (1.6, 1.85, 2.1)]
    rings = clip_all(rings, holes)
    return make("Archery Target with Arrows", rings + legs + arrows)


@design("sports_archer", T)
def archer(rng):
    fig = athlete((-0.3, 2.1), [(-0.6, -0.1), (-0.5, 0.8), (-0.4, 1.55)],
                  arms=[[(-0.1, 1.4), (0.8, 1.5), (1.75, 1.5)], [(-0.7, 1.4), (-0.15, 1.6), (-0.05, 1.85)]],
                  legs=[[(-0.4, -0.1), (0.2, -1.3), (0.4, -2.6), (0.85, -2.7)], [(-0.75, -0.1), (-1.2, -1.3), (-1.55, -2.55), (-1.1, -2.7)]])
    bow = [chain(quad((1.35, 3.5), (2.4, 2.6), (1.8, 1.5), 16), quad((1.8, 1.5), (2.4, 0.4), (1.35, -0.5), 16))]
    string = [[(1.35, 3.5), (-0.05, 1.85), (1.35, -0.5)]]
    arrow = [[(-0.05, 1.85), (3.0, 1.85)], poly((3.0, 2.0), (3.35, 1.85), (3.0, 1.7)), lens((-0.05, 1.85), (0.6, 1.85), 0.25, 8)]
    ground_ = [[(-2.4, -2.75), (2.8, -2.75)]]
    return make("Archer Drawing a Bow", fig + bow + string + arrow + ground_)


@design("sports_dartboard", T)
def dartboard(rng):
    rings = [circle(0, 0.2, r, 100) for r in (3.0, 2.45, 2.15, 1.5, 1.25, 0.42)] + [circle(0, 0.2, 0.18, 14)]
    seg = []
    for k in range(20):
        a = math.pi / 2 + math.pi / 20 + k * TAU / 20
        seg.append([(0.42 * math.cos(a), 0.2 + 0.42 * math.sin(a)), (2.45 * math.cos(a), 0.2 + 2.45 * math.sin(a))])
    darts, holes = [], []
    for (x, y), a in (((0.6, 1.2), -0.5), ((-0.9, -0.5), -0.75), ((0.15, 0.25), -0.3)):
        darts += stuck_arrow((x, y), a, 0, dart=True)
        holes += [(x + t * math.cos(a), y + t * math.sin(a), 0.2 if t < 1.4 else 0.45) for t in (0.4, 0.7, 1.0, 1.3, 1.65, 1.95)]
    return make("Dartboard with Three Darts", clip_all(rings + seg, holes) + darts)


@design("sports_pool_table", T)
def pool_table(rng):
    rail = [rrect(-3.3, -1.95, 3.3, 1.95, 0.35), rect(-2.9, -1.55, 2.9, 1.55)]
    pockets = [circle(x, y, 0.28, 18) for x in (-2.9, 0.0, 2.9) for y in (-1.55, 1.55)]
    balls = []
    r = 0.22
    for row in range(5):
        for j in range(row + 1):
            balls.append(circle(1.0 + row * 0.39, (j - row / 2) * 0.46, r, 16))
    cue_ball = [circle(-1.4, 0.0, r, 16)]
    cue = [tube([(-1.75, -0.12), (-4.2, -1.2)], lambda t: 0.08 + 0.14 * t, cap=True)]
    return make("Pool Table with Racked Balls", rail + pockets + balls + cue_ball + clip_all(cue, [(-2.9, -1.55, 0.0)]))


# ---------------------------------------------------------------- combat & gymnastics

def fencer():
    """Fencer lunging to the right (left of centre)."""
    fig = athlete((-1.55, 1.55), [(-1.9, -0.1), (-1.75, 0.55), (-1.6, 1.15)], tw=0.85, aw=0.28, lw=0.45,
                  arms=[[(-1.35, 1.0), (-0.75, 1.1), (-0.15, 1.25)], [(-1.85, 1.0), (-2.45, 1.2), (-2.55, 1.9)]],
                  legs=[[(-1.7, -0.1), (-0.85, -0.8), (-0.85, -2.1), (-0.35, -2.2)], [(-2.1, -0.1), (-2.8, -1.2), (-3.4, -2.05), (-3.05, -2.25)]])
    mask = [rrect(-1.95, 1.15, -1.15, 1.95, 0.3), [(-1.15, 1.55), (-1.95, 1.55)], [(-1.55, 1.15), (-1.55, 1.95)], rect(-1.95, 0.85, -1.3, 1.15)]
    guard = [arc(-0.05, 1.27, 0.3, -math.pi / 2, math.pi / 2, 10), [(-0.05, 0.97), (-0.05, 1.57)]]
    return fig + mask + guard


@design("sports_fencing", T)
def fencing(rng):
    left = [transform(p, -0.4, 0) for p in fencer()] + [[(-0.15, 1.27), (1.25, 1.8)]]
    right = [transform(mirror_x(p), 0.4, 0) for p in fencer()] + [[(0.15, 1.27), (-1.25, 1.65)]]
    piste = [[(-3.5, -2.25), (3.5, -2.25)], [(-3.5, -2.7), (3.5, -2.7)], [(0, -2.25), (0, -2.7)]]
    return make("Fencing Duel", clip_all(left + right, [(0.0, 1.27, 0.0)]) + piste)


@design("sports_still_rings", T)
def still_rings(rng):
    half = athlete((0.0, 1.55), [(0.0, -0.6), (0.0, 0.3), (0.0, 1.05)], tw=1.15, aw=0.4, lw=0.5,
                   arms=[[(0.5, 0.95), (1.3, 0.97), (2.05, 1.0)]],
                   legs=[[(0.2, -0.6), (0.16, -1.8), (0.1, -2.9), (0.15, -3.3)]])
    right = half[2:]
    left = [mirror_x(p) for p in right]
    straps = [[(2.05, 1.3), (2.6, 3.4)], [(-2.05, 1.3), (-2.6, 3.4)], [(-3.2, 3.4), (3.2, 3.4)]]
    rings = clip_all([circle(2.05, 1.0, 0.36, 24), circle(-2.05, 1.0, 0.36, 24)], [(2.05, 1.0, 0.22), (-2.05, 1.0, 0.22)]) + \
        [arc(2.05, 1.0, 0.36, -0.6, 0.6, 6), arc(-2.05, 1.0, 0.36, math.pi - 0.6, math.pi + 0.6, 6)]
    leotard = [[(-0.42, -0.4), (0.0, -0.95), (0.42, -0.4)]]
    return make("Gymnast on the Still Rings", half[:2] + right + left + straps + rings + leotard)


@design("sports_balance_beam", T)
def balance_beam(rng):
    fig = athlete((0.15, 2.4), [(0.0, 0.5), (0.05, 1.25), (0.1, 1.9)], tw=0.85, aw=0.28, lw=0.42,
                  arms=[[(0.35, 1.75), (1.0, 2.3), (1.55, 2.95)], [(-0.2, 1.75), (-0.9, 2.25), (-1.45, 2.85)]],
                  legs=[[(0.2, 0.5), (1.4, 0.75), (2.6, 0.95), (3.05, 1.0)], [(-0.2, 0.5), (-1.4, 0.65), (-2.6, 0.75), (-3.05, 0.6)]])
    bun = [circle(0.0, 2.95, 0.2, 14)]
    leotard = [[(-0.38, 0.85), (0.0, 0.35), (0.38, 0.85)]]
    beam = [rrect(-3.3, -0.85, 3.3, -0.45, 0.12)]
    stands = []
    for x in (-2.3, 2.3):
        stands += [[(x - 0.12, -0.85), (x - 0.12, -2.6)], [(x + 0.12, -0.85), (x + 0.12, -2.6)], rrect(x - 0.7, -2.8, x + 0.7, -2.6, 0.08)]
    return make("Balance Beam Split Leap", fig + bun + leotard + beam + stands)


@design("sports_karate", T)
def karate(rng):
    fig = athlete((-1.1, 2.25), [(-0.75, 0.2), (-0.95, 1.0), (-1.05, 1.65)], tw=1.15, aw=0.42, lw=0.6,
                  arms=[[(-0.7, 1.5), (-0.2, 1.05), (0.25, 1.55)], [(-1.4, 1.5), (-1.95, 0.95), (-1.45, 0.6)]],
                  legs=[[(-0.95, 0.15), (-1.2, -1.1), (-1.25, -2.55), (-0.7, -2.65)], [(-0.5, 0.2), (0.8, 0.5), (2.1, 0.8), (2.55, 1.15)]])
    gi = [[(-1.45, 1.6), (-0.95, 0.95), (-0.6, 1.6)], [(-1.25, 1.65), (-1.05, 1.3)]]
    belt = [rect(-1.35, 0.25, -0.2, 0.55), poly((-0.75, 0.3), (-0.55, -0.4), (-0.4, -0.35), (-0.6, 0.3), closed=False),
            poly((-0.75, 0.3), (-1.0, -0.35), (-0.85, -0.42), (-0.62, 0.28), closed=False)]
    band = [[(-1.45, 2.4), (-0.75, 2.4)], [(-1.45, 2.3), (-1.95, 2.0)], [(-1.45, 2.3), (-1.9, 2.45)]]
    floor = [[(-3.0, -2.7), (2.8, -2.7)]]
    impact = [[(2.85 + 0.5 * math.cos(a), 1.3 + 0.5 * math.sin(a)), (2.85 + 0.85 * math.cos(a), 1.3 + 0.85 * math.sin(a))] for a in (-0.6, 0.2, 1.0)]
    return make("Karate Side Kick", fig + gi + belt + band + floor + impact)


@design("sports_climbing_wall", T)
def climbing_wall(rng):
    wall = [rect(-3.0, -3.0, 3.0, 3.4)]
    panels = [[(-1.0, -3.0), (-1.0, 3.4)], [(1.0, -3.0), (1.0, 3.4)], [(-3.0, 0.2), (3.0, 0.2)]]
    fig = athlete((0.1, 1.15), [(0.2, -0.85), (0.15, 0.0), (0.1, 0.7)], tw=1.0, aw=0.32, lw=0.48, feet=False,
                  arms=[[(0.5, 0.6), (1.0, 1.5), (1.25, 2.4)], [(-0.3, 0.6), (-0.9, 0.9), (-1.35, 1.6)]],
                  legs=[[(0.4, -0.85), (1.3, -1.3), (1.25, -2.3), (1.6, -2.4)], [(0.0, -0.85), (-0.85, -0.85), (-1.3, -1.8), (-1.5, -2.0)]])
    shoes = [lens((1.05, -2.35), (1.65, -2.4), 0.35, 10), lens((-1.15, -1.85), (-1.7, -2.05), 0.35, 10)]
    harness = [[(-0.3, -0.55), (0.65, -0.55)], [(-0.3, -0.75), (0.65, -0.75)], circle(0.2, -0.95, 0.15, 12)]
    rope = [[(0.2, -1.1), (0.25, -1.6)], quad((0.2, -1.1), (2.4, -0.2), (2.2, 3.4), 20)]
    helmet = [arc(0.1, 1.15, 0.48, 0.0, math.pi, 16)]
    holds = []
    for x, y, r in ((1.3, 2.55, 0.32), (-1.45, 1.75, 0.3), (1.55, -2.55, 0.3), (-1.65, -2.15, 0.28), (-2.2, 2.6, 0.35), (2.2, 1.2, 0.3),
                    (-2.3, -0.3, 0.32), (2.4, -1.4, 0.28), (-0.2, 2.9, 0.3), (-0.4, -2.6, 0.3), (2.5, 2.9, 0.25)):
        pts = [(x + r * (1 + 0.25 * math.sin(3 * t + x)) * math.cos(t), y + r * 0.8 * (1 + 0.25 * math.sin(3 * t + x)) * math.sin(t)) for t in [TAU * i / 30 for i in range(31)]]
        holds.append(pts)
    return make("Rock Climber on the Wall", clip_all(wall + panels, [(0.15, 0.0, 0.0)]) + fig + shoes + harness + rope + helmet + holds)


# ---------------------------------------------------------------- bat & stick sports

@design("sports_cricket", T)
def cricket(rng):
    stumps = []
    for x in (0.9, 1.5, 2.1):
        stumps.append(rrect(x - 0.12, -2.8, x + 0.12, 0.8, 0.06))
    bails = [rrect(0.85, 0.82, 1.55, 0.98, 0.07), rrect(1.45, 0.82, 2.15, 0.98, 0.07)]
    bat = [rrect(-0.55, -1.8, 0.55, 1.6, 0.25), [(-0.15, 1.6), (-0.15, 3.3)], [(0.15, 1.6), (0.15, 3.3)], rrect(-0.2, 2.2, 0.2, 3.5, 0.1),
           quad((-0.3, 1.4), (0.0, -0.2), (-0.3, -1.6), 12)]
    bat = [transform(p, -1.3, -0.4, 1, 0.3) for p in bat]
    grip = [transform([(-0.2, 2.5 + 0.3 * k), (0.2, 2.6 + 0.3 * k)], -1.3, -0.4, 1, 0.3) for k in range(3)]
    ball = [circle(0.0, -2.3, 0.5, 30), transform([(-0.5, 0.0), (0.5, 0.0)], 0.0, -2.3, 1, 0.5),
            transform([(-0.45, 0.12), (0.45, 0.12)], 0.0, -2.3, 1, 0.5)]
    ground_ = [[(-3.2, -2.8), (3.2, -2.8)]]
    return make("Cricket Bat, Ball and Wickets", stumps + bails + bat + grip + ball + ground_)


@design("sports_rugby_ball", T)
def rugby_ball(rng):
    rot = -0.35
    ball = ellipse(0, 0, 1.45, 2.4, 90)
    seams = [[(0.55 * math.cos(t), 2.4 * math.sin(t)) for t in [-math.pi / 2 + math.pi * i / 40 for i in range(41)]],
             [(-0.55 * math.cos(t), 2.4 * math.sin(t)) for t in [-math.pi / 2 + math.pi * i / 40 for i in range(41)]]]
    stitch = [[(0.45, y), (0.68, y)] for y in (-0.6, -0.2, 0.2, 0.6)]
    parts = [transform(p, 0, 0.6, 1, rot) for p in [ball] + seams + stitch]
    tee = [chain([(-1.3, -2.35)], quad((-1.3, -2.35), (-0.6, -2.15), (-0.5, -1.35), 8), [(0.5, -1.35)], quad((0.5, -1.35), (0.6, -2.15), (1.3, -2.35), 8), [(-1.3, -2.35)])]
    posts = [[(-3.0, -2.6), (-3.0, 3.0)], [(3.0, -2.6), (3.0, 3.0)], [(-3.0, 0.6), (3.0, 0.6)]]
    field = [[(-3.4, -2.6), (3.4, -2.6)]]
    return make("Rugby Ball on a Kicking Tee", clip_all(posts, [(0, 0.6, 2.45)]) + parts + tee + field)


@design("sports_lacrosse", T)
def lacrosse(rng):
    def stick(dx, rot):
        head = smooth([(0.0, 1.1), (-0.55, 1.6), (-0.95, 2.6), (-0.85, 3.4), (0.0, 3.6), (0.85, 3.4), (0.95, 2.6), (0.55, 1.6), (0.0, 1.1)], 8)
        mesh = []
        for k in range(1, 4):
            y = 1.3 + 0.55 * k
            mesh.append([(-0.85 + 0.12 * (3 - k) * 0, y - 0.05), (0.85, y + 0.05)])
        mesh = [[(-0.5, 1.6), (0.75, 3.35)], [(-0.85, 2.3), (0.4, 3.55)], [(0.5, 1.6), (-0.75, 3.35)], [(0.85, 2.3), (-0.4, 3.55)],
                [(-0.7, 2.0), (0.7, 2.0)], [(-0.93, 2.75), (0.93, 2.75)]]
        shaft = [tube([(0.0, 1.1), (0.0, -3.0)], 0.22, cap=True), [(-0.11, -2.4), (0.11, -2.4)], [(-0.11, -2.7), (0.11, -2.7)]]
        return [transform(p, dx, 0.0, 1, rot) for p in [head] + mesh + shaft]
    ball = [circle(0.0, -2.1, 0.4, 24)]
    return make("Crossed Lacrosse Sticks", stick(-0.4, 0.45) + stick(0.4, -0.45) + ball)
