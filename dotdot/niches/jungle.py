"""Jungle & Rainforest niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "jungle"


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


# ================================================================== big cats

@design("jungle_jaguar_drinking", T)
def jaguar_drinking(rng):
    body = spl([(-2.2, 0.15), (-1.9, 0.6), (-1.0, 0.85), (0.2, 0.7), (1.0, 0.9), (1.45, 0.75), (1.75, 0.2),
                (1.4, -0.5), (0.4, -0.75), (-0.8, -0.75), (-1.8, -0.55)])
    neck = limb([(1.1, 0.35), (1.7, 0.0), (2.15, -0.35)], 0.95, 0.75)
    head = spl([(1.8, -0.1), (2.1, 0.15), (2.45, 0.12), (2.72, -0.1), (2.88, -0.45), (2.95, -0.78), (2.75, -0.95),
                (2.45, -0.95), (2.1, -0.82), (1.85, -0.5)])
    ear = spl([(1.98, 0.02), (1.9, 0.33), (2.1, 0.42), (2.3, 0.12)])
    fl_near = limb([(1.15, 0.0), (0.85, -0.75), (1.4, -1.12), (1.85, -1.18)], 0.62, 0.3)
    fl_far = limb([(1.5, -0.1), (1.35, -0.85), (1.95, -1.1), (2.3, -1.12)], 0.55, 0.28)
    thigh = ellipse(-1.35, -0.2, 0.75, 0.62, 60, rot=0.3)
    hl_near = limb([(-1.2, -0.45), (-1.95, -0.95), (-1.5, -1.18), (-0.8, -1.2)], 0.5, 0.3)
    hl_far = limb([(-0.9, -0.5), (-1.3, -1.0), (-0.6, -1.15), (-0.3, -1.17)], 0.45, 0.28)
    tail = limb([(-2.05, 0.35), (-2.65, 0.0), (-2.95, -0.7), (-2.6, -1.15), (-2.1, -1.15)], 0.3, 0.2)
    front = [fl_near, ear, head, neck, body, thigh, hl_near, tail]
    sil = union(head, neck, body, thigh, hl_near, tail, fl_near)
    near_leg = [arc(1.0, -0.62, 0.3, 2.2, 3.9, 10)]
    far = hide([fl_far, hl_far], *front)
    thigh_line = [arc(-1.35, -0.2, 0.75, 0.9, 2.3, 14)]
    ear_l = hide([ear], head)
    ros = []
    for x, y in [(-1.6, 0.35), (-1.0, 0.5), (-0.4, 0.45), (0.2, 0.4), (0.8, 0.5), (-1.3, -0.1), (-0.7, 0.0),
                 (-0.1, 0.0), (0.5, 0.05), (-0.4, -0.45), (0.25, -0.4), (-1.6, -0.45), (1.3, 0.35), (2.45, -0.35)]:
        ros.append(ellipse(x, y, 0.15, 0.12, 14, rot=x))
    ros = keep(ros, body, head, thigh)
    ros = hide(ros, fl_near)
    nose = [poly((2.82, -0.68), (2.97, -0.74), (2.88, -0.84))]
    mouth = [quad((2.88, -0.86), (2.7, -0.9), (2.58, -0.82), 8)]
    lid = [quad((2.35, -0.45), (2.48, -0.52), (2.6, -0.45), 8)]
    bank = [[(-3.3, -1.28), (1.0, -1.28)], quad((1.0, -1.28), (1.6, -1.3), (1.9, -1.55), 10)]
    water = [ripples(1.9, 3.4, -1.6, 3), ripples(1.2, 3.4, -1.95, 4), ripples(-0.5, 3.4, -2.3, 5),
             arc(2.95, -1.3, 0.25, math.pi + 0.3, TAU - 0.3, 12), arc(2.95, -1.3, 0.45, math.pi + 0.35, TAU - 0.35, 14)]
    water = hide(water, head)
    plants = tuft(0.2, -1.28, 0.5) + leaf((-3.3, -1.28), (-3.25, 0.6), 0.22)
    plants = hide(plants, tail, *front)
    return make("Jaguar Crouched to Drink", sil + near_leg + far + ear_l + ros + nose + mouth + lid +
                bank + water + plants)


@design("jungle_bengal_tiger", T)
def bengal_tiger(rng):
    body = spl([(-2.1, 0.55), (-1.6, 1.0), (-0.5, 1.05), (0.7, 1.0), (1.5, 1.1), (1.95, 0.75), (1.85, 0.0),
                (1.2, -0.3), (0.0, -0.25), (-1.2, -0.2), (-2.05, 0.0)])
    head = spl([(1.75, 1.15), (2.0, 1.45), (2.45, 1.5), (2.85, 1.3), (3.1, 0.95), (3.12, 0.62), (2.9, 0.42),
                (2.5, 0.3), (2.05, 0.35), (1.75, 0.6)])
    ruff = fringe(spl([(1.85, 1.1), (1.7, 0.75), (1.95, 0.42), (2.4, 0.28)], closed=False), -0.12, 5)
    ears = [spl([(1.95, 1.38), (1.9, 1.68), (2.12, 1.75), (2.25, 1.48)]), spl([(2.3, 1.48), (2.35, 1.78), (2.58, 1.76), (2.6, 1.46)])]
    fl = limb([(1.35, 0.5), (1.6, -0.45), (1.5, -1.15)], 0.62, 0.36)
    fl_paw = ellipse(1.68, -1.3, 0.3, 0.15, 30)
    ff = limb([(0.95, 0.4), (0.85, -0.45), (0.6, -1.15)], 0.55, 0.32)
    ff_paw = ellipse(0.75, -1.3, 0.28, 0.14, 30)
    thigh = ellipse(-1.45, 0.35, 0.65, 0.72, 60)
    hl = limb([(-1.35, 0.1), (-1.0, -0.55), (-1.6, -1.05), (-1.45, -1.2)], 0.55, 0.32)
    hl_paw = ellipse(-1.3, -1.3, 0.28, 0.14, 30)
    hf = limb([(-0.85, 0.1), (-0.45, -0.5), (-0.95, -1.05), (-0.85, -1.2)], 0.5, 0.3)
    hf_paw = ellipse(-0.7, -1.3, 0.26, 0.13, 30)
    tail = limb([(-2.0, 0.65), (-2.7, 0.55), (-3.1, -0.05), (-2.95, -0.75), (-2.65, -0.85)], 0.3, 0.22)
    front = [head, fl, fl_paw, body, thigh, hl, hl_paw, tail]
    sil = union(head, body, fl, fl_paw, thigh, hl, hl_paw, tail)
    far = hide([ff, ff_paw, hf, hf_paw], *front)
    ear_l = hide(ears, head) + [arc(2.08, 1.5, 0.08, 0.3, 2.8, 6), arc(2.45, 1.52, 0.08, 0.3, 2.8, 6)]
    thigh_line = [arc(-1.45, 0.35, 0.65, 3.5, 5.6, 16)]
    stripes = []
    for k, x in enumerate([-1.7, -1.25, -0.8, -0.35, 0.1, 0.55, 1.0, 1.4]):
        top = 1.1 if x < 1.3 else 1.2
        stripes.append(lens((x, top + 0.05), (x + 0.18, 0.45 - 0.08 * (k % 2)), 0.1))
        stripes.append(lens((x + 0.12, -0.3), (x + 0.04, 0.05 + 0.08 * (k % 2)), 0.12))
    for y in (-0.1, -0.5, -0.85):
        stripes.append(lens((1.2, y), (1.55, y + 0.08), 0.15))
        stripes.append(lens((-1.85, y + 0.2), (-1.45, y + 0.28), 0.15))
    for t in (0.3, 0.55, 0.8):
        x = -2.6 - 0.35 * t
        stripes.append(lens((x - 0.25, 0.6 - 1.3 * t), (x + 0.25, 0.6 - 1.3 * t + 0.1), 0.12))
    stripes = keep(stripes, body, thigh, tail, fl, hl)
    stripes = hide(stripes, head)
    face = [lens((2.35, 1.35), (2.55, 1.05), 0.15), lens((2.75, 1.25), (2.65, 1.02), 0.15),
            poly((2.95, 0.78), (3.1, 0.72), (3.05, 0.6)), quad((3.05, 0.6), (2.95, 0.48), (2.8, 0.52), 8),
            quad((2.95, 0.48), (2.7, 0.4), (2.55, 0.5), 8)]
    ground = [[(-3.3, -1.45), (3.3, -1.45)]]
    grass = tuft(-2.4, -1.45, 0.7) + tuft(2.6, -1.45, 0.8) + tuft(0.1, -1.45, 0.5)
    ferns = [leaf((-3.3, -1.45), (-3.0, 1.2), 0.18), leaf((3.3, -1.45), (3.1, 0.2), 0.2)]
    return make("Bengal Tiger Prowling", sil + far + ear_l + thigh_line + stripes + face + [ruff] + ground +
                hide(grass + [s for f in ferns for s in f], *front), [eye(2.62, 0.95, 0.07)])


# ================================================================== bears & apes

@design("jungle_sun_bear", T)
def sun_bear(rng):
    body = spl([(0.0, 0.95), (0.9, 0.8), (1.3, 0.0), (1.25, -1.0), (0.9, -1.75), (0.0, -1.9), (-0.9, -1.75),
                (-1.25, -1.0), (-1.3, 0.0), (-0.9, 0.8)])
    head = spl([(0.0, 2.35), (0.7, 2.2), (0.95, 1.65), (0.8, 1.05), (0.0, 0.75), (-0.8, 1.05), (-0.95, 1.65), (-0.7, 2.2)])
    ears = [circle(0.82, 2.2, 0.22, 24), circle(-0.82, 2.2, 0.22, 24)]
    muzzle = spl([(0.0, 1.55), (0.42, 1.4), (0.45, 1.05), (0.0, 0.88), (-0.45, 1.05), (-0.42, 1.4)])
    nose = spl([(0.0, 1.42), (0.18, 1.36), (0.12, 1.25), (0.0, 1.22), (-0.12, 1.25), (-0.18, 1.36)])
    mouth = [quad((0.0, 1.22), (0.0, 1.05), (0.22, 1.02), 6), quad((0.0, 1.22), (0.0, 1.05), (-0.22, 1.02), 6)]
    bib = [chain(quad((-0.75, 0.55), (-0.5, -0.25), (0.0, -0.3), 14), quad((0.0, -0.3), (0.5, -0.25), (0.75, 0.55), 14)),
           chain(quad((-0.4, 0.62), (-0.25, 0.08), (0.0, 0.05), 12), quad((0.0, 0.05), (0.25, 0.08), (0.4, 0.62), 12))]
    bib = [chain(bib[0], bib[1][::-1], [bib[0][0]])]
    arm_r = limb([(1.0, 0.55), (1.85, 1.0), (2.15, 1.85)], 0.6, 0.48)
    arm_l = limb([(-1.0, 0.55), (-1.85, 1.0), (-2.15, 1.85)], 0.6, 0.48)
    claws = []
    for s in (1, -1):
        for k in range(4):
            x = s * (1.95 + 0.13 * k)
            claws.append(quad((x, 2.0), (x + s * 0.05, 2.35), (x - s * 0.1, 2.45), 8))
    leg_r = limb([(0.7, -1.4), (0.85, -2.3), (1.0, -2.55)], 0.7, 0.55)
    leg_l = limb([(-0.7, -1.4), (-0.85, -2.3), (-1.0, -2.55)], 0.7, 0.55)
    feet = [ellipse(1.15, -2.7, 0.45, 0.2, 30), ellipse(-1.15, -2.7, 0.45, 0.2, 30)]
    sil = union(body, head, ears[0], ears[1], arm_r, arm_l, leg_r, leg_l, feet[0], feet[1])
    toes = []
    for s in (1, -1):
        for k in range(3):
            x = s * (1.0 + 0.16 * k)
            toes.append([(x, -2.9), (x + s * 0.05, -2.75)])
    inner_ears = [arc(0.82, 2.2, 0.11, 0, TAU, 14), arc(-0.82, 2.2, 0.11, 0, TAU, 14)]
    inner_ears = hide(inner_ears, head)
    ground = [[(-3.0, -2.92), (-1.6, -2.92)], [(1.6, -2.92), (3.0, -2.92)]]
    plants = leaf((-2.8, -2.92), (-2.6, -0.5), 0.2) + leaf((-2.8, -2.92), (-1.9, -1.2), 0.22) + \
        leaf((2.8, -2.92), (2.6, -0.4), 0.2) + leaf((2.8, -2.92), (1.95, -1.5), 0.22)
    return make("Sun Bear Standing Tall", sil + [muzzle, nose] + mouth + bib + claws + toes + inner_ears + ground + plants,
                [eye(0.35, 1.75, 0.08), eye(-0.35, 1.75, 0.08)])


@design("jungle_orangutan", T)
def orangutan(rng):
    branch = limb([(-3.3, 2.55), (0.0, 2.65), (3.3, 2.5)], 0.42, 0.36, cap0=False, cap1=False)
    head = spl([(0.0, 1.95), (0.65, 1.8), (0.8, 1.2), (0.55, 0.65), (0.0, 0.5), (-0.55, 0.65), (-0.8, 1.2), (-0.65, 1.8)])
    face = spl([(0.0, 1.6), (0.4, 1.55), (0.5, 1.15), (0.38, 0.75), (0.0, 0.62), (-0.38, 0.75), (-0.5, 1.15), (-0.4, 1.55)])
    body = spl([(0.0, 0.65), (0.95, 0.55), (1.4, -0.4), (1.3, -1.4), (0.7, -1.85), (0.0, -1.9), (-0.7, -1.85),
                (-1.3, -1.4), (-1.4, -0.4), (-0.95, 0.55)])
    arm_up = limb([(0.8, 0.4), (1.75, 1.2), (1.35, 2.45)], 0.55, 0.42)
    arm_dn = limb([(-0.85, 0.35), (-1.85, -0.5), (-0.7, -1.05)], 0.55, 0.42)
    leg_l = limb([(-0.6, -1.55), (-1.75, -1.65), (-0.7, -2.3)], 0.62, 0.42)
    leg_r = limb([(0.6, -1.55), (1.75, -1.65), (0.7, -2.3)], 0.62, 0.42)
    foot_l = ellipse(-0.45, -2.35, 0.48, 0.2, 30, rot=0.15)
    foot_r = ellipse(0.45, -2.35, 0.48, 0.2, 30, rot=-0.15)
    mom = [head, body, arm_up, arm_dn, leg_l, leg_r, foot_l, foot_r]
    b_head = circle(0.2, -0.2, 0.42, 50)
    b_face = spl([(0.2, -0.02), (0.42, -0.12), (0.4, -0.38), (0.2, -0.5), (0.0, -0.38), (-0.02, -0.12)])
    b_body = ellipse(0.25, -0.9, 0.48, 0.5, 50)
    b_arm = limb([(0.55, -0.7), (0.95, -0.25), (0.85, 0.25)], 0.22, 0.2)
    baby = [b_head, b_body, b_arm]
    baby_sil = union(*baby)
    mom_sil = hide(union(*mom), *baby)
    br = hide([branch], arm_up)
    fingers = [arc(1.35 + 0.14 * k, 2.6, 0.12, math.pi * 0.15, math.pi * 1.1, 8) for k in (-1, 0, 1)]
    hair = fringe(spl([(1.0, 0.1), (1.55, 0.55), (1.95, 1.3)], closed=False), -0.14, 5) + []
    hair2 = fringe(spl([(-1.1, 0.05), (-1.75, -0.25), (-2.05, -0.55)], closed=False), 0.13, 4)
    hair = hide([hair], *baby)
    face_l = hide([face], *baby)
    mouth = [quad((-0.25, 0.85), (0.0, 0.72), (0.25, 0.85), 8)]
    nostr = [circle(-0.07, 1.08, 0.04, 8), circle(0.07, 1.08, 0.04, 8)]
    brow = [quad((-0.32, 1.42), (-0.18, 1.48), (-0.05, 1.4), 6), quad((0.32, 1.42), (0.18, 1.48), (0.05, 1.4), 6)]
    b_det = [b_face, quad((0.12, -0.38), (0.2, -0.43), (0.28, -0.38), 6)]
    leaves = leaf((-2.4, 2.55), (-2.0, 1.6), 0.25) + leaf((-2.4, 2.55), (-2.9, 1.7), 0.25) + \
        leaf((2.5, 2.55), (2.9, 1.6), 0.25) + leaf((2.5, 2.55), (2.2, 1.55), 0.25) + leaf((-0.6, 2.75), (-0.2, 3.4), 0.25)
    leaves = hide(leaves, branch)
    return make("Orangutan Mother and Baby", mom_sil + baby_sil + br + fingers + hair + face_l + mouth + nostr + brow +
                b_det + leaves,
                [eye(-0.18, 1.25, 0.07), eye(0.18, 1.25, 0.07), eye(0.12, -0.2, 0.05), eye(0.3, -0.2, 0.05)])


@design("jungle_sloth", T)
def sloth(rng):
    branch = limb([(-3.3, 2.0), (-1.0, 2.15), (1.2, 2.05), (3.3, 2.2)], 0.4, 0.34, cap0=False, cap1=False)
    body = ellipse(-0.2, 0.45, 1.75, 0.8, 80, rot=-0.08)
    head = spl([(1.55, 0.95), (2.15, 0.85), (2.4, 0.35), (2.2, -0.2), (1.75, -0.35), (1.3, -0.15), (1.15, 0.4)])
    face = spl([(1.78, 0.68), (2.12, 0.5), (2.15, 0.1), (1.85, -0.12), (1.5, -0.02), (1.42, 0.35)])
    arms = [limb([(1.2, 0.7), (1.4, 1.5), (1.25, 2.0)], 0.38, 0.3), limb([(0.6, 0.9), (0.55, 1.6), (0.75, 2.05)], 0.36, 0.3),
            limb([(-1.3, 0.85), (-1.5, 1.55), (-1.4, 2.05)], 0.4, 0.32), limb([(-0.7, 0.95), (-0.85, 1.6), (-0.65, 2.1)], 0.36, 0.3)]
    sil = union(body, head, *arms)
    claws = []
    for x, y in [(1.25, 2.05), (0.75, 2.08), (-1.4, 2.1), (-0.65, 2.12)]:
        for k in (-1, 0, 1):
            claws.append(quad((x + 0.1 * k, y), (x + 0.1 * k - 0.05, y + 0.42), (x + 0.1 * k - 0.25, y + 0.36), 8))
    br = hide([branch], *arms)
    claws = hide(claws, branch) + keep(claws, branch)[:0]
    fur = fringe(spl([(-1.9, 0.2), (-1.2, -0.3), (0.0, -0.4), (1.1, -0.2)], closed=False), -0.13, 9)
    masks = [lens((1.55, 0.42), (1.75, 0.05), 0.35), lens((2.02, 0.4), (1.95, 0.02), 0.35)]
    nose = [ellipse(1.85, 0.05, 0.09, 0.06, 14)]
    smile = [quad((1.6, -0.05), (1.82, -0.15), (2.02, -0.05), 8)]
    leaves = []
    for x, d in [(-2.6, -1), (-0.1, 1), (2.6, 1)]:
        leaves += leaf((x, 2.15), (x + 0.35 * d, 3.0), 0.28)
    leaves += leaf((2.9, 2.2), (3.3, 1.3), 0.25) + leaf((-2.9, 2.1), (-3.2, 1.2), 0.25)
    leaves = hide(leaves, branch)
    return make("Three-Toed Sloth Hanging", sil + br + claws + [face, fur] + masks + nose + smile + leaves,
                [eye(1.66, 0.25, 0.07), eye(1.95, 0.24, 0.07)])


# ================================================================== frogs & snakes

@design("jungle_red_eyed_frog", T)
def red_eyed_frog(rng):
    stem = limb([(-3.3, -1.55), (0.0, -1.35), (3.3, -1.6)], 0.38, 0.3, cap0=False, cap1=False)
    head = spl([(0.0, 0.95), (0.75, 0.85), (1.3, 0.45), (1.38, -0.05), (1.05, -0.65), (0.6, -1.1), (0.0, -1.25),
                (-0.6, -1.1), (-1.05, -0.65), (-1.38, -0.05), (-1.3, 0.45), (-0.75, 0.85)])
    eyes = [circle(0.82, 0.95, 0.52, 50), circle(-0.82, 0.95, 0.52, 50)]
    irises = [circle(0.82, 0.95, 0.3, 30), circle(-0.82, 0.95, 0.3, 30)]
    parts, pads, toes = [], [], []
    for s in (1, -1):
        parts.append(ellipse(s * 1.3, -0.65, 0.62, 0.42, 50, rot=s * 0.7))
        parts.append(limb([(s * 1.75, -0.3), (s * 1.95, -0.9), (s * 1.5, -1.35)], 0.36, 0.26))
        parts.append(limb([(s * 0.55, -0.45), (s * 0.68, -0.95), (s * 0.62, -1.3)], 0.3, 0.24))
        for (bx, by), angs in [((s * 1.5, -1.38), (200, 250, 290)), ((s * 0.62, -1.33), (225, 270, 315))]:
            for a in angs:
                r = math.radians(a if s > 0 else 180 - a)
                p = (bx + 0.42 * math.cos(r) * (1 if a != 270 else 0.9), by + 0.3 * math.sin(r))
                toes.append(limb([(bx, by), p], 0.1, 0.08))
                pads.append(circle(p[0], p[1], 0.1, 12))
    front = eyes + [head] + parts + toes + pads
    sil = union(*front)
    belly = keep([spl([(-0.55, -0.25), (0.0, -0.45), (0.55, -0.25)], closed=False)], head)
    mouth = [chain(quad((-1.15, 0.05), (-0.6, -0.25), (0.0, -0.22), 12), quad((0.0, -0.22), (0.6, -0.25), (1.15, 0.05), 12))]
    nost = [circle(0.15, 0.45, 0.04, 8), circle(-0.15, 0.45, 0.04, 8)]
    flank = []
    for s in (1, -1):
        flank += keep([[(s * 1.2, -0.2 - 0.2 * k), (s * 0.95, -0.4 - 0.2 * k)] for k in range(2)], head)
    st = hide([stem], *front)
    leaves = leaf((-2.4, -1.4), (-2.9, 0.6), 0.28) + leaf((2.5, -1.45), (3.1, 0.2), 0.28) + leaf((2.0, -1.45), (2.6, -2.6), 0.25)
    leaves = hide(leaves, stem, *front)
    return make("Red-Eyed Tree Frog", sil + irises + belly + mouth + nost + flank + st + leaves,
                [ellipse(0.82, 0.95, 0.07, 0.2, 16), ellipse(-0.82, 0.95, 0.07, 0.2, 16)])


@design("jungle_dart_frog", T)
def dart_frog(rng):
    lf = lens((-3.0, -2.6), (2.9, 2.4), 0.28)
    rib = [[(-3.0, -2.6), (2.6, 2.15)]]
    body = spl([(0.0, 1.6), (0.65, 1.35), (0.85, 0.5), (0.75, -0.6), (0.4, -1.2), (0.0, -1.3), (-0.4, -1.2),
                (-0.75, -0.6), (-0.85, 0.5), (-0.65, 1.35)])
    eyes = [circle(0.55, 1.3, 0.28, 30), circle(-0.55, 1.3, 0.28, 30)]
    legs = []
    for s in (1, -1):
        legs.append(limb([(s * 0.6, 0.6), (s * 1.35, 0.95), (s * 1.55, 1.6)], 0.28, 0.2))
        legs.append(limb([(s * 0.6, -0.7), (s * 1.6, -0.35), (s * 1.55, -1.25), (s * 1.2, -1.75)], 0.38, 0.22))
    toes = []
    for s in (1, -1):
        for a in (60, 95, 130):
            r = math.radians(a if s > 0 else 180 - a)
            p = (s * 1.55 + 0.38 * math.cos(r), 1.6 + 0.38 * math.sin(r))
            toes += [limb([(s * 1.55, 1.6), p], 0.09, 0.08), circle(p[0], p[1], 0.1, 12)]
        for a in (-60, -100, -140):
            r = math.radians(a if s > 0 else 180 - a)
            p = (s * 1.2 + 0.5 * math.cos(r), -1.75 + 0.5 * math.sin(r))
            toes += [limb([(s * 1.2, -1.75), p], 0.09, 0.08), circle(p[0], p[1], 0.1, 12)]
    sil = union(body, *eyes, *legs, *toes)
    blobs = [ellipse(0.0, 0.6, 0.28, 0.18, 24), ellipse(-0.35, 0.0, 0.2, 0.3, 24, rot=0.4), ellipse(0.38, -0.2, 0.22, 0.3, 24, rot=-0.3),
             ellipse(0.0, -0.75, 0.22, 0.17, 24), ellipse(-0.42, 0.75, 0.13, 0.13, 16), ellipse(0.42, 0.55, 0.13, 0.12, 16)]
    blobs += [ellipse(1.05, -0.5, 0.15, 0.1, 14, rot=0.6), ellipse(-1.05, -0.5, 0.15, 0.1, 14, rot=-0.6)]
    blobs = keep(blobs, body, *legs)
    rest = hide([lf] + rib, body, *eyes, *legs, *toes)
    return make("Poison Dart Frog on a Leaf", sil + blobs + rest, [eye(0.6, 1.33, 0.12), eye(-0.6, 1.33, 0.12)])


def _band(cx, cy, rx, ry, w, rot=0.0):
    """A closed ring band (coil) as one even-odd polygon."""
    o = ellipse(cx, cy, rx + w / 2, ry + w / 2, 70, rot=rot)
    i = ellipse(cx, cy, rx - w / 2, ry - w / 2, 70, rot=rot)
    return o, i, o + i[::-1] + [o[0]]


@design("jungle_tree_boa", T)
def tree_boa(rng):
    branch = limb([(-3.3, 0.1), (0.0, 0.25), (3.3, 0.05)], 0.5, 0.42, cap0=False, cap1=False)
    coils = [_band(x, -0.1, 0.62, 0.8, 0.42, rot=0.1 * k) for k, x in enumerate([-1.9, -0.75, 0.4, 1.55])]
    head = spl([(0.6, 1.45), (0.95, 1.6), (1.65, 1.55), (2.0, 1.35), (1.9, 1.15), (1.35, 1.05), (0.7, 1.1)])
    neck = limb([(-0.05, 0.75), (0.25, 1.15), (0.75, 1.3)], 0.4, 0.38)
    tail = limb([(2.15, -0.1), (2.6, -0.6), (2.6, -1.2), (2.3, -1.5)], 0.38, 0.12)
    out, covers = [], [head, neck]
    out += [head] + hide([neck], head)
    for o, i, band in reversed(coils):
        out += hide([o, i], *covers)
        covers.append(band)
    out += hide([tail], *covers)
    covers.append(tail)
    out += hide([branch], *covers)
    vis = []
    xs = [-1.9, -0.75, 0.4, 1.55]
    for idx, x in enumerate(xs):
        zz = []
        for k in range(29):
            t = TAU * k / 28 + 0.3
            if k % 4:
                continue
            rot = 0.1 * idx
            seg = []
            for r in (0.83, 1.17):
                px, py = (0.62 + (r - 1) * 0.6) * math.cos(t), (0.8 + (r - 1) * 0.6) * math.sin(t)
                seg.append((x + px * math.cos(rot) - py * math.sin(rot), -0.1 + px * math.sin(rot) + py * math.cos(rot)))
            zz.append(seg)
        fr = [head, neck, tail] + [c[2] for c in coils[idx + 1:]]
        vis += hide(zz, *fr)
    mouth = [quad((1.95, 1.25), (1.6, 1.22), (1.3, 1.25), 8)]
    nost = [circle(1.85, 1.42, 0.035, 8)]
    leaves = leaf((-3.0, 0.25), (-2.6, 1.3), 0.28) + leaf((2.9, 0.15), (3.2, 1.1), 0.28) + leaf((-2.9, 0.0), (-3.2, -0.9), 0.25)
    leaves = hide(leaves, branch, *[c[2] for c in coils])
    return make("Emerald Tree Boa Coiled on a Branch", out + vis + mouth + nost + leaves, [eye(1.55, 1.38, 0.07)])


@design("jungle_anaconda", T)
def anaconda(rng):
    c = [(x, 0.55 * math.sin(1.1 * x) - 0.2) for x in [-3.0 + 0.05 * i for i in range(111)]]
    w = lambda t: 0.25 + 0.4 * math.sin(math.pi * min(1.0, t * 1.15)) ** 0.6
    body = tube(c, w)
    head = spl([(2.2, -0.05), (2.55, 0.25), (3.05, 0.3), (3.35, 0.15), (3.3, -0.05), (2.95, -0.15), (2.45, -0.3)])
    snake = union(body, head)
    spots = []
    for k, x in enumerate([-2.2, -1.6, -1.0, -0.4, 0.2, 0.8, 1.4, 1.95]):
        y = 0.55 * math.sin(1.1 * x) - 0.2
        spots.append(ellipse(x, y + (0.08 if k % 2 else -0.08), 0.22, 0.13, 20, rot=0.6 * math.cos(1.1 * x)))
    spots = keep(spots, body)
    water = []
    for y, x0, x1 in [(-0.25, -3.3, 3.4), (-0.85, -3.0, 3.2), (-1.5, -3.3, 3.0), (-2.1, -2.5, 2.6)]:
        water.append(ripples(x0, x1, y, 6, 0.06))
    water = hide(water, body, head)
    water = [s for s in water]
    bank = [quad((-3.3, 1.2), (-1.5, 1.35), (0.0, 1.25), 20)]
    reeds = []
    for x in (-2.8, -2.3, -1.6, -0.9, 0.6, 1.4, 2.2, 2.9):
        reeds.append(quad((x, 1.28), (x + 0.1, 2.0), (x + 0.3 * (1 if x > 0 else -1), 2.6), 10))
    reeds += leaf((-1.2, 1.3), (-1.9, 2.6), 0.25) + leaf((1.6, 1.25), (2.5, 2.4), 0.25)
    bank = [quad((-3.3, 1.2), (0.0, 1.4), (3.3, 1.2), 20)]
    nost = [circle(3.2, 0.15, 0.035, 8)]
    mouth = [quad((3.3, -0.03), (2.95, -0.02), (2.65, -0.12), 8)]
    return make("Anaconda in the River", snake + spots + water + bank + reeds + nost + mouth, [eye(2.9, 0.18, 0.07)])


@design("jungle_tapir", T)
def tapir(rng):
    body = spl([(-2.3, 0.2), (-2.15, 0.8), (-1.4, 1.2), (-0.2, 1.15), (0.9, 1.0), (1.6, 0.95), (1.95, 0.6),
                (1.9, -0.1), (1.2, -0.45), (0.0, -0.55), (-1.3, -0.45), (-2.1, -0.25)])
    head = spl([(1.5, 1.05), (2.05, 1.05), (2.55, 0.75), (3.0, 0.35), (3.25, 0.1), (3.2, -0.12), (2.85, -0.05),
                (2.45, 0.1), (2.0, 0.05), (1.6, 0.3)])
    ear = spl([(1.85, 1.0), (1.8, 1.4), (2.0, 1.45), (2.1, 1.05)])
    legs = [limb([(1.4, -0.1), (1.45, -0.8), (1.5, -1.35)], 0.48, 0.38), limb([(-1.6, 0.0), (-1.35, -0.7), (-1.55, -1.35)], 0.55, 0.38)]
    far_legs = [limb([(0.9, -0.2), (0.75, -0.8), (0.85, -1.3)], 0.42, 0.34), limb([(-1.0, -0.1), (-0.85, -0.75), (-0.95, -1.3)], 0.45, 0.34)]
    hooves = [[(1.3, -1.45), (1.33, -1.35)], [(1.5, -1.5), (1.52, -1.38)], [(-1.75, -1.45), (-1.72, -1.35)], [(-1.55, -1.5), (-1.53, -1.38)]]
    front = [head, body] + legs
    sil = union(head, body, *legs)
    far = hide(far_legs, *front)
    ear_l = hide([ear], head) + [arc(1.95, 1.2, 0.07, 0.5, 2.8, 6)]
    saddle = keep([spl([(-0.1, 1.3), (-0.4, 0.6), (-0.1, -0.1), (0.6, -0.7)], closed=False),
                   spl([(-1.5, 1.3), (-1.2, 0.5), (-1.6, -0.2), (-2.0, -0.6)], closed=False)], body)
    thigh = [arc(-1.55, 0.35, 0.55, 3.6, 5.2, 14), arc(1.35, 0.4, 0.45, 4.0, 5.6, 12)]
    nose = [quad((3.2, 0.05), (3.05, 0.0), (3.08, -0.1), 6)]
    mouth = [quad((2.9, -0.06), (2.65, -0.05), (2.5, 0.05), 6)]
    ground = [[(-3.3, -1.45), (3.3, -1.45)]]
    plants = leaf((-3.1, -1.45), (-2.9, 0.4), 0.2) + leaf((-3.1, -1.45), (-2.5, -0.3), 0.2) + leaf((3.1, -1.45), (3.0, -0.4), 0.2) + \
        leaf((-0.3, -1.45), (0.3, -0.9), 0.25)
    plants = hide(plants, *front + far_legs)
    return make("Malayan Tapir", sil + far + hooves + ear_l + saddle + hide(thigh, *legs[:0]) + nose + mouth + ground + plants,
                [eye(2.45, 0.6, 0.07)])


@design("jungle_capybara", T)
def capybara(rng):
    body = spl([(-2.4, -0.3), (-2.3, 0.45), (-1.6, 1.0), (-0.4, 1.15), (0.8, 1.05), (1.4, 1.0), (1.6, 0.4),
                (1.2, -0.45), (-0.4, -0.6), (-1.8, -0.55)])
    head = spl([(1.0, 1.15), (1.6, 1.4), (2.2, 1.35), (2.75, 1.05), (3.1, 0.6), (3.15, 0.15), (2.95, -0.05),
                (2.5, -0.1), (2.0, 0.0), (1.4, 0.2)])
    ear = spl([(1.55, 1.3), (1.45, 1.6), (1.7, 1.68), (1.85, 1.38)])
    bird_b = spl([(-0.9, 1.1), (-0.95, 1.45), (-0.7, 1.75), (-0.4, 1.75), (-0.3, 1.55), (-0.1, 1.5), (-0.35, 1.4),
                  (-0.4, 1.2), (-0.7, 1.1), (-1.3, 1.25), (-1.45, 1.3), (-1.25, 1.12)])
    bird_w = spl([(-0.85, 1.35), (-0.6, 1.4), (-0.95, 1.18)], closed=False)
    bird_legs = [[(-0.7, 1.12), (-0.72, 1.05)], [(-0.55, 1.12), (-0.55, 1.05)]]
    front = [head, body, bird_b]
    sil = hide(union(head, body), bird_b) + [bird_b, bird_w]
    ear_l = hide([ear], head) + [arc(1.68, 1.45, 0.08, 0.4, 2.7, 6)]
    nose = [quad((3.05, 0.5), (2.95, 0.42), (3.0, 0.32), 6), [(3.0, 0.32), (2.95, 0.15)]]
    mouth = [quad((2.95, 0.15), (2.75, 0.1), (2.6, 0.18), 6)]
    cheek = [quad((2.0, 0.95), (1.75, 0.55), (2.05, 0.15), 10)]
    hair = [quad((-1.6 + 0.5 * k, 0.75 - 0.05 * k), (-1.45 + 0.5 * k, 0.55), (-1.3 + 0.5 * k, 0.5), 6) for k in range(5)]
    hair = hide(keep(hair, body), bird_b)
    water = [ripples(-3.3, -2.5, -0.35, 1, 0.05), ripples(1.45, 2.2, -0.35, 1, 0.05), ripples(2.95, 3.4, -0.35, 1, 0.04),
             ripples(-3.0, 3.2, -0.9, 6), ripples(-2.6, 2.8, -1.45, 5), ripples(-1.8, 1.9, -2.0, 4)]
    surf = [chain(arc(-2.35, -0.38, 0.25, math.pi, TAU, 10))]
    lilies = [chain(arc(2.3, -1.55, 0.35, 0.3, TAU - 0.2, 24), [(2.3, -1.55)], [(2.3 + 0.35 * math.cos(0.3), -1.55 + 0.35 * math.sin(0.3))])]
    reeds = [quad((-3.0, -0.35), (-3.05, 0.6), (-3.2, 1.5), 10), quad((-2.7, -0.35), (-2.65, 0.5), (-2.75, 1.2), 10)]
    reeds += leaf((-2.9, -0.35), (-2.2, 1.6), 0.18)
    return make("Capybara with a Bird on Its Back", sil + ear_l + nose + mouth + cheek + bird_legs + hair + water +
                lilies + hide(reeds, body), [eye(2.35, 0.82, 0.07), eye(-0.48, 1.6, 0.04)])


# ================================================================== primates

def _ape_face(cx, cy, s=1.0):
    return spl([(cx, cy + 0.42 * s), (cx + 0.36 * s, cy + 0.3 * s), (cx + 0.42 * s, cy - 0.05 * s), (cx + 0.25 * s, cy - 0.38 * s),
                (cx, cy - 0.45 * s), (cx - 0.25 * s, cy - 0.38 * s), (cx - 0.42 * s, cy - 0.05 * s), (cx - 0.36 * s, cy + 0.3 * s)])


@design("jungle_spider_monkey", T)
def spider_monkey(rng):
    branch = limb([(-3.3, 2.35), (0.0, 2.5), (3.3, 2.3)], 0.36, 0.3, cap0=False, cap1=False)
    body = spl([(0.25, 1.25), (0.62, 1.0), (0.62, 0.0), (0.35, -0.75), (-0.1, -0.8), (-0.35, -0.3), (-0.3, 0.6), (-0.15, 1.15)])
    head = circle(0.85, 1.55, 0.48, 50)
    face = _ape_face(0.95, 1.48, 0.75)
    arm_up = limb([(0.55, 1.15), (1.45, 1.75), (1.6, 2.38)], 0.24, 0.2)
    arm_out = limb([(-0.05, 1.0), (-1.2, 0.85), (-2.3, 1.15)], 0.24, 0.2)
    hand_out = [limb([(-2.3, 1.15), (-2.6, 1.35)], 0.12, 0.1), limb([(-2.3, 1.15), (-2.65, 1.18)], 0.12, 0.1),
                limb([(-2.3, 1.15), (-2.6, 0.98)], 0.12, 0.1)]
    leg1 = limb([(0.2, -0.6), (0.95, -1.35), (1.25, -2.4)], 0.3, 0.2)
    leg2 = limb([(-0.05, -0.6), (-0.7, -1.4), (-0.55, -2.5)], 0.3, 0.2)
    feet = [limb([(1.25, -2.4), (1.55, -2.6)], 0.16, 0.12), limb([(-0.55, -2.5), (-0.3, -2.75)], 0.16, 0.12)]
    tail = limb([(-0.25, -0.6), (-1.3, -0.8), (-1.9, 0.2), (-1.4, 1.6), (-0.8, 2.15)], 0.2, 0.15, cap1=False)
    curl = [arc(-0.7, 2.47, 0.3, math.pi * 1.15, math.pi * 1.15 - TAU * 0.85, 24), arc(-0.7, 2.47, 0.17, math.pi * 1.1, math.pi * 1.1 - TAU * 0.8, 18)]
    front = [head, body, arm_up, arm_out, leg1, leg2, tail] + hand_out + feet
    sil = union(*front)
    fingers = [arc(1.6 + 0.12 * k, 2.52, 0.11, math.pi * 0.1, math.pi * 1.1, 8) for k in (-1, 0, 1)]
    br = hide([branch], arm_up, *[ellipse(-0.7, 2.47, 0.32, 0.32, 30)])
    curl = hide(curl, *[])
    mouth = [quad((0.85, 1.2), (0.97, 1.13), (1.1, 1.2), 6)]
    nost = [circle(0.92, 1.38, 0.03, 8), circle(1.02, 1.38, 0.03, 8)]
    leaves = leaf((2.4, 2.4), (2.9, 1.5), 0.25) + leaf((2.4, 2.4), (2.0, 1.5), 0.25) + leaf((-2.4, 2.45), (-2.9, 3.2), 0.25) + \
        leaf((-2.0, 2.45), (-1.6, 3.3), 0.25)
    leaves = hide(leaves, branch)
    return make("Spider Monkey Swinging by Its Tail", sil + [face] + fingers + br + curl + mouth + nost + leaves,
                [eye(0.82, 1.6, 0.06), eye(1.1, 1.6, 0.06)])


@design("jungle_howler_monkey", T)
def howler_monkey(rng):
    branch = limb([(-3.3, -0.75), (0.0, -0.95), (3.3, -0.8)], 0.42, 0.34, cap0=False, cap1=False)
    body = spl([(-0.95, -0.6), (-1.25, 0.2), (-0.95, 1.05), (-0.2, 1.45), (0.5, 1.25), (0.85, 0.5), (0.7, -0.25), (0.2, -0.65)])
    head = spl([(0.1, 1.5), (0.2, 2.0), (0.6, 2.32), (1.05, 2.35), (1.35, 2.25), (1.62, 2.42), (1.75, 2.28, 0),
                (1.45, 2.0, 0), (1.7, 1.8, 0), (1.55, 1.6), (1.1, 1.2), (0.55, 1.1)])
    mouth_o = [quad((1.45, 2.0), (1.5, 2.08), (1.62, 2.12), 6)]
    beard = fringe(spl([(1.5, 1.55), (1.1, 1.17), (0.55, 1.08)], closed=False), 0.17, 4)
    arm = limb([(0.45, 1.1), (1.05, 0.35), (1.15, -0.6)], 0.38, 0.3)
    leg = limb([(-0.5, -0.35), (0.35, -0.05), (0.45, -0.7)], 0.48, 0.32)
    hand = [arc(1.15 + 0.12 * k, -0.75, 0.11, math.pi * 0.05, math.pi * 1.05, 8) for k in (-1, 0, 1)]
    tail = limb([(-0.9, -0.5), (-1.6, -0.7), (-1.65, -1.6), (-1.15, -2.1)], 0.26, 0.2, cap1=False)
    tail_curl = spiral(-1.15, -2.45, 0.32, 0.1, 0.9, 40, rot=math.pi / 2)
    front = [head, body, arm, leg, tail]
    sil = union(*front)
    br = hide([branch], arm, leg, tail, body)
    br += []
    howl = [arc(1.75, 2.15, r, -0.3, 1.0, 10) for r in (0.45, 0.75, 1.05)]
    brow = [quad((0.9, 2.05), (1.05, 2.15), (1.2, 2.1), 6)]
    nose = [circle(1.45, 2.28, 0.035, 8)]
    ear = [arc(0.45, 1.8, 0.14, 1.2, 4.5, 8)]
    leaves = leaf((-2.6, -0.8), (-3.1, 0.3), 0.28) + leaf((2.6, -0.85), (3.1, 0.2), 0.28) + leaf((2.0, -0.95), (2.4, -2.0), 0.25) + \
        leaf((-2.2, -0.85), (-2.6, -1.9), 0.25)
    leaves = hide(leaves, branch)
    return make("Howler Monkey Calling", sil + mouth_o + [beard, tail_curl] + hand + br + howl + brow + nose + ear + leaves,
                [eye(1.05, 1.9, 0.06)])


@design("jungle_ring_tailed_lemur", T)
def ring_tailed_lemur(rng):
    body = spl([(0.0, 0.75), (0.75, 0.55), (1.0, -0.3), (0.95, -1.3), (0.5, -1.8), (0.0, -1.85), (-0.5, -1.8), (-0.95, -1.3),
                (-1.0, -0.3), (-0.75, 0.55)])
    head = spl([(0.0, 2.1), (0.55, 1.95), (0.85, 1.4), (0.5, 0.9), (0.15, 0.55), (0.0, 0.5), (-0.15, 0.55), (-0.5, 0.9),
                (-0.85, 1.4), (-0.55, 1.95)])
    ears = [spl([(0.45, 1.95), (0.85, 2.45, 0), (0.85, 1.75)]), spl([(-0.45, 1.95), (-0.85, 2.45, 0), (-0.85, 1.75)])]
    arms = [limb([(0.75, 0.3), (0.95, -0.6), (0.45, -1.05)], 0.34, 0.28), limb([(-0.75, 0.3), (-0.95, -0.6), (-0.45, -1.05)], 0.34, 0.28)]
    feet = [ellipse(0.6, -1.95, 0.42, 0.16, 30), ellipse(-0.6, -1.95, 0.42, 0.16, 30)]
    tc = spl([(0.6, -1.7), (1.6, -1.6), (2.2, -0.6), (1.9, 0.7), (1.55, 1.7), (1.85, 2.6), (2.5, 2.9)], closed=False)
    tail = tube(tc, lambda t: 0.42 - 0.08 * t)
    front = [head] + ears + arms + [body] + feet
    sil = union(head, *ears, *arms, body, *feet)
    tl = hide([tail], *front)
    rings = []
    n = len(tc)
    for k in range(1, 12):
        i = int(n * k / 12)
        a, b = tc[max(0, i - 1)], tc[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        nx, ny = -dy / L, dx / L
        w = 0.25
        rings.append([(tc[i][0] + nx * w, tc[i][1] + ny * w), (tc[i][0] - nx * w, tc[i][1] - ny * w)])
    rings = hide(keep(rings, tail), *front)
    masks = [spl([(0.12, 1.55), (0.5, 1.5), (0.55, 1.2), (0.25, 1.05)]), spl([(-0.12, 1.55), (-0.5, 1.5), (-0.55, 1.2), (-0.25, 1.05)])]
    nose = [poly((-0.1, 0.68), (0.1, 0.68), (0.0, 0.55))]
    mouth = [quad((0.0, 0.55), (-0.08, 0.5), (-0.14, 0.53), 4), quad((0.0, 0.55), (0.08, 0.5), (0.14, 0.53), 4)]
    ear_in = [[(0.55, 1.9), (0.78, 2.25)], [(-0.55, 1.9), (-0.78, 2.25)]]
    rock = [quad((-3.0, -2.1), (0.0, -2.2), (3.0, -2.05), 20)]
    belly = keep([quad((-0.4, 0.3), (0.0, -0.7), (0.4, 0.3), 12)], body)
    return make("Ring-Tailed Lemur", sil + tl + rings + masks + nose + mouth + hide(ear_in, *[]) + rock + belly,
                [eye(0.33, 1.32, 0.08), eye(-0.33, 1.32, 0.08)])


@design("jungle_tarsier", T)
def tarsier(rng):
    stem = limb([(-0.35, -3.0), (-0.2, 0.0), (-0.4, 3.0)], 0.55, 0.45, cap0=False, cap1=False)
    head = spl([(0.0, 1.9), (0.95, 1.75), (1.4, 1.0), (1.2, 0.3), (0.6, 0.0), (0.0, -0.05), (-0.6, 0.0), (-1.2, 0.3),
                (-1.4, 1.0), (-0.95, 1.75)])
    ears = [spl([(0.75, 1.65), (1.25, 2.4), (1.6, 2.15), (1.3, 1.4)]), spl([(-0.75, 1.65), (-1.25, 2.4), (-1.6, 2.15), (-1.3, 1.4)])]
    eyes_o = [circle(0.55, 0.95, 0.48, 50), circle(-0.55, 0.95, 0.48, 50)]
    eyes_i = [circle(0.55, 0.95, 0.27, 30), circle(-0.55, 0.95, 0.27, 30)]
    body = spl([(0.0, 0.1), (0.75, -0.2), (0.95, -1.1), (0.75, -1.9), (0.0, -2.1), (-0.75, -1.9), (-0.95, -1.1), (-0.75, -0.2)])
    arms = [limb([(0.6, -0.35), (0.95, -0.6), (0.35, -0.6)], 0.24, 0.2), limb([(-0.6, -0.35), (-0.95, -0.6), (-0.4, -0.65)], 0.24, 0.2)]
    legs = [limb([(0.6, -1.6), (1.2, -1.75), (0.3, -2.25)], 0.4, 0.22), limb([(-0.6, -1.6), (-1.2, -1.75), (-0.45, -2.3)], 0.4, 0.22)]
    fingers, pads = [], []
    for (x, y), d in [((0.35, -0.6), 1), ((-0.4, -0.65), -1), ((0.3, -2.25), 1), ((-0.45, -2.3), -1)]:
        for k, dy in enumerate((0.22, 0.0, -0.22)):
            p = (x - d * 0.5, y + dy)
            fingers.append(limb([(x, y), p], 0.07, 0.06))
            pads.append(circle(p[0], p[1], 0.08, 10))
    tail = limb([(0.2, -2.0), (0.6, -2.5), (0.9, -3.2)], 0.12, 0.08)
    front = [head, *ears, body, *arms, *legs, *fingers, *pads]
    sil = union(head, *ears, body, *arms, *legs, *fingers, *pads)
    st = hide([stem], *front, tail)
    tl = hide([tail], *front)
    nose = [quad((-0.08, 0.35), (0.0, 0.3), (0.08, 0.35), 4)]
    mouth = [quad((-0.25, 0.18), (0.0, 0.12), (0.25, 0.18), 6)]
    ear_in = [[(0.95, 1.75), (1.3, 2.15)], [(-0.95, 1.75), (-1.3, 2.15)]]
    leaves = leaf((-0.3, 2.0), (-1.6, 2.9), 0.25) + leaf((-0.3, -0.5), (-1.9, -0.1), 0.25) + leaf((-0.25, 1.2), (-2.2, 0.9), 0.22)
    leaves = hide(leaves, stem, *front)
    return make("Tarsier with Enormous Eyes", sil + eyes_o + eyes_i + st + tl + nose + mouth + ear_in + leaves,
                [eye(0.55, 0.95, 0.1), eye(-0.55, 0.95, 0.1)])


@design("jungle_slow_loris", T)
def slow_loris(rng):
    vy = lambda x: -0.5 + 0.4545 * x
    vine = limb([(-3.3, vy(-3.3)), (3.3, vy(3.3))], 0.3, 0.26, cap0=False, cap1=False, smooth=False)
    body = ellipse(-0.25, 0.2, 1.3, 0.62, 70, rot=0.42)
    head = circle(1.3, 1.0, 0.62, 60)
    ears = [circle(0.8, 1.48, 0.17, 20), circle(1.82, 1.5, 0.17, 20)]
    patches = [spl([(0.95, 1.3), (1.22, 1.18), (1.12, 0.75), (0.88, 0.85)]), spl([(1.65, 1.3), (1.38, 1.18), (1.48, 0.75), (1.72, 0.85)])]
    stripe = [[(1.3, 1.62), (1.3, 1.08)]]
    legs = [limb([(0.75, 0.35), (1.0, 0.1), (1.05, vy(1.05) + 0.05)], 0.3, 0.24),
            limb([(-1.05, -0.15), (-1.25, -0.6), (-1.3, vy(-1.3) + 0.05)], 0.36, 0.26)]
    far = [limb([(0.4, 0.2), (0.6, -0.05), (0.55, vy(0.55) + 0.05)], 0.28, 0.22),
           limb([(-0.7, -0.2), (-0.8, -0.55), (-0.75, vy(-0.75) + 0.05)], 0.32, 0.24)]
    front = [head, *ears, *legs, body]
    sil = union(head, *ears, *legs, body)
    back = hide(far, *front)
    v = hide([vine], *front, *far)
    grips = []
    for x in (1.05, -1.3):
        grips += [arc(x + 0.1 * k, vy(x + 0.1 * k) + 0.02, 0.09, math.pi + 0.3, TAU + 0.6, 6) for k in (-1, 0, 1)]
    nose = [quad((1.2, 0.75), (1.3, 0.68), (1.4, 0.75), 6)]
    mouth = [quad((1.15, 0.56), (1.3, 0.5), (1.45, 0.56), 6)]
    ear_in = hide([circle(0.8, 1.48, 0.08, 10), circle(1.82, 1.5, 0.08, 10)], head)
    fur = keep([spl([(-1.3, 0.55), (-0.5, 0.75), (0.4, 0.95)], closed=False)], body)
    leaves = leaf((2.5, vy(2.5)), (2.9, 2.0), 0.28) + leaf((2.5, vy(2.5)), (3.3, 0.0), 0.28) + leaf((-2.4, vy(-2.4)), (-3.0, -0.4), 0.28) + \
        leaf((-2.4, vy(-2.4)), (-2.0, -2.8), 0.28)
    leaves = hide(leaves, vine)
    return make("Slow Loris on a Vine", sil + back + v + patches + stripe + grips + nose + mouth + ear_in + fur + leaves,
                [eye(1.07, 1.03, 0.1), eye(1.53, 1.03, 0.1)])


@design("jungle_gibbon", T)
def gibbon(rng):
    vine1 = [quad((-1.6, 3.2), (-1.7, 2.0), (-1.5, 1.2), 14)]
    branch = limb([(0.6, 2.6), (2.0, 2.0), (3.3, 2.3)], 0.32, 0.26, cap0=True, cap1=False)
    head = circle(0.15, 0.55, 0.52, 50)
    face = _ape_face(0.2, 0.48, 0.85)
    ring = _ape_face(0.2, 0.48, 1.05)
    body = spl([(-0.25, 0.25), (0.3, 0.05), (0.45, -0.7), (0.15, -1.45), (-0.35, -1.55), (-0.65, -1.0), (-0.6, -0.2)])
    arm1 = limb([(-0.35, 0.15), (-1.0, 0.8), (-1.5, 1.35)], 0.26, 0.22)
    arm2 = limb([(0.25, 0.0), (1.2, 0.9), (2.0, 1.95)], 0.26, 0.22)
    leg1 = limb([(-0.3, -1.3), (0.5, -1.5), (0.35, -2.1)], 0.34, 0.24)
    leg2 = limb([(-0.5, -1.35), (-1.2, -1.7), (-0.8, -2.3)], 0.32, 0.24)
    hands = [arc(-1.5, 1.45, 0.14, -0.4, 3.4, 10), arc(2.05, 2.05, 0.13, -0.5, 3.3, 10)]
    feet = [limb([(0.35, -2.1), (0.7, -2.25)], 0.16, 0.12), limb([(-0.8, -2.3), (-0.5, -2.5)], 0.16, 0.12)]
    front = [head, body, arm1, arm2, leg1, leg2] + feet
    sil = union(*front)
    sil = hide(sil, *[])
    br = hide([branch], arm2, ellipse(2.05, 2.05, 0.15, 0.15, 20))
    v = hide(vine1, arm1, ellipse(-1.5, 1.45, 0.16, 0.16, 20))
    v += [quad((-1.5, 1.2), (-1.3, 0.3), (-1.6, -0.6), 12)]
    v = hide(v, arm1, body, *front)
    mouth = [quad((0.08, 0.15), (0.2, 0.1), (0.32, 0.15), 6)]
    nost = [circle(0.15, 0.38, 0.03, 8), circle(0.25, 0.38, 0.03, 8)]
    leaves = leaf((2.9, 2.25), (3.3, 1.2), 0.28) + leaf((2.6, 2.15), (2.4, 3.2), 0.28) + leaf((-1.6, 2.6), (-2.6, 2.9), 0.25) + \
        leaf((-1.55, 1.8), (-0.9, 2.5), 0.25) + leaf((-1.62, 0.0), (-2.4, -0.4), 0.25)
    leaves = hide(leaves, branch, *front)
    return make("Gibbon Swinging through the Trees", sil + [face, ring] + hands + br + v + mouth + nost + leaves,
                [eye(0.08, 0.6, 0.06), eye(0.32, 0.6, 0.06)])


@design("jungle_proboscis_monkey", T)
def proboscis_monkey(rng):
    branch = limb([(-3.3, -1.0), (0.0, -1.15), (3.3, -0.95)], 0.45, 0.38, cap0=False, cap1=False)
    head = spl([(0.0, 2.45), (0.55, 2.3), (0.72, 1.85), (0.6, 1.35), (0.25, 1.05), (0.0, 1.0), (-0.25, 1.05), (-0.6, 1.35),
                (-0.72, 1.85), (-0.55, 2.3)])
    cap = [quad((-0.62, 2.0), (0.0, 2.35), (0.62, 2.0), 14)]
    nose = spl([(0.0, 1.85), (0.2, 1.6), (0.35, 1.15), (0.2, 0.85), (0.0, 0.8), (-0.2, 0.85), (-0.35, 1.15), (-0.2, 1.6)])
    body = spl([(0.0, 1.05), (0.85, 0.85), (1.25, 0.0), (1.2, -0.75), (0.7, -1.1), (0.0, -1.15), (-0.7, -1.1),
                (-1.2, -0.75), (-1.25, 0.0), (-0.85, 0.85)])
    belly = ellipse(0.0, -0.35, 0.75, 0.68, 50)
    arms = [limb([(0.95, 0.6), (1.45, -0.2), (0.95, -0.75)], 0.38, 0.3), limb([(-0.95, 0.6), (-1.45, -0.2), (-0.95, -0.75)], 0.38, 0.3)]
    legs = [limb([(0.6, -1.0), (1.0, -1.5), (0.9, -2.3)], 0.42, 0.32), limb([(-0.6, -1.0), (-1.0, -1.5), (-0.9, -2.3)], 0.42, 0.32)]
    feet = [ellipse(1.05, -2.4, 0.3, 0.14, 24), ellipse(-1.05, -2.4, 0.3, 0.14, 24)]
    tail = limb([(0.3, -1.1), (0.35, -2.0), (0.25, -3.0)], 0.2, 0.16)
    front = [nose, head, *arms, body, *legs, *feet]
    sil = union(head, *arms, body, *legs, *feet)
    nose_l = [nose]
    sil = hide(sil, nose)
    bl = hide(keep([belly], body), *arms)
    br = hide([branch], *legs, body)
    tl = hide([tail], branch, *front)
    mouth = [quad((-0.18, 0.92), (0.0, 0.88), (0.18, 0.92), 6)]
    leaves = leaf((-2.5, -1.0), (-3.0, 0.2), 0.28) + leaf((-2.0, -1.1), (-1.6, 0.0), 0.28) + leaf((2.5, -1.0), (3.0, 0.2), 0.28) + \
        leaf((2.2, -1.05), (2.6, -2.1), 0.25)
    leaves = hide(leaves, branch, *front)
    return make("Proboscis Monkey", sil + cap + nose_l + bl + br + tl + mouth + leaves,
                [eye(-0.25, 1.9, 0.07), eye(0.25, 1.9, 0.07)])


@design("jungle_mandrill", T)
def mandrill(rng):
    R = [(0.0, 2.9), (0.95, 2.75), (1.75, 2.2), (2.15, 1.3), (2.1, 0.2), (1.75, -0.8), (1.25, -1.6), (0.6, -2.3), (0.0, -2.55)]
    head = spl(R + [(-x, y) for x, y in R[-2:0:-1]])
    mane = fringe(spl([(0.0, 3.05), (1.05, 2.9), (1.95, 2.3), (2.35, 1.3), (2.3, 0.1), (1.95, -0.9)], closed=False), -0.14, 13)
    mane2 = mirror_x(mane)
    brow = [chain(quad((-1.15, 1.25), (-0.6, 1.75), (-0.12, 1.3), 12), quad((0.12, 1.3), (0.6, 1.75), (1.15, 1.25), 12))]
    eyes = [ellipse(0.55, 1.15, 0.24, 0.13, 20), ellipse(-0.55, 1.15, 0.24, 0.13, 20)]
    ridge = spl([(-0.15, 1.2), (-0.2, 0.0), (-0.3, -1.05), (0.0, -1.3), (0.3, -1.05), (0.2, 0.0), (0.15, 1.2)], closed=False)
    nose = [ellipse(0.0, -1.18, 0.38, 0.22, 24)]
    nost = [ellipse(0.15, -1.22, 0.07, 0.05, 10), ellipse(-0.15, -1.22, 0.07, 0.05, 10)]
    cheeks = []
    for s in (1, -1):
        cheeks.append(spl([(s * 0.35, 0.9), (s * 1.05, 0.75), (s * 1.3, -0.1), (s * 0.95, -0.9), (s * 0.45, -0.95), (s * 0.35, 0.0)]))
        for k in range(3):
            cheeks.append(spl([(s * (0.55 + 0.17 * k), 0.68 - 0.03 * k), (s * (0.65 + 0.2 * k), -0.1), (s * (0.55 + 0.12 * k), -0.78)], closed=False))
    mouth = [quad((-0.5, -1.65), (0.0, -1.9), (0.5, -1.65), 10)]
    beard = [chain(quad((-0.65, -1.95), (-0.25, -2.55), (0.0, -3.1), 10), quad((0.0, -3.1), (0.25, -2.55), (0.65, -1.95), 10))]
    ears = [arc(2.1, 1.0, 0.3, -1.4, 1.4, 10), arc(-2.1, 1.0, 0.3, math.pi - 1.4, math.pi + 1.4, 10)]
    return make("Mandrill Face", [head, mane, mane2] + brow + eyes + [ridge] + nose + nost + cheeks + mouth + beard +
                hide(ears, head), [eye(0.55, 1.15, 0.08), eye(-0.55, 1.15, 0.08)])


@design("jungle_golden_lion_tamarin", T)
def golden_lion_tamarin(rng):
    branch = limb([(-3.3, -0.55), (0.0, -0.35), (3.3, -0.6)], 0.42, 0.36, cap0=False, cap1=False)
    mane = polar(lambda t: 1.0 + 0.13 * math.cos(11 * t), cx=1.3, cy=1.0, n=240)
    face = spl([(1.55, 1.3), (1.85, 1.15), (1.95, 0.75), (1.75, 0.4), (1.45, 0.45), (1.3, 0.8)])
    body = spl([(-1.6, 0.2), (-1.2, 0.85), (-0.2, 1.05), (0.6, 0.95), (0.9, 0.5), (0.5, -0.05), (-0.6, -0.05), (-1.4, -0.15)])
    legs = [limb([(0.55, 0.2), (0.8, -0.1), (0.75, -0.35)], 0.3, 0.24), limb([(-1.1, 0.1), (-0.85, -0.2), (-1.0, -0.35)], 0.36, 0.26)]
    back_legs = [limb([(0.25, 0.2), (0.3, -0.1), (0.15, -0.35)], 0.26, 0.22), limb([(-0.7, 0.1), (-0.5, -0.2), (-0.55, -0.35)], 0.3, 0.24)]
    tail = limb([(-1.5, 0.3), (-2.1, -0.1), (-2.3, -1.2), (-2.0, -2.4), (-2.2, -3.0)], 0.28, 0.24)
    front = [mane, body, *legs]
    sil = union(mane, body, *legs)
    back = hide(back_legs, *front)
    tl = hide([tail], *front, branch)
    br = hide([branch], *front, *back_legs)
    grips = [arc(0.78 + 0.1 * k, -0.4, 0.09, 0.2, 3.0, 6) for k in (-1, 0, 1)]
    mouth = [quad((1.6, 0.58), (1.7, 0.53), (1.8, 0.58), 6)]
    nose = [circle(1.75, 0.82, 0.03, 8), circle(1.85, 0.82, 0.03, 8)]
    leaves = leaf((2.6, -0.55), (3.2, 0.5), 0.28) + leaf((2.3, -0.5), (2.6, -1.6), 0.28) + leaf((-2.9, -0.55), (-3.2, 0.6), 0.28)
    leaves = hide(leaves, branch, tail)
    return make("Golden Lion Tamarin", sil + [face] + back + tl + br + grips + mouth + nose + leaves,
                [eye(1.55, 0.95, 0.06), eye(1.8, 0.95, 0.06)])


@design("jungle_aye_aye", T)
def aye_aye(rng):
    branch = limb([(-3.3, -1.3), (0.0, -1.1), (3.3, -1.4)], 0.42, 0.36, cap0=False, cap1=False)
    body = spl([(-1.3, -0.95), (-1.6, -0.2), (-1.0, 0.6), (0.0, 0.85), (0.8, 0.6), (1.05, 0.0), (0.7, -0.7), (-0.3, -0.95)])
    head = spl([(0.6, 0.85), (1.1, 1.25), (1.75, 1.15), (2.15, 0.7), (2.35, 0.35), (2.1, 0.15), (1.6, 0.1), (1.0, 0.3)])
    ear = spl([(1.0, 1.15), (0.35, 1.75), (0.45, 2.45), (1.1, 2.6), (1.55, 2.1), (1.45, 1.3)])
    ear_in = spl([(1.05, 1.4), (0.6, 1.85), (0.7, 2.3), (1.1, 2.38), (1.35, 2.0), (1.3, 1.5)], closed=False)
    ear2 = spl([(1.5, 1.2), (1.85, 1.7), (2.25, 1.9), (2.4, 1.5), (2.1, 1.0)])
    arm = limb([(0.6, 0.0), (1.2, -0.45), (1.55, -0.95)], 0.3, 0.22)
    finger = limb([(1.55, -0.95), (2.1, -0.85), (2.55, -0.95), (2.75, -1.0)], 0.07, 0.05)
    leg = limb([(-0.8, -0.4), (-0.3, -0.8), (-0.6, -1.0)], 0.42, 0.3)
    tail = spl([(-1.4, -0.3), (-2.2, 0.4), (-3.0, 1.3), (-2.8, 1.8), (-2.2, 1.6), (-1.6, 0.6), (-1.15, -0.05)])
    tail_f = fringe(spl([(-1.45, -0.1), (-2.3, 0.65), (-2.9, 1.5)], closed=False), -0.15, 7)
    front = [head, ear, arm, finger, leg, body, tail]
    sil = union(head, ear, arm, finger, leg, body, tail)
    br = hide([branch], *front)
    fur = hide([ear2], *front)
    nose = [circle(2.25, 0.3, 0.04, 8)]
    mouth = [quad((2.2, 0.17), (2.0, 0.12), (1.85, 0.2), 6)]
    eye_ring = [circle(1.7, 0.7, 0.22, 24)]
    leaves = leaf((2.8, -1.35), (3.2, -0.3), 0.28) + leaf((-2.6, -1.25), (-3.1, -2.3), 0.28) + leaf((2.3, -1.3), (2.6, -2.4), 0.28)
    leaves = hide(leaves, branch)
    return make("Aye-Aye Tapping for Grubs", sil + [ear_in] + br + fur + nose + mouth + eye_ring + leaves,
                [eye(1.7, 0.7, 0.1)])


# ================================================================== other mammals

@design("jungle_kinkajou", T)
def kinkajou(rng):
    branch = limb([(-3.3, -0.85), (0.0, -1.0), (3.3, -0.8)], 0.42, 0.36, cap0=False, cap1=False)
    body = spl([(0.0, 0.9), (0.85, 0.65), (1.1, -0.2), (0.85, -0.95), (0.0, -1.05), (-0.85, -0.95), (-1.1, -0.2), (-0.85, 0.65)])
    head = ellipse(0.0, 1.55, 0.78, 0.65, 60)
    ears = [circle(0.7, 1.95, 0.2, 20), circle(-0.7, 1.95, 0.2, 20)]
    muzzle = ellipse(0.0, 1.22, 0.3, 0.22, 24)
    fruit = ellipse(0.0, 0.55, 0.38, 0.32, 30)
    arms = [limb([(0.8, 0.5), (0.85, 0.15), (0.35, 0.45)], 0.32, 0.26), limb([(-0.8, 0.5), (-0.85, 0.15), (-0.35, 0.45)], 0.32, 0.26)]
    feet = [limb([(0.6, -0.75), (0.75, -1.05)], 0.34, 0.3), limb([(-0.6, -0.75), (-0.75, -1.05)], 0.34, 0.3)]
    tail = limb([(-0.8, -0.85), (-1.6, -1.25), (-1.6, -2.1), (-1.0, -2.55), (-0.6, -2.2)], 0.36, 0.2)
    front = [fruit, *arms, head, *ears, body, *feet]
    sil = hide(union(head, *ears, body, *feet), fruit, *arms) + hide(arms, fruit)
    stem = [quad((0.0, 0.85), (0.05, 1.0), (0.15, 1.05), 6)]
    stem = hide(stem, muzzle)
    br = hide([branch], body, *feet, tail)
    tl = hide([tail], body, *feet)
    ear_in = [circle(0.7, 1.95, 0.1, 12), circle(-0.7, 1.95, 0.1, 12)]
    ear_in = hide(ear_in, head)
    nose = [ellipse(0.0, 1.3, 0.1, 0.07, 12)]
    mouth = [quad((-0.15, 1.12), (0.0, 1.06), (0.15, 1.12), 6)]
    leaves = leaf((2.4, -0.85), (2.9, 0.3), 0.28) + leaf((2.0, -0.9), (2.3, -2.0), 0.28) + leaf((-2.6, -0.85), (-3.1, 0.3), 0.28)
    leaves = hide(leaves, branch)
    return make("Kinkajou Eating Fruit", sil + [fruit, muzzle] + stem + br + tl + ear_in + nose + mouth + leaves,
                [eye(-0.32, 1.65, 0.1), eye(0.32, 1.65, 0.1)])


@design("jungle_coati", T)
def coati(rng):
    body = spl([(-1.9, 0.1), (-1.7, 0.75), (-0.6, 1.05), (0.6, 1.0), (1.35, 0.85), (1.65, 0.35), (1.35, -0.15), (0.2, -0.3),
                (-1.2, -0.25)])
    head = spl([(1.25, 1.0), (1.7, 1.2), (2.1, 1.05), (2.6, 0.62), (3.1, 0.3), (3.22, 0.18), (3.05, 0.08), (2.4, 0.2),
                (1.85, 0.2), (1.45, 0.4)])
    ear = spl([(1.65, 1.15), (1.6, 1.42), (1.82, 1.45), (1.9, 1.18)])
    legs = [limb([(1.2, 0.2), (1.3, -0.5), (1.25, -1.1)], 0.42, 0.3), limb([(-1.3, 0.2), (-1.0, -0.45), (-1.25, -1.1)], 0.5, 0.3)]
    far = [limb([(0.75, 0.0), (0.7, -0.5), (0.85, -1.05)], 0.36, 0.28), limb([(-0.7, 0.0), (-0.5, -0.5), (-0.65, -1.05)], 0.4, 0.28)]
    feet = [ellipse(1.4, -1.15, 0.25, 0.1, 20), ellipse(-1.1, -1.15, 0.25, 0.1, 20)]
    ffeet = [ellipse(1.0, -1.1, 0.23, 0.1, 20), ellipse(-0.5, -1.1, 0.23, 0.1, 20)]
    tc = spl([(-1.7, 0.5), (-2.3, 0.9), (-2.5, 1.8), (-2.2, 2.6), (-1.85, 3.0)], closed=False)
    tail = tube(tc, lambda t: 0.4 - 0.22 * t)
    front = [head, body, *legs, *feet]
    sil = union(head, body, *legs, *feet)
    back = hide(far + ffeet, *front)
    tl = hide([tail], *front)
    rings = []
    n = len(tc)
    for k in range(1, 9):
        i = int(n * k / 9)
        a, b = tc[i - 1], tc[i + 1]
        L = math.dist(a, b)
        nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
        rings.append([(tc[i][0] + nx * 0.3, tc[i][1] + ny * 0.3), (tc[i][0] - nx * 0.3, tc[i][1] - ny * 0.3)])
    rings = hide(keep(rings, tail), *front)
    ear_l = hide([ear], head)
    mask = [quad((2.0, 0.95), (2.25, 0.75), (2.55, 0.62), 8)]
    nose = [ellipse(3.15, 0.17, 0.06, 0.08, 10)]
    claws = [[(1.55 + 0.08 * k, -1.2), (1.62 + 0.08 * k, -1.28)] for k in range(2)]
    ground = [[(-3.2, -1.25), (3.3, -1.25)]]
    plants = tuft(2.6, -1.25, 0.7) + tuft(-2.8, -1.25, 0.7) + leaf((0.2, -1.25), (-0.3, -0.7), 0.25)
    plants = hide(plants, *front, *far)
    return make("Coati with Its Tail Held High", sil + back + tl + rings + ear_l + mask + nose + claws + ground + plants,
                [eye(2.15, 0.82, 0.06)])


@design("jungle_giant_anteater", T)
def giant_anteater(rng):
    body = spl([(-1.6, 0.9), (-0.6, 1.35), (0.5, 1.3), (1.2, 1.05), (1.5, 0.5), (1.25, -0.15), (0.3, -0.35),
                (-0.9, -0.3), (-1.65, 0.1)])
    head = spl([(1.1, 1.15), (1.6, 1.1), (2.4, 0.65), (3.25, 0.2), (3.3, 0.08), (2.5, 0.12), (1.75, 0.3), (1.25, 0.5)])
    ear = spl([(1.5, 1.1), (1.5, 1.3), (1.68, 1.28), (1.7, 1.05)])
    legs = [limb([(1.0, 0.2), (1.15, -0.5), (1.05, -1.15)], 0.55, 0.42), limb([(-1.15, 0.2), (-0.95, -0.5), (-1.2, -1.15)], 0.6, 0.42)]
    far = [limb([(0.55, 0.1), (0.5, -0.5), (0.6, -1.1)], 0.5, 0.38), limb([(-0.6, 0.1), (-0.4, -0.5), (-0.55, -1.1)], 0.5, 0.38)]
    tail = spl([(-1.5, 1.0), (-2.4, 1.25), (-3.15, 1.0), (-3.3, 0.4), (-3.1, -0.4, 0), (-2.95, -0.2), (-2.75, -0.75, 0),
                (-2.55, -0.45), (-2.3, -0.8, 0), (-2.15, -0.35), (-1.7, 0.2)])
    hair = [quad((-1.9, 0.85), (-2.7, 0.8), (-2.95, -0.1), 12), quad((-1.9, 0.45), (-2.4, 0.3), (-2.5, -0.35), 10)]
    front = [head, body, *legs]
    sil = union(head, body, *legs)
    tl = hide([tail], *front)
    back = hide(far, *front, tail)
    stripe = keep([spl([(0.4, -0.3), (0.8, 0.4), (1.3, 0.9), (1.7, 1.15)], closed=False),
                   spl([(0.0, -0.3), (0.5, 0.45), (1.0, 0.95), (1.45, 1.25)], closed=False)], body, head)
    stripe = hide(stripe, legs[0])
    ear_l = hide([ear], head)
    claws = [quad((0.9 + 0.12 * k, -1.2), (0.85 + 0.12 * k, -1.35), (0.75 + 0.12 * k, -1.32), 4) for k in range(3)]
    ground = [[(-3.3, -1.3), (3.3, -1.3)]]
    mound = [quad((2.0, -1.3), (2.6, -0.5), (3.2, -1.3), 14)]
    ants = [ellipse(2.6 + 0.2 * k, -1.0 - 0.08 * (k % 2), 0.05, 0.03, 8) for k in range(-1, 2)]
    return make("Giant Anteater", sil + tl + hide(hair, *front) + back + stripe + ear_l + claws + ground + mound,
                [eye(1.8, 0.75, 0.05)])


@design("jungle_ocelot", T)
def ocelot(rng):
    log = limb([(-3.3, -2.1), (2.9, -2.1)], 0.95, 0.95, cap0=False, cap1=False, smooth=False)
    log_end = ellipse(2.9, -2.1, 0.24, 0.475, 40)
    rings = [ellipse(2.9, -2.1, 0.13, 0.28, 30), ellipse(2.9, -2.1, 0.05, 0.1, 12)]
    haunch = ellipse(-0.55, -0.9, 0.8, 0.72, 60)
    body = spl([(-1.2, -1.55), (-1.35, -0.6), (-0.95, 0.35), (-0.3, 1.1), (0.3, 1.35), (0.8, 0.9), (0.9, 0.0), (0.8, -1.55)])
    head = spl([(-0.05, 1.85), (0.1, 2.3), (0.55, 2.48), (1.0, 2.35), (1.3, 2.02), (1.5, 1.68), (1.42, 1.42), (1.05, 1.25),
                (0.5, 1.2), (0.05, 1.45)])
    ears = [spl([(0.12, 2.25), (0.12, 2.75), (0.5, 2.46)]), spl([(0.68, 2.44), (0.88, 2.82), (1.06, 2.34)])]
    fl = limb([(0.55, 0.4), (0.65, -0.6), (0.65, -1.45)], 0.42, 0.32)
    fpaw = ellipse(0.82, -1.56, 0.27, 0.12, 24)
    ff = limb([(0.25, 0.3), (0.3, -0.6), (0.3, -1.45)], 0.38, 0.3)
    ffpaw = ellipse(0.45, -1.57, 0.25, 0.11, 24)
    hfoot = ellipse(-0.2, -1.55, 0.5, 0.13, 30)
    tail = limb([(-1.2, -1.35), (-1.85, -1.5), (-2.15, -2.05), (-1.95, -2.75)], 0.28, 0.22)
    front = [tail, head, *ears, fl, fpaw, hfoot, haunch, body]
    sil = union(head, *ears, fl, fpaw, hfoot, haunch, body)
    tl = hide([tail], *front[1:])
    back = hide([ff, ffpaw], *front)
    lg = hide([log, log_end] + rings, *front, ff, ffpaw)
    bark = hide([[(-2.8, -1.85), (-1.6, -1.85)], [(-2.4, -2.35), (-0.4, -2.35)], [(1.2, -1.9), (2.4, -1.9)], [(0.6, -2.38), (2.3, -2.38)]],
                *front, ff, ffpaw)
    chains = []
    for x, y, r in [(-0.9, -0.3, 0.6), (-0.45, 0.35, 0.9), (0.15, 0.8, 1.1), (-0.95, -0.95, 0.3), (-0.4, -0.9, 0.2), (-0.65, -1.35, 0.1),
                    (0.3, 0.2, 1.4), (0.35, -0.4, 1.5), (-0.2, -0.3, 1.0), (0.1, -1.0, 1.5)]:
        chains.append(ellipse(x, y, 0.2, 0.09, 16, rot=r))
    chains = keep(chains, body, haunch)
    chains = hide(chains, fl)
    spots = keep([circle(0.62 + 0.05 * k, -0.4 - 0.3 * k, 0.05, 8) for k in range(3)], fl)
    trings = keep([[(-1.6, -1.25), (-1.65, -1.65)], [(-2.0, -1.65), (-2.25, -1.75)], [(-1.85, -2.25), (-2.2, -2.15)]], tail)
    face = [poly((1.38, 1.6), (1.48, 1.52), (1.36, 1.48)), quad((1.36, 1.48), (1.25, 1.36), (1.1, 1.42), 6),
            quad((0.45, 1.95), (0.65, 1.8), (0.8, 1.6), 8), quad((0.35, 1.72), (0.5, 1.58), (0.68, 1.48), 8),
            [(1.42, 1.48), (1.75, 1.6)], [(1.4, 1.44), (1.75, 1.42)]]
    ear_in = [[(0.2, 2.35), (0.2, 2.6)], [(0.82, 2.45), (0.88, 2.65)]]
    return make("Ocelot Sitting on a Log", sil + tl + back + lg + bark + chains + spots + trings + face + ear_in,
                [eye(1.08, 1.95, 0.07)])


@design("jungle_binturong", T)
def binturong(rng):
    branch = limb([(-3.3, -0.85), (0.0, -0.7), (3.3, -0.85)], 0.42, 0.36, cap0=False, cap1=False)
    body = spl([(-1.75, -0.35), (-1.85, 0.35), (-1.25, 0.85), (0.0, 1.0), (1.0, 0.85), (1.5, 0.45), (1.35, -0.25),
                (0.3, -0.45), (-1.0, -0.45)])
    head = spl([(1.15, 0.8), (1.6, 1.1), (2.1, 1.05), (2.55, 0.75), (2.9, 0.5), (2.98, 0.32), (2.72, 0.2), (2.2, 0.15),
                (1.7, 0.2), (1.35, 0.35)])
    ear = spl([(1.6, 1.05), (1.58, 1.4), (1.72, 1.62, 0), (1.88, 1.38), (1.92, 1.05)])
    tufts = [quad((1.72, 1.62), (1.65, 1.85), (1.55, 1.95), 6), quad((1.72, 1.62), (1.78, 1.88), (1.85, 1.98), 6)]
    legs = [limb([(1.1, 0.0), (1.25, -0.35), (1.2, -0.55)], 0.45, 0.36), limb([(-1.3, -0.1), (-1.1, -0.4), (-1.25, -0.55)], 0.5, 0.38)]
    far = [limb([(0.6, -0.1), (0.7, -0.35), (0.6, -0.55)], 0.4, 0.34), limb([(-0.7, -0.15), (-0.55, -0.4), (-0.7, -0.55)], 0.42, 0.34)]
    tail = limb([(-1.7, 0.1), (-2.45, -0.3), (-2.6, -1.25), (-2.1, -1.7), (-1.55, -1.45), (-1.45, -1.05)], 0.6, 0.3)
    front = [head, ear, *legs, body, tail]
    sil = union(head, ear, *legs, body, tail)
    back = hide(far, *front)
    br = hide([branch], *front, *far)
    fur = [quad((-1.3 + 0.55 * k, 0.75 + 0.05 * (k % 2)), (-1.2 + 0.55 * k, 0.45), (-1.0 + 0.55 * k, 0.35), 6) for k in range(5)]
    fur = keep(fur, body)
    whisk = [quad((2.75, 0.32), (3.1, 0.45), (3.4, 0.62), 8), quad((2.75, 0.28), (3.1, 0.3), (3.45, 0.32), 8),
             quad((2.75, 0.24), (3.05, 0.12), (3.35, 0.0), 8)]
    nose = [ellipse(2.93, 0.36, 0.06, 0.05, 10)]
    claws = [arc(1.2 + 0.11 * k, -0.6, 0.08, math.pi + 0.3, TAU, 5) for k in (-1, 0, 1)]
    leaves = leaf((2.6, -0.8), (3.1, 0.3), 0.28) + leaf((0.2, -0.75), (0.6, -1.8), 0.28) + leaf((-3.0, -0.85), (-3.3, 0.2), 0.28)
    leaves = hide(leaves, branch, *front)
    return make("Binturong on a Branch", sil + back + br + tufts + fur + whisk + nose + claws + leaves, [eye(2.15, 0.72, 0.07)])


@design("jungle_tree_kangaroo", T)
def tree_kangaroo(rng):
    branch = limb([(-3.3, -0.95), (0.0, -1.05), (3.3, -0.9)], 0.45, 0.38, cap0=False, cap1=False)
    body = spl([(-1.0, -0.75), (-1.25, 0.0), (-0.85, 0.8), (0.0, 1.15), (0.7, 1.0), (1.0, 0.5), (0.9, -0.2), (0.5, -0.75)])
    head = spl([(0.6, 1.3), (0.85, 1.65), (1.3, 1.72), (1.65, 1.5), (1.85, 1.2), (1.8, 1.0), (1.5, 0.88), (1.0, 0.85), (0.7, 1.0)])
    ears = [circle(0.88, 1.75, 0.2, 20), circle(1.28, 1.82, 0.19, 20)]
    arm = limb([(0.65, 0.55), (1.15, 0.05), (1.05, -0.72)], 0.32, 0.26)
    thigh = ellipse(-0.45, -0.3, 0.62, 0.55, 40)
    foot = ellipse(-0.1, -0.78, 0.7, 0.15, 30)
    tail = limb([(-1.0, -0.55), (-1.35, -1.5), (-1.25, -3.0)], 0.36, 0.26)
    front = [arm, head, *ears, body, thigh, foot]
    sil = hide(union(head, *ears, body, thigh, foot), arm) + [arm]
    br = hide([branch], *front)
    tl = hide([tail], branch, *front)
    thigh_l = hide(keep([arc(-0.45, -0.3, 0.62, 0.3, 2.6, 14)], body), arm)
    ear_in = hide([circle(0.88, 1.75, 0.1, 12), circle(1.28, 1.82, 0.1, 12)], head)
    nose = [ellipse(1.8, 1.12, 0.07, 0.06, 10)]
    mouth = [quad((1.75, 0.95), (1.6, 0.9), (1.45, 0.95), 6)]
    claws = [arc(1.05 + 0.1 * k, -0.85, 0.08, math.pi * 0.1, math.pi * 1.1, 5) for k in (-1, 0, 1)]
    toes = [[(0.5 + 0.0, -0.75 - 0.05 * k), (0.62, -0.8 - 0.05 * k)] for k in range(2)]
    leaves = leaf((-2.5, -0.95), (-3.0, 0.2), 0.28) + leaf((-2.1, -1.0), (-1.7, 0.1), 0.28) + leaf((2.5, -0.92), (3.0, 0.2), 0.28) + \
        leaf((2.1, -0.95), (2.4, -2.1), 0.28)
    leaves = hide(leaves, branch)
    return make("Tree Kangaroo", sil + br + tl + thigh_l + ear_in + nose + mouth + claws + leaves, [eye(1.35, 1.3, 0.07)])


@design("jungle_bongo", T)
def bongo(rng):
    body = spl([(-1.85, 0.35), (-1.65, 1.0), (-0.4, 1.12), (0.9, 1.18), (1.5, 1.05), (1.75, 0.6), (1.5, 0.1), (0.4, -0.05),
                (-0.9, 0.0), (-1.75, 0.05)])
    neck = limb([(1.2, 0.75), (1.85, 1.45), (2.15, 1.9)], 0.75, 0.48)
    head = spl([(1.95, 2.15), (2.28, 2.28), (2.58, 1.98), (2.95, 1.58), (3.05, 1.38), (2.9, 1.27), (2.5, 1.45), (2.1, 1.75)])
    ear = lens((2.05, 2.15), (1.5, 2.45), 0.32)
    horns = [limb([(2.18, 2.25), (1.95, 2.85), (1.55, 3.3), (1.25, 3.65)], 0.17, 0.07), limb([(2.35, 2.2), (2.25, 2.85), (1.95, 3.3), (1.7, 3.7)], 0.17, 0.07)]
    legs = [limb([(1.3, 0.3), (1.38, -0.5), (1.3, -1.35)], 0.32, 0.16), limb([(-1.4, 0.4), (-1.0, -0.35), (-1.45, -0.75), (-1.35, -1.35)], 0.48, 0.16)]
    far = [limb([(0.9, 0.2), (0.95, -0.5), (1.0, -1.32)], 0.3, 0.15), limb([(-0.95, 0.3), (-0.6, -0.35), (-1.0, -0.75), (-0.9, -1.32)], 0.42, 0.15)]
    hooves = [poly((1.22, -1.35), (1.42, -1.35), (1.45, -1.48), (1.2, -1.48)), poly((-1.43, -1.35), (-1.27, -1.35), (-1.24, -1.48), (-1.47, -1.48))]
    fhooves = [poly((0.92, -1.32), (1.08, -1.32), (1.1, -1.45), (0.9, -1.45)), poly((-0.98, -1.32), (-0.82, -1.32), (-0.8, -1.45), (-1.0, -1.45))]
    tail = [quad((-1.82, 0.85), (-2.15, 0.3), (-2.1, -0.3), 10), lens((-2.1, -0.3), (-2.15, -0.75), 0.25)]
    front = [ear, head, neck, body, *legs, *hooves]
    sil = union(head, neck, body, *legs)
    sil = hide(sil, ear) + [ear]
    hn = hide(horns, head, ear)
    hn = [hn[0]] + hide(hn[1:], horns[0]) if hn else hn
    ridges = []
    for h in horns:
        c = spl([(2.18, 2.25), (1.95, 2.85), (1.55, 3.3), (1.25, 3.65)], closed=False)
    back = hide(far + fhooves, *front)
    stripes = keep([[(x, 1.3), (x + 0.05, -0.1)] for x in [-1.3, -1.0, -0.7, -0.4, -0.1, 0.2, 0.5, 0.8, 1.1]], body)
    stripes = hide(stripes, *legs)
    face = [quad((2.45, 1.85), (2.6, 1.7), (2.7, 1.45), 8), ellipse(2.98, 1.4, 0.05, 0.04, 8)]
    ground = [[(-3.0, -1.48), (3.2, -1.48)]]
    grass = tuft(-2.6, -1.48, 0.7) + tuft(2.6, -1.48, 0.7) + tuft(0.1, -1.48, 0.5)
    grass = hide(grass, *front, *far)
    return make("Bongo Antelope", sil + hn + back + hooves + hide(tail, body) + stripes + face + ground + grass,
                [eye(2.38, 1.9, 0.06)])


# ================================================================== birds

@design("jungle_quetzal", T)
def quetzal(rng):
    branch = limb([(-3.3, -0.35), (0.0, -0.45), (3.3, -0.3)], 0.36, 0.3, cap0=False, cap1=False)
    head = circle(0.3, 1.75, 0.5, 50)
    crest = fringe(arc(0.3, 1.75, 0.5, math.radians(160), math.radians(40), 20), 0.14, 6)
    beak = spl([(0.72, 1.82), (1.0, 1.68, 0), (0.75, 1.55)])
    body = spl([(-0.2, 1.45), (0.55, 1.35), (0.75, 0.6), (0.5, -0.15), (0.05, -0.45), (-0.4, -0.25), (-0.65, 0.5)])
    wing = spl([(-0.15, 1.3), (0.25, 0.95), (0.25, 0.2), (-0.3, -0.7, 0), (-0.6, 0.0), (-0.6, 0.8)])
    cover = fringe(spl([(-0.5, 1.2), (0.0, 1.05), (0.28, 0.7)], closed=False), -0.13, 4)
    plumes = [lens((-0.25, -0.5), (-1.4, -3.2), 0.07), lens((-0.15, -0.5), (-0.6, -3.35), 0.07)]
    stail = lens((-0.15, -0.4), (-0.55, -1.2), 0.2)
    feet = [arc(0.1 + 0.12 * k, -0.42, 0.1, -0.3, 3.4, 8) for k in (-1, 0, 1)]
    front = [wing, beak, head, body]
    sil = union(head, body, beak)
    sil = hide(sil, wing) + [wing]
    cr = hide([crest], *[])
    br = hide([branch], *front, stail, *plumes)
    pl = hide(plumes + [stail], *front)
    pl = hide(pl[:2], branch) + pl[2:]
    breast = keep([spl([(0.7, 0.75), (0.3, 0.55), (0.25, 0.1)], closed=False)], body)
    breast = hide(breast, wing)
    leaves = leaf((2.4, -0.3), (2.9, 0.8), 0.28) + leaf((2.0, -0.32), (2.3, -1.4), 0.28) + leaf((-2.6, -0.4), (-3.1, 0.7), 0.28)
    leaves = hide(leaves, branch)
    return make("Resplendent Quetzal", sil + [crest] + br + pl + feet + breast + leaves, [eye(0.45, 1.8, 0.07)])


@design("jungle_harpy_eagle", T)
def harpy_eagle(rng):
    branch = limb([(-3.3, -2.05), (0.0, -2.0), (3.3, -2.1)], 0.42, 0.36, cap0=False, cap1=False)
    R = [(0.0, 1.0), (0.85, 0.8), (1.25, -0.1), (1.1, -1.1), (0.6, -1.75), (0.0, -1.85)]
    body = spl(R + [(-x, y) for x, y in R[-2:0:-1]])
    wings = []
    for s in (1, -1):
        wings.append(spl([(s * 0.75, 0.95), (s * 1.55, 0.4), (s * 1.65, -0.8), (s * 1.3, -2.3, 0), (s * 0.95, -1.2)]))
    head = ellipse(0.0, 1.6, 0.66, 0.58, 60)
    crest = []
    for k, a in enumerate([-50, -25, 0, 25, 50]):
        r = math.radians(90 + a)
        base = (0.25 * math.cos(r), 2.05 + 0.1 * math.sin(r))
        tip = (0.85 * math.cos(r), 1.95 + 1.0 * math.sin(r))
        crest.append(lens(base, tip, 0.18))
    beak = spl([(-0.17, 1.6), (0.17, 1.6), (0.14, 1.3), (0.0, 1.08, 0), (-0.14, 1.3)])
    disc = [arc(0.0, 1.5, 0.48, math.radians(200), math.radians(340), 16)]
    legs = [limb([(0.45, -1.4), (0.5, -1.95)], 0.42, 0.36), limb([(-0.45, -1.4), (-0.5, -1.95)], 0.42, 0.36)]
    talons = []
    for s in (1, -1):
        for k in (-1, 0, 1):
            x = s * 0.5 + 0.17 * k
            talons.append(quad((x, -1.9), (x + 0.12, -2.05), (x + 0.02, -2.3), 8))
    tail = spl([(-0.45, -1.7), (-0.55, -3.0), (0.55, -3.0), (0.45, -1.7)], closed=False)
    front = [head, *crest, *legs, *wings, body]
    hd = union(head, *crest)
    bd = hide(union(body, *legs), head, *wings)
    wg = hide(wings, head)
    br = hide([branch], *legs, *talons, body, *wings)
    tl = hide([tail], branch, *front)
    band = keep([quad((-1.0, 0.45), (0.0, 0.05), (1.0, 0.45), 14)], body)
    band = hide(band, *wings)
    feathers = []
    for s in (1, -1):
        feathers += [quad((s * 1.05, 0.2 - 0.6 * k), (s * 1.35, -0.1 - 0.6 * k), (s * 1.55, -0.2 - 0.6 * k), 6) for k in range(3)]
    feathers = keep(feathers, *wings)
    leg_f = [[(0.3, -1.6), (0.35, -1.85)], [(-0.3, -1.6), (-0.35, -1.85)]]
    return make("Harpy Eagle", hd + bd + wg + [beak] + disc + br + tl + talons + band + feathers,
                [eye(0.3, 1.68, 0.08), eye(-0.3, 1.68, 0.08)])


@design("jungle_cassowary", T)
def cassowary(rng):
    top = spl([(0.95, 0.0), (1.15, 0.6), (0.85, 1.25), (0.1, 1.55), (-1.1, 1.45), (-1.95, 0.85), (-2.1, 0.1)], closed=False)
    bot = fringe(spl([(-2.1, 0.1), (-1.6, -0.35), (-0.5, -0.45), (0.4, -0.35), (0.95, 0.0)], closed=False), 0.2, 11)
    body = chain(top, bot, [top[0]])
    neck = limb([(0.75, 1.0), (1.15, 1.75), (1.35, 2.45)], 0.5, 0.3)
    head = ellipse(1.55, 2.62, 0.36, 0.26, 30, rot=-0.15)
    beak = spl([(1.82, 2.7), (2.35, 2.5, 0), (1.85, 2.45)])
    casque = spl([(1.3, 2.75), (1.32, 3.25), (1.55, 3.55), (1.78, 3.3), (1.82, 2.8)])
    wattles = [lens((1.25, 2.2), (1.05, 1.65), 0.3), lens((1.42, 2.15), (1.48, 1.6), 0.3)]
    legs = [limb([(0.35, -0.2), (0.45, -1.0), (0.35, -2.05)], 0.38, 0.26), limb([(-0.3, -0.2), (-0.45, -1.0), (-0.55, -2.05)], 0.36, 0.24)]
    toes = []
    for x, f in [(0.35, legs[0]), (-0.55, legs[1])]:
        toes.append([limb([(x, -2.05), (x + 0.55, -2.15)], 0.13, 0.08), limb([(x, -2.05), (x + 0.35, -2.25)], 0.13, 0.08),
                     limb([(x, -2.05), (x - 0.3, -2.15)], 0.13, 0.08)])
    near = [head, casque, *wattles, neck, body, legs[0], *toes[0]]
    sil = union(head, casque, neck, body, legs[0], *toes[0])
    sil = hide(sil, *wattles) + wattles
    far = hide([legs[1]] + toes[1], *near)
    shag = []
    fluff = keep([quad((-1.6, 1.0), (-1.2, 0.6), (-0.7, 0.55), 8), quad((-1.2, 1.25), (-0.6, 0.95), (-0.1, 0.95), 8),
                  quad((-0.6, 1.4), (0.0, 1.15), (0.5, 1.15), 8), quad((-1.75, 0.45), (-1.3, 0.1), (-0.9, 0.1), 8)], body)
    nost = [[(2.0, 2.6), (2.12, 2.57)]]
    claw = [quad((0.9, -2.15), (1.05, -2.18), (1.12, -2.1), 4)]
    ground = [[(-3.0, -2.3), (3.0, -2.3)]]
    plants = leaf((-2.8, -2.3), (-2.6, -0.6), 0.22) + leaf((-2.8, -2.3), (-2.0, -1.3), 0.22) + leaf((2.7, -2.3), (2.9, -0.8), 0.22) + \
        leaf((2.7, -2.3), (2.0, -1.4), 0.22)
    plants = hide(plants, *near)
    return make("Cassowary", sil + far + shag + fluff + nost + claw + ground + plants, [eye(1.6, 2.68, 0.06)])


@design("jungle_crowned_pigeon", T)
def crowned_pigeon(rng):
    branch = limb([(-3.3, -1.25), (0.0, -1.15), (3.3, -1.3)], 0.4, 0.34, cap0=False, cap1=False)
    head = circle(0.9, 1.1, 0.42, 40)
    beak = spl([(1.28, 1.1), (1.62, 0.98, 0), (1.27, 0.92)])
    body = spl([(0.65, 1.0), (1.05, 0.7), (1.05, 0.0), (0.6, -0.75), (-0.2, -1.0), (-1.0, -0.75), (-1.3, -0.2), (-0.8, 0.45),
                (0.0, 0.85)])
    wing = spl([(0.6, 0.45), (0.1, 0.55), (-0.8, 0.2), (-1.6, -0.55), (-2.4, -1.2, 0), (-1.2, -0.95), (-0.2, -0.75), (0.45, -0.2)])
    tail = spl([(-1.3, -0.6), (-2.6, -1.4), (-2.75, -1.65), (-2.4, -1.75), (-1.0, -1.0)])
    crest = []
    for k in range(9):
        a = math.radians(150 - 13 * k)
        base = (0.85 + 0.25 * math.cos(a), 1.25 + 0.25 * math.sin(a))
        tip = (0.85 + 1.25 * math.cos(a), 1.3 + 1.2 * math.sin(a))
        crest.append([base, tip])
        crest.append(lens((base[0] + (tip[0] - base[0]) * 0.75, base[1] + (tip[1] - base[1]) * 0.75), (tip[0] + 0.15 * math.cos(a), tip[1] + 0.15 * math.sin(a)), 0.35))
    feet = [arc(0.0 + 0.12 * k, -1.02, 0.1, -0.3, 3.4, 8) for k in (-1, 0, 1)] + [[(0.0, -0.95), (0.0, -0.8)]]
    front = [wing, beak, head, body]
    sil = union(head, body, beak)
    sil = hide(sil, wing) + [wing]
    cr = hide(crest, head)
    tl = hide([tail], *front)
    br = hide([branch], *front, tail)
    wl = keep([quad((-0.6, 0.1), (-1.2, -0.4), (-1.8, -0.8), 8), quad((0.0, -0.1), (-0.8, -0.55), (-1.5, -0.95), 8)], wing)
    mask = [quad((0.7, 1.12), (0.95, 1.2), (1.25, 1.08), 8)]
    leaves = leaf((2.4, -1.3), (2.9, -0.1), 0.28) + leaf((2.0, -1.25), (2.3, -2.3), 0.28)
    leaves = hide(leaves, branch)
    return make("Victoria Crowned Pigeon", sil + cr + tl + br + wl + mask + leaves + feet, [eye(1.0, 1.12, 0.07)])


@design("jungle_hoatzin", T)
def hoatzin(rng):
    branch = limb([(-3.3, -0.9), (0.0, -1.05), (3.3, -0.8)], 0.4, 0.34, cap0=False, cap1=False)
    head = circle(-0.75, 1.55, 0.42, 40)
    beak = spl([(-1.12, 1.55), (-1.42, 1.45, 0), (-1.1, 1.38)])
    crest = [lens((-0.7 + 0.1 * k, 1.9), (-1.0 + 0.32 * k, 2.75 - 0.08 * abs(k - 2)), 0.08) for k in range(5)]
    neck = limb([(-0.55, 1.2), (-0.35, 0.7)], 0.55, 0.65)
    body = spl([(-0.6, 0.9), (0.2, 0.85), (0.9, 0.35), (1.1, -0.35), (0.6, -0.95), (-0.2, -1.0), (-0.75, -0.5), (-0.85, 0.3)])
    wing = spl([(-0.3, 0.75), (0.5, 0.75), (1.4, 0.25), (2.1, -0.4, 0), (1.2, -0.45), (0.3, -0.5), (-0.3, -0.1)])
    tail = spl([(0.7, -0.6), (1.5, -1.4), (2.0, -2.4), (2.35, -2.65, 0), (2.4, -2.2), (1.9, -1.2), (1.05, -0.25)])
    front = [wing, beak, head, neck, body]
    sil = hide(union(head, beak, neck, body), wing) + [wing]
    cr = hide(crest, head)
    tl = hide([tail], *front)
    br = hide([branch], *front, tail)
    wl = keep([quad((0.3, 0.45), (1.0, 0.2), (1.6, -0.2), 8), quad((0.1, 0.0), (0.7, -0.15), (1.3, -0.35), 8)], wing)
    tf = keep([quad((1.0, -0.6), (1.6, -1.3), (2.1, -2.3), 10)], tail)
    face = [circle(-0.72, 1.6, 0.17, 20)]
    feet = [arc(-0.25 + 0.12 * k, -1.0, 0.1, -0.3, 3.4, 8) for k in (-1, 0, 1)] + [[(-0.25, -0.92), (-0.25, -0.85)]]
    leaves = leaf((-2.4, -0.95), (-2.9, 0.2), 0.28) + leaf((-2.0, -1.0), (-1.7, -2.1), 0.28) + leaf((2.8, -0.85), (3.2, 0.2), 0.28)
    leaves = hide(leaves, branch)
    return make("Crested Hoatzin", sil + cr + tl + br + wl + tf + face + feet + leaves, [eye(-0.72, 1.6, 0.07)])


@design("jungle_gecko_bamboo", T)
def gecko_bamboo(rng):
    a = math.radians(62)
    ux, uy = math.cos(a), math.sin(a)
    def P(s, t=0.0):
        return (s * ux - t * uy, s * uy + t * ux)
    stalk = [P(-3.6, -0.3), P(3.6, -0.3), P(3.6, 0.3), P(-3.6, 0.3), P(-3.6, -0.3)]
    nodes = [[P(s, -0.3), P(s, 0.3)] for s in (-3.0, -2.85, 2.75, 2.9)]
    leaves_b = leaf(P(2.9, 0.3), (P(2.9, 0.3)[0] - 1.9, P(2.9, 0.3)[1] + 0.2), 0.22) + leaf(P(-2.85, -0.3), (P(-2.85, -0.3)[0] + 1.9, P(-2.85, -0.3)[1] - 0.1), 0.22)
    spine = [P(s, 0.0) for s in (1.9, 1.3, 0.5, -0.4, -1.1)]
    head = spl([P(2.45, 0.0), P(2.25, 0.32), P(1.75, 0.38), P(1.45, 0.22), P(1.45, -0.22), P(1.75, -0.38), P(2.25, -0.32)])
    body = spl([P(1.5, 0.0), P(1.2, 0.33), P(0.3, 0.45), P(-0.6, 0.38), P(-1.1, 0.0), P(-0.6, -0.38), P(0.3, -0.45), P(1.2, -0.33)])
    tc = [P(-1.0, 0.0), P(-1.8, -0.3), P(-2.3, 0.4), P(-2.0, 1.0), P(-1.5, 0.75)]
    tail = limb(tc, 0.34, 0.1)
    legs, pads = [], []
    for s0, side, d in [(1.0, 1, 1), (1.0, -1, 1), (-0.5, 1, -1), (-0.5, -1, -1)]:
        sh = P(s0, side * 0.3)
        el = P(s0 + 0.35 * d, side * 0.85)
        ft = P(s0 + 0.65 * d, side * 0.85)
        legs.append(limb([sh, el, ft], 0.2, 0.15))
        for k in (-1, 0, 1):
            tp = P(s0 + 0.65 * d + 0.32 * d * math.cos(k * 0.7), side * (0.85 + 0.32 * math.sin(k * 0.7) * d))
            legs.append(limb([ft, tp], 0.07, 0.06))
            pads.append(circle(tp[0], tp[1], 0.09, 10))
    front = [head, body, tail, *legs, *pads]
    sil = union(*front)
    st = hide([stalk] + nodes, *front)
    lv = hide(leaves_b, stalk, *front)
    spots = keep([circle(*P(s, t), 0.07, 10) for s, t in [(0.9, 0.15), (0.5, -0.2), (0.1, 0.15), (-0.3, -0.15), (-0.7, 0.05)]], body)
    nost = [circle(*P(2.35, 0.1), 0.03, 6), circle(*P(2.35, -0.1), 0.03, 6)]
    e1, e2 = P(1.95, 0.28), P(1.95, -0.28)
    return make("Gecko Climbing a Bamboo Stalk", sil + st + lv + spots + nost,
                [eye(e1[0], e1[1], 0.08), eye(e2[0], e2[1], 0.08)])


# ================================================================== reptiles & fish

@design("jungle_green_iguana", T)
def green_iguana(rng):
    branch = limb([(-3.3, -0.95), (0.0, -0.75), (3.3, -1.0)], 0.45, 0.38, cap0=False, cap1=False)
    body = spl([(-1.3, -0.45), (-1.2, 0.15), (-0.2, 0.5), (0.8, 0.55), (1.35, 0.6), (1.5, 0.15), (1.2, -0.35), (0.2, -0.55)])
    head = spl([(1.2, 0.55), (1.55, 0.95), (2.2, 1.0), (2.75, 0.75), (2.95, 0.5), (2.8, 0.3), (2.2, 0.25), (1.65, 0.1), (1.35, 0.15)])
    dewlap = spl([(1.6, 0.15), (2.3, 0.25), (2.05, -0.25), (1.65, -0.5), (1.45, -0.1)])
    cheek = circle(1.8, 0.45, 0.17, 20)
    tc = [(-1.2, -0.15), (-2.0, -0.4), (-2.6, -0.9), (-2.75, -1.6), (-2.4, -2.3), (-2.0, -2.6)]
    tail = limb(tc, 0.5, 0.08)
    legs = [limb([(1.05, -0.2), (1.35, -0.6), (1.25, -0.75)], 0.28, 0.22), limb([(-0.9, -0.25), (-0.5, -0.6), (-0.65, -0.75)], 0.32, 0.24)]
    far = [limb([(0.6, -0.25), (0.75, -0.6), (0.6, -0.75)], 0.24, 0.2)]
    front = [head, dewlap, body, tail, *legs]
    sil = union(head, body, tail, *legs)
    sil = hide(sil, dewlap) + [dewlap]
    back = hide(far, *front)
    br = hide([branch], *front, *far)
    crest = zigzag(0, 1, 0, 0.1, 12)
    spine = spl([(1.55, 0.95), (1.0, 0.6), (0.0, 0.55), (-1.0, 0.25), (-1.6, 0.0)], closed=False)
    L = len(spine)
    cr = []
    for k in range(14):
        i = int((L - 1) * k / 14)
        j = int((L - 1) * (k + 0.5) / 14)
        a, b = spine[i], spine[min(L - 1, j + 1)]
        cr.append([spine[i], (spine[j][0], spine[j][1] + 0.22 - 0.008 * k), spine[int((L - 1) * (k + 1) / 14)]])
    cr = [chain(*cr)]
    bands = keep([[(-2.3 + 0.0, -0.6), (-1.95, -0.85)], [(-2.75, -1.25), (-2.35, -1.3)], [(-2.65, -1.95), (-2.3, -1.85)]], tail)
    claws = [arc(1.25 + 0.1 * k, -0.8, 0.08, math.pi + 0.3, TAU, 5) for k in (-1, 0, 1)] + \
        [arc(-0.65 + 0.1 * k, -0.8, 0.08, math.pi + 0.3, TAU, 5) for k in (-1, 0, 1)]
    mouth = [quad((2.9, 0.42), (2.5, 0.38), (2.15, 0.45), 8)]
    leaves = leaf((2.6, -0.95), (3.1, 0.2), 0.28) + leaf((0.4, -0.8), (0.0, -1.9), 0.28) + leaf((-3.0, -0.95), (-3.3, 0.2), 0.28)
    leaves = hide(leaves, branch, *front)
    return make("Green Iguana", sil + back + br + hide(cr, head) + bands + [cheek] + claws + mouth + leaves, [eye(2.35, 0.72, 0.06)])


@design("jungle_water_monitor", T)
def water_monitor(rng):
    body = spl([(-1.4, 0.0), (-1.2, 0.45), (0.0, 0.7), (1.0, 0.65), (1.5, 0.45), (1.6, 0.05), (1.0, -0.3), (-0.2, -0.35), (-1.2, -0.3)])
    neck = limb([(1.3, 0.35), (1.9, 0.45)], 0.65, 0.5)
    head = spl([(1.8, 0.7), (2.4, 0.75), (2.95, 0.55), (3.15, 0.4), (3.0, 0.25), (2.4, 0.18), (1.85, 0.2)])
    tongue = [chain([(3.12, 0.33), (3.45, 0.3)], [(3.6, 0.42)]), [(3.45, 0.3), (3.6, 0.2)]]
    tail = limb([(-1.3, 0.1), (-2.2, 0.1), (-2.9, -0.3), (-3.2, -0.9), (-2.8, -1.2)], 0.55, 0.06)
    legs = [limb([(1.1, 0.0), (1.55, -0.45), (1.4, -0.95)], 0.32, 0.24), limb([(-0.9, 0.0), (-0.4, -0.45), (-0.65, -0.95)], 0.38, 0.26)]
    far = [limb([(0.75, -0.1), (0.6, -0.5), (0.85, -0.95)], 0.28, 0.22), limb([(-1.2, -0.1), (-1.5, -0.55), (-1.35, -0.95)], 0.32, 0.24)]
    toes = []
    for x, y in [(1.4, -0.95), (-0.65, -0.95)]:
        for k in (-1, 0, 1):
            toes.append(limb([(x, y), (x + 0.25 + 0.05 * k, y - 0.08 + 0.08 * k)], 0.08, 0.05))
    front = [head, neck, body, tail, *legs, *toes]
    sil = union(*front)
    back = hide(far, *front)
    spots = []
    for x, y in [(-0.8, 0.2), (-0.3, 0.35), (0.2, 0.4), (0.7, 0.35), (-0.5, -0.05), (0.0, 0.05), (0.5, 0.05), (1.05, 0.25),
                 (-1.8, 0.15), (-2.3, 0.0)]:
        spots.append(ellipse(x, y, 0.13, 0.08, 12))
    spots = hide(keep(spots, body, tail), *legs)
    nost = [circle(3.0, 0.48, 0.03, 6)]
    mouth = [quad((3.05, 0.3), (2.6, 0.28), (2.2, 0.35), 8)]
    ground = [[(-3.3, -1.05), (0.4, -1.05)], quad((0.4, -1.05), (1.0, -1.05), (1.5, -1.3), 8), [(1.5, -1.3), (3.4, -1.3)]]
    ground = hide(ground, *front, *far)
    water = [ripples(1.8, 3.3, -1.6, 2), ripples(0.8, 3.4, -1.95, 3)]
    reeds = tuft(-2.2, -1.05, 0.8) + tuft(0.0, -1.05, 0.5) + leaf((-3.2, -1.05), (-2.9, 0.6), 0.22)
    reeds = hide(reeds, *front, *far)
    return make("Water Monitor Lizard", sil + back + spots + tongue + nost + mouth + ground + water + reeds, [eye(2.55, 0.58, 0.06)])


@design("jungle_piranha", T)
def piranha(rng):
    body = spl([(-2.0, 0.15), (-1.3, 1.1), (-0.2, 1.65), (0.9, 1.55), (1.8, 1.0), (2.3, 0.5), (2.45, 0.15, 0), (2.0, 0.0, 0),
                (2.35, -0.25, 0), (2.2, -0.65), (1.5, -1.25), (0.3, -1.5), (-0.9, -1.15), (-1.8, -0.35)])
    tail = spl([(-1.9, 0.1), (-2.7, 0.95), (-3.1, 0.9, 0), (-2.75, 0.0, 0), (-3.1, -0.9, 0), (-2.7, -0.95), (-1.9, -0.2)])
    dorsal = spl([(-0.4, 1.6), (-0.65, 2.15, 0), (0.3, 1.66)])
    anal = spl([(-0.6, -1.3), (-1.0, -1.85, 0), (-0.1, -1.45)])
    pect = lens((0.9, -0.3), (0.2, -0.75), 0.3)
    teeth = zigzag(1.95, 2.42, 0.0, 0.08, 4)
    teeth = [[(2.02 + 0.1 * k, 0.07 if k % 2 == 0 else -0.08) for k in range(5)]]
    front = [body, tail, dorsal, anal]
    sil = union(body, tail, dorsal, anal)
    gill = [quad((1.0, 1.25), (0.65, 0.3), (1.0, -0.9), 14)]
    scales = []
    for r in range(4):
        for c in range(5):
            x, y = -1.4 + 0.45 * c + 0.22 * (r % 2), 0.9 - 0.5 * r
            scales.append(arc(x, y, 0.2, -0.9, 0.9, 6))
    scales = keep(scales, body)
    scales = hide(scales, pect, ellipse(1.0, 0.2, 0.4, 1.2, 20))
    tail_l = keep([[(-2.3, 0.0), (-2.85, 0.6)], [(-2.3, 0.0), (-2.85, -0.6)]], tail)
    bubbles = [circle(2.8, 1.0, 0.12, 14), circle(3.0, 1.5, 0.17, 16), circle(2.85, 2.1, 0.1, 12)]
    weeds = [spl([(-3.0, -3.0), (-2.7, -2.2), (-3.0, -1.6), (-2.8, -1.0)], closed=False),
             spl([(2.4, -3.0), (2.7, -2.3), (2.45, -1.7)], closed=False), spl([(2.9, -3.0), (3.1, -2.4), (2.9, -1.9), (3.1, -1.4)], closed=False)]
    weeds = hide(weeds, *front)
    pebbles = [ellipse(-1.5, -2.85, 0.35, 0.15, 20), ellipse(-0.6, -2.9, 0.25, 0.1, 16), ellipse(1.0, -2.85, 0.4, 0.15, 20)]
    floor = [[(-3.3, -3.0), (3.3, -3.0)]]
    return make("Red-Bellied Piranha", sil + [pect] + teeth + gill + scales + tail_l + bubbles + weeds + pebbles + floor,
                [eye(1.55, 0.6, 0.12)])


@design("jungle_arapaima", T)
def arapaima(rng):
    body = spl([(-2.4, 0.0), (-1.8, 0.45), (-0.5, 0.75), (1.0, 0.75), (2.2, 0.55), (3.1, 0.2), (3.25, 0.0), (3.1, -0.2),
                (2.2, -0.5), (0.8, -0.7), (-0.6, -0.65), (-1.9, -0.4)])
    tail = spl([(-2.3, 0.05), (-3.0, 0.55), (-3.35, 0.35), (-3.35, -0.35), (-3.0, -0.55), (-2.3, -0.1)])
    dorsal = spl([(-0.8, 0.7), (-1.4, 0.95), (-2.2, 0.75), (-2.3, 0.3)])
    anal = spl([(-0.9, -0.62), (-1.5, -0.9), (-2.2, -0.65), (-2.3, -0.25)])
    pect = lens((2.0, -0.2), (1.4, -0.7), 0.3)
    sil = union(body, tail, dorsal, anal)
    scales = []
    for r in range(3):
        for c in range(9):
            x, y = -1.6 + 0.4 * c + 0.2 * (r % 2), 0.45 - 0.42 * r
            scales.append(arc(x, y, 0.2, -1.0, 1.0, 6))
    scales = hide(keep(scales, body), pect, ellipse(2.6, 0.0, 0.75, 0.8, 30))
    gill = [quad((2.2, 0.5), (1.95, 0.0), (2.2, -0.45), 10)]
    mouth = [[(3.2, -0.05), (2.85, -0.05)]]
    weeds = []
    for x, h in [(-2.9, 2.0), (-2.4, 1.4), (-0.6, 1.2), (0.3, 1.8), (2.2, 1.3), (2.8, 2.0)]:
        weeds.append(spl([(x, -2.6), (x + 0.2, -2.6 + h * 0.35), (x - 0.15, -2.6 + h * 0.7), (x + 0.1, -2.6 + h)], closed=False))
    weeds = hide(weeds, *[body, tail, dorsal, anal])
    floor = [wave(-3.3, 3.3, -2.6, 0.08, 3, 60)]
    surface = [ripples(-3.3, 3.3, 2.4, 6), ripples(-2.5, 2.5, 2.0, 5, 0.04)]
    bubbles = [circle(3.3, 0.6, 0.1, 12), circle(3.4, 1.0, 0.13, 14), circle(3.25, 1.45, 0.08, 10)]
    fish = [spl([(1.0, 1.6), (1.4, 1.75), (1.8, 1.6), (1.4, 1.45)]), poly((1.0, 1.6), (0.8, 1.75), (0.8, 1.45))]
    return make("Arapaima, Giant of the Amazon", sil + [pect] + scales + gill + mouth + weeds + floor + surface + bubbles + fish,
                [eye(2.75, 0.18, 0.08)])


# ================================================================== plants & places

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


@design("jungle_kapok_tree", T)
def kapok_tree(rng):
    canopy = crown(0.0, 2.15, 2.6, 0.75, 13, 0.13)
    trunk = [spl([(-0.3, 1.5), (-0.35, 0.0), (-0.45, -1.5), (-0.9, -2.3), (-1.8, -2.75)], closed=False),
             spl([(0.3, 1.5), (0.35, 0.0), (0.45, -1.5), (0.9, -2.3), (1.8, -2.75)], closed=False)]
    butt = [spl([(-0.4, -1.4), (-0.6, -2.3), (-0.75, -2.75)], closed=False), spl([(0.4, -1.4), (0.6, -2.3), (0.7, -2.75)], closed=False),
            spl([(0.0, -1.8), (0.0, -2.75)], closed=False)]
    branches = [spl([(-0.25, 1.3), (-1.2, 1.7), (-1.9, 1.9)], closed=False), spl([(0.25, 1.3), (1.1, 1.75), (1.8, 1.9)], closed=False),
                spl([(0.0, 1.4), (0.1, 1.85)], closed=False)]
    branches = keep(branches, canopy)
    trunk = hide(trunk + butt, canopy)
    under = [crown(-2.2, -1.4, 1.1, 0.75, 7, 0.15, seed=0.3), crown(2.3, -1.5, 1.0, 0.7, 7, 0.15, seed=0.7),
             crown(-1.3, -2.0, 0.8, 0.5, 6, 0.15, seed=1.1), crown(1.5, -2.1, 0.75, 0.5, 6, 0.15)]
    trunk_shape = poly((-0.3, 1.6), (0.3, 1.6), (0.45, -1.5), (1.8, -2.75), (-1.8, -2.75), (-0.45, -1.5))
    under_v = []
    for i, u in enumerate(under):
        under_v += hide([u], trunk_shape, *under[i + 1:]) if i < 2 else hide([u], trunk_shape)
    under_v = hide(under_v[:2], *under[2:]) + under_v[2:]
    ground = [[(-3.3, -2.75), (3.3, -2.75)]]
    birds = [chain(arc(-2.0, 3.4, 0.2, 0.3, 2.8, 6), arc(-1.6, 3.4, 0.2, 0.3, 2.8, 6)),
             chain(arc(1.5, 3.6, 0.15, 0.3, 2.8, 6), arc(1.8, 3.6, 0.15, 0.3, 2.8, 6))]
    bark = [[(-0.1, 0.9), (-0.12, 0.2)], [(0.12, 0.0), (0.15, -0.8)]]
    return make("Giant Kapok Tree", [canopy] + branches + trunk + under_v + ground + birds + bark)


@design("jungle_strangler_fig", T)
def strangler_fig(rng):
    canopy = crown(0.0, 2.1, 2.7, 0.95, 11, 0.14, seed=0.4)
    host = [[(-0.55, 1.4), (-0.55, -2.6)], [(0.55, 1.4), (0.55, -2.6)]]
    roots = []
    for k in range(4):
        x0 = -0.45 + 0.3 * k
        pts = []
        for i in range(41):
            y = 1.4 - 4.05 * i / 40
            x = x0 + 0.5 * math.sin(i / 40 * TAU * 1.1 + k * 1.6)
            if y < -1.7:
                x += (x0 + 0.05) * (-1.7 - y) * 2.2
            pts.append((x, y))
        roots.append(tube(pts, 0.3))
    vis = []
    for i, r in enumerate(roots):
        vis += hide([r], *roots[i + 1:])
    vis = hide(vis, canopy)
    leafy = keep([arc(x, y, 0.35, 0.3, 2.8, 10) for x, y in [(-1.6, 2.2), (-0.7, 2.5), (0.4, 2.3), (1.4, 2.5), (-1.1, 1.75),
                                                             (0.9, 1.8), (1.9, 2.0), (-2.0, 1.7)]], canopy)
    host_v = hide(host, canopy, *roots)
    ground = [[(-3.3, -2.65), (3.3, -2.65)]]
    ferns = palm_frond((-2.3, -2.65), (-3.0, -0.6), 0.15) + palm_frond((2.3, -2.65), (3.0, -0.7), -0.15)
    vines = [spl([(-1.8, 1.4), (-1.9, 0.3), (-1.7, -0.6)], closed=False), spl([(1.9, 1.35), (2.0, 0.6), (1.85, 0.0)], closed=False)]
    vines = hide(vines, canopy)
    return make("Strangler Fig Tree", [canopy] + vis + leafy + host_v + ground + ferns + vines)


@design("jungle_buttress_roots", T)
def buttress_roots(rng):
    trunk = [[(-0.75, 3.4), (-0.7, 1.4)], [(0.75, 3.4), (0.7, 1.4)]]
    G = -2.5
    planks = [  # (top edge start, c1, c2, end) back to front
        ((-0.3, 1.2), (-0.6, -0.2), (-1.4, -1.6), (-2.3, G + 0.35)),
        ((0.3, 1.2), (0.6, -0.2), (1.5, -1.5), (2.4, G + 0.35)),
        ((-0.7, 1.4), (-1.0, 0.0), (-2.4, -1.2), (-3.3, G - 0.1)),
        ((0.7, 1.4), (1.0, 0.0), (2.4, -1.3), (3.3, G - 0.1)),
        ((0.0, 1.0), (0.1, -0.6), (0.4, -1.8), (0.55, G - 0.45)),
    ]
    shapes, edges = [], []
    for st, c1, c2, en in planks:
        top = cubic(st, c1, c2, en, 30)
        base_x = st[0] * 0.6
        shp = chain(top, [(en[0], en[1] - 0.05), (base_x, G - 0.2), (st[0], st[1])])
        shapes.append(shp)
        edges.append(top + [(en[0], en[1] - 0.05)])
    vis = []
    for i, e in enumerate(edges):
        vis += hide([e], *shapes[i + 1:])
    gnd = [[(-3.3, G - 0.05), (3.3, G - 0.05)], [(-3.3, G - 0.5), (3.3, G - 0.5)]]
    gnd = hide(gnd, *shapes)
    gnd = [[(-3.3, G + 0.1), (-2.3, G + 0.3)]] + hide([[(-3.3, G - 0.5), (3.3, G - 0.5)]], shapes[-1])
    tr = hide(trunk, *shapes)
    bark = keep([spl([(-0.35, 3.3), (-0.3, 2.4), (-0.4, 1.6)], closed=False), spl([(0.3, 3.2), (0.35, 2.5), (0.25, 1.7)], closed=False)],
                poly((-0.75, 3.4), (0.75, 3.4), (0.7, 1.4), (-0.7, 1.4)))
    shrooms = []
    for x, y, r in [(1.25, -1.3, 0.28), (1.65, -1.6, 0.22)]:
        shrooms += [chain(arc(x, y, r, 0.0, math.pi, 12), [(x - r, y)], [(x + r, y)]), [(x - 0.06, y), (x - 0.06, y - 0.3)], [(x + 0.06, y), (x + 0.06, y - 0.3)]]
    ferns = palm_frond((-2.7, G - 0.5), (-3.3, 0.2), 0.12) + palm_frond((2.9, G - 0.5), (3.3, -0.2), -0.12)
    ferns = hide(ferns, *shapes)
    vine = [spl([(-0.5, 3.4), (-0.2, 2.8), (-0.45, 2.2), (-0.15, 1.6)], closed=False)]
    return make("Buttress Roots of a Rainforest Giant", vis + tr + gnd + bark + shrooms + ferns + vine)


@design("jungle_giant_water_lily", T)
def giant_water_lily(rng):
    pads = [(-1.7, 0.9, 1.35, 0.42), (1.6, 1.25, 1.15, 0.36), (0.4, -0.6, 1.9, 0.6), (-2.2, -1.9, 1.1, 0.34), (2.2, -1.75, 1.2, 0.36)]
    outs, shapes = [], []
    order = sorted(range(len(pads)), key=lambda i: pads[i][1])  # front (low) first
    for i in order:
        cx, cy, rx, ry = pads[i]
        rim = ellipse(cx, cy, rx, ry, 90)
        inner = ellipse(cx, cy + 0.08, rx - 0.12, ry - 0.06, 90)
        notch = [(cx + (rx - 0.12) * 0.3, cy + 0.02 - (ry - 0.06) * 0.95), (cx + rx * 0.05, cy - ry * 0.4)]
        ribs = [[(cx, cy + 0.04), (cx + (rx - 0.2) * math.cos(a), cy + 0.08 + (ry - 0.12) * math.sin(a))] for a in
                [0.3, 1.0, 1.8, 2.5, 3.3, 4.1, 5.6]]
        outs += hide([rim, inner] + ribs + [notch], *shapes)
        shapes.append(rim)
    fl = []
    cx, cy = 0.5, 0.0
    petals = []
    for k in range(7):
        a = math.radians(200 + 140 * k / 6)
        petals.append(lens((cx, cy - 0.1), (cx + 1.0 * math.cos(a) * -1, cy + 0.55 + 0.45 * abs(math.sin(a + 1.57)) * 0.3), 0.32))
    back_p = [lens((cx, cy + 0.0), (cx + dx, cy + 1.3 - abs(dx) * 0.35), 0.3) for dx in (-0.9, -0.45, 0.0, 0.45, 0.9)]
    front_p = [lens((cx, cy - 0.05), (cx + dx, cy + 0.85 - abs(dx) * 0.4), 0.33) for dx in (-0.75, -0.25, 0.25, 0.75)]
    flower = union(*front_p) + hide(back_p, *front_p)
    outs = hide(outs, *front_p, *back_p)
    water = [ripples(-3.3, -2.0, 0.15, 1), ripples(2.8, 3.4, 0.4, 1), ripples(-3.3, -1.0, -1.05, 2), ripples(-0.8, 3.3, -2.55, 4),
             ripples(-3.3, 0.8, -2.85, 4), ripples(-0.2, 3.3, 2.2, 3), ripples(-3.3, -0.4, 2.0, 3)]
    water = hide(water, *shapes)
    bud = [lens((2.9, 0.3), (2.95, 1.2), 0.3), [(2.9, 0.3), (2.85, -0.1)]]
    bud = hide(bud, *shapes)
    return make("Giant Amazon Water Lily", outs + flower + water + bud)


@design("jungle_pitcher_plant", T)
def pitcher_plant(rng):
    stem = spl([(-3.2, 2.6), (-1.8, 2.2), (-0.4, 2.5), (1.2, 2.1), (3.2, 2.5)], closed=False)
    out = [stem]
    leaves = [((-2.4, 2.35), (-2.6, 1.0)), ((-0.9, 2.35), (-1.2, 1.15)), ((0.7, 2.25), (0.85, 1.0)), ((2.3, 2.3), (2.25, 1.1))]
    pitchers = [(-2.35, -0.6, 0.55), (-0.6, -1.4, 0.75), (1.2, -0.35, 0.6), (2.6, -1.5, 0.5)]
    for (b, t), (px, py, s) in zip(leaves, pitchers):
        out += leaf(b, t, 0.22)
        out.append(spl([t, (t[0] + 0.15, (t[1] + py + 1.3 * s) / 2 + 0.3), (px + 0.35 * s, py + 1.35 * s)], closed=False))
        body = spl([(px - 0.45 * s, py + 1.05 * s), (px - 0.6 * s, py + 0.2 * s), (px - 0.55 * s, py - 0.7 * s), (px, py - 1.0 * s),
                    (px + 0.55 * s, py - 0.7 * s), (px + 0.6 * s, py + 0.2 * s), (px + 0.45 * s, py + 1.05 * s)], closed=False)
        rim = ellipse(px, py + 1.08 * s, 0.48 * s, 0.17 * s, 40)
        lid = spl([(px + 0.15 * s, py + 1.22 * s), (px + 0.2 * s, py + 1.7 * s), (px + 0.65 * s, py + 1.85 * s), (px + 0.75 * s, py + 1.4 * s),
                   (px + 0.4 * s, py + 1.2 * s)], closed=False)
        wings = [spl([(px - 0.12 * s, py + 0.9 * s), (px - 0.15 * s, py - 0.1 * s), (px - 0.05 * s, py - 0.85 * s)], closed=False)]
        out += [body, rim] + hide([lid], ellipse(px, py + 1.08 * s, 0.48 * s, 0.17 * s, 40)) + wings
        out += [arc(px + 0.1 * s, py + 0.95 * s - 0.0, 0.32 * s, math.pi + 0.4, TAU - 0.4, 10)]
    fly = [ellipse(0.2, 0.6, 0.12, 0.07, 12), lens((0.2, 0.62), (0.05, 0.85), 0.35), lens((0.22, 0.62), (0.4, 0.82), 0.35)]
    return make("Hanging Pitcher Plant", out + fly)


@design("jungle_rafflesia", T)
def rafflesia(rng):
    cx, cy = 0.0, -0.1
    petals = []
    for k in range(5):
        a = math.pi / 2 + k * TAU / 5
        petals.append(ellipse(cx + 1.55 * math.cos(a), cy + 1.0 * math.sin(a), 1.05, 0.72, 60, rot=a))
    disc = ellipse(cx, cy, 1.05, 0.65, 70)
    hole = ellipse(cx, cy + 0.12, 0.62, 0.3, 50)
    rim_in = ellipse(cx, cy + 0.12, 0.8, 0.42, 50)
    order = [0, 1, 4, 2, 3]
    vis = []
    for k in order:
        later = [petals[j] for j in order[order.index(k) + 1:]]
        vis += hide([petals[k]], disc, *later)
    spots = []
    for k in range(5):
        a = math.pi / 2 + k * TAU / 5
        for r, d in [(1.9, 0.0), (1.55, 0.35), (1.55, -0.35), (2.25, 0.25), (2.25, -0.25)]:
            x = cx + r * math.cos(a) - d * math.sin(a)
            y = cy + r * 0.66 * math.sin(a) + d * math.cos(a) * 0.66
            spots.append(circle(x, y, 0.09, 10))
    spots = hide(spots, disc)
    vis_spots = []
    for sp in spots:
        vis_spots += keep([sp], *petals)
    spikes = [[(cx + 0.35 * k, cy + 0.12 - 0.1), (cx + 0.35 * k, cy + 0.32)] for k in (-1, 0, 1)]
    bud = [spl([(2.6, -2.6), (2.25, -2.0), (2.4, -1.5), (2.8, -1.3), (3.2, -1.6), (3.3, -2.2), (3.0, -2.6)]),
           spl([(2.5, -2.3), (2.75, -1.8), (3.1, -1.5)], closed=False), spl([(2.9, -2.55), (3.05, -2.0), (3.25, -1.75)], closed=False)]
    ground = [[(-3.3, -2.6), (3.3, -2.6)]]
    ground = hide(ground, *petals)
    leaves = leaf((-2.8, -2.6), (-3.2, -1.2), 0.25) + leaf((-2.5, -2.6), (-1.9, -1.6), 0.25)
    leaves = hide(leaves, *petals)
    return make("Giant Rafflesia Flower", vis + [disc, rim_in, hole] + vis_spots + bud + ground + leaves)


@design("jungle_bromeliad", T)
def bromeliad(rng):
    branch = limb([(-3.3, -1.6), (-1.0, -1.25), (1.0, -1.3), (3.3, -1.7)], 0.7, 0.55, cap0=False, cap1=False)
    leaves = []
    specs = [(90, 1.7), (125, 2.3), (55, 2.3), (160, 2.8), (20, 2.8)]
    for a, L in specs:
        r = math.radians(a)
        bx = 0.45 * math.cos(r)
        b1, b2 = (bx - 0.38, -1.0), (bx + 0.38, -1.0)
        tip = (bx + L * math.cos(r), -1.0 + L * math.sin(r) * 0.55 + (0.3 if 30 < a < 150 else -0.1))
        up = 0.9 * math.sin(r) + 0.5
        c1 = (bx + 0.5 * L * math.cos(r) - 0.45 * math.sin(r), -1.0 + up + 0.4 * abs(math.cos(r)))
        c2 = (bx + 0.5 * L * math.cos(r) + 0.45 * math.sin(r), -1.0 + up - 0.4 * abs(math.cos(r)))
        leaves.append(chain(quad(b1, c1, tip, 16), quad(tip, c2, b2, 16), [b1]))
    lv_vis = []
    for i, l in enumerate(leaves):
        lv_vis += hide([l], *leaves[i + 1:])
    leaves = lv_vis
    spike = limb([(0.0, -0.8), (0.05, 1.0), (0.0, 2.2)], 0.22, 0.16)
    bracts = []
    for k in range(6):
        y = 0.9 + 0.32 * k
        s = 1 if k % 2 else -1
        bracts.append(lens((0.0, y), (s * 0.55, y + 0.25), 0.3))
    top = [lens((0.0, 2.2), (0.0, 2.75), 0.3)]
    front = bracts + top
    sp = hide([spike], *front)
    lv = hide(leaves, spike, *bracts)
    lv = [l for l in lv]
    br = hide([branch], *[poly((-2.4, -1.0), (2.4, -1.0), (0.4, -1.6), (-0.4, -1.6))])
    br = hide([branch], ellipse(0.0, -1.1, 0.5, 0.3, 20))
    bark = keep([spl([(-3.0, -1.5), (-1.8, -1.35), (-1.0, -1.4)], closed=False), spl([(1.2, -1.5), (2.2, -1.6), (3.0, -1.75)], closed=False)], branch)
    cup = []
    moss = []
    return make("Bromeliad on a Branch", front + sp + lv + br + bark + cup + moss)


@design("jungle_heliconia", T)
def heliconia(rng):
    stalk = spl([(0.2, 3.0), (0.3, 1.5), (0.1, 0.0), (0.2, -1.5)], closed=False)
    bracts = []
    for k in range(7):
        t = k / 7
        y = 2.7 - 0.62 * k
        x = 0.25 - 0.05 * math.sin(k)
        s = 1 if k % 2 == 0 else -1
        L = 1.15 - 0.08 * k
        tip = (x + s * L, y - 0.55)
        bracts.append(spl([(x, y + 0.12), (x + s * 0.45 * L, y + 0.05), (tip[0], tip[1], 0), (x + s * 0.35 * L, y - 0.3), (x, y - 0.25)]))
    vis = []
    for i, b in enumerate(bracts):
        vis += hide([b], *bracts[:i])
    sk = hide([stalk], *bracts)
    flowers = []
    for i, b in enumerate(bracts):
        s = 1 if i % 2 == 0 else -1
        y = 2.7 - 0.62 * i
        flowers.append(quad((0.25 + s * 0.3, y - 0.05), (0.25 + s * 0.5, y + 0.2), (0.25 + s * 0.6, y + 0.35), 6))
    flowers = hide(flowers, *bracts[:0])
    big = [spl([(-0.1, -1.5), (-1.2, -0.6), (-2.6, 1.0), (-3.0, 2.6, 0), (-2.0, 1.6), (-0.9, 0.2), (-0.1, -1.4)]),
           spl([(0.3, -1.5), (1.4, -1.2), (2.6, -0.1), (3.2, 1.3, 0), (2.2, 0.6), (1.2, -0.4), (0.3, -1.4)])]
    ribs = [spl([(-0.1, -1.45), (-1.5, 0.3), (-3.0, 2.6)], closed=False), spl([(0.3, -1.45), (1.9, -0.5), (3.2, 1.3)], closed=False)]
    leafy = hide(big + ribs, *bracts, tube(stalk, 0.1))
    veins = []
    for k in range(4):
        t = 0.2 + 0.18 * k
        veins.append([(-0.1 - 2.9 * t, -1.45 + 4.0 * t * 0.95), (-0.1 - 2.9 * t - 0.3, -1.45 + 4.0 * t * 0.95 + 0.35)])
        veins.append([(0.3 + 2.9 * t, -1.45 + 2.75 * t), (0.3 + 2.9 * t + 0.1, -1.45 + 2.75 * t - 0.4)])
    veins = hide(keep(veins, *big), *bracts)
    ground = [[(-1.5, -1.6), (1.8, -1.6)]]
    return make("Heliconia Lobster Claws", vis + sk + leafy + veins + ground)


@design("jungle_temple_ruins", T)
def temple_ruins(rng):
    tiers = []
    G = -2.4
    for k in range(5):
        w = 2.9 - 0.45 * k
        y0 = G + 0.7 * k
        tiers.append(poly((-w, y0), (w, y0), (w - 0.18, y0 + 0.7), (-w + 0.18, y0 + 0.7)))
    shrine = rect(-0.75, G + 3.5, 0.75, G + 4.5)
    roof = poly((-0.95, G + 4.5), (0.95, G + 4.5), (0.6, G + 4.85), (-0.6, G + 4.85))
    door = chain([(-0.28, G + 3.5), (-0.28, G + 4.05)], arc(0.0, G + 4.05, 0.28, math.pi, 0.0, 10), [(0.28, G + 3.5)])
    stairs = poly((-0.55, G), (0.55, G), (0.45, G + 3.5), (-0.45, G + 3.5))
    steps = [[(-0.55 + 0.1 * t / 3.5, G + t), (0.55 - 0.1 * t / 3.5, G + t)] for t in [0.35 * i for i in range(1, 10)]]
    struct = hide(tiers, stairs) + [stairs] + steps + [shrine, roof] + hide([door], *[])
    blocks = []
    for k in range(5):
        w = 2.9 - 0.45 * k
        y = G + 0.7 * k + 0.35
        for x in [-w + 0.6 + 0.7 * i for i in range(int((2 * w - 1.0) / 0.7) + 1)]:
            if abs(x) > 0.75 and abs(x) < w - 0.3:
                blocks.append([(x, y - 0.33), (x, y + 0.33)])
    blocks = blocks[::2]
    vines = [spl([(-2.0, G + 2.1), (-2.2, G + 1.5), (-1.95, G + 0.9), (-2.15, G + 0.3)], closed=False),
             spl([(1.5, G + 2.8), (1.7, G + 2.2), (1.45, G + 1.6), (1.65, G + 1.0)], closed=False),
             spl([(-0.95, G + 4.5), (-1.1, G + 3.9), (-0.9, G + 3.4)], closed=False)]
    vleaves = []
    for v in vines:
        for i in (len(v) // 3, 2 * len(v) // 3):
            x, y = v[i]
            vleaves.append(lens((x, y), (x + 0.35, y + 0.1), 0.35))
    tree = [crown(1.25, G + 4.1, 0.55, 0.4, 7, 0.15), [(1.15, G + 3.5), (1.15, G + 3.75)], [(1.35, G + 3.5), (1.35, G + 3.75)]]
    blocks = hide(blocks, *[poly((x - 0.2, y - 0.6), (x + 0.2, y - 0.6), (x + 0.2, y + 0.6), (x - 0.2, y + 0.6)) for v in vines for x, y in v[::6]])
    jungle = palm_frond((-3.0, G), (-3.3, G + 2.3), 0.1) + palm_frond((3.0, G), (3.3, G + 2.0), -0.1) + \
        [crown(-2.9, G + 3.3, 0.6, 0.45, 7, 0.15), crown(2.9, G + 3.2, 0.6, 0.45, 7, 0.15)]
    jungle += [[(-2.9, G + 2.85), (-2.9, G + 1.2)], [(2.9, G + 2.75), (2.9, G + 1.5)]]
    jungle = hide(jungle, *tiers)
    ground = [[(-3.3, G), (3.3, G)]]
    birds = [chain(arc(-1.5, 2.6, 0.15, 0.3, 2.8, 6), arc(-1.22, 2.6, 0.15, 0.3, 2.8, 6))]
    return make("Overgrown Jungle Temple", struct + blocks + vines + vleaves + tree + jungle + ground + birds)


@design("jungle_lianas", T)
def lianas(rng):
    trunks = [limb([(-2.6, -3.0), (-2.5, 0.0), (-2.6, 3.4)], 0.9, 0.75, cap0=False, cap1=False),
              limb([(2.6, -3.0), (2.55, 0.0), (2.7, 3.4)], 0.85, 0.7, cap0=False, cap1=False)]
    ropes = []
    for (x0, y0), (x1, y1), sag in [((-2.1, 2.8), (2.2, 2.4), 2.6), ((-2.1, 1.6), (2.2, 0.8), 2.2), ((-2.1, 0.2), (2.15, -0.3), 1.6)]:
        c = cubic((x0, y0), (x0 + 1.2, y0 - sag), (x1 - 1.2, y1 - sag), (x1, y1), 50)
        ropes.append(tube(c, 0.2))
    hang = [spl([(-0.6, 0.9), (-0.7, -0.6), (-0.5, -1.6), (-0.9, -2.0), (-1.3, -1.8), (-1.2, -1.4)], closed=False),
            spl([(1.0, 0.3), (1.15, -1.0), (0.95, -2.2)], closed=False)]
    hang = [tube(h, 0.15) for h in hang]
    allr = ropes + hang
    vis = []
    for i, r in enumerate(allr):
        vis += hide([r], *allr[i + 1:])
    vis = hide(vis, *trunks)
    lv = []
    for c in [cubic((-2.1, 2.8), (-0.9, 0.2), (1.0, -0.2), (2.2, 2.4), 50)]:
        for i in (12, 22, 32):
            x, y = c[i]
            lv += [lens((x, y - 0.1), (x - 0.3, y - 0.7), 0.35), lens((x, y - 0.1), (x + 0.35, y - 0.6), 0.35)]
    lv = hide(lv, *ropes)
    ground = [[(-3.3, -3.0), (3.3, -3.0)]]
    ferns = palm_frond((-1.5, -3.0), (-0.8, -1.4), -0.15) + palm_frond((1.6, -3.0), (0.7, -1.7), 0.15)
    ferns = hide(ferns, *trunks, *hang)
    bark = keep([spl([(-2.5, 3.3), (-2.4, 1.0), (-2.55, -1.5)], closed=False), spl([(2.6, 3.2), (2.7, 0.5), (2.55, -2.0)], closed=False)], *trunks)
    return make("Lianas Looping between the Trees", hide(trunks, *[]) + vis + lv + ground + hide(ferns, *allr) + bark)


@design("jungle_cacao_pods", T)
def cacao_pods(rng):
    trunk = limb([(-0.2, -3.0), (0.0, 0.0), (-0.3, 3.4)], 1.1, 0.8, cap0=False, cap1=False)
    pods = []
    for cx, cy, rot, s in [(0.85, 0.6, -0.5, 1.0), (-0.9, -0.6, 0.45, 1.0), (0.75, -1.7, -0.3, 0.85), (-0.85, 1.8, 0.35, 0.8)]:
        shp = [(cx + s * x * math.cos(rot) - s * y * math.sin(rot), cy + s * x * math.sin(rot) + s * y * math.cos(rot))
               for x, y in spl([(0.0, 0.75), (0.38, 0.45), (0.42, -0.2), (0.15, -0.75), (0.0, -0.95, 0), (-0.15, -0.75), (-0.42, -0.2), (-0.38, 0.45)])]
        ridges = [[(cx + s * x * math.cos(rot) - s * y * math.sin(rot), cy + s * x * math.sin(rot) + s * y * math.cos(rot))
                   for x, y in spl([(0.0, 0.72), (d * 0.6, 0.3), (d * 0.6, -0.3), (0.0, -0.9)], closed=False)] for d in (-0.4, 0.0, 0.4)]
        stem_top = (cx - s * 0.75 * math.sin(rot) * -1, cy + s * 0.75 * math.cos(rot))
        pods.append((shp, ridges, [stem_top, ((stem_top[0] + 0.0 * cx) * 0.6, stem_top[1] + 0.15)]))
    out = []
    shapes = [p[0] for p in pods]
    out += hide([trunk], *shapes)
    for shp, ridges, stem in pods:
        out += [shp] + ridges + [stem]
    flowers = []
    for x, y in [(0.45, -0.4), (-0.4, 0.5), (0.4, 2.6)]:
        flowers += [circle(x + 0.12 * math.cos(a), y + 0.12 * math.sin(a), 0.07, 8) for a in [0.3 + TAU * k / 5 for k in range(5)]]
    flowers = hide(flowers, *shapes)
    leaves = leaf((-0.2, 3.0), (-2.6, 2.4), 0.25) + leaf((-0.1, 2.6), (2.4, 3.1), 0.25) + leaf((0.1, 2.2), (2.8, 1.6), 0.22) + \
        leaf((-0.3, 3.3), (-2.0, 3.4), 0.2)
    leaves = hide(leaves, *shapes)
    bark = keep([spl([(0.1, -2.8), (0.2, -1.0), (0.05, 0.4)], closed=False), spl([(-0.35, 1.0), (-0.25, 2.5)], closed=False)], trunk)
    bark = hide(bark, *shapes)
    half = [spl([(1.9, -2.9), (1.6, -2.55), (2.0, -2.2), (3.1, -2.2), (3.3, -2.55), (3.1, -2.9)]),
            ellipse(2.5, -2.55, 0.65, 0.22, 30)]
    beans = [ellipse(2.2 + 0.3 * k, -2.55, 0.13, 0.09, 12) for k in range(3)]
    ground = [[(-3.3, -3.0), (3.3, -3.0)]]
    ground = hide(ground, half[0])
    return make("Cacao Pods on the Trunk", out + flowers + leaves + bark + half + beans + ground)


@design("jungle_mangrove", T)
def mangrove(rng):
    canopy = crown(0.0, 2.25, 2.6, 0.95, 11, 0.13, seed=0.2)
    trunk = [spl([(-0.35, 1.5), (-0.3, 0.8), (-0.4, 0.25)], closed=False), spl([(0.35, 1.5), (0.3, 0.8), (0.4, 0.25)], closed=False)]
    roots = []
    for x1, h in [(-2.9, 0.9), (-2.1, 1.2), (-1.3, 1.1), (-0.5, 0.6), (0.5, 0.6), (1.3, 1.1), (2.1, 1.2), (2.9, 0.9)]:
        x0 = max(-0.32, min(0.32, x1 * 0.12))
        roots.append(tube(quad((x0, 0.45 - abs(x1) * 0.06), ((x0 + x1) / 2, 0.45 + h * 0.4), (x1, -1.9), 20), 0.14))
    trunk = hide(trunk, canopy)
    rv = []
    for i, r in enumerate(roots):
        rv += hide([r], *roots[i + 1:])
    rv = hide(rv, canopy)
    water = [[(-3.3, -1.2), (3.3, -1.2)]]
    water = hide(water, *roots)
    below = keep(rv, poly((-4, -1.2), (4, -1.2), (4, -3), (-4, -3)))
    above = hide(rv, poly((-4, -1.2), (4, -1.2), (4, -3), (-4, -3)))
    ripple = [ripples(-3.3, 3.3, -2.3, 6, 0.05), ripples(-2.5, 2.5, -2.8, 5, 0.05)]
    ripple = hide(ripple, *roots)
    fish = [spl([(1.2, -2.0), (1.55, -1.85), (1.9, -2.0), (1.55, -2.15)]), poly((1.2, -2.0), (1.0, -1.85), (1.0, -2.15))]
    leafy = keep([arc(x, y, 0.35, 0.3, 2.8, 10) for x, y in [(-1.7, 2.2), (-0.7, 2.6), (0.5, 2.4), (1.5, 2.6), (-1.1, 1.6), (0.9, 1.7),
                                                             (1.9, 1.9), (-2.1, 1.7)]], canopy)
    pods = []
    heron = []
    return make("Mangrove Roots in the Water", [canopy] + trunk + above + below + water + ripple + fish + leafy + pods)


@design("jungle_stone_head", T)
def stone_head(rng):
    head = spl([(-1.6, -2.2, 0), (-1.75, 0.5), (-1.55, 1.7), (-0.9, 2.3), (0.0, 2.45), (0.9, 2.3), (1.55, 1.7), (1.75, 0.5), (1.6, -2.2, 0)])
    band = [spl([(-1.7, 1.2), (0.0, 1.45), (1.7, 1.2)], closed=False)]
    brows = [quad((-1.2, 0.75), (-0.65, 0.95), (-0.15, 0.7), 10), quad((1.2, 0.75), (0.65, 0.95), (0.15, 0.7), 10)]
    eyes = [lens((-1.1, 0.35), (-0.25, 0.35), 0.2), lens((1.1, 0.35), (0.25, 0.35), 0.2)]
    nose = [spl([(-0.15, 0.6), (-0.2, -0.25), (-0.5, -0.55), (-0.35, -0.75), (0.0, -0.65), (0.35, -0.75), (0.5, -0.55), (0.2, -0.25), (0.15, 0.6)],
                closed=False)]
    lips = [spl([(-0.8, -1.15), (-0.3, -0.95), (0.0, -1.0), (0.3, -0.95), (0.8, -1.15), (0.35, -1.5), (-0.35, -1.5)]),
            [(-0.8, -1.15), (0.8, -1.15)]]
    ears = [spl([(-1.72, 0.6), (-2.1, 0.5), (-2.15, -0.4), (-1.75, -0.5)], closed=False), spl([(1.72, 0.6), (2.1, 0.5), (2.15, -0.4), (1.75, -0.5)], closed=False)]
    cracks = [[(0.9, 2.3), (0.75, 1.9), (0.95, 1.6)], [(-1.6, -1.0), (-1.25, -1.3), (-1.35, -1.7)], [(1.3, -0.4), (1.1, -0.8)]]
    roots = [tube(spl([(-0.7, 3.4), (-0.6, 2.4), (-1.3, 1.9), (-1.7, 0.9), (-2.4, 0.2), (-2.6, -1.0)], closed=False), 0.18),
             tube(spl([(0.6, 3.4), (0.75, 2.3), (1.45, 1.75), (1.9, 0.6), (2.5, -0.3), (2.6, -1.6)], closed=False), 0.16)]
    face = [head] + band + brows + eyes + nose + lips + ears + cracks
    face = hide(face, *roots)
    ground = [[(-3.3, -2.2), (3.3, -2.2)]]
    ferns = palm_frond((-2.2, -2.2), (-3.1, -0.4), 0.12) + palm_frond((2.3, -2.2), (3.2, -0.6), -0.12)
    ferns = hide(ferns, head, *roots)
    leaves = []
    for r in roots:
        x, y = r[len(r) // 4]
        leaves += [lens((x, y), (x - 0.45, y + 0.25), 0.35)]
    return make("Vine-Covered Stone Head", face + roots + ground + ferns + leaves, [eye(-0.67, 0.35, 0.1), eye(0.67, 0.35, 0.1)])


@design("jungle_river_bend", T)
def river_bend(rng):
    lb = spl([(-3.3, -3.0), (-1.6, -1.8), (-1.4, -0.6), (-0.6, 0.2), (-0.3, 0.75)], closed=False)
    rb = spl([(3.3, -3.0), (1.2, -1.6), (1.0, -0.5), (0.4, 0.3), (0.15, 0.75)], closed=False)
    hills = [spl([(-3.3, 1.1), (-2.2, 1.9), (-1.0, 1.4), (0.2, 2.2), (1.6, 1.5), (2.6, 2.0), (3.3, 1.6)], closed=False)]
    sun = [arc(1.6, 2.4, 0.45, 0.0, math.pi, 16)]
    hills_line = hills
    trees = []
    for x, y, r in [(-2.6, -0.2, 0.75), (-1.8, 0.6, 0.55), (-1.05, 1.05, 0.4), (2.4, -0.3, 0.75), (1.65, 0.55, 0.55), (0.95, 1.05, 0.38)]:
        trees.append(crown(x, y + r * 0.6, r, r * 0.75, 7, 0.15, seed=x))
    trunks = []
    for x, y, r in [(-2.6, -0.2, 0.75), (-1.8, 0.6, 0.55), (-1.05, 1.05, 0.4), (2.4, -0.3, 0.75), (1.65, 0.55, 0.55), (0.95, 1.05, 0.38)]:
        trunks += [[(x - 0.06, y), (x - 0.06, y - 0.6 * r)], [(x + 0.06, y), (x + 0.06, y - 0.6 * r)]]
    tv = []
    for i, t in enumerate(trees):
        tv += hide([t], *[trees[j] for j in range(len(trees)) if (j < i) and ((j < 3) == (i < 3))])
    hills_v = hide(hills_line, *trees)
    sun = hide(sun, *trees, *[poly((-4, 0), (4, 0), (4, 1.9), (-4, 1.9))])
    sun = hide([arc(1.6, 2.45, 0.4, 0.0, math.pi, 16)], *[])
    hills_v = hide(hills_v, ellipse(1.6, 2.45, 0.4, 0.4, 30))
    palms = palm_frond((-3.0, -1.6), (-1.9, -0.6), -0.2) + palm_frond((-3.0, -1.6), (-3.3, -0.2), 0.1) + \
        palm_frond((3.0, -1.8), (2.0, -0.9), 0.2)
    ripple = [[(-0.6, -2.4), (0.6, -2.4)], [(-0.3, -1.2), (0.4, -1.2)], [(-0.1, -0.2), (0.4, -0.2)], [(-0.8, -2.85), (0.2, -2.85)]]
    canoe = []
    birds = [chain(arc(-1.0, 2.7, 0.14, 0.3, 2.8, 6), arc(-0.74, 2.7, 0.14, 0.3, 2.8, 6)),
             chain(arc(-0.4, 3.0, 0.11, 0.3, 2.8, 6), arc(-0.2, 3.0, 0.11, 0.3, 2.8, 6))]
    return make("Rainforest River Bend", [lb, rb] + tv + hide(trunks, *trees) + hills_v + sun + palms + ripple + birds)


@design("jungle_stilt_house", T)
def stilt_house(rng):
    W = -0.9
    floor = rect(-1.9, 0.0, 1.9, 0.25)
    walls = rect(-1.6, 0.25, 1.6, 1.6)
    roof = spl([(-2.4, 1.45, 0), (0.0, 3.0, 0), (2.4, 1.45, 0)], closed=False) + []
    roof = [[(-2.4, 1.45), (0.0, 3.0), (2.4, 1.45), (-2.4, 1.45)]]
    thatch = [[(-2.4 + 0.4 * k, 1.45), (-2.4 + 0.4 * k + 0.25, 1.75)] for k in range(1, 12)]
    thatch = keep(thatch, roof[0])
    thatch2 = [zigzag(-2.4, 2.4, 1.38, 0.07, 12)]
    door = rect(-0.35, 0.25, 0.35, 1.2)
    win = [rect(0.75, 0.75, 1.25, 1.2), [(1.0, 0.75), (1.0, 1.2)], rect(-1.25, 0.75, -0.75, 1.2), [(-1.0, 0.75), (-1.0, 1.2)]]
    stilts = []
    for x in (-1.7, -0.6, 0.6, 1.7):
        stilts += [[(x - 0.08, 0.0), (x - 0.08, -2.2)], [(x + 0.08, 0.0), (x + 0.08, -2.2)]]
    ladder = [[(0.5, 0.0), (0.9, -1.0)], [(0.85, 0.0), (1.25, -1.0)]] + [[(0.5 + 0.4 * t, -t), (0.85 + 0.4 * t, -t)] for t in (0.25, 0.5, 0.75)]
    water_y = -1.0
    water = [[(-3.3, water_y), (3.3, water_y)], ripples(-3.3, 3.3, -1.6, 7, 0.05), ripples(-3.0, 3.0, -2.2, 6, 0.05), ripples(-2.6, 2.6, -2.8, 5, 0.05)]
    stilts_c = [rect(x - 0.08, -2.3, x + 0.08, 0.0) for x in (-1.7, -0.6, 0.6, 1.7)]
    water = [water[0]] + water[1:]
    stilts = keep(stilts, poly((-4, -1.0), (4, -1.0), (4, 1), (-4, 1)))
    boat = [spl([(-3.0, -1.55), (-2.6, -1.85), (-1.4, -1.85), (-1.0, -1.55)], closed=False), [(-3.0, -1.55), (-1.0, -1.55)]]
    water = hide(water, poly((-3.0, -1.55), (-1.0, -1.55), (-1.4, -1.85), (-2.6, -1.85)))
    palms = [spl([(2.6, -1.0), (2.75, 0.8), (2.6, 2.4)], closed=False), spl([(2.85, -1.0), (2.98, 0.8), (2.85, 2.4)], closed=False)]
    palms += palm_frond((2.72, 2.4), (1.6, 2.0), -0.2) + palm_frond((2.72, 2.4), (3.4, 1.7), 0.2) + palm_frond((2.72, 2.4), (2.4, 3.3), -0.2)
    palms = hide(palms, *roof)
    bushes = [crown(-2.9, 0.0, 0.5, 0.5, 6, 0.15)]
    bushes = hide(bushes, poly((-4, -1.0), (4, -1.0), (4, -4), (-4, -4)), floor)
    return make("Stilt House by the Jungle River", [floor, walls, door] + hide(roof, *[]) + thatch + win + stilts + ladder + water +
                boat + palms + bushes)
