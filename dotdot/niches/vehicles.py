"""Cars & Trucks niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "vehicles"


def _wheel(cx, cy, r):
    return [circle(cx, cy, r, 50), circle(cx, cy, r * 0.4, 20)]


@design("sedan", T)
def sedan(rng):
    body = chain([(-3.0, -0.6), (-3.0, 0.4)], quad((-3.0, 0.6), (-2.2, 0.7), (-1.6, 0.7), 8), [(-0.8, 1.6), (1.0, 1.6), (1.8, 0.7)],
                 quad((1.8, 0.7), (2.9, 0.6), (3.0, 0.0), 8), [(3.0, -0.6), (-3.0, -0.6)])
    windows = [poly((-1.3, 0.8), (-0.7, 1.45), (0.0, 1.45), (0.0, 0.8)), poly((0.2, 0.8), (0.2, 1.45), (0.9, 1.45), (1.4, 0.8))]
    door = [[(0.1, 0.8), (0.1, -0.5)], [(-0.4, 0.1), (-0.1, 0.1)]]
    lights = [rect(2.7, 0.1, 3.0, 0.4), rect(-3.0, 0.0, -2.8, 0.3)]
    return Design("Family Car", [body] + windows + door + lights + _wheel(-1.8, -0.6, 0.6) + _wheel(1.8, -0.6, 0.6), [], T)


@design("pickup", T)
def pickup(rng):
    body = poly((-3.0, -0.6), (-3.0, 0.5), (-0.2, 0.5), (-0.2, 1.6), (1.4, 1.6), (2.2, 0.6), (3.0, 0.5), (3.0, -0.6))
    window = poly((0.0, 0.7), (0.0, 1.4), (1.3, 1.4), (1.9, 0.7))
    bed = [[(-2.8, 0.5), (-2.8, 0.1)], [(-2.8, 0.1), (-0.4, 0.1)]]
    hay = [arc(-2.0, 0.5, 0.45, 0, math.pi, 16), arc(-1.1, 0.5, 0.45, 0, math.pi, 16)]
    return Design("Pickup Truck", [body, window] + bed + hay + _wheel(-1.9, -0.6, 0.6) + _wheel(1.9, -0.6, 0.6), [], T)


@design("beetle_car", T)
def beetle_car(rng):
    body = chain(arc(0, -0.4, 2.6, math.radians(5), math.radians(175), 80), [(-2.9, -0.2), (-2.9, -0.7), (2.9, -0.7), (2.9, -0.2), (2.59, -0.17)])
    windows = [poly((-1.6, 0.6), (-1.1, 1.4), (-0.1, 1.65), (-0.1, 0.6)), poly((0.1, 0.6), (0.1, 1.65), (1.1, 1.4), (1.6, 0.6))]
    fenders = [arc(-1.7, -0.7, 0.85, 0, math.pi, 20), arc(1.7, -0.7, 0.85, 0, math.pi, 20)]
    flower = [circle(0.0, 0.0, 0.15, 12)] + [lens((0, 0), (0.45 * math.cos(a), 0.45 * math.sin(a)), 0.35) for a in [k * 2 * math.pi / 5 for k in range(5)]]
    return Design("Retro Bug Car", [body] + windows + fenders + flower + _wheel(-1.7, -0.7, 0.55) + _wheel(1.7, -0.7, 0.55), [], T)


@design("school_bus", T)
def school_bus(rng):
    body = rrect(-3.2, -0.8, 2.6, 1.8, 0.3)
    hood = poly((2.6, -0.8), (3.4, -0.8), (3.4, 0.6), (2.6, 0.8), closed=False)
    windows = [rect(-2.9 + 0.95 * k, 0.6, -2.2 + 0.95 * k, 1.4) for k in range(5)]
    door = rect(1.7, -0.6, 2.4, 1.4)
    stripe = [(-3.2, 0.2), (2.6, 0.2)]
    stop = [poly(*[(-3.5 + 0.35 * math.cos(math.pi / 8 + k * math.pi / 4), 0.6 + 0.35 * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)])]
    return Design("School Bus", [body, hood, door, stripe] + windows + stop + _wheel(-2.0, -0.8, 0.6) + _wheel(1.9, -0.8, 0.6), [], T)


@design("fire_truck", T)
def fire_truck(rng):
    body = rect(-3.2, -0.6, 1.8, 0.8)
    cab = poly((1.8, -0.6), (1.8, 1.8), (2.8, 1.8), (3.4, 0.6), (3.4, -0.6), closed=False)
    window = poly((2.0, 0.9), (2.0, 1.6), (2.7, 1.6), (3.1, 0.9))
    ladder = [[(-3.0, 1.2), (1.6, 2.0)], [(-3.0, 1.6), (1.6, 2.4)]] + [[(-3.0 + 0.6 * k, 1.2 + 0.105 * k), (-3.0 + 0.6 * k, 1.6 + 0.105 * k)] for k in range(8)]
    siren = rect(2.2, 1.8, 2.6, 2.1)
    hose = spiral(-1.2, 0.1, 0.1, 0.5, 2.0, 60)
    return Design("Fire Truck", [body, cab, window, siren, hose] + ladder + _wheel(-2.2, -0.6, 0.6) + _wheel(2.4, -0.6, 0.6), [], T)


@design("motorcycle", T)
def motorcycle(rng):
    wheels = _wheel(-2.0, -1.0, 0.9) + _wheel(2.0, -1.0, 0.9)
    frame = poly((-2.0, -1.0), (-0.6, -0.6), (1.0, -0.6), (2.0, -1.0), closed=False)
    tank = chain(quad((-0.6, 0.0), (0.2, 0.7), (1.0, 0.1)), [(-0.6, 0.0)])
    seat = [quad((-1.8, 0.1), (-1.2, 0.3), (-0.6, 0.05))]
    fork = [(2.0, -1.0), (1.4, 0.8)]
    bars = [(1.2, 0.8), (1.8, 1.0)]
    light = circle(1.75, 0.4, 0.2, 16)
    exhaust = [(-1.6, -0.9), (-0.2, -0.75)]
    return Design("Motorcycle", wheels + [frame, tank, fork, bars, light, exhaust] + seat, [], T)


@design("race_car", T)
def race_car(rng):
    body = poly((-3.2, -0.4), (-3.0, 0.4), (-1.0, 0.5), (-0.4, 1.1), (0.6, 1.1), (1.0, 0.5), (3.2, 0.0), (3.2, -0.4))
    wing = [rect(-3.4, 0.8, -2.6, 1.0), [(-3.0, 0.4), (-3.0, 0.8)]]
    num = circle(-1.6, 0.0, 0.3, 24)
    stripes = [[(0.4, 0.3), (2.6, 0.0)], [(0.4, 0.05), (2.6, -0.2)]]
    helmet = arc(0.1, 1.1, 0.35, 0, math.pi, 12)
    flag = [rect(2.4, 1.8, 3.4, 2.6)] + [rect(2.4 + 0.25 * (i % 4), 1.8 + 0.2 * (i // 4), 2.65 + 0.25 * (i % 4), 2.0 + 0.2 * (i // 4)) for i in range(0, 16, 2)][:4]
    return Design("Race Car", [body, num, helmet] + wing + stripes + flag + _wheel(-2.1, -0.4, 0.55) + _wheel(2.2, -0.4, 0.55), [], T)


@design("traffic_light", T)
def traffic_light(rng):
    box = rrect(-0.9, -0.6, 0.9, 3.2, 0.3)
    lights = [circle(0, y, 0.45, 40) for y in (2.5, 1.3, 0.1)]
    visors = [arc(0, y, 0.6, math.radians(20), math.radians(160), 16) for y in (2.5, 1.3, 0.1)]
    pole = [[(-0.15, -0.6), (-0.15, -3.0)], [(0.15, -0.6), (0.15, -3.0)]]
    sign = poly((1.4, -1.6), (2.6, -1.6), (2.0, -0.5))
    return Design("Traffic Light", [box, sign] + lights + visors + pole, [], T)


@design("gas_pump", T)
def gas_pump(rng):
    pump = rect(-1.4, -2.6, 0.8, 1.8)
    screen = rect(-1.0, 0.6, 0.4, 1.4)
    top = rect(-1.6, 1.8, 1.0, 2.2)
    hose = cubic((0.8, 0.8), (2.2, 0.8), (2.2, -1.8), (1.6, -2.0), 30)
    nozzle = poly((1.6, -2.0), (1.4, -1.4), (1.9, -1.2), (2.1, -1.8), closed=False)
    drop = [lens((-0.3, -1.6), (-0.3, -0.6), 0.4)]
    return Design("Gas Pump", [pump, screen, top, hose, nozzle] + drop, [], T)
