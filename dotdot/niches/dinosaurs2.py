"""Dinosaurs niche, part 2 (pictures 10-53)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
from .safari2 import above, fringe, outside, sides, spl  # noqa: F401  (spline helpers)
import math

T = "dinosaurs"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


def scallop(line, amp, n):
    """Smooth wavy edge along a polyline (feathers, fur, membranes)."""
    return spl(fringe(line, amp, n), closed=False, res=20)


def fern(x0, y0, x1, y1, n=5, size=0.45, side=1):
    """A fern frond from (x0, y0) to (x1, y1) with paired leaflets."""
    out = [quad((x0, y0), ((x0 + x1) / 2 + 0.25 * side, (y0 + y1) / 2), (x1, y1), 16)]
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    for k in range(n):
        t = 0.25 + 0.7 * k / n
        bx, by = x0 + dx * t + 0.25 * side * 4 * t * (1 - t) * 0, y0 + dy * t
        s = size * (1 - 0.6 * k / n)
        for sg in (1, -1):
            ex = bx + s * (ux * 0.5 - uy * sg)
            ey = by + s * (uy * 0.5 + ux * sg)
            out.append(lens((bx, by), (ex, ey), 0.3))
    return out


def teeth(x0, x1, y, h, n, down=True):
    pts = []
    for k in range(n + 1):
        x = x0 + (x1 - x0) * k / n
        pts.append((x, y))
        if k < n:
            pts.append((x + (x1 - x0) / (2 * n), y - h if down else y + h))
    return pts


def mirror(parts, axis=0.0):
    return [mirror_x(p, axis) for p in parts]


def densify(pts, step=0.04):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(1, n + 1)]
    return out


def inside(p, poly_):
    x, y = p
    c = False
    for (x0, y0), (x1, y1) in zip(poly_, poly_[1:] + poly_[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            c = not c
    return c


def hide(strokes, masks):
    """Drop the parts of `strokes` that fall inside any closed mask shape
    (so a shape drawn in front hides the lines behind it)."""
    out = []
    for st in strokes:
        cur = []
        for p in densify(st):
            if any(inside(p, m) for m in masks):
                if len(cur) > 1:
                    out.append(cur)
                cur = []
            else:
                cur.append(p)
        if len(cur) > 1:
            out.append(cur)
    return [r for r in out if sum(math.dist(a, b) for a, b in zip(r, r[1:])) > 0.08]


def biped_leg(hip, knee, ankle, ball, s=1, thigh=0.55, w=0.36):
    """Side-view dinosaur hind leg: drumstick thigh, shin and three-toed
    foot pointing in direction s (+1 right, -1 left).  Returns (strokes,
    masks) where masks are the closed shapes, for hiding lines behind."""
    cx, cy = (hip[0] + knee[0]) / 2, (hip[1] + knee[1]) / 2
    rx = math.dist(hip, knee) / 2 + 0.18
    th = ellipse(cx, cy, rx, thigh * 0.75, 60, rot=math.atan2(knee[1] - hip[1], knee[0] - hip[0]))
    bx, by = ball
    foot = spl([(bx - s * 0.25, by + 0.1), (bx + s * 0.3, by + 0.06), (bx + s * 0.62, by - 0.06), (bx + s * 0.92, by - 0.22, 0),
                (bx - s * 0.28, by - 0.22, 0)])
    lower = tube([knee, ankle, ball], lambda t: w * 1.15 * (1 - 0.45 * t))
    toes = [[(bx + s * 0.45, by - 0.22), (bx + s * 0.38, by - 0.02)], [(bx + s * 0.15, by - 0.22), (bx + s * 0.1, by + 0.05)]]
    strokes = [th, foot] + hide([lower], [th, foot]) + hide(toes, [])
    return strokes, [th, lower, foot]


# ------------------------------------------------------------------ theropods

@design("dinosaurs_velociraptor", T)
def velociraptor(rng):
    body = spl([(3.0, 1.55, 0), (2.6, 1.85), (2.0, 2.0), (1.7, 1.85), (1.4, 1.4), (0.5, 1.0), (-0.5, 1.05), (-1.6, 1.1), (-2.9, 1.2),
                (-3.7, 1.25, 0), (-2.9, 0.95), (-1.6, 0.75), (-0.9, 0.45), (0.0, 0.15), (0.7, 0.25), (1.1, 0.5), (1.5, 0.95),
                (1.9, 1.3), (2.5, 1.35), (2.85, 1.45)])
    near, nm = biped_leg((-0.45, 0.55), (0.15, -0.55), (-0.4, -1.5), (-0.2, -2.25), 1, 0.5, 0.32)
    far, fm = biped_leg((-0.25, 0.55), (0.6, -0.45), (0.5, -1.45), (0.85, -2.25), 1, 0.45, 0.3)
    claw = [spl([(-0.05, -2.12), (0.12, -1.85), (0.0, -1.7, 0)], closed=False)]
    arm = tube([(1.15, 0.6), (1.4, 0.0), (1.9, -0.15)], 0.24)
    hand = [[(1.95, -0.08), (2.25, -0.05)], [(1.95, -0.18), (2.2, -0.35)], [(1.9, -0.25), (2.0, -0.5)]]
    feathers = [scallop([(1.3, -0.12), (1.55, -0.45), (1.9, -0.32)], 0.15, 4)]
    tail_feathers = [scallop([(-2.2, 0.85), (-2.9, 0.92), (-3.6, 1.2)], 0.18, 6)]
    mouth = [teeth(2.1, 2.85, 1.48, 0.1, 5)]
    stripes = [quad((x, 1.0 - 0.02 * x), (x - 0.15, 0.7), (x - 0.05, 0.45), 6) for x in (0.3, -0.3, -0.9, -1.5)]
    ground = [[(-3.6, -2.47), (3.2, -2.47)]]
    front = [body, arm] + nm
    strokes = [body] + hide(stripes + tail_feathers, nm) + hide(far, [body] + nm) + near + [arm] + hide(claw, []) + hand + feathers + mouth + ground
    return make("Velociraptor", mirror(hide([body], [arm] + nm) + strokes[1:]), [eye(-2.05, 1.68, 0.08)])


@design("dinosaurs_allosaurus", T)
def allosaurus(rng):
    body = spl([(3.2, 1.3, 0), (2.6, 1.75), (2.25, 1.88), (2.12, 2.18, 0), (1.95, 1.9), (1.6, 1.85), (1.1, 1.4), (0.0, 1.35), (-0.8, 1.3),
                (-2.0, 1.1), (-3.4, 0.6), (-4.0, 0.35, 0), (-3.2, 0.3), (-2.0, 0.4), (-1.3, 0.3), (-0.4, 0.0), (0.4, 0.2), (1.0, 0.5),
                (1.4, 0.85), (1.9, 0.9), (2.6, 1.0), (3.0, 1.1)])
    near, nm = biped_leg((-0.7, 0.45), (-0.15, -0.85), (-0.6, -1.75), (-0.35, -2.25), 1, 0.7, 0.45)
    far, fm = biped_leg((-0.55, 0.45), (-1.15, -0.7), (-1.6, -1.6), (-1.35, -2.25), 1, 0.6, 0.4)
    arm = tube([(0.85, 0.55), (1.2, 0.05), (1.55, -0.1)], 0.24)
    hand = [[(1.6, -0.02), (1.85, 0.05)], [(1.6, -0.12), (1.85, -0.25)], [(1.55, -0.2), (1.7, -0.45)]]
    mouth = [teeth(3.15, 1.95, 1.28, 0.12, 8)]
    jaw = [spl([(1.95, 1.28), (1.85, 1.15), (1.95, 1.0)], closed=False)]
    nostril = [ellipse(2.85, 1.55, 0.1, 0.06, 10)]
    holes = [ellipse(2.35, 1.5, 0.25, 0.14, 16)]
    bands = [spl([(x, 1.32 - 0.12 * max(0, -x - 0.8)), (x - 0.2, 0.95), (x - 0.1, 0.6)], closed=False) for x in (0.4, -0.3, -1.0, -1.8, -2.6)]
    ground = [[(-4.0, -2.47), (3.4, -2.47)]]
    out = hide([body], [arm] + nm) + hide(bands, nm + [arm]) + hide(far, [body] + nm) + near + [arm] + hand + mouth + jaw + nostril + holes
    return make("Allosaurus", out + ground + fern(-3.6, -2.47, -3.2, -0.6, 4, 0.4), [eye(2.0, 1.7, 0.08)])


@design("dinosaurs_carnotaurus", T)
def carnotaurus(rng):
    body = spl([(3.0, 1.55, 0), (2.95, 1.95), (2.55, 2.1), (2.0, 2.05), (1.6, 1.6), (0.6, 1.35), (-0.3, 1.4), (-1.6, 1.2), (-2.9, 0.7),
                (-3.7, 0.4, 0), (-2.9, 0.4), (-1.6, 0.55), (-0.9, 0.4), (0.0, 0.1), (0.7, 0.3), (1.4, 0.6), (1.8, 1.0), (2.4, 1.2),
                (2.85, 1.3)])
    near, nm = biped_leg((-0.4, 0.75), (0.25, -0.5), (-0.35, -1.45), (-0.1, -2.2), 1, 0.6, 0.38)
    far, fm = biped_leg((-0.3, 0.75), (-0.9, -0.4), (-1.55, -1.1), (-1.6, -2.2), 1, 0.55, 0.34)
    horns = [tube(cubic((2.35, 2.05), (2.45, 2.5), (2.2, 2.75), (1.9, 2.8), 14), lambda t: 0.22 * (1 - t) + 0.04),
             tube(cubic((2.05, 2.03), (2.05, 2.4), (1.85, 2.55), (1.6, 2.55), 14), lambda t: 0.18 * (1 - t) + 0.04)]
    arm = [spl([(1.4, 0.65), (1.6, 0.45), (1.62, 0.3), (1.45, 0.42)], closed=False)]
    mouth = [teeth(2.95, 2.1, 1.48, 0.1, 6)]
    bumps = [circle(x, y, 0.11, 10) for x, y in [(1.4, 1.2), (0.8, 1.1), (0.2, 1.1), (-0.4, 1.12), (-1.0, 1.0), (-1.6, 0.92),
                                               (0.5, 0.75), (-0.1, 0.78), (-2.2, 0.7)]]
    ground = [[(-3.7, -2.42), (3.4, -2.42)]]
    rocks = [spl([(2.2, -2.42), (2.45, -2.0), (2.9, -1.95), (3.2, -2.42)], closed=False)]
    out = hide([body], nm) + hide(bumps, nm) + hide(far, [body] + nm) + near + hide(horns[1:], [horns[0]]) + horns[:1] + arm + mouth
    return make("Carnotaurus", out + ground + rocks, [eye(2.45, 1.75, 0.08)])


@design("dinosaurs_dilophosaurus", T)
def dilophosaurus(rng):
    body = spl([(3.0, 1.6, 0), (2.5, 1.95), (1.6, 1.95), (1.25, 1.35), (0.2, 1.0), (-0.7, 1.05), (-2.0, 0.9), (-3.4, 0.5), (-4.0, 0.3, 0),
                (-3.3, 0.15), (-2.0, 0.25), (-1.3, 0.2), (-0.3, -0.1), (0.3, 0.1), (0.9, 0.45), (1.4, 0.95), (2.0, 1.2), (2.8, 1.35)])
    near, nm = biped_leg((-0.65, 0.4), (-0.1, -0.8), (-0.6, -1.7), (-0.4, -2.25), 1, 0.6, 0.36)
    far, fm = biped_leg((-0.5, 0.4), (0.35, -0.6), (0.3, -1.5), (0.7, -2.25), 1, 0.55, 0.32)
    crests = [spl([(2.55, 1.95), (2.35, 2.55), (1.95, 2.7), (1.7, 1.98)], closed=False),
              spl([(2.3, 2.25), (2.0, 2.95), (1.55, 3.0), (1.4, 2.4), (1.55, 1.98)], closed=False)]
    crests = [crests[0]] + hide(crests[1:], [crests[0] + [crests[0][0]]])
    mouth = [teeth(2.95, 2.0, 1.55, 0.1, 6)]
    notch = [spl([(2.6, 1.6), (2.5, 1.45), (2.4, 1.58)], closed=False)]
    arm = tube([(0.75, 0.55), (1.05, 0.0), (1.4, -0.12)], 0.22)
    hand = [[(1.45, -0.05), (1.7, 0.0)], [(1.45, -0.15), (1.7, -0.3)]]
    stripes = [quad((x, 1.0), (x - 0.2, 0.7), (x - 0.1, 0.35), 6) for x in (0.2, -0.5, -1.2, -1.9, -2.6)]
    ground = [[(-4.0, -2.47), (3.4, -2.47)]]
    out = hide([body], [arm] + nm) + hide(stripes, nm + [arm]) + hide(far, [body] + nm) + near + [arm] + hand + crests + mouth + notch
    return make("Dilophosaurus", mirror(out + ground + fern(3.0, -2.47, 3.3, -0.6, 4, 0.4)), [eye(-2.05, 1.7, 0.08)])


@design("dinosaurs_compsognathus", T)
def compsognathus(rng):
    def compy(dx, dy, s):
        body = spl([(2.9, 1.7, 0), (2.5, 1.95), (2.2, 1.9), (1.8, 1.5), (1.3, 0.95), (0.4, 0.7), (-0.4, 0.75), (-1.6, 0.8), (-3.0, 1.0),
                    (-3.7, 1.1, 0), (-3.0, 0.85), (-1.6, 0.5), (-0.9, 0.35), (-0.8, 0.05), (-0.45, -0.5), (-0.5, -1.0),
                    (-0.2, -1.45), (0.4, -1.55, 0), (0.42, -1.42, 0), (0.0, -1.3), (-0.25, -0.95), (-0.05, -0.45), (0.1, 0.05),
                    (0.7, 0.2), (1.2, 0.45), (1.75, 1.1), (2.15, 1.5), (2.6, 1.55)])
        far = sides([(-0.6, 0.0), (-1.1, -0.6), (-1.6, -1.0), (-1.85, -1.45)], 0.24) + [[(-2.05, -1.5), (-1.55, -1.5)]]
        arm = [[(1.2, 0.5), (1.55, 0.2), (1.75, 0.25)]]
        pts = [body] + far + arm
        return [transform(p, dx=dx, dy=dy, s=s) for p in pts]
    c = compy(-0.6, 0.0, 1.0)
    fly = [[(2.95, 2.55), (3.75, 2.75)], lens((3.3, 2.65), (3.0, 3.25), 0.25), lens((3.3, 2.65), (3.75, 3.2), 0.25),
           lens((3.3, 2.65), (3.0, 2.1), 0.25), lens((3.3, 2.65), (3.7, 2.15), 0.25)]
    ground = [[(-3.6, -2.0), (3.6, -2.0)]]
    plants = fern(-3.2, -2.0, -2.6, 0.6, 5, 0.5) + fern(2.8, -2.0, 2.4, 0.2, 5, 0.45, -1)
    stones = [spl([(-0.6, -2.0), (-0.3, -1.7), (0.3, -1.75), (0.5, -2.0)], closed=False)]
    return make("Compsognathus Chasing a Dragonfly", c + fly + ground + plants + stones, [eye(-0.6 + 2.45, 1.75, 0.06)])


@design("dinosaurs_gallimimus", T)
def gallimimus(rng):
    body = spl([(3.2, 2.4, 0), (2.8, 2.65), (2.5, 2.6), (2.0, 2.0), (1.5, 1.1), (0.6, 0.75), (-0.3, 0.85), (-1.5, 0.85), (-2.8, 0.7),
                (-3.5, 0.6, 0), (-2.8, 0.45), (-1.5, 0.45), (-0.9, 0.35), (-0.8, 0.05), (-0.25, -0.75), (-0.8, -1.45),
                (-0.45, -2.3), (-0.5, -2.45, 0), (0.25, -2.45, 0), (0.2, -2.3, 0), (-0.2, -2.2), (-0.55, -1.5), (0.05, -0.65),
                (0.25, 0.0), (0.8, 0.2), (1.3, 0.6), (1.75, 1.2), (2.2, 2.0), (2.55, 2.3), (2.9, 2.35)])
    far = sides([(-0.5, 0.0), (-1.3, -0.7), (-1.85, -1.25), (-2.4, -1.5)], 0.26) + [[(-2.55, -1.55), (-2.95, -1.4)], [(-2.55, -1.55), (-2.85, -1.75)]]
    arm = sides([(1.25, 0.45), (1.55, -0.1), (1.9, -0.2)], 0.18) + [[(1.9, -0.15), (2.15, -0.35)], [(1.85, -0.25), (2.0, -0.5)]]
    beak = [[(3.2, 2.4), (2.75, 2.45)]]
    dust = [spl([(x - 0.4, -2.45), (x - 0.2, -2.15), (x, -2.2), (x + 0.2, -2.0), (x + 0.4, -2.45)], closed=False) for x in (-1.9, -3.0)]
    ground = [[(-3.6, -2.45), (3.4, -2.45)]]
    return make("Running Gallimimus", [body] + far + arm + beak + dust + ground + fern(2.9, -2.45, 3.3, -0.6, 4, 0.4),
                [eye(2.72, 2.55, 0.06)])


@design("dinosaurs_therizinosaurus", T)
def therizinosaurus(rng):
    body = spl([(2.0, 3.0, 0), (1.6, 3.3), (1.3, 3.2), (1.1, 2.6), (0.6, 1.8), (0.0, 1.5), (-0.8, 0.9), (-1.6, 0.3), (-2.4, -0.4, 0),
                (-1.6, -0.4), (-1.2, -0.9), (-1.1, -1.4), (-0.9, -2.0), (-1.0, -2.6), (-1.05, -2.8, 0), (0.0, -2.8, 0),
                (-0.05, -2.65, 0), (-0.4, -2.55), (-0.35, -2.0), (-0.2, -1.6), (0.5, -1.3), (1.1, -0.5), (1.3, 0.4), (1.4, 1.4),
                (1.5, 2.2), (1.6, 2.75), (1.75, 2.85)])
    feathers = [fringe(spl([(1.15, 2.7), (0.6, 1.85), (0.0, 1.55), (-0.8, 0.95), (-1.6, 0.35)], closed=False), 0.16, 14)]
    arm = sides([(0.8, 1.2), (1.4, 0.5), (1.9, 0.0)], 0.32)
    wrist = [arc(1.9, 0.0, 0.16, math.radians(-150), math.radians(30), 8)]
    claws = [tube(cubic((x, y), (x + 0.4, y - 0.4), (x + 0.6, y - 1.1), (x + 0.4, y - 1.7), 20), lambda t: 0.16 * (1 - t) + 0.02)
             for x, y in [(1.82, -0.12), (2.0, -0.08), (2.15, 0.0)]]
    arm_feathers = [scallop([(0.85, 0.95), (1.2, 0.4), (1.6, -0.05)], -0.2, 4)]
    belly = [spl([(0.2, 0.6), (0.6, -0.4), (0.3, -1.2)], closed=False)]
    tree = [spl([(-3.0, -2.8), (-3.0, -0.5), (-2.8, 1.5)], closed=False), spl([(-3.6, 1.2), (-3.0, 2.6), (-2.0, 2.8), (-1.4, 2.0),
                                                                             (-2.2, 1.2)])]
    ground = [[(-3.6, -2.8), (3.2, -2.8)]]
    return make("Therizinosaurus", [body] + feathers + arm + wrist + claws + arm_feathers + belly + tree + ground,
                [eye(1.55, 3.05, 0.06)])


@design("dinosaurs_oviraptor_nest", T)
def oviraptor_nest(rng):
    body = spl([(-2.2, -1.4, 0), (-2.6, -0.9), (-3.0, -0.5, 0), (-2.0, 0.05), (-0.8, 0.6), (0.3, 0.7), (0.9, 1.3), (1.0, 2.0),
                (1.3, 2.75, 0), (1.7, 2.3), (2.2, 1.9, 0), (1.9, 1.7), (1.6, 1.75), (1.4, 1.3), (1.5, 0.6), (1.6, 0.0),
                (1.9, -0.8), (2.1, -1.4, 0)], closed=False)
    beak = [[(2.2, 1.9), (1.75, 1.95)]]
    wing = [spl([(1.1, 0.4), (0.2, 0.3), (-0.8, 0.0), (-1.7, -0.6)], closed=False),
            scallop([(-1.7, -0.6), (-0.6, -1.2), (0.6, -1.25), (1.4, -0.7)], -0.2, 7)]
    feathers = [spl([(0.6, 0.0), (-0.3, -0.3), (-1.0, -0.6)], closed=False), [(1.1, 0.4), (1.4, -0.7)]]
    tail = [scallop([(-2.0, 0.05), (-2.5, -0.2), (-3.0, -0.5)], 0.15, 4)]
    nest = [spl([(-3.2, -2.5), (-2.75, -1.65), (-2.2, -1.42)], closed=False), spl([(2.1, -1.42), (2.75, -1.65), (3.2, -2.5)], closed=False),
            [(-3.4, -2.5), (3.4, -2.5)], spl([(-2.8, -2.2), (0, -2.0), (2.8, -2.2)], closed=False)]
    eggs = [ellipse(x, -1.72, 0.2, 0.34, 20, rot=r) for x, r in [(-1.8, 0.4), (-1.1, 0.15), (-0.4, 0.0), (0.3, 0.0), (1.0, -0.15),
                                                                (1.7, -0.4)]]
    return make("Oviraptor Guarding Its Nest", [body] + beak + wing + feathers + tail + nest + eggs, [eye(1.45, 2.05, 0.07)])


@design("dinosaurs_microraptor", T)
def microraptor(rng):
    body = spl([(0, 2.6), (0.22, 2.4), (0.18, 2.0), (0.4, 1.35), (0.45, 0.6), (0.3, -0.3), (0.12, -0.8), (-0.12, -0.8), (-0.3, -0.3),
                (-0.45, 0.6), (-0.4, 1.35), (-0.18, 2.0), (-0.22, 2.4)])
    wing = chain(spl([(0.4, 1.35), (1.4, 1.75), (2.4, 1.92), (3.3, 1.7, 0)], closed=False),
                 scallop([(3.3, 1.7), (2.5, 1.0), (1.4, 0.75), (0.45, 0.65)], -0.2, 8))
    leg_wing = chain(spl([(0.35, -0.1), (1.2, -0.45), (2.2, -1.1, 0)], closed=False),
                     scallop([(2.2, -1.1), (1.4, -1.3), (0.6, -1.0), (0.2, -0.6)], -0.16, 5))
    quills = [[(0.8, 1.45), (1.0, 0.85)], [(1.5, 1.7), (1.8, 0.9)], [(2.3, 1.85), (2.6, 1.15)], [(0.9, -0.35), (1.05, -0.95)],
              [(1.5, -0.65), (1.6, -1.15)]]
    right = [wing, leg_wing] + quills
    tail = [[(0, -0.8), (0, -2.2)], spl([(0, -1.6), (0.35, -2.2), (0.0, -3.0, 0), (-0.35, -2.2)])]
    claws = [[(1.8, 1.85), (1.85, 2.1)], [(1.95, 1.88), (2.05, 2.12)]]
    sky = [spl([(-3.6, -2.0), (-2.8, -1.6), (-2.2, -1.9), (-1.6, -1.55), (-1.0, -1.95)], closed=False),
           spl([(1.4, 2.8), (2.0, 3.1), (2.6, 2.85), (3.2, 3.1)], closed=False)]
    return make("Four-Winged Microraptor", [body] + right + mirror(right) + tail + claws + mirror(claws) + sky,
                [eye(-0.1, 2.3, 0.05), eye(0.1, 2.3, 0.05)])


@design("dinosaurs_archaeopteryx", T)
def archaeopteryx(rng):
    body = spl([(2.2, 1.6, 0), (1.75, 1.95), (1.4, 1.85), (1.2, 1.4), (0.6, 0.9), (0.0, 0.4), (0.2, 0.0), (0.8, -0.2), (1.3, 0.3),
                (1.5, 0.9), (1.9, 1.3)])
    toothy = [teeth(2.15, 1.65, 1.55, 0.07, 3)]
    wing = chain(spl([(0.95, 1.15), (0.3, 2.2), (-0.6, 2.75), (-1.9, 3.0, 0)], closed=False),
                 scallop([(-1.9, 3.0), (-1.2, 2.2), (-0.4, 1.4), (0.3, 0.75)], -0.22, 7))
    fingers = [spl([(0.3, 2.2), (0.55, 2.55), (0.4, 2.65, 0)], closed=False), spl([(0.15, 2.3), (0.3, 2.7), (0.12, 2.75, 0)], closed=False)]
    quills = [[(-0.6, 2.75), (-0.75, 2.0)], [(0.0, 2.4), (-0.15, 1.55)], [(-1.2, 2.88), (-1.25, 2.4)]]
    shaft = [(0.05, 0.2) + (0,)[:0], (-2.5, -1.6)]
    feathers = []
    for k in range(7):
        t = 0.12 + 0.13 * k
        x, y = 0.05 + (-2.55) * t, 0.2 + (-1.8) * t
        feathers += [lens((x, y), (x - 0.45, y + 0.25), 0.3), lens((x, y), (x + 0.05, y - 0.5), 0.3)]
    tail = [[(0.05, 0.2), (-2.5, -1.6)]] + feathers
    legs = [[(0.6, -0.15), (0.65, -0.75)], [(0.95, -0.1), (1.05, -0.7)], [(0.45, -0.8), (0.95, -0.75)], [(0.8, -0.78), (1.3, -0.7)]]
    branch = sides([(-1.0, -1.0), (1.0, -0.8), (3.4, -0.4)], 0.3) + [[(-1.0, -1.15), (-1.0, -0.85)]]
    leaves = [lens((2.6, -0.3), (3.0, 0.5), 0.3), lens((2.9, -0.55), (3.6, -1.0), 0.3), [(2.4, -0.3), (2.6, -0.3)]]
    return make("Archaeopteryx", [body, wing] + toothy + fingers + quills + tail + legs + branch + leaves, [eye(1.62, 1.72, 0.06)])


@design("dinosaurs_pteranodon", T)
def pteranodon(rng):
    right = [chain(spl([(0.3, 0.6), (1.2, 1.0), (2.0, 1.2), (3.6, 0.6, 0)], closed=False),
                   spl([(3.6, 0.6), (2.4, 0.15), (1.4, -0.2), (0.3, -0.55)], closed=False)),
             [(1.95, 1.2), (2.05, 1.45)], [(2.05, 1.15), (2.25, 1.35)], [(0.25, -0.8), (0.45, -1.25)]]
    body = [ellipse(0, 0.0, 0.38, 0.9, 40)]
    neck = sides([(0.0, 0.85), (0.15, 1.25), (0.45, 1.5)], 0.3)
    head = spl([(0.3, 1.38), (0.25, 1.62), (-0.3, 2.0), (-1.1, 2.35, 0), (-0.2, 2.15), (0.6, 1.85), (1.4, 1.72), (2.4, 1.6, 0),
                (1.4, 1.45), (0.62, 1.4)], closed=False)
    fish = [spl([(2.25, 1.6), (2.4, 1.3), (2.35, 0.9), (2.2, 0.75, 0), (2.08, 0.95), (2.1, 1.35)]),
            poly((2.2, 0.75), (2.0, 0.5), (2.4, 0.5), closed=False)]
    sea = [wave(-3.6, 3.6, -2.0, 0.12, 6, 120), wave(-3.0, 3.0, -2.6, 0.1, 5, 100)]
    sun = [circle(-2.6, 2.5, 0.55, 40)]
    return make("Pteranodon Fishing", body + neck + [head] + right + mirror(right) + fish + sea + sun, [eye(0.32, 1.72, 0.06)])


def along(line, t):
    """Point at fraction t of a polyline plus its left-hand unit normal."""
    i = min(len(line) - 2, max(1, int(t * (len(line) - 1))))
    (x0, y0), (x1, y1) = line[i - 1], line[i + 1]
    L = math.hypot(x1 - x0, y1 - y0) or 1
    return line[i], (-(y1 - y0) / L, (x1 - x0) / L)


# ------------------------------------------------------------------ plant eaters

@design("dinosaurs_brachiosaurus", T)
def brachiosaurus(rng):
    body = spl([(2.6, 3.05, 0), (2.2, 3.4), (1.95, 3.45), (1.75, 3.2), (1.4, 2.2), (0.9, 1.0), (0.0, 0.4), (-1.2, 0.0), (-2.4, -0.4),
                (-3.5, -0.6, 0), (-2.4, -0.8), (-1.6, -0.75), (-1.5, -1.0), (-1.45, -2.4), (-1.5, -2.6, 0), (-0.85, -2.6, 0),
                (-0.9, -2.4), (-0.95, -1.3), (-0.2, -1.15), (0.4, -1.0), (0.45, -1.3), (0.5, -2.4), (0.45, -2.6, 0), (1.1, -2.6, 0),
                (1.05, -2.4), (1.05, -1.0), (1.3, -0.2), (1.5, 0.8), (1.85, 2.0), (2.15, 2.85), (2.4, 2.9)], res=18)
    far = [leg(-0.65, -0.2, -1.1, -2.52), leg(1.15, 1.55, -0.6, -2.52)]
    tree = [spl([(3.2, -2.6), (3.15, -0.5), (3.35, 1.6)], closed=False), spl([(3.4, -2.6), (3.45, -0.5), (3.6, 1.6)], closed=False),
            spl([(2.65, 2.2), (2.9, 3.0), (3.6, 3.3), (4.3, 2.9), (4.4, 2.0), (3.8, 1.5), (3.0, 1.6)])]
    twig = [[(2.6, 3.0), (2.95, 2.75)], lens((2.75, 2.85), (2.7, 2.45), 0.35)]
    nails = [arc(x, -2.6, 0.1, 0, math.pi, 5) for x in (-1.3, -1.05, 0.65, 0.9)]
    skin = [spl([(0.9, 0.6), (0.6, -0.2), (0.75, -0.9)], closed=False), spl([(-1.0, -0.1), (-1.2, -0.5), (-1.1, -0.9)], closed=False)]
    ground = [[(-3.6, -2.6), (4.4, -2.6)]]
    return make("Brachiosaurus Eating Leaves", [body] + far + tree + twig + nails + skin + ground, [eye(2.15, 3.2, 0.06)])


@design("dinosaurs_diplodocus", T)
def diplodocus(rng):
    body = spl([(-3.9, 1.4, 0), (-3.6, 1.7), (-3.3, 1.65), (-2.6, 1.6), (-1.5, 1.55), (-0.6, 1.4), (0.4, 1.7), (1.2, 1.55),
                (2.4, 1.1), (3.5, 0.6), (4.6, 0.3), (5.2, 0.25, 0), (4.6, 0.18), (3.5, 0.35), (2.4, 0.6), (1.9, 0.5), (1.85, -0.3),
                (1.8, -1.4), (1.85, -1.6, 0), (1.2, -1.6, 0), (1.25, -1.4), (1.2, -0.4), (0.3, -0.3), (-0.5, -0.2), (-0.6, -0.5),
                (-0.65, -1.4), (-0.6, -1.6, 0), (-1.2, -1.6, 0), (-1.15, -1.4), (-1.15, -0.3), (-1.4, 0.4), (-2.4, 1.05),
                (-3.3, 1.25), (-3.7, 1.3)], res=16)
    far = [leg(0.8, 1.2, -0.35, -1.52), leg(-0.6, -0.2, -0.25, -1.52)]
    spines = [fringe(spl([(-2.6, 1.62), (-1.5, 1.57), (-0.6, 1.42), (0.4, 1.72), (1.2, 1.57), (2.4, 1.12)], closed=False), 0.14, 18)]
    ground = [[(-4.0, -1.6), (5.2, -1.6)]]
    volcano = [poly((-3.6, 2.4), (-2.6, 3.6), (-2.0, 3.6), (-1.0, 2.4), closed=False), circle(-2.3, 4.0, 0.3, 20), circle(-1.9, 4.4, 0.35, 20)]
    plants = fern(3.2, -1.6, 3.6, 0.0, 4, 0.4) + fern(-3.4, -1.6, -3.0, 0.2, 4, 0.4)
    return make("Diplodocus", [body] + far + spines + ground + volcano + plants, [eye(-3.45, 1.5, 0.05)])


@design("dinosaurs_ankylosaurus", T)
def ankylosaurus(rng):
    body = spl([(-3.0, -0.3, 0), (-2.85, 0.15), (-2.35, 0.4), (-2.05, 0.6, 0), (-1.9, 0.3), (-1.3, 0.9), (0.0, 1.25), (1.3, 1.0),
                (2.0, 0.5), (3.0, 0.2), (3.25, 0.4), (3.55, 0.55), (3.9, 0.4), (4.05, 0.05), (3.9, -0.3), (3.5, -0.38), (3.2, -0.15),
                (2.6, -0.05), (1.9, 0.05), (1.6, -0.3), (1.5, -0.6), (1.5, -1.3), (1.45, -1.5, 0), (0.85, -1.5, 0), (0.9, -1.3),
                (0.9, -0.6), (0.0, -0.55), (-0.8, -0.5), (-0.9, -0.75), (-0.95, -1.3), (-1.0, -1.5, 0), (-1.6, -1.5, 0),
                (-1.55, -1.3), (-1.55, -0.6), (-1.9, -0.3), (-2.5, -0.5), (-2.85, -0.45)])
    skirt = spl([(-1.8, 0.2), (0.0, -0.05), (1.75, 0.15)], closed=False)
    spikes = []
    for k in range(7):
        (x, y), (nx, ny) = along(skirt, 0.07 + 0.86 * k / 6)
        spikes.append(poly((x - 0.16, y + 0.02), (x - 0.05 + 0.15 * (k - 3) / 3, y - 0.4), (x + 0.16, y - 0.02), closed=False))
    plates = [ellipse(x, y, 0.2, 0.13, 14) for x, y in [(-0.9, 0.5), (-0.3, 0.6), (0.3, 0.6), (0.9, 0.5), (-0.6, 0.95), (0.0, 1.0),
                                                       (0.6, 0.95), (-1.4, 0.4), (1.4, 0.4)]]
    tail_spikes = [poly((x - 0.12, y), (x, y + 0.28), (x + 0.12, y), closed=False) for x, y in [(2.3, 0.4), (2.75, 0.27)]]
    club = [spl([(3.5, 0.5), (3.6, 0.05), (3.5, -0.32)], closed=False)]
    far = [leg(0.5, 0.85, -0.6, -1.42), leg(-0.85, -0.5, -0.5, -1.42)]
    ground = [[(-3.3, -1.5), (4.1, -1.5)]]
    return make("Ankylosaurus", [body, skirt] + spikes + plates + tail_spikes + club + far + ground + fern(3.2, -1.5, 3.5, 0.0, 3, 0.35)[:0],
                [eye(-2.45, 0.1, 0.07)])


@design("dinosaurs_kentrosaurus", T)
def kentrosaurus(rng):
    body = spl([(3.2, -0.2, 0), (3.0, 0.1), (2.6, 0.15), (2.0, 0.25), (1.0, 1.0), (0.0, 1.3), (-0.8, 1.2), (-1.8, 0.7), (-3.0, 0.2),
                (-3.8, -0.1, 0), (-3.0, -0.1), (-1.8, 0.2), (-1.4, -0.1), (-1.35, -0.5), (-1.3, -1.6), (-1.35, -1.8, 0),
                (-0.75, -1.8, 0), (-0.75, -1.6), (-0.8, -0.6), (0.2, -0.65), (0.9, -0.55), (1.1, -0.75), (1.05, -1.6),
                (1.0, -1.8, 0), (1.55, -1.8, 0), (1.55, -1.6), (1.6, -0.6), (2.0, -0.3), (2.5, -0.35), (2.95, -0.4)])
    back = spl([(2.0, 0.25), (1.0, 1.0), (0.0, 1.3), (-0.8, 1.2), (-1.8, 0.7), (-3.0, 0.2), (-3.6, 0.0)], closed=False)
    armour = []
    for k in range(13):
        t = 0.06 + 0.88 * k / 12
        (x, y), (nx, ny) = along(back, t)
        nx, ny = -nx, -ny
        if t < 0.38:
            h, w = 0.55, 0.22
            armour.append(spl([(x - w * ny * 0 - w, y), (x + nx * h * 0.6 - 0.05, y + ny * h * 0.6), (x + nx * h, y + ny * h, 0),
                               (x + w, y)], closed=False))
        else:
            h, w = 0.95 - 0.35 * (t - 0.38), 0.12
            tx, ty = x + nx * h - 0.35 * h, y + ny * h
            armour.append(poly((x - w, y), (tx, ty), (x + w, y), closed=False))
    shoulder = [poly((1.2, 0.2), (0.1, -0.5), (1.0, -0.1), closed=False)]
    far = [leg(-0.65, -0.25, -0.6, -1.72), leg(0.6, 1.0, -0.6, -1.72)]
    ground = [[(-3.8, -1.8), (3.4, -1.8)]]
    return make("Kentrosaurus", [body] + armour + shoulder + far + ground + fern(2.8, -1.8, 3.2, -0.2, 3, 0.35)[:0],
                [eye(2.7, -0.02, 0.06)])


@design("dinosaurs_parasaurolophus", T)
def parasaurolophus(rng):
    body = spl([(3.0, 1.2, 0), (2.95, 1.45), (2.5, 1.75), (2.2, 1.95), (1.2, 2.6), (0.85, 2.7, 0), (0.85, 2.5, 0), (1.9, 1.75), (1.7, 1.55),
                (1.2, 1.2), (0.2, 1.35), (-0.8, 1.4), (-2.0, 1.1), (-3.4, 0.5), (-4.0, 0.25, 0), (-3.3, 0.15), (-2.0, 0.35),
                (-1.3, 0.2), (-0.3, -0.2), (0.6, -0.1), (1.0, 0.2), (1.5, 0.7), (2.2, 0.95), (2.7, 1.05)])
    near, nm = biped_leg((-0.8, 0.55), (-0.3, -0.75), (-0.85, -1.65), (-0.65, -2.25), 1, 0.75, 0.45)
    far, fm = biped_leg((-0.65, 0.55), (-1.2, -0.65), (-1.75, -1.5), (-1.6, -2.25), 1, 0.65, 0.4)
    arm = tube([(0.8, 0.25), (0.55, -0.85), (0.95, -1.9), (1.2, -2.3)], lambda t: 0.34 - 0.12 * t)
    farm = tube([(0.45, 0.1), (0.25, -0.9), (0.55, -1.9), (0.75, -2.3)], lambda t: 0.3 - 0.1 * t)
    hands = [[(1.05, -2.42), (1.45, -2.42)], [(0.6, -2.42), (0.95, -2.42)]]
    crest_line = [spl([(2.15, 1.85), (1.4, 2.35), (0.95, 2.58)], closed=False)]
    bill = [[(3.0, 1.2), (2.55, 1.25)]]
    stripes = [quad((x, 1.3), (x - 0.2, 0.95), (x - 0.1, 0.6), 6) for x in (0.2, -0.5, -1.2, -1.9, -2.6)]
    ground = [[(-4.0, -2.47), (3.4, -2.47)]]
    out = hide([body], [arm] + nm) + hide(stripes, nm + [arm]) + hide(far + [farm], [body, arm] + nm) + near + [arm] + hide(hands, [arm]) + crest_line + bill
    return make("Parasaurolophus", out + ground + fern(2.4, -2.47, 2.9, -0.4, 5, 0.45) + fern(-3.6, -2.47, -3.1, -0.9, 4, 0.4),
                [eye(2.35, 1.4, 0.07)])


@design("dinosaurs_iguanodon", T)
def iguanodon(rng):
    body = spl([(-3.1, 1.3, 0), (-3.0, 1.6), (-2.4, 1.85), (-2.0, 1.75), (-1.6, 1.4), (-0.6, 1.25), (0.6, 1.4), (1.8, 1.1), (3.0, 0.6),
                (3.8, 0.3, 0), (2.9, 0.25), (1.8, 0.45), (1.3, 0.3), (1.35, -0.4), (1.3, -1.4), (1.35, -2.3), (1.3, -2.45, 0),
                (0.55, -2.45, 0), (0.6, -2.3), (0.65, -1.4), (0.5, -0.5), (-0.3, -0.3), (-0.6, -0.5), (-1.0, -1.5), (-1.2, -2.3),
                (-1.2, -2.45, 0), (-1.7, -2.45, 0), (-1.6, -2.3), (-1.4, -1.4), (-1.15, -0.4), (-1.3, 0.2), (-1.8, 0.75),
                (-2.4, 0.95), (-2.9, 1.1)], res=16)
    spike = [spl([(-1.42, -1.85), (-1.85, -1.6), (-2.05, -1.45, 0), (-1.5, -1.6)], closed=False)]
    far = [leg(-0.95, -0.6, -0.6, -2.38), leg(0.95, 1.4, -0.4, -2.38)]
    mouth = [spl([(-3.05, 1.35), (-2.6, 1.3), (-2.3, 1.38)], closed=False)]
    skin = [spl([(-0.2, 1.2), (0.0, 0.5), (-0.2, -0.2)], closed=False), spl([(0.9, 1.3), (1.0, 0.7), (0.85, 0.3)], closed=False)]
    ground = [[(-3.3, -2.45), (3.8, -2.45)]]
    return make("Iguanodon", [body] + spike + far + mouth + skin + ground + fern(2.6, -2.45, 3.0, -0.8, 4, 0.4),
                [eye(-2.35, 1.55, 0.07)])


@design("dinosaurs_pachycephalosaurus", T)
def pachycephalosaurus(rng):
    body = spl([(3.0, 0.85, 0), (2.95, 1.15), (2.85, 1.6), (2.55, 2.12), (2.05, 2.2), (1.65, 1.85), (1.4, 1.3), (0.4, 1.25), (-0.6, 1.3),
                (-1.8, 1.15), (-3.0, 0.9), (-3.6, 0.85, 0), (-3.0, 0.6), (-1.8, 0.55), (-1.2, 0.35), (-0.2, 0.0), (0.6, 0.15), (1.2, 0.45),
                (1.8, 0.7), (2.4, 0.75), (2.8, 0.8)])
    near, nm = biped_leg((-0.6, 0.55), (-0.1, -0.7), (-0.6, -1.6), (-0.35, -2.25), 1, 0.6, 0.38)
    far, fm = biped_leg((-0.45, 0.55), (0.35, -0.55), (0.3, -1.45), (0.7, -2.25), 1, 0.55, 0.34)
    knobs = []
    for a in (100, 125, 150, 175, 200):
        x, y = 2.3 + 0.62 * math.cos(math.radians(a)), 1.5 + 0.62 * math.sin(math.radians(a))
        ux, uy = math.cos(math.radians(a)), math.sin(math.radians(a))
        knobs.append(poly((x - 0.1 * uy, y + 0.1 * ux), (x + 0.3 * ux, y + 0.3 * uy), (x + 0.1 * uy, y - 0.1 * ux), closed=False))
    knobs = hide(knobs, [body])
    rim = [spl([(2.85, 1.4), (2.3, 1.5), (1.75, 1.6)], closed=False)]
    bumps = [circle(x, y, 0.09, 8) for x, y in [(2.75, 1.1), (2.55, 1.25)]]
    arm = tube([(1.2, 0.5), (1.45, 0.1), (1.75, 0.0)], 0.2)
    hand = [[(1.8, 0.07), (2.0, 0.1)], [(1.8, -0.05), (1.95, -0.2)]]
    mouth = [spl([(3.0, 0.85), (2.6, 0.92), (2.35, 0.95)], closed=False)]
    stripes = [quad((x, 1.25), (x - 0.2, 0.95), (x - 0.1, 0.6), 6) for x in (0.5, -0.2, -0.9, -1.6, -2.3)]
    ground = [[(-3.7, -2.47), (3.4, -2.47)]]
    out = hide([body], [arm] + nm) + hide(stripes, nm + [arm]) + hide(far, [body] + nm) + near + [arm] + hand + knobs + rim + bumps + mouth
    return make("Pachycephalosaurus", out + ground + fern(-3.4, -2.47, -3.0, -0.6, 4, 0.4) + fern(3.1, -2.47, 3.4, -0.9, 4, 0.4),
                [eye(2.3, 1.25, 0.07)])


@design("dinosaurs_spinosaurus", T)
def spinosaurus(rng):
    body = spl([(-1.4, -0.6, 0), (-1.6, 0.2), (-2.0, 0.45), (-2.7, 0.5), (-3.8, 0.62, 0), (-3.75, 0.8), (-2.9, 1.0), (-2.3, 1.2),
                (-1.95, 1.55), (-1.8, 1.72, 0), (-1.5, 1.45), (-1.1, 1.1), (-0.8, 1.15), (0.2, 1.05), (1.4, 0.95), (2.3, 0.9), (3.0, 0.4),
                (3.8, -0.2), (4.2, -0.6, 0)], closed=False, res=16)
    sail = spl([(-0.8, 1.15), (-0.3, 2.6), (0.6, 3.05), (1.5, 2.65), (2.1, 1.6), (2.3, 0.92)], closed=False)
    ribs = []
    for k in range(1, 8):
        (x, y), _ = along(sail, k / 8)
        bx = -0.8 + 3.1 * k / 8
        ribs.append([(bx, 1.1 - 0.05 * k / 8 * 3), (x, y)])
    mouth = [teeth(-3.75, -2.2, 0.7, 0.09, 9)]
    fish = []
    arm = sides([(-1.1, 0.2), (-1.5, -0.1), (-1.8, -0.35)], 0.2) + [[(-1.8, -0.3), (-2.05, -0.35)], [(-1.8, -0.42), (-2.0, -0.55)]]
    water = [wave(-3.6, 4.4, -0.6, 0.08, 9, 160), wave(-3.0, 3.6, -1.3, 0.08, 7, 120), wave(-2.0, 2.6, -2.0, 0.07, 5, 90)]
    return make("Spinosaurus Fishing", [body, sail] + ribs + mouth + fish + water, [eye(-1.95, 1.2, 0.08)])


@design("dinosaurs_styracosaurus", T)
def styracosaurus(rng):
    cx, cy = 0.0, 0.6
    pts = [(-1.25, -0.6)]
    spikes = [150, 128, 106, 74, 52, 30]

    def P(a, r, sharp=False):
        q = (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
        return q + ((0,) if sharp else ())
    pts += [P(205, 1.9), P(180, 2.0), P(165, 2.05)]
    for a in spikes:
        pts += [P(a + 9, 2.0), P(a, 3.4, True), P(a - 9, 2.0)]
        if a != 30:
            pts.append(P(a - 11, 2.08))
    pts += [P(15, 2.05), P(0, 2.0), P(-25, 1.9), (1.25, -0.6)]
    frill = spl(pts, closed=False)
    holes = [ellipse(-1.15, 1.6, 0.35, 0.22, 20, rot=0.6), ellipse(1.15, 1.6, 0.35, 0.22, 20, rot=-0.6)]
    face = spl([(0, 1.1), (0.7, 0.95), (1.15, 0.4), (1.3, -0.3), (1.0, -1.0), (0.5, -1.7), (0.2, -2.5), (0, -2.75, 0), (-0.2, -2.5),
                (-0.5, -1.7), (-1.0, -1.0), (-1.3, -0.3), (-1.15, 0.4), (-0.7, 0.95)])
    face = [p for p in face if not (abs(p[0]) < 0.17 and p[1] > 0.8)]
    k = max(range(len(face) - 1), key=lambda i: math.dist(face[i], face[i + 1]))
    face = [face[:k + 1], face[k + 1:]]
    horn = spl([(-0.28, -1.2), (-0.12, 0.6), (0.0, 1.9, 0), (0.12, 0.6), (0.28, -1.2)], closed=False)
    horn_base = [quad((-0.28, -1.2), (0, -1.35), (0.28, -1.2), 8)]
    brows = [spl([(-0.95, 0.45), (-0.6, 0.6), (-0.3, 0.45)], closed=False), spl([(0.95, 0.45), (0.6, 0.6), (0.3, 0.45)], closed=False)]
    nostrils = [ellipse(-0.35, -1.55, 0.1, 0.15, 10), ellipse(0.35, -1.55, 0.1, 0.15, 10)]
    beak = [quad((-0.35, -2.05), (0, -2.25), (0.35, -2.05), 8)]
    cheeks = [poly((-1.25, -0.3), (-1.7, -0.7), (-1.1, -0.65), closed=False), poly((1.25, -0.3), (1.7, -0.7), (1.1, -0.65), closed=False)]
    return make("Styracosaurus Portrait", [frill, horn] + face + holes + horn_base + brows + nostrils + beak + cheeks,
                [eye(-0.62, 0.25, 0.1), eye(0.62, 0.25, 0.1)])


@design("dinosaurs_protoceratops", T)
def protoceratops(rng):
    body = spl([(3.0, 0.2, 0), (2.85, 0.6), (2.5, 0.95), (2.15, 1.15), (1.75, 2.1), (1.4, 2.45), (0.85, 2.35, 0), (0.65, 1.7), (0.3, 1.2), (-0.5, 1.35),
                (-1.2, 1.2), (-2.0, 0.8), (-3.0, 0.2), (-3.4, -0.1, 0), (-2.8, -0.2), (-2.0, 0.1), (-1.6, -0.2), (-1.55, -0.6),
                (-1.5, -1.4), (-1.55, -1.6, 0), (-0.9, -1.6, 0), (-0.95, -1.4), (-1.0, -0.7), (0.0, -0.6), (0.7, -0.7),
                (0.75, -1.4), (0.7, -1.6, 0), (1.25, -1.6, 0), (1.2, -1.4), (1.25, -0.6), (1.5, -0.3), (2.0, -0.15),
                (2.5, -0.05), (2.7, 0.1)])
    frill_edge = [spl([(2.15, 1.15), (1.85, 0.6), (1.65, 0.0)], closed=False), spl([(1.55, 2.2), (0.95, 2.1), (0.8, 1.6)], closed=False)]
    frill_hole = [ellipse(1.35, 1.6, 0.25, 0.18, 16, rot=0.6)]
    beak = [spl([(3.0, 0.2), (2.75, 0.25), (2.55, 0.3)], closed=False), circle(2.6, 0.6, 0.06, 6)]
    cheek = [spl([(2.3, 0.35), (2.15, 0.15), (2.25, -0.05)], closed=False)]
    far = [leg(-0.85, -0.5, -0.65, -1.52), leg(0.3, 0.65, -0.65, -1.52)]
    tail_bumps = [fringe(spl([(-1.2, 1.22), (-2.0, 0.82), (-2.9, 0.25)], closed=False), 0.12, 8)]
    dunes = [spl([(-3.6, -1.6), (-1.0, -1.65), (1.5, -1.55), (3.4, -1.65)], closed=False),
             spl([(-3.6, -2.4), (-2.2, -2.0), (-0.6, -2.4)], closed=False), spl([(0.4, -2.45), (1.8, -2.05), (3.4, -2.45)], closed=False)]
    sun = [circle(-2.6, 2.4, 0.5, 40)]
    return make("Protoceratops", [body] + frill_edge + frill_hole + beak + cheek + far + tail_bumps + dunes + sun, [eye(2.25, 0.62, 0.07)])


@design("dinosaurs_dimetrodon", T)
def dimetrodon(rng):
    body = spl([(3.25, 0.0, 0), (3.1, 0.4), (2.5, 0.65), (2.0, 0.5), (1.8, 0.55), (-1.7, 0.45), (-2.6, 0.2), (-3.8, -0.3, 0),
                (-2.6, -0.15), (-1.8, -0.2), (-1.6, -0.4), (-1.9, -0.9), (-1.6, -1.4), (-1.65, -1.55, 0), (-1.0, -1.55, 0),
                (-1.15, -1.35), (-1.3, -0.95), (-1.1, -0.5), (0.0, -0.5), (0.9, -0.45), (1.1, -0.6), (1.3, -1.0), (1.1, -1.4),
                (1.05, -1.55, 0), (1.7, -1.55, 0), (1.6, -1.35), (1.75, -0.95), (1.6, -0.5), (2.0, -0.35), (2.6, -0.2), (3.0, -0.15)])
    sail = spl([(1.8, 0.55), (1.3, 2.2), (0.3, 2.75), (-0.8, 2.4), (-1.5, 0.9), (-1.7, 0.45)], closed=False)
    ribs = []
    for k in range(1, 9):
        (x, y), _ = along(sail, k / 9)
        bx = 1.8 - 3.5 * k / 9
        ribs.append([(bx, 0.53 - 0.1 * k / 9), (x, y)])
    mouth = [teeth(3.2, 2.35, 0.02, 0.1, 6)]
    far = [leg(-0.95, -0.65, -0.5, -1.3), leg(0.7, 1.0, -0.45, -1.3)]
    ground = [[(-3.8, -1.55), (3.4, -1.55)]]
    rocks = [spl([(2.4, -1.55), (2.7, -1.15), (3.2, -1.2), (3.4, -1.55)], closed=False)]
    return make("Dimetrodon", [body, sail] + ribs + mouth + far + ground + rocks + fern(-3.4, -1.55, -3.1, 0.3, 4, 0.4),
                [eye(2.6, 0.35, 0.07)])



def teeth_along(line, h, n):
    """Saw teeth along a polyline, pointing to the right of travel."""
    out = []
    for k in range(2 * n + 1):
        (x, y), (nx, ny) = along(line, 0.02 + 0.96 * k / (2 * n))
        out.append((x - nx * h, y - ny * h) if k % 2 else (x, y))
    return out


def small_fish(x, y, s=1.0, flip=1):
    pts = [spl([(0.5, 0.0, 0), (0.2, 0.22), (-0.3, 0.15), (-0.5, 0.0, 0), (-0.3, -0.15), (0.2, -0.22)]),
           poly((-0.5, 0.0), (-0.85, 0.25), (-0.85, -0.25), closed=False)]
    return [transform(mirror_x(p) if flip < 0 else p, dx=x, dy=y, s=s) for p in pts]


def bubbles(pts):
    return [circle(x, y, r, 16) for x, y, r in pts]


# ------------------------------------------------------------------ sea reptiles and others

@design("dinosaurs_plesiosaur", T)
def plesiosaur(rng):
    body = spl([(1.0, 0.2), (0.3, 0.75), (-0.8, 0.8), (-1.8, 0.4), (-2.9, -0.1, 0), (-2.0, -0.25), (-1.0, -0.6), (0.2, -0.6), (1.0, -0.25)])
    neck = tube([(0.6, 0.0), (1.6, 0.6), (2.3, 1.5), (2.7, 2.3)], lambda t: 0.85 - 0.45 * t, cap=False)
    head = ellipse(3.05, 2.5, 0.6, 0.33, 30, rot=0.35)
    mouth = [[(3.6, 2.65), (3.0, 2.42)]]
    flips = [lens((0.6, -0.4), (1.4, -1.45), 0.3), lens((-1.3, -0.4), (-2.0, -1.3), 0.3)]
    far_flips = [lens((0.2, -0.4), (0.0, -1.5), 0.3), lens((-1.6, -0.3), (-2.4, -0.9), 0.3)]
    out = hide([body], flips + [neck + [neck[0]]]) + hide([neck], [head]) + [head] + flips + hide(far_flips, [body] + flips) + mouth
    sea = bubbles([(3.4, 3.2, 0.12), (3.6, 3.6, 0.09), (-1.5, 1.6, 0.15), (-1.2, 2.1, 0.1)])
    weed = [spl([(x, -2.8), (x + 0.25, -2.2), (x - 0.15, -1.6), (x + 0.2, -1.0)], closed=False) for x in (-3.0, -2.6, 2.6)]
    fish = small_fish(-2.4, 2.4, 0.6) + small_fish(-1.6, 2.9, 0.5) + small_fish(1.4, -2.0, 0.6, -1)
    return make("Plesiosaur", out + sea + weed + fish + [wave(-3.4, 3.8, 3.9, 0.08, 6, 100)], [eye(3.0, 2.62, 0.07)])


@design("dinosaurs_mosasaur", T)
def mosasaur(rng):
    body = spl([(-3.4, 0.6, 0), (-2.6, 0.95), (-1.8, 1.05), (-0.5, 0.95), (1.0, 0.7), (2.2, 0.35), (3.0, 0.1), (3.6, 0.9, 0), (3.5, 0.1),
                (3.8, -0.55, 0), (3.0, -0.2), (2.0, -0.3), (0.5, -0.5), (-0.8, -0.5), (-1.6, -0.35), (-2.4, -0.25), (-3.2, -0.05, 0),
                (-2.5, 0.15), (-1.9, 0.35, 0), (-2.6, 0.45)])
    upper = teeth_along(spl([(-3.3, 0.58), (-2.6, 0.47), (-2.0, 0.38)], closed=False), 0.12, 6)
    lower = teeth_along(spl([(-2.05, 0.33), (-2.5, 0.17), (-3.1, -0.02)], closed=False), 0.12, 5)
    flips = [lens((-0.9, -0.4), (-1.5, -1.3), 0.3), lens((1.5, -0.3), (1.0, -1.0), 0.3)]
    stripes = [spl([(x, 0.9 - 0.12 * max(0, x)), (x + 0.1, 0.2), (x, -0.4)], closed=False) for x in (-1.2, -0.4, 0.4, 1.2, 2.0)]
    out = hide([body], flips) + flips + hide(stripes, flips) + [upper, lower]
    fish = small_fish(-3.2, 1.9, 0.7, -1) + small_fish(-2.2, 2.6, 0.55, -1) + small_fish(1.6, 2.2, 0.5, -1)
    sea = bubbles([(-0.2, 1.8, 0.15), (0.2, 2.3, 0.1), (2.8, -1.4, 0.12)]) + [wave(-3.6, 3.8, 3.0, 0.08, 6, 100)]
    floor = [spl([(-3.6, -2.4), (-1.5, -2.1), (0.5, -2.45), (3.8, -2.2)], closed=False)]
    return make("Mosasaur Attack", out + fish + sea + floor, [eye(-1.75, 0.75, 0.08)])


@design("dinosaurs_ichthyosaur", T)
def ichthyosaur(rng):
    body = spl([(3.4, 0.2, 0), (2.4, 0.35), (1.9, 0.7), (0.5, 1.05), (0.0, 1.1), (-0.3, 1.8, 0), (-0.7, 1.0), (-1.6, 0.6), (-2.5, 0.15),
                (-3.3, 1.1, 0), (-3.0, 0.1), (-3.3, -0.9, 0), (-2.5, -0.1), (-1.5, -0.4), (0.3, -0.65), (1.7, -0.3), (2.4, 0.0),
                (3.3, 0.12)])
    ring = [circle(1.85, 0.4, 0.22, 20)]
    mouth = [[(3.35, 0.16), (2.3, 0.15)]]
    flips = [lens((1.0, -0.5), (0.4, -1.3), 0.3), lens((-1.3, -0.35), (-1.7, -0.9), 0.3)]
    out = hide([body], flips) + flips + ring + mouth
    fish = small_fish(-1.8, 2.4, 0.5) + small_fish(-1.0, 2.8, 0.5) + small_fish(-2.4, 2.9, 0.45) + small_fish(-1.6, 3.3, 0.45)
    sea = bubbles([(3.2, 1.2, 0.15), (3.5, 1.7, 0.1), (3.3, 2.1, 0.08)]) + [spl([(x, -2.8), (x + 0.25, -2.2), (x - 0.15, -1.6)], closed=False)
                                                                         for x in (-2.0, 1.6, 2.0)]
    floor = [spl([(-3.6, -2.8), (0.0, -2.6), (3.6, -2.8)], closed=False)]
    return make("Ichthyosaur", out + fish + sea + floor, [eye(1.85, 0.4, 0.1)])


@design("dinosaurs_dunkleosteus", T)
def dunkleosteus(rng):
    body = spl([(2.8, 0.4, 0), (2.2, 1.2), (1.0, 1.6), (0.0, 1.55), (-1.2, 1.1), (-2.4, 0.5), (-2.9, 0.2), (-3.8, 1.2, 0), (-3.4, 0.1),
                (-3.7, -0.8, 0), (-2.9, -0.2), (-1.5, -0.6), (0.0, -0.8), (1.5, -0.6), (2.5, -0.3), (2.7, 0.0, 0), (2.0, 0.0),
                (1.4, 0.1, 0), (2.1, 0.35)])
    plate = [spl([(0.0, 1.55), (0.25, 0.4), (0.0, -0.8)], closed=False), spl([(1.0, 1.6), (1.05, 0.7), (1.4, 0.15)], closed=False),
             spl([(1.4, 0.05), (1.0, -0.3), (0.2, -0.55)], closed=False)]
    fin = [spl([(-0.6, 1.4), (-1.0, 2.1, 0), (-1.4, 1.0)], closed=False), lens((0.4, -0.5), (-0.4, -1.4), 0.3)]
    ring = [circle(1.55, 0.95, 0.2, 18)]
    fish = small_fish(-2.4, 2.3, 0.6) + small_fish(3.2, 2.0, 0.6, -1)
    sea = bubbles([(3.2, 0.6, 0.12), (3.4, 1.0, 0.09)]) + [spl([(x, -2.6), (x + 0.25, -2.0), (x - 0.15, -1.4)], closed=False) for x in (-2.8, 2.4)]
    floor = [spl([(-3.8, -2.6), (0.0, -2.4), (3.6, -2.6)], closed=False)]
    return make("Dunkleosteus Armored Fish", [body] + plate + hide(fin[1:], [body]) + fin[:1] + ring + fish + sea + floor,
                [eye(1.55, 0.95, 0.09)])


@design("dinosaurs_mammoth", T)
def mammoth(rng):
    body = spl([(-1.9, 2.6), (-2.5, 2.3), (-2.75, 1.6), (-2.85, 0.4), (-2.75, -1.0), (-2.55, -1.5, 0), (-2.3, -1.4), (-2.35, 0.2),
                (-2.15, 0.8), (-1.7, 0.6), (-1.65, -0.4), (-1.6, -2.3), (-1.6, -2.5, 0), (-0.9, -2.5, 0), (-0.9, -2.3), (-0.85, -0.6),
                (-0.6, -0.4), (0.3, -0.5), (1.2, -0.6), (1.3, -2.2), (1.25, -2.5, 0), (1.9, -2.5, 0), (1.95, -2.3), (2.0, 0.0),
                (1.9, 1.1), (1.3, 1.6), (0.0, 2.2), (-1.2, 2.65)])
    tusk = tube(cubic((-2.3, 0.78), (-3.0, -0.5), (-4.0, -0.3), (-3.85, 0.8), 30), lambda t: 0.3 * (1 - t) + 0.06)
    tusk2 = tube(cubic((-2.1, 0.75), (-2.6, -0.2), (-3.4, -0.2), (-3.35, 0.55), 30), lambda t: 0.26 * (1 - t) + 0.06)
    hair = []
    for x, y in [(-1.6, -0.5), (-1.3, -0.5), (-0.6, -0.45), (-0.25, -0.5), (0.1, -0.52), (0.45, -0.55), (0.8, -0.58), (1.4, -0.6),
                 (1.7, -0.5), (-1.65, 0.2), (1.98, -0.3)]:
        hair.append(quad((x, y), (x + 0.12, y - 0.25), (x + 0.02, y - 0.5), 6))
    fur = [spl([(x, y), (x - 0.15, y - 0.3), (x - 0.05, y - 0.55)], closed=False) for x, y in
           [(-1.2, 2.3), (-0.5, 2.0), (0.2, 1.8), (0.9, 1.5), (-0.8, 1.3), (0.0, 1.1), (0.8, 0.8), (1.5, 0.9), (-0.3, 0.4), (0.5, 0.2)]]
    ear = [arc(-1.7, 1.75, 0.3, math.radians(60), math.radians(300), 12)]
    far = [leg(-0.85, -0.3, -0.7, -2.42), leg(0.7, 1.2, -0.7, -2.42)]
    tail = [quad((1.98, 0.6), (2.3, 0.1), (2.3, -0.3), 8), lens((2.3, -0.3), (2.35, -0.75), 0.35)]
    ground = [[(-3.9, -2.5), (3.0, -2.5)]]
    snow = []
    for x, y in [(1.8, 2.6), (2.6, 1.8), (-3.4, 2.6), (2.8, 3.0)]:
        snow += [[(x + 0.2 * math.cos(a), y + 0.2 * math.sin(a)), (x - 0.2 * math.cos(a), y - 0.2 * math.sin(a))] for a in (0.5, 1.55, 2.6)]
    tusks = [tusk] + hide([tusk2], [tusk])
    out = hide([body], [tusk, tusk2]) + tusks + hide(hair, [tusk, tusk2]) + fur + ear + hide(far, [body]) + tail + ground + snow
    return make("Woolly Mammoth", out, [eye(-2.15, 1.55, 0.08)])


@design("dinosaurs_smilodon", T)
def smilodon(rng):
    body = spl([(3.3, 0.9, 0), (3.15, 1.2), (2.7, 1.55), (2.45, 1.9, 0), (2.25, 1.62), (1.8, 1.5), (1.0, 1.65), (-0.3, 1.2), (-1.7, 1.3),
                (-2.15, 1.3), (-2.45, 1.1, 0), (-2.2, 0.95), (-2.3, 0.5), (-2.3, -0.3), (-2.1, -0.9), (-2.2, -1.75), (-2.25, -1.9, 0),
                (-1.65, -1.9, 0), (-1.75, -1.75), (-1.7, -0.9), (-1.45, -0.1), (-0.8, 0.25), (0.3, 0.0), (0.95, -0.35), (1.05, -1.75),
                (1.05, -1.9, 0), (1.8, -1.9, 0), (1.65, -1.75), (1.6, -0.7), (1.9, -0.1), (2.3, 0.45), (2.6, 0.55), (2.9, 0.6),
                (3.2, 0.75)])
    saber = spl([(2.78, 0.68), (2.85, 0.15), (2.7, -0.4, 0), (3.06, 0.15), (3.1, 0.78)], closed=False)
    mask = saber + [saber[0]]
    nose = [spl([(3.3, 0.9), (3.1, 0.95), (3.0, 0.85)], closed=False)]
    whisk = [circle(x, y, 0.05, 6) for x, y in [(2.85, 0.95), (3.0, 1.05)]]
    stripes = [spl([(x, 1.35 - 0.1 * abs(x)), (x - 0.12, 0.95), (x - 0.02, 0.6)], closed=False) for x in (-1.4, -0.8, -0.2, 0.4)]
    far = hide([leg(-1.35, -0.85, -0.3, -1.85), leg(1.45, 1.95, -0.5, -1.85)], [body])
    ear = [arc(2.42, 1.62, 0.12, 0.3, 2.8, 6)]
    toes = [[(x, -1.9), (x, -1.75)] for x in (1.3, 1.55, -2.0)]
    shoulder = [spl([(0.9, 1.2), (1.2, 0.5), (1.1, -0.3)], closed=False)]
    rocks = [spl([(2.4, -1.9), (2.7, -1.35), (3.3, -1.3), (3.6, -1.9)], closed=False), [(-3.0, -1.9), (3.7, -1.9)]]
    return make("Sabre-Toothed Cat", hide([body], [mask]) + [saber] + nose + whisk + stripes + far + ear + toes + shoulder + rocks +
                fern(-2.8, -1.9, -2.5, -0.1, 4, 0.4), [eye(2.75, 1.25, 0.08)])


@design("dinosaurs_trex_skeleton", T)
def trex_skeleton(rng):
    skull = spl([(1.75, 1.6), (1.85, 1.95), (2.6, 2.2), (3.4, 1.9), (3.7, 1.45, 0), (3.0, 1.35), (2.0, 1.3)])
    jaw = spl([(1.9, 1.15), (3.0, 1.08), (3.5, 1.05, 0), (3.0, 0.82), (2.0, 0.85), (1.8, 1.0)])
    holes = [circle(2.3, 1.85, 0.17, 16), ellipse(2.9, 1.75, 0.25, 0.14, 16), ellipse(2.5, 0.98, 0.25, 0.06, 12)]
    spine_c = spl([(1.75, 1.55), (1.3, 1.35), (0.0, 1.5), (-0.8, 1.45), (-2.0, 1.05), (-3.0, 0.6), (-3.8, 0.1)], closed=False)
    spine = sides(spine_c, lambda t: 0.22 * (1 - 0.6 * t))
    procs = []
    for k in range(1, 22):
        (x, y), (nx, ny) = along(spine_c, k / 22)
        h = 0.35 * (1 - k / 26)
        procs.append([(x + nx * 0.1, y + ny * 0.1), (x + nx * (0.1 + h), y + ny * (0.1 + h))])
    ribs = [spl([(x, y), (x + 0.25, y - 0.6), (x + 0.1, y - 1.1 + 0.1 * abs(x))], closed=False)
            for x, y in [(1.1, 1.3), (0.75, 1.35), (0.4, 1.4), (0.05, 1.4), (-0.3, 1.38)]]
    pelvis = spl([(-1.3, 1.3), (-0.3, 1.25), (-0.5, 0.75), (-0.95, 0.55), (-1.3, 0.85)])

    def bone_leg(hip, knee, ankle, ball, toe):
        out = []
        for a, b in [(hip, knee), (knee, ankle), (ankle, ball)]:
            out += sides(densify([a, b], 0.1), 0.17)
        out += [circle(knee[0], knee[1], 0.17, 12), circle(ankle[0], ankle[1], 0.14, 12), [ball, toe]]
        return out
    near = bone_leg((-0.8, 0.75), (-0.3, -0.6), (-0.75, -1.6), (-0.55, -2.25), (0.1, -2.3))
    far = bone_leg((-0.7, 0.75), (-1.2, -0.5), (-1.6, -1.45), (-1.45, -2.25), (-0.85, -2.3))
    arm = [[(1.2, 0.9), (1.45, 0.55), (1.65, 0.6)]]
    stand = [rrect(-3.0, -2.7, 2.8, -2.35, 0.1), [(-2.0, -2.35), (-2.0, 0.85)], [(1.0, -2.35), (1.0, 0.25)]]
    stand = hide(stand, [pelvis])
    return make("T-Rex Skeleton", [skull, jaw, pelvis] + holes + spine + procs + ribs + near + far + arm + stand +
                [teeth(3.6, 2.0, 1.33, 0.1, 9), teeth(3.4, 2.0, 1.05, -0.1, 8)])


@design("dinosaurs_trex_head", T)
def trex_head(rng):
    head = spl([(-3.0, -2.6, 0), (-2.6, 0.2), (-2.0, 1.5), (-1.5, 2.0), (0.0, 2.3), (0.8, 2.2), (2.6, 1.6), (3.3, 1.2), (3.3, 0.9, 0),
                (2.0, 0.75), (-0.4, 0.4, 0), (1.0, -0.4), (2.6, -0.9), (3.0, -1.0, 0), (2.8, -1.35), (1.0, -1.25), (-0.6, -1.4),
                (-1.4, -2.6, 0)], closed=False)
    upper = teeth_along(spl([(3.2, 0.9), (2.0, 0.76), (0.4, 0.5)], closed=False), 0.25, 9)
    lower = teeth_along(spl([(0.6, -0.15), (1.6, -0.55), (2.9, -0.95)], closed=False), 0.22, 8)
    tongue = [spl([(-0.1, 0.25), (0.8, 0.0), (1.6, -0.2), (2.2, -0.4)], closed=False)]
    brow = [spl([(0.2, 1.75), (0.75, 2.0), (1.3, 1.8)], closed=False)]
    nostril = [ellipse(2.9, 1.35, 0.14, 0.08, 12, rot=-0.3)]
    scales = [arc(x, y, 0.18, math.radians(200), math.radians(340), 6) for x, y in [(-0.8, 1.6), (-1.3, 1.1), (-0.5, 1.15), (1.8, 1.45),
                                                                                (-1.6, 0.4), (0.2, -0.9), (1.4, -1.0)]]
    folds = [spl([(-2.2, -0.6), (-1.6, -0.8), (-1.0, -1.2)], closed=False), spl([(-2.4, -1.4), (-1.8, -1.6), (-1.3, -2.0)], closed=False)]
    roar = [[(3.5, 0.6), (4.0, 0.8)], [(3.5, 0.2), (4.1, 0.2)], [(3.5, -0.2), (4.0, -0.4)]]
    return make("Roaring T-Rex Head", [head, upper, lower] + tongue + brow + nostril + scales + folds + roar, [eye(0.8, 1.55, 0.12)])



# ------------------------------------------------------------------ babies, fossils and scenes

@design("dinosaurs_hatching_baby", T)
def hatching_baby(rng):
    rim = [(-1.7, -0.3), (-1.3, 0.1), (-1.0, -0.25), (-0.6, 0.15), (-0.2, -0.2), (0.2, 0.15), (0.6, -0.2), (1.0, 0.1), (1.35, -0.25),
           (1.7, -0.3)]
    shell = chain(rim, spl([(1.7, -0.3), (1.55, -1.4), (0.8, -2.3), (0.0, -2.5), (-0.8, -2.3), (-1.55, -1.4), (-1.7, -0.3)], closed=False))
    neck = tube([(0.0, -0.8), (0.1, 0.4), (0.45, 1.2)], 0.75, cap=False)
    head = spl([(0.2, 1.0), (-0.3, 1.6), (-0.1, 2.35), (0.6, 2.6), (1.5, 2.45), (2.1, 1.95), (2.0, 1.4), (1.2, 1.1)])
    cap = chain(spl([(-0.55, 2.0), (-0.4, 2.7), (0.3, 3.2), (1.2, 3.1), (1.7, 2.6)], closed=False),
                [(1.7, 2.6), (1.35, 2.35), (1.1, 2.6), (0.8, 2.3), (0.45, 2.6), (0.15, 2.3), (-0.2, 2.45), (-0.55, 2.0)])
    smile = [spl([(1.2, 1.55), (1.6, 1.4), (1.95, 1.55)], closed=False)]
    nostril = [circle(1.85, 1.85, 0.06, 6)]
    eye_ring = [circle(0.75, 1.85, 0.28, 24)]
    hands = [spl([(-0.7, 0.4), (-0.85, 0.05), (-0.6, 0.0)], closed=False), spl([(0.9, 0.35), (1.1, 0.05), (0.85, -0.05)], closed=False)]
    spots = [circle(x, y, r, 18) for x, y, r in [(-0.9, -1.2, 0.3), (0.7, -1.5, 0.25), (0.0, -1.9, 0.2), (1.1, -0.7, 0.18)]]
    bits = [poly((-2.8, -2.5), (-2.4, -2.1), (-2.1, -2.5), closed=False), poly((2.1, -2.5), (2.5, -2.0), (2.9, -2.5), closed=False)]
    ground = [[(-3.2, -2.5), (-0.8, -2.5)], [(0.8, -2.5), (3.2, -2.5)]]
    sh = shell + [shell[0]]
    front = hide([head], [cap]) + [cap]
    return make("Baby Dinosaur Hatching", [shell] + hide(neck_sides(neck), [sh, head]) + front + smile + nostril + eye_ring +
                hide(hands, []) + spots + bits + ground + fern(-3.0, -2.5, -2.6, -0.4, 4, 0.4), [eye(0.8, 1.82, 0.13)])


def neck_sides(band):
    n = len(band) // 2
    return [band[:n], band[n:]]


@design("dinosaurs_baby_trex", T)
def baby_trex(rng):
    head = spl([(-0.8, 1.6), (0.3, 2.35), (1.6, 2.2), (2.35, 1.4), (2.3, 0.5), (1.5, 0.1), (0.2, 0.1), (-0.75, 0.6)])
    body = spl([(-0.62, 0.45), (-1.15, -0.4), (-1.05, -1.5), (-0.5, -1.95), (0.4, -1.95), (0.85, -1.2), (0.75, 0.12)], closed=False)
    tail = spl([(-1.1, -0.65), (-2.0, -1.2), (-2.8, -1.75, 0), (-1.9, -1.65), (-1.0, -1.5)], closed=False)
    feet = [ellipse(-0.55, -2.05, 0.42, 0.2, 24), ellipse(0.5, -2.05, 0.42, 0.2, 24)]
    arm = [spl([(0.8, -0.45), (1.1, -0.35), (1.15, -0.55)], closed=False)]
    belly = [spl([(0.6, -0.1), (0.2, -0.8), (0.3, -1.6)], closed=False)]
    smile = [spl([(1.0, 0.65), (1.6, 0.5), (2.15, 0.75)], closed=False)]
    fangs = [poly((1.3, 0.6), (1.38, 0.38), (1.46, 0.57), closed=False), poly((1.75, 0.55), (1.83, 0.33), (1.9, 0.58), closed=False)]
    eye_ring = [circle(1.15, 1.45, 0.38, 30)]
    blush = [ellipse(1.75, 1.0, 0.25, 0.13, 16)]
    nostril = [circle(2.15, 1.4, 0.06, 6)]
    spikes = [poly((x - 0.18, y), (x, y + 0.3), (x + 0.18, y), closed=False) for x, y in [(-0.3, 2.0), (0.4, 2.33), (1.1, 2.33)]]
    spikes = hide(spikes, [head])
    bodies = hide([body, tail] + feet, [head]) + [head]
    return make("Cute Baby T-Rex", bodies + hide(feet[:0], []) + arm + belly + smile + fangs + eye_ring + blush + nostril + spikes +
                [[(-3.0, -2.25), (3.0, -2.25)]] + fern(2.6, -2.25, 2.9, -0.5, 4, 0.4), [eye(1.2, 1.42, 0.2)])


def _triceratops(cx, cy, s):
    body = spl([(3.7, -0.35, 0), (3.55, 0.1), (3.2, 0.45), (2.75, 0.85), (2.5, 1.25), (2.3, 1.85), (1.85, 2.2), (1.35, 2.0), (1.1, 1.5),
                (0.9, 1.35), (0.0, 1.4), (-1.0, 1.4), (-1.9, 1.15), (-2.7, 0.6), (-3.5, 0.0, 0), (-2.7, 0.05), (-2.3, -0.2),
                (-2.3, -0.6), (-2.2, -1.6), (-2.25, -1.8, 0), (-1.55, -1.8, 0), (-1.55, -1.6), (-1.6, -0.75), (-0.4, -0.65),
                (0.6, -0.6), (0.85, -0.75), (0.85, -1.6), (0.8, -1.8, 0), (1.5, -1.8, 0), (1.5, -1.6), (1.55, -0.6), (1.85, -0.45),
                (2.3, -0.55), (3.0, -0.55), (3.5, -0.45)])
    horns = [tube(cubic((2.75, 0.85), (3.1, 1.2), (3.5, 1.5), (3.95, 1.75), 16), lambda t: 0.22 * (1 - t) + 0.03),
             tube(cubic((3.2, 0.45), (3.3, 0.6), (3.4, 0.72), (3.5, 0.88), 8), lambda t: 0.16 * (1 - t) + 0.03)]
    horn2 = hide([tube(cubic((2.55, 0.95), (2.85, 1.35), (3.2, 1.7), (3.6, 2.0), 16), lambda t: 0.2 * (1 - t) + 0.03)], [horns[0], body])
    frill_edge = [spl([(2.5, 1.25), (2.05, 0.5), (2.05, -0.4)], closed=False)]
    bumps = [circle(x, y, 0.1, 8) for x, y in [(2.1, 1.75), (1.75, 1.95), (1.4, 1.75)]]
    far = hide([leg(-1.25, -0.75, -0.6, -1.75), leg(1.25, 1.75, -0.6, -1.75)], [body])
    mouth = [spl([(3.7, -0.35), (3.35, -0.3), (3.05, -0.2)], closed=False)]
    parts = hide([body], horns) + horns + horn2 + frill_edge + bumps + far + mouth
    return [transform(p, dx=cx, dy=cy, s=s) for p in parts], [transform(body, dx=cx, dy=cy, s=s)]


@design("dinosaurs_triceratops_family", T)
def triceratops_family(rng):
    mom, mmask = _triceratops(0.3, 0.0, 1.0)
    baby, bmask = _triceratops(-2.75, -0.99, 0.45)
    ground = [[(-4.5, -1.8), (4.4, -1.8)]]
    return make("Triceratops Mother and Baby", hide(mom, bmask) + baby + ground,
                [eye(0.3 + 2.8, 0.5, 0.08), eye(-2.75 + 2.8 * 0.45, -0.99 + 0.5 * 0.45, 0.05)])


@design("dinosaurs_ammonite", T)
def ammonite(rng):
    k = math.log(1 / 0.56) / TAU
    th1 = 5.0 * math.pi

    def P(t, rad=None):
        r = 2.4 * math.exp(-k * t) if rad is None else rad
        return (r * math.cos(-t), r * math.sin(-t) - 0.1)
    outer = [P(i * th1 / 400) for i in range(401)]
    ribs = []
    t = 0.0
    while t + TAU <= th1 + 1e-6:
        a, b = P(t), P(t + TAU)
        m = P(t + 0.18, 2.4 * math.exp(-k * t) * 0.72 + 2.4 * math.exp(-k * (t + TAU)) * 0.28)
        ribs.append(quad(a, m, b, 8))
        t += 0.32
    centre = [circle(*P(th1 + 0.3, 0.0), 0.15, 12)]
    slab = [spl([(-3.2, -2.4), (-3.4, 0.4), (-2.6, 2.7), (0.4, 3.0), (3.0, 2.4), (3.4, -0.4), (2.8, -2.8), (-0.4, -3.1)])]
    cracks = [poly((2.9, 1.9), (2.5, 1.5), (2.7, 1.1), closed=False), poly((-2.9, -1.6), (-2.5, -1.9), (-2.6, -2.4), closed=False)]
    return make("Ammonite Fossil", [outer] + ribs + centre + slab + cracks)


@design("dinosaurs_trilobite", T)
def trilobite(rng):
    head = spl([(-2.0, 0.6, 0), (-1.9, 1.5), (-1.2, 2.35), (0, 2.65), (1.2, 2.35), (1.9, 1.5), (2.0, 0.6, 0), (1.55, 1.15), (-1.55, 1.15)])
    glabella = [spl([(-0.4, 1.2), (-0.5, 1.9), (0, 2.4), (0.5, 1.9), (0.4, 1.2)], closed=False)]
    eyes_ = [lens((-1.2, 1.4), (-0.7, 1.95), 0.3), lens((1.2, 1.4), (0.7, 1.95), 0.3)]
    segs = []
    left = [(-1.55, 1.15)]
    n = 9
    for k in range(n):
        y0 = 1.15 - 0.3 * k
        w = 1.55 - 0.07 * k
        y1 = y0 - 0.3
        left += [(-w - 0.2, y0 - 0.25), (-w + 0.05, y1)]
        segs.append([(-w + 0.05, y1), (w - 0.05, y1)])
    yb = 1.15 - 0.3 * n
    tail = spl([(-0.95, yb), (-0.85, yb - 0.6), (0, yb - 0.95), (0.85, yb - 0.6), (0.95, yb)], closed=False)
    outline = chain(left, [(x, y) for x, y in left[::-1]][:0])
    sides_ = [poly(*left, closed=False), poly(*mirror_x(left), closed=False)]
    axis = [spl([(-0.45, 1.15), (-0.4, -0.5), (-0.3, yb - 0.4)], closed=False), spl([(0.45, 1.15), (0.4, -0.5), (0.3, yb - 0.4)], closed=False)]
    pyg = [arc(0, yb, 0.55, math.radians(200), math.radians(340), 10)]
    rock = [spl([(-3.0, -3.2), (-3.3, 0.0), (-2.6, 3.0), (2.6, 3.2), (3.3, 0.2), (2.8, -3.2)])]
    return make("Trilobite Fossil", [head, tail] + glabella + eyes_ + hide(segs, []) + sides_ + hide(axis, []) + pyg + rock + [[(-0.9, yb), (-1.15, yb + 0.05)], [(0.9, yb), (1.15, yb + 0.05)]][:0])


@design("dinosaurs_amber", T)
def amber(rng):
    gem = spl([(0, 2.8), (1.4, 2.4), (2.4, 1.0), (2.5, -0.8), (1.6, -2.3), (0, -2.8), (-1.6, -2.3), (-2.5, -0.8), (-2.4, 1.0), (-1.4, 2.4)])
    shine = [spl([(-1.7, 1.4), (-1.1, 2.0), (-0.5, 2.25)], closed=False), spl([(1.9, -1.0), (1.6, -1.6), (1.1, -2.0)], closed=False)]
    body = [ellipse(0.1, -0.2, 0.28, 0.5, 24, rot=0.5), circle(-0.25, 0.4, 0.2, 16), ellipse(0.55, -1.15, 0.22, 0.65, 24, rot=0.55)]
    nose = [[(-0.4, 0.55), (-1.1, 1.3)]]
    wings = [lens((0.1, 0.0), (1.4, 1.0), 0.25), lens((0.0, 0.05), (-0.4, 1.6), 0.25)]
    legs = [[(x0, y0), (x1, y1), (x2, y2)] for x0, y0, x1, y1, x2, y2 in [(-0.1, -0.3), (-0.9, -0.2), (-1.5, -0.7)][:0] or
            [(-0.05, -0.35, -0.8, -0.3, -1.4, -0.9), (0.05, -0.45, -0.4, -1.0, -0.8, -1.8), (0.2, -0.5, 0.1, -1.3, -0.1, -2.1),
             (0.3, -0.1, 1.0, -0.3, 1.6, -0.9), (0.35, -0.25, 1.1, -0.8, 1.4, -1.6), (-0.15, -0.2, -0.9, 0.25, -1.6, 0.0)]]
    feelers = [[(-0.35, 0.55), (-0.7, 1.0)], [(-0.2, 0.6), (-0.3, 1.1)]][:0]
    rings = [quad((0.3, y), (0.55, y - 0.08), (0.8, y + 0.05), 4) for y in (-0.9, -1.2, -1.5)]
    bub = [circle(x, y, r, 12) for x, y, r in [(1.4, 1.6, 0.15), (-1.6, -1.6, 0.2), (1.8, 0.2, 0.12), (-1.2, -2.0, 0.1)]]
    return make("Mosquito in Amber", [gem] + shine + hide(body + wings, []) + nose + legs + rings + bub, [])


@design("dinosaurs_dig_site", T)
def dig_site(rng):
    surface = [[(-3.6, 1.0), (3.6, 1.0)]]
    layers = [spl([(-3.6, -0.3), (-1.5, -0.1), (1.0, -0.4), (3.6, -0.2)], closed=False),
              spl([(-3.6, -2.0), (-1.0, -1.8), (1.5, -2.1), (3.6, -1.9)], closed=False)]
    skull = spl([(-1.3, -0.9), (-0.9, -0.55), (-0.1, -0.5), (0.5, -0.8), (0.55, -1.1, 0), (-0.2, -1.2), (-1.25, -1.2)])
    jaw = spl([(-1.1, -1.35), (-0.3, -1.4), (0.35, -1.25, 0), (-0.3, -1.6), (-1.1, -1.55)])
    holes = [circle(-0.75, -0.8, 0.13, 12), ellipse(-0.2, -0.82, 0.2, 0.1, 12)]
    spine = [circle(0.75 + 0.36 * k, -1.0 - 0.06 * k, 0.15, 12) for k in range(6)]
    ribs = [arc(0.95 + 0.36 * k, -1.35 - 0.06 * k, 0.3, math.radians(200), math.radians(340), 6) for k in range(4)]
    bone = [spl([(-3.0, -1.0), (-2.85, -0.85), (-2.65, -1.0), (-1.85, -1.1), (-1.65, -0.95), (-1.5, -1.15), (-1.7, -1.3), (-1.85, -1.2),
                 (-2.65, -1.15), (-2.85, -1.3)])]
    rocks = [spl([(x, y), (x + 0.3, y + 0.2), (x + 0.6, y), (x + 0.4, y - 0.2), (x + 0.1, y - 0.2)]) for x, y in [(2.4, -2.6), (-2.6, -2.6), (2.6, -0.8)]]
    shovel = [[(-2.3, 3.2), (-2.0, 1.4)], rrect(-2.45, 3.1, -2.1, 3.35, 0.08), spl([(-2.3, 1.45), (-1.7, 1.35), (-1.75, 1.0), (-2.15, 0.65, 0),
                                                                                   (-2.4, 1.1)], closed=False)]
    shovel = [shovel[0], shovel[1], spl([(-2.35, 1.45), (-1.7, 1.38), (-1.85, 0.9), (-2.15, 0.7, 0), (-2.4, 1.05)])]
    bucket = [poly((1.4, 1.0), (1.25, 2.1), (2.35, 2.1), (2.2, 1.0)), spl([(1.25, 2.1), (1.8, 2.8), (2.35, 2.1)], closed=False)]
    brush = [rrect(2.7, 1.0, 3.5, 1.2, 0.08), [(2.75, 1.2), (2.75, 1.45)], [(2.95, 1.2), (2.95, 1.45)], [(3.15, 1.2), (3.15, 1.45)]]
    hat = [ellipse(-0.3, 1.1, 0.8, 0.15, 30), spl([(-0.75, 1.15), (-0.7, 1.6), (-0.3, 1.8), (0.1, 1.6), (0.15, 1.15)], closed=False)]
    sun = [circle(2.8, 3.0, 0.45, 30)]
    return make("Paleontologist Dig Site", surface + layers + [skull, jaw] + holes + spine + ribs + bone + rocks + shovel + bucket + brush +
                hide([hat[0]], [hat[0][:0] or [(-0.75, 1.15), (-0.7, 1.6), (-0.3, 1.8), (0.1, 1.6), (0.15, 1.15)]]) + hat[1:] + sun)


@design("dinosaurs_prehistoric_plants", T)
def prehistoric_plants(rng):
    trunk = [spl([(-2.6, -2.6), (-2.5, -1.4), (-2.3, -0.4)], closed=False), spl([(-1.8, -2.6), (-1.9, -1.4), (-2.0, -0.4)], closed=False)]
    scales = [arc(-2.15, y, 0.25, math.radians(200), math.radians(340), 6) for y in (-2.2, -1.8, -1.4, -1.0, -0.6)]
    fronds = []
    for a in (10, 40, 70, 110, 140, 170):
        ex, ey = -2.15 + 1.7 * math.cos(math.radians(a)), -0.5 + 1.0 * math.sin(math.radians(a))
        st = spl([(-2.15, -0.35), (-2.15 + 0.8 * math.cos(math.radians(a)), -0.35 + 1.0 * math.sin(math.radians(a)) + 0.35), (ex, ey)],
                 closed=False)
        fronds.append(st)
        for k in range(4, len(st) - 1, 5):
            x, y = st[k]
            fronds.append([(x, y), (x, y - 0.3)])
    tf = [spl([(1.6, -2.6), (1.7, 0.0), (1.55, 2.0)], closed=False), spl([(2.0, -2.6), (2.05, 0.0), (1.85, 2.0)], closed=False)]
    tf_fronds = []
    for ex, ey in [(3.4, 1.4), (3.0, 3.0), (0.1, 1.5), (0.6, 3.0), (1.7, 3.5)]:
        tf_fronds += [spl([(1.7, 2.0), ((1.7 + ex) / 2, max(2.0, ey) + 0.4), (ex, ey)], closed=False)]
    leaflets = []
    for st in tf_fronds:
        for k in range(3, len(st) - 2, 5):
            x, y = st[k]
            leaflets.append([(x, y), (x, y - 0.35)])
    horsetails = []
    for x, h in [(-0.6, 1.4), (-0.2, 1.9), (0.3, 1.2)]:
        horsetails.append([(x, -2.6), (x, -2.6 + h)])
        horsetails += [[(x - 0.18, y), (x + 0.18, y)] for y in [-2.6 + h * f for f in (0.3, 0.55, 0.8)]]
        horsetails.append(lens((x, -2.6 + h), (x, -2.6 + h + 0.4), 0.3))
    ground = [[(-3.6, -2.6), (3.6, -2.6)]]
    return make("Prehistoric Plants", trunk + scales + fronds + tf + tf_fronds + leaflets + horsetails + ground)



@design("dinosaurs_meteor", T)
def meteor(rng):
    rock = [circle(1.3, 1.3, 0.75, 60), circle(1.1, 1.45, 0.2, 14), circle(1.55, 1.05, 0.16, 12), circle(1.0, 0.9, 0.12, 10)]
    trail = [scallop([(1.83, 0.77), (2.9, 1.7), (4.0, 2.4)], 0.18, 7), scallop([(0.77, 1.83), (1.7, 2.9), (2.4, 4.0)], -0.18, 7),
             spl([(2.0, 1.6), (2.7, 2.4), (3.6, 3.3)], closed=False), spl([(1.6, 2.0), (2.4, 2.7), (3.1, 3.7)], closed=False)]
    flames = []
    small = [circle(-2.4, 3.2, 0.2, 16), [(-2.25, 3.35), (-1.7, 3.9)], circle(-0.3, 3.6, 0.15, 12), [(-0.18, 3.72), (0.2, 4.1)]]
    hills = [spl([(-3.8, -1.0), (-2.4, -0.4), (-1.2, -0.9), (0.2, -0.5), (1.6, -1.1), (3.0, -0.6), (4.0, -0.9)], closed=False)]
    volcano = [poly((-3.6, -0.6), (-2.7, 1.0), (-2.1, 1.0), (-1.3, -0.8), closed=False), circle(-2.4, 1.5, 0.35, 20), circle(-2.0, 2.0, 0.4, 20)]
    brach = spl([(2.6, 3.05, 0), (2.2, 3.4), (1.95, 3.45), (1.75, 3.2), (1.4, 2.2), (0.9, 1.0), (0.0, 0.4), (-1.2, 0.0), (-2.4, -0.4),
                 (-3.5, -0.6, 0), (-2.4, -0.8), (-1.6, -0.75), (-1.5, -1.0), (-1.45, -2.4), (-1.5, -2.6, 0), (-0.85, -2.6, 0),
                 (-0.9, -2.4), (-0.95, -1.3), (-0.2, -1.15), (0.4, -1.0), (0.45, -1.3), (0.5, -2.4), (0.45, -2.6, 0), (1.1, -2.6, 0),
                 (1.05, -2.4), (1.05, -1.0), (1.3, -0.2), (1.5, 0.8), (1.85, 2.0), (2.15, 2.85), (2.4, 2.9)], res=18)
    dino = [transform(brach, dx=-0.6, dy=-1.6, s=0.5)]
    ground = [[(-3.8, -2.9), (4.0, -2.9)]]
    ptero = [spl([(x - 0.35, y + 0.05), (x - 0.15, y + 0.15), (x, y, 0), (x + 0.15, y + 0.15), (x + 0.35, y + 0.05)], closed=False)
             for x, y in [(-1.0, 2.2), (-0.4, 2.6)]]
    return make("Meteor Strike", rock + trail + flames + small + hide(hills, [dino[0]]) + volcano + dino + ground + ptero +
                fern(3.4, -2.9, 3.7, -1.2, 4, 0.4))


@design("dinosaurs_meganeura", T)
def meganeura(rng):
    abdomen = tube([(0, 0.55), (0, -1.0), (0.05, -2.2), (0.15, -3.1)], lambda t: 0.38 - 0.18 * t)
    rings = [[(-0.17 + 0.01 * k, 0.2 - 0.38 * k), (0.17 - 0.01 * k + 0.01 * k, 0.2 - 0.38 * k)] for k in range(8)]
    thorax = ellipse(0, 0.95, 0.38, 0.5, 30)
    head = circle(0, 1.68, 0.26, 20)
    eyes_ = [circle(-0.28, 1.82, 0.2, 16), circle(0.28, 1.82, 0.2, 16)]
    wing_r = [lens((0.3, 1.1), (3.5, 1.7), 0.12), lens((0.3, 0.65), (3.3, -0.35), 0.13)]
    veins = [[(0.5, 1.15), (3.2, 1.65)], [(0.5, 0.6), (3.0, -0.25)]] + \
            [[(x, 1.15 + (x - 0.5) * 0.19 - 0.05), (x + 0.15, 1.15 + (x - 0.5) * 0.19 + 0.25)] for x in (1.2, 1.9, 2.6)] + \
            [[(x, 0.6 - (x - 0.5) * 0.34 + 0.05), (x + 0.15, 0.6 - (x - 0.5) * 0.34 - 0.27)] for x in (1.2, 1.9, 2.6)]
    right = wing_r + veins
    fronds = fern(-3.6, -3.0, -2.4, -1.0, 5, 0.45) + fern(3.6, -3.0, 2.4, -1.2, 5, 0.45, -1)
    wings = hide(right + mirror(right), [thorax])
    return make("Giant Dragonfly Meganeura", [thorax, head] + hide([abdomen], [thorax]) + hide(rings, []) + hide(eyes_, [head])[:0] + eyes_ + wings + fronds,
                [eye(-0.28, 1.82, 0.08), eye(0.28, 1.82, 0.08)])


@design("dinosaurs_coelacanth", T)
def coelacanth(rng):
    body = spl([(3.0, 0.1, 0), (2.4, 0.8), (1.5, 1.15), (0.2, 1.25), (-1.4, 1.0), (-2.4, 0.55), (-3.4, 1.4, 0), (-3.05, 0.35),
                (-3.7, 0.05, 0), (-3.05, -0.25), (-3.4, -1.3, 0), (-2.4, -0.5), (-1.0, -1.0), (1.0, -1.0), (2.3, -0.5), (3.0, -0.1, 0)])
    fins = [spl([(0.3, 1.24), (-0.1, 2.0, 0), (-0.5, 1.2)], closed=False),
            spl([(-1.3, 1.02), (-1.5, 1.3), (-1.85, 1.75, 0), (-2.0, 0.75)], closed=False),
            lens((1.2, -0.5), (0.4, -1.6), 0.3), lens((-0.3, -0.95), (-0.9, -1.75), 0.3), lens((-1.7, -0.75), (-2.2, -1.4), 0.3)]
    stalks = [[(1.2, -0.5), (0.85, -1.0)], [(-0.3, -0.95), (-0.55, -1.3)]]
    gill = [spl([(1.9, 0.85), (1.6, 0.0), (1.85, -0.75)], closed=False)]
    mouth = [[(3.0, 0.0), (2.5, -0.1)]]
    blotch = [ellipse(x, y, 0.16, 0.11, 12) for x, y in [(0.8, 0.6), (0.0, 0.2), (-0.8, 0.6), (-0.4, -0.4), (0.6, -0.3), (-1.6, 0.1)]]
    sea = bubbles([(3.3, 0.6, 0.12), (3.5, 1.0, 0.09), (3.4, 1.4, 0.07)]) + \
        [spl([(x, -2.6), (x + 0.25, -2.0), (x - 0.15, -1.4)], closed=False) for x in (-2.6, 2.4, 2.8)]
    rocks = [spl([(-3.6, -2.6), (-3.2, -2.0), (-2.2, -2.1), (-1.8, -2.6)], closed=False), [(-3.8, -2.6), (3.6, -2.6)]]
    return make("Coelacanth", hide([body], fins[2:]) + fins + stalks + gill + mouth + blotch + sea + rocks, [eye(2.25, 0.4, 0.1)])


@design("dinosaurs_quetzalcoatlus", T)
def quetzalcoatlus(rng):
    body = ellipse(-0.6, 0.55, 0.95, 0.55, 50, rot=0.15)
    neck = tube([(0.15, 0.85), (0.9, 1.7), (1.55, 2.45)], lambda t: 0.42 - 0.12 * t, cap=False)
    head = spl([(1.35, 2.35), (1.5, 2.75), (1.85, 3.0), (2.15, 2.75), (3.8, 1.25, 0), (2.0, 2.25), (1.65, 2.15)])
    arm = tube([(0.15, 0.6), (0.5, -0.4), (0.95, -1.2), (1.05, -1.75)], lambda t: 0.36 - 0.12 * t)
    wing = lens((0.75, -0.85), (-0.7, 1.35), 0.13)
    far_arm = tube([(-0.1, 0.4), (0.0, -0.6), (0.3, -1.3), (0.35, -1.75)], lambda t: 0.3 - 0.1 * t)
    hind = tube([(-1.2, 0.2), (-1.5, -0.6), (-1.35, -1.6)], lambda t: 0.3 - 0.1 * t)
    far_hind = tube([(-0.9, 0.2), (-0.95, -0.7), (-0.75, -1.6)], lambda t: 0.26 - 0.08 * t)
    feet = [[(-1.55, -1.75), (-1.05, -1.75)], [(-0.95, -1.75), (-0.5, -1.75)], [(0.85, -1.85), (1.35, -1.85)], [(0.15, -1.85), (0.6, -1.85)]]
    mouth = [[(3.75, 1.28), (2.0, 2.4)]]
    front = [head, arm, wing, hind]
    out = [head] + hide([neck], [head]) + hide([wing], [arm]) + [arm] + hide([body], [arm, wing, hind, neck + [neck[0]]]) + [hind] + \
        hide([far_arm, far_hind], [body, arm, wing, hind]) + feet + mouth
    ground = [[(-3.4, -1.85), (3.8, -1.85)]]
    return make("Quetzalcoatlus", out + ground + fern(-3.0, -1.85, -2.6, 0.3, 5, 0.45) + fern(3.0, -1.85, 3.3, -0.4, 4, 0.4),
                [eye(1.85, 2.65, 0.07)])


@design("dinosaurs_footprint_trail", T)
def footprint_trail(rng):
    def theropod(x, y, a):
        shape = spl([(0, -0.5), (0.3, -0.25), (0.72, 0.45, 0), (0.22, 0.22), (0.0, 1.0, 0), (-0.22, 0.22), (-0.72, 0.45, 0), (-0.3, -0.25)])
        return [transform(shape, dx=x, dy=y, s=0.75, rot=a)]

    def sauropod(x, y):
        return [ellipse(x, y, 0.45, 0.38, 30)] + [arc(x + dx, y + 0.42, 0.12, 0, math.pi, 6) for dx in (-0.25, 0.0, 0.25)]
    prints = []
    path = [(-2.6, -2.6, -0.5), (-1.6, -1.6, -0.2), (-1.2, -0.3, -0.5), (-0.2, 0.6, -0.2), (0.1, 1.9, -0.5), (1.1, 2.8, -0.2)]
    for k, (x, y, a) in enumerate(path):
        prints += theropod(x + (0.35 if k % 2 else -0.35), y, a)
    for x, y in [(1.6, -2.6), (2.6, -1.9), (1.9, -0.9), (2.9, -0.1), (2.2, 0.9)]:
        prints += sauropod(x, y)
    puddles = [spl([(-3.4, 1.0), (-2.6, 1.5), (-1.8, 1.2), (-2.2, 0.6), (-3.0, 0.5)]), spl([(2.6, 2.6), (3.2, 3.0), (3.7, 2.6), (3.2, 2.2)])]
    ripples = [spl([(-3.0, 1.0), (-2.6, 1.1), (-2.2, 0.95)], closed=False)]
    cracks = [poly((-3.6, -1.0), (-3.1, -1.3), (-2.9, -0.9), closed=False), poly((0.4, -2.9), (0.7, -2.5), (1.1, -2.7), closed=False)]
    return make("Dinosaur Footprint Trail", prints + puddles + ripples + cracks + fern(-3.6, 2.0, -2.8, 3.6, 4, 0.4))



@design("dinosaurs_psittacosaurus", T)
def psittacosaurus(rng):
    body = spl([(3.0, 1.25, 0), (2.95, 1.55), (2.5, 1.9), (2.05, 1.75), (1.6, 1.35), (0.5, 1.1), (-0.5, 1.15), (-1.8, 1.0), (-3.2, 0.7),
                (-3.7, 0.6, 0), (-3.1, 0.45), (-1.8, 0.55), (-1.1, 0.35), (0.0, 0.0), (0.8, 0.15), (1.3, 0.45), (1.8, 0.9),
                (2.0, 0.75, 0), (2.25, 1.0), (2.6, 1.0), (2.85, 1.1)])
    near, nm = biped_leg((-0.45, 0.5), (0.05, -0.65), (-0.4, -1.55), (-0.2, -2.25), 1, 0.6, 0.36)
    far, fm = biped_leg((-0.3, 0.5), (0.5, -0.5), (0.45, -1.45), (0.8, -2.25), 1, 0.55, 0.32)
    quills = []
    for k in range(9):
        (x, y), (nx, ny) = along(spl([(-1.0, 1.12), (-1.8, 1.0), (-2.8, 0.78)], closed=False), 0.05 + 0.9 * k / 8)
        quills.append([(x, y), (x - nx * 0.45 - 0.15, y - ny * 0.45)])
    beak = [spl([(3.0, 1.25), (2.75, 1.3), (2.55, 1.2)], closed=False)]
    arm = tube([(1.0, 0.4), (1.25, -0.1), (1.6, -0.2)], 0.2)
    hand = [[(1.65, -0.13), (1.85, -0.1)], [(1.65, -0.24), (1.8, -0.4)]]
    spots_ = [circle(x, y, 0.12, 10) for x, y in [(0.3, 0.8), (-0.4, 0.75), (0.9, 0.85), (-1.2, 0.75)]]
    ground = [[(-3.7, -2.47), (3.4, -2.47)]]
    out = hide([body], [arm] + nm) + hide(spots_, nm + [arm]) + hide(far, [body] + nm) + near + [arm] + hand + quills + beak
    return make("Psittacosaurus", out + ground + fern(-3.3, -2.47, -2.9, -0.7, 4, 0.4) + fern(3.0, -2.47, 3.3, -0.6, 4, 0.4),
                [eye(2.4, 1.55, 0.07)])


@design("dinosaurs_egg_nest", T)
def egg_nest(rng):
    nest = [spl([(-3.0, -0.6), (-2.6, -1.9), (-1.2, -2.6), (1.2, -2.6), (2.6, -1.9), (3.0, -0.6)], closed=False),
            spl([(-3.0, -0.6), (-1.5, -1.0), (0.0, -1.1), (1.5, -1.0), (3.0, -0.6)], closed=False)]
    weave = [quad((x, -1.15 + 0.02 * abs(x)), (x + 0.4, -1.9 + 0.1 * abs(x)), (x + 0.1, -2.4 + 0.1 * abs(x)), 8) for x in (-2.2, -1.2, -0.2, 0.8, 1.8)]
    eggs = [(-1.7, -0.3, 0.6, 0.85, 0.25), (0.0, 0.0, 0.65, 0.95, 0.0), (1.7, -0.3, 0.6, 0.85, -0.25), (-0.85, -0.65, 0.55, 0.75, 0.1),
            (0.9, -0.65, 0.55, 0.75, -0.1)]
    shapes = [ellipse(x, y, rx, ry, 60, rot=r) for x, y, rx, ry, r in eggs]
    out = []
    for k, sh in enumerate(shapes):
        out += hide([sh], shapes[k + 1:])
    out = hide(out, [nest[0][:0] + nest[1] + nest[1][:1]][:0])
    spots_ = hide([circle(x, y, r, 14) for x, y, r in [(-1.9, 0.0, 0.18), (-1.5, 0.3, 0.12), (0.2, 0.5, 0.18), (-0.2, 0.2, 0.12),
                                                     (1.9, 0.1, 0.16), (1.5, -0.1, 0.1)]], shapes[3:])
    crack = [poly((-0.5, 0.25), (-0.25, 0.4), (-0.05, 0.15), (0.2, 0.4), (0.45, 0.2), (0.62, 0.35), closed=False)]
    plants = fern(-3.8, -2.6, -3.5, 1.2, 5, 0.45) + fern(3.8, -2.6, 3.5, 1.2, 5, 0.45, -1)
    sun = [circle(2.4, 2.6, 0.5, 40)]
    return make("Dinosaur Egg Nest", hide(nest + weave, shapes) + out + spots_ + crack + plants + sun)
