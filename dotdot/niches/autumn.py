"""Autumn niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "autumn"


@design("oak_leaf", T)
def oak_leaf(rng):
    pts = []
    for i in range(201):
        t = i / 200
        y = -2.4 + 5.0 * t
        w = 1.4 * math.sin(math.pi * t) * (1 + 0.28 * math.sin(10 * math.pi * t))
        pts.append((w, y))
    leaf = chain(pts, mirror_x(pts)[::-1])
    stem = [(0, -2.4), (0.1, -3.2)]
    veins = [[(0, -2.4), (0, 2.4)]] + [[(0, -1.6 + 0.8 * k), (s * 1.0, -1.1 + 0.8 * k)] for k in range(4) for s in (-1, 1)]
    return Design("Oak Leaf", [leaf, stem] + veins, [], T)


@design("squirrel", T)
def squirrel(rng):
    body = chain(cubic((-0.5, 1.0), (-1.2, 0.2), (-1.0, -1.6), (0.0, -1.8), 40), quad((0.0, -1.8), (1.0, -1.4), (0.6, 0.6), 20))
    head = circle(0.2, 1.4, 0.65, 50)
    ear = poly((-0.1, 1.95), (0.0, 2.5), (0.3, 2.0), closed=False)
    tail = chain(cubic((-0.8, -1.5), (-3.4, -1.2), (-3.4, 2.4), (-1.6, 3.0), 50),
                 cubic((-1.6, 3.0), (-0.6, 3.3), (-0.4, 2.4), (-1.0, 2.2), 20),
                 cubic((-1.0, 2.2), (-2.2, 1.8), (-2.0, -0.2), (-0.85, -0.4), 40))
    fur = [quad((-2.6, 0.2 + 0.7 * k), (-2.1, 0.4 + 0.7 * k), (-1.8, 0.2 + 0.7 * k)) for k in range(3)]
    acorn = [ellipse(0.95, 0.1, 0.3, 0.38, 24), arc(0.95, 0.25, 0.32, 0, math.pi, 12)]
    paws = [quad((0.4, 0.4), (0.9, 0.5), (0.8, 0.0))]
    feet = [ellipse(0.4, -1.85, 0.45, 0.18, 20)]
    return Design("Squirrel", [body, head, ear, tail] + fur + acorn + paws + feet, [eye(0.4, 1.55, 0.09)], T)


@design("scarecrow", T)
def scarecrow(rng):
    hat = [poly((-0.7, 1.9), (0, 3.0), (0.7, 1.9), closed=False), ellipse(0, 1.9, 1.3, 0.25, 50)]
    head = circle(0, 1.2, 0.65, 50)
    smile = arc(0, 1.15, 0.35, math.radians(210), math.radians(330), 12)
    body = poly((-0.8, 0.5), (-0.9, -1.5), (0.9, -1.5), (0.8, 0.5))
    arms = [[(-0.8, 0.2), (-2.6, 0.4)], [(0.8, 0.2), (2.6, 0.4)]]
    straw = [[(-2.6, 0.4), (-3.0, 0.7)], [(-2.6, 0.4), (-3.0, 0.1)], [(2.6, 0.4), (3.0, 0.7)], [(2.6, 0.4), (3.0, 0.1)]]
    patch = rect(-0.5, -0.9, -0.1, -0.5)
    post = [(0, -1.5), (0, -3.0)]
    crow = chain(cubic((1.6, 0.45), (1.8, 1.2), (2.6, 1.2), (2.7, 0.7), 16), [(1.6, 0.45)])
    return Design("Scarecrow", hat + [head, smile, body, patch, post, crow] + arms + straw, [eye(-0.25, 1.35, 0.08), eye(0.25, 1.35, 0.08)], T)


@design("hedgehog", T)
def hedgehog(rng):
    spikes = [(r * math.cos(t), -0.4 + r * 0.75 * math.sin(t)) for t, r in [(math.pi * i / 80, 2.2 + (0.3 if i % 2 else 0.0)) for i in range(81)]]
    back = chain(spikes, [(-2.2, -0.4)])
    face = chain(quad((1.6, 0.6), (2.6, 0.2), (2.9, -0.4), 16), quad((2.9, -0.4), (2.2, -0.6), (1.6, -0.6), 10))
    belly = [(-2.2, -0.4), (1.6, -0.6)]
    nose = circle(2.95, -0.4, 0.12, 12)
    feet = [arc(x, -0.65, 0.2, math.pi, 2 * math.pi, 8) for x in (-1.2, 0.8)]
    leaves = [lens((-2.8, -1.2), (-1.8, -1.4), 0.3), lens((2.0, -1.2), (3.0, -1.0), 0.3)]
    return Design("Hedgehog", [back, face, belly, nose] + feet + leaves, [eye(2.1, 0.0, 0.08)], T)


@design("fall_tree", T)
def fall_tree(rng):
    trunk = [quad((-0.3, -2.8), (-0.2, -1.0), (-1.0, 0.2)), quad((0.3, -2.8), (0.2, -1.0), (1.0, 0.4)), [(0.0, -1.0), (0.1, 0.6)]]
    crown = [circle(x, y, r, 50) for x, y, r in [(-1.0, 0.9, 0.9), (0.6, 1.1, 1.0), (-0.1, 2.0, 0.9), (1.5, 0.3, 0.6)]]
    falling = [lens((x, y), (x + 0.4, y - 0.3), 0.4) for x, y in [(-2.4, -0.6), (2.2, -1.2), (-1.6, -2.0), (1.8, -2.4)]]
    pile = [arc(0, -3.4, 2.0, math.radians(30), math.radians(150), 30)]
    return Design("Autumn Tree", trunk + crown + falling + pile, [], T)


@design("mushroom_cluster", T)
def mushroom_cluster(rng):
    out = []
    for cx, s in [(-1.4, 0.8), (0.3, 1.1), (1.7, 0.7)]:
        cap = chain(arc(cx, 0.0, 1.0 * s, 0, math.pi, 30), quad((cx - s, 0), (cx, -0.25 * s), (cx + s, 0), 12))
        stem = poly((cx - 0.25 * s, -0.15 * s), (cx - 0.3 * s, -2.2), (cx + 0.3 * s, -2.2), (cx + 0.25 * s, -0.15 * s), closed=False)
        out += [cap, stem, [(cx - 0.6 * s, 0.4 * s), (cx + 0.6 * s, 0.4 * s)]]
    grass = [zigzag(-2.8, 2.8, -2.2, 0.15, 14)]
    return Design("Toadstools", out + grass, [], T)


@design("pine_cone", T)
def pine_cone(rng):
    cone = chain(cubic((0, 2.4), (1.6, 1.8), (1.6, -1.6), (0, -2.6), 40), cubic((0, -2.6), (-1.6, -1.6), (-1.6, 1.8), (0, 2.4), 40))
    scales = []
    for row in range(6):
        y = 1.6 - 0.75 * row
        w = 1.2 * math.sin(math.pi * (row + 0.7) / 6.6)
        for k in range(3):
            x = -w + w * k
            scales.append(arc(x, y, 0.42, math.radians(200), math.radians(340), 10))
    stem = [(0, 2.4), (0.2, 3.0)]
    needles = [[(0.2, 2.9), (1.2 + 0.2 * k, 3.6 - 0.3 * k)] for k in range(3)]
    return Design("Pine Cone", [cone, stem] + scales + needles, [], T)


@design("rain_boots", T)
def rain_boots(rng):
    def boot(dx):
        b = poly((-0.7, 2.0), (0.5, 2.0), (0.5, -0.8), (1.6, -1.0), (1.6, -1.8), (-0.7, -1.8))
        top = [(-0.7, 1.6), (0.5, 1.6)]
        sole = [(-0.7, -1.5), (1.6, -1.5)]
        return [transform(p, dx=dx) for p in [b, top, sole]]
    puddle = [ellipse(0, -2.1, 3.2, 0.35, 100)]
    drops = [lens((x, y), (x, y - 0.5), 0.4) for x, y in [(-2.6, 2.8), (0.2, 3.0), (2.6, 2.6)]]
    return Design("Rain Boots", boot(-1.4) + boot(0.8) + puddle + drops, [], T)


@design("cider_mug", T)
def cider_mug(rng):
    mug = rrect(-1.6, -2.0, 1.4, 1.0, 0.25)
    handle = arc(1.4, -0.5, 0.8, math.radians(-90), math.radians(90), 20)
    cinnamon = [rect(-0.6, 0.8, -0.3, 2.6), rect(-0.25, 0.8, 0.05, 2.5)]
    slice_ = [circle(0.8, 1.2, 0.55, 40), circle(0.8, 1.2, 0.4, 30)] + [[(0.8, 1.2), (0.8 + 0.4 * math.cos(a), 1.2 + 0.4 * math.sin(a))] for a in [k * math.pi / 3 for k in range(6)]]
    leaf = lens((-1.0, -0.6), (0.4, 0.0), 0.35)
    return Design("Apple Cider", [mug, handle, leaf] + cinnamon + slice_, [], T)
