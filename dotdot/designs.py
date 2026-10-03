"""Built-in, original line-art designs.

Every design is a function `fn(rng) -> Design`.  `rng` is a seeded
`random.Random`, so each family can produce many distinct pictures
(a 100-page book needs variety) while staying reproducible.
"""
import math
from dataclasses import dataclass, field

from .geometry import (TAU, arc, chain, circle, cubic, ellipse, mirror_x,
                       parametric, polar, quad, transform)


@dataclass
class Design:
    title: str
    strokes: list
    hints: list = field(default_factory=list)  # lines pre-printed on the puzzle
    theme: str = "misc"


REGISTRY = {}


def design(name, theme):
    def deco(fn):
        REGISTRY[name] = (fn, theme)
        return fn
    return deco


# ------------------------------------------------------------ nature

@design("butterfly", "animals")
def butterfly(rng):
    def wing_r(t, s=1.0):
        return s * (math.exp(math.sin(t)) - 2 * math.cos(4 * t) + math.sin((2 * t - math.pi) / 24) ** 5)

    # Fay's butterfly curve (one pass), turned upright.
    outer = parametric(lambda t: math.sin(t) * wing_r(t), lambda t: math.cos(t) * wing_r(t) * 0.92,
                       0, TAU, 1400)
    inner_scale = rng.uniform(0.45, 0.6)
    inner = parametric(lambda t: math.sin(t) * wing_r(t, inner_scale),
                       lambda t: math.cos(t) * wing_r(t, inner_scale) * 0.92 + 0.25, 0, TAU, 900)
    body = ellipse(0, 0.6, 0.18, 1.55, 90)
    head = circle(0, 2.35, 0.3, 50)
    ant_l = cubic((-0.1, 2.6), (-0.3, 3.3), (-0.9, 3.7), (-1.3, 3.9), 40)
    ant_r = mirror_x(ant_l)
    spots = []
    for _ in range(rng.randint(1, 3)):
        x, y, r = rng.uniform(1.4, 2.2), rng.uniform(-1.8, 1.8), rng.uniform(0.18, 0.35)
        spots.append(circle(x, y, r, 40))
        spots.append(circle(-x, y, r, 40))
    hints = [circle(-1.3, 3.9, 0.08, 12), circle(1.3, 3.9, 0.08, 12)]
    return Design("Butterfly", [outer, inner, body, head, ant_l, ant_r] + spots, hints, "animals")


@design("flower", "flowers")
def flower(rng):
    k = rng.choice([5, 6, 7, 8])
    petal_r = lambda t: 1.0 + 0.0 * t
    # Petals: polar curve with k bumps on an inner ring.
    bloom = polar(lambda t: 0.55 + 0.75 * abs(math.cos(k * t / 2)) ** 0.7, n=1600)
    inner = polar(lambda t: 0.42 + 0.22 * abs(math.cos(k * t / 2 + math.pi / 2)) ** 0.8, n=900)
    centre = circle(0, 0, 0.3, 60)
    stem = cubic((0.05, -1.25), (0.3, -2.3), (-0.3, -3.2), (0.1, -4.6), 60)
    leaf_l = chain(quad((0.12, -3.0), (-0.8, -2.3), (-1.5, -2.7)), quad((-1.5, -2.7), (-0.7, -3.3), (0.12, -3.0)))
    leaf_r = chain(quad((0.0, -3.7), (0.9, -3.0), (1.5, -3.3)), quad((1.5, -3.3), (0.8, -4.0), (0.0, -3.7)))
    vein_l = quad((0.05, -3.0), (-0.7, -2.75), (-1.35, -2.72))
    vein_r = quad((0.0, -3.7), (0.8, -3.4), (1.35, -3.32))
    hints = [circle(0, 0, 0.06, 10)]
    return Design("Garden Flower", [bloom, inner, centre, stem, leaf_l, leaf_r, vein_l, vein_r], hints, "flowers")


@design("sunflower", "flowers")
def sunflower(rng):
    n = rng.choice([13, 16, 18, 21])
    petals = []
    for i in range(n):
        a = TAU * i / n
        petal = chain(quad((0.95, -0.18), (1.75, -0.32), (2.3, 0.0)), quad((2.3, 0.0), (1.75, 0.32), (0.95, 0.18)))
        petals.append(transform(petal, rot=a))
    disc = circle(0, 0, 1.0, 140)
    spirals = []
    for j in range(8):
        a0 = TAU * j / 8
        spirals.append(polar(lambda t: 0.15 + 0.75 * t / 2.2, 0, 2.2, 60, rot=a0))
    return Design("Sunflower", petals + [disc] + spirals, [], "flowers")


@design("leaf", "nature")
def leaf(rng):
    bend = rng.uniform(-0.4, 0.4)
    outline = chain(cubic((0, -3), (2.2, -1.5 + bend), (1.8, 1.8), (0, 3.3), 120),
                    cubic((0, 3.3), (-1.8, 1.8), (-2.2, -1.5 - bend), (0, -3), 120))
    stem = cubic((0, -3), (0.05, -3.5), (0.2, -4.0), (0.45, -4.4), 30)
    midrib = cubic((0, -3), (0.1, -1), (0.05, 1.5), (0, 3.2), 80)
    veins = []
    for i in range(6):
        y = -2.2 + i * 0.85
        w = 1.45 * math.sin(math.pi * (i + 1) / 7.5)
        veins.append(quad((0.04, y), (w * 0.6, y + 0.25), (w, y + 0.75)))
        veins.append(quad((0.02, y + 0.05), (-w * 0.6, y + 0.3), (-w, y + 0.8)))
    return Design("Leaf", [outline, stem, midrib] + veins, [], "nature")


@design("tree", "nature")
def tree(rng):
    spread = rng.uniform(0.38, 0.5)
    shrink = rng.uniform(0.72, 0.78)
    depth = 6

    def outline(base, ang, length, width, d):
        dx, dy = math.cos(ang), math.sin(ang)
        nx, ny = -dy, dx
        top = (base[0] + dx * length, base[1] + dy * length)
        tw = width * 0.72
        bl = (base[0] + nx * width / 2, base[1] + ny * width / 2)
        br = (base[0] - nx * width / 2, base[1] - ny * width / 2)
        tl = (top[0] + nx * tw / 2, top[1] + ny * tw / 2)
        tr = (top[0] - nx * tw / 2, top[1] - ny * tw / 2)
        if d == 0:
            tip = arc(top[0], top[1], tw / 2, ang + math.pi / 2, ang - math.pi / 2, 6)
            return [bl, tl] + tip[1:-1] + [tr, br]
        jitter = rng.uniform(-0.12, 0.12)
        left = outline(tl, ang + spread + jitter, length * shrink, tw * 0.62, d - 1)
        right = outline(tr, ang - spread + jitter, length * shrink * rng.uniform(0.9, 1.05), tw * 0.62, d - 1)
        return [bl] + left + right + [br]

    trunk = outline((0, 0), math.pi / 2, 2.2, 0.75, depth)
    ground = [(-3.2, 0.0), (-0.45, 0.0)]
    ground2 = [(0.45, 0.0), (3.2, 0.0)]
    grass = []
    for x in (-2.6, -1.4, 1.2, 2.4):
        grass.append([(x - 0.15, 0), (x, 0.35), (x + 0.05, 0), (x + 0.2, 0.3), (x + 0.25, 0)])
    return Design("Windswept Tree", [trunk, ground, ground2] + grass, [], "nature")


@design("nautilus", "sea")
def nautilus(rng):
    b = 0.17 + rng.uniform(-0.01, 0.01)
    turns = 3.0
    r = lambda t: 0.08 * math.exp(b * t)
    t_end = turns * TAU
    spiral = polar(r, 0, t_end, 1500)
    outer_end = spiral[-1]
    # Close the shell mouth back onto the previous whorl.
    mouth_in = (r(t_end - TAU) * math.cos(t_end - TAU), r(t_end - TAU) * math.sin(t_end - TAU))
    shell = chain(spiral, [mouth_in])
    septa = []
    for k in range(1, 18):
        t = t_end - TAU + 0.05 - k * 0.32
        if t < TAU:
            break
        p_out = (r(t) * math.cos(t), r(t) * math.sin(t))
        p_in = (r(t - TAU) * math.cos(t - TAU), r(t - TAU) * math.sin(t - TAU))
        mid = ((p_out[0] + p_in[0]) / 2, (p_out[1] + p_in[1]) / 2)
        bow = 0.18 * math.dist(p_out, p_in)
        ang = t + math.pi / 2
        ctrl = (mid[0] + bow * math.cos(ang), mid[1] + bow * math.sin(ang))
        septa.append(quad(p_out, ctrl, p_in, 16))
    return Design("Nautilus Shell", [shell] + septa, [], "sea")


@design("fish", "sea")
def fish(rng):
    tall = rng.uniform(1.2, 1.6)
    top = cubic((-3, 0), (-1.8, tall * 1.6), (1.2, tall * 1.5), (2.4, 0.25), 80)
    tail_top = [(2.4, 0.25), (3.6, 1.3), (3.25, 0.0), (3.6, -1.3), (2.4, -0.25)]
    bottom = cubic((2.4, -0.25), (1.2, -tall * 1.4), (-1.8, -tall * 1.4), (-3, 0), 80)
    body = chain(top, tail_top, bottom)
    eye = circle(-1.9, 0.35, 0.28, 50)
    gill = arc(-0.5, 0.0, 1.15, math.radians(130), math.radians(230), 40)
    mouth = quad((-3, 0), (-2.65, -0.12), (-2.45, -0.35))
    dorsal = chain(quad((-0.6, tall * 1.18), (0.0, tall * 1.9), (1.2, tall * 1.6)),
                   quad((1.2, tall * 1.6), (0.9, tall * 1.3), (1.1, tall * 1.02)))
    fin = chain(quad((-0.2, -0.3), (0.7, -0.6), (0.6, -1.0)), quad((0.6, -1.0), (0.2, -0.8), (-0.2, -0.3)))
    scales = []
    for col in range(4):
        for row in range(-1, 2):
            cx = 0.1 + col * 0.5
            cy = row * 0.55 + (0.27 if col % 2 else 0)
            if abs(cy) < tall * 0.8 - col * 0.1:
                scales.append(arc(cx, cy, 0.28, math.radians(-70), math.radians(70), 14))
    bubbles = [circle(-3.6, 1.2, 0.18, 30), circle(-3.9, 1.8, 0.26, 36), circle(-3.5, 2.6, 0.34, 40)]
    hints = [circle(-1.95, 0.4, 0.09, 12)]
    return Design("Little Fish", [body, eye, gill, mouth, dorsal, fin] + scales + bubbles, hints, "sea")


@design("turtle", "sea")
def turtle(rng):
    shell = ellipse(0, 0, 2.2, 1.65, 200)
    rim = ellipse(0, 0, 1.75, 1.25, 160)
    hexes = []
    hexes.append([(0.45 * math.cos(a), 0.45 * math.sin(a)) for a in [TAU * i / 6 for i in range(7)]])
    for i in range(6):
        a = TAU * i / 6
        hexes.append([(0.45 * math.cos(a), 0.45 * math.sin(a)), (1.75 * math.cos(a) * 0.98, 1.25 * math.sin(a) * 0.98)])
    head = chain(cubic((2.15, 0.35), (2.7, 0.75), (3.6, 0.6), (3.6, 0.0), 40),
                 cubic((3.6, 0.0), (3.6, -0.6), (2.7, -0.75), (2.15, -0.35), 40))
    legs = []
    for sx, sy, rot in [(1.3, 1.35, 0.6), (1.3, -1.35, -0.6), (-1.4, 1.3, 2.4), (-1.4, -1.3, -2.4)]:
        leg = ellipse(0, 0, 0.75, 0.38, 60)
        legs.append(transform(leg, dx=sx + 0.45 * math.cos(rot), dy=sy + 0.45 * math.sin(rot), rot=rot))
    tail = [(-2.15, 0.15), (-2.7, 0.0), (-2.15, -0.15)]
    hints = [circle(3.15, 0.25, 0.08, 12)]
    return Design("Sea Turtle", [shell, rim] + hexes + [head] + legs + [tail], hints, "sea")


@design("snail", "animals")
def snail(rng):
    turns = rng.uniform(2.6, 3.2)
    shell_spiral = polar(lambda t: 0.12 + 0.24 * t / math.pi, 0, turns * TAU, 900, cx=0, cy=0.9, rot=-turns * TAU)
    r_out = 0.12 + 0.24 * turns * 2
    shell_rim = circle(0, 0.9, r_out, 160)
    body = chain(
        cubic((-r_out * 0.7, 0.9 - r_out * 0.72), (-2.5, -0.6), (-3.2, -0.6), (-3.0, -0.25), 40),
        cubic((-3.0, -0.25), (-2.9, 0.6), (-2.2, 1.2), (-2.0, 1.6), 40),
        cubic((-2.0, 1.6), (-1.9, 1.95), (-2.6, 2.0), (-2.7, 1.6), 30),
        cubic((-2.7, 1.6), (-2.85, 0.9), (-3.6, 0.3), (-3.6, -0.25), 30),
        cubic((-3.6, -0.25), (-3.6, -0.75), (-2.5, -0.85), (r_out * 1.2, -0.75), 60),
        cubic((r_out * 1.2, -0.75), (r_out * 1.5, -0.7), (r_out * 1.5, -0.4), (r_out * 0.8, 0.9 - r_out * 0.62), 30),
    )
    ant1 = quad((-2.3, 1.85), (-2.2, 2.6), (-1.8, 3.0))
    ant2 = quad((-2.55, 1.9), (-2.8, 2.6), (-3.1, 3.0))
    hints = [circle(-1.8, 3.0, 0.1, 12), circle(-3.1, 3.0, 0.1, 12), circle(-2.45, 1.65, 0.06, 10)]
    return Design("Garden Snail", [shell_spiral, shell_rim, body, ant1, ant2], hints, "animals")


@design("cat", "animals")
def cat(rng):
    # Head outline with ears as one continuous closed stroke.
    head = chain(
        arc(0, 0, 2.0, math.radians(-30), math.radians(55), 30),
        [(1.35, 2.7)],
        arc(0, 0, 2.0, math.radians(78), math.radians(102), 12),
        [(-1.35, 2.7)],
        arc(0, 0, 2.0, math.radians(125), math.radians(210), 30),
        cubic((-1.73, -1.0), (-1.2, -2.0), (1.2, -2.0), (1.73, -1.0), 40),
    )
    ear_l = [(-1.0, 1.75), (-1.25, 2.35), (-0.65, 1.95)]
    ear_r = mirror_x(ear_l)
    eye_l = chain(quad((-1.25, 0.45), (-0.8, 0.95), (-0.35, 0.45)), quad((-0.35, 0.45), (-0.8, -0.05), (-1.25, 0.45)))
    eye_r = mirror_x(eye_l)
    nose = [(-0.22, -0.3), (0.22, -0.3), (0.0, -0.55), (-0.22, -0.3)]
    mouth = chain(quad((-0.6, -0.85), (-0.25, -1.1), (0, -0.55)), quad((0, -0.55), (0.25, -1.1), (0.6, -0.85)))
    whiskers = []
    for dy in (-0.45, -0.7, -0.95):
        whiskers.append(quad((0.6, -0.55), (1.6, dy + 0.1), (2.6, dy)))
        whiskers.append(quad((-0.6, -0.55), (-1.6, dy + 0.1), (-2.6, dy)))
    hints = [ellipse(-0.8, 0.45, 0.09, 0.3, 16), ellipse(0.8, 0.45, 0.09, 0.3, 16)]
    return Design("Curious Cat", [head, ear_l, ear_r, eye_l, eye_r, nose, mouth] + whiskers, hints, "animals")


@design("owl", "animals")
def owl(rng):
    body = chain(
        cubic((-1.6, 2.1), (-2.6, 0.5), (-2.4, -2.6), (0, -3.0), 80),
        cubic((0, -3.0), (2.4, -2.6), (2.6, 0.5), (1.6, 2.1), 80),
        [(1.9, 3.0), (0.9, 2.45)],
        quad((0.9, 2.45), (0, 2.75), (-0.9, 2.45)),
        [(-1.9, 3.0), (-1.6, 2.1)],
    )
    eye_l = circle(-0.85, 1.35, 0.75, 90)
    eye_r = circle(0.85, 1.35, 0.75, 90)
    iris_l = circle(-0.85, 1.35, 0.32, 40)
    iris_r = circle(0.85, 1.35, 0.32, 40)
    beak = [(-0.25, 0.6), (0.25, 0.6), (0, 0.05), (-0.25, 0.6)]
    wing_l = cubic((-1.8, 0.4), (-1.0, -0.6), (-1.0, -1.9), (-1.6, -2.5), 50)
    wing_r = mirror_x(wing_l)
    chest = []
    for row in range(3):
        for col in range(-1, 2):
            cx = col * 0.55 + (0.27 if row % 2 else 0)
            if row % 2 and col == 1:
                continue
            chest.append(arc(cx, -0.55 - row * 0.5, 0.25, math.radians(200), math.radians(340), 12))
    branch = [(-3.0, -3.05), (3.0, -3.05)]
    feet = []
    for x in (-0.6, 0.6):
        for dx in (-0.18, 0, 0.18):
            feet.append([(x + dx, -2.95), (x + dx * 1.4, -3.3)])
    hints = [circle(-0.85, 1.35, 0.12, 16), circle(0.85, 1.35, 0.12, 16)]
    return Design("Wise Owl", [body, eye_l, eye_r, iris_l, iris_r, beak, wing_l, wing_r, branch] + chest + feet,
                  hints, "animals")


@design("mushroom", "nature")
def mushroom(rng):
    cap = chain(cubic((-2.6, 0.2), (-2.6, 3.2), (2.6, 3.2), (2.6, 0.2), 140),
                quad((2.6, 0.2), (0, -0.35), (-2.6, 0.2), 60))
    stem = chain(quad((-0.75, 0.0), (-1.0, -1.6), (-0.95, -2.6), 30),
                 quad((-0.95, -2.6), (0, -2.9), (0.95, -2.6), 30),
                 quad((0.95, -2.6), (1.0, -1.6), (0.75, 0.0), 30))
    spots = []
    for x, y, r in [(-1.3, 1.4, 0.38), (0.2, 2.0, 0.45), (1.4, 1.1, 0.33), (-0.4, 0.75, 0.25), (0.9, 0.4, 0.2)]:
        spots.append(circle(x + rng.uniform(-0.1, 0.1), y + rng.uniform(-0.1, 0.1), r, 40))
    grass = [[(-3, -2.7), (-2.7, -2.0), (-2.5, -2.7), (-2.2, -2.2), (-1.9, -2.75)],
             [(1.9, -2.75), (2.2, -2.1), (2.4, -2.7), (2.75, -2.25), (3.0, -2.7)]]
    return Design("Forest Mushroom", [cap, stem] + spots + grass, [], "nature")


# ------------------------------------------------------------ places & things

@design("sailboat", "travel")
def sailboat(rng):
    hull = [(-3.0, 0.0), (3.0, 0.0), (2.2, -1.0), (-2.2, -1.0), (-3.0, 0.0)]
    mast = [(0.0, 0.0), (0.0, 5.0)]
    main = [(0.15, 4.8), (0.15, 0.35), (2.6, 0.35), (0.15, 4.8)]
    jib = [(-0.15, 4.4), (-0.15, 0.35), (-2.2, 0.35), (-0.15, 4.4)]
    flag = [(0, 5.0), (0.8, 4.75), (0, 4.5)]
    waves = []
    for k, y in enumerate((-1.25, -1.75)):
        waves.append(parametric(lambda t: t, lambda t, y=y, k=k: y + 0.18 * math.sin(3 * t + k), -4, 4, 300))
    sun = circle(-3.0, 4.0, 0.7, 80)
    birds = []
    for bx, by in [(2.5, 4.4), (3.3, 3.8)]:
        birds.append(chain(quad((bx - 0.45, by), (bx - 0.2, by + 0.25), (bx, by)), quad((bx, by), (bx + 0.2, by + 0.25), (bx + 0.45, by))))
    portholes = [circle(x, -0.5, 0.17, 24) for x in (-1.2, 0.0, 1.2)]
    return Design("Sailboat", [hull, mast, main, jib, flag, sun] + waves + birds + portholes, [], "travel")


@design("house", "travel")
def house(rng):
    walls = [(-2.2, 0), (2.2, 0), (2.2, 2.6), (-2.2, 2.6), (-2.2, 0)]
    roof = [(-2.7, 2.5), (0, 4.6), (2.7, 2.5)]
    chimney = [(1.1, 3.75), (1.1, 4.7), (1.7, 4.7), (1.7, 3.28)]
    door = [(-0.45, 0), (-0.45, 1.6), (0.45, 1.6), (0.45, 0)]
    win_l = [(-1.75, 1.2), (-0.95, 1.2), (-0.95, 2.0), (-1.75, 2.0), (-1.75, 1.2)]
    win_r = transform(win_l, dx=2.7)
    bars = [[(-1.35, 1.2), (-1.35, 2.0)], [(-1.75, 1.6), (-0.95, 1.6)],
            [(1.35, 1.2), (1.35, 2.0)], [(0.95, 1.6), (1.75, 1.6)]]
    attic = circle(0, 3.35, 0.38, 50)
    smoke = polar(lambda t: 0.1 + 0.14 * t, 0, 3.5 * math.pi, 300, cx=1.6, cy=5.6)
    path = [quad((-0.45, 0), (-0.8, -0.8), (-1.6, -1.5)), quad((0.45, 0), (0.1, -0.8), (-0.6, -1.5))]
    fence = []
    for x in (2.6, 3.0, 3.4):
        fence.append([(x, 0), (x, 1.0), (x + 0.1, 1.2), (x + 0.2, 1.0), (x + 0.2, 0)])
    ground = [(-3.6, 0), (3.8, 0)]
    return Design("Cozy Cottage", [walls, roof, chimney, door, win_l, win_r, attic, smoke, ground] + bars + path + fence,
                  [circle(0.25, 0.8, 0.06, 10)], "travel")


@design("balloon", "travel")
def balloon(rng):
    def env(t):
        # Teardrop envelope: round top, narrowing to the basket throat.
        x = 2.3 * math.sin(t) * (1 - 0.35 * (1 - math.cos(t)) / 2) if t < math.pi else 0
        return x
    right = parametric(lambda t: 2.4 * math.sin(t) ** 1.0 * (0.62 + 0.38 * math.sin(t / 2) ** 0.4) if t < math.pi else 0,
                       lambda t: 1.0 + 2.5 * math.cos(t), 0.0, math.pi * 0.86, 160)
    left = mirror_x(right)[::-1]
    outline = chain(left, right[1:])
    throat = [outline[-1], (0.5, -1.0), (-0.5, -1.0), outline[0]]
    gores = []
    for f in (-0.55, 0.0, 0.55):
        gores.append(parametric(lambda t, f=f: f * 2.0 * math.sin(t) * (0.62 + 0.38 * math.sin(t / 2) ** 0.4),
                                lambda t: 1.0 + 2.5 * math.cos(t), 0.0, math.pi * 0.86, 120))
    basket = [(-0.45, -1.7), (0.45, -1.7), (0.38, -2.4), (-0.38, -2.4), (-0.45, -1.7)]
    ropes = [[(-0.5, -1.0), (-0.45, -1.7)], [(0.5, -1.0), (0.45, -1.7)]]
    clouds = []
    for cx, cy, s in [(-3.0, 2.6, 0.5), (3.0, -0.8, 0.6)]:
        cl = chain(arc(cx - s, cy, s, math.pi, 0, 20), arc(cx + s * 0.4, cy + s * 0.3, s * 0.9, math.pi * 0.9, 0, 20),
                   arc(cx + s * 1.6, cy, s * 0.6, math.pi, 0, 14))
        cl.append((cx - 2 * s, cy))
        clouds.append(cl)
    return Design("Hot Air Balloon", [outline, throat, basket] + gores + ropes + clouds, [], "travel")


@design("lighthouse", "travel")
def lighthouse(rng):
    tower = [(-1.0, 0), (-0.6, 4.0), (0.6, 4.0), (1.0, 0)]
    gallery = [(-0.9, 4.0), (0.9, 4.0), (0.9, 4.25), (-0.9, 4.25), (-0.9, 4.0)]
    lamp = [(-0.5, 4.25), (-0.5, 5.0), (0.5, 5.0), (0.5, 4.25)]
    cap = [(-0.65, 5.0), (0, 5.6), (0.65, 5.0)]
    stripes = [[(-0.87, 1.3), (0.87, 1.3)], [(-0.81, 1.9), (0.81, 1.9)], [(-0.71, 2.9), (0.71, 2.9)], [(-0.65, 3.5), (0.65, 3.5)]]
    door = [(-0.3, 0), (-0.3, 0.7), (0.3, 0.7), (0.3, 0)]
    beams = [[(0.6, 4.75), (3.6, 5.4)], [(0.6, 4.5), (3.6, 4.0)], [(-0.6, 4.75), (-3.6, 5.4)], [(-0.6, 4.5), (-3.6, 4.0)]]
    rocks = chain(quad((-3.5, 0), (-2.5, 0.6), (-1.5, 0.15)), quad((-1.5, 0.15), (-1.2, 0.1), (-1.0, 0)))
    rocks2 = chain(quad((1.0, 0), (2.0, 0.7), (3.5, 0)))
    sea = parametric(lambda t: t, lambda t: -0.5 + 0.15 * math.sin(4 * t), -3.8, 3.8, 300)
    return Design("Lighthouse", [tower, gallery, lamp, cap, door, rocks, rocks2, sea] + stripes + beams, [], "travel")


# ------------------------------------------------------------ geometric / mindful

@design("hearts", "patterns")
def hearts(rng):
    def heart(s, dy=0.0):
        return parametric(lambda t: s * 16 * math.sin(t) ** 3,
                          lambda t: dy + s * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)),
                          0, TAU, 500)
    n = rng.randint(3, 4)
    strokes = [heart(0.2 * (1 - i * 0.22), dy=i * 0.25) for i in range(n)]
    small = []
    for x, y, s in [(-4.2, 3.0, 0.045), (4.0, 3.4, 0.055), (3.8, -2.8, 0.04)]:
        small.append(transform(heart(1), dx=x, dy=y, s=s))
    return Design("Hearts", strokes + small, [], "patterns")


@design("spirograph", "patterns")
def spirograph(rng):
    while True:
        R = rng.randint(7, 13)
        r = rng.randint(2, R - 2)
        if math.gcd(R, r) in (1, 2) and R // math.gcd(R, r) >= 5:
            break
    d = rng.uniform(0.5, 1.1) * r
    g = math.gcd(R, r)
    turns = r // g
    pts = parametric(lambda t: (R - r) * math.cos(t) + d * math.cos((R - r) / r * t),
                     lambda t: (R - r) * math.sin(t) - d * math.sin((R - r) / r * t),
                     0, TAU * turns, 600 * turns)
    ring = circle(0, 0, R - r + d + 0.8, 200)
    return Design("Spirograph", [pts, ring], [], "patterns")


@design("mandala", "patterns")
def mandala(rng):
    strokes = []
    r = 0.6
    strokes.append(circle(0, 0, r * 0.6, 60))
    layers = rng.randint(4, 5)
    for i in range(layers):
        n = rng.choice([6, 8, 10, 12, 16]) if i else rng.choice([6, 8])
        depth = rng.uniform(0.45, 0.8)
        p = rng.choice([0.5, 1.0, 2.0])
        phase = rng.choice([0, math.pi / n])
        strokes.append(polar(lambda t, r=r, n=n, d=depth, p=p, ph=phase:
                             r + d * abs(math.cos(n * (t + ph) / 2)) ** p, n=2000))
        r += depth + 0.08
        if rng.random() < 0.6:
            strokes.append(circle(0, 0, r, 220))
            r += 0.12
    return Design("Mandala", strokes, [circle(0, 0, 0.1, 12)], "patterns")


@design("snowflake", "patterns")
def snowflake(rng):
    level = 4

    def koch(a, b, d):
        if d == 0:
            return [a]
        dx, dy = (b[0] - a[0]) / 3, (b[1] - a[1]) / 3
        p1 = (a[0] + dx, a[1] + dy)
        p3 = (a[0] + 2 * dx, a[1] + 2 * dy)
        ang = math.atan2(dy, dx) + math.pi / 3
        L = math.hypot(dx, dy)
        p2 = (p1[0] + L * math.cos(ang), p1[1] + L * math.sin(ang))
        return koch(a, p1, d - 1) + koch(p1, p2, d - 1) + koch(p2, p3, d - 1) + koch(p3, b, d - 1)

    tri = [(math.cos(a), math.sin(a)) for a in (math.pi / 2, math.pi / 2 - TAU / 3, math.pi / 2 - 2 * TAU / 3)]
    outer = []
    for i in range(3):
        outer += koch(tri[i], tri[(i + 1) % 3], level)
    outer.append(outer[0])
    inner_hex = [(0.35 * math.cos(a), 0.35 * math.sin(a)) for a in [math.pi / 2 + TAU * i / 6 for i in range(7)]]
    return Design("Koch Snowflake", [outer, inner_hex], [], "patterns")


@design("dragon", "patterns")
def dragon(rng):
    level = rng.choice([9, 10])
    turns = [1]
    for _ in range(level - 1):
        turns = turns + [1] + [-t for t in reversed(turns)]
    x = y = 0
    d = 0
    pts = [(0, 0)]
    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    x, y = 1, 0
    pts.append((x, y))
    for t in turns:
        d = (d + t) % 4
        x += dirs[d][0]
        y += dirs[d][1]
        pts.append((x, y))
    # Round the corners slightly so the path never touches itself visually.
    soft = []
    for a, b in zip(pts, pts[1:]):
        soft.append((a[0] + (b[0] - a[0]) * 0.18, a[1] + (b[1] - a[1]) * 0.18))
        soft.append((a[0] + (b[0] - a[0]) * 0.82, a[1] + (b[1] - a[1]) * 0.82))
    return Design("Dragon Curve", [soft], [], "patterns")


@design("sun", "patterns")
def sun(rng):
    n = rng.choice([12, 14, 16])
    rays = polar(lambda t: 2.4 + 0.55 * math.sin(n * t) + 0.25 * math.sin(2 * n * t), n=2000)
    face = circle(0, 0, 1.55, 160)
    eye_l = arc(-0.55, 0.35, 0.3, math.radians(20), math.radians(160), 20)
    eye_r = arc(0.55, 0.35, 0.3, math.radians(20), math.radians(160), 20)
    smile = arc(0, 0.1, 0.85, math.radians(215), math.radians(325), 40)
    cheeks = [circle(-0.9, -0.3, 0.2, 24), circle(0.9, -0.3, 0.2, 24)]
    return Design("Smiling Sun", [rays, face, eye_l, eye_r, smile] + cheeks, [], "patterns")


@design("star", "patterns")
def star(rng):
    k = rng.choice([(5, 2), (7, 3), (8, 3), (9, 4), (11, 4)])
    n, m = k
    pts = [(math.cos(math.pi / 2 + TAU * (i * m % n) / n), math.sin(math.pi / 2 + TAU * (i * m % n) / n)) for i in range(n + 1)]
    outer = circle(0, 0, 1.12, 200)
    inner = [(0.35 * math.cos(math.pi / 2 + TAU * i / n), 0.35 * math.sin(math.pi / 2 + TAU * i / n)) for i in range(n + 1)]
    return Design(f"{n}-Point Star", [pts, outer, inner], [], "patterns")


def decorate(d, aspect, rng):
    """Add a decorative dotted border that fills the page around a design.
    Used when a picture alone cannot carry the requested number of dots."""
    from .geometry import bounds
    x0, y0, x1, y1 = bounds(d.strokes + d.hints)
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    # Grow the box to the page's aspect ratio, plus breathing room.
    if w / h < aspect:
        w = h * aspect
    else:
        h = w / aspect
    w, h = w * 1.14, h * 1.14
    style = rng.choice(["wave", "scallop", "double", "zigzag"])
    size = min(w, h)
    amp = size * 0.018

    def rect_path(ww, hh, n=1600):
        per = 2 * (ww + hh)
        pts = []
        for i in range(n + 1):
            s = per * i / n
            if s < ww:
                p, nrm = (cx - ww / 2 + s, cy + hh / 2), (0, 1)
            elif s < ww + hh:
                p, nrm = (cx + ww / 2, cy + hh / 2 - (s - ww)), (1, 0)
            elif s < 2 * ww + hh:
                p, nrm = (cx + ww / 2 - (s - ww - hh), cy - hh / 2), (0, -1)
            else:
                p, nrm = (cx - ww / 2, cy - hh / 2 + (s - 2 * ww - hh)), (-1, 0)
            pts.append((p, nrm, s, per))
        return pts

    def offset(pts, f):
        return [(p[0] + nrm[0] * f(s, per), p[1] + nrm[1] * f(s, per)) for p, nrm, s, per in pts]

    base = rect_path(w, h)
    waves = rng.choice([40, 48, 56])
    if style == "wave":
        border = [offset(base, lambda s, per: amp * math.sin(TAU * waves * s / per))]
    elif style == "scallop":
        border = [offset(base, lambda s, per: amp * 1.3 * abs(math.sin(math.pi * waves * s / per)))]
    elif style == "zigzag":
        border = [offset(base, lambda s, per: amp * (2 * abs(2 * ((waves * s / per) % 1) - 1) - 1))]
    else:
        border = [offset(base, lambda s, per: 0.0), offset(rect_path(w * 0.965, h * 0.965), lambda s, per: 0.0)]
    for b in border:
        b[-1] = b[0]
    return Design(d.title, d.strokes + border, d.hints, d.theme)


def build(name, seed):
    import random
    fn, theme = REGISTRY[name]
    d = fn(random.Random(seed))
    d.theme = theme
    return d
