"""Cars & Trucks niche, part 2 (pictures 10-55)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "vehicles"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


def wheel(cx, cy, r, hub=0.5, spokes=0, wall=False):
    """Tyre + rim (+ optional whitewall ring and spokes)."""
    out = [circle(cx, cy, r, 60), circle(cx, cy, r * hub, 36)]
    if wall:
        out.append(circle(cx, cy, r * 0.76, 44))
    if spokes:
        h = r * 0.16
        out.append(circle(cx, cy, h, 12))
        out += [[(cx + h * math.cos(a), cy + h * math.sin(a)), (cx + r * hub * math.cos(a), cy + r * hub * math.sin(a))]
                for a in [k * TAU / spokes for k in range(spokes)]]
    return out


def knobby(cx, cy, r, hub=0.5):
    """Off-road tyre: chunky tread blocks on the rim plus a sidewall ring."""
    knobs = max(16, int(r * 26))
    d = 0.07 * r + 0.02
    pts = []
    for k in range(knobs):
        a0 = TAU * k / knobs
        a1 = a0 + TAU / knobs * 0.6
        a2 = a0 + TAU / knobs
        pts += arc(cx, cy, r, a0, a1, 3) + arc(cx, cy, r - d, a1, a2, 3)
    pts.append(pts[0])
    return [chain(pts), circle(cx, cy, r * 0.8, 50), circle(cx, cy, r * hub, 36), circle(cx, cy, r * hub * 0.35, 14)]


def under(x1, x0, y, wheels, gap=0.1):
    """Body underside from x1 (right) back to x0 (left) with wheel arches."""
    pts = [(x1, y)]
    for cx, r in sorted(wheels, reverse=True):
        pts += arc(cx, y, r + gap, 0, math.pi, 20)
    pts.append((x0, y))
    return pts


def body(top, y, wheels, gap=0.1):
    """Closed body: `top` runs left-bottom -> over the roof -> right-bottom."""
    return chain(top, under(top[-1][0], top[0][0], y, wheels, gap), [top[0]])


def wheels_at(wh, y, **kw):
    out = []
    for cx, r in wh:
        out += wheel(cx, y, r, **kw)
    return out


def tracks(x0, x1, y0, y1, rollers=5):
    """Crawler track: stadium outline, inner belt and road wheels."""
    r = (y1 - y0) / 2
    out = [rrect(x0, y0, x1, y1, r), rrect(x0 + 0.12, y0 + 0.12, x1 - 0.12, y1 - 0.12, r - 0.12)]
    out += [circle(x0 + r, y0 + r, r * 0.6, 24), circle(x1 - r, y0 + r, r * 0.6, 24)]
    for k in range(1, rollers - 1):
        x = x0 + r + (x1 - x0 - 2 * r) * k / (rollers - 1)
        out.append(circle(x, y0 + r * 0.75, r * 0.4, 18))
    return out


def ground(x0=-3.6, x1=3.6, y=-1.3):
    return [(x0, y), (x1, y)]


def mini_car(cx, cy, s):
    """Small side-view car silhouette (for transporters, tow trucks)."""
    top = [(-1.0, 0.0), (-1.0, 0.35), (-0.55, 0.4), (-0.3, 0.75), (0.35, 0.75), (0.6, 0.4), (1.0, 0.3), (1.0, 0.0)]
    b = body(top, 0.0, [(-0.6, 0.22), (0.6, 0.22)], 0.05)
    win = poly((-0.22, 0.42), (-0.12, 0.66), (0.3, 0.66), (0.45, 0.42))
    parts = [b, win, circle(-0.6, 0.0, 0.22, 20), circle(0.6, 0.0, 0.22, 20)]
    return [transform(p, dx=cx, dy=cy, s=s) for p in parts]


# ---------------------------------------------------------------- cars

@design("vehicles_convertible", T)
def convertible(rng):
    y, wh = -0.5, [(-2.0, 0.55), (2.0, 0.55)]
    top = chain([(-3.3, y), (-3.3, 0.25), (-3.1, 0.8), (-2.3, 0.35), (1.0, 0.35)],
                quad((1.0, 0.35), (2.0, 0.42), (2.9, 0.3), 10), quad((2.9, 0.3), (3.4, 0.2), (3.4, y), 8))
    seats = [quad((-1.6, 0.35), (-1.3, 1.2), (-0.9, 0.35), 12), quad((-0.4, 0.35), (-0.1, 1.2), (0.3, 0.35), 12)]
    screen = poly((0.8, 0.35), (1.1, 1.2), (1.45, 1.2), (1.15, 0.35))
    spear = [poly((-2.9, 0.0), (-1.0, 0.12), (2.7, 0.0), closed=False)]
    bumpers = [rrect(3.25, -0.6, 3.6, -0.25, 0.1), rrect(-3.6, -0.6, -3.25, -0.25, 0.1)]
    lights = [ellipse(3.2, 0.05, 0.1, 0.16, 12), lens((-3.25, 0.3), (-3.15, 0.65), 0.4)]
    return make("Classic Convertible", [body(top, y, wh), screen] + seats + spear + bumpers + lights + wheels_at(wh, y, wall=True))


@design("vehicles_muscle_car", T)
def muscle_car(rng):
    y, wh = -0.45, [(-2.1, 0.62), (2.0, 0.58)]
    top = [(-3.3, y), (-3.3, 0.4), (-2.1, 0.5), (-1.0, 1.2), (0.3, 1.2), (1.1, 0.55), (3.2, 0.42), (3.3, y)]
    win = poly((-1.6, 0.6), (-0.95, 1.08), (-0.1, 1.08), (-0.1, 0.6))
    win2 = poly((0.05, 0.6), (0.05, 1.08), (0.3, 1.08), (0.85, 0.6))
    scoop = poly((1.6, 0.5), (1.9, 0.75), (2.6, 0.75), (2.6, 0.46), closed=False)
    stripes = [[(-3.3, 0.05), (3.3, 0.05)], [(-3.3, -0.12), (3.3, -0.12)]]
    spoiler = [poly((-3.0, 0.43), (-3.0, 0.7), (-3.5, 0.75), (-3.5, 0.62), (-2.7, 0.55), closed=False)]
    exhaust = [rrect(-3.65, -0.62, -3.3, -0.45, 0.08)]
    return make("American Muscle Car", [body(top, y, wh), win, win2, scoop] + stripes + spoiler + exhaust + wheels_at(wh, y, spokes=5))


@design("vehicles_sports_car", T)
def sports_car(rng):
    y, wh = -0.35, [(-2.0, 0.55), (2.1, 0.52)]
    top = chain([(-3.3, y), (-3.3, 0.35), (-2.4, 0.55)], cubic((-2.4, 0.55), (-1.4, 1.2), (0.2, 1.25), (1.1, 0.55), 30),
                cubic((1.1, 0.55), (2.0, 0.45), (3.0, 0.3), (3.4, 0.0), 14), [(3.4, y)])
    win = chain(cubic((-1.6, 0.6), (-1.0, 1.05), (0.1, 1.1), (0.8, 0.6), 20), [(-1.6, 0.6)])
    intake = lens((-1.4, 0.0), (0.2, 0.25), 0.18)
    wing = [poly((-3.0, 0.45), (-3.0, 0.85), closed=False), rrect(-3.6, 0.85, -2.5, 1.0, 0.07)]
    light = [lens((2.6, 0.32), (3.25, 0.1), 0.2)]
    return make("Sleek Sports Car", [body(top, y, wh), win, intake] + wing + light + wheels_at(wh, y, spokes=5))


@design("vehicles_vintage_roadster", T)
def vintage_roadster(rng):
    wy, r = -1.0, 0.72
    tub = poly((0.5, -0.45), (-2.8, -0.45), (-2.95, 0.6), (0.5, 0.6), closed=False)
    door = [rect(-1.3, -0.3, -0.2, 0.5), [(-0.45, 0.2), (-0.3, 0.2)]]
    hood = poly((0.5, -0.45), (0.5, 0.75), (1.95, 0.75), (1.95, -0.45), closed=False)
    louvers = [[(x, -0.15), (x, 0.45)] for x in (0.9, 1.15, 1.4, 1.65)]
    radiator = [rrect(1.95, -0.5, 2.3, 1.05, 0.08), circle(2.12, 1.2, 0.12, 10)]
    roof = [rrect(-3.0, 2.0, 0.65, 2.25, 0.08), [(-2.85, 0.6), (-2.85, 2.0)], [(-1.2, 0.6), (-1.2, 2.0)], [(0.5, 0.75), (0.5, 2.0)],
            [(0.5, 1.4), (0.75, 1.4)]]
    steer = [[(0.2, 0.75), (-0.15, 1.25)], ellipse(-0.18, 1.28, 0.32, 0.08, 14, rot=-0.15)]
    fenders = [chain([(1.1, -0.55)], arc(1.9, wy, 0.86, math.pi - 0.55, 0.05, 20)), chain(arc(-2.0, wy, 0.86, math.pi - 0.05, 0.55, 20), [(-1.2, -0.55)])]
    board = [[(-1.2, -0.55), (1.1, -0.55)]]
    lamp = [circle(2.6, 0.9, 0.24, 18), [(2.3, 0.7), (2.45, 0.75)]]
    spare = [circle(-3.3, -0.1, 0.55, 40), circle(-3.3, -0.1, 0.35, 30)]
    wh = wheel(-2.0, wy, r, hub=0.82, spokes=12) + wheel(1.9, wy, r, hub=0.82, spokes=12)
    return make("1920s Vintage Roadster", [tub, hood] + door + louvers + radiator + roof + steer + fenders + board + lamp + spare + wh)


@design("vehicles_woodie_wagon", T)
def woodie_wagon(rng):
    y, wh = -0.4, [(-2.1, 0.55), (2.0, 0.55)]
    top = [(-3.3, y), (-3.3, 1.3), (0.5, 1.35), (1.2, 0.6), (3.2, 0.45), (3.3, y)]
    wins = [poly((-3.1, 0.65), (-3.1, 1.15), (-1.9, 1.15), (-1.9, 0.65)), rect(-1.7, 0.65, -0.6, 1.15), poly((-0.4, 0.65), (-0.4, 1.15), (0.4, 1.15), (0.9, 0.65))]
    wood = [rrect(-3.1, -0.3, -1.4, 0.5, 0.12), rrect(-1.3, -0.3, 0.6, 0.5, 0.12)]
    board = lens((-3.4, 1.75), (0.8, 1.75), 0.08)
    rack = [[(-3.0, 1.32), (-3.0, 1.62)], [(0.0, 1.35), (0.0, 1.62)]]
    return make("Woodie Wagon with Surfboard", [body(top, y, wh), board] + wins + wood + rack + wheels_at(wh, y, wall=True))


@design("vehicles_minivan", T)
def minivan(rng):
    y, wh = -0.5, [(-2.0, 0.55), (2.0, 0.55)]
    top = chain([(-3.2, y), (-3.2, 1.2)], quad((-3.2, 1.5), (-3.0, 1.65), (-2.6, 1.65), 6), [(0.6, 1.65), (2.3, 0.5), (3.2, 0.35)],
                quad((3.2, 0.35), (3.35, 0.2), (3.35, y), 5))
    wins = [rrect(-3.0, 0.7, -2.1, 1.45, 0.15), rect(-1.9, 0.7, -0.6, 1.45), rect(-0.4, 0.7, 0.4, 1.45), poly((0.6, 0.7), (0.6, 1.45), (1.6, 0.7))]
    door = [[(-0.5, 0.7), (-0.5, -0.4)], [(0.5, 0.7), (0.5, -0.4)], [(-1.9, 0.55), (-0.6, 0.55)], [(-0.9, 0.2), (-0.7, 0.2)]]
    light = [lens((2.7, 0.35), (3.25, 0.28), 0.25)]
    return make("Family Minivan", [body(top, y, wh)] + wins + door + light + wheels_at(wh, y))


@design("vehicles_suv", T)
def suv(rng):
    y, wh = -0.3, [(-2.0, 0.66), (2.0, 0.66)]
    top = [(-3.1, y), (-3.1, 1.6), (0.7, 1.65), (1.5, 0.8), (3.1, 0.65), (3.15, y)]
    wins = [rect(-2.9, 0.85, -1.9, 1.4), rect(-1.7, 0.85, -0.5, 1.4), poly((-0.3, 0.85), (-0.3, 1.4), (0.6, 1.4), (1.2, 0.85))]
    roof = [[(-2.8, 1.65), (-2.8, 1.85)], [(0.2, 1.65), (0.2, 1.85)], [(-3.0, 1.85), (0.5, 1.85)], rrect(-2.4, 1.85, -0.2, 2.35, 0.2)]
    trim = [[(-3.1, 0.1), (3.15, 0.1)], [(-0.4, 0.8), (-0.4, -0.2)]]
    bars = [rrect(3.0, -0.35, 3.35, 0.6, 0.08)]
    return make("SUV with Roof Box", [body(top, y, wh)] + wins + roof + trim + bars + wheels_at(wh, y, spokes=6))


@design("vehicles_jeep", T)
def jeep(rng):
    y, wh = -0.6, [(-1.8, 0.75), (1.9, 0.75)]
    top = [(-2.6, y), (-2.6, 0.7), (-0.4, 0.7), (-0.4, 0.25), (0.6, 0.25), (0.6, 0.75), (2.9, 0.75), (2.95, y)]
    screen = [poly((0.65, 0.75), (0.8, 1.75), (0.95, 1.75), (0.85, 0.75), closed=False), [(0.8, 1.75), (0.6, 1.75)]]
    rollbar = [poly((-2.0, 0.7), (-1.9, 1.75), (-0.5, 1.75), (-0.4, 0.7), closed=False)]
    spare = knobby(-3.3, 0.15, 0.6)
    flares = [arc(-1.8, y, 0.95, 0, math.pi, 20), arc(1.9, y, 0.95, 0, math.pi, 20)]
    grille = [[(x, 0.0), (x, 0.6)] for x in (2.95,)]
    lamp = [circle(2.7, 0.45, 0.17, 14)]
    return make("Off-Road Jeep", [body(top, y, wh, 0.12)] + screen + rollbar + spare + flares + grille + lamp
                + knobby(-1.8, y, 0.75) + knobby(1.9, y, 0.75) + [ground(-3.6, 3.4, y - 0.75)])


@design("vehicles_camper_van", T)
def camper_van(rng):
    y, wh = -0.5, [(-2.0, 0.55), (2.0, 0.55)]
    top = chain([(-3.2, y), (-3.2, 1.8)], arc(-2.6, 1.8, 0.6, math.pi, math.pi / 2, 8), [(2.3, 2.4)],
                quad((2.3, 2.4), (3.25, 2.4), (3.3, 1.2), 12), [(3.3, y)])
    tone = [[(-3.2, 0.9), (3.3, 0.9)]]
    wins = [rrect(-2.9 + 1.05 * k, 1.3, -2.1 + 1.05 * k, 2.1, 0.15) for k in range(4)] + [poly((1.4, 1.3), (1.4, 2.1), (2.6, 2.1), (3.0, 1.3))]
    curtains = [arc(-2.5 + 1.05 * k, 2.1, 0.4, math.pi, 1.5 * math.pi, 8) for k in range(4)]
    door = [rect(0.3, -0.35, 1.3, 0.85), [(0.4, 0.4), (0.6, 0.4)]]
    flower = [circle(-0.6, 0.3, 0.13, 12)] + [lens((-0.6, 0.3), (-0.6 + 0.45 * math.cos(a), 0.3 + 0.45 * math.sin(a)), 0.3) for a in [k * TAU / 5 + 0.3 for k in range(5)]]
    bumpers = [rrect(-3.45, -0.6, -3.15, -0.2, 0.08), rrect(3.25, -0.6, 3.55, -0.2, 0.08)]
    lamp = [circle(3.15, 0.45, 0.15, 12)]
    rack = [[(-2.6, 2.4), (-2.6, 2.6)], [(1.2, 2.4), (1.2, 2.6)], [(-2.9, 2.6), (1.5, 2.6)], rrect(-2.2, 2.6, -0.3, 3.0, 0.15), rect(0.0, 2.6, 1.0, 2.9)]
    return make("Hippie Camper Van", [body(top, y, wh)] + tone + wins + curtains + door + flower + bumpers + lamp + rack + wheels_at(wh, y, hub=0.6))


@design("vehicles_rv", T)
def rv_motorhome(rng):
    y, wh = -0.6, [(-2.2, 0.5), (2.3, 0.5)]
    top = [(-3.5, y), (-3.5, 2.1), (1.4, 2.1), (2.3, 1.95), (2.3, 1.3), (1.9, 1.3), (2.7, 0.55), (3.3, 0.4), (3.35, y)]
    wins = [rrect(-3.2, 0.9, -2.0, 1.6, 0.12), rrect(-0.6, 0.9, 0.6, 1.6, 0.12), poly((1.85, 1.2), (2.55, 0.55), (1.85, 0.55))]
    door = [rect(-1.7, -0.4, -1.0, 1.7), circle(-1.35, 1.35, 0.15, 12), [(-1.15, 0.6), (-1.05, 0.6)]]
    awning = [poly((-3.3, 1.75), (-3.0, 1.9), (0.9, 1.9), (1.1, 1.75), closed=False)]
    ac = [rrect(-1.4, 2.1, -0.3, 2.45, 0.1)]
    ladder = [[(-3.6, 2.2), (-3.6, -0.2)]] + [[(-3.6, yy), (-3.5, yy)] for yy in (0.3, 0.9, 1.5)]
    stripe = [wave(-3.5, 1.7, 0.4, 0.1, 2.5)]
    return make("RV Motorhome", [body(top, y, wh)] + wins + door + awning + ac + ladder + stripe + wheels_at(wh, y))


# ---------------------------------------------------------------- vans & trucks

@design("vehicles_ice_cream_truck", T)
def ice_cream_truck(rng):
    y, wh = -0.6, [(-2.2, 0.55), (2.1, 0.55)]
    top = [(-3.3, y), (-3.3, 1.8), (1.4, 1.8), (1.4, 1.0), (2.4, 1.0), (2.9, 0.5), (3.3, 0.4), (3.3, y)]
    win = poly((1.55, 0.95), (2.35, 0.95), (2.75, 0.5), (1.55, 0.5))
    hatch = rect(-2.4, 0.2, 0.6, 1.3)
    awning = [chain([(-2.6, 1.6), (0.8, 1.6)], [(0.8, 1.6)], *[arc(0.8 - 0.34 * (k + 0.5), 1.6, 0.17, 0, -math.pi, 6) for k in range(10)])]
    sign_cone = [poly((-0.5, 1.8), (0.1, 3.2), (-1.1, 3.2)), circle(-0.5, 3.4, 0.55, 30), circle(-0.5, 3.95, 0.12, 10)]
    pops = [rrect(-2.2, -0.4, -1.6, 0.0, 0.15), rrect(-1.2, -0.4, -0.6, 0.0, 0.15), [(-1.9, -0.4), (-1.9, -0.55)], [(-0.9, -0.4), (-0.9, -0.55)]]
    return make("Ice Cream Truck", [body(top, y, wh), win, hatch] + awning + sign_cone + pops + wheels_at(wh, y))


@design("vehicles_food_truck", T)
def food_truck(rng):
    y, wh = -0.6, [(-2.2, 0.55), (2.1, 0.55)]
    top = chain([(-3.3, y), (-3.3, 1.6)], quad((-3.3, 2.0), (-2.9, 2.0), (-2.9, 2.0), 3), [(1.6, 2.0)],
                quad((2.9, 2.0), (3.3, 1.2), (3.3, 0.6), 12), [(3.3, y)])
    win = poly((2.0, 0.9), (2.0, 1.75), (2.75, 1.65), (3.05, 0.9))
    hatch = rect(-2.6, 0.2, 0.8, 1.35)
    awning = [poly((-2.8, 1.45), (1.0, 1.45), (1.2, 1.9), (-3.0, 1.9))] + [[(-2.8 + 0.6 * k, 1.45), (-2.95 + 0.6 * k + 0.1, 1.9)] for k in range(1, 7)]
    counter = [rect(-2.8, 0.05, 1.0, 0.2)]
    cups = [poly((-2.2, 0.2), (-2.15, 0.7), (-1.75, 0.7), (-1.7, 0.2)), poly((-1.5, 0.2), (-1.45, 0.7), (-1.05, 0.7), (-1.0, 0.2)), [(-1.9, 0.7), (-1.8, 1.0)]]
    menu = [rect(1.15, -0.2, 1.75, 1.0)] + [[(1.25, yy), (1.65, yy)] for yy in (0.1, 0.4, 0.7)]
    burger = [chain(arc(-0.6, 2.35, 0.75, 0, math.pi, 20), [(0.15, 2.35)]), rrect(-1.4, 2.12, 0.2, 2.32, 0.08), wave(-1.45, 0.25, 2.03, 0.05, 4, 24),
              rrect(-1.35, 1.75, 0.15, 1.97, 0.1)]
    seeds = [eye(x, yy, 0.05) for x, yy in [(-0.9, 2.65), (-0.5, 2.85), (-0.2, 2.6)]]
    return make("Street Food Truck", [body(top, y, wh), win, hatch] + awning + counter + cups + menu + burger + wheels_at(wh, y), seeds)


@design("vehicles_delivery_van", T)
def delivery_van(rng):
    y, wh = -0.6, [(-2.0, 0.55), (2.0, 0.55)]
    top = chain([(-3.2, y), (-3.2, 1.9), (1.2, 1.9)], quad((1.6, 1.9), (2.4, 0.7), (2.4, 0.7), 4), [(3.2, 0.45), (3.3, y)])
    win = poly((1.3, 0.9), (1.3, 1.7), (1.55, 1.7), (2.15, 0.9))
    door = rect(-1.4, -0.45, 0.6, 1.75)
    boxes = [rect(-1.3, -0.45, -0.3, 0.45), rect(-0.2, -0.45, 0.5, 0.25), rect(-1.1, 0.45, -0.1, 1.2), rect(-0.1, 0.25, 0.45, 0.85)]
    tape = [[(-0.8, -0.45), (-0.8, 0.45)], [(-0.6, 0.45), (-0.6, 1.2)], [(0.15, -0.45), (0.15, 0.25)]]
    rail = [[(-3.0, 1.75), (0.8, 1.75)], [(-3.0, 0.0), (-1.6, 0.0)]]
    mirror = [rect(2.25, 0.95, 2.45, 1.3)]
    return make("Parcel Delivery Van", [body(top, y, wh), win, door] + boxes + tape + rail + mirror + wheels_at(wh, y))


@design("vehicles_mail_truck", T)
def mail_truck(rng):
    y, wh = -0.6, [(-1.8, 0.55), (1.6, 0.55)]
    top = [(-2.8, y), (-2.8, 2.3), (0.9, 2.3), (1.5, 1.0), (2.7, 0.75), (2.8, y)]
    win = poly((0.4, 1.2), (0.4, 2.1), (0.95, 2.1), (1.35, 1.2))
    door = [rect(-0.1, -0.4, 1.3, 1.2)]
    env = [rect(-2.4, 0.4, -0.8, 1.4), poly((-2.4, 1.4), (-1.6, 0.85), (-0.8, 1.4), closed=False)]
    stripe = [[(-2.8, 0.15), (2.8, 0.15)], [(-2.8, -0.05), (2.8, -0.05)]]
    mirror = [[(1.45, 1.4), (2.0, 1.8)], rect(1.9, 1.8, 2.2, 2.3)]
    box = [chain(arc(3.5, 0.5, 0.45, 0, math.pi, 14), [(3.05, -0.3), (3.95, -0.3), (3.95, 0.5)]), [(3.5, -0.3), (3.5, -1.15)], [(4.0, 0.3), (4.0, 1.0), (4.3, 1.0)]]
    return make("Mail Truck", [body(top, y, wh), win] + door + env + stripe + mirror + box + wheels_at(wh, y) + [ground(-3.0, 4.4, -1.15)])


@design("vehicles_garbage_truck", T)
def garbage_truck(rng):
    y, wh = -0.7, [(-1.5, 0.6), (2.3, 0.6)]
    top = chain([(-2.7, y), (-3.4, -0.2), (-3.4, 0.5), (-2.5, 2.2)], [(0.9, 2.2)], quad((1.25, 2.2), (1.25, 1.9), (1.25, 1.9), 3),
                [(1.25, 1.6), (2.7, 1.6), (3.3, 0.6), (3.3, y)])
    win = poly((1.45, 0.8), (1.45, 1.4), (2.6, 1.4), (2.95, 0.8))
    seams = [[(-2.5, 2.2), (-2.5, -0.4)], [(1.25, 1.6), (1.25, -0.4)], [(-3.0, -0.4), (3.3, -0.4)]]
    ribs = [[(x, 2.2), (x, -0.4)] for x in (-1.2, 0.0)]
    mouth = [poly((-3.3, 0.45), (-2.65, 0.45), (-2.65, -0.25), (-3.3, -0.25))]
    tipped = [transform(p, dx=-3.6, dy=1.35, rot=2.5) for p in [poly((-0.4, -0.55), (-0.33, 0.55), (0.33, 0.55), (0.4, -0.55)), rect(-0.45, 0.55, 0.45, 0.7)]]
    trash = [poly((-3.2, 0.95), (-3.0, 0.75), (-2.85, 0.95), (-3.0, 1.1)), circle(-3.4, 0.7, 0.12, 10), lens((-3.0, 0.55), (-2.75, 0.45), 0.3)]
    step = [[(-3.4, -0.55), (-2.85, -0.55)]]
    return make("Garbage Truck", [body(top, y, wh), win] + seams + ribs + mouth + tipped + trash + step + wheels_at(wh, y) + [ground(-4.2, 3.5, y - 0.6)])


@design("vehicles_dump_truck", T)
def dump_truck(rng):
    y, wh = -0.8, [(-2.2, 0.65), (-0.9, 0.65), (2.2, 0.65)]
    chassis = body([(-3.0, y), (-3.0, -0.3), (1.0, -0.3), (1.0, 1.7), (2.3, 1.7), (3.0, 0.7), (3.3, 0.6), (3.3, y)], y, wh)
    win = poly((1.2, 0.8), (1.2, 1.5), (2.2, 1.5), (2.75, 0.8))
    bed = transform(poly((0.0, 0.0), (3.8, 0.0), (4.0, 1.5), (-0.2, 1.5)), dx=-3.0, dy=-0.25, rot=0.42)
    bedribs = [transform([(x, 0.0), (x, 1.5)], dx=-3.0, dy=-0.25, rot=0.42) for x in (1.3, 2.6)]
    ram = [[(-1.0, -0.3), (-1.6, 1.1)], [(-0.85, -0.3), (-1.45, 1.15)]]
    pile = [chain([(-4.3, -1.45)], quad((-4.0, 0.2), (-3.5, 0.4), (-3.1, -0.4), 16), [(-2.9, -1.45)])]
    rocks = [circle(x, yy, r, 14) for x, yy, r in [(-3.3, 0.6, 0.15), (-3.6, 1.2, 0.18), (-3.9, 0.7, 0.13)]]
    return make("Dump Truck Unloading", [chassis, win, bed] + bedribs + ram + pile + rocks + wheels_at(wh, y) + [ground(-4.4, 3.5, y - 0.65)])


@design("vehicles_cement_mixer", T)
def cement_mixer(rng):
    y, wh = -0.8, [(-2.3, 0.55), (-1.2, 0.55), (2.2, 0.55)]
    chassis = body([(-3.2, y), (-3.2, -0.4), (1.2, -0.4), (1.2, 1.4), (2.5, 1.4), (3.1, 0.6), (3.3, 0.5), (3.3, y)], y, wh)
    win = poly((1.4, 0.6), (1.4, 1.2), (2.4, 1.2), (2.85, 0.6))
    drum = ellipse(-1.0, 0.75, 2.1, 1.05, 120, rot=0.18)
    stripes = [transform(quad((-0.9 + d, -1.0), (-0.1 + d, 0.0), (-0.9 + d, 1.0), 16), dx=-1.0, dy=0.75, rot=0.18) for d in (-0.6, 0.3, 1.2)]
    neck = [transform(rect(-2.6, -0.32, -2.0, 0.32), dx=-1.0, dy=0.75, rot=0.18)]
    chute = [poly((-3.4, 0.15), (-3.9, -0.6), (-3.65, -0.7), (-3.2, -0.05), closed=False)]
    stand = [[(0.3, -0.4), (0.7, 0.2)], [(-2.6, -0.4), (-2.9, 0.2)]]
    return make("Cement Mixer Truck", [chassis, win, drum] + stripes + neck + chute + stand + wheels_at(wh, y))


@design("vehicles_tow_truck", T)
def tow_truck(rng):
    y, wh = -0.8, [(-0.6, 0.5), (2.4, 0.5)]
    chassis = body([(-1.4, y), (-1.4, -0.2), (1.2, -0.2), (1.2, 1.4), (2.4, 1.4), (3.0, 0.5), (3.3, 0.4), (3.3, y)], y, wh)
    win = poly((1.4, 0.6), (1.4, 1.2), (2.3, 1.2), (2.75, 0.6))
    beacon = [rrect(1.6, 1.4, 2.1, 1.65, 0.1)]
    boom = [tube([(0.4, -0.2), (-1.6, 1.7)], 0.3)]
    cable = [[(-1.6, 1.7), (-2.0, 0.3)], arc(-2.0, 0.15, 0.15, math.pi / 2, 2.4 * math.pi / 1.0 - math.pi, 10)]
    car = [transform(p, rot=0.25) for p in mini_car(0, 0, 1.0)]
    car = [transform(p, dx=-3.0, dy=-0.4, s=1.1) for p in car]
    return make("Tow Truck", [chassis, win] + beacon + boom + cable + car + wheels_at(wh, y) + [ground(-4.4, 3.5, y - 0.5)])


@design("vehicles_semi_truck", T)
def semi_truck(rng):
    y = -0.8
    wh = [(-2.9, 0.4), (-2.05, 0.4), (0.6, 0.4), (1.45, 0.4), (3.0, 0.4)]
    trailer = rect(-3.6, -0.4, 0.9, 1.8)
    tractor = body([(0.3, y), (0.3, -0.3), (1.0, -0.3), (1.0, 1.95), (2.2, 1.95), (2.4, 0.7), (3.5, 0.6), (3.6, y)], y, [w for w in wh if w[0] > 0])
    win = poly((1.6, 1.0), (1.6, 1.75), (2.15, 1.75), (2.25, 1.0))
    sleeper_win = [rrect(1.1, 1.15, 1.45, 1.6, 0.08)]
    stack = [rrect(0.85, 0.3, 1.0, 2.5, 0.05)]
    grille = [[(3.45, -0.25), (3.45, 0.5)], [(3.3, -0.25), (3.3, 0.5)]]
    legs = [[(-0.6, -0.4), (-0.6, -1.15)], [(-0.7, -1.15), (-0.5, -1.15)]]
    stripes = [[(-3.4, 0.6), (0.7, 0.6)], [(-3.4, 0.8), (0.7, 0.8)]]
    trailer_wheels = []
    for cx, r in wh[:2]:
        trailer_wheels += wheel(cx, y, r)
    tw = []
    for cx, r in wh[2:]:
        tw += wheel(cx, y, r)
    return make("Semi Truck with Trailer", [trailer, tractor, win] + sleeper_win + stack + grille + legs + stripes + trailer_wheels + tw
                + [[(-3.6, -0.4), (-3.6, -0.55), (-1.6, -0.55), (-1.6, -0.4)]])


@design("vehicles_tanker_truck", T)
def tanker_truck(rng):
    y, wh = -0.8, [(-2.6, 0.45), (-1.6, 0.45), (2.5, 0.45)]
    frame = body([(-3.4, y), (-3.4, -0.4), (1.4, -0.4), (1.4, 1.5), (2.8, 1.5), (3.3, 0.5), (3.3, y)], y, wh)
    win = poly((1.6, 0.6), (1.6, 1.3), (2.7, 1.3), (3.05, 0.6))
    tank = rrect(-3.5, -0.3, 1.2, 1.6, 0.95)
    rings = [[(x, -0.3), (x, 1.6)] for x in (-1.6, -0.3)]
    hatches = [rrect(x - 0.25, 1.6, x + 0.25, 1.8, 0.06) for x in (-2.3, -0.95, 0.4)]
    rail = [[(-2.9, 1.95), (0.9, 1.95)]] + [[(x, 1.6), (x, 1.95)] for x in (-2.9, -1.0, 0.9)]
    ladder = [[(1.25, -0.4), (1.25, 1.95)], [(1.0, -0.4), (1.0, 1.4)]] + [[(1.0, yy), (1.25, yy)] for yy in (0.0, 0.5, 1.0)]
    diamond = [poly((-1.0, 0.3), (-0.6, 0.7), (-1.0, 1.1), (-1.4, 0.7))]
    return make("Fuel Tanker Truck", [frame, win, tank] + rings + hatches + rail + ladder + diamond + wheels_at(wh, y))


@design("vehicles_car_transporter", T)
def car_transporter(rng):
    y = -1.0
    wh = [(-2.9, 0.38), (-2.05, 0.38), (2.5, 0.38), (3.3, 0.38)]
    cab = body([(2.0, y), (2.0, 1.9), (3.4, 1.9), (3.7, 1.4), (3.7, y)], y, wh[2:])
    win = poly((2.6, 1.0), (2.6, 1.7), (3.35, 1.7), (3.55, 1.25), (3.55, 1.0))
    deck_lo = rect(-3.6, -0.75, 1.9, -0.55)
    deck_hi = rect(-3.6, 0.85, 1.9, 1.0)
    posts = [[(x, -0.55), (x, 0.85)] for x in (-3.5, -0.9, 1.8)] + [[(-3.5, 1.0), (-3.5, 2.6)], [(1.8, 1.0), (1.8, 2.6)]]
    cars = mini_car(-2.2, -0.35, 0.95) + mini_car(0.4, -0.35, 0.95) + mini_car(-2.2, 1.25, 0.95) + mini_car(0.4, 1.25, 0.95)
    out = [cab, win, deck_lo, deck_hi] + posts + cars + [[(-3.6, -0.75), (-3.6, y), (-1.6, y)]]
    for cx, r in wh:
        out += wheel(cx, y, r)
    return make("Car Transporter", out)


@design("vehicles_monster_truck", T)
def monster_truck(rng):
    body_ = poly((-3.0, 0.3), (-3.0, 1.1), (-0.3, 1.1), (-0.15, 2.0), (1.3, 2.0), (2.0, 1.2), (3.0, 1.05), (3.05, 0.3))
    win = poly((0.05, 1.2), (0.05, 1.85), (1.2, 1.85), (1.75, 1.2))
    bed = [[(-2.8, 1.1), (-2.8, 0.7), (-0.5, 0.7)]]
    flames = [chain([(1.2, 0.5)], quad((1.6, 0.9), (2.2, 0.6), (2.6, 0.75), 6), quad((2.2, 0.45), (1.9, 0.4), (1.2, 0.5), 6))]
    springs = []
    for x in (-1.9, 1.9):
        springs.append([(x + (0.2 if k % 2 else -0.2), -1.1 + 0.2 * k) for k in range(8)])
    axle = [[(-1.9, -1.55), (1.9, -1.55)]]
    rollbar = [poly((-1.8, 1.1), (-1.6, 1.7), (-0.3, 1.7), closed=False)]
    return make("Monster Truck", [body_, win] + bed + flames + springs + axle + rollbar
                + knobby(-1.9, -1.55, 1.15) + knobby(1.9, -1.55, 1.15))


# ---------------------------------------------------------------- service & city

def _sedan(y, wh):
    top = chain([(-3.2, y), (-3.2, 0.45), (-2.2, 0.55), (-1.2, 1.3), (0.6, 1.3), (1.4, 0.6)],
                quad((1.4, 0.6), (3.0, 0.5), (3.25, 0.2), 8), [(3.25, y)])
    wins = [poly((-1.7, 0.65), (-1.05, 1.18), (-0.3, 1.18), (-0.3, 0.65)), poly((-0.1, 0.65), (-0.1, 1.18), (0.5, 1.18), (1.05, 0.65))]
    return body(top, y, wh), wins


@design("vehicles_police_car", T)
def police_car(rng):
    y, wh = -0.5, [(-2.0, 0.55), (2.0, 0.55)]
    b, wins = _sedan(y, wh)
    bar = [rrect(-1.0, 1.3, 0.5, 1.6, 0.1), [(-0.25, 1.3), (-0.25, 1.6)], arc(-0.6, 1.6, 0.15, 0, math.pi, 6), arc(0.1, 1.6, 0.15, 0, math.pi, 6)]
    badge = [star(-0.2, 0.05, 0.42, 5, 0.45), circle(-0.2, 0.05, 0.1, 10)]
    stripe = [[(-3.2, -0.25), (-0.75, -0.25)], [(0.35, -0.25), (3.25, -0.25)]]
    push = [rrect(3.25, -0.6, 3.55, 0.25, 0.08), [(3.25, -0.2), (3.55, -0.2)]]
    return make("Police Patrol Car", [b] + wins + bar + badge + stripe + push + wheels_at(wh, y, spokes=5))


@design("vehicles_ambulance", T)
def ambulance(rng):
    y, wh = -0.6, [(-2.1, 0.55), (2.1, 0.55)]
    top = [(-3.3, y), (-3.3, 2.0), (1.1, 2.0), (1.1, 1.4), (2.2, 1.4), (2.8, 0.6), (3.3, 0.45), (3.3, y)]
    win = poly((1.3, 0.65), (1.3, 1.25), (2.15, 1.25), (2.6, 0.65))
    cross = poly((-1.4, 0.4), (-0.9, 0.4), (-0.9, -0.1), (-0.5, -0.1), (-0.5, 0.4), (0.0, 0.4), (0.0, 0.8), (-0.5, 0.8), (-0.5, 1.3),
                 (-0.9, 1.3), (-0.9, 0.8), (-1.4, 0.8))
    lights = [rrect(1.3, 1.4, 2.0, 1.65, 0.1), rrect(-3.2, 2.0, -2.6, 2.25, 0.1), rrect(0.4, 2.0, 1.0, 2.25, 0.1)]
    stripe = [[(-3.3, 1.65), (1.1, 1.65)], [(-3.3, -0.25), (3.3, -0.25)]]
    rear = [[(-3.1, 1.5), (-3.1, -0.1)], [(-2.4, 1.5), (-2.4, -0.1)]]
    return make("Ambulance", [body(top, y, wh), win, cross] + lights + stripe + rear + wheels_at(wh, y))


@design("vehicles_taxi", T)
def taxi(rng):
    y, wh = -0.5, [(-2.0, 0.6), (2.0, 0.6)]
    top = chain([(-3.2, y), (-3.2, 0.45)], quad((-3.2, 0.6), (-2.5, 0.6), (-2.0, 0.6), 4), cubic((-2.0, 0.6), (-1.5, 1.55), (0.6, 1.6), (1.2, 0.6), 24),
                quad((1.2, 0.6), (3.1, 0.6), (3.25, 0.2), 8), [(3.25, y)])
    wins = [chain(quad((-1.55, 0.7), (-1.2, 1.35), (-0.35, 1.38), 10), [(-0.35, 0.7), (-1.55, 0.7)]),
            chain(quad((-0.15, 1.38), (0.6, 1.35), (0.95, 0.7), 10), [(-0.15, 0.7), (-0.15, 1.38)])]
    sign = [rrect(-0.75, 1.45, 0.35, 1.9, 0.1)]
    band = [rect(-2.5, -0.15, 2.5, 0.35)]
    checks = [rect(-2.5 + 0.5 * j, -0.15 + 0.25 * (j % 2), -2.0 + 0.5 * j, 0.1 + 0.25 * (j % 2)) for j in range(10)]
    return make("Checkered Taxi Cab", [body(top, y, wh)] + wins + sign + band + checks + wheels_at(wh, y, wall=True))


@design("vehicles_limousine", T)
def limousine(rng):
    y, wh = -0.3, [(-2.7, 0.42), (2.8, 0.42)]
    top = chain([(-3.9, y), (-3.9, 0.3), (-3.1, 0.38), (-2.6, 0.8), (1.9, 0.8), (2.5, 0.38)], quad((2.5, 0.38), (3.8, 0.33), (3.9, 0.1), 6), [(3.9, y)])
    wins = [poly((-2.95, 0.42), (-2.55, 0.72), (-2.0, 0.72), (-2.0, 0.42))] + [rect(-1.8 + 0.85 * k, 0.42, -1.1 + 0.85 * k, 0.72) for k in range(4)] + \
           [poly((1.6, 0.42), (1.6, 0.72), (1.85, 0.72), (2.3, 0.42))]
    doors = [[(x, 0.4), (x, -0.2)] for x in (-1.9, -0.25, 1.5)]
    trim = [[(-3.8, 0.1), (3.8, 0.1)]]
    flag = [[(3.6, 0.3), (3.6, 0.75)], poly((3.6, 0.75), (3.95, 0.68), (3.6, 0.6), closed=False)]
    return make("Stretch Limousine", [body(top, y, wh, 0.07)] + wins + doors + trim + flag + wheels_at(wh, y, wall=True))


@design("vehicles_double_decker", T)
def double_decker(rng):
    y, wh = -1.2, [(-2.0, 0.55), (1.9, 0.55)]
    shell = body(chain([(-3.0, y), (-3.0, 2.2)], quad((-3.0, 2.6), (-2.6, 2.6), (-2.6, 2.6), 3), [(2.4, 2.6)], quad((2.8, 2.6), (2.8, 2.2), (2.8, 2.2), 3), [(2.8, y)]), y, wh)
    upper = [rrect(-2.8 + 0.9 * k, 1.5, -2.05 + 0.9 * k, 2.35, 0.1) for k in range(6)]
    lower = [rrect(-2.8 + 0.9 * k, 0.15, -2.05 + 0.9 * k, 0.95, 0.1) for k in range(5)]
    front = [rrect(1.75, 0.15, 2.65, 0.95, 0.1), rect(1.85, 1.1, 2.6, 1.35)]
    band = [[(-3.0, 1.1), (1.6, 1.1)], [(-3.0, 1.35), (1.6, 1.35)]]
    plat = [[(-2.9, -1.0), (-2.9, 0.0)], [(-2.3, -1.0), (-2.3, 0.0)]]
    lamp = [circle(2.55, -0.5, 0.15, 12)]
    return make("Double-Decker Bus", [shell] + upper + lower + front + band + plat + lamp + wheels_at(wh, y))


@design("vehicles_city_bus", T)
def city_bus(rng):
    y, wh = -0.7, [(-2.4, 0.5), (2.0, 0.5)]
    top = chain([(-3.6, y), (-3.6, 1.6)], quad((-3.6, 1.9), (-3.3, 1.9), (-3.3, 1.9), 3), [(3.2, 1.9)], quad((3.6, 1.9), (3.6, 1.2), (3.6, 1.2), 6), [(3.6, y)])
    wins = [rect(-3.4 + 0.95 * k, 0.55, -2.55 + 0.95 * k, 1.5) for k in (0, 1, 3, 4, 5)]
    doors = [rect(-1.55, -0.55, -0.6, 1.5), [(-1.075, -0.55), (-1.075, 1.5)], rect(2.55, -0.55, 3.25, 1.5), [(2.9, -0.55), (2.9, 1.5)]]
    screen = [poly((3.35, 0.4), (3.35, 1.5), (3.55, 1.5), (3.55, 0.4))]
    route = [rect(1.0, 1.6, 2.35, 1.82)]
    roof = [rrect(-2.4, 1.9, -0.6, 2.15, 0.08)]
    skirt = [[(-3.6, 0.1), (-1.55, 0.1)], [(-0.6, 0.1), (2.55, 0.1)]]
    return make("City Bus", [body(top, y, wh)] + wins + doors + screen + route + roof + skirt + wheels_at(wh, y))


# ---------------------------------------------------------------- work machines

@design("vehicles_forklift", T)
def forklift(rng):
    gy = -1.6
    rear = chain([(-2.4, -1.1)], arc(-2.4, -0.3, 0.8, -math.pi / 2, -1.5 * math.pi, 16), [(-2.4, 0.5), (0.9, 0.5), (0.9, -1.1)])
    under_ = [(-2.4, -1.1), (-2.0, -1.1)] + arc(-1.6, -1.1, 0.55, math.pi, 0, 14)[::-1][::-1] + [(-1.05, -1.1), (0.2, -1.1)] + arc(0.6, -1.1, 0.6, math.pi, 0, 14) + [(1.2, -1.1), (0.9, -1.1)]
    guard = [poly((-1.6, 0.5), (-1.6, 2.4), (0.8, 2.4), (0.9, 0.5), closed=False)]
    seat = [poly((-1.2, 0.5), (-1.3, 1.4), (-1.0, 1.4), (-0.9, 0.8), (-0.2, 0.8), closed=False)]
    wheel_ = [[(0.2, 0.5), (0.6, 1.3)], ellipse(0.62, 1.32, 0.3, 0.08, 14, rot=-0.6)]
    mast = [rect(1.2, -1.2, 1.45, 2.9), rect(1.55, -1.2, 1.8, 2.9)]
    forks = [poly((1.8, -0.2), (1.8, 1.4), (1.95, 1.4), (1.95, -0.05), (3.6, -0.05), (3.6, -0.2))]
    pallet = [rect(1.95, -0.05, 3.6, 0.1)]
    boxes = [rect(2.05, 0.1, 2.8, 0.85), rect(2.8, 0.1, 3.5, 0.75), rect(2.3, 0.85, 3.2, 1.6)]
    tape = [[(2.425, 0.1), (2.425, 0.85)], [(2.75, 0.85), (2.75, 1.6)]]
    w = wheel(-1.6, -1.1, 0.5) + wheel(0.6, -1.1, 0.55)
    return make("Warehouse Forklift", [rear, under_] + guard + seat + wheel_ + mast + forks + pallet + boxes + tape + w + [ground(-3.4, 3.8, gy - 0.05)])


@design("vehicles_bulldozer", T)
def bulldozer(rng):
    tr = tracks(-2.9, 1.4, -2.4, -1.4, 6)
    hull = poly((-2.6, -1.4), (-2.6, -0.1), (1.0, -0.1), (1.4, -0.7), (1.4, -1.4), closed=False)
    cab = [poly((-2.3, -0.1), (-2.3, 1.7), (-0.4, 1.7), (-0.1, -0.1), closed=False), poly((-2.1, 0.3), (-2.1, 1.5), (-0.55, 1.5), (-0.35, 0.3)), rect(-2.5, 1.7, -0.2, 1.85)]
    stack = [rrect(0.3, -0.1, 0.5, 1.1, 0.05), [(0.25, 1.1), (0.55, 1.1)]]
    grille = [[(0.55, -0.6), (1.2, -0.6)], [(0.55, -0.35), (1.15, -0.35)]]
    blade = [chain(quad((2.2, -2.5), (2.9, -1.4), (2.3, -0.2), 16), [(2.6, -0.2)], quad((2.6, -0.2), (3.25, -1.4), (2.55, -2.5), 16), [(2.2, -2.5)])]
    arms = [[(1.4, -1.0), (2.45, -1.2)], [(1.2, -0.3), (2.4, -0.6)]]
    ripper = [poly((-2.9, -0.9), (-3.5, -0.9), (-3.6, -2.0), (-3.35, -2.3), closed=False)]
    return make("Bulldozer", tr + [hull] + cab + stack + grille + blade + arms + ripper)


@design("vehicles_excavator", T)
def excavator(rng):
    tr = tracks(-3.0, 0.8, -2.6, -1.7, 5)
    base = [rect(-2.6, -1.7, 0.4, -1.45)]
    house = poly((-3.3, -1.45), (-3.3, -0.3), (-2.9, 0.1), (-0.6, 0.1), (-0.6, -1.45), closed=False)
    cab = [poly((-0.6, -1.45), (-0.6, 1.4), (0.3, 1.4), (0.6, 0.2), (0.6, -1.45), (-0.6, -1.45)), poly((-0.45, 0.2), (-0.45, 1.25), (0.2, 1.25), (0.45, 0.2))]
    boom = [poly((0.6, -1.0), (0.6, -0.5), (1.6, 2.3), (2.75, 2.55), (2.85, 2.1), (1.95, 1.85))]
    stick = [poly((2.5, 2.3), (2.85, 2.45), (3.35, -0.45), (3.0, -0.55))]
    bucket = [chain([(2.95, -0.4)], quad((2.2, -1.1), (2.6, -1.9), (3.3, -2.0), 14), [(3.65, -1.6), (3.45, -0.4), (2.95, -0.4)])]
    teeth = [poly((2.75 + 0.18 * k, -1.97), (2.82 + 0.18 * k, -2.25), (2.92 + 0.18 * k, -1.99), closed=False) for k in range(3)]
    cyl = [[(0.6, -0.1), (1.5, 1.6)], [(0.75, -0.25), (1.65, 1.45)]]
    rail = [[(-2.9, 0.1), (-2.9, 0.45), (-1.0, 0.45), (-1.0, 0.1)]]
    return make("Excavator Digger", tr + base + [house] + cab + boom + stick + bucket + teeth + cyl + rail + [ground(-3.6, 3.8, -2.6)])


@design("vehicles_crane_truck", T)
def crane_truck(rng):
    y, wh = -1.3, [(-2.6, 0.42), (-1.7, 0.42), (0.6, 0.42), (1.5, 0.42), (2.8, 0.42)]
    carrier = body([(-3.3, y), (-3.3, -0.8), (2.2, -0.8), (2.2, 0.3), (3.1, 0.3), (3.5, -0.3), (3.5, y)], y, wh, 0.06)
    win = poly((2.35, -0.4), (2.35, 0.15), (3.0, 0.15), (3.3, -0.4))
    turret = rrect(-1.6, -0.8, 0.4, 0.2, 0.1)
    cab = [rect(-0.3, -0.6, 0.4, 0.6), rect(-0.2, -0.2, 0.3, 0.45)]
    boom = [tube([(-1.2, -0.2), (1.8, 2.8)], 0.4), tube([(1.8, 2.8), (2.8, 3.8)], 0.25, cap=False)]
    cable = [[(2.85, 3.85), (2.85, 1.1)]]
    hook = [rrect(2.6, 0.6, 3.1, 1.1, 0.1), chain([(2.85, 0.6), (2.85, 0.35)], arc(2.7, 0.35, 0.15, 0, -math.pi, 8), [(2.55, 0.45)])]
    outriggers = [[(-3.1, -0.9), (-3.6, -1.75)], [(-3.8, -1.75), (-3.4, -1.75)], [(1.9, -0.9), (2.3, -1.75)], [(2.1, -1.75), (2.5, -1.75)]]
    return make("Mobile Crane Truck", [carrier, win, turret] + cab + boom + cable + hook + outriggers + wheels_at(wh, y))


@design("vehicles_road_roller", T)
def road_roller(rng):
    drum = [circle(1.8, -1.2, 1.1, 70), circle(1.8, -1.2, 0.95, 60), circle(1.8, -1.2, 0.25, 16)]
    yoke = [poly((0.6, -1.2), (0.9, 0.3), (2.0, 0.3), (2.0, -0.15), closed=False)]
    chassis = poly((0.6, -1.0), (-2.9, -1.0), (-3.1, -0.4), (-3.1, 0.5), (0.9, 0.5), (0.9, -0.2), closed=False)
    rear = wheel(-1.9, -1.45, 0.85, hub=0.45)
    canopy = [rect(-3.3, 2.4, -0.2, 2.6), [(-3.0, 0.5), (-3.0, 2.4)], [(-0.5, 0.5), (-0.5, 2.4)]]
    seat = [poly((-2.4, 0.5), (-2.5, 1.4), (-2.2, 1.4), (-2.1, 0.85), (-1.5, 0.85), closed=False)]
    steer = [[(-1.0, 0.5), (-0.8, 1.1)], ellipse(-0.8, 1.15, 0.3, 0.07, 14, rot=-0.2)]
    beacon = [arc(-1.75, 2.6, 0.2, 0, math.pi, 8)]
    asphalt = [[(-3.6, -2.3), (3.6, -2.3)], [(0.0, -2.1), (0.6, -2.1)], [(-3.4, -2.1), (-3.0, -2.1)]]
    return make("Road Roller", drum + yoke + [chassis] + rear + canopy + seat + steer + beacon + asphalt)


# ---------------------------------------------------------------- small rides

@design("vehicles_go_kart", T)
def go_kart(rng):
    frame = poly((-3.0, -0.9), (-2.4, -0.6), (1.6, -0.75), (3.0, -0.6), (3.1, -0.95), (-3.0, -1.0))
    nose = [poly((1.6, -0.75), (2.0, -0.2), (3.0, -0.3), (3.0, -0.6), closed=False)]
    driver = [circle(-0.9, 1.55, 0.55, 40), rrect(-0.72, 1.35, -0.3, 1.75, 0.1),
              poly((-1.45, -0.62), (-1.35, 1.0), (-0.65, 1.0), (-0.4, 0.55), (0.55, 0.3), (0.55, 0.05), (-0.55, 0.25), (-0.6, -0.15),
                   (1.1, -0.2), (1.1, -0.55), (-0.5, -0.62))]
    wheel_ = [[(0.5, -0.6), (0.65, 0.2)], ellipse(0.65, 0.25, 0.08, 0.32, 14, rot=-0.3)]
    engine = [rect(-2.9, -0.6, -2.1, 0.0), [(-2.9, -0.3), (-3.4, -0.4)]]
    w = wheel(-2.2, -1.25, 0.65, hub=0.45) + wheel(2.3, -1.3, 0.5, hub=0.45)
    flag = [[(2.8, 1.6), (2.8, 0.2)], rect(2.8, 1.0, 3.6, 1.6)] + [rect(2.8 + 0.4 * (k % 2), 1.0 + 0.3 * (k // 2), 3.0 + 0.4 * (k % 2), 1.3 + 0.3 * (k // 2)) for k in range(4)]
    return make("Go-Kart Racer", [frame] + nose + driver + wheel_ + engine + w + flag)


@design("vehicles_dune_buggy", T)
def dune_buggy(rng):
    y, wh = -0.95, [(-1.9, 0.9), (2.1, 0.75)]
    top = chain([(-3.0, y), (-3.0, -0.2)], quad((-3.0, -0.2), (-1.9, 0.95), (-0.7, -0.2), 18), [(-0.55, -0.45), (0.85, -0.45), (1.0, -0.2)],
                quad((1.0, -0.2), (2.1, 0.75), (3.2, -0.2), 16), [(3.45, -0.55), (3.35, y)])
    cage = [poly((-0.55, -0.45), (-0.55, 1.3), (0.05, 1.35), (0.2, -0.45), closed=False)]
    screen = [poly((0.95, -0.25), (1.2, 0.6), (1.35, 0.6), (1.15, -0.1), closed=False)]
    driver = [circle(0.35, 0.55, 0.38, 30), rrect(0.45, 0.42, 0.75, 0.68, 0.08), [(0.0, -0.45), (0.1, 0.2)], [(0.6, -0.45), (0.55, 0.2)]]
    lamps = [circle(2.3, 0.15, 0.17, 14), circle(1.8, 0.2, 0.15, 12)]
    engine = [rect(-3.45, -0.75, -3.0, -0.05), [(-3.0, 0.1), (-3.45, -0.05)], tube([(-3.45, -0.55), (-3.85, -0.45), (-3.95, -0.1)], 0.16)]
    flag = [[(-0.55, 1.3), (-0.9, 3.0)], poly((-0.9, 3.0), (-1.8, 2.85), (-0.85, 2.6), closed=False)]
    sun = [circle(2.4, 2.3, 0.5, 30)] + [[(2.4 + 0.7 * math.cos(a), 2.3 + 0.7 * math.sin(a)), (2.4 + 0.95 * math.cos(a), 2.3 + 0.95 * math.sin(a))] for a in [k * TAU / 8 for k in range(8)]]
    dunes = [chain(quad((-3.9, -1.85), (-1.0, -1.85), (0.5, -1.75), 12), quad((0.5, -1.75), (2.0, -1.65), (3.8, -1.72), 12)), quad((-3.9, 1.0), (-2.8, 1.6), (-1.6, 1.1), 12)]
    w = knobby(-1.9, y, 0.9) + knobby(2.1, y, 0.75)
    return make("Beach Dune Buggy", [body(top, y, wh, 0.12)] + cage + screen + driver + lamps + engine + flag + sun + dunes + w)


@design("vehicles_vespa", T)
def vespa(rng):
    cowl = chain([(-0.5, -1.0)], cubic((-0.5, -1.0), (-1.5, -1.05), (-2.6, -1.1), (-2.75, -0.6), 16),
                 cubic((-2.75, -0.6), (-2.85, -0.1), (-2.3, 0.05), (-1.6, 0.05), 14), [(-0.5, 0.05), (-0.5, -1.0)])
    seat = [rrect(-2.2, 0.05, -0.6, 0.45, 0.18)]
    floor = [[(-0.5, -1.0), (0.9, -1.0)], [(-0.5, -1.18), (0.95, -1.18)]]
    shield = [chain([(0.9, -1.0)], cubic((0.9, -1.0), (1.35, -0.6), (1.4, 0.4), (1.25, 1.1), 16), [(1.5, 1.1)],
                    cubic((1.5, 1.1), (1.7, 0.4), (1.6, -0.7), (0.95, -1.18), 16))]
    column = [[(1.38, 1.1), (1.45, 1.5)]]
    bars = [rrect(0.9, 1.5, 2.0, 1.78, 0.12), circle(2.15, 1.64, 0.2, 16), [(1.0, 1.78), (0.8, 2.25)], ellipse(0.75, 2.35, 0.2, 0.12, 12)]
    fender = [chain(arc(2.0, -1.55, 0.72, 0.25, 2.5, 18), [(1.4, -0.9)])]
    fork = [[(1.5, -0.6), (2.0, -1.55)]]
    vent = [[(-2.3, -0.4), (-1.2, -0.4)], [(-2.3, -0.6), (-1.2, -0.6)]]
    w = wheel(-1.7, -1.55, 0.55, hub=0.55) + wheel(2.0, -1.55, 0.55, hub=0.55)
    stand = [[(-0.6, -1.18), (-0.8, -2.1)]]
    return make("Vintage Vespa Scooter", [cowl] + seat + floor + shield + column + bars + fender + fork + vent + w + stand)


@design("vehicles_quad_bike", T)
def quad_bike(rng):
    fend_r = chain(arc(-1.8, -0.9, 1.05, 0.15, math.pi - 0.05, 20), [(-3.0, -0.2)])
    fend_f = chain([(3.0, -0.2)], arc(1.9, -0.9, 1.05, 0.15, math.pi - 0.05, 20)[::-1][::-1])
    body_ = poly((-0.8, -0.1), (-0.7, 0.4), (0.9, 0.4), (1.0, -0.1), (0.4, -0.7), (-0.3, -0.7))
    seat = [chain(quad((-2.2, 0.35), (-1.2, 0.85), (-0.2, 0.55), 12), [(-0.6, 0.35), (-2.2, 0.35)])]
    tank = [quad((0.0, 0.55), (0.6, 1.0), (1.2, 0.5), 10)]
    bars = [[(1.0, 0.7), (1.3, 1.5)], [(1.0, 1.55), (1.7, 1.45)]]
    rack = [[(1.4, 0.3), (2.8, 0.3)], [(1.6, 0.3), (1.6, 0.0)], [(2.6, 0.3), (2.6, 0.0)]]
    lamp = [circle(2.75, -0.25, 0.18, 14)]
    return make("Quad Bike ATV", [fend_r, fend_f, body_] + seat + tank + bars + rack + lamp
                + knobby(-1.8, -0.9, 0.85) + knobby(1.9, -0.9, 0.85))


@design("vehicles_sidecar", T)
def sidecar(rng):
    bike_w = wheel(-2.5, -1.0, 0.7, hub=0.4) + wheel(2.5, -1.0, 0.7, hub=0.4)
    fork = [[(2.5, -1.0), (2.0, 0.9)], [(1.6, 1.1), (2.3, 1.1)], [(2.05, 0.9), (2.0, 1.1)], circle(2.3, 0.6, 0.18, 14)]
    frame = [[(-2.5, -1.0), (-1.6, -0.55)], [(-2.5, -1.0), (-1.9, 0.45)], [(1.3, 0.45), (2.05, 0.7)]]
    tank = [chain(quad((-0.4, 0.4), (0.4, 1.0), (1.3, 0.45), 12), [(-0.4, 0.4)])]
    seat = [chain(quad((-1.9, 0.45), (-1.1, 0.8), (-0.4, 0.45), 10), [(-1.9, 0.45)])]
    fenders = [arc(-2.5, -1.0, 0.85, 0.5, 2.4, 14), arc(2.5, -1.0, 0.85, 0.6, 2.6, 14)]
    side = chain([(-1.6, -0.2)], cubic((-1.6, -0.2), (-1.7, -1.4), (0.4, -1.4), (1.9, -0.75), 24), quad((1.9, -0.75), (2.0, -0.2), (1.2, -0.05), 8), [(-1.6, -0.2)])
    screen = [poly((0.5, -0.1), (0.8, 0.5), (1.1, 0.45), (1.0, -0.08), closed=False)]
    stripe = [quad((-1.4, -0.6), (0.0, -0.75), (1.6, -0.55), 10)]
    sw = wheel(0.0, -1.35, 0.45, hub=0.4)
    return make("Motorcycle with Sidecar", bike_w + fork + frame + tank + seat + fenders + [side] + screen + stripe + sw + [ground(-3.4, 3.4, -1.8)])


@design("vehicles_chopper", T)
def chopper(rng):
    rear = wheel(-2.3, -1.2, 0.8, hub=0.35)
    front = [circle(3.0, -1.35, 0.65, 50), circle(3.0, -1.35, 0.12, 10)] + [[(3.0, -1.35), (3.0 + 0.6 * math.cos(a), -1.35 + 0.6 * math.sin(a))] for a in [k * TAU / 10 for k in range(10)]]
    frame = [poly((-2.3, -1.2), (-0.8, -1.0), (0.9, -1.0), closed=False), [(-2.3, -1.2), (-1.6, 0.1)], [(0.9, -1.0), (1.0, 0.6)]]
    fork = [[(3.0, -1.35), (1.0, 0.8)], [(3.15, -1.25), (1.15, 0.85)]]
    bars = [poly((1.05, 0.85), (0.75, 2.4), (0.3, 2.5), closed=False)]
    tank = [chain(quad((-0.3, 0.3), (0.4, 1.05), (1.05, 0.35), 12), [(-0.3, 0.3)])]
    seat = [chain(quad((-2.0, 0.15), (-1.3, 0.05), (-0.35, 0.35), 8), [(-0.5, 0.05), (-2.0, 0.15)]), [(-2.0, 0.15), (-2.3, 1.6)], arc(-2.3, 1.8, 0.2, -math.pi / 2, math.pi / 2, 8)]
    cyl = []
    for dx, rot in ((-0.35, 0.35), (0.35, -0.35)):
        cyl.append(transform(rect(-0.25, 0.0, 0.25, 0.85), dx=dx, dy=-0.95, rot=rot))
        cyl += [transform([(-0.25, yy), (0.25, yy)], dx=dx, dy=-0.95, rot=rot) for yy in (0.3, 0.5, 0.7)]
    pipes = [[(-0.2, -0.75), (-1.2, -0.55)], [(0.2, -0.75), (-1.2, -0.75)], [(-1.2, -0.45), (-1.2, -0.85)]]
    lamp = [circle(1.5, 0.75, 0.22, 16)]
    return make("Chopper Motorcycle", rear + front + frame + fork + bars + tank + seat + cyl + pipes + lamp)


@design("vehicles_tuk_tuk", T)
def tuk_tuk(rng):
    canopy = [chain(quad((-2.7, 1.9), (-0.4, 2.6), (1.8, 2.0), 20), [(1.8, 1.7), (-2.7, 1.7), (-2.7, 1.9)])]
    posts = [[(-2.5, 1.7), (-2.5, -0.1)], [(0.4, 1.7), (0.4, -0.1)]]
    tub = chain([(-2.8, -0.1), (-2.8, -0.9)], under(1.2, -2.8, -0.9, [(-1.6, 0.55)])[::-1], [(1.2, -0.9)], quad((2.5, -0.9), (2.5, -0.1), (2.3, 0.3), 10),
                [(1.7, 1.7)], [(1.2, 1.7)], [(1.2, -0.1), (-2.8, -0.1)])
    screen = [poly((1.4, 0.6), (1.75, 1.6), (2.05, 0.6))]
    bench = [rrect(-2.4, -0.1, -0.6, 0.15, 0.08), poly((-2.4, 0.15), (-2.4, 0.9), (-2.1, 0.9), (-2.1, 0.15), closed=False)]
    front_fork = [[(2.2, 0.1), (2.3, -1.4)], arc(2.3, -1.4, 0.7, 0.4, 2.7, 14)]
    lamp = [circle(2.5, 0.35, 0.15, 12)]
    fringe = zigzag(-2.6, 1.7, 1.6, 0.08, 14)
    w = wheel(-1.6, -0.9, 0.55) + wheel(2.3, -1.4, 0.5)
    return make("Tuk-Tuk Rickshaw", canopy + posts + [tub] + screen + bench + front_fork + lamp + [fringe] + w)


# ---------------------------------------------------------------- parts & scenes

@design("vehicles_steering_wheel", T)
def steering_wheel(rng):
    rim = [circle(0, 0, 2.8, 160), circle(0, 0, 2.3, 140)]
    grips = [arc(0, 0, 2.55, math.radians(a - 12), math.radians(a + 12), 8) for a in (150, 30)]
    hub = rrect(-0.9, -0.8, 0.9, 0.5, 0.35)
    spokes = [poly((-0.9, 0.0), (-2.32, 0.4), (-2.32, -0.4), (-0.9, -0.5), closed=False), poly((0.9, 0.0), (2.32, 0.4), (2.32, -0.4), (0.9, -0.5), closed=False),
              poly((-0.35, -0.8), (-0.5, -2.25), closed=False), poly((0.35, -0.8), (0.5, -2.25), closed=False)]
    emblem = [ellipse(0, -0.15, 0.45, 0.28, 24), ellipse(0, -0.15, 0.25, 0.14, 16)]
    return make("Steering Wheel", rim + grips + [hub] + spokes + emblem)


@design("vehicles_tire_rim", T)
def tire_rim(rng):
    pts = []
    n = 36
    for k in range(n):
        a0 = TAU * k / n
        pts += arc(0, 0, 2.9, a0, a0 + TAU / n * 0.55, 3) + arc(0, 0, 2.7, a0 + TAU / n * 0.55, a0 + TAU / n, 3)
    tread = chain(pts, [pts[0]])
    side = [circle(0, 0, 2.3, 140), circle(0, 0, 1.75, 120)]
    hub = circle(0, 0, 0.45, 30)
    spokes = []
    for k in range(5):
        a = math.pi / 2 + k * TAU / 5
        p = lambda r, da: (r * math.cos(a + da), r * math.sin(a + da))
        spokes.append(chain([p(0.45, -0.35)], quad(p(1.0, -0.15), p(1.75, -0.28), p(1.75, -0.28), 4)[1:], [p(1.75, 0.28)], [p(0.45, 0.35)]))
    nuts = [eye(0.25 * math.cos(math.pi / 2 + k * TAU / 5 + 0.6), 0.25 * math.sin(math.pi / 2 + k * TAU / 5 + 0.6), 0.06) for k in range(5)]
    grooves = [arc(0, 0, 2.5, a, a + 0.5, 8) for a in [k * TAU / 6 for k in range(6)]]
    return make("Tire and Alloy Rim", [tread, hub] + side + spokes + grooves, nuts)


@design("vehicles_v8_engine", T)
def v8_engine(rng):
    half = [(0, -2.3), (-1.2, -2.3), (-1.45, -1.6), (-1.55, -0.3), (-2.6, 0.75), (-2.15, 1.25), (-1.05, 0.25), (-1.0, 0.9), (0, 0.9)]
    outline = chain(half, mirror_x(half)[::-1][1:])
    seams = [[(-1.45, -1.6), (1.45, -1.6)]] + mirror_all([[(-1.55, -0.3), (-1.05, 0.25)], [(-2.0, 0.2), (-1.55, 0.65)]])
    blower = [rrect(-1.1, 0.9, 1.1, 1.8, 0.15)] + [[(-1.1, y), (1.1, y)] for y in (1.2, 1.5)]
    scoop = [poly((-0.9, 1.8), (-0.8, 2.6), (0.8, 2.6), (0.9, 1.8), closed=False), rect(-0.6, 2.0, 0.6, 2.4), [(0.0, 2.0), (0.0, 2.4)]]
    pulleys = [circle(0, -1.0, 0.45, 30), circle(0, -1.0, 0.12, 10), circle(0, 1.35, 0.25, 18)]
    belt = [[(-0.45, -1.0), (-0.25, 1.35)], [(0.45, -1.0), (0.25, 1.35)]]
    headers = mirror_all([tube([(-1.5, -0.7), (-2.4, -1.0), (-2.7, -2.3)], 0.28)]) + [tube([(-1.5, -0.7), (-2.4, -1.0), (-2.7, -2.3)], 0.28)]
    return make("Hot Rod V8 Engine", [outline] + seams + blower + scoop + pulleys + belt + headers)


@design("vehicles_car_wash", T)
def car_wash(rng):
    frame = [poly((-3.4, -1.6), (-3.4, 2.4), (3.4, 2.4), (3.4, -1.6), closed=False), poly((-3.0, -1.6), (-3.0, 2.0), (3.0, 2.0), (3.0, -1.6), closed=False)]
    brush_l = [rect(-2.9, -1.3, -2.4, 1.9)] + [wave(-2.9, -2.4, y, 0.06, 1.5, 12) for y in (-0.8, -0.2, 0.4, 1.0, 1.6)]
    brush_t = [rrect(-1.9, 1.5, 1.9, 1.95, 0.2)]
    y, wh = -1.0, [(-1.2, 0.45), (1.3, 0.45)]
    top = [(-2.2, y), (-2.2, -0.35), (-1.3, -0.25), (-0.7, 0.45), (0.6, 0.45), (1.1, -0.2), (2.2, -0.35), (2.2, y)]
    car = [body(top, y, wh), poly((-1.0, -0.2), (-0.6, 0.32), (0.45, 0.32), (0.85, -0.2))] + wheels_at(wh, y)
    bubbles = [circle(x, yy, r, 18) for x, yy, r in [(-1.8, 0.8, 0.3), (-1.2, 1.1, 0.2), (1.5, 0.75, 0.3), (2.2, 1.1, 0.22), (0.2, 0.95, 0.22), (-2.1, 0.0, 0.18)]]
    drops = [lens((x, yy), (x, yy + 0.35), 0.35) for x, yy in [(-0.6, 0.85), (0.9, 0.95)]]
    return make("Car Wash", frame + brush_l + mirror_all(brush_l) + brush_t + car + bubbles + drops + [ground(-3.6, 3.6, -1.45)])


@design("vehicles_classic_front", T)
def classic_front(rng):
    half_body = [(0, -1.2), (-2.6, -1.2), (-2.9, -0.8), (-2.9, 0.3), (-2.4, 0.6), (-1.8, 0.65), (-1.4, 1.9), (0, 1.95)]
    outline = chain(half_body, mirror_x(half_body)[::-1][1:])
    screen = poly((-1.2, 0.75), (-1.1, 1.75), (1.1, 1.75), (1.2, 0.75))
    lamps = [circle(-2.1, 0.0, 0.42, 30), circle(-2.1, 0.0, 0.25, 20), circle(2.1, 0.0, 0.42, 30), circle(2.1, 0.0, 0.25, 20)]
    grille = [rrect(-1.2, -0.75, 1.2, 0.35, 0.25)] + [[(x, -0.7), (x, 0.3)] for x in (-0.8, -0.4, 0.0, 0.4, 0.8)]
    bumper = [rrect(-3.1, -1.45, 3.1, -0.95, 0.2)]
    plate = [rect(-0.5, -1.4, 0.5, -1.0)]
    tyres = [rrect(-2.7, -1.9, -2.0, -1.45, 0.1), rrect(2.0, -1.9, 2.7, -1.45, 0.1)]
    mirrors = [[(-2.4, 0.6), (-2.7, 0.95)], ellipse(-2.8, 1.05, 0.2, 0.14, 12), [(2.4, 0.6), (2.7, 0.95)], ellipse(2.8, 1.05, 0.2, 0.14, 12)]
    hood = [[(-0.9, 0.65), (-0.6, 0.4)], [(0.9, 0.65), (0.6, 0.4)]]
    return make("Classic Car Front View", [outline, screen] + lamps + grille + bumper + plate + tyres + mirrors + hood)


@design("vehicles_speedometer", T)
def speedometer(rng):
    a0, a1 = math.radians(225), math.radians(-45)
    face = [circle(0, 0, 2.8, 160), circle(0, 0, 2.5, 140)]
    ticks = []
    for k in range(13):
        a = a0 + (a1 - a0) * k / 12
        r0 = 1.85 if k % 2 == 0 else 2.1
        ticks.append([(r0 * math.cos(a), r0 * math.sin(a)), (2.35 * math.cos(a), 2.35 * math.sin(a))])
    red = [arc(0, 0, 2.2, a1 + 0.5, a1, 10)]
    na = a0 + (a1 - a0) * 0.62
    needle = [poly((0.12 * math.cos(na + math.pi / 2), 0.12 * math.sin(na + math.pi / 2)), (2.0 * math.cos(na), 2.0 * math.sin(na)),
                   (0.12 * math.cos(na - math.pi / 2), 0.12 * math.sin(na - math.pi / 2)))]
    hub = [circle(0, 0, 0.3, 20)]
    odo = [rect(-0.8, -1.5, 0.8, -1.05)] + [[(x, -1.5), (x, -1.05)] for x in (-0.4, 0.0, 0.4)]
    fuel = [arc(0, -0.2, 0.9, math.radians(200), math.radians(340), 12)]
    return make("Speedometer Gauge", face + ticks + red + needle + hub + odo + fuel)
