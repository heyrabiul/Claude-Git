"""Trains niche, part 2 (pictures 10-54)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "trains"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


def wheels(xs, y, r):
    out = []
    for x in xs:
        out += [circle(x, y, r, 40), circle(x, y, r * 0.3, 14)]
    return out


def track(y=-1.6, x0=-3.6, x1=3.6, ties=9):
    """Side-view rail with sleepers underneath."""
    out = [[(x0, y), (x1, y)]]
    for k in range(ties):
        x = x0 + 0.3 + (x1 - x0 - 0.6) * k / (ties - 1)
        out.append(rect(x - 0.2, y - 0.25, x + 0.2, y))
    return out


def bogie(cx, y, span=1.1, r=0.38):
    """Two-axle truck: wheels plus side frame."""
    out = wheels((cx - span / 2, cx + span / 2), y, r)
    out.append(rrect(cx - span / 2 - 0.35, y + r * 0.5, cx + span / 2 + 0.35, y + r * 0.5 + 0.25, 0.08))
    return out


def couplers(x0, x1, y):
    return [rect(x0 - 0.3, y - 0.1, x0, y + 0.1), rect(x1, y - 0.1, x1 + 0.3, y + 0.1)]


def pine(x, y, h):
    w = h * 0.4
    return poly((x - w, y), (x, y + h), (x + w, y), closed=True)


# ---------------------------------------------------------------- locomotives

@design("trains_diesel_loco", T)
def diesel_loco(rng):
    frame = rect(-3.4, -0.6, 3.4, -0.3)
    hood = poly((1.5, -0.3), (-3.0, -0.3), (-3.0, 1.15), (1.5, 1.15), closed=False)
    cab = poly((1.5, -0.3), (1.5, 1.85), (2.9, 1.85), (2.9, -0.3), closed=False)
    roof = rrect(1.35, 1.85, 3.05, 2.05, 0.08)
    nose = poly((2.9, 0.9), (3.35, 0.9), (3.35, -0.3), closed=False)
    wins = [rect(1.7, 0.9, 2.3, 1.6), rect(2.45, 0.9, 2.75, 1.6)]
    louvers = [[(x, 0.25), (x, 0.85)] for x in (-2.7, -2.45, -2.2, -1.95)] + [[(x, 0.25), (x, 0.85)] for x in (0.2, 0.45, 0.7)]
    doors = [rect(-1.4, -0.15, -0.6, 0.95)]
    fans = [ellipse(-2.3, 1.15, 0.45, 0.12, 20), ellipse(-0.9, 1.15, 0.45, 0.12, 20)]
    horn = [rect(2.0, 2.05, 2.45, 2.25)]
    lamp = [arc(3.35, 0.55, 0.18, -math.pi / 2, math.pi / 2, 8)]
    tank = [rrect(-1.0, -1.1, 0.7, -0.6, 0.2)]
    stripe = [[(-3.0, 0.05), (-1.4, 0.05)], [(-0.6, 0.05), (2.9, 0.05)]]
    return make("Diesel Locomotive", [frame, hood, cab, roof, nose] + wins + louvers + doors + fans + horn + lamp + tank + stripe
                + bogie(-2.2, -1.0, 1.2, 0.4) + bogie(2.2, -1.0, 1.2, 0.4) + track(-1.4))


@design("trains_electric_loco", T)
def electric_loco(rng):
    body = poly((-3.1, -0.4), (-3.4, 0.5), (-3.0, 1.5), (3.0, 1.5), (3.4, 0.5), (3.1, -0.4))
    wins = [poly((-3.25, 0.6), (-2.95, 1.35), (-2.4, 1.35), (-2.4, 0.6)), poly((3.25, 0.6), (2.95, 1.35), (2.4, 1.35), (2.4, 0.6))]
    grilles = [rect(-1.8 + 1.0 * k, 0.4, -1.1 + 1.0 * k, 1.15) for k in range(4)]
    stripe = [[(-3.3, 0.05), (3.3, 0.05)]]
    panto = [poly((-1.0, 1.5), (0.4, 2.25), (-0.4, 2.95), closed=False), [(-0.9, 2.95), (0.2, 2.95)], rect(-1.3, 1.5, -0.7, 1.65)]
    wire = [[(-3.6, 3.0), (3.6, 3.0)], [(-3.6, 3.5), (3.6, 3.5)]] + [[(x, 3.0), (x, 3.5)] for x in (-2.8, -1.2, 1.2, 2.8)]
    return make("Electric Locomotive", [body] + wins + grilles + stripe + panto + wire
                + bogie(-2.0, -0.85, 1.2, 0.38) + bogie(2.0, -0.85, 1.2, 0.38) + track(-1.23))


@design("trains_stephenson_rocket", T)
def stephenson_rocket(rng):
    boiler = rrect(-1.6, -0.2, 1.4, 0.8, 0.45)
    firebox = rrect(-2.4, -0.6, -1.5, 1.0, 0.2)
    chimney = [poly((1.05, 0.7), (1.0, 3.0), (1.4, 3.0), (1.35, 0.7), closed=False), rect(0.9, 3.0, 1.5, 3.2)]
    cyl = [transform(rect(-0.6, -0.15, 0.6, 0.15), dx=-1.4, dy=0.0, rot=-0.65)]
    rod = [[(-0.9, -0.4), (1.0, -1.15)]]
    big = [circle(1.0, -1.15, 1.0, 60), circle(1.0, -1.15, 0.15, 12)] + [[(1.0 + 0.15 * math.cos(a), -1.15 + 0.15 * math.sin(a)), (1.0 + 0.95 * math.cos(a), -1.15 + 0.95 * math.sin(a))] for a in [k * TAU / 12 for k in range(12)]]
    small = [circle(-1.9, -1.55, 0.6, 40), circle(-1.9, -1.55, 0.12, 10)]
    frame = [[(-2.6, -0.65), (2.1, -0.65)]]
    tender = [rect(-3.9, -1.1, -2.75, -0.9), rrect(-3.8, -0.9, -2.85, 0.3, 0.25), [(-3.8, -0.5), (-2.85, -0.5)], [(-3.8, -0.1), (-2.85, -0.1)], circle(-3.3, -1.7, 0.45, 30), circle(-3.3, -1.7, 0.12, 10)]
    smoke = [circle(1.6, 3.5, 0.3, 20), circle(2.2, 3.7, 0.38, 22), circle(2.95, 3.65, 0.45, 26)]
    return make("Stephenson's Rocket", [boiler, firebox] + chimney + cyl + rod + big + small + frame + tender + smoke + track(-2.15, -3.8, 2.4, 7))


@design("trains_steam_front", T)
def steam_front(rng):
    boiler = circle(0, 0.6, 1.9, 120)
    door = [circle(0, 0.6, 1.4, 100), circle(0, 0.6, 0.25, 18)]
    dogs = [[(1.4 * math.cos(a) * 0.7, 0.6 + 1.4 * math.sin(a) * 0.7), (1.4 * math.cos(a) * 0.95, 0.6 + 1.4 * math.sin(a) * 0.95)] for a in [k * TAU / 8 for k in range(8)]]
    stack = [poly((-0.45, 2.45), (-0.65, 3.3), (0.65, 3.3), (0.45, 2.45), closed=False), rect(-0.8, 3.3, 0.8, 3.5)]
    lamp = [rrect(-0.5, 1.95, 0.5, 2.6, 0.1), circle(0, 2.27, 0.22, 16)]
    plate = [ellipse(0, 1.15, 0.55, 0.28, 24)]
    beam = rect(-2.6, -1.6, 2.6, -1.1)
    buffers = [circle(-2.0, -1.35, 0.35, 24), circle(2.0, -1.35, 0.35, 24)]
    cow = poly((-2.2, -1.6), (2.2, -1.6), (1.0, -2.8), (-1.0, -2.8))
    bars = [[(x, -1.6), (x * 0.45, -2.8)] for x in (-1.3, -0.45, 0.45, 1.3)]
    steps = [[(-2.6, -1.1), (-2.6, -0.4)], [(2.6, -1.1), (2.6, -0.4)], [(-2.6, -0.4), (-1.6, -0.4)], [(2.6, -0.4), (1.6, -0.4)]]
    return make("Steam Engine Front View", [boiler, beam, cow] + door + dogs + stack + lamp + plate + buffers + bars + steps)


@design("trains_bullet_front", T)
def bullet_front(rng):
    nose = chain([(-2.4, -2.4)], cubic((-2.4, -2.4), (-2.6, 1.0), (-1.6, 2.6), (0, 2.7), 30), cubic((0, 2.7), (1.6, 2.6), (2.6, 1.0), (2.4, -2.4), 30), [(-2.4, -2.4)])
    screen = chain(cubic((-1.5, 1.1), (-1.3, 2.1), (1.3, 2.1), (1.5, 1.1), 24), quad((1.5, 1.1), (0, 0.8), (-1.5, 1.1), 16))
    lamps = [lens((-1.9, -0.6), (-1.0, -0.4), 0.25), lens((1.9, -0.6), (1.0, -0.4), 0.25)]
    beak = [quad((-1.6, -1.2), (0, -0.4), (1.6, -1.2), 20), quad((-1.6, -1.2), (0, -1.6), (1.6, -1.2), 20)]
    stripe = [[(-2.4, -1.9), (2.4, -1.9)]]
    rails = [[(-1.8, -2.4), (-3.0, -3.2)], [(1.8, -2.4), (3.0, -3.2)], [(-2.6, -2.9), (2.6, -2.9)]]
    return make("Bullet Train Head-On", [nose, screen] + lamps + beak + stripe + rails)


@design("trains_snowplow", T)
def snowplow(rng):
    body = rect(-3.2, -0.5, 1.2, 1.7)
    roof = [quad((-3.35, 1.7), (-1.0, 2.15), (1.35, 1.7), 16)]
    hood = poly((1.2, -0.5), (1.2, 2.1), (2.0, 2.1), (2.0, -0.5), closed=False)
    rotor = [circle(2.6, 0.6, 1.3, 80), circle(2.6, 0.6, 0.2, 14)] + [quad((2.6, 0.6), (2.6 + 0.9 * math.cos(a + 0.5), 0.6 + 0.9 * math.sin(a + 0.5)), (2.6 + 1.2 * math.cos(a), 0.6 + 1.2 * math.sin(a)), 10) for a in [k * TAU / 8 for k in range(8)]]
    chute = [poly((1.4, 2.1), (1.8, 2.9), (2.2, 2.7), (1.9, 2.1), closed=False)]
    spray = [circle(x, y, r, 18) for x, y, r in [(1.4, 3.3, 0.25), (0.8, 3.6, 0.3), (0.0, 3.7, 0.35), (-0.8, 3.6, 0.28)]]
    wins = [rect(-2.8, 0.6, -2.0, 1.3), rect(-1.4, 0.6, -0.6, 1.3)]
    flakes = [star(x, y, 0.25, 6, 0.3) for x, y in [(-3.0, 2.8), (-2.0, 3.3), (3.2, 2.7)]]
    drift = [quad((-3.6, -1.3), (-0.5, -0.9), (1.3, -1.1), 12)]
    return make("Rotary Snowplow Train", [body, hood] + roof + rotor + chute + spray + wins + flakes + bogie(-2.2, -0.95, 1.1, 0.38) + bogie(0.2, -0.95, 1.1, 0.38) + drift + track(-1.33))


@design("trains_toy_train", T)
def toy_train(rng):
    eng = [rect(-0.2, -0.6, 1.6, 0.4), rect(-0.2, 0.4, 0.8, 1.6), rect(-0.4, 1.6, 1.0, 1.85), poly((1.1, 0.4), (1.0, 1.4), (1.6, 1.4), (1.5, 0.4)),
           circle(0.3, 1.0, 0.25, 16), rect(1.6, -0.5, 1.9, 0.2)]
    car = [rect(-3.3, -0.6, -1.7, 0.4), rect(-3.1, 0.4, -2.4, 1.1), rect(-2.4, 0.4, -1.9, 0.9), circle(-2.75, 0.75, 0.2, 14)]
    car2 = [rect(-1.5, -0.6, -0.4, 0.4), poly((-1.35, 0.4), (-0.95, 1.2), (-0.55, 0.4))]
    links = [[(-1.7, -0.3), (-1.5, -0.3)], [(-0.4, -0.3), (-0.2, -0.3)]]
    wh = wheels((-2.9, -2.1, -1.25, -0.65, 0.25, 1.2), -0.8, 0.27)
    string = [cubic((1.9, -0.15), (2.6, 0.5), (2.4, -1.4), (3.2, -1.0), 30), circle(3.35, -0.95, 0.15, 12)]
    floor = [[(-3.6, -1.1), (3.6, -1.1)]]
    return make("Wooden Toy Train", eng + car + car2 + links + wh + string + floor)


# ---------------------------------------------------------------- city & mountain rail

@design("trains_tram", T)
def tram(rng):
    body = rrect(-3.2, -0.6, 3.2, 1.5, 0.35)
    roof = [poly((-3.3, 1.5), (-3.0, 1.8), (-1.8, 1.8), (-1.8, 2.1), (1.8, 2.1), (1.8, 1.8), (3.0, 1.8), (3.3, 1.5), closed=False)]
    wins = [rrect(-2.2 + 0.75 * k, 0.5, -1.65 + 0.75 * k, 1.3, 0.1) for k in range(6)]
    doors = [rect(-3.0, -0.45, -2.4, 1.3), rect(2.4, -0.45, 3.0, 1.3)]
    band = [[(-2.4, 0.3), (2.4, 0.3)]]
    pole = [[(0.0, 2.1), (2.2, 3.1)], circle(2.25, 3.13, 0.1, 10)]
    wire = [[(-3.6, 3.25), (3.6, 3.25)]]
    lamp = [circle(3.25, 0.3, 0.15, 12)]
    fender = [poly((3.2, -0.6), (3.5, -0.9), (2.4, -0.9), closed=False)]
    return make("Vintage Streetcar", [body] + roof + wins + doors + band + pole + wire + lamp + fender + bogie(-1.6, -0.95, 1.0, 0.33) + bogie(1.6, -0.95, 1.0, 0.33) + [[(-3.6, -1.28), (3.6, -1.28)]])


@design("trains_cable_car", T)
def cable_car(rng):
    a = 0.12
    parts = [rect(-2.8, -0.6, 2.8, -0.3), rect(-1.2, -0.3, 1.2, 1.6), rrect(-3.0, 1.6, 3.0, 1.9, 0.1)]
    parts += [rect(-1.0 + 0.6 * k, 0.6, -0.6 + 0.6 * k, 1.35) for k in range(4)]
    parts += [[(x, -0.3), (x, 1.6)] for x in (-2.7, -2.0, 2.0, 2.7)]
    parts += [[(-2.7, 0.2), (-1.2, 0.2)], [(1.2, 0.2), (2.7, 0.2)]]
    parts += [arc(0, 1.9, 0.25, 0, math.pi, 10), [(0, 2.15), (0, 2.4)]]
    parts += wheels((-1.8, 1.8), -0.85, 0.3)
    parts += [[(-3.8, -1.15), (3.8, -1.15)], [(-3.8, -1.5), (3.8, -1.5)]]
    parts += [[(-0.1, -0.6), (-0.1, -1.3)], [(0.1, -0.6), (0.1, -1.3)]]
    parts += [transform(rect(-0.3, -0.05, 0.3, 0.05), dx=-2.3, dy=-0.05), rect(-3.1, -0.45, -2.8, -0.25)]
    return make("San Francisco Cable Car", [transform(p, rot=a) for p in parts])


@design("trains_funicular", T)
def funicular(rng):
    a = math.atan(0.6)
    k = 0.6
    outline = []
    for i in range(4):
        x0, x1 = -2.0 + i, -1.0 + i
        fl = k * x0 + 0.3
        outline += [(x0, fl + 1.3), (x1, fl + 1.3)]
    top = outline
    body = chain([(-2.0, k * -2.0)], top, [(2.0, k * 2.0), (-2.0, k * -2.0)])
    wins = [rrect(-1.85 + i, k * (-2.0 + i) + 0.75, -1.15 + i, k * (-2.0 + i) + 1.4, 0.08) for i in range(4)]
    slope = [[(-3.6, k * -3.6 - 0.4), (3.6, k * 3.6 - 0.4)]]
    whs = [circle(x, k * x - 0.2, 0.2, 16) for x in (-1.6, 1.6)]
    hill = [poly((-3.6, -3.0), (-3.6, k * -3.6 - 0.6), (3.6, k * 3.6 - 0.6), (3.6, -3.0), closed=False)]
    station = [rect(2.2, 1.8, 3.6, 3.0), poly((2.0, 3.0), (2.9, 3.6), (3.8, 3.0), closed=False), circle(2.9, 2.4, 0.3, 18)]
    trees = [pine(-2.5, -2.5, 1.0), pine(-1.2, -2.3, 0.8), pine(1.2, -1.2, 0.8)]
    return make("Mountain Funicular", [body] + wins + slope + whs + hill + station + trees)


@design("trains_monorail", T)
def monorail(rng):
    body = chain([(-3.0, 0.0)], cubic((-3.0, 0.0), (-3.6, 0.2), (-3.5, 1.5), (-2.4, 1.6), 20), [(2.4, 1.6)],
                 cubic((2.4, 1.6), (3.5, 1.5), (3.6, 0.2), (3.0, 0.0), 20), [(-3.0, 0.0)])
    wins = [rrect(-2.0 + 0.85 * k, 0.75, -1.4 + 0.85 * k, 1.3, 0.12) for k in range(5)]
    cabs = [chain(quad((-3.35, 0.7), (-3.2, 1.35), (-2.5, 1.4), 10), [(-2.5, 0.7), (-3.35, 0.7)]), chain(quad((3.35, 0.7), (3.2, 1.35), (2.5, 1.4), 10), [(2.5, 0.7), (3.35, 0.7)])]
    stripe = [[(-3.2, 0.4), (3.2, 0.4)]]
    skirt = [[(-2.6, 0.0), (-2.6, -0.35)], [(2.6, 0.0), (2.6, -0.35)]]
    beam = rect(-3.8, -0.75, 3.8, -0.35)
    pylons = [poly((x - 0.3, -0.75), (x - 0.2, -2.8), (x + 0.2, -2.8), (x + 0.3, -0.75), closed=False) for x in (-2.0, 2.0)]
    bases = [rect(x - 0.6, -3.0, x + 0.6, -2.8) for x in (-2.0, 2.0)]
    city = [poly((-3.6, -3.0), (-3.6, -1.6), (-3.0, -1.6), (-3.0, -2.2), (-2.6, -2.2), (-2.6, -3.0), closed=False),
            poly((3.6, -3.0), (3.6, -1.4), (3.0, -1.4), (3.0, -2.0), (2.6, -2.0), (2.6, -3.0), closed=False)]
    return make("Monorail", [body, beam] + wins + cabs + stripe + skirt + pylons + bases + city)


@design("trains_subway_tunnel", T)
def subway_tunnel(rng):
    tunnel = [circle(0, 0, 3.0, 160)]
    ribs = [arc(0, 0, 2.7, math.radians(20), math.radians(160), 40)]
    front = rrect(-1.7, -2.0, 1.7, 1.7, 0.4)
    screen = rrect(-1.4, 0.0, 1.4, 1.3, 0.2)
    sign = rect(-0.9, 1.35, 0.9, 1.6)
    door = [[(0, 0.0), (0, -1.6)]]
    lamps = [circle(-1.1, -0.8, 0.22, 16), circle(1.1, -0.8, 0.22, 16)]
    bumper = [rect(-1.8, -2.0, 1.8, -1.7)]
    rails = [[(-0.9, -2.0), (-2.0, -2.8)], [(0.9, -2.0), (2.0, -2.8)], [(-2.3, -2.4), (2.3, -2.4)]]
    lights = [circle(-2.3, 1.4, 0.15, 12), circle(2.3, 1.4, 0.15, 12)]
    return make("Subway Train in Tunnel", tunnel + ribs + [front, screen, sign] + door + lamps + bumper + rails + lights)


@design("trains_maglev", T)
def maglev(rng):
    body = chain([(-3.6, -0.1)], cubic((-3.6, -0.1), (-3.4, 0.9), (-2.4, 1.3), (-1.4, 1.3), 20), [(1.4, 1.3)],
                 cubic((1.4, 1.3), (2.4, 1.3), (3.4, 0.9), (3.6, -0.1), 20), [(-3.6, -0.1)])
    wins = [rrect(-1.6 + 0.65 * k, 0.55, -1.2 + 0.65 * k, 0.95, 0.1) for k in range(5)]
    cabs = [quad((-3.2, 0.45), (-2.8, 1.05), (-2.0, 1.1), 10), quad((3.2, 0.45), (2.8, 1.05), (2.0, 1.1), 10)]
    stripe = [[(-3.5, 0.2), (3.5, 0.2)]]
    way = [rect(-3.8, -0.75, 3.8, -0.45), rect(-1.0, -2.8, 1.0, -0.75)]
    gap = [wave(-3.0, 3.0, -0.27, 0.06, 10)]
    spd = [[(-4.4, y), (-3.9, y)] for y in (0.3, 0.8)]
    return make("Maglev Train", [body] + wins + cabs + stripe + way + gap + spd)


# ---------------------------------------------------------------- rolling stock

@design("trains_handcar", T)
def handcar(rng):
    deck = rect(-2.0, -0.5, 2.0, -0.2)
    post = [rect(-0.15, -0.2, 0.15, 1.0), circle(0, 1.0, 0.18, 14)]
    beam = [transform(rect(-2.0, -0.08, 2.0, 0.08), dy=1.0, rot=0.25)]
    handles = [[(-2.0 * math.cos(0.25) - 0.0, 1.0 - 2.0 * math.sin(0.25)), (-1.9, 0.25)], [(2.0 * math.cos(0.25), 1.0 + 2.0 * math.sin(0.25)), (2.0, 2.1)]]
    workers = []
    for x, hy, flip in ((-2.5, 1.2, -1), (2.5, 2.2, 1)):
        workers += [circle(x, hy + 0.85, 0.35, 24), [(x, hy + 0.5), (x, -0.2 + 0.8)], [(x, hy + 0.3), (x - flip * 0.6, hy - 0.05)],
                    [(x, 0.6), (x - 0.3, -0.2)], [(x, 0.6), (x + 0.3, -0.2)]]
    gear = [circle(0, -0.75, 0.25, 18)]
    w = wheels((-1.3, 1.3), -0.8, 0.45)
    return make("Railroad Handcar", [deck] + post + beam + handles + workers + gear + w + track(-1.25))


@design("trains_mine_cart", T)
def mine_cart(rng):
    bucket = poly((-2.0, -0.6), (-2.5, 1.0), (2.5, 1.0), (2.0, -0.6))
    rim = rect(-2.7, 1.0, 2.7, 1.25)
    ribs = [[(x, -0.6), (x * 1.22, 1.0)] for x in (-1.0, 0.0, 1.0)]
    rivets = [eye(x, 0.0, 0.07) for x in (-1.55, -0.5, 0.5, 1.55)]
    ore = [poly((-2.2, 1.25), (-1.8, 1.9), (-1.2, 1.7), (-0.8, 2.3), (-0.2, 1.9), (0.4, 2.4), (1.0, 1.85), (1.6, 2.1), (2.2, 1.25), closed=False)]
    gems = [poly((-0.6, 1.55), (-0.4, 1.8), (-0.2, 1.55), (-0.4, 1.35)), poly((1.0, 1.45), (1.2, 1.7), (1.4, 1.45), (1.2, 1.3))]
    w = wheels((-1.3, 1.3), -0.85, 0.45)
    pick = [[(2.8, -1.25), (3.4, 2.0)], quad((2.6, 2.2), (3.4, 2.4), (3.9, 1.6), 10)]
    lantern = [rrect(-3.6, -1.25, -2.9, -0.3, 0.1), arc(-3.25, -0.3, 0.3, 0, math.pi, 8)]
    beams = [[(-3.8, 3.0), (3.8, 3.0)]]
    return make("Mine Cart Full of Ore", [bucket, rim] + ribs + ore + gems + w + pick + lantern + beams + track(-1.3), rivets)


@design("trains_coal_tender", T)
def coal_tender(rng):
    box = poly((-2.6, -0.5), (-2.6, 1.2), (2.6, 1.2), (2.6, -0.5))
    flare = [poly((-2.6, 1.2), (-2.9, 1.6), (2.9, 1.6), (2.6, 1.2), closed=False)]
    coal = [chain([(-2.8, 1.6)], [(-2.8 + 0.4 * k, 1.6 + (0.35 + 0.2 * math.sin(k * 1.7)) * math.sin(math.pi * k / 14)) for k in range(1, 14)], [(2.8, 1.6)])]
    lumps = [poly((x - 0.2, y), (x, y + 0.2), (x + 0.2, y), (x, y - 0.15)) for x, y in [(-1.6, 2.1), (-0.3, 2.3), (0.9, 2.2), (1.9, 1.95)]]
    hatch = [rect(1.5, 1.6, 2.2, 1.75)]
    lettering = [rrect(-1.8, 0.1, 1.8, 0.85, 0.15)]
    shovel = [[(-2.4, 2.0), (-3.4, 3.0)], lens((-3.3, 2.9), (-3.8, 3.4), 0.3)]
    return make("Coal Tender", [box] + flare + coal + lumps + hatch + lettering + shovel + couplers(-2.6, 2.6, -0.3)
                + bogie(-1.5, -0.95, 1.0, 0.36) + bogie(1.5, -0.95, 1.0, 0.36) + track(-1.31))


@design("trains_tank_car", T)
def tank_car(rng):
    tank = rrect(-3.2, -0.3, 3.2, 1.7, 1.0)
    dome = [chain([(-0.5, 1.7), (-0.5, 2.1)], arc(0, 2.1, 0.5, math.pi, 0, 12), [(0.5, 1.7)]), rect(-0.7, 2.6, 0.7, 2.75)]
    bands = [[(x, -0.3), (x, 1.7)] for x in (-1.8, 1.8)]
    walk = [[(-3.0, -0.45), (3.0, -0.45)]]
    ladder = [[(-0.3, -0.45), (-0.3, 1.7)], [(0.3, -0.45), (0.3, 1.7)]] + [[(-0.3, y), (0.3, y)] for y in (-0.05, 0.4, 0.85, 1.3)]
    label = [rrect(-1.6, 0.55, -0.55, 1.05, 0.1), rrect(0.55, 0.55, 1.6, 1.05, 0.1)]
    deck = rect(-3.0, -0.65, 3.0, -0.45)
    return make("Railroad Tank Car", [tank, deck] + dome + bands + walk + ladder + label + couplers(-3.0, 3.0, -0.55)
                + bogie(-2.1, -1.05, 1.0, 0.36) + bogie(2.1, -1.05, 1.0, 0.36) + track(-1.41))


@design("trains_log_car", T)
def log_car(rng):
    deck = rect(-3.2, -0.6, 3.2, -0.3)
    logs = []
    for row, (y, n, off) in enumerate([(-0.3, 4, 0.0), (0.3, 3, 0.4), (0.9, 2, 0.8)]):
        for k in range(n):
            x0 = -3.0 + off
            logs.append(rrect(x0 - 0.1, y, 3.1 - off, y + 0.6, 0.3) if k == 0 else [])
    logs = [l for l in logs if l]
    ends = []
    for y, n, off in [(-0.3, 4, 0.0), (0.3, 3, 0.4), (0.9, 2, 0.8)]:
        ends += [circle(3.1 - off - 0.3, y + 0.3, 0.22, 14)]
        ends += [spiral(3.1 - off - 0.3, y + 0.3, 0.02, 0.14, 1.5, 30)]
    bark = [[(-2.4, 0.0), (-1.2, 0.05)], [(0.2, 0.6), (1.5, 0.55)], [(-1.6, 1.2), (-0.2, 1.25)]]
    stakes = [[(-3.1, -0.3), (-3.1, 1.8)], [(-2.9, -0.3), (-2.9, 1.8)], [(3.1, -0.3), (3.1, 1.8)], [(2.9, -0.3), (2.9, 1.8)]]
    chain_ = [quad((-2.0, 1.5), (-1.0, 2.0), (0.0, 1.5), 10), quad((0.0, 1.5), (1.0, 2.0), (2.0, 1.5), 10)]
    return make("Logging Flatcar", [deck] + logs + ends + bark + stakes + chain_ + couplers(-3.2, 3.2, -0.45)
                + bogie(-2.1, -1.0, 1.0, 0.36) + bogie(2.1, -1.0, 1.0, 0.36) + track(-1.36))


@design("trains_hopper_car", T)
def hopper_car(rng):
    body = poly((-3.0, 1.8), (3.0, 1.8), (3.0, 0.4), (2.2, -0.4), (1.4, -0.4), (0.6, 0.3), (-0.6, 0.3), (-1.4, -0.4), (-2.2, -0.4), (-3.0, 0.4))
    chutes = [rect(-2.1, -0.75, -1.5, -0.4), rect(1.5, -0.75, 2.1, -0.4)]
    ribs = [[(x, 1.8), (x, 0.4 if abs(x) > 2.0 else 0.6)] for x in (-2.4, -1.4, -0.4, 0.6, 1.6, 2.6)]
    top = [[(-3.0, 1.55), (3.0, 1.55)]]
    load = [quad((-2.8, 1.8), (0, 2.6), (2.8, 1.8), 30)]
    end_ladders = [[(-3.2, 0.2), (-3.2, 1.8)], [(3.2, 0.2), (3.2, 1.8)]]
    return make("Grain Hopper Car", [body] + chutes + ribs + top + load + end_ladders + bogie(-2.3, -1.05, 1.0, 0.36) + bogie(2.3, -1.05, 1.0, 0.36) + track(-1.41))


@design("trains_cattle_car", T)
def cattle_car(rng):
    box = rect(-3.0, -0.6, 3.0, 1.8)
    roof = [rect(-3.2, 1.8, 3.2, 2.0)]
    slats = [[(-3.0, y), (-0.8, y)] for y in (0.0, 0.6, 1.2)] + [[(0.8, y), (3.0, y)] for y in (0.0, 0.6, 1.2)]
    door = [rect(-0.8, -0.6, 0.8, 1.8), [(-0.8, -0.6), (0.8, 1.8)]]
    cows = []
    for cx in (-1.9, 1.9):
        cows += [ellipse(cx, 0.9, 0.5, 0.42, 30), ellipse(cx, 0.6, 0.32, 0.2, 20),
                 lens((cx - 0.45, 1.15), (cx - 0.95, 1.3), 0.3), lens((cx + 0.45, 1.15), (cx + 0.95, 1.3), 0.3),
                 quad((cx - 0.25, 1.3), (cx - 0.35, 1.6), (cx - 0.15, 1.65), 6), quad((cx + 0.25, 1.3), (cx + 0.35, 1.6), (cx + 0.15, 1.65), 6)]
    eyes_ = [eye(cx + d, 1.0, 0.07) for cx in (-1.9, 1.9) for d in (-0.2, 0.2)] + [eye(cx + d, 0.6, 0.05) for cx in (-1.9, 1.9) for d in (-0.12, 0.12)]
    return make("Cattle Car with Cows", [box] + roof + slats + door + cows + couplers(-3.0, 3.0, -0.4)
                + bogie(-2.0, -1.05, 1.0, 0.36) + bogie(2.0, -1.05, 1.0, 0.36) + track(-1.41), eyes_)


@design("trains_observation_car", T)
def observation_car(rng):
    body = rrect(-3.3, -0.6, 3.3, 1.2, 0.25)
    dome = chain([(-1.8, 1.2)], cubic((-1.8, 1.2), (-1.4, 2.4), (1.4, 2.4), (1.8, 1.2), 30))
    panes = [[(x, 1.2), (x * 0.85, 2.05 - 0.15 * abs(x))] for x in (-1.0, 0.0, 1.0)]
    wins = [rrect(-3.0 + 0.8 * k, 0.2, -2.45 + 0.8 * k, 0.9, 0.1) for k in range(8)]
    stripe = [[(-3.3, -0.1), (3.3, -0.1)]]
    rail = [poly((3.3, 0.0), (3.7, 0.0), (3.7, -0.6), closed=False)]
    return make("Observation Dome Car", [body, dome] + panes + wins + stripe + rail
                + bogie(-2.2, -1.0, 1.0, 0.36) + bogie(2.2, -1.0, 1.0, 0.36) + track(-1.36))


# ---------------------------------------------------------------- interiors

@design("trains_dining_car", T)
def dining_car(rng):
    window = rrect(-2.4, 0.2, 2.4, 2.6, 0.3)
    hills = [chain(quad((-2.4, 0.9), (-1.2, 2.0), (0.0, 1.1), 12), quad((0.0, 1.1), (1.2, 2.2), (2.4, 1.0), 12))]
    sun = [circle(1.4, 2.0, 0.25, 16)]
    curtains = [chain([(-2.4, 2.6)], quad((-1.6, 1.6), (-2.2, 0.4), (-2.2, 0.4), 10), [(-2.4, 0.4)]), chain([(2.4, 2.6)], quad((1.6, 1.6), (2.2, 0.4), (2.2, 0.4), 10), [(2.4, 0.4)])]
    table = [poly((-2.6, -0.2), (2.6, -0.2), (2.3, -1.0), (-2.3, -1.0)), [(0, -1.0), (0, -2.6)], [(-0.8, -2.6), (0.8, -2.6)]]
    plates = [ellipse(-1.2, -0.55, 0.6, 0.2, 30), ellipse(-1.2, -0.55, 0.35, 0.1, 20), ellipse(1.2, -0.55, 0.6, 0.2, 30), ellipse(1.2, -0.55, 0.35, 0.1, 20)]
    lamp = [[(0, -0.55), (0, 0.4)], poly((-0.4, 0.4), (-0.2, 0.9), (0.2, 0.9), (0.4, 0.4))]
    vase = [lens((0.1, -0.3), (0.1, 0.1), 0.3)]
    seats = [rrect(-3.4, -2.6, -2.8, 0.6, 0.2), rrect(2.8, -2.6, 3.4, 0.6, 0.2)]
    return make("Dining Car Table", [window] + hills + sun + curtains + table + plates + lamp + seats)


@design("trains_sleeper_car", T)
def sleeper_car(rng):
    frame = rect(-2.8, -2.6, 2.8, 2.8)
    bunks = [rect(-2.8, -1.6, 2.8, -1.3), rect(-2.8, 0.6, 2.8, 0.9)]
    pillows = [rrect(-2.6, -1.3, -1.5, -0.9, 0.15), rrect(-2.6, 0.9, -1.5, 1.3, 0.15)]
    blankets = [chain([(-1.6, -1.3)], quad((0.5, -0.6), (2.6, -1.0), (2.6, -1.0), 12), [(2.6, -1.3)]), chain([(-1.6, 0.9)], quad((0.5, 1.6), (2.6, 1.2), (2.6, 1.2), 12), [(2.6, 0.9)])]
    window = [rrect(-1.0, 1.6, 1.0, 2.6, 0.2), arc(0.3, 2.1, 0.3, -1.6, 1.6, 10), quad((0.3, 1.8), (0.0, 2.1), (0.3, 2.4), 8)]
    curtain = [wave(-2.8, 2.8, 2.6, 0.05, 10)]
    ladder = [[(1.8, -1.3), (2.2, 0.6)], [(2.3, -1.3), (2.7, 0.6)]] + [[(1.8 + 0.4 * t, -1.3 + 1.9 * t), (2.3 + 0.4 * t, -1.3 + 1.9 * t)] for t in (0.25, 0.5, 0.75)]
    zz = [poly((-0.6, -0.2), (-0.2, -0.2), (-0.6, -0.5), (-0.2, -0.5), closed=False), poly((0.0, 0.1), (0.3, 0.1), (0.0, -0.15), (0.3, -0.15), closed=False)]
    floor = [[(-2.8, -2.0), (2.8, -2.0)]]
    shoes = [rrect(-1.4, -2.6, -0.7, -2.3, 0.12), rrect(-0.5, -2.6, 0.2, -2.3, 0.12)]
    return make("Sleeper Car Bunks", [frame] + bunks + pillows + blankets + window + curtain + ladder + zz + shoes)


@design("trains_cab_interior", T)
def cab_interior(rng):
    backhead = chain(arc(0, -0.5, 3.0, math.radians(20), math.radians(160), 60), [(-2.8, -3.0), (2.8, -3.0)], [(2.82, 0.53)])
    firedoor = [rrect(-1.0, -2.6, 1.0, -1.2, 0.2), [(-0.8, -1.9), (0.8, -1.9)], ellipse(0, -1.55, 0.35, 0.15, 16)]
    gauges = []
    for cx, cy, r in [(-1.0, 1.5, 0.6), (1.0, 1.5, 0.6), (0.0, 0.5, 0.45)]:
        gauges += [circle(cx, cy, r, 40), [(cx, cy), (cx + r * 0.7 * math.cos(1.0 + cx), cy + r * 0.7 * math.sin(1.0 + cx))]]
        gauges += [[(cx + r * 0.8 * math.cos(a), cy + r * 0.8 * math.sin(a)), (cx + r * math.cos(a), cy + r * math.sin(a))] for a in [math.radians(d) for d in (-30, 30, 90, 150, 210)]]
    glass = [rrect(1.8, -1.0, 2.1, 0.6, 0.1)]
    pipes = [[(-2.5, 0.8), (-2.5, -0.6), (-1.0, -0.6)], [(2.3, 1.0), (2.3, -1.4), (1.0, -1.4)]]
    lever = [[(-2.0, -1.0), (-1.4, 0.2)], circle(-1.35, 0.3, 0.15, 12)]
    shovel = [[(2.8, -3.0), (3.4, -1.0)], lens((2.6, -3.1), (2.9, -2.5), 0.35)]
    return make("Steam Locomotive Cab", [backhead] + firedoor + gauges + glass + pipes + lever + shovel)


# ---------------------------------------------------------------- scenery

def _little_train(x0, y, s=1.0):
    """Short train silhouette (engine + 2 cars) running right."""
    out = []
    eng = [rect(0.0, 0.0, 1.2, 0.5), rect(0.0, 0.5, 0.5, 1.0), rect(0.8, 0.5, 1.0, 0.85)]
    cars = [rect(-1.3 * (k + 1), 0.0, -1.3 * (k + 1) + 1.15, 0.7) for k in range(2)]
    for p in eng + cars:
        out.append(transform(p, dx=x0, dy=y, s=s))
    return out


@design("trains_trestle_bridge", T)
def trestle_bridge(rng):
    deck = rect(-3.6, 0.0, 3.6, 0.25)
    bents = []
    for x in (-2.7, -0.9, 0.9, 2.7):
        bents += [[(x - 0.4, 0.0), (x - 0.9, -2.8)], [(x + 0.4, 0.0), (x + 0.9, -2.8)]]
    braces = []
    for k, (ya, yb) in enumerate([(0.0, -1.4), (-1.4, -2.8)]):
        for x in (-2.7, -0.9, 0.9, 2.7):
            dx_a, dx_b = 0.4 + 0.5 * (-ya / 2.8), 0.4 + 0.5 * (-yb / 2.8)
            braces += [[(x - dx_a, ya), (x + dx_b, yb)], [(x + dx_a, ya), (x - dx_b, yb)]]
    tie = [[(-3.6, -1.4), (3.6, -1.4)]]
    river = [wave(-3.2, 3.2, -3.1, 0.08, 5)]
    canyon = [poly((-3.8, 0.0), (-3.8, -3.3), closed=False), poly((3.8, 0.0), (3.8, -3.3), closed=False)]
    train = _little_train(0.8, 0.25, 1.0)
    smoke = [circle(1.15, 1.6, 0.2, 14), circle(0.7, 1.9, 0.28, 18), circle(0.0, 2.05, 0.35, 22)]
    return make("Wooden Trestle Bridge", [deck] + bents + braces + tie + river + canyon + train + smoke)


@design("trains_stone_viaduct", T)
def stone_viaduct(rng):
    top = [[(-3.8, 0.8), (3.8, 0.8)], [(-3.8, 0.4), (3.8, 0.4)]]
    arches = []
    for k in range(4):
        cx = -2.7 + 1.8 * k
        arches.append(chain([(cx - 0.65, -2.8), (cx - 0.65, -0.6)], arc(cx, -0.6, 0.65, math.pi, 0, 20), [(cx + 0.65, -2.8)]))
        arches.append(arc(cx, -0.6, 0.85, math.radians(10), math.radians(170), 18))
    piers = [[(-3.8, 0.4), (-3.8, -2.8)], [(3.8, 0.4), (3.8, -2.8)]]
    water = [wave(-3.8, 3.8, -2.9, 0.07, 9)]
    train = _little_train(0.4, 0.8, 1.2)
    clouds = [chain(arc(-2.2, 2.4, 0.4, 0, math.pi, 10), arc(-2.8, 2.3, 0.3, 0.5, math.pi, 8)[::-1][::-1]), arc(2.6, 2.6, 0.35, 0, math.pi, 10)]
    return make("Stone Railway Viaduct", top + arches + piers + water + train + clouds)


@design("trains_mountain_pass", T)
def mountain_pass(rng):
    peaks = [poly((-3.8, -0.4), (-2.2, 2.4), (-1.0, 0.8), (0.4, 3.0), (2.0, 1.0), (2.8, 2.0), (3.8, 0.4), closed=False)]
    snow = [poly((-2.65, 1.6), (-2.2, 2.4), (-1.8, 1.7), (-2.2, 1.85), closed=True), poly((-0.1, 2.2), (0.4, 3.0), (0.95, 2.15), (0.4, 2.4), closed=True)]
    p0, p1, p2 = (-3.8, -2.6), (0.0, -0.4), (3.8, -1.2)
    curve = [quad(p0, p1, p2, 40), [(x, y - 0.4) for x, y in quad(p0, p1, p2, 40)]]

    def at(t):
        u = 1 - t
        x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
        y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
        dx = 2 * u * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0])
        dy = 2 * u * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1])
        return x, y, math.atan2(dy, dx)

    train = []
    x, y, r = at(0.66)
    engine = [rect(-0.7, 0.0, 0.7, 0.55), rect(-0.7, 0.55, -0.15, 1.0), rect(0.25, 0.55, 0.45, 0.9), poly((0.7, 0.0), (0.95, 0.0), (0.7, 0.3))]
    train += [transform(p, dx=x, dy=y, rot=r) for p in engine]
    smoke = [circle(x + 0.5, y + 1.25, 0.2, 14), circle(x + 0.05, y + 1.55, 0.28, 18), circle(x - 0.55, y + 1.7, 0.34, 20)]
    for t in (0.47, 0.30):
        x, y, r = at(t)
        train += [transform(rrect(-0.65, 0.0, 0.65, 0.65, 0.1), dx=x, dy=y, rot=r), transform(rect(-0.4, 0.3, 0.4, 0.5), dx=x, dy=y, rot=r)]
    trees = [pine(-3.2, -1.6, 1.0), pine(-2.6, -1.9, 0.8), pine(2.8, -2.8, 1.0), pine(2.0, -3.0, 0.8)]
    return make("Train Through the Mountains", peaks + snow + curve + train + smoke + trees)


@design("trains_tracks_perspective", T)
def tracks_perspective(rng):
    horizon = [[(-3.6, 1.0), (3.6, 1.0)]]
    rails = [[(-2.8, -3.0), (-0.12, 1.0)], [(-2.3, -3.0), (-0.07, 1.0)], [(2.8, -3.0), (0.12, 1.0)], [(2.3, -3.0), (0.07, 1.0)]]
    ties = []
    for k in range(9):
        t = 1 - (1 - k / 9) ** 0.0 if False else (k / 9) ** 1.6
        y = -2.8 + 3.7 * (1 - (1 - k / 9) ** 1.0) * (1 - 0.0)
        y = -2.8 + 3.7 * (1 - 0.82 ** (k * 1.2))
        w = 3.1 * (1.0 - (y + 3.0) / 4.0) + 0.1
        h = 0.18 * (1.0 - (y + 3.0) / 4.0) + 0.03
        ties.append(rect(-w, y - h, w, y + h))
    poles = []
    for x0, s in ((-3.2, 1.0), (-1.9, 0.55), (-1.15, 0.3)):
        top = 1.0 + 2.2 * s
        poles += [[(x0, 1.0 - 3.6 * s + 0.6 * s), (x0, top)], [(x0 - 0.5 * s, top - 0.3 * s), (x0 + 0.5 * s, top - 0.3 * s)]]
    wire = [[(-3.2, 2.9), (-1.9, 2.04), (-1.15, 1.57), (-0.4, 1.1)]]
    sun = [arc(1.6, 1.0, 0.7, 0, math.pi, 20)] + [[(1.6 + 0.9 * math.cos(a), 1.0 + 0.9 * math.sin(a)), (1.6 + 1.2 * math.cos(a), 1.0 + 1.2 * math.sin(a))] for a in [k * math.pi / 6 for k in range(1, 6)]]
    return make("Railroad Tracks to the Horizon", horizon + rails + ties + poles + wire + sun)


@design("trains_roundhouse", T)
def roundhouse(rng):
    pit = [circle(0, -1.0, 1.6, 100), circle(0, -1.0, 1.4, 90)]
    bridge = [transform(rect(-1.4, -0.25, 1.4, 0.25), dy=-1.0, rot=0.5), circle(0, -1.0, 0.15, 12)]
    stalls = []
    for k in range(7):
        a = math.radians(30 + 20 * k)
        ca, sa = math.cos(a), math.sin(a)
        stalls.append([(1.6 * ca - 0.15 * sa, -1.0 + 1.6 * sa + 0.15 * ca), (3.0 * ca - 0.15 * sa, -1.0 + 3.0 * sa + 0.15 * ca)])
        stalls.append([(1.6 * ca + 0.15 * sa, -1.0 + 1.6 * sa - 0.15 * ca), (3.0 * ca + 0.15 * sa, -1.0 + 3.0 * sa - 0.15 * ca)])
    house = [arc(0, -1.0, 3.0, math.radians(20), math.radians(160), 40), arc(0, -1.0, 4.2, math.radians(20), math.radians(160), 50),
             [(3.0 * math.cos(math.radians(20)), -1.0 + 3.0 * math.sin(math.radians(20))), (4.2 * math.cos(math.radians(20)), -1.0 + 4.2 * math.sin(math.radians(20)))],
             [(-3.0 * math.cos(math.radians(20)), -1.0 + 3.0 * math.sin(math.radians(20))), (-4.2 * math.cos(math.radians(20)), -1.0 + 4.2 * math.sin(math.radians(20)))]]
    walls = [[(3.0 * math.cos(a), -1.0 + 3.0 * math.sin(a)), (4.2 * math.cos(a), -1.0 + 4.2 * math.sin(a))] for a in [math.radians(40 + 20 * k) for k in range(6)]]
    lead = [[(-0.15, -2.6), (-0.15, -3.4)], [(0.15, -2.6), (0.15, -3.4)]]
    engine = [transform(rrect(-0.9, -0.17, 0.9, 0.17, 0.08), dy=-1.0, rot=0.5)]
    return make("Roundhouse and Turntable", pit + bridge + stalls + house + walls + lead + engine)


# ---------------------------------------------------------------- station & trackside

@design("trains_water_tower", T)
def water_tower(rng):
    tank = rect(-1.8, 0.4, 1.8, 2.2)
    hoops = [[(-1.8, y), (1.8, y)] for y in (0.85, 1.3, 1.75)]
    roof = [poly((-2.0, 2.2), (0, 3.2), (2.0, 2.2), closed=False), [(0, 3.2), (0, 3.45)]]
    legs = [[(-1.6, 0.4), (-2.0, -2.8)], [(1.6, 0.4), (2.0, -2.8)], [(-0.5, 0.4), (-0.6, -2.8)], [(0.5, 0.4), (0.6, -2.8)]]
    braces = [[(-1.75, -0.8), (1.75, -0.8)], [(-1.8, -0.8), (-0.55, 0.4)], [(1.8, -0.8), (0.55, 0.4)], [(-1.9, -2.0), (-0.58, -0.8)], [(1.9, -2.0), (0.58, -0.8)]]
    spout = [tube([(1.8, 0.7), (2.8, 0.3), (3.1, -0.6)], 0.28), [(3.0, -0.5), (3.3, -1.2)]]
    ladder = [[(-1.2, 0.4), (-1.2, 2.2)], [(-0.9, 0.4), (-0.9, 2.2)]] + [[(-1.2, y), (-0.9, y)] for y in (0.9, 1.4, 1.9)]
    ground = [[(-3.0, -2.8), (3.6, -2.8)]]
    return make("Railroad Water Tower", [tank] + hoops + roof + legs + braces + spout + ladder + ground)


@design("trains_country_depot", T)
def country_depot(rng):
    walls = rect(-2.6, -2.0, 2.6, 0.6)
    roof = poly((-3.5, 0.5), (-2.2, 2.0), (2.2, 2.0), (3.5, 0.5))
    gable = [poly((-0.9, 2.0), (0, 2.9), (0.9, 2.0), closed=False), circle(0, 2.35, 0.25, 16)]
    door = [rect(-0.5, -2.0, 0.5, -0.2), [(0, -2.0), (0, -0.2)]]
    wins = []
    for x in (-1.8, 1.8):
        wins += [rect(x - 0.45, -1.4, x + 0.45, -0.1), [(x, -1.4), (x, -0.1)], [(x - 0.45, -0.75), (x + 0.45, -0.75)]]
    sign = [rect(-1.2, 0.05, 1.2, 0.45)]
    brackets = [[(-2.6, 0.0), (-3.2, 0.5)], [(2.6, 0.0), (3.2, 0.5)]]
    chimney = [poly((1.2, 1.5), (1.2, 2.6), (1.6, 2.6), (1.6, 1.0), closed=False)]
    platform = [rect(-3.8, -2.4, 3.8, -2.0)]
    bench = [rect(-2.4, -1.75, -1.2, -1.6), [(-2.3, -1.75), (-2.3, -2.0)], [(-1.3, -1.75), (-1.3, -2.0)]]
    return make("Country Railway Depot", [walls, roof] + gable + door + wins + sign + brackets + chimney + platform + bench + track(-2.8, -3.8, 3.8, 10))


@design("trains_platform_bench", T)
def platform_bench(rng):
    seat = [rect(-2.4, -0.9, 1.4, -0.7)]
    back = [rect(-2.4, -0.4, 1.4, -0.2), rect(-2.4, 0.0, 1.4, 0.2)]
    legs = [[(-2.2, -0.9), (-2.3, -2.0)], [(1.2, -0.9), (1.3, -2.0)], [(-2.2, -0.7), (-2.2, 0.2)], [(1.2, -0.7), (1.2, 0.2)]]
    arms = [quad((-2.4, -0.7), (-2.7, -0.4), (-2.3, -0.3), 8), quad((1.4, -0.7), (1.7, -0.4), (1.3, -0.3), 8)]
    lamp = [[(2.4, -2.0), (2.4, 2.0)], [(2.6, -2.0), (2.6, 2.0)], rect(2.2, -2.0, 2.8, -1.8), poly((2.1, 2.0), (2.25, 2.7), (2.75, 2.7), (2.9, 2.0)),
            poly((2.0, 2.7), (2.5, 3.1), (3.0, 2.7), closed=False)]
    sign = [rect(-2.0, 2.2, 1.0, 2.9), [(-1.5, 2.9), (-1.5, 3.4)], [(0.5, 2.9), (0.5, 3.4)]]
    case = [rrect(-1.2, -0.7, -0.1, 0.1, 0.1), arc(-0.65, 0.1, 0.25, 0, math.pi, 8), [(-1.2, -0.3), (-0.1, -0.3)]]
    edge = [[(-3.6, -2.0), (3.6, -2.0)], [(-3.6, -2.3), (3.6, -2.3)]]
    return make("Station Platform Bench", seat + back + legs + arms + lamp + sign + case + edge)


@design("trains_ticket_booth", T)
def ticket_booth(rng):
    booth = rect(-2.0, -2.6, 2.0, 1.6)
    roof = [poly((-2.6, 1.6), (0, 2.8), (2.6, 1.6))]
    sign = [rect(-1.5, 1.85, 1.5, 2.25)]
    window = [rrect(-1.4, -0.6, 1.4, 1.2, 0.5)] + [[(x, -0.6), (x, 1.2 - 0.0)] for x in (-0.7, 0.0, 0.7)]
    slot = [rect(-0.6, -0.95, 0.6, -0.6), rect(-1.8, -1.1, 1.8, -0.95)]
    panel = [rect(-1.5, -2.3, 1.5, -1.4)]
    bell = [chain([(-0.25, -1.1)], quad((-0.3, -0.85), (0, -0.8), (0.3, -0.85), 6)[1:], [(0.25, -1.1)])]
    tickets = [transform(rect(-0.3, -0.15, 0.3, 0.15), dx=1.0, dy=-0.75, rot=0.2)]
    return make("Ticket Booth", [booth] + roof + sign + window + slot + panel + bell + tickets)


@design("trains_signal_box", T)
def signal_box(rng):
    base = rect(-2.4, -2.8, 2.4, 0.0)
    bricks = [[(-2.4, y), (2.4, y)] for y in (-2.1, -1.4, -0.7)]
    upper = rect(-2.6, 0.0, 2.6, 1.8)
    panes = [rect(-2.4 + 1.2 * k, 0.4, -1.4 + 1.2 * k, 1.6) for k in range(4)]
    mullions = [[(-1.9 + 1.2 * k, 0.4), (-1.9 + 1.2 * k, 1.6)] for k in range(4)]
    roof = [poly((-3.0, 1.8), (-2.0, 2.8), (2.0, 2.8), (3.0, 1.8))]
    stairs = [poly((-2.4, -2.8), (-3.6, -2.8), (-3.6, -2.4), (-3.3, -2.4), (-3.3, -2.0), (-3.0, -2.0), (-3.0, -1.6), (-2.7, -1.6), (-2.7, -1.2), (-2.4, -1.2), closed=False)]
    door = [rect(-2.3, -1.2, -1.6, 0.0)]
    name = [rect(-1.0, -0.5, 1.6, -0.1)]
    levers = [[(x, 0.4), (x + 0.15, 0.9)] for x in (-0.5, -0.2, 0.1, 0.4)]
    return make("Signal Box", [base, upper] + bricks + panes + mullions + roof + stairs + door + name + levers)


@design("trains_wild_west_depot", T)
def wild_west_depot(rng):
    front = poly((-2.6, -2.0), (-2.6, 1.6), (-1.8, 1.6), (-1.8, 2.2), (1.8, 2.2), (1.8, 1.6), (2.6, 1.6), (2.6, -2.0))
    sign = [rect(-1.5, 1.2, 1.5, 1.9)]
    porch = [poly((-3.2, 0.4), (3.2, 0.4), (2.9, 0.8), (-2.9, 0.8)), [(-3.0, 0.4), (-3.0, -2.0)], [(3.0, 0.4), (3.0, -2.0)]]
    planks = [[(-2.6, y), (2.6, y)] for y in (-1.6, -1.2, -0.8, -0.4, 0.0)]
    door = [rect(-0.5, -2.0, 0.5, -0.1)]
    win = [rect(-2.1, -1.4, -1.2, -0.4), rect(1.2, -1.4, 2.1, -0.4)]
    barrel = [rrect(-3.7, -2.0, -3.1, -1.0, 0.15), [(-3.7, -1.5), (-3.1, -1.5)]]
    cactus = [chain([(3.3, -2.0), (3.3, -0.4)], arc(3.45, -0.4, 0.15, math.pi, 0, 6), [(3.6, -1.0), (3.75, -1.0), (3.75, -0.7)], arc(3.85, -0.7, 0.1, math.pi, 0, 4), [(3.95, -1.15), (3.6, -1.15), (3.6, -2.0)])]
    boards = [[(-3.8, -2.0), (4.0, -2.0)], [(-3.8, -2.3), (4.0, -2.3)]]
    return make("Wild West Train Depot", [front] + sign + porch + planks + door + win + barrel + cactus + boards + track(-2.9, -3.8, 4.0, 10))


@design("trains_semaphore", T)
def semaphore(rng):
    mast = [[(-0.15, -3.0), (-0.15, 2.6)], [(0.15, -3.0), (0.15, 2.6)], circle(0, 2.75, 0.15, 12)]
    arm = [poly((0.15, 1.6), (2.9, 2.2), (2.95, 1.9), (0.15, 1.25)), [(2.0, 1.8), (2.3, 2.1)], [(2.3, 1.85), (2.6, 2.15)]]
    spect = [poly((-0.15, 1.3), (-1.4, 1.0), (-1.5, 0.0), (-0.15, 0.4)), circle(-0.8, 0.95, 0.22, 16), circle(-0.85, 0.45, 0.2, 14)]
    lamp = [rrect(0.15, 0.2, 0.75, 0.8, 0.1), circle(0.45, 0.5, 0.15, 12)]
    ladder = [[(-0.6, -3.0), (-0.6, 0.0)]] + [[(-0.6, y), (-0.15, y)] for y in (-2.4, -1.8, -1.2, -0.6)]
    wire = [[(0.15, -2.8), (2.6, -2.8)], [(0.15, -2.6), (2.6, -2.6)]]
    base = [rect(-0.7, -3.2, 0.7, -3.0)]
    return make("Semaphore Signal", mast + arm + spect + lamp + ladder + wire + base)


@design("trains_crossing_gate", T)
def crossing_gate(rng):
    post = [[(-2.6, -2.6), (-2.6, 1.8)], [(-2.3, -2.6), (-2.3, 1.8)], rect(-3.0, -2.8, -1.9, -2.6)]
    cross = [transform(rect(-1.1, -0.15, 1.1, 0.15), dx=-2.45, dy=2.3, rot=0.6), transform(rect(-1.1, -0.15, 1.1, 0.15), dx=-2.45, dy=2.3, rot=-0.6)]
    lights = [circle(-3.1, 0.9, 0.35, 24), circle(-1.8, 0.9, 0.35, 24), [(-2.75, 0.9), (-2.15, 0.9)]]
    hoods = [arc(-3.1, 0.9, 0.45, 0.3, 2.8, 10), arc(-1.8, 0.9, 0.45, 0.3, 2.8, 10)]
    bell = [chain(arc(-2.45, 1.55, 0.25, 0, math.pi, 10), [(-2.7, 1.45), (-2.2, 1.45)], [(-2.2, 1.55)])]
    box = [rect(-2.1, -1.4, -1.2, -0.5)]
    gate = [rect(-1.3, -0.95, 3.6, -0.75)] + [rect(-0.6 + 1.0 * k, -0.95, -0.1 + 1.0 * k, -0.75) for k in range(4)]
    road = [[(-3.6, -2.6), (3.6, -2.6)], [(-1.0, -1.8), (3.6, -1.8)]]
    marks = [rect(-0.4 + 1.4 * k, -2.25, 0.4 + 1.4 * k, -2.15) for k in range(3)]
    return make("Railroad Crossing Gate", post + cross + lights + hoods + bell + box + gate + road + marks)


@design("trains_switch_stand", T)
def switch_stand(rng):
    rails = [[(-3.6, -2.6), (3.6, -2.6)], [(-3.6, -1.6), (3.6, -1.6)], quad((-1.0, -2.6), (1.5, -2.5), (3.6, -1.9), 20)]
    ties = [rect(-3.4 + 0.8 * k, -2.9, -3.1 + 0.8 * k, -1.3) for k in range(9)]
    stand = [rect(-1.6, -1.3, -0.8, -0.9), [(-1.2, -0.9), (-1.2, 1.4)], [(-1.05, -0.9), (-1.05, 1.4)]]
    target = [circle(-1.12, 1.9, 0.55, 40), circle(-1.12, 1.9, 0.25, 20)]
    lever = [[(-1.2, -0.95), (0.6, -0.4)], [(-1.2, -1.15), (0.6, -0.55)], circle(0.75, -0.45, 0.17, 12)]
    lamp = [rrect(-1.45, 0.7, -0.8, 1.2, 0.1)]
    return make("Track Switch Stand", rails + ties + stand + target + lever + lamp)


# ---------------------------------------------------------------- railway objects

@design("trains_lantern", T)
def lantern(rng):
    base = rrect(-1.2, -2.6, 1.2, -1.9, 0.15)
    globe = chain([(-1.0, -1.9)], cubic((-1.0, -1.9), (-1.5, -0.8), (-1.4, 0.5), (-0.9, 0.9), 20), [(0.9, 0.9)],
                  cubic((0.9, 0.9), (1.4, 0.5), (1.5, -0.8), (1.0, -1.9), 20))
    cage = [quad((x, -1.9), (x * 1.5, -0.5), (x * 0.95, 0.9), 14) for x in (-0.45, 0.45)] + [[(-1.4, -0.5), (1.4, -0.5)]]
    top = [poly((-0.9, 0.9), (-0.6, 1.5), (0.6, 1.5), (0.9, 0.9), closed=False), rect(-0.4, 1.5, 0.4, 1.8), circle(0, 2.0, 0.2, 14)]
    bail = [chain([(-1.2, -1.9)], cubic((-1.2, -1.9), (-2.4, 2.0), (2.4, 2.0), (1.2, -1.9), 40))]
    flame = [lens((0, -1.4), (0, -0.2), 0.3), lens((0, -1.2), (0, -0.6), 0.25)]
    return make("Railway Lantern", [base, globe] + cage + top + bail + flame)


@design("trains_conductor_cap", T)
def conductor_cap(rng):
    crown = chain([(-2.2, -0.4)], cubic((-2.2, -0.4), (-2.6, 1.4), (-1.4, 1.9), (0, 1.9), 20), cubic((0, 1.9), (1.4, 1.9), (2.6, 1.4), (2.2, -0.4), 20))
    band = [rect(-2.2, -0.9, 2.2, -0.4)]
    brim = [chain([(-2.2, -0.9)], quad((-1.2, -2.2), (2.8, -2.0), (3.2, -1.2), 20), quad((3.0, -1.0), (2.6, -0.9), (2.2, -0.9), 8))]
    badge = [rrect(-0.9, -0.25, 0.9, 0.6, 0.15), poly((-0.5, 0.15), (0.5, 0.15), (0.5, 0.4), (-0.5, 0.4))]
    cord = [[(-2.2, -0.65), (2.2, -0.65)]]
    buttons = [circle(-1.9, -0.65, 0.15, 12), circle(1.9, -0.65, 0.15, 12)]
    seam = [quad((-1.8, 1.4), (0, 2.1), (1.8, 1.4), 16)]
    return make("Conductor's Cap", [crown] + band + brim + badge + cord + buttons + seam)


@design("trains_pocket_watch", T)
def pocket_watch(rng):
    case = [circle(0, -0.4, 2.4, 140), circle(0, -0.4, 2.05, 120)]
    crown = [rect(-0.25, 2.0, 0.25, 2.35), rrect(-0.4, 2.35, 0.4, 2.7, 0.1), circle(0, 3.1, 0.4, 30)]
    ticks = [[(1.65 * math.cos(a), -0.4 + 1.65 * math.sin(a)), (1.9 * math.cos(a), -0.4 + 1.9 * math.sin(a))] for a in [k * math.pi / 6 for k in range(12)]]
    hands = [poly((0, -0.4), (0.15, 0.3), (0, 1.3), (-0.15, 0.3)), poly((0, -0.4), (0.7, -0.2), (1.1, -0.8), (0.5, -0.6))]
    sub = [circle(0, -1.3, 0.4, 30), [(0, -1.3), (0.2, -1.05)]]
    chain_ = [ellipse(0.65 + 0.42 * k, 3.2 + 0.12 * k * k * 0.3 - 0.0, 0.25, 0.14, 14, rot=0.2 * k) for k in range(6)]
    return make("Railroad Pocket Watch", case + crown + ticks + hands + sub + chain_, [circle(0, -0.4, 0.1, 10)])


@design("trains_whistle", T)
def whistle(rng):
    bell = rrect(-0.9, -0.2, 0.9, 2.4, 0.4)
    rings = [[(-0.9, y), (0.9, y)] for y in (0.6, 1.6)]
    cap = [chain(arc(0, 2.4, 0.9, 0, math.pi, 20)), [(0, 3.3), (0, 3.6)], circle(0, 3.7, 0.12, 10)]
    mouth = [rect(-0.9, -0.6, 0.9, -0.2), rect(-0.5, -1.4, 0.5, -0.6)]
    valve = [rect(-0.8, -2.1, 0.8, -1.4), [(0.8, -1.75), (2.6, -1.0)], circle(2.75, -0.95, 0.18, 12), [(0.8, -1.75), (0.8, -1.75)]]
    pipe = [[(-0.25, -2.1), (-0.25, -3.0)], [(0.25, -2.1), (0.25, -3.0)]]
    steam = [chain(arc(-1.6, 0.0, 0.4, -0.5, 2.3, 10), arc(-2.2, 0.5, 0.45, 0.0, 2.8, 12), arc(-2.8, 0.1, 0.4, 1.0, 3.6, 10)),
             chain(arc(1.6, 0.0, 0.4, 0.8, 3.6, 10)[::-1], arc(2.2, 0.5, 0.45, 0.3, 3.1, 12)[::-1], arc(2.8, 0.1, 0.4, -0.5, 2.1, 10)[::-1])]
    return make("Steam Train Whistle", [bell] + rings + cap + mouth + valve[:3] + pipe + steam)


@design("trains_ticket", T)
def ticket(rng):
    edge = []
    for k in range(12):
        x0 = -3.0 + 0.5 * k
        edge += arc(x0 + 0.25, 1.6, 0.25, math.pi, 0, 6)
    bottom = []
    for k in range(12):
        x0 = 3.0 - 0.5 * k
        bottom += arc(x0 - 0.25, -1.6, 0.25, 0, -math.pi, 6)
    outline = chain(edge, [(3.0, 1.6), (3.0, -1.6)], bottom, [(-3.0, -1.6), (-3.0, 1.6)])
    stub = [[(1.4, 1.35), (1.4, -1.35)]]
    hole = [circle(2.2, 0.0, 0.3, 20)]
    eng = [rect(-2.4, -0.5, -0.8, 0.1), rect(-2.4, 0.1, -1.8, 0.8), poly((-1.2, 0.1), (-1.3, 0.7), (-0.8, 0.7), (-0.9, 0.1)), circle(-2.0, -0.7, 0.25, 16), circle(-1.2, -0.7, 0.25, 16)]
    lines = [[(-0.4, y), (1.0, y)] for y in (0.7, 0.2, -0.3, -0.8)]
    border = [rect(-2.75, -1.2, 1.2, 1.2)]
    return make("Vintage Train Ticket", [outline] + stub + hole + eng + lines + border)


@design("trains_drive_wheels", T)
def drive_wheels(rng):
    wl = []
    for cx in (-1.6, 1.6):
        wl += [circle(cx, -0.6, 1.5, 90), circle(cx, -0.6, 1.25, 80), circle(cx, -0.6, 0.3, 20)]
        wl += [[(cx + 0.3 * math.cos(a), -0.6 + 0.3 * math.sin(a)), (cx + 1.25 * math.cos(a), -0.6 + 1.25 * math.sin(a))] for a in [k * TAU / 12 + 0.13 for k in range(12)]]
        wl.append(chain(arc(cx, -0.6, 1.25, math.radians(200), math.radians(250), 6), arc(cx, -0.6, 0.7, math.radians(250), math.radians(200), 6), [(cx + 1.25 * math.cos(math.radians(200)), -0.6 + 1.25 * math.sin(math.radians(200)))]))
    rod = [rrect(-1.9, -0.1, 1.9, 0.2, 0.15), circle(-1.6, 0.05, 0.22, 14), circle(1.6, 0.05, 0.22, 14)]
    main = [tube([(1.6, 0.05), (3.6, 0.5)], 0.25), rect(3.4, 0.25, 3.9, 0.75)]
    cyl = [rrect(3.9, -0.2, 4.6, 1.2, 0.15)]
    rail = [[(-3.4, -2.1), (4.6, -2.1)], [(-3.4, -2.3), (4.6, -2.3)]]
    body = [[(-3.4, 1.4), (4.6, 1.4)]]
    return make("Locomotive Driving Wheels", wl + rod + main + cyl + rail + body)


@design("trains_golden_spike", T)
def golden_spike(rng):
    tie = [rect(-3.4, -2.6, 3.4, -1.6)]
    grain = [wave(-3.2, 3.2, -2.1, 0.08, 4)]
    rail = [poly((-3.6, -1.6), (-3.6, -1.4), (-2.4, -1.35), (-2.4, -0.7), (-2.9, -0.6), (-2.9, -0.35), (-1.3, -0.35), (-1.3, -0.6), (-1.8, -0.7), (-1.8, -1.35), (-0.6, -1.4), (-0.6, -1.6), closed=False)]
    spike = [poly((0.3, -1.6), (0.3, 0.6), (0.0, 0.7), (0.0, 0.95), (1.2, 0.95), (1.2, 0.7), (0.9, 0.6), (0.9, -1.6), closed=False), poly((0.3, -1.6), (0.6, -2.0), (0.9, -1.6), closed=False)]
    shine = [star(1.6, 1.6, 0.35, 4, 0.3), star(-0.4, 1.3, 0.25, 4, 0.3)]
    hammer = [transform(p, dx=1.6, dy=1.0, rot=0.5) for p in [rrect(-0.2, 0.0, 0.2, 2.6, 0.08), rrect(-0.9, 2.5, 0.9, 3.0, 0.1)]]
    return make("Golden Spike and Hammer", tie + grain + rail + spike + shine + hammer)
