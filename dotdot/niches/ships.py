"""Boats & Ships niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "ships"


@design("cruise_ship", T)
def cruise_ship(rng):
    hull = poly((-3.4, -0.4), (3.4, -0.4), (2.8, -1.6), (-3.0, -1.6))
    decks = [rect(-2.8, -0.4, 2.6, 0.4), rect(-2.2, 0.4, 2.0, 1.1), rect(-1.4, 1.1, 1.2, 1.7)]
    funnels = [poly((0.0, 1.7), (0.2, 2.7), (0.8, 2.7), (0.8, 1.7), closed=False)]
    portholes = [circle(-2.4 + 0.6 * k, -0.95, 0.12, 12) for k in range(9)]
    windows = [[(-2.6, 0.0), (2.4, 0.0)], [(-2.0, 0.75), (1.8, 0.75)]]
    water = [wave(-3.6, 3.6, -1.8, 0.12, 6, 100)]
    return Design("Cruise Ship", [hull] + decks + funnels + portholes + windows + water, [], T)


@design("steamboat", T)
def steamboat(rng):
    hull = poly((-3.0, -0.6), (3.0, -0.6), (2.4, -1.4), (-2.6, -1.4))
    cabin = rect(-1.8, -0.6, 1.4, 0.6)
    upper = rect(-1.2, 0.6, 0.8, 1.2)
    stacks = [rect(-0.8, 1.2, -0.5, 2.6), rect(0.0, 1.2, 0.3, 2.6)]
    wheel = [circle(2.3, -0.4, 0.8, 50)] + [[(2.3, -0.4), (2.3 + 0.8 * math.cos(a), -0.4 + 0.8 * math.sin(a))] for a in [k * math.pi / 4 for k in range(8)]]
    windows = [rect(-1.5 + 0.8 * k, -0.2, -1.1 + 0.8 * k, 0.3) for k in range(4)]
    water = [wave(-3.4, 3.4, -1.6, 0.1, 6, 100)]
    return Design("Paddle Steamer", [hull, cabin, upper] + stacks + wheel + windows + water, [], T)


@design("rowboat", T)
def rowboat(rng):
    hull = chain(quad((-3.0, 0.4), (0, -1.8), (3.0, 0.4)), [(-3.0, 0.4)])
    seat = [(-0.8, -0.1), (0.8, -0.1)]
    planks = [quad((-2.6, 0.0), (0, -1.1), (2.6, 0.0)), quad((-2.2, -0.4), (0, -1.45), (2.2, -0.4))]
    oars = [[(-1.2, 0.2), (-3.4, -1.6)], lens((-3.4, -1.6), (-2.8, -1.2), 0.3), [(1.2, 0.2), (3.4, -1.6)], lens((3.4, -1.6), (2.8, -1.2), 0.3)]
    water = [wave(-3.6, 3.6, -1.3, 0.1, 5, 100)]
    return Design("Rowboat", [hull, seat] + planks + oars + water, [], T)


@design("canoe", T)
def canoe(rng):
    hull = chain(cubic((-3.4, 0.6), (-2.0, -1.0), (2.0, -1.0), (3.4, 0.6), 40), quad((3.4, 0.6), (0, -0.2), (-3.4, 0.6), 40))
    stripe = quad((-3.0, 0.2), (0, -0.55), (3.0, 0.2))
    paddle = [[(-1.0, 2.6), (0.8, -0.8)], lens((0.8, -0.8), (1.4, -1.8), 0.3)]
    pines = [poly((x - 0.6, -2.4), (x, -0.6), (x + 0.6, -2.4)) for x in (-2.4, 2.4)]
    water = [wave(-3.6, 3.6, -0.9, 0.1, 5, 100)]
    return Design("Canoe", [hull, stripe] + paddle + pines + water, [], T)


@design("submarine", T)
def submarine(rng):
    body = rrect(-3.0, -1.0, 2.6, 0.6, 0.8)
    tower = rect(-0.6, 0.6, 0.8, 1.6)
    periscope = [[(0.4, 1.6), (0.4, 2.4)], [(0.4, 2.4), (0.9, 2.4)]]
    portholes = [circle(-1.8 + 1.0 * k, -0.2, 0.3, 24) for k in range(4)]
    prop = [lens((-3.0, -0.2), (-3.6, 0.4), 0.3), lens((-3.0, -0.2), (-3.6, -0.8), 0.3)]
    bubbles = [circle(-3.6, 0.9, 0.15, 12), circle(-3.4, 1.4, 0.2, 14), circle(-3.7, 1.9, 0.12, 10)]
    return Design("Submarine", [body, tower] + periscope + portholes + prop + bubbles, [], T)


@design("ship_wheel", T)
def ship_wheel(rng):
    rim = circle(0, 0, 2.0, 120)
    inner = circle(0, 0, 1.6, 100)
    hub = circle(0, 0, 0.4, 30)
    spokes = []
    for k in range(8):
        a = k * math.pi / 4
        spokes.append([(0.4 * math.cos(a), 0.4 * math.sin(a)), (2.6 * math.cos(a), 2.6 * math.sin(a))])
        spokes.append(circle(2.75 * math.cos(a), 2.75 * math.sin(a), 0.18, 12))
    return Design("Ship's Wheel", [rim, inner, hub] + spokes, [], T)


@design("tugboat", T)
def tugboat(rng):
    hull = chain(quad((-3.0, 0.0), (-2.8, -1.4), (0, -1.4), 20), [(2.6, -1.4), (3.2, 0.2), (-3.0, 0.0)])
    cabin = rect(-1.6, 0.0, 1.0, 1.4)
    bridge = rect(-1.0, 1.4, 0.6, 2.0)
    stack = poly((1.4, 0.0), (1.4, 1.8), (2.0, 1.8), (2.0, 0.0), closed=False)
    tires = [circle(x, -0.5, 0.3, 20) for x in (-2.2, -1.0, 0.2, 1.4)]
    windows = [rect(-1.3 + 0.8 * k, 0.6, -0.9 + 0.8 * k, 1.0) for k in range(3)]
    water = [wave(-3.4, 3.4, -1.6, 0.1, 6, 100)]
    return Design("Tugboat", [hull, cabin, bridge, stack] + tires + windows + water, [], T)
