"""Mermaids & Fairy Tales niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "mermaids"


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


def limb(a, b, c, w):
    """Tube along a quadratic from a (control b) to c."""
    return tube(quad(a, b, c, 16), w)


# ------------------------------------------------------------ parts

def place_items(items, dx=0.0, dy=0.0, s=1.0, rot=0.0, flip=False):
    return [(place(st, dx, dy, s, rot, flip), place(ms, dx, dy, s, rot, flip)) for st, ms in items]


def masks_of(items):
    return [m for _, ms in items for m in ms]


def fan_shell(cx, cy, r, rot=0.0, ribs=2):
    """Scallop shell with its hinge at (cx, cy), opening upward (rotated by rot)."""
    out = chain([(0, 0)], arc(0, 0.0, r, math.radians(28), math.radians(152), 24), [(0, 0)])
    out = scallop(out[1:-1], 0.08 * r, 5)
    shape = chain([(0, 0)], out, [(0, 0)])
    lines = [[(0, 0), (0.8 * r * math.cos(a), 0.8 * r * math.sin(a))] for a in [math.radians(90 + 60 * (k - (ribs - 1) / 2) / max(1, ribs - 1) * (1 if ribs > 1 else 0)) for k in range(ribs)]]
    if ribs == 1:
        lines = [[(0, 0), (0, 0.8 * r)]]
    return [transform(p, cx, cy, 1.0, rot) for p in [shape] + lines], transform(shape, cx, cy, 1.0, rot)


def girl_head(hx, hy, hs, hair="long", eyes="open", crown=None, smile=True):
    """Returns (front_items, back_items, hints) for a girl's head."""
    S = lambda pts: [(hx + x * hs, hy + y * hs) for x, y in pts]
    face = S(ellipse(0, 0, 0.55, 0.64, 60))
    front, back, hints = [], [], []
    if crown == "shell":
        sh, shm = fan_shell(0, 0.55, 0.45, 0.0, 3)
        front.append(([S(l) for l in sh], [S(shm)]))
        front.append(([S(circle(-0.45, 0.6, 0.1, 10)), S(circle(0.45, 0.6, 0.1, 10))], []))
    elif crown == "tiara":
        t = S(poly((-0.45, 0.55), (-0.32, 0.82), (-0.17, 0.66), (0, 1.02), (0.17, 0.66), (0.32, 0.82), (0.45, 0.55), (0, 0.65)))
        front.append(([t, S(circle(0, 0.8, 0.08, 10))], [t]))
    elif crown == "crown":
        c = S(poly((-0.5, 0.5), (-0.55, 1.0), (-0.28, 0.78), (0, 1.12), (0.28, 0.78), (0.55, 1.0), (0.5, 0.5)))
        front.append(([c, S([(-0.52, 0.65), (0.52, 0.65)])], [c]))
    elif crown == "flower":
        fl = []
        for k in range(5):
            a = TAU * k / 5 + 0.3
            fl.append(S(circle(0.48 + 0.16 * math.cos(a), 0.5 + 0.16 * math.sin(a), 0.12, 12)))
        ctr = S(circle(0.48, 0.5, 0.08, 10))
        front.append(([ctr], [ctr]))
        front.append((fl, fl))
    if hair in ("long", "bun", "short", "pony"):
        bl = chain(quad((-0.56, 0.12), (-0.25, 0.5), (0.25, 0.44), 12), quad((0.25, 0.44), (0.5, 0.38), (0.57, 0.1), 8))
        bm = chain(bl, arc(0, 0.05, 0.69, math.radians(-2), math.radians(182), 30), [bl[0]])
        front.append(([S(bl)], [S(bm)]))
    if eyes == "open":
        for sx in (-1, 1):
            e = S(ellipse(sx * 0.21, 0.0, 0.12, 0.15, 16))
            lash = [S([(sx * (0.21 + 0.12 * math.cos(a)), 0.15 * math.sin(a)), (sx * (0.21 + 0.19 * math.cos(a)), 0.22 * math.sin(a))]) for a in (0.5, 1.0)] if hs > 1.2 else []
            front.append(([e] + lash, []))
            hints.append(S(eye(sx * 0.21, -0.02, 0.065)))
    else:
        for sx in (-1, 1):
            front.append(([S(arc(sx * 0.21, 0.08, 0.13, math.radians(200), math.radians(340), 8))], []))
    if hs > 1.2:
        front.append(([S(quad((-0.02, -0.08), (0.08, -0.15), (-0.04, -0.17), 6))], []))
    if smile:
        front.append(([S(arc(0, -0.2, 0.17, math.radians(215), math.radians(325), 8))], []))
    else:
        front.append(([S(ellipse(0, -0.33, 0.09, 0.06, 10))], []))
    front.append(([face], [face]))
    if hair == "long":
        h = chain(arc(0, 0.05, 0.72, math.radians(-12), math.radians(192), 40),
                  scallop(cubic((-0.705, -0.1), (-0.95, -0.6), (-0.7, -1.1), (-1.05, -1.75), 20), 0.05, 4),
                  cubic((-1.05, -1.75), (-0.6, -1.5), (-0.55, -0.9), (-0.32, -0.5), 16), [(0.32, -0.5)],
                  cubic((0.32, -0.5), (0.55, -0.9), (0.6, -1.5), (1.1, -1.85), 16),
                  scallop(cubic((1.1, -1.85), (0.75, -1.1), (0.95, -0.6), (0.705, -0.1), 20), 0.05, 4))
        h = chain(h, [h[0]])
        strands = keep_in([cubic((-0.62, -0.2), (-0.85, -0.7), (-0.65, -1.1), (-0.9, -1.6), 12),
                           cubic((0.62, -0.2), (0.85, -0.7), (0.65, -1.1), (0.95, -1.65), 12)], h)
        back.append(([S(h)] + [S(p) for p in strands], [S(h)]))
    elif hair == "bun":
        h = chain(arc(0, 0.05, 0.71, math.radians(-25), math.radians(205), 40), [(0.64, -0.25)])
        bun = S(circle(0, 0.88, 0.32, 24))
        back.append(([S(h)], [S(h)]))
        back.append(([bun], [bun]))
    elif hair == "short":
        h = chain(arc(0, 0.05, 0.72, math.radians(-12), math.radians(192), 40), quad((-0.705, -0.1), (-0.85, -0.5), (-0.7, -0.62), 8),
                  [(-0.4, -0.45), (0.4, -0.45)], quad((0.7, -0.62), (0.85, -0.5), (0.705, -0.1), 8)[0:1], quad((0.7, -0.62), (0.85, -0.5), (0.705, -0.1), 8))
        h = chain(h, [h[0]])
        back.append(([S(h)], [S(h)]))
    elif hair == "pony":
        h = chain(arc(0, 0.05, 0.71, math.radians(-25), math.radians(205), 40), [(0.64, -0.25)])
        tail = S(chain(cubic((0.55, 0.55), (1.4, 0.8), (1.3, -0.4), (1.0, -1.0), 16), cubic((1.0, -1.0), (1.0, -0.3), (0.9, 0.2), (0.6, 0.3), 16)))
        back.append(([S(h)], [S(h)]))
        back.append(([tail], [tail]))
    return front, back, hints


ARM = {"down": ((0.62, 1.2), (0.98, 0.55), (0.72, -0.05)),
       "hip": ((0.62, 1.2), (1.2, 0.7), (0.5, 0.2)),
       "up": ((0.62, 1.2), (1.05, 1.8), (0.7, 2.55)),
       "out": ((0.62, 1.2), (1.2, 1.05), (1.8, 1.4)),
       "wave": ((0.62, 1.2), (1.35, 1.3), (1.4, 2.25)),
       "chest": ((0.62, 1.2), (0.85, 0.35), (0.2, 0.6)),
       "rest": ((0.62, 1.2), (1.0, 0.4), (1.3, -0.3)),
       "low": ((0.62, 1.2), (1.1, 0.8), (1.6, 0.4))}

TAILS = {"sit": ((0, -0.45), (0.5, -1.7), (1.8, -2.4), (2.9, -1.6)),
         "swim": ((0, -0.45), (0.15, -1.6), (-0.6, -2.4), (0.1, -3.5)),
         "curl": ((0, -0.45), (0.2, -1.9), (1.7, -2.1), (1.7, -0.9)),
         "drape": ((0, -0.45), (-0.2, -1.6), (-1.4, -2.0), (-2.6, -2.4)),
         "short": ((0, -0.45), (0.1, -1.2), (0.9, -1.6), (1.4, -1.1))}


def tail_items(ctrl, scales=True, width=1.24):
    c = cubic(*ctrl, 60)
    wf = lambda t: 0.2 + (width - 0.2) * (1 - t) ** 0.85 + 0.3 * math.sin(math.pi * t) * (1 - t)
    body = tube(c, wf, cap=False)
    mask = body + [body[0]]
    left0, right0 = body[0], body[-1]
    seam = scallop([right0, left0], 0.13, 4)
    E = c[-1]
    d = (c[-1][0] - c[-4][0], c[-1][1] - c[-4][1])
    L = math.hypot(*d)
    d = (d[0] / L, d[1] / L)
    fins, ribs = [], []
    for sgn in (1, -1):
        a = math.radians(50) * sgn
        v = (d[0] * math.cos(a) - d[1] * math.sin(a), d[0] * math.sin(a) + d[1] * math.cos(a))
        tip = (E[0] + 1.25 * v[0], E[1] + 1.25 * v[1])
        mid = (E[0] + 0.62 * v[0], E[1] + 0.62 * v[1])
        n = (-v[1] * sgn, v[0] * sgn)
        lobe = chain(quad(E, (mid[0] + 0.5 * n[0], mid[1] + 0.5 * n[1]), tip, 16), quad(tip, (mid[0] - 0.12 * n[0], mid[1] - 0.12 * n[1]), E, 12))
        fins.append(lobe)
        ribs.append([(E[0] + 0.25 * v[0] + 0.05 * n[0], E[1] + 0.25 * v[1] + 0.05 * n[1]), (E[0] + 0.85 * v[0] + 0.2 * n[0], E[1] + 0.85 * v[1] + 0.2 * n[1])])
    sc = []
    if scales:
        upper = tube(c[:34], lambda t: wf(t * 33 / 60) * 0.98)
        xs = [p[0] for p in upper]
        ys = [p[1] for p in upper]
        r = 0.2
        row = 0
        y = max(ys) - 0.35
        while y > min(ys):
            x = min(xs) + (r if row % 2 else 0)
            while x < max(xs):
                sc.append(arc(x, y, r, math.pi * 1.05, math.pi * 1.95, 8))
                x += 2 * r
            y -= 0.32
            row += 1
        sc = keep_in(sc, upper)
        sc = hide(sc, [scallop_mask(right0, left0)])
    items = [([body, seam] + sc, [mask]), (fins + ribs, fins)]
    return items


def scallop_mask(a, b):
    s_ = scallop([a, b], 0.13, 4)
    return chain(s_, [(b[0], b[1] + 0.3), (a[0], a[1] + 0.3), s_[0]])


def mermaid(dx=0.0, dy=0.0, s=1.0, rot=0.0, flip=False, tail="sit", arms=("down", "down"), hair="long", eyes="open", crown=None,
            head_scale=1.0, held=(), scales=True, male=False):
    """Mermaid with her head at (0, 2.2) in local units.  `held` are extra
    (strokes, masks) items drawn in front of the arms.  Returns (strokes, masks, hints)."""
    hs = head_scale
    hy = 1.55 + 0.64 * hs
    if male:
        front, back, hints = man_head(0, hy, hs, crown=crown)
    else:
        front, back, hints = girl_head(0, hy, hs, hair, eyes, crown)
    neck = [[(-0.13, 1.62), (-0.13, 1.38)], [(0.13, 1.62), (0.13, 1.38)]]
    sw = 0.85 if male else 0.72
    side = chain(quad((-0.13, 1.42), (-sw, 1.42), (-sw - 0.02, 1.12), 8), cubic((-sw - 0.02, 1.12), (-0.62, 0.6), (-0.38, 0.4), (-0.42, 0.0), 14),
                 quad((-0.42, 0.0), (-0.5, -0.25), (-0.62, -0.45), 8))
    torso_line = [side, mirror_x(side)]
    torso_mask = chain(side, mirror_x(side)[::-1], [side[0]])
    deco = []
    if not male:
        for sx in (-1, 1):
            sh, shm = fan_shell(sx * 0.27, 0.62, 0.3, 0.0, 2)
            deco.append((sh, [shm]))
    else:
        deco.append(([quad((-0.45, 0.95), (-0.2, 0.75), (0.0, 0.95), 8), quad((0.0, 0.95), (0.2, 0.75), (0.45, 0.95), 8), [(0.0, 0.6), (0.0, 0.2)]], []))
    arm_items = []
    hands = []
    for sx, pose in zip((-1, 1), arms):
        a, b, c = ARM[pose] if isinstance(pose, str) else pose
        if sx < 0:
            a, b, c = (-a[0], a[1]), (-b[0], b[1]), (-c[0], c[1])
        arm = limb(a, b, c, 0.26 if not male else 0.32)
        hand = circle(c[0], c[1], 0.14 if not male else 0.17, 12)
        hands.append(([hand], [hand]))
        arm_items.append(([arm], [arm]))
    titems = tail_items(TAILS[tail] if isinstance(tail, str) else tail, scales, 1.24 if not male else 1.4)
    items = list(held) + hands + arm_items + front + deco + [(neck + torso_line, [torso_mask])] + titems + back
    items = place_items(items, dx, dy, s, rot, flip)
    hints = place(hints, dx, dy, s, rot, flip)
    return scene(*items), masks_of(items), hints


def man_head(hx, hy, hs, crown="crown"):
    S = lambda pts: [(hx + x * hs, hy + y * hs) for x, y in pts]
    face = S(ellipse(0, 0, 0.55, 0.66, 60))
    front, back, hints = [], [], []
    if crown:
        c = S(poly((-0.5, 0.42), (-0.6, 1.05), (-0.3, 0.75), (0, 1.2), (0.3, 0.75), (0.6, 1.05), (0.5, 0.42)))
        front.append(([c, S([(-0.53, 0.6), (0.53, 0.6)])], [c]))
    moust = [S(chain(quad((0, -0.22), (-0.3, -0.18), (-0.42, -0.08), 8), quad((-0.42, -0.08), (-0.3, -0.35), (0, -0.3), 8))),
             S(chain(quad((0, -0.22), (0.3, -0.18), (0.42, -0.08), 8), quad((0.42, -0.08), (0.3, -0.35), (0, -0.3), 8)))]
    front.append((moust, moust))
    beard = S(chain([(-0.55, -0.05)], scallop(cubic((-0.55, -0.05), (-0.7, -1.0), (-0.2, -1.4), (0, -1.45), 20) + mirror_x(cubic((-0.55, -0.05), (-0.7, -1.0), (-0.2, -1.4), (0, -1.45), 20))[::-1][1:], 0.07, 8), [(0.55, -0.05)]))
    front.append(([beard], [chain(beard, [beard[0]])]))
    for sx in (-1, 1):
        front.append(([S(ellipse(sx * 0.21, 0.08, 0.11, 0.1, 14)), S([(sx * 0.08, 0.27), (sx * 0.36, 0.3)])], []))
        hints.append(S(eye(sx * 0.21, 0.07, 0.055)))
    front.append(([S(quad((-0.03, 0.05), (0.12, -0.12), (-0.05, -0.12), 6))], []))
    front.append(([face], [face]))
    h = S(chain(arc(0, 0.05, 0.72, math.radians(-15), math.radians(195), 40), cubic((-0.695, -0.14), (-0.9, -0.6), (-0.8, -0.9), (-0.95, -1.1), 10),
                [(-0.4, -0.6), (0.4, -0.6)], cubic((0.95, -1.1), (0.8, -0.9), (0.9, -0.6), (0.695, -0.14), 10)))
    back.append(([h], [chain(h, [h[0]])]))
    return front, back, hints


def smooth(pts, it=3):
    """Chaikin corner cutting for a closed polygon."""
    p = pts[:-1] if math.dist(pts[0], pts[-1]) < 1e-9 else pts[:]
    for _ in range(it):
        q = []
        for a, b in zip(p, p[1:] + p[:1]):
            q += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]), (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        p = q
    return p + [p[0]]


def rock(cx, cy, w, h, seed=0):
    pts = [(cx - w, cy)]
    k = 6
    for i in range(k + 1):
        t = i / k
        a = math.pi * (1 - t)
        bump = 1 + 0.1 * math.sin(7 * t + seed) + 0.06 * math.cos(13 * t + 2 * seed)
        pts.append((cx + w * math.cos(a) * bump, cy + h * math.sin(a) * bump))
    pts.append((cx + w, cy))
    sm = smooth(pts + [pts[0]], 3)
    # keep the flat bottom flat
    return [(x, max(y, cy)) for x, y in sm]


def bubbles(pts):
    return [circle(x, y, r, 16) for x, y, r in pts]


def seaweed(x, y, h, w=0.35, waves=1.5, phase=0.0):
    c = [(x + 0.25 * math.sin(phase + TAU * waves * i / 30), y + h * i / 30) for i in range(31)]
    return tube(c, lambda t: w * (1 - t) + 0.06)


def starfish(cx, cy, r, rot=0.0):
    pts = []
    for k in range(10):
        a = math.pi / 2 + rot + k * math.pi / 5
        rr = r if k % 2 == 0 else 0.45 * r
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    out = []
    n = len(pts)
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        if i % 2 == 0:
            m1 = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            m2 = ((b[0] + c[0]) / 2, (b[1] + c[1]) / 2)
            out += quad(m1, b, m2, 6)
        else:
            out.append(b)
    return chain(out, [out[0]])


def sea_waves(y, x0=-3.6, x1=3.6, amp=0.1, waves=7):
    return wave(x0, x1, y, amp, waves, 160)


def dolphin(dx, dy, s, rot=0.0, flip=False):
    body = chain([(2.0, 0.0)], quad((2.0, 0.0), (1.8, 0.28), (1.35, 0.35), 8), cubic((1.35, 0.35), (1.2, 0.75), (0.6, 0.75), (0.0, 0.62), 14),
                 cubic((0.0, 0.62), (-0.9, 0.5), (-1.5, 0.25), (-2.0, 0.06), 14), quad((-2.0, 0.06), (-2.3, 0.45), (-2.7, 0.65), 8),
                 quad((-2.7, 0.65), (-2.5, 0.2), (-2.35, 0.0), 6), quad((-2.35, 0.0), (-2.5, -0.25), (-2.7, -0.6), 6),
                 quad((-2.7, -0.6), (-2.3, -0.4), (-2.0, -0.08), 8), cubic((-2.0, -0.08), (-1.2, -0.35), (0.2, -0.75), (1.0, -0.42), 14),
                 quad((1.0, -0.42), (1.5, -0.2), (2.0, -0.05), 8), [(2.0, 0.0)])
    fin = chain([(-0.05, 0.6)], quad((-0.05, 0.6), (-0.2, 1.1), (-0.6, 1.3), 8), quad((-0.6, 1.3), (-0.5, 0.9), (-0.6, 0.55), 8))
    flipper = chain([(0.55, -0.45)], quad((0.55, -0.45), (0.4, -0.9), (0.0, -1.05), 8), quad((0.0, -1.05), (0.25, -0.75), (0.15, -0.52), 8))
    mouth = [quad((1.95, 0.0), (1.6, -0.05), (1.4, 0.02), 6)]
    items = [([body] + mouth, [body]), ([flipper], [chain(flipper, [flipper[0]])]), ([fin], [chain(fin, [fin[0]])])]
    items = place_items(items, dx, dy, s, rot, flip)
    h = place([eye(1.15, 0.22, 0.07)], dx, dy, s, rot, flip)
    return items, h


def seahorse(dx, dy, s, flip=False):
    spine = chain(cubic((0.0, 1.2), (0.9, 0.9), (0.9, -0.4), (0.3, -1.0), 20), cubic((0.3, -1.0), (0.0, -1.3), (0.2, -1.7), (0.55, -1.7), 10))
    w = lambda t: 0.75 * math.sin(math.pi * min(1, t * 1.3 + 0.15)) ** 0.7 * (1 - t) + 0.12
    body = tube(spine, w)
    curl = spiral(0.55, -1.45, 0.28, 0.05, 0.8, 30, rot=-math.pi / 2)
    head = chain([(-0.25, 1.0)], quad((-0.25, 1.0), (-0.2, 1.75), (0.3, 1.65), 10), quad((0.3, 1.65), (0.55, 1.5), (0.4, 1.15), 8))
    snout = rrect(-1.05, 1.25, -0.2, 1.48, 0.1)
    crown_ = poly((-0.05, 1.68), (0.05, 1.95), (0.18, 1.7), closed=False)
    fin = chain([(0.75, 0.3)], quad((0.75, 0.3), (1.3, 0.2), (0.85, -0.3), 8))
    belly = keep_in([quad((-0.5, y), (0.1, y - 0.15), (0.6, y), 8) for y in (0.5, 0.15, -0.2, -0.55)], body)
    snout = tube([(-0.1, 1.4), (-1.0, 1.32)], lambda t: 0.3 - 0.1 * t)
    items = [([head, crown_], [chain(head, [head[0]])]), ([snout], [snout]), ([body] + belly, [body]), ([fin], [chain(fin, [fin[0]])]), ([curl], [])]
    items = place_items(items, dx, dy, s, 0.0, flip)
    return items, place([eye(0.05, 1.42, 0.07)], dx, dy, s, 0.0, flip)


def turtle(dx, dy, s, rot=0.0, flip=False):
    shell_ = chain(arc(0, -0.1, 1.5, math.radians(5), math.radians(175), 40), quad((-1.5, 0.03), (0, -0.45), (1.5, 0.03), 20))
    shell_ = chain(shell_, [shell_[0]])
    plates = keep_in([poly((-0.5, 0.0), (-0.3, 0.75), (0.3, 0.75), (0.5, 0.0), closed=False), [(-0.3, 0.75), (-0.6, 1.25)], [(0.3, 0.75), (0.6, 1.25)],
                      [(-0.5, 0.05), (-1.3, 0.3)], [(0.5, 0.05), (1.3, 0.3)]], shell_)
    rim = keep_in([quad((-1.6, 0.0), (0, -0.25), (1.6, 0.0), 20)], shell_)
    head = chain([(1.3, 0.1)], cubic((1.3, 0.1), (1.6, 0.6), (2.4, 0.6), (2.4, 0.0), 12), cubic((2.4, 0.0), (2.4, -0.4), (1.8, -0.4), (1.4, -0.25), 12))
    fl1 = lens((0.8, -0.3), (1.6, -1.2), 0.25)
    fl2 = lens((-0.9, -0.3), (-1.7, -0.9), 0.25)
    tailp = poly((-1.4, -0.1), (-1.85, -0.25), (-1.4, -0.3), closed=False)
    items = [([shell_] + plates + rim, [shell_]), ([head], [chain(head, [head[0]])]), ([fl1], [fl1]), ([fl2], [fl2]), ([tailp], [])]
    items = place_items(items, dx, dy, s, rot, flip)
    return items, place([eye(2.05, 0.15, 0.08)], dx, dy, s, rot, flip)


def little_fish(x, y, s, flip=False):
    b = chain(quad((0.6, 0), (0.1, 0.4), (-0.4, 0.0), 10), quad((-0.4, 0.0), (0.1, -0.4), (0.6, 0), 10))
    t = poly((-0.35, 0.0), (-0.75, 0.25), (-0.75, -0.25))
    return place([b, t], x, y, s, flip=flip), place([eye(0.3, 0.05, 0.05)], x, y, s, flip=flip)


# ------------------------------------------------------------ designs: mermaids

@design("mermaids_on_rock", T)
def on_rock(rng):
    m, mm, mh = mermaid(0, 0, 1.0, tail="sit", arms=("rest", "up"))
    rk = rock(0.0, -3.2, 2.2, 2.7, 1)
    sea = hide([sea_waves(-2.4), sea_waves(-3.0, amp=0.08)], [rk])
    gulls = [chain(quad((x - s_, y), (x - 0.5 * s_, y + 0.45 * s_), (x, y), 8), quad((x, y), (x + 0.5 * s_, y + 0.45 * s_), (x + s_, y), 8)) for x, y, s_ in [(-2.6, 3.2, 0.35), (-1.9, 3.7, 0.28)]]
    sun = [circle(2.6, 3.2, 0.6, 30)]
    out = scene((m, mm), ([rk, quad((-1.2, -1.6), (-0.8, -2.0), (-1.0, -2.6), 8), quad((1.4, -2.2), (1.0, -2.6), (1.3, -3.0), 8)], [rk]), (sea + gulls + sun, []))
    return make("Mermaid Sitting on a Rock", out, mh)


@design("mermaids_swimming", T)
def swimming(rng):
    m, mm, mh = mermaid(-0.4, 0.4, 1.0, rot=math.radians(-65), tail="swim", arms=("up", "wave"))
    fish = []
    fh = []
    for x, y, s_ in [(2.9, 1.6, 0.6), (2.4, 2.4, 0.45), (-2.8, 2.2, 0.45)]:
        f, h = little_fish(x, y, s_)
        fish += f
        fh += h
    bub = bubbles([(2.0, -1.3, 0.2), (2.4, -0.8, 0.14), (2.2, -0.3, 0.1), (-3.0, -2.0, 0.18), (-2.7, -1.5, 0.12)])
    weeds = [seaweed(x, -3.4, h, 0.35, 1.2, p) for x, h, p in [(-2.6, 1.8, 0.0), (-1.9, 1.2, 1.0), (2.8, 1.6, 2.0)]]
    sand = [wave(-3.6, 3.6, -3.4, 0.08, 3, 60)]
    out = scene((m, mm), (fish, fish), (weeds, weeds), (bub + sand, []))
    return make("Mermaid Swimming with Little Fish", out, mh + fh)


@design("mermaids_comb_mirror", T)
def comb_mirror(rng):
    mirror_ = [ellipse(2.05, 2.0, 0.42, 0.55, 30), ellipse(2.05, 2.0, 0.3, 0.42, 26), tube([(1.95, 1.48), (1.82, 0.95)], 0.16)]
    comb = [rect(-1.15, 2.5, -0.35, 2.75)] + [[(-1.05 + 0.15 * k, 2.5), (-1.05 + 0.15 * k, 2.2)] for k in range(6)]
    held = [(mirror_, [mirror_[0], mirror_[2]]), (comb, [comb[0]])]
    m, mm, mh = mermaid(0, 0, 1.0, tail="curl", arms=(((0.62, 1.2), (1.1, 1.6), (0.75, 2.5)), ((0.62, 1.2), (1.4, 0.9), (1.8, 1.0))), held=held)
    rk = rock(0.4, -3.0, 2.4, 2.3, 3)
    sea = hide([sea_waves(-2.3), sea_waves(-2.9, amp=0.08)], [rk])
    out = scene((m, mm), ([rk], [rk]), (sea, []))
    return make("Mermaid with Comb and Mirror", out, mh)


@design("mermaids_tail_splash", T)
def tail_splash(rng):
    ctrl = ((-0.6, -1.0), (-0.6, 0.4), (0.2, 1.0), (0.6, 2.0))
    titems = tail_items(ctrl, True, 1.5)
    tl = scene(*titems)
    tm = masks_of(titems)
    drops = [lens((x, y), (x + 0.15 * math.cos(a), y + 0.45 * math.sin(a) + 0.1), 0.35) for x, y, a in
             [(-2.0, 0.2, 2.2), (-1.6, 0.9, 1.9), (1.4, 0.6, 1.0), (1.9, 0.0, 0.8), (-2.6, -0.4, 2.6), (2.5, -0.5, 0.5)]]
    splash = [chain(quad((-2.2, -1.0), (-1.6, -0.1), (-1.25, -1.0), 10)), chain(quad((0.3, -1.0), (0.9, 0.0), (1.5, -1.0), 10))]
    rings = [ellipse(-0.4, -1.1, 2.4, 0.5, 80), ellipse(-0.4, -1.15, 3.3, 0.8, 100)]
    sea = [sea_waves(-2.4, amp=0.1), sea_waves(-3.0, amp=0.1)]
    out = scene((tl, tm), (splash + drops, drops), (rings + sea, []))
    return make("Mermaid Tail Splash", out)


@design("mermaids_princess_portrait", T)
def princess_portrait(rng):
    front, back, hints = girl_head(0, 1.0, 1.9, "long", "open", "shell")
    neck = [[(-0.28, -0.1), (-0.28, -0.75)], [(0.28, -0.1), (0.28, -0.75)]]
    shoulders = [chain(quad((-0.28, -0.7), (-1.7, -0.8), (-2.1, -1.7), 10), [(-2.2, -3.4)]), chain(quad((0.28, -0.7), (1.7, -0.8), (2.1, -1.7), 10), [(2.2, -3.4)])]
    pearls = [circle(0.85 * math.sin(a), -0.95 - 0.55 * math.cos(a), 0.11, 10) for a in [math.radians(-70 + 20 * k) for k in range(8)]]
    shells = []
    for sx in (-1, 1):
        sh, shm = fan_shell(sx * 0.6, -2.6, 0.62, 0.0, 3)
        shells.append((sh, [shm]))
    star_ = starfish(-1.25, 1.6, 0.35, 0.3)
    body = [(pearls, pearls)] + shells + [(neck + shoulders, [poly((-0.28, -0.1), (-0.28, -0.7), (-2.1, -1.7), (-2.2, -3.4), (2.2, -3.4), (2.1, -1.7), (0.28, -0.7), (0.28, -0.1))])]
    out = scene(([star_], [star_]), *front, *body, *back)
    bub = bubbles([(2.4, 2.4, 0.2), (2.7, 2.9, 0.14), (-2.6, -0.5, 0.16)])
    return make("Mermaid Princess with Shell Crown", out + bub, hints)


@design("mermaids_with_dolphin", T)
def with_dolphin(rng):
    d_items, dh = dolphin(1.3, 1.0, 1.0, math.radians(25))
    m, mm, mh = mermaid(-1.5, -0.4, 0.82, rot=math.radians(-15), tail="swim", arms=("down", "out"))
    bub = bubbles([(0.2, 3.2, 0.18), (0.6, 3.6, 0.12), (-3.0, 2.6, 0.16)])
    sea = [sea_waves(-3.6, amp=0.08, waves=6)]
    out = scene((m, mm), *d_items, (bub + sea, []))
    return make("Mermaid and Dolphin Friend", out, mh + dh)


@design("mermaids_with_seahorse", T)
def with_seahorse(rng):
    s_items, sh = seahorse(2.3, 0.6, 0.95, flip=False)
    m, mm, mh = mermaid(-0.9, 0.0, 0.95, tail="sit", arms=("rest", "out"))
    rk = rock(-0.9, -3.15, 2.0, 2.5, 2)
    weeds = [seaweed(2.9, -3.3, 2.0, 0.35, 1.2, 0.5), seaweed(-3.3, -3.3, 2.6, 0.35, 1.5, 1.5)]
    bub = bubbles([(1.6, 2.7, 0.15), (1.9, 3.2, 0.11)])
    out = scene(*s_items, (m, mm), ([rk], [rk]), (weeds, weeds), (bub + [wave(-3.6, 3.6, -3.3, 0.06, 3, 60)], []))
    return make("Mermaid with a Seahorse", out, mh + sh)


@design("mermaids_baby", T)
def baby(rng):
    st = starfish(1.15, 0.85, 0.42, 0.2)
    m, mm, mh = mermaid(0, 0, 1.0, tail="short", arms=("down", "chest"), head_scale=1.55, hair="pony", held=[([st], [st])])
    bub = bubbles([(-1.8, 2.5, 0.25), (-2.2, 3.1, 0.17), (-1.7, 3.5, 0.12), (2.2, 3.0, 0.2)])
    shells = [fan_shell(-1.8, -1.9, 0.5, 0.2, 3), fan_shell(2.4, -1.6, 0.4, -0.3, 3)]
    sand = [wave(-2.8, 3.2, -1.9, 0.06, 3, 60)]
    out = scene((m, mm), *[(a, [b]) for a, b in shells], (bub + sand, []))
    return make("Baby Mermaid with Starfish", out, mh)


def onion_dome(cx, y, w, h):
    return chain([(cx - w, y)], cubic((cx - w, y), (cx - w * 1.3, y + h * 0.6), (cx - w * 0.1, y + h * 0.7), (cx, y + h), 14),
                 cubic((cx, y + h), (cx + w * 0.1, y + h * 0.7), (cx + w * 1.3, y + h * 0.6), (cx + w, y), 14), [(cx - w, y)])


def arch_window(cx, y, w, h):
    return chain([(cx - w, y), (cx - w, y + h - w)], arc(cx, y + h - w, w, math.pi, 0, 10), [(cx + w, y), (cx - w, y)])


@design("mermaids_sea_castle", T)
def sea_castle(rng):
    items = []
    for cx, top, w in [(-2.3, 0.6, 0.55), (2.3, 0.6, 0.55), (-1.1, 1.4, 0.55), (1.1, 1.4, 0.55), (0.0, 2.2, 0.7)]:
        tw = rect(cx - w, -2.6, cx + w, top)
        dome = onion_dome(cx, top, w + 0.12, 1.0 + 0.3 * w)
        spire = [[(cx, top + 1.0 + 0.3 * w), (cx, top + 1.45 + 0.3 * w)], circle(cx, top + 1.55 + 0.3 * w, 0.1, 10)]
        win = arch_window(cx, top - 1.0, 0.18, 0.6)
        items.append((spire + [dome], [dome]))
        items.append(([tw, win], [tw]))
    wall = rect(-2.9, -2.6, 2.9, -0.6)
    door = chain([(-0.5, -2.6), (-0.5, -1.7)], arc(0, -1.7, 0.5, math.pi, 0, 14), [(0.5, -2.6)])
    crenel = zigzag(-2.9, 2.9, -0.45, 0.15, 12)
    shells_ = [fan_shell(x, -1.0, 0.3, 0.0, 2) for x in (-1.7, 1.7)]
    weeds = [seaweed(x, -3.0, h, 0.35, 1.3, p) for x, h, p in [(-3.4, 2.6, 0.0), (3.3, 2.2, 1.0)]]
    bub = bubbles([(-2.9, 2.2, 0.2), (-2.6, 2.8, 0.14), (2.8, 2.5, 0.18), (3.1, 3.1, 0.12)])
    sand = [wave(-3.6, 3.6, -2.7, 0.08, 4, 60)]
    sf = [starfish(-1.5, -3.1, 0.3), starfish(2.0, -3.15, 0.25, 0.4)]
    out = scene(*[(a, [b]) for a, b in shells_], ([wall, door], [wall]), (items[8][0], items[8][1]), (items[9][0], items[9][1]),
                *items[4:8], *items[0:4], (weeds, weeds), (bub + sand + sf + [crenel], []))
    return make("Mermaid Castle Under the Sea", out)


def trident(x0, y0, x1, y1, w=0.18):
    ang = math.atan2(y1 - y0, x1 - x0)
    L = math.hypot(x1 - x0, y1 - y0)
    shaft = rect(0, -w / 2, L - 1.0, w / 2)
    head = chain([(L - 1.0, -0.8)], quad((L - 1.0, -0.8), (L - 1.3, 0.0), (L - 1.0, 0.8), 12), [(L - 0.2, 0.8), (L + 0.2, 0.62), (L - 0.2, 0.55), (L - 0.85, 0.5)],
                 [(L - 0.85, 0.12), (L, 0.12), (L + 0.55, 0.0), (L, -0.12), (L - 0.85, -0.12), (L - 0.85, -0.5), (L - 0.2, -0.55), (L + 0.2, -0.62), (L - 0.2, -0.8), (L - 1.0, -0.8)])
    pts = [transform(p, x0, y0, 1.0, ang) for p in (shaft, head)]
    return pts


@design("mermaids_sea_king", T)
def sea_king(rng):
    tr = trident(2.0, -2.6, 2.0, 3.6, 0.2)
    m, mm, mh = mermaid(-0.5, 0.0, 1.0, tail="curl", arms=("hip", ((0.7, 1.2), (1.6, 1.0), (2.3, 1.1))), male=True, crown="crown",
                        held=[])
    out = scene((m, mm), (tr, tr))
    bub = bubbles([(-2.6, 2.8, 0.2), (-2.9, 3.3, 0.13), (-2.3, 3.6, 0.1)])
    return make("Sea King with Trident", out + bub, mh)


@design("mermaids_trident", T)
def golden_trident(rng):
    tr = trident(-1.5, -3.2, 1.2, 3.4, 0.28)
    ribbon = tube(chain([(x, -0.6 + 0.5 * math.sin(x * 2.2)) for x in [-2.4 + 0.1 * i for i in range(49)]]), 0.45)
    pearls_ = [circle(x, y, 0.2, 14) for x, y in [(-2.6, 1.6), (-2.2, 2.2), (2.3, -1.6), (2.6, -2.2)]]
    waves_ = [chain(arc(x, -3.2, 0.5, 0, math.pi, 12)) for x in (-2.5, -1.5, -0.5, 0.5, 1.5, 2.5)]
    sp = [star(2.6, 2.4, 0.4, 4, 0.3), star(-2.8, -0.2, 0.3, 4, 0.3)]
    out = scene(([ribbon], [ribbon]), (tr, tr), (pearls_ + waves_ + sp, []))
    return make("Golden Trident with Ribbon", out)


@design("mermaids_shell_throne", T)
def shell_throne(rng):
    back_c = (0, 0.0)
    back = chain(arc(0, -0.4, 2.9, math.radians(8), math.radians(172), 60))
    back = scallop(back, 0.25, 9)
    back = chain([(-2.9, -0.4)], back, [(2.9, -0.4)])
    ribs = [[(0.4 * math.cos(a), -0.2 + 0.4 * math.sin(a)), (2.55 * math.cos(a), -0.4 + 2.55 * math.sin(a))] for a in [math.radians(20 + 20 * k) for k in range(8)]]
    seat = rrect(-2.4, -1.4, 2.4, -0.4, 0.3)
    cushion = ellipse(0, -0.4, 2.0, 0.35, 50)
    base = poly((-2.2, -1.4), (-2.0, -2.6), (2.0, -2.6), (2.2, -1.4))
    steps = [rect(-2.6, -2.95, 2.6, -2.6), rect(-3.0, -3.3, 3.0, -2.95)]
    pearl_posts = [circle(-2.9, -0.1, 0.3, 20), circle(2.9, -0.1, 0.3, 20)]
    crown_ = poly((-0.5, 2.7), (-0.6, 3.3), (-0.3, 3.0), (0, 3.5), (0.3, 3.0), (0.6, 3.3), (0.5, 2.7))
    out = scene((pearl_posts, pearl_posts), ([cushion], [cushion]), ([seat], [seat]), ([base], [base]), (steps, steps), ([crown_], [crown_]),
                ([chain(back, [back[0]])] + ribs, [chain(back, [back[0]])]))
    return make("Seashell Throne", out)


@design("mermaids_asleep_in_clam", T)
def asleep_in_clam(rng):
    bottom = chain([(-3.2, -0.6)], quad((-3.2, -0.6), (0, -3.2), (3.2, -0.6), 40), [(-3.2, -0.6)])
    bottom_s = chain(scallop(quad((-3.2, -0.6), (0, -3.2), (3.2, -0.6), 40), -0.15, 10))
    lid = chain(scallop(quad((-3.2, -0.4), (-1.4, 3.6), (3.2, -0.4), 40)[::-1], 0.15, 10))
    lid = chain([(3.2, -0.4)], scallop(quad((3.2, -0.4), (-1.0, 4.0), (-3.2, -0.4), 40), 0.18, 9), [(3.2, -0.4)])
    bottom = chain([(-3.2, -0.6)], scallop(quad((-3.2, -0.6), (0, -3.2), (3.2, -0.6), 40), 0.15, 9), [(-3.2, -0.6)])
    lid_ribs = keep_in([[(0, -0.4), (5 * math.cos(a), -0.4 + 5 * math.sin(a))] for a in [math.radians(25 + 26 * k) for k in range(6)]], lid)
    bot_ribs = keep_in([[(0, -0.6), (5 * math.cos(a), -0.6 + 5 * math.sin(a))] for a in [math.radians(-30 - 30 * k) for k in range(4)]], bottom)
    ctrl = ((0.6, -0.9), (1.4, -1.0), (2.0, -1.0), (2.6, -0.4))
    titems = tail_items(ctrl, False, 0.95)
    front, back, hints = girl_head(-1.6, -0.35, 0.9, "long", "closed")
    pillow = ellipse(-1.7, -1.0, 0.9, 0.35, 30)
    body = chain([(-1.05, -0.65)], scallop(quad((-1.05, -0.65), (-0.2, -0.3), (0.75, -0.5), 16), 0.08, 4), [(0.75, -1.3)],
                 quad((0.75, -1.3), (-0.3, -1.4), (-1.05, -1.2), 10))
    blanket = []
    pearl = circle(2.4, 2.0, 0.35, 24)
    zz = [poly((-0.6, 1.0), (-0.3, 1.0), (-0.6, 0.75), (-0.3, 0.75), closed=False), poly((-0.1, 1.5), (0.3, 1.5), (-0.1, 1.15), (0.3, 1.15), closed=False)]
    items = front + [([body], [chain(body, [body[0]])])] + titems + back + [([pillow], [pillow]), ([bottom] + bot_ribs, [bottom]), ([lid] + lid_ribs, [lid])]
    out = scene(*items)
    return make("Mermaid Asleep in a Clam Shell", out + zz, hints)


def sparkle(x, y, r):
    return star(x, y, r, 4, 0.3)


def book(cx, cy, w, h, rot=0.0):
    """Open book seen from the front, spine at (cx, cy)."""
    pts = [chain([(0, 0)], quad((0, 0), (-w * 0.5, 0.25 * h), (-w, 0.05 * h), 10), [(-w, h)], quad((-w, h), (-w * 0.5, 1.2 * h), (0, h), 10), [(0, 0)]),
           chain([(0, 0)], quad((0, 0), (w * 0.5, 0.25 * h), (w, 0.05 * h), 10), [(w, h)], quad((w, h), (w * 0.5, 1.2 * h), (0, h), 10), [(0, 0)])]
    lines = []
    for sx in (-1, 1):
        for k in range(3):
            y = h * (0.35 + 0.18 * k)
            lines.append(quad((sx * 0.15 * w, y), (sx * 0.5 * w, y + 0.12 * h), (sx * 0.85 * w, y - 0.0), 8))
    return [transform(p, cx, cy, 1.0, rot) for p in pts + lines], [transform(p, cx, cy, 1.0, rot) for p in pts]


@design("mermaids_reading", T)
def reading(rng):
    bk, bm = book(0.0, 0.25, 0.9, 0.95, 0.0)
    m, mm, mh = mermaid(0, 0, 1.0, tail="sit", arms=(((0.62, 1.2), (0.9, 0.3), (0.85, 0.35)), ((0.62, 1.2), (0.9, 0.3), (0.85, 0.35))),
                        eyes="closed", held=[(bk, bm)])
    rk = rock(0.3, -3.1, 2.3, 2.6, 4)
    sea = hide([sea_waves(-2.4), sea_waves(-3.0, amp=0.08)], [rk])
    sh = fan_shell(-2.6, -1.95, 0.45, 0.2, 3)
    out = scene((m, mm), ([rk], [rk]), (sh[0], [sh[1]]), (sea, []))
    return make("Mermaid Reading a Storybook", out, mh)


@design("mermaids_on_moon", T)
def on_moon(rng):
    moon = chain(arc(0.0, 0.0, 3.0, math.radians(100), math.radians(330), 80), arc(1.1, 0.6, 2.4, math.radians(300), math.radians(125), 80)[::-1][::-1])
    outer = arc(0, 0, 3.0, math.radians(95), math.radians(335), 80)
    inner = arc(1.0, 0.55, 2.35, math.radians(110), math.radians(318), 80)
    moon = chain(outer, inner[::-1], [outer[0]])
    ctrl = ((0, -0.45), (0.3, -1.6), (1.1, -2.0), (1.4, -2.9))
    m, mm, mh = mermaid(-1.6, -1.2, 0.72, tail=ctrl, arms=("rest", "wave"))
    stars_ = [star(x, y, r) for x, y, r in [(2.6, 2.6, 0.35), (1.8, 3.3, 0.22), (3.2, 1.2, 0.25), (-2.9, 3.0, 0.25), (2.8, -2.6, 0.3)]]
    out = scene((m, mm), ([moon], [moon]), (stars_, []))
    return make("Mermaid on the Crescent Moon", out, mh)


@design("mermaids_merman_conch", T)
def merman_conch(rng):
    conch = chain([(1.1, 3.3)], cubic((1.1, 3.3), (1.8, 3.9), (2.9, 3.6), (3.3, 2.9), 14), quad((3.3, 2.9), (2.4, 2.7), (1.3, 2.9), 10), [(1.1, 3.3)])
    conch_lines = [quad((1.6, 3.4), (1.9, 3.1), (1.7, 2.85), 6), quad((2.2, 3.6), (2.5, 3.2), (2.3, 2.8), 6)]
    bell = ellipse(3.35, 2.95, 0.25, 0.55, 20, rot=-0.3)
    m, mm, mh = mermaid(0, 0, 1.0, tail="swim", arms=(((0.7, 1.2), (1.2, 1.2), (0.6, 2.4)), ((0.7, 1.2), (1.4, 2.0), (1.2, 2.9))), male=True,
                        crown=None, held=[([bell], [bell]), ([conch] + conch_lines, [conch])])
    notes = [chain(circle(-2.4, 2.6, 0.18, 12)), [(-2.22, 2.6), (-2.22, 3.3), (-1.9, 3.15)]]
    bub = bubbles([(2.4, -1.0, 0.2), (2.7, -0.4, 0.14), (-2.5, -1.2, 0.18), (-2.2, -0.6, 0.12)])
    weeds = [seaweed(-3.0, -3.6, 2.0, 0.35, 1.3, 0.0), seaweed(2.6, -3.6, 2.2, 0.35, 1.3, 1.7)]
    out = scene((m, mm), (weeds, weeds), (bub, []))
    return make("Merman Blowing a Conch Shell", out, mh)


@design("mermaids_harp", T)
def harp(rng):
    frame = chain([(1.2, -1.2)], [(1.25, 2.4)], cubic((1.25, 2.4), (1.9, 3.1), (2.6, 2.0), (3.0, 2.6), 16), [(3.2, 2.5)],
                  cubic((3.2, 2.5), (3.0, 1.0), (2.2, -0.4), (1.45, -1.1), 16), [(1.2, -1.2)])
    inner = chain([(1.45, -0.7)], [(1.48, 2.2)], cubic((1.48, 2.2), (1.9, 2.75), (2.5, 1.85), (2.85, 2.25), 14),
                  cubic((2.85, 2.25), (2.6, 1.0), (2.0, -0.2), (1.45, -0.7), 14))
    strings = keep_in([[(1.5 + 0.28 * k, -1.5), (1.5 + 0.28 * k, 3.0)] for k in range(1, 5)], inner)
    held = [(hide([frame, inner] + strings, []), [frame])]
    m, mm, mh = mermaid(-0.6, 0.0, 1.0, tail="sit", arms=(((0.62, 1.2), (1.3, 0.6), (1.85, 0.9)), ((0.62, 1.2), (1.4, 1.1), (2.1, 1.6))),
                        eyes="closed", held=[])
    m2, mm2, _ = m, mm, mh
    rk = rock(-0.3, -3.1, 2.4, 2.6, 5)
    notes = [[(-2.6, 2.4), (-2.6, 3.1), (-2.2, 3.3), (-2.2, 2.6)], circle(-2.75, 2.35, 0.17, 12), circle(-2.35, 2.55, 0.17, 12)]
    sea = hide([sea_waves(-2.4), sea_waves(-3.0, amp=0.08)], [rk])
    hands = [circle(1.25, 0.9, 0.14, 12), circle(1.5, 1.6, 0.14, 12)]
    out = scene((place(hands, -0.6, 0.0), place(hands, -0.6, 0.0)), (place([frame, inner] + strings, -0.6, 0.0), [place([frame], -0.6, 0.0)[0]]),
                (m, mm), ([rk], [rk]), (sea + notes, []))
    return make("Mermaid Playing the Harp", out, mh)


@design("mermaids_heart_tails", T)
def heart_tails(rng):
    ctrl = ((0, -0.45), (0.2, -1.8), (1.0, -2.6), (2.2, -2.9))
    m1, mm1, h1 = mermaid(-1.5, 0.3, 0.85, rot=math.radians(10), tail=ctrl, arms=("down", "out"), hair="long")
    m2, mm2, h2 = mermaid(1.5, 0.3, 0.85, rot=math.radians(-10), flip=True, tail=ctrl, arms=("down", "out"), hair="bun")
    hrt = heart(0, 1.8, 0.45)
    out = scene(([hrt], [hrt]), (m1, mm1), (m2, mm2))
    bub = bubbles([(-0.3, 3.1, 0.15), (0.3, 3.5, 0.11)])
    return make("Two Mermaids with a Heart", out + bub, h1 + h2)


@design("mermaids_blowing_bubbles", T)
def blowing_bubbles(rng):
    m, mm, mh = mermaid(-0.9, -0.4, 1.0, tail="swim", arms=("down", ((0.62, 1.2), (1.0, 1.5), (0.45, 2.25))), eyes="closed")
    bub = bubbles([(0.2, 2.2, 0.25), (0.7, 2.6, 0.35), (1.4, 2.4, 0.22), (1.3, 3.2, 0.45), (2.2, 2.9, 0.3), (2.6, 2.0, 0.2), (2.2, 3.7, 0.2), (0.6, 3.4, 0.2)])
    shine = [arc(1.3, 3.2, 0.32, math.radians(100), math.radians(160), 6), arc(0.7, 2.6, 0.24, math.radians(100), math.radians(160), 6)]
    weeds = [seaweed(x, -3.9, h, 0.35, 1.4, p) for x, h, p in [(1.6, 2.6, 0.3), (2.4, 1.8, 1.1), (3.0, 2.2, 2.2)]]
    sf = [starfish(2.0, -3.6, 0.35, 0.2)]
    out = scene((bub + shine, bub), (m, mm), (sf, sf), (weeds, weeds), ([wave(-3.4, 3.6, -3.9, 0.06, 3, 60)], []))
    return make("Mermaid Blowing Bubbles", out, mh)


@design("mermaids_lagoon", T)
def lagoon(rng):
    cliff = smooth([(-3.6, -0.6), (-3.6, 3.2), (-3.0, 3.5), (-2.4, 3.2), (-1.4, 3.1), (-1.2, 1.0), (-0.5, 0.7), (-0.3, -0.6), (-3.6, -0.6)], 2)
    cliff = [p for p in cliff if p[1] > -0.59 or p[0] < -3.5]
    cliff2 = smooth([(3.6, -0.6), (3.6, 2.6), (3.0, 3.0), (2.4, 2.7), (1.7, 2.2), (1.3, 0.5), (0.5, 0.3), (0.3, -0.6), (3.6, -0.6)], 2)
    cliff2 = [p for p in cliff2 if p[1] > -0.59 or p[0] > 3.5]
    cracks = [poly((-3.0, 2.4), (-2.6, 1.9), (-2.8, 1.2), closed=False), poly((2.7, 2.0), (2.3, 1.4), (2.5, 0.8), closed=False)]
    fall = [[(-1.35, 3.0), (-1.35, 0.9)], [(-0.95, 3.0), (-0.95, 0.85)], quad((-1.15, 2.6), (-1.1, 1.8), (-1.15, 1.0), 6)]
    fall_top = [quad((-1.4, 3.0), (-1.15, 3.15), (-0.9, 3.0), 6)]
    foam = [chain(arc(x, 0.75, 0.2, 0, math.pi, 8)) for x in (-1.5, -1.15, -0.8)]
    pool = ellipse(0.0, -1.0, 3.4, 0.7, 120)
    ripples = [ellipse(0.2, -1.1, 1.6, 0.3, 60)]
    m, mm, mh = mermaid(1.6, -0.35, 0.55, tail="sit", arms=("rest", "wave"))
    pt = []
    lily = [ellipse(-2.2, -1.2, 0.5, 0.18, 24), ellipse(-1.5, -1.5, 0.35, 0.13, 20)]
    out = scene((m, mm), (lily, lily), ([pool] + ripples, [pool]), (fall + fall_top + foam, []), ([cliff, cliff2] + cracks, []))
    return make("Mermaid Lagoon with Waterfall", out, mh)


@design("mermaids_with_turtle", T)
def with_turtle(rng):
    t_items, th = turtle(0.4, -1.7, 1.15, rot=math.radians(8))
    ctrl = ((0, -0.45), (0.6, -1.2), (-0.8, -1.6), (-2.2, -1.2))
    m, mm, mh = mermaid(-0.4, -0.75, 0.8, tail=ctrl, arms=("down", "out"))
    bub = bubbles([(2.6, 1.6, 0.2), (2.9, 2.2, 0.14), (-2.8, 2.4, 0.18)])
    weeds = [seaweed(-3.2, -3.8, 2.2, 0.35, 1.3, 0.4), seaweed(3.0, -3.8, 2.6, 0.35, 1.3, 1.4)]
    out = scene((m, mm), *t_items, (weeds, weeds), (bub, []))
    return make("Mermaid Riding a Sea Turtle", out, mh + th)


def fairy(dx=0.0, dy=0.0, s=1.0, rot=0.0, flip=False, arms=("down", "down"), hair="bun", eyes="open", crown=None, held=(), legs="stand",
          wings=True, skirt="petal"):
    front, back, hints = girl_head(0, 2.2, 1.0, hair, eyes, crown)
    neck = [[(-0.12, 1.62), (-0.12, 1.4)], [(0.12, 1.62), (0.12, 1.4)]]
    side = chain(quad((-0.12, 1.42), (-0.62, 1.42), (-0.6, 1.1), 8), quad((-0.6, 1.1), (-0.4, 0.8), (-0.36, 0.55), 8))
    bodice = chain(side, [(0.36, 0.55)], mirror_x(side)[::-1])
    bodice_m = chain(bodice, [bodice[0]])
    if skirt == "petal":
        hem = []
        n = 5
        for k in range(n):
            x0 = -1.3 + 2.6 * k / n
            x1 = -1.3 + 2.6 * (k + 1) / n
            hem += quad((x0, -0.75 + 0.1 * math.sin(k)), ((x0 + x1) / 2, -1.25), (x1, -0.75 + 0.1 * math.sin(k + 1)), 8)[:-1]
        hem.append((1.3, -0.75))
        sk = chain([(-0.36, 0.55)], quad((-0.36, 0.55), (-1.0, 0.1), (-1.3, -0.75), 12), hem, quad((1.3, -0.75), (1.0, 0.1), (0.36, 0.55), 12))
    else:
        hem = scallop([(-1.3, -0.85), (1.3, -0.85)], -0.15, 6)
        sk = chain([(-0.36, 0.55)], quad((-0.36, 0.55), (-1.0, 0.1), (-1.3, -0.85), 12), hem, quad((1.3, -0.85), (1.0, 0.1), (0.36, 0.55), 12))
    skm = chain(sk, [sk[0]])
    belt = [[(-0.36, 0.55), (0.36, 0.55)]]
    if legs == "stand":
        lg = [limb((-0.3, -0.7), (-0.32, -1.5), (-0.35, -2.3), 0.22), limb((0.3, -0.7), (0.32, -1.5), (0.35, -2.3), 0.22)]
        shoes = [lens((-0.65, -2.4), (-0.15, -2.35), 0.25), lens((0.15, -2.35), (0.65, -2.4), 0.25)]
    elif legs == "fly":
        lg = [limb((-0.3, -0.7), (-0.6, -1.4), (-1.3, -1.8), 0.22), limb((0.3, -0.7), (0.1, -1.6), (-0.4, -2.2), 0.22)]
        shoes = [lens((-1.25, -1.75), (-1.65, -1.95), 0.3), lens((-0.35, -2.15), (-0.7, -2.45), 0.3)]
    else:  # sit: legs forward / dangling
        lg = [limb((-0.3, -0.7), (-0.3, -1.3), (-0.6, -1.9), 0.22), limb((0.3, -0.7), (0.4, -1.3), (0.2, -2.0), 0.22)]
        shoes = [lens((-0.55, -1.95), (-0.95, -2.1), 0.3), lens((0.25, -2.05), (-0.1, -2.25), 0.3)]
    arm_items = []
    for sx, pose in zip((-1, 1), arms):
        a, b, c = ARM[pose] if isinstance(pose, str) else pose
        a = (a[0] * 0.85, a[1])
        if sx < 0:
            a, b, c = (-a[0], a[1]), (-b[0], b[1]), (-c[0], c[1])
        arm = limb(a, b, c, 0.22)
        hand = circle(c[0], c[1], 0.12, 12)
        arm_items += [([hand], [hand]), ([arm], [arm])]
    wing_items = []
    if wings:
        for sx in (1, -1):
            up = lens((sx * 0.25, 1.25), (sx * 2.1, 2.7), 0.42)
            lo = lens((sx * 0.25, 1.0), (sx * 1.55, -0.05), 0.4)
            vu = keep_in([quad((sx * 0.4, 1.3), (sx * 1.2, 2.2), (sx * 1.8, 2.5), 10)], up)
            vl = keep_in([quad((sx * 0.4, 0.95), (sx * 1.0, 0.6), (sx * 1.35, 0.15), 10)], lo)
            wing_items += [([up] + vu, [up]), ([lo] + vl, [lo])]
    items = list(held) + arm_items + front + [(neck + [bodice] + belt, [bodice_m]), ([sk], [skm]), (shoes, shoes), (lg, lg)] + back + wing_items
    items = place_items(items, dx, dy, s, rot, flip)
    return scene(*items), masks_of(items), place(hints, dx, dy, s, rot, flip)


def wand(x0, y0, x1, y1, r=0.4):
    return [[(x0, y0), (x1, y1)], star(x1, y1 + 0.05, r, 5, 0.45)]


# dropped: the Unicorns book has this subject
def flower_fairy(rng):
    w = wand(1.7, 1.45, 2.6, 2.9, 0.45)
    m, mm, mh = fairy(0, 0, 1.0, arms=("low", ((0.62, 1.2), (1.3, 1.1), (1.7, 1.45))), legs="fly", held=[(w, [w[1]])], crown="flower")
    sp = [sparkle(x, y, r) for x, y, r in [(2.9, 1.6, 0.25), (3.1, 2.4, 0.18), (2.0, 3.6, 0.2), (-2.6, -1.8, 0.25), (-2.0, 3.4, 0.2)]]
    trail = [spiral(2.6, 2.0, 0.2, 0.9, 1.2, 60, rot=math.pi)]
    out = scene((m, mm), (sp, []))
    return make("Flower Fairy with Magic Wand", out, mh)


def mushroom(cx, cy, w, h, cap_h, spots=True):
    """Toadstool standing at (cx, cy)."""
    stem = chain([(cx - 0.35 * w, cy)], quad((cx - 0.35 * w, cy), (cx - 0.25 * w, cy + 0.5 * h), (cx - 0.3 * w, cy + h), 10), [(cx + 0.3 * w, cy + h)],
                 quad((cx + 0.3 * w, cy + h), (cx + 0.25 * w, cy + 0.5 * h), (cx + 0.35 * w, cy), 10), [(cx - 0.35 * w, cy)])
    cap = chain([(cx - w, cy + h)], cubic((cx - w, cy + h), (cx - w, cy + h + cap_h * 1.2), (cx + w, cy + h + cap_h * 1.2), (cx + w, cy + h), 30),
                quad((cx + w, cy + h), (cx, cy + h - 0.25 * cap_h), (cx - w, cy + h), 16))
    parts = [cap]
    if spots:
        for fx, fy, fr in [(-0.5, 0.45, 0.16), (0.1, 0.7, 0.2), (0.55, 0.4, 0.14), (-0.1, 0.3, 0.12)]:
            parts.append(circle(cx + fx * w, cy + h + fy * cap_h, fr * w, 14))
    return [(parts, [cap]), ([stem], [stem])]


# dropped: the Unicorns book has this subject
def mushroom_house(rng):
    cap = chain([(-3.0, 0.6)], cubic((-3.0, 0.6), (-3.0, 4.2), (3.0, 4.2), (3.0, 0.6), 50), quad((3.0, 0.6), (0, -0.1), (-3.0, 0.6), 30))
    spots = [circle(x, y, r, 20) for x, y, r in [(-1.8, 1.4, 0.35), (-0.4, 2.4, 0.45), (1.2, 1.8, 0.4), (2.2, 1.0, 0.25), (0.4, 1.05, 0.25), (-1.0, 3.0, 0.2)]]
    stem = chain([(-1.6, -2.8)], quad((-1.6, -2.8), (-1.3, -1.0), (-1.5, 0.3), 16), [(1.5, 0.3)], quad((1.5, 0.3), (1.3, -1.0), (1.6, -2.8), 16), [(-1.6, -2.8)])
    door = chain([(-0.5, -2.8), (-0.5, -1.6)], arc(0, -1.6, 0.5, math.pi, 0, 14), [(0.5, -2.8)])
    knob = circle(0.3, -2.2, 0.08, 8)
    wins = [circle(-0.95, -0.6, 0.32, 20), circle(0.95, -0.6, 0.32, 20)]
    cross = [[(-1.27, -0.6), (-0.63, -0.6)], [(-0.95, -0.92), (-0.95, -0.28)], [(0.63, -0.6), (1.27, -0.6)], [(0.95, -0.92), (0.95, -0.28)]]
    chimney = rect(1.6, 2.6, 2.1, 3.6)
    smoke = [spiral(2.3, 4.0, 0.05, 0.3, 1.2, 30), spiral(2.7, 4.6, 0.05, 0.22, 1.2, 24)]
    steps = [ellipse(0.2, -3.1, 0.45, 0.15, 16), ellipse(0.6, -3.45, 0.4, 0.13, 16)]
    grass = [zigzag(-3.4, -1.6, -2.75, 0.12, 6), zigzag(1.6, 3.4, -2.75, 0.12, 6)]
    flowers = []
    for x in (-2.6, 2.6):
        flowers += [[(x, -2.75), (x, -1.9)], circle(x, -1.75, 0.15, 12)] + [circle(x + 0.25 * math.cos(a), -1.75 + 0.25 * math.sin(a), 0.12, 10) for a in [TAU * k / 5 for k in range(5)]]
    out = scene(([knob], []), ([door], [chain(door, [door[0]])]), (wins + cross, wins), ([chimney], [chimney]), ([cap] + spots, [cap]), ([stem], [stem]),
                (smoke + steps + grass + flowers, []))
    return make("Fairy House in a Mushroom", out)


@design("mermaids_fairy_on_flower", T)
def fairy_on_flower(rng):
    petals = []
    for k in range(8):
        a = TAU * k / 8 + 0.2
        petals.append(lens((0, -1.0), (2.2 * math.cos(a), -1.0 + 0.8 * math.sin(a)), 0.22))
    centre = ellipse(0, -1.0, 0.8, 0.35, 40)
    stem = tube(quad((0, -1.3), (0.3, -2.4), (-0.2, -3.6), 16), 0.2)
    leaf = lens((0.1, -2.6), (1.5, -2.1), 0.35)
    m, mm, mh = fairy(0.0, 1.55, 0.95, arms=("rest", "wave"), legs="sit", hair="pony", crown=None)
    out = scene((m, mm), ([centre], [centre]), *[([p], [p]) for p in sorted(petals, key=lambda p: -min(q[1] for q in p))[::-1]], ([leaf], [leaf]), ([stem], [stem]))
    sp = [sparkle(x, y, r) for x, y, r in [(-2.6, 2.6, 0.25), (2.8, 3.0, 0.2), (-2.9, 0.8, 0.18)]]
    return make("Fairy Sitting on a Flower", out + sp, mh)


# dropped: the Unicorns book has this subject
def magic_wand(rng):
    st = star(1.2, 1.4, 1.6, 5, 0.48)
    st_in = star(1.2, 1.4, 1.05, 5, 0.48)
    stick = tube([(-2.6, -3.0), (0.35, 0.15)], 0.28)
    bow = [lens((0.0, -0.4), (-0.9, 0.2), 0.45), lens((0.0, -0.4), (0.4, -1.3), 0.45), circle(0.0, -0.4, 0.18, 12)]
    ribbons = [tube(cubic((0.0, -0.5), (-0.6, -1.2), (-0.2, -1.8), (-0.9, -2.4), 16), 0.22), tube(cubic((0.05, -0.5), (0.3, -1.4), (1.1, -1.4), (1.1, -2.3), 16), 0.22)]
    sp = [sparkle(x, y, r) for x, y, r in [(-1.4, 2.4, 0.35), (-0.4, 3.3, 0.25), (3.0, -0.6, 0.3), (2.6, -1.6, 0.2), (-2.4, 0.9, 0.25), (3.2, 3.2, 0.25)]]
    swirl = [cubic((-2.0, 1.6), (-1.0, 3.6), (2.4, 4.0), (3.4, 1.6), 30)]
    out = scene((bow, [bow[0], bow[1], bow[2]]), (ribbons, ribbons), ([st, st_in], [st]), ([stick], [stick]), (sp + swirl, sp))
    return make("Fairy Godmother's Magic Wand", out)


@design("mermaids_pumpkin_carriage", T)
def pumpkin_carriage(rng):
    body = ellipse(0, 0.6, 2.4, 1.9, 120)
    ribs = keep_in([ellipse(0, 0.6, 1.4, 1.9, 80), ellipse(0, 0.6, 0.6, 1.9, 60)], body)
    door = chain([(-0.7, -0.7)], [(-0.7, 0.7)], arc(0, 0.7, 0.7, math.pi, 0, 16), [(0.7, -0.7), (-0.7, -0.7)])
    win = chain([(-0.45, 0.3)], [(-0.45, 0.75)], arc(0, 0.75, 0.45, math.pi, 0, 14), [(0.45, 0.3), (-0.45, 0.3)])
    stem = chain([(-0.2, 2.45)], quad((-0.2, 2.45), (-0.3, 3.1), (0.3, 3.4), 10), [(0.45, 3.2)], quad((0.45, 3.2), (0.1, 3.0), (0.2, 2.45), 8))
    curls = [spiral(-1.0, 3.0, 0.05, 0.4, 1.3, 30, rot=0), spiral(1.2, 2.9, 0.05, 0.38, 1.3, 30, rot=math.pi)]
    wheels = []
    for x, r in [(-1.8, 1.05), (1.9, 1.15)]:
        wheels.append(([circle(x, -1.6, r, 60), circle(x, -1.6, 0.25, 16)] +
                       [[(x + 0.25 * math.cos(a), -1.6 + 0.25 * math.sin(a)), (x + r * math.cos(a), -1.6 + r * math.sin(a))] for a in [k * math.pi / 4 for k in range(8)]],
                       [circle(x, -1.6, r, 60)]))
    axle = [chain([(-3.2, -0.8)], quad((-3.2, -0.8), (0, -2.0), (3.4, -0.8), 20))]
    steps = [rect(-0.5, -1.5, 0.5, -1.3)]
    out = scene((curls, []), ([door, win], [chain(door, [door[0]])]), ([body] + ribs, [body]), ([stem], [chain(stem, [stem[0]])]), *wheels, (axle + steps, []))
    sp = [sparkle(x, y, r) for x, y, r in [(-2.9, 2.4, 0.3), (2.9, 2.6, 0.25), (3.2, 0.9, 0.2)]]
    return make("Cinderella's Pumpkin Carriage", out + sp)


@design("mermaids_glass_slipper", T)
def glass_slipper(rng):
    shoe = chain([(-2.6, 0.6)], quad((-2.6, 0.6), (-3.0, 1.4), (-2.3, 1.6), 10), quad((-2.3, 1.6), (-1.5, 0.8), (-0.4, 0.9), 14),
                 cubic((-0.4, 0.9), (0.8, 1.1), (1.8, 0.4), (2.6, 0.0), 16), quad((2.6, 0.0), (2.8, -0.3), (2.3, -0.35), 8),
                 cubic((2.3, -0.35), (0.6, -0.4), (-0.6, -0.1), (-1.4, -0.3), 14), [(-1.9, -1.4), (-2.25, -1.4)], [(-2.1, -0.35)],
                 quad((-2.1, -0.35), (-2.6, 0.0), (-2.6, 0.6), 8))
    opening = chain(quad((-2.3, 1.55), (-1.4, 0.7), (-0.4, 0.85), 12))
    shine = [quad((0.4, 0.5), (1.1, 0.4), (1.7, 0.1), 8), quad((-1.6, 0.1), (-1.2, 0.0), (-0.8, 0.05), 6)]
    bow = [lens((0.1, 0.95), (-0.5, 1.4), 0.4), lens((0.1, 0.95), (0.7, 1.4), 0.4), circle(0.1, 0.95, 0.12, 10)]
    cushion = chain([(-3.2, -1.4)], quad((-3.2, -1.4), (0, -1.0), (3.2, -1.4), 20), quad((3.2, -1.4), (3.5, -2.0), (3.2, -2.6), 8),
                    quad((3.2, -2.6), (0, -3.0), (-3.2, -2.6), 20), quad((-3.2, -2.6), (-3.5, -2.0), (-3.2, -1.4), 8))
    tassels = [poly((x, y), (x - 0.15, y - 0.5), (x + 0.15, y - 0.5)) for x, y in [(-3.2, -2.6), (3.2, -2.6)]]
    sp = [sparkle(x, y, r) for x, y, r in [(-1.0, 2.4, 0.35), (1.6, 1.9, 0.28), (2.8, 1.2, 0.2)]]
    out = scene((bow, bow), ([shoe, opening] + shine, [shoe]), (tassels, tassels), ([cushion], [cushion]), (sp, []))
    return make("Cinderella's Glass Slipper", out)


@design("mermaids_rapunzel_tower", T)
def rapunzel_tower(rng):
    tower = chain([(-1.3, -3.4)], [(-1.1, 1.6)], [(1.1, 1.6)], [(1.3, -3.4)])
    roof = poly((-1.6, 1.6), (0, 4.4), (1.6, 1.6))
    eave = [[(-1.6, 1.6), (1.6, 1.6)]]
    window = chain([(-0.55, 0.0), (-0.55, 0.8)], arc(0, 0.8, 0.55, math.pi, 0, 14), [(0.55, 0.0), (-0.55, 0.0)])
    front, back, hints = girl_head(0.0, 0.75, 0.55, "short", "open", None)
    braid_c = cubic((0.35, 0.4), (1.2, -0.2), (0.6, -1.8), (1.8, -3.3), 60)
    braid = tube(braid_c, 0.42)
    plaits = []
    for k in range(3, 58, 4):
        a, b = braid_c[k], braid_c[k + 1]
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy)
        plaits.append(quad((a[0] - dy / n * 0.2, a[1] + dx / n * 0.2), (a[0] + dx / n * 0.2, a[1] + dy / n * 0.2), (a[0] + dy / n * 0.2, a[1] - dx / n * 0.2), 6))
    bow = [lens((1.8, -3.3), (1.4, -3.0), 0.4), lens((1.8, -3.3), (2.2, -3.0), 0.4)]
    stones = keep_in([[(-1.5, y), (1.5, y)] for y in (-2.6, -1.6, -0.6, 1.0)] + [[(x, y), (x, y + 1.0)] for x, y in [(-0.6, -3.4), (0.4, -2.6), (-0.3, -1.6), (0.7, -0.6)]],
                     poly((-1.3, -3.4), (-1.1, 1.6), (1.1, 1.6), (1.3, -3.4)))
    stones = hide(stones, [window])
    flag = [[(0, 4.4), (0, 5.0)], poly((0, 5.0), (0.7, 4.85), (0, 4.65), closed=False)]
    vines = [cubic((-1.25, -3.4), (-1.6, -2.0), (-0.8, -1.5), (-1.2, -0.4), 20)]
    leaves = [lens((-1.35, -2.6), (-1.9, -2.3), 0.4), lens((-1.0, -1.6), (-1.6, -1.2), 0.4)]
    ground = [[(-3.0, -3.4), (3.0, -3.4)]]
    items = [(bow, bow), ([braid] + plaits, [braid])] + front + back + [([window], [chain(window, [window[0]])]),
                                                                          ([roof], [roof]), (leaves, leaves), ([tower] + eave + stones + flag + vines + ground, [])]
    return make("Rapunzel's Tower with Long Braid", scene(*items), hints)


@design("mermaids_frog_prince", T)
def frog_prince(rng):
    body = chain([(-1.6, -1.6)], cubic((-1.6, -1.6), (-2.2, 0.0), (-1.2, 1.0), (0, 1.0), 20), cubic((0, 1.0), (1.2, 1.0), (2.2, 0.0), (1.6, -1.6), 20),
                 [(-1.6, -1.6)])
    head_bumps = [circle(-0.8, 1.15, 0.55, 30), circle(0.8, 1.15, 0.55, 30)]
    eyes_ = [circle(-0.8, 1.2, 0.3, 20), circle(0.8, 1.2, 0.3, 20)]
    mouth = quad((-1.1, 0.35), (0, -0.2), (1.1, 0.35), 16)
    belly = ellipse(0, -0.75, 1.0, 0.8, 40)
    crown = poly((-0.6, 1.5), (-0.7, 2.2), (-0.35, 1.9), (0, 2.4), (0.35, 1.9), (0.7, 2.2), (0.6, 1.5))
    legs = [chain(cubic((-1.5, -0.9), (-2.8, -0.6), (-2.8, -1.8), (-1.8, -1.9), 16)), chain(cubic((1.5, -0.9), (2.8, -0.6), (2.8, -1.8), (1.8, -1.9), 16))]
    feet = [poly((-2.6, -2.0), (-2.9, -2.3), (-2.4, -2.2), (-2.3, -2.5), (-2.0, -2.2), (-1.6, -2.3), (-1.7, -1.95)),
            poly((2.6, -2.0), (2.9, -2.3), (2.4, -2.2), (2.3, -2.5), (2.0, -2.2), (1.6, -2.3), (1.7, -1.95))]
    hands = [poly((-0.7, -1.6), (-0.9, -2.0), (-0.6, -1.85), (-0.45, -2.1), (-0.3, -1.85), (-0.1, -1.95), (-0.3, -1.6)),
             poly((0.7, -1.6), (0.9, -2.0), (0.6, -1.85), (0.45, -2.1), (0.3, -1.85), (0.1, -1.95), (0.3, -1.6))]
    pad = chain(arc(0.0, -2.2, 3.2, math.radians(-80), math.radians(260), 80, ), [(0, -2.2)], [arc(0.0, -2.2, 3.2, math.radians(-80), 0, 1)[0]])
    pad = chain([(0.0, -2.2)], [(3.2 * math.cos(math.radians(-80)), -2.2 + 0.7 * math.sin(math.radians(-80)))],
                [(3.2 * math.cos(t), -2.2 + 0.7 * math.sin(t)) for t in [math.radians(-80 + 340 * i / 80) for i in range(81)]], [(0.0, -2.2)])
    lily = [lens((2.6, -1.6), (2.6, -0.6), 0.3), lens((2.6, -1.6), (2.0, -0.8), 0.3), lens((2.6, -1.6), (3.2, -0.8), 0.3)]
    water = [wave(-3.6, 3.6, -3.3, 0.08, 6, 100)]
    out = scene(([crown], [crown]), (eyes_, eyes_), (head_bumps, head_bumps), (hands, hands), ([belly, mouth], []), ([body], [body]), (feet, feet),
                (legs, []), (lily, lily), ([pad], [pad]), (water, []))
    return make("Frog Prince with a Golden Crown", out, [eye(-0.8, 1.2, 0.13), eye(0.8, 1.2, 0.13)])


@design("mermaids_spinning_wheel", T)
def spinning_wheel(rng):
    wx, wy, r = 0.8, 0.9, 1.9
    wheel = [circle(wx, wy, r, 100), circle(wx, wy, r - 0.25, 90), circle(wx, wy, 0.25, 16)]
    spokes = [[(wx + 0.25 * math.cos(a), wy + 0.25 * math.sin(a)), (wx + (r - 0.25) * math.cos(a), wy + (r - 0.25) * math.sin(a))] for a in [k * math.pi / 6 for k in range(12)]]
    bench = poly((-3.2, -1.5), (2.8, -1.5), (2.8, -1.15), (-3.2, -1.15))
    legs = [[(-2.8, -1.5), (-3.2, -3.0)], [(-2.0, -1.5), (-1.8, -3.0)], [(2.4, -1.5), (2.8, -3.0)], [(1.6, -1.5), (1.4, -3.0)]]
    posts = [[(0.6, -1.15), (0.6, wy)], [(1.0, -1.15), (1.0, wy)]]
    treadle = [[(-0.8, -3.0), (1.2, -2.6)], [(0.2, -2.8), (0.8, wy - 0.6)]]
    spindle_post = rect(-2.4, -1.15, -2.2, 0.6)
    spindle = tube([(-3.2, 0.7), (-1.6, 0.7)], lambda t: 0.12 + 0.18 * math.sin(math.pi * t))
    bobbin = ellipse(-2.3, 0.7, 0.35, 0.3, 16)
    yarn = [quad((-1.6, 0.7), (-0.4, 1.4), (wx, wy + r), 16)]
    distaff = [[(-1.3, -1.15), (-1.3, 2.2)], ellipse(-1.3, 2.7, 0.45, 0.65, 30)]
    fluff = keep_in([quad((-1.8, y), (-1.3, y + 0.25), (-0.8, y), 6) for y in (2.4, 2.8, 3.1)], distaff[1])
    out = scene((spokes + wheel, [wheel[0]]), ([bobbin], [bobbin]), ([spindle], [spindle]), ([spindle_post], [spindle_post]), (distaff + fluff, [distaff[1]]),
                ([bench], [bench]), (posts + legs + treadle + yarn, []))
    return make("Sleeping Beauty's Spinning Wheel", out)


@design("mermaids_magic_mirror", T)
def magic_mirror(rng):
    frame = ellipse(0, 0, 2.2, 2.9, 120)
    glass = ellipse(0, 0, 1.75, 2.45, 110)
    crest = chain(spiral(-0.9, 3.25, 0.05, 0.45, 1.2, 30, rot=0)[::-1], quad((-0.45, 3.25), (0, 3.9), (0.45, 3.25), 10), spiral(0.9, 3.25, 0.05, 0.45, 1.2, 30, rot=math.pi))
    crown = poly((-0.45, 3.6), (-0.55, 4.2), (-0.25, 3.95), (0, 4.45), (0.25, 3.95), (0.55, 4.2), (0.45, 3.6))
    side_scrolls = [spiral(-2.45, 0.0, 0.05, 0.4, 1.2, 30), spiral(2.45, 0.0, 0.05, 0.4, 1.2, 30, rot=math.pi)]
    base = [spiral(-0.6, -3.15, 0.05, 0.35, 1.1, 24, rot=0), spiral(0.6, -3.15, 0.05, 0.35, 1.1, 24, rot=math.pi), poly((-0.3, -2.9), (0, -3.6), (0.3, -2.9))]
    face = ellipse(0, 0.2, 0.9, 1.25, 60)
    eyes_ = [chain(quad((-0.65, 0.5), (-0.35, 0.8), (-0.1, 0.5), 8), quad((-0.1, 0.5), (-0.35, 0.3), (-0.65, 0.5), 8)),
             chain(quad((0.65, 0.5), (0.35, 0.8), (0.1, 0.5), 8), quad((0.1, 0.5), (0.35, 0.3), (0.65, 0.5), 8))]
    mouth = ellipse(0, -0.5, 0.35, 0.18, 20)
    nose = quad((0, 0.3), (0.12, -0.05), (-0.08, -0.1), 6)
    shine = [quad((-1.3, 1.6), (-1.0, 2.0), (-0.6, 2.2), 6)]
    gems = [ellipse(0, -2.68, 0.2, 0.14, 12), circle(-1.95, 1.45, 0.14, 10), circle(1.95, 1.45, 0.14, 10)]
    out = scene((gems, gems), ([crown], [crown]), ([crest], []), (base, [base[2]]), ([frame, glass, face, nose, mouth] + eyes_ + shine, [frame]), (side_scrolls, []))
    return make("Magic Mirror on the Wall", out, [eye(-0.37, 0.53, 0.09), eye(0.37, 0.53, 0.09)])


@design("mermaids_enchanted_rose", T)
def enchanted_rose(rng):
    dome = chain([(-1.8, -1.9)], [(-1.8, 1.6)], arc(0, 1.6, 1.8, math.pi, 0, 40), [(1.8, -1.9)])
    knob = circle(0, 3.65, 0.25, 16)
    base = [rrect(-2.3, -2.4, 2.3, -1.9, 0.12), poly((-2.0, -2.4), (-1.7, -3.0), (1.7, -3.0), (2.0, -2.4))]
    bloom = [spiral(0, 1.3, 0.05, 0.55, 1.6, 50), chain(quad((-0.75, 1.3), (-0.8, 0.5), (0, 0.4), 10), quad((0, 0.4), (0.8, 0.5), (0.75, 1.3), 10)),
             chain(quad((-0.75, 1.3), (-0.95, 1.9), (-0.3, 2.0), 10)), chain(quad((0.75, 1.3), (0.95, 1.9), (0.3, 2.0), 10))]
    stem = quad((0, 0.4), (0.25, -0.7), (0, -1.9), 12)
    leaves = [lens((0.1, -0.6), (1.0, -0.2), 0.35), lens((0.05, -1.1), (-0.9, -0.8), 0.35)]
    fallen = [lens((-1.1, -1.85), (-0.6, -1.7), 0.4), lens((0.9, -1.85), (1.4, -1.75), 0.4)]
    sp = [sparkle(x, y, r) for x, y, r in [(-1.1, 2.4, 0.22), (1.2, 2.6, 0.18), (1.2, -0.9, 0.18), (-2.8, 1.5, 0.3), (2.9, 2.2, 0.3)]]
    out = scene((sp[:3], []), (bloom, [bloom[1]]), (leaves, leaves), ([stem] + fallen, []), ([knob], [knob]), ([dome], []), (base, base), (sp[3:], []))
    return make("Enchanted Rose Under Glass", out)


def pine(x, y, h, w):
    pts = [(x - 0.12 * w, y), (x - 0.12 * w, y + 0.15 * h)]
    for k, f in enumerate((0.15, 0.45, 0.72)):
        ww = w * (1 - 0.28 * k)
        pts += [(x - ww / 2, y + f * h), (x - ww / 4, y + (f + 0.18) * h)]
    pts += [(x, y + h)]
    right = [(2 * x - px, py) for px, py in pts[::-1]]
    return chain(pts, right[1:])


@design("mermaids_woodland_cottage", T)
def woodland_cottage(rng):
    walls = rect(-2.0, -2.6, 1.8, 0.2)
    roof = chain([(-2.5, 0.0)], quad((-2.5, 0.0), (-2.4, 2.6), (-0.1, 2.6), 16), quad((-0.1, 2.6), (2.2, 2.6), (2.3, 0.0), 16), quad((2.3, 0.0), (-0.1, -0.35), (-2.5, 0.0), 20))
    thatch = keep_in([quad((-2.4, y), (-0.1, y - 0.35), (2.3, y), 16) for y in (0.8, 1.6)], roof)
    door = chain([(-0.4, -2.6), (-0.4, -1.4)], arc(0.05, -1.4, 0.45, math.pi, 0, 14), [(0.5, -2.6)])
    wins = [rect(-1.65, -1.6, -0.9, -0.8), rect(0.9, -1.6, 1.55, -0.8)]
    panes = [[(-1.275, -1.6), (-1.275, -0.8)], [(-1.65, -1.2), (-0.9, -1.2)], [(1.225, -1.6), (1.225, -0.8)], [(0.9, -1.2), (1.55, -1.2)]]
    chimney = rect(0.8, 1.6, 1.3, 3.0)
    smoke = [cubic((1.05, 3.1), (0.6, 3.6), (1.6, 3.9), (1.2, 4.4), 16)]
    trees = [pine(-3.1, -2.6, 4.0, 1.6), pine(3.0, -2.6, 3.6, 1.5)]
    path = [cubic((-0.4, -2.6), (-0.6, -3.0), (-1.4, -3.2), (-1.6, -3.6), 12), cubic((0.5, -2.6), (0.6, -3.0), (0.4, -3.3), (0.6, -3.6), 12)]
    bushes = [chain(arc(-2.4, -2.6, 0.45, 0, math.pi, 14)), chain(arc(2.4, -2.6, 0.45, 0, math.pi, 14))]
    out = scene(([chimney], [chimney]), ([roof] + thatch, [roof]), ([door] + wins + panes, [chain(door, [door[0]])] + wins), ([walls], [walls]),
                (bushes, [chain(b, [b[0]]) for b in bushes]), (trees + smoke + path + [[(-3.6, -2.6), (3.6, -2.6)]], []))
    return make("Cottage in the Enchanted Woods", out)


@design("mermaids_red_riding_hood", T)
def red_riding_hood(rng):
    front, back, hints = girl_head(0, 1.6, 0.9, "short", "open", None)
    hood = chain([(0, 2.9)], cubic((0, 2.9), (-1.2, 2.9), (-1.3, 1.6), (-1.0, 0.9), 16), cubic((-1.0, 0.9), (-1.6, -0.6), (-1.9, -1.6), (-2.0, -2.4), 16),
                 [(2.0, -2.4)], cubic((2.0, -2.4), (1.9, -1.6), (1.6, -0.6), (1.0, 0.9), 16), cubic((1.0, 0.9), (1.3, 1.6), (1.2, 2.9), (0, 2.9), 16))
    opening = ellipse(0, 1.55, 0.85, 0.95, 50)
    bow = [lens((0, 0.75), (-0.5, 0.45), 0.4), lens((0, 0.75), (0.5, 0.45), 0.4), [(0, 0.7), (-0.25, 0.1)], [(0, 0.7), (0.25, 0.1)]]
    folds = [quad((-0.6, 0.3), (-0.8, -1.0), (-1.1, -2.3), 10), quad((0.5, 0.3), (0.5, -1.0), (0.4, -2.3), 10)]
    legs = [rect(-0.6, -3.2, -0.3, -2.4), rect(0.3, -3.2, 0.6, -2.4)]
    shoes = [ellipse(-0.55, -3.25, 0.3, 0.15, 14), ellipse(0.55, -3.25, 0.3, 0.15, 14)]
    basket = chain([(0.9, -0.6)], [(1.1, -1.6), (2.5, -1.6), (2.7, -0.6)])
    basket_m = poly((0.9, -0.6), (1.1, -1.6), (2.5, -1.6), (2.7, -0.6))
    handle = arc(1.8, -0.6, 0.9, 0, math.pi, 20)
    weave = keep_in([[(0.8, -0.95), (2.8, -0.95)], [(0.8, -1.3), (2.8, -1.3)]], basket_m)
    cloth = [chain(quad((0.9, -0.6), (1.4, -0.3), (1.8, -0.55), 6), quad((1.8, -0.55), (2.2, -0.3), (2.7, -0.6), 6))]
    hand = circle(1.4, 0.0, 0.17, 12)
    trees = [pine(-3.0, -3.3, 4.2, 1.4), pine(3.1, -3.3, 3.4, 1.2)]
    out = scene(([hand], [hand]), ([basket] + weave + cloth, [basket_m]), ([handle], []), (bow, bow[:2]), *front, ([opening], [opening]), *back,
                ([hood] + folds, [hood]), (shoes, shoes), (legs, legs), (trees, []))
    return make("Little Red Riding Hood with Basket", out, hints)


@design("mermaids_three_pigs_houses", T)
def three_pigs_houses(rng):
    items = []
    # straw
    straw = chain([(-3.5, -2.6)], quad((-3.6, -1.0), (-3.4, -0.6), 8) if False else quad((-3.5, -2.6), (-3.7, -1.2), (-3.1, -0.6), 10), [(-2.35, 0.9)],
                  [(-1.6, -0.6)], quad((-1.6, -0.6), (-1.0, -1.2), (-1.2, -2.6), 10), [(-3.5, -2.6)])
    straw_l = keep_in([[(-2.35 + 0.0, 0.9), (-2.35 + 1.5 * math.cos(a), 0.9 - 4 * math.sin(a))] for a in (1.25, 1.4, 1.57, 1.74, 1.89)], straw)
    sdoor = chain([(-2.65, -2.6), (-2.65, -1.8)], arc(-2.35, -1.8, 0.3, math.pi, 0, 10), [(-2.05, -2.6)])
    # sticks
    sticks = rect(-1.0, -2.6, 1.0, -0.5)
    sroof = poly((-1.3, -0.5), (0, 1.0), (1.3, -0.5))
    st_l = keep_in([[(x, -2.6), (x, -0.5)] for x in (-0.6, -0.2, 0.6)] + [[(-1.3, -0.5), (0, 1.0)]], sticks)
    stdoor = rect(0.0, -2.6, 0.45, -1.7)
    # bricks
    bricks = rect(1.4, -2.6, 3.5, 0.0)
    broof = poly((1.2, 0.0), (2.45, 1.5), (3.7, 0.0))
    chim = rect(3.0, 0.6, 3.35, 1.6)
    rows = [[(1.4, y), (3.5, y)] for y in (-2.1, -1.6, -1.1, -0.55)]
    joints = []
    for k, (y0, y1) in enumerate([(-2.6, -2.1), (-2.1, -1.6), (-1.6, -1.1), (-1.1, -0.55), (-0.55, 0.0)]):
        for x in ([1.9, 2.6, 3.2] if k % 2 == 0 else [2.25, 2.95]):
            joints.append([(x, y0), (x, y1)])
    bdoor = chain([(2.1, -2.6), (2.1, -1.6)], arc(2.45, -1.6, 0.35, math.pi, 0, 10), [(2.8, -2.6)])
    bdoor_m = chain(bdoor, [bdoor[0]])
    ground = [[(-3.7, -2.6), (3.7, -2.6)]]
    out = scene(([sdoor], [chain(sdoor, [sdoor[0]])]), ([straw] + straw_l, [straw]), ([stdoor], [stdoor]), ([sroof], [sroof]), ([sticks] + st_l, [sticks]),
                ([bdoor], [bdoor_m]), ([chim], [chim]), ([broof], [broof]), ([bricks] + rows + joints, [bricks]), (ground, []))
    return make("Three Little Pigs' Houses", out)


@design("mermaids_beanstalk", T)
def beanstalk(rng):
    c = [(0.5 * math.sin(t * 5.5) * (1 - 0.3 * t) - 0.2, -3.6 + 6.0 * t) for t in [i / 120 for i in range(121)]]
    stalk = tube(c, lambda t: 0.6 * (1 - t) + 0.15)
    vine2 = [(0.35 * math.sin(t * 5.5 + 2.0) - 0.2, -3.6 + 5.0 * t) for t in [i / 100 for i in range(101)]]
    leaves = []
    for k in range(10, 115, 13):
        x, y = c[k]
        sgn = 1 if (k // 13) % 2 else -1
        leaves.append(lens((x, y), (x + sgn * 1.1, y + 0.45), 0.4))
    cl = [chain(arc(-1.6, 2.3, 0.7, math.radians(180), math.radians(30), 14), arc(-0.6, 2.7, 0.8, math.radians(150), math.radians(20), 14),
                arc(0.6, 2.5, 0.7, math.radians(130), math.radians(-10), 14), arc(1.6, 2.1, 0.55, math.radians(100), math.radians(-60), 12), [(-2.3, 1.75)])]
    clm = [chain(cl[0], [cl[0][0]])]
    castle = [rect(0.6, 3.0, 2.0, 3.9), rect(0.4, 3.0, 0.9, 4.6), rect(1.7, 3.0, 2.2, 4.6), poly((0.3, 4.6), (0.65, 5.2), (1.0, 4.6)), poly((1.6, 4.6), (1.95, 5.2), (2.3, 4.6))]
    gate = chain([(1.1, 3.0), (1.1, 3.4)], arc(1.3, 3.4, 0.2, math.pi, 0, 8), [(1.5, 3.0)])
    jack_front, jack_back, jh = girl_head(-1.6, -0.5, 0.45, "short", "open", None)
    body = poly((-1.85, -0.8), (-1.35, -0.8), (-1.3, -1.7), (-1.9, -1.7))
    jarms = [limb((-1.4, -0.9), (-1.0, -0.6), (-0.75, -0.3), 0.18), limb((-1.85, -0.95), (-1.9, -0.4), (-1.6, -0.15), 0.18)]
    jlegs = [limb((-1.75, -1.7), (-1.9, -2.2), (-1.6, -2.4), 0.2), limb((-1.45, -1.7), (-1.1, -1.95), (-0.95, -2.3), 0.2)]
    ground = [chain(arc(-0.2, -3.6, 2.6, math.radians(170), math.radians(10), 30))]
    items = [(jarms, jarms)] + jack_front + [([body], [body])] + jack_back + [(jlegs, jlegs), (leaves, leaves), ([stalk], [stalk]),
                                                                             ([gate], []), (castle, castle), (cl, clm), (ground, [])]
    return make("Jack and the Beanstalk", scene(*items), jh)


@design("mermaids_golden_goose", T)
def golden_goose(rng):
    body = chain([(-0.2, 0.9)], cubic((-0.2, 0.9), (0.3, 0.2), (-0.4, -0.6), (-1.6, -0.9), 20), quad((-1.6, -0.9), (-2.8, -1.0), (-3.0, 0.2), 14),
                 quad((-3.0, 0.2), (-2.3, -0.1), (-1.8, 0.2), 8))
    body = chain([(0.9, 1.7)], cubic((0.9, 1.7), (0.6, 0.8), (1.6, -0.2), (0.6, -1.0), 20), cubic((0.6, -1.0), (-0.6, -1.6), (-2.4, -1.4), (-3.0, 0.2), 20),
                 quad((-3.0, 0.2), (-2.0, -0.1), (-1.0, 0.1), 10), cubic((-1.0, 0.1), (0.0, 0.3), (0.2, 1.4), (0.4, 2.6), 16))
    head = chain(arc(0.9, 2.75, 0.55, math.radians(200), math.radians(-30), 30))
    head = chain([(0.4, 2.6)], head, [(0.9, 1.7)])
    beak = poly((1.42, 2.95), (2.1, 2.7), (1.4, 2.5))
    wing = chain([(-0.6, 0.3)], cubic((-0.6, 0.3), (-1.4, 0.4), (-2.2, 0.0), (-2.6, -0.4), 16), cubic((-2.6, -0.4), (-1.6, -0.9), (-0.6, -0.6), (-0.6, 0.3), 16))
    feathers = keep_in([quad((-2.4, y), (-1.4, y + 0.1), (-0.6, y + 0.4), 8) for y in (-0.5, -0.2)], wing)
    legs = [[(-0.6, -1.25), (-0.6, -1.9)], [(0.0, -1.1), (0.0, -1.9)]]
    nest = chain([(-1.8, -1.9)], quad((-1.8, -1.9), (0.6, -3.2), 2.6 * 0 + 0.0 or (2.6, -1.9), 20) if False else quad((-1.8, -1.9), (0.4, -3.4), (2.6, -1.9), 20), [(-1.8, -1.9)])
    twigs = keep_in([quad((-2.0, y), (0.4, y - 0.4), (2.8, y + 0.1), 12) for y in (-2.2, -2.5)], nest)
    egg = ellipse(1.6, -1.35, 0.5, 0.62, 30)
    shine = [arc(1.6, -1.35, 0.35, math.radians(110), math.radians(160), 6)]
    sp = [sparkle(2.6, -0.4, 0.3), sparkle(2.9, -1.2, 0.2)]
    out = scene(([beak], [beak]), ([head], [chain(head, [head[0]])]), ([wing] + feathers, [wing]), ([body], [chain(body, [body[0]])]),
                ([egg] + shine, [egg]), (twigs + [nest], [nest]), (legs + sp, []))
    return make("Goose That Laid the Golden Egg", out, [eye(1.05, 2.9, 0.09)])


@design("mermaids_genie_lamp", T)
def genie_lamp(rng):
    body = chain([(-1.6, -1.4)], cubic((-1.6, -1.4), (-2.2, -1.3), (-2.0, -0.2), (-1.0, -0.1), 16), [(0.6, -0.1)],
                 cubic((0.6, -0.1), (1.4, -0.1), (2.0, -0.6), (3.2, 0.3), 16), quad((3.2, 0.3), (3.4, 0.45), (3.3, 0.15), 4),
                 cubic((3.3, 0.15), (2.4, -1.0), (1.6, -1.4), (0.8, -1.4), 16), [(-1.6, -1.4)])
    body = chain([(-1.4, -1.4)], cubic((-1.4, -1.4), (-2.4, -1.2), (-2.0, -0.1), (-0.8, -0.1), 16), [(0.5, -0.1)],
                 cubic((0.5, -0.1), (1.3, -0.1), (2.0, -0.3), (3.3, 0.5), 16), [(3.4, 0.3)],
                 cubic((3.4, 0.3), (2.4, -0.6), (1.7, -1.4), (0.6, -1.4), 16), [(-1.4, -1.4)])
    lid = chain([(-1.0, -0.1)], cubic((-1.0, -0.1), (-0.9, 0.6), (0.3, 0.6), (0.4, -0.1), 14))
    knob = circle(-0.3, 0.75, 0.2, 14)
    handle = tube(cubic((-1.9, -0.4), (-3.0, -0.2), (-3.1, -1.4), (-1.9, -1.2), 20), 0.25)
    foot = poly((-0.9, -1.4), (-1.2, -1.9), (0.5, -1.9), (0.2, -1.4))
    band = keep_in([quad((-2.2, -0.75), (-0.4, -1.0), (1.6, -0.75), 12)], chain(body, [body[0]]))
    smoke = tube(chain(cubic((3.4, 0.5), (3.6, 1.6), (1.6, 1.4), (1.8, 2.4), 24), cubic((1.8, 2.4), (2.0, 3.2), (0.4, 3.0), (0.0, 3.6), 20)), lambda t: 0.25 + 0.6 * t)
    puffs = [circle(-0.5, 3.8, 0.55, 24), circle(0.3, 4.1, 0.6, 24), circle(-0.1, 3.4, 0.4, 20)]
    sp = [sparkle(x, y, r) for x, y, r in [(2.6, 3.4, 0.3), (-2.0, 2.6, 0.3), (-1.4, 1.6, 0.2), (3.0, 2.2, 0.2)]]
    out = scene(([knob], [knob]), ([lid], [chain(lid, [lid[0]])]), ([body] + band, [chain(body, [body[0]])]), ([foot], [foot]), ([handle], [handle]),
                (puffs, puffs), ([smoke], [smoke]), (sp, []))
    return make("Magic Genie Lamp", out)


@design("mermaids_flying_carpet", T)
def flying_carpet(rng):
    def P(u, v):
        x = -3.0 + 6.0 * u + 0.6 * v
        y = -0.6 + 1.6 * v + 0.35 * math.sin(math.pi * 2 * u)
        return (x, y)
    edge = [P(u / 40, 0) for u in range(41)] + [P(1, v / 10) for v in range(1, 11)] + [P(1 - u / 40, 1) for u in range(1, 41)] + [P(0, 1 - v / 10) for v in range(1, 11)]
    border = [P(0.06 + 0.88 * u / 40, 0.18) for u in range(41)] + [P(0.94, 0.18 + 0.64 * v / 10) for v in range(1, 11)] + \
             [P(0.94 - 0.88 * u / 40, 0.82) for u in range(1, 41)] + [P(0.06, 0.82 - 0.64 * v / 10) for v in range(1, 11)]
    diamond = [P(0.5, 0.3), P(0.62, 0.5), P(0.5, 0.7), P(0.38, 0.5), P(0.5, 0.3)]
    d2 = [P(0.2, 0.4), P(0.26, 0.5), P(0.2, 0.6), P(0.14, 0.5), P(0.2, 0.4)]
    d3 = [P(0.8, 0.4), P(0.86, 0.5), P(0.8, 0.6), P(0.74, 0.5), P(0.8, 0.4)]
    tassels = []
    for u in (0.0, 1.0):
        for v in (0.2, 0.5, 0.8):
            x, y = P(u, v)
            sx = -1 if u == 0 else 1
            tassels.append([(x, y), (x + sx * 0.45, y - 0.1)])
    moon = chain(arc(2.2, 2.6, 0.9, math.radians(60), math.radians(300), 30), arc(2.6, 2.75, 0.75, math.radians(260), math.radians(95), 30)[::-1][::-1])
    moon = chain(arc(2.2, 2.6, 0.9, math.radians(70), math.radians(290), 30), arc(2.55, 2.6, 0.72, math.radians(242), math.radians(118), 30))
    stars_ = [star(x, y, r) for x, y, r in [(-2.5, 2.8, 0.3), (-1.0, 3.3, 0.22), (0.6, 2.6, 0.25), (-2.9, 1.4, 0.2)]]
    dunes = [chain(quad((-3.6, -2.8), (-2.0, -1.8), (-0.4, -2.8), 16), quad((-0.4, -2.8), (1.4, -1.6), (3.6, -2.7), 16))]
    out = scene(([chain(edge, [edge[0]]), border, diamond, d2, d3], [chain(edge, [edge[0]])]), (tassels + [chain(moon, [moon[0]])] + stars_ + dunes, []))
    return make("Flying Magic Carpet", out)


def bean(cx, cy, s, rot=0.0):
    pts = chain(arc(0, 0, 1.0, math.radians(200), math.radians(340), 14), quad((0.94, -0.34), (1.3, 0.4), (0.6, 0.55), 8),
                quad((0.6, 0.55), (0.0, 0.2), (-0.6, 0.55), 8), quad((-0.6, 0.55), (-1.3, 0.4), (-0.94, -0.34), 8))
    return transform(pts, cx, cy, s, rot)


@design("mermaids_magic_beans", T)
def magic_beans(rng):
    sack = chain([(-1.6, -0.4)], cubic((-1.6, -0.4), (-3.2, -0.9), (-3.4, -2.9), (-2.2, -3.0), 20), [(-0.8, -3.0)],
                 cubic((-0.8, -3.0), (0.4, -2.9), (0.2, -0.9), (-1.0, -0.4), 20))
    ruffle = chain([(-1.6, -0.4)], quad((-1.6, -0.4), (-2.2, 0.0), (-2.0, 0.35), 6), quad((-2.0, 0.35), (-1.7, 0.1), (-1.4, 0.4), 6),
                   quad((-1.4, 0.4), (-1.1, 0.1), (-0.8, 0.35), 6), quad((-0.8, 0.35), (-0.6, 0.0), (-1.0, -0.4), 6))
    tie = [[(-1.65, -0.45), (-0.95, -0.45)], [(-1.3, -0.45), (-1.6, -1.0)], [(-1.3, -0.45), (-1.0, -1.0)]]
    beans = [bean(x, y, 0.32, r) for x, y, r in [(0.6, -2.85, 0.2), (1.3, -2.9, -0.3), (0.9, -2.4, 0.6), (2.2, -2.95, 0.1)]]
    sprout_b = bean(2.4, -2.1, 0.4, -0.2)
    stem = cubic((2.4, -1.95), (2.0, -0.6), (3.0, 0.6), (2.2, 2.2), 30)
    stem_t = tube(stem, lambda t: 0.25 * (1 - t) + 0.08)
    tendrils = [spiral(1.55, 0.4, 0.05, 0.35, 1.2, 30, rot=0.0), spiral(3.15, 1.45, 0.05, 0.3, 1.2, 30, rot=math.pi)]
    t_link = [quad((2.35, 0.0), (2.0, 0.5), (1.85, 0.45), 8), quad((2.75, 1.2), (3.0, 1.6), (3.3, 1.5), 8)]
    leaves = [heart(1.6, -0.7, 0.4), heart(3.0, 0.3, 0.38), heart(1.8, 2.3, 0.35)]
    sp = [sparkle(x, y, r) for x, y, r in [(0.6, 1.4, 0.3), (-0.8, 2.4, 0.25), (3.2, -1.0, 0.25), (-2.6, 1.4, 0.25)]]
    out = scene((leaves, leaves), (tendrils + t_link, []), ([stem_t], [stem_t]), ([sprout_b], [sprout_b]), (beans, beans), ([ruffle], []),
                ([sack] + tie, [chain(sack, [sack[0]])]), (sp + [[(-3.4, -3.0), (3.4, -3.0)]], []))
    return make("Bag of Magic Beans", out)


@design("mermaids_storybook", T)
def storybook(rng):
    bk, bm = book(0, -2.8, 3.3, 2.2, 0.0)
    cover = chain([(-3.4, -2.5)], [(-3.5, -0.4)], quad((-3.5, -0.4), (-1.6, 0.0), (0, -0.55), 10), quad((0, -0.55), (1.6, 0.0), (3.5, -0.4), 10), [(3.4, -2.5)],
                  quad((3.4, -2.5), (1.6, -2.1), (0, -2.95), 10), quad((0, -2.95), (-1.6, -2.1), (-3.4, -2.5), 10))
    castle = []
    keep = rect(-0.9, -0.9, 0.9, 1.4)
    t1 = rect(-1.8, -0.9, -1.0, 2.0)
    t2 = rect(1.0, -0.9, 1.8, 2.0)
    r1 = poly((-2.0, 2.0), (-1.4, 3.1), (-0.8, 2.0))
    r2 = poly((0.8, 2.0), (1.4, 3.1), (2.0, 2.0))
    battle = chain([(-0.9, 1.4)], [(-0.9, 1.75), (-0.55, 1.75), (-0.55, 1.4), (-0.2, 1.4), (-0.2, 1.75), (0.2, 1.75), (0.2, 1.4), (0.55, 1.4),
                                    (0.55, 1.75), (0.9, 1.75), (0.9, 1.4)])
    gate = chain([(-0.4, -0.9), (-0.4, -0.1)], arc(0, -0.1, 0.4, math.pi, 0, 12), [(0.4, -0.9)])
    wins = [arch_window(-1.4, 0.6, 0.15, 0.6), arch_window(1.4, 0.6, 0.15, 0.6), arch_window(0, 0.5, 0.18, 0.55)]
    flags = [[(-1.4, 3.1), (-1.4, 3.7)], poly((-1.4, 3.7), (-0.8, 3.55), (-1.4, 3.4), closed=False), [(1.4, 3.1), (1.4, 3.7)], poly((1.4, 3.7), (2.0, 3.55), (1.4, 3.4), closed=False)]
    stars_ = [star(x, y, r) for x, y, r in [(-2.8, 2.6, 0.3), (2.9, 2.4, 0.3), (-2.3, 3.6, 0.2), (2.4, 3.6, 0.22)]]
    moon = chain(arc(0.0, 3.6, 0.45, math.radians(60), math.radians(300), 20), arc(0.25, 3.6, 0.36, math.radians(245), math.radians(115), 20))
    out = scene((flags, []), ([r1], [r1]), ([r2], [r2]), ([gate] + wins, []), ([keep, battle], [keep]), ([t1], [t1]), ([t2], [t2]), (bk, bm), ([cover], []),
                (stars_ + [chain(moon, [moon[0]])], []))
    return make("Open Storybook with Pop-Up Castle", out)


@design("mermaids_fairy_ring", T)
def fairy_ring(rng):
    ms = []
    n = 9
    for k in range(n):
        a = TAU * k / n + 0.2
        x, y = 2.7 * math.cos(a), -0.8 + 1.2 * math.sin(a)
        sc = 1.0 - 0.25 * (y + 0.8) / 1.2
        ms.append((y, mushroom(x, y - 0.4 * sc, 0.55 * sc, 0.6 * sc, 0.6 * sc, spots=(k % 2 == 0))))
    ms.sort(key=lambda t: t[0])
    items = []
    for _, m in ms:
        items += m
    sp = [sparkle(x, y, r) for x, y, r in [(-1.3, 1.4, 0.25), (1.4, 1.6, 0.22), (0.0, 2.9, 0.3), (-2.2, 2.4, 0.22), (2.3, 2.6, 0.22)]]
    f, fm, fh = fairy(0, -0.4, 0.42, arms=("wave", "wave"), legs="stand", hair="bun")
    ring = [ellipse(0, -1.25, 3.2, 1.45, 120)]
    grass = [zigzag(-3.6, -2.0, -2.9, 0.15, 6), zigzag(2.0, 3.6, -2.9, 0.15, 6)]
    flowers = [circle(x, y, 0.15, 12) for x, y in [(-1.6, -2.5), (1.6, -2.6)]] + [circle(x + 0.27 * math.cos(a), y + 0.27 * math.sin(a), 0.13, 10) for x, y in [(-1.6, -2.5), (1.6, -2.6)] for a in [TAU * k / 5 for k in range(5)]]
    front_ms = [i for y, m in ms if y < -0.8 for i in m]
    back_ms = [i for y, m in ms if y >= -0.8 for i in m]
    out = scene(*front_ms, (f, fm), *back_ms, (sp + grass + flowers + ring, []))
    return make("Fairy Ring of Mushrooms", out, fh)


def pointy_hat(cx, cy, s, curl=1):
    """Pixie / elf hat; (cx, cy) is the middle of the brim."""
    P = lambda x, y: (cx + x * s, cy + y * s)
    hat = chain([P(-0.75, 0.0)], quad(P(-0.75, 0.0), P(-0.3, 1.0), P(0.3 * curl, 1.6), 12), quad(P(0.3 * curl, 1.6), P(0.9 * curl, 1.8), P(1.0 * curl, 1.3), 8),
                quad(P(1.0 * curl, 1.3), P(0.8 * curl, 1.5), P(0.5 * curl, 1.4), 6), quad(P(0.5 * curl, 1.4), P(0.4, 0.8), P(0.75, 0.0), 10), [P(-0.75, 0.0)])
    brim = chain(quad(P(-0.85, 0.05), P(0, -0.25), P(0.85, 0.05), 12), quad(P(0.85, 0.05), P(0, 0.12), P(-0.85, 0.05), 12))
    return [hat, brim], [hat, brim]


@design("mermaids_pixie_toadstool", T)
def pixie_toadstool(rng):
    shroom = mushroom(0, -3.4, 2.4, 1.8, 1.7, spots=True)
    hat, hm = pointy_hat(0, 2.85, 0.9, 1)
    ears = [poly((-0.5, 2.3), (-1.05, 2.6), (-0.55, 2.0)), poly((0.5, 2.3), (1.05, 2.6), (0.55, 2.0))]
    m, mm, mh = fairy(0, 0.2, 0.75, arms=("rest", "wave"), legs="sit", hair="short", held=[(hat, hm), (ears, ears)])
    sp = [sparkle(x, y, r) for x, y, r in [(-2.6, 2.6, 0.3), (2.6, 3.0, 0.25), (2.9, 1.2, 0.2)]]
    grass = [zigzag(-3.4, 3.4, -3.4, 0.12, 18)]
    out = scene((m, mm), *shroom, (sp + grass, []))
    return make("Pixie on a Toadstool", out, mh)


def tooth(cx, cy, s):
    pts = chain([(-0.9, 0.6)], cubic((-0.9, 0.6), (-1.1, 1.4), (-0.4, 1.5), (0, 1.15), 12), cubic((0, 1.15), (0.4, 1.5), (1.1, 1.4), (0.9, 0.6), 12),
                cubic((0.9, 0.6), (0.85, -0.2), (0.75, -1.2), (0.45, -1.3), 12), quad((0.45, -1.3), (0.2, -0.6), (0, -0.4), 8),
                quad((0, -0.4), (-0.2, -0.6), (-0.45, -1.3), 8), cubic((-0.45, -1.3), (-0.75, -1.2), (-0.85, -0.2), (-0.9, 0.6), 12))
    return transform(pts, cx, cy, s, 0.0)


@design("mermaids_tooth_fairy", T)
def tooth_fairy(rng):
    t = tooth(1.75, 1.1, 0.8)
    shine = [quad((1.25, 1.6), (1.4, 1.9), (1.7, 1.95), 6)]
    m, mm, mh = fairy(-0.6, -0.2, 0.95, arms=(((0.62, 1.2), (1.2, 1.4), (1.95, 1.2)), ((0.62, 1.2), (1.3, 0.8), (2.0, 1.0))), legs="fly", hair="pony",
                      crown="tiara", held=[([t] + shine, [t])])
    m, mm, mh = fairy(-0.8, -0.3, 0.95, arms=("low", ((0.62, 1.2), (1.4, 1.0), (2.0, 1.4))), legs="fly", hair="pony", crown="tiara")
    w = wand(-2.3, -0.1, -3.0, 1.0, 0.35)
    moon = chain(arc(2.4, 3.0, 0.8, math.radians(70), math.radians(290), 30), arc(2.75, 3.0, 0.64, math.radians(242), math.radians(118), 30))
    sp = [sparkle(x, y, r) for x, y, r in [(-2.5, 3.0, 0.3), (0.8, 3.4, 0.2), (2.9, -1.6, 0.25), (-2.9, -2.4, 0.2)]]
    out = scene(([t] + shine, [t]), (m, mm), (sp + [chain(moon, [moon[0]])], []))
    return make("Tooth Fairy Carrying a Tooth", out, mh)


@design("mermaids_wishing_star", T)
def wishing_star(rng):
    st = star(1.6, 2.2, 1.2, 5, 0.5)
    trail = [cubic((0.6, 1.8), (-0.6, 1.2), (-1.8, 1.5), (-3.2, 0.9), 20), cubic((0.8, 1.4), (-0.4, 0.6), (-1.6, 0.8), (-2.9, 0.2), 20)]
    tiny = [sparkle(x, y, r) for x, y, r in [(-1.2, 1.9, 0.2), (-2.2, 1.6, 0.18), (-0.4, 0.4, 0.18), (-2.0, 0.2, 0.15)]]
    houses = []
    for x0, w, h, roof in [(-3.4, 2.0, 1.6, 1.0), (-1.4, 1.6, 2.2, 0.9), (0.2, 1.8, 1.4, 1.1), (2.0, 1.5, 1.9, 0.8)]:
        body = rect(x0, -3.2, x0 + w, -3.2 + h)
        rf = poly((x0 - 0.15, -3.2 + h), (x0 + w / 2, -3.2 + h + roof), (x0 + w + 0.15, -3.2 + h))
        win = rect(x0 + w / 2 - 0.25, -3.2 + h * 0.45, x0 + w / 2 + 0.25, -3.2 + h * 0.45 + 0.5)
        houses.append(([rf], [rf]))
        houses.append(([body, win, [(x0 + w / 2, -3.2 + h * 0.45), (x0 + w / 2, -3.2 + h * 0.45 + 0.5)]], [body]))
    chim = rect(-1.2, -0.9, -0.9, -0.05)
    moon = chain(arc(-2.4, 3.0, 0.6, math.radians(70), math.radians(290), 24), arc(-2.15, 3.0, 0.48, math.radians(242), math.radians(118), 24))
    out = scene(([st, star(1.6, 2.2, 0.6, 5, 0.5)], [st]), (houses[:2], []) if False else (houses[0][0], houses[0][1]), *houses[1:],
                ([chim], [chim]), (trail + tiny + [chain(moon, [moon[0]])], []))
    return make("Wishing Star over the Rooftops", out)


def shoe(cx, cy, s, flip=False):
    pts = chain([(-1.2, 0.0)], quad((-1.3, 0.6), (-0.9, 0.9), 8) if False else quad((-1.2, 0.0), (-1.3, 0.7), (-0.8, 0.85), 8),
                quad((-0.8, 0.85), (-0.2, 0.55), (0.3, 0.6), 8), cubic((0.3, 0.6), (0.9, 0.6), (1.3, 0.3), (1.3, 0.0), 10), [(-1.2, 0.0)])
    sole = rect(-1.25, -0.18, 1.35, 0.0)
    heel = rect(-1.2, -0.45, -0.7, -0.18)
    buckle = rect(-0.35, 0.35, 0.05, 0.75)
    opening = quad((-0.8, 0.85), (-0.3, 0.7), (0.0, 0.62), 6)
    parts = [pts, sole, heel, buckle, opening]
    return place(parts, cx, cy, s, flip=flip), place([pts, sole, heel, buckle], cx, cy, s, flip=flip)


@design("mermaids_elves_shoemaker", T)
def elves_shoemaker(rng):
    bench = [rect(-3.4, -1.3, 3.4, -0.9), [(-3.0, -1.3), (-3.0, -3.2)], [(3.0, -1.3), (3.0, -3.2)], [(-2.6, -1.3), (-2.6, -3.2)], [(2.6, -1.3), (2.6, -3.2)]]
    s1, s1m = shoe(-1.9, -0.45, 0.9)
    s2, s2m = shoe(-0.2, -0.45, 0.9)
    hammer = [rect(1.2, -0.9, 2.6, -0.75), rect(2.5, -0.95, 2.9, -0.45)]
    hat, hm = pointy_hat(1.6, 1.8, 0.55, -1)
    front, back, hints = girl_head(1.6, 1.4, 0.6, "short", "open", None)
    ears = [poly((1.27, 1.45), (0.95, 1.7), (1.3, 1.2)), poly((1.93, 1.45), (2.25, 1.7), (1.9, 1.2))]
    body = poly((1.3, 1.0), (1.9, 1.0), (2.2, -0.2), (1.0, -0.2))
    belt = [[(1.1, 0.3), (2.1, 0.3)]]
    legs = [[(1.35, -0.2), (1.35, -0.75)], [(1.85, -0.2), (1.85, -0.75)]]
    feet = [poly((1.4, -0.75), (1.0, -0.75), (0.9, -0.6), closed=False), poly((1.8, -0.75), (2.2, -0.75), (2.3, -0.6), closed=False)]
    arm = limb((1.3, 0.8), (0.9, 0.5), (0.6, 0.65), 0.2)
    needle = [[(0.55, 0.7), (0.15, 0.95)], cubic((0.15, 0.95), (-0.2, 1.4), (0.4, 1.7), (0.1, 2.2), 14)]
    candle = [rect(-3.1, -0.9, -2.7, 0.3), lens((-2.9, 0.4), (-2.9, 1.0), 0.3)]
    items = [(hat, hm), (ears, ears)] + front + back + [([arm], [arm]), ([body] + belt, [body]), (legs + feet, []), (s1, s1m), (s2, s2m), (hammer, hammer),
                                                    (candle, candle), (bench + needle, [bench[0]])]
    return make("The Elves and the Shoemaker", scene(*items), hints)


@design("mermaids_puss_in_boots", T)
def puss_in_boots(rng):
    head = circle(0, 1.8, 0.85, 50)
    ears = [poly((-0.75, 2.15), (-0.8, 3.0), (-0.2, 2.6)), poly((0.75, 2.15), (0.8, 3.0), (0.2, 2.6))]
    brim = ellipse(0.1, 2.55, 1.6, 0.32, 50, rot=0.12)
    crown = chain(arc(0.05, 2.55, 0.75, math.radians(10), math.radians(170), 20))
    plume = tube(cubic((0.6, 2.9), (1.4, 3.6), (2.4, 3.4), (2.6, 2.4), 24), lambda t: 0.6 * math.sin(math.pi * t) ** 0.7 + 0.05)
    eyes_ = [ellipse(-0.33, 1.85, 0.2, 0.25, 16), ellipse(0.33, 1.85, 0.2, 0.25, 16)]
    nose = poly((-0.1, 1.5), (0.1, 1.5), (0, 1.38))
    mouth = [arc(-0.12, 1.38, 0.12, math.pi, TAU, 8), arc(0.12, 1.38, 0.12, math.pi, TAU, 8)]
    whisk = [[(sx * 0.35, 1.45 + d), (sx * 1.25, 1.5 + 2 * d)] for sx in (-1, 1) for d in (0.05, -0.12)]
    cape = chain([(-0.6, 1.0)], quad((-0.6, 1.0), (-1.8, -0.5), (-1.7, -1.6), 12), [(1.7, -1.6)], quad((1.7, -1.6), (1.8, -0.5), (0.6, 1.0), 12))
    body = poly((-0.55, 1.0), (0.55, 1.0), (0.75, -1.2), (-0.75, -1.2))
    belt = rect(-0.72, -0.35, 0.72, -0.1)
    buckle = rect(-0.18, -0.4, 0.18, -0.05)
    arms = [limb((-0.5, 0.8), (-1.2, 0.2), (-0.7, -0.3), 0.3), limb((0.5, 0.8), (1.2, 0.8), (1.5, 1.4), 0.3)]
    paws = [circle(-0.65, -0.35, 0.18, 12), circle(1.55, 1.5, 0.18, 12)]
    legs = [rect(-0.6, -1.9, -0.15, -1.2), rect(0.15, -1.9, 0.6, -1.2)]
    boots = [chain([(-0.7, -1.7)], [(-0.75, -2.0), (-0.65, -2.9), (-1.3, -2.9), (-1.3, -3.2), (-0.1, -3.2), (-0.15, -2.0), (-0.05, -1.7)]),
             chain([(0.7, -1.7)], [(0.75, -2.0), (0.65, -2.9), (1.3, -2.9), (1.3, -3.2), (0.1, -3.2), (0.15, -2.0), (0.05, -1.7)])]
    boots_m = [chain(b, [b[0]]) for b in boots]
    cuffs = [[(-0.75, -2.0), (-0.15, -2.0)], [(0.75, -2.0), (0.15, -2.0)]]
    sword = [[(0.7, -0.6), (2.6, -2.4)], rect(0.45, -0.55, 0.9, -0.45)]
    tail = tube(cubic((0.7, -1.0), (2.2, -1.0), (2.6, 0.2), (2.0, 0.6), 20), 0.28)
    items = [(eyes_ + [nose] + mouth + whisk, []), ([brim], [brim]), ([crown], [chain(crown, [crown[0]])]), ([plume], [plume]), ([head], [head]), (ears, ears),
             (paws, paws), (arms, arms), ([buckle], [buckle]), ([belt], [belt]), ([body], [body]), (boots + cuffs, boots_m), (legs, legs), (sword, [sword[1]]),
             ([cape], [chain(cape, [cape[0]])]), ([tail], [tail])]
    return make("Puss in Boots", scene(*items), [eye(-0.33, 1.83, 0.09), eye(0.33, 1.83, 0.09)])


def bowl(cx, cy, w, h):
    rim = ellipse(cx, cy, w, 0.25 * w, 40)
    body = chain([(cx - w, cy)], quad((cx - w, cy), (cx - w, cy - h), (cx - 0.4 * w, cy - h), 10), [(cx + 0.4 * w, cy - h)],
                 quad((cx + 0.4 * w, cy - h), (cx + w, cy - h), (cx + w, cy), 10))
    foot = rect(cx - 0.35 * w, cy - h - 0.15, cx + 0.35 * w, cy - h)
    por = keep_in([quad((cx - w, cy - 0.02), (cx, cy + 0.2 * w), (cx + w, cy - 0.02), 12)], rim)
    return [rim, body, foot] + por, [rim, chain(body, [body[0]]), foot]


@design("mermaids_three_bowls", T)
def three_bowls(rng):
    items = []
    for cx, w, h in [(-2.2, 1.2, 1.1), (0.4, 0.95, 0.85), (2.4, 0.7, 0.65)]:
        b, bm = bowl(cx, -1.3, w, h)
        spoon = [[(cx + 0.3 * w, -1.25), (cx + 1.0 * w, 0.0)], ellipse(cx + 1.08 * w, 0.18, 0.12 * w + 0.05, 0.22 * w + 0.05, 12, rot=0.5)]
        steam = [cubic((cx + d, -0.9), (cx + d - 0.3, -0.3), (cx + d + 0.3, 0.1), (cx + d, 0.7 * w + 0.3), 12) for d in (-0.3 * w, 0.2 * w)]
        items.append((spoon, [spoon[1]]))
        items.append((b, bm))
        items.append((steam, []))
    cloth = [chain([(-3.6, -2.4)], scallop([(-3.6, -2.4), (3.6, -2.4)], -0.18, 12), [(3.6, -2.4)]), [(-3.6, -2.4), (-3.6, -1.6)], [(3.6, -2.4), (3.6, -1.6)]]
    table = [[(-3.6, -1.6), (3.6, -1.6)]]
    out = scene(*items, (cloth + table, []))
    return make("Goldilocks and the Three Bowls", out)


def mouse(cx, cy, s, flip=False):
    body = chain(quad((0.8, 0.0), (0.3, 0.75), (-0.6, 0.3), 12), quad((-0.6, 0.3), (-0.8, 0.0), (-0.6, -0.1), 6), [(0.8, 0.0)])
    ear = circle(0.3, 0.55, 0.2, 14)
    tail = cubic((-0.65, 0.05), (-1.2, 0.1), (-1.2, 0.6), (-1.6, 0.5), 12)
    feet = [[(-0.3, -0.05), (-0.35, -0.2)], [(0.4, -0.02), (0.45, -0.18)]]
    items = [([ear], [ear]), ([body], [body]), ([tail] + feet, [])]
    return place_items(items, cx, cy, s, flip=flip), place([eye(0.5, 0.2, 0.05)], cx, cy, s, flip=flip)


@design("mermaids_pied_piper", T)
def pied_piper(rng):
    front, back, hints = girl_head(-1.0, 2.0, 0.75, "short", "closed", None)
    hat = chain([(-1.6, 2.45)], quad((-1.6, 2.45), (-1.2, 3.3), (-0.3, 3.0), 10), [(-0.35, 2.55)], quad((-0.35, 2.55), (-1.0, 2.75), (-1.6, 2.45), 10))
    feather = tube(cubic((-0.5, 2.9), (0.2, 3.4), (0.4, 3.6), (0.9, 3.5), 16), lambda t: 0.35 * math.sin(math.pi * t) + 0.03)
    body = poly((-1.5, 1.4), (-0.5, 1.4), (-0.3, -0.6), (-1.7, -0.6))
    diam = keep_in([[(-1.9 + 0.5 * k, -0.6), (-1.9 + 0.5 * k + 2.0, 1.4)] for k in range(-1, 3)] + [[(-1.9 + 0.5 * k, 1.4), (-1.9 + 0.5 * k + 2.0, -0.6)] for k in range(-1, 3)], body)
    legs = [limb((-1.3, -0.6), (-1.4, -1.6), (-1.6, -2.5), 0.3), limb((-0.7, -0.6), (-0.5, -1.6), (-0.1, -2.4), 0.3)]
    shoes = [poly((-1.45, -2.45), (-2.1, -2.7), (-1.4, -2.75)), poly((-0.2, -2.35), (0.45, -2.55), (-0.1, -2.65))]
    pipe = rect(-0.75, 1.55, 1.6, 1.75)
    holes = [circle(x, 1.65, 0.05, 6) for x in ()]
    arms = [limb((-1.4, 1.2), (-0.6, 0.6), (0.1, 1.5), 0.24), limb((-0.6, 1.2), (0.4, 0.9), (0.9, 1.55), 0.24)]
    hands = [circle(0.1, 1.6, 0.15, 12), circle(0.9, 1.6, 0.15, 12)]
    notes = [[(1.9, 2.4), (1.9, 3.1), (2.3, 3.3), (2.3, 2.6)], circle(1.75, 2.35, 0.17, 12), circle(2.15, 2.55, 0.17, 12), [(2.8, 1.9), (2.8, 2.6)], circle(2.65, 1.85, 0.17, 12)]
    mice = []
    mh = []
    for x, y, s_ in [(0.9, -2.5, 0.55), (2.0, -2.6, 0.5), (3.0, -2.5, 0.45)]:
        it_, h_ = mouse(x, y, s_, flip=True)
        mice += it_
        mh += h_
    ground = [[(-3.0, -2.75), (3.6, -2.75)]]
    items = [(hands, hands), ([pipe] + holes, [pipe]), (arms, arms), ([hat], [chain(hat, [hat[0]])]), ([feather], [feather])] + front + back + \
            [([body] + diam, [body]), (shoes, shoes), (legs, legs)] + mice + [(notes + ground, [])]
    return make("Pied Piper and the Mice", scene(*items), hints + mh)


@design("mermaids_swan_princess", T)
def swan_princess(rng):
    body = chain([(-0.4, 0.2)], cubic((-0.4, 0.2), (0.4, -0.6), (2.4, -0.4), (2.9, 0.8), 20), quad((2.9, 0.8), (2.4, 0.4), (2.2, 0.3), 6),
                 cubic((2.2, 0.3), (2.6, -1.0), (1.0, -1.6), (-1.0, -1.5), 20), cubic((-1.0, -1.5), (-2.2, -1.4), (-2.6, -0.6), (-2.2, -0.2), 16),
                 quad((-2.2, -0.2), (-1.6, -0.6), (-1.0, -0.2), 10))
    wing = chain([(-0.2, -0.2)], cubic((-0.2, -0.2), (0.6, 0.6), (1.6, 0.5), (2.4, 1.3), 20),
                 scallop(cubic((2.4, 1.3), (2.0, -0.4), (0.8, -0.9), (-0.2, -0.2), 20), 0.12, 5))
    neck_c = chain(cubic((-1.6, -0.3), (-1.0, 0.8), (-2.6, 1.6), (-2.0, 2.7), 30))
    neck = tube(neck_c, lambda t: 0.6 * (1 - t) + 0.32)
    head = ellipse(-1.75, 2.85, 0.55, 0.38, 30, rot=-0.3)
    beak = poly((-1.3, 2.75), (-0.5, 2.45), (-1.25, 2.5))
    crown = poly((-2.15, 3.15), (-2.2, 3.7), (-1.95, 3.45), (-1.75, 3.85), (-1.55, 3.4), (-1.3, 3.6), (-1.35, 3.05))
    ripples = [ellipse(0, -1.6, 3.4, 0.45, 100), ellipse(0.2, -1.65, 2.4, 0.25, 80)]
    reeds = [tube([(3.0, -2.6), (3.1, 0.8)], 0.08), ellipse(3.1, 1.2, 0.15, 0.45, 16), tube([(3.4, -2.6), (3.35, 0.2)], 0.08), ellipse(3.35, 0.6, 0.15, 0.4, 16),
             lens((3.2, -2.6), (2.5, -0.6), 0.15)]
    water = [wave(-3.4, 3.6, -2.6, 0.08, 6, 100)]
    out = scene(([crown], [crown]), ([beak], [beak]), ([head], [head]), ([neck], [neck]), ([wing], [chain(wing, [wing[0]])]), ([body], [chain(body, [body[0]])]),
                (reeds, [reeds[0], reeds[1], reeds[2], reeds[3]]), (ripples + water, []))
    return make("Swan Princess with Crown", out, [eye(-1.7, 2.95, 0.08)])


@design("mermaids_princess_pea", T)
def princess_pea(rng):
    mats = []
    y = -2.8
    for k in range(7):
        dx = 0.15 * math.sin(k * 1.7)
        h = 0.5
        m = rrect(-2.4 + dx, y, 2.4 + dx, y + h, 0.2)
        stripes = keep_in([[(x, y), (x, y + h)] for x in (-1.6 + dx, -0.6 + dx, 0.4 + dx, 1.4 + dx)], m)
        mats.append(([m] + stripes[:0], [m]))
        y += h
    pea = circle(0.6, -3.0, 0.2, 14)
    posts = [rect(-2.9, -3.3, -2.6, y + 1.6), rect(2.6, -3.3, 2.9, y + 1.6), circle(-2.75, y + 1.8, 0.22, 14), circle(2.75, y + 1.8, 0.22, 14)]
    front, back, hints = girl_head(-1.4, y + 0.55, 0.65, "long", "open", "tiara")
    pillow = rrect(-2.3, y, -0.6, y + 0.45, 0.2)
    blanket = chain([(-0.9, y + 0.2)], quad((-0.9, y + 0.2), (0.6, y + 1.1), (2.3, y + 0.5), 14), [(2.3, y)], [(-0.9, y)])
    blanket_m = chain(blanket, [blanket[0]])
    ladder = [[(3.2, -3.3), (3.5, y)], [(3.7, -3.3), (4.0, y)]] + [[(3.2 + 0.3 * t, -3.3 + (y + 3.3) * t), (3.7 + 0.3 * t, -3.3 + (y + 3.3) * t)] for t in (0.15, 0.35, 0.55, 0.75, 0.95)]
    items = front + [([blanket], [blanket_m])] + back + [([pillow], [pillow])] + mats[::-1] + [([pea], [pea]), (posts, posts[:2]), (ladder + [[(-3.2, -3.3), (3.4, -3.3)]], [])]
    return make("The Princess and the Pea", scene(*items), hints)


# dropped: the Unicorns book has this subject
def fairy_jar(rng):
    jar = chain([(-1.6, 2.0)], quad((-1.6, 2.0), (-2.2, 1.6), (-2.2, 0.8), 8), [(-2.2, -2.6)], quad((-2.2, -2.6), (-2.2, -3.2), (-1.6, -3.2), 6), [(1.6, -3.2)],
                quad((1.6, -3.2), (2.2, -3.2), (2.2, -2.6), 6), [(2.2, 0.8)], quad((2.2, 0.8), (2.2, 1.6), (1.6, 2.0), 8))
    lid = rrect(-1.8, 2.0, 1.8, 2.6, 0.12)
    cloth = chain([(-1.9, 2.3)], quad((-1.9, 2.3), (-2.3, 2.9), (-1.6, 3.2), 8), quad((-1.6, 3.2), (0, 3.6), (1.6, 3.2), 12), quad((1.6, 3.2), (2.3, 2.9), (1.9, 2.3), 8),
                  scallop([(1.9, 2.3), (-1.9, 2.3)], 0.15, 7))
    string = [[(-1.9, 2.45), (1.9, 2.45)], lens((0.6, 2.45), (1.2, 1.8), 0.3), lens((0.6, 2.45), (0.2, 1.8), 0.3)]
    m, mm, mh = fairy(0, -1.3, 0.62, arms=("low", "wave"), legs="fly", hair="bun")
    shine = [quad((-1.8, 0.8), (-1.85, -0.8), (-1.75, -2.2), 10)]
    sp = [sparkle(x, y, r) for x, y, r in [(1.4, 0.8, 0.22), (-1.2, -2.4, 0.2), (1.3, -2.5, 0.18), (-1.3, 1.2, 0.18)]]
    glow = [[(2.6 * math.cos(a), -0.6 + 2.6 * math.sin(a)), (3.3 * math.cos(a), -0.6 + 3.3 * math.sin(a))] for a in (0.2, -0.3, math.pi - 0.2, math.pi + 0.3)]
    out = scene((string, string[1:]), ([cloth], [chain(cloth, [cloth[0]])]), ([lid], [lid]), (m, mm), ([jar] + shine + sp, []), (glow, []))
    return make("Fairy in a Glass Jar", out, mh)


@design("mermaids_tiara_pillow", T)
def tiara_pillow(rng):
    band = chain(quad((-2.4, 0.0), (0, -0.6), (2.4, 0.0), 30), quad((2.4, 0.0), (2.3, 0.3), (2.2, 0.35), 4), quad((2.2, 0.35), (0, -0.25), (-2.2, 0.35), 30),
                 quad((-2.2, 0.35), (-2.3, 0.3), (-2.4, 0.0), 4))
    arches = chain([(-2.2, 0.35)], quad((-2.2, 0.35), (-1.9, 1.4), (-1.2, 1.1), 10), quad((-1.2, 1.1), (-0.8, 2.6), (0, 2.6), 12),
                   quad((0, 2.6), (0.8, 2.6), (1.2, 1.1), 12), quad((1.2, 1.1), (1.9, 1.4), (2.2, 0.35), 10))
    inner = [chain(quad((-1.7, 0.2), (-1.5, 0.9), (-1.2, 0.85), 8)), chain(quad((-1.0, 0.0), (-0.6, 1.9), (0, 1.9), 10), quad((0, 1.9), (0.6, 1.9), (1.0, 0.0), 10)),
             chain(quad((1.7, 0.2), (1.5, 0.9), (1.2, 0.85), 8))]
    gem = poly((0, 1.5), (-0.35, 1.0), (0, 0.4), (0.35, 1.0))
    gems = [circle(-1.2, 1.3, 0.16, 12), circle(1.2, 1.3, 0.16, 12), circle(0, 2.85, 0.22, 14)]
    pearls = [circle(x, -0.25 + 0.05 * x * x, 0.1, 8) for x in (-1.6, -0.8, 0.8, 1.6)]
    pillow = chain([(-3.2, -0.6)], quad((-3.2, -0.6), (0, 0.1), (3.2, -0.6), 20), quad((3.2, -0.6), (3.6, -1.5), (3.2, -2.4), 10),
                   quad((3.2, -2.4), (0, -3.1), (-3.2, -2.4), 20), quad((-3.2, -2.4), (-3.6, -1.5), (-3.2, -0.6), 10))
    tassels = [poly((x, y), (x - 0.18, y - 0.6), (x + 0.18, y - 0.6)) for x, y in [(-3.2, -0.6), (3.2, -0.6), (-3.2, -2.4), (3.2, -2.4)]]
    button = circle(0, -1.6, 0.12, 10)
    out = scene(([gem] + gems + pearls, [gem] + gems), ([band], [band]), ([arches] + inner, [chain(arches, [(0, 0.0), arches[0]])]), (tassels, tassels),
                ([pillow, button], [pillow]))
    return make("Princess Tiara on a Velvet Pillow", out)


# dropped: the Unicorns book has this subject
def fairy_door_tree(rng):
    trunk = chain([(-3.4, -3.0)], quad((-3.4, -3.0), (-2.2, -2.6), (-2.0, -1.6), 10), [(-2.1, 3.8)], [(2.1, 3.8)], [(2.0, -1.6)], quad((2.0, -1.6), (2.2, -2.6), (3.4, -3.0), 10))
    roots = [quad((-1.2, -3.0), (-1.0, -2.6), (-0.9, -2.3), 6), quad((1.2, -3.0), (1.0, -2.6), (0.9, -2.3), 6)]
    bark = [quad((-1.6, 3.6), (-1.3, 2.0), (-1.6, 0.6), 10), quad((1.5, 3.4), (1.8, 2.2), (1.4, 1.0), 10), quad((-1.5, -0.6), (-1.7, -1.4), (-1.4, -2.0), 8)]
    door = chain([(-0.7, -2.6), (-0.7, -0.6)], arc(0, -0.6, 0.7, math.pi, 0, 20), [(0.7, -2.6), (-0.7, -2.6)])
    frame = chain([(-0.95, -2.6), (-0.95, -0.6)], arc(0, -0.6, 0.95, math.pi, 0, 20), [(0.95, -2.6)])
    planks = keep_in([[(x, -2.6), (x, 0.2)] for x in (-0.25, 0.25)], door)
    knob = circle(0.45, -1.6, 0.1, 10)
    hinges = [rect(-0.7, -0.9, -0.35, -0.75), rect(-0.7, -2.2, -0.35, -2.05)]
    win = circle(0, 1.3, 0.45, 30)
    win_x = [[(-0.45, 1.3), (0.45, 1.3)], [(0, 0.85), (0, 1.75)]]
    steps = [ellipse(0, -2.85, 0.9, 0.18, 24), ellipse(0.2, -3.25, 0.75, 0.15, 20)]
    shrooms = mushroom(-1.6, -3.0, 0.45, 0.45, 0.45) + mushroom(1.7, -3.0, 0.38, 0.35, 0.4)
    lantern_ = [[(1.1, 0.6), (1.1, 0.2)], rect(0.9, -0.5, 1.3, 0.2), lens((1.1, -0.35), (1.1, 0.05), 0.3)]
    branch = [chain([(-2.1, 3.0)], quad((-2.1, 3.0), (-2.8, 3.3), (-3.3, 4.0), 8)), chain([(-2.1, 2.5)], quad((-2.1, 2.5), (-2.9, 2.8), (-3.4, 3.4), 8))]
    out = scene(([knob], []), (hinges, hinges), ([door] + planks, [door]), ([frame], []), (win_x + [win], [win]), (lantern_, [lantern_[1]]), *shrooms,
                (steps, steps), ([trunk] + roots + bark + branch, []))
    return make("Fairy Door in a Tree Trunk", out)


@design("mermaids_troll_bridge", T)
def troll_bridge(rng):
    deck = chain([(-3.6, 0.2)], quad((-3.6, 0.2), (0, 1.0), (3.6, 0.2), 30))
    deck2 = chain([(-3.6, -0.2)], quad((-3.6, -0.2), (0, 0.6), (3.6, -0.2), 30))
    arch = chain([(-2.4, -2.6)], cubic((-2.4, -2.6), (-2.4, 0.0), (2.4, 0.0), (2.4, -2.6), 30))
    stones = keep_in([[(x, -3.0), (x, 1.0)] for x in (-3.0, 3.0)] + [[(-3.6, y), (3.6, y)] for y in (-1.0, -1.8)], poly((-3.6, -2.6), (-3.6, -0.2), (3.6, -0.2), (3.6, -2.6)))
    stones = hide(stones, [chain(arch, [(2.4, -3.0), (-2.4, -3.0), arch[0]])])
    face = ellipse(0, -1.4, 1.0, 0.85, 50)
    nose = chain([(-0.2, -1.1)], quad((-0.2, -1.1), (-0.6, -1.9), (0.0, -1.95), 8), quad((0.0, -1.95), (0.6, -1.9), (0.2, -1.1), 8))
    ears = [lens((-0.95, -1.2), (-1.6, -0.8), 0.35), lens((0.95, -1.2), (1.6, -0.8), 0.35)]
    hair = [poly((-0.5, -0.65), (-0.6, -0.15), (-0.2, -0.6), (0.0, -0.1), (0.2, -0.6), (0.6, -0.15), (0.5, -0.65), closed=False)]
    hands = [chain(arc(-1.6, -2.3, 0.4, 0, math.pi, 12)), chain(arc(1.6, -2.3, 0.4, 0, math.pi, 12))]
    fingers = [[(x, -2.3), (x, -2.0)] for x in (-1.75, -1.45, 1.45, 1.75)]
    water = [wave(-3.6, 3.6, -2.6, 0.08, 6, 100), wave(-3.6, 3.6, -3.1, 0.08, 6, 100)]
    gx, gy = 0.6, 1.0
    goat = chain([(gx - 0.9, gy + 0.35)], [(gx - 0.9, gy + 1.0)], quad((gx - 0.9, gy + 1.0), (gx, gy + 1.15), (gx + 0.9, gy + 1.0), 8), [(gx + 0.9, gy + 0.35)],
                 [(gx - 0.9, gy + 0.35)])
    glegs = [[(gx + dx, gy + 0.35), (gx + dx, gy + 0.0)] for dx in (-0.75, -0.45, 0.45, 0.75)]
    ghead = chain([(gx + 0.8, gy + 1.0)], [(gx + 1.2, gy + 1.6)], [(gx + 1.75, gy + 1.25)], [(gx + 1.65, gy + 1.05)], [(gx + 1.0, gy + 0.85)])
    horns = [quad((gx + 1.15, gy + 1.6), (gx + 0.9, gy + 2.2), (gx + 0.55, gy + 1.9), 8), quad((gx + 1.3, gy + 1.6), (gx + 1.2, gy + 2.2), (gx + 0.85, gy + 2.2), 8)]
    beard = poly((gx + 1.55, gy + 1.1), (gx + 1.55, gy + 0.65), (gx + 1.35, gy + 1.0), closed=False)
    gtail = [[(gx - 0.9, gy + 0.95), (gx - 1.2, gy + 1.15)]]
    items = [([ghead] + horns + [beard], [chain(ghead, [ghead[0]])]), ([goat] + glegs + gtail, [goat]), ([deck, deck2], []),
             (hands + fingers, [chain(h, [h[0]]) for h in hands]), ([nose], [nose]), (hair, []), ([face], [face]), (ears, ears), ([arch] + stones, []), (water, [])]
    return make("Billy Goat and the Troll Bridge", scene(*items), [eye(-0.35, -1.15, 0.12), eye(0.35, -1.15, 0.12)])
