"""Flowers & Garden niche, part 2 (pictures 9-50)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "garden"


def bloom(cx, cy, n, r0, r1, bulge=0.35, rot=0.0, centre=True):
    out = [lens((cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a)), bulge)
           for a in [rot + k * 2 * math.pi / n for k in range(n)]]
    if centre:
        out.append(circle(cx, cy, r0, 30))
    return out


def stem(x0, y0, x1, y1, leaves=2):
    out = [quad((x0, y0), ((x0 + x1) / 2 + 0.3, (y0 + y1) / 2), (x1, y1))]
    for k in range(leaves):
        t = 0.35 + 0.3 * k
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        out.append(lens((x, y), (x + (1.2 if k % 2 else -1.2), y + 0.5), 0.3))
    return out


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


@design("lily", T)
def lily(rng):
    petals = [transform(chain(quad((0, 0), (0.6, 1.2), (0.2, 2.4)), quad((0.2, 2.4), (-0.4, 1.2), (0, 0))), dy=0.6, rot=a) for a in [k * 2 * math.pi / 6 for k in range(6)]]
    stamens = [[(0, 0.6), (0.8 * math.cos(a), 0.6 + 0.8 * math.sin(a))] for a in [math.radians(d) for d in (60, 90, 120)]]
    tips = [circle(0.8 * math.cos(a), 0.6 + 0.8 * math.sin(a), 0.1, 8) for a in [math.radians(d) for d in (60, 90, 120)]]
    return make("Lily", petals + stamens + tips + stem(0, -1.6, 0.2, -3.6, 1))


@design("iris", T)
def iris(rng):
    falls = [chain(quad((0, 0.6), (-1.8, 0.4), (-1.6, -0.8)), quad((-1.6, -0.8), (-0.6, -0.4), (0, 0.4))),
             chain(quad((0, 0.6), (1.8, 0.4), (1.6, -0.8)), quad((1.6, -0.8), (0.6, -0.4), (0, 0.4)))]
    standards = [lens((0, 0.6), (-0.6, 2.4), 0.35), lens((0, 0.6), (0.6, 2.4), 0.35), lens((0, 0.6), (0, 2.6), 0.3)]
    beard = [[(-0.6, 0.2), (-1.2, -0.3)], [(0.6, 0.2), (1.2, -0.3)]]
    leaves = [lens((0, -3.4), (-1.4, 0.0), 0.12), lens((0, -3.4), (1.2, -0.4), 0.12)]
    return make("Iris", falls + standards + beard + leaves + [[(0, 0.4), (0, -3.4)]])


@design("orchid", T)
def orchid(rng):
    out = []
    for cx, cy, s in [(-0.6, 1.6, 1.0), (1.2, 0.2, 0.8), (-1.2, -1.0, 0.7)]:
        out += [transform(p, dx=cx, dy=cy, s=s) for p in [lens((0, 0), (0, 1.2), 0.35), lens((0, 0), (-1.1, -0.6), 0.35), lens((0, 0), (1.1, -0.6), 0.35),
                                                           ellipse(-0.8, 0.3, 0.7, 0.4, 24, rot=0.4), ellipse(0.8, 0.3, 0.7, 0.4, 24, rot=-0.4),
                                                           chain(arc(0, -0.4, 0.4, math.radians(200), math.radians(340), 10))]]
    spike = [quad((2.6, -3.2), (2.4, 0.0), (0.0, 2.8))]
    pot = [poly((1.6, -3.2), (3.4, -3.2), (3.2, -2.2), (1.8, -2.2))]
    return make("Orchid", out + spike + pot)


@design("lotus", T)
def lotus(rng):
    outer = [lens((0, -0.4), (2.6 * math.cos(a), -0.4 + 1.6 * math.sin(a)), 0.32) for a in [math.radians(d) for d in (10, 40, 140, 170)]]
    inner = [lens((0, -0.4), (1.2 * math.cos(a), -0.4 + 2.4 * math.sin(a)), 0.35) for a in [math.radians(d) for d in (60, 90, 120)]]
    pad = [chain(arc(0, -1.4, 3.0, math.radians(195), math.radians(330), 40), [(0, -1.4)]), [(0, -1.4), (2.6, -2.9)]]
    water = [wave(-3.4, 3.4, -2.4, 0.08, 6, 80)]
    return make("Lotus Blossom", outer + inner + pad + water)


@design("poppy", T)
def poppy(rng):
    cup = [chain(arc(-0.8, 1.2, 1.1, math.radians(90), math.radians(300), 30)), chain(arc(0.8, 1.2, 1.1, math.radians(-120), math.radians(90), 30)),
           arc(0, 1.0, 1.3, math.radians(200), math.radians(340), 20)]
    centre = [circle(0, 1.6, 0.4, 24)] + [[(0, 1.6), (0.55 * math.cos(a), 1.6 + 0.55 * math.sin(a))] for a in [k * math.pi / 3 for k in range(6)]]
    bud = [ellipse(2.2, -0.4, 0.35, 0.55, 20), quad((2.2, -0.95), (1.6, -2.2), (1.2, -3.4))]
    return make("Red Poppy", cup + centre + bud + [quad((0, -0.2), (0.4, -1.8), (0.2, -3.4))])


@design("pansy", T)
def pansy(rng):
    top = [circle(-0.8, 1.0, 1.0, 50), circle(0.8, 1.0, 1.0, 50)]
    sides = [circle(-1.4, -0.2, 0.9, 40), circle(1.4, -0.2, 0.9, 40)]
    bottom = circle(0, -0.9, 1.1, 50)
    face = [quad((-0.3, 0.0), (0, -0.6), (0.3, 0.0))] + [[(0, -0.3), (0.6 * math.cos(a), -0.3 + 0.6 * math.sin(a))] for a in [math.radians(d) for d in (220, 270, 320)]]
    return make("Pansy", top + sides + [bottom, circle(0, 0, 0.25, 16)] + face)


@design("hibiscus", T)
def hibiscus(rng):
    petals = [transform(chain(quad((0, 0), (1.6, 0.6), (2.0, 1.6)), arc(1.4, 1.8, 0.65, math.radians(-20), math.radians(160), 14), quad((0.8, 2.0), (0.2, 1.0), (0, 0))), rot=a)
              for a in [k * 2 * math.pi / 5 for k in range(5)]]
    pistil = [quad((0, 0), (0.6, 1.6), (1.4, 3.0))] + [circle(1.4 + 0.2 * math.cos(a), 3.0 + 0.2 * math.sin(a), 0.1, 8) for a in [k * math.pi / 2 for k in range(4)]]
    return make("Hibiscus", petals + pistil)


@design("big_daisy", T)
def big_daisy(rng):
    return make("Oxeye Daisy", bloom(0, 0.6, 18, 0.8, 2.6, 0.18) + [circle(0, 0.6, 0.45, 24)] + stem(0, -2.0, 0.0, -3.6, 1))


@design("dandelion", T)
def dandelion(rng):
    seeds = []
    for k in range(18):
        a = k * 2 * math.pi / 18
        x, y = 1.8 * math.cos(a), 1.0 + 1.8 * math.sin(a)
        seeds += [[(0, 1.0), (x, y)]] + [[(x, y), (x + 0.3 * math.cos(a + d), y + 0.3 * math.sin(a + d))] for d in (-0.5, 0.0, 0.5)]
    flying = []
    for x, y in [(2.6, 2.8), (3.0, 2.0)]:
        flying += [[(x, y), (x - 0.4, y - 0.4)]] + [[(x, y), (x + 0.3 * math.cos(d), y + 0.3 * math.sin(d))] for d in (0.6, 1.2, 1.8)]
    return make("Dandelion Puff", seeds + flying + [circle(0, 1.0, 0.25, 16), quad((0, 0.75), (0.3, -1.4), (0, -3.4))])


@design("lavender", T)
def lavender(rng):
    out = []
    for x, lean in [(-1.0, -0.3), (0.0, 0.0), (1.0, 0.3)]:
        out.append(quad((0, -3.2), (x * 0.5, -1.0), (x + lean, 0.6)))
        for k in range(6):
            cx, cy = x + lean + lean * 0.3 * k, 0.8 + 0.4 * k
            out += [ellipse(cx - 0.15, cy, 0.18, 0.12, 10, rot=0.5), ellipse(cx + 0.15, cy, 0.18, 0.12, 10, rot=-0.5)]
    ribbon = [lens((0, -2.2), (-0.8, -1.8), 0.4), lens((0, -2.2), (0.8, -1.8), 0.4)]
    return make("Lavender Bunch", out + ribbon)


@design("bluebells", T)
def bluebells(rng):
    arch = quad((-0.4, -3.4), (0.2, 2.0), (2.6, 2.2))
    bells = []
    for t, x, y in [(0.3, -0.1, 0.6), (0.5, 0.6, 1.4), (0.7, 1.4, 1.8), (0.9, 2.2, 1.9)]:
        bells += [chain(arc(x, y - 0.5, 0.35, 0, math.pi, 12)), zigzag(x - 0.35, x + 0.35, y - 0.55, 0.06, 3), [(x, y - 0.15), (x, y + 0.1)]]
    leaves = [lens((-0.4, -3.4), (-1.8, -0.8), 0.15), lens((-0.4, -3.4), (1.0, -1.0), 0.15)]
    return make("Bluebells", [arch] + bells + leaves)


@design("lily_valley", T)
def lily_valley(rng):
    stalk = quad((0, -3.0), (0.4, 0.6), (2.0, 2.4))
    bells = [chain(arc(x, y, 0.3, math.radians(200), math.radians(520), 20)) for x, y in [(0.3, 0.0), (0.7, 0.8), (1.2, 1.5), (1.7, 2.0)]]
    leaf = [chain(cubic((0, -3.0), (-2.0, -1.0), (-1.6, 1.6), (-0.6, 2.6), 30), cubic((-0.6, 2.6), (-0.4, 0.6), (-0.2, -1.6), (0, -3.0), 30))]
    return make("Lily of the Valley", [stalk] + bells + leaf)


@design("morning_glory", T)
def morning_glory(rng):
    out = []
    for cx, cy, s in [(-0.8, 1.2, 1.0), (1.4, -0.2, 0.8)]:
        out += [circle(cx, cy, 1.1 * s, 50), circle(cx, cy, 0.3 * s, 16)] + [[(cx + 0.3 * s * math.cos(a), cy + 0.3 * s * math.sin(a)), (cx + 1.1 * s * math.cos(a), cy + 1.1 * s * math.sin(a))] for a in [k * 2 * math.pi / 5 for k in range(5)]]
    vine = spiral(-1.0, -2.0, 0.1, 0.8, 1.6, 60)
    leaves = [lens((-2.2, -0.4), (-3.2, 0.4), 0.45), lens((2.4, 1.2), (3.2, 2.0), 0.45)]
    return make("Morning Glory", out + [vine] + leaves)


@design("carnation", T)
def carnation(rng):
    head = polar(lambda t: 1.4 + 0.2 * abs(math.sin(6 * t)), math.radians(0), math.radians(180), 200, cy=0.6)
    frills = [zigzag(-1.2, 1.2, 0.9 + 0.4 * k, 0.12, 6 - k) for k in range(3)]
    base = chain([(-1.4, 0.6)], [(-0.4, -0.6), (0.4, -0.6), (1.4, 0.6)])
    return make("Carnation", [head, base] + frills + stem(0, -0.6, 0.1, -3.4, 2))


@design("peony", T)
def peony(rng):
    rings = [polar(lambda t, r=r: r + 0.15 * math.sin(7 * t + r), n=200) for r in (2.2, 1.6, 1.0)]
    swirl = spiral(0, 0, 0.05, 0.6, 1.6, 60)
    leaves = [lens((-1.6, -1.6), (-3.0, -2.6), 0.35), lens((1.6, -1.6), (3.0, -2.6), 0.35)]
    return make("Peony", rings + [swirl] + leaves)


@design("hydrangea", T)
def hydrangea(rng):
    florets = []
    for x, y in [(0, 1.2), (-0.9, 0.8), (0.9, 0.8), (-0.5, 0.0), (0.5, 0.0), (-1.4, -0.2), (1.4, -0.2), (0, 1.9), (-0.9, 1.7), (0.9, 1.7)]:
        florets += bloom(x, y, 4, 0.05, 0.45, 0.6, rot=0.4, centre=False)
    leaves = [lens((0, -0.8), (-2.2, -1.8), 0.35), lens((0, -0.8), (2.2, -1.8), 0.35)]
    return make("Hydrangea", florets + leaves + [[(0, -0.8), (0, -3.2)]])


@design("marigold", T)
def marigold(rng):
    rings = [polar(lambda t, r=r: r + 0.18 * abs(math.sin(9 * t)), n=300, cy=0.8) for r in (2.0, 1.4, 0.8)]
    pot = [poly((-1.4, -1.4), (1.4, -1.4), (1.1, -3.2), (-1.1, -3.2)), rect(-1.6, -1.4, 1.6, -1.0)]
    return make("Marigold", rings + pot + [[(0, -1.0), (0, -1.2)]])


@design("cosmos", T)
def cosmos(rng):
    out = []
    for cx, cy, s in [(-1.2, 1.4, 1.0), (1.4, 0.6, 0.85)]:
        for a in [k * 2 * math.pi / 8 for k in range(8)]:
            p = transform(chain(quad((0, 0), (0.5, 0.6), (0.3, 1.4)), zigzag(0.3, -0.3, 1.45, 0.06, 2), quad((-0.3, 1.4), (-0.5, 0.6), (0, 0))), dx=cx, dy=cy, s=s, rot=a)
            out.append(p)
        out.append(circle(cx, cy, 0.3 * s, 16))
    stems = [quad((-1.2, 0.0), (-0.8, -1.8), (-0.4, -3.4)), quad((1.4, -0.5), (0.8, -2.0), (-0.2, -3.4))]
    return make("Cosmos Flowers", out + stems)


@design("foxglove", T)
def foxglove(rng):
    spike = [(0, -3.4), (0, 3.0)]
    bells = []
    for k in range(7):
        y = -1.6 + 0.65 * k
        s = 1.0 - 0.1 * k
        side = 1 if k % 2 else -1
        bells.append(transform(chain([(0, 0)], cubic((0, 0), (0.6, 0.3), (1.2, 0.0), (1.4, -0.4), 10)[1:], arc(1.25, -0.45, 0.2, 0, -math.pi, 6), quad((1.1, -0.5), (0.5, -0.4), (0, -0.2), 8)), dy=y, s=s, sx=side * s))
    leaves = [lens((0, -3.4), (-1.6, -2.6), 0.35), lens((0, -3.4), (1.6, -2.6), 0.35)]
    return make("Foxglove", [spike] + bells + leaves)


@design("calla_lily", T)
def calla_lily(rng):
    out = []
    for x, r in [(-0.8, 0.2), (0.8, -0.2)]:
        spathe = chain(cubic((0, 0), (-1.0, 1.0), (-0.6, 2.6), (0.6, 3.0), 30), cubic((0.6, 3.0), (0.2, 2.0), (0.8, 0.8), (0, 0), 20))
        spadix = [(0, 0.4), (0.0, 1.8)]
        out += [transform(p, dx=x, dy=0.0, rot=r) for p in [spathe, spadix]]
        out.append(transform([(0, 0), (0, -3.2)], dx=x, rot=r * 0.3))
    vase = [chain([(-1.4, -1.6)], [(-1.0, -3.4), (1.0, -3.4), (1.4, -1.6)]), ellipse(0, -1.6, 1.4, 0.25, 30)]
    return make("Calla Lilies", out + vase)


@design("magnolia", T)
def magnolia(rng):
    branch = [quad((-3.2, -2.6), (-0.4, -1.2), (2.8, -2.8)), [(-0.6, -1.4), (-1.2, 0.0)]]
    cup = [lens((-1.2, 0.0), (-2.2, 2.0), 0.35), lens((-1.2, 0.0), (-0.2, 2.0), 0.35), lens((-1.2, 0.0), (-1.2, 2.4), 0.3)]
    bud = [lens((1.6, -2.3), (2.2, -0.8), 0.4)]
    return make("Magnolia Branch", branch + cup + bud)


@design("bird_of_paradise", T)
def bird_of_paradise(rng):
    beak = chain(quad((-2.4, -0.4), (0.0, 0.6), (2.6, 0.0)), quad((2.6, 0.0), (0.0, -0.4), (-2.4, -0.4)))
    petals = [poly((0.0, 0.3), (-0.6 + 0.5 * k, 2.6 + 0.2 * k), (0.4 + 0.3 * k, 0.4), closed=False) for k in range(3)]
    blue = [poly((0.6, 0.3), (1.6, 1.4), (1.2, 0.3), closed=False)]
    stem = [quad((-2.4, -0.4), (-2.0, -2.0), (-1.8, -3.4))]
    return make("Bird of Paradise", [beak] + petals + blue + stem)


@design("flower_vase", T)
def flower_vase(rng):
    vase = chain(cubic((-0.8, -0.2), (-2.0, -1.0), (-1.4, -3.2), (0, -3.2), 30), cubic((0, -3.2), (1.4, -3.2), (2.0, -1.0), (0.8, -0.2), 30))
    neck = [ellipse(0, -0.2, 0.8, 0.2, 24)]
    flowers = bloom(-1.0, 1.8, 6, 0.25, 0.8) + bloom(0.6, 2.4, 8, 0.2, 0.7) + bloom(1.4, 1.0, 5, 0.2, 0.7)
    stems = [[(0, -0.2), (-1.0, 1.0)], [(0, -0.2), (0.6, 1.7)], [(0, -0.2), (1.2, 0.4)]]
    return make("Vase of Flowers", [vase] + neck + flowers + stems)


@design("hanging_basket", T)
def hanging_basket(rng):
    basket = chain(arc(0, 0.4, 2.0, math.radians(195), math.radians(345), 40), [(-1.93, -0.12)])
    chains_ = [[(-1.9, 0.0), (0, 3.2)], [(1.9, 0.0), (0, 3.2)], [(0, 0.0), (0, 3.2)]]
    flowers = bloom(-1.2, 0.4, 5, 0.15, 0.6) + bloom(0.0, 0.6, 5, 0.15, 0.6) + bloom(1.2, 0.4, 5, 0.15, 0.6)
    trailing = [quad((-1.6, -0.6), (-2.2, -1.6), (-1.8, -2.8)), quad((1.6, -0.6), (2.2, -1.6), (1.8, -2.8))] + \
               [lens((-2.0 - 0.0, -1.2 - 0.6 * k), (-2.6, -1.0 - 0.6 * k), 0.4) for k in range(2)] + [lens((2.0, -1.2 - 0.6 * k), (2.6, -1.0 - 0.6 * k), 0.4) for k in range(2)]
    return make("Hanging Flower Basket", [basket] + chains_ + flowers + trailing)


@design("rose_trellis", T)
def rose_trellis(rng):
    arch = [chain([(-2.4, -3.2), (-2.4, 0.8)], arc(0, 0.8, 2.4, math.pi, 0, 40), [(2.4, -3.2)]),
            chain([(-1.9, -3.2), (-1.9, 0.8)], arc(0, 0.8, 1.9, math.pi, 0, 40), [(1.9, -3.2)])]
    rungs = [[(-2.4, y), (-1.9, y)] for y in (-2.4, -1.4, -0.4)] + [[(1.9, y), (2.4, y)] for y in (-2.4, -1.4, -0.4)]
    roses = [spiral(x, y, 0.05, 0.4, 1.8, 40) for x, y in [(-2.2, 1.6), (-0.8, 3.0), (0.9, 3.0), (2.2, 1.4), (-2.1, -1.0), (2.1, -2.0)]]
    return make("Rose Arch", arch + rungs + roses)


@design("garden_gate", T)
def garden_gate(rng):
    gate = [rect(-1.6, -3.0, 1.6, 0.8)] + [[(x, -3.0), (x, 0.8)] for x in (-0.8, 0.0, 0.8)] + [[(-1.6, -2.4), (1.6, 0.2)]]
    posts = [rect(-2.2, -3.0, -1.6, 1.4), rect(1.6, -3.0, 2.2, 1.4), poly((-2.2, 1.4), (-1.9, 1.8), (-1.6, 1.4)), poly((1.6, 1.4), (1.9, 1.8), (2.2, 1.4))]
    latch = [circle(1.3, -1.0, 0.12, 10)]
    vines = [quad((-2.2, 0.4), (-2.8, 1.6), (-2.4, 2.6)), quad((2.2, 0.4), (2.8, 1.6), (2.4, 2.6))] + bloom(-2.4, 2.7, 5, 0.1, 0.4) + bloom(2.4, 2.7, 5, 0.1, 0.4)
    return make("Garden Gate", gate + posts + latch + vines)


@design("picket_fence", T)
def picket_fence(rng):
    pickets = [poly((x - 0.3, -3.0), (x - 0.3, 0.6), (x, 1.0), (x + 0.3, 0.6), (x + 0.3, -3.0)) for x in (-2.4, -1.2, 0.0, 1.2, 2.4)]
    rails = [[(-3.2, -0.2), (3.2, -0.2)], [(-3.2, -2.0), (3.2, -2.0)]]
    flowers = bloom(-1.8, 1.6, 5, 0.15, 0.55) + bloom(0.6, 2.0, 6, 0.15, 0.55) + bloom(2.0, 1.4, 5, 0.15, 0.55)
    stems_ = [[(-1.8, 1.45), (-1.8, 0.0)], [(0.6, 1.85), (0.6, 0.0)], [(2.0, 1.25), (2.0, 0.0)]]
    return make("Picket Fence Flowers", pickets + rails + flowers + stems_)


@design("garden_bench", T)
def garden_bench(rng):
    seat = [rect(-2.6, -0.8, 2.6, -0.5)]
    back = [rect(-2.6, 0.4, 2.6, 0.7), rect(-2.6, 1.0, 2.6, 1.3)]
    legs = [chain(arc(-2.4, -1.6, 0.6, math.radians(60), math.radians(180), 10)), chain(arc(2.4, -1.6, 0.6, 0, math.radians(120), 10)),
            [(-2.2, -0.5), (-2.2, 1.3)], [(2.2, -0.5), (2.2, 1.3)], [(-2.0, -0.8), (-2.0, -2.4)], [(2.0, -0.8), (2.0, -2.4)]]
    pot = [poly((2.8, -2.4), (3.0, -1.4), (3.6, -1.4), (3.8, -2.4))] + bloom(3.3, -0.8, 5, 0.12, 0.45)
    book = [poly((-1.4, -0.5), (-0.4, -0.3), (0.6, -0.5), (0.6, -0.4), (-1.4, -0.4))]
    return make("Garden Bench", seat + back + legs + pot + book)


@design("greenhouse", T)
def greenhouse(rng):
    body = poly((-2.6, -2.6), (2.6, -2.6), (2.6, 0.4), (0, 2.4), (-2.6, 0.4))
    panes = [[(x, -2.6), (x, 0.4 + (2.0 * (1 - abs(x) / 2.6)))] for x in (-1.3, 0.0, 1.3)] + [[(-2.6, -1.0), (2.6, -1.0)], [(-2.6, 0.4), (2.6, 0.4)]]
    door = rect(-0.5, -2.6, 0.5, -0.4)
    plants = bloom(-1.9, -1.8, 5, 0.1, 0.4) + bloom(1.9, -1.8, 5, 0.1, 0.4) + [lens((-1.9, -2.5), (-1.6, -2.0), 0.4)]
    return make("Greenhouse", [body, door] + panes + plants)


@design("seed_packets", T)
def seed_packets(rng):
    out = []
    for x, r, n in [(-1.6, 0.2, 5), (0.0, 0.0, 8), (1.6, -0.2, 6)]:
        out += [transform(p, dx=x, rot=r) for p in [rect(-0.8, -1.6, 0.8, 1.4), [(-0.8, 1.0), (0.8, 1.0)]] + bloom(0, 0.0, n, 0.15, 0.6)]
    seeds = [ellipse(x, -2.6, 0.12, 0.07, 8) for x in (-1.0, -0.6, 0.2, 0.8, 1.2)]
    return make("Seed Packets", out + seeds)


@design("pot_stack", T)
def pot_stack(rng):
    pots = []
    for y, s in [(-2.0, 1.2), (-0.4, 1.0), (1.0, 0.8)]:
        pots += [poly((-1.2 * s, y + 0.6 * s), (1.2 * s, y + 0.6 * s), (0.9 * s, y - 0.9 * s), (-0.9 * s, y - 0.9 * s)), rect(-1.3 * s, y + 0.4 * s, 1.3 * s, y + 0.8 * s)]
    sprout = [quad((0, 1.6), (0.1, 2.4), (0, 2.8)), lens((0, 2.6), (-0.8, 3.2), 0.4), lens((0, 2.6), (0.8, 3.2), 0.4)]
    trowel = [[(2.0, -2.6), (2.6, -1.4)], lens((2.6, -1.4), (3.2, 0.0), 0.35)]
    return make("Stack of Flower Pots", pots + sprout + trowel)


@design("hose_reel", T)
def hose_reel(rng):
    reel = [circle(-0.6, 0.4, 1.8, 80), circle(-0.6, 0.4, 0.4, 24)] + [arc(-0.6, 0.4, r, 0, 2 * math.pi, 50) for r in (1.0, 1.4)]
    stand_ = [[(-2.2, -1.2), (-1.6, -2.6)], [(1.0, -1.2), (0.4, -2.6)], [(-2.0, -2.6), (0.6, -2.6)]]
    crank = [[(-0.6, 0.4), (0.6, 1.4)], circle(0.7, 1.5, 0.15, 10)]
    hose = cubic((1.2, 0.0), (2.6, -0.6), (1.6, -2.2), (3.2, -2.6), 30)
    nozzle = [rect(3.2, -2.8, 3.6, -2.4)]
    return make("Garden Hose Reel", reel + stand_ + crank + [hose] + nozzle)


@design("sunhat", T)
def sunhat(rng):
    brim = ellipse(0, -0.6, 3.0, 0.8, 140)
    crown = chain(arc(0, -0.4, 1.4, math.radians(10), math.radians(170), 40))
    band = quad((-1.38, -0.15), (0, -0.4), (1.38, -0.15))
    flowers = bloom(-0.8, 0.0, 5, 0.12, 0.45) + bloom(0.0, 0.1, 5, 0.12, 0.45)
    gloves = [rrect(1.0, -2.8, 2.0, -1.6, 0.35), lens((1.0, -2.0), (0.6, -1.4), 0.35), rrect(2.2, -3.0, 3.2, -1.8, 0.35)]
    return make("Gardener's Sun Hat", [brim, crown, band] + flowers + gloves)


@design("stepping_stones", T)
def stepping_stones(rng):
    stones = [transform(polar(lambda t: 0.6 + 0.08 * math.sin(3 * t + k), n=60), dx=x, dy=y, sx=1.2, sy=0.7) for k, (x, y) in enumerate([(-1.8, -2.4), (-0.4, -1.4), (0.8, -0.4), (1.8, 0.6), (2.4, 1.6)])]
    grass = [zigzag(x - 0.4, x + 0.4, y, 0.15, 3) for x, y in [(-2.8, -1.4), (-1.6, -0.4), (0.2, 0.6), (-2.4, 1.0), (1.2, 1.8)]]
    lamp = [[(-2.0, 0.4), (-2.0, 2.4)], poly((-2.4, 2.4), (-1.6, 2.4), (-1.8, 3.0), (-2.2, 3.0))]
    return make("Stepping Stone Path", stones + grass + lamp)


@design("gazebo", T)
def gazebo(rng):
    roof = poly((-3.0, 0.8), (0, 3.0), (3.0, 0.8))
    trim = zigzag(-3.0, 3.0, 0.65, 0.15, 10)
    posts = [[(x, 0.6), (x, -2.4)] for x in (-2.6, -0.9, 0.9, 2.6)]
    rail = [[(-2.6, -1.2), (2.6, -1.2)]] + [[(x, -1.2), (x, -2.4)] for x in (-2.0, -1.4, 1.4, 2.0)]
    floor = [rect(-3.0, -2.8, 3.0, -2.4)]
    finial = [[(0, 3.0), (0, 3.5)], circle(0, 3.6, 0.12, 10)]
    return make("Garden Gazebo", [roof, trim] + posts + rail + floor + finial)


@design("fountain", T)
def fountain(rng):
    basin = [ellipse(0, -2.0, 2.8, 0.6, 100), chain([(-2.8, -2.0), (-2.6, -2.8), (2.6, -2.8), (2.8, -2.0)])]
    pillar = [rect(-0.25, -2.0, 0.25, 0.0)]
    bowl = [ellipse(0, 0.0, 1.4, 0.3, 50), quad((-1.4, 0.0), (0, -0.7), (1.4, 0.0))]
    jets = [quad((0, 0.3), (-0.6, 2.6), (-1.6, 1.0)), quad((0, 0.3), (0.6, 2.6), (1.6, 1.0)), [(0, 0.3), (0, 2.4)]]
    drops = [lens((x, y), (x, y - 0.3), 0.4) for x, y in [(-1.7, 0.6), (1.7, 0.6), (-2.2, -1.2), (2.2, -1.2)]]
    return make("Garden Fountain", basin + pillar + bowl + jets + drops)


@design("flower_wreath", T)
def flower_wreath(rng):
    ring = [circle(0, 0, 2.2, 120), circle(0, 0, 1.6, 100)]
    flowers = []
    for k in range(8):
        a = k * 2 * math.pi / 8
        flowers += bloom(1.9 * math.cos(a), 1.9 * math.sin(a), 5, 0.1, 0.45, rot=a)
    bow = [lens((0, -2.4), (-0.9, -3.0), 0.4), lens((0, -2.4), (0.9, -3.0), 0.4)]
    return make("Flower Wreath", ring + flowers + bow)


@design("sundial", T)
def sundial(rng):
    face = ellipse(0, 0.6, 2.4, 0.8, 100)
    gnomon = poly((0, 0.6), (1.6, 0.6), (0, 2.2))
    ticks = [[(1.9 * math.cos(a), 0.6 + 0.62 * math.sin(a)), (2.3 * math.cos(a), 0.6 + 0.76 * math.sin(a))] for a in [k * math.pi / 6 for k in range(12)]]
    pedestal = [poly((-0.6, -0.2), (-0.8, -2.6), (0.8, -2.6), (0.6, -0.2)), rect(-1.2, -3.0, 1.2, -2.6)]
    return make("Sundial", [face, gnomon] + ticks + pedestal)


@design("potting_bench", T)
def potting_bench(rng):
    top = [rect(-3.0, -0.4, 3.0, 0.0)]
    shelf = [rect(-2.8, -2.0, 2.8, -1.8)]
    legs = [[(-2.8, -0.4), (-2.8, -3.0)], [(2.8, -0.4), (2.8, -3.0)]]
    back = [[(-2.8, 0.0), (-2.8, 2.8)], [(2.8, 0.0), (2.8, 2.8)], [(-2.8, 2.6), (2.8, 2.6)]]
    hooks = [[(-1.0, 2.6), (-1.0, 2.0)], [(1.0, 2.6), (1.0, 2.0)], lens((-1.0, 2.0), (-1.0, 0.8), 0.3), [(1.0, 2.0), (1.4, 0.8)]]
    pots = [poly((-2.2, 0.0), (-2.0, 0.8), (-1.2, 0.8), (-1.0, 0.0)), poly((0.4, 0.0), (0.6, 0.9), (1.6, 0.9), (1.8, 0.0))] + bloom(1.1, 1.5, 5, 0.12, 0.45)
    return make("Potting Bench", top + shelf + legs + back + hooks + pots)


@design("flower_cart", T)
def flower_cart(rng):
    cart = [rect(-2.6, -1.0, 1.8, 0.4), [(1.8, 0.0), (3.2, 0.6)], circle(-1.6, -1.6, 0.6, 30), circle(0.8, -1.6, 0.6, 30)]
    buckets = [poly((-2.4, 0.4), (-2.2, 1.2), (-1.2, 1.2), (-1.0, 0.4)), poly((-0.6, 0.4), (-0.4, 1.2), (0.6, 1.2), (0.8, 0.4))]
    flowers = bloom(-2.0, 2.0, 5, 0.1, 0.45) + bloom(-1.3, 2.3, 6, 0.1, 0.45) + bloom(-0.2, 2.1, 5, 0.1, 0.45) + bloom(0.5, 2.4, 6, 0.1, 0.45)
    return make("Flower Cart", cart + buckets + flowers)


@design("window_box", T)
def window_box(rng):
    window = [rect(-2.2, -0.4, 2.2, 3.0), [(0, -0.4), (0, 3.0)], [(-2.2, 1.3), (2.2, 1.3)]]
    shutters = [rect(-3.2, -0.4, -2.4, 3.0), rect(2.4, -0.4, 3.2, 3.0)]
    box = [rect(-2.6, -1.6, 2.6, -0.6)]
    flowers = bloom(-1.8, 0.0, 5, 0.12, 0.45) + bloom(-0.6, 0.2, 6, 0.12, 0.45) + bloom(0.6, 0.0, 5, 0.12, 0.45) + bloom(1.8, 0.2, 6, 0.12, 0.45)
    return make("Window Box Flowers", window + shutters + box + flowers)


@design("tulip_field", T)
def tulip_field(rng):
    out = []
    for k, (x, y, s) in enumerate([(-2.4, -0.6, 0.7), (-1.2, -0.2, 0.8), (0.0, -0.6, 0.75), (1.2, -0.2, 0.8), (2.4, -0.6, 0.7)]):
        cup = chain(quad((-0.4, 0.0), (-0.6, 0.8), (-0.3, 1.1)), [(-0.1, 0.8), (0.0, 1.1), (0.1, 0.8), (0.3, 1.1)], quad((0.3, 1.1), (0.6, 0.8), (0.4, 0.0)), [(-0.4, 0.0)])
        out += [transform(cup, dx=x, dy=y, s=s), [(x, y), (x, -2.4)]]
    windmill = [poly((2.2, 1.0), (2.4, 2.4), (2.8, 2.4), (3.0, 1.0)), [(2.6, 2.4), (3.4, 3.2)], [(2.6, 2.4), (1.8, 3.2)], [(2.6, 2.4), (3.4, 1.6)], [(2.6, 2.4), (1.8, 1.6)]]
    rows = [[(-3.2, -2.4), (3.2, -2.4)], [(-3.2, -1.6), (3.2, -1.6)]]
    return make("Tulip Field", out + windmill + rows)
