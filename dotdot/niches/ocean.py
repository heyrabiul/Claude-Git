"""Ocean Life niche."""
import math

from ._kit import *  # noqa: F401,F403  (shared drawing kit)

T = "ocean"


@design("octopus", T)
def octopus(rng):
    head = chain(arc(0, 1.3, 1.45, math.radians(-15), math.radians(195), 80),
                 quad((-1.4, 0.92), (0, 0.2), (1.4, 0.92)))
    arms = []
    for i in range(6):
        x0 = -1.15 + i * 0.46
        side = -1 if i < 3 else 1
        reach = 1.2 + 0.25 * (i % 3)
        cl = [(x0 + side * reach * t + 0.22 * math.sin(5 * t + i), 0.5 - 2.6 * t) for t in [k / 40 for k in range(41)]]
        curl = spiral(cl[-1][0] + side * 0.18, cl[-1][1] + 0.05, 0.05, 0.2, 1.0, 30, rot=0 if side > 0 else math.pi)
        arms.append(tube(cl, lambda t: 0.34 * (1 - t) + 0.06, cap=False))
        arms.append(curl)
    eyes = [circle(-0.55, 1.45, 0.32, 30), circle(0.55, 1.45, 0.32, 30)]
    smile = arc(0, 1.05, 0.35, math.radians(210), math.radians(330), 14)
    return Design("Octopus", [head] + arms + eyes + [smile], [eye(-0.5, 1.5), eye(0.6, 1.5)], T)


@design("crab", T)
def crab(rng):
    body = ellipse(0, 0, 1.6, 1.0, 140)
    stalks = [[(-0.45, 0.9), (-0.6, 1.6)], [(0.45, 0.9), (0.6, 1.6)]]
    eyes = [circle(-0.6, 1.8, 0.22, 24), circle(0.6, 1.8, 0.22, 24)]
    claws = []
    for s in (-1, 1):
        claws.append(quad((s * 1.45, 0.4), (s * 2.1, 0.9), (s * 2.2, 1.6)))
        claws.append(arc(s * 2.35, 2.05, 0.5, math.radians(-110 if s > 0 else -70) + (0.5 if s > 0 else -0.5),
                         math.radians(-110 if s > 0 else -70) + (5.3 if s > 0 else -5.3), 40))
        for k in range(3):
            y = -0.1 - k * 0.35
            claws.append([(s * 1.5, y), (s * 2.3, y - 0.25), (s * 2.6, y - 0.75)])
    smile = arc(0, 0.1, 0.5, math.radians(210), math.radians(330), 16)
    return Design("Happy Crab", [body] + stalks + eyes + claws + [smile], [eye(-0.6, 1.8, 0.09), eye(0.6, 1.8, 0.09)], T)


@design("seahorse", T)
def seahorse(rng):
    cl = chain([(0.1, 2.5), (0.45, 1.9)], cubic((0.45, 1.9), (0.9, 1.0), (-0.6, 0.4), (0.1, -0.6), 40),
               cubic((0.1, -0.6), (0.6, -1.3), (0.2, -2.1), (-0.4, -1.9), 30))
    body = tube(cl, lambda t: 1.0 * (1 - t) ** 0.7 + 0.12, cap=False)
    tail = spiral(-0.55, -1.55, 0.08, 0.38, 1.1, 50, rot=-0.6)
    head = circle(0.05, 2.55, 0.55, 60)
    snout = tube([(-0.35, 2.45), (-1.5, 2.25)], lambda t: 0.36 - 0.12 * t)
    fin = [(0.75, 1.0), (1.45, 1.35), (1.4, 0.55), (1.5, 0.0), (0.7, 0.3)]
    crest = [(-0.1, 3.0), (0.05, 3.45), (0.25, 3.05), (0.45, 3.35), (0.5, 2.85)]
    ridges = [quad((-0.25 + 0.05 * k, 1.3 - 0.45 * k), (0.1, 1.25 - 0.45 * k), (0.45 - 0.05 * k, 1.35 - 0.45 * k)) for k in range(5)]
    bubbles = [circle(-1.6, 3.0, 0.15, 16), circle(-1.4, 3.5, 0.2, 18), circle(-1.75, 3.9, 0.12, 14)]
    return Design("Seahorse", [body, tail, head, snout, fin, crest] + ridges + bubbles, [eye(0.1, 2.65, 0.1)], T)


@design("jellyfish", T)
def jellyfish(rng):
    bell = chain(arc(0, 1.0, 1.7, 0, math.pi, 90),
                 [(-1.7 + 0.34 * i, 1.0 + (0.0 if i % 2 == 0 else -0.25)) for i in range(11)])
    inner = arc(0, 1.0, 1.1, math.radians(20), math.radians(160), 40)
    tentacles = []
    for i in range(6):
        x0 = -1.3 + i * 0.52
        L = 3.0 + 0.6 * ((i * 7) % 3)
        tentacles.append([(x0 + 0.25 * math.sin(4 * t + i), 0.85 - L * t) for t in [k / 60 for k in range(61)]])
    arms = [tube([(x + 0.18 * math.sin(6 * t), 0.8 - 2.2 * t) for t in [k / 40 for k in range(41)]], 0.28)
            for x in (-0.35, 0.35)]
    return Design("Jellyfish", [bell, inner] + tentacles + arms, [eye(-0.45, 1.6), eye(0.45, 1.6)], T)


@design("starfish", T)
def starfish(rng):
    outer = polar(lambda t: 0.42 + 0.58 * ((1 + math.cos(5 * t)) / 2) ** 1.6, n=600, rot=math.pi / 2)
    inner = polar(lambda t: 0.2 + 0.25 * ((1 + math.cos(5 * t)) / 2) ** 1.6, n=400, rot=math.pi / 2)
    dots = [circle(0.62 * math.cos(math.pi / 2 + k * TAU / 5), 0.62 * math.sin(math.pi / 2 + k * TAU / 5), 0.06, 10) for k in range(5)]
    return Design("Starfish", [outer, inner], dots, T)


@design("dolphin", T)
def dolphin(rng):
    body = chain(cubic((-3.0, 0.2), (-2.6, 0.4), (-2.3, 0.9), (-1.8, 1.0), 20),
                 cubic((-1.8, 1.0), (-0.8, 1.5), (0.4, 1.4), (1.0, 1.15), 30),
                 [(0.3, 2.1)], quad((0.3, 2.1), (1.2, 1.7), (1.5, 1.0), 16),
                 quad((1.5, 1.0), (2.2, 0.6), (2.6, 0.45), 16),
                 [(3.2, 1.2), (3.0, 0.3), (3.4, -0.5), (2.5, 0.05)],
                 quad((2.5, 0.05), (1.4, -0.3), (0.2, -0.75), 20),
                 [(-0.4, -1.6), (-0.9, -0.7)],
                 cubic((-0.9, -0.7), (-1.6, -0.6), (-2.2, -0.3), (-2.6, -0.05), 20), [(-3.0, 0.2)])
    mouth = quad((-3.0, 0.2), (-2.6, 0.0), (-2.3, 0.1))
    belly = quad((-2.3, -0.2), (-1.0, -0.3), (0.5, -0.5))
    waves_ = [arc(-1.0 + 1.0 * k, -2.4, 0.5, 0, math.pi, 20) for k in range(4)]
    return Design("Dolphin", [body, mouth, belly] + waves_, [eye(-1.9, 0.6)], T)


@design("shark", T)
def shark(rng):
    body = chain(quad((-3.2, 0.0), (-2.5, 0.9), (-1.2, 1.0), 20),
                 [(-0.4, 1.05), (0.1, 2.2), (0.7, 1.0)],
                 quad((0.7, 1.0), (2.0, 0.8), (2.6, 0.3), 16),
                 [(3.4, 1.6), (3.0, 0.0), (3.4, -1.2), (2.6, -0.2)],
                 quad((2.6, -0.2), (1.5, -0.7), (0.4, -0.8), 16),
                 [(-0.1, -1.6), (-0.6, -0.8)],
                 quad((-0.6, -0.8), (-2.2, -0.75), (-3.2, 0.0), 20))
    gills = [quad((-1.6 + 0.25 * k, 0.45), (-1.45 + 0.25 * k, 0.0), (-1.6 + 0.25 * k, -0.4)) for k in range(3)]
    mouth = [(-2.9, -0.15), (-2.5, -0.35), (-2.3, -0.2)]
    bubbles = [circle(-3.4, 1.2, 0.15, 16), circle(-3.6, 1.7, 0.2, 18)]
    return Design("Shark", [body, mouth] + gills + bubbles, [eye(-2.3, 0.35)], T)


@design("scallop", T)
def scallop(rng):
    edge = polar(lambda t: 2.4 + 0.12 * math.cos(18 * t), math.radians(25), math.radians(155), 300, cy=-1.6)
    shell = chain([(0, -1.6)], edge, [(0, -1.6)])
    ribs = [[(0, -1.6), (2.4 * math.cos(math.radians(a)), -1.6 + 2.4 * math.sin(math.radians(a)))] for a in range(40, 150, 14)]
    ear = poly((-0.6, -1.6), (0.6, -1.6), (0.45, -2.1), (-0.45, -2.1))
    pearl = circle(1.9, -1.9, 0.3, 30)
    return Design("Scallop Shell", [shell, ear, pearl] + ribs, [], T)


@design("coral", T)
def coral(rng):
    out = []

    def branch(x, y, ang, L, d):
        x2, y2 = x + L * math.cos(ang), y + L * math.sin(ang)
        out.append([(x, y), (x2, y2)])
        if d == 0:
            out.append(circle(x2, y2, 0.12, 14))
            return
        for da in (-0.45, 0.4):
            branch(x2, y2, ang + da + rng.uniform(-0.1, 0.1), L * 0.72, d - 1)

    branch(0, -2.0, math.pi / 2, 1.3, 4)
    rocks = [chain(arc(-1.6, -2.0, 0.7, 0, math.pi, 30), [(0.9, -2.0)]), arc(1.6, -2.0, 0.6, 0, math.pi, 24)]
    return Design("Coral Reef", out + rocks, [], T)


@design("treasure", T)
def treasure(rng):
    box = rect(-2, -1.6, 2, 0.3)
    lid = chain(arc(0, 0.3, 2.0, math.pi, 0, 60), [(-2, 0.3)])
    bands = [rect(-1.4, -1.6, -1.0, 1.85), rect(1.0, -1.6, 1.4, 1.85)]
    lock = [rect(-0.35, -0.5, 0.35, 0.4), circle(0, -0.05, 0.12, 14)]
    coins = [ellipse(x, -1.85, 0.35, 0.12, 30) for x in (-2.6, -2.1, 2.3)]
    return Design("Treasure Chest", [box, lid] + bands + lock + coins, [], T)
