"""Fishing niche: game fish, tackle, anglers and lakeside scenes."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "fishing"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ---------------------------------------------------------------- generic helpers

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


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def limb(pts, w0, w1=None, cap=False, n=8):
    w1 = w0 if w1 is None else w1
    return tube(smooth(pts, n), lambda t: w0 + (w1 - w0) * t, cap)


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
        w = tw * (0.9 - 0.08 * math.sin(math.pi * min(1.0, t / 0.6)) if t < 0.45 else 0.84 + 0.16 * min(1.0, (t - 0.45) / 0.35)) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    dx, dy = c[-1][0] - c[-2][0], c[-1][1] - c[-2][1]
    L = math.hypot(dx, dy) or 1.0
    ox, oy = dx / L * tw * 0.35, dy / L * tw * 0.35
    shoulders = cubic(left[-1], (left[-1][0] + ox, left[-1][1] + oy), (right[-1][0] + ox, right[-1][1] + oy), right[-1], 14)
    return left + shoulders[1:] + right[::-1][1:] + [left[0]]


def boot(ankle, toe):
    heel = lerp(ankle, toe, -0.3)
    return lens(heel, toe, 0.32, 16)


def person(head, torso, arms=(), legs=(), hr=0.4, tw=1.0, aw=0.34, lw=0.5, hands=True, feet=True):
    """Figure from smooth tubes. arms: [shoulder, elbow, hand]; legs: [hip, knee, ankle, toe]."""
    out = [circle(head[0], head[1], hr, 40), body_shape(torso, tw)]
    for a in arms:
        out.append(limb(a[:3], aw, aw * 0.8))
        if hands:
            out.append(circle(a[2][0], a[2][1], aw * 0.62, 14))
    for lg in legs:
        out.append(limb(lg[:3], lw, lw * 0.7))
        if feet and len(lg) > 3:
            out.append(boot(lg[2], lg[3]))
    return out


def bucket_hat(cx, cy, r, tilt=0.0):
    """Angler's bucket hat sitting on a head of radius r centred (cx, cy)."""
    crown = chain([(-0.85 * r, 0.25 * r)], quad((-0.85 * r, 0.25 * r), (-0.75 * r, 1.25 * r), (0.0, 1.25 * r), 8),
                  quad((0.0, 1.25 * r), (0.75 * r, 1.25 * r), (0.85 * r, 0.25 * r), 8))
    brim = chain([(-0.85 * r, 0.25 * r)], quad((-1.3 * r, 0.2 * r), (-1.45 * r, -0.05 * r), (-1.4 * r, -0.05 * r), 4),
                 [(1.4 * r, -0.05 * r)], quad((1.45 * r, -0.05 * r), (1.3 * r, 0.2 * r), (0.85 * r, 0.25 * r), 4))
    band = [(-0.82 * r, 0.45 * r), (0.82 * r, 0.45 * r)]
    return [transform(p, cx, cy, 1, tilt) for p in (crown, brim, band)]


def densify(pts, step=0.05):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(1, int(L / step))
        out += [lerp(a, b, i / k) for i in range(1, k + 1)]
    return out


def clip_out(pts, holes):
    segs, cur = [], []
    for p in densify(pts):
        if any(math.hypot(p[0] - cx, p[1] - cy) < r for cx, cy, r in holes):
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


def clip_box(strokes, x0, y0, x1, y1):
    """Drop the parts of strokes inside a rectangle."""
    out = []
    for s in strokes:
        cur = []
        for p in densify(s):
            if x0 < p[0] < x1 and y0 < p[1] < y1:
                if len(cur) > 1:
                    out.append(cur)
                cur = []
            else:
                cur.append(p)
        if len(cur) > 1:
            out.append(cur)
    return out


def yat(curve, x):
    """y of a left-to-right or right-to-left curve at x (linear interpolation)."""
    best = None
    for a, b in zip(curve, curve[1:]):
        if (a[0] - x) * (b[0] - x) <= 0 and a[0] != b[0]:
            t = (x - a[0]) / (b[0] - a[0])
            return a[1] + (b[1] - a[1]) * t
        d = min(abs(a[0] - x), abs(b[0] - x))
        if best is None or d < best[0]:
            best = (d, a[1])
    return best[1]


# ---------------------------------------------------------------- fish builder

class Fish:
    """A side-view fish facing right.

    `top` / `bot` are profile points from the nose back to the tail root."""

    def __init__(self, top, bot, n=8):
        self.upper = smooth(top, n)
        self.lower = smooth(bot, n)
        self.parts = [self.upper[::-1] + self.lower[1:]]
        self.hints = []
        self.nose = top[0]
        self.tail_top, self.tail_bot = top[-1], bot[-1]

    def top(self, x):
        return yat(self.upper, x)

    def bot(self, x):
        return yat(self.lower, x)

    def mid(self, x):
        return (self.top(x) + self.bot(x)) / 2

    def tail(self, kind="fork", w=1.0, h=0.9, rays=2):
        (xt, yt), (_, yb) = self.tail_top, self.tail_bot
        c = (yt + yb) / 2
        if kind == "fork":
            pts = chain(quad((xt, yb), (xt - 0.3 * w, c - 0.75 * h), (xt - w, c - h), 8), quad((xt - w, c - h), (xt - 0.7 * w, c - 0.35 * h), (xt - 0.42 * w, c), 8),
                        quad((xt - 0.42 * w, c), (xt - 0.7 * w, c + 0.35 * h), (xt - w, c + h), 8), quad((xt - w, c + h), (xt - 0.3 * w, c + 0.75 * h), (xt, yt), 8))
        elif kind == "crescent":
            pts = chain(quad((xt, yb), (xt - 0.15 * w, c - 0.85 * h), (xt - w, c - h), 8), quad((xt - w, c - h), (xt - 0.6 * w, c - 0.35 * h), (xt - 0.4 * w, c), 10),
                        quad((xt - 0.4 * w, c), (xt - 0.6 * w, c + 0.35 * h), (xt - w, c + h), 10), quad((xt - w, c + h), (xt - 0.15 * w, c + 0.85 * h), (xt, yt), 8))
        elif kind == "square":
            pts = chain(quad((xt, yb), (xt - 0.5 * w, c - 0.6 * h), (xt - w, c - h), 8), quad((xt - w, c - h), (xt - 0.85 * w, c), (xt - w, c + h), 12),
                        quad((xt - w, c + h), (xt - 0.5 * w, c + 0.6 * h), (xt, yt), 8))
        elif kind == "shark":
            pts = chain(quad((xt, yb), (xt - 0.4 * w, c - 0.5 * h), (xt - 0.75 * w, c - 0.55 * h), 8), quad((xt - 0.75 * w, c - 0.55 * h), (xt - 0.8 * w, c), (xt - w, c + 1.2 * h), 10),
                        quad((xt - w, c + 1.2 * h), (xt - 0.5 * w, c + 0.5 * h), (xt, yt), 10))
        else:  # round
            pts = smooth([(xt, yb), (xt - 0.45 * w, c - 0.85 * h), (xt - w, c - 0.5 * h), (xt - 1.08 * w, c), (xt - w, c + 0.5 * h), (xt - 0.45 * w, c + 0.85 * h), (xt, yt)], 6)
        self.parts.append(pts)
        for k in range(rays):
            f = (k + 1) / (rays + 1)
            yy = c + (f - 0.5) * 1.1 * h
            self.parts.append([(xt - 0.1 * w, c + (yy - c) * 0.2), (xt - 0.75 * w, yy)])
        return self

    def fin(self, x0, x1, h, side="top", kind="soft", lean=0.3, rays=0, teeth=5):
        """Fin from x0 (front) back to x1. h>0; side 'top' or 'bot'."""
        f = self.top if side == "top" else self.bot
        s = 1 if side == "top" else -1
        p0, p1 = (x0, f(x0) - s * 0.02), (x1, f(x1) - s * 0.02)
        if kind == "tri":
            pts = [p0, (x0 - lean, p0[1] + s * h), p1]
        elif kind == "spiny":
            pts, spines = [p0], []
            dxs = (x1 - x0) / teeth
            for k in range(teeth):
                t = (k + 0.5) / teeth
                x = x0 + dxs * (k + 0.5)
                env = h * (1.0 - 0.4 * t)
                tip = (x - 0.12, f(x) + s * env)
                pts.append(tip)
                spines.append([(x, f(x)), lerp((x, f(x)), tip, 0.92)])
                if k < teeth - 1:
                    xd = x + dxs * 0.5
                    pts.append((xd - 0.04, f(xd) + s * env * 0.5))
            pts.append(p1)
            self.parts += spines
        elif kind == "long":
            pts = smooth([p0, (x0 - lean, p0[1] + s * h), (x0 + (x1 - x0) * 0.5, f(x0 + (x1 - x0) * 0.5) + s * h * 0.75),
                          (x1 - 0.1, f(x1) + s * h * 0.5), p1], 8)
        else:  # soft rounded
            pts = smooth([p0, (x0 - lean, p0[1] + s * h), (x1 - lean * 0.6, f(x1) + s * h * 0.55), p1], 8)
        self.parts.append(pts)
        for k in range(rays):
            t = (k + 1) / (rays + 1)
            bx = x0 + (x1 - x0) * t
            base = (bx, f(bx))
            tip = pts[int(len(pts) * (0.2 + 0.6 * t))]
            self.parts.append([base, lerp(base, tip, 0.85)])
        return self

    def pectoral(self, x, y, L=0.9, ang=-2.7, bulge=0.3):
        tip = (x + L * math.cos(ang), y + L * math.sin(ang))
        self.parts.append(lens((x, y), tip, bulge, 10))
        return self

    def gill(self, x, bulge=0.25, frac=0.85):
        yt, yb = self.top(x), self.bot(x)
        m = (yt + yb) / 2
        self.parts.append(quad((x, m + (yt - m) * frac), (x - bulge, m), (x, m + (yb - m) * frac), 12))
        return self

    def eye(self, x, y, r=0.18, pupil=0.09):
        self.parts.append(circle(x, y, r, 18))
        self.hints.append(circle(x, y, pupil, 10))
        return self

    def mouth(self, L=0.4, dy=-0.05, open_=0.0):
        nx, ny = self.nose
        self.parts.append([(nx - 0.02, ny + dy), (nx - L, ny + dy - 0.06)])
        return self

    def add(self, *strokes):
        self.parts += list(strokes)
        return self

    def done(self, dx=0.0, dy=0.0, s=1.0, rot=0.0, flip=False):
        parts = [mirror_x(p) for p in self.parts] if flip else self.parts
        hints = [mirror_x(p) for p in self.hints] if flip else self.hints
        return [transform(p, dx, dy, s, rot) for p in parts], [transform(p, dx, dy, s, rot) for p in hints]


def spots(fish, pts, r=0.12):
    return [circle(x, y, r, 10) for x, y in pts]


def splash(cx, cy, w=1.6, h=0.8):
    """Water splash: droplets and a crown of spray."""
    out = [wave(cx - w, cx + w, cy, 0.08, 2, 30)]
    for k in range(5):
        a = math.pi * (0.15 + 0.175 * k)
        out.append(lens((cx + 0.35 * w * math.cos(a), cy + 0.1), (cx + 0.85 * w * math.cos(a), cy + h * math.sin(a) + 0.1), 0.18, 8))
    out += [circle(cx - 1.1 * w, cy + 0.7 * h, 0.12, 10), circle(cx + 1.1 * w, cy + 0.8 * h, 0.12, 10), circle(cx + 0.2 * w, cy + 1.35 * h, 0.1, 10)]
    return out


def ripples(cx, cy, rs=(0.5, 1.0, 1.5), k=0.28):
    return [ellipse(cx, cy, r, r * k, 50) for r in rs]


def reeds(x, y, h, n=3):
    out = []
    for k in range(n):
        xx = x + 0.25 * k
        hh = h * (1 - 0.15 * k)
        out.append(quad((xx, y), (xx + 0.05, y + hh * 0.6), (xx + 0.15 * (k - 1), y + hh), 8))
    out.append(rrect(x + 0.2, y + h * 0.55, x + 0.4, y + h * 0.9, 0.1))
    return out


def pine(x, y, h, w):
    tiers = []
    for k in range(3):
        b = y + 0.15 * h + k * 0.27 * h
        ww = w * (1 - 0.25 * k)
        tiers.append(poly((x - ww, b), (x, b + 0.45 * h), (x + ww, b), closed=False))
    return tiers + [[(x - 0.08 * w, y), (x - 0.08 * w, y + 0.15 * h)], [(x + 0.08 * w, y), (x + 0.08 * w, y + 0.15 * h)]]


# ---------------------------------------------------------------- tackle helpers

def spin_reel(cx, cy, s=1.0):
    """Spinning reel hanging under a rod, seen from the side."""
    parts = [rrect(-0.55, -0.45, 0.55, 0.45, 0.2), rrect(0.55, -0.35, 0.85, 0.35, 0.1), rect(0.85, -0.25, 1.2, 0.25),
             [(0.0, 0.45), (0.0, 1.1)], [(-0.35, 1.1), (0.35, 1.1)], [(-0.55, 0.0), (-0.9, 0.0)], [(-0.9, 0.0), (-0.9, -0.6)],
             rrect(-1.05, -0.95, -0.75, -0.6, 0.1)]
    return [transform(p, cx, cy, s) for p in parts]


def treble(x, y, s=1.0):
    """Treble hook hanging from (x, y)."""
    out = [circle(x, y - 0.08 * s, 0.08 * s, 8), [(x, y - 0.16 * s), (x, y - 0.6 * s)]]
    for sg in (-1, 1):
        out.append(chain([(x, y - 0.6 * s)], arc(x + sg * 0.18 * s, y - 0.6 * s, 0.18 * s, math.pi if sg > 0 else 0, 2 * math.pi if sg > 0 else -math.pi, 8),
                         [(x + sg * 0.36 * s, y - 0.35 * s)]))
    return out


def hook(x, y, s=1.0, rot=0.0):
    """Single J hook with eye at (x, y)."""
    pts = chain([(0, 0.9)], [(0, -0.3)], arc(0.3, -0.3, 0.3, math.pi, 2 * math.pi, 14), [(0.6, 0.0)], [(0.48, -0.08)])
    return [transform(p, x, y, s, rot) for p in [circle(0, 1.0, 0.1, 10), pts]]


def band_line(f, x0, x1, amp=0.12, n=9, off=0.0):
    pts = []
    for k in range(n + 1):
        x = x0 + (x1 - x0) * k / n
        pts.append((x, f.mid(x) + off + (amp if k % 2 else -amp)))
    return smooth(pts, 6)


# ---------------------------------------------------------------- freshwater game fish

@design("fishing_bass_jumping", T)
def bass_jumping(rng):
    f = Fish([(2.25, 0.2), (1.9, 0.65), (1.2, 1.05), (0.2, 1.2), (-0.9, 1.0), (-1.8, 0.5), (-2.3, 0.32)],
             [(2.4, -0.3), (1.9, -0.7), (1.0, -1.0), (0.0, -1.05), (-1.0, -0.85), (-1.8, -0.45), (-2.3, -0.32)])
    f.add([(2.25, 0.2), (1.45, -0.08), (2.4, -0.3)])
    f.tail("square", 1.0, 0.95, 3).fin(0.95, -0.1, 0.75, "top", "spiny", 0.1, teeth=5).fin(-0.25, -1.35, 0.7, "top", "soft", 0.2, rays=3)
    f.fin(-0.75, -1.5, 0.55, "bot", "soft", 0.2).fin(0.9, 0.35, 0.55, "bot", "tri", 0.4)
    f.pectoral(1.0, -0.25, 0.95, -2.75).gill(1.25).eye(1.75, 0.45, 0.2, 0.1)
    f.add(band_line(f, 1.0, -2.2, 0.13, 10))
    parts, hints = f.done(0.3, 0.9, 1.0, 0.45)
    lure = [[(1.95, 2.45), (3.4, 3.6)], transform(lens((-0.35, 0), (0.35, 0), 0.4, 10), 2.05, 2.25, 1, 0.5)]
    water = splash(-1.6, -1.6, 1.5, 0.9) + [wave(-3.4, 3.4, -2.4, 0.1, 4, 80)]
    return make("Largemouth Bass Jumping", parts + lure + water, hints)


@design("fishing_rainbow_trout", T)
def rainbow_trout(rng):
    f = Fish([(2.6, 0.05), (2.3, 0.45), (1.5, 0.8), (0.3, 0.95), (-1.0, 0.8), (-2.0, 0.45), (-2.6, 0.3)],
             [(2.6, -0.12), (2.2, -0.5), (1.2, -0.8), (0.0, -0.85), (-1.2, -0.65), (-2.0, -0.4), (-2.6, -0.3)])
    f.tail("square", 1.1, 1.0, 3).fin(0.65, -0.35, 0.75, "top", "soft", 0.25, rays=3).fin(-1.6, -1.95, 0.32, "top", "soft", 0.1)
    f.fin(-0.2, -0.75, 0.5, "bot", "soft", 0.2).fin(-1.1, -1.65, 0.5, "bot", "soft", 0.2)
    f.pectoral(1.4, -0.35, 0.85, -2.7).gill(1.6).eye(2.05, 0.2, 0.17, 0.09).mouth(0.55, -0.03)
    f.add(smooth([(1.45, 0.05), (0.0, 0.1), (-1.5, 0.05), (-2.55, 0.02)], 8), smooth([(1.45, -0.3), (0.0, -0.3), (-1.5, -0.25), (-2.55, -0.18)], 8))
    pts = []
    for x in [1.1 - 0.42 * k for k in range(9)]:
        for yy in (0.62, 0.35):
            y = f.top(x) - (0.95 - yy) * 0.9 if False else min(f.top(x) - 0.22, yy + 0.05 * math.sin(7 * x))
            if y > 0.3:
                pts.append((x + 0.12 * math.sin(11 * x + yy * 5), y))
    f.add(*spots(f, pts, 0.1))
    f.add(*spots(f, [(-2.95, 0.5), (-3.2, 0.15), (-2.95, -0.25), (-3.25, -0.55), (0.25, 1.25), (-0.05, 1.05)], 0.09))
    parts, hints = f.done(0.2, 0.3, 1.0)
    stones = [smooth([(-3.4, -2.2), (-2.6, -1.4), (-1.6, -1.6), (-1.0, -2.2)], 8), smooth([(-1.0, -2.2), (-0.4, -1.7), (0.6, -1.8), (1.0, -2.2)], 8),
              smooth([(1.0, -2.2), (1.7, -1.3), (2.8, -1.5), (3.4, -2.2)], 8), [(-3.4, -2.2), (3.4, -2.2)]]
    bubbles = [circle(2.9, 0.8, 0.13, 10), circle(3.1, 1.3, 0.1, 10), circle(2.95, 1.75, 0.12, 10)]
    return make("Rainbow Trout", parts + stones + bubbles, hints)


@design("fishing_salmon_falls", T)
def salmon_falls(rng):
    f = Fish([(2.3, 0.05), (1.95, 0.5), (1.1, 0.85), (0.0, 0.95), (-1.1, 0.75), (-1.9, 0.4), (-2.3, 0.28)],
             [(2.45, -0.05), (2.15, -0.45), (1.1, -0.8), (-0.1, -0.85), (-1.2, -0.6), (-1.9, -0.35), (-2.3, -0.28)])
    f.add(quad((2.45, -0.05), (2.55, 0.15), (2.38, 0.22), 6))
    f.tail("fork", 1.1, 1.0, 2).fin(0.6, -0.3, 0.75, "top", "soft", 0.25, rays=2).fin(-1.4, -1.75, 0.3, "top", "soft", 0.1)
    f.fin(-0.3, -0.8, 0.45, "bot", "soft", 0.2).fin(-1.1, -1.6, 0.45, "bot", "soft", 0.2)
    f.pectoral(1.2, -0.35, 0.85, -2.7).gill(1.45).eye(1.85, 0.25, 0.17, 0.09).mouth(0.6, -0.08)
    f.add(*spots(f, [(0.9, 0.55), (0.4, 0.7), (-0.1, 0.55), (-0.6, 0.65), (-1.1, 0.45), (-1.5, 0.3), (0.2, 0.3), (-0.8, 0.25)], 0.1))
    parts, hints = f.done(-1.3, 0.55, 0.8, 0.85)
    ledge = [[(0.2, 0.9), (3.4, 0.9)], smooth([(0.2, 0.9), (0.35, 0.3), (0.25, -0.5), (0.45, -1.3), (0.4, -1.7)], 6)]
    river = [wave(0.4, 3.4, 1.35, 0.08, 3, 40), wave(1.2, 3.2, 1.9, 0.08, 2, 30)]
    falls = [quad((0.2 + 0.35 * k, 0.9), (0.35 + 0.45 * k, 0.6), (0.6 + 0.55 * k, -1.65), 12) for k in range(4)]
    pool = [wave(-3.4, 3.4, -1.75, 0.09, 6, 90)]
    foam = [circle(1.1, -1.35, 0.17, 10), circle(1.6, -1.45, 0.14, 10), circle(0.7, -1.25, 0.12, 10), circle(2.1, -1.35, 0.14, 10)]
    rocks = [smooth([(-3.4, -2.8), (-3.1, -2.1), (-2.2, -2.0), (-1.7, -2.8)], 8), smooth([(1.4, -2.8), (1.9, -2.2), (2.8, -2.15), (3.3, -2.8)], 8),
             [(-3.4, -2.8), (3.4, -2.8)]]
    jump = splash(-2.4, -1.75, 0.8, 0.6)
    return make("Salmon Leaping Up the Falls", parts + ledge + river + falls + pool + foam + rocks + jump, hints)


@design("fishing_catfish", T)
def catfish(rng):
    f = Fish([(2.4, 0.1), (2.1, 0.45), (1.2, 0.75), (0.0, 0.78), (-1.2, 0.55), (-2.1, 0.3), (-2.5, 0.25)],
             [(2.4, -0.25), (2.0, -0.6), (1.0, -0.85), (-0.2, -0.75), (-1.4, -0.5), (-2.1, -0.3), (-2.5, -0.25)])
    f.add([(2.4, 0.1), (2.48, -0.08), (2.4, -0.25)])
    f.tail("fork", 1.1, 0.95, 2).fin(0.85, 0.25, 0.95, "top", "tri", 0.35).fin(-1.55, -2.0, 0.3, "top", "soft", 0.1)
    f.fin(-0.4, -2.05, 0.4, "bot", "long", 0.15).fin(0.6, 0.15, 0.4, "bot", "tri", 0.3)
    f.pectoral(1.3, -0.3, 0.9, -2.6, 0.22).gill(1.5, 0.2).eye(1.95, 0.32, 0.13, 0.07)
    f.add([(2.45, -0.1), (1.95, -0.15)])
    f.add(cubic((2.3, 0.05), (3.0, 0.35), (3.2, 1.1), (2.7, 1.6), 20), cubic((2.2, 0.15), (2.6, 0.9), (2.3, 1.5), (1.8, 1.8), 20),
          cubic((2.25, -0.3), (2.6, -0.8), (2.9, -1.0), (3.3, -1.0), 14), cubic((2.1, -0.35), (2.3, -0.9), (2.5, -1.2), (2.8, -1.4), 14))
    parts, hints = f.done(-0.1, 0.4, 1.05)
    bottom = [smooth([(-3.4, -1.9), (-2.4, -1.6), (-1.0, -1.85), (0.6, -1.6), (2.0, -1.9), (3.4, -1.7)], 8),
              ellipse(-2.3, -2.25, 0.6, 0.25, 24), ellipse(1.2, -2.3, 0.75, 0.28, 24), ellipse(2.9, -2.35, 0.45, 0.2, 20)]
    return make("Whiskered Catfish", parts + bottom, hints)


@design("fishing_pike", T)
def pike(rng):
    f = Fish([(2.95, 0.0), (2.6, 0.15), (1.6, 0.45), (0.0, 0.55), (-1.5, 0.55), (-2.4, 0.35), (-2.9, 0.25)],
             [(3.0, -0.12), (2.5, -0.3), (1.4, -0.55), (0.0, -0.6), (-1.5, -0.5), (-2.4, -0.3), (-2.9, -0.25)])
    f.add([(2.95, 0.0), (3.0, -0.12)])
    f.tail("fork", 1.0, 0.85, 2).fin(-1.25, -2.4, 0.65, "top", "soft", 0.25, rays=2).fin(-1.4, -2.4, 0.55, "bot", "soft", 0.2)
    f.fin(0.05, -0.45, 0.4, "bot", "soft", 0.2).pectoral(1.5, -0.35, 0.75, -2.75, 0.25).gill(1.7, 0.2)
    f.eye(2.15, 0.2, 0.15, 0.08).add([(3.0, -0.06), (1.9, -0.14)])
    marks = []
    for row, yy in enumerate((0.3, 0.0, -0.3)):
        for k in range(6):
            x = 1.2 - 0.55 * k - 0.27 * (row % 2)
            if x > -2.4:
                marks.append(ellipse(x, yy, 0.17, 0.08, 14, rot=0.2))
    f.add(*marks)
    parts, hints = f.done(0.0, 0.0, 1.0)
    reeds_ = []
    for x, h in ((-3.3, 4.6), (-3.0, 1.6), (-2.6, 1.3), (-1.0, 1.4), (-0.6, 1.0), (1.2, 1.2), (2.7, 1.5), (3.1, 4.4), (3.4, 1.8)):
        reeds_.append(quad((x, -2.6), (x + 0.15, -2.6 + h * 0.5), (x + 0.05 * (1 if x > 0 else -1), -2.6 + h), 10))
    reeds_ = clip_box(reeds_, -3.95, -0.75, 3.05, 0.85)
    minnow = [lens((0.2, 2.0), (1.0, 2.05), 0.3, 10), poly((0.2, 2.0), (-0.05, 2.18), (-0.05, 1.82))]
    bottom = [[(-3.4, -2.6), (3.4, -2.6)]]
    return make("Northern Pike in the Weeds", parts + reeds_ + minnow + bottom, hints)


@design("fishing_walleye", T)
def walleye(rng):
    f = Fish([(2.5, 0.0), (2.1, 0.4), (1.2, 0.8), (0.0, 0.9), (-1.2, 0.7), (-2.1, 0.35), (-2.5, 0.28)],
             [(2.55, -0.15), (2.1, -0.5), (1.0, -0.8), (-0.2, -0.8), (-1.4, -0.55), (-2.1, -0.32), (-2.5, -0.28)])
    f.add([(2.5, 0.0), (2.55, -0.15)])
    f.tail("fork", 1.05, 0.95, 2).fin(0.95, -0.25, 0.8, "top", "spiny", 0.1, teeth=6).fin(-0.45, -1.45, 0.6, "top", "soft", 0.2, rays=2)
    f.fin(-0.7, -1.4, 0.5, "bot", "soft", 0.2).fin(0.6, 0.15, 0.45, "bot", "tri", 0.3)
    f.pectoral(1.1, -0.3, 0.8, -2.7).gill(1.4).mouth(0.55, -0.08)
    f.add(circle(1.85, 0.3, 0.3, 24), circle(1.85, 0.3, 0.19, 18))
    f.hints.append(circle(1.85, 0.3, 0.1, 10))
    for x in (0.9, 0.1, -0.7, -1.5):
        f.add(quad((x + 0.25, f.top(x + 0.25) - 0.05), (x, f.mid(x) + 0.05), (x - 0.25, f.top(x - 0.25) - 0.05), 8))
    f.add([(-3.35, -0.75), (-3.0, -0.55)])
    parts, hints = f.done(0.1, 0.3, 1.05)
    return make("Walleye with Glassy Eyes", parts + [[(2.8, 0.2), (3.3, 2.9)]], hints)


@design("fishing_carp", T)
def carp(rng):
    f = Fish([(2.2, 0.2), (1.9, 0.7), (1.1, 1.35), (0.0, 1.55), (-1.1, 1.3), (-1.9, 0.7), (-2.3, 0.45)],
             [(2.25, -0.05), (1.9, -0.5), (1.0, -1.0), (-0.2, -1.1), (-1.3, -0.85), (-2.0, -0.5), (-2.3, -0.42)])
    f.add([(2.2, 0.2), (2.35, 0.12), (2.25, -0.05)])
    f.tail("fork", 1.25, 1.15, 2).fin(0.5, -1.6, 0.85, "top", "long", 0.3, rays=3).fin(-1.0, -1.6, 0.55, "bot", "soft", 0.2)
    f.fin(0.3, -0.25, 0.5, "bot", "soft", 0.2).pectoral(1.0, -0.4, 0.85, -2.6).gill(1.2, 0.3).eye(1.7, 0.45, 0.16, 0.08)
    f.add(quad((2.3, 0.0), (2.5, -0.3), (2.35, -0.55), 6))
    scales = []
    for i, x in enumerate([0.85 - 0.42 * k for k in range(7)]):
        y0, y1 = f.bot(x) + 0.3, f.top(x) - 0.3
        y = y0 + (0.19 if i % 2 else 0.0)
        while y < y1:
            scales.append(arc(x, y, 0.24, math.radians(115), math.radians(245), 10))
            y += 0.38
    f.add(*scales)
    parts, hints = f.done(0.1, 0.0, 1.0)
    plants = [quad((-3.0, -2.6), (-3.4, -1.0), (-2.9, 0.5), 12), quad((-2.7, -2.6), (-2.3, -1.4), (-2.6, -0.4), 12),
              quad((2.9, -2.6), (3.3, -1.2), (2.9, -0.1), 12), [(-3.4, -2.6), (3.4, -2.6)]]
    bubbles = [circle(2.75, 0.9, 0.12, 10), circle(2.95, 1.35, 0.15, 10), circle(2.8, 1.85, 0.1, 10)]
    return make("Common Carp", parts + plants + bubbles, hints)


@design("fishing_bluegill", T)
def bluegill(rng):
    f = Fish([(1.7, 0.1), (1.5, 0.6), (0.9, 1.35), (0.0, 1.6), (-0.9, 1.35), (-1.5, 0.7), (-1.75, 0.35)],
             [(1.75, -0.05), (1.5, -0.6), (0.8, -1.35), (-0.1, -1.55), (-0.9, -1.25), (-1.5, -0.65), (-1.75, -0.35)])
    f.add([(1.7, 0.1), (1.82, 0.03), (1.75, -0.05)])
    f.tail("fork", 1.0, 1.05, 2).fin(0.55, -0.45, 0.5, "top", "spiny", 0.05, teeth=5).fin(-0.45, -1.4, 0.6, "top", "soft", 0.15, rays=2)
    f.fin(-0.25, -1.35, 0.55, "bot", "soft", 0.1, rays=2).fin(0.75, 0.3, 0.45, "bot", "tri", 0.3)
    f.pectoral(0.75, -0.2, 1.0, -2.5, 0.25).gill(0.95, 0.25).eye(1.25, 0.4, 0.17, 0.09)
    f.add(ellipse(0.72, 0.2, 0.24, 0.2, 18))
    for x in (0.3, -0.2, -0.7, -1.15):
        f.add(quad((x + 0.1, f.top(x + 0.1) - 0.1), (x - 0.12, f.mid(x)), (x + 0.1, f.bot(x + 0.1) + 0.12), 12))
    parts, hints = f.done(0.3, 0.3, 1.25)
    worm = [[(2.95, 3.3), (2.95, 1.05)]] + hook(2.95, 0.05, 1.0) + [tube(smooth([(2.95, 0.6), (3.35, 0.4), (2.9, 0.15), (3.4, -0.1), (3.2, -0.5)], 6), 0.14, cap=True)]
    plants = [[(-3.4, -2.4), (3.4, -2.4)], ellipse(-2.4, -2.25, 0.45, 0.15, 18), ellipse(1.9, -2.25, 0.5, 0.15, 18)]
    return make("Bluegill and the Worm", parts + worm + plants, hints)


@design("fishing_yellow_perch", T)
def yellow_perch(rng):
    f = Fish([(2.2, 0.0), (1.8, 0.45), (1.0, 0.9), (0.0, 1.0), (-1.1, 0.75), (-1.9, 0.35), (-2.3, 0.27)],
             [(2.25, -0.12), (1.8, -0.5), (0.9, -0.8), (-0.2, -0.85), (-1.3, -0.55), (-1.9, -0.32), (-2.3, -0.27)])
    f.add([(2.2, 0.0), (2.25, -0.12)])
    f.tail("fork", 1.0, 0.9, 2).fin(0.85, -0.35, 0.85, "top", "spiny", 0.05, teeth=6).fin(-0.5, -1.5, 0.6, "top", "soft", 0.2, rays=2)
    f.fin(-0.7, -1.4, 0.5, "bot", "soft", 0.2).fin(0.7, 0.25, 0.45, "bot", "tri", 0.3)
    f.pectoral(1.0, -0.25, 0.8, -2.7).gill(1.25).eye(1.65, 0.3, 0.18, 0.09).mouth(0.45, -0.07)
    for x in (0.85, 0.35, -0.15, -0.65, -1.15, -1.6):
        f.add(poly((x + 0.2, f.top(x + 0.2) - 0.03), (x - 0.02, f.bot(x) * 0.55), (x - 0.22, f.top(x - 0.22) - 0.03), closed=False))
    parts, hints = f.done(0.1, 0.2, 1.1)
    plants = [quad((-2.9, -2.4), (-3.3, -0.5), (-2.9, 1.0), 12), quad((2.8, -2.4), (3.3, -1.0), (2.9, 0.2), 12), [(-3.4, -2.4), (3.4, -2.4)]]
    pebbles = [ellipse(-1.5, -2.25, 0.4, 0.15, 18), ellipse(0.6, -2.25, 0.5, 0.15, 18), ellipse(1.8, -2.25, 0.3, 0.13, 16)]
    return make("Yellow Perch", parts + plants + pebbles, hints)


@design("fishing_striped_bass", T)
def striped_bass(rng):
    f = Fish([(2.6, 0.05), (2.2, 0.45), (1.3, 0.85), (0.0, 0.95), (-1.3, 0.75), (-2.2, 0.35), (-2.6, 0.27)],
             [(2.7, -0.15), (2.2, -0.55), (1.2, -0.85), (-0.1, -0.9), (-1.4, -0.6), (-2.2, -0.32), (-2.6, -0.27)])
    f.add([(2.6, 0.05), (2.7, -0.15)])
    f.tail("fork", 1.15, 1.0, 2).fin(1.05, 0.05, 0.85, "top", "spiny", 0.05, teeth=6).fin(-0.3, -1.4, 0.65, "top", "soft", 0.2, rays=2)
    f.fin(-0.6, -1.4, 0.5, "bot", "soft", 0.2).fin(0.8, 0.3, 0.45, "bot", "tri", 0.3)
    f.pectoral(1.3, -0.3, 0.8, -2.7).gill(1.55).eye(2.0, 0.25, 0.17, 0.09).mouth(0.55, -0.1)
    for k, yy in enumerate((0.62, 0.36, 0.1, -0.16, -0.42)):
        x0 = 1.45 if abs(yy) < 0.5 else 1.1
        f.add(smooth([(x0, yy + 0.02), (0.0, yy + 0.05 * (1 if yy > 0 else -0.3)), (-1.4, yy * 0.8), (-2.5, yy * 0.35)], 8))
    parts, hints = f.done(0.0, 0.5, 1.0)
    surf = [wave(-3.4, 3.4, -1.6, 0.12, 4, 80), wave(-3.4, 3.4, -2.3, 0.1, 5, 80), [(-3.4, -2.9), (3.4, -2.9)]]
    lure = [[(2.9, 0.45), (3.3, 2.9)], transform(lens((-0.3, 0), (0.45, 0), 0.4, 10), 3.05, 0.15, 1, -0.6)]
    return make("Striped Bass", parts + surf + lure, hints)


@design("fishing_crappie", T)
def crappie(rng):
    f = Fish([(2.0, 0.25), (1.75, 0.65), (1.0, 1.15), (0.0, 1.3), (-1.0, 1.05), (-1.7, 0.5), (-2.0, 0.3)],
             [(2.15, 0.0), (1.8, -0.55), (1.0, -1.15), (0.0, -1.3), (-1.0, -1.0), (-1.7, -0.5), (-2.0, -0.3)])
    f.add([(2.0, 0.25), (1.6, 0.05), (2.15, 0.0)])
    f.tail("fork", 1.0, 0.95, 2).fin(-0.15, -1.6, 0.95, "top", "long", 0.15, rays=4).fin(-0.15, -1.6, 0.9, "bot", "long", 0.15, rays=4)
    f.fin(0.9, 0.45, 0.5, "bot", "tri", 0.3).pectoral(0.8, -0.2, 0.85, -2.6).gill(1.05, 0.28).eye(1.45, 0.45, 0.2, 0.1)
    blots = []
    for x, y, rx, ry, rot in ((0.6, 0.75, 0.22, 0.13, 0.4), (0.1, 0.3, 0.25, 0.14, -0.3), (-0.4, 0.8, 0.2, 0.12, 0.2), (-0.5, -0.2, 0.24, 0.14, 0.6),
                              (0.4, -0.55, 0.2, 0.12, -0.2), (-1.1, 0.35, 0.2, 0.12, 0.3), (-0.05, -0.85, 0.2, 0.11, 0.1), (0.75, 0.15, 0.17, 0.11, 0.0),
                              (-1.05, -0.5, 0.17, 0.11, 0.5)):
        blots.append(ellipse(x, y, rx, ry, 16, rot=rot))
    f.add(*blots)
    parts, hints = f.done(0.0, 0.2, 1.15)
    brush = [smooth([(-3.4, -2.6), (-2.9, -1.9), (-2.7, -0.8)], 6), [(-2.95, -2.0), (-3.4, -1.3)], [(-2.75, -1.2), (-2.2, -0.6)],
             smooth([(3.4, -2.6), (3.0, -1.8), (3.1, -1.0)], 6), [(3.02, -1.7), (2.6, -1.2)], [(-3.4, -2.6), (3.4, -2.6)]]
    return make("Black Crappie", parts + brush + [[(2.6, 0.45), (2.95, 3.0)]], hints)


@design("fishing_sturgeon", T)
def sturgeon(rng):
    f = Fish([(3.0, 0.05), (2.5, 0.25), (1.6, 0.55), (0.3, 0.7), (-1.2, 0.6), (-2.4, 0.35), (-2.9, 0.3)],
             [(3.0, 0.0), (2.4, -0.35), (1.4, -0.6), (0.0, -0.7), (-1.4, -0.5), (-2.4, -0.3), (-2.9, -0.25)])
    f.tail("shark", 1.4, 0.75, 0).fin(-1.6, -2.3, 0.6, "top", "tri", 0.4).fin(-1.5, -2.1, 0.45, "bot", "tri", 0.35)
    f.fin(-0.2, -0.7, 0.4, "bot", "soft", 0.2).pectoral(1.35, -0.4, 0.85, -2.75, 0.25).gill(1.55, 0.2).eye(2.0, 0.2, 0.12, 0.06)
    f.add(*[[(x, f.bot(x) + 0.02), (x - 0.05, f.bot(x) - 0.3)] for x in (2.55, 2.4, 2.25)])
    f.add(quad((2.0, f.bot(2.0) + 0.05), (1.85, f.bot(1.85) + 0.18), (1.7, f.bot(1.7) + 0.06), 6))
    sc = []
    for k in range(9):
        x = 1.3 - 0.4 * k
        y = f.top(x)
        sc.append(poly((x + 0.18, y - 0.05), (x, y + 0.13), (x - 0.18, y - 0.05), (x, y - 0.22)))
    for k in range(10):
        x = 1.2 - 0.4 * k
        y = f.mid(x) + 0.05
        sc.append(poly((x + 0.17, y), (x, y + 0.14), (x - 0.17, y), (x, y - 0.14)))
    f.add(*sc)
    parts, hints = f.done(0.0, 0.3, 1.0)
    bed = [smooth([(-3.4, -1.3), (-2.0, -1.1), (-0.5, -1.35), (1.2, -1.15), (3.4, -1.3)], 8), ellipse(-1.8, -1.75, 0.6, 0.22, 24), ellipse(1.6, -1.7, 0.45, 0.18, 20)]
    return make("Lake Sturgeon", parts + bed, hints)


@design("fishing_marlin", T)
def marlin(rng):
    f = Fish([(2.2, 0.15), (1.8, 0.55), (0.8, 0.9), (-0.5, 0.85), (-1.8, 0.45), (-2.6, 0.16), (-3.0, 0.1)],
             [(2.2, -0.15), (1.7, -0.55), (0.6, -0.85), (-0.7, -0.75), (-1.9, -0.4), (-2.6, -0.15), (-3.0, -0.1)])
    f.add([(2.2, 0.15), (4.2, 0.02), (2.2, -0.15)])
    f.tail("crescent", 1.3, 1.5, 0).fin(1.35, -0.9, 1.45, "top", "long", 0.25, rays=4).fin(-1.6, -2.0, 0.6, "bot", "tri", 0.4)
    f.fin(-0.9, -1.4, 0.5, "bot", "tri", 0.4).pectoral(1.2, -0.4, 1.4, -2.85, 0.15).gill(1.45, 0.2).eye(1.8, 0.25, 0.16, 0.08)
    for x in (0.7, 0.2, -0.3, -0.8, -1.3, -1.8):
        f.add([(x, f.top(x) - 0.08), (x - 0.1, f.bot(x) + 0.12)])
    parts, hints = f.done(-0.1, 0.9, 0.85, 0.45)
    sea = [wave(-3.6, 3.6, -1.9, 0.12, 5, 90), wave(-3.6, 3.6, -2.6, 0.12, 4, 90)] + splash(-1.9, -1.9, 1.2, 0.9)
    line = [quad((1.5, 1.75), (2.8, 2.4), (3.6, 3.4), 12)]
    return make("Hooked Blue Marlin Leaping", parts + sea + line, hints)


@design("fishing_tuna", T)
def tuna(rng):
    f = Fish([(2.4, 0.05), (2.0, 0.5), (1.0, 0.95), (-0.3, 1.0), (-1.6, 0.6), (-2.5, 0.2), (-2.9, 0.12)],
             [(2.45, -0.12), (2.0, -0.55), (1.0, -0.9), (-0.3, -0.95), (-1.6, -0.55), (-2.5, -0.2), (-2.9, -0.12)])
    f.add([(2.4, 0.05), (2.45, -0.12)])
    f.tail("crescent", 1.2, 1.45, 0).fin(1.0, 0.2, 0.5, "top", "spiny", 0.05, teeth=4).fin(-0.3, -0.8, 1.0, "top", "tri", 0.55)
    f.fin(-0.3, -0.8, 0.95, "bot", "tri", 0.55).pectoral(1.3, 0.0, 1.3, -2.9, 0.18).gill(1.55, 0.2).eye(1.95, 0.25, 0.16, 0.08).mouth(0.4, -0.05)
    for k in range(6):
        x = -1.05 - 0.28 * k
        for side, fn in ((1, f.top), (-1, f.bot)):
            y = fn(x)
            f.add(poly((x, y), (x - 0.12, y + side * 0.2), (x - 0.24, fn(x - 0.24)), closed=False))
    f.add(smooth([(1.35, 0.1), (-0.5, 0.15), (-2.0, 0.05), (-2.8, 0.0)], 8))
    parts, hints = f.done(-0.4, 0.0, 1.0)
    lure = [[(3.15, 0.1), (3.7, 0.1)], circle(2.95, 0.1, 0.2, 14)] + [[(2.8, 0.1 + d), (2.3, 0.1 + d * 2.8)] for d in (-0.12, 0.0, 0.12)]
    bubbles = [circle(-3.8, 0.9, 0.15, 10), circle(-4.1, 1.3, 0.1, 10), circle(-3.7, -0.9, 0.12, 10)]
    return make("Bluefin Tuna Chasing a Lure", parts + lure + bubbles, hints)


@design("fishing_mahi", T)
def mahi(rng):
    f = Fish([(2.3, -0.05), (2.4, 0.5), (2.05, 1.1), (1.2, 1.3), (0.0, 1.05), (-1.3, 0.6), (-2.3, 0.25), (-2.7, 0.18)],
             [(2.3, -0.2), (2.0, -0.6), (1.0, -0.82), (-0.3, -0.75), (-1.5, -0.45), (-2.3, -0.22), (-2.7, -0.18)])
    f.add([(2.3, -0.05), (2.42, -0.12), (2.3, -0.2)])
    f.tail("fork", 1.4, 1.35, 2).fin(1.85, -2.35, 0.6, "top", "long", 0.15, rays=6).fin(-0.15, -2.35, 0.45, "bot", "long", 0.1, rays=3)
    f.pectoral(1.3, -0.25, 0.9, -2.75).gill(1.55, 0.25).eye(1.95, 0.0, 0.16, 0.08)
    f.add(*spots(f, [(0.9, 0.55), (0.3, 0.75), (0.5, 0.15), (-0.3, 0.45), (-0.9, 0.25), (0.0, -0.3), (-1.5, 0.15), (-0.6, -0.15)], 0.11))
    parts, hints = f.done(-0.2, 0.3, 1.0, -0.12)
    sea = [wave(-3.4, 3.4, 2.6, 0.1, 4, 80), circle(2.8, 1.8, 0.14, 10), circle(3.1, 2.2, 0.1, 10)]
    weed = [smooth([(-3.4, -2.2), (-2.0, -2.0), (-0.5, -2.3), (1.0, -2.0), (2.6, -2.25), (3.4, -2.1)], 8)] + \
        [ellipse(x, -2.1 + 0.15 * math.sin(x * 3), 0.22, 0.13, 12) for x in (-2.6, -1.3, 0.2, 1.7, 3.0)]
    return make("Mahi-Mahi Dorado", parts + sea + weed, hints)


@design("fishing_tarpon", T)
def tarpon(rng):
    f = Fish([(2.3, 0.35), (2.0, 0.6), (1.2, 0.9), (0.0, 1.0), (-1.2, 0.8), (-2.1, 0.4), (-2.5, 0.3)],
             [(2.45, -0.05), (2.1, -0.55), (1.2, -0.9), (-0.1, -0.95), (-1.3, -0.65), (-2.1, -0.35), (-2.5, -0.3)])
    f.add([(2.3, 0.35), (1.85, 0.1), (2.45, -0.05)])
    f.tail("fork", 1.3, 1.25, 2).fin(-0.3, -0.9, 0.7, "top", "tri", 0.45).fin(-0.9, -1.5, 0.55, "bot", "tri", 0.35)
    f.add(quad((-0.95, f.top(-0.95) + 0.55), (-1.5, f.top(-1.5) + 1.0), (-2.2, f.top(-2.2) + 0.85), 10))
    f.pectoral(1.0, -0.4, 0.8, -2.6).eye(1.85, 0.42, 0.17, 0.09)
    f.add(quad((1.45, 0.75), (0.9, 0.0), (1.4, -0.75), 12))
    scales = []
    for i, x in enumerate([0.7 - 0.45 * k for k in range(6)]):
        y0, y1 = f.bot(x) + 0.32, f.top(x) - 0.3
        y = y0 + (0.22 if i % 2 else 0.0)
        while y < y1:
            scales.append(arc(x, y, 0.3, math.radians(115), math.radians(245), 10))
            y += 0.45
    f.add(*scales)
    parts, hints = f.done(0.4, 1.0, 0.95, 0.7)
    water = splash(-1.3, -1.9, 1.4, 0.8) + [wave(-3.4, 3.4, -2.6, 0.1, 5, 80)]
    return make("Tarpon Jumping in the Flats", parts + water, hints)


# ---------------------------------------------------------------- tackle

def crankbait(cx, cy, s=1.0, rot=0.0, hooks=True):
    body = smooth([(1.2, 0.0), (1.0, 0.4), (0.3, 0.6), (-0.6, 0.5), (-1.2, 0.15), (-1.25, -0.1), (-0.6, -0.45), (0.3, -0.55), (1.0, -0.35)], 8, True)
    lip = poly((1.05, -0.2), (1.9, -0.75), (1.75, -0.98), (0.85, -0.45))
    parts = [body, lip, circle(0.72, 0.12, 0.2, 16), quad((0.45, 0.45), (0.25, 0.0), (0.45, -0.45), 8),
             [(-0.1, 0.35), (-0.7, -0.25)], [(-0.5, 0.42), (-1.0, -0.1)], [(0.2, 0.25), (-0.3, -0.35)]]
    if hooks:
        parts += treble(0.0, -0.55, 0.9) + treble(-1.25, -0.05, 0.9)
    return [transform(p, cx, cy, s, rot) for p in parts]


@design("fishing_rod_and_reel", T)
def rod_and_reel(rng):
    rod = [rrect(-3.8, -0.17, -2.0, 0.17, 0.15), rect(-2.0, -0.12, -1.3, 0.12), rrect(-1.3, -0.14, -0.5, 0.14, 0.12),
           [(-0.5, 0.1), (2.5, 0.05)], [(-0.5, -0.1), (2.5, -0.05)], [(2.5, 0.05), (4.4, 0.0), (2.5, -0.05)]]
    for x, r in ((0.3, 0.3), (1.3, 0.25), (2.2, 0.2), (3.0, 0.17), (3.7, 0.15)):
        cy = -0.1 - 0.12 - r
        rod += [circle(x, cy, r, 16), [(x, -0.07), (x, cy + r)]]
    rod += spin_reel(-1.65, -1.25, 1.0)
    rod += [[(-0.45, -1.25), (0.3, -0.4), (4.4, 0.0)]]
    rot = 0.5
    parts = [transform(p, -0.3, -1.0, 1, rot) for p in rod]
    tip = transform([(4.4, 0.0)], -0.3, -1.0, 1, rot)[0]
    hang = [[tip, (tip[0], tip[1] - 2.6)]]
    lure = crankbait(tip[0] + 0.1, tip[1] - 3.15, 0.75, -1.4)
    return make("Spinning Rod and Reel", parts + hang + lure)


@design("fishing_baitcaster", T)
def baitcaster(rng):
    plate = [circle(0.6, 0.6, 1.7, 80), circle(0.6, 0.6, 1.3, 70), circle(0.6, 0.6, 0.25, 16)]
    star_ = [star(0.6, 0.6, 0.7, 6, 0.6)]
    a = 0.55
    ux, uy = math.cos(a), math.sin(a)
    arm = [[(0.6 + t * ux + o * -uy, 0.6 + t * uy + o * ux) for t in (-1.9, 1.9)] for o in (-0.17, 0.17)]
    arm = clip_all(arm, [(0.6, 0.6, 0.72)])
    knobs = [ellipse(0.6 + 2.15 * ux, 0.6 + 2.15 * uy, 0.55, 0.32, 24, rot=a + math.pi / 2),
             ellipse(0.6 - 2.15 * ux, 0.6 - 2.15 * uy, 0.55, 0.32, 24, rot=a + math.pi / 2)]
    body = clip_all([rrect(-2.8, -0.9, 0.2, 2.0, 0.9)], [(0.6, 0.6, 1.72), (0.6 - 2.15 * ux, 0.6 - 2.15 * uy, 0.6)])
    thumb = [rrect(-2.2, 1.55, -0.8, 1.85, 0.12)]
    wind = [rrect(-3.2, -0.5, -2.8, 0.9, 0.15)]
    foot = [poly((-1.8, -0.9), (-1.6, -1.6), (0.2, -1.6), (0.4, -1.05), closed=False)]
    rod = [rrect(-3.5, -2.05, 3.4, -1.6, 0.2), [(-2.2, -2.05), (-2.2, -1.6)], [(1.2, -2.05), (1.2, -1.6)]]
    line = [quad((-3.2, 0.2), (-3.6, 0.6), (-3.7, 1.6), 8)]
    return make("Baitcasting Reel", plate + star_ + arm + knobs + body + thumb + wind + foot + rod + line)


@design("fishing_fly_reel", T)
def fly_reel(rng):
    cx, cy = -0.3, 0.2
    out = [circle(cx, cy, 2.3, 100), circle(cx, cy, 2.0, 90), circle(cx, cy, 0.4, 24), circle(cx, cy, 0.18, 12)]
    for k in range(6):
        a = k * TAU / 6 + 0.3
        out.append(circle(cx + 1.15 * math.cos(a), cy + 1.15 * math.sin(a), 0.38, 24))
    out += [rrect(cx + 0.95, cy - 0.95 - 0.0, cx + 1.45, cy - 0.45, 0.2)]
    out = out[:-1]
    knob = [circle(cx + 1.6 * math.cos(-0.22), cy + 1.6 * math.sin(-0.22), 0.28, 20)]
    foot = [rect(cx - 0.35, cy + 2.3, cx + 0.35, cy + 2.6), rrect(cx - 1.4, cy + 2.6, cx + 1.4, cy + 2.85, 0.1)]
    line = [cubic((cx + 2.0, cy + 1.0), (2.6, 2.2), (3.0, 1.0), (3.4, 2.9), 24)]
    return make("Fly Fishing Reel", out + knob + foot + line)


@design("fishing_crankbait", T)
def crankbait_design(rng):
    lure = crankbait(-0.3, 0.6, 2.2, 0.0)
    bubbles = [circle(-3.4, 1.5, 0.15, 10), circle(-3.1, 2.0, 0.12, 10), circle(-3.5, 2.4, 0.1, 10)]
    return make("Crankbait Lure with Treble Hooks", lure + bubbles)


@design("fishing_spinner_spoon", T)
def spinner_spoon(rng):
    x = -1.3
    spin = [circle(x, 2.75, 0.17, 12), [(x, 2.58), (x, -1.7)], circle(x, 2.15, 0.17, 12),
            lens((x + 0.05, 2.1), (x + 1.0, 0.25), 0.33, 16), [(x + 0.2, 1.7), (x + 0.8, 0.6)],
            circle(x, 1.75, 0.2, 14), circle(x, 1.35, 0.2, 14), lens((x, 1.15), (x, -0.55), 0.3, 16)]
    spin += treble(x, -0.55, 1.2)
    spin += [[(x - 0.1, -0.8), (x - 0.45, -1.8)], [(x + 0.1, -0.8), (x + 0.45, -1.8)], [(x, -0.8), (x, -1.9)]]
    sx = 1.6
    spoon = [circle(sx, 2.75, 0.17, 12), circle(sx, 2.35, 0.2, 12),
             smooth([(sx, 2.1), (sx + 0.55, 1.6), (sx + 0.75, 0.3), (sx + 0.4, -0.7), (sx, -0.9), (sx - 0.4, -0.7), (sx - 0.75, 0.3), (sx - 0.55, 1.6)], 8, True),
             smooth([(sx, 1.75), (sx + 0.4, 1.2), (sx + 0.5, 0.3), (sx + 0.25, -0.45), (sx, -0.55), (sx - 0.25, -0.45), (sx - 0.5, 0.3), (sx - 0.4, 1.2)], 8, True),
             circle(sx, -0.75, 0.12, 10)]
    spoon += treble(sx, -0.9, 1.2)
    spoon += [lens((sx - 0.2, 0.9), (sx + 0.2, 0.0), 0.0001, 2)[:2]]
    lines = [[(x, 2.92), (x, 3.4)], [(sx, 2.92), (sx, 3.4)]]
    return make("Inline Spinner and Casting Spoon", spin + spoon[:-1] + lines)


def fly_hook(x, y, L=1.8):
    """Horizontal fly hook: eye on the right, bend on the left."""
    return [[(x + L / 2, y), (x - L / 2, y)], arc(x - L / 2, y - 0.3, 0.3, math.pi / 2, 3 * math.pi / 2, 10),
            [(x - L / 2, y - 0.6), (x - L / 2 + 0.45, y - 0.45)], circle(x + L / 2 + 0.12, y, 0.12, 10)]


@design("fishing_flies", T)
def flies(rng):
    # dry fly
    dx, dy = -1.6, 1.4
    dry = fly_hook(dx, dy) + [lens((dx - 0.8, dy + 0.05), (dx + 0.3, dy + 0.05), 0.2, 10)]
    dry += [[(dx + 0.5 + 0.2 * math.cos(a), dy + 0.2 * math.sin(a)), (dx + 0.5 + 0.7 * math.cos(a), dy + 0.7 * math.sin(a))] for a in [k * TAU / 8 + 0.4 for k in range(8)]]
    dry += [lens((dx + 0.45, dy + 0.1), (dx + 0.15, dy + 1.35), 0.25, 10), lens((dx + 0.55, dy + 0.1), (dx + 0.85, dy + 1.35), 0.25, 10)]
    dry += [[(dx - 0.85, dy + 0.05), (dx - 1.8, dy + 0.35)], [(dx - 0.85, dy), (dx - 1.85, dy - 0.05)], [(dx - 0.85, dy - 0.05), (dx - 1.75, dy - 0.45)]]
    # streamer
    sx, sy = 1.3, 0.2
    stream = fly_hook(sx, sy, 2.0) + [lens((sx + 0.9, sy + 0.05), (sx - 2.2, sy + 0.45), 0.13, 16), lens((sx + 0.9, sy + 0.1), (sx - 2.0, sy + 0.85), 0.1, 16),
                                       lens((sx - 0.9, sy - 0.02), (sx + 0.8, sy - 0.02), 0.15, 10), circle(sx + 0.95, sy + 0.05, 0.2, 14)]
    stream = [transform(p, 0, 0, 1, 0.0) for p in stream]
    # nymph
    nx, ny = -0.4, -1.9
    nymph = fly_hook(nx, ny, 1.6) + [circle(nx + 0.75, ny, 0.28, 16), lens((nx - 0.75, ny), (nx + 0.5, ny), 0.3, 12)]
    nymph += [[(nx - 0.45 + 0.3 * k, ny - 0.15), (nx - 0.45 + 0.3 * k, ny + 0.15)] for k in range(4)]
    nymph += [[(nx + 0.3, ny - 0.15), (nx + 0.6, ny - 0.6)], [(nx + 0.1, ny - 0.15), (nx + 0.2, ny - 0.65)], [(nx - 0.75, ny), (nx - 1.3, ny + 0.2)], [(nx - 0.75, ny), (nx - 1.3, ny - 0.2)]]
    dry = [transform(p, -0.2, 0.6, 1.15) for p in dry]
    stream = [transform(p, 0.3, -0.9, 1.1) for p in stream]
    nymph = [transform(p, 0.2, -0.3, 1.25) for p in nymph]
    return make("Hand-Tied Fishing Flies", dry + stream + nymph)


@design("fishing_bobber", T)
def bobber(rng):
    bob = [circle(0, 0.7, 1.3, 70), arc(0, 0.7, 1.3, 0, 0, 2)]
    band = [[(1.3 * math.cos(t), 0.7 + 0.35 * math.sin(t)) for t in [math.pi + math.pi * i / 30 for i in range(31)]]]
    stem = [rrect(-0.12, 1.95, 0.12, 2.5, 0.06), [(0, 2.5), (0.4, 3.6)]]
    shine = [arc(0, 0.7, 1.0, math.radians(110), math.radians(160), 8)]
    water = [wave(-3.4, -1.45, 0.25, 0.06, 1.5, 24), wave(1.45, 3.4, 0.25, 0.06, 1.5, 24)]
    rip = clip_all([ellipse(0, 0.25, r, r * 0.25, 60) for r in (1.9, 2.6, 3.3)], [(0, 0.7, 1.35)])
    under = [[(0, -0.6), (0, -2.0)]] + hook(0, -2.9, 0.9) + [tube(smooth([(0.0, -2.3), (0.35, -2.5), (0.0, -2.75), (0.4, -3.0), (0.15, -3.3)], 6), 0.13, cap=True)]
    pad = [[(x, y * 0.4 - 0.75) for x, y in chain(arc(-2.4, 0, 0.8, 0.35, TAU - 0.2, 30), [(-2.4, 0.0)], [(-2.4 + 0.8 * math.cos(0.35), 0.8 * math.sin(0.35))])]]
    return make("Bobber Floating on the Pond", bob + band + stem + shine + water + rip + under + pad)


@design("fishing_tackle_box", T)
def tackle_box(rng):
    base = [rect(-2.4, -2.8, 2.4, -0.8), rrect(-0.35, -1.4, 0.35, -1.0, 0.08)]
    lid = [poly((-2.4, -0.8), (-2.1, 1.4), (2.1, 1.4), (2.4, -0.8), closed=False), rrect(-0.7, 1.4, 0.7, 1.75, 0.15)]
    trays = []
    for x0, x1, y0, y1 in ((-3.4, -0.2, -0.8, -0.1), (0.2, 3.4, -0.8, -0.1), (-2.9, -0.4, 0.3, 1.0), (0.4, 2.9, 0.3, 1.0)):
        trays.append(rect(x0, y0, x1, y1))
        n = 3
        for k in range(1, n):
            x = x0 + (x1 - x0) * k / n
            trays.append([(x, y0), (x, y1)])
    arms = [[(-2.4, -1.2), (-3.0, -0.8)], [(2.4, -1.2), (3.0, -0.8)], [(-1.9, -0.1), (-1.7, 0.3)], [(1.9, -0.1), (1.7, 0.3)]]
    items = []
    # lower left tray
    items += [lens((-3.25, -0.45), (-2.5, -0.45), 0.3, 8), smooth([(-2.15, -0.25), (-1.95, -0.6), (-1.7, -0.3), (-1.45, -0.65)], 4),
              circle(-0.73, -0.45, 0.22, 12)]
    # lower right tray
    items += [smooth([(0.35, -0.3), (0.6, -0.6), (0.85, -0.3), (1.1, -0.6)], 4), lens((1.4, -0.3), (2.25, -0.55), 0.3, 8),
              circle(2.75, -0.45, 0.2, 12), [(2.75, -0.25), (2.75, -0.15)]]
    # upper trays
    items += [hook(-2.55, 0.6, 0.3)[1], circle(-1.6, 0.65, 0.22, 12), lens((-1.15, 0.65), (-0.55, 0.65), 0.35, 8),
              lens((0.55, 0.65), (1.15, 0.65), 0.35, 8), smooth([(1.4, 0.45), (1.6, 0.85), (1.85, 0.45), (2.0, 0.85)], 4), circle(2.45, 0.65, 0.2, 12)]
    return make("Open Tackle Box", base + lid + trays + arms + items)


def simple_fish(L=3.0, H=0.7, tail=0.7):
    """Plain fish for nets, stringers and scales; nose at +L/2."""
    f = Fish([(L / 2, 0.0), (L * 0.38, 0.4 * H), (L * 0.15, 0.9 * H), (-L * 0.15, H), (-L * 0.38, 0.6 * H), (-L / 2, 0.22 * H)],
             [(L / 2, -0.05), (L * 0.38, -0.4 * H), (L * 0.1, -0.85 * H), (-L * 0.2, -0.85 * H), (-L * 0.38, -0.5 * H), (-L / 2, -0.22 * H)])
    f.tail("fork", tail, 0.8 * H + 0.3, 1).fin(0.05 * L, -0.2 * L, 0.45 * H, "top", "soft", 0.15).pectoral(L * 0.25, -0.15 * H, 0.25 * L, -2.7, 0.3)
    f.gill(L * 0.3, 0.15).eye(L * 0.4, 0.25 * H, 0.06 * L + 0.04, 0.035 * L + 0.02).mouth(0.1 * L, -0.08 * H)
    return f


@design("fishing_landing_net", T)
def landing_net(rng):
    hoop = [ellipse(0.7, 1.4, 2.0, 0.75, 80)]
    handle = [tube([(-1.25, 1.2), (-3.3, -2.8)], 0.26, cap=True), tube([(-2.6, -1.42), (-3.3, -2.8)], 0.42, cap=True)]
    bag = [smooth([(-1.3, 1.3), (-1.0, -0.3), (0.3, -1.9), (1.2, -2.0), (2.0, -0.6), (2.7, 1.3)], 8)]
    mesh = []
    for k in range(1, 6):
        x = -1.3 + 4.0 * k / 6
        mesh.append(quad((x, 1.4 - 0.75 * math.sqrt(max(0, 1 - ((x - 0.7) / 2.0) ** 2))), (x * 0.5 + 0.3, -0.6), (0.75, -1.95), 10))
    mesh += [quad((-1.1, 0.3), (0.7, -0.2), (2.25, 0.3), 12), quad((-0.5, -0.8), (0.75, -1.2), (1.95, -0.8), 12)]
    f = simple_fish(2.8, 0.65, 0.8)
    fish, hints = f.done(0.8, 0.2, 1.0, 0.45)
    holes = [(0.8 + t * math.cos(0.45), 0.2 + t * math.sin(0.45), 0.62) for t in (-1.1, -0.6, -0.1, 0.4, 0.9, 1.2)]
    return make("Landing Net with the Catch", clip_all(hoop + bag + mesh, holes) + handle + fish, hints)


@design("fishing_creel", T)
def creel(rng):
    body = [poly((-2.3, 1.0), (-2.1, -2.4), (2.1, -2.4), (2.3, 1.0), closed=False), [(-2.3, 1.0), (2.3, 1.0)]]
    weave = []
    for y in (0.6, 0.1, -0.4, -0.9, -1.4, -1.9):
        w = 2.1 + 0.2 * (y + 2.4) / 3.4
        weave.append(wave(-w + 0.02, w - 0.02, y, 0.08, 6, 60))
    for k in range(1, 8):
        x = -2.1 + 4.2 * k / 8
        weave.append([(x * 1.07, 1.0), (x, -2.4)])
    lid = [poly((-2.45, 1.0), (-2.3, 1.75), (2.3, 1.75), (2.45, 1.0), closed=False), ellipse(-0.3, 1.38, 0.55, 0.22, 24)]
    hinge = [rect(-1.6, 1.75, -1.1, 2.0), rect(1.1, 1.75, 1.6, 2.0)]
    latch = [rrect(-0.2, 0.55, 0.2, 1.25, 0.08)]
    strap = [cubic((-2.25, 0.6), (-2.6, 3.4), (2.6, 3.4), (2.25, 0.6), 30), cubic((-2.0, 0.6), (-2.3, 3.0), (2.3, 3.0), (2.0, 0.6), 30)]
    tail = [chain(quad((-0.6, 1.45), (-0.55, 1.9), (-0.75, 2.25), 6), quad((-0.75, 2.25), (-1.0, 2.5), (-1.15, 2.85), 6),
                  quad((-1.15, 2.85), (-0.75, 2.55), (-0.55, 2.5), 6), quad((-0.55, 2.5), (-0.3, 2.65), (0.1, 2.75), 6),
                  quad((0.1, 2.75), (-0.2, 2.4), (-0.3, 2.2), 6), quad((-0.3, 2.2), (-0.1, 1.9), (-0.05, 1.45), 6))]
    return make("Wicker Fishing Creel", body + clip_box(weave, -0.25, 0.0, 0.25, 1.3) + lid + hinge + latch + clip_box(strap, -2.4, 0.5, 2.4, 2.05) + tail)


def mini_fly(x, y, s=1.0, rot=0.0):
    parts = [[(-0.5, 0), (0.5, 0)], arc(-0.5, -0.18, 0.18, math.pi / 2, 3 * math.pi / 2, 8), lens((-0.4, 0.02), (0.3, 0.02), 0.35, 8),
             lens((0.25, 0.05), (0.0, 0.75), 0.3, 8), lens((0.3, 0.05), (0.6, 0.7), 0.3, 8), [(-0.45, 0.05), (-0.95, 0.25)]]
    return [transform(p, x, y, s, rot) for p in parts]


@design("fishing_hat_with_flies", T)
def hat_with_flies(rng):
    crown = chain([(-1.9, 0.0)], cubic((-1.9, 0.0), (-1.8, 2.6), (1.8, 2.6), (1.9, 0.0), 40))
    brim = [chain(arc(0, 0.0, 3.2, math.pi, 2 * math.pi, 1)[:0], quad((-1.9, 0.0), (-3.3, 0.0), (-3.4, -0.7), 12), quad((-3.4, -0.7), (0.0, -1.5), (3.4, -0.7), 30),
                  quad((3.4, -0.7), (3.3, 0.0), (1.9, 0.0), 12)), quad((-1.9, 0.0), (0.0, -0.5), (1.9, 0.0), 20)]
    band = [quad((-1.85, 0.45), (0.0, 0.05), (1.85, 0.45), 20), quad((-1.8, 0.95), (0.0, 0.6), (1.8, 0.95), 20)]
    stitch = [quad((-2.9, -0.55), (0.0, -1.2), (2.9, -0.55), 30)]
    fl = mini_fly(-1.0, 0.55, 0.9, 0.2) + mini_fly(0.4, 0.42, 0.9, -0.1) + mini_fly(1.4, 1.35, 0.8, 0.5)
    vents = [circle(-1.1, 1.6, 0.13, 10), circle(1.1, 1.6, 0.13, 10)]
    holes = [(-1.0, 0.75, 0.42), (0.4, 0.65, 0.42)]
    return make("Angler's Hat with Flies", [crown] + brim + clip_all(band, holes) + stitch + fl + vents)


@design("fishing_waders", T)
def waders(rng):
    peg = [circle(0, 3.2, 0.18, 12), [(-1.5, 3.2), (1.5, 3.2)]]
    straps = [[(-1.0, 1.75), (-0.15, 3.1)], [(1.0, 1.75), (0.15, 3.1)], [(-0.75, 1.75), (-0.1, 2.9)], [(0.75, 1.75), (0.1, 2.9)]]
    bib = [poly((-1.15, 1.75), (1.15, 1.75), (1.3, 0.0), closed=False), [(-1.15, 1.75), (-1.3, 0.0)], rrect(-0.6, 0.6, 0.6, 1.4, 0.12)]
    belt = [rect(-1.35, -0.25, 1.35, 0.05), rect(-0.25, -0.3, 0.25, 0.1)]
    legs = [poly((-1.35, -0.25), (-1.4, -2.2), closed=False), poly((1.35, -0.25), (1.4, -2.2), closed=False),
            poly((-0.15, -0.25), (-0.12, -2.2), closed=False), poly((0.15, -0.25), (0.12, -2.2), closed=False)]
    boots = []
    for sg in (-1, 1):
        x0, x1 = sorted((sg * 0.12, sg * 1.4))
        boots += [rect(x0, -2.6, x1, -2.2), poly((x0, -2.6), (x0 - 0.05 * (sg < 0), -3.0), (x1 + 0.45 * (sg > 0), -3.0), (x1 + 0.05, -2.6), closed=False)]
    boots = []
    for sg in (-1, 1):
        a, b = sg * 0.12, sg * 1.4
        toe = sg * 1.95
        boots += [[(a, -2.2), (b, -2.2)], chain([(a, -2.2), (a, -3.0), (toe, -3.0)], quad((toe, -3.0), (toe, -2.55), (b, -2.45), 6), [(b, -2.2)]),
                  [(a, -2.8), (toe, -2.8)]]
    knees = [arc(-0.75, -1.2, 0.35, math.radians(200), math.radians(340), 8), arc(0.75, -1.2, 0.35, math.radians(200), math.radians(340), 8)]
    return make("Chest Waders and Boots", peg + straps + bib + belt + legs + boots + knees)


@design("fishing_worm_hook", T)
def worm_hook(rng):
    hk = [circle(0, 2.6, 0.22, 16), [(0, 2.38), (0, -1.4)], arc(0.75, -1.4, 0.75, math.pi, 2 * math.pi, 24), [(1.5, -1.4), (1.5, -0.6)],
          poly((1.5, -0.6), (1.75, -0.95), (1.5, -0.9), closed=False)]
    line = [[(0, 2.82), (0, 3.5)]]
    worm = tube(smooth([(-1.3, 1.9), (-0.6, 2.0), (0.4, 1.6), (-0.4, 1.0), (0.5, 0.4), (-0.5, -0.2), (0.4, -0.8), (-0.3, -1.6), (-1.5, -1.8), (-2.2, -1.2)], 8),
                lambda t: 0.36 if 0.1 < t < 0.9 else 0.36 * (0.4 + 0.6 * min(t, 1 - t) / 0.1), cap=True)
    bubbles = [circle(2.4, 0.5, 0.18, 12), circle(2.7, 1.2, 0.14, 10), circle(2.3, 1.9, 0.11, 10)]
    wc = smooth([(-1.3, 1.9), (-0.6, 2.0), (0.4, 1.6), (-0.4, 1.0), (0.5, 0.4), (-0.5, -0.2), (0.4, -0.8), (-0.3, -1.6), (-1.5, -1.8), (-2.2, -1.2)], 8)
    holes = [(x, y, 0.25) for x, y in densify(wc, 0.1)]
    return make("Worm on a Hook", clip_all(hk, holes) + line + [worm] + bubbles + [[(-3.4, -3.0), (3.4, -3.0)]])


@design("fishing_stringer", T)
def stringer(rng):
    post = [rect(-3.2, 2.3, 3.2, 2.75), [(-3.2, 2.75), (-3.2, 3.2)], [(3.2, 2.75), (3.2, 3.2)], [(-3.2, 3.2), (3.2, 3.2)],
            rect(-2.6, -1.8, -2.1, 2.3), rect(2.1, -1.8, 2.6, 2.3)]
    cord = [quad((-2.1, 1.9), (0.0, 0.6), (2.1, 1.9), 30)]
    fish, hints = [], []
    for x, L, H in ((-1.3, 2.5, 0.55), (0.0, 3.0, 0.65), (1.3, 2.4, 0.5)):
        top = 1.9 - (1.3 * (1 - (x / 2.1) ** 2)) + 0.0
        top = yat(cord[0], x) - 0.25
        f = simple_fish(L, H, 0.7)
        p, h = f.done(x, top - L / 2, 1.0, math.pi / 2)
        fish += p
        hints += h
        fish.append(circle(x, top + 0.1, 0.13, 10))
    water = [wave(-3.4, 3.4, -2.9, 0.1, 5, 80)]
    return make("Stringer of Fresh Catch", post + cord + fish + water, hints)


@design("fishing_lure_collection", T)
def lure_collection(rng):
    board = [rrect(-3.4, -3.0, 3.4, 3.0, 0.2), rrect(-3.15, -2.75, 3.15, 2.75, 0.15)]
    items = []
    # row 1: crankbait, popper, spoon
    items += [[(-2.2, 2.25), (-2.2, 1.9)]] + crankbait(-2.2, 1.35, 0.55, -1.57)
    popper = [[(0.0, 2.25), (0.0, 1.95)], ellipse(0.0, 1.85, 0.35, 0.12, 16),
              chain([(-0.35, 1.85)], quad((-0.42, 1.0), (-0.3, 0.4), (-0.05, 0.1), 10), quad((0.3, 0.4), (0.42, 1.0), (0.35, 1.85), 10)),
              circle(0.0, 1.45, 0.12, 10), [(-0.36, 1.2), (0.36, 1.2)]]
    popper += treble(0.0, 0.1, 0.8) + [[(-0.15, -0.2), (-0.25, -0.55)], [(0.15, -0.2), (0.25, -0.55)]]
    items += popper
    spoon = [[(2.2, 2.25), (2.2, 1.95)], circle(2.2, 1.85, 0.1, 8),
             smooth([(2.2, 1.75), (2.6, 1.3), (2.65, 0.6), (2.4, 0.2), (2.2, 0.1), (2.0, 0.2), (1.75, 0.6), (1.8, 1.3)], 8, True),
             smooth([(2.2, 1.45), (2.4, 1.15), (2.42, 0.65), (2.2, 0.38), (1.98, 0.65), (2.0, 1.15)], 8, True)]
    spoon += treble(2.2, 0.1, 0.8)
    items += spoon
    # row 2: jig, soft worm, spinnerbait
    jig = [[(-2.2, -0.25), (-2.2, -0.55)], circle(-2.2, -0.85, 0.3, 18), [(-2.2, -1.15), (-2.2, -2.2)],
           arc(-1.95, -2.2, 0.25, math.pi, 2 * math.pi, 8), [(-1.7, -2.2), (-1.7, -1.9)]]
    jig += [[(-2.25, -1.2), (-2.6 + 0.15 * k, -2.5)] for k in range(4)]
    items += jig
    worm = [[(0.0, -0.25), (0.0, -0.5)], tube(smooth([(0.0, -0.6), (0.3, -1.0), (-0.25, -1.4), (0.3, -1.8), (-0.1, -2.2), (0.15, -2.5)], 6), 0.22, cap=True)]
    items += worm
    sb = [[(2.2, -0.25), (2.2, -0.5)], [(2.2, -0.5), (1.8, -1.6)], [(2.2, -0.5), (2.65, -0.9)], lens((2.65, -0.95), (2.75, -1.75), 0.35, 10),
          lens((2.68, -0.75), (2.95, -1.0), 0.4, 8), ellipse(1.75, -1.75, 0.18, 0.25, 12), [(1.75, -2.0), (1.75, -2.5)]]
    sb += [[(1.7, -2.0), (1.4, -2.55)], [(1.8, -2.0), (2.1, -2.55)]]
    items += sb
    return make("Collection of Fishing Lures", board + items)


@design("fishing_fly_vise", T)
def fly_vise(rng):
    base = [ellipse(0.0, -2.4, 2.2, 0.45, 60), ellipse(0.0, -2.55, 2.2, 0.45, 60)[30:61] if False else
            [(2.2 * math.cos(t), -2.65 + 0.45 * math.sin(t)) for t in [math.pi + math.pi * i / 30 for i in range(31)]],
            [(-2.2, -2.4), (-2.2, -2.65)], [(2.2, -2.4), (2.2, -2.65)]]
    stem = [rect(-0.15, -2.4, 0.15, 0.6), rrect(-0.4, 0.6, 0.4, 1.0, 0.1)]
    jaws = [poly((-0.3, 1.0), (0.8, 2.4), (1.4, 2.4), (1.5, 2.2), (0.3, 0.9), closed=False), [(0.25, 1.65), (1.0, 1.0)],
            rrect(0.95, 0.85, 1.25, 1.15, 0.08)]
    lever = [[(-0.2, 0.8), (-1.3, 0.3)], circle(-1.4, 0.25, 0.15, 10)]
    hook_ = [[(1.45, 2.32), (2.7, 2.32)], arc(1.45, 2.02, 0.3, math.pi / 2, 3 * math.pi / 2, 10), [(1.45, 1.72), (1.75, 1.85)], circle(2.82, 2.32, 0.1, 8)]
    fly = [lens((1.6, 2.35), (2.5, 2.35), 0.3, 10)] + [[(2.4, 2.35), (2.4 + 0.5 * math.cos(a), 2.35 + 0.5 * math.sin(a))] for a in (0.6, 1.3, 2.0, 2.7, 3.6, 4.4)]
    bobbin = [[(2.0, 2.2), (2.0, 0.6)], circle(2.0, 0.35, 0.25, 14), [(1.75, 0.35), (1.6, -0.6)], [(2.25, 0.35), (2.4, -0.6)], [(2.0, 0.1), (2.0, -1.2)]]
    feather = [lens((-3.2, -2.0), (-1.4, -1.6), 0.2, 16), [(-3.3, -2.05), (-1.4, -1.6)]]
    return make("Fly Tying Vise", base + stem + jaws + lever + hook_ + fly + bobbin + feather)


@design("fishing_vest", T)
def vest(rng):
    left = [chain([(-0.2, -2.6), (-0.2, 1.2), (-0.9, 3.0), (-1.5, 3.05)], quad((-1.5, 3.05), (-1.6, 1.9), (-2.7, 1.5), 12), [(-2.75, -2.6), (-0.2, -2.6)])]
    right = [mirror_x(p) for p in left]
    pockets = []
    for sg in (-1, 1):
        for (x0, x1, y0, y1) in ((0.45, 1.35, 0.2, 1.3), (1.5, 2.45, 0.2, 1.3), (0.45, 2.45, -2.3, -0.8)):
            a, b = sorted((sg * x0, sg * x1))
            pockets += [rect(a, y0, b, y1), [(a, y1 - 0.3), (b, y1 - 0.3)], rrect((a + b) / 2 - 0.12, y1 - 0.45, (a + b) / 2 + 0.12, y1 - 0.2, 0.05)]
    patch = [rrect(-1.75, 1.6, -0.55, 2.3, 0.15), lens((-1.6, 1.95), (-0.95, 2.1), 0.35, 8), lens((-1.3, 1.75), (-0.7, 1.85), 0.35, 8)]
    zinger = [circle(1.0, 2.0, 0.28, 16), [(1.0, 1.72), (1.0, 1.45)], circle(1.0, 2.0, 0.1, 8)]
    return make("Fly Fishing Vest", left + right + pockets + patch + zinger)


@design("fishing_fillet_board", T)
def fillet_board(rng):
    board = [rrect(-3.7, -2.4, 3.0, 0.9, 0.35), ellipse(-3.25, -0.75, 0.2, 0.45, 16)]
    f = simple_fish(4.2, 0.9, 1.0)
    fish, hints = f.done(0.45, -0.75, 1.0, 0.0)
    knife = [chain([(-1.5, 1.55)], quad((0.3, 1.95), (2.2, 1.8), (2.9, 1.65), 10), quad((2.1, 1.35), (0.3, 1.25), (-1.5, 1.3), 10), [(-1.5, 1.55)]),
             rrect(-3.3, 1.25, -1.5, 1.6, 0.17), [(-2.95, 1.35), (-2.95, 1.5)], [(-1.85, 1.35), (-1.85, 1.5)]]
    return make("Fillet Knife and Fresh Catch", board + fish + knife, hints)


@design("fishing_tournament_trophy", T)
def tournament_trophy(rng):
    f = Fish([(1.5, 0.15), (1.25, 0.45), (0.75, 0.7), (0.0, 0.8), (-0.7, 0.6), (-1.2, 0.3), (-1.5, 0.2)],
             [(1.6, -0.2), (1.25, -0.45), (0.6, -0.65), (-0.1, -0.7), (-0.7, -0.55), (-1.2, -0.28), (-1.5, -0.2)])
    f.add([(1.5, 0.15), (0.95, -0.05), (1.6, -0.2)])
    f.tail("square", 0.7, 0.65, 2).fin(0.6, -0.1, 0.5, "top", "spiny", 0.05, teeth=4).fin(-0.15, -0.9, 0.45, "top", "soft", 0.15)
    f.pectoral(0.6, -0.15, 0.6, -2.7).gill(0.8, 0.18).eye(1.15, 0.3, 0.14, 0.07)
    fish, hints = f.done(0.0, 2.3, 1.0, 0.55)
    cup = [chain([(-1.4, 1.2)], cubic((-1.4, 1.2), (-1.4, -0.3), (-0.6, -0.8), (-0.25, -0.9), 20), [(0.25, -0.9)],
                 cubic((0.25, -0.9), (0.6, -0.8), (1.4, -0.3), (1.4, 1.2), 20)), ellipse(0, 1.2, 1.4, 0.25, 50)]
    handles = [smooth([(-1.38, 0.9), (-2.1, 1.0), (-2.15, 0.3), (-1.2, -0.2)], 8), smooth([(1.38, 0.9), (2.1, 1.0), (2.15, 0.3), (1.2, -0.2)], 8)]
    stem = [[(-0.25, -0.9), (-0.2, -1.6)], [(0.25, -0.9), (0.2, -1.6)], ellipse(0, -1.65, 0.45, 0.12, 20),
            poly((-0.35, -1.7), (-0.8, -2.2), (0.8, -2.2), (0.35, -1.7), closed=False)]
    base = [rect(-1.5, -3.0, 1.5, -2.2), rect(-1.0, -2.8, 1.0, -2.4)]
    hookm = hook(-0.15, -0.3, 0.6)
    return make("Bass Tournament Trophy", fish + cup + handles + stem + base + hookm, hints)


@design("fishing_cooler", T)
def cooler(rng):
    box = [rrect(-2.8, -2.8, 2.8, -0.2, 0.25), [(-2.8, -0.75), (2.8, -0.75)], rrect(-0.6, -1.4, 0.6, -1.05, 0.1)]
    lid = [poly((-2.8, -0.2), (-2.4, 2.0), (2.4, 2.0), (2.8, -0.2), closed=False), [(-2.6, 0.9), (2.6, 0.9)]]
    handles = [rrect(-3.3, -1.6, -2.8, -1.2, 0.1), rrect(2.8, -1.6, 3.3, -1.2, 0.1)]
    fish, hints = [], []
    for x, rot, L in ((-1.3, 1.25, 2.4), (0.2, 1.75, 2.6), (1.5, 1.4, 2.2)):
        f = simple_fish(L, 0.5, 0.65)
        p, h = f.done(x, 0.2, 1.0, rot)
        fish += p
        hints += h
    ice = [rrect(x - 0.3, -0.45, x + 0.3, 0.05, 0.08) for x in (-2.2, -0.6, 0.85, 2.2)]
    fish = clip_box(fish, -2.79, -2.0, 2.79, -0.2)
    return make("Cooler of Fish on Ice", clip_all(lid, [(-1.3, 0.2, 0.0)]) + box + handles + fish + ice, hints)


# ---------------------------------------------------------------- anglers

def rod(butt, tip, bend=0.0, grip=0.28, reel=True):
    """Fishing rod from butt to tip, bent sideways by `bend` (fraction of length)."""
    L = math.hypot(tip[0] - butt[0], tip[1] - butt[1])
    ux, uy = (tip[0] - butt[0]) / L, (tip[1] - butt[1]) / L
    m = lerp(butt, tip, 0.6)
    ctrl = (m[0] - uy * bend * L, m[1] + ux * bend * L)
    curve = quad(butt, ctrl, tip, 30)
    k = max(2, int(len(curve) * grip))
    out = [tube(curve[:k], 0.16, cap=True), curve[k - 1:]]
    if reel:
        r = curve[max(1, k // 2)]
        out.append(circle(r[0] + uy * 0.22, r[1] - ux * 0.22, 0.17, 12))
    return out


def seated(hip, knee, foot, side=1):
    """Seated legs: thigh forward, shin hanging down (side=+1 faces right)."""
    return [limb([hip, knee], 0.5, 0.42), limb([knee, foot], 0.42, 0.32), boot(foot, (foot[0] + side * 0.4, foot[1] - 0.05))]


@design("fishing_fly_fisherman", T)
def fly_fisherman(rng):
    fig = person((0.0, 1.85), [(0.0, -0.9), (0.0, 0.4), (0.0, 1.35)], tw=1.1,
                 arms=[[(0.42, 1.2), (0.95, 1.45), (0.95, 2.2)], [(-0.42, 1.2), (-0.75, 0.55), (-0.3, 0.2)]])
    hat = bucket_hat(0.0, 1.97, 0.4)
    bib = [rect(-0.35, 0.3, 0.35, 0.95), [(-0.3, 0.95), (-0.42, 1.3)], [(0.3, 0.95), (0.42, 1.3)]]
    rd = rod((0.95, 1.95), (0.1, 4.6), 0.08)
    line = [chain(cubic((0.1, 4.6), (-1.2, 5.3), (-3.2, 4.6), (-2.5, 3.8), 24), cubic((-2.5, 3.8), (-1.5, 3.2), (1.5, 4.3), (3.3, 3.6), 30)),
            [(-0.3, 0.2), (0.3, 1.0)]]
    water = clip_box([wave(-3.6, 3.6, -0.9, 0.08, 6, 100), wave(-3.6, 3.6, -1.7, 0.08, 5, 100), wave(-3.6, 3.6, -2.5, 0.08, 6, 100)], -0.8, -1.05, 0.8, -0.75)
    bank = [[(-3.6, 0.9), (-1.3, 0.9)], [(1.3, 0.9), (3.6, 0.9)]] + pine(-2.6, 0.9, 1.8, 0.55) + pine(-1.8, 0.9, 1.3, 0.4) + pine(2.6, 0.9, 1.6, 0.5)
    fig = clip_box(fig, -1.0, -1.5, 1.0, -0.9)
    return make("Fly Fisherman Casting", fig + hat + bib + rd + line + water + [ellipse(0, -0.9, 0.9, 0.2, 40)[20:62]] + bank)


@design("fishing_dock_cast", T)
def dock_cast(rng):
    fig = person((-1.6, 1.95), [(-1.75, -0.2), (-1.7, 0.6), (-1.6, 1.45)],
                 arms=[[(-1.25, 1.3), (-0.6, 1.5), (-0.2, 2.0)], [(-1.95, 1.3), (-1.6, 0.8), (-0.9, 1.0)]],
                 legs=[[(-1.55, -0.2), (-1.3, -1.1), (-1.25, -2.0), (-0.8, -2.1)], [(-1.95, -0.2), (-2.35, -1.1), (-2.6, -1.95), (-2.2, -2.15)]])
    cap = [chain(arc(-1.6, 2.0, 0.42, 0.1, math.pi - 0.1, 14)), [(-1.2, 2.05), (-0.75, 1.95)]]
    rd = rod((-0.95, 1.4), (1.6, 3.6), -0.03)
    line = [quad((1.6, 3.6), (3.0, 3.4), (3.2, -1.95), 20)]
    bob = [circle(3.2, -1.75, 0.22, 14), [(3.0, -1.75), (3.4, -1.75)]]
    deck = [rect(-3.6, -2.45, 0.4, -2.15)] + [[(x, -2.45), (x, -3.4)] for x in (-3.2, -1.6, 0.0)] + [[(x + 0.25, -2.45), (x + 0.25, -3.4)] for x in (-3.2, -1.6, 0.0)]
    water = clip_box([wave(-3.6, 3.6, -2.9, 0.08, 7, 120)], -3.25, -3.0, 0.3, -2.4) + ripples(3.2, -1.95, (0.45, 0.8))
    return make("Angler Casting from the Dock", fig + cap + rd + line + bob + deck + water)


@design("fishing_rowboat_angler", T)
def rowboat_angler(rng):
    hull = [chain(quad((-3.3, -0.2), (-2.8, -1.5), (-1.0, -1.5), 12), [(1.5, -1.5)], quad((1.5, -1.5), (2.9, -1.4), (3.4, 0.0), 12)),
            [(-3.3, -0.2), (3.4, 0.0)], quad((-3.1, -0.55), (0.0, -0.45), (3.2, -0.35), 20)]
    fig = person((0.1, 1.7), [(-0.1, -0.1), (0.0, 0.6), (0.05, 1.2)],
                 arms=[[(0.4, 1.05), (0.95, 0.75), (1.35, 1.05)], [(-0.25, 1.05), (0.4, 0.6), (1.2, 0.85)]])
    hat = bucket_hat(0.1, 1.82, 0.4)
    knees = [limb([(0.1, -0.05), (1.0, 0.1)], 0.5, 0.42)]
    rd = rod((0.8, 0.6), (2.8, 3.0), -0.18)
    line = [quad((2.8, 3.0), (3.2, 1.5), (3.6, -0.65), 12)]
    fish = splash(3.6, -0.65, 0.7, 0.6)
    oar = [tube([(-1.6, 0.4), (-3.4, -1.4)], 0.14, cap=True), transform(lens((-0.6, 0), (0.6, 0), 0.25, 12), -3.6, -1.6, 1, 0.78)]
    water = clip_box([wave(-3.8, 4.2, -1.1, 0.1, 7, 140), wave(-3.8, 4.2, -1.9, 0.1, 6, 140)], -3.0, -1.6, 2.9, -0.6)
    return make("Fisherman in a Rowboat", hull + clip_box(fig, -3.4, -2.0, 3.4, -0.1) + hat + knees + rd + line + fish + oar + water)


@design("fishing_first_catch", T)
def first_catch(rng):
    fig = person((0.0, 1.35), [(0.0, -0.6), (0.0, 0.2), (0.0, 0.85)], hr=0.48, tw=0.95, aw=0.3, lw=0.45,
                 arms=[[(0.4, 0.7), (1.05, 1.0), (1.4, 1.65)], [(-0.4, 0.7), (-0.95, 0.3), (-1.3, 0.75)]],
                 legs=[[(0.22, -0.6), (0.35, -1.7), (0.4, -2.7), (0.85, -2.8)], [(-0.22, -0.6), (-0.35, -1.7), (-0.4, -2.7), (-0.85, -2.8)]])
    cap = [chain(arc(0.0, 1.45, 0.5, 0.15, math.pi - 0.15, 16)), [(-0.48, 1.55), (-1.0, 1.45)], [(-0.45, 1.6), (0.45, 1.6)]]
    face = [arc(0.0, 1.3, 0.25, math.radians(200), math.radians(340), 10)]
    hints = [circle(-0.15, 1.45, 0.05, 8), circle(0.15, 1.45, 0.05, 8)]
    rd = rod((-1.3, 0.75), (-3.0, 3.2), 0.05, reel=True)
    line = [[(1.4, 1.85), (1.42, 1.2)]]
    f = simple_fish(1.9, 0.5, 0.55)
    fish, h2 = f.done(1.42, 0.22, 1.0, math.pi / 2)
    shorts = [[(-0.5, -0.6), (0.5, -0.6)], [(0.0, -0.6), (0.0, -1.1)]]
    sparkle = [[(2.2, 1.0), (2.6, 1.2)], [(2.25, 0.4), (2.7, 0.4)], [(2.2, -0.2), (2.6, -0.4)]]
    return make("Kid's First Catch", fig + cap + face + rd + line + fish + shorts + sparkle, hints + h2)


@design("fishing_grandpa", T)
def grandpa(rng):
    gp = person((-1.4, 1.9), [(-1.6, 0.05), (-1.55, 0.75), (-1.45, 1.4)], tw=1.15,
                arms=[[(-1.0, 1.25), (-0.5, 0.7), (0.1, 0.65)]]) + seated((-1.4, 0.05), (-0.3, 0.1), (-0.25, -1.1))
    gp += bucket_hat(-1.4, 2.02, 0.4) + [quad((-1.65, 1.6), (-1.4, 1.2), (-1.15, 1.6), 8)]
    kid = person((1.0, 1.15), [(0.9, 0.05), (0.92, 0.5), (0.95, 0.8)], hr=0.36, tw=0.8, aw=0.26,
                 arms=[[(1.25, 0.7), (1.7, 0.4), (2.15, 0.6)]]) + seated((1.0, 0.05), (1.85, 0.1), (1.9, -0.85))
    kid += [chain(arc(1.0, 1.2, 0.37, 0.1, math.pi - 0.1, 12)), [(1.35, 1.25), (1.7, 1.15)]]
    rods = rod((0.1, 0.65), (2.0, 2.9), 0.04, reel=False) + rod((2.15, 0.6), (3.6, 2.2), 0.04, reel=False)
    lines = [quad((2.0, 2.9), (2.6, 1.0), (2.75, -1.85), 16), quad((3.6, 2.2), (3.7, 0.5), (3.65, -1.85), 16)]
    bobs = [circle(2.75, -1.75, 0.16, 12), circle(3.65, -1.75, 0.16, 12)]
    dock = [rect(-3.2, -0.25, 2.3, 0.05), [(-3.2, -0.1), (2.3, -0.1)]] + [[(x, -0.25), (x, -2.2)] for x in (-2.8, -1.2, 0.6, 2.0)]
    water = clip_box([wave(-3.4, 4.2, -1.9, 0.08, 7, 120)], -100, -2.1, 2.3, -0.25) + ripples(2.75, -1.95, (0.35,)) + ripples(3.65, -1.95, (0.35,))
    return make("Fishing with Grandpa", gp + kid + rods + lines + bobs + dock + water)


@design("fishing_ice_auger", T)
def ice_auger(rng):
    fig = person((-0.9, 1.95), [(-1.0, -0.3), (-0.95, 0.6), (-0.9, 1.4)], tw=1.5, aw=0.42, lw=0.6,
                 arms=[[(-0.4, 1.2), (0.2, 0.95), (0.55, 1.25)], [(-1.4, 1.2), (-0.7, 0.5), (0.25, 0.55)]],
                 legs=[[(-0.7, -0.3), (-0.5, -1.4), (-0.45, -2.4), (0.05, -2.5)], [(-1.25, -0.3), (-1.55, -1.4), (-1.7, -2.35), (-1.25, -2.55)]])
    hood = [arc(-0.9, 1.95, 0.6, -0.5, math.pi + 0.5, 24), circle(-0.9, 2.62, 0.22, 14)]
    auger = [[(0.35, 1.25), (1.3, 1.25)], [(0.8, 1.25), (0.8, 0.55)], rect(0.68, -2.0, 0.92, 0.55)]
    for k in range(6):
        y = -0.1 - 0.32 * k
        auger.append([(0.55, y), (1.05, y - 0.18)])
    auger = [rrect(0.25, 1.1, 1.35, 1.4, 0.12), rect(0.7, -0.1, 0.9, 1.1)]
    for k in range(5):
        y = -0.15 - 0.35 * k
        auger.append(poly((0.8, y), (1.25, y - 0.12), (0.8, y - 0.25), (0.35, y - 0.12)))
    hole = [ellipse(0.8, -2.15, 0.55, 0.16, 24)]
    ice = [[(-3.2, -2.55), (3.4, -2.55)], [(-2.6, -2.95), (-1.5, -2.75)], [(1.6, -2.85), (2.6, -2.95)]]
    pines = pine(2.9, -2.55, 2.6, 0.6) + pine(-2.8, -2.55, 2.4, 0.55)
    return make("Ice Angler with an Auger", clip_all(fig, [(0.8, 1.25, 0.0)]) + hood + auger + hole + ice + pines)


@design("fishing_surf_cast", T)
def surf_cast(rng):
    fig = person((-1.3, 1.6), [(-1.45, -0.4), (-1.4, 0.4), (-1.3, 1.1)],
                 arms=[[(-0.9, 0.95), (-0.5, 1.65), (-0.6, 2.4)], [(-1.65, 0.95), (-1.6, 1.7), (-1.2, 2.25)]],
                 legs=[[(-1.25, -0.4), (-0.9, -1.4), (-0.85, -2.3), (-0.4, -2.45)], [(-1.65, -0.4), (-2.05, -1.3), (-2.45, -2.2), (-2.1, -2.4)]])
    cap = [chain(arc(-1.3, 1.65, 0.42, 0.1, math.pi - 0.1, 14)), [(-0.9, 1.7), (-0.45, 1.6)]]
    rd = rod((-1.2, 1.9), (1.3, 4.3), -0.1)
    line = [quad((1.3, 4.3), (2.8, 4.6), (3.6, 1.0), 20)]
    waves = [chain(wave(0.2, 3.8, -0.4, 0.15, 3, 50)), quad((0.6, -0.8), (1.4, -0.3), (2.0, -0.9), 10), quad((2.2, -0.8), (2.9, -0.3), (3.5, -0.9), 10),
             wave(-0.6, 3.8, -1.3, 0.1, 4, 50)]
    sand = [smooth([(-3.4, -2.6), (-1.0, -2.45), (1.0, -1.7), (3.8, -1.55)], 8)]
    bucket = [poly((-3.0, -2.55), (-2.9, -1.7), (-2.1, -1.7), (-2.0, -2.55), closed=False), ellipse(-2.5, -1.7, 0.4, 0.1, 18),
              arc(-2.5, -1.7, 0.4, 0.2, math.pi - 0.2, 10)]
    return make("Surf Casting at the Shore", fig + cap + rd + line + waves + sand + bucket)


@design("fishing_kayak", T)
def kayak(rng):
    hull = [chain(quad((-3.6, 0.1), (-2.0, -0.8), (0.0, -0.8), 16), quad((0.0, -0.8), (2.2, -0.8), (3.6, 0.15), 16)),
            [(-3.6, 0.1), (3.6, 0.15)], quad((-3.3, -0.15), (0.0, -0.4), (3.3, -0.1), 20)]
    fig = person((-0.4, 1.95), [(-0.5, 0.1), (-0.45, 0.8), (-0.4, 1.45)],
                 arms=[[(0.0, 1.3), (0.6, 1.0), (1.05, 1.25)], [(-0.75, 1.3), (-0.1, 0.8), (0.8, 0.95)]])
    vest_ = [[(-0.85, 0.35), (-0.05, 0.35)], [(-0.45, 0.35), (-0.45, 1.35)]]
    cap = [chain(arc(-0.4, 2.0, 0.42, 0.1, math.pi - 0.1, 14)), [(0.0, 2.05), (0.45, 1.95)]]
    legs = [limb([(-0.4, 0.15), (0.6, 0.35), (1.4, 0.15)], 0.45, 0.35)]
    rd = rod((0.6, 0.8), (2.9, 2.6), -0.2)
    line = [quad((2.9, 2.6), (3.6, 1.2), (3.9, -0.8), 12)]
    fish = splash(3.9, -0.8, 0.7, 0.6)
    holders = [[(-1.5, 0.1), (-2.1, 1.6)], [(-1.75, 0.1), (-2.8, 1.3)], [(-2.1, 1.6), (-2.6, 3.2)], [(-2.8, 1.3), (-3.6, 2.6)]]
    water = clip_box([wave(-3.9, 4.4, -0.6, 0.1, 8, 150), wave(-3.9, 4.4, -1.4, 0.1, 7, 150)], -3.5, -0.85, 3.5, 0.2)
    return make("Kayak Angler Hooked Up", hull + clip_box(fig, -3.0, -1.0, 3.0, 0.12) + vest_ + cap + legs + rd + line + fish + holders + water)


# ---------------------------------------------------------------- lakeside scenes

def sun_rays(cx, cy, r, n=9, a0=0.15, a1=math.pi - 0.15, L=0.5):
    out = [arc(cx, cy, r, 0, math.pi, 40)]
    for k in range(n):
        a = a0 + (a1 - a0) * k / (n - 1)
        out.append([(cx + (r + 0.2) * math.cos(a), cy + (r + 0.2) * math.sin(a)), (cx + (r + 0.2 + L) * math.cos(a), cy + (r + 0.2 + L) * math.sin(a))])
    return out


@design("fishing_bank_chair", T)
def bank_chair(rng):
    sun = sun_rays(1.6, 0.2, 1.0, 9)
    bank = [smooth([(-3.6, -1.95), (-1.0, -2.0), (0.4, -2.3), (1.2, -3.0)], 8)]
    chair = [quad((-2.75, -0.75), (-2.0, -1.0), (-1.25, -0.75), 10), [(-2.75, -0.75), (-2.6, -1.9)], [(-1.25, -0.75), (-1.4, -1.9)],
             [(-2.6, -1.9), (-1.25, -0.75)], [(-1.4, -1.9), (-2.75, -0.75)], [(-2.75, -0.75), (-3.0, 0.9)], [(-1.25, -0.75), (-1.5, 0.9)],
             quad((-3.0, 0.9), (-2.25, 0.6), (-1.5, 0.9), 10), quad((-2.9, 0.25), (-2.2, 0.0), (-1.4, 0.25), 10)]
    stick = [[(-0.6, -1.5), (-0.5, -0.4)], [(-0.5, -0.4), (-0.75, -0.05)], [(-0.5, -0.4), (-0.25, -0.05)]]
    rd = rod((-1.3, -0.65), (1.0, 1.9), -0.05, reel=True)
    line = [quad((1.0, 1.9), (2.0, 0.6), (2.6, -0.7), 14)]
    bob = [circle(2.6, -0.6, 0.17, 12)] + ripples(2.6, -0.75, (0.4, 0.75))
    water = [wave(1.1, 3.6, -1.6, 0.06, 2, 40), wave(1.6, 3.6, -2.3, 0.06, 2, 40)]
    thermos = [rrect(-3.65, -1.95, -3.15, -0.95, 0.12), rect(-3.55, -0.95, -3.25, -0.7)]
    horizon = [[(-0.7, 0.2), (0.4, 0.2)], [(2.8, 0.2), (3.6, 0.2)]]
    return make("Bank Fishing Chair at Sunset", sun + horizon + bank + chair + stick + rd + line + bob + water + thermos)


@design("fishing_pier_sunrise", T)
def pier_sunrise(rng):
    sun = sun_rays(0.7, 0.0, 1.0, 9)
    sea = [[(-3.6, 0.0), (-0.5, 0.0)], [(1.9, 0.0), (3.6, 0.0)], wave(-3.6, 3.6, -0.6, 0.06, 6, 100), wave(-3.6, 3.6, -1.9, 0.08, 5, 100)]
    deck = [[(-3.6, -1.0), (3.6, -1.0)], [(-3.6, -1.25), (3.6, -1.25)]]
    rail = [[(-3.6, -0.3), (3.6, -0.3)]] + [[(x, -1.0), (x, -0.3)] for x in (-3.0, -1.0, 1.0, 3.0)]
    posts = [[(x, -1.25), (x, -2.9)] for x in (-3.0, -1.0, 1.0, 3.0)] + [[(x + 0.25, -1.25), (x + 0.25, -2.9)] for x in (-3.0, -1.0, 1.0, 3.0)]
    a1 = person((-2.3, 0.75), [(-2.4, -0.55), (-2.35, -0.0), (-2.3, 0.38)], hr=0.3, tw=0.7, aw=0.24, lw=0.36,
                arms=[[(-2.05, 0.25), (-1.7, 0.0), (-1.4, 0.25)]],
                legs=[[(-2.3, -0.55), (-2.25, -0.95), (-2.25, -1.0)], [(-2.5, -0.55), (-2.55, -0.95), (-2.55, -1.0)]], feet=False)
    a1 += bucket_hat(-2.3, 0.84, 0.3)
    r1 = rod((-1.4, 0.25), (-0.9, 2.5), -0.08, reel=False)
    l1 = [quad((-0.9, 2.5), (-0.5, 0.5), (-0.6, -1.9), 14)]
    a2 = person((2.5, 0.75), [(2.5, -0.55), (2.5, 0.0), (2.5, 0.38)], hr=0.3, tw=0.7, aw=0.24, lw=0.36,
                arms=[[(2.75, 0.25), (3.05, 0.05), (3.3, 0.3)]],
                legs=[[(2.4, -0.55), (2.4, -0.95), (2.4, -1.0)], [(2.6, -0.55), (2.6, -0.95), (2.6, -1.0)]], feet=False)
    a2 += [chain(arc(2.5, 0.78, 0.31, 0.1, math.pi - 0.1, 10)), [(2.8, 0.8), (3.1, 0.75)]]
    r2 = rod((3.3, 0.3), (3.7, 2.4), 0.03, reel=False)
    l2 = [quad((3.7, 2.4), (3.9, 0.0), (3.8, -1.9), 12)]
    gulls = [chain(arc(-2.0 + dx, 2.4 + dy, 0.3, 0.3, math.pi - 0.3, 8), arc(-1.45 + dx, 2.4 + dy, 0.3, 0.3, math.pi - 0.3, 8)) for dx, dy in ((0.4, 0.3), (2.3, 0.9))]
    back = clip_box(clip_box(sun + sea + rail, -2.75, -1.0, -1.85, 1.2), 2.05, -1.0, 2.95, 1.2)
    return make("Fishing Pier at Sunrise", back + deck + posts + a1 + r1 + l1 + a2 + r2 + l2 + gulls)


@design("fishing_lake_cabin", T)
def lake_cabin(rng):
    cabin = [rect(-3.4, -0.4, -1.0, 1.1), poly((-3.7, 1.0), (-2.2, 2.3), (-0.7, 1.0), closed=False), [(-3.7, 1.0), (-0.7, 1.0)]]
    logs = [[(-3.4, y), (-1.0, y)] for y in (-0.05, 0.3, 0.65)]
    door = [rect(-1.9, -0.4, -1.3, 0.65)]
    win = [rect(-3.05, 0.0, -2.35, 0.6), [(-2.7, 0.0), (-2.7, 0.6)]]
    logs = clip_box(logs, -3.06, -0.01, -2.34, 0.61)
    logs = clip_box(logs, -1.91, -0.41, -1.29, 0.66)
    chimney = [poly((-1.4, 1.6), (-1.4, 2.3), (-1.0, 2.3), (-1.0, 1.25), closed=False)]
    smoke = [circle(-1.1, 2.65, 0.15, 10), circle(-0.85, 3.0, 0.2, 12)]
    dock = [poly((-0.6, -0.55), (2.6, -0.55), (2.6, -0.8), (-0.6, -0.8)), [(0.4, -0.8), (0.4, -1.4)], [(1.5, -0.8), (1.5, -1.4)], [(2.5, -0.8), (2.5, -1.4)]]
    boat = [chain(quad((0.6, -1.6), (0.9, -2.15), (1.6, -2.15), 8), [(2.6, -2.15)], quad((2.6, -2.15), (3.2, -2.1), (3.5, -1.55), 8)), [(0.6, -1.6), (3.5, -1.55)],
            quad((1.3, -1.0), (1.0, -1.3), (0.75, -1.6), 6)]
    rd = rod((2.2, -0.55), (2.9, 1.6), 0.0, reel=True)
    water = [wave(-0.4, 3.6, -1.15, 0.05, 4, 60), wave(-3.6, 0.4, -1.6, 0.05, 3, 50), wave(-3.6, 3.6, -2.6, 0.05, 6, 100)]
    water = clip_box(water, 0.55, -2.2, 3.55, -1.5)
    trees = pine(0.2, -0.45, 2.2, 0.55) + pine(1.0, -0.5, 1.6, 0.45) + pine(3.2, -0.5, 2.4, 0.55)
    return make("Lakeside Cabin and Dock", cabin + logs + door + win + chimney + smoke + dock + boat + rd + water + clip_box(trees, -0.7, -0.81, 2.65, -0.54))


@design("fishing_mountain_lake", T)
def mountain_lake(rng):
    mts = [poly((-3.6, 0.3), (-2.0, 2.6), (-1.0, 1.4), (0.4, 3.1), (1.9, 1.2), (2.7, 2.0), (3.6, 0.9), closed=False)]
    snow = [poly((-2.45, 1.95), (-2.0, 2.6), (-1.55, 2.0), (-1.85, 2.1), (-2.1, 1.85), closed=False),
            poly((-0.15, 2.3), (0.4, 3.1), (0.95, 2.35), (0.6, 2.45), (0.35, 2.2), (0.05, 2.45), closed=False)]
    sun_ = [circle(2.6, 3.0, 0.45, 30)]
    shore = [[(-3.6, 0.3), (3.6, 0.3)]]
    trees = pine(-3.0, 0.3, 1.5, 0.4) + pine(-2.4, 0.3, 1.1, 0.32) + pine(2.6, 0.3, 1.3, 0.38) + pine(3.2, 0.3, 1.7, 0.42)
    f = Fish([(1.3, 0.05), (1.1, 0.3), (0.6, 0.5), (0.0, 0.55), (-0.6, 0.45), (-1.1, 0.2), (-1.3, 0.15)],
             [(1.3, -0.08), (1.05, -0.3), (0.5, -0.45), (-0.1, -0.45), (-0.7, -0.33), (-1.1, -0.17), (-1.3, -0.15)])
    f.tail("square", 0.6, 0.55, 2).fin(0.3, -0.25, 0.4, "top", "soft", 0.15).pectoral(0.6, -0.15, 0.45, -2.7).gill(0.75, 0.12).eye(1.0, 0.12, 0.1, 0.05)
    f.add(*spots(f, [(0.3, 0.25), (-0.15, 0.3), (-0.6, 0.15), (0.1, -0.05)], 0.08))
    fish, hints = f.done(-0.1, -0.35, 1.0, 0.6)
    water = splash(-0.85, -1.15, 0.9, 0.5) + ripples(-0.85, -1.25, (1.5, 2.1), 0.22)
    lines = [[(-3.6, -2.6), (-2.6, -2.6)], [(1.5, -2.6), (3.6, -2.6)], [(2.0, -0.4), (3.2, -0.4)], [(-3.4, -0.3), (-2.5, -0.3)]]
    return make("Trout Rising on a Mountain Lake", mts + snow + sun_ + shore + trees + fish + water + lines, hints)


@design("fishing_bass_boat", T)
def bass_boat(rng):
    hull = [chain([(-3.0, 0.3)], [(-3.0, -0.5)], quad((-3.0, -0.5), (-1.0, -0.85), (1.5, -0.7), 12), quad((1.5, -0.7), (3.0, -0.4), (3.8, 0.35), 12)),
            [(-3.0, 0.3), (3.8, 0.35)], [(-2.9, -0.1), (3.2, -0.05)]]
    stripe = [quad((-2.9, -0.3), (0.5, -0.55), (3.4, 0.0), 20)]
    motor = [smooth([(-3.0, 0.4), (-3.1, 1.3), (-3.6, 1.4), (-3.9, 0.9), (-3.7, 0.4)], 6), [(-3.3, 0.35), (-3.35, -1.1)], [(-3.55, 0.35), (-3.55, -1.1)],
             poly((-3.65, -1.1), (-3.2, -1.1), (-3.2, -1.3), (-3.7, -1.3), closed=False), [(-3.0, 0.4), (-3.7, 0.4)]]
    console = [poly((-0.6, 0.3), (-0.6, 1.0), (0.4, 1.0), (0.7, 0.3), closed=False), poly((-0.1, 1.0), (0.15, 1.5), (0.4, 1.0), closed=False)]
    seats = [rrect(-2.3, 0.85, -1.6, 1.45, 0.15), [(-1.95, 0.85), (-1.95, 0.3)], rrect(1.6, 0.85, 2.3, 1.45, 0.15), [(1.95, 0.85), (1.95, 0.3)]]
    trolling = [[(3.3, 0.4), (3.5, 1.0)], [(3.5, 1.0), (3.9, -0.9)], rrect(3.65, -1.25, 4.2, -0.95, 0.12)]
    rods_ = [[(-1.3, 0.3), (0.6, 2.6)], [(-1.0, 0.3), (1.6, 2.2)], [(0.9, 0.3), (2.8, 2.5)]]
    water = clip_box([wave(-4.2, 4.4, -0.75, 0.1, 9, 150), wave(-4.2, 4.4, -1.6, 0.1, 8, 150)], -3.75, -1.35, 3.6, 0.4)
    return make("Bass Boat on the Lake", hull + stripe + motor + console + seats + trolling + rods_ + water)


# ---------------------------------------------------------------- wildlife anglers

@design("fishing_grizzly_salmon", T)
def grizzly_salmon(rng):
    outline = smooth([(-2.6, -1.0), (-2.7, 0.3), (-2.8, 1.0), (-2.4, 1.8), (-1.2, 2.1), (0.2, 2.6), (0.9, 2.45), (1.4, 2.0), (1.9, 2.25),
                      (2.5, 2.2), (2.9, 1.9), (3.6, 1.65), (3.8, 1.4), (3.6, 1.2), (3.1, 1.1), (3.3, 0.85), (2.7, 0.65), (1.9, 0.75), (1.5, 0.4),
                      (1.4, -1.0)], 8)
    under = smooth([(0.65, -1.0), (0.6, 0.15), (-0.4, 0.25), (-1.4, 0.2), (-1.7, 0.0), (-1.75, -1.0)], 8)
    body, head = outline, under
    ears = [arc(1.95, 2.3, 0.28, 0.3, math.pi + 0.3, 10), arc(2.5, 2.3, 0.26, -0.1, math.pi - 0.3, 10)]
    nose = [ellipse(3.72, 1.42, 0.13, 0.11, 12)]
    hump = [arc(0.0, 1.4, 1.0, 1.2, 2.2, 10), arc(-1.6, 0.9, 0.9, 1.4, 2.4, 10), [(2.0, 0.95), (1.85, 1.6)]]
    legs = [[(0.0, 0.2), (0.05, -1.0)], [(-2.1, 0.2), (-2.15, -1.0)]]
    f = simple_fish(2.3, 0.55, 0.7)
    fish, fh = f.done(3.2, 0.9, 1.0, 1.35)
    holes = [(3.2 + t * math.cos(1.35), 0.9 + t * math.sin(1.35), 0.48) for t in (-0.9, -0.5, -0.1, 0.3, 0.7, 1.0)]
    bear = clip_all([body, head] + ears + nose + hump, holes) + clip_box(legs, -10, -10, 10, -0.95)
    water = [wave(-3.6, 3.8, -0.95, 0.1, 7, 120), wave(-3.6, 3.8, -1.8, 0.1, 6, 120), wave(-3.6, 3.8, -2.6, 0.1, 7, 120)]
    leap = simple_fish(1.8, 0.45, 0.5)
    lp, lh = leap.done(-3.0, 2.6, 1.0, 0.7)
    return make("Grizzly Bear Catching Salmon", bear + fish + water, fh + [circle(2.6, 1.8, 0.09, 8)])


# dropped: the Birds book has a heron
def heron(rng):
    body = smooth([(0.5, 0.9), (0.2, 0.2), (-0.6, -0.35), (-1.6, -0.6), (-2.3, -0.9), (-1.6, -0.3), (-1.3, 0.3), (-0.6, 0.85), (0.1, 1.05)], 8, True)
    wing = [smooth([(0.2, 0.75), (-0.5, 0.45), (-1.3, -0.05), (-2.0, -0.55)], 8)]
    neck = tube(smooth([(0.25, 0.85), (0.7, 1.5), (0.35, 2.1), (0.75, 2.55)], 8), 0.3, cap=False)
    head = [ellipse(0.95, 2.62, 0.32, 0.22, 24)]
    bill = [poly((1.2, 2.7), (2.5, 2.55), (1.2, 2.5))]
    plume = [quad((0.7, 2.75), (0.3, 2.95), (-0.1, 2.75), 8)]
    legs = [[(-0.35, -0.3), (-0.35, -1.0), (-0.45, -2.3)], [(-0.2, -0.3), (-0.2, -1.0), (-0.3, -2.3)],
            [(-0.05, -0.25), (0.15, -1.0), (0.25, -2.3)], [(0.1, -0.2), (0.3, -1.0), (0.4, -2.3)]]
    legs = clip_box(legs, -10, -10, 10, -1.9)
    f = simple_fish(1.3, 0.35, 0.4)
    fish, fh = f.done(1.95, 2.6, 1.0, 1.35)
    water = [wave(-3.4, 3.4, -1.9, 0.08, 6, 100), ellipse(-0.1, -1.95, 0.9, 0.2, 40), wave(-3.4, 3.4, -2.7, 0.08, 6, 100)]
    water = clip_box(water[:1], -0.55, -2.1, 0.5, -1.7) + [ellipse(-0.05, -1.95, 1.0, 0.2, 40), wave(-3.4, 3.4, -2.7, 0.08, 6, 100)]
    reeds_ = []
    for x, h in ((-3.2, 3.0), (-2.9, 2.2), (2.8, 2.6), (3.15, 3.2)):
        reeds_ += [quad((x, -1.95), (x + 0.1, -1.95 + h / 2), (x + 0.05, -1.95 + h), 10), rrect(x - 0.08, -1.95 + h * 0.6, x + 0.18, -1.95 + h * 0.9, 0.12)]
    hints = fh + [circle(1.0, 2.66, 0.06, 8)]
    return make("Great Blue Heron with a Fish", [body] + wing + [neck] + head + bill + plume + clip_box(legs, -10, -10, 10, -1.9) + fish + water + reeds_, hints)


@design("fishing_osprey", T)
def osprey(rng):
    wing = smooth([(-0.4, 0.75), (-1.2, 1.7), (-2.3, 2.6), (-3.3, 3.0), (-3.0, 2.6), (-3.4, 2.4), (-3.0, 2.1), (-3.3, 1.85), (-2.8, 1.7),
                   (-2.0, 1.1), (-1.0, 0.35), (-0.4, 0.15)], 8)
    feathers = [quad((-0.8, 0.8), (-1.8, 1.5), (-2.7, 2.0), 10), quad((-1.0, 1.25), (-1.9, 1.95), (-2.9, 2.55), 10)]
    left = [wing] + feathers
    right = [mirror_x(p) for p in left]
    body = [ellipse(0, -0.1, 0.6, 1.15, 50)]
    head = [circle(0, 1.35, 0.45, 30), poly((-0.12, 1.15), (0.0, 0.85), (0.12, 1.15), closed=False), [(-0.42, 1.45), (-0.15, 1.35)], [(0.42, 1.45), (0.15, 1.35)]]
    tail = [poly((-0.35, -1.15), (-0.55, -1.8), (0.55, -1.8), (0.35, -1.15), closed=False), [(0.0, -1.25), (0.0, -1.8)]]
    legs = [[(-0.3, -0.9), (-0.5, -1.9)], [(0.3, -0.9), (0.5, -1.9)]]
    f = simple_fish(3.0, 0.6, 0.8)
    fish, fh = f.done(0.2, -2.45, 1.0, 0.05)
    talons = [chain([(-0.5, -1.9)], arc(-0.5, -2.1, 0.22, math.pi / 2, math.pi * 1.3, 8)), chain([(-0.5, -1.9)], arc(-0.5, -2.1, 0.22, math.pi / 2, -0.3, 8)),
              chain([(0.5, -1.9)], arc(0.5, -2.1, 0.22, math.pi / 2, math.pi * 1.3, 8)), chain([(0.5, -1.9)], arc(0.5, -2.1, 0.22, math.pi / 2, -0.3, 8))]
    drops = [circle(-1.2, -3.0, 0.12, 10), circle(1.6, -3.1, 0.12, 10), circle(0.4, -3.3, 0.1, 10)]
    water = [wave(-3.4, 3.4, -3.6, 0.1, 6, 100)]
    hints = fh + [circle(-0.18, 1.45, 0.07, 8), circle(0.18, 1.45, 0.07, 8)]
    return make("Osprey Snatching a Fish", left + right + body + head + tail + legs + clip_all(fish, [(-0.5, -2.1, 0.0)]) + talons + drops + water, hints)


@design("fishing_campfire_roast", T)
def campfire_roast(rng):
    stones = [ellipse(x, -2.3 + 0.08 * abs(x), 0.45, 0.3, 20) for x in (-1.9, -1.0, 0.0, 1.0, 1.9)]
    logs = clip_all([transform(rrect(-1.5, -0.18, 1.5, 0.18, 0.18), 0, -1.75, 1, 0.3), transform(rrect(-1.5, -0.18, 1.5, 0.18, 0.18), 0, -1.75, 1, -0.3)],
                    [(0, -1.75, 0.0)])
    flames = [smooth([(-1.1, -1.55), (-1.15, -0.8), (-0.75, -0.1), (-0.6, -0.7), (-0.15, 0.25), (0.15, -0.5), (0.6, 0.0), (0.75, -0.8), (1.1, -1.55)], 8),
              smooth([(-0.55, -1.55), (-0.5, -1.0), (-0.15, -0.55), (0.05, -0.95), (0.35, -0.7), (0.5, -1.55)], 6)]
    forks = []
    for x in (-2.6, 2.6):
        forks += [[(x, -2.6), (x, 0.4)], [(x, 0.4), (x - 0.35, 0.95)], [(x, 0.4), (x + 0.35, 0.95)]]
    spit = [[(-3.2, 0.6), (3.2, 0.6)]]
    fishes, hints, holes = [], [], []
    for cx, flip in ((-1.15, False), (1.15, True)):
        f = simple_fish(2.0, 0.55, 0.6)
        p, h = f.done(cx, 0.6, 1.0, math.pi if flip else 0.0)
        fishes += p
        hints += h
        holes += [(cx + t, 0.6, 0.45) for t in (-0.7, -0.35, 0.0, 0.35, 0.7)]
    sparks = [circle(-0.3, 1.8, 0.1, 8), circle(0.35, 2.2, 0.1, 8), circle(-0.05, 2.6, 0.08, 8)]
    ground_ = [[(-3.4, -2.6), (3.4, -2.6)]]
    return make("Campfire Fish Roast", stones + logs + clip_all(flames + spit, holes) + forks + fishes + sparks + ground_, hints)


@design("fishing_catch_release", T)
def catch_release(rng):
    f = Fish([(2.6, 0.05), (2.3, 0.45), (1.5, 0.8), (0.3, 0.95), (-1.0, 0.8), (-2.0, 0.45), (-2.6, 0.3)],
             [(2.6, -0.12), (2.2, -0.5), (1.2, -0.8), (0.0, -0.85), (-1.2, -0.65), (-2.0, -0.4), (-2.6, -0.3)])
    f.tail("square", 1.0, 0.95, 2).fin(0.65, -0.35, 0.7, "top", "soft", 0.25, rays=2).fin(-1.6, -1.95, 0.3, "top", "soft", 0.1)
    f.pectoral(1.4, -0.35, 0.8, -2.7).gill(1.6).eye(2.05, 0.2, 0.17, 0.09).mouth(0.55, -0.03)
    f.add(*spots(f, [(1.0, 0.45), (0.5, 0.6), (0.0, 0.5), (-0.5, 0.6), (-1.0, 0.4), (-1.5, 0.3), (0.3, 0.2), (-0.4, 0.15)], 0.1))
    fish, hints = f.done(0.0, 0.9, 1.0)
    # front hand under the belly
    palm = smooth([(1.6, -0.5), (1.1, -0.85), (-0.3, -0.85), (-0.55, -0.45)], 8)
    fingers = []
    for k in range(4):
        x = -0.35 + 0.42 * k
        fingers.append(chain([(x - 0.19, -0.35)], [(x - 0.19, 0.05)], arc(x, 0.05, 0.19, math.pi, 0, 8), [(x + 0.19, -0.35)]))
    thumb = [chain([(1.6, -0.5)], quad((2.0, -0.2), (2.0, 0.2), (1.75, 0.35), 8))]
    arm1 = [[(1.1, -0.85), (1.9, -2.9)], [(-0.3, -0.85), (0.5, -2.9)]]
    # rear hand round the tail wrist
    grip = [rrect(-2.65, -0.05, -1.75, 1.85, 0.4)] + [[(-2.65, y), (-1.85, y)] for y in (0.4, 0.85, 1.3)]
    arm2 = [[(-2.6, -0.05), (-3.2, -2.9)], [(-1.8, -0.05), (-2.2, -2.9)]]
    fish = clip_box(fish, -2.66, -0.06, -1.74, 1.86)
    fish = clip_box(fish, -0.56, -0.86, 1.25, 0.25)
    water = clip_box([wave(-3.6, 3.6, -1.9, 0.1, 6, 100), wave(-3.6, 3.6, -2.6, 0.1, 6, 100)], -3.25, -3.0, 1.95, -1.6)
    drops = [circle(2.8, -0.9, 0.12, 10), circle(3.1, -1.3, 0.1, 10), circle(-0.6, -1.4, 0.1, 10)]
    return make("Catch and Release", fish + [palm] + fingers + thumb + arm1 + grip + arm2 + water + drops, hints)


def letter(ch, x, y, h=1.0):
    L = {
        "G": [smooth([(0.6, 0.85), (0.4, 1.0), (0.12, 0.95), (0.0, 0.6), (0.0, 0.35), (0.15, 0.03), (0.45, 0.0), (0.6, 0.2)], 4) + [(0.6, 0.45), (0.33, 0.45)]],
        "O": [smooth([(0.3, 1.0), (0.6, 0.75), (0.6, 0.25), (0.3, 0.0), (0.0, 0.25), (0.0, 0.75)], 6, True)],
        "N": [[(0, 0), (0, 1), (0.6, 0), (0.6, 1)]],
        "E": [[(0.6, 1), (0, 1), (0, 0), (0.6, 0)], [(0, 0.5), (0.45, 0.5)]],
        "F": [[(0.6, 1), (0, 1), (0, 0)], [(0, 0.5), (0.45, 0.5)]],
        "I": [[(0.3, 0), (0.3, 1)], [(0.1, 1), (0.5, 1)], [(0.1, 0), (0.5, 0)]],
        "S": [smooth([(0.58, 0.85), (0.35, 1.0), (0.05, 0.9), (0.05, 0.6), (0.55, 0.42), (0.6, 0.12), (0.3, 0.0), (0.0, 0.15)], 5)],
        "H": [[(0, 0), (0, 1)], [(0.6, 0), (0.6, 1)], [(0, 0.5), (0.6, 0.5)]],
        "B": [chain([(0, 0.5), (0, 1), (0.35, 1)], quad((0.35, 1), (0.6, 0.98), (0.58, 0.75), 5), quad((0.58, 0.75), (0.56, 0.52), (0.3, 0.5), 5), [(0, 0.5)]),
              chain([(0.3, 0.5)], quad((0.3, 0.5), (0.64, 0.48), (0.62, 0.25), 5), quad((0.62, 0.25), (0.6, 0.0), (0.35, 0.0), 5), [(0, 0), (0, 0.5)])],
        "A": [[(0, 0), (0.3, 1), (0.6, 0)], [(0.12, 0.4), (0.48, 0.4)]],
        "T": [[(0, 1), (0.6, 1)], [(0.3, 1), (0.3, 0)]],
    }[ch]
    return [[(x + px * h, y + py * h) for px, py in s] for s in L]


def word(text, cx, y, h=1.0, gap=0.3):
    adv = 0.6 * h + gap * h
    x = cx - (len(text) * adv - gap * h) / 2
    out = []
    for ch in text:
        out += letter(ch, x, y, h)
        x += adv
    return out


@design("fishing_gone_fishing", T)
def gone_fishing(rng):
    plank = [rrect(-3.2, -1.3, 3.2, 1.6, 0.3), rrect(-2.95, -1.05, 2.95, 1.35, 0.2)]
    text = word("GONE", 0.0, 0.35, 0.8) + word("FISHING", 0.0, -0.75, 0.8)
    ropes = [[(-2.6, 1.6), (0.0, 3.1)], [(2.6, 1.6), (0.0, 3.1)], circle(0.0, 3.25, 0.15, 10)]
    f = simple_fish(1.6, 0.4, 0.45)
    fish, hints = f.done(2.2, -2.3, 1.0, 0.0)
    bob = [[(-2.3, -1.3), (-2.3, -1.85)], circle(-2.3, -2.15, 0.3, 18), [(-2.6, -2.15), (-2.0, -2.15)], [(-2.3, -2.45), (-2.3, -2.8)]]
    return make("Gone Fishing Sign", plank + text + ropes + [[(2.95, -1.3), (2.95, -2.3)]] + fish + bob, hints)


@design("fishing_bait_bucket", T)
def bait_bucket(rng):
    bucket = [[(-1.9, 0.6), (-1.6, -2.6)], [(1.9, 0.6), (1.6, -2.6)], ellipse(0, 0.6, 1.9, 0.4, 70),
              [(1.6 * math.cos(t), -2.6 + 0.3 * math.sin(t)) for t in [math.pi + math.pi * i / 30 for i in range(31)]]]
    bands = [[(1.85 * math.cos(t), 0.15 + 0.38 * math.sin(t)) for t in [math.pi + math.pi * i / 30 for i in range(31)]],
             [(1.66 * math.cos(t), -2.15 + 0.32 * math.sin(t)) for t in [math.pi + math.pi * i / 30 for i in range(31)]]]
    handle = [cubic((-1.9, 0.5), (-2.3, 3.0), (2.3, 3.0), (1.9, 0.5), 30)]
    label = word("BAIT", 0.0, -1.5, 0.8)
    dirt = [wave(-1.6, 1.6, 0.65, 0.07, 3, 30)]
    worms = [tube(smooth([(-0.9, 0.7), (-1.5, 1.1), (-2.2, 0.7), (-2.4, -0.2), (-2.1, -0.8)], 6), 0.24, cap=True),
             tube(smooth([(0.6, 0.75), (1.0, 1.35), (1.7, 1.0), (2.3, 0.6), (2.5, -0.3)], 6), 0.24, cap=True),
             tube(smooth([(-0.2, 0.75), (0.0, 1.4), (-0.5, 1.8), (-0.1, 2.2)], 6), 0.22, cap=True)]
    worm_bits = [tube(smooth([(-3.2, -2.75), (-2.8, -2.45), (-2.4, -2.75), (-2.0, -2.5)], 6), 0.22, cap=True)]
    return make("Bait Bucket Full of Worms", clip_all(bucket[:2] + [handle[0]], [(-1.9, 0.6, 0.0)]) + bucket[2:] + bands + handle + label + dirt + worms + worm_bits)


@design("fishing_trophy_plaque", T)
def trophy_plaque(rng):
    plaque = [smooth([(-3.2, 2.2), (0.0, 2.7), (3.2, 2.2), (3.3, 0.0), (2.6, -1.8), (0.0, -2.9), (-2.6, -1.8), (-3.3, 0.0)], 8, True),
              smooth([(-2.85, 1.9), (0.0, 2.35), (2.85, 1.9), (2.95, 0.0), (2.35, -1.55), (0.0, -2.5), (-2.35, -1.55), (-2.95, 0.0)], 8, True)]
    f = Fish([(2.05, 0.15), (1.75, 0.5), (1.1, 0.85), (0.2, 0.95), (-0.8, 0.8), (-1.6, 0.4), (-2.0, 0.27)],
             [(2.15, -0.25), (1.75, -0.55), (0.9, -0.85), (0.0, -0.9), (-0.9, -0.7), (-1.6, -0.36), (-2.0, -0.27)])
    f.add([(2.05, 0.15), (1.35, -0.06), (2.15, -0.25)])
    f.tail("square", 0.85, 0.8, 2).fin(0.85, -0.05, 0.6, "top", "spiny", 0.05, teeth=5).fin(-0.2, -1.2, 0.55, "top", "soft", 0.2)
    f.fin(-0.6, -1.3, 0.45, "bot", "soft", 0.2).pectoral(0.9, -0.2, 0.75, -2.75).gill(1.1).eye(1.55, 0.38, 0.17, 0.08)
    f.add(band_line(f, 0.9, -1.9, 0.11, 9))
    fish, hints = f.done(0.2, 0.55, 1.0, 0.12)
    plate = [rect(-1.3, -2.05, 1.3, -1.35), circle(-1.05, -1.7, 0.08, 8), circle(1.05, -1.7, 0.08, 8), [(-0.7, -1.7), (0.7, -1.7)]]
    hanger = [circle(0.0, 2.15, 0.13, 10)]
    return make("Trophy Bass on a Plaque", plaque + fish + plate + hanger, hints)


@design("fishing_hanging_scale", T)
def hanging_scale(rng):
    ring = [circle(0.0, 3.35, 0.3, 20)]
    body = [rrect(-0.75, 0.75, 0.75, 3.0, 0.35), circle(0.0, 2.0, 0.55, 36)]
    ticks = [[(0.55 * math.cos(a) * 0.75, 2.0 + 0.55 * math.sin(a) * 0.75), (0.55 * math.cos(a), 2.0 + 0.55 * math.sin(a))] for a in [math.pi * k / 6 for k in range(-1, 8)]]
    needle = [[(0.0, 2.0), (0.32, 2.3)], circle(0.0, 2.0, 0.07, 8)]
    hook_ = [[(0.0, 0.75), (0.0, 0.2)], arc(0.25, 0.2, 0.25, math.pi, 2 * math.pi + 0.6, 12)]
    f = Fish([(1.6, 0.0), (1.35, 0.4), (0.7, 0.75), (-0.2, 0.85), (-1.0, 0.65), (-1.6, 0.3), (-1.9, 0.22)],
             [(1.6, -0.2), (1.3, -0.55), (0.6, -0.8), (-0.3, -0.8), (-1.1, -0.55), (-1.6, -0.28), (-1.9, -0.22)])
    f.add([(1.6, 0.0), (1.1, -0.1), (1.6, -0.2)])
    f.tail("square", 0.8, 0.75, 2).fin(0.7, -0.2, 0.6, "top", "spiny", 0.05, teeth=5).fin(-0.3, -1.2, 0.5, "top", "soft", 0.2)
    f.fin(-0.5, -1.2, 0.4, "bot", "soft", 0.2).pectoral(0.7, -0.2, 0.6, -2.7).gill(0.9).eye(1.2, 0.3, 0.15, 0.07)
    fish, hints = f.done(0.35, -1.65, 1.0, math.pi / 2)
    sparkle = [[(1.6, 1.8), (2.1, 2.1)], [(1.7, 1.2), (2.25, 1.2)], [(-1.6, 1.8), (-2.1, 2.1)], [(-1.7, 1.2), (-2.25, 1.2)]]
    return make("Weighing the Big Catch", ring + body + ticks + needle + hook_ + fish + sparkle, hints)
