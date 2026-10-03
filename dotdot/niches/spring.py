"""Spring niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "spring"


@design("daffodil", T)
def daffodil(rng):
    petals = [lens((0, 1.2), (1.4 * math.cos(a), 1.2 + 1.4 * math.sin(a)), 0.35) for a in [math.pi / 2 + k * 2 * math.pi / 6 for k in range(6)]]
    frill = [(0.55 * math.cos(t) * (1 + 0.1 * math.sin(10 * t)), 1.2 + 0.55 * math.sin(t) * (1 + 0.1 * math.sin(10 * t)))
             for t in [2 * math.pi * i / 120 for i in range(121)]]
    stem = quad((0, -0.2), (0.3, -1.6), (0.0, -3.0))
    leaves = [lens((0, -3.0), (-1.2, -0.6), 0.15), lens((0, -3.0), (1.0, -1.0), 0.15)]
    return Design("Daffodil", petals + [frill, stem] + leaves, [], T)


@design("kite", T)
def kite(rng):
    k = poly((0, 3.0), (1.4, 1.2), (0, -1.0), (-1.4, 1.2))
    spars = [[(0, 3.0), (0, -1.0)], [(-1.4, 1.2), (1.4, 1.2)]]
    tail = [(0.3 * math.sin(3 * t), -1.0 - t) for t in [i / 40 * 2.4 for i in range(41)]]
    bows = [transform(lens((0, 0), (0.5, 0.2), 0.4), dx=0.3 * math.sin(3 * t), dy=-1.0 - t) for t in (0.6, 1.4, 2.2)]
    string = quad((0, -1.0), (1.8, -1.6), (2.8, -3.2))
    clouds = [chain(arc(-2.2, 2.2, 0.5, math.pi, 0, 16), arc(-1.6, 2.4, 0.6, math.pi, 0, 16), [(-2.7, 2.2)])]
    return Design("Spring Kite", [k, tail, string] + spars + bows + clouds, [], T)


@design("cherry_blossom", T)
def cherry_blossom(rng):
    branch = [quad((-3.2, -1.6), (-0.6, -0.6), (2.8, 1.8)), quad((-0.4, -0.5), (0.2, 0.6), (0.0, 1.8))]
    flowers = []
    for cx, cy in [(-1.6, -1.0), (0.6, 0.4), (2.2, 1.6), (0.0, 1.9), (-0.6, 0.2)]:
        flowers.append(circle(cx, cy, 0.12, 10))
        flowers += [heart(cx + 0.38 * math.cos(a), cy + 0.38 * math.sin(a), 0.22) for a in [k * 2 * math.pi / 5 for k in range(5)]]
    petals = [lens((x, y), (x + 0.3, y - 0.2), 0.4) for x, y in [(-2.4, 1.4), (1.6, -1.6), (-0.6, -2.4)]]
    return Design("Cherry Blossom", branch + flowers + petals, [], T)


@design("robin", T)
def robin(rng):
    body = chain(cubic((-1.4, 0.4), (-1.4, 1.8), (0.8, 2.2), (1.2, 1.0), 40), quad((1.2, 1.0), (0.6, -0.8), (-0.8, -0.6), 30),
                 quad((-0.8, -0.6), (-1.4, -0.2), (-1.4, 0.4), 10))
    breast = quad((1.15, 1.1), (0.2, 0.6), (0.2, -0.6))
    beak = poly((1.2, 1.3), (1.7, 1.2), (1.2, 1.05), closed=False)
    wing = quad((-1.0, 0.8), (0.0, 0.4), (-0.6, -0.2))
    tail = poly((-1.3, 0.3), (-2.4, 0.0), (-1.2, -0.2), closed=False)
    legs = [[(0, -0.7), (0, -1.4)], [(0.4, -0.7), (0.4, -1.4)]]
    worm = [(1.7 + 0.15 * math.sin(4 * t), 1.15 - 0.4 * t) for t in [i / 20 for i in range(21)]]
    branch = [(-2.4, -1.4), (2.4, -1.4)]
    return Design("Robin", [body, breast, beak, wing, tail, worm, branch] + legs, [eye(0.7, 1.5, 0.08)], T)


@design("sprout", T)
def sprout(rng):
    pot = poly((-1.2, -0.8), (1.2, -0.8), (0.9, -2.6), (-0.9, -2.6))
    rim = rect(-1.4, -0.8, 1.4, -0.3)
    stem = quad((0, -0.3), (-0.2, 0.8), (0.0, 1.6))
    leaves = [lens((0.0, 1.4), (-1.6, 2.2), 0.4), lens((0.0, 1.5), (1.4, 2.4), 0.4)]
    veins = [[(0.0, 1.4), (-1.3, 2.05)], [(0.0, 1.5), (1.2, 2.25)]]
    sun = [circle(2.4, 2.8, 0.5, 30)] + [[(2.4 + 0.65 * math.cos(a), 2.8 + 0.65 * math.sin(a)), (2.4 + 0.95 * math.cos(a), 2.8 + 0.95 * math.sin(a))]
                                          for a in [k * math.pi / 4 for k in range(8)]]
    return Design("New Sprout", [pot, rim, stem] + leaves + veins + sun, [], T)


@design("rain_cloud", T)
def rain_cloud(rng):
    cloud = chain(arc(-1.4, 0.8, 0.9, math.radians(100), math.radians(270), 30), [(1.6, -0.1)],
                  arc(1.6, 0.8, 0.9, math.radians(-90), math.radians(90), 30), arc(0.2, 1.4, 1.3, math.radians(20), math.radians(170), 40))
    drops = [lens((x, y), (x, y - 0.6), 0.4) for x, y in [(-1.4, -0.6), (-0.5, -1.0), (0.4, -0.6), (1.3, -1.0), (-0.9, -2.0), (0.9, -2.2)]]
    flowers = [circle(-2.4, -2.6, 0.3, 20), circle(2.4, -2.6, 0.3, 20), [(-2.4, -2.9), (-2.4, -3.4)], [(2.4, -2.9), (2.4, -3.4)]]
    return Design("Spring Shower", [cloud] + drops + flowers, [], T)


@design("picnic_basket", T)
def picnic_basket(rng):
    basket = rrect(-2.4, -2.2, 2.4, 0.2, 0.2)
    lids = [poly((-2.4, 0.2), (-2.2, 1.0), (0, 1.0), (0, 0.2), closed=False), poly((2.4, 0.2), (2.2, 1.0), (0, 1.0), closed=False)]
    handle = arc(0, 1.0, 1.4, 0, math.pi, 30)
    weave = [[(-2.4, y), (2.4, y)] for y in (-0.6, -1.4)] + [[(x, 0.2), (x, -2.2)] for x in (-1.2, 0.0, 1.2)]
    cloth = zigzag(-2.4, 2.4, 0.0, 0.12, 10)
    return Design("Picnic Basket", [basket, handle, cloth] + lids + weave, [], T)


@design("beehive", T)
def beehive(rng):
    rings = [ellipse(0, -1.8 + 0.8 * k, 2.0 - 0.3 * k, 0.45, 80) for k in range(5)]
    door = chain([(-0.4, -2.2), (-0.4, -1.8)], arc(0, -1.8, 0.4, math.pi, 0, 12), [(0.4, -2.2)])
    bees = []
    for x, y in [(2.4, 1.4), (-2.4, 0.8)]:
        bees += [ellipse(x, y, 0.35, 0.22, 20), ellipse(x - 0.1, y + 0.3, 0.18, 0.12, 12), ellipse(x + 0.15, y + 0.3, 0.18, 0.12, 12)]
    branch = [(-2.6, 2.4), (2.6, 2.4)]
    return Design("Beehive", rings + [door, branch, [(0, 2.4), (0, 1.6)]] + bees, [], T)
