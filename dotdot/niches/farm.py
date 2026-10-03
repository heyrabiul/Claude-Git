"""Farm Life niche."""
import math

from ._kit import *  # noqa: F401,F403  (shared drawing kit)

T = "farm"


@design("cow", T)
def cow(rng):
    head = chain(cubic((-1.2, 1.4), (-1.4, -0.2), (-1.0, -1.0), (0, -1.0), 30), cubic((0, -1.0), (1.0, -1.0), (1.4, -0.2), (1.2, 1.4), 30),
                 quad((1.2, 1.4), (0, 2.0), (-1.2, 1.4), 20))
    muzzle = ellipse(0, -0.75, 1.0, 0.6, 60)
    nostrils = [ellipse(-0.35, -0.75, 0.13, 0.2, 14), ellipse(0.35, -0.75, 0.13, 0.2, 14)]
    ears = [ellipse(-1.8, 1.0, 0.65, 0.3, 40, rot=-0.3), ellipse(1.8, 1.0, 0.65, 0.3, 40, rot=0.3)]
    horns = [quad((-0.8, 1.7), (-1.2, 2.5), (-0.6, 2.7)), quad((0.8, 1.7), (1.2, 2.5), (0.6, 2.7))]
    spot = chain(cubic((0.3, 1.6), (1.2, 1.5), (1.1, 0.5), (0.5, 0.7), 20), quad((0.5, 0.7), (0.2, 1.1), (0.3, 1.6), 10))
    bell = [chain(arc(0, -1.6, 0.35, 0, math.pi, 16), [(0.35, -1.6)]), [(-0.4, -1.0), (0, -1.25), (0.4, -1.0)]]
    return Design("Dairy Cow", [head, muzzle, spot] + nostrils + ears + horns + bell, [eye(-0.5, 0.45, 0.13), eye(0.5, 0.45, 0.13)], T)


@design("pig", T)
def pig(rng):
    body = ellipse(0, 0, 2.3, 1.5, 160)
    head = circle(-1.9, 0.6, 1.0, 80)
    snout = ellipse(-2.6, 0.35, 0.45, 0.35, 40)
    nostrils = [circle(-2.75, 0.35, 0.08, 10), circle(-2.45, 0.35, 0.08, 10)]
    ears = [poly((-2.3, 1.4), (-2.6, 2.1), (-1.9, 1.6), closed=False), poly((-1.5, 1.5), (-1.2, 2.2), (-1.1, 1.4), closed=False)]
    legs = [rect(x, -2.1, x + 0.45, -1.2) for x in (-1.3, -0.4, 0.6, 1.4)]
    tail = spiral(2.45, 0.4, 0.05, 0.3, 1.5, 40)
    mud = [ellipse(0, -2.3, 2.8, 0.25, 60)]
    return Design("Little Pig", [body, head, snout, tail] + ears + legs + mud, nostrils + [eye(-2.2, 0.95, 0.09)], T)


@design("sheep", T)
def sheep(rng):
    fleece = polar(lambda t: 1.8 + 0.18 * math.sin(14 * t), n=500)
    fleece = [(1.15 * x, y) for x, y in fleece]
    head = ellipse(-2.0, 0.3, 0.6, 0.8, 50)
    ears = [ellipse(-2.6, 0.7, 0.4, 0.15, 20, rot=0.4), ellipse(-1.45, 0.75, 0.4, 0.15, 20, rot=-0.4)]
    tuft = arc(-2.0, 1.0, 0.35, 0, math.pi, 16)
    legs = [rect(x, -2.6, x + 0.3, -1.6) for x in (-1.0, -0.3, 0.6, 1.3)]
    curls = [arc(x, y, 0.25, 0, 1.5 * math.pi, 14) for x, y in [(-0.6, 0.6), (0.5, 0.9), (0.9, -0.4), (-0.3, -0.6)]]
    return Design("Woolly Sheep", [fleece, head, tuft] + ears + legs + curls, [eye(-2.15, 0.4, 0.08)], T)


@design("hen", T)
def hen(rng):
    body = chain(cubic((-0.4, 1.2), (-2.4, 1.6), (-2.6, -1.6), (0, -1.6), 50), cubic((0, -1.6), (1.8, -1.6), (1.6, 0.8), (0.9, 1.5), 40))
    head = circle(0.5, 1.7, 0.65, 60)
    comb = [arc(0.2 + 0.3 * k, 2.4, 0.18, 0, math.pi, 10) for k in range(3)]
    beak = poly((1.1, 1.8), (1.6, 1.65), (1.1, 1.5), closed=False)
    wattle = lens((1.05, 1.45), (1.0, 0.95), 0.4)
    wing = chain(cubic((-1.4, 0.6), (-0.4, 0.8), (0.6, 0.0), (0.2, -0.6), 30), quad((0.2, -0.6), (-0.8, -0.6), (-1.4, 0.6), 20))
    tail = [quad((-1.7, 0.8), (-2.6, 1.6), (-2.3, 2.4)), quad((-1.9, 0.5), (-3.0, 1.2), (-2.9, 2.0))]
    legs = [[(-0.4, -1.6), (-0.4, -2.4)], [(0.3, -1.6), (0.3, -2.4)]]
    eggs = [ellipse(2.1, -2.0, 0.4, 0.5, 30), ellipse(2.8, -2.05, 0.35, 0.45, 30)]
    return Design("Mother Hen", [body, head, beak, wattle, wing] + comb + tail + legs + eggs, [eye(0.65, 1.85, 0.09)], T)


@design("horse_head", T)
def horse_head(rng):
    head = chain(cubic((0.6, 2.6), (1.6, 2.0), (2.6, 0.2), (2.6, -0.8), 40), cubic((2.6, -0.8), (2.6, -1.6), (1.6, -1.8), (1.2, -1.2), 30),
                 cubic((1.2, -1.2), (0.6, -0.2), (-0.4, -0.6), (-1.0, -2.8), 30))
    neck_back = cubic((0.6, 2.6), (-0.6, 2.2), (-1.8, 0.8), (-2.2, -2.8), 40)
    ear = poly((0.4, 2.5), (0.6, 3.4), (1.0, 2.6), closed=False)
    mane = [quad((0.2 - 0.35 * k, 2.4 - 0.55 * k), (-0.6 - 0.35 * k, 2.2 - 0.55 * k), (-0.9 - 0.35 * k, 1.6 - 0.55 * k)) for k in range(6)]
    nostril = ellipse(2.25, -0.9, 0.15, 0.25, 14)
    mouth = quad((2.4, -1.4), (2.0, -1.45), (1.7, -1.3))
    bridle = [[(1.0, 1.4), (2.3, -0.3)], [(1.0, 1.4), (1.3, -0.9)]]
    return Design("Horse Head", [head, neck_back, ear, nostril, mouth] + mane + bridle, [eye(1.15, 1.05, 0.13)], T)


@design("barn", T)
def barn(rng):
    walls = poly((-2.2, -2.0), (2.2, -2.0), (2.2, 0.6), (0, 2.0), (-2.2, 0.6))
    roof = poly((-2.6, 0.5), (-1.6, 1.6), (0, 2.5), (1.6, 1.6), (2.6, 0.5), closed=False)
    door = rect(-0.9, -2.0, 0.9, -0.2)
    cross = [[(-0.9, -2.0), (0.9, -0.2)], [(-0.9, -0.2), (0.9, -2.0)]]
    loft = rect(-0.45, 0.4, 0.45, 1.2)
    weather = [[(0, 2.5), (0, 3.2)], [(-0.4, 3.0), (0.5, 3.0)], poly((0.5, 3.0), (0.3, 3.15), (0.3, 2.85))]
    fence = [[(2.2, -1.2), (3.4, -1.2)], [(2.2, -1.7), (3.4, -1.7)], [(2.9, -2.0), (2.9, -0.9)]]
    return Design("Red Barn", [walls, roof, door, loft] + cross + weather + fence, [], T)


@design("tractor", T)
def tractor(rng):
    cab = poly((-0.6, 0.0), (-0.6, 2.2), (1.0, 2.2), (1.2, 0.0), closed=False)
    window = rect(-0.35, 1.0, 0.85, 1.9)
    hood = rect(1.2, -0.6, 3.0, 0.6)
    pipe = rect(2.3, 0.6, 2.5, 1.4)
    body = rect(-1.6, -0.6, 1.2, 0.0)
    big = circle(-1.0, -1.1, 1.2, 90)
    big_hub = circle(-1.0, -1.1, 0.4, 30)
    small = circle(2.4, -1.4, 0.75, 60)
    small_hub = circle(2.4, -1.4, 0.25, 20)
    smoke = [circle(2.6, 1.8, 0.2, 16), circle(2.9, 2.3, 0.28, 18), circle(3.3, 2.9, 0.35, 20)]
    return Design("Farm Tractor", [cab, window, hood, pipe, body, big, big_hub, small, small_hub] + smoke, [], T)


@design("windmill", T)
def windmill(rng):
    tower = poly((-1.0, -3.0), (-0.6, 1.0), (0.6, 1.0), (1.0, -3.0))
    cap = chain(arc(0, 1.0, 0.75, 0, math.pi, 24), [(0.75, 1.0)])
    hub = circle(0, 1.3, 0.2, 16)
    blades = []
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        blades.append(transform(rect(0.2, -0.3, 2.6, 0.3), dx=0, dy=1.3, rot=a))
    door = chain([(-0.3, -3.0), (-0.3, -2.2)], arc(0, -2.2, 0.3, math.pi, 0, 12), [(0.3, -3.0)])
    window = circle(0, -0.8, 0.25, 20)
    return Design("Windmill", [tower, cap, hub, door, window] + blades, [], T)


@design("egg_basket", T)
def egg_basket(rng):
    basket = chain([(-2.2, 0.0)], quad((-2.0, -2.2), (0, -2.4), (2.0, -2.2), 40), [(2.2, 0.0), (-2.2, 0.0)])
    handle = arc(0, 0.0, 2.0, 0, math.pi, 50)
    weave = [quad((-2.1, -0.6 - 0.5 * k), (0, -0.8 - 0.5 * k), (2.1, -0.6 - 0.5 * k)) for k in range(3)]
    eggs = [ellipse(x, 0.4, 0.45, 0.6, 40, rot=r) for x, r in [(-1.2, 0.3), (-0.4, 0.1), (0.4, -0.1), (1.2, -0.3)]]
    return Design("Basket of Eggs", [basket, handle] + weave + eggs, [], T)


@design("milk_can", T)
def milk_can(rng):
    body = poly((-1.2, -2.6), (-1.2, 0.4), (-0.6, 1.4), (-0.6, 2.2), (0.6, 2.2), (0.6, 1.4), (1.2, 0.4), (1.2, -2.6))
    lid = rect(-0.8, 2.2, 0.8, 2.6)
    handles = [arc(-1.2, 0.6, 0.4, math.radians(90), math.radians(270), 14), arc(1.2, 0.6, 0.4, math.radians(-90), math.radians(90), 14)]
    bands = [[(-1.2, -0.4), (1.2, -0.4)], [(-1.2, -2.2), (1.2, -2.2)]]
    flowers = [circle(2.2, -2.0, 0.25, 20), [(2.2, -2.25), (2.2, -2.6)], circle(-2.1, -1.8, 0.25, 20), [(-2.1, -2.05), (-2.1, -2.6)]]
    return Design("Milk Can", [body, lid] + handles + bands + flowers, [], T)
