"""Trains niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "trains"


def _wheels(xs, y, r):
    out = []
    for x in xs:
        out += [circle(x, y, r, 40), circle(x, y, r * 0.3, 14)]
    return out


def _track(y=-1.6):
    return [[(-3.4, y), (3.4, y)]] + [[(x, y - 0.25), (x, y)] for x in [-3.0 + 0.75 * k for k in range(9)]]


@design("steam_engine", T)
def steam_engine(rng):
    boiler = rrect(-1.2, -0.6, 2.6, 0.9, 0.4)
    cab = rect(-3.0, -0.6, -1.2, 1.9)
    roof = rect(-3.3, 1.9, -0.9, 2.2)
    window = rect(-2.5, 0.8, -1.6, 1.5)
    stack = poly((1.6, 0.9), (1.4, 2.0), (2.4, 2.0), (2.2, 0.9))
    cow = poly((2.6, -0.6), (3.3, -1.3), (2.6, -1.3), closed=False)
    smoke = [circle(2.0, 2.5, 0.35, 24), circle(1.4, 3.0, 0.45, 26), circle(0.6, 3.3, 0.55, 30)]
    return Design("Steam Locomotive", [boiler, cab, roof, window, stack, cow] + smoke + _wheels((-2.2, -0.6, 0.6, 1.8), -1.0, 0.55) + _track(), [], T)


@design("passenger_car", T)
def passenger_car(rng):
    body = rrect(-3.2, -0.8, 3.2, 1.6, 0.3)
    roof = chain(quad((-3.3, 1.6), (0, 2.2), (3.3, 1.6)))
    windows = [rrect(-2.8 + 1.15 * k, 0.2, -2.0 + 1.15 * k, 1.1, 0.15) for k in range(5)]
    stripe = [(-3.2, -0.2), (3.2, -0.2)]
    return Design("Passenger Carriage", [body, roof, stripe] + windows + _wheels((-2.3, -1.5, 1.5, 2.3), -1.1, 0.4) + _track(), [], T)


@design("caboose", T)
def caboose(rng):
    body = rect(-2.4, -0.8, 2.4, 1.4)
    cupola = rect(-0.8, 1.4, 0.8, 2.4)
    roof = [rect(-2.6, 1.4, 2.6, 1.6), rect(-1.0, 2.4, 1.0, 2.6)]
    windows = [rect(-1.8, 0.2, -1.0, 0.9), rect(1.0, 0.2, 1.8, 0.9), rect(-0.4, 1.7, 0.4, 2.2)]
    rails = [[(-3.0, -0.8), (-3.0, 0.6)], [(-3.0, 0.6), (-2.4, 0.6)], [(3.0, -0.8), (3.0, 0.6)], [(3.0, 0.6), (2.4, 0.6)]]
    lamp = circle(2.2, 2.0, 0.25, 16)
    return Design("Caboose", [body, cupola, lamp] + roof + windows + rails + _wheels((-1.6, 1.6), -1.1, 0.45) + _track(), [], T)


@design("rail_crossing", T)
def rail_crossing(rng):
    pole = [[(-0.12, -3.0), (-0.12, 2.0)], [(0.12, -3.0), (0.12, 2.0)]]
    xsign = [transform(rect(-2.0, -0.3, 2.0, 0.3), dy=2.2, rot=0.6), transform(rect(-2.0, -0.3, 2.0, 0.3), dy=2.2, rot=-0.6)]
    lights = [circle(-0.8, 0.6, 0.4, 30), circle(0.8, 0.6, 0.4, 30)]
    bar = [(-1.2, 0.6), (1.2, 0.6)]
    base = rect(-0.8, -3.0, 0.8, -2.6)
    return Design("Railroad Crossing", pole + xsign + lights + [bar, base], [], T)


@design("tunnel", T)
def tunnel(rng):
    mountain = poly((-3.4, -1.6), (-1.6, 1.8), (-0.6, 1.0), (0.6, 2.6), (3.4, -1.6), closed=False)
    snow = [poly((-2.0, 1.0), (-1.6, 1.8), (-1.2, 1.2), closed=False), poly((0.1, 1.9), (0.6, 2.6), (1.1, 1.9), closed=False)]
    arch = chain([(-1.2, -1.6), (-1.2, -0.4)], arc(0, -0.4, 1.2, math.pi, 0, 30), [(1.2, -1.6)])
    stones = arc(0, -0.4, 1.5, 0, math.pi, 30)
    train_front = [rrect(-0.7, -1.4, 0.7, 0.2, 0.3), circle(0, -0.4, 0.25, 16)]
    return Design("Mountain Tunnel", [mountain, arch, stones] + snow + train_front + _track(), [], T)


@design("station_clock", T)
def station_clock(rng):
    face = circle(0, 0.6, 1.8, 120)
    rim = circle(0, 0.6, 2.1, 140)
    ticks = [[(1.5 * math.cos(a), 0.6 + 1.5 * math.sin(a)), (1.75 * math.cos(a), 0.6 + 1.75 * math.sin(a))] for a in [k * math.pi / 6 for k in range(12)]]
    hands = [[(0, 0.6), (0, 1.9)], [(0, 0.6), (0.9, 0.2)]]
    bracket = [[(0, 2.7), (0, 3.4)], [(-1.4, 3.4), (1.4, 3.4)]]
    return Design("Station Clock", [face, rim] + ticks + hands + bracket, [circle(0, 0.6, 0.1, 10)], T)


@design("freight_car", T)
def freight_car(rng):
    box = rect(-3.0, -0.8, 3.0, 1.8)
    door = rect(-0.8, -0.8, 0.8, 1.6)
    planks = [[(x, -0.8), (x, 1.8)] for x in (-2.2, -1.5, 1.5, 2.2)]
    cross = [[(-0.8, -0.8), (0.8, 1.6)], [(-0.8, 1.6), (0.8, -0.8)]]
    return Design("Freight Car", [box, door] + planks + cross + _wheels((-2.2, -1.4, 1.4, 2.2), -1.1, 0.4) + _track(), [], T)


@design("bullet_train", T)
def bullet_train(rng):
    body = chain([(-3.4, -0.6), (-3.4, 1.0)], [(0.0, 1.0)], cubic((0.0, 1.0), (2.0, 1.0), (3.2, 0.2), (3.6, -0.6), 30), [(-3.4, -0.6)])
    windows = [rrect(-3.1 + 0.8 * k, 0.2, -2.6 + 0.8 * k, 0.7, 0.1) for k in range(4)]
    cockpit = quad((0.6, 0.9), (1.8, 0.8), (2.4, 0.2))
    stripe = [(-3.4, -0.1), (3.0, -0.1)]
    speed = [[(-4.0, y), (-3.6, y)] for y in (0.8, 0.2, -0.4)]
    return Design("Bullet Train", [body, cockpit, stripe] + windows + speed + _track(-0.9), [], T)


@design("signal_lamp", T)
def signal_lamp(rng):
    pole = [[(-0.15, -3.0), (-0.15, 1.2)], [(0.15, -3.0), (0.15, 1.2)]]
    head = rrect(-0.8, 1.2, 0.8, 3.4, 0.4)
    lamps = [circle(0, 2.8, 0.4, 30), circle(0, 1.8, 0.4, 30)]
    arm = [rect(0.15, 0.2, 2.4, 0.6), poly((2.4, 0.2), (2.8, 0.4), (2.4, 0.6))]
    ladder = [[(-0.6, -3.0), (-0.6, 0.6)]] + [[(-0.6, y), (-0.15, y)] for y in (-2.4, -1.6, -0.8, 0.0)]
    return Design("Railway Signal", pole + [head] + lamps + arm + ladder, [], T)
