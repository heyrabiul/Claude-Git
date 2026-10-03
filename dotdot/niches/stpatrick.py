"""St. Patrick's Day niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "stpatrick"


def _leaf_heart(cx, cy, s, rot):
    return transform(heart(0, 0, 1.0), dx=cx, dy=cy, s=s, rot=rot)


@design("shamrock", T)
def shamrock(rng):
    leaves = [transform([(x, -y) for x, y in heart(0, 0, 1.0)], dx=1.05 * math.cos(a), dy=1.05 * math.sin(a), rot=a - math.pi / 2 + math.pi)
              for a in (math.radians(90), math.radians(210), math.radians(330))]
    veins = [[(0, 0), (0.9 * math.cos(a), 0.9 * math.sin(a))] for a in (math.radians(90), math.radians(210), math.radians(330))]
    stem = quad((0, -0.3), (0.3, -1.8), (1.0, -2.8))
    return Design("Shamrock", leaves + veins + [stem], [], T)


@design("four_leaf_clover", T)
def four_leaf_clover(rng):
    leaves = [transform([(x, -y) for x, y in heart(0, 0, 0.9)], dx=0.95 * math.cos(a), dy=0.95 * math.sin(a), rot=a - math.pi / 2 + math.pi)
              for a in (math.radians(45), math.radians(135), math.radians(225), math.radians(315))]
    stem = quad((0, 0), (-0.4, -2.0), (-1.2, -3.0))
    sparkles = [star(x, y, 0.3, 4, 0.3) for x, y in [(2.2, 2.0), (-2.3, 1.6)]]
    return Design("Lucky Four-Leaf Clover", leaves + [stem] + sparkles, [], T)


@design("leprechaun_hat", T)
def leprechaun_hat(rng):
    crown = poly((-1.4, 0.0), (-1.1, 2.6), (1.1, 2.6), (1.4, 0.0), closed=False)
    top = [(-1.1, 2.6), (1.1, 2.6)]
    brim = ellipse(0, 0, 2.7, 0.55, 140)
    band = [[(-1.35, 0.4), (1.35, 0.4)], [(-1.3, 1.0), (1.3, 1.0)]]
    buckle = [rect(-0.4, 0.3, 0.4, 1.1), rect(-0.18, 0.5, 0.18, 0.9)]
    clover = [transform([(x, -y) for x, y in heart(0, 0, 0.3)], dx=1.7 + 0.32 * math.cos(a), dy=1.6 + 0.32 * math.sin(a), rot=a + math.pi / 2)
              for a in (math.radians(90), math.radians(210), math.radians(330))]
    return Design("Leprechaun Hat", [crown, top, brim] + band + buckle + clover, [], T)


@design("pot_of_gold", T)
def pot_of_gold(rng):
    pot = chain(arc(0, -0.7, 1.8, math.radians(195), math.radians(345), 60), [(-1.74, -0.23)])
    rim = ellipse(0, -0.2, 1.9, 0.35, 100)
    coins = [ellipse(x, y, 0.4, 0.15, 24) for x, y in [(-1.0, 0.1), (-0.3, 0.3), (0.4, 0.15), (1.0, 0.3), (-0.6, 0.6), (0.3, 0.7), (0.0, 1.05)]]
    rainbow = [arc(-0.5, 0.4, r, math.radians(90), math.radians(175), 30) for r in (2.4, 2.8, 3.2)]
    legs = [[(-1.2, -2.0), (-1.4, -2.5)], [(1.2, -2.0), (1.4, -2.5)]]
    return Design("Pot of Gold", [pot, rim] + coins + rainbow + legs, [], T)


@design("rainbow_clouds", T)
def rainbow_clouds(rng):
    bands = [arc(0, -1.2, r, 0, math.pi, 80) for r in (1.6, 2.1, 2.6, 3.1)]
    clouds = []
    for cx in (-2.4, 2.4):
        cl = chain(arc(cx - 0.6, -1.2, 0.5, math.pi, 0, 16), arc(cx, -0.9, 0.6, math.pi, 0, 16), arc(cx + 0.6, -1.2, 0.5, math.pi, 0, 16),
                   [(cx - 1.1, -1.2)])
        clouds.append(cl)
    sun = circle(0, 2.6, 0.5, 40)
    return Design("Rainbow", bands + clouds + [sun], [], T)


@design("horseshoe", T)
def horseshoe(rng):
    outer = arc(0, 0.2, 2.0, math.radians(-50), math.radians(230), 100)
    inner = arc(0, 0.2, 1.3, math.radians(-50), math.radians(230), 80)
    shoe = chain(outer, [inner[-1]], inner[::-1], [outer[0]])
    nails = [circle(1.65 * math.cos(math.radians(a)), 0.2 + 1.65 * math.sin(math.radians(a)), 0.1, 10) for a in (-20, 20, 60, 120, 160, 200)]
    sparkles = [star(0, 0.4, 0.4, 4, 0.3)]
    return Design("Lucky Horseshoe", [shoe] + sparkles, nails, T)


@design("harp", T)
def harp(rng):
    frame = chain(quad((-1.6, -2.6), (-2.0, 0.4), (-1.0, 2.8), 30), cubic((-1.0, 2.8), (0.4, 2.0), (1.0, 3.0), (1.8, 2.6), 30),
                  [(1.4, -2.6), (-1.6, -2.6)])
    strings = [[(-1.6 + 0.4 * k, -2.6), (-1.6 + 0.4 * k, 2.1 + 0.15 * math.sin(k))] for k in range(1, 8)]
    return Design("Celtic Harp", [frame] + strings, [], T)


@design("celtic_knot", T)
def celtic_knot(rng):
    loops = [transform(ellipse(0, 1.0, 0.8, 1.5, 100), rot=a) for a in (0, 2 * math.pi / 3, 4 * math.pi / 3)]
    inner = [transform(ellipse(0, 1.0, 0.45, 1.1, 80), rot=a) for a in (0, 2 * math.pi / 3, 4 * math.pi / 3)]
    ring = circle(0, 0, 1.2, 100)
    return Design("Celtic Knot", loops + inner + [ring], [], T)


@design("gold_coins", T)
def gold_coins(rng):
    coins = [ellipse(0, -1.8 + 0.35 * k, 1.6, 0.45, 80) for k in range(5)]
    face = [circle(1.2, 1.2, 1.2, 80), circle(1.2, 1.2, 0.95, 70), transform([(x, -y) for x, y in heart(0, 0, 0.35)], dx=1.2, dy=1.4, rot=math.pi)]
    shine = [star(x, y, 0.3, 4, 0.3) for x, y in [(-1.6, 1.4), (2.8, 2.6)]]
    return Design("Gold Coins", coins + face + shine, [], T)
