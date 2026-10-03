"""Farm Life niche, part 2 (pictures 11-50)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "farm"


def quad_body(L=3.0, H=1.2, cx=0.0, cy=0.0, leg_h=1.6, tail=True):
    """Four-legged animal side view facing left: body, legs, tail."""
    body = rrect(-L / 2, -H / 2, L / 2, H / 2, H * 0.45)
    legs = [leg(x, x + 0.32, -H / 2 + 0.3, -H / 2 - leg_h) for x in (-L / 2 + 0.2, -L / 2 + 0.7, L / 2 - 0.95, L / 2 - 0.45)]
    out = [body] + legs
    if tail:
        out.append(quad((L / 2 - 0.05, H / 2 - 0.2), (L / 2 + 0.5, 0.0), (L / 2 + 0.45, -H / 2 - 0.4)))
    return [transform(p, dx=cx, dy=cy) for p in out]


def ground(y=-2.6):
    return [(-3.4, y), (3.4, y)]


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


@design("goat", T)
def goat(rng):
    b = quad_body(2.8, 1.2, 0.4, -0.4)
    head = chain(quad((-0.9, 0.2), (-1.6, 1.4), (-2.2, 1.0), 16), quad((-2.2, 1.0), (-2.6, 0.4), (-2.2, 0.2), 10), [(-1.2, -0.2)])
    horns = [quad((-1.6, 1.3), (-1.2, 2.2), (-0.6, 2.0)), quad((-1.4, 1.2), (-0.9, 1.9), (-0.4, 1.7))]
    beard = poly((-2.3, 0.25), (-2.2, -0.4), (-2.0, 0.2), closed=False)
    ear = lens((-1.4, 1.1), (-0.8, 1.0), 0.35)
    return make("Billy Goat", b + [head, beard, ear, ground(-2.0)] + horns, [eye(-1.75, 0.95, 0.08)])


@design("donkey", T)
def donkey(rng):
    b = quad_body(2.8, 1.3, 0.5, -0.4)
    neck = [(-0.8, 0.2), (-1.4, 1.2)]
    head = chain(quad((-1.0, 0.4), (-1.4, 1.6), (-2.0, 1.2), 12), quad((-2.0, 1.2), (-2.8, 0.6), (-2.6, 0.2), 12), quad((-2.6, 0.2), (-2.0, 0.0), (-1.4, 0.2), 10))
    ears = [lens((-1.5, 1.4), (-1.2, 2.8), 0.25), lens((-1.3, 1.3), (-0.6, 2.5), 0.25)]
    mane = zigzag(-1.2, -0.6, 0.8, 0.12, 3)
    basket = [rect(0.0, 0.4, 1.0, 1.2), rect(0.4, 0.5, 1.4, 1.1)]
    return make("Donkey", b + [neck, head, mane, ground(-2.1)] + ears + basket, [eye(-1.9, 1.0, 0.08)])


@design("rooster", T)
def rooster(rng):
    body = chain(cubic((-0.4, 1.0), (-1.6, 0.8), (-1.4, -1.2), (0.2, -1.2), 30), quad((0.2, -1.2), (1.4, -0.8), (1.2, 0.4), 16))
    tail = [quad((1.0, 0.2), (2.2, 2.4), (2.8, 1.6)), quad((1.1, 0.0), (2.6, 1.6), (3.0, 0.6)), quad((1.2, -0.3), (2.6, 0.4), (2.8, -0.4))]
    head = circle(-0.5, 1.4, 0.5, 30)
    comb = [arc(-0.7 + 0.3 * k, 1.95, 0.18, 0, math.pi, 8) for k in range(3)]
    beak = poly((-1.0, 1.55), (-1.6, 1.8), (-1.0, 1.3), closed=False)
    wattle = lens((-0.95, 1.2), (-0.9, 0.7), 0.4)
    fence = [[(-3.0, -1.4), (3.0, -1.4)], [(-3.0, -2.2), (3.0, -2.2)], [(-2.2, -2.8), (-2.2, -1.2)], [(2.2, -2.8), (2.2, -1.2)]]
    sun = arc(-2.2, 2.2, 0.7, 0, 2 * math.pi, 30)
    notes = [[(-2.0, 0.6), (-2.6, 0.9)], [(-2.0, 0.3), (-2.7, 0.3)]]
    return make("Crowing Rooster", [body, head, beak, wattle, sun] + tail + comb + fence + notes, [eye(-0.6, 1.5, 0.07)])


@design("farm_ducks", T)
def farm_ducks(rng):
    pond = ellipse(0, -1.4, 3.2, 1.2, 100)
    ducks = []
    for x, y, s in [(-1.2, -1.0, 1.0), (0.6, -1.4, 0.7), (1.6, -1.2, 0.6)]:
        ducks += [transform(p, dx=x, dy=y, s=s) for p in [chain(quad((-0.6, 0.0), (0, -0.4), (0.8, 0.0)), quad((0.8, 0.0), (0.4, 0.4), (-0.1, 0.3))),
                                                           circle(-0.4, 0.55, 0.3, 16), poly((-0.7, 0.6), (-1.0, 0.5), (-0.7, 0.45), closed=False)]]
    reeds = [quad((x, -0.4), (x + 0.2, 1.0), (x + 0.1, 2.0)) for x in (-2.8, -2.4, 2.6)] + [ellipse(-2.3, 1.8, 0.1, 0.3, 10)]
    return make("Duck Pond", [pond] + ducks + reeds)


@design("rabbit_hutch", T)
def rabbit_hutch(rng):
    hutch = [rect(-2.6, -0.8, 2.6, 1.6), poly((-2.9, 1.5), (0, 2.6), (2.9, 1.5), closed=False)]
    mesh = [rect(-2.2, -0.4, 0.2, 1.2)] + [[(x, -0.4), (x, 1.2)] for x in (-1.6, -1.0, -0.4)] + [[(-2.2, 0.4), (0.2, 0.4)]]
    door = [rect(0.6, -0.4, 2.2, 1.2), circle(2.0, 0.4, 0.08, 8)]
    legs = [[(-2.4, -0.8), (-2.4, -2.4)], [(2.4, -0.8), (2.4, -2.4)]]
    bunny = [circle(-1.0, 0.1, 0.4, 20), lens((-1.1, 0.4), (-1.3, 1.1), 0.3), lens((-0.9, 0.4), (-0.7, 1.1), 0.3)]
    carrot = [poly((1.2, -1.6), (2.2, -1.4), (1.2, -1.3)), lens((1.2, -1.45), (0.8, -1.0), 0.3)]
    return make("Rabbit Hutch", hutch + mesh + door + legs + bunny + carrot)


@design("llama", T)
def llama(rng):
    body = ellipse(0.6, -0.4, 1.6, 0.8, 70)
    neck = tube([(-0.6, -0.2), (-1.0, 2.0)], 0.7, cap=False)
    head = ellipse(-1.2, 2.3, 0.6, 0.4, 30)
    ears = [lens((-1.0, 2.6), (-0.9, 3.4), 0.3), lens((-0.7, 2.6), (-0.4, 3.3), 0.3)]
    legs = [leg(x, x + 0.3, -0.7, -2.6) for x in (-0.6, -0.1, 1.2, 1.7)]
    blanket = [poly((0.0, 0.4), (1.4, 0.4), (1.6, -0.6), (-0.2, -0.6)), zigzag(-0.2, 1.6, -0.3, 0.12, 5)]
    tail = [arc(2.2, 0.0, 0.25, math.radians(-60), math.radians(120), 8)]
    return make("Llama", [body, neck, head] + ears + legs + blanket + tail, [eye(-1.4, 2.4, 0.07)])


@design("sow_piglets", T)
def sow_piglets(rng):
    sow = ellipse(-0.6, 0.4, 2.2, 1.2, 100)
    head = [circle(-2.6, 0.8, 0.8, 50), ellipse(-3.1, 0.6, 0.35, 0.28, 20), poly((-2.6, 1.5), (-2.8, 2.1), (-2.2, 1.6), closed=False)]
    piglets = []
    for x in (0.6, 1.6, 2.6):
        piglets += [ellipse(x, -1.6, 0.5, 0.35, 24), circle(x - 0.5, -1.45, 0.25, 14), spiral(x + 0.6, -1.4, 0.03, 0.12, 1.2, 12)]
    sow_legs = [leg(x, x + 0.4, -0.5, -1.0) for x in (-2.0, 0.6)]
    return make("Mama Pig and Piglets", [sow] + head + piglets + sow_legs + [ground(-2.0)], [eye(-2.8, 1.0, 0.08)])


@design("calf", T)
def calf(rng):
    b = quad_body(2.4, 1.1, 0.4, -0.2, leg_h=1.8)
    head = [ellipse(-1.4, 0.8, 0.6, 0.7, 40), ellipse(-1.5, 0.3, 0.4, 0.3, 24)]
    ears = [lens((-1.0, 1.2), (-0.4, 1.4), 0.4), lens((-1.8, 1.2), (-2.4, 1.4), 0.4)]
    spots = [ellipse(0.6, 0.0, 0.4, 0.3, 20), ellipse(1.2, -0.3, 0.25, 0.2, 14)]
    flower = [circle(-2.2, -1.6, 0.15, 10), [(-2.2, -1.75), (-2.2, -2.4)]]
    return make("Spotted Calf", b + head + ears + spots + flower + [ground(-2.4)], [eye(-1.6, 0.95, 0.08)])


@design("cow_side", T)
def cow_side(rng):
    b = quad_body(3.4, 1.6, 0.4, -0.2)
    head = chain(quad((-1.2, 0.6), (-2.4, 1.0), (-2.6, 0.2), 12), quad((-2.6, 0.2), (-2.6, -0.6), (-2.0, -0.6), 10), [(-1.3, -0.4)])
    horn = quad((-1.8, 0.85), (-1.7, 1.4), (-1.4, 1.5))
    udder = [chain(arc(0.8, -1.0, 0.4, math.radians(200), math.radians(340), 10))]
    spots = [ellipse(-0.4, 0.2, 0.5, 0.35, 24), ellipse(1.0, -0.1, 0.4, 0.3, 20)]
    grass = [zigzag(-3.2, 3.2, -2.6, 0.15, 14)]
    return make("Grazing Cow", b + [head, horn] + udder + spots + grass, [eye(-2.1, 0.5, 0.08)])


@design("horse_side", T)
def horse_side(rng):
    b = quad_body(3.2, 1.3, 0.6, -0.2, leg_h=2.0)
    neck = tube([(-0.9, 0.2), (-1.6, 1.6)], 0.8, cap=False)
    head = chain(quad((-1.3, 1.9), (-2.6, 1.8), (-2.8, 1.0), 12), quad((-2.8, 1.0), (-2.4, 0.9), (-1.9, 1.2), 10))
    ear = poly((-1.5, 1.9), (-1.4, 2.4), (-1.2, 1.9), closed=False)
    mane = [quad((-1.3, 1.9), (-1.0, 1.0), (-0.6, 0.4))]
    tail_ = [quad((2.2, 0.3), (2.9, -0.6), (2.6, -1.6)), quad((2.2, 0.1), (2.7, -0.8), (2.3, -1.6))]
    return make("Horse", b + [head, ear] + [neck] + mane + tail_ + [ground(-2.5)], [eye(-1.9, 1.6, 0.08)])


@design("pony", T)
def pony(rng):
    b = quad_body(2.4, 1.1, 0.4, -0.6, leg_h=1.3)
    head = [ellipse(-1.5, 0.5, 0.75, 0.45, 30, rot=-0.6)]
    fringe = zigzag(-1.6, -1.0, 1.0, 0.15, 3)
    mane = [quad((-1.0, 0.9), (-0.6, 0.4), (-0.6, 0.0))]
    ear = poly((-1.3, 1.0), (-1.2, 1.5), (-1.0, 1.0), closed=False)
    saddle = [chain(arc(0.3, -0.05, 0.6, 0, math.pi, 16)), [(0.3, -0.1), (0.3, -0.9)]]
    return make("Little Pony", b + head + [fringe, ear] + mane + saddle + [ground(-2.0)], [eye(-1.6, 0.6, 0.07)])


@design("foal", T)
def foal(rng):
    body = ellipse(0.4, 0.0, 1.2, 0.6, 50)
    legs = [[(x, -0.4), (x - 0.1, -2.4)] for x in (-0.4, 0.0, 0.8, 1.2)]
    neck = tube([(-0.5, 0.2), (-1.0, 1.4)], 0.5, cap=False)
    head = ellipse(-1.3, 1.6, 0.6, 0.35, 30, rot=-0.4)
    ears = [poly((-1.0, 1.85), (-0.9, 2.3), (-0.75, 1.85), closed=False)]
    tail = quad((1.5, 0.2), (2.0, 0.0), (2.0, -0.6))
    flowers = [circle(x, -2.2, 0.15, 10) for x in (-2.4, 1.8, 2.6)]
    return make("Newborn Foal", [body, neck, head, tail] + legs + ears + flowers + [ground(-2.4)], [eye(-1.4, 1.7, 0.06)])


@design("chicks", T)
def chicks(rng):
    out = []
    for x, y, s in [(-1.8, -0.6, 1.0), (0.0, -0.4, 1.1), (1.8, -0.7, 0.9)]:
        out += [transform(p, dx=x, dy=y, s=s) for p in [circle(0, 0, 0.8, 40), circle(0, 1.0, 0.5, 30), poly((-0.5, 1.0), (-0.85, 0.9), (-0.5, 0.8), closed=False),
                                                        quad((0.3, 0.1), (0.8, 0.3), (0.6, -0.2)), [(-0.2, -0.8), (-0.3, -1.1)], [(0.2, -0.8), (0.3, -1.1)]]]
    seeds = [ellipse(x, -2.2, 0.1, 0.06, 8) for x in (-2.4, -1.0, 0.8, 2.4)]
    return make("Fluffy Chicks", out + seeds, [eye(-1.95, 0.45, 0.06), eye(-0.15, 0.7, 0.06), eye(1.65, 0.2, 0.06)])


@design("chicken_coop", T)
def chicken_coop(rng):
    house = [poly((-2.0, -1.0), (2.0, -1.0), (2.0, 1.2), (0, 2.4), (-2.0, 1.2))]
    roof = [poly((-2.4, 1.0), (0, 2.8), (2.4, 1.0), closed=False)]
    door = [rect(-0.6, -1.0, 0.6, 0.6)]
    ramp = [[(-0.6, -1.0), (-2.4, -2.6)], [(0.6, -1.0), (-1.2, -2.6)]] + [[(-0.6 - 0.4 * k, -1.35 - 0.35 * k), (0.2 - 0.4 * k, -1.35 - 0.35 * k)] for k in range(3)]
    stilts = [[(-1.8, -1.0), (-1.8, -2.6)], [(1.8, -1.0), (1.8, -2.6)]]
    window = [circle(0, 1.4, 0.35, 20)]
    hen = [ellipse(2.6, -2.2, 0.6, 0.4, 24), circle(2.1, -1.7, 0.25, 14), arc(2.1, -1.4, 0.1, 0, math.pi, 6)]
    return make("Chicken Coop", house + roof + door + ramp + stilts + window + hen)


@design("hay_bales", T)
def hay_bales(rng):
    round_ = [circle(-1.4, -1.0, 1.4, 70), spiral(-1.4, -1.0, 0.1, 1.2, 3.0, 120)]
    square = [rect(0.6, -2.4, 3.0, -1.2), rect(1.0, -1.2, 2.8, 0.0), [(0.6, -1.8), (3.0, -1.8)], [(1.0, -0.6), (2.8, -0.6)]]
    straws = [[(x, -1.2), (x + 0.1, -1.4)] for x in (1.2, 1.8, 2.4)]
    return make("Hay Bales", round_ + square + straws + [ground(-2.4)])


@design("pitchfork", T)
def pitchfork(rng):
    handle = [[(-0.1, -3.2), (-0.1, 1.2)], [(0.1, -3.2), (0.1, 1.2)]]
    head = [quad((-1.0, 2.6), (-1.0, 1.2), (0, 1.2)), quad((1.0, 2.6), (1.0, 1.2), (0, 1.2)), [(0, 1.2), (0, 3.0)], [(-0.5, 1.4), (-0.5, 2.8)], [(0.5, 1.4), (0.5, 2.8)]]
    hay = [quad((-3.0, -3.2), (-2.0, -0.6), (-1.0, -3.2)), quad((1.0, -3.2), (2.0, -1.0), (3.2, -3.2))] + [[(x, -3.2), (x + 0.2, -1.8)] for x in (-2.4, -1.8, 1.6, 2.4)]
    return make("Pitchfork and Hay", handle + head + hay)


@design("hay_wagon", T)
def hay_wagon(rng):
    bed = [rect(-2.8, -0.8, 2.6, -0.2)]
    hay = [chain(quad((-2.8, -0.2), (-2.6, 1.6), (-0.2, 1.8)), quad((-0.2, 1.8), (2.4, 1.6), (2.6, -0.2)))] + [[(x, 0.4), (x + 0.3, 1.2)] for x in (-1.8, -0.6, 0.6, 1.6)]
    wheels = []
    for x in (-1.8, 1.6):
        wheels += [circle(x, -1.4, 0.8, 40), circle(x, -1.4, 0.15, 10)] + [[(x, -1.4), (x + 0.8 * math.cos(a), -1.4 + 0.8 * math.sin(a))] for a in [k * math.pi / 3 for k in range(6)]]
    tongue = [(2.6, -0.6), (3.4, -1.2)]
    return make("Hay Wagon", bed + hay + wheels + [tongue])


@design("water_pump", T)
def water_pump(rng):
    body = [rect(-0.5, -2.0, 0.5, 1.2), poly((-0.6, 1.2), (0.6, 1.2), (0.4, 1.8), (-0.4, 1.8))]
    spout = [poly((0.5, 0.6), (1.6, 0.4), (1.6, 0.0), (0.5, 0.1), closed=False)]
    handle = [[(-0.4, 1.6), (-2.2, 2.6)], circle(-2.3, 2.65, 0.15, 10)]
    bucket = [poly((1.0, -2.6), (1.2, -1.2), (2.4, -1.2), (2.6, -2.6)), arc(1.8, -1.2, 0.6, 0, math.pi, 12)]
    drops = [lens((1.5, -0.2), (1.5, -0.6), 0.4), lens((1.7, -0.8), (1.7, -1.1), 0.4)]
    base = [rect(-1.0, -2.6, 1.0, -2.0)]
    return make("Old Water Pump", body + spout + handle + bucket + drops + base)


@design("silo", T)
def silo(rng):
    tower = [rect(-0.9, -2.8, 0.9, 1.6), chain(arc(0, 1.6, 0.9, 0, math.pi, 20))]
    bands = [[(-0.9, y), (0.9, y)] for y in (-1.6, -0.4, 0.8)]
    barn = [poly((1.0, -2.8), (1.0, -0.2), (2.2, 0.8), (3.4, -0.2), (3.4, -2.8)), rect(1.8, -2.8, 2.6, -1.4)]
    ladder = [[(-0.6, -2.8), (-0.6, 1.4)], [(-0.3, -2.8), (-0.3, 1.4)]] + [[(-0.6, y), (-0.3, y)] for y in (-2.2, -1.0, 0.2)]
    return make("Grain Silo", tower + bands + barn + ladder + [ground(-2.8)])


@design("farmhouse", T)
def farmhouse(rng):
    house = [rect(-2.4, -2.4, 1.6, 0.6), poly((-2.8, 0.4), (-0.4, 2.2), (2.0, 0.4), closed=False)]
    porch = [rect(-2.6, -2.6, 2.4, -2.4), [(-2.4, -0.6), (1.6, -0.6)], [(-2.0, -2.4), (-2.0, -0.6)], [(1.2, -2.4), (1.2, -0.6)]]
    door = [rect(-0.8, -2.4, 0.0, -1.0)]
    windows = [rect(-2.0, -0.2, -1.2, 0.4), rect(0.4, -0.2, 1.2, 0.4), rect(0.4, -1.8, 1.0, -1.0)]
    chimney = [rect(1.0, 1.0, 1.4, 2.0)]
    tree = [[(2.8, -2.6), (2.8, -0.6)], circle(2.8, 0.4, 0.9, 40)]
    return make("Farmhouse", house + porch + door + windows + chimney + tree)


@design("farm_gate", T)
def farm_gate(rng):
    posts = [rect(-3.0, -2.6, -2.6, 1.0), rect(2.6, -2.6, 3.0, 1.0)]
    bars = [[(-2.6, y), (2.6, y)] for y in (-2.0, -1.2, -0.4, 0.4)] + [[(-2.6, -2.0), (2.6, 0.4)], [(0.0, -2.0), (0.0, 0.4)]]
    hills = [quad((-3.4, -0.2), (-1.0, 1.6), (1.2, 0.6)), quad((0.6, 0.8), (2.2, 2.0), (3.4, 1.0))]
    sun = arc(0, 2.6, 0.6, 0, 2 * math.pi, 24)
    return make("Farm Gate", posts + bars + hills + [sun])


@design("wheat_sheaf", T)
def wheat_sheaf(rng):
    stalks = [[(0, -1.0), (x, 2.4)] for x in (-1.4, -0.7, 0.0, 0.7, 1.4)] + [[(0, -1.0), (x, -3.0)] for x in (-0.8, -0.3, 0.3, 0.8)]
    heads = []
    for x in (-1.4, -0.7, 0.0, 0.7, 1.4):
        for k in range(4):
            heads += [lens((x * (1 - 0.06 * k), 2.4 - 0.0 + 0.3 * k), (x * (1 - 0.06 * k) - 0.25, 2.65 + 0.3 * k), 0.4),
                      lens((x * (1 - 0.06 * k), 2.4 + 0.3 * k), (x * (1 - 0.06 * k) + 0.25, 2.65 + 0.3 * k), 0.4)]
    tie = [quad((-0.6, -0.9), (0, -1.2), (0.6, -0.9)), lens((0, -1.0), (-0.8, -1.6), 0.4), lens((0, -1.0), (0.8, -1.6), 0.4)]
    return make("Wheat Sheaf", stalks + heads + tie)


@design("apple_tree", T)
def apple_tree(rng):
    trunk = [quad((-0.4, -2.8), (-0.2, -1.0), (-0.8, 0.0)), quad((0.4, -2.8), (0.2, -1.0), (0.9, 0.2))]
    crown = polar(lambda t: 2.0 + 0.2 * math.sin(7 * t), n=300, cy=1.2)
    apples = [circle(x, y, 0.25, 16) for x, y in [(-1.0, 1.6), (0.4, 2.2), (1.2, 1.0), (-0.4, 0.6), (1.4, 2.0), (-1.4, 0.4)]]
    basket = [chain([(1.6, -2.8), (1.8, -2.0), (3.0, -2.0), (3.2, -2.8)]), arc(2.4, -2.0, 0.6, 0, math.pi, 12)]
    fallen = [circle(-1.8, -2.6, 0.22, 14)]
    return make("Apple Tree", trunk + [crown] + apples + basket + fallen + [ground(-2.8)])


@design("orchard_ladder", T)
def orchard_ladder(rng):
    rails = [[(-1.4, -2.8), (-0.4, 2.6)], [(1.4, -2.8), (0.4, 2.6)]]
    rungs = [[(-1.4 + 0.18 * k * 1.0 + 0.0, -2.2 + 0.9 * k), (1.4 - 0.18 * k, -2.2 + 0.9 * k)] for k in range(5)]
    leg = [[(0, 2.6), (2.6, -2.8)]]
    branch = [quad((-3.2, 3.0), (0, 2.4), (3.2, 3.2))] + [circle(x, 2.4, 0.22, 14) for x in (-1.8, 1.4, 2.4)]
    return make("Orchard Ladder", rails + rungs + leg + branch)


@design("veggie_rows", T)
def veggie_rows(rng):
    rows = [quad((-3.4, y), (0, y + 0.3), (3.4, y)) for y in (-2.6, -1.2, 0.2)]
    cabbages = [circle(x, -2.2, 0.4, 24) for x in (-2.4, -1.0, 0.4, 1.8)] + [arc(x, -2.2, 0.25, 0, math.pi, 8) for x in (-2.4, -1.0, 0.4, 1.8)]
    carrots = [lens((x, -0.8), (x - 0.3, -0.2), 0.3) for x in (-2.6, -1.6, -0.6, 0.4, 1.4, 2.4)] + [lens((x, -0.8), (x + 0.3, -0.2), 0.3) for x in (-2.6, -1.6, -0.6, 0.4, 1.4, 2.4)]
    beans = [[(x, 0.4), (x, 2.4)] for x in (-2.0, 0.0, 2.0)] + [spiral(x, 1.4, 0.1, 0.5, 1.5, 30) for x in (-2.0, 0.0, 2.0)]
    return make("Vegetable Rows", rows + cabbages + carrots + beans)


@design("milking_stool", T)
def milking_stool(rng):
    seat = [ellipse(-1.0, 0.0, 1.2, 0.35, 40)]
    legs = [[(-1.8, -0.2), (-2.2, -2.6)], [(-0.2, -0.2), (0.2, -2.6)], [(-1.0, -0.3), (-1.0, -2.6)]]
    pail = [poly((0.8, -2.6), (0.6, -0.6), (2.6, -0.6), (2.4, -2.6)), ellipse(1.6, -0.6, 1.0, 0.2, 30), arc(1.6, -0.6, 1.0, 0, math.pi, 16)]
    milk = [wave(0.7, 2.5, -0.9, 0.05, 2, 20)]
    return make("Milking Stool and Pail", seat + legs + pail + milk + [ground(-2.6)])


@design("farmer_hat", T)
def farmer_hat(rng):
    brim = ellipse(0, -0.4, 3.0, 0.7, 120)
    crown = chain(arc(0, -0.2, 1.4, math.radians(10), math.radians(170), 30))
    weave = [[(x, -0.15), (x * 0.9, 1.0 - 0.1 * abs(x))] for x in (-0.8, 0.0, 0.8)]
    band = quad((-1.38, 0.05), (0, -0.2), (1.38, 0.05))
    overalls = [rect(-1.0, -3.2, 1.0, -1.6), [(-0.8, -1.6), (-1.2, -1.2)], [(0.8, -1.6), (1.2, -1.2)], rect(-0.4, -2.4, 0.4, -1.9)]
    return make("Farmer's Straw Hat", [brim, crown, band] + weave + overalls)


@design("egg_carton", T)
def egg_carton(rng):
    tray = [rect(-3.0, -2.0, 3.0, -1.0)] + [arc(x, -1.0, 0.45, math.pi, 2 * math.pi, 10) for x in (-2.4, -1.2, 0.0, 1.2, 2.4)]
    lid = [poly((-3.0, -1.0), (-3.0, 0.2), (3.0, 1.6), (3.0, -1.0), closed=False)]
    eggs = [ellipse(x, -0.6, 0.4, 0.55, 30) for x in (-2.4, -1.2, 0.0, 1.2)]
    cracked = [chain(arc(2.4, -0.8, 0.4, math.radians(-30), math.radians(210), 14)), zigzag(2.0, 2.8, -0.75, 0.1, 3)]
    return make("Egg Carton", tray + lid + eggs + cracked)


@design("butter_churn", T)
def butter_churn(rng):
    churn = [poly((-1.2, -2.8), (-0.9, 1.0), (0.9, 1.0), (1.2, -2.8)), ellipse(0, 1.0, 0.95, 0.2, 30)]
    bands = [quad((-1.1, -2.2), (0, -2.35), (1.1, -2.2)), quad((-0.98, 0.4), (0, 0.25), (0.98, 0.4))]
    dasher = [[(0, 1.0), (0, 3.2)], [(-0.4, 3.2), (0.4, 3.2)]]
    butter = [rect(1.8, -2.8, 3.2, -2.0), [(1.8, -2.0), (2.2, -1.6), (3.6, -1.6), (3.2, -2.0)]]
    return make("Butter Churn", churn + bands + dasher + butter)


@design("cheese_wheel", T)
def cheese_wheel(rng):
    wheel = [ellipse(-0.6, 0.6, 2.2, 0.7, 80), ellipse(-0.6, -0.8, 2.2, 0.7, 80), [(-2.8, 0.6), (-2.8, -0.8)], [(1.6, 0.6), (1.6, -0.8)]]
    wedge = [poly((1.0, -1.6), (3.2, -1.2), (3.2, -2.2), (1.0, -2.6)), [(1.0, -1.6), (3.2, -2.2)]]
    holes = [ellipse(x, y, 0.2, 0.1, 12) for x, y in [(-1.4, 0.6), (-0.2, 0.8), (0.6, 0.4)]] + [circle(2.4, -1.9, 0.12, 10)]
    knife = [[(-2.6, -2.4), (-0.6, -2.0)], rrect(-3.4, -2.6, -2.6, -2.3, 0.1)]
    return make("Cheese Wheel", wheel + wedge + holes + knife)


@design("farm_stand", T)
def farm_stand(rng):
    roof = poly((-3.0, 1.6), (0, 2.6), (3.0, 1.6))
    posts = [[(-2.6, 1.6), (-2.6, -2.6)], [(2.6, 1.6), (2.6, -2.6)]]
    table = [rect(-2.8, -0.8, 2.8, -0.5)]
    crates = [rect(-2.4, -0.5, -0.8, 0.4), rect(-0.6, -0.5, 0.8, 0.4), rect(1.0, -0.5, 2.4, 0.4)]
    produce = [circle(x, 0.6, 0.25, 14) for x in (-2.0, -1.4, 1.4, 2.0)] + [lens((0.1, 0.4), (0.0, 1.2), 0.3)]
    sign = [rect(-1.4, 0.9, 1.4, 1.5)]
    return make("Farm Stand", [roof] + posts + table + crates + produce + sign)


@design("tire_swing", T)
def tire_swing(rng):
    branch = [quad((-3.2, 2.6), (0, 2.2), (3.0, 2.8))]
    rope = [(0.2, 2.35), (0.2, -0.2)]
    tire = [ellipse(0.2, -1.0, 1.2, 0.9, 60), ellipse(0.2, -1.0, 0.6, 0.45, 40)]
    trunk = [[(-2.6, 2.5), (-2.6, -3.0)], [(-2.0, 2.4), (-2.0, -3.0)]]
    grass = [zigzag(-3.2, 3.2, -3.0, 0.15, 14)]
    return make("Tire Swing", branch + [rope] + tire + trunk + grass)


@design("sheep_face", T)
def sheep_face(rng):
    wool = polar(lambda t: 2.0 + 0.18 * math.sin(12 * t), n=300, cy=0.8)
    face = chain(cubic((-0.8, 1.2), (-1.2, -0.6), (-0.6, -1.6), (0, -1.6), 20), cubic((0, -1.6), (0.6, -1.6), (1.2, -0.6), (0.8, 1.2), 20), quad((0.8, 1.2), (0, 1.6), (-0.8, 1.2), 10))
    ears = [lens((-0.9, 0.6), (-2.0, 0.2), 0.35), lens((0.9, 0.6), (2.0, 0.2), 0.35)]
    nose = [poly((-0.2, -1.0), (0.2, -1.0), (0, -1.25)), quad((-0.3, -1.4), (0, -1.5), (0.3, -1.4))]
    return make("Sheep Face", [wool, face] + ears + nose, [eye(-0.4, 0.2, 0.12), eye(0.4, 0.2, 0.12)])


@design("piglet_face", T)
def piglet_face(rng):
    face = circle(0, 0, 2.0, 120)
    ears = [poly((-1.4, 1.4), (-2.0, 2.6), (-0.6, 1.9)), poly((1.4, 1.4), (2.0, 2.6), (0.6, 1.9))]
    snout = [ellipse(0, -0.6, 0.9, 0.6, 40), ellipse(-0.3, -0.6, 0.14, 0.22, 12), ellipse(0.3, -0.6, 0.14, 0.22, 12)]
    cheeks = [circle(-1.3, -0.6, 0.3, 16), circle(1.3, -0.6, 0.3, 16)]
    smile = arc(0, -1.0, 0.6, math.radians(220), math.radians(320), 12)
    return make("Piglet Face", [face, smile] + ears + snout + cheeks, [eye(-0.7, 0.5, 0.14), eye(0.7, 0.5, 0.14)])


@design("lantern", T)
def lantern(rng):
    frame = [poly((-1.0, -2.4), (1.0, -2.4), (0.8, 1.0), (-0.8, 1.0)), rect(-1.2, -2.8, 1.2, -2.4)]
    glass = [ellipse(0, -0.7, 0.6, 1.2, 40)]
    flame = [lens((0, -1.4), (0, -0.2), 0.4)]
    top = [poly((-0.9, 1.0), (0, 1.8), (0.9, 1.0)), arc(0, 2.0, 0.5, 0, math.pi, 14)]
    rays = [[(1.4 * math.cos(a), -0.7 + 1.4 * math.sin(a)), (2.0 * math.cos(a), -0.7 + 2.0 * math.sin(a))] for a in [math.radians(d) for d in (0, 30, 150, 180, 210, 330)]]
    return make("Barn Lantern", frame + glass + flame + top + rays)


@design("stable_horse", T)
def stable_horse(rng):
    stable = [rect(-2.8, -2.8, 2.8, 1.6), poly((-3.2, 1.4), (0, 2.8), (3.2, 1.4), closed=False)]
    door = [rect(-1.6, -2.8, 1.6, -0.6), [(-1.6, -2.8), (1.6, -0.6)], [(-1.6, -0.6), (1.6, -2.8)]]
    head = [chain(quad((-0.6, -0.6), (-0.8, 1.0), (0.0, 1.6)), quad((0.0, 1.6), (0.9, 1.0), (0.6, -0.6))), ellipse(0, -0.3, 0.6, 0.35, 20),
            poly((-0.4, 1.5), (-0.5, 2.0), (-0.2, 1.6), closed=False), poly((0.4, 1.5), (0.5, 2.0), (0.2, 1.6), closed=False)]
    blaze = [quad((0, 1.4), (-0.1, 0.4), (0, -0.1))]
    return make("Horse in the Stable", stable + door + head + blaze, [eye(-0.4, 0.8, 0.08), eye(0.4, 0.8, 0.08)])


@design("field_mouse", T)
def field_mouse(rng):
    stalk = [quad((0.6, -3.0), (0.8, 0.0), (0.4, 2.6))] + [lens((0.4 + 0.02 * k, 1.6 + 0.3 * k), (0.1, 1.9 + 0.3 * k), 0.4) for k in range(3)] + \
            [lens((0.4 + 0.02 * k, 1.6 + 0.3 * k), (0.7, 1.9 + 0.3 * k), 0.4) for k in range(3)]
    mouse = [ellipse(0.2, 0.2, 0.7, 0.9, 30), circle(0.0, 1.2, 0.45, 24), circle(-0.35, 1.6, 0.25, 14), circle(0.35, 1.6, 0.25, 14),
             quad((0.5, -0.5), (1.6, -1.4), (1.0, -2.4))]
    paws = [ellipse(0.5, 0.5, 0.2, 0.12, 10), ellipse(0.5, 0.2, 0.2, 0.12, 10)]
    return make("Harvest Mouse", stalk + mouse + paws, [eye(-0.1, 1.25, 0.07)])


@design("cow_bell", T)
def cow_bell(rng):
    strap = [chain(arc(0, 1.6, 1.6, math.radians(-20), math.radians(200), 40)), chain(arc(0, 1.6, 1.3, math.radians(-20), math.radians(200), 40))]
    bell = chain(quad((-0.8, 0.8), (-1.2, -1.2), (-1.6, -2.0), 12),
                 [(1.6, -2.0)], quad((1.6, -2.0), (1.2, -1.2), (0.8, 0.8), 12), [(-0.8, 0.8)])
    clapper = [[(0, -1.4), (0, -2.3)], circle(0, -2.45, 0.18, 12)]
    flowers = [circle(x, -2.6, 0.2, 12) for x in (-2.6, 2.6)]
    return make("Cow Bell", strap + [bell] + clapper + flowers)


@design("chicken_feed", T)
def chicken_feed(rng):
    scoop = [poly((-2.8, 1.4), (-1.0, 1.4), (-0.6, 0.4), (-2.6, 0.4)), [(-0.8, 0.9), (0.4, 1.4)]]
    seeds = [ellipse(x, y, 0.1, 0.06, 8) for x, y in [(-1.0, 0.0), (-0.6, -0.5), (-1.2, -0.9), (-0.4, -1.4), (-0.9, -1.8)]]
    hen = [ellipse(1.6, -1.6, 1.0, 0.7, 40), circle(0.7, -1.1, 0.4, 24), poly((0.35, -1.15), (0.0, -1.4), (0.35, -1.3), closed=False),
           arc(0.7, -0.75, 0.12, 0, math.pi, 6), quad((2.4, -1.4), (3.0, -0.8), (2.9, -0.4))]
    return make("Feeding the Chickens", scoop + seeds + hen + [ground(-2.4)], [eye(0.65, -1.0, 0.06)])


@design("farm_sunrise", T)
def farm_sunrise(rng):
    sun = [arc(0, 0.0, 1.4, 0, math.pi, 40)] + [[(1.7 * math.cos(a), 1.7 * math.sin(a)), (2.4 * math.cos(a), 2.4 * math.sin(a))] for a in [k * math.pi / 8 for k in range(1, 8)]]
    rows = [[(-3.4, 0.0), (3.4, 0.0)]] + [[(0, 0.0), (x, -3.0)] for x in (-3.2, -2.0, -0.8, 0.8, 2.0, 3.2)]
    barn = [poly((2.2, 0.0), (2.2, 0.8), (2.6, 1.2), (3.0, 0.8), (3.0, 0.0), closed=False)]
    return make("Farm Sunrise", sun + rows + barn)


@design("country_mailbox", T)
def country_mailbox(rng):
    box = [chain([(-1.8, 0.0), (-1.8, 1.0)], arc(-0.4, 1.0, 1.4, math.pi, 0, 30), [(1.0, 0.0), (-1.8, 0.0)]), [(-0.4, 0.0), (-0.4, -2.8)]]
    flag = [[(1.0, 0.4), (1.6, 0.4), (1.6, 1.6)], rect(1.6, 1.0, 2.4, 1.6)]
    sunflowers = []
    for x, y in [(-2.4, -1.0), (2.2, -1.4)]:
        sunflowers += [circle(x, y, 0.3, 16)] + [lens((x + 0.3 * math.cos(a), y + 0.3 * math.sin(a)), (x + 0.7 * math.cos(a), y + 0.7 * math.sin(a)), 0.35) for a in [k * math.pi / 4 for k in range(8)]] + [[(x, y - 0.3), (x, -2.8)]]
    return make("Country Mailbox", box + flag + sunflowers + [ground(-2.8)])
