"""Halloween niche, part 2 (pictures 12-51)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "halloween"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


def pumpkin(cx, cy, s, face=None):
    """Ribbed pumpkin; face is None, 'happy' or 'scared'."""
    out = [ellipse(cx, cy, 0.7 * s, 1.0 * s, 70)]
    for dx, rx in [(0.55, 0.75), (1.0, 0.65)]:
        half = [(cx + (dx + rx * math.cos(t)) * s, cy + 0.95 * s * math.sin(t)) for t in [-math.pi / 2 + math.pi * i / 40 for i in range(41)]]
        out += [half, mirror_x(half, cx)]
    out.append(poly((cx - 0.12 * s, cy + 0.95 * s), (cx - 0.2 * s, cy + 1.4 * s), (cx + 0.15 * s, cy + 1.45 * s), (cx + 0.15 * s, cy + 0.95 * s), closed=False))
    if face == "happy":
        out += [poly((cx - 0.75 * s, cy + 0.2 * s), (cx - 0.25 * s, cy + 0.2 * s), (cx - 0.5 * s, cy + 0.6 * s)),
                poly((cx + 0.25 * s, cy + 0.2 * s), (cx + 0.75 * s, cy + 0.2 * s), (cx + 0.5 * s, cy + 0.6 * s)),
                poly((cx - 0.9 * s, cy - 0.3 * s), (cx - 0.3 * s, cy - 0.45 * s), (cx, cy - 0.3 * s), (cx + 0.3 * s, cy - 0.45 * s), (cx + 0.9 * s, cy - 0.3 * s),
                     (cx + 0.4 * s, cy - 0.75 * s), (cx - 0.4 * s, cy - 0.75 * s))]
    elif face == "scared":
        out += [circle(cx - 0.45 * s, cy + 0.3 * s, 0.22 * s, 20), circle(cx + 0.45 * s, cy + 0.3 * s, 0.22 * s, 20),
                ellipse(cx, cy - 0.45 * s, 0.25 * s, 0.32 * s, 24)]
    return out


def mini_bat(x, y, s):
    return poly((x - s, y), (x - 0.55 * s, y + 0.3 * s), (x - 0.2 * s, y + 0.1 * s), (x, y + 0.3 * s), (x + 0.2 * s, y + 0.1 * s),
                (x + 0.55 * s, y + 0.3 * s), (x + s, y), (x + 0.5 * s, y - 0.05 * s), (x, y - 0.3 * s), (x - 0.5 * s, y - 0.05 * s))


@design("hw_witch_on_broom", T)
def witch_on_broom(rng):
    moon = circle(0, 0.4, 2.4, 160)
    stick = [[(-2.6, -0.6), (2.6, 0.6)]]
    bristles = poly((1.9, 0.43), (3.0, 1.1), (3.2, 0.4), (3.0, -0.2), (2.0, 0.2))
    body = poly((-0.6, -0.2), (-0.1, 1.2), (0.6, 0.15))
    head = circle(-0.1, 1.45, 0.3, 24)
    hat = poly((-0.75, 1.6), (0.55, 1.6), (0.3, 1.75), (-0.5, 2.6), (-0.25, 1.75), (-0.75, 1.6), closed=False)
    cape = poly((-0.3, 1.0), (-1.6, 0.6), (-1.0, 0.3), (-1.8, 0.0), (-0.5, 0.0), closed=False)
    boot = [[(0.4, 0.1), (0.4, -0.6), (0.8, -0.6)]]
    return make("Witch Flying Across the Moon", [moon, bristles, body, head, hat, cape] + stick + boot + [mini_bat(-2.6, 2.6, 0.4), mini_bat(2.4, -2.6, 0.35)])


@design("hw_skull", T)
def skull(rng):
    cran = chain(arc(0, 0.4, 2.0, math.radians(-30), math.radians(210), 100), [(-1.2, -1.2), (-1.2, -1.9), (1.2, -1.9), (1.2, -1.2)],
                 [(1.73, -0.6)])
    eyes_ = [ellipse(-0.75, 0.0, 0.55, 0.6, 40), ellipse(0.75, 0.0, 0.55, 0.6, 40)]
    nose = poly((0, -0.5), (-0.25, -1.0), (0.25, -1.0))
    teeth = [[(x, -1.3), (x, -1.9)] for x in (-0.6, -0.2, 0.2, 0.6)] + [[(-1.2, -1.3), (1.2, -1.3)]]
    crack = [poly((0.4, 2.35), (0.6, 1.8), (0.3, 1.5), (0.55, 1.1), closed=False)]
    return make("Grinning Skull", [cran, nose] + eyes_ + teeth + crack)


@design("hw_dancing_skeleton", T)
def dancing_skeleton(rng):
    head = circle(0, 2.3, 0.6, 50)
    sockets = [circle(-0.22, 2.4, 0.15, 14), circle(0.22, 2.4, 0.15, 14)]
    spine = [[(0, 1.7), (0, -0.4)]]
    ribs = [ellipse(0, 1.2 - 0.35 * k, 0.75 - 0.08 * k, 0.12, 30) for k in range(4)]
    pelvis = ellipse(0, -0.6, 0.6, 0.3, 30)
    arms = [[(-0.7, 1.4), (-1.5, 2.0), (-2.2, 2.8)], [(0.7, 1.4), (1.5, 0.8), (2.3, 1.4)]]
    hands = [circle(-2.3, 2.95, 0.18, 14), circle(2.45, 1.5, 0.18, 14)]
    legs = [[(-0.4, -0.85), (-1.2, -1.8), (-1.0, -2.8)], [(0.4, -0.85), (1.4, -1.6), (2.2, -1.2)]]
    feet = [ellipse(-0.75, -2.85, 0.35, 0.14, 16), ellipse(2.4, -1.05, 0.35, 0.14, 16, rot=0.6)]
    joints = [circle(x, y, 0.12, 12) for x, y in [(-1.5, 2.0), (1.5, 0.8), (-1.2, -1.8), (1.4, -1.6)]]
    return make("Dancing Skeleton", [head, pelvis] + sockets + spine + ribs + arms + hands + legs + feet + joints)


@design("hw_mummy", T)
def mummy(rng):
    head = chain(arc(0, 1.6, 1.0, 0, math.pi, 40), [(-1.0, 0.8)])
    body = chain([(-1.0, 0.8), (-1.3, -2.6), (1.3, -2.6), (1.0, 0.8), (1.0, 1.6)])
    wraps = [quad((-1.0, y), (0, y + 0.25 * (1 if k % 2 else -1)), (1.0 + 0.03 * k, y - 0.15)) for k, y in enumerate([2.2, 1.7, 0.3, -0.3, -0.9, -1.5, -2.1])]
    eyes_slot = rect(-0.75, 1.05, 0.75, 1.45)
    eyes_ = [circle(-0.35, 1.25, 0.15, 14), circle(0.35, 1.25, 0.15, 14)]
    arms = [tube([(1.0, 0.2), (2.0, 0.4), (2.8, 0.4)], 0.5), tube([(-1.0, 0.2), (-2.0, 0.4), (-2.8, 0.4)], 0.5)]
    loose = [cubic((1.3, -2.0), (1.8, -2.2), (2.0, -1.6), (2.6, -2.0), 16)]
    return make("Wandering Mummy", [head, body, eyes_slot] + wraps + eyes_ + arms + loose)


@design("hw_frankenstein", T)
def frankenstein(rng):
    face = rect(-1.5, -2.0, 1.5, 1.6)
    hair = zigzag(-1.5, 1.5, 1.85, 0.25, 7)
    hair_box = [[(-1.5, 1.6), (-1.5, 2.1)], [(1.5, 1.6), (1.5, 2.1)]]
    brow = [[(-1.5, 0.9), (1.5, 0.9)]]
    eyes_ = [rect(-1.0, 0.2, -0.3, 0.6), rect(0.3, 0.2, 1.0, 0.6)]
    nose = poly((-0.15, 0.1), (-0.3, -0.5), (0.3, -0.5), (0.15, 0.1), closed=False)
    mouth = [[(-0.9, -1.2), (0.9, -1.2)]] + [[(x, -1.35), (x, -1.05)] for x in (-0.6, -0.2, 0.2, 0.6)]
    scar = [[(-1.3, 1.3), (-0.4, 1.3)]] + [[(x, 1.15), (x, 1.45)] for x in (-1.1, -0.85, -0.6)]
    bolts = [rect(-2.1, -1.2, -1.5, -0.8), rect(1.5, -1.2, 2.1, -0.8)]
    neck = [[(-1.0, -2.0), (-1.1, -2.8)], [(1.0, -2.0), (1.1, -2.8)]]
    return make("Frankenstein's Monster", [face, hair, nose] + hair_box + brow + eyes_ + mouth + scar + bolts + neck)


@design("hw_vampire", T)
def vampire(rng):
    face = ellipse(0, 0.6, 1.2, 1.5, 100)
    hair = poly((-1.2, 1.0), (-1.1, 2.0), (0, 1.6), (1.1, 2.0), (1.2, 1.0), closed=False)
    peak = poly((-0.6, 1.85), (0, 1.0), (0.6, 1.85), closed=False)
    eyes_ = [ellipse(-0.45, 0.7, 0.25, 0.15, 16), ellipse(0.45, 0.7, 0.25, 0.15, 16)]
    brows = [[(-0.8, 1.05), (-0.2, 0.9)], [(0.8, 1.05), (0.2, 0.9)]]
    mouth = quad((-0.5, -0.2), (0, -0.4), (0.5, -0.2))
    fangs = [poly((-0.3, -0.3), (-0.22, -0.6), (-0.12, -0.36), closed=False), poly((0.12, -0.36), (0.22, -0.6), (0.3, -0.3), closed=False)]
    collar = [poly((-0.8, -0.7), (-2.8, 1.4), (-2.4, -2.6), (-0.4, -2.6), closed=False), poly((0.8, -0.7), (2.8, 1.4), (2.4, -2.6), (0.4, -2.6), closed=False)]
    shirt = poly((-0.4, -2.6), (0, -1.0), (0.4, -2.6), closed=False)
    bow = [poly((0, -1.3), (-0.4, -1.1), (-0.4, -1.5)), poly((0, -1.3), (0.4, -1.1), (0.4, -1.5))]
    return make("Count Vampire", [face, hair, peak, mouth, shirt] + eyes_ + brows + fangs + collar + bow)


@design("hw_howling_werewolf", T)
def howling_werewolf(rng):
    moon = circle(1.8, 0.6, 1.2, 100)
    head = poly((-2.4, -2.8), (-2.2, -1.2), (-1.9, 0.0), (-1.7, 0.7), (-1.9, 1.6), (-1.3, 1.05), (-0.9, 1.3), (-0.3, 1.9), (0.3, 2.6),
                (0.5, 2.35), (-0.25, 1.55), (0.4, 1.8), (0.35, 1.55), (-0.4, 1.0), (-0.6, 0.4), (-0.35, 0.1), (-0.7, -0.2), (-0.45, -0.6),
                (-0.6, -1.0), (-0.3, -2.8), closed=False)
    ear_in = poly((-1.75, 1.3), (-1.55, 1.0), closed=False)
    fur = [poly((-2.1, -0.8), (-1.6, -1.0), (-2.0, -1.3), (-1.5, -1.6), closed=False)]
    ground = poly((-3.0, -2.8), (-1.0, -2.8), (0.4, -2.2), (1.6, -2.4), (3.0, -2.0), closed=False)
    stars_ = [star(x, y, r) for x, y, r in [(2.6, 2.6, 0.25), (-2.6, 2.4, 0.2), (0.8, -1.2, 0.2)]]
    return make("Howling Werewolf", [moon, head, ear_in, ground] + fur + stars_, [eye(-0.9, 1.15, 0.08)])


@design("hw_pumpkin_patch", T)
def pumpkin_patch(rng):
    p = pumpkin(-1.6, -1.2, 1.0) + pumpkin(1.3, -1.5, 0.75) + pumpkin(0.2, 0.9, 0.6)
    vines = [spiral(-2.6, 0.6, 0.05, 0.4, 1.5), spiral(2.6, 0.2, 0.05, 0.35, 1.5)]
    leaves = [lens((-2.4, -0.1), (-3.0, 0.4), 0.5), lens((2.2, -0.6), (2.9, -0.4), 0.5)]
    ground = [wave(-3.0, 3.0, -2.6, 0.08, 6)]
    return make("Pumpkin Patch", p + vines + leaves + ground)


@design("hw_scared_pumpkin", T)
def scared_pumpkin(rng):
    p = pumpkin(0, -0.4, 2.0, "scared")
    sweat = [poly((1.9, 0.9), (1.75, 0.5), (2.05, 0.5), (1.9, 0.9), closed=False)]
    lines = [[(-2.8, 1.0), (-2.3, 0.7)], [(-2.9, 0.3), (-2.4, 0.2)], [(2.8, -0.2), (2.4, -0.1)]]
    ghost_ = chain(arc(1.9, 2.0, 0.7, 0, math.pi, 30), [(1.2, 1.2), (1.45, 1.4), (1.7, 1.2), (1.95, 1.4), (2.2, 1.2), (2.45, 1.4), (2.6, 1.2), (2.6, 2.0)])
    return make("Scared Little Pumpkin", p + sweat + lines + [ghost_], [eye(1.65, 2.1, 0.08), eye(2.15, 2.1, 0.08)])


@design("hw_spider_web", T)
def spider_web(rng):
    cx, cy = -0.4, 0.4
    spokes = [[(cx, cy), (cx + 3.0 * math.cos(a), cy + 3.0 * math.sin(a))] for a in [k * math.pi / 5 for k in range(10)]]
    rings = []
    for r in (0.6, 1.2, 1.8, 2.4):
        pts = []
        for k in range(10):
            a0, a1 = k * math.pi / 5, (k + 1) * math.pi / 5
            p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0))
            p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
            mid = (cx + 0.85 * r * math.cos((a0 + a1) / 2), cy + 0.85 * r * math.sin((a0 + a1) / 2))
            pts += quad(p0, mid, p1, 8)[:-1]
        rings.append(pts + [pts[0]])
    spider = [circle(1.8, -1.9, 0.35, 20), circle(1.8, -1.4, 0.2, 14), [(1.8, -1.2), (cx + 1.8 * math.cos(-0.97), cy + 1.8 * math.sin(-0.97))]]
    legs = [[(1.8 + s * 0.3, -1.9 + dy), (1.8 + s * 0.7, -1.7 + dy), (1.8 + s * 0.9, -2.1 + dy)] for s in (-1, 1) for dy in (0.15, -0.15)]
    return make("Spider Web", spokes + rings + spider + legs)


@design("hw_spooky_owl", T)
def spooky_owl(rng):
    moon = circle(1.6, 1.8, 1.1, 80)
    body = ellipse(-0.4, 0.0, 1.3, 1.8, 100)
    ears = [poly((-1.4, 1.2), (-1.5, 2.2), (-0.9, 1.6), closed=False), poly((0.6, 1.2), (0.7, 2.2), (0.1, 1.6), closed=False)]
    eyes_ = [circle(-0.9, 0.7, 0.42, 30), circle(0.1, 0.7, 0.42, 30)]
    beak = poly((-0.6, 0.4), (-0.4, -0.1), (-0.2, 0.4))
    belly = [quad((-1.1, y), (-0.4, y - 0.3), (0.3, y)) for y in (-0.4, -0.9, -1.4)]
    branch = [[(-3.0, -1.8), (3.0, -1.6)], [(1.5, -1.65), (2.4, -1.0)]]
    feet = [[(x, -1.75), (x, -1.6)] for x in (-0.9, -0.7, 0.0, 0.2)]
    return make("Owl in the Moonlight", [moon, body, beak] + ears + eyes_ + belly + branch + feet, [eye(-0.9, 0.7, 0.15), eye(0.1, 0.7, 0.15)])


@design("hw_scarecrow_halloween", T)
def scarecrow_halloween(rng):
    post = [[(0, -3.0), (0, 0.6)], [(-2.8, 0.6), (2.8, 0.6)]]
    head = circle(0, 1.5, 0.75, 50)
    hat = [poly((-1.4, 2.0), (1.4, 2.0), (0.6, 2.2), (0.3, 3.0), (-0.5, 2.9), (-0.6, 2.2), (-1.4, 2.0), closed=False)]
    face = [poly((-0.45, 1.6), (-0.15, 1.6), (-0.3, 1.9)), poly((0.15, 1.6), (0.45, 1.6), (0.3, 1.9)), zigzag(-0.4, 0.4, 1.1, 0.06, 4)]
    shirt = poly((-2.4, 0.9), (2.4, 0.9), (2.4, 0.3), (1.0, 0.2), (1.1, -1.6), (-1.1, -1.6), (-1.0, 0.2), (-2.4, 0.3))
    straw = [poly((x, 0.3), (x + 0.2 * s, 0.0), (x + 0.15 * s, 0.3), closed=False) for x, s in [(-2.4, -1), (2.4, 1)]]
    patch = rect(-0.6, -0.9, -0.1, -0.4)
    crow = [ellipse(2.0, 1.2, 0.4, 0.25, 20), circle(2.35, 1.4, 0.15, 12), poly((2.48, 1.45), (2.7, 1.38), (2.48, 1.32), closed=False)]
    return make("Spooky Scarecrow", post + [head, shirt, patch] + hat + face + straw + crow)


@design("hw_treat_bucket", T)
def treat_bucket(rng):
    p = pumpkin(0, -0.8, 1.8, "happy")
    handle = arc(0, -0.2, 2.2, math.radians(15), math.radians(165), 50)
    candy = [rrect(-1.2, 0.9, -0.4, 1.4, 0.2), poly((-1.2, 1.15), (-1.5, 1.4), (-1.5, 0.9)), poly((-0.4, 1.15), (-0.1, 1.4), (-0.1, 0.9)),
             circle(0.6, 1.4, 0.35, 20), [(0.6, 1.05), (0.6, 0.85)]]
    return make("Trick-or-Treat Bucket", p + [handle] + candy)


@design("hw_wrapped_candies", T)
def wrapped_candies(rng):
    def wrapper(cx, cy, s, rot):
        parts = [ellipse(0, 0, 0.8, 0.5, 40), poly((-0.75, 0.15), (-1.4, 0.5), (-1.4, -0.5), (-0.75, -0.15)),
                 poly((0.75, 0.15), (1.4, 0.5), (1.4, -0.5), (0.75, -0.15)), [(-0.3, 0.45), (0.1, -0.48)], [(0.2, 0.47), (0.55, -0.35)]]
        return [transform(p, dx=cx, dy=cy, s=s, rot=rot) for p in parts]
    pop = [circle(1.6, 1.6, 0.8, 60), spiral(1.6, 1.6, 0.05, 0.7, 2.5), [(1.6, 0.8), (1.1, -0.8)]]
    return make("Halloween Candy", wrapper(-1.4, 1.2, 1.2, 0.3) + wrapper(-0.6, -1.6, 1.0, -0.2) + wrapper(1.8, -1.8, 0.8, 0.6) + pop)


@design("hw_potion_bottles", T)
def potion_bottles(rng):
    def bottle(cx, w, h, neck):
        body = chain([(cx - 0.25, -2.6 + h + neck)], [(cx - 0.25, -2.6 + h)], arc(cx, -2.6 + h / 2, w, math.radians(110), math.radians(430), 60),
                     [(cx + 0.25, -2.6 + h)], [(cx + 0.25, -2.6 + h + neck)])
        cork = rect(cx - 0.3, -2.6 + h + neck, cx + 0.3, -2.6 + h + neck + 0.4)
        liquid = wave(cx - w * 0.9, cx + w * 0.9, -2.6 + h / 2, 0.08, 2, 30)
        return [body, cork, liquid]
    b = bottle(-1.8, 0.9, 1.8, 0.7) + bottle(0.3, 1.1, 2.2, 1.0) + bottle(2.2, 0.7, 1.4, 0.5)
    bubbles = [circle(x, y, r, 14) for x, y, r in [(0.2, 1.7, 0.18), (0.5, 2.2, 0.13), (0.1, 2.6, 0.1)]]
    labels = [heart(0.3, -1.7, 0.35), star(-1.8, -1.8, 0.3)]
    shelf = [[(-3.0, -2.7), (3.0, -2.7)]]
    return make("Potion Bottles", b + bubbles + labels + shelf)


@design("hw_spell_book", T)
def spell_book(rng):
    cover = poly((-2.8, -1.8), (0, -1.4), (2.8, -1.8), (2.8, 1.6), (0, 2.0), (-2.8, 1.6))
    spine = [[(0, -1.4), (0, 2.0)]]
    pages = [quad((-2.4, y), (-1.2, y + 0.15), (-0.4, y + 0.1)) for y in (1.0, 0.6, 0.2)] + [quad((0.4, y + 0.1), (1.2, y + 0.15), (2.4, y)) for y in (-0.4, -0.8, -1.2)]
    pent = star(-1.4, -0.7, 0.6)
    pent_ring = circle(-1.4, -0.75, 0.62, 40)
    moon_ = chain(arc(1.4, 1.1, 0.5, math.radians(60), math.radians(300), 20), arc(1.6, 1.1, 0.38, math.radians(270), math.radians(90), 16)[::-1])
    sparkle = [star(x, y, 0.22, 4, 0.3) for x, y in [(-2.4, 2.6), (0.6, 2.8), (2.4, 2.6)]]
    return make("Witch's Spell Book", [cover, pent, pent_ring, moon_] + spine + pages + sparkle)


@design("hw_crystal_ball", T)
def crystal_ball(rng):
    ball = circle(0, 0.6, 2.0, 140)
    shine = arc(0, 0.6, 1.6, math.radians(110), math.radians(160), 14)
    base = poly((-1.4, -1.25), (1.4, -1.25), (1.9, -2.2), (-1.9, -2.2))
    feet = [[(-2.2, -2.6), (2.2, -2.6)], [(-1.9, -2.2), (-2.2, -2.6)], [(1.9, -2.2), (2.2, -2.6)]]
    ghost_ = chain(arc(0.3, 0.9, 0.6, 0, math.pi, 24), [(-0.3, 0.1), (-0.1, 0.25), (0.1, 0.1), (0.3, 0.25), (0.5, 0.1), (0.9, 0.2), (0.9, 0.9)])
    stars_ = [star(-0.9, 1.6, 0.22), star(1.1, 1.8, 0.18)]
    hands = [cubic((-2.9, -1.0), (-2.4, -0.4), (-2.0, -0.6), (-1.8, -0.2), 14), cubic((2.9, -1.0), (2.4, -0.4), (2.0, -0.6), (1.8, -0.2), 14)]
    return make("Fortune Teller's Crystal Ball", [ball, shine, base, ghost_] + feet + stars_ + hands, [eye(0.1, 1.0, 0.07), eye(0.5, 1.0, 0.07)])


@design("hw_coffin", T)
def coffin(rng):
    box = poly((-0.9, 2.8), (0.9, 2.8), (1.6, 1.4), (1.0, -2.8), (-1.0, -2.8), (-1.6, 1.4))
    inner = poly((-0.6, 2.4), (0.6, 2.4), (1.15, 1.35), (0.7, -2.4), (-0.7, -2.4), (-1.15, 1.35))
    cross = [[(0, 1.6), (0, -0.6)], [(-0.6, 0.9), (0.6, 0.9)]]
    bat = [mini_bat(2.4, 2.2, 0.5), mini_bat(-2.3, 1.0, 0.4)]
    cobweb = [quad((-3.0, -1.6), (-2.2, -2.0), (-2.0, -2.8)), [(-3.0, -2.8), (-2.3, -2.1)]]
    return make("Vampire's Coffin", [box, inner] + cross + bat + cobweb)


@design("hw_cemetery_gate", T)
def cemetery_gate(rng):
    posts = [rect(-2.8, -2.6, -2.2, 1.6), rect(2.2, -2.6, 2.8, 1.6)]
    caps = [circle(-2.5, 1.9, 0.3, 20), circle(2.5, 1.9, 0.3, 20)]
    arch = arc(0, 0.6, 2.2, 0, math.pi, 60)
    bars = [[(x, -2.6), (x, 0.6 + math.sqrt(max(0.0, 2.2 ** 2 - x * x)))] for x in (-1.6, -0.8, 0, 0.8, 1.6)]
    rails = [[(-2.2, -1.8), (2.2, -1.8)], [(-2.2, 0.2), (2.2, 0.2)]]
    tips = [poly((x - 0.15, 0.6 + math.sqrt(max(0.0, 2.2 ** 2 - x * x))), (x, 0.95 + math.sqrt(max(0.0, 2.2 ** 2 - x * x))),
                 (x + 0.15, 0.6 + math.sqrt(max(0.0, 2.2 ** 2 - x * x))), closed=False) for x in (-1.6, -0.8, 0, 0.8, 1.6)]
    moon_ = arc(1.6, 3.0, 0.45, math.radians(100), math.radians(330), 16)
    return make("Cemetery Gate", posts + caps + [arch, moon_] + bars + rails + tips)


@design("hw_cat_on_pumpkin", T)
def cat_on_pumpkin(rng):
    p = pumpkin(0, -1.6, 1.2, "happy")
    body = chain([(-0.7, -0.4)], cubic((-0.9, 0.4), (-0.7, 1.2), (-0.3, 1.4), (0, 1.4), 20), cubic((0, 1.4), (0.3, 1.4), (0.9, 1.2), (0.7, -0.4), 20))
    head = circle(0, 1.9, 0.6, 40)
    ears = [poly((-0.5, 2.2), (-0.5, 2.85), (-0.1, 2.45), closed=False), poly((0.1, 2.45), (0.5, 2.85), (0.5, 2.2), closed=False)]
    tail = cubic((0.7, -0.3), (1.8, -0.2), (2.0, 1.0), (1.6, 1.6), 24)
    whiskers = [[(-0.25, 1.75), (-0.9, 1.85)], [(-0.25, 1.65), (-0.9, 1.55)], [(0.25, 1.75), (0.9, 1.85)], [(0.25, 1.65), (0.9, 1.55)]]
    return make("Black Cat on a Pumpkin", p + [body, head, tail] + ears + whiskers, [eye(-0.2, 2.0, 0.08), eye(0.2, 2.0, 0.08)])


@design("hw_witch_boots", T)
def witch_boots(rng):
    def boot(dx):
        shape = poly((dx - 0.5, 2.2), (dx + 0.5, 2.2), (dx + 0.45, -1.4), (dx + 1.6, -1.8), (dx + 2.0, -1.4), (dx + 1.9, -2.2),
                     (dx - 0.6, -2.2), (dx - 0.5, -1.5))
        heel = rect(dx - 0.6, -2.6, dx - 0.2, -2.2)
        laces = [[(dx - 0.45, y), (dx + 0.45, y + 0.25)] for y in (1.4, 0.8, 0.2, -0.4)]
        cuff = [[(dx - 0.5, 1.8), (dx + 0.5, 1.8)]]
        return [shape, heel] + laces + cuff
    stripes = [star(2.6, 2.4, 0.3)]
    return make("Witch's Boots", boot(-2.0) + boot(0.6) + stripes)


@design("hw_haunted_tree", T)
def haunted_tree(rng):
    trunk = poly((-0.9, -2.8), (-0.6, -0.6), (-0.8, 0.8), (-2.4, 2.0), (-2.6, 2.8), (-2.1, 2.2), (-0.7, 1.4), (-0.2, 2.6), (0.1, 2.9),
                 (0.2, 2.4), (0.0, 1.5), (0.6, 1.2), (2.2, 2.4), (2.6, 2.3), (1.0, 0.8), (0.7, -0.6), (1.1, -2.8), closed=False)
    roots = [[(-0.9, -2.8), (-1.8, -3.0)], [(1.1, -2.8), (2.0, -3.0)]]
    face = [ellipse(-0.25, 0.0, 0.2, 0.3, 16), ellipse(0.35, 0.05, 0.2, 0.3, 16), ellipse(0.05, -1.0, 0.3, 0.45, 20)]
    twigs = [[(-2.1, 2.2), (-2.8, 2.0)], [(2.0, 2.2), (2.2, 2.9)], [(0.1, 2.9), (-0.4, 3.0)]]
    swing = [[(1.6, 1.85), (1.6, 0.0)], [(2.4, 2.25), (2.4, 0.0)], rect(1.4, -0.2, 2.6, 0.0)]
    return make("Haunted Tree", [trunk] + roots + face + twigs + swing)


@design("hw_ghost_parade", T)
def ghost_parade(rng):
    def g(cx, cy, s):
        body = chain(arc(cx, cy + 0.6 * s, 0.7 * s, 0, math.pi, 30),
                     [(cx - 0.7 * s + 0.35 * s * i, cy - 0.9 * s + (0.25 * s if i % 2 else 0.0)) for i in range(5)], [(cx + 0.7 * s, cy + 0.6 * s)])
        return [body, ellipse(cx, cy + 0.1 * s, 0.15 * s, 0.2 * s, 14)]
    hints = [eye(cx + d * s, cy + 0.7 * s, 0.08) for cx, cy, s in [(-2.0, -1.0, 1.1), (0.2, 0.2, 1.4), (2.2, -1.2, 0.9)] for d in (-0.25, 0.25)]
    return make("Ghost Parade", g(-2.0, -1.0, 1.1) + g(0.2, 0.2, 1.4) + g(2.2, -1.2, 0.9) + [wave(-3.0, 3.0, -2.6, 0.1, 4), star(-2.4, 2.4, 0.3)], hints)


@design("hw_bat_swarm", T)
def bat_swarm(rng):
    moon = circle(0, 0, 1.6, 120)
    bats = [mini_bat(x, y, s) for x, y, s in [(-2.2, 2.2, 0.7), (1.6, 2.4, 0.55), (2.4, 0.6, 0.6), (-2.4, -0.4, 0.5), (0.4, 0.4, 0.6),
                                                (-1.0, -2.2, 0.55), (1.8, -2.0, 0.7), (-0.4, 2.6, 0.4)]]
    return make("Swarm of Bats", [moon] + bats)


@design("hw_candelabra", T)
def candelabra(rng):
    base = poly((-1.0, -2.8), (1.0, -2.8), (0.3, -2.2), (0.2, -0.6), (-0.2, -0.6), (-0.3, -2.2))
    arms = [arc(0, -0.2, 1.6, math.pi, 2 * math.pi, 40), [(0, -0.6), (0, 0.4)]]
    cups = [rect(x - 0.3, y, x + 0.3, y + 0.2) for x, y in [(-1.6, -0.2), (0, 0.4), (1.6, -0.2)]]
    candles = [rect(x - 0.2, y + 0.2, x + 0.2, y + 1.6) for x, y in [(-1.6, -0.2), (0, 0.4), (1.6, -0.2)]]
    flames = [lens((x, y + 1.75), (x, y + 2.5), 0.45) for x, y in [(-1.6, -0.2), (0, 0.4), (1.6, -0.2)]]
    drips = [quad((x - 0.2, y + 1.3), (x - 0.25, y + 0.9), (x - 0.1, y + 1.25)) for x, y in [(-1.6, -0.2), (1.6, -0.2)]]
    return make("Spooky Candelabra", [base] + arms + cups + candles + flames + drips)


@design("hw_old_lantern", T)
def old_lantern(rng):
    ring = circle(0, 2.6, 0.35, 24)
    top = poly((-1.3, 1.2), (0, 2.2), (1.3, 1.2))
    frame = rect(-1.1, -1.6, 1.1, 1.2)
    glass = [[(0, -1.6), (0, 1.2)], [(-1.1, -0.2), (1.1, -0.2)]]
    base = poly((-1.4, -1.6), (1.4, -1.6), (1.1, -2.2), (-1.1, -2.2))
    flame = lens((0.55, -0.1), (0.55, 0.9), 0.5)
    candle = rect(0.35, -1.2, 0.75, -0.2)
    moths = [lens((x - 0.2, y), (x + 0.2, y), 0.6) for x, y in [(-2.2, 1.0), (2.2, 0.0), (-2.0, -1.0)]]
    return make("Old Lantern", [ring, top, frame, base, flame, candle] + glass + moths)


@design("hw_raven_tombstone", T)
def raven_tombstone(rng):
    stone = chain([(-1.6, -2.8), (-1.6, -0.2)], arc(0, -0.2, 1.6, math.pi, 0, 40), [(1.6, -2.8)])
    rip = [[(-0.6, -0.8), (0.6, -0.8)], [(-0.8, -1.4), (0.8, -1.4)], [(-0.5, -2.0), (0.5, -2.0)]]
    raven = poly((-0.6, 1.4), (-0.3, 2.3), (0.2, 2.6), (0.5, 2.5), (0.9, 2.55), (0.55, 2.3), (0.6, 1.9), (0.3, 1.4), (-0.2, 1.2), closed=True)
    tail = poly((-0.6, 1.4), (-1.4, 1.1), (-0.3, 1.25), closed=False)
    feet = [[(0.0, 1.25), (0.0, 1.4)], [(0.25, 1.4), (0.25, 1.4)]]
    wing = quad((-0.3, 2.0), (0.1, 1.8), (0.3, 1.5))
    grass = [zigzag(-3.0, 3.0, -2.8, 0.15, 16)]
    return make("Raven on a Gravestone", [stone, raven, tail, wing] + rip + feet[:1] + grass, [eye(0.4, 2.35, 0.06)])


@design("hw_zombie_hand", T)
def zombie_hand(rng):
    arm = poly((-0.8, -2.0), (-0.7, 0.2), (-1.4, 0.8), (-1.6, 1.8), (-1.3, 1.85), (-1.1, 1.2), (-0.9, 2.6), (-0.6, 2.6), (-0.55, 1.4),
               (-0.3, 2.9), (0.0, 2.85), (0.0, 1.4), (0.3, 2.6), (0.6, 2.5), (0.35, 1.2), (0.7, 1.9), (1.0, 1.8), (0.6, 0.6), (0.6, -2.0), closed=False)
    sleeve = [zigzag(-0.85, 0.65, -0.8, 0.15, 4)]
    ground = [poly((-3.0, -2.0), (-1.4, -2.0), (-1.0, -1.6), (-0.4, -1.8), (0.4, -1.7), (1.0, -1.6), (1.4, -2.0), (3.0, -2.0), closed=False)]
    clods = [circle(x, y, r, 14) for x, y, r in [(-1.8, -1.6, 0.18), (1.6, -1.5, 0.22), (2.2, -1.7, 0.12)]]
    worm = [wave(1.8, 2.8, -2.5, 0.12, 2, 24)]
    return make("Zombie Hand Rising", [arm] + sleeve + ground + clods + worm)


@design("hw_eyeball_jar", T)
def eyeball_jar(rng):
    jar = chain([(-1.6, 1.6)], [(-1.8, 1.2), (-1.8, -2.4)], arc(-1.3, -2.4, 0.5, math.pi, 1.5 * math.pi, 8), [(1.3, -2.9)],
                arc(1.3, -2.4, 0.5, 1.5 * math.pi, 2 * math.pi, 8), [(1.8, 1.2), (1.6, 1.6)])
    lid = rrect(-1.8, 1.6, 1.8, 2.4, 0.2)
    eyes_ = [circle(x, y, 0.55, 30) for x, y in [(-0.8, -1.8), (0.6, -1.6), (-0.1, -0.6), (0.9, 0.3), (-0.9, 0.4)]]
    irises = [circle(x + 0.1, y, 0.22, 14) for x, y in [(-0.8, -1.8), (0.6, -1.6), (-0.1, -0.6), (0.9, 0.3), (-0.9, 0.4)]]
    label = [rect(-1.2, 0.95, 1.2, 1.35)]
    return make("Jar of Eyeballs", [jar, lid] + eyes_ + irises + label,
                [eye(x + 0.12, y, 0.08) for x, y in [(-0.8, -1.8), (0.6, -1.6), (-0.1, -0.6), (0.9, 0.3), (-0.9, 0.4)]])


@design("hw_monster_cupcake", T)
def monster_cupcake(rng):
    cup = poly((-1.6, -0.4), (1.6, -0.4), (1.2, -2.6), (-1.2, -2.6))
    pleats = [[(x, -0.4), (x * 0.75, -2.6)] for x in (-1.0, -0.4, 0.2, 0.8)]
    frosting = chain([(-1.8, -0.4)], cubic((-2.4, 0.4), (-1.4, 1.0), (-1.0, 0.8), (-1.2, 1.4), 16), cubic((-1.2, 1.4), (-0.6, 2.2), (0.6, 2.2), (1.2, 1.4), 20),
                     cubic((1.2, 1.4), (1.0, 0.8), (2.4, 0.4), (1.8, -0.4), 16), [(-1.8, -0.4)])
    eye_big = circle(0, 1.0, 0.55, 30)
    mouth = quad((-0.7, 0.1), (0, -0.25), (0.7, 0.1))
    fangs = [poly((-0.35, 0.0), (-0.25, -0.3), (-0.15, -0.07), closed=False), poly((0.15, -0.07), (0.25, -0.3), (0.35, 0.0), closed=False)]
    horns = [poly((-0.8, 1.8), (-1.1, 2.7), (-0.5, 2.0), closed=False), poly((0.8, 1.8), (1.1, 2.7), (0.5, 2.0), closed=False)]
    return make("Monster Cupcake", [cup, frosting, eye_big, mouth] + pleats + fangs + horns, [eye(0.1, 1.0, 0.2)])


@design("hw_witch_portrait", T)
def witch_portrait(rng):
    face = chain([(-1.0, 0.8)], cubic((-1.1, -0.4), (-0.6, -1.6), (0.2, -1.8), (0.6, -1.4), 30), cubic((0.6, -1.4), (1.1, -0.9), (1.1, 0.2), (1.0, 0.8), 20))
    nose = poly((0.2, 0.3), (1.2, -0.4), (0.3, -0.5), closed=False)
    wart = circle(0.85, -0.1, 0.1, 10)
    smile = quad((-0.5, -0.9), (0.0, -1.2), (0.4, -0.95))
    brim = ellipse(0, 0.9, 2.8, 0.45, 120)
    hat = poly((-1.2, 1.2), (-0.4, 2.6), (0.6, 3.0), (1.6, 2.4), (0.9, 2.5), (1.2, 1.2), closed=False)
    hair = [poly((-1.0, 0.6), (-1.8, -0.2), (-1.4, -0.4), (-2.0, -1.4), (-1.3, -1.2), (-1.6, -2.2), (-0.8, -1.4), closed=False),
            poly((1.0, 0.6), (1.7, -0.3), (1.3, -0.5), (1.8, -1.4), (1.0, -1.2), closed=False)]
    eyes_ = [ellipse(-0.45, 0.1, 0.22, 0.14, 14), ellipse(0.35, 0.15, 0.2, 0.13, 14)]
    return make("Witch Portrait", [face, nose, wart, smile, brim, hat] + hair + eyes_, [eye(-0.42, 0.1, 0.06), eye(0.38, 0.15, 0.06)])


@design("hw_masquerade_mask", T)
def masquerade_mask(rng):
    half = [(0, 0.2), (-0.6, 0.6), (-1.6, 0.8), (-2.6, 1.4), (-2.8, 0.6), (-2.4, -0.4), (-1.6, -0.9), (-0.8, -0.8), (-0.3, -0.4), (0, -0.5)]
    mask = chain(half, mirror_x(half)[::-1])
    eyes_ = [lens((-1.9, 0.1), (-0.8, 0.0), 0.5), lens((1.9, 0.1), (0.8, 0.0), 0.5)]
    feathers = [lens((-2.6, 1.4), (-2.0 + dx, 3.0), 0.3) for dx in (-0.8, 0.0, 0.6)]
    stick = tube([(2.4, -0.4), (2.9, -2.8)], 0.22)
    gems = [circle(0, 0.6, 0.18, 14), star(0, -0.05, 0.22, 4, 0.4)]
    return make("Masquerade Mask", [mask, stick] + eyes_ + feathers + gems)


@design("hw_toadstools", T)
def toadstools(rng):
    def shroom(cx, cy, s):
        cap = chain([(cx - 1.2 * s, cy)], cubic((cx - 1.2 * s, cy), (cx - 1.2 * s, cy + 1.2 * s), (cx + 1.2 * s, cy + 1.2 * s), (cx + 1.2 * s, cy), 30), [(cx - 1.2 * s, cy)])
        stem = chain([(cx - 0.35 * s, cy)], quad((cx - 0.35 * s, cy), (cx - 0.5 * s, cy - 1.0 * s), (cx - 0.4 * s, cy - 1.8 * s), 10),
                     [(cx + 0.4 * s, cy - 1.8 * s)], quad((cx + 0.4 * s, cy - 1.8 * s), (cx + 0.5 * s, cy - 1.0 * s), (cx + 0.35 * s, cy), 10))
        spots = [circle(cx + dx * s, cy + dy * s, 0.15 * s, 12) for dx, dy in [(-0.6, 0.35), (0.1, 0.65), (0.65, 0.3)]]
        return [cap, stem] + spots
    s = shroom(-0.8, 0.6, 1.5) + shroom(1.8, -0.8, 0.9)
    toad_eyes = [circle(-2.2, -1.9, 0.3, 16), circle(-1.6, -1.9, 0.3, 16)]
    toad = chain(arc(-1.9, -2.6, 0.9, 0, math.pi, 30), [(-1.0, -2.6)])
    return make("Witch's Toadstools", s + toad_eyes + [toad, [(-3.0, -2.6), (3.0, -2.6)]], [eye(-2.2, -1.9, 0.1), eye(-1.6, -1.9, 0.1)])


@design("hw_spooky_castle", T)
def spooky_castle(rng):
    keep = rect(-1.4, -2.6, 1.4, 0.6)
    crenel = poly(*[(x, 0.6 + (0.35 if (i // 2) % 2 else 0)) for i, x in enumerate(sorted([-1.4 + 0.35 * k for k in range(9)] * 2))], closed=False)
    towers = [rect(-2.6, -2.6, -1.4, 1.4), rect(1.4, -2.6, 2.6, 1.4)]
    roofs = [poly((-2.8, 1.4), (-2.0, 2.9), (-1.2, 1.4), closed=False), poly((1.2, 1.4), (2.0, 2.9), (2.8, 1.4), closed=False)]
    gate = chain([(-0.5, -2.6), (-0.5, -1.6)], arc(0, -1.6, 0.5, math.pi, 0, 16), [(0.5, -2.6)])
    windows = [chain([(x - 0.2, y), (x - 0.2, y + 0.4)], arc(x, y + 0.4, 0.2, math.pi, 0, 8), [(x + 0.2, y)], [(x - 0.2, y)])
               for x, y in [(-2.0, 0.0), (2.0, 0.0), (-0.6, -0.4), (0.6, -0.4)]]
    flags = [[(-2.0, 2.9), (-2.0, 3.0)]]
    bats = [mini_bat(0, 2.4, 0.5), mini_bat(-0.8, 1.6, 0.3)]
    return make("Spooky Castle", [keep, crenel, gate] + towers + roofs + windows + bats + flags[:0])


@design("hw_pumpkin_tower", T)
def pumpkin_tower(rng):
    p = pumpkin(0, -2.0, 0.85, "happy") + pumpkin(0, 0.0, 0.7, "scared") + pumpkin(0, 1.8, 0.55, "happy")
    leaves = [lens((0.3, 2.6), (1.2, 2.9), 0.5), spiral(-0.5, 2.7, 0.05, 0.3, 1.2)]
    return make("Stack of Jack-o'-Lanterns", p + leaves)


@design("hw_cute_monster", T)
def cute_monster(rng):
    body = chain([(-1.8, -2.0)], cubic((-2.4, 0.0), (-1.8, 2.6), (0, 2.6), (1.8, 2.6), 40), cubic((1.8, 2.6), (2.4, 0.0), (1.8, -2.0), (1.8, -2.0), 20),
                 [(1.8, -2.0), (1.2, -2.0), (1.0, -2.6), (0.6, -2.0), (-0.6, -2.0), (-1.0, -2.6), (-1.2, -2.0), (-1.8, -2.0)])
    eye_ = circle(0, 1.0, 0.75, 40)
    iris = circle(0.15, 0.95, 0.35, 24)
    mouth = chain([(-1.0, -0.4)], quad((-1.0, -0.4), (0, -1.4), (1.0, -0.4), 20), [(-1.0, -0.4)])
    teeth = [poly((-0.5, -0.4), (-0.35, -0.75), (-0.2, -0.4), closed=False), poly((0.2, -0.4), (0.35, -0.75), (0.5, -0.4), closed=False)]
    antennae = [[(-0.6, 2.35), (-1.0, 3.0)], [(0.6, 2.35), (1.0, 3.0)], circle(-1.05, 3.05, 0.12, 10), circle(1.05, 3.05, 0.12, 10)]
    arms = [quad((-2.0, 0.0), (-2.9, 0.5), (-2.8, 1.4)), quad((2.0, 0.0), (2.9, -0.4), (2.9, -1.2))]
    return make("Cute One-Eyed Monster", [body, eye_, iris, mouth] + teeth + antennae + arms, [eye(0.2, 0.95, 0.15)])


@design("hw_trick_or_treater", T)
def trick_or_treater(rng):
    sheet = chain(arc(-0.6, 1.4, 1.1, 0, math.pi, 40), [(-1.9, -2.2)],
                  [(-1.9 + 0.43 * i, -2.2 + (0.25 if i % 2 else 0.0)) for i in range(1, 7)], [(0.7, -2.2), (0.5, 1.4)])
    holes = [ellipse(-1.0, 1.4, 0.18, 0.26, 14), ellipse(-0.2, 1.4, 0.18, 0.26, 14)]
    arm = quad((0.6, 0.0), (1.2, -0.2), (1.6, -0.6))
    bucket = pumpkin(2.0, -1.4, 0.65, "happy")
    handle = arc(2.0, -1.2, 0.75, math.radians(20), math.radians(160), 16)
    shoes = [ellipse(-1.2, -2.5, 0.35, 0.15, 14), ellipse(0.1, -2.5, 0.35, 0.15, 14)]
    door = rect(-3.0, -2.6, -2.2, 0.8)
    return make("Little Trick-or-Treater", [sheet, arm, handle, door] + holes + bucket + shoes)


@design("hw_grim_reaper", T)
def grim_reaper(rng):
    robe = poly((-0.2, 2.6), (-1.0, 2.2), (-1.2, 1.0), (-1.5, -1.0), (-1.9, -2.8), (1.3, -2.8), (1.0, -1.0), (1.0, 1.0), (0.7, 2.2), closed=True)
    hood = chain(arc(-0.15, 1.3, 0.6, math.radians(-40), math.radians(220), 30))
    sleeve = poly((0.8, 0.6), (1.7, 0.2), (1.8, -0.4), (1.0, -0.2), closed=False)
    scythe = [[(1.9, -2.8), (1.9, 2.8)]]
    blade = chain([(1.9, 2.8)], quad((1.9, 2.8), (0.2, 3.2), (-1.4, 2.0), 20), quad((-1.4, 2.0), (0.2, 2.6), (1.9, 2.4), 20))
    hand = circle(1.9, -0.2, 0.18, 12)
    folds = [[(-0.6, -0.4), (-0.9, -2.6)], [(0.3, -0.6), (0.4, -2.6)]]
    return make("Grim Reaper", [robe, hood, sleeve, blade, hand] + scythe + folds, [eye(-0.35, 1.25, 0.08), eye(0.05, 1.25, 0.08)])


@design("hw_poison_apple", T)
def poison_apple(rng):
    apple = chain([(0, 1.0)], cubic((-0.6, 1.6), (-2.4, 1.4), (-2.4, -0.6), (-1.2, -2.0), 30), cubic((-1.2, -2.0), (-0.6, -2.5), (-0.2, -2.0), (0, -2.0), 10),
                  cubic((0, -2.0), (0.2, -2.0), (0.6, -2.5), (1.2, -2.0), 10), cubic((1.2, -2.0), (2.4, -0.6), (2.4, 1.4), (0, 1.0), 30))
    stem = [[(0, 1.0), (0.2, 1.8)]]
    leaf = lens((0.2, 1.5), (1.2, 1.9), 0.45)
    skull_ = [circle(0, -0.2, 0.6, 30), rect(-0.35, -1.0, 0.35, -0.7), circle(-0.22, -0.2, 0.14, 12), circle(0.22, -0.2, 0.14, 12)]
    drip = [poly((-1.6, -1.2), (-1.7, -1.6), (-1.5, -1.6), (-1.6, -1.2), closed=False)]
    shine = arc(0, -0.4, 1.7, math.radians(120), math.radians(150), 8)
    return make("Poison Apple", [apple, leaf, shine] + stem + skull_ + drip)
