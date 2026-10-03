"""Airplanes & Flight niche, part 2 (pictures 9-60)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "aviation"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ------------------------------------------------------------------ helpers

def cloud(cx, cy, s=1.0, bumps=None):
    """Puffy cloud with a flat bottom (upper envelope of a few circles)."""
    bumps = bumps or [(-0.85, 0.0, 0.4), (-0.35, 0.2, 0.55), (0.3, 0.25, 0.6), (0.85, 0.0, 0.4)]
    bs = [(cx + bx * s, cy + by * s, r * s) for bx, by, r in bumps]
    x0 = min(b[0] - b[2] for b in bs)
    x1 = max(b[0] + b[2] for b in bs)
    n = 70
    top = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        ys = [by + math.sqrt(max(0.0, r * r - (x - bx) ** 2)) for bx, by, r in bs if abs(x - bx) <= r + 1e-9]
        top.append((x, max(ys) if ys else cy))
    return chain(top, [(x1, cy), (x0, cy), top[0]])


def fuselage(xt, xn, h, nose=0.9, tail=1.4, yc=0.0, droop=0.1, end=0.25):
    """Side-view fuselage, nose to the right.  Closed outline."""
    top, bot = yc + h / 2, yc - h / 2
    y_end = top - h * end
    return chain([(xt, top), (xn - nose, top)],
                 cubic((xn - nose, top), (xn - nose * 0.35, top), (xn, yc + h * 0.2), (xn, yc - h * droop), 14),
                 cubic((xn, yc - h * droop), (xn, yc - h * 0.42), (xn - nose * 0.4, bot), (xn - nose, bot), 12),
                 [(xt + tail, bot)],
                 quad((xt + tail, bot), (xt + tail * 0.45, bot), (xt, y_end), 16), [(xt, top)])


def windows(x0, x1, y, r=0.09, step=0.32, skip=()):
    out, x = [], x0
    while x <= x1 + 1e-9:
        if not any(a <= x <= b for a, b in skip):
            out.append(circle(x, y, r, 12))
        x += step
    return out


def wheel(cx, cy, r, hub=True):
    out = [circle(cx, cy, r, 28)]
    if hub and r >= 0.22:
        out.append(circle(cx, cy, r * 0.4, 14))
    return out


def blade(cx, cy, length, width, rot):
    """Propeller blade (paddle) from a hub, pointing at angle `rot`."""
    shape = chain(cubic((0.0, width * 0.35), (length * 0.3, width * 0.9), (length * 0.75, width * 0.75), (length * 0.92, width * 0.45), 16),
                  arc(length * 0.92, 0.0, width * 0.45, math.pi / 2, -math.pi / 2, 10),
                  cubic((length * 0.92, -width * 0.45), (length * 0.7, -width * 0.55), (length * 0.3, -width * 0.6), (0.0, -width * 0.35), 16))
    return transform(shape, dx=cx, dy=cy, rot=rot)


def mini_jet(cx, cy, s, rot=0.0):
    """Small jet seen from above, nose up."""
    right = [(0, 1.0), (0.1, 0.75), (0.14, 0.3), (0.85, -0.25), (0.85, -0.42), (0.15, -0.3), (0.13, -0.68), (0.42, -0.92),
             (0.42, -1.02), (0.08, -0.98), (0.0, -1.08)]
    outline = chain(right, mirror_x(right)[::-1])
    canopy = ellipse(0, 0.42, 0.07, 0.2, 16)
    return [transform(p, dx=cx, dy=cy, s=s, rot=rot) for p in (outline, canopy)]


def balloon_right(cx, cy, s):
    """Right half of a hot-air-balloon envelope, from the crown to the throat."""
    a = arc(0, 1.0, 1.9, math.pi / 2, -math.pi / 6, 40)
    p = a[-1]
    right = chain(a, cubic(p, (p[0] - 0.3, p[1] - 0.52), (0.6, -1.0), (0.45, -1.5), 20))
    return [(cx + x * s, cy + y * s) for x, y in right]


def balloon(cx, cy, s, gores=(0.35, 0.72), band=False):
    right = balloon_right(cx, cy, s)
    left = mirror_x(right, cx)
    env = chain(left[::-1], right, [left[-1]])
    out = [env]
    for f in gores:
        g = [(cx + (x - cx) * f, y) for x, y in right]
        out += [g, mirror_x(g, cx)]
    if band:
        fr = sorted([-1.0, 1.0] + [f for f in gores] + [-f for f in gores])
        def half(y):
            # half width of the envelope at height y (right side, below the crown)
            best = min(right, key=lambda p: abs(p[1] - y))
            return best[0] - cx
        pts = []
        for k, f in enumerate(fr):
            y = cy + (0.25 if k % 2 else -0.25) * s
            pts.append((cx + f * half(y), y))
        out.append(pts)
    tb = cy - 1.5 * s
    bw = 0.38 * s
    basket = rrect(cx - bw, tb - 1.05 * s, cx + bw, tb - 0.55 * s, 0.08 * s)
    ropes = [[(cx - 0.45 * s, tb), (cx - bw, tb - 0.55 * s)], [(cx + 0.45 * s, tb), (cx + bw, tb - 0.55 * s)]]
    out += [basket] + ropes
    return out


def P3(x, y, z):
    """Simple oblique projection used for the 3/4 views (x forward, y up, z span)."""
    return (z * 0.95 + x * 0.6, y + x * 0.42 - z * 0.12)


def p3(*pts):
    return [P3(*p) for p in pts]


# ------------------------------------------------------------------ airliners

@design("aviation_jump_jet", T)
def jump_jet(rng):
    body = chain([(3.1, 0.3)], quad((3.1, 0.3), (2.6, 0.62), (2.0, 0.7), 8), [(1.15, 0.75), (0.4, 1.0), (-0.6, 0.95), (-2.9, 0.62), (-2.9, 0.38),
                 (-1.0, -0.1), (1.6, -0.1)], quad((1.6, -0.1), (2.6, 0.0), (3.1, 0.3), 8))
    canopy = chain(quad((2.1, 0.7), (1.85, 1.15), (1.3, 1.1), 10), [(1.0, 0.9)])
    intake = chain(arc(0.95, 0.35, 0.36, math.pi / 2, 1.5 * math.pi, 14), [(1.2, -0.01), (1.2, 0.71), (0.95, 0.71)])
    wing = poly((0.5, 0.7), (-0.75, -0.75), (-1.35, -0.75), (-0.75, 0.6), closed=False)
    outrigger = [[(-1.05, -0.75), (-1.05, -1.0)], circle(-1.05, -1.1, 0.1, 10)]
    fin = poly((-1.9, 0.8), (-2.6, 1.85), (-2.95, 1.85), (-2.9, 0.62), closed=False)
    stab = lens((-2.2, 0.3), (-3.4, 0.0), 0.08)
    nozzles = [rrect(0.45, -0.75, 0.85, -0.05, 0.15), rrect(-0.6, -0.7, -0.2, -0.05, 0.15)]
    blast = []
    for x in (0.65, -0.4):
        for d in (-0.1, 0.1):
            blast.append([(x + d + 0.04 * math.sin(k * 1.3), -0.8 - 0.22 * k) for k in range(8)])
    pad = [ellipse(0.1, -2.75, 2.4, 0.45, 90), [(-0.35, -2.95), (-0.35, -2.55)], [(0.55, -2.95), (0.55, -2.55)], [(-0.35, -2.75), (0.55, -2.75)]]
    dust = [cloud(-2.2, -2.75, 0.55), cloud(2.4, -2.75, 0.5)]
    return make("Jump Jet Hovering", [body, canopy, intake, wing, fin, stab] + outrigger + nozzles + blast + pad + dust)


@design("aviation_jumbo_jet", T)
def jumbo_jet(rng):
    top, bot = 0.5, -0.5
    body = chain([(-3.2, top), (0.4, top)], cubic((0.4, top), (0.9, top), (1.0, 0.9), (1.6, 0.92), 14), [(2.0, 0.92)],
                 cubic((2.0, 0.92), (2.8, 0.9), (3.2, 0.3), (3.25, -0.1), 18),
                 cubic((3.25, -0.1), (3.25, -0.4), (2.8, bot), (2.3, bot), 10), [(-1.6, bot)],
                 quad((-1.6, bot), (-2.6, bot), (-3.2, 0.3), 16), [(-3.2, top)])
    fin = poly((-1.9, top), (-2.8, 2.3), (-3.25, 2.3), (-3.1, top), closed=False)
    stab = poly((-2.2, 0.1), (-3.0, 0.5), (-3.45, 0.5), (-2.85, 0.0), closed=False)
    wing = poly((1.2, -0.35), (-1.2, -2.3), (-1.8, -2.3), (-0.4, -0.45), closed=False)
    wing_far = poly((0.6, top), (-0.4, 1.3), (-0.85, 1.3), (-0.4, top), closed=False)
    nac = []
    for t in (0.33, 0.72):
        x, y = 1.2 + (-1.2 - 1.2) * t, -0.35 + (-2.3 + 0.35) * t
        nac += [rrect(x - 0.35, y - 0.55, x + 0.65, y - 0.12, 0.2), ellipse(x + 0.65, y - 0.335, 0.08, 0.2, 12)]
    upper = windows(1.25, 2.05, 0.68, 0.075, 0.27)
    main = windows(-2.0, 2.2, 0.05, 0.085, 0.3, skip=[(-0.1, 0.25)])
    cockpit = poly((2.35, 0.75), (2.7, 0.72), (2.85, 0.6), (2.4, 0.6))
    doors = [rrect(2.45, -0.35, 2.67, 0.3, 0.07), rrect(-0.02, -0.35, 0.2, 0.3, 0.07)]
    return make("Jumbo Jet", [body, fin, stab, wing, wing_far, cockpit] + nac + upper + main + doors)


def _front_airliner(s=1.0, dx=0.0, dy=0.0, gear=True):
    fus = circle(0, 0, 0.75, 70)
    wing = chain([(0.7, -0.25), (3.2, 0.3), (3.3, 0.85), (3.36, 0.85), (3.32, 0.18), (0.66, -0.45)])
    wing_l = mirror_x(wing)
    eng = []
    for x in (1.75, -1.75):
        eng += [circle(x, -0.55, 0.42, 40), circle(x, -0.55, 0.26, 30), [(x, -0.13), (x, 0.06 + 0.22 * (abs(x) - 0.7) / 2.5)]]
    fin = poly((-0.09, 0.745), (-0.02, 2.4), (0.02, 2.4), (0.09, 0.745), closed=False)
    stab = [[(-0.08, 1.0), (-1.3, 1.2), (-1.3, 1.1), (-0.06, 0.88)], [(0.08, 1.0), (1.3, 1.2), (1.3, 1.1), (0.06, 0.88)]]
    shield = chain([(-0.55, 0.22)], quad((-0.55, 0.22), (0, 0.42), (0.55, 0.22), 12), [(0.48, 0.05)],
                   quad((0.48, 0.05), (0, 0.18), (-0.48, 0.05), 12), [(-0.55, 0.22)])
    panes = [[(-0.17, 0.12), (-0.18, 0.33)], [(0.17, 0.12), (0.18, 0.33)]]
    parts = [fus, wing, wing_l, fin, shield] + eng + stab + panes
    if gear:
        parts += [[(0, -0.75), (0, -1.2)], rrect(-0.18, -1.55, 0.18, -1.15, 0.12)]
        for x in (0.9, -0.9):
            parts += [[(x * 0.7, -0.62), (x, -1.15)], rrect(x - 0.22, -1.6, x + 0.22, -1.15, 0.12)]
    return [transform(p, dx=dx, dy=dy, s=s) for p in parts]


@design("aviation_airliner_front", T)
def airliner_front(rng):
    ground = [[(-3.4, -1.65), (3.4, -1.65)]]
    lines_ = [[(-0.25, -2.6), (-0.15, -1.9)], [(0.25, -2.6), (0.15, -1.9)]]
    return make("Airliner Head-On", _front_airliner() + ground + lines_ + [cloud(-2.3, 2.0, 0.6), cloud(2.4, 2.4, 0.5)])


@design("aviation_takeoff", T)
def takeoff(rng):
    rot = math.radians(14)
    body = fuselage(-2.6, 2.6, 0.8, nose=0.8, tail=1.3)
    fin = poly((-1.5, 0.4), (-2.2, 1.7), (-2.6, 1.7), (-2.5, 0.4), closed=False)
    stab = poly((-1.75, 0.05), (-2.45, 0.35), (-2.8, 0.35), (-2.35, -0.05), closed=False)
    wing = poly((0.8, -0.25), (-0.4, -1.5), (-0.9, -1.5), (-0.25, -0.32), closed=False)
    eng = [rrect(-0.15, -1.15, 0.75, -0.75, 0.2)]
    win = windows(-1.5, 1.4, 0.06, 0.075, 0.26, skip=[(-0.2, 0.25)])
    cockpit = poly((1.9, 0.15), (2.25, 0.15), (2.42, 0.0), (1.95, 0.0))
    gear = [[(1.7, -0.4), (1.7, -0.75)], circle(1.7, -0.88, 0.13, 12), [(-1.15, -0.37), (-1.15, -0.85)], circle(-1.32, -1.0, 0.16, 14),
            circle(-0.98, -1.0, 0.16, 14)]
    plane = [transform(p, dx=0.4, dy=0.9, rot=rot) for p in [body, fin, stab, wing, cockpit] + eng + win + gear]
    runway = [[(-3.4, -2.2), (3.4, -2.2)], [(-3.4, -2.9), (3.4, -2.9)]]
    dashes = [rect(x, -2.6, x + 0.6, -2.5) for x in (-3.0, -1.8, -0.6, 0.6, 1.8)]
    lights = [circle(x, -2.05, 0.07, 8) for x in (-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0)]
    return make("Airliner Taking Off", plane + runway + dashes + lights + [cloud(2.2, 2.6, 0.55)])


@design("aviation_airliner_top", T)
def airliner_top(rng):
    right = chain(quad((0.0, 3.1), (0.33, 2.95), (0.34, 2.3), 10),
                  [(0.34, 0.75), (3.05, -0.65), (3.12, -0.95), (2.85, -1.0), (1.0, -0.62), (0.34, -0.72), (0.34, -1.9)],
                  quad((0.34, -1.9), (0.3, -2.35), (0.2, -2.45), 6), [(1.3, -2.95), (1.28, -3.15), (0.14, -3.0), (0.0, -3.2)])
    outline = chain(right, mirror_x(right)[::-1])
    engines = []
    for x in (1.35, -1.35):
        engines += [rrect(x - 0.22, -0.35, x + 0.22, 0.75, 0.18), [(x - 0.12, 0.75), (x + 0.12, 0.75)]]
    cockpit = arc(0, 2.45, 0.27, math.radians(20), math.radians(160), 12)
    fin = [[(0, -2.0), (0, -3.15)]]
    flaps = [[(1.0 * sx, -0.62), (0.9 * sx, -0.45), (2.4 * sx, -0.73)] for sx in (1, -1)]
    clouds = [cloud(-2.3, 1.9, 0.55), cloud(2.3, 2.1, 0.5), cloud(2.0, -2.4, 0.6)]
    return make("Airliner Seen from Above", [outline, cockpit] + engines + fin + flaps + clouds)


# ------------------------------------------------------------------ light & vintage aircraft

def _cessna_parts(gear=True):
    fus = chain([(-1.0, 1.0)], [(-3.1, 0.62), (-3.1, 0.38), (-0.9, -0.3), (1.8, -0.35)],
                quad((1.8, -0.35), (2.45, -0.25), (2.5, 0.3), 10), quad((2.5, 0.3), (2.45, 0.68), (1.65, 0.7), 10), [(1.05, 1.0)])
    wing = rrect(-1.05, 1.0, 1.35, 1.32, 0.16)
    fin = poly((-1.9, 0.82), (-2.75, 2.0), (-3.2, 2.0), (-3.1, 0.62), closed=False)
    stab = lens((-2.3, 0.45), (-3.45, 0.45), 0.07)
    win = [poly((0.25, 0.4), (1.15, 0.4), (0.95, 0.88), (0.25, 0.88)), poly((-0.4, 0.4), (0.05, 0.4), (0.05, 0.88), (-0.25, 0.88))]
    strut = [[(-0.15, -0.28), (-0.85, 1.0)]]
    prop = [lens((2.6, 0.3), (2.6, 1.45), 0.12), lens((2.6, 0.3), (2.6, -0.85), 0.12)]
    cowl = [[(1.65, 0.7), (1.75, -0.33)]]
    out = [fus, wing, fin, stab] + win + strut + prop + cowl
    if gear:
        out += [[(1.9, -0.35), (1.9, -0.75)]] + wheel(1.9, -0.95, 0.22) + [[(0.1, -0.32), (-0.1, -0.75)]] + wheel(-0.15, -1.0, 0.27)
    return out


@design("aviation_cessna", T)
def cessna(rng):
    ground = [[(-3.4, -1.27), (3.4, -1.27)]]
    grass = [zigzag(-3.2, -1.2, -1.4, 0.1, 6), zigzag(1.0, 3.2, -1.4, 0.1, 6)]
    return make("High-Wing Light Aircraft", _cessna_parts() + ground + grass + [cloud(-1.8, 2.4, 0.6)])


@design("aviation_crop_duster", T)
def crop_duster(rng):
    fus = chain([(-3.0, 1.55), (-3.0, 1.3), (-0.6, 0.85), (1.5, 0.85)], quad((1.5, 0.85), (2.3, 0.9), (2.35, 1.35), 8),
                quad((2.35, 1.35), (2.3, 1.8), (1.5, 1.8), 8), [(0.75, 1.8), (-0.95, 1.75), (-3.0, 1.55)])
    canopy = [poly((0.75, 1.8), (0.45, 2.35), (-0.55, 2.35), (-0.95, 1.75), closed=False), [(-0.05, 1.78), (-0.05, 2.35)]]
    cowl = [[(1.5, 1.8), (1.5, 0.85)]]
    wing = chain(quad((1.1, 0.85), (0.3, 0.55), (-0.7, 0.75), 12), [(-0.75, 0.85)])
    fin = chain([(-2.2, 1.65)], quad((-2.2, 1.65), (-2.8, 2.6), (-3.1, 2.55), 10), [(-3.0, 1.55)])
    stab = lens((-2.3, 1.35), (-3.4, 1.4), 0.08)
    prop = [lens((2.45, 1.35), (2.45, 2.45), 0.11), lens((2.45, 1.35), (2.45, 0.25), 0.11)]
    gear = [[(1.2, 0.85), (1.35, 0.15)]] + wheel(1.35, -0.07, 0.22) + [[(-2.7, 1.33), (-2.8, 1.1)], circle(-2.8, 1.0, 0.1, 10)]
    spray = []
    spray.append(rrect(-0.85, 0.5, 0.6, 0.62, 0.05))
    for k, x in enumerate((-0.6, -0.1, 0.4)):
        spray.append(quad((x, 0.5), (x - 0.9, 0.0), (x - 2.6, -0.4 - 0.25 * k), 16))
        spray.append(quad((x, 0.5), (x - 0.5, -0.3), (x - 1.5, -1.2 - 0.2 * k), 16))
    rows = [[(-3.4 + 1.1 * k, -3.0), (-1.0 + 0.4 * k, -2.0)] for k in range(7)]
    horizon = [[(-3.4, -2.0), (3.4, -2.0)]]
    return make("Crop Duster", [fus, wing, fin, stab] + canopy + cowl + prop + gear + spray + rows + horizon)


def _semi_wing(cx, cy, rx, ry, xcut, side, n=40):
    t0 = math.acos(xcut / rx)
    if side > 0:
        ts = [t0 - 2 * t0 * i / n for i in range(n + 1)]
    else:
        ts = [math.pi - t0 + 2 * t0 * i / n for i in range(n + 1)]
    return [(cx + rx * math.cos(t), cy + ry * math.sin(t)) for t in ts]


@design("aviation_spitfire", T)
def spitfire(rng):
    fus = chain(cubic((0.0, 2.55), (0.42, 2.4), (0.36, 0.4), (0.28, -1.0), 30), [(0.1, -2.75)], [(-0.1, -2.75)],
                cubic((-0.28, -1.0), (-0.36, 0.4), (-0.42, 2.4), (0.0, 2.55), 30))
    wings = [_semi_wing(0, 0.2, 3.1, 0.75, 0.34, 1), _semi_wing(0, 0.2, 3.1, 0.75, 0.34, -1)]
    stabs = [_semi_wing(0, -2.2, 1.15, 0.32, 0.17, 1, 24), _semi_wing(0, -2.2, 1.15, 0.32, 0.17, -1, 24)]
    canopy = ellipse(0, 0.75, 0.16, 0.42, 20)
    spinner = arc(0, 2.4, 0.2, 0, math.pi, 10)
    prop = lens((-1.0, 2.75), (1.0, 2.75), 0.06)
    roundels = []
    for x in (1.85, -1.85):
        roundels += [circle(x, 0.15, 0.36, 30), circle(x, 0.15, 0.17, 18)]
    guns = [[(x, 0.92), (x, 1.15)] for x in (1.1, 1.4, -1.1, -1.4)]
    return make("Spitfire Fighter", [fus, canopy, spinner, prop] + wings + stabs + roundels + guns)


@design("aviation_mustang", T)
def mustang(rng):
    fus = chain([(2.45, -0.2), (2.45, 0.62)], quad((2.45, 0.62), (1.6, 0.78), (0.85, 0.76), 10), [(-0.85, 0.72)],
                [(-2.95, 0.42), (-2.95, 0.15), (-1.0, -0.2), (-0.45, -0.25)], quad((-0.45, -0.25), (-0.2, -0.62), (0.4, -0.62), 8),
                [(0.75, -0.6)], quad((0.75, -0.6), (1.0, -0.6), (1.1, -0.3), 6), [(2.45, -0.2)])
    canopy = chain(quad((0.85, 0.76), (0.45, 1.3), (-0.15, 1.2), 12), quad((-0.15, 1.2), (-0.6, 1.08), (-0.85, 0.72), 10))
    spinner = chain(quad((2.45, 0.62), (3.1, 0.55), (3.15, 0.21), 8), quad((3.15, 0.21), (3.1, -0.15), (2.45, -0.2), 8))
    prop = [lens((2.65, 0.75), (2.65, 2.2), 0.1), lens((2.65, -0.33), (2.65, -1.8), 0.1)]
    wing = poly((1.15, -0.25), (0.45, -1.7), (-0.35, -1.7), (-0.42, -0.3), closed=False)
    fin = chain([(-1.9, 0.58)], quad((-1.9, 0.58), (-2.6, 1.75), (-2.95, 1.7), 12), [(-2.95, 0.42)])
    stab = lens((-2.2, 0.3), (-3.35, 0.32), 0.08)
    insignia = [circle(-1.45, 0.25, 0.3, 30), star(-1.45, 0.25, 0.27)]
    exhaust = [[(1.9, 0.35), (1.3, 0.38)]]
    clouds = [cloud(-2.0, -2.1, 0.7), cloud(1.6, -2.6, 0.5)]
    return make("P-51 Mustang", [fus, canopy, spinner, wing, fin, stab] + prop + insignia + exhaust + clouds)


@design("aviation_fighter_top", T)
def fighter_top(rng):
    right = [(0.0, 3.2), (0.18, 2.5), (0.3, 1.6), (0.38, 0.9), (0.55, 0.45), (2.75, -0.8), (2.75, -1.3), (0.62, -1.25), (0.55, -1.75),
             (1.55, -2.45), (1.55, -2.75), (0.45, -2.6), (0.38, -3.0), (0.22, -3.2), (0.0, -3.2)]
    outline = chain(right, mirror_x(right)[::-1])
    canopy = ellipse(0, 1.6, 0.17, 0.6, 24)
    missiles = [rrect(2.82, -1.45, 3.0, -0.35, 0.08), rrect(-3.0, -1.45, -2.82, -0.35, 0.08)]
    lines_ = [[(0.0, -1.5), (0.0, -3.0)], [(0.3, -3.0), (-0.3, -3.0)]]
    flaps = [[(0.62, -1.05), (2.75, -1.1)], [(-0.62, -1.05), (-2.75, -1.1)]]
    return make("Jet Fighter Top View", [outline, canopy] + missiles + lines_ + flaps)


@design("aviation_stealth_bomber", T)
def stealth_bomber(rng):
    right = [(0.0, 1.6), (3.3, -0.85), (3.15, -1.1), (2.05, -0.38), (1.15, -1.1), (0.6, -0.65), (0.0, -1.05)]
    outline = chain(right, mirror_x(right)[::-1])
    cockpit = [poly((-0.3, 0.95), (0.3, 0.95), (0.18, 1.2), (-0.18, 1.2))]
    hump = [quad((-0.55, 0.65), (0, 1.0), (0.55, 0.65)), quad((-0.7, 0.0), (0, 0.4), (0.7, 0.0))]
    intakes = [zigzag(0.75, 1.45, 0.38, 0.07, 3), zigzag(-1.45, -0.75, 0.38, 0.07, 3)]
    exhaust = [[(0.65, -0.35), (1.15, -0.55)], [(-0.65, -0.35), (-1.15, -0.55)]]
    clouds = [cloud(-2.0, -2.6, 0.7), cloud(1.9, -2.3, 0.6), cloud(2.2, 1.6, 0.5)]
    return make("Stealth Bomber", [outline] + cockpit + hump + intakes + exhaust + clouds)


@design("aviation_concorde", T)
def concorde(rng):
    body = chain([(-3.0, 0.22), (2.2, 0.22)], quad((2.2, 0.22), (3.0, 0.15), (3.45, -0.15), 12),
                 quad((3.45, -0.15), (2.8, -0.22), (2.2, -0.22), 8), [(-2.4, -0.22)], quad((-2.4, -0.22), (-2.9, -0.1), (-3.0, 0.22), 6))
    wing = chain(cubic((1.6, -0.22), (0.4, -0.4), (-0.6, -1.25), (-1.9, -1.45), 24), [(-2.75, -1.45)], [(-2.45, -0.22)])
    fin = chain([(-1.35, 0.22)], quad((-1.35, 0.22), (-2.2, 0.9), (-2.75, 1.9), 12), [(-3.0, 1.9), (-3.0, 0.22)])
    nac = [rrect(-2.15, -0.95, -0.7, -0.62, 0.06), rrect(-2.3, -1.38, -1.0, -1.05, 0.06)]
    cockpit = [[(2.25, 0.12), (2.6, 0.08)]]
    win = windows(-2.2, 1.9, -0.0, 0.06, 0.22)
    trail = [[(-3.2, -0.8), (-3.6, -0.75)], [(-3.3, -1.2), (-3.7, -1.15)]]
    sky = [cloud(1.5, -2.0, 0.6), cloud(-0.2, 1.8, 0.6)]
    return make("Concorde Supersonic Jet", [body, wing, fin] + nac + cockpit + win + trail + sky)


@design("aviation_cargo_plane", T)
def cargo_plane(rng):
    body = chain([(-1.1, -0.5)], [(2.2, -0.5)], quad((2.2, -0.5), (3.05, -0.4), (3.1, 0.25), 10),
                 cubic((3.1, 0.25), (3.1, 0.75), (2.7, 1.05), (2.0, 1.05), 12), [(-0.6, 1.05)],
                 quad((-0.6, 1.05), (-2.0, 1.05), (-3.2, 1.6), 12), [(-3.25, 1.35)])
    opening = quad((-3.25, 1.35), (-2.0, 0.4), (-1.1, -0.5), 14)
    ramp = poly((-1.1, -0.5), (-2.5, -1.3), (-2.65, -1.2), (-1.25, -0.35))
    wing = chain([(-0.3, 1.05)], quad((-0.3, 1.05), (-0.2, 1.38), (0.4, 1.38), 8), [(1.3, 1.38)], quad((1.3, 1.38), (1.7, 1.35), (1.75, 1.05), 6))
    fin = poly((-2.5, 1.33), (-2.95, 2.9), (-3.4, 2.9), (-3.3, 1.55), closed=False)
    stab = lens((-2.7, 1.75), (-3.7, 1.8), 0.08)
    nacelles = [rrect(1.0, 0.75, 2.3, 1.2, 0.18), lens((2.38, 0.98), (2.38, 2.2), 0.1), lens((2.38, 0.98), (2.38, -0.25), 0.1)]
    cockpit = poly((2.35, 0.75), (2.85, 0.75), (3.0, 0.5), (2.45, 0.5))
    gear = wheel(0.5, -0.82, 0.3) + wheel(-0.25, -0.82, 0.3) + wheel(2.4, -0.88, 0.24)
    gear += [[(2.4, -0.5), (2.4, -0.64)]]
    crates = [rect(-3.5, -1.3, -2.8, -0.6), rect(-3.4, -0.6, -2.9, -0.1), [(-3.5, -1.3), (-2.8, -0.6)]]
    ground = [[(-3.6, -1.3), (3.3, -1.3)]]
    door = rrect(1.6, -0.35, 1.95, 0.45, 0.06)
    return make("Cargo Plane with Open Ramp", [body, opening, ramp, wing, fin, stab, cockpit, door] + nacelles + gear + crates + ground)


@design("aviation_glider", T)
def glider(rng):
    fus = chain(cubic((0.0, 2.2), (0.32, 2.1), (0.3, 1.2), (0.2, 0.4), 18), [(0.07, -2.0)], [(-0.07, -2.0)],
                cubic((-0.2, 0.4), (-0.3, 1.2), (-0.32, 2.1), (0.0, 2.2), 18))
    wr = chain([(0.24, 0.85)], [(3.15, 0.62)], quad((3.15, 0.62), (3.4, 0.55), (3.2, 0.38), 6), [(0.21, 0.4)])
    wl = mirror_x(wr)
    tail = [chain([(0.07, -1.8)], [(0.9, -1.85)], quad((0.9, -1.85), (1.05, -1.95), (0.9, -2.05), 4), [(0.07, -2.0)])]
    tail.append(mirror_x(tail[0]))
    canopy = ellipse(0, 1.45, 0.14, 0.42, 18)
    birds = [chain(arc(x - 0.2, y, 0.2, math.radians(30), math.radians(150), 6)[::-1], arc(x + 0.2, y, 0.2, math.radians(30), math.radians(150), 6)[::-1])
             for x, y in [(-2.2, 2.4), (-1.6, 2.7), (2.0, -1.5)]]
    thermal = [spiral(-1.6, -1.6, 0.15, 1.0, 1.6, 90)]
    return make("Sailplane Glider", [fus, wr, wl, canopy] + tail + birds + thermal + [cloud(2.1, 2.2, 0.6)])


@design("aviation_hang_glider", T)
def hang_glider(rng):
    sail = chain([(-3.2, 0.9), (0.0, 2.2), (3.2, 0.9)], quad((3.2, 0.9), (2.3, 0.75), (1.6, 1.05), 10), quad((1.6, 1.05), (0.8, 0.8), (0.0, 1.25), 10),
                 quad((0.0, 1.25), (-0.8, 0.8), (-1.6, 1.05), 10), quad((-1.6, 1.05), (-2.3, 0.75), (-3.2, 0.9), 10))
    battens = [[(0, 2.2), (0, 1.25)], [(-1.6, 1.05), (-1.25, 1.65)], [(1.6, 1.05), (1.25, 1.65)]]
    frame = poly((0, 1.25), (-0.95, -0.9), (0.95, -0.9))
    head = circle(0, 0.1, 0.3, 26)
    visor = arc(0, 0.1, 0.2, math.radians(200), math.radians(340), 8)
    harness = [rrect(-0.35, -0.5, 0.35, -0.2, 0.12)]
    arms = [[(-0.25, -0.35), (-0.55, -0.88)], [(0.25, -0.35), (0.55, -0.88)]]
    hills = [quad((-3.4, -2.8), (-2.0, -1.2), (-0.6, -2.8)), quad((-1.2, -2.8), (0.8, -1.5), (3.4, -2.8))]
    trees = [poly((x - 0.2, -2.5), (x, -2.0), (x + 0.2, -2.5)) for x in (1.8, 2.3)]
    return make("Hang Glider", [sail, frame, head, visor] + battens + harness + arms + hills + trees)


@design("aviation_paraglider", T)
def paraglider(rng):
    a0, a1 = math.radians(20), math.radians(160)
    outer = arc(0, -0.8, 3.3, a0, a1, 80)
    inner = arc(0, -0.8, 2.75, a0, a1, 70)
    canopy = chain(outer, inner[::-1], [outer[0]])
    cells = [[(2.75 * math.cos(a), -0.8 + 2.75 * math.sin(a)), (3.3 * math.cos(a), -0.8 + 3.3 * math.sin(a))]
             for a in [a0 + (a1 - a0) * k / 10 for k in range(1, 10)]]
    lines_ = []
    for k in range(0, 11, 2):
        a = a0 + (a1 - a0) * k / 10
        sx = 0.22 if math.cos(a) > 0 else -0.22
        lines_.append([(2.75 * math.cos(a), -0.8 + 2.75 * math.sin(a)), (sx, -1.7)])
    head = circle(0, -1.6, 0.22, 20)
    body = rrect(-0.3, -2.4, 0.3, -1.85, 0.12)
    seat = rrect(-0.45, -2.65, 0.55, -2.35, 0.12)
    legs = [[(0.3, -2.4), (0.9, -2.75)], [(0.3, -2.25), (0.95, -2.55)]]
    mountains = [poly((-3.4, -3.3), (-2.3, -2.0), (-1.6, -2.7), (-1.0, -2.2), (0.0, -3.3), closed=False),
                 poly((1.0, -3.3), (2.2, -2.1), (3.4, -3.3), closed=False)]
    return make("Paraglider", [canopy, head, body, seat] + cells + lines_ + legs + mountains)


# ------------------------------------------------------------------ balloons & airships

@design("aviation_striped_balloon", T)
def striped_balloon(rng):
    parts = balloon(0, 0.3, 1.25, gores=(0.25, 0.5, 0.75), band=True)
    flame = lens((0, -1.75), (0, -1.15), 0.25)
    return make("Striped Hot Air Balloon", parts + [flame, cloud(-2.6, -1.4, 0.45), cloud(2.6, 2.6, 0.45)])


@design("aviation_balloon_basket", T)
def balloon_basket(rng):
    env = [chain([(-3.2, 3.2)], quad((-3.2, 3.2), (-1.6, 2.5), (-1.0, 1.9), 14), [(1.0, 1.9)], quad((1.0, 1.9), (1.6, 2.5), (3.2, 3.2), 14)),
           [(-0.4, 1.9), (-0.6, 3.2)], [(0.4, 1.9), (0.6, 3.2)]]
    burner = [rrect(-0.5, 0.75, 0.5, 1.2, 0.1), lens((0, 1.2), (0, 2.4), 0.22), lens((0, 1.25), (0, 1.9), 0.15)]
    ropes = [[(-1.8, -0.6), (-0.5, 0.95)], [(1.8, -0.6), (0.5, 0.95)], [(-1.0, 1.9), (-0.5, 1.2)], [(1.0, 1.9), (0.5, 1.2)]]
    basket = rrect(-1.9, -3.0, 1.9, -0.85, 0.2)
    rim = rrect(-2.05, -0.9, 2.05, -0.55, 0.15)
    weave = [[(-1.9, y), (1.9, y)] for y in (-1.45, -2.05, -2.55)] + [[(x, -0.9), (x, -3.0)] for x in (-1.25, -0.6, 0.0, 0.6, 1.25)]
    p1 = [circle(-0.95, 0.05, 0.36, 30), [(-1.3, -0.5), (-1.75, 0.4)], [(-0.6, -0.55), (-0.5, -0.55)]]
    p2 = [circle(0.95, 0.05, 0.36, 30), [(1.3, -0.5), (1.85, 0.5)], circle(1.9, 0.6, 0.12, 10)]
    hints = [eye(-1.07, 0.1, 0.05), eye(-0.83, 0.1, 0.05), eye(0.83, 0.1, 0.05), eye(1.07, 0.1, 0.05)]
    return make("Balloon Basket and Burner", env + burner + ropes + [basket, rim] + weave + p1 + p2, hints)


@design("aviation_balloon_festival", T)
def balloon_festival(rng):
    parts = balloon(-1.2, 0.85, 0.95, gores=(0.4, 0.8))
    parts += balloon(1.85, 1.75, 0.55, gores=(0.5,))
    parts += balloon(1.6, -1.05, 0.45, gores=(0.0, 0.6))
    hills = [quad((-3.6, -3.1), (-1.8, -2.1), (0.0, -3.1)), quad((-0.4, -3.1), (1.6, -2.2), (3.6, -3.1)), [(-3.6, -3.1), (3.6, -3.1)]]
    return make("Balloon Festival", parts + hills + [cloud(-2.8, 2.9, 0.4)])


@design("aviation_zeppelin", T)
def zeppelin(rng):
    rx, ry, cy = 3.1, 0.8, 0.8
    hull = ellipse(0, cy, rx, ry, 160)
    rings = []
    for x in (-2.2, -1.2, -0.2, 0.8, 1.8):
        h = ry * math.sqrt(1 - (x / rx) ** 2)
        rings.append(quad((x, cy + h), (x + 0.22, cy), (x, cy - h), 14))
    spine = [[(-2.9, cy + 0.05), (2.9, cy + 0.05)]]
    fins = [poly((-2.3, cy + 0.55), (-3.3, cy + 1.3), (-3.25, cy + 0.2), closed=False),
            poly((-2.3, cy - 0.55), (-3.3, cy - 1.3), (-3.25, cy - 0.2), closed=False)]
    gondola = [rrect(0.6, -0.55, 2.0, -0.1, 0.18)] + [rrect(x, -0.45, x + 0.2, -0.25, 0.05) for x in (0.85, 1.2, 1.55)]
    pods = []
    for x in (-1.4, -0.4):
        pods += [ellipse(x, -0.35, 0.3, 0.15, 16), [(x, cy - ry * math.sqrt(1 - (x / rx) ** 2)), (x, -0.2)], lens((x - 0.35, -0.65), (x - 0.35, -0.05), 0.12)]
    clouds = [cloud(-2.0, -2.0, 0.7), cloud(2.0, -1.8, 0.5)]
    return make("Zeppelin Airship", [hull] + rings + spine + fins + gondola + pods + clouds)


# ------------------------------------------------------------------ pioneers

@design("aviation_wright_flyer", T)
def wright_flyer(rng):
    def foil(x0, x1, y, rise=0.42):
        c = (x0 + x1) / 2
        return chain(quad((x1, y), (c + 0.15 * (x1 - x0), y + rise), (x0, y + 0.03), 16), quad((x0, y + 0.03), (c, y + 0.1), (x1, y), 14))
    wings = [foil(-1.1, 1.1, 1.3), foil(-1.1, 1.1, 0.0)]
    struts = [[(x, 0.12), (x, 1.32)] for x in (-0.9, 0.0, 0.9)] + [[(-0.9, 0.12), (0.0, 1.38)], [(0.0, 0.12), (0.9, 1.32)]]
    canard = [foil(2.2, 3.3, 1.1, 0.25), foil(2.2, 3.3, 0.3, 0.25), [(2.75, 0.38), (2.75, 1.2)]]
    booms = [[(1.1, 0.0), (2.2, 0.3)], [(1.1, 1.3), (2.2, 1.1)], [(-1.1, 0.03), (-2.75, 0.05)], [(-1.1, 1.33), (-2.75, 1.3)],
             [(-1.1, 0.03), (-2.75, 1.3)]]
    rudder = [rrect(-3.2, -0.05, -2.75, 1.4, 0.06), [(-2.97, -0.05), (-2.97, 1.4)]]
    props = [lens((-1.35, 0.65), (-1.35, 1.4), 0.12), lens((-1.35, 0.65), (-1.35, -0.1), 0.12)]
    pilot = [circle(0.55, 0.42, 0.16, 14), [(0.4, 0.3), (-0.5, 0.25)]]
    engine = [rect(-0.35, 0.35, 0.05, 0.7)]
    skids = [chain([(-0.9, -0.4), (2.6, -0.4)], quad((2.6, -0.4), (3.05, -0.4), (3.15, 0.05), 8)), [(-0.5, 0.03), (-0.5, -0.4)], [(0.7, 0.03), (0.7, -0.4)],
             [(2.6, -0.4), (2.6, 0.35)]]
    rail = [[(-3.4, -0.6), (3.4, -0.6)]]
    dunes = [quad((-3.4, -1.8), (-2.0, -0.9), (-0.4, -1.8), 20), quad((-1.0, -1.8), (1.2, -1.0), (3.4, -1.8), 24)]
    return make("Wright Flyer 1903", wings + struts + canard + booms + rudder + props + pilot + engine + skids + rail + dunes
                + [cloud(-2.2, 2.3, 0.55), cloud(2.0, 2.6, 0.45)])


@design("aviation_triplane", T)
def triplane(rng):
    wings = [rrect(-3.0, 1.6, 3.0, 1.85, 0.12), rrect(-2.7, 0.75, 2.7, 1.0, 0.12), rrect(-2.4, -0.4, 2.4, -0.15, 0.12)]
    cowl = [circle(0, 0.35, 0.55, 50), circle(0, 0.35, 0.18, 16)]
    prop = [lens((0.1, 0.45), (0.95, 1.95), 0.1), lens((-0.1, 0.25), (-0.95, -1.25), 0.1)]
    struts = [[(x, -0.15), (x, 1.6)] for x in (-2.0, 2.0)] + [[(-0.4, 1.0), (-0.3, 1.6)], [(0.4, 1.0), (0.3, 1.6)]]
    pilot = [arc(0, 1.25, 0.3, 0, math.pi, 12)]
    gear = [[(-0.35, -0.2), (-0.85, -1.35)], [(0.35, -0.2), (0.85, -1.35)], [(-0.85, -1.4), (0.85, -1.4)],
            ellipse(-1.0, -1.4, 0.16, 0.5, 24), ellipse(1.0, -1.4, 0.16, 0.5, 24)]
    axle = [rrect(-0.75, -1.5, 0.75, -1.3, 0.08)]
    ground = [[(-3.2, -1.95), (3.2, -1.95)]]
    return make("Triplane", wings + cowl + prop + struts + pilot + gear + axle + ground)


@design("aviation_bleriot", T)
def bleriot(rng):
    top = [(1.6, 0.55), (-3.0, 0.3)]
    bot = [(1.6, -0.2), (-3.0, 0.15)]
    frame = [top, bot, [(-3.0, 0.15), (-3.0, 0.3)]]
    xs = [1.6, 0.8, 0.0, -0.8, -1.6, -2.3]
    def yat(line, x):
        (x0, y0), (x1, y1) = line
        return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    truss = [[(x, yat(top, x)), (x, yat(bot, x))] for x in xs[1:]]
    truss += [[(xs[i], yat(top, xs[i])), (xs[i + 1], yat(bot, xs[i + 1]))] for i in range(len(xs) - 1)]
    cowl = [rrect(1.6, -0.25, 2.3, 0.6, 0.15)]
    prop = [lens((2.4, 0.18), (2.4, 1.35), 0.12), lens((2.4, 0.18), (2.4, -1.0), 0.12)]
    wing = poly((0.9, 0.52), (0.6, 1.75), (-0.2, 1.75), (-0.5, 0.45), closed=False)
    wing_near = poly((1.0, -0.12), (0.7, -1.45), (-0.1, -1.45), (-0.6, -0.05), closed=False)
    tail = [lens((-2.5, 0.22), (-3.6, 0.22), 0.14), chain([(-2.85, 0.3)], quad((-2.85, 0.3), (-2.9, 1.1), (-3.3, 1.0), 10), quad((-3.3, 1.0), (-3.55, 0.6), (-3.0, 0.3), 8))]
    pylon = [[(0.2, 0.5), (0.2, 1.75)]]
    gear = [[(1.4, -0.2), (1.2, -1.3)], [(0.6, -0.15), (1.2, -1.3)]] + wheel(1.2, -1.6, 0.35)
    pilot = [circle(-1.0, 0.62, 0.2, 18)]
    ground = [[(-3.7, -1.95), (3.0, -1.95)]]
    return make("Early Monoplane", frame + truss + cowl + prop + [wing, wing_near] + tail + pylon + gear + pilot + ground)


@design("aviation_da_vinci", T)
def da_vinci(rng):
    def wing(side):
        root = (0.4 * side, 0.6)
        tips = [(3.2 * side, 2.6), (3.4 * side, 1.4), (3.3 * side, 0.2), (2.8 * side, -0.8), (2.0 * side, -1.4)]
        ribs = [[root, t] for t in tips]
        edge = [root, tips[0]]
        for a, b in zip(tips, tips[1:]):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            ix, iy = mx + (root[0] - mx) * 0.18, my + (root[1] - my) * 0.18
            edge += quad(a, (ix, iy), b, 10)[1:]
        edge.append(root)
        spar = quad((0.4 * side, 1.4), (1.8 * side, 2.6), (3.2 * side, 2.6), 14)
        return [edge, spar] + ribs[1:]
    frame = [rrect(-0.45, -1.6, 0.45, 1.4, 0.15), [(-0.45, 0.6), (0.45, 0.6)]]
    pilot = [circle(0, 2.0, 0.3, 24), [(0, 1.7), (0, 1.4)]]
    pulley = [circle(0, -0.4, 0.3, 24), [(0, -0.1), (0, 0.6)]]
    tail = [poly((0, -1.6), (-0.9, -2.8), (0.9, -2.8)), [(0, -1.6), (0, -2.8)], [(-0.45, -2.2), (0.45, -2.2)]]
    return make("Leonardo's Flying Machine", wing(1) + wing(-1) + frame + pilot + pulley + tail)


# ------------------------------------------------------------------ rotorcraft & drones

@design("aviation_autogyro", T)
def autogyro(rng):
    pod = chain(cubic((-0.9, -0.2), (-1.0, 0.9), (0.4, 1.1), (1.4, 0.6), 20), quad((1.4, 0.6), (1.95, 0.2), (1.3, -0.2), 10), [(-0.9, -0.2)])
    screen = [[(0.75, 0.88), (0.55, 1.35)]]
    pilot = [circle(0.15, 1.25, 0.25, 22), [(-0.1, 1.3), (0.4, 1.3)]]
    mast = [[(-0.35, 0.95), (-0.35, 2.15)]]
    rotor = tube([(-3.3, 2.32), (2.7, 2.16)], 0.12)
    hub = circle(-0.35, 2.24, 0.14, 12)
    prop = [lens((-1.2, 0.35), (-1.2, 1.45), 0.11), lens((-1.2, 0.35), (-1.2, -0.75), 0.11)]
    boom = [[(-0.7, -0.1), (-2.8, 0.3)], [(-0.95, 0.15), (-2.8, 0.45)]]
    tail = [rrect(-3.25, 0.1, -2.8, 1.25, 0.15), lens((-2.7, 0.38), (-3.6, 0.38), 0.08)]
    gear = [[(0.0, -0.2), (0.0, -0.55)]] + wheel(0.0, -0.8, 0.25) + [[(1.3, -0.2), (1.35, -0.55)], circle(1.35, -0.72, 0.17, 14)]
    ground = [[(-3.6, -1.05), (3.0, -1.05)]]
    return make("Autogyro", [pod, rotor, hub] + screen + pilot + mast + prop + boom + tail + gear + ground + [cloud(1.9, 3.0, 0.5)])


@design("aviation_tiltrotor", T)
def tiltrotor(rng):
    fus = chain([(-0.6, 0.5), (-0.6, -0.6)], arc(0, -0.6, 0.6, math.pi, 2 * math.pi, 20), [(0.6, 0.5)])
    wing = [[(-2.12, 0.5), (2.12, 0.5)], [(-2.12, 0.78), (2.12, 0.78)]]
    shield = poly((-0.45, -0.05), (0.45, -0.05), (0.35, 0.3), (-0.35, 0.3))
    parts = [fus, shield, [(0, -0.05), (0, 0.3)]] + wing
    for x in (-2.4, 2.4):
        parts += [rrect(x - 0.28, 0.0, x + 0.28, 1.55, 0.2), ellipse(x, 1.75, 1.45, 0.24, 60), arc(x, 1.55, 0.2, 0, math.pi, 8)]
        for a in (math.pi / 2 + 0.3, math.pi * 7 / 6 + 0.3, math.pi * 11 / 6 + 0.3):
            parts.append([(x, 1.75), (x + 1.4 * math.cos(a), 1.75 + 0.22 * math.sin(a))])
    fins = [rrect(0.75, 0.78, 0.95, 1.45, 0.06), rrect(-0.95, 0.78, -0.75, 1.45, 0.06)]
    gear = [rrect(-0.5, -1.65, -0.25, -1.15, 0.1), rrect(0.25, -1.65, 0.5, -1.15, 0.1)]
    ground = [[(-3.6, -1.7), (3.6, -1.7)]]
    return make("Tiltrotor Aircraft", parts + fins + gear + ground)


@design("aviation_rescue_helicopter", T)
def rescue_helicopter(rng):
    body = chain([(-1.0, 1.0), (1.2, 1.0)], quad((1.2, 1.0), (2.3, 0.75), (2.4, 0.0), 12), quad((2.4, 0.0), (2.3, -0.6), (1.5, -0.6), 10),
                 [(-1.0, -0.6)], quad((-1.0, -0.6), (-1.4, -0.4), (-1.6, 0.35), 8), [(-3.1, 0.6), (-3.3, 0.35), (-3.55, 1.7), (-3.15, 1.7), (-2.85, 0.85), (-1.0, 1.0)])
    hump = quad((-0.8, 1.0), (0.0, 1.55), (0.9, 1.0), 14)
    mast = [[(0.0, 1.28), (0.0, 1.65)], rrect(-0.2, 1.62, 0.2, 1.78, 0.06)]
    rotor = tube([(-3.2, 1.78), (3.3, 1.62)], 0.1)
    fenestron = [circle(-3.3, 1.0, 0.22, 18)]
    shield = poly((1.35, 0.95), (2.1, 0.7), (2.25, 0.2), (1.35, 0.2))
    door = rrect(-0.6, -0.45, 0.6, 0.8, 0.08)
    winch = [[(0.5, 1.0), (0.5, 1.15), (1.0, 1.15)], rrect(0.9, 0.95, 1.15, 1.15, 0.05)]
    cable = [[(1.02, 0.95), (1.02, -1.55)]]
    hook = [circle(1.02, -1.62, 0.07, 8)]
    r1 = [circle(0.75, -1.95, 0.22, 18), rrect(0.55, -2.75, 0.95, -2.2, 0.12), [(0.95, -2.3), (1.0, -1.7)], [(0.65, -2.75), (0.55, -3.1)], [(0.85, -2.75), (0.95, -3.1)]]
    r2 = [circle(1.35, -2.05, 0.22, 18), rrect(1.15, -2.85, 1.55, -2.3, 0.12), [(1.15, -2.4), (1.04, -1.7)], [(1.25, -2.85), (1.15, -3.15)], [(1.45, -2.85), (1.55, -3.15)]]
    gear = wheel(1.5, -0.85, 0.2, hub=False) + wheel(-0.7, -0.85, 0.2, hub=False) + [[(1.5, -0.6), (1.5, -0.65)]]
    sea = [wave(-3.6, 3.6, -3.35, 0.1, 7, 140), wave(-3.0, 0.0, -2.9, 0.08, 3, 60)]
    return make("Rescue Helicopter", [body, hump, rotor, shield, door] + mast + fenestron + winch + cable + hook + r1 + r2 + gear + sea)


@design("aviation_chinook", T)
def chinook(rng):
    body = chain([(-2.6, 0.9), (1.0, 0.9)], quad((1.0, 0.9), (1.2, 1.35), (1.7, 1.35), 6), [(2.1, 1.35)],
                 cubic((2.1, 1.35), (2.4, 1.3), (3.0, 0.7), (3.0, 0.0), 14), quad((3.0, 0.0), (2.95, -0.6), (2.4, -0.6), 8),
                 [(-2.4, -0.6), (-3.1, 0.2), (-3.1, 0.9), (-2.95, 2.0), (-1.75, 2.0), (-1.55, 0.9)])
    rotors = [tube([(-0.6, 1.55), (3.7, 1.5)], 0.1), tube([(-4.4, 2.18), (-0.3, 2.12)], 0.1),
              [(1.6, 1.35), (1.6, 1.5)], [(-2.35, 2.0), (-2.35, 2.13)]]
    engines = [rrect(-2.55, 1.05, -1.35, 1.38, 0.15)]
    cockpit = poly((2.05, 1.05), (2.65, 1.05), (2.9, 0.45), (2.15, 0.45))
    win = [rrect(x, 0.25, x + 0.28, 0.55, 0.06) for x in (-1.9, -1.3, -0.7, -0.1, 0.5)]
    door = rrect(1.15, -0.4, 1.55, 0.6, 0.06)
    gear = wheel(2.2, -0.85, 0.22, hub=False) + wheel(-1.7, -0.85, 0.22, hub=False) + wheel(-2.2, -0.85, 0.22, hub=False)
    sling = [[(0.3, -0.6), (-0.6, -1.9)], [(0.3, -0.6), (1.2, -1.9)]]
    crate = [rect(-0.8, -2.9, 1.4, -1.9), [(-0.8, -1.9), (1.4, -2.9)], [(-0.8, -2.9), (1.4, -1.9)]]
    return make("Twin-Rotor Helicopter", [body, cockpit, door] + rotors + engines + win + gear + sling + crate)


@design("aviation_drone", T)
def drone(rng):
    body = rrect(-0.75, -0.55, 0.75, 0.55, 0.28)
    lid = circle(0, 0, 0.25, 20)
    parts = [body, lid]
    for sx in (1, -1):
        for sy in (1, -1):
            cx, cy = 1.95 * sx, 1.95 * sy
            parts.append(tube([(0.6 * sx, 0.4 * sy), (cx - 0.22 * sx, cy - 0.22 * sy)], 0.28, cap=False))
            parts += [circle(cx, cy, 0.25, 18), circle(cx, cy, 1.05, 70)]
            a = 0.5 if sx * sy > 0 else -0.5
            parts.append(lens((cx + 0.25 * math.cos(a), cy + 0.25 * math.sin(a)), (cx + 0.95 * math.cos(a), cy + 0.95 * math.sin(a)), 0.13))
            parts.append(lens((cx - 0.25 * math.cos(a), cy - 0.25 * math.sin(a)), (cx - 0.95 * math.cos(a), cy - 0.95 * math.sin(a)), 0.13))
    cam = [rrect(-0.3, -1.0, 0.3, -0.55, 0.08), circle(0, -0.78, 0.14, 12)]
    return make("Quadcopter Drone", parts + cam)


# ------------------------------------------------------------------ people & flying

@design("aviation_formation", T)
def formation(rng):
    pos = [(0.0, 2.0, 0.85), (-1.45, 0.9, 0.75), (1.45, 0.9, 0.75), (-2.8, -0.2, 0.7), (2.8, -0.2, 0.7)]
    parts = []
    for cx, cy, s in pos:
        parts += mini_jet(cx, cy, s)
        y0 = cy - 1.1 * s
        c = [(cx + 0.18 * math.sin(k * 0.9), y0 - 0.3 * k) for k in range(int((y0 + 3.2) / 0.3) + 1)]
        if len(c) > 2:
            parts.append(tube(c, lambda t: 0.12 + 0.35 * t))
    return make("Air Show Formation", parts)


@design("aviation_skydiver", T)
def skydiver(rng):
    torso = ellipse(0, 0, 0.6, 1.05, 60)
    helmet = [circle(0, 1.45, 0.42, 34), arc(0, 1.45, 0.42, math.radians(200), math.radians(340), 10)]
    rig = [rrect(-0.42, -0.6, 0.42, 0.7, 0.15), circle(0.25, -0.75, 0.1, 10)]
    limbs = []
    for sx in (1, -1):
        limbs.append(tube([(0.45 * sx, 0.6), (1.35 * sx, 0.95), (1.55 * sx, 1.85)], 0.36))
        limbs.append(circle(1.6 * sx, 2.08, 0.22, 16))
        limbs.append(tube([(0.3 * sx, -0.85), (1.0 * sx, -1.6), (1.55 * sx, -2.4)], 0.44))
        limbs.append(ellipse(1.68 * sx, -2.62, 0.18, 0.3, 14, rot=0.6 * sx))
    clouds = [cloud(-2.4, -3.0, 0.6), cloud(2.5, 0.0, 0.55), cloud(-2.6, 2.6, 0.45)]
    return make("Skydiver in Freefall", [torso] + helmet + rig + limbs + clouds)


@design("aviation_aviator", T)
def aviator(rng):
    face = [(1.0 * math.cos(t), 0.3 + 1.35 * math.sin(t)) for t in [math.pi + math.pi * i / 40 for i in range(41)]]
    helmet = chain([(0.85, -0.55), (1.18, -0.4), (1.22, 0.0)], arc(0, 0.45, 1.3, math.radians(-20), math.radians(200), 70), [(-1.18, -0.4), (-0.85, -0.55)])
    brim = quad((-1.08, 0.7), (0, 1.0), (1.08, 0.7), 20)
    goggles = [circle(-0.5, 1.25, 0.4, 30), circle(0.5, 1.25, 0.4, 30), circle(-0.5, 1.25, 0.26, 20), circle(0.5, 1.25, 0.26, 20),
               [(-0.1, 1.3), (0.1, 1.3)], [(-0.9, 1.25), (-1.25, 1.1)], [(0.9, 1.25), (1.25, 1.1)]]
    brows = [arc(-0.4, 0.3, 0.3, math.radians(50), math.radians(130), 8), arc(0.4, 0.3, 0.3, math.radians(50), math.radians(130), 8)]
    nose = quad((0.0, 0.3), (0.18, -0.1), (-0.05, -0.15), 8)
    smile = arc(0, -0.25, 0.4, math.radians(220), math.radians(320), 12)
    strap = [[(0.85, -0.55), (0.3, -1.0)], [(-0.85, -0.55), (-0.3, -1.0)]]
    scarf = tube([(-1.0, -1.25), (0.0, -1.4), (1.0, -1.25)], 0.38)
    tail = tube(cubic((0.9, -1.38), (1.7, -0.9), (2.3, -1.9), (3.2, -1.2), 30), lambda t: 0.42 - 0.12 * t)
    jacket = [quad((-1.1, -1.4), (-2.6, -1.6), (-3.0, -3.0), 16), quad((1.1, -1.4), (2.6, -1.6), (3.0, -3.0), 16)]
    collar = [zigzag(-2.4, -0.9, -1.85, 0.1, 5), zigzag(0.9, 2.4, -1.85, 0.1, 5), [(0.0, -1.6), (0.0, -3.0)]]
    return make("Vintage Aviator", [face, helmet, brim, nose, smile, scarf, tail] + goggles + brows + strap + jacket + collar,
                [eye(-0.4, 0.05, 0.08), eye(0.4, 0.05, 0.08)])


@design("aviation_pilot_wings", T)
def pilot_wings(rng):
    def wing():
        tip = (3.4, 0.9)
        top = quad((0.7, 0.3), (1.9, 0.95), tip, 20)
        feathers = []
        base = [(3.4 - 0.45 * k, 0.9 - 0.2 * k) for k in range(7)]
        lows = [(3.15 - 0.45 * k, 0.45 - 0.17 * k) for k in range(6)]
        edge = [tip]
        for k in range(6):
            a, b = base[k], base[k + 1]
            edge += quad(a, (lows[k][0], lows[k][1]), b, 8)[1:]
        for k in range(1, 6):
            feathers.append(quad(base[k], (base[k][0] + 0.2, base[k][1] + 0.3), (base[k][0] + 0.55, base[k][1] + 0.55), 8))
        edge += [(0.7, -0.25)]
        return [top, edge] + feathers
    w = wing()
    parts = w + mirror_all(w)
    parts += [circle(0, 0.1, 0.7, 60), star(0, 0.08, 0.52), [(0.7, 0.3), (0.7, -0.25)], [(-0.7, 0.3), (-0.7, -0.25)]]
    parts += [poly((-0.25, 0.75), (0, 1.2), (0.25, 0.75), closed=False)]
    return make("Pilot Wings Badge", parts)


@design("aviation_captain_hat", T)
def captain_hat(rng):
    crown = ellipse(0, 1.5, 2.7, 0.8, 120)
    sides = [quad((-2.7, 1.5), (-2.5, 0.5), (-2.05, 0.1), 14), quad((2.7, 1.5), (2.5, 0.5), (2.05, 0.1), 14)]
    band = [quad((-2.05, 0.1), (0, -0.25), (2.05, 0.1), 30), quad((-2.0, -0.55), (0, -0.9), (2.0, -0.55), 30), [(-2.05, 0.1), (-2.0, -0.55)], [(2.05, 0.1), (2.0, -0.55)]]
    visor = chain(quad((-2.0, -0.55), (-1.9, -1.6), (0, -1.75), 16), quad((0, -1.75), (1.9, -1.6), (2.0, -0.55), 16))
    cord = [quad((-1.8, -0.25), (0, -0.6), (1.8, -0.25), 30), circle(-1.85, -0.25, 0.14, 12), circle(1.85, -0.25, 0.14, 12)]
    badge = [circle(0, 0.5, 0.38, 30), star(0, 0.5, 0.28)]
    for sx in (1, -1):
        badge.append(chain([(0.38 * sx, 0.6)], quad((0.38 * sx, 0.6), (1.0 * sx, 0.95), (1.5 * sx, 0.9), 10),
                           quad((1.5 * sx, 0.9), (1.0 * sx, 0.45), (0.38 * sx, 0.4), 10)))
        badge.append(quad((0.5 * sx, 0.5), (0.95 * sx, 0.68), (1.3 * sx, 0.8), 8))
    leaves = [lens((x, -1.15), (x + 0.45 * (1 if x > 0 else -1), -1.05), 0.25) for x in (-1.3, -0.7, 0.7, 1.3)]
    return make("Pilot's Captain Hat", [crown, visor] + sides + band + cord + badge + leaves)


@design("aviation_marshal", T)
def marshal(rng):
    head = circle(0, 1.3, 0.4, 34)
    muffs = [rrect(-0.6, 1.05, -0.38, 1.5, 0.1), rrect(0.38, 1.05, 0.6, 1.5, 0.1), arc(0, 1.3, 0.52, math.radians(15), math.radians(165), 16)]
    vest = poly((-0.75, 0.8), (-0.3, 0.8), (0, 0.4), (0.3, 0.8), (0.75, 0.8), (0.68, -1.0), (-0.68, -1.0))
    stripes = [[(-0.72, -0.15), (0.72, -0.15)], [(-0.7, -0.45), (0.7, -0.45)]]
    arms = [tube([(0.68, 0.6), (1.7, 1.95)], 0.3), tube([(-0.68, 0.6), (-1.7, 1.95)], 0.3)]
    paddles = []
    for sx in (1, -1):
        paddles += [circle(1.75 * sx, 2.05, 0.15, 12), [(1.8 * sx, 2.15), (2.05 * sx, 2.45)], circle(2.3 * sx, 2.75, 0.42, 34), circle(2.3 * sx, 2.75, 0.22, 20)]
    legs = [leg(-0.6, -0.1, -1.0, -2.6), leg(0.1, 0.6, -1.0, -2.6)]
    shoes = [ellipse(-0.45, -2.75, 0.4, 0.15, 16), ellipse(0.45, -2.75, 0.4, 0.15, 16)]
    tarmac = [[(-3.2, -2.95), (3.2, -2.95)], [(-1.4, -2.95), (-2.6, -3.6)], [(1.4, -2.95), (2.6, -3.6)]]
    return make("Aircraft Marshaller", [head, vest] + muffs + stripes + arms + paddles + legs + shoes + tarmac,
                [eye(-0.14, 1.38, 0.06), eye(0.14, 1.38, 0.06)])


# ------------------------------------------------------------------ airport

@design("aviation_terminal", T)
def terminal(rng):
    base = [[(-3.4, -1.6), (3.4, -1.6)], [(-3.2, -1.6), (-3.2, 0.6)], [(3.2, -1.6), (3.2, 0.6)]]
    roof = [quad((-3.5, 0.6), (0, 1.6), (3.5, 0.6), 40), quad((-3.5, 0.6), (0, 1.3), (3.5, 0.6), 40)]
    mull = [[(x, -1.6), (x, 0.6 + 0.35 * (1 - (x / 3.5) ** 2))] for x in (-2.4, -1.6, -0.8, 0.8, 1.6, 2.4)]
    trans = [[(-3.2, -0.4), (-0.8, -0.4)], [(0.8, -0.4), (3.2, -0.4)]]
    doors = [rect(-0.6, -1.6, 0.6, -0.2), [(0, -1.6), (0, -0.2)], rect(-0.8, -0.2, 0.8, 0.2)]
    tower = [[(-2.3, 0.85), (-2.2, 2.3)], [(-1.9, 0.92), (-2.0, 2.3)], poly((-2.6, 2.3), (-2.75, 2.85), (-1.45, 2.85), (-1.6, 2.3)),
             rect(-2.7, 2.85, -1.5, 3.0)]
    jet = mini_jet(2.0, 2.4, 0.5, rot=-1.0)
    planters = [arc(x, -1.6, 0.3, 0, math.pi, 10) for x in (-2.8, 2.8)]
    return make("Airport Terminal", base + roof + mull + trans + doors + tower + jet + planters)


@design("aviation_windsock", T)
def windsock(rng):
    pole = [[(-2.2, -2.6), (-2.2, 1.9)], [(-2.0, -2.6), (-2.0, 1.4)], circle(-2.1, 2.0, 0.12, 10)]
    ring = ellipse(-1.75, 1.3, 0.18, 0.62, 30)
    def sockpt(t, side):
        x = -1.75 + 4.6 * t
        yc = 1.3 - 0.45 * t * t
        r = 0.62 - 0.32 * t
        return (x, yc + side * r)
    topl = [sockpt(i / 40, 1) for i in range(41)]
    botl = [sockpt(i / 40, -1) for i in range(41)]
    end = ellipse(sockpt(1, 0)[0], sockpt(1, 0)[1], 0.1, 0.3, 16, start=-math.pi / 2)
    sock = chain(topl, botl[::-1])
    bands = []
    for t in (0.2, 0.4, 0.6, 0.8):
        a, b = sockpt(t, 1), sockpt(t, -1)
        bands.append(quad(a, ((a[0] + b[0]) / 2 + 0.12, (a[1] + b[1]) / 2), b, 10))
    tail = [chain(end[:9])]
    ground = [[(-3.4, -2.6), (3.4, -2.6)], zigzag(-3.2, -0.8, -2.75, 0.1, 8)]
    return make("Windsock", pole + [ring, sock] + bands + tail + ground + [cloud(1.2, 2.6, 0.6), cloud(1.6, -1.4, 0.5)])


@design("aviation_runway", T)
def runway(rng):
    hz = 0.0
    edges = [[(-3.0, -3.2), (-0.35, hz)], [(3.0, -3.2), (0.35, hz)], [(-3.6, hz), (3.6, hz)]]
    def at(t, u):
        # t: 0 bottom .. 1 horizon, u: -1..1 across
        y = -3.2 + (hz + 3.2) * t
        half = 3.0 + (0.35 - 3.0) * t
        return (u * half, y)
    dashes = []
    for t0 in (0.32, 0.55, 0.72):
        t1 = t0 + 0.1
        dashes.append(poly(at(t0, -0.05), at(t0, 0.05), at(t1, 0.05), at(t1, -0.05)))
    keys = [poly(at(0.04, u), at(0.04, u + 0.1), at(0.2, u + 0.1), at(0.2, u)) for u in (-0.85, -0.65, -0.45, 0.35, 0.55, 0.75)]
    lights = [circle(*at(t, s * 1.12), 0.12 - 0.07 * t, 10) for t in (0.0, 0.25, 0.5, 0.7) for s in (-1, 1)]
    plane = _front_airliner(0.5, 0.0, 1.9)
    hills = [quad((-3.6, hz), (-2.6, 0.7), (-1.4, hz), 12), quad((1.6, hz), (2.6, 0.5), (3.6, hz), 12)]
    return make("Runway Approach", edges + dashes + keys + lights + plane + hills + [cloud(-2.4, 2.4, 0.45)])


@design("aviation_radar_dish", T)
def radar_dish(rng):
    rot = 0.5
    cx, cy = 0.2, 0.9
    rim = ellipse(cx, cy, 2.0, 0.9, 120, rot=rot)
    rings = [ellipse(cx, cy, 1.3, 0.58, 90, rot=rot), ellipse(cx, cy, 0.6, 0.27, 40, rot=rot)]
    n = (-math.sin(rot), math.cos(rot))
    feed = (cx + 1.4 * n[0], cy + 1.4 * n[1])
    struts = []
    for t in (0.3, 0.3 + 2 * math.pi / 3, 0.3 + 4 * math.pi / 3):
        x, y = 2.0 * math.cos(t), 0.9 * math.sin(t)
        p = (cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot))
        struts.append([p, feed])
    horn = circle(*feed, 0.14, 12)
    waves = [arc(feed[0], feed[1], r, math.atan2(n[1], n[0]) - 0.45, math.atan2(n[1], n[0]) + 0.45, 12) for r in (0.5, 0.85)]
    mount = [[(cx - 0.9 * n[0] * 0.3, cy - 0.9 * n[1] * 0.3), (0.4, -0.6)]]
    tower = [poly((-0.6, -2.8), (-0.1, -0.6), (0.9, -0.6), (1.4, -2.8), closed=False)]
    lattice = [[(-0.6, -2.8), (1.15, -1.7)], [(1.4, -2.8), (-0.35, -1.7)], [(-0.35, -1.7), (1.15, -1.7)],
               [(-0.35, -1.7), (0.9, -0.6)], [(1.15, -1.7), (-0.1, -0.6)]]
    base = [rect(-1.6, -3.2, 2.4, -2.8)]
    return make("Radar Dish", [rim, horn] + rings + struts + waves + mount + tower + lattice + base)


@design("aviation_cockpit", T)
def cockpit(rng):
    panel = chain([(-3.3, -1.7), (-3.3, 0.7)], quad((-3.3, 0.7), (0, 1.35), (3.3, 0.7), 40), [(3.3, -1.7), (-3.3, -1.7)])
    frame = [poly((-3.3, 0.7), (-2.7, 3.0), (2.7, 3.0), (3.3, 0.7), closed=False), [(0, 1.35), (0, 3.0)]]
    horizon = [[(-2.95, 1.95), (-0.05, 1.95)], [(0.05, 1.95), (2.95, 1.95)], quad((-2.5, 1.95), (-1.8, 2.3), (-1.0, 1.95), 10)]
    gauges = []
    for k, (x, y) in enumerate([(-2.4, 0.3), (-1.45, 0.3), (-0.5, 0.3), (-2.4, -0.7), (-1.45, -0.7), (-0.5, -0.7)]):
        gauges.append(circle(x, y, 0.4, 36))
        a = 0.7 + 1.3 * k
        gauges.append([(x, y), (x + 0.3 * math.cos(a), y + 0.3 * math.sin(a))])
        if k == 1:
            gauges.append([(x - 0.3, y - 0.05), (x + 0.3, y + 0.05)])
        if k == 4:
            gauges += [[(x - 0.22, y), (x + 0.22, y)], [(x, y - 0.15), (x, y + 0.2)]]
    radios = [rect(0.3, 0.35, 1.9, 0.75), rect(0.3, -0.25, 1.9, 0.15), rect(0.3, -0.85, 1.9, -0.45)]
    knobs = [circle(1.65, y, 0.1, 10) for y in (0.55, -0.05, -0.65)]
    small = [circle(2.6, y, 0.25, 22) for y in (0.45, -0.25, -0.95)]
    yoke = tube([(-2.2, -1.1), (-2.15, -1.85), (-1.45, -2.05), (-0.75, -1.85), (-0.7, -1.1)], 0.26)
    column = [[(-1.55, -2.18), (-1.55, -3.0)], [(-1.35, -2.18), (-1.35, -3.0)]]
    throttles = [[(1.0, -1.7), (1.0, -2.4)], circle(1.0, -2.55, 0.15, 12), [(1.5, -1.7), (1.5, -2.2)], circle(1.5, -2.35, 0.15, 12)]
    return make("Cockpit Instrument Panel", [panel, yoke] + frame + horizon + gauges + radios + knobs + small + column + throttles)


@design("aviation_propeller", T)
def propeller(rng):
    angles = [math.pi / 2, math.pi / 2 + 2 * math.pi / 3, math.pi / 2 + 4 * math.pi / 3]
    blades = [blade(0, 0, 3.0, 0.8, a) for a in angles]
    tips = []
    for a in angles:
        c, s_ = math.cos(a), math.sin(a)
        for d in (2.35, 2.6):
            w = 0.36
            tips.append([(d * c - w * -s_, d * s_ + w * c), (d * c + w * -s_, d * s_ - w * c)])
    spinner = [circle(0, 0, 0.6, 40), circle(0, 0, 0.25, 20)]
    cowl = []
    gap = 0.22
    for k in range(3):
        a0 = angles[k] + gap
        a1 = angles[(k + 1) % 3] - gap + (2 * math.pi if k == 2 else 0)
        cowl.append(arc(0, 0, 1.55, a0, a1, 30))
    return make("Propeller Close-Up", blades + tips + spinner + cowl)


@design("aviation_jet_engine", T)
def jet_engine(rng):
    lip = [circle(0, 0, 2.8, 140), circle(0, 0, 2.45, 120)]
    blades = []
    for k in range(18):
        a0 = TAU * k / 18
        blades.append([((0.65 + 1.75 * i / 12) * math.cos(a0 + 0.55 * i / 12), (0.65 + 1.75 * i / 12) * math.sin(a0 + 0.55 * i / 12)) for i in range(13)])
    spinner = [circle(0, 0, 0.65, 40), spiral(0, 0, 0.08, 0.5, 0.9, 40)]
    pylon = [[(-0.35, 2.78), (-0.25, 3.45)], [(0.35, 2.78), (0.25, 3.45)], [(-3.4, 3.45), (3.4, 3.65)]]
    return make("Jet Engine Intake", lip + blades + spinner + pylon)


@design("aviation_window_view", T)
def window_view(rng):
    frame = [rrect(-2.4, -3.0, 2.4, 3.0, 1.75), rrect(-1.9, -2.5, 1.9, 2.5, 1.3)]
    shade = [[(-1.88, 1.55), (1.88, 1.55)], rrect(-0.3, 1.25, 0.3, 1.45, 0.08), [(0, 1.55), (0, 1.45)]]
    wing = poly((-1.9, -0.45), (1.15, -0.95), (1.45, -0.1), (1.7, -0.1), (1.6, -1.15), (-1.83, -1.6), closed=False)
    eng = rrect(-1.0, -2.15, 0.1, -1.65, 0.24)
    sun = [circle(0.9, 0.75, 0.3, 24)] + [[(0.9 + 0.42 * math.cos(a), 0.75 + 0.42 * math.sin(a)), (0.9 + 0.6 * math.cos(a), 0.75 + 0.6 * math.sin(a))]
                                         for a in [k * math.pi / 4 for k in range(8)]]
    clouds = [cloud(-0.8, 0.25, 0.45), cloud(0.7, -2.15, 0.35)]
    return make("View from the Plane Window", frame + shade + [wing, eng] + sun + clouds)


@design("aviation_baggage_tug", T)
def baggage_tug(rng):
    ground = [[(-3.6, -1.5), (3.6, -1.5)]]
    tug = [poly((0.6, -1.05), (0.6, -0.2), (1.5, -0.2), (1.6, 0.25), (2.4, 0.25), (2.5, -0.2), (2.9, -0.35), (2.9, -1.05)),
           [(0.75, 1.15), (2.15, 1.15)], [(0.8, -0.2), (0.8, 1.15)], [(2.1, 0.25), (2.1, 1.15)], rrect(1.05, -0.2, 1.4, 0.55, 0.08),
           [(1.6, 0.25), (1.9, 0.7)], ellipse(1.9, 0.75, 0.2, 0.08, 12)] + wheel(1.0, -1.15, 0.35) + wheel(2.5, -1.15, 0.35)
    carts = []
    for x0 in (-3.4, -1.45):
        carts += [rect(x0, -1.0, x0 + 1.6, -0.82)] + wheel(x0 + 0.35, -1.25, 0.25, hub=False) + wheel(x0 + 1.25, -1.25, 0.25, hub=False)
        carts += [[(x0 + 1.6, -0.95), (x0 + 1.95, -0.95)]]
    bags = [rrect(-3.3, -0.82, -2.6, 0.0, 0.1), rrect(-2.5, -0.82, -1.9, -0.2, 0.1), rrect(-3.2, 0.0, -2.2, 0.55, 0.1),
            rrect(-1.35, -0.82, -0.45, -0.1, 0.1), rrect(-0.4, -0.82, 0.1, -0.35, 0.08), rrect(-1.2, -0.1, -0.3, 0.6, 0.1)]
    handles = [arc(-2.95, 0.0, 0.15, 0, math.pi, 6), arc(-2.7, 0.55, 0.15, 0, math.pi, 6), arc(-0.75, 0.6, 0.15, 0, math.pi, 6),
               arc(-2.2, -0.2, 0.12, 0, math.pi, 6)]
    tags = [[(-0.9, -0.1), (-0.9, -0.45)], [(-2.9, -0.82), (-2.9, 0.0)]]
    return make("Baggage Tug and Carts", ground + tug + carts + bags + handles + tags + [mini_jet(2.6, 2.4, 0.45, rot=-1.2)[0], mini_jet(2.6, 2.4, 0.45, rot=-1.2)[1]])


@design("aviation_boarding_stairs", T)
def boarding_stairs(rng):
    fus = chain([(3.6, 2.4), (1.0, 2.4)], cubic((1.0, 2.4), (0.0, 2.4), (-0.75, 1.75), (-0.8, 1.2), 16),
                cubic((-0.8, 1.2), (-0.75, 0.55), (0.2, 0.2), (1.0, 0.2), 14), [(3.6, 0.2)])
    cockpit = poly((-0.3, 1.75), (0.15, 2.0), (0.6, 2.0), (0.6, 1.75))
    door = rrect(1.55, 0.55, 2.15, 2.0, 0.12)
    win = windows(2.6, 3.4, 1.45, 0.11, 0.4)
    steps = [(-1.3, -1.8)]
    x, y = -1.3, -1.8
    for k in range(8):
        y += 0.29
        steps.append((x, y))
        x += 0.36
        steps.append((x, y))
    steps.append((1.55, steps[-1][1]))
    under = [[(-1.3, -1.8), (1.55, 0.45)]]
    rail = [[(-1.2, -0.95), (1.4, 1.35)]] + [[(-1.2 + 0.65 * k, -0.95 + 0.575 * k), (-1.2 + 0.65 * k, -0.95 + 0.575 * k - 0.85)] for k in range(5)]
    truck = [rect(-2.6, -2.15, 1.9, -1.8), rrect(-3.4, -2.15, -2.3, -0.9, 0.15), rect(-3.2, -1.55, -2.55, -1.05),
             [(0.3, -1.8), (0.6, -0.1)], [(1.4, -1.8), (1.4, 0.45)]]
    wheels = wheel(-2.8, -2.3, 0.32) + wheel(1.2, -2.3, 0.32)
    ground = [[(-3.6, -2.62), (3.6, -2.62)]]
    return make("Boarding Stairs", [fus, cockpit, door, steps] + win + under + rail + truck + wheels + ground)


@design("aviation_hangar", T)
def hangar(rng):
    outer = arc(0, -1.8, 3.1, 0, math.pi, 90)
    inner = arc(0, -1.8, 2.8, 0, math.pi, 80)
    base = [[(-3.5, -1.8), (3.5, -1.8)]]
    opening = poly((-2.2, -1.8), (-2.2, 0.2), (2.2, 0.2), (2.2, -1.8), closed=False)
    ribs = [[(x, 0.2), (x, -1.8 + math.sqrt(2.8 ** 2 - x * x))] for x in (-1.6, -0.8, 0.0, 0.8, 1.6)]
    doors = [[(-2.2, 0.0), (-2.75, 0.0)], [(2.2, 0.0), (2.75, 0.0)], [(-2.5, 0.0), (-2.5, -1.8)], [(2.5, 0.0), (2.5, -1.8)]]
    fus = circle(0, -0.85, 0.42, 36)
    wings = [[(-0.42, -0.95), (-1.95, -0.8)], [(-1.95, -0.8), (-1.95, -0.65)], [(-1.95, -0.65), (-0.4, -0.75)],
             [(0.42, -0.95), (1.95, -0.8)], [(1.95, -0.8), (1.95, -0.65)], [(1.95, -0.65), (0.4, -0.75)]]
    prop = [lens((0, -0.85), (-0.9, -0.15), 0.09), lens((0, -0.85), (0.9, -1.55), 0.09), circle(0, -0.85, 0.12, 10)]
    fin = [poly((-0.06, -0.43), (0, 0.1), (0.06, -0.43), closed=False)]
    gear = [[(-0.3, -1.2), (-0.6, -1.55)], [(0.3, -1.2), (0.6, -1.55)], rrect(-0.72, -1.8, -0.5, -1.45, 0.08), rrect(0.5, -1.8, 0.72, -1.45, 0.08)]
    sock = [[(3.3, -1.8), (3.3, 0.6)], poly((3.3, 0.6), (3.95, 0.45), (3.95, 0.25), (3.3, 0.2), closed=False)]
    return make("Aircraft Hangar", [outer, inner, opening, fus] + base + ribs + doors + wings + prop + fin + gear + sock + [cloud(-2.6, 2.0, 0.5)])


# ------------------------------------------------------------------ more aircraft

@design("aviation_dc3", T)
def dc3(rng):
    body = fuselage(-3.0, 3.0, 0.95, nose=1.1, tail=1.9, end=0.3)
    fin = chain([(-1.85, 0.475)], quad((-1.85, 0.475), (-2.5, 1.95), (-2.95, 1.85), 12), quad((-2.95, 1.85), (-3.15, 1.6), (-3.0, 0.475), 8))
    stab = lens((-2.3, 0.2), (-3.5, 0.25), 0.1)
    wing = poly((0.9, -0.3), (0.2, -1.8), (-0.7, -1.8), (-0.45, -0.4), closed=False)
    nac = [rrect(0.45, -1.1, 1.75, -0.55, 0.25), lens((1.85, -0.82), (1.85, 0.35), 0.1), lens((1.85, -0.82), (1.85, -2.0), 0.1)]
    win = [rrect(x, -0.02, x + 0.22, 0.25, 0.06) for x in (-1.6, -1.15, -0.7, -0.25, 0.2, 0.65, 1.1)]
    cockpit = poly((2.2, 0.2), (2.65, 0.18), (2.9, 0.0), (2.25, 0.0))
    door = rrect(-2.2, -0.3, -1.95, 0.3, 0.06)
    gear = [[(0.8, -1.1), (0.75, -1.7)]] + wheel(0.75, -2.05, 0.38) + [[(-2.6, -0.2), (-2.65, -0.55)], circle(-2.65, -0.68, 0.13, 12)]
    rot = math.radians(7)
    parts = [transform(p, rot=rot) for p in [body, fin, stab, wing, cockpit, door] + nac + win + gear]
    gy = min(y for p in parts for _, y in p)
    return make("Vintage Twin-Prop Airliner", parts + [[(-3.6, gy), (3.6, gy)]])


@design("aviation_bizjet", T)
def bizjet(rng):
    body = fuselage(-3.0, 3.0, 0.75, nose=1.2, tail=1.7, end=0.2)
    fin = poly((-1.9, 0.375), (-2.75, 1.9), (-3.15, 1.9), (-2.95, 0.375), closed=False)
    stab = lens((-2.35, 1.92), (-3.6, 1.98), 0.07)
    eng = [rrect(-2.1, 0.15, -0.95, 0.6, 0.2), ellipse(-0.95, 0.375, 0.07, 0.2, 12)]
    win = [ellipse(x, 0.12, 0.09, 0.13, 12) for x in (-0.6, -0.2, 0.2, 0.6, 1.0, 1.4)]
    cockpit = poly((2.0, 0.15), (2.4, 0.12), (2.65, -0.02), (2.05, -0.02))
    wing = poly((0.9, -0.3), (-0.3, -1.65), (-0.55, -1.95), (-0.65, -1.65), (-0.35, -0.33), closed=False)
    door = rrect(1.4, -0.28, 1.62, 0.28, 0.07)
    stripe = [quad((-2.5, -0.15), (0, -0.25), (2.6, -0.1), 20)]
    return make("Private Business Jet", [body, fin, stab, cockpit, wing, door] + eng + win + stripe + [cloud(1.8, -1.8, 0.7), cloud(-1.6, 2.2, 0.5)])


@design("aviation_water_bomber", T)
def water_bomber(rng):
    hull = chain([(-2.6, 1.45), (1.3, 1.45)], quad((1.3, 1.45), (2.25, 1.35), (2.4, 0.85), 10), quad((2.4, 0.85), (2.2, 0.3), (1.5, 0.3), 8),
                 [(0.1, 0.3), (0.0, 0.45), (-2.6, 1.15), (-2.6, 1.45)])
    wing = chain([(-0.6, 1.45)], quad((-0.6, 1.45), (-0.5, 1.75), (0.0, 1.75), 8), [(0.9, 1.75)], quad((0.9, 1.75), (1.2, 1.7), (1.25, 1.45), 6))
    fin = poly((-1.85, 1.45), (-2.45, 2.75), (-2.85, 2.75), (-2.6, 1.45), closed=False)
    stab = lens((-2.2, 2.75), (-3.25, 2.8), 0.07)
    nac = [rrect(0.0, 1.55, 1.35, 1.9, 0.15), lens((1.45, 1.72), (1.45, 2.65), 0.1), lens((1.45, 1.72), (1.45, 0.8), 0.1)]
    cockpit = poly((1.55, 1.3), (2.05, 1.3), (2.25, 1.0), (1.6, 1.0))
    win = [circle(x, 0.95, 0.1, 10) for x in (-1.2, -0.75, -0.3, 0.15, 0.6)]
    water = [quad((x, 0.3 + 0.02 * k), (x - 0.4, -0.5), (x - 1.3 + 0.2 * k, -1.6 - 0.2 * k), 16) for k, x in enumerate((-0.2, 0.25, 0.7, 1.1))]
    drops = [circle(x, y, 0.08, 8) for x, y in [(-1.6, -1.4), (-1.1, -1.9), (-0.5, -2.0), (0.1, -1.7), (-2.0, -0.9)]]
    def tree(x, h):
        return [poly((x - 0.35, -2.9), (x, -2.9 + h), (x + 0.35, -2.9)), [(x, -2.9), (x, -3.15)]]
    def flame(cx, h):
        return chain(quad((cx - 0.3, -2.9), (cx - 0.45, -2.9 + h * 0.6), (cx, -2.9 + h), 10), quad((cx, -2.9 + h), (cx + 0.05, -2.9 + h * 0.4), (cx + 0.3, -2.9), 10))
    forest = tree(-3.0, 1.1) + tree(-1.4, 1.3) + tree(0.6, 1.0) + tree(2.6, 1.2) + [flame(-2.2, 0.9), flame(-0.4, 1.1), flame(1.6, 0.9), flame(3.3, 0.7)]
    ground = [[(-3.6, -3.15), (3.6, -3.15)]]
    return make("Water Bomber", [hull, wing, fin, stab, cockpit] + nac + win + water + drops + forest + ground)


@design("aviation_banner_plane", T)
def banner_plane(rng):
    plane = [transform(p, dx=2.0, dy=1.6, s=0.45) for p in _cessna_parts(gear=False)]
    top = wave(-3.5, 0.4, 0.6, 0.12, 2.0, 60)
    bot = wave(-3.5, 0.4, -0.7, 0.12, 2.0, 60)
    banner = chain(top, [bot[-1]], bot[::-1], [(-3.85, -0.05), top[0]])
    pole = [[(0.45, 0.85), (0.45, -0.95)]]
    rope = [[(0.45, 0.85), (0.6, 1.8)]]
    heart_ = heart(-1.55, 0.0, 0.45)
    stars_ = [star(-2.7, -0.05, 0.3), star(-0.4, -0.05, 0.3)]
    return make("Banner Towing Plane", plane + [banner, heart_] + pole + rope + stars_ + [cloud(-2.0, 2.2, 0.55), cloud(1.6, -2.0, 0.6)])


# ------------------------------------------------------------------ fun & decor

@design("aviation_kite", T)
def kite(rng):
    k = poly((0, 2.9), (1.5, 1.5), (0, -0.7), (-1.5, 1.5))
    spars = [[(0, 2.9), (0, -0.7)], [(-1.5, 1.5), (1.5, 1.5)]]
    tail = [(0.05 * math.sin(i * 0.5) + 0.0 + 1.9 * i / 40 + 0.35 * math.sin(i / 40 * 2 * math.pi * 1.2), -0.7 - 2.5 * i / 40) for i in range(41)]
    bows = []
    for i in (10, 20, 30):
        x, y = tail[i]
        bows.append(poly((x - 0.32, y + 0.2), (x + 0.32, y - 0.2), (x + 0.32, y + 0.2), (x - 0.32, y - 0.2)))
    string = [quad((0, 1.5), (-1.6, 0.0), (-3.0, -3.2), 20)]
    sun = [circle(2.4, 2.5, 0.45, 30)]
    clouds = [cloud(-2.2, 2.5, 0.55), cloud(2.4, -0.4, 0.5)]
    return make("Diamond Kite", [k, tail] + spars + bows + string + sun + clouds)


@design("aviation_weather_vane", T)
def weather_vane(rng):
    rod = [[(0, -2.0), (0, 1.1)]]
    plane = [chain([(-2.0, 1.55), (-2.0, 1.25), (1.2, 1.15)], quad((1.2, 1.15), (1.75, 1.2), (1.8, 1.45), 8), quad((1.8, 1.45), (1.75, 1.75), (1.2, 1.75), 8), [(-2.0, 1.55)]),
             poly((-1.4, 1.6), (-1.9, 2.4), (-2.25, 2.4), (-2.0, 1.55), closed=False), lens((0.6, 1.45), (-0.5, 1.45), 0.13),
             lens((1.9, 1.45), (1.9, 2.15), 0.13), lens((1.9, 1.45), (1.9, 0.75), 0.13), arc(0.7, 1.75, 0.3, 0, math.pi, 10)]
    ball = [circle(0, 0.45, 0.25, 20)]
    arms = [[(-2.0, -0.4), (2.0, -0.4)], [(-0.9, -0.95), (0.9, 0.15)]]
    ends = [poly((2.0, -0.25), (2.35, -0.4), (2.0, -0.55)), poly((-2.0, -0.25), (-2.35, -0.4), (-2.0, -0.55)),
            circle(0.98, 0.2, 0.12, 10), circle(-0.98, -1.0, 0.12, 10)]
    roof = [[(-3.2, -3.2), (0, -2.0), (3.2, -3.2)], [(-0.25, -2.1), (0.25, -2.1)]]
    shingles = [[(-2.0, -2.72), (-1.6, -2.56)], [(-1.0, -2.6), (-0.6, -2.44)], [(1.0, -2.6), (1.4, -2.76)], [(2.0, -2.84), (2.4, -3.0)]]
    return make("Airplane Weather Vane", rod + plane + ball + arms + ends + roof + shingles + [cloud(2.3, 2.9, 0.4)])


@design("aviation_toy_plane", T)
def toy_plane(rng):
    body = rrect(-2.4, -0.4, 1.8, 0.75, 0.5)
    nose = arc(1.8, 0.175, 0.45, -math.pi / 2, math.pi / 2, 14)
    hub = circle(2.35, 0.175, 0.15, 12)
    prop = [lens((2.35, 0.33), (2.35, 1.4), 0.15), lens((2.35, 0.02), (2.35, -1.05), 0.15)]
    wing = [circle(x, 0.2, 0.2, 18) for x in (-1.3, -0.6, 0.1, 0.8)]
    fin = chain([(-1.6, 0.75)], quad((-1.6, 0.75), (-2.0, 1.8), (-2.45, 1.75), 10), quad((-2.45, 1.75), (-2.7, 1.5), (-2.4, 0.5), 8))
    pilot = [chain(arc(0.1, 1.1, 0.35, -0.3, math.pi + 0.3, 20)), [(-0.4, 0.75), (0.6, 0.75)]]
    wheels = wheel(-0.2, -0.95, 0.5) + wheel(1.1, -0.95, 0.5)
    axle = [[(-0.2, -0.45), (-0.2, -0.4)]]
    grain = [wave(-2.0, -0.6, -0.2, 0.05, 1.5, 24), wave(0.2, 1.5, 0.55, 0.05, 1.5, 24)]
    string = [cubic((2.45, -0.4), (2.9, -1.5), (1.8, -1.8), (3.2, -2.4), 24), circle(3.3, -2.5, 0.14, 12)]
    floor = [[(-3.0, -1.45), (2.6, -1.45)]]
    return make("Wooden Toy Plane", [body, nose, hub, fin] + wing + prop + pilot + wheels + axle + grain + string + floor,
                [eye(0.0, 1.15, 0.05), eye(0.2, 1.15, 0.05)])
