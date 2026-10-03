"""Butterflies & Bugs niche."""
import math

from ._kit import *  # noqa: F401,F403  (shared drawing kit)

T = "bugs"


@design("dragonfly", T)
def dragonfly(rng):
    body = tube([(0, 1.6 - 4.6 * k / 40) for k in range(41)], lambda t: 0.36 * (1 - t) + 0.1)
    head = circle(0, 1.9, 0.38, 30)
    wings = [ellipse(-1.6, 1.3, 1.5, 0.42, 60, rot=0.18), ellipse(-1.5, 0.6, 1.4, 0.38, 60, rot=-0.15),
             ellipse(1.6, 1.3, 1.5, 0.42, 60, rot=-0.18), ellipse(1.5, 0.6, 1.4, 0.38, 60, rot=0.15)]
    veins = [[(-0.3, 1.35), (-2.9, 1.55)], [(0.3, 1.35), (2.9, 1.55)], [(-0.3, 0.6), (-2.7, 0.4)], [(0.3, 0.6), (2.7, 0.4)]]
    segs = [[(-0.18, y), (0.18, y)] for y in (-0.2, -0.8, -1.4, -2.0)]
    return Design("Dragonfly", [body, head] + wings + veins + segs, [eye(-0.18, 2.0, 0.1), eye(0.18, 2.0, 0.1)], T)


@design("caterpillar", T)
def caterpillar(rng):
    segs = []
    for k in range(7):
        x = -2.4 + 0.75 * k
        y = 0.35 * math.sin(k * 0.9)
        segs.append(circle(x, y, 0.5, 40))
        segs.append([(x, y - 0.5), (x - 0.1, y - 0.9)])
    head = circle(2.9, 0.5, 0.65, 50)
    ants = [quad((2.7, 1.1), (2.6, 1.7), (2.3, 1.9)), quad((3.1, 1.1), (3.3, 1.7), (3.6, 1.8))]
    smile = arc(3.0, 0.45, 0.3, math.radians(210), math.radians(330), 12)
    leaf = chain(cubic((-3.4, -1.3), (-1.0, -2.6), (2.0, -2.2), (3.6, -1.2), 40), cubic((3.6, -1.2), (1.5, -0.9), (-1.0, -0.9), (-3.4, -1.3), 40))
    return Design("Caterpillar", segs + [head, smile, leaf] + ants,
                  [eye(2.8, 0.7, 0.09), eye(3.15, 0.7, 0.09), circle(2.3, 1.9, 0.08, 10), circle(3.6, 1.8, 0.08, 10)], T)


@design("ant", T)
def ant(rng):
    parts = [ellipse(-1.9, 0, 0.9, 0.7, 60), ellipse(-0.5, 0.05, 0.55, 0.42, 40), circle(0.8, 0.35, 0.6, 50)]
    legs = []
    for x in (-0.8, -0.5, -0.2):
        legs.append([(x, -0.2), (x - 0.4, -0.9), (x - 0.7, -1.6)])
        legs.append([(x, 0.3), (x + 0.2, 1.0), (x - 0.2, 1.5)])
    ants = [quad((1.1, 0.9), (1.6, 1.8), (2.3, 1.9)), quad((0.9, 0.95), (1.1, 1.9), (1.6, 2.4))]
    crumb = poly((2.0, -0.6), (2.9, -0.4), (2.7, -1.2), (2.0, -1.1))
    return Design("Busy Ant", parts + legs + ants + [crumb], [eye(1.05, 0.5, 0.1)], T)


@design("beetle", T)
def beetle(rng):
    shell = ellipse(0, -0.6, 1.25, 2.1, 140)
    split = [(0, 1.45), (0, -2.7)]
    thorax = ellipse(0, 1.55, 0.95, 0.5, 60)
    head = ellipse(0, 2.25, 0.6, 0.35, 40)
    jaws = [chain(quad((-0.35, 2.5), (-1.2, 3.2), (-0.6, 3.9)), [(-0.75, 3.35)]),
            chain(quad((0.35, 2.5), (1.2, 3.2), (0.6, 3.9)), [(0.75, 3.35)])]
    ridges = [quad((s * 0.35, 0.9), (s * 0.45, -0.6), (s * 0.3, -2.3)) for s in (-1, 1)] + \
             [quad((s * 0.75, 0.6), (s * 0.95, -0.6), (s * 0.65, -1.9)) for s in (-1, 1)]
    legs = []
    for y in (1.2, -0.2, -1.4):
        legs.append([(-1.1, y), (-2.0, y + 0.4), (-2.4, y - 0.1)])
        legs.append([(1.1, y), (2.0, y + 0.4), (2.4, y - 0.1)])
    return Design("Stag Beetle", [shell, split, thorax, head] + jaws + ridges + legs,
                  [eye(-0.35, 2.3, 0.08), eye(0.35, 2.3, 0.08)], T)


@design("spider_web", T)
def spider_web(rng):
    spokes = [[(0, 0), (3.0 * math.cos(math.radians(a)), 3.0 * math.sin(math.radians(a)))] for a in range(0, 360, 45)]
    rings = []
    for r in (0.7, 1.4, 2.1, 2.8):
        pts = []
        for k in range(9):
            a1, a2 = math.radians(45 * k), math.radians(45 * (k + 1))
            p1 = (r * math.cos(a1), r * math.sin(a1))
            p2 = (r * math.cos(a2), r * math.sin(a2))
            mid = ((p1[0] + p2[0]) * 0.45, (p1[1] + p2[1]) * 0.45)
            pts += quad(p1, mid, p2, 8)[:-1]
        rings.append(pts[:len(pts)] + [pts[0]])
    spider = circle(1.2, -1.6, 0.3, 24)
    thread = [(1.2, -1.3), (1.2, -0.1)]
    legs = [[(1.2, -1.6), (1.2 + 0.55 * s, -1.6 + d), (1.2 + 0.75 * s, -1.6 + d - 0.3)] for s in (-1, 1) for d in (0.25, 0.0, -0.25)]
    return Design("Spider Web", spokes + rings + [spider, thread] + legs, [], T)


@design("firefly", T)
def firefly(rng):
    body = ellipse(0, 0, 0.6, 1.4, 60)
    glow = ellipse(0, -1.0, 0.75, 0.75, 50)
    head = circle(0, 1.6, 0.4, 30)
    wings = [ellipse(-0.9, 0.5, 0.6, 1.2, 50, rot=0.4), ellipse(0.9, 0.5, 0.6, 1.2, 50, rot=-0.4)]
    rays = [[(1.2 * math.cos(a), -1.0 + 1.2 * math.sin(a)), (1.7 * math.cos(a), -1.0 + 1.7 * math.sin(a))]
            for a in [math.radians(d) for d in (200, 240, 270, 300, 340)]]
    ants = [quad((-0.2, 1.95), (-0.5, 2.5), (-0.9, 2.6)), quad((0.2, 1.95), (0.5, 2.5), (0.9, 2.6))]
    return Design("Firefly", [body, glow, head] + wings + rays + ants, [eye(-0.15, 1.65, 0.07), eye(0.15, 1.65, 0.07)], T)


@design("worm", T)
def worm(rng):
    cl = [(-2.6 + 5.0 * k / 60, -0.6 + 0.6 * math.sin(k / 60 * 2.5 * math.pi)) for k in range(61)]
    body = tube(cl, 0.7)
    rings = [[(cl[i][0], cl[i][1] - 0.35), (cl[i][0], cl[i][1] + 0.35)] for i in range(8, 56, 6)]
    hat = poly((2.1, 0.0), (2.7, 0.2), (2.6, 0.9), (2.0, 0.7))
    apple = [circle(-1.8, 1.6, 1.0, 80), quad((-1.8, 2.6), (-1.7, 3.0), (-1.4, 3.2))]
    return Design("Garden Worm", [body, hat] + rings + apple, [eye(2.25, -0.05, 0.08)], T)
