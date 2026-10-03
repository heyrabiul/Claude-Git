"""Faith & Bible niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "faith"


def _cross(cx, cy, s):
    return transform(poly((-0.3, -2.0), (0.3, -2.0), (0.3, 0.6), (1.2, 0.6), (1.2, 1.2), (0.3, 1.2), (0.3, 2.0), (-0.3, 2.0),
                          (-0.3, 1.2), (-1.2, 1.2), (-1.2, 0.6), (-0.3, 0.6)), dx=cx, dy=cy, s=s)


@design("cross_sunrise", T)
def cross_sunrise(rng):
    cross = _cross(0, 0.4, 1.0)
    rays = [[(0.0 + 1.6 * math.cos(a), 1.3 + 1.6 * math.sin(a)), (0.0 + 2.8 * math.cos(a), 1.3 + 2.8 * math.sin(a))]
            for a in [math.radians(d) for d in (10, 35, 60, 120, 145, 170)]]
    hills = [quad((-3.2, -1.6), (-1.6, -0.8), (0, -1.6)), quad((0, -1.6), (1.6, -0.8), (3.2, -1.6))]
    return Design("Cross at Sunrise", [cross] + rays + hills, [], T)


@design("noahs_ark", T)
def noahs_ark(rng):
    hull = poly((-3.0, 0.0), (3.0, 0.0), (2.2, -1.4), (-2.2, -1.4))
    house = rect(-1.6, 0.0, 1.6, 1.4)
    roof = poly((-2.0, 1.3), (0, 2.4), (2.0, 1.3), closed=False)
    windows = [rect(x - 0.3, 0.4, x + 0.3, 1.0) for x in (-0.9, 0.0, 0.9)]
    giraffe = [[(1.2, 1.4), (1.6, 3.0)], circle(1.75, 3.15, 0.25, 16)]
    rainbow = [arc(0, -0.5, r, math.radians(20), math.radians(160), 40) for r in (3.4, 3.8)]
    water = [wave(-3.6, 3.6, -1.6, 0.12, 6, 100)]
    return Design("Noah's Ark", [hull, house, roof] + windows + giraffe + rainbow + water, [], T)


@design("dove_olive", T)
def dove_olive(rng):
    body = chain(cubic((-2.0, -0.2), (-1.0, 0.8), (0.8, 0.8), (1.6, 0.4), 30), quad((1.6, 0.4), (2.2, 0.6), (2.4, 0.2), 10),
                 quad((2.4, 0.2), (1.2, -0.8), (-0.6, -0.6), 20), [(-2.0, -0.2)])
    wing = chain(cubic((-0.6, 0.6), (-1.2, 2.6), (0.6, 3.2), (1.2, 2.8), 30), quad((1.2, 2.8), (0.6, 1.6), (0.6, 0.7), 20))
    feathers = [quad((-0.4 + 0.3 * k, 1.0 + 0.4 * k), (0.1 + 0.25 * k, 1.4 + 0.4 * k), (0.5 + 0.2 * k, 1.2 + 0.4 * k)) for k in range(3)]
    tail = poly((-2.0, -0.2), (-3.0, 0.4), (-2.8, -0.4), (-3.0, -1.0), (-1.8, -0.5), closed=False)
    branch = [(2.4, 0.2), (3.4, -0.8)]
    leaves = [lens((2.7, -0.1), (3.2, 0.4), 0.35), lens((3.0, -0.4), (3.4, -0.1), 0.35), lens((2.9, -0.3), (2.6, -0.9), 0.35)]
    return Design("Dove of Peace", [body, wing, tail, branch] + feathers + leaves, [eye(1.6, 0.5, 0.07)], T)


@design("open_bible", T)
def open_bible(rng):
    left = chain(quad((0, -1.6), (-1.4, -1.2), (-3.0, -1.6)), [(-3.0, 1.6)], quad((-3.0, 1.6), (-1.4, 2.0), (0, 1.6)))
    right = mirror_x(left)
    spine = [(0, -1.6), (0, 1.6)]
    lines_ = [quad((-2.6, y), (-1.4, y + 0.2), (-0.4, y)) for y in (1.0, 0.5, 0.0, -0.5)] + \
             [quad((0.4, y), (1.4, y + 0.2), (2.6, y)) for y in (1.0, 0.5)]
    cross = _cross(1.5, -0.6, 0.25)
    ribbon = [(0.2, -1.6), (0.4, -2.8), (0.6, -2.5), (0.8, -2.9), (0.6, -1.6)]
    return Design("Open Bible", [left, right, spine, cross, ribbon] + lines_, [], T)


@design("chapel", T)
def chapel(rng):
    body = rect(-1.8, -2.2, 1.8, 0.4)
    roof = poly((-2.2, 0.2), (0, 1.8), (2.2, 0.2), closed=False)
    tower = rect(-0.5, 1.0, 0.5, 2.6)
    spire = poly((-0.6, 2.6), (0, 3.8), (0.6, 2.6), closed=False)
    cross = [[(0, 3.8), (0, 4.4)], [(-0.2, 4.15), (0.2, 4.15)]]
    door = chain([(-0.5, -2.2), (-0.5, -1.2)], arc(0, -1.2, 0.5, math.pi, 0, 16), [(0.5, -2.2)])
    windows = [chain([(x - 0.3, -0.8), (x - 0.3, -0.2)], arc(x, -0.2, 0.3, math.pi, 0, 10), [(x + 0.3, -0.8), (x - 0.3, -0.8)]) for x in (-1.1, 1.1)]
    bell = circle(0, 1.8, 0.25, 16)
    return Design("Little Chapel", [body, roof, tower, spire, door, bell] + cross + windows, [], T)


@design("ichthys", T)
def ichthys(rng):
    fish = [arc(0, -1.6, 2.6, math.radians(45), math.radians(160), 50), arc(0, 1.6, 2.6, math.radians(200), math.radians(315), 50)]
    waves_ = [wave(-3.2, 3.2, -2.4 - 0.4 * k, 0.12, 5, 80) for k in range(2)]
    eye_ = circle(-1.3, 0.2, 0.12, 12)
    return Design("Fish Symbol", fish + waves_ + [eye_], [], T)


@design("angel", T)
def angel(rng):
    halo = ellipse(0, 3.0, 0.7, 0.2, 40)
    head = circle(0, 2.2, 0.55, 40)
    gown = poly((-0.5, 1.7), (-1.6, -2.4), (1.6, -2.4), (0.5, 1.7), closed=False)
    wings = [chain(cubic((-0.5, 1.2), (-2.6, 2.4), (-3.2, 0.0), (-1.2, -0.4), 40)), chain(cubic((0.5, 1.2), (2.6, 2.4), (3.2, 0.0), (1.2, -0.4), 40))]
    feathers = [quad((-1.4 - 0.4 * k, 0.8 + 0.3 * k), (-1.0 - 0.4 * k, 0.6 + 0.3 * k), (-0.8, 0.4 + 0.3 * k)) for k in range(3)] + \
               [quad((1.4 + 0.4 * k, 0.8 + 0.3 * k), (1.0 + 0.4 * k, 0.6 + 0.3 * k), (0.8, 0.4 + 0.3 * k)) for k in range(3)]
    hands = [quad((-0.4, 0.6), (0, 0.2), (0.4, 0.6))]
    return Design("Guardian Angel", [halo, head, gown] + wings + feathers + hands, [], T)


@design("heart_cross", T)
def heart_cross(rng):
    big = heart(0, 0.2, 2.4)
    inner = heart(0, 0.2, 2.0)
    cross = _cross(0, 0.4, 0.55)
    rays = [[(2.8 * math.cos(a), 0.2 + 2.8 * math.sin(a)), (3.3 * math.cos(a), 0.2 + 3.3 * math.sin(a))] for a in [math.radians(d) for d in (30, 60, 120, 150)]]
    return Design("Heart and Cross", [big, inner, cross] + rays, [], T)


@design("praying_hands", T)
def praying_hands(rng):
    right = chain(cubic((0, 2.6), (0.6, 2.4), (1.2, 0.8), (1.0, -0.8), 40), quad((1.0, -0.8), (0.8, -1.8), (0.9, -2.6), 20))
    hands = [right, mirror_x(right), [(0, 2.6), (0, -1.0)]]
    fingers = [quad((0.1, 2.0 - 0.5 * k), (0.5, 2.1 - 0.5 * k), (0.9, 1.6 - 0.5 * k)) for k in range(3)]
    thumb = [quad((0.1, 0.4), (0.4, 0.0), (0.2, -0.6))]
    cuffs = [[(-0.9, -2.0), (0.9, -2.0)]]
    beads = [circle(-1.4 + 0.3 * k, -1.2 - 0.25 * math.sin(k / 9 * math.pi), 0.1, 10) for k in range(10)]
    return Design("Praying Hands", hands + fingers + thumb + cuffs + beads, [], T)
