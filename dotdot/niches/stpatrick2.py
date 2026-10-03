"""St. Patrick's Day niche, part 2 (pictures 10-55)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "stpatrick"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ------------------------------------------------------------ helpers

def smooth(pts, k=8, closed=False):
    """Catmull-Rom spline through the given points."""
    P = list(pts)
    if closed:
        if math.dist(P[0], P[-1]) < 1e-9:
            P = P[:-1]
        P = [P[-1]] + P + [P[0], P[1]]
    else:
        P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(k):
            t = j / k
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[d] + (-p0[d] + p2[d]) * t + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * t2
                                    + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * t3) for d in (0, 1)))
    out.append(P[-2])
    return out


def densify(pts, step=0.03):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        k = max(1, int(math.dist(a, b) / step))
        for i in range(1, k + 1):
            out.append((a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k))
    return out


def inside(shape):
    pts = list(shape)

    def f(x, y):
        c = False
        for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
            if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
                c = not c
        return c
    return f


def hide(strokes, *fronts):
    """Drop the parts of `strokes` covered by any of the closed `fronts`."""
    tests = [inside(f) for f in fronts]
    out = []
    for s in strokes:
        cur = []
        for p in densify(s):
            if any(t(*p) for t in tests):
                if len(cur) > 1:
                    out.append(cur)
                cur = []
            else:
                cur.append(p)
        if len(cur) > 1:
            out.append(cur)
    return out


def bumpy(pts, amp, bumps):
    """Push a line outwards (to its right) in a row of round bumps."""
    pts = densify(pts, 0.02)
    n = len(pts)
    out = []
    for i, (x, y) in enumerate(pts):
        a, b = pts[max(0, i - 1)], pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        d = amp * abs(math.sin(math.pi * bumps * i / (n - 1)))
        out.append((x + dy / L * d, y - dx / L * d))
    return out


def union(shapes):
    """Outline of overlapping closed shapes: each one minus the others' insides."""
    out = []
    for i, sh in enumerate(shapes):
        out += hide([sh], *[o for j, o in enumerate(shapes) if j != i])
    return out


def leaf(cx, cy, s, a):
    """Heart-shaped clover leaflet with its tip at (cx, cy), pointing to angle a."""
    return transform(heart(0, 1.0625 * s, s, 60), dx=cx, dy=cy, rot=a - math.pi / 2)


def shamrock(cx, cy, s, rot=0.0, leaves=3, stem=1.0, veins=False):
    out = []
    for k in range(leaves):
        a = rot + math.pi / 2 + (k * TAU / leaves if leaves == 3 else math.pi / 4 + k * math.pi / 2)
        out.append(leaf(cx, cy, s, a))
        if veins:
            out.append([(cx, cy), (cx + 1.1 * s * math.cos(a), cy + 1.1 * s * math.sin(a))])
    if stem:
        a = rot - math.pi / 2
        L = 2.0 * s * stem
        ex, ey = cx + L * math.cos(a) + 0.4 * s * math.cos(a + 1.2), cy + L * math.sin(a) + 0.4 * s * math.sin(a + 1.2)
        out.append(quad((cx, cy), (cx + 0.6 * L * math.cos(a), cy + 0.6 * L * math.sin(a)), (ex, ey), 16))
    return out


def coin(cx, cy, r, tilt=1.0, mark=True):
    out = [ellipse(cx, cy, r, r * tilt, 40)]
    if mark and r * tilt > 0.25:
        out.append(ellipse(cx, cy, r * 0.72, r * tilt * 0.72, 32))
    return out


def cloud(cx, cy, s):
    return chain(arc(cx - 0.8 * s, cy + 0.25 * s, 0.45 * s, math.radians(210), math.radians(80), 16),
                 arc(cx, cy + 0.5 * s, 0.6 * s, math.radians(160), math.radians(20), 20),
                 arc(cx + 0.8 * s, cy + 0.25 * s, 0.45 * s, math.radians(100), math.radians(-30), 16),
                 [(cx - 1.19 * s, cy + 0.025 * s)])


def sparkle(x, y, r):
    return star(x, y, r, 4, 0.3)


def boot(cx, cy, s, flip=False):
    """Leprechaun buckle shoe, toe pointing right; (cx, cy) is the heel bottom."""
    sole = chain([(0, 0.55), (0, 0.0), (1.35, 0.0)], quad((1.35, 0.0), (1.75, 0.05), (1.6, 0.35), 8),
                 quad((1.6, 0.35), (1.2, 0.5), (0.65, 0.6), 8), [(0, 0.55)])
    buckle = rect(0.55, 0.2, 0.85, 0.5)
    parts = [sole, buckle]
    if flip:
        parts = [mirror_x(p) for p in parts]
    return [transform(p, dx=cx, dy=cy, s=s) for p in parts]


# ------------------------------------------------------------ people & folklore

@design("stpatrick_leprechaun", T)
def leprechaun(rng):
    hat = [poly((-0.75, 2.14), (-0.6, 3.0), (0.6, 3.0), (0.75, 2.14), closed=False), ellipse(0, 1.95, 1.45, 0.22, 60),
           [(-0.71, 2.35), (-0.2, 2.35)], [(0.2, 2.35), (0.71, 2.35)], [(-0.68, 2.6), (-0.2, 2.6)], [(0.2, 2.6), (0.68, 2.6)],
           rect(-0.2, 2.28, 0.2, 2.67)]
    head = [[(-0.55, 1.75), (-0.55, 1.42)], [(0.55, 1.75), (0.55, 1.42)],
            arc(-0.55, 1.6, 0.14, math.pi / 2, 1.5 * math.pi, 10), arc(0.55, 1.6, 0.14, math.pi / 2, -math.pi / 2, 10)]
    beard_base = chain(cubic((-0.55, 1.42), (-0.85, 0.6), (-0.35, 0.3), (0, 0.25), 30), cubic((0, 0.25), (0.35, 0.3), (0.85, 0.6), (0.55, 1.42), 30))
    beard = bumpy(beard_base, 0.12, 9)
    face = [circle(0, 1.38, 0.12, 16), chain(cubic((0, 1.2), (-0.15, 1.3), (-0.4, 1.3), (-0.5, 1.2), 10), cubic((-0.5, 1.2), (-0.35, 1.05), (-0.1, 1.05), (0, 1.2), 10)),
            chain(cubic((0, 1.2), (0.15, 1.3), (0.4, 1.3), (0.5, 1.2), 10), cubic((0.5, 1.2), (0.35, 1.05), (0.1, 1.05), (0, 1.2), 10)),
            arc(0, 1.0, 0.18, math.radians(200), math.radians(340), 10)]
    coat = poly((-0.45, 0.6), (-0.95, 0.35), (-1.05, -1.3), (1.05, -1.3), (0.95, 0.35), (0.45, 0.6), closed=False)
    belt = [[(-1.0, -0.3), (-0.25, -0.3)], [(0.25, -0.3), (1.0, -0.3)], [(-1.01, -0.6), (-0.25, -0.6)], [(0.25, -0.6), (1.01, -0.6)],
            rect(-0.25, -0.68, 0.25, -0.22), rect(-0.1, -0.53, 0.1, -0.37)]
    buttons = [circle(0, 0.0, 0.07, 10), circle(0, -0.95, 0.07, 10)]
    arm_l = tube([(-0.95, 0.25), (-1.45, -0.3), (-1.4, -0.9)], 0.4, cap=False)
    arm_r = tube([(0.95, 0.25), (1.5, 0.75), (1.7, 1.35)], 0.4, cap=False)
    hands = [circle(-1.4, -1.1, 0.22, 18), circle(1.75, 1.55, 0.22, 18)]
    clover = shamrock(1.8, 2.05, 0.25, rot=-0.3, stem=0.0) + [[(1.8, 2.05), (1.78, 1.75)]]
    legs = [[(-0.85, -1.3), (-0.85, -2.35)], [(-0.2, -1.3), (-0.2, -2.35)], [(0.85, -1.3), (0.85, -2.35)], [(0.2, -1.3), (0.2, -2.35)],
            [(-0.85, -1.85), (-0.2, -1.85)], [(0.2, -1.85), (0.85, -1.85)]]
    shoes = boot(-0.2, -2.8, 0.85, flip=True) + boot(0.2, -2.8, 0.85)
    return make("Jolly Leprechaun", hat + head + [beard, coat] + face + belt + buttons + [arm_l, arm_r] + hands + clover + legs + shoes,
                [eye(-0.22, 1.55, 0.06), eye(0.22, 1.55, 0.06)])


@design("stpatrick_leprechaun_face", T)
def leprechaun_face(rng):
    crown = poly((-1.3, 1.7), (-1.05, 3.0), (1.05, 3.0), (1.3, 1.7), closed=False)
    brim = ellipse(0, 1.4, 2.6, 0.35, 120)
    band = [[(-1.26, 1.95), (-0.35, 1.95)], [(0.35, 1.95), (1.26, 1.95)], [(-1.17, 2.45), (-0.35, 2.45)], [(0.35, 2.45), (1.17, 2.45)],
            rect(-0.35, 1.85, 0.35, 2.55), rect(-0.15, 2.05, 0.15, 2.35)]
    clover = shamrock(0.85, 2.75, 0.22, rot=-0.4, stem=0.0)
    sides = [[(-1.15, 1.08), (-1.18, 0.3)], [(1.15, 1.08), (1.18, 0.3)]]
    ears = [arc(-1.16, 0.7, 0.28, math.pi / 2, 1.5 * math.pi, 14), arc(1.16, 0.7, 0.28, math.pi / 2, -math.pi / 2, 14)]
    base = chain(cubic((-1.18, 0.3), (-1.4, -1.6), (-0.6, -2.8), (0, -2.9), 40), cubic((0, -2.9), (0.6, -2.8), (1.4, -1.6), (1.18, 0.3), 40))
    beard = bumpy(base, 0.2, 11)
    cheeks_line = [bumpy(quad((-1.18, 0.3), (-0.9, -0.1), (-0.6, -0.3), 20)[::-1], 0.06, 3), bumpy(quad((0.6, -0.3), (0.9, -0.1), (1.18, 0.3), 20)[::-1], 0.06, 3)]
    nose = circle(0, 0.05, 0.3, 30)
    mus = chain(cubic((0, -0.3), (-0.3, -0.1), (-0.9, -0.1), (-1.15, 0.1), 16), cubic((-1.15, 0.1), (-1.0, -0.5), (-0.4, -0.65), (0, -0.4), 16))
    mouth = chain(arc(0, -0.75, 0.38, math.radians(210), math.radians(330), 16), [(-0.33, -0.94)])
    brows = [bumpy(quad((-0.8, 0.85), (-0.5, 1.05), (-0.18, 0.9), 16), 0.05, 3), bumpy(quad((0.18, 0.9), (0.5, 1.05), (0.8, 0.85), 16), 0.05, 3)]
    eyes_ = [ellipse(-0.47, 0.55, 0.18, 0.16, 20), ellipse(0.47, 0.55, 0.18, 0.16, 20)]
    cheeks = [circle(-0.8, 0.2, 0.18, 16), circle(0.8, 0.2, 0.18, 16)]
    curls = [arc(-0.7, -1.5, 0.25, 0.3, 3.5, 12), arc(0.6, -1.9, 0.25, 0.3, 3.5, 12), arc(-0.1, -2.3, 0.2, 0.3, 3.5, 10)]
    return make("Leprechaun Face with Curly Beard", [crown, brim, beard, nose, mus, mirror_x(mus), mouth] + band + clover + sides + ears + cheeks_line
                + brows + eyes_ + cheeks + curls, [eye(-0.47, 0.55, 0.08), eye(0.47, 0.55, 0.08)])


@design("stpatrick_saint_patrick", T)
def saint_patrick(rng):
    mitre = chain([(-0.6, 1.6)], quad((-0.75, 2.3), (-0.3, 2.8), (0, 3.05), 12), quad((0, 3.05), (0.3, 2.8), (0.75, 2.3), 12)[1:], [(0.6, 1.6), (-0.6, 1.6)])
    mitre_d = [[(0, 1.6), (0, 2.95)], [(-0.6, 1.85), (0.6, 1.85)]] + [poly((-0.18, 2.35), (0.18, 2.35), (0, 2.6), closed=False)]
    face = [[(-0.5, 1.6), (-0.5, 1.15)], [(0.5, 1.6), (0.5, 1.15)]]
    beard = bumpy(chain(cubic((-0.5, 1.15), (-0.7, 0.4), (-0.2, -0.2), (0, -0.3), 20), cubic((0, -0.3), (0.2, -0.2), (0.7, 0.4), (0.5, 1.15), 20)), 0.1, 9)
    feat = [quad((-0.3, 1.38), (0, 1.25), (0.3, 1.38), 10), [(0, 1.42), (-0.08, 1.2)], quad((-0.18, 0.95), (0, 0.88), (0.18, 0.95), 8)]
    robe = poly((-0.5, 1.05), (-1.4, 0.6), (-1.9, -2.8), (1.9, -2.8), (1.4, 0.6), (0.5, 1.05), closed=False)
    stole = [[(-0.35, 0.0), (-0.45, -2.8)], [(0.35, 0.0), (0.45, -2.8)]] + [star(0, y, 0.18, 4, 0.4) for y in (-1.0, -1.8)]
    cape = [quad((-1.4, 0.6), (-0.6, -0.7), (0, -0.3), 16), quad((1.4, 0.6), (0.6, -0.7), (0, -0.3), 16)]
    hem = [wave(-1.9, 1.9, -2.5, 0.05, 6, 80)]
    crozier = [tube([(-2.3, -2.8), (-2.3, 1.8)], 0.22, cap=True), spiral(-1.95, 2.25, 0.08, 0.4, 1.1, 60, rot=math.pi),
               [(-2.41, 1.9), (-2.35, 2.25)]]
    hand_l = circle(-1.85, 0.0, 0.25, 18)
    arm_l = [quad((-1.45, 0.4), (-1.75, 0.25), (-1.75, 0.2), 6)]
    clover = shamrock(1.6, 1.8, 0.4, rot=0.2, stem=0.9, veins=True)
    hand_r = circle(1.62, 0.95, 0.25, 18)
    return make("Saint Patrick with Shamrock", [mitre, robe, beard, hand_l, hand_r] + mitre_d + face + feat + stole + cape + hem + crozier + arm_l + clover,
                [eye(-0.2, 1.43, 0.06), eye(0.2, 1.43, 0.06)])


@design("stpatrick_leprechaun_toadstool", T)
def leprechaun_toadstool(rng):
    cap = chain(cubic((-2.6, -0.6), (-2.4, 1.0), (2.4, 1.0), (2.6, -0.6), 50), quad((2.6, -0.6), (0, -1.0), (-2.6, -0.6), 40))
    stem_ = chain([(-0.7, -0.85)], cubic((-0.7, -0.85), (-0.5, -1.8), (-0.9, -2.6), (-1.0, -2.8), 16), [(1.0, -2.8)],
                  cubic((1.0, -2.8), (0.9, -2.6), (0.5, -1.8), (0.7, -0.85), 16))
    grass = [zigzag(-3.0, -1.0, -2.75, 0.1, 6), zigzag(1.0, 3.0, -2.75, 0.1, 6)]
    spots = [ellipse(x, y, rx, ry, 20) for x, y, rx, ry in [(-1.9, -0.2, 0.3, 0.16), (1.9, -0.2, 0.3, 0.16), (-1.3, 0.3, 0.22, 0.12), (1.3, 0.3, 0.22, 0.12)]]
    s = 1.25
    def L(pts):
        return transform(pts, dy=0.55 * (1 - s), s=s)
    hat = [poly((-0.38, 2.42), (-0.3, 2.95), (0.3, 2.95), (0.38, 2.42), closed=False), ellipse(0, 2.35, 0.75, 0.12, 40), [(-0.36, 2.6), (0.36, 2.6)]]
    head = [[(-0.3, 2.25), (-0.3, 2.05)], [(0.3, 2.25), (0.3, 2.05)]]
    beard = bumpy(chain(quad((-0.3, 2.05), (-0.35, 1.5), (0, 1.4), 12), quad((0, 1.4), (0.35, 1.5), (0.3, 2.05), 12)), 0.06, 7)
    body = poly((-0.25, 1.55), (-0.55, 1.35), (-0.6, 0.55), (0.6, 0.55), (0.55, 1.35), (0.25, 1.55), closed=False)
    belt = [[(-0.58, 0.85), (-0.13, 0.85)], [(0.13, 0.85), (0.58, 0.85)], rect(-0.13, 0.77, 0.13, 0.93)]
    leg_c = [[(-0.4, 0.6), (-0.5, 0.1), (-0.5, -0.4)], [(0.4, 0.6), (0.5, 0.1), (0.5, -0.4)]]
    legs = [tube(c, 0.28, cap=False) for c in leg_c]
    shoes = boot(-0.38, -0.75, 0.5, flip=True) + boot(0.38, -0.75, 0.5)
    arms = [tube([(-0.55, 1.25), (-0.95, 0.8), (-0.8, 0.6)], 0.24, cap=False), tube([(0.55, 1.25), (1.0, 1.6), (1.1, 2.0)], 0.24, cap=False)]
    clover = shamrock(1.15, 2.35, 0.18, stem=0.0) + [[(1.15, 2.35), (1.12, 2.1)]]
    man = [L(p) for p in hat + head + [beard, body] + belt + legs + shoes + arms + clover]
    covers = [L(tube(c, 0.28)) for c in leg_c] + [L(shoes[0]), L(shoes[2]), L(rect(-0.6, 0.55, 0.6, 1.4))]
    back = hide([cap] + spots, *covers)
    return make("Leprechaun on a Toadstool", back + [stem_] + grass + man,
                [eye(-0.12 * s, 0.55 * (1 - s) + 2.15 * s, 0.05), eye(0.12 * s, 0.55 * (1 - s) + 2.15 * s, 0.05)])


@design("stpatrick_irish_dancer", T)
def irish_dancer(rng):
    head = circle(0, 2.2, 0.42, 36)
    curls = [bumpy(arc(0, 2.2, 0.48, math.radians(10), math.radians(170), 40), 0.18, 7),
             bumpy([(-0.48, 2.25), (-0.6, 1.4)], 0.15, 4)[::-1], bumpy([(0.6, 1.4), (0.48, 2.25)], 0.15, 4)[::-1]]
    crown = [zigzag(-0.35, 0.35, 2.68, 0.06, 3)]
    neck = [[(-0.12, 1.78), (-0.12, 1.6)], [(0.12, 1.78), (0.12, 1.6)]]
    bodice = poly((-0.12, 1.6), (-0.5, 1.5), (-0.4, 0.4), (0.4, 0.4), (0.5, 1.5), (0.12, 1.6), closed=False)
    skirt = chain([(-0.4, 0.4)], quad((-0.4, 0.4), (-1.2, 0.0), (-1.55, -0.6), 12), quad((-1.55, -0.6), (0, -0.95), (1.55, -0.6), 30),
                  quad((1.55, -0.6), (1.2, 0.0), (0.4, 0.4), 12))
    trim = [quad((-1.3, -0.35), (0, -0.7), (1.3, -0.35), 30)]
    knots = [circle(x, y, 0.13, 14) for x, y in [(-0.75, -0.15), (0.0, -0.3), (0.75, -0.15)]] + [spiral(x, 0.05, 0.02, 0.13, 1.2, 24) for x in (-0.4, 0.4)]
    shawl = quad((-0.5, 1.5), (0, 1.0), (0.5, 1.5), 10)
    arm_c = [[(-0.42, 1.45), (-0.6, 0.6), (-0.72, -0.15)], [(0.42, 1.45), (0.6, 0.6), (0.72, -0.15)]]
    arms = [tube(c, 0.24, cap=False) for c in arm_c]
    hands = [circle(-0.73, -0.3, 0.14, 12), circle(0.73, -0.3, 0.14, 12)]
    back = hide([skirt] + trim + knots, *[tube(c, 0.24) for c in arm_c] + hands)
    leg_down = tube([(-0.35, -0.85), (-0.35, -1.7), (-0.3, -2.5)], 0.3, cap=False)
    leg_up = tube([(0.35, -0.85), (1.1, -1.2), (2.2, -0.7)], 0.3, cap=False)
    shoe_down = chain([(-0.45, -2.5)], [(-0.5, -2.8), (0.2, -2.8)], quad((0.2, -2.8), (0.25, -2.55), (-0.15, -2.5), 6))
    shoe_up = chain([(2.17, -0.55)], quad((2.6, -0.5), (2.75, -0.7), (2.55, -0.9), 6)[1:], [(2.22, -0.85)])
    laces = [[(-0.4, -2.6), (0.0, -2.68)]]
    floor = [[(-2.4, -2.85), (2.4, -2.85)]]
    return make("Irish Step Dancer", [head, bodice, shawl, leg_down, leg_up, shoe_down, shoe_up] + back + curls + crown + neck + arms + hands + laces + floor,
                [eye(-0.14, 2.25, 0.05), eye(0.14, 2.25, 0.05)])


@design("stpatrick_leprechaun_trap", T)
def leprechaun_trap(rng):
    a = math.radians(-20)

    def B(pts):
        return transform(pts, dx=1.6, dy=-2.6, rot=a)
    front = B(rect(-3.2, 0.0, 0.0, 2.6))
    side = B(poly((0.0, 0.0), (0.55, 0.45), (0.55, 3.05), (0.0, 2.6), closed=False))
    top = B(poly((0.0, 2.6), (-0.55 + 0.55, 3.05), (-3.2 + 0.55, 3.05), (-3.2, 2.6), closed=False))
    slats = [B([(-3.2, y), (0.0, y)]) for y in (0.85, 1.75)]
    clover = [B(p) for p in shamrock(-1.6, 1.3, 0.35, stem=0.0)]
    corner = B([(-3.2, 0.0)])[0]
    stick = tube([(corner[0] + 0.05, -2.6), (corner[0] + 0.05, corner[1])], 0.16, cap=False)
    string = cubic((corner[0], -2.3), (-2.0, -2.8), (-2.6, -2.2), (-3.0, -2.5), 20)
    ground = [[(-3.0, -2.62), (3.0, -2.62)]]
    coins = [ellipse(x, y, 0.32, 0.11, 22) for x, y in [(-0.7, -2.5), (-0.05, -2.5), (-0.4, -2.28), (0.25, -2.28)]]
    coins = hide(coins, front)
    sign = [rect(-2.9, 1.0, -1.5, 2.2), [(-2.2, 1.0), (-2.2, 0.4)]] + shamrock(-2.2, 1.55, 0.25, stem=0.0)
    rainbow = [arc(2.2, 0.8, r, math.radians(20), math.radians(160), 30) for r in (0.6, 0.85, 1.1)]
    rainbow = hide(rainbow, front, B(poly((0.0, 0.0), (0.55, 0.45), (0.55, 3.05), (0.0, 2.6))))
    return make("Leprechaun Trap", [front, side, top, stick, string] + slats + clover + ground + coins + sign + rainbow
                + [sparkle(2.6, 2.6, 0.3), sparkle(-0.3, 2.7, 0.22)])


# ------------------------------------------------------------ things a leprechaun owns

@design("stpatrick_buckle_boot", T)
def buckle_boot(rng):
    outline = chain([(-1.75, 2.6), (-1.85, -1.5), (-1.85, -2.3), (-0.9, -2.3), (-0.9, -1.75)],
                    quad((-0.9, -1.75), (-0.5, -1.9), (0.0, -1.9), 8),
                    [(1.6, -1.9)], cubic((1.6, -1.9), (2.6, -1.9), (3.0, -1.3), (2.9, -0.5), 20),
                    quad((2.9, -0.5), (2.78, -0.15), (2.55, -0.4), 8),
                    cubic((2.55, -0.4), (2.3, -0.9), (1.2, -0.7), (0.4, -0.3), 20),
                    quad((0.4, -0.3), (-0.2, 0.0), (-0.25, 0.6), 10), [(-0.3, 2.6)])
    top = ellipse(-1.02, 2.6, 0.73, 0.2, 40)
    cuff = [quad((-1.77, 2.0), (-1.0, 1.85), (-0.28, 2.0), 12)]
    strap = [[(-1.79, 0.55), (-1.35, 0.55)], [(-0.7, 0.55), (-0.25, 0.55)], [(-1.8, 1.15), (-1.35, 1.15)], [(-0.7, 1.15), (-0.26, 1.15)]]
    buckle = [rect(-1.35, 0.35, -0.7, 1.35), rect(-1.17, 0.58, -0.88, 1.12)]
    sole = [[(0.0, -1.7), (1.6, -1.7)], [(-1.85, -1.5), (-0.9, -1.5)]]
    ball = circle(2.85, -0.12, 0.18, 16)
    clover = shamrock(0.95, -1.15, 0.22, rot=-0.2, stem=0.0)
    coins = coin(-2.4, -2.0, 0.45) + coin(2.2, 1.6, 0.55)
    return make("Leprechaun Buckle Boot", [outline, top, ball] + cuff + strap + buckle + sole + clover + coins + [sparkle(1.2, 2.5, 0.3)])


@design("stpatrick_pipe", T)
def pipe(rng):
    bowl = chain([(-2.3, 0.9)], cubic((-2.3, 0.9), (-2.4, -1.1), (-0.9, -1.2), (-0.8, 0.9), 30))
    rim = ellipse(-1.55, 0.9, 0.75, 0.2, 40)
    tobacco = [zigzag(-2.1, -1.0, 0.92, 0.05, 5)]
    stem_c = cubic((-0.95, -0.25), (0.3, -0.6), (1.3, -0.1), (2.4, 0.35), 30)
    stem = tube(stem_c, 0.32, cap=False)
    mouth = tube([(2.38, 0.35), (2.9, 0.58)], 0.2, cap=True)
    band = [[(stem_c[8][0] - 0.04, stem_c[8][1] + 0.17), (stem_c[8][0] + 0.04, stem_c[8][1] - 0.17)],
            [(stem_c[12][0] - 0.05, stem_c[12][1] + 0.17), (stem_c[12][0] + 0.03, stem_c[12][1] - 0.17)]]
    clover = shamrock(-1.6, -0.15, 0.25, stem=0.0)
    smoke = [cubic((-1.4, 1.2), (-0.8, 1.7), (-1.6, 2.0), (-0.9, 2.5), 24), cubic((-1.9, 1.2), (-2.5, 1.7), (-1.8, 2.1), (-2.3, 2.7), 24)]
    puff = shamrock(0.2, 2.2, 0.38, rot=-0.3, stem=0.0)
    return make("Leprechaun's Clay Pipe", [bowl, rim, stem, mouth] + tobacco + band + clover + smoke + puff + [sparkle(2.2, 2.0, 0.3), sparkle(1.4, -1.6, 0.25)])


@design("stpatrick_shillelagh", T)
def shillelagh(rng):
    c = [(-1.9 + 3.9 * t + 0.12 * math.sin(7 * t), 1.8 - 4.6 * t) for t in [i / 40 for i in range(41)]]
    stick = tube(c, lambda t: 0.42 - 0.12 * t, cap=False)
    knob = polar(lambda t: 0.6 * (1 + 0.07 * math.sin(5 * t) + 0.04 * math.sin(3 * t + 1)), t0=math.radians(-20), t1=math.radians(280), n=90,
                 cx=-2.12, cy=2.15)
    tip = arc(c[-1][0], c[-1][1], 0.15, math.radians(-150), math.radians(30), 10)
    nubs = []
    for i, sgn in [(10, 1), (17, -1), (24, 1), (31, -1)]:
        x, y = c[i]
        nubs.append(poly((x + sgn * 0.2, y + sgn * 0.12), (x + sgn * 0.48, y + sgn * 0.3), (x + sgn * 0.22, y - sgn * 0.05), closed=False))
    rings = [ellipse(*c[k], 0.13, 0.08, 14) for k in (14, 28)]
    bx, by = c[6]
    bow = [lens((bx, by), (bx - 1.0, by + 0.6), 0.35), lens((bx, by), (bx + 0.9, by + 0.75), 0.35), circle(bx, by, 0.16, 14),
           poly((bx - 0.1, by - 0.12), (bx - 0.6, by - 1.2), (bx - 0.35, by - 1.05), (bx - 0.3, by - 1.35), (bx + 0.05, by - 0.15), closed=False),
           poly((bx + 0.12, by - 0.1), (bx + 0.75, by - 0.9), (bx + 0.45, by - 0.9), (bx + 0.55, by - 1.2), (bx + 0.0, by - 0.18), closed=False)]
    clovers = shamrock(1.6, 1.6, 0.42, rot=-0.3, stem=1.0, veins=True) + shamrock(-1.4, -1.6, 0.35, rot=0.4, stem=1.0)
    stick = hide([stick], circle(bx, by, 0.16, 14))
    return make("Blackthorn Shillelagh", stick + [knob, tip] + nubs + rings + bow + clovers)


@design("stpatrick_treasure_chest", T)
def treasure_chest(rng):
    box = rect(-2.2, -2.6, 2.2, -0.2)
    lid = chain([(-2.2, -0.2), (-2.4, 1.4)], cubic((-2.4, 1.4), (-2.0, 2.4), (2.0, 2.4), (2.4, 1.4), 30), [(2.2, -0.2)])
    lid_edge = cubic((-2.35, 1.0), (-1.9, 1.95), (1.9, 1.95), (2.35, 1.0), 30)
    bands = [[(-1.4, -2.6), (-1.4, -0.2)], [(1.4, -2.6), (1.4, -0.2)], [(-2.2, -0.6), (2.2, -0.6)]]
    lock = [rrect(-0.35, -1.5, 0.35, -0.8, 0.08), circle(0, -1.05, 0.1, 10), [(0, -1.15), (0, -1.35)]]
    coins = [ellipse(x, y, 0.42, 0.14, 22) for x, y in [(-1.6, 0.0), (-0.8, 0.15), (0.0, 0.0), (0.8, 0.2), (1.6, 0.0), (-1.2, 0.4), (-0.4, 0.55),
                                                       (0.4, 0.45), (1.2, 0.5), (0.0, 0.85), (-0.8, 0.85), (0.8, 0.9)]]
    front_c = coin(-2.6, -2.2, 0.38) + coin(2.6, -2.3, 0.33) + [ellipse(2.5, -2.75, 0.4, 0.12, 20)]
    coins = hide(coins, rect(-2.2, -2.6, 2.2, -0.2))
    gem = [poly((0.0, 1.25), (0.3, 1.45), (0.0, 1.75), (-0.3, 1.45))]
    rivets = [circle(x, y, 0.07, 8) for x in (-1.4, 1.4) for y in (-2.3, -0.9)]
    return make("Treasure Chest of Gold", [box, lid, lid_edge] + bands + lock + coins + front_c + gem + rivets + [sparkle(-2.6, 2.4, 0.3), sparkle(2.7, 2.2, 0.25)])


@design("stpatrick_gold_sack", T)
def gold_sack(rng):
    sack = chain([(-0.6, 0.9)], cubic((-0.6, 0.9), (-2.8, -0.2), (-2.6, -2.7), (0, -2.7), 30), cubic((0, -2.7), (2.6, -2.7), (2.8, -0.2), (0.6, 0.9), 30))
    neck = [quad((-0.6, 0.9), (0, 0.7), (0.6, 0.9), 10)]
    ruffle = chain([(-0.6, 0.9)], quad((-1.3, 1.6), (-1.0, 2.2), (-0.5, 1.8), 10)[1:], quad((-0.5, 1.8), (0, 2.3), (0.5, 1.8), 10)[1:],
                   quad((0.5, 1.8), (1.0, 2.2), (1.3, 1.6), 10)[1:], [(0.6, 0.9)])
    tie = [ellipse(-0.75, 0.75, 0.35, 0.15, 18, rot=0.4), ellipse(0.75, 0.75, 0.35, 0.15, 18, rot=-0.4),
           quad((-0.3, 0.75), (-0.6, 0.0), (-0.9, -0.4), 10), quad((0.3, 0.75), (0.5, 0.1), (0.9, -0.3), 10)]
    patch = [rect(-1.0, -1.9, 0.0, -1.0)]
    clover = shamrock(0.7, -1.2, 0.35, stem=0.8)
    coins = coin(-2.5, -2.4, 0.4) + coin(2.4, -2.3, 0.45) + [ellipse(1.6, -2.75, 0.4, 0.12, 20), ellipse(-1.6, -2.8, 0.38, 0.12, 20)]
    coins = hide(coins, sack)
    stitches = [[(x, -1.0), (x, -0.85)] for x in (-0.8, -0.5, -0.2)]
    return make("Sack of Gold Coins", [sack, ruffle] + neck + tie + patch + clover + coins + stitches + [sparkle(2.4, 1.6, 0.3), sparkle(-2.4, 1.2, 0.25)])


@design("stpatrick_top_hat", T)
def top_hat(rng):
    crown = chain([(-1.3, -0.9)], cubic((-1.3, -0.9), (-1.5, 1.0), (-1.2, 2.0), (-1.4, 2.6), 20), [(1.4, 2.6)],
                  cubic((1.4, 2.6), (1.2, 2.0), (1.5, 1.0), (1.3, -0.9), 20))
    top = ellipse(0, 2.6, 1.4, 0.3, 50)
    brim = chain(cubic((-1.3, -0.9), (-2.4, -0.9), (-3.0, -0.6), (-2.9, -0.2), 16), cubic((-2.9, -0.2), (-2.8, -1.6), (2.8, -1.6), (2.9, -0.2), 40),
                 cubic((2.9, -0.2), (3.0, -0.6), (2.4, -0.9), (1.3, -0.9), 16))
    band = [quad((-1.33, -0.35), (0, -0.55), (1.33, -0.35), 20), quad((-1.39, 0.35), (0, 0.15), (1.39, 0.35), 20)]
    clover = shamrock(0.0, 1.2, 0.55, stem=0.0, veins=True)
    bow = [lens((0.9, -0.1), (2.0, 0.6), 0.3), lens((0.9, -0.1), (1.9, -0.7), 0.3)]
    bow = [lens((1.3, -0.1), (2.1, 0.5), 0.3)]
    coins = coin(-2.4, 1.8, 0.4) + coin(2.3, 1.6, 0.35)
    return make("Shamrock Top Hat", [crown, top, brim] + band + clover + coins + [sparkle(-2.2, 2.9, 0.25), sparkle(2.6, 2.7, 0.25)])


@design("stpatrick_bow_tie", T)
def bow_tie(rng):
    wing = chain([(-0.45, 0.45)], cubic((-0.45, 0.45), (-1.5, 1.5), (-2.8, 1.8), (-2.9, 0.9), 20), quad((-2.9, 0.9), (-3.0, 0.0), (-2.9, -0.9), 12),
                 cubic((-2.9, -0.9), (-2.8, -1.8), (-1.5, -1.5), (-0.45, -0.45), 20))
    knot = rrect(-0.45, -0.6, 0.45, 0.6, 0.15)
    folds = [quad((-0.6, 0.3), (-1.3, 0.2), (-1.8, 0.9), 10), quad((-0.6, -0.3), (-1.3, -0.2), (-1.8, -0.9), 10)]
    clovers = shamrock(-2.0, 0.1, 0.25, stem=0.0) + shamrock(-1.1, 0.95, 0.18, stem=0.0, rot=0.3) + shamrock(-1.1, -0.9, 0.18, stem=0.0, rot=-0.3)
    left = [wing] + folds + clovers
    knot_l = [quad((-0.2, 0.6), (-0.3, 0.0), (-0.2, -0.6), 8), quad((0.2, 0.6), (0.3, 0.0), (0.2, -0.6), 8)]
    band = [[(-0.25, 0.6), (-0.4, 2.2)], [(0.25, 0.6), (0.4, 2.2)]]
    band = [quad((-0.35, 0.6), (-0.6, 1.6), (-1.6, 2.4), 12), quad((0.35, 0.6), (0.6, 1.6), (1.6, 2.4), 12)]
    return make("Shamrock Bow Tie", left + mirror_all(left) + [knot] + knot_l + [sparkle(0, -2.0, 0.35)])


@design("stpatrick_charm_bracelet", T)
def charm_bracelet(rng):
    links = []
    pts = [(2.7 * math.cos(a), 1.6 + 1.4 * math.sin(a)) for a in [math.pi + math.pi * (k + 0.5) / 15 for k in range(15)]]
    for k, (x, y) in enumerate(pts):
        a = math.atan2(y - 1.6, x) + math.pi / 2
        links.append(ellipse(x, y, 0.3, 0.14, 18, rot=a))
    clasp = [circle(-2.85, 1.85, 0.22, 16), poly((2.7, 1.6), (2.95, 2.0), (2.6, 2.1), closed=False)]
    charms = []
    hang = {2: "clover", 5: "shoe", 7: "heart", 9: "coin", 12: "hat"}
    for k, kind in hang.items():
        x, y = pts[k]
        cy = y - 0.6
        charms.append(circle(x, y - 0.25, 0.09, 10))
        if kind == "clover":
            charms += shamrock(x, cy - 0.35, 0.28, stem=0.0, leaves=4)
        elif kind == "shoe":
            charms.append(chain(arc(x, cy - 0.45, 0.45, math.radians(-50), math.radians(230), 30),
                                arc(x, cy - 0.45, 0.25, math.radians(230), math.radians(-50), 20), [arc(x, cy - 0.45, 0.45, math.radians(-50), 0, 1)[0]]))
        elif kind == "heart":
            charms.append(heart(x, cy - 0.45, 0.45, 60))
        elif kind == "coin":
            charms += coin(x, cy - 0.45, 0.45) + [sparkle(x, cy - 0.45, 0.18)]
        elif kind == "hat":
            charms += [poly((x - 0.3, cy - 0.65), (x - 0.25, cy - 0.15), (x + 0.25, cy - 0.15), (x + 0.3, cy - 0.65), closed=False),
                       ellipse(x, cy - 0.7, 0.55, 0.1, 24), [(x - 0.28, cy - 0.45), (x + 0.28, cy - 0.45)]]
    return make("Lucky Charm Bracelet", links + clasp + charms)


@design("stpatrick_shamrock_glasses", T)
def shamrock_glasses(rng):
    def lens_(cx):
        return shamrock(cx, -0.1, 0.75, stem=0.0)
    rims = lens_(-1.55) + lens_(1.55)
    bridge = [quad((-0.75, 0.25), (0, 0.6), (0.75, 0.25), 12)]
    arms = [[(-2.95, 0.9), (-3.2, 1.0), (-3.4, 2.0)], [(2.95, 0.9), (3.2, 1.0), (3.4, 2.0)]]
    shine = [quad((-1.85, 0.75), (-1.75, 1.15), (-1.45, 1.3), 6), quad((1.25, 0.75), (1.35, 1.15), (1.65, 1.3), 6)]
    sparkles = [sparkle(0, -1.6, 0.35), sparkle(-2.6, -2.0, 0.25), sparkle(2.6, -2.0, 0.25)]
    return make("Shamrock Party Glasses", rims + bridge + arms + shine + sparkles)


@design("stpatrick_headband", T)
def headband(rng):
    band = tube(arc(0, -2.0, 2.4, math.radians(10), math.radians(170), 60), 0.3, cap=True)
    springs = []
    for sx in (-1, 1):
        x0, y0 = sx * 1.1, -2.0 + math.sqrt(2.4 ** 2 - 1.1 ** 2) + 0.15
        pts = []
        for i in range(81):
            t = i / 80
            cx, cy = x0 + sx * 0.7 * t, y0 + 1.7 * t
            pts.append((cx + 0.15 * math.cos(TAU * 5 * t), cy + 0.1 * math.sin(TAU * 5 * t)))
        springs.append(pts)
        springs += shamrock(x0 + sx * 0.7, y0 + 1.75, 0.45, rot=-sx * 0.25, stem=0.0, veins=True)
    hat = [poly((-0.45, -0.2), (-0.35, 0.75), (0.35, 0.75), (0.45, -0.2), closed=False), ellipse(0, -0.25, 0.85, 0.15, 30),
           [(-0.42, 0.1), (0.42, 0.1)], rect(-0.15, 0.0, 0.15, 0.2)]
    return make("Shamrock Headband Boppers", [band] + springs + hat)


@design("stpatrick_fiddle", T)
def fiddle(rng):
    half = chain(cubic((0, 1.0), (0.7, 1.05), (1.1, 0.8), (1.05, 0.2), 16), cubic((1.05, 0.2), (1.0, -0.1), (0.62, -0.2), (0.62, -0.6), 12),
                 cubic((0.62, -0.6), (0.62, -1.0), (1.0, -1.0), (1.25, -1.2), 12), cubic((1.25, -1.2), (1.55, -1.7), (1.2, -2.6), (0, -2.6), 20))
    body = chain(half, mirror_x(half)[::-1])
    board = poly((-0.17, 2.3), (-0.25, -0.45), (0.25, -0.45), (0.17, 2.3), closed=False)
    body = hide([body], poly((-0.17, 2.3), (-0.25, -0.45), (0.25, -0.45), (0.17, 2.3)))
    pegbox = [[(-0.17, 2.3), (-0.13, 2.85)], [(0.17, 2.3), (0.13, 2.85)], [(-0.17, 2.3), (0.17, 2.3)]]
    scroll = spiral(0, 3.05, 0.04, 0.24, 1.6, 50, rot=-math.pi / 2)
    pegs = [[(-0.15, y), (-0.5, y + 0.05)] for y in (2.45, 2.7)] + [[(0.15, y), (0.5, y + 0.05)] for y in (2.45, 2.7)]
    pegs += [ellipse(-0.58, y + 0.06, 0.1, 0.07, 10) for y in (2.45, 2.7)] + [ellipse(0.58, y + 0.06, 0.1, 0.07, 10) for y in (2.45, 2.7)]
    bridge = poly((-0.48, -1.05), (-0.4, -0.82), (0.4, -0.82), (0.48, -1.05), closed=False)
    tail = poly((-0.27, -1.3), (0.27, -1.3), (0.13, -2.35), (-0.13, -2.35))
    strings = [[(x, -1.3), (x * 0.8, 2.3)] for x in (-0.09, 0.09)]
    strings = hide(strings, poly((-0.48, -1.05), (-0.4, -0.82), (0.4, -0.82), (0.48, -1.05)))
    fh = cubic((0.55, -0.3), (0.3, -0.6), (0.75, -1.2), (0.5, -1.5), 20)
    holes = [fh, mirror_x(fh)]
    parts = body + [board, bridge, tail, scroll] + pegbox + pegs + strings + holes
    parts = [transform(p, dx=-0.7) for p in parts]
    hints = [eye(x - 0.7, y, 0.06) for x, y in [(0.55, -0.3), (0.5, -1.5), (-0.55, -0.3), (-0.5, -1.5)]]
    bow = [quad((1.95, -2.7), (2.05, 0.2), (1.95, 3.0), 20), [(2.3, -2.3), (2.3, 2.75)], rect(1.97, -2.75, 2.45, -2.2), poly((1.95, 3.0), (2.35, 2.95), (2.3, 2.75), closed=False)]
    clover = shamrock(-2.3, 2.3, 0.35, stem=0.8)
    return make("Irish Fiddle and Bow", parts + bow + clover, hints)


@design("stpatrick_bagpipes", T)
def bagpipes(rng):
    rot = -0.25
    bag = ellipse(0.2, -0.8, 1.7, 1.15, 120, rot=rot)
    tartan = []
    for x in (-0.9, -0.3, 0.3, 0.9):
        h = 1.15 * math.sqrt(1 - (x / 1.7) ** 2)
        tartan.append(transform([(x, -h), (x, h)], dx=0.2, dy=-0.8, rot=rot))
    for y in (-0.5, 0.0, 0.5):
        w = 1.7 * math.sqrt(1 - (y / 1.15) ** 2)
        tartan.append(transform([(-w, y), (w, y)], dx=0.2, dy=-0.8, rot=rot))
    drones, tops = [], []
    for (x0, y0), L in [((-0.9, -0.1), 3.4), ((-0.3, 0.1), 2.7), ((0.3, 0.2), 2.4)]:
        a = math.radians(115)
        c = [(x0 + L * t * math.cos(a), y0 + L * t * math.sin(a)) for t in [i / 10 for i in range(11)]]
        drones.append(tube(c, 0.24, cap=False))
        ex, ey = c[-1]
        tops.append(transform(poly((-0.13, 0), (-0.22, 0.35), (0.22, 0.35), (0.13, 0), closed=False), dx=ex, dy=ey, rot=a - math.pi / 2))
        mx, my = c[6]
        tops.append(ellipse(mx, my, 0.22, 0.13, 16, rot=a - math.pi / 2))
    drones = hide(drones, bag)
    cord = [cubic((-2.05, 2.4), (-1.4, 1.6), (-0.9, 1.8), (-0.6, 2.2), 20), [(-1.25, 1.8), (-1.3, 1.1)], poly((-1.3, 1.1), (-1.45, 0.7), (-1.15, 0.7), (-1.3, 1.1), closed=False)]
    ch_c = [(-1.2, -1.2), (-1.4, -2.0), (-1.55, -2.7)]
    chanter = hide([tube(ch_c, lambda t: 0.3 + 0.08 * t, cap=False)], bag)
    bell = [ellipse(-1.55, -2.8, 0.28, 0.1, 16)]
    holes = [circle(-1.35 - 0.13 * k, -1.85 - 0.25 * k, 0.06, 8) for k in range(3)]
    blow = hide([tube([(1.4, -0.1), (2.2, 1.0), (2.6, 1.8)], 0.2, cap=False)], bag)
    mouth = [tube([(2.6, 1.8), (2.78, 2.25)], 0.14, cap=True)]
    tassel = [poly((-0.6, 2.2), (-0.75, 1.75), (-0.45, 1.75), (-0.6, 2.2), closed=False)]
    return make("Bagpipes", [bag] + tartan + drones + tops + cord + chanter + bell + blow + mouth + tassel, holes)


@design("stpatrick_bodhran", T)
def bodhran(rng):
    cx, cy = -0.3, 0.3
    rim = [circle(cx, cy, 2.45, 140), circle(cx, cy, 2.15, 130)]
    knotring = polar(lambda t: 1.55 + 0.1 * math.sin(14 * t), n=300, cx=cx, cy=cy)
    inner = circle(cx, cy, 1.25, 80)
    clover = shamrock(cx, cy + 0.05, 0.55, stem=0.0, veins=True)
    tipper_c = [(0.6, -2.9), (2.9, -0.6)]
    tipper = tube(densify(tipper_c, 0.2), 0.18, cap=True)
    knobs = [circle(0.5, -3.0, 0.24, 18), circle(3.0, -0.5, 0.24, 18)]
    back = hide(rim + [knotring], tipper, *knobs)
    tacks = [eye(cx + 2.3 * math.cos(a), cy + 2.3 * math.sin(a), 0.06) for a in [TAU * k / 24 for k in range(24)]]
    return make("Bodhran Drum and Tipper", back + [inner, tipper] + clover + knobs, tacks)


@design("stpatrick_tin_whistle", T)
def tin_whistle(rng):
    a = math.radians(35)

    def R(p):
        return transform(p, dx=-0.3, dy=-0.6, rot=a)
    body = poly((-2.0, 0.22), (2.6, 0.22), (2.6, -0.22), (-2.0, -0.22), closed=False)
    end = ellipse(2.6, 0.0, 0.07, 0.22, 16)
    mouth = poly((-2.0, 0.26), (-3.0, 0.2), (-3.05, -0.12), (-2.0, -0.26))
    window = poly((-1.85, 0.22), (-1.65, 0.0), (-1.35, 0.0), (-1.35, 0.22), closed=False)
    holes = [circle(x, 0.0, 0.1, 12) for x in (-0.4, 0.0, 0.4, 1.0, 1.4, 1.8)]
    parts = [R(p) for p in [body, end, mouth, window] + holes]

    def note(x, y, s, flag=True):
        out = [ellipse(x, y, 0.22 * s, 0.16 * s, 16, rot=0.4), [(x + 0.2 * s, y + 0.05 * s), (x + 0.2 * s, y + 0.95 * s)]]
        if flag:
            out.append(quad((x + 0.2 * s, y + 0.95 * s), (x + 0.6 * s, y + 0.7 * s), (x + 0.45 * s, y + 0.35 * s), 8))
        return out
    notes = note(-2.2, 1.2, 1.1) + note(-1.2, 2.0, 1.0) + note(1.6, -1.8, 1.0)
    pair = [ellipse(0.3, 2.3, 0.2, 0.15, 16, rot=0.4), ellipse(1.0, 2.1, 0.2, 0.15, 16, rot=0.4), [(0.5, 2.35), (0.5, 3.05)], [(1.2, 2.15), (1.2, 2.85)],
            [(0.5, 3.05), (1.2, 2.85)]]
    clover = shamrock(2.3, -0.6, 0.4, stem=0.9, rot=-0.2)
    return make("Tin Whistle and Music Notes", parts + notes + pair + clover)


@design("stpatrick_concertina", T)
def concertina(rng):
    hexa = [(-1.75 + 1.25 * math.cos(math.pi / 6 + k * math.pi / 3) * 0.75, 1.25 * math.sin(math.pi / 6 + k * math.pi / 3)) for k in range(7)]
    face = poly(*hexa[:-1])
    inner = [transform(p, dx=-1.75, s=0.78, sx=0.78 * 0.75, sy=0.78) for p in [[(x + 1.75, y) for x, y in hexa]]]
    buttons = [circle(-1.75 + dx, dy, 0.1, 10) for dx, dy in [(-0.35, 0.5), (0.0, 0.6), (0.35, 0.5), (-0.4, 0.0), (0.0, 0.0), (0.4, 0.0),
                                                               (-0.35, -0.5), (0.0, -0.6), (0.35, -0.5)]]
    strap = [rrect(-2.9, -0.4, -2.55, 0.4, 0.1)]
    folds = 8
    x0, x1 = -0.95, 1.9
    top = [(x0 + (x1 - x0) * i / (2 * folds), 0.95 + (0.12 if i % 2 else 0.0)) for i in range(2 * folds + 1)]
    bot = [(x, -y) for x, y in top]
    pleats = [[(x0 + (x1 - x0) * i / (2 * folds), 0.95 + (0.12 if i % 2 else 0.0)), (x0 + (x1 - x0) * i / (2 * folds), -0.95 - (0.12 if i % 2 else 0.0))]
              for i in range(1, 2 * folds)]
    right = poly((1.9, 1.08), (2.05, 1.25), (2.35, 1.25), (2.5, 0.0), (2.35, -1.25), (2.05, -1.25), (1.9, -1.08), closed=False)
    right_strap = [rrect(2.55, -0.4, 2.85, 0.4, 0.1)]
    notes = [ellipse(-0.3, 2.2, 0.2, 0.14, 14, rot=0.4), [(-0.12, 2.25), (-0.12, 3.0)], quad((-0.12, 3.0), (0.25, 2.75), (0.15, 2.45), 8)]
    clover = shamrock(1.2, 2.2, 0.32, stem=0.0, rot=0.2) + shamrock(-0.2, -2.3, 0.32, stem=0.0, rot=-0.2)
    return make("Irish Concertina", [face, top, bot, right] + inner + buttons + strap + pleats + right_strap + notes + clover)


# ------------------------------------------------------------ Irish places


@design("stpatrick_thatched_cottage", T)
def thatched_cottage(rng):
    walls = poly((-2.6, 0.0), (-2.6, -2.0), (2.6, -2.0), (2.6, 0.0), closed=False)
    roof = chain(quad((-2.95, 0.0), (-2.85, 1.9), (-2.1, 1.9), 16), [(2.1, 1.9)], quad((2.1, 1.9), (2.85, 1.9), (2.95, 0.0), 16))
    eave = bumpy([(2.95, 0.0), (-2.95, 0.0)], 0.12, 10)
    chim = [poly((1.5, 1.9), (1.5, 2.6), (2.05, 2.6), (2.05, 1.9), closed=False), rect(1.4, 2.6, 2.15, 2.78)]
    smoke = [cubic((1.8, 2.85), (2.4, 3.2), (1.6, 3.5), (2.3, 3.9), 20)]
    texture = [quad((x, 1.6), (x + 0.15, 1.0), (x + 0.05, 0.4), 8) for x in (-2.0, -1.0, 0.0, 1.0)]
    door = [rect(-0.4, -2.0, 0.4, -0.55), [(-0.4, -1.25), (0.4, -1.25)], circle(0.25, -1.45, 0.06, 8)]
    wins = []
    for wx in (-1.6, 1.6):
        wins += [rect(wx - 0.45, -1.15, wx + 0.45, -0.4), [(wx, -1.15), (wx, -0.4)], [(wx - 0.45, -0.78), (wx + 0.45, -0.78)],
                 [(wx - 0.55, -1.15), (wx + 0.55, -1.15)]]
    flowers = [circle(x, -1.6, 0.15, 12) for x in (-2.1, -1.6, -1.1, 1.1, 1.6, 2.1)]
    path = [[(-0.4, -2.0), (-1.0, -2.9)], [(0.4, -2.0), (1.0, -2.9)]]
    ground = [[(-3.0, -2.0), (-2.6, -2.0)], [(2.6, -2.0), (3.0, -2.0)]]
    return make("Thatched Irish Cottage", [walls, roof, eave] + chim + smoke + texture + door + wins + flowers + path + ground)


@design("stpatrick_castle_ruin", T)
def castle_ruin(rng):
    keep = poly((-1.0, -2.3), (-1.0, 1.2), (-0.8, 1.6), (-0.6, 1.3), (-0.4, 1.9), (-0.2, 1.65), (0.0, 2.1), (0.0, 2.45),
                (0.2, 2.45), (0.2, 2.2), (0.4, 2.2), (0.4, 2.45), (0.6, 2.45), (0.6, 2.2), (0.8, 2.2), (0.8, 2.45), (1.0, 2.45), (1.0, -2.3), closed=False)
    wall_r = poly((1.0, 0.2), (1.6, 0.2), (1.8, -0.2), (2.1, 0.0), (2.4, -0.7), (2.6, -0.5), (2.9, -2.3), closed=False)
    wall_l = poly((-1.0, -0.7), (-1.6, -0.7), (-1.9, -1.0), (-2.2, -0.9), (-2.5, -1.5), (-2.8, -2.3), closed=False)
    windows = [chain([(x - 0.12, y)], arc(x, y + 0.25, 0.12, math.pi, 0, 8)[1:-1], [(x + 0.12, y + 0.25), (x + 0.12, y), (x - 0.12, y)]) for x, y in [(-0.4, 0.6), (0.45, 0.9), (0.45, -0.3)]]
    door = chain([(-0.3, -2.3), (-0.3, -1.6)], arc(0, -1.6, 0.3, math.pi, 0, 12)[1:], [(0.3, -2.3)])
    arch = chain([(1.7, -2.3), (1.7, -1.3)], arc(2.0, -1.3, 0.3, math.pi, 0, 12)[1:], [(2.3, -2.3)])
    stones = [[(x, y), (x + 0.4, y)] for x, y in [(-0.8, 0.0), (0.3, 0.3), (-0.7, -1.0), (0.4, -1.4), (-0.6, 1.0), (1.2, -0.6), (-1.9, -1.6)]]
    vine = cubic((-1.0, -2.3), (-1.5, -1.0), (-0.7, -0.2), (-1.2, 1.0), 30)
    leaves = [lens(vine[i], (vine[i][0] + d * 0.35, vine[i][1] + 0.22), 0.35) for i, d in [(5, -1), (11, 1), (17, -1), (23, 1), (29, -1)]]
    hill = [[(-3.0, -2.3), (3.0, -2.3)]]
    birds = [chain(arc(x - 0.15, y, 0.15, math.radians(20), math.radians(160), 6)[::-1], arc(x + 0.15, y, 0.15, math.radians(20), math.radians(160), 6)[::-1])
             for x, y in [(2.0, 2.4), (2.6, 2.0), (-2.2, 2.2)]]
    birds = [chain(arc(x - 0.18, y, 0.18, math.radians(160), math.radians(20), 6), arc(x + 0.18, y, 0.18, math.radians(160), math.radians(20), 6))
             for x, y in [(2.0, 2.4), (2.6, 1.9), (-2.2, 2.2)]]
    return make("Ruined Irish Castle", [keep, wall_r, wall_l, door, arch, vine] + windows + stones + leaves + hill + birds)


@design("stpatrick_celtic_cross", T)
def celtic_cross(rng):
    cx, cy, w, h, R, r = 0.0, 1.2, 0.4, 0.4, 1.35, 1.0
    ao, bo = math.acos(w / R), math.asin(h / R)
    right = chain([(0, 2.95), (w, 2.95), (w, cy + R * math.sin(ao))], arc(cx, cy, R, ao, bo, 16)[1:], [(1.95, cy + h), (2.0, cy), (1.95, cy - h)],
                  [(cx + R * math.cos(bo), cy - h)], arc(cx, cy, R, -bo, -ao, 16)[1:], [(w, -1.9), (0.75, -1.9), (0.75, -2.4), (1.1, -2.4), (1.1, -2.85), (0, -2.85)])
    outline = chain(mirror_x(right)[::-1], right)
    holes = []
    ai, bi = math.acos(w / r), math.asin(h / r)
    q = chain([(w, cy + h), (w, cy + r * math.sin(ai))], arc(cx, cy, r, ai, bi, 12)[1:], [(w, cy + h)])
    for sx, sy in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
        holes.append([(sx * x, cy + sy * (y - cy)) for x, y in q])
    boss = [circle(cx, cy, 0.28, 24), circle(cx, cy, 0.12, 12)]
    panel = [rect(-0.25, -1.7, 0.25, 0.2)]
    knot = [zigzag(-0.15, 0.15, 0, 0.1, 1)]
    knot = [chain(*[[(0.18 * (1 if k % 2 else -1), 0.05 - 0.22 * k)] for k in range(9)])]
    arms = [circle(1.55, cy, 0.18, 14), circle(-1.55, cy, 0.18, 14), circle(0, 2.55, 0.18, 14)]
    grass = [zigzag(-2.6, -1.1, -2.85, 0.12, 6), zigzag(1.1, 2.6, -2.85, 0.12, 6)]
    clover = shamrock(-2.1, -2.0, 0.3, stem=0.8) + shamrock(2.1, -1.9, 0.3, stem=0.8, rot=0.2)
    return make("Celtic High Cross", [outline] + holes + boss + panel + knot + arms + grass + clover)


@design("stpatrick_round_tower", T)
def round_tower(rng):
    body = poly((-0.6, 1.8), (-0.78, -2.4), (0.78, -2.4), (0.6, 1.8), closed=False)
    cap = poly((-0.72, 1.8), (0, 3.1), (0.72, 1.8), (-0.72, 1.8))
    courses = [quad((-0.6 - 0.18 * (1.8 - y) / 4.2, y), (0, y - 0.1), (0.6 + 0.18 * (1.8 - y) / 4.2, y), 12) for y in (1.1, 0.2, -0.8, -1.7)]
    door = chain([(-0.2, -1.6), (-0.2, -0.95)], arc(0, -0.95, 0.2, math.pi, 0, 10)[1:], [(0.2, -1.6), (-0.2, -1.6)])
    wins = [rect(-0.08, 1.25, 0.08, 1.6), rect(-0.08, 0.4, 0.08, 0.75), rect(-0.08, -0.55, 0.08, -0.25)]
    ladder = [[(-0.25, -1.6), (-0.65, -2.4)], [(0.15, -1.6), (-0.25, -2.4)]] + [[(-0.33 - 0.1 * k, -1.76 - 0.2 * k), (0.07 - 0.1 * k, -1.76 - 0.2 * k)] for k in range(3)]
    church = poly((1.3, -2.4), (1.3, -0.6), (2.15, 0.6), (3.0, -0.6), (3.0, -2.4), closed=False)
    gable_w = chain([(2.0, -1.6), (2.0, -0.6)], [(2.15, -0.25), (2.3, -0.6), (2.3, -1.6), (2.0, -1.6)])
    broken = poly((1.3, -1.2), (0.78, -1.5), closed=False)
    ground = [[(-3.0, -2.4), (3.0, -2.4)]]
    stones = [rrect(-2.6 + 0.5 * k, -2.4, -2.2 + 0.5 * k, -2.1 - 0.06 * (k % 2), 0.08) for k in range(3)]
    birds = [chain(arc(x - 0.18, y, 0.18, math.radians(160), math.radians(20), 6), arc(x + 0.18, y, 0.18, math.radians(160), math.radians(20), 6))
             for x, y in [(1.5, 2.4), (2.2, 2.0), (-2.0, 2.6), (-1.5, 1.8)]]
    clover = shamrock(-2.0, -0.8, 0.35, stem=1.0)
    return make("Ancient Round Tower", [body, cap, door, church, gable_w, broken] + courses + wins + ladder + ground + stones + birds + clover)


@design("stpatrick_dublin_door", T)
def dublin_door(rng):
    door = rect(-0.85, -2.3, 0.85, 0.9)
    panels = [rect(x0, y0, x0 + 0.55, y0 + h) for x0 in (-0.7, 0.15) for y0, h in [(-2.1, 0.8), (-1.15, 0.6), (-0.4, 1.1)]]
    fan = [arc(0, 0.9, 0.85, 0, math.pi, 40), arc(0, 0.9, 0.3, 0, math.pi, 16)] + [[(0.3 * math.cos(a), 0.9 + 0.3 * math.sin(a)), (0.85 * math.cos(a), 0.9 + 0.85 * math.sin(a))]
                                                                                for a in [math.pi * k / 6 for k in range(1, 6)]]
    frame = chain([(-1.05, -2.3), (-1.05, 0.9)], arc(0, 0.9, 1.05, math.pi, 0, 40)[1:], [(1.05, -2.3)])
    cols = []
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 1.2, sx * 1.6))
        cols += [rect(x0, -2.3, x1, 1.0), rect(x0 - 0.08, 1.0, x1 + 0.08, 1.2), [(x0 + 0.13, -2.1), (x0 + 0.13, 0.8)], [(x1 - 0.13, -2.1), (x1 - 0.13, 0.8)]]
    lintel = poly((-1.8, 1.2), (-1.8, 1.45), (1.8, 1.45), (1.8, 1.2), closed=False)
    top = poly((-1.95, 1.45), (0, 2.5), (1.95, 1.45), closed=False)
    knocker = [circle(0, -0.55, 0.16, 14), circle(0, -0.3, 0.07, 8)]
    slot = [rect(-0.3, -1.4, 0.3, -1.25)]
    steps = [rect(-1.9, -2.6, 1.9, -2.3), rect(-2.2, -2.9, 2.2, -2.6)]
    pots = []
    for sx in (-1, 1):
        x = sx * 2.4
        pots += [poly((x - 0.35, -2.3), (x - 0.45, -1.6), (x + 0.45, -1.6), (x + 0.35, -2.3), closed=False)]
        pots += shamrock(x, -0.9, 0.3, stem=0.9)
    pots = [poly((x - 0.35, -2.6), (x - 0.45, -1.9), (x + 0.45, -1.9), (x + 0.35, -2.6), closed=False) for x in (-2.45, 2.45)]
    plants = shamrock(-2.45, -1.2, 0.3, stem=0.6) + shamrock(2.45, -1.2, 0.3, stem=0.6, rot=0.15)
    return make("Georgian Dublin Door", [door, frame, lintel, top] + panels + fan + cols + knocker + slot + steps + pots + plants)


@design("stpatrick_wishing_well", T)
def wishing_well(rng):
    rim = ellipse(0, -0.4, 1.8, 0.4, 80)
    inner = ellipse(0, -0.4, 1.45, 0.28, 60)
    base = chain([(-1.8, -0.4), (-1.8, -2.4)], quad((-1.8, -2.4), (0, -2.9), (1.8, -2.4), 30), [(1.8, -0.4)])
    rows = [quad((-1.8, y), (0, y - 0.45), (1.8, y), 30) for y in (-0.95, -1.5, -2.0)]
    joints = []
    for k, (y0, y1) in enumerate([(-0.4, -0.95), (-0.95, -1.5), (-1.5, -2.0), (-2.0, -2.4)]):
        for x in ([-1.2, 0.0, 1.2] if k % 2 == 0 else [-0.6, 0.6]):
            d = 0.45 * (1 - (x / 1.8) ** 2)
            joints.append([(x, y0 - d - 0.02 if k else y0 - 0.4 * (1 - (x / 1.8) ** 2) ** 0.5), (x, y1 - d + 0.02)])
    joints = hide(joints, inner)
    posts = [rect(-1.65, -0.5, -1.4, 1.9), rect(1.4, -0.5, 1.65, 1.9)]
    posts = hide(posts, poly(*rim[: len(rim) // 2 + 1]))
    roof = [poly((-2.3, 1.75), (0, 3.0), (2.3, 1.75)), [(-1.15, 2.37), (1.15, 2.37)]]
    axle = [[(-1.4, 1.1), (1.4, 1.1)], [(1.65, 1.1), (2.1, 1.1), (2.1, 0.6), (2.4, 0.6)]]
    rope = [[(0.2, 1.1), (0.2, 0.5)]]
    bucket = [poly((-0.2, 0.5), (-0.1, -0.15), (0.5, -0.15), (0.6, 0.5)), arc(0.2, 0.5, 0.4, 0, math.pi, 12)]
    clovers = shamrock(-2.4, -2.2, 0.32, stem=0.8) + shamrock(2.5, -2.3, 0.3, stem=0.8, rot=0.2) + shamrock(2.6, -0.8, 0.25, stem=0.8)
    coins = coin(-0.6, -0.42, 0.18, 0.4, mark=False)
    return make("Lucky Wishing Well", [rim, inner, base] + rows + joints + posts + roof + axle + rope + bucket + clovers)


@design("stpatrick_cliffs", T)
def cliffs(rng):
    heads = [((-3.0, 1.9), (-1.3, 1.65), (-1.05, -2.4)), ((-1.25, 1.05), (0.3, 0.85), (0.45, -1.3)),
             ((0.4, 0.55), (1.5, 0.42), (1.6, -0.55)), ((1.55, 0.25), (2.4, 0.2), (2.45, -0.05))]
    out = []
    for (x0, y0), (x1, y1), (x2, y2) in heads:
        top = smooth([(x0, y0), ((2 * x0 + x1) / 3, y0 + 0.12), ((x0 + 2 * x1) / 3, y1 + 0.05), (x1, y1)], 8)
        n = 7
        face = [(x1 + (x2 - x1) * k / n + (0.08 if k % 2 else -0.04) * (1 if 0 < k < n else 0), y1 + (y2 - y1) * k / n) for k in range(n + 1)]
        out.append(chain(top, face[1:]))
        depth = y1 - y2
        for k in ((1, 2, 3) if depth > 2 else (2,) if depth > 1 else ()):
            yy = y1 - depth * k / 4
            xx = x1 + (x2 - x1) * k / 4
            out.append(quad((xx, yy), (xx - 0.3, yy + 0.04), (xx - 0.6 + 0.1 * k, yy - 0.03), 8))
    horizon = [[(2.45, -0.05), (3.0, -0.05)]]
    tower = [poly((-2.5, 1.86), (-2.5, 2.55), (-2.55, 2.55), (-2.55, 2.8), (-2.4, 2.8), (-2.4, 2.67), (-2.25, 2.67), (-2.25, 2.8), (-2.1, 2.8),
                  (-2.1, 2.55), (-2.15, 2.55), (-2.15, 1.88), closed=False), rect(-2.38, 2.1, -2.27, 2.35)]
    stack = poly((0.9, -1.9), (1.0, -0.8), (1.15, -0.7), (1.3, -0.85), (1.4, -1.9), closed=False)
    waves = [wave(-1.0, 3.0, -2.55, 0.08, 6, 120), wave(-0.2, 3.0, -1.9, 0.07, 5, 90), wave(1.6, 3.0, -0.9, 0.05, 3, 50)]
    waves = hide(waves, poly((0.9, -1.9), (1.0, -0.8), (1.15, -0.7), (1.3, -0.85), (1.4, -1.9)))
    foam = [chain(*[arc(-0.9 + 0.3 * k, -2.4, 0.15, math.pi, 0, 6) for k in range(4)])]
    birds = [chain(arc(x - 0.18, y, 0.18, math.radians(160), math.radians(20), 6), arc(x + 0.18, y, 0.18, math.radians(160), math.radians(20), 6))
             for x, y in [(0.6, 2.3), (1.4, 2.7), (2.1, 1.9)]]
    grass = [zigzag(-1.9, -1.4, 1.75, 0.07, 3), zigzag(-0.7, -0.1, 1.05, 0.06, 3)]
    return make("Cliffs by the Wild Atlantic", out + horizon + tower + [stack] + waves + foam + birds + grass)


@design("stpatrick_parade_float", T)
def parade_float(rng):
    deck = rect(-2.9, -1.2, 2.9, -0.8)
    skirt = [chain(*[arc(-2.9 + 0.58 * (k + 0.5), -1.2, 0.29, math.pi, 2 * math.pi, 8) for k in range(10)])]
    wheels = [arc(x, -2.3, 0.45, math.radians(20), math.radians(160), 12) for x in (-1.8, 1.8)]
    wheels = [chain(arc(x, -2.1, 0.45, math.radians(0), math.radians(-180), 14)) for x in (-1.9, 1.9)]
    wheels = [arc(x, -2.05, 0.45, math.radians(-200), math.radians(20), 20) for x in (-1.9, 1.9)]
    hubs = [circle(x, -2.05, 0.15, 12) for x in (-1.9, 1.9)]
    hat = [poly((-1.95, -0.8), (-1.75, 1.0), (-0.25, 1.0), (-0.05, -0.8), closed=False), [(-1.9, -0.4), (-0.1, -0.4)], [(-1.85, 0.0), (-0.15, 0.0)],
           rect(-1.3, -0.5, -0.7, 0.1), ellipse(-1.0, 1.0, 0.75, 0.13, 30)]
    hat[0] = poly((-1.92, -0.55), (-1.75, 1.0), (-0.25, 1.0), (-0.08, -0.55), closed=False)
    hat.append(ellipse(-1.0, -0.6, 1.35, 0.17, 50))
    big = shamrock(1.3, 0.6, 0.7, stem=1.1, veins=True)
    balloons = []
    for x, y in [(-2.6, 2.3), (-0.4, 2.6), (2.7, 2.4)]:
        balloons += [ellipse(x, y, 0.35, 0.45, 24), poly((x - 0.08, y - 0.5), (x, y - 0.45), (x + 0.08, y - 0.5), closed=False),
                     cubic((x, y - 0.5), (x + 0.2, y - 1.2), (x - 0.2, y - 1.8), (x * 0.6, -0.8), 20)]
    balloons = hide(balloons, poly((-1.92, -0.55), (-1.75, 1.0), (-0.25, 1.0), (-0.08, -0.55)), *big[0:6:2])
    return make("St. Patrick's Parade Float", [deck] + skirt + wheels + hubs + hat + big + balloons)


@design("stpatrick_claddagh", T)
def claddagh(rng):
    hrt = heart(0, 0, 1.3, 160)
    crown = poly((-0.9, 0.8), (-1.1, 2.0), (-0.55, 1.5), (0, 2.35), (0.55, 1.5), (1.1, 2.0), (0.9, 0.8))
    band_l = [[(-0.96, 1.15), (0.96, 1.15)]]
    balls = [circle(x, y, 0.13, 12) for x, y in [(-1.13, 2.13), (0, 2.48), (1.13, 2.13)]]
    jewel = [poly((0, 0.85), (0.15, 1.0), (0, 1.12), (-0.15, 1.0))]
    fingers, palm = [], []
    for sx in (-1, 1):
        fs = [rrect(-1.8, y - 0.16, x1, y + 0.16, 0.16) for y, x1 in [(0.5, -0.8), (0.15, -0.6), (-0.2, -0.65), (-0.55, -0.85)]]
        back = chain(cubic((-1.8, 0.62), (-2.3, 0.6), (-2.25, -0.4), (-2.1, -1.2), 20), [(-2.07, -1.65)])
        under = chain(quad((-1.75, -0.7), (-1.6, -1.0), (-1.62, -1.25), 10), [(-1.69, -1.52)])
        thumb = chain(quad((-1.8, 0.62), (-1.3, 0.95), (-0.75, 0.75), 10))
        cuff = [[(-2.1, -1.2), (-1.62, -1.15)], [(-2.08, -1.4), (-1.65, -1.38)]]
        if sx > 0:
            fs = mirror_all(fs)
            back, under, thumb = mirror_x(back), mirror_x(under), mirror_x(thumb)
            cuff = mirror_all(cuff)
        fingers += fs
        palm += [back, under, thumb] + cuff
    ring = [chain(arc(0, -0.9, 2.2, math.radians(200), math.radians(340), 60)), chain(arc(0, -0.9, 1.81, math.radians(200), math.radians(340), 60))]
    ring[1] = arc(0, -0.9, 1.81, math.radians(204), math.radians(336), 60)
    heart_parts = hide([hrt], crown, *fingers)
    return make("Claddagh Ring", heart_parts + [crown] + band_l + balls + jewel + fingers + palm + ring + [sparkle(2.4, 2.2, 0.3), sparkle(-2.4, 2.2, 0.3)])


@design("stpatrick_wolfhound", T)
def wolfhound(rng):
    torso = smooth([(2.15, 0.15), (1.6, -0.75), (0.2, -0.5), (-0.9, -0.35), (-1.85, -0.55), (-2.15, 0.15), (-1.0, 0.68), (1.2, 0.72), (1.85, 0.6)], 8, closed=True)
    neck = tube([(1.55, 0.35), (1.85, 1.0), (2.15, 1.55)], 0.8, cap=True)
    head = smooth([(1.85, 1.85), (2.3, 2.08), (2.7, 1.92), (3.15, 1.72), (3.22, 1.5), (3.0, 1.3), (2.4, 1.22), (1.95, 1.4)], 8, closed=True)
    legs_near = [tube([(1.35, -0.2), (1.4, -1.4), (1.45, -2.45)], lambda t: 0.5 - 0.22 * t), tube([(-1.6, 0.0), (-1.2, -1.0), (-1.7, -1.75), (-1.55, -2.45)], lambda t: 0.8 - 0.52 * t)]
    legs_far = [tube([(0.95, -0.3), (0.9, -1.4), (0.85, -2.45)], lambda t: 0.5 - 0.22 * t), tube([(-1.0, -0.2), (-0.75, -1.0), (-1.1, -1.85), (-1.0, -2.45)], lambda t: 0.6 - 0.32 * t)]
    paws = [ellipse(1.62, -2.48, 0.3, 0.13, 20), ellipse(-1.38, -2.48, 0.3, 0.13, 20)]
    paws_far = [ellipse(1.02, -2.48, 0.28, 0.12, 20), ellipse(-0.83, -2.48, 0.28, 0.12, 20)]
    tail = tube([(-2.0, 0.25), (-2.5, -0.4), (-2.65, -1.3), (-2.4, -1.95)], lambda t: 0.28 - 0.18 * t)
    front = [torso, neck, head, tail] + legs_near + paws
    out = []
    for i, sh in enumerate(front):
        for piece in hide([sh], *[o for j, o in enumerate(front) if j != i]):
            L = sum(math.dist(a, b) for a, b in zip(piece, piece[1:]))
            out.append(bumpy(piece, 0.07, max(1, int(L / 0.22))) if i in (0, 1, 3) and L > 0.4 else piece)
    out += hide(legs_far + paws_far, *front)
    beard = [bumpy(quad((3.05, 1.32), (2.8, 1.0), (2.45, 1.15), 10), 0.08, 3)]
    tufts = [poly((x, y), (x + 0.12, y + 0.18), (x + 0.2, y), closed=False) for x, y in [(-0.4, 0.62), (0.4, 0.62), (2.5, 2.0)]]
    ear = [lens((2.1, 1.95), (1.65, 1.68), 0.35)]
    nose = [circle(3.15, 1.55, 0.08, 10)]
    thigh = [quad((-1.85, 0.0), (-1.3, 0.35), (-1.0, -0.3), 10)]
    collar = [[(1.55, 0.98), (2.18, 0.72)], [(1.68, 1.2), (2.3, 0.94)]]
    ground = [[(-3.0, -2.62), (3.0, -2.62)]]
    clover = shamrock(-0.2, -1.6, 0.3, stem=1.6) + shamrock(2.5, -1.6, 0.3, stem=1.7, rot=-0.2)
    return make("Irish Wolfhound", out + beard + tufts + ear + nose + thigh + collar + ground + clover, [eye(2.55, 1.7, 0.07)])


def sheep(cx, cy, s, flip=False):
    body = bumpy(ellipse(0, 0, 1.5, 0.9, 120), 0.16, 16)
    head = ellipse(1.45, 0.15, 0.35, 0.52, 40, rot=-0.5)
    ears = [lens((1.15, 0.5), (0.75, 0.75), 0.3), lens((1.55, 0.62), (1.85, 0.95), 0.3)]
    legs = [leg(x, x + 0.22, -0.7, -1.8) for x in (-1.0, -0.6, 0.5, 0.9)]
    tail = [circle(-1.7, 0.2, 0.15, 12)]
    parts = hide([body] + tail, head) + hide(ears, head) + [head] + hide(legs, body)
    if flip:
        parts = mirror_all(parts)
    return [transform(p, dx=cx, dy=cy, s=s) for p in parts], (cx + (-1 if flip else 1) * 1.5 * s, cy + 0.25 * s)


@design("stpatrick_sheep_hills", T)
def sheep_hills(rng):
    big, e1 = sheep(-0.5, -1.0, 1.0)
    small, e2 = sheep(1.6, 0.9, 0.45, flip=True)
    hill_back = smooth([(-3.0, 1.0), (-1.6, 1.7), (-0.2, 1.25), (1.2, 1.6), (3.0, 1.0)], 10)
    hill_mid = smooth([(-3.0, 0.1), (-1.0, 0.6), (1.0, 0.3), (3.0, 0.5)], 10)
    posts, rails = [], []
    top = [(x, y + 0.55) for x, y in hill_mid]
    mid = [(x, y + 0.3) for x, y in hill_mid]
    rails = [top, mid]
    for k in range(0, len(hill_mid), 6):
        x, y = hill_mid[k]
        posts.append(rect(x - 0.06, y, x + 0.06, y + 0.68))
    rails = hide(rails, *posts)
    back = hide([hill_back, hill_mid] + rails + posts, *[small[0]], *big[:1])
    ground = [wave(-3.0, 3.0, -2.85, 0.06, 7, 100)]
    clovers = shamrock(2.3, -2.2, 0.3, stem=0.9) + shamrock(-2.6, -2.3, 0.25, stem=0.9)
    sun = [circle(-2.3, 2.5, 0.4, 30)]
    return make("Sheep on the Green Hills", big + small + back + ground + clovers + sun, [eye(*e1, 0.06), eye(*e2, 0.04)])


@design("stpatrick_rainbow_fields", T)
def rainbow_fields(rng):
    hills = smooth([(-3.0, -0.4), (-1.8, 0.3), (-0.6, -0.1), (0.8, 0.4), (2.0, 0.0), (3.0, 0.2)], 10)
    hill_poly = hills + [(3.0, -3.0), (-3.0, -3.0)]
    bows = hide([arc(0.2, -0.6, r, math.radians(5), math.radians(175), 60) for r in (2.0, 2.4, 2.8, 3.2)], hill_poly)
    hedges = [smooth([(-3.0, -1.2), (-1.0, -0.8), (1.0, -1.1), (3.0, -0.7)], 8), smooth([(-1.2, 0.05), (-1.6, -1.0), (-2.2, -2.2), (-2.6, -3.0)], 8),
              smooth([(1.4, 0.2), (1.2, -0.9), (2.0, -1.9), (2.4, -3.0)], 8), smooth([(-1.9, -2.0), (0.0, -1.7), (2.0, -1.9)], 8)]
    hedges = [bumpy(h, 0.07, int(len(h) / 6)) for h in hedges]
    river = [smooth([(0.2, -0.05), (0.0, -0.8), (0.6, -1.5), (-0.2, -2.3), (0.2, -3.0)], 8), smooth([(0.35, -0.05), (0.35, -0.8), (1.1, -1.5), (0.5, -2.3), (1.0, -3.0)], 8)]
    hedges = hide(hedges, chain(river[0], river[1][::-1]))
    trees = []
    for x, y in [(-2.4, -0.55), (2.5, -0.35), (-0.6, -0.45)]:
        trees += [[(x, y - 0.4), (x, y)], bumpy(circle(x, y + 0.25, 0.28, 40), 0.06, 6)]
    clouds = [cloud(-2.1, 1.6, 0.8), cloud(2.3, 1.7, 0.7)]
    bows = hide(bows, *clouds)
    return make("Rainbow over Patchwork Fields", [hills] + bows + hedges + river + trees + clouds)


@design("stpatrick_clover_magnifier", T)
def clover_magnifier(rng):
    lens_c = (0.3, 0.5)
    rim = [circle(*lens_c, 1.7, 120), circle(*lens_c, 1.5, 110)]
    handle = tube([(1.5, -0.7), (2.8, -2.0)], 0.45, cap=True)
    handle = hide([handle], circle(*lens_c, 1.7, 80))
    small = []
    for x, y, s, r in [(-2.4, -0.6, 0.35, 0.2), (-1.9, -2.1, 0.4, -0.2), (-0.7, -1.8, 0.3, 0.1), (0.6, -2.3, 0.35, -0.3), (2.5, 0.3, 0.32, 0.3),
                       (-2.5, 1.8, 0.3, -0.1), (2.3, 2.3, 0.3, 0.2), (-1.2, 2.6, 0.28, 0.0), (2.6, -0.9, 0.25, 0.0)]:
        small += shamrock(x, y, s, rot=r, stem=1.2)
    small = hide(small, circle(*lens_c, 1.72, 90), handle[0] if handle else [])
    big = shamrock(lens_c[0], lens_c[1] + 0.05, 0.6, leaves=4, stem=0.0, veins=True)
    big_stem = [quad((lens_c[0], lens_c[1]), (lens_c[0] + 0.2, lens_c[1] - 0.8), (lens_c[0] - 0.2, lens_c[1] - 1.45), 12)]
    grass = [zigzag(-3.0, 3.0, -2.9, 0.12, 20)]
    grass = hide(grass, *handle)
    return make("Finding the Four-Leaf Clover", rim + handle + small + big + big_stem + grass + [sparkle(-0.9, 1.5, 0.15)])


@design("stpatrick_bouquet", T)
def bouquet(rng):
    heads = [(-1.4, 1.5, 0.45, 0.4), (0.0, 2.1, 0.5, 0.0), (1.4, 1.5, 0.45, -0.4), (-0.75, 0.6, 0.42, 0.2), (0.75, 0.6, 0.42, -0.2), (-2.0, 0.3, 0.35, 0.7), (2.0, 0.3, 0.35, -0.7)]
    clovers, stems, covers = [], [], []
    for x, y, s, r in heads:
        sh = shamrock(x, y, s, rot=r, stem=0.0)
        clovers += sh
        covers += sh
        stems.append(quad((x, y), ((x + 0.0) * 0.5, (y - 1.0) * 0.6), (0.0, -1.2), 12))
    cone = poly((-1.7, -0.3), (0, -2.9), (1.7, -0.3))
    cone_top = [chain(*[arc(-1.7 + 0.425 * (k + 0.5), -0.3, 0.2125, math.pi, 0, 8) for k in range(8)])]
    stems = hide(stems, cone, *covers)
    clovers = hide(clovers, cone)
    folds = [[(-0.6, -0.3), (-0.15, -2.2)], [(0.7, -0.3), (0.2, -2.3)]]
    bx, by = 0.0, -1.5
    bow = [lens((bx, by), (bx - 1.0, by + 0.5), 0.35), lens((bx, by), (bx + 1.0, by + 0.5), 0.35), circle(bx, by, 0.16, 14),
           poly((bx - 0.1, by - 0.12), (bx - 0.7, by - 1.1), (bx - 0.45, by - 0.95), (bx - 0.4, by - 1.25), (bx + 0.03, by - 0.16), closed=False),
           poly((bx + 0.1, by - 0.12), (bx + 0.7, by - 1.1), (bx + 0.45, by - 0.95), (bx + 0.4, by - 1.25), (bx - 0.03, by - 0.16), closed=False)]
    under_bow = hide([cone] + folds, *bow[:3])
    return make("Shamrock Bouquet", clovers + stems + under_bow + cone_top + bow)


@design("stpatrick_clover_wreath", T)
def clover_wreath(rng):
    leaves = []
    covers = []
    for k in range(12):
        a = math.pi / 2 + TAU * k / 12
        x, y = 1.9 * math.cos(a), 1.9 * math.sin(a)
        if k == 6 or k % 2:
            continue
        sh = shamrock(x, y, 0.5, rot=a - math.pi / 2 + (0.5 if k % 2 else -0.5), stem=0.0)
        leaves += sh
        covers += sh
    rings = hide([circle(0, 0, 1.6, 100), circle(0, 0, 2.2, 120)], *covers)
    bx, by = 0.0, -1.9
    bow = [lens((bx, by), (bx - 1.1, by + 0.45), 0.4), lens((bx, by), (bx + 1.1, by + 0.45), 0.4), circle(bx, by, 0.2, 16),
           poly((bx - 0.12, by - 0.15), (bx - 0.6, by - 1.05), (bx - 0.35, by - 0.9), (bx - 0.3, by - 1.15), (bx + 0.05, by - 0.2), closed=False),
           poly((bx + 0.12, by - 0.15), (bx + 0.6, by - 1.05), (bx + 0.35, by - 0.9), (bx + 0.3, by - 1.15), (bx - 0.05, by - 0.2), closed=False)]
    rings = hide(rings, *bow[:3])
    center = shamrock(0, 0.25, 0.5, stem=0.8, leaves=4, veins=True)
    return make("Shamrock Wreath", leaves + rings + bow + center)


@design("stpatrick_cocoa_mug", T)
def cocoa_mug(rng):
    body = chain([(-1.8, 0.8), (-1.8, -1.95)], quad((-1.8, -2.3), (-1.8, -2.3), (-1.45, -2.3), 6)[1:], [(1.05, -2.3)],
                 quad((1.05, -2.3), (1.4, -2.3), (1.4, -1.95), 6)[1:], [(1.4, 0.8)])
    rim = ellipse(-0.2, 0.8, 1.6, 0.3, 60)
    cocoa = ellipse(-0.2, 0.75, 1.35, 0.2, 50)
    marsh = [rrect(-1.0, 0.6, -0.55, 0.95, 0.08), rrect(-0.35, 0.65, 0.1, 1.0, 0.08), rrect(0.3, 0.6, 0.75, 0.92, 0.08)]
    cocoa = hide([cocoa], *marsh)
    handle = [arc(1.4, -0.6, 0.95, math.radians(80), math.radians(-80), 30), arc(1.4, -0.6, 0.6, math.radians(70), math.radians(-70), 26)]
    clover = shamrock(-0.2, -0.8, 0.6, stem=0.8, veins=True)
    steam = [cubic((x, 1.25), (x + 0.4, 1.7), (x - 0.4, 2.1), (x, 2.6), 20) for x in (-0.9, -0.2, 0.5)]
    saucer = [ellipse(-0.2, -2.35, 2.6, 0.45, 80)]
    saucer = hide(saucer, poly((-1.8, 0.8), (-1.8, -2.3), (1.4, -2.3), (1.4, 0.8)))
    return make("Shamrock Cocoa Mug", [body, rim] + cocoa + marsh + handle + clover + steam + saucer)


@design("stpatrick_triskele", T)
def triskele(rng):
    out = []
    for k in range(3):
        a = math.pi / 2 + k * TAU / 3
        cx, cy = 1.25 * math.cos(a), 1.25 * math.sin(a)
        turns = 1.75
        rot = a + math.pi - TAU * turns
        out.append(spiral(cx, cy, 0.0, 1.0, turns, 160, rot=rot))
        out.append(spiral(cx, cy, 0.0, 1.0, turns + 0.5, 180, rot=a - TAU * (turns + 0.5)))
    rings = [circle(0, 0, 0.25, 24), circle(0, 0, 2.25, 140), circle(0, 0, 2.6, 150)]
    dots = [eye(2.43 * math.cos(t), 2.43 * math.sin(t), 0.06) for t in [TAU * k / 30 for k in range(30)]]
    return make("Celtic Triskele", out + rings, dots)


@design("stpatrick_star_knot", T)
def star_knot(rng):
    def r_(t, d):
        return 1.55 + 1.05 * math.cos(2.5 * t) + d
    outer = polar(lambda t: r_(t, 0.17), t0=0.0, t1=2 * TAU, n=900, rot=math.pi / 2)
    inner = polar(lambda t: r_(t, -0.17), t0=0.0, t1=2 * TAU, n=900, rot=math.pi / 2)
    border = [circle(0, 0, 2.95, 160)]
    centre = shamrock(0, 0.05, 0.28, stem=0.0)
    return make("Celtic Star Knot", [outer, inner] + border + centre)


@design("stpatrick_aran_sweater", T)
def aran_sweater(rng):
    half = [(0.0, -2.7), (1.5, -2.7), (1.55, 0.9), (2.3, -1.5), (2.9, -1.2), (1.6, 2.2), (0.6, 2.4)]
    outline = chain(half, [(x, y) for x, y in mirror_x(half)[::-1]])
    outline = chain([(0.6, 2.4)], half[::-1][1:], mirror_x(half)[1:], [(-0.6, 2.4)])
    collar = [arc(0, 2.5, 0.6, math.pi, 2 * math.pi, 30), arc(0, 2.5, 0.38, math.pi, 2 * math.pi, 24)]
    hem = [[(-1.5, -2.3), (1.5, -2.3)]] + [[(x, -2.68), (x, -2.32)] for x in [-1.25 + 0.25 * k for k in range(11)]]
    cuffs = []
    for sx in (-1, 1):
        a, b = (sx * 2.15, -1.08), (sx * 2.72, -0.8)
        cuffs.append([a, b])
        for k in range(1, 4):
            t = k / 4
            p = (sx * 2.3 + (sx * 2.9 - sx * 2.3) * t, -1.5 + 0.3 * t)
            q = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            cuffs.append([p, q])
    cables = []
    for x0 in (-0.95, 0.95):
        cables += [[(x0 - 0.32, -2.3), (x0 - 0.32, 1.9)], [(x0 + 0.32, -2.3), (x0 + 0.32, 1.9)]]
        cables += [[(x0 + 0.2 * math.sin(TAU * (y + 2.2) / 0.9 + ph), y) for y in [-2.2 + 4.0 * i / 120 for i in range(121)]] for ph in (0, math.pi)]
    lattice = [zigzag(-0.6, 0.6, 0, 0.0, 1)]
    diamonds = []
    for k in range(4):
        y = -1.7 + 1.0 * k
        diamonds.append(poly((0, y - 0.45), (0.45, y), (0, y + 0.45), (-0.45, y)))
        diamonds.append(circle(0, y, 0.1, 10))
    sleeve = []
    for sx in (-1, 1):
        sleeve.append([(sx * (1.75 + 0.85 * t) + 0.1 * math.sin(TAU * 4 * t), 1.6 - 2.7 * t) for t in [i / 80 for i in range(81)]])
    return make("Aran Knit Sweater", [outline] + collar + hem + cuffs + cables + diamonds + sleeve)


@design("stpatrick_puffin", T)
def puffin(rng):
    head = circle(0.2, 1.3, 0.75, 70)
    beak = poly((0.85, 1.68), (1.5, 1.45), (1.9, 1.02), (1.55, 0.98), (0.85, 0.88))
    stripes = [quad((1.15, 1.6), (1.22, 1.25), (1.12, 0.92), 8), quad((1.42, 1.5), (1.5, 1.25), (1.4, 0.98), 8)]
    face = [chain(arc(0.45, 1.25, 0.42, math.radians(80), math.radians(260), 20))]
    body = smooth([(-0.4, 0.75), (-1.2, 0.2), (-1.5, -0.8), (-1.75, -1.7), (-1.1, -1.75), (0.3, -1.85), (0.95, -1.1), (1.0, -0.2), (0.7, 0.7)], 8)
    wing = lens((-0.2, 0.4), (-1.45, -1.45), 0.25)
    feet = [[(-0.2, -1.8), (-0.2, -2.25)], [(0.3, -1.8), (0.3, -2.25)],
            poly((-0.2, -2.25), (-0.6, -2.5), (0.15, -2.5)), poly((0.3, -2.25), (-0.05, -2.5), (0.75, -2.5))]
    rock = smooth([(-2.8, -3.0), (-2.5, -2.5), (-1.0, -2.5), (1.0, -2.5), (2.4, -2.6), (2.9, -3.0)], 8)
    hat_c = poly((-0.45, 2.0), (-0.3, 2.85), (0.45, 2.85), (0.6, 2.0), closed=False)
    brim = ellipse(0.08, 1.95, 1.05, 0.16, 40)
    hat = [hat_c, brim, [(-0.4, 2.25), (0.56, 2.25)], [(-0.36, 2.45), (0.53, 2.45)], rect(-0.05, 2.18, 0.2, 2.52)]
    head_v = hide([head], brim, poly((-0.45, 2.0), (-0.3, 2.85), (0.45, 2.85), (0.6, 2.0)), beak)
    body = hide([body], head)
    clover = shamrock(2.2, 0.0, 0.4, stem=1.0, veins=True)
    waves = [wave(1.2, 3.0, -2.25, 0.06, 3, 40)]
    return make("Puffin in a Leprechaun Hat", head_v + [beak] + stripes + face + body + [wing] + feet + [rock] + hat + clover,
                [eye(0.5, 1.45, 0.08)])


@design("stpatrick_teapot", T)
def teapot(rng):
    body = chain([(-2.2, 0.4)], cubic((-2.2, 0.4), (-2.8, -0.6), (-2.3, -1.9), (-1.6, -2.0), 20), [(0.4, -2.0)],
                 cubic((0.4, -2.0), (1.1, -1.9), (1.6, -0.6), (1.0, 0.4), 20))
    rim = ellipse(-0.6, 0.4, 1.6, 0.25, 60)
    lid = [cubic((-1.75, 0.6), (-1.5, 1.6), (0.3, 1.6), (0.55, 0.6), 30), [(-0.75, 1.35), (-0.75, 1.6)], [(-0.45, 1.35), (-0.45, 1.6)]]
    knob = circle(-0.6, 1.8, 0.22, 16)
    spout = [cubic((-2.55, -0.4), (-3.1, -0.5), (-3.1, 0.6), (-3.4, 1.0), 20), cubic((-2.45, -1.1), (-3.5, -1.0), (-3.5, 0.6), (-3.75, 0.9), 20),
             [(-3.4, 1.0), (-3.75, 0.9)]]
    handle = [arc(1.1, -0.65, 0.95, math.radians(90), math.radians(-80), 30), arc(1.1, -0.65, 0.6, math.radians(80), math.radians(-70), 24)]
    handle = hide(handle, chain(body, [(-2.2, 0.4)]))
    clovers = shamrock(-0.6, -0.9, 0.45, stem=0.0, veins=True) + shamrock(-1.8, -0.5, 0.22, stem=0.0, rot=0.4) + shamrock(0.6, -0.5, 0.22, stem=0.0, rot=-0.4)
    band = [quad((-2.45, -1.6), (-0.6, -1.85), (1.25, -1.6), 20)]
    cup = [chain(cubic((1.6, -1.7), (1.65, -2.7), (2.95, -2.7), (3.0, -1.7), 20)),
           ellipse(2.3, -1.7, 0.7, 0.14, 30), arc(3.0, -2.0, 0.25, math.radians(90), math.radians(-90), 10), ellipse(2.3, -2.65, 1.0, 0.2, 40)]
    steam = [cubic((-3.6, 1.2), (-3.2, 1.6), (-3.9, 2.0), (-3.5, 2.5), 16), cubic((2.2, -1.4), (2.5, -1.0), (2.0, -0.7), (2.3, -0.3), 12)]
    return make("Shamrock Teapot and Cup", [body, rim, knob] + lid + spout + handle + clovers + band + cup + steam)


@design("stpatrick_soda_bread", T)
def soda_bread(rng):
    loaf = chain(cubic((-2.4, -0.9), (-2.5, 1.0), (-1.2, 1.6), (0, 1.6), 30), cubic((0, 1.6), (1.2, 1.6), (2.5, 1.0), (2.4, -0.9), 30))
    base = quad((2.4, -0.9), (0, -1.3), (-2.4, -0.9), 30)
    cut1 = [quad((-2.2, 0.0), (0, 1.0), (2.2, 0.0), 30), quad((-2.15, -0.25), (0, 0.72), (2.15, -0.25), 30)]
    cut2 = [quad((-0.15, 1.58), (-0.25, 0.5), (-0.1, -1.08), 20), quad((0.18, 1.58), (0.15, 0.5), (0.3, -1.06), 20)]
    cut2 = hide(cut2, chain(cut1[0], cut1[1][::-1]))
    board = [ellipse(0, -1.15, 3.0, 0.8, 120), arc(0, -1.4, 3.0, math.radians(180), math.radians(360), 60)]
    board[1] = chain([(-3.0, -1.15)], ellipse(0, -1.4, 3.0, 0.8, 120)[60:121], [(3.0, -1.15)])
    board = hide(board, chain(loaf, base))
    knife = [poly((-2.2, -1.75), (-0.4, -1.55), (-0.4, -1.8), (-2.0, -1.95)), rrect(-0.4, -1.83, 0.9, -1.52, 0.12)]
    knife = [transform(p, dx=0.3, dy=-0.05, rot=0.0) for p in knife]
    crumbs = [circle(x, y, 0.07, 8) for x, y in [(1.4, -1.7), (1.7, -1.55), (2.0, -1.75)]]
    clover = shamrock(-2.2, 2.3, 0.38, stem=0.9, rot=0.2) + shamrock(2.2, 2.3, 0.38, stem=0.9, rot=-0.2)
    flour = [eye(x, y, 0.05) for x, y in [(-1.2, 0.9), (-0.8, 1.2), (0.9, 1.1), (1.4, 0.6), (-1.6, 0.4), (0.6, 0.0), (-0.9, -0.4), (1.2, -0.5)]]
    return make("Irish Soda Bread", [loaf, base] + cut1 + cut2 + board + knife + crumbs + clover, flour)


@design("stpatrick_potted_shamrock", T)
def potted_shamrock(rng):
    pot = poly((-1.4, -0.6), (-1.1, -2.9), (1.1, -2.9), (1.4, -0.6), closed=False)
    rim = rect(-1.65, -0.6, 1.65, 0.0)
    soil = [quad((-1.5, 0.0), (0, 0.25), (1.5, 0.0), 12)]
    heads = [(-1.6, 1.3, 0.42, 0.5), (-0.6, 2.2, 0.45, 0.2), (0.7, 2.4, 0.45, -0.1), (1.7, 1.4, 0.4, -0.5), (0.0, 1.1, 0.4, 0.0), (-2.4, 0.4, 0.35, 0.9),
             (2.4, 0.5, 0.35, -0.9)]
    clovers, stems = [], []
    for x, y, s, r in heads:
        sh = shamrock(x, y, s, rot=r, stem=0.0)
        clovers += sh
        stems.append(quad((x, y), (x * 0.5, y * 0.4), (x * 0.25, 0.1), 12))
    stems = hide(stems, *[c for c in clovers])
    tag = [heart(2.3, -1.9, 0.45, 60), [(1.4, -1.6), (1.95, -1.75)]]
    return make("Potted Shamrock Plant", [pot, rim] + soil + clovers + stems)


@design("stpatrick_mandala", T)
def mandala(rng):
    out = shamrock(0, 0, 0.42, stem=0.0, veins=True)
    out += [circle(0, 0, 1.0, 80), circle(0, 0, 1.2, 90)]
    for k in range(8):
        a = math.pi / 2 + TAU * k / 8
        out.append(leaf(1.2 * math.cos(a), 1.2 * math.sin(a), 0.34, a))
    out.append(circle(0, 0, 2.05, 130))
    out.append(polar(lambda t: 2.75 + 0.18 * math.cos(16 * t), n=600))
    for k in range(16):
        a = math.pi / 2 + TAU * k / 16
        out.append(circle(2.4 * math.cos(a), 2.4 * math.sin(a), 0.14, 12))
    hints = [eye(1.6 * math.cos(a), 1.6 * math.sin(a), 0.07) for a in [math.pi / 2 + TAU * (k + 0.5) / 8 for k in range(8)]]
    return make("Shamrock Mandala", out, hints)


@design("stpatrick_cupcake", T)
def cupcake(rng):
    liner = poly((-1.6, -0.5), (-1.2, -2.8), (1.2, -2.8), (1.6, -0.5), closed=False)
    pleats = [[(x, -0.6), (x * 0.75, -2.7)] for x in (-1.0, -0.5, 0.0, 0.5, 1.0)]
    tiers = [bumpy([(1.8, -0.5), (-1.8, -0.5)], 0.28, 6), bumpy([(1.4, 0.4), (-1.4, 0.4)], 0.24, 5), bumpy([(0.9, 1.2), (-0.9, 1.2)], 0.22, 4)]
    sides = [quad((-1.8, -0.5), (-1.95, -0.1), (-1.4, 0.4), 8), quad((1.8, -0.5), (1.95, -0.1), (1.4, 0.4), 8),
             quad((-1.4, 0.4), (-1.45, 0.8), (-0.9, 1.2), 8), quad((1.4, 0.4), (1.45, 0.8), (0.9, 1.2), 8),
             quad((-0.9, 1.2), (-0.6, 2.0), (0.0, 2.1), 8), quad((0.9, 1.2), (0.6, 2.0), (0.0, 2.1), 8)]
    tip = [quad((0.0, 2.1), (0.3, 2.3), (0.1, 2.5), 6)]
    pick = [[(0.6, 1.6), (1.3, 2.4)]] + shamrock(1.55, 2.65, 0.32, rot=-0.6, stem=0.0)
    pick = hide(pick, chain(sides[4], sides[5][::-1]))
    coin_ = coin(-0.8, 0.95, 0.38)
    sprinkles = [eye(x, y, 0.06) for x, y in [(-1.0, -0.2), (0.3, -0.1), (1.0, -0.15), (-0.4, 0.65), (0.6, 0.7), (0.2, 1.5)]]
    return make("Shamrock Cupcake", [liner] + pleats + tiers + sides + tip + pick + coin_, sprinkles)
