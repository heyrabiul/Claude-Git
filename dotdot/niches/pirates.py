"""Pirates niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "pirates"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ------------------------------------------------------------ layering helpers

def _dense(pts, step=0.03):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        d = math.dist(a, b)
        k = max(1, int(d / step))
        for i in range(1, k + 1):
            out.append((a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k))
    return out


def _bbox(m):
    xs = [p[0] for p in m]
    ys = [p[1] for p in m]
    return min(xs), min(ys), max(xs), max(ys)


def _inside(p, m, bb):
    x, y = p
    if x < bb[0] or x > bb[2] or y < bb[1] or y > bb[3]:
        return False
    c = False
    n = len(m)
    for i in range(n):
        x1, y1 = m[i]
        x2, y2 = m[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def _split(strokes, test, minlen=0.1):
    out = []
    for s in strokes:
        if len(s) < 2:
            continue
        closed = math.dist(s[0], s[-1]) < 1e-6
        segs, seg = [], []
        for p in _dense(s):
            if test(p):
                if seg:
                    segs.append(seg)
                seg = []
            else:
                seg.append(p)
        if seg:
            segs.append(seg)
        if closed and len(segs) > 1 and segs[0][0] == s[0] and segs[-1][-1] == s[-1]:
            segs[0] = segs.pop() + segs[0][1:]
        if len(segs) == 1 and len(segs[0]) == len(_dense(s)):
            out.append(s)
            continue
        for g in segs:
            if len(g) > 1 and sum(math.dist(a, b) for a, b in zip(g, g[1:])) >= minlen:
                out.append(g)
    return out


def hide(strokes, masks):
    """Remove the parts of `strokes` that lie inside any of the masks."""
    ms = [(m, _bbox(m)) for m in masks if len(m) > 2]
    if not ms:
        return [list(s) for s in strokes]
    return _split(strokes, lambda p: any(_inside(p, m, bb) for m, bb in ms))


def keep_in(strokes, mask):
    """Keep only the parts of `strokes` inside the mask."""
    bb = _bbox(mask)
    return _split(strokes, lambda p: not _inside(p, mask, bb))


def scene(*items):
    """Painter's algorithm: items are (strokes, masks) listed FRONT to BACK."""
    out, masks = [], []
    for strokes, ms in items:
        out += hide(strokes, masks)
        masks += ms
    return out


def it(*strokes):
    """A scene item whose first stroke is its own mask."""
    return (list(strokes), [strokes[0]])


def place(strokes, dx=0.0, dy=0.0, s=1.0, rot=0.0, flip=False):
    out = []
    for p in strokes:
        if flip:
            p = [(-x, y) for x, y in p]
        out.append(transform(p, dx, dy, s, rot))
    return out


def scallop(pts, amp, bumps):
    """Offset a path outward (to its left) by bumps of |sin|."""
    d = _dense(pts, 0.02)
    L = [0.0]
    for a, b in zip(d, d[1:]):
        L.append(L[-1] + math.dist(a, b))
    tot = L[-1] or 1
    out = []
    for i, (x, y) in enumerate(d):
        a = d[max(0, i - 1)]
        b = d[min(len(d) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy) or 1
        o = amp * abs(math.sin(math.pi * bumps * L[i] / tot))
        out.append((x - dy / n * o, y + dx / n * o))
    return out


# ------------------------------------------------------------ pirate parts

def skull_shape(cx, cy, s):
    """Cartoon skull: returns (strokes, mask)."""
    head = chain(arc(cx, cy + 0.25 * s, 1.0 * s, math.radians(-38), math.radians(218), 70),
                 [(cx - 0.55 * s, cy - 0.55 * s), (cx - 0.55 * s, cy - 1.0 * s), (cx + 0.55 * s, cy - 1.0 * s),
                  (cx + 0.55 * s, cy - 0.55 * s)], [arc(cx, cy + 0.25 * s, 1.0 * s, math.radians(-38), 0, 2)[0]])
    eyes = [ellipse(cx - 0.4 * s, cy + 0.1 * s, 0.27 * s, 0.31 * s, 30), ellipse(cx + 0.4 * s, cy + 0.1 * s, 0.27 * s, 0.31 * s, 30)]
    nose = poly((cx, cy - 0.25 * s), (cx - 0.14 * s, cy - 0.5 * s), (cx + 0.14 * s, cy - 0.5 * s))
    teeth = [[(cx + k * 0.28 * s, cy - 0.72 * s), (cx + k * 0.28 * s, cy - 1.0 * s)] for k in (-1, 0, 1)]
    teeth.append([(cx - 0.55 * s, cy - 0.72 * s), (cx + 0.55 * s, cy - 0.72 * s)])
    return [head] + eyes + [nose] + teeth, head


def bone(p0, p1, w):
    """Closed outline of a cartoon bone from p0 to p1 with knobbly ends."""
    L = math.dist(p0, p1)
    r, k = 0.6 * w, 0.55 * w
    xe = L - r
    end = chain(arc(xe, k, r, math.radians(185), math.radians(-66), 20), arc(xe, -k, r, math.radians(66), math.radians(-185), 20))
    start = [(L - x, -y) for x, y in end]
    pts = chain(end, start, [end[0]])
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    return transform(pts, p0[0], p0[1], 1.0, a)


def skull_and_bones(cx, cy, s):
    sk, mask = skull_shape(cx, cy + 0.1 * s, s)
    b1 = bone((cx - 1.6 * s, cy - 1.4 * s), (cx + 1.6 * s, cy + 1.2 * s), 0.32 * s)
    b2 = bone((cx + 1.6 * s, cy - 1.4 * s), (cx - 1.6 * s, cy + 1.2 * s), 0.32 * s)
    return scene((sk, [mask]), ([b1], [b1]), ([b2], [b2])), [mask, b1, b2]


def mini_skull(cx, cy, r):
    """Small emblem skull (for flags and hats)."""
    head = chain(arc(cx, cy + 0.15 * r, r, math.radians(-40), math.radians(220), 30),
                 [(cx - 0.5 * r, cy - 0.75 * r), (cx + 0.5 * r, cy - 0.75 * r)], [arc(cx, cy + 0.15 * r, r, math.radians(-40), 0, 2)[0]])
    xb = [[(cx - 1.4 * r, cy - 1.2 * r), (cx + 1.4 * r, cy + 0.9 * r)], [(cx + 1.4 * r, cy - 1.2 * r), (cx - 1.4 * r, cy + 0.9 * r)]]
    return [head] + hide(xb, [head]), [eye(cx - 0.38 * r, cy + 0.05 * r, 0.22 * r), eye(cx + 0.38 * r, cy + 0.05 * r, 0.22 * r)]


def wavy_flag(x0, y0, w, h, waves=1.0, amp=0.12):
    top = [(x0 + w * t, y0 + amp * math.sin(TAU * waves * t)) for t in [i / 30 for i in range(31)]]
    bot = [(x0 + w * t, y0 - h + amp * math.sin(TAU * waves * t)) for t in [i / 30 for i in range(31)]]
    return chain(top, bot[::-1], [top[0]])


def sail(cx, ytop, ybot, w, belly=0.14):
    l, r = cx - w / 2, cx + w / 2
    return chain(quad((l, ytop), (l - belly, (ytop + ybot) / 2), (l + 0.05, ybot), 14),
                 quad((l + 0.05, ybot), (cx, ybot - 1.4 * belly), (r - 0.05, ybot), 16),
                 quad((r - 0.05, ybot), (r + belly, (ytop + ybot) / 2), (r, ytop), 14), [(l, ytop)])


def galleon(skull=True):
    """Three-masted pirate ship facing right, roughly x[-2.8,3.4] y[-1,4.3].
    Returns (strokes, masks)."""
    hull = chain([(-2.7, 1.05), (-1.6, 1.05), (-1.6, 0.5), (1.4, 0.5), (1.6, 0.8), (2.4, 0.8)],
                 cubic((2.4, 0.8), (2.65, 0.0), (2.3, -0.7), (1.7, -1.0), 20), [(-1.9, -1.0)],
                 cubic((-1.9, -1.0), (-2.5, -0.8), (-2.85, 0.2), (-2.7, 1.05), 20))
    wale = keep_in([cubic((-3.0, 0.05), (-1.0, -0.1), (1.0, -0.1), (2.8, 0.15), 40)], hull)
    rail = [poly((-2.7, 1.05), (-2.75, 1.35), (-1.6, 1.35), (-1.6, 1.05), closed=False),
            poly((1.6, 0.8), (1.6, 1.05), (2.45, 1.05), (2.4, 0.8), closed=False)]
    ports = [rect(x - 0.13, -0.5, x + 0.13, -0.25) for x in (-1.5, -0.75, 0.0, 0.75, 1.5)]
    stern_win = [rect(-2.45, 0.55, -2.1, 0.8), rect(-2.0, 0.55, -1.75, 0.8)]
    masts = {-1.35: 3.0, 0.15: 4.0, 1.65: 3.4}
    sails = [sail(-1.35, 2.3, 1.4, 1.0), sail(-1.35, 2.85, 2.4, 0.75),
             sail(0.15, 2.2, 0.85, 1.7), sail(0.15, 3.3, 2.35, 1.3),
             sail(1.65, 2.0, 1.1, 1.2), sail(1.65, 2.95, 2.1, 0.95)]
    yards = [[(-1.35 - 0.6, 2.3), (-1.35 + 0.6, 2.3)], [(-1.35 - 0.47, 2.85), (-1.35 + 0.47, 2.85)],
             [(0.15 - 0.97, 2.2), (0.15 + 0.97, 2.2)], [(0.15 - 0.77, 3.3), (0.15 + 0.77, 3.3)],
             [(1.65 - 0.72, 2.0), (1.65 + 0.72, 2.0)], [(1.65 - 0.6, 2.95), (1.65 + 0.6, 2.95)]]
    mast_lines = [[(x, 0.5 if x < 1.5 else 0.8), (x, top)] for x, top in masts.items()]
    jib = poly((1.8, 3.1), (3.3, 1.45), (2.35, 1.15))
    bowsprit = [[(2.4, 0.9), (3.45, 1.5)]]
    flag = wavy_flag(0.15, 4.1, 0.95, 0.6, 1.0, 0.08)
    fmast = [[(0.15, 4.0), (0.15, 4.25)]]
    pennant = [poly((1.65, 3.4), (2.3, 3.28), (1.65, 3.15), closed=False), poly((-1.35, 3.0), (-1.9, 2.9), (-1.35, 2.78), closed=False)]
    extras = []
    if skull:
        sk, _ = mini_skull(0.15, 1.6, 0.32)
        extras = sk
    fsk = [circle(0.6, 3.85, 0.13, 14), [(0.4, 3.6), (0.8, 3.75)], [(0.4, 3.75), (0.8, 3.6)]]
    out = scene(([hull] + wale + rail + ports + stern_win, [hull]),
                (sails + extras, sails), (yards, []), ([flag] + fsk, [flag]),
                (mast_lines + fmast + bowsprit + pennant, []), ([jib], [jib]))
    return out, [hull, jib, flag] + sails


def water(x0, x1, y, amp=0.12, waves=6):
    return wave(x0, x1, y, amp, waves, 160)


def gull(x, y, s):
    return chain(quad((x - s, y), (x - 0.5 * s, y + 0.45 * s), (x, y)), quad((x, y), (x + 0.5 * s, y + 0.45 * s), (x + s, y)))


def palm(x, y, h, lean=0.4, s=1.0):
    """Palm tree rooted at (x, y): returns (strokes, masks)."""
    top = (x + lean * h, y + h)
    trunk_c = quad((x, y), (x + 0.1 * h, y + 0.6 * h), top, 30)
    trunk = tube(trunk_c, lambda t: (0.42 - 0.18 * t) * s)
    rings = []
    for t in (0.2, 0.38, 0.56, 0.74):
        i = int(t * 30)
        a, b = trunk_c[i], trunk_c[i + 1]
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy)
        w = (0.42 - 0.18 * t) * s / 2
        rings.append(quad((a[0] - dy / n * w, a[1] + dx / n * w), (a[0] + dx / n * 0.12, a[1] - 0.1 * s), (a[0] + dy / n * w, a[1] - dx / n * w), 8))
    fronds = []
    for ang, L, droop in [(160, 1.9, 0.9), (125, 1.6, 0.5), (85, 1.4, 0.3), (40, 1.7, 0.6), (5, 1.9, 1.0), (-30, 1.4, 0.9)]:
        a = math.radians(ang)
        end = (top[0] + L * s * math.cos(a), top[1] + L * s * math.sin(a) - droop * s)
        ctrl = (top[0] + 0.7 * L * s * math.cos(a), top[1] + 0.7 * L * s * math.sin(a) + 0.35 * s)
        c = quad(top, ctrl, end, 24)
        fronds.append(tube(c, lambda t: 0.5 * s * math.sin(math.pi * t) ** 0.8))
    nuts = [circle(top[0] - 0.15 * s, top[1] - 0.2 * s, 0.17 * s, 14), circle(top[0] + 0.18 * s, top[1] - 0.25 * s, 0.17 * s, 14)]
    out = scene((fronds, fronds), (nuts, nuts), ([trunk] + hide(rings, []), [trunk]))
    return out, fronds + nuts + [trunk]


def tricorn(cx, cy, s, emblem=True):
    """Front-view tricorn hat; (cx, cy) is the front point of the brim."""
    P = lambda x, y: (cx + x * s, cy + y * s)
    out = chain(quad(P(-1.7, 1.05), P(-0.8, 0.05), P(0, -0.15), 20), quad(P(0, -0.15), P(0.8, 0.05), P(1.7, 1.05), 20),
                quad(P(1.7, 1.05), P(1.2, 1.1), P(0.85, 1.25), 8), cubic(P(0.85, 1.25), P(0.8, 2.15), P(-0.8, 2.15), P(-0.85, 1.25), 30),
                quad(P(-0.85, 1.25), P(-1.2, 1.1), P(-1.7, 1.05), 8))
    trim = chain(quad(P(-1.7, 1.05), P(-0.7, 0.55), P(0, 0.3), 16), quad(P(0, 0.3), P(0.7, 0.55), P(1.7, 1.05), 16))
    parts, hints = [out, trim], []
    if emblem:
        sk, hints = mini_skull(cx, cy + 1.05 * s, 0.24 * s)
        parts += sk
    return parts, out, hints


def pirate_head(cx, cy, s, hat="tricorn", patch=True, beard="full", earring=True, grin=False):
    """Front-view pirate head.  Returns (strokes, masks, hints)."""
    P = lambda x, y: (cx + x * s, cy + y * s)
    face = ellipse(cx, cy, 0.9 * s, 1.05 * s, 70)
    items, hints = [], []
    if hat == "tricorn":
        h, hm, hh = tricorn(cx, cy + 0.5 * s, 0.85 * s)
        items.append((h, [hm]))
        hints += hh
    elif hat == "bandana":
        band = chain(arc(cx, cy, 0.97 * s, math.radians(12), math.radians(168), 40),
                     quad(P(-0.95, 0.2), P(0, 0.55), P(0.95, 0.2), 20))
        knot = [lens(P(0.85, 0.3), P(1.55, -0.25), 0.3), lens(P(0.85, 0.3), P(1.35, -0.55), 0.25)]
        dots = [circle(*P(-0.4, 0.7), 0.1 * s, 12), circle(*P(0.25, 0.8), 0.1 * s, 12), circle(*P(0.6, 0.55), 0.09 * s, 12)]
        items.append(([band] + dots, [band]))
        items.append((knot, knot))
    if earring:
        items.append(([circle(*P(0.95, -0.42), 0.14 * s, 16)], []))
    if beard == "full":
        moust = [chain(cubic(P(0, -0.38), P(-0.3, -0.25), P(-0.6, -0.3), P(-0.85, -0.12), 14),
                       cubic(P(-0.85, -0.12), P(-0.75, -0.55), P(-0.3, -0.6), P(0, -0.5), 14))]
        moust.append(mirror_x(moust[0], cx))
        items.append((moust, moust))
        half = cubic(P(-0.88, -0.05), P(-0.95, -1.4), P(-0.35, -2.0), P(0, -2.05), 30)
        outline = scallop(chain(half, mirror_x(half, cx)[::-1]), 0.1 * s, 9)
        bm = chain(outline, [outline[0]])
        mouth = arc(cx, cy - 0.55 * s, 0.25 * s, math.radians(200), math.radians(340), 12)
        items.append(([outline, mouth], [bm]))
    elif beard == "stubble":
        items.append(([quad(P(-0.35, -0.55), P(0, -0.75 if not grin else -0.85), P(0.35, -0.55), 14)] +
                      ([[P(-0.25, -0.62), P(0.25, -0.62)]] if grin else []), []))
        items.append(([chain(cubic(P(-0.05, -0.38), P(-0.3, -0.3), P(-0.5, -0.4), P(-0.6, -0.3), 10)),
                       chain(cubic(P(0.05, -0.38), P(0.3, -0.3), P(0.5, -0.4), P(0.6, -0.3), 10))], []))
    else:
        items.append(([quad(P(-0.3, -0.55), P(0, -0.75), P(0.3, -0.55), 12)], []))
    # eyes
    if patch:
        pm = ellipse(cx - 0.35 * s, cy + 0.12 * s, 0.27 * s, 0.22 * s, 24)
        items.append(([pm], [pm]))
        items.append(([[P(-0.58, 0.2), P(-0.9, 0.45)], [P(-0.12, 0.22), P(0.7, 0.85)]], []))
    else:
        items.append(([ellipse(cx - 0.35 * s, cy + 0.12 * s, 0.17 * s, 0.13 * s, 18)], []))
        hints.append(eye(cx - 0.35 * s, cy + 0.12 * s, 0.07 * s))
    items.append(([ellipse(cx + 0.35 * s, cy + 0.12 * s, 0.17 * s, 0.13 * s, 18),
                   [P(0.15, 0.38), P(0.55, 0.42)]] + ([[P(-0.15, 0.38), P(-0.55, 0.42)]] if not patch else []), []))
    hints.append(eye(cx + 0.35 * s, cy + 0.12 * s, 0.07 * s))
    items.append(([quad(P(-0.02, 0.05), P(0.3, -0.28), P(-0.1, -0.28), 10)], []))
    items.append(([face, arc(cx + 0.9 * s, cy - 0.05 * s, 0.18 * s, -math.pi / 2, math.pi / 2, 10)], [face]))
    masks = [m for _, ms in items for m in ms]
    return scene(*items), masks, hints


def parrot(cx, cy, s, flip=False):
    """Perched parrot facing left (feet at about cy - 1.0 s)."""
    head = circle(0, 1.0, 0.5, 40)
    beak = chain(quad((-0.38, 1.3), (-0.95, 1.3), (-0.82, 0.7), 14), quad((-0.82, 0.7), (-0.62, 0.92), (-0.42, 0.88), 8))
    low = quad((-0.45, 0.88), (-0.55, 0.7), (-0.3, 0.68), 6)
    ring = circle(-0.08, 1.12, 0.17, 16)
    body = chain(cubic((-0.42, 0.75), (-0.75, 0.0), (-0.35, -0.85), (0.15, -1.0), 24),
                 cubic((0.15, -1.0), (0.6, -0.6), (0.7, 0.3), (0.42, 0.78), 24))
    wing = chain(cubic((0.4, 0.55), (0.1, 0.3), (0.0, -0.6), (0.5, -1.3), 20), cubic((0.5, -1.3), (0.75, -0.6), (0.75, 0.2), (0.4, 0.55), 20))
    feathers = keep_in([quad((0.0, y), (0.35, y - 0.25), (0.8, y + 0.05), 10) for y in (-0.05, -0.45)], wing)
    tail = [lens((0.25, -0.9), (0.55, -2.6), 0.12), lens((0.1, -0.9), (0.15, -2.4), 0.12)]
    feet = [arc(-0.15 + dx, -1.0, 0.13, 0, math.pi, 6) for dx in (0.0, 0.32)]
    strokes = scene(([beak, low], [beak]), ([ring], [ring]), ([head], [head]), ([wing] + feathers, [wing]),
                    ([body], [body]), (tail, tail), (feet, []))
    pts = place(strokes, cx, cy, s, flip=flip)
    masks = place([beak, head, wing, body] + tail, cx, cy, s, flip=flip)
    ex = (-0.08 if not flip else 0.08)
    return pts, masks, [eye(cx + ex * s, cy + 1.12 * s, 0.07 * s)]


def coin(cx, cy, r):
    return [circle(cx, cy, r, 30), circle(cx, cy, 0.68 * r, 24)]


def coin_side(cx, cy, w, h=0.16):
    """A coin seen edge-on in a stack."""
    return rrect(cx - w, cy - h / 2, cx + w, cy + h / 2, h / 2)


def chest_closed(cx, cy, s, lock=True):
    """Front-and-side chest; (cx, cy) bottom centre."""
    P = lambda x, y: (cx + x * s, cy + y * s)
    box = rect(*P(-1.6, 0), *P(1.6, 1.5))
    lid = chain([P(-1.6, 1.5)], arc(cx, cy + 1.5 * s, 1.6 * s, math.pi, 0, 1), [P(1.6, 1.5)],
                quad(P(1.6, 1.5), P(1.6, 2.6), P(0, 2.65), 16), quad(P(0, 2.65), P(-1.6, 2.6), P(-1.6, 1.5), 16))
    straps = [[P(x, 0), P(x, 1.5)] for x in (-1.1, -0.8, 0.8, 1.1)]
    lstraps = keep_in([[P(x, 1.5), P(x, 2.9)] for x in (-1.1, -0.8, 0.8, 1.1)], lid)
    plate = rect(*P(-0.3, 0.8), *P(0.3, 1.65))
    hole = [circle(*P(0, 1.3), 0.08 * s, 10), [P(0, 1.22), P(0, 1.0)]]
    planks = [[P(-0.8, y), P(0.8, y)] for y in (0.5,)] + [[P(-1.6, 0.5), P(-1.1, 0.5)], [P(1.1, 0.5), P(1.6, 0.5)]]
    planks = hide(planks, [plate])
    out = scene(([plate] + hole, [plate]), ([box] + straps + planks, [box]), ([lid] + lstraps, [lid]))
    return out, [box, lid]


# ------------------------------------------------------------ designs

@design("pirates_galleon", T)
def ship(rng):
    g, gm = galleon()
    sea = hide([water(-3.4, 3.8, -0.8, 0.12, 7), water(-3.0, 3.4, -1.5, 0.1, 6)], gm)
    gulls = [gull(-2.4, 3.6, 0.35), gull(-1.6, 4.1, 0.28), gull(3.0, 3.4, 0.3)]
    return make("Pirate Galleon Under Full Sail", g + sea + gulls)


@design("pirates_captain_portrait", T)
def captain_portrait(rng):
    head, hm, hints = pirate_head(0, 0.6, 1.35, "tricorn", True, "full")
    coat = [chain([(-0.7, -1.4), (-1.9, -1.8), (-2.6, -2.4), (-2.8, -3.4)]), chain([(0.7, -1.4), (1.9, -1.8), (2.6, -2.4), (2.8, -3.4)])]
    lapels = [poly((-0.7, -1.6), (-1.3, -2.2), (-0.9, -2.5), (-0.5, -3.4), closed=False),
              poly((0.7, -1.6), (1.3, -2.2), (0.9, -2.5), (0.5, -3.4), closed=False)]
    buttons = [circle(x, y, 0.13, 12) for x in (-1.25, 1.25) for y in (-2.75, -3.2)]
    eps = [ellipse(sx * 2.0, -1.9, 0.75, 0.28, 30, rot=-sx * 0.38) for sx in (-1, 1)]
    fringe = [[(sx * (1.55 + 0.25 * k), -1.95 - 0.1 * k), (sx * (1.55 + 0.25 * k), -2.45 - 0.1 * k)] for sx in (-1, 1) for k in range(4)]
    body = scene(([e for e in eps], eps), (fringe + coat + lapels + buttons, []))
    return make("Pirate Captain Portrait", head + hide(body, hm), hints)


@design("pirates_parrot_on_shoulder", T)
def parrot_on_shoulder(rng):
    head, hm, hints = pirate_head(-0.7, 1.0, 1.05, "tricorn", True, "stubble")
    pr, pm, ph = parrot(1.55, 0.05, 0.95, flip=True)
    torso = [chain([(-1.2, -0.15), (-2.2, -0.5), (-2.8, -1.1), (-3.0, -3.0)]), chain([(-0.2, -0.15), (1.0, -0.6), (2.2, -0.9), (2.6, -1.5), (2.7, -3.0)])]
    neck = [[(-1.0, -0.6), (-0.7, -1.2), (-0.4, -0.6)]]
    stripes = keep_in([[(-3.2, y), (3.0, y + 0.1)] for y in (-1.5, -2.05, -2.6)],
                      poly((-2.9, -1.0), (2.6, -1.0), (2.7, -3.0), (-3.0, -3.0)))
    body = scene((pr, pm), (head, hm), (torso + neck + stripes, []))
    return make("Pirate with Parrot on Shoulder", body, hints + ph)


@design("pirates_jolly_roger", T)
def jolly_roger(rng):
    pole = [rect(-2.9, -3.2, -2.65, 3.0), circle(-2.775, 3.15, 0.18, 14)]
    flag = wavy_flag(-2.65, 2.7, 5.6, 3.9, 1.2, 0.25)
    sb, sm = skull_and_bones(0.2, 0.9, 0.85)
    rope = [[(-2.65, 2.4), (-2.5, 2.2)], [(-2.65, -0.9), (-2.5, -1.1)]]
    tear = poly((2.95, 0.2), (2.4, -0.1), (2.85, -0.4), closed=False)
    return make("Jolly Roger Flag", [flag] + sb + pole + rope + [tear], [eye(-0.14, 1.12, 0.12), eye(0.54, 1.12, 0.12)])


@design("pirates_open_chest", T)
def open_chest(rng):
    box = rect(-2.4, -2.8, 2.4, -0.6)
    lid = poly((-2.4, -0.6), (-2.1, 1.7), (2.1, 1.7), (2.4, -0.6))
    lid_in = poly((-2.05, -0.1), (-1.85, 1.35), (1.85, 1.35), (2.05, -0.1), closed=False)
    straps = [[(x, -2.8), (x, -0.6)] for x in (-1.6, 1.6)] + [[(-1.8, 1.7), (-2.0, -0.1)], [(1.8, 1.7), (2.0, -0.1)]]
    plate = rect(-0.35, -1.6, 0.35, -0.75)
    hole = [circle(0, -1.05, 0.1, 10)]
    coins = []
    for (x, y, r) in [(-1.7, -0.45, 0.45), (-0.8, -0.2, 0.5), (0.3, -0.35, 0.45), (1.3, -0.15, 0.5), (2.0, -0.5, 0.4),
                      (-1.2, 0.4, 0.42), (0.0, 0.55, 0.5), (1.0, 0.6, 0.45), (-0.5, 1.1, 0.4), (0.6, 1.25, 0.38)]:
        coins.append((coin(x, y, r), [circle(x, y, r, 30)]))
    gem = poly((-2.6, -0.2), (-2.3, 0.15), (-1.9, 0.15), (-1.6, -0.2), (-2.1, -0.65))
    pearls = [circle(1.9 + 0.32 * k, 0.1 - 0.55 * k + 0.1 * k * k, 0.16, 12) for k in range(4)]
    spill = coin(3.0, -2.6, 0.35) + coin(-3.0, -2.65, 0.3)
    out = scene(([plate] + hole, [plate]), ([gem], [gem]), (pearls, pearls), *coins[::-1],
                ([box] + straps, [box]), ([lid, lid_in], [lid]))
    return make("Open Treasure Chest of Gold", out + spill)


@design("pirates_treasure_map", T)
def treasure_map(rng):
    paper = chain(wave(-3.0, 3.0, 2.3, 0.08, 3, 60), [(3.0, 2.3)], wave(3.0, 3.0, 2.3, 0, 1, 2)[1:], [(3.1, -2.3)],
                  [(x, y) for x, y in wave(-3.0, 3.1, -2.3, 0.08, 3, 60)][::-1], [(-3.0, 2.3)])
    rolls = [ellipse(-3.0, 0.0, 0.3, 2.35, 50), ellipse(3.05, 0.0, 0.3, 2.35, 50)]
    island = polar(lambda t: 1.35 + 0.25 * math.sin(3 * t) + 0.15 * math.cos(5 * t + 1), cx=-0.3, cy=0.0, n=200)
    path = [[(-1.0 + 0.45 * k, -0.6 + 0.35 * math.sin(k)), (-0.8 + 0.45 * k, -0.5 + 0.35 * math.sin(k + 0.4))] for k in range(4)]
    x = [[(0.45, 0.5), (0.95, 1.0)], [(0.45, 1.0), (0.95, 0.5)]]
    pt, _ = palm(-1.1, -0.2, 0.9, 0.2, 0.45)
    rose = [star(2.0, -1.3, 0.65, 4, 0.3), circle(2.0, -1.3, 0.35, 20), [(2.0, -0.55), (2.0, -0.2)]]
    waves = [gull(-2.2, 1.5, 0.25), gull(-2.0, -1.6, 0.25), gull(1.8, 1.6, 0.25), gull(1.2, -2.0, 0.22)]
    ship_ = [quad((1.3, 1.2), (1.7, 0.95), (2.1, 1.2), 8), [(1.3, 1.2), (2.1, 1.2)], [(1.7, 1.2), (1.7, 1.8)], poly((1.7, 1.75), (2.05, 1.35), (1.7, 1.35))]
    out = scene((rolls, rolls), ([paper, island] + hide(path, []) + x + pt + rose + ship_ + waves, []))
    return make("Treasure Map with X Marks the Spot", out)


@design("pirates_digging", T)
def digging(rng):
    ground = [chain([(-3.4, -1.0), (-0.6, -1.0)], quad((-0.6, -1.0), (0.4, -2.9), (1.4, -1.0), 20), [(1.6, -1.0)]),
              chain([(1.6, -1.0)], quad((1.6, -1.0), (2.3, -0.2), (3.0, -1.0), 16), [(3.6, -1.0)])]
    chest, cm = chest_closed(0.4, -2.45, 0.45)
    items, hh = stick_pirate(-2.0, -1.0, 0.9)
    arms = [limb((-1.5, 1.6), (-1.0, 1.4), (-0.45, 0.85), 0.32), limb((-2.5, 1.6), (-1.6, 2.2), (-0.95, 1.6), 0.32)]
    hands = [circle(-0.4, 0.8, 0.2, 14), circle(-0.92, 1.55, 0.2, 14)]
    shovel = [tube([(-1.25, 2.05), (0.55, -1.55)], 0.14), poly((0.35, -1.35), (0.95, -1.65), (0.95, -2.3), (0.45, -2.25))]
    grip = [tube([(-1.45, 2.0), (-1.05, 2.2)], 0.18)]
    dirt = [circle(2.0, 0.5, 0.12, 10), circle(2.4, 0.9, 0.1, 10), circle(1.6, 0.9, 0.1, 10)]
    pt, pm = palm(2.7, -1.0, 3.6, -0.25, 0.85)
    out = scene((hands, hands), (arms, arms), *items, (grip + shovel, grip + shovel[:1] + [shovel[1]]), (chest, cm), (ground + dirt, []), (pt, pm))
    return make("Digging for Buried Treasure", out, hh)


@design("pirates_tricorn_hat", T)
def tricorn_hat(rng):
    h, hm, hints = tricorn(0, -1.6, 1.75)
    fc = cubic((-0.6, 1.0), (0.6, 2.6), (2.4, 2.8), (3.3, 1.2), 40)
    plume = tube(fc, lambda t: 1.0 * math.sin(math.pi * t) ** 0.6 + 0.05)
    barbs = []
    for k in range(4, 37, 4):
        x, y = fc[k]
        x2, y2 = fc[k + 2]
        dx, dy = x2 - x, y2 - y
        n = math.hypot(dx, dy)
        w = (1.0 * math.sin(math.pi * k / 40) ** 0.6) / 2
        barbs.append([(x - dy / n * w, y + dx / n * w), (x - dy / n * w * 0.45 + dx / n * 0.15, y + dx / n * w * 0.45 + dy / n * 0.15)])
    band = keep_in([quad((-1.8, 0.95), (0, 0.15), (1.8, 0.95), 30)], hm)
    out = scene((h + band, [hm]), ([plume, fc[:38]] + barbs, [plume]))
    return make("Pirate Tricorn Hat with Feather", out, hints)


def cutlass(p0, ang, L=4.6, curve=0.35, flip=False):
    """Cutlass with the hilt at p0, blade along `ang`.  Returns scene items."""
    c, sn = math.cos(ang), math.sin(ang)
    f = -1 if flip else 1
    T_ = lambda pts: [(p0[0] + x * c - f * y * sn, p0[1] + x * sn + f * y * c) for x, y in pts]
    grip = T_(rrect(-1.0, -0.15, 0.0, 0.15, 0.07))
    pommel = T_(circle(-1.15, 0, 0.18, 14))
    shell = T_(ellipse(0.08, -0.05, 0.15, 0.55, 20))
    bow = T_(tube(quad((0.05, -0.52), (-0.55, -1.0), (-1.12, -0.18), 16), 0.13))
    w = 0.2 + 0.03 * L
    blade = T_(chain(quad((0.15, 0.17), (0.6 * L, 0.17 + 0.5 * curve), (L, 0.25 + curve), 24),
                     quad((L, 0.25 + curve), (0.8 * L, -w + 0.35 * curve), (0.15, -0.19), 24), [(0.15, 0.17)]))
    fuller = T_(quad((0.5, 0.05), (0.55 * L, 0.08 + 0.45 * curve), (0.8 * L, 0.12 + 0.8 * curve), 20))
    return [([shell], [shell]), ([pommel], [pommel]), ([grip], [grip]), ([bow], [bow]), ([blade, fuller], [blade])]


@design("pirates_crossed_cutlasses", T)
def crossed_cutlasses(rng):
    a = cutlass((-2.3, -2.3), math.radians(50), 6.0, 0.9)
    b = cutlass((2.3, -2.3), math.radians(130), 6.0, 0.9, flip=True)
    sk, skm = skull_shape(0, 0.35, 0.62)
    banner = tube(wave(-2.4, 2.4, -3.1, 0.15, 1.5, 40), 0.55)
    tails = [poly((-2.4, -2.85), (-3.1, -2.95), (-2.8, -3.2), (-3.1, -3.5), (-2.4, -3.35), closed=False),
             poly((2.4, -2.85), (3.1, -2.75), (2.8, -3.05), (3.1, -3.35), (2.4, -3.35), closed=False)]
    out = scene((sk, [skm]), ([banner], [banner]), *a, *b, (tails, []))
    return make("Crossed Cutlasses and Skull", out)


@design("pirates_flintlock", T)
def flintlock(rng):
    barrel = rrect(-0.6, 0.55, 3.3, 1.05, 0.08)
    muzzle = rect(3.15, 0.45, 3.4, 1.15)
    bands = [[(1.0, 0.55), (1.0, 1.05)], [(2.2, 0.55), (2.2, 1.05)]]
    stock = chain([(1.8, 0.55), (-0.5, 0.45)], cubic((-0.5, 0.45), (-1.2, 0.3), (-1.7, -0.6), (-2.3, -1.9), 20),
                  quad((-2.3, -1.9), (-2.6, -2.5), (-2.0, -2.6), 10), [(-1.3, -2.4)],
                  cubic((-1.3, -2.4), (-1.1, -1.4), (-0.6, -0.4), (0.1, -0.1), 20), [(1.8, 0.2), (1.8, 0.55)])
    cap = poly((-2.3, -1.9), (-2.45, -2.4), (-2.05, -2.55), (-1.75, -2.45), closed=False)
    guard = chain([(0.6, -0.08)], quad((0.6, -0.08), (0.8, -0.9), (0.0, -0.75), 14), [(-0.2, -0.45)])
    trigger = quad((0.2, -0.1), (0.35, -0.5), (0.15, -0.6), 8)
    lock = rrect(-0.9, 0.0, 0.3, 0.45, 0.15)
    hammer = chain([(-0.6, 0.45)], quad((-0.8, 1.0), (-1.2, 1.4), (-1.3, 1.6), 10), [(-1.0, 1.65)], quad((-1.0, 1.65), (-0.6, 1.2), (-0.3, 0.45), 10))
    frizzen = poly((0.0, 0.45), (0.1, 1.2), (0.3, 1.2), closed=False)
    smoke = [circle(3.9, 0.85, 0.3, 20), circle(4.4, 1.1, 0.4, 20), circle(4.6, 0.5, 0.3, 20)]
    out = scene((smoke, smoke), ([muzzle], [muzzle]), ([barrel] + bands, [barrel]), ([hammer], [hammer]), ([lock], [lock]),
                ([frizzen], []), ([stock, cap], [stock]), ([guard, trigger], []))
    return make("Flintlock Pistol", out)


def cannon(cx, cy, s, ang=0.25):
    """Cannon on wheeled carriage facing right."""
    c, sn = math.cos(ang), math.sin(ang)
    R = lambda x, y: (cx + s * (x * c - y * sn), cy + s * (0.9 + x * sn + y * c))
    prof = [(-1.4, 0.0), (-1.4, 0.55), (-1.2, 0.62), (2.2, 0.38), (2.25, 0.48), (2.55, 0.48), (2.55, 0.0)]
    top = [R(x, y) for x, y in prof]
    bot = [R(x, -y) for x, y in prof][::-1]
    barrel = chain(top, bot[:-1], [top[0]])
    knob = circle(*R(-1.65, 0), 0.22 * s, 16)
    rings = [[R(x, 0.55 - 0.07 * (x + 1.2)), R(x, -0.55 + 0.07 * (x + 1.2))] for x in (-0.6, 0.6)]
    carriage = poly((cx - 2.0 * s, cy + 0.1 * s), (cx - 1.9 * s, cy + 0.85 * s), (cx + 0.8 * s, cy + 0.85 * s), (cx + 1.0 * s, cy + 0.1 * s))
    wheels = []
    for wx in (-1.3, 0.5):
        wheels += [circle(cx + wx * s, cy, 0.55 * s, 30), circle(cx + wx * s, cy, 0.15 * s, 12)]
        wheels += [[(cx + wx * s + 0.15 * s * math.cos(a), cy + 0.15 * s * math.sin(a)), (cx + wx * s + 0.55 * s * math.cos(a), cy + 0.55 * s * math.sin(a))] for a in (0.4, 0.4 + math.pi / 2, 0.4 + math.pi, 0.4 + 1.5 * math.pi)]
    items = [([knob], [knob]), ([barrel] + rings, [barrel]), ([wheels[0], wheels[1]] + wheels[2:6], [wheels[0]]),
             (wheels[6:], [wheels[6]]), ([carriage], [carriage])]
    return items, R


@design("pirates_cannon_firing", T)
def cannon_firing(rng):
    items, R = cannon(-1.3, -2.2, 1.0, 0.3)
    mx, my = R(2.55, 0)
    puff = []
    for k, (dx, dy, r) in enumerate([(0.45, 0.1, 0.45), (0.95, 0.5, 0.55), (0.9, -0.3, 0.45), (1.5, 0.15, 0.6), (1.4, 0.85, 0.45)]):
        puff.append(circle(mx + dx, my + dy, r, 30))
    cloud = puff
    ball = circle(3.4, 2.7, 0.35, 24)
    speed = [[(2.4, 2.25), (2.95, 2.5)], [(2.55, 1.95), (3.05, 2.2)]]
    flash = star(mx + 0.2, my, 0.6, 7, 0.5)
    deck = [[(-3.4, -2.75), (3.4, -2.75)], [(-3.4, -2.75), (-3.4, -3.0)]]
    pile = [circle(2.2 + dx, -2.4 + dy, 0.3, 20) for dx, dy in [(0, 0), (0.6, 0), (0.3, 0.5)]]
    out = scene(*[([c], [c]) for c in cloud], *items, ([ball] + speed, []), (pile, pile), (deck[:1], []))
    return make("Pirate Cannon Firing", out)


@design("pirates_cannonball_pyramid", T)
def cannonball_pyramid(rng):
    r = 0.62
    balls = []
    for row, n in enumerate([4, 3, 2, 1]):
        for k in range(n):
            x = (k - (n - 1) / 2) * 2 * r
            y = -2.4 + r + row * r * math.sqrt(3)
            balls.append(circle(x, y, r, 40))
            balls.append(arc(x - 0.15, y + 0.15, r * 0.55, math.radians(110), math.radians(170), 8))
    frame = poly((-2.8, -2.4), (2.8, -2.4), closed=False)
    rammer = [rect(-3.0, -2.4, -2.8, 1.8), ellipse(-2.9, 2.1, 0.35, 0.35, 20)]
    bucket = [poly((2.6, -2.4), (2.5, -0.9), (3.4, -0.9), (3.3, -2.4), closed=False), ellipse(2.95, -0.9, 0.45, 0.12, 20),
              arc(2.95, -0.9, 0.5, 0, math.pi, 16)]
    return make("Pyramid of Cannonballs", balls + [frame] + rammer + bucket)


@design("pirates_spyglass_view", T)
def spyglass_view(rng):
    a = math.radians(35)
    c, s = math.cos(a), math.sin(a)
    R = lambda x, y: (-2.9 + x * c - y * s, -2.6 + x * s + y * c)
    segs = [(0, 1.3, 0.32), (1.3, 2.4, 0.27), (2.4, 3.3, 0.22)]
    tube_parts = []
    for x0, x1, w in segs:
        tube_parts.append([R(x0, w), R(x1, w), R(x1, -w), R(x0, -w), R(x0, w)])
    rings = [[R(x, 0.36), R(x, -0.36)] for x in (0.15, 1.15)]
    lens_ = [R(-0.05, 0.38), R(0.0, 0.38)]
    view = circle(1.0, 1.0, 2.1, 120)
    g, gm = galleon()
    g = place(g, 0.85, 0.15, 0.5)
    sea = keep_in([water(-1.2, 3.2, -0.15, 0.08, 6), water(-1.2, 3.2, -0.6, 0.08, 5)], view)
    sea = hide(sea, place(gm, 0.85, 0.15, 0.5))
    cross = []
    out = scene((tube_parts[::-1] + rings, tube_parts), ([view] + g + sea + cross, [view]))
    return make("Spyglass View of a Distant Ship", out)


def ship_wheel(cx, cy, r):
    out = [circle(cx, cy, r, 100), circle(cx, cy, 0.78 * r, 90), circle(cx, cy, 0.22 * r, 24)]
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        ca, sa = math.cos(a), math.sin(a)
        n = (-sa, ca)
        w = 0.06 * r
        spoke = [(cx + 0.22 * r * ca, cy + 0.22 * r * sa), (cx + 1.25 * r * ca, cy + 1.25 * r * sa)]
        out.append(tube(spoke, 0.12 * r))
        out.append(ellipse(cx + 1.38 * r * ca, cy + 1.38 * r * sa, 0.2 * r, 0.11 * r, 16, rot=a))
    rim = [circle(cx, cy, r, 100), circle(cx, cy, 0.78 * r, 90)]
    hub = circle(cx, cy, 0.22 * r, 24)
    spokes = out[3:]
    ring_band = hide(rim, [])
    sp = hide(spokes, [hub])
    sp = [s_ for s_ in sp]
    band = chain(rim[0])
    res = [hub] + hide(spokes, [hub, ring_mask(cx, cy, r)]) + rim
    return res, [circle(cx, cy, 1.5 * r, 40)]


def ring_mask(cx, cy, r):
    outer = circle(cx, cy, r, 100)
    inner = circle(cx, cy, 0.78 * r, 90)[::-1]
    return outer + inner


@design("pirates_helm_and_flag", T)
def helm_and_flag(rng):
    w, wm = ship_wheel(0, -1.05, 1.3)
    flag = wavy_flag(-2.4, 3.7, 4.9, 2.3, 1.0, 0.18)
    sk, skh = mini_skull(0.1, 2.6, 0.5)
    pole = [rect(-2.62, -3.3, -2.4, 3.9), circle(-2.51, 4.05, 0.16, 14)]
    rope = [cubic((-2.4, 3.3), (-1.8, 2.9), (-2.2, 2.1), (-1.6, 1.6), 16)]
    out = scene((w, []), ([flag] + sk, [flag]), (pole, [pole[0]]))
    return make("Pirate Helm and Skull Flag", out, skh)


@design("pirates_anchor_rope", T)
def anchor_rope(rng):
    ring = circle(0, 2.65, 0.5, 30)
    ring_in = circle(0, 2.65, 0.3, 24)
    stock = rrect(-1.6, 1.6, 1.6, 1.95, 0.15)
    knobs = [circle(-1.8, 1.775, 0.22, 16), circle(1.8, 1.775, 0.22, 16)]
    shank = rect(-0.24, -2.4, 0.24, 2.15)
    cy0, ro, ri = -0.25, 2.35, 2.0
    a = math.radians(-22)
    rm = (ro + ri) / 2
    E = (rm * math.cos(a), cy0 + rm * math.sin(a))
    tg = (-math.sin(a), math.cos(a))
    nm = (math.cos(a), math.sin(a))
    tip = (E[0] + 0.95 * tg[0], E[1] + 0.95 * tg[1])
    bo = (E[0] + 0.6 * nm[0] - 0.2 * tg[0], E[1] + 0.6 * nm[1] - 0.2 * tg[1])
    bi = (E[0] - 0.6 * nm[0] - 0.2 * tg[0], E[1] - 0.6 * nm[1] - 0.2 * tg[1])
    right = chain(arc(0, cy0, ro, -math.pi / 2, a, 20), [bo, tip, bi], arc(0, cy0, ri, a, -math.pi / 2, 20))
    outer_r = right[:right.index(bo)]
    inner_r = right[right.index(bi) + 1:]
    left_outer = [(-x, y) for x, y in outer_r][::-1]
    left_fluke = [(-bi[0], bi[1]), (-tip[0], tip[1]), (-bo[0], bo[1])]
    left_inner = [(-x, y) for x, y in inner_r][::-1]
    arms = chain(left_outer[:-1] if False else left_outer, outer_r, [bo, tip, bi], inner_r, left_inner, left_fluke[::-1][::-1], [left_outer[0]])
    arms = chain(left_outer, outer_r[1:], [bo, tip, bi], inner_r[:-1], left_inner[1:] if False else [(-x, y) for x, y in inner_r[::-1]][1:])
    arms = chain(arms, [(-bi[0], bi[1]), (-tip[0], tip[1]), (-bo[0], bo[1])], [arms[0]])
    front, back = [], []
    turns, y0, y1 = 3.5, 1.35, -1.4
    n = 140
    ts = [i / n for i in range(n + 1)]
    pts = [(0.62 * math.sin(TAU * turns * t), y0 + (y1 - y0) * t + 0.12 * math.cos(TAU * turns * t)) for t in ts]
    seg, cur_front = [pts[0]], math.cos(0) > 0
    for i in range(1, n + 1):
        f = math.cos(TAU * turns * ts[i]) > 0
        seg.append(pts[i])
        if f != cur_front or i == n:
            (front if cur_front else back).append(tube(seg, 0.24))
            seg, cur_front = [pts[i]], f
    tail = tube(chain(pts[-1:], cubic(pts[-1], (1.2, -1.9), (2.2, -1.2), (2.4, 0.2), 20)[1:]), 0.24)
    out = scene(*[([t], [t]) for t in front], ([tail], [tail]), ([ring, ring_in], [ring]), ([stock] + knobs, [stock] + knobs),
                ([arms], [arms]), ([shank], [shank]), *[([t], [t]) for t in back])
    return make("Anchor with Rope", out)


@design("pirates_powder_keg", T)
def powder_keg(rng):
    body = chain(quad((-1.6, -2.6), (-2.2, 0.0), (-1.6, 2.0), 30), [(1.6, 2.0)], quad((1.6, 2.0), (2.2, 0.0), (1.6, -2.6), 30), [(-1.6, -2.6)])
    hoops = [quad((-1.85 + 0.05 * abs(y) ** 1.5, y), (0, y - 0.25), (1.85 - 0.05 * abs(y) ** 1.5, y), 20) for y in (-1.9, -1.5, 1.3, 0.9)]
    hoops = keep_in(hoops, body)
    top = ellipse(0, 2.0, 1.6, 0.35, 50)
    staves = keep_in([quad((x, 2.0), (x * 1.3, 0.0), (x, -2.6), 20) for x in (-0.8, 0.8)], body)
    sk, skh = mini_skull(0, -0.25, 0.45)
    label = ellipse(0, -0.3, 1.0, 0.85, 40)
    fuse = cubic((0.3, 2.0), (0.6, 2.8), (1.4, 2.4), (1.8, 3.0), 30)
    spark = star(1.95, 3.15, 0.45, 8, 0.45)
    out = scene(([spark], [spark]), ([fuse], []), ([top], [top]), ([label] + sk, [label]), ([body] + hoops + staves, [body]))
    return make("Powder Keg with Lit Fuse", out, skh)


def barrel_up(cx, cy, w, h):
    body = chain(quad((cx - w, cy), (cx - 1.25 * w, cy + h / 2), (cx - w, cy + h), 20), [(cx + w, cy + h)],
                 quad((cx + w, cy + h), (cx + 1.25 * w, cy + h / 2), (cx + w, cy), 20), [(cx - w, cy)])
    top = ellipse(cx, cy + h, w, 0.18 * w, 40)
    hoops = keep_in([quad((cx - 1.3 * w, cy + f * h), (cx, cy + f * h - 0.15 * w), (cx + 1.3 * w, cy + f * h), 16) for f in (0.15, 0.3, 0.7, 0.85)], body)
    return [top, body] + hoops, [top, body]


@design("pirates_dock_barrels", T)
def dock_barrels(rng):
    b1, m1 = barrel_up(-1.5, -2.4, 1.0, 2.4)
    b2, m2 = barrel_up(1.0, -2.4, 1.0, 2.4)
    b3, m3 = barrel_up(-0.25, 0.15, 0.95, 2.2)
    crate = rect(2.0, -2.4, 3.6, -0.8)
    crate_d = keep_in([[(2.0, -2.4), (3.6, -0.8)], [(2.0, -1.6), (3.6, -1.6)]], crate)
    rope = [spiral(-2.9, -2.1, 0.1, 0.55, 3)]
    li, lm = lantern(2.8, -0.8, 0.6)
    planks = [[(-3.4, -2.4), (3.8, -2.4)], [(-3.4, -2.8), (3.8, -2.8)]] + [[(x, -2.4), (x, -2.8)] for x in (-2.0, 0.2, 2.6)]
    out = scene(*li, (b3, m3), (b1, m1), (b2, m2), ([crate] + crate_d, [crate]), (rope, []), (planks, []))
    return make("Barrels on the Pirate Dock", out)


@design("pirates_compass", T)
def compass(rng):
    cy = -1.4
    case = circle(0, cy, 1.6, 110)
    bezel = circle(0, cy, 1.32, 100)
    rose = star(0, cy, 1.15, 4, 0.24)
    rose2 = star(0, cy, 0.75, 4, 0.32, rot=math.pi / 4)
    needle = lens((0, cy - 0.95), (0, cy + 0.95), 0.09)
    hub = circle(0, cy, 0.13, 12)
    hinge = rect(-0.35, 0.15, 0.35, 0.4)
    lid = circle(0, 1.95, 1.6, 110)
    lid_in = circle(0, 1.95, 1.32, 100)
    sk, skh = mini_skull(0, 2.05, 0.55)
    ticks = [[(1.32 * math.cos(a), cy + 1.32 * math.sin(a)), (1.6 * math.cos(a), cy + 1.6 * math.sin(a))] for a in [k * math.pi / 4 + math.pi / 8 for k in range(8)]]
    chain_ = [ellipse(1.9 + 0.38 * k, cy - 1.0 - 0.2 * k, 0.22, 0.13 if k % 2 else 0.13, 14, rot=-0.4) for k in range(0)]
    out = scene(([hub], [hub]), ([needle], [needle]), ([rose2], [rose2]), ([rose], [rose]), ([bezel], [bezel]),
                ([case] + ticks, [case]), ([hinge], [hinge]), ([lid, lid_in] + sk, [lid]))
    return make("Pirate's Brass Compass", out, skh)


@design("pirates_hook_hand", T)
def hook_hand(rng):
    sleeve = chain([(-4.2, 0.95)], quad((-4.2, 0.95), (-2.6, 0.75), (-1.3, 0.85), 12), [(-1.3, -0.85)], quad((-1.3, -0.85), (-2.6, -0.8), (-4.2, -1.1), 12))
    folds = [quad((-3.4, 0.6), (-3.0, 0.1), (-3.3, -0.4), 10), quad((-2.5, 0.55), (-2.2, 0.0), (-2.4, -0.5), 10)]
    cuff = rrect(-1.6, -1.05, -0.4, 1.05, 0.12)
    buttons = [circle(-1.0, 0.5, 0.14, 12), circle(-1.0, -0.5, 0.14, 12)]
    lace = chain([(-0.4, 0.95)], scallop([(0.05, 0.95), (0.05, -0.95)], -0.28, 5), [(-0.4, -0.95), (-0.4, 0.95)])
    lace = chain([(-0.4, 0.95), (0.05, 0.95)], scallop([(0.05, 0.95), (0.05, -0.95)], 0.28, 5), [(0.05, -0.95), (-0.4, -0.95), (-0.4, 0.95)])
    cup = chain([(0.2, 0.6)], quad((0.2, 0.6), (1.0, 0.55), (1.1, 0.3), 10), [(1.1, -0.3)], quad((1.1, -0.3), (1.0, -0.55), (0.2, -0.6), 10), [(0.2, 0.6)])
    bands = [[(0.55, 0.62), (0.55, -0.62)]]
    shaft = rect(1.1, -0.13, 2.3, 0.13)
    hc = arc(2.3, 1.0, 1.0, -math.pi / 2, math.radians(165), 50)
    hook = tube(hc, lambda t: 0.3 * (1 - t) + 0.05)
    local = scene(([hook], [hook]), ([shaft], [shaft]), ([cup] + bands, [cup]), ([lace], [lace]), ([cuff] + buttons, [cuff]),
                  ([sleeve] + folds, [sleeve]))
    return make("Captain's Hook Hand", place(local, 0.3, -0.6, 1.0, math.radians(28)))


@design("pirates_peg_leg", T)
def peg_leg(rng):
    head, hm, hints = pirate_head(0, 2.1, 0.75, "tricorn", True, "full")
    coat = poly((-0.75, 0.65), (-1.3, 0.3), (-1.5, -1.3), (-0.3, -1.2), (0.3, -1.2), (1.5, -1.3), (1.3, 0.3), (0.75, 0.65))
    belt = rect(-1.3, -0.65, 1.3, -0.35)
    buckle = rect(-0.25, -0.7, 0.25, -0.3)
    shirt = poly((-0.4, 0.6), (0, -0.35), (0.4, 0.6), closed=False)
    leg_l = poly((-0.8, -1.25), (-0.8, -2.8), (-0.25, -2.8), (-0.25, -1.25), closed=False)
    boot = poly((-0.85, -2.3), (-0.85, -3.1), (-1.5, -3.1), (-1.5, -2.9), (-0.25, -2.9), closed=False)
    boot = [rrect(-1.5, -3.15, -0.2, -2.85, 0.1), poly((-0.85, -2.85), (-0.85, -2.25), (-0.2, -2.25), (-0.2, -2.85), closed=False)]
    trouser_r = poly((0.25, -1.25), (0.3, -2.0), (0.85, -2.0), (0.8, -1.25), closed=False)
    peg = poly((0.4, -2.0), (0.5, -3.15), (0.65, -3.15), (0.75, -2.0), closed=False)
    knee = rect(0.3, -2.15, 0.85, -1.95)
    arm_l = tube([(-1.2, 0.2), (-1.8, -0.6), (-1.5, -1.0)], 0.4)
    arm_r = tube([(1.2, 0.2), (1.9, 0.6), (2.1, 1.2)], 0.4)
    sw = cutlass((2.1, 1.25), math.radians(70), 2.6, 0.2)
    out = scene((head, hm), *sw, ([arm_r], [arm_r]), ([arm_l], [arm_l]), ([buckle], [buckle]), ([belt], [belt]),
                ([coat, shirt], [coat]), (boot, [boot[0]]), ([leg_l, trouser_r, knee, peg], []))
    return make("Peg-Leg Pirate", out, hints)


@design("pirates_walk_the_plank", T)
def walk_the_plank(rng):
    hull = chain([(-3.4, 2.0), (-1.0, 2.0)], quad((-1.0, 2.0), (-0.9, -0.8), (-1.6, -2.0), 20), [(-3.4, -2.0)])
    rail = [[(-3.4, 2.5), (-1.0, 2.5)]] + [[(x, 2.0), (x, 2.5)] for x in (-3.0, -2.4, -1.8, -1.2)]
    ports = [circle(-2.2, 0.6, 0.28, 16), circle(-2.4, -0.7, 0.28, 16)]
    plank = rect(-1.0, 1.85, 2.0, 2.05)
    head, hm, hh = pirate_head(1.1, 4.0, 0.5, "bandana", False, "stubble")
    body = poly((0.7, 3.5), (0.65, 2.75), (1.55, 2.75), (1.5, 3.5))
    legs = [limb((0.85, 2.8), (0.8, 2.4), (0.75, 2.05), 0.28), limb((1.35, 2.8), (1.4, 2.4), (1.5, 2.05), 0.28)]
    arms = [limb((0.75, 3.35), (0.3, 3.4), (0.15, 3.95), 0.25), limb((1.45, 3.35), (1.9, 3.4), (2.05, 3.95), 0.25)]
    sea = hide([water(-3.4, 3.4, -1.0, 0.12, 6), water(-3.0, 3.4, -1.8, 0.1, 5)], [hull])
    fins = []
    for bx, sc in [(0.9, 1.0), (-0.5, 0.6)]:
        P = lambda x, y: (bx + x * sc, -1.0 + y * sc)
        fins.append(chain([P(0, 0)], cubic(P(0, 0), P(0.3, 0.7), P(0.8, 1.4), P(1.5, 1.6), 16), quad(P(1.5, 1.6), P(1.0, 0.8), P(1.3, 0), 12)))
    out = scene((head, hm), (arms, arms), ([body], [body]), (legs, legs), ([plank], [plank]), ([hull] + ports + rail, [hull]),
                (fins, [chain(f, [f[0]]) for f in fins]), (sea, []))
    return make("Walking the Plank", out, hh)


@design("pirates_crows_nest", T)
def crows_nest(rng):
    mast = [[(-0.2, -3.2), (-0.2, 3.2)], [(0.2, -3.2), (0.2, 3.2)]]
    basket = chain([(-1.6, 0.6)], quad((-1.6, 0.6), (-1.4, -0.6), (-1.0, -0.9), 10), [(1.0, -0.9)], quad((1.0, -0.9), (1.4, -0.6), (1.6, 0.6), 10), [(-1.6, 0.6)])
    slats = keep_in([[(x, 0.7), (x * 0.8, -1.0)] for x in (-0.8, 0.0, 0.8)], basket)
    rim = rrect(-1.75, 0.55, 1.75, 0.8, 0.1)
    head, hm, hh = pirate_head(-0.5, 1.75, 0.65, "bandana", True, "stubble")
    a = math.radians(15)
    sg = tube([(0.0, 1.85), (2.2, 2.4)], lambda t: 0.36 - 0.12 * t)
    sg_end = ellipse(2.25, 2.41, 0.12, 0.22, 16, rot=a)
    hand = circle(0.4, 1.75, 0.22, 16)
    flag = wavy_flag(-0.2, 3.9, 1.8, 0.9, 1.0, 0.1)
    fsk, fh = mini_skull(0.75, 3.45, 0.22)
    ropes = [[(-1.6, 0.55), (-3.2, -3.2)], [(1.6, 0.55), (3.2, -3.2)], [(-1.2, 0.55), (-2.2, -3.2)], [(1.2, 0.55), (2.2, -3.2)]]
    ratlines = keep_in([[(-3.4, y), (3.4, y)] for y in (-0.6, -1.4, -2.2, -3.0)], poly((-1.6, 0.55), (-3.2, -3.2), (-2.2, -3.2), (-1.2, 0.55))) + \
        keep_in([[(-3.4, y), (3.4, y)] for y in (-0.6, -1.4, -2.2, -3.0)], poly((1.6, 0.55), (3.2, -3.2), (2.2, -3.2), (1.2, 0.55)))
    pole = [[(-0.2, 3.2), (-0.2, 4.0)]]
    out = scene(([hand], [hand]), ([sg, sg_end], [sg]), (head, hm), ([rim], [rim]), ([basket] + slats, [basket]),
                ([flag] + fsk, [flag]), (mast + pole + ropes + ratlines, []))
    return make("Lookout in the Crow's Nest", out, hh + fh)


@design("pirates_map_in_bottle", T)
def map_in_bottle(rng):
    a = math.radians(18)
    tr = lambda p: transform(p, 0, 0.3, 1.0, a)
    bottle = tr(chain([(-2.6, -0.75)], quad((-2.6, -0.75), (-2.9, 0.0), (-2.6, 0.75), 10), [(0.9, 0.75)],
                      cubic((0.9, 0.75), (1.6, 0.75), (1.8, 0.27), (2.3, 0.27), 14), [(2.6, 0.27), (2.6, -0.27), (2.3, -0.27)],
                      cubic((2.3, -0.27), (1.8, -0.27), (1.6, -0.75), (0.9, -0.75), 14), [(-2.6, -0.75)]))
    cork = tr(rrect(2.6, -0.22, 3.25, 0.22, 0.06))
    scroll = tr(rect(-2.1, -0.42, 0.4, 0.42))
    ribbon = tr([(-0.9, -0.42), (-0.9, 0.42)])
    ends = [tr(ellipse(x, 0, 0.13, 0.42, 16)) for x in (-2.1, 0.4)]
    shine = [tr(quad((-1.8, 0.6), (-0.5, 0.65), (0.7, 0.6), 10))]
    sand = [chain(wave(-3.4, 0.6, -1.6, 0.06, 2, 40), quad((0.6, -1.6), (1.6, -1.4), (3.4, -2.0), 16))]
    sea = [water(0.8, 3.4, -2.5, 0.1, 3), water(-3.4, 3.4, -3.0, 0.1, 6)]
    shell = [chain(arc(-2.2, -2.2, 0.4, 0, math.pi, 12), [(-2.2, -2.5), (-1.8, -2.2)])] + \
        [[(-2.2, -2.5), (-2.2 + 0.4 * math.cos(t), -2.2 + 0.4 * math.sin(t))] for t in (0.8, 1.57, 2.35)]
    out = scene(([cork], [cork]), (ends, ends), ([ribbon], []), ([scroll], [scroll]), ([bottle] + shine, [bottle]), (sand + sea + shell, []))
    return make("Treasure Map in a Bottle", out)


@design("pirates_treasure_island", T)
def treasure_island(rng):
    isl = chain([(-3.0, -1.0)], cubic((-3.0, -1.0), (-2.2, 0.4), (1.8, 0.5), (3.0, -1.0), 40))
    p1, m1 = palm(-1.4, 0.1, 2.6, 0.25, 0.8)
    p2, m2 = palm(0.5, 0.25, 2.0, -0.35, 0.65)
    ch, cm = chest_closed(1.75, -0.35, 0.38)
    x = [[(-0.6, -0.55), (-0.1, -0.2)], [(-0.6, -0.2), (-0.1, -0.55)]]
    sun = [circle(2.6, 2.6, 0.5, 30)]
    sea = [water(-3.6, 3.6, -1.0, 0.1, 7), water(-3.2, 3.2, -1.7, 0.1, 6), water(-3.6, 2.6, -2.4, 0.1, 5)]
    out = scene((ch, cm), (p2, m2), (p1, m1), ([isl] + x + sun + sea, []))
    out += [gull(-2.6, 2.4, 0.3), gull(1.6, 3.0, 0.25)]
    return make("Treasure Island", out)


@design("pirates_skull_rock", T)
def skull_rock(rng):
    rock = chain([(-3.0, -1.2)], cubic((-3.0, -1.2), (-3.4, 2.2), (-1.5, 3.2), (0.0, 3.2), 30),
                 cubic((0.0, 3.2), (1.5, 3.2), (3.4, 2.2), (3.0, -1.2), 30))
    sockets = [chain(cubic((-2.0, 1.4), (-2.0, 2.3), (-0.6, 2.3), (-0.5, 1.3), 16), quad((-0.5, 1.3), (-1.2, 0.6), (-2.0, 1.4), 12)),
               chain(cubic((2.0, 1.4), (2.0, 2.3), (0.6, 2.3), (0.5, 1.3), 16), quad((0.5, 1.3), (1.2, 0.6), (2.0, 1.4), 12))]
    nose = poly((0, 0.9), (-0.35, 0.2), (0.35, 0.2))
    mouth = chain([(-1.6, -1.2)], cubic((-1.6, -1.2), (-1.5, -0.1), (1.5, -0.1), (1.6, -1.2), 30))
    teeth = keep_in([[(x, -0.2), (x, -0.75)] for x in (-0.9, -0.3, 0.3, 0.9)], chain(mouth, [mouth[0]]))
    cracks = [poly((-2.6, 2.3), (-2.2, 2.6), (-2.3, 3.0), closed=False), poly((2.7, 0.2), (2.3, -0.1), (2.5, -0.5), closed=False)]
    boat = chain(quad((0.8, -2.0), (1.9, -2.9), (3.0, -2.0), 16), [(0.8, -2.0)])
    oars = [[(1.4, -1.9), (0.6, -2.9)], [(2.4, -1.9), (3.3, -2.8)]]
    seat = [[(1.3, -2.2), (2.5, -2.2)]]
    sea = [water(-3.6, 3.6, -1.3, 0.1, 7), water(-3.4, 3.4, -2.2, 0.1, 6), water(-3.6, 3.6, -3.0, 0.1, 7)]
    out = scene(([boat] + seat, [boat]), (oars, []), ([rock, nose, mouth] + sockets + teeth + cracks, []), (sea, []))
    out += [gull(-2.2, 3.4, 0.3), gull(2.4, 3.6, 0.25)]
    return make("Skull Rock Pirate Hideout", out)


@design("pirates_kraken", T)
def kraken(rng):
    g, gm = galleon(skull=True)
    g = place(g, 0.0, 0.2, 0.62)
    gm = place(gm, 0.0, 0.2, 0.62)
    tents = []
    for (x0, x1, ytop, curl) in [(-3.2, -2.4, 2.6, 1), (3.0, 2.3, 2.2, -1), (-1.8, -1.2, 1.4, -1), (1.6, 2.6, 1.0, 1)]:
        c = cubic((x0, -1.3), (x0 - 0.4 * curl, 0.5), (x1 + 0.7 * curl, ytop - 0.6), (x1, ytop), 40)
        tip = spiral(x1 - 0.25 * curl, ytop + 0.05, 0.25, 0.05, 0.9, 20, rot=0 if curl > 0 else math.pi)
        t = tube(c, lambda u: 0.55 * (1 - u) + 0.1)
        suck = [circle(*c[k], 0.09, 10) for k in (8, 16, 24)]
        tents.append((t, suck))
    sea = [water(-3.6, 3.6, -0.6, 0.12, 7), water(-3.4, 3.4, -1.3, 0.12, 6), water(-3.6, 3.6, -2.0, 0.1, 7)]
    head = chain([(-1.2, -2.0)], cubic((-1.2, -2.0), (-1.3, -1.0), (1.3, -1.0), (1.2, -2.0), 20))
    eyes_ = [circle(-0.45, -1.45, 0.2, 14), circle(0.45, -1.45, 0.2, 14)]
    items = [([t] + [s_ for s_ in su], [t]) for t, su in tents[2:]]
    items = [(g, gm)] + items + [([t] + su, [t]) for t, su in tents[:2]]
    out = scene(*items, ([head] + eyes_, [chain(head, [head[0]])]), (sea, []))
    return make("Kraken Attacks the Pirate Ship", out, [eye(-0.45, -1.45, 0.08), eye(0.45, -1.45, 0.08)])


def limb(a, b, c, w):
    """Tube along a quadratic from a (control b) to c."""
    return tube(quad(a, b, c, 16), w)


def lantern(cx, cy, s):
    """Ship's lantern standing at (cx, cy)."""
    P = lambda pts: [(cx + x * s, cy + y * s) for x, y in pts]
    base = P(rrect(-0.75, 0, 0.75, 0.3, 0.08))
    glass = P(poly((-0.55, 0.3), (-0.68, 1.6), (0.68, 1.6), (0.55, 0.3)))
    bars = P([(-0.2, 0.3), (-0.23, 1.6)]), P([(0.2, 0.3), (0.23, 1.6)])
    cap = P(poly((-0.8, 1.6), (0.8, 1.6), (0.35, 2.2), (-0.35, 2.2)))
    chim = P(rect(-0.2, 2.2, 0.2, 2.45))
    ring = P(circle(0, 2.72, 0.27, 20))
    flame = P(lens((0, 0.75), (0, 1.4), 0.32))
    candle = P(rect(-0.17, 0.3, 0.17, 0.75))
    items = [([flame], [flame]), ([candle], [candle]), (list(bars), []), ([glass], []), ([base], [base]), ([cap], [cap]),
             ([chim], [chim]), ([ring], [])]
    return items, [base, glass, cap, chim]


@design("pirates_monkey", T)
def monkey(rng):
    head = circle(0, 1.3, 1.0, 60)
    ears = [circle(-1.1, 1.3, 0.42, 24), circle(1.1, 1.3, 0.42, 24)]
    ears_in = [circle(-1.1, 1.3, 0.24, 16), circle(1.1, 1.3, 0.24, 16)]
    face = chain(arc(-0.32, 1.45, 0.38, math.radians(40), math.radians(250), 20), quad((-0.45, 1.1), (-0.75, 0.6), (0, 0.45), 10),
                 quad((0, 0.45), (0.75, 0.6), (0.45, 1.1), 10), arc(0.32, 1.45, 0.38, math.radians(-70), math.radians(140), 20))
    face = chain(face, [face[0]])
    band = chain(arc(0, 1.3, 1.04, math.radians(20), math.radians(160), 30), quad((-0.98, 1.65), (0, 2.15), (0.98, 1.65), 20))
    knot = [lens((0.85, 1.85), (1.6, 2.4), 0.3), lens((0.85, 1.85), (1.75, 1.75), 0.25)]
    nostrils = [circle(-0.12, 0.85, 0.06, 8), circle(0.12, 0.85, 0.06, 8)]
    mouth = quad((-0.35, 0.68), (0, 0.5), (0.35, 0.68), 10)
    earring = circle(-1.25, 0.82, 0.14, 14)
    body = chain(quad((-0.6, 0.4), (-1.3, -0.4), (-1.0, -1.4), 16), [(1.0, -1.4)], quad((1.0, -1.4), (1.3, -0.4), (0.6, 0.4), 16))
    belly = ellipse(0, -0.6, 0.6, 0.7, 30)
    arm_l = limb((-0.75, 0.0), (-1.5, -0.6), (-0.6, -1.2), 0.4)
    arm_r = limb((0.75, 0.0), (1.6, 0.3), (1.9, 1.0), 0.4)
    c_ = coin(2.0, 1.35, 0.42)
    legs = [limb((-0.7, -1.3), (-1.4, -1.6), (-0.9, -2.0), 0.42), limb((0.7, -1.3), (1.4, -1.6), (0.9, -2.0), 0.42)]
    tail = tube(chain(cubic((1.0, -1.3), (2.6, -1.8), (3.0, -0.2), (2.6, 0.2), 30)), 0.22)
    bar, bm = barrel_up(0, -3.6, 1.5, 1.6)
    out = scene((c_, [c_[0]]), ([arm_r], [arm_r]), ([arm_l], [arm_l]), (knot, knot), ([band], [band]), ([earring], []),
                ([face] + nostrils + [mouth], [face]), ([head], [head]), (ears + ears_in, ears), (legs, legs), ([belly], [belly]),
                ([body], [body]), ([tail], [tail]), (bar, bm))
    return make("Pirate Monkey in a Bandana", out, [eye(-0.32, 1.42, 0.1), eye(0.32, 1.42, 0.1)])


@design("pirates_ship_lantern", T)
def ship_lantern(rng):
    items, masks = lantern(0, -2.6, 2.0)
    hook = [[(0.0, 3.9), (0.0, 3.4)], [(-1.4, 3.9), (-0.1, 3.4)]]
    beam = rect(-3.2, 3.9, 2.6, 4.35)
    glow = [[(1.6 * math.cos(a), 0.0 + 1.6 * math.sin(a)), (2.5 * math.cos(a), 0.0 + 2.5 * math.sin(a))] for a in (0.0, 0.5, -0.5, math.pi, math.pi - 0.5, math.pi + 0.5)]
    out = scene(*items, (glow, []), ([beam], [beam]), (hook, []))
    return make("Ship's Hanging Lantern", out)


@design("pirates_crown_jewels", T)
def crown_jewels(rng):
    mound = chain([(-3.2, -2.6)], cubic((-3.2, -2.6), (-2.6, 0.2), (2.6, 0.2), (3.2, -2.6), 40), [(-3.2, -2.6)])
    coins_ = []
    for x, y, r in [(-2.2, -1.9, 0.42), (-1.2, -1.5, 0.45), (1.0, -1.6, 0.45), (2.1, -2.0, 0.42), (-0.2, -2.2, 0.45), (1.6, -1.0, 0.38), (-1.8, -0.9, 0.38)]:
        coins_.append((coin(x, y, r), [circle(x, y, r, 30)]))
    band = chain([(-1.3, -0.6)], [(1.3, -0.6)], [(1.4, 0.0)], quad((1.4, 0.0), (0, 0.2), (-1.4, 0.0), 12), [(-1.3, -0.6)])
    pts = [(-1.4, 0.0), (-1.7, 1.5), (-0.75, 0.6), (0.0, 1.9), (0.75, 0.6), (1.7, 1.5), (1.4, 0.0)]
    top = chain(pts)
    crown = chain(band[:-1], [pts[0]])
    crown_shape = chain([(-1.3, -0.6), (1.3, -0.6)], pts[::-1], [(-1.3, -0.6)])
    balls = [circle(x, y + 0.2, 0.2, 14) for x, y in [(-1.7, 1.5), (0.0, 1.9), (1.7, 1.5)]]
    gems = [poly((-0.25, -0.3), (0, 0.0), (0.25, -0.3), (0, -0.55)), ellipse(-0.85, -0.3, 0.2, 0.15, 14), ellipse(0.85, -0.3, 0.2, 0.15, 14)]
    neck = [circle(-2.8 + 0.34 * k, 0.6 - 0.8 * math.sin(k / 7 * math.pi) * 1.0 - 0.1 * k, 0.16, 12) for k in range(8)]
    goblet = [chain(quad((1.9, 1.6), (1.9, 0.6), (2.5, 0.5), 10), [(2.55, 0.0), (2.2, -0.15), (3.1, -0.15), (2.75, 0.0), (2.75, 0.5)],
                    quad((2.75, 0.5), (3.3, 0.6), (3.3, 1.6), 10)), ellipse(2.6, 1.6, 0.7, 0.18, 30)]
    gem2 = [poly((-2.5, -2.9), (-2.2, -2.6), (-1.9, -2.9), (-2.2, -3.2)), star(2.9, -2.9, 0.3, 5, 0.5)]
    out = scene((gems + balls, gems + balls), ([crown_shape, [(-1.3, -0.6), (1.3, -0.6)], [(-1.4, -0.3), (1.4, -0.3)]], [crown_shape]),
                (neck, neck), (goblet, [goblet[0], goblet[1]]), *coins_, ([mound], [mound]))
    return make("Pirate Crown and Jewels", out + gem2)


@design("pirates_coin_stacks", T)
def coin_stacks(rng):
    stacks = []
    for x, n, w in [(-2.3, 6, 0.75), (-0.8, 10, 0.75), (0.7, 8, 0.75)]:
        for k in range(n):
            stacks.append(([coin_side(x, -2.6 + 0.24 * k, w, 0.24)], [coin_side(x, -2.6 + 0.24 * k, w, 0.24)]))
        stacks.append(([ellipse(x, -2.6 + 0.24 * n, w, 0.22, 30)], [ellipse(x, -2.6 + 0.24 * n, w, 0.22, 30)]))
    sack = chain([(2.25, -0.3)], cubic((2.25, -0.3), (1.2, -0.9), (1.3, -2.7), (2.0, -2.75), 20), [(3.4, -2.75)],
                 cubic((3.4, -2.75), (4.1, -2.7), (4.2, -0.9), (3.15, -0.3), 20), [(2.25, -0.3)])
    ruffle = chain([(2.25, -0.3)], quad((2.25, -0.3), (1.8, 0.2), (2.0, 0.55), 6), quad((2.0, 0.55), (2.35, 0.25), (2.6, 0.6), 6),
                   quad((2.6, 0.6), (2.85, 0.25), (3.2, 0.55), 6), quad((3.2, 0.55), (3.6, 0.2), (3.15, -0.3), 6))
    tie = [[(2.6, -0.35), (2.35, -0.9)], [(2.8, -0.35), (3.05, -0.9)]]
    big = coin(-2.7, -2.2, 0.8)
    cross = [[(-2.7, -2.55), (-2.7, -1.85)], [(-3.05, -2.2), (-2.35, -2.2)]]
    gem = poly((-1.3, 0.0), (-1.0, 0.35), (-0.6, 0.35), (-0.3, 0.0), (-0.8, -0.5))
    gem_f = [[(-1.3, 0.0), (-0.3, 0.0)], [(-1.0, 0.35), (-0.8, 0.0), (-0.6, 0.35)]]
    loose = [ellipse(-1.6, -3.0, 0.55, 0.18, 20), ellipse(0.4, -3.05, 0.55, 0.18, 20)]
    out = scene(([gem] + gem_f, [gem]), (big + cross, [big[0]]), ([ruffle], []), ([sack] + tie, [sack]), *stacks, (loose, []))
    return make("Stacks of Gold Doubloons", out)


@design("pirates_pirate_girl", T)
def pirate_girl(rng):
    face = ellipse(0, 0.6, 0.95, 1.15, 70)
    h, hm, hh = tricorn(0, 1.45, 1.05)
    fc = cubic((1.2, 2.1), (2.0, 2.4), (2.4, 3.0), (2.2, 3.7), 30)
    plume = tube(fc, lambda t: 0.8 * math.sin(math.pi * t) ** 0.7 + 0.04)
    hair_l = chain([(-0.85, 1.45)], cubic((-0.85, 1.45), (-1.6, 1.2), (-1.5, -0.5), (-1.3, -1.2), 16),
                   cubic((-1.3, -1.2), (-1.1, -1.8), (-1.7, -2.3), (-1.2, -2.6), 16), cubic((-1.2, -2.6), (-0.8, -1.8), (-0.9, -0.8), (-0.8, 0.0), 16))
    hair_r = mirror_x(hair_l)
    curls = [quad((-1.25, -0.4), (-1.0, -1.0), (-1.2, -1.6), 8), mirror_x(quad((-1.25, -0.4), (-1.0, -1.0), (-1.2, -1.6), 8))]
    eyes_ = [ellipse(-0.38, 0.75, 0.2, 0.14, 18), ellipse(0.38, 0.75, 0.2, 0.14, 18)]
    lashes = [[(x + d * 0.2, 0.86), (x + d * 0.32, 0.98)] for x in (-0.38, 0.38) for d in (-1, 1)]
    brows = [quad((-0.6, 1.05), (-0.38, 1.15), (-0.15, 1.05), 8), quad((0.15, 1.05), (0.38, 1.15), (0.6, 1.05), 8)]
    nose = quad((0.0, 0.6), (0.18, 0.25), (-0.06, 0.25), 8)
    lips = chain(quad((-0.32, -0.05), (0, 0.05), (0.32, -0.05), 8), quad((0.32, -0.05), (0, -0.3), (-0.32, -0.05), 8))
    hoops = [circle(-1.0, 0.05, 0.2, 16), circle(1.0, 0.05, 0.2, 16)]
    neck = [[(-0.35, -0.5), (-0.35, -1.1)], [(0.35, -0.5), (0.35, -1.1)]]
    blouse = [chain([(-0.35, -1.1), (-1.8, -1.6), (-2.6, -2.2), (-2.8, -3.4)]), chain([(0.35, -1.1), (1.8, -1.6), (2.6, -2.2), (2.8, -3.4)]),
              scallop([(-1.6, -1.5), (0, -2.3), (1.6, -1.5)], 0.15, 7)]
    vest = [poly((-1.6, -1.55), (-0.7, -3.4), closed=False), poly((1.6, -1.55), (0.7, -3.4), closed=False)]
    laces = [[(-0.35, -2.5 - 0.35 * k), (0.35, -2.7 - 0.35 * k)] for k in range(2)] + [[(0.35, -2.5 - 0.35 * k), (-0.35, -2.7 - 0.35 * k)] for k in range(2)]
    out = scene(([plume, fc], [plume]), (h, [hm]), (eyes_ + lashes + brows + [nose, lips], []), (hoops, []), ([face], [face]),
                ([hair_l, hair_r] + curls, [hair_l, hair_r]), (neck + blouse + vest + laces, []))
    return make("Pirate Girl with Feathered Hat", out, hh + [eye(-0.38, 0.75, 0.08), eye(0.38, 0.75, 0.08)])


@design("pirates_captains_desk", T)
def captains_desk(rng):
    top = poly((-3.4, -0.6), (3.4, -0.6), (2.8, 0.6), (-2.8, 0.6))
    front = rect(-3.4, -1.0, 3.4, -0.6)
    legs = [poly((-3.2, -1.0), (-3.0, -3.0), (-2.6, -3.0), (-2.6, -1.0), closed=False), poly((3.2, -1.0), (3.0, -3.0), (2.6, -3.0), (2.6, -1.0), closed=False)]
    drawer = [rect(-1.0, -0.95, 1.0, -0.65)]
    mp = poly((-1.6, -0.45), (1.0, -0.45), (1.3, 0.45), (-1.3, 0.45))
    xm = [[(0.0, -0.1), (0.3, 0.15)], [(0.0, 0.15), (0.3, -0.1)]]
    path = [[(-1.0 + 0.3 * k, -0.2 + 0.05 * k), (-0.85 + 0.3 * k, -0.17 + 0.05 * k)] for k in range(3)]
    isl = ellipse(-0.4, 0.05, 0.7, 0.28, 30)
    candle = [rect(-2.55, 0.0, -2.15, 1.5), ellipse(-2.35, -0.05, 0.6, 0.18, 24), lens((-2.35, 1.6), (-2.35, 2.3), 0.3)]
    drip = [quad((-2.55, 1.3), (-2.45, 1.0), (-2.4, 1.35), 6)]
    ink = [rrect(1.6, -0.1, 2.3, 0.5, 0.12), rect(1.75, 0.5, 2.15, 0.65)]
    quill = tube(cubic((1.95, 0.6), (2.2, 1.6), (2.6, 2.4), (3.2, 3.0), 30), lambda t: 0.5 * math.sin(math.pi * t) ** 0.6 + 0.03)
    hg_top = rect(-0.3, 1.9, 0.9, 2.05)
    hg_bot = rect(-0.3, 0.45, 0.9, 0.6)
    hg_glass = chain(quad((-0.15, 1.9), (-0.1, 1.25), (0.25, 1.25), 10), quad((0.25, 1.25), (-0.1, 1.25), (-0.15, 0.6), 10),
                     [(0.75, 0.6)], quad((0.75, 0.6), (0.6, 1.25), (0.35, 1.25), 10), quad((0.35, 1.25), (0.6, 1.25), (0.75, 1.9), 10), [(-0.15, 1.9)])
    posts = [[(-0.25, 0.6), (-0.25, 1.9)], [(0.85, 0.6), (0.85, 1.9)]]
    sand = [quad((0.0, 0.6), (0.3, 0.95), (0.6, 0.6), 8)]
    out = scene((candle + drip, [candle[0], candle[2]]), ([quill], [quill]), (ink, ink), ([hg_top], [hg_top]), ([hg_bot], [hg_bot]),
                (posts, []), ([hg_glass] + sand, [hg_glass]), ([mp, isl] + xm + path, [mp]), ([top], [top]), ([front] + drawer, [front]), (legs, []))
    return make("Captain's Desk with Map and Candle", out)


@design("pirates_rowboat_landing", T)
def rowboat_landing(rng):
    beach = [chain([(-3.6, -0.6)], cubic((-3.6, -0.6), (-1.0, -1.0), (0.5, -2.2), (3.6, -3.0), 30))]
    boat = chain([(-2.8, -1.2)], quad((-2.8, -1.2), (-1.8, -2.4), (0.2, -2.0), 16), [(0.5, -1.2)], [(-2.8, -1.2)])
    rim = [[(-2.6, -1.4), (0.35, -1.4)]]
    seat = [[(-1.6, -1.4), (-1.6, -1.9)], [(-0.6, -1.4), (-0.6, -2.0)]]
    oars = [tube([(-2.2, -0.6), (0.2, -1.0)], 0.12), lens((0.1, -0.98), (1.2, -1.15), 0.2)]
    rope = [cubic((0.5, -1.3), (1.2, -1.6), (1.4, -1.9), (2.0, -1.7), 16)]
    post = rect(2.0, -2.0, 2.25, -1.2)
    steps = [ellipse(2.0 + 0.5 * k, -2.4 - 0.15 * k, 0.12, 0.07, 10) for k in range(0)]
    g, gm = galleon()
    g = place(g, -1.0, 1.0, 0.42)
    gm = place(gm, -1.0, 1.0, 0.42)
    sea = hide([water(-3.6, 3.6, 0.6, 0.06, 9), water(-3.6, 3.6, 0.05, 0.06, 8)], gm)
    pt, pm = palm(2.6, -1.0, 3.6, -0.3, 0.75)
    out = scene((pt, pm), (oars, oars), ([boat] + rim + seat, [boat]), ([post], [post]), (rope, []), (g, gm), (sea + beach, []))
    return make("Rowboat Landing on the Island", out)


@design("pirates_ship_bell", T)
def ship_bell(rng):
    bell = chain([(-0.6, 2.0)], cubic((-0.6, 2.0), (-1.2, 1.9), (-1.0, 0.2), (-1.4, -0.6), 20), quad((-1.4, -0.6), (-1.9, -0.8), (-1.9, -1.0), 8),
                 [(1.9, -1.0)], quad((1.9, -1.0), (1.9, -0.8), (1.4, -0.6), 8), cubic((1.4, -0.6), (1.0, 0.2), (1.2, 1.9), (0.6, 2.0), 20), [(-0.6, 2.0)])
    bands = keep_in([[(-2, 1.6), (2, 1.6)], [(-2, -0.4), (2, -0.4)], [(-2, -0.6), (2, -0.6)]], bell)
    crown = rect(-0.3, 2.0, 0.3, 2.4)
    clapper = [[(0.0, -1.0), (0.0, -1.55)], circle(0, -1.8, 0.25, 16)]
    rope = tube(cubic((0.0, -2.05), (0.3, -2.5), (-0.3, -2.9), (0.05, -3.3), 16), 0.24)
    knot = ellipse(0.05, -3.5, 0.32, 0.26, 16)
    tassel = poly((-0.2, -3.7), (-0.35, -4.2), (0.45, -4.2), (0.3, -3.7), closed=False)
    bracket = [rect(-3.2, 2.4, 2.6, 2.8), chain([(-3.2, 1.0)], quad((-1.8, 1.1), (-1.6, 2.4), 10) if False else quad((-3.2, 1.0), (-1.8, 1.1), (-1.6, 2.4), 10))]
    wall = [rect(-3.6, -3.6, -3.2, 3.2)]
    sk, skh = mini_skull(0, 0.6, 0.5)
    out = scene(([knot], [knot]), ([rope], [rope]), (clapper, [clapper[1]]), ([bell] + bands + sk, [bell]), ([crown], [crown]),
                (bracket + wall, [])) + [tassel]
    return make("Pirate Ship's Bell", out, skh)


@design("pirates_sea_chart", T)
def sea_chart(rng):
    paper = rect(-3.4, -2.6, 3.4, 2.6)
    border = rect(-3.1, -2.3, 3.1, 2.3)
    rc = (-1.6, -0.6)
    rose = star(*rc, 1.1, 8, 0.35)
    rose_c = circle(*rc, 0.5, 30)
    lines = keep_in([[rc, (rc[0] + 9 * math.cos(a), rc[1] + 9 * math.sin(a))] for a in [k * math.pi / 4 + math.pi / 8 for k in range(8)]], border)
    lines = hide(lines, [circle(*rc, 1.15, 40)])
    coast = chain([(1.2, 2.3)], cubic((1.2, 2.3), (0.6, 1.4), (1.6, 0.8), (1.2, 0.0), 20), cubic((1.2, 0.0), (0.8, -0.8), (2.0, -1.4), (1.6, -2.3), 20))
    coast_in = [quad((1.9, 1.7), (2.4, 1.2), (2.2, 0.6), 10), circle(2.4, -0.4, 0.15, 12)]
    isle = polar(lambda t: 0.45 + 0.1 * math.sin(3 * t), cx=-0.2, cy=1.5, n=60)
    ship_ = [chain(quad((-0.3, -1.6), (0.15, -1.9), (0.6, -1.6), 8), [(-0.3, -1.6)]), [(0.15, -1.6), (0.15, -0.95)], poly((0.15, -1.0), (0.55, -1.45), (0.15, -1.45))]
    route = [[(0.7 + 0.35 * k, -1.5 + 0.28 * k), (0.9 + 0.35 * k, -1.34 + 0.28 * k)] for k in range(0)]
    out = scene(([rose, rose_c], [rose]), (ship_, [ship_[0]]), ([paper, border, coast, isle] + coast_in + lines + route, []))
    return make("Old Sea Chart with Compass Rose", out)


@design("pirates_octopus", T)
def octopus(rng):
    head = chain(arc(0, 0.9, 1.6, math.radians(-25), math.radians(205), 60), quad((-1.45, 0.2), (0, -0.6), (1.45, 0.2), 20))
    head = chain(head, [head[0]])
    h, hm, hh = tricorn(0, 1.6, 0.9, emblem=True)
    patch = ellipse(-0.55, 0.65, 0.35, 0.28, 24)
    strap = [[(-0.85, 0.8), (-1.5, 1.25)], [(-0.25, 0.8), (1.4, 1.4)]]
    ey = circle(0.55, 0.65, 0.3, 20)
    smile = arc(0, 0.2, 0.45, math.radians(205), math.radians(335), 12)
    tents = []
    for k, (ax, ay, ex, ey_, rot) in enumerate([(-1.3, -0.2, -3.0, -0.5, 1), (-0.8, -0.4, -2.2, -2.8, 1), (-0.25, -0.5, -0.7, -3.2, -1),
                                                 (0.3, -0.5, 0.6, -3.1, 1), (0.8, -0.4, 2.1, -2.9, -1), (1.3, -0.2, 3.0, -0.8, -1)]):
        c = cubic((ax, ay), (ax * 1.5, ay - 1.2), (ex - 0.3 * rot, ey_ + 0.8), (ex, ey_), 30)
        cur = spiral(ex + 0.25 * rot, ey_ + 0.05, 0.25, 0.04, 0.8, 16, rot=math.pi if rot > 0 else 0)
        tents.append(tube(c, lambda t: 0.6 * (1 - t) + 0.12))
    sword = cutlass((2.5, 1.3), math.radians(60), 2.6, 0.25)
    grip_t = tube(cubic((1.4, 0.4), (2.4, 0.2), (2.9, 0.9), (2.5, 1.3), 20), lambda t: 0.45 * (1 - t) + 0.15)
    out = scene((h, [hm]), ([patch], [patch]), (strap + [ey, smile], []), ([head], [head]), ([grip_t], [grip_t]), *sword,
                *[([t], [t]) for t in tents])
    return make("Octopus Pirate", out, hh + [eye(0.55, 0.65, 0.12)])


@design("pirates_cat", T)
def pirate_cat(rng):
    ch, cm = chest_closed(0, -3.2, 0.95)
    head = circle(0, 1.5, 1.05, 60)
    ears = [poly((-0.95, 1.85), (-1.0, 2.95), (-0.25, 2.45), closed=False), poly((0.95, 1.85), (1.0, 2.95), (0.25, 2.45), closed=False)]
    ears_in = [poly((-0.8, 2.15), (-0.85, 2.65), (-0.45, 2.4), closed=False), poly((0.8, 2.15), (0.85, 2.65), (0.45, 2.4), closed=False)]
    band = chain(arc(0, 1.5, 1.09, math.radians(18), math.radians(162), 30), quad((-1.04, 1.84), (0, 2.25), (1.04, 1.84), 20))
    knot = [lens((0.95, 2.0), (1.75, 2.55), 0.3), lens((0.95, 2.0), (1.85, 1.75), 0.25)]
    patch = ellipse(-0.4, 1.45, 0.32, 0.26, 24)
    strap = [[(-0.7, 1.55), (-1.05, 1.75)], [(-0.1, 1.55), (0.9, 2.0)]]
    eye_r = ellipse(0.4, 1.45, 0.22, 0.2, 18)
    nose = poly((-0.12, 1.1), (0.12, 1.1), (0, 0.95))
    mouth = chain(arc(-0.15, 0.95, 0.15, math.radians(0), math.radians(-160), 8)[::-1], arc(0.15, 0.95, 0.15, math.radians(-20), math.radians(-180), 8))
    mouth = [arc(-0.15, 0.95, 0.15, math.radians(-180), math.radians(0), 8), arc(0.15, 0.95, 0.15, math.radians(-180), math.radians(0), 8)]
    whisk = [[(sx * 0.45, 1.0 + d), (sx * 1.5, 1.05 + 2 * d)] for sx in (-1, 1) for d in (0.0, -0.18)]
    body = chain([(-0.6, 0.6)], cubic((-1.4, 0.0), (-1.6, -1.4), (-1.2, -0.55 - 0.0), 1) if False else cubic((-0.6, 0.6), (-1.5, 0.0), (-1.6, -0.9), (-1.2, -0.6 - 0.0), 16))
    body = chain([(-0.6, 0.6)], cubic((-0.6, 0.6), (-1.6, 0.0), (-1.7, -0.9), (-1.3, -0.55), 16), [(1.3, -0.55)],
                 cubic((1.3, -0.55), (1.7, -0.9), (1.6, 0.0), (0.6, 0.6), 16))
    paws = [ellipse(-0.45, -0.45, 0.35, 0.2, 16), ellipse(0.45, -0.45, 0.35, 0.2, 16)]
    legs = [[(-0.2, -0.3), (-0.2, 0.4)], [(0.2, -0.3), (0.2, 0.4)]]
    tail = tube(cubic((1.3, -0.4), (2.6, -0.6), (2.8, 0.8), (2.2, 1.6), 30), 0.32)
    earring = circle(-1.05, 1.0, 0.13, 12)
    out = scene((knot, knot), ([band], [band]), ([patch], [patch]), (strap + [eye_r, nose] + mouth + whisk, []), ([earring], []),
                ([head], [head]), (ears + ears_in, []), (paws, paws), (legs + [body], [body]), ([tail], [tail]), (ch, cm))
    return make("Pirate Cat on a Treasure Chest", out, [eye(0.4, 1.45, 0.09)])


@design("pirates_hourglass", T)
def hourglass(rng):
    top = rrect(-1.9, 2.4, 1.9, 2.9, 0.12)
    bot = rrect(-1.9, -2.9, 1.9, -2.4, 0.12)
    feet = [circle(-1.5, -3.1, 0.2, 14), circle(1.5, -3.1, 0.2, 14)]
    knob = [circle(0, 3.15, 0.25, 16)]
    glass = chain(cubic((-1.2, 2.4), (-1.4, 0.8), (-0.2, 0.4), (-0.15, 0.0), 24), cubic((-0.15, 0.0), (-0.2, -0.4), (-1.4, -0.8), (-1.2, -2.4), 24),
                  [(1.2, -2.4)], cubic((1.2, -2.4), (1.4, -0.8), (0.2, -0.4), (0.15, 0.0), 24), cubic((0.15, 0.0), (0.2, 0.4), (1.4, 0.8), (1.2, 2.4), 24), [(-1.2, 2.4)])
    sand_top = keep_in([[(-2, 1.0), (2, 1.0)]], glass)
    sand_bot = chain([(-1.25, -2.4)], quad((-1.0, -1.7), (0, -1.0), 10) if False else quad((-1.25, -2.4), (-0.6, -1.4), (0, -1.1), 12),
                     quad((0, -1.1), (0.6, -1.4), (1.25, -2.4), 12))
    stream = [[(0, 0.0), (0, -1.1)]]
    posts = []
    for x in (-1.65, 1.65):
        posts.append(rect(x - 0.13, -2.4, x + 0.13, 2.4))
        posts.append(ellipse(x, 1.2, 0.22, 0.3, 16))
        posts.append(ellipse(x, -1.2, 0.22, 0.3, 16))
    out = scene((posts[1:3] + posts[4:6], [posts[1], posts[2], posts[4], posts[5]]), ([posts[0], posts[3]], [posts[0], posts[3]]),
                ([top, bot] + knob + feet, [top, bot]), ([glass] + sand_top + [sand_bot] + stream, []))
    return make("Captain's Hourglass", out)


def skeleton_key(L=3.0):
    bow = chain(arc(-0.5, 0, 0.55, math.radians(25), math.radians(335), 40))
    bow_in = circle(-0.5, 0, 0.27, 20)
    top_y = bow[0][1]
    bot_y = bow[-1][1]
    out = chain(bow, [(L - 0.85, bot_y), (L - 0.85, bot_y - 0.5), (L - 0.55, bot_y - 0.5), (L - 0.55, bot_y - 0.3), (L - 0.3, bot_y - 0.3),
                      (L - 0.3, bot_y - 0.5), (L, bot_y - 0.5), (L, top_y), bow[0]])
    collar = [[(0.4, top_y), (0.4, bot_y)], [(0.6, top_y), (0.6, bot_y)]]
    return [out, bow_in] + collar, out


@design("pirates_skeleton_keys", T)
def skeleton_keys(rng):
    ring = circle(0, 1.8, 1.1, 80)
    ring2 = circle(0, 1.8, 0.88, 70)
    items = []
    for ang, L in [(-60, 3.6), (-95, 4.0), (-130, 3.4)]:
        a = math.radians(ang)
        k, km = skeleton_key(L)
        cx, cy = 1.0 * math.cos(a) + 0.5 * math.cos(a), 1.8 + 1.0 * math.sin(a) + 0.5 * math.sin(a)
        k = [transform(p, cx, cy, 1.0, a) for p in k]
        km = transform(km, cx, cy, 1.0, a)
        items.append((k, [km]))
    out = scene(items[1], items[0], items[2], ([ring, ring2], []))
    nail = [circle(0, 3.4, 0.2, 14), [(0, 3.2), (0, 2.9)]]
    return make("Ring of Skeleton Keys", out + nail)


@design("pirates_bandana_buccaneer", T)
def bandana_buccaneer(rng):
    head, hm, hints = pirate_head(0, 0.9, 1.45, "bandana", False, "stubble", True, grin=True)
    tooth = rect(0.05, -0.08, 0.3, 0.1)
    scar = [[(0.65, 1.55), (1.05, 0.95)]] + [[(0.7 + 0.13 * k, 1.38 - 0.19 * k), (0.9 + 0.13 * k, 1.5 - 0.19 * k)] for k in range(3)]
    neck = [[(-0.55, -0.45), (-0.6, -1.0)], [(0.55, -0.45), (0.6, -1.0)]]
    shirt = [chain([(-0.6, -1.0), (-2.2, -1.6), (-2.9, -2.4), (-3.0, -3.4)]), chain([(0.6, -1.0), (2.2, -1.6), (2.9, -2.4), (3.0, -3.4)]),
             poly((-0.6, -1.0), (0, -2.0), (0.6, -1.0), closed=False)]
    stripes = keep_in([[(-3.2, y), (3.2, y)] for y in (-2.1, -2.6, -3.1)], poly((-2.2, -1.6), (2.2, -1.6), (3.0, -3.4), (-3.0, -3.4)))
    stripes = hide(stripes, [poly((-0.6, -1.0), (0, -2.0), (0.6, -1.0))])
    out = scene((head + [tooth] + scar, hm), (neck + shirt + stripes, []))
    return make("Bandana Buccaneer with Gold Tooth", out, hints)


def stick_pirate(cx, cy, s, hat="bandana", patch=False, beard="stubble"):
    """Standing pirate (feet at cy) with arms as given later; returns items, head hints, joints."""
    head, hm, hh = pirate_head(cx, cy + 3.75 * s, 0.6 * s, hat, patch, beard)
    torso = poly((cx - 0.65 * s, cy + 3.1 * s), (cx + 0.65 * s, cy + 3.1 * s), (cx + 0.55 * s, cy + 1.6 * s), (cx - 0.55 * s, cy + 1.6 * s))
    belt = rect(cx - 0.6 * s, cy + 1.6 * s, cx + 0.6 * s, cy + 1.85 * s)
    stripes = keep_in([[(cx - s, cy + y * s), (cx + s, cy + y * s)] for y in (2.15, 2.5, 2.85)], torso)
    legs = [limb((cx - 0.3 * s, cy + 1.65 * s), (cx - 0.35 * s, cy + 0.9 * s), (cx - 0.45 * s, cy + 0.3 * s), 0.38 * s),
            limb((cx + 0.3 * s, cy + 1.65 * s), (cx + 0.35 * s, cy + 0.9 * s), (cx + 0.45 * s, cy + 0.3 * s), 0.38 * s)]
    boots = [rrect(cx - 0.95 * s, cy, cx - 0.25 * s, cy + 0.4 * s, 0.1 * s), rrect(cx + 0.25 * s, cy, cx + 0.95 * s, cy + 0.4 * s, 0.1 * s)]
    items = [(head, hm), ([belt], [belt]), ([torso] + stripes, [torso]), (boots, boots), (legs, legs)]
    return items, hh


def cloud(cx, cy, w):
    bumps = chain(arc(cx - 0.5 * w, cy, 0.3 * w, math.radians(180), math.radians(60), 14),
                  arc(cx, cy + 0.15 * w, 0.38 * w, math.radians(150), math.radians(20), 14),
                  arc(cx + 0.5 * w, cy, 0.3 * w, math.radians(110), math.radians(0), 14), [(cx + 0.8 * w, cy - 0.1 * w)])
    return chain(bumps, [(cx - 0.8 * w, cy - 0.1 * w), bumps[0]])


def bolt(x, y, s):
    return poly((x, y), (x - 0.35 * s, y - 0.9 * s), (x - 0.05 * s, y - 0.85 * s), (x - 0.35 * s, y - 1.8 * s), (x + 0.3 * s, y - 0.6 * s),
                (x + 0.02 * s, y - 0.65 * s), (x + 0.3 * s, y))


@design("pirates_storm", T)
def storm(rng):
    g, gm = galleon()
    rot = math.radians(-14)
    g = place(g, 0.0, 0.0, 0.72, rot)
    gm = place(gm, 0.0, 0.0, 0.72, rot)
    crest = []
    for (x0, y0, s) in [(-3.6, -1.2, 1.0), (0.4, -1.5, 1.1)]:
        P = lambda x, y: (x0 + x * s, y0 + y * s)
        crest.append(chain(cubic(P(0, -0.6), P(1.2, -0.4), P(1.8, 0.4), P(2.3, 0.9), 20), cubic(P(2.3, 0.9), P(2.9, 1.3), P(3.4, 0.6), P(2.9, 0.4), 14),
                           cubic(P(2.9, 0.4), P(2.6, 0.3), P(2.7, 0.0), P(3.2, -0.3), 10), cubic(P(3.2, -0.3), P(3.4, -0.5), P(3.6, -0.6), P(3.8, -0.6), 8)))
    sea = [chain(crest[0], crest[1][1:]) if False else c for c in crest]
    lower = [water(-3.6, 3.8, -2.4, 0.18, 4), water(-3.6, 3.8, -3.0, 0.15, 5)]
    foam = [quad((-2.6, -1.4), (-2.0, -1.2), (-1.6, -0.6), 8), quad((1.4, -1.7), (2.1, -1.4), (2.6, -0.9), 8)]
    clouds = [cloud(-2.3, 3.6, 1.6), cloud(2.4, 3.9, 1.5)]
    bolts = [bolt(-2.3, 3.4, 1.0), bolt(2.6, 3.7, 0.9)]
    out = scene((clouds, clouds), (bolts, bolts), (sea + foam, [chain(c, [(4.0, -3.0), (-3.6, -3.0), c[0]]) for c in crest]), (g, gm), (lower, []))
    return make("Pirate Ship in a Storm", out)


@design("pirates_stern_view", T)
def stern_view(rng):
    stern = chain([(-1.0, -2.0), (1.0, -2.0)], quad((1.0, -2.0), (2.3, -1.0), (2.3, 1.3), 16), quad((2.3, 1.3), (0, 2.1), (-2.3, 1.3), 20),
                  quad((-2.3, 1.3), (-2.3, -1.0), (-1.0, -2.0), 16))
    rail = chain(quad((-2.3, 1.3), (0, 2.1), (2.3, 1.3), 20))
    rail2 = quad((-2.1, 1.05), (0, 1.8), (2.1, 1.05), 20)
    wins = []
    for k in range(5):
        x = -1.6 + 0.8 * k
        wins.append(chain([(x - 0.25, 0.1)], [(x - 0.25, 0.65)], arc(x, 0.65, 0.25, math.pi, 0, 10), [(x + 0.25, 0.1), (x - 0.25, 0.1)]))
    for k in range(3):
        x = -0.8 + 0.8 * k
        wins.append(chain([(x - 0.22, -1.0)], [(x - 0.22, -0.55)], arc(x, -0.55, 0.22, math.pi, 0, 10), [(x + 0.22, -1.0), (x - 0.22, -1.0)]))
    trims = keep_in([quad((-2.6, -0.15), (0, 0.0), (2.6, -0.15), 20), quad((-2.6, -1.25), (0, -1.1), (2.6, -1.25), 20)], stern)
    rudder = rect(-0.2, -2.7, 0.2, -1.95)
    lan = []
    for sx in (-1, 1):
        it_, m = lantern(sx * 2.3, 1.3, 0.45)
        lan += it_
    mast = [[(0, 1.9), (0, 5.9)]]
    sails = [sail(0, 4.0, 2.2, 3.0, 0.2), sail(0, 5.5, 4.2, 2.2, 0.16)]
    yards = [[(-1.7, 4.0), (1.7, 4.0)], [(-1.3, 5.5), (1.3, 5.5)]]
    flag = wavy_flag(0, 6.3, 1.4, 0.8, 1.0, 0.08)
    fs, fh = mini_skull(0.7, 5.9, 0.2)
    pole = [[(0, 5.5), (0, 6.4)]]
    sea = [water(-3.4, 3.4, -2.0, 0.12, 6), water(-3.0, 3.0, -2.7, 0.1, 5)]
    out = scene(*lan, ([rudder], [rudder]), ([stern, rail2] + wins + trims, [stern]), (yards, []), (sails, sails), ([flag] + fs, [flag]),
                (mast + pole, []), (sea, []))
    return make("Pirate Galleon Stern View", out, fh)


@design("pirates_cove", T)
def cove(rng):
    left = chain([(-3.6, -1.0)], [(-3.6, 2.6), (-3.0, 2.9), (-2.6, 2.2), (-2.0, 2.4), (-1.6, 1.4), (-1.9, 0.6), (-1.4, -0.2), (-1.0, -1.0)])
    right = chain([(3.6, -1.0)], [(3.6, 3.0), (3.0, 3.2), (2.5, 2.4), (2.0, 2.0), (1.8, 1.0), (1.3, 0.5), (1.4, -0.2), (1.0, -1.0)])
    cracks = [poly((-3.0, 1.8), (-2.6, 1.3), (-2.8, 0.8), closed=False), poly((2.9, 2.2), (2.5, 1.6), (2.7, 0.9), closed=False),
              poly((-2.6, 0.2), (-2.1, -0.3), closed=False), poly((2.4, 0.3), (2.0, -0.4), closed=False)]
    g, gm = galleon()
    g = place(g, -0.1, -0.7, 0.32)
    gm = place(gm, -0.1, -0.7, 0.32)
    sea = hide([water(-1.2, 1.3, -1.0, 0.05, 3), water(-1.4, 1.5, -1.4, 0.05, 3)], gm)
    beach = [chain([(-3.6, -1.6)], quad((-3.6, -1.6), (0, -1.9), (3.6, -1.5), 30))]
    hut = [poly((0.8, -2.4), (0.8, -3.3), (2.4, -3.3), (2.4, -2.4), closed=False), poly((0.4, -2.4), (1.6, -1.6), (2.8, -2.4)),
           rect(1.4, -3.3, 1.8, -2.75)]
    thatch = keep_in([[(1.6, -1.6), (1.6 + 0.7 * math.cos(a) * 3, -1.6 - 3 * math.sin(a))] for a in (0.6, 0.9, 1.2, 1.57, 1.9, 2.2, 2.5)], hut[1])
    pole = [[(2.6, -3.3), (2.6, -1.0)]]
    flag = wavy_flag(2.6, -1.0, 0.9, 0.55, 1.0, 0.06)
    pt, pm = palm(-2.3, -3.3, 2.4, 0.3, 0.6)
    sand = [[(-3.6, -3.3), (3.6, -3.3)]]
    out = scene((pt, pm), (hut + thatch, [hut[1], poly((0.8, -2.4), (0.8, -3.3), (2.4, -3.3), (2.4, -2.4))]), ([flag], [flag]), (pole, []),
                (g, gm), ([left, right] + cracks, []), (sea + beach + sand, []))
    return make("Hidden Pirate Cove", out)


@design("pirates_jeweled_dagger", T)
def jeweled_dagger(rng):
    blade = poly((-0.45, 0.0), (-0.42, 2.4), (0.0, 3.6), (0.42, 2.4), (0.45, 0.0))
    fuller = [[(0.0, 0.2), (0.0, 2.9)]]
    guard = chain([(-1.3, 0.0)], quad((-1.3, 0.0), (0, -0.15), (1.3, 0.0), 10), arc(1.5, 0.15, 0.25, math.radians(-140), math.radians(160), 14),
                  quad((1.27, 0.24), (0, 0.18), (-1.27, 0.24), 10), arc(-1.5, 0.15, 0.25, math.radians(20), math.radians(320), 14))
    guard = chain(guard, [guard[0]])
    gem = poly((0, 0.35), (-0.3, 0.05), (0, -0.25), (0.3, 0.05))
    grip = rect(-0.27, -2.0, 0.27, -0.1)
    wraps = keep_in([[(-0.5, -0.4 - 0.32 * k), (0.5, -0.2 - 0.32 * k)] for k in range(5)], grip)
    pommel = circle(0, -2.35, 0.42, 30)
    pgem = circle(0, -2.35, 0.2, 16)
    sheath = transform(chain([(-0.55, 0.0)], [(-0.5, 2.4)], quad((-0.5, 2.4), (0, 3.7), (0.5, 2.4), 12), [(0.55, 0.0), (-0.55, 0.0)]), 2.4, -2.5, 1.0, math.radians(-12))
    sh_dec = [transform(p, 2.4, -2.5, 1.0, math.radians(-12)) for p in [rect(-0.55, 0.2, 0.55, 0.55), circle(0, 1.5, 0.22, 14), circle(0, 2.6, 0.16, 12)]]
    blade_t = [transform(p, -0.9, -0.4, 1.0, math.radians(12)) for p in [blade] + fuller + [guard, gem, grip] + wraps + [pommel, pgem]]
    bm = [transform(p, -0.9, -0.4, 1.0, math.radians(12)) for p in [blade, guard, grip, pommel]]
    out = scene((blade_t, bm), (sh_dec, sh_dec[:1]), ([sheath], [sheath]))
    return make("Jeweled Pirate Dagger and Sheath", out)


@design("pirates_parrot_in_hat", T)
def parrot_in_hat(rng):
    pr, pm, ph = parrot(0, -0.1, 1.35)
    h, hm, hh = tricorn(0.1, 1.95, 0.5)
    bar = rrect(-2.2, -1.65, 2.2, -1.35, 0.12)
    post = rect(-0.15, -3.3, 0.15, -1.65)
    base = ellipse(0, -3.4, 1.4, 0.3, 30)
    cup = chain([(-2.2, -1.35)], [(-2.1, -0.8)], [(-1.4, -0.8), (-1.3, -1.35)])
    cracker = rect(-2.05, -0.8, -1.45, -0.55)
    out = scene((h, [hm]), (pr, pm), ([bar], [bar]), ([cup, cracker], [poly((-2.2, -1.35), (-2.1, -0.8), (-1.4, -0.8), (-1.3, -1.35))]),
                ([post], [post]), ([base], []))
    return make("Parrot in a Pirate Hat", out, ph + hh)


@design("pirates_sunset", T)
def sunset(rng):
    sun = chain(arc(0.6, -0.6, 2.4, 0, math.pi, 80), [(0.6 + 2.4, -0.6)])
    rays = [[(0.6 + 2.8 * math.cos(a), -0.6 + 2.8 * math.sin(a)), (0.6 + 3.5 * math.cos(a), -0.6 + 3.5 * math.sin(a))] for a in [math.pi * k / 8 for k in range(1, 8)]]
    g, gm = galleon()
    g = place(g, -0.9, -0.2, 0.55)
    gm = place(gm, -0.9, -0.2, 0.55)
    horizon = [[(-3.6, -0.6), (3.6, -0.6)]]
    refl = [[(0.6 - w, -0.6 - 0.35 * k), (0.6 + w, -0.6 - 0.35 * k)] for k, w in [(1, 2.0), (2, 1.5), (3, 1.0), (4, 0.6)]]
    refl = hide(refl, gm)
    sea = [water(-3.6, -1.8, -1.6, 0.06, 2), water(2.9, 3.6, -1.3, 0.05, 1)]
    gulls = [gull(-2.6, 2.4, 0.3), gull(-1.8, 2.9, 0.25), gull(2.8, 3.2, 0.25)]
    out = scene((g, gm), ([sun] + rays + horizon + refl + sea, []))
    return make("Pirate Ship at Sunset", out + gulls)


@design("pirates_ship_in_bottle", T)
def ship_in_bottle(rng):
    bottle = chain(arc(-2.6, 0.0, 1.3, math.radians(90), math.radians(270), 30), [(1.4, -1.3)],
                   cubic((1.4, -1.3), (2.2, -1.3), (2.4, -0.45), (2.9, -0.45), 16), [(3.3, -0.45), (3.3, 0.45), (2.9, 0.45)],
                   cubic((2.9, 0.45), (2.4, 0.45), (2.2, 1.3), (1.4, 1.3), 16), [(-2.6, 1.3)])
    cork = rrect(3.3, -0.38, 3.9, 0.38, 0.08)
    g, gm = galleon()
    g = place(g, -0.6, -0.45, 0.33)
    gm = place(gm, -0.6, -0.45, 0.33)
    sea = keep_in([water(-4.0, 2.0, -0.85, 0.07, 6)], bottle)
    sea = hide(sea, gm)
    shine = [quad((-2.8, 1.0), (-1.0, 1.15), (0.8, 1.1), 10)]
    cradles = [poly((x - 0.7, -2.2), (x - 0.7, -1.4), (x - 0.4, -1.4), (x, -1.2 - 0.0), (x + 0.4, -1.4), (x + 0.7, -1.4), (x + 0.7, -2.2)) for x in (-2.2, 1.0)]
    base = rrect(-3.6, -2.7, 2.6, -2.2, 0.12)
    out = scene(([cork], [cork]), (g, gm), ([bottle] + sea + shine, [bottle]), (cradles, cradles), ([base], [base]))
    return make("Pirate Ship in a Bottle", out)


@design("pirates_shipwreck", T)
def shipwreck(rng):
    hull = chain([(-3.2, -0.6)], [(-1.2, -0.3), (-0.9, 0.1), (-0.5, -0.4), (-0.2, 0.0), (0.2, -0.5)], [(0.4, -2.4)], [(-2.6, -2.4)],
                 cubic((-2.6, -2.4), (-3.2, -2.0), (-3.4, -1.0), (-3.2, -0.6), 16))
    hull = transform(hull, 0.0, 0.0, 1.0, math.radians(8))
    planks = keep_in([[(-4, y), (1, y + 0.2)] for y in (-1.0, -1.5, -2.0)], hull)
    ports = [transform(circle(x, -1.2, 0.2, 14), 0, 0, 1.0, math.radians(8)) for x in (-2.4, -1.5)]
    mast = tube([(-1.6, -0.2), (-0.8, 2.4)], 0.25)
    sail_ = chain([(-1.2, 1.2)], [(0.3, 0.8)], quad((0.3, 0.8), (0.0, 1.6), (0.4, 2.2), 8), [(-0.95, 2.0)])
    sand = [chain([(-3.6, -2.2)], quad((-3.6, -2.2), (0, -2.8), (3.6, -2.3), 30))]
    chs, chm = chest_closed(2.1, -2.65, 0.45)
    chs = place(chs, 0, 0, 1.0, math.radians(-6))
    chm = place(chm, 0, 0, 1.0, math.radians(-6))
    coins_ = [circle(1.0 + 0.45 * k, -2.75 - 0.08 * (k % 2), 0.2, 12) for k in (0, 1, 5)]
    weeds = [tube(wave(0, 2.5, 0, 0.18, 1.5, 30), lambda t: 0.3 * (1 - t) + 0.08)]
    weeds = [place([w[0] for w in [[pt] for pt in weeds[0]]] if False else weeds[0:1], dx, -2.6, s, math.pi / 2) for dx, s in [(3.2, 1.0), (-3.4, 0.8), (0.9, 0.7)]]
    weeds = [w[0] for w in weeds]
    bubbles = [circle(x, y, r, 14) for x, y, r in [(-0.6, 2.6, 0.18), (-0.4, 3.1, 0.13), (-0.7, 3.5, 0.1), (2.4, 0.3, 0.15), (2.6, 0.8, 0.12)]]
    rocks = [chain(arc(-0.2, -2.55, 0.5, 0, math.pi, 12)), chain(arc(3.2, -2.35, 0.35, 0, math.pi, 10))]
    out = scene((coins_, coins_), (chs, chm), ([hull] + planks + ports, [hull]), ([sail_], [sail_]), ([mast], [mast]),
                (weeds, weeds), (rocks + sand + bubbles, []))
    return make("Sunken Pirate Shipwreck", out)


@design("pirates_lit_bomb", T)
def lit_bomb(rng):
    ball = circle(0, -0.8, 2.3, 120)
    shine = [arc(0, -0.8, 1.8, math.radians(110), math.radians(160), 14), arc(0, -0.8, 1.8, math.radians(170), math.radians(180), 4)]
    neck = rrect(-0.65, 1.3, 0.65, 2.0, 0.1)
    neck_ring = [[(-0.65, 1.65), (0.65, 1.65)]]
    fuse = cubic((0.0, 2.0), (0.2, 2.9), (1.2, 2.4), (1.6, 3.2), 24)
    spark = star(1.75, 3.45, 0.6, 9, 0.45)
    sparks = [[(2.6, 3.4), (2.9, 3.5)], [(2.4, 4.0), (2.6, 4.25)], [(1.0, 4.1), (0.85, 4.35)]]
    xb = [bone((-1.5, -2.2), (1.5, 0.2), 0.32), bone((1.5, -2.2), (-1.5, 0.2), 0.32)]
    out = scene(([spark], [spark]), ([fuse] + sparks, []), ([neck] + neck_ring, [neck]), (xb[:1], xb[:1]), (xb[1:], xb[1:]), ([ball] + shine, [ball]))
    return make("Lit Black-Powder Bomb", out)


@design("pirates_captain_full", T)
def captain_full(rng):
    head, hm, hh = pirate_head(0, 2.6, 0.72, "tricorn", True, "full")
    coat = poly((-0.8, 1.2), (-1.0, 0.0), (-1.6, -1.7), (-0.15, -1.6), (0.15, -1.6), (1.6, -1.7), (1.0, 0.0), (0.8, 1.2))
    front = [[(0.0, 1.2), (0.0, -1.6)]]
    sash = rect(-1.0, -0.35, 1.0, -0.05)
    buttons = [circle(0.25, y, 0.08, 10) for y in (0.8, 0.4)]
    legs = [rect(-0.75, -2.6, -0.2, -1.6), rect(0.2, -2.6, 0.75, -1.6)]
    boots = [poly((-0.85, -2.2), (-0.85, -3.1), (-1.5, -3.1), (-1.5, -2.85), (-0.15, -2.85), (-0.15, -2.2)),
             poly((0.85, -2.2), (0.85, -3.1), (1.5, -3.1), (1.5, -2.85), (0.15, -2.85), (0.15, -2.2))]
    boots = [poly((-0.85, -2.1), (-0.85, -2.85), (-1.45, -2.85), (-1.45, -3.15), (-0.15, -3.15), (-0.15, -2.1)),
             poly((0.85, -2.1), (0.85, -2.85), (1.45, -2.85), (1.45, -3.15), (0.15, -3.15), (0.15, -2.1))]
    cuffs = [rect(-0.95, -2.3, -0.05, -2.05), rect(0.05, -2.3, 0.95, -2.05)]
    arm_r = limb((0.85, 1.0), (1.6, 0.9), (2.0, 1.4), 0.45)
    hand_r = circle(2.05, 1.5, 0.25, 16)
    arm_l = limb((-0.85, 1.0), (-1.8, 0.3), (-0.95, -0.2), 0.45)
    sw = cutlass((2.05, 1.5), math.radians(60), 2.7, 0.4)
    out = scene((head, hm), ([hand_r], [hand_r]), *sw, ([arm_r], [arm_r]), ([arm_l], [arm_l]), ([sash], [sash]),
                ([coat] + front + buttons, [coat]), (cuffs, cuffs), (boots, boots), (legs, []))
    return make("Pirate Captain with Raised Cutlass", out, hh)


@design("pirates_crab", T)
def crab(rng):
    body = chain(arc(0, -0.6, 2.0, math.radians(-10), math.radians(190), 60), quad((-1.97, -0.95), (0, -1.9), (1.97, -0.95), 30))
    body = chain(body, [body[0]])
    stalks = [tube([(-0.9, 1.0), (-1.2, 2.1)], 0.2), tube([(0.9, 1.0), (1.2, 2.1)], 0.2)]
    eyes_ = [circle(-1.25, 2.4, 0.38, 20), circle(1.25, 2.4, 0.38, 20)]
    patch = ellipse(1.25, 2.4, 0.4, 0.4, 20)
    strap = [[(0.9, 2.6), (0.5, 2.75)], [(1.6, 2.6), (1.9, 2.8)]]
    h, hm, hh = tricorn(0, 1.05, 0.7)
    smile = arc(0, -0.5, 0.6, math.radians(210), math.radians(330), 14)
    claws = []
    for sx in (-1, 1):
        arm = tube(quad((sx * 1.8, -0.3), (sx * 2.8, 0.2), (sx * 2.6, 1.4), 16), 0.4)
        upper = lens((sx * 2.6, 1.3), (sx * 2.2, 3.0), 0.35)
        lower = lens((sx * 2.75, 1.3), (sx * 3.3, 2.6), 0.3)
        claws.append((upper, lower, arm))
    legs = []
    for sx in (-1, 1):
        for (x0, y0, cx_, cy_, x1, y1) in [(1.8, -0.75, 2.9, -0.3, 3.4, -1.5), (1.6, -1.15, 2.6, -1.0, 2.9, -2.2), (1.2, -1.45, 2.0, -1.6, 2.1, -2.7)]:
            legs.append(limb((sx * x0, y0), (sx * cx_, cy_), (sx * x1, y1), 0.26))
    citems = []
    for u, l, a in claws:
        citems += [([u], [u]), ([l], [l]), ([a], [a])]
    out = scene((h, [hm]), ([patch], [patch]), (eyes_, eyes_), (stalks + strap, stalks), ([body, smile], [body]), *citems, (legs, legs))
    return make("Pirate Crab with Eye Patch", out, hh + [eye(-1.25, 2.4, 0.14)])


@design("pirates_doubloon", T)
def doubloon(rng):
    rim = polar(lambda t: 2.4 + 0.08 * math.sin(5 * t) + 0.06 * math.cos(9 * t + 1), cx=-0.5, cy=0.0, n=240)
    inner = polar(lambda t: 1.95 + 0.05 * math.sin(4 * t), cx=-0.5, cy=0.0, n=200)
    cr = 0.32
    cross = [(-0.5 + x, y) for x, y in [(-cr, 1.3), (cr, 1.3), (cr, cr), (1.3, cr), (1.3, -cr), (cr, -cr), (cr, -1.3), (-cr, -1.3), (-cr, -cr),
                                         (-1.3, -cr), (-1.3, cr), (-cr, cr), (-cr, 1.3)]]
    bars = [[(-0.5 + x - 0.4, y), (-0.5 + x + 0.4, y)] for x, y in [(0, 1.3), (0, -1.3)]] + [[(-0.5 + x, y - 0.4), (-0.5 + x, y + 0.4)] for x, y in [(1.3, 0), (-1.3, 0)]]
    dots = [circle(-0.5 + 0.85 * sx, 0.85 * sy, 0.18, 12) for sx in (-1, 1) for sy in (-1, 1)]
    c2 = coin(2.4, 1.9, 1.0)
    pillars = [rect(2.0, 1.4, 2.2, 2.4), rect(2.6, 1.4, 2.8, 2.4)]
    c3 = coin(2.3, -2.0, 0.85)
    c3s = [star(2.3, -2.0, 0.45, 5, 0.45)]
    out = scene(([rim, inner, chain(cross)] + hide(bars, [cross]) + dots, [rim]), (c2 + pillars, [c2[0]]), (c3 + c3s, [c3[0]]))
    return make("Spanish Gold Doubloon", out)


@design("pirates_locked_chest", T)
def locked_chest(rng):
    ch, cm = chest_closed(0, -2.8, 1.5)
    links = []
    for (p0, p1) in [((-3.0, 1.2), (3.0, -2.4)), ((3.0, 1.2), (-3.0, -2.4))]:
        n = 13
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        for k in range(n):
            t = k / (n - 1)
            x, y = p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t
            if k % 2 == 0:
                o = ellipse(x, y, 0.36, 0.22, 20, rot=ang)
                links.append(([o, ellipse(x, y, 0.2, 0.07, 14, rot=ang)], [o]))
            else:
                o = ellipse(x, y, 0.36, 0.09, 16, rot=ang)
                links.append(([o], [o]))
    shackle = tube(chain([(-0.45, -0.6)], arc(0, -0.6 + 0.0, 0.45, math.pi, 0, 20)[1:], [(0.45, -0.6)]), 0.18, cap=True)
    shackle = tube(chain([(-0.45, -1.1), (-0.45, -0.6)], arc(0, -0.6, 0.45, math.pi, 0, 20)[1:], [(0.45, -1.1)]), 0.2)
    lock = rrect(-0.75, -2.2, 0.75, -1.0, 0.15)
    hole = [circle(0, -1.5, 0.15, 12), poly((-0.08, -1.6), (-0.15, -1.9), (0.15, -1.9), (0.08, -1.6), closed=False)]
    out = scene(([lock] + hole, [lock]), ([shackle], [shackle]), *links, (ch, cm))
    return make("Locked Treasure Chest with Chains", out)


@design("pirates_treasure_cave", T)
def treasure_cave(rng):
    ceil = [(-3.6, 3.2)]
    xs = [-3.6 + 0.6 * k for k in range(13)]
    tips = []
    for k, x in enumerate(xs[:-1]):
        depth = [1.2, 0.6, 1.6, 0.8, 0.5, 1.4, 0.7, 1.1, 0.5, 1.5, 0.9, 0.6][k]
        ceil += [(x + 0.3, 3.2 - depth), (x + 0.6, 3.2 - 0.1)]
    ceiling = chain([(-3.6, 3.6)], ceil, [(3.6, 3.6)])
    walls = [chain([(-3.6, 3.2)], quad((-3.6, 3.2), (-3.0, 0.0), (-3.6, -2.6), 20)), chain([(3.6, 3.2)], quad((3.6, 3.2), (3.0, 0.0), (3.6, -2.6), 20))]
    floor = [chain([(-3.6, -2.6)], quad((-3.6, -2.6), (0, -2.2), (3.6, -2.6), 20))]
    box = rect(-1.1, -2.5, 1.1, -1.2)
    lid = poly((-1.1, -1.2), (-0.95, 0.1), (0.95, 0.1), (1.1, -1.2))
    coins_ = []
    for x, y, r in [(-0.7, -1.05, 0.3), (0.0, -0.95, 0.32), (0.7, -1.05, 0.3), (-0.35, -0.55, 0.28), (0.4, -0.55, 0.28)]:
        coins_.append((coin(x, y, r), [circle(x, y, r, 24)]))
    heap = [chain([(-3.0, -2.5)], quad((-3.0, -2.5), (-2.3, -1.4), (-1.4, -2.4), 12)), chain([(1.4, -2.4)], quad((1.4, -2.4), (2.3, -1.4), (3.0, -2.5), 12))]
    heap_c = [circle(x, y, 0.2, 14) for x, y in [(-2.5, -2.1), (-2.0, -2.15), (-2.25, -1.8), (2.0, -2.1), (2.5, -2.15), (2.25, -1.8)]]
    flame = chain(quad((-2.0, 1.0), (-2.9, 1.6), (-2.2, 2.6), 12), quad((-2.2, 2.6), (-2.1, 2.0), (-1.8, 2.2), 8), quad((-1.8, 2.2), (-1.2, 1.5), (-2.0, 1.0), 12))
    torch = [tube([(-2.4, -0.6), (-2.0, 1.0)], 0.3), flame, lens((-2.0, 1.15), (-2.0, 1.85), 0.25), rect(-2.85, -0.1, -2.15, 0.15)]
    gems = [poly((1.3, -0.4), (1.55, -0.1), (1.85, -0.4), (1.55, -0.8)), poly((-1.9, -0.6), (-1.6, -0.3), (-1.3, -0.6), (-1.6, -1.0))]
    out = scene(*coins_, ([box], [box]), ([lid], [lid]), (heap_c, heap_c), (gems, gems), (torch, [torch[0], torch[1], torch[3]]), ([ceiling] + walls + floor + heap, []))
    return make("Treasure Cave", out)


@design("pirates_rowing_treasure", T)
def rowing_treasure(rng):
    boat = chain([(-3.0, -0.5)], quad((-3.0, -0.5), (-2.4, -1.9), (0.0, -1.8), 16), quad((0.0, -1.8), (2.4, -1.9), (3.2, -0.3), 16), [(-3.0, -0.5)])
    plank = keep_in([quad((-3.4, -1.0), (0, -1.2), (3.4, -0.8), 20)], boat)
    items, hh = stick_pirate(-1.1, -2.0, 0.8)
    arms = [limb((-0.65, 0.3), (0.0, 0.0), (0.4, -0.3), 0.3), limb((-1.55, 0.3), (-0.6, 0.1), (0.3, -0.1), 0.3)]
    oar = [tube([(0.8, 0.1), (-2.8, -2.4)], 0.14), lens((-2.4, -2.1), (-3.4, -2.8), 0.25)]
    chest, cm = chest_closed(1.8, -0.75, 0.42)
    sea = [water(-3.6, 3.6, -1.6, 0.1, 6), water(-3.6, 3.6, -2.4, 0.1, 6)]
    isle = [chain([(1.8, 1.2)], quad((1.8, 1.2), (2.7, 2.0), (3.6, 1.2), 10))]
    ip, im = palm(2.7, 1.6, 1.2, 0.2, 0.35)
    flag = [[(-2.8, -0.5), (-2.9, 1.4)], wavy_flag(-2.9, 1.4, 0.8, 0.5, 1.0, 0.05)]
    out = scene((arms, arms), (oar[:1], oar[:1]), *items, (chest, cm), ([boat] + plank, [boat]), (flag, [flag[1]]), (oar[1:], oar[1:]),
                (sea, []), (ip, im), (isle, []))
    return make("Rowing Back with the Treasure", out, hh)
