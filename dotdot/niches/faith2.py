"""Faith & Bible niche, part 2."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "faith"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


def R(d):
    return math.radians(d)


def cross(cx, cy, h, w=None, t=None):
    """Latin cross outline, centred on the vertical post, height h."""
    w = 0.62 * h if w is None else w
    t = 0.14 * h if t is None else t
    yb, yt = cy - h / 2, cy + h / 2
    ya = cy + h / 2 - 0.3 * h
    return poly((cx - t / 2, yb), (cx + t / 2, yb), (cx + t / 2, ya - t / 2), (cx + w / 2, ya - t / 2), (cx + w / 2, ya + t / 2),
                (cx + t / 2, ya + t / 2), (cx + t / 2, yt), (cx - t / 2, yt), (cx - t / 2, ya + t / 2), (cx - w / 2, ya + t / 2),
                (cx - w / 2, ya - t / 2), (cx - t / 2, ya - t / 2))


def cloud(cx, cy, w, h, k=7, n=160):
    pts = []
    for i in range(n + 1):
        t = TAU * i / n
        f = 1 + 0.16 * abs(math.sin(k * t / 2))
        pts.append((cx + w / 2 * math.cos(t) * f, max(cy + h / 2 * math.sin(t) * f, cy - h * 0.28)))
    return pts


def bumpy(cx, cy, rx, ry, k=10, amp=0.08, n=160, rot=0.0):
    pts = []
    c, s = math.cos(rot), math.sin(rot)
    for i in range(n + 1):
        t = TAU * i / n
        f = 1 + amp * abs(math.sin(k * t / 2))
        x, y = rx * math.cos(t) * f, ry * math.sin(t) * f
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return pts


def rays(cx, cy, r0, r1, angles):
    return [[(cx + r0 * math.cos(R(a)), cy + r0 * math.sin(R(a))), (cx + r1 * math.cos(R(a)), cy + r1 * math.sin(R(a)))] for a in angles]


def sheep(cx, cy, s, d=1, lying=False):
    """Woolly sheep side view facing d (+1 right / -1 left)."""
    body = bumpy(cx, cy, 1.0 * s, 0.62 * s, k=14, amp=0.09)
    hx, hy = cx + d * 1.05 * s, cy + 0.3 * s
    head = ellipse(hx, hy, 0.36 * s, 0.24 * s, 40, rot=-d * 0.5)
    ear = lens((cx + d * 0.85 * s, cy + 0.5 * s), (cx + d * 0.6 * s, cy + 0.25 * s), 0.35)
    out = [body, head, ear]
    if lying:
        out += [ellipse(cx + d * 0.5 * s, cy - 0.66 * s, 0.32 * s, 0.1 * s, 20), ellipse(cx - d * 0.5 * s, cy - 0.66 * s, 0.32 * s, 0.1 * s, 20)]
    else:
        for x in (-0.6, -0.3, 0.3, 0.6):
            x0 = cx + x * s - 0.07 * s
            out.append(leg(x0, x0 + 0.14 * s, cy - 0.55 * s, cy - 1.1 * s))
    return out, [eye(hx + d * 0.08 * s, hy + 0.06 * s, 0.05 * s)]


def figure(cx, by, s, staff=None):
    """Robed figure standing on y=by, height about 4.2*s."""
    def P(x, y):
        return (cx + x * s, by + y * s)
    head = circle(*P(0, 3.55), 0.42 * s, 40)
    cloth = chain([P(-0.8, 2.55)], arc(cx, by + 3.55 * s, 0.6 * s, R(205), R(-25), 30), [P(0.8, 2.55)])
    robe = chain([P(-0.42, 2.85), P(-0.85, 2.5), P(-1.1, 0.8), P(-1.3, 0.0)], quad(P(-1.3, 0.0), P(0, 0.15), P(1.3, 0.0), 16),
                 [P(1.1, 0.8), P(0.85, 2.5), P(0.42, 2.85)])
    belt = quad(P(-1.0, 1.55), P(0, 1.4), P(1.0, 1.55), 12)
    folds = [[P(-0.4, 1.3), P(-0.55, 0.15)], [P(0.4, 1.3), P(0.55, 0.15)]]
    return [head, cloth, robe, belt] + folds


def palm(x, y, s):
    trunk = tube(cubic((x, y), (x + 0.1 * s, y + 0.8 * s), (x - 0.1 * s, y + 1.6 * s), (x + 0.1 * s, y + 2.2 * s), 12), 0.2 * s)
    fronds = [lens((x + 0.1 * s, y + 2.2 * s), (x + 0.1 * s + 1.0 * s * math.cos(R(a)), y + 2.2 * s + 0.7 * s * math.sin(R(a))), 0.18) for a in (20, 75, 130, 170, -15, 200)]
    return [trunk] + fronds


# --------------------------------------------------------------- pictures


@design("faith_good_shepherd", T)
def good_shepherd(rng):
    fig = figure(-0.3, -2.6, 1.15)
    arm = tube([(0.6, 0.0), (1.2, -0.4), (1.55, -0.2)], 0.38)
    staff = chain([(1.65, -2.6), (1.65, 2.2)], arc(2.05, 2.2, 0.4, math.pi, R(-30), 24))
    lamb, h = sheep(-2.3, -1.5, 0.75, d=1)
    ground = [[(-3.4, -2.75), (3.0, -2.75)]]
    return make("The Good Shepherd", fig + [arm, staff] + lamb + ground, h)


@design("faith_lost_sheep", T)
def lost_sheep(rng):
    s, h = sheep(0.2, 0.68, 1.5, d=-1)
    rocks = [poly((-3.2, -2.6), (-2.7, -1.3), (-1.8, -1.0), (1.8, -1.0), (2.5, -0.7), (3.4, -2.6), closed=False),
             [(-3.2, -2.6), (3.4, -2.6)], [(-1.8, -1.0), (-1.4, -1.9), (-1.6, -2.6)], [(1.0, -1.0), (1.3, -1.8)], [(2.5, -0.7), (2.2, -1.7)]]
    thorns = [cubic((2.6, -0.8), (2.8, 0.6), (3.0, 1.2), (3.3, 2.2), 14), cubic((2.8, 0.2), (2.4, 0.9), (2.6, 1.6), (2.3, 2.5), 14)]
    spikes = [[(2.85, 0.6), (3.15, 0.5)], [(3.0, 1.3), (3.25, 1.15)], [(2.5, 1.2), (2.25, 1.1)], [(2.5, 1.9), (2.25, 1.85)]]
    star_ = star(-2.6, 2.6, 0.4)
    return make("The Lost Sheep", s + rocks + thorns + spikes + [star_], h)


@design("faith_nativity_stable", T)
def nativity_stable(rng):
    roof = poly((-3.0, 0.6), (0, 2.0), (3.0, 0.6), (2.6, 0.6), (0, 1.6), (-2.6, 0.6))
    posts = [[(-2.4, 0.75), (-2.4, -2.4)], [(2.4, 0.75), (2.4, -2.4)]]
    ground = [(-3.4, -2.4), (3.4, -2.4)]
    planks = [[(-2.4, 0.0 - 0.6 * k), (-1.6, 0.0 - 0.6 * k)] for k in range(3)] + [[(2.4, 0.0 - 0.6 * k), (1.6, 0.0 - 0.6 * k)] for k in range(3)]
    manger = poly((-1.0, -1.0), (1.0, -1.0), (0.7, -1.6), (-0.7, -1.6))
    mlegs = [[(-0.9, -1.6), (-0.5, -2.4)], [(0.9, -1.6), (0.5, -2.4)], [(-0.5, -1.6), (-0.9, -2.4)], [(0.5, -1.6), (0.9, -2.4)]]
    hay = zigzag(-1.0, 1.0, -0.9, 0.12, 8)
    baby = [ellipse(0.0, -0.75, 0.55, 0.22, 30), circle(0.55, -0.6, 0.2, 20)]
    halo = arc(0.55, -0.6, 0.35, R(-30), R(150), 14)
    st = star(0, 3.0, 0.75, n=8, inner=0.35)
    return make("Stable in Bethlehem", [roof, ground, manger, hay, halo, st] + posts + planks + mlegs + baby)


@design("faith_three_crosses", T)
def three_crosses(rng):
    hill = chain(cubic((-3.6, -2.6), (-2.6, -0.6), (-1.2, -0.2), (0, -0.2), 30), cubic((0, -0.2), (1.2, -0.2), (2.6, -0.6), (3.6, -2.6), 30))
    c = [cross(0, 1.3, 3.0), cross(-2.0, 0.4, 2.0), cross(2.0, 0.4, 2.0)]
    sun = arc(0, -0.2, 3.3, R(15), R(165), 60)
    rays_ = rays(0, -0.2, 3.4, 3.9, (25, 45, 135, 155))
    path = [cubic((0.2, -0.4), (0.8, -1.2), (-0.6, -1.8), (0.0, -2.6), 20)]
    return make("Three Crosses on Calvary", [hill, sun] + c + rays_ + path)


@design("faith_empty_tomb", T)
def empty_tomb(rng):
    rockface = chain([(-3.4, -2.2)], cubic((-3.4, -2.2), (-3.2, 2.2), (2.2, 2.6), (2.6, -2.2), 50))
    door = chain([(-1.6, -2.2), (-1.6, -0.6)], arc(-0.8, -0.6, 0.8, math.pi, 0, 24), [(0.0, -2.2)])
    inner = chain([(-1.3, -2.2), (-1.3, -0.7)], arc(-0.8, -0.7, 0.5, math.pi, 0, 16), [(-0.3, -2.2)])
    stone = [circle(1.6, -1.2, 1.0, 70), circle(1.6, -1.2, 0.6, 50)]
    ground = [(-3.6, -2.2), (3.6, -2.2)]
    light = rays(-0.8, -1.2, 1.3, 1.9, (60, 90, 120))
    lilies = [poly((-2.6, -2.2), (-2.6, -1.6), closed=False), lens((-2.6, -1.6), (-2.9, -1.1), 0.4), lens((-2.6, -1.6), (-2.3, -1.1), 0.4),
              poly((3.0, -2.2), (3.0, -1.4), closed=False), lens((3.0, -1.4), (2.75, -0.9), 0.4), lens((3.0, -1.4), (3.25, -0.9), 0.4)]
    sun = circle(2.6, 2.4, 0.5, 30)
    return make("The Empty Tomb", [rockface, door, inner, ground, sun] + stone + light + lilies)


def fish(cx, cy, s, d=1):
    body = chain(quad((cx - d * 1.0 * s, cy), (cx, cy + 0.65 * s), (cx + d * 1.0 * s, cy), 20),
                 quad((cx + d * 1.0 * s, cy), (cx, cy - 0.65 * s), (cx - d * 1.0 * s, cy), 20))
    tail = poly((cx - d * 1.0 * s, cy), (cx - d * 1.5 * s, cy + 0.4 * s), (cx - d * 1.5 * s, cy - 0.4 * s))
    gill = arc(cx + d * 0.45 * s, cy, 0.25 * s, R(110), R(250), 10) if d > 0 else arc(cx - 0.45 * s, cy, 0.25 * s, R(70), R(-70), 10)
    return [body, tail, gill], [eye(cx + d * 0.7 * s, cy + 0.08 * s, 0.06 * s)]


@design("faith_loaves_fishes", T)
def loaves_fishes(rng):
    basket = chain([(-2.8, 0.2)], quad((-2.8, 0.2), (-2.6, -2.4), (0, -2.4), 20), quad((0, -2.4), (2.6, -2.4), (2.8, 0.2), 20), [(-2.8, 0.2)])
    rim = rrect(-3.0, 0.0, 3.0, 0.45, 0.2)
    weave = [quad((-2.7, y), (0, y - 0.3), (2.7, y)) for y in (-0.5, -1.1, -1.7)] + [[(x, 0.0), (x * 0.8, -2.3)] for x in (-1.6, -0.8, 0.0, 0.8, 1.6)]
    loaves = [chain(arc(x, y, 0.62, 0, math.pi, 24)) for x, y in [(-2.1, 0.45), (-0.85, 0.45), (0.4, 0.45)]] + \
             [chain(arc(x, y, 0.6, R(10), R(170), 22)) for x, y in [(-1.5, 1.0), (-0.25, 1.0)]]
    slashes = [[(x - 0.2, y + 0.3), (x + 0.15, y + 0.45)] for x, y in [(-2.1, 0.45), (-0.85, 0.45), (0.4, 0.45), (-1.5, 1.05), (-0.25, 1.05)]]
    f1, h1 = fish(1.9, 1.3, 0.9, -1)
    f2, h2 = fish(2.2, 0.75, 0.75, -1)
    return make("Five Loaves and Two Fish", [basket, rim] + weave + loaves + slashes + f1 + f2, h1 + h2)


@design("faith_jonah_whale", T)
def jonah_whale(rng):
    back = chain(cubic((3.0, -0.6), (3.2, 1.6), (1.0, 2.2), (-1.0, 1.4), 40), cubic((-1.0, 1.4), (-2.2, 0.9), (-2.4, 0.4), (-2.9, 1.4), 20))
    tail = chain([(-2.9, 1.4)], quad((-3.2, 1.6), (-3.6, 1.6), (-3.6, 1.7), 6)[1:], [(-3.0, 1.1), (-3.5, 0.6), (-2.6, 0.5)])
    belly = chain([(-2.6, 0.5)], cubic((-2.0, -0.3), (-0.6, -1.4), (1.6, -1.4), (3.0, -0.6), 40))
    mouth = cubic((3.0, -0.4), (2.4, -0.4), (1.8, -0.6), (1.3, -0.9), 16)
    grooves = [quad((1.4, -1.2 + 0.18 * k), (0.4, -1.25 + 0.15 * k), (-0.5, -1.0 + 0.1 * k)) for k in range(2)]
    spout = [cubic((1.0, 2.0), (0.9, 2.6), (0.4, 2.8), (0.1, 2.6), 12), cubic((1.0, 2.0), (1.1, 2.6), (1.6, 2.8), (1.9, 2.6), 12), [(1.0, 2.0), (1.0, 2.9)]]
    jonah = [circle(3.5, -0.4, 0.22, 20), poly((3.3, -0.65), (3.15, -1.6), (3.85, -1.6), (3.7, -0.65)), [(3.35, -0.75), (3.0, -0.2)], [(3.65, -0.75), (4.0, -0.2)]]
    sea = [wave(-3.6, 4.2, -1.8, 0.12, 7, 120), wave(-3.4, 4.0, -2.4, 0.1, 6, 100)]
    return make("Jonah and the Whale", [back, tail, belly, mouth] + grooves + spout + jonah + sea, [eye(2.0, 0.2, 0.12)])


@design("faith_david_harp", T)
def david_harp(rng):
    neck = cubic((-1.8, 2.4), (-0.6, 3.3), (0.6, 1.2), (2.2, 1.9), 60)
    pillar = rrect(-2.15, -2.7, -1.55, 2.6, 0.2)
    box = tube([(-1.5, -2.4), (2.1, 1.7)], 0.55)
    frame = [neck, chain(cubic((-1.8, 2.75), (-0.4, 3.6), (0.8, 1.6), (2.4, 2.25), 60)), arc(2.25, 1.95, 0.3, R(-60), R(110), 10)]
    strings = []
    for k in range(8):
        x = -1.2 + 3.0 * k / 8 + 0.15
        yb = -2.4 + (x + 1.5) * (4.1 / 3.6) + 0.3
        yt = min(neck, key=lambda p: abs(p[0] - x))[1]
        strings.append([(x, yb), (x, yt)])
    knob = circle(-1.85, 2.9, 0.25, 16)
    notes = []
    for x, y in [(1.6, -1.6), (2.7, -0.9)]:
        notes += [ellipse(x, y, 0.28, 0.2, 20, rot=0.4), [(x + 0.26, y + 0.08), (x + 0.26, y + 1.3)], quad((x + 0.26, y + 1.3), (x + 0.7, y + 1.0), (x + 0.6, y + 0.6), 8)]
    base = [(-2.6, -2.9), (2.6, -2.9)]
    return make("King David's Harp", [pillar, box, knob, base] + frame + strings + notes)


def roman(n, x, y, h):
    """Roman numerals I..X as strokes, left edge x, baseline y."""
    sym = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X"}[n]
    out, cx = [], x
    w = 0.42 * h
    for ch in sym:
        if ch == "I":
            out.append([(cx, y), (cx, y + h)])
            cx += 0.18 * h
        elif ch == "V":
            out.append([(cx, y + h), (cx + w / 2, y), (cx + w, y + h)])
            cx += w + 0.15 * h
        else:
            out += [[(cx, y), (cx + w, y + h)], [(cx, y + h), (cx + w, y)]]
            cx += w + 0.15 * h
    return out


@design("faith_tablets", T)
def tablets(rng):
    left = chain([(-0.1, -2.6), (-0.1, 1.6)], arc(-1.4, 1.6, 1.3, 0, math.pi, 30), [(-2.7, -2.6), (-0.1, -2.6)])
    right = mirror_x(left)
    inl = chain([(-0.35, -2.35), (-0.35, 1.6)], arc(-1.4, 1.6, 1.05, 0, math.pi, 26), [(-2.45, -2.35), (-0.35, -2.35)])
    text = []
    for k in range(5):
        y = 1.6 - 0.85 * k
        text += roman(k + 1, -2.0, y - 0.35, 0.5)
        text += roman(k + 6, 0.8, y - 0.35, 0.5)
    rays_ = rays(0, 1.6, 3.0, 3.6, (20, 50, 90, 130, 160))
    return make("The Ten Commandments", [left, right, inl, mirror_x(inl)] + text + rays_)


@design("faith_burning_bush", T)
def burning_bush(rng):
    low = [(x, y) for x, y in bumpy(0, -0.6, 2.4, 1.2, k=16, amp=0.12, n=200)[100:]][::-1]
    tips = [(-1.8, 1.0), (-1.1, 2.0), (-0.3, 3.2), (0.5, 2.4), (1.2, 2.9), (1.9, 1.3)]
    fl = flame_outline(low[-1][0], low[0][0], -0.6, tips)
    outline = chain(low, fl)
    inner = flame_outline(-1.0, 1.0, -0.5, [(-0.5, 1.0), (0.1, 1.9), (0.6, 1.2)])
    twigs = [[(0, -1.7), (0, -0.9), (-0.8, -0.4)], [(0, -0.9), (0.9, -0.5)], [(-1.4, -1.2), (-0.8, -0.9)], [(1.5, -1.3), (0.8, -0.8)]]
    trunk = [[(-0.25, -1.8), (-0.35, -2.5)], [(0.25, -1.8), (0.35, -2.5)]]
    ground = [(-3.4, -2.5), (3.4, -2.5)]
    sandals = [ellipse(-2.6, -2.85, 0.5, 0.18, 24), ellipse(-1.5, -2.9, 0.5, 0.18, 24), [(-2.75, -2.7), (-2.45, -3.0)], [(-1.65, -2.75), (-1.35, -3.05)]]
    glow = rays(0, 0.6, 3.0, 3.6, (15, 40, 140, 165))
    return make("The Burning Bush", [outline, inner, ground] + twigs + trunk + sandals + glow)


@design("faith_parting_sea", T)
def parting_sea(rng):
    lw = chain([(-3.4, -2.6), (-3.4, 1.2)], cubic((-3.4, 1.2), (-3.3, 2.6), (-2.0, 3.3), (-0.9, 2.7), 24),
               cubic((-0.9, 2.7), (-0.8, 2.3), (-1.2, 2.0), (-1.3, 1.8), 10), cubic((-1.3, 1.8), (-1.0, 1.0), (-0.8, -1.0), (-0.7, -2.6), 20))
    curl = spiral(-1.55, 2.45, 0.42, 0.08, 0.85, 40, rot=R(10))
    rw, rcurl = mirror_x(lw), mirror_x(curl)
    foam = [wave(-3.2, -1.4, y, 0.1, 2.5, 40) for y in (1.0, 0.0, -1.0)] + [wave(1.4, 3.2, y, 0.1, 2.5, 40) for y in (1.0, 0.0, -1.0)]
    fish_ = []
    hs = []
    for x, y, d in [(-2.3, -1.8, 1), (2.3, 0.5, -1)]:
        f, h = fish(x, y, 0.35, d)
        fish_ += f
        hs += h
    path = [[(-0.7, -2.6), (-0.2, 1.0)], [(0.7, -2.6), (0.2, 1.0)]]
    moses = figure(0, -2.5, 0.35)
    staff = [[(0.4, -2.5), (0.55, -0.4)]]
    pillar = [cloud(0, 3.1, 1.6, 0.7, k=5)]
    return make("Parting of the Red Sea", [lw, rw, curl, rcurl] + foam + fish_ + path + moses + staff + pillar, hs)


@design("faith_jacobs_ladder", T)
def jacobs_ladder(rng):
    rails = [[(-1.2, -2.6), (-0.4, 1.8)], [(1.2, -2.6), (0.4, 1.8)]]
    rungs = []
    for k in range(9):
        t = (k + 0.5) / 9
        y = -2.6 + 4.4 * t
        x = 1.2 - 0.8 * t
        rungs.append([(-x, y), (x, y)])
    clouds = [cloud(-1.6, 2.2, 2.6, 1.0, k=6), cloud(1.6, 2.2, 2.4, 0.9, k=6)]
    rays_ = rays(0, 2.2, 1.3, 2.1, (40, 65, 90, 115, 140))
    rock = chain(arc(-2.6, -2.6, 0.5, 0, math.pi, 16), [(-3.1, -2.6)])
    sleeper = [ellipse(2.4, -2.35, 0.9, 0.25, 30), circle(1.35, -2.2, 0.2, 16)]
    ground = [(-3.4, -2.6), (3.4, -2.6)]
    stars_ = [star(x, y, 0.22) for x, y in [(-2.8, 0.6), (2.8, 0.3), (-2.2, -0.8), (2.4, -1.0)]]
    return make("Jacob's Ladder", rails + rungs + clouds + rays_ + [rock, ground] + sleeper + stars_)


@design("faith_tower_babel", T)
def tower_babel(rng):
    tiers = []
    widths = [3.2, 2.7, 2.2, 1.7, 1.25, 0.85]
    y = -2.6
    for k, w in enumerate(widths):
        h = 0.8 - 0.05 * k
        tiers.append(rect(-w, y, w, y + h) if k == 0 else poly((-w, y), (-w, y + h), (w, y + h), (w, y), closed=False))
        tiers.append([(-w, y), (w, y)] if k else [(-w, y), (w, y)])
        # ramp
        tiers.append([(-w + 0.1, y + 0.05), (w - 0.1, y + h - 0.05)] if k % 2 == 0 else [(w - 0.1, y + 0.05), (-w + 0.1, y + h - 0.05)])
        for a in range(-int(w) + 0, int(w) + 1):
            if k < 4:
                xx = a * 0.9 * (w / max(1, int(w)))
                if abs(xx) < w - 0.3:
                    tiers.append(chain([(xx - 0.12, y + 0.1)], arc(xx, y + h - 0.35, 0.12, math.pi, 0, 6), [(xx + 0.12, y + 0.1)]))
        y += h
    top = poly((-0.5, y), (-0.5, y + 0.5), (0.5, y + 0.5), (0.5, y), closed=False)
    clouds = [cloud(-2.4, 2.0, 1.6, 0.6, k=5), cloud(2.5, 1.4, 1.4, 0.5, k=5)]
    return make("Tower of Babel", tiers + [top] + clouds)


@design("faith_lion_judah", T)
def lion_judah(rng):
    mane = bumpy(0, 0.2, 2.6, 2.7, k=18, amp=0.1, n=220)
    face = chain(cubic((0, 2.0), (-1.4, 2.0), (-1.5, 0.2), (-0.9, -1.2), 30), quad((-0.9, -1.2), (0, -1.9), (0.9, -1.2), 20),
                 cubic((0.9, -1.2), (1.5, 0.2), (1.4, 2.0), (0, 2.0), 30))
    ears = [arc(-1.0, 1.7, 0.4, R(30), R(200), 14), arc(1.0, 1.7, 0.4, R(-20), R(150), 14)]
    nose = poly((-0.45, -0.3), (0.45, -0.3), (0, -0.75))
    muzzle = [chain([(0, -0.75), (0, -0.95)], arc(-0.4, -0.95, 0.4, 0, R(-160), 12)), arc(0.4, -0.95, 0.4, R(180), R(340), 12)]
    brows = [quad((-1.0, 0.75), (-0.6, 0.95), (-0.25, 0.7)), quad((1.0, 0.75), (0.6, 0.95), (0.25, 0.7))]
    bridge = [[(-0.25, 0.4), (-0.35, -0.3)], [(0.25, 0.4), (0.35, -0.3)]]
    eyes_ = [ellipse(-0.6, 0.45, 0.25, 0.15, 20), ellipse(0.6, 0.45, 0.25, 0.15, 20)]
    return make("Lion of Judah", [mane, face, nose] + ears + muzzle + brows + bridge + eyes_, [eye(-0.6, 0.45, 0.09), eye(0.6, 0.45, 0.09)])


@design("faith_rainbow_covenant", T)
def rainbow_covenant(rng):
    bands = [arc(0, -1.6, r, R(0), R(180), 80) for r in (3.0, 2.55, 2.1, 1.65)]
    clouds = [cloud(-2.4, -1.6, 2.0, 1.0, k=6), cloud(2.4, -1.6, 2.0, 1.0, k=6)]
    drops = [drop(x, y, 0.12) for x, y in [(-2.8, -2.7), (-2.2, -3.0), (-1.6, -2.6), (1.8, -2.7), (2.4, -3.0), (3.0, -2.6)]]
    d, h = dove_side(0.0, 1.85, 0.6)
    branch = [[(0.93, 2.09), (1.3, 1.7)], lens((1.1, 1.9), (1.45, 2.05), 0.35), lens((1.2, 1.8), (1.3, 1.45), 0.35)]
    return make("Rainbow of the Covenant", bands + clouds + drops + d + branch, h)


@design("faith_star_bethlehem", T)
def star_bethlehem(rng):
    st = star(0, 1.8, 1.2, n=8, inner=0.3)
    tail = [[(0, 0.6), (0, -0.9)], [(-0.2, 0.7), (-1.0, -0.6)], [(0.2, 0.7), (1.0, -0.6)]]
    town = chain([(-3.4, -2.6), (-3.4, -1.4), (-2.6, -1.4), (-2.6, -1.0)], arc(-2.1, -1.0, 0.5, math.pi, 0, 16),
                 [(-1.6, -1.0), (-1.6, -1.6), (-0.6, -1.6), (-0.6, -1.2), (0.4, -1.2), (0.4, -1.8), (1.0, -1.8), (1.0, -0.9),
                  (1.4, -0.9), (1.4, -1.5), (2.4, -1.5)], arc(2.9, -1.5, 0.5, math.pi, 0, 16), [(3.4, -1.5), (3.4, -2.6), (-3.4, -2.6)])
    windows = [rect(x, y, x + 0.25, y + 0.3) for x, y in [(-3.1, -2.0), (-2.25, -1.8), (-1.25, -2.1), (-0.1, -1.7), (0.6, -2.2), (1.8, -2.0), (2.75, -2.1)]]
    small = [star(x, y, 0.2) for x, y in [(-2.6, 2.4), (2.7, 2.6), (-2.0, 0.6), (2.2, 0.4), (-3.0, 1.2)]]
    return make("Star of Bethlehem", [st, town] + tail + windows + small)


@design("faith_crown_thorns", T)
def crown_thorns(rng):
    a = [(2.4 * math.cos(t), 0.9 * math.sin(t) + 0.12 * math.sin(7 * t)) for t in [TAU * i / 200 for i in range(201)]]
    b = [(2.4 * math.cos(t), 0.9 * math.sin(t) - 0.12 * math.sin(7 * t)) for t in [TAU * i / 200 for i in range(201)]]
    c = [(2.0 * math.cos(t), 0.65 * math.sin(t) + 0.1 * math.sin(9 * t)) for t in [TAU * i / 200 for i in range(201)]]
    thorns = []
    for k in range(14):
        t = TAU * (k + 0.5) / 14
        x, y = 2.3 * math.cos(t), 0.85 * math.sin(t)
        nx, ny = math.cos(t), math.sin(t) * 1.4
        L = math.hypot(nx, ny)
        nx, ny = nx / L, ny / L
        px, py = -ny, nx
        thorns.append(poly((x + px * 0.12, y + py * 0.12), (x + nx * 0.5, y + ny * 0.5 + 0.1), (x - px * 0.12, y - py * 0.12), closed=False))
    nails = [poly((x - 0.08, -2.2), (x - 0.08, -1.4), (x - 0.25, -1.35), (x + 0.25, -1.35), (x + 0.08, -1.4), (x + 0.08, -2.2), (x, -2.5), (x - 0.08, -2.2),
                  closed=False) for x in (-0.8, 0.0, 0.8)]
    rays_ = rays(0, 0.0, 2.9, 3.4, (30, 60, 90, 120, 150))
    return make("Crown of Thorns", [a, b, c] + thorns + nails + rays_)


@design("faith_communion", T)
def communion(rng):
    bowl = chain([(-1.8, 2.4)], cubic((-1.8, 2.4), (-1.8, 0.6), (-0.8, 0.0), (-0.2, -0.1), 30), [(0.2, -0.1)],
                 cubic((0.2, -0.1), (0.8, 0.0), (1.8, 0.6), (1.8, 2.4), 30), [(-1.8, 2.4)])
    wine = quad((-1.72, 1.8), (0, 1.6), (1.72, 1.8))
    stem = [poly((-0.2, -0.1), (-0.15, -1.4), (-0.6, -2.3), (0.6, -2.3), (0.15, -1.4), (0.2, -0.1), closed=False)]
    knob = ellipse(0, -0.8, 0.38, 0.2, 24)
    base = ellipse(0, -2.35, 1.2, 0.3, 40)
    cr = cross(0, 0.95, 0.9)
    bread = chain(arc(2.4, -2.0, 1.1, 0, math.pi, 30), [(3.5, -2.0)][::-1], [(1.3, -2.6), (3.5, -2.6), (3.5, -2.0)])
    slashes = [[(1.9 + 0.4 * k, -1.4 + (0.05 if k == 1 else 0)), (2.15 + 0.4 * k, -1.05 + (0.05 if k == 1 else 0))] for k in range(3)]
    grapes = [circle(x, y, 0.25, 18) for x, y in [(-2.6, -1.6), (-2.1, -1.6), (-2.35, -2.0), (-2.85, -2.0), (-2.6, -2.4), (-3.1, -1.6)]] + [[(-2.4, -1.35), (-2.2, -0.9)]]
    return make("Communion Cup and Bread", [bowl, wine, base, knob, cr, bread] + stem + slashes + grapes)


@design("faith_candle", T)
def candle(rng):
    body = chain([(-0.9, -2.0), (-0.9, 0.9)], [(-0.6, 1.0), (-0.55, 0.6), (-0.45, 1.0), (0.2, 1.05), (0.3, 0.4), (0.45, 1.0), (0.9, 0.9), (0.9, -2.0)])
    top = ellipse(0, 1.0, 0.9, 0.18, 40)
    wick = [(0, 1.0), (0, 1.35)]
    flame = chain(cubic((0, 1.3), (-0.6, 1.6), (-0.3, 2.4), (0, 3.0), 20), cubic((0, 3.0), (0.3, 2.4), (0.6, 1.6), (0, 1.3), 20))
    inner = chain(cubic((0, 1.45), (-0.25, 1.65), (-0.15, 2.1), (0, 2.35), 12), cubic((0, 2.35), (0.15, 2.1), (0.25, 1.65), (0, 1.45), 12))
    glow = [arc(0, 2.0, 1.4, R(10), R(170), 40)] + rays(0, 2.0, 1.7, 2.3, (0, 30, 60, 90, 120, 150, 180))
    dish = [ellipse(0, -2.1, 2.0, 0.45, 60), ellipse(0, -2.0, 1.2, 0.22, 40)]
    handle = [circle(2.3, -2.0, 0.35, 24)]
    return make("Candle of Light", [body, top, wick, flame, inner] + glow + dish + handle)


@design("faith_rose_window", T)
def rose_window(rng):
    outer = [circle(0, 0, 3.0, 160), circle(0, 0, 2.7, 150)]
    hub = [circle(0, 0, 0.7, 50), star(0, 0, 0.55, n=6, inner=0.5)]
    petals, lobes = [], []
    for k in range(12):
        a = TAU * k / 12
        petals.append(lens((0.7 * math.cos(a), 0.7 * math.sin(a)), (2.0 * math.cos(a), 2.0 * math.sin(a)), 0.2))
        lobes.append(circle(2.35 * math.cos(a + TAU / 24), 2.35 * math.sin(a + TAU / 24), 0.28, 20))
    return make("Rose Window", outer + hub + petals + lobes)


@design("faith_stained_glass", T)
def stained_glass(rng):
    frame = chain([(-2.0, -3.0), (-2.0, 1.2)], arc(0.0, 1.2, 2.0, math.pi, 0, 40), [(2.0, -3.0), (-2.0, -3.0)])
    inner = chain([(-1.7, -2.7), (-1.7, 1.2)], arc(0.0, 1.2, 1.7, math.pi, 0, 36), [(1.7, -2.7), (-1.7, -2.7)])
    dove = chain(quad((-0.9, 1.2), (0, 1.0), (0.9, 1.2), 10), quad((0.9, 1.2), (0.3, 1.9), (0, 2.2), 10),
                 quad((0, 2.2), (-0.3, 1.9), (-0.9, 1.2), 10))
    dove = [chain(arc(0, 1.7, 0.25, R(-60), R(240), 16)), poly((-0.2, 1.5), (-1.3, 1.9), (-1.0, 1.4), (-0.15, 1.2)), poly((0.2, 1.5), (1.3, 1.9), (1.0, 1.4), (0.15, 1.2)),
            poly((-0.2, 1.25), (0, 0.6), (0.2, 1.25), closed=False)]
    cr = cross(0, -1.0, 2.6, w=1.6, t=0.4)
    leads = [[(-1.7, 0.2), (1.7, 0.2)], [(-1.7, -1.6), (-0.2, -1.2)], [(1.7, -1.6), (0.2, -1.2)], [(-1.7, -0.6), (-0.8, -0.2)],
             [(1.7, -0.6), (0.8, -0.2)], [(-1.7, -2.3), (-0.2, -2.0)], [(1.7, -2.3), (0.2, -2.0)]]
    return make("Stained Glass Window", [frame, inner, cr] + dove + leads)


@design("faith_church_steeple", T)
def church_steeple(rng):
    tower = rect(-0.9, -3.0, 0.9, 0.6)
    belfry = [rect(-0.9, 0.6, 0.9, 1.9), chain([(-0.45, 0.7), (-0.45, 1.4)], arc(0, 1.4, 0.45, math.pi, 0, 14), [(0.45, 0.7)])]
    louvers = [[(-0.35, 0.85 + 0.15 * k), (0.35, 0.85 + 0.15 * k)] for k in range(4)]
    spire = poly((-1.0, 1.9), (0, 4.4), (1.0, 1.9), closed=False)
    cr = cross(0, 4.85, 0.9)
    clock = [circle(0, -0.3, 0.55, 40), [(0, -0.3), (0, 0.05)], [(0, -0.3), (0.25, -0.4)]]
    door = chain([(-0.45, -3.0), (-0.45, -2.2)], arc(0, -2.2, 0.45, math.pi, 0, 14), [(0.45, -3.0)])
    roofs = [poly((-0.9, -0.9), (-3.0, -1.8), (-3.0, -3.0), (-0.9, -3.0), closed=False), poly((0.9, -0.9), (3.0, -1.8), (3.0, -3.0), (0.9, -3.0), closed=False)]
    wins = [chain([(x - 0.2, -2.6), (x - 0.2, -2.1)], arc(x, -2.1, 0.2, math.pi, 0, 8), [(x + 0.2, -2.6), (x - 0.2, -2.6)]) for x in (-2.2, -1.5, 1.5, 2.2)]
    return make("Church Steeple", [tower, spire, door, cr] + belfry + louvers + clock + roofs + wins)


@design("faith_bell_tower", T)
def bell_tower(rng):
    tower = poly((-1.8, -3.0), (-1.8, 1.8), (1.8, 1.8), (1.8, -3.0), closed=False)
    arch = chain([(-1.3, -0.6), (-1.3, 0.9)], arc(0, 0.9, 1.3, math.pi, 0, 30), [(1.3, -0.6), (-1.3, -0.6)])
    roof = poly((-2.2, 1.8), (0, 3.4), (2.2, 1.8), (-2.2, 1.8))
    cr = cross(0, 3.85, 0.9)
    bell = chain([(-0.9, -0.3)], cubic((-0.9, -0.3), (-0.5, 0.0), (-0.7, 1.4), (0, 1.5), 20), cubic((0, 1.5), (0.7, 1.4), (0.5, 0.0), (0.9, -0.3), 20), [(-0.9, -0.3)])
    yoke = [[(-1.3, 1.6), (1.3, 1.6)], [(0, 1.5), (0, 1.6)]]
    clapper = circle(0, -0.45, 0.15, 14)
    rope = [[(0, -0.6), (0, -2.4)]]
    bands = [quad((-0.75, 0.0), (0, 0.1), (0.75, 0.0))]
    stones = [[(-1.8, y), (1.8, y)] for y in (-1.2, -1.9, -2.6)] + [[(x, -1.2), (x, -1.9)] for x in (-0.6, 0.6)]
    return make("Bell Tower", [tower, arch, roof, cr, bell, clapper, bands[0]] + yoke + rope + stones)


@design("faith_rosary", T)
def rosary(rng):
    path = [(2.2 * math.sin(t), 1.0 + 1.8 * math.cos(t) - 0.25 * math.cos(2 * t)) for t in [TAU * i / 600 for i in range(601)]]
    pts = resample(path, 34)
    beads = []
    for k, (x, y) in enumerate(pts):
        if k in (16, 17, 18):
            continue
        beads.append(circle(x, y, 0.2 if k % 8 else 0.26, 16))
    medal = [ellipse(0, -1.05, 0.35, 0.42, 24), heart(0, -1.05, 0.18, 30)]
    drop_ = [circle(0, -1.85 - 0.45 * k, 0.18, 14) for k in range(3)]
    cr = cross(0, -3.75, 1.6, w=1.0, t=0.25)
    return make("Rosary Beads", beads + medal + drop_ + [cr])


@design("faith_easter_lilies", T)
def easter_lilies(rng):
    def lily(x, y, a, s):
        def P(u, v):
            c, n = math.cos(a), math.sin(a)
            return (x + (u * c - v * n) * s, y + (u * n + v * c) * s)
        trumpet = chain([P(-0.15, 0)], [P(-0.5, 1.4)], quad(P(-0.5, 1.4), P(-1.1, 1.5), P(-1.2, 2.0), 8), quad(P(-1.2, 2.0), P(-0.6, 1.8), P(-0.3, 2.2), 8),
                        quad(P(-0.3, 2.2), P(0, 2.6), P(0.3, 2.2), 8), quad(P(0.3, 2.2), P(0.6, 1.8), P(1.2, 2.0), 8),
                        quad(P(1.2, 2.0), P(1.1, 1.5), P(0.5, 1.4), 8), [P(0.15, 0)])
        vein = [P(0, 0.2), P(0, 1.9)]
        stam = [[P(-0.1, 1.6), P(-0.25, 2.3)], [P(0.1, 1.6), P(0.25, 2.3)]]
        return [trumpet, vein] + stam
    out = lily(-1.2, 0.0, R(30), 1.0) + lily(0.3, 0.6, R(-5), 1.1) + lily(1.6, -0.2, R(-35), 0.95)
    stems = [cubic((0.0, -3.0), (0.0, -1.5), (-0.8, -0.5), (-1.12, 0.05), 20), cubic((0.0, -3.0), (0.2, -1.0), (0.3, 0.0), (0.3, 0.6), 20),
             cubic((0.0, -3.0), (0.4, -1.5), (1.2, -0.9), (1.55, -0.15), 20)]
    leaves = [lens((0.05, -2.2), (-1.6, -1.6), 0.18), lens((0.15, -1.8), (1.8, -1.6), 0.18), lens((0.1, -2.7), (-1.4, -2.9), 0.16)]
    return make("Easter Lilies", out + stems + leaves)


@design("faith_mustard_tree", T)
def mustard_tree(rng):
    trunk = poly((-0.5, -2.6), (-0.35, -0.4), (-1.4, 0.6), (-1.1, 0.75), (-0.1, 0.0), (0.0, 1.2), (0.3, 1.2), (0.3, 0.1), (1.3, 0.8), (1.5, 0.55),
                 (0.4, -0.4), (0.5, -2.6), closed=False)
    canopy = cloud(0, 1.4, 6.2, 3.0, k=13)
    birds = []
    for x, y, s in [(-1.6, 1.4, 0.35), (1.2, 2.1, 0.35), (-0.4, 2.5, 0.3), (2.6, 3.4, 0.35), (-2.6, 3.3, 0.3)]:
        birds.append(chain(quad((x - s, y), (x - s / 2, y + s * 0.6), (x, y), 8), quad((x, y), (x + s / 2, y + s * 0.6), (x + s, y), 8)))
    nest = [ellipse(0.9, 0.7, 0.45, 0.15, 20), arc(0.9, 0.7, 0.45, R(180), R(360), 12)]
    ground = [quad((-3.0, -2.6), (0, -2.4), (3.0, -2.6))]
    seed = [circle(-2.4, -2.0, 0.15, 12), arc(-2.4, -2.0, 0.45, R(200), R(340), 12)]
    return make("Mustard Seed Tree", [trunk, canopy] + birds + nest + ground + seed)


def grape_cluster(cx, cy, s):
    out = []
    rows = [4, 4, 3, 3, 2, 1]
    for r, n in enumerate(rows):
        for k in range(n):
            out.append(circle(cx + (k - (n - 1) / 2) * 0.48 * s, cy - r * 0.42 * s, 0.24 * s, 18))
    return out


@design("faith_vine_branches", T)
def vine_branches(rng):
    vine = cubic((-3.4, 2.4), (-1.0, 2.8), (1.0, 1.6), (3.4, 2.6), 50)
    g = grape_cluster(-0.8, 1.6, 1.0) + grape_cluster(1.8, 1.7, 0.8)
    stems = [[(-0.8, 1.85), (-0.7, 2.45)], [(1.8, 1.9), (1.9, 2.0)]]

    def vleaf(cx, cy, s, rot):
        pts = polar(lambda t: s * (0.7 + 0.3 * abs(math.cos(2.5 * t)) + 0.04 * abs(math.sin(15 * t))), n=200, cx=cx, cy=cy, rot=rot)
        veins = [[(cx, cy), (cx + 0.8 * s * math.cos(rot + R(a)), cy + 0.8 * s * math.sin(rot + R(a)))] for a in (0, 72, -72, 144, -144)]
        return [pts] + veins
    leaves = vleaf(-2.5, 1.3, 0.95, R(-120)) + vleaf(0.5, 3.15, 0.6, R(80)) + vleaf(2.95, 1.0, 0.75, R(-60))
    tendrils = [spiral(-1.6, 3.0, 0.05, 0.35, 1.5, 40), spiral(2.6, 3.0, 0.05, 0.3, -1.5, 40)]
    return make("The Vine and the Branches", [vine] + g + stems + leaves + tendrils)


@design("faith_oil_lamp", T)
def oil_lamp(rng):
    body = chain([(-2.8, -0.2)], cubic((-2.8, -0.2), (-2.6, -1.3), (-0.4, -1.4), (0.6, -0.9), 30), cubic((0.6, -0.9), (1.4, -0.5), (2.4, -0.6), (2.8, -0.2), 20),
                 cubic((2.8, -0.2), (2.4, 0.2), (1.4, 0.0), (0.6, 0.3), 20), cubic((0.6, 0.3), (-0.4, 0.8), (-2.6, 0.7), (-2.8, -0.2), 30))
    hole = ellipse(-0.8, 0.25, 0.4, 0.14, 24)
    handle = chain(arc(-3.1, 0.0, 0.5, R(-60), R(-300), 24))
    flame = chain(cubic((2.6, 0.0), (2.2, 0.6), (2.6, 1.3), (2.9, 1.9), 16), cubic((2.9, 1.9), (3.1, 1.2), (3.2, 0.5), (2.6, 0.0), 16))
    foot = poly((-1.2, -1.15), (-1.0, -1.6), (0.2, -1.6), (0.3, -1.1), closed=False)
    deco = [circle(-1.6, -0.4, 0.18, 14), circle(-0.8, -0.6, 0.18, 14), circle(0.0, -0.5, 0.18, 14)]
    stand = [ellipse(-0.4, -1.75, 2.2, 0.2, 50), [(-0.4, -1.95), (-0.4, -2.8)], ellipse(-0.4, -2.85, 1.0, 0.18, 30)]
    glow = rays(2.85, 1.0, 1.0, 1.6, (20, 60, 100, 140))
    return make("Parable of the Oil Lamp", [body, hole, handle, flame, foot] + deco + stand + glow)


@design("faith_lighthouse", T)
def lighthouse(rng):
    tower = poly((-1.0, -2.0), (-0.6, 1.4), (0.6, 1.4), (1.0, -2.0), closed=False)
    stripes = [[(-0.95 + 0.04 * k, -1.2 + 0.85 * k), (0.95 - 0.04 * k, -1.2 + 0.85 * k)] for k in range(3)]
    gallery = rect(-0.9, 1.4, 0.9, 1.7)
    lamp = rect(-0.5, 1.7, 0.5, 2.5)
    cap = poly((-0.7, 2.5), (0, 3.1), (0.7, 2.5), (-0.7, 2.5))
    cr = cross(0, 3.45, 0.7)
    beams = [poly((0.5, 2.3), (3.6, 2.9), (3.6, 1.7), (0.5, 1.9), closed=False), poly((-0.5, 2.3), (-3.6, 2.9), (-3.6, 1.7), (-0.5, 1.9), closed=False)]
    door = chain([(-0.25, -1.9), (-0.25, -1.5)], arc(0, -1.5, 0.25, math.pi, 0, 8), [(0.25, -1.9)])
    rocks = poly((-2.6, -2.6), (-2.0, -2.0), (-1.0, -2.0), (1.0, -2.0), (1.8, -1.9), (2.6, -2.6), closed=False)
    sea = [wave(-3.6, 3.6, -2.7, 0.12, 6, 100)]
    boat = [poly((-3.4, -2.3), (-2.2, -2.3), (-2.4, -2.6), (-3.2, -2.6)), poly((-2.8, -2.3), (-2.8, -1.4), (-2.3, -2.3))]
    return make("Light of the World", [tower, gallery, lamp, cap, cr, door, rocks] + stripes + beams + sea + boat)


@design("faith_anchor_hope", T)
def anchor_hope(rng):
    shank = rect(-0.18, -2.25, 0.18, 2.0)
    ring = [circle(0, 2.45, 0.45, 30), circle(0, 2.45, 0.22, 20)]
    stock = rrect(-1.4, 1.2, 1.4, 1.55, 0.12)
    arms = [chain(arc(0, -0.6, 2.0, R(180), R(360), 60)), chain(arc(0, -0.6, 1.65, R(180), R(360), 50))]
    flukes = [poly((-2.35, -0.6), (-1.825, 0.3), (-1.3, -0.6)), poly((2.35, -0.6), (1.825, 0.3), (1.3, -0.6))]
    tip = poly((-0.3, -2.45), (0, -2.95), (0.3, -2.45), closed=False)
    h = heart(0, 0.2, 0.5)
    rope = [cubic((0.45, 2.2), (1.6, 1.6), (1.4, 0.6), (0.18, 0.5), 20), cubic((-0.18, -0.2), (-1.4, -0.4), (-1.6, -1.6), (-0.18, -1.7), 20)]
    return make("Anchor of Hope", [shank, stock, tip, h] + ring + arms + flukes + rope)


@design("faith_crook_lantern", T)
def crook_lantern(rng):
    outer = arc(-0.35, 2.05, 0.75, math.pi, R(-40), 30)
    inner = arc(-0.35, 2.05, 0.53, math.pi, R(-40), 26)
    staff = chain([(-1.6, -3.0), (-1.1, 2.05)], outer, inner[::-1], [(-0.88, 2.05), (-1.38, -3.0), (-1.6, -3.0)])
    hang = [(0.2, 1.55), (0.2, 1.1)]
    lantern = [rect(-0.3, -0.9, 0.7, 0.6), poly((-0.45, 0.6), (0.2, 1.1), (0.85, 0.6), (-0.45, 0.6)), rect(-0.45, -1.15, 0.85, -0.9)]
    flame = lens((0.2, -0.6), (0.2, 0.2), 0.3)
    bars = [[(0.2, -0.9), (0.2, -0.65)], [(-0.3, -0.15), (0.0, -0.15)], [(0.4, -0.15), (0.7, -0.15)]]
    glow = rays(0.2, -0.2, 1.2, 1.9, (-35, -10, 15, 40))
    ground = [quad((-3.2, -3.0), (0, -2.7), (3.2, -3.0))]
    grass = [zigzag(1.0, 2.8, -2.7, 0.2, 5), zigzag(-3.0, -2.0, -2.8, 0.2, 3)]
    star_ = [star(-2.6, 2.4, 0.35), star(2.4, 2.6, 0.3)]
    return make("Shepherd's Crook and Lantern", [staff, hang, flame] + lantern + bars + glow + ground + grass + star_)


@design("faith_wheat_sheaf", T)
def wheat_sheaf(rng):
    # Five well-spaced stalks: the old nine-stalk sheaf crowded its dots.
    stalks, heads = [], []
    for k in range(-2, 3):
        a = R(90 - k * 14)
        base = (k * 0.3, 0.0)
        top = (k * 0.3 + 2.3 * math.cos(a), 2.3 * math.sin(a))
        stalks.append([base, top])
        stalks.append([(k * 0.3, -0.6), (k * 0.65, -2.8)])
        for j in range(4):
            px = top[0] + 0.32 * j * math.cos(a)
            py = top[1] + 0.32 * j * math.sin(a)
            heads.append(lens((px, py), (px + 0.38 * math.cos(a + 0.6), py + 0.38 * math.sin(a + 0.6)), 0.35))
            heads.append(lens((px, py), (px + 0.38 * math.cos(a - 0.6), py + 0.38 * math.sin(a - 0.6)), 0.35))
    tie = [rrect(-0.85, -0.6, 0.85, 0.0, 0.1), lens((0, -0.3), (-0.9, -1.2), 0.3), lens((0, -0.3), (0.9, -1.2), 0.3)]
    return make("Sheaf of Wheat", stalks + heads + tie)


@design("faith_scroll", T)
def scroll(rng):
    sheet = chain([(-2.2, -2.2)], cubic((-2.2, -2.2), (-2.0, -0.8), (-2.4, 0.8), (-2.2, 2.2), 20), [(2.2, 2.2)],
                  cubic((2.2, 2.2), (2.4, 0.8), (2.0, -0.8), (2.2, -2.2), 20), [(-2.2, -2.2)])
    rollers = [rrect(-2.7, -2.6, 2.7, -2.0, 0.3), rrect(-2.7, 2.0, 2.7, 2.6, 0.3)]
    knobs = [circle(x, y, 0.22, 16) for x in (-3.0, 3.0) for y in (-2.3, 2.3)]
    rod = [[(-3.4, y), (-2.7, y)] for y in (-2.3, 2.3)] + [[(2.7, y), (3.4, y)] for y in (-2.3, 2.3)]
    lines_ = [wave(-1.6, 1.6, y, 0.04, 4, 40) for y in (1.3, 0.8, 0.3, -0.2, -0.7, -1.2)]
    seal = [circle(1.4, -1.6, 0.3, 20)]
    return make("Ancient Scroll", [sheet] + rollers + knobs + rod + lines_ + seal)


@design("faith_praying_child", T)
def praying_child(rng):
    head = circle(0.2, 1.45, 0.55, 50)
    hair = chain(arc(0.2, 1.45, 0.66, R(-10), R(215), 40), [(-0.25, 1.2)])
    body = chain([(-0.2, 0.92)], cubic((-0.2, 0.92), (-0.6, 0.6), (-0.7, -0.3), (-0.5, -1.2), 16), [(-1.7, -1.2)], [(-1.85, -1.6), (0.55, -1.6), (0.55, -0.7)],
                 cubic((0.55, -0.7), (0.6, 0.0), (0.55, 0.6), (0.45, 0.95), 12))
    arm = tube([(0.35, 0.7), (0.4, -0.05), (0.95, 0.55)], 0.24)
    hands = lens((0.9, 0.45), (1.2, 1.15), 0.3)
    closed_eye = arc(0.55, 1.5, 0.1, R(200), R(340), 8)
    bed = [rect(1.5, -1.6, 3.6, -0.2), rrect(1.7, -0.2, 3.4, 0.35, 0.2), [(1.5, -1.6), (1.5, -2.2)], [(3.6, -1.6), (3.6, -2.2)]]
    blanket = [quad((1.5, -0.6), (2.6, -0.9), (3.6, -0.6))]
    window = [rect(-3.2, 0.6, -1.6, 2.6), [(-2.4, 0.6), (-2.4, 2.6)], [(-3.2, 1.6), (-1.6, 1.6)]]
    moon = [chain(arc(-2.85, 2.1, 0.28, R(70), R(290), 14), arc(-2.7, 2.1, 0.22, R(-70), R(70), 10))]
    floor = [(-3.4, -1.6), (1.5, -1.6)]
    return make("Child at Bedtime Prayer", [head, hair, body, arm, hands, closed_eye, floor] + bed + blanket + window + moon + [star(-1.95, 1.2, 0.2)])


@design("faith_dove_descending", T)
def dove_descending(rng):
    body = chain(arc(0, 0.6, 0.45, R(20), R(160), 12), cubic((-0.42, 0.75), (-0.5, -0.6), (-0.3, -1.0), (0, -1.6), 16),
                 cubic((0, -1.6), (0.3, -1.0), (0.5, -0.6), (0.42, 0.75), 16))
    tail = poly((-0.3, 0.9), (-0.6, 2.2), (-0.2, 2.0), (0, 2.25), (0.2, 2.0), (0.6, 2.2), (0.3, 0.9), closed=False)
    lead = cubic((-0.42, 0.4), (-1.2, 1.6), (-2.4, 2.4), (-3.4, 2.8), 30)
    knots = [(-3.4, 2.8), (-3.0, 1.9), (-2.4, 1.2), (-1.7, 0.6), (-1.0, 0.0), (-0.42, -0.4)]
    trail = []
    for a, b in zip(knots, knots[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        c = ((a[0] + b[0]) / 2 + 0.35 * dy, (a[1] + b[1]) / 2 - 0.35 * dx)
        trail += quad(a, c, b, 10)
    wing = chain(lead, trail)
    quills = [quad((-0.9, 0.6), (-1.6, 1.2), (-2.6, 1.9)), quad((-0.8, 0.2), (-1.4, 0.6), (-1.9, 0.9))]
    wings = [wing, mirror_x(wing)] + quills + mirror_all(quills)
    beak = poly((-0.12, -1.45), (0, -1.85), (0.12, -1.45), closed=False)
    rays_ = rays(0, -0.4, 1.5, 3.2, (215, 240, 260, 280, 300, 325))
    return make("Dove Descending", [body, tail, beak] + wings + rays_, [eye(-0.18, -1.15, 0.06), eye(0.18, -1.15, 0.06)])


def camel(dx, dy, s):
    pts = poly((-1.0, 0.35), (-0.95, 0.55), (-0.7, 0.85), (-0.35, 1.1), (0.0, 0.9), (0.25, 0.65), (0.55, 0.65), (0.8, 1.15), (0.95, 1.35),
               (1.25, 1.33), (1.32, 1.18), (0.98, 1.08), (0.82, 0.45), (0.62, 0.1), (0.6, -0.95), (0.48, -0.95), (0.45, -0.1), (0.25, -0.15),
               (0.2, -0.95), (0.08, -0.95), (0.05, -0.15), (-0.45, -0.1), (-0.5, -0.95), (-0.62, -0.95), (-0.68, 0.0), (-0.8, -0.95), (-0.92, -0.95),
               (-0.9, 0.2))
    rider = [circle(-0.3, 1.75, 0.16, 14), poly((-0.55, 1.05), (-0.3, 1.58), (-0.05, 1.05), closed=False),
             poly((-0.45, 1.9), (-0.4, 2.1), (-0.3, 1.95), (-0.2, 2.1), (-0.15, 1.9), closed=False)]
    return [transform(p, dx=dx, dy=dy, s=s) for p in [pts] + rider]


@design("faith_wise_men", T)
def wise_men(rng):
    c = camel(-1.8, -1.0, 1.1) + camel(0.3, -0.5, 0.85) + camel(2.2, -0.1, 0.65)
    dunes = [quad((-3.6, -2.2), (-1.0, -1.6), (1.0, -2.2), 20), quad((0.0, -1.4), (2.0, -0.6), (3.6, -1.2), 20), [(-3.6, -2.2), (3.6, -2.2)]]
    st = star(-2.4, 2.4, 0.6, n=8, inner=0.35)
    trail = rays(-2.4, 2.4, 0.75, 1.3, (-20, -45, -70))
    return make("Three Wise Men", c + dunes + [st] + trail)


@design("faith_fishers_boat", T)
def fishers_boat(rng):
    hull = chain([(-3.0, 0.4)], cubic((-3.0, 0.4), (-2.4, -1.2), (2.0, -1.2), (3.0, 0.6), 40), [(-3.0, 0.4)])
    rail = quad((-2.8, 0.15), (0, -0.2), (2.8, 0.35))
    mast = [(-0.4, -0.05), (-0.4, 3.0)]
    sail = chain([(-0.4, 2.8)], quad((-0.4, 2.8), (1.4, 2.3), (1.8, 0.6), 16), [(-0.4, 0.6)])
    yard = [(-0.4, 2.8), (1.0, 3.0)]
    A, B, Cc, D = (1.5, 0.05), (2.7, 0.35), (3.5, -2.6), (1.0, -2.8)
    net = [poly(A, B, Cc, D)]
    for k in range(1, 5):
        f = k / 5
        net.append([(A[0] + f * (B[0] - A[0]), A[1] + f * (B[1] - A[1])), (D[0] + f * (Cc[0] - D[0]), D[1] + f * (Cc[1] - D[1]))])
    for k in range(1, 5):
        f = k / 5
        net.append([(A[0] + f * (D[0] - A[0]), A[1] + f * (D[1] - A[1])), (B[0] + f * (Cc[0] - B[0]), B[1] + f * (Cc[1] - B[1]))])
    fishes, hs = [], []
    for x, y in [(2.1, -1.0), (2.6, -2.0)]:
        f, h = fish(x, y, 0.35)
        fishes += f
        hs += h
    sea = [wave(-3.6, 0.9, -1.0, 0.12, 4, 80), wave(-3.4, 0.7, -1.7, 0.1, 4, 70), wave(-3.0, 0.5, -2.4, 0.1, 3, 60)]
    return make("Fishers of Men", [hull, rail, mast, sail, yard] + net + fishes + sea, hs)


def frond(base, tip, n=14, side=0.7, bend=0.25, start=2):
    bx, by = base
    tx, ty = tip
    mx, my = (bx + tx) / 2, (by + ty) / 2
    dx, dy = tx - bx, ty - by
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    ctrl = (mx + nx * bend * L, my + ny * bend * L)
    spine = quad(base, ctrl, tip, 40)
    out = [spine]
    for k in range(start, n):
        i = int(40 * k / n)
        x, y = spine[i]
        x2, y2 = spine[min(40, i + 1)]
        ax, ay = x2 - x, y2 - y
        al = math.hypot(ax, ay)
        ax, ay = ax / al, ay / al
        ln = side * math.sin(math.pi * k / n) + 0.1
        for sgn in (1, -1):
            ex = x + (ax * 0.6 + sgn * -ay) * ln
            ey = y + (ay * 0.6 + sgn * ax) * ln
            out.append([(x, y), (ex, ey)])
    return out


@design("faith_palm_branches", T)
def palm_branches(rng):
    a = frond((0.3, -2.8), (-2.8, 2.8), n=18, side=0.85, bend=-0.12, start=7)
    b = frond((-0.3, -2.8), (2.8, 2.8), n=18, side=0.85, bend=0.12, start=7)
    ribbon = [lens((0, -2.2), (-0.9, -2.9), 0.35), lens((0, -2.2), (0.9, -2.9), 0.35), circle(0, -2.2, 0.2, 14)]
    return make("Palm Sunday Branches", a + b + ribbon)


@design("faith_lion_lamb", T)
def lion_lamb(rng):
    body = chain([(-0.3, -1.6), (-2.6, -1.6)], cubic((-2.6, -1.6), (-3.3, -1.4), (-3.2, 0.2), (-1.8, 0.3), 30),
                 cubic((-1.8, 0.3), (-1.2, 0.4), (-0.7, 0.3), (-0.4, 0.5), 12))
    mane = bumpy(0.3, 0.4, 1.15, 1.2, k=14, amp=0.12, n=140)
    face = ellipse(0.5, 0.3, 0.6, 0.7, 40)
    nose = poly((0.85, 0.15), (1.1, 0.15), (0.98, -0.05))
    mouth = quad((0.98, -0.05), (0.85, -0.3), (0.65, -0.25))
    ears = [arc(0.2, 0.95, 0.18, R(0), R(180), 8), arc(0.75, 0.95, 0.18, R(0), R(180), 8)]
    paws = [chain([(-0.2, -0.75), (1.4, -0.75)], arc(1.4, -0.95, 0.2, R(90), R(-90), 8), [(-0.1, -1.15)]),
            chain([(-0.1, -1.2), (1.7, -1.2)], arc(1.7, -1.4, 0.2, R(90), R(-90), 8), [(-0.3, -1.6)])]
    tail = [cubic((-2.9, -1.0), (-3.6, -1.6), (-3.6, -0.2), (-3.3, 0.6), 20), bumpy(-3.25, 0.75, 0.18, 0.25, k=6, amp=0.3, n=40)]
    lamb, h = sheep(2.55, -0.9, 0.95, d=-1, lying=True)
    ground = [(-3.6, -1.62), (3.6, -1.62)]
    return make("The Lion and the Lamb", [body, mane, face, nose, mouth, ground] + ears + paws + tail + lamb,
                h + [eye(0.4, 0.5, 0.07), eye(0.8, 0.5, 0.07)])


@design("faith_heart_dove", T)
def heart_dove(rng):
    big = heart(0, 0.2, 2.8, n=160)
    d, h = dove_side(-0.3, -0.3, 0.7)
    return make("Heart with Dove", [big, heart(0, 0.2, 2.45, n=150)] + d, h)


@design("faith_alpha_omega", T)
def alpha_omega(rng):
    A = poly((-3.4, -2.0), (-2.9, -2.0), (-2.65, -1.2), (-1.65, -1.2), (-1.4, -2.0), (-0.9, -2.0), (-1.9, 2.0), (-2.4, 2.0))
    Ai = poly((-2.5, -0.75), (-1.8, -0.75), (-2.15, 0.7))
    om = chain([(0.9, -2.0), (1.9, -2.0), (1.9, -1.6)], arc(2.15, 0.2, 1.75, R(-115), R(295), 80),
               [(2.4, -1.6), (2.4, -2.0), (3.4, -2.0), (3.4, -1.6), (2.75, -1.6)],
               arc(2.15, 0.2, 1.3, R(-72), R(252), 70), [(1.55, -1.6), (0.9, -1.6), (0.9, -2.0)])
    cr = cross(0, 2.6, 1.2)
    rays_ = rays(0, 2.75, 0.8, 1.2, (0, 30, 150, 180))
    return make("Alpha and Omega", [A, Ai, om, cr] + rays_)


@design("faith_baptism_shell", T)
def baptism_shell(rng):
    n = 9
    outline = []
    for k in range(n):
        a0 = R(15 + 150 * k / n)
        a1 = R(15 + 150 * (k + 1) / n)
        p0 = (2.6 * math.cos(a0), -1.6 + 2.6 * math.sin(a0))
        p1 = (2.6 * math.cos(a1), -1.6 + 2.6 * math.sin(a1))
        am = (a0 + a1) / 2
        c = (3.0 * math.cos(am), -1.6 + 3.0 * math.sin(am))
        outline += quad(p0, c, p1, 8)
    shell = chain(outline, [(-0.6, -2.4), (0.6, -2.4), outline[0]])
    ribs = [[(0, -2.0), (2.6 * math.cos(R(15 + 150 * k / n)), -1.6 + 2.6 * math.sin(R(15 + 150 * k / n)))] for k in range(1, n)]
    ear = [rect(-0.6, -2.4, 0.6, -2.0)]
    drops = [drop(x, y, 0.25) for x, y in [(0, 2.1), (-0.8, 1.6), (0.8, 1.6)]]
    return make("Baptism Shell", [shell] + ribs + ear + drops)


@design("faith_house_rock", T)
def house_rock(rng):
    rock = poly((-3.0, -2.8), (-2.6, -1.0), (-1.8, -0.6), (-0.4, -0.5), (1.2, -0.5), (2.0, -0.9), (2.6, -2.0), (2.8, -2.8), closed=False)
    cracks = [[(-1.8, -0.6), (-1.5, -1.6)], [(1.2, -0.5), (1.5, -1.5), (1.2, -2.0)], [(-0.4, -0.5), (-0.2, -1.2)]]
    house = rect(-1.4, -0.5, 1.0, 1.0)
    roof = poly((-1.8, 0.9), (-0.2, 2.2), (1.4, 0.9), closed=False)
    door = rect(-0.4, -0.5, 0.2, 0.4)
    win = [rect(-1.15, 0.2, -0.65, 0.65), rect(0.45, 0.2, 0.85, 0.65)]
    chim = poly((0.6, 1.5), (0.6, 2.0), (0.95, 2.0), (0.95, 1.2), closed=False)
    waves_ = [chain([(-3.6, -2.0)], cubic((-3.6, -2.0), (-3.6, -0.8), (-2.6, -0.8), (-2.6, -1.4), 16)),
              wave(-3.6, 3.6, -2.9, 0.12, 6, 100), cubic((3.6, -1.8), (3.6, -0.8), (2.7, -0.8), (2.8, -1.5), 16)]
    clouds = [cloud(-2.2, 2.6, 2.4, 0.9, k=6), cloud(2.2, 2.8, 2.2, 0.8, k=6)]
    rain = [[(x, 1.9), (x - 0.25, 1.3)] for x in (-3.0, -2.4, -1.8, 1.6, 2.2, 2.8)]
    return make("House on the Rock", [rock, house, roof, door, chim] + cracks + win + waves_ + clouds + rain)


@design("faith_ark_covenant", T)
def ark_covenant(rng):
    chest = rect(-2.2, -1.6, 2.2, 0.2)
    lid = rect(-2.4, 0.2, 2.4, 0.55)
    panel = rect(-1.8, -1.2, 1.8, -0.2)
    legs_ = [rect(-2.1, -2.2, -1.7, -1.6), rect(1.7, -2.2, 2.1, -1.6)]
    poles = [rrect(-3.6, -1.0, 3.6, -0.7, 0.15)]

    def cherub(d):
        body = poly((d * 0.55, 0.55), (d * 0.65, 1.2), (d * 1.0, 1.25), (d * 1.35, 1.35), (d * 1.7, 0.95), (d * 2.0, 0.55), closed=False)
        head = circle(d * 0.72, 1.48, 0.25, 18)
        lead = cubic((d * 1.35, 1.35), (d * 2.0, 2.1), (d * 1.6, 2.7), (d * 0.12, 2.55), 30)
        knots = [(d * 0.12, 2.55), (d * 0.5, 2.2), (d * 0.85, 2.0), (d * 1.15, 1.8), (d * 1.35, 1.35)]
        trail = []
        for a, b in zip(knots, knots[1:]):
            c = ((a[0] + b[0]) / 2 - d * 0.1, (a[1] + b[1]) / 2 - 0.14)
            trail += quad(a, c, b, 8)
        arm = [(d * 0.95, 1.0), (d * 0.35, 1.05)]
        return [body, head, chain(lead, trail), arm]
    deco = [circle(0, -0.7, 0.3, 20)] + [circle(x, -0.7, 0.15, 12) for x in (-1.2, -0.6, 0.6, 1.2)]
    return make("Ark of the Covenant", [chest, lid, panel] + legs_ + poles + cherub(-1) + cherub(1) + deco)


@design("faith_menorah", T)
def menorah(rng):
    stem = [rect(-0.15, -1.8, 0.15, 1.0)]
    branches = []
    for k, r in enumerate((0.8, 1.6, 2.4)):
        branches.append(arc(0, 1.0, r, R(180), R(360), 30))
        branches.append(arc(0, 1.0, r + 0.25, R(180), R(360), 30))
    cups = []
    for x in (-2.525, -1.725, -0.925, 0.0, 0.925, 1.725, 2.525):
        cups.append(poly((x - 0.25, 1.0), (x - 0.18, 1.3), (x + 0.18, 1.3), (x + 0.25, 1.0)))
        cups.append(lens((x, 1.35), (x, 2.1), 0.3))
    base = [poly((-0.15, -1.8), (-1.2, -2.6), (1.2, -2.6), (0.15, -1.8), closed=False), ellipse(0, -2.7, 1.5, 0.15, 40)]
    knobs = [ellipse(0, y, 0.3, 0.12, 16) for y in (-1.2, -0.4)]
    return make("Temple Menorah", stem + branches + cups + base + knobs)


@design("faith_jericho", T)
def jericho(rng):
    wall = chain([(-3.4, -2.4), (-3.4, 1.0), (-3.1, 1.0), (-3.1, 0.8), (-2.8, 0.8), (-2.8, 1.0), (-2.5, 1.0), (-2.5, 0.8), (-2.2, 0.8), (-2.2, 1.0), (-1.9, 1.0),
                  (-1.9, 0.0), (-1.3, 0.4), (-1.0, -0.4), (-0.4, 0.1), (0.0, -0.6), (0.6, 0.0), (0.9, -0.2), (0.9, 0.2), (1.2, 0.2), (1.2, 0.0),
                  (1.5, 0.0), (1.5, 0.2), (1.8, 0.2), (1.8, -2.4)])
    bricks = [[(-3.4, y), (-1.9, y)] for y in (-0.2, -1.0, -1.8)] + [[(-1.0, y), (1.8, y)] for y in (-1.0, -1.8)] + \
             [[(x, -1.0), (x, -1.8)] for x in (-2.6, -0.2, 1.0)] + [[(x, -1.8), (x, -2.4)] for x in (-3.0, -1.4, 0.4)]
    rubble = [poly((-1.6, -2.4), (-1.4, -1.9), (-1.0, -2.0), (-0.9, -2.4)), poly((2.0, -2.4), (2.1, -2.0), (2.5, -2.1), (2.6, -2.4))]
    path = cubic((-0.6, 1.4), (0.6, 1.0), (2.0, 1.4), (2.9, 3.0), 30)
    horn = tube(path, lambda t: 0.18 + 0.55 * t * t)
    rings = []
    for i in (8, 15, 22):
        (x, y), (x2, y2) = path[i], path[i + 1]
        a = math.atan2(y2 - y, x2 - x) + math.pi / 2
        w = (0.18 + 0.55 * (i / 30) ** 2) / 2
        rings.append([(x + w * math.cos(a), y + w * math.sin(a)), (x - w * math.cos(a), y - w * math.sin(a))])
    mouth = ellipse(2.9, 3.0, 0.38, 0.15, 24, rot=R(-35))
    notes = rays(2.9, 3.0, 0.6, 1.0, (-10, -40, 200))
    ground = [(-3.6, -2.4), (3.6, -2.4)]
    return make("Walls of Jericho", [wall, horn, mouth, ground] + bricks + rubble + rings)


@design("faith_church_doors", T)
def church_doors(rng):
    outer = chain([(-2.6, -3.0), (-2.6, 0.6)], arc(0, 0.6, 2.6, math.pi, 0, 50), [(2.6, -3.0)])
    mid = chain([(-2.1, -3.0), (-2.1, 0.6)], arc(0, 0.6, 2.1, math.pi, 0, 44), [(2.1, -3.0)])
    door = chain([(-1.6, -3.0), (-1.6, 0.6)], arc(0, 0.6, 1.6, math.pi, 0, 40), [(1.6, -3.0)])
    split = [(0, -3.0), (0, 2.2)]
    hinges = [poly((x0, y), (x1, y), (x1, y + 0.2), (x0, y + 0.2)) for y in (-2.4, -0.4) for x0, x1 in ((-1.6, -0.6), (1.6, 0.6))]
    handles = [circle(-0.3, -1.2, 0.15, 12), circle(0.3, -1.2, 0.15, 12)]
    win = circle(0, 1.2, 0.5, 30)
    cr = cross(0, 1.2, 0.7)
    steps = [[(-3.2, -3.0), (3.2, -3.0)], [(-3.2, -3.0), (-3.2, -3.3), (3.2, -3.3), (3.2, -3.0)]]
    return make("Church Doors", [outer, mid, door, split, win, cr] + hinges + handles + steps)


@design("faith_garden_eden", T)
def garden_eden(rng):
    trunk = poly((-0.5, -2.8), (-0.35, -0.2), (-1.2, 0.6), (-0.9, 0.7), (0.0, 0.1), (0.9, 0.7), (1.2, 0.6), (0.35, -0.2), (0.5, -2.8), closed=False)
    canopy = cloud(0, 1.6, 5.4, 3.0, k=11)
    ap = [(-1.6, 1.4), (-0.4, 2.2), (0.9, 1.9), (1.8, 2.4), (-0.2, 1.1), (-1.0, 2.7)]
    apples = [circle(x, y, 0.25, 18) for x, y in ap]
    stems = [[(x, y + 0.25), (x + 0.08, y + 0.4)] for x, y in ap]
    sp = cubic((1.6, 0.85), (2.4, 0.4), (1.0, -0.4), (1.9, -1.2), 30)
    snake = tube(sp, lambda t: 0.26 - 0.1 * t)
    head = ellipse(2.1, -1.35, 0.3, 0.2, 20, rot=-0.5)
    tongue = [(2.35, -1.55), (2.55, -1.75)]
    ground = [quad((-3.2, -2.8), (0, -2.5), (3.2, -2.8))]
    flowers = [star(x, -2.45, 0.25, n=5, inner=0.5) for x in (-2.4, -1.6, 2.4)]
    return make("Garden of Eden", [trunk, canopy, snake, head, tongue] + apples + stems + ground + flowers, [eye(2.15, -1.28, 0.04)])


@design("faith_baby_manger", T)
def baby_manger(rng):
    box = poly((-2.6, 0.0), (2.6, 0.0), (1.9, -1.3), (-1.9, -1.3))
    planks = [[(-2.3, -0.45), (2.3, -0.45)], [(-2.05, -0.9), (2.05, -0.9)]]
    legs_ = [[(-2.4, -0.3), (-1.0, -2.6)], [(-1.0, -0.6), (-2.4, -2.6)], [(2.4, -0.3), (1.0, -2.6)], [(1.0, -0.6), (2.4, -2.6)]]
    hay = zigzag(-2.6, 2.6, 0.1, 0.15, 13)
    body = rrect(-1.6, 0.3, 0.85, 1.2, 0.45)
    head = circle(1.3, 0.8, 0.45, 30)
    wraps = [[(-0.9, 0.3), (-0.5, 1.2)], [(-0.2, 0.3), (0.2, 1.2)]]
    halo = arc(1.3, 0.8, 0.75, R(-50), R(130), 24)
    st = star(0, 2.6, 0.6, n=8, inner=0.35)
    beams = [[(0, 1.95), (0, 1.55)], [(-0.4, 2.1), (-1.0, 1.6)], [(0.4, 2.1), (1.0, 1.6)]]
    return make("Baby in the Manger", [box, hay, body, head, halo, st] + planks + legs_ + wraps + beams)


def drop(x, y, r):
    return chain(arc(x, y, r, R(150), R(390), 14), [(x, y + 2.2 * r)], [(x + r * math.cos(R(150)), y + r * math.sin(R(150)))])


def resample(pts, k):
    """k points evenly spaced by arc length along pts."""
    d = [0.0]
    for a, b in zip(pts, pts[1:]):
        d.append(d[-1] + math.dist(a, b))
    out, j = [], 0
    for i in range(k):
        s = d[-1] * i / k
        while d[j + 1] < s:
            j += 1
        f = (s - d[j]) / ((d[j + 1] - d[j]) or 1)
        out.append((pts[j][0] + f * (pts[j + 1][0] - pts[j][0]), pts[j][1] + f * (pts[j + 1][1] - pts[j][1])))
    return out


def flame_outline(x0, x1, y0, tips):
    """Flame tongues from (x0, y0) to (x1, y0); tips = [(x, y), ...] left to right."""
    pts = [(x0, y0)]
    for k, (tx, ty) in enumerate(tips):
        nx = tips[k + 1][0] if k + 1 < len(tips) else x1
        vx = (tx + nx) / 2
        vy = y0 if k + 1 == len(tips) else y0 + 0.45 * min(ty, tips[k + 1][1]) - 0.45 * y0
        px, py = pts[-1]
        pts += cubic((px, py), (px - 0.1, py + 0.5 * (ty - py)), (tx - 0.35, ty - 0.5), (tx, ty), 12)[1:]
        nxp = x1 if k + 1 == len(tips) else vx
        pts += cubic((tx, ty), (tx + 0.05, ty - 0.5), (nxp - 0.2, vy + 0.3), (nxp, vy), 12)[1:]
    return pts


@design("faith_olive_branch", T)
def olive_branch(rng):
    stem = cubic((-3.0, -2.8), (-1.2, -1.6), (0.4, 0.6), (2.8, 2.6), 80)
    leaves, olives = [], []
    for k, i in enumerate(range(8, 80, 8)):
        x, y = stem[i]
        x2, y2 = stem[i + 1]
        a = math.atan2(y2 - y, x2 - x)
        for sgn in (1, -1):
            b = a + sgn * 0.75
            L = 1.1 - 0.04 * k
            leaves.append(lens((x, y), (x + L * math.cos(b), y + L * math.sin(b)), 0.16))
        if k in (2, 5):
            ox, oy = x + 0.45 * math.cos(a - 1.9), y + 0.45 * math.sin(a - 1.9)
            olives += [[(x, y), (ox, oy)], ellipse(ox + 0.15, oy - 0.2, 0.2, 0.28, 18, rot=0.4), ellipse(ox - 0.25, oy - 0.1, 0.2, 0.28, 18, rot=-0.3)]
    tip = lens(stem[-1], (stem[-1][0] + 0.7, stem[-1][1] + 0.3), 0.18)
    return make("Olive Branch of Peace", [stem, tip] + leaves + olives)


def dove_side(cx, cy, s):
    """Side-view dove facing right with one wing raised (about 3.5 x 2.6 units at s=1)."""
    knots = [(-0.6, 2.2), (-0.6, 1.65), (-0.5, 1.15), (-0.35, 0.7), (-0.15, 0.38)]
    trail = []
    for a, b in zip(knots, knots[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        c = ((a[0] + b[0]) / 2 + 0.3 * dy, (a[1] + b[1]) / 2 - 0.3 * dx)
        trail += quad(a, c, b, 8)
    wing = chain(cubic((0.45, 0.48), (0.7, 1.3), (0.3, 2.0), (-0.6, 2.2), 24), trail)
    body = chain([(1.55, 0.4), (1.25, 0.52)], arc(0.95, 0.45, 0.32, R(15), R(165), 16),
                 cubic((0.64, 0.53), (0.3, 0.4), (-0.4, 0.35), (-1.0, 0.12), 16), [(-1.9, 0.5), (-1.85, 0.1), (-1.95, -0.3), (-1.0, -0.12)],
                 cubic((-1.0, -0.12), (-0.4, -0.6), (0.6, -0.5), (1.12, 0.2), 16), [(1.3, 0.3), (1.55, 0.4)])
    feather = [quad((0.2, 1.4), (-0.1, 1.2), (-0.3, 1.5), 8), quad((0.25, 0.95), (0.0, 0.8), (-0.2, 1.0), 8)]
    parts = [body, wing] + feather
    return [transform(p, dx=cx, dy=cy, s=s) for p in parts], [eye(cx + 1.0 * s, cy + 0.5 * s, 0.06 * s)]
