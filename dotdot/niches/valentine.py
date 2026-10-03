"""Valentine's Day niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "valentine"


@design("heart_balloons", T)
def heart_balloons(rng):
    out = []
    for cx, cy, s in [(-1.0, 1.2, 0.95), (0.9, 1.6, 1.1), (0.0, -0.2, 0.8)]:
        out.append(heart(cx, cy, s))
        out.append(arc(cx - 0.35 * s, cy + 0.2 * s, 0.3 * s, math.radians(100), math.radians(170), 8))
        out.append(quad((cx, cy - 0.95 * s), (cx + 0.3, cy - 2.0), (0.0, -3.0)))
    bow = [lens((0, -3.0), (-0.6, -2.6), 0.4), lens((0, -3.0), (0.6, -2.6), 0.4)]
    return Design("Heart Balloons", out + bow, [], T)


@design("love_letter", T)
def love_letter(rng):
    env = rect(-2.4, -1.6, 2.4, 1.4)
    flap = [(-2.4, 1.4), (0, -0.2), (2.4, 1.4)]
    folds = [[(-2.4, -1.6), (-0.6, 0.2)], [(2.4, -1.6), (0.6, 0.2)]]
    seal = heart(0, -0.25, 0.45)
    hearts = [heart(x, y, s) for x, y, s in [(-2.2, 2.4, 0.35), (1.8, 2.6, 0.45), (2.9, 1.9, 0.25)]]
    return Design("Love Letter", [env, flap, seal] + folds + hearts, [], T)


@design("cupid_arrow", T)
def cupid_arrow(rng):
    big = heart(0, 0.3, 1.9)
    shaft = [(-3.2, -1.6), (3.0, 1.9)]
    head = poly((3.0, 1.9), (2.4, 1.85), (2.85, 1.35))
    fletch = [[(-3.2, -1.6), (-3.3, -0.9)], [(-3.2, -1.6), (-2.5, -1.65)], [(-2.8, -1.38), (-2.9, -0.7)], [(-2.8, -1.38), (-2.1, -1.4)]]
    small = heart(0, 0.4, 0.7)
    return Design("Cupid's Arrow", [big, shaft, head, small] + fletch, [], T)


@design("teddy_bear", T)
def teddy_bear(rng):
    head = circle(0, 1.5, 1.0, 90)
    ears = [circle(-0.85, 2.3, 0.4, 30), circle(0.85, 2.3, 0.4, 30)]
    muzzle = ellipse(0, 1.2, 0.45, 0.35, 30)
    nose = ellipse(0, 1.35, 0.15, 0.1, 12)
    body = ellipse(0, -0.8, 1.2, 1.4, 100)
    arms = [ellipse(-1.3, -0.4, 0.35, 0.7, 30, rot=-0.5), ellipse(1.3, -0.4, 0.35, 0.7, 30, rot=0.5)]
    feet = [circle(-0.8, -2.1, 0.5, 40), circle(0.8, -2.1, 0.5, 40)]
    love = heart(0, -0.7, 0.55)
    return Design("Teddy Bear", [head, muzzle, nose, body, love] + ears + arms + feet, [eye(-0.35, 1.7, 0.1), eye(0.35, 1.7, 0.1)], T)


@design("chocolate_box", T)
def chocolate_box(rng):
    box = heart(0, 0.2, 2.6)
    inner = heart(0, 0.25, 2.2)
    chocs = [circle(x, y, 0.35, 30) for x, y in [(-1.0, 1.1), (0.0, 0.5), (1.0, 1.1), (-0.5, -0.4), (0.5, -0.4), (0.0, -1.2)]]
    swirls = [arc(x, y, 0.18, 0, math.pi * 1.5, 10) for x, y in [(-1.0, 1.1), (1.0, 1.1), (0.0, -1.2)]]
    return Design("Box of Chocolates", [box, inner] + chocs + swirls, [], T)


@design("diamond_ring", T)
def diamond_ring(rng):
    band = circle(0, -0.6, 1.6, 120)
    band_in = circle(0, -0.6, 1.25, 100)
    gem = poly((-0.8, 1.6), (-0.5, 2.1), (0.5, 2.1), (0.8, 1.6), (0, 0.9))
    facets = [[(-0.8, 1.6), (0.8, 1.6)], [(-0.5, 2.1), (-0.2, 1.6), (0, 0.9)], [(0.5, 2.1), (0.2, 1.6), (0, 0.9)]]
    setting = [[(-0.35, 1.05), (-0.25, 1.35)], [(0.35, 1.05), (0.25, 1.35)]]
    sparkles = [star(x, y, 0.3, 4, 0.3) for x, y in [(-1.8, 2.2), (1.9, 2.0), (2.2, 0.4)]]
    return Design("Diamond Ring", [band, band_in, gem] + facets + setting + sparkles, [], T)


@design("lovebirds", T)
def lovebirds(rng):
    def bird(s):
        body = chain(cubic((0, 0), (0.2, 1.4), (1.6, 1.6), (1.8, 0.6), 30), quad((1.8, 0.6), (1.0, -0.8), (0, 0), 20))
        head = circle(1.4, 1.4, 0.5, 30)
        beak = poly((1.85, 1.5), (2.2, 1.35), (1.85, 1.2), closed=False)
        wing = quad((0.4, 0.4), (1.0, 0.9), (1.4, 0.2))
        tail = poly((0, 0.2), (-0.7, 0.6), (-0.6, -0.1), closed=False)
        return [mirror_x(p) if s < 0 else p for p in [body, head, beak, wing, tail]]
    left = [transform(p, dx=-2.3) for p in bird(1)]
    right = [transform(p, dx=2.3) for p in bird(-1)]
    branch = [(-3.0, -0.6), (3.0, -0.6)]
    love = heart(0, 2.2, 0.6)
    return Design("Lovebirds", left + right + [branch, love], [eye(-0.9, 1.5, 0.07), eye(0.9, 1.5, 0.07)], T)


@design("heart_lock", T)
def heart_lock(rng):
    lock = heart(0, -0.4, 2.0)
    shackle = chain([(-1.0, 0.9), (-1.0, 1.8)], arc(0, 1.8, 1.0, math.pi, 0, 30), [(1.0, 0.9)])
    keyhole = [circle(0, -0.2, 0.3, 24), poly((-0.15, -0.4), (0.15, -0.4), (0.25, -1.2), (-0.25, -1.2))]
    key = [circle(2.4, -1.6, 0.4, 30), [(2.4, -2.0), (2.4, -3.2)], [(2.4, -2.8), (2.75, -2.8)], [(2.4, -3.1), (2.7, -3.1)]]
    return Design("Heart Lock", [lock, shackle] + keyhole + key, [], T)


@design("rose_bouquet", T)
def rose_bouquet(rng):
    roses = [spiral(x, y, 0.05, 0.55, 2.2, 80) for x, y in [(-0.8, 1.4), (0.5, 1.7), (0.0, 0.7), (1.1, 0.7), (-1.2, 0.4)]]
    stems = [[(x, y - 0.55), (0, -2.0)] for x, y in [(-0.8, 1.4), (0.5, 1.7), (0.0, 0.7), (1.1, 0.7), (-1.2, 0.4)]]
    wrap = poly((-1.9, 0.6), (1.9, 0.6), (0.4, -3.0), (-0.4, -3.0))
    bow = [lens((0, -1.8), (-0.9, -1.4), 0.4), lens((0, -1.8), (0.9, -1.4), 0.4)]
    leaves = [lens((-1.4, 0.0), (-2.2, 0.8), 0.3), lens((1.4, 0.2), (2.2, 1.0), 0.3)]
    return Design("Rose Bouquet", roses + stems + [wrap] + bow + leaves, [], T)
