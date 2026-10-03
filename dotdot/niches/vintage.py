"""Vintage Treasures niche: antique and retro objects."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "vintage"


def make(title, parts, hints=()):
    return Design(title, [p for p in parts if len(p) > 1], list(hints), T)


# ------------------------------------------------------------------ occlusion
# hide() removes the parts of strokes that fall inside "cover" shapes, so a
# front object can sit over a back one without lines crossing it; keep() is
# the opposite (clip a pattern to the inside of a shape).

def _inside(p, pg):
    x, y = p
    c = False
    n = len(pg)
    for i in range(n):
        x1, y1 = pg[i]
        x2, y2 = pg[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def _dense(s, step=0.04):
    out = [s[0]]
    for a, b in zip(s, s[1:]):
        k = max(1, int(math.dist(a, b) / step))
        for i in range(1, k + 1):
            out.append((a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k))
    return out


def _bbox(pg):
    xs = [p[0] for p in pg]
    ys = [p[1] for p in pg]
    return min(xs), min(ys), max(xs), max(ys)


def _plen(s):
    return sum(math.dist(a, b) for a, b in zip(s, s[1:]))


def _clip(strokes, covers, keep_in=False):
    cv = [(c, _bbox(c)) for c in covers if len(c) > 2]

    def gone(p):
        hit = any(b[0] <= p[0] <= b[2] and b[1] <= p[1] <= b[3] and _inside(p, c) for c, b in cv)
        return hit != keep_in

    def edge(a, b):
        for _ in range(14):
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            if gone(m):
                b = m
            else:
                a = m
        return a

    out = []
    for s in strokes:
        if len(s) < 2:
            continue
        closed = math.dist(s[0], s[-1]) < 1e-9
        d = _dense(s)
        fl = [gone(p) for p in d]
        if not any(fl):
            out.append(list(s))
            continue
        segs, cur = [], []
        for i, p in enumerate(d):
            if fl[i]:
                if cur:
                    cur.append(edge(d[i - 1], p))
                    segs.append(cur)
                    cur = []
            else:
                if not cur and i > 0:
                    cur = [edge(p, d[i - 1])]
                cur.append(p)
        if cur:
            segs.append(cur)
        if closed and len(segs) > 1 and not fl[0] and not fl[-1]:
            segs[0] = segs[-1] + segs[0][1:]
            segs.pop()
        out += [g for g in segs if len(g) > 1 and _plen(g) > 0.06]
    return out


def hide(strokes, *covers):
    return _clip(strokes, covers)


def keep(strokes, *covers):
    return _clip(strokes, covers, True)


def scene(*layers):
    """Layers listed back to front as (strokes, covers); a layer's covers
    hide every earlier layer's lines."""
    out = []
    for i, (st, _) in enumerate(layers):
        later = [c for _, cv in layers[i + 1:] for c in cv]
        out += hide(st, *later) if later else [list(s) for s in st]
    return out


def solid(*shapes):
    """A layer whose outlines are also its covers."""
    return (list(shapes), list(shapes))


# ------------------------------------------------------------------ pieces

def smooth(pts, it=3, closed=True):
    """Chaikin corner cutting."""
    p = list(pts)
    if closed and math.dist(p[0], p[-1]) < 1e-9:
        p = p[:-1]
    for _ in range(it):
        q = []
        n = len(p)
        rng_ = range(n) if closed else range(n - 1)
        if not closed:
            q.append(p[0])
        for i in rng_:
            a, b = p[i], p[(i + 1) % n]
            q.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            q.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        if not closed:
            q.append(p[-1])
        p = q
    return p + [p[0]] if closed else p


def seg(a, b):
    return [a, b]


def ticks(cx, cy, r0, r1, n, rot=math.pi / 2):
    return [[(cx + r0 * math.cos(rot + TAU * k / n), cy + r0 * math.sin(rot + TAU * k / n)),
             (cx + r1 * math.cos(rot + TAU * k / n), cy + r1 * math.sin(rot + TAU * k / n))] for k in range(n)]


def spokes(cx, cy, r0, r1, n, rot=0.0):
    return ticks(cx, cy, r0, r1, n, rot)


def hand(cx, cy, length, ang, w):
    """Spade-tipped clock hand pointing at angle ang (radians)."""
    c, s = math.cos(ang), math.sin(ang)
    pts = [(-0.12 * length, 0), (0.0, w), (0.7 * length, w * 0.5), (0.78 * length, w * 1.5), (length, 0),
           (0.78 * length, -w * 1.5), (0.7 * length, -w * 0.5), (0.0, -w), (-0.12 * length, 0)]
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]


def clock_face(cx, cy, r, h=10.1, m=2.0, n_ticks=12):
    out = [circle(cx, cy, r, 90)]
    out += ticks(cx, cy, 0.8 * r, 0.95 * r, n_ticks)
    out.append(hand(cx, cy, 0.55 * r, math.pi / 2 - TAU * h / 12, 0.05 * r))
    out.append(hand(cx, cy, 0.8 * r, math.pi / 2 - TAU * m / 12, 0.04 * r))
    return out


def gear(cx, cy, r, teeth, depth=0.12, rot=0.0):
    pts = []
    for k in range(teeth * 4 + 1):
        a = rot + TAU * k / (teeth * 4)
        rr = r if (k % 4) in (1, 2) else r - depth
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def coil(path, r, loops, n=None):
    """Coiled cord following a centre path (list of points)."""
    d = _dense(path, 0.02)
    L = _plen(d)
    n = n or loops * 24
    acc = [0.0]
    for a, b in zip(d, d[1:]):
        acc.append(acc[-1] + math.dist(a, b))
    out = []
    j = 0
    for i in range(n + 1):
        s = L * i / n
        while j < len(d) - 2 and acc[j + 1] < s:
            j += 1
        a, b = d[j], d[j + 1]
        f = (s - acc[j]) / max(1e-9, acc[j + 1] - acc[j])
        x, y = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
        tx, ty = (b[0] - a[0]), (b[1] - a[1])
        tl = math.hypot(tx, ty) or 1
        tx, ty = tx / tl, ty / tl
        th = TAU * loops * i / n
        out.append((x + r * (math.cos(th) * tx - math.sin(th) * ty),
                    y + r * (math.cos(th) * ty + math.sin(th) * tx)))
    return out


def reel(cx, cy, R, holes=3, rot=0.3):
    """Film reel: rim, hub and kidney-shaped cut-outs."""
    out = [circle(cx, cy, R, 100), circle(cx, cy, 0.14 * R, 20)]
    for k in range(holes):
        a0 = rot + TAU * k / holes + 0.35
        a1 = a0 + TAU / holes - 0.7
        r0, r1 = 0.32 * R, 0.8 * R
        out.append(chain(arc(cx, cy, r1, a0, a1, 24), arc(cx, cy, r0, a1, a0, 12), [(cx + r1 * math.cos(a0), cy + r1 * math.sin(a0))]))
    return out


def ball_feet(xs, y, r=0.18):
    return [arc(x, y, r, math.pi * 0.05, -math.pi * 1.05, 16) for x in xs]


def scallop(path, r, closed=False, out=1):
    """Run of small half-circle bumps along a polyline (lace / perforation edge)."""
    d = _dense(path, 0.01)
    L = _plen(d)
    k = max(1, int(round(L / (2 * r))))
    acc = [0.0]
    for a, b in zip(d, d[1:]):
        acc.append(acc[-1] + math.dist(a, b))

    def at(s):
        j = 0
        while j < len(d) - 2 and acc[j + 1] < s:
            j += 1
        a, b = d[j], d[j + 1]
        f = (s - acc[j]) / max(1e-9, acc[j + 1] - acc[j])
        tl = math.dist(a, b) or 1
        return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f), ((b[0] - a[0]) / tl, (b[1] - a[1]) / tl)

    pts = []
    m = k * 10
    for i in range(m + 1):
        s = L * i / m
        (x, y), (tx, ty) = at(min(s, L - 1e-6))
        h = abs(math.sin(math.pi * i / 10)) * r * 0.9 * out
        pts.append((x - ty * h, y + tx * h))
    return pts


def tube_rect(x0, y0, x1, y1):
    return rect(x0, y0, x1, y1)


# ================================================================== designs

@design("vintage_rotary_phone", T)
def rotary_phone(rng):
    body = chain(cubic((2.5, -2.4), (2.65, -1.2), (2.1, 0.3), (1.5, 0.45)), [(-1.5, 0.45)],
                 cubic((-1.5, 0.45), (-2.1, 0.3), (-2.65, -1.2), (-2.5, -2.4)))
    body_cv = body + [body[0]]
    foot = rrect(-2.75, -2.75, 2.75, -2.4, 0.12)
    dial = [circle(0, -1.0, 1.22, 90), circle(0, -1.0, 0.45, 40)]
    holes = [circle(0.86 * math.cos(math.radians(a)), -1.0 + 0.86 * math.sin(math.radians(a)), 0.15, 18)
             for a in range(60, 331, 30)]
    stop = [chain(arc(0, -1.0, 1.22, math.radians(-62), math.radians(-48), 4), [(1.05 * math.cos(math.radians(-50)), -1.0 + 1.05 * math.sin(math.radians(-50)))])]
    prongs = [chain([(-1.35, 0.45), (-1.35, 0.95)], [(-1.05, 0.95), (-1.05, 0.45)]),
              chain([(1.35, 0.45), (1.35, 0.95)], [(1.05, 0.95), (1.05, 0.45)])]
    handle = tube(quad((-2.0, 1.05), (0, 2.15), (2.0, 1.05), 40), 0.5)
    cups = [ellipse(-2.05, 0.95, 0.78, 0.42, 50), ellipse(2.05, 0.95, 0.78, 0.42, 50)]
    cup_rims = [ellipse(-2.05, 0.85, 0.55, 0.2, 40), ellipse(2.05, 0.85, 0.55, 0.2, 40)]
    cord = coil(cubic((-2.55, 0.6), (-3.6, 0.3), (-3.4, -1.5), (-2.5, -1.85), 40), 0.17, 9)
    return make("Rotary Telephone", scene(
        ([cord], []),
        ([body] + dial + holes + stop, [body_cv]),
        ([foot], [foot]),
        (prongs, []),
        ([handle], [handle]),
        (cups + cup_rims, cups)))


@design("vintage_candlestick_phone", T)
def candlestick_phone(rng):
    skirt_l = cubic((-1.3, -2.7), (-1.25, -2.0), (-0.45, -1.95), (-0.24, -1.5), 30)
    skirt = chain(skirt_l, [(0.24, -1.5)], mirror_x(skirt_l)[::-1])
    skirt_cv = skirt + [skirt[0]]
    base = rrect(-1.5, -2.95, 1.5, -2.7, 0.1)
    rings = [quad((-1.0, -2.45), (0, -2.3), (1.0, -2.45))]
    stem = [seg((-0.2, -1.5), (-0.2, 1.5)), seg((0.2, -1.5), (0.2, 1.5))]
    collar = [rect(-0.32, -1.45, 0.32, -1.25), rect(-0.3, 0.2, 0.3, 0.38)]
    head = rrect(-0.4, 1.45, 0.4, 2.2, 0.08)
    neck = tube([(0.35, 1.85), (0.8, 2.0)], 0.3)
    horn_top = quad((0.75, 2.12), (1.05, 2.25), (1.4, 2.65))
    horn_bot = quad((0.75, 1.88), (1.05, 1.75), (1.4, 1.35))
    horn_cv = horn_top + [(1.55, 2.0)] + horn_bot[::-1]
    rim = [ellipse(1.42, 2.0, 0.17, 0.66, 40, rot=-0.08), ellipse(1.43, 2.0, 0.08, 0.32, 24, rot=-0.08)]
    hook = [chain([(-0.2, 1.05), (-0.95, 1.2)], arc(-1.05, 1.32, 0.15, -0.6, 2.2, 10))]
    rec_cup = poly((-1.6, 1.62), (-0.7, 1.62), (-0.98, 1.1), (-1.32, 1.1))
    rec_top = ellipse(-1.15, 1.62, 0.45, 0.13, 30)
    rec = rrect(-1.32, -0.75, -0.98, 1.12, 0.12)
    bands = [seg((-1.32, -0.35), (-0.98, -0.35)), seg((-1.32, 0.7), (-0.98, 0.7))]
    cord = cubic((-1.15, -0.75), (-1.15, -1.7), (-2.3, -1.6), (-1.1, -2.35), 40)
    cord2 = cubic((1.2, -2.4), (2.2, -2.6), (2.3, -1.6), (2.9, -2.5), 40)
    return make("Candlestick Telephone", scene(
        ([cord, cord2], []),
        ([skirt] + rings, [skirt_cv]),
        ([base], [base]),
        (stem, []),
        (collar, collar),
        ([head], [head]),
        ([neck], [neck]),
        ([horn_top, horn_bot] + rim, [horn_cv, rim[0]]),
        (hook, []),
        ([rec_cup, rec_top, rec] + bands, [rec_cup, rec_top, rec])))


@design("vintage_wall_phone", T)
def wall_phone(rng):
    box = chain([(-1.3, -0.6), (-1.3, 2.4)]), chain([(1.3, -0.6), (1.3, 2.4)])
    panel = rect(-1.05, -0.35, 1.05, 2.15)
    crown = poly((-1.55, 2.4), (1.55, 2.4), (1.35, 2.8), (-1.35, 2.8))
    crown2 = poly((-1.0, 2.8), (1.0, 2.8), (0.8, 3.05), (-0.8, 3.05), closed=False)
    bells = [circle(-0.55, 1.65, 0.42, 40), circle(0.55, 1.65, 0.42, 40)]
    bell_in = [circle(-0.55, 1.65, 0.14, 16), circle(0.55, 1.65, 0.14, 16)]
    striker = [seg((0, 1.0), (0, 1.75)), circle(0, 1.85, 0.1, 12)]
    arm = rect(-0.14, 0.45, 0.14, 1.05)
    mouth = [circle(0, 0.35, 0.48, 40), circle(0, 0.35, 0.28, 30)]
    shelf = rect(-1.75, -0.88, 1.75, -0.6)
    lower = chain([(-1.1, -0.88), (-1.1, -2.85), (1.1, -2.85), (1.1, -0.88)])
    lpanel = rrect(-0.8, -2.5, 0.8, -1.2, 0.12)
    crank = [circle(1.62, 1.0, 0.15, 16), tube([(1.3, 1.0), (1.48, 1.0)], 0.14, cap=False)]
    crank_arm = tube([(1.62, 1.0), (1.75, 0.3)], 0.17)
    crank_knob = ellipse(1.98, 0.3, 0.3, 0.12, 20)
    hook = [seg((-1.3, 1.5), (-1.62, 1.58))]
    rec_cup = poly((-2.32, 1.95), (-1.42, 1.95), (-1.7, 1.45), (-2.04, 1.45))
    rec_top = ellipse(-1.87, 1.95, 0.45, 0.13, 30)
    rec = rrect(-2.04, -0.15, -1.7, 1.47, 0.12)
    cord = cubic((-1.87, -0.15), (-1.9, -0.7), (-1.45, -0.6), (-1.3, -0.25), 30)
    return make("Hand-Crank Wall Telephone", scene(
        (list(box) + [panel, lpanel, lower], []),
        (bells + bell_in, bells),
        (striker, [striker[1]]),
        ([arm], [arm]),
        (mouth, [mouth[0]]),
        ([crown, crown2], [crown]),
        ([shelf], [shelf]),
        (crank + [crank_arm], [crank_arm]),
        ([crank_knob], [crank_knob]),
        ([cord] + hook, []),
        ([rec_cup, rec_top, rec], [rec_cup, rec_top, rec])))


@design("vintage_typewriter", T)
def typewriter(rng):
    side = cubic((2.6, -2.3), (2.75, -1.3), (2.35, 0.0), (2.0, 0.5), 30)
    body = chain(mirror_x(side)[::-1], [(-2.0, 0.5), (2.0, 0.5)], side[::-1])
    body_cv = body + [body[0]]
    foot = rrect(-2.8, -2.6, 2.8, -2.3, 0.1)
    keys = []
    for row, (n, y) in enumerate([(8, -1.4), (9, -0.9), (9, -0.4)]):
        for k in range(n):
            x = (k - (n - 1) / 2) * 0.48 + (0.12 if row == 1 else 0)
            keys.append(circle(x, y, 0.17, 18))
    space = rrect(-1.4, -2.05, 1.4, -1.8, 0.12)
    platen = rrect(-2.7, 0.3, 2.7, 0.95, 0.3)
    knobs = [circle(-3.0, 0.62, 0.33, 30), circle(3.0, 0.62, 0.33, 30)]
    knob_in = [circle(-3.0, 0.62, 0.13, 14), circle(3.0, 0.62, 0.13, 14)]
    paper = rect(-1.45, 0.6, 1.45, 3.1)
    lines = [seg((-1.15, y), (x, y)) for y, x in [(2.75, 0.95), (2.45, 1.1), (2.15, 0.6), (1.85, 0.9)]]
    bail = seg((-2.0, 1.3), (2.0, 1.3))
    rollers = [rrect(-0.75, 1.18, -0.4, 1.42, 0.1), rrect(0.4, 1.18, 0.75, 1.42, 0.1)]
    lever = tube([(-2.5, 0.9), (-2.75, 1.35), (-3.35, 1.5)], 0.17)
    vent = [arc(0, 0.5, 1.0, math.pi + 0.15, 2 * math.pi - 0.15, 30)]
    return make("Manual Typewriter", scene(
        ([paper] + lines, [paper]),
        ([bail], []),
        (rollers, rollers),
        ([body] + keys + [space] + vent, [body_cv]),
        ([foot], [foot]),
        ([lever], [lever]),
        ([platen], [platen]),
        (knobs + knob_in, knobs)))


@design("vintage_treadle_sewing_machine", T)
def treadle_sewing_machine(rng):
    m = chain([(0.9, 0.9), (0.9, 1.6)], quad((0.9, 1.6), (0.9, 1.8), (0.7, 1.8), 8), [(-1.2, 1.8), (-1.2, 1.15), (-1.95, 1.15), (-1.95, 2.25)],
              quad((-1.95, 2.25), (-1.95, 2.55), (-1.65, 2.55), 8), [(0.85, 2.55)],
              cubic((0.85, 2.55), (1.25, 2.55), (1.5, 2.3), (1.5, 1.95), 12), [(1.5, 0.9)])
    m_cv = m + [m[0]]
    wheel = [circle(1.75, 1.9, 0.62, 50), circle(1.75, 1.9, 0.48, 40), circle(1.75, 1.9, 0.12, 12)] + spokes(1.75, 1.9, 0.12, 0.48, 5, 0.3)
    bed = rect(-2.4, 0.65, 2.0, 0.9)
    needle = [seg((-1.75, 1.15), (-1.75, 0.9)), seg((-1.45, 1.15), (-1.45, 0.98)), seg((-1.6, 0.98), (-1.3, 0.98))]
    decal = [lens((-0.9, 2.17), (0.45, 2.2), 0.16), spiral(-1.62, 1.85, 0.05, 0.22, 1.5)]
    spool = [rect(-0.22, 2.55, 0.22, 2.95), seg((-0.3, 2.95), (0.3, 2.95))]
    table = rrect(-2.95, 0.35, 2.95, 0.65, 0.06)
    drawers = [chain([(-2.7, 0.35), (-2.7, -1.0), (-1.45, -1.0), (-1.45, 0.35)]), seg((-2.7, -0.33), (-1.45, -0.33)),
               circle(-2.07, 0.01, 0.09, 12), circle(-2.07, -0.66, 0.09, 12)]
    drawer_cv = rect(-2.7, -1.0, -1.45, 0.4)

    def ironleg(x, top):
        out = poly((x - 0.17, top), (x - 0.6, -2.85), (x + 0.6, -2.85), (x + 0.17, top))
        return out, [lens((x, top - 0.25), (x, -2.4), 0.12), circle(x, -2.15, 0.17, 16)]
    l1, l1d = ironleg(-2.1, -1.0)
    l2, l2d = ironleg(2.4, 0.35)
    stretch = [seg((-1.6, -2.35), (2.0, -2.35)), seg((-1.6, -2.55), (2.0, -2.55))]
    treadle = poly((-1.2, -2.25), (1.2, -2.25), (1.45, -1.85), (-0.95, -1.85))
    lattice = keep([seg((x, -2.4), (x + 0.6, -1.7)) for x in (-1.0, -0.4, 0.2, 0.8)], treadle)
    fly = [circle(1.15, -0.85, 0.9, 70), circle(1.15, -0.85, 0.75, 60), circle(1.15, -0.85, 0.15, 14)] + spokes(1.15, -0.85, 0.15, 0.75, 6, 0.2)
    pitman = tube([(0.6, -1.95), (1.55, -1.3)], 0.12)
    belt = [seg((2.05, -0.85), (2.37, 1.9))]
    return make("Treadle Sewing Machine", scene(
        (belt, []),
        (fly, [fly[0]]),
        ([pitman], [pitman]),
        (stretch, []),
        ([treadle] + lattice, [treadle]),
        ([l1, l2] + l1d + l2d, [l1, l2]),
        (drawers, [drawer_cv]),
        ([table], [table]),
        (wheel, [wheel[0]]),
        ([bed], [bed]),
        ([m] + decal + needle + spool, [m_cv, spool[0]])))


@design("vintage_bellows_camera", T)
def bellows_camera(rng):
    n = 5
    top, bot = [], []
    for i in range(2 * n + 1):
        t = i / (2 * n)
        x = -1.55 + 2.15 * t
        top.append((x, 2.45 - 0.3 * t + (0.13 if i % 2 else 0)))
        bot.append((x, 0.55 + 0.3 * t - (0.13 if i % 2 else 0)))
    folds = [seg(top[i], bot[i]) for i in range(1, 2 * n, 2)]
    rear = rrect(-2.0, 0.3, -1.55, 2.65, 0.08)
    rear_in = rect(-1.92, 0.75, -1.63, 2.2)
    front = rrect(0.6, 0.65, 0.95, 2.35, 0.06)
    barrel = rect(0.95, 1.18, 1.42, 1.82)
    ring = chain([(1.42, 1.05), (1.85, 1.05)]), chain([(1.42, 1.95), (1.85, 1.95)]), seg((1.42, 1.05), (1.42, 1.95))
    glass = [ellipse(1.85, 1.5, 0.17, 0.45, 40), ellipse(1.86, 1.5, 0.08, 0.24, 20)]
    bed = rrect(-2.25, 0.05, 2.0, 0.35, 0.05)
    knob = [circle(1.2, 0.2, 0.2, 18)]
    head = rect(-0.55, -0.25, 0.55, 0.05)

    def legshape(a, b):
        return tube([a, b], lambda t: 0.24 - 0.1 * t)
    legs = [legshape((-0.35, -0.2), (-2.2, -2.95)), legshape((0.35, -0.2), (2.1, -2.95))]
    mid = legshape((0.0, -0.2), (0.15, -2.6))
    hose = cubic((1.6, 1.05), (1.8, 0.2), (2.6, 0.6), (2.6, -0.6), 30)
    bulb = ellipse(2.6, -0.95, 0.24, 0.38, 30)
    return make("Bellows Camera on a Tripod", scene(
        ([mid], [mid]),
        (legs, legs),
        ([head], [head]),
        ([top, bot] + folds, []),
        ([rear, rear_in], [rear]),
        ([front], [front]),
        ([barrel], [barrel]),
        (list(ring) + glass, [glass[0], rect(1.42, 1.05, 1.85, 1.95)]),
        ([hose], []),
        ([bulb], [bulb]),
        ([bed], [bed]),
        (knob, knob)))


@design("vintage_twin_lens_camera", T)
def twin_lens_camera(rng):
    body = rrect(-1.5, -2.45, 1.5, 2.0, 0.2)
    panel = rrect(-1.15, -2.15, 1.15, 1.75, 0.1)
    hood = poly((-1.25, 2.0), (1.25, 2.0), (1.05, 2.95), (-1.05, 2.95))
    hood_in = poly((-0.8, 2.15), (0.8, 2.15), (0.65, 2.75), (-0.65, 2.75))
    flaps = [poly((-1.25, 2.0), (-1.55, 2.65), (-1.05, 2.95), closed=False), poly((1.25, 2.0), (1.55, 2.65), (1.05, 2.95), closed=False)]
    vl = [circle(0, 0.85, r, 60) for r in (0.72, 0.52, 0.24)]
    tl = [circle(0, -1.15, r, 60) for r in (0.82, 0.6, 0.36)]
    glare = [arc(0, -1.15, 0.48, 2.0, 2.7, 8), arc(0, 0.85, 0.38, 2.0, 2.7, 8)]
    levers = [circle(-0.85, -0.12, 0.13, 14), circle(0.85, -0.12, 0.13, 14)]
    knob = rrect(-1.85, -0.65, -1.5, 0.45, 0.12)
    knob_lines = [seg((-1.85, y), (-1.62, y)) for y in (-0.35, -0.1, 0.15)]
    crank = [rrect(1.5, 0.15, 1.72, 0.75, 0.08), tube([(1.72, 0.45), (2.15, 0.7)], 0.15), circle(2.2, 0.73, 0.14, 14)]
    lugs = [rect(-1.65, 1.2, -1.5, 1.6), rect(1.5, 1.2, 1.65, 1.6)]
    strap = [cubic((-1.65, 1.4), (-2.6, 1.0), (-2.6, -2.0), (-2.2, -3.0), 30), cubic((1.65, 1.4), (2.6, 1.0), (2.6, -2.0), (2.5, -3.0), 30)]
    return make("Twin-Lens Reflex Camera", scene(
        (strap, []),
        ([body, panel] + vl + tl + glare + levers + lugs, [body]),
        ([hood, hood_in] + flaps, [hood]),
        ([knob] + knob_lines, [knob]),
        (crank, crank)))


@design("vintage_film_projector", T)
def film_projector(rng):
    body = rrect(-1.4, -0.8, 1.2, 0.7, 0.15)
    base = poly((-1.85, -1.45), (1.6, -1.45), (1.3, -0.65), (-1.55, -0.65))
    lens = poly((1.2, -0.35), (1.9, -0.35), (1.9, -0.45), (2.5, -0.45), (2.5, 0.35), (1.9, 0.35), (1.9, 0.25), (1.2, 0.25), closed=False)
    lens_cv = poly((1.1, -0.35), (1.9, -0.35), (1.9, -0.45), (2.5, -0.45), (2.5, 0.35), (1.9, 0.35), (1.9, 0.25), (1.1, 0.25))
    glass = ellipse(2.5, -0.05, 0.13, 0.4, 30)
    vents = [rrect(-1.1, y, -0.25, y + 0.15, 0.07) for y in (-0.5, -0.15, 0.2)]
    knob = [circle(0.55, -0.05, 0.3, 30), seg((0.55, -0.05), (0.75, 0.15))]
    arm1 = tube([(-0.7, 0.6), (-1.15, 2.0)], 0.2)
    arm2 = tube([(0.6, 0.6), (1.2, 1.75)], 0.2)
    r1 = reel(-1.15, 2.0, 1.0, rot=0.4)
    r2 = reel(1.2, 1.75, 0.82, rot=1.1)
    film = [seg((-0.2, 1.75), (-0.1, 0.7)), seg((0.1, 0.7), (0.42, 1.25))]
    feet = [rect(-1.6, -1.65, -1.2, -1.45), rect(1.0, -1.65, 1.4, -1.45)]
    beam = [seg((2.65, 0.25), (3.4, 0.95)), seg((2.65, -0.35), (3.4, -1.05))]
    return make("Reel-to-Reel Film Projector", scene(
        (r2, [r2[0]]),
        ([arm2], [arm2]),
        (film, []),
        ([arm1], [arm1]),
        (r1, [r1[0]]),
        ([base] + feet, [base]),
        ([body] + vents + knob, [body]),
        ([lens, glass] + beam, [lens_cv, glass])))


@design("vintage_clapperboard_reel", T)
def clapperboard_reel(rng):
    rot = -0.1

    def R(pts):
        return transform(pts, -0.4, -0.4, 1.0, rot)
    board = R(rect(-2.4, -2.3, 1.6, 0.6))
    rows = [R(seg((-2.4, -0.25), (1.6, -0.25))), R(seg((-2.4, -1.1), (1.6, -1.1))), R(seg((-1.0, 0.6), (-1.0, -0.25))),
            R(seg((0.3, 0.6), (0.3, -0.25))), R(seg((-0.4, -0.25), (-0.4, -1.1))), R(seg((-2.0, -1.7), (1.2, -1.7)))]
    stick = R(rect(-2.4, 0.6, 1.6, 1.08))
    stripes = keep([R(seg((x, 0.6), (x + 0.4, 1.08))) for x in (-1.9, -1.1, -0.3, 0.5, 1.3)], stick)
    top_pts = transform(rect(0, 0, 4.0, 0.48), -2.4, 1.12, 1.0, 0.38)
    top = R(top_pts)
    tstripes = keep([R(transform(seg((x, 0), (x + 0.4, 0.48)), -2.4, 1.12, 1.0, 0.38)) for x in (0.5, 1.3, 2.1, 2.9, 3.7)], top)
    hinge = R(circle(-2.4, 1.1, 0.13, 14))
    rl = reel(1.7, 1.6, 1.3, rot=0.2)
    path = cubic((2.85, 1.0), (3.4, -0.5), (1.4, -1.6), (3.0, -3.0), 50)
    film = tube(path, 0.75)
    dd = _dense(path, 0.01)
    holes, frames = [], []
    acc = 0
    nxt = 0.15
    for a, b in zip(dd, dd[1:]):
        acc += math.dist(a, b)
        if acc >= nxt:
            tx, ty = (b[0] - a[0]), (b[1] - a[1])
            tl = math.hypot(tx, ty)
            tx, ty = tx / tl, ty / tl
            ang = math.atan2(ty, tx)
            for side in (-1, 1):
                cx, cy = b[0] - ty * 0.27 * side, b[1] + tx * 0.27 * side
                holes.append(transform(rect(-0.08, -0.06, 0.08, 0.06), cx, cy, 1.0, ang))
            if int(round(nxt / 0.4)) % 2 == 0:
                frames.append([(b[0] - ty * 0.16, b[1] + tx * 0.16), (b[0] + ty * 0.16, b[1] - tx * 0.16)])
            nxt += 0.4
    return make("Clapperboard and Film Reel", scene(
        (rl, [rl[0]]),
        ([film] + holes + frames, [film]),
        ([board] + rows, [board]),
        ([stick] + stripes, [stick]),
        ([top] + tstripes, [top]),
        ([hinge], [hinge])))


@design("vintage_tv_rabbit_ears", T)
def tv_rabbit_ears(rng):
    cab = rrect(-2.7, -1.6, 2.7, 1.7, 0.35)
    bezel = rrect(-2.45, -1.35, 1.05, 1.45, 0.6)
    screen = rrect(-2.25, -1.15, 0.85, 1.25, 0.5)
    glare = arc(-0.7, 0.05, 1.0, 1.95, 2.65, 12)
    k1 = [circle(1.85, 0.8, 0.42, 36), circle(1.85, 0.8, 0.14, 14)] + ticks(1.85, 0.8, 0.5, 0.62, 8)
    k2 = [circle(1.85, -0.1, 0.28, 24), seg((1.85, -0.1), (2.03, 0.08))]
    grille = rrect(1.35, -1.38, 2.35, -0.6, 0.1)
    glines = [seg((1.45, y), (2.25, y)) for y in (-0.8, -0.99, -1.18)]

    def lg(a, b):
        return tube([a, b], lambda t: 0.26 - 0.13 * t)
    legs = [lg((-2.1, -1.55), (-2.55, -2.85)), lg((2.1, -1.55), (2.55, -2.85))]
    blegs = [lg((-1.3, -1.55), (-1.1, -2.6)), lg((1.3, -1.55), (1.1, -2.6))]
    dome = chain(arc(0.0, 1.7, 0.45, 0, math.pi, 20))
    dome_cv = dome + [dome[0]]
    rods = [seg((-0.12, 2.05), (-1.7, 3.5)), seg((0.12, 2.05), (1.95, 3.35))]
    tips = [circle(-1.75, 3.55, 0.1, 12), circle(2.0, 3.4, 0.1, 12)]
    return make("Retro Television with Rabbit Ears", scene(
        (blegs, blegs),
        (rods, []),
        (tips, tips),
        ([dome], [dome_cv]),
        (legs, legs),
        ([cab, bezel, screen, glare, grille] + k1 + k2 + glines, [cab])))


@design("vintage_magic_lantern", T)
def magic_lantern(rng):
    body = chain([(-1.4, -1.1), (-1.4, 0.9), (0.9, 0.9), (0.9, -1.1)])
    body_cv = rect(-1.4, -1.15, 0.9, 0.9)
    band = seg((-1.4, 0.6), (0.9, 0.6))
    chim = [seg((-0.8, 0.9), (-0.8, 2.0)), seg((-0.2, 0.9), (-0.2, 2.0))]
    cap = poly((-1.1, 2.0), (0.1, 2.0), (-0.15, 2.32), (-0.85, 2.32))
    dome = chain(arc(-0.5, 2.32, 0.33, 0, math.pi, 16))
    fin = circle(-0.5, 2.78, 0.11, 12)
    holes = [circle(-0.5, 1.25, 0.1, 12), circle(-0.5, 1.62, 0.1, 12)]
    win = [circle(-0.5, -0.2, 0.62, 50), circle(-0.5, -0.2, 0.48, 40)]
    flame = chain(quad((-0.5, 0.22), (-0.72, -0.1), (-0.72, -0.42), 10), arc(-0.5, -0.42, 0.22, math.pi, 2 * math.pi, 12),
                  quad((-0.28, -0.42), (-0.28, -0.1), (-0.5, 0.22), 10))
    carrier = rect(0.95, -1.4, 1.25, 1.15)
    tube1 = chain([(0.9, -0.62), (0.95, -0.62)]), chain([(1.25, -0.5), (2.0, -0.5), (2.0, -0.62), (2.7, -0.62), (2.7, 0.42), (2.0, 0.42), (2.0, 0.3), (1.25, 0.3)])
    t_cv = rect(1.2, -0.62, 2.7, 0.42)
    glass = ellipse(2.7, -0.1, 0.14, 0.5, 30)
    knob = circle(1.65, -0.75, 0.13, 12)
    knob_stem = seg((1.65, -0.5), (1.65, -0.62))
    base = rrect(-1.75, -1.45, 1.55, -1.1, 0.08)
    feet = ball_feet([-1.45, 1.25], -1.45, 0.2)
    handle = chain([(-1.4, 0.2)], quad((-2.1, 0.25), (-2.1, -0.75), (-1.4, -0.7), 16))
    return make("Magic Lantern Projector", scene(
        (feet, []),
        ([base], [base]),
        ([handle], []),
        ([body, band] + chim + holes + win + [flame], [body_cv]),
        ([cap, dome, fin], [cap, fin]),
        (list(tube1) + [knob_stem], [t_cv]),
        ([knob], [knob]),
        ([glass], [glass]),
        ([carrier], [carrier])))


@design("vintage_mantel_clock", T)
def mantel_clock(rng):
    a = 0.07
    sx, sy = -1.62 * math.cos(a), 0.25 + 1.62 * math.sin(a)
    wing = chain([(-2.7, -1.2), (-2.7, -0.55)], cubic((-2.7, -0.55), (-2.0, -0.45), (-1.7, -0.05), (sx, sy), 20))
    outline = chain(wing, arc(0, 0.25, 1.62, math.pi - a, a, 70), mirror_x(wing)[::-1])
    base = rrect(-2.95, -1.6, 2.95, -1.2, 0.1)
    feet = ball_feet([-2.5, 2.5], -1.6, 0.2)
    bezel = circle(0, 0.25, 1.32, 90)
    face = clock_face(0, 0.25, 1.1)
    hub = circle(0, 0.25, 0.08, 10)
    inlay = [lens((-2.45, -0.85), (-1.55, -0.85), 0.22), lens((1.55, -0.85), (2.45, -0.85), 0.22)]
    return make("Tambour Mantel Clock", [outline, base, bezel, hub] + face + inlay + feet)


@design("vintage_grandfather_clock", T)
def grandfather_clock(rng):
    plinth = chain([(-1.1, -1.9), (-1.1, -3.0), (1.1, -3.0), (1.1, -1.9)])
    ppanel = rrect(-0.75, -2.75, 0.75, -2.15, 0.1)
    feet = [poly((-1.15, -3.0), (-0.55, -3.0), (-0.65, -3.25), (-1.1, -3.25), closed=False),
            poly((1.15, -3.0), (0.55, -3.0), (0.65, -3.25), (1.1, -3.25), closed=False)]
    m1 = rect(-1.22, -1.9, 1.22, -1.68)
    waist = [seg((-0.8, -1.68), (-0.8, 1.1)), seg((0.8, -1.68), (0.8, 1.1))]
    door = chain([(-0.55, 0.45), (-0.55, -1.45), (0.55, -1.45), (0.55, 0.45)], arc(0, 0.45, 0.55, 0, math.pi, 24))
    rod = seg((0, 0.85), (0, -0.55))
    bob = [circle(0, -0.85, 0.3, 30), circle(0, -0.85, 0.13, 14)]
    weights = [rrect(-0.42, -0.25, -0.2, 0.5, 0.05), rrect(0.2, 0.05, 0.42, 0.8, 0.05)]
    wchains = [seg((-0.31, 0.5), (-0.31, 0.95)), seg((0.31, 0.8), (0.31, 0.95))]
    m2 = rect(-1.02, 1.1, 1.02, 1.3)
    hood = [seg((-0.95, 1.3), (-0.95, 3.15)), seg((0.95, 1.3), (0.95, 3.15))]
    dial = chain([(-0.75, 2.35), (-0.75, 1.42), (0.75, 1.42), (0.75, 2.35)], arc(0, 2.35, 0.75, 0, math.pi, 30))
    face = clock_face(0, 1.88, 0.42)
    moon_arc = arc(0, 2.35, 0.6, 0.05, math.pi - 0.05, 24)
    humps = [arc(-0.35, 2.35, 0.2, 0, math.pi, 10), arc(0.35, 2.35, 0.2, 0, math.pi, 10)]
    moon = circle(0, 2.75, 0.14, 14)
    m3 = rect(-1.12, 3.15, 1.12, 3.32)
    neck = cubic((-1.05, 3.32), (-0.95, 3.95), (-0.55, 3.55), (-0.35, 3.8), 20)
    pediment = [neck, mirror_x(neck), spiral(-0.35, 3.62, 0.03, 0.17, 1.2, 30, rot=1.6), mirror_x(spiral(-0.35, 3.62, 0.03, 0.17, 1.2, 30, rot=1.6))]
    urn = chain(quad((-0.12, 3.32), (-0.25, 3.6), (-0.1, 3.75), 8), [(0.1, 3.75)], quad((0.1, 3.75), (0.25, 3.6), (0.12, 3.32), 8))
    finial = circle(0, 3.9, 0.14, 14)
    return make("Grandfather Clock", [plinth, ppanel, m1, door, rod, m2, dial, moon_arc, moon, m3, urn, finial]
                + feet + waist + bob + weights + wchains + hood + face + humps + pediment)


@design("vintage_cuckoo_clock", T)
def cuckoo_clock(rng):
    house = chain([(-1.5, 1.05), (-1.5, -1.4), (1.5, -1.4), (1.5, 1.05)])
    roof = poly((-2.45, 0.7), (0, 2.65), (2.45, 0.7), (2.15, 0.5), (0, 2.28), (-2.15, 0.5))
    leaves = []
    for k in range(5):
        t = (k + 0.5) / 5
        x, y = -2.3 + 2.15 * t, 0.6 + 1.7 * t
        leaves.append(lens((x, y), (x - 0.35, y - 0.45), 0.3))
        leaves.append(mirror_x(lens((x, y), (x - 0.35, y - 0.45), 0.3)))
    crest = [lens((0, 2.65), (0, 3.4), 0.3), lens((0, 2.65), (-0.6, 3.15), 0.28), lens((0, 2.65), (0.6, 3.15), 0.28)]
    face = clock_face(0, -0.35, 0.8)
    side_leaves = [lens((-1.45, -1.3), (-1.1, -0.55), 0.3), mirror_x(lens((-1.45, -1.3), (-1.1, -0.55), 0.3)),
                   lens((-1.45, 0.75), (-1.05, 0.15), 0.3), mirror_x(lens((-1.45, 0.75), (-1.05, 0.15), 0.3))]
    door = rect(-0.3, 0.6, 0.3, 1.3)
    open_door = poly((-0.3, 0.6), (-0.65, 0.75), (-0.65, 1.42), (-0.3, 1.3), closed=False)
    bird = chain(ellipse(0.15, 1.0, 0.32, 0.17, 30))
    head = circle(0.45, 1.18, 0.15, 16)
    beak = poly((0.58, 1.24), (0.85, 1.2), (0.6, 1.12), closed=False)
    tail = poly((-0.15, 1.05), (-0.45, 1.2), (-0.38, 0.95), closed=False)
    rod = seg((0, -1.4), (0, -2.2))
    bob = lens((0, -2.15), (0, -3.05), 0.35)
    bob_vein = seg((0, -2.25), (0, -2.95))

    def cone(x, y):
        out = [ellipse(x, y, 0.3, 0.55, 30)]
        for k in range(3):
            yy = y + 0.3 - k * 0.3
            out.append(poly((x - 0.26, yy + 0.08), (x, yy - 0.12), (x + 0.26, yy + 0.08), closed=False))
        return out
    weights = cone(-0.95, -2.45) + cone(0.95, -2.85)
    chains_ = [seg((-0.95, -1.4), (-0.95, -1.9)), seg((0.95, -1.4), (0.95, -2.3))]
    return make("Cuckoo Clock", scene(
        ([house, rod, bob_vein, door] + face + chains_ + weights + crest, []),
        (side_leaves, side_leaves),
        ([bob], [bob]),
        ([open_door, tail], []),
        ([bird, head, beak], [bird, head]),
        ([roof] + leaves, [roof] + leaves)))


@design("vintage_alarm_clock", T)
def alarm_clock(rng):
    cy = -0.3
    body = circle(0, cy, 1.75, 100)
    bezel = circle(0, cy, 1.5, 90)
    face = clock_face(0, cy, 1.3, h=7.0, m=0.0)
    alarm = [seg((0, cy), (1.0 * math.cos(math.radians(30)), cy + 1.0 * math.sin(math.radians(30))))]
    hub = circle(0, cy, 0.09, 10)

    def bell(side):
        a = math.radians(90 + 38 * side)
        bx, by = 1.95 * math.cos(a), cy + 1.95 * math.sin(a)
        rot = a - math.pi / 2
        dome = chain(arc(0, 0, 0.72, 0, math.pi, 30), [(0.72, 0)])
        lip = rect(-0.8, -0.12, 0.8, 0.0)
        knob = circle(0, 0.82, 0.12, 12)
        post = seg((0, -0.12), (0, -0.35))
        return [transform(p, bx, by, 1.0, rot) for p in (dome, lip, knob, post)]
    bl, br = bell(-1), bell(1)
    striker = [seg((0, 1.45), (0, 2.05)), circle(0, 2.15, 0.13, 14)]
    feet = [tube([(-0.95, cy - 1.4), (-1.45, -2.75)], 0.2), tube([(0.95, cy - 1.4), (1.45, -2.75)], 0.2),
            ellipse(-1.5, -2.8, 0.3, 0.12, 16), ellipse(1.5, -2.8, 0.3, 0.12, 16)]
    ring = []
    for side in (-1, 1):
        c = (2.0 * side, 2.0)
        for r in (0.55, 0.85):
            a0 = math.radians(90 + 70 * side) if side < 0 else math.radians(-10)
            ring.append(arc(c[0] + 0.0, c[1], r, math.radians(100) if side < 0 else math.radians(-20),
                            math.radians(200) if side < 0 else math.radians(80), 10))
    return make("Twin-Bell Alarm Clock", scene(
        (feet, feet[:2]),
        (striker, [striker[1]]),
        (bl + br, [bl[0] + [bl[0][0]], br[0] + [br[0][0]], bl[1], br[1]]),
        ([body, bezel, hub] + face + alarm, [body]),
        (ring, [])))


@design("vintage_carriage_clock", T)
def carriage_clock(rng):
    base = rrect(-1.6, -2.15, 1.6, -1.8, 0.08)
    feet = ball_feet([-1.3, 1.3], -2.15, 0.17)
    case = chain([(-1.35, -1.8), (-1.35, 1.6)]), chain([(1.35, -1.8), (1.35, 1.6)])
    cols = [seg((-1.05, -1.8), (-1.05, 1.6)), seg((1.05, -1.8), (1.05, 1.6))]
    caps = [rect(-1.45, 1.2, -0.95, 1.4), rect(0.95, 1.2, 1.45, 1.4), rect(-1.45, -1.6, -0.95, -1.4), rect(0.95, -1.6, 1.45, -1.4)]
    cornice = rrect(-1.6, 1.6, 1.6, 1.92, 0.08)
    top = poly((-1.3, 1.92), (1.3, 1.92), (1.15, 2.12), (-1.15, 2.12))
    dial_plate = rrect(-0.85, -0.35, 0.85, 1.2, 0.1)
    face = clock_face(0, 0.42, 0.65, h=3.2, m=8.0)
    g = gear(-0.2, -1.0, 0.42, 12, 0.1)
    g_in = circle(-0.2, -1.0, 0.12, 12)
    bal = [circle(0.55, -0.95, 0.3, 24), seg((0.25, -0.95), (0.85, -0.95))]
    handle = tube(chain([(-0.9, 2.12), (-0.9, 2.35)], quad((-0.9, 2.35), (-0.9, 3.0), (0, 3.0), 12), quad((0, 3.0), (0.9, 3.0), (0.9, 2.35), 12), [(0.9, 2.12)]), 0.16)
    hinges = [circle(-0.9, 2.2, 0.12, 12), circle(0.9, 2.2, 0.12, 12)]
    return make("Brass Carriage Clock", scene(
        (list(case) + cols + [dial_plate, g, g_in] + face + bal, []),
        (caps, caps),
        ([handle], [handle]),
        (hinges, hinges),
        ([top], [top]),
        ([cornice], [cornice]),
        ([base], [base]),
        (feet, [])))


@design("vintage_tiffany_lamp", T)
def tiffany_lamp(rng):
    side = cubic((-2.75, 0.25), (-2.45, 1.75), (-1.1, 2.35), (0, 2.4), 30)
    hem = quad((-2.75, 0.25), (0, -0.25), (2.75, 0.25), 40)
    shade = chain(side, mirror_x(side)[::-1], hem[::-1])
    cap = chain(arc(0, 2.4, 0.45, 0, math.pi, 16))
    cap_cv = cap + [cap[0]]
    knob = circle(0, 3.0, 0.15, 14)
    bands = [quad((-2.55, 0.9), (0, 0.4), (2.55, 0.9), 40), quad((-1.95, 1.75), (0, 1.35), (1.95, 1.75), 40)]
    rad = []
    for x in (-1.9, -0.95, 0.0, 0.95, 1.9):
        rad.append(quad((x * 0.18, 2.4), (x * 0.75, 1.7), (x, 0.2 - 0.25 * (1 - (x / 2.75) ** 2)), 20))
    rad = keep(rad, shade)
    flowers = []
    for x in (-2.0, -1.0, 0.0, 1.0, 2.0):
        y = 1.12 - 0.35 * (1 - (x / 2.6) ** 2) + 0.15
        flowers.append(circle(x + 0.47, y, 0.18, 16))
    flowers = keep(flowers, shade)
    drops = [lens((-0.9, 2.0), (-0.3, 2.15), 0.3), lens((0.3, 2.15), (0.9, 2.0), 0.3)]
    fringe = scallop(hem, 0.18, out=-1)
    stem = tube([(0, -2.35), (0, 0.0)], lambda t: 0.3 + 0.55 * math.exp(-((t - 0.35) / 0.16) ** 2))
    foot_s = cubic((-1.45, -2.85), (-1.35, -2.4), (-0.6, -2.45), (-0.2, -2.25), 20)
    foot = chain(foot_s, mirror_x(foot_s)[::-1], [(-1.45, -2.85)])
    ring = rect(-0.35, -2.3, 0.35, -2.1)
    chains_ = [seg((-0.6, -0.15), (-0.6, -1.0)), seg((0.6, -0.15), (0.6, -0.75))]
    beads = [circle(-0.6, -1.12, 0.12, 12), circle(0.6, -0.87, 0.12, 12)]
    return make("Stained Glass Dome Lamp", scene(
        ([stem], [stem]),
        (chains_ + beads, beads),
        ([foot], [foot]),
        ([ring], [ring]),
        ([shade, fringe] + bands + rad + flowers + drops, [shade]),
        ([cap], [cap_cv]),
        ([knob], [knob])))


@design("vintage_steamer_trunk", T)
def steamer_trunk(rng):
    dx, dy = 0.95, 0.55
    x0, x1, y0, y1, yl, yt = -2.6, 1.4, -2.2, 0.4, 0.4, 0.95
    front = rect(x0, y0, x1, yt)
    lid_line = seg((x0, yl), (x1, yl))
    side = poly((x1, y0), (x1 + dx, y0 + dy), (x1 + dx, yt + dy), (x1, yt), closed=False)
    side_lid = seg((x1, yl), (x1 + dx, yl + dy))
    topf = poly((x0, yt), (x0 + dx, yt + dy), (x1 + dx, yt + dy), closed=False)
    slats = []
    for x in (-1.75, 0.35):
        slats += [seg((x, y0), (x, yt)), seg((x + 0.3, y0), (x + 0.3, yt)),
                  seg((x, yt), (x + dx, yt + dy)), seg((x + 0.3, yt), (x + 0.3 + dx, yt + dy))]
    band = [seg((x0, -1.0), (x1, -1.0)), seg((x0, -1.25), (x1, -1.25)), seg((x1, -1.0), (x1 + dx, -1.0 + dy)), seg((x1, -1.25), (x1 + dx, -1.25 + dy))]
    corners = [poly((x0, y0), (x0 + 0.45, y0), (x0, y0 + 0.45)), poly((x1, y0), (x1 - 0.45, y0), (x1, y0 + 0.45)),
               poly((x0, yt), (x0 + 0.45, yt), (x0, yt - 0.45)), poly((x1, yt), (x1 - 0.45, yt), (x1, yt - 0.45))]
    lock = rrect(-0.85, 0.1, -0.35, 0.75, 0.08)
    keyhole = [circle(-0.6, 0.5, 0.08, 10), poly((-0.66, 0.44), (-0.54, 0.44), (-0.6, 0.25))]
    latches = [rrect(-2.35, 0.2, -2.05, 0.6, 0.06), rrect(0.95, 0.2, 1.25, 0.6, 0.06)]
    handle = [chain(quad((x1 + 0.25, -0.15), (x1 + 0.45, -0.6), (x1 + 0.7, -0.0), 14)),
              rect(x1 + 0.2, -0.12, x1 + 0.32, 0.12), rect(x1 + 0.63, 0.04, x1 + 0.75, 0.28)]
    return make("Steamer Trunk", scene(
        ([front, lid_line, side, side_lid, topf] + slats + band + handle, []),
        (corners, corners),
        (latches, latches),
        ([lock] + keyhole, [lock])))


@design("vintage_suitcase_stickers", T)
def suitcase_stickers(rng):
    case = rrect(-2.7, -1.8, 2.7, 1.4, 0.3)
    seam = seg((-2.7, 0.9), (2.7, 0.9))
    grip = tube(quad((-0.75, 1.58), (0, 2.3), (0.75, 1.58), 24), 0.24)
    brackets = [rect(-0.95, 1.4, -0.6, 1.65), rect(0.6, 1.4, 0.95, 1.65)]
    latches = [rect(x - 0.22, 0.7, x + 0.22, 1.12) for x in (-1.75, 1.75)]
    lat_d = [circle(x, 0.83, 0.07, 10) for x in (-1.75, 1.75)]
    straps = [seg((x, -1.8), (x, 1.4)) for x in (-1.15, -0.85, 0.85, 1.15)]
    buckles = [rect(x - 0.25, -0.05, x + 0.25, 0.35) for x in (-1.0, 1.0)]
    corners = [arc(-2.4, 1.1, 0.5, math.pi * 0.5, math.pi, 8)[::-1] + [], arc(2.4, 1.1, 0.5, 0, math.pi * 0.5, 8),
               arc(-2.4, -1.5, 0.5, math.pi, 1.5 * math.pi, 8), arc(2.4, -1.5, 0.5, 1.5 * math.pi, 2 * math.pi, 8)]
    corners = [chain([(-2.7, 0.6)], quad((-2.2, 0.6), (-2.1, 0.9), (-2.1, 1.4), 8)), chain([(2.7, 0.6)], quad((2.2, 0.6), (2.1, 0.9), (2.1, 1.4), 8)),
               chain([(-2.7, -1.3)], quad((-2.2, -1.3), (-2.1, -1.5), (-2.1, -1.8), 8)), chain([(2.7, -1.3)], quad((2.2, -1.3), (2.1, -1.5), (2.1, -1.8), 8))]
    s1 = circle(-1.85, -0.55, 0.55, 40)
    s1d = keep([poly((-2.4, -0.8), (-2.05, -0.3), (-1.85, -0.55), (-1.55, -0.15), (-1.25, -0.75), closed=False), circle(-1.55, -0.6, 0.0001, 3)], s1)
    s2 = ellipse(0.0, -0.75, 0.75, 0.48, 40)
    s2d = [star(0.0, -0.75, 0.32, 5, 0.45)]
    s3 = scallop(rect(1.35, -1.4, 2.4, -0.3), 0.1, out=1)
    s3_cv = rect(1.3, -1.45, 2.45, -0.25)
    ship = [poly((1.6, -1.0), (2.15, -1.0), (2.25, -0.8), (1.5, -0.8)), rect(1.75, -0.8, 1.95, -0.5)]
    s4 = poly((-0.1, 0.2), (0.35, 0.65), (-0.1, 1.1), (-0.55, 0.65))
    s4_cv = s4
    s4d = [arc(-0.1, 0.65, 0.18, 0, TAU, 14)]
    feet = [rrect(-2.2, -2.0, -1.7, -1.8, 0.06), rrect(1.7, -2.0, 2.2, -1.8, 0.06)]
    return make("Suitcase with Travel Stickers", scene(
        ([grip], [grip]),
        (brackets, brackets),
        ([case, seam] + straps + corners + feet, []),
        (latches + lat_d, latches),
        (buckles, buckles),
        ([s1] + s1d, [s1]),
        ([s2] + s2d, [s2]),
        ([s3] + ship, [s3_cv]),
        ([s4] + s4d, [s4_cv])))


@design("vintage_hatbox_hat", T)
def hatbox_hat(rng):
    lid_top = ellipse(0, 0.0, 2.3, 0.55, 80)
    lid_band = chain([(-2.3, 0.0), (-2.3, -0.5)], [(2.3 * math.cos(t), -0.5 + 0.55 * math.sin(t)) for t in [math.pi + math.pi * i / 40 for i in range(41)]], [(2.3, 0.0)])
    lid_cv = chain(lid_band, arc(0, 0, 2.3, 0, math.pi, 30))
    box = chain([(-2.1, -0.6), (-2.1, -2.6)], [(2.1 * math.cos(t), -2.6 + 0.5 * math.sin(t)) for t in [math.pi + math.pi * i / 40 for i in range(41)]], [(2.1, -0.6)])
    stripes = []
    for k in range(-3, 4):
        x = 2.1 * math.sin(k * 0.4)
        yb = -2.6 - 0.5 * math.sqrt(max(0, 1 - (x / 2.1) ** 2))
        stripes.append(seg((x, -0.8), (x, yb)))
    brim = ellipse(-0.1, 0.55, 2.3, 0.62, 80)
    crown = chain([(-1.3, 0.62)], cubic((-1.3, 0.62), (-1.45, 2.55), (1.25, 2.6), (1.1, 0.62), 30))
    crown_cv = crown + [crown[0]]
    band = [quad((-1.33, 1.0), (-0.1, 0.65), (1.14, 1.0), 16), quad((-1.36, 1.38), (-0.1, 1.03), (1.18, 1.38), 16)]
    band_cv = chain(band[0], band[1][::-1], [band[0][0]])
    bow = [lens((0.95, 1.2), (1.55, 1.75), 0.35), lens((0.95, 1.2), (1.65, 0.8), 0.35), circle(0.97, 1.2, 0.13, 12)]
    fc = cubic((0.95, 1.3), (1.9, 2.0), (2.3, 2.8), (2.95, 3.4), 40)
    feather = tube(fc, lambda t: 0.8 * math.sin(math.pi * min(1, t * 1.1)) ** 0.6 + 0.02)
    quill = fc
    notches = []
    dd = fc
    for i in (12, 20, 28):
        a, b = dd[i], dd[i + 1]
        tx, ty = b[0] - a[0], b[1] - a[1]
        tl = math.hypot(tx, ty)
        notches.append([a, (a[0] - ty / tl * 0.3 + tx / tl * 0.2, a[1] + tx / tl * 0.3 + ty / tl * 0.2)])
    return make("Hatbox and Feathered Hat", scene(
        ([box] + stripes, [box + [box[0]]]),
        ([lid_top, lid_band], [lid_cv]),
        ([feather, quill] + notches, [feather]),
        ([brim], [brim]),
        ([crown], [crown_cv]),
        (band, [band_cv]),
        (bow, bow)))


@design("vintage_lace_parasol", T)
def lace_parasol(rng):
    rot = 0.3
    ends = [(-2.7, 0.25), (-1.9, -0.05), (-0.7, -0.22), (0.6, -0.22), (1.85, -0.05), (2.7, 0.25)]
    apex = (0, 2.15)
    side = cubic((-2.7, 0.25), (-2.35, 1.55), (-1.0, 2.15), apex, 30)
    hem = []
    for a, b in zip(ends, ends[1:]):
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 0.35)
        hem = chain(hem, quad(a, m, b, 16))
    canopy = chain(side, mirror_x(side)[::-1], hem[::-1])
    ribs = [quad(apex, (e[0] * 0.75, 1.7 + 0.1 * abs(e[0])), e, 20) for e in ends[1:-1]]
    ruffle = scallop(hem, 0.14, out=-1)
    hem2 = [(x, y + 0.38) for x, y in hem]
    lace = keep([scallop(hem2, 0.12, out=-1)], canopy)
    tip = [seg(apex, (0, 2.6)), circle(0, 2.7, 0.1, 12)]
    shaft = tube([(0, -0.3), (0, -3.0)], 0.14)
    crook = tube(chain([(0, -3.0)], arc(0.4, -3.0, 0.4, math.pi, 2 * math.pi, 16), [(0.8, -2.75)]), 0.2)
    parts = scene(
        ([shaft, crook], [shaft]),
        ([canopy, ruffle] + ribs + lace, [canopy]),
        (tip, []))
    return make("Lace Parasol", [transform(p, 0, 0, 1.0, rot) for p in parts])


@design("vintage_cameo_brooch", T)
def cameo_brooch(rng):
    outer = [((2.3 + 0.1 * math.cos(24 * t)) * math.cos(t), (2.9 + 0.1 * math.cos(24 * t)) * math.sin(t)) for t in [TAU * i / 480 for i in range(481)]]
    rim = ellipse(0, 0, 2.05, 2.62, 100)
    field = ellipse(0, 0, 1.8, 2.35, 100)
    face = smooth([(0.15, 1.45), (0.42, 1.12), (0.5, 0.82), (0.47, 0.66), (0.82, 0.32), (0.58, 0.24), (0.64, 0.1), (0.54, 0.03),
                   (0.62, -0.05), (0.47, -0.2), (0.53, -0.38), (0.3, -0.55), (0.22, -0.85), (0.32, -1.25), (0.95, -1.6), (1.3, -2.2)], 2, closed=False)
    back = smooth([(0.15, 1.45), (-0.4, 1.62), (-1.0, 1.35), (-1.35, 0.9), (-1.3, 0.35), (-0.85, 0.1), (-0.6, -0.15), (-0.5, -0.7),
                   (-0.95, -1.35), (-1.45, -1.9)], 2, closed=False)
    bun = circle(-0.95, 0.85, 0.42, 36)
    curls = [spiral(-0.95, 0.85, 0.05, 0.3, 1.6, 40), spiral(0.0, 1.1, 0.05, 0.2, 1.2, 30, rot=2.0)]
    waves = [cubic((0.1, 1.38), (-0.3, 1.2), (-0.35, 0.75), (-0.6, 0.55), 16)]
    ringlet = tube(cubic((-0.75, 0.2), (-0.5, -0.1), (-0.85, -0.35), (-0.6, -0.65), 16), 0.16)
    ear = arc(-0.05, 0.35, 0.16, math.pi * 0.4, math.pi * 1.6, 10)
    eye_ = quad((0.25, 0.62), (0.36, 0.56), (0.45, 0.62), 6)
    drape = [cubic((-1.45, -1.6), (-0.6, -1.4), (0.2, -1.9), (1.1, -1.75), 20), cubic((-1.2, -2.0), (-0.5, -1.75), (0.2, -2.25), (0.9, -2.15), 20)]
    bail = [circle(0, 3.2, 0.22, 20)]
    inner = keep([face, back, bun, ear, eye_, ringlet] + curls + waves + drape, field)
    return make("Cameo Brooch", [outer, rim, field] + inner + bail)


@design("vintage_powder_compact", T)
def powder_compact(rng):
    lid = ellipse(0, 1.3, 2.3, 1.75, 100)
    mirror = ellipse(0, 1.35, 1.95, 1.45, 90)
    glare = [seg((-1.1, 1.9), (-0.4, 2.45)), seg((-1.05, 1.35), (0.05, 2.3))]
    filig = keep([scallop(ellipse(0, 1.3, 2.13, 1.6, 80), 0.08)], lid)
    rim = ellipse(0, -1.3, 2.3, 0.85, 90)
    band = chain([(-2.3, -1.3), (-2.3, -1.65)], [(2.3 * math.cos(t), -1.65 + 0.85 * math.sin(t)) for t in [math.pi + math.pi * i / 40 for i in range(41)]], [(2.3, -1.3)])
    base_cv = chain(band, arc(0, -1.3, 2.3, 0, math.pi, 1)[1:])
    base_cv = chain(band, [(2.3 * math.cos(t), -1.3 + 0.85 * math.sin(t)) for t in [math.pi * i / 30 for i in range(31)]])
    pan = ellipse(0, -1.3, 1.95, 0.65, 80)
    puff = ellipse(0.1, -1.3, 1.25, 0.42, 60)
    bow = [lens((0.1, -1.2), (-0.45, -0.95), 0.4), lens((0.1, -1.2), (0.65, -0.95), 0.4), circle(0.1, -1.2, 0.1, 10)]
    hinge = rect(-0.3, -0.55, 0.3, -0.38)
    clasp = rrect(-0.3, -2.62, 0.3, -2.3, 0.08)
    return make("Powder Compact with Mirror", scene(
        ([lid, mirror, filig] + glare, [lid]),
        ([hinge], [hinge]),
        ([rim, band, pan, puff], [base_cv]),
        (bow, bow),
        ([clasp], [clasp])))


@design("vintage_perfume_atomizer", T)
def perfume_atomizer(rng):
    cx = -0.8
    sh = cubic((cx - 0.32, 0.55), (cx - 1.6, 0.4), (cx - 1.75, -1.4), (cx - 1.15, -2.3), 30)
    body = chain(sh, [(cx + 1.15, -2.3)], mirror_x(sh, cx)[::-1])
    body_cv = body + [body[0]]
    facets = keep([seg((cx - 2 + k * 0.55, -2.6), (cx - 2 + k * 0.55 + 2.0, 0.9)) for k in range(-3, 8)] +
                  [seg((cx + 2 - k * 0.55, -2.6), (cx + 2 - k * 0.55 - 2.0, 0.9)) for k in range(-3, 8)], body_cv)
    base = rrect(cx - 1.3, -2.55, cx + 1.3, -2.3, 0.08)
    neck = rect(cx - 0.3, 0.45, cx + 0.3, 0.85)
    collar = rrect(cx - 0.45, 0.85, cx + 0.45, 1.3, 0.08)
    pipe = rect(cx - 0.1, 1.3, cx + 0.1, 1.85)
    head = circle(cx, 2.0, 0.22, 18)
    nozzle = tube([(cx - 0.15, 2.0), (cx - 0.75, 2.05)], 0.12)
    spray = [seg((cx - 1.0, 2.1), (cx - 1.6, 2.4)), seg((cx - 1.0, 2.0), (cx - 1.7, 2.0)), seg((cx - 1.0, 1.9), (cx - 1.6, 1.6))]
    hose = tube(cubic((cx + 0.4, 1.05), (1.3, 1.4), (1.9, 0.9), (1.85, 0.25), 30), 0.17)
    bulb = ellipse(1.9, -0.55, 0.62, 0.85, 50)
    cup = poly((1.65, 0.35), (2.15, 0.35), (2.05, 0.1), (1.75, 0.1))
    net = keep([seg((1.0 + k * 0.35, -1.6), (2.0 + k * 0.35, 0.4)) for k in range(-2, 4)] +
               [seg((2.8 - k * 0.35, -1.6), (1.8 - k * 0.35, 0.4)) for k in range(-2, 4)], bulb)
    knot = circle(1.95, -1.48, 0.12, 12)
    tassel = poly((1.85, -1.6), (2.05, -1.6), (2.3, -2.6), (1.6, -2.6))
    fringe = [seg((x, -2.0), (x, -2.6)) for x in (1.8, 2.1)]
    return make("Perfume Atomizer", scene(
        ([body] + facets, [body_cv]),
        ([base], [base]),
        ([neck], [neck]),
        ([hose], [hose]),
        ([collar], [collar]),
        ([pipe], [pipe]),
        ([nozzle] + spray, [nozzle]),
        ([head], [head]),
        (fringe + [tassel], [tassel]),
        ([knot], [knot]),
        ([bulb] + net, [bulb]),
        ([cup], [cup])))


@design("vintage_penny_farthing", T)
def penny_farthing(rng):
    fx, fy, R = 0.65, -0.75, 2.05
    big = [circle(fx, fy, R, 120), circle(fx, fy, R - 0.18, 110), circle(fx, fy, 0.16, 14)] + spokes(fx, fy, 0.16, R - 0.18, 14, 0.1)
    rx, ry, r = -2.4, -2.35, 0.45
    small = [circle(rx, ry, r, 40), circle(rx, ry, r - 0.12, 30), circle(rx, ry, 0.07, 8)] + spokes(rx, ry, 0.07, r - 0.12, 6)
    fork = tube([(fx, fy), (0.45, 1.45)], 0.16)
    spine = tube(cubic((0.4, 1.4), (-0.9, 1.45), (-2.2, 0.4), (rx, ry), 40), lambda t: 0.22 - 0.1 * t)
    saddle = poly((-0.55, 1.55), (0.25, 1.75), (0.2, 1.55), (-0.3, 1.45))
    spring = [seg((-0.4, 1.5), (-0.4, 1.35)), seg((0.0, 1.6), (0.0, 1.42))]
    bars = tube([(0.45, 1.45), (0.5, 1.75), (1.1, 1.8), (1.35, 1.55)], 0.1)
    grip = tube([(1.35, 1.55), (1.45, 1.25)], 0.18)
    crank = [seg((fx, fy), (fx + 0.35, fy - 0.5)), rect(fx + 0.15, fy - 0.62, fx + 0.6, fy - 0.45)]
    step = seg((-1.5, 0.55), (-1.75, 0.6))
    ground = seg((-3.1, -2.85), (3.0, -2.85))
    return make("Penny-Farthing Bicycle", scene(
        (small, [small[0]]),
        (big, []),
        ([spine, step], [spine]),
        ([fork], [fork]),
        (crank, [crank[1]]),
        (spring, []),
        ([bars, grip], [grip]),
        ([saddle], [saddle]),
        ([], [])) + [ground])


@design("vintage_sewing_notions", T)
def sewing_notions(rng):
    sx = -1.2
    ftop = [ellipse(sx, 1.55, 1.2, 0.32, 50)]
    fside_t = chain([(sx - 1.2, 1.55), (sx - 1.2, 1.3)], [(sx + 1.2 * math.cos(t), 1.3 + 0.32 * math.sin(t)) for t in [math.pi + math.pi * i / 30 for i in range(31)]], [(sx + 1.2, 1.55)])
    fbot = chain([(sx - 1.2, -1.45), (sx - 1.2, -1.75)], [(sx + 1.2 * math.cos(t), -1.75 + 0.32 * math.sin(t)) for t in [math.pi + math.pi * i / 30 for i in range(31)]], [(sx + 1.2, -1.45)],
                 [(sx + 1.2 * math.cos(t), -1.45 + 0.32 * math.sin(t)) for t in [math.pi * i / 30 for i in range(31)]])
    thread = chain([(sx - 0.95, 1.3), (sx - 0.95, -1.45)]), chain([(sx + 0.95, 1.3), (sx + 0.95, -1.45)])
    wraps = [quad((sx - 0.95, y), (sx, y - 0.28), (sx + 0.95, y), 16) for y in (0.95, 0.55, 0.15, -0.25, -0.65, -1.05)]
    hole = ellipse(sx, 1.55, 0.25, 0.08, 14)
    loose = cubic((sx + 0.95, 0.15), (0.6, 0.3), (-0.2, 2.3), (0.5, 2.37), 30)
    loose2 = cubic((0.5, 2.37), (0.9, 2.42), (0.6, 2.9), (1.2, 3.05), 20)
    needle = chain([(0.15, 2.42), (2.9, 2.62), (0.15, 2.22)], arc(0.15, 2.32, 0.1, -math.pi / 2, -1.5 * math.pi, 8))
    needle_cv = needle + [needle[0]]
    n_eye = ellipse(0.42, 2.335, 0.17, 0.045, 12, rot=0.07)
    tx, ty = 1.85, 0.25
    th_side = chain([(tx - 0.62, ty)], cubic((tx - 0.62, ty), (tx - 0.55, ty + 1.0), (tx - 0.5, ty + 1.2), (tx, ty + 1.3), 16),
                    cubic((tx, ty + 1.3), (tx + 0.5, ty + 1.2), (tx + 0.55, ty + 1.0), (tx + 0.62, ty), 16))
    th_rim = ellipse(tx, ty, 0.62, 0.17, 30)
    th_band = quad((tx - 0.6, ty + 0.3), (tx, ty + 0.12), (tx + 0.6, ty + 0.3), 12)
    th_cv = th_side + [(tx, ty - 0.17)]
    dimples = keep([circle(tx + dx, ty + dy, 0.09, 10) for dy in (0.6, 0.9) for dx in (-0.3, 0.0, 0.3)] + [circle(tx, ty + 1.12, 0.09, 10)], th_cv)

    def scissors():
        b1 = chain(quad((0, 0.06), (1.3, 0.38), (2.5, 0.18), 16), quad((2.5, 0.18), (1.3, 0.05), (0, -0.14), 16))
        b2 = [(x, -y) for x, y in b1]
        h1 = [ellipse(-1.15, 0.5, 0.5, 0.33, 30, rot=0.2), ellipse(-1.15, 0.5, 0.3, 0.17, 24, rot=0.2)]
        h2 = [ellipse(-1.15, -0.5, 0.5, 0.33, 30, rot=-0.2), ellipse(-1.15, -0.5, 0.3, 0.17, 24, rot=-0.2)]
        s1 = tube([(0, 0.0), (-0.7, 0.38)], 0.2, cap=False)
        s2 = tube([(0, 0.0), (-0.7, -0.38)], 0.2, cap=False)
        piv = circle(0, 0, 0.1, 10)
        return b1, b2, h1, h2, s1, s2, piv
    b1, b2, h1, h2, s1, s2, piv = scissors()
    tf = lambda p: transform(p, 0.85, -2.05, 1.0, 0.18)
    b1, b2, s1, s2, piv = tf(b1), tf(b2), tf(s1), tf(s2), tf(piv)
    h1, h2 = [tf(p) for p in h1], [tf(p) for p in h2]
    return make("Thimble, Spool and Scissors", scene(
        ([needle, n_eye], [needle_cv]),
        ([loose, loose2], []),
        ([th_side, th_rim, th_band] + dimples, [th_cv]),
        (ftop + [fside_t, hole] + list(thread) + wraps, [rect(sx - 1.2, -1.5, sx + 1.2, 1.55)] + ftop),
        ([fbot], [fbot]),
        ([s2] + h2, [s2] + h2[:1]),
        ([b2], [b2]),
        ([s1] + h1, [s1] + h1[:1]),
        ([b1], [b1]),
        ([piv], [piv])))


@design("vintage_apothecary_bottles", T)
def apothecary_bottles(rng):
    shelf = rect(-3.0, -2.75, 3.0, -2.45)
    # tall stoppered bottle
    a_sh = chain([(-2.65, -2.45), (-2.65, 0.4)], quad((-2.65, 0.85), (-2.2, 0.9), (-2.2, 1.35), 10))
    a = chain(a_sh, [(-2.2, 1.65), (-1.7, 1.65), (-1.7, 1.35)], quad((-1.7, 1.35), (-1.7, 0.9), (-1.25, 0.85), 10), [(-1.25, 0.4), (-1.25, -2.45)])
    a_cv = a + [a[0]]
    a_lip = rrect(-2.3, 1.6, -1.6, 1.8, 0.06)
    a_stop = chain([(-2.08, 1.8), (-2.08, 2.07)], arc(-1.95, 2.35, 0.31, -2.0, -1.14 - TAU, 30), [(-1.82, 1.8)])
    a_lab = rrect(-2.5, -1.4, -1.4, -0.1, 0.1)
    a_lab2 = rect(-2.38, -1.27, -1.52, -0.23)
    a_liq = wave(-2.65, -1.25, 0.15, 0.05, 2, 20)
    # wide jar with domed lid
    j = rrect(-0.95, -2.45, 1.0, 0.55, 0.35)
    j_neck = rect(-0.75, 0.55, 0.8, 0.8)
    j_lid = chain([(-0.95, 0.8)], cubic((-0.95, 1.5), (1.0, 1.5), (1.0, 0.8), (1.0, 0.8), 20), [(-0.95, 0.8)])
    j_knob = circle(0.025, 1.5, 0.2, 18)
    j_lab = ellipse(0.025, -0.9, 0.7, 0.55, 40)
    j_lab2 = ellipse(0.025, -0.9, 0.55, 0.42, 36)
    herbs = keep([lens((-0.6, -2.3), (-0.2, -1.6), 0.3), lens((0.2, -2.3), (0.6, -1.5), 0.3), lens((0.7, -2.3), (0.85, -1.8), 0.3)], j)
    # round flask with cork
    fcx = 2.1
    f_body = chain([(fcx - 0.22, 0.6)],
                   [(fcx + 0.88 * math.cos(t), -1.55 + 0.88 * math.sin(t)) for t in [math.radians(104) + math.radians(332) * i / 60 for i in range(61)]], [(fcx + 0.22, 0.6)])
    f_cv = f_body + [f_body[0]]
    f_base = seg((fcx - 0.55, -2.45), (fcx + 0.55, -2.45))
    cork = poly((fcx - 0.28, 0.6), (fcx + 0.28, 0.6), (fcx + 0.22, 1.05), (fcx - 0.22, 1.05))
    f_lab = poly((fcx - 0.5, -1.0), (fcx + 0.5, -1.0), (fcx + 0.5, -1.6), (fcx, -1.9), (fcx - 0.5, -1.6))
    f_liq = keep([wave(fcx - 0.9, fcx + 0.9, -0.95, 0.05, 2, 20)], f_cv)
    return make("Apothecary Bottles and Jar", scene(
        ([shelf], [shelf]),
        ([a, a_lab, a_lab2, a_liq], [a_cv]),
        ([a_lip], [a_lip]),
        ([a_stop], [a_stop + [a_stop[0]]]),
        ([j, j_neck, j_lab, j_lab2] + herbs, [j, j_neck]),
        ([j_lid], [j_lid]),
        ([j_knob], [j_knob]),
        ([f_body, f_lab, f_base] + f_liq, [f_cv]),
        ([cork], [cork])))


@design("vintage_balance_scale", T)
def balance_scale(rng):
    plinth = rrect(-1.5, -2.85, 1.5, -2.5, 0.08)
    step = rect(-1.0, -2.5, 1.0, -2.25)
    col = tube([(0, -2.25), (0, 1.55)], lambda t: 0.3 + 0.35 * math.exp(-((t - 0.1) / 0.08) ** 2) + 0.2 * math.exp(-((t - 0.6) / 0.05) ** 2))
    tilt = 0.13
    L = 2.3
    lx, ly = -L * math.cos(tilt), 1.6 - L * math.sin(tilt)
    rx_, ry_ = L * math.cos(tilt), 1.6 + L * math.sin(tilt)
    beam = tube([(lx, ly), (0, 1.6), (rx_, ry_)], 0.17)
    pivot = circle(0, 1.6, 0.2, 18)
    pointer = [(x * math.cos(tilt) - (y - 1.6) * math.sin(tilt), 1.6 + x * math.sin(tilt) + (y - 1.6) * math.cos(tilt)) for x, y in lens((0, 1.75), (0, 2.75), 0.12)]
    dial = arc(0, 1.6, 1.25, math.radians(70), math.radians(110), 12)

    def pan(x, top):
        y = top - 2.45
        bowl = cubic((x - 1.0, y), (x - 0.9, y - 0.65), (x + 0.9, y - 0.65), (x + 1.0, y), 24)
        rim = ellipse(x, y, 1.0, 0.2, 40)
        strings = [seg((x, top), (x - 0.9, y + 0.05)), seg((x, top), (x + 0.9, y + 0.05)), seg((x, top), (x, y + 0.2))]
        hook = circle(x, top, 0.1, 10)
        return bowl, rim, strings, hook, y
    lb, lr, ls, lh, lyb = pan(lx, ly)
    rb, rr, rs, rh, ryb = pan(rx_, ry_)
    w1 = rect(lx - 0.6, lyb, lx + 0.1, lyb + 0.45)
    w2 = rect(lx - 0.45, lyb + 0.45, lx - 0.05, lyb + 0.8)
    w4 = rect(lx + 0.2, lyb, lx + 0.6, lyb + 0.3)
    fr = [circle(rx_ + dx, ryb + dy, 0.27, 20) for dx, dy in ((-0.45, 0.22), (0.1, 0.22), (0.62, 0.22), (-0.18, 0.66), (0.38, 0.66))]
    return make("Brass Balance Scale", scene(
        ([plinth], [plinth]),
        ([step], [step]),
        ([col], [col]),
        ([dial] + ls + rs, []),
        ([lb, w1, w2, w4], [w1, w2, w4, lb + [lb[0]]]),
        ([lr], []),
        (fr, fr),
        ([rb, rr], [rb + [rb[0]]]),
        ([pointer], [pointer]),
        ([beam], [beam]),
        ([pivot, lh, rh], [pivot])))


@design("vintage_desk_globe", T)
def desk_globe(rng):
    cx, cy, R, rot = 0.0, 0.55, 2.0, -0.4

    def P(pts):
        return transform(pts, cx, cy, 1.0, rot)
    sphere = circle(cx, cy, R, 120)
    mer = [seg((0, -R), (0, R))]
    for lam in (35, 70):
        s = math.sin(math.radians(lam))
        half = [(R * s * math.cos(t), R * math.sin(t)) for t in [-math.pi / 2 + math.pi * i / 40 for i in range(41)]]
        mer += [half, mirror_x(half)]
    lat = []
    for ph in (-60, -30, 0, 30, 60):
        c = math.cos(math.radians(ph))
        y0 = R * math.sin(math.radians(ph))
        lat.append([(R * c * math.cos(t), y0 + 0.18 * R * c * math.sin(t)) for t in [math.pi + math.pi * i / 40 for i in range(41)]])
    land = smooth([(-1.3, 1.25), (-0.5, 1.6), (0.15, 1.2), (-0.15, 0.75), (-0.45, 0.45), (-0.25, 0.15), (0.1, -0.05), (0.55, -0.35),
                   (0.4, -0.95), (0.0, -1.55), (-0.15, -1.05), (-0.35, -0.45), (-0.65, 0.15), (-1.1, 0.55), (-1.55, 0.95)], 3)
    land2 = smooth([(0.9, 1.4), (1.5, 1.3), (1.75, 0.8), (1.35, 0.3), (1.2, -0.3), (0.95, 0.2), (0.75, 0.75)], 3)
    grid = hide([P(g) for g in mer + lat], P(land), P(land2))
    ring_a = math.pi / 2 + rot
    ring = [arc(cx, cy, 2.18, ring_a, ring_a + math.pi, 70), arc(cx, cy, 2.42, ring_a, ring_a + math.pi, 70)]
    caps = [seg((cx + 2.18 * math.cos(a), cy + 2.18 * math.sin(a)), (cx + 2.42 * math.cos(a), cy + 2.42 * math.sin(a))) for a in (ring_a, ring_a + math.pi)]
    pins = [circle(cx + 2.3 * math.cos(ring_a), cy + 2.3 * math.sin(ring_a), 0.12, 12)]
    stem = tube([(0, cy - 2.42), (0, -2.45)], lambda t: 0.25 + 0.25 * math.exp(-((t - 0.5) / 0.15) ** 2))
    fs = cubic((-1.5, -2.95), (-1.4, -2.5), (-0.6, -2.55), (-0.2, -2.4), 20)
    foot = chain(fs, mirror_x(fs)[::-1], [fs[0]])
    return make("Antique Desk Globe", scene(
        ([sphere, P(land), P(land2)] + grid, [sphere]),
        (ring + caps, []),
        (pins, pins),
        ([stem], [stem]),
        ([foot], [foot])))


@design("vintage_rocking_chair", T)
def rocking_chair(rng):
    rocker = tube(quad((-2.7, -2.05), (0, -3.15), (2.7, -2.05), 40), 0.22)
    fleg = tube([(1.35, -2.55), (1.25, 0.75)], 0.2)
    bleg = tube([(-0.95, -2.6), (-1.0, -0.4), (-1.95, 3.0)], 0.22)
    far = tube([(-0.55, -0.3), (-1.35, 2.95)], 0.2)
    knobs = [circle(-1.97, 3.15, 0.16, 14), circle(-1.37, 3.1, 0.15, 14)]

    def on(a, b, t):
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    slats = []
    for t in (0.42, 0.66, 0.9):
        p = on((-1.0, -0.4), (-1.95, 3.0), t)
        q = on((-0.55, -0.3), (-1.35, 2.95), t)
        slats.append(tube(quad(p, ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 - 0.1), q, 8), 0.24))
    seat = poly((-1.2, -0.55), (1.55, -0.45), (1.55, -0.2), (-1.15, -0.3))
    cushion = smooth([(-1.05, -0.3), (1.5, -0.2), (1.55, 0.15), (-1.0, 0.1)], 2)
    arm = tube([(-1.55, 0.95), (1.4, 0.85), (1.75, 0.9)], 0.2)
    scroll = circle(1.75, 0.8, 0.18, 14)
    spind = [seg((x, 0.1), (x, 0.75)) for x in (-0.6, -0.05, 0.5)]
    stretch = [tube([(-0.95, -1.7), (1.3, -1.65)], 0.12)]
    return make("Rocking Chair", scene(
        ([far], [far]),
        (slats, slats),
        (stretch, stretch),
        ([bleg], [bleg]),
        (knobs, knobs),
        ([seat], [seat]),
        ([cushion], [cushion]),
        (spind, []),
        ([fleg], [fleg]),
        ([arm], [arm]),
        ([scroll], [scroll]),
        ([rocker], [rocker])))


@design("vintage_wingback_chair", T)
def wingback_chair(rng):
    bs = cubic((-1.3, -0.6), (-1.35, 1.4), (-1.4, 2.4), (0, 2.75), 30)
    back = chain(bs, mirror_x(bs)[::-1])
    back_cv = back + [back[0]]
    tuft = []
    for k in range(-5, 6):
        tuft += [seg((k * 0.7 - 3, -2.0), (k * 0.7 + 3, 4.0)), seg((k * 0.7 + 3, -2.0), (k * 0.7 - 3, 4.0))]
    tuft = keep(tuft, poly((-1.2, -0.2), (1.2, -0.2), (1.25, 2.3), (0, 2.6), (-1.25, 2.3)))
    buttons = [circle(x * 0.7, y * 0.7 + 1.0, 0.08, 8) for x in range(-2, 3) for y in range(-2, 3)
               if (x + y) % 2 == 0 and _inside((x * 0.7, y * 0.7 + 1.0), poly((-1.1, -0.1), (1.1, -0.1), (1.15, 2.25), (0, 2.5), (-1.15, 2.25)))]
    wing = chain([(-1.3, 2.35)], cubic((-1.3, 2.35), (-2.1, 2.7), (-2.6, 2.2), (-2.4, 1.4), 20), quad((-2.4, 1.4), (-2.3, 0.7), (-1.95, 0.4), 10), [(-1.3, 0.4)])
    wing_cv = wing + [wing[0]]
    wings = [wing, mirror_x(wing)]
    seat = rrect(-1.7, -1.3, 1.7, -0.55, 0.25)
    arm = chain([(-1.5, -1.45), (-1.5, 0.15)], arc(-2.05, 0.15, 0.55, 0, math.pi, 24), [(-2.6, -1.45)])
    arm_cv = arm + [arm[0]]
    arms = [arm, mirror_x(arm)]
    scrolls = [spiral(-2.05, 0.1, 0.06, 0.38, 1.25, 50, rot=0.5), mirror_x(spiral(-2.05, 0.1, 0.06, 0.38, 1.25, 50, rot=0.5))]
    base = rrect(-2.7, -2.0, 2.7, -1.4, 0.12)
    skirt = scallop([(-2.6, -2.0), (2.6, -2.0)], 0.22, out=-1)

    def cab(x, s):
        return chain([(x, -2.0)], cubic((x, -2.0), (x - 0.25 * s, -2.3), (x + 0.15 * s, -2.55), (x - 0.15 * s, -2.8), 12),
                     [(x + 0.15 * s, -2.8)], cubic((x + 0.15 * s, -2.8), (x + 0.3 * s, -2.4), (x + 0.05 * s, -2.3), (x + 0.25 * s, -2.0), 12))
    legs = [cab(-2.3, 1), cab(2.3, -1)]
    return make("Wingback Armchair", scene(
        (legs, []),
        ([back] + tuft + buttons, [back_cv]),
        (wings, [wing_cv, mirror_x(wing_cv)]),
        ([seat], [seat]),
        (arms + scrolls, [arm_cv, mirror_x(arm_cv)]),
        ([base, skirt], [base])))


@design("vintage_roll_top_desk", T)
def roll_top_desk(rng):
    def P(x, d, h):
        return (x + 0.55 * d, h + 0.32 * d)
    X0, X1, D = -2.4, 1.6, 1.6
    out = []
    out.append(chain([P(X0, 0, -0.2), P(X0, 0, -2.7), P(-0.9, 0, -2.7), P(-0.9, 0, -0.75), P(0.1, 0, -0.75), P(0.1, 0, -2.7),
                      P(X1, 0, -2.7), P(X1, 0, -0.2), P(X0, 0, -0.2)]))
    out.append(chain([P(X1, 0, -2.7), P(X1, D, -2.7), P(X1, D, -0.2)]))
    out.append(seg(P(-0.9, 0, -0.75), P(-0.9, 0, -0.2)))
    out.append(seg(P(0.1, 0, -0.75), P(0.1, 0, -0.2)))
    for x0, x1 in ((X0, -0.9), (0.1, X1)):
        for h in (-0.98, -1.82):
            out.append(seg(P(x0, 0, h), P(x1, 0, h)))
        for hc in (-0.6, -1.4, -2.26):
            out.append(circle((x0 + x1) / 2, hc, 0.09, 10))
    out.append(circle(-0.4, -0.48, 0.09, 10))
    out.append(seg(P(-0.9, 0, -2.7), P(-0.9, 0.5, -2.7)))
    # desk top strip and hutch with S-shaped roll
    out.append(seg(P(X0, 0, -0.2), P(X0, 0.35, -0.2)))
    prof = cubic((0.35, -0.2), (0.35, 0.95), (0.75, 1.55), (D, 1.55), 40)
    out.append([P(X0, d, h) for d, h in prof])
    out.append([P(X1, d, h) for d, h in prof])
    out.append(seg(P(X1, D, -0.2), P(X1, D, 1.55)))
    out.append(seg(P(X0, D, 1.55), P(X1, D, 1.55)))
    out.append(seg(P(X1, 0.35, -0.2), P(X1, D, -0.2)))
    dd = _dense(prof, 0.01)
    acc, nxt = 0.0, 0.42
    for a, b in zip(dd, dd[1:]):
        acc += math.dist(a, b)
        if acc >= nxt and nxt < _plen(prof) - 0.15:
            out.append(seg(P(X0, b[0], b[1]), P(X1, b[0], b[1])))
            nxt += 0.24
    hs = [rrect(-1.6, 0.0, -1.1, 0.13, 0.06), rrect(0.4, 0.0, 0.9, 0.13, 0.06)]
    lock = [circle(-0.33, 0.02, 0.07, 8)]
    ct = P(X0 - 0.12, D + 0.05, 1.55)
    cornice = chain([ct, P(X1 + 0.12, D + 0.05, 1.55)]), chain([P(X0 - 0.12, D + 0.05, 1.55), P(X0 - 0.12, D + 0.05, 1.8), P(X1 + 0.12, D + 0.05, 1.8), P(X1 + 0.12, D + 0.05, 1.55)])
    pan = [poly(P(X1, 0.3, -2.45), P(X1, 1.3, -2.45), P(X1, 1.3, -0.45), P(X1, 0.3, -0.45))]
    return make("Roll-Top Desk", out + hs + lock + [cornice[1]] + pan)


@design("vintage_fountain_pen_letter", T)
def fountain_pen_letter(rng):
    env = transform(rect(-1.6, -1.0, 1.6, 1.0), 1.3, 1.75, 1.0, -0.22)
    flap = transform(poly((-1.6, 1.0), (0, -0.1), (1.6, 1.0), closed=False), 1.3, 1.75, 1.0, -0.22)
    rot = 0.1
    paper = transform(rect(-2.2, -2.7, 1.5, 2.3), -0.6, 0.0, 1.0, rot)
    rows = []
    for k, L in enumerate([2.6, 2.9, 2.4, 2.9, 2.7, 1.6]):
        y = 1.7 - k * 0.55
        n = int(L / 0.32)
        pts = [(-2.0 + 0.05 * t - 0.09 * math.sin(t) + 0.0, y + 0.11 * math.cos(t) * -1) for t in [TAU * n * i / (n * 16) for i in range(n * 16 + 1)]]
        rows.append(transform(pts, -0.6 + 0.0, 0.0, 1.0, rot))
    sign = transform(spiral(0.3, -2.0, 0.05, 0.3, 1.5, 40), -0.6, 0, 1.0, rot)
    flourish = transform(cubic((-0.5, -2.25), (0.0, -2.45), (0.6, -1.9), (1.1, -2.3), 20), -0.6, 0, 1.0, rot)

    def pen():
        nib = chain([(0, 0)], quad((0, 0), (0.45, 0.18), (0.95, 0.24), 10), [(0.95, -0.24)], quad((0.95, -0.24), (0.45, -0.18), (0, 0), 10))
        slit = seg((0.12, 0), (0.6, 0))
        hole = circle(0.68, 0, 0.07, 8)
        section = poly((0.95, -0.22), (1.55, -0.28), (1.55, 0.28), (0.95, 0.22))
        barrel = rrect(1.55, -0.33, 4.6, 0.33, 0.25)
        ring = seg((2.0, -0.33), (2.0, 0.33))
        ring2 = seg((3.4, -0.33), (3.4, 0.33))
        clip = tube([(3.55, 0.45), (4.55, 0.45)], 0.14)
        return [nib, slit, hole, section, barrel, ring, ring2, clip], [nib, section, barrel, clip]
    ps, pc = pen()
    tf = lambda p: transform(p, 0.25, -1.25, 1.0, 0.62)
    ps = [tf(p) for p in ps]
    pc = [tf(p) for p in pc]
    return make("Fountain Pen and Handwritten Letter", scene(
        ([env, flap], [env]),
        ([paper] + rows + [sign, flourish], [paper]),
        (ps, pc)))


@design("vintage_postage_stamps", T)
def postage_stamps(rng):
    def stamp(cx, cy, rot, pic):
        edge = scallop(rect(-1.15, -1.4, 1.15, 1.4), 0.11, out=-1)
        frame = rect(-0.88, -1.1, 0.88, 1.1)
        corner = circle(0.6, -0.82, 0.18, 14)
        parts = [edge, frame] + hide(pic, corner) + [corner]
        cv = rect(-1.15, -1.4, 1.15, 1.4)
        return [transform(p, cx, cy, 1.0, rot) for p in parts], [transform(cv, cx, cy, 1.0, rot)]
    ship = [poly((-0.7, -0.4), (0.7, -0.4), (0.5, -0.7), (-0.5, -0.7)), seg((0, -0.4), (0, 0.85)),
            poly((0.05, 0.8), (0.05, -0.3), (0.65, -0.3)), poly((-0.05, 0.7), (-0.05, -0.3), (-0.6, -0.3)), wave(-0.85, 0.85, -0.85, 0.05, 3, 30)]
    flower = [circle(0, 0.45, 0.15, 14)] + [transform(lens((0, 0.0), (0, 0.42), 0.4), 0, 0.45, 1.0, k * TAU / 6 + 0.26) for k in range(6)] + \
             [seg((0, -0.03), (0, -1.0)), lens((0, -0.6), (-0.5, -0.3), 0.3), lens((0, -0.75), (0.45, -0.45), 0.3)]
    house = [poly((-0.3, -1.0), (0.3, -1.0), (0.2, 0.3), (-0.2, 0.3)), rect(-0.27, 0.3, 0.27, 0.6), poly((-0.32, 0.6), (0.32, 0.6), (0, 0.9)),
             seg((-0.27, -0.4), (0.27, -0.4)), seg((-0.24, -0.0), (0.24, -0.0)), seg((-0.75, 0.75), (-0.38, 0.5)), seg((0.75, 0.75), (0.38, 0.5))]
    face = smooth([(0.0, 0.85), (0.22, 0.65), (0.25, 0.45), (0.45, 0.25), (0.28, 0.18), (0.32, 0.05), (0.25, -0.05), (0.27, -0.2),
                   (0.12, -0.3), (0.1, -0.6), (0.5, -0.85), (0.6, -1.1)], 2, closed=False)
    hair = smooth([(0.0, 0.85), (-0.4, 0.9), (-0.65, 0.5), (-0.55, 0.05), (-0.3, -0.3), (-0.45, -0.75), (-0.75, -1.1)], 2, closed=False)
    crown = [poly((-0.4, 0.8), (-0.35, 1.0), (-0.2, 0.88), (-0.05, 1.05), (0.1, 0.92), (0.12, 0.78), closed=False)]
    portrait = [face, hair] + crown
    s1, c1 = stamp(-1.3, 1.5, 0.06, ship)
    s2, c2 = stamp(1.3, 1.6, -0.08, flower)
    s3, c3 = stamp(-1.25, -1.5, -0.05, house)
    s4, c4 = stamp(1.35, -1.45, 0.1, portrait)
    return make("Postage Stamp Collection", scene((s1, c1), (s2, c2), (s3, c3), (s4, c4)))


@design("vintage_cash_register", T)
def cash_register(rng):
    drawer = rrect(-2.4, -2.6, 2.4, -1.6, 0.1)
    dknob = circle(0, -2.1, 0.15, 14)
    dpanel = [rrect(-2.1, -2.4, -0.4, -1.8, 0.08), rrect(0.4, -2.4, 2.1, -1.8, 0.08)]
    feet = ball_feet([-2.1, 2.1], -2.6, 0.2)
    kb = poly((-2.25, -1.6), (2.25, -1.6), (1.9, 0.6), (-1.9, 0.6))
    keys = [circle(-1.4 + c * 0.56 + r * 0.04, -1.25 + r * 0.5, 0.17, 16) for r in range(4) for c in range(6)]
    keys = [k for k in keys if all(_inside(p, kb) for p in k[::6])]
    cab = rect(-1.75, 0.6, 1.75, 1.85)
    med = [ellipse(0, 1.22, 0.55, 0.4, 30), ellipse(0, 1.22, 0.38, 0.25, 24)]
    scrolls = [spiral(-1.15, 1.22, 0.05, 0.35, 1.5, 40), mirror_x(spiral(-1.15, 1.22, 0.05, 0.35, 1.5, 40))]
    win = rrect(-1.25, 1.85, 1.25, 2.6, 0.1)
    tabs = [rect(x - 0.25, 2.0, x + 0.25, 2.45) for x in (-0.65, 0.0, 0.65)]
    ped = chain(cubic((-1.45, 2.6), (-0.8, 3.3), (0.8, 3.3), (1.45, 2.6), 30))
    ped_cv = ped + [ped[0]]
    fin = circle(0, 3.42, 0.17, 14)
    crank = [circle(2.35, -0.6, 0.15, 14), tube([(2.35, -0.6), (2.75, -1.3)], 0.16), ellipse(2.95, -1.3, 0.3, 0.12, 16)]
    return make("Antique Cash Register", scene(
        ([kb] + keys, [kb]),
        ([cab] + med + scrolls, [cab]),
        ([win] + tabs, [win]),
        ([ped], [ped_cv]),
        ([fin], [fin]),
        (crank, crank),
        ([drawer, dknob] + dpanel, [drawer]),
        (feet, [])))


@design("vintage_washboard_tub", T)
def washboard_tub(rng):
    rim = ellipse(0, -0.6, 2.4, 0.55, 90)
    rim_in = ellipse(0, -0.6, 2.2, 0.45, 80)
    sides = chain([(-2.4, -0.6), (-2.0, -2.75)], [(2.0 * math.cos(t), -2.75 + 0.4 * math.sin(t)) for t in [math.pi + math.pi * i / 40 for i in range(41)]], [(2.4, -0.6)])
    staves = []
    for k in range(-3, 4):
        a = k * 0.4
        xt, xb = 2.4 * math.sin(a), 2.0 * math.sin(a)
        staves.append(seg((xt, -0.6 - 0.55 * math.cos(a)), (xb, -2.75 - 0.4 * math.cos(a))))
    hoops = []
    for y0, rx in ((-1.25, 2.28), (-1.45, 2.24), (-2.25, 2.1), (-2.45, 2.06)):
        hoops.append([(rx * math.cos(t), y0 + 0.5 * math.sin(t)) for t in [math.pi + math.pi * i / 40 for i in range(41)]])
    ears = [poly((-2.42, -0.6), (-2.42, 0.1), (-2.0, 0.1), (-2.0, -0.6), closed=False), poly((2.42, -0.6), (2.42, 0.1), (2.0, 0.1), (2.0, -0.6), closed=False)]
    ear_holes = [ellipse(-2.21, -0.15, 0.1, 0.13, 10), ellipse(2.21, -0.15, 0.1, 0.13, 10)]

    def W(p):
        return transform(p, 0.15, 0.2, 1.0, 0.14)
    posts = [W(rect(-1.3, -1.6, -1.0, 3.0)), W(rect(1.0, -1.6, 1.3, 3.0))]
    header = W(rrect(-1.45, 2.0, 1.45, 3.0, 0.15))
    head_in = W(rrect(-1.1, 2.25, 1.1, 2.75, 0.1))
    ribs = [W(quad((-1.0, y), (0, y + 0.1), (1.0, y), 12)) for y in [-0.3 + 0.28 * k for k in range(8)]]
    bar = W(rect(-1.0, -0.6, 1.0, -0.4))
    bubbles = [circle(x, y, r, 18) for x, y, r in ((-1.6, -0.35, 0.3), (-1.0, -0.2, 0.2), (1.65, -0.3, 0.26), (2.0, 0.15, 0.15), (-1.95, 0.25, 0.14))]
    front_cover = sides + [(2.4 * math.cos(t), -0.6 + 0.55 * math.sin(t)) for t in [-math.pi * i / 40 for i in range(41)]][::-1]
    return make("Washboard and Wash Tub", scene(
        ([rim_in], []),
        (posts + [header, head_in, bar] + ribs, posts + [header]),
        ([rim, sides] + staves + hoops, [front_cover]),
        (ears + ear_holes, [poly((-2.42, -0.6), (-2.42, 0.1), (-2.0, 0.1), (-2.0, -0.6))]),
        (bubbles, bubbles)))


@design("vintage_sad_iron", T)
def sad_iron(rng):
    body = chain([(-2.55, -0.75), (2.0, -0.75), (2.05, -0.35)], quad((2.05, -0.35), (2.0, 0.5), (1.4, 0.55), 10), [(-0.6, 0.55)],
                 quad((-0.6, 0.55), (-1.6, 0.45), (-2.55, -0.55), 14), [(-2.55, -0.75)])
    part = seg((-2.4, -0.5), (2.03, -0.5))
    arch = tube(chain(quad((-1.1, 0.3), (-1.15, 1.75), (-0.55, 1.75), 12), [(0.95, 1.75)], quad((0.95, 1.75), (1.55, 1.75), (1.5, 0.5), 12)), 0.18)
    grip = rrect(-0.75, 1.48, 1.05, 2.02, 0.27)
    grain = [quad((-0.5, 1.76), (0.15, 1.86), (0.8, 1.74), 10)]
    tri = ellipse(0, -1.05, 2.75, 0.55, 90)
    tri_in = ellipse(0, -1.05, 2.35, 0.4, 80)
    hearts = [heart(x, -1.1, 0.16) for x in (-1.6, 1.6)]
    tri_sp = [seg((-2.3 * math.cos(a), -1.05 - 0.4 * math.sin(a)), (-2.75 * math.cos(a), -1.05 - 0.55 * math.sin(a))) for a in (0.5, 1.2, 1.9, 2.6)]
    legs = [tube([(x, -1.4), (x * 1.05, -2.2)], 0.2) for x in (-2.0, 2.0)] + [tube([(0.3, -1.55), (0.3, -2.4)], 0.2)]
    heat = [[(x + 0.12 * math.sin(i * 0.6), 0.9 + i * 0.12) for i in range(14)] for x in (-2.3, -1.9)]
    return make("Cast Iron Sad Iron on a Trivet", scene(
        (legs, legs),
        ([tri, tri_in] + hearts + tri_sp, [tri]),
        ([body, part], [body]),
        ([arch], [arch]),
        ([grip] + grain, [grip]),
        (heat, [])))


@design("vintage_dress_form", T)
def dress_form(rng):
    half = smooth([(0.0, 2.3), (0.38, 2.3), (0.45, 2.1), (1.3, 1.85), (1.55, 1.5), (1.32, 1.15), (1.42, 0.7), (1.15, 0.15), (0.85, -0.45),
                   (1.15, -1.0), (1.3, -1.55)], 3, closed=False)
    left = mirror_x(half)
    torso = chain(left[::-1], half)
    bottom = [(1.3 * math.cos(t), -1.55 + 0.28 * math.sin(t)) for t in [-math.pi * i / 40 for i in range(41)]]
    torso_cv = chain(torso, bottom)
    neck = ellipse(0, 2.3, 0.38, 0.1, 24)
    knob = [seg((0, 2.4), (0, 2.6)), circle(0, 2.75, 0.17, 16)]
    seams = [cubic((0.75, 2.05), (0.5, 1.2), (0.75, 0.5), (0.45, -0.45), 20), cubic((0.45, -0.45), (0.65, -0.9), (0.7, -1.3), (0.65, -1.8), 12)]
    seams += [mirror_x(x) for x in seams]
    waist = quad((-0.85, -0.45), (0, -0.62), (0.85, -0.45), 16)
    pole = tube([(0, -1.82), (0, -2.75)], 0.16)
    collar = rect(-0.25, -2.0, 0.25, -1.82)
    hub = rect(-0.3, -2.85, 0.3, -2.65)
    legs = [tube(quad((-0.2, -2.8), (-1.0, -2.85), (-1.8, -3.2), 10), 0.15), tube(quad((0.2, -2.8), (1.0, -2.85), (1.8, -3.2), 10), 0.15),
            tube([(0, -2.85), (0.15, -3.35)], 0.15)]
    wheels = [circle(-1.85, -3.35, 0.13, 12), circle(1.85, -3.35, 0.13, 12), circle(0.17, -3.5, 0.13, 12)]
    tl = cubic((-0.42, 2.25), (-0.9, 1.8), (-0.65, 0.5), (-1.0, -0.6), 40)
    tr = cubic((0.42, 2.25), (0.6, 1.5), (0.4, 0.0), (0.6, -1.2), 40)
    tapes = [tube(tl, 0.24), tube(tr, 0.24)]
    tick = []
    for c in (tl, tr):
        for i in range(3, len(c) - 1, 4):
            a, b = c[i], c[i + 1]
            tx, ty = b[0] - a[0], b[1] - a[1]
            L = math.hypot(tx, ty)
            tick.append([(a[0] - ty / L * 0.12, a[1] + tx / L * 0.12), (a[0] - ty / L * 0.02, a[1] + tx / L * 0.02)])
    pins = [circle(1.0, 0.6, 0.09, 8), seg((1.0, 0.6), (0.7, 0.85)), circle(-1.05, 1.3, 0.09, 8), seg((-1.05, 1.3), (-0.75, 1.45))]
    return make("Dressmaker's Dress Form", scene(
        (legs + wheels, legs),
        ([pole], [pole]),
        ([hub, collar], [hub, collar]),
        ([torso, bottom, neck, waist] + seams + pins, [torso_cv]),
        (knob, [knob[1]]),
        (tapes + tick, tapes)))


@design("vintage_button_boots", T)
def button_boots(rng):
    def boot():
        out = smooth([(-1.0, 2.6), (-0.92, 0.6), (-0.95, -0.4), (-1.12, -1.2), (-1.0, -1.75), (-0.75, -2.0)], 2, closed=False)
        heel = [(-0.75, -2.0), (-0.68, -2.62), (-0.42, -2.62), (-0.38, -2.05)]
        arch = quad((-0.38, -2.05), (0.2, -1.95), (0.85, -2.35), 12)
        sole = chain([(0.85, -2.35), (2.15, -2.4)], quad((2.15, -2.4), (2.45, -2.3), (2.3, -2.05), 8))
        top = smooth([(2.3, -2.05), (1.6, -1.75), (0.6, -1.2), (0.3, -0.4), (0.3, 1.0), (0.4, 2.6)], 2, closed=False)
        o = chain(out, heel, arch, sole, top, [(-1.0, 2.6)])
        return o
    o = boot()
    flap = smooth([(0.1, 2.6), (-0.1, 1.2), (0.0, -0.3), (0.35, -1.05), (1.05, -1.55)], 2, closed=False)
    btns = []
    for t in range(1, 9):
        i = int(t * (len(flap) - 1) / 9)
        x, y = flap[i]
        btns.append(circle(x - 0.15, y - 0.03, 0.1, 10))
    welt = quad((-0.35, -2.0), (0.6, -2.0), (2.2, -2.25), 12)
    toe = quad((1.45, -1.85), (1.6, -2.15), (1.75, -2.35), 8)
    cuff = seg((-0.98, 2.25), (0.38, 2.25))
    tab = poly((-0.55, 2.6), (-0.5, 3.0), (-0.25, 3.0), (-0.2, 2.6), closed=False)
    one = [o, flap, welt, toe, cuff, tab] + btns
    back = [transform(p, -0.9, 0.45, 0.92) for p in one]
    back_cv = transform(o, -0.9, 0.45, 0.92)
    return make("Victorian Button Boots", scene((back, [back_cv]), (one, [o])))


@design("vintage_padlock", T)
def padlock(rng):
    shackle = tube(chain([(-0.95, 0.8), (-0.95, 1.6)], arc(0, 1.6, 0.95, math.pi, 0, 30), [(0.95, 0.8)]), 0.42)
    body = smooth([(-1.75, 0.95), (1.75, 0.95), (1.9, -0.3), (1.35, -1.65), (0, -2.4), (-1.35, -1.65), (-1.9, -0.3)], 2)
    inner = smooth([(-1.45, 0.7), (1.45, 0.7), (1.58, -0.3), (1.12, -1.45), (0, -2.05), (-1.12, -1.45), (-1.58, -0.3)], 2)
    plate = lens((0, 0.3), (0, -1.35), 0.32)
    hole = [circle(0, -0.35, 0.16, 14), poly((-0.08, -0.45), (0.08, -0.45), (0.14, -0.85), (-0.14, -0.85))]
    scrolls = [spiral(-0.85, -0.3, 0.05, 0.38, 1.5, 40, rot=0.0), mirror_x(spiral(-0.85, -0.3, 0.05, 0.38, 1.5, 40, rot=0.0))]
    rivets = [circle(x, y, 0.11, 10) for x, y in ((-1.2, 0.45), (1.2, 0.45), (0, -1.75))]
    boards = [rect(-3.0, 1.3, 3.0, 2.45), rect(-3.0, 2.45, 3.0, 3.6)]
    grain = [wave(-2.8, -1.4, 1.85, 0.05, 1.5, 20), wave(1.4, 2.8, 2.0, 0.05, 1.5, 20), wave(-2.6, -1.0, 3.0, 0.05, 1.5, 20),
             wave(1.3, 2.7, 3.1, 0.05, 1.5, 20), circle(2.2, 1.7, 0.15, 12)]
    hasp = rrect(-2.7, 2.15, 0.55, 2.75, 0.12)
    hasp_r = [circle(x, 2.45, 0.1, 10) for x in (-2.35, -1.6)]
    plate2 = rrect(0.65, 1.6, 1.35, 3.3, 0.1)
    plate2_r = [circle(1.0, 1.85, 0.1, 10), circle(1.0, 3.05, 0.1, 10)]
    staple = ellipse(0, 2.45, 0.2, 0.42, 24)
    staple_front = keep([staple], rect(-1.0, 2.45, 1.0, 3.2))
    return make("Antique Iron Padlock on a Hasp", scene(
        (boards + grain, []),
        ([plate2] + plate2_r, [plate2]),
        ([hasp] + hasp_r, [hasp]),
        ([staple], [staple]),
        ([shackle], [shackle]),
        (staple_front, [poly((-0.22, 2.45), (0.22, 2.45), (0.22, 2.95), (-0.22, 2.95))]),
        ([body, inner] + scrolls + rivets, [body]),
        ([plate] + hole, [plate])))


@design("vintage_soda_crate", T)
def soda_crate(rng):
    def bottle(x, y0, h=3.6):
        w = 0.36
        sh = y0 + h * 0.55
        lh = chain([(x - w, y0), (x - w, sh)], cubic((x - w, sh), (x - w, sh + 0.45), (x - 0.13, sh + 0.55), (x - 0.13, sh + 0.9), 12),
                   [(x - 0.13, y0 + h - 0.15)])
        pts = chain(lh, mirror_x(lh, x)[::-1])
        cv = pts + [pts[0]]
        lip = rect(x - 0.17, y0 + h - 0.3, x + 0.17, y0 + h - 0.15)
        cap = zigzag(x - 0.2, x + 0.2, y0 + h + 0.0, 0.04, 4)
        capbox = poly((x - 0.2, y0 + h - 0.15), (x - 0.2, y0 + h - 0.02), (x + 0.2, y0 + h - 0.02), (x + 0.2, y0 + h - 0.15))
        lab = lens((x, sh - 0.3), (x, sh - 1.3), 0.3)
        bands = [seg((x - w, y0 + 0.35), (x + w, y0 + 0.35))]
        return [pts, lip, capbox, lab] + bands, [cv, lip, capbox]
    parts = []
    xs = [-2.15, -1.25, -0.35, 0.55]
    for k, x in enumerate(xs):
        parts.append(bottle(x, -2.2, 3.6 - 0.12 * (k % 2)))
    out_b = bottle(2.0, -2.75, 3.6)
    cap_off = [circle(2.75, -2.6, 0.2, 18)]
    crate_top = rect(-2.75, -1.3, 1.15, -0.65)
    crate_bot = rect(-2.75, -2.75, 1.15, -2.05)
    posts = [rect(-2.75, -2.75, -2.45, -0.65), rect(0.85, -2.75, 1.15, -0.65)]
    handle = rrect(-1.4, -1.12, -0.3, -0.85, 0.12)
    back_rim = seg((-2.45, -0.4), (0.85, -0.4))
    side = [poly((1.15, -0.65), (1.55, -0.35), (1.55, -2.45), (1.15, -2.75), closed=False), seg((-2.75, -0.65), (-2.35, -0.35)), seg((-2.35, -0.35), (1.55, -0.35))]
    grain = [wave(-2.3, 0.7, -2.45, 0.04, 2, 30), wave(-2.3, 0.7, -0.95, 0.04, 2, 30)]
    grain = hide(grain, handle)
    layers = [(side, [])]
    for p in parts:
        layers.append((p[0], p[1]))
    layers += [([crate_top, crate_bot] + grain, [crate_top, crate_bot]), (posts, posts), ([handle], [handle]), (out_b[0], out_b[1]), (cap_off, cap_off)]
    return make("Crate of Glass Soda Bottles", scene(*layers))


@design("vintage_tin_toy_car", T)
def tin_toy_car(rng):
    body = poly((-2.6, -0.8), (-2.6, 0.25), (-2.2, 0.6), (-1.75, 0.62), (-1.6, 1.7), (0.1, 1.7), (0.55, 0.62), (2.15, 0.45), (2.45, 0.2), (2.45, -0.8))
    win = rrect(-1.4, 0.8, -0.1, 1.5, 0.1)
    head = circle(-0.75, 1.08, 0.3, 24)
    cap = chain(arc(-0.75, 1.12, 0.32, 0.2, math.pi - 0.1, 14), [(-0.35, 1.15)])
    door = [seg((-1.5, 0.62), (-1.5, -0.6)), seg((0.25, 0.62), (0.25, -0.6)), rect(-0.4, 0.2, -0.1, 0.3)]
    stripe = [seg((-2.6, -0.2), (2.45, -0.2))]
    grille = [seg((2.45, y), (2.3, y)) for y in (-0.6, -0.4)]
    hood = [seg((1.0, 0.55), (1.15, -0.2)), seg((1.5, 0.5), (1.65, -0.2))]
    wf = poly((0.95, -0.8), (1.2, -0.15), (2.05, -0.15), (2.45, -0.8))
    wr = poly((-2.5, -0.8), (-2.35, -0.15), (-1.15, -0.15), (-0.9, -0.8))
    board = rect(-0.95, -0.95, 1.0, -0.78)
    wheels = []
    for x in (-1.7, 1.65):
        wheels += [circle(x, -1.05, 0.65, 50), circle(x, -1.05, 0.42, 36), circle(x, -1.05, 0.12, 12)] + spokes(x, -1.05, 0.12, 0.42, 6)
    lamp = [circle(2.35, 0.55, 0.2, 16), seg((2.35, 0.35), (2.35, 0.2))]
    key = [tube([(-2.6, 0.0), (-3.0, 0.0)], 0.14), ellipse(-3.25, 0.42, 0.25, 0.38, 20), ellipse(-3.25, -0.42, 0.25, 0.38, 20), circle(-3.1, 0.0, 0.12, 10)]
    tabs = [rect(x - 0.08, -0.85, x + 0.08, -0.7) for x in (-2.3, 2.1)]
    motion = [seg((-3.0, -1.2), (-3.4, -1.2)), seg((-2.8, -1.5), (-3.5, -1.5))]
    return make("Wind-Up Tin Toy Car", scene(
        (key, key[1:3]),
        ([body, win, head, cap] + door + stripe + grille + hood + tabs, [body]),
        (wheels, [w for w in wheels[::12]]),
        ([wf, wr, board], [wf, wr]),
        (lamp, [lamp[0]]),
        (motion, [])))


@design("vintage_jack_in_the_box", T)
def jack_in_the_box(rng):
    dx, dy = 0.85, 0.5
    front = rect(-1.75, -2.9, 0.95, -0.5)
    side = poly((0.95, -2.9), (0.95 + dx, -2.9 + dy), (0.95 + dx, -0.5 + dy), (0.95, -0.5), closed=False)
    top = poly((-1.75, -0.5), (-1.75 + dx, -0.5 + dy), (0.95 + dx, -0.5 + dy), closed=False)
    top_cv = poly((-1.75, -0.5), (-1.75 + dx, -0.5 + dy), (0.95 + dx, -0.5 + dy), (0.95, -0.5))
    star_ = star(-0.4, -1.7, 0.75, 5, 0.45)
    diamonds = [poly((x, -0.9), (x + 0.25, -1.2), (x, -1.5), (x - 0.25, -1.2)) for x in (-1.45, 0.65)] + \
               [poly((x, -1.9), (x + 0.25, -2.2), (x, -2.5), (x - 0.25, -2.2)) for x in (-1.45, 0.65)]
    side_c = poly((1.15, -1.9), (1.6, -1.6), (1.6, -1.1), (1.15, -1.4))
    lid = poly((-1.75 + dx, -0.5 + dy), (0.95 + dx, -0.5 + dy), (2.05 + 0.2, 2.1), (-0.65 + 0.2, 2.1))
    crank = [circle(1.4, -1.5, 0.12, 12), tube([(1.4, -1.5), (2.3, -1.7)], 0.14), tube([(2.3, -1.7), (2.35, -1.1)], 0.14), ellipse(2.4, -0.95, 0.12, 0.22, 14)]
    spring = []
    pts = []
    for i in range(9):
        y = -0.3 + i * 0.17
        pts.append((-0.35 + (0.42 if i % 2 else -0.42), y))
    spring = [smooth(pts, 2, closed=False)]
    ang = [TAU * i / 360 for i in range(361)]
    collar = [(-0.35 + (1.15 + 0.22 * math.cos(12 * t)) * math.cos(t), 1.05 + (0.5 + 0.1 * math.cos(12 * t)) * math.sin(t)) for t in ang]
    head = circle(-0.35, 1.85, 0.78, 60)
    eyes_ = [circle(-0.65, 2.0, 0.13, 12), circle(-0.05, 2.0, 0.13, 12)]
    nose = circle(-0.35, 1.72, 0.19, 16)
    smile = arc(-0.35, 1.75, 0.48, math.radians(205), math.radians(335), 16)
    cheeks = [circle(-0.85, 1.55, 0.13, 12), circle(0.15, 1.55, 0.13, 12)]
    hair = [spiral(-1.15, 2.05, 0.04, 0.25, 1.3, 24), mirror_x(spiral(-1.15, 2.05, 0.04, 0.25, 1.3, 24), -0.35)]
    hat = poly((-0.95, 2.4), (0.25, 2.45), (0.45, 3.55))
    pom = circle(0.5, 3.7, 0.17, 14)
    hat_dots = keep([circle(-0.3, 2.65, 0.1, 10), circle(0.15, 2.95, 0.08, 8)], hat)
    return make("Jack-in-the-Box", scene(
        ([lid], [lid]),
        ([front, side, top] + [star_] + diamonds + [side_c], [front, top_cv, poly((0.95, -2.9), (0.95 + dx, -2.9 + dy), (0.95 + dx, -0.5 + dy), (0.95, -0.5))]),
        (crank, crank[1:3]),
        (spring, []),
        ([collar], [collar]),
        ([head, nose, smile] + cheeks + hair, [head]),
        ([hat] + hat_dots, [hat]),
        ([pom], [pom])), eyes_)


@design("vintage_porcelain_doll", T)
def porcelain_doll(rng):
    head = circle(0, 1.35, 0.82, 60)
    bonnet = chain(arc(0, 1.4, 1.25, -0.35, math.pi + 0.35, 60))
    bonnet_cv = bonnet + [bonnet[0]]
    ruffle = scallop(arc(0, 1.4, 1.02, -0.2, math.pi + 0.2, 50), 0.11, out=1)
    curls_l = [spiral(-0.95, 0.45, 0.04, 0.22, 1.3, 24), spiral(-1.1, 0.0, 0.04, 0.22, 1.3, 24)]
    curls = curls_l + [mirror_x(c) for c in curls_l]
    eyes_ = [ellipse(-0.3, 1.42, 0.17, 0.12, 16), ellipse(0.3, 1.42, 0.17, 0.12, 16)]
    brows = [arc(-0.3, 1.45, 0.25, 1.1, 2.0, 6), arc(0.3, 1.45, 0.25, 1.1, 2.0, 6)]
    mouth = heart(0, 0.95, 0.09)
    cheeks = [circle(-0.48, 1.1, 0.13, 12), circle(0.48, 1.1, 0.13, 12)]
    bow = [lens((0, 0.45), (-0.55, 0.65), 0.4), lens((0, 0.45), (0.55, 0.65), 0.4), circle(0, 0.45, 0.1, 10),
           seg((-0.05, 0.38), (-0.25, -0.05)), seg((0.05, 0.38), (0.25, -0.05))]
    ties = [seg((-1.05, 0.95), (-0.12, 0.48)), seg((1.05, 0.95), (0.12, 0.48))]
    body = poly((-0.6, 0.45), (0.6, 0.45), (0.5, -0.55), (-0.5, -0.55))
    collar = scallop([(-0.62, 0.38), (0.0, 0.05), (0.62, 0.38)], 0.12, out=-1)
    sleeves = [ellipse(-0.85, 0.15, 0.38, 0.45, 30), ellipse(0.85, 0.15, 0.38, 0.45, 30)]
    arms = [tube([(-0.95, -0.2), (-0.75, -0.9)], 0.22), tube([(0.95, -0.2), (0.75, -0.9)], 0.22)]
    hands = [circle(-0.72, -1.0, 0.15, 12), circle(0.72, -1.0, 0.15, 12)]
    sk = cubic((-0.55, -0.5), (-1.3, -1.0), (-1.9, -1.8), (-2.2, -2.3), 20)
    hem = []
    for k in range(6):
        a, b = -2.2 + k * 4.4 / 6, -2.2 + (k + 1) * 4.4 / 6
        hem = chain(hem, quad((a, -2.3), ((a + b) / 2, -2.55), (b, -2.3), 10))
    skirt = chain(sk, hem, mirror_x(sk)[::-1])
    skirt_cv = skirt + [skirt[0]]
    frill = scallop(hem, 0.12, out=-1)
    pleats = [quad((x * 0.3, -0.6), (x * 0.8, -1.4), (x, -2.35), 10) for x in (-1.4, -0.5, 0.5, 1.4)]
    sash = quad((-0.58, -0.45), (0, -0.62), (0.58, -0.45), 10)
    legs = [tube([(-0.5, -2.4), (-0.6, -2.9)], 0.3), tube([(0.5, -2.4), (0.6, -2.9)], 0.3)]
    shoes = [ellipse(-0.7, -3.0, 0.32, 0.17, 20), ellipse(0.7, -3.0, 0.32, 0.17, 20)]
    return make("Porcelain Doll in a Bonnet", scene(
        (legs, legs),
        (shoes, shoes),
        ([skirt] + pleats, [skirt_cv]),
        ([frill], []),
        ([body, sash], [body]),
        (sleeves, sleeves),
        (arms, arms),
        (hands, hands),
        ([bonnet, ruffle], [bonnet_cv]),
        (curls, []),
        (ties, []),
        ([head, mouth] + eyes_ + brows + cheeks, [head]),
        (bow, bow[:3])), [eye(-0.3, 1.42, 0.07), eye(0.3, 1.42, 0.07)])


@design("vintage_marbles_bag", T)
def marbles_bag(rng):
    bx = -0.9
    bag = smooth([(bx - 0.4, 0.95), (bx - 1.5, -0.2), (bx - 1.65, -1.6), (bx - 0.6, -2.4), (bx + 0.8, -2.35), (bx + 1.6, -1.5),
                  (bx + 1.45, -0.2), (bx + 0.4, 0.95)], 2)
    frill = smooth([(bx - 0.4, 0.95), (bx - 1.1, 1.5), (bx - 0.7, 1.85), (bx - 0.3, 1.6), (bx, 1.95), (bx + 0.3, 1.6), (bx + 0.75, 1.85),
                    (bx + 1.1, 1.45), (bx + 0.4, 0.95)], 2)
    tie = rrect(bx - 0.55, 0.75, bx + 0.55, 1.05, 0.12)
    cord = [cubic((bx + 0.5, 0.9), (bx + 1.3, 0.8), (bx + 1.5, 0.3), (bx + 1.3, -0.1), 20),
            cubic((bx + 0.5, 0.9), (bx + 1.4, 1.2), (bx + 1.9, 0.9), (bx + 2.0, 0.4), 20)]
    knots = [circle(bx + 1.3, -0.22, 0.12, 12), circle(bx + 2.0, 0.28, 0.12, 12)]
    folds = [cubic((bx - 0.2, 0.7), (bx - 0.6, 0.0), (bx - 0.9, -0.8), (bx - 0.8, -1.6), 16),
             cubic((bx + 0.25, 0.7), (bx + 0.5, 0.0), (bx + 0.7, -0.6), (bx + 0.5, -1.2), 16)]
    patch = keep([circle(bx + 0.1, -1.4, 0.45, 30)], bag)

    def marble(x, y, r, kind):
        out = [circle(x, y, r, 40)]
        if kind == 0:
            out.append(lens((x - 0.7 * r, y - 0.35 * r), (x + 0.7 * r, y + 0.35 * r), 0.25))
        elif kind == 1:
            out += [cubic((x - r, y), (x - 0.3 * r, y + 0.7 * r), (x + 0.3 * r, y - 0.7 * r), (x + r, y), 16)]
        else:
            out += [arc(x, y, 0.55 * r, 0.5, 2.6, 10), arc(x, y, 0.55 * r, 3.6, 5.7, 10)]
        out.append(arc(x, y, 0.75 * r, 1.9, 2.5, 6))
        return out
    ms = [(1.2, -2.35, 0.55, 0), (2.4, -1.9, 0.42, 1), (1.85, -0.95, 0.4, 2), (0.65, -0.85, 0.36, 1), (2.55, -0.25, 0.32, 0),
          (-2.35, -2.75, 0.3, 2), (1.45, 0.35, 0.3, 2)]
    marbles = [marble(*m) for m in ms]
    layers = [([bag] + folds + patch, [bag]), ([frill], [frill]), ([tie], [tie]), (cord, []), (knots, knots)]
    for m in marbles:
        layers.append((m, [m[0]]))
    return make("Bag of Glass Marbles", scene(*layers))


@design("vintage_spinning_tops", T)
def spinning_tops(rng):
    def T1():
        prof = smooth([(0.0, 1.7), (0.25, 1.65), (0.3, 1.45), (1.25, 1.05), (1.35, 0.6), (0.9, -0.3), (0.35, -0.9), (0.08, -1.1)], 2, closed=False)
        body = chain(mirror_x(prof)[::-1], prof)
        body = body + [body[0]]
        stem = rect(-0.15, 1.65, 0.15, 2.15)
        knob = circle(0, 2.25, 0.15, 12)
        peg = poly((-0.1, -1.08), (0.1, -1.08), (0, -1.5))
        bands = [quad((-1.3, 0.95), (0, 0.65), (1.3, 0.95), 16), quad((-1.33, 0.6), (0, 0.3), (1.33, 0.6), 16), quad((-0.95, -0.2), (0, -0.4), (0.95, -0.2), 16)]
        return [body, stem, knob, peg] + keep(bands, body), [body, stem, knob]
    s1, c1 = T1()
    s1 = [transform(p, -1.0, 0.3, 1.25, -0.2) for p in s1]
    c1 = [transform(p, -1.0, 0.3, 1.25, -0.2) for p in c1]
    cx, cy = 1.75, -1.3
    dome = ellipse(cx, cy, 1.2, 0.85, 70)
    rim = quad((cx - 1.2, cy), (cx, cy - 0.35), (cx + 1.2, cy), 20)
    mer = keep([quad((cx + x * 0.3, cy + 0.85), (cx + x * 0.9, cy), (cx + x * 0.3, cy - 0.85), 16) for x in (-1.0, -0.4, 0.4, 1.0)], dome)
    rod = [[(cx + 0.12 * math.sin(i * 0.9), cy + 0.8 + i * 0.1) for i in range(16)]]
    rod_box = [seg((cx - 0.15, cy + 0.82), (cx - 0.15, cy + 2.3)), seg((cx + 0.15, cy + 0.82), (cx + 0.15, cy + 2.3))]
    handle = rrect(cx - 0.5, cy + 2.3, cx + 0.5, cy + 2.6, 0.13)
    foot = poly((cx - 0.15, cy - 0.85), (cx + 0.15, cy - 0.85), (cx, cy - 1.1), closed=False)
    swish = [arc(-1.25, -1.6, 0.9, math.radians(200), math.radians(300), 12), arc(-1.25, -1.6, 1.25, math.radians(210), math.radians(290), 12)]
    ground = seg((-3.0, -2.6), (3.0, -2.6))
    string = cubic((-2.9, -2.6), (-2.2, -1.5), (-3.0, 1.0), (-2.2, 2.0), 30)
    return make("Spinning Tops", scene(
        (s1, c1),
        ([dome, rim] + mer + rod + rod_box + [foot], [dome]),
        ([handle], [handle]),
        (swish, [])) + [ground])


# dropped: binoculars elsewhere / protected design
def opera_glasses(rng):
    def barrel(oy):
        top = [(-1.7, oy + 0.78), (-1.0, oy + 0.62), (0.0, oy + 0.55), (0.0, oy + 0.4), (0.5, oy + 0.4)]
        bot = [(x, 2 * oy - y) for x, y in top]
        outline = chain(top, [(0.5, oy - 0.4)], bot[::-1], [(-1.7, oy + 0.78)])
        lensf = ellipse(-1.7, oy, 0.24, 0.78, 40)
        lensi = ellipse(-1.72, oy, 0.13, 0.55, 30)
        bands = [seg((-1.0, oy + 0.62), (-1.0, oy - 0.62)), seg((-0.35, oy + 0.58), (-0.35, oy - 0.58)), seg((0.0, oy + 0.55), (0.0, oy - 0.55))]
        pearl = keep([seg((x, oy - 1), (x + 0.25, oy + 1)) for x in (-0.95, -0.75, -0.55)], rect(-1.0, oy - 0.62, -0.35, oy + 0.62))
        eyep = ellipse(0.5, oy, 0.1, 0.4, 20)
        return [outline, lensf, lensi, eyep] + bands, [outline, lensf]
    a, ac = barrel(0.0)
    a = [transform(p, 0.4, 1.25, 1.2) for p in a]
    ac = [transform(p, 0.4, 1.25, 1.2) for p in ac]
    b, bc = barrel(0.0)
    b = [transform(p, -0.2, -0.35, 1.25) for p in b]
    bc = [transform(p, -0.2, -0.35, 1.25) for p in bc]
    bridge = rect(0.1, -0.1, 0.5, 1.0)
    wheel = ellipse(0.3, 0.45, 0.32, 0.18, 24)
    ridges = [seg((x, 0.3), (x, 0.6)) for x in (0.12, 0.3, 0.48)]
    handle = tube([(-0.5, -1.0), (-1.4, -2.2), (-2.1, -3.1)], 0.2)
    handle_end = circle(-2.2, -3.2, 0.2, 16)
    ring = rect(-0.75, -1.45, -0.45, -1.25)
    return make("Opera Glasses with Handle", scene(
        (a, ac),
        ([bridge] + ridges, [bridge]),
        ([wheel], [wheel]),
        ([handle], [handle]),
        ([handle_end], [handle_end]),
        (b, bc)))


@design("vintage_gas_street_lamp", T)
def gas_street_lamp(rng):
    ps = cubic((-0.85, -3.0), (-0.85, -2.4), (-0.3, -2.3), (-0.25, -1.7), 20)
    plinth = chain(ps, mirror_x(ps)[::-1], [ps[0]])
    flutes = keep([seg((x, -2.95), (x * 0.4, -1.8)) for x in (-0.45, 0.0, 0.45)], plinth)
    shaft = tube([(0, -1.75), (0, 1.75)], lambda t: 0.36 - 0.12 * t)
    collars = [rect(-0.3, -1.8, 0.3, -1.6), rect(-0.25, 0.1, 0.25, 0.3), rect(-0.22, 1.55, 0.22, 1.75)]
    bar = tube([(-1.0, 1.35), (1.0, 1.35)], 0.13)
    bar_ends = [circle(-1.05, 1.35, 0.13, 12), circle(1.05, 1.35, 0.13, 12)]
    bowl = poly((-0.2, 1.75), (0.2, 1.75), (0.75, 2.1), (-0.75, 2.1))
    cage = poly((-0.75, 2.1), (0.75, 2.1), (1.0, 3.4), (-1.0, 3.4))
    frames = [seg((-0.3, 2.1), (-0.38, 3.4)), seg((0.3, 2.1), (0.38, 3.4))]
    flame = chain(quad((0, 3.0), (-0.22, 2.75), (-0.2, 2.5), 8), arc(0, 2.5, 0.2, math.pi, 2 * math.pi, 10), quad((0.2, 2.5), (0.22, 2.75), (0, 3.0), 8))
    burner = seg((0, 2.1), (0, 2.3))
    roof = poly((-1.2, 3.4), (1.2, 3.4), (0.35, 3.95), (-0.35, 3.95))
    dome = chain(arc(0, 3.95, 0.3, 0, math.pi, 12))
    spike = poly((-0.08, 4.25), (0, 4.65), (0.08, 4.25), closed=False)
    rays = [seg((1.3 * math.cos(a), 2.75 + 1.3 * math.sin(a)), (1.75 * math.cos(a), 2.75 + 1.75 * math.sin(a))) for a in (0.0, 0.5, math.pi, math.pi - 0.5, -0.45, math.pi + 0.45)]
    stones = [rrect(x, y, x + 0.75, y + 0.35, 0.12) for x, y in ((-2.4, -3.1), (-1.55, -3.15), (0.95, -3.1), (1.8, -3.15), (-2.0, -3.6), (-1.1, -3.6), (-0.2, -3.6), (0.7, -3.6), (1.6, -3.6))]
    return make("Gas Street Lamp", scene(
        (stones, []),
        ([shaft], [shaft]),
        (collars, collars),
        ([bar] + bar_ends, [bar] + bar_ends),
        ([plinth] + flutes, [plinth]),
        ([cage, flame, burner] + frames, [cage]),
        ([bowl], [bowl]),
        ([roof, dome, spike], [roof]),
        (rays, [])))


# dropped: binoculars elsewhere / protected design
def telephone_box(rng):
    dx, dy = 0.6, 0.35
    X0, X1, Y0, Y1 = -1.25, 1.05, -3.0, 2.2
    front = rect(X0, Y0, X1, Y1)
    side = poly((X1, Y0), (X1 + dx, Y0 + dy), (X1 + dx, Y1 + dy), (X1, Y1), closed=False)
    door = rect(X0 + 0.22, Y0 + 0.25, X1 - 0.22, 1.5)
    px0, px1, py0, py1 = X0 + 0.42, X1 - 0.42, -1.35, 1.3
    panes = [rect(px0, py0, px1, py1)]
    for k in (1, 2):
        x = px0 + (px1 - px0) * k / 3
        panes.append(seg((x, py0), (x, py1)))
    for k in range(1, 8):
        y = py0 + (py1 - py0) * k / 8
        panes.append(seg((px0, y), (px1, y)))
    handle = rrect(X1 - 0.38, -0.7, X1 - 0.28, 0.0, 0.05)
    lower = rrect(px0, Y0 + 0.5, px1, -1.6, 0.08)
    sign = rrect(X0 + 0.25, 1.68, X1 - 0.25, 2.05, 0.08)

    def S(t, y):
        return (X1 + dx * t, y + dy * t)
    spanes = [poly(S(0.25, py0), S(0.75, py0), S(0.75, py1), S(0.25, py1))]
    for k in range(1, 8):
        y = py0 + (py1 - py0) * k / 8
        spanes.append(seg(S(0.25, y), S(0.75, y)))
    ssign = poly(S(0.2, 1.68), S(0.8, 1.68), S(0.8, 2.05), S(0.2, 2.05))
    pedi = chain([(X0 - 0.1, Y1)], quad((X0 - 0.1, Y1), ((X0 + X1) / 2, Y1 + 0.9), (X1 + 0.1, Y1), 20), [(X0 - 0.1, Y1)])
    spedi = quad((X1 + 0.1, Y1), (X1 + dx * 0.5, Y1 + 0.7), (X1 + dx, Y1 + dy), 10)
    dome = chain(arc((X0 + X1) / 2 + 0.25, Y1 + 0.6, 0.6, 0.15, math.pi - 0.15, 20))
    crown = circle((X0 + X1) / 2, Y1 + 0.38, 0.15, 14)
    plinth = poly((X0 - 0.15, Y0), (X0 - 0.15, Y0 - 0.25), (X1 + 0.15, Y0 - 0.25), (X1 + dx + 0.15, Y0 + dy - 0.25), (X1 + dx + 0.15, Y0 + dy - 0.05), (X1 + dx, Y0 + dy), closed=False)
    return make("Old-Fashioned Telephone Box", scene(
        ([front, side, door, handle, lower, sign, ssign, spedi, plinth] + panes + spanes, [front]),
        ([pedi, crown], [pedi])))


@design("vintage_shaving_set", T)
def shaving_set(rng):
    mx = -1.45
    mug = chain([(mx - 1.2, -0.9), (mx - 1.2, -2.2)], [(mx + 1.2 * math.cos(t), -2.2 + 0.3 * math.sin(t)) for t in [math.pi + math.pi * i / 30 for i in range(31)]], [(mx + 1.2, -0.9)])
    mug_cv = mug + [mug[0]]
    rim = ellipse(mx, -0.9, 1.2, 0.3, 50)
    stripes = [quad((mx - 1.2, y), (mx, y - 0.3), (mx + 1.2, y), 16) for y in (-1.25, -1.85)]
    handle = [chain(arc(mx - 1.2, -1.55, 0.45, math.pi / 2, 1.5 * math.pi, 20)), chain(arc(mx - 1.2, -1.55, 0.25, math.pi / 2, 1.5 * math.pi, 16))]
    foam = smooth([(mx - 1.0, -0.95), (mx - 0.9, -0.7), (mx - 0.5, -0.55), (mx - 0.1, -0.62), (mx + 0.35, -0.5), (mx + 0.85, -0.68), (mx + 1.0, -0.95)], 2)
    bubbles = [circle(mx - 0.5, -0.25, 0.12, 12), circle(mx + 0.2, -0.15, 0.09, 10)]
    bx = 1.2
    bh = tube([(bx, -2.45), (bx, -0.6)], lambda t: 0.75 - 0.45 * math.sin(math.pi * t * 0.9) + 0.15 * math.exp(-((t - 0.85) / 0.06) ** 2))
    foot = ellipse(bx, -2.45, 0.5, 0.12, 24)
    ferrule = rect(bx - 0.45, -0.6, bx + 0.45, -0.3)
    knot = chain([(bx - 0.45, -0.3)], cubic((bx - 0.45, -0.3), (bx - 1.0, 0.6), (bx - 0.7, 1.4), (bx, 1.45), 20),
                 cubic((bx, 1.45), (bx + 0.7, 1.4), (bx + 1.0, 0.6), (bx + 0.45, -0.3), 20))
    knot_cv = knot + [knot[0]]
    bristles = keep([quad((bx + x * 0.3, -0.3), (bx + x * 0.5, 0.5), (bx + x * 0.6, 1.5), 10) for x in (-1, 0, 1)], knot_cv)

    def razor():
        blade = chain([(0, 0.1)], [(1.9, 0.18)], quad((1.9, 0.18), (2.25, 0.15), (2.25, -0.2), 8), quad((2.25, -0.2), (1.2, -0.45), (0.15, -0.3), 12), [(0, 0.1)])
        spine = seg((0.1, -0.0), (1.95, 0.05))
        tang = poly((0, 0.1), (-0.35, 0.05), (-0.45, -0.1), (0.15, -0.3), closed=False)
        scale = smooth([(-0.25, 0.2), (-2.2, 0.55), (-2.4, 0.3), (-2.2, 0.15), (-0.25, -0.15)], 2)
        pin = circle(-0.2, 0.02, 0.09, 10)
        return [scale, blade, spine, tang, pin], [scale, blade]
    rs, rc = razor()
    tf = lambda p: transform(p, 0.35, -2.75, 1.05, 0.06)
    rs = [tf(p) for p in rs]
    rc = [tf(p) for p in rc]
    return make("Shaving Mug, Brush and Razor", scene(
        ([knot] + bristles, [knot_cv]),
        ([ferrule], [ferrule]),
        ([bh, foot], [bh, foot]),
        (handle, [chain(arc(mx - 1.0, -1.2, 0.55, math.pi / 2, 1.5 * math.pi, 20))]),
        ([mug, rim] + stripes, [mug_cv]),
        ([foam] + bubbles, [foam]),
        (rs[:1], rc[:1]),
        (rs[1:], rc[1:])))


@design("vintage_barber_pole", T)
def barber_pole(rng):
    R, y0, y1 = 0.75, -2.0, 2.0
    glass = rect(-R, y0, R, y1)
    stripes = []
    pitch = 2.0
    for k in range(-6, 8):
        off = y0 + k * pitch / 4
        stripes.append([(R * math.sin(t), off + pitch * (t + math.pi / 2) / TAU) for t in [-math.pi / 2 + math.pi * i / 30 for i in range(31)]])
    stripes = keep(stripes, glass)
    shine = seg((-0.5, y0 + 0.3), (-0.5, y1 - 0.3))
    bt = rect(-0.95, y1, 0.95, y1 + 0.3)
    dome_t = chain(arc(0, y1 + 0.3, 0.95, 0, math.pi, 30))
    ball_t = circle(0, y1 + 1.5, 0.28, 20)
    neck_t = rect(-0.12, y1 + 1.2, 0.12, y1 + 1.25)
    bb = rect(-0.95, y0 - 0.3, 0.95, y0)
    dome_b = chain(arc(0, y0 - 0.3, 0.95, math.pi, 2 * math.pi, 30))
    ball_b = circle(0, y0 - 1.5, 0.28, 20)
    plate = rrect(1.75, -2.6, 2.1, 2.6, 0.1)
    arms = [tube([(0.95, y1 + 0.15), (1.75, y1 + 0.15)], 0.16), tube([(0.95, y0 - 0.15), (1.75, y0 - 0.15)], 0.16)]
    screws = [circle(1.92, 2.35, 0.08, 8), circle(1.92, -2.35, 0.08, 8)]
    return make("Barber Pole", scene(
        ([plate] + screws, [plate]),
        (arms, arms),
        ([glass, shine] + stripes, [glass]),
        ([bt, dome_t], [bt, dome_t + [dome_t[0]]]),
        ([bb, dome_b], [bb, dome_b + [dome_b[0]]]),
        ([ball_t, ball_b], [ball_t, ball_b])))


@design("vintage_brass_microscope", T)
def brass_microscope(rng):
    base = smooth([(-1.9, -2.8), (1.6, -2.8), (1.5, -2.45), (0.9, -2.3), (-1.2, -2.3), (-1.8, -2.45)], 1)
    pillar = rect(0.45, -2.35, 0.95, -1.15)
    hinge = circle(0.7, -1.05, 0.25, 20)
    arm = tube(cubic((0.7, -1.0), (1.8, 0.2), (1.5, 1.6), (0.15, 1.75), 40), 0.5)
    tube_ = rect(-1.0, -0.05, -0.25, 2.35)
    rings = [seg((-1.0, 0.6), (-0.25, 0.6))]
    eyep = rect(-0.85, 2.35, -0.4, 3.05)
    cap = ellipse(-0.625, 3.05, 0.3, 0.08, 16)
    rack = rect(-0.25, 0.9, 0.25, 2.1)
    knob = [circle(0.15, 1.75, 0.38, 30), circle(0.15, 1.75, 0.14, 14)]
    nose = poly((-1.05, -0.05), (-0.2, -0.05), (-0.35, -0.3), (-0.9, -0.3))
    obj = [poly((-0.95, -0.3), (-0.75, -0.3), (-0.8, -0.65), (-0.9, -0.65)), poly((-0.5, -0.3), (-0.3, -0.3), (-0.33, -0.55), (-0.47, -0.55))]
    stage = rect(-2.1, -1.05, 0.6, -0.85)
    slide = rect(-1.45, -0.85, 0.0, -0.75)
    clips = [poly((-1.9, -0.85), (-1.9, -0.72), (-1.4, -0.72), closed=False), poly((0.3, -0.85), (0.3, -0.72), (-0.15, -0.72), closed=False)]
    yoke = chain([(-1.05, -2.0), (-1.05, -1.6)], [(-0.25, -1.6), (-0.25, -2.0)])
    mirror = ellipse(-0.65, -1.95, 0.48, 0.22, 30, rot=0.25)
    mstem = seg((-0.65, -1.6), (0.45, -1.6))
    return make("Brass Microscope", scene(
        ([mstem, yoke], []),
        ([mirror], [mirror]),
        ([base], [base]),
        ([pillar], [pillar]),
        ([arm], [arm]),
        ([hinge], [hinge]),
        ([rack], [rack]),
        ([tube_] + rings, [tube_]),
        ([eyep, cap], [eyep]),
        (knob, [knob[0]]),
        ([nose] + obj, [nose] + obj),
        ([stage, slide] + clips, [stage, slide])))


@design("vintage_baby_pram", T)
def baby_pram(rng):
    body = chain([(-2.3, 0.3), (1.5, 0.3)], cubic((1.5, 0.3), (1.5, -0.6), (1.0, -1.1), (0.2, -1.1), 16), [(-1.4, -1.1)],
                 cubic((-1.4, -1.1), (-2.1, -1.1), (-2.3, -0.5), (-2.3, 0.3), 16))
    body_cv = body + [body[0]]
    lace = scallop([(-2.3, 0.3), (1.5, 0.3)], 0.13, out=-1)
    panel = smooth([(-1.9, 0.0), (1.15, 0.0), (1.0, -0.75), (-1.5, -0.75)], 2)
    hood = chain(arc(-1.0, 0.3, 1.35, 0, math.pi, 50))
    hood_cv = hood + [hood[0]]
    hood_lines = [[(-1.0 + 1.35 * f * math.cos(t), 0.3 + 1.35 * math.sin(t)) for t in [math.pi * i / 30 for i in range(31)]] for f in (0.75, 0.45)]
    handle = tube([(1.4, 0.1), (2.4, 1.6)], 0.14)
    grip = tube([(2.15, 1.75), (2.75, 1.4)], 0.22)
    springs = [chain(arc(-1.3, -1.45, 0.35, math.pi / 2, 1.5 * math.pi, 12)), chain(arc(0.7, -1.45, 0.35, -math.pi / 2, math.pi / 2, 12))]
    chassis = seg((-1.6, -2.0), (1.0, -2.1))
    wheels = []
    for x, y, r in ((-1.6, -2.0, 0.9), (1.05, -2.15, 0.75)):
        wheels += [circle(x, y, r, 60), circle(x, y, r - 0.12, 50), circle(x, y, 0.1, 10)] + spokes(x, y, 0.1, r - 0.12, 10)
    return make("Victorian Baby Pram", scene(
        (wheels, []),
        ([chassis] + springs, []),
        ([handle, grip], [handle]),
        ([hood] + hood_lines, [hood_cv]),
        ([body, panel, lace], [body_cv])))


@design("vintage_banjo_barometer", T)
def banjo_barometer(rng):
    cy = -1.3
    a = math.atan2(1.502, 0.55)
    outline = chain([(-0.55, 2.8), (-0.55, cy + 1.502)], arc(0, cy, 1.6, math.pi - a, 2 * math.pi + a, 90), [(0.55, 2.8)])
    bezel = circle(0, cy, 1.32, 90)
    dial = circle(0, cy, 1.12, 80)
    sc = [seg((0.85 * math.cos(math.radians(d)), cy + 0.85 * math.sin(math.radians(d))), ((0.98 if d % 30 else 1.08) * math.cos(math.radians(d)), cy + (0.98 if d % 30 else 1.08) * math.sin(math.radians(d))))
          for d in range(-30, 211, 15)]
    scale_arc = arc(0, cy, 0.85, math.radians(-30), math.radians(210), 40)
    ptr = hand(0, cy, 0.95, math.radians(55), 0.05)
    ptr2 = [seg((0, cy), (0.7 * math.cos(math.radians(120)), cy + 0.7 * math.sin(math.radians(120))))]
    hub = circle(0, cy, 0.1, 10)
    thermo_plate = rrect(-0.35, 0.35, 0.35, 2.15, 0.1)
    thermo = rrect(-0.07, 0.65, 0.07, 1.95, 0.07)
    bulb = circle(0, 0.6, 0.13, 12)
    tks = [seg((0.12, y), (0.25, y)) for y in (0.95, 1.2, 1.45, 1.7)]
    small = [circle(0, 2.48, 0.3, 24), seg((0, 2.48), (0.15, 2.65))]
    top = rect(-0.75, 2.8, 0.75, 3.0)
    neck = cubic((-0.75, 3.0), (-0.65, 3.6), (-0.3, 3.25), (-0.18, 3.5), 16)
    pedi = [neck, mirror_x(neck), spiral(-0.18, 3.38, 0.02, 0.12, 1.2, 20, rot=1.6), mirror_x(spiral(-0.18, 3.38, 0.02, 0.12, 1.2, 20, rot=1.6))]
    urn = chain(quad((-0.1, 3.0), (-0.22, 3.3), (-0.08, 3.45), 8), [(0.08, 3.45)], quad((0.08, 3.45), (0.22, 3.3), (0.1, 3.0), 8))
    fin = circle(0, 3.62, 0.13, 12)
    drop = lens((0, cy - 1.6), (0, cy - 2.2), 0.25)
    level = rrect(-0.35, cy - 1.55, 0.35, cy - 1.38, 0.08)
    return make("Banjo Barometer", [outline, bezel, dial, scale_arc, ptr, hub, thermo_plate, thermo, bulb, top, urn, fin, drop, level]
                + sc + ptr2 + tks + small + pedi)


@design("vintage_desk_fan", T)
def desk_fan(rng):
    cx, cy = 0.0, 0.85
    rim = circle(cx, cy, 2.0, 120)
    rings = [circle(cx, cy, 1.35, 90), circle(cx, cy, 0.75, 60)]
    wires = spokes(cx, cy, 0.42, 2.0, 12, 0.13)
    badge = [circle(cx, cy, 0.42, 30), circle(cx, cy, 0.18, 16)]
    blades = [transform(lens((0, 0.0), (0, 1.75), 0.32), cx, cy, 1.0, k * math.pi / 2 + 0.6) for k in range(4)]
    blades = hide(blades, badge[0])
    motor = ellipse(0.0, cy, 1.0, 1.0, 40)
    neck = tube([(0, cy - 2.0), (0, -1.95)], 0.36)
    joint = circle(0, -1.3, 0.22, 16)
    bs = cubic((-1.7, -2.9), (-1.6, -2.2), (-0.6, -2.0), (-0.3, -1.95), 20)
    base = chain(bs, mirror_x(bs)[::-1], [bs[0]])
    switch = [rect(0.8, -2.7, 1.1, -2.45), circle(-0.95, -2.5, 0.13, 12)]
    breeze = [wave(2.25, 3.2, 1.6, 0.1, 1.5, 20), wave(2.3, 3.3, 0.9, 0.1, 1.5, 20), wave(2.25, 3.2, 0.2, 0.1, 1.5, 20)]
    return make("Oscillating Desk Fan", scene(
        ([neck], [neck]),
        ([joint], [joint]),
        ([base] + switch, [base]),
        (blades, blades),
        ([rim] + rings + wires + badge, [rim]),
        (breeze, [])))


@design("vintage_vanity_table", T)
def vanity_table(rng):
    top = rrect(-2.7, -0.25, 2.7, 0.05, 0.08)
    apron = chain([(-2.45, -0.25), (-2.45, -0.95)], scallop([(-2.45, -0.95), (2.45, -0.95)], 0.2, out=-1), [(2.45, -0.95), (2.45, -0.25)])
    dl = [seg((-0.8, -0.25), (-0.8, -0.85)), seg((0.8, -0.25), (0.8, -0.85))]
    knobs = [circle(x, -0.55, 0.1, 10) for x in (-1.6, 0.0, 1.6)]

    def cab(x, s):
        return chain([(x, -0.95)], cubic((x, -0.95), (x + 0.35 * s, -1.5), (x - 0.3 * s, -2.3), (x - 0.05 * s, -2.9), 16),
                     [(x + 0.25 * s, -2.9)], cubic((x + 0.25 * s, -2.9), (x + 0.0 * s, -2.3), (x + 0.6 * s, -1.6), (x + 0.3 * s, -0.95), 16))
    legs = [cab(-2.4, 1), cab(2.4, -1)]
    frame = ellipse(0, 1.85, 1.3, 1.6, 90)
    mirror = ellipse(0, 1.85, 1.08, 1.38, 80)
    glare = [seg((-0.55, 2.35), (-0.05, 2.9)), seg((-0.65, 1.8), (0.15, 2.7))]
    posts = [tube([(x, 0.05), (x, 2.0)], 0.2) for x in (-1.55, 1.55)]
    finials = [circle(x, 2.2, 0.17, 14) for x in (-1.55, 1.55)]
    pivots = [circle(x, 1.85, 0.12, 12) for x in (-1.36, 1.36)]
    crest = [lens((0, 3.4), (-0.6, 3.75), 0.35), lens((0, 3.4), (0.6, 3.75), 0.35), circle(0, 3.45, 0.12, 12)]
    bottle = [circle(-2.1, 0.4, 0.33, 24), rect(-2.18, 0.72, -2.02, 0.85), circle(-2.1, 0.98, 0.13, 12)]
    brush = [ellipse(1.95, 0.35, 0.45, 0.28, 24), tube([(1.55, 0.25), (0.95, 0.12)], 0.16)]
    box = [rect(1.0, 0.05, 1.5, 0.35)]
    return make("Vanity Table with Oval Mirror", scene(
        (posts, posts),
        (finials + pivots, finials),
        ([frame, mirror] + glare, [frame]),
        (crest, crest),
        (legs, []),
        ([apron] + dl + knobs, [rect(-2.45, -1.15, 2.45, -0.25)]),
        ([top], [top]),
        (bottle, bottle),
        (box, box),
        (brush, brush)))


@design("vintage_bowler_hat_cane", T)
def bowler_hat_cane(rng):
    cane = tube([(-2.4, -3.0), (1.6, 2.4)], 0.2)
    crook = tube(chain(arc(2.05, 2.4, 0.45, math.pi, 0.0, 16), [(2.5, 2.0)]), 0.22)
    ferrule = transform(rect(-0.12, -0.2, 0.12, 0.2), -2.33, -2.9, 1.0, -0.64)
    collar_ = transform(rect(-0.15, -0.12, 0.15, 0.12), 1.48, 2.24, 1.0, -0.64)
    brim = ellipse(0, -0.05, 2.0, 0.55, 90)
    curl = [(1.75 * math.cos(t), -0.02 + 0.38 * math.sin(t)) for t in [math.pi + 0.15 + (math.pi - 0.3) * i / 40 for i in range(41)]]
    crown = chain(cubic((-1.35, -0.05), (-1.5, 1.2), (-1.0, 2.05), (0, 2.05), 20),
                  cubic((0, 2.05), (1.0, 2.05), (1.5, 1.2), (1.35, -0.05), 20))
    crown_cv = crown + [crown[0]]
    band_lo = quad((-1.36, 0.05), (0, -0.25), (1.36, 0.05), 16)
    band_hi = quad((-1.4, 0.45), (0, 0.15), (1.4, 0.45), 16)
    bow = [lens((-1.0, 0.18), (-0.55, 0.4), 0.4), lens((-1.0, 0.18), (-0.5, 0.0), 0.4)]
    mono = [circle(1.0, -1.85, 0.5, 40), circle(1.0, -1.85, 0.4, 36)]
    mchain = cubic((1.48, -1.95), (2.2, -2.4), (2.4, -1.4), (2.9, -2.2), 20)
    return make("Bowler Hat, Cane and Monocle", scene(
        ([cane, crook, ferrule, collar_], [cane, crook]),
        ([brim, curl], [brim]),
        ([crown], [crown_cv]),
        ([band_lo, band_hi], [chain(band_lo, band_hi[::-1], [band_lo[0]])]),
        (bow, bow),
        ([mchain], []),
        (mono, [mono[0]])))


@design("vintage_clawfoot_tub", T)
def clawfoot_tub(rng):
    rim = smooth([(-2.9, 0.75), (-2.5, 0.25), (2.7, 0.25), (2.9, 0.5), (2.6, 0.55), (-2.4, 0.55)], 2)
    body = chain(cubic((-2.55, 0.3), (-2.4, -1.3), (-1.8, -1.5), (-1.2, -1.5), 20), [(1.2, -1.5)], cubic((1.2, -1.5), (2.0, -1.5), (2.5, -1.0), (2.6, 0.3), 20))
    body_cv = body + [body[0]]

    def claw(x):
        leg = chain(quad((x - 0.35, -1.2), (x - 0.15, -1.8), (x - 0.3, -2.2), 10),
                    [(x + 0.3, -2.2)], quad((x + 0.3, -2.2), (x + 0.15, -1.8), (x + 0.35, -1.2), 10))
        ball = circle(x, -2.45, 0.28, 20)
        toes = [chain(arc(x + dx, -2.3, 0.12, math.pi, 2 * math.pi, 8)) for dx in (-0.2, 0.0, 0.2)]
        return [leg], [ball] + toes, leg + [leg[0]]
    feet = [claw(-1.7), claw(1.7)]
    tap_pipe = tube(chain([(2.2, 0.55), (2.2, 1.5)], arc(1.85, 1.5, 0.35, 0, math.pi, 12), [(1.5, 1.2)]), 0.18)
    handles = [poly((2.0, 1.0), (2.4, 1.0), closed=False), circle(1.95, 1.0, 0.08, 8), circle(2.45, 1.0, 0.08, 8)]
    bub = [circle(x, y, r, 18) for x, y, r in ((-1.8, 0.85, 0.35), (-1.25, 1.05, 0.42), (-0.6, 0.85, 0.32), (-0.05, 1.1, 0.38),
                                            (0.55, 0.85, 0.3), (-1.0, 1.65, 0.22), (0.3, 1.7, 0.18), (-0.3, 2.1, 0.13))]
    floor = seg((-3.0, -2.75), (3.0, -2.75))
    layers = [(bub, bub), ([tap_pipe] + handles, [tap_pipe])]
    for leg, ball, cv in feet:
        layers.append((leg, [cv]))
    layers += [([body], [body_cv]), ([rim], [rim])]
    for leg, ball, cv in feet:
        layers.append((ball, ball[:1]))
    return make("Clawfoot Bathtub", scene(*layers) + [floor])


@design("vintage_pot_belly_stove", T)
def pot_belly_stove(rng):
    belly = ellipse(0, -0.4, 1.45, 1.45, 90)
    bands = [quad((-1.38, 0.05), (0, -0.25), (1.38, 0.05), 16)]
    door = chain([(-0.55, -1.2), (-0.55, -0.35)], arc(0, -0.35, 0.55, math.pi, 0, 16), [(0.55, -1.2), (-0.55, -1.2)])
    slots = [seg((x, -1.05), (x, -0.4)) for x in (-0.3, 0.0, 0.3)]
    handle = [seg((0.55, -0.7), (0.85, -0.7)), circle(0.92, -0.7, 0.08, 8)]
    flames = keep([chain(quad((x - 0.12, -1.2), (x - 0.15, -0.95), (x, -0.75), 6), quad((x, -0.75), (x + 0.15, -0.95), (x + 0.12, -1.2), 6)) for x in (-0.15, 0.15)], door)
    ash = rrect(-1.2, -2.2, 1.2, -1.75, 0.1)
    ash_door = rect(-0.5, -2.1, 0.5, -1.85)
    legs = [tube(cubic((-0.9, -2.2), (-1.0, -2.6), (-1.5, -2.6), (-1.6, -2.95), 12), 0.16), tube(cubic((0.9, -2.2), (1.0, -2.6), (1.5, -2.6), (1.6, -2.95), 12), 0.16)]
    collar = rect(-1.0, 0.9, 1.0, 1.15)
    tp = poly((-1.25, 1.15), (1.25, 1.15), (1.0, 1.4), (-1.0, 1.4))
    crown = chain(arc(0, 1.4, 0.75, 0, math.pi, 20))
    pipe = tube([(0, 1.9), (0, 3.6)], 0.6)
    damper = [seg((-0.3, 2.7), (0.3, 2.7)), seg((0.3, 2.7), (0.55, 2.7)), circle(0.62, 2.7, 0.08, 8)]
    joint = rect(-0.36, 2.15, 0.36, 2.3)
    return make("Pot-Belly Stove", scene(
        ([pipe], [pipe]),
        ([joint] + damper, [joint]),
        ([crown], [crown + [crown[0]]]),
        ([tp], [tp]),
        ([collar], [collar]),
        (legs, legs),
        ([ash, ash_door], [ash]),
        ([belly, door] + bands + slots + handle + flames, [belly])))
