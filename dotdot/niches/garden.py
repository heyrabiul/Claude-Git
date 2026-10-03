"""Flowers & Garden niche."""
import math

from ._kit import *  # noqa: F401,F403  (shared drawing kit)

T = "garden"


@design("tulip", T)
def tulip(rng):
    bloom = chain(cubic((-1.0, 1.0), (-1.4, 2.4), (-0.8, 3.2), (-0.6, 3.4), 30), [(-0.25, 2.6), (0, 3.4), (0.25, 2.6), (0.6, 3.4)],
                  cubic((0.6, 3.4), (0.8, 3.2), (1.4, 2.4), (1.0, 1.0), 30), quad((1.0, 1.0), (0, 0.5), (-1.0, 1.0), 20))
    stem = cubic((0, 0.7), (0.1, -0.8), (-0.1, -2.0), (0, -3.2), 40)
    leaves = [lens((0, -2.6), (-1.6, -0.4), 0.3), lens((0, -2.2), (1.4, -0.8), 0.3)]
    ground = [(-2.0, -3.2), (2.0, -3.2)]
    return Design("Tulip", [bloom, stem, ground] + leaves, [], T)


@design("rose", T)
def rose(rng):
    swirl = spiral(0, 1.4, 0.15, 1.3, 2.4, 200)
    petals = [arc(-0.6, 1.0, 1.0, math.radians(120), math.radians(260), 30),
              arc(0.6, 1.0, 1.0, math.radians(-80), math.radians(60), 30),
              arc(0, 0.8, 1.6, math.radians(200), math.radians(340), 40)]
    stem = cubic((0, -0.6), (0.2, -1.6), (-0.2, -2.6), (0, -3.6), 40)
    thorns = [poly((0.05, -1.4), (0.4, -1.5), (0.06, -1.65), closed=False), poly((-0.05, -2.4), (-0.4, -2.5), (-0.06, -2.65), closed=False)]
    leaves = [lens((0, -2.0), (1.4, -1.4), 0.32), lens((0, -2.9), (-1.4, -2.4), 0.32)]
    return Design("Rose", [swirl, stem] + petals + thorns + leaves, [], T)


@design("daisy_pot", T)
def daisy_pot(rng):
    pot = poly((-1.4, -1.0), (1.4, -1.0), (1.1, -3.0), (-1.1, -3.0))
    rim = rect(-1.6, -1.0, 1.6, -0.5)
    flowers = []
    for cx, cy, s in [(0, 2.2, 1.0), (-1.4, 1.2, 0.8), (1.4, 1.3, 0.8)]:
        flowers.append(circle(cx, cy, 0.3 * s, 24))
        for k in range(10):
            a = k * 2 * math.pi / 10
            flowers.append(lens((cx + 0.32 * s * math.cos(a), cy + 0.32 * s * math.sin(a)),
                                (cx + 0.95 * s * math.cos(a), cy + 0.95 * s * math.sin(a)), 0.28))
        flowers.append([(cx, cy - 0.32 * s), (cx * 0.3, -0.5)])
    return Design("Potted Daisies", [pot, rim] + flowers, [], T)


@design("watering_can", T)
def watering_can(rng):
    body = rrect(-1.6, -1.6, 1.4, 0.8, 0.3)
    spout = poly((1.4, -0.6), (3.0, 1.2), (3.2, 1.0), (1.4, -1.0), closed=False)
    rose_ = ellipse(3.2, 1.25, 0.25, 0.45, 30, rot=-0.7)
    handle = arc(-0.1, 0.8, 1.1, 0, math.pi, 40)
    drops = [lens((3.6 + 0.3 * k, 0.4 - 0.5 * k), (3.6 + 0.3 * k, 0.0 - 0.5 * k), 0.4) for k in range(3)]
    band = [(-1.6, -0.8), (1.4, -0.8)]
    return Design("Watering Can", [body, spout, rose_, handle, band] + drops, [], T)


@design("wheelbarrow", T)
def wheelbarrow(rng):
    tray = poly((-2.4, 0.6), (1.4, 0.6), (0.9, -0.8), (-1.6, -0.8))
    wheel = circle(1.6, -1.4, 0.7, 60)
    hub = circle(1.6, -1.4, 0.15, 14)
    frame = [[(-1.6, -0.8), (1.6, -1.4)], [(-2.4, 0.6), (-3.4, 1.0)], [(-1.4, -0.8), (-1.6, -2.0)]]
    plants = [arc(-1.0, 0.6, 0.6, 0, math.pi, 20), arc(0.2, 0.6, 0.7, 0, math.pi, 20), lens((-0.4, 1.0), (-0.2, 2.0), 0.3)]
    return Design("Wheelbarrow", [tray, wheel, hub] + frame + plants, [], T)


@design("gnome", T)
def gnome(rng):
    hat = poly((-1.1, 1.0), (0.3, 3.8), (1.1, 1.0))
    face = circle(0, 0.75, 0.55, 40)
    beard = chain(cubic((-0.95, 0.9), (-1.2, -0.8), (-0.3, -1.5), (0, -1.6), 30), cubic((0, -1.6), (0.3, -1.5), (1.2, -0.8), (0.95, 0.9), 30))
    nose = circle(0, 0.6, 0.22, 20)
    body = poly((-1.0, -0.4), (-1.4, -2.4), (1.4, -2.4), (1.0, -0.4), closed=False)
    boots = [ellipse(-0.7, -2.6, 0.55, 0.25, 30), ellipse(0.7, -2.6, 0.55, 0.25, 30)]
    mushroom = [chain(arc(2.4, -1.6, 0.7, 0, math.pi, 30), [(3.1, -1.6)]), rect(2.25, -2.7, 2.55, -1.6)]
    return Design("Garden Gnome", [hat, face, beard, nose, body] + boots + mushroom, [eye(-0.25, 0.95, 0.07), eye(0.25, 0.95, 0.07)], T)


@design("birdbath", T)
def birdbath(rng):
    bowl = chain([(-2.2, 0.6)], quad((-1.6, -0.4), (0, -0.5), (1.6, -0.4), 30), [(2.2, 0.6), (-2.2, 0.6)])
    water = ellipse(0, 0.6, 2.2, 0.3, 80)
    pedestal = poly((-0.3, -0.45), (-0.5, -2.4), (0.5, -2.4), (0.3, -0.45), closed=False)
    base = rect(-1.2, -2.8, 1.2, -2.4)
    bird = chain(cubic((-1.4, 0.7), (-1.4, 1.6), (-0.4, 1.7), (-0.2, 1.2), 20), quad((-0.2, 1.2), (-0.6, 0.7), (-1.4, 0.7), 12))
    beak = poly((-0.2, 1.4), (0.2, 1.35), (-0.18, 1.25), closed=False)
    return Design("Bird Bath", [bowl, water, pedestal, base, bird, beak], [eye(-0.45, 1.4, 0.06)], T)


@design("garden_tools", T)
def garden_tools(rng):
    shovel = [rect(-1.15, -0.2, -0.85, 3.0), chain(quad((-1.6, -0.2), (-1.0, -2.6), (-0.4, -0.2), 30), [(-1.6, -0.2)]),
              rrect(-1.4, 3.0, -0.6, 3.5, 0.2)]
    rake = [rect(0.85, -1.4, 1.15, 3.2), rect(0.0, -1.6, 2.0, -1.4)] + [[(0.1 + 0.3 * k, -1.6), (0.1 + 0.3 * k, -2.3)] for k in range(7)]
    gloves = [rrect(-2.8, -2.6, -1.9, -1.2, 0.4), lens((-1.9, -1.6), (-1.5, -1.0), 0.3)]
    return Design("Garden Tools", shovel + rake + gloves, [], T)
