"""Small Pets niche: hamsters, guinea pigs, rabbits, rodents, cage birds,
fish, reptiles and their homes (no cats or dogs - they have their own books)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "pets"


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


def sides(center, w):
    """The two edges of a band along `center` (no end caps), as two strokes."""
    band = tube(center, w, cap=False)
    n = len(center)
    return [band[:n], band[n:][::-1]]


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


def pt(p, dx=0.0, dy=0.0, s=1.0, flip=False, rot=0.0):
    return tf([[p]], dx, dy, s, flip, rot)[0][0]


def bumpy(cx, cy, rx, ry, k, a=0.13, n=None, rot=0.0):
    """Scalloped fluffy outline with k bumps."""
    n = n or k * 14
    pts = []
    for i in range(n + 1):
        t = rot + TAU * i / n
        r = 1 - a * (1 - abs(math.sin(k * (t - rot) / 2)))
        pts.append((cx + rx * r * math.cos(t), cy + ry * r * math.sin(t)))
    return pts


def grass(x, y, s=1.0):
    return [quad((x, y), (x + dx * 0.4 * s, y + h * 0.6 * s), (x + dx * s, y + h * s), 10)
            for dx, h in [(-0.35, 0.55), (0.0, 0.75), (0.35, 0.55)]]


def seed(cx, cy, L=0.45, rot=0.0):
    """Sunflower seed with its stripe."""
    a = (cx - L / 2 * math.cos(rot), cy - L / 2 * math.sin(rot))
    b = (cx + L / 2 * math.cos(rot), cy + L / 2 * math.sin(rot))
    return [lens(a, b, 0.28, 12)]


def bedding(x0, x1, y, k=9, amp=0.18):
    """Wavy shredded bedding along the floor."""
    pts = []
    for i in range(k * 2 + 1):
        x = x0 + (x1 - x0) * i / (2 * k)
        pts.append((x, y + (amp if i % 2 else 0.0)))
    return spl(pts, closed=False, res=10)


# ---------------------------------------------------------- shared animals

def run_hamster():
    """Hamster trotting to the right; front toe at (1.12, 0)."""
    body = spl([(1.56, 0.95), (1.42, 1.35), (1.0, 1.72), (0.2, 1.95), (-0.6, 1.85), (-1.15, 1.4), (-1.32, 0.85), (-1.3, 0.55),
                (-1.42, 0.38), (-1.5, 0.26, 0), (-1.1, 0.25, 0), (-0.92, 0.38), (-0.4, 0.32), (0.3, 0.32), (0.72, 0.36),
                (0.92, 0.12), (1.1, 0.0, 0), (1.3, 0.08, 0), (1.17, 0.36), (1.22, 0.58), (1.45, 0.76)])
    ear = spl([(0.66, 1.84), (0.62, 2.16), (0.92, 2.28), (1.13, 2.0), (1.1, 1.66)], closed=False)
    inner = spl([(0.76, 1.85), (0.77, 2.08), (0.95, 2.12), (1.03, 1.86)], closed=False)
    belly = spl([(1.2, 0.62), (0.5, 0.82), (-0.3, 0.72), (-0.95, 0.9), (-1.28, 1.05)], closed=False)
    wh = [[(1.48, 0.92), (1.95, 1.06)], [(1.48, 0.86), (1.95, 0.76)]]
    return body, [ear, inner, belly] + wh, [eye(1.15, 1.25, 0.11), eye(1.56, 0.95, 0.06)]


def front_hamster(cheeks=False):
    """Hamster sitting facing us; base at y=0, about 2.8 tall, 2.5 wide."""
    half = [(0, 2.4), (0.5, 2.35), (0.88, 2.12), (1.08, 1.75), (1.15, 1.3), (1.25, 0.8), (1.25, 0.35), (1.0, 0.06), (0.5, -0.02),
            (0, -0.02)]
    body = sym(half)
    ears = []
    for sx in (1, -1):
        ears.append(spl([(sx * 0.48, 2.36), (sx * 0.5, 2.7), (sx * 0.78, 2.82), (sx * 1.0, 2.62), (sx * 0.9, 2.12)], closed=False))
        ears.append(spl([(sx * 0.62, 2.4), (sx * 0.65, 2.6), (sx * 0.8, 2.65), (sx * 0.86, 2.38)], closed=False))
    nose = poly((-0.1, 1.62), (0.1, 1.62), (0, 1.5))
    mouth = [spl([(-0.22, 1.32), (-0.1, 1.3), (0, 1.5), (0.1, 1.3), (0.22, 1.32)], closed=False)]
    paws = [ellipse(sx * 0.3, 1.0, 0.2, 0.15, 16) for sx in (1, -1)]
    feet = [ellipse(sx * 0.62, 0.05, 0.3, 0.13, 18) for sx in (1, -1)]
    belly = spl([(-0.7, 1.2), (-0.8, 0.5), (0, 0.28), (0.8, 0.5), (0.7, 1.2)], closed=False)
    wh = [[(sx * 0.3, 1.52), (sx * 0.95, 1.62)] for sx in (1, -1)] + [[(sx * 0.3, 1.45), (sx * 0.95, 1.33)] for sx in (1, -1)]
    masks = [body]
    if cheeks:
        pouch = [circle(sx * 1.05, 1.35, 0.62, 40) for sx in (1, -1)]
        body_out = hide([body], *pouch) + pouch
        masks += pouch
        wh = [[(sx * 0.3, 1.52), (sx * 0.75, 1.6)] for sx in (1, -1)] + [[(sx * 0.3, 1.45), (sx * 0.75, 1.36)] for sx in (1, -1)]
    else:
        body_out = [body]
    eyes = [eye(sx * 0.42, 1.85, 0.11) for sx in (1, -1)]
    det = ears + [nose] + mouth + hide([belly] + wh, *paws) + paws
    det = hide(det, *feet) + feet
    return body_out, det, eyes, masks


def guinea_pig():
    """Guinea pig standing, facing right; feet at y=0, about 3.2 long."""
    body = spl([(1.65, 0.55), (1.6, 0.85), (1.35, 1.2), (0.9, 1.45), (0.2, 1.55), (-0.6, 1.5), (-1.2, 1.25), (-1.55, 0.8),
                (-1.55, 0.35), (-1.3, 0.12), (-1.1, 0.02, 0), (-0.75, 0.02, 0), (-0.6, 0.12), (0.4, 0.12), (0.62, 0.02, 0),
                (0.95, 0.02, 0), (1.05, 0.15), (1.35, 0.22), (1.6, 0.35)])
    ear = spl([(0.7, 1.42), (0.62, 1.66), (0.82, 1.8), (1.05, 1.62), (0.98, 1.38)], closed=False)
    ear_in = spl([(0.75, 1.5), (0.85, 1.65), (0.95, 1.52)], closed=False)
    patch = spl([(0.55, 1.47), (0.35, 0.9), (0.55, 0.35), (0.62, 0.13)], closed=False)
    mouth = spl([(1.62, 0.42), (1.5, 0.38), (1.45, 0.28)], closed=False)
    wh = [[(1.55, 0.6), (2.0, 0.72)], [(1.55, 0.55), (2.0, 0.45)]]
    toes = [[(0.78, 0.02), (0.78, 0.12)], [(-0.92, 0.02), (-0.92, 0.12)]]
    return body, [ear, ear_in, patch, mouth] + wh + toes, [eye(1.15, 0.95, 0.11), eye(1.62, 0.66, 0.05)]


def rabbit(ears="up"):
    """Rabbit sitting, facing right; feet at y=0."""
    body = spl([(1.55, 1.75), (1.45, 2.1), (1.15, 2.35), (0.7, 2.35), (0.35, 2.05), (-0.2, 1.75), (-0.9, 1.55), (-1.45, 1.05),
                (-1.6, 0.45), (-1.4, 0.05), (-0.9, 0.0, 0), (0.2, 0.0, 0), (0.1, 0.25), (0.55, 0.35), (0.6, 0.02, 0),
                (0.95, 0.0, 0), (0.95, 0.25), (0.75, 0.75), (0.9, 1.25), (1.2, 1.4), (1.5, 1.55)])
    tail = spl([(-1.45, 0.75), (-1.8, 0.85), (-1.9, 0.5), (-1.55, 0.3)], closed=False)
    haunch = spl([(-0.2, 0.0), (-0.75, 0.25), (-0.9, 0.75), (-0.5, 1.1), (0.0, 0.95), (0.15, 0.55)], closed=False)
    nose = spl([(1.55, 1.75), (1.45, 1.7), (1.4, 1.6)], closed=False)
    wh = [[(1.45, 1.75), (1.95, 1.9)], [(1.45, 1.7), (1.95, 1.6)]]
    if ears == "up":
        e = [spl([(0.75, 2.33), (0.6, 2.9), (0.55, 3.5), (0.75, 3.75), (0.95, 3.5), (1.0, 2.9), (1.0, 2.38)], closed=False),
             spl([(0.75, 2.6), (0.72, 3.2), (0.77, 3.5), (0.86, 3.2), (0.87, 2.6)], closed=False),
             spl([(0.5, 2.25), (0.25, 2.8), (0.12, 3.3), (0.3, 3.5), (0.5, 3.15), (0.68, 2.6)], closed=False)]
    elif ears == "back":
        e = [spl([(0.95, 2.36), (0.5, 2.7), (-0.3, 2.85), (-0.75, 2.75), (-0.5, 2.5), (0.1, 2.32), (0.45, 2.15)], closed=False),
             spl([(0.6, 2.42), (0.1, 2.6), (-0.45, 2.66)], closed=False)]
    else:  # lop
        e = [spl([(0.95, 2.36), (0.65, 2.45), (0.3, 2.2), (0.15, 1.5), (0.2, 0.95), (0.45, 0.85), (0.62, 1.2), (0.68, 1.8),
                  (0.85, 2.15)], closed=False),
             spl([(0.48, 2.05), (0.35, 1.5), (0.42, 1.05)], closed=False)]
    return body, [tail, haunch, nose] + wh + e, [eye(1.12, 1.98, 0.11)]


# ------------------------------------------------------------------ hamsters

@design("pets_hamster_wheel", T)
def hamster_wheel(rng):
    cx, cy, R, r = 0.0, 0.4, 2.55, 2.28
    hb, hd, he = run_hamster()
    s = 0.95
    hb, hd, he = tf([hb], -0.05, -1.58, s)[0], tf(hd, -0.05, -1.58, s), tf(he, -0.05, -1.58, s)
    spokes = [[(cx + 0.28 * math.cos(a), cy + 0.28 * math.sin(a)), (cx + r * math.cos(a), cy + r * math.sin(a))]
              for a in [math.pi / 2 + k * math.pi / 3 for k in range(6)]]
    rungs = [[(cx + r * math.cos(a), cy + r * math.sin(a)), (cx + R * math.cos(a), cy + R * math.sin(a))]
             for a in [k * TAU / 28 for k in range(28)]]
    rim = [circle(cx, cy, R, 140), circle(cx, cy, r, 130), circle(cx, cy, 0.28, 18)]
    legs = [[(cx + R * math.cos(a), cy + R * math.sin(a)), (bx, -2.75)] for a, bx in [(math.radians(-120), -1.75), (math.radians(-60), 1.75)]]
    base = [rrect(-2.4, -3.05, 2.4, -2.75, 0.12)]
    spin = [arc(cx, cy, 2.95, math.radians(100), math.radians(150), 20), poly((-1.68, 2.85), (-1.88, 2.62), (-1.6, 2.55), closed=False)]
    behind = hide(spokes + [rim[1]], hb)
    return make("Hamster Running in a Wheel", [hb, rim[0], rim[2]] + behind + rungs + hd + legs + base + spin, he)


@design("pets_hamster_cheeks", T)
def hamster_cheeks(rng):
    s, dy = 1.2, -2.5
    body, det, eyes, masks = front_hamster(cheeks=True)
    body, det, eyes = tf(body, 0, dy, s), tf(det, 0, dy, s), tf(eyes, 0, dy, s)
    sd = []
    for x, y, a in [(-2.5, -2.3, 0.4), (2.4, -2.1, -0.6), (2.7, -2.7, 0.2), (-2.1, -2.8, -0.3), (2.6, 0.6, 1.2), (-2.7, 1.0, -0.9)]:
        sd += seed(x, y, 0.5, a)
    seedheld = lens((0, -0.85), (0.0, -1.6), 0.32, 12)
    pawz = [ellipse(sx * 0.36, -1.35, 0.25, 0.19, 16) for sx in (1, -1)]
    det = hide(det, seedheld, *pawz) + hide([seedheld], *pawz) + pawz
    return make("Hamster with Stuffed Cheeks", body + det + sd + [[(-3.0, -2.6), (3.0, -2.6)]], eyes)


@design("pets_hamster_ball", T)
def hamster_ball(rng):
    cx, cy, R = 0.0, 0.3, 2.45
    hb, hd, he = run_hamster()
    s = 1.05
    hb, hd, he = tf([hb], -0.15, -1.75, s)[0], tf(hd, -0.15, -1.75, s), tf(he, -0.15, -1.75, s)
    slots = []
    for k in range(16):
        a = math.pi / 2 + k * TAU / 16
        slots.append(tube(arc(cx, cy, 2.0, a - 0.09, a + 0.09, 6), 0.18))
    ring = [circle(cx, cy, R, 160), circle(cx, cy, R - 0.14, 150)]
    lid = [circle(cx, cy + 1.0, 0.55, 40), circle(cx, cy + 1.0, 0.4, 30)]
    inner = hide(slots, hb)
    floor = [[(-3.2, -2.15), (3.2, -2.15)]]
    motion = [[(-3.3, y), (-2.75, y)] for y in (0.9, 0.3, -0.3)]
    return make("Hamster Rolling in an Exercise Ball", [hb] + hd + ring + inner + lid + floor + motion, he)


@design("pets_hamster_hideout", T)
def hamster_hideout(rng):
    front = poly((-2.3, -2.4), (2.3, -2.4), (2.3, 0.7), (-2.3, 0.7))
    roof = poly((-2.8, 0.5), (0, 2.75), (2.8, 0.5), (2.55, 0.25), (0, 2.3), (-2.55, 0.25))
    door = chain([(-1.15, -2.4), (-1.15, -0.6)], arc(0, -0.6, 1.15, math.pi, 0, 30), [(1.15, -2.4)])
    body, det, eyes, masks = front_hamster()
    s, dy = 0.85, -2.5
    body, det, eyes, masks = tf(body, 0, dy, s), tf(det, 0, dy, s), tf(eyes, 0, dy, s), tf(masks, 0, dy, s)
    cut = poly((-3, -1.45), (3, -1.45), (3, 3), (-3, 3))
    head = keep_in(body, cut)
    planks = [[(-2.3, y), (2.3, y)] for y in (-1.6, -0.8, 0.0)]
    planks = hide(planks, chain(door[:-1], [(1.15, -2.4), (-1.15, -2.4)]))
    window = [circle(0, 1.25, 0.45, 30), [(-0.45, 1.25), (0.45, 1.25)], [(0, 0.8), (0, 1.7)]]
    pawz = [ellipse(sx * 0.42, -1.45, 0.26, 0.17, 16) for sx in (1, -1)]
    sill = [[(-1.15, -1.45), (1.15, -1.45)]]
    hd = hide(keep_in(det, cut) + head, *pawz)
    door_vis = hide([door], *masks)
    chips = [rrect(x, -2.75, x + 0.42, -2.5, 0.08) for x in (-2.6, -1.9, 1.5, 2.2)]
    return make("Hamster Peeking from Its Hideout", [front, roof] + door_vis + planks + window + hide(sill, *masks, *pawz) + hd + pawz + chips,
                eyes)


@design("pets_hamster_asleep", T)
def hamster_asleep(rng):
    body = spl([(1.45, -0.2), (1.6, 0.35), (1.35, 0.95), (0.7, 1.35), (-0.2, 1.45), (-1.1, 1.15), (-1.65, 0.45), (-1.6, -0.35),
                (-1.1, -0.85), (-0.2, -1.0), (0.7, -0.92), (1.25, -0.6)])
    ear = spl([(0.65, 1.36), (0.65, 1.7), (0.95, 1.78), (1.1, 1.5), (1.05, 1.2)], closed=False)
    lid = [arc(0.92, 0.42, 0.18, math.radians(200), math.radians(340), 8)]
    nose = [arc(1.5, 0.1, 0.1, math.radians(-90), math.radians(90), 6)]
    paw = [ellipse(1.05, -0.45, 0.28, 0.18, 16)]
    tuck = spl([(-1.55, -0.1), (-0.7, 0.15), (0.3, -0.05), (0.9, -0.35)], closed=False)
    nest = spl([(-2.8, 0.2), (-2.6, -0.6), (-2.2, -1.3), (-1.2, -1.75), (0.0, -1.9), (1.2, -1.75), (2.2, -1.3), (2.6, -0.6),
                (2.8, 0.2)], closed=False)
    nest_rim = spl([(-2.8, 0.2), (-2.3, -0.45), (-1.4, -0.55), (-0.6, -0.75)], closed=False)
    nest_rim2 = spl([(1.0, -0.75), (1.8, -0.5), (2.4, -0.4), (2.8, 0.2)], closed=False)
    shreds = [spl([(x, y), (x + 0.35, y - 0.25), (x + 0.75, y - 0.1)], closed=False)
              for x, y in [(-2.3, -0.9), (-1.6, -1.3), (-0.6, -1.45), (0.5, -1.45), (1.4, -1.2), (1.9, -0.8)]]
    zs = []
    for x, y, s in [(1.9, 1.5, 0.35), (2.4, 2.1, 0.45), (3.0, 2.85, 0.55)]:
        zs.append([(x, y), (x + s, y), (x, y - s * 0.9), (x + s, y - s * 0.9)])
    body_vis = hide([body], paw[0])
    return make("Hamster Asleep in Its Nest", body_vis + [ear] + lid + nose + paw + hide([tuck], paw[0]) + [nest] +
                hide([nest_rim, nest_rim2], body) + shreds + zs)


@design("pets_hamster_tower", T)
def hamster_tower(rng):
    out, hints = [], []
    for dy, s in [(-3.0, 1.15), (-0.45, 0.95), (1.55, 0.75)]:
        b, d, e, m = front_hamster()
        b, d, e, m = tf(b, 0, dy, s), tf(d, 0, dy, s), tf(e, 0, dy, s), tf(m, 0, dy, s)
        out = hide(out, *m)
        out += b + d
        hints += e
    stars_ = [star(x, y, 0.3) for x, y in [(-2.3, 2.6), (2.2, 1.5), (-2.0, 0.2)]]
    ground = [[(-2.8, -3.05), (2.8, -3.05)]]
    return make("Tower of Three Hamsters", out + stars_ + ground, hints)


@design("pets_hamster_tube", T)
def hamster_tube(rng):
    c = cubic((-3.0, -1.8), (-1.0, -2.4), (-0.6, 1.2), (1.6, 0.9), 60)
    w = 1.3
    walls = sides(c, w)
    rings = []
    for t in (0.3, 0.55, 0.8):
        i = int(t * (len(c) - 1))
        a, b = c[i - 1], c[i + 1]
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        nx, ny = -math.sin(ang) * w / 2, math.cos(ang) * w / 2
        for o in (-0.13, 0.13):
            px, py = c[i][0] + o * math.cos(ang), c[i][1] + o * math.sin(ang)
            rings.append([(px - nx, py - ny), (px + nx, py + ny)])
    mouth = ellipse(1.6, 0.9, 0.25, w / 2, 40)
    start = ellipse(-3.0, -1.8, 0.2, w / 2, 40, rot=-0.3)
    # hamster head poking out of the end, facing right
    head = spl([(1.45, 1.45), (1.9, 1.85), (2.55, 1.85), (3.0, 1.5), (3.3, 1.05), (3.35, 0.85), (3.05, 0.55), (2.4, 0.3),
                (1.8, 0.3), (1.5, 0.45)])
    ear = spl([(1.95, 1.86), (1.9, 2.25), (2.25, 2.4), (2.5, 2.05), (2.45, 1.84)], closed=False)
    ear_in = spl([(2.05, 1.9), (2.05, 2.15), (2.25, 2.22), (2.36, 1.95)], closed=False)
    paw = [ellipse(2.4, 0.32, 0.27, 0.16, 14), ellipse(1.95, 0.34, 0.25, 0.15, 14)]
    wh = [[(3.2, 0.92), (3.7, 1.08)], [(3.2, 0.86), (3.7, 0.72)]]
    cheek = spl([(2.95, 0.62), (2.55, 0.85), (2.1, 0.7)], closed=False)
    vis = hide(walls + [mouth] + rings, head, *paw)
    head_vis = hide([head], *paw)
    floor = [[(-3.4, -2.75), (3.4, -2.75)]]
    return make("Hamster Popping Out of a Play Tube", vis + [start] + head_vis + [ear, ear_in, cheek] + paw + wh + floor,
                [eye(2.75, 1.3, 0.11), eye(3.33, 0.9, 0.06)])


# ------------------------------------------------------------------ gerbils

def gerbil():
    """Plump gerbil sitting up on its hind legs, facing right; feet at y=0, ~4 tall."""
    body = spl([(1.32, 3.0), (1.05, 3.45), (0.45, 3.65), (-0.1, 3.42), (-0.38, 3.0), (-0.75, 2.3), (-1.02, 1.4), (-1.05, 0.6),
                (-0.85, 0.12), (-0.6, 0.0, 0), (0.75, 0.0, 0), (0.78, 0.14, 0), (0.12, 0.26), (0.45, 0.62), (0.62, 1.3),
                (0.66, 1.95), (0.76, 2.42), (0.98, 2.7), (1.2, 2.86)])
    arm = spl([(0.62, 2.25), (0.98, 2.12), (1.12, 1.92), (0.95, 1.82), (0.62, 1.92)])
    ear = spl([(0.08, 3.56), (0.0, 3.95), (0.3, 4.12), (0.52, 3.85), (0.45, 3.64)], closed=False)
    ear_in = spl([(0.14, 3.62), (0.12, 3.88), (0.3, 3.97), (0.4, 3.78)], closed=False)
    thigh = spl([(-0.25, 0.28), (-0.8, 0.75), (-0.62, 1.45), (0.0, 1.5), (0.35, 0.95)], closed=False)
    belly = spl([(0.62, 1.8), (0.25, 1.55), (0.12, 1.4)], closed=False)
    tail = sides(spl([(-0.85, 0.35), (-1.5, 0.12), (-2.25, 0.15), (-2.8, 0.6), (-2.9, 1.2)], closed=False), lambda t: 0.26 - 0.14 * t)
    tuft = lens((-2.9, 1.15), (-2.95, 1.85), 0.3, 10)
    wh = [[(1.26, 3.0), (1.8, 3.18)], [(1.26, 2.93), (1.8, 2.8)]]
    return body, [ear, ear_in, thigh, belly] + hide(tail, body) + [tuft, arm] + wh, [eye(0.78, 3.15, 0.15), eye(1.32, 3.0, 0.06)]


@design("pets_gerbil_standing", T)
def gerbil_standing(rng):
    b, d, e = gerbil()
    dx, dy, s = 0.4, -2.6, 1.32
    b, d, e = tf([b], dx, dy, s)[0], tf(d, dx, dy, s), tf(e, dx, dy, s)
    arm = d[-3]
    body_vis = hide([b], arm)
    sd = seed(2.2, -2.45, 0.5, 0.2) + seed(2.6, -2.2, 0.45, -0.5) + seed(-1.8, -2.45, 0.45, 0.4)
    ground = [[(-3.2, -2.62), (3.2, -2.62)]]
    return make("Gerbil Standing on Its Hind Legs", body_vis + d + sd + ground + grass(-2.9, -2.62, 0.7) + grass(2.9, -2.62, 0.6), e)


@design("pets_gerbil_tunnels", T)
def gerbil_tunnels(rng):
    tank = [rect(-3.0, -2.6, 3.0, 1.8), [(-3.0, 1.55), (3.0, 1.55)], [(-3.0, -2.35), (3.0, -2.35)]]
    surf = spl([(-3.0, 0.2), (-2.2, 0.35), (-1.3, 0.15), (-0.3, 0.3), (0.8, 0.2), (1.9, 0.35), (3.0, 0.2)], closed=False)
    t1 = spl([(-2.0, 0.3), (-1.85, -0.4), (-1.3, -1.0), (-0.6, -1.3)], closed=False)
    t2 = spl([(0.6, -1.35), (1.3, -1.2), (1.75, -0.6), (2.0, 0.3)], closed=False)
    t3 = spl([(-0.9, -1.3), (-1.6, -1.65), (-2.4, -1.75)], closed=False)
    ch = ellipse(0.0, -1.35, 1.0, 0.6, 50)
    nest = ellipse(-2.55, -1.75, 0.45, 0.35, 30)
    walls = []
    for t in (t1, t2, t3):
        walls += sides(t, 0.55)
    walls = hide(walls, ch, nest)
    # sleeping gerbil in the chamber
    sleeper = spl([(0.55, -1.55), (0.6, -1.2), (0.3, -0.95), (-0.25, -0.95), (-0.55, -1.2), (-0.5, -1.55)])
    stail = spl([(-0.5, -1.5), (-0.85, -1.62), (-0.55, -1.75), (0.0, -1.75), (0.45, -1.7)], closed=False)
    sear = arc(0.32, -1.0, 0.12, 0.2, 2.9, 6)
    lid = arc(0.38, -1.25, 0.08, math.radians(200), math.radians(340), 6)
    # gerbil on the surface
    b, d, e = gerbil()
    dx, dy, s = -0.5, 0.25, 0.32
    b, d, e = tf([b], dx, dy, s)[0], tf(d, dx, dy, s), tf(e, dx, dy, s)
    d = [x for x in d if math.dist(x[0], x[-1]) > 0.05 or len(x) > 6]
    roll = [ellipse(1.3, 0.75, 0.22, 0.42, 24), [(1.3, 1.17), (2.5, 1.17)], [(1.3, 0.33), (2.5, 0.33)],
            arc(2.5, 0.75, 0.42, -math.pi / 2, math.pi / 2, 16)]
    roll = [[(x, y) for x, y in ellipse(1.3, 0.75, 0.42, 0.42, 30)][:0] or roll[0]] + roll[1:]
    seeds_ = seed(-2.4, -0.5, 0.35, 0.4) + seed(1.2, -2.0, 0.35, -0.3)
    return make("Gerbil Tunnels in a Glass Tank", tank + [surf, ch, nest] + walls + [sleeper, stail, sear, lid] + [b] + d + roll + seeds_, e)


# -------------------------------------------------------------- guinea pigs

def hay_pile(x0, x1, y, h):
    mid = (x0 + x1) / 2
    w = x1 - x0
    mound = spl([(x0, y, 0), (x0 + 0.15 * w, y + 0.55 * h), (mid, y + h), (x1 - 0.15 * w, y + 0.55 * h), (x1, y, 0)], closed=False)
    strands = [quad((mid + w * a, y + h * b), (mid + w * (a + 0.12), y + h * (b + 0.25)), (mid + w * (a + 0.28), y + h * (b + 0.05)), 8)
               for a, b in [(-0.38, 0.25), (-0.15, 0.45), (0.05, 0.2), (-0.05, 0.75), (0.15, 0.5)]]
    sticks = [quad((mid + w * a, y + h * 0.9), (mid + w * (a + 0.1), y + h * 1.25), (mid + w * (a + 0.25), y + h * 1.35), 8)
              for a in (-0.25, 0.05)]
    return [mound] + strands + sticks


@design("pets_guinea_pig_hay", T)
def guinea_pig_hay(rng):
    b, d, e = guinea_pig()
    dx, dy, s = -1.1, -1.2, 1.5
    b, d, e = tf([b], dx, dy, s)[0], tf(d, dx, dy, s), tf(e, dx, dy, s)
    pile = hay_pile(0.9, 3.4, -1.2, 1.1)
    mouth_hay = [quad((1.35, -0.45), (1.6, -0.75), (1.95, -0.85), 8), quad((1.3, -0.5), (1.45, -0.9), (1.75, -1.0), 8)]
    vis = hide([b] + d, pile[0] + [(3.4, -1.25), (0.9, -1.25)])
    ground = [[(-3.2, -1.22), (0.9, -1.22)], [(3.4, -1.22), (3.6, -1.22)]]
    return make("Guinea Pig Munching Hay", vis + pile + mouth_hay + ground, e)


@design("pets_guinea_pigs_lettuce", T)
def guinea_pigs_lettuce(rng):
    out, hints = [], []
    s = 0.92
    for flip in (False, True):
        b, d, e = guinea_pig()
        dx = (-1.65 * s - 0.42) * (1 if not flip else -1)
        b, d, e = tf([b], dx, -0.8, s, flip)[0], tf(d, dx, -0.8, s, flip), tf(e, dx, -0.8, s, flip)
        out += [b] + d
        hints += e
    leaf = spl([(-0.42, -0.3), (-0.3, 0.0), (0.0, 0.1), (0.3, 0.0), (0.42, -0.3), (0.5, -0.65), (0.3, -0.95), (0.0, -1.1),
                (-0.3, -0.95), (-0.5, -0.65)])
    frill = wave(-0.45, 0.45, -0.95, 0.06, 3, 30)
    vein = [[(0.0, 0.05), (0.0, -1.05)], [(0.0, -0.4), (0.3, -0.2)], [(0.0, -0.4), (-0.3, -0.2)], [(0.0, -0.7), (0.32, -0.55)],
            [(0.0, -0.7), (-0.32, -0.55)]]
    out = hide(out, leaf)
    ground = [[(-3.4, -0.82), (3.4, -0.82)]]
    hearts = [heart(0.0, 1.0, 0.35)]
    return make("Two Guinea Pigs Sharing Lettuce", out + [leaf] + vein + ground + hearts + grass(-3.0, -0.82, 0.5) + grass(3.0, -0.82, 0.5), hints)


@design("pets_abyssinian_guinea_pig", T)
def abyssinian(rng):
    body = spl([(1.65, 0.55), (1.6, 0.9), (1.35, 1.25), (1.05, 1.55, 0), (0.85, 1.42), (0.6, 1.85, 0), (0.35, 1.55), (0.0, 1.9, 0),
                (-0.25, 1.6), (-0.6, 1.9, 0), (-0.85, 1.55), (-1.25, 1.68, 0), (-1.35, 1.3), (-1.8, 1.1, 0), (-1.6, 0.75),
                (-1.88, 0.35, 0), (-1.45, 0.2), (-1.1, 0.02, 0), (-0.75, 0.02, 0), (-0.6, 0.12), (0.4, 0.12), (0.62, 0.02, 0),
                (0.95, 0.02, 0), (1.05, 0.15), (1.35, 0.22), (1.6, 0.35)])
    _, d, e = guinea_pig()
    d = [d[0], d[1], d[3]] + d[4:]
    ros = [spiral(x, y, 0.04, 0.3, 1.25, 40, rot=r) for x, y, r in [(-0.75, 1.0, 0.0), (0.15, 0.95, 2.0), (-1.3, 0.6, 1.0)]]
    tufts = [poly((x, 0.12), (x + 0.12, 0.4), (x + 0.24, 0.12), closed=False) for x in (-0.3, 0.05)]
    dx, dy, s = -0.1, -1.4, 1.6
    out = tf([body] + d + ros, dx, dy, s)
    e = tf(e, dx, dy, s)
    ground = [[(-3.4, -1.42), (3.4, -1.42)]]
    return make("Abyssinian Guinea Pig with Rosettes", out + tf(tufts, dx, dy, s)[:0] + ground + grass(-3.0, -1.42, 0.5) + grass(2.9, -1.42, 0.5), e)


def gp_front_head():
    half = [(0, 1.0), (0.6, 0.98), (1.1, 0.8), (1.45, 0.4), (1.5, -0.1), (1.25, -0.55), (0.75, -0.85), (0.3, -0.95), (0, -0.97)]
    head = sym(half)
    ears = []
    for sx in (1, -1):
        ears.append(spl([(sx * 0.95, 0.86), (sx * 1.35, 1.2), (sx * 1.85, 1.1), (sx * 1.95, 0.7), (sx * 1.48, 0.42)], closed=False))
        ears.append(spl([(sx * 1.25, 0.88), (sx * 1.6, 0.98), (sx * 1.72, 0.75)], closed=False))
    muzzle = spl([(-0.6, -0.05), (-0.45, -0.75)], closed=False)
    nose = [spl([(-0.2, -0.3), (0.0, -0.22), (0.2, -0.3), (0.0, -0.45)])]
    mouth = [[(0.0, -0.45), (0.0, -0.58)], spl([(-0.28, -0.62), (-0.12, -0.66), (0.0, -0.58), (0.12, -0.66), (0.28, -0.62)], closed=False)]
    wh = [[(sx * 0.32, -0.4), (sx * 1.25, -0.25)] for sx in (1, -1)] + [[(sx * 0.32, -0.47), (sx * 1.25, -0.6)] for sx in (1, -1)]
    blaze = [spl([(-0.25, 0.98), (-0.2, 0.5), (-0.3, -0.1)], closed=False), spl([(0.25, 0.98), (0.2, 0.5), (0.3, -0.1)], closed=False)]
    return head, ears + nose + mouth + blaze + hide(wh, *nose), [eye(sx * 0.82, 0.28, 0.15) for sx in (1, -1)]


@design("pets_guinea_pig_bed", T)
def guinea_pig_bed(rng):
    b, d, e = guinea_pig()
    dx, dy, s = -0.15, -1.05, 1.35
    b, d, e = tf([b], dx, dy, s)[0], tf(d, dx, dy, s), tf(e, dx, dy, s)
    cy = -0.95
    rim_o = ellipse(0, cy, 3.0, 0.9, 140)
    rim_i = ellipse(0, cy, 2.45, 0.6, 120)
    cup = spl([(-3.0, cy, 0), (-2.85, cy - 1.0), (-1.6, cy - 1.55), (0, cy - 1.65), (1.6, cy - 1.55), (2.85, cy - 1.0), (3.0, cy, 0)], closed=False)
    front = chain(rim_i[60:], [(2.45, cy), (2.45, -3.5), (-2.45, -3.5), (-2.45, cy)])
    gp = hide([b] + d, front)
    back = hide([rim_i], b)
    pillow = hide([spl([(-2.2, cy + 0.15), (-1.0, cy + 0.65), (0.6, cy + 0.6), (2.1, cy + 0.2)], closed=False)], b)
    hearts = [heart(x, y, 0.22) for x, y in [(-1.7, cy - 1.05), (0.0, cy - 1.2), (1.7, cy - 1.05)]]
    zs = []
    for x, y, sz in [(2.0, 1.4, 0.3), (2.45, 1.95, 0.38), (2.95, 2.6, 0.46)]:
        zs.append([(x, y), (x + sz, y), (x, y - sz * 0.9), (x + sz, y - sz * 0.9)])
    lid = arc(dx + 1.15 * s, dy + 0.98 * s, 0.17, math.radians(200), math.radians(340), 8)
    return make("Guinea Pig in a Cosy Bed", gp + [lid, rim_o] + back + pillow + [cup] + hearts + zs, e[1:])


# ------------------------------------------------------------------ rabbits

@design("pets_lop_rabbit", T)
def lop_rabbit(rng):
    b, d, e = rabbit("lop")
    dx, dy, s = -0.8, -2.0, 1.45
    b, d, e = tf([b], dx, dy, s)[0], tf(d, dx, dy, s), tf(e, dx, dy, s)
    ear = d[-2]
    vis = hide([b], ear) + d
    bowl = [spl([(1.6, -1.5), (1.75, -1.98, 0), (3.05, -1.98, 0), (3.2, -1.5)], closed=False), ellipse(2.4, -1.5, 0.8, 0.2, 40)]
    pellets = [ellipse(x, -1.45, 0.11, 0.06, 10) for x in (2.0, 2.3, 2.6, 2.85, 2.15, 2.45)][:4]
    ground = [[(-3.2, -2.0), (1.75, -2.0)], [(3.05, -2.0), (3.4, -2.0)]]
    return make("Lop-Eared Rabbit", vis + bowl + pellets + ground + grass(-2.9, -2.0, 0.5), e)


@design("pets_angora_rabbit", T)
def angora_rabbit(rng):
    fluff = []
    n = 26
    for i in range(n + 1):
        t = TAU * i / n
        rx, ry = 2.6, 2.1
        r = 1.0 if i % 2 == 0 else 1.1
        fluff.append((rx * r * math.cos(t), -0.3 + ry * r * math.sin(t)))
    body = spl(fluff[:-1])
    face = ellipse(0, 0.3, 0.95, 0.8, 50)
    ears = hide([lens((sx * 0.5, 1.2), (sx * 0.95, 3.35), 0.2, 24) for sx in (1, -1)], body)
    ears += [spl([(sx * 0.6, 1.9), (sx * 0.75, 2.6), (sx * 0.88, 3.05)], closed=False) for sx in (1, -1)]
    tufts = [poly((sx * 0.85, 3.3), (sx * 0.7, 3.75), (sx * 0.95, 3.5), (sx * 1.05, 3.85), (sx * 1.1, 3.45), (sx * 1.35, 3.6),
                  (sx * 1.02, 3.22), closed=False) for sx in (1, -1)]
    nose = [poly((-0.12, 0.15), (0.12, 0.15), (0, 0.02)), [(0, 0.02), (0, -0.12)],
            spl([(-0.25, -0.15), (-0.1, -0.2), (0, -0.12), (0.1, -0.2), (0.25, -0.15)], closed=False)]
    wh = [[(sx * 0.25, 0.05), (sx * 0.95, 0.15)] for sx in (1, -1)]
    locks = [spl([(x, y), (x + 0.25, y - 0.3), (x + 0.15, y - 0.65)], closed=False)
             for x, y in [(-2.0, 0.3), (-1.6, -1.0), (-0.6, -1.6), (0.6, -1.5), (1.5, -1.0), (1.85, 0.4), (-1.3, 1.1), (1.2, 1.15)]]
    feet = [ellipse(sx * 0.9, -2.45, 0.5, 0.22, 20) for sx in (1, -1)]
    vis = hide([body], *feet)
    return make("Fluffy Angora Rabbit", vis + [face] + ears + tufts + nose + wh + hide(locks, face) + feet,
                [eye(sx * 0.42, 0.5, 0.13) for sx in (1, -1)])


@design("pets_rabbit_agility", T)
def rabbit_agility(rng):
    body = spl([(2.2, 0.9), (2.05, 1.25), (1.6, 1.45), (1.0, 1.32), (0.2, 1.48), (-0.7, 1.38), (-1.4, 1.02), (-1.62, 1.12),
                (-1.8, 0.92), (-1.55, 0.7), (-1.2, 0.45), (-0.4, 0.35), (0.5, 0.4), (1.2, 0.45), (1.6, 0.55), (1.9, 0.68), (2.1, 0.78)])
    hind = spl([(-0.6, 0.95), (-1.25, 0.8), (-2.0, 0.5), (-2.65, 0.34), (-2.85, 0.22, 0), (-2.62, 0.1, 0), (-1.9, 0.18),
                (-1.15, 0.32), (-0.45, 0.5)])
    fl1 = spl([(0.95, 0.75), (1.3, 0.25), (1.52, -0.22), (1.68, -0.3, 0), (1.72, -0.12, 0), (1.6, 0.3), (1.5, 0.7)])
    fl2 = [(x - 0.3, y + 0.08) for x, y in fl1]
    fl2 = hide([fl2], fl1, body)
    body_v = hide([body], hind, fl1)
    ears = [spl([(1.68, 1.44), (1.25, 1.95), (0.55, 2.25), (0.68, 1.95), (1.22, 1.42)], closed=False),
            spl([(1.42, 1.4), (0.9, 1.75), (0.25, 1.9), (0.42, 1.65), (0.95, 1.36)], closed=False)]
    ears = [ears[0]] + hide([ears[1]], poly(*ears[0][::1]))
    wh = [[(2.15, 0.88), (2.65, 1.03)], [(2.15, 0.83), (2.65, 0.7)]]
    body = body_v[0]
    rest = body_v[1:] + [hind, fl1] + fl2
    dx, dy, s = -0.2, 0.25, 1.15
    rab = tf([body] + ears + rest + wh, dx, dy, s)
    he = tf([eye(1.72, 1.05, 0.11)], dx, dy, s)
    posts = [rect(-2.0, -2.6, -1.75, -0.8), rect(1.75, -2.6, 2.0, -0.8)]
    caps = [circle(-1.875, -0.68, 0.13, 14), circle(1.875, -0.68, 0.13, 14)]
    bar = [rect(-1.75, -1.5, 1.75, -1.2)] + [[(x, -1.5), (x, -1.2)] for x in (-1.05, -0.35, 0.35, 1.05)]
    feet_ = [[(-2.4, -2.6), (-1.35, -2.6)], [(1.35, -2.6), (2.4, -2.6)]]
    path = [arc(0.0, -2.2, 3.0, math.radians(165 - 8 * k), math.radians(165 - 8 * k - 4.5), 4) for k in range(3)]
    path += [arc(0.0, -2.2, 3.0, math.radians(15 + 8 * k), math.radians(15 + 8 * k + 4.5), 4) for k in range(3)]
    ground = [[(-3.3, -2.6), (3.3, -2.6)]]
    return make("Rabbit Jumping an Agility Hurdle", rab + posts + caps + bar + feet_ + hide(path, *tf([spl([(2.2, 0.9), (2.05, 1.25), (1.6, 1.45), (-0.7, 1.38), (-2.85, 0.22), (-1.2, 0.3), (1.7, -0.3)])], dx, dy, s)) + ground, he)


def rabbit_front_head():
    head = sym([(0, 0.9), (0.55, 0.85), (0.95, 0.5), (1.05, 0.0), (0.85, -0.5), (0.45, -0.8), (0, -0.88)])
    ear_l = spl([(-0.55, 0.8), (-0.75, 1.7), (-0.7, 2.6), (-0.42, 2.8), (-0.2, 2.5), (-0.18, 1.6), (-0.2, 0.88)], closed=False)
    ear_li = spl([(-0.45, 1.0), (-0.52, 1.8), (-0.45, 2.45)], closed=False)
    ear_r = spl([(0.2, 0.88), (0.3, 1.7), (0.55, 2.1), (1.0, 2.05), (1.5, 1.7), (1.4, 1.48), (0.85, 1.6), (0.6, 1.3), (0.6, 0.82)], closed=False)
    ear_ri = spl([(0.38, 1.1), (0.48, 1.65), (0.75, 1.85), (1.25, 1.68)], closed=False)
    nose = [poly((-0.13, -0.1), (0.13, -0.1), (0, -0.25)), [(0, -0.25), (0, -0.4)],
            spl([(-0.28, -0.45), (-0.12, -0.5), (0, -0.4), (0.12, -0.5), (0.28, -0.45)], closed=False)]
    wh = [[(sx * 0.3, -0.25), (sx * 1.25, -0.12)] for sx in (1, -1)] + [[(sx * 0.3, -0.32), (sx * 1.25, -0.45)] for sx in (1, -1)]
    return head, [ear_l, ear_li, ear_r, ear_ri] + nose + wh, [eye(sx * 0.45, 0.18, 0.13) for sx in (1, -1)]


@design("pets_rabbit_box_castle", T)
def rabbit_box_castle(rng):
    top = 0.2
    merl = [(-2.2, top)]
    xs = [-2.2, -1.6, -1.0, -0.4, 0.2, 0.8, 1.4, 2.0]
    for i in range(len(xs) - 1):
        a, b_ = xs[i], xs[i + 1]
        h = 0.45 if i % 2 == 0 else 0.0
        merl += [(a, top + h), (b_, top + h)]
    merl += [(2.0, top)]
    wall = [(-2.2, -2.7)] + merl + [(2.0, -2.7)]
    tower = [(2.0, -2.7), (2.0, 1.0), (2.0, 1.4), (2.2, 1.4), (2.2, 1.1), (2.45, 1.1), (2.45, 1.4), (2.7, 1.4), (2.7, 1.1),
             (2.95, 1.1), (2.95, 1.4), (3.15, 1.4), (3.15, -2.7)]
    door = chain([(-0.9, -2.7), (-0.9, -1.7)], arc(-0.3, -1.7, 0.6, math.pi, 0, 20), [(0.3, -2.7)])
    win = chain([(2.35, 0.0), (2.35, 0.4)], arc(2.575, 0.4, 0.225, math.pi, 0, 10), [(2.8, 0.0)], [(2.35, 0.0)])
    win2 = rect(-1.8, -1.2, -1.3, -0.6)
    flap = [poly((-2.2, -0.3), (-2.75, -0.55), (-2.75, -2.45), (-2.2, -2.7), closed=False)]
    corr = [[(x, -2.6), (x, -2.3)] for x in ()]
    head, hd, he = rabbit_front_head()
    dx, dy, s = -0.35, 0.95, 0.95
    head, hd, he = tf([head], dx, dy, s)[0], tf(hd, dx, dy, s), tf(he, dx, dy, s)
    block = poly(*wall[:-1], (2.0, -2.7))
    rab = hide([head] + hd, block)
    wall_vis = hide([poly(*wall, closed=False)], head)
    floor = [[(-3.2, -2.7), (3.4, -2.7)]]
    paws = [ellipse(dx + sx * 0.4, 0.35, 0.22, 0.15, 14) for sx in (1, -1)]
    return make("Rabbit in a Cardboard Castle", rab + wall_vis + [poly(*tower, closed=False), door, win, win2] + flap + paws + floor + corr, he)


@design("pets_rabbit_harness", T)
def rabbit_harness(rng):
    b, d, e = rabbit("up")
    dx, dy, s = -0.6, -2.4, 1.25
    b, d, e = tf([b], dx, dy, s)[0], tf(d, dx, dy, s), tf(e, dx, dy, s)
    strap1 = tf([spl([(0.75, 1.9), (0.55, 1.45), (0.62, 0.95)], closed=False)], dx, dy, s)
    strap2 = tf([spl([(0.05, 1.82), (-0.15, 1.0), (0.12, 0.3)], closed=False)], dx, dy, s)
    belly_ = tf([[(0.12, 0.3), (0.65, 0.6)], [(0.6, 1.4), (0.08, 1.45)]], dx, dy, s)
    ring = [circle(pt((0.25, 1.85), dx, dy, s)[0], pt((0.25, 1.85), dx, dy, s)[1], 0.12, 12)]
    rx, ry = pt((0.25, 1.85), dx, dy, s)
    lead = [cubic((rx - 0.1, ry + 0.08), (rx - 0.8, ry + 0.2), (-2.3, 0.6), (-2.75, 1.1), 40)]
    stake = [rect(-2.95, -2.42, -2.6, 1.0), poly((-2.95, 1.0), (-2.775, 1.3), (-2.6, 1.0), closed=False), [(-2.95, 0.8), (-2.6, 0.8)]]
    lead = hide(lead, stake[0])
    loop = [ellipse(-2.775, 0.95, 0.3, 0.12, 20)]
    ground = [[(-3.2, -2.42), (3.2, -2.42)]]
    flowers = []
    for x in (2.2, 2.9):
        flowers += [[(x, -2.42), (x, -1.6)], circle(x, -1.45, 0.15, 14)] + [circle(x + 0.25 * math.cos(a), -1.45 + 0.25 * math.sin(a), 0.1, 10)
                                                                         for a in [k * TAU / 6 for k in range(6)]]
    return make("Rabbit on a Harness and Lead", [b] + d + strap1 + strap2 + belly_ + ring + lead + stake + loop + ground + flowers + grass(-2.9, -2.42, 0.5), e)


@design("pets_rabbit_hay_rack", T)
def rabbit_hay_rack(rng):
    b, d, e = rabbit("up")
    dx, dy, s = -2.05, -2.6, 1.2
    b, d, e = tf([b], dx, dy, s)[0], tf(d, dx, dy, s), tf(e, dx, dy, s)
    nose = pt((1.55, 1.75), dx, dy, s)
    x0, x1, yb, yt = 0.5, 2.9, 0.6, 2.4
    rack = poly((x0 - 0.25, yt), (x1 + 0.25, yt), (x1, yb), (x0, yb))
    bars = [[(x0 + (x1 - x0) * k / 5, yb), (x0 - 0.25 + (x1 - x0 + 0.5) * k / 5, yt)] for k in range(1, 5)]
    plate = [rect(x0 - 0.45, 2.4, x1 + 0.45, 2.7), circle(x0 - 0.2, 2.55, 0.08, 8), circle(x1 + 0.2, 2.55, 0.08, 8)][:1]
    hay = [quad((x0 + 0.1 + 0.48 * k, yt + 0.3), (x0 + 0.25 + 0.48 * k, yt + 0.7), (x0 + 0.5 + 0.48 * k, yt + 0.85 - 0.15 * (k % 2)), 8)
           for k in range(5)]
    dangle = [quad((0.75, yb), (0.5, 0.0), nose, 10), quad((1.4, yb), (1.5, 0.1), (1.3, -0.25), 8), quad((2.4, yb), (2.6, 0.2), (2.45, -0.15), 8)]
    floor = [bedding(-3.3, 3.3, -2.62, 10, 0.12)]
    bowl = [spl([(1.2, -1.95), (1.35, -2.5, 0), (2.65, -2.5, 0), (2.8, -1.95)], closed=False), ellipse(2.0, -1.95, 0.8, 0.18, 40)]
    return make("Rabbit at the Hay Rack", [b] + d + [rack] + bars + plate + hay + dangle + floor + bowl, e)


# ------------------------------------------------- chinchillas and ferrets

def chinchilla():
    """Chinchilla sitting up, facing right; feet at y=0."""
    body = spl([(1.35, 2.55), (1.15, 2.95), (0.6, 3.2), (0.1, 3.02), (-0.4, 2.5), (-0.85, 1.7), (-1.05, 0.9), (-0.9, 0.3),
                (-0.6, 0.04), (-0.4, 0.0, 0), (0.72, 0.0, 0), (0.74, 0.12, 0), (0.2, 0.25), (0.55, 0.8), (0.72, 1.5),
                (0.85, 2.0), (1.1, 2.3), (1.3, 2.42)])
    ear = spl([(0.28, 3.12), (0.02, 3.65), (0.3, 4.2), (0.85, 4.18), (1.0, 3.7), (0.78, 3.12)], closed=False)
    ear_in = spl([(0.42, 3.25), (0.28, 3.65), (0.48, 3.98), (0.78, 3.9), (0.8, 3.55)], closed=False)
    tail = spl([(-0.9, 0.35), (-1.5, 0.28), (-1.95, 0.65), (-2.12, 1.25), (-2.02, 1.9), (-1.75, 2.45), (-1.35, 2.7), (-1.15, 2.45),
                (-1.32, 1.95), (-1.42, 1.35), (-1.3, 0.88), (-1.05, 0.72)])
    fur = [spl([(-1.85, 1.0), (-1.7, 1.45)], closed=False), spl([(-1.8, 1.8), (-1.6, 2.2)], closed=False)]
    arm = spl([(0.7, 1.9), (1.05, 1.75), (1.12, 1.55), (0.95, 1.48), (0.7, 1.6)])
    thigh = spl([(-0.15, 0.27), (-0.75, 0.75), (-0.6, 1.4), (0.0, 1.45), (0.35, 0.95)], closed=False)
    wh = [[(1.3, 2.55), (2.0, 2.85)], [(1.3, 2.5), (2.05, 2.5)], [(1.3, 2.45), (1.95, 2.15)]]
    body_v = hide([body], arm, tail)
    return body_v, [ear, ear_in, tail, arm, thigh] + fur + wh, [eye(0.92, 2.72, 0.16), eye(1.35, 2.55, 0.05)], body


@design("pets_chinchilla_dust_bath", T)
def chinchilla_dust_bath(rng):
    b, d, e, m = chinchilla()
    dx, dy, s = 0.2, -1.6, 1.05
    b, d, e, m = tf(b, dx, dy, s), tf(d, dx, dy, s), tf(e, dx, dy, s), tf([m], dx, dy, s)[0]
    tub_top = ellipse(0, -1.2, 3.0, 0.55, 140)
    front = chain(ellipse(0, -1.2, 3.0, 0.55, 140)[70:], [(3.0, -1.2), (2.7, -3.0), (-2.7, -3.0), (-3.0, -1.2)])
    tub = [spl([(-3.0, -1.2, 0), (-2.7, -2.9, 0), (2.7, -2.9, 0), (3.0, -1.2, 0)], closed=False)]
    sand = wave(-2.6, 2.6, -1.35, 0.06, 4, 60)
    chin = hide(b + d, front)
    puffs = []
    for x, y, r in [(-2.2, -0.6, 0.45), (-1.6, -0.3, 0.35), (2.3, -0.5, 0.42), (2.75, 0.05, 0.3), (-2.6, 0.1, 0.28), (1.8, 0.2, 0.25)]:
        puffs.append(circle(x, y, r, 24))
    puffs = [p_ for p_ in hide(puffs, m, d[2])]
    rim_v = hide([tub_top], m)
    specks = [circle(x, y, 0.06, 6) for x, y in [(-1.0, 0.4), (2.2, 0.9), (-2.0, 0.9), (1.4, 0.6)]]
    return make("Chinchilla in a Dust Bath", chin + rim_v + tub + [sand] + puffs + specks, e)


@design("pets_chinchilla_ledge", T)
def chinchilla_ledge(rng):
    b, d, e, m = chinchilla()
    dx, dy, s = 0.4, -0.95, 1.12
    b, d, e = tf(b, dx, dy, s), tf(d, dx, dy, s), tf(e, dx, dy, s)
    ledge = [rect(-2.6, -1.35, 2.6, -0.95)]
    grain = [wave(-2.3, -0.4, -1.15, 0.05, 2, 30), wave(0.6, 2.3, -1.15, 0.05, 2, 30)]
    bracket = [poly((-1.9, -1.35), (-1.9, -2.6), (-1.5, -2.6), (-1.5, -1.75), (-0.9, -1.35), closed=False),
               poly((1.9, -1.35), (1.9, -2.6), (1.5, -2.6), (1.5, -1.75), (0.9, -1.35), closed=False)]
    screws = [circle(-1.7, -2.3, 0.08, 8), circle(1.7, -2.3, 0.08, 8)]
    bars = [[(x, -3.0), (x, 3.3)] for x in (-3.0, 3.2)]
    return make("Chinchilla on a Wooden Ledge", b + d + ledge + grain + bracket + screws, e)


def ferret_head(x, y, s=1.0, closed_eyes=False, flip=False):
    """Ferret head in profile, facing right, nose at (x + 1.25s, y)."""
    pts = [(-0.35, 0.55), (0.1, 0.65), (0.6, 0.5), (1.05, 0.2), (1.25, 0.02), (1.15, -0.12), (0.7, -0.25), (0.2, -0.35),
           (-0.3, -0.3)]
    head = spl(pts, closed=False)
    ear = spl([(0.0, 0.62), (-0.05, 0.9), (0.22, 0.95), (0.35, 0.62)], closed=False)
    mask = spl([(0.85, 0.32), (0.55, 0.42), (0.2, 0.22), (0.25, 0.0), (0.6, -0.1), (0.95, 0.12)])
    nose = circle(1.18, 0.0, 0.06, 8)
    wh = [[(1.1, -0.05), (1.6, 0.05)], [(1.1, -0.1), (1.6, -0.25)]]
    strokes = tf([head, ear, mask] + wh, x, y, s, flip)
    if closed_eyes:
        strokes += tf([arc(0.62, 0.22, 0.13, math.radians(200), math.radians(340), 6)], x, y, s, flip)
        hints = []
    else:
        hints = [eye(*pt((0.62, 0.17), x, y, s, flip), 0.1 * s)]
    hints += [eye(*pt((1.2, 0.0), x, y, s, flip), 0.07 * s)]
    return strokes, hints


@design("pets_ferret_hammock", T)
def ferret_hammock(rng):
    top = cubic((-2.9, 0.6), (-1.3, -0.9), (1.3, -0.9), (2.9, 0.6), 60)
    low = cubic((-2.9, 0.6), (-1.3, -1.55), (1.3, -1.55), (2.9, 0.6), 60)
    hooks = [[(-2.9, 0.6), (-3.1, 2.7)], [(2.9, 0.6), (3.1, 2.7)], [(-2.9, 0.6), (-2.5, 2.7)], [(2.9, 0.6), (2.5, 2.7)]]
    bar = [[(-3.4, 2.75), (3.4, 2.75)]]
    clips = [circle(x, 2.75, 0.12, 10) for x in (-3.1, -2.5, 2.5, 3.1)]
    body = spl([(-2.3, -0.05), (-1.9, 0.6), (-1.0, 0.95), (0.0, 0.95), (0.6, 0.9), (0.85, 0.85)], closed=False)
    head, hh = ferret_head(0.95, 0.3, 1.25, closed_eyes=True)
    paw = spl([(0.4, -0.45), (0.5, -1.05), (0.65, -1.45), (0.95, -1.45), (0.95, -1.05), (0.9, -0.5)], closed=False)
    toes = [[(0.75, -1.45), (0.75, -1.3)]]
    tail = sides(cubic((-2.25, -0.2), (-2.8, -0.6), (-2.6, -1.4), (-2.9, -2.3), 30), lambda t: 0.45 - 0.33 * t)
    tip = arc(-2.9, -2.3, 0.06, math.pi, TAU, 4)
    tail_shape = poly(*tail[0], *tail[1][::-1])
    fab = hide([low, top], poly((0.4, -0.45), (0.5, -1.05), (0.65, -1.45), (0.95, -1.45), (0.95, -1.05), (0.9, -0.5)), tail_shape)
    ferret = hide([body] + head, chain(top, [(2.9, -2.5), (-2.9, -2.5)]))
    folds = hide([quad((-1.6, -0.75), (-0.8, -1.05), (0.1, -1.1), 10), quad((1.2, -0.85), (1.7, -0.6), (2.2, -0.2), 10)], tail_shape)
    zs = []
    for x, y, sz in [(0.6, 1.5, 0.3), (1.05, 2.0, 0.36)]:
        zs.append([(x, y), (x + sz, y), (x, y - sz * 0.9), (x + sz, y - sz * 0.9)])
    return make("Ferret Snoozing in a Hammock", fab + hooks + bar + clips + ferret + [paw] + toes + tail + [tip] + folds + zs, hh)


@design("pets_ferret_sock", T)
def ferret_sock(rng):
    body = spl([(2.88, 1.0, 0), (2.6, 1.3), (2.2, 1.55), (1.85, 1.6), (1.4, 1.45), (0.6, 1.85), (-0.3, 1.95), (-1.0, 1.72),
                (-1.5, 1.32), (-1.68, 0.9), (-1.62, 0.5), (-1.62, 0.0, 0), (-1.15, 0.0, 0), (-1.18, 0.35), (-0.9, 0.7), (0.0, 0.85),
                (0.9, 0.75), (1.15, 0.45), (1.15, 0.0, 0), (1.55, 0.0, 0), (1.52, 0.4), (1.75, 0.75), (2.2, 0.85), (2.6, 0.88)])
    ear = spl([(1.72, 1.58), (1.66, 1.9), (1.95, 1.98), (2.08, 1.62)], closed=False)
    mask = spl([(2.58, 1.25), (2.22, 1.42), (1.88, 1.28), (1.92, 1.05), (2.3, 1.0)])
    far = [poly((0.95, 0.55), (0.88, 0.0), (1.12, 0.0), closed=False), poly((-1.35, 0.6), (-1.38, 0.0), (-1.6, 0.0), closed=False)]
    far = hide(far, body)
    tail = sides(cubic((-1.55, 1.2), (-2.1, 1.25), (-2.6, 0.9), (-3.2, 1.15), 30), lambda t: 0.4 - 0.28 * t)
    tail = hide(tail, body)
    tip = arc(-3.2, 1.15, 0.06, math.pi / 2, 1.5 * math.pi, 4)
    sock = spl([(2.5, 1.05), (2.98, 1.0), (3.0, 0.5), (3.2, 0.35), (3.7, 0.32), (3.85, 0.15), (3.7, 0.0, 0), (2.85, 0.0, 0),
                (2.55, 0.15), (2.5, 0.55)])
    cuff = [[(2.5, 0.85), (2.98, 0.82)]]
    stripes = [[(2.5, 0.55), (3.0, 0.52)], [(3.25, 0.34), (3.25, 0.0)]]
    heel = [arc(2.9, 0.3, 0.25, math.radians(180), math.radians(270), 6)]
    sock_v = hide([sock] + cuff + stripes + heel, body)
    wh = [[(2.8, 1.05), (3.3, 1.3)], [(2.8, 1.0), (3.35, 1.12)]]
    nose = [circle(2.85, 1.02, 0.06, 8)]
    ground = [[(-3.4, 0.0), (-2.0, 0.0)], [(-0.3, 0.0), (4.0, 0.0)]]
    out = tf([body, ear, mask] + far + tail + [tip] + sock_v + hide(wh, sock), 0.75, -1.6, 0.78)
    eyes = [eye(*pt((2.22, 1.2), 0.75, -1.6, 0.78), 0.09)]
    basket = poly((-3.3, 1.2), (-2.95, -1.6), (-1.15, -1.6), (-0.8, 1.2), closed=False)
    rim = [rrect(-3.45, 1.1, -0.65, 1.45, 0.12)]
    weave = [[(-3.3 + 0.35 * (1.2 - y) / 2.8 * 1.0, y), (-0.8 - 0.35 * (1.2 - y) / 2.8, y)] for y in (0.5, -0.2, -0.9)]
    handles = [arc(-3.05, 1.6, 0.18, math.pi * 0.2, math.pi * 1.0, 8)][:0]
    shirt = spl([(-3.2, 1.45), (-3.0, 2.1), (-2.5, 2.35), (-2.2, 2.1), (-1.8, 2.4), (-1.3, 2.2), (-1.0, 1.45)], closed=False)
    dangle = spl([(-1.05, 1.45), (-0.55, 1.4), (-0.4, 0.6), (-0.15, 0.4), (-0.25, 0.15), (-0.65, 0.3), (-0.75, 0.9), (-0.82, 1.1)], closed=False)
    dangle_v = hide([dangle], rim[0])
    stripes2 = [[(-0.6, 1.0), (-0.38, 0.98)]]
    floor = [[(-3.5, -1.6), (3.9, -1.6)]]
    return make("Ferret Stealing a Sock", out + [basket] + rim + weave + [shirt] + dangle_v + stripes2 + floor, eyes)




# ------------------------------------------------------------- rats & mice

def rat():
    """Fancy rat sitting up, facing right; feet at y=0."""
    body = spl([(1.6, 2.6, 0), (1.2, 2.95), (0.6, 3.18), (0.0, 3.0), (-0.5, 2.4), (-0.95, 1.5), (-1.15, 0.7), (-0.95, 0.15),
                (-0.65, 0.0, 0), (0.8, 0.0, 0), (0.82, 0.12, 0), (0.15, 0.25), (0.5, 0.7), (0.7, 1.4), (0.85, 1.95), (1.1, 2.3),
                (1.38, 2.45)])
    ear = spl([(0.12, 3.06), (-0.12, 3.5), (0.2, 3.9), (0.72, 3.75), (0.75, 3.18)], closed=False)
    ear_in = spl([(0.22, 3.15), (0.1, 3.5), (0.3, 3.72), (0.6, 3.6)], closed=False)
    hood = spl([(0.85, 2.0), (0.3, 2.15), (-0.3, 2.0), (-0.75, 1.85)], closed=False)
    thigh = spl([(-0.2, 0.27), (-0.8, 0.75), (-0.62, 1.4), (0.0, 1.42), (0.32, 0.95)], closed=False)
    tailc = spl([(-0.95, 0.25), (-1.7, 0.08), (-2.5, 0.2), (-2.95, 0.7), (-2.8, 1.35), (-2.35, 1.5)], closed=False)
    tail = hide(sides(tailc, lambda t: 0.3 - 0.22 * t), body)
    rings = []
    wh = [[(1.5, 2.62), (2.05, 2.85)], [(1.5, 2.56), (2.05, 2.45)]]
    return body, [ear, ear_in, hood, thigh] + tail + rings + wh, [eye(0.98, 2.75, 0.13), eye(1.6, 2.6, 0.06)]


@design("pets_fancy_rat", T)
def fancy_rat(rng):
    b, d, e = rat()
    dx, dy, s = 0.3, -2.4, 1.3
    b, d, e = tf([b], dx, dy, s)[0], tf(d, dx, dy, s), tf(e, dx, dy, s)
    cracker = rrect(1.05, -0.35, 1.75, 0.25, 0.08)
    paws = [ellipse(1.15, -0.05, 0.2, 0.14, 12), ellipse(1.6, -0.1, 0.2, 0.14, 12)]
    dots = [circle(x, y, 0.05, 6) for x, y in [(1.25, 0.12), (1.55, 0.12), (1.4, -0.1)]][:0]
    vis = hide([b] + d, cracker, *paws)
    cr = hide([cracker], *paws)
    holes = [circle(x, y, 0.06, 6) for x, y in [(1.4, 0.05), (1.4, -0.2)]]
    ground = [[(-3.2, -2.42), (3.2, -2.42)]]
    crumbs = [circle(x, -2.33, 0.07, 8) for x in (1.7, 2.3, 2.6)]
    return make("Fancy Rat Nibbling a Cracker", vis + cr + paws + holes + ground + crumbs, e)


@design("pets_rat_coconut", T)
def rat_coconut(rng):
    dome = chain([(-2.8, -2.2)], arc(0, -2.2, 2.8, math.pi, 0, 80)[1:], [(2.8, -2.2)])
    rim = [[(-3.1, -2.2), (3.1, -2.2)]]
    door = circle(0.2, -0.9, 1.0, 60)
    fibres = []
    for a in (150, 125, 60, 35, 20, 160):
        r0, r1 = 1.6 if a in (125, 60) else 1.4, 2.6
        aa = math.radians(a)
        fibres.append(quad((r0 * math.cos(aa), -2.2 + r0 * math.sin(aa)), ((r0 + 0.5) * math.cos(aa + 0.08), -2.2 + (r0 + 0.5) * math.sin(aa + 0.08)),
                           (r1 * math.cos(aa + 0.02), -2.2 + r1 * math.sin(aa + 0.02)), 8))
    fibres = hide(fibres, door)
    # rat head looking out (three-quarter front)
    head = spl([(-0.45, -1.3), (-0.55, -0.75), (-0.25, -0.3), (0.3, -0.25), (0.8, -0.55), (1.15, -0.9), (1.25, -1.15), (1.05, -1.35),
                (0.5, -1.5), (-0.1, -1.55)])
    ears = [spl([(-0.4, -0.55), (-0.85, -0.2), (-0.65, 0.3), (-0.2, 0.25), (-0.1, -0.28)], closed=False),
            spl([(0.25, -0.25), (0.3, 0.2), (0.75, 0.3), (0.95, -0.05), (0.75, -0.5)], closed=False)]
    paws = [ellipse(-0.3, -1.6, 0.25, 0.15, 12), ellipse(0.45, -1.65, 0.25, 0.15, 12)]
    wh = [[(1.15, -1.1), (1.7, -0.95)], [(1.15, -1.15), (1.7, -1.3)]]
    vis = hide([head], *paws)
    door_v = hide([door], head, *ears, *paws)
    window = [circle(-1.6, -0.6, 0.35, 24)]
    rope = []
    floor = [bedding(-3.3, 3.3, -2.45, 10, 0.12)]
    return make("Pet Rat Peeking from a Coconut Hut", [dome] + rim + door_v + fibres + vis + ears + paws + wh + window + rope + floor,
                [eye(0.35, -0.7, 0.11), eye(1.22, -1.12, 0.06)])


def mouse_side():
    """Small mouse sitting, facing right; feet at y=0."""
    body = spl([(1.3, 1.4, 0), (1.05, 1.68), (0.6, 1.85), (0.1, 1.7), (-0.4, 1.3), (-0.75, 0.75), (-0.75, 0.25), (-0.5, 0.0, 0),
                (0.75, 0.0, 0), (0.75, 0.12, 0), (0.2, 0.2), (0.5, 0.55), (0.75, 0.95), (1.0, 1.2)])
    ear = spl([(0.18, 1.75), (-0.2, 2.15), (0.05, 2.65), (0.6, 2.62), (0.75, 2.2), (0.55, 1.85)], closed=False)
    ear_in = spl([(0.3, 1.88), (0.08, 2.2), (0.2, 2.48), (0.55, 2.45), (0.6, 2.15)], closed=False)
    thigh = spl([(-0.15, 0.2), (-0.5, 0.55), (-0.3, 0.95), (0.15, 0.85)], closed=False)
    wh = [[(1.22, 1.42), (1.75, 1.6)], [(1.22, 1.37), (1.75, 1.25)]]
    return body, [ear, ear_in, thigh] + wh, [eye(0.85, 1.5, 0.1), eye(1.3, 1.4, 0.05)]


@design("pets_mouse_cheese", T)
def mouse_cheese(rng):
    top = poly((-2.8, -0.2), (2.4, 0.4), (1.2, -0.6))
    front = poly((-2.8, -0.2), (1.2, -0.6), (1.2, -2.6), (-2.8, -2.2), closed=False)
    side = poly((1.2, -0.6), (2.4, 0.4), (2.4, -1.6), (1.2, -2.6), closed=False)
    holes = [ellipse(-1.9, -1.0, 0.35, 0.28, 24), ellipse(-0.6, -1.6, 0.42, 0.33, 24), ellipse(0.5, -0.95, 0.25, 0.2, 18),
             ellipse(-2.2, -1.9, 0.2, 0.16, 14), ellipse(1.8, -0.7, 0.18, 0.28, 16), ellipse(1.75, -1.6, 0.14, 0.22, 14),
             ellipse(0.4, -2.1, 0.22, 0.17, 14)]
    b, d, e = mouse_side()
    dx, dy, s = -0.6, -0.15, 1.15
    b, d, e = tf([b], dx, dy, s)[0], tf(d, dx, dy, s), tf(e, dx, dy, s)
    tail = sides(spl([(-1.3, 0.1), (-2.1, -0.05), (-2.85, -0.3), (-3.1, -1.0), (-2.95, -1.8)], closed=False), lambda t: 0.16 - 0.1 * t)
    tail = hide(tail, b)
    cheese = hide([top], b) + [front, side] + holes
    crumbs = [lens((1.6, 0.9), (1.85, 1.05), 0.4, 6)][:0]
    ground = [[(-3.3, -2.3), (-2.8, -2.3)], [(2.4, -1.75), (3.3, -1.75)]][:0]
    return make("Fancy Mouse on a Cheese Wedge", [b] + d + tail + cheese, e)


@design("pets_mouse_maze", T)
def mouse_maze(rng):
    import random
    R = random.Random(11)
    n, c = 6, 0.95
    x0, y0 = -n * c / 2, -n * c / 2
    seen = {(0, 0)}
    walls = {(i, j, d) for i in range(n) for j in range(n) for d in "ER"}  # E: right wall, R: top wall
    stack = [(0, 0)]
    while stack:
        i, j = stack[-1]
        nb = [(i + di, j + dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= i + di < n and 0 <= j + dj < n and (i + di, j + dj) not in seen]
        if not nb:
            stack.pop()
            continue
        a, b_ = R.choice(nb)
        if a != i:
            walls.discard((min(a, i), j, "E"))
        else:
            walls.discard((i, min(b_, j), "R"))
        seen.add((a, b_))
        stack.append((a, b_))
    segs = []
    for (i, j, d) in walls:
        if d == "E" and i < n - 1:
            segs.append([(x0 + (i + 1) * c, y0 + j * c), (x0 + (i + 1) * c, y0 + (j + 1) * c)])
        if d == "R" and j < n - 1:
            segs.append([(x0 + i * c, y0 + (j + 1) * c), (x0 + (i + 1) * c, y0 + (j + 1) * c)])
    X1, Y1 = x0 + n * c, y0 + n * c
    border = [[(x0, y0 + c), (x0, Y1), (X1, Y1)], [(X1, Y1 - c), (X1, y0), (x0, y0)]]
    # mouse seen from above, entering bottom-left gap
    m = spl([(x0 - 0.15, y0 + 0.5 * c), (x0 - 0.45, y0 + 0.7 * c), (x0 - 1.0, y0 + 0.72 * c), (x0 - 1.35, y0 + 0.5 * c),
             (x0 - 1.0, y0 + 0.28 * c), (x0 - 0.45, y0 + 0.3 * c)])
    mears = [circle(x0 - 0.5, y0 + 0.5 * c + 0.3, 0.16, 14), circle(x0 - 0.5, y0 + 0.5 * c - 0.3, 0.16, 14)]
    mtail = [spl([(x0 - 1.35, y0 + 0.5 * c), (x0 - 1.7, y0 + 0.8 * c), (x0 - 1.9, y0 + 0.2 * c)], closed=False)]
    cy = Y1 - 0.5 * c
    cheese = [poly((X1 + 0.2, cy - 0.3), (X1 + 1.2, cy - 0.3), (X1 + 1.2, cy + 0.15), (X1 + 0.2, cy - 0.05)),
              circle(X1 + 0.85, cy - 0.12, 0.08, 8)]
    return make("Mouse Running a Maze", border + segs + [m] + mears + mtail + cheese,
                [eye(x0 - 0.3, y0 + 0.5 * c + 0.12, 0.06), eye(x0 - 0.3, y0 + 0.5 * c - 0.12, 0.06)])


@design("pets_degu_log", T)
def degu_log(rng):
    log = [spl([(-3.0, -0.8), (3.0, -0.6)], closed=False), spl([(-3.0, -2.6), (3.0, -2.5)], closed=False),
           ellipse(3.0, -1.55, 0.35, 0.95, 40)]
    rings = [ellipse(3.0, -1.55, 0.2, 0.55, 30)]
    bark = [spl([(x, -0.95), (x + 0.3, -1.4), (x + 0.1, -1.9)], closed=False) for x in (-2.3, -1.0, 0.6, 1.8)]
    body = spl([(1.85, 0.35), (1.65, 0.8), (1.15, 1.05), (0.4, 1.2), (-0.4, 1.15), (-1.05, 0.85), (-1.35, 0.35), (-1.3, -0.2),
                (-1.4, -0.65, 0), (-0.85, -0.68, 0), (-0.8, -0.35), (0.6, -0.3), (0.72, -0.62, 0), (1.12, -0.62, 0), (1.1, -0.35),
                (1.5, -0.1), (1.8, 0.1)])
    ear = spl([(0.9, 1.1), (0.75, 1.55), (1.1, 1.75), (1.32, 1.4), (1.22, 1.03)], closed=False)
    thigh = spl([(-0.85, -0.38), (-0.6, 0.3), (-0.1, 0.25), (0.0, -0.3)], closed=False)
    tailc = cubic((-1.3, 0.2), (-2.0, 0.1), (-2.5, -0.1), (-2.85, 0.6), 30)
    tail = sides(tailc, lambda t: 0.2 - 0.08 * t)
    tuft = lens((-2.82, 0.5), (-2.95, 1.3), 0.3, 10)
    twig = [[(1.7, -0.05), (2.7, 0.6)], [(2.3, 0.33), (2.55, 0.85)]]
    leaf = [lens((2.55, 0.85), (2.75, 1.4), 0.35)]
    wh = [[(1.8, 0.3), (2.3, 0.45)], [(1.8, 0.25), (2.3, 0.05)]]
    paw = [ellipse(1.55, -0.05, 0.2, 0.13, 12)]
    out = tf([body, ear, thigh] + hide(tail, body) + [tuft] + hide(twig, *paw) + leaf + wh + paw, 0, 0.1, 1.0)
    return make("Degu Nibbling a Twig", out + log + rings + bark, [eye(1.3, 0.62, 0.12)])


# ------------------------------------------------------------ sugar gliders

@design("pets_sugar_glider_gliding", T)
def sugar_glider_gliding(rng):
    half = [(0, 2.55), (0.4, 2.48), (0.58, 2.2), (0.6, 1.85), (0.8, 1.55), (2.35, 2.0, 0), (2.3, 1.75), (2.1, 1.1), (2.15, 0.35),
            (2.0, -0.4), (2.25, -1.05, 0), (1.2, -1.15), (0.55, -1.35), (0.22, -1.55, 0), (0, -1.55)]
    body = sym(half)
    tail = sym([(0, -1.55), (0.28, -1.62, 0), (0.48, -2.3), (0.38, -3.0), (0, -3.4), ], closed=False)
    tail = spl([(0.22, -1.55), (0.45, -2.2), (0.4, -2.9), (0.0, -3.35), (-0.4, -2.9), (-0.45, -2.2), (-0.22, -1.55)], closed=False)
    ears = []
    for sx in (1, -1):
        ears.append(spl([(sx * 0.28, 2.5), (sx * 0.45, 2.95), (sx * 0.82, 2.98), (sx * 0.8, 2.6), (sx * 0.56, 2.3)], closed=False))
    fingers = []
    for sx in (1, -1):
        fingers += [[(sx * 2.35, 2.0), (sx * 2.6, 2.25)], [(sx * 2.35, 2.0), (sx * 2.68, 2.0)], [(sx * 2.25, 1.85), (sx * 2.55, 1.7)]]
        fingers += [[(sx * 2.25, -1.05), (sx * 2.55, -1.2)], [(sx * 2.25, -1.05), (sx * 2.45, -1.4)]]
    stripe = [[(0, 2.45), (0, -1.3)]]
    limbs = [spl([(sx * 0.65, 1.5), (sx * 1.4, 1.5), (sx * 2.2, 1.85)], closed=False) for sx in (1, -1)]
    limbs += [spl([(sx * 0.55, -1.0), (sx * 1.3, -0.95), (sx * 2.15, -0.95)], closed=False) for sx in (1, -1)]
    face = [spl([(-0.12, 1.55), (0.0, 1.45), (0.12, 1.55)], closed=False)]
    rings = [circle(sx * 0.3, 2.0, 0.2, 18) for sx in (1, -1)]
    stars_ = [star(x, y, 0.25) for x, y in [(-2.6, 3.0), (2.7, -2.6), (-2.3, -2.4)]]
    moon = [chain(arc(2.4, 2.9, 0.45, math.radians(100), math.radians(340), 20), arc(2.6, 3.05, 0.35, math.radians(300), math.radians(120), 16)[::-1])]
    return make("Sugar Glider Gliding", [body, tail] + ears + fingers + hide(stripe, *rings) + limbs + face + rings + stars_ + moon,
                [eye(sx * 0.3, 2.0, 0.13) for sx in (1, -1)])


@design("pets_sugar_glider_pouch", T)
def sugar_glider_pouch(rng):
    pouch = spl([(-2.0, 0.3, 0), (-2.1, -1.5), (-1.6, -2.7), (0.0, -3.0), (1.6, -2.7), (2.1, -1.5), (2.0, 0.3, 0)], closed=False)
    lip = [rrect(-2.2, 0.0, 2.2, 0.5, 0.2)]
    zip_ = [[(x, 0.05), (x, 0.45)] for x in ()]
    strap = [cubic((-1.9, 0.5), (-1.6, 2.6), (1.6, 2.6), (1.9, 0.5), 40), cubic((-1.6, 0.5), (-1.4, 2.25), (1.4, 2.25), (1.6, 0.5), 40)]
    head = sym([(0, 1.55), (0.45, 1.5), (0.8, 1.25), (0.95, 0.9), (0.85, 0.5), (0.5, 0.3), (0, 0.25)])
    ears = []
    for sx in (1, -1):
        ears.append(spl([(sx * 0.55, 1.42), (sx * 0.95, 2.1), (sx * 1.45, 2.0), (sx * 1.35, 1.45), (sx * 0.9, 1.08)], closed=False))
        ears.append(spl([(sx * 0.75, 1.42), (sx * 1.0, 1.85), (sx * 1.25, 1.8), (sx * 1.15, 1.45)], closed=False))
    stripe = [[(0, 1.55), (0, 1.0)]]
    nose = [poly((-0.1, 0.62), (0.1, 0.62), (0, 0.5))]
    paws = [ellipse(sx * 0.65, 0.5, 0.22, 0.14, 12) for sx in (1, -1)]
    fingers = [[(sx * 0.6 + d, 0.36), (sx * 0.6 + d, 0.25)] for sx in (1, -1) for d in (-0.08, 0.08)]
    eyes_o = [circle(sx * 0.4, 0.95, 0.22, 18) for sx in (1, -1)]
    gl = hide([head] + ears + stripe + nose + eyes_o, *paws, lip[0])
    strap_v = hide(strap, head, *ears)
    hearts = [heart(0, -1.4, 0.5), heart(-1.2, -1.0, 0.25), heart(1.2, -1.0, 0.25)]
    seams = [spl([(-1.85, -0.2), (-1.9, -1.5), (-1.45, -2.45), (0.0, -2.75), (1.45, -2.45), (1.9, -1.5), (1.85, -0.2)], closed=False)]
    return make("Sugar Glider in a Bonding Pouch", [pouch] + lip + zip_ + strap_v + gl + paws + hearts + seams,
                [eye(sx * 0.4, 0.95, 0.13) for sx in (1, -1)])


# ------------------------------------------------------------------- birds

def note(x, y, s=1.0):
    return [ellipse(x, y, 0.2 * s, 0.14 * s, 14, rot=0.4), [(x + 0.18 * s, y + 0.05 * s), (x + 0.18 * s, y + 0.85 * s)],
            quad((x + 0.18 * s, y + 0.85 * s), (x + 0.45 * s, y + 0.6 * s), (x + 0.4 * s, y + 0.35 * s), 6)]


@design("pets_cockatiel", T)
def cockatiel(rng):
    body = spl([(1.0, 1.72), (1.05, 1.0), (0.85, 0.0), (0.45, -0.75), (0.0, -1.0), (-0.35, -1.45), (-0.75, -2.6), (-0.95, -3.1, 0),
                (-0.68, -3.15, 0), (-0.3, -2.3), (-0.05, -1.6), (-0.4, -1.1), (-0.58, -0.4), (-0.55, 0.4), (-0.35, 1.25),
                (-0.05, 1.95), (0.45, 2.32), (0.85, 2.22), (1.05, 1.98)])
    beak = spl([(1.04, 2.05), (1.38, 1.92), (1.32, 1.62, 0), (1.15, 1.7), (1.0, 1.72)], closed=False)
    crest = [spl([(0.55, 2.32), (0.45, 2.85), (0.05, 3.45), (0.3, 2.75), (0.25, 2.25)], closed=False),
             spl([(0.35, 2.55), (0.0, 2.95), (-0.4, 3.15), (-0.05, 2.6)], closed=False),
             spl([(0.75, 2.27), (0.75, 2.75), (0.5, 3.2)], closed=False)]
    cheek = circle(0.72, 1.72, 0.22, 20)
    wing = spl([(0.25, 1.35), (0.55, 0.6), (0.45, -0.35), (-0.15, -1.3), (-0.5, -1.75, 0), (-0.5, -0.8), (-0.4, 0.3), (-0.15, 1.1)])
    wing_lines = [spl([(0.35, 0.2), (0.05, -0.4), (-0.25, -1.0)], closed=False), spl([(0.1, 0.9), (-0.15, 0.1), (-0.3, -0.5)], closed=False)]
    feet = [arc(x, -0.95, 0.13, math.pi, TAU, 6) for x in (0.2, 0.48)]
    perch = [rrect(-3.0, -1.3, 3.0, -0.97, 0.15)]
    perch = hide(perch, body)
    millet = [[(2.3, 3.2), (2.3, 1.9)], spl([(2.3, 1.9), (2.1, 1.2), (2.25, 0.2), (2.5, 0.25), (2.6, 1.2), (2.4, 1.9)])]
    grains = [arc(2.35, y, 0.18, math.radians(200), math.radians(340), 6) for y in (1.5, 1.1, 0.7)]
    tail_lines = [[(-0.75, -2.85), (-0.35, -1.8)]]
    return make("Cockatiel with a Crest", [body, beak, cheek, wing] + crest + wing_lines + hide(feet, wing) + perch + millet + grains + tail_lines,
                [eye(0.5, 2.02, 0.11)])


@design("pets_canary_swing", T)
def canary_swing(rng):
    body = spl([(1.05, 1.5), (0.85, 1.95), (0.35, 2.15), (-0.15, 1.95), (-0.55, 1.4), (-0.95, 0.75), (-1.55, 0.35), (-1.95, 0.15, 0),
                (-1.8, -0.05, 0), (-1.2, -0.05), (-0.6, -0.35), (0.25, -0.35), (0.8, 0.15), (1.0, 0.8), (1.0, 1.2)])
    beak_u = poly((0.98, 1.6), (1.45, 1.62), (1.0, 1.4), closed=False)
    beak_l = poly((1.0, 1.35), (1.4, 1.2), (0.97, 1.2), closed=False)
    wing = spl([(-0.1, 1.2), (-0.9, 0.5), (-1.55, 0.15), (-0.8, 0.0), (-0.1, 0.25), (0.25, 0.75)])
    wing_l = [spl([(-0.3, 0.75), (-0.8, 0.3)], closed=False)]
    feet = [arc(x, -0.45, 0.13, math.pi, TAU, 6) for x in (-0.15, 0.2)]
    dy = -0.1
    tri = [[(0.0, 3.2), (-1.9, -0.5)], [(0.0, 3.2), (1.9, -0.5)]]
    beads = [circle(-1.9 * t, 3.2 - 3.7 * t, 0.16, 14) for t in (0.35, 0.65)] + [circle(1.9 * t, 3.2 - 3.7 * t, 0.16, 14) for t in (0.35, 0.65)]
    tri = hide(tri, *beads)
    dowel = [rrect(-2.1, -0.75, 2.1, -0.45, 0.12)]
    hook = [arc(0.0, 3.4, 0.2, -math.pi / 2, math.pi, 10)]
    bird = tf([body, beak_u, beak_l, wing] + wing_l + feet, 0.0, dy + 0.0, 1.0)
    tri = hide(tri, bird[0])
    notes = note(1.9, 1.7, 1.0) + note(2.5, 2.5, 0.8)
    return make("Canary Singing on a Swing", bird + tri + beads + dowel + hook + notes, [eye(0.55, 1.7, 0.1)])


def finch(x, y, s=1.0, flip=False):
    body = spl([(0.85, 0.95), (0.6, 1.25), (0.15, 1.3), (-0.3, 1.05), (-0.6, 0.6), (-1.05, 0.35), (-1.4, 0.25, 0), (-1.3, 0.05, 0),
                (-0.9, 0.05), (-0.45, -0.2), (0.2, -0.2), (0.65, 0.2), (0.8, 0.6)])
    beak = poly((0.82, 1.05), (1.25, 0.85), (0.8, 0.62), closed=False)
    cheek = ellipse(0.35, 0.75, 0.2, 0.17, 16)
    tear = [[(0.62, 0.9), (0.62, 0.55)]]
    bars = [spl([(0.7, 0.45 - 0.13 * k), (0.55, 0.35 - 0.13 * k), (0.4, 0.42 - 0.13 * k)], closed=False) for k in range(2)]
    wing = spl([(-0.1, 0.85), (-0.6, 0.45), (-1.0, 0.25), (-0.4, 0.1), (0.1, 0.35)])
    tail_bars = [[(-1.0, 0.27), (-1.05, 0.1)], [(-1.2, 0.24), (-1.18, 0.07)]]
    feet = [arc(xx, -0.3, 0.1, math.pi, TAU, 6) for xx in (-0.15, 0.15)]
    st = tf([body, beak, cheek, wing] + tear + bars + tail_bars + feet, x, y, s, flip)
    return st, [eye(*pt((0.5, 1.0), x, y, s, flip), 0.08 * s)]


@design("pets_zebra_finches", T)
def zebra_finches(rng):
    a, ha = finch(-1.35, 0.25, 1.3)
    b_, hb = finch(1.55, 0.25, 1.15)
    branch = [spl([(-3.2, -0.35), (-1.0, -0.15), (1.0, -0.1), (3.2, -0.3)], closed=False),
              spl([(-3.2, -0.75), (-1.0, -0.55), (1.0, -0.5), (3.2, -0.7)], closed=False)]
    twig = [spl([(1.9, -0.55), (2.3, -1.3), (2.4, -2.0)], closed=False)]
    leaves = [lens((2.3, -1.3), (2.9, -1.6), 0.35), lens((2.38, -1.8), (1.9, -2.3), 0.35), lens((-2.6, -0.65), (-3.0, -1.25), 0.35)]
    branch = hide(branch, a[0], b_[0])
    return make("Zebra Finches on a Branch", a + b_ + branch + twig + leaves, ha + hb)


# -------------------------------------------------------------------- fish

def fish_simple(x, y, s=1.0, flip=False):
    body = spl([(-0.9, 0.0), (-0.4, 0.42), (0.3, 0.38), (0.75, 0.05, 0), (1.15, 0.38, 0), (1.05, 0.0), (1.15, -0.38, 0),
                (0.75, -0.05, 0), (0.3, -0.38), (-0.4, -0.42)])
    gill = arc(-0.55, 0.0, 0.3, -0.9, 0.9, 6)
    fin = poly((-0.1, 0.4), (0.25, 0.65), (0.3, 0.38), closed=False)
    st = tf([body, gill, fin], x, y, s, flip)
    return st, [eye(*pt((-0.6, 0.1), x, y, s, flip), 0.07 * s)]


@design("pets_betta_fish", T)
def betta_fish(rng):
    body = spl([(-2.1, 0.15), (-1.5, 0.7), (-0.4, 0.85), (0.6, 0.6), (1.0, 0.35), (1.0, -0.2), (0.4, -0.55), (-0.6, -0.62),
                (-1.5, -0.45), (-2.05, -0.1)])
    tail = spl([(1.0, 0.35), (1.5, 1.4), (2.2, 2.25), (2.55, 1.85), (2.95, 1.75), (3.05, 1.1), (3.35, 0.65), (3.1, 0.0),
                (3.35, -0.65), (3.0, -1.2), (2.95, -1.85), (2.5, -1.9), (2.15, -2.4), (1.5, -1.5), (1.0, -0.2)], closed=False)
    rays = [quad((1.05, 0.1), (1.8, 0.1 + 0.4 * k), (2.9, 0.15 + 0.7 * k), 10) for k in (-2, -1, 0, 1, 2)]
    dorsal = spl([(-0.5, 0.85), (-0.1, 1.6), (0.5, 2.15), (1.2, 2.3), (1.45, 1.6), (1.05, 0.9), (0.6, 0.6)], closed=False)
    anal = spl([(-0.7, -0.62), (-0.4, -1.5), (0.2, -2.3), (1.0, -2.75), (1.55, -2.1), (1.2, -1.2), (0.7, -0.45)], closed=False)
    d_rays = [quad((0.0, 0.9), (0.4, 1.5), (0.9, 2.1), 8), quad((0.4, 0.75), (0.8, 1.3), (1.2, 1.7), 8)]
    a_rays = [quad((-0.2, -0.65), (0.2, -1.4), (0.8, -2.3), 8), quad((0.3, -0.6), (0.7, -1.2), (1.2, -1.75), 8)]
    pelvic = lens((-1.0, -0.55), (-0.7, -1.9), 0.18, 16)
    pect = lens((-1.05, -0.05), (-0.45, -0.35), 0.35, 10)
    gill = spl([(-1.3, 0.62), (-1.15, 0.1), (-1.3, -0.4)], closed=False)
    mouth = [[(-2.1, 0.02), (-1.85, 0.0)]]
    scales = [arc(x, y, 0.22, -1.2, 1.2, 6) for x, y in [(-0.7, 0.35), (-0.2, 0.35), (0.3, 0.3), (-0.45, -0.15), (0.05, -0.15)]]
    bubbles = [circle(-2.5, 1.1, 0.16, 14), circle(-2.8, 1.7, 0.22, 16), circle(-2.45, 2.4, 0.13, 12)]
    return make("Betta Fish with Flowing Fins", [body, tail, dorsal, anal, pelvic, gill] + hide(rays, body) + hide(d_rays + a_rays, body)
                + hide([pect], body)[:0] + [pect] + mouth + scales + bubbles, [eye(-1.6, 0.3, 0.12)])


@design("pets_home_aquarium", T)
def home_aquarium(rng):
    tank = [rect(-3.0, -1.6, 3.0, 1.9), rect(-3.1, 1.9, 3.1, 2.35)]
    stand = [rect(-2.8, -3.0, 2.8, -1.6), [(0.0, -3.0), (0.0, -1.6)], circle(-0.3, -2.3, 0.08, 8), circle(0.3, -2.3, 0.08, 8)]
    water = [wave(-3.0, 3.0, 1.55, 0.05, 6, 80)]
    gravel = [spl([(-3.0, -1.15), (-1.5, -1.0), (0.0, -1.2), (1.5, -1.0), (3.0, -1.15)], closed=False)]
    stones = [ellipse(x, -1.35, 0.17, 0.1, 10) for x in (-2.5, -1.8, -0.4, 0.9, 2.1, 2.6)]
    cx = -1.55
    castle = poly((cx - 0.9, -1.1), (cx - 0.9, 0.0), (cx - 0.9, 0.25), (cx - 0.65, 0.25), (cx - 0.65, 0.05), (cx - 0.4, 0.05), (cx - 0.4, 0.25),
                  (cx - 0.2, 0.25), (cx - 0.2, -0.3), (cx + 0.2, -0.3), (cx + 0.2, 0.65), (cx + 0.4, 0.65), (cx + 0.4, 0.45), (cx + 0.6, 0.45),
                  (cx + 0.6, 0.65), (cx + 0.8, 0.65), (cx + 0.8, -1.1), closed=False)
    door = chain([(cx - 0.3, -1.1), (cx - 0.3, -0.75)], arc(cx, -0.75, 0.3, math.pi, 0, 10), [(cx + 0.3, -1.1)])
    win = [rrect(cx + 0.38, 0.0, cx + 0.62, 0.3, 0.1)]
    plants = [lens((1.9, -1.05), (1.6, 1.0), 0.12), lens((2.2, -1.05), (2.5, 0.6), 0.12), lens((2.45, -1.05), (2.9, 0.1), 0.12),
              lens((-2.7, -1.05), (-2.6, 0.5), 0.12)]
    f1, h1 = fish_simple(0.6, 0.85, 0.8, flip=True)
    f2, h2 = fish_simple(-0.2, -0.2, 0.65)
    f3, h3 = fish_simple(1.3, 0.0, 0.5)
    plants = hide(plants, f3[0])
    bubbles = [circle(-0.2 + 0.08 * (k % 2), -0.9 + 0.55 * k, 0.1 + 0.02 * k, 12) for k in range(4)][:0]
    bub = [circle(0.15, y, r, 12) for y, r in [(0.55, 0.1), (1.0, 0.12), (1.35, 0.09)]]
    light = [[(-2.6, 2.1), (2.6, 2.1)]]
    return make("Home Aquarium with a Castle", tank + stand + water + gravel + stones + [castle, door] + win + plants + f1 + f2 + f3 + bub
                + light, h1 + h2 + h3)


@design("pets_pleco_catfish", T)
def pleco(rng):
    body = spl([(-2.6, -0.5), (-2.4, 0.05), (-1.8, 0.45), (-0.9, 0.55), (0.3, 0.45), (1.4, 0.25), (2.0, 0.12), (2.0, -0.35),
                (1.3, -0.55), (0.0, -0.75), (-1.4, -0.85), (-2.3, -0.8)])
    tail = spl([(2.0, 0.12), (2.6, 0.75), (3.2, 1.15, 0), (2.95, 0.4), (2.9, -0.55), (3.2, -1.35, 0), (2.6, -0.95), (2.0, -0.35)], closed=False)
    sail = spl([(-1.2, 0.55), (-1.0, 1.4), (-0.5, 2.0, 0), (0.1, 1.8), (0.7, 1.45), (1.2, 0.9), (1.3, 0.3)], closed=False)
    sail_rays = [[(-1.0 + 0.45 * k, 0.55 - 0.03 * k), (-0.7 + 0.42 * k, 1.85 - 0.22 * k)] for k in range(1, 4)]
    pect = lens((-1.4, -0.65), (-0.4, -1.4), 0.3)
    pelvic = lens((0.4, -0.65), (1.1, -1.15), 0.3)
    adip = poly((1.6, 0.2), (1.8, 0.55), (1.95, 0.15), closed=False)
    plates = [spl([(x, 0.45), (x + 0.15, -0.1), (x, -0.7)], closed=False) for x in (-1.6, -1.0, -0.4, 0.2, 0.8, 1.35)]
    mouth = [ellipse(-2.45, -0.75, 0.25, 0.12, 14)]
    barbel = [quad((-2.6, -0.7), (-2.9, -0.8), (-3.0, -1.05), 6)]
    spots = [circle(x, y, 0.07, 6) for x, y in [(-1.3, 0.1), (-0.7, -0.25), (0.0, 0.1), (0.5, -0.3), (1.1, 0.0), (-0.2, 1.1), (0.4, 0.95)]]
    wood = [spl([(-3.2, -1.55), (-1.5, -1.1), (0.5, -1.25), (2.0, -1.4), (3.3, -1.9)], closed=False),
            spl([(-3.2, -2.3), (-1.0, -2.0), (1.0, -2.2), (3.3, -2.6)], closed=False),
            spl([(0.5, -1.25), (0.9, -0.8), (1.5, -0.6)], closed=False)[:0] or [(-1.5, -1.6), (-0.4, -1.75)]]
    wood = hide(wood, pect, pelvic)
    return make("Pleco Catfish on Driftwood", [body, tail, sail] + hide(sail_rays, body) + [pect, pelvic, adip] + plates + mouth + barbel
                + spots + wood, [eye(-1.75, 0.15, 0.1)])


@design("pets_fish_bag", T)
def fish_bag(rng):
    bag = spl([(-0.3, 1.9, 0), (-1.2, 1.1), (-2.3, 0.0), (-2.6, -1.4), (-2.0, -2.55), (0.0, -2.95), (2.0, -2.55), (2.6, -1.4),
               (2.3, 0.0), (1.2, 1.1), (0.3, 1.9, 0)], closed=False)
    neck = [spl([(-0.3, 1.9), (-0.25, 2.3), (-0.6, 3.1), (-0.2, 3.3), (0.2, 3.3), (0.6, 3.1), (0.25, 2.3), (0.3, 1.9)], closed=False)]
    tie = [rrect(-0.42, 1.95, 0.42, 2.25, 0.08)]
    bow = [lens((0.4, 2.1), (1.2, 2.5), 0.35), lens((0.4, 2.1), (1.1, 1.65), 0.35)]
    water = [wave(-2.15, 2.15, 0.25, 0.08, 3, 60)]
    f, h = fish_simple(-0.1, -1.0, 1.7, flip=True)
    bubbles = [circle(-1.2, -0.3, 0.15, 12), circle(-1.5, 0.0, 0.1, 10), circle(1.4, -1.9, 0.12, 10)]
    shine = [spl([(1.6, -0.2), (2.0, -1.0), (1.95, -1.8)], closed=False)]
    gravel = [spl([(-2.3, -2.3), (-1.0, -2.1), (1.0, -2.1), (2.3, -2.3)], closed=False)]
    return make("New Pet Fish in a Take-Home Bag", [bag] + neck + tie + bow + water + f + bubbles + shine + gravel, h)


# ------------------------------------------------- reptiles & amphibians

@design("pets_axolotl", T)
def axolotl(rng):
    body = spl([(0, 2.55), (0.7, 2.45), (1.2, 2.1), (1.35, 1.6), (1.2, 1.05), (0.75, 0.72), (0.68, 0.0), (0.62, -0.8), (0.5, -1.4),
                (0.75, -1.95), (1.35, -2.35), (2.2, -2.5), (2.95, -2.25, 0), (2.15, -2.95), (1.1, -3.05), (0.2, -2.65), (-0.4, -1.9),
                (-0.62, -1.2), (-0.68, 0.0), (-0.75, 0.72), (-1.2, 1.05), (-1.35, 1.6), (-1.2, 2.1), (-0.7, 2.45)])
    fin = spl([(0.1, -0.6), (-0.05, -1.5), (0.3, -2.25), (1.1, -2.65), (2.1, -2.7)], closed=False)
    gills = []
    for sx in (1, -1):
        for (bx, by), (tx, ty) in [((1.15, 2.05), (2.15, 2.85)), ((1.33, 1.65), (2.5, 1.85)), ((1.25, 1.25), (2.25, 0.75))]:
            g = lens((sx * bx, by), (sx * tx, ty), 0.22, 20)
            gills.append(g)
            mx, my = (bx + tx) / 2, (by + ty) / 2
            gills.append([(sx * bx, by), (sx * tx, ty)])
    gills = hide(gills, body)
    legs = []
    for sx in (1, -1):
        legs.append(tube([(sx * 0.6, 0.35), (sx * 1.1, 0.1), (sx * 1.45, -0.2)], 0.3))
        legs += [[(sx * 1.5, -0.25), (sx * (1.5 + 0.3 * math.cos(a)), -0.25 + 0.3 * math.sin(a))] for a in ((-0.2, -0.8, -1.4) if sx > 0 else (math.pi + 0.2, math.pi + 0.8, math.pi + 1.4))]
        legs.append(tube([(sx * 0.5, -1.0), (sx * 0.95, -1.3), (sx * 1.2, -1.65)], 0.28))
    legs = hide(legs, body)
    smile = [spl([(-0.5, 1.45), (0.0, 1.25), (0.5, 1.45)], closed=False)]
    spots = [circle(x, y, 0.09, 8) for x, y in [(0.2, 0.5), (-0.3, 0.1), (0.25, -0.5), (-0.2, -1.0), (0.9, -2.5), (1.6, -2.65)]]
    blush = [ellipse(sx * 0.85, 1.45, 0.17, 0.1, 12) for sx in (1, -1)]
    return make("Smiling Axolotl", [body, fin] + gills + legs + smile + spots + blush, [eye(sx * 0.55, 1.92, 0.13) for sx in (1, -1)])


@design("pets_red_eared_slider", T)
def red_eared_slider(rng):
    dome = chain([(-2.1, -0.1)], arc(0, -0.6, 2.15, math.radians(166), math.radians(14), 60), [(2.1, -0.1)])
    rim = [[(-2.25, -0.1), (2.25, -0.1)], [(-2.1, -0.45), (2.1, -0.45)], [(-2.25, -0.1), (-2.1, -0.45)], [(2.25, -0.1), (2.1, -0.45)]]
    marg = [[(x, -0.1), (x, -0.45)] for x in (-1.5, -0.75, 0.0, 0.75, 1.5)]
    scutes = [poly((-0.55, 0.35), (-0.3, 1.05), (0.3, 1.05), (0.55, 0.35), (0.3, -0.1), closed=False),
              [(-0.3, -0.1), (-0.55, 0.35)], [(-0.3, 1.05), (-0.55, 1.45)], [(0.3, 1.05), (0.55, 1.45)],
              [(-0.55, 0.35), (-1.45, 0.75)], [(0.55, 0.35), (1.45, 0.75)], [(-1.2, -0.1), (-0.95, 0.5)], [(1.2, -0.1), (0.95, 0.5)]]
    neck = spl([(1.85, -0.3), (2.3, 0.05), (2.75, 0.45), (3.2, 0.55), (3.45, 0.35, 0), (3.3, 0.12), (2.85, -0.05), (2.4, -0.4), (2.05, -0.6)],
               closed=False)
    stripes = [spl([(2.25, -0.25), (2.7, 0.1), (3.2, 0.25)], closed=False), spl([(2.2, -0.42), (2.6, -0.2)], closed=False)]
    ear = [ellipse(2.75, 0.3, 0.2, 0.09, 12, rot=0.3)]
    fl = spl([(1.2, -0.45), (1.55, -1.0), (1.75, -1.15, 0), (2.15, -1.1, 0), (1.95, -0.95), (1.75, -0.45)], closed=False)
    bl = spl([(-1.2, -0.45), (-1.55, -1.0), (-1.75, -1.15, 0), (-2.15, -1.1, 0), (-1.95, -0.95), (-1.75, -0.45)], closed=False)
    claws = [[(2.15, -1.1), (2.3, -1.2)], [(1.95, -1.15), (2.05, -1.28)], [(-2.15, -1.1), (-2.3, -1.2)]]
    tail = poly((-2.25, -0.3), (-2.65, -0.55), (-2.2, -0.45), closed=False)
    rock = spl([(-3.2, -2.1), (-2.9, -1.4), (-2.0, -1.1), (0.0, -1.15), (2.0, -1.1), (2.8, -1.3), (3.2, -2.1)], closed=False)
    water = [wave(-3.4, -3.2, -2.1, 0.0, 1, 4), wave(-3.4, 3.4, -2.3, 0.07, 6, 80), wave(-2.8, 2.8, -2.75, 0.07, 5, 70)]
    water = water[1:]
    rock = hide([rock], fl, bl)
    lamp = [chain(arc(2.4, 2.0, 0.75, math.radians(200), math.radians(340), 20)), [(1.7, 1.75), (3.1, 1.75)][:0] or
            [(2.4 - 0.75 * math.cos(math.radians(20)), 2.0 - 0.75 * math.sin(math.radians(20))), (2.4 + 0.75 * math.cos(math.radians(20)), 2.0 - 0.75 * math.sin(math.radians(20)))],
            [(2.4, 2.75), (2.4, 3.3)]]
    lamp[0] = arc(2.4, 2.0, 0.75, math.radians(160), math.radians(380), 24)
    rays = [[(2.4 + 0.95 * math.cos(a), 1.9 + 0.95 * math.sin(a)), (2.4 + 1.3 * math.cos(a), 1.9 + 1.3 * math.sin(a))]
            for a in [math.radians(d) for d in (215, 250, 290, 325)]]
    return make("Red-Eared Slider on a Basking Rock", [dome] + rim + marg + scutes + [neck] + stripes + ear + [fl, bl] + claws + [tail]
                + rock + water + lamp + rays, [eye(3.08, 0.38, 0.08)])


@design("pets_bearded_dragon", T)
def bearded_dragon(rng):
    pts = [(3.05, 0.55, 0), (2.85, 0.95), (2.45, 1.2), (2.0, 1.25), (1.7, 1.15)]
    x = 1.5
    while x > -0.9:
        pts += [(x, 1.32 - 0.05 * (1.5 - x), 0), (x - 0.18, 1.12 - 0.06 * (1.5 - x))]
        x -= 0.36
    pts += [(-1.3, 0.75), (-2.0, 0.45), (-3.3, 0.05, 0), (-2.0, 0.1), (-1.3, 0.05), (-0.5, 0.0), (0.8, 0.0), (1.5, 0.15),
            (1.75, -0.15, 0), (1.95, 0.15), (2.15, -0.12, 0), (2.35, 0.18), (2.55, -0.05, 0), (2.7, 0.25), (2.95, 0.25)]
    body = spl(pts)
    jaw = spl([(1.7, 1.15), (1.62, 0.6), (1.6, 0.2)], closed=False)
    mouth = [spl([(3.0, 0.48), (2.6, 0.45), (2.3, 0.55)], closed=False)]
    legs = [spl([(0.95, 0.02), (0.85, -0.4), (1.0, -0.78, 0), (1.55, -0.78, 0), (1.5, -0.65), (1.2, -0.55), (1.3, -0.1), (1.35, 0.08)], closed=False),
            spl([(-1.05, 0.04), (-0.65, -0.35), (-0.95, -0.78, 0), (-0.35, -0.78, 0), (-0.4, -0.62), (-0.3, -0.3), (-0.5, 0.0)], closed=False)]
    toes = [[(1.55, -0.78), (1.8, -0.7)], [(1.5, -0.68), (1.75, -0.52)], [(-0.35, -0.78), (-0.1, -0.7)], [(-0.4, -0.66), (-0.15, -0.52)]]
    side = zigzag(-0.7, 1.2, 0.45, 0.07, 9)
    rock = spl([(-3.4, -0.8), (-2.0, -0.78), (0.0, -0.8), (2.5, -0.78), (3.3, -0.85)], closed=False)
    rock2 = spl([(-3.3, -0.8), (-3.1, -1.9), (-1.5, -2.3), (1.0, -2.35), (2.8, -2.0), (3.3, -0.85)], closed=False)
    cracks = [spl([(-1.6, -1.1), (-1.2, -1.5), (-1.3, -1.9)], closed=False), spl([(1.2, -1.2), (1.6, -1.6)], closed=False)]
    lamp = [arc(-2.2, 2.6, 0.6, math.radians(180), math.radians(360), 16), [(-2.8, 2.6), (-1.6, 2.6)], [(-2.2, 2.6), (-2.2, 3.2)]]
    rays = [[(-2.2 + 0.8 * math.cos(a), 2.4 + 0.8 * math.sin(a)), (-2.2 + 1.1 * math.cos(a), 2.4 + 1.1 * math.sin(a))]
            for a in [math.radians(d) for d in (220, 270, 320)]]
    return make("Bearded Dragon on a Rock", [body, jaw] + mouth + legs + toes + [side, rock, rock2] + cracks + lamp + rays, [eye(2.3, 0.9, 0.1)])


# dropped: the Jungle book has a gecko
def leopard_gecko(rng):
    half = [(0, 2.85), (0.42, 2.72), (0.72, 2.3), (0.75, 1.8), (0.52, 1.42), (0.75, 0.9), (0.85, 0.0), (0.72, -0.8), (0.5, -1.2),
            (0.68, -1.65), (0.72, -2.3), (0.45, -2.9), (0, -3.15)]
    body = sym(half)
    legs = []
    for sx in (1, -1):
        legs.append(spl([(sx * 0.75, 1.05), (sx * 1.35, 1.35), (sx * 1.6, 1.15), (sx * 1.15, 0.9), (sx * 0.8, 0.7)], closed=False))
        legs += [[(sx * 1.55, 1.25), (sx * 1.9, 1.5)], [(sx * 1.6, 1.15), (sx * 1.98, 1.15)], [(sx * 1.55, 1.05), (sx * 1.85, 0.8)]]
        legs.append(spl([(sx * 0.72, -0.65), (sx * 1.3, -0.35), (sx * 1.55, -0.6), (sx * 1.15, -0.95), (sx * 0.6, -1.05)], closed=False))
        legs += [[(sx * 1.5, -0.45), (sx * 1.85, -0.2)], [(sx * 1.55, -0.6), (sx * 1.95, -0.6)], [(sx * 1.45, -0.72), (sx * 1.75, -1.0)]]
    bands = [spl([(-0.66, y), (0.0, y - 0.12), (0.66, y)], closed=False) for y in (-1.8, -2.35)]
    spots = [circle(x, y, 0.11, 10) for x, y in [(-0.35, 0.95), (0.3, 0.75), (0.0, 0.3), (-0.45, -0.05), (0.42, -0.25), (-0.15, -0.65),
                                                  (0.3, -1.0), (0.0, 1.9), (-0.3, 2.35), (0.3, 2.3)]]
    mouth = [spl([(-0.4, 2.45), (0.0, 2.38), (0.4, 2.45)], closed=False)][:0]
    pebbles = [ellipse(x, y, 0.3, 0.2, 18) for x, y in [(-2.3, -2.5), (2.2, 2.4), (2.4, -2.2), (-2.4, 2.2)]]
    eyes_o = [ellipse(sx * 0.6, 2.2, 0.2, 0.25, 16) for sx in (1, -1)]
    return make("Leopard Gecko", [body] + legs + bands + spots + pebbles + eyes_o, [eye(sx * 0.6, 2.2, 0.09) for sx in (1, -1)])


def crested_gecko(rng):
    leaf = lens((-3.2, -1.6), (3.2, -0.6), 0.2, 50)
    rib = [spl([(-3.2, -1.6), (0.0, -1.0), (3.2, -0.6)], closed=False)]
    veins = [quad((x, -1.0 + 0.06 * x), (x + 0.35, -0.8 + 0.06 * x), (x + 0.75, -0.55 + 0.06 * x), 6) for x in (-2.2, -1.0, 0.2, 1.4)]
    veins += [quad((x, -1.05 + 0.06 * x), (x + 0.35, -1.35 + 0.06 * x), (x + 0.75, -1.5 + 0.06 * x), 6) for x in (-2.6, -1.4, -0.2, 1.0)]
    body = spl([(2.75, 0.65), (2.5, 1.05), (2.0, 1.15), (1.6, 0.95), (0.6, 0.85), (-0.4, 0.75), (-1.1, 0.5), (-1.6, 0.1), (-1.9, -0.4),
                (-1.7, -0.8), (-1.35, -0.75), (-1.45, -0.45), (-1.3, -0.15), (-0.9, 0.05), (-0.2, 0.0), (0.8, 0.05), (1.6, 0.15),
                (2.2, 0.3), (2.6, 0.45)])
    crest = zigzag(1.95, 2.55, 1.2, 0.06, 4)
    crest = [(x, y + 0.08 * (x - 2.0)) for x, y in crest]
    back_crest = zigzag(-0.6, 1.4, 0.95, 0.06, 7)
    legs = []
    for (x0, y0), (x1, y1) in [((1.4, 0.1), (1.8, -0.45)), ((-0.6, 0.0), (-0.95, -0.55)), ((1.0, 0.1), (0.7, -0.4))]:
        legs.append(tube([(x0, y0), ((x0 + x1) / 2 + 0.15, (y0 + y1) / 2), (x1, y1)], 0.22))
        legs += [circle(x1 + dx, y1 - 0.05 + dy, 0.09, 8) for dx, dy in ((-0.2, 0.0), (0.0, -0.1), (0.2, 0.0))]
    legs = hide(legs, body)
    mouth = [spl([(2.75, 0.62), (2.4, 0.55), (2.1, 0.62)], closed=False)]
    curl = [spiral(-1.55, -0.6, 0.05, 0.12, 0.5, 10)][:0]
    return make("Crested Gecko on a Leaf", hide([leaf] + rib + veins, body, *[l_ for l_ in legs if len(l_) > 20]) + [body] + [crest, back_crest]
                + legs + mouth, [eye(2.2, 0.82, 0.13)])


def path_pts(c, step):
    L = [0.0]
    for a, b in zip(c, c[1:]):
        L.append(L[-1] + math.dist(a, b))
    out, d, j = [], step / 2, 0
    while d < L[-1]:
        while L[j + 1] < d:
            j += 1
        a, b = c[j], c[j + 1]
        f = (d - L[j]) / ((L[j + 1] - L[j]) or 1)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, ang, d / L[-1]))
        d += step
    return out


@design("pets_corn_snake", T)
def corn_snake(rng):
    c = spl([(-2.7, -2.7), (-2.6, -1.4), (-2.1, 0.2), (-1.4, 0.5), (-0.9, -0.4), (-0.5, -1.5), (0.3, -1.6), (0.75, -0.5), (1.1, 0.45),
             (1.7, 0.75), (2.3, 1.2), (2.55, 1.85)], closed=False)
    w = lambda t: 0.18 + 0.32 * min(1.0, t * 3)
    snake = tube(c, w, cap=True)
    tip = c[0]
    blot = []
    for x, y, a, t in path_pts(c, 0.55)[1:-1]:
        blot.append(ellipse(x, y, 0.14, 0.09 + 0.06 * min(1.0, t * 3), 12, rot=a))
    hx, hy = c[-1]
    head = spl([(hx - 0.25, hy - 0.15), (hx - 0.3, hy + 0.2), (hx - 0.05, hy + 0.55), (hx + 0.3, hy + 0.6), (hx + 0.55, hy + 0.35),
                (hx + 0.45, hy - 0.05), (hx + 0.2, hy - 0.2)])
    tongue = [[(hx + 0.55, hy + 0.3), (hx + 0.85, hy + 0.42), (hx + 1.0, hy + 0.6)], [(hx + 0.85, hy + 0.42), (hx + 1.05, hy + 0.35)]]
    snake_v = hide([snake], head)
    branch = [spl([(-3.3, 0.05), (-1.0, 0.0), (1.0, 0.15), (3.3, 0.35)], closed=False), spl([(-3.3, -0.45), (-1.0, -0.5), (1.0, -0.35), (3.3, -0.15)], closed=False),
              spl([(0.3, -0.42), (0.9, -1.4), (1.2, -2.4)], closed=False)[:0] or [(2.2, 0.3), (2.9, 1.1)]]
    leaves = [lens((2.9, 1.1), (3.3, 1.7), 0.35), lens((2.9, 1.1), (3.5, 1.0), 0.35)]
    branch = hide(branch, snake)
    leaves = hide(leaves, snake, head)
    return make("Corn Snake on a Branch", snake_v + [head] + hide(blot, head) + tongue + branch + leaves, [eye(hx + 0.18, hy + 0.32, 0.08)])


@design("pets_ball_python", T)
def ball_python(rng):
    outer = circle(0, -0.3, 2.6, 160)
    sp = spiral(0, -0.3, 0.6, 2.6, 2.2, 260, rot=math.pi / 2)
    sp = [p for p in sp if math.hypot(p[0], p[1] + 0.3) < 2.55]
    inner = circle(0, -0.3, 0.6, 30)
    head = spl([(-0.5, 1.15), (-0.4, 1.5), (0.2, 1.75), (0.9, 1.8), (1.35, 1.65), (1.6, 1.4), (1.45, 1.15), (0.9, 1.0), (0.2, 0.95)])
    neck_ = hide([sp], head)
    blots = []
    for k in range(12):
        a = k * TAU / 12 + 0.3
        r = 1.15 if k % 2 else 2.0
        x, y = r * math.cos(a), -0.3 + r * math.sin(a)
        blots.append(ellipse(x, y, 0.28, 0.18, 14, rot=a + math.pi / 2))
    blots = hide(blots, head)
    mouth = [spl([(1.55, 1.3), (1.2, 1.25), (0.85, 1.3)], closed=False)]
    pits = [[(1.55, 1.45), (1.6, 1.55)]][:0]
    stripe = [spl([(-0.9, 1.75), (0.2, 1.7), (1.0, 1.55)], closed=False)][:0]
    tongue = [[(1.6, 1.35), (2.0, 1.45), (2.2, 1.6)], [(2.0, 1.45), (2.22, 1.36)]]
    hide_rock = [spl([(-3.3, -2.9), (-2.5, -2.6), (2.5, -2.6), (3.3, -2.9)], closed=False)][:0]
    return make("Ball Python Curled Up", [outer, head] + neck_ + hide([inner], head) + blots + mouth + tongue, [eye(1.0, 1.48, 0.1)])


def green_iguana(rng):
    body = spl([(3.1, 1.1), (2.85, 1.5), (2.3, 1.65), (1.7, 1.5), (0.8, 1.35), (-0.4, 1.2), (-1.2, 0.85), (-1.8, 0.6), (-2.7, 0.45),
                (-3.3, 0.2, 0), (-2.7, 0.15), (-1.8, 0.15), (-1.2, 0.2), (-0.3, 0.35), (0.9, 0.45), (1.6, 0.55), (1.85, 0.5),
                (2.4, 0.75), (2.9, 0.82)])
    dew = spl([(2.75, 0.82), (2.55, 0.25), (2.1, -0.05), (1.75, 0.2), (1.75, 0.5)], closed=False)
    dew_l = [spl([(2.5, 0.65), (2.25, 0.25)], closed=False)]
    spikes = []
    for k in range(10):
        t = k / 9
        x = 1.6 - 2.8 * t
        y = 1.48 - 0.55 * t + (0.0 if x > 0 else 0.0)
        y = 1.5 - 0.2 * t if x > 0.8 else (1.35 - 0.12 * (0.8 - x) if x > -0.4 else 1.2 - 0.45 * (-0.4 - x))
        h = 0.32 - 0.18 * t
        spikes.append(poly((x + 0.12, y - 0.02), (x - 0.02, y + h), (x - 0.12, y - 0.02), closed=False))
    shield = circle(2.3, 0.95, 0.17, 14)
    tympan = []
    legs = [spl([(1.4, 0.55), (1.6, 0.05), (1.45, -0.3), (1.9, -0.35, 0)], closed=False),
            spl([(1.05, 0.48), (1.25, 0.05), (1.05, -0.3), (1.4, -0.3)], closed=False),
            spl([(-0.6, 0.3), (-0.3, -0.05), (-0.55, -0.35), (-0.05, -0.38, 0)], closed=False),
            spl([(-1.0, 0.25), (-0.8, -0.05), (-1.0, -0.33), (-0.6, -0.33)], closed=False)]
    claws = [[(1.9, -0.35), (2.1, -0.28)], [(-0.05, -0.38), (0.15, -0.3)]]
    bands = [[(-1.7 - 0.4 * k, 0.6 - 0.06 * k), (-1.7 - 0.4 * k, 0.15 - 0.0 * k)] for k in range(3)]
    branch = [spl([(-3.4, -0.35), (-1.0, -0.3), (1.0, -0.4), (3.4, -0.55)], closed=False),
              spl([(-3.4, -0.9), (-1.0, -0.85), (1.0, -0.95), (3.4, -1.1)], closed=False),
              spl([(-1.5, -0.88), (-1.9, -1.8), (-1.7, -2.8)], closed=False)]
    leaves = [lens((-1.7, -2.8), (-1.1, -2.4), 0.35), lens((-1.85, -2.0), (-2.5, -2.3), 0.35), lens((2.6, -1.0), (3.0, -1.8), 0.35)]
    tail2 = [spl([(-2.7, 0.15), (-3.0, -0.2), (-3.1, -0.4)], closed=False)][:0]
    branch = hide(branch, *legs[:0])
    return make("Green Iguana on a Branch", [body, dew] + dew_l + spikes + [shield] + legs + claws + bands + branch + leaves,
                [eye(2.55, 1.32, 0.09)])


def tree_frog_terrarium(rng):
    glass = [rect(-2.7, -2.9, 2.7, 2.0), rect(-2.8, 2.0, 2.8, 2.55)]
    mesh = [[(x, 2.0), (x + 0.35, 2.55)] for x in [-2.7 + 0.45 * k for k in range(12)]]
    mesh = [[p for p in m_] for m_ in mesh]
    base = [[(-2.7, -2.45), (2.7, -2.45)]]
    branch = sides(spl([(-2.7, -1.55), (-1.0, -1.18), (0.6, -1.05), (2.7, -0.85)], closed=False), 0.4)
    # frog sitting on the branch, facing us
    body = spl([(0.0, 0.95), (0.6, 0.85), (1.05, 0.45), (1.15, -0.1), (0.9, -0.5), (0.0, -0.65), (-0.9, -0.5), (-1.15, -0.1),
                (-1.05, 0.45), (-0.6, 0.85)])
    eyes_o = [circle(sx * 0.62, 0.85, 0.36, 26) for sx in (1, -1)]
    body = hide([body], *eyes_o)
    smile = [spl([(-0.6, 0.2), (0.0, 0.0), (0.6, 0.2)], closed=False)]
    arms = []
    for sx in (1, -1):
        arms.append(spl([(sx * 0.75, -0.25), (sx * 0.85, -0.6), (sx * 0.6, -0.75)], closed=False))
        arms += [circle(sx * (0.45 + 0.22 * k), -0.82, 0.1, 10) for k in range(3)]
        arms.append(spl([(sx * 1.1, -0.2), (sx * 1.55, -0.35), (sx * 1.4, -0.65), (sx * 1.15, -0.62)], closed=False))
        arms += [circle(sx * (1.25 + 0.2 * k), -0.72 + 0.03 * k, 0.1, 10) for k in range(3)]
    frog = [ [(x, y + 0.0) for x, y in st] for st in body + eyes_o + smile + arms]
    frog = tf(frog, 0.4, 0.15, 1.0)
    fshape = tf([spl([(0.0, 1.25), (1.1, 1.0), (1.6, -0.3), (1.6, -0.88), (-1.6, -0.88), (-1.2, 0.8)])], 0.4, 0.15)[0]
    branch = hide(branch, *[st for st in frog if len(st) < 14])
    plant = [lens((-2.2, -2.45), (-2.5, -0.6), 0.2), lens((-1.9, -2.45), (-1.3, -0.9), 0.2), lens((-2.05, -2.45), (-1.9, -0.2), 0.18)]
    dish = [ellipse(1.6, -1.95, 0.8, 0.2, 40), spl([(0.8, -1.95), (0.9, -2.4, 0), (2.3, -2.4, 0), (2.4, -1.95)], closed=False)]
    return make("Tree Frog in a Terrarium", glass + mesh + base + branch + frog + plant + dish,
                [eye(sx * 0.62 + 0.4, 1.0, 0.15) for sx in (1, -1)])


@design("pets_tarantula", T)
def tarantula(rng):
    ceph = ellipse(0, 0.75, 0.75, 0.68, 50)
    abd = ellipse(0, -0.95, 1.0, 1.15, 60)
    fangs = [ellipse(sx * 0.22, 1.5, 0.16, 0.22, 12) for sx in (1, -1)]
    legs = []
    for sx in (1, -1):
        for P in [[(0.45, 1.1), (1.2, 2.0), (1.5, 2.7), (1.3, 3.25)], [(0.65, 0.9), (1.6, 1.5), (2.4, 1.9), (2.95, 1.65)],
                  [(0.7, 0.55), (1.7, 0.3), (2.5, -0.4), (2.8, -1.05)], [(0.6, 0.3), (1.4, -0.5), (1.9, -1.6), (1.85, -2.6)]]:
            c = spl([(sx * x, y) for x, y in P], closed=False, res=10)
            legs.append(tube(c, lambda t: 0.36 - 0.18 * t))
            for q in P[1:3]:
                legs.append([(sx * q[0] - 0.12, q[1] - 0.1), (sx * q[0] + 0.12, q[1] + 0.1)][:0] or arc(sx * q[0], q[1], 0.17, 0, TAU, 10)[:0] or
                            [(sx * q[0], q[1])][:0] or [(sx * q[0] - 0.1, q[1] + 0.12), (sx * q[0] + 0.1, q[1] - 0.12)])
    legs = hide(legs, ceph, abd)
    palps = [tube([(sx * 0.35, 1.3), (sx * 0.65, 1.9), (sx * 0.55, 2.3)], 0.2) for sx in (1, -1)]
    fuzz = [spl([(x, y), (x + 0.15, y + 0.12), (x + 0.3, y)], closed=False) for x, y in [(-0.5, -0.6), (0.15, -0.5), (-0.2, -1.2), (-0.6, -1.6), (0.25, -1.65)]]
    mark = [[(0, 0.75), (0.3 * math.cos(a), 0.75 + 0.3 * math.sin(a))] for a in (0.6, 2.54, 4.0, 5.4)]
    return make("Pet Tarantula", [ceph, abd] + fangs + legs + hide(palps, ceph) + fuzz + mark,
                [eye(-0.1, 1.05, 0.06), eye(0.1, 1.05, 0.06)])


# ------------------------------------------------------- homes and scenes

LETTERS = {
    "P": [[(0, 0), (0, 0.6), (0.3, 0.6), (0.4, 0.5), (0.4, 0.4), (0.3, 0.3), (0, 0.3)]],
    "E": [[(0.4, 0.6), (0, 0.6), (0, 0), (0.4, 0)], [(0, 0.3), (0.3, 0.3)]],
    "T": [[(0, 0.6), (0.46, 0.6)], [(0.23, 0.6), (0.23, 0)]],
    "S": [spl([(0.4, 0.52), (0.2, 0.6), (0.03, 0.47), (0.2, 0.31), (0.38, 0.15), (0.2, 0.0), (0.0, 0.08)], closed=False)],
}


def word(text, x, y, s=1.0, gap=0.65):
    out = []
    for i, ch in enumerate(text):
        out += tf(LETTERS[ch], x + i * gap * s, y, s)
    return out


@design("pets_pet_shop", T)
def pet_shop(rng):
    wall = [rect(-3.0, -2.8, 3.0, 2.0)]
    sign = [rrect(-1.6, 2.0, 1.6, 3.0, 0.15)]
    letters = word("PETS", -1.05, 2.15, 1.15)
    aw = []
    xs = [-3.2 + 0.8 * k for k in range(9)]
    scal = [(-3.2, 1.55)]
    for a, b_ in zip(xs, xs[1:]):
        scal += arc((a + b_) / 2, 1.15, 0.4, math.pi, TAU, 10)[1:]
    aw = [poly((-3.2, 1.55), (-3.0, 2.0), (3.0, 2.0), (3.2, 1.55), closed=False), scal]
    aw += [[(x, 1.15), (x + 0.03 * (x / 3), 2.0)] for x in xs[1:-1]]
    door = [rect(-0.7, -2.8, 0.7, 0.6), circle(0.0, -0.2, 0.35, 24), circle(0.45, -1.4, 0.08, 8)]
    hang = [rect(-0.45, -0.95, 0.45, -0.65), [(-0.3, -0.65), (0.0, -0.45), (0.3, -0.65)]]
    winL = [rect(-2.7, -1.4, -1.0, 0.7)]
    winR = [rect(1.0, -1.4, 2.7, 0.7)]
    tank = [rect(-2.45, -1.4, -1.25, -0.45)]
    f, fh = fish_simple(-1.85, -0.9, 0.38)
    cage = [chain([(1.25, -1.4), (1.25, -0.55)], arc(1.85, -0.55, 0.6, math.pi, 0, 20), [(2.45, -1.4)]), [(1.15, -1.4), (2.55, -1.4)]]
    bars = [[(x, -1.4), (x, -0.55 + math.sqrt(max(0, 0.36 - (x - 1.85) ** 2)))] for x in (1.55, 2.15)]
    bird = [ellipse(1.85, -0.85, 0.22, 0.17, 16), circle(2.0, -0.62, 0.11, 12), [(1.55, -1.05), (2.15, -1.05)]]
    bars = hide(bars, bird[0], bird[1])
    sill = [[(-2.85, -1.55), (-0.85, -1.55)], [(0.85, -1.55), (2.85, -1.55)]]
    step = [[(-1.0, -2.8), (-1.0, -2.6), (1.0, -2.6), (1.0, -2.8)]]
    plants = [[(-2.6, -2.8), (-2.6, -1.9), (-2.1, -1.9), (-2.1, -2.8)], lens((-2.35, -1.9), (-2.7, -1.3), 0.35), lens((-2.35, -1.9), (-2.0, -1.35), 0.35)]
    return make("Pet Shop Storefront", wall + sign + letters + aw + door + hang + winL + winR + tank + f + cage + bars + bird + sill + step + plants, fh)


@design("pets_chew_toys", T)
def chew_toys(rng):
    cx, cy, r = -1.3, 0.9, 1.35
    ball = circle(cx, cy, r, 80)
    weave = keep_in([ellipse(cx, cy, r, 0.45 * r, 60, rot=a) for a in (0.0, math.pi / 3, 2 * math.pi / 3)], ball)
    sticks = []
    for k, dx in enumerate((-0.45, -0.15, 0.15, 0.45)):
        sticks.append(rrect(1.3 + dx - 0.12, -2.8, 1.3 + dx + 0.12, -0.6 - 0.15 * (k % 2), 0.1))
    tie = [rect(0.7, -1.95, 1.9, -1.7)]
    sticks = hide(sticks, tie[0])
    knots = [circle(1.3 + dx, -1.0 - 0.1 * (k % 2), 0.05, 6) for k, dx in enumerate((-0.45, 0.15))]
    chain_ = [[(2.3, 3.0), (2.3, 2.6)]]
    toy = [rect(2.0, 2.0, 2.6, 2.6), circle(2.3, 1.65, 0.33, 22), rect(2.05, 0.75, 2.55, 1.3), circle(2.3, 0.4, 0.33, 22), rect(1.95, -0.5, 2.65, 0.05)]
    toy += [[(2.3, 2.0), (2.3, 1.98)]]
    hook = [arc(2.3, 3.15, 0.15, -math.pi / 2, math.pi, 8)]
    cube = [rect(-2.8, -2.8, -1.3, -1.4), poly((-2.8, -1.4), (-2.4, -1.0), (-0.9, -1.0), (-1.3, -1.4), closed=False), [(-0.9, -1.0), (-0.9, -2.4), (-1.3, -2.8)]]
    strands = [quad((x, -2.6), (x + 0.2, -2.1), (x + 0.05, -1.6), 6) for x in (-2.6, -2.15, -1.7)]
    floor = [[(-3.2, -2.82), (3.2, -2.82)]]
    return make("Small Pet Chew Toys", [ball] + weave + sticks + tie + knots + chain_ + toy + hook + cube + strands + floor)


@design("pets_hamster_sunflower_seed", T)
def hamster_sunflower_seed(rng):
    body = spl([(1.35, 2.35), (1.15, 2.75), (0.5, 2.95), (-0.1, 2.75), (-0.7, 2.2), (-1.15, 1.3), (-1.25, 0.5), (-1.0, 0.08),
                (-0.6, 0.0, 0), (0.55, 0.0, 0), (0.6, 0.12, 0), (0.1, 0.22), (0.75, 0.6), (1.0, 1.2), (1.05, 1.7), (1.15, 2.05),
                (1.3, 2.2)])
    ear = spl([(0.18, 2.9), (0.12, 3.28), (0.45, 3.42), (0.65, 3.1), (0.58, 2.93)], closed=False)
    ear_in = spl([(0.27, 2.95), (0.25, 3.2), (0.45, 3.28), (0.55, 3.05)], closed=False)
    sd = lens((1.1, 1.75), (1.75, 2.35), 0.28, 14)
    stripe = [[(1.2, 1.88), (1.68, 2.3)]]
    paws = [ellipse(1.2, 1.85, 0.2, 0.14, 12, rot=0.5), ellipse(1.42, 1.72, 0.2, 0.14, 12, rot=0.5)]
    belly = spl([(1.0, 1.4), (0.3, 1.25), (-0.2, 0.5), (0.1, 0.22)], closed=False)
    cheek = spl([(1.15, 2.1), (0.75, 2.0), (0.5, 2.25)], closed=False)
    thigh = spl([(-0.2, 0.22), (-0.8, 0.6), (-0.7, 1.2), (-0.2, 1.1)], closed=False)
    wh = [[(1.3, 2.35), (1.75, 2.65)], [(1.3, 2.3), (1.85, 2.5)]]
    ham = hide([body, belly, cheek] + wh, sd, *paws) + hide([sd] + stripe, *paws) + paws + [ear, ear_in, thigh]
    dx, dy, s = 0.1, -2.5, 1.3
    ham = tf(ham, dx, dy, s)
    he = tf([eye(0.82, 2.48, 0.12), eye(1.35, 2.35, 0.05)], dx, dy, s)
    # sunflower head behind on the left
    fc = (-2.1, 1.6)
    petals = [lens((fc[0] + 0.85 * math.cos(a), fc[1] + 0.85 * math.sin(a)), (fc[0] + 1.45 * math.cos(a), fc[1] + 1.45 * math.sin(a)), 0.3, 12)
              for a in [k * TAU / 14 for k in range(14)]]
    disc = circle(fc[0], fc[1], 0.85, 50)
    grid = keep_in([[(fc[0] - 1, fc[1] + d - 1), (fc[0] + 1, fc[1] + d + 1)] for d in (-0.8, -0.4, 0.0, 0.4, 0.8)] +
                   [[(fc[0] - 1, fc[1] + d + 1), (fc[0] + 1, fc[1] + d - 1)] for d in (-0.8, -0.4, 0.0, 0.4, 0.8)], disc)
    flower = hide(petals + [disc] + grid, *[poly(*st) for st in ham[:1]])
    husks = seed(-1.8, -2.35, 0.45, 0.3) + seed(-1.2, -2.4, 0.45, -0.4) + seed(2.6, -2.35, 0.45, 0.2)
    ground = [[(-3.3, -2.52), (3.3, -2.52)]]
    return make("Hamster Nibbling a Sunflower Seed", ham + flower + husks + ground, he)


@design("pets_rabbit_guinea_pig_friends", T)
def rabbit_gp_friends(rng):
    rb, rd, re_ = rabbit("up")
    dx, dy, s = -2.0, -2.3, 1.15
    rb, rd, re_ = tf([rb], dx, dy, s)[0], tf(rd, dx, dy, s), tf(re_, dx, dy, s)
    gb, gd, ge = guinea_pig()
    gx, gy, gs = 1.25, -2.3, 0.95
    gb, gd, ge = tf([gb], gx, gy, gs, flip=True)[0], tf(gd, gx, gy, gs, flip=True), tf(ge, gx, gy, gs, flip=True)
    rab = hide([rb] + rd, gb)
    hearts = [heart(0.2, 0.6, 0.35), heart(0.75, 1.2, 0.22)]
    ground = [[(-3.4, -2.32), (3.4, -2.32)]]
    flowers = []
    for x in (2.7,):
        flowers += [[(x, -2.32), (x, -1.2)], circle(x, -1.05, 0.15, 14)] + [circle(x + 0.25 * math.cos(a), -1.05 + 0.25 * math.sin(a), 0.1, 10)
                                                                         for a in [k * TAU / 6 for k in range(6)]]
    return make("Rabbit and Guinea Pig Friends", rab + [gb] + gd + hearts + ground + flowers + grass(-3.1, -2.32, 0.5), re_ + ge)


@design("pets_hamster_habitat", T)
def hamster_habitat(rng):
    tray = [rrect(-3.0, -2.9, 3.0, -2.0, 0.2)]
    top = chain([(-2.8, -2.0), (-2.8, 1.8)], arc(-2.3, 1.8, 0.5, math.pi, math.pi / 2, 8), [(2.3, 2.3)], arc(2.3, 1.8, 0.5, math.pi / 2, 0, 8),
                [(2.8, -2.0)])
    handle = [chain([(-0.5, 2.3)], arc(0, 2.3, 0.5, math.pi, 0, 14)[1:], [(0.5, 2.3)])]
    wcx, wcy, wr = -1.6, -0.75, 1.05
    wheel = [circle(wcx, wcy, wr, 60), circle(wcx, wcy, 0.85, 50), circle(wcx, wcy, 0.15, 10)]
    spokes = [[(wcx + 0.15 * math.cos(a), wcy + 0.15 * math.sin(a)), (wcx + 0.85 * math.cos(a), wcy + 0.85 * math.sin(a))] for a in [k * TAU / 5 + 0.3 for k in range(5)]]
    wleg = [[(wcx, wcy), (wcx - 0.6, -2.0)], [(wcx, wcy), (wcx + 0.6, -2.0)]]
    wleg = hide(wleg, wheel[0])
    shelf = [rect(0.4, 0.05, 2.8, 0.3)]
    ladder = [[(0.6, -2.0), (1.0, 0.05)], [(1.1, -2.0), (1.5, 0.05)]] + [[(0.6 + 0.4 * t, -2.0 + 2.05 * t), (1.1 + 0.4 * t, -2.0 + 2.05 * t)] for t in (0.2, 0.4, 0.6, 0.8)]
    house = [poly((1.75, 0.3), (1.75, 1.1), (2.2, 1.55), (2.65, 1.1), (2.65, 0.3), closed=False), [(1.65, 1.0), (2.2, 1.55), (2.75, 1.0)],
             chain([(1.95, 0.3), (1.95, 0.6)], arc(2.2, 0.6, 0.25, math.pi, 0, 8), [(2.45, 0.3)])]
    hb, hd, he = run_hamster()
    hb, hd, he = tf([hb], 1.05, 0.3, 0.42, flip=True)[0], [], tf(he, 1.05, 0.3, 0.42, flip=True)
    hd = tf(run_hamster()[1], 1.05, 0.3, 0.42, flip=True)
    hb_shape = hb
    bottle = [rrect(2.95, 0.2, 3.45, 1.9, 0.2), [(3.2, 0.2), (3.2, -0.3)], circle(3.2, -0.35, 0.06, 6), [(2.95, 1.6), (2.8, 1.6)], [(2.95, 0.5), (2.8, 0.5)],
              wave(2.95, 3.45, 1.3, 0.04, 1, 10)]
    bowl = [spl([(0.2, -1.6), (0.3, -2.0, 0), (1.3, -2.0, 0), (1.4, -1.6)], closed=False)[:0] or [(1.8, -1.6), (1.9, -2.0), (2.6, -2.0), (2.7, -1.6)],
            ellipse(2.25, -1.6, 0.45, 0.12, 24)]
    bedding_ = [bedding(-2.8, 2.8, -2.0, 10, 0.1)][:0]
    objs = [wheel[0], shelf[0], poly(*house[0]), hb_shape, poly(*bowl[0]), poly((0.6, -2.0), (1.0, 0.05), (1.5, 0.05), (1.1, -2.0))]
    bars = [[(x, -2.0), (x, 2.3 if abs(x) < 2.3 else 1.8 + math.sqrt(max(0.0, 0.25 - (abs(x) - 2.3) ** 2)))] for x in [-2.8 + 0.56 * k for k in range(1, 10)]]
    bars = hide(bars, *objs)
    ladder = hide(ladder, hb_shape)
    return make("Hamster Habitat with Wheel and Ladder", tray + [top] + handle + wheel + hide(spokes, hb_shape) + wleg + shelf + ladder + house
                + [hb] + hd + bottle + bowl + bars, he)


@design("pets_rat_rope", T)
def rat_rope(rng):
    rope_c = [(0.0, 3.2), (0.0, -3.0)]
    rope = [[(-0.22, 3.0), (-0.22, -2.6)], [(0.22, 3.0), (0.22, -2.6)]]
    twists = [[(-0.22, y), (0.22, y + 0.3)] for y in [2.8 - 0.45 * k for k in range(12)]]
    knot = [ellipse(0.0, -2.75, 0.38, 0.22, 20)]
    tassel = [[(x, -2.95), (x * 1.3, -3.4)] for x in (-0.2, 0.0, 0.2)]
    ring = [circle(0.0, 3.25, 0.25, 20)]
    body = spl([(0.05, 2.45), (0.35, 2.75, 0), (0.7, 2.5), (1.05, 2.1), (1.3, 1.3), (1.35, 0.4), (1.15, -0.4), (0.8, -0.85),
                (0.4, -0.95), (0.25, -0.5), (0.2, 0.4), (0.15, 1.4), (0.05, 2.0)])
    ear = spl([(0.85, 2.3), (1.25, 2.6), (1.45, 2.3), (1.2, 2.0)], closed=False)
    ear_in = spl([(0.95, 2.3), (1.22, 2.45), (1.3, 2.25)], closed=False)
    paw_f = [ellipse(0.15, 1.75, 0.22, 0.14, 12), ellipse(0.12, 1.3, 0.2, 0.13, 12)]
    paw_b = [ellipse(0.25, -0.75, 0.25, 0.15, 12)]
    thigh = spl([(0.4, -0.5), (0.95, -0.4), (1.1, 0.3), (0.75, 0.55)], closed=False)
    tail = sides(cubic((0.85, -0.85), (1.2, -1.6), (0.9, -2.3), (1.4, -3.1), 30), lambda t: 0.26 - 0.18 * t)
    wh = [[(0.35, 2.75), (0.0, 3.1)], [(0.38, 2.72), (0.55, 3.15)]]
    rat_shape = body
    rope_v = hide(rope + twists, rat_shape, *paw_f, *paw_b, knot[0])
    rat = hide([body], *paw_f, *paw_b) + [ear, ear_in, thigh] + hide(tail, body) + paw_f + paw_b + wh
    shelf = [rect(-3.0, 3.0, -1.2, 3.25)][:0]
    stars_ = []
    return make("Pet Rat Climbing a Rope", rope_v + knot + tassel + ring + rat, [eye(0.62, 2.3, 0.1)])


@design("pets_guinea_pig_birthday", T)
def guinea_pig_birthday(rng):
    b, d, e = guinea_pig()
    dx, dy, s = -1.3, -2.3, 1.2
    b, d, e = tf([b], dx, dy, s)[0], tf(d, dx, dy, s), tf(e, dx, dy, s)
    hat = poly(pt((0.55, 1.45), dx, dy, s), pt((0.9, 2.55), dx, dy, s), pt((1.25, 1.35), dx, dy, s))
    pom = circle(*pt((0.9, 2.62), dx, dy, s), 0.15, 12)
    hat_stripes = [[pt((0.68, 1.85), dx, dy, s), pt((1.1, 1.8), dx, dy, s)]]
    gp = hide([b] + d, hat)
    cake_x, base = 2.0, -2.3
    tiers = [rect(cake_x - 1.0, base, cake_x + 1.0, base + 0.9), rect(cake_x - 0.7, base + 0.9, cake_x + 0.7, base + 1.6)]
    slices = [circle(cake_x + x, base + 0.45, 0.2, 14) for x in (-0.6, 0.0, 0.6)]
    slices += [circle(cake_x + x, base + 0.45, 0.08, 8) for x in (-0.6, 0.0, 0.6)]
    carrot = [poly((cake_x - 0.1, base + 1.6), (cake_x, base + 2.4), (cake_x + 0.1, base + 1.6), closed=False)]
    tops = [lens((cake_x, base + 2.4), (cake_x - 0.3, base + 2.85), 0.35), lens((cake_x, base + 2.4), (cake_x + 0.3, base + 2.85), 0.35)]
    leaves = [lens((cake_x - 0.5, base + 1.6), (cake_x - 0.8, base + 2.0), 0.35), lens((cake_x + 0.5, base + 1.6), (cake_x + 0.85, base + 1.95), 0.35)]
    bunting = [spl([(-3.2, 3.0), (-1.6, 2.4), (0.0, 2.6), (1.6, 2.4), (3.2, 3.0)], closed=False)]
    flags = [poly((x, y), (x + 0.25, y - 0.55), (x + 0.5, y + 0.02), closed=False) for x, y in [(-2.7, 2.72), (-1.5, 2.4), (-0.3, 2.53), (0.9, 2.47), (2.2, 2.62)]]
    ground = [[(-3.3, -2.32), (3.3, -2.32)]]
    return make("Guinea Pig Birthday Party", gp + [hat, pom] + hat_stripes + tiers + slices + carrot + tops + leaves + bunting + flags + ground, e)


@design("pets_hamster_in_hands", T)
def hamster_in_hands(rng):
    rim = spl([(-2.3, 0.1), (-1.6, -0.85), (0.0, -1.2), (1.6, -0.85), (2.3, 0.1)], closed=False)
    palm = spl([(2.3, 0.1), (2.55, -0.9), (2.3, -2.0), (1.4, -2.75), (0.0, -2.95), (-1.4, -2.75), (-2.3, -2.0), (-2.55, -0.9),
                (-2.3, 0.1)], closed=False)
    bowl = rim + palm[1:]
    tips = []
    for sx in (1, -1):
        for k, (x, y) in enumerate([(2.55, -0.25), (2.75, -1.0), (2.65, -1.75), (2.25, -2.4)]):
            tips.append(circle(sx * x, y, 0.42 - 0.03 * k, 30))
    tip_v = []
    for i, c in enumerate(tips):
        tip_v += hide([c], poly(*bowl), *tips[i + 1:])
    bowl_v = hide([bowl], *tips)
    thumbs = [spl([(sx * 2.3, 0.1), (sx * 1.9, 0.0), (sx * 1.45, -0.55), (sx * 1.5, -0.8)], closed=False) for sx in (1, -1)]
    nails = [lens((sx * 2.0, -0.05), (sx * 1.7, -0.3), 0.4, 8) for sx in (1, -1)]
    creases = [spl([(sx * 2.0, -1.4), (sx * 1.3, -1.8), (sx * 0.6, -1.85)], closed=False) for sx in (1, -1)]
    b, d, e, m = front_hamster()
    dx, dy, s = 0.0, -1.55, 1.05
    b, d, e, m = tf(b, dx, dy, s), tf(d, dx, dy, s), tf(e, dx, dy, s), tf(m, dx, dy, s)
    ham = hide(b + d, bowl)
    seam = [[(0.0, -1.2), (0.0, -2.95)]]
    wrists = [[(-1.3, -2.8), (-1.5, -3.4)], [(1.3, -2.8), (1.5, -3.4)]]
    hearts = [heart(-2.4, 2.0, 0.35), heart(2.5, 2.3, 0.28)]
    return make("Hamster Cupped in Two Hands", ham + bowl_v + tip_v + thumbs + nails + creases + seam + wrists + hearts, e)


@design("pets_guinea_pig_scale", T)
def guinea_pig_scale(rng):
    b, d, e = guinea_pig()
    dx, dy, s = -0.15, -0.95, 1.45
    b, d, e = tf([b], dx, dy, s)[0], tf(d, dx, dy, s), tf(e, dx, dy, s)
    tray = [rrect(-2.9, -1.25, 2.9, -0.95, 0.12)]
    stem = [rect(-0.4, -1.6, 0.4, -1.25)]
    body = [poly((-2.3, -1.6), (2.3, -1.6), (2.6, -3.0), (-2.6, -3.0))]
    dial = [circle(0.0, -2.3, 0.55, 40)]
    ticks = [[(0.42 * math.cos(a), -2.3 + 0.42 * math.sin(a)), (0.52 * math.cos(a), -2.3 + 0.52 * math.sin(a))] for a in [math.radians(d_) for d_ in (30, 60, 90, 120, 150)]]
    needle = [[(0.0, -2.3), (0.3, -1.95)], circle(0.0, -2.3, 0.07, 8)]
    feet = [rrect(-2.4, -3.2, -1.8, -3.0, 0.08), rrect(1.8, -3.2, 2.4, -3.0, 0.08)]
    btn = [rrect(1.3, -2.5, 1.9, -2.2, 0.1)]
    hearts = [heart(-2.4, 2.0, 0.3), heart(2.4, 1.6, 0.25)]
    return make("Guinea Pig on a Weighing Scale", [b] + d + tray + stem + body + dial + ticks + needle + feet + btn + hearts, e)


@design("pets_lionhead_rabbit", T)
def lionhead_rabbit(rng):
    head = ellipse(0, 0.9, 1.15, 0.95, 60)
    mane = bumpy(0, 0.75, 2.05, 1.75, 13, 0.14)
    ears = [lens((sx * 0.35, 1.7), (sx * 0.75, 3.25), 0.24, 20) for sx in (1, -1)]
    ears = hide(ears, mane)
    ears_in = hide([spl([(sx * 0.48, 2.0), (sx * 0.6, 2.6), (sx * 0.72, 3.0)], closed=False) for sx in (1, -1)], mane)
    nose = [poly((-0.13, 0.75), (0.13, 0.75), (0.0, 0.6)), [(0.0, 0.6), (0.0, 0.45)],
            spl([(-0.28, 0.4), (-0.12, 0.35), (0.0, 0.45), (0.12, 0.35), (0.28, 0.4)], closed=False)]
    wh = [[(sx * 0.3, 0.6), (sx * 1.1, 0.75)] for sx in (1, -1)] + [[(sx * 0.3, 0.52), (sx * 1.1, 0.4)] for sx in (1, -1)]
    tufts = [spl([(x, y), (x + 0.2, y - 0.3), (x + 0.1, y - 0.6)], closed=False) for x, y in [(-1.6, 1.3), (1.4, 1.4), (-1.5, 0.0), (1.5, -0.1)]]
    body = hide([spl([(-1.6, -0.55), (-2.0, -1.6), (-1.7, -2.6), (0.0, -2.8), (1.7, -2.6), (2.0, -1.6), (1.6, -0.55)], closed=False)], mane)
    paws = [ellipse(sx * 0.55, -2.55, 0.42, 0.28, 20) for sx in (1, -1)]
    chest = hide([spl([(-0.7, -0.9), (0.0, -1.2), (0.7, -0.9)], closed=False)], *paws)
    ground = [[(-3.0, -2.82), (-1.75, -2.82)], [(1.75, -2.82), (3.0, -2.82)]]
    return make("Fluffy Lionhead Rabbit", [mane, head] + ears + ears_in + nose + wh + hide(tufts, head) + body + chest + paws + ground,
                [eye(sx * 0.48, 1.05, 0.13) for sx in (1, -1)])

