"""Winter Wonderland niche (snow and cold, not Christmas)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "winter"


@design("snow_crystal", T)
def snow_crystal(rng):
    out = []
    for k in range(6):
        a = k * math.pi / 3
        ca, sa = math.cos(a), math.sin(a)
        out.append([(0, 0), (2.4 * ca, 2.4 * sa)])
        for d, L in ((0.9, 0.6), (1.6, 0.45)):
            px, py = d * ca, d * sa
            for s in (-1, 1):
                b = a + s * math.pi / 4
                out.append([(px, py), (px + L * math.cos(b), py + L * math.sin(b))])
        out.append(circle(2.55 * ca, 2.55 * sa, 0.15, 12))
    out.append(poly(*[(0.5 * math.cos(k * math.pi / 3), 0.5 * math.sin(k * math.pi / 3)) for k in range(6)]))
    return Design("Ice Crystal", out, [], T)


@design("snow_globe", T)
def snow_globe(rng):
    globe = arc(0, 0.6, 2.2, math.radians(-60), math.radians(240), 120)
    base = poly((-1.6, -1.3), (-2.0, -2.4), (2.0, -2.4), (1.6, -1.3))
    houses = [poly((-1.2, -1.2), (-1.2, -0.2), (-0.7, 0.4), (-0.2, -0.2), (-0.2, -1.2), closed=False),
              poly((0.2, -1.2), (0.2, 0.0), (0.8, 0.7), (1.4, 0.0), (1.4, -1.2), closed=False)]
    tree = poly((-1.7, -1.2), (-1.4, -0.4), (-1.6, -0.4), (-1.3, 0.3), (-1.0, -1.2), closed=False)
    flakes = [star(x, y, 0.15, 6, 0.5) for x, y in [(-0.8, 1.6), (0.4, 2.2), (1.2, 1.3), (-1.4, 1.0), (0.0, 1.2)]]
    plaque = rect(-0.8, -2.1, 0.8, -1.6)
    return Design("Snow Globe", [globe, base, tree, plaque] + houses + flakes, [], T)


@design("ice_skates", T)
def ice_skates(rng):
    def skate(dx):
        boot = poly((-1.0, 2.4), (0.2, 2.4), (0.2, 0.6), (1.4, 0.2), (1.6, -0.4), (-1.0, -0.4))
        blade = chain([(-1.1, -1.0), (1.4, -1.0)], arc(1.4, -0.8, 0.2, -math.pi / 2, math.pi / 2, 8))
        posts = [[(-0.6, -0.4), (-0.6, -1.0)], [(1.0, -0.4), (1.0, -1.0)]]
        laces = [[(-0.1, y), (0.25, y - 0.2)] for y in (2.0, 1.5, 1.0)]
        return [transform(p, dx=dx) for p in [boot, blade] + posts + laces]
    bow = [lens((0, 2.6), (-0.7, 3.0), 0.4), lens((0, 2.6), (0.7, 3.0), 0.4)]
    return Design("Ice Skates", skate(-1.4) + skate(1.4) + bow, [], T)


@design("beanie", T)
def beanie(rng):
    hat = chain(cubic((-2.0, -0.6), (-2.2, 2.4), (2.2, 2.4), (2.0, -0.6), 50))
    cuff = rrect(-2.2, -1.6, 2.2, -0.5, 0.2)
    ribs = [[(x, -1.6), (x, -0.5)] for x in (-1.6, -1.0, -0.4, 0.2, 0.8, 1.4)]
    pom = polar(lambda t: 0.7 + 0.08 * math.sin(10 * t), n=200, cy=2.4)
    pattern = zigzag(-1.9, 1.9, 0.3, 0.2, 7)
    return Design("Knitted Beanie", [hat, cuff, pom, pattern] + ribs, [], T)


@design("cocoa_mug", T)
def cocoa_mug(rng):
    mug = poly((-1.6, 1.0), (-1.4, -1.8), (1.4, -1.8), (1.6, 1.0), closed=False)
    rim = ellipse(0, 1.0, 1.6, 0.3, 80)
    handle = arc(1.6, -0.3, 0.75, math.radians(-90), math.radians(90), 20)
    marshmallows = [rrect(x - 0.25, 0.95, x + 0.25, 1.4, 0.1) for x in (-0.7, 0.0, 0.6)]
    steam = [quad((x, 1.8), (x + 0.3, 2.4), (x, 3.0)) for x in (-0.6, 0.1, 0.8)]
    snowflake = star(0, -0.4, 0.5, 6, 0.4)
    return Design("Hot Cocoa", [mug, rim, handle, snowflake] + marshmallows + steam, [], T)


@design("sled", T)
def sled(rng):
    seat = rrect(-2.4, 0.0, 2.0, 0.5, 0.15)
    slats = [[(x, 0.0), (x, 0.5)] for x in (-1.6, -0.6, 0.4, 1.4)]
    runner = chain([(-2.2, -0.8), (2.0, -0.8)], arc(2.0, -0.2, 0.6, -math.pi / 2, math.pi / 2, 16), [(1.6, 0.4)])
    posts = [[(-1.8, 0.0), (-1.8, -0.8)], [(1.2, 0.0), (1.2, -0.8)]]
    rope = cubic((2.4, 0.2), (3.2, 1.4), (2.4, 2.4), (1.2, 2.2), 30)
    hill = [quad((-3.2, -1.6), (0, -1.0), (3.2, -2.4))]
    return Design("Wooden Sled", [seat, runner, rope] + slats + posts + hill, [], T)


@design("igloo", T)
def igloo(rng):
    dome = arc(0, -1.6, 2.6, 0, math.pi, 100)
    door = chain([(1.0, -1.6)], arc(1.6, -1.6, 0.6, math.pi, 0, 20), [(2.2, -1.6)])
    courses = [[(-math.sqrt(max(0, 6.76 - (y + 1.6) ** 2)), y), (math.sqrt(max(0, 6.76 - (y + 1.6) ** 2)), y)] for y in (-0.9, -0.1, 0.6)]
    joints = [[(x, -1.6), (x, -0.9)] for x in (-1.8, -0.6)] + [[(x, -0.9), (x, -0.1)] for x in (-1.2, 0.0, 1.2)] + \
             [[(x, -0.1), (x, 0.6)] for x in (-0.6, 0.6)]
    ground = [(-3.2, -1.6), (3.2, -1.6)]
    return Design("Igloo", [dome, door, ground] + courses + joints, [], T)


@design("snowy_pine", T)
def snowy_pine(rng):
    tiers = [poly((-2.4, -1.4), (0, 0.4), (2.4, -1.4), closed=False), poly((-1.9, -0.2), (0, 1.6), (1.9, -0.2), closed=False),
             poly((-1.3, 1.0), (0, 2.8), (1.3, 1.0), closed=False)]
    snow = [wave(-2.4, 2.4, -1.4, 0.12, 5, 60), wave(-1.9, 1.9, -0.2, 0.1, 4, 50), wave(-1.3, 1.3, 1.0, 0.08, 3, 40)]
    trunk = rect(-0.3, -2.4, 0.3, -1.4)
    drifts = [arc(-1.8, -2.4, 1.0, 0, math.pi, 30), arc(1.6, -2.4, 0.8, 0, math.pi, 30)]
    flakes = [star(x, y, 0.15, 6, 0.5) for x, y in [(-2.4, 2.4), (2.2, 2.0), (2.6, 0.6)]]
    return Design("Snowy Pine", tiers + snow + [trunk] + drifts + flakes, [], T)


@design("snowy_cabin", T)
def snowy_cabin(rng):
    walls = rect(-2.0, -2.0, 2.0, 0.4)
    roof = poly((-2.6, 0.2), (0, 2.2), (2.6, 0.2), closed=False)
    snow = wave(-2.6, 2.6, 0.3, 0.08, 6, 80)
    logs = [[(-2.0, y), (2.0, y)] for y in (-1.4, -0.8, -0.2)]
    window = rect(0.6, -1.2, 1.4, -0.4)
    door = rect(-1.2, -2.0, -0.4, -0.6)
    chimney = rect(1.0, 1.3, 1.5, 2.2)
    smoke = [circle(1.3, 2.6, 0.2, 16), circle(1.6, 3.0, 0.28, 18), circle(2.0, 3.4, 0.35, 20)]
    return Design("Snowy Cabin", [walls, roof, snow, window, door, chimney] + logs + smoke, [], T)
