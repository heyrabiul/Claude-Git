"""Kawaii Cute niche: Japanese-style cute food, animals and everyday objects,
each with a simple happy face (dot eyes, small smile, blush ovals)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "kawaii"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ------------------------------------------------------------------ helpers

def spl(pts, closed=True, res=14, tension=0.5):
    """Smooth Catmull-Rom outline through `pts`; a point given as (x, y, 0)
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


def sym(half, closed=True, axis=0.0):
    """Symmetric outline from the right half (top to bottom, on the axis at both ends)."""
    left = [(2 * axis - p[0],) + tuple(p[1:]) for p in half[-2:0:-1]]
    return spl(list(half) + left, closed=closed)


def dense(pts, step=0.04):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        d = math.dist(a, b)
        k = max(1, int(d / step))
        for i in range(1, k + 1):
            out.append((a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k))
    return out


def clip(pts, keep):
    out, cur = [], []
    for p in dense(pts):
        if keep(p):
            cur.append(p)
        else:
            if len(cur) > 1:
                out.append(cur)
            cur = []
    if len(cur) > 1:
        out.append(cur)
    return out


def inside_poly(pg):
    def f(p):
        x, y = p
        c = False
        for (x0, y0), (x1, y1) in zip(pg, pg[1:] + pg[:1]):
            if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
                c = not c
        return c
    return f


def hide(strokes, *outlines):
    """Clip strokes so nothing shows inside any of the given closed outlines."""
    tests = [inside_poly(o) for o in outlines]
    out = []
    for s in strokes:
        out += clip(s, lambda p: not any(t(p) for t in tests))
    return [s for s in out if len(s) > 1]


def keep_in(strokes, outline):
    test = inside_poly(outline)
    out = []
    for s in strokes:
        out += clip(s, test)
    return out


def tf(strokes, dx=0.0, dy=0.0, s=1.0, flip=False, rot=0.0):
    out = []
    c, n = math.cos(rot), math.sin(rot)
    for st in strokes:
        pts = []
        for x, y in st:
            x = -x if flip else x
            x, y = x * c - y * n, x * n + y * c
            pts.append((dx + x * s, dy + y * s))
        out.append(pts)
    return out


def face(cx, cy, s=1.0, mouth="smile", blush=True, eyes="dot", spread=0.55):
    """Kawaii face: returns (strokes, hints)."""
    st, hints = [], []
    ex = spread * s
    if eyes == "dot":
        hints += [eye(cx - ex, cy, 0.13 * s), eye(cx + ex, cy, 0.13 * s)]
    elif eyes == "closed":
        st += [arc(cx + sx * ex, cy + 0.05 * s, 0.17 * s, math.radians(200), math.radians(340), 8) for sx in (-1, 1)]
    elif eyes == "happy":
        st += [arc(cx + sx * ex, cy - 0.08 * s, 0.17 * s, math.radians(20), math.radians(160), 8) for sx in (-1, 1)]
    elif eyes == "sparkle":
        for sx in (-1, 1):
            st.append(circle(cx + sx * ex, cy, 0.2 * s, 16))
            hints.append(eye(cx + sx * ex, cy - 0.04 * s, 0.11 * s))
    my = cy - 0.3 * s
    if mouth == "smile":
        st.append(arc(cx, my + 0.12 * s, 0.17 * s, math.radians(200), math.radians(340), 10))
    elif mouth == "open":
        st.append(chain(arc(cx, my + 0.05 * s, 0.17 * s, math.pi, TAU, 10), [(cx - 0.17 * s, my + 0.05 * s)]))
    elif mouth == "cat":
        st.append(chain(arc(cx - 0.1 * s, my + 0.08 * s, 0.1 * s, math.pi, TAU, 6), arc(cx + 0.1 * s, my + 0.08 * s, 0.1 * s, math.pi, TAU, 6)))
    elif mouth == "o":
        st.append(ellipse(cx, my, 0.09 * s, 0.11 * s, 10))
    elif mouth == "flat":
        st.append([(cx - 0.12 * s, my + 0.05 * s), (cx + 0.12 * s, my + 0.05 * s)])
    if blush:
        st += [ellipse(cx + sx * (ex + 0.32 * s), cy - 0.25 * s, 0.19 * s, 0.1 * s, 14) for sx in (-1, 1)]
    return st, hints


def sparkle(x, y, r=0.3):
    return star(x, y, r, 4, 0.35)


def bumpy(cx, cy, rx, ry, k, a=0.13, n=None, rot=0.0):
    """Scalloped cloud / fluff outline with k bumps."""
    n = n or k * 14
    pts = []
    for i in range(n + 1):
        t = rot + TAU * i / n
        r = 1 - a * (1 - abs(math.sin(k * (t - rot) / 2)))
        pts.append((cx + rx * r * math.cos(t), cy + ry * r * math.sin(t)))
    return pts


def puff(pts):
    """Cloud built from overlapping circles [(x, y, r), ...] - outer outline only."""
    circles = [circle(x, y, r, 40) for x, y, r in pts]
    out = []
    for i, c in enumerate(circles):
        out += hide([c], *[d for j, d in enumerate(circles) if j != i])
    return out, circles


# ------------------------------------------------------------------- food

@design("kawaii_onigiri", T)
def onigiri(rng):
    body = spl([(0, 2.55), (0.6, 2.25), (1.6, 0.55), (2.45, -1.15), (2.3, -1.85), (1.4, -2.15), (0, -2.2), (-1.4, -2.15),
                (-2.3, -1.85), (-2.45, -1.15), (-1.6, 0.55), (-0.6, 2.25)])
    nori = keep_in([[(-1.05, -3), (-1.05, -0.75), (1.05, -0.75), (1.05, -3)]], body)
    grains = [lens((x, y), (x + 0.3 * math.cos(a), y + 0.3 * math.sin(a)), 0.3, 8) for x, y, a in
              [(-0.4, 1.6, 0.5), (0.5, 1.1, -0.4), (-1.7, -1.0, 1.0), (1.55, -1.1, 2.0), (-0.1, 1.0, 1.4), (1.8, -1.6, 0.3)]]
    f, h = face(0, 0.15, 1.1)
    sp = [sparkle(-2.4, 1.8), sparkle(2.4, 1.4, 0.25), sparkle(2.7, 2.4, 0.18)]
    return make("Kawaii Onigiri Rice Ball", [body] + nori + grains + f + sp, h)


@design("kawaii_nigiri", T)
def nigiri(rng):
    rice = spl([(-2.4, -0.6), (-2.5, -1.4), (-2.0, -2.0), (0, -2.15), (2.0, -2.0), (2.5, -1.4), (2.4, -0.6), (0, -0.4)])
    fish = spl([(-2.9, -0.55), (-2.6, 0.2), (-1.5, 0.75), (0.0, 0.95), (1.5, 0.85), (2.6, 0.35), (3.0, -0.5), (2.4, -0.75),
                (1.4, -0.45), (0.0, -0.35), (-1.4, -0.5), (-2.4, -0.85)])
    rice = hide([rice], fish)
    stripes = keep_in([spl([(x, -0.6), (x + 0.4, 0.1), (x + 0.75, 1.0)], closed=False) for x in (-2.0, -1.0, 0.0, 1.0)], fish)
    grains = [lens((x, y), (x + 0.28 * math.cos(a), y + 0.28 * math.sin(a)), 0.3, 8) for x, y, a in [(-1.8, -1.2, 0.3), (1.6, -1.5, 1.2), (1.9, -0.9, -0.3)]]
    f, h = face(0, -1.35, 0.9)
    geta = [rect(-3.2, -2.55, 3.2, -2.15), rect(-2.6, -2.95, -1.9, -2.55), rect(1.9, -2.95, 2.6, -2.55)]
    wasabi = [spl([(2.5, 1.4), (2.75, 1.85), (3.0, 1.4), (2.75, 1.25)])][:0]
    hearts = [heart(-2.2, 2.0, 0.35), heart(2.3, 2.2, 0.28)]
    return make("Kawaii Salmon Nigiri", rice + [fish] + stripes + grains + f + geta + wasabi + hearts, h)


@design("kawaii_bento", T)
def bento(rng):
    box = [rrect(-3.0, -2.4, 3.0, 1.7, 0.35), rrect(-2.8, -2.2, 2.8, 1.5, 0.25)]
    div = [[(0.2, -2.2), (0.2, 1.5)], [(0.2, -0.3), (2.8, -0.3)]]
    rice = spl([(-2.8, 0.9), (-2.3, 1.15), (-1.8, 0.95), (-1.3, 1.2), (-0.8, 0.95), (-0.3, 1.15), (0.2, 0.9)], closed=False)
    ume = [circle(-1.3, 0.35, 0.28, 20)]
    f, h = face(-1.3, -0.75, 0.95)
    rolls = []
    for x in (0.65, 1.6):
        rolls += [rrect(x, 0.0, x + 0.85, 0.85 + 0.25, 0.2), spiral(x + 0.42, 0.55, 0.05, 0.3, 1.3, 30)]
    tako = chain([(2.65, 0.2)], arc(2.25, 0.6, 0.45, -0.6, math.pi + 0.6, 20)[1:])[:0]
    # octopus sausage
    ox, oy = 1.1, -1.25
    oct_ = chain(arc(ox, oy, 0.6, 0, math.pi, 20), [(ox - 0.6, oy - 0.55), (ox - 0.4, oy - 0.35), (ox - 0.2, oy - 0.6), (ox, oy - 0.35),
                                                  (ox + 0.2, oy - 0.6), (ox + 0.4, oy - 0.35), (ox + 0.6, oy - 0.55), (ox + 0.6, oy)])
    of, oh = face(ox, oy + 0.15, 0.45)
    broc = bumpy(2.25, -1.05, 0.5, 0.42, 6, 0.18)
    stem = [[(2.1, -1.45), (2.05, -1.95), (2.45, -1.95), (2.4, -1.45)]]
    chop = [poly((-2.9, 2.0), (2.9, 2.55), (2.9, 2.7), (-2.9, 2.2)), poly((-2.9, 2.45), (2.9, 2.95), (2.9, 3.1), (-2.9, 2.65))]
    return make("Kawaii Bento Box", box + div + [rice] + ume + f + rolls + [oct_] + of + [broc] + stem + chop, h + oh)


@design("kawaii_dango", T)
def dango(rng):
    stick = [[(-0.12, -3.2), (-0.12, -2.4)], [(0.12, -3.2), (0.12, -2.4)], [(-0.12, -3.2), (0.12, -3.2)],
             [(-0.12, 2.4), (-0.12, 3.1)], [(0.12, 2.4), (0.12, 3.1)], [(-0.12, 3.1), (0.12, 3.1)]]
    balls = [circle(0, y, 0.95, 70) for y in (1.6, 0.0, -1.6)]
    vis = [balls[0]] + hide([balls[1]], balls[0]) + hide([balls[2]], balls[1])
    out, hints = [], []
    for y, eyes_, m in [(1.6, "dot", "smile"), (0.0, "happy", "open"), (-1.6, "closed", "cat")]:
        f, h = face(0, y + 0.05, 0.85, m, eyes=eyes_)
        out += f
        hints += h
    shine = [arc(0, y, 0.72, math.radians(110), math.radians(150), 6) for y in (1.6, 0.0, -1.6)]
    plate = [ellipse(0, -2.75, 2.4, 0.4, 60)]
    plate = hide(plate, balls[2])
    sp = [sparkle(-2.0, 2.2), sparkle(2.0, 0.8, 0.25), sparkle(-1.9, -0.6, 0.2)]
    stick = hide(stick, *balls)
    return make("Smiling Dango Skewer", vis + stick + out + shine + plate + sp, hints)


@design("kawaii_taiyaki", T)
def taiyaki(rng):
    body = spl([(-2.6, 0.2), (-2.2, 1.2), (-1.0, 1.75), (0.6, 1.6), (1.5, 1.0), (1.8, 0.55), (2.6, 1.5, 0), (3.0, 1.0), (2.8, 0.0),
                (3.0, -1.0), (2.6, -1.5, 0), (1.8, -0.55), (1.5, -1.0), (0.6, -1.6), (-1.0, -1.7), (-2.2, -1.1)])
    rim = spl([(-2.3, 0.2), (-1.95, 1.0), (-1.0, 1.45), (0.5, 1.3), (1.4, 0.65), (1.4, -0.65), (0.5, -1.3), (-1.0, -1.4), (-1.95, -0.9)])
    fin_t = poly((-0.6, 1.72), (0.1, 2.3), (0.7, 1.58), closed=False)
    fin_b = poly((-0.6, -1.72), (0.1, -2.3), (0.7, -1.58), closed=False)
    scales = []
    for row, y in enumerate((0.55, -0.1, -0.75)):
        for k in range(3):
            x = -0.5 + 0.55 * k + (0.27 if row % 2 else 0.0)
            scales.append(arc(x, y, 0.27, -1.1, 1.1, 8))
    tailr = [[(2.0, 0.4), (2.6, 0.9)], [(2.1, 0.0), (2.75, 0.0)], [(2.0, -0.4), (2.6, -0.9)]]
    gill = arc(-1.1, 0.0, 0.7, -1.0, 1.0, 12)
    f, h = face(-1.75, 0.35, 0.6)
    steam = [spl([(x, 2.2), (x - 0.2, 2.55), (x + 0.1, 2.85), (x - 0.1, 3.15)], closed=False) for x in (-1.5, -0.8)]
    return make("Kawaii Taiyaki Fish Cake", [body, rim, fin_t, fin_b, gill] + scales + tailr + f + steam, h)


@design("kawaii_toast", T)
def toast(rng):
    out = spl([(-2.0, -2.5, 0), (-2.15, 0.6), (-2.65, 1.4), (-2.4, 2.3), (-1.3, 2.75), (0, 2.55), (1.3, 2.75), (2.4, 2.3), (2.65, 1.4),
               (2.15, 0.6), (2.0, -2.5, 0)])
    inner = spl([(-1.7, -2.2, 0), (-1.85, 0.7), (-2.3, 1.45), (-2.1, 2.05), (-1.25, 2.4), (0, 2.22), (1.25, 2.4), (2.1, 2.05), (2.3, 1.45),
                 (1.85, 0.7), (1.7, -2.2, 0)])
    butter = transform(rrect(-0.75, -0.55, 0.75, 0.55, 0.15), dx=0.0, dy=0.7, rot=0.2)
    drip = spl([(-0.6, 0.2), (-0.7, -0.35), (-0.5, -0.45), (-0.35, 0.1)], closed=False)
    f, h = face(0, -1.0, 1.0)
    shine = [[(-0.45, 1.0), (-0.1, 1.08)]]
    crumbs = [circle(x, y, 0.07, 8) for x, y in [(-2.6, -2.6), (2.5, -2.4), (2.8, -2.7)]]
    return make("Kawaii Toast with a Butter Pat", [out, inner, butter] + hide([drip], butter) + f + shine + crumbs, h)


@design("kawaii_fried_egg", T)
def fried_egg(rng):
    white = polar(lambda t: 2.5 + 0.25 * math.sin(3 * t) + 0.15 * math.sin(5 * t + 1.0), n=300, cy=0.0)
    yolk = circle(-0.2, 0.3, 1.25, 80)
    f, h = face(-0.2, 0.25, 0.85)
    shine = [arc(-0.2, 0.3, 0.95, math.radians(110), math.radians(160), 8)]
    sp = [sparkle(2.0, 2.4, 0.3), sparkle(-2.3, -2.3, 0.25)]
    pan_hint = []
    return make("Sunny-Side-Up Egg Friend", [white, yolk] + f + shine + sp + pan_hint, h)


@design("kawaii_popcorn", T)
def popcorn(rng):
    bucket = poly((-2.0, 0.2), (2.0, 0.2), (1.5, -2.9), (-1.5, -2.9))
    rim = [rrect(-2.2, 0.0, 2.2, 0.45, 0.15)]
    stripes = [[(x0, 0.0), (x1, -2.9)] for x0, x1 in [(-1.2, -0.9), (-0.4, -0.3), (0.4, 0.3), (1.2, 0.9)]]
    kern, circles = puff([(-1.6, 0.75, 0.55), (-0.75, 0.95, 0.6), (0.2, 0.9, 0.62), (1.1, 0.95, 0.58), (1.75, 0.7, 0.5),
                          (-1.1, 1.65, 0.55), (-0.1, 1.85, 0.6), (0.9, 1.7, 0.55), (0.35, 2.55, 0.5), (-0.6, 2.5, 0.45)])
    kern = hide(kern, rim[0])
    pops = [bumpy(x, y, 0.32, 0.28, 5, 0.2) for x, y in [(-2.6, -1.5), (2.5, -2.3), (2.7, 1.8)]]
    f, h = face(0, -1.2, 0.95)
    face_clear = ellipse(0, -1.35, 1.0, 0.65, 40)
    stripes = hide(stripes, face_clear)
    return make("Kawaii Popcorn Bucket", [bucket] + rim + stripes + kern + pops + f, h)


@design("kawaii_fries", T)
def fries(rng):
    carton = spl([(-1.9, 0.9, 0), (-1.0, 0.45), (0.0, 0.3), (1.0, 0.45), (1.9, 0.9, 0), (1.35, -2.8, 0), (-1.35, -2.8, 0)])
    fries_ = []
    for x, top, rot in [(-1.45, 1.9, 0.12), (-0.9, 2.6, 0.05), (-0.35, 2.2, 0.0), (0.2, 2.9, -0.03), (0.75, 2.3, -0.06),
                        (1.3, 2.0, -0.12), (-0.62, 1.4, 0.0), (0.48, 1.6, 0.0)]:
        r = transform(rect(-0.22, -1.0, 0.22, top), dx=x, rot=rot)
        fries_.append(r)
    vis = []
    for i, fr in enumerate(fries_):
        vis += hide([fr], carton, *fries_[:i][:0])
    vis = []
    order = fries_[6:] + fries_[:6]
    for i, fr in enumerate(order):
        vis += hide([fr], carton, *order[i + 1:])
    f, h = face(0, -1.05, 1.05)
    band = [spl([(-1.75, -0.2), (0.0, -0.45), (1.75, -0.2)], closed=False)][:0]
    return make("Kawaii French Fries", [carton] + vis + f + band, h)


@design("kawaii_milk_carton", T)
def milk_carton(rng):
    front = rect(-1.4, -2.8, 1.0, 1.0)
    side = poly((1.0, -2.8), (2.0, -2.45), (2.0, 1.3), (1.0, 1.0), closed=False)
    gable = poly((-1.4, 1.0), (-0.2, 2.3), (1.0, 1.0), closed=False)
    roof = poly((-0.2, 2.3), (0.85, 2.6), (2.0, 1.3), closed=False)
    fin = [rect(-0.35, 2.3, 0.85, 2.85)][:0] + [poly((-0.2, 2.3), (-0.2, 2.75), (0.85, 3.05), (0.85, 2.6), closed=False)]
    label = [rrect(-1.1, -0.2, 0.7, 0.75, 0.15)]
    letters = []
    lx = -0.85
    M = [(0, 0), (0, 0.45), (0.15, 0.2), (0.3, 0.45), (0.3, 0)]
    I = [(0, 0), (0, 0.45)]
    L = [(0, 0.45), (0, 0), (0.25, 0)]
    K = [[(0, 0), (0, 0.45)], [(0.25, 0.45), (0, 0.2), (0.25, 0)]]
    letters = [transform(M, dx=lx, dy=0.05), transform(I, dx=lx + 0.5, dy=0.05), transform(L, dx=lx + 0.7, dy=0.05)]
    letters += [transform(k, dx=lx + 1.1, dy=0.05) for k in K]
    f, h = face(-0.2, -1.4, 0.95)
    drops = [spl([(2.6, 0.2), (2.45, -0.15), (2.6, -0.3), (2.75, -0.15)]), spl([(-2.3, 1.6), (-2.45, 1.25), (-2.3, 1.1), (-2.15, 1.25)])]
    return make("Kawaii Milk Carton", [front, side, gable, roof] + fin + label + letters + f + drops, h)


@design("kawaii_juice_box", T)
def juice_box(rng):
    front = rect(-1.7, -2.8, 1.1, 1.4)
    top = poly((-1.7, 1.4), (-1.0, 1.9), (1.8, 1.9), (1.1, 1.4), closed=False)
    side = poly((1.1, -2.8), (1.8, -2.3), (1.8, 1.9), closed=False)
    straw = tube([(0.6, 1.65), (0.6, 2.7), (1.3, 3.25)], 0.22)
    hole = [ellipse(0.6, 1.65, 0.18, 0.08, 10)]
    straw = hide([straw], hole[0])
    oc = (-0.3, 0.25)
    orange = [circle(oc[0], oc[1], 0.75, 50), circle(oc[0], oc[1], 0.6, 40)]
    segs = [[oc, (oc[0] + 0.6 * math.cos(a), oc[1] + 0.6 * math.sin(a))] for a in [k * TAU / 8 for k in range(8)]]
    leaf = [lens((oc[0] + 0.5, oc[1] + 0.55), (oc[0] + 1.1, oc[1] + 0.95), 0.4)]
    f, h = face(-0.3, -1.55, 0.95)
    return make("Kawaii Juice Box", [front, top, side] + straw + hole + orange + segs + leaf + f, h)


@design("kawaii_melon_pan", T)
def melon_pan(rng):
    bun = spl([(0, 2.1), (1.6, 1.85), (2.65, 0.9), (2.8, -0.2), (2.35, -1.3), (1.2, -1.85), (0, -1.95), (-1.2, -1.85), (-2.35, -1.3),
               (-2.8, -0.2), (-2.65, 0.9), (-1.6, 1.85)])
    base = spl([(-2.5, -1.15), (-1.5, -2.4), (0, -2.65), (1.5, -2.4), (2.5, -1.15)], closed=False)
    clear = ellipse(0, -0.6, 1.25, 0.75, 40)
    grid = []
    for d in [-3.0 + 0.75 * k for k in range(9)]:
        grid.append([(d - 3, -3), (d + 3, 3)])
        grid.append([(d - 3, 3), (d + 3, -3)])
    grid = hide(keep_in(grid, bun), clear)
    f, h = face(0, -0.5, 0.95)
    sp = [sparkle(-2.6, 2.3, 0.3), sparkle(2.6, 2.2, 0.22)]
    return make("Kawaii Melon Pan Bun", [bun, base] + grid + f + sp, h)


@design("kawaii_shaved_ice", T)
def shaved_ice(rng):
    cup = spl([(-2.2, -0.2, 0), (-1.9, -1.4), (-1.0, -2.05), (1.0, -2.05), (1.9, -1.4), (2.2, -0.2, 0)], closed=False)
    rim = [ellipse(0, -0.2, 2.2, 0.35, 60)]
    foot = [poly((-0.5, -2.05), (-0.7, -2.6), (0.7, -2.6), (0.5, -2.05), closed=False), ellipse(0, -2.7, 1.2, 0.25, 40)]
    ice = spl([(-1.95, 0.0), (-1.8, 1.0), (-1.2, 1.8), (-0.4, 2.35), (0.4, 2.4), (1.2, 1.9), (1.8, 1.0), (1.95, 0.0)], closed=False)
    syrup = spl([(-1.75, 1.05), (-1.3, 0.6), (-1.05, 1.1), (-0.6, 0.4), (-0.2, 1.0), (0.3, 0.55), (0.7, 1.1), (1.2, 0.6), (1.75, 1.05)],
                closed=False)
    rim = hide(rim, poly(*ice))
    spoon = [tube([(1.2, 1.6), (2.4, 3.0)], 0.2), ellipse(1.15, 1.5, 0.3, 0.18, 16, rot=0.85)]
    spoon = hide(spoon[:1], poly(*ice)) + []
    f, h = face(0, -1.05, 0.85)
    cherry = [circle(0.2, 2.75, 0.3, 20), quad((0.25, 3.05), (0.5, 3.4), (0.9, 3.5), 8)]
    return make("Kawaii Shaved Ice", [cup, ice, syrup] + rim + foot + spoon + f + cherry, h)


@design("kawaii_burrito", T)
def burrito(rng):
    wrap = spl([(-1.6, 2.5), (-0.3, 2.85), (1.0, 2.5), (1.6, 1.4), (1.7, -1.0), (1.6, -2.6), (0, -2.85), (-1.6, -2.6), (-1.7, -1.0),
                (-1.7, 1.4)])
    fold = [spl([(-1.6, 2.4), (-0.6, 1.9), (0.6, 1.95), (1.4, 1.6)], closed=False), spl([(-1.55, 1.2), (-0.8, 1.55)], closed=False)]
    foil = zigzag(-1.7, 1.7, -0.6, 0.15, 7)
    foil = [(x, y + 0.03 * x) for x, y in foil]
    lettuce = wave(-1.2, 1.2, 2.25, 0.08, 4, 40)
    lettuce = [(x, y + 0.2 * math.cos(x)) for x, y in lettuce]
    crinkle = [[(-1.2, -1.2), (-0.9, -1.6)], [(1.0, -1.4), (1.3, -1.9)], [(-0.4, -2.2), (-0.1, -2.5)]]
    f, h = face(0, 0.45, 0.95)
    sp = [sparkle(2.5, 2.4, 0.3), sparkle(-2.5, -1.5, 0.25)]
    return make("Kawaii Burrito", [wrap] + fold + [foil, lettuce] + crinkle + f + sp, h)


@design("kawaii_sandwich", T)
def sandwich(rng):
    out = spl([(0, 2.6, 0), (2.6, -1.9, 0), (-2.6, -1.9, 0)])
    out = spl([(-0.3, 2.35), (0, 2.55), (0.3, 2.35), (2.45, -1.55), (2.25, -1.95), (-2.25, -1.95), (-2.45, -1.55)])
    crust = spl([(-0.15, 1.95), (0, 2.05), (0.15, 1.95), (2.0, -1.5), (1.85, -1.7), (-1.85, -1.7), (-2.0, -1.5)])
    fill = spl([(-1.55, -0.8), (-1.0, -0.6), (-0.5, -0.85), (0.0, -0.6), (0.5, -0.85), (1.0, -0.6), (1.55, -0.8)], closed=False)
    fill2 = spl([(-1.75, -1.2), (1.75, -1.2)], closed=False)
    berries = [heart(x, -0.95, 0.2) for x in (-0.9, 0.0, 0.9)]
    fill = hide([fill, fill2], *berries)
    f, h = face(0, 0.45, 0.85)
    return make("Kawaii Triangle Sandwich", [out, crust] + fill + berries + f, h)


# ---------------------------------------------------------------- animals

@design("kawaii_panda", T)
def panda(rng):
    head = ellipse(0, 0.9, 1.65, 1.35, 90)
    ears = hide([circle(sx * 1.15, 2.05, 0.48, 30) for sx in (1, -1)], head)
    patches = [ellipse(sx * 0.62, 0.85, 0.36, 0.5, 30, rot=-sx * 0.5) for sx in (1, -1)]
    nose = [ellipse(0, 0.42, 0.18, 0.12, 14)]
    mouth = [chain(arc(-0.12, 0.22, 0.12, math.pi, TAU, 6), arc(0.12, 0.22, 0.12, math.pi, TAU, 6))]
    blush = [ellipse(sx * 1.15, 0.35, 0.2, 0.1, 12) for sx in (1, -1)]
    body = hide([ellipse(0, -1.45, 1.4, 1.25, 80)], head)
    bamboo = [rect(0.95, -2.9, 1.35, 2.2)]
    nodes = [[(0.95, y), (1.35, y)] for y in (-1.6, -0.3, 1.0)]
    leaves = [lens((1.35, 1.0), (2.3, 1.6), 0.3), lens((1.35, 1.0), (2.25, 0.6), 0.3), lens((0.95, 2.2), (0.5, 3.0), 0.3)]
    arms = [ellipse(0.95, -0.85, 0.45, 0.32, 24, rot=0.4), ellipse(1.3, -1.5, 0.45, 0.32, 24, rot=-0.3)]
    feet = [ellipse(sx * 0.85, -2.6, 0.55, 0.38, 30) for sx in (1, -1)]
    pads = [circle(sx * 0.85, -2.6, 0.17, 12) for sx in (1, -1)]
    stick = hide(bamboo + nodes, head, *arms, *feet, *[circle(sx * 1.15, 2.05, 0.48, 30) for sx in (1, -1)])
    body = hide(body, *arms, *feet, bamboo[0])
    leaves = hide(leaves, head)
    return make("Kawaii Panda Munching Bamboo", [head] + ears + patches + nose + mouth + blush + body + stick + leaves + arms + feet + pads,
                [eye(sx * 0.6, 0.9, 0.13) for sx in (1, -1)])


@design("kawaii_red_panda", T)
def red_panda(rng):
    head = sym([(0, 1.95), (1.0, 1.85), (1.65, 1.2), (1.8, 0.5), (1.4, 0.0), (0.6, -0.3), (0, -0.35)])
    ears = []
    for sx in (1, -1):
        ears.append(spl([(sx * 0.8, 1.9), (sx * 1.3, 2.75), (sx * 1.7, 2.3), (sx * 1.55, 1.35)], closed=False))
        ears.append(spl([(sx * 1.0, 1.95), (sx * 1.3, 2.45), (sx * 1.5, 2.15), (sx * 1.42, 1.65)], closed=False))
    muzzle = [ellipse(0, 0.22, 0.6, 0.42, 30)]
    brows = [ellipse(sx * 0.6, 1.3, 0.2, 0.13, 12) for sx in (1, -1)]
    tears = [spl([(sx * 0.62, 0.6), (sx * 0.8, 0.05), (sx * 0.62, -0.25)], closed=False) for sx in (1, -1)]
    cheeks = [spl([(sx * 1.05, 0.7), (sx * 1.45, 0.45), (sx * 1.3, 0.05)], closed=False) for sx in (1, -1)]
    nose = [ellipse(0, 0.38, 0.15, 0.1, 12)]
    mouth = [chain(arc(-0.11, 0.18, 0.11, math.pi, TAU, 6), arc(0.11, 0.18, 0.11, math.pi, TAU, 6))]
    body = spl([(-1.05, -0.25), (-1.35, -1.4), (-1.1, -2.55), (1.1, -2.55), (1.35, -1.4), (1.05, -0.25)], closed=False)
    tailc = spl([(0.9, -2.35), (2.1, -2.2), (2.75, -1.0), (2.6, 0.5), (2.2, 1.3)], closed=False)
    tail = tube(tailc, lambda t: 0.95 - 0.35 * t)
    tail = hide([tail], poly(*body, (0.0, -0.2)))
    rings = []
    for k in range(1, 5):
        i = int(len(tailc) * k / 5)
        a, b = tailc[i - 1], tailc[min(i + 1, len(tailc) - 1)]
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        w = (0.95 - 0.35 * k / 5) / 2
        rings.append([(tailc[i][0] - w * math.sin(ang), tailc[i][1] + w * math.cos(ang)), (tailc[i][0] + w * math.sin(ang), tailc[i][1] - w * math.cos(ang))])
    rings = hide(rings, poly(*body, (0.0, -0.2)))
    paws = [ellipse(sx * 0.55, -0.6, 0.3, 0.25, 20) for sx in (1, -1)] + [ellipse(sx * 0.6, -2.55, 0.42, 0.25, 20) for sx in (1, -1)]
    body = hide([body], *paws)
    blush = [ellipse(sx * 1.1, 0.75, 0.18, 0.09, 12) for sx in (1, -1)]
    return make("Kawaii Red Panda", [head] + ears + muzzle + brows + tears + cheeks + nose + mouth + body + tail + rings + paws + blush,
                [eye(sx * 0.6, 0.9, 0.14) for sx in (1, -1)])


@design("kawaii_koala", T)
def koala(rng):
    trunk = [[(-0.9, -3.2), (-0.85, 3.2)], [(0.9, -3.2), (0.85, 3.2)]]
    bark = [spl([(-0.4, 2.8), (-0.3, 2.4)], closed=False), spl([(0.3, -2.6), (0.4, -3.0)], closed=False)]
    head = ellipse(0, 1.15, 1.45, 1.2, 80)
    ears = [bumpy(sx * 1.45, 1.9, 0.72, 0.68, 7, 0.12) for sx in (1, -1)]
    ears = hide(ears, head)
    ears_in = hide([circle(sx * 1.5, 1.95, 0.38, 24) for sx in (1, -1)], head)
    nose = ellipse(0, 0.95, 0.32, 0.42, 30)
    mouth = [arc(0, 0.5, 0.15, math.radians(200), math.radians(340), 8)]
    blush = [ellipse(sx * 0.95, 0.65, 0.2, 0.1, 12) for sx in (1, -1)]
    body = ellipse(0, -1.05, 1.15, 1.25, 70)
    arms = [ellipse(sx * 0.95, -0.25, 0.32, 0.55, 24, rot=sx * 0.6) for sx in (1, -1)]
    legs = [ellipse(sx * 0.95, -1.9, 0.32, 0.55, 24, rot=-sx * 0.3) for sx in (1, -1)]
    claws = [[(sx * 1.2, y), (sx * 1.35, y - 0.05)] for sx in (1, -1) for y in (-0.05, -0.25)]
    body_v = hide([body], head, *arms, *legs)
    trunk = hide(trunk, head, body, *arms, *legs, *ears)
    leaves = [lens((0.85, 2.6), (1.9, 3.2), 0.28), lens((0.85, 2.6), (2.0, 2.55), 0.28), lens((-0.85, -2.4), (-2.0, -2.0), 0.28),
              lens((-0.85, -2.4), (-1.9, -2.9), 0.28)]
    twig = [[(0.85, 2.6), (1.4, 2.8)]][:0]
    return make("Kawaii Koala Hugging a Tree", trunk + bark + [head] + ears + ears_in + [nose] + mouth + blush + body_v + arms + legs + claws + leaves,
                [eye(sx * 0.65, 1.3, 0.13) for sx in (1, -1)])


# dropped: the subject repeats another book
def frog_umbrella(rng):
    ux, uy, R = 0.95, 1.2, 2.1
    dome = [(x, uy + (y - uy) * 0.62) for x, y in arc(ux, uy, R, 0, math.pi, 60)]
    w = 2 * R / 5
    scallop = [(ux + R, uy)]
    for k in range(5):
        a = ux + R - k * w
        scallop += arc(a - w / 2, uy, w / 2, TAU, math.pi, 10)[1:]
    canopy = chain(dome, scallop[::-1][1:])
    ribs = [quad((ux, uy + 0.62 * R), (ux + d * 0.55, uy + 0.9), (ux + d, uy), 10) for d in (-1.5 * w, -0.5 * w, 0.5 * w, 1.5 * w)]
    tip = [[(ux, uy + 0.62 * R), (ux, uy + 0.62 * R + 0.35)]]
    body = spl([(0, 0.15), (0.75, 0.05), (1.3, -0.55), (1.45, -1.4), (1.1, -2.2), (0.0, -2.4), (-1.1, -2.2), (-1.45, -1.4), (-1.3, -0.55),
                (-0.75, 0.05)])
    bumps = [circle(sx * 0.72, 0.05, 0.52, 30) for sx in (1, -1)]
    body_v = hide([body], *bumps)
    smile = [arc(0, -0.5, 0.55, math.radians(205), math.radians(335), 14)]
    blush = [ellipse(sx * 0.95, -0.6, 0.2, 0.1, 12) for sx in (1, -1)]
    belly = [ellipse(0, -1.65, 0.75, 0.55, 30)]
    hand = [ellipse(ux, -0.85, 0.3, 0.24, 16)]
    handle = hide([[(ux, uy), (ux, -0.85)]], *bumps, *hand)
    hook = [arc(ux + 0.25, -1.25, 0.25, math.pi, TAU, 8)]
    hook = hide(hook, *hand)
    legs = [ellipse(sx * 0.95, -2.4, 0.55, 0.22, 20) for sx in (1, -1)]
    drops = [spl([(x, y + 0.3), (x - 0.12, y), (x, y - 0.1), (x + 0.12, y)]) for x, y in [(-2.6, -0.4), (-2.2, 1.6), (2.6, -1.6), (-2.3, -2.0), (-1.2, 2.6)]]
    frog = hide(body_v + bumps + smile + blush + belly, *hand)
    return make("Kawaii Frog with an Umbrella", [canopy] + ribs + tip + handle + hook + frog + hand + hide(legs, body) + drops,
                [eye(sx * 0.72, 0.12, 0.17) for sx in (1, -1)])


@design("kawaii_bear_balloon", T)
def bear_balloon(rng):
    hx, hy = -0.9, 0.35
    head = ellipse(hx, hy, 1.35, 1.15, 70)
    ears = hide([circle(hx + sx * 1.0, hy + 1.0, 0.45, 26) for sx in (1, -1)], head)
    ears_in = hide([circle(hx + sx * 1.0, hy + 1.0, 0.22, 16) for sx in (1, -1)], head)
    muzzle = ellipse(hx, hy - 0.35, 0.5, 0.36, 24)
    nose = [ellipse(hx, hy - 0.22, 0.15, 0.1, 12)]
    mouth = [chain(arc(hx - 0.1, hy - 0.45, 0.1, math.pi, TAU, 6), arc(hx + 0.1, hy - 0.45, 0.1, math.pi, TAU, 6))]
    blush = [ellipse(hx + sx * 0.85, hy - 0.25, 0.2, 0.1, 12) for sx in (1, -1)]
    body = hide([spl([(hx - 0.9, hy - 0.8), (hx - 1.15, hy - 2.0), (hx - 0.8, hy - 2.95), (hx + 0.8, hy - 2.95), (hx + 1.15, hy - 2.0),
                      (hx + 0.9, hy - 0.8)], closed=False)], head)
    belly = [ellipse(hx, hy - 2.0, 0.6, 0.55, 30)]
    arm_r = tube([(hx + 0.95, hy - 1.15), (hx + 1.45, hy - 0.5), (hx + 1.55, hy + 0.05)], 0.5)
    paw = circle(hx + 1.55, hy + 0.1, 0.28, 18)
    arm_r = hide([arm_r], paw, head)
    arm_l = [ellipse(hx - 1.05, hy - 1.6, 0.3, 0.45, 20, rot=-0.4)]
    feet = [ellipse(hx + sx * 0.55, hy - 3.0, 0.45, 0.25, 20) for sx in (1, -1)]
    bx, by = 1.75, 1.9
    balloon = spl([(bx, by + 1.05), (bx + 0.85, by + 0.55), (bx + 0.8, by - 0.45), (bx, by - 1.0), (bx - 0.8, by - 0.45), (bx - 0.85, by + 0.55)])
    knot = poly((bx, by - 1.0), (bx - 0.15, by - 1.25), (bx + 0.15, by - 1.25))
    string = [spl([(bx, by - 1.25), (bx - 0.2, by - 1.8), (0.85, 0.85), (hx + 1.6, hy + 0.35)], closed=False)]
    shine = [arc(bx, by + 0.05, 0.6, math.radians(110), math.radians(160), 8)]
    bf, bh = face(bx, by, 0.55, "smile")
    return make("Kawaii Bear with a Balloon", [head] + ears + ears_in + [muzzle] + nose + mouth + blush + body + belly + arm_r + [paw] + arm_l
                + hide(feet, belly[0]) + [balloon, knot] + hide(string, paw) + shine + bf,
                [eye(hx + sx * 0.5, hy + 0.2, 0.13) for sx in (1, -1)] + bh)


@design("kawaii_alpaca", T)
def alpaca(rng):
    body = bumpy(-0.5, -0.9, 1.9, 1.15, 12, 0.08)
    neck = spl([(0.45, -0.2), (0.55, 0.3), (0.55, 0.7), (1.65, 0.7), (1.6, 0.3), (1.55, -0.4)], closed=False)
    head = spl([(0.4, 0.75), (0.3, 1.35), (0.6, 1.75), (1.6, 1.75), (1.9, 1.35), (1.8, 0.75), (1.4, 0.4), (0.8, 0.4)])
    tuft = bumpy(1.1, 1.8, 0.8, 0.45, 7, 0.2)
    head_v = hide([head], tuft)
    ears = [lens((0.5, 1.85), (0.2, 2.6), 0.3, 14), lens((1.7, 1.85), (2.0, 2.6), 0.3, 14)]
    ears = hide(ears, tuft)
    neck = hide([neck], head, body)
    f, h = face(1.1, 1.05, 0.65, "cat")
    legs = [leg(x, x + 0.45, -1.6, -2.8) for x in (-1.9, -1.2, 0.0, 0.7)]
    legs = hide(legs, body)
    hooves = [[(x, -2.55), (x + 0.45, -2.55)] for x in (-1.9, -1.2, 0.0, 0.7)]
    tail = [bumpy(-2.5, -0.55, 0.35, 0.3, 5, 0.2)]
    tail = hide(tail, body)
    blanket = keep_in([spl([(-1.3, 0.3), (-0.9, -0.6), (0.0, -0.7), (0.4, 0.2)], closed=False)], body)
    hearts = [heart(-2.0, 1.6, 0.35), heart(-0.9, 2.3, 0.25)]
    return make("Kawaii Alpaca", [body] + neck + head_v + [tuft] + ears + f + legs + hooves + tail + hearts, h)


@design("kawaii_ice_cubes", T)
def ice_cubes(rng):
    glass = poly((-2.2, 2.2), (-1.8, -2.8), (1.8, -2.8), (2.2, 2.2), closed=False)
    rim = [ellipse(0, 2.2, 2.2, 0.3, 60)]
    base = [[(-1.75, -2.45), (1.75, -2.45)]]
    water = [wave(-2.05, 2.05, 0.9, 0.06, 3, 50)]
    cubes, hints = [], []
    for cx, cy, rot, m in [(-0.75, -1.4, 0.15, "smile"), (0.75, -0.75, -0.2, "open"), (-0.35, 0.65, 0.35, "cat")]:
        cube = transform(rrect(-0.75, -0.7, 0.75, 0.7, 0.18), dx=cx, dy=cy, rot=rot)
        f, h = face(0, -0.05, 0.55, m, spread=0.3)
        cubes.append((cube, [transform(p_, dx=cx, dy=cy, rot=rot) for p_ in f], [transform(p_, dx=cx, dy=cy, rot=rot) for p_ in h]))
    out = []
    for i, (c, f, h) in enumerate(cubes):
        later = [cc for cc, _, _ in cubes[i + 1:]]
        out += hide([c] + f, *later)
        hints += h
    water = hide(water, *[c for c, _, _ in cubes])
    straw = tube([(1.0, -1.9), (1.4, 2.4), (2.4, 3.2)], 0.3)
    straw = hide([straw], *[c for c, _, _ in cubes])
    lemon = [circle(1.9, 2.25, 0.75, 40), circle(1.9, 2.25, 0.58, 36)]
    segs = [[(1.9, 2.25), (1.9 + 0.58 * math.cos(a), 2.25 + 0.58 * math.sin(a))] for a in [k * TAU / 6 for k in range(6)]]
    lemon_all = lemon + segs
    lemon_all = hide(lemon_all, poly((2.2, 2.2), (-2.2, 2.2), (-1.8, -2.8), (1.8, -2.8)))[:0] + lemon_all
    glass_v = hide([glass] + rim + water + straw, lemon[0])
    bubbles = [circle(x, y, r, 12) for x, y, r in [(-1.4, 0.2, 0.12), (1.3, 0.3, 0.1), (0.2, -2.1, 0.12)]]
    return make("Kawaii Ice Cubes in a Glass", glass_v + base + out + lemon_all + bubbles, hints)


@design("kawaii_tanuki", T)
def tanuki(rng):
    head = ellipse(0, 1.1, 1.5, 1.2, 80)
    ears = hide([circle(sx * 1.05, 2.05, 0.42, 26) for sx in (1, -1)], head)
    mask = spl([(0, 1.05), (-0.45, 1.45), (-1.05, 1.25), (-1.2, 0.75), (-0.75, 0.55), (0, 0.75), (0.75, 0.55), (1.2, 0.75), (1.05, 1.25),
                (0.45, 1.45)])
    muzzle = ellipse(0, 0.45, 0.5, 0.32, 24)
    muzzle_v = hide([muzzle], mask)
    nose = [ellipse(0, 0.62, 0.15, 0.1, 12)]
    mouth = [chain(arc(-0.1, 0.42, 0.1, math.pi, TAU, 6), arc(0.1, 0.42, 0.1, math.pi, TAU, 6))]
    leaf = lens((0.0, 2.25), (0.9, 3.2), 0.3)
    stem = [[(0.0, 2.25), (-0.2, 2.05)], [(0.1, 2.35), (0.75, 3.05)]]
    stem = hide(stem, head)
    body = hide([ellipse(0, -1.4, 1.35, 1.35, 80)], head)
    belly = [ellipse(0, -1.5, 0.85, 0.85, 50)]
    arms = [ellipse(sx * 1.15, -1.0, 0.28, 0.45, 18, rot=sx * 0.3) for sx in (1, -1)]
    feet = [ellipse(sx * 0.65, -2.75, 0.45, 0.22, 20) for sx in (1, -1)]
    tailc = spl([(1.15, -2.2), (2.1, -2.1), (2.6, -1.2), (2.45, -0.3)], closed=False)
    tail = tube(tailc, lambda t: 0.75 - 0.2 * t)
    tail = hide([tail], body[0] if body else head)
    bands = keep_in([[(1.6, -2.7), (1.9, -1.6)], [(2.2, -1.9), (2.9, -1.4)], [(2.0, -0.85), (2.9, -0.95)]], tube(tailc, lambda t: 0.75 - 0.2 * t))
    blush = [ellipse(sx * 1.05, 0.35, 0.18, 0.09, 12) for sx in (1, -1)]
    return make("Kawaii Tanuki with a Leaf", [head] + ears + [mask] + muzzle_v + nose + mouth + [leaf] + stem + body + belly + arms
                + hide(feet, belly[0]) + tail + bands + blush, [eye(sx * 0.65, 0.95, 0.13) for sx in (1, -1)])


@design("kawaii_quokka", T)
def quokka(rng):
    body = sym([(0, 1.9), (0.85, 1.75), (1.35, 1.05), (1.45, 0.2), (1.6, -0.9), (1.55, -1.9), (1.1, -2.55), (0, -2.65)])
    ears = []
    for sx in (1, -1):
        ears.append(spl([(sx * 0.6, 1.82), (sx * 0.75, 2.4), (sx * 1.25, 2.4), (sx * 1.3, 1.85), (sx * 1.18, 1.4)], closed=False))
        ears.append(spl([(sx * 0.82, 1.85), (sx * 0.92, 2.2), (sx * 1.12, 2.17), (sx * 1.12, 1.8)], closed=False))
    nose = [ellipse(0, 0.85, 0.2, 0.13, 14)]
    smile = [chain([(0, 0.72), (0, 0.55)]), arc(0, 0.75, 0.45, math.radians(215), math.radians(325), 14)]
    blush = [ellipse(sx * 0.85, 0.65, 0.2, 0.1, 12) for sx in (1, -1)]
    belly = [ellipse(0, -1.2, 0.85, 1.0, 50)]
    paws = [ellipse(sx * 0.5, -0.25, 0.25, 0.32, 18) for sx in (1, -1)]
    feet = [ellipse(sx * 0.75, -2.65, 0.55, 0.22, 20) for sx in (1, -1)]
    tail = [spl([(-1.45, -2.2), (-2.3, -2.6), (-2.9, -2.65)], closed=False), spl([(-1.3, -2.5), (-2.2, -2.8), (-2.9, -2.65)], closed=False)]
    leaf = [lens((1.6, 1.6), (2.6, 2.4), 0.35), [(1.6, 1.6), (2.6, 2.4)]]
    return make("Smiling Kawaii Quokka", hide([body], *feet) + ears + nose + smile + blush + hide(belly, *paws, *feet) + paws + feet + tail + leaf,
                [eye(sx * 0.55, 1.2, 0.13) for sx in (1, -1)])


# ------------------------------------------------------ stationery & gadgets

@design("kawaii_backpack", T)
def backpack(rng):
    body = rrect(-2.0, -2.8, 2.0, 1.6, 0.6)
    top = chain([(-2.0, 1.0)], arc(0, 1.0, 2.0, math.pi, 0, 40)[1:], [(2.0, 1.0)])
    top = [(x, 1.0 + (y - 1.0) * 0.55) for x, y in top]
    body = chain([(2.0, 1.0), (2.0, -2.2)], arc(1.4, -2.2, 0.6, 0, -math.pi / 2, 8), [(-1.4, -2.8)], arc(-1.4, -2.2, 0.6, -math.pi / 2, -math.pi, 8),
                 [(-2.0, 1.0)])
    flap = spl([(-2.1, 1.05), (-2.05, -0.6), (-1.6, -0.95), (1.6, -0.95), (2.05, -0.6), (2.1, 1.05)], closed=False)
    clasp = [rrect(-0.3, -1.25, 0.3, -0.75, 0.1)]
    handle = [arc(0, 2.0, 0.55, 0.2, math.pi - 0.2, 16), arc(0, 2.0, 0.35, 0.3, math.pi - 0.3, 12)]
    straps = [spl([(-2.0, 0.6), (-2.6, -0.6), (-2.5, -2.4)], closed=False), spl([(2.0, 0.6), (2.6, -0.6), (2.5, -2.4)], closed=False)]
    pocket = [rrect(-1.2, -2.5, 1.2, -1.55, 0.3)]
    f, h = face(0, 0.3, 1.05)
    star_ = [star(1.3, -2.05, 0.25)]
    return make("Kawaii School Backpack", [top, body, flap] + clasp + handle + straps + hide(pocket, clasp[0]) + f + star_, h)


@design("kawaii_pencil_eraser", T)
def pencil_eraser(rng):
    rot = 0.55
    pencil = [rect(-0.45, -2.2, 0.45, 1.9), poly((-0.45, -2.2), (0.0, -3.3), (0.45, -2.2), closed=False),
              [(-0.17, -2.75), (0.17, -2.75)], rect(-0.45, 1.9, 0.45, 2.35), [(-0.45, 2.12), (0.45, 2.12)]]
    cap = [chain([(-0.45, 2.35), (-0.45, 2.6)], arc(-0.05, 2.6, 0.4, math.pi, 0, 10), [(0.35, 2.35)])]
    cap = [chain([(-0.45, 2.35), (-0.45, 2.65)], arc(0.0, 2.65, 0.45, math.pi, 0, 12), [(0.45, 2.35)])]
    stripes = [[(-0.15, -2.2), (-0.15, 1.9)], [(0.15, -2.2), (0.15, 1.9)]][:0]
    f, h = face(0.0, 0.2, 0.55, spread=0.25)
    pen = tf(pencil + cap + f, -1.2, 0.3, 1.0, rot=rot)
    ph = [eye(*tf([[(x, y)]], -1.2, 0.3, 1.0, rot=rot)[0][0], 0.08) for x, y in [(-0.14, 0.2), (0.14, 0.2)]]
    pen_f = tf([[(xy[0], xy[1]) for xy in st] for st in face(0.0, 0.2, 0.55, spread=0.25)[0]], -1.2, 0.3, 1.0, rot=rot)
    eraser = transform(rrect(-1.2, -0.75, 1.2, 0.75, 0.2), dx=1.5, dy=-1.2, rot=-0.15)
    sleeve = transform(rect(-1.2, -0.75, 0.2, 0.75), dx=1.5, dy=-1.2, rot=-0.15)
    ef, eh = face(1.9, -1.35, 0.6, "open")
    shavings = []
    stars_ = [star(2.2, 1.3, 0.3), sparkle(-2.4, -2.0, 0.3)]
    return make("Kawaii Pencil and Eraser Pals", pen[:5] + pen[5:6] + pen_f + [eraser, sleeve] + ef + shavings + stars_, ph + eh)


@design("kawaii_camera", T)
def camera(rng):
    body = rrect(-2.8, -1.9, 2.8, 1.3, 0.45)
    top = [poly((-1.0, 1.3), (-0.75, 1.9), (0.75, 1.9), (1.0, 1.3), closed=False)]
    btn = [rrect(1.6, 1.3, 2.3, 1.6, 0.1)]
    flash = [rrect(-2.4, 0.55, -1.6, 0.95, 0.12)]
    lens_ = [circle(0, -0.3, 1.35, 70), circle(0, -0.3, 1.05, 60)]
    f, h = face(0, -0.25, 0.75)
    shine = [arc(0, -0.3, 0.85, math.radians(115), math.radians(160), 8)]
    strap = [[(-2.8, 0.6), (-3.2, 0.9)], [(2.8, 0.6), (3.2, 0.9)]]
    stripe = [[(-2.8, -1.4), (-1.35, -1.4)], [(1.35, -1.4), (2.8, -1.4)]]
    hearts = [heart(-2.3, 2.4, 0.3), sparkle(2.4, 2.5, 0.3)]
    return make("Kawaii Camera", [body] + top + btn + flash + lens_ + f + shine + strap + stripe + hearts, h)


@design("kawaii_game_console", T)
def game_console(rng):
    body = chain([(-1.9, 2.9), (1.9, 2.9), (1.9, -2.1)], arc(1.2, -2.1, 0.7, 0, -math.pi / 2, 10), [(-1.5, -2.8)],
                 arc(-1.5, -2.4, 0.4, -math.pi / 2, -math.pi, 8), [(-1.9, 2.9)])
    bezel = rrect(-1.5, 0.2, 1.5, 2.5, 0.2)
    screen = rect(-1.1, 0.5, 1.1, 2.2)
    f, h = face(0, 1.4, 0.75)
    dpad = poly((-1.25, -0.6), (-1.25, -0.9), (-0.95, -0.9), (-0.95, -1.2), (-0.65, -1.2), (-0.65, -0.9), (-0.35, -0.9), (-0.35, -0.6),
                (-0.65, -0.6), (-0.65, -0.3), (-0.95, -0.3), (-0.95, -0.6))
    ab = [circle(0.75, -0.95, 0.25, 18), circle(1.35, -0.6, 0.25, 18)]
    sel = [rrect(-0.6, -1.75, -0.15, -1.6, 0.07), rrect(0.1, -1.75, 0.55, -1.6, 0.07)]
    speaker = [[(0.75 + 0.22 * k, -2.0 - 0.0 * k), (0.95 + 0.22 * k, -2.4)] for k in range(3)]
    stars_ = [star(-2.6, 2.3, 0.3), star(2.6, 0.0, 0.25), sparkle(-2.6, -1.8, 0.3)]
    return make("Kawaii Handheld Game Console", [body, bezel, screen] + f + [dpad] + ab + sel + speaker + stars_, h)


@design("kawaii_smartphone", T)
def smartphone(rng):
    body = rrect(-1.6, -3.0, 1.6, 3.0, 0.45)
    screen = rrect(-1.35, -2.4, 1.35, 2.5, 0.15)
    notch = [rrect(-0.4, 2.62, 0.4, 2.78, 0.08)]
    home = [circle(0, -2.7, 0.17, 14)]
    f, h = face(0, 0.2, 1.0)
    bubble = [rrect(0.5, 1.2, 2.9, 2.5, 0.4), poly((0.9, 1.2), (0.7, 0.85), (1.3, 1.2), closed=False)]
    hrt = [heart(1.2, 1.85, 0.3), heart(2.2, 1.85, 0.3)]
    bubble = hide(bubble, body)
    bubble = [chain([(1.35, 1.2), (2.5, 1.2)], arc(2.5, 1.6, 0.4, -math.pi / 2, math.pi / 2, 8), [(1.35, 2.0)])][:0] + bubble
    signal = [[(-1.1 + 0.18 * k, 2.25), (-1.1 + 0.18 * k, 2.3 + 0.0)] for k in ()]
    apps = [rrect(-1.05 + 0.75 * k, -2.0, -0.6 + 0.75 * k, -1.55, 0.1) for k in range(3)]
    return make("Kawaii Smartphone", [body, screen] + notch + home + f + hide(hrt, body) + bubble + apps, h)


@design("kawaii_succulent", T)
def succulent(rng):
    pot = poly((-1.8, -0.4), (1.8, -0.4), (1.35, -2.9), (-1.35, -2.9))
    rim = [rrect(-2.05, -0.55, 2.05, 0.05, 0.15)]
    leaves = []
    for k, a in enumerate([90, 50, 130, 20, 160]):
        aa = math.radians(a)
        L = 2.4 if k == 0 else (1.9 if k < 3 else 1.6)
        leaves.append(lens((0, 0.05), (L * math.cos(aa), 0.05 + L * math.sin(aa)), 0.28, 20))
    vis = []
    for i, lf in enumerate(leaves):
        vis += hide([lf], rim[0], *leaves[i + 1:])
    centre = hide([lens((0, 0.05), (0.0, 1.3), 0.3, 14)], rim[0])
    vis = hide(vis, centre[0] if centre else rim[0]) + centre
    f, h = face(0, -1.55, 0.9)
    return make("Kawaii Succulent in a Pot", [pot] + rim + vis + f, h)


@design("kawaii_house", T)
def house(rng):
    walls = poly((-2.2, -2.8), (2.2, -2.8), (2.2, 0.6), (-2.2, 0.6))
    roof = spl([(-2.8, 0.45), (0.0, 2.85), (2.8, 0.45), (2.5, 0.2, 0), (0.0, 2.35), (-2.5, 0.2, 0)])
    roof = poly((-2.8, 0.5), (0.0, 2.85), (2.8, 0.5), (2.55, 0.25), (0.0, 2.4), (-2.55, 0.25))
    chimney = [poly((1.2, 1.8), (1.2, 2.6), (1.75, 2.6), (1.75, 1.35), closed=False)]
    smoke = [spl([(1.5, 2.8), (1.3, 3.1), (1.6, 3.35), (1.4, 3.6)], closed=False)]
    door = [chain([(0.55, -2.8), (0.55, -1.3)], arc(1.15, -1.3, 0.6, math.pi, 0, 14), [(1.75, -2.8)]), circle(1.55, -2.05, 0.07, 6)]
    win = [rect(-1.85, -1.0, -0.95, -0.1), [(-1.4, -1.0), (-1.4, -0.1)], [(-1.85, -0.55), (-0.95, -0.55)]]
    f, h = face(0.0, 1.1, 0.7)
    flowers = [bumpy(-1.4, -2.45, 0.75, 0.38, 6, 0.15)]
    flowers = [keep_in(flowers, poly((-3, -2.8), (3, -2.8), (3, 3), (-3, 3)))[0]] + [[(-2.2, -2.8), (-2.15, -2.6)]][:0]
    flowers += [circle(x, y, 0.12, 10) for x, y in [(-1.8, -2.35), (-1.3, -2.2), (-0.9, -2.45)]]
    path = [[(0.55, -2.8), (0.2, -3.2)], [(1.75, -2.8), (2.1, -3.2)]]
    return make("Kawaii Little House", [walls, roof] + chimney + smoke + door + win + f + flowers + path, h)


@design("kawaii_socks", T)
def socks(rng):
    def sock(dx, flip):
        out = spl([(-0.75, 2.6, 0), (0.75, 2.6, 0), (0.75, -0.4), (1.0, -1.1), (1.9, -1.7), (2.05, -2.35), (1.6, -2.75), (0.4, -2.6),
                   (-0.55, -1.9), (-0.8, -0.8)])
        cuff = [[(-0.78, 2.0), (0.78, 2.0)]]
        ribs = [[(x, 2.0), (x, 2.6)] for x in (-0.4, 0.0, 0.4)]
        stripe = [[(-0.79, 0.8), (0.75, 0.8)], [(-0.8, 0.35), (0.75, 0.35)]]
        heel = [arc(-0.2, -2.0, 0.65, math.radians(140), math.radians(250), 10)]
        toe = [arc(1.55, -2.2, 0.55, math.radians(-80), math.radians(60), 10)]
        f, h = face(0.0, 1.3, 0.55, spread=0.3)
        st = tf([out] + cuff + ribs + stripe + heel + toe + f, dx, 0.2, 1.0, flip)
        hh = [eye(*tf([[(x, 1.3)]], dx, 0.2, 1.0, flip)[0][0], 0.08) for x in (-0.3, 0.3)]
        return st, hh
    a, ha = sock(-1.5, True)
    b, hb = sock(1.3, False)
    hearts = [heart(0.0, 2.6, 0.3)]
    return make("Pair of Kawaii Socks", a + b + hearts, ha + hb)


@design("kawaii_thundercloud", T)
def thundercloud(rng):
    cl, circles = puff([(-1.7, 0.9, 0.95), (-0.5, 1.5, 1.2), (0.9, 1.35, 1.05), (2.0, 0.75, 0.85), (0.2, 0.45, 1.0), (-1.0, 0.3, 0.8), (1.3, 0.35, 0.8)])
    f, h = face(0.1, 0.8, 0.95, "o")
    brows = [[(-0.75, 1.3), (-0.3, 1.15)], [(0.95, 1.3), (0.5, 1.15)]]
    bolt = poly((-0.2, -0.45), (-0.9, -1.75), (-0.35, -1.75), (-0.8, -3.0), (0.6, -1.4), (0.0, -1.4), (0.4, -0.45))
    bolt = hide([bolt], *circles)
    bolt2 = poly((1.7, -0.1), (1.35, -0.9), (1.7, -0.9), (1.45, -1.7), (2.3, -0.7), (1.95, -0.7), (2.2, -0.1))
    bolt2 = hide([bolt2], *circles)
    drops = [spl([(x, y + 0.3), (x - 0.12, y), (x, y - 0.1), (x + 0.12, y)]) for x, y in [(-2.1, -1.0), (-1.6, -2.2), (1.0, -2.6), (2.6, -2.0)]]
    return make("Kawaii Thundercloud with Lightning", cl + f + brows + bolt + bolt2 + drops, h)


# ------------------------------------------------------ Japanese charms

@design("kawaii_daruma", T)
def daruma(rng):
    body = spl([(0, 2.7), (1.55, 2.3), (2.3, 1.0), (2.4, -0.6), (1.9, -2.2), (0.0, -2.75), (-1.9, -2.2), (-2.4, -0.6), (-2.3, 1.0), (-1.55, 2.3)])
    face_o = ellipse(0, 0.85, 1.45, 1.15, 70)
    eyes_o = [circle(sx * 0.6, 1.0, 0.38, 26) for sx in (1, -1)]
    brows = [spl([(sx * 0.25, 1.65), (sx * 0.6, 1.85), (sx * 1.0, 1.7)], closed=False) for sx in (1, -1)]
    stache = [spl([(0, 0.35), (sx * 0.4, 0.5), (sx * 0.8, 0.35), (sx * 0.95, 0.15)], closed=False) for sx in (1, -1)]
    mouth = [arc(0, 0.05, 0.2, math.radians(200), math.radians(340), 8)]
    blush = [ellipse(sx * 1.05, 0.25, 0.2, 0.1, 12) for sx in (1, -1)]
    belly = [spl([(-1.3, -1.0), (-0.6, -0.75), (0.0, -1.0), (0.6, -0.75), (1.3, -1.0)], closed=False)]
    swirls = [spiral(sx * 0.9, -1.75, 0.05, 0.38, 1.3, 40, rot=0.0 if sx > 0 else math.pi) for sx in (1, -1)]
    kotobuki = [rrect(-0.45, -2.05, 0.45, -1.3, 0.1), [(-0.25, -1.5), (0.25, -1.5)], [(-0.25, -1.68), (0.25, -1.68)], [(0, -1.4), (0, -1.95)]]
    return make("Kawaii Daruma Doll", [body, face_o] + eyes_o + brows + stache + mouth + blush + belly + swirls + kotobuki,
                [eye(sx * 0.6, 1.0, 0.17) for sx in (1, -1)])


@design("kawaii_kokeshi", T)
def kokeshi(rng):
    head = circle(0, 1.25, 1.55, 90)
    hair = spl([(-1.55, 1.1), (-1.0, 1.75), (-0.2, 2.0), (0.3, 1.55), (0.9, 1.95), (1.4, 1.6), (1.55, 1.1)], closed=False)
    side = [[(-1.5, 0.85), (-1.15, 0.2)], [(1.5, 0.85), (1.15, 0.2)]][:0]
    bun = [circle(0, 3.0, 0.45, 30)]
    bun = hide(bun, head)
    flower = [circle(1.3, 2.35, 0.17, 12)] + [circle(1.3 + 0.28 * math.cos(a), 2.35 + 0.28 * math.sin(a), 0.14, 10) for a in [k * TAU / 5 + 0.3 for k in range(5)]]
    flower = hide(flower, *[circle(1.3, 2.35, 0.17, 12)][:0])
    f, h = face(0, 0.75, 0.8)
    body = spl([(-1.15, -0.2), (-1.35, -1.4), (-1.2, -2.8, 0), (1.2, -2.8, 0), (1.35, -1.4), (1.15, -0.2)], closed=False)
    body = hide([body], head)
    collar = [poly((-0.7, -0.15), (0.0, -0.85), (0.7, -0.15), closed=False)]
    sash = [[(-1.33, -1.1), (1.33, -1.1)], [(-1.35, -1.55), (1.35, -1.55)]]
    blossoms = []
    for x, y in [(-0.55, -2.2), (0.55, -2.25)]:
        blossoms += [circle(x, y, 0.12, 10)] + [circle(x + 0.24 * math.cos(a), y + 0.24 * math.sin(a), 0.12, 10) for a in [k * TAU / 5 for k in range(5)]]
    return make("Kawaii Kokeshi Doll", [head, hair] + side + bun + flower + f + body + collar + sash + blossoms, h)


@design("kawaii_teru_teru_bozu", T)
def teru_teru(rng):
    head = circle(0, 0.8, 1.35, 80)
    string = [[(0, 2.15), (0, 3.2)], [(-0.6, 3.2), (0.6, 3.2)]]
    skirt = spl([(-0.85, -0.35), (-1.6, -1.4), (-2.0, -2.6), (-1.3, -2.3), (-0.7, -2.75), (0.0, -2.35), (0.7, -2.75), (1.3, -2.3),
                 (2.0, -2.6), (1.6, -1.4), (0.85, -0.35)], closed=False)
    skirt = hide([skirt], head)
    tie = [ellipse(0, -0.55, 0.85, 0.15, 30)]
    tie = hide(tie, head)
    bow = [lens((0.2, -0.6), (0.9, -1.05), 0.4), lens((0.2, -0.6), (0.85, -0.25), 0.4)][:0]
    folds = [spl([(-0.6, -0.8), (-0.9, -1.6), (-1.0, -2.3)], closed=False), spl([(0.6, -0.8), (0.9, -1.6), (1.0, -2.3)], closed=False),
             spl([(0, -0.75), (0, -2.2)], closed=False)]
    f, h = face(0, 0.75, 0.95)
    drops = [spl([(x, y + 0.3), (x - 0.12, y), (x, y - 0.1), (x + 0.12, y)]) for x, y in [(-2.4, 1.6), (2.3, 1.2), (-2.6, -0.6), (2.5, -0.9)]]
    sun = [circle(2.4, 2.7, 0.35, 24)] + [[(2.4 + 0.5 * math.cos(a), 2.7 + 0.5 * math.sin(a)), (2.4 + 0.75 * math.cos(a), 2.7 + 0.75 * math.sin(a))]
                                         for a in [k * TAU / 8 for k in range(8)]]
    return make("Teru Teru Bozu Rain Charm", [head] + string + skirt + tie + folds + f + drops + sun, h)


@design("kawaii_koinobori", T)
def koinobori(rng):
    pole = [[(-2.7, -3.0), (-2.7, 2.6)], [(-2.45, -3.0), (-2.45, 2.6)]]
    ball = [circle(-2.575, 2.85, 0.25, 20)]
    wheel = [circle(-2.575, 2.2, 0.35, 20)][:0]

    def carp(y, L, s):
        top = spl([(0, 0.55), (L * 0.35, 0.7), (L * 0.7, 0.55), (L, 0.75, 0)], closed=False)
        bot = spl([(0, -0.55), (L * 0.35, -0.5), (L * 0.7, -0.65), (L, -0.75, 0)], closed=False)
        tail = poly((L, 0.75), (L - 0.25, 0.0), (L, -0.75), closed=False)
        mouth = ellipse(0, 0.0, 0.15, 0.55, 24)
        eye_o = circle(0.55, 0.12, 0.25, 18)
        scales = []
        for k in range(2):
            for j in (-1, 1):
                scales.append(arc(L * (0.45 + 0.2 * k), 0.25 * j, 0.25, -1.2, 1.2, 8))
        gill = [arc(0.75, 0.0, 0.45, -1.0, 1.0, 10)]
        blush = [ellipse(0.55, -0.3, 0.17, 0.08, 10)]
        smile = [arc(0.28, -0.12, 0.1, math.radians(200), math.radians(340), 6)][:0]
        st = [top, bot, tail, mouth, eye_o] + scales + gill + blush
        return tf(st, -2.45, y, s), [eye(*tf([[(0.55, 0.1)]], -2.45, y, s)[0][0], 0.1 * s)]
    a, ha = carp(1.6, 4.6, 1.15)
    b, hb = carp(-0.4, 4.2, 1.0)
    c, hc = carp(-2.1, 3.6, 0.85)
    smile = [arc(-2.45 + 0.9, 1.6 - 0.25, 0.12, math.radians(200), math.radians(340), 6)]
    return make("Kawaii Koinobori Carp Streamers", pole + ball + a + b + c, ha + hb + hc)


@design("kawaii_origami_crane", T)
def origami_crane(rng):
    body = poly((-1.1, -0.5), (0.0, -1.5), (1.1, -0.5), (0.0, 0.1))
    wing_l = poly((-0.55, -0.2), (0.0, 0.1), (-2.0, 2.7))
    wing_r = poly((0.0, 0.1), (0.55, -0.2), (2.3, 2.4))
    wing_r = hide([wing_r], wing_l)
    neck = poly((-1.1, -0.5), (-0.7, -0.75), (-2.45, 1.0))
    head = poly((-2.45, 1.0), (-2.85, 0.55), (-2.25, 0.8))
    tail = poly((1.1, -0.5), (0.7, -0.75), (2.85, 0.55))
    keel = [[(0.0, 0.1), (0.0, -1.5)]][:0]
    f, h = face(0.0, -0.55, 0.45, spread=0.28)
    sparkles = [sparkle(-2.4, -2.0, 0.35), sparkle(2.4, -1.6, 0.3), sparkle(0.2, 2.7, 0.25)]
    waves = [wave(-3.0, 3.0, -2.75, 0.08, 6, 80)]
    return make("Kawaii Origami Crane", [body, wing_l] + wing_r + [neck, head, tail] + f + sparkles + waves, h)


# ------------------------------------------------------ everyday things

@design("kawaii_lightbulb", T)
def lightbulb(rng):
    bulb = spl([(0, 2.7), (1.35, 2.3), (1.85, 1.2), (1.5, 0.0), (0.85, -0.75), (0.75, -1.2, 0), (-0.75, -1.2, 0), (-0.85, -0.75),
                (-1.5, 0.0), (-1.85, 1.2), (-1.35, 2.3)])
    base = [rect(-0.8, -1.2, 0.8, -2.3)] + [[(-0.8, y), (0.8, y + 0.15)] for y in (-1.55, -1.9)]
    tip = [chain([(-0.5, -2.3)], arc(0, -2.3, 0.5, math.pi, TAU, 10)[1:], [(0.5, -2.3)])]
    tip = [[(-0.45, -2.3), (-0.3, -2.65), (0.3, -2.65), (0.45, -2.3)]]
    f, h = face(0, 1.0, 1.0, "open")
    shine = [arc(0, 1.2, 1.4, math.radians(120), math.radians(160), 8)]
    rays = [[(2.3 * math.cos(a), 1.1 + 2.3 * math.sin(a)), (2.85 * math.cos(a), 1.1 + 2.85 * math.sin(a))] for a in [math.radians(d) for d in (0, 35, 70, 110, 145, 180)]]
    return make("Kawaii Lightbulb with a Bright Idea", [bulb] + base + tip + f + shine + rays, h)


@design("kawaii_alarm_clock", T)
def alarm_clock(rng):
    body = circle(0, -0.2, 2.1, 100)
    rim = circle(0, -0.2, 1.8, 90)
    bells = [arc(sx * 1.45, 1.9, 0.75, math.radians(-10 if sx > 0 else 10), math.radians(190 if sx > 0 else 170), 20) for sx in (1, -1)]
    bells = [chain(arc(sx * 1.45, 1.85, 0.72, 0, math.pi, 20), [(sx * 1.45 - 0.72, 1.85)]) for sx in (1, -1)]
    bells = [transform(b, dx=0, dy=0) for b in bells]
    bells = hide(bells, body)
    hammer = [[(0, 1.9), (0, 2.45)], circle(0, 2.6, 0.17, 12)]
    legs = [[(-1.3, -1.85), (-1.8, -2.75)], [(1.3, -1.85), (1.8, -2.75)]]
    ticks = [[(1.55 * math.cos(a), -0.2 + 1.55 * math.sin(a)), (1.75 * math.cos(a), -0.2 + 1.75 * math.sin(a))] for a in [k * math.pi / 2 for k in range(4)]]
    hands = [[(0, -0.2), (0, 0.95)], [(0, -0.2), (0.7, -0.2)]][:0]
    f, h = face(0, -0.35, 1.0, "open")
    zz = [[(2.3, 1.0), (2.65, 1.0), (2.3, 0.65), (2.65, 0.65)], [(2.6, 1.6), (3.0, 1.6), (2.6, 1.2), (3.0, 1.2)]]
    lines = [[(-2.6, 1.2), (-2.25, 1.0)], [(-2.75, 0.5), (-2.35, 0.45)], [(-2.6, -0.2), (-2.3, -0.05)]]
    return make("Kawaii Alarm Clock", [body, rim] + bells + hammer + legs + ticks + hands + f + lines, h)


@design("kawaii_retro_tv", T)
def retro_tv(rng):
    box = rrect(-2.8, -1.9, 2.8, 1.6, 0.4)
    screen = rrect(-2.35, -1.5, 1.0, 1.2, 0.5)
    knobs = [circle(1.9, 0.6, 0.35, 22), circle(1.9, -0.35, 0.35, 22), [(1.9, 0.6), (2.1, 0.8)], [(1.9, -0.35), (1.7, -0.15)]]
    grille = [[(1.5, y), (2.3, y)] for y in (-1.0, -1.25, -1.5)][:2]
    ant = [[(-0.2, 1.6), (-1.3, 3.0)], [(0.2, 1.6), (1.3, 3.0)], circle(-1.35, 3.07, 0.12, 10), circle(1.35, 3.07, 0.12, 10)]
    base = [chain(arc(0, 1.6, 0.45, 0, math.pi, 12))]
    legs = [[(-2.0, -1.9), (-2.3, -2.7)], [(2.0, -1.9), (2.3, -2.7)]]
    f, h = face(-0.68, -0.1, 0.95)
    hearts = [heart(-2.0, 0.8, 0.22)]
    return make("Kawaii Retro Television", [box, screen] + knobs + grille + ant + base + legs + f, h)


@design("kawaii_crayons", T)
def crayons(rng):
    box = poly((-2.4, -2.9), (2.4, -2.9), (2.4, 0.6), (-2.4, 0.6))
    flap = poly((-2.4, 0.6), (-1.8, 1.0), (1.8, 1.0), (2.4, 0.6), closed=False)
    cray = []
    for k, x in enumerate([-1.8, -1.0, -0.2, 0.6, 1.4]):
        top = 2.2 + 0.35 * (k % 2) + 0.15 * (k == 2)
        c = [poly((x, 0.6), (x, top), (x + 0.12, top + 0.25), (x + 0.3, top + 0.7), (x + 0.48, top + 0.25), (x + 0.6, top), (x + 0.6, 0.6),
                  closed=False), [(x, top), (x + 0.6, top)], [(x, top - 0.4), (x + 0.6, top - 0.4)]]
        cray += c
    cray = hide(cray, poly((-2.4, 0.6), (-1.8, 1.0), (1.8, 1.0), (2.4, 0.6), (2.4, -2.9), (-2.4, -2.9)))
    f, h = face(0, -1.3, 1.05)
    stripe = [[(-2.4, -0.1), (2.4, -0.1)]]
    doodle = [star(2.8, 2.0, 0.3), spl([(-2.9, 1.5), (-2.6, 1.9), (-2.3, 1.5), (-2.0, 1.9)], closed=False)]
    return make("Kawaii Crayon Box", [box, flap] + cray + f + stripe + doodle, h)


@design("kawaii_bandages", T)
def bandages(rng):
    def band(dx, dy, rot, m):
        out = rrect(-2.6, -0.65, 2.6, 0.65, 0.65)
        pad = rrect(-0.9, -0.5, 0.9, 0.5, 0.15)
        dots = [circle(x, y, 0.07, 8) for x in (-2.0, -1.5) for y in (-0.25, 0.25)] + [circle(x, y, 0.07, 8) for x in (1.5, 2.0) for y in (-0.25, 0.25)]
        f, h = face(0, 0.02, 0.55, m, spread=0.32)
        st = [transform(p, dx=dx, dy=dy, rot=rot) for p in [out, pad] + dots + f]
        hh = [transform(p, dx=dx, dy=dy, rot=rot) for p in h]
        return st, hh, transform(out, dx=dx, dy=dy, rot=rot)
    a, ha, oa = band(0.0, 0.0, 0.6, "smile")
    b, hb, ob = band(0.0, 0.0, -0.6, "open")
    b = hide(b, oa)
    hb = [x for x in hb if not inside_poly(oa)(x[0])]
    hearts = [heart(-2.2, -2.4, 0.3), heart(2.3, -2.3, 0.3)]
    return make("Kawaii Bandage Buddies", a + b + hearts, ha + hb)


@design("kawaii_toothbrush", T)
def toothbrush(rng):
    tube_ = spl([(-2.6, -2.5, 0), (-0.4, -2.5, 0), (-0.4, 0.4, 0), (-0.9, 0.85), (-2.1, 0.85), (-2.6, 0.4, 0)])
    tube_ = poly((-2.6, -2.2), (-0.5, -2.2), (-0.7, 0.9), (-2.4, 0.9))
    crimp = [rect(-2.75, -2.6, -0.35, -2.2)] + [[(x, -2.6), (x, -2.2)] for x in (-2.2, -1.55, -0.9)]
    cap = [rect(-1.9, 0.9, -1.2, 1.5), [(-1.9, 1.2), (-1.2, 1.2)]]
    f, h = face(-1.55, -0.6, 0.75)
    handle = transform(rrect(-0.3, -3.0, 0.3, 1.2, 0.3), dx=1.5, dy=0.0, rot=0.0)
    head = rrect(1.15, 1.2, 1.85, 2.4, 0.2)
    bristles = [rect(0.75, 1.3, 1.15, 2.3)] + [[(0.75, y), (1.15, y)] for y in (1.55, 1.8, 2.05)]
    bf, bh = face(1.5, -0.6, 0.5, spread=0.25)
    paste = [spl([(0.75, 2.0), (0.35, 2.3), (0.4, 2.7), (0.75, 2.6), (0.6, 2.9)], closed=False)]
    bubbles = [circle(x, y, r, 14) for x, y, r in [(2.6, 2.3, 0.25), (2.7, 1.5, 0.18), (0.0, -2.8, 0.2)]]
    return make("Kawaii Toothbrush and Toothpaste", [tube_] + crimp + cap + f + [handle, head] + bristles + bf + bubbles, h + bh)


@design("kawaii_tissue_box", T)
def tissue_box(rng):
    front = rect(-2.4, -2.6, 1.6, 0.4)
    top = poly((-2.4, 0.4), (-1.6, 1.2), (2.4, 1.2), (1.6, 0.4), closed=False)
    side = poly((1.6, -2.6), (2.4, -1.8), (2.4, 1.2), closed=False)
    slot = ellipse(0.0, 0.8, 1.2, 0.2, 40)
    tissue = spl([(-1.0, 0.8), (-1.2, 1.6), (-0.6, 2.4), (0.1, 2.9), (0.4, 2.3), (1.0, 2.6), (0.8, 1.6), (1.0, 0.8)], closed=False)
    fold = [spl([(0.1, 2.9), (0.0, 2.0), (-0.2, 1.1)], closed=False)]
    slot_v = hide([slot], poly(*tissue))
    f, h = face(-0.4, -1.1, 1.0)
    pattern = [heart(-1.9, 0.0, 0.2), heart(1.1, -2.2, 0.2)]
    return make("Kawaii Tissue Box", [front, top, side] + slot_v + [tissue] + fold + f + pattern, h)


@design("kawaii_vending_machine", T)
def vending_machine(rng):
    body = rect(-2.0, -3.0, 2.0, 3.0)
    top = [rect(-2.0, 2.4, 2.0, 3.0)]
    win = [rect(-1.7, 0.2, 1.7, 2.2)]
    bottles = []
    for row, y in enumerate((1.25, 0.25)):
        for k in range(4):
            x = -1.3 + 0.85 * k
            bottles.append(chain([(x - 0.2, y), (x - 0.2, y + 0.55)], [(x - 0.1, y + 0.75), (x - 0.1, y + 0.85), (x + 0.1, y + 0.85), (x + 0.1, y + 0.75)],
                                 [(x + 0.2, y + 0.55), (x + 0.2, y), (x - 0.2, y)]))
    shelf = [[(-1.7, 1.2), (1.7, 1.2)]]
    buttons = [circle(-1.3 + 0.85 * k, 0.0, 0.1, 8) for k in range(4)][:0]
    slot = [rrect(-1.6, -2.7, 0.4, -2.1, 0.12)]
    coin = [rrect(1.0, -1.05, 1.5, -0.25, 0.1), [(1.25, -0.85), (1.25, -0.45)]]
    f, h = face(-0.5, -1.0, 0.85)
    return make("Kawaii Drink Vending Machine", [body] + top + win + bottles + shelf + slot + coin + f, h)


# dropped: the subject repeats another book
def folding_fan(rng):
    cx, cy = 0.0, -2.3
    R, r = 4.4, 1.2
    a0, a1 = math.radians(20), math.radians(160)
    outer = arc(cx, cy, R, a0, a1, 80)
    inner = arc(cx, cy, r, a0, a1, 20)
    n = 9
    ribs = [[(cx + r * math.cos(a), cy + r * math.sin(a)), (cx + R * math.cos(a), cy + R * math.sin(a))] for a in [a0 + (a1 - a0) * k / n for k in range(n + 1)]]
    pivot = [circle(cx, cy, 0.18, 12)]
    sticks = [[(cx, cy), (cx + r * math.cos(a0), cy + r * math.sin(a0))], [(cx, cy), (cx + r * math.cos(a1), cy + r * math.sin(a1))]]
    tassel = [[(cx, cy - 0.18), (cx, cy - 0.6)], poly((cx - 0.15, cy - 0.6), (cx + 0.15, cy - 0.6), (cx + 0.25, cy - 1.0), (cx - 0.25, cy - 1.0))]
    clear = ellipse(0.0, 0.3, 1.45, 0.85, 40)
    ribs = hide(ribs, clear)
    f, h = face(0.0, 0.4, 1.1)
    petals = [circle(-2.1 + 0.42 * math.cos(a), 0.9 + 0.42 * math.sin(a), 0.26, 16) for a in [k * TAU / 5 + 0.3 for k in range(5)]]
    blossom = [circle(-2.1, 0.9, 0.2, 14)] + [p_ for i, p_ in enumerate(petals) for p_ in hide([p_], *petals[i + 1:])]
    blossom = hide(blossom[1:], blossom[0]) + blossom[:1]
    ribs = hide(ribs, *petals)
    return make("Kawaii Folding Fan", [outer, inner] + ribs + pivot + sticks + tassel + f + blossom, h)


@design("kawaii_kendama", T)
def kendama(rng):
    cup_big = [chain(arc(0, 0.9, 0.95, math.pi, TAU, 20)), [(-0.95, 0.9), (0.95, 0.9)]]
    cross = [rect(-0.95, 0.9, 0.95, 1.4)]
    ends = [chain([(-0.95, 1.15)], arc(-1.25, 1.15, 0.3, 0, math.pi * 2, 16)), chain([(0.95, 1.15)], arc(1.25, 1.15, 0.3, math.pi, math.pi * 3, 16))]
    ends = [ellipse(-1.25, 1.15, 0.3, 0.42, 20), ellipse(1.25, 1.15, 0.3, 0.42, 20)]
    handle = [rect(-0.25, -2.6, 0.25, -0.05)]
    small_cup = [chain([(-0.45, -2.6)], arc(0, -2.6, 0.45, math.pi, TAU, 12)[1:], [(0.45, -2.6)])]
    spike = [poly((-0.15, 1.4), (0.0, 1.85), (0.15, 1.4), closed=False)]
    ball = circle(1.9, 2.3, 0.95, 60)
    f, h = face(1.9, 2.25, 0.65)
    hole = [circle(1.9, 1.38, 0.12, 10)]
    string = [spl([(0.25, -1.2), (1.3, -0.9), (2.2, 0.0), (2.0, 1.35)], closed=False)]
    stripe = [arc(1.9, 2.3, 0.95, math.radians(200), math.radians(340), 20)][:0]
    return make("Kawaii Kendama Toy", cup_big + cross + ends + handle + small_cup + spike + [ball] + f + string, h)


@design("kawaii_virtual_pet", T)
def virtual_pet(rng):
    egg = spl([(0, 2.6), (1.5, 1.9), (2.2, 0.2), (1.8, -1.7), (0, -2.6), (-1.8, -1.7), (-2.2, 0.2), (-1.5, 1.9)])
    screen = rrect(-1.2, -0.6, 1.2, 1.4, 0.2)
    pixels = []
    px = 0.2
    pattern = ["..XX..", ".X..X.", "X.X.X.", "X....X", ".XXXX."][:0]
    critter = [rect(-0.5, -0.2, 0.5, 0.6), rect(-0.3, 0.6, -0.1, 0.8), rect(0.1, 0.6, 0.3, 0.8), [(-0.5, -0.2), (-0.5, -0.4)], [(0.5, -0.2), (0.5, -0.4)]]
    pix_eyes = [rect(-0.3, 0.25, -0.15, 0.4), rect(0.15, 0.25, 0.3, 0.4)]
    btns = [circle(x, -1.3, 0.25, 18) for x in (-0.75, 0.0, 0.75)]
    ring = [circle(0, 3.0, 0.4, 28), circle(0, 3.0, 0.25, 20)][:1]
    f, h = face(0, 1.95, 0.55, spread=0.35)
    hearts = [heart(-2.4, 2.2, 0.3), heart(2.5, -2.2, 0.3)]
    return make("Kawaii Virtual Pet Toy", [egg, screen] + critter + pix_eyes + btns + ring + hide(f, ring[0]) + hearts, h)


# dropped: the subject repeats another book
def gachapon(rng):
    globe = circle(0, 1.2, 1.75, 90)
    cap = [chain(arc(0, 2.95, 0.6, 0, math.pi, 14), [(0.6, 2.95)])]
    cap = hide(cap, globe)
    base = poly((-1.8, -0.55), (1.8, -0.55), (2.0, -2.9), (-2.0, -2.9))
    collar = [rrect(-1.9, -0.75, 1.9, -0.35, 0.12)]
    globe_v = hide([globe], collar[0])
    caps = []
    for x, y, r in [(-0.9, 0.3, 0.42), (0.0, 0.25, 0.42), (0.9, 0.35, 0.42), (-0.5, 1.0, 0.42), (0.45, 1.05, 0.42), (-1.0, 1.65, 0.38), (0.0, 1.8, 0.4), (0.95, 1.7, 0.38)]:
        caps += [circle(x, y, r, 24), [(x - r, y), (x + r, y)]]
    vis = []
    shapes = [c for c in caps if len(c) > 2]
    caps = hide(caps, collar[0])
    knob = [circle(0, -1.5, 0.5, 30), rect(-0.12, -1.95, 0.12, -1.05)]
    chute = [rrect(-0.7, -2.7, 0.7, -2.25, 0.15)]
    f, h = face(-1.25, -1.5, 0.45, spread=0.25)
    f2, h2 = face(1.25, -1.5, 0.45, spread=0.25)
    return make("Kawaii Gachapon Capsule Machine", globe_v + cap + [base] + collar + caps + knob + chute + f + f2, h + h2)


@design("kawaii_claw_machine", T)
def claw_machine(rng):
    cab = rect(-2.4, -3.0, 2.4, 3.0)
    roof = [rect(-2.4, 2.3, 2.4, 3.0)]
    glass = [rect(-2.1, -0.3, 2.1, 2.1)]
    rail = [[(-2.1, 1.9), (2.1, 1.9)]]
    cable = [[(0.6, 1.9), (0.6, 1.2)]]
    claw = [rect(0.4, 1.0, 0.8, 1.2), spl([(0.45, 1.0), (0.2, 0.7), (0.35, 0.45)], closed=False), spl([(0.75, 1.0), (1.0, 0.7), (0.85, 0.45)], closed=False)]
    plush = []
    hints = []
    for x, kind in [(-1.3, "bear"), (0.0, "bunny"), (1.3, "bear")]:
        head = circle(x, 0.25, 0.5, 30)
        plush.append(head)
        if kind == "bear":
            plush += hide([circle(x + sx * 0.38, 0.65, 0.17, 12) for sx in (1, -1)], head)
        else:
            plush += hide([lens((x + sx * 0.18, 0.6), (x + sx * 0.25, 1.35), 0.3, 12) for sx in (1, -1)], head)
        ff, hh = face(x, 0.25, 0.4, spread=0.22)
        plush += ff
        hints += hh
    plush = hide(plush, claw[0])
    floor = [[(-2.1, -0.15), (2.1, -0.15)]]
    plush = [p for p in plush]
    panel = [rect(-2.4, -1.4, 2.4, -0.3)]
    joy = [circle(-1.2, -0.6, 0.22, 16), [(-1.2, -0.82), (-1.2, -1.15)], rect(-1.45, -1.3, -0.95, -1.15)]
    btn = [circle(1.0, -0.85, 0.25, 18)]
    door = [rrect(-0.9, -2.7, 0.9, -1.8, 0.15)]
    sign = [heart(0.0, 2.6, 0.28), star(-1.4, 2.65, 0.25), star(1.4, 2.65, 0.25)]
    return make("Kawaii Claw Machine with Plushies", [cab] + roof + glass + rail + cable + claw + plush + panel + joy + btn + door + sign, hints)


@design("kawaii_washi_tape", T)
def washi_tape(rng):
    out, hints = [], []
    for cx, cy, R, m in [(-1.2, 0.8, 1.55, "smile"), (1.5, -1.2, 1.3, "open")]:
        out += [circle(cx, cy, R, 80), circle(cx, cy, R * 0.5, 40)]
        f, h = face(cx, cy - R * 0.72, R * 0.35, m, spread=0.5)
        out += [circle(cx + R * 0.75 * math.cos(a), cy + R * 0.75 * math.sin(a), 0.1, 8) for a in [k * TAU / 10 + 0.2 for k in range(10)]
                if not (3.6 < a < 5.8)]
        out += f
        hints += h
    strip = poly((-1.2 + 1.55, 0.8), (2.9, 1.3), (2.75, 2.45), (-1.2 + 1.35, 1.6), closed=False)
    zig = zigzag(2.8, 2.95, 1.9, 0.0, 1)[:0]
    tear = [(2.9, 1.3), (2.95, 1.55), (2.82, 1.75), (2.95, 1.95), (2.82, 2.2), (2.9, 2.45)][:0]
    hearts_ = [heart(1.4, 1.45, 0.2), heart(2.3, 1.75, 0.2)]
    out = hide(out, circle(1.5, -1.2, 1.3, 80))[:0] + out
    big = circle(1.5, -1.2, 1.3, 80)
    first = [s_ for s_ in out[:len(out)]]
    return make("Kawaii Washi Tape Rolls", out + [strip] + hearts_, hints)


@design("kawaii_paint_palette", T)
def paint_palette(rng):
    pal = spl([(-2.7, 0.2), (-2.3, 1.7), (-0.8, 2.5), (1.0, 2.4), (2.5, 1.5), (2.8, 0.0), (2.2, -1.5), (1.0, -1.9), (0.2, -1.5),
               (-0.3, -0.8), (-1.1, -1.4), (-2.2, -1.1)])
    thumb = ellipse(-1.3, -0.2, 0.45, 0.35, 24)
    blobs = [bumpy(x, y, 0.42, 0.36, 5, 0.12) for x, y in [(-1.4, 1.4), (0.0, 1.85), (1.4, 1.55), (2.05, 0.35)]]
    f, h = face(0.5, 0.0, 0.85)
    brush = [tube([(0.4, -2.9), (2.9, -1.2)], 0.22)]
    ferrule = transform(rect(-0.25, -0.17, 0.25, 0.17), dx=1.15, dy=-2.4, rot=math.atan2(1.7, 2.5))
    tipb = lens((1.4, -2.22), (2.1, -1.75), 0.3, 12)
    brush = [tube([(-0.6, -3.3), (0.95, -2.55)], 0.22), ferrule, tipb]
    return make("Kawaii Paint Palette and Brush", [pal, thumb] + blobs + f + brush, h)


@design("kawaii_post_box", T)
def post_box(rng):
    body = [[(-1.5, -2.6), (-1.5, 1.4)], [(1.5, -2.6), (1.5, 1.4)]]
    cap = [chain([(-1.75, 1.4)], arc(0, 1.4, 1.75, math.pi, 0, 40)[1:], [(1.75, 1.4)]), [(-1.75, 1.4), (1.75, 1.4)]]
    cap = [[(x, 1.4 + (y - 1.4) * 0.55) for x, y in cap[0]], [(-1.75, 1.4), (1.75, 1.4)], [(-1.75, 1.15), (1.75, 1.15)], [(-1.75, 1.15), (-1.75, 1.4)], [(1.75, 1.15), (1.75, 1.4)]]
    slot = [rrect(-0.9, 0.35, 0.9, 0.65, 0.12)]
    plate = [rrect(-0.75, -2.0, 0.75, -1.2, 0.1)]
    sym_ = [[(-0.35, -1.4), (0.35, -1.4)], [(-0.35, -1.6), (0.35, -1.6)], [(0.0, -1.6), (0.0, -1.85)]]
    base = [rect(-1.8, -3.0, 1.8, -2.6)]
    f, h = face(0, -0.35, 0.95)
    letter = [rect(1.9, 1.9, 3.0, 2.6), [(1.9, 2.6), (2.45, 2.2), (3.0, 2.6)]]
    hrt = [heart(-2.4, 2.2, 0.3)]
    return make("Kawaii Japanese Post Box", body + cap + slot + plate + sym_ + base + f + letter + hrt, h)
