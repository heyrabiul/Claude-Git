"""Fourth of July niche, part 2 (pictures 10-55)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "patriotic"


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


def keep(strokes, shape):
    """Keep only the parts of `strokes` inside the closed `shape`."""
    t = inside(shape)
    out = []
    for s in strokes:
        cur = []
        for p in densify(s):
            if t(*p):
                cur.append(p)
            else:
                if len(cur) > 1:
                    out.append(cur)
                cur = []
        if len(cur) > 1:
            out.append(cur)
    return out


def sparkle(x, y, r):
    return star(x, y, r, 4, 0.3)


def flag(x0, y0, w, h, amp=0.12, waves=1.0, stripes=7, srows=2, scols=3, phase=0.0):
    """Waving stars-and-stripes flag; (x0, y0) is the top-left corner."""
    n = 48

    def top(t):
        return (x0 + w * t, y0 + amp * math.sin(TAU * waves * t + phase))
    tops = [top(i / n) for i in range(n + 1)]
    out = [chain(tops, [(x, y - h) for x, y in tops[::-1]], [tops[0]])]
    cw, crows = 0.42, (stripes + 1) // 2
    ci = int(round(n * cw))
    ch = h * crows / stripes
    for k in range(1, stripes):
        d = h * k / stripes
        start = ci if k <= crows else 0
        if k == crows:
            start = 0
        out.append([(x, y - d) for x, y in tops[start:]])
    if crows >= stripes:
        out.append([(x, y - ch) for x, y in tops[:ci + 1]])
    out.append([tops[ci], (tops[ci][0], tops[ci][1] - ch)])
    r = min(cw * w / scols, ch / srows) * 0.36
    for i in range(scols):
        for j in range(srows):
            tx, ty = top((i + 0.5) / scols * cw)
            out.append(star(tx, ty - ch * (j + 0.5) / srows, r))
    return out


def burst(cx, cy, r, n=12, inner=0.3):
    out = [[(cx + inner * r * math.cos(a), cy + inner * r * math.sin(a)), (cx + r * math.cos(a), cy + r * math.sin(a))]
           for a in [TAU * k / n for k in range(n)]]
    return out


def bird(x, y, s=0.18):
    return chain(arc(x - s, y, s, math.radians(160), math.radians(20), 6), arc(x + s, y, s, math.radians(160), math.radians(20), 6))


def stars_(*pts):
    return [star(x, y, r) for x, y, r in pts]


@design("patriotic_liberty_head", T)
def liberty_head(rng):
    band_o = arc(0, 0.35, 1.45, math.radians(15), math.radians(165), 50)
    band_i = arc(0, 0.35, 1.12, math.radians(165), math.radians(15), 40)
    band = chain(band_o, band_i, [band_o[0]])
    spikes = []
    for k in range(7):
        a = math.radians(30 + 20 * k)
        da = 0.1
        b1 = (1.45 * math.cos(a - da), 0.35 + 1.45 * math.sin(a - da))
        b2 = (1.45 * math.cos(a + da), 0.35 + 1.45 * math.sin(a + da))
        tip = (2.85 * math.cos(a), 0.35 + 2.85 * math.sin(a))
        spikes.append([b1, tip, b2])
    windows = [circle(1.28 * math.cos(a), 0.35 + 1.28 * math.sin(a), 0.09, 10) for a in [math.radians(40 + 25 * k) for k in range(5)]]
    face = ellipse(0, -0.25, 0.95, 1.3, 120)
    face = hide([face], band)
    hair = [bumpy(cubic((-1.12, 0.62), (-1.3, 0.0), (-1.1, -0.6), (-1.3, -1.1), 20)[::-1], 0.12, 5),
            bumpy(cubic((1.12, 0.62), (1.3, 0.0), (1.1, -0.6), (1.3, -1.1), 20), 0.12, 5)]
    brows = [quad((-0.65, 0.3), (-0.4, 0.45), (-0.12, 0.32), 8), quad((0.12, 0.32), (0.4, 0.45), (0.65, 0.3), 8)]
    eyes_ = [lens((-0.62, 0.05), (-0.18, 0.05), 0.25), lens((0.18, 0.05), (0.62, 0.05), 0.25)]
    nose = [poly((-0.05, 0.25), (-0.12, -0.55), (0.0, -0.62), (0.15, -0.55), closed=False)]
    lips = [chain(quad((-0.35, -0.95), (0, -0.85), (0.35, -0.95), 10)), quad((-0.35, -0.95), (0, -1.15), (0.35, -0.95), 10)]
    neck = [[(-0.5, -1.38), (-0.55, -2.1)], [(0.5, -1.38), (0.6, -1.9)]]
    robe = [poly((-0.55, -2.1), (-2.6, -2.5), (-2.9, -3.0), closed=False), poly((0.6, -1.9), (1.4, -1.8), (2.7, -2.4), (2.9, -3.0), closed=False),
            quad((-0.55, -2.1), (0.6, -2.4), (1.4, -1.8), 12), quad((-1.4, -2.3), (-0.2, -2.9), (0.8, -2.2), 12)]
    return make("Statue of Liberty Portrait", [band] + face + spikes + windows + hair + brows + eyes_ + nose + lips + neck + robe,
                [eye(-0.4, 0.05, 0.08), eye(0.4, 0.05, 0.08)])


@design("patriotic_liberty_statue", T)
def liberty_statue(rng):
    robe = poly((-0.45, 1.5), (-0.9, -0.6), (0.9, -0.6), (0.45, 1.5), closed=False)
    folds = [quad((-0.2, 1.3), (-0.4, 0.4), (-0.3, -0.6), 10), quad((0.15, 1.0), (0.3, 0.2), (0.25, -0.6), 10), quad((-0.45, 1.3), (0.2, 0.9), (0.45, 1.3), 8)]
    head = circle(0, 1.85, 0.32, 30)
    spikes = [[(0.3 * math.cos(a - 0.15), 1.85 + 0.3 * math.sin(a - 0.15)), (0.62 * math.cos(a), 1.85 + 0.62 * math.sin(a)),
               (0.3 * math.cos(a + 0.15), 1.85 + 0.3 * math.sin(a + 0.15))] for a in [math.radians(30 + 30 * k) for k in range(5)]]
    arm = tube([(0.4, 1.4), (0.65, 2.2), (0.75, 2.75)], 0.24, cap=False)
    torch = [poly((0.5, 2.8), (1.0, 2.8), (0.85, 2.6), (0.65, 2.6), closed=False), [(0.5, 2.8), (1.0, 2.8)],
             chain(quad((0.55, 2.85), (0.5, 3.2), (0.75, 3.5), 8), quad((0.75, 3.5), (1.0, 3.2), (0.95, 2.85), 8))]
    tablet = [transform(rect(-0.25, -0.5, 0.25, 0.5), dx=-0.75, dy=0.6, rot=0.25), quad((-0.4, 1.3), (-0.7, 0.9), (-0.55, 0.55), 8)]
    pedestal = [rect(-1.0, -1.6, 1.0, -0.6), rect(-1.25, -1.75, 1.25, -1.6), rect(-1.4, -3.0, 1.4, -1.75), rect(-1.15, -0.75, 1.15, -0.6)]
    pedestal += [chain([(x - 0.15, -1.45)], [(x - 0.15, -1.05)], arc(x, -1.05, 0.15, math.pi, 0, 8)[1:], [(x + 0.15, -1.45), (x - 0.15, -1.45)]) for x in (-0.5, 0.5)]
    pedestal += [rect(-0.5, -2.8, 0.5, -2.1)]
    rays = burst(0.75, 3.25, 1.1, 10, 0.55)
    water = [wave(-3.0, -1.6, -2.9, 0.07, 3, 40), wave(1.6, 3.0, -2.9, 0.07, 3, 40)]
    return make("Statue of Liberty", [robe, head, arm] + folds + spikes + torch + tablet + pedestal + rays[1:5] + rays[6:] + water)


@design("patriotic_capitol", T)
def capitol(rng):
    wings = [rect(-3.0, -2.4, -1.2, -1.0), rect(1.2, -2.4, 3.0, -1.0), [(-3.0, -0.85), (-1.2, -0.85)], [(1.2, -0.85), (3.0, -0.85)],
             [(-3.0, -0.85), (-3.0, -1.0)], [(3.0, -0.85), (3.0, -1.0)]]
    wins = [rect(x, -1.9, x + 0.25, -1.4) for x in (-2.7, -2.2, -1.7, 1.45, 1.95, 2.45)]
    center = rect(-1.2, -2.4, 1.2, -0.7)
    portico = [poly((-0.95, -0.7), (0, -0.2), (0.95, -0.7))] + [[(x, -2.2), (x, -0.7)] for x in (-0.8, -0.4, 0.0, 0.4, 0.8)]
    steps = [[(-1.0, -2.2), (1.0, -2.2)], rect(-1.4, -2.75, 1.4, -2.4), rect(-1.7, -3.0, 1.7, -2.75)]
    drum = [rect(-1.1, -0.2, 1.1, 0.35), rect(-0.95, 0.35, 0.95, 1.05)] + [[(x, 0.4), (x, 1.0)] for x in (-0.7, -0.35, 0.0, 0.35, 0.7)]
    dome = chain([(-0.85, 1.05)], cubic((-0.85, 1.05), (-0.85, 2.0), (-0.3, 2.3), (-0.22, 2.35), 20), [(0.22, 2.35)], cubic((0.22, 2.35), (0.3, 2.3), (0.85, 2.0), (0.85, 1.05), 20))
    ribs = [quad((x, 1.05), (x * 0.9, 2.0), (x * 0.25, 2.33), 12) for x in (-0.45, 0.45)] + [[(0, 1.05), (0, 2.35)]]
    lantern = [rect(-0.22, 2.35, 0.22, 2.75), arc(0, 2.75, 0.22, 0, math.pi, 10), [(0, 2.97), (0, 3.25)], circle(0, 3.33, 0.08, 8)]
    flags = [[(-2.1, -0.85), (-2.1, 0.0)], poly((-2.1, 0.0), (-1.6, -0.12), (-2.1, -0.25), closed=False), [(2.1, -0.85), (2.1, 0.0)], poly((2.1, 0.0), (2.6, -0.12), (2.1, -0.25), closed=False)]
    return make("United States Capitol", wings + wins + [center] + portico + steps + drum + [dome] + ribs + lantern + flags)


@design("patriotic_washington_monument", T)
def washington_monument(rng):
    obelisk = poly((-0.38, -1.4), (-0.26, 2.3), (0, 2.95), (0.26, 2.3), (0.38, -1.4), closed=False)
    cap = [[(-0.26, 2.3), (0.26, 2.3)]]
    pool = poly((-1.0, -1.7), (-2.6, -3.0), (2.6, -3.0), (1.0, -1.7))
    refl = [poly((-0.38, -1.75), (-0.33, -2.5), (0, -2.75), (0.33, -2.5), (0.38, -1.75), closed=False)]
    ground = [[(-3.0, -1.4), (3.0, -1.4)], [(-3.0, -1.7), (3.0, -1.7)]]
    flags = []
    for x in (-1.3, -0.9, 0.9, 1.3):
        flags += [[(x, -1.4), (x, -0.7)], poly((x, -0.7), (x + 0.3 * (1 if x > 0 else -1), -0.8), (x, -0.9), closed=False)]
    trees = []
    for x in (-2.5, -1.9, 1.9, 2.5):
        trees += [[(x, -1.4), (x, -1.0)], bumpy(circle(x, -0.6, 0.38, 50), 0.07, 8)]
    fw = burst(-1.8, 1.7, 1.0, 12) + [circle(-1.8, 1.7, 0.12, 10)] + burst(1.9, 2.0, 0.85, 10) + [circle(1.9, 2.0, 0.1, 10)]
    return make("Washington Monument", [obelisk, pool] + cap + refl + ground + flags + trees + fw + stars_((1.2, 0.5, 0.2), (-1.2, 0.2, 0.18)))


@design("patriotic_lincoln_memorial", T)
def lincoln_memorial(rng):
    steps = [rect(-3.0, -3.0, 3.0, -2.7), rect(-2.7, -2.7, 2.7, -2.4), rect(-2.4, -2.4, 2.4, -2.1)]
    base = rect(-2.6, -2.1, 2.6, -1.8)
    cols = []
    for k in range(8):
        x = -2.3 + k * 4.6 / 7
        cols += [[(x - 0.15, -1.8), (x - 0.13, 0.6)], [(x + 0.15, -1.8), (x + 0.13, 0.6)], rect(x - 0.22, 0.6, x + 0.22, 0.75), rect(x - 0.22, -1.8, x + 0.22, -1.68)]
    cols = [c for c in cols]
    entab = [rect(-2.7, 0.75, 2.7, 1.5), [(-2.7, 1.1), (2.7, 1.1)]]
    wreaths = [circle(-2.4 + 0.6 * k, 1.3, 0.1, 10) for k in range(9)]
    attic = [poly((-2.4, 1.5), (-2.4, 2.1), (2.4, 2.1), (2.4, 1.5), closed=False), rect(-2.55, 2.1, 2.55, 2.25)]
    statue = [rect(-0.55, -1.55, 0.55, -0.6), rect(-0.4, -0.6, 0.4, 0.15), circle(0, 0.35, 0.18, 14), [(-0.55, -0.6), (-0.7, -0.4)], [(0.55, -0.6), (0.7, -0.4)]]
    statue = hide(statue, *[rect(x - 0.15, -1.8, x + 0.15, 0.6) for x in [-2.3 + k * 4.6 / 7 for k in range(8)]])
    return make("Lincoln Memorial", steps + [base] + cols + entab + wreaths + attic + statue)


@design("patriotic_independence_hall", T)
def independence_hall(rng):
    main = rect(-2.8, -2.4, 2.8, -0.1)
    roof = poly((-2.8, -0.1), (-2.5, 0.35), (2.5, 0.35), (2.8, -0.1), closed=False)
    wins = []
    for x in (-2.4, -1.8, -1.2, 0.9, 1.5, 2.1):
        for y0 in (-1.9, -0.95):
            wins += [rect(x, y0, x + 0.35, y0 + 0.6), [(x, y0 + 0.3), (x + 0.35, y0 + 0.3)]]
    door = chain([(-0.35, -2.4), (-0.35, -1.6)], arc(0, -1.6, 0.35, math.pi, 0, 12)[1:], [(0.35, -2.4)])
    fan = [rect(-0.35, -0.9, 0.35, -0.4)]
    tower = [poly((-0.7, 0.35), (-0.7, 1.4), (0.7, 1.4), (0.7, 0.35), closed=False), rect(-0.6, 1.4, 0.6, 2.2),
             circle(0, 1.8, 0.28, 24), [(0, 1.8), (0, 1.98)], [(0, 1.8), (0.12, 1.75)],
             poly((-0.45, 2.2), (-0.45, 2.75), (0.45, 2.75), (0.45, 2.2), closed=False), [(-0.55, 2.75), (0.55, 2.75)],
             chain([(-0.15, 2.3), (-0.15, 2.5)], arc(0, 2.5, 0.15, math.pi, 0, 6)[1:], [(0.15, 2.3)]),
             poly((-0.4, 2.75), (0, 3.6), (0.4, 2.75), closed=False), [(0, 3.6), (0, 3.85)]]
    tower_win = [chain([(-0.2, 0.55), (-0.2, 0.95)], arc(0, 0.95, 0.2, math.pi, 0, 8)[1:], [(0.2, 0.55), (-0.2, 0.55)])]
    bricks = [[(-2.8, -1.0), (-0.6, -1.0)], [(0.6, -1.0), (2.8, -1.0)]]
    ground = [[(-3.0, -2.4), (3.0, -2.4)], [(-0.6, -2.4), (-1.0, -3.0)], [(0.6, -2.4), (1.0, -3.0)]]
    trees = [[(-3.2, -2.4), (-3.2, -1.6)], bumpy(circle(-3.2, -1.1, 0.5, 50), 0.08, 9)]
    return make("Independence Hall", [main, roof, door] + wins + fan + tower + tower_win + bricks + ground)


@design("patriotic_firework_rocket", T)
def firework_rocket(rng):
    body = rect(-0.55, -1.3, 0.55, 1.4)
    nose = poly((-0.7, 1.4), (0, 2.7), (0.7, 1.4), (-0.7, 1.4))
    bands = [[(-0.55, -0.5), (0.55, -0.5)], [(-0.55, 0.6), (0.55, 0.6)]]
    st = [star(0, 0.05, 0.35)]
    stripes = [[(x, -1.3), (x, -0.5)] for x in (-0.25, 0.05, 0.3)]
    stick = [rect(0.6, -3.0, 0.75, -0.9)]
    fins = [poly((-0.55, -0.6), (-1.0, -1.5), (-0.55, -1.3)), poly((0.55, -0.6), (1.0, -1.5), (0.6, -1.3), closed=False)]
    fuse = [cubic((0, -1.3), (-0.2, -1.8), (-0.6, -1.7), (-0.7, -2.2), 16)]
    spark = burst(-0.75, -2.35, 0.45, 8, 0.25)
    bursts = burst(-2.0, 1.8, 0.9, 10) + burst(2.1, 0.8, 0.8, 10) + [circle(-2.0, 1.8, 0.12, 10), circle(2.1, 0.8, 0.12, 10)]
    return make("Firework Rocket", [body, nose] + bands + st + stripes + stick + fins + fuse + spark + bursts + stars_((2.3, 2.6, 0.25), (-2.3, -1.0, 0.22)))


@design("patriotic_sparklers", T)
def sparklers(rng):
    out = []
    for (x0, y0), (x1, y1) in [((-1.6, -3.0), (0.6, 1.2)), ((1.8, -3.0), (-0.5, 1.0))]:
        mx, my = x0 + 0.45 * (x1 - x0), y0 + 0.45 * (y1 - y0)
        out += [[(x0, y0), (mx, my)], tube([(mx, my), (x1, y1)], 0.22, cap=True)]
    for cx, cy, r in [(0.75, 1.55, 1.4), (-0.65, 1.3, 1.2)]:
        for k in range(14):
            a = TAU * k / 14 + 0.1
            r1 = r * (0.75 if k % 2 else 1.0)
            out.append([(cx + 0.35 * math.cos(a), cy + 0.35 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))])
    return make("Fourth of July Sparklers", out + stars_((2.4, 2.6, 0.25), (-2.5, 2.4, 0.3), (2.6, -0.6, 0.2), (-2.6, -0.4, 0.2)))


@design("patriotic_star_balloons", T)
def star_balloons(rng):
    def sballoon(cx, cy, r, rot):
        pts = star(cx, cy, r, 5, 0.55, rot)
        return smooth(pts[:-1], 4, closed=True)
    b = [sballoon(-1.3, 1.6, 1.0, 0.2), sballoon(1.2, 1.9, 1.05, -0.15), sballoon(0.0, 0.3, 0.9, 0.05)]
    rnd = [ellipse(-2.3, -0.1, 0.55, 0.7, 40), ellipse(2.3, 0.3, 0.55, 0.7, 40)]
    ties = [(-1.3, 0.75), (1.2, 1.0), (0.0, -0.5), (-2.3, -0.8), (2.3, -0.4)]
    knots = [poly((x - 0.1, y - 0.12), (x, y), (x + 0.1, y - 0.12), closed=False) for x, y in ties]
    strings = [cubic((x, y - 0.12), (x + 0.3, y - 0.8), (-0.2, -1.6), (0.0, -2.3), 20) for x, y in ties]
    strings = hide(strings, *b, *rnd)
    bow = [lens((0, -2.3), (-0.6, -2.0), 0.4), lens((0, -2.3), (0.6, -2.0), 0.4), [(0, -2.3), (-0.3, -3.0)], [(0, -2.3), (0.3, -3.0)]]
    back = hide(b[:2], b[2])
    shine = [arc(x - 0.25, y + 0.2, 0.25, math.radians(100), math.radians(170), 6) for x, y in [(-2.3, -0.1), (2.3, 0.3)]]
    inner = [star(0.0, 0.3, 0.35, 5, 0.45, 0.05)]
    return make("Star-Spangled Balloons", back + [b[2]] + rnd + knots + strings + bow + shine + inner)


@design("patriotic_picnic_table", T)
def picnic_table(rng):
    top = poly((-2.6, 0.0), (2.6, 0.0), (2.2, 0.8), (-2.2, 0.8))
    drape = [chain([(-2.6, 0.0)], *[arc(-2.6 + 0.52 * (k + 0.5), 0.0, 0.26, math.pi, 2 * math.pi, 8)[1:] for k in range(10)])]
    checks = [[(-2.2 + 0.55 * k, 0.8), (-2.6 + 0.65 * k, 0.0)] for k in range(1, 8)] + [[(-2.4, 0.4), (2.4, 0.4)]]
    legs = [[(-1.8, -0.25), (-2.4, -2.6)], [(-1.8, -0.25), (-1.2, -2.6)], [(1.8, -0.25), (2.4, -2.6)], [(1.8, -0.25), (1.2, -2.6)]]
    bench = [rect(-3.0, -1.6, 3.0, -1.35)]
    legs = hide(legs, bench[0])
    pie = [ellipse(-1.2, 1.05, 0.75, 0.25, 40), chain([(-1.95, 1.05), (-1.85, 0.8)], quad((-1.85, 0.8), (-1.2, 0.6), (-0.55, 0.8), 12)[1:], [(-0.45, 1.05)])]
    pitcher = [poly((0.4, 0.55), (0.3, 2.0), (0.95, 2.0), (1.05, 0.55), closed=False), [(0.4, 0.55), (1.05, 0.55)], poly((0.3, 2.0), (0.15, 2.2), (0.35, 2.05), closed=False),
               arc(1.05, 1.35, 0.35, math.radians(80), math.radians(-80), 12)]
    pitcher += [circle(0.68, 1.3, 0.2, 14)]
    flagpole = [[(1.9, 0.6), (1.9, 2.6)]] + flag(1.9, 2.6, 1.0, 0.7, 0.05, 1.0, 5, 1, 2)
    return make("Fourth of July Picnic Table", [top] + drape + checks + legs + bench + pie + pitcher + flagpole)


@design("patriotic_bbq_grill", T)
def bbq_grill(rng):
    bowl = chain(arc(0, 0.2, 2.0, math.pi, 2 * math.pi, 50))
    grate = ellipse(0, 0.2, 2.0, 0.45, 80)
    bars = keep([[(x, -0.5), (x, 0.9)] for x in (-1.2, -0.6, 0.0, 0.6, 1.2)], grate)
    food = [ellipse(-0.9, 0.3, 0.45, 0.16, 24), ellipse(0.2, 0.42, 0.45, 0.16, 24), rrect(0.75, 0.05, 1.6, 0.27, 0.11), rrect(-0.6, -0.05, 0.25, 0.17, 0.11)]
    bars = hide(bars, *food)
    handles = [poly((-2.0, -0.1), (-2.35, -0.1), (-2.35, -0.4), (-1.98, -0.4), closed=False), poly((2.0, -0.1), (2.35, -0.1), (2.35, -0.4), (1.98, -0.4), closed=False)]
    legs = [[(-1.2, -1.4), (-1.8, -2.8)], [(1.2, -1.4), (1.8, -2.8)], [(0.0, -1.8), (0.0, -2.6)], [(-1.55, -2.3), (1.55, -2.3)]]
    wheels = [circle(-1.85, -2.7, 0.25, 18), circle(1.85, -2.7, 0.25, 18)]
    vent = [circle(0, -1.25, 0.25, 16)]
    smoke = [cubic((x, 0.8), (x + 0.4, 1.3), (x - 0.4, 1.8), (x, 2.5), 20) for x in (-0.8, 0.0, 0.8)]
    tool = [tube([(2.1, -0.3), (2.8, 1.8)], 0.15, cap=True), rect(2.65, 1.8, 3.15, 2.5)]
    flg = [[(-2.6, -0.4), (-2.6, 2.2)]] + flag(-2.6, 2.2, 1.0, 0.65, 0.05, 1.0, 5, 1, 2)
    return make("Backyard BBQ Grill", [bowl, grate] + bars + food + handles + legs + wheels + vent + smoke + tool + flg)


@design("patriotic_watermelon", T)
def watermelon(rng):
    rind_o = chain(arc(0, 0.6, 3.0, math.pi, 2 * math.pi, 80), [(-3.0, 0.6)])
    rind_i = arc(0, 0.6, 2.55, math.pi, 2 * math.pi, 70)
    flesh_line = arc(0, 0.6, 2.35, math.pi, 2 * math.pi, 70)
    bite = arc(1.9, 0.6, 0.45, math.pi, 2 * math.pi, 16)
    seeds = []
    for r_, n in [(1.0, 4), (1.7, 6)]:
        for k in range(n):
            a = math.pi + math.pi * (k + 0.5) / n
            x, y = r_ * math.cos(a), 0.6 + r_ * math.sin(a)
            seeds.append(lens((x, y), (x + 0.25 * math.cos(a), y + 0.25 * math.sin(a)), 0.35))
    seeds = hide(seeds, circle(1.9, 0.6, 0.45, 20))
    outline = hide([rind_o, rind_i, flesh_line], circle(1.9, 0.6, 0.45, 30))
    pick = [[(-0.6, 0.6), (-0.6, 2.2)]] + flag(-0.6, 2.9, 1.5, 0.95, 0.06, 1.0, 5, 1, 3)
    return make("Fourth of July Watermelon", outline + [bite] + seeds + pick + stars_((2.3, 2.4, 0.3), (-2.3, 1.9, 0.25)))


@design("patriotic_apple_pie", T)
def apple_pie(rng):
    crust = bumpy(ellipse(0, 0.0, 2.7, 1.1, 160), 0.12, 22)
    top = ellipse(0, 0.0, 2.35, 0.9, 120)
    lattice = keep([[(x, -1.0), (x + 0.6, 1.0)] for x in (-1.9, -1.1, -0.3, 0.5, 1.3)] + [[(x, 1.0), (x + 0.6, -1.0)] for x in (-1.9, -1.1, 0.5, 1.3)], top)
    star_c = star(0, 0.0, 0.5)
    lattice = hide(lattice, star_c)
    dish = chain([(-2.8, -0.15)], [(-2.45, -1.3)], quad((-2.45, -1.3), (0, -1.9), (2.45, -1.3), 30)[1:], [(2.8, -0.15)])
    dish = hide([dish], crust)
    steam = [cubic((x, 1.25), (x + 0.3, 1.7), (x - 0.3, 2.1), (x, 2.6), 16) for x in (-0.8, 0.0, 0.8)]
    cloth = [[(-3.0, -2.4), (3.0, -2.4)], [(-3.0, -2.9), (3.0, -2.9)]] + [[(x, -2.4), (x, -2.9)] for x in (-2.0, -1.0, 0.0, 1.0, 2.0)]
    return make("Star-Topped Apple Pie", [crust, top, star_c] + lattice + dish + steam + cloth)


@design("patriotic_ice_cream_flag", T)
def ice_cream_flag(rng):
    cone_p = poly((-1.0, -0.6), (0, -3.0), (1.0, -0.6))
    hatch = keep([[(x, -3.2), (x + 1.6, -0.4)] for x in (-1.8, -1.3, -0.8, -0.3, 0.2)] + [[(x, -3.2), (x - 1.6, -0.4)] for x in (1.8, 1.3, 0.8, 0.3, -0.2)], cone_p)

    def scoop(yc, r):
        a0 = -0.2
        top = arc(0, yc, r, a0, math.pi - a0, 40)
        left, right = top[-1], top[0]
        return chain(top, bumpy([left, right], 0.16, 5)[1:])
    s1, s2, s3 = scoop(-0.45, 1.25), scoop(0.75, 1.05), scoop(1.75, 0.82)
    parts = hide([poly((-1.0, -0.6), (0, -3.0), (1.0, -0.6), closed=False)] + hatch, s1) + hide([s1], s2) + hide([s2], s3) + [s3]
    pick = [[(0.2, 2.5), (0.2, 3.4)]] + flag(0.2, 3.4, 1.3, 0.8, 0.05, 1.0, 5, 1, 2)
    pick = hide(pick, s3)
    sprinkles = stars_((-0.5, -0.1, 0.15), (0.45, -0.2, 0.15), (-0.3, 0.95, 0.14), (0.45, 0.9, 0.14), (-0.25, 1.85, 0.13))
    return make("Ice Cream Cone with Flag", parts + pick + sprinkles)


@design("patriotic_fife_drum", T)
def fife_drum(rng):
    def low(x, yc):
        return yc - 0.5 * math.sqrt(max(0.0, 1 - (x / 1.9) ** 2))
    top = ellipse(0, 0.3, 1.9, 0.5, 80)
    side = chain([(-1.9, 0.3)], [(x, low(x, -1.9)) for x in [-1.9 + 3.8 * i / 60 for i in range(61)]], [(1.9, 0.3)])
    hoops = [[(x, low(x, yc)) for x in [-1.9 + 3.8 * i / 60 for i in range(61)]] for yc in (0.0, -1.6)]
    xs = [-1.9 + 3.8 * k / 8 for k in range(9)]
    rope = [[(xs[i], low(xs[i], 0.0)), (xs[i + 1], low(xs[i + 1], -1.6))] for i in range(8)] + \
           [[(xs[i + 1], low(xs[i + 1], 0.0)), (xs[i], low(xs[i], -1.6))] for i in range(8)]
    sticks = [tube([(-1.6, 2.6), (0.3, 0.9)], 0.16, cap=True), tube([(1.6, 2.6), (-0.3, 0.9)], 0.16, cap=True), circle(-1.65, 2.65, 0.15, 12), circle(1.65, 2.65, 0.15, 12)]
    fife = [rrect(-2.7, -2.82, 2.7, -2.58, 0.1)] + [circle(0.9 + 0.4 * k, -2.7, 0.06, 8) for k in range(4)]
    fife = hide(fife, chain(side, [(-1.9, 0.3)]))
    return make("Colonial Fife and Drum", [top, side] + hoops + rope + sticks + fife + stars_((-2.5, 1.0, 0.25), (2.5, 1.0, 0.25)))


@design("patriotic_trumpet", T)
def trumpet(rng):
    bell = chain(cubic((0.6, 0.85), (1.6, 0.9), (2.3, 1.2), (2.7, 1.9), 20), [(2.7, -0.5)], cubic((2.7, -0.5), (2.3, 0.2), (1.6, 0.5), (0.6, 0.55), 20))
    rim = ellipse(2.7, 0.7, 0.2, 1.2, 40)
    pipe_top = [[(-2.6, 0.85), (0.6, 0.85)], [(-2.6, 0.55), (0.6, 0.55)]]
    mouth = [poly((-2.6, 0.85), (-2.9, 1.0), (-2.9, 0.4), (-2.6, 0.55), closed=False)]
    loop = [chain([(-1.6, 0.55)], arc(-1.6, -0.2, 0.75, math.pi / 2, 1.5 * math.pi, 20)[1:], [(0.9, -0.95)], arc(0.9, -0.5, 0.45, -math.pi / 2, math.pi / 2, 12)[1:], [(0.6, -0.05)]),
            chain([(-1.6, 0.25)], arc(-1.6, -0.2, 0.45, math.pi / 2, 1.5 * math.pi, 16)[1:], [(0.9, -0.65)], arc(0.9, -0.5, 0.15, -math.pi / 2, math.pi / 2, 6)[1:], [(0.6, -0.35)])]
    valves = []
    for x in (-0.6, -0.2, 0.2):
        valves += [rect(x - 0.13, -0.65, x + 0.13, 1.35), rect(x - 0.18, 1.35, x + 0.18, 1.5), [(x, 1.5), (x, 1.75)], ellipse(x, 1.82, 0.18, 0.07, 14)]
    pipe_top = hide(pipe_top, *[rect(x - 0.13, -0.65, x + 0.13, 1.35) for x in (-0.6, -0.2, 0.2)])
    loop = hide(loop, *[rect(x - 0.13, -0.65, x + 0.13, 1.35) for x in (-0.6, -0.2, 0.2)])
    banner = flag(-2.2, 0.5, 2.6, 1.9, 0.0, 1.0, 7, 2, 3)
    fringe = [zigzag(-2.2, 0.4, -1.5, 0.1, 9)]
    banner = hide(banner, *[rect(x - 0.13, -0.65, x + 0.13, 1.35) for x in (-0.6, -0.2, 0.2)])
    cords = [[(-2.2, 0.5), (-2.2, 0.55)], [(0.4, 0.5), (0.4, 0.55)]]
    return make("Parade Trumpet with Banner", [bell, rim] + pipe_top + mouth + valves + banner + stars_((2.0, 2.7, 0.3), (-2.4, 2.3, 0.25)))


@design("patriotic_band_hat", T)
def band_hat(rng):
    body = poly((-1.3, -1.5), (-1.2, 1.4), (1.2, 1.4), (1.3, -1.5), closed=False)
    top = ellipse(0, 1.4, 1.2, 0.3, 50)
    bottom = quad((-1.3, -1.5), (0, -1.8), (1.3, -1.5), 20)
    visor = chain([(-1.3, -1.5)], cubic((-1.3, -1.5), (-1.0, -2.15), (1.0, -2.15), (1.3, -1.5), 30))
    band = [quad((-1.28, -1.0), (0, -1.3), (1.28, -1.0), 20)]
    strap = [quad((-1.25, -0.6), (0, -0.2), (1.25, -0.6), 16)]
    badge = [star(0, 0.35, 0.75), circle(0, 0.35, 0.28, 20)]
    plume = []
    for k in range(7):
        a = math.radians(60 + 10 * k)
        plume.append(lens((0, 1.55), (1.7 * math.cos(a) * 0.6, 1.55 + 1.6 * math.sin(a)), 0.18))
    plume_base = [rrect(-0.15, 1.45, 0.15, 1.9, 0.07)]
    plume = hide(plume, plume_base[0])
    cords = [quad((-1.25, 0.9), (0, 0.4), (1.25, 0.9), 16)]
    cords = hide(cords, *badge[:1])
    strap = hide(strap, *badge[:1])
    return make("Marching Band Hat", [body, top, bottom, visor] + band + strap + badge + plume + plume_base + cords)


@design("patriotic_eagle_head", T)
def eagle_head(rng):
    head = smooth([(1.6, -2.8), (1.4, -1.2), (1.6, 0.0), (1.4, 1.2), (0.6, 2.0), (-0.6, 2.1), (-1.4, 1.6), (-1.7, 1.0)], 10)
    beak = chain(cubic((-1.7, 1.0), (-2.4, 1.1), (-3.0, 0.6), (-2.9, -0.3), 20), quad((-2.9, -0.3), (-2.75, -0.05), (-2.55, -0.05), 6)[1:],
                 cubic((-2.55, -0.05), (-2.4, 0.2), (-1.9, 0.2), (-1.4, 0.15), 14)[1:])
    lower = [(-2.4, 0.05), (-2.2, -0.25), (-1.3, -0.25)]
    mouth = quad((-1.4, 0.15), (-1.15, 0.0), (-1.3, -0.25), 6)
    cere = quad((-1.75, 1.0), (-1.55, 0.6), (-1.4, 0.15), 10)
    nostril = ellipse(-2.0, 0.75, 0.13, 0.07, 12, rot=-0.3)
    brow = quad((-1.5, 1.35), (-0.9, 1.6), (-0.3, 1.25), 12)
    eye_ring = circle(-0.85, 1.05, 0.25, 24)
    throat = smooth([(-1.3, -0.25), (-1.0, -1.0), (-0.7, -1.8), (-0.9, -2.8)], 10)
    neck = zigzag(-1.15, 1.5, -1.9, 0.18, 9)
    neck = [(x, y + 0.2 * (x + 1.15) / 2.65) for x, y in neck]
    neck = keep([neck], chain(throat, [(1.6, -2.8)], head[::-1][:-1], [(-1.3, -0.25)]))
    feathers = [quad((x, y), (x + 0.3, y - 0.2), (x + 0.6, y - 0.1), 6) for x, y in [(0.0, 0.4), (0.4, -0.5), (-0.3, -0.9), (0.6, 1.1)]]
    stars = stars_((-2.4, 2.4, 0.3), (-2.6, -1.6, 0.25), (2.5, 2.5, 0.25))
    return make("Bald Eagle Portrait", [head, beak, lower, mouth, cere, nostril, brow, eye_ring, throat] + neck + feathers + stars, [eye(-0.85, 1.05, 0.11)])


@design("patriotic_eagle_shield", T)
def eagle_shield(rng):
    out = []
    lead = smooth([(0.5, 0.7), (1.2, 1.6), (2.1, 2.5), (2.95, 2.95)], 8)
    tips = [(2.95, 2.95), (3.05, 2.15), (2.95, 1.35), (2.7, 0.6), (2.3, -0.05), (1.75, -0.55), (1.1, -0.8)]
    trail = [tips[0]]
    lines = []
    for a, b in zip(tips, tips[1:]):
        n = (a[0] + (b[0] - a[0]) * 0.5 - 0.45 * (a[0] - 0.6) / 3, a[1] + (b[1] - a[1]) * 0.5 - 0.45 * (a[1] - 0.6) / 3)
        trail += [n, b]
        lines.append([n, (n[0] - 0.55 * (n[0] - 0.6) / 2.5, n[1] - 0.55 * (n[1] - 0.6) / 2.5)])
    wing_r = chain(lead, trail[1:], [(0.6, -0.5)])
    coverts = [quad((0.9, 1.0), (1.8, 1.4), (2.6, 2.3), 10)]
    for sx in (-1, 1):
        wing, arm = [wing_r] + lines, coverts[0]
        if sx < 0:
            wing, arm = mirror_all(wing), mirror_x(arm)
        out.append((wing, arm))
    body = ellipse(0, -0.3, 0.75, 1.3, 60)
    head = smooth([(-0.3, 0.8), (-0.35, 1.5), (0.0, 1.85), (0.45, 1.8), (0.9, 1.55), (0.55, 1.4), (0.3, 1.2), (0.3, 0.8)], 6)
    beak_l = quad((0.9, 1.55), (1.0, 1.35), (0.85, 1.3), 4)
    shield = chain([(-0.8, 0.5), (0.8, 0.5), (0.8, -0.6)], cubic((0.8, -0.6), (0.8, -1.3), (0.2, -1.5), (0, -1.75), 12),
                   cubic((0, -1.75), (-0.2, -1.5), (-0.8, -1.3), (-0.8, -0.6), 12), [(-0.8, 0.5)])
    chief = [[(-0.8, 0.0), (0.8, 0.0)]]
    sh_stripes = keep([[(x, 0.0), (x, -1.8)] for x in (-0.5, -0.2, 0.1, 0.4)], shield)
    tail = [poly((-0.5, -1.4), (-0.9, -2.6), (-0.3, -2.4), (0, -2.8), (0.3, -2.4), (0.9, -2.6), (0.5, -1.4), closed=False)]
    olive = [quad((-0.6, -1.5), (-1.5, -1.9), (-2.4, -1.6), 12)] + [lens(p, (p[0] - 0.2, p[1] + 0.35), 0.35) for p in [(-1.2, -1.7), (-1.8, -1.72)]] + \
            [lens(p, (p[0] - 0.15, p[1] - 0.35), 0.35) for p in [(-1.5, -1.75), (-2.1, -1.65)]]
    arrows = [[(0.6, -1.5), (2.4, -2.2)], [(0.6, -1.6), (2.3, -2.5)], poly((2.4, -2.2), (2.2, -2.0), (2.6, -2.3), (2.25, -2.35), closed=False)]
    stars = [star(x, 0.25, 0.14) for x in (-0.5, 0.0, 0.5)]
    front = [shield, head]
    wings = []
    for wing, arm in out:
        wings += hide(wing + [arm], body, shield, head)
    body_v = hide([body], shield, head)
    return make("Eagle with Shield", wings + body_v + [head, beak_l, shield] + chief + sh_stripes + tail + olive + arrows + stars, [eye(0.4, 1.55, 0.06)])


@design("patriotic_flag_heart", T)
def flag_heart(rng):
    h = heart(0, 0.2, 2.8, 240)
    canton = poly((-2.9, 2.6), (0.0, 2.6), (0.0, 0.35), (-2.9, 0.35))
    stripes = keep([[(-3.0, y), (3.0, y)] for y in (2.0, 1.4, 0.8, 0.2, -0.4, -1.0, -1.6, -2.2)], h)
    stripes = hide(stripes, canton)
    cant = keep([[(-3.0, 0.35), (0.0, 0.35)], [(0.0, 0.35), (0.0, 3.0)]], h)
    st = [star(x, y, 0.22) for x, y in [(-1.9, 1.75), (-1.2, 1.95), (-0.5, 1.8), (-2.2, 1.0), (-1.5, 1.2), (-0.8, 1.05), (-1.15, 0.6)]]
    return make("Stars and Stripes Heart", [h] + stripes + cant + st + stars_((2.6, 2.6, 0.25), (-2.7, -1.8, 0.25)))


@design("patriotic_flagpole", T)
def flagpole(rng):
    pole = rect(-2.0, -2.4, -1.85, 2.6)
    ball = circle(-1.925, 2.75, 0.17, 16)
    fl = flag(-1.85, 2.5, 4.4, 2.6, 0.25, 1.3, 7, 3, 4)
    rope = [[(-2.05, 2.5), (-2.05, -1.6)], [(-2.05, -1.6), (-2.2, -1.6)]]
    base = [rect(-2.6, -2.7, -1.25, -2.4), rect(-2.9, -3.0, -0.95, -2.7)]
    clouds = [chain(arc(1.4, -1.7, 0.4, math.pi, 0, 12), arc(2.1, -1.6, 0.5, math.pi, 0, 14), arc(2.8, -1.7, 0.3, math.pi, 0, 10), [(1.0, -1.7)])]
    grass = [zigzag(-3.0, 3.0, -3.05, 0.1, 18)]
    grass = hide(grass, base[1])
    return make("Flag on a Flagpole", [pole, ball] + fl + rope + base + clouds + grass + [bird(0.8, -0.6), bird(1.6, -0.2)])


@design("patriotic_rosette", T)
def rosette(rng):
    tails = [poly((-0.5, -0.8), (-1.6, -3.0), (-1.0, -2.6), (-0.7, -3.0), (0.2, -0.9)), poly((0.5, -0.8), (1.6, -3.0), (1.0, -2.6), (0.7, -3.0), (-0.2, -0.9))]
    tail_lines = [[(-0.85, -1.4), (-1.35, -2.6)], [(0.85, -1.4), (1.35, -2.6)]]
    outer = polar(lambda t: 2.1 + 0.18 * math.cos(24 * t), n=720, cy=0.4)
    pleats = [[(1.35 * math.cos(a), 0.4 + 1.35 * math.sin(a)), (1.9 * math.cos(a), 0.4 + 1.9 * math.sin(a))] for a in [TAU * k / 24 for k in range(24)]]
    ring = [circle(0, 0.4, 1.35, 90), circle(0, 0.4, 1.05, 80)]
    st = [star(0, 0.4, 0.95)]
    tails = hide(tails + tail_lines, outer)
    return make("Ribbon Rosette", [outer] + pleats + ring + st + tails)


@design("patriotic_rocket_pops", T)
def rocket_pops(rng):
    def pop(cx, cy, s, rot, bite=False):
        out = poly((-0.55, -1.0), (-0.55, 0.2), (-0.42, 0.25), (-0.42, 0.95), (-0.25, 1.0), (0.0, 1.6), (0.25, 1.0), (0.42, 0.95), (0.42, 0.25), (0.55, 0.2), (0.55, -1.0))
        parts = [out, [(-0.55, 0.2), (0.55, 0.2)], [(-0.42, 0.95), (0.42, 0.95)], rect(-0.1, -1.9, 0.1, -1.0)]
        parts.append(quad((-0.55, -0.4), (-0.2, -0.55), (0.0, -0.3), 6))
        if bite:
            parts = hide(parts, circle(0.5, 1.2, 0.28, 20)) + [arc(0.5, 1.2, 0.28, math.radians(120), math.radians(250), 10)]
        return [transform(p, dx=cx, dy=cy, s=s, rot=rot) for p in parts]
    out = pop(-1.7, -0.2, 1.3, 0.25) + pop(0.0, 0.3, 1.45, 0.0, True) + pop(1.7, -0.2, 1.3, -0.25)
    drips = [ellipse(x, -3.0, 0.35, 0.1, 16) for x in (-1.2, 1.4)]
    return make("Rocket Pop Popsicles", out + drips + stars_((-2.6, 2.4, 0.25), (2.6, 2.4, 0.25), (0.0, -2.8, 0.2)))


@design("patriotic_lemonade_jar", T)
def lemonade_jar(rng):
    jar = chain([(-1.4, 1.2), (-1.5, 0.9), (-1.5, -2.45)], arc(-1.1, -2.45, 0.4, math.pi, 1.5 * math.pi, 6)[1:], [(1.1, -2.85)], arc(1.1, -2.45, 0.4, 1.5 * math.pi, 2 * math.pi, 6)[1:], [(1.5, 0.9), (1.4, 1.2)])
    lid = [rect(-1.45, 1.2, 1.45, 1.75)] + [[(-1.45, y), (1.45, y)] for y in (1.38, 1.56)]
    handle = [arc(1.25, -0.6, 0.95, math.radians(75), math.radians(-75), 20), arc(1.25, -0.6, 0.65, math.radians(65), math.radians(-65), 18)]
    level = [quad((-1.5, 0.3), (0, 0.15), (1.5, 0.3), 16)]
    lemons = [circle(-0.6, -1.4, 0.55, 40), circle(-0.6, -1.4, 0.42, 30)] + [[(-0.6, -1.4), (-0.6 + 0.42 * math.cos(a), -1.4 + 0.42 * math.sin(a))] for a in [TAU * k / 6 for k in range(6)]]
    ice = [transform(rrect(-0.3, -0.3, 0.3, 0.3, 0.06), dx=x, dy=y, rot=r) for x, y, r in [(0.7, -0.4, 0.3), (0.4, -2.1, -0.2), (-0.7, -0.1, 0.1)]]
    straw = [tube([(0.3, -1.0), (0.5, 1.75), (0.7, 3.0)], 0.28, cap=True)]
    straw_in = hide(straw, rect(-1.45, 1.2, 1.45, 1.75))
    stripes = keep([[(0.0, y), (1.2, y + 0.4)] for y in (1.8, 2.15, 2.5)], straw[0])
    ice = hide(ice, *lemons[:1])
    st = stars_((-0.1, -0.9, 0.25)) + stars_((-2.5, 2.2, 0.25), (2.6, 2.6, 0.25))
    return make("Mason Jar Lemonade", [jar] + lid + handle + level + lemons + ice + straw_in + stripes + st)


@design("patriotic_hot_air_balloon", T)
def hot_air_balloon(rng):
    env = chain(cubic((-0.6, -0.9), (-1.2, -0.3), (-2.3, 0.6), (-2.3, 1.6), 20), arc(0, 1.6, 2.3, math.pi, 0, 50)[1:], cubic((2.3, 1.6), (2.3, 0.6), (1.2, -0.3), (0.6, -0.9), 20)[1:])
    gores = []
    for f in (-0.66, -0.33, 0.0, 0.33, 0.66):
        gores.append(smooth([(0.6 * f, -0.9), (2.0 * f, 0.2), (2.3 * f * 1.0, 1.6), (1.9 * f, 2.9), (0.0, 3.9 if f == 0 else 3.75)], 8))
    gores = keep(gores, chain(env, [(-0.6, -0.9)]))
    band = [quad((-2.25, 1.0), (0, 0.6), (2.25, 1.0), 30), quad((-2.15, 0.35), (0, -0.05), (2.15, 0.35), 30)]
    band_st = [star(x, 0.67 - 0.06 * (1 - abs(x) / 2), 0.18) for x in (-1.5, -0.75, 0.0, 0.75, 1.5)]
    gores = hide(gores, chain(band[0], band[1][::-1], [band[0][0]]))
    skirt = [[(-0.6, -0.9), (0.6, -0.9)]]
    ropes = [[(-0.6, -0.9), (-0.45, -2.0)], [(0.6, -0.9), (0.45, -2.0)]]
    basket = [rrect(-0.55, -2.7, 0.55, -2.0, 0.08)] + [[(-0.55, -2.25), (0.55, -2.25)]] + [[(x, -2.7), (x, -2.25)] for x in (-0.2, 0.2)]
    clouds = [chain(arc(-2.3, -1.6, 0.35, math.pi, 0, 10), arc(-1.7, -1.5, 0.45, math.pi, 0, 12), arc(-1.1, -1.6, 0.3, math.pi, 0, 8), [(-2.65, -1.6)]),
              chain(arc(1.4, -2.3, 0.35, math.pi, 0, 10), arc(2.0, -2.2, 0.45, math.pi, 0, 12), arc(2.6, -2.3, 0.3, math.pi, 0, 8), [(1.05, -2.3)])]
    return make("Patriotic Hot Air Balloon", [env] + gores + band + band_st + skirt + ropes + basket + clouds)


@design("patriotic_bicycle", T)
def bicycle(rng):
    wheels = [circle(-1.9, -1.5, 1.05, 80), circle(1.9, -1.5, 1.05, 80), circle(-1.9, -1.5, 0.9, 70), circle(1.9, -1.5, 0.9, 70)]
    spokes = [[(cx, -1.5), (cx + 0.9 * math.cos(a), -1.5 + 0.9 * math.sin(a))] for cx in (-1.9, 1.9) for a in [TAU * k / 8 for k in range(8)]]
    frame = [[(-1.9, -1.5), (-0.2, -1.5)], [(-0.2, -1.5), (-0.7, 0.2)], [(-1.9, -1.5), (-0.7, 0.2)], [(-0.7, 0.2), (1.25, 0.2)], [(-0.2, -1.5), (1.25, 0.2)],
             [(1.9, -1.5), (1.15, 0.8)]]
    seat = [[(-0.7, 0.2), (-0.8, 0.6)], poly((-1.25, 0.6), (-0.4, 0.7), (-0.5, 0.85), (-1.15, 0.8))]
    bars = [[(1.15, 0.8), (1.0, 1.2)], quad((0.6, 1.25), (1.0, 1.15), (1.45, 1.35), 8)]
    crank = [circle(-0.2, -1.5, 0.25, 18), [(-0.2, -1.5), (0.15, -2.0)], rect(0.0, -2.08, 0.4, -1.95)]
    streamers = [cubic((0.65, 1.25), (0.3, 0.7), (0.9, 0.3), (0.5, -0.1), 14), cubic((1.45, 1.35), (1.9, 0.9), (1.6, 0.5), (2.1, 0.1), 14)]
    basket = [poly((1.4, 0.75), (1.55, 0.0), (2.55, 0.0), (2.7, 0.75)), [(1.45, 0.5), (2.65, 0.5)], [(1.5, 0.25), (2.6, 0.25)]]
    fl = [[(2.3, 0.75), (2.3, 2.5)]] + flag(2.3, 2.5, 1.1, 0.7, 0.05, 1.0, 5, 1, 2)
    ground = [[(-3.2, -2.58), (3.2, -2.58)]]
    spokes = hide(spokes, *crank[:1])
    return make("Patriotic Bicycle", wheels + spokes + frame + seat + bars + crank + streamers + basket + fl + ground)


@design("patriotic_pinwheel", T)
def pinwheel(rng):
    cx, cy, r = 0.0, 0.8, 2.2
    blades = []
    for k in range(4):
        a = math.radians(45 + 90 * k)
        tip = (cx + r * math.cos(a), cy + r * math.sin(a))
        fold = (cx + 0.55 * r * math.cos(a + math.pi / 2 - 0.25), cy + 0.55 * r * math.sin(a + math.pi / 2 - 0.25))
        ctrl = (cx + 0.75 * r * math.cos(a + 0.6), cy + 0.75 * r * math.sin(a + 0.6))
        blades.append(chain([(cx, cy), tip], quad(tip, ctrl, fold, 14)[1:], [(cx, cy)]))
        blades.append(quad((cx + 0.2 * math.cos(a + 0.3), cy + 0.2 * math.sin(a + 0.3)), (cx + 0.6 * r * math.cos(a + 0.2), cy + 0.6 * r * math.sin(a + 0.2)), tip, 10))
    st = [star(cx + 1.1 * math.cos(a), cy + 1.1 * math.sin(a), 0.22) for a in [math.radians(20 + 90 * k) for k in range(4)]]
    pin = [circle(cx, cy, 0.18, 14)]
    stick = [rect(-0.09, -3.0, 0.09, cy - 0.18)]
    stick = hide(stick, *blades[0::2])
    blades = hide(blades, pin[0])
    return make("Patriotic Pinwheel", blades + st + pin + stick + [sparkle(2.4, -1.2, 0.3), sparkle(-2.4, -1.6, 0.25)])


@design("patriotic_star_wreath", T)
def star_wreath(rng):
    sts = []
    for k in range(16):
        a = math.pi / 2 + TAU * k / 16
        if k == 8:
            continue
        r = 2.0
        sts.append(star(r * math.cos(a), r * math.sin(a), 0.55 if k % 2 == 0 else 0.38, rot=a - math.pi / 2))
    ring = hide([circle(0, 0, 1.6, 120), circle(0, 0, 2.4, 140)], *sts)
    bow = [lens((0, -2.0), (-1.2, -1.5), 0.4), lens((0, -2.0), (1.2, -1.5), 0.4), rrect(-0.25, -2.25, 0.25, -1.75, 0.08),
           poly((-0.15, -2.25), (-0.8, -3.1), (-0.5, -3.0), (-0.35, -3.2), (0.1, -2.25), closed=False),
           poly((0.15, -2.25), (0.8, -3.1), (0.5, -3.0), (0.35, -3.2), (-0.1, -2.25), closed=False)]
    stripes = [[(-0.55, -2.55), (-0.25, -2.25)], [(0.55, -2.55), (0.25, -2.25)]]
    ring = hide(ring, *bow[:3])
    sts = hide(sts, *bow[:3])
    center = [star(0, 0.1, 0.9), star(0, 0.1, 0.55)]
    return make("Wreath of Stars", sts + ring + bow + stripes + center)


@design("patriotic_uncle_sam", T)
def uncle_sam(rng):
    hat = [poly((-0.5, 2.35), (-0.6, 3.4), (0.6, 3.4), (0.5, 2.35), closed=False), ellipse(0, 3.4, 0.6, 0.12, 30), ellipse(0, 2.3, 1.0, 0.14, 40),
           [(-0.52, 2.6), (0.52, 2.6)], [(-0.53, 2.85), (0.53, 2.85)]] + [[(x, 2.85), (x * 1.1, 3.3)] for x in (-0.3, 0.0, 0.3)] + [star(x, 2.72, 0.1) for x in (-0.3, 0.0, 0.3)]
    face = [chain([(-0.42, 2.18)], cubic((-0.42, 2.18), (-0.5, 1.6), (-0.3, 1.45), (0, 1.45), 12)[1:], cubic((0, 1.45), (0.3, 1.45), (0.5, 1.6), (0.42, 2.18), 12)[1:])]
    hair = [bumpy([(-0.45, 2.15), (-0.75, 1.7)], 0.08, 3)[::-1], bumpy([(0.75, 1.7), (0.45, 2.15)], 0.08, 3)[::-1]]
    goatee = [poly((-0.18, 1.48), (0, 0.85), (0.18, 1.48), closed=False)]
    feat = [[(0, 1.95), (-0.07, 1.75), (0.03, 1.72)], quad((-0.15, 1.6), (0, 1.55), (0.15, 1.6), 6), [(-0.3, 2.08), (-0.1, 2.05)], [(0.3, 2.08), (0.1, 2.05)]]
    bow = [poly((0, 1.15), (-0.35, 1.3), (-0.35, 1.0)), poly((0, 1.15), (0.35, 1.3), (0.35, 1.0))]
    coat = poly((-0.3, 1.3), (-0.95, 1.1), (-1.05, -0.6), (-1.5, -1.8), (-0.65, -0.65), (0.65, -0.65), (1.5, -1.8), (1.05, -0.6), (0.95, 1.1), (0.3, 1.3), closed=False)
    lapels = [poly((-0.3, 1.3), (-0.3, 0.2), (0, -0.1), closed=False), poly((0.3, 1.3), (0.3, 0.2), (0, -0.1), closed=False)]
    vest = [[(0, -0.1), (0, -0.65)]]
    arm_r = tube([(0.9, 0.9), (1.7, 1.1), (2.4, 1.25)], 0.4, cap=False)
    hand = [circle(2.55, 1.28, 0.2, 16), [(2.72, 1.38), (3.05, 1.45)]]
    arm_l = tube([(-0.95, 0.9), (-1.25, 0.0), (-1.2, -0.6)], 0.38, cap=False)
    hand_l = [circle(-1.2, -0.8, 0.2, 16)]
    legs = [rect(-0.6, -2.7, -0.08, -0.65), rect(0.08, -2.7, 0.6, -0.65)] + [[(x, -2.7), (x, -0.65)] for x in (-0.42, -0.25, 0.25, 0.42)]
    shoes = [ellipse(-0.45, -2.8, 0.4, 0.13, 20), ellipse(0.45, -2.8, 0.4, 0.13, 20)]
    legs = hide(legs, *shoes)
    return make("Uncle Sam", hat + face + hair + goatee + feat + bow + [coat] + lapels + vest + [arm_r, arm_l] + hand + hand_l + legs + shoes,
                [eye(-0.2, 1.92, 0.05), eye(0.2, 1.92, 0.05)])


@design("patriotic_quill_scroll", T)
def quill_scroll(rng):
    top_roll = [rrect(-2.3, 1.9, 1.3, 2.4, 0.25), circle(1.05, 2.15, 0.12, 12), circle(-2.05, 2.15, 0.12, 12)]
    bot_roll = [rrect(-2.4, -2.45, 1.2, -1.95, 0.25), circle(0.95, -2.2, 0.12, 12), circle(-2.15, -2.2, 0.12, 12)]
    sides = [[(-2.15, 1.9), (-2.25, -1.95)], [(1.15, 1.9), (1.05, -1.95)]]
    text = [wave(-1.8 + 0.01 * k, 0.7, 1.4 - 0.42 * k, 0.04, 6, 50) for k in range(6)]
    sig = [cubic((-1.6, -1.4), (-1.2, -1.0), (-1.0, -1.8), (-0.6, -1.4), 16), cubic((-0.6, -1.4), (-0.3, -1.1), (0.0, -1.7), (0.5, -1.35), 16)]
    quill = lens((1.0, -0.4), (3.1, 2.9), 0.12)
    shaft = [[(1.0, -0.4), (2.8, 2.45)]]
    barbs = [[(1.2 + 0.25 * k, -0.05 + 0.4 * k), (1.05 + 0.25 * k, 0.25 + 0.4 * k)] for k in range(1, 6)]
    well = [rrect(1.4, -2.6, 2.8, -1.4, 0.2), rect(1.75, -1.4, 2.45, -1.1), ellipse(2.1, -1.1, 0.42, 0.1, 20)]
    quill_all = [quill] + shaft + barbs
    return make("Quill and Declaration Scroll", top_roll + bot_roll + sides + text + sig + quill_all + well + stars_((-2.6, -2.8, 0.2), (2.6, 0.8, 0.22)))


@design("patriotic_porch", T)
def porch(rng):
    roof = poly((-3.0, 1.6), (3.0, 1.6), (2.6, 2.4), (-2.6, 2.4))
    beam = [[(-2.8, 1.25), (2.8, 1.25)], [(-2.8, 1.6), (-2.8, 1.25)], [(2.8, 1.6), (2.8, 1.25)]]
    cols = [rect(x - 0.15, -2.2, x + 0.15, 1.25) for x in (-2.6, 2.6)]
    floor = [rect(-3.0, -2.5, 3.0, -2.2)]
    rail = [[(-2.45, -0.9), (2.45, -0.9)], [(-2.45, -2.0), (2.45, -2.0)]]
    balus = [[(x, -2.0), (x, -0.9)] for x in [-2.2 + 0.4 * k for k in range(12)]]
    house = [rect(-1.0, -2.2, 0.0, 0.5), rect(-0.8, -0.6, -0.2, 0.3), circle(-0.15, -1.0, 0.06, 8), rect(0.5, -0.6, 1.6, 0.6), [(1.05, -0.6), (1.05, 0.6)], [(0.5, 0.0), (1.6, 0.0)]]
    house = hide(house, *[rect(x - 0.03, -2.0, x + 0.03, -0.9) for x in [-2.2 + 0.4 * k for k in range(12)]], poly((-2.45, -0.95), (2.45, -0.95), (2.45, -2.0), (-2.45, -2.0)))
    swags = []
    for x0 in (-2.4, -0.8, 0.8):
        swags += [arc(x0 + 0.8, 1.25, 0.8, math.pi, 2 * math.pi, 24), arc(x0 + 0.8, 1.25, 0.55, math.pi, 2 * math.pi, 18), arc(x0 + 0.8, 1.25, 0.3, math.pi, 2 * math.pi, 12)]
    swags += [star(x, 1.05, 0.12) for x in (-1.6, 0.0, 1.6)]
    house = hide(house, *[s for s in swags[:9:3]])
    return make("Front Porch with Bunting", [roof] + beam + cols + floor + rail + balus + house + swags)


@design("patriotic_mailbox", T)
def mailbox(rng):
    box = chain([(1.4, 0.0), (-2.0, 0.0), (-2.0, 1.2)], arc(-0.3, 1.2, 1.7, math.pi, 0.0, 40)[1:], [(1.4, 0.0)])
    door = [[(1.4, 0.0), (1.7, 0.0), (1.7, 1.2)], rect(1.7, 0.6, 1.9, 0.8)]
    stripes = keep([[(-2.1, y), (1.5, y)] for y in (0.45, 0.9)], box)
    st = [star(x, 1.75, 0.22) for x in (-1.2, -0.3, 0.6)]
    flag_arm = [rect(-1.65, 1.0, -1.45, 2.6), rect(-1.45, 2.0, -0.6, 2.6)]
    post = [rect(-0.5, -3.0, 0.1, 0.0)]
    flowers = []
    for x, y in [(-1.6, -2.3), (1.0, -2.1), (1.8, -2.6), (-2.4, -2.7)]:
        flowers += [circle(x, y, 0.13, 12), polar(lambda t: 0.38 + 0.08 * math.cos(5 * t), n=120, cx=x, cy=y), [(x, y - 0.4), (x, -3.0)]]
    flowers = hide(flowers, *post)
    grass = [zigzag(-3.0, 3.0, -3.0, 0.1, 18)]
    return make("Mailbox with Stars", [box] + door + stripes + st + flag_arm + post + flowers + grass)


@design("patriotic_lake_fireworks", T)
def lake_fireworks(rng):
    shore = [chain([(-3.0, -0.3)], *[[(-3.0 + 0.4 * k + 0.2, -0.3 + (0.7 if k % 3 == 0 else 0.45)), (-3.0 + 0.4 * (k + 1), -0.3)] for k in range(15)])]
    water = [wave(-3.0, 3.0, y, 0.05, 6, 80) for y in (-1.0, -1.7, -2.5)]
    canoe = chain(quad((-1.8, -1.4), (-0.3, -2.05), (1.2, -1.4), 20), quad((1.2, -1.4), (-0.3, -1.6), (-1.8, -1.4), 20))
    rower = [circle(-0.3, -0.85, 0.18, 14), [(-0.3, -1.03), (-0.35, -1.5)], [(-0.75, -1.0), (0.4, -2.2)], ellipse(0.45, -2.25, 0.12, 0.25, 12, rot=0.6)]
    water = hide(water, chain(canoe, [(-1.8, -1.4)]), ellipse(0.45, -2.25, 0.12, 0.25, 12, rot=0.6))
    fw = []
    for cx, cy, r, n in [(-1.6, 1.9, 1.0, 14), (1.2, 2.3, 0.8, 12), (1.9, 0.8, 0.6, 10)]:
        fw += burst(cx, cy, r, n, 0.25)
    refl = [[(x - 0.3, -1.25), (x + 0.3, -1.25)] for x in (-1.6, 1.2)] + [[(x - 0.2, -1.35 - 0.3), (x + 0.2, -1.35 - 0.3)] for x in (2.0,)]
    moon = [chain(arc(2.4, 2.6, 0.4, math.radians(60), math.radians(300), 20), arc(2.6, 2.6, 0.33, math.radians(260), math.radians(100), 16))]
    return make("Fireworks over the Lake", shore + water + [canoe] + rower + fw + refl + moon)


@design("patriotic_star_cookies", T)
def star_cookies(rng):
    tray = [rrect(-3.0, -2.2, 3.0, 1.8, 0.3), rrect(-2.75, -1.95, 2.75, 1.55, 0.2)]
    cookies = []
    for i, x in enumerate((-1.8, 0.0, 1.8)):
        for j, y in enumerate((0.75, -1.15)):
            c = smooth(star(x, y, 0.8, 5, 0.5, 0.15 * ((i + j) % 2))[:-1], 4, closed=True)
            cookies.append(c)
            k = (i + 2 * j) % 3
            if k == 0:
                cookies.append(smooth(star(x, y, 0.5, 5, 0.5, 0.15 * ((i + j) % 2))[:-1], 4, closed=True))
            elif k == 1:
                cookies += keep([[(x - 1, y + d), (x + 1, y + d)] for d in (-0.3, 0.0, 0.3)], c)
            else:
                cookies += [circle(x, y, 0.22, 16)]
    pin = [rrect(-0.6, 2.2, 2.0, 2.8, 0.25), rrect(-1.3, 2.4, -0.6, 2.6, 0.08), rrect(2.0, 2.4, 2.7, 2.6, 0.08)]
    return make("Star Cookies on a Tray", tray + cookies + pin)


@design("patriotic_soaring_eagle", T)
def soaring_eagle(rng):
    lead = smooth([(0.35, 0.35), (1.2, 0.75), (2.2, 1.0), (3.1, 1.35)], 8)
    tips = [(3.1, 1.35), (3.25, 0.8), (3.05, 0.25), (2.7, -0.25), (2.25, -0.55)]
    trail = [tips[0]]
    for a, b in zip(tips, tips[1:]):
        trail += [((a[0] + b[0]) / 2 - 0.35, (a[1] + b[1]) / 2 - 0.05), b]
    wing = chain(lead, trail[1:], smooth([(2.25, -0.55), (1.4, -0.45), (0.45, -0.5)], 6)[1:])
    lines = [quad((0.6, 0.15), (1.5, 0.35), (2.4, 0.5), 10), quad((0.6, -0.15), (1.4, -0.1), (2.2, 0.0), 10)]
    wings = [wing] + lines
    wings += mirror_all(wings)
    body = ellipse(0, -0.35, 0.5, 1.15, 50)
    head = smooth([(-0.38, 0.55), (-0.42, 1.1), (-0.1, 1.45), (0.35, 1.4), (0.75, 1.15), (0.4, 1.0), (0.32, 0.6)], 8, closed=True)
    beak = [quad((0.75, 1.15), (0.82, 0.95), (0.6, 0.92), 6)]
    neck = [zigzag(-0.38, 0.32, 0.65, 0.1, 3)]
    tail = [poly((-0.35, -1.35), (-0.7, -2.5), (0.7, -2.5), (0.35, -1.35), closed=False), [(-0.2, -2.5), (-0.1, -1.6)], [(0.2, -2.5), (0.1, -1.6)]]
    talons = [[(-0.2, -1.35), (-0.25, -1.75)], [(0.2, -1.35), (0.25, -1.75)]]
    parts = hide(wings, body, head) + hide([body], head) + [head] + beak + neck
    tail = hide(tail, body)
    clouds = [chain(arc(-2.4, -2.2, 0.35, math.pi, 0, 10), arc(-1.8, -2.1, 0.45, math.pi, 0, 12), arc(-1.2, -2.2, 0.3, math.pi, 0, 8), [(-2.75, -2.2)]),
              chain(arc(1.3, -2.5, 0.35, math.pi, 0, 10), arc(1.9, -2.4, 0.45, math.pi, 0, 12), arc(2.5, -2.5, 0.3, math.pi, 0, 8), [(0.95, -2.5)])]
    return make("Soaring Bald Eagle", parts + tail + talons + clouds + stars_((-2.3, 2.4, 0.25), (2.4, 2.6, 0.25)), [eye(0.3, 1.2, 0.07)])


@design("patriotic_dog", T)
def patriotic_dog(rng):
    head = smooth([(-0.9, 1.0), (-0.85, 1.9), (0.0, 2.2), (0.85, 1.9), (0.9, 1.0), (0.5, 0.45), (-0.5, 0.45)], 8, closed=True)
    ears = [smooth([(-0.75, 1.95), (-1.35, 1.7), (-1.5, 0.8), (-1.15, 0.6), (-0.85, 1.2)], 8), smooth([(0.75, 1.95), (1.35, 1.7), (1.5, 0.8), (1.15, 0.6), (0.85, 1.2)], 8)]
    ears = hide(ears, head)
    muzzle = ellipse(0, 0.85, 0.5, 0.35, 30)
    nose = ellipse(0, 1.05, 0.17, 0.11, 14)
    mouth = [[(0, 0.94), (0, 0.75)], quad((-0.3, 0.75), (-0.15, 0.62), (0, 0.75), 6), quad((0, 0.75), (0.15, 0.62), (0.3, 0.75), 6),
             chain([(-0.1, 0.68)], arc(0, 0.6, 0.12, math.pi, 2 * math.pi, 8)[1:], [(0.1, 0.68)])]
    body = smooth([(-0.6, 0.5), (-1.3, -0.5), (-1.5, -2.0), (-1.2, -2.7), (1.2, -2.7), (1.5, -2.0), (1.3, -0.5), (0.6, 0.5)], 8)
    legs = [[(-0.55, -0.6), (-0.6, -2.55)], [(-0.15, -0.6), (-0.15, -2.55)], [(0.55, -0.6), (0.6, -2.55)], [(0.15, -0.6), (0.15, -2.55)]]
    paws = [ellipse(-0.38, -2.65, 0.32, 0.15, 18), ellipse(0.38, -2.65, 0.32, 0.15, 18)]
    bandana = poly((-0.85, 0.5), (0.85, 0.5), (0.0, -0.9))
    legs = hide(legs, bandana, *paws)
    body = hide([body], head, bandana)
    band_st = [star(x, y, 0.15) for x, y in [(-0.4, 0.25), (0.4, 0.25), (0.0, -0.2)]]
    tail = [cubic((1.3, -2.2), (2.2, -2.0), (2.4, -1.0), (2.1, -0.5), 16), cubic((1.4, -2.5), (2.5, -2.3), (2.7, -1.0), (2.1, -0.5), 16)]
    tail = hide(tail, poly((-1.3, -0.5), (-1.5, -2.0), (-1.2, -2.7), (1.2, -2.7), (1.5, -2.0), (1.3, -0.5)))
    hat = [poly((-0.3, 2.2), (-0.35, 3.0), (0.45, 3.1), (0.5, 2.25), closed=False), ellipse(0.1, 2.2, 0.75, 0.12, 30, rot=0.05), [(-0.32, 2.5), (0.48, 2.55)]] + [star(0.08, 2.78, 0.12)]
    head_v = hide([head], ellipse(0.1, 2.2, 0.75, 0.12, 30, rot=0.05), poly((-0.3, 2.2), (-0.35, 3.0), (0.45, 3.1), (0.5, 2.25)))
    return make("Patriotic Pup", head_v + ears + [muzzle, nose, bandana] + mouth + body + legs + paws + band_st + tail + hat,
                [eye(-0.35, 1.45, 0.1), eye(0.35, 1.45, 0.1)])


@design("patriotic_flag_cupcake", T)
def flag_cupcake(rng):
    liner = poly((-1.5, -0.6), (-1.15, -2.9), (1.15, -2.9), (1.5, -0.6), closed=False)
    pleats = keep([[(x, -0.6), (x * 0.75, -2.9)] for x in (-1.05, -0.55, 0.0, 0.55, 1.05)], poly((-1.5, -0.6), (-1.15, -2.9), (1.15, -2.9), (1.5, -0.6)))
    tiers = []
    for (w0, y0), (w1, y1) in [((1.7, -0.6), (1.35, 0.25)), ((1.35, 0.25), (0.95, 1.0)), ((0.95, 1.0), (0.5, 1.6))]:
        tiers.append(chain(quad((-w0, y0), (-w0 - 0.35, (y0 + y1) / 2 + 0.1), (-w1, y1), 10), quad((-w1, y1), (0, y1 - 0.25), (w1, y1), 14)[1:],
                           quad((w1, y1), (w0 + 0.35, (y0 + y1) / 2 + 0.1), (w0, y0), 10)[1:]))
    top = [chain(quad((-0.5, 1.6), (-0.4, 2.1), (0.0, 2.25), 8), quad((0.0, 2.25), (0.3, 2.35), (0.15, 2.6), 6)[1:]), quad((0.5, 1.6), (0.45, 2.0), (0.0, 2.25), 8)]
    base_line = [quad((-1.7, -0.6), (0, -0.85), (1.7, -0.6), 20)]
    pick = [[(0.7, 1.2), (1.1, 2.6)]] + flag(1.1, 2.6, 1.4, 0.85, 0.05, 1.0, 5, 1, 2)
    pick = hide(pick, *tiers[2:])
    sprinkles = stars_((-0.9, -0.2, 0.15), (0.6, -0.15, 0.15), (-0.4, 0.6, 0.13), (0.3, 1.25, 0.12))
    return make("Flag Cupcake", [liner] + pleats + tiers + top + base_line + pick + sprinkles)


@design("patriotic_star_sunglasses", T)
def star_sunglasses(rng):
    def lens_(cx):
        return smooth(star(cx, 0.0, 1.45, 5, 0.55)[:-1], 5, closed=True)
    L, R = lens_(-1.55), lens_(1.55)
    inner = [smooth(star(-1.55, 0.0, 1.1, 5, 0.55)[:-1], 5, closed=True), smooth(star(1.55, 0.0, 1.1, 5, 0.55)[:-1], 5, closed=True)]
    bridge = [quad((-0.6, 0.35), (0, 0.75), (0.6, 0.35), 10)]
    arms = [[(-2.95, 0.45), (-3.3, 0.6), (-3.4, 1.6)], [(2.95, 0.45), (3.3, 0.6), (3.4, 1.6)]]
    shine = [[(-2.0, 0.35), (-1.6, 0.7)], [(1.1, 0.35), (1.5, 0.7)]]
    stripes = keep([[(0.0, y), (3.2, y)] for y in (-0.3, -0.6)], inner[1]) + keep([[(-3.2, y), (0.0, y)] for y in (-0.3, -0.6)], inner[0])
    return make("Star Party Sunglasses", [L, R] + inner + bridge + arms + shine + stripes + [sparkle(0, -2.0, 0.4), sparkle(-2.6, -2.3, 0.25), sparkle(2.6, -2.3, 0.25)])


@design("patriotic_cannon", T)
def cannon(rng):
    barrel = poly((-2.8, 0.3), (1.6, 1.25), (1.75, 0.65), (-2.7, -0.4))
    muzzle = [ellipse(1.7, 0.95, 0.15, 0.35, 20, rot=0.22)]
    rings = [[(x, 0.3 + (x + 2.8) * 0.216 - 0.02), (x + 0.12, -0.4 + (x + 2.8) * 0.236)] for x in (-1.6, 0.0, 1.1)]
    knob = [circle(-2.95, -0.05, 0.2, 14)]
    carriage = poly((-2.3, -0.3), (0.3, 0.35), (0.6, -0.6), (-1.6, -1.6), (-2.6, -1.8), closed=False)
    wheel = [circle(-0.4, -1.1, 1.2, 80), circle(-0.4, -1.1, 1.0, 70), circle(-0.4, -1.1, 0.25, 18)]
    spokes = [[(-0.4 + 0.25 * math.cos(a), -1.1 + 0.25 * math.sin(a)), (-0.4 + 1.0 * math.cos(a), -1.1 + 1.0 * math.sin(a))] for a in [TAU * k / 10 for k in range(10)]]
    back = hide([barrel] + muzzle + rings + [carriage], circle(-0.4, -1.1, 1.2, 60))
    balls = [circle(1.6, -2.1, 0.32, 20), circle(2.25, -2.1, 0.32, 20), circle(1.92, -1.55, 0.32, 20)]
    ground = [[(-3.0, -2.43), (3.0, -2.43)]]
    return make("Colonial Cannon", back + wheel + spokes + knob + balls + ground + stars_((-2.2, 2.2, 0.3), (0.2, 2.6, 0.25), (2.5, 2.2, 0.3)))


@design("patriotic_sailboat", T)
def sailboat(rng):
    hull = poly((-2.6, -1.0), (2.8, -1.0), (2.0, -1.8), (-2.0, -1.8))
    mast = [[(0.0, -1.0), (0.0, 2.8)]]
    main = poly((-0.1, -0.7), (-0.1, 2.6), (-2.3, -0.7))
    jib = poly((0.15, -0.7), (0.15, 2.4), (2.2, -0.7))
    stripes = keep([[(-3, y), (0, y)] for y in (0.1, 0.9, 1.7)], main)
    st = [star(0.75, y, 0.2) for y in (0.0, 0.8)] + [star(1.2, 0.0, 0.2)]
    pennant = [poly((0.0, 2.8), (0.8, 2.6), (0.0, 2.4), closed=False)]
    portholes = [circle(x, -1.4, 0.15, 12) for x in (-1.0, 0.0, 1.0)]
    waves = [wave(-3.0, 3.0, -2.1, 0.1, 6, 100), wave(-2.5, 2.5, -2.6, 0.08, 5, 80)]
    gulls = [bird(-2.3, 2.3), bird(-1.6, 2.6, 0.15), bird(2.3, 2.2)]
    return make("Patriotic Sailboat", [hull, main, jib] + mast + stripes + st + pennant + portholes + waves + gulls)


@design("patriotic_burger_plate", T)
def burger_plate(rng):
    plate = [ellipse(0, -1.6, 3.1, 0.95, 120), ellipse(0, -1.55, 2.4, 0.65, 100)]
    bun_top = chain([(-1.9, 0.3)], cubic((-1.9, 0.3), (-1.9, 2.0), (1.5, 2.0), (1.5, 0.3), 30), [(-1.9, 0.3)])
    seeds = [ellipse(x, y, 0.12, 0.06, 10, rot=0.4) for x, y in [(-1.0, 1.3), (-0.3, 1.5), (0.5, 1.25), (-0.5, 0.8), (0.9, 0.75)]]
    lettuce = [wave(-2.1, 1.7, 0.15, 0.1, 6, 80)]
    cheese = [poly((-2.0, -0.05), (1.6, -0.05), (1.3, -0.45), (0.9, -0.05), closed=False)]
    patty = rrect(-2.0, -0.7, 1.6, -0.05, 0.3)
    bun_bot = rrect(-1.9, -1.3, 1.5, -0.7, 0.25)
    lettuce = hide(lettuce, bun_top)
    bun_bot_v = hide([bun_bot], patty)
    corn = [transform(ellipse(0, 0, 1.0, 0.4, 50), dx=2.0, dy=-1.6, rot=0.35)]
    kern = keep([transform([(x, -0.5), (x, 0.5)], dx=2.0, dy=-1.6, rot=0.35) for x in (-0.6, -0.3, 0.0, 0.3, 0.6)] +
                [transform([(-1.1, 0.0), (1.1, 0.0)], dx=2.0, dy=-1.6, rot=0.35)], corn[0])
    husk = [transform(lens((-0.9, 0.0), (-1.8, 0.4), 0.3), dx=2.0, dy=-1.6, rot=0.35), transform(lens((-0.9, 0.0), (-1.8, -0.4), 0.3), dx=2.0, dy=-1.6, rot=0.35)]
    back = hide(plate, bun_bot, patty, *corn, *husk)
    husk = hide(husk, corn[0])
    pick = [[(-0.2, 1.6), (-0.2, 2.6)]] + flag(-0.2, 2.6, 1.3, 0.8, 0.05, 1.0, 5, 1, 2)
    return make("Burger and Corn Plate", back + [bun_top, patty] + bun_bot_v + seeds + lettuce + cheese + corn + kern + husk + pick)


@design("patriotic_picnic_basket", T)
def picnic_basket(rng):
    body = poly((-2.4, 0.0), (-2.0, -2.6), (2.0, -2.6), (2.4, 0.0))
    rim = rrect(-2.6, -0.2, 2.6, 0.25, 0.1)
    weave = keep([[(-3, y), (3, y)] for y in (-0.7, -1.25, -1.8, -2.3)], body)
    vert = []
    for k, (y0, y1) in enumerate([(-0.2, -0.7), (-0.7, -1.25), (-1.25, -1.8), (-1.8, -2.3), (-2.3, -2.6)]):
        for x in [(-1.8 + 0.6 * i + (0.3 if k % 2 else 0.0)) for i in range(7)]:
            if abs(x) < 2.2:
                vert.append([(x, y0), (x * 0.97, y1)])
    vert = keep(vert, body)
    handle = [arc(0, 0.25, 1.7, math.radians(10), math.radians(170), 40), arc(0, 0.25, 1.45, math.radians(12), math.radians(168), 36)]
    cloth = [poly((-2.2, 0.25), (-2.6, 1.2), (-1.4, 0.9), (-0.9, 1.4), (-0.6, 0.25), closed=False)]
    checks = keep([[(-2.4, 0.6), (-0.7, 0.6)], [(-2.5, 0.95), (-0.8, 0.95)], [(-1.9, 0.25), (-1.95, 1.4)], [(-1.3, 0.25), (-1.35, 1.4)]], poly((-2.2, 0.25), (-2.6, 1.2), (-1.4, 0.9), (-0.9, 1.4), (-0.6, 0.25)))
    bread = [transform(rrect(-1.0, -0.25, 1.0, 0.25, 0.25), dx=1.0, dy=1.0, rot=0.6)] + [transform([(x - 0.1, -0.2), (x + 0.1, 0.2)], dx=1.0, dy=1.0, rot=0.6) for x in (-0.4, 0.0, 0.4)]
    back = hide(handle, *cloth, bread[0])
    bread = hide(bread, rim)
    cloth = cloth + checks
    fl = [[(0.2, 0.25), (0.2, 2.2)]] + flag(0.2, 2.2, 1.0, 0.65, 0.05, 1.0, 5, 1, 2)
    fl = hide(fl, bread[0])
    return make("Independence Day Picnic Basket", [body, rim] + weave + vert + back + cloth + bread + fl)


@design("patriotic_kite", T)
def kite(rng):
    k = poly((0.0, 2.9), (1.6, 1.0), (0.0, -1.6), (-1.6, 1.0))
    spars = [[(0.0, 2.9), (0.0, -1.6)], [(-1.6, 1.0), (1.6, 1.0)]]
    stripes = keep([[(0.0, y), (2.0, y)] for y in (0.4, -0.2, -0.8)] + [[(-2.0, y), (0.0, y)] for y in (0.4, -0.2, -0.8)], k)
    st = [star(-0.55, 1.75, 0.25), star(0.55, 1.75, 0.25)] + [star(-0.6, 1.25, 0.18), star(0.6, 1.25, 0.18)]
    tail = cubic((0.0, -1.6), (1.4, -2.0), (-1.4, -2.7), (0.8, -3.4), 36)
    bows = []
    for i in (9, 20, 31):
        x, y = tail[i]
        bows += [poly((x, y), (x - 0.35, y + 0.2), (x - 0.35, y - 0.2)), poly((x, y), (x + 0.35, y + 0.2), (x + 0.35, y - 0.2))]
    string = [quad((0.0, 0.2), (1.8, -0.6), (2.8, -3.0), 20)]
    clouds = [chain(arc(-2.4, -1.6, 0.35, math.pi, 0, 10), arc(-1.8, -1.5, 0.45, math.pi, 0, 12), arc(-1.2, -1.6, 0.3, math.pi, 0, 8), [(-2.75, -1.6)])]
    return make("Stars and Stripes Kite", [k] + spars + stripes + st + [tail] + bows + string + clouds + [bird(2.2, 2.4), bird(-2.3, 2.6)])


@design("patriotic_firecrackers", T)
def firecrackers(rng):
    sticks = []
    for x, h in [(-1.3, 0.2), (-0.45, 0.6), (0.45, 0.4), (1.3, 0.0)]:
        sticks.append(rrect(x - 0.4, -2.6, x + 0.4, h, 0.1))
        sticks.append(ellipse(x, h, 0.4, 0.12, 20))
    band = [rect(-1.8, -1.6, 1.8, -1.2)]
    sticks = hide(sticks, band[0])
    stars = [star(x, -0.6, 0.22) for x in (-1.3, 0.45)] + [star(x, -2.1, 0.22) for x in (-0.45, 1.3)]
    fuse = [cubic((-0.45, 0.6), (-0.6, 1.4), (0.4, 1.6), (0.3, 2.2), 20)]
    spark = burst(0.3, 2.45, 0.7, 10, 0.3)
    small = [rrect(1.9, -2.9, 2.9, -2.5, 0.08), cubic((2.9, -2.7), (3.2, -2.6), (3.0, -2.3), (3.3, -2.1), 10), rrect(-2.9, -2.9, -1.9, -2.5, 0.08)]
    return make("Bundle of Firecrackers", sticks + band + stars + fuse + spark + small + stars_((-2.4, 1.6, 0.25), (2.4, 0.8, 0.25)))


@design("patriotic_flag_cake", T)
def flag_cake(rng):
    top = poly((-2.8, 0.2), (2.2, 0.2), (2.9, 1.6), (-2.1, 1.6))
    sides = [poly((-2.8, 0.2), (-2.8, -1.6), (2.2, -1.6), (2.2, 0.2), closed=False), poly((2.2, -1.6), (2.9, -0.2), (2.9, 1.6), closed=False)]
    frost = [chain(*[arc(-2.8 + 0.5 * (k + 0.5), 0.2, 0.25, math.pi, 2 * math.pi, 8) for k in range(10)])]
    layer = [[(-2.8, -0.7), (2.2, -0.7)], [(2.2, -0.7), (2.9, 0.7)]]
    def P(u, v):
        return (-2.8 + 5.0 * u + 0.7 * v, 0.2 + 1.4 * v)
    blue = [circle(*P(u, v), 0.12, 10) for u in (0.06, 0.15, 0.24, 0.33) for v in (0.6, 0.8)]
    berries = []
    for v in (0.12, 0.36):
        for u in [0.08 + 0.12 * i for i in range(8)]:
            x, y = P(u, v)
            berries.append(heart(x, y, 0.13, 30))
    for v in (0.6, 0.84):
        for u in [0.48 + 0.12 * i for i in range(4)]:
            x, y = P(u, v)
            berries.append(heart(x, y, 0.13, 30))
    plate = [ellipse(0.0, -1.7, 3.2, 0.4, 100)]
    plate = hide(plate, poly((-2.8, 0.2), (-2.8, -1.6), (2.2, -1.6), (2.9, -0.2), (2.9, 1.6)))
    candles = [rect(-0.1, 1.0, 0.1, 2.0), chain(quad((-0.1, 2.05), (0.0, 2.45), (0.0, 2.55), 6), quad((0.0, 2.55), (0.15, 2.3), (0.1, 2.05), 6)[1:])]
    return make("Flag Sheet Cake", [top] + sides + frost + layer + blue + berries + plate + candles + stars_((-2.4, 2.5, 0.25), (2.4, 2.6, 0.25)))


@design("patriotic_parade_car", T)
def parade_car(rng):
    body = chain([(-2.6, -0.9), (-3.0, -0.6), (-3.0, 0.2)], quad((-3.0, 0.45), (-2.6, 0.45), (-2.4, 0.45), 6)[1:],
                 [(-1.45, 0.45), (-1.35, 1.05)], quad((-1.35, 1.05), (-1.2, 1.2), (-0.9, 1.05), 6)[1:], [(-0.85, 0.45), (0.05, 0.45), (0.15, 1.05)],
                 quad((0.15, 1.05), (0.3, 1.2), (0.6, 1.05), 6)[1:], [(0.65, 0.45), (2.6, 0.45)], quad((2.6, 0.45), (3.15, 0.4), (3.15, -0.3), 8)[1:],
                 [(3.15, -0.6), (2.8, -0.9)])
    under = [[(-1.2, -0.9), (1.4, -0.9)]]
    fenders = [arc(-1.9, -0.95, 0.75, 0, math.pi, 20), arc(2.1, -0.95, 0.75, 0, math.pi, 20)]
    wheels = [circle(-1.9, -1.0, 0.62, 40), circle(2.1, -1.0, 0.62, 40), circle(-1.9, -1.0, 0.24, 16), circle(2.1, -1.0, 0.24, 16)]
    windshield = [poly((0.95, 0.45), (0.8, 1.3), (1.25, 1.3), (1.35, 0.45), closed=False)]
    hood = [[(1.6, 0.45), (1.6, -0.6)], [(2.0, 0.2), (2.6, 0.2)], [(2.0, 0.0), (2.6, 0.0)]]
    door = [[(-0.85, 0.45), (-0.85, -0.9)], [(0.75, 0.45), (0.75, -0.9)]]
    swag = [quad((-0.85, 0.3), (-0.05, -0.55), (0.75, 0.3), 16), quad((-0.85, 0.3), (-0.05, -0.15), (0.75, 0.3), 16), star(-0.05, -0.15, 0.15)]
    swag[2] = star(-0.05, -0.32, 0.14)
    lights = [circle(3.05, 0.1, 0.13, 10)]
    flags = []
    for x in (-2.75, 2.75):
        flags += [[(x, 0.45), (x, 2.0)]] + flag(x, 2.0, 0.9, 0.6, 0.05, 1.0, 5, 1, 2)
    ground = [[(-3.2, -1.64), (3.2, -1.64)]]
    parts = hide([body] + under + fenders, *wheels[:2])
    return make("Parade Convertible", parts + wheels + windshield + hood + door + swag + lights + flags + ground)
