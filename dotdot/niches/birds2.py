"""Birds niche, part 2 (pictures 11-50)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "birds"


def perched(cx=0.0, cy=0.0, s=1.0, beak=0.5, crest=0, tail=1.0, belly=False, legs=True, fat=1.0):
    """Side-view perching bird facing left.  Returns (strokes, hints)."""
    body = chain(cubic((-0.6, 0.6), (-1.0 * fat, -0.6), (0.2, -1.2 * fat), (1.0, -0.6), 30), [(1.0 + 1.4 * tail, -1.2 - 0.6 * tail)],
                 [(1.2 + 1.2 * tail, -0.8 - 0.5 * tail)], quad((1.0, -0.2), (0.6, 0.6), (0.2, 0.9), 16))
    head = circle(-0.45, 0.9, 0.55, 40)
    bk = poly((-0.95, 1.05), (-0.95 - beak, 0.9), (-0.97, 0.75), closed=False)
    wing = quad((-0.3, 0.2), (0.6, 0.0), (1.2, -0.7))
    out = [body, head, bk, wing]
    if crest:
        out.append(poly((-0.3, 1.4), (0.1, 1.9 + 0.3 * crest), (0.1, 1.25), closed=False))
    if belly:
        out.append(quad((-0.95, 0.4), (-0.8, -0.6), (0.2, -1.0)))
    if legs:
        out += [[(-0.1, -0.9), (-0.2, -1.4)], [(0.3, -0.95), (0.25, -1.4)]]
    strokes = [transform(p, dx=cx, dy=cy, s=s) for p in out]
    return strokes, [eye(cx - 0.6 * s, cy + 1.0 * s, 0.08 * s)]


def branch(y=-1.4, x0=-3.0, x1=3.0):
    b = [(x0, y), (x1, y + 0.1)]
    leaves = [lens((x1 - 0.6, y + 0.05), (x1 - 0.1, y + 0.6), 0.35), lens((x0 + 0.6, y), (x0 + 0.1, y - 0.6), 0.35)]
    return [b] + leaves


def make(title, parts, hints=(), flip=False, rot=0.0):
    parts, hints = list(parts), list(hints)
    if flip:
        parts, hints = [mirror_x(p) for p in parts], [mirror_x(p) for p in hints]
    if rot:
        parts, hints = [transform(p, rot=rot) for p in parts], [transform(p, rot=rot) for p in hints]
    return Design(title, parts, hints, T)


@design("blue_jay", T)
def blue_jay(rng):
    b, h = perched(0, 0.2, 1.2, crest=1, tail=1.2)
    bars = [[(0.6 + 0.25 * k, -0.4 - 0.2 * k), (0.8 + 0.25 * k, -0.2 - 0.2 * k)] for k in range(3)]
    return make("Blue Jay", b + bars + branch(-1.5), h)


@design("cardinal", T)
def cardinal(rng):
    b, h = perched(0, 0.3, 1.2, beak=0.35, crest=1.5, tail=1.0)
    mask = [arc(-0.85, 1.35, 0.35, math.radians(180), math.radians(300), 8)]
    snow = [wave(-3.0, 3.0, -1.2, 0.08, 6, 60)] + [star(x, y, 0.2, 6, 0.5) for x, y in [(-2.4, 2.6), (2.4, 2.4)]]
    return make("Cardinal in Snow", b + mask + branch(-1.4) + snow, h, flip=True)


@design("sparrow", T)
def sparrow(rng):
    b, h = perched(0, 0.0, 1.1, beak=0.3, fat=1.2)
    seeds = [ellipse(x, -2.0, 0.12, 0.07, 8) for x in (-1.6, -1.2, 1.4, 1.9)]
    fence = [[(-3.0, -1.6), (3.0, -1.6)], [(-3.0, -2.2), (3.0, -2.2)], [(-2.0, -2.6), (-2.0, -1.2)], [(2.2, -2.6), (2.2, -1.2)]]
    return make("House Sparrow", b + seeds + fence, h)


@design("chickadee", T)
def chickadee(rng):
    b, h = perched(0, 0.2, 1.1, beak=0.25, fat=1.3, belly=True)
    cap = arc(-0.5, 1.2, 0.45, math.radians(20), math.radians(170), 12)
    bib = quad((-0.95, 0.75), (-0.6, 0.3), (-0.2, 0.5))
    berries = [circle(x, -1.9, 0.15, 12) for x in (1.6, 1.9, 2.2)] + [[(1.9, -1.75), (2.2, -1.4)]]
    return make("Upside-Down Chickadee", b + [cap, bib] + berries + branch(-1.4), h, rot=math.pi)


@design("woodpecker", T)
def woodpecker(rng):
    trunk = [[(0.6, -3.0), (0.6, 3.0)], [(2.0, -3.0), (2.0, 3.0)]] + [arc(1.3, y, 0.3, math.radians(200), math.radians(340), 8) for y in (-2.0, 0.8, 2.2)]
    body = chain(cubic((0.5, 1.6), (-0.6, 1.2), (-0.6, -0.6), (0.4, -1.4), 30), [(0.6, -2.6)])
    head = circle(0.0, 1.8, 0.5, 30)
    crest = poly((0.0, 2.3), (0.5, 2.6), (0.4, 2.1), closed=False)
    beak = poly((-0.45, 1.9), (-1.3, 1.85), (-0.45, 1.7), closed=False)
    wing = quad((-0.1, 1.0), (0.1, -0.2), (0.5, -1.0))
    hole = ellipse(1.3, -0.6, 0.25, 0.35, 20)
    chips = [poly((-1.4 + 0.3 * k, 1.2 - 0.3 * k), (-1.2 + 0.3 * k, 1.3 - 0.3 * k), (-1.25 + 0.3 * k, 1.05 - 0.3 * k)) for k in range(3)]
    return make("Woodpecker", trunk + [body, head, crest, beak, wing, hole] + chips, [eye(-0.1, 1.9, 0.08)])


@design("toucan", T)
def toucan(rng):
    b, h = perched(0.4, 0.0, 1.1, beak=0.0, tail=1.1)
    beak = chain(cubic((-0.6, 1.4), (-2.0, 1.6), (-2.8, 0.9), (-2.6, 0.6), 30), quad((-2.6, 0.6), (-1.6, 0.6), (-0.6, 0.6), 16))
    stripe = quad((-0.7, 1.0), (-1.6, 1.15), (-2.5, 0.85))
    bib = quad((-0.55, 0.55), (-0.3, -0.2), (0.3, -0.4))
    return make("Toucan", b + [beak, stripe, bib] + branch(-1.6), h)


@design("pelican", T)
def pelican(rng):
    body = ellipse(0.8, -0.4, 1.6, 1.0, 80)
    neck = tube(quad((-0.2, 0.0), (-0.8, 1.2), (-0.4, 2.0)), 0.5)
    head = circle(-0.4, 2.2, 0.45, 30)
    bill = poly((-0.85, 2.3), (-3.2, 1.8), (-0.8, 2.05), closed=False)
    pouch = quad((-0.8, 2.0), (-2.0, 0.8), (-3.2, 1.8))
    wing = quad((0.0, 0.0), (1.2, 0.4), (2.4, -0.6))
    post = [rect(0.2, -3.0, 1.2, -1.4)]
    water = [wave(-3.4, 3.4, -2.4, 0.1, 6, 80)]
    return make("Pelican on a Post", [body, neck, head, bill, pouch, wing] + post + water, [eye(-0.45, 2.35, 0.07)])


@design("heron", T)
def heron(rng):
    body = chain(cubic((-0.2, 0.6), (-0.6, -0.4), (0.6, -1.0), (1.8, -1.4), 30), quad((1.8, -1.4), (1.0, 0.0), (-0.2, 0.6), 20))
    neck = cubic((-0.1, 0.6), (-0.6, 1.4), (0.4, 1.8), (-0.2, 2.6), 30)
    head = circle(-0.3, 2.7, 0.3, 24)
    bill = poly((-0.55, 2.75), (-1.8, 2.5), (-0.55, 2.6), closed=False)
    plume = quad((-0.1, 2.9), (0.4, 3.2), (0.9, 3.0))
    legs = [[(0.4, -0.9), (0.3, -3.0)], [(0.7, -1.0), (0.9, -3.0)]]
    reeds = [quad((x, -3.0), (x + 0.2, -1.6), (x + 0.1, -0.6)) for x in (-2.6, -2.2, 2.4, 2.8)]
    water = [wave(-3.2, 3.2, -2.6, 0.08, 6, 80)]
    return make("Grey Heron", [body, neck, head, bill, plume] + legs + reeds + water, [eye(-0.35, 2.75, 0.06)])


@design("stork", T)
def stork(rng):
    body = ellipse(0.4, 0.4, 1.8, 0.7, 70)
    neck = tube([(-1.2, 0.7), (-2.0, 1.2)], 0.4)
    head = circle(-2.2, 1.3, 0.35, 24)
    bill = poly((-2.5, 1.4), (-3.6, 1.0), (-2.5, 1.2), closed=False)
    wings = [poly((0.0, 0.9), (0.8, 2.6), (2.0, 2.4), (1.4, 0.8), closed=False)]
    legs = [[(0.6, -0.3), (1.6, -1.2)], [(0.8, -0.3), (2.0, -1.0)]]
    bundle = [chain(quad((-3.4, 0.9), (-3.0, -1.4), (-2.6, -1.4)), quad((-2.6, -1.4), (-2.2, -1.4), (-2.0, 0.6)))]
    baby = [circle(-2.8, -0.2, 0.35, 20)]
    return make("Stork Delivery", [body, neck, head, bill] + wings + legs + bundle + baby, [eye(-2.25, 1.4, 0.06)])


@design("golden_eagle", T)
def golden_eagle(rng):
    right = [(0.3, 0.4), (1.4, 1.2), (2.8, 1.6), (3.6, 1.2), (3.2, 0.9), (3.4, 0.6), (2.9, 0.5), (3.0, 0.2), (2.4, 0.1), (1.2, -0.2), (0.3, -0.3)]
    wings = chain(mirror_x(right)[::-1], right, [(-0.3, 0.4)])
    head = chain(arc(0, 0.75, 0.4, math.radians(-30), math.radians(210), 20))
    beak = poly((-0.15, 0.55), (0, 0.15), (0.15, 0.55), closed=False)
    tail = poly((-0.4, -0.3), (-0.6, -1.4), (0.6, -1.4), (0.4, -0.3), closed=False)
    peaks = [poly((-3.2, -2.6), (-1.8, -1.0), (-0.6, -2.6), (0.8, -1.4), (2.0, -2.6), closed=False)]
    return make("Soaring Eagle", [wings, head, beak, tail] + peaks, [eye(-0.15, 0.85, 0.06), eye(0.15, 0.85, 0.06)])


@design("falcon", T)
def falcon(rng):
    b, h = perched(0, 0.6, 1.3, beak=0.25, tail=0.6, belly=True)
    mustache = [quad((-0.75, 1.6), (-0.9, 1.1), (-0.6, 0.8))]
    glove = [rrect(-1.2, -2.8, 1.6, -1.4, 0.4), [(-1.2, -2.2), (1.6, -2.2)]]
    jesses = [[(0.0, -0.8), (-0.2, -1.4)], [(0.3, -0.8), (0.4, -1.4)]]
    return make("Falcon on a Glove", b + mustache + glove + jesses, h)


@design("barn_owl", T)
def barn_owl(rng):
    face = [(x, -y + 3.2) for x, y in heart(0, 1.0, 1.4)]
    body = chain(cubic((-1.4, 1.0), (-2.0, -1.4), (-0.6, -2.6), (0, -2.6), 30), cubic((0, -2.6), (0.6, -2.6), (2.0, -1.4), (1.4, 1.0), 30))
    eyes_ = [circle(-0.5, 1.8, 0.3, 24), circle(0.5, 1.8, 0.3, 24)]
    beak = poly((-0.12, 1.4), (0.12, 1.4), (0, 0.95))
    dots = [circle(x, y, 0.08, 8) for x, y in [(-0.6, -0.4), (0.2, -0.8), (0.7, -0.2), (-0.3, -1.4), (0.5, -1.6)]]
    branch_ = [(-2.6, -2.6), (2.6, -2.6)]
    return make("Barn Owl", [face, body, beak, branch_] + eyes_ + dots, [eye(-0.5, 1.8, 0.12), eye(0.5, 1.8, 0.12)])


@design("snowy_owl", T)
def snowy_owl(rng):
    body = chain(cubic((-1.2, 1.6), (-2.2, 0.0), (-1.4, -2.4), (0, -2.4), 30), cubic((0, -2.4), (1.4, -2.4), (2.2, 0.0), (1.2, 1.6), 30),
                 quad((1.2, 1.6), (0, 2.2), (-1.2, 1.6), 16))
    eyes_ = [circle(-0.5, 1.0, 0.35, 24), circle(0.5, 1.0, 0.35, 24)]
    beak = poly((-0.12, 0.6), (0.12, 0.6), (0, 0.2))
    chevrons = [poly((x - 0.2, y + 0.1), (x, y - 0.1), (x + 0.2, y + 0.1), closed=False) for x, y in [(-0.8, -0.6), (0.0, -0.9), (0.8, -0.6), (-0.4, -1.5), (0.4, -1.5)]]
    snow = [wave(-3.0, 3.0, -2.5, 0.1, 5, 60)] + [star(x, y, 0.2, 6, 0.5) for x, y in [(-2.6, 2.4), (2.4, 2.6), (2.6, 0.2)]]
    return make("Snowy Owl", [body, beak] + eyes_ + chevrons + snow, [eye(-0.5, 1.0, 0.15), eye(0.5, 1.0, 0.15)])


@design("kingfisher", T)
def kingfisher(rng):
    b, h = perched(0.2, 0.4, 1.1, beak=1.2, tail=0.5, fat=1.2)
    stripe = quad((-0.6, 1.0), (-0.2, 0.9), (0.2, 1.1))
    fish = [chain(quad((-2.0, -1.8), (-1.4, -1.4), (-0.8, -1.8)), [(-0.5, -1.5), (-0.5, -2.1), (-0.8, -1.8)], quad((-0.8, -1.8), (-1.4, -2.2), (-2.0, -1.8)))]
    water = [wave(-3.2, 3.2, -2.4, 0.1, 6, 80)]
    return make("Kingfisher", b + [stripe] + fish + branch(-1.2) + water, h, flip=True)


@design("puffin", T)
def puffin(rng):
    body = chain(cubic((-0.6, 1.4), (-1.4, 0.4), (-1.4, -1.6), (0.0, -1.8), 30), quad((0.0, -1.8), (1.4, -1.2), (0.8, 1.0), 20))
    head = circle(-0.1, 1.6, 0.75, 40)
    beak = chain(quad((-0.8, 1.9), (-1.8, 1.5), (-0.8, 1.2)))
    beak_bands = [[(-1.1, 1.85), (-1.1, 1.3)], [(-1.4, 1.75), (-1.4, 1.4)]]
    belly = quad((-1.0, 0.8), (-0.8, -0.8), (0.2, -1.6))
    feet = [lens((-0.4, -1.8), (-0.9, -2.2), 0.4), lens((0.2, -1.8), (0.0, -2.3), 0.4)]
    rock = [chain(arc(0, -2.6, 2.4, math.radians(20), math.radians(160), 30))]
    fishes = [[(-0.9, 1.3), (-1.3, 0.8)], [(-1.0, 1.25), (-0.8, 0.7)]]
    return make("Puffin", [body, head, beak, belly] + beak_bands + feet + rock + fishes, [eye(-0.3, 1.8, 0.08)])


@design("ostrich", T)
def ostrich(rng):
    body = chain(cubic((-1.2, 0.0), (-1.4, 1.4), (1.2, 1.6), (2.0, 0.4), 30), quad((2.0, 0.4), (1.0, -0.6), (-1.2, 0.0), 20))
    plumes = [quad((1.6, 0.8), (2.4, 1.4), (2.8, 1.0)), quad((1.8, 0.4), (2.6, 0.6), (2.9, 0.2))]
    neck = cubic((-1.0, 0.6), (-1.6, 1.6), (-1.0, 2.4), (-1.4, 3.2), 30)
    neck2 = cubic((-0.7, 0.8), (-1.2, 1.6), (-0.7, 2.4), (-1.1, 3.2), 30)
    head = circle(-1.3, 3.35, 0.3, 20)
    beak = poly((-1.55, 3.35), (-2.0, 3.25), (-1.55, 3.2), closed=False)
    legs = [[(-0.2, -0.3), (-0.4, -1.6), (-0.1, -3.0)], [(0.4, -0.3), (0.6, -1.6), (0.9, -3.0)]]
    return make("Ostrich", [body, neck, neck2, head, beak] + plumes + legs, [eye(-1.35, 3.45, 0.06)])


@design("goose", T)
def goose(rng):
    body = chain(cubic((-0.6, 0.0), (-1.0, -1.4), (1.6, -1.6), (2.6, -0.4), 30), quad((2.6, -0.4), (1.8, 0.4), (0.4, 0.2), 20))
    neck = tube(cubic((-0.4, 0.0), (-0.8, 1.2), (-0.2, 1.6), (-0.6, 2.4), 30), 0.45)
    head = ellipse(-0.75, 2.55, 0.45, 0.32, 24)
    beak = poly((-1.15, 2.6), (-1.7, 2.45), (-1.15, 2.35), closed=False)
    wing = quad((0.2, -0.2), (1.2, 0.2), (2.2, -0.4))
    feet = [lens((0.4, -1.4), (0.0, -2.0), 0.4), lens((1.0, -1.4), (1.2, -2.0), 0.4)]
    bonnet = [arc(-0.7, 2.6, 0.55, math.radians(-20), math.radians(200), 16), quad((-0.2, 2.2), (0.2, 1.8), (0.0, 1.4))]
    return make("Goose in a Bonnet", [body, neck, head, beak, wing] + feet + bonnet, [eye(-0.85, 2.65, 0.06)])


@design("crane", T)
def crane(rng):
    body = chain(cubic((-0.6, 0.4), (-1.0, -0.8), (1.0, -1.0), (2.2, -0.6), 30), quad((2.2, -0.6), (1.0, 0.2), (-0.6, 0.4), 20))
    tail = [poly((1.8, -0.5), (2.8, -1.2), (2.4, -0.4), closed=False)]
    neck = cubic((-0.4, 0.4), (-1.0, 1.4), (-0.2, 2.2), (-0.8, 3.0), 30)
    head = circle(-0.9, 3.1, 0.25, 20)
    crown = arc(-0.9, 3.1, 0.25, math.radians(40), math.radians(140), 8)
    bill = poly((-1.12, 3.15), (-1.8, 2.9), (-1.12, 3.0), closed=False)
    wing_up = poly((0.0, 0.3), (0.6, 2.4), (1.8, 2.6), (1.4, 0.2), closed=False)
    legs = [[(0.4, -0.8), (0.2, -3.0)], [(0.8, -0.85), (1.0, -3.0)]]
    sun = arc(2.2, 2.0, 0.8, 0, 2 * math.pi, 30)
    return make("Dancing Crane", [body, neck, head, crown, bill, wing_up, sun] + tail + legs, [eye(-0.95, 3.15, 0.05)])


@design("pigeon", T)
def pigeon(rng):
    b, h = perched(0, 0.0, 1.2, beak=0.25, fat=1.3, tail=0.8)
    neck_ring = [quad((-0.9, 0.5), (-0.5, 0.2), (-0.1, 0.5))]
    crumbs = [circle(x, -2.2, 0.08, 8) for x in (-2.0, -1.6, -1.1, 1.8, 2.3)]
    ground = [(-3.0, -1.75), (3.0, -1.75)]
    return make("City Pigeon", [transform(p, rot=0.45) for p in b + neck_ring] + crumbs + [ground], [transform(p, rot=0.45) for p in h])


@design("crow", T)
def crow(rng):
    b, h = perched(0, 0.4, 1.2, beak=0.6, tail=1.3)
    shine = [quad((-0.6, 0.6), (0.2, 0.4), (0.8, -0.2))]
    pumpkin = [ellipse(2.2, -2.2, 0.8, 0.55, 40), ellipse(2.2, -2.2, 0.3, 0.55, 24), [(2.2, -1.65), (2.3, -1.3)]]
    return make("Crow on a Branch", b + shine + branch(-1.3) + pumpkin, h)


@design("macaw", T)
def macaw(rng):
    body = chain(cubic((-0.4, 1.4), (-1.4, 0.8), (-1.2, -1.2), (-0.2, -1.6), 30), quad((-0.2, -1.6), (0.8, -0.6), (0.4, 1.2), 20))
    head = circle(-0.1, 1.7, 0.65, 40)
    beak = chain(cubic((-0.65, 2.0), (-1.4, 2.0), (-1.5, 1.2), (-1.0, 1.1), 16), quad((-1.0, 1.1), (-0.9, 1.4), (-0.65, 1.4), 8))
    face = ellipse(-0.25, 1.75, 0.3, 0.22, 20)
    tail = [poly((-0.2, -1.6), (0.2, -3.6), (0.5, -3.6), (0.4, -1.4)), [(0.2, -1.6), (0.35, -3.6)]]
    wing = quad((-0.6, 0.8), (0.2, -0.4), (0.0, -1.4))
    ring = [circle(0.2, -0.4, 1.9, 80)]
    return make("Scarlet Macaw", [body, head, beak, face, wing] + tail + ring, [eye(-0.2, 1.8, 0.08)])


@design("cockatoo", T)
def cockatoo(rng):
    b, h = perched(0, 0.2, 1.2, beak=0.2, tail=0.9)
    crest = [poly((-0.4, 1.5), (-0.9 + 0.3 * k, 2.6 + 0.2 * k), (-0.1, 1.5), closed=False) for k in range(4)]
    beak = chain(quad((-0.95, 1.2), (-1.4, 1.0), (-1.0, 0.7)))
    return make("Cockatoo", b + crest + [beak] + branch(-1.3), h)


@design("budgie_cage", T)
def budgie_cage(rng):
    cage = [chain([(-2.0, -2.6), (-2.0, 1.0)], arc(0, 1.0, 2.0, math.pi, 0, 40), [(2.0, -2.6)]), rect(-2.3, -2.9, 2.3, -2.6)]
    bars = [[(x, -2.6), (x, 1.0 + math.sqrt(max(0, 4 - x * x)) * 0.95)] for x in (-1.2, -0.4, 0.4, 1.2)]
    hook = [[(0, 3.0), (0, 3.4)], arc(0, 3.6, 0.2, -math.pi / 2, math.pi, 10)]
    perch = [(-1.6, -0.8), (1.6, -0.8)]
    bird, hints = perched(0.2, 0.3, 0.55, beak=0.15, tail=0.8)
    door = [rect(0.6, -2.4, 1.6, -1.4)]
    return make("Budgie in a Cage", cage + bars + hook + [perch] + bird + door, hints)


@design("bird_feeder", T)
def bird_feeder(rng):
    roof = poly((-2.0, 1.0), (0, 2.4), (2.0, 1.0))
    tube_ = rect(-0.9, -1.6, 0.9, 1.0)
    tray = rect(-1.6, -2.0, 1.6, -1.6)
    seeds = [ellipse(x, y, 0.12, 0.07, 8) for x in (-0.5, 0.0, 0.5) for y in (-1.1, -0.4, 0.3)]
    hook = [[(0, 2.4), (0, 3.2)]]
    bird, h = perched(-2.2, -0.9, 0.5, beak=0.2)
    bird2, h2 = perched(2.2, -0.9, 0.5, beak=0.2)
    bird2 = [mirror_x(p, 2.2) for p in bird2]
    h2 = [mirror_x(p, 2.2) for p in h2]
    return make("Bird Feeder", [roof, tube_, tray] + seeds + hook + bird + bird2, h + h2)


@design("baby_birds", T)
def baby_birds(rng):
    nest = chain(arc(0, 0.4, 2.6, math.radians(195), math.radians(345), 60), [(-2.5, -0.27)])
    twigs = [quad((-2.4, -0.4 - 0.3 * k), (0, -1.0 - 0.35 * k), (2.4, -0.4 - 0.3 * k)) for k in range(3)]
    chicks = []
    for x in (-1.2, 0.0, 1.2):
        chicks += [circle(x, 0.6, 0.55, 30), poly((x - 0.25, 1.0), (x, 2.0), (x + 0.25, 1.0), closed=False), [(x - 0.25, 1.0), (x + 0.25, 1.0)]]
    mom, h = perched(2.4, 2.4, 0.55, beak=0.3)
    worm = [(1.6, 3.0), (1.4, 2.7), (1.6, 2.5), (1.4, 2.3)]
    return make("Hungry Baby Birds", [nest] + twigs + chicks + mom + [worm],
                h + [eye(x + 0.15, 0.75, 0.07) for x in (-1.2, 0.0, 1.2)])


@design("kiwi_bird", T)
def kiwi_bird(rng):
    body = ellipse(0.4, 0.0, 2.0, 1.5, 100)
    head = circle(-1.4, 0.5, 0.55, 30)
    beak = quad((-1.9, 0.4), (-2.8, -0.4), (-3.2, -1.4))
    legs = [[(0.0, -1.4), (-0.2, -2.2)], [(0.8, -1.4), (0.8, -2.2)]]
    toes = [[(-0.2, -2.2), (-0.6, -2.4)], [(-0.2, -2.2), (0.1, -2.4)], [(0.8, -2.2), (0.4, -2.4)], [(0.8, -2.2), (1.1, -2.4)]]
    fern = [[(2.6, -2.4), (2.4, 1.8)]] + [lens((2.55 - 0.03 * k, -1.8 + 0.6 * k), (3.1, -1.5 + 0.6 * k), 0.3) for k in range(6)]
    return make("Kiwi Bird", [body, head, beak] + legs + toes + fern, [eye(-1.5, 0.65, 0.07)])


@design("roadrunner", T)
def roadrunner(rng):
    body = chain(cubic((-0.8, 0.6), (-0.4, -0.4), (1.0, -0.4), (1.6, 0.0), 20), [(3.4, 0.6), (3.2, 0.2), (1.6, -0.4)], quad((1.6, -0.4), (0.0, -0.8), (-0.8, 0.6), 20))
    head = circle(-1.0, 1.0, 0.45, 30)
    crest = [poly((-0.8, 1.4), (-0.2, 2.0), (-0.6, 1.4), closed=False), poly((-0.9, 1.45), (-0.5, 2.2), (-0.75, 1.45), closed=False)]
    beak = poly((-1.4, 1.05), (-2.4, 0.95), (-1.4, 0.85), closed=False)
    legs = [[(0.2, -0.6), (-0.6, -1.8)], [(0.6, -0.6), (1.2, -1.8)]]
    dust = [circle(1.8, -2.0, 0.3, 16), circle(2.4, -1.8, 0.4, 18), circle(3.0, -2.0, 0.3, 16)]
    cactus = [[(-2.8, -2.4), (-2.8, 0.0)], [(-2.4, -2.4), (-2.4, 0.0)], arc(-2.6, 0.0, 0.2, 0, math.pi, 8)]
    return make("Roadrunner", [body, head, beak] + crest + legs + dust + cactus, [eye(-1.1, 1.1, 0.07)])


@design("quail", T)
def quail(rng):
    b, h = perched(0, 0.0, 1.2, beak=0.2, fat=1.4, tail=0.4, legs=True)
    plume = quad((-0.5, 1.45), (-0.9, 2.2), (-1.3, 2.1))
    scales = [arc(x, y, 0.2, math.radians(200), math.radians(340), 6) for x in (-0.2, 0.3, 0.8) for y in (-0.2, -0.6)]
    babies = [circle(2.0, -1.4, 0.3, 16), circle(2.7, -1.5, 0.3, 16)]
    return make("Quail Family", b + [plume] + scales + babies + [[(-3.0, -1.8), (3.2, -1.8)]], h)


@design("pheasant", T)
def pheasant(rng):
    b, h = perched(0, 0.4, 1.2, beak=0.25, tail=2.2)
    ring = [quad((-0.95, 0.55), (-0.5, 0.25), (0.0, 0.55))]
    wattle = [ellipse(-0.7, 1.0, 0.18, 0.25, 12)]
    grass = [zigzag(-3.2, 3.2, -1.5, 0.25, 14)]
    return make("Pheasant", b + ring + wattle + grass, h, flip=True)


@design("swallow", T)
def swallow(rng):
    body = chain(quad((-1.6, 0.2), (0.0, 0.6), (1.4, 0.0), 20), [(3.0, 0.8), (1.8, -0.1), (3.0, -0.8), (1.4, -0.3)], quad((1.4, -0.3), (0.0, -0.6), (-1.6, 0.2), 20))
    wings = [poly((-0.4, 0.4), (0.6, 2.6), (1.0, 2.4), (0.6, 0.4), closed=False), poly((-0.4, -0.3), (0.2, -2.4), (0.6, -2.2), (0.6, -0.4), closed=False)]
    beak = poly((-1.6, 0.25), (-2.0, 0.15), (-1.6, 0.05), closed=False)
    clouds = [chain(arc(-2.2, -2.2, 0.4, math.pi, 0, 10), arc(-1.6, -2.0, 0.5, math.pi, 0, 10), [(-2.6, -2.2)])]
    return make("Swallow in Flight", [body, beak] + wings + clouds, [eye(-1.2, 0.3, 0.06)])


@design("bird_flock", T)
def bird_flock(rng):
    out = []
    for k, (x, y, s) in enumerate([(0, 2.0, 1.0), (-1.0, 1.4, 0.9), (1.0, 1.4, 0.9), (-2.0, 0.8, 0.8), (2.0, 0.8, 0.8), (-3.0, 0.2, 0.7), (3.0, 0.2, 0.7)]):
        out.append(chain(quad((x - 0.6 * s, y), (x - 0.3 * s, y + 0.35 * s), (x, y)), quad((x, y), (x + 0.3 * s, y + 0.35 * s), (x + 0.6 * s, y))))
    sun = arc(0, -2.2, 1.4, 0, math.pi, 40)
    sea = [wave(-3.4, 3.4, -2.2, 0.08, 6, 80), wave(-3.4, 3.4, -2.7, 0.08, 7, 80)]
    return make("Migrating Flock", out + [sun] + sea)


@design("bluebird_mailbox", T)
def bluebird_mailbox(rng):
    box = [chain([(-1.6, -0.6), (-1.6, 0.4)], arc(0, 0.4, 1.6, math.pi, 0, 30), [(1.6, -0.6), (-1.6, -0.6)]), [(0, -0.6), (0, -3.0)], ellipse(-1.6, 0.0, 0.2, 0.6, 20)]
    flag = [[(1.6, -0.2), (2.2, -0.2), (2.2, 0.8)], rect(2.2, 0.4, 2.8, 0.8)]
    bird, h = perched(0.2, 2.6, 0.55, beak=0.2, belly=True)
    flowers = [circle(-2.2, -2.6, 0.25, 16), circle(2.4, -2.6, 0.25, 16)]
    return make("Bluebird on a Mailbox", box + flag + bird + flowers, h)


@design("wren", T)
def wren(rng):
    body = chain(cubic((-0.8, 0.4), (-1.2, -1.0), (0.6, -1.4), (1.2, -0.6), 30), [(1.8, 0.8), (1.4, 0.9)], quad((1.4, 0.9), (0.6, 0.6), (0.0, 0.8), 16))
    head = circle(-0.6, 0.7, 0.55, 30)
    beak = poly((-1.1, 0.75), (-1.6, 0.65), (-1.12, 0.55), closed=False)
    brow = arc(-0.6, 0.9, 0.35, math.radians(120), math.radians(200), 8)
    bars = [[(1.2 + 0.1 * k, -0.4 + 0.3 * k), (1.5 + 0.1 * k, -0.3 + 0.3 * k)] for k in range(4)]
    teapot = [ellipse(0.2, -2.4, 1.6, 0.9, 60), quad((1.8, -2.4), (2.6, -1.8), (2.8, -1.4)), arc(-1.8, -2.4, 0.5, math.radians(90), math.radians(270), 12),
              [(-0.6, -1.5), (1.0, -1.5)]]
    return make("Wren on a Teapot", [body, head, beak, brow] + bars + teapot, [eye(-0.7, 0.8, 0.07)])


@design("magpie", T)
def magpie(rng):
    b, h = perched(0, 0.4, 1.1, beak=0.4, tail=2.0, belly=True)
    shiny = [circle(-1.9, 0.4, 0.25, 16), star(-2.5, 1.0, 0.2, 4, 0.3)]
    return make("Magpie with a Ring", b + shiny + branch(-1.2), h, flip=True)


@design("goldfinch_sunflower", T)
def goldfinch_sunflower(rng):
    centre = circle(0.6, -0.4, 1.0, 60)
    petals = [lens((0.6 + 1.0 * math.cos(a), -0.4 + 1.0 * math.sin(a)), (0.6 + 1.9 * math.cos(a), -0.4 + 1.9 * math.sin(a)), 0.3) for a in [k * 2 * math.pi / 14 for k in range(14)]]
    seeds = [arc(0.6, -0.4, r, 0, 2 * math.pi, 20) for r in (0.4, 0.7)]
    stem = [(0.6, -2.3), (0.4, -3.4)]
    bird, h = perched(-1.0, 1.6, 0.55, beak=0.2, tail=0.8)
    wingbar = [[(-0.9, 1.5), (-0.5, 1.4)]]
    return make("Goldfinch and Sunflower", [centre, stem] + petals + seeds + bird + wingbar, h)


@design("owl_pair", T)
def owl_pair(rng):
    def owl(x, s):
        body = ellipse(x, -0.4, 0.9 * s, 1.3 * s, 50)
        ears = [poly((x - 0.6 * s, 0.6 * s), (x - 0.7 * s, 1.2 * s), (x - 0.2 * s, 0.8 * s), closed=False),
                poly((x + 0.6 * s, 0.6 * s), (x + 0.7 * s, 1.2 * s), (x + 0.2 * s, 0.8 * s), closed=False)]
        eyes_ = [circle(x - 0.35 * s, 0.2 * s, 0.3 * s, 20), circle(x + 0.35 * s, 0.2 * s, 0.3 * s, 20)]
        beak = poly((x - 0.1 * s, -0.1 * s), (x + 0.1 * s, -0.1 * s), (x, -0.4 * s))
        return [body, beak] + ears + eyes_
    branch_ = [(-3.0, -1.8), (3.0, -1.8)]
    moon = arc(0, 2.6, 0.6, math.radians(60), math.radians(300), 20)
    return make("Owl Couple", owl(-1.2, 1.1) + owl(1.2, 0.9) + [branch_, moon],
                [eye(-1.6, 0.25, 0.1), eye(-0.8, 0.25, 0.1), eye(0.9, 0.2, 0.08), eye(1.5, 0.2, 0.08)])


@design("penguin_parent", T)
def penguin_parent(rng):
    big = chain(cubic((0, 2.4), (-1.4, 2.4), (-1.6, -1.8), (-0.6, -2.4), 40), [(0.8, -2.4)], cubic((0.8, -2.4), (1.6, -1.8), (1.4, 2.4), (0, 2.4), 40))
    belly = chain(cubic((0, 1.2), (-1.0, 1.0), (-1.1, -1.8), (0, -2.0), 30), cubic((0, -2.0), (1.1, -1.8), (1.0, 1.0), (0, 1.2), 30))
    beak = poly((-0.2, 1.6), (-0.8, 1.4), (-0.2, 1.3), closed=False)
    chick = [ellipse(1.9, -1.6, 0.6, 0.8, 40), circle(1.9, -0.6, 0.4, 24)]
    ice = [(-3.0, -2.4), (3.0, -2.4)]
    return make("Penguin and Chick", [big, belly, beak, ice] + chick, [eye(-0.35, 1.8, 0.09), eye(1.8, -0.5, 0.06)])


@design("hornbill", T)
def hornbill(rng):
    b, h = perched(0.4, 0.2, 1.1, beak=0.0, tail=1.2)
    beak = chain(cubic((-0.6, 1.3), (-1.6, 1.2), (-2.6, 0.4), (-2.8, 0.0), 30), quad((-2.8, 0.0), (-1.6, 0.6), (-0.6, 0.8), 16))
    casque = chain(cubic((-0.5, 1.45), (-1.2, 2.0), (-2.0, 1.6), (-2.0, 1.2), 20))
    return make("Hornbill", b + [beak, casque] + branch(-1.5), h, flip=True)


@design("weathervane", T)
def weathervane(rng):
    rooster = chain(poly((-1.2, 1.0), (-1.4, 1.6), (-1.0, 1.4), (-0.8, 1.8), (-0.6, 1.3), closed=False),
                    cubic((-0.6, 1.3), (0.4, 1.2), (0.8, 0.8), (1.6, 1.6), 16), [(1.8, 0.6)], quad((1.8, 0.6), (0.4, 0.4), (-0.6, 0.6), 12), [(-1.2, 1.0)])
    pole = [(0.2, 0.5), (0.2, -2.6)]
    arrow = [[(-2.0, 0.0), (2.4, 0.0)], poly((2.4, 0.0), (2.0, 0.25), (2.0, -0.25)), poly((-2.0, 0.0), (-2.4, 0.3), (-2.4, -0.3))]
    cross = [[(-1.0, -1.2), (1.4, -1.2)]]
    letters = [poly((-1.4, -1.0), (-1.4, -1.6), (-1.1, -1.6), closed=False), poly((1.6, -1.0), (1.6, -1.6), (1.9, -1.0), (1.9, -1.6), closed=False)]
    return make("Rooster Weathervane", [rooster, pole] + arrow + cross + letters)


@design("quill_ink", T)
def quill_ink(rng):
    vane = transform(chain(cubic((0, -1.6), (1.0, -0.4), (0.8, 1.8), (0.2, 2.6), 30), cubic((0.2, 2.6), (-0.6, 1.8), (-0.8, -0.4), (0, -1.6), 30)), dx=0.6, dy=0.8, rot=-0.4)
    shaft = transform([(0.0, -2.4), (0.2, 2.6)], dx=0.6, dy=0.8, rot=-0.4)
    barbs = [transform(quad((0.05, -1.0 + 0.6 * k), (0.4, -0.8 + 0.6 * k), (0.7, -0.6 + 0.6 * k)), dx=0.6, dy=0.8, rot=-0.4) for k in range(5)]
    pot = [chain([(-1.6, -1.2), (-1.8, -2.8), (-0.2, -2.8), (-0.4, -1.2)]), ellipse(-1.0, -1.2, 0.6, 0.15, 24)]
    paper = [rect(-3.2, -3.2, 3.2, -2.8)]
    return make("Quill and Ink", [vane, shaft] + barbs + pot + paper)
