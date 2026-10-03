"""Dogs niche, part 2 (pictures 11-50)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "dogs"


def dhead(cx, cy, r=1.0, ears="floppy", snout=0.55):
    """Front-facing dog head; returns (strokes, hints)."""
    h = ellipse(cx, cy, r, r * 0.95, 80)
    out = [h]
    if ears == "floppy":
        e = chain(cubic((-0.7, 0.7), (-1.5, 0.9), (-1.6, -0.5), (-1.15, -0.8), 20), quad((-1.15, -0.8), (-0.9, -0.3), (-0.95, 0.2), 10))
        out += [transform(e, dx=cx, dy=cy, s=r), transform(mirror_x(e), dx=cx, dy=cy, s=r)]
    elif ears == "pointy":
        e = poly((-0.75, 0.6), (-0.95, 1.6), (-0.25, 0.9), closed=False)
        out += [transform(e, dx=cx, dy=cy, s=r), transform(mirror_x(e), dx=cx, dy=cy, s=r)]
    elif ears == "round":
        out += [circle(cx - 0.8 * r, cy + 0.75 * r, 0.3 * r, 20), circle(cx + 0.8 * r, cy + 0.75 * r, 0.3 * r, 20)]
    elif ears == "big":
        e = poly((-0.6, 0.5), (-1.6, 1.4), (-0.4, 0.95), closed=False)
        out += [transform(e, dx=cx, dy=cy, s=r), transform(mirror_x(e), dx=cx, dy=cy, s=r)]
    out.append(ellipse(cx, cy - 0.45 * r, snout * r, snout * 0.7 * r, 40))
    out.append(chain(quad((cx - 0.2 * r, cy - 0.2 * r), (cx, cy - 0.05 * r), (cx + 0.2 * r, cy - 0.2 * r)),
                     quad((cx + 0.2 * r, cy - 0.2 * r), (cx, cy - 0.45 * r), (cx - 0.2 * r, cy - 0.2 * r))))
    out.append(chain(quad((cx - 0.3 * r, cy - 0.7 * r), (cx - 0.1 * r, cy - 0.8 * r), (cx, cy - 0.45 * r)),
                     quad((cx, cy - 0.45 * r), (cx + 0.1 * r, cy - 0.8 * r), (cx + 0.3 * r, cy - 0.7 * r))))
    hints = [eye(cx - 0.4 * r, cy + 0.2 * r, 0.12 * r), eye(cx + 0.4 * r, cy + 0.2 * r, 0.12 * r)]
    return out, hints


def sit(cx, cy, s=1.0):
    body = chain(cubic((-0.5, 0.6), (-1.4, -0.2), (-1.5, -2.0), (-0.9, -2.6), 30), [(0.9, -2.6)],
                 cubic((0.9, -2.6), (1.5, -2.0), (1.4, -0.2), (0.5, 0.6), 30))
    legs = [[(-0.3, -0.3), (-0.35, -2.6)], [(0.3, -0.3), (0.35, -2.6)]]
    paws = [arc(-0.6, -2.6, 0.25, 0, math.pi, 8), arc(0.6, -2.6, 0.25, 0, math.pi, 8)]
    tail = quad((1.2, -2.2), (2.2, -2.0), (2.2, -1.2))
    return [transform(p, dx=cx, dy=cy, s=s) for p in [body, tail] + legs + paws]


def stand(cx, cy, s=1.0, L=3.0):
    body = rrect(-L / 2, -0.55, L / 2, 0.55, 0.5)
    legs = [leg(x, x + 0.35, -0.3, -1.8) for x in (-L / 2 + 0.2, -L / 2 + 0.75, L / 2 - 1.0, L / 2 - 0.45)]
    tail = quad((L / 2 - 0.1, 0.3), (L / 2 + 0.7, 0.8), (L / 2 + 0.9, 1.4))
    return [transform(p, dx=cx, dy=cy, s=s) for p in [body, tail] + legs]


def side_head(cx, cy, s=1.0, ear="floppy"):
    h = chain(cubic((0.4, -0.5), (-0.6, -0.6), (-0.8, 0.8), (0.2, 0.9), 20), quad((0.2, 0.9), (0.6, 0.8), (0.8, 0.4), 8),
              [(1.6, 0.3)], quad((1.9, 0.2), (1.8, -0.3), (1.6, -0.3), 6), [(0.4, -0.5)])
    ear_ = chain(cubic((0.0, 0.8), (-0.6, 0.8), (-0.7, -0.2), (-0.3, -0.3), 16)) if ear == "floppy" else poly((-0.2, 0.7), (-0.1, 1.6), (0.3, 0.85), closed=False)
    out = [transform(p, dx=cx, dy=cy, s=s) for p in [h, ear_]]
    return out, [eye(cx + 0.45 * s, cy + 0.45 * s, 0.1 * s), eye(cx + 1.75 * s, cy + 0.0 * s, 0.1 * s)]


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


@design("pug", T)
def pug(rng):
    h, e = dhead(0, 0.4, 1.8, "round", snout=0.65)
    wrinkles = [arc(0, 1.4, 0.5, math.radians(30), math.radians(150), 10), arc(0, 1.1, 0.35, math.radians(30), math.radians(150), 8)]
    return make("Pug Face", h + wrinkles, e)


@design("corgi", T)
def corgi(rng):
    body = stand(0.3, -0.4, 1.0, 3.6)
    h, e = side_head(-1.9, 0.6, 0.9, "pointy")
    e2 = [poly((-2.2, 1.3), (-2.3, 2.1), (-1.8, 1.4), closed=False)]
    butt = arc(2.1, -0.2, 0.4, math.radians(-90), math.radians(90), 10)
    return make("Corgi", body + h + e2 + [butt], e)


@design("beagle", T)
def beagle(rng):
    b = sit(0, -0.6, 0.8)
    h, e = dhead(0, 1.0, 0.9, "floppy")
    spot = chain(cubic((-0.6, -0.4), (-1.1, -0.6), (-1.1, -1.6), (-0.6, -1.7), 12), quad((-0.6, -1.7), (-0.3, -1.0), (-0.6, -0.4), 8))
    return make("Beagle", b + h + [spot], e)


@design("labrador", T)
def labrador(rng):
    h, e = dhead(0, 0.5, 1.9, "floppy", snout=0.6)
    collar = [quad((-1.4, -1.3), (0, -2.0), (1.4, -1.3)), quad((-1.3, -1.6), (0, -2.3), (1.3, -1.6)), circle(0, -2.5, 0.3, 20)]
    return make("Labrador", h + collar, e)


@design("shepherd", T)
def shepherd(rng):
    h, e = dhead(0, 0.3, 1.8, "pointy", snout=0.5)
    mask = [quad((-1.2, 0.9), (0, 0.4), (1.2, 0.9))]
    chest = [quad((-1.4, -1.4), (0, -2.8), (1.4, -1.4))]
    return make("German Shepherd", h + mask + chest, e)


@design("husky", T)
def husky(rng):
    h, e = dhead(0, 0.2, 1.8, "pointy", snout=0.5)
    mask = [chain(quad((-1.6, 0.4), (-1.0, 1.6), (0, 1.2)), quad((0, 1.2), (1.0, 1.6), (1.6, 0.4)))]
    brow = [circle(-0.6, 1.0, 0.15, 10), circle(0.6, 1.0, 0.15, 10)]
    snow = [star(x, y, 0.2, 6, 0.5) for x, y in [(-2.6, 2.4), (2.6, 2.6), (2.8, -1.6)]]
    return make("Husky", h + mask + brow + snow, e)


@design("dalmatian", T)
def dalmatian(rng):
    body = stand(0.4, -0.5, 1.0, 3.2)
    h, e = side_head(-1.8, 0.5, 0.85)
    spots = [circle(x, y, 0.13, 10) for x, y in [(-0.4, -0.2), (0.4, 0.1), (1.0, -0.3), (1.5, 0.15), (-0.8, 0.2), (0.0, -0.4)]]
    hydrant = [rect(2.6, -2.3, 3.2, -0.9), arc(2.9, -0.9, 0.3, 0, math.pi, 10)]
    return make("Dalmatian", body + h + spots + hydrant, e)


@design("bulldog", T)
def bulldog(rng):
    h, e = dhead(0, 0.8, 1.5, "round", snout=0.8)
    jowls = [arc(-0.6, -0.3, 0.6, math.radians(200), math.radians(340), 12), arc(0.6, -0.3, 0.6, math.radians(200), math.radians(340), 12)]
    body = chain(quad((-1.4, -0.4), (-2.4, -1.6), (-2.0, -2.6)), [(2.0, -2.6)], quad((2.0, -2.6), (2.4, -1.6), (1.4, -0.4)))
    collar = [quad((-1.4, -0.6), (0, -1.1), (1.4, -0.6))] + [circle(x, -0.85 + 0.0 * x, 0.08, 8) for x in (-0.8, 0.0, 0.8)]
    return make("Bulldog", h + jowls + [body] + collar, e)


@design("chihuahua", T)
def chihuahua(rng):
    h, e = dhead(0, 0.6, 1.2, "big", snout=0.45)
    bag = [rrect(-1.8, -2.6, 1.8, -0.4, 0.3), arc(0, -0.4, 1.4, 0, math.pi, 20), heart(0, -1.6, 0.4)]
    paws = [ellipse(-0.5, -0.45, 0.3, 0.2, 16), ellipse(0.5, -0.45, 0.3, 0.2, 16)]
    return make("Chihuahua in a Bag", h + bag + paws, e)


@design("terrier", T)
def terrier(rng):
    body = stand(0.3, -0.5, 1.0, 2.6)
    head_ = rrect(-2.4, -0.2, -0.9, 1.2, 0.2)
    beard = zigzag(-2.4, -1.6, -0.25, 0.12, 4)
    ears = [poly((-1.4, 1.2), (-1.2, 1.8), (-1.0, 1.2), closed=False)]
    brows = [[(-2.2, 0.85), (-1.8, 0.95)]]
    return make("Scruffy Terrier", body + [head_, beard] + ears + brows, [eye(-1.95, 0.7, 0.09), eye(-2.45, 0.2, 0.1)])


@design("dog_fetch", T)
def dog_fetch(rng):
    body = stand(0.4, -0.6, 1.0, 3.0)
    h, e = side_head(-1.6, 0.5, 0.9)
    ball = [circle(-3.2, 2.2, 0.45, 30), arc(-3.6, 2.2, 0.35, math.radians(-50), math.radians(50), 8)]
    motion = [[(-2.6, 2.4), (-2.0, 2.6)], [(-2.6, 2.0), (-2.0, 2.0)]]
    return make("Playing Fetch", body + h + ball + motion, e)


@design("dog_frisbee_jump", T)
def dog_frisbee_jump(rng):
    body = transform(rrect(-1.4, -0.5, 1.4, 0.5, 0.45), rot=0.35)
    legs = [[(-1.0, -0.6), (-1.8, -1.4)], [(-0.5, -0.8), (-1.0, -1.6)], [(1.0, 0.2), (2.0, -0.4)], [(0.8, 0.0), (1.6, -0.8)]]
    h, e = side_head(-1.4, 1.0, 0.8)
    disc = [ellipse(-2.6, 2.2, 0.8, 0.25, 30, rot=0.2)]
    grass = [zigzag(-3.2, 3.2, -2.6, 0.15, 14)]
    return make("Frisbee Catch", [body] + legs + h + disc + grass, e)


@design("dog_bath", T)
def dog_bath(rng):
    tub = chain(quad((-2.8, 0.0), (-2.6, -2.0), (0, -2.0), 20), quad((0, -2.0), (2.6, -2.0), (2.8, 0.0), 20), [(-2.8, 0.0)])
    h, e = dhead(0, 0.9, 0.9, "floppy")
    bubbles = [circle(x, y, r, 16) for x, y, r in [(-1.8, 0.3, 0.45), (-1.1, 0.25, 0.3), (1.2, 0.3, 0.4), (1.9, 0.6, 0.3), (-2.2, 1.2, 0.25), (2.3, 1.6, 0.2)]]
    shower = [[(2.6, 3.0), (1.6, 3.0)], poly((1.6, 3.2), (1.0, 2.6), (2.0, 2.6))] + [[(1.2 + 0.25 * k, 2.4), (1.0 + 0.25 * k, 2.0)] for k in range(3)]
    return make("Bath Time Dog", [tub] + h + bubbles + shower, e)


@design("dog_bed", T)
def dog_bed(rng):
    bed = [rrect(-2.8, -2.2, 2.8, -0.6, 0.6), rrect(-2.2, -1.6, 2.2, -0.9, 0.3)]
    curl = arc(0.3, -0.9, 1.2, 0, math.pi, 30)
    h, e = dhead(-0.9, -0.3, 0.6, "floppy")
    bone = [circle(2.2, 1.0, 0.18, 12), circle(2.2, 0.7, 0.18, 12), [(2.3, 0.85), (3.0, 0.85)], circle(3.1, 1.0, 0.18, 12), circle(3.1, 0.7, 0.18, 12)]
    return make("Dog Bed Nap", bed + [curl] + h + bone, e)


@design("puppy_basket", T)
def puppy_basket(rng):
    basket = chain(quad((-2.4, 0.0), (-2.2, -2.2), (0, -2.4), 30), quad((0, -2.4), (2.2, -2.2), (2.4, 0.0), 30), [(-2.4, 0.0)])
    weave = [quad((-2.3, -0.6 - 0.55 * k), (0, -0.8 - 0.55 * k), (2.3, -0.6 - 0.55 * k)) for k in range(3)]
    h1, e1 = dhead(-1.0, 0.8, 0.6, "floppy")
    h2, e2 = dhead(1.0, 0.85, 0.65, "pointy")
    bow = [lens((2.4, 0.0), (3.0, 0.5), 0.4), lens((2.4, 0.0), (3.0, -0.5), 0.4)]
    return make("Puppies in a Basket", [basket] + weave + h1 + h2 + bow, e1 + e2)


@design("dog_bird", T)
def dog_bird(rng):
    b = sit(-0.6, -0.6, 0.75)
    h, e = dhead(-0.6, 0.9, 0.8, "floppy")
    bird = [chain(cubic((1.4, 2.2), (1.6, 2.8), (2.4, 2.8), (2.5, 2.4), 16), [(1.4, 2.2)]), poly((2.5, 2.5), (2.8, 2.45), (2.5, 2.35), closed=False)]
    branch = [(0.8, 2.1), (3.2, 2.0)]
    return make("Dog and Bird Friend", b + h + bird + [branch], e + [eye(2.2, 2.55, 0.06)])


@design("dog_walk", T)
def dog_walk(rng):
    body = stand(0.6, -0.8, 0.9, 2.8)
    h, e = side_head(-1.1, 0.2, 0.8)
    leash = quad((-0.9, -0.2), (-1.8, 1.6), (-2.6, 2.6))
    hand = [circle(-2.7, 2.8, 0.3, 20)]
    path = [(-3.2, -2.5), (3.2, -2.5)]
    tree = [[(2.8, -2.5), (2.8, 0.4)], circle(2.8, 1.2, 0.9, 40)]
    return make("Walk in the Park", body + h + [leash, path] + hand + tree, e)


@design("dog_sleeping", T)
def dog_sleeping(rng):
    body = ellipse(0.5, -0.6, 2.2, 1.0, 100)
    h = [ellipse(-1.4, -0.4, 0.9, 0.7, 50), chain(cubic((-1.6, 0.2), (-2.4, 0.2), (-2.6, -0.8), (-2.2, -1.0), 16))]
    lids = [arc(-1.2, -0.3, 0.18, math.radians(200), math.radians(340), 8)]
    zz = [[(-0.4, 1.0), (0.0, 1.0), (-0.4, 0.6), (0.0, 0.6)], [(0.4, 1.8), (0.9, 1.8), (0.4, 1.3), (0.9, 1.3)]]
    tail = quad((2.6, -0.8), (2.4, -1.8), (1.0, -1.8))
    return make("Sleepy Dog", [body, tail] + h + lids + zz)


@design("dog_birthday", T)
def dog_birthday(rng):
    h, e = dhead(0, 0.2, 1.4, "floppy")
    hat = [poly((-0.6, 1.4), (0.1, 3.2), (0.7, 1.35)), circle(0.1, 3.35, 0.18, 12)]
    stripes = [[(-0.35, 1.9), (0.5, 2.0)], [(-0.15, 2.5), (0.35, 2.55)]]
    cake = [rect(-1.4, -3.0, 1.4, -2.0), wave(-1.4, 1.4, -2.2, 0.1, 4, 40), rect(-0.1, -2.0, 0.1, -1.5), lens((0, -1.45), (0, -1.0), 0.4)]
    confetti = [star(x, y, 0.18) for x, y in [(-2.6, 2.6), (2.4, 2.4), (-2.6, -1.0), (2.6, -0.8)]]
    return make("Birthday Pup", h + hat + stripes + cake + confetti, e)


@design("dog_house_peek", T)
def dog_house_peek(rng):
    walls = rect(-2.0, -2.4, 2.0, 0.6)
    roof = poly((-2.6, 0.4), (0, 2.6), (2.6, 0.4), closed=False)
    door = chain([(-0.9, -2.4), (-0.9, -0.6)], arc(0, -0.6, 0.9, math.pi, 0, 24), [(0.9, -2.4)])
    h, e = dhead(0, -1.0, 0.65, "floppy")
    paws = [ellipse(-0.4, -2.3, 0.28, 0.15, 14), ellipse(0.4, -2.3, 0.28, 0.15, 14)]
    sign = [rrect(-0.8, 1.0, 0.8, 1.5, 0.1)]
    return make("Peeking from the Dog House", [walls, roof, door] + h + paws + sign, e)


@design("dog_newspaper", T)
def dog_newspaper(rng):
    b = sit(0, -0.6, 0.8)
    h, e = dhead(0, 1.0, 0.85, "floppy")
    paper = transform(rect(-1.2, -0.3, 1.2, 0.3), dx=0, dy=0.35, rot=-0.1)
    lines_ = [transform([(-0.9, 0.0), (0.9, 0.0)], dx=0, dy=0.35, rot=-0.1)]
    mat = [rect(-2.4, -3.0, 2.4, -2.5)]
    return make("Dog Fetching Newspaper", b + h + [paper] + lines_ + mat, e)


@design("dog_with_bone", T)
def dog_with_bone(rng):
    body = stand(0.4, -0.6, 1.0, 3.0)
    h, e = side_head(-1.6, 0.5, 0.9)
    bone = [rect(-0.7, -0.05, 0.4, 0.1), circle(-0.75, 0.15, 0.15, 10), circle(-0.75, -0.1, 0.15, 10), circle(0.45, 0.15, 0.15, 10), circle(0.45, -0.1, 0.15, 10)]
    bone = [transform(p, dx=-0.2, dy=0.0) for p in bone]
    return make("Proud Dog with Bone", body + h + bone, e)


@design("dog_shake", T)
def dog_shake(rng):
    b = sit(0, -0.6, 0.85)
    h, e = dhead(0, 1.0, 0.9, "pointy")
    paw = [tube([(0.6, -0.4), (1.6, 0.2)], 0.45), ellipse(1.75, 0.3, 0.35, 0.3, 20)]
    hand = [chain(quad((2.0, 0.6), (3.0, 0.8), (3.4, 0.2)), quad((3.4, 0.2), (2.8, -0.2), (2.0, 0.0)))]
    return make("Shake a Paw", b + h + paw + hand, e)


@design("dog_bandana", T)
def dog_bandana(rng):
    h, e = dhead(0, 0.8, 1.6, "floppy")
    bandana = [poly((-1.4, -0.6), (1.4, -0.6), (0, -2.4)), [(-1.4, -0.6), (-1.8, -0.2)], [(1.4, -0.6), (1.8, -0.2)]]
    dots = [circle(x, y, 0.12, 10) for x, y in [(-0.6, -0.9), (0.0, -1.2), (0.6, -0.9), (0.0, -1.7)]]
    return make("Dog in a Bandana", h + bandana + dots, e)


@design("dog_sweater", T)
def dog_sweater(rng):
    body = stand(0.4, -0.5, 1.0, 3.0)
    sweater = [rrect(-0.8, -0.6, 1.6, 0.65, 0.4), zigzag(-0.6, 1.4, 0.0, 0.15, 5)]
    h, e = side_head(-1.6, 0.5, 0.9)
    flakes = [star(x, y, 0.2, 6, 0.5) for x, y in [(-2.6, 2.4), (1.6, 2.6), (2.8, 1.4)]]
    return make("Dog in a Sweater", body + sweater + h + flakes, e)


@design("dog_raincoat", T)
def dog_raincoat(rng):
    b = sit(0, -0.8, 0.8)
    h, e = dhead(0, 0.8, 0.85, "floppy")
    hood = arc(0, 0.8, 1.15, math.radians(-10), math.radians(190), 30)
    coat = [quad((-1.0, -0.2), (0, -0.6), (1.0, -0.2)), [(0, -0.4), (0, -2.2)]] + [circle(0.2, y, 0.08, 8) for y in (-0.9, -1.4)]
    drops = [lens((x, y), (x, y - 0.4), 0.4) for x, y in [(-2.6, 2.6), (2.4, 2.8), (2.8, 0.8), (-2.8, 0.4)]]
    puddle = ellipse(0, -2.9, 2.4, 0.3, 60)
    return make("Dog in a Raincoat", b + h + [hood, puddle] + coat + drops, e)


@design("dog_car_window", T)
def dog_car_window(rng):
    car = [chain([(-3.2, -2.0), (-3.2, -0.6)], [(-2.0, 0.8), (1.6, 0.8), (2.8, -0.6), (3.2, -0.6), (3.2, -2.0), (-3.2, -2.0)]),
           poly((-1.8, -0.5), (-1.2, 0.5), (0.2, 0.5), (0.2, -0.5))]
    h, e = side_head(-0.8, 0.8, 0.85)
    ears_flap = [quad((-1.0, 1.4), (-1.8, 1.8), (-2.6, 1.6))]
    wheels = [circle(-2.0, -2.0, 0.55, 30), circle(2.0, -2.0, 0.55, 30)]
    wind = [[(-3.2, 2.2), (-2.4, 2.2)], [(-3.0, 2.6), (-2.2, 2.6)]]
    return make("Road Trip Dog", car + h + ears_flap + wheels + wind, e)


@design("dog_beach", T)
def dog_beach(rng):
    b = sit(-0.6, -0.6, 0.75)
    h, e = dhead(-0.6, 0.9, 0.8, "pointy")
    shades = [rrect(-1.25, 0.95, -0.7, 1.3, 0.12), rrect(-0.5, 0.95, 0.05, 1.3, 0.12), [(-0.7, 1.15), (-0.5, 1.15)]]
    umbrella = [chain(arc(2.0, 1.4, 1.4, math.radians(10), math.radians(170), 40)), [(2.0, 2.8), (2.0, -2.6)]]
    sand = [wave(-3.2, 3.2, -2.7, 0.1, 4, 80)]
    return make("Beach Dog", b + h + shades + umbrella + sand, [])


@design("puppy_love", T)
def puppy_love(rng):
    h1, e1 = dhead(-1.3, 0.0, 1.0, "floppy")
    h2, e2 = dhead(1.3, 0.0, 1.0, "pointy")
    love = heart(0, 2.0, 0.6)
    small = [heart(-2.6, 2.4, 0.3), heart(2.6, 2.6, 0.25)]
    return make("Puppy Love", h1 + h2 + [love] + small, e1 + e2)


@design("dog_portrait", T)
def dog_portrait(rng):
    frame = [rrect(-2.4, -2.8, 2.4, 2.8, 0.4), rrect(-2.0, -2.4, 2.0, 2.4, 0.3)]
    h, e = dhead(0, 0.4, 1.2, "floppy")
    shoulders = quad((-1.8, -2.4), (0, -0.4), (1.8, -2.4))
    tie = [poly((0, -1.0), (-0.3, -1.3), (0, -2.2), (0.3, -1.3))]
    return make("Distinguished Dog", frame + h + [shoulders] + tie, e)


@design("treat_jar", T)
def treat_jar(rng):
    jar = [rrect(-1.8, -2.6, 1.8, 1.2, 0.5), rect(-1.4, 1.2, 1.4, 1.8), rect(-1.6, 1.8, 1.6, 2.2), circle(0, 2.5, 0.3, 20)]
    label = [rrect(-1.2, -1.2, 1.2, 0.2, 0.2)]
    bones = []
    for x, y in [(-0.8, -1.9), (0.6, -2.0), (-0.2, 0.6)]:
        bones += [rect(x - 0.4, y - 0.08, x + 0.4, y + 0.08), circle(x - 0.45, y + 0.1, 0.12, 8), circle(x - 0.45, y - 0.1, 0.12, 8),
                  circle(x + 0.45, y + 0.1, 0.12, 8), circle(x + 0.45, y - 0.1, 0.12, 8)]
    paw = [circle(0, -0.6, 0.25, 16)] + [circle(dx, -0.2, 0.1, 8) for dx in (-0.3, 0.0, 0.3)]
    return make("Treat Jar", jar + label + bones + paw)


@design("leash_collar", T)
def leash_collar(rng):
    collar = [ellipse(-1.0, 0.4, 1.6, 0.9, 80), ellipse(-1.0, 0.4, 1.3, 0.65, 70)]
    buckle = [rect(-2.75, 0.1, -2.35, 0.7)]
    leash = cubic((0.6, 0.4), (2.6, 1.2), (1.0, -2.0), (2.6, -2.4), 40)
    handle = [ellipse(2.8, -2.4, 0.5, 0.3, 24)]
    tag = [circle(-1.0, -0.65, 0.35, 24), [(-1.0, -0.3), (-1.0, -0.5)]]
    return make("Collar and Leash", collar + buckle + [leash] + handle + tag)


@design("rope_toy", T)
def rope_toy(rng):
    rope = tube([(-2.2, 0.0), (2.2, 0.0)], 0.6)
    twists = [[(-1.8 + 0.4 * k, -0.3), (-1.6 + 0.4 * k, 0.3)] for k in range(10)]
    knots = [circle(-2.5, 0.0, 0.5, 30), circle(2.5, 0.0, 0.5, 30)]
    fringe = [[(-3.0, y), (-3.6, y + 0.1 * y)] for y in (-0.3, 0.0, 0.3)] + [[(3.0, y), (3.6, y + 0.1 * y)] for y in (-0.3, 0.0, 0.3)]
    return make("Rope Tug Toy", [rope] + twists + knots + fringe)


@design("squeaky_toy", T)
def squeaky_toy(rng):
    body = chain(cubic((-2.0, -0.4), (-2.0, -1.8), (1.8, -1.8), (2.0, -0.2), 30), [(2.6, 0.4), (1.8, 0.4)], quad((1.8, 0.4), (0.0, 0.0), (-0.8, 0.4), 20))
    head = circle(-1.4, 1.0, 0.8, 50)
    beak = chain(quad((-2.1, 1.0), (-2.9, 1.0), (-2.9, 0.7)), quad((-2.9, 0.7), (-2.5, 0.5), (-2.1, 0.7)))
    wing = quad((-0.6, -0.4), (0.4, 0.2), (1.0, -0.6))
    notes = [[(1.6, 2.0), (1.6, 2.8), (2.0, 2.6)], circle(1.45, 2.0, 0.15, 10)]
    return make("Squeaky Duck Toy", [body, head, beak, wing] + notes, [eye(-1.3, 1.2, 0.1)])


@design("paw_heart", T)
def paw_heart(rng):
    pad = heart(0, -0.6, 1.6)
    toes = [ellipse(x, y, 0.45, 0.6, 30, rot=r) for x, y, r in [(-1.6, 1.0, 0.35), (-0.55, 1.6, 0.1), (0.55, 1.6, -0.1), (1.6, 1.0, -0.35)]]
    return make("Paw Print Heart", [pad] + toes)


@design("dog_food_bag", T)
def dog_food_bag(rng):
    bag = poly((-1.8, -2.6), (1.8, -2.6), (1.6, 1.8), (1.2, 2.4), (-1.2, 2.4), (-1.6, 1.8))
    fold = [(-1.6, 1.8), (1.6, 1.8)]
    h, e = dhead(0, 0.0, 0.8, "floppy")
    bowl = [ellipse(2.4, -2.4, 0.8, 0.2, 30), quad((1.6, -2.4), (2.4, -3.0), (3.2, -2.4))]
    return make("Bag of Dog Food", [bag, fold] + h + bowl, e)


@design("agility_hoop", T)
def agility_hoop(rng):
    hoop = [circle(0.6, 0.6, 1.6, 90), circle(0.6, 0.6, 1.35, 80)]
    stand_ = [[(0.6, -1.0), (0.6, -2.6)], [(-0.4, -2.6), (1.6, -2.6)]]
    body = transform(rrect(-1.2, -0.4, 1.2, 0.4, 0.4), dx=0.6, dy=0.6, rot=0.15)
    legs = [[(-0.4, 0.4), (-1.4, 0.0)], [(-0.2, 0.2), (-1.2, -0.4)], [(1.6, 0.9), (2.6, 1.4)], [(1.6, 0.7), (2.6, 0.9)]]
    h, e = side_head(1.6, 1.0, 0.65)
    return make("Agility Hoop Jump", hoop + stand_ + [body] + legs + h, e)


@design("sheepdog", T)
def sheepdog(rng):
    fluff = polar(lambda t: 1.9 + 0.12 * math.sin(14 * t), n=300, cy=0.4)
    fringe = zigzag(-1.4, 1.4, 0.9, 0.25, 6)
    nose = chain(quad((-0.3, -0.2), (0, 0.1), (0.3, -0.2)), quad((0.3, -0.2), (0, -0.5), (-0.3, -0.2)))
    mouth = arc(0, -0.5, 0.35, math.radians(210), math.radians(330), 10)
    tongue = quad((-0.15, -0.8), (0, -1.2), (0.15, -0.8))
    return make("Shaggy Sheepdog", [fluff, fringe, nose, mouth, tongue])


@design("dog_bench", T)
def dog_bench(rng):
    bench = [rect(-2.8, -0.6, 2.8, -0.3), rect(-2.8, 0.6, 2.8, 0.9), rect(-2.8, 1.2, 2.8, 1.5)]
    legs_ = [[(-2.4, -0.6), (-2.4, -2.4)], [(2.4, -0.6), (2.4, -2.4)], [(-2.4, -0.3), (-2.4, 1.5)], [(2.4, -0.3), (2.4, 1.5)]]
    b = sit(-0.6, 1.5, 0.45)
    h, e = dhead(-0.6, 2.35, 0.5, "floppy")
    lamp = [[(3.2, -2.4), (3.2, 2.8)], poly((2.9, 2.8), (3.5, 2.8), (3.3, 3.3), (3.1, 3.3))]
    return make("Dog on a Park Bench", bench + legs_ + b + h + lamp, e)


@design("dog_slippers", T)
def dog_slippers(rng):
    h, e = dhead(-0.6, 0.8, 1.1, "floppy")
    body = chain(quad((-1.6, 0.0), (-2.2, -1.6), (-1.6, -2.4)), [(0.4, -2.4)], quad((0.4, -2.4), (1.0, -1.6), (0.4, 0.0)))
    slippers = [rrect(1.2, -2.6, 3.0, -1.9, 0.35), rrect(1.4, -1.9, 3.2, -1.2, 0.35)]
    pompoms = [circle(1.5, -1.9, 0.2, 12), circle(1.7, -1.2, 0.2, 12)]
    return make("Dog with Slippers", h + [body] + slippers + pompoms, e)


@design("dog_ice_cream", T)
def dog_ice_cream(rng):
    h, e = dhead(-0.8, 0.6, 1.1, "floppy")
    tongue = quad((-1.0, -0.3), (-0.6, -0.9), (-0.2, -0.4))
    cone = [poly((1.2, -0.4), (2.4, -0.4), (1.8, -2.6)), circle(1.8, 0.0, 0.7, 40)]
    drip = lens((1.2, -0.2), (1.2, -0.8), 0.4)
    return make("Dog and Ice Cream", h + [tongue, drip] + cone, e)


@design("dog_mailbox", T)
def dog_mailbox(rng):
    box = [chain([(1.0, 0.0), (1.0, 1.4)], arc(2.0, 1.4, 1.0, math.pi, 0, 20), [(3.0, 0.0), (1.0, 0.0)]), [(2.0, 0.0), (2.0, -2.6)],
           [(3.0, 1.6), (3.0, 2.6)], poly((3.0, 2.6), (3.6, 2.4), (3.0, 2.2))]
    b = sit(-1.2, -0.4, 0.6)
    h, e = dhead(-1.2, 0.75, 0.65, "pointy")
    letter = [rect(-0.3, 0.2, 0.7, 0.8), [(-0.3, 0.8), (0.2, 0.45), (0.7, 0.8)]]
    return make("Dog at the Mailbox", box + b + h + letter, e)
