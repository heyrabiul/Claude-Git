"""Ocean Life niche, part 2 (pictures 11-50)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "ocean"


def fish(L=4.0, H=1.6, tail="fork", nose=0.0, belly=1.0):
    """Generic fish outline: length L, height H, tail style."""
    x0, x1 = -L / 2, L / 2 - 0.8
    top = cubic((x0 - nose, 0), (x0 + 0.3, H * 0.9), (x1 - 0.6, H * 0.8), (x1, 0.15), 40)
    bot = cubic((x1, -0.15), (x1 - 0.6, -H * 0.8 * belly), (x0 + 0.3, -H * 0.9 * belly), (x0 - nose, 0), 40)
    if tail == "fork":
        t = [(x1 + 0.9, H * 0.6), (x1 + 0.55, 0.0), (x1 + 0.9, -H * 0.6)]
    elif tail == "round":
        t = arc(x1 + 0.45, 0, 0.55, math.radians(110), math.radians(-110), 20)
    else:  # crescent
        t = [(x1 + 0.6, H * 0.8), (x1 + 0.3, 0.0), (x1 + 0.6, -H * 0.8)]
    return chain(top, t, bot)


@design("turtle_swim", T)
def turtle_swim(rng):
    shell = ellipse(0, 0, 1.8, 1.4, 120)
    plates = [poly(*[(0.5 * math.cos(a), 0.5 * math.sin(a)) for a in [k * math.pi / 3 for k in range(6)]])] + \
             [[(0.5 * math.cos(a), 0.5 * math.sin(a)), (1.45 * math.cos(a), 1.1 * math.sin(a))] for a in [k * math.pi / 3 for k in range(6)]]
    head = ellipse(2.4, 0, 0.6, 0.45, 30)
    flips = [lens((1.0, 1.0), (2.2, 2.4), 0.3), lens((1.0, -1.0), (2.2, -2.4), 0.3), lens((-1.2, 0.9), (-2.0, 1.6), 0.3), lens((-1.2, -0.9), (-2.0, -1.6), 0.3)]
    return Design("Swimming Sea Turtle", [shell, head] + plates + flips, [eye(2.6, 0.15, 0.07), eye(2.6, -0.15, 0.07)], T)


@design("clownfish", T)
def clownfish(rng):
    body = fish(4.2, 1.5, "round")
    bands = [quad((x, 1.2 - abs(x) * 0.2), (x + 0.3, 0), (x, -1.2 + abs(x) * 0.2)) for x in (-1.0, 0.2, 1.1)]
    fin = arc(0, 1.0, 0.8, math.radians(20), math.radians(160), 16)
    anemone = [quad((x, -2.6), (x + 0.3, -1.9), (x - 0.1, -1.4)) for x in (-1.6, -1.0, -0.4, 0.2, 0.8, 1.4)]
    return Design("Clownfish", [body, fin] + bands + anemone, [eye(-1.5, 0.3, 0.12)], T)


@design("pufferfish", T)
def pufferfish(rng):
    body = circle(0, 0, 1.8, 120)
    spikes = [poly((1.8 * math.cos(a - 0.08), 1.8 * math.sin(a - 0.08)), (2.3 * math.cos(a), 2.3 * math.sin(a)),
                   (1.8 * math.cos(a + 0.08), 1.8 * math.sin(a + 0.08)), closed=False) for a in [k * math.pi / 9 for k in range(18) if k not in (0, 17, 1)]]
    mouth = circle(1.75, -0.1, 0.18, 14)
    tail = poly((-1.8, 0.4), (-2.6, 0.9), (-2.6, -0.9), (-1.8, -0.4), closed=False)
    fins = [lens((0.2, -0.4), (0.9, -1.0), 0.35)]
    return Design("Pufferfish", [body, mouth, tail] + spikes + fins, [eye(0.9, 0.6, 0.15)], T)


@design("angelfish", T)
def angelfish(rng):
    body = poly((-1.6, 0.0), (0.4, 1.6), (1.2, 0.2), (1.2, -0.2), (0.4, -1.6))
    top_fin = quad((0.0, 1.3), (1.0, 3.4), (1.6, 2.6))
    bot_fin = quad((0.0, -1.3), (1.0, -3.4), (1.6, -2.6))
    fins = [quad((1.6, 2.6), (1.4, 1.0), (1.2, 0.2)), quad((1.6, -2.6), (1.4, -1.0), (1.2, -0.2))]
    tail = poly((1.2, 0.2), (2.2, 0.8), (2.2, -0.8), (1.2, -0.2), closed=False)
    stripes = [[(-0.6, 1.0), (-0.6, -1.0)], [(0.3, 1.5), (0.3, -1.5)]]
    return Design("Angelfish", [body, top_fin, bot_fin, tail] + fins + stripes, [eye(-0.9, 0.25, 0.1)], T)


@design("manta_ray", T)
def manta_ray(rng):
    right = [(0, 1.4), (1.2, 1.0), (3.4, 0.2), (1.6, -0.6), (0.4, -1.4), (0, -1.6)]
    body = chain(mirror_x(right)[::-1], right[1:])
    horns = [quad((-0.4, 1.3), (-0.6, 1.9), (-0.2, 2.1)), quad((0.4, 1.3), (0.6, 1.9), (0.2, 2.1))]
    tail = [(0, -1.6), (0.2, -3.6)]
    gills = [[(-0.5, 0.4 - 0.25 * k), (-0.2, 0.4 - 0.25 * k)] for k in range(4)] + [[(0.2, 0.4 - 0.25 * k), (0.5, 0.4 - 0.25 * k)] for k in range(4)]
    return Design("Manta Ray", [body, tail] + horns + gills, [], T)


@design("stingray", T)
def stingray(rng):
    disc = ellipse(0, 0.4, 2.2, 1.7, 120)
    tail = quad((0, -1.3), (0.6, -2.6), (1.6, -3.4))
    spine = [(1.1, -2.9), (1.5, -2.7)]
    spots = [circle(x, y, 0.18, 14) for x, y in [(-1.0, 0.8), (0.9, 0.9), (-0.6, -0.2), (0.6, -0.1), (0.0, 1.4)]]
    return Design("Spotted Stingray", [disc, tail, spine] + spots, [eye(-0.4, 1.2, 0.1), eye(0.4, 1.2, 0.1)], T)


@design("hammerhead", T)
def hammerhead(rng):
    body = chain(quad((-1.6, 0.25), (0.4, 0.9), (2.0, 0.4), 20), [(2.6, 1.3), (2.4, 0.0), (2.6, -1.3)],
                 quad((2.0, -0.4), (0.4, -0.7), (-1.6, -0.25), 20))
    head = poly((-1.6, 0.25), (-1.9, 1.1), (-2.3, 1.1), (-2.3, -1.1), (-1.9, -1.1), (-1.6, -0.25), closed=False)
    fin = poly((-0.2, 0.75), (0.2, 1.9), (0.8, 0.8), closed=False)
    gills = [[(-1.1 + 0.2 * k, 0.4), (-1.1 + 0.2 * k, -0.3)] for k in range(3)]
    return Design("Hammerhead Shark", [body, head, fin] + gills, [eye(-2.2, 0.95, 0.08), eye(-2.2, -0.95, 0.08)], T)


@design("orca", T)
def orca(rng):
    body = chain(cubic((-3.0, 0.0), (-2.6, 1.2), (0.0, 1.4), (1.6, 0.6), 40), [(2.6, 1.4), (2.4, 0.2), (3.0, -0.6), (1.8, -0.2)],
                 cubic((1.8, -0.2), (0.4, -1.0), (-2.4, -1.0), (-3.0, 0.0), 40))
    fin = poly((-0.4, 1.3), (0.0, 2.8), (0.6, 1.25), closed=False)
    patch = ellipse(-1.9, 0.35, 0.45, 0.2, 24)
    belly = quad((-2.8, -0.2), (-1.0, -0.6), (0.6, -0.5))
    flipper = lens((-1.4, -0.7), (-1.0, -1.6), 0.3)
    return Design("Orca", [body, fin, patch, belly, flipper], [], T)


@design("narwhal", T)
def narwhal(rng):
    body = chain(cubic((-2.4, 0.0), (-2.2, 1.0), (0.4, 1.2), (1.6, 0.4), 40), [(2.6, 1.0), (2.3, 0.0), (2.6, -1.0), (1.6, -0.4)],
                 cubic((1.6, -0.4), (0.4, -1.0), (-2.2, -1.0), (-2.4, 0.0), 40))
    tusk = poly((-2.3, 0.25), (-4.2, 0.6), (-2.35, 0.0), closed=False)
    twist = [[(-2.6 - 0.35 * k, 0.32 + 0.06 * k), (-2.5 - 0.35 * k, 0.2 + 0.05 * k)] for k in range(5)]
    spots = [circle(x, y, 0.12, 10) for x, y in [(-0.4, 0.7), (0.3, 0.5), (0.9, 0.3), (-1.0, 0.5)]]
    flipper = lens((-1.0, -0.6), (-0.6, -1.4), 0.3)
    return Design("Narwhal", [body, tusk, flipper] + twist + spots, [eye(-1.7, 0.2, 0.08)], T)


@design("seal", T)
def seal(rng):
    body = chain(cubic((-0.2, 1.4), (-1.4, 0.6), (-1.6, -1.2), (0.0, -1.6), 40), quad((0.0, -1.6), (1.8, -1.8), (2.8, -1.2), 20),
                 [(3.4, -0.8), (3.2, -1.5), (2.6, -1.6)], quad((2.6, -1.6), (1.0, -1.0), (0.6, 1.0), 20), quad((0.6, 1.0), (0.4, 1.5), (-0.2, 1.4), 10))
    head = circle(0.1, 1.9, 0.65, 50)
    snout = ellipse(-0.6, 1.95, 0.35, 0.22, 20)
    whisk = [[(-0.8, 1.9), (-1.6, 2.1)], [(-0.8, 1.85), (-1.6, 1.6)]]
    flipper = lens((-0.4, 0.0), (-1.4, -0.6), 0.3)
    ball = [circle(-0.9, 3.0, 0.55, 40), quad((-1.45, 3.0), (-0.9, 2.8), (-0.35, 3.0)), [(-0.9, 2.45), (-0.9, 3.55)]]
    return Design("Playful Seal", [body, head, snout, flipper] + whisk + ball, [eye(0.25, 2.1, 0.09)], T)


@design("sea_otter", T)
def sea_otter(rng):
    body = ellipse(0, -0.2, 2.6, 0.9, 120)
    head = circle(-2.4, 0.4, 0.8, 60)
    ears = [circle(-2.9, 1.1, 0.18, 12), circle(-1.9, 1.1, 0.18, 12)]
    muzzle = ellipse(-2.4, 0.15, 0.35, 0.25, 20)
    paws = [ellipse(-0.8, 0.6, 0.35, 0.25, 20), ellipse(-0.2, 0.6, 0.35, 0.25, 20)]
    shell = [arc(-0.5, 0.75, 0.45, 0, math.pi, 14)]
    tail = lens((2.4, -0.2), (3.4, 0.2), 0.3)
    water = [wave(-3.6, 3.6, -1.1, 0.1, 6, 100)]
    return Design("Sea Otter", [body, head, muzzle, tail] + ears + paws + shell + water, [eye(-2.6, 0.55, 0.07), eye(-2.2, 0.55, 0.07)], T)


@design("lobster", T)
def lobster(rng):
    segs = [ellipse(0, 1.0 - 0.55 * k, 0.75 - 0.08 * k, 0.32, 30) for k in range(5)]
    head = ellipse(0, 1.7, 0.85, 0.7, 40)
    tail = poly((-0.6, -1.6), (0, -2.6), (0.6, -1.6), closed=False)
    tail_fan = [lens((0, -1.7), (-0.8, -2.6), 0.3), lens((0, -1.7), (0.8, -2.6), 0.3)]
    claws = []
    for s in (-1, 1):
        claws.append([(s * 0.7, 2.0), (s * 1.4, 2.6)])
        claws.append(chain(arc(s * 1.7, 3.1, 0.55, math.radians(-120 if s > 0 else -60), math.radians(200 if s > 0 else -380), 30)))
    antennae = [quad((-0.3, 2.3), (-1.0, 3.4), (-2.6, 3.8)), quad((0.3, 2.3), (1.0, 3.4), (2.6, 3.8))]
    legs = [[(s * 0.7, 1.1 - 0.35 * k), (s * 1.4, 0.8 - 0.35 * k)] for s in (-1, 1) for k in range(3)]
    return Design("Lobster", segs + [head, tail] + tail_fan + claws + antennae + legs, [eye(-0.3, 1.9, 0.08), eye(0.3, 1.9, 0.08)], T)


@design("shrimp", T)
def shrimp(rng):
    cl = [(1.8 * math.cos(t), 1.8 * math.sin(t)) for t in [math.radians(200 - 2.2 * i) for i in range(101)]]
    body = tube(cl, lambda t: 1.0 * (1 - t) + 0.25)
    segs = [[(1.3 * math.cos(a), 1.3 * math.sin(a)), (2.3 * math.cos(a), 2.3 * math.sin(a))] for a in [math.radians(170 - 30 * k) for k in range(5)]]
    tail = [lens(cl[-1], (cl[-1][0] + 0.6, cl[-1][1] - 0.6), 0.3), lens(cl[-1], (cl[-1][0] - 0.2, cl[-1][1] - 0.8), 0.3)]
    whiskers = [quad((-1.8, -0.3), (-2.6, 1.2), (-1.2, 2.6)), quad((-1.7, -0.5), (-3.0, 0.6), (-2.4, 2.4))]
    legs = [[(1.8 * math.cos(a) * 0.75, 1.8 * math.sin(a) * 0.75), (1.0 * math.cos(a), 1.0 * math.sin(a))] for a in [math.radians(190 - 25 * k) for k in range(4)]]
    return Design("Shrimp", [body] + segs + tail + whiskers + legs, [eye(-1.55, -0.3, 0.09)], T)


@design("squid", T)
def squid(rng):
    mantle = chain([(-0.8, 0.0)], cubic((-1.0, 1.6), (-0.4, 3.0), (0, 3.4), (0, 3.4), 30)[1:], cubic((0, 3.4), (0.4, 3.0), (1.0, 1.6), (0.8, 0.0), 30))
    fins = [poly((-0.5, 2.6), (-1.4, 3.0), (-0.3, 3.3), closed=False), poly((0.5, 2.6), (1.4, 3.0), (0.3, 3.3), closed=False)]
    head = ellipse(0, -0.3, 0.8, 0.5, 40)
    arms = [[(x, -0.7), (x * 1.5 + 0.2 * math.sin(k), -2.6 + 0.2 * k)] for k, x in enumerate((-0.6, -0.35, -0.1, 0.1, 0.35, 0.6))]
    long_ = [quad((-0.2, -0.7), (-1.2, -2.2), (-1.0, -3.4)), quad((0.2, -0.7), (1.2, -2.2), (1.0, -3.4))]
    return Design("Squid", [mantle, head] + fins + arms + long_, [eye(-0.35, -0.25, 0.12), eye(0.35, -0.25, 0.12)], T)


@design("sea_urchin", T)
def sea_urchin(rng):
    ball = circle(0, 0, 1.2, 100)
    spines = [[(1.2 * math.cos(a), 1.2 * math.sin(a)), (2.6 * math.cos(a), 2.6 * math.sin(a))] for a in [k * math.pi / 12 for k in range(24)]]
    dots = [circle(0.6 * math.cos(a), 0.6 * math.sin(a), 0.1, 10) for a in [k * math.pi / 3 for k in range(6)]]
    return Design("Sea Urchin", [ball] + spines + dots, [], T)


@design("anemone", T)
def anemone(rng):
    base = poly((-1.2, -2.4), (-1.0, 0.0), (1.0, 0.0), (1.2, -2.4), closed=False)
    rim = ellipse(0, 0, 1.0, 0.3, 40)
    tentacles = [quad((0.8 * math.cos(a) * 0.9, 0.1), (1.6 * math.cos(a), 1.2 + 0.4 * math.sin(3 * a)), (2.0 * math.cos(a), 2.4 - abs(math.cos(a))))
                 for a in [math.radians(15 + 150 * k / 9) for k in range(10)]]
    tips = [circle(2.0 * math.cos(a), 2.4 - abs(math.cos(a)), 0.12, 10) for a in [math.radians(15 + 150 * k / 9) for k in range(10)]]
    rocks = [arc(-2.2, -2.4, 0.8, 0, math.pi, 20), arc(2.3, -2.4, 0.6, 0, math.pi, 16)]
    return Design("Sea Anemone", [base, rim] + tentacles + tips + rocks, [], T)


@design("clam_pearl", T)
def clam_pearl(rng):
    lower = chain(arc(0, 0.0, 2.4, math.radians(190), math.radians(350), 60), [(-2.36, -0.42)])
    upper = chain(arc(0, -0.6, 2.4, math.radians(30), math.radians(150), 60), [(2.08, 0.6)])
    ridges = [[(0, -0.2), (2.2 * math.cos(a), -0.6 + 2.2 * math.sin(a))] for a in [math.radians(40 + 20 * k) for k in range(6)]]
    pearl = circle(0, 0.15, 0.55, 40)
    shine = arc(-0.15, 0.3, 0.3, math.radians(100), math.radians(170), 8)
    return Design("Clam with Pearl", [lower, upper, pearl, shine] + ridges, [], T)


@design("oyster", T)
def oyster(rng):
    shell = chain(cubic((-2.4, 0.0), (-2.4, 2.0), (1.4, 2.4), (2.6, 0.6), 40), cubic((2.6, 0.6), (2.6, -1.4), (-1.6, -1.8), (-2.4, 0.0), 40))
    rings = [chain(cubic((-1.8 + 0.4 * k, 0.0), (-1.8 + 0.4 * k, 1.6 - 0.3 * k), (1.0 - 0.3 * k, 1.9 - 0.3 * k), (2.0 - 0.4 * k, 0.5), 30)) for k in range(3)]
    rock = [quad((-3.2, -1.8), (0, -2.6), (3.2, -1.8))]
    return Design("Oyster", [shell] + rings + rock, [], T)


@design("hermit_crab", T)
def hermit_crab(rng):
    shell = spiral(0.6, 0.6, 0.15, 1.6, 2.2, 160)
    rim = circle(0.6, 0.6, 1.75, 100)
    body = ellipse(-1.2, -0.6, 0.8, 0.5, 40)
    claw = chain(arc(-2.3, -0.4, 0.45, math.radians(-60), math.radians(240), 24))
    eyes_ = [[(-1.4, -0.2), (-1.6, 0.6)], [(-1.1, -0.2), (-1.2, 0.6)], circle(-1.6, 0.7, 0.12, 10), circle(-1.2, 0.7, 0.12, 10)]
    legs = [[(-1.0 + 0.3 * k, -1.0), (-1.3 + 0.35 * k, -1.6)] for k in range(3)]
    sand = [wave(-3.2, 3.2, -1.7, 0.08, 4, 80)]
    return Design("Hermit Crab", [shell, rim, body, claw] + eyes_ + legs + sand, [], T)


@design("blue_whale", T)
def blue_whale(rng):
    body = chain(cubic((-3.4, 0.2), (-3.2, 1.0), (-1.0, 1.2), (1.8, 0.4), 50), quad((1.8, 0.4), (2.6, 0.2), (3.0, 0.5), 10),
                 [(3.6, 1.0), (3.4, 0.2), (3.6, -0.6)], quad((3.0, -0.1), (2.4, -0.4), (1.8, -0.3), 10),
                 cubic((1.8, -0.3), (-0.6, -1.0), (-3.0, -0.8), (-3.4, 0.2), 50))
    grooves = [quad((-3.2, -0.2 - 0.12 * k), (-2.0, -0.6 - 0.1 * k), (-0.6, -0.6 - 0.05 * k)) for k in range(4)]
    fin = poly((1.0, 0.65), (1.3, 1.0), (1.5, 0.55), closed=False)
    flipper = lens((-1.6, -0.7), (-1.0, -1.6), 0.25)
    calf = transform(chain(cubic((-1, 0), (-0.8, 0.5), (0.6, 0.5), (1.0, 0.1), 20), [(1.4, 0.4), (1.3, 0.0), (1.4, -0.4)],
                           cubic((1.0, -0.1), (0.6, -0.5), (-0.8, -0.5), (-1, 0), 20)), dx=0.6, dy=-2.4, s=0.8)
    return Design("Blue Whale and Calf", [body, fin, flipper, calf] + grooves, [eye(-2.6, 0.0, 0.07)], T)


@design("beluga", T)
def beluga(rng):
    body = chain(cubic((-2.2, 0.6), (-2.4, 1.8), (-0.6, 1.8), (0.4, 1.0), 40), quad((0.4, 1.0), (1.8, 0.4), (2.4, 0.3), 20),
                 [(3.0, 1.0), (2.8, 0.1), (3.0, -0.8)], quad((2.4, -0.1), (0.8, -0.9), (-1.6, -0.6), 20),
                 quad((-1.6, -0.6), (-2.6, -0.4), (-2.6, 0.2), 12), [(-2.2, 0.6)])
    smile = arc(-2.1, 0.5, 0.45, math.radians(220), math.radians(320), 12)
    flipper = lens((-0.8, -0.5), (-0.4, -1.4), 0.3)
    bubbles = [circle(-2.4, 2.4, 0.18, 14), circle(-2.0, 2.9, 0.25, 18)]
    return Design("Beluga", [body, smile, flipper] + bubbles, [eye(-1.5, 0.9, 0.09)], T)


@design("swordfish", T)
def swordfish(rng):
    body = fish(4.4, 1.2, "crescent")
    sword = poly((-2.2, 0.15), (-4.2, 0.0), (-2.2, -0.1), closed=False)
    sail = poly((-1.2, 0.85), (-0.6, 2.4), (0.4, 1.0), closed=False)
    stripes = [quad((-1.2 + 0.6 * k, 0.5), (-1.0 + 0.6 * k, 0.0), (-1.2 + 0.6 * k, -0.5)) for k in range(4)]
    return Design("Swordfish", [body, sword, sail] + stripes, [eye(-1.7, 0.2, 0.09)], T)


@design("flying_fish", T)
def flying_fish(rng):
    body = fish(3.6, 0.9, "fork")
    wings = [lens((-0.6, 0.4), (1.2, 2.2), 0.25), lens((-0.6, -0.4), (1.2, -2.0), 0.25)]
    veins = [[(-0.3, 0.6), (0.8, 1.7)], [(-0.3, -0.6), (0.8, -1.5)]]
    splash = [quad((1.6, -2.4), (2.4, -1.6), (3.2, -2.4)), circle(2.0, -1.4, 0.12, 10), circle(2.8, -1.2, 0.1, 10)]
    return Design("Flying Fish", [body] + wings + veins + splash, [eye(-1.4, 0.15, 0.08)], T)


@design("anglerfish", T)
def anglerfish(rng):
    body = chain(cubic((-2.0, 0.4), (-2.0, 2.2), (1.2, 2.2), (1.8, 0.4), 40), [(2.8, 1.2), (2.6, 0.0), (2.8, -1.2), (1.8, -0.4)],
                 cubic((1.8, -0.4), (1.2, -2.0), (-1.6, -1.8), (-2.0, -0.4), 40))
    jaw = [zigzag(-2.0, -0.4, 0.0, 0.25, 4)]
    lure = [quad((-0.6, 1.9), (-1.0, 3.2), (-2.2, 3.0)), circle(-2.3, 2.9, 0.3, 20)]
    glow = [[(-2.3 + 0.6 * math.cos(a), 2.9 + 0.6 * math.sin(a)), (-2.3 + 0.9 * math.cos(a), 2.9 + 0.9 * math.sin(a))] for a in [k * math.pi / 3 for k in range(6)]]
    return Design("Anglerfish", [body] + jaw + lure + glow, [eye(-0.6, 0.9, 0.18)], T)


@design("moray_eel", T)
def moray_eel(rng):
    cl = [(-2.6 + 5.4 * t, 0.9 * math.sin(2.4 * math.pi * t) - 0.6 * t) for t in [i / 80 for i in range(81)]]
    body = tube(cl, lambda t: 0.9 * (1 - 0.6 * t))
    mouth = [(-2.9, 0.0), (-2.3, -0.15)]
    rocks = [chain(arc(2.4, -2.2, 1.0, 0, math.pi, 30)), arc(-2.2, -2.2, 0.7, 0, math.pi, 20)]
    spots = [circle(cl[i][0], cl[i][1], 0.1, 10) for i in range(10, 75, 9)]
    return Design("Moray Eel", [body, mouth] + rocks + spots, [eye(-2.4, 0.2, 0.08)], T)


@design("sea_snail", T)
def sea_snail(rng):
    shell = spiral(0.4, 0.6, 0.1, 1.5, 3.0, 220)
    cone = chain(cubic((-1.2, -0.2), (-0.8, -1.2), (1.6, -1.0), (1.9, 0.6), 30))
    body = chain(quad((-2.8, -1.2), (-1.6, -1.6), (2.0, -1.4)), quad((2.0, -1.4), (2.6, -1.2), (2.4, -0.8)))
    stalks = [[(-2.4, -1.2), (-2.8, -0.2)], [(-2.1, -1.2), (-2.2, -0.2)], circle(-2.8, -0.1, 0.12, 10), circle(-2.2, -0.1, 0.12, 10)]
    return Design("Sea Snail", [shell, cone, body] + stalks, [], T)


@design("kelp_forest", T)
def kelp_forest(rng):
    out = []
    for x in (-2.2, -0.6, 1.0, 2.4):
        stem = [(x + 0.35 * math.sin(2.5 * t + x), -3.0 + 6.0 * t) for t in [i / 60 for i in range(61)]]
        out.append(stem)
        for k in range(4):
            px, py = stem[10 + 12 * k]
            out.append(lens((px, py), (px + (0.9 if k % 2 else -0.9), py + 0.6), 0.3))
    fish_ = [transform(fish(1.2, 0.5, "fork"), dx=x, dy=y) for x, y in [(0.2, 1.8), (-1.4, 0.4)]]
    return Design("Kelp Forest", out + fish_, [], T)


@design("brain_coral", T)
def brain_coral(rng):
    dome = chain(arc(0, -1.6, 2.6, 0, math.pi, 90), [(2.6, -1.6)])
    grooves = [[(x + 0.3 * math.sin(4 * t), -1.4 + (2.3 - abs(x) * 0.5) * t) for t in [i / 30 for i in range(31)]] for x in (-1.6, -0.8, 0.0, 0.8, 1.6)]
    sand = [wave(-3.2, 3.2, -1.7, 0.08, 4, 80)]
    return Design("Brain Coral", [dome] + grooves + sand, [], T)


@design("diver_helmet", T)
def diver_helmet(rng):
    dome = circle(0, 0.6, 2.0, 120)
    window = circle(0, 0.6, 0.9, 60)
    frame = circle(0, 0.6, 1.1, 70)
    bolts = [circle(1.1 * math.cos(a), 0.6 + 1.1 * math.sin(a), 0.08, 8) for a in [k * math.pi / 4 for k in range(8)]]
    collar = rrect(-2.2, -2.2, 2.2, -1.2, 0.3)
    side = [circle(-1.6, 1.4, 0.35, 24), circle(1.6, 1.4, 0.35, 24)]
    hose = cubic((2.0, 1.6), (3.0, 2.4), (3.4, 0.0), (3.0, -2.0), 30)
    return Design("Diving Helmet", [dome, window, frame, collar, hose] + side, bolts, T)


@design("scuba_diver", T)
def scuba_diver(rng):
    body = tube([(-2.0, 0.4), (1.2, 0.0)], 0.8)
    head = circle(-2.6, 0.6, 0.5, 40)
    mask = rrect(-3.05, 0.5, -2.55, 0.85, 0.1)
    tank = rrect(-1.6, 0.6, 0.6, 1.2, 0.3)
    legs = [[(1.2, 0.3), (2.4, 0.6)], [(1.2, -0.3), (2.4, -0.4)]]
    flippers = [poly((2.4, 0.6), (3.4, 1.1), (3.2, 0.4), closed=False), poly((2.4, -0.4), (3.4, -0.2), (3.0, -0.9), closed=False)]
    arms = [[(-1.6, 0.0), (-2.4, -0.8)]]
    bubbles = [circle(-3.2 + 0.2 * k, 1.4 + 0.6 * k, 0.12 + 0.05 * k, 12) for k in range(4)]
    return Design("Scuba Diver", [body, head, mask, tank] + legs + flippers + arms + bubbles, [], T)


@design("shipwreck", T)
def shipwreck(rng):
    hull = transform(poly((-3.0, 0.0), (2.6, 0.0), (2.0, -1.4), (-2.4, -1.4)), rot=-0.15)
    mast = transform([(0.0, 0.0), (0.4, 2.8)], rot=-0.15)
    broken = transform([(0.4, 2.8), (1.4, 2.2)], rot=-0.15)
    portholes = [transform(circle(x, -0.7, 0.2, 14), rot=-0.15) for x in (-1.6, -0.6, 0.4, 1.4)]
    sand = [wave(-3.4, 3.4, -2.0, 0.1, 4, 80)]
    weeds = [quad((x, -2.0), (x + 0.3, -1.2), (x - 0.1, -0.6)) for x in (-2.6, 2.6, 3.0)]
    return Design("Shipwreck", [hull, mast, broken] + portholes + sand + weeds, [], T)


@design("message_bottle", T)
def message_bottle(rng):
    bottle = transform(chain([(-1.0, -2.0)], [(-1.0, 0.6)], quad((-1.0, 1.2), (-0.35, 1.4), (-0.35, 1.4), 6), [(-0.35, 2.2), (0.35, 2.2), (0.35, 1.4)],
                             quad((1.0, 1.2), (1.0, 0.6), (1.0, 0.6), 6), [(1.0, -2.0), (-1.0, -2.0)]), rot=-0.5)
    cork = transform(rect(-0.3, 2.2, 0.3, 2.7), rot=-0.5)
    scroll = transform(rrect(-0.5, -1.4, 0.5, 0.4, 0.2), rot=-0.5)
    tie = transform([(-0.55, -0.5), (0.55, -0.5)], rot=-0.5)
    waves_ = [wave(-3.4, 3.4, -2.4, 0.15, 4, 80), wave(-3.4, 3.4, -2.9, 0.15, 5, 80)]
    return Design("Message in a Bottle", [bottle, cork, scroll, tie] + waves_, [], T)


@design("fish_school", T)
def fish_school(rng):
    out = []
    for i, (x, y, s) in enumerate([(-2.0, 1.6, 0.55), (-0.6, 2.0, 0.6), (0.9, 1.5, 0.55), (-1.4, 0.2, 0.6), (0.2, 0.4, 0.7), (1.8, 0.2, 0.55),
                                    (-0.8, -1.2, 0.6), (0.9, -1.0, 0.55), (-2.2, -1.4, 0.5)]):
        out.append(transform(fish(2.0, 0.8, "fork"), dx=x, dy=y, s=s))
        out.append(circle(x - 0.55 * s, y + 0.1 * s, 0.06, 8))
    return Design("School of Fish", out, [], T)


@design("leafy_seadragon", T)
def leafy_seadragon(rng):
    cl = chain(cubic((-2.0, 1.4), (-0.6, 2.0), (0.6, 0.0), (1.4, -0.6), 40), cubic((1.4, -0.6), (2.4, -1.4), (1.8, -2.6), (1.2, -2.2), 20))
    body = tube(cl, lambda t: 0.55 * (1 - t) + 0.1, cap=False)
    snout = tube([(-2.0, 1.4), (-3.2, 1.2)], 0.2)
    leaves = [lens(cl[i], (cl[i][0] + 0.6 * (1 if k % 2 else -1), cl[i][1] + 0.8), 0.35) for k, i in enumerate(range(6, 55, 8))]
    return Design("Leafy Sea Dragon", [body, snout] + leaves, [eye(-1.7, 1.55, 0.08)], T)


@design("butterflyfish", T)
def butterflyfish(rng):
    body = chain(cubic((-1.8, 0.0), (-1.0, 2.0), (1.2, 2.0), (1.6, 0.2), 40), [(2.4, 0.8), (2.4, -0.8), (1.6, -0.2)],
                 cubic((1.6, -0.2), (1.2, -2.0), (-1.0, -2.0), (-1.8, 0.0), 40))
    snout = poly((-1.8, 0.15), (-2.6, 0.05), (-1.8, -0.1), closed=False)
    band = [quad((-0.9, 1.4), (-0.6, 0.0), (-0.9, -1.4))]
    spot = circle(0.9, 0.6, 0.35, 24)
    lines_ = [quad((-0.2, 1.4 - 0.5 * k), (0.4, 1.2 - 0.5 * k), (1.2, 1.0 - 0.5 * k)) for k in range(4)]
    return Design("Butterflyfish", [body, snout, spot] + band + lines_, [eye(-1.2, 0.3, 0.1)], T)


@design("barracuda", T)
def barracuda(rng):
    body = fish(6.0, 0.7, "fork", nose=0.4)
    jaw = zigzag(-3.4, -2.2, -0.05, 0.08, 5)
    fins = [poly((0.4, 0.5), (0.8, 1.1), (1.2, 0.45), closed=False), poly((-0.6, -0.5), (-0.3, -1.0), (0.1, -0.5), closed=False)]
    bars = [[(-1.2 + 0.7 * k, 0.5), (-1.0 + 0.7 * k, 0.1)] for k in range(5)]
    return Design("Barracuda", [body, jaw] + fins + bars, [eye(-2.4, 0.15, 0.08)], T)


@design("sea_lion", T)
def sea_lion(rng):
    body = chain(cubic((-0.4, 2.8), (0.8, 2.4), (1.0, 0.6), (1.6, -0.8), 40), quad((1.6, -0.8), (2.6, -1.6), (3.0, -1.2), 12),
                 [(2.8, -1.8), (-0.6, -1.8)], cubic((-0.6, -1.8), (-1.2, -0.4), (-1.0, 1.2), (-1.2, 2.0), 30))
    head = chain(quad((-1.2, 2.0), (-2.2, 2.4), (-2.4, 2.0), 12), quad((-2.4, 2.0), (-1.4, 3.2), (-0.4, 2.8), 16))
    flipper = lens((0.0, -0.2), (-0.8, -1.6), 0.25)
    rock = [chain(arc(0.6, -1.8, 3.0, math.radians(200), math.radians(340), 40)), [(-2.2, -1.8), (3.4, -1.8)]]
    return Design("Sea Lion", [body, head, flipper] + rock, [eye(-1.4, 2.6, 0.08)], T)


@design("horseshoe_crab", T)
def horseshoe_crab(rng):
    shell = chain(arc(0, -0.2, 2.2, math.radians(5), math.radians(175), 70))
    back = poly((-1.4, -0.1), (1.4, -0.1), (0.9, -1.6), (-0.9, -1.6))
    ridge = [(0, 2.0), (0, -1.6)]
    eyes_ = [ellipse(-1.0, 1.0, 0.25, 0.12, 16), ellipse(1.0, 1.0, 0.25, 0.12, 16)]
    spines = [poly((x, -0.6), (x + 0.4 * (1 if x > 0 else -1), -0.8), (x, -1.0), closed=False) for x in (-1.1, 1.1)]
    tail = [(0, -1.6), (0, -3.6)]
    base = [(-2.19, 0.0), (2.19, 0.0)]
    return Design("Horseshoe Crab", [shell, base, back, ridge, tail] + eyes_ + spines, [], T)


@design("nudibranch", T)
def nudibranch(rng):
    cl = [(-2.8 + 5.6 * t, 0.3 * math.sin(math.pi * t * 1.5)) for t in [i / 60 for i in range(61)]]
    body = tube(cl, lambda t: 0.9 * math.sin(math.pi * (0.1 + 0.85 * t)) + 0.2)
    horns = [quad((-2.4, 0.3), (-2.8, 1.0), (-2.5, 1.4)), quad((-2.1, 0.35), (-2.2, 1.1), (-1.8, 1.4))]
    frills = [lens((x, 0.5 + 0.2 * math.sin(x)), (x + 0.2, 1.4 + 0.2 * math.sin(x)), 0.4) for x in (-1.2, -0.4, 0.4, 1.2, 2.0)]
    spots = [circle(x, 0.0 + 0.3 * math.sin(math.pi * (x + 2.8) / 5.6 * 1.5), 0.12, 10) for x in (-1.6, -0.8, 0.0, 0.8, 1.6)]
    return Design("Sea Slug", [body] + horns + frills + spots, [], T)


@design("sunfish", T)
def sunfish(rng):
    body = ellipse(0, 0, 2.2, 2.0, 140)
    fins = [poly((0.4, 1.9), (0.9, 3.6), (1.4, 1.6), closed=False), poly((0.4, -1.9), (0.9, -3.6), (1.4, -1.6), closed=False)]
    tail = chain(arc(2.0, 0, 0.9, math.radians(-75), math.radians(75), 24))
    scallop = [arc(2.3 + 0.0, y, 0.3, math.radians(-80), math.radians(80), 8) for y in (-0.6, 0.0, 0.6)]
    mouth = circle(-2.15, -0.2, 0.15, 12)
    gill = arc(-1.2, 0.2, 0.5, math.radians(-60), math.radians(60), 10)
    return Design("Ocean Sunfish", [body, tail, mouth, gill] + fins + scallop, [eye(-1.5, 0.5, 0.12)], T)
