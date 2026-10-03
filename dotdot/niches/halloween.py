"""Halloween niche."""
import math

from ._kit import *  # noqa: F401,F403  (shared drawing kit)

T = "halloween"


@design("jack_o_lantern", T)
def jack_o_lantern(rng):
    lobes = [ellipse(0, 0, 1.0, 1.8, 120)]
    for dx, rx, ry in [(0.8, 1.15, 1.75), (1.5, 1.0, 1.6)]:
        half = [(dx + rx * math.cos(t), ry * math.sin(t)) for t in [-math.pi / 2 + math.pi * i / 60 for i in range(61)]]
        lobes += [half, mirror_x(half)]
    stem = poly((-0.25, 1.75), (-0.3, 2.5), (0.2, 2.7), (0.3, 1.75), closed=False)
    eyes_ = [poly((-1.2, 0.4), (-0.4, 0.4), (-0.8, 1.1)), poly((0.4, 0.4), (1.2, 0.4), (0.8, 1.1))]
    nose = poly((-0.2, -0.1), (0.2, -0.1), (0, 0.25))
    mouth = poly((-1.4, -0.5), (-0.9, -0.7), (-0.6, -0.45), (-0.3, -0.7), (0.3, -0.7), (0.6, -0.45), (0.9, -0.7), (1.4, -0.5),
                 (0.9, -1.2), (0.3, -1.0), (-0.3, -1.0), (-0.9, -1.2))
    return Design("Jack-o'-Lantern", lobes + [stem, nose, mouth] + eyes_, [], T)


@design("ghost", T)
def ghost(rng):
    body = chain(arc(0, 1.2, 1.6, 0, math.pi, 60), [(-1.6, -1.8)],
                 [(-1.6 + 0.4 * i, -1.8 + (0.35 if i % 2 else 0.0)) for i in range(1, 9)], [(1.6, 1.2)])
    eyes_ = [ellipse(-0.55, 1.3, 0.25, 0.4, 24), ellipse(0.55, 1.3, 0.25, 0.4, 24)]
    mouth = ellipse(0, 0.4, 0.35, 0.45, 30)
    arms = [quad((-1.6, 0.2), (-2.4, 0.6), (-2.6, 1.3)), quad((1.6, 0.2), (2.4, 0.6), (2.6, 1.3))]
    return Design("Friendly Ghost", [body, mouth] + eyes_ + arms, [], T)


@design("witch_hat", T)
def witch_hat(rng):
    cone = chain([(-1.4, 0.0)], cubic((-1.0, 1.4), (0.0, 2.6), (0.4, 3.0), (1.6, 2.6), 40), [(1.0, 2.4)],
                 cubic((1.0, 2.4), (0.6, 2.0), (1.0, 1.0), (1.4, 0.0), 30))
    brim = ellipse(0, 0, 2.8, 0.55, 140)
    band = [quad((-1.35, 0.35), (0, 0.15), (1.35, 0.35)), quad((-1.3, 0.75), (0, 0.55), (1.3, 0.75))]
    buckle = [rect(-0.35, 0.25, 0.35, 0.85), rect(-0.15, 0.4, 0.15, 0.7)]
    stars_ = [star(x, y, r) for x, y, r in [(-2.2, 2.2, 0.35), (2.6, 1.4, 0.3), (-1.6, 3.2, 0.25)]]
    return Design("Witch's Hat", [cone, brim] + band + buckle + stars_, [], T)


@design("bat", T)
def bat(rng):
    right = [(0.4, 0.4), (1.2, 1.2), (2.4, 1.6), (3.4, 1.2), (3.0, 0.4), (2.4, 0.7), (2.0, -0.1), (1.4, 0.3), (0.9, -0.4), (0.4, -0.2)]
    wings = chain(mirror_x(right)[::-1], right, [(-0.4, 0.4)])
    head = chain(poly((-0.45, 0.6), (-0.35, 1.3), (-0.1, 0.9), (0.1, 0.9), (0.35, 1.3), (0.45, 0.6), closed=False))
    body = ellipse(0, 0.1, 0.45, 0.75, 40)
    moon_ = circle(1.6, -1.8, 0.9, 60)
    return Design("Night Bat", [wings, head, body, moon_], [eye(-0.18, 0.7, 0.07), eye(0.18, 0.7, 0.07)], T)


@design("arched_cat", T)
def arched_cat(rng):
    body = chain([(-2.2, -1.6)], cubic((-2.2, 0.0), (-1.4, 1.6), (0.4, 1.6), (1.2, 0.6), 50), [(1.6, -1.6)])
    belly = quad((-1.6, -1.6), (-0.3, -0.2), (1.1, -1.6))
    head = circle(1.6, 0.9, 0.6, 50)
    ears = [poly((1.2, 1.3), (1.25, 1.9), (1.55, 1.5), closed=False), poly((1.75, 1.5), (2.1, 1.85), (2.05, 1.25), closed=False)]
    tail = cubic((-2.1, 0.2), (-3.0, 0.8), (-2.4, 2.4), (-3.2, 2.8), 30)
    fence = [[(-3.2, -1.6), (3.2, -1.6)]]
    moon_ = arc(-0.4, 2.8, 0.7, math.radians(60), math.radians(300), 30)
    return Design("Black Cat", [body, belly, head, tail, moon_] + ears + fence, [eye(1.4, 1.0, 0.08), eye(1.8, 1.0, 0.08)], T)


@design("haunted_house", T)
def haunted_house(rng):
    walls = poly((-2.0, -2.4), (2.0, -2.4), (2.0, 0.4), (-2.0, 0.4))
    roof = poly((-2.4, 0.3), (-1.0, 2.0), (0.2, 1.2), (1.2, 2.6), (2.4, 0.3), closed=False)
    tower = [rect(0.6, 0.4, 1.6, 1.6)]
    door = chain([(-0.5, -2.4), (-0.5, -1.2)], arc(0, -1.2, 0.5, math.pi, 0, 20), [(0.5, -2.4)])
    windows = [rect(-1.6, -0.9, -0.9, -0.1), rect(0.9, -0.9, 1.6, -0.1), circle(1.1, 1.0, 0.25, 20)]
    bats = [poly((x - 0.4, y), (x - 0.15, y + 0.15), (x, y), (x + 0.15, y + 0.15), (x + 0.4, y), closed=False) for x, y in [(-2.4, 2.6), (2.6, 2.2)]]
    tree = [[(-2.8, -2.4), (-2.8, 0.4)], [(-2.8, -0.4), (-3.4, 0.4)], [(-2.8, -0.8), (-2.2, 0.0)]]
    return Design("Haunted House", [walls, roof, door] + tower + windows + bats + tree, [], T)


@design("cauldron", T)
def cauldron(rng):
    pot = chain(arc(0, -0.2, 2.0, math.radians(190), math.radians(350), 80), [(-1.97, 0.15)])
    rim = ellipse(0, 0.25, 2.1, 0.4, 100)
    legs = [poly((-1.2, -1.85), (-1.4, -2.5), (-0.9, -1.95), closed=False), poly((1.2, -1.85), (1.4, -2.5), (0.9, -1.95), closed=False)]
    bubbles = [circle(x, y, r, 20) for x, y, r in [(-0.6, 0.9, 0.35), (0.3, 1.3, 0.45), (0.9, 2.1, 0.3), (-0.2, 2.4, 0.25)]]
    fire = [poly((-1.6, -2.8), (-1.2, -2.0), (-0.9, -2.6), (-0.4, -1.9), (0.0, -2.6), (0.4, -1.9), (0.9, -2.6), (1.2, -2.0), (1.6, -2.8), closed=False)]
    spoon = [[(1.0, 0.4), (2.0, 2.4)], ellipse(2.1, 2.6, 0.2, 0.3, 16, rot=-0.45)]
    return Design("Witch's Cauldron", [pot, rim] + legs + bubbles + fire + spoon, [], T)


@design("candy_corn", T)
def candy_corn(rng):
    def corn(cx, cy, s, r):
        outline = chain(quad((-1.0, -1.2), (0, -1.5), (1.0, -1.2), 20), cubic((1.0, -1.2), (1.0, 0.0), (0.3, 1.6), (0, 1.8), 20),
                        cubic((0, 1.8), (-0.3, 1.6), (-1.0, 0.0), (-1.0, -1.2), 20))
        bands = [quad((-0.95, -0.5), (0, -0.75), (0.95, -0.5)), quad((-0.65, 0.5), (0, 0.3), (0.65, 0.5))]
        return [transform(p, dx=cx, dy=cy, s=s, rot=r) for p in [outline] + bands]
    return Design("Candy Corn", corn(0, 0.6, 1.1, 0.0) + corn(-2.0, -1.4, 0.7, 0.5) + corn(2.0, -1.2, 0.75, -0.4), [], T)


@design("hanging_spider", T)
def hanging_spider(rng):
    thread = [(0, 3.5), (0, 1.2)]
    body = ellipse(0, -0.2, 0.9, 1.1, 70)
    head = circle(0, 1.05, 0.5, 40)
    legs = []
    for s in (-1, 1):
        for k, dy in enumerate((0.6, 0.2, -0.3, -0.8)):
            legs.append([(s * 0.8, dy), (s * (1.7 + 0.1 * k), dy + 0.6), (s * (2.3 + 0.1 * k), dy - 0.5)])
    smile = arc(0, 1.0, 0.25, math.radians(210), math.radians(330), 10)
    web = [[(-3.0, 3.5), (3.0, 3.5)], quad((-3.0, 2.6), (-2.2, 3.0), (-2.0, 3.5)), quad((3.0, 2.6), (2.2, 3.0), (2.0, 3.5))]
    return Design("Dangling Spider", [thread, body, head, smile] + legs + web, [eye(-0.18, 1.15, 0.08), eye(0.18, 1.15, 0.08)], T)


@design("broomstick", T)
def broomstick(rng):
    stick = tube([(-2.8, 2.4), (1.2, -0.8)], 0.22)
    bristles = poly((0.9, -0.4), (2.8, -1.2), (3.0, -2.2), (1.6, -2.6), (1.4, -1.0))
    straws = [[(1.2, -0.8), (2.4 - 0.2 * k, -2.0 - 0.15 * k)] for k in range(4)]
    tie = [[(0.8, -0.3), (1.5, -1.1)], [(1.0, -0.15), (1.65, -0.95)]]
    stars_ = [star(x, y, r) for x, y, r in [(-1.6, -1.6, 0.35), (2.4, 2.2, 0.3), (-2.8, 0.2, 0.25)]]
    return Design("Witch's Broom", [stick, bristles] + straws + tie + stars_, [], T)


@design("tombstone", T)
def tombstone(rng):
    stone = chain([(-1.4, -2.0), (-1.4, 0.8)], arc(0, 0.8, 1.4, math.pi, 0, 50), [(1.4, -2.0), (-1.4, -2.0)])
    rip = [[(-0.7, 0.6), (-0.7, 1.4)], arc(-0.5, 1.2, 0.2, -math.pi / 2, math.pi / 2, 8), [(-0.5, 1.0), (-0.3, 0.6)],
           [(0, 0.6), (0, 1.4)], [(0.35, 0.6), (0.35, 1.4)], arc(0.55, 1.2, 0.2, -math.pi / 2, math.pi / 2, 8)]
    cracks = [poly((0.6, -0.4), (0.8, -0.8), (0.6, -1.1), (0.9, -1.5), closed=False)]
    grass = [zigzag(-2.6, 2.6, -2.0, 0.15, 14)]
    pumpkin = [ellipse(2.2, -1.6, 0.55, 0.42, 40), [(2.2, -1.18), (2.25, -0.9)]]
    return Design("Spooky Tombstone", [stone] + rip + cracks + grass + pumpkin, [], T)
