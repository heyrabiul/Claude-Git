"""Sweets & Desserts niche."""
import math

from ._kit import *  # noqa: F401,F403  (shared drawing kit)

T = "desserts"


@design("donut", T)
def donut(rng):
    ring = circle(0, 0, 2.1, 160)
    hole = circle(0, 0, 0.7, 60)
    icing = [(r * math.cos(t), r * math.sin(t)) for t, r in
             [(2 * math.pi * i / 200, 1.7 + 0.18 * math.sin(9 * 2 * math.pi * i / 200)) for i in range(201)]]
    inner = circle(0, 0, 0.95, 70)
    sprinkles = [transform([(-0.15, 0), (0.15, 0)], dx=1.3 * math.cos(a), dy=1.3 * math.sin(a), rot=a * 2.3)
                 for a in [2 * math.pi * k / 12 + 0.2 for k in range(12)]]
    return Design("Sprinkle Donut", [ring, hole, icing, inner] + sprinkles, [], T)


@design("cake_slice", T)
def cake_slice(rng):
    top = poly((-2.2, 0.6), (2.2, 0.6), (0.4, 2.0), closed=True)
    front = rect(-2.2, -1.8, 2.2, 0.6)
    side = poly((2.2, 0.6), (2.2, -1.8), (0.4, -0.6), (0.4, 2.0), closed=False)
    layers = [[(-2.2, -0.2), (2.2, -0.2)], [(-2.2, -1.0), (2.2, -1.0)]]
    drips = wave(-2.2, 2.2, 0.35, 0.18, 5, 80)
    berry = [circle(0.0, 1.5, 0.35, 30), quad((0.0, 1.85), (0.1, 2.2), (0.35, 2.3))]
    plate = ellipse(0, -2.0, 3.0, 0.4, 120)
    return Design("Slice of Cake", [top, front, side, drips, plate] + layers + berry, [], T)


@design("birthday_cake", T)
def birthday_cake(rng):
    tiers = [rect(-2.2, -2.2, 2.2, -0.6), rect(-1.5, -0.6, 1.5, 0.8)]
    drips = [wave(-2.2, 2.2, -0.85, 0.15, 6, 80), wave(-1.5, 1.5, 0.55, 0.12, 4, 60)]
    candles = []
    for x in (-0.9, 0.0, 0.9):
        candles.append(rect(x - 0.15, 0.8, x + 0.15, 1.8))
        candles.append(lens((x, 1.9), (x, 2.5), 0.4))
    hearts = [heart(x, -1.6, 0.3) for x in (-1.2, 0.0, 1.2)]
    plate = ellipse(0, -2.35, 2.9, 0.35, 120)
    return Design("Birthday Cake", tiers + drips + candles + hearts + [plate], [], T)


@design("lollipop", T)
def lollipop(rng):
    swirl = spiral(0, 1.0, 0.0, 1.8, 3.2, 300)
    candy = circle(0, 1.0, 1.9, 140)
    stick = rect(-0.12, -3.2, 0.12, -0.9)
    bow = [lens((0, -1.2), (-0.9, -0.7), 0.4), lens((0, -1.2), (0.9, -0.7), 0.4)]
    return Design("Swirl Lollipop", [candy, swirl, stick] + bow, [], T)


@design("wrapped_candy", T)
def wrapped_candy(rng):
    candy = ellipse(0, 0, 1.4, 0.9, 100)
    ends = [poly((-1.35, 0.3), (-2.8, 1.0), (-2.5, 0.0), (-2.8, -1.0), (-1.35, -0.3), closed=False),
            poly((1.35, 0.3), (2.8, 1.0), (2.5, 0.0), (2.8, -1.0), (1.35, -0.3), closed=False)]
    stripes = [quad((-0.8, -0.7), (-0.5, 0), (-0.8, 0.7)), quad((0, -0.9), (0.3, 0), (0, 0.9)), quad((0.8, -0.7), (1.1, 0), (0.8, 0.7))]
    return Design("Wrapped Candy", [candy] + ends + stripes, [], T)


@design("cookie", T)
def cookie(rng):
    edge = [(r * math.cos(t), r * math.sin(t)) for t, r in [(2 * math.pi * i / 160, 2.0 + 0.08 * math.sin(11 * 2 * math.pi * i / 160)) for i in range(161)]]
    chips = [poly((x - 0.2, y - 0.15), (x + 0.2, y - 0.1), (x + 0.05, y + 0.2)) for x, y in
             [(-0.9, 0.8), (0.4, 1.1), (1.1, 0.1), (-0.3, -0.2), (-1.1, -0.6), (0.5, -1.1), (-0.2, -1.4)]]
    bite = arc(2.0, 1.0, 0.6, math.radians(110), math.radians(250), 20)
    milk = [rect(2.4, -2.6, 3.4, -0.6), ellipse(2.9, -0.6, 0.5, 0.12, 20)]
    return Design("Chocolate Chip Cookie", [edge, bite] + chips + milk, [], T)


@design("macaron", T)
def macaron(rng):
    def mac(cx, cy, s):
        top = rrect(-1.4, 0.2, 1.4, 1.0, 0.4)
        bottom = rrect(-1.4, -1.0, 1.4, -0.2, 0.4)
        filling = wave(-1.3, 1.3, 0.0, 0.08, 6, 60)
        feet = [zigzag(-1.3, 1.3, 0.25, 0.05, 10), zigzag(-1.3, 1.3, -0.25, 0.05, 10)]
        return [transform(p, dx=cx, dy=cy, s=s) for p in [top, bottom, filling] + feet]
    return Design("Macarons", mac(0, 1.4, 1.0) + mac(-1.2, -1.2, 0.8) + mac(1.4, -1.0, 0.7), [], T)


@design("popsicle", T)
def popsicle(rng):
    pop = chain([(-1.0, -1.0), (-1.0, 1.8)], arc(0, 1.8, 1.0, math.pi, 0, 30), [(1.0, -1.0), (-1.0, -1.0)])
    stick = chain([(-0.25, -1.0), (-0.25, -2.6)], arc(0, -2.6, 0.25, math.pi, 2 * math.pi, 10), [(0.25, -1.0)])
    stripes = [quad((-1.0, y), (0, y - 0.25), (1.0, y)) for y in (0.0, 1.0)]
    bite = arc(-0.8, 2.4, 0.4, math.radians(-60), math.radians(120), 12)
    drops = [lens((1.2, -1.2), (1.2, -1.7), 0.4), lens((-1.3, -1.4), (-1.3, -1.9), 0.4)]
    return Design("Fruit Popsicle", [pop, stick, bite] + stripes + drops, [], T)
