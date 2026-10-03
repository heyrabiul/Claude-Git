"""Fourth of July niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "patriotic"


@design("usa_flag", T)
def usa_flag(rng):
    flag = [(-2.4 + 4.8 * i / 60, 1.6 + 0.2 * math.sin(i / 60 * 2 * math.pi)) for i in range(61)]
    bottom = [(x, y - 3.0) for x, y in flag]
    outline = chain(flag, bottom[::-1], [flag[0]])
    stripes = [[(x, y - 3.0 * k / 7) for x, y in flag[24:]] for k in range(1, 7)]
    canton = [(flag[24][0], flag[24][1] - 1.3), (-2.4, flag[0][1] - 1.3)]
    stars_ = [star(-2.0 + 0.6 * i, 1.3 - 0.45 * j, 0.14) for i in range(3) for j in range(2)]
    pole = [(-2.45, 1.9), (-2.45, -2.8)]
    return Design("Stars and Stripes", [outline, canton, pole] + stripes + stars_, [], T)


@design("liberty_torch", T)
def liberty_torch(rng):
    flame = chain(quad((0, 1.2), (-1.0, 2.0), (-0.2, 3.4)), quad((-0.2, 3.4), (0.2, 2.6), (0.4, 3.0)), quad((0.4, 3.0), (1.0, 2.0), (0, 1.2)))
    cup = poly((-1.0, 1.2), (1.0, 1.2), (0.6, 0.3), (-0.6, 0.3))
    rim = rect(-1.15, 1.1, 1.15, 1.35)
    handle = poly((-0.4, 0.3), (-0.3, -2.6), (0.3, -2.6), (0.4, 0.3))
    bands = [[(-0.35, -0.6), (0.35, -0.6)], [(-0.32, -1.4), (0.32, -1.4)]]
    rays = [[(1.5 * math.cos(a), 2.2 + 1.5 * math.sin(a)), (2.2 * math.cos(a), 2.2 + 2.2 * math.sin(a))] for a in [math.radians(d) for d in (20, 50, 130, 160)]]
    return Design("Liberty Torch", [flame, cup, rim, handle] + bands + rays, [], T)


@design("fireworks", T)
def fireworks(rng):
    out = []
    for cx, cy, r, n in [(-1.2, 1.0, 1.4, 12), (1.5, 1.6, 1.1, 10), (0.8, -1.2, 0.9, 8)]:
        for k in range(n):
            a = 2 * math.pi * k / n
            out.append([(cx + 0.3 * r * math.cos(a), cy + 0.3 * r * math.sin(a)), (cx + r * math.cos(a), cy + r * math.sin(a))])
        out.append(circle(cx, cy, 0.15 * r, 12))
    trails = [quad((0.8, -2.2), (0.6, -2.8), (0.9, -3.3))]
    skyline = [poly((-3.0, -3.3), (-3.0, -2.4), (-2.2, -2.4), (-2.2, -2.9), (-1.4, -2.9), (-1.4, -2.1), (-0.6, -2.1), (-0.6, -3.3), closed=False)]
    return Design("Fireworks", out + trails + skyline, [], T)


@design("uncle_sam_hat", T)
def uncle_sam_hat(rng):
    crown = poly((-1.2, 0.0), (-1.4, 3.0), (1.4, 3.0), (1.2, 0.0), closed=False)
    top = ellipse(0, 3.0, 1.4, 0.3, 60)
    brim = ellipse(0, 0, 2.6, 0.5, 140)
    band = [quad((-1.25, 0.6), (0, 0.4), (1.25, 0.6)), quad((-1.3, 1.2), (0, 1.0), (1.3, 1.2))]
    stripes = [[(x, 1.25), (x * 1.08, 2.95)] for x in (-0.8, -0.3, 0.2, 0.7)]
    stars_ = [star(x, 0.85, 0.15) for x in (-0.7, 0.0, 0.7)]
    return Design("Uncle Sam Hat", [crown, top, brim] + band + stripes + stars_, [], T)


@design("liberty_bell", T)
def liberty_bell(rng):
    right = chain(cubic((0, 2.0), (1.2, 2.0), (1.2, 0.4), (1.5, -0.8), 30), quad((1.5, -0.8), (1.7, -1.4), (2.1, -1.5), 10))
    bell = chain(mirror_x(right)[::-1], right, [(-2.1, -1.5)])
    crack = poly((0.2, -1.5), (0.0, -0.8), (0.3, -0.3), (0.1, 0.4), closed=False)
    yoke = rrect(-1.6, 2.0, 1.6, 2.5, 0.2)
    bands = [quad((-1.35, -0.6), (0, -0.85), (1.35, -0.6)), quad((-1.0, 1.4), (0, 1.25), (1.0, 1.4))]
    clapper = circle(0, -1.8, 0.3, 24)
    return Design("Liberty Bell", [bell, crack, yoke, clapper] + bands, [], T)


@design("bald_eagle", T)
def bald_eagle(rng):
    head = chain(cubic((-0.6, 1.2), (-0.8, 2.6), (0.6, 2.8), (1.0, 2.2), 30), [(1.8, 2.0), (1.0, 1.6)], quad((1.0, 1.6), (0.6, 1.0), (0.4, 0.8), 10))
    body = chain(cubic((-0.6, 1.2), (-1.4, 0.0), (-0.6, -2.0), (0, -2.4), 30), quad((0, -2.4), (0.8, -1.0), (0.4, 0.8), 20))
    wing_l = chain(quad((-0.6, 1.0), (-2.4, 2.2), (-3.4, 1.4), 20), zigzag(-3.4, -0.8, 0.4, 0.25, 6), [(-0.6, 0.2)])
    feathers = [[(-0.2 + 0.25 * k, -2.4), (-0.3 + 0.3 * k, -3.2)] for k in range(3)]
    shield = [poly((0.4, -0.6), (1.6, -0.6), (1.6, -1.4), (1.0, -2.0), (0.4, -1.4))] + [[(x, -0.6), (x, -1.6)] for x in (0.7, 1.0, 1.3)]
    return Design("Bald Eagle", [head, body, wing_l] + feathers + shield, [eye(0.6, 2.2, 0.09)], T)


@design("star_badge", T)
def star_badge(rng):
    outer = star(0, 0.2, 2.6)
    inner = star(0, 0.2, 1.8)
    centre = circle(0, 0.2, 0.7, 60)
    ribbons = [poly((-0.8, -1.4), (-1.4, -3.2), (-0.9, -2.9), (-0.5, -3.3), (-0.2, -1.6)), poly((0.8, -1.4), (1.4, -3.2), (0.9, -2.9), (0.5, -3.3), (0.2, -1.6))]
    return Design("Star Badge", [outer, inner, centre] + ribbons, [], T)


@design("bunting", T)
def bunting(rng):
    out = []
    for row, y0 in enumerate((2.2, -0.6)):
        line = [(-3.2 + 6.4 * i / 60, y0 - 0.5 * math.sin(i / 60 * math.pi)) for i in range(61)]
        out.append(line)
        for k in range(5):
            i = 4 + 11 * k
            x, y = line[i]
            x2, y2 = line[i + 8]
            out.append(poly((x, y), ((x + x2) / 2, (y + y2) / 2 - 1.0), (x2, y2)))
            if (k + row) % 2 == 0:
                out.append(star((x + x2) / 2, (y + y2) / 2 - 0.45, 0.2))
    return Design("Party Bunting", out, [], T)


@design("picnic_hotdog", T)
def picnic_hotdog(rng):
    bun = chain(cubic((-2.6, 0.2), (-2.6, -1.2), (2.6, -1.2), (2.6, 0.2), 40), quad((2.6, 0.2), (0, -0.2), (-2.6, 0.2), 30))
    sausage = rrect(-3.0, -0.1, 3.0, 0.6, 0.35)
    mustard = wave(-2.4, 2.4, 0.25, 0.12, 6, 90)
    flagpick = [[(0.0, 0.6), (0.0, 2.4)], poly((0.0, 2.4), (1.0, 2.1), (0.0, 1.8))]
    return Design("Picnic Hot Dog", [bun, sausage, mustard] + flagpick, [], T)
