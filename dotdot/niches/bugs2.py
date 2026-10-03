"""Butterflies & Bugs niche, part 2 (pictures 8-50)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "bugs"


def wings(up, low, cx=0.0, cy=0.0, s=1.0, tails=False):
    """Symmetric butterfly: `up`/`low` are right-wing polylines from the body."""
    out = [chain(up), chain(low), mirror_x(chain(up)), mirror_x(chain(low))]
    if tails:
        out += [poly((0.9, -1.6), (1.1, -2.6), (1.3, -1.6), closed=False), mirror_x(poly((0.9, -1.6), (1.1, -2.6), (1.3, -1.6), closed=False))]
    body = ellipse(0, -0.2, 0.18, 1.3, 30)
    head = circle(0, 1.25, 0.25, 16)
    ants = [quad((-0.1, 1.45), (-0.4, 2.2), (-0.9, 2.5)), quad((0.1, 1.45), (0.4, 2.2), (0.9, 2.5))]
    return [transform(p, dx=cx, dy=cy, s=s) for p in out + [body, head] + ants]


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


UP_ROUND = cubic((0.15, 0.6), (1.0, 2.6), (3.0, 2.8), (2.8, 0.8), 30) + cubic((2.8, 0.8), (2.6, 0.0), (1.0, 0.0), (0.15, 0.1), 20)
LOW_ROUND = cubic((0.15, -0.1), (1.6, -0.2), (2.4, -1.4), (1.6, -2.0), 20) + cubic((1.6, -2.0), (0.8, -2.4), (0.3, -1.4), (0.15, -0.8), 16)
UP_POINT = cubic((0.15, 0.6), (0.8, 2.0), (2.6, 3.2), (3.2, 2.6), 30) + cubic((3.2, 2.6), (2.8, 1.0), (1.4, 0.2), (0.15, 0.1), 20)
LOW_TAIL = cubic((0.15, -0.1), (1.4, -0.2), (2.0, -1.0), (1.3, -1.6), 20) + [(1.1, -2.6)] + cubic((0.9, -1.6), (0.6, -1.4), (0.3, -1.0), (0.15, -0.8), 12)


@design("swallowtail", T)
def swallowtail(rng):
    w = wings(UP_POINT, LOW_TAIL)
    bands = [quad((0.4, 0.5), (1.4, 1.4), (2.6, 2.4)), mirror_x(quad((0.4, 0.5), (1.4, 1.4), (2.6, 2.4)))]
    spots = [circle(1.0, -1.2, 0.15, 12), circle(-1.0, -1.2, 0.15, 12)]
    return make("Swallowtail Butterfly", w + bands + spots)


@design("monarch", T)
def monarch(rng):
    w = wings(UP_POINT, LOW_ROUND)
    veins = []
    for s in (1, -1):
        veins += [[(0.2 * s, 0.4), (2.2 * s, 2.2)], [(0.2 * s, 0.3), (2.6 * s, 1.6)], [(0.2 * s, -0.2), (1.4 * s, -1.4)], [(0.2 * s, -0.3), (0.8 * s, -1.8)]]
    dots = [circle(2.6 * s, 2.2, 0.1, 8) for s in (1, -1)] + [circle(2.9 * s, 1.7, 0.1, 8) for s in (1, -1)]
    return make("Monarch Butterfly", w + veins + dots)


@design("morpho", T)
def morpho(rng):
    w = wings(UP_ROUND, LOW_ROUND)
    edges = [arc(1.6, 1.4, 1.1, math.radians(-20), math.radians(110), 20), mirror_x(arc(1.6, 1.4, 1.1, math.radians(-20), math.radians(110), 20))]
    eyes_ = [circle(1.4, -1.0, 0.25, 16), circle(-1.4, -1.0, 0.25, 16)]
    return make("Blue Morpho", w + edges + eyes_)


@design("feathery_moth", T)
def feathery_moth(rng):
    up = [(0.15, 0.5), (2.8, 1.4), (2.6, 0.2), (0.15, 0.0)]
    low = [(0.15, -0.1), (2.0, -0.6), (1.4, -1.4), (0.15, -0.8)]
    w = wings(up, low)
    feathers = [[(-0.6 + 0.12 * k, 2.0 + 0.1 * k), (-0.9 + 0.12 * k, 2.3 + 0.1 * k)] for k in range(5)] + \
               [[(0.6 - 0.12 * k, 2.0 + 0.1 * k), (0.9 - 0.12 * k, 2.3 + 0.1 * k)] for k in range(5)]
    fuzz = zigzag(-0.2, 0.2, 0.6, 0.08, 2)
    return make("Fuzzy Moth", w + feathers + [fuzz])


@design("luna_moth", T)
def luna_moth(rng):
    up = cubic((0.15, 0.5), (1.2, 2.4), (2.8, 2.6), (2.6, 1.0), 30) + quad((2.6, 1.0), (1.4, 0.0), (0.15, 0.0), 20)
    low = cubic((0.15, -0.2), (1.4, -0.4), (1.8, -1.6), (1.4, -3.4), 30) + quad((1.4, -3.4), (0.6, -1.6), (0.15, -0.8), 20)
    w = wings(up, low)
    spots = [circle(1.6, 1.4, 0.3, 20), circle(-1.6, 1.4, 0.3, 20), circle(0.9, -1.2, 0.25, 16), circle(-0.9, -1.2, 0.25, 16)]
    moon = arc(2.6, 3.2, 0.6, math.radians(60), math.radians(300), 20)
    return make("Luna Moth", w + spots + [moon])


@design("butterfly_flower", T)
def butterfly_flower(rng):
    w = wings(UP_ROUND, LOW_ROUND, 0.0, 1.4, 0.55)
    flower = [circle(0, -1.2, 0.35, 24)] + [lens((0, -1.2), (1.3 * math.cos(a), -1.2 + 1.3 * math.sin(a)), 0.35) for a in [k * 2 * math.pi / 8 for k in range(8)]]
    stem = quad((0, -2.5), (0.2, -3.0), (0, -3.6))
    return make("Butterfly on a Flower", w + flower + [stem])


@design("emerging", T)
def emerging(rng):
    twig = [(-3.0, 3.0), (3.0, 2.8)]
    shell = chain(cubic((-0.3, 2.9), (-0.9, 1.6), (-0.6, 0.0), (0.0, -0.4), 20), cubic((0.0, -0.4), (0.6, 0.0), (0.9, 1.6), (0.3, 2.9), 20))
    crack = poly((-0.6, 0.6), (-0.2, 0.9), (0.2, 0.5), (0.6, 0.8), closed=False)
    wing = [chain(cubic((0.0, 0.2), (1.2, 0.4), (2.4, -0.8), (1.8, -2.0), 20), quad((1.8, -2.0), (0.8, -1.6), (0.0, -0.6), 16)),
            chain(cubic((0.0, 0.2), (-1.2, 0.4), (-2.4, -0.8), (-1.8, -2.0), 20), quad((-1.8, -2.0), (-0.8, -1.6), (0.0, -0.6), 16))]
    return make("Butterfly Emerging", [twig, shell, crack] + wing)


@design("cocoon", T)
def cocoon(rng):
    branch = [(-3.0, 2.6), (3.0, 2.4)]
    pods = []
    for x, L in [(-1.2, 2.6), (0.6, 3.2), (2.0, 2.2)]:
        pods.append(chain(cubic((x - 0.1, 2.5), (x - 0.8, 2.5 - L * 0.4), (x - 0.4, 2.5 - L), (x, 2.5 - L - 0.2), 20),
                          cubic((x, 2.5 - L - 0.2), (x + 0.4, 2.5 - L), (x + 0.8, 2.5 - L * 0.4), (x + 0.1, 2.5), 20)))
        pods.append([(x - 0.35, 2.5 - L * 0.5), (x + 0.35, 2.5 - L * 0.5)])
    leaves = [lens((-2.4, 2.58), (-2.8, 1.8), 0.35), lens((2.8, 2.42), (3.2, 1.6), 0.35)]
    return make("Hanging Cocoons", [branch] + pods + leaves)


@design("butterfly_pair", T)
def butterfly_pair(rng):
    a = wings(UP_ROUND, LOW_ROUND, -1.4, 1.0, 0.5)
    b = wings(UP_POINT, LOW_ROUND, 1.5, -0.8, 0.45)
    a = [transform(p, rot=0.2) for p in a]
    b = [transform(p, rot=-0.25) for p in b]
    trail = [[(x, -2.2 + 0.4 * math.sin(3 * x)) for x in [-3.0 + 0.2 * k for k in range(31)]]]
    return make("Dancing Butterflies", a + b + trail)


@design("butterfly_net", T)
def butterfly_net(rng):
    hoop = ellipse(-0.8, 1.2, 1.4, 0.6, 60, rot=0.4)
    net = chain(quad((-2.0, 0.6), (-1.6, -1.6), (-0.4, -1.8)), quad((-0.4, -1.8), (0.4, -0.6), (0.4, 1.8)))
    mesh = [[(-1.6, 0.4), (0.2, 0.8)], [(-1.2, -0.6), (0.2, -0.2)], [(-1.2, 1.0), (-0.8, -1.4)], [(-0.4, 1.3), (-0.2, -1.0)]]
    handle = [(0.4, 1.6), (3.0, -2.8)]
    bfly = wings(UP_ROUND, LOW_ROUND, 2.0, 2.4, 0.35)
    return make("Butterfly Net", [hoop, net, handle] + mesh + bfly)


@design("bumblebee", T)
def bumblebee(rng):
    body = polar(lambda t: 1.6 + 0.07 * math.sin(20 * t), n=300)
    body = [(1.2 * x, 0.9 * y) for x, y in body]
    stripes = [quad((x, 1.3), (x + 0.25, 0), (x, -1.3)) for x in (-0.4, 0.4, 1.1)]
    head = circle(-2.0, 0.2, 0.7, 40)
    wings_ = [ellipse(-0.2, 1.8, 0.6, 1.0, 40, rot=0.3), ellipse(0.7, 1.7, 0.55, 0.9, 40, rot=-0.3)]
    sting = poly((1.9, 0.15), (2.4, 0.0), (1.9, -0.15), closed=False)
    ants = [quad((-2.2, 0.85), (-2.5, 1.5), (-2.9, 1.6)), quad((-1.8, 0.85), (-1.7, 1.6), (-2.0, 2.0))]
    return make("Fuzzy Bumblebee", [body, head, sting] + stripes + wings_ + ants, [eye(-2.25, 0.35, 0.1)])


@design("bee_flower", T)
def bee_flower(rng):
    flower = [circle(0, -0.6, 0.6, 40)] + [lens((0.6 * math.cos(a), -0.6 + 0.6 * math.sin(a)), (2.0 * math.cos(a), -0.6 + 2.0 * math.sin(a)), 0.3) for a in [k * 2 * math.pi / 10 for k in range(10)]]
    bee = [ellipse(1.2, 2.4, 0.6, 0.4, 30), [(1.1, 2.0), (1.1, 2.8)], [(1.4, 2.05), (1.4, 2.75)], circle(0.45, 2.5, 0.25, 16),
           ellipse(1.1, 3.0, 0.3, 0.45, 20, rot=0.4), ellipse(1.5, 3.0, 0.3, 0.45, 20, rot=-0.4)]
    path = [(-2.6 + 0.4 * k, 2.6 + 0.4 * math.sin(2 * k)) for k in range(8)]
    stem = [(0, -2.6), (0, -3.6)]
    return make("Bee and Flower", flower + bee + [path, stem])


@design("honeycomb", T)
def honeycomb(rng):
    cells = []
    for i in range(-2, 3):
        for j in range(-2, 3):
            x = i * 1.04 + (0.52 if j % 2 else 0)
            y = j * 0.9
            if x * x + y * y < 6.0:
                cells.append(poly(*[(x + 0.55 * math.cos(math.pi / 6 + k * math.pi / 3), y + 0.55 * math.sin(math.pi / 6 + k * math.pi / 3)) for k in range(6)]))
    drip = lens((0.5, -2.1), (0.5, -3.0), 0.4)
    dipper = [[(2.0, 1.4), (3.4, 3.0)]] + [ellipse(1.8, 1.2 - 0.2 * k, 0.35, 0.12, 16) for k in range(3)]
    return make("Honeycomb", cells + [drip] + dipper)


@design("ladybug_leaf", T)
def ladybug_leaf(rng):
    leaf = chain(cubic((-3.2, -2.0), (-1.0, 0.4), (1.6, 1.6), (3.2, 2.4), 40), cubic((3.2, 2.4), (1.4, -0.8), (-0.8, -1.8), (-3.2, -2.0), 40))
    midrib = quad((-3.2, -2.0), (0.2, -0.2), (3.2, 2.4))
    bug = [circle(0.4, 0.4, 0.9, 50), [(0.4, 1.3), (0.4, -0.5)], chain(arc(0.4, 1.2, 0.4, 0, math.pi, 12))]
    spots = [circle(x, y, 0.15, 10) for x, y in [(0.0, 0.7), (0.8, 0.7), (0.0, 0.0), (0.8, 0.0)]]
    holes = [circle(-1.6, -1.2, 0.2, 12), circle(1.8, 1.2, 0.15, 10)]
    return make("Ladybug on a Leaf", [leaf, midrib] + bug + spots + holes)


@design("grasshopper", T)
def grasshopper(rng):
    body = chain(quad((-2.0, 0.2), (0.0, 0.9), (2.6, 0.2), 30), quad((2.6, 0.2), (0.0, -0.4), (-2.0, 0.2), 30))
    head = ellipse(-2.2, 0.3, 0.5, 0.6, 30)
    wing = quad((-1.0, 0.5), (0.8, 1.0), (2.4, 0.3))
    hind = [[(0.6, 0.2), (1.4, 1.6), (2.4, -0.8)], [(0.2, 0.0), (0.8, 1.2), (1.8, -0.8)]]
    front = [[(-1.4, -0.1), (-1.6, -0.8)], [(-1.0, -0.1), (-0.9, -0.8)]]
    ants = [quad((-2.4, 0.8), (-2.0, 2.2), (-0.6, 2.8))]
    grass = [quad((x, -2.6), (x + 0.3, -1.6), (x + 0.1, -0.8)) for x in (-3.0, -2.6, 2.6, 3.0)]
    return make("Grasshopper", [body, head, wing] + hind + front + ants + grass, [eye(-2.35, 0.45, 0.1)])


@design("cricket_violin", T)
def cricket_violin(rng):
    body = ellipse(0, -0.4, 0.8, 1.4, 50)
    head = circle(0, 1.3, 0.55, 30)
    ants = [quad((-0.2, 1.8), (-0.8, 2.8), (-1.6, 3.2)), quad((0.2, 1.8), (0.8, 2.8), (1.6, 3.2))]
    legs = [[(-0.5, -1.4), (-1.0, -2.4), (-0.6, -3.0)], [(0.5, -1.4), (1.0, -2.4), (0.6, -3.0)]]
    violin = [ellipse(-1.8, 0.0, 0.5, 0.8, 30, rot=0.5), [(-1.4, 0.7), (-0.6, 1.8)], [(-2.0, -0.4), (-1.6, 0.4)]]
    bow = [[(1.4, 1.0), (-2.4, -0.2)]]
    notes = [[(2.0, 1.6), (2.0, 2.4), (2.3, 2.2)], circle(1.85, 1.6, 0.15, 10), [(2.6, 0.6), (2.6, 1.4), (2.9, 1.2)], circle(2.45, 0.6, 0.15, 10)]
    return make("Cricket Playing Violin", [body, head] + ants + legs + violin + bow + notes, [eye(-0.2, 1.4, 0.08), eye(0.2, 1.4, 0.08)])


@design("praying_mantis", T)
def praying_mantis(rng):
    abdomen = ellipse(1.6, -0.6, 1.4, 0.45, 40, rot=-0.3)
    thorax = [(0.3, -0.2), (-0.6, 1.6)]
    head = poly((-0.9, 1.6), (-0.3, 1.8), (-0.6, 1.2))
    arms = [[(-0.4, 1.1), (-1.4, 0.6), (-1.0, 1.4)], [(-0.3, 0.9), (-1.2, 0.2), (-0.8, 1.0)]]
    legs = [[(0.6, -0.6), (0.2, -2.0)], [(1.4, -0.8), (1.6, -2.0)], [(1.0, -0.7), (0.8, -2.0)]]
    ants = [quad((-0.8, 1.8), (-1.2, 2.6), (-2.0, 3.0))]
    stem = [(-3.0, -2.0), (3.0, -2.0)]
    return make("Praying Mantis", [abdomen, thorax, head, stem] + arms + legs + ants, [eye(-0.8, 1.6, 0.06)])


@design("stick_insect", T)
def stick_insect(rng):
    twig = [[(-3.2, -2.4), (3.2, 2.4)], [(1.2, 0.9), (2.0, 0.0)], [(-1.0, -0.75), (-1.6, 0.2)]]
    body = [(-2.0, -0.8), (1.6, 1.9)]
    body2 = [(-2.0, -0.6), (1.6, 2.1)]
    legs = [[(x, x * 0.75 + 0.6), (x - 0.6, x * 0.75 + 1.8)] for x in (-1.2, 0.0, 1.0)] + [[(x, x * 0.75 + 0.6), (x + 0.4, x * 0.75 - 0.8)] for x in (-1.0, 0.2, 1.2)]
    ants = [[(1.6, 2.0), (2.6, 3.0)], [(1.6, 2.0), (2.8, 2.4)]]
    return make("Stick Insect", twig + [body, body2] + legs + ants)


@design("scorpion", T)
def scorpion(rng):
    body = ellipse(0, -0.8, 1.2, 0.6, 40)
    tail = [circle(1.2 + 0.4 * k * math.cos(k * 0.5), -0.6 + 0.5 * k, 0.28, 16) for k in range(5)]
    stinger = poly((2.0, 2.0), (1.4, 2.6), (1.6, 2.0), closed=False)
    claws = [[(-1.0, -0.6), (-2.0, 0.4)], chain(arc(-2.4, 0.8, 0.5, math.radians(-60), math.radians(240), 20)),
             [(-1.0, -1.0), (-2.2, -1.6)], chain(arc(-2.6, -1.6, 0.4, math.radians(30), math.radians(330), 16))]
    legs = [[(x, -1.3), (x - 0.3, -2.2)] for x in (-0.6, -0.2, 0.2, 0.6)]
    sand = [wave(-3.2, 3.2, -2.4, 0.08, 4, 60)]
    return make("Desert Scorpion", [body, stinger] + tail + claws + legs + sand)


@design("centipede", T)
def centipede(rng):
    cl = [(-2.6 + 5.2 * t, 0.8 * math.sin(2 * math.pi * t)) for t in [i / 14 for i in range(15)]]
    segs = [circle(x, y, 0.35, 20) for x, y in cl]
    legs = []
    for x, y in cl[1:]:
        legs += [[(x, y - 0.35), (x - 0.2, y - 0.9)], [(x, y + 0.35), (x - 0.2, y + 0.9)]]
    head = [circle(-2.9, 0.0, 0.45, 24), quad((-3.1, 0.4), (-3.4, 1.0), (-3.0, 1.4)), quad((-2.8, 0.4), (-2.6, 1.0), (-2.2, 1.3))]
    return make("Centipede", segs + legs + head, [eye(-3.1, 0.1, 0.07)])


@design("snail_mushroom", T)
def snail_mushroom(rng):
    cap = chain(arc(0, 0.0, 2.2, 0, math.pi, 50), quad((-2.2, 0.0), (0, -0.4), (2.2, 0.0), 20))
    stem = poly((-0.5, -0.2), (-0.7, -2.6), (0.7, -2.6), (0.5, -0.2), closed=False)
    spots = [circle(x, y, 0.25, 16) for x, y in [(-1.2, 0.8), (0.2, 1.5), (1.3, 0.6)]]
    snail = [spiral(-0.1, 2.85, 0.05, 0.55, 2.0, 60), quad((-1.0, 2.25), (0.4, 2.15), (1.2, 2.3)),
             [(-0.9, 2.3), (-1.2, 2.9)], circle(-1.25, 3.0, 0.1, 8)]
    return make("Snail on a Mushroom", [cap, stem] + spots + snail)


@design("slug", T)
def slug(rng):
    body = chain(cubic((-2.8, -0.6), (-2.4, 0.8), (1.4, 0.8), (3.0, -0.4), 40), [(-2.8, -0.6)])
    mantle = ellipse(-1.0, 0.0, 1.0, 0.4, 30)
    stalks = [[(-2.4, -0.2), (-2.8, 0.8)], [(-2.1, -0.1), (-2.2, 0.9)], circle(-2.85, 0.9, 0.1, 8), circle(-2.2, 1.0, 0.1, 8)]
    trail = [wave(-0.4, 3.4, -0.9, 0.05, 6, 60)]
    leaf = [chain(cubic((-3.2, -1.2), (-1.0, -2.4), (2.0, -2.2), (3.4, -1.2), 30)), [(-3.2, -1.2), (3.4, -1.2)]]
    return make("Garden Slug", [body, mantle] + stalks + trail + leaf)


@design("mosquito", T)
def mosquito(rng):
    body = ellipse(0.6, 0.0, 1.4, 0.3, 30, rot=-0.3)
    thorax = circle(-0.8, 0.5, 0.4, 24)
    head = circle(-1.3, 0.8, 0.25, 16)
    nose = [(-1.5, 0.75), (-2.8, 0.2)]
    wings_ = [lens((-0.6, 0.8), (0.8, 2.4), 0.25), lens((-0.6, 0.8), (1.4, 1.8), 0.25)]
    legs = [[(-0.8, 0.2), (-1.6, -1.6)], [(-0.6, 0.2), (-0.2, -1.8)], [(-0.5, 0.25), (0.8, -1.6)], [(-0.9, 0.3), (-2.2, -1.0)]]
    no = [circle(1.8, 2.2, 0.9, 50), [(1.2, 1.6), (2.4, 2.8)]]
    return make("Mosquito", [body, thorax, head, nose] + wings_ + legs + no)


@design("housefly", T)
def housefly(rng):
    body = ellipse(0, -0.6, 0.8, 1.2, 40)
    thorax = circle(0, 0.8, 0.6, 30)
    eyes_ = [circle(-0.4, 1.5, 0.35, 20), circle(0.4, 1.5, 0.35, 20)]
    wings_ = [ellipse(-1.2, 0.2, 1.2, 0.5, 40, rot=-0.5), ellipse(1.2, 0.2, 1.2, 0.5, 40, rot=0.5)]
    veins = [[(-0.6, 0.6), (-2.0, -0.4)], [(0.6, 0.6), (2.0, -0.4)]]
    legs = [[(s * 0.5, 0.5), (s * 1.6, 1.4)] for s in (-1, 1)] + [[(s * 0.6, 0.0), (s * 1.8, -0.6)] for s in (-1, 1)] + [[(s * 0.5, -0.6), (s * 1.4, -1.8)] for s in (-1, 1)]
    swatter = [rect(1.8, 2.0, 3.2, 3.4), [(2.5, 2.0), (2.5, 0.6)]] + [[(1.8, y), (3.2, y)] for y in (2.4, 2.8, 3.1)]
    return make("House Fly", [body, thorax] + eyes_ + wings_ + veins + legs + swatter)


@design("wasp", T)
def wasp(rng):
    abdomen = ellipse(1.2, -0.6, 1.2, 0.6, 40, rot=-0.3)
    stripes = [transform(quad((x, 0.55), (x + 0.15, 0), (x, -0.55)), dx=1.2, dy=-0.6, rot=-0.3) for x in (-0.4, 0.1, 0.6)]
    thorax = ellipse(-0.6, 0.2, 0.55, 0.4, 24)
    head = circle(-1.4, 0.5, 0.4, 20)
    sting = [(2.3, -1.25), (2.8, -1.5)]
    wings_ = [lens((-0.6, 0.5), (1.0, 1.8), 0.3), lens((-0.5, 0.5), (1.6, 1.2), 0.3)]
    legs = [[(-0.6, -0.1), (-1.0, -1.2)], [(-0.4, -0.1), (-0.2, -1.3)], [(-0.2, 0.0), (0.4, -1.2)]]
    ants = [quad((-1.6, 0.85), (-2.0, 1.6), (-2.6, 1.7))]
    return make("Wasp", [abdomen, thorax, head, sting] + stripes + wings_ + legs + ants, [eye(-1.55, 0.6, 0.08)])


@design("hornet_nest", T)
def hornet_nest(rng):
    branch = [(-3.0, 3.0), (3.0, 2.8)]
    nest = chain(cubic((-0.3, 2.9), (-2.4, 2.4), (-2.6, -1.6), (0, -2.0), 40), cubic((0, -2.0), (2.6, -1.6), (2.4, 2.4), (0.3, 2.9), 40))
    layers = [quad((-2.0 + 0.1 * k, 1.6 - 0.8 * k), (0, 1.3 - 0.8 * k), (2.0 - 0.1 * k, 1.6 - 0.8 * k)) for k in range(4)]
    hole = circle(0, -1.6, 0.3, 20)
    buzz = [ellipse(2.4, -0.4, 0.3, 0.18, 16), ellipse(-2.6, 0.6, 0.3, 0.18, 16)]
    return make("Paper Wasp Nest", [branch, nest, hole] + layers + buzz)


@design("anthill", T)
def anthill(rng):
    hill = chain(quad((-3.2, -2.4), (0, 2.6), (3.2, -2.4)))
    holes = [ellipse(0, 0.0, 0.35, 0.2, 16)]
    tunnels = [[(0, -0.2), (-0.4, -1.0), (-1.2, -1.4)], [(-0.4, -1.0), (0.4, -1.8)], ellipse(-1.4, -1.5, 0.4, 0.25, 16), ellipse(0.6, -1.9, 0.4, 0.25, 16)]
    ants = []
    for x, y in [(1.4, 0.4), (2.2, -0.8), (-1.6, 0.6)]:
        ants += [circle(x, y, 0.12, 8), circle(x + 0.2, y + 0.05, 0.1, 8), circle(x + 0.38, y + 0.1, 0.12, 8)]
    ground = [(-3.4, -2.4), (3.4, -2.4)]
    return make("Ant Hill", [hill, ground] + holes + tunnels + ants)


@design("leafcutter", T)
def leafcutter(rng):
    out = []
    for k, (x, y) in enumerate([(-2.0, -1.0), (0.0, -0.6), (2.0, -1.0)]):
        out += [ellipse(x - 0.4, y, 0.35, 0.25, 16), circle(x, y + 0.05, 0.15, 10), circle(x + 0.35, y + 0.1, 0.2, 12)]
        out += [[(x, y), (x - 0.2, y - 0.5)], [(x, y), (x + 0.2, y - 0.5)], [(x + 0.4, y + 0.25), (x + 0.6, y + 1.2)]]
        out.append(lens((x + 0.6, y + 1.2), (x + 0.6 + (0.8 if k % 2 else -0.8), y + 2.2), 0.4))
    path = [(-3.2, -1.6), (3.2, -1.6)]
    return make("Leafcutter Ants", out + [path])


@design("water_strider", T)
def water_strider(rng):
    body = ellipse(0, 0.0, 0.9, 0.2, 30)
    legs = [quad((-0.3, 0.0), (-1.4, 0.8), (-2.8, 0.6)), quad((-0.2, 0.0), (-1.2, -0.6), (-2.6, -1.0)),
            quad((0.3, 0.0), (1.4, 0.8), (2.8, 0.6)), quad((0.2, 0.0), (1.2, -0.6), (2.6, -1.0))]
    ripples = [ellipse(x, y, 0.4, 0.12, 20) for x, y in [(-2.8, 0.6), (-2.6, -1.0), (2.8, 0.6), (2.6, -1.0)]]
    pond = [ellipse(0, -0.2, 3.4, 2.0, 120)]
    lily = [arc(1.6, -2.6, 0.8, math.radians(30), math.radians(330), 30)]
    return make("Water Strider", [body] + legs + ripples + pond + lily)


@design("cicada", T)
def cicada(rng):
    body = ellipse(0, -0.2, 0.7, 1.4, 40)
    head = ellipse(0, 1.3, 0.8, 0.4, 30)
    eyes_ = [circle(-0.8, 1.35, 0.25, 16), circle(0.8, 1.35, 0.25, 16)]
    wings_ = [chain(cubic((-0.3, 1.0), (-2.4, 0.4), (-2.0, -2.4), (-0.4, -2.6), 30)), chain(cubic((0.3, 1.0), (2.4, 0.4), (2.0, -2.4), (0.4, -2.6), 30))]
    veins = [[(-0.4, 0.6), (-1.6, -1.6)], [(-0.4, 0.2), (-1.0, -2.2)], [(0.4, 0.6), (1.6, -1.6)], [(0.4, 0.2), (1.0, -2.2)]]
    bark = [[(-3.0, -3.2), (-3.0, 3.2)], [(3.0, -3.2), (3.0, 3.2)]]
    return make("Cicada", [body, head] + eyes_ + wings_ + veins + bark)


@design("rhino_beetle", T)
def rhino_beetle(rng):
    shell = chain(cubic((-1.0, 0.0), (-1.0, 1.8), (2.4, 1.8), (2.6, 0.0), 40), [(-1.0, 0.0)])
    split = [(0.8, 1.35), (0.8, 0.0)]
    head = chain(cubic((-1.0, 0.8), (-2.0, 0.8), (-2.4, 0.2), (-2.0, -0.1), 16), [(-1.0, 0.0)])
    horn = chain(quad((-2.0, 0.6), (-2.8, 1.2), (-2.6, 2.4), 16), quad((-2.6, 2.4), (-2.4, 1.2), (-1.7, 0.75), 16))
    legs = [[(x, 0.0), (x - 0.4, -0.9), (x - 0.1, -1.2)] for x in (-0.6, 0.6, 1.8)]
    log = [rrect(-3.2, -2.4, 3.2, -1.2, 0.5), arc(-3.2, -1.8, 0.5, math.radians(90), math.radians(270), 12)]
    return make("Rhinoceros Beetle", [shell, split, head, horn] + legs + log, [eye(-1.7, 0.4, 0.07)])


@design("ladybug_family", T)
def ladybug_family(rng):
    out = []
    for x, y, s in [(-1.4, 0.6, 1.0), (1.2, 1.2, 0.7), (1.4, -1.2, 0.55), (-0.4, -1.8, 0.45)]:
        out += [circle(x, y, s, 40), [(x, y + s), (x, y - s)], chain(arc(x, y + 0.9 * s, 0.4 * s, 0, math.pi, 10))]
        out += [circle(x + dx * s, y + dy * s, 0.13 * s, 8) for dx, dy in [(-0.45, 0.3), (0.45, 0.3), (-0.4, -0.35), (0.4, -0.35)]]
    return make("Ladybug Family", out)


@design("firefly_jar", T)
def firefly_jar(rng):
    jar = [rrect(-1.8, -2.8, 1.8, 1.4, 0.5), rect(-1.4, 1.4, 1.4, 2.0), [(-1.6, 2.0), (1.6, 2.0)]]
    holes = [circle(x, 1.7, 0.08, 8) for x in (-0.8, 0.0, 0.8)]
    flies = []
    for x, y in [(-0.8, 0.4), (0.6, -0.6), (-0.4, -1.8), (0.9, 0.8)]:
        flies += [ellipse(x, y, 0.25, 0.15, 12), circle(x + 0.3, y, 0.25, 12)] + \
                 [[(x + 0.3 + 0.35 * math.cos(a), y + 0.35 * math.sin(a)), (x + 0.3 + 0.55 * math.cos(a), y + 0.55 * math.sin(a))] for a in (0.0, 1.6, 3.2, 4.8)]
    grass = [zigzag(-3.0, 3.0, -2.8, 0.2, 12)]
    return make("Jar of Fireflies", jar + holes + flies + grass)


@design("magnifier_bug", T)
def magnifier_bug(rng):
    lens_ = [circle(-0.6, 0.6, 1.8, 90), circle(-0.6, 0.6, 1.55, 80)]
    handle = [tube([(0.7, -0.7), (2.6, -2.6)], 0.5)]
    bug = [ellipse(-0.6, 0.4, 0.6, 0.85, 30), [(-0.6, 1.25), (-0.6, -0.45)], circle(-0.6, 1.45, 0.25, 16)] + \
          [[(-0.6 + s * 0.55, y), (-0.6 + s * 1.1, y - 0.2)] for s in (-1, 1) for y in (0.8, 0.4, 0.0)]
    return make("Bug Under a Magnifier", lens_ + handle + bug)


@design("bug_hotel", T)
def bug_hotel(rng):
    house = poly((-2.0, -2.6), (2.0, -2.6), (2.0, 1.0), (0, 2.6), (-2.0, 1.0))
    shelves = [[(-2.0, 1.0), (2.0, 1.0)], [(-2.0, -0.4), (2.0, -0.4)], [(0, -2.6), (0, 1.0)]]
    logs = [circle(x, y, 0.3, 16) for x in (-1.5, -0.8) for y in (0.5, -0.1)]
    straws = [[(x, -0.4), (x, -2.6)] for x in (0.4, 0.8, 1.2, 1.6)]
    cones = [ellipse(-1.0, -1.5, 0.6, 0.8, 30)]
    sign = [rect(-0.5, 1.3, 0.5, 1.8)]
    return make("Bug Hotel", [house] + shelves + logs + straws + cones + sign)


@design("orb_spider", T)
def orb_spider(rng):
    spokes = [[(0, 0), (3.0 * math.cos(a), 3.0 * math.sin(a))] for a in [k * math.pi / 6 for k in range(12)]]
    spiral_ = spiral(0, 0, 0.3, 2.8, 5.0, 300)
    spider = [ellipse(0, -0.2, 0.4, 0.55, 24), circle(0, 0.45, 0.25, 16)] + \
             [[(s * 0.3, y), (s * 0.9, y + 0.4), (s * 1.1, y - 0.3)] for s in (-1, 1) for y in (0.3, 0.0, -0.3)]
    return make("Orb Weaver Spider", spokes + [spiral_] + spider)


@design("jumping_spider", T)
def jumping_spider(rng):
    head = ellipse(0, 0.6, 1.8, 1.4, 80)
    eyes_ = [circle(-0.55, 0.6, 0.45, 30), circle(0.55, 0.6, 0.45, 30), circle(-1.3, 1.0, 0.2, 14), circle(1.3, 1.0, 0.2, 14)]
    fangs = [ellipse(-0.35, -0.7, 0.25, 0.4, 16), ellipse(0.35, -0.7, 0.25, 0.4, 16)]
    legs = [[(s * 1.6, 0.0), (s * 2.6, 1.0), (s * 3.2, -0.6)] for s in (-1, 1)] + [[(s * 1.4, -0.5), (s * 2.2, -1.4), (s * 2.8, -2.6)] for s in (-1, 1)]
    fuzz = [zigzag(-1.4, 1.4, 1.75, 0.1, 6)]
    return make("Jumping Spider", [head] + eyes_ + fangs + legs + fuzz, [eye(-0.55, 0.6, 0.2), eye(0.55, 0.6, 0.2)])


@design("dung_beetle", T)
def dung_beetle(rng):
    ball = circle(1.4, 0.6, 1.4, 70)
    texture = [arc(1.2, 0.8, 0.6, 0.4, 2.4, 10), arc(1.8, 0.0, 0.4, 2.0, 4.0, 8)]
    beetle = [ellipse(-1.2, 0.2, 0.9, 0.6, 30, rot=0.6), circle(-1.9, -0.3, 0.3, 16)]
    legs = [[(-0.6, 0.6), (0.1, 1.2)], [(-0.5, 0.4), (0.1, 0.6)], [(-1.4, -0.3), (-1.8, -1.2)], [(-1.0, -0.2), (-1.0, -1.2)]]
    sand = [wave(-3.2, 3.2, -1.2, 0.08, 4, 60)]
    return make("Dung Beetle", [ball] + texture + beetle + legs + sand)


@design("moth_lamp", T)
def moth_lamp(rng):
    lamp = [poly((-1.2, 1.0), (1.2, 1.0), (0.8, 2.6), (-0.8, 2.6)), circle(0, 0.5, 0.5, 30), [(0, 1.0), (0, 0.0)]]
    glow = [[(0.7 * math.cos(a), 0.5 + 0.7 * math.sin(a)), (1.2 * math.cos(a), 0.5 + 1.2 * math.sin(a))] for a in [math.radians(d) for d in (200, 240, 270, 300, 340)]]
    moths = []
    for x, y, r in [(-2.0, 0.0, 0.3), (2.0, -0.6, -0.4), (1.8, 1.6, 0.2)]:
        moths += [transform(p, dx=x, dy=y, rot=r) for p in [lens((0, 0), (0.6, 0.5), 0.4), lens((0, 0), (-0.6, 0.5), 0.4), lens((0, 0), (0.4, -0.4), 0.4), lens((0, 0), (-0.4, -0.4), 0.4)]]
    post = [[(0, 2.6), (0, 3.2)], [(-1.0, 3.2), (1.0, 3.2)]]
    return make("Moths and Lamp", lamp + glow + moths + post)


@design("munching_caterpillar", T)
def munching_caterpillar(rng):
    leaf = chain(cubic((-3.0, 0.0), (-1.6, 2.4), (1.6, 2.4), (3.0, 0.0), 40), cubic((3.0, 0.0), (1.6, -2.4), (-1.6, -2.4), (-3.0, 0.0), 40))
    bites = [arc(1.6, 1.6, 0.5, math.radians(180), math.radians(360), 12), arc(2.4, 0.6, 0.4, math.radians(100), math.radians(260), 10)]
    holes = [circle(-1.2, 0.6, 0.3, 16), circle(0.6, -0.8, 0.25, 14)]
    cat = [circle(-1.6 + 0.55 * k, -1.6 + 0.2 * math.sin(k), 0.3, 16) for k in range(5)] + [circle(1.2, -1.3, 0.4, 20)]
    return make("Munching Caterpillar", [leaf] + bites + holes + cat, [eye(1.3, -1.2, 0.07)])


@design("katydid", T)
def katydid(rng):
    wing = chain(cubic((-1.6, 0.4), (-0.4, 1.6), (2.0, 1.4), (2.8, 0.2), 30), quad((2.8, 0.2), (0.6, -0.2), (-1.6, 0.4), 20))
    veins = [[(-1.2, 0.5), (2.6, 0.3)]] + [[(-0.6 + 0.6 * k, 0.45), (-0.2 + 0.6 * k, 1.1)] for k in range(5)]
    head = ellipse(-2.0, 0.3, 0.5, 0.45, 24)
    ants = [quad((-2.4, 0.6), (-1.0, 2.8), (1.6, 3.2)), quad((-2.3, 0.7), (-1.6, 3.0), (-0.4, 3.4))]
    legs = [[(0.6, 0.0), (1.6, -1.2), (2.4, -1.6)], [(-1.2, 0.0), (-1.6, -1.2)], [(-0.6, 0.0), (-0.6, -1.2)]]
    return make("Katydid", [wing, head] + veins + ants + legs, [eye(-2.15, 0.4, 0.08)])


@design("ladybug_umbrella", T)
def ladybug_umbrella(rng):
    leaf_umb = chain(cubic((-2.6, 0.6), (-2.0, 2.6), (2.0, 2.6), (2.6, 0.6), 40), quad((2.6, 0.6), (0, 1.0), (-2.6, 0.6), 20))
    stem = [(0.0, 0.8), (0.4, -1.2)]
    bug = [circle(0.4, -1.8, 0.7, 40), [(0.4, -1.1), (0.4, -2.5)], chain(arc(0.4, -1.2, 0.3, 0, math.pi, 10))] + \
          [circle(0.4 + dx, -1.8 + dy, 0.1, 8) for dx, dy in [(-0.3, 0.2), (0.3, 0.2), (-0.3, -0.25), (0.3, -0.25)]]
    drops = [lens((x, y), (x, y - 0.4), 0.4) for x, y in [(-3.0, 0.4), (3.0, 0.2), (-2.6, -1.4), (2.6, -1.6)]]
    return make("Ladybug with Leaf Umbrella", [leaf_umb, stem] + bug + drops)


@design("shield_bug", T)
def shield_bug(rng):
    shield = poly((-1.6, 1.0), (1.6, 1.0), (1.4, -0.6), (0, -2.2), (-1.4, -0.6))
    tri = poly((-0.8, 1.0), (0.8, 1.0), (0, -0.8))
    head = chain(arc(0, 1.3, 0.5, math.radians(-10), math.radians(190), 16))
    ants = [quad((-0.2, 1.7), (-0.6, 2.6), (-1.2, 2.9)), quad((0.2, 1.7), (0.6, 2.6), (1.2, 2.9))]
    legs = [[(s * 1.5, y), (s * 2.4, y - 0.4)] for s in (-1, 1) for y in (0.6, -0.2, -0.8)]
    dots = [circle(x, y, 0.1, 8) for x, y in [(-1.0, 0.4), (1.0, 0.4), (-0.6, -0.8), (0.6, -0.8)]]
    return make("Shield Bug", [shield, tri, head] + ants + legs + dots)
