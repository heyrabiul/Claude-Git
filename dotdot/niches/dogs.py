"""Dogs niche."""
import math

from ._kit import *  # noqa: F401,F403  (shared drawing kit)

T = "dogs"


@design("puppy_face", T)
def puppy_face(rng):
    head = ellipse(0, 0.3, 1.6, 1.5, 140)
    ear_l = chain(cubic((-1.2, 1.4), (-2.4, 1.6), (-2.6, -0.6), (-1.9, -1.0), 40), quad((-1.9, -1.0), (-1.5, -0.6), (-1.5, 0.5), 20))
    ear_r = mirror_x(ear_l)
    muzzle = ellipse(0, -0.45, 0.8, 0.6, 60)
    nose = chain(quad((-0.3, -0.1), (0, 0.15), (0.3, -0.1)), quad((0.3, -0.1), (0, -0.45), (-0.3, -0.1)))
    mouth = chain(quad((-0.45, -0.75), (-0.15, -0.9), (0, -0.45)), quad((0, -0.45), (0.15, -0.9), (0.45, -0.75)))
    tongue = chain(quad((-0.2, -0.85), (0, -1.45), (0.2, -0.85)))
    brows = [arc(-0.55, 0.85, 0.3, math.radians(40), math.radians(140), 10), arc(0.55, 0.85, 0.3, math.radians(40), math.radians(140), 10)]
    return Design("Happy Puppy", [head, ear_l, ear_r, muzzle, nose, mouth, tongue] + brows,
                  [eye(-0.55, 0.5, 0.16), eye(0.55, 0.5, 0.16)], T)


@design("sitting_dog", T)
def sitting_dog(rng):
    head = circle(0.2, 2.0, 0.85, 80)
    snout = chain(quad((0.8, 1.7), (1.7, 1.8), (1.65, 1.35)), quad((1.65, 1.35), (1.2, 1.05), (0.75, 1.35)))
    ear = chain(cubic((-0.3, 2.6), (-1.2, 2.6), (-1.1, 1.2), (-0.55, 1.3), 30))
    body = chain(cubic((-0.4, 1.3), (-1.4, 0.4), (-1.6, -1.6), (-1.0, -2.2), 40), [(1.1, -2.2)],
                 cubic((1.1, -2.2), (1.2, -1.0), (0.9, 0.6), (0.6, 1.25), 40))
    legs = [[(0.2, 0.5), (0.3, -2.2)], [(0.75, 0.3), (0.85, -2.2)]]
    tail = cubic((-1.4, -1.6), (-2.3, -1.4), (-2.4, -0.5), (-2.0, 0.0), 30)
    collar = [quad((-0.4, 1.3), (0.15, 1.05), (0.65, 1.25)), circle(0.15, 0.85, 0.2, 20)]
    return Design("Loyal Dog", [head, snout, ear, body, tail] + legs + collar,
                  [eye(0.45, 2.2, 0.12), eye(1.6, 1.55, 0.12)], T)


@design("dachshund", T)
def dachshund(rng):
    body = rrect(-2.4, -0.6, 1.8, 0.6, 0.55)
    head = chain(cubic((1.4, 0.5), (1.5, 1.6), (2.4, 1.7), (2.9, 1.1), 30), quad((2.9, 1.1), (3.3, 0.7), (2.6, 0.55), 12),
                 quad((2.6, 0.55), (1.9, 0.5), (1.6, 0.1), 12))
    ear = chain(cubic((1.8, 1.4), (1.2, 1.4), (1.3, 0.3), (1.7, 0.5), 20))
    legs = [rect(x, -1.4, x + 0.4, -0.55) for x in (-2.1, -1.4, 0.9, 1.4)]
    tail = quad((-2.35, 0.3), (-3.0, 0.6), (-3.2, 1.2))
    collar = [(1.55, 0.6), (1.75, -0.15)]
    return Design("Dachshund", [body, head, ear, tail, collar] + legs, [eye(2.35, 1.2, 0.1), eye(3.05, 0.85, 0.09)], T)


@design("poodle", T)
def poodle(rng):
    puffs = [circle(0, 2.3, 0.75, 70), circle(-0.1, 0.6, 1.0, 90), circle(-1.6, 0.9, 0.5, 50)]
    head = ellipse(0.6, 1.4, 0.6, 0.45, 50)
    snout = quad((1.1, 1.5), (1.7, 1.4), (1.15, 1.1))
    legs = [[(x, -0.35), (x, -1.9)] for x in (-0.6, 0.4)]
    feet = [circle(x, -2.1, 0.32, 30) for x in (-0.6, 0.4)]
    ear = ellipse(0.25, 1.1, 0.3, 0.55, 40)
    bow = [lens((-0.35, 2.95), (-0.8, 3.3), 0.4), lens((-0.35, 2.95), (0.1, 3.3), 0.4)]
    return Design("Poodle", puffs + [head, snout, ear] + legs + feet + bow, [eye(0.8, 1.55, 0.1)], T)


@design("dog_bone", T)
def dog_bone(rng):
    bone = chain(arc(-2.0, 0.45, 0.55, math.radians(-30), math.radians(220), 30),
                 arc(-2.0, -0.45, 0.55, math.radians(140), math.radians(390), 30),
                 arc(2.0, -0.45, 0.55, math.radians(-220), math.radians(30), 30),
                 arc(2.0, 0.45, 0.55, math.radians(-40), math.radians(210), 30), [(-1.53, 0.17)])
    shine = quad((-1.2, 0.05), (0, 0.15), (1.2, 0.05))
    return Design("Dog Bone", [bone, shine], [], T)


@design("doghouse", T)
def doghouse(rng):
    walls = rect(-1.8, -2.0, 1.8, 0.8)
    roof = poly((-2.3, 0.6), (0, 2.6), (2.3, 0.6), closed=False)
    door = chain([(-0.8, -2.0), (-0.8, -0.4)], arc(0, -0.4, 0.8, math.pi, 0, 30), [(0.8, -2.0)])
    sign = rrect(-0.9, 1.0, 0.9, 1.6, 0.15)
    boards = [[(-1.8, y), (-1.0, y)] for y in (-1.2, -0.4, 0.4)] + [[(1.0, y), (1.8, y)] for y in (-1.2, -0.4, 0.4)]
    bowl = chain([(2.2, -2.0)], quad((2.3, -2.4), (3.0, -2.4), (3.1, -2.0)), [(2.2, -2.0)])
    return Design("Dog House", [walls, roof, door, sign, bowl] + boards, [], T)


@design("tennis_ball", T)
def tennis_ball(rng):
    ball = circle(0, 0, 1.8, 160)
    seams = [arc(-2.4, 0, 1.6, math.radians(-48), math.radians(48), 30), arc(2.4, 0, 1.6, math.radians(132), math.radians(228), 30)]
    motion = [[(-3.6, y), (-2.3, y)] for y in (0.8, 0.0, -0.8)]
    return Design("Tennis Ball", [ball] + seams + motion, [], T)


@design("hydrant", T)
def hydrant(rng):
    body = rect(-0.8, -2.0, 0.8, 0.9)
    dome = chain(arc(0, 0.9, 0.85, 0, math.pi, 30), [(0.85, 0.9)])
    cap = rect(-0.2, 1.7, 0.2, 2.1)
    base = rect(-1.2, -2.4, 1.2, -2.0)
    band = rect(-1.0, 0.5, 1.0, 0.9)
    nozzles = [rect(-1.4, -0.7, -0.8, -0.1), rect(0.8, -0.7, 1.4, -0.1)]
    bolt = circle(0, -0.4, 0.3, 30)
    return Design("Fire Hydrant", [body, dome, cap, base, band, bolt] + nozzles, [], T)


@design("dog_bowl", T)
def dog_bowl(rng):
    rim = ellipse(0, 0, 2.4, 0.5, 140)
    side = chain([(-2.4, 0)], [(-1.9, -1.4)], quad((0, -1.75), (0, -1.75), (1.9, -1.4), 20), [(2.4, 0)])
    bone = transform(chain(arc(-0.6, 0.12, 0.16, math.radians(-30), math.radians(220), 10),
                           arc(-0.6, -0.12, 0.16, math.radians(140), math.radians(390), 10),
                           arc(0.6, -0.12, 0.16, math.radians(-220), math.radians(30), 10),
                           arc(0.6, 0.12, 0.16, math.radians(-40), math.radians(210), 10), [(-0.47, 0.04)]), dy=-0.8, s=1.0)
    kibble = [circle(x, y, 0.15, 14) for x, y in [(-1.2, 0.1), (-0.6, 0.2), (0.0, 0.15), (0.6, 0.2), (1.2, 0.1)]]
    return Design("Dog Food Bowl", [rim, side, bone] + kibble, [], T)


@design("frisbee", T)
def frisbee(rng):
    disc = ellipse(0, 0, 2.2, 0.8, 140, rot=0.25)
    rim = ellipse(0, 0, 1.6, 0.55, 110, rot=0.25)
    stars_ = [star(0, 0, 0.35, rot=0.25)]
    trail = [quad((-2.6 - 0.2 * k, 0.4 + 0.5 * k), (-3.2 - 0.2 * k, 0.0 + 0.5 * k), (-3.8 - 0.2 * k, 0.2 + 0.5 * k)) for k in range(3)]
    return Design("Flying Disc", [disc, rim] + stars_ + trail, [], T)
