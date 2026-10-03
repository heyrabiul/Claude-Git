"""Music niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "music"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ------------------------------------------------------------- helpers -----

def place(pts, x, y, ang=0.0, s=1.0):
    """Rotate (radians) and scale a local drawing about its origin, then move it to (x, y)."""
    return transform(pts, x, y, s, ang)


def orient(parts, dx=0.0, dy=0.0, ang=0.0, s=1.0):
    """Shift every stroke by (dx, dy), then rotate/scale the lot about the origin."""
    return [transform([(x + dx, y + dy) for x, y in p], 0, 0, s, ang) for p in parts]


def smooth(pts, closed=False, n=8):
    """Catmull-Rom spline through the given points."""
    P = list(pts)
    P = [P[-1]] + P + [P[0], P[1]] if closed else [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * (2 * p1[j] + (p2[j] - p0[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (3 * p1[j] - p0[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    out.append(P[-2])
    return out


def mirrored(right):
    """Closed outline from a right-hand half listed bottom -> top (x >= 0)."""
    return chain(right, [(-x, y) for x, y in reversed(right)])


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


def in_poly(p, pts):
    """Even-odd point-in-polygon test."""
    x, y = p
    inside = False
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


def note(x, y, s=1.0, flag=True, hollow=False):
    """Single note: (strokes, hints).  Head at (x, y), stem up."""
    head = ellipse(x, y, 0.27 * s, 0.19 * s, 20, rot=0.35)
    sx, top = x + 0.24 * s, y + 1.35 * s
    strokes = [[(sx, y + 0.06 * s), (sx, top)]]
    if flag:
        strokes.append(cubic((sx, top), (sx + 0.05 * s, top - 0.35 * s), (sx + 0.6 * s, top - 0.45 * s), (sx + 0.35 * s, top - 1.0 * s), 14))
    if hollow:
        return strokes + [head], []
    return strokes, [head]


def beamed(x, y, s=1.0, dx=0.9, rise=0.25):
    """Two beamed eighth notes."""
    h1 = ellipse(x, y, 0.27 * s, 0.19 * s, 20, rot=0.35)
    h2 = ellipse(x + dx * s, y + rise * s, 0.27 * s, 0.19 * s, 20, rot=0.35)
    s1, s2 = x + 0.24 * s, x + dx * s + 0.24 * s
    t1, t2 = y + 1.35 * s, y + rise * s + 1.35 * s
    beam = poly((s1, t1), (s2, t2), (s2, t2 - 0.22 * s), (s1, t1 - 0.22 * s))
    return [[(s1, y + 0.06 * s), (s1, t1)], [(s2, y + rise * s + 0.06 * s), (s2, t2)], beam], [h1, h2]


def notes(spec):
    """spec: list of (kind, x, y, s) -> strokes, hints."""
    st, hi = [], []
    for kind, x, y, s in spec:
        a, b = beamed(x, y, s) if kind == "b" else note(x, y, s, flag=(kind == "e"), hollow=(kind == "h"))
        st += a
        hi += b
    return st, hi


def keyboard(x0, x1, y0, y1, n, black=0.6, start=0):
    """Piano keys: n white keys from x0 to x1, black keys in the usual 2+3 groups."""
    w = (x1 - x0) / n
    yb = y1 - (y1 - y0) * black
    out = [rect(x0, y0, x1, y1)]
    for k in range(1, n):
        has_black = (k - 1 + start) % 7 in (0, 1, 3, 4, 5)
        out.append([(x0 + w * k, y0), (x0 + w * k, yb if has_black else y1)])
        if has_black:
            bx = x0 + w * k
            out.append([(bx - 0.32 * w, y1), (bx - 0.32 * w, yb), (bx + 0.32 * w, yb), (bx + 0.32 * w, y1)])
    return out


def frets(x, y0, y1, w, first=0.45, k=0.93):
    """Fret lines across a neck running upward from y0 (body) to y1 (nut)."""
    out, y, gap = [], y1, first
    while y - gap > y0 + 0.15:
        y -= gap
        out.append([(x - w / 2, y), (x + w / 2, y)])
        gap *= k
    return out


def peg(x, y, side, L=0.35):
    """Tuning peg sticking out sideways from a headstock."""
    return [[(x, y), (x + side * L * 0.4, y)], ellipse(x + side * L * 0.75, y, L * 0.38, 0.13, 12)]


def steam(x, y, h=1.0, amp=0.15, n=24):
    return [(x + amp * math.sin(TAU * 1.25 * i / n), y + h * i / n) for i in range(n + 1)]


# ------------------------------------------------------------- pianos ------

@design("music_grand_piano", T)
def grand_piano(rng):
    case = rect(-2.4, -0.7, 2.7, 0.0)
    rim = [[(-2.4, -0.15), (2.7, -0.15)]]
    lid = chain([(-2.1, 0.0)], cubic((-2.1, 0.0), (-1.0, 0.6), (1.0, 2.4), (2.4, 2.8), 30), [(2.7, 2.6)], [(2.7, 0.0)])
    lid_edge = cubic((-1.8, 0.05), (-0.8, 0.55), (1.0, 2.15), (2.4, 2.55), 30)
    prop = [[(1.2, 0.0), (1.35, 1.75)]]
    keys = [rect(-3.1, -0.5, -2.4, -0.15), [(-3.1, -0.3), (-2.4, -0.3)]]
    stand = [poly((-2.35, 0.0), (-2.6, 0.9), (-1.6, 0.9), (-1.75, 0.0), closed=False), [(-2.55, 0.75), (-1.65, 0.75)]]
    legs = []
    for x in (-2.0, 2.3):
        legs.append(poly((x - 0.25, -0.7), (x - 0.12, -2.6), (x + 0.12, -2.6), (x + 0.25, -0.7), closed=False))
        legs.append(circle(x, -2.75, 0.15, 12))
    lyre = [poly((-0.2, -0.7), (-0.35, -2.2), (0.35, -2.2), (0.2, -0.7), closed=False), rrect(-0.6, -2.45, 0.6, -2.2, 0.08),
            [(0.0, -0.9), (0.0, -2.0)]]
    pedals = [[(-0.3, -2.45), (-0.4, -2.75)], [(0.0, -2.45), (0.0, -2.75)], [(0.3, -2.45), (0.4, -2.75)]]
    bench = [rrect(-3.4, -1.2, -2.0, -0.95, 0.08), [(-3.2, -1.2), (-3.25, -2.7)], [(-2.2, -1.2), (-2.15, -2.7)]]
    st, hi = notes([("e", 0.2, 2.2, 0.6), ("b", -1.2, 1.4, 0.55)])
    return make("Grand Piano with Open Lid", [case, lid, lid_edge] + rim + prop + keys + stand + legs + lyre + pedals + bench + st, hi)


@design("music_upright_piano", T)
def upright_piano(rng):
    body = rect(-2.6, -2.8, 2.6, 2.2)
    top = rrect(-2.75, 2.2, 2.75, 2.5, 0.08)
    panel = rrect(-2.2, 0.6, 2.2, 1.9, 0.15)
    inner = rrect(-1.9, 0.8, 1.9, 1.7, 0.1)
    sheet = [poly((-0.9, 1.0), (0.9, 1.0), (0.9, 2.0), (-0.9, 2.0))]
    staff = [[(-0.75, y), (0.75, y)] for y in (1.25, 1.45, 1.65, 1.85)]
    shelf = rect(-2.75, 0.2, 2.75, 0.6)
    keys = keyboard(-2.4, 2.4, -0.4, 0.2, 14, 0.55)
    lower = rrect(-2.2, -2.2, 2.2, -0.7, 0.15)
    lower_in = rrect(-1.9, -2.0, 1.9, -0.9, 0.1)
    pedals = [ellipse(x, -2.55, 0.18, 0.09, 12) for x in (-0.45, 0.0, 0.45)]
    cand = [rrect(-2.5, 2.5, -2.0, 2.6, 0.03), rect(-2.35, 2.6, -2.15, 3.2), lens((-2.25, 3.25), (-2.25, 3.65), 0.35, 8)]
    vase = [poly((1.7, 2.5), (2.3, 2.5), (2.4, 3.0), (2.2, 3.2), (1.8, 3.2), (1.6, 3.0)), circle(1.75, 3.55, 0.25, 14), circle(2.25, 3.5, 0.22, 14)]
    return make("Upright Piano", [body, top, panel, inner, shelf, lower, lower_in] + sheet + staff + keys + pedals + cand + vase)


@design("music_piano_keys", T)
def piano_keys(rng):
    ang = -0.18
    keys = [place(p, 0, -0.6, ang) for p in keyboard(-3.2, 3.2, -1.2, 1.2, 9, 0.62, start=0)]
    st, hi = notes([("e", -2.3, 1.6, 0.8), ("b", -0.6, 1.9, 0.75), ("e", 1.6, 2.0, 0.8), ("h", 2.6, 1.3, 0.6)])
    swirl = [cubic((-3.0, 1.1), (-1.0, 3.6), (0.8, 0.8), (3.2, 2.6), 40)]
    return make("Piano Keys and Flying Notes", keys + st + swirl, hi)


# ------------------------------------------------------------- strings -----

def guitar_outline(bw=1.3, ww=0.82, uw=1.0, scale=1.0):
    r = [(0.0, -2.0), (bw * 0.73, -1.8), (bw, -1.0), (bw * 0.88, -0.2), (ww, 0.35), (uw * 0.95, 0.9), (uw, 1.4), (uw * 0.75, 1.85), (0.3, 2.0), (0.0, 2.02)]
    full = r + [(-x, y) for x, y in reversed(r[1:-1])]
    return [(x * scale, y * scale) for x, y in smooth(full, closed=True, n=8)]


@design("music_acoustic_guitar", T)
def acoustic_guitar(rng):
    body = guitar_outline()
    hole = [circle(0, 1.05, 0.42, 30), circle(0, 1.05, 0.56, 34)]
    bridge = [rrect(-0.6, -1.2, 0.6, -0.92, 0.1), [(-0.4, -0.85), (0.4, -0.85)]]
    guard = chain(arc(0, 1.05, 0.62, math.radians(-80), math.radians(10), 10), quad((0.61, 1.16), (1.0, 0.6), (0.4, 0.2), 10))
    neck = rect(-0.25, 2.0, 0.25, 5.0)
    fr = frets(0, 2.0, 5.0, 0.5, 0.42, 0.93)
    head = poly((-0.25, 5.0), (-0.42, 6.1), (0.0, 6.25), (0.42, 6.1), (0.25, 5.0), closed=False)
    pegs = [s for y in (5.35, 5.65, 5.95) for s in peg(-0.36 + 0.03 * (y - 5.0), y, -1) + peg(0.36 - 0.03 * (y - 5.0), y, 1)]
    strings = [[(x, -0.9), (x * 0.8, 5.0)] for x in (-0.12, 0.12)]
    parts = [body, neck, head, guard] + hole + bridge + fr + pegs + strings
    return make("Acoustic Guitar", orient(parts, 0, -2.1, -0.6))


def strat_body():
    pts = [(0, -2.0), (1.1, -1.85), (1.65, -1.2), (1.55, -0.4), (1.25, 0.15), (1.45, 0.8), (1.6, 1.5), (1.35, 1.75), (0.95, 1.4), (0.5, 0.9),
           (-0.5, 0.9), (-0.8, 1.5), (-1.0, 2.25), (-1.3, 2.4), (-1.55, 2.0), (-1.45, 1.2), (-1.35, 0.4), (-1.7, -0.4), (-1.75, -1.2), (-1.2, -1.85)]
    return smooth(pts, closed=True, n=8)


@design("music_electric_guitar", T)
def electric_guitar(rng):
    body = strat_body()
    guard = smooth([(0.0, -1.3), (0.9, -1.2), (1.1, -0.6), (0.9, 0.3), (0.45, 0.75), (-0.45, 0.75), (-0.9, 1.0), (-1.05, 0.4), (-0.6, -0.6), (-0.6, -1.1)], closed=True)
    pickups = [rrect(-0.45, y - 0.12, 0.45, y + 0.12, 0.08) for y in (-0.55, 0.0, 0.5)]
    bridge = [rrect(-0.5, -1.15, 0.5, -0.85, 0.06)]
    knobs = [circle(1.05, -1.0, 0.16, 12), circle(1.3, -0.6, 0.16, 12), circle(0.75, -1.35, 0.16, 12)]
    jack = [circle(1.35, -1.45, 0.12, 10)]
    neck = rect(-0.25, 0.9, 0.25, 4.6)
    fr = frets(0, 0.9, 4.6, 0.5, 0.4, 0.94)
    head = smooth([(-0.25, 4.6), (-0.4, 5.3), (-0.2, 6.1), (0.15, 6.25), (0.45, 6.0), (0.5, 5.4), (0.25, 4.9), (0.25, 4.6)], n=6)
    strings = [[(x, -1.0), (x * 0.8, 4.6)] for x in (-0.13, 0.13)]
    parts = [body, guard, neck, head] + pickups + bridge + knobs + jack + fr + strings
    hints = [place([(-0.2 + 0.07 * k, 5.05 + 0.18 * k)], 0, 0)[0] for k in range(6)]
    hints = [eye(*transform([(x, y - 2.0)], 0, 0, 1, -0.7)[0], 0.07) for x, y in hints]
    return make("Electric Guitar", orient(parts, 0, -2.0, -0.7), hints)


@design("music_bass_guitar", T)
def bass_guitar(rng):
    pts = [(-2.4, 0.0), (-2.3, 0.8), (-1.7, 1.2), (-1.1, 1.0), (-0.7, 1.15), (-0.2, 1.6), (0.1, 1.5), (-0.1, 0.9), (0.2, 0.3), (0.2, -0.3),
           (-0.3, -0.85), (-0.9, -1.15), (-1.7, -1.2), (-2.3, -0.8)]
    body = smooth(pts, closed=True)
    guard = smooth([(-1.9, 0.6), (-1.2, 0.85), (-0.5, 0.9), (0.0, 0.5), (-0.4, -0.3), (-1.2, -0.65), (-1.9, -0.5)], closed=True)
    pickup = [rrect(-1.25, 0.05, -0.95, 0.5, 0.08), rrect(-1.05, -0.45, -0.75, 0.0, 0.08)]
    bridge = [rrect(-2.05, -0.4, -1.75, 0.4, 0.06)]
    knobs = [circle(-1.6, -0.85, 0.15, 12), circle(-1.15, -0.95, 0.15, 12)]
    neck = rect(0.15, -0.22, 4.2, 0.22)
    fr = [[(x, -0.22), (x, 0.22)] for x in [4.2 - sum(0.42 * 0.95 ** j for j in range(k + 1)) for k in range(9)]]
    head = smooth([(4.2, -0.22), (4.25, -0.4), (5.6, -0.35), (5.75, 0.0), (5.6, 0.35), (4.6, 0.35), (4.2, 0.22)], n=6)
    keys = []
    for k in range(4):
        x = 4.5 + 0.33 * k
        keys += [[(x, 0.35), (x, 0.6)], ellipse(x, 0.82, 0.13, 0.22, 14)]
    strings = [[(-1.9, y), (4.2, y * 0.9)] for y in (-0.1, 0.1)]
    parts = [body, guard, neck, head] + pickup + bridge + knobs + fr + keys + strings
    return make("Bass Guitar", orient(parts, -1.7, 0.0, 0.32))


def violin_parts():
    half = chain(cubic((0.0, 2.2), (0.75, 2.2), (1.15, 1.5), (0.95, 0.75), 16), cubic((0.95, 0.75), (0.55, 0.6), (0.5, -0.2), (0.95, -0.45), 14),
                 cubic((0.95, -0.45), (1.45, -0.9), (1.35, -2.4), (0.0, -2.4), 18))
    body = chain(half, [(-x, y) for x, y in reversed(half)])
    fhole = cubic((0.45, 0.6), (0.2, 0.25), (0.7, -0.3), (0.42, -0.7), 14)
    board = poly((-0.15, 3.6), (0.15, 3.6), (0.28, 0.1), (-0.28, 0.1))
    box = rect(-0.17, 3.6, 0.17, 4.35)
    scroll = spiral(0.0, 4.6, 0.04, 0.3, 1.6, 50, rot=-math.pi / 2)
    pegs = [[(-0.17, y), (-0.45, y + 0.05)] for y in (3.8, 4.15)] + [[(0.17, y), (0.45, y + 0.05)] for y in (3.95, 4.3)]
    bridge = poly((-0.42, -0.4), (0.42, -0.4), (0.32, -0.15), (-0.32, -0.15))
    tail = poly((-0.3, -0.9), (0.3, -0.9), (0.17, -2.05), (-0.17, -2.05))
    chin = ellipse(-0.6, -2.0, 0.42, 0.22, 20)
    return [body, fhole, mirror_x(fhole), board, box, scroll, bridge, tail, chin] + pegs


@design("music_violin", T)
def violin(rng):
    parts = orient(violin_parts(), 0, -1.0, -0.55)
    bow = [[(-2.9, -2.0), (2.6, 2.3)], [(-2.7, -2.25), (2.65, 1.95)], rrect(-0.2, -0.25, 0.4, 0.25, 0.08), [(2.6, 2.3), (2.75, 2.35), (2.65, 1.95)]]
    bow = [bow[0], bow[1], place(rrect(-0.35, -0.2, 0.35, 0.2, 0.08), -2.8, -2.12, 0.66), bow[3]]
    return make("Violin and Bow", parts + bow)


@design("music_cello", T)
def cello(rng):
    vp = violin_parts()
    vp = [[(x * 1.25, y) for x, y in p] for p in vp[:8] + vp[9:]]
    parts = orient(vp, 0, -0.6, 0.0)
    pin = [[(0, -3.0), (0, -3.9)]]
    floor = [[(-2.6, -3.9), (2.6, -3.9)]]
    bow = [[(-2.4, -3.2), (2.2, 3.4)], [(-2.2, -3.32), (2.32, 3.3)], place(rrect(-0.35, -0.2, 0.35, 0.2, 0.08), -2.3, -3.25, 0.96)]
    st, hi = notes([("e", -2.6, 2.0, 0.55), ("b", 1.6, -2.2, 0.5)])
    return make("Cello on Its Endpin", parts + pin + floor + bow + st, hi)


@design("music_harp", T)
def harp(rng):
    column = rrect(-1.65, -2.4, -1.25, 2.5, 0.12)
    crown = [rrect(-1.8, 2.5, -1.1, 2.75, 0.06), poly((-1.75, 2.75), (-1.6, 3.1), (-1.45, 2.85), (-1.3, 3.1), (-1.15, 2.75), closed=False)]
    neck_c = cubic((-1.25, 2.4), (-0.2, 1.6), (0.9, 3.3), (2.0, 2.25), 40)
    neck = tube(neck_c, 0.35)
    box_c = [(-1.1 + 3.0 * t, -2.3 + 4.4 * t) for t in [i / 30 for i in range(31)]]
    box = tube(box_c, lambda t: 0.9 - 0.55 * t)
    base = [rrect(-2.0, -2.9, 0.4, -2.4, 0.12), rect(-1.8, -3.1, -1.4, -2.9), rect(-0.2, -3.1, 0.2, -2.9)]
    strings = []
    for k in range(13):
        x = -1.0 + 0.24 * k
        ytop = min((p for p in neck_c), key=lambda p: abs(p[0] - x))[1] - 0.17
        ybot = -2.3 + (x + 1.1) * (4.4 / 3.0) + 0.15
        if ytop - ybot > 0.3:
            strings.append([(x, ytop), (x, ybot)])
    return make("Concert Harp", [column, neck, box] + crown + base + strings)


# ------------------------------------------------------------- brass/wind --

@design("music_saxophone", T)
def saxophone(rng):
    c = chain(cubic((-1.3, 3.0), (-0.6, 3.2), (-0.2, 2.9), (-0.15, 2.3), 16), [(-0.25 - 0.1 * i / 10, 2.3 - 3.8 * i / 10) for i in range(1, 11)],
              arc(0.45, -1.5, 0.8, math.pi, 2 * math.pi, 20), [(1.25 + 0.1 * i / 10, -1.5 + 2.0 * i / 10) for i in range(1, 11)])
    w = lambda t: 0.16 + 0.6 * min(1.0, t / 0.6) if t < 0.85 else 0.76 + 2.8 * (t - 0.85)
    body = tube(c, w, cap=False)
    bell = ellipse(1.35, 0.55, 0.65, 0.18, 30)
    mouth = [poly((-1.3, 2.93), (-1.75, 2.95), (-1.75, 3.1), (-1.3, 3.1), closed=False)]
    keys = [circle(x, y, 0.17, 12) for x, y in [(-0.27, 1.6), (-0.3, 1.1), (-0.33, 0.6), (-0.36, 0.0), (-0.38, -0.5)]]
    rods = [[(0.1, 1.9), (0.1, -0.9)], [(1.05, -1.1), (1.15, 0.1)]]
    st, hi = notes([("e", 1.9, 2.0, 0.6), ("b", 2.0, -2.3, 0.5), ("e", -2.4, 0.3, 0.55)])
    return make("Saxophone", [body, bell] + mouth + keys + rods + st, hi)


@design("music_trumpet", T)
def trumpet(rng):
    bell = chain([(0.2, 0.42)], [(1.0, 0.42)], cubic((1.0, 0.42), (2.0, 0.5), (2.6, 0.8), (2.9, 1.3), 20))
    bell_b = chain([(0.2, 0.12)], [(1.0, 0.12)], cubic((1.0, 0.12), (2.0, 0.05), (2.6, -0.25), (2.9, -0.7), 20))
    rim = ellipse(2.9, 0.3, 0.15, 1.0, 30)
    valves = []
    for x in (-0.8, -0.3, 0.2):
        valves += [rect(x - 0.17, -0.8, x + 0.17, 0.75), [(x, 0.75), (x, 1.15)], rrect(x - 0.25, 1.15, x + 0.25, 1.32, 0.06), rect(x - 0.2, -1.0, x + 0.2, -0.8)]
    lead = [[(-3.0, 0.42), (-0.97, 0.42)], [(-3.0, 0.12), (-0.97, 0.12)], poly((-3.0, 0.42), (-3.3, 0.55), (-3.3, 0.0), (-3.0, 0.12), closed=False)]
    loop = [rrect(-2.4, -1.4, -0.97, -0.3, 0.45), rrect(-2.15, -1.15, -0.97, -0.55, 0.25)]
    tune = chain([(0.37, -0.5)], [(1.2, -0.5)], arc(1.2, -0.85, 0.35, math.pi / 2, -math.pi / 2, 10), [(0.37, -1.2)])
    tune_in = chain([(0.37, -0.7)], [(1.2, -0.7)], arc(1.2, -0.85, 0.15, math.pi / 2, -math.pi / 2, 8), [(0.37, -1.0)])
    st, hi = notes([("e", -1.8, 1.2, 0.55), ("b", 0.8, 1.6, 0.5)])
    return make("Shining Trumpet", [bell, bell_b, rim, tune, tune_in] + valves + lead + loop + st, hi)


@design("music_trombone", T)
def trombone(rng):
    bell_t = chain([(-2.9, 2.0)], cubic((-2.9, 2.0), (-2.1, 1.2), (-1.2, 1.15), (0.0, 1.15), 20), [(1.6, 1.15)])
    bell_b = chain([(-2.9, 0.2)], cubic((-2.9, 0.2), (-2.1, 0.95), (-1.2, 0.95), (0.0, 0.95), 20), [(1.6, 0.95)])
    rim = ellipse(-2.9, 1.1, 0.15, 0.9, 30)
    crook = [arc(1.6, 0.6, 0.55, math.pi / 2, -math.pi / 2, 14), arc(1.6, 0.6, 0.35, math.pi / 2, -math.pi / 2, 12)]
    back = [[(1.6, 0.25), (0.8, 0.25)], [(1.6, 0.05), (0.8, 0.05)]]
    slide = [[(0.8, 0.25), (-3.0, 0.25)], [(0.8, 0.05), (-3.0, 0.05)], [(1.4, -0.45), (-3.0, -0.45)], [(1.4, -0.65), (-3.0, -0.65)]]
    u = [arc(-3.0, -0.2, 0.45, math.pi / 2, 1.5 * math.pi, 12), arc(-3.0, -0.2, 0.25, math.pi / 2, 1.5 * math.pi, 10)]
    mouth = [poly((1.4, -0.45), (1.8, -0.35), (1.8, -0.75), (1.4, -0.65), closed=False)]
    braces = [[(-0.2, 0.05), (-0.2, -0.45)], [(0.6, 0.05), (0.6, -0.45)], [(-1.9, 0.05), (-1.9, -0.45)], [(-0.6, 0.95), (-0.6, 0.25)]]
    st, hi = notes([("e", -0.6, 1.7, 0.55), ("b", 0.6, 1.9, 0.5)])
    return make("Trombone with Long Slide", [bell_t, bell_b, rim] + crook + back + slide + u + mouth + braces + st, hi)


@design("music_french_horn", T)
def french_horn(rng):
    coil = [circle(-0.6, 0.3, 1.8, 120), circle(-0.6, 0.3, 1.5, 110), circle(-0.6, 0.3, 1.0, 80), circle(-0.6, 0.3, 0.75, 60)]
    c = cubic((0.55, -1.05), (1.2, -1.5), (1.8, -1.8), (2.4, -2.6), 24)
    bell = tube(c, lambda t: 0.3 + 1.9 * t ** 2.5, cap=False)
    ang = math.atan2(c[-1][1] - c[-2][1], c[-1][0] - c[-2][0])
    rim = ellipse(c[-1][0], c[-1][1], 0.3, 1.1, 40, rot=ang)
    coil = [s for k in coil for s in clip_out(k, lambda p: in_poly(p, bell))]
    valves = [circle(-0.6 + 0.5 * k, 1.55, 0.22, 14) for k in (-1, 0, 1)]
    levers = [[(-1.1 + 0.5 * k, 1.77), (-1.4 + 0.45 * k, 2.6)] for k in range(3)]
    lead = [[(-2.15, 1.2), (-3.0, 2.3)], [(-1.95, 1.4), (-2.8, 2.5)], poly((-3.0, 2.3), (-3.3, 2.45), (-3.1, 2.75), (-2.8, 2.5), closed=False)]
    return make("French Horn", coil + [bell, rim] + valves + levers + lead)


@design("music_tuba", T)
def tuba(rng):
    rim = ellipse(0.5, 2.7, 1.5, 0.35, 60)
    bell = [chain([(-1.0, 2.7)], cubic((-1.0, 2.7), (-0.2, 2.2), (0.0, 1.5), (0.0, 0.6), 20)), chain([(2.0, 2.7)], cubic((2.0, 2.7), (1.2, 2.2), (1.0, 1.5), (1.0, 0.6), 20))]
    body = [ellipse(0.0, -0.9, 1.6, 1.9, 90), ellipse(0.0, -0.9, 1.2, 1.5, 80)]
    body = [s for b in body for s in clip_out(b, lambda p: 0.0 < p[0] < 1.0 and p[1] > -0.4)]
    bell.append([(0.0, 0.6), (0.0, 0.3)])
    bell.append([(1.0, 0.6), (1.0, 0.75)])
    valves = []
    for k in range(4):
        x = -1.2 + 0.38 * k
        valves += [rect(x - 0.15, -0.6, x + 0.15, 0.6), [(x, 0.6), (x, 0.95)], rrect(x - 0.2, 0.95, x + 0.2, 1.08, 0.04)]
    pipe = [[(-1.6, -0.2), (-2.7, 0.6)], [(-1.6, 0.05), (-2.6, 0.8)], poly((-2.7, 0.6), (-3.0, 0.75), (-2.85, 1.0), (-2.6, 0.8), closed=False)]
    tube_ = [rrect(-0.6, -2.95, 0.6, -2.6, 0.15)]
    return make("Big Brass Tuba", [rim] + bell + body + valves + pipe + tube_)


@design("music_clarinet", T)
def clarinet(rng):
    half = [(0.55, -2.6), (0.5, -2.3), (0.3, -1.9), (0.22, -1.7), (0.22, 0.3), (0.2, 0.3), (0.2, 2.2), (0.26, 2.2), (0.26, 2.65), (0.18, 2.65), (0.16, 3.0), (0.08, 3.3), (0.0, 3.35)]
    body = mirrored(half)
    rings = [[(-w, y), (w, y)] for y, w in [(-1.7, 0.22), (0.3, 0.22), (2.2, 0.2), (2.65, 0.26)]]
    lig = [[(-0.17, 2.85), (0.17, 2.85)]]
    holes = [eye(0.0, y, 0.07) for y in (1.8, 1.4, 1.0, -0.2, -0.6, -1.0)]
    rods = [[(0.12, 2.0), (0.12, 0.4)], [(0.12, 0.15), (0.12, -1.6)]]
    keys = [ellipse(-0.05, 0.6, 0.12, 0.22, 10), ellipse(-0.05, -1.35, 0.12, 0.22, 10)]
    parts = orient([body] + rings + lig + rods + keys, 0, -0.35, -0.5)
    hi = [orient([h], 0, -0.35, -0.5)[0] for h in holes]
    st, hi2 = notes([("e", -2.4, 0.2, 0.6), ("b", 0.9, 1.6, 0.55), ("e", 1.4, -2.0, 0.55)])
    return make("Clarinet", parts + st, hi + hi2)


@design("music_flute", T)
def flute(rng):
    body = rrect(-3.0, -0.2, 3.0, 0.2, 0.1)
    head = [[(-2.0, -0.2), (-2.0, 0.2)], [(-1.3, -0.2), (-1.3, 0.2)], [(2.0, -0.2), (2.0, 0.2)]]
    lip = ellipse(-2.5, 0.25, 0.25, 0.14, 16)
    keys = [circle(x, 0.0, 0.16, 12) for x in (-0.9, -0.45, 0.0, 0.6, 1.05, 1.5)]
    rod = [[(-1.1, -0.28), (1.8, -0.28)]]
    flute_parts = orient([body, lip] + head + keys + rod, 0, 0, 0.45)
    staff = [[(x, 0.7 * math.sin(x * 0.9) - 1.4 + 0.25 * k) for x in [-3.2 + 6.4 * i / 80 for i in range(81)]] for k in range(5)]
    st, hi = notes([("e", -2.0, -1.4 + 0.7 * math.sin(-2.0 * 0.9) + 0.4, 0.5), ("b", -0.6, -1.4 + 0.7 * math.sin(-0.6 * 0.9) + 0.3, 0.5),
                    ("e", 1.6, -1.4 + 0.7 * math.sin(1.6 * 0.9) + 0.6, 0.5)])
    return make("Silver Flute over a Melody", flute_parts + staff + st, hi)


# ------------------------------------------------------------- percussion --

def drum(cx, top, rx, ry, h, lugs=4):
    """Cylinder drum seen from the front: top ellipse, sides, bottom curve, lugs."""
    out = [ellipse(cx, top, rx, ry, 60), chain([(cx - rx, top)], [(cx - rx, top - h)],
                                               [(cx + rx * math.cos(t), top - h + ry * math.sin(t)) for t in [math.pi + math.pi * i / 30 for i in range(31)]], [(cx + rx, top)])]
    out.append([(cx + rx * math.cos(t), top - 0.18 + ry * math.sin(t)) for t in [math.pi + math.pi * i / 30 for i in range(31)]])
    for k in range(lugs):
        t = math.pi + math.pi * (k + 0.5) / lugs
        x = cx + rx * math.cos(t)
        y = top - h / 2 + ry * math.sin(t)
        out.append(rrect(x - 0.08, y - 0.18, x + 0.08, y + 0.18, 0.05))
    return out


@design("music_drum_kit", T)
def drum_kit(rng):
    bass = [circle(0, -1.3, 1.35, 90), circle(0, -1.3, 1.12, 80), star(0, -1.3, 0.55, 5, 0.45)]
    spurs = [[(-1.1, -2.0), (-1.6, -2.75)], [(1.1, -2.0), (1.6, -2.75)]]
    toms = drum(-0.65, 0.65, 0.55, 0.18, 0.55, 3) + drum(0.65, 0.65, 0.55, 0.18, 0.55, 3)
    toms = [s for t in toms for s in clip_out(t, lambda p: p[0] ** 2 + (p[1] + 1.3) ** 2 < 1.35 ** 2)]
    floor = drum(2.15, -0.5, 0.75, 0.22, 1.5, 3) + [[(1.6, -2.1), (1.5, -2.85)], [(2.7, -2.1), (2.8, -2.85)]]
    floor = [s for t in floor for s in clip_out(t, lambda p: p[0] ** 2 + (p[1] + 1.3) ** 2 < 1.35 ** 2)]
    snare = drum(-2.05, -0.55, 0.7, 0.2, 0.5, 3) + [[(-2.05, -1.25), (-2.05, -2.2)], [(-2.05, -2.2), (-2.6, -2.85)], [(-2.05, -2.2), (-1.5, -2.85)]]
    snare = [s for t in snare for s in clip_out(t, lambda p: p[0] ** 2 + (p[1] + 1.3) ** 2 < 1.35 ** 2)]
    hihat = [[(-2.9, 0.75), (-2.9, -0.35)], ellipse(-2.9, 0.85, 0.75, 0.1, 30), ellipse(-2.9, 1.05, 0.75, 0.1, 30), [(-2.9, 1.15), (-2.9, 1.35)]]
    crash = [ellipse(2.3, 1.9, 0.95, 0.15, 36, rot=0.15), circle(2.3, 2.0, 0.12, 10), [(2.3, 1.75), (2.3, -0.25)]]
    sticks = [[(-0.2, 1.3), (0.9, 2.6)], [(0.3, 1.3), (-0.8, 2.6)]]
    return make("Rock Drum Kit", bass + spurs + toms + floor + snare + hihat + crash + sticks)


@design("music_snare_drum", T)
def snare_drum(rng):
    top = ellipse(0, 0.6, 2.4, 0.7, 120)
    hoop = [(2.4 * math.cos(t), 0.35 + 0.7 * math.sin(t)) for t in [math.pi + math.pi * i / 60 for i in range(61)]]
    side = chain([(-2.4, 0.6)], [(-2.4, -1.4)], [(2.4 * math.cos(t), -1.4 + 0.7 * math.sin(t)) for t in [math.pi + math.pi * i / 60 for i in range(61)]], [(2.4, 0.6)])
    hoop2 = [(2.4 * math.cos(t), -1.15 + 0.7 * math.sin(t)) for t in [math.pi + math.pi * i / 60 for i in range(61)]]
    lugs = []
    for k in range(5):
        t = math.pi + math.pi * (k + 0.5) / 5
        x, yy = 2.4 * math.cos(t), 0.7 * math.sin(t)
        lugs += [rrect(x - 0.13, -0.75 + yy, x + 0.13, -0.15 + yy, 0.06), [(x, 0.35 + yy), (x, -0.15 + yy)], [(x, -0.75 + yy), (x, -1.15 + yy)]]
    sticks = [tube([(-2.6, 2.8), (0.6, 1.0)], lambda t: 0.22 - 0.1 * t), tube([(2.6, 2.8), (-0.6, 1.0)], lambda t: 0.22 - 0.1 * t),
              ellipse(0.62, 0.99, 0.12, 0.09, 10), ellipse(-0.62, 0.99, 0.12, 0.09, 10)]
    return make("Snare Drum and Sticks", [top, hoop, side, hoop2] + lugs + sticks)


@design("music_bongos", T)
def bongos(rng):
    out = []
    for cx, rx, top, bot, bw in [(-1.2, 1.25, 0.9, -2.2, 0.85), (1.35, 1.0, 0.55, -2.0, 0.65)]:
        ry = rx * 0.32
        out.append(ellipse(cx, top, rx, ry, 60))
        out.append([(cx + rx * math.cos(t), top - 0.25 + ry * math.sin(t)) for t in [math.pi + math.pi * i / 30 for i in range(31)]])
        out.append(chain([(cx - rx, top)], [(cx - bw, bot)], [(cx + bw * math.cos(t), bot + 0.25 * math.sin(t)) for t in [math.pi + math.pi * i / 20 for i in range(21)]],
                         [(cx + rx, top)]))
        for f in (-0.6, 0.0, 0.6):
            x = cx + f * rx
            out.append([(x, top - 0.25 - ry * math.sqrt(1 - f * f)), (cx + f * bw, top - 0.9 - ry * math.sqrt(1 - f * f) * 0.5)])
            out.append(rrect(cx + f * bw * 1.05 - 0.09, top - 1.25, cx + f * bw * 1.05 + 0.09, top - 0.85, 0.04))
        out.append(cubic((cx - rx * 0.92, top - 1.6), (cx - 0.3, top - 1.9), (cx + 0.3, top - 1.9), (cx + rx * 0.92, top - 1.6), 16))
    block = rect(-0.0, -0.7, 0.4, -0.2)
    return make("Pair of Bongo Drums", out + [block])


@design("music_tambourine", T)
def tambourine(rng):
    outer = circle(0, 0.3, 2.4, 140)
    inner = circle(0, 0.3, 1.95, 120)
    slots, hints = [], []
    for k in range(6):
        a = math.pi / 2 + k * TAU / 6 + math.pi / 6
        slot = arc(0, 0.3, 2.3, a - 0.22, a + 0.22, 8) + arc(0, 0.3, 2.05, a + 0.22, a - 0.22, 8)
        slots.append(slot + [slot[0]])
        cx, cy = 2.18 * math.cos(a), 0.3 + 2.18 * math.sin(a)
        slots.append(ellipse(cx, cy, 0.35, 0.35, 16))
        hints.append(eye(cx, cy, 0.06))
    pattern = [star(0, 0.3, 1.1, 8, 0.55), circle(0, 0.3, 0.35, 20)]
    ribbons = [cubic((0.0, -2.1), (-0.6, -2.6), (0.2, -2.9), (-0.7, -3.4), 20), cubic((0.1, -2.1), (0.6, -2.7), (-0.1, -3.0), (0.6, -3.5), 20)]
    shake = [arc(0, 0.3, 2.8, math.radians(30), math.radians(55), 8), arc(0, 0.3, 2.8, math.radians(125), math.radians(150), 8)]
    return make("Tambourine with Ribbons", [outer, inner] + slots + pattern + ribbons + shake, hints)


@design("music_xylophone", T)
def xylophone(rng):
    bars, hints = [], []
    n = 9
    for k in range(n):
        x = -2.6 + 0.62 * k
        h = 3.6 - 0.2 * k
        y0, y1 = -0.9 - h / 2, -0.9 + h / 2
        bars.append(rrect(x - 0.24, y0, x + 0.24, y1, 0.1))
        hints += [eye(x, y0 + 0.4, 0.06), eye(x, y1 - 0.4, 0.06)]
    rails = [[(-3.0, -2.7 + 0.4 + 0.1), (2.75, -0.9 - (3.6 - 0.2 * 8) / 2 + 0.4 + 0.1)], [(-3.0, 0.9 - 0.4 - 0.1), (2.75, -0.9 + (3.6 - 0.2 * 8) / 2 - 0.4 - 0.1)]]
    mallets = [[(-0.6, 1.3), (2.6, 2.6)], circle(-0.75, 1.24, 0.25, 16), [(1.0, 1.2), (3.0, 1.9)], circle(0.8, 1.13, 0.25, 16)]
    return make("Wooden Xylophone with Mallets", bars + rails + mallets, hints)


@design("music_accordion", T)
def accordion(rng):
    left = rrect(-2.7, -2.0, -1.0, 2.0, 0.15)
    right = rrect(1.0, -2.2, 2.6, 2.2, 0.15)
    pleats = []
    xs = [-1.0 + 2.0 * k / 7 for k in range(8)]
    for k, x in enumerate(xs[1:-1]):
        d = 0.15 if k % 2 == 0 else 0.0
        pleats.append([(x, 1.85 + d), (x, -1.85 - d)])
    top_edge = [(x, 1.9 + (0.15 if k % 2 == 1 else 0.0) + 0.05 * (x + 1.0)) for k, x in enumerate(xs)]
    bot_edge = [(x, -1.9 - (0.15 if k % 2 == 1 else 0.0) - 0.05 * (x + 1.0)) for k, x in enumerate(xs)]
    buttons = [circle(-2.25 + 0.42 * c + (0.21 if r % 2 else 0), 1.4 - 0.5 * r, 0.13, 10) for r in range(6) for c in range(3)]
    keys = [rect(2.6, -1.9, 3.1, 1.9)] + [[(2.6, -1.9 + 0.38 * k), (3.1, -1.9 + 0.38 * k)] for k in range(1, 10)]
    keys += [rect(2.6, -1.9 + 0.38 * k - 0.09, 2.85, -1.9 + 0.38 * k + 0.09) for k in (1, 2, 4, 5, 6, 8, 9)]
    grille = [rrect(1.3, 0.4, 2.3, 1.8, 0.15), star(1.8, 1.1, 0.45, 5, 0.45)]
    strap = [rrect(-2.4, 2.0, -1.3, 2.35, 0.1), rrect(1.3, 2.2, 2.3, 2.55, 0.1)]
    return make("Accordion", [left, right, top_edge, bot_edge] + pleats + buttons + keys + grille + strap)


@design("music_banjo", T)
def banjo(rng):
    pot = [circle(0, 0, 1.6, 100), circle(0, 0, 1.95, 110), circle(0, 0, 1.4, 90)]
    brackets = []
    for k in range(18):
        a = k * TAU / 18
        brackets.append([(1.62 * math.cos(a), 1.62 * math.sin(a)), (1.93 * math.cos(a), 1.93 * math.sin(a))])
    bridge = [rrect(-0.45, -0.55, 0.45, -0.38, 0.05)]
    tail = poly((-0.25, -0.75), (0.25, -0.75), (0.15, -1.45), (-0.15, -1.45))
    neck = [[(-0.25, 1.95), (-0.25, 5.4)], [(0.25, 1.95), (0.25, 5.4)]]
    fr = frets(0, 1.95, 5.4, 0.5, 0.4, 0.94)
    head = smooth([(-0.25, 5.4), (-0.45, 5.8), (-0.35, 6.4), (0.0, 6.6), (0.35, 6.4), (0.45, 5.8), (0.25, 5.4)], n=6)
    pegs = [s for y in (5.8, 6.2) for s in peg(-0.42, y, -1) + peg(0.42, y, 1)]
    fifth = peg(0.25, 3.6, 1)
    strings = [[(x, -0.75), (x * 0.9, 5.4)] for x in (-0.12, 0.12)]
    parts = pot + brackets + bridge + [tail] + neck + fr + [head] + pegs + fifth + strings
    return make("Five-String Banjo", orient(parts, 0, -2.2, -0.55))


@design("music_ukulele", T)
def ukulele(rng):
    body = guitar_outline(1.15, 0.8, 0.95, 0.85)
    hole = [circle(0, 0.85, 0.42, 30)]
    bridge = [rrect(-0.55, -1.05, 0.55, -0.8, 0.1)]
    neck = rect(-0.24, 1.72, 0.24, 3.9)
    fr = frets(0, 1.72, 3.9, 0.48, 0.38, 0.92)
    head = smooth([(-0.24, 3.9), (-0.45, 4.3), (-0.4, 4.85), (0.0, 5.0), (0.4, 4.85), (0.45, 4.3), (0.24, 3.9)], n=6)
    pegs = [s for y in (4.3, 4.65) for s in peg(-0.43, y, -1) + peg(0.43, y, 1)]
    flower = [lens((-0.55, -0.35), (-0.55 + 0.45 * math.cos(a), -0.35 + 0.45 * math.sin(a)), 0.35, 10) for a in [k * TAU / 5 + 0.3 for k in range(5)]]
    strings = [[(x, -0.8), (x * 0.8, 3.9)] for x in (-0.12, 0.12)]
    parts = orient([body, neck, head] + hole + bridge + fr + pegs + flower + strings, 0, -1.4, 0.35)
    st, hi = notes([("e", 1.0, 1.5, 0.55), ("b", 0.9, -1.9, 0.5)])
    return make("Ukulele with a Flower", parts + st, hi + [eye(*orient([[(-0.55, -0.35)]], 0, -1.4, 0.35)[0][0], 0.1)])


@design("music_mandolin", T)
def mandolin(rng):
    r = [(0.0, -1.9), (0.8, -1.75), (1.35, -1.1), (1.4, -0.2), (1.05, 0.7), (0.55, 1.35), (0.22, 1.65)]
    body = smooth(r + [(-x, y) for x, y in reversed(r[1:])], closed=True)
    hole = [ellipse(0, 0.35, 0.32, 0.5, 30), ellipse(0, 0.35, 0.45, 0.65, 34)]
    guard = [cubic((0.45, 0.0), (0.9, -0.2), (1.0, 0.6), (0.6, 0.9), 12)]
    tail = poly((-0.4, -1.1), (0.4, -1.1), (0.25, -1.85), (-0.25, -1.85))
    bridge = [rrect(-0.55, -0.6, 0.55, -0.45, 0.05)]
    neck = rect(-0.22, 1.65, 0.22, 3.6)
    fr = frets(0, 1.65, 3.6, 0.44, 0.36, 0.93)
    head = poly((-0.22, 3.6), (-0.4, 4.9), (0.0, 5.05), (0.4, 4.9), (0.22, 3.6), closed=False)
    pegs = [s for y in (3.85, 4.15, 4.45, 4.75) for s in peg(-0.3 - 0.13 * (y - 3.6), y, -1, 0.3) + peg(0.3 + 0.13 * (y - 3.6), y, 1, 0.3)]
    strings = [[(x, -0.45), (x * 0.8, 3.6)] for x in (-0.1, 0.1)]
    parts = orient([body, tail, neck, head] + hole + guard + bridge + fr + pegs + strings, 0, -1.55, 0.6)
    return make("Mandolin", parts)


@design("music_harmonica", T)
def harmonica(rng):
    front = rect(-3.0, -0.9, 2.6, 0.1)
    top = poly((-3.0, 0.1), (-2.4, 1.3), (3.2, 1.3), (2.6, 0.1), closed=False)
    side = poly((2.6, -0.9), (3.2, 0.3), (3.2, 1.3), closed=False)
    holes = [rect(-2.75 + 0.55 * k, -0.6, -2.45 + 0.55 * k, -0.3) for k in range(10)]
    engr = [[(-2.2, 0.55), (2.2, 0.55)], [(-1.9, 0.95), (2.6, 0.95)], ellipse(0.35, 0.75, 0.8, 0.2, 30)]
    screws = [eye(-2.75, -0.15, 0.06), eye(2.35, -0.15, 0.06)]
    st, hi = notes([("e", -2.4, 2.0, 0.55), ("b", -0.7, 2.2, 0.5), ("e", 1.5, 2.1, 0.55), ("h", 2.6, -2.2, 0.5), ("e", -1.6, -2.3, 0.5)])
    return make("Harmonica", [front, top, side] + holes + engr + st, screws + hi)


# ------------------------------------------------------------- audio -------

@design("music_vintage_microphone", T)
def vintage_microphone(rng):
    cap = rrect(-1.0, -0.2, 1.0, 2.8, 0.95)
    bars = []
    for k in range(1, 10):
        y = -0.2 + 0.3 * k
        d = abs(y - 1.3)
        half = 1.0 if d < 0.55 else math.sqrt(max(0.0, 0.95 ** 2 - (d - 0.55) ** 2)) + 0.05
        bars.append([(-half + 0.05, y), (half - 0.05, y)])
    band = [[(-0.25, -0.2), (-0.25, 2.8)], [(0.25, -0.2), (0.25, 2.8)]]
    bars = [s for b in bars for s in clip_out(b, lambda p: abs(p[0]) < 0.25)]
    yoke = chain([(-1.0, 1.2)], [(-1.3, 1.2)], [(-1.3, -0.5)], arc(0, -0.5, 1.3, math.pi, 2 * math.pi, 20)[1:-1], [(1.3, -0.5)], [(1.3, 1.2)], [(1.0, 1.2)])
    pivots = [circle(-1.3, 1.2, 0.15, 10), circle(1.3, 1.2, 0.15, 10)]
    pole = [[(-0.1, -1.8), (-0.1, -2.55)], [(0.1, -1.8), (0.1, -2.55)]]
    base = [ellipse(0, -2.7, 1.5, 0.3, 50), [(-1.5, -2.7), (-1.5, -2.9)], [(1.5, -2.7), (1.5, -2.9)],
            [(1.5 * math.cos(t), -2.9 + 0.3 * math.sin(t)) for t in [math.pi + math.pi * i / 30 for i in range(31)]]]
    return make("Vintage Stage Microphone", [cap, yoke] + bars + band + pivots + pole + base)


@design("music_headphones", T)
def headphones(rng):
    band = tube(arc(0, -0.2, 2.3, math.radians(10), math.radians(170), 60), 0.4, cap=False)
    pad = arc(0, -0.2, 2.1, math.radians(40), math.radians(140), 30)
    out = [band, pad]
    for s in (-1, 1):
        out.append(rrect(s * 2.25 - 0.18, -0.4, s * 2.25 + 0.18, 0.3, 0.06))
        cup = ellipse(s * 2.1, -1.4, 0.75, 1.15, 50)
        cush = ellipse(s * 2.1 - s * 0.25, -1.4, 0.55, 1.05, 50)
        out += [cup, cush, ellipse(s * 2.25, -1.4, 0.3, 0.5, 24)]
    cable = chain([(-2.1, -2.55)], cubic((-2.1, -2.55), (-1.8, -3.4), (0.0, -2.2), (0.3, -3.0), 20))
    jack = [rrect(0.15, -3.5, 0.45, -3.0, 0.06), [(0.3, -3.5), (0.3, -3.8)]]
    st, hi = notes([("e", -0.9, -1.5, 0.55), ("b", 0.1, -1.2, 0.45)])
    return make("Over-Ear Headphones", out + [cable] + jack + st, hi)


@design("music_turntable", T)
def turntable(rng):
    plinth = rrect(-3.0, -2.4, 3.0, 2.4, 0.2)
    platter = circle(-0.6, 0.0, 2.1, 120)
    grooves = [circle(-0.6, 0.0, r, 100) for r in (1.9, 1.55, 1.2)]
    label = circle(-0.6, 0.0, 0.7, 50)
    arm_base = [circle(2.2, 1.5, 0.45, 30), circle(2.2, 1.5, 0.2, 14)]
    arm = [chain([(2.2, 1.5)], quad((2.2, 1.5), (2.4, 0.0), (1.2, -0.9), 20))]
    shell = [place(rrect(-0.2, -0.35, 0.2, 0.25, 0.06), 1.15, -0.95, 0.9)]
    weight = [place(rrect(-0.2, -0.25, 0.2, 0.25, 0.05), 2.15, 2.2, 0.0)]
    knobs = [circle(2.3, -1.7, 0.25, 16), rrect(1.4, -2.1, 1.9, -1.85, 0.06), rrect(1.4, -1.75, 1.9, -1.5, 0.06)]
    rest = [rect(2.65, 0.0, 2.8, 0.6)]
    return make("Record Turntable", [plinth, platter, label] + grooves + arm_base + arm + shell + weight + knobs + rest, [eye(-0.6, 0.0, 0.1)])


@design("music_cassette_tape", T)
def cassette_tape(rng):
    shell = rrect(-3.0, -1.9, 3.0, 1.9, 0.2)
    label = rrect(-2.6, -0.65, 2.6, 1.55, 0.15)
    window = rrect(-0.8, 0.0, 0.8, 0.8, 0.1)
    reels = []
    for x in (-1.45, 1.45):
        reels += [circle(x, 0.4, 0.5, 30), star(x, 0.4, 0.3, 6, 0.65)]
    tape = [[(-0.7, 0.15), (0.7, 0.15)]]
    lines = [[(-2.3, 1.2), (2.3, 1.2)]]
    bottom = poly((-2.0, -1.9), (-1.6, -0.95), (1.6, -0.95), (2.0, -1.9), closed=False)
    holes = [circle(x, -1.45, 0.14, 10) for x in (-1.0, 1.0)] + [rect(-0.4, -1.6, -0.15, -1.3), rect(0.15, -1.6, 0.4, -1.3)]
    screws = [eye(x, y, 0.08) for x, y in [(-2.75, 1.65), (2.75, 1.65), (-2.75, -1.65), (2.75, -1.65), (0.0, -1.2)]]
    return make("Mixtape Cassette", [shell, label, window, bottom] + reels + tape + lines + holes, screws)


@design("music_boombox", T)
def boombox(rng):
    body = rrect(-3.0, -1.7, 3.0, 1.2, 0.3)
    handle = chain([(-2.2, 1.2)], [(-2.2, 2.2)], [(2.2, 2.2)], [(2.2, 1.2)])
    handle_in = chain([(-1.9, 1.2)], [(-1.9, 1.9)], [(1.9, 1.9)], [(1.9, 1.2)])
    spk = []
    for x in (-1.95, 1.95):
        spk += [circle(x, -0.35, 0.9, 60), circle(x, -0.35, 0.65, 50), circle(x, -0.35, 0.25, 20)]
    deck = [rrect(-0.85, -1.3, 0.85, 0.15, 0.1), rrect(-0.6, -0.95, 0.6, -0.35, 0.08), circle(-0.3, -0.65, 0.13, 10), circle(0.3, -0.65, 0.13, 10)]
    btns = [rrect(-0.8 + 0.42 * k, 0.4, -0.5 + 0.42 * k, 0.75, 0.05) for k in range(4)]
    dial = [rrect(-2.7, 0.55, -1.2, 0.95, 0.1), [(-2.0, 0.6), (-2.0, 0.9)], circle(1.5, 0.75, 0.17, 12), circle(2.0, 0.75, 0.17, 12), circle(2.5, 0.75, 0.17, 12)]
    antenna = [[(2.4, 2.2), (3.2, 3.2)], circle(3.25, 3.25, 0.08, 8)]
    return make("Retro Boombox", [body, handle, handle_in] + spk + deck + btns + dial + antenna)


@design("music_jukebox", T)
def jukebox(rng):
    body = chain([(-2.1, -3.0)], [(-2.1, 0.8)], arc(0, 0.8, 2.1, math.pi, 0, 60), [(2.1, -3.0)], [(-2.1, -3.0)])
    tube_ = chain([(-1.75, -1.2)], [(-1.75, 0.8)], arc(0, 0.8, 1.75, math.pi, 0, 50), [(1.75, -1.2)])
    window = chain([(-1.3, -0.4)], [(-1.3, 0.8)], arc(0, 0.8, 1.3, math.pi, 0, 40), [(1.3, -0.4)], [(-1.3, -0.4)])
    record = [ellipse(0, 0.6, 0.9, 0.3, 40), ellipse(0, 0.6, 0.35, 0.12, 20)]
    arm = [[(0.9, 1.6), (0.3, 0.75)]]
    sel = [rrect(-1.3 + 0.55 * c, -1.0 - 0.4 * r, -0.95 + 0.55 * c, -0.75 - 0.4 * r, 0.05) for r in range(2) for c in range(5)]
    grille = [rrect(-1.5, -2.7, 1.5, -1.9, 0.1)] + [[(x, -2.6), (x, -2.0)] for x in (-1.1, -0.7, -0.3, 0.1, 0.5, 0.9)]
    side = [[(-2.1, -1.2), (2.1, -1.2)], [(-2.1, -1.75), (2.1, -1.75)]]
    st, hi = notes([("e", -2.9, 2.0, 0.55), ("b", 2.2, 2.3, 0.45)])
    return make("Classic Jukebox", [body, tube_, window, arm[0]] + record + sel + grille + side + st, hi)


@design("music_gramophone", T)
def gramophone(rng):
    box = rect(-2.0, -2.8, 1.6, -1.4)
    top = poly((-2.0, -1.4), (-1.6, -1.0), (2.0, -1.0), (1.6, -1.4), closed=False)
    side = poly((1.6, -2.8), (2.0, -2.4), (2.0, -1.0), closed=False)
    panel = rrect(-1.7, -2.5, 1.3, -1.7, 0.1)
    disc = ellipse(-0.2, -1.05, 1.4, 0.25, 50)
    crank = [[(2.0, -1.8), (2.6, -1.8)], [(2.6, -1.8), (2.6, -2.3)], rrect(2.5, -2.6, 2.7, -2.3, 0.06)]
    c = cubic((0.6, -0.95), (0.7, 0.2), (0.4, 0.6), (-0.2, 1.4), 30)
    horn = tube(c, lambda t: 0.25 + 2.3 * t ** 2.5, cap=False)
    mouth = ellipse(c[-1][0], c[-1][1], 1.3, 0.4, 50, rot=math.atan2(c[-1][1] - c[-2][1], c[-1][0] - c[-2][0]) + math.pi / 2)
    arm = [[(0.6, -0.95), (0.0, -1.0)]]
    st, hi = notes([("e", 1.6, 1.4, 0.55), ("b", 1.9, -0.2, 0.45)])
    return make("Antique Gramophone", [box, top, side, panel, disc, horn, mouth] + crank + arm + st, hi)


@design("music_metronome", T)
def metronome(rng):
    body = poly((-1.7, -2.4), (1.7, -2.4), (0.6, 2.6), (-0.6, 2.6))
    cap = rrect(-0.75, 2.6, 0.75, 2.85, 0.1)
    base = rrect(-2.0, -2.9, 2.0, -2.4, 0.1)
    window = poly((-0.9, -1.2), (0.9, -1.2), (0.42, 2.0), (-0.42, 2.0))
    ticks = [[(-0.1, y), (0.1, y)] for y in (1.6, 1.25, 0.9, 0.55, 0.2, -0.15)]
    arm = [[(0.0, -1.0), (0.75, 2.9)]]
    wt = [place(poly((-0.3, -0.2), (0.3, -0.2), (0.2, 0.2), (-0.2, 0.2)), 0.45, 1.35, -0.19)]
    lower = rrect(-1.3, -2.2, 1.3, -1.5, 0.1)
    key = [[(1.55, -1.8), (2.3, -1.8)], ellipse(2.5, -1.8, 0.2, 0.35, 16)]
    swing = [arc(0.0, -1.0, 3.7, math.radians(70), math.radians(85), 8), arc(0.0, -1.0, 3.7, math.radians(95), math.radians(110), 8)]
    return make("Wooden Metronome", [body, cap, base, window, lower] + ticks + arm + wt + key + swing, [eye(0, -1.0, 0.08)])


@design("music_music_stand", T)
def music_stand(rng):
    desk = poly((-2.4, 0.2), (2.4, 0.2), (2.2, 3.0), (-2.2, 3.0))
    lip = rrect(-2.5, 0.0, 2.5, 0.25, 0.08)
    sheet = [poly((-1.9, 0.3), (0.0, 0.25), (0.0, 2.85), (-1.8, 2.9)), poly((0.0, 0.25), (1.9, 0.3), (1.8, 2.9), (0.0, 2.85))]
    staves = []
    for x0, x1 in ((-1.65, -0.25), (0.25, 1.65)):
        for base in (1.9, 0.75):
            staves += [[(x0, base + 0.2 * k), (x1, base + 0.2 * k)] for k in range(5)]
    hi = [ellipse(x, y, 0.13, 0.09, 12, rot=0.35) for x, y in [(-1.3, 2.1), (-0.9, 2.3), (-0.5, 2.0), (0.6, 2.2), (1.0, 1.9), (1.4, 2.4),
                                                               (-1.2, 0.95), (-0.7, 1.15), (0.5, 0.85), (1.2, 1.25)]]
    stems = [[(x + 0.12, y), (x + 0.12, y + 0.55)] for x, y in [(-1.3, 2.1), (-0.9, 2.3), (-0.5, 2.0), (0.6, 2.2), (1.0, 1.9), (1.4, 2.4),
                                                                 (-1.2, 0.95), (-0.7, 1.15), (0.5, 0.85), (1.2, 1.25)]]
    pole = [[(-0.08, 0.0), (-0.08, -2.2)], [(0.08, 0.0), (0.08, -2.2)], rrect(-0.18, -1.0, 0.18, -0.7, 0.05)]
    legs = [[(0.0, -2.2), (-1.8, -3.0)], [(0.0, -2.2), (1.8, -3.0)], [(0.0, -2.2), (0.0, -3.0)]]
    return make("Music Stand with Sheet Music", [desk, lip] + sheet + staves + stems + pole + legs, hi)


@design("music_treble_clef", T)
def treble_clef(rng):
    pts = [(-0.45, -2.3), (-0.55, -2.65), (-0.2, -2.95), (0.2, -2.7), (0.25, -2.0), (0.1, -0.6), (-0.05, 0.8), (-0.05, 2.0), (0.15, 2.95), (0.5, 3.4),
           (0.8, 2.95), (0.65, 2.2), (-0.3, 1.45), (-0.95, 0.5), (-1.05, -0.4), (-0.6, -1.1), (0.2, -1.25), (0.85, -0.8), (0.85, -0.05), (0.35, 0.35),
           (-0.25, 0.15), (-0.35, -0.35), (0.0, -0.6)]
    c = smooth(pts, n=10)
    clef = [(x * 1.15 - 1.6, y * 0.95) for x, y in c]
    ball = (-0.45 * 1.15 - 1.6, -2.3 * 0.95)
    staff = []
    for k in range(5):
        y = -1.2 + 0.6 * k
        staff += clip_out([(-3.0 + 6.2 * i / 124, y) for i in range(125)], lambda p: any(math.dist(p, q) < 0.18 for q in clef[::2]))
    st, hi = notes([("q", 0.0, -0.9, 0.8), ("e", 0.9, 0.0, 0.8), ("q", 1.85, 0.6, 0.8)])
    return make("Treble Clef on the Staff", [clef] + staff + st, hi + [eye(ball[0], ball[1], 0.22)])


@design("music_staff_swirl", T)
def staff_swirl(rng):
    def y_at(x):
        return 1.1 * math.sin(0.9 * x + 0.4)
    lines = [[(x, y_at(x) - 0.5 + 0.25 * k) for x in [-3.2 + 6.4 * i / 100 for i in range(101)]] for k in range(5)]
    spec = []
    for x, k, kind in [(-2.4, 1, "e"), (-1.6, 3, "q"), (-0.7, 2, "b"), (0.6, 4, "q"), (1.4, 0, "e"), (2.4, 2, "q")]:
        spec.append((kind, x, y_at(x) - 0.5 + 0.25 * k, 0.55))
    st, hi = notes(spec)
    sparkles = [star(-2.6, 2.4, 0.3, 4, 0.35), star(2.5, -2.3, 0.3, 4, 0.35), star(0.3, 2.7, 0.22, 4, 0.35)]
    return make("Swirling Musical Staff", lines + st + sparkles, hi)


@design("music_concert_stage", T)
def concert_stage(rng):
    floor = poly((-3.2, -1.6), (3.2, -1.6), (2.6, -0.6), (-2.6, -0.6))
    front = rect(-3.2, -2.4, 3.2, -1.6)
    boards = [[(x, -1.6), (x * 0.8, -0.6)] for x in (-1.6, 0.0, 1.6)]
    val = chain([(-3.2, 3.2)], [(-3.2, 2.6)], *[arc(-3.2 + 0.8 * (k + 0.5), 2.6, 0.4, math.pi, 2 * math.pi, 10) for k in range(8)], [(3.2, 2.6)], [(3.2, 3.2)], [(-3.2, 3.2)])
    curtains = [chain([(-3.2, 2.6)], [(-3.2, -0.6)], [(-2.5, -0.6)], quad((-2.5, -0.6), (-2.1, 0.6), (-2.6, 1.0), 12), quad((-2.6, 1.0), (-2.0, 1.9), (-1.8, 2.6), 12)),
                chain([(3.2, 2.6)], [(3.2, -0.6)], [(2.5, -0.6)], quad((2.5, -0.6), (2.1, 0.6), (2.6, 1.0), 12), quad((2.6, 1.0), (2.0, 1.9), (1.8, 2.6), 12))]
    folds = [[(-2.9, 2.5), (-2.9, -0.5)], [(2.9, 2.5), (2.9, -0.5)]]
    lamp = [rrect(-0.35, 2.15, 0.35, 2.6, 0.1)]
    beams = [[(-0.3, 2.15), (-1.4, -0.95)], [(0.3, 2.15), (1.4, -0.95)]]
    spot = [ellipse(0.0, -1.05, 1.45, 0.3, 50)]
    mic = [[(0.0, -1.0), (0.0, 0.6)], [(0.0, 0.6), (0.4, 0.9)], ellipse(0.48, 0.97, 0.12, 0.18, 10, rot=-0.9), [(-0.3, -1.1), (0.0, -1.0), (0.3, -1.1)]]
    amps = [rrect(-2.3, -1.4, -1.6, -0.3, 0.06), circle(-1.95, -0.85, 0.25, 16), rrect(1.6, -1.4, 2.3, -0.3, 0.06), circle(1.95, -0.85, 0.25, 16)]
    st, hi = notes([("e", -0.9, 0.9, 0.4), ("b", 0.4, 1.2, 0.35)])
    return make("Concert Stage under Spotlights", [floor, front, val] + boards + curtains + folds + lamp + beams + spot + mic + amps + st, hi)


@design("music_amplifier", T)
def amplifier(rng):
    body = rrect(-2.8, -2.4, 2.8, 1.8, 0.25)
    panel = rect(-2.6, 0.9, 2.6, 1.6)
    knobs = [circle(-1.9 + 0.62 * k, 1.25, 0.2, 14) for k in range(6)]
    jack = [circle(-2.35, 1.25, 0.1, 8)]
    grille = rrect(-2.5, -2.1, 2.5, 0.6, 0.15)
    cone = [circle(0, -0.75, 1.15, 60), circle(0, -0.75, 0.4, 24)]
    logo = rrect(1.0, 0.0, 2.2, 0.4, 0.1)
    handle = chain([(-0.9, 1.8)], [(-0.9, 2.2)], quad((-0.9, 2.2), (0.0, 2.6), (0.9, 2.2), 12), [(0.9, 1.8)])
    feet = [rect(-2.4, -2.6, -1.9, -2.4), rect(1.9, -2.6, 2.4, -2.4)]
    cable = [cubic((-2.35, 1.25), (-3.2, 1.0), (-3.4, -1.0), (-3.0, -2.8), 20), rrect(-3.15, -3.3, -2.85, -2.8, 0.06)]
    return make("Guitar Amplifier", [body, panel, grille, logo, handle] + knobs + jack + cone + feet + cable)


@design("music_sitar", T)
def sitar(rng):
    gourd = chain(arc(0, -1.0, 1.5, math.radians(70), math.radians(470), 90))
    gourd_band = arc(0, -1.0, 1.25, math.radians(200), math.radians(340), 30)
    neck = [[(-0.32, 0.4), (-0.32, 5.4)], [(0.32, 0.4), (0.32, 5.4)]]
    fr = [arc(0, y - 0.2, 0.4, math.radians(55), math.radians(125), 6) for y in [1.0 + 0.38 * k for k in range(11)]]
    top_gourd = [circle(0.9, 4.6, 0.6, 40)]
    top_gourd = clip_out(top_gourd[0], lambda p: abs(p[0]) < 0.33)
    head = [rect(-0.32, 5.4, 0.32, 6.0), poly((-0.32, 6.0), (0.0, 6.4), (0.32, 6.0), closed=False)]
    pegs = [s for y in (5.55, 5.85) for s in peg(-0.32, y, -1, 0.4)] + [s for y in (5.7,) for s in peg(0.32, y, 1, 0.4)] + \
        [s for y in (2.6, 3.2, 3.8) for s in peg(-0.32, y, -1, 0.35)]
    bridge = [rrect(-0.45, -1.4, 0.45, -1.2, 0.05)]
    rose = [circle(0, -1.0, 0.35, 20)]
    return make("Sitar", orient([gourd, gourd_band] + neck + fr + top_gourd + head + pegs + bridge + rose, 0, -2.4, -0.7))


@design("music_didgeridoo", T)
def didgeridoo(rng):
    c = [(-3.0 + 6.0 * t, -1.6 + 3.0 * t + 0.15 * math.sin(5 * t)) for t in [i / 40 for i in range(41)]]
    w = lambda t: 0.75 - 0.35 * t
    body = tube(c, w)
    mouth = ellipse(c[0][0], c[0][1], 0.2, 0.39, 20, rot=-0.5)
    bands = []
    for f in (0.15, 0.4, 0.65, 0.88):
        i = int(f * 40)
        x, y = c[i]
        a = math.atan2(c[i + 1][1] - c[i - 1][1], c[i + 1][0] - c[i - 1][0]) + math.pi / 2
        hw = w(f) / 2
        bands.append([(x - hw * math.cos(a), y - hw * math.sin(a)), (x + hw * math.cos(a), y + hw * math.sin(a))])
    hints = []
    for f in (0.22, 0.27, 0.32, 0.47, 0.52, 0.57, 0.72, 0.77, 0.82):
        x, y = c[int(f * 40)]
        hints.append(eye(x, y, 0.08))
    st, hi = notes([("e", -2.2, 1.5, 0.6), ("b", -0.9, 2.0, 0.5), ("e", 1.8, -1.9, 0.6)])
    return make("Painted Didgeridoo", [body, mouth] + bands + st, hints + hi)


@design("music_triangle", T)
def triangle(rng):
    c = [(-0.2, 2.3), (-2.4, -1.6), (2.4, -1.6), (0.3, 2.1)]
    pts = []
    for a, b in zip(c, c[1:]):
        pts += [(a[0] + (b[0] - a[0]) * i / 30, a[1] + (b[1] - a[1]) * i / 30) for i in range(30)]
    pts.append(c[-1])
    tri = tube(pts, 0.25)
    loop = [chain([(0.05, 2.3)], quad((0.05, 2.3), (-0.4, 3.0), (0.05, 3.2), 10), quad((0.05, 3.2), (0.5, 3.0), (0.05, 2.3), 10))]
    beater = [tube([(0.4, -0.9), (2.8, 1.6)], 0.14)]
    ring = [arc(-0.4, 0.0, 2.9, math.radians(150), math.radians(190), 10), arc(-0.4, 0.0, 3.3, math.radians(145), math.radians(195), 10),
            arc(0.6, 0.0, 2.9, math.radians(-15), math.radians(15), 10)]
    st, hi = notes([("e", 1.7, 2.0, 0.5)])
    return make("Ringing Triangle", [tri] + loop + beater + ring + st, hi)


@design("music_maracas", T)
def maracas(rng):
    out = []
    for x, y, a in [(-1.0, 0.6, 0.45), (1.0, 0.6, -0.45)]:
        head = ellipse(0, 1.2, 1.0, 1.35, 60)
        handle = chain([(-0.15, -0.12)], [(-0.18, -2.4)], arc(0, -2.4, 0.18, math.pi, 2 * math.pi, 6), [(0.15, -0.12)])
        zz = zigzag(-0.95, 0.95, 1.2, 0.15, 5)
        bands = [arc(0, 1.2 + 0.5 - 2.0, 2.0, math.radians(64), math.radians(116), 14), arc(0, 1.2 - 0.5 + 2.0, 2.0, math.radians(244), math.radians(296), 14)]
        dots = [circle(dx, 1.2 + dy, 0.12, 10) for dx, dy in [(0.0, 0.85), (-0.45, 0.75), (0.45, 0.75), (0.0, -0.85)]]
        out += [place(p, x, y - 0.4, a) for p in [head, handle, zz] + bands + dots]
    shake = [arc(-1.0, 1.9, 2.2, math.radians(110), math.radians(135), 8), arc(1.0, 1.9, 2.2, math.radians(45), math.radians(70), 8)]
    return make("Pair of Maracas", out + shake)


@design("music_hand_cymbals", T)
def hand_cymbals(rng):
    left = ellipse(-1.3, 0.0, 1.5, 1.9, 90, rot=0.15)
    right = ellipse(1.3, 0.0, 1.5, 1.9, 90, rot=-0.15)
    left = clip_out(left, lambda p: ((p[0] - 1.3) / 1.5) ** 2 + (p[1] / 1.9) ** 2 < 0.95)
    bell = [ellipse(1.3, 0.0, 0.5, 0.62, 30, rot=-0.15), ellipse(1.3, 0.0, 0.25, 0.3, 20, rot=-0.15)]
    rings = [ellipse(1.3, 0.0, 1.0, 1.25, 70, rot=-0.15)]
    strapL = [chain([(-2.4, 0.4)], quad((-2.4, 0.4), (-3.4, 0.0), (-2.4, -0.4), 12))]
    clash = [[(-0.1 + 0.6 * math.cos(a), 2.0 + 0.6 * math.sin(a)), (-0.1 + 1.0 * math.cos(a), 2.0 + 1.0 * math.sin(a))] for a in (0.7, 1.57, 2.4)]
    clash = [[(0.0 + 0.5 * math.cos(a), 2.0 + 0.5 * math.sin(a)), (0.0 + 0.95 * math.cos(a), 2.0 + 0.95 * math.sin(a))] for a in (0.55, 1.57, 2.6)]
    return make("Pair of Clashing Cymbals", [right] + left + bell + rings + strapL + clash)


@design("music_pipe_organ", T)
def pipe_organ(rng):
    out = []
    heights = [2.2, 2.8, 3.3, 3.8, 4.2, 3.8, 3.3, 2.8, 2.2]
    for k, h in enumerate(heights):
        x = -2.6 + 0.65 * k
        top = -0.2 + h
        out.append(chain([(x - 0.24, -0.2 + 0.5)], [(x - 0.24, top)], arc(x, top, 0.24, math.pi, 0, 8), [(x + 0.24, -0.2 + 0.5)], [(x, -0.2)], [(x - 0.24, -0.2 + 0.5)]))
        out.append(arc(x, 0.6, 0.15, 0, math.pi, 6) + [(x - 0.15, 0.6)])
    case = [rect(-3.0, -2.9, 3.0, -0.2)]
    keys1 = keyboard(-2.3, 2.3, -1.2, -0.75, 13, 0.6)
    keys2 = [rect(-2.5, -1.55, 2.5, -1.2)]
    stops = [circle(x, -0.48, 0.13, 10) for x in (-2.7, -2.35, 2.35, 2.7)]
    bench = [rrect(-1.6, -2.15, 1.6, -1.9, 0.05)]
    return make("Grand Pipe Organ", out + case + keys1 + keys2 + stops + bench)


@design("music_music_box", T)
def music_box(rng):
    front = rect(-2.4, -2.8, 2.0, -1.0)
    top = poly((-2.4, -1.0), (-1.8, -0.5), (2.6, -0.5), (2.0, -1.0), closed=False)
    side = poly((2.0, -2.8), (2.6, -2.3), (2.6, -0.5), closed=False)
    lid = poly((-1.8, -0.5), (-1.6, 2.6), (2.8, 2.6), (2.6, -0.5), closed=False)
    mirror = ellipse(0.6, 1.1, 1.1, 1.15, 50)
    panel = rrect(-2.1, -2.5, 1.7, -1.3, 0.1)
    heart_ = heart(-0.2, -1.9, 0.35)
    key = [[(2.6, -1.4), (3.0, -1.4)], ellipse(3.2, -1.4, 0.2, 0.35, 16)]
    # ballerina
    base = ellipse(0.4, -0.75, 0.5, 0.12, 20)
    leg = [[(0.4, -0.75), (0.4, 0.3)], [(0.45, 0.3), (1.2, 0.0)]]
    tutu = [(0.4 + 0.75 * math.cos(t) * (1 + 0.08 * math.sin(10 * t)), 0.38 + 0.2 * math.sin(t) * (1 + 0.3 * math.sin(10 * t))) for t in [TAU * i / 60 for i in range(61)]]
    torso = poly((0.25, 0.45), (0.55, 0.45), (0.5, 1.1), (0.3, 1.1))
    head = circle(0.4, 1.35, 0.2, 16)
    bun = circle(0.4, 1.63, 0.1, 10)
    arms = [quad((0.3, 1.05), (-0.2, 1.5), (0.25, 1.95), 10), quad((0.5, 1.05), (1.0, 1.5), (0.55, 1.95), 10)]
    st, hi = notes([("e", -2.6, 1.4, 0.5), ("b", -2.4, -0.2, 0.4)])
    return make("Ballerina Music Box", [front, top, side, lid, mirror, panel, heart_, base, tutu, torso, head, bun] + key + leg + arms + st, hi)


@design("music_cathedral_radio", T)
def cathedral_radio(rng):
    a1 = math.atan2(math.sqrt(1.6 ** 2 - 0.6 ** 2), 0.6)
    a2 = math.atan2(math.sqrt(1.25 ** 2 - 0.45 ** 2), 0.45)
    body = chain([(-2.2, -2.8)], [(-2.2, 0.4)], arc(-0.6, 0.4, 1.6, math.pi, a1, 30), arc(0.6, 0.4, 1.6, math.pi - a1, 0, 30), [(2.2, -2.8)], [(-2.2, -2.8)])
    inner = chain([(-1.7, -0.6)], [(-1.7, 0.4)], arc(-0.45, 0.4, 1.25, math.pi, a2, 24), arc(0.45, 0.4, 1.25, math.pi - a2, 0, 24), [(1.7, -0.6)], [(-1.7, -0.6)])
    bars = []
    for x in (-1.2, -0.6, 0.0, 0.6, 1.2):
        ytop = max(y for xx, y in inner if abs(xx - x) < 0.08) - 0.05
        bars.append([(x, -0.6), (x, ytop)])
    arches = [arc(-0.6, 0.6, 0.6, 0, math.pi, 12), arc(0.6, 0.6, 0.6, 0, math.pi, 12)]
    dial = [chain(arc(0, -1.5, 0.7, 0, math.pi, 20), [(0.7, -1.5)])] + [[(0.55 * math.cos(a), -1.5 + 0.55 * math.sin(a)), (0.68 * math.cos(a), -1.5 + 0.68 * math.sin(a))] for a in (0.4, 0.9, 1.57, 2.2, 2.75)]
    needle = [[(0, -1.5), (0.3, -1.0)]]
    knobs = [circle(-1.4, -2.0, 0.28, 18), circle(1.4, -2.0, 0.28, 18), circle(0.0, -2.35, 0.22, 14)]
    base = [rect(-2.4, -3.05, 2.4, -2.8)]
    return make("Cathedral Radio", [body, inner] + bars + arches + dial + needle + knobs + base)


@design("music_floor_speaker", T)
def floor_speaker(rng):
    cab = rrect(-1.7, -2.8, 1.7, 3.0, 0.2)
    woof = [circle(0, -1.0, 1.25, 80), circle(0, -1.0, 1.05, 70), circle(0, -1.0, 0.35, 24)]
    mid = [circle(0, 1.0, 0.7, 50), circle(0, 1.0, 0.55, 40), circle(0, 1.0, 0.2, 16)]
    tweet = [circle(0, 2.35, 0.35, 24), circle(0, 2.35, 0.15, 12)]
    port = [ellipse(0, -2.45, 0.6, 0.15, 24)]
    feet = [rect(-1.5, -3.05, -1.0, -2.8), rect(1.0, -3.05, 1.5, -2.8)]
    waves = [arc(0, 0.0, r, math.radians(-35), math.radians(35), 10) for r in (2.1, 2.6)] + [arc(0, 0.0, r, math.radians(145), math.radians(215), 10) for r in (2.1, 2.6)]
    st, hi = notes([("e", 2.4, 1.8, 0.5), ("b", -3.2, 1.6, 0.4)])
    return make("Hi-Fi Floor Speaker", [cab] + woof + mid + tweet + port + feet + waves + st, hi)


@design("music_synthesizer", T)
def synthesizer(rng):
    case = rrect(-3.2, -1.6, 3.2, 1.4, 0.15)
    keys = keyboard(-2.4, 3.0, -1.4, 0.0, 15, 0.6)
    wheels = [rrect(-3.0, -1.3, -2.75, -0.1, 0.1), rrect(-2.7, -1.3, -2.45, -0.1, 0.1)]
    screen = rrect(-0.6, 0.4, 0.8, 1.1, 0.08)
    knobs = [circle(x, 0.75, 0.17, 12) for x in (-2.7, -2.2, -1.7, -1.2)]
    sliders = []
    for x in (1.3, 1.75, 2.2, 2.65):
        sliders += [[(x, 0.25), (x, 1.2)], rrect(x - 0.12, 0.5 + 0.15 * ((x * 10) % 3), x + 0.12, 0.7 + 0.15 * ((x * 10) % 3), 0.04)]
    stand = [[(-2.2, -1.6), (2.2, -3.0)], [(2.2, -1.6), (-2.2, -3.0)]]
    return make("Synthesizer Keyboard", [case, screen] + keys + wheels + knobs + sliders + stand)


@design("music_vinyl_sleeve", T)
def vinyl_sleeve(rng):
    sleeve = rect(-3.0, -2.4, 0.9, 2.4)
    rec = [circle(1.0, 0.0, 2.3, 140), circle(1.0, 0.0, 1.95, 120), circle(1.0, 0.0, 1.55, 100), circle(1.0, 0.0, 0.75, 50)]
    rec = [s for r in rec for s in clip_out(r, lambda p: p[0] < 0.9)]
    art = [circle(-1.05, 0.3, 1.2, 60), star(-1.05, 0.3, 0.9, 8, 0.5)]
    st, hi = notes([("b", -1.4, -0.1, 0.5)])
    title = [[(-2.6, -1.6), (-0.4, -1.6)], [(-2.6, -2.0), (-1.2, -2.0)]]
    return make("Vinyl Record and Sleeve", [sleeve] + rec + art + title, [eye(1.6, 0.0, 0.1)] + hi)


@design("music_timpani", T)
def timpani(rng):
    rim = ellipse(0, 0.8, 2.5, 0.7, 120)
    hoop = [(2.5 * math.cos(t), 0.55 + 0.7 * math.sin(t)) for t in [math.pi + math.pi * i / 60 for i in range(61)]]
    kettle = chain([(-2.5, 0.55)], cubic((-2.5, 0.55), (-2.4, -1.6), (-1.0, -2.0), (0.0, -2.0), 20), cubic((0.0, -2.0), (1.0, -2.0), (2.4, -1.6), (2.5, 0.55), 20))
    rods = []
    for k in range(5):
        t = math.pi + math.pi * (k + 0.5) / 5
        x = 2.5 * math.cos(t)
        y = 0.55 + 0.7 * math.sin(t)
        rods.append([(x, y), (x * 0.95, y - 1.0)])
        rods.append([(x - 0.15, y + 0.2), (x + 0.15, y + 0.2)])
    base = [[(-1.0, -1.95), (-1.6, -2.9)], [(1.0, -1.95), (1.6, -2.9)], [(0.0, -2.0), (0.0, -2.9)], circle(-1.6, -2.95, 0.12, 10), circle(1.6, -2.95, 0.12, 10),
            rrect(0.2, -2.9, 1.0, -2.7, 0.06)]
    mallets = [[(-2.4, 2.9), (-0.4, 1.0)], circle(-0.3, 0.9, 0.22, 14), [(2.4, 2.9), (0.4, 1.0)], circle(0.3, 0.9, 0.22, 14)]
    return make("Copper Timpani Drum", [rim, hoop, kettle] + rods + base + mallets)


@design("music_steelpan", T)
def steelpan(rng):
    rim = ellipse(0, 0.9, 2.7, 1.3, 120)
    skirt = chain([(-2.7, 0.9)], [(-2.7, -0.3)], [(2.7 * math.cos(t), -0.3 + 1.3 * math.sin(t)) for t in [math.pi + math.pi * i / 60 for i in range(61)]], [(2.7, 0.9)])
    pads = []
    for k in range(8):
        a = k * TAU / 8
        pads.append(ellipse(1.75 * math.cos(a), 0.9 + 0.82 * math.sin(a), 0.45, 0.22, 20))
    for k in range(4):
        a = k * TAU / 4 + math.pi / 4
        pads.append(ellipse(0.75 * math.cos(a), 0.9 + 0.36 * math.sin(a), 0.3, 0.14, 16))
    legs = [[(-1.8, -1.25), (-2.4, -3.0)], [(1.8, -1.25), (2.4, -3.0)], [(-2.1, -2.1), (2.1, -2.1)]]
    sticks = [[(-1.0, 2.0), (-2.6, 3.2)], ellipse(-0.85, 1.9, 0.25, 0.2, 14), [(1.0, 2.1), (2.6, 3.2)], ellipse(0.85, 2.0, 0.25, 0.2, 14)]
    return make("Caribbean Steel Drum", [rim, skirt] + pads + legs + sticks)


@design("music_notes_medley", T)
def notes_medley(rng):
    st = []
    a, b = beamed(-2.6, -1.6, 1.6, 0.9, 0.3)
    st += a + b
    q, _ = note(0.3, 0.4, 1.5, flag=True, hollow=True)
    st += q
    h, _ = note(-2.0, 1.2, 1.1, flag=False, hollow=True)
    st += h
    whole = [ellipse(1.6, -2.1, 0.55, 0.38, 30), ellipse(1.6, -2.1, 0.28, 0.2, 20, rot=-0.6)]
    sharp = [[(1.75, 1.0), (1.75, 2.9)], [(2.25, 1.0), (2.25, 2.9)], poly((1.45, 2.0), (2.55, 2.3), (2.55, 2.05), (1.45, 1.75)), poly((1.45, 1.4), (2.55, 1.7), (2.55, 1.45), (1.45, 1.15))]
    flat = [chain([(2.5, 0.6)], [(2.5, -1.1)], cubic((2.5, -1.1), (3.4, -0.6), (3.3, -0.1), (2.5, -0.35), 16))]
    sparkles = [star(-0.6, 2.6, 0.3, 4, 0.35), star(0.2, -2.6, 0.25, 4, 0.35), star(-2.9, 0.0, 0.22, 4, 0.35)]
    return make("Medley of Music Notes", st + whole + sharp + flat + sparkles)


@design("music_panpipes", T)
def panpipes(rng):
    out = []
    for k in range(8):
        x = -2.45 + 0.7 * k
        top = 2.2
        bot = 2.2 - (4.8 - 0.42 * k)
        out.append(chain([(x - 0.28, top)], [(x - 0.28, bot + 0.28)], arc(x, bot + 0.28, 0.28, math.pi, 2 * math.pi, 8), [(x + 0.28, top)]))
        out.append(ellipse(x, top, 0.28, 0.1, 16))
    bind = [rrect(-2.85, 0.9, 2.85, 1.3, 0.1), rrect(-2.85, -0.2, 0.8, 0.2, 0.1)]
    out = [s for p in out for s in clip_out(p, lambda q: (-2.85 < q[0] < 2.85 and 0.9 < q[1] < 1.3) or (-2.85 < q[0] < 0.8 and -0.2 < q[1] < 0.2))]
    cord = [quad((2.85, 1.1), (3.4, 0.0), (2.9, -1.0), 10), circle(2.9, -1.2, 0.2, 12)]
    st, hi = notes([("e", 2.0, -1.8, 0.6), ("b", 0.9, -2.4, 0.45)])
    return make("Bamboo Panpipes", out + bind + cord + st, hi)


@design("music_marching_drum", T)
def marching_drum(rng):
    shell = ellipse(-1.6, 0.0, 0.65, 2.0, 60)
    shell2 = clip_out(ellipse(1.6, 0.0, 0.65, 2.0, 60), lambda p: p[0] < 1.6)
    body = [[(-1.6, 2.0), (1.6, 2.0)], [(-1.6, -2.0), (1.6, -2.0)]]
    inner = ellipse(-1.6, 0.0, 0.45, 1.75, 50)
    zig = [(-1.6 + 3.2 * k / 6, 1.75 if k % 2 == 0 else -1.75) for k in range(7)]
    strap = [cubic((-1.0, 2.0), (-0.6, 3.3), (0.6, 3.3), (1.0, 2.0), 20), cubic((-0.7, 2.0), (-0.4, 2.9), (0.4, 2.9), (0.7, 2.0), 16)]
    mallets = [[(-2.9, -2.9), (-2.15, -0.85)], circle(-2.05, -0.6, 0.28, 16), [(2.9, 2.9), (2.45, 0.7)], circle(2.35, 0.45, 0.28, 16)]
    return make("Marching Bass Drum", [shell, inner, zig] + shell2 + body + strap + mallets)


@design("music_ocarina", T)
def ocarina(rng):
    body = smooth([(-2.6, 0.2), (-2.2, 1.2), (-0.8, 1.7), (1.0, 1.4), (2.3, 0.6), (2.6, -0.2), (2.0, -1.0), (0.4, -1.4), (-1.4, -1.2), (-2.4, -0.6)], closed=True)
    mouth = [rrect(-3.4, -0.1, -2.4, 0.45, 0.12)]
    window = rect(-1.9, 0.6, -1.4, 0.95)
    holes = [circle(x, y, r, 16) for x, y, r in [(-0.6, 0.6, 0.22), (0.1, 0.75, 0.2), (0.8, 0.6, 0.2), (1.5, 0.3, 0.18), (-0.2, -0.4, 0.17), (0.6, -0.5, 0.17)]]
    pattern = [wave(-1.8, 1.8, -0.95, 0.12, 3, 50)]
    st, hi = notes([("e", -1.6, 2.1, 0.55), ("b", 0.4, 2.3, 0.45), ("e", 2.3, 1.4, 0.5)])
    return make("Clay Ocarina", [body, window] + mouth + holes + pattern + st, hi)
