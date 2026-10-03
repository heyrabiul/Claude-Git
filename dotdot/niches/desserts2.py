"""Sweet Treats & Desserts niche, part 2 (pictures 9-51)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "desserts"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


def scoop(cx, cy, r, drips=5):
    """Ice-cream scoop: round top with a scalloped bottom edge."""
    top = arc(cx, cy, r, math.radians(-10), math.radians(190), 50)
    x0, x1 = cx - r * math.cos(math.radians(10)), cx + r * math.cos(math.radians(10))
    y = cy - r * math.sin(math.radians(10))
    w = (x1 - x0) / drips
    bottom = []
    for k in range(drips):
        bottom += arc(x0 + w * (k + 0.5), y, w / 2, math.pi, 2 * math.pi, 10)[:-1]
    return chain(top, bottom, [(x1, y)])


def cherry(x, y, r=0.25):
    return [circle(x, y, r, 20), quad((x, y + r), (x + 0.1, y + 0.6), (x + 0.4, y + 0.8))]


def cone(cx, top, w, h):
    """Waffle cone with cross-hatching."""
    out = [poly((cx - w, top), (cx + w, top), (cx, top - h))]
    for t in (0.25, 0.5, 0.75):
        out.append([(cx - w * (1 - t), top - h * t), (cx - w + 2 * w * t, top)])
        out.append([(cx + w * (1 - t), top - h * t), (cx + w - 2 * w * t, top)])
    return out


@design("ds_ice_cream_cone", T)
def ice_cream_cone(rng):
    c = cone(0, -0.2, 1.3, 2.8)
    s = scoop(0, 0.6, 1.5, 6)
    sprinkles = [[(x, y), (x + 0.2 * math.cos(a), y + 0.2 * math.sin(a))] for x, y, a in [(-0.6, 1.2, 0.5), (0.3, 1.6, 2.0), (0.8, 0.8, 1.0), (-0.2, 0.5, 2.6), (0.6, 1.9, 0.2)]]
    return make("Waffle Cone Ice Cream", c + [s] + cherry(0, 2.35, 0.3) + sprinkles)


@design("ds_triple_scoop", T)
def triple_scoop(rng):
    c = cone(0, -1.0, 1.0, 2.0)
    s = [scoop(0, -0.5, 1.15, 5), scoop(-0.15, 0.85, 1.0, 5), scoop(0.1, 2.0, 0.85, 4)]
    chips = [circle(x, y, 0.09, 10) for x, y in [(-0.5, -0.1), (0.4, 0.2), (-0.4, 1.4), (0.3, 1.2), (0.0, 2.4)]]
    return make("Triple Scoop Cone", c + s + chips)


@design("ds_sundae", T)
def sundae(rng):
    glass = chain([(-2.2, 0.0)], quad((-2.2, 0.0), (-1.8, -1.6), (-0.3, -1.7), 20), [(-0.3, -2.4), (-1.3, -2.8), (1.3, -2.8), (0.3, -2.4), (0.3, -1.7)],
                  quad((0.3, -1.7), (1.8, -1.6), (2.2, 0.0), 20), [(-2.2, 0.0)])
    scoops = [scoop(-0.9, 0.5, 0.9, 4), scoop(0.9, 0.5, 0.9, 4), scoop(0, 1.4, 0.9, 4)]
    sauce = [wave(-1.6, 1.6, 0.2, 0.12, 3, 40)]
    wafer = [rect(1.4, 1.2, 1.9, 2.8), [(1.4, 1.8), (1.9, 1.8)], [(1.4, 2.3), (1.9, 2.3)]]
    spoon = [[(-1.6, 1.0), (-2.6, 2.6)], ellipse(-2.7, 2.8, 0.2, 0.3, 14, rot=0.55)]
    return make("Ice Cream Sundae", [glass] + scoops + sauce + cherry(0, 2.4, 0.3) + wafer + spoon)


@design("ds_banana_split", T)
def banana_split(rng):
    boat = chain([(-3.0, -0.4)], quad((-3.0, -0.4), (0, -2.6), (3.0, -0.4), 40), [(-3.0, -0.4)])
    rim = ellipse(0, -0.4, 3.0, 0.35, 120)
    bananas = [quad((-2.9, -0.2), (-2.0, -0.6), (-1.0, -0.3)), quad((1.0, -0.3), (2.0, -0.6), (2.9, -0.2))]
    scoops = [scoop(x, 0.4, 0.75, 4) for x in (-1.5, 0.0, 1.5)]
    cream = [spiral(x, 1.3, 0.05, 0.35, 1.5) for x in (-1.5, 0.0, 1.5)]
    cherries = cherry(-1.5, 1.85, 0.2) + cherry(0, 1.85, 0.2) + cherry(1.5, 1.85, 0.2)
    return make("Banana Split", [boat, rim] + bananas + scoops + cream + cherries)


@design("ds_swirl_cupcake", T)
def swirl_cupcake(rng):
    liner = poly((-1.7, -0.4), (1.7, -0.4), (1.2, -2.8), (-1.2, -2.8))
    pleats = [[(x, -0.4), (x * 0.7, -2.8)] for x in (-1.1, -0.55, 0.0, 0.55, 1.1)]
    tiers = [ellipse(0, -0.1, 1.9, 0.45, 80), ellipse(0, 0.6, 1.5, 0.4, 70), ellipse(0, 1.25, 1.05, 0.35, 60), ellipse(0, 1.8, 0.6, 0.3, 40)]
    tip = poly((-0.3, 2.0), (0.1, 2.5), (0.3, 2.0), closed=False)
    sprinkles = [circle(x, y, 0.08, 8) for x, y in [(-1.2, 0.0), (0.9, 0.3), (-0.5, 0.8), (0.6, 1.3), (-0.2, 1.6)]]
    return make("Swirl Cupcake", [liner, tip] + pleats + tiers + sprinkles + cherry(0.6, 2.4, 0.22))


@design("ds_cherry_pie", T)
def cherry_pie(rng):
    tin = ellipse(0, -0.6, 2.9, 1.3, 140)
    tin_side = chain([(-2.9, -0.6), (-2.6, -1.6)], quad((-2.6, -1.6), (0, -2.6), (2.6, -1.6), 40), [(2.9, -0.6)])
    crust = ellipse(0, -0.5, 2.5, 1.05, 120)
    lattice = []
    for k in range(-2, 3):
        x = 0.9 * k
        h = 1.0 * math.sqrt(max(0.0, 1 - (x / 2.5) ** 2))
        lattice.append([(x - 0.2, -0.5 - h), (x + 0.2, -0.5 + h)])
    for k in (-1, 0, 1):
        y = -0.5 + 0.55 * k
        w = 2.5 * math.sqrt(max(0.0, 1 - ((y + 0.5) / 1.05) ** 2))
        lattice.append([(-w, y), (w, y)])
    steam = [[(x + 0.15 * math.sin(3 * t), 1.0 + t) for t in [i / 15 for i in range(16)]] for x in (-1.0, 0.0, 1.0)]
    berries = [circle(x, y, 0.15, 12) for x, y in [(-1.4, -0.75), (0.45, -0.2), (1.35, -0.75), (-0.45, -1.0)]]
    return make("Cherry Pie", [tin, tin_side, crust] + lattice + steam + berries)


@design("ds_wedding_cake", T)
def wedding_cake(rng):
    tiers = [rect(-2.4, -2.6, 2.4, -1.2), rect(-1.7, -1.2, 1.7, 0.2), rect(-1.0, 0.2, 1.0, 1.4)]
    swags = []
    for (x0, x1, y) in [(-2.4, 2.4, -1.2), (-1.7, 1.7, 0.2), (-1.0, 1.0, 1.4)]:
        n = int(round((x1 - x0) / 0.8))
        w = (x1 - x0) / n
        for k in range(n):
            swags.append(arc(x0 + w * (k + 0.5), y, w / 2, math.pi, 2 * math.pi, 8))
    dots = [circle(x, -2.1, 0.1, 8) for x in (-1.8, -0.9, 0.0, 0.9, 1.8)]
    topper = [heart(0, 2.1, 0.4), [(0, 1.4), (0, 1.75)]]
    plate = [[(-2.9, -2.6), (2.9, -2.6)], ellipse(0, -2.75, 2.9, 0.15, 60)]
    return make("Wedding Cake", tiers + swags + dots + topper + plate)


@design("ds_pancakes", T)
def pancakes(rng):
    plate = ellipse(0, -2.3, 2.9, 0.6, 120)
    stack = []
    for k in range(5):
        y = -1.9 + 0.55 * k
        stack.append(chain(arc(-1.9, y, 0.25, math.pi / 2, 3 * math.pi / 2, 8), [(1.9, y - 0.25)], arc(1.9, y, 0.25, -math.pi / 2, math.pi / 2, 8), [(-1.9, y + 0.25)]))
    butter = rrect(-0.5, 0.75, 0.5, 1.25, 0.1)
    syrup = poly((-1.9, 0.45), (-1.9, -0.4), (-1.6, -0.6), (-1.4, 0.3), (1.2, 0.3), (1.4, -0.9), (1.7, -0.7), (1.8, 0.45), closed=False)
    fork = [[(2.4, -1.6), (2.8, 1.2)]] + [[(2.65 + 0.12 * k, 1.0), (2.75 + 0.12 * k, 1.8)] for k in range(3)]
    return make("Stack of Pancakes", [plate, butter, syrup] + stack + fork)


@design("ds_waffle", T)
def waffle(rng):
    body = rrect(-2.4, -2.0, 2.4, 2.0, 0.5)
    grid = [[(x, -1.75), (x, 1.75)] for x in (-1.6, -0.8, 0.0, 0.8, 1.6)] + [[(-2.15, y), (2.15, y)] for y in (-1.2, -0.4, 0.4, 1.2)]
    strawberries = [heart(-1.2, 2.4, 0.4), heart(1.3, 2.3, 0.35)]
    cream = [spiral(0.2, 2.3, 0.05, 0.5, 2)]
    return make("Belgian Waffle", [body] + grid + strawberries + cream)


@design("ds_croissant", T)
def croissant(rng):
    outer = arc(0, -1.4, 2.8, math.radians(10), math.radians(170), 80)
    inner = arc(0, -1.9, 1.5, math.radians(170), math.radians(10), 50)
    body = chain(outer, [(-2.95, -1.9)], inner, [(2.95, -1.9)], [outer[0]])
    segs = [quad((1.5 * math.cos(a), -1.9 + 1.5 * math.sin(a)), (2.3 * math.cos(a + 0.12), -1.6 + 2.3 * math.sin(a + 0.12)),
                 (2.8 * math.cos(a), -1.4 + 2.8 * math.sin(a)), 14) for a in [math.radians(d) for d in (35, 65, 90, 115, 145)]]
    crumbs = [circle(x, y, 0.1, 8) for x, y in [(-1.0, -2.5), (0.6, -2.6), (1.8, -2.4)]]
    return make("Butter Croissant", [body] + segs + crumbs)

@design("ds_cinnamon_roll", T)
def cinnamon_roll(rng):
    roll = spiral(0, 0.3, 0.1, 2.3, 3.2, 360)
    outer = ellipse(0, -0.2, 2.6, 2.4, 140)
    icing = [quad((-1.6, 1.6), (0, 2.2), (1.6, 1.4)), quad((-1.4, 1.6), (-1.6, 0.9), (-1.3, 0.6)), quad((1.2, 1.5), (1.5, 0.9), (1.2, 0.5))]
    plate = [[(-3.0, -2.75), (3.0, -2.75)]]
    return make("Cinnamon Roll", [roll, outer] + icing + plate)


@design("ds_blueberry_muffin", T)
def blueberry_muffin(rng):
    liner = poly((-1.6, -0.2), (1.6, -0.2), (1.2, -2.6), (-1.2, -2.6))
    pleats = [[(x, -0.2), (x * 0.75, -2.6)] for x in (-1.0, -0.35, 0.35, 1.0)]
    top = chain([(-1.6, -0.2), (-2.1, 0.0)], cubic((-2.1, 0.0), (-2.4, 2.6), (2.4, 2.6), (2.1, 0.0), 50), [(1.6, -0.2)])
    berries = [circle(x, y, 0.2, 14) for x, y in [(-1.2, 0.6), (-0.3, 1.3), (0.7, 1.0), (1.3, 0.3), (0.0, 0.3), (-0.9, 1.6)]]
    crumbs = [circle(x, y, 0.07, 8) for x, y in [(0.5, 1.7), (-0.6, 0.8), (1.0, 1.5)]]
    return make("Blueberry Muffin", [liner, top] + pleats + berries + crumbs)


@design("ds_shortcake", T)
def shortcake(rng):
    layers = [rect(-2.2, y, 2.2, y + 0.9) for y in (-2.2, -0.6)]
    creams = [wave(-2.3, 2.3, -1.0, 0.15, 6), wave(-2.3, 2.3, 0.5, 0.15, 6)]
    berries = []
    for x in (-1.6, -0.5, 0.6, 1.7):
        berries.append(heart(x, -1.0, 0.25))
    top = [spiral(0, 1.2, 0.05, 0.6, 2.0)]
    big = [heart(0, 2.2, 0.55), poly((-0.3, 2.65), (0, 2.95), (0.3, 2.65), closed=False)]
    plate = [ellipse(0, -2.4, 2.8, 0.35, 80)]
    return make("Strawberry Shortcake", layers + creams + berries + top + big + plate)


@design("ds_eclair", T)
def eclair(rng):
    pastry = chain(arc(-2.2, -0.5, 0.8, math.pi / 2, 3 * math.pi / 2, 20), [(2.2, -1.3)], arc(2.2, -0.5, 0.8, -math.pi / 2, math.pi / 2, 20), [(-2.2, 0.3)])
    glaze_bottom = [(x, -0.25 - (0.25 if k % 3 == 1 else 0.0)) for k, x in enumerate([-2.4 + 0.4 * k for k in range(13)])]
    lines = [[(-1.5, -0.8), (-0.3, -0.8)], [(0.3, -0.8), (1.5, -0.8)]]
    zig = [zigzag(-2.0, 2.0, 0.55, 0.1, 9)]
    plate = [ellipse(0, -1.8, 3.0, 0.5, 100)]
    return make("Chocolate Eclair", [pastry, glaze_bottom] + lines + zig + plate)


@design("ds_chocolate_bar", T)
def chocolate_bar(rng):
    bar = rect(-1.8, -2.6, 1.8, 2.0)
    squares = [rrect(-1.6 + 1.1 * i, -2.4 + 1.1 * j, -0.7 + 1.1 * i, -1.5 + 1.1 * j, 0.1) for i in range(3) for j in range(4)]
    wrapper = poly((-2.0, -2.8), (2.0, -2.8), (2.0, -0.6), (1.4, -0.3), (0.8, -0.7), (0.2, -0.3), (-0.4, -0.7), (-1.0, -0.3), (-1.6, -0.7), (-2.0, -0.6))
    foil = zigzag(-1.8, 1.8, 2.2, 0.1, 9)
    label = [heart(0, -1.6, 0.4)]
    return make("Chocolate Bar", [bar, wrapper, foil] + squares[3:] + label)


@design("ds_gumball_machine", T)
def gumball_machine(rng):
    globe = circle(0, 1.0, 1.8, 120)
    cap = [rrect(-0.6, 2.7, 0.6, 3.0, 0.1), ellipse(0, 2.75, 0.3, 0.15, 12)]
    base = poly((-1.2, -0.6), (1.2, -0.6), (1.6, -2.6), (-1.6, -2.6))
    slot = [circle(0, -1.3, 0.35, 20), [(-0.25, -1.3), (0.25, -1.3)]]
    chute = rect(-0.4, -2.3, 0.4, -1.9)
    balls = [circle(x, y, 0.3, 18) for x, y in [(-1.0, 0.0), (-0.3, -0.1), (0.4, 0.0), (1.0, 0.2), (-0.7, 0.6), (0.0, 0.5), (0.7, 0.7),
                                                 (-1.1, 1.2), (-0.4, 1.1), (0.3, 1.2), (1.1, 1.3), (-0.6, 1.8), (0.1, 1.8), (0.8, 1.9)]]
    return make("Gumball Machine", [globe, base, chute] + cap + slot + balls)


@design("ds_cotton_candy", T)
def cotton_candy(rng):
    puff = polar(lambda t: 1.6 + 0.2 * math.sin(7 * t) + 0.1 * math.sin(13 * t), cx=0, cy=1.0, n=300)
    swirls = [spiral(-0.5, 1.3, 0.05, 0.5, 1.6), spiral(0.6, 0.6, 0.05, 0.45, 1.5), arc(0.3, 1.9, 0.4, 0.3, 2.8, 12)]
    stick = [[(-0.12, -0.5), (-0.1, -2.9)], [(0.12, -0.5), (0.1, -2.9)], [(-0.1, -2.9), (0.1, -2.9)]]
    clouds = [arc(-2.2, 2.2, 0.35, 0, math.pi, 10), arc(2.2, -1.2, 0.3, 0, math.pi, 10)]
    return make("Cotton Candy", [puff] + swirls + stick + clouds)


@design("ds_gelatin", T)
def gelatin(rng):
    mold = chain([(-2.2, -2.0)], [(-1.8, 0.8)], [(-1.4 + 0.7 * k, 0.8 + (0.4 if k % 2 == 0 else 0.0)) for k in range(5)], [(1.8, 0.8)], [(2.2, -2.0)])
    ridges = [[(x, -2.0), (x * 0.82, 0.8)] for x in (-1.3, -0.45, 0.45, 1.3)]
    top_ring = ellipse(0, 1.0, 1.0, 0.3, 40)
    cream = [spiral(0, 1.6, 0.05, 0.5, 2)]
    wobble = [[(-2.6, 0.0), (-2.4, 0.4)], [(2.6, 0.0), (2.4, 0.4)], [(-2.7, -0.6), (-2.5, -0.2)], [(2.7, -0.6), (2.5, -0.2)]]
    plate = [ellipse(0, -2.2, 2.9, 0.4, 100)]
    return make("Wobbly Gelatin", [mold, top_ring] + ridges + cream + cherry(0.1, 2.3, 0.25) + wobble + plate)


@design("ds_flan", T)
def flan(rng):
    body = chain([(-2.2, -1.6)], [(-1.6, 0.8)], [(1.6, 0.8)], [(2.2, -1.6)])
    top = ellipse(0, 0.8, 1.6, 0.4, 70)
    caramel = chain([(-1.62, 0.7), (-1.7, 0.0)], arc(-1.55, 0.0, 0.15, math.pi, 2 * math.pi, 6), [(-1.4, 0.45), (-0.8, 0.4), (-0.7, -0.4)],
                    arc(-0.55, -0.4, 0.15, math.pi, 2 * math.pi, 6), [(-0.4, 0.4), (0.6, 0.4), (0.7, -0.1)], arc(0.85, -0.1, 0.15, math.pi, 2 * math.pi, 6),
                    [(1.0, 0.45), (1.62, 0.7)])
    plate = [ellipse(0, -1.8, 3.0, 0.6, 120), ellipse(0, -1.8, 2.4, 0.4, 100)]
    spoon = [[(1.8, 1.6), (2.8, 2.8)], ellipse(1.6, 1.4, 0.25, 0.35, 16, rot=0.7)]
    return make("Caramel Flan", [body, top, caramel] + plate + spoon)


@design("ds_milkshake", T)
def milkshake(rng):
    glass = poly((-1.4, 0.8), (1.4, 0.8), (1.0, -1.8), (-1.0, -1.8))
    stem = [[(-0.2, -1.8), (-0.2, -2.4)], [(0.2, -1.8), (0.2, -2.4)], ellipse(0, -2.55, 1.0, 0.2, 40)]
    cream = chain([(-1.5, 0.8)], arc(-1.0, 0.9, 0.5, math.pi, 0.3, 12), arc(0, 1.3, 0.75, 2.6, 0.5, 16), arc(1.0, 0.9, 0.5, 2.8, 0, 12), [(1.5, 0.8)])
    straw = [[(0.5, 1.6), (1.4, 3.0)], [(0.75, 1.5), (1.65, 2.9)], [(1.4, 3.0), (1.65, 2.9)]]
    stripes = [[(-1.2, -0.4), (1.2, -0.4)]]
    return make("Milkshake", [glass, cream] + stem + straw + stripes + cherry(-0.3, 2.3, 0.25))


@design("ds_hot_cocoa", T)
def hot_cocoa(rng):
    mug = chain([(-1.8, 0.8)], [(-1.8, -2.0)], arc(-1.3, -2.0, 0.5, math.pi, 1.5 * math.pi, 8), [(1.3, -2.5)], arc(1.3, -2.0, 0.5, 1.5 * math.pi, 2 * math.pi, 8), [(1.8, 0.8)])
    rim = ellipse(0, 0.8, 1.8, 0.35, 80)
    handle = [arc(1.9, -0.7, 0.8, -math.pi / 2, math.pi / 2, 20), arc(1.9, -0.7, 0.4, -math.pi / 2, math.pi / 2, 12)]
    marsh = [rrect(x - 0.3, y - 0.2, x + 0.3, y + 0.2, 0.08) for x, y in [(-0.8, 0.95), (0.1, 1.1), (0.9, 0.9)]]
    steam = [[(x + 0.2 * math.sin(4 * t), 1.6 + 1.2 * t) for t in [i / 16 for i in range(17)]] for x in (-0.7, 0.1, 0.9)]
    heart_ = heart(0, -0.8, 0.5)
    return make("Hot Cocoa with Marshmallows", [mug, rim, heart_] + handle + marsh + steam)


@design("ds_brownies", T)
def brownies(rng):
    def brownie(x, y, s):
        return [rect(x, y, x + s, y + s * 0.8), [(x, y + s * 0.65), (x + s, y + s * 0.65)], [(x + 0.2 * s, y + 0.3 * s), (x + 0.4 * s, y + 0.4 * s)],
                [(x + 0.6 * s, y + 0.2 * s), (x + 0.8 * s, y + 0.35 * s)]]
    b = brownie(-2.6, -2.4, 1.6) + brownie(-0.8, -2.4, 1.6) + brownie(1.0, -2.4, 1.6) + brownie(-1.7, -1.12, 1.6) + brownie(0.1, -1.12, 1.6) + brownie(-0.8, 0.16, 1.6)
    nuts = [circle(x, y, 0.1, 8) for x, y in [(-0.3, 1.25), (0.3, 1.3), (-0.5, 1.2)]]
    return make("Stack of Brownies", b + nuts + [[(-3.0, -2.4), (3.0, -2.4)]])


@design("ds_cake_pops", T)
def cake_pops(rng):
    pops = []
    for x, y in [(-1.6, 1.4), (0, 2.0), (1.6, 1.4), (-0.8, 0.6), (0.8, 0.6)]:
        pops += [circle(x, y, 0.6, 40), [(x, y - 0.6), (0.3 * x, -1.0)],
                 quad((x - 0.55, y + 0.2), (x, y + 0.45), (x + 0.55, y + 0.2))]
    jar = poly((-1.2, -1.0), (1.2, -1.0), (1.0, -2.8), (-1.0, -2.8))
    bow = [poly((0, -1.5), (-0.6, -1.2), (-0.6, -1.8)), poly((0, -1.5), (0.6, -1.2), (0.6, -1.8))]
    return make("Cake Pops", pops + [jar] + bow)


@design("ds_churros", T)
def churros(rng):
    sticks = [tube([(x, -1.4), (x + d, 2.6)], 0.5) for x, d in [(-1.0, -0.8), (0.0, 0.0), (1.0, 0.8)]]
    ridges = [[(x + d * 0.1, -1.0), (x + d * 0.9, 2.2)] for x, d in [(-1.0, -0.8), (0.0, 0.0), (1.0, 0.8)]]
    cup = poly((-1.8, -0.6), (1.8, -0.6), (1.3, -2.8), (-1.3, -2.8))
    stripes = [[(-1.6, -1.3), (1.6, -1.3)], [(-1.45, -2.0), (1.45, -2.0)]]
    sugar = [circle(x, y, 0.06, 6) for x, y in [(-2.0, 1.6), (2.0, 2.0), (1.9, 0.9), (-2.2, 0.4)]]
    dip = [ellipse(2.4, -2.4, 0.6, 0.25, 30), chain([(1.8, -2.4), (1.9, -2.8), (2.9, -2.8), (3.0, -2.4)])]
    return make("Churros", sticks + ridges + [cup] + stripes + sugar + dip)


@design("ds_candy_jar", T)
def candy_jar(rng):
    jar = chain([(-1.0, 2.0)], [(-1.0, 1.6)], cubic((-1.0, 1.6), (-2.6, 1.2), (-2.6, -2.6), (0, -2.6), 40), cubic((0, -2.6), (2.6, -2.6), (2.6, 1.2), (1.0, 1.6), 40), [(1.0, 2.0)])
    lid = [rrect(-1.3, 2.0, 1.3, 2.4, 0.1), circle(0, 2.7, 0.3, 20)]
    candies = []
    for x, y in [(-1.2, -1.8), (0.0, -2.0), (1.2, -1.7), (-0.6, -1.0), (0.6, -1.0), (-1.4, -0.4), (0.0, -0.3), (1.4, -0.3), (-0.6, 0.4), (0.7, 0.4)]:
        candies.append(circle(x, y, 0.32, 18))
    swirl_ = [spiral(x, y, 0.03, 0.25, 1.2) for x, y in [(0.0, -2.0), (-1.4, -0.4), (0.7, 0.4)]]
    label = [heart(0, 1.0, 0.35)]
    return make("Candy Jar", [jar] + lid + candies + swirl_ + label)


@design("ds_fruit_tart", T)
def fruit_tart(rng):
    shell = ellipse(0, -0.4, 2.8, 1.2, 140)
    side = chain([(-2.8, -0.4)], [(-2.6, -1.4)], quad((-2.6, -1.4), (0, -2.4), (2.6, -1.4), 40), [(2.8, -0.4)])
    flutes = [[(x, -0.4 - 1.2 * math.sqrt(max(0.0, 1 - (x / 2.8) ** 2))), (x * 0.93, -1.4 - 0.9 * math.sqrt(max(0.0, 1 - (x / 2.6) ** 2)))] for x in (-2.0, -1.0, 0.0, 1.0, 2.0)]
    kiwis = [circle(x, y, 0.45, 24) for x, y in [(-1.4, -0.4), (1.4, -0.4)]]
    kiwi_in = [circle(x, y, 0.15, 10) for x, y in [(-1.4, -0.4), (1.4, -0.4)]]
    berries = [heart(x, y, 0.25) for x, y in [(0.0, 0.2), (-0.5, -0.8), (0.5, -0.8)]]
    blue = [circle(x, y, 0.13, 10) for x, y in [(-0.7, 0.2), (0.7, 0.2), (0.0, -0.4), (-1.9, -0.9), (1.9, -0.9)]]
    mint = lens((0.0, 0.5), (0.4, 1.0), 0.5)
    return make("Fruit Tart", [shell, side, mint] + flutes + kiwis + kiwi_in + berries + blue)


@design("ds_swiss_roll", T)
def swiss_roll(rng):
    face = spiral(-1.4, 0, 0.1, 1.4, 2.5, 220)
    end = circle(-1.4, 0, 1.5, 100)
    body = [[(-1.4, 1.5), (2.4, 1.5)], [(-1.4, -1.5), (2.4, -1.5)], arc(2.4, 0, 1.5, -math.pi / 2, math.pi / 2, 30)]
    dust = [circle(x, y, 0.07, 6) for x, y in [(0.2, 1.8), (1.0, 1.9), (1.8, 1.8), (0.6, 2.2)]]
    plate = [[(-3.0, -1.9), (3.0, -1.9)]]
    berries = [heart(1.0, 2.6, 0.3)]
    return make("Swiss Roll", [face, end] + body + dust + plate + berries)


@design("ds_ice_cream_sandwich", T)
def ice_cream_sandwich(rng):
    top = rrect(-2.4, 0.6, 2.4, 1.6, 0.3)
    mid = [[(-2.25, 0.6), (-2.35, 0.0), (-2.25, -0.6)], [(2.25, 0.6), (2.35, 0.0), (2.25, -0.6)], [(1.2, -0.6), (1.25, -1.0), (1.4, -0.6)]]
    bottom = rrect(-2.4, -1.6, 2.4, -0.6, 0.3)
    holes = [circle(x, y, 0.08, 8) for x in (-1.6, -0.6, 0.4, 1.4) for y in (1.1, -1.1)]
    bite = arc(2.4, 1.6, 0.6, math.pi, 1.5 * math.pi, 12)
    return make("Ice Cream Sandwich", [top, bottom, bite] + mid + holes)


@design("ds_frozen_yogurt", T)
def frozen_yogurt(rng):
    cup = poly((-1.6, -0.2), (1.6, -0.2), (1.2, -2.8), (-1.2, -2.8))
    band = [[(-1.5, -0.8), (1.5, -0.8)], [(-1.35, -1.8), (1.35, -1.8)]]
    swirl = [ellipse(0, 0.2, 1.6, 0.45, 70), ellipse(0, 0.9, 1.2, 0.4, 60), ellipse(0, 1.5, 0.8, 0.35, 40), poly((-0.4, 1.8), (0.1, 2.5), (0.4, 1.8), closed=False)]
    toppings = [circle(x, y, 0.15, 10) for x, y in [(-1.1, 0.5), (0.9, 0.6), (-0.4, 1.2), (0.5, 1.6)]]
    spoon = [[(1.0, 1.2), (2.4, 2.8)], ellipse(2.55, 2.95, 0.22, 0.3, 14, rot=-0.7)]
    return make("Frozen Yogurt Cup", [cup] + band + swirl + toppings + spoon)


@design("ds_donut_box", T)
def donut_box(rng):
    box = rect(-2.8, -2.4, 2.8, 1.2)
    lid = poly((-2.8, 1.2), (-2.4, 2.8), (2.4, 2.8), (2.8, 1.2), closed=False)
    donuts = []
    for i in range(3):
        for j in range(2):
            x, y = -1.85 + 1.85 * i, -1.5 + 1.8 * j
            donuts += [circle(x, y, 0.8, 40), circle(x, y, 0.25, 16), polar(lambda t: 0.6 + 0.06 * math.sin(8 * t), cx=x, cy=y, n=60)]
    return make("Box of Donuts", [box, lid] + donuts)


@design("ds_sugar_cookies", T)
def sugar_cookies(rng):
    c = [heart(-1.5, 1.3, 1.0), star(1.5, 1.4, 1.3, 5, 0.5), circle(-1.4, -1.5, 1.1, 60), poly((0.6, -0.4), (2.6, -0.4), (2.6, -2.6), (0.6, -2.6))]
    icing = [heart(-1.5, 1.3, 0.75), star(1.5, 1.4, 0.95, 5, 0.5), circle(-1.4, -1.5, 0.85, 50), rrect(0.85, -2.35, 2.35, -0.65, 0.2)]
    dots = [circle(x, y, 0.08, 8) for x, y in [(-1.6, -1.3), (-1.1, -1.8), (-1.5, -1.9), (1.3, -1.2), (1.9, -1.8)]]
    return make("Sugar Cookies", c + icing + dots)


@design("ds_truffles", T)
def truffles(rng):
    box = rect(-2.8, -2.4, 2.8, 1.6)
    cells = [[(x, -2.4), (x, 1.6)] for x in (-0.93, 0.93)] + [[(-2.8, -0.4), (2.8, -0.4)]]
    balls = []
    for i in range(3):
        for j in range(2):
            x, y = -1.87 + 1.87 * i, -1.4 + 2.0 * j
            balls.append(circle(x, y, 0.7, 40))
            balls.append([quad((x - 0.5, y + 0.1), (x, y + 0.4), (x + 0.5, y + 0.1)), zigzag(x - 0.4, x + 0.4, y - 0.2, 0.1, 3), circle(x, y + 0.2, 0.15, 10)][(i + j) % 3])
    ribbon = [poly((0, 1.6), (-1.0, 2.6), (-1.0, 1.9)), poly((0, 1.6), (1.0, 2.6), (1.0, 1.9))]
    return make("Box of Chocolate Truffles", [box] + cells + balls + ribbon)


@design("ds_meringue_pie", T)
def meringue_pie(rng):
    crust = poly((-2.8, -1.4), (2.0, -0.4), (2.6, -2.2), (-2.4, -2.6))
    filling = [[(-2.6, -1.8), (2.3, -0.9)]]
    meringue = chain([(-2.8, -1.4)], [(-2.6 + 0.6 * k + 0.3, -1.25 + 0.21 * k + (0.9 if k % 2 == 0 else 0.5)) for k in range(8)], [(2.0, -0.4)])
    peaks = [poly((x, y), (x + 0.15, y + 0.4), (x + 0.3, y), closed=False) for x, y in [(-1.4, -0.4), (0.0, 0.0), (1.2, 0.3)]]
    lemon = [circle(-1.4, 1.8, 0.9, 40), circle(-1.4, 1.8, 0.7, 36)] + [[(-1.4, 1.8), (-1.4 + 0.7 * math.cos(a), 1.8 + 0.7 * math.sin(a))] for a in [k * math.pi / 4 for k in range(8)]]
    return make("Lemon Meringue Pie", [crust, meringue] + filling + peaks + lemon)


@design("ds_parfait", T)
def parfait(rng):
    glass = chain([(-1.4, 2.0), (-1.2, -1.6)], quad((-1.2, -1.6), (0, -2.2), (1.2, -1.6), 20), [(1.4, 2.0)])
    layers = [wave(-1.33, 1.33, y, 0.1, 3, 40) for y in (-1.2, -0.4, 0.4, 1.2)]
    granola = [circle(x, y, 0.08, 6) for x, y in [(-0.6, -0.8), (0.3, -0.7), (0.8, -0.9), (-0.3, 0.8), (0.6, 0.8)]]
    berries = [circle(x, y, 0.22, 14) for x, y in [(-0.5, 0.0), (0.5, 0.0), (0.0, -0.1)]] + [heart(-0.4, 2.3, 0.3), circle(0.4, 2.3, 0.25, 14)]
    mint = lens((0.0, 2.2), (0.5, 2.9), 0.5)
    spoon = [[(1.0, 1.6), (1.9, 3.0)]]
    base = [ellipse(0, -2.5, 1.2, 0.25, 40), [(0, -2.2), (0, -2.5)]]
    return make("Berry Parfait", [glass, mint] + layers + granola + berries + spoon + base)


@design("ds_cannoli", T)
def cannoli(rng):
    def can(cx, cy, rot):
        shell = [ellipse(0, 0, 1.6, 0.6, 60)]
        ends = [ellipse(-1.6, 0, 0.3, 0.6, 20), ellipse(1.6, 0, 0.3, 0.6, 20)]
        cream = [chain(arc(-1.75, 0, 0.55, math.pi / 2, 3 * math.pi / 2, 12)), chain(arc(1.75, 0, 0.55, -math.pi / 2, math.pi / 2, 12))]
        chips = [circle(x, y, 0.06, 6) for x, y in [(-2.0, 0.2), (-2.0, -0.2), (2.0, 0.15), (2.0, -0.25)]]
        bumps = [[(x, -0.45), (x + 0.2, 0.45)] for x in (-0.9, -0.3, 0.3, 0.9)]
        return [transform(p, dx=cx, dy=cy, rot=rot) for p in shell + ends + cream + chips + bumps]
    plate = [ellipse(0, -1.6, 3.0, 0.8, 120)]
    return make("Cannoli", can(0, 1.4, 0.15) + can(0, -0.6, -0.1) + plate)


@design("ds_mochi", T)
def mochi(rng):
    def m(cx, cy, s):
        return [chain([(cx - 1.0 * s, cy)], cubic((cx - 1.0 * s, cy), (cx - 1.0 * s, cy + 1.3 * s), (cx + 1.0 * s, cy + 1.3 * s), (cx + 1.0 * s, cy), 30), [(cx - 1.0 * s, cy)])]
    parts = m(-1.6, -1.6, 1.1) + m(1.6, -1.6, 1.1) + m(0, -0.4, 1.1)
    faces = [quad((x - 0.2, y + 0.4), (x, y + 0.25), (x + 0.2, y + 0.4)) for x, y in [(-1.6, -1.6), (1.6, -1.6), (0, -0.4)]]
    blush = [ellipse(x + d, y + 0.35, 0.18, 0.08, 10) for x, y in [(-1.6, -1.6), (1.6, -1.6), (0, -0.4)] for d in (-0.55, 0.55)]
    leaf = [lens((-0.5, 1.0), (0.6, 1.4), 0.5)]
    plate = [[(-3.0, -1.6), (3.0, -1.6)]]
    hints = [eye(x + d, y + 0.55, 0.07) for x, y in [(-1.6, -1.6), (1.6, -1.6), (0, -0.4)] for d in (-0.35, 0.35)]
    return make("Mochi Friends", parts + faces + blush + leaf + plate, hints)


@design("ds_cake_stand", T)
def cake_stand(rng):
    dome = chain([(-2.2, -1.2)], arc(0, -1.2, 2.2, math.pi, 0, 80), [(2.2, -1.2)])
    knob = circle(0, 1.25, 0.25, 16)
    stand = [[(-2.6, -1.2), (2.6, -1.2)], ellipse(0, -1.35, 2.6, 0.15, 60), [(-0.3, -1.5), (-0.3, -2.5)], [(0.3, -1.5), (0.3, -2.5)], ellipse(0, -2.65, 1.2, 0.2, 40)]
    cake = [rect(-1.3, -1.2, 1.3, -0.1), wave(-1.3, 1.3, -0.3, 0.1, 4, 40)]
    shine = arc(0, -1.2, 1.9, math.radians(120), math.radians(150), 8)
    cherries = cherry(-0.6, 0.15, 0.18) + cherry(0.6, 0.15, 0.18)
    return make("Cake Under a Glass Dome", [dome, knob, shine] + stand + cake + cherries)


@design("ds_rock_candy", T)
def rock_candy(rng):
    sticks = [[(x, -2.8), (x + d, 2.8)] for x, d in [(-1.2, -0.6), (0, 0), (1.2, 0.6)]]
    crystals = []
    for x, d in [(-1.2, -0.6), (0, 0), (1.2, 0.6)]:
        for k in range(5):
            t = 0.45 + 0.1 * k
            cx, cy = x + d * t, -2.8 + 5.6 * t
            crystals.append(poly((cx - 0.45, cy), (cx - 0.2, cy + 0.3), (cx + 0.3, cy + 0.25), (cx + 0.45, cy - 0.1), (cx + 0.1, cy - 0.3), (cx - 0.3, cy - 0.25)))
    glass = poly((-2.0, -0.8), (2.0, -0.8), (1.6, -2.9), (-1.6, -2.9))
    return make("Rock Candy Sticks", sticks + crystals + [glass])


@design("ds_smores", T)
def smores(rng):
    graham_b = rrect(-2.2, -2.4, 2.2, -1.4, 0.15)
    choc = rect(-1.8, -1.4, 1.8, -1.0)
    marsh = [cubic((-1.8, -1.0), (-2.7, -0.9), (-2.7, 0.3), (-1.8, 0.4), 16), cubic((1.8, -1.0), (2.7, -0.9), (2.7, 0.3), (1.8, 0.4), 16)]
    drip = [poly((-1.0, -1.0), (-1.1, -1.6), (-0.9, -1.6), closed=False)]
    graham_t = rrect(-2.2, 0.4, 2.2, 1.4, 0.15)
    holes = [circle(x, y, 0.08, 8) for x in (-1.4, -0.4, 0.6, 1.6) for y in (0.9, -1.9)]
    crumbs = [circle(x, y, 0.1, 8) for x, y in [(-1.6, 2.2), (0.4, 2.5), (1.8, 2.0)]]
    return make("S'mores", [graham_b, choc, graham_t] + marsh + drip + holes + crumbs)

@design("ds_fortune_cookie", T)
def fortune_cookie(rng):
    outer = chain(arc(0, -0.6, 2.4, 0, math.pi, 80), quad((-2.4, -0.6), (-1.0, -0.7), (0, -1.4), 20), quad((0, -1.4), (1.0, -0.7), (2.4, -0.6), 20))
    crease = quad((0, -1.4), (-0.5, 0.2), (0.3, 1.5), 24)
    paper = poly((0.15, -1.1), (2.6, -2.0), (2.8, -1.6), (0.35, -0.75))
    lines = [[(1.0, -1.2), (2.2, -1.65)]]
    plate = [ellipse(0, -2.4, 2.8, 0.4, 100)]
    return make("Fortune Cookie", [outer, crease, paper] + lines + plate)

@design("ds_fondue", T)
def fondue(rng):
    pot = chain([(-1.8, 0.0)], arc(0, 0.0, 1.8, math.pi, 2 * math.pi, 50), [(1.8, 0.0)])
    rim = ellipse(0, 0.0, 1.9, 0.35, 80)
    stand = [[(-1.6, -1.0), (-2.0, -2.6)], [(1.6, -1.0), (2.0, -2.6)], [(-2.2, -2.6), (2.2, -2.6)]]
    flame = [lens((0, -2.5), (0, -2.0), 0.6)]
    forks = [[(x, 0.2), (x + d, 2.8)] for x, d in [(-0.8, -1.0), (0.3, 0.2), (1.0, 1.2)]]
    fruit = [heart(-1.65, 2.55, 0.3), circle(0.48, 2.4, 0.3, 18), rect(2.0, 2.4, 2.5, 2.9)]
    drips = [poly((-1.0, -0.3), (-1.05, -0.8), (-0.9, -0.8), (-0.9, -0.3), closed=False)]
    return make("Chocolate Fondue", [pot, rim] + stand + flame + forks + fruit + drips)


@design("ds_bundt_cake", T)
def bundt_cake(rng):
    body = chain([(-2.4, 0.4)], [(-2.6, -1.8)], quad((-2.6, -1.8), (0, -2.5), (2.6, -1.8), 40), [(2.4, 0.4)])
    top = ellipse(0, 0.4, 2.4, 0.7, 120)
    hole = ellipse(0, 0.5, 0.5, 0.18, 30)
    flutes = [[(x, 0.4 - 0.7 * math.sqrt(max(0.0, 1 - (x / 2.4) ** 2))), (x * 1.08, -1.8 - 0.6 * math.sqrt(max(0.0, 1 - (x / 2.6) ** 2)))] for x in (-1.8, -0.9, 0.0, 0.9, 1.8)]
    glaze = [poly((x, y), (x - 0.1, y - 0.6), (x + 0.1, y - 0.6), (x + 0.15, y), closed=False) for x, y in [(-1.6, -0.1), (0.4, -0.3), (1.6, -0.1)]]
    plate = [ellipse(0, -2.3, 3.0, 0.5, 100)]
    return make("Bundt Cake", [body, top, hole] + flutes + glaze + plate)


@design("ds_chocolate_strawberries", T)
def chocolate_strawberries(rng):
    def berry(cx, cy, s, rot):
        body = chain(cubic((0, -1.1), (-0.9, -0.6), (-1.0, 0.7), (0, 0.7), 24), cubic((0, 0.7), (1.0, 0.7), (0.9, -0.6), (0, -1.1), 24))
        dip = wave(-0.85, 0.85, -0.2, 0.08, 2, 30)
        seeds = [circle(x, y, 0.05, 6) for x, y in [(-0.35, 0.25), (0.35, 0.3), (0.0, 0.45)]]
        leaves = poly((-0.6, 0.55), (-0.3, 0.95), (0, 0.75), (0.3, 0.95), (0.6, 0.55), closed=False)
        return [transform(p, dx=cx, dy=cy, s=s, rot=rot) for p in [body, dip, leaves] + seeds]
    b = berry(-1.6, 0.4, 1.1, 0.3) + berry(0.2, 1.3, 1.1, 0.0) + berry(1.8, 0.2, 1.1, -0.3)
    plate = [ellipse(0, -1.9, 3.0, 0.7, 120), ellipse(0, -1.9, 2.3, 0.45, 100)]
    return make("Chocolate-Dipped Strawberries", b + plate)
