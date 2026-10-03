"""Cats niche, part 2 (pictures 10-50)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
from .cats import _cat_head
import math

T = "cats"


def head(cx, cy, r=0.8):
    return _cat_head(cx, cy, r)


def eyes(cx, cy, r=0.8, closed=False):
    if closed:
        return [], [arc(cx - 0.33 * r, cy + 0.25 * r, 0.18 * r, math.radians(200), math.radians(340), 8),
                    arc(cx + 0.33 * r, cy + 0.25 * r, 0.18 * r, math.radians(200), math.radians(340), 8)]
    return [eye(cx - 0.33 * r, cy + 0.2 * r, 0.12 * r / 0.8), eye(cx + 0.33 * r, cy + 0.2 * r, 0.12 * r / 0.8)], []


def sit_body(cx, cy, s=1.0, tail=1):
    """Sitting body below a head at (cx, cy + 1.3 s)."""
    body = chain(cubic((-0.5, 0.6), (-1.5, -0.2), (-1.6, -2.0), (-0.8, -2.6), 30), [(0.8, -2.6)],
                 cubic((0.8, -2.6), (1.6, -2.0), (1.5, -0.2), (0.5, 0.6), 30))
    legs = [[(-0.3, -0.2), (-0.35, -2.6)], [(0.3, -0.2), (0.35, -2.6)]]
    t = tube(chain(quad((1.2, -2.3), (2.4 * tail, -2.2), (2.2 * tail, -0.9)), quad((2.2 * tail, -0.9), (2.1 * tail, -0.2), (2.6 * tail, 0.1))), 0.28)
    return [transform(p, dx=cx, dy=cy, s=s) for p in [body, t] + legs]


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


@design("cat_walking", T)
def cat_walking(rng):
    body = rrect(-1.8, -0.6, 1.6, 0.6, 0.6)
    legs = [leg(x, x + 0.35, -0.3, -2.0) for x in (-1.5, -0.9, 0.6, 1.2)]
    tail = quad((1.5, 0.4), (2.8, 0.6), (2.6, 2.0))
    h = head(-2.1, 1.2, 0.7)
    e, _ = eyes(-2.1, 1.2, 0.7)
    return make("Walking Cat", [body, tail] + legs + h, e)


@design("cat_window", T)
def cat_window(rng):
    frame = rect(-2.6, -1.6, 2.6, 3.2)
    panes = [[(0, -1.6), (0, 3.2)], [(-2.6, 0.8), (2.6, 0.8)]]
    sill = rect(-3.0, -2.0, 3.0, -1.6)
    curtains = [quad((-2.6, 3.2), (-1.6, 1.0), (-2.6, -1.6)), quad((2.6, 3.2), (1.6, 1.0), (2.6, -1.6))]
    cat = sit_body(0.6, -0.4, 0.45)
    h = head(0.6, 0.55, 0.45)
    e, _ = eyes(0.6, 0.55, 0.45)
    moon = arc(-1.2, 2.2, 0.5, math.radians(60), math.radians(300), 20)
    return make("Cat at the Window", [frame, sill, moon] + panes + curtains + cat + h, e)


@design("cat_teacup", T)
def cat_teacup(rng):
    cup = chain(cubic((-2.0, 0.6), (-2.0, -1.4), (-1.0, -2.0), (0.0, -2.0), 30), cubic((0.0, -2.0), (1.0, -2.0), (2.0, -1.4), (2.0, 0.6), 30))
    rim = ellipse(0, 0.6, 2.0, 0.35, 80)
    handle = arc(2.1, -0.4, 0.6, math.radians(-90), math.radians(90), 16)
    saucer = ellipse(0, -2.1, 2.8, 0.4, 100)
    h = head(0, 1.6, 0.85)
    e, _ = eyes(0, 1.6, 0.85)
    paws = [ellipse(-0.7, 0.75, 0.3, 0.2, 20), ellipse(0.7, 0.75, 0.3, 0.2, 20)]
    return make("Kitten in a Teacup", [cup, rim, handle, saucer] + h + paws, e)


@design("cat_basket", T)
def cat_basket(rng):
    basket = chain([(-2.4, 0.0)], quad((-2.2, -2.2), (0, -2.4), (2.2, -2.2), 30), [(2.4, 0.0), (-2.4, 0.0)])
    weave = [quad((-2.3, -0.6 - 0.55 * k), (0, -0.8 - 0.55 * k), (2.3, -0.6 - 0.55 * k)) for k in range(3)]
    h1, h2 = head(-1.0, 0.8, 0.6), head(1.0, 0.9, 0.65)
    e1, _ = eyes(-1.0, 0.8, 0.6)
    _, c2 = eyes(1.0, 0.9, 0.65, closed=True)
    blanket = wave(-2.4, 2.4, 0.15, 0.12, 5, 60)
    return make("Kittens in a Basket", [basket, blanket] + weave + h1 + h2 + c2, e1)


@design("cat_moon", T)
def cat_moon(rng):
    moon = chain(arc(0, 0, 2.6, math.radians(80), math.radians(280), 90), arc(1.0, 0.0, 2.15, math.radians(240), math.radians(120), 70))
    cat = sit_body(-0.9, -0.2, 0.45)
    h = head(-0.9, 0.75, 0.45)
    stars_ = [star(x, y, 0.25) for x, y in [(1.6, 2.0), (2.6, 0.4), (1.9, -1.8)]]
    return make("Cat on the Moon", [moon] + cat + h + stars_)


@design("cat_with_fish", T)
def cat_with_fish(rng):
    h = head(0, 1.6, 1.0)
    e, _ = eyes(0, 1.6, 1.0)
    fish = chain(quad((-1.4, -0.4), (0.0, 0.3), (1.0, -0.4)), [(1.6, 0.1), (1.6, -0.9), (1.0, -0.4)], quad((1.0, -0.4), (0.0, -1.1), (-1.4, -0.4)))
    paws = [ellipse(-1.0, -0.6, 0.35, 0.3, 20), ellipse(0.4, -0.6, 0.35, 0.3, 20)]
    body = chain(quad((-1.2, 0.8), (-2.0, -1.0), (-1.2, -2.6)), [(1.2, -2.6)], quad((1.2, -2.6), (2.0, -1.0), (1.2, 0.8)))
    return make("Cat with a Fish", h + [fish, body] + paws, e + [eye(-1.0, -0.35, 0.07)])


@design("cat_butterfly", T)
def cat_butterfly(rng):
    cat = sit_body(-0.8, -0.6, 0.7)
    h = head(-0.8, 0.45, 0.7)
    e, _ = eyes(-0.8, 0.45, 0.7)
    bfly = [lens((1.8, 2.2), (2.6, 3.0), 0.5), lens((1.8, 2.2), (2.7, 1.8), 0.5), lens((1.8, 2.2), (1.0, 3.0), 0.5), lens((1.8, 2.2), (0.9, 1.8), 0.5)]
    path = [(1.2 + 0.2 * k, 1.0 + 0.25 * math.sin(k)) for k in range(5)]
    return make("Cat and Butterfly", cat + h + bfly + [path], e)


@design("cat_bow", T)
def cat_bow(rng):
    h = head(0, 0, 2.0)
    e, _ = eyes(0, 0, 2.0)
    bow = [lens((1.1, 2.4), (2.1, 3.1), 0.45), lens((1.1, 2.4), (2.1, 1.7), 0.45), circle(1.1, 2.4, 0.2, 14)]
    return make("Kitty with a Bow", h + bow, e)


@design("cat_glasses", T)
def cat_glasses(rng):
    h = head(0, 0, 2.0)
    glasses = [circle(-0.66, 0.4, 0.55, 40), circle(0.66, 0.4, 0.55, 40), arc(0, 0.4, 0.2, math.radians(30), math.radians(150), 8)]
    book = [poly((-2.4, -2.6), (0, -2.2), (2.4, -2.6), (2.4, -3.2), (0, -2.8), (-2.4, -3.2)), [(0, -2.2), (0, -2.8)]]
    return make("Professor Cat", h + glasses + book, [eye(-0.66, 0.4, 0.15), eye(0.66, 0.4, 0.15)])


@design("cat_crown", T)
def cat_crown(rng):
    h = head(0, -0.2, 1.8)
    e, _ = eyes(0, -0.2, 1.8)
    crown = poly((-1.0, 1.9), (-1.2, 3.2), (-0.5, 2.5), (0, 3.4), (0.5, 2.5), (1.2, 3.2), (1.0, 1.9))
    gems = [circle(0, 2.25, 0.15, 12)]
    return make("King Cat", h + [crown] + gems, e)


@design("cat_heart", T)
def cat_heart(rng):
    big = heart(0, 0.2, 2.6)
    h = head(0, 0.1, 1.1)
    e, _ = eyes(0, 0.1, 1.1)
    small = [heart(x, y, 0.3) for x, y in [(-2.8, 2.4), (2.8, 2.2)]]
    return make("Cat in a Heart", [big] + h + small, e)


@design("cat_loaf", T)
def cat_loaf(rng):
    loaf = chain(quad((-2.4, -1.0), (-2.6, 1.0), (-0.8, 1.2), 20), quad((-0.8, 1.2), (1.6, 1.4), (2.6, 0.2), 20), [(2.4, -1.0), (-2.4, -1.0)])
    h = head(-1.2, 1.2, 0.75)
    _, c = eyes(-1.2, 1.2, 0.75, closed=True)
    tail = quad((2.4, -0.8), (1.0, -1.4), (-0.6, -1.2))
    floor = [(-3.0, -1.0), (3.0, -1.0)]
    return make("Cat Loaf", [loaf, tail, floor] + h + c)


@design("lucky_cat", T)
def lucky_cat(rng):
    cat = sit_body(0, -0.6, 0.85)
    h = head(0, 0.6, 0.85)
    _, c = eyes(0, 0.6, 0.85, closed=True)
    paw = [tube([(0.8, -0.2), (1.6, 1.4)], 0.5), ellipse(1.65, 1.6, 0.35, 0.3, 20)]
    coin = [ellipse(-0.4, -1.4, 0.7, 0.45, 40), ellipse(-0.4, -1.4, 0.45, 0.28, 30)]
    bell = [circle(0, -0.25, 0.2, 14)]
    return make("Lucky Waving Cat", cat + h + c + paw + coin + bell)


@design("cat_back", T)
def cat_back(rng):
    body = chain(cubic((-0.6, 0.8), (-1.8, 0.2), (-1.8, -2.0), (0, -2.4), 40), cubic((0, -2.4), (1.8, -2.0), (1.8, 0.2), (0.6, 0.8), 40))
    headb = chain(arc(0, 1.5, 0.85, math.radians(-40), math.radians(40), 12), [(0.75, 2.5)], arc(0, 1.5, 0.85, math.radians(70), math.radians(110), 8),
                  [(-0.75, 2.5)], arc(0, 1.5, 0.85, math.radians(140), math.radians(220), 12), quad((-0.65, 0.95), (0, 0.7), (0.65, 0.95), 10))
    tail = quad((0, -2.3), (1.6, -2.4), (1.2, -0.6))
    hills = [quad((-3.2, -2.4), (-1.2, -1.6), (0.6, -2.4)), quad((0.6, -2.4), (2.0, -1.8), (3.2, -2.4))]
    sun = arc(2.0, 2.0, 0.7, 0, 2 * math.pi, 30)
    return make("Cat Watching the Sunset", [body, headb, tail, sun] + hills)


@design("two_cats", T)
def two_cats(rng):
    a = sit_body(-1.2, -0.8, 0.6, tail=-1)
    b = sit_body(1.2, -0.8, 0.6)
    ha, hb = head(-1.2, 0.0, 0.6), head(1.2, 0.0, 0.6)
    ea, _ = eyes(-1.2, 0.0, 0.6)
    eb, _ = eyes(1.2, 0.0, 0.6)
    love = heart(0, 1.9, 0.5)
    return make("Cat Couple", a + b + ha + hb + [love], ea + eb)


@design("cat_mouse_chase", T)
def cat_mouse_chase(rng):
    body = rrect(-1.2, -0.4, 1.6, 0.6, 0.5)
    legs = [[(-1.0, -0.2), (-1.8, -1.2)], [(-0.6, -0.4), (-0.4, -1.4)], [(1.2, -0.3), (2.0, -1.2)], [(1.4, 0.0), (1.0, -1.4)]]
    tail = quad((1.5, 0.4), (2.6, 1.6), (3.2, 1.0))
    h = head(-1.6, 0.9, 0.6)
    e, _ = eyes(-1.6, 0.9, 0.6)
    mouse = [chain(quad((-3.4, -1.4), (-3.0, -0.8), (-2.6, -1.4)), [(-3.4, -1.4)]), circle(-3.0, -0.85, 0.15, 12), quad((-2.6, -1.4), (-2.2, -1.2), (-2.0, -1.6))]
    return make("Cat Chasing Mouse", [body, tail] + legs + h + mouse, e)


@design("scratch_post", T)
def scratch_post(rng):
    post = rect(-0.5, -2.4, 0.5, 1.6)
    rope = [[(-0.5, y), (0.5, y + 0.2)] for y in [-2.0 + 0.4 * k for k in range(9)]]
    base = rect(-2.0, -2.8, 2.0, -2.4)
    top = rect(-1.4, 1.6, 1.4, 2.0)
    toy = [[(1.2, 1.6), (1.2, 0.6)], circle(1.2, 0.4, 0.22, 16)]
    cat = [transform(p, dx=0, dy=0) for p in head(0, 2.6, 0.55)]
    return make("Scratching Post", [post, base, top] + rope + toy + cat, [eye(-0.18, 2.7, 0.07), eye(0.18, 2.7, 0.07)])


@design("cat_tree", T)
def cat_tree(rng):
    posts = [rect(-1.8, -2.6, -1.4, 1.0), rect(0.8, -2.6, 1.2, 2.2)]
    shelves = [rect(-2.6, 1.0, -0.6, 1.3), rect(0.0, 2.2, 2.0, 2.5), rect(-0.4, -0.6, 1.8, -0.3)]
    base = rect(-3.0, -2.9, 3.0, -2.6)
    box = [rect(-2.6, -2.6, -0.4, -1.0), circle(-1.5, -1.8, 0.4, 24)]
    cat = [transform(p) for p in head(1.0, 3.1, 0.5)]
    sleeper = [chain(arc(-1.6, 1.3, 0.7, 0, math.pi, 20))]
    return make("Cat Tree", posts + shelves + [base] + box + cat + sleeper, [eye(0.85, 3.2, 0.07), eye(1.15, 3.2, 0.07)])


@design("collar_bell", T)
def collar_bell(rng):
    collar = [ellipse(0, 0.6, 2.6, 1.2, 120), ellipse(0, 0.6, 2.2, 0.9, 100)]
    bell = [circle(0, -1.0, 0.8, 60), [(-0.8, -1.0), (0.8, -1.0)], circle(0, -1.4, 0.12, 10), [(0, -1.5), (0, -1.8)]]
    tag = heart(1.6, -0.6, 0.4)
    studs = [circle(2.4 * math.cos(a), 0.6 + 1.05 * math.sin(a), 0.08, 8) for a in [math.radians(d) for d in (20, 60, 120, 160)]]
    return make("Collar and Bell", collar + bell + [tag] + studs)


@design("cat_milk", T)
def cat_milk(rng):
    cat = sit_body(-0.8, -0.4, 0.6)
    h = head(-0.8, 0.4, 0.6)
    e, _ = eyes(-0.8, 0.4, 0.6)
    saucer = [ellipse(1.6, -2.0, 1.2, 0.3, 50), ellipse(1.6, -1.95, 0.8, 0.18, 40)]
    bottle = [poly((2.2, -1.6), (2.2, 0.4), (2.5, 0.9), (2.5, 1.4), (2.9, 1.4), (2.9, 0.9), (3.2, 0.4), (3.2, -1.6))]
    return make("Cat and Milk", cat + h + saucer + bottle, e)


@design("cat_flowerpot", T)
def cat_flowerpot(rng):
    pot = poly((-1.8, 0.0), (1.8, 0.0), (1.4, -2.6), (-1.4, -2.6))
    rim = rect(-2.0, -0.4, 2.0, 0.2)
    h = head(0, 1.1, 0.85)
    e, _ = eyes(0, 1.1, 0.85)
    leaves = [lens((-1.6, 0.2), (-2.6, 1.6), 0.3), lens((1.6, 0.2), (2.6, 1.8), 0.3), lens((1.4, 0.2), (2.0, 2.4), 0.3)]
    return make("Cat in a Flowerpot", [pot, rim] + h + leaves, e)


@design("cat_books", T)
def cat_books(rng):
    books = [rect(-2.4, -2.6, 2.0, -1.8), rect(-2.0, -1.8, 2.4, -1.0), rect(-2.2, -1.0, 1.8, -0.2)]
    spines = [[(-1.8, -2.6), (-1.8, -1.8)], [(1.8, -1.8), (1.8, -1.0)], [(-1.6, -1.0), (-1.6, -0.2)]]
    loaf = chain(quad((-1.6, -0.2), (-1.8, 1.0), (0, 1.1)), quad((0, 1.1), (1.6, 1.0), (1.6, -0.2)))
    h = head(-0.6, 1.2, 0.6)
    _, c = eyes(-0.6, 1.2, 0.6, closed=True)
    tail = quad((1.5, 0.0), (2.4, -0.4), (2.2, -1.6))
    return make("Cat on Books", books + spines + [loaf, tail] + h + c)


@design("cat_umbrella", T)
def cat_umbrella(rng):
    canopy = chain(arc(0.6, 1.6, 2.0, math.radians(5), math.radians(175), 60), *[arc(0.6 - 1.5 + 0.75 * k, 1.75, 0.375, math.pi, 2 * math.pi, 10) for k in range(4)])
    handle = chain([(0.6, 1.6), (0.6, -1.4)], arc(0.3, -1.4, 0.3, 0, -math.pi, 10))
    cat = sit_body(-1.0, -0.8, 0.5)
    h = head(-1.0, -0.15, 0.5)
    e, _ = eyes(-1.0, -0.15, 0.5)
    drops = [lens((x, y), (x, y - 0.4), 0.4) for x, y in [(-2.8, 2.6), (2.8, 2.8), (3.0, 0.4), (-2.9, 0.6)]]
    return make("Cat with Umbrella", [canopy, handle] + cat + h + drops, e)


@design("cat_scarf", T)
def cat_scarf(rng):
    h = head(0, 0.6, 1.6)
    e, _ = eyes(0, 0.6, 1.6)
    scarf = [quad((-1.6, -0.6), (0, -1.4), (1.6, -0.6)), quad((-1.5, -1.0), (0, -1.8), (1.5, -1.0)),
             poly((0.6, -1.5), (0.8, -3.0), (1.4, -3.0), (1.3, -1.3))]
    fringe = [[(0.8 + 0.15 * k, -3.0), (0.8 + 0.15 * k, -3.3)] for k in range(5)]
    flakes = [star(x, y, 0.2, 6, 0.5) for x, y in [(-2.6, 2.4), (2.6, 2.6), (-2.8, -0.6)]]
    return make("Cozy Winter Cat", h + scarf + fringe + flakes, e)


@design("kitten_yarn", T)
def kitten_yarn(rng):
    body = ellipse(-0.6, -0.8, 1.4, 0.8, 70)
    h = head(-1.6, 0.4, 0.7)
    e, _ = eyes(-1.6, 0.4, 0.7)
    paws = [ellipse(0.6, -0.1, 0.3, 0.2, 20, rot=0.6)]
    yarn = [circle(1.6, 0.4, 0.8, 50), arc(1.3, 0.4, 0.7, math.radians(-50), math.radians(60), 16), arc(1.9, 0.5, 0.6, math.radians(120), math.radians(230), 16)]
    strand = cubic((1.4, -0.4), (0.8, -2.0), (2.6, -2.0), (3.2, -1.2), 30)
    tail = quad((0.8, -1.0), (1.6, -1.6), (1.2, -2.2))
    return make("Kitten Playing", [body, strand, tail] + h + paws + yarn, e)


@design("gentleman_cat", T)
def gentleman_cat(rng):
    h = head(0, 0.4, 1.4)
    e, _ = eyes(0, 0.4, 1.4)
    hat = [rect(-0.8, 2.3, 0.8, 3.6), ellipse(0, 2.3, 1.4, 0.25, 40)]
    bowtie = [poly((0, -1.3), (-0.8, -0.9), (-0.8, -1.7)), poly((0, -1.3), (0.8, -0.9), (0.8, -1.7)), circle(0, -1.3, 0.15, 10)]
    monocle = [circle(0.47, 0.68, 0.4, 30), quad((0.85, 0.5), (1.2, -0.4), (1.0, -1.0))]
    return make("Gentleman Cat", h + hat + bowtie + monocle, e)


@design("cat_balloon", T)
def cat_balloon(rng):
    cat = sit_body(0, -1.2, 0.55)
    h = head(0, -0.45, 0.55)
    e, _ = eyes(0, -0.45, 0.55)
    balloon = [ellipse(1.6, 2.2, 0.9, 1.1, 60), poly((1.5, 1.1), (1.6, 0.95), (1.7, 1.1)), quad((1.6, 0.95), (1.0, 0.0), (0.5, -1.0))]
    return make("Cat with a Balloon", cat + h + balloon, e)


@design("cat_cloud", T)
def cat_cloud(rng):
    cloud = chain(arc(-1.8, -0.4, 0.9, math.radians(90), math.radians(270), 20), [(1.8, -1.3)], arc(1.8, -0.4, 0.9, math.radians(-90), math.radians(90), 20),
                  arc(0.6, 0.4, 1.0, math.radians(0), math.radians(160), 20), arc(-0.9, 0.4, 0.9, math.radians(20), math.radians(180), 20))
    loaf = chain(arc(0.0, 0.9, 1.2, 0, math.pi, 30))
    h = head(-0.8, 1.5, 0.55)
    _, c = eyes(-0.8, 1.5, 0.55, closed=True)
    zz = [[(1.2, 2.4), (1.6, 2.4), (1.2, 2.0), (1.6, 2.0)]]
    stars_ = [star(x, y, 0.22) for x, y in [(-2.6, 2.4), (2.6, 1.6)]]
    return make("Cat on a Cloud", [cloud, loaf] + h + c + zz + stars_)


@design("cat_sunbathing", T)
def cat_sunbathing(rng):
    body = ellipse(0.4, -1.2, 2.2, 0.7, 100)
    h = head(-1.9, -0.7, 0.65)
    _, c = eyes(-1.9, -0.7, 0.65, closed=True)
    tail = quad((2.5, -1.2), (3.2, -0.6), (3.0, 0.0))
    sun = [circle(1.8, 2.0, 0.8, 50)] + [[(1.8 + 1.0 * math.cos(a), 2.0 + 1.0 * math.sin(a)), (1.8 + 1.4 * math.cos(a), 2.0 + 1.4 * math.sin(a))] for a in [k * math.pi / 4 for k in range(8)]]
    rug = rect(-3.0, -2.1, 3.2, -1.8)
    return make("Sunbathing Cat", [body, tail, rug] + h + c + sun)


@design("cat_hammock", T)
def cat_hammock(rng):
    hammock = [quad((-3.0, 1.0), (0, -1.6), (3.0, 1.0)), quad((-3.0, 1.0), (0, -0.6), (3.0, 1.0))]
    ropes = [[(-3.0, 1.0), (-3.2, 2.6)], [(3.0, 1.0), (3.2, 2.6)]]
    h = head(-0.6, 0.0, 0.6)
    _, c = eyes(-0.6, 0.0, 0.6, closed=True)
    tail = quad((0.8, -0.6), (1.4, -1.8), (1.0, -2.4))
    paw = ellipse(0.4, -0.3, 0.3, 0.2, 16)
    return make("Cat in a Hammock", hammock + ropes + h + c + [tail, paw])


@design("cat_bag", T)
def cat_bag(rng):
    bag = poly((-1.8, -2.6), (1.8, -2.6), (1.6, 0.6), (-1.6, 0.6))
    folds = [[(-1.6, 0.6), (-1.0, 0.2)], [(1.6, 0.6), (1.0, 0.2)], [(-1.7, -1.0), (-1.2, -1.2)]]
    h = head(0, 1.4, 0.8)
    e, _ = eyes(0, 1.4, 0.8)
    paws = [ellipse(-0.6, 0.65, 0.28, 0.2, 16), ellipse(0.6, 0.65, 0.28, 0.2, 16)]
    return make("Cat in a Paper Bag", [bag] + folds + h + paws, e)


@design("cat_laptop", T)
def cat_laptop(rng):
    screen = poly((-2.2, -0.4), (-2.6, 2.4), (1.2, 2.4), (1.6, -0.4))
    inner = poly((-1.9, 0.0), (-2.2, 2.1), (0.95, 2.1), (1.25, 0.0))
    base = poly((-2.6, -0.4), (2.0, -0.4), (2.6, -1.2), (-3.2, -1.2))
    loaf = chain(arc(0.4, -0.4, 1.2, 0, math.pi, 30))
    h = head(-0.4, 0.4, 0.55)
    _, c = eyes(-0.4, 0.4, 0.55, closed=True)
    tail = quad((1.6, -0.5), (2.6, 0.2), (2.4, 1.0))
    return make("Cat on the Laptop", [screen, inner, base, loaf, tail] + h + c)


@design("cat_plant", T)
def cat_plant(rng):
    pot = poly((0.6, -2.6), (0.8, -1.2), (2.6, -1.2), (2.8, -2.6))
    leaves = [lens((1.7, -1.2), (1.7 + 1.4 * math.cos(a), -1.2 + 2.0 * math.sin(a)), 0.25) for a in [math.radians(d) for d in (40, 70, 100, 130)]]
    cat = sit_body(-1.4, -0.4, 0.55)
    h = head(-1.4, 0.35, 0.55)
    e, _ = eyes(-1.4, 0.35, 0.55)
    return make("Curious Cat and Plant", [pot] + leaves + cat + h, e)


@design("mother_cat", T)
def mother_cat(rng):
    mom = ellipse(0, -0.6, 2.4, 1.0, 110)
    h = head(-2.1, 0.3, 0.8)
    e, _ = eyes(-2.1, 0.3, 0.8)
    kits = []
    for x in (-0.6, 0.6, 1.8):
        kits += head(x, -1.8, 0.45)
    tail = quad((2.3, -0.4), (3.2, 0.4), (3.0, 1.0))
    return make("Mother Cat and Kittens", [mom, tail] + h + kits, e)


@design("feather_wand", T)
def feather_wand(rng):
    stick = [(-2.6, -2.6), (1.0, 1.2)]
    string = quad((1.0, 1.2), (2.4, 1.6), (2.2, 0.2))
    feathers = [lens((2.2, 0.2), (2.2 + 1.2 * math.cos(a), 0.2 + 1.2 * math.sin(a)), 0.3) for a in [math.radians(d) for d in (230, 260, 290)]]
    barbs = [[(2.2 + 0.6 * math.cos(a), 0.2 + 0.6 * math.sin(a)), (2.2 + 0.6 * math.cos(a) + 0.2, 0.2 + 0.6 * math.sin(a))] for a in [math.radians(d) for d in (230, 260, 290)]]
    paw = [ellipse(-1.0, 1.6, 0.5, 0.4, 24)] + [circle(-1.0 + 0.3 * math.cos(a), 1.6 + 0.6 * math.sin(a), 0.14, 10) for a in [math.radians(d) for d in (50, 90, 130)]]
    return make("Feather Toy", [stick, string] + feathers + barbs + paw)


@design("cat_carrier", T)
def cat_carrier(rng):
    box = rrect(-2.6, -2.0, 2.6, 1.2, 0.4)
    door = rrect(-1.6, -1.6, 1.6, 0.8, 0.3)
    bars = [[(x, -1.6), (x, 0.8)] for x in (-1.0, -0.4, 0.2, 0.8)]
    handle = arc(0, 1.2, 1.0, 0, math.pi, 20)
    h = head(0, -0.5, 0.6)
    e, _ = eyes(0, -0.5, 0.6)
    vents = [[(1.9, y), (2.3, y)] for y in (0.4, 0.0, -0.4)]
    return make("Cat Carrier", [box, door, handle] + bars + h + vents, e)


@design("cat_fence", T)
def cat_fence(rng):
    fence = [rect(-3.0, -2.6, 3.0, -1.6)] + [[(x, -2.6), (x, -1.6)] for x in (-2.0, -1.0, 0.0, 1.0, 2.0)]
    cat = sit_body(-0.6, 0.3, 0.6, tail=-1)
    h = head(-0.6, 1.15, 0.6)
    e, _ = eyes(-0.6, 1.15, 0.6)
    stars_ = [star(x, y, 0.25) for x, y in [(1.8, 2.6), (2.6, 1.2), (-2.6, 2.4)]]
    lamp = [[(2.4, -1.6), (2.4, 1.2)], poly((2.0, 1.2), (2.8, 1.2), (2.6, 1.8), (2.2, 1.8))]
    return make("Cat on a Fence", fence + cat + h + stars_ + lamp, e)


@design("cat_portrait", T)
def cat_portrait(rng):
    frame = [ellipse(0, 0.2, 2.4, 3.0, 140), ellipse(0, 0.2, 2.0, 2.6, 120)]
    h = head(0, 0.6, 1.1)
    e, _ = eyes(0, 0.6, 1.1)
    shoulders = quad((-1.6, -1.8), (0, -0.4), (1.6, -1.8))
    ruff = zigzag(-1.0, 1.0, -0.7, 0.15, 5)
    return make("Cat Portrait", frame + h + [shoulders, ruff], e)


@design("cat_pumpkin_patch", T)
def cat_pumpkin_patch(rng):
    pumpkin = [ellipse(1.2, -1.6, 1.4, 1.0, 70), ellipse(1.2, -1.6, 0.5, 1.0, 40), rect(1.1, -0.65, 1.35, -0.2)]
    cat = sit_body(-1.4, -0.4, 0.55)
    h = head(-1.4, 0.35, 0.55)
    e, _ = eyes(-1.4, 0.35, 0.55)
    leaves = [lens((-2.6, -2.6), (-3.2, -1.8), 0.35), lens((2.8, -2.6), (3.3, -1.8), 0.35)]
    return make("Cat and Pumpkin", pumpkin + cat + h + leaves, e)


@design("cat_bathtub", T)
def cat_bathtub(rng):
    tub = chain(quad((-2.8, 0.0), (-2.6, -2.0), (0, -2.0), 20), quad((0, -2.0), (2.6, -2.0), (2.8, 0.0), 20), [(-2.8, 0.0)])
    feet = [circle(-2.0, -2.2, 0.2, 14), circle(2.0, -2.2, 0.2, 14)]
    h = head(0, 0.9, 0.7)
    e, _ = eyes(0, 0.9, 0.7)
    bubbles = [circle(x, y, r, 16) for x, y, r in [(-1.6, 0.4, 0.4), (-1.0, 0.3, 0.3), (1.2, 0.4, 0.4), (1.8, 0.8, 0.3), (-2.2, 1.0, 0.25)]]
    duck = [circle(2.2, 0.15, 0.25, 14), ellipse(2.0, -0.1, 0.4, 0.2, 16)]
    return make("Cat in the Bath", [tub] + feet + h + bubbles + duck, e)


@design("cat_sushi", T)
def cat_sushi(rng):
    h = head(-0.8, 0.8, 0.9)
    e, _ = eyes(-0.8, 0.8, 0.9)
    plate = ellipse(1.2, -1.6, 2.0, 0.45, 80)
    rolls = []
    for x in (0.4, 1.3, 2.2):
        rolls += [ellipse(x, -1.2, 0.4, 0.25, 24), ellipse(x, -1.2, 0.2, 0.12, 12), [(x - 0.4, -1.2), (x - 0.4, -1.5)], [(x + 0.4, -1.2), (x + 0.4, -1.5)]]
    sticks = [[(2.6, 0.6), (0.6, -0.8)], [(2.8, 0.4), (0.8, -1.0)]]
    return make("Cat and Sushi", h + [plate] + rolls + sticks, e)


@design("cat_garden", T)
def cat_garden(rng):
    cat = sit_body(0.6, -0.6, 0.6)
    h = head(0.6, 0.15, 0.6)
    e, _ = eyes(0.6, 0.15, 0.6)
    flowers = []
    for x, y in [(-2.2, -0.8), (-1.2, -1.4), (2.4, -1.0)]:
        flowers += [circle(x, y, 0.15, 10)] + [lens((x, y), (x + 0.5 * math.cos(a), y + 0.5 * math.sin(a)), 0.4) for a in [k * 2 * math.pi / 5 for k in range(5)]] + [[(x, y - 0.15), (x, -2.4)]]
    ground = [(-3.0, -2.4), (3.0, -2.4)]
    return make("Cat in the Garden", cat + h + flowers + [ground], e)


@design("cat_bed", T)
def cat_bed(rng):
    bed = [ellipse(0, -1.0, 2.8, 1.0, 100), ellipse(0, -0.8, 2.2, 0.7, 90)]
    curl = chain(arc(0.2, -0.8, 1.0, math.radians(200), math.radians(520), 60))
    h = head(-0.7, -0.4, 0.55)
    _, c = eyes(-0.7, -0.4, 0.55, closed=True)
    bone = [circle(2.4, 1.2, 0.2, 12)]
    mouse = [chain(quad((1.8, 0.6), (2.2, 1.2), (2.6, 0.6)), [(1.8, 0.6)]), quad((2.6, 0.6), (3.0, 0.8), (3.2, 0.4))]
    return make("Cat in Bed", bed + [curl] + h + c + mouse)


@design("cat_pawprints_trail", T)
def cat_pawprints_trail(rng):
    def paw(x, y, r):
        return [transform(ellipse(0, 0, 0.35, 0.3, 20), dx=x, dy=y, rot=r)] + \
               [transform(circle(dx, 0.45, 0.12, 10), dx=x, dy=y, rot=r) for dx in (-0.3, 0.0, 0.3)]
    out = []
    for k in range(6):
        out += paw(-2.6 + 1.0 * k, -2.0 + 0.8 * k + (0.3 if k % 2 else -0.3), -0.6)
    house = [poly((1.8, 2.4), (2.6, 3.2), (3.4, 2.4)), rect(2.0, 1.4, 3.2, 2.4)]
    return make("Paw Print Trail", out + house)


@design("cat_silhouette_moonlit", T)
def cat_silhouette_moonlit(rng):
    moon = circle(1.4, 1.6, 1.4, 90)
    roof = [poly((-3.2, -1.2), (-0.8, 0.6), (1.6, -1.2), closed=False), [(-3.2, -1.2), (3.2, -1.2)]]
    chimney = rect(0.4, -0.4, 0.8, 0.4)
    cat = sit_body(-0.8, 0.9, 0.4, tail=-1)
    h = head(-0.8, 1.45, 0.4)
    bats = [poly((x - 0.3, y), (x - 0.1, y + 0.12), (x, y), (x + 0.1, y + 0.12), (x + 0.3, y), closed=False) for x, y in [(-2.4, 2.6), (2.8, 3.2)]]
    return make("Rooftop Cat", [moon, chimney] + roof + cat + h + bats)
