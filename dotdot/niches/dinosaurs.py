"""Dinosaurs niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "dinosaurs"


@design("trex", T)
def trex(rng):
    body = chain([(-0.2, 3.0)], cubic((1.4, 3.2), (2.2, 2.6), (2.0, 2.0), (1.2, 1.8), 30), [(1.6, 1.4), (0.8, 1.4)],
                 cubic((0.6, 0.6), (0.9, 0.0), (0.6, -0.6), (0.4, -0.8), 20), [(0.6, -2.4), (1.2, -2.6), (0.1, -2.6), (-0.2, -1.2)],
                 [(-0.6, -1.4), (-0.8, -2.6), (-1.4, -2.6), (-1.0, -1.0)],
                 quad((-1.0, -1.0), (-2.6, -0.8), (-3.6, -1.6), 20), quad((-3.6, -1.6), (-2.2, 0.4), (-0.8, 1.6), 30),
                 quad((-0.8, 1.6), (-0.8, 2.6), (-0.2, 3.0), 12))
    arm = poly((0.5, 0.6), (1.2, 0.2), (1.25, -0.1), closed=False)
    teeth = zigzag(0.9, 1.7, 1.55, 0.08, 4)
    plates = [arc(-1.2 - 0.6 * k, 0.9 - 0.45 * k, 0.2, 0, math.pi, 8) for k in range(3)]
    return Design("T-Rex", [body, arm, teeth] + plates, [eye(0.7, 2.6, 0.12)], T)


@design("stegosaurus", T)
def stegosaurus(rng):
    body = chain(cubic((-3.4, -0.6), (-2.0, 1.2), (1.6, 1.4), (2.4, 0.0), 50), quad((2.4, 0.0), (2.9, 0.1), (3.2, -0.2), 12),
                 quad((3.2, -0.2), (2.8, -0.6), (2.2, -0.5), 12), quad((2.2, -0.5), (0, -1.2), (-3.4, -0.6), 40))
    plates = [poly((x - 0.35, y), (x, y + 0.9 - abs(x) * 0.1), (x + 0.35, y), closed=False)
              for x, y in [(-1.9, 0.55), (-1.1, 0.95), (-0.3, 1.1), (0.5, 1.05), (1.3, 0.8)]]
    spikes = [poly((-3.0, -0.35), (-3.6, 0.3), (-2.7, -0.2), closed=False), poly((-3.2, -0.5), (-3.9, -0.1), (-3.0, -0.55), closed=False)]
    legs = [leg(x, x + 0.5, -0.50, -2.0) for x in (-1.6, -0.9, 0.6, 1.3)]
    return Design("Stegosaurus", [body] + plates + spikes + legs, [eye(2.75, -0.05, 0.07)], T)


@design("brontosaurus", T)
def brontosaurus(rng):
    body = ellipse(-0.4, -0.6, 2.0, 1.1, 120)
    neck = tube(cubic((1.2, -0.2), (2.2, 1.0), (2.2, 2.4), (2.8, 3.0), 40), lambda t: 0.8 - 0.35 * t, cap=False)
    head = ellipse(3.0, 3.1, 0.55, 0.32, 30, rot=0.2)
    tail = tube(cubic((-2.2, -0.5), (-3.2, -0.6), (-3.6, -0.2), (-4.0, 0.4), 30), lambda t: 0.6 * (1 - t) + 0.05, cap=False)
    legs = [leg(x, x + 0.55, -1.05, -2.6) for x in (-1.9, -1.1, 0.3, 1.0)]
    palms = [[(-4.0, -2.6), (-4.0, -0.8)], lens((-4.0, -0.8), (-4.8, -0.4), 0.3), lens((-4.0, -0.8), (-3.2, -0.4), 0.3)]
    return Design("Brontosaurus", [body, neck, head, tail] + legs + palms, [eye(3.2, 3.2, 0.06)], T)


@design("triceratops", T)
def triceratops(rng):
    body = ellipse(0.6, -0.3, 2.0, 1.2, 140)
    frill = chain(arc(-1.6, 0.6, 1.3, math.radians(-30), math.radians(150), 40))
    head = chain(quad((-0.6, 0.6), (-2.2, 0.8), (-3.2, -0.2), 20), quad((-3.2, -0.2), (-2.4, -0.8), (-1.0, -0.6), 20))
    horns = [poly((-2.0, 0.6), (-2.6, 1.8), (-1.6, 0.8), closed=False), poly((-1.4, 0.7), (-1.6, 1.9), (-1.0, 0.9), closed=False),
             poly((-2.9, 0.0), (-3.4, 0.6), (-2.75, 0.2), closed=False)]
    legs = [leg(x, x + 0.55, -0.85, -2.4) for x in (-0.6, 0.2, 1.3, 2.0)]
    tail = quad((2.5, 0.0), (3.3, -0.4), (3.6, -1.0))
    return Design("Triceratops", [body, frill, head, tail] + horns + legs, [eye(-2.0, 0.15, 0.08)], T)


@design("pterodactyl", T)
def pterodactyl(rng):
    right = [(0.3, 0.2), (1.6, 1.2), (3.6, 1.6), (2.6, 0.6), (2.2, -0.2), (1.0, -0.1), (0.3, -0.3)]
    wings = chain(mirror_x(right)[::-1], right, [(-0.3, 0.2)])
    head = chain(poly((-0.3, 0.2), (-0.4, 1.0), (0.0, 1.2), (1.6, 1.0), (0.3, 0.75), closed=False))
    crest = poly((-0.3, 1.1), (-1.2, 1.6), (-0.2, 1.2), closed=False)
    body = ellipse(0, -0.3, 0.35, 0.6, 30)
    mountains = [poly((-3.6, -2.6), (-2.2, -0.8), (-1.0, -2.6), (0.4, -1.2), (1.8, -2.6), closed=False)]
    return Design("Pterodactyl", [wings, head, crest, body] + mountains, [eye(0.1, 1.0, 0.06)], T)


@design("dino_egg", T)
def dino_egg(rng):
    egg = chain(cubic((0, 2.6), (1.8, 2.6), (2.0, -1.2), (0, -1.6), 40), cubic((0, -1.6), (-2.0, -1.2), (-1.8, 2.6), (0, 2.6), 40))
    crack = poly((-1.7, 0.4), (-1.0, 0.9), (-0.5, 0.3), (0.1, 0.9), (0.6, 0.3), (1.2, 0.9), (1.75, 0.4), closed=False)
    baby = [chain(arc(0, 1.6, 0.8, math.radians(10), math.radians(170), 30)), circle(0.4, 2.1, 0.12, 12)]
    spots = [circle(x, y, r, 20) for x, y, r in [(-0.8, -0.4, 0.3), (0.6, -0.8, 0.25), (0.9, 0.0, 0.2)]]
    nest = [quad((-2.4, -1.4), (0, -2.8), (2.4, -1.4)), quad((-2.2, -1.8), (0, -2.4), (2.2, -1.8))]
    return Design("Dinosaur Egg", [egg, crack] + baby + spots + nest, [], T)


@design("volcano", T)
def volcano(rng):
    mount = poly((-3.2, -2.4), (-0.8, 1.2), (0.8, 1.2), (3.2, -2.4), closed=False)
    crater = [(-0.8, 1.2), (-0.4, 1.0), (0.0, 1.25), (0.4, 1.0), (0.8, 1.2)]
    lava = [quad((-0.4, 1.0), (-1.0, 0.0), (-0.8, -1.2)), quad((0.4, 1.0), (1.2, -0.2), (1.0, -1.0))]
    smoke = [circle(0, 2.0, 0.5, 40), circle(-0.6, 2.7, 0.6, 40), circle(0.5, 3.3, 0.7, 40)]
    rocks = [poly((x - 0.2, y), (x, y + 0.25), (x + 0.2, y)) for x, y in [(-2.0, 2.4), (1.8, 2.2), (2.4, 3.0)]]
    return Design("Erupting Volcano", [mount, crater] + lava + smoke + rocks, [], T)


@design("dino_footprint", T)
def dino_footprint(rng):
    def foot(cx, cy, s, r):
        toes = [tube([(0.25 * math.cos(a), 0.25 * math.sin(a)), (1.5 * math.cos(a), 1.5 * math.sin(a))], lambda t: 0.5 * (1 - t) + 0.05)
                for a in (math.radians(50), math.radians(90), math.radians(130))]
        pad = ellipse(0, -0.3, 0.6, 0.5, 30)
        return [transform(p, dx=cx, dy=cy, s=s, rot=r) for p in toes + [pad]]
    fern = [[(2.4, -2.6), (2.0, 1.0)]] + [lens((2.4 - 0.11 * k * 3, -2.0 + 0.9 * k), (2.9 - 0.1 * k * 3, -1.6 + 0.9 * k), 0.3) for k in range(4)] + \
           [lens((2.4 - 0.11 * k * 3, -2.0 + 0.9 * k), (1.9 - 0.1 * k * 3, -1.6 + 0.9 * k), 0.3) for k in range(4)]
    return Design("Dinosaur Tracks", foot(-1.2, -1.4, 1.0, 0.2) + foot(0.2, 1.4, 1.0, -0.15) + fern, [], T)


@design("dino_skull", T)
def dino_skull(rng):
    skull = chain(cubic((-2.8, 0.0), (-2.4, 1.6), (1.0, 2.2), (2.4, 0.8), 40), quad((2.4, 0.8), (2.6, 0.0), (1.8, -0.4), 15),
                  [(-2.8, -0.2)])
    jaw = chain(quad((-2.6, -0.5), (-0.4, -1.6), (1.6, -0.8), 30), [(1.6, -0.6)])
    teeth = zigzag(-2.4, 0.6, -0.35, 0.15, 9)
    holes = [ellipse(0.6, 0.8, 0.5, 0.4, 30), ellipse(-1.8, 0.5, 0.35, 0.22, 24), ellipse(1.6, 0.6, 0.3, 0.25, 20)]
    ground = [(-3.2, -2.0), (3.2, -2.0)]
    bones = [rrect(-2.4, -1.85, -1.0, -1.6, 0.12), rrect(0.6, -1.85, 2.2, -1.6, 0.12)]
    return Design("Fossil Skull", [skull, jaw, teeth, ground] + holes + bones, [], T)
