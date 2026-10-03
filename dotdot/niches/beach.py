"""Summer Beach niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "beach"


@design("beach_umbrella", T)
def beach_umbrella(rng):
    scallops = chain(*[arc(-2.04 + 1.02 * k, 1.05, 0.51, math.pi, 2 * math.pi, 12) for k in range(5)])
    canopy = chain(arc(0, 0.6, 2.6, math.radians(10), math.radians(170), 80), scallops)
    ribs = [quad((0, 3.2), (x * 0.6, 2.0), (x, 1.05)) for x in (-1.53, -0.51, 0.51, 1.53)]
    pole = [(0.2, 3.2), (0.6, -2.4)]
    sand = [wave(-3.2, 3.2, -2.4, 0.1, 4, 80)]
    chair = [poly((-2.8, -2.4), (-2.0, -1.0), (-1.2, -2.4), closed=False), [(-2.6, -1.8), (-1.2, -1.8)]]
    return Design("Beach Umbrella", [canopy, pole] + ribs + sand + chair, [], T)


@design("sandcastle", T)
def sandcastle(rng):
    base = rect(-2.4, -2.4, 2.4, -0.8)
    towers = [poly((x - 0.6, -0.8), (x - 0.6, 0.8), (x - 0.3, 0.8), (x - 0.3, 1.1), (x, 1.1), (x, 0.8), (x + 0.3, 0.8), (x + 0.3, 1.1),
                   (x + 0.6, 1.1), (x + 0.6, -0.8), closed=False) for x in (-1.6, 1.6)]
    keep = poly((-0.7, -0.8), (-0.7, 1.6), (0.7, 1.6), (0.7, -0.8), closed=False)
    door = chain([(-0.35, -2.4), (-0.35, -1.6)], arc(0, -1.6, 0.35, math.pi, 0, 12), [(0.35, -2.4)])
    flag = [[(0, 1.6), (0, 2.6)], poly((0, 2.6), (0.7, 2.35), (0, 2.1))]
    bucket = [poly((2.6, -2.4), (2.8, -1.4), (3.5, -1.4), (3.7, -2.4)), arc(3.15, -1.4, 0.45, 0, math.pi, 12)]
    shell = [arc(-3.0, -2.4, 0.35, 0, math.pi, 12)]
    return Design("Sandcastle", [base, keep, door] + towers + flag + bucket + shell, [], T)


@design("flip_flops", T)
def flip_flops(rng):
    def sandal(cx, rot):
        sole = chain(cubic((0, 2.0), (0.9, 2.0), (1.0, 0.0), (0.7, -1.4), 30), cubic((0.7, -1.4), (0.5, -2.2), (-0.5, -2.2), (-0.7, -1.4), 30),
                     cubic((-0.7, -1.4), (-1.0, 0.0), (-0.9, 2.0), (0, 2.0), 30))
        strap = [quad((0, 1.4), (-0.6, 0.6), (-0.8, 0.0)), quad((0, 1.4), (0.6, 0.6), (0.8, 0.0))]
        flower = circle(0, 1.4, 0.18, 14)
        return [transform(p, dx=cx, rot=rot) for p in [sole, flower] + strap]
    return Design("Flip-Flops", sandal(-1.1, 0.15) + sandal(1.1, -0.15), [], T)


@design("beach_ball", T)
def beach_ball(rng):
    ball = circle(0, 0, 2.1, 160)
    panels = [arc(-2.6, 0, 2.6, math.radians(-50), math.radians(50), 30), arc(2.6, 0, 2.6, math.radians(130), math.radians(230), 30),
              arc(0, 3.2, 2.6, math.radians(235), math.radians(305), 30), arc(0, -3.2, 2.6, math.radians(55), math.radians(125), 30)]
    cap = circle(0, 0, 0.35, 30)
    shine = arc(-0.6, 0.6, 1.0, math.radians(110), math.radians(160), 12)
    return Design("Beach Ball", [ball, cap, shine] + panels, [], T)


@design("palm_tree", T)
def palm_tree(rng):
    trunk = chain(cubic((-0.4, -2.6), (-0.2, -0.6), (0.2, 0.8), (0.6, 1.6), 40))
    trunk2 = chain(cubic((0.3, -2.6), (0.4, -0.6), (0.7, 0.8), (1.0, 1.6), 40))
    rings = [quad((-0.35 + 0.08 * k, -2.0 + 0.6 * k), (0.0 + 0.08 * k, -2.15 + 0.6 * k), (0.35 + 0.08 * k, -2.0 + 0.6 * k)) for k in range(5)]
    fronds = [lens((0.8, 1.6), (0.8 + 2.4 * math.cos(a), 1.6 + 1.2 * math.sin(a) - 0.6 * abs(math.cos(a))), 0.18)
              for a in (math.radians(d) for d in (10, 50, 95, 140, 175))]
    coconuts = [circle(0.6, 1.3, 0.25, 20), circle(1.05, 1.25, 0.25, 20)]
    island = [arc(0, -3.4, 2.4, math.radians(25), math.radians(155), 40), wave(-3.2, 3.2, -2.6, 0.1, 5, 80)]
    return Design("Palm Tree", [trunk, trunk2] + rings + fronds + coconuts + island, [], T)


@design("sunglasses", T)
def sunglasses(rng):
    lenses = [rrect(-2.8, -0.9, -0.4, 0.8, 0.6), rrect(0.4, -0.9, 2.8, 0.8, 0.6)]
    bridge = arc(0, 0.4, 0.45, math.radians(30), math.radians(150), 12)
    arms = [[(-2.8, 0.5), (-3.5, 0.9)], [(2.8, 0.5), (3.5, 0.9)]]
    shine = [[(-2.2, 0.4), (-1.6, -0.3)], [(1.0, 0.4), (1.6, -0.3)]]
    sun = [circle(0, 2.6, 0.5, 40)] + [[(0.7 * math.cos(a), 2.6 + 0.7 * math.sin(a)), (1.1 * math.cos(a), 2.6 + 1.1 * math.sin(a))]
                                       for a in [k * math.pi / 4 for k in range(8)]]
    return Design("Sunglasses", lenses + [bridge] + arms + shine + sun, [], T)


@design("surfboard", T)
def surfboard(rng):
    board = transform(chain(cubic((0, 3.2), (1.2, 2.4), (1.0, -2.0), (0, -3.0), 50), cubic((0, -3.0), (-1.0, -2.0), (-1.2, 2.4), (0, 3.2), 50)), rot=-0.35)
    stripe = transform([(0, 2.8), (0, -2.7)], rot=-0.35)
    fin = transform(poly((0, -2.0), (0.5, -2.6), (0, -2.6)), rot=-0.35)
    waves_ = [quad((-3.0, -2.2 + 0.5 * k), (-2.0, -1.6 + 0.5 * k), (-1.4, -2.2 + 0.5 * k)) for k in range(2)]
    hibiscus = [circle(0.2, 0.6, 0.15, 12)] + [transform(lens((0, 0), (0.6, 0), 0.4), dx=0.2, dy=0.6, rot=k * 2 * math.pi / 5) for k in range(5)]
    return Design("Surfboard", [board, stripe, fin] + waves_ + hibiscus, [], T)


@design("bucket_spade", T)
def bucket_spade(rng):
    bucket = poly((-1.8, 0.6), (1.8, 0.6), (1.4, -2.2), (-1.4, -2.2))
    rim = ellipse(0, 0.6, 1.8, 0.3, 80)
    handle = arc(0, 0.6, 1.6, math.radians(15), math.radians(165), 40)
    band = [quad((-1.65, -0.4), (0, -0.6), (1.65, -0.4))]
    star_ = star(0, -1.3, 0.4)
    spade = [[(2.2, 3.0), (2.0, -0.4)], chain(quad((1.6, -0.4), (2.0, -1.8), (2.4, -0.4)), [(1.6, -0.4)]), rect(1.95, 3.0, 2.45, 3.2)]
    return Design("Bucket and Spade", [bucket, rim, handle, star_] + band + spade, [], T)


@design("sand_dollar", T)
def sand_dollar(rng):
    disc = circle(0, 0, 2.2, 160)
    rim = circle(0, 0, 1.95, 140)
    petals = [lens((0.25 * math.cos(a), 0.25 * math.sin(a)), (1.45 * math.cos(a), 1.45 * math.sin(a)), 0.22)
              for a in [math.pi / 2 + k * 2 * math.pi / 5 for k in range(5)]]
    slots = [lens((1.55 * math.cos(a) * 0.9, 1.55 * math.sin(a) * 0.9), (1.75 * math.cos(a), 1.75 * math.sin(a)), 0.3)
             for a in [math.pi / 2 + math.pi / 5 + k * 2 * math.pi / 5 for k in range(5)]]
    centre = circle(0, 0, 0.18, 14)
    sand = [wave(-3.0, 3.0, -2.6, 0.1, 4, 80)]
    return Design("Sand Dollar", [disc, rim, centre] + petals + slots + sand, [], T)
