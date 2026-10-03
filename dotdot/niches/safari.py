"""Safari Animals niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "safari"


@design("lion", T)
def lion(rng):
    mane = polar(lambda t: 2.0 + 0.22 * math.sin(16 * t), n=500)
    face = circle(0, -0.1, 1.25, 100)
    ears = [circle(-1.0, 0.9, 0.3, 24), circle(1.0, 0.9, 0.3, 24)]
    muzzle = [ellipse(-0.35, -0.6, 0.45, 0.35, 30), ellipse(0.35, -0.6, 0.45, 0.35, 30)]
    nose = poly((-0.3, -0.15), (0.3, -0.15), (0, -0.45))
    mouth = arc(0, -0.95, 0.25, math.radians(200), math.radians(340), 10)
    return Design("Lion King", [mane, face, nose, mouth] + ears + muzzle, [eye(-0.45, 0.25, 0.13), eye(0.45, 0.25, 0.13)], T)


@design("elephant", T)
def elephant(rng):
    body = ellipse(0.6, -0.2, 2.0, 1.4, 140)
    head = circle(-1.4, 0.6, 1.0, 90)
    ear = chain(cubic((-1.0, 1.4), (0.4, 2.0), (0.6, -0.4), (-0.6, -0.4), 40))
    trunk = tube(cubic((-2.1, 0.2), (-2.6, -1.0), (-2.4, -2.0), (-3.0, -2.2), 40), lambda t: 0.5 - 0.25 * t)
    tusk = quad((-1.8, -0.3), (-1.9, -0.9), (-1.4, -1.0))
    legs = [leg(x, x + 0.6, -0.85, -2.6) for x in (-0.6, 0.3, 1.2, 1.9)]
    tail = quad((2.55, 0.0), (3.0, -0.3), (2.9, -0.9))
    return Design("Elephant", [body, head, ear, trunk, tusk, tail] + legs, [eye(-1.65, 0.85, 0.1)], T)


@design("giraffe", T)
def giraffe(rng):
    body = ellipse(0.8, -0.6, 1.5, 0.85, 100)
    neck = tube([(-0.2, -0.2), (-1.1, 2.4)], 0.65, cap=False)
    head = ellipse(-1.4, 2.8, 0.75, 0.45, 50, rot=-0.3)
    ossicones = [[(-1.3, 3.2), (-1.3, 3.7)], [(-0.9, 3.1), (-0.9, 3.6)]]
    knobs = [circle(-1.3, 3.75, 0.1, 10), circle(-0.9, 3.65, 0.1, 10)]
    legs = [[(x, -1.3), (x, -3.2)] for x in (-0.3, 0.2, 1.4, 1.9)]
    spots = [ellipse(x, y, 0.28, 0.2, 18) for x, y in [(0.2, -0.4), (0.9, -0.2), (1.5, -0.7), (0.6, -0.9), (-0.5, 0.6), (-0.8, 1.6)]]
    tail = [(2.3, -0.4), (2.7, -1.2)]
    return Design("Giraffe", [body, neck, head, tail] + ossicones + knobs + legs + spots, [eye(-1.5, 2.9, 0.08)], T)


@design("zebra", T)
def zebra(rng):
    head = chain(cubic((-0.8, 2.0), (-1.4, 0.6), (-0.9, -1.6), (-0.4, -2.0), 40), [(0.4, -2.0)],
                 cubic((0.4, -2.0), (0.9, -1.6), (1.4, 0.6), (0.8, 2.0), 40), quad((0.8, 2.0), (0, 2.4), (-0.8, 2.0), 20))
    ears = [lens((-0.6, 2.1), (-1.0, 3.1), 0.3), lens((0.6, 2.1), (1.0, 3.1), 0.3)]
    nose = ellipse(0, -1.5, 0.6, 0.45, 40)
    stripes = [quad((-1.0 + 0.05 * k, 1.4 - 0.55 * k), (-0.5, 1.2 - 0.55 * k), (-0.2, 1.5 - 0.55 * k)) for k in range(5)] + \
              [quad((1.0 - 0.05 * k, 1.4 - 0.55 * k), (0.5, 1.2 - 0.55 * k), (0.2, 1.5 - 0.55 * k)) for k in range(5)]
    mane = zigzag(-0.4, 0.4, 2.45, 0.12, 4)
    return Design("Zebra", [head, nose, mane] + ears + stripes, [eye(-0.5, 0.7, 0.12), eye(0.5, 0.7, 0.12)], T)


@design("hippo", T)
def hippo(rng):
    head = chain(cubic((-1.4, 1.6), (-2.0, 0.6), (-2.2, -1.4), (0, -1.6), 40), cubic((0, -1.6), (2.2, -1.4), (2.0, 0.6), (1.4, 1.6), 40),
                 quad((1.4, 1.6), (0, 2.2), (-1.4, 1.6), 20))
    nostrils = [ellipse(-0.6, -0.6, 0.2, 0.3, 16), ellipse(0.6, -0.6, 0.2, 0.3, 16)]
    eyes_ = [circle(-0.8, 1.9, 0.4, 30), circle(0.8, 1.9, 0.4, 30)]
    ears = [ellipse(-1.4, 2.3, 0.2, 0.3, 16), ellipse(1.4, 2.3, 0.2, 0.3, 16)]
    water = [wave(-3.0, 3.0, -1.9, 0.12, 5, 100)]
    return Design("Hippo", [head] + nostrils + eyes_ + ears + water, [eye(-0.75, 1.95, 0.13), eye(0.85, 1.95, 0.13)], T)


@design("monkey", T)
def monkey(rng):
    head = circle(0, 1.2, 1.1, 90)
    face = chain(cubic((0, 1.3), (-1.0, 1.9), (-1.0, 0.0), (0, 0.2), 30), cubic((0, 0.2), (1.0, 0.0), (1.0, 1.9), (0, 1.3), 30))
    ears = [circle(-1.25, 1.2, 0.4, 30), circle(1.25, 1.2, 0.4, 30)]
    body = ellipse(0, -1.2, 0.9, 1.1, 70)
    arm = tube(cubic((0.7, -0.6), (1.8, 0.0), (2.0, 1.6), (2.4, 2.6), 30), 0.3)
    branch = [(1.0, 2.7), (3.4, 2.4)]
    tail = cubic((0.6, -2.0), (1.6, -2.6), (2.4, -1.8), (2.0, -1.2), 30)
    banana = [lens((-1.8, -1.0), (-1.0, -2.0), 0.25)]
    smile = arc(0, 0.75, 0.3, math.radians(210), math.radians(330), 12)
    return Design("Cheeky Monkey", [head, face, body, arm, branch, tail, smile] + ears + banana, [eye(-0.3, 1.15, 0.1), eye(0.3, 1.15, 0.1)], T)


@design("acacia", T)
def acacia(rng):
    trunk = [quad((-0.2, -2.6), (0.0, -0.8), (-0.8, 0.8)), quad((0.2, -2.6), (0.2, -0.8), (0.9, 0.9)), [(0, -0.6), (0.2, 0.9)]]
    canopy = chain(cubic((-3.0, 1.0), (-2.6, 2.2), (2.6, 2.2), (3.0, 1.0), 60), quad((3.0, 1.0), (0, 0.5), (-3.0, 1.0), 40))
    sun = circle(2.2, 3.0, 0.6, 50)
    grass = [zigzag(-3.2, 3.2, -2.6, 0.15, 16)]
    birds = [poly((x - 0.3, y), (x, y + 0.15), (x + 0.3, y), closed=False) for x, y in [(-1.8, 3.0), (-1.2, 3.4)]]
    return Design("Acacia Tree", trunk + [canopy, sun] + grass + birds, [], T)


@design("crocodile", T)
def crocodile(rng):
    body = chain(quad((-3.2, 0.2), (-2.0, 0.8), (-0.6, 0.6), 20), quad((-0.6, 0.6), (1.6, 0.9), (3.4, 0.0), 20),
                 quad((3.4, 0.0), (1.6, -0.5), (-0.6, -0.4), 20), [(-3.2, -0.1)])
    jaw = [(-3.2, 0.05), (-1.4, 0.05)]
    teeth = zigzag(-3.0, -1.6, 0.0, 0.08, 6)
    eye_bump = arc(-1.2, 0.7, 0.3, 0, math.pi, 12)
    scutes = [arc(x, 0.65, 0.2, 0, math.pi, 8) for x in (0.0, 0.5, 1.0, 1.5, 2.0)]
    legs = [poly((x, -0.35), (x - 0.2, -1.0), (x + 0.3, -1.0), closed=False) for x in (-0.6, 1.4)]
    water = [wave(-3.4, 3.4, -1.3, 0.1, 6, 100)]
    return Design("Crocodile", [body, jaw, teeth, eye_bump] + scutes + legs + water, [eye(-1.2, 0.8, 0.08)], T)


@design("rhino", T)
def rhino(rng):
    body = ellipse(0.6, -0.2, 2.0, 1.3, 140)
    head = chain(cubic((-1.2, 0.8), (-2.2, 0.8), (-3.0, 0.0), (-2.8, -0.8), 30), quad((-2.8, -0.8), (-1.8, -1.0), (-1.1, -0.6), 20))
    horns = [poly((-2.6, -0.1), (-3.0, 1.1), (-2.2, 0.3), closed=False), poly((-1.9, 0.5), (-2.0, 1.1), (-1.6, 0.65), closed=False)]
    ear = lens((-1.2, 0.9), (-1.0, 1.6), 0.3)
    legs = [leg(x, x + 0.55, -0.85, -2.4) for x in (-0.6, 0.3, 1.2, 1.9)]
    tail = quad((2.6, 0.0), (3.0, -0.3), (2.9, -0.8))
    return Design("Rhino", [body, head, ear, tail] + horns + legs, [eye(-1.7, 0.2, 0.08)], T)
