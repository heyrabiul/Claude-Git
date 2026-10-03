"""Arctic & Polar Animals niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

import numpy as np

T = "polar"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ------------------------------------------------------------ drawing helpers

def spl(pts, closed=True, res=14, tension=0.5):
    """Smooth Catmull-Rom curve through `pts`; a point given as (x, y, 0)
    is a sharp corner."""
    P = [(p[0], p[1]) for p in pts]
    sharp = [len(p) > 2 and p[2] == 0 for p in pts]
    m = len(P)

    def tan(i):
        if sharp[i]:
            return (0.0, 0.0)
        if closed:
            a, b = P[(i - 1) % m], P[(i + 1) % m]
        else:
            a, b = P[max(i - 1, 0)], P[min(i + 1, m - 1)]
        return ((b[0] - a[0]) * tension, (b[1] - a[1]) * tension)

    out = [P[0]]
    for i in range(m if closed else m - 1):
        p0, p1 = P[i], P[(i + 1) % m]
        t0, t1 = tan(i), tan((i + 1) % m)
        n = max(3, int(math.dist(p0, p1) * res))
        for k in range(1, n + 1):
            t = k / n
            h00, h10, h01, h11 = 2 * t**3 - 3 * t**2 + 1, t**3 - 2 * t**2 + t, -2 * t**3 + 3 * t**2, t**3 - t**2
            out.append((h00 * p0[0] + h10 * t0[0] + h01 * p1[0] + h11 * t1[0],
                        h00 * p0[1] + h10 * t0[1] + h01 * p1[1] + h11 * t1[1]))
    return out


def sides(center, w):
    """The two edges of a band along `center` (no end caps), as two strokes."""
    band = tube(center, w, cap=False)
    n = len(center)
    return [band[:n], band[n:][::-1]]


def _dense(pts, step=0.012):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        k = max(1, int(math.dist(a, b) / step))
        for j in range(1, k + 1):
            out.append((a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k))
    return out


def _inside(pts, poly):
    P = np.asarray(pts, float)
    Q = np.asarray(poly, float)
    x, y = P[:, 0:1], P[:, 1:2]
    x0, y0 = Q[:-1, 0][None, :], Q[:-1, 1][None, :]
    x1, y1 = Q[1:, 0][None, :], Q[1:, 1][None, :]
    cond = (y0 > y) != (y1 > y)
    with np.errstate(divide="ignore", invalid="ignore"):
        xc = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
    return (np.sum(cond & (x < xc), axis=1) % 2) == 1


def _bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def _clip(strokes, polys, keep_inside):
    out = []
    polys = [p if math.dist(p[0], p[-1]) < 1e-9 else list(p) + [p[0]] for p in polys if len(p) > 2]
    for s in strokes:
        if len(s) < 2:
            continue
        sb = _bbox(s)
        hit = [p for p in polys if not (_bbox(p)[2] < sb[0] or _bbox(p)[0] > sb[2] or _bbox(p)[3] < sb[1] or _bbox(p)[1] > sb[3])]
        if not hit:
            if not keep_inside:
                out.append(s)
            continue
        d = _dense(s)
        mask = np.zeros(len(d), bool)
        for p in hit:
            mask |= _inside(d, p)
        if keep_inside:
            mask = ~mask
        run = []
        for p, m in zip(d, mask):
            if not m:
                run.append(p)
            else:
                if len(run) > 1:
                    out.append(run)
                run = []
        if len(run) > 1:
            out.append(run)
    return [r for r in out if path_len(r) > 0.03]


def path_len(s):
    return sum(math.dist(a, b) for a, b in zip(s, s[1:]))


def hide(strokes, polys):
    """Remove the parts of `strokes` lying inside any of `polys`."""
    return _clip(strokes, polys, False)


def within(strokes, polys):
    """Keep only the parts of `strokes` inside `polys`."""
    return _clip(strokes, polys, True)


def tf(pts, dx=0.0, dy=0.0, s=1.0, rot=0.0, flip=False):
    if flip:
        pts = [(-x, y) for x, y in pts]
    return transform(pts, dx, dy, s, rot)


def ground(x0, x1, y=0.0):
    return [(x0, y), (x1, y)]


def tufts(pts, s=1.0):
    out = []
    for x, y in pts:
        out += [quad((x, y), (x + dx * 0.4 * s, y + h * 0.6 * s), (x + dx * s, y + h * s), 8)
                for dx, h in [(-0.22, 0.32), (0.0, 0.42), (0.22, 0.32)]]
    return out


def dirv(a):
    a = math.radians(a)
    return (math.sin(a), -math.cos(a))


def nrmv(a):
    a = math.radians(a)
    return (math.cos(a), math.sin(a))


def add(p, v, k=1.0):
    return (p[0] + v[0] * k, p[1] + v[1] * k)


def scene(*items):
    """Front-to-back list of placed things (dicts with strokes/sil, or plain
    stroke lists); each is hidden behind everything listed before it."""
    out, hints, sil = [], [], []
    for it in items:
        if isinstance(it, dict):
            out += hide(it["strokes"], sil)
            hints += it.get("hints", [])
            sil = sil + it.get("sil", [])
        else:
            out += hide(it, sil)
    return out, hints


def closed(pts):
    return list(pts) + [pts[0]]


def obj(strokes, sil=None, hints=()):
    """A scene item whose silhouette is `sil` (default: its closed strokes)."""
    if sil is None:
        sil = [s for s in strokes if len(s) > 3 and math.dist(s[0], s[-1]) < 1e-6]
    return {"strokes": strokes, "sil": sil, "hints": list(hints)}



def sea(y, x0=-3.4, x1=3.4, amp=0.06, waves=7):
    return wave(x0, x1, y, amp, waves, 160)


def floe(x0, x1, y, h=0.35):
    """An ice floe seen from the side (top edge at y)."""
    top = [(x0, y), (x0 + 0.3, y + 0.04), (x1 - 0.3, y + 0.03), (x1, y)]
    return poly((x0, y), (x1, y), (x1 - 0.15, y - h), (x0 + 0.2, y - h))


def bubbles(pts):
    return [circle(x, y, r, 14) for x, y, r in pts]


def flakes(pts):
    return []



# ------------------------------------------------------------ polar bears

BEAR = [(3.05, 0.45, 0), (2.85, 0.62), (2.5, 0.86), (2.25, 1.02), (2.12, 1.12), (*(2.02, 1.28), 0), (1.9, 1.12), (1.5, 1.02), (0.9, 1.18),
        (0.1, 1.24), (-0.8, 1.32), (-1.45, 1.42), (-1.88, 1.24), (*(-2.06, 1.02), 0), (-2.06, 0.7), (-1.98, 0.15), (-1.8, -0.35),
        (-1.82, -0.85), (-1.92, -1.08), (*(-1.86, -1.2), 0), (*(-1.18, -1.2), 0), (-1.22, -1.02), (-1.32, -0.55), (-1.2, -0.12),
        (-0.8, -0.22), (-0.1, -0.3), (0.5, -0.26), (0.72, -0.35), (0.7, -0.8), (0.76, -1.08), (*(0.7, -1.2), 0), (*(1.52, -1.2), 0),
        (1.45, -1.02), (1.32, -0.62), (1.38, -0.12), (1.68, 0.22), (2.05, 0.2), (2.45, 0.22), (2.78, 0.3), (2.98, 0.36)]


def bear(dx=0.0, dy=0.0, s=1.0, flip=False, far=True):
    body = spl(BEAR, res=18)
    fars = []
    if far:
        fars = [spl([(0.25, -0.2), (0.1, -0.7), (-0.05, -1.05), (*(-0.1, -1.2), 0), (*(0.55, -1.2), 0), (0.5, -1.0), (0.6, -0.6), (0.75, -0.3)], closed=False),
                spl([(-0.6, -0.15), (-0.75, -0.6), (-0.85, -1.05), (*(-0.92, -1.2), 0), (*(-0.3, -1.2), 0), (-0.32, -1.0), (-0.3, -0.6), (-0.2, -0.2)], closed=False)]
        fars = hide(fars, [body])
    det = [arc(2.95, 0.48, 0.1, -1.2, 2.2, 8), [(2.95, 0.37), (2.62, 0.36)], arc(2.0, 1.12, 0.07, 0.5, 3.0, 6)]
    claws = [[(1.52 - 0.17 * k, -1.2), (1.54 - 0.17 * k, -1.08)] for k in range(1, 4)]
    g = lambda pts: tf(pts, dx, dy, s, 0.0, flip)  # noqa: E731
    return {"strokes": [g(p) for p in [body] + fars + det + claws], "sil": [g(body)], "hints": [g(eye(2.42, 0.74, 0.06))]}


@design("polar_bear_mother_cubs", T)
def bear_mother_cubs(rng):
    mom = bear(-0.6, 0.6, 1.0)
    c1 = bear(1.0, -0.82, 0.45)
    c2 = bear(-2.3, -0.75, 0.42)
    st, hi = scene(c1, mom, c2)
    snow = [spl([(-3.4, -1.32), (-1.5, -1.25), (0.5, -1.33), (3.4, -1.25)], closed=False)]
    return make("Polar Bear Mother with Cubs", st + snow, hi)


@design("polar_bear_swimming", T)
def bear_swimming(rng):
    body = spl([(*(3.0, 0.62), 0), (2.65, 0.9), (2.2, 1.08), (2.02, 1.26), (*(1.9, 1.36), 0), (1.78, 1.2), (1.2, 1.15), (0.2, 1.2), (-1.0, 1.05),
                (-1.9, 0.75), (-2.3, 0.45), (-2.9, 0.1), (*(-3.2, -0.15), 0), (-2.7, -0.15), (-2.1, 0.1), (-1.5, 0.0), (-0.6, -0.05), (0.3, 0.0),
                (0.9, -0.15), (1.5, -0.7), (*(1.65, -1.0), 0), (*(2.05, -0.8), 0), (1.85, -0.5), (1.65, 0.1), (2.1, 0.32), (2.5, 0.36), (2.95, 0.5)], res=18)
    far_paw = spl([(0.5, 0.0), (0.4, -0.6), (*(0.3, -1.0), 0), (*(0.7, -0.95), 0), (0.85, -0.3)], closed=False)
    far_hind = spl([(-1.6, 0.0), (-2.2, -0.5), (*(-2.8, -0.75), 0), (*(-2.6, -0.4), 0), (-2.1, 0.1)], closed=False)
    det = [arc(2.95, 0.6, 0.1, -1.2, 2.2, 8), [(2.9, 0.5), (2.65, 0.45)]]
    surface = sea(2.4, -3.4, 3.4, 0.08, 6)
    bub = bubbles([(3.1, 1.2, 0.12), (3.25, 1.6, 0.09), (3.05, 1.95, 0.14), (-2.5, 1.1, 0.1), (-2.7, 1.6, 0.13)])
    rays = [[(x, 2.2), (x - 0.5, 0.9)] for x in (-1.6, -0.4, 0.8)]
    st = [body] + hide([far_paw, far_hind], [body]) + det + [surface] + bub + hide(rays, [body])
    floor = [spl([(-3.4, -1.9), (-1.6, -1.6), (0.4, -2.0), (2.0, -1.7), (3.4, -1.95)], closed=False)]
    return make("Polar Bear Swimming Underwater", st + floor, [eye(2.35, 0.82, 0.06)])


@design("polar_bear_standing", T)
def bear_standing(rng):
    body = spl([(*(1.3, 2.9), 0), (1.05, 3.12), (0.72, 3.3), (0.52, 3.42), (*(0.42, 3.58), 0), (0.28, 3.4), (-0.05, 3.2), (-0.55, 2.6),
                (-0.95, 1.6), (-1.25, 0.5), (-1.45, -0.5), (-1.5, -1.4), (-1.3, -2.2), (-1.38, -2.8), (*(-1.3, -3.0), 0), (*(-0.2, -3.0), 0),
                (-0.3, -2.8), (-0.5, -2.3), (-0.3, -1.6), (0.2, -0.9), (0.6, 0.0), (0.85, 0.8), (1.2, 0.55), (*(1.5, 0.35), 0), (*(1.9, 0.42), 0),
                (1.8, 0.7), (1.5, 1.1), (1.15, 1.6), (0.9, 2.05), (0.85, 2.5), (1.05, 2.7), (1.25, 2.8)], res=16)
    arm2 = spl([(0.55, 1.6), (0.95, 1.25), (1.25, 1.0), (*(1.5, 0.85), 0), (*(1.4, 1.15), 0), (1.1, 1.5)], closed=False)
    far_leg = spl([(-0.4, -1.6), (-0.55, -2.3), (*(-0.6, -3.0), 0), (*(0.4, -3.0), 0), (0.3, -2.75), (0.1, -2.2), (0.15, -1.2)], closed=False)
    arm2 = hide([arm2, far_leg], [body])[:0] + [far_leg]
    det = [arc(1.22, 2.91, 0.08, -1.2, 2.2, 8), arc(0.4, 3.4, 0.06, 0.5, 3.0, 6), [(1.25, 2.8), (1.0, 2.74)]]
    floe_ = [poly((-2.6, -2.85), (2.4, -2.85), (2.1, -3.3), (-2.3, -3.3))]
    water = [sea(-3.25, -3.4, -2.4, 0.05, 2), sea(-3.25, 2.25, 3.4, 0.05, 2)]
    return make("Polar Bear Standing Tall", [body] + hide(arm2, [body]) + det + floe_ + water, [eye(0.82, 3.1, 0.06)])


@design("polar_bear_sleeping", T)
def bear_sleeping(rng):
    body = spl([(*(2.0, -0.05), 0), (1.7, 0.35), (1.4, 0.55), (1.2, 0.85), (*(1.05, 0.98), 0), (0.95, 0.75), (0.4, 0.95), (-0.6, 1.2),
                (-1.7, 1.05), (-2.35, 0.5), (-2.45, -0.2), (-2.1, -0.65), (*(-1.5, -0.75), 0), (*(2.5, -0.75), 0), (2.55, -0.5), (2.3, -0.4),
                (2.05, -0.3)], res=18)
    paw = spl([(0.6, -0.75), (0.8, -0.35), (1.6, -0.3), (*(2.5, -0.4), 0)], closed=False)
    hind = spl([(-1.9, -0.75), (-1.6, -0.2), (-0.9, 0.0), (-0.6, -0.4), (-0.4, -0.75)], closed=False)
    det = [arc(2.0, -0.05, 0.08, -1.0, 2.0, 6), [(1.4, 0.15), (1.6, 0.13)], arc(1.0, 0.8, 0.06, 0.5, 3.0, 6)]
    zz = [poly((2.4, 1.2), (2.7, 1.2), (2.4, 0.95), (2.7, 0.95), closed=False), poly((2.8, 1.65), (3.2, 1.65), (2.8, 1.3), (3.2, 1.3), closed=False)]
    floe_ = [poly((-3.0, -0.75), (3.0, -0.75), (2.7, -1.4), (-2.6, -1.4))]
    return make("Sleeping Polar Bear", [body, paw, hind] + det + zz + floe_ + [sea(-1.25, -3.4, -2.75, 0.05, 1), sea(-1.25, 2.85, 3.4, 0.05, 1)], [])


@design("polar_bear_portrait", T)
def bear_portrait(rng):
    head = spl([(0.0, 2.0), (1.1, 1.85), (1.75, 1.2), (2.0, 0.2), (1.75, -0.8), (1.0, -1.5), (0.5, -1.9), (0.0, -2.0), (-0.5, -1.9),
                (-1.0, -1.5), (-1.75, -0.8), (-2.0, 0.2), (-1.75, 1.2), (-1.1, 1.85)], res=14)
    ears = [arc(1.35, 1.75, 0.45, -0.5, 2.6, 16), arc(-1.35, 1.75, 0.45, 0.55, 3.65, 16)]
    ears_in = [arc(1.35, 1.75, 0.22, -0.2, 2.4, 10), arc(-1.35, 1.75, 0.22, 0.75, 3.35, 10)]
    muzzle = spl([(0.0, -0.1), (0.75, -0.45), (0.95, -1.05), (0.5, -1.55), (0.0, -1.6), (-0.5, -1.55), (-0.95, -1.05), (-0.75, -0.45)], res=14)
    nose = spl([(0.0, -0.35), (0.35, -0.35), (*(0.0, -0.75), 0), (-0.35, -0.35)], res=20)
    mouth = [spl([(0.0, -0.75), (0.0, -1.1), (0.3, -1.25), (0.5, -1.15)], closed=False), spl([(0.0, -1.1), (-0.3, -1.25), (-0.5, -1.15)], closed=False)]
    eyes_ = [lens((0.55, 0.5), (0.95, 0.45), 0.3, 10), lens((-0.55, 0.5), (-0.95, 0.45), 0.3, 10)]
    fur = [spl([(-2.0, 0.2), (-2.4, -0.8), (-2.5, -2.2), (-2.6, -3.0)], closed=False), spl([(2.0, 0.2), (2.4, -0.8), (2.5, -2.2), (2.6, -3.0)], closed=False)]
    tufts_ = [poly((-1.95, -0.3), (-2.15, -0.45), (-1.9, -0.6), closed=False), poly((1.95, -0.3), (2.15, -0.45), (1.9, -0.6), closed=False)]
    ears = hide(ears + ears_in, [head])
    return make("Polar Bear Portrait", [head, muzzle, nose] + ears + mouth + eyes_ + fur, [eye(0.75, 0.48, 0.1), eye(-0.75, 0.48, 0.1), nose[:-1]][:2])


@design("polar_bear_cub_floe", T)
def bear_cub_floe(rng):
    body = spl([(*(1.5, 0.4), 0), (1.25, 0.75), (0.95, 0.95), (0.85, 1.2), (*(0.75, 1.32), 0), (0.6, 1.15), (0.3, 1.1), (-0.3, 1.25),
                (-1.1, 1.15), (-1.5, 0.75), (-1.55, 0.2), (-1.35, -0.2), (*(-1.6, -0.45), 0), (*(-0.9, -0.45), 0), (-0.75, -0.2), (-0.4, -0.05),
                (0.1, -0.1), (*(0.0, -0.45), 0), (*(0.75, -0.45), 0), (0.7, -0.15), (0.85, 0.1), (1.1, 0.2), (1.45, 0.3)], res=18)
    det = [arc(1.46, 0.42, 0.08, -1.2, 2.2, 8), arc(0.7, 1.15, 0.07, 0.5, 3.0, 6)]
    floe_ = [poly((-2.2, -0.45), (2.0, -0.45), (1.6, -1.1), (-1.9, -1.1))]
    under = [poly((-1.9, -1.1), (1.6, -1.1), (0.8, -2.4), (-0.6, -2.6), (-1.4, -1.9), closed=False)]
    water = [sea(-0.95, -3.4, -2.05, 0.06, 2), sea(-0.95, 1.7, 3.4, 0.06, 2)]
    fish = [lens((2.2, -2.0), (3.0, -1.8), 0.25, 12), poly((2.2, -2.0), (1.95, -1.8), (1.95, -2.2), (2.2, -2.0), closed=False)]
    return make("Polar Bear Cub on an Ice Floe", [body] + det + floe_ + hide(under, []) + water + fish, [eye(1.05, 0.66, 0.06)])


# ------------------------------------------------------------ penguins

def penguin(dx=0.0, dy=0.0, s=1.0, flip=False, kind="emperor"):
    """Standing penguin facing right (feet at y=0, about 4.2 tall)."""
    out = spl([(*(1.25, 3.3), 0), (0.75, 3.55), (0.3, 3.95), (-0.25, 3.95), (-0.65, 3.5), (-0.85, 2.6), (-1.05, 1.4), (-1.1, 0.5),
               (-0.85, 0.15), (*(-1.3, -0.05), 0), (-0.4, 0.05), (0.0, 0.0), (0.55, 0.05), (0.9, 0.5), (1.0, 1.4), (0.85, 2.4),
               (0.6, 2.95), (0.8, 3.15)], res=14)
    belly = spl([(0.45, 3.05), (0.3, 2.4), (0.1, 1.4), (0.05, 0.6), (0.4, 0.15)], closed=False)
    wing = spl([(-0.55, 2.5), (-0.95, 1.6), (*(-0.75, 0.75), 0), (-0.45, 1.6), (-0.4, 2.3)], closed=False)
    feet = [poly((0.0, 0.0), (0.25, -0.15), (0.55, -0.12), (0.7, 0.0), closed=False)]
    beak = [[(1.25, 3.3), (0.62, 3.38)]]
    patch = []
    if kind in ("emperor", "king"):
        patch = [spl([(0.05, 3.2), (0.35, 3.05), (0.45, 2.7), (0.25, 2.5), (0.05, 2.75)], res=20)]
    g = lambda pts: tf(pts, dx, dy, s, 0.0, flip)  # noqa: E731
    return {"strokes": [g(p) for p in [out, belly, wing] + feet + beak + patch], "sil": [g(out)], "hints": [g(eye(0.4, 3.45, 0.07))]}


# dropped: the subject repeats another book
def emperor_chick(rng):
    adult = penguin(0.0, 0.0, 1.0)
    chick = spl([(*(2.0, 1.85), 0), (1.7, 2.05), (1.6, 2.4), (1.3, 2.6), (0.9, 2.45), (0.75, 2.0), (0.6, 1.3), (0.7, 0.6), (1.0, 0.35),
                 (1.45, 0.35), (1.75, 0.7), (1.8, 1.3), (1.65, 1.75)], res=16)
    cface = spl([(1.6, 2.35), (1.35, 2.3), (1.2, 2.05), (1.3, 1.8), (1.6, 1.78)], closed=False)
    cwing = spl([(0.85, 1.7), (0.7, 1.1), (0.95, 0.8)], closed=False)
    fluff = zigzag(0.65, 1.75, 0.45, 0.06, 5)
    cfeet = [poly((1.0, 0.35), (1.15, 0.05), (1.45, 0.05), (1.45, 0.35), closed=False)]
    ice = [ground(-3.0, 3.0, -0.15), ground(-2.4, -1.4, -0.45), ground(0.6, 2.2, -0.5)]
    chk = {"strokes": [chick, cface, cwing, fluff] + cfeet, "sil": [chick], "hints": [eye(1.62, 2.1, 0.06)]}
    st, hi = scene(chk, adult)
    return make("Emperor Penguin with Chick", st + ice, hi)


@design("polar_king_penguin", T)
def king_penguin(rng):
    p = penguin(0.0, 0.0, 1.0, kind="king")
    bib = [spl([(0.62, 2.9), (0.75, 2.5), (0.95, 2.1)], closed=False)]
    stripe = [spl([(0.9, 3.28), (0.55, 3.25), (0.4, 3.05)], closed=False)]
    rocks = [spl([(-2.6, 0.0), (-2.4, 0.5), (-1.8, 0.6), (-1.5, 0.0)], closed=False), spl([(1.5, 0.0), (1.8, 0.35), (2.4, 0.3), (2.6, 0.0)], closed=False)]
    p2 = penguin(-2.4, 0.9, 0.55, flip=True, kind="king")
    st, hi = scene(p, p2)
    return make("King Penguins", st + bib + stripe + hide(rocks, p["sil"]) + [ground(-3.0, 3.0, 0.0)], hi)


@design("polar_adelie_sliding", T)
def adelie_sliding(rng):
    def slider(dx, dy, s):
        body = spl([(*(2.0, 0.55), 0), (1.55, 0.7), (1.2, 0.95), (0.7, 0.95), (0.3, 0.7), (-0.6, 0.65), (-1.3, 0.55), (*(-1.75, 0.5), 0),
                    (-1.3, 0.2), (-0.5, 0.0), (0.5, 0.0), (1.1, 0.15), (1.5, 0.35)], res=18)
        belly = spl([(1.1, 0.2), (0.5, 0.15), (-0.5, 0.15), (-1.3, 0.3)], closed=False)
        wing = spl([(0.6, 0.55), (0.0, 0.25), (*(-0.7, 0.05), 0), (-0.1, 0.5)], closed=False)
        feet = [poly((-1.65, 0.45), (-2.05, 0.6), (-2.0, 0.35), closed=False)]
        eyering = circle(1.3, 0.72, 0.1, 12)
        beak = [[(2.0, 0.55), (1.55, 0.6)]]
        g = lambda pts: tf(pts, dx, dy, s)  # noqa: E731
        return {"strokes": [g(p) for p in [body, belly, wing, eyering] + feet + beak], "sil": [g(body)], "hints": [g(eye(1.3, 0.72, 0.045))]}
    a, b, c = slider(0.6, 0.0, 1.0), slider(-1.7, 1.2, 0.75), slider(1.5, 2.2, 0.6)
    st, hi = scene(a, b, c)
    trails = [[(-3.2, -0.05), (-1.2, -0.05)], [(-3.4, 1.15), (-3.0, 1.15)], [(-0.4, 2.15), (0.5, 2.15)]]
    hill = [spl([(-3.4, 2.8), (-2.0, 3.4), (-0.4, 3.0)], closed=False)]
    return make("Adelie Penguins Sliding on Their Bellies", st + trails + [ground(-3.4, 3.4, -0.15)] + hide(hill, []), hi)


@design("polar_rockhopper", T)
def rockhopper(rng):
    p = penguin(0.0, 0.6, 0.95, kind="rock")
    crest = [spl([(0.9, 3.62), (0.4, 3.78), (-0.1, 3.82), (*(-0.75, 3.55), 0), (-0.2, 3.66), (*(-0.6, 3.3), 0), (0.1, 3.6), (0.55, 3.58)], closed=False)]
    brow = [spl([(1.0, 3.62), (0.55, 3.72), (0.1, 3.75)], closed=False)]
    crest = [tf(c_, 0.0, 0.6, 0.95) for c_ in crest]
    brow = [tf(c_, 0.0, 0.6, 0.95) for c_ in brow]
    rock = [spl([(-2.4, 0.6), (-1.8, 0.75), (1.4, 0.6), (2.3, 0.0), (2.6, -1.0), (*(2.9, -1.6), 0), (*(-2.9, -1.6), 0), (-2.8, -0.6)], closed=False)]
    cracks = [[(-1.2, 0.0), (-0.7, -0.6), (-0.9, -1.2)], [(1.2, -0.4), (1.6, -1.0)]]
    splash = [sea(-1.6, -3.4, 3.4, 0.08, 6)]
    st, hi = scene(p, obj(rock + cracks, []))
    return make("Rockhopper Penguin", st + crest + brow + splash, hi)


@design("polar_chinstrap", T)
def chinstrap(rng):
    p = penguin(0.0, 0.0, 1.0, kind="chin")
    strap = [spl([(0.05, 3.75), (0.25, 3.15), (0.7, 2.95)], closed=False)]
    cap = [spl([(0.75, 3.55), (0.3, 3.6), (-0.15, 3.35), (-0.5, 3.0)], closed=False)]
    p2 = penguin(-2.2, 0.4, 0.62, flip=True, kind="chin")
    strap2 = [tf(spl([(0.05, 3.75), (0.25, 3.15), (0.7, 2.95)], closed=False), -2.2, 0.4, 0.62, 0, True)]
    snow = [spl([(-3.0, 0.0), (-1.0, 0.1), (1.0, -0.05), (3.0, 0.05)], closed=False)]
    st, hi = scene(obj(strap + cap, []), p, obj(strap2, []), p2)
    return make("Chinstrap Penguins", st + snow, hi)


@design("polar_gentoo_pebble", T)
def gentoo_pebble(rng):
    p = penguin(0.0, 0.5, 1.0, kind="gentoo")
    head_patch = [spl([(0.15, 3.85), (0.55, 3.8), (0.7, 3.6)], closed=False)]
    pebble = [ellipse(1.42, 3.82, 0.17, 0.12, 16)]
    nest = []
    for k in range(9):
        x = -2.4 + 0.55 * k
        nest.append(ellipse(x, 0.42 + 0.06 * (k % 2), 0.3, 0.2, 20))
    for k in range(6):
        nest.append(ellipse(-1.9 + 0.6 * k, 0.1, 0.32, 0.2, 20))
    egg = [ellipse(-1.85, 1.02, 0.38, 0.5, 30)]
    st, hi = scene(obj(pebble), p, obj(egg), obj(nest))
    return make("Gentoo Penguin Bringing a Pebble", st + head_patch, hi)


@design("polar_emperor_huddle", T)
def emperor_huddle(rng):
    items = []
    spots = [(0.0, -1.6, 0.85, False), (-1.7, -1.4, 0.75, True), (1.7, -1.35, 0.72, False), (-0.85, -0.6, 0.62, True), (0.9, -0.55, 0.6, False),
             (-2.6, -0.5, 0.5, True), (2.5, -0.45, 0.48, False), (0.0, 0.15, 0.5, True)]
    for x, y, s, fl in spots:
        items.append(penguin(x, y, s, fl))
    st, hi = scene(*items)
    snow = [ground(-3.4, 3.4, -1.75)]
    flakes_ = [star(x, y, 0.12, 6, 0.4) for x, y in [(-2.8, 2.6), (-1.5, 3.1), (0.6, 3.3), (2.2, 2.8), (2.9, 1.6), (-3.0, 1.4)]]
    return make("Emperor Penguins Huddling Together", st + snow + flakes_, hi)


# ------------------------------------------------------------ seals, walruses, whales

def walrus(dx=0.0, dy=0.0, s=1.0, flip=False):
    body = spl([(2.72, 0.72), (2.8, 1.05), (2.52, 1.38), (2.1, 1.55), (1.6, 1.52), (0.6, 1.62), (-0.6, 1.35), (-1.6, 0.9), (-2.4, 0.4),
                (-2.85, 0.05), (*(-3.35, -0.05), 0), (*(-3.2, -0.42), 0), (-2.6, -0.52), (-1.5, -0.62), (0.0, -0.66), (0.75, -0.62),
                (*(0.95, -0.98), 0), (*(1.95, -0.98), 0), (1.62, -0.7), (1.42, -0.3), (1.88, 0.1), (2.28, 0.35), (2.55, 0.5)], res=16)
    tusks = [spl([(2.38, 0.5), (2.32, -0.2), (*(2.12, -1.05), 0), (2.22, -0.2), (2.25, 0.45)], closed=False),
             spl([(2.6, 0.5), (2.6, -0.2), (*(2.48, -1.0), 0), (2.5, -0.2), (2.48, 0.48)], closed=False)]
    pad = [spl([(2.8, 1.0), (2.45, 1.05), (2.25, 0.75), (2.4, 0.5)], closed=False)]
    whisk = [[(2.75, 0.8 - 0.12 * k), (3.05, 0.75 - 0.18 * k)] for k in range(3)]
    folds = [arc(1.6, 0.6, 0.65, 1.0, 2.6, 12), arc(1.2, 0.5, 0.75, 1.1, 2.4, 12), arc(-1.6, -0.2, 0.6, 0.7, 1.9, 10)]
    flip2 = [spl([(-0.2, -0.6), (0.2, -0.98), (*(0.9, -0.98), 0)], closed=False)]
    g = lambda pts: tf(pts, dx, dy, s, 0.0, flip)  # noqa: E731
    st = [body] + hide(tusks, [body]) + tusks[:0] + pad + whisk + folds + hide(flip2, [body])
    return {"strokes": [g(p) for p in st], "sil": [g(body)] + [g(t + [t[0]]) for t in tusks], "hints": [g(eye(2.05, 1.2, 0.06))]}


@design("polar_walrus", T)
def walrus_one(rng):
    w = walrus()
    tusk_lines = [tf(t, 0, 0, 1.0) for t in []]
    ice = [floe(-3.6, 3.4, -0.98, 0.5)]
    water = [sea(-1.75, -3.6, 3.4, 0.06, 6)]
    return make("Walrus with Long Tusks", w["strokes"] + hide(ice, w["sil"]) + water, w["hints"])


@design("polar_walrus_herd", T)
def walrus_herd(rng):
    a = walrus(0.3, -0.6, 0.75)
    b = walrus(-1.0, 0.6, 0.62, flip=True)
    c = walrus(1.6, 1.3, 0.5)
    st, hi = scene(a, b, c)
    ice = [spl([(-3.4, -1.35), (-1.0, -1.3), (1.5, -1.38), (3.6, -1.32)], closed=False)]
    return make("Walrus Herd on the Ice", st + ice + [sea(-1.9, -3.4, 3.6, 0.06, 7)], hi)


@design("polar_harp_seal_pup", T)
def harp_seal_pup(rng):
    body = spl([(2.42, 0.72), (2.3, 1.15), (1.9, 1.52), (1.3, 1.5), (0.6, 1.05), (-0.6, 0.72), (-1.7, 0.38), (*(-2.45, 0.6), 0), (-2.2, 0.15),
                (*(-2.55, -0.15), 0), (-1.8, -0.22), (0.0, -0.3), (1.2, -0.25), (1.9, 0.2), (2.25, 0.45)], res=16)
    eye_r = [ellipse(1.9, 1.45, 0.2, 0.24, 24)]
    nose = [spl([(2.38, 0.78), (2.5, 0.72), (*(2.42, 0.6), 0), (2.32, 0.7)], res=30)]
    mouth = [spl([(2.38, 0.55), (2.3, 0.45), (2.15, 0.48)], closed=False)]
    whisk = [[(2.2, 0.62 - 0.1 * k), (2.75, 0.68 - 0.2 * k)] for k in range(3)]
    flipper = [spl([(0.9, 0.3), (1.2, -0.05), (*(1.0, -0.42), 0), (0.75, -0.1)], closed=False)]
    fluff = [spl([(0.2, 1.0), (0.0, 0.85), (-0.2, 0.95)], closed=False), spl([(-0.8, 0.6), (-1.0, 0.48), (-1.2, 0.55)], closed=False)]
    ice = [spl([(-3.2, -0.3), (-1.0, -0.38), (1.5, -0.3), (3.2, -0.36)], closed=False)]
    g = lambda L: [transform(q, 0, 0, sx=1.0, sy=1.45) for q in L]  # noqa: E731
    return make("Harp Seal Pup", g([body] + nose + mouth + whisk + flipper + fluff + ice) + eye_r, g([eye(1.92, 1.0, 0.13)]))


@design("polar_leopard_seal", T)
def leopard_seal(rng):
    body = spl([(*(3.05, 0.5), 0), (2.5, 0.88), (1.7, 0.85), (0.4, 0.75), (-1.2, 0.5), (-2.3, 0.15), (*(-3.15, 0.55), 0), (-2.85, 0.05),
                (*(-3.2, -0.38), 0), (-2.2, -0.22), (-0.6, -0.5), (0.9, -0.5), (1.9, -0.38), (2.5, -0.25), (*(2.9, -0.05), 0), (*(2.15, 0.22), 0)], res=16)
    teeth = [zigzag(2.25, 2.95, 0.4, 0.06, 5), zigzag(2.25, 2.85, -0.03, 0.05, 4)]
    teeth = [[(x, y - 0.03 * (x - 2.25)) for x, y in teeth[0]], [(x, y - 0.06 * (x - 2.25)) for x, y in teeth[1]]]
    flipper = [lens((0.9, -0.2), (0.3, -1.2), 0.25, 14)]
    sp = [circle(x, y, 0.1, 10) for x, y in [(1.2, 0.2), (0.6, 0.45), (0.2, 0.0), (-0.4, 0.4), (-0.9, 0.05), (-1.5, 0.25), (1.6, 0.45)]]
    pg = spl([(*(-1.0, 2.0), 0), (-1.3, 2.25), (-1.9, 2.35), (-2.6, 2.2), (*(-3.0, 2.3), 0), (-2.6, 1.95), (-1.9, 1.8), (-1.3, 1.85)], res=16)
    pg_belly = [spl([(-1.05, 2.0), (-1.6, 1.88), (-2.4, 1.98)], closed=False)]
    pg_wing = [lens((-1.7, 2.15), (-2.3, 2.6), 0.25, 10)]
    bub = bubbles([(3.2, 1.0, 0.1), (3.3, 1.5, 0.14), (-0.2, 1.7, 0.12)])
    rays = [[(x, 3.0), (x - 0.8, 1.0)] for x in (0.6, 1.8)]
    return make("Leopard Seal Hunting", [body] + teeth + hide(flipper, [body]) + within(sp, [body]) + [pg] + pg_belly + pg_wing + bub + hide(rays, [body]) + [sea(3.0, -3.4, 3.4, 0.07, 6)],
                [eye(2.1, 0.62, 0.07), eye(-1.3, 2.12, 0.045)])


@design("polar_elephant_seal", T)
def elephant_seal(rng):
    body = spl([(*(2.55, 1.15), 0), (2.5, 1.55), (2.2, 1.95), (1.75, 2.08), (1.3, 1.92), (0.8, 1.4), (0.0, 0.95), (-1.5, 0.45), (-2.6, 0.05),
                (*(-3.2, 0.3), 0), (-2.95, -0.1), (*(-3.25, -0.45), 0), (-1.6, -0.62), (0.4, -0.7), (1.2, -0.62), (1.5, -0.2), (1.62, 0.45),
                (1.95, 0.88), (2.22, 0.95), (*(2.05, 1.18), 0), (2.35, 1.12)], res=16)
    nose = [spl([(1.95, 1.95), (2.15, 1.6), (2.38, 1.3)], closed=False)]
    nostril = [arc(2.45, 1.2, 0.08, 0.5, 3.5, 8)]
    folds = [arc(1.0, 1.1, 0.5, -0.2, 1.3, 10), arc(0.8, 0.8, 0.55, -0.1, 1.2, 10), arc(0.55, 0.55, 0.55, 0.0, 1.1, 10)]
    flipper = [spl([(0.9, -0.1), (1.25, -0.7), (*(1.75, -0.72), 0), (1.4, -0.4), (1.3, 0.0)], closed=False)]
    teeth = [[(2.1, 1.12), (2.12, 1.0)]]
    sand = [spl([(-3.4, -0.72), (-1.0, -0.66), (1.4, -0.74), (3.0, -0.7)], closed=False)]
    rocks = [spl([(2.6, -0.7), (2.75, -0.35), (3.15, -0.3), (3.3, -0.7)], closed=False)]
    return make("Elephant Seal Bull Roaring", [body] + nose + nostril + folds + hide(flipper, [body]) + teeth + sand + rocks, [eye(1.72, 1.6, 0.07)])


def whale_body(pts, res=16):
    return spl(pts, res=res)


# dropped: the subject repeats another book
def narwhal(rng):
    body = whale_body([(2.25, 0.2), (2.1, 0.6), (1.5, 0.85), (0.3, 0.82), (-1.0, 0.55), (-2.1, 0.2), (-2.5, 0.12), (*(-3.1, 0.62), 0),
                       (-2.85, 0.15), (*(-3.15, -0.35), 0), (-2.45, -0.02), (-1.8, -0.22), (-0.5, -0.5), (0.9, -0.55), (1.8, -0.35)])
    tusk = tube(cubic((2.2, 0.32), (3.0, 0.45), (3.8, 0.58), (4.6, 0.72), 30), lambda t: 0.16 * (1 - t) + 0.02)
    grooves = []
    for k in range(1, 9):
        t = k / 9
        x, y = 2.2 + 2.4 * t, 0.32 + 0.4 * t
        w = 0.08 * (1 - t) + 0.01
        grooves.append([(x - 0.06, y - w), (x + 0.06, y + w)])
    flip_ = [lens((1.2, -0.3), (0.6, -0.9), 0.3, 12)]
    spots = [ellipse(x, y, 0.13, 0.08, 12) for x, y in [(0.0, 0.5), (-0.5, 0.35), (-1.0, 0.3), (0.5, 0.55), (-1.5, 0.15), (-0.2, 0.1)]]
    small = transform(body, -0.6, 2.0, 0.45)
    stusk = transform(tube(cubic((2.2, 0.32), (3.0, 0.45), (3.8, 0.58), (4.6, 0.72), 20), lambda t: 0.16 * (1 - t) + 0.02), -0.6, 2.0, 0.45)
    return make("Narwhal with Spiral Tusk", [body, tusk] + grooves + hide(flip_, [body]) + spots + [small, stusk] + [sea(3.2, -3.0, 4.6, 0.07, 6)],
                [eye(1.65, 0.12, 0.07), eye(-0.6 + 1.65 * 0.45, 2.0 + 0.12 * 0.45, 0.04)])


# dropped: the subject repeats another book
def beluga(rng):
    body = whale_body([(2.85, 0.05), (2.75, 0.3), (2.45, 0.42), (2.35, 0.9), (1.9, 1.3), (1.2, 1.25), (0.0, 0.95), (-1.3, 0.55), (-2.2, 0.18),
                       (*(-2.9, 0.75), 0), (-2.65, 0.1), (*(-3.0, -0.5), 0), (-2.2, -0.12), (-1.0, -0.45), (0.5, -0.65), (1.8, -0.5), (2.5, -0.2)])
    melon = [spl([(2.45, 0.42), (2.2, 0.55), (2.0, 0.85)], closed=False)]
    smile = [spl([(2.82, 0.0), (2.5, -0.05), (2.25, 0.1)], closed=False)]
    flip_ = [lens((1.4, -0.4), (0.9, -1.1), 0.3, 12)]
    ridge = [spl([(0.6, 1.08), (-0.4, 0.85), (-1.2, 0.6)], closed=False)]
    bub = bubbles([(2.1, 1.7, 0.12), (2.3, 2.1, 0.15), (2.0, 2.55, 0.1)])
    return make("Beluga Whale", [body] + melon + smile + hide(flip_, [body]) + ridge + bub + [sea(3.0, -3.0, 3.0, 0.07, 6)], [eye(1.95, 0.35, 0.07)])


def orca_pts():
    return [(3.0, 0.0), (2.6, 0.45), (1.6, 0.78), (0.65, 0.85), (*(0.25, 2.0), 0), (0.0, 0.85), (-1.2, 0.6), (-2.3, 0.22),
            (*(-3.2, 0.78), 0), (-2.95, 0.12), (*(-3.2, -0.48), 0), (-2.3, -0.08), (-1.3, -0.35), (0.3, -0.62), (1.6, -0.5),
            (2.5, -0.25), (2.95, -0.08)]


@design("polar_orca_breaching", T)
def orca_breaching(rng):
    rot = math.radians(52)
    g = lambda pts: transform(pts, 0.0, 0.0, 1.0, rot)  # noqa: E731
    body = g(spl(orca_pts(), res=16))
    patch = g(lens((1.35, 0.35), (2.05, 0.3), 0.3, 12))
    belly = g(spl([(2.6, -0.2), (1.6, -0.3), (0.4, -0.35), (-0.6, -0.05), (-1.2, -0.28)], closed=False))
    saddle = g(arc(-0.05, 0.25, 0.65, 0.6, 2.4, 12))
    flip_ = g(lens((1.4, -0.4), (0.9, -1.2), 0.3, 12))
    wl = -1.6
    under = [poly((-4, wl), (4, wl), (4, -6), (-4, -6))]
    st = hide([body, patch, belly, saddle, flip_], under)
    splash = [quad((-2.2, wl), (-2.6, wl + 1.0), (-3.0, wl + 0.3), 10), quad((-1.5, wl), (-1.7, wl + 1.4), (-2.1, wl + 1.1), 10),
              quad((-0.6, wl), (-0.3, wl + 1.2), (0.1, wl + 0.6), 10), quad((0.2, wl), (0.7, wl + 0.8), (1.1, wl + 0.2), 10)]
    drops = [circle(x, y, 0.1, 10) for x, y in [(-2.8, wl + 1.3), (-2.3, wl + 1.8), (0.4, wl + 1.5), (1.0, wl + 1.0)]]
    water = [wave(-3.4, -1.9, wl, 0.06, 2, 40), wave(0.7, 3.4, wl, 0.06, 4, 60), wave(-3.4, 3.4, wl - 0.8, 0.06, 7, 120)]
    return make("Orca Breaching", st + hide(splash, [body]) + drops + water, [transform([eye(1.7, 0.18, 0.06)][0], 0, 0, 1.0, rot)])


@design("polar_bowhead", T)
def bowhead(rng):
    body = whale_body([(3.0, 0.2), (2.75, 0.75), (2.2, 1.1), (1.75, 1.22), (1.3, 1.05), (0.2, 1.0), (-1.4, 0.65), (-2.4, 0.2),
                       (*(-3.2, 0.85), 0), (-2.9, 0.12), (*(-3.25, -0.6), 0), (-2.4, -0.12), (-1.0, -0.6), (0.5, -0.85), (2.0, -0.65), (2.75, -0.25)])
    mouth = [spl([(2.98, 0.18), (2.6, 0.45), (2.0, 0.55), (1.45, 0.25), (1.25, -0.05)], closed=False)]
    chin = [spl([(2.75, -0.2), (2.3, -0.3), (1.8, -0.15), (1.6, -0.45), (2.1, -0.65)], closed=False)]
    blow = [quad((1.8, 1.25), (1.6, 2.0), (1.1, 2.4), 10), quad((1.85, 1.25), (2.0, 2.0), (2.5, 2.4), 10)]
    flip_ = [lens((1.0, -0.6), (0.4, -1.4), 0.3, 12)]
    ice = [poly((-3.4, 2.6), (-1.6, 2.6), (-1.8, 2.3), (-3.3, 2.25)), poly((2.6, 2.7), (3.4, 2.7), (3.4, 2.35), (2.7, 2.4))]
    return make("Bowhead Whale", [body] + mouth + chin + blow + hide(flip_, [body]) + ice + [sea(2.6, -1.5, 2.5, 0.06, 4)], [eye(1.3, 0.12, 0.07)])


@design("polar_weddell_seal", T)
def weddell_seal(rng):
    ice_top, ice_bot = 2.6, 1.9
    hole = (0.6, 1.4)
    ice = [[(-3.4, ice_bot), (hole[0], ice_bot)], [(hole[1], ice_bot), (3.4, ice_bot)], [(-3.4, ice_top), (hole[0] - 0.1, ice_top)],
           [(hole[1] + 0.1, ice_top), (3.4, ice_top)], [(hole[0] - 0.1, ice_top), (hole[0], ice_bot)], [(hole[1] + 0.1, ice_top), (hole[1], ice_bot)]]
    body = spl([(*(1.0, 2.25), 0), (1.3, 2.05), (1.5, 1.6), (1.55, 0.8), (1.35, -0.2), (0.8, -1.2), (0.05, -1.95), (*(-0.6, -2.6), 0),
                (-0.3, -2.0), (*(-1.0, -2.25), 0), (-0.4, -1.7), (0.05, -0.9), (0.35, 0.2), (0.6, 1.2), (0.72, 1.9)], res=16)
    face = [arc(1.02, 2.15, 0.07, 3.6, 6.6, 8), [(1.05, 2.0), (1.22, 1.98)]]
    flip_ = [lens((1.25, 0.6), (1.9, -0.1), 0.3, 12)]
    spots = [ellipse(x, y, 0.13, 0.09, 10) for x, y in [(0.95, 0.3), (0.6, -0.5), (0.3, -1.1), (1.05, 1.0), (1.2, -0.2), (0.6, 0.8)]]
    bub = bubbles([(-0.2, 1.0, 0.1), (-0.4, 0.4, 0.13), (-0.25, -0.2, 0.09)])
    cracks = [[(-2.5, ice_top), (-2.2, ice_bot)], [(2.5, ice_top), (2.2, 2.2), (2.6, ice_bot)]]
    fish = [lens((-2.6, -0.6), (-1.8, -0.4), 0.25, 12), poly((-2.6, -0.6), (-2.85, -0.4), (-2.8, -0.8), (-2.6, -0.6), closed=False)]
    return make("Weddell Seal under the Ice", ice + [body] + face + hide(flip_, [body]) + within(spots, [body]) + bub + cracks + fish, [eye(1.13, 2.12, 0.05)])


@design("polar_bearded_seal", T)
def bearded_seal(rng):
    body = spl([(2.5, 1.05), (2.35, 1.45), (1.95, 1.65), (1.45, 1.5), (0.6, 1.05), (-0.8, 0.75), (-1.9, 0.35), (*(-2.7, 0.65), 0),
                (-2.4, 0.15), (*(-2.8, -0.15), 0), (-1.8, -0.25), (0.2, -0.32), (1.5, -0.2), (2.0, 0.4), (2.35, 0.75)], res=16)
    whisk = [quad((2.35, 0.95 - 0.07 * k), (2.7, 0.95 - 0.15 * k), (3.0, 0.7 - 0.3 * k), 10) for k in range(4)]
    nose = [arc(2.45, 1.08, 0.07, -1.0, 2.2, 8)]
    flipper = [spl([(1.2, 0.2), (1.45, -0.1), (*(1.3, -0.3), 0), (1.0, -0.05)], closed=False)]
    claws = [[(1.3 + 0.07 * k, -0.28), (1.34 + 0.07 * k, -0.18)] for k in range(3)][:0]
    floe_ = [floe(-3.2, 3.2, -0.32, 0.45)]
    water = [sea(-0.9, -3.4, 3.4, 0.06, 6)]
    return make("Bearded Seal on an Ice Floe", [body] + whisk + nose + flipper + floe_ + water, [eye(1.98, 1.3, 0.07)])


@design("polar_greenland_shark", T)
def greenland_shark(rng):
    body = spl([(3.0, 0.1), (2.7, 0.55), (1.6, 0.85), (0.6, 0.95), (*(0.25, 1.4), 0), (-0.1, 0.9), (-1.0, 0.7), (*(-1.25, 1.0), 0), (-1.5, 0.62),
                (-2.3, 0.35), (*(-3.1, 0.95), 0), (-2.85, 0.1), (*(-3.05, -0.45), 0), (-2.3, -0.08), (-1.4, -0.35), (0.6, -0.65),
                (1.8, -0.55), (2.6, -0.3)], res=16)
    gills = [spl([(1.6 - 0.18 * k, 0.4), (1.55 - 0.18 * k, 0.1), (1.6 - 0.18 * k, -0.2)], closed=False) for k in range(4)]
    fin = [lens((1.0, -0.45), (0.3, -1.2), 0.3, 12), lens((-1.0, -0.4), (-1.5, -0.8), 0.3, 10)]
    mouth = [quad((2.75, -0.15), (2.5, -0.3), (2.25, -0.25), 8)]
    spots = [circle(x, y, 0.08, 10) for x, y in [(0.5, 0.4), (0.0, 0.2), (-0.6, 0.35), (-1.1, 0.1), (0.9, 0.1), (-1.7, 0.2)]]
    snow = [circle(x, y, 0.06, 8) for x, y in []]
    rays = [[(x, 2.6), (x - 0.6, 1.4)] for x in (-2.0, -0.5, 1.0, 2.5)]
    return make("Greenland Shark", [body] + gills + hide(fin, [body]) + mouth + spots + rays + [sea(2.8, -3.4, 3.4, 0.07, 6)], [eye(2.3, 0.35, 0.07)])


def union(polys):
    """Outline of the union of closed shapes."""
    out = []
    for i, p in enumerate(polys):
        out += hide([p], [q for j, q in enumerate(polys) if j != i])
    return out


def limb(pts, w0, w1, foot=None):
    """Closed tapered leg along `pts` (top to bottom)."""
    c = spl(pts, closed=False, res=30)
    return tube(c, lambda t: w0 + (w1 - w0) * t)


# ------------------------------------------------------------ land mammals

@design("polar_musk_ox", T)
def musk_ox(rng):
    body = spl([(2.6, -0.25), (2.7, 0.3), (2.45, 0.8), (2.05, 0.95), (1.4, 1.45), (0.8, 1.7), (-0.3, 1.45), (-1.4, 1.3), (-2.0, 1.05),
                (-2.35, 0.5), (-2.4, -0.2), (*(-2.35, -0.65), 0), (*(-2.0, -0.45), 0), (*(-1.7, -0.7), 0), (*(-1.3, -0.45), 0),
                (*(-0.9, -0.72), 0), (*(-0.5, -0.45), 0), (*(-0.1, -0.75), 0), (*(0.3, -0.48), 0), (*(0.7, -0.75), 0), (*(1.1, -0.5), 0),
                (*(1.5, -0.78), 0), (*(1.85, -0.5), 0), (*(2.1, -0.85), 0), (2.25, -0.55), (2.45, -0.4)], res=16)
    legs = [rect(x - 0.15, -1.3, x + 0.15, -0.5) for x in (-1.8, -1.1, 0.9, 1.6)]
    hooves = [[(x - 0.15, -1.15), (x + 0.15, -1.15)] for x in (-1.8, -1.1, 0.9, 1.6)]
    horn = tube(spl([(2.3, 1.0), (1.9, 1.0), (1.7, 0.6), (1.75, 0.15), (2.0, -0.05), (*(2.35, 0.1), 0)], closed=False, res=30),
                lambda t: 0.3 * (1 - t) + 0.04)
    boss = [spl([(2.35, 0.95), (2.05, 1.08), (1.7, 0.98)], closed=False)]
    strands = [spl([(x, 1.3 - 0.1 * abs(x)), (x - 0.12, 0.6), (x + 0.05, 0.0), (x - 0.05, -0.35)], closed=False) for x in (-1.6, -0.9, -0.2, 0.5, 1.2)]
    nose = [arc(2.6, -0.1, 0.08, -1.0, 2.0, 8)]
    st = [body] + hide(legs, [body]) + hooves + [horn] + hide(boss, [horn]) + nose + strands
    snow = [ground(-3.0, 3.0, -1.3)]
    return make("Musk Ox", st + snow + tufts([(-2.6, -1.3), (2.6, -1.3)], 0.8), [eye(2.15, 0.45, 0.06)])


@design("polar_caribou", T)
def caribou(rng):
    body = spl([(1.4, 1.5), (0.6, 1.62), (-0.6, 1.55), (-1.4, 1.5), (-1.7, 1.2), (-1.65, 0.75), (-1.2, 0.45), (0.0, 0.35), (1.0, 0.45), (1.5, 0.75)], res=16)
    neck = spl([(0.9, 1.4), (1.5, 2.1), (1.9, 2.45), (2.25, 2.3), (1.9, 1.7), (1.85, 1.2), (1.5, 0.6), (1.0, 0.8)], res=16)
    head = spl([(1.75, 2.45), (2.0, 2.65), (2.5, 2.4), (*(2.95, 2.05), 0), (2.8, 1.88), (2.35, 1.95), (2.0, 2.05)], res=16)
    mane = [spl([(1.55, 1.2), (1.75, 0.85), (*(1.75, 0.6), 0), (1.95, 1.0), (*(2.05, 0.8), 0), (2.05, 1.3), (1.95, 1.75)], closed=False)]
    legs = [limb([(1.2, 0.6), (1.25, -0.4), (1.2, -1.4)], 0.32, 0.14), limb([(0.75, 0.6), (0.7, -0.4), (0.6, -1.4)], 0.3, 0.13),
            limb([(-1.3, 0.9), (-1.0, -0.2), (-1.25, -1.4)], 0.45, 0.14), limb([(-0.9, 0.6), (-0.7, -0.3), (-0.85, -1.4)], 0.38, 0.13)]
    hooves = [poly((x - 0.12, -1.35), (x + 0.12, -1.35), (x + 0.16, -1.55), (x - 0.12, -1.55)) for x in (1.2, 0.6, -1.25, -0.85)]
    ear = [lens((1.95, 2.55), (1.75, 2.95), 0.3, 10)]
    tail = [lens((-1.68, 1.2), (-1.95, 0.8), 0.35, 10)]
    near = union([body, neck, head] + legs[:1] + legs[2:3])
    farl = hide([legs[1], legs[3]], [body, neck, legs[0], legs[2]])

    def antler(sgn, dx):
        beam = spl([(2.05 + dx, 2.62), (1.7 + dx, 3.2), (1.2 + dx, 3.6), (1.0 + dx, 4.3), (1.4 + dx, 4.9)], closed=False)
        tines = [spl([(1.6 + dx, 3.3), (1.95 + dx, 3.75), (2.35 + dx, 3.8)], closed=False), spl([(1.08 + dx, 3.95), (0.75 + dx, 4.35), (0.55 + dx, 4.35)], closed=False),
                 spl([(1.2 + dx, 4.65), (1.65 + dx, 4.75), (1.9 + dx, 5.0)], closed=False), spl([(1.95 + dx, 2.8), (2.35 + dx, 3.05), (2.6 + dx, 2.95)], closed=False)]
        return [beam] + tines
    ants = antler(1, 0.0) + antler(1, -0.35)
    ants = [tube(a_, 0.1) for a_ in ants[:5]] + [tube(a_, 0.1) for a_ in ants[5:]]
    ants = ants[:5] + hide(ants[5:], ants[:5] + [head])
    snow = [ground(-2.6, 3.2, -1.55)]
    return make("Caribou with Great Antlers", near + farl + hooves + hide(ear, [head]) + ear[:0] + tail + mane + ants + snow, [eye(2.25, 2.3, 0.06)])


@design("polar_arctic_wolf", T)
def arctic_wolf(rng):
    body = spl([(*(1.4, 3.4), 0), (1.15, 3.05), (0.8, 2.85), (0.55, 2.9), (*(0.2, 3.4), 0), (0.05, 2.9), (-0.3, 2.55), (-0.6, 1.8),
                (-1.0, 0.8), (-1.45, 0.0), (-1.55, -0.6), (-1.9, -0.75), (-2.4, -0.8), (*(-2.8, -1.0), 0), (-2.2, -1.12),
                (*(-1.0, -1.12), 0), (*(0.15, -1.12), 0), (0.05, -0.95), (-0.5, -0.8), (-0.55, -0.4), (-0.2, -0.3), (0.25, -0.5),
                (*(0.25, -1.12), 0), (*(0.95, -1.12), 0), (0.75, -0.9), (0.72, 0.4), (0.82, 1.2), (*(1.0, 1.45), 0), (0.95, 1.7),
                (*(1.15, 1.9), 0), (1.05, 2.2), (1.2, 2.6), (*(1.55, 3.05), 0), (*(1.25, 2.95), 0), (1.45, 3.25)], res=16)
    det = [arc(1.38, 3.36, 0.08, -0.5, 2.6, 8), spl([(0.4, 3.25), (0.3, 3.0), (0.2, 2.95)], closed=False),
           spl([(-0.9, 0.2), (-0.5, 0.0), (-0.3, -0.35)], closed=False)]
    moon = circle(-1.0, 2.8, 1.5, 90)
    rock = [spl([(-3.0, -1.12), (-2.8, -1.6), (-1.0, -1.75), (1.2, -1.7), (2.6, -1.5), (2.9, -1.12)], closed=False), [(-3.0, -1.12), (2.9, -1.12)][:0]]
    rock = [spl([(-3.2, -1.9), (-2.9, -1.2), (-2.4, -1.12)], closed=False), spl([(1.0, -1.12), (2.4, -1.15), (2.9, -1.6), (3.1, -1.9)], closed=False)]
    stars = [star(x, y, 0.15) for x, y in [(2.3, 3.4), (2.8, 2.2), (1.8, 4.0), (-2.9, 4.0)]]
    return make("Arctic Wolf Howling at the Moon", [body] + det + hide([moon], [body]) + rock + stars, [eye(0.75, 3.0, 0.05)])


@design("polar_arctic_hare", T)
def arctic_hare(rng):
    body = spl([(*(1.15, 2.2), 0), (0.95, 2.6), (0.65, 2.75), (0.45, 2.9), (0.3, 3.8), (*(0.2, 4.6), 0), (0.05, 3.8), (0.1, 2.85),
                (-0.15, 2.5), (-0.6, 1.6), (-1.0, 0.6), (-1.25, -0.2), (-1.55, -0.1), (*(-1.75, -0.4), 0), (-1.4, -0.7),
                (*(-1.0, -1.0), 0), (*(0.6, -1.0), 0), (0.5, -0.8), (-0.1, -0.7), (0.15, -0.3), (0.55, 0.3), (*(0.6, -0.3), 0),
                (*(0.95, -0.3), 0), (0.9, 0.1), (0.75, 0.7), (0.65, 1.4), (0.85, 1.85), (1.05, 2.0)], res=16)
    ear2 = spl([(0.55, 2.85), (0.65, 3.6), (*(0.65, 4.4), 0), (0.45, 3.6)], closed=False)
    ear_in = [spl([(0.2, 3.0), (0.2, 3.7), (0.2, 4.3)], closed=False)]
    det = [arc(1.12, 2.2, 0.07, -1.0, 2.0, 8), [(1.1, 2.1), (1.0, 2.0)], spl([(-0.9, 0.3), (-0.4, 0.2), (-0.1, -0.4)], closed=False)]
    whisk = [[(1.05, 2.15 - 0.08 * k), (1.5, 2.25 - 0.15 * k)] for k in range(3)]
    tail = [circle(-1.35, -0.3, 0.25, 20)][:0]
    hills = [spl([(-3.0, -1.0), (-1.4, -0.95), (1.4, -1.05), (3.0, -0.98)], closed=False), spl([(-3.0, 0.5), (-1.8, 1.1), (-1.0, 0.7)], closed=False),
             spl([(1.2, 0.6), (2.2, 1.2), (3.0, 0.8)], closed=False)]
    return make("Arctic Hare Sitting Up", [body] + hide([ear2], [body]) + ear_in + det + whisk + hide(hills, [body]), [eye(0.72, 2.45, 0.07)])


@design("polar_lemming", T)
def lemming(rng):
    body = spl([(2.0, 0.2), (1.95, 0.6), (1.6, 0.95), (1.4, 1.15), (*(1.25, 1.28), 0), (1.1, 1.12), (0.5, 1.35), (-0.6, 1.3), (-1.4, 0.9),
                (-1.7, 0.3), (*(-2.0, 0.15), 0), (-1.6, -0.15), (*(-1.2, -0.35), 0), (*(-0.6, -0.35), 0), (-0.6, -0.15), (0.6, -0.15),
                (*(0.65, -0.35), 0), (*(1.25, -0.35), 0), (1.2, -0.15), (1.6, -0.05), (1.9, 0.05)], res=16)
    det = [arc(1.98, 0.32, 0.08, -1.0, 2.0, 8), arc(1.25, 1.1, 0.09, 0.3, 3.0, 8)]
    whisk = [[(1.9, 0.25 - 0.08 * k), (2.4, 0.35 - 0.15 * k)] for k in range(3)]
    fur = [spl([(0.0, 1.2), (-0.1, 0.9)], closed=False), spl([(-0.6, 1.1), (-0.7, 0.8)], closed=False)]
    grass = []
    for x in (-2.8, -2.5, 2.6, 2.9):
        grass.append([(x, -0.35), (x + 0.05, 1.4)])
        grass.append(ellipse(x + 0.05, 1.6, 0.18, 0.24, 16))
    berries = [circle(x, y, 0.13, 12) for x, y in [(-2.2, -0.15), (-1.95, -0.05)]] + [lens((-2.4, -0.2), (-2.0, 0.25), 0.3, 8)]
    moss = [spl([(-3.0, -0.35), (-1.5, -0.4), (1.0, -0.33), (3.2, -0.38)], closed=False)]
    rock = [spl([(2.0, -0.35), (2.2, 0.0), (2.6, 0.05), (2.8, -0.35)], closed=False)]
    return make("Lemming on the Tundra", [body] + det + whisk + fur + grass + berries + moss + hide(rock, [body]), [eye(1.55, 0.7, 0.07)])


@design("polar_ermine", T)
def ermine(rng):
    body = spl([(*(1.25, 2.55), 0), (1.05, 2.85), (0.8, 2.95), (*(0.65, 3.2), 0), (0.45, 3.0), (0.2, 2.7), (-0.05, 2.0), (-0.2, 1.0),
                (-0.45, 0.2), (-0.7, -0.5), (*(-1.0, -0.95), 0), (*(-0.3, -0.95), 0), (-0.25, -0.75), (0.1, -0.6), (0.2, -0.75),
                (*(0.25, -0.95), 0), (*(0.75, -0.95), 0), (0.55, -0.5), (0.4, 0.4), (0.45, 1.3), (0.6, 1.65), (*(0.85, 1.55), 0),
                (*(0.95, 1.7), 0), (0.65, 1.95), (0.7, 2.25), (1.0, 2.4)], res=16)
    tail = spl([(-0.6, -0.4), (-1.3, -0.6), (-2.0, -0.4), (-2.4, 0.0), (*(-2.75, 0.3), 0), (-2.25, -0.35), (-1.4, -0.85), (-0.7, -0.75)], closed=False)
    tip = [spl([(-2.0, -0.4), (-2.05, -0.62)], closed=False)]
    det = [arc(1.22, 2.58, 0.06, -1.0, 2.0, 8), arc(0.6, 3.0, 0.08, 0.3, 3.0, 8)]
    whisk = [[(1.15, 2.55 - 0.08 * k), (1.6, 2.65 - 0.15 * k)] for k in range(3)]
    log = [spl([(-3.0, -0.95), (3.0, -0.95)], closed=False), spl([(1.2, -0.95), (1.5, -0.4), (2.6, -0.3), (3.0, -0.95)], closed=False)]
    rings = [ellipse(2.2, -0.55, 0.25, 0.15, 16)]
    return make("Ermine in Its White Winter Coat", [body] + hide([tail], [body]) + tip + det + whisk + log + rings, [eye(0.95, 2.72, 0.05)])


@design("polar_wolverine", T)
def wolverine(rng):
    body = spl([(*(2.7, 0.55), 0), (2.45, 0.85), (2.05, 1.05), (*(1.9, 1.25), 0), (1.75, 1.05), (1.2, 1.2), (0.0, 1.45), (-1.2, 1.3),
                (-1.7, 1.0), (-2.0, 0.9), (-2.6, 1.0), (*(-3.0, 0.75), 0), (-2.5, 0.6), (-1.95, 0.55), (-1.8, 0.1), (-1.6, -0.45),
                (*(-1.75, -0.7), 0), (*(-1.0, -0.7), 0), (-1.05, -0.5), (-1.0, 0.0), (-0.3, 0.05), (0.8, 0.05), (1.05, -0.45),
                (*(0.95, -0.7), 0), (*(1.75, -0.7), 0), (1.6, -0.45), (1.6, 0.0), (1.9, 0.25), (2.35, 0.3), (2.6, 0.42)], res=16)
    stripe = [spl([(1.4, 0.75), (0.5, 0.85), (-0.5, 0.78), (-1.3, 0.55), (-1.65, 0.2)], closed=False)]
    farlegs = hide([limb([(0.5, 0.3), (0.35, -0.3), (0.3, -0.6)], 0.38, 0.32), limb([(-0.6, 0.3), (-0.75, -0.3), (-0.8, -0.6)], 0.4, 0.32)], [body])
    claws = [[(1.75 - 0.15 * k, -0.7), (1.85 - 0.15 * k, -0.85)] for k in range(3)] + [[(-1.0 - 0.15 * k, -0.7), (-0.9 - 0.15 * k, -0.85)] for k in range(3)]
    det = [arc(2.68, 0.55, 0.08, -1.0, 2.0, 8), arc(1.88, 1.1, 0.08, 0.3, 3.0, 8)]
    trees = []
    for x, s_ in [(-2.6, 1.0), (2.7, 0.8)]:
        trees.append(poly((x, 1.4 + 2.2 * s_), (x + 0.6 * s_, 1.4 + 1.2 * s_), (x + 0.3 * s_, 1.4 + 1.2 * s_), (x + 0.8 * s_, 1.4), (x - 0.8 * s_, 1.4),
                          (x - 0.3 * s_, 1.4 + 1.2 * s_), (x - 0.6 * s_, 1.4 + 1.2 * s_)))
    snow = [spl([(-3.2, -0.85), (-1.0, -0.8), (1.5, -0.88), (3.2, -0.82)], closed=False)]
    return make("Wolverine on the Prowl", [body] + stripe + farlegs + claws + det + hide(trees, [body]) + snow, [eye(2.15, 0.78, 0.06)])


# ------------------------------------------------------------ birds

def flyer(body, wing_up, wing_down=None):
    out = [body]
    out += hide([wing_up], [body])
    if wing_down:
        out += hide([wing_down], [body, wing_up])
    return out


@design("polar_ptarmigan", T)
def ptarmigan(rng):
    body = spl([(*(2.0, 1.75), 0), (1.75, 2.05), (1.4, 2.15), (1.05, 1.95), (0.8, 1.45), (0.0, 1.35), (-1.0, 1.25), (*(-2.2, 1.5), 0),
                (-1.8, 1.0), (-1.2, 0.5), (-0.4, 0.0), (0.4, -0.05), (1.1, 0.3), (1.45, 0.9), (1.6, 1.4), (1.8, 1.6)], res=16)
    wing = [spl([(0.6, 1.2), (-0.3, 1.1), (-1.3, 0.95), (*(-1.7, 0.85), 0), (-1.0, 0.55), (0.1, 0.55), (0.6, 0.85)], closed=False)]
    tail_band = [[(-1.95, 1.3), (-1.65, 0.95)]]
    comb = [lens((1.25, 1.95), (1.65, 1.97), 0.35, 10)]
    feet = [spl([(0.1, 0.0), (0.0, -0.5), (*(-0.15, -0.65), 0), (0.3, -0.65), (0.35, -0.4), (0.5, 0.0)], closed=False),
            spl([(0.6, 0.1), (0.7, -0.45), (*(0.6, -0.65), 0), (1.05, -0.65), (1.0, -0.4), (0.95, 0.15)], closed=False)]
    beak = [[(2.0, 1.75), (1.72, 1.78)]]
    snow = [spl([(-3.0, -0.65), (-1.0, -0.6), (1.5, -0.68), (3.0, -0.6)], closed=False)]
    willow = [[(2.5, -0.65), (2.6, 0.6)], lens((2.55, 0.0), (2.95, 0.3), 0.3, 8), lens((2.58, 0.35), (2.25, 0.65), 0.3, 8), lens((2.6, 0.6), (2.7, 1.0), 0.3, 8)]
    return make("Rock Ptarmigan in Winter White", [body] + wing + tail_band + comb + hide(feet, [body]) + beak + snow + willow, [eye(1.5, 1.8, 0.06)])


@design("polar_arctic_tern", T)
def arctic_tern(rng):
    body = spl([(*(2.4, 0.35), 0), (1.85, 0.45), (1.5, 0.55), (0.8, 0.35), (-0.5, 0.1), (-1.4, -0.05), (*(-2.8, 0.45), 0), (-1.6, -0.2),
                (*(-2.7, -0.55), 0), (-1.3, -0.3), (0.0, -0.3), (1.0, -0.2), (1.6, 0.1), (1.9, 0.22)], res=16)
    cap = [spl([(1.95, 0.42), (1.6, 0.25), (1.15, 0.38)], closed=False)]
    wing1 = spl([(0.7, 0.3), (0.0, 1.2), (-0.8, 2.1), (*(-1.6, 2.9), 0), (-0.6, 1.6), (-0.1, 0.5)], closed=True)
    wing2 = spl([(0.6, -0.1), (0.9, -0.9), (1.4, -1.7), (*(1.8, -2.4), 0), (0.9, -1.4), (0.2, -0.25)], closed=True)
    waves = [sea(-2.4, -3.4, 3.4, 0.08, 6), sea(-2.9, -3.4, 3.4, 0.06, 5)]
    fish = [lens((2.25, 0.3), (2.7, 0.15), 0.3, 8)]
    return make("Arctic Tern in Flight", flyer(body, wing1, wing2) + cap + waves + fish, [eye(1.75, 0.33, 0.05)])


@design("polar_albatross", T)
def albatross(rng):
    body = spl([(*(1.9, 0.15), 0), (1.6, 0.4), (1.2, 0.45), (0.5, 0.3), (-0.6, 0.2), (*(-1.3, 0.1), 0), (-0.6, -0.1), (0.5, -0.25), (1.3, -0.15)], res=16)
    beak = [spl([(1.9, 0.15), (1.6, 0.05), (1.25, 0.1)], closed=False), arc(1.85, 0.08, 0.08, -1.5, 1.5, 6)]
    wing = spl([(0.6, 0.25), (-0.4, 0.55), (-1.8, 0.9), (-3.0, 1.05), (*(-3.8, 0.95), 0), (-2.8, 0.75), (-1.6, 0.45), (-0.3, 0.0)], closed=True)
    wing2 = spl([(0.6, 0.2), (1.3, 0.65), (2.4, 1.15), (3.4, 1.45), (*(4.0, 1.5), 0), (3.2, 1.2), (2.2, 0.75), (1.0, 0.1)], closed=True)
    tips = [[(-3.2, 0.85), (-2.8, 1.0)], [(3.4, 1.3), (3.6, 1.45)]]
    swell = [spl([(-3.8, -1.2), (-2.4, -0.7), (-1.4, -1.4), (0.2, -0.9), (1.6, -1.5), (3.0, -0.95), (4.0, -1.3)], closed=False),
             spl([(-3.8, -2.0), (-2.0, -1.7), (0.0, -2.1), (2.0, -1.75), (4.0, -2.1)], closed=False)]
    return make("Wandering Albatross Gliding", flyer(body, wing2, wing) + beak + swell, [eye(1.45, 0.25, 0.05)])


@design("polar_snow_petrel", T)
def snow_petrel(rng):
    def petrel(dx, dy, s, rot):
        body = spl([(*(1.0, 0.1), 0), (0.75, 0.32), (0.3, 0.3), (-0.5, 0.12), (*(-1.0, 0.0), 0), (-0.5, -0.12), (0.3, -0.18), (0.8, -0.05)], res=20)
        w1 = spl([(0.3, 0.2), (-0.1, 0.8), (*(-0.6, 1.5), 0), (-0.2, 0.7), (-0.3, 0.1)], closed=True)
        w2 = spl([(0.2, -0.1), (0.3, -0.7), (*(0.1, -1.3), 0), (-0.1, -0.6), (-0.3, -0.05)], closed=True)
        st = flyer(body, w1, w2)
        g = lambda p: transform(p, dx, dy, s, rot)  # noqa: E731
        return [g(p) for p in st], [g(eye(0.62, 0.15, 0.04))]
    berg = [spl([(-3.4, -1.5), (-3.0, 0.2), (-2.4, 0.6), (-1.8, 1.4), (-1.2, 0.8), (-0.6, 0.9), (-0.2, -0.2), (0.3, -1.5)], closed=False),
            [(-2.4, 0.6), (-2.0, -0.3)], [(-1.2, 0.8), (-1.0, -0.4)]]
    sea_ = [sea(-1.5, -3.6, 3.6, 0.07, 7)]
    a, ha = petrel(1.2, 1.4, 1.3, 0.2)
    b, hb = petrel(2.4, -0.2, 0.9, -0.15)
    c, hc = petrel(-0.8, 2.6, 0.75, 0.1)
    return make("Snow Petrels by an Iceberg", a + b + c + berg + sea_, ha + hb + hc)


@design("polar_snow_geese", T)
def snow_geese(rng):
    def goose(dx, dy, s):
        body = spl([(*(1.6, 0.18), 0), (1.38, 0.3), (1.15, 0.26), (0.65, 0.16), (0.3, 0.26), (-0.6, 0.26), (*(-1.05, 0.08), 0),
                    (-0.5, -0.25), (0.3, -0.25), (0.7, 0.0), (1.1, 0.12), (1.38, 0.1)], res=20)
        w = spl([(0.3, 0.22), (0.0, 0.9), (-0.3, 1.5), (*(-0.65, 1.75), 0), (-0.65, 1.2), (-0.5, 0.22)], closed=True)
        w2 = spl([(0.25, -0.15), (0.1, -0.7), (*(-0.25, -1.1), 0), (-0.35, -0.6), (-0.4, -0.15)], closed=True)
        tip = [[(-0.62, 1.45), (-0.35, 1.32)]]
        st = flyer(body, w, w2) + tip
        return [transform(p, dx, dy, s) for p in st], [transform(eye(1.3, 0.2, 0.04), dx, dy, s)]
    st, hi = [], []
    for x, y, s_ in [(1.6, 0.6, 1.0), (0.2, 1.5, 0.9), (0.4, -0.5, 0.9), (-1.2, 2.3, 0.8), (-1.0, -1.4, 0.8), (-2.5, 3.0, 0.7), (-2.4, -2.2, 0.7)]:
        a, h_ = goose(x, y, s_)
        st += a
        hi += h_
    clouds = [spl([(1.5, 3.0), (1.8, 3.4), (2.3, 3.35), (2.6, 3.6), (3.1, 3.3), (3.3, 3.0)], closed=False)]
    return make("Snow Geese Flying in a V", st + clouds, hi)


@design("polar_gyrfalcon", T)
def gyrfalcon(rng):
    body = spl([(*(1.15, 2.6), 0), (1.0, 2.95), (0.6, 3.15), (0.2, 3.0), (-0.1, 2.5), (-0.5, 1.5), (-0.85, 0.3), (*(-1.2, -1.2), 0),
                (*(-0.55, -1.25), 0), (-0.15, 0.0), (0.35, 0.3), (0.65, 1.0), (0.8, 1.9), (0.9, 2.35), (1.05, 2.45)], res=16)
    wing = [spl([(0.15, 2.5), (-0.3, 1.8), (-0.65, 0.6), (*(-1.0, -0.7), 0), (-0.25, 0.4), (0.25, 1.4), (0.45, 2.0)], closed=False)]
    beak = [spl([(1.15, 2.6), (1.0, 2.5), (0.95, 2.62)], closed=False)]
    tooth = [spl([(0.75, 2.75), (0.6, 2.5), (0.7, 2.35)], closed=False)]
    marks = [poly((-0.1 + 0.15 * k, 1.5 - 0.35 * k), (0.0 + 0.15 * k, 1.42 - 0.35 * k), closed=False)[:0] for k in range(3)]
    chev = [[(x - 0.1, y), (x, y - 0.08), (x + 0.1, y)] for x, y in [(0.35, 1.2), (0.15, 0.7), (0.45, 0.75), (0.25, 0.25), (-0.4, 1.1), (-0.5, 0.5)]]
    feet = [spl([(0.2, 0.1), (0.15, -0.3), (*(0.45, -0.4), 0)], closed=False), spl([(0.4, 0.2), (0.4, -0.25), (*(0.7, -0.38), 0)], closed=False)]
    rock = [spl([(-3.0, -2.6), (-2.6, -1.2), (-1.6, -0.6), (-0.6, -0.4), (0.8, -0.4), (2.0, -0.8), (2.8, -1.6), (3.0, -2.6)], closed=False)]
    cracks = [[(-1.0, -0.5), (-0.6, -1.3), (-0.9, -2.0)], [(1.6, -0.65), (2.0, -1.4)]]
    return make("Gyrfalcon on a Rocky Perch", hide([body], []) + hide(wing, []) + beak + tooth + chev + hide(feet, [body]) + hide(rock, [body]) + cracks, [eye(0.72, 2.75, 0.06)])


@design("polar_eider", T)
def eider(rng):
    body = spl([(*(2.6, 1.0), 0), (2.25, 1.4), (1.8, 1.75), (1.35, 1.65), (1.15, 1.2), (0.6, 0.85), (-0.6, 0.85), (-1.6, 0.75), (*(-2.3, 0.85), 0),
                (-1.9, 0.3), (-1.2, -0.1), (0.4, -0.2), (1.4, 0.0), (1.75, 0.45), (2.05, 0.85)], res=16)
    cap = [spl([(2.12, 1.38), (1.75, 1.45), (1.4, 1.35)], closed=False)]
    wing = [spl([(1.0, 0.7), (0.0, 0.65), (-1.0, 0.55), (*(-1.6, 0.45), 0), (-0.8, 0.25), (0.4, 0.3)], closed=False)]
    side = [spl([(1.2, 0.3), (0.0, 0.2), (-1.2, 0.15)], closed=False)]
    water = [sea(0.0, -3.2, 3.2, 0.07, 6), sea(-0.6, -2.6, 2.6, 0.06, 5), sea(-1.2, -2.0, 2.0, 0.06, 4)]
    below = [poly((-3.4, 0.0), (3.4, 0.0), (3.4, -2.0), (-3.4, -2.0))]
    duckling = spl([(*(-2.3, 0.3), 0), (-2.45, 0.55), (-2.7, 0.6), (-2.85, 0.35), (-3.3, 0.3), (-3.1, 0.0), (-2.4, 0.0)], res=30)
    return make("Common Eider Duck", hide([body] + wing + side, below) + cap + water, [eye(1.95, 1.5, 0.06)])


# ------------------------------------------------------------ sea life

@design("polar_krill_swarm", T)
def krill_swarm(rng):
    def krill(dx, dy, s, rot):
        body = spl([(*(1.2, 0.15), 0), (0.9, 0.35), (0.2, 0.35), (-0.5, 0.25), (-1.0, 0.05), (*(-1.25, -0.2), 0), (-0.9, -0.15),
                    (-0.3, -0.1), (0.4, -0.1), (1.0, 0.0)], res=20)
        segs = [[(x, 0.33 - 0.05 * abs(x)), (x - 0.05, -0.1)] for x in (0.4, 0.0, -0.4)]
        legs = [[(x, -0.1), (x - 0.1, -0.45)] for x in (0.7, 0.45, 0.2, -0.05)]
        ant = [quad((1.15, 0.2), (1.6, 0.6), (2.0, 0.5), 8), quad((1.1, 0.25), (1.4, 0.9), (1.9, 1.0), 8)]
        tail = [poly((-1.25, -0.2), (-1.5, 0.05), (-1.5, -0.4), (-1.25, -0.2), closed=False)]
        g = lambda p: transform(p, dx, dy, s, rot)  # noqa: E731
        return [g(p) for p in [body] + segs + legs + ant + tail], [g(eye(0.95, 0.2, 0.06))]
    st, hi = [], []
    for x, y, s_, r in [(0.0, 0.0, 1.0, 0.1), (-1.9, 1.6, 0.7, -0.2), (1.7, 1.9, 0.65, 0.3), (-1.8, -1.8, 0.75, 0.2), (1.8, -1.6, 0.7, -0.1),
                        (-0.2, 2.6, 0.5, 0.0), (2.6, 0.3, 0.5, 0.4), (-2.8, 0.1, 0.5, -0.3)]:
        a, h_ = krill(x, y, s_, r)
        st += a
        hi += h_
    return make("Antarctic Krill Swarm", st + bubbles([(0.8, 1.2, 0.1), (-0.9, -0.8, 0.12), (0.5, -1.0, 0.08)]), hi)


def fish(body_pts, fins, dx=0.0, dy=0.0, s=1.0):
    body = spl(body_pts, res=16)
    return [transform(p, dx, dy, s) for p in [body] + hide(fins, [body])]


@design("polar_toothfish", T)
def toothfish(rng):
    body = spl([(3.0, 0.0), (2.8, 0.4), (2.2, 0.75), (1.0, 0.9), (-0.5, 0.7), (-2.0, 0.35), (-2.5, 0.2), (*(-3.1, 0.7), 0), (-2.9, 0.0),
                (*(-3.1, -0.65), 0), (-2.5, -0.2), (-2.0, -0.35), (-0.5, -0.65), (1.0, -0.75), (2.2, -0.6), (*(2.95, -0.15), 0), (*(2.4, -0.15), 0), (2.95, -0.08)], res=16)
    fins = [spl([(1.2, 0.85), (0.8, 1.35), (0.2, 1.4), (-0.1, 0.85)], closed=False), spl([(-0.3, 0.75), (-0.6, 1.2), (-1.8, 1.0), (-2.1, 0.35)], closed=False),
            spl([(-0.3, -0.65), (-0.6, -1.05), (-1.8, -0.85), (-2.1, -0.35)], closed=False), lens((1.5, -0.1), (0.7, -0.5), 0.35, 12)]
    gill = [spl([(1.95, 0.6), (1.75, 0.0), (1.95, -0.55)], closed=False)]
    line = [spl([(1.8, 0.4), (0.0, 0.35), (-2.3, 0.05)], closed=False)]
    teeth = [zigzag(2.45, 2.9, -0.15, 0.04, 3)]
    rays = [[(x, 2.8), (x - 0.5, 1.8)] for x in (-1.5, 0.0, 1.5)]
    floor = [spl([(-3.4, -2.2), (-1.5, -1.8), (0.4, -2.3), (2.2, -1.9), (3.4, -2.2)], closed=False)]
    weed = [spl([(-2.5, -1.95), (-2.7, -1.2), (-2.4, -0.6)], closed=False), spl([(2.6, -2.0), (2.8, -1.3), (2.5, -0.9)], closed=False)]
    return make("Antarctic Toothfish", [body] + hide(fins, [body]) + gill + line + teeth + rays + floor + weed, [eye(2.4, 0.35, 0.08)])


@design("polar_arctic_char", T)
def arctic_char(rng):
    body = spl([(2.9, 0.1), (2.6, 0.55), (1.8, 0.85), (0.5, 0.95), (-1.0, 0.7), (-2.2, 0.25), (*(-3.0, 0.85), 0), (-2.75, 0.0),
                (*(-3.0, -0.8), 0), (-2.2, -0.25), (-1.0, -0.6), (0.5, -0.8), (1.8, -0.6), (2.5, -0.3), (2.85, -0.05)], res=16)
    fins = [spl([(0.6, 0.92), (0.3, 1.5), (-0.4, 1.45), (-0.5, 0.85)], closed=False), lens((-1.4, 0.55), (-1.75, 0.85), 0.35, 8),
            lens((1.5, -0.2), (0.8, -0.6), 0.35, 12), spl([(0.0, -0.75), (-0.3, -1.2), (-0.7, -0.7)], closed=False),
            spl([(-1.1, -0.6), (-1.3, -0.95), (-1.6, -0.45)], closed=False)]
    gill = [spl([(1.9, 0.62), (1.7, 0.0), (1.9, -0.5)], closed=False)]
    mouth = [quad((2.85, 0.0), (2.6, -0.05), (2.45, 0.05), 8)]
    spots = [circle(x, y, 0.1, 10) for x, y in [(1.0, 0.5), (0.5, 0.2), (0.0, 0.55), (-0.5, 0.25), (-1.0, 0.4), (1.2, 0.05), (-0.2, -0.15), (-1.5, 0.05)]]
    belly = [spl([(1.6, -0.45), (0.4, -0.55), (-1.2, -0.35)], closed=False)]
    stones = [spl([(-3.4, -1.9), (-2.8, -1.5), (-2.2, -1.9)], closed=False), spl([(-1.0, -1.95), (-0.4, -1.55), (0.4, -1.95)], closed=False),
              spl([(1.4, -1.9), (2.1, -1.45), (2.9, -1.9)], closed=False), [(-3.4, -1.95), (3.4, -1.95)]]
    return make("Arctic Char", [body] + hide(fins, [body]) + gill + mouth + spots + belly + stones, [eye(2.4, 0.38, 0.08)])


@design("polar_sea_angel", T)
def sea_angel(rng):
    body = spl([(0.0, 2.2), (0.45, 2.0), (0.5, 1.5), (0.35, 1.1), (0.45, 0.2), (0.35, -1.0), (0.0, -1.9), (-0.35, -1.0), (-0.45, 0.2),
                (-0.35, 1.1), (-0.5, 1.5), (-0.45, 2.0)], res=16)
    wing_r = spl([(0.38, 1.15), (1.2, 1.6), (2.0, 1.3), (*(2.3, 0.8), 0), (1.4, 0.75), (0.45, 0.85)], closed=True)
    wing_l = mirror_x(wing_r)
    gut = [spl([(0.0, 0.0), (0.22, -0.4), (0.15, -1.0), (0.0, -1.3), (-0.15, -1.0), (-0.22, -0.4), (0.0, 0.0)], closed=False)]
    neck = [spl([(-0.38, 1.12), (0.0, 1.05), (0.38, 1.12)], closed=False)]
    horns = [quad((0.2, 2.1), (0.4, 2.5), (0.55, 2.6), 8), quad((-0.2, 2.1), (-0.4, 2.5), (-0.55, 2.6), 8)]
    bub = bubbles([(1.6, 2.6, 0.13), (-1.8, 2.2, 0.1), (1.9, -1.0, 0.12), (-1.5, -1.6, 0.15), (2.4, 2.0, 0.08)])
    small = [transform(p, 2.4, -2.0, 0.35) for p in [body, wing_r, wing_l]]
    return make("Sea Angel", [body, wing_r, wing_l] + gut + neck + horns + bub + small, [eye(0.18, 1.7, 0.06), eye(-0.18, 1.7, 0.06)])


# dropped: the subject repeats another book
def lions_mane(rng):
    bell = spl([(-2.2, 1.0), (-1.8, 2.0), (-0.9, 2.6), (0.0, 2.75), (0.9, 2.6), (1.8, 2.0), (2.2, 1.0)], closed=False)
    rim = zigzag(-2.2, 2.2, 1.0, 0.1, 11)
    lobes = [arc(-1.6 + 0.8 * k, 1.05, 0.4, math.pi, 2 * math.pi, 10) for k in range(5)]
    arms = [spl([(-0.6 + 0.4 * k, 0.8), (-0.8 + 0.5 * k, 0.0), (-0.5 + 0.35 * k, -0.8), (-0.7 + 0.45 * k, -1.4)], closed=False) for k in range(4)]
    tent = []
    for k in range(9):
        x0 = -2.0 + 0.5 * k
        tent.append(spl([(x0, 0.95), (x0 + 0.25 * math.sin(k), -0.3), (x0 - 0.2, -1.4), (x0 + 0.2 * math.cos(k), -2.4), (x0 - 0.1, -3.2)], closed=False))
    inner = [spl([(-1.4, 1.6), (0.0, 2.1), (1.4, 1.6)], closed=False)]
    arms = [tube(a_, 0.25) for a_ in arms]
    tent = hide(tent, arms)
    fish = [lens((2.3, -1.4), (3.1, -1.2), 0.25, 12), poly((2.3, -1.4), (2.05, -1.2), (2.05, -1.6), (2.3, -1.4), closed=False)]
    return make("Lion's Mane Jellyfish", [bell, rim] + inner + arms + tent + fish, [])


@design("polar_snow_crab", T)
def snow_crab(rng):
    shell = spl([(0.0, 1.3), (0.9, 1.15), (1.35, 0.6), (1.2, -0.1), (0.6, -0.5), (0.0, -0.55), (-0.6, -0.5), (-1.2, -0.1), (-1.35, 0.6), (-0.9, 1.15)], res=16)
    bumps = [circle(x, y, 0.1, 10) for x, y in [(0.0, 0.6), (0.5, 0.3), (-0.5, 0.3), (0.0, 0.0), (0.7, 0.75), (-0.7, 0.75)]]
    legs = []
    for k, (a0, a1) in enumerate([(0.55, 0.9), (0.15, 0.45), (-0.25, 0.0), (-0.6, -0.5)]):
        y0 = 0.6 - 0.35 * k
        knee = (1.3 + 1.0 * math.cos(a0), y0 + 1.0 * math.sin(a0))
        foot = (knee[0] + 1.2 * math.cos(a1 - 1.3), knee[1] + 1.2 * math.sin(a1 - 1.3))
        legs.append(tube([(1.15, y0), knee], 0.18))
        legs.append(tube([knee, foot], 0.13))
    legs += [mirror_x(l_) for l_ in legs]
    claws = [tube([(0.6, 1.05), (1.0, 1.7), (1.25, 2.1)], 0.22), poly((1.2, 2.0), (1.45, 2.5), (1.15, 2.3), closed=False)]
    claws += [mirror_x(c) for c in claws]
    eyes_ = [[(0.2, 1.25), (0.25, 1.55)], [(-0.2, 1.25), (-0.25, 1.55)]]
    floor = [spl([(-3.4, -2.6), (-1.0, -2.3), (1.4, -2.65), (3.4, -2.4)], closed=False)]
    out = [shell] + hide(legs + claws, [shell]) + bumps + eyes_ + floor
    return make("Snow Crab", out, [eye(0.25, 1.6, 0.07), eye(-0.25, 1.6, 0.07)])


@design("polar_penguin_diving", T)
def penguin_diving(rng):
    body = spl([(*(2.65, 0.15), 0), (2.25, 0.3), (2.0, 0.52), (1.65, 0.55), (1.35, 0.48), (0.4, 0.7), (-1.0, 0.45), (-1.9, 0.12),
                (*(-2.4, 0.0), 0), (-1.8, -0.2), (-0.6, -0.55), (0.8, -0.55), (1.6, -0.3), (2.0, -0.05), (2.25, 0.05)], res=16)
    belly = [spl([(1.7, -0.25), (0.5, -0.35), (-0.8, -0.3), (-1.7, -0.08)], closed=False)]
    flipper = [spl([(0.9, 0.2), (0.0, -0.4), (*(-0.9, -1.0), 0), (-0.2, -0.05)], closed=False)]
    patch = [spl([(1.4, 0.35), (1.15, 0.15), (1.3, -0.05)], closed=False)]
    feet = [poly((-2.0, -0.05), (-2.6, -0.3), (-2.3, 0.05), closed=False)]
    trail = bubbles([(-2.7, 0.3, 0.12), (-3.0, 0.7, 0.16), (-2.9, 1.2, 0.1), (-3.2, 1.6, 0.13)])
    g = lambda L: [transform(p, 0.0, 0.0, 1.0, -0.35) for p in L]  # noqa: E731
    surface = [sea(2.4, -3.4, 3.4, 0.08, 6)]
    rays = [[(x, 2.2), (x - 0.6, 0.6)] for x in (-1.0, 0.5, 2.0)]
    fishes = [lens((2.4, -1.6), (3.0, -1.45), 0.3, 10), lens((2.9, -2.1), (3.5, -1.95), 0.3, 10)]
    b = g([body])
    return make("Penguin Diving Underwater", b + g(belly + flipper + patch + feet + trail) + surface + hide(rays, b) + fishes, g([eye(1.85, 0.3, 0.06)]))


@design("polar_ringed_seal_den", T)
def ringed_seal_den(rng):
    dome = spl([(-3.0, -1.2), (-2.6, 0.8), (-1.2, 2.2), (0.6, 2.5), (2.2, 1.8), (3.0, 0.4), (3.2, -1.2)], closed=False)
    cave = spl([(-2.2, -1.2), (-1.9, 0.4), (-0.6, 1.35), (0.9, 1.45), (2.0, 0.7), (2.4, -1.2)], closed=False)
    pup = spl([(1.65, -0.5), (1.6, -0.1), (1.25, 0.25), (0.7, 0.3), (0.0, 0.05), (-0.9, -0.15), (*(-1.5, 0.05), 0), (-1.3, -0.4),
               (*(-1.6, -0.65), 0), (-0.8, -0.75), (0.5, -0.82), (1.3, -0.75)], res=16)
    face = [arc(1.62, -0.42, 0.06, -1.0, 2.0, 8), [(1.6, -0.55), (1.45, -0.58)]]
    whisk = [[(1.55, -0.45 - 0.07 * k), (1.95, -0.4 - 0.15 * k)] for k in range(3)]
    flip_ = [spl([(0.6, -0.4), (0.8, -0.65), (*(0.55, -0.8), 0)], closed=False)]
    rings = [ellipse(x, y, 0.15, 0.1, 12) for x, y in [(0.2, -0.1), (-0.3, -0.25), (0.6, 0.05)]]
    floor = [[(-3.4, -1.2), (3.4, -1.2)], [(-2.2, -0.9), (2.35, -0.9)]]
    hole = [ellipse(-1.4, -1.05, 0.4, 0.1, 20)]
    snow_top = [spl([(-3.4, 2.9), (-1.0, 3.2), (1.5, 3.0), (3.4, 3.2)], closed=False)]
    return make("Ringed Seal Pup in a Snow Den", [dome, cave, pup] + face + whisk + flip_ + rings + floor[:1] + hide(floor[1:], [pup]) + hide(hole, [pup]), [eye(1.25, -0.2, 0.06)])


# ------------------------------------------------------------ ice & scenes

@design("polar_iceberg", T)
def iceberg(rng):
    wl = 0.6
    above = spl([(-1.8, wl), (-1.6, 1.4), (-1.0, 1.6), (-0.7, 2.6), (*(-0.2, 3.3), 0), (0.3, 2.6), (0.8, 2.8), (*(1.3, 2.0), 0), (1.7, 1.5), (2.1, wl)], closed=False)
    below = spl([(-1.8, wl), (-2.6, -0.4), (-2.9, -1.6), (-2.2, -2.8), (-0.6, -3.3), (1.2, -3.0), (2.6, -2.0), (3.0, -0.8), (2.1, wl)], closed=False)
    facets = [[(-0.7, 2.6), (-0.3, 1.3), (0.3, 2.6)], [(0.8, 2.8), (0.9, 1.6)], [(-1.0, 1.6), (-0.9, 0.9)]]
    under_lines = [spl([(-2.2, -0.8), (-1.0, -1.6), (0.6, -1.4), (2.2, -1.8)], closed=False), spl([(-1.6, -2.5), (0.2, -2.6), (1.6, -2.3)], closed=False)]
    water = [wave(-3.4, -1.8, wl, 0.06, 2, 40), wave(2.1, 3.4, wl, 0.06, 2, 40)]
    fish_ = [lens((-3.0, -2.6), (-2.5, -2.45), 0.3, 10)]
    birds = [chain(arc(x - 0.15, y, 0.15, 0.3, math.pi - 0.2, 6), arc(x + 0.15, y, 0.15, 0.2, math.pi - 0.3, 6)) for x, y in [(1.8, 3.2), (2.4, 3.5)]]
    return make("Iceberg Above and Below the Waterline", [above, below] + facets + under_lines + water + fish_ + birds, [])


@design("polar_penguins_on_berg", T)
def penguins_on_berg(rng):
    top = 0.6
    berg = spl([(-3.0, -0.6), (-2.8, top), (-1.6, top + 0.1), (*(-1.4, top + 1.2), 0), (0.2, top + 1.25), (*(0.4, top), 0), (2.6, top), (3.0, -0.6)], closed=False)
    cracks = [[(-1.4, top + 1.2), (-1.2, top - 0.2), (-1.5, -0.4)], [(1.4, top), (1.6, -0.5)]]
    items = [penguin(-0.6, top + 1.25, 0.32), penguin(0.0, top + 1.25, 0.28, True), penguin(1.0, top, 0.36), penguin(1.8, top, 0.3, True),
             penguin(-2.3, top + 0.1, 0.3)]
    st, hi = scene(*items)
    water = [sea(-0.5, -3.4, 3.4, 0.07, 7), sea(-1.1, -3.0, 3.0, 0.06, 6)]
    berg = hide([berg], [s_ for it in items for s_ in it["sil"]])
    sun_ = [arc(-2.4, 2.9, 0.6, 0.0, TAU, 40)]
    return make("Penguins on a Drifting Iceberg", st + berg + cracks + hide(water, []) + sun_, hi)


@design("polar_glacier_calving", T)
def glacier_calving(rng):
    cliff = spl([(-3.4, 2.6), (-1.2, 2.5), (*(-0.4, 2.3), 0), (*(-0.5, 1.2), 0), (*(-0.2, 0.6), 0), (*(-0.4, -0.2), 0), (-0.3, -0.4)], closed=False)
    falling = spl([(*(0.1, 2.2), 0), (*(0.9, 2.5), 0), (*(1.2, 1.2), 0), (*(0.7, 0.0), 0), (*(0.2, 0.4), 0), (0.1, 2.2)], closed=False)
    lines = [spl([(-2.9, 2.55), (-2.7, 1.6), (-2.85, 0.6), (-2.7, -0.4)], closed=False), spl([(-2.1, 2.52), (-2.25, 1.4), (-2.05, 0.3)], closed=False),
             spl([(-1.3, 2.5), (-1.1, 1.5), (-1.25, 0.4), (-1.1, -0.4)], closed=False), [(0.5, 2.3), (0.8, 0.5)]]
    splash = [quad((0.0, -0.4), (0.2, 0.6), (-0.2, 0.9), 10), quad((1.0, -0.4), (1.4, 0.4), (1.8, 0.5), 10), quad((0.5, -0.4), (0.7, 0.3), (0.9, 0.2), 10)]
    drops = [circle(x, y, 0.1, 10) for x, y in [(-0.5, 1.0), (1.9, 0.9), (2.2, 0.3), (0.4, 1.0)][1:]]
    water = [wave(-0.3, 3.4, -0.4, 0.06, 5, 80), wave(-3.4, 3.4, -1.2, 0.07, 7, 120), wave(-3.4, 3.4, -2.0, 0.06, 7, 120)]
    peaks = [spl([(-3.4, 2.6), (-2.6, 3.6), (-1.8, 3.0), (-1.0, 3.9), (0.2, 3.0)], closed=False)]
    floes = [floe(1.8, 3.0, -0.8, 0.2), floe(-2.6, -1.6, -1.6, 0.18)]
    return make("Glacier Calving into the Sea", [cliff, falling] + lines + splash + drops + water + peaks + floes, [])


@design("polar_ice_cave", T)
def ice_cave(rng):
    outer = spl([(-3.2, -2.0), (-3.0, 0.8), (-2.2, 2.4), (-0.8, 3.1), (0.8, 3.1), (2.2, 2.4), (3.0, 0.8), (3.2, -2.0)], closed=False)
    inner = spl([(-2.2, -2.0), (-2.0, 0.4), (-1.3, 1.6), (0.0, 2.1), (1.3, 1.6), (2.0, 0.4), (2.2, -2.0)], closed=False)
    icicles = []
    for k in range(9):
        t = 0.12 + 0.76 * k / 8
        p = inner[int(t * (len(inner) - 1))]
        L = 0.35 + 0.25 * ((k * 7) % 3)
        icicles.append(poly((p[0] - 0.12, p[1] + 0.05), (p[0], p[1] - L), (p[0] + 0.12, p[1] + 0.05), closed=False))
    layers = [spl([(-3.05, 0.2), (-2.6, 0.3), (-2.05, 0.15)], closed=False), spl([(2.05, 0.6), (2.6, 0.7), (3.0, 0.5)], closed=False),
              spl([(-2.5, 1.9), (-1.9, 2.0), (-1.5, 1.85)], closed=False), spl([(1.6, 2.05), (2.0, 2.1), (2.4, 1.9)], closed=False)]
    mountains = [poly((-2.0, -0.6), (-1.0, 0.8), (-0.3, 0.0), (0.5, 1.2), (1.4, -0.1), (2.0, -0.6), closed=False)]
    mountains = hide(mountains, [])
    sun_ = [circle(0.9, 0.9, 0.0, 4)][:0]
    floor = [[(-3.4, -2.0), (3.4, -2.0)], spl([(-2.0, -1.2), (0.0, -1.0), (2.0, -1.25)], closed=False)]
    return make("Ice Cave Archway", [outer, inner] + hide(icicles, []) + layers + within(mountains, [inner + [inner[0]]]) + floor, [])


@design("polar_frozen_waterfall", T)
def frozen_waterfall(rng):
    left_cliff = spl([(-3.4, 3.2), (-2.4, 3.0), (-1.6, 2.6), (-1.5, 1.0), (-1.8, -0.5), (-2.0, -2.0)], closed=False)
    right_cliff = spl([(3.4, 3.0), (2.2, 2.8), (1.6, 2.5), (1.5, 0.8), (1.8, -0.8), (2.1, -2.0)], closed=False)
    cols = []
    for k in range(6):
        x = -1.25 + 0.5 * k
        cols.append(spl([(x, 2.6), (x + 0.1, 1.5), (x - 0.05, 0.4), (x + 0.08, -0.6), (*(x, -1.5 + 0.15 * (k % 2)), 0)], closed=False))
    top = [spl([(-1.6, 2.6), (0.0, 2.75), (1.6, 2.5)], closed=False)]
    base = [spl([(-2.0, -2.0), (-1.2, -1.4), (0.0, -1.2), (1.3, -1.45), (2.1, -2.0)], closed=False)]
    icicles = [poly((x - 0.1, 2.6), (x, 2.0), (x + 0.1, 2.6), closed=False) for x in (-2.3, -2.0, 2.0, 2.4)][:0]
    trees = []
    for x, y, s_ in [(-2.7, 3.1, 0.6), (2.7, 2.95, 0.55)]:
        trees.append(poly((x, y + 1.6 * s_), (x + 0.5 * s_, y + 0.7 * s_), (x + 0.25 * s_, y + 0.7 * s_), (x + 0.6 * s_, y), (x - 0.6 * s_, y),
                          (x - 0.25 * s_, y + 0.7 * s_), (x - 0.5 * s_, y + 0.7 * s_)))
    pool = [ellipse(0.0, -2.3, 2.0, 0.35, 60)]
    return make("Frozen Waterfall", [left_cliff, right_cliff] + cols + top + base + trees + pool, [])


@design("polar_research_station", T)
def research_station(rng):
    main = rect(-2.4, -0.2, 1.2, 1.2)
    legs = [[(x, -0.2), (x, -1.0)] for x in (-2.2, -1.2, -0.2, 0.9)]
    windows = [rrect(-2.1 + 0.8 * k, 0.4, -1.6 + 0.8 * k, 0.85, 0.08) for k in range(4)]
    dome = [arc(2.2, 0.0, 0.9, 0.0, math.pi, 40), [(1.3, 0.0), (3.1, 0.0)]]
    dome_lines = [arc(2.2, 0.0, 0.5, 0.0, math.pi, 20), [(2.2, 0.9), (2.2, 0.0)]]
    mast = [[(-1.8, 1.2), (-1.8, 3.0)], [(-2.1, 2.6), (-1.5, 2.6)], circle(-1.8, 3.1, 0.12, 12)]
    dish = [arc(0.2, 1.9, 0.5, math.radians(200), math.radians(340), 20), [(0.2, 1.4), (0.2, 1.2)], [(0.2, 1.4), (0.35, 1.75)]]
    flag = [[(2.2, 0.9), (2.2, 2.4)], rect(2.2, 1.9, 2.9, 2.35)]
    stairs = [[(1.2, -0.2), (1.6, -1.0)], [(1.35, -0.5), (1.0, -0.5)][:0]] + [[(1.2 + 0.1 * k, -0.2 - 0.2 * k), (1.35 + 0.1 * k, -0.2 - 0.2 * k)] for k in range(4)]
    snowmobile = [poly((-3.2, -0.75), (-2.9, -0.45), (-2.5, -0.45), (-2.4, -0.75)), [(-3.3, -0.95), (-2.3, -0.95)]]
    ground_ = [spl([(-3.4, -1.0), (-1.0, -0.95), (1.5, -1.05), (3.4, -0.98)], closed=False)]
    peaks = [spl([(-3.4, 1.0), (-2.9, 1.9), (-2.4, 1.2)], closed=False), spl([(1.2, 1.6), (2.0, 2.8), (2.6, 1.9), (3.0, 2.4), (3.4, 1.8)], closed=False)]
    peaks = hide(peaks, [main, dome[0] + [dome[0][0]], flag[1]])
    return make("Antarctic Research Station", [main] + legs + windows + dome + dome_lines + mast + dish + flag + stairs + snowmobile + ground_ + peaks, [])


@design("polar_night_moon", T)
def polar_night(rng):
    moon = circle(1.6, 2.4, 0.8, 60)
    craters = [circle(1.35, 2.6, 0.15, 12), circle(1.9, 2.2, 0.2, 14)]
    bergs = [spl([(-3.4, -0.2), (-3.0, 0.9), (-2.4, 1.3), (-1.8, 0.6), (-1.4, -0.2)], closed=False),
             spl([(-0.6, -0.2), (-0.4, 0.4), (0.4, 0.5), (0.6, -0.2)], closed=False),
             spl([(1.6, -0.2), (1.9, 0.6), (2.4, 0.9), (2.8, 0.3), (3.1, -0.2)], closed=False)]
    path = [[(1.6 + d, -0.5 - 0.4 * k), (1.6 + d + 0.6, -0.5 - 0.4 * k)] for k, d in enumerate([-0.2, -0.4, -0.1, -0.5, -0.2])]
    water = [[(-3.4, -0.2), (3.4, -0.2)]]
    stars = [star(x, y, 0.16) for x, y in [(-2.8, 3.2), (-1.6, 2.6), (-0.4, 3.4), (0.3, 2.2), (2.9, 3.4), (-2.2, 1.9), (3.1, 1.4)]]
    seal = spl([(0.2, 0.5), (0.4, 0.75), (0.15, 0.75), (-0.2, 0.55), (-0.4, 0.5)], closed=False)
    return make("Polar Night under the Moon", [moon] + craters + bergs + path + water + stars, [])
