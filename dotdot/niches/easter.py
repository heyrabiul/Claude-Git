"""Easter niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "easter"


def _egg(cx, cy, s, rot=0.0):
    e = chain(cubic((0, 1.4), (1.0, 1.4), (1.15, -1.0), (0, -1.0), 30), cubic((0, -1.0), (-1.15, -1.0), (-1.0, 1.4), (0, 1.4), 30))
    return transform(e, dx=cx, dy=cy, s=s, rot=rot)


@design("decorated_egg", T)
def decorated_egg(rng):
    egg = _egg(0, 0, 2.0)
    bands = [transform(zigzag(-1.9, 1.9, 0, 0.18, 8), dy=0.2), wave(-1.95, 1.95, -0.7, 0.12, 4, 80), wave(-1.6, 1.6, 1.3, 0.12, 3, 60)]
    dots = [circle(x, -1.3, 0.13, 12) for x in (-0.9, -0.3, 0.3, 0.9)] + [star(x, 0.75, 0.2) for x in (-1.0, 0.0, 1.0)]
    grass = [zigzag(-2.6, 2.6, -2.2, 0.2, 12)]
    return Design("Painted Easter Egg", [egg] + bands + dots + grass, [], T)


@design("easter_bunny", T)
def easter_bunny(rng):
    body = ellipse(0, -1.1, 1.3, 1.4, 100)
    head = circle(0, 0.9, 0.9, 80)
    ears = [lens((-0.4, 1.6), (-0.8, 3.6), 0.25), lens((0.4, 1.6), (0.8, 3.6), 0.25)]
    inner = [lens((-0.45, 1.9), (-0.75, 3.3), 0.15), lens((0.45, 1.9), (0.75, 3.3), 0.15)]
    nose = poly((-0.15, 0.75), (0.15, 0.75), (0, 0.55))
    whisk = [[(0.3, 0.6), (1.2, 0.75)], [(0.3, 0.5), (1.2, 0.35)], [(-0.3, 0.6), (-1.2, 0.75)], [(-0.3, 0.5), (-1.2, 0.35)]]
    feet = [ellipse(-0.7, -2.5, 0.55, 0.25, 30), ellipse(0.7, -2.5, 0.55, 0.25, 30)]
    egg = _egg(1.9, -1.8, 0.5, 0.3)
    belly = ellipse(0, -1.2, 0.7, 0.85, 50)
    return Design("Easter Bunny", [body, head, nose, egg, belly] + ears + inner + whisk + feet, [eye(-0.35, 1.05, 0.11), eye(0.35, 1.05, 0.11)], T)


@design("hatching_chick", T)
def hatching_chick(rng):
    shell_low = chain(quad((-1.6, 0.0), (-1.7, -2.2), (0, -2.3)), quad((0, -2.3), (1.7, -2.2), (1.6, 0.0)))
    crack = poly((-1.6, 0.0), (-1.1, 0.4), (-0.6, -0.1), (0, 0.4), (0.6, -0.1), (1.1, 0.4), (1.6, 0.0), closed=False)
    chick = chain(arc(0, 0.9, 1.1, math.radians(-25), math.radians(205), 60))
    beak = poly((-0.2, 0.8), (0.2, 0.8), (0, 0.45))
    tuft = [quad((0, 2.0), (-0.2, 2.5), (0.1, 2.6)), quad((0.1, 2.0), (0.3, 2.4), (0.5, 2.4))]
    wings = [quad((-1.0, 0.5), (-1.7, 0.9), (-1.6, 1.4)), quad((1.0, 0.5), (1.7, 0.9), (1.6, 1.4))]
    shell_top = transform(chain(arc(0, 0, 0.9, 0, math.pi, 20), zigzag(-0.9, 0.9, 0, 0.12, 4)[::-1]), dx=1.7, dy=2.4, rot=0.4)
    return Design("Hatching Chick", [shell_low, crack, chick, beak, shell_top] + tuft + wings, [eye(-0.35, 1.1, 0.1), eye(0.35, 1.1, 0.1)], T)


@design("easter_basket", T)
def easter_basket(rng):
    basket = chain([(-2.4, 0.0)], quad((-2.2, -2.4), (0, -2.6), (2.2, -2.4), 40), [(2.4, 0.0), (-2.4, 0.0)])
    handle = arc(0, 0.0, 2.2, 0, math.pi, 50)
    weave = [quad((-2.3, -0.7 - 0.6 * k), (0, -0.9 - 0.6 * k), (2.3, -0.7 - 0.6 * k)) for k in range(3)]
    eggs = [_egg(x, 0.45, 0.45, r) for x, r in [(-1.5, 0.4), (-0.6, 0.1), (0.4, -0.1), (1.4, -0.4)]]
    bow = [lens((-2.2, 1.2), (-2.9, 1.7), 0.4), lens((-2.2, 1.2), (-2.9, 0.7), 0.4)]
    return Design("Easter Basket", [basket, handle] + weave + eggs + bow, [], T)


@design("carrots", T)
def carrots(rng):
    out = []
    for cx, r in [(-1.0, 0.3), (0.0, 0.0), (1.0, -0.3)]:
        c = chain(quad((-0.45, 1.2), (0.0, -1.0), (0, -2.6)), quad((0, -2.6), (0.0, -1.0), (0.45, 1.2)), [(-0.45, 1.2)])
        out.append(transform(c, dx=cx, rot=r))
        out += [transform(l, dx=cx, rot=r) for l in (lens((0, 1.2), (-0.5, 2.5), 0.2), lens((0, 1.2), (0.0, 2.7), 0.2), lens((0, 1.2), (0.5, 2.5), 0.2))]
        out += [transform([(-0.25, y), (0.0, y - 0.05)], dx=cx, rot=r) for y in (0.4, -0.4, -1.2)]
    ribbon = [quad((-1.0, -0.2), (0, -0.5), (1.0, -0.2)), quad((-1.0, -0.6), (0, -0.9), (1.0, -0.6))]
    return Design("Carrot Bunch", out + ribbon, [], T)


@design("spring_lamb", T)
def spring_lamb(rng):
    fleece = [(1.1 * x, y) for x, y in polar(lambda t: 1.5 + 0.15 * math.sin(16 * t), n=400)]
    head = ellipse(-1.8, 0.5, 0.55, 0.7, 50)
    ears = [lens((-2.2, 0.9), (-2.8, 0.7), 0.3), lens((-1.4, 0.9), (-0.9, 0.7), 0.3)]
    legs = [leg(x, x + 0.3, -1.2, -2.4) for x in (-0.9, -0.3, 0.4, 1.0)]
    bow = [lens((-1.6, -0.15), (-1.1, 0.1), 0.4), lens((-1.6, -0.15), (-1.1, -0.45), 0.4), circle(-1.6, -0.15, 0.08, 10)]
    flowers = [circle(2.2, -2.2, 0.2, 16), circle(-2.6, -2.2, 0.2, 16)]
    return Design("Spring Lamb", [fleece, head] + ears + legs + bow + flowers, [eye(-1.95, 0.6, 0.08)], T)


@design("egg_trio", T)
def egg_trio(rng):
    eggs = [_egg(-1.6, -0.2, 1.1, 0.25), _egg(0, 0.3, 1.35, 0), _egg(1.6, -0.2, 1.1, -0.25)]
    patterns = [transform(zigzag(-0.9, 0.9, 0, 0.12, 5), dx=-1.6, dy=-0.2, rot=0.25),
                wave(-1.15, 1.15, 0.3, 0.12, 3, 60), transform(wave(-0.9, 0.9, 0, 0.1, 3, 60), dx=1.6, dy=-0.2, rot=-0.25),
                circle(0, 1.2, 0.2, 16), circle(0, -0.6, 0.2, 16)]
    cup = chain(quad((-2.8, -1.5), (0, -3.6), (2.8, -1.5)), [(-2.8, -1.5)])
    return Design("Three Easter Eggs", eggs + patterns + [cup], [], T)


@design("easter_bonnet", T)
def easter_bonnet(rng):
    brim = ellipse(0, -0.4, 3.0, 0.7, 160)
    crown = chain(quad((-1.5, -0.2), (-1.6, 1.6), (0, 1.7)), quad((0, 1.7), (1.6, 1.6), (1.5, -0.2)))
    band = quad((-1.5, 0.2), (0, -0.1), (1.5, 0.2))
    flowers = []
    for cx, cy in [(-0.8, 0.6), (0.2, 0.75), (1.0, 0.5)]:
        flowers.append(circle(cx, cy, 0.15, 12))
        flowers += [lens((cx, cy), (cx + 0.45 * math.cos(a), cy + 0.45 * math.sin(a)), 0.35) for a in [k * 2 * math.pi / 5 for k in range(5)]]
    ribbon = [quad((1.5, -0.6), (2.0, -1.6), (1.6, -2.4)), quad((1.6, -0.6), (2.4, -1.4), (2.4, -2.2))]
    return Design("Easter Bonnet", [brim, crown, band] + flowers + ribbon, [], T)
