"""Coastal & Lighthouses niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "coastal"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ------------------------------------------------------------------ occlusion
# hide() removes the parts of strokes that fall inside "cover" shapes, so a
# front object can sit over a back one without lines crossing it; keep() is
# the opposite (clip a pattern to the inside of a shape); union() merges
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


def path_len(s):
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
        out += [g for g in segs if len(g) > 1 and path_len(g) > 0.06]
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


def layered(*groups):
    """Each group is (strokes, cover_shapes); earlier groups are in FRONT."""
    out, covers = [], []
    for strokes, cov in groups:
        out += hide(strokes, *covers) if covers else list(strokes)
        covers += list(cov)
    return out


# ------------------------------------------------------------------ pieces

def spline(pts, closed=True, n=10):
    """Smooth curve through points; a point given as (x, y, 1) is a sharp corner."""
    P = [(p[0], p[1]) for p in pts]
    sharp = [len(p) > 2 for p in pts]
    m = len(P)
    out = []
    for i in (range(m) if closed else range(m - 1)):
        p1, p2 = P[i], P[(i + 1) % m]
        p0 = P[i - 1] if (closed or i > 0) else p1
        p3 = P[(i + 2) % m] if (closed or i + 2 < m) else p2
        if sharp[i]:
            p0 = p1
        if sharp[(i + 1) % m]:
            p3 = p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        seg = cubic(p1, c1, c2, p2, n)
        out += seg if not out else seg[1:]
    if closed:
        out[-1] = out[0]
    return out


def tf(strokes, dx=0.0, dy=0.0, s=1.0, rot=0.0, flip=False):
    out = []
    for st in strokes:
        if flip:
            st = [(-x, y) for x, y in st]
        out.append(transform(st, dx, dy, s, rot))
    return out




def lighthouse(cx, y0, H, w0, w1, bands=(), roof_="dome", door=True, wins=(), spiral_=0, rail=True):
    """Tapered lighthouse tower with gallery and lantern room.

    Returns (strokes, covers, top_y) where top_y is the lantern centre."""
    u = w1
    top = y0 + H
    body = poly((cx - w0 / 2, y0), (cx + w0 / 2, y0), (cx + w1 / 2, top), (cx - w1 / 2, top))

    def hw(y):
        return (w0 + (w1 - w0) * (y - y0) / H) / 2

    det = []
    for f in bands:
        y = y0 + f * H
        det.append([(cx - hw(y), y), (cx + hw(y), y)])
    if spiral_:
        sl = []
        for k in range(-6, 8):
            sl.append([(cx - 3 * w0, y0 + k * H / spiral_ - 1.2 * w0), (cx + 3 * w0, y0 + k * H / spiral_ + 1.2 * w0)])
        det += keep(sl, body)
    for f in wins:
        y = y0 + f * H
        det.append(rrect(cx - 0.11 * u - 0.03, y - 0.17 * u - 0.05, cx + 0.11 * u + 0.03, y + 0.17 * u + 0.05, 0.06))
    if door:
        dw = 0.2 * u + 0.08
        dh = 0.45 * u + 0.15
        det.append(chain([(cx - dw, y0)], [(cx - dw, y0 + dh)], arc(cx, y0 + dh, dw, math.pi, 0, 10), [(cx + dw, y0)]))
    dh = 0.13 * u + 0.04
    deck = rect(cx - 0.78 * u, top, cx + 0.78 * u, top + dh)
    brackets = [[(cx - 0.78 * u + 0.05, top), (cx - w1 / 2, top - 0.25 * u)], [(cx + 0.78 * u - 0.05, top), (cx + w1 / 2, top - 0.25 * u)]]
    rt = top + dh
    rh = 0.75 * u
    room = rect(cx - 0.45 * u, rt, cx + 0.45 * u, rt + rh)
    mull = [[(cx + x * u, rt), (cx + x * u, rt + rh)] for x in (-0.15, 0.15)]
    lamp = circle(cx, rt + 0.5 * rh, 0.12 * u + 0.03, 14)
    out = [body] + det + brackets + [deck]
    rail_l = []
    if rail:
        rh2 = 0.35 * u
        rail_l = [[(cx - 0.72 * u, rt), (cx - 0.72 * u, rt + rh2), (cx + 0.72 * u, rt + rh2), (cx + 0.72 * u, rt)]]
        n = max(2, int(1.44 * u / 0.3))
        rail_l += [[(cx - 0.72 * u + 1.44 * u * k / n, rt), (cx - 0.72 * u + 1.44 * u * k / n, rt + rh2)] for k in range(1, n)]
        rail_l = hide(rail_l, rect(cx - 0.45 * u, rt, cx + 0.45 * u, rt + rh)) + [[(cx - 0.72 * u, rt + rh2), (cx + 0.72 * u, rt + rh2)]]
    rtop = rt + rh
    if roof_ == "dome":
        cap = chain([(cx - 0.58 * u, rtop)], quad((cx - 0.55 * u, rtop + 0.55 * u), (cx, rtop + 0.6 * u), 12)[1:] if False else
                    cubic((cx - 0.58 * u, rtop), (cx - 0.5 * u, rtop + 0.55 * u), (cx + 0.5 * u, rtop + 0.55 * u), (cx + 0.58 * u, rtop), 20)[1:], [(cx - 0.58 * u, rtop)])
        ch = 0.42 * u
    else:
        cap = poly((cx - 0.6 * u, rtop), (cx + 0.6 * u, rtop), (cx, rtop + 0.6 * u))
        ch = 0.6 * u
    vent = circle(cx, rtop + ch + 0.1 * u, 0.1 * u + 0.02, 12)
    fin = [[(cx, rtop + ch + 0.2 * u + 0.04), (cx, rtop + ch + 0.5 * u)]]
    out += [room] + mull + [lamp] + rail_l + [cap, vent] + fin
    covers = [body, deck, room, cap]
    return out, covers, rt + 0.5 * rh


def rocks(specs):
    """Pile of rounded boulders: specs = (cx, cy, w, h, seed)."""
    shapes = []
    for cx, cy, w, h, sd in specs:
        pts = []
        for k in range(7):
            a = k * TAU / 7 + sd
            r = 1.0 + 0.18 * math.sin(3 * a + sd * 2) + 0.1 * math.cos(5 * a)
            pts.append((cx + w * r * math.cos(a), cy + h * r * math.sin(a)))
        shapes.append(spline(pts, True, 8))
    return shapes


def rock_pile(specs, ground=None):
    sh = rocks(specs)
    out = layered(*[([s], [s]) for s in sh])
    if ground is not None:
        out = hide(out, ground)
    return out, sh


def gull(x, y, s=0.4):
    return chain(quad((x - s, y + 0.1 * s), (x - 0.5 * s, y + 0.5 * s), (x, y), 6), quad((x, y), (x + 0.5 * s, y + 0.5 * s), (x + s, y + 0.1 * s), 6)[1:])


def sea(y, x0=-3.8, x1=3.8, rows=2, amp=0.07, gap=0.45):
    return [wave(x0 + 0.3 * k, x1 - 0.3 * k, y - gap * k, amp, int((x1 - x0) / 1.2), 160) for k in range(rows)]


def beams(cx, cy, r0, r1, angs, spread=0.12):
    out = []
    for a in angs:
        out.append([(cx + r0 * math.cos(a - spread / 2), cy + r0 * math.sin(a - spread / 2)), (cx + r1 * math.cos(a - spread), cy + r1 * math.sin(a - spread))])
        out.append([(cx + r0 * math.cos(a + spread / 2), cy + r0 * math.sin(a + spread / 2)), (cx + r1 * math.cos(a + spread), cy + r1 * math.sin(a + spread))])
    return out


def house(x0, x1, y0, wall_h, roof_h, door_x=None, wins=(), chimney=None, overhang=0.15):
    """Simple gabled house front; returns (strokes, covers)."""
    mid = (x0 + x1) / 2
    walls = rect(x0, y0, x1, y0 + wall_h)
    rf = poly((x0 - overhang, y0 + wall_h), (x1 + overhang, y0 + wall_h), (mid, y0 + wall_h + roof_h))
    out = [walls]
    if door_x is not None:
        out.append(rect(door_x - 0.22, y0, door_x + 0.22, y0 + 0.75))
        out.append(circle(door_x + 0.12, y0 + 0.38, 0.04, 6))
    for wx, wy in wins:
        out.append(rect(wx - 0.2, wy - 0.22, wx + 0.2, wy + 0.22))
        out.append([(wx, wy - 0.22), (wx, wy + 0.22)])
        out.append([(wx - 0.2, wy), (wx + 0.2, wy)])
    if chimney is not None:
        ch = rect(chimney - 0.15, y0 + wall_h + 0.2, chimney + 0.15, y0 + wall_h + roof_h + 0.1)
        out = hide([ch], rf) + out
    out = hide(out, rf) + [rf]
    return out, [walls, rf]


def fence(x0, x1, y, h=0.55, step=0.32):
    n = int((x1 - x0) / step)
    out = []
    for k in range(n + 1):
        x = x0 + k * step
        out.append(poly((x - 0.09, y), (x - 0.09, y + h), (x, y + h + 0.12), (x + 0.09, y + h), (x + 0.09, y)))
    rails = [[(x0, y + 0.2), (x0 + n * step, y + 0.2)], [(x0, y + h - 0.12), (x0 + n * step, y + h - 0.12)]]
    return out, hide(rails, *out)


# ------------------------------------------------------------------ lighthouses

@design("coastal_striped_rocks", T)
def striped_rocks(rng):
    lh, lc, ly = lighthouse(0, -1.4, 3.5, 1.5, 0.95, bands=(0.25, 0.42, 0.6, 0.77), wins=(0.5,))
    rk, rc = rock_pile([(-1.7, -1.7, 1.0, 0.5, 0.3), (1.6, -1.8, 1.1, 0.55, 1.1), (0.0, -2.0, 1.4, 0.5, 2.0),
                        (-2.9, -2.4, 0.8, 0.45, 0.7), (2.9, -2.4, 0.8, 0.4, 1.7)])
    water = sea(-2.6, rows=2)
    water = hide(water, *rc)
    spray = [arc(-2.6, -1.9, 0.5, 0.4, 2.6, 10), arc(2.9, -1.95, 0.45, 0.5, 2.7, 10)]
    out = layered((lh, lc), (rk, rc), (water + spray, [])) + [gull(-2.4, 1.9, 0.35), gull(-1.6, 2.4, 0.3), gull(2.2, 2.6, 0.3)]
    return make("Striped Lighthouse on the Rocks", out)


@design("coastal_keepers_cottage", T)
def keepers_cottage(rng):
    lh, lc, ly = lighthouse(-1.6, -1.6, 3.6, 1.3, 0.85, wins=(0.45, 0.75), door=False)
    hs, hc = house(-0.9, 2.9, -1.6, 1.3, 1.1, door_x=0.2, wins=[(1.2, -0.85), (2.2, -0.85)], chimney=2.3)
    link = rect(-1.05, -1.6, -0.9, -0.6)
    fn, fr = fence(-3.4, 3.2, -2.6, 0.45, 0.4)
    path = [[(0.0, -1.6), (-0.4, -2.6)], [(0.4, -1.6), (0.8, -2.6)]]
    grass = [wave(-3.6, 3.6, -2.75, 0.04, 8, 100)]
    out = layered((fn + fr, fn), (hs, hc), (lh, lc), (path + grass, [])) + [gull(1.6, 2.3, 0.35), gull(2.5, 1.8, 0.3)]
    return make("Lighthouse with Keeper's Cottage", out)


@design("coastal_screwpile", T)
def screwpile(rng):
    hx = rect(-1.6, 0.0, 1.6, 1.3)
    roof1 = poly((-2.0, 1.3), (2.0, 1.3), (1.0, 2.2), (-1.0, 2.2))
    lr = rect(-0.45, 2.2, 0.45, 2.9)
    lr_m = [[(-0.15, 2.2), (-0.15, 2.9)], [(0.15, 2.2), (0.15, 2.9)]]
    dome = chain(cubic((-0.55, 2.9), (-0.45, 3.4), (0.45, 3.4), (0.55, 2.9), 16), [(-0.55, 2.9)])
    vent = circle(0, 3.42, 0.1, 10)
    rail = [[(-1.0, 2.2), (-1.0, 2.45), (1.0, 2.45), (1.0, 2.2)]]
    gallery = rect(-2.1, -0.25, 2.1, 0.0)
    grail = [[(-2.1, 0.0), (-2.1, 0.45), (-1.6, 0.45)], [(2.1, 0.0), (2.1, 0.45), (1.6, 0.45)]]
    wins = [rect(x - 0.22, 0.4, x + 0.22, 0.95) for x in (-0.9, 0.9)] + [rect(-0.25, 0.0, 0.25, 0.85)]
    piles = []
    for x in (-1.8, -0.6, 0.6, 1.8):
        piles.append([(x, -0.25), (x * 1.1, -2.6)])
    braces = [[(-1.8, -0.4), (-0.6 * 1.1, -1.6)], [(-0.6, -0.4), (-1.8 * 1.1, -1.6)], [(1.8, -0.4), (0.6 * 1.1, -1.6)], [(0.6, -0.4), (1.8 * 1.1, -1.6)],
              [(-0.6, -0.4), (0.66, -1.6)], [(0.6, -0.4), (-0.66, -1.6)]]
    water = sea(-1.9, rows=3, gap=0.5)
    bell = [[(1.6, 0.9), (2.4, 0.9)], chain(arc(2.4, 0.55, 0.22, 0, math.pi, 10), [(2.18, 0.4), (2.62, 0.4), (2.62, 0.55)])]
    out = layered(([lr] + lr_m + [dome, vent] + rail, [lr, dome]), ([roof1], [roof1]), ([hx] + wins, [hx]), ([gallery] + grail, [gallery]),
                  (bell, []), (piles + braces, []))
    out = hide(out, *[]) + water
    return make("Screwpile Lighthouse on Stilts", hide(out[:-3], *[]) + hide(water, *[]))


@design("coastal_storm", T)
def storm(rng):
    lh, lc, ly = lighthouse(1.2, -0.6, 3.0, 1.2, 0.75, bands=(0.5,), wins=(0.3, 0.7))
    rk, rc = rock_pile([(1.2, -1.0, 1.4, 0.55, 0.4), (2.6, -1.4, 0.8, 0.5, 1.4)])
    big = spline([(-3.8, -2.0), (-2.8, -0.6), (-1.8, 0.8), (-0.6, 1.4), (0.3, 1.0, 1), (-0.4, 0.95), (-0.9, 0.5), (-0.7, 0.0),
                  (-0.2, -0.3), (0.6, -0.9), (1.5, -1.9), (3.8, -2.6, 1), (-3.8, -2.6, 1)])
    curl = spiral(-0.6, 0.6, 0.05, 0.35, 1.1, 30)
    foam = [arc(x, y, 0.22, 0.2, math.pi - 0.2, 8) for x, y in [(-0.2, 1.4), (0.35, 1.25), (-0.8, 1.55)]]
    inner = [quad((-2.8, -1.8), (-2.0, -0.4), (-1.1, 0.4), 12), quad((-2.0, -2.2), (-1.0, -1.2), (0.0, -1.0), 12)]
    rain = [[(x, y), (x - 0.25, y - 0.6)] for x, y in [(-2.8, 3.0), (-1.8, 2.7), (-0.8, 3.1), (0.0, 2.5), (-3.3, 2.0), (-2.3, 1.8), (2.6, 3.2), (3.3, 2.4)]]
    cloud = [chain(arc(-2.4, 3.6, 0.6, 0, math.pi, 12), arc(-1.3, 3.75, 0.7, 0, math.pi, 12)[::-1][::-1] if False else arc(-1.3, 3.8, 0.7, 0.2, math.pi, 12)[::-1])]
    bolt = [poly((3.0, 3.8), (2.6, 3.0), (2.9, 3.0), (2.5, 2.2), closed=False)]
    bm = beams(1.2, ly, 0.5, 2.0, [math.pi - 0.15], 0.15)
    out = layered(([big, curl] + foam + inner, [big]), (lh, lc), (rk, rc), (rain + bolt + bm, []))
    return make("Lighthouse in a Storm", out + sea(-2.9, rows=1, amp=0.1))


@design("coastal_night_beams", T)
def night_beams(rng):
    lh, lc, ly = lighthouse(0, -1.8, 3.2, 1.3, 0.85, bands=(0.33, 0.66), wins=(0.5,))
    land = [chain(quad((-3.8, -1.6), (-2.0, -1.2), (-0.8, -1.8), 20), [(1.0, -1.8)], quad((1.0, -1.8), (2.2, -1.3), (3.8, -1.7), 20))]
    land = hide(land, *lc)
    bm = beams(0, ly, 0.75, 3.8, [0.08, math.pi - 0.08], 0.2)
    moon = [arc(-2.6, 3.0, 0.6, 0.6, 2 * math.pi - 0.6, 30), arc(-2.25, 3.0, 0.45, 1.2, 2 * math.pi - 1.2, 20)]
    moon = [chain(arc(-2.6, 3.0, 0.6, 0.9, 2 * math.pi - 0.9, 30), arc(-2.35, 3.0, 0.45, 2 * math.pi - 1.35, 1.35, 20))]
    stars_ = [star(x, y, 0.15) for x, y in [(1.6, 3.4), (2.9, 2.6), (-1.0, 3.6), (-3.3, 1.6), (0.6, 3.8), (3.3, 3.8)]]
    water = sea(-2.4, rows=3, gap=0.45)
    refl = [[(x - 0.3, y), (x + 0.3, y)] for x, y in [(0, -2.15), (0.1, -2.6), (-0.1, -3.05)]]
    return make("Lighthouse Beaming at Night", hide(lh + land + bm, *[]) + moon + stars_ + water + refl)


@design("coastal_breakwater", T)
def breakwater(rng):
    lh, lc, ly = lighthouse(2.3, 0.0, 2.2, 0.9, 0.6, bands=(0.5,), wins=(), door=True, roof_="cone")
    pier_top = [(-3.8, -0.6), (1.6, 0.0)]
    blocks = [poly((-3.8, -0.6), (3.0, 0.0), (3.0, -0.6), (-3.8, -1.3))]
    stones = keep([[(x, -1.6), (x, 0.2)] for x in [-3.2 + 0.7 * k for k in range(7)]] + [[(-3.8, -0.95), (3.0, -0.3)]], blocks[0])
    base = rect(1.6, -0.6, 3.0, 0.0)
    water = sea(-1.6, rows=3, gap=0.5)
    splash = [arc(3.2, -0.3, 0.5, 0.3, 2.0, 10), arc(3.5, -0.6, 0.4, 0.2, 1.8, 10)]
    post = [[(-1.6, -0.35), (-1.6, 0.2)], [(-0.4, -0.22), (-0.4, 0.33)]]
    chainl = [quad((-1.6, 0.15), (-1.0, -0.1), (-0.4, 0.28), 10)]
    boat = [chain(quad((-3.2, 1.5), (-2.6, 1.0), (-1.8, 1.1), 10), [(-1.6, 1.5), (-3.2, 1.5)]), [(-2.5, 1.5), (-2.5, 2.9)], poly((-2.45, 1.7), (-2.45, 2.8), (-1.6, 1.7))]
    out = layered((lh, lc), ([base], [base]), (blocks + stones + post + chainl, blocks), (splash + water + boat, []))
    return make("Lighthouse at the End of the Breakwater", out + [gull(0.4, 2.5, 0.35), gull(1.0, 3.0, 0.3)])


@design("coastal_clifftop", T)
def clifftop(rng):
    cliff = chain([(-3.8, 0.6)], [(-0.4, 0.6)], quad((-0.2, 0.6), (0.3, 0.2), (0.2, -0.4), 8), quad((0.2, -0.4), (0.8, -0.9), (0.6, -1.5), 8),
                  quad((0.6, -1.5), (1.2, -1.9), (1.0, -2.6), 8), [(-3.8, -2.6)])
    strata = keep([quad((-3.8, y), (-1.5, y + 0.15), (1.5, y - 0.1), 12) for y in (-0.2, -1.0, -1.8)], chain(cliff, [cliff[0]]))
    lh, lc, ly = lighthouse(-2.2, 0.6, 2.9, 1.1, 0.75, bands=(0.5,), wins=(0.7,))
    grass = [zigzag(-3.8, -0.4, 0.62, 0.08, 14)]
    hs, hc = house(-1.3, -0.5, 0.6, 0.6, 0.45, wins=[(-0.9, 0.9)], overhang=0.08)
    water = sea(-2.2, x0=0.8, rows=3, gap=0.45)
    crash = [arc(1.2, -2.2, 0.45, 0.3, 2.6, 10), arc(1.6, -2.0, 0.35, 0.3, 2.6, 10)]
    birds = [gull(1.5, 2.0, 0.4), gull(2.4, 2.6, 0.35), gull(3.0, 1.5, 0.3)]
    bm = beams(-2.0, ly, 0.5, 2.6, [0.25], 0.18)
    out = layered((lh, lc), (hs, hc), ([cliff] + strata, [chain(cliff, [cliff[0]])]), (grass + water + crash + birds + bm, []))
    return make("Clifftop Lighthouse", out)


def pine(cx, y0, h, w):
    """Layered conifer; returns (strokes, cover)."""
    tiers = []
    for k in range(4):
        yb = y0 + 0.25 * h + k * 0.19 * h
        ww = w * (1 - 0.22 * k)
        tiers.append(poly((cx - ww / 2, yb), (cx, yb + 0.42 * h - 0.05 * k * h), (cx + ww / 2, yb)))
    sh = union(*tiers)
    trunk = rect(cx - 0.08 * w - 0.03, y0, cx + 0.08 * w + 0.03, y0 + 0.25 * h)
    out = hide([trunk], *tiers) + sh
    return out, tiers + [trunk]


@design("coastal_cottage_tower", T)
def cottage_tower(rng):
    walls = rect(-2.6, -2.2, 1.8, -0.4)
    rf = poly((-2.9, -0.4), (2.1, -0.4), (1.2, 1.0), (-2.0, 1.0))
    tower = rect(0.0, 0.5, 0.9, 1.6)
    lh, lc, ly = lighthouse(0.45, 1.6, 0.01, 0.9, 0.9, door=False)
    door = [rect(-0.6, -2.2, 0.0, -1.1), circle(-0.1, -1.65, 0.05, 6)]
    wins = []
    for x in (-1.9, -1.1, 0.9):
        wins += [rect(x - 0.25, -1.5, x + 0.25, -0.8), [(x, -1.5), (x, -0.8)], [(x - 0.25, -1.15), (x + 0.25, -1.15)]]
    dormer = [poly((-1.6, 0.1), (-1.0, 0.1), (-1.0, 0.55), (-1.3, 0.85), (-1.6, 0.55)), rect(-1.45, 0.15, -1.15, 0.5)]
    shingles = keep([[(-3, y), (3, y)] for y in (-0.05, 0.3, 0.65)], rf)
    chim = rect(-2.2, 0.6, -1.85, 1.4)
    fn, fr = fence(-3.4, 3.4, -2.9, 0.45, 0.42)
    path = [[(-0.6, -2.2), (-1.0, -2.9)], [(0.0, -2.2), (0.4, -2.9)]]
    dune = [quad((1.8, -1.7), (2.8, -1.2), (3.6, -1.9), 12)]
    oats = [quad((x, -1.55), (x + 0.1, -0.9), (x + 0.3, -0.6), 6) for x in (2.5, 2.8, 3.1)]
    house_ = layered((lh, lc), ([tower, rect(0.15, 0.8, 0.75, 1.3)], [tower]), (dormer, dormer[:1]), ([chim], [chim]),
                     ([rf] + shingles, [rf]), ([walls] + door + wins, [walls]))
    out = layered((house_, [walls, rf, tower] + lc), (fn + fr, fn), (path + dune + oats, []))
    return make("Cottage Lighthouse with Rooftop Tower", out)


@design("coastal_skeleton", T)
def skeleton(rng):
    top, bot = 1.5, -2.6
    legs = [[(-0.7, top), (-2.0, bot)], [(0.7, top), (2.0, bot)], [(-0.3, top), (-0.8, bot)], [(0.3, top), (0.8, bot)]]
    levels = [top, 0.5, -0.5, -1.55, bot]
    def xw(y, outer=True):
        f = (top - y) / (top - bot)
        return (0.7 + 1.3 * f) if outer else (0.3 + 0.5 * f)
    struts = []
    for y in levels[1:-1]:
        struts.append([(-xw(y), y), (xw(y), y)])
    for ya, yb in zip(levels, levels[1:]):
        struts += [[(-xw(ya), ya), (-xw(yb, False), yb)], [(-xw(ya, False), ya), (-xw(yb), yb)],
                   [(xw(ya), ya), (xw(yb, False), yb)], [(xw(ya, False), ya), (xw(yb), yb)]]
    column = rect(-0.18, bot, 0.18, top)
    column_l = [[(-0.18, y), (0.18, y)] for y in (-2.0, -1.0, 0.0, 1.0)]
    watch = rect(-0.6, top, 0.6, top + 0.6)
    watch_w = [rect(-0.35, top + 0.15, -0.05, top + 0.45), rect(0.05, top + 0.15, 0.35, top + 0.45)]
    lh, lc, ly = lighthouse(0, top + 0.6, 0.01, 0.9, 0.9, door=False)
    stair = [[(0.18, -2.3 + 0.5 * k), (0.35, -2.1 + 0.5 * k)] for k in range(0)]
    ground = [[(-3.0, bot), (3.0, bot)]]
    pads = [rect(x - 0.25, bot - 0.15, x + 0.25, bot) for x in (-2.0, 2.0)]
    marsh = [quad((x, bot), (x + 0.1, bot + 0.4), (x + 0.3, bot + 0.7), 6) for x in (-2.8, -2.6, 2.5, 2.7, 2.9)]
    frame = layered((lh, lc), ([watch] + watch_w, [watch]), ([column] + column_l, [column]), (legs + struts, []))
    return make("Iron Skeleton Lighthouse", frame + ground + pads + marsh + [gull(-2.2, 2.6, 0.35), gull(2.0, 3.0, 0.3)])


@design("coastal_spiral", T)
def spiral_tower(rng):
    lh, lc, ly = lighthouse(-0.3, -1.9, 4.6, 1.3, 0.75, spiral_=4.5, wins=())
    plinth = poly((-1.2, -1.9), (0.6, -1.9), (0.75, -2.4), (-1.35, -2.4))
    dunes = [chain(quad((-3.8, -2.0), (-2.6, -1.3), (-1.4, -2.0), 14)), quad((0.8, -2.1), (2.2, -1.2), (3.8, -2.0), 14)]
    oats = [quad((x, y), (x + 0.15, y + 0.5), (x + 0.4, y + 0.75), 6) for x, y in [(-2.8, -1.6), (-2.5, -1.55), (2.0, -1.5), (2.3, -1.45), (2.6, -1.55)]]
    fence_ = [[(x, -2.3), (x, -1.9)] for x in (1.2, 1.7, 2.2, 2.7, 3.2)] + [quad((1.2, -2.0), (2.2, -2.15), (3.2, -2.0), 10)]
    ground = [[(-3.8, -2.4), (3.8, -2.4)]]
    bm = beams(-0.3, ly, 0.5, 2.6, [0.1], 0.18)
    out = layered((lh, lc), ([plinth], [plinth]), (dunes + oats + fence_ + ground + bm, []))
    return make("Spiral-Striped Lighthouse", out + [gull(2.2, 2.0, 0.35), gull(2.9, 2.6, 0.3)])


@design("coastal_pines", T)
def pines(rng):
    lh, lc, ly = lighthouse(0.3, -1.2, 3.0, 1.15, 0.8, bands=(0.85,), wins=(0.35, 0.65))
    trees = []
    for cx, y0, h, w in [(-1.9, -1.9, 3.6, 1.8), (-0.9, -2.2, 2.6, 1.4), (2.2, -2.0, 3.2, 1.6), (1.3, -2.3, 2.0, 1.1), (-3.1, -2.1, 2.4, 1.3), (3.3, -2.3, 2.2, 1.2)]:
        trees.append(pine(cx, y0, h, w))
    front = [t for t in trees[1:2] + trees[3:4]]
    back = trees[0:1] + trees[2:3] + trees[4:]
    rk, rc = rock_pile([(0.3, -1.45, 0.9, 0.35, 0.2)])
    water = sea(-2.6, rows=2, gap=0.4)
    out = layered(*(front + [(rk, rc), (lh, lc)] + back + [(water, [])]))
    return make("Red Lighthouse Among the Pines", out)


@design("coastal_fresnel", T)
def fresnel(rng):
    hive = spline([(-1.1, 3.0), (-1.9, 2.3), (-2.3, 1.0), (-2.3, -0.2), (-1.9, -1.4), (-1.1, -2.0, 1), (1.1, -2.0, 1), (1.9, -1.4), (2.3, -0.2),
                   (2.3, 1.0), (1.9, 2.3), (1.1, 3.0, 1), (-1.1, 3.0, 1)])
    band = rect(-2.4, 0.0, 2.4, 0.9)
    prisms = keep([[(-3, y), (3, y)] for y in (2.6, 2.2, 1.8, 1.35, -0.45, -0.9, -1.35, -1.7)] + [[(-3, 0.0), (3, 0.0)], [(-3, 0.9), (3, 0.9)]], hive)
    panels = keep([[(x, -2.0), (x * 0.55, 3.0)] for x in (-1.2, 1.2)], hive)
    bulls = [circle(0, 0.45, 0.32, 24), circle(0, 0.45, 0.15, 14), circle(-1.6, 0.45, 0.28, 20), circle(1.6, 0.45, 0.28, 20)]
    cap = [rect(-1.1, 3.0, 1.1, 3.2), rect(-0.5, 3.2, 0.5, 3.45)]
    ped = [rect(-1.2, -2.3, 1.2, -2.0), poly((-0.9, -2.3), (0.9, -2.3), (1.3, -3.1), (-1.3, -3.1)), rect(-1.6, -3.4, 1.6, -3.1)]
    gear = [circle(0.6, -2.7, 0.18, 14)]
    flame = lens((0, 0.0), (0, 0.9), 0.0001) if False else []
    out = [hive] + prisms + hide(panels, *bulls) + bulls + cap + ped + gear
    rays = [[(2.5 * math.cos(a), 0.45 + 2.5 * math.sin(a)), (3.4 * math.cos(a), 0.45 + 3.4 * math.sin(a))] for a in (-0.25, 0.0, 0.25, math.pi - 0.25, math.pi, math.pi + 0.25)]
    return make("Fresnel Lens Close-Up", out + rays)


@design("coastal_lantern_room", T)
def lantern_room(rng):
    gal = ellipse(0, -1.4, 3.3, 0.7, 120)
    gal2 = [(3.3 * math.cos(t), -1.4 - 0.25 + 0.7 * math.sin(t)) for t in [math.pi + math.pi * i / 60 for i in range(61)]]
    gal_s = [[(-3.3, -1.4), (-3.3, -1.65)], [(3.3, -1.4), (3.3, -1.65)]]
    rail_top = [(3.15 * math.cos(t), -0.5 + 0.65 * math.sin(t)) for t in [math.pi + math.pi * i / 60 for i in range(61)]]
    posts = [[(3.15 * math.cos(t), -1.4 + 0.65 * math.sin(t)), (3.15 * math.cos(t), -0.5 + 0.65 * math.sin(t))] for t in [math.pi + math.pi * (i + 0.5) / 9 for i in range(9)]]
    room = rect(-1.8, -1.2, 1.8, 1.6)
    base_ring = [(1.8 * math.cos(t), -1.2 + 0.35 * math.sin(t)) for t in [math.pi + math.pi * i / 40 for i in range(41)]]
    glaze = [[(x, -1.0), (x, 1.5)] for x in (-1.2, -0.4, 0.4, 1.2)]
    diag = keep([[(x, -1.0), (x + 1.2, 1.5)] for x in (-3.0, -2.2, -1.4, -0.6, 0.2, 1.0)], rect(-1.8, -1.0, 1.8, 1.5))
    sill = [[(-1.8, -1.0), (1.8, -1.0)], [(-1.8, 1.5), (1.8, 1.5)]]
    dome = chain([(-2.1, 1.6)], cubic((-2.1, 1.6), (-1.9, 3.0), (1.9, 3.0), (2.1, 1.6), 30)[1:], [(-2.1, 1.6)])
    ribs = keep([quad((x, 1.6), (x * 0.6, 2.4), (0, 2.65), 10) for x in (-1.2, 0.0, 1.2)], dome)
    vent = [circle(0, 2.95, 0.3, 20), [(0, 3.25), (0, 3.7)], poly((0.0, 3.7), (0.6, 3.55), (0.0, 3.45))]
    lens_ = [ellipse(0, 0.25, 0.75, 1.0, 40)] + keep([[(-1, y), (1, y)] for y in (-0.35, 0.05, 0.45, 0.85)], ellipse(0, 0.25, 0.75, 1.0, 40))
    inside = keep(lens_, rect(-1.8, -1.2, 1.8, 1.6))
    glass = hide(glaze + diag, *lens_[:1])
    front = rail_top and [rail_top] + posts
    out = layered((front, []), ([room] + glass + inside + sill, [room]), ([dome] + ribs + vent, [dome]), ([gal, gal2] + gal_s + [base_ring], [gal]))
    return make("Lighthouse Lantern Room and Gallery", out)


@design("coastal_lightship", T)
def lightship(rng):
    hull = poly((-3.4, 0.3), (-3.0, -1.1), (2.6, -1.1), (3.5, 0.3))
    stripe = [[(-3.33, 0.05), (3.33, 0.05)]]
    deckhouse = [rect(-1.6, 0.3, 0.4, 1.0), rect(-1.2, 0.5, -0.8, 0.8), rect(-0.4, 0.5, 0.0, 0.8)]
    stack = rect(0.7, 0.3, 1.1, 1.4)
    masts = [[(-2.3, 0.3), (-2.3, 3.4)], [(2.0, 0.3), (2.0, 3.0)]]
    cage1 = [ellipse(-2.3, 2.9, 0.5, 0.42, 30), [(-2.8, 2.9), (-1.8, 2.9)], [(-2.3, 2.48), (-2.3, 3.32)]]
    cage2 = [ellipse(2.0, 2.5, 0.4, 0.35, 24), [(1.6, 2.5), (2.4, 2.5)]]
    caps = [poly((-2.6, 3.4), (-2.0, 3.4), (-2.3, 3.7)), poly((1.75, 3.0), (2.25, 3.0), (2.0, 3.25))]
    stays = [[(-2.3, 3.4), (-3.3, 0.3)], [(2.0, 3.0), (3.4, 0.3)]]
    portholes = [circle(x, -0.45, 0.15, 12) for x in (-2.0, -1.0, 0.0, 1.0, 2.0)]
    anchor_chain = [[(3.0, -0.2), (3.4, -1.6), (3.5, -2.8)]]
    water = sea(-1.25, rows=3, gap=0.5)
    water = hide(water, hull)
    bm = beams(-2.3, 2.9, 0.6, 2.2, [math.pi + 0.1], 0.15)
    out = layered((cage1 + cage2, [cage1[0], cage2[0]]), (masts + caps + stays, []), ([stack] + deckhouse, [stack, deckhouse[0]]), ([hull] + stripe + portholes, [hull]),
                  (anchor_chain + water + bm, []))
    return make("Red Lightship at Anchor", out)


@design("coastal_keeper", T)
def keeper(rng):
    face = ellipse(-0.6, 1.4, 0.7, 0.8, 50)
    beard = spline([(-1.3, 1.25), (-1.2, 0.5), (-0.6, 0.15), (0.0, 0.5), (0.1, 1.25), (-0.25, 0.95, 1), (-0.6, 1.05), (-0.95, 0.95, 1)])
    cap = chain([(-1.35, 1.85)], quad((-1.35, 2.5), (-0.6, 2.6), (0.15, 2.5), 10)[1:], [(0.15, 1.85), (-1.35, 1.85)])
    brim = poly((-1.4, 1.85), (0.3, 1.85), (0.5, 1.65), (-1.2, 1.7))
    badge = circle(-0.6, 2.2, 0.15, 12)
    nose = quad((-0.55, 1.45), (-0.4, 1.2), (-0.6, 1.15), 6)
    coat = spline([(-1.3, 0.55), (-2.1, 0.2), (-2.3, -1.2), (-2.2, -3.0, 1), (1.0, -3.0, 1), (1.1, -1.2), (0.9, 0.2), (0.1, 0.55)])
    buttons = [circle(-0.6, y, 0.08, 8) for y in (-0.6, -1.3, -2.0)]
    lapel = [[(-0.6, 0.2), (-0.6, -2.95)]]
    arm = tube([(0.6, 0.0), (1.5, -0.6), (1.8, 0.3)], 0.5)
    hand = circle(1.85, 0.55, 0.25, 16)
    lamp_h = arc(1.85, 1.2, 0.35, math.pi * 1.1, math.pi * 1.9 + math.pi, 12)
    lamp = [poly((1.4, 1.5), (2.3, 1.5), (2.15, 1.75), (1.55, 1.75)), rect(1.5, 1.5, 2.2, 1.6)]
    glass = rrect(1.5, 0.95, 2.2, 1.5, 0.1)
    glow = lens((1.85, 1.0), (1.85, 1.4), 0.3)
    lamp_base = rect(1.45, 0.75, 2.25, 0.95)
    ring = arc(1.85, 1.75, 0.3, 0, math.pi, 10)
    rays = [[(1.85 + 0.6 * math.cos(a), 1.2 + 0.6 * math.sin(a)), (1.85 + 0.95 * math.cos(a), 1.2 + 0.95 * math.sin(a))] for a in (-0.3, 0.3, 1.0, 2.2)]
    lh, lc, ly = lighthouse(2.7, -3.0, 2.1, 0.7, 0.45, bands=(0.5,), door=False)
    lh = tf(lh, 0, 0)
    out = layered(([glass, glow, lamp_base, ring] + lamp, [glass, lamp_base] + lamp), ([hand], [hand]), ([arm], [arm]), ([brim, cap, badge], [brim, cap]),
                  ([beard], [beard]), ([face, nose], [face]), ([coat] + buttons + lapel, [coat]), (rays, []), (lh, lc))
    return make("Lighthouse Keeper with an Oil Lamp", out, [eye(-0.85, 1.55, 0.08), eye(-0.35, 1.55, 0.08)])


def cylinder(cx, y0, y1, r, ry=None, top=True):
    ry = 0.25 * r if ry is None else ry
    bottom = [(cx + r * math.cos(t), y0 + ry * math.sin(t)) for t in [math.pi + math.pi * i / 40 for i in range(41)]]
    out = [chain([(cx - r, y1)], bottom[::-1][::-1], [(cx + r, y1)])]
    out = [chain([(cx - r, y1), (cx - r, y0)], bottom[1:], [(cx + r, y1)])]
    if top:
        out.append(ellipse(cx, y1, r, ry, 50))
    cover = chain([(cx - r, y1), (cx - r, y0)], bottom[1:], [(cx + r, y1)], [(cx + r * math.cos(t), y1 + ry * math.sin(t)) for t in [math.pi * i / 30 for i in range(1, 30)]])
    return out, cover


@design("coastal_sparkplug", T)
def sparkplug(rng):
    base, bc = cylinder(0, -2.0, -0.8, 2.0, 0.45)
    base_det = keep([[(x, -2.6), (x, -0.8)] for x in (-1.4, -0.7, 0.0, 0.7, 1.4)], bc)
    base_det = [quad((-2.0, -1.4), (0, -1.95), (2.0, -1.4), 16)]
    rail = [chain([(-1.9, -0.8), (-1.9, -0.4)], [(1.9 * math.cos(t), -0.4 + 0.42 * math.sin(t)) for t in [math.pi + math.pi * i / 30 for i in range(31)]], [(1.9, -0.8)])]
    rposts = [[(1.9 * math.cos(t), -0.8 + 0.42 * math.sin(t)), (1.9 * math.cos(t), -0.4 + 0.42 * math.sin(t))] for t in [math.pi + math.pi * (i + 0.5) / 7 for i in range(7)]]
    tower, tc = cylinder(0, -0.8, 1.5, 1.2, 0.3, top=False)
    floors = [quad((-1.2, y), (0, y - 0.3), (1.2, y), 12) for y in (0.35,)]
    wins = [rect(x - 0.17, y - 0.25, x + 0.17, y + 0.25) for x in (-0.6, 0.6) for y in (-0.2, 0.9)] + [rect(-0.2, -0.75, 0.2, -0.05)]
    lh, lc, ly = lighthouse(0, 1.5, 0.01, 2.4, 1.3, door=False)
    ladder = [[(1.85, -2.5), (1.85, -0.9)], [(2.1, -2.5), (2.1, -1.0)]] + [[(1.85, y), (2.1, y)] for y in (-2.2, -1.8, -1.4, -1.1)]
    water = hide(sea(-2.3, rows=3, gap=0.45), bc)
    out = layered((lh, lc), ([tower[0]] + floors + wins, [tc]), (rail + rposts, []), (base + base_det, [bc]), (ladder + water, []))
    return make("Sparkplug Lighthouse in the Bay", out + [gull(-2.8, 2.6, 0.35), gull(2.6, 2.2, 0.3)])


@design("coastal_islet", T)
def islet(rng):
    sun = arc(1.6, -0.6, 1.5, 0, math.pi, 50)
    rays = [[(1.6 + 1.8 * math.cos(a), -0.6 + 1.8 * math.sin(a)), (1.6 + 2.4 * math.cos(a), -0.6 + 2.4 * math.sin(a))] for a in [0.25 + k * 0.38 for k in range(8)]]
    isle = chain(quad((-3.4, -0.6), (-2.6, 0.4), (-1.4, 0.5), 14), quad((-1.4, 0.5), (-0.3, 0.6), (0.4, -0.6), 14))
    lh, lc, ly = lighthouse(-1.6, 0.4, 2.2, 0.75, 0.5, bands=(0.5,), wins=())
    hs, hc = house(-1.1, -0.2, 0.25, 0.5, 0.4, wins=[], door_x=-0.65, overhang=0.08)
    tree = [circle(-2.75, 0.6, 0.35, 20), [(-2.75, 0.25), (-2.75, 0.0)]]
    water = [wave(-3.8, 3.8, -0.6 - 0.45 * k, 0.06, 6 - k, 140) for k in range(5)]
    water = [s for s in water]
    sunrefl = [[(1.6 - w, -1.0 - 0.45 * k), (1.6 + w, -1.0 - 0.45 * k)] for k, w in enumerate((1.0, 0.75, 0.5, 0.3))]
    boat = [chain(quad((2.6, 0.6), (3.0, 0.2), (3.6, 0.3), 8), [(3.7, 0.6), (2.6, 0.6)])]
    out = layered((lh, lc), (hs, hc), (tree, tree[:1]), ([isle], [chain(isle, [isle[0]])]), ([sun] + rays + water[:1], []))
    out += hide(water[1:], *[]) + hide(sunrefl, *[])
    return make("Lighthouse Islet at Sunrise", hide(out, *[]) + [gull(-0.4, 2.6, 0.35), gull(0.4, 3.0, 0.3), gull(-3.0, 2.2, 0.3)])


@design("coastal_foghorn", T)
def foghorn(rng):
    hs, hc = house(-2.0, 1.2, -1.0, 1.4, 0.9, door_x=-1.3, wins=[(0.4, -0.3)], overhang=0.15)
    horns = []
    for y, L in [(0.1, 1.8), (-0.55, 1.5)]:
        horns.append(chain([(1.2, y + 0.12)], quad((1.2 + 0.4 * L, y + 0.12), (1.2 + L, y + 0.2), (1.2 + L, y + 0.5), 10),
                           [(1.2 + L, y - 0.5)], quad((1.2 + L, y - 0.5), (1.2 + L, y - 0.2), (1.2 + 0.4 * L, y - 0.12), 10), [(1.2, y - 0.12)]))
    mouths = [ellipse(1.2 + L, y, 0.12, 0.5, 20) for y, L in [(0.1, 1.8), (-0.55, 1.5)]]
    rk, rc = rock_pile([(-1.6, -1.4, 1.4, 0.45, 0.5), (0.6, -1.5, 1.4, 0.5, 1.3), (2.6, -1.9, 0.9, 0.4, 2.2)])
    fog = [wave(x0, x1, y, 0.12, 2, 40) for x0, x1, y in [(3.0, 4.2, 0.5), (3.2, 4.4, -0.2), (2.9, 4.0, -0.8), (-3.6, -2.3, 1.6), (-3.8, -2.6, 0.9)]]
    sound = [arc(3.2, 0.1, r, -0.5, 0.5, 8) for r in (0.4, 0.8)]
    lh, lc, ly = lighthouse(-3.0, -1.0, 2.6, 0.75, 0.5, door=False, wins=(0.6,))
    water = hide(sea(-2.2, rows=2, gap=0.45), *rc)
    out = layered((horns + mouths, horns), (hs, hc), (lh, lc), (rk, rc), (water + fog, []))
    return make("Foghorn Station on the Point", out)


@design("coastal_staircase", T)
def staircase(rng):
    y0, H, w0, w1 = -3.0, 5.0, 2.8, 1.8
    lh, lc, ly = lighthouse(0, y0, H, w0, w1, door=False)
    tower = lh[0]

    def hw(y):
        return (w0 + (w1 - w0) * (y - y0) / H) / 2 - 0.2

    inner = poly((-hw(y0), y0), (hw(y0), y0), (hw(y0 + H), y0 + H), (-hw(y0 + H), y0 + H))
    stairs, rails = [], []
    y = y0
    for k in range(5):
        xa, xb = (-hw(y) + 0.1, hw(y) - 0.1) if k % 2 == 0 else (hw(y) - 0.1, -hw(y) + 0.1)
        n = 4
        rise = 0.92 / n
        run = (xb - xa) / n
        pts = [(xa, y)]
        for j in range(n):
            pts += [(xa + run * j, y + rise * (j + 1)), (xa + run * (j + 1), y + rise * (j + 1))]
        stairs.append(pts)
        rails.append([(xa + run * 0.5, y + rise + 0.45), (xb - run * 0.5, y + 0.92 + 0.45)])
        rails += [[(xa + run * (j + 0.5), y + rise * (j + 1)), (xa + run * (j + 0.5), y + rise * (j + 1) + 0.45)] for j in (0, n - 1)]
        y += 0.92
    landings = [[(-hw(y0 + 0.92 * k), y0 + 0.92 * k), (hw(y0 + 0.92 * k), y0 + 0.92 * k)] for k in range(1, 6)]
    wins = [rrect(-0.2 + sx * 0.0, y0 + 0.92 * k + 0.25, 0.2, y0 + 0.92 * k + 0.75, 0.12) for k, sx in [(0, 0), (2, 0), (4, 0)]]
    keeper = [circle(0.9, -2.0 + 0.0, 0.0001, 3)] * 0
    out = [tower] + lh[1:] + [inner] + stairs + rails + landings
    door = [chain([(-0.35, y0), (-0.35, y0 + 0.6)], arc(0, y0 + 0.6, 0.35, math.pi, 0, 10), [(0.35, y0)])]
    ground = [[(-3.0, y0), (3.0, y0)]]
    return make("Cutaway Lighthouse with Spiral Stairs", hide(out, *[]) + ground + [gull(-2.2, 2.0, 0.35), gull(2.0, 1.4, 0.3)])


# ------------------------------------------------------------------ coastal life

@design("coastal_cottage", T)
def cottage(rng):
    hs, hc = house(-2.6, 1.4, -1.6, 1.8, 1.4, door_x=-0.6, wins=[(-1.8, -0.6), (0.6, -0.6), (-0.6, 0.85)], chimney=0.7)
    shutters = [rect(x - 0.4, -0.85, x - 0.25, -0.35) for x in (-1.8, 0.6)] + [rect(x + 0.25, -0.85, x + 0.4, -0.35) for x in (-1.8, 0.6)]
    boxes = [rect(x - 0.3, -1.05, x + 0.3, -0.85) for x in (-1.8, 0.6)]
    blooms = [circle(x + dx, -0.88, 0.1, 8) for x in (-1.8, 0.6) for dx in (-0.18, 0.0, 0.18)]
    porch = [poly((-1.15, 0.2), (-0.05, 0.2), (-0.6, 0.55)), [(-1.05, 0.2), (-1.05, -1.6)], [(-0.15, 0.2), (-0.15, -1.6)]]
    shingles = keep([[(-3, y), (2, y)] for y in (-1.2, -0.8, -0.4, 0.0)], rect(-2.6, -1.6, 1.4, 0.2))
    shingles = hide(shingles, *[rect(x - 0.42, -0.9, x + 0.42, -0.3) for x in (-1.8, 0.6)], rect(-1.1, -1.6, -0.1, 0.25))
    fn, fr = fence(-3.6, 3.6, -2.7, 0.55, 0.36)
    gate_gap = rect(-1.0, -2.8, -0.2, -1.9)
    fn = hide(fn, gate_gap)
    fr = hide(fr, gate_gap)
    bush = union(circle(2.3, -1.6, 0.7, 30), circle(2.9, -1.4, 0.6, 30), circle(1.8, -1.3, 0.5, 30))
    hydr = [circle(x, y, 0.22, 12) for x, y in [(2.1, -1.2), (2.7, -1.0), (3.1, -1.6), (2.4, -1.7)]]
    path = [[(-0.85, -1.6), (-1.0, -2.7)], [(-0.35, -1.6), (-0.2, -2.7)]]
    out = layered((fn + fr, fn), (bush + hydr, [max(bush, key=len)]), (shutters + boxes + blooms + porch, boxes), (hs + shingles, hc), (path, []))
    return make("Coastal Cottage with Picket Fence", out + [gull(2.5, 2.4, 0.35), gull(3.1, 1.9, 0.3)])


def adirondack(cx, y):
    """Adirondack chair seen from behind (fan of back slats)."""
    top = arc(cx, y + 1.0, 1.25, math.radians(40), math.radians(140), 24)
    back = chain([(cx - 0.65, y)], [top[-1]], top[::-1], [(cx + 0.65, y)], [(cx - 0.65, y)])
    slats = []
    for k in (-2, -1, 1, 2):
        pass
    for f in (-0.6, -0.2, 0.2, 0.6):
        bx = cx + f * 0.65
        a = math.pi / 2 - f * (math.pi / 2 - math.radians(40))
        slats.append([(bx, y), (cx + 1.25 * math.cos(a), y + 1.0 + 1.25 * math.sin(a))])
    bar = keep([[(cx - 2, y + 0.75), (cx + 2, y + 0.75)]], back)
    arms = [rrect(cx - 1.4, y + 0.45, cx - 0.55, y + 0.62, 0.06), rrect(cx + 0.55, y + 0.45, cx + 1.4, y + 0.62, 0.06)]
    legs = [[(cx - 0.55, y), (cx - 0.55, y - 0.9)], [(cx + 0.55, y), (cx + 0.55, y - 0.9)], [(cx - 1.2, y + 0.45), (cx - 1.2, y - 1.05)], [(cx + 1.2, y + 0.45), (cx + 1.2, y - 1.05)],
            [(cx - 1.25, y - 0.1), (cx - 0.55, y - 0.1)], [(cx + 0.55, y - 0.1), (cx + 1.25, y - 0.1)]]
    return layered(([back] + slats + bar, [back]), (arms, arms), (legs, []))


@design("coastal_adirondack", T)
def adirondack_dock(rng):
    a = adirondack(-1.6, -0.5)
    b = adirondack(1.6, -0.5)
    table = [rect(-0.45, -0.75, 0.45, -0.6), [(-0.3, -0.75), (-0.3, -1.6)], [(0.3, -0.75), (0.3, -1.6)]]
    glasses = [poly((-0.3, -0.6), (-0.25, -0.15), (-0.05, -0.15), (0.0, -0.6)), poly((0.08, -0.6), (0.13, -0.2), (0.33, -0.2), (0.38, -0.6))]
    dock = [[(-3.8, -1.6), (3.8, -1.6)], [(-3.8, -2.0), (3.8, -2.0)]] + [[(x, -1.6), (x, -2.0)] for x in (-2.6, -1.1, 0.4, 1.9, 3.3)]
    piles = [rect(x - 0.15, -2.9, x + 0.15, -2.0) for x in (-3.0, -0.4, 2.5)]
    water = hide(sea(-2.5, rows=2, gap=0.4), *piles)
    horizon = [[(-3.8, 0.9), (3.8, 0.9)]]
    sailboat = [poly((0.3, 1.1), (0.3, 2.3), (0.9, 1.1)), chain(quad((0.0, 1.05), (0.4, 0.85), (1.0, 0.95), 8), [(1.1, 1.1), (0.0, 1.1), (0.0, 1.05)])]
    sun = [arc(-0.2, 0.9, 0.6, 0, math.pi, 20)] * 0
    birds = [gull(-2.6, 2.6, 0.35), gull(2.4, 2.9, 0.3)]
    chairs = a + b
    cov = []
    out = chairs + table + glasses + dock + piles + water + hide(horizon, *[poly((-3.1, -0.5), (-0.1, -0.5), (-0.4, 1.9), (-2.8, 1.9)), poly((0.1, -0.5), (3.1, -0.5), (2.8, 1.9), (0.4, 1.9))]) + birds
    return make("Adirondack Chairs on the Dock", out)


@design("coastal_seaglass", T)
def seaglass_jar(rng):
    jar = chain([(-1.3, 1.6)], quad((-1.3, 1.4), (-1.8, 1.0), (-1.8, 0.4), 10)[1:], [(-1.8, -2.4)], quad((-1.8, -2.4), (-1.8, -2.8), (-1.4, -2.8), 6)[1:],
                [(1.4, -2.8)], quad((1.4, -2.8), (1.8, -2.8), (1.8, -2.4), 6)[1:], [(1.8, 0.4)], quad((1.8, 0.4), (1.8, 1.0), (1.3, 1.4), 10)[1:], [(1.3, 1.6)])
    lid = [rrect(-1.45, 1.6, 1.45, 2.3, 0.1), [(-1.45, 1.8), (1.45, 1.8)]]
    twine = [[(-1.35, 1.5), (1.35, 1.5)], lens((0.3, 1.45), (0.95, 1.9), 0.4), lens((0.3, 1.45), (0.95, 1.0), 0.4), [(0.3, 1.45), (0.5, 0.7)], [(0.3, 1.45), (0.0, 0.8)]]
    pieces = []
    import random as _r
    R = _r.Random(7)
    cov = []
    for x, y in [(-1.2, -2.3), (-0.4, -2.35), (0.5, -2.3), (1.25, -2.25), (-0.85, -1.65), (0.05, -1.6), (0.9, -1.6), (-1.3, -0.95), (-0.45, -0.95),
                 (0.4, -0.95), (1.25, -0.9), (-0.9, -0.3), (0.0, -0.3), (0.85, -0.25), (-0.4, 0.3), (0.5, 0.3)]:
        pts = [(x + (0.32 + 0.08 * R.random()) * math.cos(a), y + (0.26 + 0.06 * R.random()) * math.sin(a)) for a in [k * TAU / 6 + R.random() * 0.4 for k in range(6)]]
        pieces.append(spline(pts, True, 6))
    loose = []
    for x, y in [(-2.8, -2.6), (2.6, -2.5), (3.0, -1.9)]:
        pts = [(x + (0.38 + 0.1 * R.random()) * math.cos(a), y + (0.28 + 0.05 * R.random()) * math.sin(a)) for a in [k * TAU / 6 + R.random() * 0.4 for k in range(6)]]
        loose.append(spline(pts, True, 6))
    shine = [[(-1.5, -1.8), (-1.5, 0.2)]]
    table = [[(-3.6, -2.8), (3.6, -2.8)]]
    return make("Jar of Sea Glass", layered((twine, twine[1:3]), (lid, lid[:1]), ([jar] + shine, []), (pieces, pieces)) + loose + table)


def rope_ring(cx, cy, r, w=0.28):
    return [circle(cx, cy, r + w / 2, 60), circle(cx, cy, r - w / 2, 50)] + \
        [[(cx + (r - w / 2) * math.cos(a), cy + (r - w / 2) * math.sin(a)), (cx + (r + w / 2) * math.cos(a + 0.25), cy + (r + w / 2) * math.sin(a + 0.25))]
         for a in [k * TAU / 14 for k in range(14)]]


@design("coastal_knot_board", T)
def knot_board(rng):
    board = rect(-3.2, -3.0, 3.2, 2.6)
    board_in = rect(-2.9, -2.7, 2.9, 2.3)
    hanger = [[(-2.0, 2.6), (0, 3.4), (2.0, 2.6)], circle(0, 3.45, 0.1, 8)]
    out = [board, board_in] + hanger
    # monkey's fist
    mf = circle(-1.5, 1.0, 0.7, 50)
    wraps = keep([[(-2.5, y), (-0.5, y)] for y in (0.75, 1.0, 1.25)], mf) + keep([[(x, 0.0), (x, 2.0)] for x in (-1.75, -1.25)], mf)
    wraps = hide(wraps, rect(-1.85, 0.6, -1.15, 1.4))
    tail1 = tube([(-1.5, 0.3), (-1.4, -0.1), (-1.7, -0.5)], 0.22)
    out += [mf] + wraps + hide([tail1], mf)
    # figure-eight knot
    pts = [(1.5 + 0.7 * math.sin(t), 1.0 + 0.9 * math.sin(t) * math.cos(t) * 1.4) for t in [TAU * i / 80 for i in range(81)]]
    pts = [(1.5 + 0.55 * math.sin(2 * t), 1.0 + 0.85 * math.sin(t)) for t in [TAU * i / 80 for i in range(81)]]
    half1 = tube(pts[:41], 0.24)
    half2 = tube(pts[40:], 0.24)
    out += layered(([half1], [half1]), ([half2], [half2]))
    out += [tube([(1.5, 0.15), (1.5, -0.4)], 0.22)]
    # coil
    out += [spiral(-1.5, -1.6, 0.15, 0.85, 3.0, 160)]
    # loop with tails (bowline-ish)
    ring = rope_ring(1.5, -1.5, 0.55)
    tails = [tube([(1.5, -2.05), (1.4, -2.5)], 0.22), tube([(1.95, -1.85), (2.4, -2.35)], 0.22)]
    out += hide(tails, circle(1.5, -1.5, 0.69, 40)) + ring
    return make("Sailor's Knot Board", out)


def trap(x0, y0, w, h):
    box = rect(x0, y0, x0 + w, y0 + h)
    grid = keep([[(x0 + w * k / 6, y0), (x0 + w * k / 6, y0 + h)] for k in range(1, 6)] + [[(x0, y0 + h * k / 3), (x0 + w, y0 + h * k / 3)] for k in range(1, 3)], box)
    runners = [rect(x0 - 0.05, y0 - 0.12, x0 + w + 0.05, y0)]
    funnel = ellipse(x0 + w / 2, y0 + h / 2, 0.3, 0.22, 16)
    return [box] + hide(grid, funnel) + [funnel] + runners, [box, runners[0]]


@design("coastal_lobster_traps", T)
def lobster_traps(rng):
    groups = []
    for x0, y0 in [(-3.2, -2.6), (-1.1, -2.6), (1.0, -2.6), (-2.2, -1.25), (-0.1, -1.25), (-1.2, 0.1)]:
        groups.append(trap(x0, y0, 2.0, 1.2))
    out = layered(*groups[::-1])
    buoy1, _ = buoy(2.7, 0.6, 1.4, 0.6)
    rope = [cubic((2.7, 0.85), (2.4, 1.8), (1.4, 2.1), (0.8, 1.3), 16)]
    coil = [ellipse(2.7, -2.4, 0.7, 0.25, 30), ellipse(2.7, -2.25, 0.6, 0.2, 30), ellipse(2.7, -2.1, 0.5, 0.16, 30)]
    ground = [[(-3.6, -2.75), (3.7, -2.75)]]
    gull_ = [gull(-2.6, 2.2, 0.4), gull(2.0, 2.8, 0.3)]
    return make("Stacked Lobster Traps", out + buoy1 + rope + coil + ground + gull_)


def buoy(cx, top, L=1.2, w=0.42):
    shape = spline([(cx, top), (cx + w / 2, top - 0.15), (cx + w / 2 + 0.03, top - 0.7 * L), (cx, top - L, 1), (cx - w / 2 - 0.03, top - 0.7 * L), (cx - w / 2, top - 0.15)])
    bands = keep([[(cx - 1, top - 0.35 * L), (cx + 1, top - 0.35 * L)], [(cx - 1, top - 0.6 * L), (cx + 1, top - 0.6 * L)]], shape)
    return [shape, [(cx, top), (cx, top + 0.25)]] + bands, [shape]


@design("coastal_buoy_shack", T)
def buoy_shack(rng):
    hs, hc = house(-2.4, 2.4, -2.4, 2.6, 1.3, door_x=None, wins=[], overhang=0.25)
    boards = keep([[(x, -2.4), (x, 0.2)] for x in [-2.4 + 0.6 * k for k in range(1, 8)]], rect(-2.4, -2.4, 2.4, 0.2))
    door = rect(-0.5, -2.4, 0.5, -0.8)
    win = [rect(1.0, -1.0, 1.9, -0.3), [(1.45, -1.0), (1.45, -0.3)]]
    hang_line = [[(-2.4, -0.05), (2.4, -0.05)]]
    bys, bcs = [], []
    for x, L in [(-2.0, 1.1), (-1.4, 1.3), (-0.85, 1.0), (0.8, 1.2), (1.4, 1.0), (2.0, 1.25)]:
        s, c = buoy(x, -0.3, L, 0.42)
        bys.append((s, c))
    front = layered(*bys)
    bcov = [c for _, cc in bys for c in cc]
    oar = [tube([(-3.2, -2.4), (-2.7, 0.6)], 0.16), lens((-3.3, -2.6), (-3.05, -1.7), 0.4)]
    out = layered((front, bcov), ([door] + win + hang_line, [door]), (hs + boards, hc))
    out = hide(out, *[]) + oar
    ground = [[(-3.8, -2.4), (3.8, -2.4)]]
    return make("Buoys Hanging on a Fishing Shack", out + ground)


def oats(x, y, h, lean=0.3):
    stem = quad((x, y), (x + lean * 0.3, y + 0.6 * h), (x + lean, y + h), 8)
    head = lens((x + lean * 0.85, y + h * 0.75), (x + lean * 1.1, y + h * 1.15), 0.3)
    return [stem, head]


@design("coastal_dunes", T)
def dunes(rng):
    d1 = chain(quad((-3.8, -0.4), (-1.8, 1.2), (0.2, -0.6), 30), quad((0.2, -0.6), (2.0, 0.8), (3.8, -0.2), 30))
    d2 = quad((-3.8, -1.6), (-0.4, -0.2), (3.8, -1.4), 30)
    fence_ = []
    for k in range(9):
        x = -3.2 + 0.8 * k
        y = -2.0 + 0.12 * math.sin(k)
        fence_.append([(x, y - 0.3), (x + 0.05, y + 0.9)])
    wire = [quad((-3.2, -1.95), (0, -1.75), (3.2, -1.95), 20), quad((-3.15, -1.45), (0, -1.25), (3.25, -1.45), 20)]
    wire = [[(x, -2.0 + 0.12 * math.sin(k) + dy) for k, x in enumerate([-3.2 + 0.8 * k for k in range(9)])] for dy in (0.1, 0.6)]
    grass = []
    for x, y, h, l in [(-2.8, 0.3, 1.0, 0.3), (-2.5, 0.4, 1.2, -0.2), (-2.2, 0.3, 0.9, 0.4), (1.3, 0.1, 1.0, 0.3), (1.6, 0.2, 1.2, -0.25),
                       (1.9, 0.1, 0.9, 0.35), (-0.6, -0.9, 1.0, -0.3), (-0.3, -0.85, 1.2, 0.25), (2.7, -1.2, 0.9, 0.3)]:
        grass += oats(x, y, h, l)
    sea_ = [wave(-3.8, 3.8, 2.0, 0.05, 6, 120), wave(-3.5, 3.5, 2.5, 0.05, 5, 100)]
    sea_ = hide(sea_, chain(d1, [(3.8, -3), (-3.8, -3)]))
    sun = [circle(2.4, 3.2, 0.45, 30)]
    tracks = [ellipse(x, -2.7 + 0.05 * k, 0.12, 0.07, 8) for k, x in enumerate((-2.5, -2.1, -1.7, -1.3))]
    out = [d1, d2] + hide(grass, *[]) + fence_ + wire + sea_ + sun + tracks
    return make("Sand Dunes with Sea Oats and Fence", out)


@design("coastal_sea_arch", T)
def sea_arch(rng):
    arch_ = spline([(-3.6, -1.8, 1), (-3.4, 0.5), (-2.9, 1.8), (-1.8, 2.4), (0.0, 2.5), (1.4, 2.2), (2.2, 1.2), (2.4, -1.8, 1), (1.4, -1.8, 1),
                    (1.3, -0.2), (0.6, 0.8), (-0.6, 0.9), (-1.4, 0.3), (-1.7, -1.8, 1)])
    strata = keep([quad((-4, y), (0, y + 0.25), (3, y - 0.1), 14) for y in (0.2, 1.0, 1.7)] + [[(-2.6, -1.8), (-2.4, 1.2)], [(1.9, -1.8), (1.8, 0.9)]], arch_)
    hole = [poly((-1.5, -1.8), (-1.6, 0.2), (-0.6, 0.8), closed=False)]
    stack = spline([(2.9, -1.8, 1), (2.8, -0.4), (3.1, 0.3), (3.5, 0.1), (3.6, -1.8, 1)])
    grass = [zigzag(-2.6, 1.0, 2.5, 0.08, 10)]
    water = [wave(-3.8, 3.8, -1.8, 0.07, 7, 160), wave(-3.4, 3.4, -2.3, 0.07, 6, 140), wave(-3.0, 3.0, -2.8, 0.07, 5, 120)]
    sea_in = keep([wave(-1.6, 1.4, -1.0, 0.05, 2, 40)], arch_) * 0
    sun = [circle(0.0, -0.1, 0.55, 30)]
    sun = keep(sun, chain(arch_)) * 0
    birds = [gull(-2.0, 3.2, 0.35), gull(-1.2, 3.6, 0.3), gull(2.6, 3.0, 0.3)]
    horizon = [[(-1.55, -0.6), (1.35, -0.6)]]
    return make("Natural Sea Arch", [arch_, stack] + strata + grass + water + birds + horizon)


@design("coastal_sea_stacks", T)
def sea_stacks(rng):
    sun = circle(0.4, 0.6, 1.2, 80)
    rays = [[(0.4 + 1.5 * math.cos(a), 0.6 + 1.5 * math.sin(a)), (0.4 + 2.1 * math.cos(a), 0.6 + 2.1 * math.sin(a))] for a in [0.2 + k * 0.39 for k in range(8)]]
    stacks = []
    for pts in [[(-3.4, -0.9, 1), (-3.3, 0.9), (-2.9, 1.9), (-2.4, 1.6), (-2.1, 0.4), (-2.0, -0.9, 1)],
                [(-1.3, -0.9, 1), (-1.2, 0.3), (-0.9, 0.9), (-0.5, 0.6), (-0.4, -0.9, 1)],
                [(1.4, -0.9, 1), (1.5, 1.1), (1.9, 2.3), (2.5, 2.4), (2.8, 1.2), (2.9, -0.9, 1)],
                [(3.2, -0.9, 1), (3.3, 0.0), (3.6, 0.3), (3.8, -0.9, 1)]]:
        stacks.append(spline(pts, True, 10))
    cracks = keep([quad((-3.0, 1.3), (-2.7, 0.6), (-2.9, -0.2), 8), quad((2.0, 1.9), (2.3, 0.9), (2.1, -0.4), 8), [(1.5, 0.6), (2.85, 0.5)]], *stacks)
    tufts = [zigzag(-3.0, -2.5, 1.85, 0.06, 3), zigzag(1.9, 2.5, 2.37, 0.06, 3)]
    horizon = [[(-3.8, -0.9), (3.8, -0.9)]]
    water = [wave(-3.6, 3.6, -1.5, 0.06, 6, 140), wave(-3.2, 3.2, -2.1, 0.06, 5, 120), wave(-2.8, 2.8, -2.7, 0.06, 4, 100)]
    refl = [[(0.4 - w, y), (0.4 + w, y)] for w, y in [(0.9, -1.2), (0.6, -1.8), (0.35, -2.4)]]
    out = layered((stacks + cracks + tufts, stacks), (sun_s := [sun] + rays, []), (horizon + water + refl, []))
    return make("Sea Stacks at Sunset", out + [gull(-1.0, 2.8, 0.35), gull(-0.3, 3.2, 0.3)])


def shorebird(x, y, s=1.0, bill=0.7, leg=0.8, flip=False, wing=True):
    """Small wading bird facing right, feet at (x, y)."""
    body = spline([(0.55, 1.55), (0.85, 1.6), (1.0, 1.45, 1), (0.85, 1.3), (0.7, 1.15), (0.55, 0.85), (0.1, 0.65), (-0.6, 0.9), (-1.0, 1.15, 1),
                   (-0.6, 1.2), (0.0, 1.35), (0.3, 1.5)])
    beak = poly((0.98, 1.47), (1.0 + bill, 1.38 - 0.1 * bill), (0.92, 1.36), closed=False)
    w = [lens((-0.55, 1.05), (0.35, 0.95), 0.25)] if wing else []
    legs = [[(0.0, 0.67), (0.05, 0.67 - leg)], [(0.15, 0.68), (0.25, 0.68 - leg)]]
    toes = [[(0.05 - 0.15, 0.67 - leg), (0.05 + 0.2, 0.67 - leg)], [(0.25 - 0.1, 0.68 - leg), (0.25 + 0.25, 0.68 - leg)]]
    parts = [body, beak] + w + legs + toes
    return tf(parts, x, y - (0.67 - leg) * s * 0, s, flip=flip), (x + (0.75 if not flip else -0.75) * s, y + 1.45 * s)


@design("coastal_sandpipers", T)
def sandpipers(rng):
    birds, eyes_ = [], []
    bc = []
    for x, y, s, f in [(-2.6, -1.3, 1.0, False), (0.0, -1.6, 1.0, False), (2.7, -1.2, 1.0, True)]:
        b, e = shorebird(x, y, s, 0.55, 0.65, f)
        birds += b
        bc.append(b[0])
        eyes_.append(eye(e[0], e[1], 0.07))
    surf = [chain(*[arc(-3.6 + 0.6 * k + 0.3, 1.9, 0.3, math.pi, 0, 8) for k in range(12)])]
    surf = [wave(-3.8, 3.8, 1.9, 0.12, 9, 200), wave(-3.8, 3.8, 2.5, 0.08, 7, 160), chain(*[arc(-3.8 + 0.76 * k + 0.38, 1.1, 0.38, math.pi, 0, 8) for k in range(10)])]
    prints = [poly((x - 0.12, y + 0.15), (x, y), (x + 0.12, y + 0.15), closed=False) for x, y in [(-1.2, -2.6), (-0.7, -2.85), (-0.2, -2.6), (0.3, -2.85), (0.8, -2.6)]]
    shells = [chain(arc(2.6, -2.8, 0.3, 0, math.pi, 10), [(2.3, -2.8)]), circle(-2.8, -2.7, 0.15, 10)]
    refl = [[(x - 0.5, y - 0.2), (x + 0.5, y - 0.2)] for x, y in [(-2.6, -1.3), (0.0, -1.6), (2.7, -1.2)]]
    return make("Sandpipers at the Surf Edge", birds + surf + prints + shells + refl, eyes_)


@design("coastal_oystercatcher", T)
def oystercatcher(rng):
    body = spline([(0.5, 1.7), (0.95, 1.75), (1.15, 1.55, 1), (1.0, 1.3), (0.8, 1.0), (0.7, 0.4), (0.2, -0.1), (-0.8, -0.1), (-1.8, 0.4), (-2.3, 0.6, 1),
                   (-1.6, 0.8), (-0.6, 1.0), (0.0, 1.3), (0.3, 1.6)])
    bill = poly((1.13, 1.58), (2.6, 1.25), (1.12, 1.4), closed=False)
    bib = quad((0.95, 1.2), (0.4, 0.8), (0.3, 0.2), 10)
    wing = spline([(-0.2, 0.9), (-1.0, 0.7), (-2.0, 0.55), (-1.0, 0.35), (0.0, 0.4), (0.3, 0.6)])
    wing_bar = [quad((-1.6, 0.5), (-0.8, 0.5), (0.1, 0.55), 10)]
    legs = [[(-0.1, -0.08), (-0.15, -0.9)], [(0.2, -0.08), (0.3, -0.9)]]
    toes = [[(-0.4, -0.95), (-0.15, -0.9), (0.1, -0.98)], [(0.05, -0.95), (0.3, -0.9), (0.6, -0.95)]]
    rk, rc = rock_pile([(0.0, -1.6, 1.8, 0.75, 0.3), (-2.5, -2.1, 1.1, 0.6, 1.2), (2.4, -2.0, 1.2, 0.65, 2.4)])
    mussels = [lens((1.2, -1.0), (1.8, -1.2), 0.3), lens((-1.6, -1.1), (-1.0, -1.0), 0.3)]
    water = hide(sea(-2.3, rows=2, gap=0.45), *rc)
    out = layered(([body, bill, bib, wing] + wing_bar, [body]), (legs + toes, []), (mussels, mussels), (rk, rc), (water, []))
    return make("Oystercatcher on the Rocks", out, [eye(0.8, 1.52, 0.1)])


@design("coastal_cypress", T)
def cypress(rng):
    trunk = tube(spline([(0.6, -1.5), (0.4, -0.6), (-0.1, 0.2), (0.0, 0.9), (-0.5, 1.6)], closed=False, n=10), lambda t: 0.6 - 0.4 * t)
    br1 = tube(spline([(-0.05, 0.3), (-1.0, 0.8), (-2.2, 0.9)], closed=False, n=10), lambda t: 0.3 - 0.2 * t)
    br2 = tube(spline([(0.0, 0.8), (1.0, 1.3), (2.1, 1.5)], closed=False, n=10), lambda t: 0.28 - 0.18 * t)
    canopies = [ellipse(-2.4, 1.15, 1.1, 0.45, 40), ellipse(-0.6, 2.0, 1.4, 0.55, 50), ellipse(2.2, 1.75, 1.0, 0.45, 40), ellipse(0.9, 2.5, 1.0, 0.4, 40)]
    can = []
    for c in canopies:
        can.append(polar(lambda t: 1.0, n=4))
    blobs = []
    for cx, cy, rx, ry in [(-2.4, 1.15, 1.1, 0.45), (-0.6, 2.0, 1.4, 0.55), (2.2, 1.75, 1.0, 0.45), (0.9, 2.55, 1.0, 0.4)]:
        blobs.append([(cx + rx * (1 + 0.06 * math.sin(9 * t)) * math.cos(t), cy + ry * (1 + 0.1 * math.sin(9 * t)) * math.sin(t)) for t in [TAU * i / 120 for i in range(121)]])
    tex = []
    for cx, cy, rx, ry in [(-2.4, 1.15, 1.1, 0.45), (-0.6, 2.0, 1.4, 0.55), (2.2, 1.75, 1.0, 0.45), (0.9, 2.55, 1.0, 0.4)]:
        tex.append(quad((cx - 0.6 * rx, cy - 0.1), (cx, cy + 0.2), (cx + 0.6 * rx, cy - 0.1), 10))
    point = spline([(-3.8, -1.3), (-2.6, -1.1), (-1.0, -1.4), (0.2, -1.6), (1.4, -1.3), (2.4, -1.7), (3.0, -2.4), (3.0, -2.4, 1), (-3.8, -2.4, 1)])
    cracks = keep([quad((-2.6, -1.2), (-2.4, -1.8), (-2.7, -2.3), 8), quad((1.6, -1.4), (1.9, -1.9), (1.7, -2.4), 8)], point)
    water = [wave(-3.8, 3.8, -2.6, 0.07, 7, 160), wave(-3.4, 3.4, -3.1, 0.07, 6, 140), wave(2.0, 3.8, -1.9, 0.07, 2, 40)]
    out = layered((blobs + tex, blobs), (hide([trunk], *[]) + [br1, br2], [trunk, br1, br2]), ([point] + cracks, [point]), (water, []))
    return make("Lone Cypress on a Rocky Point", out + [gull(2.6, 3.2, 0.35)])


def rose5(cx, cy, r, rot=0.0):
    pet = [circle(cx + 0.55 * r * math.cos(rot + k * TAU / 5), cy + 0.55 * r * math.sin(rot + k * TAU / 5), 0.5 * r, 20) for k in range(5)]
    sh = union(*pet)
    c = circle(cx, cy, 0.25 * r, 14)
    dots = [[(cx + 0.25 * r * math.cos(a), cy + 0.25 * r * math.sin(a)), (cx + 0.42 * r * math.cos(a), cy + 0.42 * r * math.sin(a))] for a in [k * TAU / 7 for k in range(7)]]
    return hide(sh, c) + [c] + dots, pet


@design("coastal_beach_roses", T)
def beach_roses(rng):
    out, cov = [], []
    for x, y, r, rot in [(-1.4, 0.9, 0.8, 0.2), (0.6, 1.5, 0.75, 0.9), (1.9, 0.3, 0.7, 0.4), (-0.4, -0.2, 0.7, 1.3), (-2.5, -0.4, 0.6, 0.0)]:
        s_, c_ = rose5(x, y, r, rot)
        out += hide(s_, *cov)
        cov += c_
    flowers_xy = [(-1.4, 0.9), (0.6, 1.5), (1.9, 0.3), (-0.4, -0.2), (-2.5, -0.4)]
    hips_xy = [(1.4, 2.6), (2.9, 1.3), (-2.7, 1.3)]
    hips = [circle(x, y, 0.2, 14) for x, y in hips_xy]
    sepals = [poly((x - 0.15, y + 0.15), (x, y + 0.35), (x + 0.15, y + 0.15), closed=False) for x, y in hips_xy]
    stems, leaves = [], []
    bases = [(-0.8, -2.0), (0.2, -2.0), (0.6, -2.0), (-0.2, -2.0), (-1.2, -2.0), (0.4, -2.0), (1.0, -2.0), (-1.6, -2.0)]
    for (x1, y1), (x0, y0) in zip(flowers_xy + hips_xy, bases):
        st = quad((x0, y0), ((x0 + x1) / 2 + 0.3, (y0 + y1) / 2), (x1, y1), 12)
        stems.append(st)
        mx, my = st[6]
        sg = 1 if x1 > x0 else -1
        leaves += [lens((mx, my), (mx + sg * 0.7, my + 0.35), 0.3), [(mx, my), (mx + sg * 0.5, my + 0.25)]]
    dune = [quad((-3.8, -2.0), (0, -1.4), (3.8, -2.2), 30)]
    fence_ = [[(x, -2.9), (x, -1.9 + 0.0)] for x in (-3.2, -2.2)] + [[(-3.4, -2.2), (-2.0, -2.15)]]
    front = out + hips + sepals
    lv_cov = [l for l in leaves if len(l) > 3]
    out2 = layered((front, cov + hips), (leaves, lv_cov), (stems, []))
    out2 += hide(dune + fence_, *cov, *lv_cov) if False else hide(dune + fence_, *[])
    return make("Beach Roses on the Dunes", out2 + [wave(-3.8, 3.8, 3.3, 0.05, 6, 100)])


def flag(x, y, w, h, kind):
    o = rect(x, y - h, x + w, y)
    if kind == "cross":
        d = [rect(x + w * 0.4, y - h, x + w * 0.6, y), [(x, y - h * 0.4), (x + w * 0.4, y - h * 0.4)], [(x + w * 0.6, y - h * 0.4), (x + w, y - h * 0.4)],
             [(x, y - h * 0.6), (x + w * 0.4, y - h * 0.6)], [(x + w * 0.6, y - h * 0.6), (x + w, y - h * 0.6)]]
    elif kind == "diag":
        d = [[(x, y), (x + w, y - h)]]
    elif kind == "quarters":
        d = [[(x + w / 2, y), (x + w / 2, y - h)], [(x, y - h / 2), (x + w, y - h / 2)]]
    elif kind == "border":
        d = [rect(x + w * 0.25, y - h * 0.75, x + w * 0.75, y - h * 0.25)]
    elif kind == "stripes":
        d = [[(x, y - h * f), (x + w, y - h * f)] for f in (0.33, 0.66)]
    elif kind == "vert":
        d = [[(x + w * f, y), (x + w * f, y - h)] for f in (0.33, 0.66)]
    elif kind == "swallow":
        o = poly((x, y), (x + w, y), (x + 0.6 * w, y - h / 2), (x + w, y - h), (x, y - h))
        d = [[(x + w * 0.4, y), (x + w * 0.4, y - h)]]
    elif kind == "dot":
        d = [circle(x + w / 2, y - h / 2, 0.22 * w, 16)]
    else:
        d = [poly((x, y), (x + w, y - h / 2), (x, y - h), closed=False)]
    return [o] + d


@design("coastal_signal_flags", T)
def signal_flags(rng):
    mast_l = [[(-3.4, -2.6), (-3.4, 2.6)], circle(-3.4, 2.72, 0.12, 10)]
    mast_r = [[(3.4, -2.6), (3.4, 2.6)], circle(3.4, 2.72, 0.12, 10)]
    out = mast_l + mast_r
    rope = quad((-3.4, 2.5), (0, -0.4), (3.4, 2.5), 60)
    out.append(rope)
    kinds = ["cross", "diag", "quarters", "border", "stripes", "dot", "vert"]
    for k, kind in enumerate(kinds):
        t = (k + 0.5) / 7
        x = -3.4 + 6.8 * t
        y = (1 - t) ** 2 * 2.5 + 2 * (1 - t) * t * -0.4 + t * t * 2.5
        out += flag(x - 0.42, y, 0.84, 0.84, kind)
    for k, kind in enumerate(["swallow", "tri", "cross", "stripes"]):
        x = -2.4 + 1.6 * k
        out += [[(x + 0.4, -0.2), (x + 0.4, 0.15)]] if False else []
    dock = [[(-3.8, -2.6), (3.8, -2.6)], [(-3.8, -2.95), (3.8, -2.95)]] + [[(x, -2.6), (x, -2.95)] for x in (-2.0, 0.0, 2.0)]
    water = sea(-1.3, rows=2, gap=0.45)
    water = hide(water, *[rect(-3.5, -3, -3.3, 3), rect(3.3, -3, 3.5, 3)])
    boat = [chain(quad((-1.6, -1.2), (-1.2, -2.2), (1.4, -2.1), 12), [(1.9, -1.2), (-1.6, -1.2)]), rect(-0.6, -1.2, 0.6, -0.7), circle(-1.0, -1.5, 0.1, 8), circle(0.9, -1.5, 0.1, 8)]
    return make("Line of Nautical Signal Flags", out + dock + hide(water, boat[0]) + boat + [gull(-1.4, 3.0, 0.4), gull(1.2, 3.3, 0.3)])


@design("coastal_village", T)
def village(rng):
    hill = chain(quad((-3.8, 1.6), (-1.5, 2.6), (0.6, 1.4), 20), quad((0.6, 1.4), (2.2, 0.6), (3.8, 0.4), 20))
    groups = []
    for x0, y0, w, wh, rh, ch in [(-3.4, 0.6, 1.1, 0.8, 0.6, True), (-2.0, 0.9, 1.0, 0.7, 0.55, False), (-0.7, 0.4, 1.2, 0.9, 0.6, True),
                                  (0.8, 0.1, 1.0, 0.7, 0.5, False), (-2.8, -0.6, 1.2, 0.9, 0.65, False), (-1.3, -0.7, 1.1, 0.8, 0.6, True),
                                  (0.2, -0.9, 1.1, 0.8, 0.55, False)]:
        wins = [(x0 + 0.3, y0 + 0.45), (x0 + w - 0.3, y0 + 0.45)] if w > 1.05 else [(x0 + w / 2, y0 + 0.45)]
        hs, hc = house(x0, x0 + w, y0, wh, rh, wins=[(x, y) for x, y in wins], chimney=(x0 + w * 0.7) if ch else None, overhang=0.1)
        groups.append((hs, hc))
    houses = layered(*groups[::-1][::-1][4:], *groups[:4]) if False else layered(*(groups[4:] + groups[:4]))
    wall = poly((-3.8, -1.6), (1.6, -1.6), (1.6, -1.0), (-3.8, -1.0))
    wall_d = keep([[(x, -1.6), (x, -1.0)] for x in (-3.0, -2.0, -1.0, 0.0, 1.0)], wall)
    quay_pier = poly((1.6, -1.6), (3.8, -1.2), (3.8, -0.9), (1.6, -1.0))
    lh, lc, ly = lighthouse(3.3, -0.9, 1.6, 0.5, 0.35, bands=(0.5,), door=False)
    boats = []
    for bx, by in [(-2.4, -2.3), (0.4, -2.6)]:
        boats += [chain(quad((bx - 0.9, by + 0.4), (bx - 0.6, by), (bx + 0.6, by), 8), [(bx + 0.9, by + 0.4), (bx - 0.9, by + 0.4)]), rect(bx - 0.2, by + 0.4, bx + 0.3, by + 0.75), [(bx + 0.5, by + 0.4), (bx + 0.5, by + 1.3)]]
    water = hide([wave(-3.8, 3.8, -2.0 - 0.5 * k, 0.05, 6, 120) for k in range(2)], *[b for b in boats[::3]])
    out = layered((lh, lc), (boats, boats[::3]), ([wall] + wall_d + [quay_pier], [wall, quay_pier]), (houses, [c for g in groups for c in g[1]]), ([hill], []), (water, []))
    return make("Fishing Village on the Hillside", out)


@design("coastal_chapel", T)
def chapel(rng):
    nave = rect(-1.6, -0.8, 1.4, 0.8)
    nroof = poly((-1.8, 0.8), (1.6, 0.8), (1.0, 1.7), (-1.2, 1.7))
    tower = rect(-2.6, -0.8, -1.6, 1.6)
    belfry = [rect(-2.6, 1.6, -1.6, 2.4), chain([(-2.35, 1.75), (-2.35, 2.05)], arc(-2.1, 2.05, 0.25, math.pi, 0, 8), [(-1.85, 1.75)])]
    spire = poly((-2.75, 2.4), (-1.45, 2.4), (-2.1, 3.9))
    cross_ = [[(-2.1, 3.9), (-2.1, 4.35)], [(-2.3, 4.15), (-1.9, 4.15)]]
    door = [chain([(-2.35, -0.8), (-2.35, 0.0)], arc(-2.1, 0.0, 0.25, math.pi, 0, 10), [(-1.85, -0.8)])]
    wins = [chain([(x - 0.18, -0.2), (x - 0.18, 0.25)], arc(x, 0.25, 0.18, math.pi, 0, 8), [(x + 0.18, -0.2), (x - 0.18, -0.2)]) for x in (-0.9, 0.0, 0.9)]
    bluff = chain([(-3.8, -0.8)], [(1.8, -0.8)], quad((2.3, -0.8), (2.5, -1.4), (2.2, -2.0), 8), quad((2.2, -2.0), (2.9, -2.4), (2.7, -3.0), 8))
    grass = [zigzag(-3.8, 1.8, -0.75, 0.07, 18)]
    fence_ = [[(x, -0.8), (x, -0.35)] for x in (-3.6, -3.2, 1.7)] + [[(-3.7, -0.5), (-3.0, -0.5)]]
    stones = [chain([(x - 0.15, -1.3), (x - 0.15, -1.05)], arc(x, -1.05, 0.15, math.pi, 0, 6), [(x + 0.15, -1.3)]) for x in (-3.0, -0.5)] * 0
    water = sea(-2.2, x0=2.6, rows=2, gap=0.45) + [wave(1.0, 3.8, -1.3, 0.05, 2, 40)]
    water = [wave(2.9, 3.8, -2.0, 0.05, 1, 20), wave(3.0, 3.8, -2.5, 0.05, 1, 20)]
    path = [quad((-2.35, -0.8), (-2.7, -1.6), (-3.2, -2.6), 8), quad((-1.85, -0.8), (-2.0, -1.6), (-2.2, -2.6), 8)]
    out = layered((cross_ + [spire], [spire]), (belfry, belfry[:1]), ([tower] + door, [tower]), ([nroof], [nroof]), ([nave] + wins, [nave]), ([bluff] + grass + fence_ + water + path, []))
    return make("Seaside Chapel on the Bluff", out + [gull(0.6, 3.0, 0.4), gull(1.6, 3.5, 0.3), gull(2.6, 2.6, 0.35)])


@design("coastal_whale_vane", T)
def whale_vane(rng):
    whale = spline([(2.6, 1.3), (2.4, 1.9), (1.5, 2.2), (0.0, 2.1), (-1.4, 1.75), (-2.3, 1.95), (-2.9, 2.45, 1), (-2.65, 1.75), (-3.0, 1.15, 1),
                    (-2.2, 1.45), (-1.2, 1.15), (0.3, 0.85), (1.6, 0.85), (2.3, 1.0)])
    mouth = [quad((2.55, 1.35), (2.0, 1.1), (1.5, 1.15), 8)]
    fin = poly((0.6, 0.9), (0.3, 0.45), (1.1, 0.88))
    grooves = keep([[(x, 0.8), (x + 0.6, 1.1)] for x in (1.3, 1.6, 1.9)], whale)
    rod = [[(0, 0.88), (0, -2.6)]]
    arms = [[(-1.8, -0.6), (1.8, -0.6)], [(-0.7, -0.95), (0.7, -0.25)]]
    tips = [poly((1.8, -0.45), (2.2, -0.6), (1.8, -0.75)), poly((-1.8, -0.45), (-2.2, -0.6), (-1.8, -0.75)), poly((0.7, -0.15), (1.05, -0.12), (0.8, -0.38)),
            poly((-0.7, -1.05), (-1.05, -1.08), (-0.8, -0.82))]
    ball = circle(0, -1.3, 0.25, 18)
    roof = poly((-3.4, -3.2), (0, -2.0), (3.4, -3.2), closed=False)
    cupola = [rect(-0.8, -2.6, 0.8, -1.8)] * 0
    out = layered(([whale, fin] + mouth + grooves, [whale]), (tips + [ball], tips + [ball]), (rod + arms, []), ([roof], []))
    return make("Whale Weathervane", out, [eye(1.95, 1.45, 0.09)])


def lobster(cx, cy, s=1.0):
    body = spline([(0.0, 1.0), (0.35, 0.6), (0.4, -0.2), (0.3, -0.9), (0.0, -1.0, 1), (-0.3, -0.9), (-0.4, -0.2), (-0.35, 0.6)])
    segs = keep([[(-1, y), (1, y)] for y in (-0.2, -0.45, -0.7)], body)
    tail = poly((-0.3, -0.95), (-0.5, -1.4), (0.0, -1.25), (0.5, -1.4), (0.3, -0.95))
    claws = []
    for sg in (-1, 1):
        claws.append(tube([(sg * 0.3, 0.5), (sg * 0.8, 0.9), (sg * 0.7, 1.3)], 0.15))
        claws.append(lens((sg * 0.7, 1.3), (sg * 0.75, 2.1), 0.45))
        claws.append([(sg * 0.72, 1.7), (sg * 0.73, 2.05)])
    legs = [[(sg * 0.38, y), (sg * 0.8, y - 0.25)] for sg in (-1, 1) for y in (0.3, 0.05, -0.2)]
    ant = [quad((-0.1, 1.0), (-0.6, 1.8), (-1.2, 2.2), 8), quad((0.1, 1.0), (0.6, 1.8), (1.2, 2.2), 8)]
    return tf(layered(([body, tail] + segs, [body, tail]), (claws, claws[1::3]), (legs + ant, [])), cx, cy, s)


@design("coastal_lobster_shack", T)
def lobster_shack(rng):
    hs, hc = house(-2.4, 1.6, -1.6, 1.7, 1.1, door_x=-1.6, wins=[], overhang=0.2)
    counter = [rect(-1.0, -0.6, 1.2, 0.4), [(-1.0, -0.6), (1.2, -0.6)]]
    awning = [poly((-1.2, 0.4), (1.4, 0.4), (1.6, -0.05), (-1.4, -0.05))] + [[(x, 0.4), (x + 0.04 * x, -0.05)] for x in (-0.6, 0.0, 0.6)]
    boards = keep([[(-3, y), (2, y)] for y in (-1.2, -0.8)], rect(-2.4, -1.6, 1.6, 0.1))
    sign = rrect(-2.1, 1.95, 1.3, 3.7, 0.2)
    lob = lobster(-0.4, 2.45, 0.32)
    lob = tf(lobster(0, 0, 0.62), -0.25, 2.85, 1, -math.pi / 2)
    table = [rect(1.9, -1.0, 3.6, -0.85), [(2.1, -0.85), (2.3, -1.6)], [(3.4, -0.85), (3.2, -1.6)], rect(1.8, -1.35, 3.7, -1.25)]
    umb = [chain(arc(2.75, 0.2, 1.0, 0.15, math.pi - 0.15, 20), [(1.76, 0.35), (3.74, 0.35)]), [(2.75, 0.35), (2.75, -0.85)]]
    buoys_ = []
    for x in (-2.15, 1.3):
        b, _ = buoy(x, 1.2, 0.8, 0.32)
        buoys_ += b
    ground = [[(-3.8, -1.6), (3.8, -1.6)]]
    out = layered((lob, []), ([sign], [sign]), (buoys_, []), (counter + awning, counter[:1] + awning[:1]), (hs + boards, hc), (table + umb + ground, []))
    return make("Seaside Lobster Shack", out + [[(-1.6, 1.95), (-1.3, 1.55)], [(0.8, 1.95), (0.5, 1.55)]])


@design("coastal_chowder", T)
def chowder(rng):
    rim = ellipse(0, 0.4, 2.7, 0.85, 120)
    soup = ellipse(0, 0.35, 2.35, 0.65, 110)
    body = chain(cubic((-2.7, 0.4), (-2.7, -1.4), (-1.5, -2.0), (0, -2.0), 20), cubic((0, -2.0), (1.5, -2.0), (2.7, -1.4), (2.7, 0.4), 20)[1:])
    foot = [[(-1.0, -1.95), (-1.1, -2.3), (1.1, -2.3), (1.0, -1.95)]]
    plate = ellipse(0, -2.3, 3.6, 0.7, 120)
    chunks = keep([rect(x - 0.17, y - 0.12, x + 0.17, y + 0.12) for x, y in [(-1.3, 0.4), (-0.4, 0.6), (0.6, 0.2), (1.4, 0.5), (-0.8, 0.0)]] +
                  [circle(x, y, 0.08, 8) for x, y in [(0.1, 0.65), (-1.6, 0.2), (1.0, 0.65), (0.4, -0.05)]], soup)
    clam = [chain(arc(2.9, -1.65, 0.55, 0.1, math.pi - 0.1, 16), [(2.36, -1.6), (3.44, -1.6)]), quad((2.4, -1.6), (2.9, -1.95), (3.4, -1.6), 8)]
    clam += keep([[(2.9, -1.6), (2.9 + 0.6 * math.cos(a), -1.6 + 0.6 * math.sin(a))] for a in (0.6, 1.2, 1.9, 2.5)], clam[0])
    crackers = [circle(-2.9, -1.4, 0.35, 24), circle(-2.4, -1.85, 0.35, 24)]
    crackers = layered(([crackers[1], circle(-2.4, -1.85, 0.04, 6)], [crackers[1]]), ([crackers[0], circle(-2.9, -1.4, 0.04, 6)], []))
    spoon = [tube([(0.8, 0.6), (2.3, 2.8)], lambda t: 0.22 - 0.06 * t)]
    steam = [cubic((x, 1.4), (x - 0.2, 1.8), (x + 0.2, 2.2), (x, 2.7), 12) for x in (-1.0, -0.3, 0.4)]
    bowl = layered((spoon, spoon), ([rim, soup] + chunks, [rim]), ([body] + foot, [chain(body, [body[0]])]))
    out = layered((bowl, [rim, chain(body, [body[0]])]), (clam + crackers, [clam[0]] + [circle(-2.9, -1.4, 0.35, 24), circle(-2.4, -1.85, 0.35, 24)]), ([plate], []))
    return make("Bowl of Clam Chowder", out + steam)


@design("coastal_fish_chips", T)
def fish_chips(rng):
    cone = poly((-2.0, 1.0), (2.0, 1.0), (0.0, -3.2))
    fold = [[(-2.0, 1.0), (-1.2, 0.3), (1.6, 0.6)]]
    check = keep([[(x, -3.5), (x + 1.2, 1.2)] for x in (-2.4, -1.6, -0.8, 0.0)] + [[(x, -3.5), (x - 1.2, 1.2)] for x in (0.4, 1.2, 2.0, 2.8)], cone)
    check = hide(check, poly((-2.0, 1.0), (-1.2, 0.3), (1.6, 0.6), (2.0, 1.0)))
    fish1 = spline([(-1.6, 0.9), (-1.5, 1.8), (-0.9, 2.9), (-0.4, 3.2, 1), (-0.5, 2.2), (-0.7, 0.9)])
    fish2 = spline([(0.3, 0.9), (0.6, 2.0), (1.1, 2.7), (1.5, 2.8, 1), (1.4, 1.9), (1.0, 0.9)])
    batter = keep([arc(x, y, 0.15, 0, math.pi, 6) for x, y in [(-1.2, 1.6), (-0.9, 2.2), (-1.0, 1.1), (0.9, 1.5), (1.1, 2.1), (0.7, 1.1)]], fish1, fish2)
    chips = []
    for x, a, L in [(-0.3, 0.15, 1.6), (0.0, -0.1, 1.9), (-1.9, 0.4, 1.3), (1.6, -0.35, 1.5), (0.4, 0.05, 1.3), (1.9, -0.2, 1.1)]:
        chips.append(transform(rect(-0.13, 0.0, 0.13, L), x, 0.7, 1, a))
    lemon = [ellipse(2.4, -1.6, 0.7, 0.45, 30, rot=0.4), ellipse(2.4, -1.6, 0.52, 0.31, 30, rot=0.4)]
    fork = [tube([(-2.6, -1.6), (-1.3, 1.3)], 0.14)] + [[(-1.35 + dx, 1.25), (-1.1 + dx, 1.85)] for dx in (-0.1, 0.05, 0.2)]
    fork = [tube([(-3.0, -1.2), (-2.3, 0.9)], 0.16), poly((-2.45, 0.85), (-2.15, 0.95), (-2.0, 1.5), (-2.4, 1.4), closed=False)]
    out = layered(([cone] + check + fold, [cone]), ([fish1], [fish1]), ([fish2], [fish2]), (chips, chips))
    return make("Fish and Chips in a Paper Cone", out + hide(batter, *[]))


@design("coastal_cleat", T)
def cleat(rng):
    planks = [[(-3.8, y), (3.8, y)] for y in (-2.6, -1.4, -0.2, 1.0, 2.2)]
    seams = [[(x, y0), (x, y0 + 1.2)] for x, y0 in [(-1.5, -2.6), (2.2, -1.4), (-2.8, -0.2), (0.9, 1.0), (-1.0, 2.2)]]
    nails = [circle(x, y, 0.06, 6) for x, y in [(-1.7, -2.4), (-1.3, -2.4), (2.0, -1.2), (2.4, -1.2), (-3.0, 0.0), (0.7, 1.2), (1.1, 1.2)]]
    cleat_ = spline([(-2.4, 0.15, 1), (-1.6, 0.35), (-0.6, 0.45), (0.6, 0.45), (1.6, 0.35), (2.4, 0.15, 1), (2.4, -0.15, 1), (1.6, -0.35), (0.6, -0.45),
                     (-0.6, -0.45), (-1.6, -0.35), (-2.4, -0.15, 1)])
    base = rrect(-0.9, -0.75, 0.9, 0.75, 0.25)
    bolts = [circle(x, 0.0, 0.1, 8) for x in (-0.65, 0.65)]
    coil = []
    for k in range(4):
        coil.append(ellipse(0.6, -1.7, 1.9 - 0.35 * k, 0.9 - 0.17 * k, 80))
    rope_cover = ellipse(0.6, -1.7, 1.95, 0.95, 80)
    fig8 = [tube(cubic((-1.9, -0.3), (-0.8, 0.6), (0.8, -0.6), (1.9, 0.3), 20), 0.26), tube(cubic((-1.9, 0.3), (-0.8, -0.6), (0.8, 0.6), (1.9, -0.3), 20), 0.26)]
    lead = tube(cubic((-1.9, 0.3), (-2.6, 0.6), (-3.0, -0.4), (-1.3, -1.1), 20), 0.26)
    out = layered((fig8[:1], fig8[:1]), (fig8[1:], fig8[1:]), ([lead], [lead]), ([cleat_], [cleat_]), ([base] + bolts, [base]), (coil, [rope_cover]), (planks + seams + nails, []))
    return make("Mooring Cleat with Coiled Rope", out)


@design("coastal_sea_pinks", T)
def sea_pinks(rng):
    cliff = chain([(-3.8, -0.4)], quad((-3.8, -0.4), (-1.0, -0.2), (1.0, -0.6), 12)[1:], [(2.0, -0.6)], quad((2.0, -0.6), (2.6, -1.4), (2.4, -2.0), 8)[1:],
                  quad((2.4, -2.0), (2.9, -2.6), (2.7, -3.2), 8)[1:])
    strata = [quad((-3.8, y), (-1.0, y + 0.2), (2.3, y - 0.1), 12) for y in (-1.4, -2.4)]
    flowers, cov = [], []
    for x, y, h in [(-2.8, -0.4, 1.6), (-2.2, -0.4, 2.3), (-1.4, -0.3, 1.8), (-0.6, -0.4, 2.6), (0.3, -0.45, 2.0), (1.1, -0.55, 1.5), (1.7, -0.6, 2.2)]:
        top = (x + 0.1 * math.sin(x * 3), y + h)
        head = circle(top[0], top[1], 0.38, 30)
        florets = [circle(top[0] + 0.2 * math.cos(a), top[1] + 0.2 * math.sin(a), 0.14, 10) for a in [k * TAU / 5 for k in range(5)]]
        florets = keep(florets, head) + [circle(top[0], top[1], 0.08, 8)]
        stem = quad((x, y), (x - 0.1, y + h * 0.5), (top[0], top[1] - 0.38), 8)
        flowers.append(([head] + florets, [head]))
        flowers.append(([stem], []))
    tufts = [chain(*[[(x + 0.2 * k, -0.45 + 0.02 * k), (x + 0.2 * k + 0.1, 0.0)] for k in range(5)]) for x in (-2.9, -0.9, 1.0)]
    tufts = [zigzag(-3.4, 2.0, -0.35, 0.15, 22)]
    water = [wave(2.6, 3.8, -1.5, 0.05, 1, 30), wave(2.8, 3.8, -2.2, 0.05, 1, 30), [(2.2, -0.9), (3.8, -0.9)]]
    out = layered(*flowers, (tufts, []), ([cliff] + strata + water, []))
    return make("Sea Pinks on the Cliff Edge", out + [gull(1.0, 3.0, 0.4), gull(2.2, 2.6, 0.35)])


@design("coastal_cormorant", T)
def cormorant(rng):
    body = spline([(0.2, 2.2), (0.45, 2.35), (0.75, 2.25, 1), (0.5, 2.05), (0.35, 1.6), (0.4, 0.8), (0.5, 0.0), (0.3, -0.6), (0.0, -0.9), (-0.35, -0.6),
                   (-0.45, 0.0), (-0.35, 0.8), (-0.1, 1.5), (-0.05, 2.0)])
    bill = poly((0.72, 2.26), (1.35, 2.18), (1.45, 2.05, ), (0.62, 2.1), closed=False)
    wings = []
    for sg in (-1, 1):
        w = spline([(sg * 0.3, 0.9), (sg * 1.2, 1.5), (sg * 2.2, 1.9), (sg * 3.2, 1.6, 1), (sg * 2.8, 1.2), (sg * 3.0, 0.8, 1), (sg * 2.5, 0.5), (sg * 2.6, 0.1, 1),
                    (sg * 2.0, -0.1), (sg * 1.9, -0.4, 1), (sg * 1.2, -0.1), (sg * 0.4, 0.1)], closed=False)
        feathers = [[(sg * x, y), (sg * (x + 0.3), y - 0.6)] for x, y in [(1.4, 1.3), (1.9, 1.5), (2.4, 1.6)]]
        wings += [w] + feathers
    tail = poly((-0.2, -0.85), (0.0, -1.5), (0.2, -0.85), closed=False)
    feet = [[(-0.15, -0.8), (-0.3, -1.3)], [(0.15, -0.8), (0.3, -1.3)]]
    post = [rect(-0.6, -3.2, 0.6, -1.3), ellipse(0.0, -1.3, 0.6, 0.15, 24)]
    rings = [[(-0.6, y), (0.6, y)] for y in (-2.0, -2.6)]
    water = hide(sea(-2.6, rows=2, gap=0.45), post[0])
    out = layered(([body, bill], [body]), (wings + [tail] + feet, []), (post + rings, [post[0]]), (water, []))
    return make("Cormorant Drying Its Wings", out, [eye(0.45, 2.2, 0.07)])


@design("coastal_gannet", T)
def gannet(rng):
    body = spline([(0.0, -1.6, 1), (0.25, -1.0), (0.45, 0.2), (0.5, 1.2), (0.3, 2.2), (0.6, 2.9, 1), (0.0, 2.6), (-0.6, 2.9, 1), (-0.3, 2.2), (-0.5, 1.2),
                   (-0.45, 0.2), (-0.25, -1.0)])
    head_line = quad((-0.35, -0.6), (0.0, -0.4), (0.35, -0.6), 8)
    bill = [[(0.0, -1.6), (0.0, -1.0)]]
    wings = [spline([(-0.45, 0.6), (-1.4, 1.3), (-2.0, 2.4), (-2.1, 3.1, 1), (-1.4, 2.2), (-0.5, 1.4)], closed=False),
             spline([(0.45, 0.6), (1.4, 1.3), (2.0, 2.4), (2.1, 3.1, 1), (1.4, 2.2), (0.5, 1.4)], closed=False)]
    tips = [[(-1.6, 2.2), (-2.0, 2.7)], [(1.6, 2.2), (2.0, 2.7)]]
    splash = [chain(*[[(x, -2.3), (x + 0.15 * sg, -1.7 + 0.3 * abs(x))] for x, sg in []])] * 0
    splash = [poly((-1.2, -2.3), (-1.0, -1.7), (-0.7, -2.2), (-0.5, -1.4), (-0.25, -2.0), (0.25, -2.0), (0.5, -1.4), (0.7, -2.2), (1.0, -1.7), (1.2, -2.3), closed=False)]
    rings = [ellipse(0, -2.4, r, 0.25 * r, 50) for r in (1.6, 2.4)]
    drops = [circle(x, y, 0.1, 8) for x, y in [(-1.5, -1.4), (1.5, -1.3), (-0.9, -1.0), (1.0, -0.9)]]
    water = [[(-3.6, -2.4), (-2.5, -2.4)], [(2.5, -2.4), (3.6, -2.4)]]
    others = [gull(-2.6, 0.8, 0.45), gull(2.7, 0.4, 0.4)]
    out = layered(([body, head_line] + bill, [body]), (wings + tips, []), (splash, []), (rings + drops + water + others, []))
    return make("Gannet Diving into the Sea", out, [eye(0.18, -0.85, 0.07)])


def tern(x, y, s=1.0, flip=False):
    body = spline([(0.9, 0.5), (0.6, 0.75), (0.2, 0.7), (-0.6, 0.45), (-1.5, 0.15, 1), (-1.0, 0.15), (-1.6, -0.05, 1), (-0.6, 0.05), (0.2, 0.1), (0.6, 0.3)])
    cap = quad((0.85, 0.55), (0.55, 0.85), (0.1, 0.68), 8)
    bill = poly((0.88, 0.55), (1.5, 0.42), (0.85, 0.4), closed=False)
    wing = spline([(0.2, 0.45), (-0.5, 0.45), (-1.3, 0.35, 1), (-0.4, 0.2)], closed=False)
    legs = [[(0.0, 0.1), (0.0, -0.3)], [(0.2, 0.12), (0.25, -0.3)]]
    return tf([body, cap, bill, wing] + legs, x, y, s, flip=flip)


# dropped: the subject repeats another book
def terns(rng):
    posts, out = [], []
    for x, top, s, f in [(-2.4, -0.4, 1.0, False), (0.1, 0.2, 1.1, True), (2.5, -0.9, 0.95, False)]:
        p = [rect(x - 0.35, -3.2, x + 0.35, top), ellipse(x, top, 0.35, 0.1, 20)]
        posts += p + [[(x - 0.35, top - 0.8), (x + 0.35, top - 0.8)]]
        out += tern(x, top + 0.42, s, f)
    flyer = [gull(-0.8, 2.6, 0.55), gull(1.6, 3.0, 0.45)]
    water = hide(sea(-2.4, rows=2, gap=0.45), *[p for p in posts[::3]])
    return make("Terns on Wooden Posts", out + posts + flyer + water)


@design("coastal_window_view", T)
def window_view(rng):
    frame = rect(-2.8, -1.6, 2.8, 2.8)
    frame_in = rect(-2.5, -1.3, 2.5, 2.5)
    mull = [[(0, -1.3), (0, 2.5)], [(-2.5, 0.8), (2.5, 0.8)]]
    sill = rect(-3.3, -1.95, 3.3, -1.6)
    curtains = [spline([(-3.6, 3.4, 1), (-2.2, 3.4, 1), (-2.4, 2.0), (-2.9, 0.6), (-2.6, -0.6), (-3.0, -1.6, 1), (-3.6, -1.6, 1)]),
                mirror_x(spline([(-3.6, 3.4, 1), (-2.2, 3.4, 1), (-2.4, 2.0), (-2.9, 0.6), (-2.6, -0.6), (-3.0, -1.6, 1), (-3.6, -1.6, 1)]))]
    folds = [quad((-3.2, 3.3), (-3.0, 1.0), (-3.3, -1.5), 10), quad((3.2, 3.3), (3.0, 1.0), (3.3, -1.5), 10)]
    rod = [[(-3.8, 3.45), (3.8, 3.45)], circle(-3.85, 3.45, 0.12, 8), circle(3.85, 3.45, 0.12, 8)]
    view = [[(-2.5, 0.2), (2.5, 0.2)], wave(-2.5, 2.5, -0.4, 0.05, 4, 80), wave(-2.5, 2.5, -0.9, 0.05, 4, 80)]
    lh, lc, ly = lighthouse(1.4, 0.2, 1.3, 0.45, 0.3, bands=(0.5,), door=False)
    boat = [poly((-1.4, 0.35), (-1.4, 1.5), (-0.8, 0.35)), chain(quad((-1.8, 0.3), (-1.4, 0.05), (-0.7, 0.15), 8), [(-0.6, 0.3), (-1.8, 0.3)])]
    birds = [gull(-1.6, 1.9, 0.3), gull(0.6, 2.1, 0.25)]
    scene = keep(lh + view + boat + birds + [circle(-0.9, 1.9, 0.35, 24)], frame_in)
    scene = hide(scene, *[rect(-0.06, -1.3, 0.06, 2.5), rect(-2.5, 0.74, 2.5, 0.86)])
    pot = [poly((-2.2, -1.6), (-2.1, -1.0), (-1.3, -1.0), (-1.2, -1.6)), rrect(-2.3, -1.05, -1.1, -0.85, 0.05)]
    plant = [lens((-1.7, -0.85), (-2.3, 0.0), 0.3), lens((-1.7, -0.85), (-1.1, 0.1), 0.3), lens((-1.7, -0.85), (-1.7, 0.3), 0.3)]
    binoc = [rrect(0.9, -1.6, 1.4, -0.9, 0.15), rrect(1.5, -1.6, 2.0, -0.9, 0.15), rect(1.4, -1.35, 1.5, -1.15)]
    out = layered((curtains + folds, curtains), (pot + plant + binoc, pot[:1] + plant + binoc[:2]), ([sill], [sill]), ([frame, frame_in] + mull + scene, []), (rod, []))
    return make("Seaside Window with a Sea View", out)


@design("coastal_widows_walk", T)
def widows_walk(rng):
    walls = rect(-2.4, -2.4, 2.4, 0.8)
    rf = poly((-2.8, 0.8), (2.8, 0.8), (1.6, 1.8), (-1.6, 1.8))
    walk = rect(-1.6, 1.8, 1.6, 1.95)
    rail = [[(-1.5, 1.95), (-1.5, 2.45), (1.5, 2.45), (1.5, 1.95)]] + [[(x, 1.95), (x, 2.45)] for x in (-1.0, -0.5, 0.0, 0.5, 1.0)]
    chims = [rect(-2.1, 1.0, -1.75, 2.2), rect(1.75, 1.0, 2.1, 2.2)]
    wins = []
    for x in (-1.6, -0.55, 0.55, 1.6):
        for y in (-0.15,):
            wins += [rect(x - 0.28, y - 0.45, x + 0.28, y + 0.45), [(x - 0.28, y), (x + 0.28, y)], rect(x - 0.42, y - 0.45, x - 0.3, y + 0.45), rect(x + 0.3, y - 0.45, x + 0.42, y + 0.45)]
    lower = [rect(x - 0.28, -1.95, x + 0.28, -1.05) for x in (-1.6, 1.6)] + [[(x - 0.28, -1.5), (x + 0.28, -1.5)] for x in (-1.6, 1.6)]
    door = [rect(-0.4, -2.4, 0.4, -1.0), poly((-0.55, -1.0), (0.55, -1.0), (0.0, -0.75)), circle(0.25, -1.7, 0.05, 6)]
    fan = [arc(0.0, -1.0, 0.4, 0, math.pi, 10)] * 0
    steps = [rect(-0.7, -2.65, 0.7, -2.4), rect(-0.9, -2.9, 0.9, -2.65)]
    clap = keep([[(-3, y), (3, y)] for y in (-2.0, -1.6, -1.2, -0.8, 0.4)], walls)
    clap = hide(clap, *[rect(x - 0.45, -0.65, x + 0.45, 0.35) for x in (-1.6, -0.55, 0.55, 1.6)], *[rect(x - 0.3, -2.0, x + 0.3, -1.0) for x in (-1.6, 1.6)],
                rect(-0.45, -2.4, 0.45, -0.75))
    trees = []
    lh = []
    out = layered((rail, []), ([walk], [walk]), (chims, chims), ([rf], [rf]), ([walls] + wins + lower + door + clap + steps, [walls]))
    return make("Captain's House with a Widow's Walk", out + [gull(-2.8, 2.8, 0.35), gull(2.6, 3.1, 0.3)])


@design("coastal_lifesaving", T)
def lifesaving(rng):
    hs, hc = house(-2.8, 0.6, -2.0, 1.6, 1.2, wins=[(-0.3, -0.7)], overhang=0.2)
    bay = [rect(-2.4, -2.0, -1.0, -0.8)] + [[(x, -2.0), (x, -0.8)] for x in (-2.05, -1.7, -1.35)]
    tower = rect(0.6, -2.0, 1.8, 1.6)
    troof = poly((0.4, 1.6), (2.0, 1.6), (1.2, 2.3))
    lookout = rect(0.7, 1.0, 1.7, 1.5)
    look_m = [[(1.2, 1.0), (1.2, 1.5)]]
    tw = [rect(0.95, -0.4, 1.45, 0.3), rect(0.95, -1.6, 1.45, -0.9)]
    gal = [[(0.6, 0.85), (2.1, 0.85), (2.1, 1.2)], [(2.1, 1.2), (1.8, 1.2)], [(1.95, 0.85), (1.95, 1.2)]]
    flagpole = [[(2.8, -2.0), (2.8, 2.7)], poly((2.8, 2.7), (3.6, 2.45), (2.8, 2.2), closed=False)]
    ring = [circle(-0.3, 0.5, 0.0001, 3)] * 0
    boat = [chain(quad((-3.4, -2.75), (-2.2, -3.15), (0.2, -3.0), 12), [(0.7, -2.6), (-3.6, -2.6), (-3.4, -2.75)])] + [[(x, -2.6), (x, -2.9)] for x in (-2.4, -1.4, -0.4)]
    cart = [circle(-2.6, -3.1, 0.25, 16), circle(0.0, -3.1, 0.25, 16)]
    out = layered((cart, cart), (boat, boat[:1]), ([troof, lookout] + look_m + gal, [troof, lookout]), ([tower] + tw, [tower]), (hs + bay, hc), (flagpole + [[(-3.8, -2.0), (3.8, -2.0)]], []))
    return make("Lifesaving Station with Lookout Tower", out + [gull(-1.8, 2.6, 0.35)])


@design("coastal_wind_turbines", T)
def wind_turbines(rng):
    out = []
    for cx, base, h, s, rot in [(-1.6, -0.6, 3.6, 1.0, 0.3), (1.4, 0.1, 2.6, 0.7, 1.0), (3.0, 0.4, 1.8, 0.48, 0.6)]:
        hub = (cx, base + h)
        towerp = poly((cx - 0.12 * s, base), (cx + 0.12 * s, base), (cx + 0.06 * s, base + h), (cx - 0.06 * s, base + h))
        nac = rrect(cx - 0.12 * s, base + h - 0.12 * s, cx + 0.45 * s, base + h + 0.12 * s, 0.06 * s)
        hubc = circle(cx, base + h, 0.12 * s + 0.02, 12)
        blades = [transform(spline([(0.0, 0.08), (0.6, 0.14), (1.8, 0.06), (2.0, 0.0, 1), (1.8, -0.04), (0.6, -0.06), (0.0, -0.08)]), cx, base + h, s, rot + k * TAU / 3) for k in range(3)]
        found = rect(cx - 0.3 * s, base - 0.4 * s, cx + 0.3 * s, base)
        out += layered(([hubc], [hubc]), (blades, blades), ([nac], [nac]), ([towerp, found], [towerp]))
    water = [wave(-3.8, 3.8, -0.9 - 0.5 * k, 0.06, 7 - k, 150) for k in range(4)]
    horizon = [[(-3.8, 0.1), (-1.75, 0.1)], [(-1.45, 0.1), (1.2, 0.1)]]
    boat = [chain(quad((-0.2, -2.3), (0.3, -2.7), (1.6, -2.6), 10), [(2.0, -2.3), (-0.2, -2.3)]), rect(0.4, -2.3, 1.2, -1.9)]
    water = hide(water, boat[0])
    return make("Offshore Wind Turbines", out + water + boat + [gull(-3.0, 2.6, 0.35), gull(0.2, 3.3, 0.3)])


@design("coastal_lamp_post", T)
def lamp_post(rng):
    post = poly((-0.18, -2.0), (-0.12, 1.6), (0.12, 1.6), (0.18, -2.0))
    base = [poly((-0.5, -2.8), (-0.35, -2.0), (0.35, -2.0), (0.5, -2.8)), rect(-0.6, -3.0, 0.6, -2.8)]
    collar = [rect(-0.25, -1.2, 0.25, -1.05), rect(-0.2, 1.6, 0.2, 1.75)]
    arms = [cubic((0.1, 1.5), (0.8, 1.6), (1.2, 2.0), (1.3, 2.3), 14), cubic((-0.1, 1.5), (-0.8, 1.6), (-1.2, 2.0), (-1.3, 2.3), 14),
            spiral(0.45, 1.15, 0.05, 0.22, 1.2, 20), spiral(-0.45, 1.15, 0.05, 0.22, 1.2, 20, rot=math.pi)]
    lamps = []
    for x in (-1.3, 1.3):
        lamps += [poly((x - 0.35, 2.3), (x + 0.35, 2.3), (x + 0.45, 3.0), (x - 0.45, 3.0)), poly((x - 0.55, 3.0), (x + 0.55, 3.0), (x, 3.4)),
                  [(x, 3.4), (x, 3.6)], [(x, 2.3), (x, 3.0)]]
    rail_y = [-1.6, -1.0]
    rail = [[(-3.8, y), (3.8, y)] for y in (-0.6, -1.7)] + [[(x, -2.2), (x, -0.6)] for x in (-3.2, -2.0, 2.0, 3.2)]
    balust = [ellipse(x, -1.15, 0.12, 0.4, 14) for x in (-2.9, -2.6, -2.3, -1.7, -1.4, -1.1, 1.1, 1.4, 1.7, 2.3, 2.6, 2.9)]
    rail = hide(rail + balust, post, *base)
    prom = [[(-3.8, -2.2), (3.8, -2.2)], [(-3.8, -3.0), (3.8, -3.0)]]
    sea_ = [wave(-3.8, 3.8, 0.3, 0.05, 6, 120), wave(-3.5, 3.5, -0.15, 0.05, 6, 120)]
    sea_ = hide(sea_, post)
    out = [post] + base + collar + arms + lamps + rail + prom + sea_ + [gull(-2.6, 2.6, 0.4), gull(2.6, 1.6, 0.3)]
    return make("Promenade Lamp Post", out)


@design("coastal_hotel", T)
def hotel(rng):
    main = rect(-2.8, -2.2, 2.8, 0.8)
    rf = poly((-3.0, 0.8), (3.0, 0.8), (2.4, 1.6), (-2.4, 1.6))
    towers = []
    for x in (-2.4, 2.4):
        towers += [rect(x - 0.5, 0.8, x + 0.5, 2.0), poly((x - 0.65, 2.0), (x + 0.65, 2.0), (x, 3.2)), [(x, 3.2), (x, 3.6)], poly((x, 3.6), (x + 0.4, 3.45), (x, 3.3))]
    tower_w = [rect(x - 0.2, 1.1, x + 0.2, 1.7) for x in (-2.4, 2.4)]
    dormers = []
    for x in (-1.0, 0.0, 1.0):
        dormers += [poly((x - 0.3, 0.9), (x + 0.3, 0.9), (x + 0.3, 1.35), (x, 1.65), (x - 0.3, 1.35)), rect(x - 0.15, 1.0, x + 0.15, 1.3)]
    wins = []
    for y in (-0.15,):
        for x in [-2.3 + 0.66 * k for k in range(8)]:
            wins.append(rect(x - 0.18, y - 0.3, x + 0.18, y + 0.3))
    veranda = [rect(-2.9, -0.75, 2.9, -0.6), [(-2.9, -1.0), (2.9, -1.0)]] + [[(x, -2.2), (x, -0.75)] for x in (-2.7, -1.6, -0.5, 0.5, 1.6, 2.7)]
    balust = [[(-2.9, -1.6), (2.9, -1.6)]] + [[(x, -2.2), (x, -1.6)] for x in [-2.5 + 0.4 * k for k in range(13)] if abs(x) > 0.5]
    door = [rect(-0.4, -2.2, 0.4, -1.1), [(0, -2.2), (0, -1.1)]]
    steps = [rect(-0.7, -2.45, 0.7, -2.2), rect(-0.9, -2.7, 0.9, -2.45)]
    flag_ = []
    out = layered((towers + tower_w, [t for t in towers if len(t) == 5][:0] + [towers[0], towers[1], towers[4], towers[5]]), (dormers, dormers[::2]), ([rf], [rf]),
                  (veranda + door, [veranda[0]]), (hide(balust, rect(-0.45, -2.3, 0.45, -1.0)), []), ([main] + wins, [main]), (steps, []))
    return make("Victorian Seaside Hotel", out + [gull(-0.6, 2.8, 0.4), gull(0.6, 3.2, 0.3)])


@design("coastal_binocular_viewer", T)
def binocular_viewer(rng):
    head = rrect(-1.6, 0.6, 1.6, 2.0, 0.5)
    hood = [rrect(-1.8, 1.25, -0.3, 2.2, 0.3), rrect(0.3, 1.25, 1.8, 2.2, 0.3)]
    eyes_ = [circle(-1.05, 1.72, 0.3, 20), circle(1.05, 1.72, 0.3, 20)]
    lenses = [ellipse(-0.75, 0.95, 0.35, 0.25, 20), ellipse(0.75, 0.95, 0.35, 0.25, 20)]
    coinbox = [rect(-0.5, 0.2, 0.5, 0.6), rect(-0.15, 0.4, 0.15, 0.5)]
    handles = [tube([(-1.6, 1.2), (-2.4, 1.0)], 0.2), tube([(1.6, 1.2), (2.4, 1.0)], 0.2)]
    yoke = [poly((-0.6, 0.2), (0.6, 0.2), (0.35, -0.3), (-0.35, -0.3))]
    pole = poly((-0.25, -0.3), (0.25, -0.3), (0.35, -2.4), (-0.35, -2.4))
    base = [poly((-0.8, -2.8), (-0.4, -2.4), (0.4, -2.4), (0.8, -2.8)), rect(-1.0, -3.0, 1.0, -2.8)]
    rail = [[(-3.8, -1.2), (-0.3, -1.2)], [(0.3, -1.2), (3.8, -1.2)]] + [[(x, -3.0), (x, -1.2)] for x in (-3.0, -1.6, 1.6, 3.0)] + [[(-3.8, -2.0), (-0.3, -2.0)], [(0.3, -2.0), (3.8, -2.0)]]
    sea_ = [wave(-3.8, -1.9, -0.4, 0.05, 2, 40), wave(1.9, 3.8, -0.4, 0.05, 2, 40)]
    out = layered((eyes_, eyes_), (hood, hood), ([head] + lenses + coinbox, [head]), (handles, handles), (yoke + [pole] + base, [yoke[0], pole]), (rail + sea_, []))
    return make("Coin-Operated Binocular Viewer", out + [gull(-2.8, 2.6, 0.4), gull(2.7, 2.9, 0.35)])


@design("coastal_souwester", T)
def souwester(rng):
    wall = keep([[(x, -3.2), (x, 3.4)] for x in (-3.0, -1.5, 0.0, 1.5, 3.0)], rect(-3.8, -3.2, 3.8, 3.4)) * 0
    peg_board = rrect(-3.2, 2.2, 3.2, 2.7, 0.1)
    pegs = [circle(x, 2.45, 0.12, 10) for x in (-1.2, 1.4)]
    coat = spline([(-1.2, 2.3, 1), (-0.6, 2.0), (-2.4, 1.2), (-2.6, -1.6), (-2.4, -2.6, 1), (0.0, -2.6, 1), (0.2, -1.6), (0.0, 1.2), (-1.0, 2.0)])
    coat = spline([(-1.2, 2.35, 1), (-0.3, 1.8), (0.4, 0.8), (0.3, -2.6, 1), (-2.7, -2.6, 1), (-2.8, 0.8), (-2.1, 1.8)])
    collar = [poly((-1.9, 1.9), (-1.2, 1.2), (-0.5, 1.9), closed=False)]
    placket = [[(-1.2, 1.2), (-1.2, -2.6)]]
    toggles = [rrect(-1.4, y - 0.06, -1.0, y + 0.06, 0.05) for y in (0.6, -0.3, -1.2)]
    pockets = [rect(-2.4, -1.6, -1.6, -0.9), rect(-0.8, -1.6, 0.0, -0.9)]
    brim = spline([(-0.1, 1.15, 1), (0.6, 1.25), (1.6, 1.15), (2.6, 0.75), (3.0, 0.45, 1), (2.5, 0.45), (1.6, 0.8), (0.6, 0.95), (0.0, 0.95, 1)])
    crown = chain([(0.45, 1.24)], cubic((0.45, 1.24), (0.5, 2.3), (2.0, 2.3), (2.15, 1.0), 20)[1:])
    hat = [brim, crown]
    hat_band = [quad((0.5, 1.5), (1.3, 1.45), (2.12, 1.25), 10), quad((0.0, 1.05), (1.4, 1.0), (2.85, 0.5), 14)]
    seams = [quad((1.35, 2.05), (1.3, 1.7), (1.35, 1.3), 8)]
    ties = [cubic((0.8, 0.95), (0.7, 0.3), (1.0, -0.1), (0.9, -0.4), 10), cubic((1.9, 0.85), (2.0, 0.3), (1.7, -0.1), (1.8, -0.4), 10)]
    boots = [spline([(1.0, -2.6, 1), (1.0, -0.6, 1), (1.7, -0.6, 1), (1.75, -2.1), (2.6, -2.3), (2.6, -2.6, 1)]), spline([(2.3, -2.6, 1), (2.3, -0.8, 1), (3.0, -0.8, 1), (3.05, -2.1), (3.7, -2.3), (3.7, -2.6, 1)])]
    boots = [poly((1.0, -2.6), (1.0, -0.7), (1.7, -0.7), (1.7, -2.15), (2.4, -2.3), (2.4, -2.6)), poly((2.5, -2.6), (2.5, -0.9), (3.2, -0.9), (3.2, -2.15), (3.8, -2.3), (3.8, -2.6))]
    tops = [[(1.0, -1.0), (1.7, -1.0)], [(2.5, -1.2), (3.2, -1.2)]]
    floor = [[(-3.8, -2.6), (3.8, -2.6)]]
    out = layered((hat + hat_band + seams, [brim, chain(crown, [crown[0]])]), (ties, []), (pegs, pegs), ([coat] + collar + placket + toggles + pockets, [coat]), ([peg_board], []),
                  (boots[1:] + tops[1:], boots[1:]), (boots[:1] + tops[:1], boots[:1]), (floor, []))
    return make("Sou'wester Hat and Oilskin Coat", out)


# dropped: the subject repeats another book
def tidal_island(rng):
    mount = spline([(-3.0, -0.6, 1), (-2.2, 0.2), (-1.2, 1.0), (0.0, 1.4), (1.2, 0.9), (2.2, 0.1), (3.0, -0.6, 1)])
    keep_ = rect(-0.9, 1.2, 0.6, 2.4)
    crenel = [[(-0.9, 2.4), (-0.9, 2.6), (-0.6, 2.6), (-0.6, 2.4), (-0.3, 2.4), (-0.3, 2.6), (0.0, 2.6), (0.0, 2.4), (0.3, 2.4), (0.3, 2.6), (0.6, 2.6), (0.6, 2.4)]]
    tower = rect(0.6, 1.0, 1.2, 2.9)
    troof = poly((0.5, 2.9), (1.3, 2.9), (0.9, 3.6))
    church = [rect(-2.0, 0.4, -0.9, 1.5), poly((-2.15, 1.5), (-0.75, 1.5), (-1.45, 2.0))]
    wins = [rect(-0.5, 1.6, -0.2, 2.0), rect(0.8, 2.2, 1.0, 2.5), chain([(-1.6, 0.6), (-1.6, 1.0)], arc(-1.45, 1.0, 0.15, math.pi, 0, 6), [(-1.3, 0.6)])]
    houses = []
    for x0, y0 in [(-2.6, -0.4), (1.4, -0.2), (2.0, -0.55)]:
        hs, hc = house(x0, x0 + 0.6, y0, 0.45, 0.3, overhang=0.05)
        houses.append((hs, hc))
    trees = [circle(-0.2, 0.6, 0.35, 20), circle(0.4, 0.75, 0.3, 20)]
    causeway = [[(-0.5, -0.6), (-1.6, -3.0)], [(0.5, -0.6), (1.0, -3.0)]]
    stones = keep([[(-3, y), (3, y)] for y in (-1.2, -1.8, -2.4)], poly((-0.5, -0.6), (0.5, -0.6), (1.0, -3.0), (-1.6, -3.0)))
    water = hide([wave(-3.8, 3.8, -0.8 - 0.55 * k, 0.05, 6, 140) for k in range(4)], poly((-0.6, -0.55), (0.6, -0.55), (1.1, -3.1), (-1.7, -3.1)))
    people = []
    for x, y in [(-0.3, -1.6), (0.2, -2.3)]:
        people += [circle(x, y + 0.45, 0.1, 8), [(x, y + 0.35), (x, y + 0.05)], [(x, y + 0.05), (x - 0.1, y - 0.2)], [(x, y + 0.05), (x + 0.1, y - 0.2)]]
    out = layered(([troof], [troof]), ([tower] + wins[1:2], [tower]), ([keep_] + crenel + wins[:1], [keep_]), (church + wins[2:], church), *houses, (trees, trees), ([mount], []),
                  (causeway + stones + people + water, []))
    return make("Tidal Island Castle and Causeway", out + [gull(-2.6, 2.8, 0.35), gull(2.4, 2.4, 0.3)])


@design("coastal_stilt_house", T)
def stilt_house(rng):
    hs, hc = house(-2.2, 2.2, 0.0, 1.6, 1.3, door_x=1.3, wins=[(-1.3, 0.85), (0.0, 0.85)], overhang=0.3)
    deck = rect(-2.8, -0.25, 2.8, 0.0)
    deck_rail = [[(-2.8, 0.0), (-2.8, 0.6), (-2.2, 0.6)], [(2.2, 0.6), (2.8, 0.6), (2.8, 0.0)]] + [[(x, 0.0), (x, 0.6)] for x in (-2.5, 2.5)]
    stilts = [[(x, -0.25), (x, -2.6)] for x in (-2.5, -1.2, 0.0, 1.2, 2.5)]
    braces = [[(-2.5, -0.4), (-1.2, -1.5)], [(-1.2, -0.4), (-2.5, -1.5)], [(1.2, -0.4), (2.5, -1.5)], [(2.5, -0.4), (1.2, -1.5)]]
    stairs = [[(2.8, -0.25), (3.8, -2.6)], [(3.2, -0.25), (4.2, -2.6)]] + [[(2.8 + 0.25 * k + 0.1, -0.25 - 0.58 * k - 0.2), (3.2 + 0.25 * k + 0.1, -0.25 - 0.58 * k - 0.2)] for k in range(4)]
    stairs = [[(2.8, -0.25), (3.7, -2.6)], [(3.3, -0.25), (4.2, -2.6)]] + [[(2.8 + 0.9 * f, -0.25 - 2.35 * f), (3.3 + 0.9 * f, -0.25 - 2.35 * f)] for f in (0.2, 0.4, 0.6, 0.8)]
    sand = [quad((-3.8, -2.6), (0, -2.4), (4.4, -2.7), 30)]
    grass = [quad((x, -2.55), (x + 0.1, -2.0), (x + 0.3, -1.8), 6) for x in (-3.4, -3.2, -0.7, -0.5)]
    shingles = keep([[(-3, y), (3, y)] for y in (0.4, 1.3)], rect(-2.2, 0.0, 2.2, 1.6))
    shingles = hide(shingles, rect(-1.55, 0.6, -1.05, 1.1), rect(-0.25, 0.6, 0.25, 1.1), rect(1.05, 0.0, 1.55, 0.8))
    out = layered((hs + shingles, hc), ([deck] + deck_rail, [deck]), (stilts + braces + stairs + sand + grass, []))
    return make("Beach House on Stilts", out + [gull(-2.6, 3.4, 0.35), gull(-1.6, 3.0, 0.3)])


@design("coastal_boathouse", T)
def boathouse(rng):
    walls = rect(-2.6, -0.8, 2.6, 1.0)
    rf = poly((-3.0, 1.0), (3.0, 1.0), (0.0, 2.8))
    bay = chain([(-1.2, -0.8), (-1.2, 0.2)], arc(0.0, 0.2, 1.2, math.pi, 0, 20), [(1.2, -0.8)])
    doors = [[(-1.2, 0.2), (1.2, 0.2)]] * 0
    gable_w = [circle(0, 1.75, 0.35, 20), [(-0.35, 1.75), (0.35, 1.75)], [(0, 1.4), (0, 2.1)]]
    boards = keep([[(x, -0.8), (x, 1.0)] for x in (-2.2, -1.7, 1.7, 2.2)], walls)
    side_w = [rect(-2.2, 0.1, -1.6, 0.6), rect(1.6, 0.1, 2.2, 0.6)]
    piles = [[(x, -0.8), (x, -1.3)] for x in (-2.4, -1.4, 1.4, 2.4)]
    boat = [chain(quad((-0.9, -0.55), (-0.5, -0.85), (0.9, -0.8), 10), [(1.1, -0.55), (-0.9, -0.55)])]
    boat = keep(boat, chain(bay, [bay[0]]))
    dock = [rect(2.6, -0.9, 3.8, -0.75), rect(-3.8, -0.9, -2.6, -0.75)]
    water = [wave(-3.8, 3.8, -1.3 - 0.45 * k, 0.05, 6, 120) for k in range(3)]
    refl = [[(-1.0, -1.7), (1.0, -1.7)], [(-0.6, -2.15), (0.6, -2.15)]]
    trees = []
    for cx, y0, h, w in [(-3.4, -0.75, 3.2, 1.2), (3.4, -0.75, 2.8, 1.1)]:
        trees.append(pine(cx, y0, h, w))
    out = layered(([rf] + gable_w, [rf]), ([walls, bay] + boards + side_w + boat, [walls]), *trees, (dock + piles + water + refl, []))
    return make("Boathouse on the Water", out)
