"""Outer Space niche, part 2 (pictures 10-50)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "space"


def stars(pts):
    return [star(x, y, r) for x, y, r in pts]


def planet(cx, cy, r, bands=0):
    out = [circle(cx, cy, r, 80)]
    for k in range(bands):
        y = cy - r + 2 * r * (k + 1) / (bands + 1)
        w = math.sqrt(max(0.0, r * r - (y - cy) ** 2))
        out.append(quad((cx - w, y), (cx, y + 0.12 * r), (cx + w, y)))
    return out


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


def _rocket(cx, cy, s):
    left = cubic((-0.6, -1.6), (-0.8, 0.4), (-0.5, 1.6), (0, 2.4), 30)
    body = chain(left, mirror_x(left)[::-1], [(-0.6, -1.6)])
    parts = [body, circle(0, 0.8, 0.3, 24), poly((-0.62, -0.8), (-1.3, -2.0), (-0.6, -1.6), closed=False), poly((0.62, -0.8), (1.3, -2.0), (0.6, -1.6), closed=False)]
    return [transform(p, dx=cx, dy=cy, s=s) for p in parts]


@design("rocket_launch", T)
def rocket_launch(rng):
    r = _rocket(0, 0.8, 1.0)
    tower = [[(1.8, -2.8), (1.8, 2.6)], [(2.4, -2.8), (2.4, 2.6)]] + [[(1.8, y), (2.4, y + 0.6)] for y in (-2.4, -1.2, 0.0, 1.2)] + [[(1.8, 1.8), (0.5, 1.8)]]
    smoke = [circle(x, -2.4, r_, 20) for x, r_ in [(-1.6, 0.6), (-0.6, 0.7), (0.6, 0.65), (-2.5, 0.45)]]
    flame = [poly((-0.4, -0.8), (0, -1.9), (0.4, -0.8), closed=False)]
    return make("Rocket Launch", r + tower + smoke + flame)


@design("space_shuttle", T)
def space_shuttle(rng):
    body = chain(quad((-0.5, -1.6), (-0.6, 1.6), (0, 2.8)), quad((0, 2.8), (0.6, 1.6), (0.5, -1.6)), [(-0.5, -1.6)])
    wings = poly((-0.5, -0.2), (-2.0, -1.6), (2.0, -1.6), (0.5, -0.2), closed=False)
    tank = [rrect(1.0, -2.0, 1.8, 2.2, 0.4), rrect(-1.8, -2.0, -1.0, 1.6, 0.4)]
    windows = [[(-0.25, 2.0), (0.25, 2.0)]]
    flames = [poly((x - 0.3, -2.0), (x, -3.0), (x + 0.3, -2.0), closed=False) for x in (-1.4, 0.0, 1.4)]
    return make("Space Shuttle", [body, wings] + tank + windows + flames)


@design("lunar_lander", T)
def lunar_lander(rng):
    cabin = poly((-1.0, 0.0), (-1.2, 1.0), (-0.6, 1.8), (0.6, 1.8), (1.2, 1.0), (1.0, 0.0))
    window = poly((-0.4, 1.0), (-0.2, 1.4), (0.2, 1.4), (0.4, 1.0))
    base = rect(-1.2, -0.8, 1.2, 0.0)
    legs = [[(-1.2, -0.6), (-2.2, -2.2)], [(1.2, -0.6), (2.2, -2.2)], [(-0.6, -0.8), (-0.8, -2.2)], [(0.6, -0.8), (0.8, -2.2)]]
    pads = [ellipse(x, -2.25, 0.3, 0.08, 12) for x in (-2.2, -0.8, 0.8, 2.2)]
    antenna = [[(0.6, 1.8), (1.2, 2.6)], arc(1.3, 2.7, 0.3, math.radians(200), math.radians(340), 8)]
    craters = [ellipse(-2.6, -2.8, 0.5, 0.12, 20), ellipse(2.4, -2.9, 0.4, 0.1, 16)]
    return make("Lunar Lander", [cabin, window, base] + legs + pads + antenna + craters)


@design("mars_rover", T)
def mars_rover(rng):
    body = rect(-1.8, -0.4, 1.8, 0.4)
    mast = [[(-1.2, 0.4), (-1.2, 2.0)], rect(-1.6, 2.0, -0.8, 2.5)]
    panel = [poly((-0.6, 0.4), (-0.2, 1.2), (2.2, 1.2), (1.8, 0.4), closed=False)]
    arm = [[(1.8, 0.0), (2.6, -0.6), (3.0, -1.4)]]
    wheels = [circle(x, -1.4, 0.45, 24) for x in (-1.6, 0.0, 1.6)] + [[(x, -0.4), (x, -0.95)] for x in (-1.6, 0.0, 1.6)]
    rocks = [arc(-2.8, -1.85, 0.4, 0, math.pi, 10), arc(2.6, -1.85, 0.3, 0, math.pi, 8)]
    ground = [(-3.4, -1.85), (3.4, -1.85)]
    return make("Mars Rover", [body, ground] + mast + panel + arm + wheels + rocks)


@design("space_station", T)
def space_station(rng):
    core = [rect(-0.6, -0.4, 0.6, 0.4), rect(-2.0, -0.2, -0.6, 0.2), rect(0.6, -0.2, 2.0, 0.2)]
    panels = []
    for x in (-2.6, 2.6):
        for y in (1.0, -1.0):
            panels.append(rect(x - 0.4, y - 0.8, x + 0.4, y + 0.8))
            panels += [[(x - 0.4, y + d), (x + 0.4, y + d)] for d in (-0.4, 0.0, 0.4)]
        panels.append([(x, -0.2), (x, 0.2)])
    trusses = [[(-2.0, 0.0), (-2.6, 0.0)], [(2.0, 0.0), (2.6, 0.0)], [(-2.6, 0.2), (-2.6, -0.2)]]
    module = [circle(0, 1.0, 0.5, 30), [(0, 0.4), (0, 0.5)]]
    return make("Space Station", core + panels + trusses + module)


@design("tethered_astronaut", T)
def tethered_astronaut(rng):
    helmet = circle(0.4, 1.4, 0.7, 50)
    visor = ellipse(0.4, 1.4, 0.45, 0.35, 30)
    body = rrect(-0.3, -0.8, 1.1, 0.7, 0.3)
    limbs = [tube([(-0.3, 0.4), (-1.0, 1.2)], 0.35), tube([(1.1, 0.4), (1.8, -0.2)], 0.35), tube([(0.0, -0.8), (-0.4, -1.8)], 0.4), tube([(0.8, -0.8), (1.4, -1.6)], 0.4)]
    tether = cubic((-0.3, 0.0), (-1.6, -1.0), (-2.0, 1.6), (-3.0, 2.4), 40)
    ship = [rect(-3.4, 2.2, -2.6, 3.0)]
    return make("Spacewalk", [helmet, visor, body, tether] + limbs + ship + stars([(2.4, 2.6, 0.3), (2.6, -1.8, 0.25)]))


@design("astronaut_portrait", T)
def astronaut_portrait(rng):
    helmet = circle(0, 0.6, 2.0, 120)
    visor = rrect(-1.4, -0.2, 1.4, 1.6, 0.6)
    reflection = [planet(-0.6, 0.9, 0.4, 1)[0], star(0.6, 1.1, 0.2)]
    collar = [rrect(-2.0, -2.6, 2.0, -1.4, 0.4), [(-1.2, -2.0), (1.2, -2.0)]]
    lights = [circle(-1.6, 1.8, 0.2, 14), circle(1.6, 1.8, 0.2, 14)]
    return make("Astronaut Portrait", [helmet, visor] + reflection + collar + lights)


@design("full_moon", T)
def full_moon(rng):
    moon = circle(0, 0, 2.4, 160)
    craters = [circle(x, y, r, 30) for x, y, r in [(-0.8, 0.9, 0.5), (0.9, 0.4, 0.35), (-0.2, -0.9, 0.6), (1.2, -1.2, 0.3), (-1.5, -0.3, 0.25), (0.4, 1.6, 0.25)]]
    rays = [[(-0.2 + 0.6 * math.cos(a), -0.9 + 0.6 * math.sin(a)), (-0.2 + 1.0 * math.cos(a), -0.9 + 1.0 * math.sin(a))] for a in [k * math.pi / 3 for k in range(6)]]
    return make("Full Moon", [moon] + craters + rays)


@design("solar_flare", T)
def solar_flare(rng):
    sun = circle(0, 0, 1.8, 140)
    corona = [(( 2.3 + 0.25 * math.sin(14 * t)) * math.cos(t), (2.3 + 0.25 * math.sin(14 * t)) * math.sin(t)) for t in [k * 2 * math.pi / 280 for k in range(281)]]
    loops = [arc(2.75 * math.cos(a), 2.75 * math.sin(a), 0.55, a - 1.9, a + 1.9, 30) for a in (0.9, 2.6, 4.4)]
    spots = [circle(x, y, r, 16) for x, y, r in [(-0.5, 0.3, 0.22), (0.6, -0.5, 0.3)]]
    return make("Sun with Solar Flares", [sun, corona] + loops + spots)


@design("jupiter", T)
def jupiter(rng):
    p = planet(0, 0, 2.4, 6)
    spot = [ellipse(0.8, -0.8, 0.6, 0.3, 30), ellipse(0.8, -0.8, 0.3, 0.15, 20)]
    moons = [circle(x, y, r, 20) for x, y, r in [(-3.0, 2.0, 0.25), (3.0, 1.8, 0.2), (2.8, -2.4, 0.3)]]
    return make("Jupiter", p + spot + moons)


@design("mars_moons", T)
def mars_moons(rng):
    p = planet(-0.6, -0.4, 2.0)
    caps = [quad((-1.4, 1.4), (-0.6, 1.8), (0.2, 1.4))]
    valleys = [quad((-2.0, -0.4), (-0.6, -0.8), (0.8, -0.2)), quad((-1.4, -1.4), (-0.6, -1.2), (0.4, -1.6))]
    moons = [ellipse(2.2, 1.8, 0.4, 0.3, 20, rot=0.4), ellipse(2.6, -1.4, 0.3, 0.22, 16, rot=-0.3)]
    return make("Mars and Its Moons", p + caps + valleys + moons + stars([(2.6, 0.2, 0.2)]))


@design("solar_system", T)
def solar_system(rng):
    sun = circle(0, 0, 0.6, 40)
    orbits = [ellipse(0, 0, r, r * 0.45, 100) for r in (1.2, 1.9, 2.6, 3.3)]
    planets = [circle(r * math.cos(a), r * 0.45 * math.sin(a), s, 16) for r, a, s in [(1.2, 0.5, 0.12), (1.9, 2.2, 0.18), (2.6, 4.0, 0.2), (3.3, 5.6, 0.28)]]
    ring = [ellipse(3.3 * math.cos(5.6), 3.3 * 0.45 * math.sin(5.6), 0.5, 0.12, 20)]
    return make("Solar System", [sun] + orbits + planets + ring)


@design("big_dipper", T)
def big_dipper(rng):
    pts = [(-2.8, 1.8), (-1.6, 1.4), (-0.6, 1.0), (0.4, 0.4), (0.6, -0.8), (2.2, -1.0), (2.4, 0.2)]
    line = chain(pts, [pts[3]])
    st = [star(x, y, 0.3) for x, y in pts]
    polaris = [star(2.6, 2.6, 0.4), [(2.4, 0.2), (2.6, 2.2)]]
    return make("Big Dipper", [line] + st + polaris)


@design("orion", T)
def orion(rng):
    pts = {"a": (-1.4, 2.4), "b": (1.4, 2.0), "c": (-0.5, 0.2), "d": (0.0, 0.0), "e": (0.5, -0.2), "f": (-1.6, -2.4), "g": (1.6, -2.2), "h": (0.0, 2.9)}
    lines_ = [[pts["a"], pts["c"]], [pts["b"], pts["e"]], [pts["c"], pts["d"], pts["e"]], [pts["c"], pts["f"]], [pts["e"], pts["g"]], [pts["a"], pts["h"], pts["b"]]]
    st = [star(x, y, 0.28) for x, y in pts.values()]
    bow = [arc(-2.0, 1.2, 1.0, math.radians(100), math.radians(260), 20)]
    return make("Orion Constellation", lines_ + st + bow)


@design("spiral_galaxy", T)
def spiral_galaxy(rng):
    arms = [[(0.2 * math.exp(0.32 * t) * math.cos(t + k * math.pi), 0.6 * 0.2 * math.exp(0.32 * t) * math.sin(t + k * math.pi)) for t in [i / 30 * 3.2 * math.pi for i in range(31)]] for k in range(2)]
    core = ellipse(0, 0, 0.6, 0.35, 30)
    halo = ellipse(0, 0, 3.0, 1.6, 120)
    return make("Spiral Galaxy", arms + [core, halo] + stars([(-2.6, 2.4, 0.25), (2.4, 2.6, 0.3), (2.8, -2.2, 0.2)]))


@design("nebula", T)
def nebula(rng):
    cloud = [polar(lambda t, r=r: r + 0.4 * math.sin(3 * t + r) + 0.2 * math.sin(7 * t), n=200) for r in (2.4, 1.6, 0.9)]
    st = stars([(-0.4, 0.3, 0.3), (0.8, -0.6, 0.25), (-1.4, -1.2, 0.2), (1.6, 1.4, 0.2)])
    return make("Colourful Nebula", cloud + st)


@design("black_hole", T)
def black_hole(rng):
    hole = circle(0, 0, 0.9, 60)
    disk = [ellipse(0, 0, r, r * 0.3, 100) for r in (1.6, 2.2, 2.8)]
    halo = [arc(0, 0, 1.3, math.radians(20), math.radians(160), 30), arc(0, 0, 1.3, math.radians(200), math.radians(340), 30)]
    jets = [[(0, 0.9), (0, 3.0)], [(0, -0.9), (0, -3.0)]]
    return make("Black Hole", [hole] + disk + halo + jets)


@design("meteor_shower", T)
def meteor_shower(rng):
    meteors = []
    for x, y, L in [(-2.0, 2.4, 1.6), (0.4, 2.8, 1.2), (1.8, 1.6, 1.4), (-0.8, 0.6, 1.0), (2.2, -0.2, 1.0)]:
        meteors += [circle(x, y, 0.15, 12), [(x + 0.1, y + 0.1), (x + L, y + L * 0.6)]]
    hills = [quad((-3.4, -2.6), (-1.6, -0.8), (0.2, -2.6)), quad((0.0, -2.6), (1.8, -1.2), (3.4, -2.6))]
    tent = [poly((-0.6, -2.6), (0.0, -1.6), (0.6, -2.6))]
    return make("Meteor Shower", meteors + hills + tent)


@design("asteroid", T)
def asteroid(rng):
    rock = polar(lambda t: 2.0 + 0.3 * math.sin(3 * t) + 0.2 * math.sin(7 * t + 1), n=200)
    craters = [circle(x, y, r, 20) for x, y, r in [(-0.6, 0.6, 0.4), (0.8, -0.2, 0.3), (-0.2, -1.0, 0.25), (1.0, 1.0, 0.2)]]
    flag = [[(0.2, 2.1), (0.2, 3.2)], poly((0.2, 3.2), (1.0, 2.9), (0.2, 2.6))]
    return make("Asteroid", [rock] + craters + flag + stars([(-2.6, 2.4, 0.2), (2.6, -2.2, 0.25)]))


@design("star_cluster", T)
def star_cluster(rng):
    st = [star(x, y, r, 5 if k % 2 else 4, 0.4) for k, (x, y, r) in enumerate([(0, 0, 0.6), (-1.4, 0.8, 0.4), (1.2, 1.2, 0.45), (-0.8, -1.4, 0.35), (1.4, -0.8, 0.4),
                                                                                 (-2.4, -0.4, 0.3), (2.4, 0.2, 0.3), (0.2, 2.2, 0.35), (-0.4, -2.6, 0.3), (2.0, 2.4, 0.25)])]
    swirl = [arc(0, 0, 2.8, 0.3, 2.4, 30), arc(0, 0, 2.8, 3.4, 5.4, 30)]
    return make("Star Cluster", st + swirl)


@design("observatory", T)
def observatory(rng):
    building = [rect(-2.0, -2.6, 2.0, -0.4), chain(arc(0, -0.4, 2.0, 0, math.pi, 40))]
    slot = [[(-0.3, 1.6), (-0.3, -0.4)], [(0.3, 1.6), (0.3, -0.4)]]
    scope = [poly((0.0, 0.6), (1.6, 2.8), (2.0, 2.5), (0.4, 0.4))]
    door = [rect(-0.4, -2.6, 0.4, -1.4)]
    return make("Observatory", building + slot + scope + door + stars([(-2.4, 2.2, 0.3), (2.8, 1.0, 0.25), (-1.4, 2.8, 0.2)]))


@design("radio_dish", T)
def radio_dish(rng):
    dish = chain(arc(0, 2.6, 2.6, math.radians(210), math.radians(330), 40), [(-2.25, 1.3)])
    feed = [[(-1.6, 1.0), (0, 2.4)], [(1.6, 1.0), (0, 2.4)], circle(0, 2.5, 0.15, 10)]
    mount = [poly((-0.6, 0.2), (-1.4, -2.6), (1.4, -2.6), (0.6, 0.2), closed=False), [(-1.0, -1.2), (1.0, -1.2)]]
    waves = [arc(0, 2.5, r, math.radians(60), math.radians(120), 10) for r in (0.6, 1.0)]
    return make("Radio Telescope", [dish] + feed + mount + waves)


@design("alien_landscape", T)
def alien_landscape(rng):
    ground = [quad((-3.4, -1.6), (0, -0.8), (3.4, -1.8))]
    plants = [quad((-2.4, -1.4), (-2.8, 0.2), (-2.0, 1.0)), circle(-2.0, 1.2, 0.3, 16), quad((1.8, -1.6), (2.2, 0.0), (1.6, 0.6)), circle(1.6, 0.8, 0.25, 14)]
    planets_ = planet(1.6, 2.4, 0.8, 2) + planet(-1.0, 2.6, 0.4)
    rocks = [arc(0, -1.2, 0.5, 0, math.pi, 12)]
    crater = [ellipse(-0.8, -2.4, 1.0, 0.25, 30)]
    return make("Alien Planet", ground + plants + planets_ + rocks + crater)


@design("space_puppy", T)
def space_puppy(rng):
    helmet = circle(0, 0.8, 1.6, 90)
    head = ellipse(0, 0.6, 0.9, 0.85, 50)
    ears = [chain(cubic((-0.6, 1.2), (-1.4, 1.3), (-1.4, 0.2), (-1.0, 0.0), 16)), chain(cubic((0.6, 1.2), (1.4, 1.3), (1.4, 0.2), (1.0, 0.0), 16))]
    nose = ellipse(0, 0.2, 0.2, 0.12, 12)
    suit = [rrect(-1.2, -2.6, 1.2, -0.8, 0.4), circle(0, -1.5, 0.3, 16)]
    return make("Space Puppy", [helmet, head, nose] + ears + suit + stars([(-2.4, 2.4, 0.3), (2.4, 2.2, 0.25)]), [eye(-0.35, 0.8, 0.1), eye(0.35, 0.8, 0.1)])


@design("space_robot", T)
def space_robot(rng):
    head = rrect(-1.0, 1.0, 1.0, 2.4, 0.3)
    eyes_ = [circle(-0.45, 1.8, 0.25, 16), circle(0.45, 1.8, 0.25, 16)]
    mouth = [rect(-0.5, 1.2, 0.5, 1.45)] + [[(x, 1.2), (x, 1.45)] for x in (-0.25, 0.0, 0.25)]
    body = rrect(-1.4, -1.4, 1.4, 0.8, 0.3)
    panel = [rect(-0.8, -0.6, 0.8, 0.4), circle(-0.4, -0.1, 0.15, 10), circle(0.4, -0.1, 0.15, 10)]
    arms = [tube([(-1.4, 0.4), (-2.4, -0.6)], 0.35), tube([(1.4, 0.4), (2.4, 1.4)], 0.35)]
    legs = [rect(-1.0, -2.8, -0.4, -1.4), rect(0.4, -2.8, 1.0, -1.4)]
    antenna = [[(0, 2.4), (0, 3.0)], circle(0, 3.15, 0.15, 10)]
    return make("Space Robot", [head, body] + eyes_ + mouth + panel + arms + legs + antenna)


@design("porthole_view", T)
def porthole_view(rng):
    rim = [circle(0, 0, 2.6, 120), circle(0, 0, 2.1, 100)]
    bolts = [circle(2.35 * math.cos(a), 2.35 * math.sin(a), 0.1, 8) for a in [k * math.pi / 4 for k in range(8)]]
    earth = planet(0.4, -0.6, 1.2)
    land = [quad((-0.4, -0.4), (0.4, 0.2), (1.0, -0.4)), quad((0.0, -1.2), (0.6, -1.0), (1.2, -1.4))]
    st = stars([(-1.2, 1.2, 0.2), (1.2, 1.4, 0.15)])
    return make("View from the Porthole", rim + earth + land + st, bolts)


@design("moon_flag", T)
def moon_flag(rng):
    surface = [quad((-3.4, -1.4), (0, -1.0), (3.4, -1.6))]
    craters = [ellipse(x, y, r, r * 0.3, 20) for x, y, r in [(-2.0, -2.2, 0.6), (1.6, -2.4, 0.5)]]
    flag = [[(0, -1.1), (0, 1.8)], rect(0, 0.6, 1.8, 1.8)] + [[(0, y), (1.8, y)] for y in (0.85, 1.1, 1.35)]
    earth = planet(-2.2, 2.2, 0.7)
    return make("Flag on the Moon", surface + craters + flag + earth)


@design("moon_bootprint", T)
def moon_bootprint(rng):
    print_ = chain(cubic((-0.8, -2.0), (-1.4, 0.0), (-1.2, 2.2), (0.0, 2.4), 30), cubic((0.0, 2.4), (1.2, 2.2), (1.4, 0.0), (0.8, -2.0), 30), quad((0.8, -2.0), (0.0, -2.6), (-0.8, -2.0), 10))
    treads = [[(-1.0 + 0.04 * abs(y), y), (1.0 - 0.04 * abs(y), y)] for y in (-1.4, -0.8, -0.2, 0.4, 1.0, 1.6)]
    dust = [circle(x, y, 0.08, 8) for x, y in [(-2.0, 1.0), (2.2, -0.6), (-2.4, -1.6), (2.0, 2.0)]]
    return make("Moon Bootprint", [print_] + treads + dust)


@design("solar_eclipse", T)
def solar_eclipse(rng):
    corona = [[(2.0 * math.cos(a), 2.0 * math.sin(a)), ((2.6 + 0.4 * (k % 2)) * math.cos(a), (2.6 + 0.4 * (k % 2)) * math.sin(a))] for k, a in enumerate([k * math.pi / 8 for k in range(16)])]
    moon = circle(0, 0, 1.8, 120)
    ring = circle(0, 0, 2.0, 120)
    diamond = star(1.4, 1.4, 0.35, 4, 0.3)
    return make("Solar Eclipse", corona + [moon, ring, diamond])


@design("wormhole", T)
def wormhole(rng):
    rings = [ellipse(0, 0, 0.4 + 0.5 * k, (0.4 + 0.5 * k) * 0.55, 80) for k in range(6)]
    grid = [[(3.0 * math.cos(a), 3.0 * 0.55 * math.sin(a)), (0.4 * math.cos(a), 0.4 * 0.55 * math.sin(a))] for a in [k * math.pi / 6 for k in range(12)]]
    ship = _rocket(2.4, 2.2, 0.3)
    return make("Wormhole", rings + grid + ship)


@design("neptune", T)
def neptune(rng):
    p = planet(0, 0, 2.2, 4)
    storm = [ellipse(-0.6, 0.5, 0.5, 0.25, 24), arc(-0.6, 0.5, 0.7, math.radians(200), math.radians(340), 12)]
    moon = [circle(2.6, 2.2, 0.35, 20)]
    return make("Neptune", p + storm + moon + stars([(-2.6, -2.4, 0.25)]))


@design("uranus", T)
def uranus(rng):
    p = planet(0, 0, 1.8)
    rings = [ellipse(0, 0, 0.6, 2.8, 100, rot=0.3), ellipse(0, 0, 0.45, 2.4, 90, rot=0.3)]
    return make("Uranus", p + rings + stars([(-2.4, 2.4, 0.25), (2.4, -2.4, 0.2), (2.2, 2.0, 0.2)]))


@design("asteroid_belt", T)
def asteroid_belt(rng):
    rocks = [transform(polar(lambda t, k=k: 0.3 + 0.08 * math.sin(3 * t + k), n=40), dx=3.0 * math.cos(a), dy=1.0 * math.sin(a), s=1.0 - 0.3 * (k % 3) / 2)
             for k, a in enumerate([k * 2 * math.pi / 14 for k in range(14)])]
    sun = circle(0, 0, 0.6, 30)
    return make("Asteroid Belt", rocks + [sun] + stars([(0, 2.4, 0.25), (0, -2.4, 0.2)]))


@design("sputnik", T)
def sputnik(rng):
    ball = circle(0, 0, 1.0, 60)
    seam = [ellipse(0, 0, 1.0, 0.3, 40)]
    antennae = [[(-0.6, -0.6), (-3.0, -2.4)], [(-0.3, -0.8), (-1.6, -3.0)], [(0.3, -0.8), (1.0, -3.0)], [(0.6, -0.6), (2.8, -2.6)]]
    beeps = [arc(0.8, 0.8, r, math.radians(20), math.radians(70), 8) for r in (0.8, 1.2, 1.6)]
    return make("Sputnik", [ball] + seam + antennae + beeps + stars([(-2.2, 2.2, 0.3)]))


@design("capsule_splashdown", T)
def capsule_splashdown(rng):
    capsule = poly((-0.8, -1.0), (-0.4, 0.4), (0.4, 0.4), (0.8, -1.0))
    chutes = []
    for x in (-1.6, 0.0, 1.6):
        chutes += [chain(arc(x, 2.2, 0.8, 0, math.pi, 20), [(x + 0.8, 2.2)]), [(x - 0.8, 2.2), (0, 0.4)], [(x + 0.8, 2.2), (0, 0.4)]]
    water = [wave(-3.4, 3.4, -1.2, 0.12, 6, 80), wave(-3.4, 3.4, -1.8, 0.12, 7, 80)]
    return make("Splashdown", [capsule] + chutes + water)


@design("jetpack", T)
def jetpack(rng):
    helmet = circle(0, 1.6, 0.6, 40)
    body = rrect(-0.6, -0.6, 0.6, 1.0, 0.3)
    pack = [rrect(-1.2, -0.4, -0.6, 1.0, 0.25), rrect(0.6, -0.4, 1.2, 1.0, 0.25)]
    flames = [poly((-1.1, -0.4), (-0.9, -1.6), (-0.7, -0.4), closed=False), poly((0.7, -0.4), (0.9, -1.6), (1.1, -0.4), closed=False)]
    legs = [tube([(-0.3, -0.6), (-0.6, -1.8)], 0.35), tube([(0.3, -0.6), (0.6, -1.8)], 0.35)]
    trail = [quad((-0.9, -1.8), (-1.6, -2.8), (-3.0, -3.0))]
    return make("Jetpack Flyer", [helmet, body] + pack + flames + legs + trail)


@design("moon_phases", T)
def moon_phases(rng):
    out = []
    for k, x in enumerate((-2.6, -1.3, 0.0, 1.3, 2.6)):
        out.append(circle(x, 0.0, 0.55, 40))
        f = [-0.55, -0.3, 0.0, 0.3, 0.55][k]
        if f:
            out.append(arc(x, 0.0, 0.55, -math.pi / 2, math.pi / 2, 20) if f > 0 else arc(x, 0.0, 0.55, math.pi / 2, 1.5 * math.pi, 20))
            out.append([(x + f * math.cos(t), 0.55 * math.sin(t)) for t in [-math.pi / 2 + math.pi * i / 20 for i in range(21)]])
    arcline = [arc(0, -3.0, 4.0, math.radians(50), math.radians(130), 40)]
    return make("Phases of the Moon", out + arcline + stars([(0, 2.0, 0.35)]))


@design("mars_base", T)
def mars_base(rng):
    domes = [chain(arc(-1.4, -1.4, 1.2, 0, math.pi, 30)), chain(arc(1.2, -1.4, 0.9, 0, math.pi, 24))]
    tube_ = [rect(-0.2, -1.4, 0.3, -1.0)]
    windows = [circle(-1.4, -0.8, 0.25, 14), circle(1.2, -0.9, 0.2, 12)]
    antenna = [[(2.6, -1.4), (2.6, 0.6)], arc(2.6, 0.8, 0.4, math.radians(200), math.radians(340), 10)]
    ground = [(-3.4, -1.4), (3.4, -1.4)]
    p = planet(-2.0, 2.2, 0.6)
    return make("Mars Base", domes + tube_ + windows + antenna + [ground] + p + stars([(1.6, 2.4, 0.25)]))


@design("rocket_engines", T)
def rocket_engines(rng):
    base = [rect(-2.4, 0.8, 2.4, 2.6)]
    bells = [chain([(x - 0.4, 0.8)], [(x - 0.7, -0.4), (x + 0.7, -0.4), (x + 0.4, 0.8)]) for x in (-1.5, 0.0, 1.5)]
    flames = [poly((x - 0.6, -0.4), (x - 0.3, -1.6), (x, -0.8), (x + 0.3, -2.4), (x + 0.6, -0.4), closed=False) for x in (-1.5, 0.0, 1.5)]
    smoke = [circle(x, -2.8, 0.5, 20) for x in (-2.4, -1.2, 0.0, 1.2, 2.4)]
    return make("Rocket Engines Firing", base + bells + flames + smoke)


@design("shooting_stars", T)
def shooting_stars(rng):
    out = []
    for x, y, s in [(-1.6, 1.6, 0.5), (1.0, 0.6, 0.6), (-0.4, -1.4, 0.45)]:
        out += [star(x, y, s), quad((x - s, y - 0.2), (x - 1.6, y - 0.6), (x - 2.4, y - 0.4)), quad((x - s, y + 0.1), (x - 1.4, y + 0.2), (x - 2.0, y + 0.5))]
    moon = [arc(2.2, 2.2, 0.6, math.radians(60), math.radians(300), 20)]
    return make("Shooting Stars", out + moon)


@design("space_telescope", T)
def space_telescope(rng):
    tube_ = [rect(-2.4, -0.6, 1.4, 0.6), ellipse(-2.4, 0.0, 0.2, 0.6, 20)]
    door = [poly((1.4, 0.6), (2.4, 1.6), (2.6, 1.4), (1.4, 0.4), closed=False)]
    panels = [rect(-1.4, 0.8, -0.4, 2.8), rect(-1.4, -2.8, -0.4, -0.8)] + [[(-1.4, y), (-0.4, y)] for y in (1.4, 2.2, -1.4, -2.2)]
    bands = [[(x, -0.6), (x, 0.6)] for x in (-1.6, -0.2)]
    return make("Space Telescope", tube_ + door + panels + bands + stars([(2.6, -2.4, 0.3), (2.4, 2.6, 0.25)]))
