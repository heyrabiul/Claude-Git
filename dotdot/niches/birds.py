"""Birds niche."""
import math

from ._kit import *  # noqa: F401,F403  (shared drawing kit)

T = "birds"


@design("hummingbird", T)
def hummingbird(rng):
    body = chain(cubic((-0.6, 0.6), (0.4, 1.0), (1.4, 0.2), (2.6, -1.2), 40),
                 cubic((2.6, -1.2), (1.2, -0.6), (0.0, -0.4), (-0.6, 0.0), 30))
    head = circle(-0.9, 0.5, 0.55, 50)
    beak = poly((-1.4, 0.55), (-3.0, 0.75), (-1.42, 0.38), closed=False)
    wing = chain(cubic((0.0, 0.5), (0.2, 2.2), (1.6, 3.2), (2.4, 3.0), 40), cubic((2.4, 3.0), (1.6, 2.0), (0.9, 0.9), (0.5, 0.6), 30))
    feathers = [quad((0.4 + 0.25 * k, 0.9 + 0.3 * k), (1.0 + 0.2 * k, 1.6 + 0.3 * k), (1.6 + 0.15 * k, 2.4 + 0.15 * k)) for k in range(3)]
    flower = [lens((-3.4, -0.6), (-2.6, -1.6), 0.4), lens((-3.0, -1.6), (-2.2, -0.6), 0.4),
              [(-2.8, -1.4), (-2.6, -3.0)]]
    return Design("Hummingbird", [body, head, beak, wing] + feathers + flower, [eye(-1.0, 0.6, 0.09)], T)


@design("parrot", T)
def parrot(rng):
    body = chain(cubic((-0.4, 1.6), (-1.6, 1.4), (-1.4, -1.2), (-0.2, -1.8), 50),
                 cubic((-0.2, -1.8), (0.8, -1.2), (1.0, 0.6), (0.6, 1.4), 40))
    head = circle(0.0, 1.9, 0.75, 70)
    beak = chain(cubic((0.55, 2.2), (1.4, 2.3), (1.4, 1.4), (0.9, 1.3), 20), quad((0.9, 1.3), (0.8, 1.7), (0.6, 1.6), 10))
    wing = chain(cubic((-0.6, 1.0), (-1.5, 0.0), (-0.9, -1.8), (0.0, -2.2), 40))
    tail = [[(-0.4, -1.7), (-0.9, -3.6)], [(-0.1, -1.8), (-0.3, -3.8)], [(0.2, -1.7), (0.3, -3.5)]]
    perch = [(-2.4, -1.85), (2.2, -1.85)]
    feet = [arc(-0.3, -1.85, 0.2, math.pi, 2 * math.pi, 8), arc(0.3, -1.85, 0.2, math.pi, 2 * math.pi, 8)]
    eye_ring = circle(0.25, 2.1, 0.25, 24)
    return Design("Parrot", [body, head, beak, wing, perch, eye_ring] + tail + feet, [eye(0.27, 2.1, 0.1)], T)


@design("penguin", T)
def penguin(rng):
    body = chain(cubic((0, 2.6), (-1.6, 2.6), (-1.9, -1.8), (-0.9, -2.4), 50), [(0.9, -2.4)],
                 cubic((0.9, -2.4), (1.9, -1.8), (1.6, 2.6), (0, 2.6), 50))
    belly = chain(cubic((0, 1.4), (-1.2, 1.2), (-1.3, -1.8), (0, -2.1), 40), cubic((0, -2.1), (1.3, -1.8), (1.2, 1.2), (0, 1.4), 40))
    beak = poly((-0.25, 1.75), (0.25, 1.75), (0, 1.3))
    flips = [quad((-1.45, 0.6), (-2.3, -0.6), (-1.6, -1.2)), quad((1.45, 0.6), (2.3, -0.6), (1.6, -1.2))]
    feet = [lens((-0.9, -2.45), (-0.2, -2.45), 0.3), lens((0.2, -2.45), (0.9, -2.45), 0.3)]
    scarf = [quad((-1.2, 1.2), (0, 0.9), (1.2, 1.2)), [(0.7, 1.05), (1.0, 0.2), (0.6, 0.25)]]
    return Design("Penguin", [body, belly, beak] + flips + feet + scarf, [eye(-0.45, 2.05, 0.13), eye(0.45, 2.05, 0.13)], T)


@design("flamingo", T)
def flamingo(rng):
    body = chain(cubic((-1.8, 0.6), (-1.6, 1.8), (0.6, 1.8), (1.2, 0.8), 40), quad((1.2, 0.8), (0.0, -0.3), (-1.8, 0.6), 30))
    neck = tube(cubic((1.0, 1.1), (2.2, 1.8), (0.6, 2.8), (1.2, 3.8), 40), 0.28)
    head = circle(1.4, 3.9, 0.35, 30)
    beak = chain(quad((1.7, 3.9), (2.3, 3.6), (2.1, 3.1)))
    legs = [[(0.0, 0.3), (0.0, -3.0)], [(-0.1, -1.0), (-0.9, -0.6), (-0.3, -0.4)]]
    wing = quad((-1.4, 0.9), (-0.3, 1.5), (0.8, 0.9))
    water = [quad((-1.2, -3.0), (0, -3.2), (1.2, -3.0)), quad((-0.8, -3.4), (0, -3.55), (0.8, -3.4))]
    return Design("Flamingo", [body, neck, head, beak, wing] + legs + water, [eye(1.45, 4.0, 0.07)], T)


@design("duck", T)
def duck(rng):
    body = chain(cubic((-2.2, 0.6), (-2.0, -1.2), (1.4, -1.4), (1.8, 0.2), 50), quad((1.8, 0.2), (0.6, 0.6), (-0.2, 0.4), 20),
                 quad((-0.2, 0.4), (-1.4, 1.3), (-2.2, 0.6), 20))
    head = circle(1.3, 1.3, 0.75, 60)
    bill = chain(quad((1.95, 1.35), (2.9, 1.4), (2.9, 1.05)), quad((2.9, 1.05), (2.4, 0.9), (1.95, 1.0)))
    wing = chain(cubic((-1.2, 0.2), (-0.4, 0.8), (0.8, 0.4), (0.6, -0.2), 30), quad((0.6, -0.2), (-0.4, -0.5), (-1.2, 0.2), 20))
    water = [quad((-2.8 + 1.1 * k, -1.3), (-2.25 + 1.1 * k, -1.5), (-1.7 + 1.1 * k, -1.3)) for k in range(5)]
    return Design("Duck", [body, head, bill, wing] + water, [eye(1.45, 1.55, 0.1)], T)


@design("swan", T)
def swan(rng):
    body = chain(cubic((-2.4, 0.8), (-2.2, -1.2), (1.6, -1.4), (2.0, 0.0), 50), quad((2.0, 0.0), (1.0, 0.4), (0.8, 0.2), 15))
    neck = cubic((0.8, 0.2), (0.0, 1.6), (1.6, 2.6), (1.2, 3.2), 40)
    neck2 = cubic((1.25, 0.25), (0.5, 1.5), (2.0, 2.6), (1.6, 3.3), 40)
    head = arc(1.4, 3.3, 0.25, math.radians(-30), math.radians(200), 20)
    beak = poly((1.15, 3.35), (0.6, 3.15), (1.2, 3.1), closed=False)
    wing = chain(cubic((-2.4, 0.8), (-1.6, 2.2), (0.2, 1.4), (0.6, 0.2), 40))
    feathers = [quad((-1.8 + 0.5 * k, 0.9), (-1.4 + 0.5 * k, 0.4), (-1.0 + 0.5 * k, 0.6)) for k in range(4)]
    water = [quad((-2.8 + 1.1 * k, -1.35), (-2.25 + 1.1 * k, -1.55), (-1.7 + 1.1 * k, -1.35)) for k in range(5)]
    return Design("Graceful Swan", [body, neck, neck2, head, beak, wing] + feathers + water, [eye(1.45, 3.35, 0.06)], T)


@design("peacock", T)
def peacock(rng):
    fan = []
    for k in range(9):
        a = math.radians(20 + k * 140 / 8)
        cx, cy = 2.6 * math.cos(a), -0.5 + 2.6 * math.sin(a)
        fan.append([(0, -0.5), (cx * 0.78, -0.5 + (cy + 0.5) * 0.78)])
        fan.append(ellipse(cx, cy, 0.45, 0.6, 40, rot=a - math.pi / 2))
        fan.append(circle(cx, cy, 0.18, 16))
    body = chain(cubic((-0.4, -2.2), (-0.8, -0.6), (-0.4, 0.8), (0, 1.0), 30), cubic((0, 1.0), (0.4, 0.8), (0.8, -0.6), (0.4, -2.2), 30))
    head = circle(0, 1.3, 0.35, 30)
    crest = [[(0, 1.65), (-0.3, 2.2)], [(0, 1.65), (0, 2.3)], [(0, 1.65), (0.3, 2.2)]]
    beak = poly((0.3, 1.35), (0.65, 1.25), (0.3, 1.15), closed=False)
    return Design("Peacock", fan + [body, head, beak] + crest, [eye(0.1, 1.4, 0.06)], T)


@design("birdhouse", T)
def birdhouse(rng):
    house = poly((-1.4, -1.8), (1.4, -1.8), (1.4, 0.8), (0, 2.0), (-1.4, 0.8))
    roof = poly((-1.8, 0.6), (0, 2.4), (1.8, 0.6), closed=False)
    hole = circle(0, 0.2, 0.45, 40)
    perch = [(0, -0.5), (0, -0.9)]
    post = [[(-0.25, -1.8), (-0.25, -3.4)], [(0.25, -1.8), (0.25, -3.4)]]
    bird = chain(cubic((1.6, 2.4), (1.8, 3.2), (2.8, 3.2), (3.0, 2.6), 20), quad((3.0, 2.6), (2.4, 2.1), (1.6, 2.4), 12))
    beak = poly((3.0, 2.75), (3.4, 2.65), (3.0, 2.55), closed=False)
    return Design("Birdhouse", [house, roof, hole, perch, bird, beak] + post, [eye(2.7, 2.8, 0.07)], T)


@design("feather", T)
def feather(rng):
    vane = chain(cubic((0, -2.8), (1.6, -1.0), (1.3, 1.8), (0.2, 3.0), 50), cubic((0.2, 3.0), (-1.1, 1.8), (-1.3, -1.0), (0, -2.8), 50))
    shaft = cubic((0.2, -3.6), (0.1, -1.0), (0.0, 1.0), (0.2, 3.0), 40)
    barbs = []
    for k in range(7):
        y = -1.8 + 0.65 * k
        barbs.append(quad((0.05, y), (0.6, y + 0.3), (1.0, y + 0.55)))
        barbs.append(quad((0.05, y), (-0.5, y + 0.3), (-0.9, y + 0.55)))
    return Design("Feather", [vane, shaft] + barbs, [], T)


@design("nest", T)
def nest(rng):
    nest_ = chain(arc(0, 0.2, 2.4, math.radians(195), math.radians(345), 60), [(-2.32, -0.42)])
    twigs = [quad((-2.2, -0.2 - 0.3 * k), (0, -0.8 - 0.35 * k), (2.2, -0.2 - 0.3 * k)) for k in range(4)]
    eggs = [ellipse(-0.9, -0.05, 0.5, 0.65, 40, rot=0.2), ellipse(0.05, 0.1, 0.5, 0.68, 40), ellipse(0.95, -0.05, 0.5, 0.65, 40, rot=-0.2)]
    spots = [circle(-0.9, 0.2, 0.08, 10), circle(0.1, -0.2, 0.08, 10), circle(1.0, 0.25, 0.08, 10)]
    branch = [(-3.0, -1.4), (3.0, -1.6)]
    leaves = [lens((2.4, -1.55), (3.2, -0.9), 0.35), lens((-2.6, -1.42), (-3.3, -0.8), 0.35)]
    return Design("Bird Nest", [nest_, branch] + twigs + eggs + leaves, spots, T)
