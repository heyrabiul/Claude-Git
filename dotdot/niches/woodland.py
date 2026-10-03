"""Woodland Animals niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "woodland"


def make(title, parts, hints=()):
    for p in parts:
        if not isinstance(p[0], (tuple, list)):
            raise TypeError(f"{title}: a stroke was spread into points")
    return Design(title, [p for p in parts if len(p) > 1], list(hints), T)


# ------------------------------------------------------------------ curves

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


def _offsets(c, wf):
    n = len(c)
    left, right = [], []
    for i, (x, y) in enumerate(c):
        a = c[max(0, i - 1)]
        b = c[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        w = wf(i / (n - 1)) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return left, right


def limb(center, w0, w1=None, cap0=True, cap1=True, smooth=True):
    """Closed outline of a limb / tail / branch along a smooth centre line
    through the joints, width tapering from w0 to w1, with round ends."""
    c = spl(center, closed=False) if smooth else list(center)
    w1 = w0 if w1 is None else w1
    wf = w0 if callable(w0) else (lambda t: w0 + (w1 - w0) * t)
    left, right = _offsets(c, wf)
    out = list(left)
    if cap1:
        (x, y), (px, py) = c[-1], c[-2]
        a = math.atan2(left[-1][1] - y, left[-1][0] - x)
        out += arc(x, y, math.dist(left[-1], c[-1]), a, a - math.pi, 10)[1:-1]
    out += right[::-1]
    if cap0:
        x, y = c[0]
        a = math.atan2(left[0][1] - y, left[0][0] - x)
        out += arc(x, y, math.dist(left[0], c[0]), a + math.pi, a, 10)[1:-1]
    out.append(out[0])
    return out


def sides(center, w):
    """The two edges of a band along `center` (no end caps)."""
    left, right = _offsets(center, w if callable(w) else (lambda t: w))
    return [left, right]


def fringe(line, amp, teeth):
    """Zig-zag fur along a polyline (teeth to the left of travel)."""
    L = [0.0]
    for a, b in zip(line, line[1:]):
        L.append(L[-1] + math.dist(a, b))
    out, j = [], 0
    for k in range(2 * teeth + 1):
        d = L[-1] * k / (2 * teeth)
        while j < len(L) - 2 and L[j + 1] < d:
            j += 1
        a, b = line[j], line[j + 1]
        f = (d - L[j]) / ((L[j + 1] - L[j]) or 1)
        x, y = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
        ln = math.dist(a, b) or 1
        nx, ny = -(b[1] - a[1]) / ln, (b[0] - a[0]) / ln
        o = amp if k % 2 else 0.0
        out.append((x + nx * o, y + ny * o))
    return out


def leaf(p0, p1, bulge=0.3, vein=True):
    out = [lens(p0, p1, bulge)]
    if vein:
        out.append([p0, (p0[0] + (p1[0] - p0[0]) * 0.85, p0[1] + (p1[1] - p0[1]) * 0.85)])
    return out


def tuft(x, y, s=1.0):
    return [quad((x, y), (x + dx * 0.4 * s, y + h * 0.6 * s), (x + dx * s, y + h * s), 10)
            for dx, h in [(-0.35, 0.55), (0.0, 0.75), (0.35, 0.55)]]


def ripples(x0, x1, y, waves=3, amp=0.06):
    return wave(x0, x1, y, amp, waves, 60)


# ------------------------------------------------------------------ occlusion
# hide() removes the parts of strokes inside "cover" shapes (front objects),
# keep() clips a pattern to the inside of a shape, union() merges
# overlapping closed shapes into one silhouette.

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
        out += [g for g in segs if len(g) > 1 and _plen(g) > 0.08]
    return out


def hide(strokes, *covers):
    return _clip(strokes, covers)


def keep(strokes, *covers):
    return _clip(strokes, covers, True)


def join(strokes, tol=0.03):
    segs = [list(s) for s in strokes if len(s) > 1]
    out = []
    while segs:
        cur = segs.pop(0)
        changed = True
        while changed and math.dist(cur[0], cur[-1]) > tol:
            changed = False
            for i, s in enumerate(segs):
                if math.dist(cur[-1], s[0]) < tol:
                    cur = cur + s[1:]
                elif math.dist(cur[-1], s[-1]) < tol:
                    cur = cur + s[::-1][1:]
                elif math.dist(cur[0], s[-1]) < tol:
                    cur = s + cur[1:]
                elif math.dist(cur[0], s[0]) < tol:
                    cur = s[::-1] + cur[1:]
                else:
                    continue
                segs.pop(i)
                changed = True
                break
        if len(cur) > 2 and math.dist(cur[0], cur[-1]) < tol:
            cur[-1] = cur[0]
        out.append(cur)
    return out


def union(*shapes):
    out = []
    for i, s in enumerate(shapes):
        out += hide([s], *[o for j, o in enumerate(shapes) if j != i])
    return join(out)


def layer(*groups):
    """Stack groups of (strokes, covers) front to back: each group is hidden
    behind the covers of every group before it."""
    out, covers = [], []
    for strokes, cov in groups:
        out += hide(strokes, *covers) if covers else list(strokes)
        covers += list(cov)
    return out


def paw(x, y, rx=0.24, ry=0.12, toes=3, rot=0.0):
    """Rounded paw with little toe lines."""
    out = [ellipse(x, y, rx, ry, 30, rot=rot)]
    return out


def toe_lines(x, y, rx, ry, k=2, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    out = []
    for i in range(k):
        dx = rx * (-0.35 + 0.7 * (i + 1) / (k + 1)) * 1.4
        a = (x + dx * c - (-ry) * s, y + dx * s + (-ry) * c)
        b = (x + dx * c - (-ry * 0.2) * s, y + dx * s + (-ry * 0.2) * c)
        out.append([a, b])
    return out


def crown(cx, cy, rx, ry, bumps=9, amp=0.12, n=240, seed=0.0):
    return [(cx + rx * (1.0 + amp * abs(math.sin(bumps * t / 2 + seed))) * math.cos(t),
            cy + ry * (1.0 + amp * abs(math.sin(bumps * t / 2 + seed))) * math.sin(t)) for t in [TAU * i / n for i in range(n + 1)]]


def palm_frond(base, tip, bend=0.3, k=5, ll=0.75):
    mx, my = (base[0] + tip[0]) / 2, (base[1] + tip[1]) / 2
    dx, dy = tip[0] - base[0], tip[1] - base[1]
    ctrl = (mx - dy * bend, my + dx * bend)
    rib = quad(base, ctrl, tip, 20)
    out = [rib]
    for i in range(2, 2 + k):
        p = rib[int(len(rib) * i / (k + 2))]
        q = rib[int(len(rib) * i / (k + 2)) + 1]
        ux, uy = q[0] - p[0], q[1] - p[1]
        L = math.hypot(ux, uy)
        ux, uy = ux / L, uy / L
        for s in (1, -1):
            e = (p[0] + ll * (0.7 * ux - s * 0.7 * uy) * (1 - 0.06 * i), p[1] + ll * (0.7 * uy + s * 0.7 * ux) * (1 - 0.06 * i) - 0.12)
            out.append(lens(p, e, 0.18))
    return out


def pine(x, y0, h, w, tiers=4):
    """Simple layered pine tree outline with a trunk."""
    out = []
    pts = [(x, y0 + h)]
    for k in range(tiers):
        t = (k + 1) / tiers
        yy = y0 + h - h * 0.85 * t
        ww = w * (0.35 + 0.65 * t) / 2
        pts += [(x + ww, yy), (x + ww * 0.45, yy + 0.12)]
    pts = pts[:-1]
    right = pts
    left = [(2 * x - px, py) for px, py in right[::-1]]
    out.append(right + left[1:])
    out.append([(x - 0.1, y0 + h * 0.15 + 0.03), (x - 0.1, y0)])
    out.append([(x + 0.1, y0 + h * 0.15 + 0.03), (x + 0.1, y0)])
    return out


def bird_wing_m(x, y, s=0.15):
    return chain(arc(x - s, y, s, 0.3, 2.8, 6), arc(x + s, y, s, 0.3, 2.8, 6))


# ================================================================== burrowers

@design("woodland_badger_sett", T)
def badger_sett(rng):
    body = spl([(-1.2, -0.45), (-1.35, 0.2), (-0.9, 0.7), (0.2, 0.85), (1.0, 0.72), (1.45, 0.42), (1.5, -0.1), (1.0, -0.5), (0.0, -0.62)])
    head = spl([(1.2, 0.62), (1.7, 0.76), (2.15, 0.52), (2.6, 0.1), (2.68, -0.05), (2.45, -0.15), (1.9, -0.2), (1.45, -0.18)])
    ear = spl([(1.55, 0.7), (1.52, 0.95), (1.75, 0.98), (1.82, 0.72)])
    legs = [limb([(1.15, -0.2), (1.3, -0.7), (1.25, -1.0)], 0.48, 0.38), limb([(-0.75, -0.2), (-0.55, -0.7), (-0.7, -1.0)], 0.52, 0.38)]
    far = [limb([(0.75, -0.3), (0.8, -0.7), (0.7, -0.98)], 0.42, 0.34), limb([(-0.3, -0.3), (-0.15, -0.7), (-0.25, -0.98)], 0.45, 0.34)]
    tail = limb([(-1.25, 0.15), (-1.6, 0.05), (-1.75, -0.15)], 0.3, 0.2)
    front = [head, body, *legs, tail]
    sil = union(head, body, *legs, tail)
    back = hide(far, *front)
    ear_l = hide([ear], head)
    stripes = keep([spl([(2.55, 0.08), (2.1, 0.32), (1.6, 0.6)], closed=False), spl([(2.5, -0.05), (2.0, 0.08), (1.5, 0.2)], closed=False)], head)
    fur = keep([quad((-1.0 + 0.5 * k, 0.6), (-0.9 + 0.5 * k, 0.4), (-0.75 + 0.5 * k, 0.32), 6) for k in range(5)], body)
    claws = [[(1.42 + 0.08 * k, -1.08), (1.5 + 0.08 * k, -1.15)] for k in range(3)] + [[(-0.55 + 0.08 * k, -1.08), (-0.47 + 0.08 * k, -1.15)] for k in range(3)]
    nose = [ellipse(2.64, -0.05, 0.06, 0.05, 10)]
    G = -1.08
    mound = spl([(-3.3, G), (-3.0, 0.4), (-2.3, 1.05), (-1.4, 0.95), (-0.7, 0.2), (-0.2, G)], closed=False)
    hole = chain([(-2.85, G)], arc(-2.15, G, 0.7, math.pi, 0.0, 20)[1:], [(-1.45, G)])
    hole = [quad((-2.85, G), (-2.85, -0.05), (-2.15, 0.0), 10) + quad((-2.15, 0.0), (-1.45, -0.05), (-1.45, G), 10)[1:]]
    roots = [quad((-2.6, -0.05), (-2.55, -0.35), (-2.65, -0.55), 6), quad((-2.0, 0.0), (-1.95, -0.3), (-2.05, -0.45), 6)]
    ground = [[(-3.3, G), (3.3, G)]]
    scene = hide([mound] + hole + roots + ground, *front, *far)
    plants = tuft(2.6, G, 0.7) + tuft(0.4, G, 0.5) + leaf((-2.3, 1.0), (-2.6, 1.8), 0.25) + leaf((-2.3, 1.0), (-1.9, 1.7), 0.25)
    plants = hide(plants, *front, *far)
    return make("Badger at Its Sett", sil + back + ear_l + stripes + claws + nose + scene + plants, [eye(2.2, 0.2, 0.06)])


@design("woodland_beaver", T)
def beaver(rng):
    trunk_l = [(-1.95, 3.4), (-1.95, 0.45), (-1.72, 0.0), (-1.95, -0.45), (-1.95, -1.5)]
    trunk_r = [(-1.3, 3.4), (-1.3, 0.45), (-1.52, 0.0), (-1.3, -0.45), (-1.3, -1.5)]
    trunk_shape = poly(*(trunk_l + trunk_r[::-1]))
    body = spl([(0.1, 1.2), (0.9, 0.9), (1.25, 0.0), (1.1, -0.95), (0.5, -1.4), (-0.4, -1.4), (-0.75, -0.9), (-0.7, 0.0), (-0.4, 0.85)])
    head = spl([(0.3, 1.75), (-0.2, 1.98), (-0.75, 1.82), (-1.05, 1.48), (-1.15, 1.22), (-0.95, 1.0), (-0.5, 0.95), (0.2, 1.1)])
    ear = circle(0.12, 1.88, 0.14, 16)
    teeth = rect(-1.02, 0.86, -0.9, 1.04)
    arm = limb([(-0.25, 0.75), (-0.75, 0.55), (-1.25, 0.75)], 0.32, 0.26)
    foot = ellipse(-0.25, -1.48, 0.62, 0.16, 30)
    tail = ellipse(2.15, -1.42, 1.05, 0.28, 50, rot=0.05)
    tail_join = limb([(0.95, -1.1), (1.3, -1.35)], 0.4, 0.4)
    front = [arm, ear, head, body, foot, tail_join]
    sil = union(head, ear, body, foot, tail_join)
    sil = hide(sil, arm) + [arm]
    tl = hide([tail], *front)
    hatch = keep([[(1.3 + 0.3 * k, -1.8), (1.6 + 0.3 * k, -1.05)] for k in range(6)] + [[(1.6 + 0.3 * k, -1.8), (1.3 + 0.3 * k, -1.05)] for k in range(6)], tail)
    hatch = hide(hatch, *front)
    tr = hide([trunk_l, trunk_r], *front, teeth)
    fingers = [arc(-1.3, 0.72 + 0.1 * k, 0.08, 1.2, 4.6, 5) for k in (-1, 0, 1)]
    chips = [lens((-2.8, -1.5), (-2.45, -1.4), 0.35), lens((-0.9, -1.55), (-1.1, -1.45), 0.4), lens((-2.4, -1.6), (-2.2, -1.55), 0.4),
             lens((-0.6, -1.85), (-0.9, -1.8), 0.35)]
    whisk = [quad((-1.0, 1.15), (-1.3, 1.2), (-1.5, 1.3), 6), quad((-1.0, 1.1), (-1.3, 1.05), (-1.55, 1.05), 6)]
    nose = [ellipse(-1.08, 1.3, 0.07, 0.05, 10)]
    ground = [[(-3.3, -1.55), (-0.85, -1.55)], [(0.4, -1.55), (1.05, -1.55)]]
    water = [ripples(1.0, 3.4, -2.05, 3, 0.05), ripples(-0.5, 3.4, -2.5, 4, 0.05)]
    grain = keep([[(-1.72, 0.05), (-1.6, 0.0)]], trunk_shape)
    branchlet = [spl([(-1.3, 2.4), (-0.6, 2.9), (0.1, 3.05)], closed=False)] + leaf((0.1, 3.05), (0.6, 3.4), 0.3) + leaf((-0.5, 2.85), (-0.3, 3.4), 0.3)
    return make("Beaver Gnawing a Tree", sil + [teeth] + tl + hatch + tr + fingers + chips + whisk + nose + ground + water + branchlet,
                [eye(-0.55, 1.55, 0.07)])


@design("woodland_mole", T)
def mole(rng):
    G = -2.0
    mound = spl([(-3.3, G, 0), (-2.6, -1.1), (-1.5, -0.35), (0.0, -0.1), (1.5, -0.35), (2.6, -1.1), (3.3, G, 0)], closed=False)
    mound_c = mound + [(3.3, G - 1), (-3.3, G - 1), mound[0]]
    body = spl([(-1.0, -1.0), (-0.95, 0.5), (-0.5, 1.4), (0.3, 1.85), (1.1, 1.95), (1.8, 1.8), (2.35, 1.6), (2.7, 1.5), (2.72, 1.32),
                (2.35, 1.15), (1.6, 0.85), (1.1, 0.2), (0.9, -1.0)])
    hand = spl([(0.95, 0.15), (1.7, 0.0), (2.05, -0.3), (1.85, -0.6), (1.2, -0.65), (0.8, -0.3)])
    claws = [quad((1.98 + 0.0 * k, -0.15 - 0.12 * k), (2.25, -0.15 - 0.13 * k), (2.35, -0.28 - 0.13 * k), 6) for k in range(4)]
    hand2 = spl([(-0.9, -0.05), (-1.6, -0.2), (-1.95, -0.45), (-1.75, -0.75), (-1.15, -0.72), (-0.85, -0.45)])
    claws2 = [quad((-1.88 - 0.0 * k, -0.3 - 0.12 * k), (-2.15, -0.3 - 0.13 * k), (-2.25, -0.42 - 0.13 * k), 6) for k in range(3)]
    sil = hide([body], hand, hand2, mound_c) + [hand, hand2]
    md = hide([mound], hand, hand2, body)
    nose = [ellipse(2.68, 1.42, 0.08, 0.1, 10)]
    whisk = [quad((2.5, 1.45), (2.85, 1.7), (3.15, 1.8), 6), quad((2.5, 1.4), (2.9, 1.38), (3.25, 1.35), 6), quad((2.45, 1.35), (2.8, 1.15), (3.05, 1.0), 6)]
    fur = keep([quad((-0.6, 0.6), (0.0, 1.3), (0.9, 1.6), 10), quad((-0.7, -0.1), (-0.3, 0.6), (0.4, 0.95), 10)], body)
    fur = hide(fur, hand, hand2, mound_c)
    clods = [ellipse(x, y, r, r * 0.7, 14) for x, y, r in [(-2.2, -1.5, 0.15), (-1.3, -1.1, 0.13), (1.4, -1.1, 0.13), (2.3, -1.45, 0.16),
                                                            (0.2, -0.85, 0.12), (-0.6, -1.5, 0.14), (0.9, -1.6, 0.12)]]
    clods = hide(clods, hand, hand2)
    ground = [[(-3.3, G), (3.3, G)]]
    grass = tuft(-3.0, G, 0.6) + tuft(3.0, G, 0.6)
    return make("Mole Popping Out of Its Molehill", sil + claws + claws2 + md + nose + whisk + fur + clods + ground + grass,
                [eye(2.0, 1.62, 0.045)])


@design("woodland_shrew", T)
def shrew(rng):
    body = spl([(-1.9, -0.3), (-1.9, 0.4), (-1.2, 1.0), (0.0, 1.2), (0.9, 1.05), (1.5, 0.78), (2.3, 0.42), (3.2, 0.14), (3.38, 0.08),
                (3.3, 0.0), (2.8, -0.02), (2.0, -0.08), (1.2, -0.3), (0.0, -0.55), (-1.2, -0.5)])
    ear = spl([(0.95, 0.95), (0.95, 1.12), (1.15, 1.12), (1.2, 0.95)])
    legs = [limb([(1.0, -0.15), (1.2, -0.6), (1.4, -0.75)], 0.28, 0.2), limb([(-1.2, -0.3), (-0.9, -0.65), (-0.75, -0.78)], 0.36, 0.22)]
    tail = limb([(-1.8, 0.0), (-2.35, -0.1), (-2.7, -0.3)], 0.22, 0.14)
    front = [body, *legs]
    sil = union(body, *legs, tail)
    ear_l = hide([ear], body)
    whisk = [quad((3.0, 0.15), (3.3, 0.4), (3.6, 0.5), 6), quad((3.0, 0.1), (3.3, 0.15), (3.65, 0.2), 6), quad((3.0, 0.05), (3.25, -0.1), (3.55, -0.2), 6)]
    feet = [[(1.4, -0.75), (1.6, -0.8)], [(-0.75, -0.78), (-0.55, -0.82)]]
    fur = keep([quad((-1.4, 0.6), (-0.5, 0.95), (0.5, 0.95), 10), quad((-1.6, 0.0), (-0.6, 0.35), (0.6, 0.3), 10)], body)
    G = -0.85
    ground = [[(-3.3, G), (3.3, G)]]
    leaves = [lens((-2.6, G), (-1.6, G + 0.1), 0.3), lens((1.8, G), (2.9, G + 0.05), 0.3), lens((-0.4, G), (0.5, G - 0.05), 0.3)]
    leaves = hide(leaves, *front)
    beetle = [ellipse(2.8, -0.55, 0.22, 0.15, 20), circle(3.05, -0.55, 0.07, 10), [(2.8, -0.4), (2.8, -0.7)]]
    acorn = []
    ferns = palm_frond((-2.8, G), (-2.2, 1.8), -0.15) + palm_frond((2.5, G), (2.9, 2.0), 0.15)
    ferns = hide(ferns, *front)
    return make("Long-Nosed Shrew", sil + ear_l + whisk + feet + fur + ground + leaves + beetle + ferns, [eye(1.45, 0.6, 0.06)])


@design("woodland_dormouse", T)
def dormouse(rng):
    ball = circle(-0.1, 0.25, 1.15, 80)
    head = spl([(0.55, 1.05), (1.05, 1.1), (1.4, 0.75), (1.45, 0.3), (1.15, 0.0), (0.7, 0.05), (0.45, 0.4)])
    ear = circle(0.75, 1.12, 0.2, 20)
    tail = limb([(-1.15, -0.2), (-1.35, 0.8), (-0.8, 1.55), (0.2, 1.65), (0.9, 1.45)], 0.42, 0.34)
    paws = [ellipse(0.85, -0.1, 0.17, 0.1, 12), ellipse(0.5, -0.4, 0.17, 0.1, 12)]
    front = [tail, *paws, head, ear, ball]
    sil = hide(union(ball, head, ear), tail, *paws) + hide([tail], *[]) + paws
    sil = hide(union(ball, head, ear), tail, *paws) + [tail] + paws
    tail_fur = keep([[(-1.3 + 0.0, 0.3 + 0.35 * k), (-1.05, 0.25 + 0.35 * k)] for k in range(3)] +
                    [[(-0.6 + 0.35 * k, 1.6), (-0.65 + 0.35 * k, 1.35)] for k in range(4)], tail)
    lid = [quad((0.95, 0.62), (1.08, 0.55), (1.2, 0.62), 6)]
    nose = [circle(1.42, 0.45, 0.05, 8)]
    ear_in = hide([circle(0.75, 1.12, 0.1, 12)], head, tail)
    nest = []
    nest_shape = spl([(-2.3, 0.4), (-2.0, -0.7), (-1.0, -1.35), (0.5, -1.4), (1.7, -0.9), (2.2, 0.2), (1.9, -0.2), (0.5, -0.6), (-1.0, -0.6),
                      (-1.9, -0.1)])
    weave = []
    for k in range(5):
        y = -0.25 - 0.25 * k
        weave.append(wave(-2.4 + 0.12 * k * k, 2.3 - 0.12 * k * k, y, 0.06, 4, 40))
    weave = keep(weave, nest_shape)
    nest = [nest_shape] + weave
    nest = hide(nest, *front)
    zs = [[(1.6, 1.4), (1.85, 1.4), (1.6, 1.15), (1.85, 1.15)], [(2.05, 1.85), (2.4, 1.85), (2.05, 1.5), (2.4, 1.5)],
          [(2.6, 2.4), (3.05, 2.4), (2.6, 1.95), (3.05, 1.95)]]
    twig = [spl([(-3.3, -1.6), (-1.0, -1.65), (1.5, -1.5), (3.3, -1.7)], closed=False), spl([(-3.3, -1.85), (-1.0, -1.9), (1.5, -1.75), (3.3, -1.95)], closed=False)]
    twig = hide(twig, nest_shape)
    lvs = leaf((2.8, -1.65), (3.2, -0.6), 0.3) + leaf((-2.8, -1.7), (-3.2, -0.7), 0.3)
    return make("Dormouse Asleep in Its Nest", sil + tail_fur + lid + nose + ear_in + nest + zs + twig + lvs)


@design("woodland_skunk", T)
def skunk(rng):
    body = spl([(-1.45, -0.35), (-1.6, 0.35), (-1.0, 0.95), (0.2, 1.05), (1.0, 0.85), (1.4, 0.45), (1.3, -0.1), (0.6, -0.45), (-0.7, -0.45)])
    head = spl([(1.15, 0.75), (1.55, 0.92), (2.0, 0.78), (2.45, 0.4), (2.6, 0.22), (2.45, 0.1), (2.0, 0.05), (1.5, 0.1), (1.2, 0.3)])
    ear = spl([(1.5, 0.88), (1.48, 1.12), (1.7, 1.12), (1.75, 0.88)])
    tail = spl([(-1.4, 0.25), (-2.25, 0.85), (-2.45, 1.85), (-2.0, 2.75), (-1.0, 3.15), (0.1, 2.95), (0.55, 2.45), (0.05, 2.5),
                (-0.8, 2.45), (-1.35, 1.95), (-1.4, 1.3), (-1.0, 0.75)])
    legs = [limb([(1.0, 0.0), (1.1, -0.55), (1.05, -0.85)], 0.4, 0.32), limb([(-1.0, 0.0), (-0.85, -0.55), (-1.0, -0.85)], 0.45, 0.32)]
    far = [limb([(0.6, -0.1), (0.6, -0.55), (0.55, -0.82)], 0.36, 0.3), limb([(-0.55, -0.1), (-0.4, -0.55), (-0.5, -0.82)], 0.4, 0.3)]
    front = [head, tail, body, *legs]
    sil = union(head, tail, body, *legs)
    back = hide(far, *front)
    ear_l = hide([ear], head)
    stripe = keep([spl([(2.2, 0.6), (1.4, 0.95), (0.3, 1.0), (-0.9, 0.7), (-1.5, 0.9)], closed=False),
                   spl([(2.2, 0.55), (1.4, 0.7), (0.3, 0.65), (-0.9, 0.45), (-1.45, 0.6)], closed=False),
                   spl([(-1.5, 0.75), (-1.95, 1.4), (-1.85, 2.3), (-1.1, 2.85), (-0.1, 2.75)], closed=False)], body, head, tail)
    nose = [ellipse(2.57, 0.2, 0.06, 0.05, 10)]
    claws = [[(1.2 + 0.07 * k, -0.9), (1.27 + 0.07 * k, -0.96)] for k in range(3)]
    G = -0.9
    ground = [[(-3.3, G), (3.3, G)]]
    flowers = []
    for x, h in [(2.6, 0.9), (3.0, 0.6), (-2.9, 0.7)]:
        flowers += [[(x, G), (x, G + h)], circle(x, G + h + 0.15, 0.15, 14)]
        flowers += [circle(x + 0.25 * math.cos(a), G + h + 0.15 + 0.25 * math.sin(a), 0.1, 10) for a in [TAU * k / 5 for k in range(5)]]
    flowers = hide(flowers, *front)
    return make("Striped Skunk", sil + back + ear_l + stripe + nose + claws + ground + flowers, [eye(2.05, 0.5, 0.06)])


@design("woodland_opossum", T)
def opossum(rng):
    branch = limb([(-3.3, 2.5), (0.0, 2.6), (3.3, 2.45)], 0.42, 0.36, cap0=False, cap1=False)
    tail = limb([(-0.15, 0.95), (-0.25, 1.7), (-0.15, 2.25)], 0.22, 0.16, cap1=False)
    curl = [arc(0.05, 2.58, 0.33, math.pi * 1.0, math.pi * 1.0 - TAU * 0.85, 24), arc(0.05, 2.58, 0.2, math.pi * 0.95, math.pi * 0.95 - TAU * 0.8, 18)]
    body = spl([(-0.15, 1.15), (0.45, 0.85), (0.6, 0.0), (0.45, -0.8), (0.0, -1.1), (-0.5, -0.8), (-0.7, 0.0), (-0.6, 0.85)])
    head = spl([(-0.45, -0.85), (0.15, -0.9), (0.55, -1.2), (0.85, -1.6), (1.15, -2.05), (1.2, -2.2), (1.0, -2.2), (0.55, -2.0), (0.0, -1.85),
                (-0.45, -1.5)])
    ears = [circle(-0.35, -1.0, 0.22, 20), circle(0.25, -0.95, 0.2, 20)]
    legs = [limb([(0.35, -0.5), (0.95, -0.85), (1.3, -0.7)], 0.24, 0.18), limb([(-0.45, -0.55), (-1.05, -0.95), (-1.4, -0.8)], 0.24, 0.18),
            limb([(0.35, 0.65), (0.9, 0.9), (1.0, 1.4)], 0.26, 0.2), limb([(-0.5, 0.65), (-1.05, 0.95), (-1.1, 1.45)], 0.26, 0.2)]
    hands = []
    for x, y in [(1.3, -0.7), (-1.4, -0.8), (1.0, 1.4), (-1.1, 1.45)]:
        hands += [limb([(x, y), (x + 0.2 * math.cos(a), y + 0.2 * math.sin(a))], 0.07, 0.06) for a in (0.6, 1.5, 2.4)]
    front = [ears[0], ears[1], head, body, tail, *legs, *hands]
    sil = union(head, body, tail, *legs, *hands)
    sil = hide(sil, *ears) + ears
    face = [quad((-0.1, -1.2), (0.3, -1.5), (0.7, -1.4), 8)]
    face = []
    nose = [ellipse(1.12, -2.13, 0.07, 0.06, 10)]
    whisk = [quad((1.0, -2.05), (1.3, -1.9), (1.5, -1.85), 6), quad((1.0, -2.1), (1.3, -2.15), (1.55, -2.15), 6)]
    br = hide([branch], *[ellipse(0.05, 2.58, 0.35, 0.35, 24)])
    fur = keep([quad((-0.4, 0.5), (0.0, 0.2), (0.3, -0.3), 8), quad((-0.5, -0.1), (-0.2, -0.5), (0.1, -0.8), 8)], body)
    leaves = leaf((-2.4, 2.55), (-2.9, 1.5), 0.28) + leaf((-2.0, 2.55), (-1.6, 3.4), 0.28) + leaf((2.4, 2.5), (2.9, 1.5), 0.28) + leaf((2.0, 2.5), (2.2, 3.4), 0.28)
    leaves = hide(leaves, branch)
    return make("Opossum Hanging by Its Tail", sil + curl + br + nose + whisk + fur + leaves,
                [eye(0.55, -1.55, 0.07)])


@design("woodland_lynx", T)
def lynx(rng):
    head = spl([(0.0, 2.0), (0.75, 1.85), (1.05, 1.3), (0.85, 0.75), (0.0, 0.5), (-0.85, 0.75), (-1.05, 1.3), (-0.75, 1.85)])
    ruff = []
    for s in (1, -1):
        ruff.append(fringe(spl([(s * 0.95, 1.35), (s * 1.25, 0.95), (s * 1.1, 0.5), (s * 0.5, 0.25)], closed=False), 0.16 * s, 5))
    ears = [spl([(0.4, 1.9), (0.75, 2.65, 0), (0.95, 1.6)]), spl([(-0.4, 1.9), (-0.75, 2.65, 0), (-0.95, 1.6)])]
    tufts = [[(0.75, 2.65), (0.72, 3.0)], [(-0.75, 2.65), (-0.72, 3.0)]]
    body = spl([(0.0, 0.6), (0.9, 0.3), (1.3, -0.8), (1.3, -2.0), (0.8, -2.55), (0.0, -2.6), (-0.8, -2.55), (-1.3, -2.0), (-1.3, -0.8), (-0.9, 0.3)])
    legs = [limb([(0.45, 0.0), (0.5, -1.4), (0.45, -2.45)], 0.48, 0.4), limb([(-0.45, 0.0), (-0.5, -1.4), (-0.45, -2.45)], 0.48, 0.4)]
    paws = [ellipse(0.48, -2.55, 0.36, 0.18, 24), ellipse(-0.48, -2.55, 0.36, 0.18, 24)]
    haunch = [ellipse(1.15, -1.95, 0.55, 0.6, 30), ellipse(-1.15, -1.95, 0.55, 0.6, 30)]
    front = [head, *ears, *legs, *paws, body, *haunch]
    sil = union(head, *ears, body, *haunch, *legs, *paws)
    sil += [[(0.0, -0.75), (0.0, -2.5)], [(0.93, -1.0), (0.93, -2.3)], [(-0.93, -1.0), (-0.93, -2.3)]]
    sil += [fringe(spl([(-0.5, 0.35), (0.0, 0.1), (0.5, 0.35)], closed=False), -0.14, 4)]
    ruff = hide(ruff, head)
    ear_in = [[(0.6, 1.95), (0.75, 2.35)], [(-0.6, 1.95), (-0.75, 2.35)]]
    muzzle = [chain(quad((0.0, 0.95), (0.15, 0.8), (0.4, 0.82), 6)), chain(quad((0.0, 0.95), (-0.15, 0.8), (-0.4, 0.82), 6)),
              [(0.0, 1.12), (0.0, 0.95)], poly((-0.12, 1.2), (0.12, 1.2), (0.0, 1.08))]
    spots = keep([circle(x, y, 0.07, 8) for x, y in [(0.4, -0.6), (0.55, -1.0), (0.4, -1.4), (-0.4, -0.6), (-0.55, -1.0), (-0.4, -1.4),
                                                      (1.1, -1.7), (-1.1, -1.7), (1.25, -2.1), (-1.25, -2.1)]], *legs, *haunch)
    toes = [[(0.4 + 0.12 * k, -2.73), (0.4 + 0.12 * k, -2.6)] for k in (-1, 0, 1)] + [[(-0.4 - 0.12 * k, -2.73), (-0.4 - 0.12 * k, -2.6)] for k in (-1, 0, 1)]
    toes = [[(0.48 + 0.13 * k, -2.73), (0.48 + 0.13 * k, -2.6)] for k in (-1, 1)] + [[(-0.48 + 0.13 * k, -2.73), (-0.48 + 0.13 * k, -2.6)] for k in (-1, 1)]
    bg = pine(-2.6, -2.75, 4.8, 1.3, 5) + pine(2.6, -2.75, 4.2, 1.2, 4)
    bg = hide(bg, *front)
    ground = [[(-3.3, -2.75), (-1.5, -2.75)], [(1.5, -2.75), (3.3, -2.75)]]
    return make("Lynx with Tufted Ears", sil + ruff + tufts + ear_in + muzzle + spots + toes + bg + ground,
                [eye(0.4, 1.35, 0.08), eye(-0.4, 1.35, 0.08)])


# ================================================================== larger mammals

@design("woodland_grey_wolf", T)
def grey_wolf(rng):
    body = spl([(-1.6, 0.35), (-1.5, 0.95), (-0.5, 1.15), (0.6, 1.2), (1.2, 1.4), (1.65, 1.15), (1.75, 0.5), (1.35, 0.0), (0.4, 0.05),
                (-0.8, 0.15), (-1.5, 0.05)])
    head = spl([(1.3, 1.4), (1.65, 1.82), (2.05, 1.88), (2.45, 1.65), (3.0, 1.38), (3.2, 1.22), (3.1, 1.06), (2.6, 1.0), (2.2, 0.95),
                (1.75, 0.8), (1.45, 0.9)])
    ears = [spl([(1.65, 1.78), (1.68, 2.3, 0), (1.98, 1.86)]), spl([(1.82, 1.84), (1.92, 2.3, 0), (2.12, 1.84)])]
    ruff = fringe(spl([(2.25, 0.95), (1.85, 0.6), (1.6, 0.2)], closed=False), -0.15, 4)
    legs = [limb([(1.35, 0.3), (1.45, -0.5), (1.4, -1.3)], 0.4, 0.24), limb([(-1.15, 0.35), (-0.8, -0.35), (-1.25, -0.8), (-1.15, -1.3)], 0.55, 0.24)]
    far = [limb([(1.0, 0.2), (0.85, -0.5), (0.95, -1.28)], 0.36, 0.22), limb([(-0.7, 0.3), (-0.35, -0.35), (-0.75, -0.8), (-0.65, -1.28)], 0.5, 0.22)]
    paws = [ellipse(1.52, -1.35, 0.22, 0.1, 20), ellipse(-1.05, -1.35, 0.22, 0.1, 20)]
    fpaws = [ellipse(1.05, -1.33, 0.2, 0.09, 20), ellipse(-0.55, -1.33, 0.2, 0.09, 20)]
    tail = spl([(-1.5, 0.9), (-2.0, 0.6), (-2.35, -0.1), (-2.45, -0.65, 0), (-2.2, -0.5), (-1.95, -0.25), (-1.6, 0.3)])
    front = [head, *ears, body, *legs, *paws, tail]
    sil = union(head, *ears, body, *legs, *paws, tail)
    sil = hide(sil, *[]) + [ruff]
    back = hide(far + fpaws, *front)
    face = [quad((2.25, 1.6), (2.5, 1.45), (2.75, 1.4), 8), ellipse(3.15, 1.18, 0.06, 0.05, 10), quad((3.1, 1.05), (2.8, 1.02), (2.6, 1.08), 6)]
    ear_in = [[(1.75, 1.85), (1.72, 2.1)]]
    fur = keep([quad((-1.2, 0.85), (-0.5, 0.75), (0.2, 0.85), 8), quad((0.4, 1.0), (0.9, 0.9), (1.3, 1.05), 8)], body)
    G = -1.42
    ground = [[(-3.3, G), (3.3, G)]]
    bg = pine(-2.9, G, 4.2, 1.1, 4) + pine(2.85, G, 3.8, 1.0, 4) + pine(-0.2, G + 1.9, 2.0, 0.7, 3)
    bg = hide(bg, *front, *far)
    return make("Grey Wolf Among the Pines", sil + back + face + ear_in + fur + ground + bg, [eye(2.32, 1.55, 0.06)])


@design("woodland_bear_cub", T)
def bear_cub(rng):
    trunk = [spl([(-1.15, -3.0), (-1.05, 0.0), (-1.15, 3.4)], closed=False), spl([(-0.05, -3.0), (0.0, 0.0), (-0.1, 3.4)], closed=False)]
    body = ellipse(0.6, -0.15, 0.8, 1.15, 70, rot=-0.15)
    head = circle(0.7, 1.25, 0.58, 50)
    ears = [circle(0.22, 1.72, 0.18, 20), circle(1.15, 1.75, 0.18, 20)]
    muzzle = ellipse(0.72, 1.03, 0.27, 0.19, 24)
    arm = limb([(0.3, 0.55), (-0.05, 1.25), (-0.45, 1.6)], 0.38, 0.32)
    arm2 = limb([(0.95, 0.4), (0.6, 0.0), (-0.35, 0.3)], 0.34, 0.3)
    leg = limb([(0.75, -0.95), (0.3, -1.4), (-0.3, -1.3)], 0.48, 0.36)
    front = [arm, head, *ears, leg, arm2, body]
    sil = union(head, *ears, body, leg, arm2)
    sil = hide(sil, arm) + [arm]
    claws = []
    for x, y in [(-0.45, 1.6), (-0.35, 0.3), (-0.3, -1.3)]:
        claws += [quad((x - 0.05, y + 0.12 * k), (x - 0.25, y + 0.12 * k + 0.02), (x - 0.32, y + 0.12 * k - 0.06), 4) for k in (-1, 0, 1)]
    tr = hide(trunk, *front)
    bark = hide([spl([(-0.6, 3.2), (-0.5, 2.3), (-0.65, 1.2)], closed=False), spl([(-0.6, -0.5), (-0.5, -1.6), (-0.65, -2.6)], closed=False),
                 [(-0.85, 2.0), (-0.75, 1.6)], [(-0.35, -2.1), (-0.25, -2.5)]], *front)
    ear_in = hide([circle(0.22, 1.72, 0.09, 10), circle(1.15, 1.75, 0.09, 10)], head)
    nose = [ellipse(0.72, 1.1, 0.09, 0.06, 10)]
    mouth = [quad((0.6, 0.93), (0.72, 0.88), (0.84, 0.93), 6)]
    branch = [spl([(-0.05, 2.4), (1.0, 2.75), (2.2, 2.85), (3.2, 3.1)], closed=False), spl([(-0.05, 2.15), (1.0, 2.5), (2.2, 2.6), (3.2, 2.85)], closed=False)]
    lv = leaf((1.6, 2.7), (2.0, 2.0), 0.28) + leaf((2.6, 2.8), (3.0, 2.1), 0.28) + leaf((2.2, 2.75), (2.3, 3.5), 0.28)
    ground = [[(-3.3, -3.0), (3.3, -3.0)]]
    grass = tuft(1.5, -3.0, 0.7) + tuft(-2.3, -3.0, 0.7) + tuft(2.7, -3.0, 0.5)
    return make("Black Bear Cub Climbing a Tree", sil + [muzzle] + claws + tr + bark + ear_in + nose + mouth + branch + lv + ground + grass,
                [eye(0.5, 1.35, 0.07), eye(0.92, 1.35, 0.07)])


@design("woodland_brown_bear", T)
def brown_bear(rng):
    body = spl([(-0.3, -1.45), (-0.75, -0.6), (-0.9, 0.6), (-0.6, 1.6), (0.0, 2.1), (0.6, 2.15), (0.98, 1.8), (1.05, 1.0), (0.88, 0.0),
                (0.62, -1.0), (0.4, -1.5)])
    head = spl([(0.5, 2.45), (0.88, 2.75), (1.35, 2.72), (1.72, 2.48), (2.12, 2.28), (2.18, 2.08), (1.82, 1.96), (1.3, 1.86), (0.78, 1.92)])
    ear = circle(0.88, 2.75, 0.18, 20)
    arm = limb([(0.72, 1.55), (1.25, 1.05), (1.35, 0.6)], 0.52, 0.42)
    paw = ellipse(1.4, 0.45, 0.25, 0.22, 20)
    thigh = ellipse(0.05, -0.95, 0.68, 0.82, 50)
    leg = limb([(0.05, -1.2), (0.15, -2.2), (0.12, -2.55)], 0.62, 0.5)
    foot = ellipse(0.4, -2.68, 0.55, 0.16, 30)
    far_leg = limb([(-0.35, -1.3), (-0.55, -2.2), (-0.6, -2.55)], 0.55, 0.45)
    far_foot = ellipse(-0.35, -2.68, 0.5, 0.15, 30)
    far_arm = limb([(0.4, 1.4), (0.7, 0.8), (0.6, 0.35)], 0.45, 0.38)
    front = [arm, paw, head, ear, body, thigh, leg, foot]
    sil = union(head, ear, body, thigh, leg, foot)
    sil = hide(sil, arm, paw) + hide(union(arm, paw), *[])
    back = hide([far_leg, far_foot, far_arm], *front)
    claws = [quad((1.45 + 0.1 * k, 0.28), (1.5 + 0.1 * k, 0.12), (1.45 + 0.1 * k, 0.05), 4) for k in (-1, 0, 1)]
    claws += [quad((0.85 + 0.0, -2.65 + 0.08 * k), (1.0, -2.68 + 0.08 * k), (1.05, -2.75 + 0.08 * k), 4) for k in (0, 1)]
    face = [ellipse(2.15, 2.2, 0.07, 0.06, 10), quad((2.05, 2.02), (1.85, 1.98), (1.7, 2.04), 6)]
    ear_in = hide([circle(0.88, 2.75, 0.09, 10)], head)
    fur = keep([quad((-0.6, 1.2), (-0.3, 0.6), (-0.4, 0.0), 8), quad((-0.2, 1.75), (0.3, 1.4), (0.4, 0.9), 8)], body)
    fur = hide(fur, arm, thigh)
    thigh_l = hide(keep([thigh], body), arm)
    G = -2.85
    ground = [[(-3.3, G), (3.3, G)]]
    bg = pine(-2.4, G, 5.6, 1.4, 5) + pine(2.6, G, 4.6, 1.2, 4)
    bg = hide(bg, *front, far_leg, far_foot)
    grass = tuft(-1.2, G, 0.6) + tuft(1.6, G, 0.6)
    return make("Brown Bear Standing Tall", sil + back + claws + face + ear_in + fur + ground + bg + grass, [eye(1.45, 2.38, 0.07)])


@design("woodland_wild_boar", T)
def wild_boar(rng):
    body = spl([(-1.9, 0.2), (-1.8, 0.9), (-1.0, 1.35), (0.3, 1.6), (1.1, 1.4), (1.6, 0.95), (1.6, 0.2), (1.0, -0.25), (-0.5, -0.25),
                (-1.5, -0.15)])
    head = spl([(1.2, 1.35), (1.7, 1.28), (2.4, 0.72), (2.85, 0.38), (2.95, 0.12), (2.8, -0.05), (2.3, 0.05), (1.7, 0.2), (1.35, 0.45)])
    ear = spl([(1.55, 1.25), (1.5, 1.7, 0), (1.85, 1.3)])
    tusk = [quad((2.55, 0.12), (2.75, 0.2), (2.72, 0.42), 6)]
    legs = [limb([(1.2, 0.1), (1.3, -0.55), (1.25, -1.05)], 0.36, 0.2), limb([(-1.3, 0.2), (-1.0, -0.45), (-1.3, -0.75), (-1.25, -1.05)], 0.48, 0.2)]
    far = [limb([(0.8, 0.0), (0.75, -0.55), (0.82, -1.02)], 0.32, 0.18), limb([(-0.85, 0.1), (-0.6, -0.45), (-0.85, -0.75), (-0.8, -1.02)], 0.42, 0.18)]
    tail = [quad((-1.85, 0.75), (-2.15, 0.6), (-2.1, 0.2), 8)]
    mane = fringe(spl([(-0.9, 1.4), (0.3, 1.66), (1.25, 1.4)], closed=False), 0.16, 9)
    front = [head, body, *legs]
    sil = union(head, body, *legs)
    back = hide(far, *front)
    snout = [ellipse(2.9, 0.15, 0.06, 0.12, 12)]
    G = -1.08
    hooves = [[(1.13, -1.08), (1.38, -1.08)], [(-1.37, -1.08), (-1.13, -1.08)]]
    piglets = []
    for px, py, s in [(-1.6, -2.05, 0.55), (0.9, -2.2, 0.6)]:
        pb = ellipse(px, py, 0.95 * s, 0.55 * s, 40)
        ph = spl([(px + 0.7 * s, py + 0.45 * s), (px + 1.3 * s, py + 0.2 * s), (px + 1.6 * s, py - 0.05 * s), (px + 1.55 * s, py - 0.2 * s),
                  (px + 1.1 * s, py - 0.25 * s), (px + 0.7 * s, py - 0.2 * s)])
        pl = [limb([(px + 0.55 * s, py - 0.3 * s), (px + 0.6 * s, py - 0.85 * s)], 0.25 * s, 0.2 * s),
              limb([(px - 0.55 * s, py - 0.3 * s), (px - 0.6 * s, py - 0.85 * s)], 0.28 * s, 0.2 * s)]
        pe = spl([(px + 0.8 * s, py + 0.4 * s), (px + 0.85 * s, py + 0.75 * s, 0), (px + 1.05 * s, py + 0.38 * s)])
        sil_p = union(pb, ph, *pl)
        stripes = keep([spl([(px - 0.85 * s, py + (0.25 - 0.22 * k) * s), (px, py + (0.32 - 0.22 * k) * s), (px + 0.8 * s, py + (0.2 - 0.2 * k) * s)],
                            closed=False) for k in range(3)], pb)
        stripes = hide(stripes, *pl)
        piglets.append((sil_p + hide([pe], ph) + stripes + [[(px - 0.9 * s, py + 0.1 * s), (px - 1.1 * s, py + 0.25 * s)]],
                        [pb, ph] + pl, (px + 1.15 * s, py + 0.1 * s)))
    pig_strokes, pig_cov, pig_eyes = [], [], []
    for st, cv, e in piglets:
        pig_strokes += st
        pig_cov += cv
        pig_eyes.append(eye(e[0], e[1], 0.04))
    boar = hide(sil + back + snout + tusk + hide(tail, body) + [mane] + hooves, *pig_cov)
    ground = [[(-3.3, -2.6), (3.3, -2.6)]]
    grass = tuft(2.7, -2.6, 0.6) + tuft(-2.9, -2.6, 0.6)
    bg = hide(pine(-2.9, -1.1, 3.2, 0.9, 4), *front)
    return make("Wild Boar and Striped Piglets", boar + pig_strokes + ground + grass + bg, [eye(2.2, 0.75, 0.06)] + pig_eyes)


@design("woodland_pine_marten", T)
def pine_marten(rng):
    a = -0.25
    by = lambda x: 0.4 + math.tan(a) * x
    branch = limb([(-3.3, by(-3.3)), (3.3, by(3.3))], 0.45, 0.38, cap0=False, cap1=False, smooth=False)
    body = spl([(-1.3, by(-1.3) + 0.3), (-1.3, by(-1.3) + 0.85), (-0.3, by(-0.3) + 1.15), (0.7, by(0.7) + 1.1), (1.2, by(1.2) + 0.9),
                (1.3, by(1.3) + 0.45), (0.5, by(0.5) + 0.3), (-0.6, by(-0.6) + 0.3)])
    hx, hy = 1.75, by(1.75) + 1.35
    head = spl([(hx - 0.55, hy + 0.05), (hx - 0.3, hy + 0.4), (hx + 0.25, hy + 0.42), (hx + 0.7, hy + 0.15), (hx + 0.95, hy - 0.08),
                (hx + 0.8, hy - 0.22), (hx + 0.3, hy - 0.35), (hx - 0.25, hy - 0.45)])
    ears = [circle(hx - 0.25, hy + 0.42, 0.18, 20), circle(hx + 0.15, hy + 0.48, 0.17, 20)]
    neck = limb([(1.0, by(1.0) + 0.85), (hx - 0.1, hy - 0.1)], 0.62, 0.55)
    bib = keep([spl([(hx + 0.6, hy - 0.2), (hx - 0.1, hy - 0.35), (1.15, by(1.15) + 0.65), (1.35, by(1.35) + 0.45)], closed=False)], head, neck, body)
    legs = [limb([(1.0, by(1.0) + 0.6), (1.2, by(1.2) + 0.25), (1.15, by(1.15) + 0.2)], 0.3, 0.24),
            limb([(-0.9, by(-0.9) + 0.6), (-0.7, by(-0.7) + 0.25), (-0.85, by(-0.85) + 0.2)], 0.36, 0.26)]
    tail = spl([(-1.2, by(-1.2) + 0.75), (-2.0, by(-2.0) + 0.6), (-2.6, by(-2.6) - 0.1), (-2.8, by(-2.8) - 1.0), (-2.5, by(-2.5) - 1.5),
                (-2.25, by(-2.25) - 1.0), (-2.15, by(-2.15) - 0.3), (-1.6, by(-1.6) + 0.35)])
    front = [head, *ears, neck, body, *legs, tail]
    sil = union(head, *ears, neck, body, *legs, tail)
    br = hide([branch], *front)
    ear_in = hide([circle(hx - 0.25, hy + 0.42, 0.08, 10), circle(hx + 0.15, hy + 0.48, 0.08, 10)], head)
    nose = [ellipse(hx + 0.92, hy - 0.12, 0.06, 0.05, 10)]
    claws = [arc(1.15 + 0.1 * k, by(1.15 + 0.1 * k) + 0.14, 0.08, math.pi + 0.3, TAU, 5) for k in (-1, 0, 1)]
    fur = keep([quad((-2.3, by(-2.3) + 0.3), (-2.5, by(-2.5) - 0.4), (-2.45, by(-2.45) - 1.0), 8)], tail)
    lv = []
    for x in (2.5, -0.2, 2.9):
        lv += pine_needles(x, by(x))
    lv = hide(lv, branch, *front)
    cones = [ellipse(2.2, by(2.2) - 0.55, 0.16, 0.3, 16)]
    cones = hide(cones, branch)
    return make("Pine Marten on a Bough", sil + br + ear_in + nose + claws + fur + lv + cones, [eye(hx + 0.25, hy + 0.05, 0.07)])


def pine_needles(x, y, n=7, L=0.55):
    out = []
    for k in range(n):
        a = math.radians(30 + 120 * k / (n - 1))
        out.append([(x, y), (x + L * math.cos(a), y + L * math.sin(a))])
    return out


# dropped: the subject repeats another book
def stoat(rng):
    rock = spl([(-2.5, -1.9), (-2.2, -1.2), (-1.0, -0.95), (0.6, -1.0), (1.8, -1.25), (2.3, -1.9)], closed=False)
    body = spl([(-0.35, -1.0), (-0.6, -0.4), (-0.55, 0.5), (-0.4, 1.3), (-0.05, 1.75), (0.35, 1.75), (0.5, 1.3), (0.45, 0.3), (0.55, -0.5),
                (0.45, -1.0)])
    head = spl([(-0.25, 1.75), (-0.15, 2.15), (0.25, 2.35), (0.65, 2.25), (1.05, 2.05), (1.12, 1.92), (0.85, 1.8), (0.4, 1.6), (0.0, 1.55)])
    ears = [circle(0.0, 2.3, 0.15, 16), circle(0.35, 2.38, 0.14, 16)]
    paws = [limb([(0.35, 1.0), (0.75, 0.85), (0.72, 0.62)], 0.2, 0.16), limb([(0.25, 0.8), (0.6, 0.6), (0.55, 0.4)], 0.2, 0.16)]
    foot = ellipse(0.55, -1.0, 0.42, 0.12, 24)
    haunch = ellipse(-0.05, -0.55, 0.55, 0.5, 40)
    tail = limb([(-0.5, -0.7), (-1.1, -0.6), (-1.55, -0.2), (-1.7, 0.3)], 0.24, 0.2)
    tip = spl([(-1.6, 0.25), (-1.85, 0.75), (-1.75, 1.0, 0), (-1.6, 0.6)])
    front = [head, *ears, paws[0], body, haunch, foot]
    sil = union(head, *ears, body, haunch, foot, tail, tip)
    sil = hide(sil, *paws) + [paws[0]] + hide([paws[1]], paws[0])
    tip_l = keep([[(-1.62, 0.25), (-1.45, 0.3)]], tail)
    bib = keep([spl([(1.0, 1.9), (0.55, 1.68), (0.4, 1.0), (0.42, 0.0), (0.5, -0.6)], closed=False)], head, body)
    bib = hide(bib, *paws)
    nose = [ellipse(1.1, 1.97, 0.05, 0.05, 8)]
    whisk = [quad((0.95, 1.9), (1.25, 2.0), (1.45, 2.05), 6), quad((0.95, 1.86), (1.25, 1.8), (1.45, 1.75), 6)]
    ear_in = hide([circle(0.0, 2.3, 0.07, 8), circle(0.35, 2.38, 0.07, 8)], head)
    rk = hide([rock], *front, tail)
    moss = [arc(-1.6 + 0.4 * k, -1.05 + (0.02 if k > 1 else -0.03), 0.15, 0.2, 2.9, 6) for k in range(1)]
    ground = [[(-3.3, -1.9), (3.3, -1.9)]]
    grass = tuft(-2.9, -1.9, 0.7) + tuft(2.8, -1.9, 0.7)
    flowers = []
    for x, h in [(-2.8, 1.3), (2.7, 1.1)]:
        flowers += [[(x, -1.9), (x, -1.9 + h)]] + [lens((x, -1.9 + h), (x + 0.4 * math.cos(a), -1.9 + h + 0.4 * math.sin(a)), 0.35)
                                                 for a in [TAU * k / 5 + 0.3 for k in range(5)]]
    return make("Stoat on the Lookout", sil + tip_l + bib + nose + whisk + ear_in + rk + ground + grass + flowers,
                [eye(0.55, 2.05, 0.06)])


@design("woodland_woodchuck", T)
def woodchuck(rng):
    G = -2.2
    mound = spl([(-3.3, G), (-2.6, -1.0), (-1.4, -0.75), (-0.2, -1.2), (0.2, G)], closed=False)
    hole = [quad((-2.6, -1.25), (-2.0, -0.6), (-1.2, -1.2), 10)]
    body = spl([(0.9, 1.0), (1.6, 0.8), (2.0, -0.2), (1.95, -1.3), (1.55, -2.05), (0.9, -2.2), (0.25, -2.05), (-0.1, -1.3), (-0.05, -0.2), (0.35, 0.75)])
    head = spl([(1.0, 1.95), (1.5, 1.85), (1.7, 1.45), (1.6, 1.05), (1.25, 0.8), (0.85, 0.75), (0.45, 0.9), (0.3, 1.35), (0.5, 1.8)])
    ears = [circle(0.5, 1.8, 0.14, 14), circle(1.45, 1.82, 0.14, 14)]
    muzzle = ellipse(0.95, 1.05, 0.3, 0.2, 24)
    arms = [limb([(0.25, 0.4), (0.35, -0.05), (0.8, 0.1)], 0.3, 0.24), limb([(1.65, 0.4), (1.55, -0.05), (1.1, 0.1)], 0.3, 0.24)]
    clover = [[(0.95, -0.4), (0.95, 0.25)]] + [circle(0.95 + 0.17 * math.cos(a), 0.42 + 0.17 * math.sin(a), 0.14, 14) for a in (0.5, 2.6, 4.7)]
    feet = [ellipse(0.4, -2.25, 0.35, 0.13, 20), ellipse(1.5, -2.25, 0.35, 0.13, 20)]
    tail = limb([(0.0, -1.9), (-0.5, -2.05), (-0.75, -1.9)], 0.3, 0.26)
    front = [arms[0], arms[1], muzzle, head, *ears, body, *feet, tail]
    sil = union(head, *ears, body, *feet, tail)
    sil = hide(sil, *arms, *clover[1:]) + hide(arms, *clover[1:])
    cl = hide(clover, muzzle)
    cl = [clover[0][:1] + [(0.9, 0.95)]] + clover[1:]
    cl = hide([clover[0]], muzzle, *arms) + clover[1:]
    mz = hide([muzzle], *clover[1:])
    teeth = hide([rect(0.88, 0.75, 1.02, 0.9)], *clover[1:])
    nose = [ellipse(0.95, 1.18, 0.08, 0.05, 10)]
    ear_in = hide([circle(0.5, 1.8, 0.07, 8), circle(1.45, 1.82, 0.07, 8)], head)
    belly = keep([spl([(0.4, -0.2), (0.95, -1.0), (1.5, -0.2)], closed=False)], body)
    md = hide([mound] + hole, *front)
    ground = [[(-3.3, G), (3.3, G)]]
    flowers = tuft(2.7, G, 0.8) + tuft(-0.6, G, 0.5) + [[(2.9, G), (2.9, G + 1.3)], circle(2.9, G + 1.5, 0.2, 18)]
    flowers += [lens((2.9, G + 1.5), (2.9 + 0.5 * math.cos(a), G + 1.5 + 0.5 * math.sin(a)), 0.3) for a in [TAU * k / 8 for k in range(8)]]
    flowers = hide(flowers, circle(2.9, G + 1.5, 0.2, 18)) + [circle(2.9, G + 1.5, 0.2, 18)]
    return make("Woodchuck Nibbling Clover", sil + cl + mz + teeth + nose + ear_in + belly + md + ground + flowers,
                [eye(0.7, 1.4, 0.06), eye(1.25, 1.4, 0.06)])


# dropped: the subject repeats another book
def wolverine(rng):
    body = spl([(-1.6, -0.2), (-1.75, 0.4), (-1.1, 0.95), (-0.2, 1.22), (0.7, 1.08), (1.3, 0.8), (1.5, 0.3), (1.2, -0.3), (0.2, -0.45),
                (-1.0, -0.4)])
    head = spl([(1.15, 0.85), (1.6, 1.02), (2.05, 0.88), (2.45, 0.52), (2.58, 0.3), (2.38, 0.18), (1.9, 0.12), (1.45, 0.18)])
    ear = circle(1.55, 0.98, 0.15, 16)
    legs = [limb([(1.15, 0.0), (1.3, -0.6), (1.25, -1.0)], 0.5, 0.4), limb([(-1.2, 0.0), (-0.95, -0.6), (-1.15, -1.0)], 0.55, 0.4)]
    far = [limb([(0.75, -0.1), (0.75, -0.6), (0.65, -0.98)], 0.45, 0.36), limb([(-0.7, -0.1), (-0.5, -0.6), (-0.6, -0.98)], 0.5, 0.36)]
    paws = [ellipse(1.4, -1.05, 0.3, 0.12, 20), ellipse(-1.0, -1.05, 0.3, 0.12, 20)]
    tail = spl([(-1.6, 0.5), (-2.3, 0.35), (-2.65, -0.15), (-2.4, -0.3), (-1.75, 0.0)])
    front = [head, ear, body, *legs, *paws, tail]
    sil = union(head, ear, body, *legs, *paws, tail)
    back = hide(far, *front)
    band = keep([spl([(1.25, 0.55), (0.4, 0.75), (-0.5, 0.65), (-1.3, 0.35), (-1.75, 0.25)], closed=False),
                 spl([(1.15, 0.25), (0.3, 0.35), (-0.6, 0.25), (-1.4, 0.05)], closed=False)], body)
    band = hide(band, *legs)
    claws = [quad((1.6 + 0.0, -1.0 - 0.07 * k), (1.75, -1.02 - 0.07 * k), (1.8, -1.1 - 0.07 * k), 4) for k in range(3)]
    claws += [quad((-0.75, -1.0 - 0.07 * k), (-0.6, -1.02 - 0.07 * k), (-0.55, -1.1 - 0.07 * k), 4) for k in range(3)]
    face = [ellipse(2.55, 0.3, 0.06, 0.05, 10), quad((2.45, 0.18), (2.2, 0.15), (2.05, 0.22), 6), quad((1.85, 0.75), (2.1, 0.62), (2.35, 0.5), 8)]
    ear_in = hide([circle(1.55, 0.98, 0.07, 8)], head)
    G = -1.15
    rocks = [spl([(-3.3, G), (-3.0, -0.5), (-2.4, -0.35), (-2.0, G)], closed=False), spl([(2.0, G), (2.3, -0.65), (2.9, -0.55), (3.3, G)], closed=False)]
    rocks = hide(rocks, *front)
    ground = [[(-3.3, G), (3.3, G)]]
    bg = hide(pine(-2.2, G + 0.6, 3.0, 0.9, 4) + pine(2.6, G + 0.5, 2.6, 0.8, 3), *front, *far, *[r + [r[0]] for r in rocks])
    return make("Wolverine on the Prowl", sil + back + band + claws + face + ear_in + rocks + ground + bg, [eye(2.0, 0.55, 0.06)])


@design("woodland_cougar", T)
def cougar(rng):
    ledge = [[(-3.3, -0.6), (2.6, -0.6)], spl([(2.6, -0.6), (2.9, -1.1), (2.7, -1.7), (3.1, -2.5), (3.0, -3.0)], closed=False),
             spl([(-3.3, -1.3), (-1.0, -1.35), (1.0, -1.3), (2.75, -1.25)], closed=False)]
    body = spl([(-2.0, -0.6), (-2.25, -0.1), (-1.8, 0.45), (-0.6, 0.62), (0.4, 0.55), (1.0, 0.8), (1.25, 0.3), (1.0, -0.6)])
    head = spl([(0.9, 1.1), (1.15, 1.55), (1.6, 1.68), (2.0, 1.48), (2.22, 1.18), (2.28, 0.95), (2.08, 0.8), (1.6, 0.72), (1.1, 0.75)])
    ears = [spl([(1.1, 1.45), (1.05, 1.8), (1.35, 1.65)]), spl([(1.45, 1.65), (1.55, 1.95), (1.75, 1.66)])]
    fl = limb([(0.8, -0.3), (1.6, -0.45), (2.05, -0.47)], 0.38, 0.3)
    paw = ellipse(2.15, -0.48, 0.25, 0.12, 20)
    haunch = ellipse(-1.45, -0.15, 0.65, 0.5, 40)
    hfoot = limb([(-1.2, -0.45), (-0.5, -0.5)], 0.25, 0.22)
    tail = limb([(-2.1, -0.4), (-2.55, -0.65), (-2.55, -1.6), (-2.3, -2.05)], 0.28, 0.24)
    front = [head, *ears, fl, paw, body, haunch, hfoot, tail]
    sil = union(head, *ears, fl, paw, body, haunch, hfoot)
    tl = hide([tail], body, haunch)
    hl = keep([arc(-1.45, -0.15, 0.65, 0.6, 2.6, 14)], body)
    ld = hide(ledge, *front)
    face = [poly((2.18, 1.0), (2.3, 0.94), (2.2, 0.86)), quad((2.2, 0.86), (2.05, 0.75), (1.9, 0.82), 6), quad((2.2, 0.86), (2.15, 0.78), (2.08, 0.76), 4),
            quad((1.6, 1.25), (1.75, 1.15), (1.9, 1.15), 6)]
    ear_in = [[(1.15, 1.5), (1.12, 1.68)], [(1.52, 1.68), (1.56, 1.85)]]
    cracks = [[(-2.0, -0.9), (-1.6, -1.05)], [(0.2, -0.85), (0.6, -1.1)], [(2.75, -1.9), (2.4, -2.3)]]
    bg = pine(-2.6, -0.6, 3.6, 1.0, 4) + pine(0.0, -0.6, 2.8, 0.9, 3)
    bg = hide(bg, *front)
    return make("Cougar on a Rocky Ledge", sil + tl + hl + ld + face + ear_in + cracks + bg, [eye(1.75, 1.3, 0.07)])


@design("woodland_bobcat", T)
def bobcat(rng):
    body = spl([(-1.6, 0.1), (-1.72, 0.7), (-1.2, 1.05), (0.0, 1.0), (0.9, 1.12), (1.35, 0.95), (1.55, 0.45), (1.25, 0.0), (0.2, -0.1),
                (-1.0, -0.05)])
    head = spl([(1.4, 1.3), (1.65, 1.6), (2.1, 1.66), (2.45, 1.46), (2.66, 1.15), (2.6, 0.9), (2.35, 0.75), (1.9, 0.72), (1.5, 0.9)])
    ears = [spl([(1.65, 1.55), (1.72, 2.0, 0), (1.93, 1.62)]), spl([(1.98, 1.65), (2.14, 2.03, 0), (2.27, 1.55)])]
    tufts = [[(1.72, 2.0), (1.7, 2.22)], [(2.14, 2.03), (2.15, 2.25)]]
    legs = [limb([(1.2, 0.4), (1.3, -0.4), (1.25, -0.98)], 0.42, 0.3), limb([(-1.15, 0.4), (-0.8, -0.3), (-1.2, -0.7), (-1.1, -0.98)], 0.6, 0.28)]
    paws = [ellipse(1.4, -1.02, 0.26, 0.11, 20), ellipse(-0.97, -1.02, 0.26, 0.11, 20)]
    far = [limb([(0.85, 0.35), (1.15, -0.2), (1.0, -0.55)], 0.36, 0.28), limb([(-0.65, 0.3), (-0.35, -0.3), (-0.72, -0.7), (-0.62, -0.98)], 0.52, 0.26)]
    fpaws = [ellipse(1.1, -0.62, 0.2, 0.11, 16, rot=-0.6), ellipse(-0.5, -1.02, 0.24, 0.1, 20)]
    tail = limb([(-1.6, 0.78), (-2.0, 0.98)], 0.3, 0.28)
    front = [head, *ears, body, *legs, *paws, tail]
    sil = union(head, *ears, body, *legs, *paws, tail)
    back = hide(far + fpaws, *front)
    spots = keep([circle(x, y, 0.07, 8) for x, y in [(-1.1, 0.55), (-0.6, 0.65), (-0.1, 0.6), (0.4, 0.65), (-0.35, 0.25), (0.15, 0.25), (0.65, 0.3),
                                                      (1.25, -0.35), (-1.0, -0.45), (-1.3, 0.2), (0.9, 0.7)]], body, *legs)
    face = [poly((2.58, 1.12), (2.7, 1.05), (2.58, 0.98)), quad((2.58, 0.98), (2.45, 0.85), (2.28, 0.88), 6),
            [(1.75, 1.05), (1.62, 0.82)], [(1.88, 1.0), (1.78, 0.76)], [(2.1, 1.72), (2.12, 1.55)]]
    ear_in = [[(1.76, 1.65), (1.74, 1.85)], [(2.13, 1.68), (2.14, 1.88)]]
    G = -1.13
    ground = [[(-3.3, G), (3.3, G)]]
    ferns = palm_frond((-2.5, G), (-3.0, 1.2), 0.12) + palm_frond((2.9, G), (3.2, 1.0), -0.12)
    ferns = hide(ferns, *front, *far)
    return make("Bobcat on the Prowl", sil + back + tufts + spots + face + ear_in + ground + ferns, [eye(2.15, 1.32, 0.06)])


@design("woodland_muskrat", T)
def muskrat(rng):
    W = -0.2
    head = spl([(-0.6, W - 0.05), (-0.55, 0.35), (-0.1, 0.75), (0.5, 0.85), (1.05, 0.65), (1.45, 0.35), (1.55, 0.15), (1.35, W - 0.05)], closed=False)
    back = spl([(-0.6, W - 0.02), (-1.2, 0.05), (-1.9, W - 0.02)], closed=False)
    ear = circle(0.15, 0.78, 0.13, 14)
    ear = hide([ear], head + [head[0]])
    wake = [[(-0.75, W), (-2.9, -0.9)], [(1.45, W), (3.0, -0.75)], [(-2.0, W - 0.05), (-3.3, -0.45)], ripples(-0.5, 1.4, -0.35, 2, 0.04)]
    tail = [quad((-1.9, W), (-2.4, -0.1), (-2.7, -0.3), 8)]
    face = [ellipse(1.5, 0.2, 0.06, 0.05, 10), quad((1.35, 0.25), (1.65, 0.4), (1.9, 0.45), 6), quad((1.35, 0.2), (1.65, 0.15), (1.95, 0.12), 6)]
    water = [ripples(-3.3, 3.3, -1.3, 7, 0.05), ripples(-3.0, 3.0, -1.9, 6, 0.05), ripples(-3.3, 2.5, -2.5, 6, 0.05)]
    cattails = []
    for x, h, lean in [(-2.8, 2.6, -0.1), (-2.4, 3.1, 0.05), (-2.0, 2.3, 0.1), (2.2, 2.8, 0.08), (2.65, 3.2, -0.05), (3.0, 2.4, 0.1)]:
        top = (x + lean * h, W + h)
        cattails.append([(x, W), top])
        cattails.append(rrect(top[0] - 0.12, top[1] - 0.9, top[0] + 0.12, top[1] - 0.25, 0.12))
        cattails.append([(top[0], top[1] - 0.25), (top[0] + 0.02, top[1])])
    blades = [quad((-2.6, W), (-3.1, 1.2), (-3.3, 2.2), 10), quad((2.4, W), (1.9, 1.3), (1.7, 2.0), 10), quad((2.9, W), (3.3, 1.0), (3.4, 1.6), 10)]
    stems = hide(cattails + blades, *[r for r in cattails if len(r) > 3])
    stems = [c for c in cattails if len(c) == 2]
    pods = [c for c in cattails if len(c) > 3]
    stems = hide(stems, *pods)
    lily = [chain(arc(0.4, -1.6, 0.4, 0.4, TAU - 0.1, 24), [(0.4, -1.6)], [(0.4 + 0.4 * math.cos(0.4), -1.6 + 0.4 * math.sin(0.4))])]
    water = hide(water, ellipse(0.4, -1.6, 0.45, 0.2, 20))
    lily = [[(0.4 + 0.45 * math.cos(t), -1.6 + 0.2 * math.sin(t)) for t in [0.5 + (TAU - 0.6) * i / 30 for i in range(31)]] + [(0.4, -1.6)] +
            [(0.4 + 0.45 * math.cos(0.5), -1.6 + 0.2 * math.sin(0.5))]]
    return make("Muskrat Swimming among the Cattails", [head, back] + ear + wake + tail + face + water + stems + pods + blades + lily,
                [eye(0.85, 0.48, 0.06)])


@design("woodland_common_toad", T)
def common_toad(rng):
    body = spl([(-1.9, -0.6), (-1.9, 0.2), (-1.3, 0.85), (-0.2, 1.15), (0.8, 1.15), (1.5, 0.9), (2.0, 0.45), (2.2, 0.05), (2.0, -0.3),
                (1.4, -0.6), (0.0, -0.8), (-1.2, -0.8)])
    eye_bump = spl([(0.85, 1.05), (1.0, 1.42), (1.45, 1.45), (1.7, 1.1)])
    gland = ellipse(0.3, 0.95, 0.42, 0.17, 24, rot=-0.1)
    fl = limb([(1.2, -0.3), (1.55, -0.85), (1.75, -1.15)], 0.32, 0.24)
    hl = spl([(-1.6, -0.3), (-0.9, 0.15), (-0.2, -0.3), (0.2, -0.9), (-0.4, -1.15), (-1.5, -0.95)])
    foot = limb([(0.0, -1.0), (-0.9, -1.2), (-1.6, -1.15)], 0.28, 0.22)
    toes = []
    for x, y, d in [(1.75, -1.15, 1), (-1.6, -1.15, -1)]:
        for a in (-0.4, 0.0, 0.4):
            toes.append(limb([(x, y), (x + d * 0.35 * math.cos(a), y - 0.08 + 0.25 * math.sin(a))], 0.1, 0.08))
    front = [eye_bump, fl, hl, foot, body] + toes
    sil = union(body, eye_bump, fl, hl, foot, *toes)
    warts = keep([circle(x, y, 0.08, 10) for x, y in [(-1.3, 0.4), (-0.8, 0.7), (-0.3, 0.55), (-1.0, 0.2), (-0.5, 0.15), (0.6, 0.55),
                                                       (1.1, 0.6), (0.2, 0.35), (-1.5, -0.1), (1.6, 0.3)]], body)
    warts = hide(warts, hl, gland)
    mouth = [quad((2.15, 0.05), (1.6, 0.0), (1.05, 0.25), 10)]
    nost = [circle(2.0, 0.42, 0.03, 6)]
    G = -1.25
    ground = [[(-3.3, G), (3.3, G)]]
    moss = [arc(x, G, 0.25, 0.0, math.pi, 8) for x in (-2.6, -2.2, 2.5, 2.9)]
    moss = hide(moss, *front)
    leaves = [lens((-3.2, G), (-2.0, G + 0.1), 0.3), lens((2.2, G), (3.3, G + 0.05), 0.3)]
    leaves = hide(leaves, *front)
    mush = []
    for x, h, r in [(-2.6, 1.3, 0.55), (2.7, 1.0, 0.45)]:
        mush += [chain(arc(x, G + h, r, 0.0, math.pi, 14), [(x - r, G + h)], [(x + r, G + h)]), [(x - 0.1, G + h), (x - 0.12, G)], [(x + 0.1, G + h), (x + 0.12, G)]]
    mush = hide(mush, *moss)
    return make("Warty Common Toad", sil + [gland] + warts + mouth + nost + ground + leaves + mush, [eye(1.25, 1.18, 0.12)])


@design("woodland_crested_newt", T)
def crested_newt(rng):
    body = spl([(-1.0, -0.15), (-0.8, 0.25), (0.2, 0.42), (1.2, 0.4), (1.9, 0.35), (2.5, 0.2), (2.7, 0.0), (2.55, -0.15), (1.9, -0.25),
                (1.0, -0.4), (0.0, -0.4)])
    crest = [(1.6, 0.38)]
    for k in range(14):
        x = 1.5 - 0.17 * k
        y = 0.42 + (0.25 if k % 2 == 0 else 0.08) - 0.008 * k
        crest.append((x, y))
    tail = spl([(-0.9, 0.2), (-1.6, 0.35), (-2.4, 0.3), (-3.2, 0.0, 0), (-2.4, -0.15), (-1.6, -0.15), (-0.9, -0.2)])
    tcrest = spl([(-1.0, 0.25), (-1.8, 0.62), (-2.6, 0.45), (-3.15, 0.05)], closed=False)
    tcrest_b = spl([(-1.2, -0.2), (-2.0, -0.42), (-2.8, -0.2)], closed=False)
    legs = [limb([(1.7, -0.1), (2.0, -0.45), (2.15, -0.7)], 0.18, 0.14), limb([(-0.5, -0.1), (-0.2, -0.45), (0.0, -0.7)], 0.2, 0.15)]
    far = [limb([(1.35, -0.1), (1.2, -0.45), (1.3, -0.68)], 0.16, 0.13), limb([(-0.75, -0.1), (-0.95, -0.45), (-0.85, -0.68)], 0.18, 0.14)]
    toes = []
    for x, y in [(2.15, -0.7), (0.0, -0.7)]:
        for a in (-0.5, 0.0, 0.5):
            toes.append(limb([(x, y), (x + 0.25 * math.cos(a), y - 0.05 + 0.15 * math.sin(a))], 0.07, 0.06))
    front = [body, tail, *legs, *toes]
    sil = union(body, tail, *legs, *toes)
    back = hide(far, *front)
    cr = hide([crest, tcrest, tcrest_b], body, tail)
    spots = keep([circle(x, y, 0.06, 8) for x, y in [(0.0, 0.1), (0.5, 0.15), (1.0, 0.05), (1.5, 0.12), (-1.5, 0.05), (-2.1, 0.0), (0.3, -0.2),
                                                      (1.2, -0.2)]], body, tail)
    spots = hide(spots, *legs)
    mouth = [quad((2.62, -0.02), (2.35, -0.05), (2.15, 0.02), 6)]
    stone = spl([(-2.6, -0.7), (-2.1, -1.4), (0.0, -1.55), (2.4, -1.4), (2.9, -0.75), (2.2, -0.62), (0.0, -0.68), (-2.0, -0.64)])
    st = hide([stone], *front, *far)
    water = [ripples(-3.3, 3.3, -1.9, 6, 0.05), ripples(-3.0, 3.0, -2.4, 6, 0.05)]
    water = hide(water, stone)
    reeds = [quad((-3.0, -1.6), (-3.1, 0.5), (-2.9, 1.8), 10), quad((-2.7, -1.6), (-2.6, 0.3), (-2.4, 1.4), 10),
             quad((3.0, -1.5), (2.9, 0.6), (3.1, 1.9), 10)]
    reeds = hide(reeds, stone, *front)
    return make("Great Crested Newt", sil + back + cr + spots + mouth + st + water + reeds, [eye(2.25, 0.15, 0.06)])


@design("woodland_grass_snake", T)
def grass_snake(rng):
    stone = spl([(-3.1, -1.8), (-2.8, -0.9), (-1.5, -0.55), (0.0, -0.6), (1.5, -0.55), (2.8, -0.9), (3.1, -1.8)], closed=False)
    c = spl([(-3.1, -0.75), (-2.3, -0.35), (-1.4, -0.85), (-0.4, -0.35), (0.6, -0.85), (1.5, -0.55), (1.9, 0.2), (2.15, 0.75)], closed=False)
    body = tube(c, lambda t: 0.1 + 0.32 * min(1.0, t * 2.2) - 0.05 * max(0.0, t - 0.8) * 5)
    head = spl([(1.85, 0.85), (2.05, 1.18), (2.55, 1.38), (3.05, 1.32), (3.2, 1.15), (2.9, 0.95), (2.4, 0.78), (2.05, 0.65)])
    snake = union(body, head)
    collar = keep([[(2.15, 1.28), (2.3, 0.72)], [(2.0, 1.1), (2.1, 0.62)]], head, body)
    belly = []
    n = len(c)
    for k in range(1, 14):
        i = int(n * k / 15)
        a_, b_ = c[i - 1], c[i + 1]
        L = math.dist(a_, b_)
        nx, ny = -(b_[1] - a_[1]) / L, (b_[0] - a_[0]) / L
        w = 0.1 + 0.32 * min(1.0, (i / (n - 1)) * 2.2)
        belly.append([(c[i][0] + nx * w * 0.45, c[i][1] + ny * w * 0.45), (c[i][0] - nx * w * 0.45, c[i][1] - ny * w * 0.45)])
    belly = hide(keep(belly, body), head)
    tongue = [chain([(3.18, 1.2), (3.45, 1.2)], [(3.6, 1.32)]), [(3.45, 1.2), (3.6, 1.08)]]
    mouth = [quad((3.15, 1.15), (2.85, 1.05), (2.6, 1.08), 6)]
    st = hide([stone], body, head)
    ground = [[(-3.3, -1.8), (3.3, -1.8)]]
    ferns = palm_frond((-2.9, -1.8), (-3.3, 1.0), 0.1) + palm_frond((-0.2, -0.6), (-0.6, 1.6), 0.1)
    ferns = hide(ferns, stone + [stone[0]], body, head)
    moss = hide([arc(x, -0.6, 0.22, 0.25, 2.9, 8) for x in (-1.9, 1.2)], body)
    return make("Grass Snake on a Mossy Stone", snake + collar + belly + tongue + mouth + st + ground + ferns + moss,
                [eye(2.7, 1.15, 0.06)])


@design("woodland_lizard_log", T)
def lizard_log(rng):
    log = limb([(-3.3, -0.7), (2.7, -0.7)], 1.0, 1.0, cap0=False, cap1=False, smooth=False)
    log_end = ellipse(2.7, -0.7, 0.25, 0.5, 40)
    body = spl([(-1.0, -0.15), (-0.6, 0.12), (0.4, 0.22), (1.2, 0.2), (1.7, 0.28), (2.2, 0.25), (2.55, 0.1), (2.5, -0.02), (2.0, -0.12),
                (1.2, -0.18), (0.0, -0.2)])
    tail = limb([(-0.95, -0.02), (-1.8, 0.0), (-2.6, -0.1), (-3.2, 0.1)], 0.3, 0.06)
    legs = [limb([(1.3, -0.05), (1.6, 0.0), (1.75, -0.2)], 0.14, 0.11), limb([(-0.5, -0.05), (-0.2, 0.0), (-0.05, -0.2)], 0.16, 0.12)]
    toes = []
    for x, y in [(1.75, -0.2), (-0.05, -0.2)]:
        for a in (-0.6, 0.0, 0.6):
            toes.append(limb([(x, y), (x + 0.2 * math.cos(a), y - 0.03 + 0.1 * math.sin(a))], 0.06, 0.05))
    Z = lambda p: transform(p, 0.0, 0.1, 1.0, 0.0, sx=1.0, sy=1.7)
    body, tail = Z(body), Z(tail)
    legs = [Z(l) for l in legs]
    toes = [Z(t) for t in toes]
    front = [body, tail, *legs, *toes]
    sil = union(*front)
    scales = keep([[(x, 0.45), (x + 0.05, -0.25)] for x in (-0.4, 0.0, 0.4, 0.8)] + [[(-1.4 - 0.4 * k, 0.25), (-1.35 - 0.4 * k, -0.15)] for k in range(3)], body, tail)
    scales = hide(scales, *legs)
    lg = hide([log, log_end, ellipse(2.7, -0.7, 0.12, 0.25, 20)], *front)
    bark = hide([[(-2.8, -0.45), (-1.6, -0.45)], [(-2.4, -0.95), (-0.4, -0.95)], [(0.6, -0.9), (2.2, -0.9)]], *front)
    sun = [circle(-2.4, 1.7, 0.4, 30)] + [[(-2.4 + 0.55 * math.cos(a), 1.7 + 0.55 * math.sin(a)), (-2.4 + 0.8 * math.cos(a), 1.7 + 0.8 * math.sin(a))]
                                         for a in [TAU * k / 10 for k in range(10)]]
    ground = [[(-3.3, -1.2), (3.3, -1.2)]]
    ground = hide(ground, log, log_end)
    grass = tuft(-2.7, -1.2, 0.0)
    plants = leaf((2.95, -1.2), (3.2, 0.4), 0.22) + leaf((-1.0, -1.2), (-0.6, -0.6), 0.25)
    plants = hide(plants, log, log_end)
    mouth = [quad((2.5, 0.12), (2.3, 0.08), (2.1, 0.15), 6)]
    return make("Common Lizard Basking on a Log", sil + scales + lg + bark + sun + ground + plants + mouth, [eye(2.2, 0.32, 0.05)])


# ================================================================== birds

def songbird(x, y, s=1.0, facing=1, rot=0.0, plump=1.0, beak=(0.35, 0.16, 0.0), tail=(0.9, 0.34, -0.55), crest=0.0,
             head_r=0.4, feet=True, wing=True, hx=0.6, hy=0.62):
    """A perched songbird in local coords facing right; returns
    (strokes, covers, eye(x, y), map) where map converts local points."""
    def M(pts):
        out = []
        c, sn = math.cos(rot), math.sin(rot)
        for px, py in pts:
            px, py = px * facing, py
            out.append((x + s * (px * c - py * sn), y + s * (px * sn + py * c)))
        return out
    body = spl([(0.25, 0.85 * plump), (-0.3, 0.6 * plump), (-0.85, 0.05), (-0.75, -0.25 * plump), (-0.3, -0.5 * plump),
                (0.35, -0.45 * plump), (0.8, -0.05), (0.9, 0.35), (0.75, 0.7)])
    head = circle(hx, hy, head_r, 40)
    L, D, C = beak
    bx = hx + head_r * 0.92
    bk = spl([(bx - 0.05, hy + D / 2 + 0.02), (bx + L, hy - 0.02 + C, 0), (bx - 0.05, hy - D / 2 - 0.02)])
    tl, tw, ta = tail
    base = (-0.7, -0.02)
    tip = (base[0] + tl * math.cos(math.pi - ta), base[1] + tl * math.sin(math.pi - ta))
    nx, ny = -math.sin(math.pi - ta), math.cos(math.pi - ta)
    tail_p = poly((base[0] + nx * 0.15, base[1] + ny * 0.15), (tip[0] + nx * tw / 2, tip[1] + ny * tw / 2),
                  (tip[0] - nx * tw / 2, tip[1] - ny * tw / 2), (base[0] - nx * 0.15, base[1] - ny * 0.15))
    parts = [body, head, bk, tail_p]
    if crest:
        parts.append(spl([(hx - 0.3, hy + 0.25), (hx - 0.45 - 0.2 * crest, hy + 0.45 + 0.35 * crest, 0), (hx + 0.05, hy + 0.38)]))
    wg = spl([(0.35, 0.42), (-0.2, 0.42), (-0.75, 0.05), (-1.05, -0.2, 0), (-0.45, -0.22), (0.1, -0.12), (0.42, 0.12)])
    parts = [M(p) for p in parts]
    sil = union(*parts)
    strokes = list(sil)
    covers = list(parts)
    if wing:
        w = M(wg)
        strokes = hide(strokes, w) + [w]
        covers.append(w)
    if feet:
        for fx in (0.05, 0.25):
            strokes.append(M([(fx, -0.47 * plump), (fx + 0.02, -0.72)]))
            strokes.append(M(arc(fx + 0.06, -0.72, 0.1, math.pi, math.pi + 2.6, 6)))
    e = M([(hx + 0.12, hy + 0.08)])[0]
    return strokes, covers, e, M


def twig(x0, y0, x1, y1, w=0.3, buds=()):
    return limb([(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 + 0.08), (x1, y1)], w, w * 0.75, cap0=False, cap1=True)


@design("woodland_nuthatch", T)
def nuthatch(rng):
    trunk = [spl([(-0.6, -3.2), (-0.5, 0.0), (-0.65, 3.4)], closed=False), spl([(0.55, -3.2), (0.6, 0.0), (0.5, 3.4)], closed=False)]
    st, cov, e, M = songbird(1.25, 0.0, 1.35, 1, rot=-math.pi / 2 - 0.25, plump=1.05, beak=(0.42, 0.14, 0.0), tail=(0.5, 0.36, -0.2),
                             feet=False)
    stripe = [M(spl([(0.95, 0.68), (0.62, 0.72), (0.3, 0.62)], closed=False))]
    claws = [M(arc(-0.05, -0.55, 0.12, math.pi * 0.6, math.pi * 1.6, 6)), M(arc(0.3, -0.55, 0.12, math.pi * 0.6, math.pi * 1.6, 6))]
    tr = hide(trunk, *cov)
    bark = hide([spl([(-0.1, 3.2), (0.0, 2.3), (-0.15, 1.5)], closed=False), spl([(0.1, -1.5), (0.0, -2.4), (0.15, -3.1)], closed=False),
                 [(0.25, 1.2), (0.3, 0.7)], [(-0.3, -0.5), (-0.25, -1.0)]], *cov)
    hole = [ellipse(0.0, 2.5, 0.25, 0.33, 24)]
    nut = [ellipse(0.0, 1.45, 0.16, 0.22, 16)]
    nut = hide(nut, *cov)
    branch = [spl([(0.55, 2.0), (1.6, 2.4), (3.2, 2.5)], closed=False), spl([(0.55, 1.7), (1.6, 2.1), (3.2, 2.2)], closed=False)]
    lv = leaf((2.2, 2.35), (2.6, 3.1), 0.3) + leaf((2.8, 2.4), (3.3, 1.7), 0.3) + leaf((1.4, 2.2), (1.2, 2.9), 0.3)
    return make("Nuthatch Upside Down on a Trunk", st + stripe + claws + tr + bark + hole + nut + branch + lv, [eye(e[0], e[1], 0.07)])


@design("woodland_treecreeper", T)
def treecreeper(rng):
    trunk = [spl([(-0.9, -3.2), (-0.8, 0.0), (-0.95, 3.4)], closed=False), spl([(0.4, -3.2), (0.45, 0.0), (0.35, 3.4)], closed=False)]
    st, cov, e, M = songbird(1.05, 0.2, 1.25, 1, rot=math.pi / 2 - 0.15, plump=0.9, beak=(0.5, 0.1, -0.15), tail=(0.85, 0.3, 0.05),
                             feet=False)
    claws = [M(arc(0.0, -0.5, 0.12, math.pi * 0.6, math.pi * 1.6, 6)), M(arc(0.3, -0.5, 0.12, math.pi * 0.6, math.pi * 1.6, 6))]
    streaks = keep([M([(0.1 + 0.25 * k, 0.4), (-0.05 + 0.25 * k, 0.15)]) for k in range(-2, 2)], *cov[1:2])
    brow = [M(spl([(0.95, 0.75), (0.65, 0.82), (0.35, 0.72)], closed=False))]
    tr = hide(trunk, *cov)
    bark = hide([spl([(-0.3, 3.2), (-0.2, 2.2), (-0.35, 1.4)], closed=False), spl([(-0.2, -1.2), (-0.3, -2.2), (-0.15, -3.1)], closed=False),
                 [(0.0, 0.7), (0.05, 0.2)], [(-0.55, -0.3), (-0.5, -0.8)], [(-0.5, 2.7), (-0.45, 2.3)]], *cov)
    spiral = [spl([(-0.3, -2.6), (0.4, -2.0), (0.6, -1.5)], closed=False)]
    insects = [ellipse(-0.1, 2.0, 0.08, 0.05, 10), ellipse(0.05, 1.6, 0.07, 0.05, 10)]
    lv = leaf((0.4, -2.0), (1.8, -2.4), 0.28) + leaf((0.4, -2.0), (1.5, -1.3), 0.28) + leaf((-0.9, 1.0), (-2.3, 1.3), 0.28)
    return make("Treecreeper Climbing the Bark", st + claws + streaks + brow + tr + bark + insects + lv, [eye(e[0], e[1], 0.06)])


@design("woodland_crossbill", T)
def crossbill(rng):
    branch = limb([(-3.3, -0.4), (-1.0, -0.2), (1.2, -0.35), (3.3, -0.2)], 0.3, 0.26, cap0=False, cap1=False)
    st, cov, e, M = songbird(-0.3, 0.6, 1.5, 1, plump=1.05, beak=(0.0, 0.0, 0.0), tail=(0.75, 0.42, -0.5))
    hx, hy = M([(0.6, 0.62)])[0]
    up = [M([(0.95, 0.75), (1.25, 0.62), (1.32, 0.38)]), M([(0.95, 0.75), (1.1, 0.56)])]
    low = [M([(0.98, 0.5), (1.2, 0.65), (1.28, 0.85)]), M([(0.98, 0.5), (1.12, 0.62)])]
    bk = up + low
    cone = spl([(2.05, 0.3), (2.35, 0.15), (2.45, -0.4), (2.25, -1.1), (2.05, -1.3), (1.85, -1.1), (1.65, -0.4), (1.75, 0.15)])
    scales = []
    for r in range(4):
        for c in range(3):
            xx, yy = 1.82 + 0.22 * c + 0.11 * (r % 2), 0.0 - 0.32 * r
            scales.append(arc(xx, yy, 0.12, math.pi + 0.3, TAU - 0.3, 6))
    scales = keep(scales, cone)
    stalk = [[(2.05, 0.3), (2.0, 0.5)]]
    cone_v = hide([cone] + scales, *cov)
    needles = []
    for bx in (-2.4, 2.9):
        needles += pine_needles(bx, -0.3, 8, 0.7)
    needles += [[(1.4, -0.32), (2.0, 0.45)]]
    needles = hide(needles, *cov)
    br = hide([branch], *cov, cone)
    wingbars = keep([M(spl([(0.2, 0.25), (-0.3, 0.2), (-0.7, 0.0)], closed=False))], cov[-1])
    return make("Crossbill Prising Open a Pine Cone", st + bk + cone_v + stalk + needles + br + wingbars, [eye(e[0], e[1], 0.07)])


@design("woodland_waxwing", T)
def waxwing(rng):
    branch = limb([(-3.3, -0.9), (-0.5, -0.75), (1.5, -0.85), (3.3, -0.7)], 0.32, 0.26, cap0=False, cap1=False)
    st, cov, e, M = songbird(-0.4, 0.05, 1.55, 1, plump=1.0, beak=(0.22, 0.16, 0.0), tail=(0.85, 0.36, -0.45), crest=0.8)
    mask = [M(spl([(1.0, 0.62), (0.75, 0.75), (0.45, 0.72), (0.25, 0.85)], closed=False)), M(spl([(1.0, 0.55), (0.75, 0.48), (0.5, 0.52)], closed=False))]
    tip = [M([(-1.35, -0.42), (-1.48, -0.1)])]
    tip = keep(tip, *cov)
    wax = [M(ellipse(-0.75, -0.12, 0.06, 0.04, 8))]
    berries = []
    for bx, by in [(1.4, -1.2), (1.7, -1.35), (1.55, -1.55), (1.85, -1.6), (2.1, -1.3), (1.3, -1.5), (1.95, -1.85)]:
        berries.append(circle(bx, by, 0.17, 16))
    bstem = [spl([(1.7, -0.9), (1.75, -1.1), (1.6, -1.3)], closed=False)]
    vis_b = []
    for i, b in enumerate(berries):
        vis_b += hide([b], *berries[:i])
    lvs = []
    for k in range(4):
        p0 = (2.4 + 0.3 * k, -0.78)
        lvs += [lens(p0, (p0[0] + 0.2, p0[1] + 0.6), 0.3)]
    lvs += leaf((-2.3, -0.85), (-2.9, -0.2), 0.3) + leaf((-2.0, -0.82), (-1.7, -1.6), 0.3)
    br = hide([branch], *cov)
    return make("Waxwing with Rowan Berries", st + mask + tip + vis_b + hide(bstem, *berries) + lvs + br, [eye(e[0], e[1], 0.07)])


@design("woodland_bullfinch", T)
def bullfinch(rng):
    branch = limb([(-3.3, -1.0), (-0.5, -0.85), (1.5, -1.0), (3.3, -0.8)], 0.3, 0.24, cap0=False, cap1=False)
    st, cov, e, M = songbird(-0.2, -0.05, 1.7, 1, plump=1.25, beak=(0.2, 0.22, -0.02), tail=(0.7, 0.36, -0.35), head_r=0.44)
    cap = [M(spl([(0.95, 0.62), (0.75, 0.8), (0.35, 0.8), (0.22, 0.6)], closed=False))]
    wingbar = keep([M(spl([(0.3, 0.2), (-0.2, 0.18), (-0.7, -0.05)], closed=False))], cov[-1])
    blossoms = []
    for bx, by, r in [(2.2, -0.3, 0.35), (2.8, 0.2, 0.3), (-2.5, -0.3, 0.32), (1.8, 0.45, 0.28)]:
        blossoms += [circle(bx + r * math.cos(a), by + r * math.sin(a), r * 0.62, 18) for a in [TAU * k / 5 + 0.3 for k in range(5)]]
    petals = []
    for i in range(0, len(blossoms), 5):
        group = blossoms[i:i + 5]
        petals += union(*group)
        cx = sum(p[0] for g in group for p in g) / sum(len(g) for g in group)
        cy = sum(p[1] for g in group for p in g) / sum(len(g) for g in group)
        petals.append(circle(cx, cy, 0.1, 10))
    petals = hide(petals, *cov)
    stems = [[(2.2, -0.65), (2.2, -0.95)], [(2.8, -0.15), (2.7, -0.85)], [(-2.5, -0.65), (-2.4, -0.95)], [(1.8, 0.1), (1.95, -0.9)]]
    stems = hide(stems, *cov)
    br = hide([branch], *cov)
    buds = [lens((0.9, -0.9), (1.1, -0.6), 0.35), lens((-1.8, -0.88), (-1.95, -0.55), 0.35)]
    return make("Bullfinch on a Blossom Twig", st + cap + wingbar + petals + stems + br + buds, [eye(e[0], e[1], 0.07)])


@design("woodland_long_tailed_tits", T)
def long_tailed_tits(rng):
    branch = limb([(-3.3, -0.55), (0.0, -0.35), (3.3, -0.6)], 0.3, 0.26, cap0=False, cap1=False)
    a, ca, ea, Ma = songbird(-1.0, 0.25, 1.15, 1, plump=1.3, beak=(0.12, 0.1, 0.0), tail=(2.2, 0.22, -1.2), head_r=0.42)
    b, cb, eb, Mb = songbird(1.2, 0.25, 1.15, -1, plump=1.3, beak=(0.12, 0.1, 0.0), tail=(2.2, 0.22, -1.25), head_r=0.42)
    a = hide(a, *cb)
    stripes = [Ma(spl([(0.95, 0.85), (0.6, 0.98), (0.25, 0.85)], closed=False)), Mb(spl([(0.95, 0.85), (0.6, 0.98), (0.25, 0.85)], closed=False))]
    br = hide([branch], *ca, *cb)
    lv = leaf((2.6, -0.55), (3.1, 0.3), 0.3) + leaf((-2.7, -0.5), (-3.2, 0.3), 0.3) + leaf((-2.4, -0.5), (-2.0, -1.3), 0.3)
    lv = hide(lv, branch, *ca, *cb)
    love = [heart(0.1, 1.75, 0.3, 60)]
    return make("Pair of Long-Tailed Tits", b + a + stripes + br + lv + love, [eye(ea[0], ea[1], 0.06), eye(eb[0], eb[1], 0.06)])


@design("woodland_song_thrush", T)
def song_thrush(rng):
    st, cov, e, M = songbird(-0.1, 0.55, 1.75, 1, rot=0.35, plump=1.1, beak=(0.0, 0.0, 0.0), tail=(0.8, 0.36, 0.35))
    bk = [M([(0.95, 0.75), (1.4, 0.95), (0.98, 0.62)]), M([(0.98, 0.55), (1.38, 0.45), (0.95, 0.5)])]
    spots = []
    for x, y in [(0.55, 0.15), (0.75, -0.05), (0.35, -0.1), (0.6, -0.3), (0.2, -0.32), (0.75, 0.3), (0.4, 0.4)]:
        spots.append(M(spl([(x, y + 0.08), (x + 0.06, y - 0.03), (x, y - 0.08), (x - 0.06, y - 0.03)])))
    spots = keep(hide(spots, cov[-1]), cov[0])
    notes = []
    for nx, ny in [(2.1, 2.3), (2.7, 2.7)]:
        notes += [ellipse(nx, ny, 0.16, 0.11, 14, rot=0.4), [(nx + 0.15, ny + 0.03), (nx + 0.15, ny + 0.6)], [(nx + 0.15, ny + 0.6), (nx + 0.4, ny + 0.45)]]
    stump = [[(-1.3, -0.95), (-1.25, -2.9)], [(1.15, -0.95), (1.2, -2.9)], ellipse(-0.07, -0.95, 1.23, 0.3, 60)]
    rings = [ellipse(-0.07, -0.95, 0.75, 0.18, 40), ellipse(-0.07, -0.95, 0.35, 0.08, 20)]
    stump_v = hide(stump + rings, *cov)
    roots = [quad((-1.25, -2.4), (-1.6, -2.75), (-2.1, -2.9), 8), quad((1.2, -2.4), (1.55, -2.75), (2.0, -2.9), 8)]
    bark = [[(-0.6, -1.4), (-0.55, -2.3)], [(0.5, -1.5), (0.55, -2.6)]]
    ground = [[(-3.3, -2.9), (3.3, -2.9)]]
    grass = tuft(-2.6, -2.9, 0.7) + tuft(2.5, -2.9, 0.7)
    return make("Song Thrush Singing on a Stump", st + bk + spots + notes + stump_v + roots + bark + ground + grass, [eye(e[0], e[1], 0.07)])


@design("woodland_cuckoo", T)
def cuckoo(rng):
    branch = limb([(-3.3, -0.3), (-0.5, -0.15), (1.5, -0.3), (3.3, -0.15)], 0.3, 0.26, cap0=False, cap1=False)
    st, cov, e, M = songbird(0.6, 0.65, 1.35, 1, rot=0.12, plump=0.9, beak=(0.0, 0.0, 0.0), tail=(1.9, 0.34, 0.75), head_r=0.37)
    bk = [M([(0.92, 0.72), (1.3, 0.82), (0.95, 0.6)]), M([(0.95, 0.55), (1.28, 0.42), (0.92, 0.5)])]
    bars = [M(spl([(0.95 - 0.12 * k, 0.3 - 0.17 * k), (0.6 - 0.1 * k, 0.24 - 0.17 * k), (0.3 - 0.1 * k, 0.28 - 0.17 * k)], closed=False)) for k in range(5)]
    bars = keep(hide(bars, cov[-1]), cov[0])
    tspots = keep([M(circle(-1.0 - 0.32 * k * math.cos(0.75), -0.0 - 0.32 * k * math.sin(0.75) - 0.25, 0.06, 8)) for k in range(1, 5)], cov[3])
    br = hide([branch], *cov)
    calls = [M(arc(1.3, 0.65, r, -0.6, 0.6, 8)) for r in (0.35, 0.6)]
    lv = leaf((-2.4, -0.25), (-2.9, 0.6), 0.3) + leaf((-2.0, -0.2), (-1.6, -1.0), 0.3) + leaf((2.6, -0.2), (3.1, 0.6), 0.3) + \
        leaf((2.2, -0.25), (2.4, -1.1), 0.3)
    lv = hide(lv, branch, *cov)
    return make("Cuckoo Calling from a Branch", st + bk + bars + tspots + br + calls + lv, [eye(e[0], e[1], 0.06)])


@design("woodland_goshawk", T)
def goshawk(rng):
    body = spl([(0.35, 1.35), (0.85, 0.9), (0.95, 0.0), (0.7, -0.9), (0.3, -1.4), (-0.3, -1.4), (-0.6, -0.6), (-0.65, 0.4), (-0.35, 1.15)])
    head = spl([(0.0, 2.15), (0.5, 2.2), (0.85, 1.95), (1.05, 1.75), (0.9, 1.4), (0.5, 1.2), (0.0, 1.3), (-0.3, 1.7)])
    beak = spl([(0.9, 1.88), (1.25, 1.8), (1.32, 1.55, 0), (1.15, 1.62), (0.95, 1.6)])
    wing = spl([(0.35, 1.2), (-0.3, 1.0), (-0.8, 0.0), (-0.85, -1.2), (-0.55, -2.0, 0), (-0.3, -1.2), (0.1, -0.3), (0.45, 0.5)])
    tail = poly((-0.45, -1.4), (0.25, -1.4), (0.1, -3.0), (-0.75, -2.95))
    legs = [limb([(0.2, -1.25), (0.25, -1.75)], 0.3, 0.22), limb([(0.55, -1.15), (0.6, -1.75)], 0.28, 0.2)]
    front = [wing, beak, head, body, *legs]
    sil = hide(union(head, beak, body, *legs), wing) + [wing]
    tl = hide([tail], *front)
    brow = [quad((0.15, 1.95), (0.55, 2.05), (0.95, 1.85), 8)]
    bars = keep([quad((0.95 - 0.05 * k, 0.6 - 0.35 * k), (0.6, 0.5 - 0.35 * k), (0.3, 0.6 - 0.35 * k), 6) for k in range(5)], body)
    bars = hide(bars, wing)
    wfeath = keep([quad((-0.2, 0.3 - 0.5 * k), (-0.5, -0.1 - 0.5 * k), (-0.75, -0.25 - 0.5 * k), 6) for k in range(4)], wing)
    tbars = keep([[(-0.6, -1.8 - 0.4 * k), (0.25, -1.8 - 0.4 * k)] for k in range(3)], tail)
    tbars = hide(tbars, *front)
    talons = [quad((0.05 + 0.15 * k, -1.8), (0.0 + 0.15 * k, -2.0), (-0.1 + 0.15 * k, -2.0), 4) for k in range(4)]
    stump = [[(-1.5, -1.85), (-1.45, -3.2)], [(1.4, -1.85), (1.35, -3.2)], ellipse(-0.05, -1.85, 1.45, 0.3, 60)]
    stump = hide(stump + [ellipse(-0.05, -1.85, 0.9, 0.18, 40)], *front, tail)
    bark = hide([[(-0.9, -2.3), (-0.85, -3.0)], [(0.8, -2.4), (0.85, -3.1)]], tail)
    bg = pine(-2.6, -3.2, 5.0, 1.3, 5) + pine(2.6, -3.2, 4.2, 1.2, 4)
    return make("Goshawk on a Stump", sil + tl + brow + bars + wfeath + tbars + talons + stump + bark + bg, [eye(0.55, 1.82, 0.08)])


@design("woodland_golden_oriole", T)
def golden_oriole(rng):
    br1 = spl([(-3.3, 1.2), (-1.5, 0.9), (0.0, 0.6), (1.6, 1.0), (3.3, 1.5)], closed=False)
    br2 = spl([(-3.3, 0.95), (-1.5, 0.65), (0.0, 0.35), (1.6, 0.75), (3.3, 1.25)], closed=False)
    nest = spl([(-0.8, 0.5), (-1.0, -0.5), (-0.6, -1.5), (0.0, -1.8), (0.6, -1.5), (1.0, -0.5), (0.8, 0.5)], closed=False)
    rim = ellipse(0.0, 0.5, 0.8, 0.2, 40)
    weave = keep([wave(-1.2, 1.2, y, 0.06, 5, 50) for y in (0.0, -0.5, -1.0, -1.45)], chain(nest, [nest[0]]))
    hangs = [[(-0.8, 0.5), (-0.55, 0.62)], [(0.8, 0.5), (0.6, 0.48)]]
    st, cov, e, M = songbird(1.7, 1.95, 1.25, -1, rot=-0.05, plump=1.0, beak=(0.35, 0.15, -0.05), tail=(0.85, 0.36, 0.45))
    mask = [M([(1.0, 0.62), (0.75, 0.62)])]
    wingbars = keep([M(spl([(0.2, 0.2), (-0.3, 0.15), (-0.7, -0.05)], closed=False))], cov[-1])
    bv = hide([br1, br2], *cov, rim)
    lv = leaf((-2.3, 1.05), (-2.7, 1.9), 0.3) + leaf((-1.6, 0.85), (-1.2, 1.7), 0.3) + leaf((2.7, 1.38), (3.1, 2.3), 0.3) + \
        leaf((-2.8, 1.1), (-3.2, 0.3), 0.3)
    lv = hide(lv, *cov)
    chicks = [arc(-0.35, 0.65, 0.22, 0.0, math.pi, 10), arc(0.25, 0.68, 0.22, 0.0, math.pi, 10)]
    beaks = [poly((-0.3, 0.87), (-0.4, 1.1), (-0.2, 0.86)), poly((0.3, 0.9), (0.25, 1.15), (0.42, 0.88))]
    return make("Golden Oriole and Its Hanging Nest", [nest, rim] + weave + hangs + st + mask + wingbars + bv + lv + chicks + beaks,
                [eye(e[0], e[1], 0.06)])


@design("woodland_hoopoe", T)
def hoopoe(rng):
    st, cov, e, M = songbird(-0.2, -0.3, 1.7, 1, plump=0.95, beak=(0.0, 0.0, 0.0), tail=(0.95, 0.4, 0.3), head_r=0.36)
    bill = [M(spl([(0.92, 0.72), (1.35, 0.6), (1.75, 0.35), (1.95, 0.12, 0), (1.7, 0.28), (1.3, 0.48), (0.92, 0.55)], closed=False))]
    crest = []
    for k in range(7):
        a = math.radians(160 - 18 * k)
        bx, by = 0.55 + 0.25 * math.cos(a), 0.75 + 0.2 * math.sin(a)
        tx, ty = 0.5 + 0.95 * math.cos(a), 0.7 + 0.85 * math.sin(a)
        crest.append(M(lens((bx, by), (tx, ty), 0.18)))
    crest_v = []
    for i, c in enumerate(crest):
        crest_v += hide([c], *cov[:4])
    tips = [M(circle(0.5 + 0.88 * math.cos(math.radians(160 - 18 * k)), 0.7 + 0.8 * math.sin(math.radians(160 - 18 * k)), 0.06, 8)) for k in range(7)]
    bars = keep([M([(0.25 - 0.25 * k, 0.4), (-0.05 - 0.25 * k, -0.2)]) for k in range(4)], cov[-1])
    tbar = keep([M([(-1.0, 0.25), (-1.2, -0.45)])], cov[3])
    G = -1.65
    ground = [[(-3.3, G), (3.3, G)]]
    grass = tuft(-2.4, G, 0.8) + tuft(2.7, G, 0.8) + tuft(1.5, G, 0.5)
    worm = [spl([(2.5, G + 0.02), (2.7, G + 0.2), (2.9, G + 0.05), (3.1, G + 0.2)], closed=False)]
    return make("Hoopoe Raising Its Crest", st + bill + crest_v + tips + bars + tbar + ground + grass + worm, [eye(e[0], e[1], 0.06)])


@design("woodland_capercaillie", T)
def capercaillie(rng):
    body = spl([(-1.0, -0.2), (-1.1, 0.5), (-0.6, 1.0), (0.2, 1.2), (0.7, 1.4), (0.85, 1.0), (0.9, 0.2), (0.6, -0.5), (0.0, -0.8), (-0.7, -0.65)])
    neck = limb([(0.55, 1.0), (0.85, 1.8), (1.0, 2.35)], 0.6, 0.45)
    head = spl([(0.75, 2.4), (0.95, 2.75), (1.3, 2.8), (1.55, 2.65), (1.85, 2.55), (1.6, 2.35), (1.3, 2.2), (0.95, 2.15)])
    beard = fringe(spl([(1.35, 2.25), (1.15, 2.0), (0.95, 1.9)], closed=False), -0.12, 3)
    brow = [lens((1.05, 2.68), (1.42, 2.68), 0.35)]
    fan = []
    for k in range(9):
        a = math.radians(100 + 12 * k)
        bx, by = -0.8, 0.3
        tip = (bx + 2.2 * math.cos(a), by + 2.2 * math.sin(a) * 0.95)
        fan.append(lens((bx, by), tip, 0.13))
    fan_v = []
    for i, f in enumerate(fan):
        fan_v += hide([f], *fan[i + 1:])
    wing = spl([(0.45, 0.85), (-0.2, 0.75), (-0.9, 0.2), (-1.0, -0.3, 0), (-0.3, -0.4), (0.35, -0.1)])
    legs = [limb([(0.1, -0.7), (0.2, -1.5)], 0.32, 0.22), limb([(0.45, -0.6), (0.55, -1.45)], 0.3, 0.2)]
    feet = []
    for x, y in [(0.2, -1.5), (0.55, -1.45)]:
        feet += [[(x, y), (x + 0.35, y - 0.12)], [(x, y), (x - 0.25, y - 0.1)], [(x, y), (x + 0.15, y - 0.18)]]
    front = [wing, head, neck, body, *legs]
    sil = hide(union(head, neck, body, *legs), wing) + [wing]
    fv = hide(fan_v, *front)
    spots = keep([circle(-0.8 + 2.0 * math.cos(math.radians(100 + 12 * k)), 0.3 + 1.95 * math.sin(math.radians(100 + 12 * k)) * 0.95, 0.07, 8)
                  for k in range(9)], *fan)
    spots = hide(spots, *front)
    beak = [spl([(1.78, 2.6), (2.05, 2.48, 0), (1.8, 2.38)])]
    G = -1.65
    ground = [[(-3.3, G), (3.3, G)]]
    bg = hide(pine(2.6, G, 4.6, 1.3, 5), *front) + tuft(-2.2, G, 0.7) + tuft(1.4, G, 0.6)
    return make("Displaying Capercaillie", sil + [beard] + brow + fv + spots + beak + feet + ground + bg, [eye(1.35, 2.52, 0.06)])


@design("woodland_woodcock", T)
def woodcock(rng):
    body = spl([(-1.6, 0.0), (-1.2, 0.65), (-0.2, 1.0), (0.6, 1.05), (1.1, 0.8), (1.25, 0.3), (0.9, -0.3), (0.0, -0.55), (-1.0, -0.4)])
    head = circle(1.1, 1.0, 0.5, 40)
    bill = spl([(1.55, 1.1), (3.2, 0.72, 0), (1.55, 0.92)])
    wing = spl([(0.6, 0.85), (-0.3, 0.75), (-1.2, 0.3), (-1.75, -0.05, 0), (-0.8, -0.2), (0.2, -0.15), (0.65, 0.3)])
    tail = poly((-1.4, 0.15), (-2.1, 0.0), (-2.05, -0.3), (-1.35, -0.2))
    legs = [limb([(0.1, -0.5), (0.15, -1.2)], 0.12, 0.1), limb([(0.4, -0.45), (0.5, -1.2)], 0.12, 0.1)]
    feet = []
    for x in (0.15, 0.5):
        feet += [[(x, -1.2), (x + 0.3, -1.25)], [(x, -1.2), (x - 0.2, -1.25)]]
    front = [wing, bill, head, body, tail, *legs]
    sil = hide(union(head, bill, body, tail, *legs), wing) + [wing]
    bars = keep([[(0.95 + 0.15 * k, 1.5), (1.0 + 0.15 * k, 1.2)] for k in range(3)], head)
    pattern = keep([lens((x, y), (x - 0.45, y - 0.12), 0.3) for x, y in [(0.3, 0.55), (-0.3, 0.45), (-0.9, 0.2), (0.1, 0.1), (-0.5, 0.05)]], wing)
    G = -1.25
    ground = [[(-3.3, G), (3.3, G)]]
    leaves = []
    for x, y, a in [(-2.6, G, 0.2), (-1.4, G, -0.15), (1.6, G, 0.1), (2.6, G, -0.2), (-2.0, G - 0.5, 0.0), (1.0, G - 0.6, 0.15), (2.2, G - 0.9, -0.1),
                    (-0.6, G - 0.9, 0.1)]:
        leaves += leaf((x, y), (x + 0.9 * math.cos(a), y + 0.9 * math.sin(a) + 0.05), 0.3)
    leaves = hide(leaves, *front)
    ferns = hide(palm_frond((-2.8, G), (-3.2, 1.6), 0.1) + palm_frond((2.8, G), (3.2, 1.4), -0.1), *front)
    return make("Woodcock in the Leaf Litter", sil + bars + pattern + feet + ground + leaves + ferns, [eye(1.05, 1.08, 0.08)])


@design("woodland_ruffed_grouse", T)
def ruffed_grouse(rng):
    log = limb([(-3.3, -1.2), (2.6, -1.2)], 1.0, 1.0, cap0=False, cap1=False, smooth=False)
    log_end = ellipse(2.6, -1.2, 0.25, 0.5, 40)
    body = spl([(-1.3, -0.3), (-1.2, 0.4), (-0.4, 0.9), (0.4, 1.1), (0.85, 0.9), (1.0, 0.2), (0.7, -0.45), (0.0, -0.7), (-0.9, -0.6)])
    head = spl([(0.45, 1.3), (0.6, 1.8), (0.75, 2.25, 0), (1.0, 1.95), (1.3, 1.85), (1.45, 1.65), (1.2, 1.4), (0.85, 1.2)])
    beak = spl([(1.4, 1.75), (1.65, 1.62, 0), (1.38, 1.55)])
    ruff = spl([(0.35, 1.45), (0.1, 1.15), (0.2, 0.7), (0.55, 0.75), (0.75, 1.1)])
    ruff_f = fringe(spl([(0.35, 1.45), (0.05, 1.15), (0.2, 0.7)], closed=False), 0.12, 4)
    fan = []
    for k in range(5):
        a = math.radians(150 + 17 * k)
        fan.append(lens((-1.1, -0.1), (-1.1 + 1.8 * math.cos(a), -0.1 + 1.6 * math.sin(a) * 0.8 + 0.5), 0.2))
    band = [arc(-1.1, -0.1, 1.45, math.radians(148), math.radians(228), 20)]
    wing = spl([(0.6, 0.6), (-0.1, 0.55), (-0.8, 0.1), (-1.0, -0.25, 0), (-0.3, -0.35), (0.4, -0.15)])
    legs = [limb([(0.05, -0.6), (0.1, -0.72)], 0.22, 0.2), limb([(0.4, -0.55), (0.45, -0.72)], 0.22, 0.2)]
    front = [ruff, wing, beak, head, body, *legs]
    sil = hide(union(head, beak, body, *legs), wing, ruff) + [wing] + hide([ruff], wing)
    fv = []
    for i, f in enumerate(fan):
        fv += hide([f], *fan[i + 1:])
    fv = hide(fv + keep(band, *fan), *front)
    wbars = keep([quad((0.3, 0.4 - 0.25 * k), (-0.2, 0.3 - 0.25 * k), (-0.6, 0.05 - 0.2 * k), 6) for k in range(3)], wing)
    lg = hide([log, log_end, ellipse(2.6, -1.2, 0.12, 0.25, 20)], *front, *fan)
    bark = hide([[(-2.8, -0.95), (-1.6, -0.95)], [(-2.4, -1.45), (-0.4, -1.45)], [(0.6, -1.4), (2.1, -1.4)]], *front, *fan)
    beats = [arc(0.9, 0.4, r, -0.5, 0.6, 8) for r in (0.6, 0.85)]
    beats = [transform(b, 0.5, 0.0) for b in beats]
    ground = [[(-3.3, -1.7), (3.3, -1.7)]]
    ground = hide(ground, log, log_end)
    ferns = hide(palm_frond((-2.9, -1.7), (-3.2, 1.2), 0.1), log) + hide(palm_frond((3.0, -1.7), (3.3, 0.8), -0.1), log, log_end)
    return make("Ruffed Grouse Drumming on a Log", sil + [ruff_f] + fv + wbars + lg + bark + beats + ground + ferns, [eye(1.05, 1.72, 0.06)])


# ================================================================== flowers, trees and places

def petal_flower(cx, cy, r, n=5, rot=0.0, bulge=0.45, notch=False, centre=0.12):
    out = []
    for k in range(n):
        a = rot + TAU * k / n
        tip = (cx + r * math.cos(a), cy + r * math.sin(a))
        if notch:
            m = (cx + r * 0.82 * math.cos(a), cy + r * 0.82 * math.sin(a))
            pa = (cx + r * math.cos(a - 0.35), cy + r * math.sin(a - 0.35))
            pb = (cx + r * math.cos(a + 0.35), cy + r * math.sin(a + 0.35))
            out.append(chain(quad((cx, cy), (cx + 0.9 * r * math.cos(a - 0.55), cy + 0.9 * r * math.sin(a - 0.55)), pa, 10),
                             quad(pa, (m[0] + 0.05 * math.cos(a), m[1] + 0.05 * math.sin(a)), m, 5)[1:],
                             quad(m, (m[0] + 0.05 * math.cos(a), m[1] + 0.05 * math.sin(a)), pb, 5)[1:],
                             quad(pb, (cx + 0.9 * r * math.cos(a + 0.55), cy + 0.9 * r * math.sin(a + 0.55)), (cx, cy), 10)[1:]))
        else:
            out.append(lens((cx, cy), tip, bulge))
    petals = union(*out)
    c = circle(cx, cy, centre * r / 0.5 if centre else 0.0, 14)
    return hide(petals, c) + ([c] if centre else []), out + [c]


@design("woodland_trillium", T)
def trillium(rng):
    out = []
    for cx, cy, s in [(-0.9, 0.6, 1.0), (1.6, -0.3, 0.75)]:
        stem = [[(cx, cy - 0.6 * s), (cx + 0.05, -2.6)]]
        leaves = []
        for k in range(3):
            a = math.radians(-90 + 120 * k + 30)
            tip = (cx + 1.7 * s * math.cos(a), cy - 0.6 * s + 0.85 * s * math.sin(a))
            leaves.append(lens((cx, cy - 0.6 * s), tip, 0.32))
        petals = []
        for k in range(3):
            a = math.radians(90 + 120 * k)
            tip = (cx + 1.0 * s * math.cos(a), cy + 0.7 * s * math.sin(a) + 0.15 * s)
            petals.append(lens((cx, cy), tip, 0.38))
        sepals = []
        for k in range(3):
            a = math.radians(30 + 120 * k)
            tip = (cx + 0.85 * s * math.cos(a), cy + 0.6 * s * math.sin(a))
            sepals.append(lens((cx, cy), tip, 0.18))
        centre = circle(cx, cy, 0.14 * s, 14)
        pv = union(*petals)
        sv = hide(sepals, *petals)
        lv = hide(leaves, *petals, *sepals)
        veins = hide(keep([[(cx, cy - 0.6 * s), (cx + 1.4 * s * math.cos(math.radians(-90 + 120 * k + 30)),
                                                  cy - 0.6 * s + 0.7 * s * math.sin(math.radians(-90 + 120 * k + 30)))] for k in range(3)], *leaves),
                     *petals, *sepals)
        pveins = keep([[(cx, cy), (cx + 0.7 * s * math.cos(math.radians(90 + 120 * k)), cy + 0.5 * s * math.sin(math.radians(90 + 120 * k)) + 0.1 * s)]
                       for k in range(3)], *petals)
        st = hide(stem, *leaves, *petals)
        out.append((pv + sv + lv + veins + hide(pveins, centre) + [centre] + st, petals + sepals + leaves))
    a, b = out
    strokes = a[0] + hide(b[0], *a[1])
    ground = [[(-3.3, -2.6), (3.3, -2.6)]]
    leaves_g = [lens((-3.0, -2.6), (-2.1, -2.45), 0.3), lens((2.3, -2.6), (3.2, -2.5), 0.3)]
    return make("White Trillium Flowers", strokes + ground + leaves_g)


@design("woodland_primroses", T)
def primroses(rng):
    leaves = []
    for a, L in [(150, 2.6), (120, 2.4), (95, 2.0), (65, 2.3), (35, 2.6), (170, 2.2), (10, 2.3)]:
        r = math.radians(a)
        tip = (L * math.cos(r), -1.9 + L * math.sin(r) * 0.8)
        leaves.append(lens((0.0, -1.9), tip, 0.2))
    lv = []
    for i, l in enumerate(leaves):
        lv += hide([l], *leaves[i + 1:])
    flowers, covers = [], []
    for cx, cy, r in [(-1.2, 0.6, 0.6), (0.2, 1.3, 0.62), (1.4, 0.45, 0.58), (-0.4, -0.3, 0.55), (0.9, -0.6, 0.5), (-1.9, -0.6, 0.48)]:
        st, cv = petal_flower(cx, cy, r, 5, rot=math.pi / 2, notch=True, centre=0.11)
        flowers.append(st)
        covers.append(chain(*[c for c in cv[:-1]]))
    fv = []
    allc = [circle(cx, cy, r, 40) for cx, cy, r in [(-1.2, 0.6, 0.6), (0.2, 1.3, 0.62), (1.4, 0.45, 0.58), (-0.4, -0.3, 0.55), (0.9, -0.6, 0.5),
                                                       (-1.9, -0.6, 0.48)]]
    for i, f in enumerate(flowers):
        fv += hide(f, *allc[i + 1:])
    stems = [[(cx, cy), (0.0, -1.9)] for cx, cy, r in [(-1.2, 0.6, 0.6), (0.2, 1.3, 0.62), (1.4, 0.45, 0.58)]]
    stems = hide(stems, *allc)
    lv = hide(lv, *allc)
    veins = keep([[(0.0, -1.9), (1.8 * math.cos(math.radians(a)), -1.9 + 1.5 * math.sin(math.radians(a)))] for a in (150, 35, 170, 10)], *leaves)
    veins = hide(veins, *allc)
    ground = [[(-3.3, -1.95), (3.3, -1.95)]]
    return make("Clump of Wild Primroses", fv + stems + lv + veins + ground)


@design("woodland_hazelnuts", T)
def hazelnuts(rng):
    branch = limb([(-3.3, 1.6), (-1.0, 1.3), (1.2, 1.5), (3.3, 1.1)], 0.3, 0.2, cap0=False, cap1=True)
    out, covers = [], [branch]
    leaves = []
    for (bx, by), (tx, ty) in [((-2.4, 1.5), (-3.0, 0.2)), ((0.0, 1.38), (0.6, 2.9)), ((2.2, 1.35), (3.0, 2.6)), ((-1.2, 1.35), (-1.8, 2.9))]:
        lf = lens((bx, by), (tx, ty), 0.42)
        leaves.append(lf)
    nuts = []
    for cx, cy in [(-0.8, 0.0), (0.2, -0.3), (1.2, 0.05)]:
        nut = ellipse(cx, cy - 0.35, 0.42, 0.48, 40)
        husk = spl([(cx - 0.5, cy + 0.15), (cx - 0.6, cy + 0.55), (cx - 0.3, cy + 0.85), (cx, cy + 0.65), (cx + 0.3, cy + 0.85), (cx + 0.6, cy + 0.55),
                    (cx + 0.5, cy + 0.15), (cx, cy + 0.05)])
        frill = fringe(spl([(cx - 0.6, cy + 0.55), (cx - 0.3, cy + 0.85), (cx, cy + 0.65), (cx + 0.3, cy + 0.85), (cx + 0.6, cy + 0.55)], closed=False), 0.08, 6)
        tip = [[(cx, cy - 0.83), (cx, cy - 0.75)]]
        nuts.append((nut, husk, frill, tip, [(cx, cy + 0.75), (-0.05 + cx * 0.3, 1.3)]))
    for nut, husk, frill, tip, stem in nuts:
        out += hide([nut], husk) + [husk] + tip + hide([stem], husk, branch)
    nut_c = [n[0] for n in nuts] + [n[1] for n in nuts]
    lv = hide(leaves, *nut_c, branch)
    veins = []
    for (bx, by), (tx, ty) in [((-2.4, 1.5), (-3.0, 0.2)), ((0.0, 1.38), (0.6, 2.9)), ((2.2, 1.35), (3.0, 2.6)), ((-1.2, 1.35), (-1.8, 2.9))]:
        veins.append([(bx, by), (bx + (tx - bx) * 0.85, by + (ty - by) * 0.85)])
    veins = hide(veins, *nut_c, branch)
    catkins = []
    for x, y in [(2.0, 1.25), (2.5, 1.15)]:
        c = [(x + 0.08 * math.sin(i * 0.6), y - 0.12 * i) for i in range(14)]
        catkins.append(tube(c, 0.18))
    ground_nut = [ellipse(-2.2, -2.2, 0.4, 0.46, 30), [(-2.2, -1.74), (-2.2, -1.65)], ellipse(2.4, -2.3, 0.3, 0.2, 20), ellipse(2.4, -2.35, 0.15, 0.08, 12)]
    ground = [[(-3.3, -2.7), (3.3, -2.7)]]
    return make("Hazelnuts on the Branch", [branch] + out + lv + veins + catkins + ground_nut + ground)


@design("woodland_silver_birches", T)
def silver_birches(rng):
    G = -2.8
    trunks = []
    for x0, lean, w in [(-1.7, 0.15, 0.55), (0.3, -0.05, 0.65), (2.0, -0.2, 0.5)]:
        c = [(x0 + lean * t, G + t) for t in [6.3 * i / 30 for i in range(31)]]
        trunks.append(tube(c, lambda t, w=w: w * (1 - 0.35 * t), cap=False))
    vis = []
    for i, t in enumerate(trunks):
        vis += hide([t], *trunks[i + 1:])
    marks = []
    for (x0, lean, w), tr in zip([(-1.7, 0.15, 0.55), (0.3, -0.05, 0.65), (2.0, -0.2, 0.5)], trunks):
        for k, t in enumerate([0.5, 1.2, 1.9, 2.7, 3.4, 4.2, 5.0]):
            x = x0 + lean * t
            ww = w * (1 - 0.35 * t / 6.3) / 2
            side = -1 if k % 2 else 1
            marks.append(lens((x + side * ww, G + t), (x + side * ww * 0.1, G + t + 0.06), 0.25))
    marks = keep(marks, *trunks)
    marks = [m for i, m in enumerate(marks)]
    leaves = []
    for x, y in [(-2.6, 2.6), (-2.1, 1.9), (-0.8, 2.9), (-0.5, 2.2), (1.1, 2.7), (1.3, 1.9), (2.7, 2.6), (2.9, 1.8), (-2.8, 1.2)]:
        leaves += [[(x, y + 0.3), (x, y)], lens((x, y), (x - 0.08, y - 0.4), 0.4)]
    twigs = [spl([(-1.4, 2.6), (-2.2, 3.1), (-2.9, 2.9)], closed=False), spl([(0.25, 2.8), (1.0, 3.2), (1.6, 3.1)], closed=False),
             spl([(1.6, 2.3), (2.6, 2.9), (3.1, 2.7)], closed=False), spl([(-1.5, 1.7), (-2.4, 2.1)], closed=False)]
    tw = hide(twigs, *trunks)
    ground = [[(-3.3, G), (3.3, G)]]
    ground = hide(ground, *trunks)
    grass = tuft(-2.8, G, 0.7) + tuft(-0.7, G, 0.6) + tuft(1.2, G, 0.6) + tuft(3.0, G, 0.6)
    return make("Silver Birch Grove", vis + marks + leaves + tw + ground + grass)


# dropped: the subject repeats another book
def stepping_stones(rng):
    lb = spl([(-3.3, -3.0), (-1.8, -1.6), (-1.6, -0.4), (-0.6, 0.6), (-0.3, 1.3)], closed=False)
    rb = spl([(3.3, -2.6), (1.6, -1.5), (1.1, -0.3), (0.6, 0.6), (0.35, 1.3)], closed=False)
    stones = [ellipse(-0.9, -2.0, 0.55, 0.25, 30), ellipse(0.35, -1.55, 0.5, 0.22, 30), ellipse(-0.3, -0.85, 0.42, 0.18, 30),
              ellipse(0.6, -0.3, 0.36, 0.15, 30), ellipse(0.05, 0.25, 0.3, 0.12, 30)]
    tops = [arc(cx, cy + 0.05, rx * 0.9, 0.3, math.pi - 0.3, 10) for cx, cy, rx in [(-0.9, -2.0, 0.55), (0.35, -1.55, 0.5)]]
    flow = [[(-1.4, -2.6), (-0.4, -2.65)], [(0.5, -2.2), (1.3, -2.25)], [(-0.9, -1.3), (-0.3, -1.35)], [(0.2, -0.55), (0.8, -0.6)]]
    flow = hide(flow, *stones)
    trees = []
    for x, y, r in [(-2.6, 0.2, 0.9), (-1.6, 1.3, 0.6), (-0.9, 1.9, 0.4), (2.5, 0.4, 0.85), (1.6, 1.4, 0.6), (0.9, 1.95, 0.38)]:
        trees.append(crown(x, y + r * 0.7, r, r * 0.8, 7, 0.15, seed=x))
    tv = []
    for i, t in enumerate(trees):
        tv += hide([t], *[trees[j] for j in range(len(trees)) if j < i and ((j < 3) == (i < 3))])
    trunks = []
    for x, y, r in [(-2.6, 0.2, 0.9), (-1.6, 1.3, 0.6), (2.5, 0.4, 0.85), (1.6, 1.4, 0.6)]:
        trunks += [[(x - 0.08, y), (x - 0.08, y - 0.5 * r)], [(x + 0.08, y), (x + 0.08, y - 0.5 * r)]]
    trunks = hide(trunks, *trees)
    banks = hide([lb, rb], *trees)
    ferns = palm_frond((-2.6, -1.8), (-3.3, -0.4), 0.1) + palm_frond((2.4, -1.9), (3.3, -0.9), -0.1)
    reeds = [quad((1.9, -1.9), (2.0, -1.2), (1.8, -0.7), 8), quad((2.1, -1.95), (2.25, -1.3), (2.2, -0.8), 8)]
    return make("Stepping Stones across a Woodland Brook", banks + stones + tops + flow + tv + trunks + ferns + reeds)


@design("woodland_treehouse", T)
def treehouse(rng):
    G = -3.0
    trunk = [spl([(-0.9, G), (-0.7, -1.5), (-0.75, 0.6)], closed=False), spl([(0.9, G), (0.7, -1.5), (0.75, 0.6)], closed=False)]
    roots = [quad((-0.9, G + 0.4), (-1.2, G + 0.1), (-1.7, G), 8), quad((0.9, G + 0.4), (1.2, G + 0.1), (1.7, G), 8)]
    canopy = crown(0.0, 2.3, 3.0, 1.05, 12, 0.13, seed=0.4)
    platform = rect(-2.2, 0.25, 2.2, 0.5)
    house = rect(-1.4, 0.5, 1.2, 2.0)
    roof = poly((-1.7, 1.95), (1.5, 1.95), (-0.1, 2.85))
    door = chain([(-0.9, 0.5), (-0.9, 1.4)], arc(-0.6, 1.4, 0.3, math.pi, 0.0, 10), [(-0.3, 0.5)])
    win = [circle(0.55, 1.35, 0.3, 24), [(0.25, 1.35), (0.85, 1.35)], [(0.55, 1.05), (0.55, 1.65)]]
    rail = [[(-2.2, 1.0), (-1.4, 1.0)], [(1.2, 1.0), (2.2, 1.0)], [(-2.1, 0.5), (-2.1, 1.0)], [(2.1, 0.5), (2.1, 1.0)], [(1.65, 0.5), (1.65, 1.0)]]
    planks = [[(-1.4 + 0.5 * k, 0.5), (-1.4 + 0.5 * k, 2.0)] for k in range(1, 5)]
    planks = hide(planks, door, *[win[0]])
    house_c = poly((-1.7, 0.25), (2.2, 0.25), (2.2, 2.0), (1.5, 1.95), (-0.1, 2.85), (-1.7, 1.95))
    cv = hide([canopy], house_c, platform)
    tr = hide(trunk, platform)
    ladder = [[(1.2, 0.25), (1.4, G)], [(1.65, 0.25), (1.85, G)]] + [[(1.2 + 0.2 * t / 3.25, 0.25 - t), (1.65 + 0.2 * t / 3.25, 0.25 - t)] for t in
                                                                      [0.45 * i for i in range(1, 8)]]
    tr = hide(tr, poly((1.15, 0.25), (1.7, 0.25), (1.9, G), (1.35, G)))
    swing = [[(-2.4, 1.2), (-2.4, -1.8)], [(-1.7, 1.2), (-1.7, -1.8)], rect(-2.6, -2.0, -1.5, -1.8)]
    swing = hide(swing, platform)
    branchs = hide([spl([(-0.7, 0.3), (-1.8, 0.9), (-2.6, 1.4)], closed=False)], platform, house_c)
    ground = [[(-3.3, G), (3.3, G)]]
    grass = tuft(-2.9, G, 0.6) + tuft(2.8, G, 0.6) + tuft(-0.2, G, 0.5)
    leafy = keep([arc(x, y, 0.35, 0.3, 2.8, 10) for x, y in [(-2.3, 2.6), (-1.6, 3.0), (1.6, 3.0), (2.4, 2.5), (-2.6, 1.8), (2.6, 1.7)]], canopy)
    leafy = hide(leafy, house_c)
    return make("Treehouse in an Old Oak", [platform, house, roof, door] + win + rail + planks + cv + tr + roots + ladder + swing + branchs +
                ground + grass + leafy)


@design("woodland_wood_anemones", T)
def wood_anemones(rng):
    G = -2.6
    out, covers = [], []
    specs = [(-1.6, 0.9, 0.62, 0.1), (0.2, 1.6, 0.66, 0.4), (1.8, 0.6, 0.6, 0.2), (-0.6, -0.4, 0.58, 0.3), (1.0, -0.8, 0.52, 0.0),
             (-2.4, -0.9, 0.5, 0.5), (2.6, -1.2, 0.45, 0.1)]
    for cx, cy, r, rot in specs:
        st, cv = petal_flower(cx, cy, r, 6, rot=rot, bulge=0.4, centre=0.13)
        out.append(st)
        covers.append(circle(cx, cy, r * 1.02, 40))
    fv = []
    for i, f in enumerate(out):
        fv += hide(f, *covers[:i])
    stems = []
    leaves = []
    for cx, cy, r, rot in specs:
        stems.append([(cx, cy - r * 0.5), (cx + 0.05, G)])
        ly = cy - r - 0.5
        for d in (-1, 1):
            leaves.append(lens((cx, ly), (cx + d * 0.75, ly - 0.15), 0.3))
    lv = hide(leaves, *covers)
    stv = hide(stems, *covers, *leaves)
    stamens = []
    for cx, cy, r, rot in specs:
        stamens += [[(cx + 0.13 * r / 0.5 * math.cos(a), cy + 0.13 * r / 0.5 * math.sin(a)), (cx + 0.22 * r / 0.5 * math.cos(a), cy + 0.22 * r / 0.5 * math.sin(a))]
                    for a in [TAU * k / 6 for k in range(6)]]
    stamens = hide(stamens, *covers[:0])
    stamens = []
    ground = [[(-3.3, G), (3.3, G)]]
    return make("Carpet of Wood Anemones", fv + lv + stv + ground)


@design("woodland_solomons_seal", T)
def solomons_seal(rng):
    G = -2.8
    out = []
    for x0, reach, h, n in [(-2.6, 4.6, 3.0, 6), (-1.6, 3.6, 2.0, 5)]:
        c = quad((x0, G), (x0 + 0.6, G + h * 1.6), (x0 + reach, G + h * 0.9), 40)
        out.append(c)
        for k in range(n):
            i = int(len(c) * (k + 1.5) / (n + 2))
            x, y = c[i]
            a, b = c[i - 1], c[i + 1]
            ang = math.atan2(b[1] - a[1], b[0] - a[0])
            for side in (1,):
                tip = (x + 0.95 * math.cos(ang + 0.5), y + 0.95 * math.sin(ang + 0.5))
                out.append(lens((x, y), tip, 0.3))
            for d in (-0.08, 0.12):
                fy = y - 0.15
                out.append([(x + d, y), (x + d, fy - 0.25)])
                bell = spl([(x + d - 0.1, fy - 0.25), (x + d - 0.12, fy - 0.7), (x + d - 0.18, fy - 0.85, 0), (x + d, fy - 0.8),
                            (x + d + 0.18, fy - 0.85, 0), (x + d + 0.12, fy - 0.7), (x + d + 0.1, fy - 0.25)])
                out.append(bell)
    ground = [[(-3.3, G), (3.3, G)]]
    ferns = palm_frond((2.4, G), (3.0, 0.2), -0.1)
    return make("Solomon's Seal Bells", out + ground + ferns)


@design("woodland_mayapples", T)
def mayapples(rng):
    G = -2.7
    out, covers = [], []
    for cx, cy, r, h in [(-1.4, 1.0, 1.5, 3.7), (1.4, 0.2, 1.3, 2.9)]:
        top = quad((cx - r, cy - 0.3), (cx, cy + 0.65), (cx + r, cy - 0.3), 30)
        n = 6
        scal = []
        pts = []
        for k in range(n + 1):
            pts.append((cx + r - 2 * r * k / n, cy - 0.3 - (0.12 if 0 < k < n else 0.0)))
        for k in range(n):
            p, q = pts[k], pts[k + 1]
            scal += quad(p, ((p[0] + q[0]) / 2, p[1] - 0.35), q, 8)[1:]
        umb_shape = chain(top, scal)
        lobes = [umb_shape]
        umb = [umb_shape]
        ribs = [[(cx, cy + 0.17), p] for p in pts[1:-1]]
        stem = [[(cx - 0.05, cy - 0.1), (cx - 0.05, G)], [(cx + 0.05, cy - 0.1), (cx + 0.05, G)]]
        out.append((umb + ribs, lobes, stem))
    strokes = out[0][0] + hide(out[1][0], *out[0][1])
    stems = hide(out[0][2], *out[1][1]) + hide(out[1][2], *out[0][1])
    fl, _ = petal_flower(-1.4, -0.6, 0.45, 6, rot=0.3, bulge=0.4, centre=0.12)
    fruit = [ellipse(1.4, -1.2, 0.32, 0.38, 24), [(1.4, -0.82), (1.4, -0.6)]]
    stems = hide(stems, circle(-1.4, -0.6, 0.47, 30), fruit[0])
    stems += [[(-1.4, -0.15), (-1.4, 0.85)]]
    stems = hide(stems, circle(-1.4, -0.6, 0.47, 30))
    ground = [[(-3.3, G), (3.3, G)]]
    leaves = [lens((-3.0, G), (-2.2, G + 0.1), 0.3), lens((2.3, G), (3.2, G + 0.05), 0.3)]
    return make("Mayapple Umbrellas", strokes + stems + fl + fruit + ground + leaves)


@design("woodland_jack_in_pulpit", T)
def jack_in_pulpit(rng):
    G = -2.8
    tube_ = spl([(-0.45, -0.6), (-0.5, 0.6), (-0.35, 1.4), (0.35, 1.4), (0.5, 0.6), (0.45, -0.6)], closed=False)
    hood = spl([(-0.35, 1.35), (-0.55, 1.9), (-0.2, 2.5), (0.5, 2.7), (1.2, 2.45, 0), (0.7, 2.15), (0.35, 1.4)])
    hood_in = spl([(-0.25, 1.5), (0.0, 2.1), (0.55, 2.3)], closed=False)
    spadix = rrect(-0.12, 0.6, 0.12, 1.55, 0.12)
    stripes = keep([[(x, -0.5), (x * 1.1, 1.3)] for x in (-0.25, 0.0, 0.25)], tube_ + [tube_[0]])
    stripes = hide(stripes, spadix)
    stem = [[(-0.12, -0.6), (-0.12, G)], [(0.12, -0.6), (0.12, G)]]
    leaf_stem = [spl([(0.5, G), (1.2, -0.5), (1.8, 1.0)], closed=False)]
    leaflets = [lens((1.8, 1.0), (3.1, 1.6), 0.3), lens((1.8, 1.0), (2.2, 2.6), 0.3), lens((1.8, 1.0), (0.9, 2.0), 0.3)]
    lf2 = [spl([(-0.6, G), (-1.4, -0.9), (-1.9, 0.2)], closed=False), lens((-1.9, 0.2), (-3.2, 0.6), 0.3), lens((-1.9, 0.2), (-2.4, 1.6), 0.3),
           lens((-1.9, 0.2), (-1.3, 1.2), 0.3)]
    front = [hood, tube_ + [tube_[0]]]
    lv = hide(leaflets + lf2 + leaf_stem, *front)
    veins = keep([[(1.8, 1.0), (2.9, 1.55)], [(1.8, 1.0), (2.15, 2.4)], [(1.8, 1.0), (1.05, 1.9)], [(-1.9, 0.2), (-3.0, 0.55)],
                  [(-1.9, 0.2), (-2.35, 1.45)], [(-1.9, 0.2), (-1.4, 1.1)]], *leaflets, *lf2[1:])
    veins = hide(veins, *front)
    ground = [[(-3.3, G), (3.3, G)]]
    moss = [arc(x, G, 0.25, 0.0, math.pi, 8) for x in (-2.4, -1.9, 2.0, 2.5)]
    return make("Jack-in-the-Pulpit", [tube_, hood, hood_in] + hide([spadix], hood) + stripes + stem + lv + veins + ground + moss)


@design("woodland_sycamore_seeds", T)
def sycamore_seeds(rng):
    def samara(cx, cy, s, rot):
        pts = []
        wing1 = spl([(0.0, 0.0), (0.3, 0.35), (1.6, 0.55), (2.0, 0.25), (1.5, -0.05), (0.3, -0.12)])
        wing2 = [(x, -y) for x, y in spl([(0.0, 0.0), (-0.3, 0.35), (-1.6, 0.55), (-2.0, 0.25), (-1.5, -0.05), (-0.3, -0.12)])]
        wing2 = spl([(0.0, 0.0), (-0.3, 0.35), (-1.6, 0.55), (-2.0, 0.25), (-1.5, -0.05), (-0.3, -0.12)])
        seeds = [ellipse(0.28, 0.08, 0.25, 0.18, 20), ellipse(-0.28, 0.08, 0.25, 0.18, 20)]
        veins = [spl([(0.4, 0.2), (1.1, 0.35), (1.8, 0.3)], closed=False), spl([(-0.4, 0.2), (-1.1, 0.35), (-1.8, 0.3)], closed=False)]
        parts = hide([wing1, wing2], *seeds) + seeds + hide(veins, *seeds)
        return [transform(p, cx, cy, s, rot) for p in parts], [transform(p, cx, cy, s, rot) for p in [wing1, wing2] + seeds]
    a, ca = samara(-0.5, 0.6, 1.05, -0.5)
    b, cb = samara(1.5, -1.5, 0.75, 0.7)
    c, cc = samara(-1.8, -1.8, 0.6, 2.2)
    swirls = [spiral(1.5, -1.5, 0.9, 1.1, 0.6, 40, rot=1.0), arc(-1.8, -1.8, 0.85, 0.5, 2.6, 16), arc(-0.5, 0.6, 1.5, 3.6, 4.6, 14)]
    swirls = hide(swirls, *ca, *cb, *cc)
    lf = []
    cx, cy = 1.6, 2.0
    lobes = [lens((cx, cy), (cx + 1.3 * math.cos(a), cy + 1.3 * math.sin(a)), 0.38) for a in (math.radians(30), math.radians(90), math.radians(150),
                                                                                              math.radians(-10), math.radians(190))]
    lf = union(*lobes) + [[(cx, cy), (cx + 1.1 * math.cos(a), cy + 1.1 * math.sin(a))] for a in (math.radians(30), math.radians(90), math.radians(150))]
    lf += [[(cx, cy), (cx + 0.2, cy - 0.7)]]
    lf = hide(lf, *ca)
    return make("Spinning Sycamore Seeds", a + hide(b, *ca) + hide(c, *ca) + swirls + lf)


@design("woodland_beech_roots", T)
def beech_roots(rng):
    G = -2.4
    trunk = [spl([(-0.9, 3.4), (-0.85, 1.0), (-1.0, -1.2), (-1.5, G + 0.3)], closed=False),
             spl([(0.9, 3.4), (0.85, 1.0), (1.0, -1.2), (1.5, G + 0.3)], closed=False)]
    roots = []
    for (x0, y0), (x1, y1) in [((-1.3, -1.6), (-3.3, G - 0.25)), ((-0.6, -1.9), (-1.6, G - 0.7)), ((0.3, -1.9), (0.6, G - 0.75)),
                               ((1.1, -1.7), (2.4, G - 0.5)), ((1.4, -1.5), (3.3, G - 0.1))]:
        c = cubic((x0, y0), (x0 + (x1 - x0) * 0.3, y0 - 0.2), (x0 + (x1 - x0) * 0.6, y1 + 0.25), (x1, y1), 30)
        roots.append(tube(c, lambda t: 0.5 * (1 - t) + 0.1, cap=False))
    rv = []
    for i, r in enumerate(roots):
        rv += hide([r], *roots[i + 1:])
    trunk_c = poly((-0.9, 3.4), (0.9, 3.4), (1.0, -1.2), (1.5, G + 0.3), (-1.5, G + 0.3), (-1.0, -1.2))
    rv = hide(rv, poly((-0.85, 3.4), (0.85, 3.4), (0.95, -1.4), (-0.95, -1.4)))
    tr = hide(trunk, *roots)
    ground = [[(-3.3, G), (3.3, G)]]
    ground = hide(ground, *roots)
    branches = [spl([(-0.85, 2.6), (-2.0, 3.0), (-3.2, 3.4)], closed=False), spl([(-0.86, 2.3), (-2.0, 2.7), (-3.2, 3.0)], closed=False),
                spl([(0.85, 2.3), (2.0, 2.8), (3.2, 3.0)], closed=False), spl([(0.86, 2.0), (2.0, 2.5), (3.2, 2.65)], closed=False)]
    lv = []
    for x, y in [(-2.2, 2.75), (-2.9, 3.05), (2.3, 2.5), (2.9, 2.7), (-1.6, 2.6), (1.6, 2.3)]:
        lv.append(lens((x, y), (x + 0.1, y - 0.55), 0.35))
    bark = [[(-0.3, 1.0), (0.1, 1.05)], [(0.2, -0.3), (0.5, -0.25)], [(-0.5, 2.4), (-0.2, 2.45)]]
    heart_c = [heart(0.0, 0.3, 0.35, 60)]
    beechnuts = [spl([(-2.4, G - 0.3), (-2.6, G - 0.1), (-2.3, G + 0.15), (-2.0, G - 0.1), (-2.2, G - 0.3)])]
    beechnuts = []
    return make("Ancient Beech with Spreading Roots", rv + tr + ground + branches + lv + bark + beechnuts)


@design("woodland_honeysuckle", T)
def honeysuckle(rng):
    vine = spl([(-3.0, -3.0), (-2.4, -1.5), (-1.2, -0.8), (-0.3, 0.3), (0.8, 0.9), (1.6, 2.0), (2.5, 2.6)], closed=False)
    vine2 = spl([(-3.0, -3.0), (-2.0, -2.0), (-1.4, -1.2), (-0.6, 0.0), (0.4, 0.6), (1.3, 1.5), (2.5, 2.6)], closed=False)
    out = [vine, vine2]
    leaves = []
    for i in (25, 45, 70, 95):
        x, y = vine[i]
        leaves += [lens((x, y), (x - 0.75, y + 0.45), 0.35), lens((x, y), (x + 0.75, y - 0.4), 0.35)]
    clusters = []
    for cx, cy in [(-0.5, 1.4), (1.9, 0.6), (-1.9, -0.4)]:
        for k in range(4):
            a = math.radians(45 + 32 * k)
            base = (cx, cy)
            tip = (cx + 1.0 * math.cos(a), cy + 1.0 * math.sin(a))
            fl = tube([base, ((cx + tip[0]) / 2, (cy + tip[1]) / 2), tip], lambda t: 0.1 + 0.1 * t)
            lip = quad(tip, (tip[0] + 0.3 * math.cos(a - 1.2), tip[1] + 0.3 * math.sin(a - 1.2)), (tip[0] + 0.25 * math.cos(a - 2.0), tip[1] + 0.25 * math.sin(a - 2.0)), 6)
            stamen = [tip, (tip[0] + 0.35 * math.cos(a), tip[1] + 0.35 * math.sin(a))]
            clusters.append((fl, lip, stamen))
    fls = []
    covs = []
    for fl, lip, st in clusters:
        fls += hide([fl, lip, st], *covs)
        covs.append(fl)
    lv = hide(leaves, *covs)
    vv = hide(out, *covs, *leaves)
    berries = [circle(1.0 + 0.2 * k, -1.6 - 0.15 * (k % 2), 0.13, 12) for k in range(3)]
    bee = [ellipse(2.5, -0.8, 0.28, 0.18, 20), lens((2.45, -0.65), (2.3, -0.25), 0.35), lens((2.6, -0.65), (2.8, -0.3), 0.35),
           [(2.45, -0.95), (2.45, -0.65)], [(2.6, -0.95), (2.6, -0.65)]]
    return make("Twining Honeysuckle", vv + lv + fls + berries + bee)


@design("woodland_tree_stump", T)
def tree_stump(rng):
    top = ellipse(0.0, 0.6, 2.2, 0.75, 90)
    rings = [ellipse(0.1 * k / 4, 0.6, 2.2 * k / 5, 0.75 * k / 5, 60) for k in (1, 2, 3, 4)]
    rings = [ellipse(0.05, 0.6, 2.2 * f, 0.75 * f, 60) for f in (0.2, 0.42, 0.62, 0.82)]
    sides_ = [spl([(-2.2, 0.6), (-2.25, -0.8), (-2.6, -1.8), (-3.2, -2.2)], closed=False), spl([(2.2, 0.6), (2.25, -0.8), (2.6, -1.8), (3.2, -2.2)], closed=False)]
    front_roots = [spl([(-1.2, -0.15), (-1.3, -1.2), (-1.8, -2.3)], closed=False), spl([(0.4, -0.15), (0.5, -1.4), (0.3, -2.4)], closed=False),
                   spl([(1.5, -0.1), (1.7, -1.3), (2.2, -2.2)], closed=False)]
    crack = [[(0.05, 0.6), (0.8, 0.75), (1.4, 0.95)]]
    bark = [[(-1.8, -0.2), (-1.85, -1.0)], [(-0.4, -0.3), (-0.35, -1.5)], [(1.0, -0.2), (1.05, -1.1)]]
    ivy = []
    for x, y in [(-1.95, 0.2), (-1.7, -0.5), (-2.1, -1.2), (-1.6, -1.6)]:
        ivy.append(spl([(x, y), (x - 0.25, y + 0.25), (x - 0.15, y + 0.5, 0), (x, y + 0.35), (x + 0.15, y + 0.5, 0), (x + 0.25, y + 0.25)]))
    vine = [spl([(-2.3, -2.2), (-1.95, -1.4), (-1.9, -0.5), (-1.75, 0.3)], closed=False)]
    stump_shape = chain(top[:46], [(-2.2, 0.6), (-2.3, -2.2), (2.3, -2.2), (2.2, 0.6)])
    ground = [[(-3.3, -2.3), (3.3, -2.3)]]
    axe = []
    sprout = [[(1.5, 1.4), (1.6, 2.4)]] + leaf((1.6, 2.1), (2.3, 2.5), 0.3) + leaf((1.58, 1.8), (0.9, 2.2), 0.3)
    grass = tuft(-2.9, -2.3, 0.7) + tuft(2.9, -2.3, 0.7)
    return make("Old Tree Stump with Growth Rings", [top] + rings + sides_ + hide(front_roots + bark, *ivy) + crack + ivy + hide(vine, *ivy) +
                ground + sprout + grass)


@design("woodland_violets", T)
def violets(rng):
    G = -2.6
    leaves = []
    for cx, cy, s, r in [(-2.0, -1.6, 1.0, 0.3), (2.0, -1.7, 0.95, -0.3), (0.0, -1.9, 0.9, 0.0), (-1.0, -0.9, 0.7, 0.4), (1.1, -0.8, 0.7, -0.4)]:
        h = [(cx + s * 0.75 * x, cy + s * 0.75 * y) for x, y in heart(0, 0, 1.0, 80)]
        leaves.append(h)
    lv = []
    for i, l in enumerate(leaves):
        lv += hide([l], *leaves[i + 1:])
    flowers = []
    covers = []
    for cx, cy, s in [(-1.6, 1.2, 0.8), (0.4, 1.9, 0.75), (1.9, 0.9, 0.7), (-0.4, 0.3, 0.65)]:
        petals = [lens((cx, cy), (cx - 0.5 * s, cy + 0.85 * s), 0.42), lens((cx, cy), (cx + 0.5 * s, cy + 0.85 * s), 0.42),
                  lens((cx, cy), (cx - 0.85 * s, cy - 0.1 * s), 0.42), lens((cx, cy), (cx + 0.85 * s, cy - 0.1 * s), 0.42),
                  lens((cx, cy), (cx, cy - 0.95 * s), 0.5)]
        fv = hide(petals[:2], *petals[2:]) + hide(petals[2:4], petals[4]) + [petals[4]]
        lines = [[(cx, cy - 0.15 * s), (cx, cy - 0.5 * s)], [(cx - 0.12 * s, cy - 0.15 * s), (cx - 0.2 * s, cy - 0.45 * s)],
                 [(cx + 0.12 * s, cy - 0.15 * s), (cx + 0.2 * s, cy - 0.45 * s)]]
        flowers.append((fv + [circle(cx, cy, 0.08 * s, 10)] + lines, petals))
        covers += petals
    fl = []
    for st, cv in flowers:
        fl += st
    lv = hide(lv, *covers)
    stems = [[(cx, cy - 0.9 * s), (cx * 0.3, G)] for cx, cy, s in [(-1.6, 1.2, 0.8), (0.4, 1.9, 0.75), (1.9, 0.9, 0.7), (-0.4, 0.3, 0.65)]]
    stems += [[(cx, cy), (cx * 0.5, G)] for cx, cy, s, r in [(-2.0, -1.6, 1.0, 0.3), (2.0, -1.7, 0.95, -0.3), (0.0, -1.9, 0.9, 0.0),
                                                              (-1.0, -0.9, 0.7, 0.4), (1.1, -0.8, 0.7, -0.4)]]
    lveins = [[(cx, cy + 0.15 * s), (cx, cy - 0.6 * s)] for cx, cy, s, r in [(-2.0, -1.6, 1.0, 0.3), (2.0, -1.7, 0.95, -0.3), (0.0, -1.9, 0.9, 0.0),
                                                                             (-1.0, -0.9, 0.7, 0.4), (1.1, -0.8, 0.7, -0.4)]]
    lv += hide(keep(lveins, *leaves), *covers)
    stems = hide(stems, *covers, *leaves)
    ground = [[(-3.3, G), (3.3, G)]]
    return make("Sweet Wood Violets", fl + lv + stems + ground)


@design("woodland_stile", T)
def stile(rng):
    G = -2.4
    posts = [rect(-1.5, G, -1.2, 0.6), rect(1.2, G, 1.5, 0.6)]
    rails = [rect(-3.3, -0.2, -1.5, 0.05), rect(-3.3, -1.3, -1.5, -1.05), rect(1.5, -0.2, 3.3, 0.05), rect(1.5, -1.3, 3.3, -1.05),
             rect(-1.2, -0.25, 1.2, 0.0), rect(-1.2, -1.35, 1.2, -1.1)]
    step = [rect(-1.9, -1.75, 1.9, -1.55), [(-1.6, -1.75), (-1.6, G)], [(1.6, -1.75), (1.6, G)]]
    path = [spl([(-2.6, G - 0.6), (-1.0, G), (-0.5, -0.3), (-0.2, 1.0)], closed=False), spl([(2.6, G - 0.6), (1.0, G), (0.5, -0.3), (0.2, 1.0)], closed=False)]
    trees = [crown(-2.3, 2.2, 1.1, 0.9, 8, 0.14, seed=0.1), crown(2.3, 2.3, 1.1, 0.9, 8, 0.14, seed=0.5), crown(0.0, 2.0, 0.7, 0.55, 7, 0.14, seed=0.9)]
    tv = hide(trees[:2], trees[2]) + [trees[2]]
    trunks = [[(-2.4, 1.3), (-2.4, 0.15)], [(-2.15, 1.3), (-2.15, 0.15)], [(2.2, 1.4), (2.2, 0.15)], [(2.45, 1.4), (2.45, 0.15)],
              [(-0.08, 1.45), (-0.08, 0.95)], [(0.08, 1.45), (0.08, 0.95)]]
    front = posts + rails + [step[0]]
    vis = hide(rails, *posts) + posts + [step[0]] + hide(step[1:], *posts)
    pv = hide(path, *front)
    tr = hide(trunks, *front, *trees)
    tv = hide(tv, *front)
    grain = keep([[(-1.35, G + 0.3), (-1.35, -0.4)], [(1.35, G + 0.3), (1.35, -0.4)]], *posts)
    grain = hide(grain, *rails, step[0])
    ground = [[(-3.3, G), (3.3, G)]]
    ground = hide(ground, *posts)
    flowers = tuft(-2.8, G, 0.7) + tuft(2.8, G, 0.7) + tuft(-0.7, G - 0.3, 0.4)
    sign = [rect(1.7, 0.7, 2.9, 1.15), [(2.3, 0.7), (2.3, 0.05)], poly((2.9, 0.7), (3.15, 0.925), (2.9, 1.15), closed=False)]
    sign = hide(sign, *trees)
    return make("Wooden Stile on a Woodland Path", vis + pv + tr + tv + grain + ground + flowers)
