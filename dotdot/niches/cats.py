"""Cats niche."""
import math

from ._kit import *  # noqa: F401,F403  (shared drawing kit)

T = "cats"


def _cat_head(cx, cy, r):
    head = chain(arc(cx, cy, r, math.radians(-30), math.radians(52), 30), [(cx + r * 0.75, cy + r * 1.45)],
                 arc(cx, cy, r, math.radians(80), math.radians(100), 8), [(cx - r * 0.75, cy + r * 1.45)],
                 arc(cx, cy, r, math.radians(128), math.radians(210), 30),
                 quad((cx - r * 0.87, cy - r * 0.5), (cx, cy - r * 1.15), (cx + r * 0.87, cy - r * 0.5), 20))
    nose = poly((cx - 0.12 * r, cy - 0.15 * r), (cx + 0.12 * r, cy - 0.15 * r), (cx, cy - 0.3 * r))
    mouth = chain(quad((cx - 0.3 * r, cy - 0.5 * r), (cx - 0.1 * r, cy - 0.55 * r), (cx, cy - 0.3 * r)),
                  quad((cx, cy - 0.3 * r), (cx + 0.1 * r, cy - 0.55 * r), (cx + 0.3 * r, cy - 0.5 * r)))
    wh = []
    for dy in (-0.25, -0.4):
        wh.append([(cx + 0.35 * r, cy + dy * r), (cx + 1.25 * r, cy + (dy - 0.05) * r)])
        wh.append([(cx - 0.35 * r, cy + dy * r), (cx - 1.25 * r, cy + (dy - 0.05) * r)])
    return [head, nose, mouth] + wh


@design("sitting_cat", T)
def sitting_cat(rng):
    head = _cat_head(0, 2.0, 0.9)
    body = chain(cubic((-0.55, 1.3), (-1.6, 0.4), (-1.7, -1.6), (-0.9, -2.2), 40),
                 [(0.9, -2.2)], cubic((0.9, -2.2), (1.7, -1.6), (1.6, 0.4), (0.55, 1.3), 40))
    legs = [[(-0.35, 0.6), (-0.4, -2.2)], [(0.35, 0.6), (0.4, -2.2)]]
    paws = [arc(-0.6, -2.2, 0.22, 0, math.pi, 10), arc(0.6, -2.2, 0.22, 0, math.pi, 10)]
    tail = tube(chain(quad((1.3, -1.9), (2.6, -1.8), (2.4, -0.4)), quad((2.4, -0.4), (2.3, 0.4), (2.8, 0.7))), 0.3)
    hints = [eye(-0.3, 2.2, 0.13), eye(0.3, 2.2, 0.13)]
    return Design("Sitting Cat", head + [body, tail] + legs + paws, hints, T)


@design("sleeping_cat", T)
def sleeping_cat(rng):
    body = ellipse(0.4, -0.2, 2.2, 1.3, 160)
    head = circle(-1.6, -0.5, 0.85, 80)
    ears = [poly((-2.3, 0.0), (-2.4, 0.75), (-1.85, 0.25), closed=False), poly((-1.4, 0.3), (-1.0, 0.9), (-0.95, 0.15), closed=False)]
    lids = [arc(-1.95, -0.45, 0.2, math.radians(200), math.radians(340), 10), arc(-1.35, -0.45, 0.2, math.radians(200), math.radians(340), 10)]
    tail = tube(cubic((2.5, -0.6), (2.6, -1.9), (0.0, -2.0), (-1.4, -1.6), 50), lambda t: 0.4 - 0.15 * t)
    zz = [[(0.0, 1.6), (0.5, 1.6), (0.0, 1.1), (0.5, 1.1)], [(0.8, 2.4), (1.4, 2.4), (0.8, 1.8), (1.4, 1.8)]]
    cushion = rrect(-3.0, -2.6, 3.2, -1.7, 0.4)
    return Design("Sleeping Cat", [body, head, tail, cushion] + ears + lids + zz, [eye(-1.65, -0.8, 0.07)], T)


@design("kitten_box", T)
def kitten_box(rng):
    box = rect(-2.0, -2.2, 2.0, 0.2)
    flaps = [poly((-2.0, 0.2), (-2.7, 0.9), (-1.2, 0.9), (-0.9, 0.2), closed=False),
             poly((2.0, 0.2), (2.7, 0.9), (1.2, 0.9), (0.9, 0.2), closed=False)]
    head = _cat_head(0, 1.0, 0.85)
    paws = [ellipse(-0.6, 0.25, 0.3, 0.2, 24), ellipse(0.6, 0.25, 0.3, 0.2, 24)]
    tape = [[(-2.0, -0.6), (2.0, -0.6)], [(0, 0.2), (0, -2.2)]]
    return Design("Kitten in a Box", [box] + flaps + head + paws + tape,
                  [eye(-0.28, 1.2, 0.13), eye(0.28, 1.2, 0.13)], T)


@design("yarn_ball", T)
def yarn_ball(rng):
    ball = circle(0, 0, 1.8, 160)
    wraps = [arc(-0.6, 0.2, 1.6, math.radians(-50), math.radians(70), 30),
             arc(0.8, -0.4, 1.5, math.radians(100), math.radians(220), 30),
             arc(0.1, 1.2, 1.4, math.radians(200), math.radians(330), 30),
             arc(-0.4, -1.1, 1.3, math.radians(10), math.radians(150), 30)]
    strand = cubic((1.6, -0.8), (2.8, -1.6), (2.4, -2.6), (3.4, -2.8), 40)
    needles = [[(-2.4, 2.4), (0.8, -0.3)], [(2.2, 2.6), (-0.6, -0.2)]]
    knobs = [circle(-2.5, 2.5, 0.15, 14), circle(2.3, 2.7, 0.15, 14)]
    return Design("Ball of Yarn", [ball, strand] + wraps + needles + knobs, [], T)


@design("fishbowl", T)
def fishbowl(rng):
    bowl = chain(arc(0, 0, 2.0, math.radians(60), math.radians(480), 160))
    rim = ellipse(0, 1.75, 1.0, 0.18, 50)
    water = [(x, 0.9 + 0.08 * math.sin(4 * x)) for x in [-1.75 + 3.5 * i / 60 for i in range(61)]]
    fish = chain(quad((-0.7, -0.2), (0.0, 0.35), (0.5, -0.2)), [(0.9, 0.15), (0.9, -0.55), (0.5, -0.2)],
                 quad((0.5, -0.2), (0.0, -0.75), (-0.7, -0.2)))
    pebbles = [ellipse(x, -1.75, 0.25, 0.12, 20) for x in (-0.8, -0.3, 0.25, 0.8)]
    plant = [quad((-1.2, -1.6), (-1.5, -0.8), (-1.1, 0.0)), quad((-1.1, -1.6), (-0.8, -1.0), (-1.0, -0.4))]
    return Design("Goldfish Bowl", [bowl, rim, water, fish] + pebbles + plant, [eye(-0.45, -0.1, 0.07)], T)


@design("toy_mouse", T)
def toy_mouse(rng):
    body = chain(cubic((-1.8, -0.2), (-1.4, 1.2), (1.0, 1.2), (1.6, -0.6), 50), [(-1.8, -0.2)])
    ear = circle(-0.6, 1.05, 0.45, 40)
    tail = cubic((1.6, -0.6), (2.6, -0.6), (2.2, 0.8), (3.2, 1.0), 40)
    nose = circle(-1.85, -0.15, 0.1, 12)
    whisk = [[(-1.7, -0.1), (-2.5, 0.2)], [(-1.7, -0.2), (-2.5, -0.5)]]
    stitches = [[(x, 0.2), (x + 0.2, -0.2)] for x in (-0.4, 0.1, 0.6)]
    return Design("Toy Mouse", [body, ear, tail, nose] + whisk + stitches, [eye(-1.3, 0.25, 0.09)], T)


@design("cat_paw", T)
def cat_paw(rng):
    pad = chain(cubic((0, -1.6), (-1.6, -1.6), (-1.6, 0.2), (0, 0.0), 40), cubic((0, 0.0), (1.6, 0.2), (1.6, -1.6), (0, -1.6), 40))
    toes = [ellipse(x, y, 0.45, 0.6, 50, rot=r) for x, y, r in [(-1.5, 0.9, 0.35), (-0.5, 1.5, 0.1), (0.5, 1.5, -0.1), (1.5, 0.9, -0.35)]]
    hearts = [transform(lens((0, 0), (0, 0.6), 0.5), dx=x, dy=y) for x, y in [(-2.5, -1.8), (2.4, 2.2)]]
    return Design("Cat Paw Print", [pad] + toes + hearts, [], T)


@design("fish_bone", T)
def fish_bone(rng):
    spine = [(-2.0, 0), (2.0, 0)]
    head = poly((-2.0, 0.0), (-2.9, 0.7), (-2.9, -0.7))
    ribs = [quad((x, 0), (x + 0.2, 0.6), (x - 0.1, 0.95)) for x in (-1.4, -0.7, 0.0, 0.7, 1.4)] + \
           [quad((x, 0), (x + 0.2, -0.6), (x - 0.1, -0.95)) for x in (-1.4, -0.7, 0.0, 0.7, 1.4)]
    tail = poly((2.0, 0.0), (2.8, 0.7), (2.6, 0.0), (2.8, -0.7))
    return Design("Fish Bone", [spine, head, tail] + ribs, [eye(-2.55, 0.15, 0.1)], T)


@design("cat_bowl", T)
def cat_bowl(rng):
    rim = ellipse(0, 0, 2.3, 0.45, 140)
    inner = ellipse(0, 0.02, 1.9, 0.3, 120)
    side = chain([(-2.3, 0)], quad((-2.1, -1.3), (0, -1.5), (2.1, -1.3), 40), [(2.3, 0)])
    food = [circle(x, y, 0.16, 14) for x, y in [(-1.0, 0.15), (-0.5, 0.25), (0.0, 0.2), (0.5, 0.25), (1.0, 0.15), (-0.25, 0.4), (0.3, 0.42)]]
    paw = [circle(0, -0.85, 0.22, 20)] + [circle(x, -0.45, 0.1, 12) for x in (-0.3, -0.1, 0.1, 0.3)]
    return Design("Cat Food Bowl", [rim, inner, side] + food + paw, [], T)
