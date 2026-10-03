"""Wild West niche: cowboys, frontier towns, desert critters and ranch life."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "wildwest"
R = math.radians


def make(title, parts, hints=()):
    return Design(title, [p for p in parts if len(p) >= 2], list(hints), T)


# ---------------------------------------------------------------- helpers

def smooth(pts, n=8, closed=False):
    """Catmull-Rom curve through the points."""
    P = list(pts)
    if closed and P[0] == P[-1]:
        P = P[:-1]
    m = len(P)
    segs = m if closed else m - 1
    out = []
    for i in range(segs):
        p0 = P[i - 1] if (closed or i > 0) else P[0]
        p1, p2 = P[i], P[(i + 1) % m]
        p3 = P[(i + 2) % m] if (closed or i + 2 < m) else P[-1]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(P[0] if closed else P[-1])
    return out


def densify(pts, step=0.03):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        k = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k) for i in range(1, k + 1)]
    return out


def inside(p, shape):
    x, y = p
    c = False
    for (x0, y0), (x1, y1) in zip(shape, shape[1:] + shape[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            c = not c
    return c


def keep_runs(pts, keep, step=0.03):
    out, cur = [], []
    for p in densify(pts, step):
        if keep(p):
            cur.append(p)
        else:
            if len(cur) > 1:
                out.append(cur)
            cur = []
    if len(cur) > 1:
        out.append(cur)
    return out


def hide(strokes, *shapes):
    """Remove the parts of strokes lying inside any of the closed shapes."""
    if not shapes:
        return [s for s in strokes]
    boxes = [(min(p[0] for p in sh), min(p[1] for p in sh), max(p[0] for p in sh), max(p[1] for p in sh)) for sh in shapes]

    def visible(p):
        for sh, (x0, y0, x1, y1) in zip(shapes, boxes):
            if x0 <= p[0] <= x1 and y0 <= p[1] <= y1 and inside(p, sh):
                return False
        return True
    out = []
    for s in strokes:
        out += keep_runs(s, visible)
    return out


def in_shape(strokes, shape):
    out = []
    for s in strokes:
        out += keep_runs(s, lambda p: inside(p, shape))
    return out


def stack(*groups):
    """Layered drawing: groups are (strokes, occluding shapes), front first."""
    out, occ = [], []
    for strokes, shapes in groups:
        out += hide(strokes, *occ)
        occ += list(shapes)
    return out


def limb(pts, w0, w1, n=6):
    """Closed outline of a tapering limb through joint points."""
    c = smooth(pts, n)
    return tube(c, lambda t: w0 + (w1 - w0) * t)


def flipx(strokes):
    return [[(-x, y) for x, y in s] for s in strokes]


def place(strokes, dx=0.0, dy=0.0, s=1.0, rot=0.0, flip=False):
    if flip:
        strokes = flipx(strokes)
    return [transform(p, dx=dx, dy=dy, s=s, rot=rot) for p in strokes]


# ---------------------------------------------------------------- lettering

_FONT = {
    "A": [[(0, 0), (0.3, 1), (0.6, 0)], [(0.12, 0.38), (0.48, 0.38)]],
    "B": [[(0, 0), (0, 1), (0.38, 1), (0.53, 0.9), (0.53, 0.62), (0.38, 0.52), (0, 0.52)], [(0.38, 0.52), (0.58, 0.4), (0.58, 0.12), (0.42, 0), (0, 0)]],
    "C": [arc(0.33, 0.5, 0.48, R(50), R(310), 20)],
    "D": [[(0, 0), (0, 1), (0.28, 1), (0.6, 0.72), (0.6, 0.28), (0.28, 0), (0, 0)]],
    "E": [[(0.58, 1), (0, 1), (0, 0), (0.58, 0)], [(0, 0.52), (0.45, 0.52)]],
    "F": [[(0.58, 1), (0, 1), (0, 0)], [(0, 0.52), (0.45, 0.52)]],
    "G": [chain(arc(0.33, 0.5, 0.48, R(50), R(345), 20), [(0.33, 0.42)])],
    "H": [[(0, 0), (0, 1)], [(0.6, 0), (0.6, 1)], [(0, 0.52), (0.6, 0.52)]],
    "I": [[(0.3, 0), (0.3, 1)], [(0.1, 1), (0.5, 1)], [(0.1, 0), (0.5, 0)]],
    "J": [chain([(0.55, 1), (0.55, 0.3)], arc(0.3, 0.3, 0.25, 0, -math.pi, 10))],
    "K": [[(0, 0), (0, 1)], [(0.58, 1), (0, 0.38)], [(0.2, 0.58), (0.6, 0)]],
    "L": [[(0, 1), (0, 0), (0.55, 0)]],
    "M": [[(0, 0), (0, 1), (0.32, 0.4), (0.64, 1), (0.64, 0)]],
    "N": [[(0, 0), (0, 1), (0.6, 0), (0.6, 1)]],
    "O": [ellipse(0.3, 0.5, 0.32, 0.5, 30)],
    "P": [[(0, 0), (0, 1), (0.4, 1), (0.6, 0.86), (0.6, 0.64), (0.4, 0.5), (0, 0.5)]],
    "R": [[(0, 0), (0, 1), (0.4, 1), (0.6, 0.86), (0.6, 0.64), (0.4, 0.5), (0, 0.5)], [(0.3, 0.5), (0.6, 0)]],
    "S": [smooth([(0.56, 0.86), (0.3, 1.0), (0.04, 0.82), (0.12, 0.6), (0.48, 0.42), (0.58, 0.18), (0.3, 0.0), (0.02, 0.14)], 5)],
    "T": [[(0, 1), (0.6, 1)], [(0.3, 1), (0.3, 0)]],
    "U": [chain([(0, 1), (0, 0.3)], arc(0.3, 0.3, 0.3, math.pi, 2 * math.pi, 12), [(0.6, 1)])],
    "W": [[(0, 1), (0.16, 0), (0.33, 0.62), (0.5, 0), (0.66, 1)]],
    "Y": [[(0, 1), (0.3, 0.5), (0.6, 1)], [(0.3, 0.5), (0.3, 0)]],
    "$": [smooth([(0.56, 0.8), (0.3, 0.92), (0.06, 0.76), (0.14, 0.56), (0.46, 0.44), (0.56, 0.22), (0.3, 0.08), (0.04, 0.2)], 5),
          [(0.3, 1.05), (0.3, -0.05)]],
    "0": [ellipse(0.3, 0.5, 0.3, 0.5, 30)],
    "1": [[(0.1, 0.8), (0.32, 1), (0.32, 0)]],
    "5": [chain([(0.56, 1), (0.08, 1), (0.04, 0.55)], smooth([(0.04, 0.55), (0.35, 0.62), (0.58, 0.35), (0.42, 0.04), (0.04, 0.1)], 5))],
    " ": [],
}


def text(s, cx, y, h, gap=0.3):
    """Single-stroke capitals centred on cx with baseline y."""
    widths = [0.66 if ch in "MW" else 0.6 for ch in s]
    total = (sum(widths) + gap * (len(s) - 1)) * h
    x = cx - total / 2
    out = []
    for ch, w in zip(s, widths):
        out += [[(x + px * h, y + py * h) for px, py in st] for st in _FONT[ch]]
        x += (w + gap) * h
    return out


# ---------------------------------------------------------------- horse

_HEADS = {
    "up": [(1.3, 1.45), (1.85, 2.05), (2.15, 1.85), (2.75, 1.05), (2.85, 0.78), (2.55, 0.62), (2.15, 0.95), (1.75, 1.0), (1.62, 0.5)],
    "forward": [(1.4, 1.25), (2.1, 1.6), (2.45, 1.45), (3.1, 0.85), (3.15, 0.58), (2.85, 0.48), (2.4, 0.78), (1.95, 0.8), (1.7, 0.3)],
    "down": [(1.3, 1.15), (2.0, 0.95), (2.3, 0.7), (2.6, -0.05), (2.5, -0.3), (2.25, -0.25), (1.95, 0.15), (1.75, 0.3), (1.55, 0.0)],
}
_EARS = {"up": (1.85, 2.05, 0.3), "forward": (2.1, 1.6, 0.7), "down": (2.0, 0.95, 1.3)}
_EYES = {"up": (2.15, 1.55), "forward": (2.5, 1.2), "down": (2.2, 0.45)}

_LEGS = {
    # (near front, far front, near hind, far hind) joint lists, horse facing right, ground y = -2.5
    "stand": ([(1.15, -0.1), (1.2, -1.4), (1.2, -2.2), (1.27, -2.4)],
              [(0.85, -0.1), (0.85, -1.4), (0.88, -2.2), (0.95, -2.4)],
              [(-1.45, -0.1), (-1.25, -1.0), (-1.6, -1.65), (-1.5, -2.4)],
              [(-1.15, -0.1), (-0.95, -1.0), (-1.3, -1.65), (-1.2, -2.4)]),
    "walk": ([(1.15, -0.1), (1.55, -1.3), (1.7, -2.15), (1.82, -2.4)],
             [(0.85, -0.1), (0.75, -1.35), (0.5, -2.15), (0.55, -2.4)],
             [(-1.45, -0.1), (-1.5, -1.0), (-2.0, -1.6), (-2.05, -2.4)],
             [(-1.15, -0.1), (-0.85, -1.0), (-1.1, -1.65), (-0.95, -2.4)]),
    "gallop": ([(1.15, -0.1), (1.95, -0.9), (2.6, -1.35), (2.8, -1.45)],
               [(0.85, -0.1), (1.45, -0.95), (1.05, -1.55), (1.15, -1.8)],
               [(-1.45, -0.1), (-2.2, -0.95), (-2.85, -1.45), (-3.05, -1.5)],
               [(-1.15, -0.1), (-0.75, -1.0), (-1.15, -1.55), (-0.95, -1.85)]),
    "buck": ([(1.15, -0.1), (1.3, -1.3), (1.35, -2.1), (1.45, -2.3)],
             [(0.85, -0.1), (1.0, -1.3), (1.0, -2.1), (1.1, -2.3)],
             [(-1.45, -0.1), (-2.3, -0.4), (-3.0, 0.1), (-3.25, 0.2)],
             [(-1.15, -0.1), (-2.0, -0.6), (-2.75, -0.35), (-3.0, -0.3)]),
    "rear": ([(1.15, -0.1), (1.9, -0.4), (1.7, -1.1), (1.95, -1.3)],
             [(0.85, -0.1), (1.5, -0.65), (1.2, -1.3), (1.4, -1.5)],
             [(-1.45, -0.1), (-1.25, -1.0), (-1.6, -1.65), (-1.5, -2.4)],
             [(-1.15, -0.1), (-0.95, -1.0), (-1.3, -1.65), (-1.2, -2.4)]),
}


def horse_parts(legs="stand", head="up", tail="hang", mane=True):
    """Horse facing right in local coordinates (about 6 wide, ground y=-2.5).

    Returns (front_strokes, back_strokes, body_shape, hints) so riders can be layered on top."""
    body_pts = [(1.5, -0.2), (1.0, -0.68), (0.0, -0.82), (-1.1, -0.68), (-1.75, -0.35), (-1.95, 0.15), (-1.7, 0.62), (-1.1, 0.75),
                (-0.2, 0.55), (0.7, 0.8)] + _HEADS[head]
    body = smooth(body_pts, 7, closed=True)
    ex, ey, ea = _EARS[head]
    ear = [transform([(-0.15, 0), (0.0, 0.42), (0.15, 0.0)], dx=ex - 0.05, dy=ey - 0.05, rot=-ea * 0.5)]
    nf, ff, nh, fh = _LEGS[legs]

    def leg(j):
        shape = limb(j, 0.5, 0.24)
        x, y = j[-1]
        px, py = j[-2]
        a = math.atan2(y - py, x - px)
        hoof = transform(poly((-0.02, -0.16), (0.2, -0.19), (0.2, 0.19), (-0.02, 0.15)), dx=x, dy=y, rot=a)
        return shape, hoof
    near = [leg(nf), leg(nh)]
    far = [leg(ff), leg(fh)]
    near_shapes = [s for s, h in near] + [h for s, h in near]
    near_strokes = hide([s for s, h in near] + [h for s, h in near], body)
    far_strokes = hide([s for s, h in far] + [h for s, h in far], body, *near_shapes)
    extra = []
    if mane:
        hp = _HEADS[head]
        extra.append(smooth([(0.75, 0.95), ((0.7 + hp[0][0]) / 2 - 0.05, (0.8 + hp[0][1]) / 2 + 0.2), (hp[0][0] - 0.05, hp[0][1] + 0.18),
                             (hp[1][0] - 0.1, hp[1][1] + 0.12)], 6))
    if tail == "hang":
        tl = [smooth([(-1.85, 0.45), (-2.3, 0.0), (-2.4, -1.0), (-2.2, -1.6)], 6), smooth([(-1.9, 0.15), (-2.15, -0.3), (-2.05, -1.0), (-2.2, -1.6)], 6)]
    elif tail == "fly":
        tl = [smooth([(-1.85, 0.5), (-2.5, 0.75), (-3.1, 0.6), (-3.5, 0.75)], 6), smooth([(-1.9, 0.25), (-2.6, 0.35), (-3.2, 0.2), (-3.5, 0.75)], 6)]
    else:  # up (bucking)
        tl = [smooth([(-1.8, 0.55), (-2.2, 1.1), (-2.7, 1.3), (-3.1, 1.0)], 6), smooth([(-1.9, 0.3), (-2.4, 0.8), (-2.8, 0.85), (-3.1, 1.0)], 6)]
    front = [body] + hide(ear, body) + extra + near_strokes
    back = far_strokes + hide(tl, body)
    nostril = _HEADS[head][3]
    hints = [eye(*_EYES[head], 0.07)]
    return front, back, body, near_shapes, hints


def horse(legs="stand", head="up", tail="hang", dx=0.0, dy=0.0, s=1.0, rot=0.0, flip=False):
    front, back, body, near, hints = horse_parts(legs, head, tail)
    out = front + back
    return place(out, dx, dy, s, rot, flip), place(hints, dx, dy, s, rot, flip), place([body] + near, dx, dy, s, rot, flip)


# ---------------------------------------------------------------- cowboy pieces

def cowboy_hat(cx, cy, w, tilt=0.0):
    """Side/front view Stetson: curled brim and pinched crown; (cx, cy) = brim centre."""
    brim = chain(quad((-1.0, 0.18), (-0.85, -0.05), (-0.45, -0.08), 10), quad((-0.45, -0.08), (0.0, -0.12), (0.45, -0.08), 10),
                 quad((0.45, -0.08), (0.85, -0.05), (1.0, 0.18), 10), quad((1.0, 0.18), (0.8, 0.12), (0.5, 0.06), 8),
                 [(-0.5, 0.06)], quad((-0.5, 0.06), (-0.8, 0.12), (-1.0, 0.18), 8))
    crown = chain([(-0.5, 0.06)], cubic((-0.5, 0.06), (-0.55, 0.45), (-0.45, 0.72), (-0.3, 0.76), 10),
                  quad((-0.3, 0.76), (0.0, 0.62), (0.3, 0.76), 10), cubic((0.3, 0.76), (0.45, 0.72), (0.55, 0.45), (0.5, 0.06), 10))
    band = quad((-0.52, 0.2), (0.0, 0.16), (0.52, 0.2), 10)
    return [transform(p, dx=cx, dy=cy, s=w, rot=tilt) for p in (brim, crown, band)]


def rider(seat=(0.0, 0.75), lean=0.0, arm="reins", hand=None, hat=True, saddle=True):
    """Seated rider facing right.  Returns (strokes, shapes, hints, hand, back_strokes)."""
    sx, sy = seat
    hip = (sx, sy + 0.1)
    sh = (sx + 0.12 + lean, sy + 1.4)
    head_c = (sh[0] + 0.12, sh[1] + 0.55)
    torso = smooth([(hip[0] - 0.33, hip[1] - 0.05), (sh[0] - 0.36, sh[1] - 0.05), (sh[0] - 0.1, sh[1] + 0.15), (sh[0] + 0.3, sh[1] + 0.05),
                    (hip[0] + 0.38, hip[1] + 0.25), (hip[0] + 0.3, hip[1] - 0.1)], 6, closed=True)
    head = circle(head_c[0], head_c[1], 0.3, 28)
    knee = (sx + 0.6, sy - 0.5)
    ankle = (sx + 0.35, sy - 1.35)
    thigh = limb([hip, knee], 0.44, 0.36)
    shin = limb([knee, ankle], 0.36, 0.28)
    ax, ay = ankle
    boot = smooth([(ax - 0.18, ay + 0.25), (ax - 0.2, ay - 0.15), (ax - 0.12, ay - 0.27), (ax + 0.25, ay - 0.27), (ax + 0.5, ay - 0.2),
                   (ax + 0.3, ay - 0.05), (ax + 0.18, ay + 0.25)], 4, closed=True)
    if arm == "reins":
        elbow = (sh[0] + 0.12, sh[1] - 0.7)
        hnd = hand or (sh[0] + 0.75, sh[1] - 0.72)
    elif arm == "up":
        elbow = (sh[0] - 0.45, sh[1] + 0.45)
        hnd = hand or (sh[0] - 0.75, sh[1] + 1.15)
    else:  # out (lasso / waving)
        elbow = (sh[0] + 0.6, sh[1] + 0.2)
        hnd = hand or (sh[0] + 1.1, sh[1] + 0.6)
    arm_s = limb([(sh[0], sh[1] - 0.05), elbow, hnd], 0.3, 0.22)
    fist = circle(hnd[0], hnd[1], 0.15, 12)
    hat_s = cowboy_hat(head_c[0] - 0.02, head_c[1] + 0.12, 0.62) if hat else []
    kerchief = [poly((head_c[0] - 0.18, head_c[1] - 0.3), (head_c[0] + 0.25, head_c[1] - 0.28), (head_c[0] + 0.0, head_c[1] - 0.62))]
    hat_occ = [chain(hat_s[0]), chain(hat_s[1])] if hat else []
    groups = [(hat_s, hat_occ), ([fist], [fist]), ([arm_s], [arm_s]), (kerchief, kerchief), ([head], [head]),
              ([boot], [boot]), ([shin], [shin]), ([thigh], [thigh]), ([torso], [torso])]
    strokes = stack(*groups)
    shapes = [torso, head, thigh, shin, boot, arm_s, fist] + hat_occ
    back = []
    if saddle:
        back += [chain(quad((sx - 0.75, sy + 0.45), (sx - 0.55, sy - 0.05), (sx, sy - 0.05), 8), quad((sx, sy - 0.05), (sx + 0.6, sy - 0.05), (sx + 0.75, sy + 0.35), 8)),
                 [(sx + 0.75, sy + 0.35), (sx + 0.85, sy + 0.6)], ellipse(sx + 0.87, sy + 0.66, 0.16, 0.07, 12),
                 rrect(sx - 0.85, sy - 0.75, sx + 0.7, sy - 0.05, 0.15)]
        back += [[(ax - 0.05, ay + 0.3), (ax - 0.15, ay + 1.0)]]
    return strokes, shapes, [eye(head_c[0] + 0.15, head_c[1] + 0.02, 0.05)], hnd, back


def ground_line(x0=-3.4, x1=3.4, y=-2.5, bumps=3):
    return [wave(x0, x1, y, 0.04, bumps, 80)]


def cactus(x, y, h, w=0.4, arms=((0.45, 1, 0.5), (0.6, -1, 0.4))):
    """Saguaro: trunk from (x, y) of height h; arms = (height frac, side, length)."""
    trunk = chain([(x - w / 2, y), (x - w / 2, y + h - w / 2)], arc(x, y + h - w / 2, w / 2, math.pi, 0, 10), [(x + w / 2, y)])
    out = [trunk]
    shapes = [chain(trunk, [trunk[0]])]
    for f, side, L in arms:
        by = y + h * f
        aw = w * 0.8
        x0 = x + side * w / 2
        xo = x0 + side * (L + aw / 2)
        top = by + L * 1.4
        outer = chain([(x0, by - aw / 2 + 0.0)], quad((x0, by - aw / 2), (xo + side * aw / 2, by - aw / 2), (xo + side * aw / 2, by + aw / 2), 8),
                      [(xo + side * aw / 2, top)], arc(xo, top, aw / 2, 0 if side > 0 else math.pi, math.pi if side > 0 else 0, 8),
                      [(xo - side * aw / 2, by + aw)], quad((xo - side * aw / 2, by + aw), (xo - side * aw / 2, by + aw / 2), (x0, by + aw / 2), 6))
        out.append(outer)
        shapes.append(chain([(x0 - side * 0.06, by - aw / 2)], outer, [(x0 - side * 0.06, by + aw / 2)], [(x0 - side * 0.06, by - aw / 2)]))
    return hide(out[:1], *shapes[1:]) + out[1:], shapes


def mounted(legs="walk", head="up", tail="hang", seat=(-0.15, 0.62), arm="reins", lean=0.0, hand=None, reins=True, hat=True):
    """Horse with rider; returns (strokes, hints, rider_hand)."""
    front, back, body, near, hh = horse_parts(legs, head, tail)
    rs, rsh, rh, hnd, saddle = rider(seat, lean, arm, hand, hat)
    hp = _HEADS[head]
    rein = []
    if reins and arm == "reins":
        mouth = (hp[5][0] - 0.1, hp[5][1] + 0.12)
        rein = [quad(hnd, ((hnd[0] + mouth[0]) / 2, min(hnd[1], mouth[1]) - 0.25), mouth, 10)]
    out = stack((rs, rsh), (rein, []), (saddle, [rrect(seat[0] - 0.85, seat[1] - 0.75, seat[0] + 0.7, seat[1] - 0.05, 0.15)]), (front, [body] + near), (back, []))
    return out, hh + rh, hnd


def beast(body_pts, legs, w0=0.5, w1=0.26, hoof="hoof", extra_front=(), extra_back=(), n=7):
    """Generic four-legged animal: smooth body outline + four tapering legs (near, far, near, far)."""
    body = smooth(body_pts, n, closed=True)
    nf, ff, nh, fh = legs

    def leg(j):
        shape = limb(j, w0, w1)
        x, y = j[-1]
        px, py = j[-2]
        a = math.atan2(y - py, x - px)
        if hoof == "cloven":
            h = [transform(poly((-0.02, -0.16), (0.2, -0.17), (0.2, 0.17), (-0.02, 0.14)), dx=x, dy=y, rot=a),
                 transform([(0.08, 0.0), (0.2, 0.0)], dx=x, dy=y, rot=a)]
        elif hoof == "hoof":
            h = [transform(poly((-0.02, -0.16), (0.2, -0.19), (0.2, 0.19), (-0.02, 0.15)), dx=x, dy=y, rot=a)]
        else:
            h = []
        return shape, h
    near = [leg(nf), leg(nh)]
    far = [leg(ff), leg(fh)]
    near_shapes = [sh for sh, h in near] + [h[0] for sh, h in near if h]
    front = [body] + list(extra_front) + hide([sh for sh, h in near] + [x for sh, h in near for x in h], body)
    back = hide([sh for sh, h in far] + [x for sh, h in far for x in h] + list(extra_back), body, *near_shapes)
    return front + back, [body] + near_shapes


def steer_parts(horns=True, legs=None, head_down=False):
    body = [(1.55, -0.3), (1.4, -0.95), (0.0, -1.05), (-1.4, -0.9), (-1.9, -0.45), (-2.0, 0.25), (-1.85, 0.6), (-0.6, 0.55), (0.8, 0.72),
            (1.35, 0.55), (1.85, 0.55), (2.45, -0.15), (2.5, -0.45), (2.2, -0.5), (1.85, -0.25), (1.6, -0.75)]
    if head_down:
        body = [(1.55, -0.3), (1.4, -0.95), (0.0, -1.05), (-1.4, -0.9), (-1.9, -0.45), (-2.0, 0.25), (-1.85, 0.6), (-0.6, 0.6), (0.6, 0.95),
                (1.4, 0.5), (1.95, 0.0), (2.4, -0.75), (2.35, -1.0), (2.05, -1.0), (1.75, -0.65), (1.55, -0.85)]
    legs = legs or ([(1.0, -0.6), (1.05, -1.6), (1.05, -2.3)], [(0.7, -0.6), (0.72, -1.6), (0.78, -2.3)],
                    [(-1.45, -0.5), (-1.35, -1.3), (-1.55, -1.75), (-1.5, -2.3)], [(-1.15, -0.5), (-1.05, -1.3), (-1.25, -1.75), (-1.2, -2.3)])
    tail = [smooth([(-1.95, 0.4), (-2.15, -0.3), (-2.2, -1.3)], 6), lens((-2.2, -1.25), (-2.2, -1.75), 0.35)]
    strokes, shapes = beast(body, legs, 0.45, 0.28, "cloven", extra_back=tail)
    hx, hy = (1.9, 0.5) if not head_down else (2.0, -0.05)
    hints = [eye(hx + 0.12, hy - 0.3, 0.07)]
    if horns:
        hr = [tube(smooth([(hx, hy), (hx + 0.7, hy + 0.15), (hx + 1.4, hy + 0.55), (hx + 1.6, hy + 0.95)], 6), lambda t: 0.22 * (1 - t) + 0.03),
              tube(smooth([(hx - 0.1, hy + 0.05), (hx - 0.8, hy + 0.3), (hx - 1.4, hy + 0.75), (hx - 1.55, hy + 1.15)], 6), lambda t: 0.22 * (1 - t) + 0.03)]
        strokes = hide(strokes, hr[0]) + [hr[0]] + hide([hr[1]], shapes[0], hr[0])
    ear = [lens((hx - 0.05, hy - 0.15), (hx - 0.55, hy - 0.35), 0.3)]
    strokes += hide(ear, *(hr if horns else []))
    return strokes, shapes, hints


def figure_front(cx=0.0, by=-2.9, s=1.0, hands=((-1.0, 2.3), (1.0, 2.3)), hat="cowboy", skirt=False, braids=False, beard=False,
                 vest=True, holding=None):
    """Front-view standing figure (height ~5.4*s from by).  `holding` = (strokes, shapes) drawn in front of the torso."""
    def P(x, y):
        return (x, y)
    out_groups = []
    face = ellipse(0, 4.45, 0.38, 0.48, 40)
    torso = smooth([(-0.75, 3.85), (-0.25, 4.0), (0.25, 4.0), (0.75, 3.85), (0.62, 3.0), (0.5, 2.45), (0.55, 2.2), (-0.55, 2.2), (-0.5, 2.45),
                    (-0.62, 3.0)], 5, closed=True)
    arms, fists = [], []
    for sgn, hnd in zip((-1, 1), hands):
        sh = (sgn * 0.68, 3.78)
        mx, my = (sh[0] + hnd[0]) / 2, (sh[1] + hnd[1]) / 2
        dx, dy = hnd[0] - sh[0], hnd[1] - sh[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        if nx * sgn < 0:
            nx, ny = -nx, -ny
        elbow = (mx + nx * 0.25, my + ny * 0.25)
        arms.append(limb([sh, elbow, hnd], 0.32, 0.24))
        fists.append(circle(hnd[0], hnd[1], 0.16, 12))
    legs_, boots = [], []
    for sgn in (-1, 1):
        legs_.append(limb([(sgn * 0.28, 2.25), (sgn * 0.33, 1.25), (sgn * 0.37, 0.6)], 0.5, 0.4))
        x = sgn * 0.37
        boots.append(poly((x - 0.21, 0.8), (x - 0.23, 0.2), (x - 0.3 + sgn * 0.05, 0.0), (x + 0.3 + sgn * 0.05, 0.0), (x + 0.23, 0.2), (x + 0.21, 0.8)))
    belt = rect(-0.55, 2.25, 0.55, 2.45)
    buckle = rect(-0.12, 2.22, 0.12, 2.48)
    details = []
    if vest:
        details += [[(-0.25, 4.0), (-0.12, 3.3), (-0.3, 2.45)], [(0.25, 4.0), (0.12, 3.3), (0.3, 2.45)]]
    kerchief = poly((-0.32, 4.02), (0.32, 4.02), (0.0, 3.55))
    feats = [quad((-0.12, 4.18), (0.0, 4.1), (0.12, 4.18), 6), [(0.0, 4.45), (0.04, 4.3)]]
    hair_s = []
    if braids:
        for sgn in (-1, 1):
            for k in range(4):
                y0 = 4.25 - 0.32 * k
                hair_s.append(lens((sgn * (0.45 + 0.03 * k), y0), (sgn * (0.48 + 0.03 * k), y0 - 0.32), 0.45))
            hair_s.append(poly((sgn * 0.6, 2.95), (sgn * 0.42, 2.8), (sgn * 0.78, 2.8)))
    if beard:
        hair_s.append(smooth([(-0.38, 4.4), (-0.42, 4.0), (-0.2, 3.55), (0.0, 3.45), (0.2, 3.55), (0.42, 4.0), (0.38, 4.4), (0.18, 4.15),
                              (-0.18, 4.15)], 5, closed=True))
        feats = [smooth([(-0.3, 4.15), (-0.12, 4.3), (0.0, 4.25), (0.12, 4.3), (0.3, 4.15)], 4), [(0.0, 4.45), (0.04, 4.32)]]
    if hat == "cowboy":
        hat_s = cowboy_hat(0, 4.82, 1.05)
    elif hat == "floppy":
        hat_s = [smooth([(-0.95, 4.65), (-0.55, 4.88), (0.55, 4.88), (0.95, 4.65), (0.75, 4.55), (-0.75, 4.55)], 5, closed=True),
                 chain(arc(0, 4.85, 0.5, R(5), R(175), 20), [(0.5, 4.88)])]
    else:
        hat_s = []
    hat_occ = [chain(h) for h in hat_s[:2]]
    skirt_s = []
    if skirt:
        sk = chain([(-0.52, 2.3)], [(-1.05, 1.15)], wave(-1.05, 1.05, 1.15, 0.06, 4, 40), [(0.52, 2.3)], [(-0.52, 2.3)])
        skirt_s = [sk, [(-0.3, 2.2), (-0.55, 1.2)], [(0.3, 2.2), (0.55, 1.2)]]
    hold_s, hold_sh = holding if holding else ([], [])
    groups = [(fists, fists), (hold_s, hold_sh), (arms, arms), (hat_s, hat_occ), (hair_s, [h for h in hair_s if len(h) > 5])]
    groups += [(feats, []), ([face], [face]), ([kerchief], [kerchief]), (details + [belt, buckle], [belt]),
               ([torso], [torso]), (skirt_s, skirt_s[:1]), (boots, boots), (legs_, legs_)]
    strokes = stack(*groups)
    hints = [eye(-0.15, 4.55, 0.05), eye(0.15, 4.55, 0.05)]
    return place(strokes, dx=cx, dy=by, s=s), place(hints, dx=cx, dy=by, s=s)


# ================================================================ designs


@design("wildwest_cowboy_on_horseback", T)
def cowboy_rider(rng):
    out, hints, _ = mounted("walk", "up", "hang")
    mesa = [poly((-3.4, -1.2), (-3.0, -0.2), (-2.4, -0.2), (-2.1, -1.2), closed=False)]
    out += hide(mesa, chain(out[0])) if False else []
    out += ground_line(-3.4, 3.6, -2.55, 4)
    c, _ = cactus(3.4, -2.55, 2.6, 0.32, ((0.5, -1, 0.35), (0.62, 1, 0.3)))
    return make("Cowboy on Horseback", out + c, hints)


@design("wildwest_cowboy_portrait", T)
def cowboy_portrait(rng):
    face = smooth([(0, 1.2), (0.95, 1.0), (1.15, 0.0), (0.95, -1.2), (0.45, -1.8), (0, -1.9), (-0.45, -1.8), (-0.95, -1.2), (-1.15, 0.0),
                   (-0.95, 1.0)], 8, closed=True)
    hat = cowboy_hat(0, 0.9, 2.9)
    hat_occ = [chain(hat[0]), chain(hat[1])]
    ears = [chain(arc(-1.2, -0.15, 0.3, R(80), R(280), 12)), chain(arc(1.2, -0.15, 0.3, R(-100), R(100), 12))]
    brows = [quad((-0.75, 0.25), (-0.45, 0.42), (-0.15, 0.3), 6), quad((0.75, 0.25), (0.45, 0.42), (0.15, 0.3), 6)]
    nose = [chain(quad((-0.05, 0.15), (-0.1, -0.35), (-0.25, -0.55), 6), quad((-0.25, -0.55), (0.0, -0.7), (0.2, -0.58), 6))]
    stache = smooth([(-0.85, -1.05), (-0.45, -0.75), (0.0, -0.85), (0.45, -0.75), (0.85, -1.05), (0.4, -1.0), (0.0, -1.05), (-0.4, -1.0)], 5, closed=True)
    mouth = quad((-0.3, -1.25), (0.0, -1.35), (0.3, -1.25), 6)
    band = smooth([(-1.2, -1.6), (-0.6, -2.2), (0, -2.35), (0.6, -2.2), (1.2, -1.6), (1.7, -2.3), (0.6, -3.4), (0, -3.6), (-0.6, -3.4), (-1.7, -2.3)], 6, closed=True)
    knot = ellipse(0.0, -2.55, 0.28, 0.2, 16)
    dots = [circle(x, y, 0.1, 10) for x, y in [(-0.9, -2.5), (0.9, -2.5), (-0.5, -3.1), (0.5, -3.1), (0.0, -3.25)]]
    collar = [poly((-1.7, -2.3), (-2.6, -2.7), (-3.0, -3.6), closed=False), poly((1.7, -2.3), (2.6, -2.7), (3.0, -3.6), closed=False)]
    out = stack((hat, hat_occ), ([knot] + dots, [knot]), ([band], [band]), (brows + nose + [stache, mouth], [stache]), ([face] + ears, [face]))
    out += hide(collar, band)
    return make("Cowboy with Hat and Bandana", out, [eye(-0.45, 0.0, 0.1), eye(0.45, 0.0, 0.1)])


@design("wildwest_cowgirl_lasso", T)
def cowgirl(rng):
    hand_r = (1.35, 5.1)
    loop = ellipse(1.9, 5.85, 1.35, 0.42, 60, rot=0.1)
    coil = [ellipse(-1.15, 2.2, 0.32, 0.42, 24, rot=0.2), ellipse(-1.2, 2.15, 0.3, 0.4, 24, rot=0.1)]
    rope = [quad(hand_r, (1.1, 5.6), (1.0, 5.75), 6), quad(hand_r, (0.6, 3.8), (-1.0, 2.6), 12)]
    fig, hints = figure_front(0, 0, 1.0, hands=((-1.05, 2.45), hand_r), hat="cowboy", skirt=True, braids=True, vest=False,
                              holding=(coil, [chain(c) for c in coil]))
    out = fig + [loop] + hide(rope, *[circle(*hand_r, 0.16, 12)])
    out += ground_line(-2.5, 3.0, -0.02, 3)
    return make("Cowgirl Swinging a Lasso", out, hints)


def boot_shape(dx, dy, s, flip=False):
    pts = [(-0.8, 2.2), (-0.68, 1.0), (-0.65, 0.2), (-0.8, -0.35), (-0.78, -0.95), (-0.35, -0.95), (-0.33, -0.7), (0.3, -0.68),
           (1.35, -0.9), (2.0, -0.7), (1.55, -0.35), (0.7, 0.05), (0.35, 0.5), (0.42, 1.3), (0.62, 2.28), (-0.1, 2.08)]
    outline = chain(smooth(pts[:4], 6), [pts[4], pts[5], pts[6]], smooth(pts[6:], 6), [pts[0]])
    stitch = [smooth([(-0.45, 1.8), (-0.1, 1.4), (0.2, 1.75), (-0.05, 1.95)], 6), smooth([(-0.4, 1.2), (-0.05, 0.85), (0.15, 1.1)], 6)]
    toe = [smooth([(0.8, -0.1), (1.2, -0.25), (1.55, -0.6)], 5)]
    welt = [[(0.3, -0.68), (0.25, -0.55), (1.3, -0.75)][::2]]
    pull = [chain(arc(-0.45, 2.15, 0.15, R(200), R(-20), 8))]
    spur_ = [[(-0.62, 0.05), (-0.95, -0.15), (-1.35, -0.2)], star(-1.55, -0.22, 0.32, 6, 0.4), [(-0.62, 0.15), (0.05, -0.1)]]
    out = [outline] + stitch + toe + pull + spur_
    return place(out, dx, dy, s, flip=flip), place([outline], dx, dy, s, flip=flip)


@design("wildwest_boots_with_spurs", T)
def boots(rng):
    b1, sh1 = boot_shape(-0.9, 0.0, 1.15)
    b2, sh2 = boot_shape(0.9, -0.35, 1.15)
    out = stack((b2, sh2), (b1, sh1))
    out.append([(-3.2, -1.5), (3.4, -1.5)])
    return make("Cowboy Boots with Spurs", out)


@design("wildwest_spur_closeup", T)
def spur(rng):
    band = chain(arc(-0.6, 0.0, 1.9, R(55), R(305), 50))
    band_in = chain(arc(-0.6, 0.0, 1.55, R(60), R(300), 50))
    ends = [[band[0], band_in[0]], [band[-1], band_in[-1]]]
    shank = tube([(-2.45, 0.0), (-3.0, 0.15)], 0.32)
    rowel = star(-3.7, 0.25, 0.85, 10, 0.4)
    hub = circle(-3.7, 0.25, 0.18, 12)
    strap = [rrect(-0.2, 1.35, 2.9, 1.95, 0.15), rect(1.0, 1.25, 1.6, 2.05), [(1.3, 1.25), (1.3, 1.65)]]
    strap2 = [rrect(-0.2, -1.95, 2.9, -1.35, 0.15)]
    holes = [circle(x, 1.65, 0.08, 8) for x in (2.0, 2.4)]
    conchos = [circle(-0.6 + 1.9 * math.cos(a), 1.9 * math.sin(a), 0.22, 14) for a in (R(115), R(245))]
    bobs = [[(-2.45, -0.15), (-2.5, -0.6)], lens((-2.5, -0.6), (-2.5, -1.0), 0.4)]
    out = stack((conchos, conchos), (strap + holes, [strap[0]]), (strap2, strap2), ([band, band_in] + ends, []))
    return make("Spur with Star Rowel", out + [shank, hub] + hide([rowel], hub) + bobs)


@design("wildwest_cowboy_hat", T)
def hat(rng):
    brim_o = smooth([(-3.2, 0.4), (-2.6, -0.4), (-1.0, -1.15), (1.0, -1.15), (2.6, -0.4), (3.2, 0.4), (2.4, 0.1), (1.2, -0.35), (-1.2, -0.35),
                     (-2.4, 0.1)], 8, closed=True)
    crown = chain([(-1.45, -0.3)], cubic((-1.45, -0.3), (-1.6, 1.0), (-1.3, 1.9), (-0.8, 2.05), 16), quad((-0.8, 2.05), (0, 1.55), (0.8, 2.05), 12),
                  cubic((0.8, 2.05), (1.3, 1.9), (1.6, 1.0), (1.45, -0.3), 16))
    pinch = [quad((-0.55, 1.95), (-0.35, 1.2), (-0.45, 0.6), 8), quad((0.55, 1.95), (0.35, 1.2), (0.45, 0.6), 8)]
    band = [cubic((-1.5, 0.2), (-0.8, -0.05), (0.8, -0.05), (1.5, 0.2), 20), cubic((-1.46, -0.15), (-0.8, -0.4), (0.8, -0.4), (1.46, -0.15), 20)]
    conchos = [circle(x, 0.0 if abs(x) < 0.5 else 0.05, 0.13, 12) for x in (-0.9, 0.0, 0.9)]
    feather = [lens((1.15, 0.05), (2.3, 1.55), 0.18), [(1.15, 0.05), (2.15, 1.35)]]
    crown_sh = chain(crown, [crown[0]])
    out = stack((conchos, conchos), (feather, [feather[0]]), (band + pinch, []), ([crown], [crown_sh]), ([brim_o], []))
    return make("Classic Cowboy Hat", out)


@design("wildwest_sheriff_badge", T)
def badge(rng):
    pts = []
    for k in range(12):
        a = R(90) + math.pi * k / 6
        r = 2.55 if k % 2 == 0 else 1.45
        pts.append((r * math.cos(a), r * math.sin(a)))
    pts.append(pts[0])
    balls = [circle(2.75 * math.cos(R(90) + TAU * k / 6), 2.75 * math.sin(R(90) + TAU * k / 6), 0.3, 18) for k in range(6)]
    inner = circle(0, 0, 1.15, 70)
    banner = rect(-1.75, -0.32, 1.75, 0.32)
    words = text("SHERIFF", 0, -0.2, 0.4, 0.28)
    out = stack((words, []), ([banner], [banner]), ([inner], []), ([pts], [pts]), (balls, []))
    return make("Sheriff's Star Badge", out + [star(0, 0.72, 0.28, 5, 0.45), star(0, -0.75, 0.24, 5, 0.45)][0:1])


@design("wildwest_wanted_poster", T)
def wanted(rng):
    paper = poly((-2.3, -3.1), (2.1, -3.1), (2.3, -2.7), (2.3, 3.1), (-2.0, 3.1), (-2.3, 2.8))
    out = [paper, circle(0, 2.85, 0.08, 8)]
    out += text("WANTED", 0, 2.0, 0.6, 0.25)
    frame = rect(-1.3, -0.95, 1.3, 1.7)
    face = smooth([(0, 1.0), (0.55, 0.8), (0.6, 0.1), (0.3, -0.5), (0, -0.6), (-0.3, -0.5), (-0.6, 0.1), (-0.55, 0.8)], 6, closed=True)
    hat_ = cowboy_hat(0, 0.75, 0.95)
    stache = smooth([(-0.42, -0.12), (-0.15, 0.02), (0.0, -0.05), (0.15, 0.02), (0.42, -0.12), (0.0, -0.2)], 4, closed=True)
    shoulders = [smooth([(-1.25, -0.95), (-1.0, -0.65), (-0.3, -0.55)], 5), smooth([(1.25, -0.95), (1.0, -0.65), (0.3, -0.55)], 5)]
    portrait = stack((hat_, [chain(h) for h in hat_[:2]]), ([stache], [stache]), ([face], [face]), (shoulders, []))
    out += [frame] + portrait
    out += text("REWARD", 0, -1.75, 0.45, 0.25)
    out += text("$500", 0, -2.75, 0.6, 0.25)
    return make("Wanted Poster", out, [eye(-0.22, 0.3, 0.06), eye(0.22, 0.3, 0.06)])


@design("wildwest_lasso_coil", T)
def lasso(rng):
    post = [rect(-0.35, -3.2, 0.35, 3.0), chain(arc(0, 3.0, 0.35, 0, math.pi, 8))]
    nail = [circle(0, 1.6, 0.1, 8)]
    coils = [ellipse(0.05, 0.2 - 0.06 * k, 1.35 + 0.12 * k, 1.75 + 0.05 * k, 70, rot=0.08 * (k - 1)) for k in range(4)]
    loop_top = [quad((-0.25, 1.65), (0, 2.0), (0.25, 1.65), 6)]
    honda = [ellipse(1.15, -1.45, 0.2, 0.3, 14, rot=0.4)]
    tail = [smooth([(1.25, -1.6), (1.55, -2.2), (1.2, -2.6), (1.5, -3.0)], 6), smooth([(1.43, -1.55), (1.75, -2.2), (1.4, -2.6), (1.7, -3.0)], 6)]
    out = stack((honda, honda), (coils + loop_top, []), (nail, nail), (post, []))
    return make("Coiled Lasso Rope", out + tail)


def false_front(x0, x1, y0, h, top="flat"):
    """Building with a tall false front; returns outline."""
    if top == "step":
        w = x1 - x0
        return poly((x0, y0), (x0, y0 + h), (x0 + 0.2 * w, y0 + h), (x0 + 0.2 * w, y0 + h + 0.35), (x1 - 0.2 * w, y0 + h + 0.35),
                    (x1 - 0.2 * w, y0 + h), (x1, y0 + h), (x1, y0))
    if top == "peak":
        return poly((x0, y0), (x0, y0 + h), ((x0 + x1) / 2, y0 + h + 0.6), (x1, y0 + h), (x1, y0))
    return rect(x0, y0, x1, y0 + h)


def batwing(cx, y0, w, h):
    out = []
    for sgn in (-1, 1):
        x_in, x_out = cx + sgn * 0.04, cx + sgn * w
        out.append(poly((x_in, y0), (x_out, y0), (x_out, y0 + h), (cx + sgn * w * 0.5, y0 + h + 0.18), (x_in, y0 + h * 0.85)))
        out.append([(cx + sgn * w * 0.5, y0 + 0.15), (cx + sgn * w * 0.5, y0 + h * 0.7)])
    return out


@design("wildwest_saloon", T)
def saloon(rng):
    out = [false_front(-3.0, 3.0, -2.6, 4.6, "step")]
    out += [rect(-2.2, 2.25, 2.2, 3.0)] + text("SALOON", 0, 2.38, 0.48, 0.25)
    out += [[(-3.0, 0.2), (3.0, 0.2)]]
    out += [rect(-2.4, 0.75, -1.2, 1.75), rect(1.2, 0.75, 2.4, 1.75), [(-1.8, 0.75), (-1.8, 1.75)], [(1.8, 0.75), (1.8, 1.75)]]
    awning = poly((-3.3, 0.2), (3.3, 0.2), (3.0, -0.25), (-3.0, -0.25))
    posts = [rect(x - 0.1, -2.6, x + 0.1, -0.25) for x in (-2.8, 2.8)]
    door = [rect(-0.8, -2.6, 0.8, -0.55)]
    doors = batwing(0, -1.95, 0.75, 0.95)
    wins = [rect(-2.3, -1.8, -1.2, -0.75), rect(1.2, -1.8, 2.3, -0.75)]
    boardwalk = [[(-3.3, -2.6), (3.3, -2.6)], [(-3.3, -2.85), (3.3, -2.85)]]
    rail = [[(-3.4, -2.0), (-2.95, -2.0)], [(2.95, -2.0), (3.4, -2.0)]]
    out += [awning] + posts + door + doors + wins + boardwalk + rail
    return make("Saloon with Swinging Doors", out)


@design("wildwest_main_street", T)
def main_street(rng):
    out = []
    # hotel (two storeys with balcony)
    out += [false_front(-3.6, -1.0, -2.4, 4.6, "step"), rect(-3.2, 1.65, -1.4, 2.35)] + text("HOTEL", -2.3, 1.78, 0.42, 0.25)
    out += [rect(-3.3, 0.3, -2.6, 1.2), rect(-2.0, 0.3, -1.3, 1.2), [(-3.6, -0.1), (-1.0, -0.1)], [(-3.6, 0.1), (-1.0, 0.1)]]
    out += [[(x, -0.1), (x, -0.55)] for x in (-3.3, -2.9, -2.5, -2.1, -1.7, -1.3)] + [[(-3.6, -0.55), (-1.0, -0.55)]]
    out += [rect(-2.65, -2.4, -1.95, -1.0), rect(-3.4, -1.9, -2.85, -1.1), rect(-1.75, -1.9, -1.2, -1.1)]
    # barber shop
    out += [false_front(-0.8, 1.2, -2.4, 3.0, "peak"), rect(-0.6, 0.85, 1.0, 1.4)] + text("BARBER", 0.2, 0.95, 0.32, 0.22)
    out += [rect(-0.5, -2.4, 0.1, -0.9), rect(0.35, -1.8, 1.0, -0.8)]
    pole = [rrect(1.3, -2.0, 1.55, -0.5, 0.1)] + [[(1.3, y), (1.55, y + 0.25)] for y in (-1.8, -1.4, -1.0)]
    # feed store
    out += [false_front(1.8, 3.8, -2.4, 3.7, "flat"), rect(2.05, 0.6, 3.55, 1.15)] + text("FEED", 2.8, 0.7, 0.36, 0.25)
    out += [rect(2.3, -2.4, 3.3, -0.6), [(2.8, -2.4), (2.8, -0.6)], [(2.3, -0.6), (3.3, -2.4)][0:0] or [(2.3, -0.6), (2.8, -1.5), (3.3, -0.6)]]
    walk = [[(-3.8, -2.4), (4.0, -2.4)], [(-3.8, -2.65), (4.0, -2.65)]]
    rail = [[(-0.95, -1.7), (-0.95, -2.4)][0:0]]
    trough = [rect(-0.7, -3.3, 0.9, -2.85)]
    return make("Western Town Main Street", out + pole + walk + trough)


def wheel(cx, cy, r, spokes=12, hub=0.2):
    out = [circle(cx, cy, r, 70), circle(cx, cy, r - 0.15 * min(1.0, r), 64), circle(cx, cy, r * hub, 24)]
    ri = r - 0.15 * min(1.0, r)
    for k in range(spokes):
        a = TAU * k / spokes
        out.append([(cx + r * hub * math.cos(a), cy + r * hub * math.sin(a)), (cx + ri * math.cos(a), cy + ri * math.sin(a))])
    return out, circle(cx, cy, r, 70)


@design("wildwest_sheriffs_jail", T)
def jail(rng):
    out = [false_front(-3.0, 3.0, -2.5, 4.3, "flat"), rect(-1.5, 2.2, 1.5, 3.1)] + text("JAIL", 0, 2.35, 0.6, 0.3)
    out += [rect(-2.5, 1.35, 2.5, 1.9)] + text("SHERIFF", 0, 1.45, 0.35, 0.25)
    door = [rect(-0.7, -2.5, 0.7, 0.5), star(0, -0.3, 0.4, 5, 0.45), circle(0.45, -1.2, 0.07, 8)]
    win = [rect(-2.6, -1.2, -1.3, 0.4)] + [[(x, -1.2), (x, 0.4)] for x in (-2.3, -1.95, -1.6)]
    win2 = [rect(1.3, -1.2, 2.6, 0.4)] + [[(x, -1.2), (x, 0.4)] for x in (1.6, 1.95, 2.3)]
    bench = [rect(1.2, -1.9, 2.8, -1.7), [(1.4, -1.9), (1.4, -2.5)], [(2.6, -1.9), (2.6, -2.5)]]
    walk = [[(-3.3, -2.5), (3.3, -2.5)], [(-3.3, -2.75), (3.3, -2.75)]]
    hitch = [[(-3.6, -1.6), (-3.1, -1.6)][0:0]]
    lamp = [[(-1.05, 0.9), (-1.05, 0.55)], poly((-1.25, 0.55), (-0.85, 0.55), (-0.95, 0.05), (-1.15, 0.05))]
    return make("Sheriff's Office and Jail", out + door + win + win2 + bench + walk + lamp)


@design("wildwest_covered_wagon", T)
def covered_wagon(rng):
    box = rect(-2.5, -0.65, 1.8, 0.3)
    bonnet = chain([(-2.65, 0.3)], cubic((-2.65, 0.3), (-3.0, 1.2), (-2.7, 2.1), (-2.3, 2.3), 12),
                   quad((-2.3, 2.3), (-1.3, 2.05), (-0.3, 2.3), 10), quad((-0.3, 2.3), (0.7, 2.05), (1.6, 2.3), 10),
                   cubic((1.6, 2.3), (2.0, 2.1), (2.2, 1.2), (1.95, 0.3), 12))
    hoops = [quad((-1.3, 0.3), (-1.2, 1.3), (-1.3, 2.17), 8), quad((-0.3, 0.3), (-0.3, 1.3), (-0.3, 2.3), 8), quad((0.7, 0.3), (0.65, 1.3), (0.7, 2.17), 8)]
    pucker = [ellipse(1.75, 1.3, 0.22, 0.5, 20)]
    boards = [[(-2.5, -0.18), (1.8, -0.18)]]
    w1, s1 = wheel(-1.4, -1.0, 1.15, 12)
    w2, s2 = wheel(1.05, -1.2, 0.9, 10)
    tongue = [[(1.8, -0.6), (3.6, -1.1)], [(1.8, -0.45), (3.6, -0.95)]]
    barrel = [rrect(-3.25, -0.6, -2.7, 0.2, 0.12), [(-3.25, -0.2), (-2.7, -0.2)]]
    out = stack((w1, [s1]), (w2, [s2]), ([box] + boards + hoops + pucker + [bonnet], [box]), (barrel + tongue, []))
    out += ground_line(-3.6, 3.8, -2.2, 3)
    return make("Covered Wagon", out)


@design("wildwest_stagecoach", T)
def stagecoach(rng):
    body = smooth([(-2.2, -0.45), (-2.35, 0.5), (-2.15, 1.55), (0.25, 1.55), (0.45, 0.5), (0.3, -0.45)], 6, closed=True)
    win = [rrect(-1.6, 0.55, -0.4, 1.25, 0.1)]
    door = [[(-1.75, -0.35), (-1.75, 1.35)], [(-0.25, -0.35), (-0.25, 1.35)]]
    rack = [rect(-2.1, 1.55, 0.2, 1.75)] + [[(x, 1.75), (x, 2.0)] for x in (-2.0, -1.0, 0.1)] + [[(-2.05, 2.0), (0.15, 2.0)]]
    trunks = [rrect(-1.8, 1.75, -0.9, 2.3, 0.08)]
    seat = poly((0.35, 0.9), (1.25, 0.9), (1.35, 1.2), closed=False)
    foot = [[(0.45, 0.2), (1.35, 0.4)]]
    w1, s1 = wheel(-1.6, -1.4, 1.0, 12)
    w2, s2 = wheel(0.65, -1.6, 0.8, 10)
    coach = stack((w1 + w2, [s1, s2]), ([body] + win + door + rack + trunks + [seat] + foot, [body]))
    h1, hh1, sh1 = horse("gallop", "forward", "fly", dx=4.4, dy=-0.45, s=0.85)
    sh2 = []
    team = h1
    reins = [[(1.05, 1.3), (6.5, 0.0)]]
    pole = [[(0.6, -0.6), (3.2, -1.0)]]
    driver = [circle(0.95, 1.75, 0.22, 16)] + cowboy_hat(0.94, 1.85, 0.45) + [limb([(0.85, 0.95), (0.95, 1.5)], 0.42, 0.36)]
    out = stack((team, sh1 + sh2), (driver, [driver[0]]), (coach + reins + pole, []))
    out += ground_line(-3.0, 7.6, -2.45, 4)
    return make("Stagecoach on the Run", out, hh1)


@design("wildwest_gold_prospector", T)
def prospector(rng):
    pan = [ellipse(0, 2.75, 1.05, 0.32, 40), ellipse(0, 2.78, 0.7, 0.18, 30)]
    nug = [circle(x, 2.8, 0.07, 8) for x in (-0.25, 0.05, 0.3)]
    fig, hints = figure_front(0, 0, 1.0, hands=((-0.95, 2.78), (0.95, 2.78)), hat="floppy", beard=True, vest=False,
                              holding=(pan + nug, [pan[0]]))
    susp = []
    stream = [wave(-3.2, 3.2, -0.25, 0.08, 4), wave(-3.0, 3.0, -0.75, 0.08, 4), wave(-2.6, 2.6, -1.2, 0.06, 3)]
    rocks = [ellipse(-2.2, 0.15, 0.55, 0.3, 24), ellipse(2.3, 0.2, 0.45, 0.25, 20)]
    out = fig + hide(stream, *[ellipse(0, 0.0, 0.0001, 0.0001, 4)]) + rocks
    pick = [[(1.7, 0.3), (2.7, 3.2)], quad((2.1, 3.25), (2.75, 3.45), (3.2, 2.9), 8)]
    return make("Gold Prospector Panning", out + pick, hints)


@design("wildwest_mine_entrance", T)
def mine(rng):
    hill = smooth([(-3.6, -2.5), (-3.0, 0.6), (-1.5, 2.2), (0.8, 2.5), (2.6, 1.4), (3.6, -0.2), (3.8, -2.5)], 8)
    posts = [rect(-1.7, -2.5, -1.25, 0.9), rect(1.25, -2.5, 1.7, 0.9)]
    lintel = rect(-2.1, 0.9, 2.1, 1.4)
    inner = [rect(-0.95, -2.5, -0.7, 0.3), rect(0.7, -2.5, 0.95, 0.3), rect(-1.0, 0.3, 1.0, 0.55)]
    sign = [rect(-1.5, 1.65, 1.5, 2.35), [(-1.0, 1.4), (-1.0, 1.65)], [(1.0, 1.4), (1.0, 1.65)]] + text("GOLD MINE", 0, 1.8, 0.38, 0.22)
    lantern = [[(0.0, 0.3), (0.0, 0.05)], poly((-0.2, 0.05), (0.2, 0.05), (0.15, -0.5), (-0.15, -0.5)), circle(0, -0.22, 0.08, 8)]
    pick = [tube([(1.95, -2.5), (2.6, -0.4)], 0.14), chain(quad((2.0, -0.45), (2.55, -0.1), (3.2, -0.65), 8))]
    rocks = [ellipse(-2.5, -2.25, 0.45, 0.28, 20), ellipse(-2.0, -2.35, 0.3, 0.18, 16), ellipse(3.1, -2.3, 0.4, 0.22, 18)]
    out = stack((sign + [lintel] + posts + pick + rocks, [lintel] + posts + [sign[0]] + rocks[:2]), (inner + lantern, []), ([hill], []))
    out.append([(-3.6, -2.5), (3.8, -2.5)])
    return make("Gold Mine Entrance", out)


@design("wildwest_pick_and_shovel", T)
def pick_shovel(rng):
    a1 = R(45)
    handle1 = tube([(-2.4, -2.6), (2.0, 1.8)], 0.26)
    head = chain(quad((0.9, 2.55), (2.2, 2.4), (3.1, 0.8), 14), quad((3.1, 0.8), (2.4, 1.9), (2.15, 1.95), 8), [(2.2, 1.65), (1.75, 2.05)],
                 quad((1.85, 2.15), (1.4, 2.2), (0.9, 2.55), 8))
    handle2 = tube([(2.4, -1.6), (-1.6, 2.1)], 0.24)
    grip = [chain(arc(-1.95, 2.45, 0.42, R(-45), R(225), 20)), chain(arc(-1.95, 2.45, 0.22, R(-45), R(225), 16))]
    blade = smooth([(2.15, -1.3), (2.9, -1.4), (3.25, -2.2), (2.95, -3.0), (2.4, -2.8), (1.95, -2.15), (2.15, -1.3)], 5)
    nuggets = [smooth([(x - 0.3, y), (x - 0.1, y + 0.22), (x + 0.25, y + 0.15), (x + 0.3, y - 0.1), (x, y - 0.2)], 4, closed=True)
               for x, y in [(-0.6, -2.7), (0.1, -2.75), (-0.25, -2.35), (0.65, -2.6)]]
    out = stack((nuggets, nuggets), ([head], [head]), ([handle1], [handle1]), ([blade], [blade]), (grip + [handle2], []))
    return make("Crossed Pickaxe and Shovel", out)


@design("wildwest_western_saddle", T)
def saddle(rng):
    seat = chain(quad((-1.9, 1.15), (-1.4, 0.3), (-0.3, 0.35), 12), quad((-0.3, 0.35), (0.8, 0.4), (1.05, 1.1), 10))
    horn = [chain([(1.05, 1.1), (1.0, 1.45)]), ellipse(1.08, 1.55, 0.35, 0.13, 16), [(1.3, 1.0), (1.2, 1.45)]]
    cantle = chain(quad((-1.9, 1.15), (-2.1, 1.0), (-1.95, 0.55), 6))
    skirt = smooth([(-2.4, 0.55), (-0.3, 0.2), (1.6, 0.55), (1.85, -0.3), (1.4, -0.75), (-1.9, -0.75), (-2.5, -0.3)], 6, closed=True)
    fender = smooth([(-0.9, 0.3), (-1.2, -0.8), (-1.05, -1.8), (-0.3, -1.85), (0.15, -0.8), (0.0, 0.3)], 6, closed=True)
    stirrup = [poly((-1.0, -1.85), (-1.15, -2.6), (-0.15, -2.6), (-0.3, -1.85)), [(-1.15, -2.45), (-0.15, -2.45)]]
    tool = [spiral(-1.85, -0.25, 0.05, 0.3, 1.3, 30), spiral(1.25, -0.25, 0.05, 0.3, 1.3, 30), spiral(-0.6, -1.05, 0.05, 0.25, 1.3, 30)]
    cinch = [[(1.2, -0.75), (1.2, -1.6)], circle(1.2, -1.75, 0.16, 12)]
    rail = [rect(-3.4, -0.35, 3.4, 0.0), rect(-3.2, -3.0, -2.85, -0.35), rect(2.85, -3.0, 3.2, -0.35)]
    blanket = rect(-2.7, -0.95, 2.0, 0.45)
    front = [seat, cantle] + horn
    out = stack((stirrup, [stirrup[0]]), ([fender] + tool[2:], [fender]), (front, []), ([skirt] + tool[:2] + cinch, [skirt]),
                ([blanket], [blanket]), (rail, []))
    return make("Western Saddle on a Rail", out)


def skull(cx, cy, s):
    cran = smooth([(0, 0.55), (0.55, 0.45), (0.6, 0.0), (0.38, -0.6), (0.25, -1.4), (0.0, -1.6), (-0.25, -1.4), (-0.38, -0.6), (-0.6, 0.0),
                   (-0.55, 0.45)], 6, closed=True)
    eyes_ = [ellipse(-0.3, -0.05, 0.16, 0.2, 14, rot=0.4), ellipse(0.3, -0.05, 0.16, 0.2, 14, rot=-0.4)]
    nose = [lens((-0.12, -1.1), (-0.05, -1.45), 0.4), lens((0.12, -1.1), (0.05, -1.45), 0.4)]
    horns = [tube(smooth([(0.5, 0.35), (1.3, 0.35), (2.0, 0.6), (2.4, 1.1)], 6), lambda t: 0.28 * (1 - t) + 0.04)]
    horns.append(mirror_x(horns[0]))
    crack = [[(0.0, 0.5), (0.08, 0.25), (-0.05, 0.1)]]
    strokes = hide(horns, cran) + [cran] + eyes_ + nose + crack
    return place(strokes, cx, cy, s), place([cran], cx, cy, s)


@design("wildwest_skull_on_fence", T)
def skull_fence(rng):
    sk, sh = skull(0, 1.0, 1.25)
    post = [rect(-0.55, -2.8, 0.55, 0.9)]
    rails = [rect(-3.5, -0.3, -0.55, 0.05), rect(-3.5, -1.6, -0.55, -1.25), rect(0.55, -0.3, 3.5, 0.05), rect(0.55, -1.6, 3.5, -1.25)]
    posts2 = [rect(-3.3, -2.8, -2.9, 0.4), rect(2.9, -2.8, 3.3, 0.4)]
    grain = [[(-0.2, -2.5), (-0.25, -0.5)], [(0.25, -2.0), (0.2, -0.9)]]
    out = stack((sk, sh), (post + grain, post), (posts2, posts2), (rails, []))
    out += [wave(-3.6, 3.6, -2.8, 0.04, 4)]
    return make("Cattle Skull on a Fence Post", out)


@design("wildwest_longhorn_steer", T)
def longhorn(rng):
    st, sh, hints = steer_parts(True)
    patches = [smooth([(-0.9, 0.5), (-0.4, 0.1), (-0.6, -0.5), (-1.3, -0.4), (-1.5, 0.2)], 5, closed=True)]
    out = st + in_shape(patches, sh[0]) + [wave(-3.0, 3.8, -2.55, 0.04, 4)]
    grass = [[(x - 0.12, -2.55), (x, -2.2), (x + 0.12, -2.55)] for x in (-2.7, 2.6, 3.2)]
    return make("Texas Longhorn Steer", out + grass, hints)


@design("wildwest_bison", T)
def bison(rng):
    body = [(-2.0, 0.0), (-1.2, 0.5), (-0.2, 1.2), (0.7, 1.7), (1.4, 1.45), (1.75, 0.8), (2.2, 0.1), (2.45, -0.45), (2.25, -0.7),
            (2.0, -0.75), (1.95, -1.4), (1.6, -1.45), (1.3, -1.15), (0.4, -1.1), (-1.2, -0.85), (-1.9, -0.55)]
    legs = ([(1.15, -0.9), (1.2, -1.8), (1.2, -2.35)], [(0.8, -0.9), (0.85, -1.8), (0.9, -2.35)],
            [(-1.45, -0.5), (-1.35, -1.3), (-1.55, -1.8), (-1.5, -2.35)], [(-1.15, -0.5), (-1.05, -1.3), (-1.25, -1.8), (-1.2, -2.35)])
    tail = [smooth([(-1.95, -0.05), (-2.2, -0.6), (-2.15, -1.0)], 5), lens((-2.15, -0.95), (-2.15, -1.35), 0.4)]
    st, sh = beast(body, legs, 0.6, 0.32, "cloven", extra_back=tail)
    cape = [smooth([(-0.2, 1.2), (-0.35, 0.4), (-0.15, -0.3), (-0.3, -1.0)], 6)]
    face = [smooth([(1.75, 0.8), (1.5, 0.2), (1.65, -0.4), (2.0, -0.75)], 6)]
    horn = [tube(smooth([(1.7, 0.6), (1.95, 0.85), (1.9, 1.15)], 5), lambda t: 0.16 * (1 - t) + 0.03)]
    curls = [arc(0.5, 0.9, 0.15, 0, 4.5, 10), arc(1.0, 0.5, 0.15, 0, 4.5, 10), arc(0.4, 0.0, 0.15, 0, 4.5, 10), arc(1.0, -0.5, 0.15, 0, 4.5, 10)]
    out = st + cape + face + hide(horn, sh[0]) + curls + [wave(-3.0, 3.2, -2.5, 0.04, 4)]
    return make("American Bison", out, [eye(1.95, -0.05, 0.07)])


@design("wildwest_coiled_rattlesnake", T)
def rattlesnake(rng):
    groups = []
    neck = tube(smooth([(0.3, -0.6), (0.8, 0.2), (0.3, 1.0), (0.6, 1.75), (1.0, 2.0)], 8), lambda t: 0.6 - 0.2 * t)
    head = smooth([(0.75, 1.75), (1.1, 2.25), (1.8, 2.3), (2.25, 2.1), (1.85, 1.8), (1.1, 1.65)], 6, closed=True)
    tongue = [[(2.25, 2.08), (2.65, 2.05), (2.85, 2.25)], [(2.65, 2.05), (2.85, 1.85)]]
    groups.append(([head] + tongue, [head]))
    groups.append(([neck] + [poly((0.55 + 0.0, y - 0.15), (0.75, y), (0.55, y + 0.15), (0.35, y)) for y in []], [neck]))
    for k in range(3, -1, -1):
        cy = -2.2 + 0.55 * k
        rx, ry = 2.5 - 0.45 * k, 0.85 - 0.12 * k
        outer = ellipse(0, cy, rx, ry, 90)
        inner = ellipse(0, cy + 0.05, rx - 0.55, max(0.12, ry - 0.3), 80)
        diamonds = [poly((rx * 0.78 * math.cos(a) - 0.18, cy + ry * 0.78 * math.sin(a) * 0.95), (rx * 0.78 * math.cos(a), cy + ry * 0.78 * math.sin(a) + 0.13),
                         (rx * 0.78 * math.cos(a) + 0.18, cy + ry * 0.78 * math.sin(a) * 0.95), (rx * 0.78 * math.cos(a), cy + ry * 0.78 * math.sin(a) - 0.13))
                    for a in [R(250), R(290)]] if k < 2 else []
        groups.insert(len(groups), ([outer, inner] + diamonds, [outer]))
    rattle = [ellipse(-2.85, -1.55 + 0.28 * k, 0.2, 0.15, 12) for k in range(4)]
    tail = [[(-2.45, -2.0), (-2.75, -1.75)], [(-2.3, -1.75), (-2.65, -1.65)]]
    out = stack(*groups)
    out += hide(rattle + tail, ellipse(0, -2.2, 2.5, 0.85, 90))
    out += [[(-3.4, -3.05), (3.4, -3.05)]]
    return make("Coiled Rattlesnake", out, [eye(1.45, 2.05, 0.08)])


@design("wildwest_armadillo", T)
def armadillo(rng):
    shell = chain([(-1.9, -0.6)], cubic((-1.9, -0.6), (-2.0, 1.6), (1.4, 1.9), (1.7, -0.5), 30), [(-1.9, -0.6)])
    bands = in_shape([[(x, -0.6), (x + 0.05, 1.8)] for x in (-0.6, -0.3, 0.0, 0.3, 0.6)], shell)
    scutes = in_shape([[(-1.9, 0.15), (-0.6, 0.6)], [(0.6, 0.6), (1.75, 0.0)]], shell)
    head = smooth([(1.6, 0.4), (2.0, 0.3), (2.9, -0.35), (3.1, -0.55), (2.8, -0.65), (1.75, -0.6)], 6, closed=True)
    ear = [lens((1.95, 0.2), (2.1, 0.75), 0.4)]
    legs = [limb([(1.0, -0.5), (1.1, -1.25)], 0.4, 0.3), limb([(-1.2, -0.5), (-1.3, -1.25)], 0.42, 0.32)]
    claws = [[(x - 0.1, -1.3), (x - 0.2, -1.42)] for x in (1.15, -1.25)] + [[(x + 0.1, -1.3), (x + 0.15, -1.42)] for x in (1.15, -1.25)]
    tail = tube(smooth([(-1.85, -0.3), (-2.5, -0.6), (-3.1, -1.1)], 6), lambda t: 0.4 * (1 - t) + 0.03)
    rings = in_shape([[(-2.3 - 0.25 * k, 0.0), (-2.6 - 0.25 * k, -1.2)] for k in range(3)], tail)
    out = stack(([shell] + bands + scutes, [shell]), ([head] + ear, [head]), (legs + claws + [tail] + rings, []))
    out += [wave(-3.4, 3.4, -1.45, 0.03, 4)]
    return make("Armadillo", out, [eye(2.3, -0.1, 0.06)])


@design("wildwest_jackrabbit", T)
def jackrabbit(rng):
    body = smooth([(1.0, 0.6), (1.2, -0.3), (1.1, -1.4), (0.9, -2.2), (1.3, -2.45), (-0.6, -2.45), (-1.6, -2.2), (-2.0, -1.2), (-1.6, 0.0),
                   (-0.4, 0.5)], 7, closed=True)
    head = smooth([(0.5, 0.5), (0.8, 1.15), (1.5, 1.35), (2.0, 0.95), (1.95, 0.6), (1.4, 0.35)], 6, closed=True)
    ears = [smooth([(0.75, 1.15), (0.3, 2.3), (0.35, 3.1), (0.7, 2.6), (1.0, 1.3)], 6), smooth([(1.05, 1.3), (1.0, 2.4), (1.25, 3.2), (1.45, 2.4), (1.35, 1.35)], 6)]
    ear_in = [smooth([(0.75, 1.6), (0.5, 2.5), (0.65, 2.6)], 5)]
    haunch = [smooth([(-0.4, -0.6), (-1.4, -0.9), (-1.2, -2.0), (-0.2, -2.3)], 6)]
    front_leg = [[(0.75, -0.6), (0.75, -2.3)]]
    tail = [circle(-2.0, -1.6, 0.25, 16)]
    whisk = [[(2.0, 0.75), (2.6, 0.95)], [(2.0, 0.7), (2.6, 0.55)]]
    out = stack(([head] + whisk, [head]), (ears + ear_in, [chain(ears[1], [ears[1][0]])]), ([body] + haunch + front_leg, [body]), (tail, []))
    cac, _ = cactus(-2.9, -2.45, 2.3, 0.3, ((0.5, -1, 0.3), (0.65, 1, 0.25)))
    out += [[(-3.6, -2.45), (3.0, -2.45)]] + cac
    return make("Desert Jackrabbit", out, [eye(1.55, 0.95, 0.08)])


@design("wildwest_coyote_howling", T)
def coyote(rng):
    body = smooth([(1.6, 2.7), (1.15, 2.3), (0.75, 2.1), (0.35, 1.85), (0.15, 1.45), (-0.5, 0.65), (-1.1, -0.3), (-1.2, -1.0), (-0.9, -1.45),
                   (0.35, -1.5), (0.95, -1.5), (0.95, -1.35), (0.8, -0.3), (0.85, 0.45), (1.1, 1.25), (1.35, 1.8), (1.6, 2.4)], 6, closed=True)
    ear = [poly((0.35, 1.9), (0.42, 2.6), (0.7, 2.08), closed=False)]
    hind = [smooth([(-0.45, -0.4), (-0.15, -1.0), (0.2, -1.45)], 5)]
    front = [[(0.6, -0.3), (0.6, -1.45)]]
    tail = smooth([(-1.0, -1.2), (-1.7, -1.4), (-2.6, -1.35), (-2.9, -1.5), (-2.2, -1.6), (-1.0, -1.5)], 6, closed=True)
    rock = smooth([(-3.2, -2.9), (-3.0, -1.6), (-2.0, -1.5), (1.2, -1.5), (2.0, -2.0), (2.4, -2.9)], 6)
    moon = [circle(-1.9, 2.0, 1.0, 60)]
    neck_fur = [[(1.05, 1.0), (1.2, 0.85), (1.1, 0.65)]]
    out = stack(([body] + ear + hind + front + neck_fur, [body]), ([tail], [tail]), ([rock] + moon, []))
    stars_ = [star(2.6, 2.6, 0.25, 5, 0.45), star(-3.0, 0.5, 0.2, 5, 0.45), star(2.9, 0.9, 0.18, 5, 0.45)]
    cac, _ = cactus(2.9, -2.9, 2.2, 0.32, ((0.5, -1, 0.3), (0.6, 1, 0.25)))
    return make("Coyote Howling at the Moon", out + stars_ + [[(-3.6, -2.9), (3.6, -2.9)]] + cac, [eye(0.95, 2.05, 0.06)])


@design("wildwest_saguaro_sunset", T)
def saguaro_sunset(rng):
    c1, s1 = cactus(-1.2, -2.4, 5.2, 0.6, ((0.4, -1, 0.7), (0.55, 1, 0.55), (0.7, -1, 0.35)))
    c2, s2 = cactus(2.4, -2.4, 2.4, 0.35, ((0.5, 1, 0.3),))
    sun = circle(1.0, -0.2, 1.7, 90)
    stripes = in_shape([[(-1.0, y), (3.0, y)] for y in (-0.8, -1.2, -1.55)], sun)
    hills = [smooth([(-3.6, -1.0), (-2.4, -0.5), (-1.0, -1.1), (0.6, -0.6), (2.0, -1.2), (3.6, -0.7)], 6)]
    sky = hide(hills + [sun] + stripes, *(s1 + s2))
    sky = hide(sky, chain([(-3.6, -1.0)], hills[0], [(3.6, -2.4), (-3.6, -2.4)]))
    out = c1 + c2 + sky + hide(hills, *(s1 + s2)) + [[(-3.6, -2.4), (3.6, -2.4)]]
    ribs = in_shape([[(-1.2, -2.4), (-1.2, 2.6)]], s1[0])
    birds = [quad((-2.8, 2.2), (-2.55, 2.45), (-2.3, 2.2), 6) + quad((-2.3, 2.2), (-2.05, 2.45), (-1.8, 2.2), 6)[1:]]
    return make("Saguaro Cactus at Sunset", out + ribs + birds)


@design("wildwest_tumbleweed", T)
def tumbleweed(rng):
    out = []
    loops = [(0.0, 0.0, 1.7, 1.3, 0.2), (0.1, 0.1, 1.4, 0.9, 1.1), (-0.1, 0.0, 1.2, 1.5, 2.0), (0.0, -0.1, 0.8, 1.6, 0.7), (0.15, 0.05, 1.5, 0.6, 2.6)]
    for x, y, rx, ry, rot in loops:
        out.append(ellipse(x, y - 0.2, rx, ry, 70, rot=rot))
    twigs = [[(1.6 * math.cos(a), -0.2 + 1.5 * math.sin(a)), (2.0 * math.cos(a), -0.2 + 1.85 * math.sin(a))] for a in [k * TAU / 9 + 0.3 for k in range(9)]]
    motion = [[(-3.6, y), (-2.3, y)] for y in (0.3, -0.3, -0.9)]
    ground = [[(-3.6, -2.1), (3.6, -2.1)]]
    post = [rect(2.6, -2.1, 2.95, 0.9), [(2.95, 0.4), (3.6, 0.3)], [(2.95, -0.4), (3.6, -0.5)]]
    dust = [circle(-1.9, -1.95, 0.15, 10), circle(-2.4, -1.85, 0.12, 10), circle(-2.85, -1.95, 0.1, 8)]
    return make("Tumbleweed Rolling", out + twigs + motion + ground + post + dust)


@design("wildwest_monument_valley", T)
def mesas(rng):
    left = poly((-3.6, -0.6), (-3.2, -0.3), (-3.0, 1.6), (-2.85, 1.75), (-1.95, 1.75), (-1.8, 1.6), (-1.6, -0.3), (-1.2, -0.6), closed=False)
    mitten = poly((-0.9, -0.6), (-0.6, -0.2), (-0.45, 1.3), (-0.2, 1.4), (0.2, 1.35), (0.25, 0.5), (0.4, 0.5), (0.45, 1.6), (0.65, 1.65),
                  (0.75, 0.2), (1.1, -0.6), closed=False)
    right = poly((1.4, -0.6), (1.8, -0.25), (1.95, 0.8), (3.6, 0.85), closed=False)
    strata = [[(-3.05, 1.1), (-1.8, 1.1)], [(-3.2, -0.3), (-1.6, -0.3)], [(-0.55, 0.6), (0.73, 0.6)][0:0] or [(-0.55, 0.6), (0.24, 0.6)],
              [(1.85, 0.3), (3.6, 0.3)]]
    floor = [[(-3.6, -0.6), (3.6, -0.6)]]
    road = [[(-0.25, -0.6), (-1.6, -3.0)], [(0.25, -0.6), (1.6, -3.0)], [(0.0, -1.0), (0.0, -1.4)], [(0.0, -1.8), (0.0, -2.3)]]
    sun = [circle(2.3, 2.3, 0.55, 40)]
    brush = [ellipse(x, y, 0.35, 0.15, 16) for x, y in [(-2.6, -1.4), (2.4, -1.6), (-2.2, -2.5), (2.8, -2.6)]]
    return make("Monument Valley Mesas", [left, mitten, right] + strata + floor + road + sun + brush)


@design("wildwest_windmill_pump", T)
def windmill(rng):
    legs = [[(-1.2, -2.8), (-0.25, 1.4)], [(1.2, -2.8), (0.25, 1.4)]]
    braces = []
    ys = [-2.8, -1.4, -0.1, 1.0]
    def wx(y):
        return 1.2 - (y + 2.8) / 4.2 * 0.95
    for a, b in zip(ys, ys[1:]):
        braces += [[(-wx(a), a), (wx(b), b)], [(wx(a), a), (-wx(b), b)], [(-wx(b), b), (wx(b), b)]]
    platform = rect(-0.55, 1.4, 0.55, 1.6)
    hub = circle(0, 2.4, 0.22, 14)
    blades = []
    for k in range(16):
        a = TAU * k / 16
        blades.append(transform(poly((0.35, -0.08), (1.45, -0.2), (1.45, 0.2), (0.35, 0.08)), dx=0, dy=2.4, rot=a))
    rim = [circle(0, 2.4, 1.1, 70)]
    vane = [[(0.2, 2.4), (2.2, 2.6)], poly((1.7, 2.55), (2.9, 3.0), (2.9, 2.2), (1.7, 2.45))]
    pipe = [[(0, 1.4), (0, -2.8)]]
    tank = [rect(1.7, -2.8, 3.4, -1.2), ellipse(2.55, -1.2, 0.85, 0.2, 30)] + [[(1.7, y), (3.4, y)] for y in (-2.3, -1.75)]
    spout = [[(0, -1.9), (1.7, -1.6)]]
    rimshape = circle(0, 2.4, 1.1, 70)
    out = stack(([hub] + blades + rim, [rimshape]), (vane, []), ([platform], [platform]), (legs + braces + pipe + spout + tank, []))
    out += [[(-3.0, -2.8), (3.6, -2.8)]]
    return make("Windmill Water Pump", out)


@design("wildwest_ranch_gate", T)
def ranch_gate(rng):
    posts = [rect(-2.6, -2.8, -2.1, 2.2), rect(2.1, -2.8, 2.6, 2.2)]
    beam = rect(-3.2, 2.2, 3.2, 2.7)
    ends = [ellipse(-3.2, 2.45, 0.12, 0.25, 12), ellipse(3.2, 2.45, 0.12, 0.25, 12)]
    sign = [rect(-1.6, 0.6, 1.6, 1.5), [(-1.2, 1.5), (-1.2, 2.2)], [(1.2, 1.5), (1.2, 2.2)]] + text("RANCH", 0, 0.82, 0.5, 0.28)
    sk, sh = skull(0, 3.45, 0.55)
    fence = [[(-3.6, y), (-2.6, y)] for y in (-0.6, -1.6)] + [[(2.6, y), (3.6, y)] for y in (-0.6, -1.6)]
    road = [[(-1.3, -2.8), (-0.3, -0.4)], [(1.3, -2.8), (0.3, -0.4)]]
    hills = [smooth([(-2.1, -0.5), (-1.0, 0.1), (0.4, -0.3), (2.1, 0.2)], 6)]
    out = stack((sk, sh), ([beam] + ends, [beam]), (sign, [sign[0]]), (posts, posts), (fence + hide(road + hills, rect(-1.6, 0.6, 1.6, 1.5)), []))
    out += [[(-3.6, -2.8), (3.6, -2.8)]]
    return make("Ranch Gate Entrance", out)


@design("wildwest_barbed_wire_fence", T)
def barbed_wire(rng):
    posts = [(-2.6, 1.0), (0.3, 0.72), (2.3, 0.55), (3.5, 0.45)]
    out = []
    tops = []
    for x, s in posts:
        w, h = 0.4 * s, 4.2 * s
        yb = -2.8 + (1 - s) * 2.2
        out.append(poly((x - w / 2, yb), (x - w / 2, yb + h), (x, yb + h + 0.15 * s), (x + w / 2, yb + h), (x + w / 2, yb)))
        tops.append((x, yb, h, s))
    for frac in (0.85, 0.6, 0.35):
        for (x0, y0, h0, s0), (x1, y1, h1, s1) in zip(tops, tops[1:]):
            a = (x0 + 0.2 * s0, y0 + h0 * frac)
            b = (x1 - 0.2 * s1, y1 + h1 * frac)
            out.append(quad(a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 0.12), b, 16))
            for u in (0.3, 0.65):
                mx = a[0] + (b[0] - a[0]) * u
                my = a[1] + (b[1] - a[1]) * u - 0.12 * 4 * u * (1 - u)
                d = 0.13 * (s0 + s1) / 2
                out += [[(mx - d, my - d), (mx + d, my + d)], [(mx - d, my + d), (mx + d, my - d)]]
    grass = [[(x - 0.15, -2.8 + 0.0), (x, -2.4), (x + 0.15, -2.8)] for x in (-3.2, -1.7, -0.6, 1.3, 2.9)]
    out += grass + [[(-3.6, -2.8), (3.8, -2.8)]]
    hills = [smooth([(-3.6, -0.6), (-1.5, -0.3), (1.0, -0.8), (3.8, -0.4)], 6)]
    return make("Barbed Wire Fence on the Prairie", out + hide(hills, *[o for o in out[:4]]))

@design("wildwest_campfire_bean_pot", T)
def campfire(rng):
    tripod = [[(-2.2, -2.6), (0.0, 2.2)], [(2.2, -2.6), (0.0, 2.2)], [(0.5, -2.75), (0.0, 2.2)], [(-0.3, 2.5), (0.0, 2.2), (0.3, 2.5)]]
    chain_ = [[(0.0, 2.2), (0.0, 0.95)]]
    pot = chain([(-0.95, 0.6)], cubic((-0.95, 0.6), (-1.1, -0.6), (1.1, -0.6), (0.95, 0.6), 24))
    rim = ellipse(0, 0.6, 0.95, 0.18, 30)
    bail = [quad((-0.95, 0.6), (0.0, 1.5), (0.95, 0.6), 12)]
    lid_knob = [ellipse(0, 0.8, 0.2, 0.08, 10)]
    steam = [smooth([(-0.3, 0.9), (-0.5, 1.3), (-0.25, 1.6)], 5), smooth([(0.35, 0.9), (0.55, 1.3), (0.3, 1.65)], 5)]
    flames = [lens((0.0, -1.9), (0.0, -0.55), 0.3), lens((-0.4, -1.9), (-0.85, -0.85), 0.3), lens((0.4, -1.9), (0.85, -0.85), 0.3)]
    logs = [tube([(-1.6, -2.4), (1.4, -1.8)], 0.32), tube([(1.6, -2.4), (-1.4, -1.8)], 0.32)]
    stones = [ellipse(x, -2.55, 0.32, 0.2, 16) for x in (-2.1, -1.4, -0.7, 0.0, 0.7, 1.4, 2.1)]
    potshape = chain(pot, [pot[0]])
    out = stack(([rim] + lid_knob + bail, [chain(rim)]), ([pot], [potshape]), (flames, [f for f in flames]),
                (logs, logs), (stones, stones), (tripod + chain_, []))
    plate = [ellipse(2.6, -2.55, 0.6, 0.15, 24), ellipse(2.6, -2.55, 0.35, 0.08, 16), [(3.0, -2.45), (3.5, -2.0)]]
    return make("Campfire with Bean Pot", out + plate)


@design("wildwest_chuck_wagon", T)
def chuck_wagon(rng):
    bonnet = chain([(-2.3, 0.6)], cubic((-2.3, 0.6), (-2.4, 3.1), (2.4, 3.1), (2.3, 0.6), 30))
    hoop = [chain(cubic((-1.8, 0.6), (-1.85, 2.5), (1.85, 2.5), (1.8, 0.6), 30))]
    box = rect(-1.6, -1.0, 1.6, 0.6)
    shelves = [[(-1.6, -0.2), (1.6, -0.2)], [(0.0, -1.0), (0.0, 0.6)], [(-0.8, -0.2), (-0.8, 0.6)], [(0.8, -0.2), (0.8, 0.6)]]
    drawers = [rect(-1.4, -0.85, -0.2, -0.35), rect(0.2, -0.85, 1.4, -0.35), circle(-0.8, -0.6, 0.06, 8), circle(0.8, -0.6, 0.06, 8)]
    cans = [rrect(-1.45, -0.15, -1.0, 0.4, 0.06), rrect(-0.65, -0.15, -0.2, 0.3, 0.06), ellipse(0.4, 0.05, 0.2, 0.2, 12), rrect(1.0, -0.15, 1.45, 0.45, 0.06)]
    table = poly((-1.6, -1.0), (-1.6, -1.25), (1.6, -1.25), (1.6, -1.0))
    leg_ = [[(0.0, -1.25), (0.0, -2.6)]]
    bed = rect(-2.3, -1.6, 2.3, 0.6)
    wheels = [ellipse(-2.55, -1.6, 0.3, 1.2, 40), ellipse(-2.55, -1.6, 0.15, 0.95, 30), ellipse(2.55, -1.6, 0.3, 1.2, 40), ellipse(2.55, -1.6, 0.15, 0.95, 30)]
    oven = [chain(arc(-3.0, -2.5, 0.0001, 0, 0, 1))[0:0]]
    pot = [rrect(1.9, -2.85, 2.9, -2.25, 0.2), ellipse(2.4, -2.25, 0.5, 0.1, 16), ellipse(2.4, -2.1, 0.12, 0.05, 8)]
    bucket = [poly((-3.2, -2.25), (-2.5, -2.25), (-2.6, -2.85), (-3.1, -2.85)), quad((-3.2, -2.25), (-2.85, -1.8), (-2.5, -2.25), 8)]
    out = stack((pot + bucket, [pot[0], bucket[0]]), (drawers + cans + shelves + [box, table] + leg_, [box, table]), (hoop + [bonnet], []),
                ([bed], [bed]), (wheels, []))
    out += [[(-3.6, -2.85), (3.6, -2.85)]]
    return make("Chuck Wagon Kitchen", out)


def bull(rot=-0.2):
    legs = ([(1.0, -0.6), (1.35, -1.5), (1.4, -2.3)], [(0.7, -0.6), (0.9, -1.5), (0.85, -2.3)],
            [(-1.45, -0.4), (-2.3, -0.4), (-2.9, 0.15), (-3.15, 0.3)], [(-1.15, -0.4), (-2.0, -0.7), (-2.7, -0.4), (-2.95, -0.3)])
    body = [(1.55, -0.3), (1.4, -0.95), (0.0, -1.05), (-1.4, -0.9), (-1.9, -0.45), (-2.0, 0.25), (-1.85, 0.6), (-0.6, 0.7), (0.4, 1.25),
            (1.2, 0.9), (1.85, 0.35), (2.35, -0.5), (2.35, -0.8), (2.05, -0.85), (1.75, -0.55), (1.6, -0.75)]
    tail = [smooth([(-1.9, 0.45), (-2.4, 1.0), (-2.9, 1.3), (-3.2, 1.1)], 6), lens((-3.15, 1.1), (-3.45, 0.85), 0.4)]
    st, sh = beast(body, legs, 0.5, 0.3, "cloven", extra_back=tail)
    horns = [tube(smooth([(1.95, 0.25), (2.35, 0.45), (2.55, 0.85)], 5), lambda t: 0.2 * (1 - t) + 0.03)]
    hump = [smooth([(0.0, 1.0), (0.4, 0.75), (0.9, 0.85)], 5)]
    st = hide(st, horns[0]) + horns + hump
    return st, sh, [eye(2.05, -0.1, 0.07)]


@design("wildwest_rodeo_bull_rider", T)
def bull_rider(rng):
    bs, bsh, bh = bull()
    rs, rsh, rh, hnd, _ = rider((-0.45, 0.7), lean=-0.25, arm="up", hat=True, saddle=False)
    rope = [[(-0.1, 0.3), (0.5, 0.95)], [(0.4, 0.95), (0.4, -0.95)]]
    out = stack((rs, rsh), (rope, []), (bs, bsh))
    out = place(out, rot=-0.15)
    fence = [[(-3.8, -1.6), (3.6, -1.6)][0:0]]
    dirt = [wave(-3.6, 3.6, -2.75, 0.05, 4)] + [circle(x, y, 0.1, 8) for x, y in [(-2.9, -2.3), (-2.6, -2.5), (-3.2, -2.55)]]
    return make("Rodeo Bull Rider", out + dirt, place(bh + rh, rot=-0.15))


@design("wildwest_bucking_bronco", T)
def bronco(rng):
    out, hints, hnd = mounted("buck", "down", "up", seat=(-0.3, 0.62), arm="up", lean=-0.25, reins=False)
    out = place(out, rot=-0.18)
    hints = place(hints, rot=-0.18)
    dust = [circle(x, y, r, 10) for x, y, r in [(-2.8, -2.0, 0.15), (-3.2, -2.3, 0.12), (-2.4, -2.4, 0.1)]]
    fence = [[(-3.8, -0.9), (3.8, -0.9)], [(-3.8, -1.5), (3.8, -1.5)]] + [[(x, -0.7), (x, -2.4)] for x in (-3.6, 3.6)]
    fence = hide(fence, *[chain(s) for s in place([horse_parts("buck", "down", "up")[2]], rot=-0.18)])
    return make("Bucking Bronco", out + dust + [[(-3.8, -2.65), (3.8, -2.65)]], hints)


@design("wildwest_barrel_racer", T)
def barrel_racer(rng):
    out, hints, _ = mounted("gallop", "forward", "fly", seat=(-0.1, 0.62), lean=0.35)
    out = place(out, dx=0.4, rot=0.06)
    hints = place(hints, dx=0.4, rot=0.06)
    def barrel(x, y, s):
        return [chain([(x - 0.5 * s, y)], [(x - 0.55 * s, y + 0.6 * s), (x - 0.5 * s, y + 1.2 * s)], [(x + 0.5 * s, y + 1.2 * s)], [(x + 0.55 * s, y + 0.6 * s), (x + 0.5 * s, y)]),
                ellipse(x, y + 1.2 * s, 0.5 * s, 0.12 * s, 20), quad((x - 0.5 * s, y), (x, y - 0.12 * s), (x + 0.5 * s, y), 8),
                quad((x - 0.54 * s, y + 0.4 * s), (x, y + 0.3 * s), (x + 0.54 * s, y + 0.4 * s), 8), quad((x - 0.54 * s, y + 0.8 * s), (x, y + 0.7 * s), (x + 0.54 * s, y + 0.8 * s), 8)]
    b1 = barrel(-3.3, -2.3, 1.1)
    b2 = barrel(3.6, -1.0, 0.7)
    out = out + hide(b1, *[]) + b2
    dust = [circle(x, -2.4, r, 10) for x, r in [(-1.0, 0.18), (-1.5, 0.14), (-2.0, 0.1)]]
    fence = [[(-3.8, -0.4), (-2.9, -0.4)], [(2.9, 0.5), (3.8, 0.5)]]
    return make("Barrel Racing Cowgirl", out + dust + [[(-3.8, -2.6), (3.9, -2.6)]], hints)


@design("wildwest_cattle_drive", T)
def cattle_drive(rng):
    groups = []
    for dx, dy, s in [(-1.4, -1.3, 0.62), (1.4, -0.9, 0.52), (-0.3, 0.2, 0.42), (-2.6, 0.5, 0.36)]:
        st, sh, h = steer_parts(True)
        groups.append((place(st, dx, dy, s), place(sh, dx, dy, s)))
    rider_, rh, _ = mounted("walk", "up", "hang")
    groups.insert(1, (place(rider_, 2.9, 1.4, 0.38, flip=False), []))
    out = stack(*groups)
    hills = [smooth([(-3.8, 1.3), (-2.0, 1.9), (0.0, 1.5), (2.0, 2.3), (4.0, 1.8)], 6)]
    out += hide(hills, *[chain(s) for g in groups for s in g[1]])
    dust = [smooth([(3.0, -2.4), (3.4, -2.1), (3.7, -2.4)], 4), smooth([(-3.6, -2.5), (-3.3, -2.2), (-3.0, -2.5)], 4)]
    return make("Cattle Drive on the Trail", out + dust + [[(-3.8, -2.85), (3.9, -2.85)]])


@design("wildwest_branding_irons", T)
def branding_irons(rng):
    out = []
    irons = [((-2.8, 2.7), (-1.5, -0.6), "circle"), ((0.0, 3.0), (0.0, -0.75), "R"), ((2.8, 2.7), (1.5, -0.6), "star")]
    heads = []
    for (x0, y0), (x1, y1), kind in irons:
        L = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        cx, cy = x1 + ux * 0.75, y1 + uy * 0.75
        if kind == "circle":
            brand = [circle(cx, cy, 0.7, 44), circle(cx, cy, 0.48, 36)]
            shape = brand[0]
        elif kind == "R":
            brand = text("R", cx - 0.0, cy - 0.65, 1.3)
            brand = [tube(p, 0.18) for p in brand]
            shape = rect(cx - 0.55, cy - 0.75, cx + 0.55, cy + 0.75)
            shape = None
        else:
            brand = [star(cx, cy, 0.8, 5, 0.45), star(cx, cy, 0.45, 5, 0.45)]
            shape = brand[0]
        rod = tube([(x0, y0), (x1, y1)], 0.15)
        handle = circle(x0 - ux * 0.3, y0 - uy * 0.3, 0.3, 18)
        heads.append((brand, [shape] if shape else []))
        out.append(([rod, handle], [rod]))
    coals = smooth([(-3.4, -2.6), (-2.6, -2.0), (-1.6, -2.2), (-0.6, -1.85), (0.6, -2.15), (1.6, -1.85), (2.6, -2.1), (3.4, -2.6)], 6)
    flames = [lens((x, -2.15), (x + 0.1, -1.3 + 0.2 * (k % 2)), 0.3) for k, x in enumerate((-2.4, -0.85, 0.85, 2.4))]
    bricks = [rect(-3.6, -3.0, 3.6, -2.6)] + [[(x, -3.0), (x, -2.6)] for x in (-2.0, -0.6, 0.8, 2.2)]
    res = stack(*heads, (flames, flames), *out, ([coals] + bricks, []))
    return make("Branding Irons in the Fire", res)


@design("wildwest_wagon_wheel_fence", T)
def wagon_wheel(rng):
    w, s = wheel(-0.3, 0.0, 2.5, 14, 0.2)
    hubring = [circle(-0.3, 0.0, 0.25, 16)]
    fence = [rect(-3.8, 0.9, 3.8, 1.3), rect(-3.8, -0.9, 3.8, -0.5), rect(2.6, -2.6, 3.0, 2.0), rect(-3.4, -2.6, -3.0, 2.0)]
    grass = [[(x - 0.15, -2.6), (x, -2.1), (x + 0.15, -2.6)] for x in (-2.6, -1.6, 0.9, 1.9, 3.4)]
    out = stack((w + hubring, [s]), (grass, []), (fence, fence))
    return make("Wagon Wheel Against the Fence", out + [[(-3.9, -2.6), (3.9, -2.6)]])


@design("wildwest_trading_post", T)
def trading_post(rng):
    walls = rect(-3.0, -2.4, 3.0, 1.0)
    logs = [[(-3.0, y), (3.0, y)] for y in (-1.95, -1.5, -1.05, -0.6, -0.15, 0.3, 0.7)]
    ends = [circle(-3.15, y, 0.18, 12) for y in (-2.15, -1.25, -0.4, 0.5)] + [circle(3.15, y, 0.18, 12) for y in (-2.15, -1.25, -0.4, 0.5)]
    roof = poly((-3.5, 1.0), (0.0, 2.6), (3.5, 1.0), closed=True)
    sign = [rect(-2.2, 1.15, 2.2, 1.85)] + text("TRADING POST", 0, 1.33, 0.34, 0.18)
    door = [rect(-0.6, -2.4, 0.6, -0.3)]
    win = [rect(-2.4, -1.6, -1.3, -0.6), rect(1.3, -1.6, 2.4, -0.6), [(-1.85, -1.6), (-1.85, -0.6)], [(1.85, -1.6), (1.85, -0.6)]]
    barrels = [rrect(-3.7, -2.6, -3.0, -1.6, 0.15), [(-3.7, -2.1), (-3.0, -2.1)]]
    crate = [rect(2.6, -2.6, 3.6, -1.7), [(2.6, -2.6), (3.6, -1.7)]]
    hide_ = [smooth([(1.2, 0.2), (1.0, -0.1), (1.15, -0.3), (1.4, -0.15), (1.6, -0.3), (1.75, -0.1), (1.6, 0.2)], 4, closed=True)][0:0]
    front = [door[0]] + win + sign
    out = stack((barrels + crate, [barrels[0], crate[0]]), (front, [sign[0]] + door + win[:2]), ([walls] + logs + ends, [walls]), ([roof], []))
    out += [[(-3.9, -2.6), (3.9, -2.6)]]
    return make("Frontier Trading Post", out)


@design("wildwest_general_store", T)
def general_store(rng):
    out = [false_front(-3.0, 3.0, -2.4, 4.6, "peak")]
    out += [rect(-2.4, 1.0, 2.4, 2.1)] + text("GENERAL", 0, 1.6, 0.36, 0.22) + text("STORE", 0, 1.12, 0.36, 0.25)
    awning = [poly((-3.2, 0.5), (3.2, 0.5), (3.4, -0.15), (-3.4, -0.15))] + [[(-3.2 + 0.8 * k, 0.5), (-3.4 + 0.85 * k, -0.15)] for k in range(1, 8)]
    door = [rect(-0.5, -2.4, 0.5, -0.4), rect(-0.35, -1.2, 0.35, -0.55)]
    win1 = [rect(-2.7, -1.7, -0.9, -0.5)] + [rrect(-2.5, -1.7, -2.1, -1.0, 0.08), ellipse(-1.75, -1.35, 0.25, 0.32, 14), rrect(-1.35, -1.7, -1.05, -0.8, 0.08)]
    win2 = [rect(0.9, -1.7, 2.7, -0.5)] + [rect(1.1, -1.7, 1.6, -1.2), rect(1.2, -1.2, 1.5, -0.95), ellipse(2.2, -1.4, 0.3, 0.25, 14)]
    barrel = [rrect(-3.3, -2.6, -2.6, -1.85, 0.15), [(-3.3, -2.22), (-2.6, -2.22)]]
    sack = [smooth([(2.6, -2.6), (2.5, -2.1), (2.75, -1.85), (2.65, -1.7), (3.05, -1.7), (2.95, -1.85), (3.2, -2.1), (3.1, -2.6)], 5, closed=True)]
    broom = [[(1.0, -2.6), (0.85, -0.7)], poly((0.9, -2.0), (0.7, -2.6), (1.3, -2.6), (1.1, -2.0))]
    out += stack((barrel + sack + broom, [barrel[0], sack[0], broom[1]]), (awning + door + win1 + win2, []))
    out += [[(-3.6, -2.4), (3.6, -2.4)], [(-3.6, -2.6), (3.6, -2.6)]]
    return make("Frontier General Store", out)


@design("wildwest_gold_pouch", T)
def gold_pouch(rng):
    bag = smooth([(-0.6, 1.2), (-1.5, 0.3), (-1.9, -1.0), (-1.4, -2.2), (0.3, -2.5), (1.6, -2.0), (1.8, -0.7), (1.1, 0.5), (0.4, 1.2)], 8)
    neck = [smooth([(-0.6, 1.2), (-0.3, 1.0), (0.1, 1.05), (0.4, 1.2)], 5)]
    ruffle = [smooth([(-0.6, 1.2), (-0.9, 1.9), (-0.4, 1.65), (-0.1, 2.05), (0.2, 1.65), (0.6, 1.95), (0.4, 1.2)], 5)]
    string = [smooth([(-0.5, 1.05), (0.2, 0.95), (0.7, 0.6), (0.9, 0.0)], 5), circle(0.95, -0.15, 0.13, 10)]
    nug = []
    for x, y, s in [(2.0, -2.6, 0.35), (2.7, -2.4, 0.28), (1.0, -2.75, 0.25), (2.4, -1.9, 0.25), (-2.4, -2.6, 0.3)]:
        nug.append(smooth([(x - s, y), (x - 0.6 * s, y + 0.7 * s), (x + 0.3 * s, y + 0.8 * s), (x + s, y + 0.1 * s), (x + 0.5 * s, y - 0.5 * s),
                           (x - 0.5 * s, y - 0.5 * s)], 4, closed=True))
    patch = [poly((-0.7, -0.4), (0.7, -0.4), (0.6, -1.4), (-0.6, -1.4))]
    scale = [[(2.9, -2.8), (2.9, 2.0)], [(1.6, 1.8), (4.2, 1.8)], ellipse(2.9, 2.0, 0.12, 0.12, 10),
             quad((1.1, 0.6), (1.6, 0.4), (2.1, 0.6), 8), [(1.1, 0.6), (1.6, 1.8), (2.1, 0.6)],
             quad((3.7, 0.6), (4.2, 0.4), (4.7, 0.6), 8), [(3.7, 0.6), (4.2, 1.8), (4.7, 0.6)], rect(2.5, -2.95, 3.3, -2.8)]
    bagshape = chain(bag, [bag[0]])
    out = stack((nug, nug), (neck + ruffle + string + patch + [bag], [bagshape]), (scale, []))
    return make("Gold Rush Pouch and Scale", out + [[(-3.0, -2.95), (4.8, -2.95)]])


@design("wildwest_telegraph_poles", T)
def telegraph(rng):
    out = []
    pts = []
    for x, s in [(-2.8, 1.0), (-0.3, 0.7), (1.5, 0.5), (2.8, 0.36), (3.7, 0.26)]:
        base = -2.7 + (1 - s) * 2.8
        top = base + 5.2 * s
        w = 0.14 * s
        out.append(rect(x - w, base, x + w, top))
        out.append(rect(x - 0.75 * s, top - 0.55 * s, x + 0.75 * s, top - 0.4 * s))
        ins = [(x - 0.6 * s, top - 0.4 * s), (x + 0.6 * s, top - 0.4 * s)]
        out += [rrect(px - 0.07 * s, py, px + 0.07 * s, py + 0.18 * s, 0.03) for px, py in ins]
        pts.append([(px, py + 0.18 * s) for px, py in ins])
    for a, b in zip(pts, pts[1:]):
        for (ax, ay), (bx, by) in zip(a, b):
            out.append(quad((ax, ay), ((ax + bx) / 2, (ay + by) / 2 - 0.3), (bx, by), 14))
    horizon = [[(-3.6, -0.2), (4.2, -0.2)]]
    mesa = [poly((-2.2, -0.2), (-1.9, 0.6), (-1.0, 0.6), (-0.7, -0.2), closed=False)]
    trail = [[(-3.6, -2.9), (2.0, -0.2)], [(-1.8, -2.9), (2.4, -0.2)]]
    poles = [o for o in out if len(o) == 5][:0]
    out += hide(horizon + mesa + trail, *[rect(x - 0.14 * s, -2.7 + (1 - s) * 2.8, x + 0.14 * s, 3) for x, s in [(-2.8, 1.0), (-0.3, 0.7), (1.5, 0.5), (2.8, 0.36), (3.7, 0.26)]])
    return make("Telegraph Poles Across the Prairie", out)


@design("wildwest_ghost_town", T)
def ghost_town(rng):
    b1 = transform(poly((-3.4, -2.4), (-3.4, 1.4), (-2.5, 1.4), (-2.5, 1.8), (-1.1, 1.8), (-1.1, -2.4)), rot=0.04)
    planks = [transform(p, rot=0.04) for p in [[(-3.1, 0.2), (-1.4, 0.9)], [(-3.1, 0.9), (-1.4, 0.2)], rect(-3.1, 0.1, -1.4, 1.0)]]
    door1 = [transform(poly((-2.6, -2.4), (-2.6, -0.7), (-1.9, -0.7), (-1.9, -2.4), closed=False), rot=0.04),
             transform(poly((-1.9, -0.7), (-1.5, -0.9), (-1.5, -2.3), (-1.9, -2.4), closed=False), rot=0.04)]
    b2 = transform(poly((-0.6, -2.4), (-0.6, 0.6), (0.6, 1.4), (1.8, 0.6), (1.8, -2.4)), rot=-0.05)
    win2 = [transform(rect(-0.3, -0.6, 0.6, 0.2), rot=-0.05), transform([(-0.3, 0.2), (0.15, -0.25), (0.05, -0.6)], rot=-0.05),
            transform([(0.15, -0.25), (0.6, -0.1)], rot=-0.05)]
    door2 = [transform(rect(0.9, -2.4, 1.5, -1.0), rot=-0.05)]
    sign = [[(-0.1, 0.9), (-0.3, 0.4)], [(0.9, 1.05), (1.0, 0.65)], transform(rect(-0.75, -0.1, 0.65, 0.45), dx=0.35, dy=0.25, rot=-0.3)]
    sign = [[(0.0, 0.85), (0.0, 0.6)], [(1.1, 0.95), (1.1, 0.45)]]
    tree = [tube(smooth([(2.8, -2.4), (2.7, -0.5), (2.9, 1.0)], 6), 0.3), [(2.75, 0.0), (2.2, 0.8), (2.0, 1.4)], [(2.85, 0.6), (3.5, 1.4)],
            [(2.2, 0.8), (1.9, 0.9)][0:0] or [(3.2, 1.0), (3.6, 1.0)]]
    tw = [ellipse(-0.1, -2.1, 0.35, 0.3, 24), ellipse(-0.15, -2.08, 0.22, 0.25, 18, rot=0.6)]
    moon = [chain(arc(2.0, 2.4, 0.55, R(60), R(300), 30), quad(arc(2.0, 2.4, 0.55, R(300), R(300), 1)[0], (1.9, 2.4), arc(2.0, 2.4, 0.55, R(60), R(60), 1)[0], 12))]
    out = b1 and [b1] + planks + door1 + [b2] + win2 + door2 + tree + tw + moon
    return make("Abandoned Ghost Town", out + [[(-3.6, -2.4), (3.8, -2.4)]])


@design("wildwest_gila_monster", T)
def gila(rng):
    spine = smooth([(2.9, 1.0), (1.8, 0.65), (0.5, 0.05), (-0.8, -0.2), (-1.9, -0.6), (-2.9, -1.5)], 8)
    def w(t):
        if t < 0.1:
            return 0.45 + 0.35 * t / 0.1
        if t < 0.16:
            return 0.8 - 0.1 * (t - 0.1) / 0.06
        if t < 0.25:
            return 0.7 + 0.5 * (t - 0.16) / 0.09
        if t < 0.55:
            return 1.2
        return 1.2 - (t - 0.55) / 0.45 * 1.1
    body = tube(spine, w)
    n = len(spine)
    legs = []
    for u, side, fwd in [(0.28, 1, 1), (0.28, -1, 1), (0.6, 1, -1), (0.6, -1, -1)]:
        i = int(u * (n - 1))
        (x, y), (x2, y2) = spine[i], spine[i + 1]
        a = math.atan2(y2 - y, x2 - x)
        nx, ny = -math.sin(a), math.cos(a)
        base = (x + side * nx * 0.45, y + side * ny * 0.45)
        knee = (base[0] + side * nx * 0.65 - fwd * 0.25 * math.cos(a), base[1] + side * ny * 0.65 - fwd * 0.25 * math.sin(a))
        foot = (knee[0] - fwd * 0.4 * math.cos(a) + side * nx * 0.15, knee[1] - fwd * 0.4 * math.sin(a) + side * ny * 0.15)
        legs.append(limb([base, knee, foot], 0.34, 0.24))
        d = math.atan2(foot[1] - knee[1], foot[0] - knee[0])
        legs += [[foot, (foot[0] + 0.25 * math.cos(d + k), foot[1] + 0.25 * math.sin(d + k))] for k in (-0.6, 0.0, 0.6)]
    bands = []
    for u in (0.3, 0.42, 0.54, 0.66, 0.78):
        i = int(u * (n - 1))
        (x, y), (x2, y2) = spine[i], spine[i + 1]
        a = math.atan2(y2 - y, x2 - x)
        bands.append(ellipse(x, y, 0.18, 0.42 * w(u) / 1.2 + 0.05, 16, rot=a))
    beads = [circle(*spine[int(u * (n - 1))], 0.1, 8) for u in (0.36, 0.48, 0.6, 0.72)]
    mouth = [quad(spine[0], spine[int(0.06 * (n - 1))], spine[int(0.1 * (n - 1))], 6)]
    out = stack(([body] + bands + beads, [body]), (legs, []))
    return make("Gila Monster", out, [eye(2.45, 1.05, 0.07)])


@design("wildwest_pony_express", T)
def pony_express(rng):
    out, hints, _ = mounted("gallop", "forward", "fly", seat=(-0.15, 0.62), lean=0.45)
    bag = [rrect(-0.85, -0.25, -0.15, 0.45, 0.1), [(-0.85, 0.15), (-0.15, 0.15)]]
    out = stack((out, []), (bag, []))
    speed = [[(-3.9, y), (-2.9, y)] for y in (0.3, -0.3, 0.9)]
    trail = [[(-3.8, -2.6), (3.6, -2.6)]]
    dust = [circle(-3.2, -2.3, 0.18, 12), circle(-3.6, -2.0, 0.13, 10), circle(-2.8, -2.4, 0.12, 10)]
    return make("Pony Express Rider", out + speed + trail + dust, hints)


@design("wildwest_porch_rocking_chair", T)
def rocking_chair(rng):
    rocker = [quad((-2.0, -2.0), (-0.6, -2.55), (1.2, -2.15), 16), quad((-1.95, -1.8), (-0.6, -2.35), (1.15, -1.95), 16)]
    back_post = [[(-1.55, -2.15), (-1.95, 1.8)], [(-1.3, -2.25), (-1.7, 1.8)]]
    top = [rrect(-2.15, 1.7, -1.45, 2.05, 0.1)]
    spindles = [[(-1.73, 0.0), (-1.9, 1.7)], [(-1.62, 0.0), (-1.75, 1.7)]]
    seat = [poly((-1.6, -0.2), (0.8, -0.2), (0.8, 0.05), (-1.6, 0.05))]
    front_leg = [[(0.6, -0.2), (0.75, -2.05)], [(0.85, -0.2), (0.98, -2.05)]]
    arm = [quad((-1.65, 0.85), (-0.3, 1.0), (0.95, 0.75), 10), [(0.75, 0.75), (0.75, 0.05)]]
    stretch = [[(-1.45, -1.2), (0.7, -1.2)]]
    hat_ = cowboy_hat(-1.85, 2.2, 0.7, tilt=0.2)
    floor = [[(-3.6, -2.6), (3.6, -2.6)], [(-3.6, -2.95), (3.6, -2.95)]] + [[(x, -2.6), (x - 0.1, -2.95)] for x in (-2.8, -1.2, 0.4, 2.0)]
    posts = [rect(2.6, -2.6, 2.95, 3.0)]
    rail = [[(2.95, 0.0), (3.8, 0.0)], [(2.95, -0.25), (3.8, -0.25)]] + [[(x, -0.25), (x, -2.6)] for x in (3.25, 3.55)]
    roof = [[(-3.6, 3.0), (3.8, 3.0)]]
    cup = [poly((1.5, -0.2), (1.55, -0.7), (1.95, -0.7), (2.0, -0.2), closed=False)][0:0]
    table = [rect(1.4, -0.35, 2.3, -0.2), [(1.55, -0.35), (1.55, -2.6)], [(2.15, -0.35), (2.15, -2.6)]]
    jug = [smooth([(1.6, -0.2), (1.55, 0.2), (1.75, 0.5), (1.75, 0.7), (1.95, 0.7), (1.95, 0.5), (2.15, 0.2), (2.1, -0.2)], 4)]
    out = stack((hat_, [chain(hat_[0]), chain(hat_[1])]), (arm + seat, seat), (top + spindles + back_post + front_leg + stretch + rocker, top),
                (jug + table, [chain(jug[0], [jug[0][0]])]), (posts + rail + floor + roof, []))
    return make("Rocking Chair on the Porch", out)


@design("wildwest_hat_and_boots_by_door", T)
def hat_boots(rng):
    door = [rect(1.4, -2.7, 3.4, 2.4), rect(1.6, -2.7, 3.2, 2.2)] + [[(x, -2.7), (x, 2.2)] for x in (2.13, 2.66)] + [circle(1.85, -0.3, 0.1, 8)]
    peg_rail = [rect(-3.4, 1.7, 1.0, 1.95)] + [circle(x, 1.82, 0.08, 8) for x in (-2.7, -1.3, 0.2)]
    hat_ = cowboy_hat(-2.7, 1.2, 0.85)
    coat = [smooth([(-1.3, 1.75), (-1.75, 1.3), (-1.9, -0.6), (-1.2, -0.75), (-0.7, -0.6), (-0.85, 1.3), (-1.3, 1.75)], 6),
            [(-1.3, 1.7), (-1.3, -0.7)], [(-1.55, 1.3), (-1.3, 0.8), (-1.05, 1.3)]]
    coil = [ellipse(0.2, 1.0, 0.55, 0.7, 36), ellipse(0.22, 0.95, 0.45, 0.62, 32)]
    b1, sh1 = boot_shape(-2.5, -1.85, 0.42)
    b2, sh2 = boot_shape(-1.0, -1.85, 0.42)
    floor = [[(-3.4, -2.7), (1.4, -2.7)]]
    boards = [[(-3.4, y), (1.4, y)] for y in (-0.9, 0.3)]
    out = stack((hat_, [chain(hat_[0]), chain(hat_[1])]), (coat + coil, [chain(coat[0])] + coil[:1]), (b2, sh2), (b1, sh1), (peg_rail + door + floor + boards, []))
    return make("Hat, Coat and Boots by the Door", out)


@design("wildwest_belt_buckle", T)
def belt_buckle(rng):
    outer = ellipse(0, 0, 2.6, 1.85, 120)
    inner = ellipse(0, 0, 2.1, 1.4, 110)
    rope = []
    for k in range(28):
        a = TAU * k / 28
        p = (2.35 * math.cos(a), 1.62 * math.sin(a))
        q = (2.35 * math.cos(a + TAU / 28), 1.62 * math.sin(a + TAU / 28))
        rope.append(lens(p, q, 0.25))
    sk, sh = skull(0, 0.25, 0.7)
    stars_ = [star(-1.45, 0.0, 0.22, 5, 0.45), star(1.45, 0.0, 0.22, 5, 0.45)]
    belt = [rect(-3.8, -0.9, -2.45, 0.9), rect(2.45, -0.9, 3.8, 0.9)]
    stitch = [[(-3.8, 0.7), (-2.55, 0.7)], [(-3.8, -0.7), (-2.55, -0.7)], [(2.55, 0.7), (3.8, 0.7)], [(2.55, -0.7), (3.8, -0.7)]]
    holes = [circle(3.25, 0.0, 0.1, 8)]
    out = stack(([outer] + rope + [inner] + sk + stars_, [outer]), (belt + stitch + holes, []))
    return make("Western Belt Buckle", out)


def suit(kind, x, y, s):
    if kind == "heart":
        return [heart(x, y, s * 0.5, 40)]
    if kind == "diamond":
        return [poly((x, y + s * 0.55), (x + s * 0.4, y), (x, y - s * 0.55), (x - s * 0.4, y))]
    if kind == "spade":
        h = [(x - px + x, -(py - y) + y) for px, py in heart(x, y + 0.05 * s, s * 0.5, 40)]
        return [h, poly((x, y - 0.2 * s), (x - 0.15 * s, y - 0.6 * s), (x + 0.15 * s, y - 0.6 * s))]
    # club
    return [circle(x, y + 0.25 * s, 0.2 * s, 14), circle(x - 0.25 * s, y - 0.05 * s, 0.2 * s, 14), circle(x + 0.25 * s, y - 0.05 * s, 0.2 * s, 14),
            poly((x, y - 0.05 * s), (x - 0.15 * s, y - 0.55 * s), (x + 0.15 * s, y - 0.55 * s))]


@design("wildwest_poker_hand", T)
def poker(rng):
    groups = []
    for k, kind in enumerate(["spade", "heart", "club", "diamond", "spade"]):
        a = R(30) - R(15) * k
        card = rrect(-0.9, -1.4, 0.9, 1.4, 0.15)
        parts = [card] + suit(kind, 0, 0.1, 1.1) + text("A", -0.55, 0.85, 0.35)
        if k == 4:
            parts = [card] + [rect(-0.65, -1.15, 0.65, 1.15)] + suit("spade", 0, 0.05, 0.9)
        cx, cy = 2.4 * math.sin(-a) * 0.9, 2.4 * math.cos(a) - 2.4 + 0.6
        groups.insert(0, ([transform(p, dx=cx, dy=cy, rot=a) for p in parts], [transform(card, dx=cx, dy=cy, rot=a)]))
    out = stack(*groups)
    chips = []
    for x, n in [(-2.6, 3), (2.7, 2)]:
        for j in range(n):
            y = -2.6 + 0.3 * j
            chips.append(ellipse(x, y + 0.3, 0.6, 0.2, 24) if j == n - 1 else [])
            chips.append(chain(arc(x, y, 0.6, math.pi, 2 * math.pi, 16)) if True else [])
        chips.append([(x - 0.6, -2.6), (x - 0.6, -2.6 + 0.3 * n)])
        chips.append([(x + 0.6, -2.6), (x + 0.6, -2.6 + 0.3 * n)])
    table = [[(-3.6, -2.95), (3.6, -2.95)]]
    return make("Saloon Poker Hand", out + [c for c in chips if c] + table)


@design("wildwest_pack_mule", T)
def pack_mule(rng):
    front, back, body, near, hh = horse_parts("stand", "up", "hang", mane=False)
    ears = [lens((1.75, 1.95), (1.45, 2.85), 0.25), lens((1.9, 2.0), (1.95, 2.9), 0.25)]
    packs = [rrect(-1.4, -0.3, 0.3, 1.15, 0.12), rrect(-1.2, 1.15, 0.2, 1.75, 0.2), ellipse(-0.5, 1.45, 0.75, 0.32, 24)]
    straps = [[(-0.9, -0.3), (-0.9, 1.15)][0:0] or [(-0.55, -0.3), (-0.55, 1.15)]]
    pan = [ellipse(0.1, 0.4, 0.42, 0.42, 30), ellipse(0.1, 0.4, 0.28, 0.28, 24)]
    shovel = [tube([(-2.0, 1.2), (0.9, 2.3)], 0.12), smooth([(0.85, 2.15), (1.2, 2.55), (1.5, 2.5), (1.4, 2.15), (1.0, 2.05)], 4, closed=True)]
    out = stack((pan, [pan[0]]), (straps + packs[:1], packs[:1]), (shovel, [shovel[0], shovel[1]]), (packs[1:], packs[1:2] + packs[2:]),
                (ears + front, [body] + near + [chain(e) for e in ears]), (back, []))
    return make("Prospector's Pack Mule", out + ground_line(-3.0, 3.4, -2.55, 3), hh)


# dropped: the subject repeats another book
def prickly_pear(rng):
    pads = [(0.0, -1.5, 1.1, 1.4, 0.0), (-1.4, 0.2, 0.85, 1.1, 0.5), (1.3, 0.4, 0.8, 1.05, -0.45), (-0.2, 1.3, 0.7, 0.95, 0.1),
            (-2.3, 1.5, 0.55, 0.75, 0.7), (2.1, 1.85, 0.55, 0.72, -0.6)]
    groups = []
    for x, y, rx, ry, rot in pads:
        pad = ellipse(x, y, rx, ry, 50, rot=rot)
        spines = [transform([(px - 0.08, py - 0.08), (px + 0.08, py + 0.08)], dx=x, dy=y, rot=rot) for px, py in
                  [(0.0, 0.0), (-0.45 * rx, 0.4 * ry), (0.45 * rx, 0.4 * ry), (-0.4 * rx, -0.45 * ry), (0.4 * rx, -0.45 * ry)]]
        groups.append(([pad] + spines, [pad]))
    fruit = [ellipse(-0.45, 2.35, 0.2, 0.3, 16), ellipse(0.15, 2.35, 0.2, 0.3, 16), ellipse(-2.6, 2.35, 0.18, 0.26, 14)]
    flower = [circle(2.4, 2.75, 0.15, 12)] + [lens((2.4, 2.75), (2.4 + 0.5 * math.cos(a), 2.75 + 0.5 * math.sin(a)), 0.4) for a in (R(30), R(90), R(150))]
    out = stack((fruit + flower, fruit + [chain(f) for f in flower[1:]]), *groups[::-1][:0], *groups)
    out += [[(-3.4, -2.9), (3.4, -2.9)], [(-0.2, -2.9), (-0.1, -2.75)][0:0]]
    lizard = [smooth([(1.6, -2.75), (2.2, -2.6), (2.9, -2.7), (3.4, -2.85)], 5)]
    return make("Prickly Pear Cactus", out + [ellipse(-2.6, -2.75, 0.5, 0.18, 20), ellipse(2.5, -2.75, 0.4, 0.15, 18)])


@design("wildwest_horse_at_trough", T)
def horse_trough(rng):
    hs, hh, hsh = horse("stand", "down", "hang", dx=-0.9, dy=0.0)
    trough = [rect(1.0, -1.3, 3.6, -0.35), [(1.2, -0.55), (3.4, -0.55)], [(1.0, -0.85), (3.6, -0.85)],
              rect(1.2, -2.5, 1.45, -1.3), rect(3.15, -2.5, 3.4, -1.3)]
    pump = [rect(3.75, -2.5, 4.1, 0.6), [(4.1, 0.4), (4.7, 0.8)], quad((3.75, 0.2), (3.4, 0.2), (3.4, -0.2), 6), circle(3.9, 0.7, 0.15, 10)]
    trough_sh = rect(1.0, -1.3, 3.6, -0.35)
    out = stack((trough, [trough_sh]), (hs, []))
    return make("Horse at the Water Trough", out + pump + ground_line(-3.6, 4.8, -2.55, 4), hh)


@design("wildwest_frontier_bank", T)
def bank(rng):
    body = rect(-3.0, -2.4, 3.0, 1.9)
    cornice = [rect(-3.3, 1.9, 3.3, 2.3), poly((-2.0, 2.3), (0.0, 3.2), (2.0, 2.3), closed=False)]
    sign = [rect(-1.3, 1.1, 1.3, 1.75)] + text("BANK", 0, 1.22, 0.42, 0.3)
    cols = []
    for x in (-1.4, 1.4):
        cols += [rect(x - 0.25, -2.4, x + 0.25, 0.8), rect(x - 0.38, 0.8, x + 0.38, 1.0), rect(x - 0.38, -2.4, x + 0.38, -2.2)]
    door = [chain([(-0.75, -2.4), (-0.75, -0.2)], arc(0, -0.2, 0.75, math.pi, 0, 16), [(0.75, -2.4)]), [(0.0, -2.4), (0.0, 0.55)]]
    wins = []
    for x in (-2.45, 2.45):
        wins += [chain([(x - 0.35, -1.4), (x - 0.35, 0.0)], arc(x, 0.0, 0.35, math.pi, 0, 10), [(x + 0.35, -1.4), (x - 0.35, -1.4)]), [(x, -1.4), (x, 0.35)]]
    steps = [rect(-1.2, -2.6, 1.2, -2.4), rect(-1.5, -2.8, 1.5, -2.6)]
    bags = [smooth([(2.6, -2.8), (2.5, -2.3), (2.75, -2.05), (2.65, -1.9), (3.05, -1.9), (2.95, -2.05), (3.2, -2.3), (3.1, -2.8)], 5, closed=True)]
    out = [body] + cornice + sign + cols + door + wins + steps + hide([[(-3.6, -2.8), (3.6, -2.8)]], steps[1]) + hide(bags, *[])
    out += text("$", 2.85, -2.6, 0.4)[0:0]
    return make("Frontier Bank", out)


# dropped: the subject repeats another book
def anvil(rng):
    top = poly((-2.6, 0.9), (2.0, 0.9), (2.0, 0.35), (1.3, 0.2), (1.0, -0.4), (-0.8, -0.4), (-1.1, 0.2), (-1.8, 0.35))
    top = poly((2.0, 0.9), (2.0, 0.35), (1.3, 0.2), (1.0, -0.4), (-0.8, -0.4), (-1.1, 0.2), (-1.8, 0.35))
    top = chain(top[:-1], quad((-1.8, 0.35), (-2.8, 0.5), (-3.4, 0.9), 10), [(2.0, 0.9)])
    base = poly((-1.0, -0.4), (0.9, -0.4), (1.3, -1.2), (-1.4, -1.2))
    hole = [rect(1.3, 0.62, 1.55, 0.82)]
    stump = [rect(-1.8, -2.8, 1.8, -1.2)] + [[(x, -2.8), (x + 0.05, -1.4)] for x in (-1.0, 0.2, 1.1)]
    hammer = [tube([(0.4, 1.3), (2.8, 2.1)], 0.18), transform(rrect(-0.25, -0.4, 0.25, 0.4, 0.08), dx=0.25, dy=1.25, rot=0.33)]
    tongs = [[(-3.2, -2.8), (-2.2, 0.0)], [(-2.8, -2.8), (-2.05, 0.0)], arc(-2.12, 0.15, 0.2, R(200), R(380), 8)]
    sparks = [star(-0.6, 1.8, 0.3, 4, 0.3), star(0.6, 2.3, 0.22, 4, 0.3), star(-1.6, 1.5, 0.2, 4, 0.3)]
    out = stack((hammer, hammer), ([top] + hole, [top]), ([base], [base]), (stump + tongs, []))
    return make("Blacksmith's Anvil and Hammer", out + sparks)


@design("wildwest_signpost", T)
def signpost(rng):
    post = rect(-0.25, -2.8, 0.25, 2.6)
    def arrow(y, d, w, word):
        x0 = 0.0
        if d > 0:
            pts = poly((-0.6, y - 0.35), (w - 0.4, y - 0.35), (w, y), (w - 0.4, y + 0.35), (-0.6, y + 0.35))
            tx = (w - 0.6) / 2 - 0.15
        else:
            pts = poly((0.6, y - 0.35), (-w + 0.4, y - 0.35), (-w, y), (-w + 0.4, y + 0.35), (0.6, y + 0.35))
            tx = -(w - 0.6) / 2 + 0.15
        return [pts] + text(word, tx, y - 0.2, 0.4, 0.25), pts
    a1, s1 = arrow(1.9, 1, 2.9, "TOWN")
    a2, s2 = arrow(0.85, -1, 2.9, "MINE")
    a3, s3 = arrow(-0.2, 1, 2.6, "FORT")
    nails = []
    out = stack((a1, [s1]), (a2, [s2]), (a3, [s3]), ([post], []))
    tw = [ellipse(-2.4, -2.45, 0.38, 0.33, 24), ellipse(-2.45, -2.45, 0.25, 0.28, 18, rot=0.6)]
    cac, _ = cactus(2.6, -2.8, 2.0, 0.3, ((0.5, -1, 0.25), (0.6, 1, 0.22)))
    return make("Signpost at the Crossroads", out + tw + cac + [[(-3.4, -2.8), (3.4, -2.8)]])
