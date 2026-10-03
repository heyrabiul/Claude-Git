"""Valentine's Day niche, part 2 (pictures 10-56)."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

T = "valentine"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ------------------------------------------------------------------ occlusion
# hide() removes the parts of strokes that fall inside "cover" shapes, so a
# front object can sit over a back one without lines crossing it; keep() is
# the opposite (clip a pattern to the inside of a shape); union() merges
# overlapping closed shapes into one silhouette.

def _inside(p, pg):
    x, y = p
    c = False
    n = len(pg)
    for i in range(n):
        x1, y1 = pg[i]
        x2, y2 = pg[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def _dense(s, step=0.04):
    out = [s[0]]
    for a, b in zip(s, s[1:]):
        k = max(1, int(math.dist(a, b) / step))
        for i in range(1, k + 1):
            out.append((a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k))
    return out


def _bbox(pg):
    xs = [p[0] for p in pg]
    ys = [p[1] for p in pg]
    return min(xs), min(ys), max(xs), max(ys)


def _clip(strokes, covers, keep_in=False):
    cv = [(c, _bbox(c)) for c in covers if len(c) > 2]

    def gone(p):
        hit = any(b[0] <= p[0] <= b[2] and b[1] <= p[1] <= b[3] and _inside(p, c) for c, b in cv)
        return hit != keep_in

    def edge(a, b):
        for _ in range(14):
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            if gone(m):
                b = m
            else:
                a = m
        return a

    out = []
    for s in strokes:
        if len(s) < 2:
            continue
        closed = math.dist(s[0], s[-1]) < 1e-9
        d = _dense(s)
        fl = [gone(p) for p in d]
        if not any(fl):
            out.append(list(s))
            continue
        segs, cur = [], []
        for i, p in enumerate(d):
            if fl[i]:
                if cur:
                    cur.append(edge(d[i - 1], p))
                    segs.append(cur)
                    cur = []
            else:
                if not cur and i > 0:
                    cur = [edge(p, d[i - 1])]
                cur.append(p)
        if cur:
            segs.append(cur)
        if closed and len(segs) > 1 and not fl[0] and not fl[-1]:
            segs[0] = segs[-1] + segs[0][1:]
            segs.pop()
        out += [g for g in segs if len(g) > 1 and path_len(g) > 0.06]
    return out


def path_len(s):
    return sum(math.dist(a, b) for a, b in zip(s, s[1:]))


def hide(strokes, *covers):
    return _clip(strokes, covers)


def keep(strokes, *covers):
    return _clip(strokes, covers, True)


def join(strokes, tol=0.03):
    segs = [list(s) for s in strokes if len(s) > 1]
    out = []
    while segs:
        cur = segs.pop(0)
        changed = True
        while changed and math.dist(cur[0], cur[-1]) > tol:
            changed = False
            for i, s in enumerate(segs):
                if math.dist(cur[-1], s[0]) < tol:
                    cur = cur + s[1:]
                elif math.dist(cur[-1], s[-1]) < tol:
                    cur = cur + s[::-1][1:]
                elif math.dist(cur[0], s[-1]) < tol:
                    cur = s + cur[1:]
                elif math.dist(cur[0], s[0]) < tol:
                    cur = s[::-1] + cur[1:]
                else:
                    continue
                segs.pop(i)
                changed = True
                break
        if len(cur) > 2 and math.dist(cur[0], cur[-1]) < tol:
            cur[-1] = cur[0]
        out.append(cur)
    return out


def union(*shapes):
    out = []
    for i, s in enumerate(shapes):
        out += hide([s], *[o for j, o in enumerate(shapes) if j != i])
    return join(out)


def flower(cx, cy, r, k=5, rot=0.0):
    c = circle(cx, cy, 0.3 * r, 20)
    petals = [lens((cx, cy), (cx + r * math.cos(a), cy + r * math.sin(a)), 0.32)
              for a in [rot + math.pi / 2 + j * TAU / k for j in range(k)]]
    return hide(petals, c) + [c], petals + [c]


def tulip(cx, cy, s=1.0, rot=0.0):
    cup = chain(cubic((-0.5, 0.55), (-0.68, -0.05), (-0.4, -0.6), (0, -0.6), 16),
                cubic((0, -0.6), (0.4, -0.6), (0.68, -0.05), (0.5, 0.55), 16),
                [(0.25, 0.22), (0, 0.72), (-0.25, 0.22), (-0.5, 0.55)])
    mid = chain(quad((-0.25, 0.22), (-0.22, -0.35), (0, -0.42), 10), quad((0, -0.42), (0.22, -0.35), (0.25, 0.22), 10))
    return [transform(p, cx, cy, s, rot) for p in (cup, mid)], transform(cup, cx, cy, s, rot)


_GLYPH = {
    "L": [[(0, 1), (0, 0), (0.6, 0)]],
    "O": [ellipse(0.3, 0.5, 0.3, 0.5, 30)],
    "V": [[(0, 1), (0.3, 0), (0.6, 1)]],
    "E": [[(0.6, 1), (0, 1), (0, 0), (0.6, 0)], [(0, 0.5), (0.45, 0.5)]],
    "X": [[(0, 1), (0.6, 0)], [(0, 0), (0.6, 1)]],
    "U": [chain([(0, 1), (0, 0.3)], arc(0.3, 0.3, 0.3, math.pi, 2 * math.pi, 12), [(0.6, 1)])],
}


def word(text, cx, cy, h, gap=0.3, rot=0.0):
    """Simple stroke lettering centred on (cx, cy)."""
    width = (len(text) * (0.6 + gap) - gap) * h
    out, x = [], -width / 2
    for ch in text:
        if ch != " ":
            out += [transform(s, x, -h / 2, h) for s in _GLYPH[ch]]
        x += (0.6 + gap) * h
    return [transform(s, cx, cy, rot=rot) for s in out]


def hrt(cx, cy, s, rot=0.0, sy=1.0):
    return transform([(x, y * sy) for x, y in heart(0, 0, s)], cx, cy, rot=rot)


def rose(cx, cy, s=1.0, rot=0.0):
    cup = chain(cubic((-1.0, 0.3), (-1.1, -0.6), (-0.4, -1.0), (0, -1.0), 16), cubic((0, -1.0), (0.4, -1.0), (1.1, -0.6), (1.0, 0.3), 16),
                quad((1.0, 0.3), (0.85, 0.95), (0.15, 0.8), 10), quad((0.15, 0.8), (-0.55, 1.05), (-1.0, 0.3), 10))
    inner = [spiral(0.0, 0.3, 0.05, 0.42, 1.75, 60), quad((-1.0, 0.3), (-0.5, -0.4), (0.4, -0.1), 10), quad((1.0, 0.3), (0.6, -0.5), (-0.25, -0.35), 10)]
    return [transform(p, cx, cy, s, rot) for p in [cup] + inner], transform(cup, cx, cy, s, rot)


def bow(cx, cy, s=1.0):
    loops = [lens((cx, cy), (cx - 0.9 * s, cy + 0.45 * s), 0.42), lens((cx, cy), (cx + 0.9 * s, cy + 0.45 * s), 0.42)]
    knot = circle(cx, cy, 0.15 * s, 12)
    tails = [poly((cx - 0.08 * s, cy - 0.1 * s), (cx - 0.5 * s, cy - 0.85 * s), (cx - 0.22 * s, cy - 0.8 * s), closed=False),
             poly((cx + 0.08 * s, cy - 0.1 * s), (cx + 0.5 * s, cy - 0.85 * s), (cx + 0.22 * s, cy - 0.8 * s), closed=False)]
    return hide(loops, knot) + [knot] + hide(tails, *loops, knot), loops + [knot]


def front_path(pts):
    """The lower ('front') part of a closed outline between its leftmost and rightmost points."""
    pts = pts[:-1] if math.dist(pts[0], pts[-1]) < 1e-9 else pts
    i0 = min(range(len(pts)), key=lambda i: pts[i][0])
    i1 = max(range(len(pts)), key=lambda i: pts[i][0])
    n = len(pts)
    a = [pts[(i0 + k) % n] for k in range((i1 - i0) % n + 1)]
    b = [pts[(i1 + k) % n] for k in range((i0 - i1) % n + 1)][::-1]
    return a if min(p[1] for p in a) < min(p[1] for p in b) else b


# ------------------------------------------------------------------ designs

@design("valentine_cupid", T)
def cupid(rng):
    head = circle(0.2, 1.35, 0.75, 70)
    body = ellipse(0.2, -0.1, 0.85, 0.95, 70)
    legs = [ellipse(-0.25, -1.1, 0.33, 0.6, 30, rot=-0.5), ellipse(0.75, -1.15, 0.33, 0.6, 30, rot=0.4)]
    sil = union(head, body, *legs)
    wing = chain(cubic((0.6, 0.5), (1.4, 1.7), (2.9, 1.7), (2.7, 0.7), 24), arc(2.35, 0.7, 0.35, 0, -math.pi * 0.8, 8),
                 arc(1.8, 0.5, 0.35, -0.2, -math.pi * 0.8, 8), arc(1.25, 0.25, 0.3, -0.2, -math.pi * 0.8, 8), [(0.6, 0.5)])
    wings = [wing, mirror_x(wing, 0.2)]
    wings = hide(wings, head, body, *legs)
    feathers = keep([arc(1.9, 1.0, 0.5, 2.6, 4.0, 8), arc(2.4, 1.1, 0.4, 2.6, 4.0, 8), arc(-1.5, 1.0, 0.5, -0.86, 0.54, 8)], *wings) if False else []
    curl = [spiral(0.2, 2.2, 0.05, 0.25, 1.2, 30)]
    hair = keep([chain(*[arc(-0.35 + 0.28 * k, 1.85, 0.16, 0, math.pi, 8) for k in range(5)])], head)
    sash = keep([quad((-0.7, 0.4), (0.2, -0.3), (1.1, -0.6), 12), quad((-0.7, 0.0), (0.2, -0.65), (1.1, -0.95), 12)], body)
    bowarc = arc(-1.2, 0.1, 1.6, math.radians(140), math.radians(220), 30)
    string = [bowarc[0], bowarc[-1]]
    arrow = [[(-2.65, 0.1), (0.4, 0.1)], hrt(-2.75, 0.12, 0.28, rot=math.pi / 2), poly((0.4, 0.1), (0.75, 0.3), (0.65, 0.1), (0.75, -0.1))]
    arm = tube([(-0.5, 0.2), (-1.6, 0.15)], 0.28)
    hand = circle(-1.7, 0.12, 0.2, 14)
    front = hide([arm], hand, body) + [hand]
    face = [arc(0.2, 1.15, 0.3, math.pi * 1.2, math.pi * 1.8, 10)]
    out = hide(sil + wings + sash, *front[:1], hand) + hide(arrow + [bowarc] + [string], hand, *front[:1]) + front + curl + hair + face
    return make("Little Cupid", out + feathers, [eye(0.0, 1.45, 0.09), eye(0.42, 1.45, 0.09)])


@design("valentine_heart_cake", T)
def heart_cake(rng):
    top = hrt(0, 1.0, 2.2, sy=0.5)
    bot = transform(top, 0, -1.4)
    fp = front_path(bot)
    xs = [p[0] for p in top]
    lx, rx = min(xs), max(xs)
    ly = [p for p in top if p[0] == lx][0][1]
    ry = [p for p in top if p[0] == rx][0][1]
    sides = [[(lx, ly), (lx, ly - 1.4)], [(rx, ry), (rx, ry - 1.4)]]
    drip_base = front_path(transform(top, 0, -0.3))
    drip = [(x, y - 0.25 * max(0.0, math.sin(9 * i / len(drip_base) * math.pi)) ** 2) for i, (x, y) in enumerate(drip_base)]
    piping = [circle(x, y + 0.12, 0.1, 10) for x, y in fp[4::8]]
    deco = [hrt(-0.7, 1.05, 0.35, sy=0.6), hrt(0.7, 1.05, 0.35, sy=0.6), hrt(0, 0.75, 0.45, sy=0.6)]
    candle = [rect(-0.1, 1.0, 0.1, 1.9), poly((0, 1.95), (-0.12, 2.15), (0, 2.45), (0.12, 2.15))]
    plate = hide([ellipse(0, -1.3, 3.0, 0.6, 120)], poly(*fp, (rx, ry), (lx, ly)))
    stand = [poly((-0.4, -1.9), (-0.6, -2.8), (0.6, -2.8), (0.4, -1.9), closed=False), ellipse(0, -2.9, 1.4, 0.22, 50)]
    stand = hide(stand, ellipse(0, -1.3, 3.0, 0.6, 120))
    deco = hide(deco, candle[0])
    return make("Heart-Shaped Cake", [top, fp, drip] + sides + piping + deco + candle + plate + stand)


@design("valentine_conversation_hearts", T)
def conversation_hearts(rng):
    items = [(-1.5, 1.3, 1.2, 0.25, "LOVE"), (1.4, 1.5, 1.1, -0.3, "XO"), (0.0, -0.2, 1.3, 0.0, "LUV"),
             (-1.7, -1.6, 1.0, -0.2, "XOXO"), (1.6, -1.4, 1.1, 0.3, "U")]
    out = []
    for x, y, s, r, txt in items:
        o = hrt(x, y, s, r)
        i = hrt(x, y, s * 0.82, r)
        new = [o, i] + [transform(p, x, y, rot=r) for p in word(txt, 0, -0.05 * s, 0.32 * s if len(txt) > 2 else 0.42 * s)]
        out = hide(out, o) + new
    sparkle = [star(x, y, 0.25, 4, 0.3) for x, y in [(0.1, 2.5), (-3.0, 0.0), (3.0, 0.2), (0.0, -2.7)]]
    return make("Conversation Candy Hearts", out + sparkle)


@design("valentine_love_potion", T)
def love_potion(rng):
    bulb = circle(0, -1.0, 1.65, 120)
    neck = rect(-0.45, 0.3, 0.45, 2.0)
    flask = union(bulb, neck)
    lip = rrect(-0.6, 1.95, 0.6, 2.2, 0.08)
    cork = poly((-0.4, 2.2), (0.4, 2.2), (0.5, 2.85), (-0.5, 2.85))
    liquid = keep([wave(-2, 2, -0.4, 0.1, 3, 80)], bulb)
    bubbles = keep([hrt(-0.6, -1.4, 0.35), hrt(0.5, -1.0, 0.45), hrt(-0.1, -2.1, 0.3), circle(0.8, -1.9, 0.15, 12), circle(-0.9, -0.8, 0.12, 12),
                    circle(0.1, -0.7, 0.13, 12)], bulb)
    tag_string = [(0.45, 1.2), (1.4, 0.4)]
    tag = hrt(1.6, 0.0, 0.6, -0.3)
    rising = [hrt(-0.9, 3.2, 0.3, 0.2), hrt(0.8, 3.4, 0.38, -0.2), hrt(0.1, 3.9, 0.25)]
    label = word("XO", 1.6, -0.05, 0.25, rot=-0.3)
    ribbon = keep([[(-1, 1.1), (1, 1.1)], [(-1, 1.35), (1, 1.35)]], neck)
    out = hide(flask, lip) + [lip, cork] + liquid + bubbles + hide([tag_string], tag) + [tag] + label + rising + ribbon
    return make("Love Potion Bottle", out)


@design("valentine_heart_key", T)
def heart_key(rng):
    o = hrt(-1.9, 0.15, 1.35, -math.pi / 2)
    i = hrt(-1.95, 0.15, 0.85, -math.pi / 2)
    swirl = [spiral(-2.2, 0.15, 0.04, 0.3, 1.3, 30)]
    shaft = rect(-0.85, -0.15, 2.8, 0.15)
    rings = [rrect(-0.65, -0.32, -0.35, 0.32, 0.1), rrect(-0.2, -0.28, 0.05, 0.28, 0.1)]
    bit = poly((2.0, -0.15), (2.0, -1.0), (2.3, -1.0), (2.3, -0.7), (2.55, -0.7), (2.55, -1.1), (2.8, -1.1), (2.8, -0.15), closed=False)
    out = hide([o], shaft, *rings) + [i] + swirl + hide([shaft], *rings) + rings + [bit]
    rb, rc = bow(-3.0, 1.3, 0.7)
    out = hide(out, *rc) + rb
    tiny = [hrt(1.0, 1.4, 0.4, 0.3), hrt(2.0, 2.1, 0.3, -0.2)]
    return make("Heart Skeleton Key", out + tiny)


@design("valentine_bear_with_heart", T)
def bear_with_heart(rng):
    big = hrt(0, -0.7, 2.2)
    head = circle(0, 1.75, 1.05, 80)
    ears = [circle(-0.9, 2.6, 0.42, 30), circle(0.9, 2.6, 0.42, 30)]
    inner_ears = [circle(-0.9, 2.6, 0.22, 20), circle(0.9, 2.6, 0.22, 20)]
    muzzle = ellipse(0, 1.35, 0.5, 0.38, 30)
    nose = ellipse(0, 1.5, 0.18, 0.12, 14)
    mouth = [[(0, 1.38), (0, 1.2)], arc(-0.12, 1.2, 0.12, 0, -math.pi, 8), arc(0.12, 1.2, 0.12, math.pi, 2 * math.pi, 8)]
    body = ellipse(0, -0.6, 1.9, 1.9, 100)
    paws = [ellipse(-1.25, 0.3, 0.42, 0.32, 24, rot=0.4), ellipse(1.25, 0.3, 0.42, 0.32, 24, rot=-0.4)]
    feet = [ellipse(-1.4, -2.55, 0.65, 0.4, 30), ellipse(1.4, -2.55, 0.65, 0.4, 30)]
    pads = [circle(-1.4, -2.55, 0.18, 12), circle(1.4, -2.55, 0.18, 12)][:0]
    txt = word("LOVE", 0, -0.55, 0.55)
    inner = hrt(0, -0.7, 1.9)
    out = hide([body] + inner_ears[:0], head, big, *ears, *paws, *feet) + hide(ears, head) + inner_ears + [head] + hide([muzzle], ) + [nose] + mouth
    out += hide([big, inner], *paws) + paws + hide(feet, big) + txt
    return make("Teddy Bear Holding a Big Heart", out, [eye(-0.38, 1.95, 0.11), eye(0.38, 1.95, 0.11)])


@design("valentine_swans", T)
def swans(rng):
    neck_c = cubic((-0.75, -0.4), (-2.3, 0.9), (-1.6, 2.7), (-0.25, 1.95), 40)
    neck = tube(neck_c, lambda t: 0.42 - 0.2 * t)
    head = ellipse(-0.3, 1.95, 0.32, 0.25, 24, rot=-0.5)
    beak = poly((-0.05, 1.85), (0.1, 1.45), (-0.2, 1.7))
    body = ellipse(-1.6, -0.75, 1.45, 0.62, 80)
    tail = poly((-2.6, -0.45), (-3.3, 0.15), (-2.9, -0.95))
    sil = union(body, tail, neck, head)
    wing = chain(cubic((-0.6, -0.55), (-1.2, 0.2), (-2.4, 0.1), (-2.9, -0.2), 16), [(-2.4, -0.45), (-2.65, -0.6), (-2.1, -0.75)],
                 quad((-2.1, -0.75), (-1.2, -1.0), (-0.6, -0.55), 10))
    left = sil + [beak, wing]
    lc = [body, tail, neck, head, beak]
    right = [mirror_x(p) for p in left]
    rc = [mirror_x(p) for p in lc]
    water = hide([wave(-3.4, 3.4, -1.25, 0.08, 6, 160), wave(-2.8, 2.8, -1.7, 0.08, 5, 120), wave(-2.0, 2.0, -2.15, 0.08, 4, 90)], *lc, *rc)
    out = hide(left, *rc) + right + water + [hrt(0, 0.6, 0.45)]
    return make("Swans Making a Heart", hide(out, ), [eye(-0.32, 2.02, 0.06), eye(0.32, 2.02, 0.06)])


@design("valentine_coffee_for_two", T)
def coffee_for_two(rng):
    out = []
    for sg in (-1, 1):
        cx = 1.35 * sg
        rim = ellipse(cx, 0.4, 1.1, 0.32, 60)
        cup = chain([(cx - 1.1, 0.4)], quad((cx - 1.05, -1.9), (cx, -2.0), (cx + 1.05, -1.9), 20)[:0], cubic((cx - 1.1, 0.4), (cx - 1.05, -1.6), (cx - 0.6, -1.9), (cx, -1.9), 14),
                    cubic((cx, -1.9), (cx + 0.6, -1.9), (cx + 1.05, -1.6), (cx + 1.1, 0.4), 14))
        foam = ellipse(cx, 0.38, 0.9, 0.22, 50)
        art = hrt(cx, 0.4, 0.3, sy=0.45)
        hx = cx + 1.05 * sg
        handle = [arc(hx, -0.5, 0.55, -1.3, 1.3, 16), arc(hx, -0.5, 0.3, -1.2, 1.2, 12)]
        if sg < 0:
            handle = [mirror_x(h, hx) for h in handle]
        handle = hide(handle, poly(*cup, (cx + 1.1, 0.4)))
        saucer = hide([ellipse(cx, -1.95, 1.6, 0.35, 60)], poly(*cup, (cx + 1.1, 0.4)))
        deco = keep([hrt(cx, -0.75, 0.35)], poly(*cup, (cx + 1.1, 0.4)))
        out += [rim, cup, foam, art] + handle + saucer + deco
    steam = [cubic((-1.35, 0.8), (-1.6, 1.6), (-1.2, 2.0), (-0.8, 2.4), 20), cubic((1.35, 0.8), (1.6, 1.6), (1.2, 2.0), (0.8, 2.4), 20)]
    top = hrt(0, 2.65, 0.9)
    return make("Coffee for Two", out + steam + [top])


@design("valentine_champagne_toast", T)
def champagne_toast(rng):
    def flute(rot):
        bowl = chain([(-0.5, 2.6)], cubic((-0.5, 2.6), (-0.55, 0.9), (-0.35, 0.3), (-0.07, 0.15), 16), [(-0.07, -1.8)],
                     quad((-0.07, -1.8), (-0.8, -1.9), (-0.9, -2.05), 6), [(0.9, -2.05)], quad((0.9, -2.05), (0.8, -1.9), (0.07, -1.8), 6),
                     [(0.07, 0.15)], cubic((0.07, 0.15), (0.35, 0.3), (0.55, 0.9), (0.5, 2.6), 16), [(-0.5, 2.6)])
        liquid = keep([[(-1, 1.9), (1, 1.9)]], bowl)
        bub = [circle(x, y, 0.08, 8) for x, y in [(-0.15, 1.5), (0.15, 1.1), (-0.1, 0.7), (0.1, 1.65)]]
        return [transform(p, 0, -0.2, rot=rot) for p in [bowl] + liquid + bub], transform(bowl, 0, -0.2, rot=rot)
    a, ac = flute(-0.38)
    b, bc = flute(0.38)
    a = [transform(p, -1.1, 0) for p in a]
    ac = transform(ac, -1.1, 0)
    b = [transform(p, 1.1, 0) for p in b]
    bc = transform(bc, 1.1, 0)
    out = hide(a, bc) + b
    spark = [star(0, 2.85, 0.45, 4, 0.3), [(-0.6, 2.6), (-0.9, 2.9)], [(0.6, 2.6), (0.9, 2.9)], [(0, 3.4), (0, 3.7)]]
    hearts = [hrt(-2.5, 2.3, 0.4, 0.3), hrt(2.5, 2.4, 0.45, -0.3), hrt(-2.6, 0.3, 0.3), hrt(2.7, 0.5, 0.3)]
    return make("Champagne Toast", out + spark + hearts)


@design("valentine_love_tree", T)
def love_tree(rng):
    trunk = chain(quad((-2.0, -2.9), (-0.7, -2.6), (-0.45, -1.8), 8), [(-0.4, -0.2)], quad((-0.4, -0.2), (-0.6, 0.6), (-1.5, 1.2), 8),
                  [(-1.3, 1.4)], quad((-1.3, 1.4), (-0.4, 0.9), (0.0, 0.5), 8), quad((0.0, 0.5), (0.4, 0.9), (1.3, 1.4), 8), [(1.5, 1.2)],
                  quad((1.5, 1.2), (0.6, 0.6), (0.4, -0.2), 8), [(0.45, -1.8)], quad((0.45, -1.8), (0.7, -2.6), (2.0, -2.9), 8))
    carve = hrt(0, -1.1, 0.4)
    R = __import__("random").Random(5)
    out = [trunk, carve, [(-3.0, -2.9), (3.0, -2.9)]]
    pts = []
    for k in range(400):
        x, y = R.uniform(-2.6, 2.6), R.uniform(0.0, 3.3)
        if _inside((x, (y - 1.35) / 1.0), hrt(0, 0, 2.0)) and all(math.dist((x, y), p) > 0.62 for p in pts):
            pts.append((x, y))
    hs = []
    for x, y in pts:
        h = hrt(x, y, R.uniform(0.32, 0.4), R.uniform(-0.4, 0.4))
        hs.append(h)
    out = hide(out, *hs) + hs
    falling = [hrt(-2.6, -1.6, 0.3, 0.5), hrt(2.4, -1.2, 0.3, -0.4), hrt(1.6, -2.4, 0.28, 0.2)]
    return make("Tree of Hearts", out + falling)


@design("valentine_heart_wreath", T)
def heart_wreath(rng):
    o = hrt(0, 0.0, 2.7)
    i = hrt(0, 0.05, 1.85)
    mid = hrt(0, 0.0, 2.27)
    items, covers = [], []
    n = len(mid) - 1
    for k in range(0, n, 6):
        (x0, y0), (x1, y1) = mid[k], mid[(k + 2) % n]
        a = math.atan2(y1 - y0, x1 - x0) + (0.6 if (k // 6) % 2 else -0.6)
        L = lens((x0, y0), (x0 + 0.55 * math.cos(a), y0 + 0.55 * math.sin(a)), 0.3)
        items.append(L)
    roses = []
    for k in (12, 32, 60, 88, 108):
        x, y = mid[k]
        sh, c = rose(x, y, 0.42)
        roses.append((sh, c))
    out = items
    for sh, c in roses:
        out = hide(out, c) + sh
        covers.append(c)
    bb, bc = bow(0, 0.95, 0.9)
    out = hide([o, i], *covers, *bc) + hide(out, *bc) + bb
    return make("Valentine Heart Wreath", out)


@design("valentine_mailbox", T)
def mailbox(rng):
    box = chain([(-2.2, -0.2)], [(-2.2, 0.9)], arc(-1.4, 0.9, 0.8, math.pi, math.pi / 2, 12)[1:], [(1.2, 1.7)], arc(1.2, 0.9, 0.8, math.pi / 2, 0, 12)[1:],
                [(2.0, -0.2), (-2.2, -0.2)])
    door = chain([(1.75, -0.2), (1.75, 0.9)], arc(1.2, 0.9, 0.55, 0, math.pi / 2, 10)[1:])[:0]
    front = chain([(2.0, -0.2), (2.0, 0.9)], arc(1.2, 0.9, 0.8, 0, math.pi / 2, 12))[:0]
    ridge = [[(-1.4, 1.7), (-1.4, -0.2)][:0]]
    post = rect(-0.35, -2.9, 0.35, -0.2)
    flag = [rect(-1.0, 0.3, -0.85, 2.4), poly((-1.0, 2.4), (-1.0, 1.8), (-1.75, 1.8), (-1.75, 2.4))]
    flag = hide(flag[:1], box) + [flag[1]]
    letters = []
    for x, y, r in [(2.55, 0.9, 0.5), (2.3, 2.1, 0.15), (1.2, 2.75, -0.25)]:
        env = transform(rect(-0.65, -0.42, 0.65, 0.42), x, y, rot=r)
        flapl = transform([(-0.65, 0.42), (0, -0.05), (0.65, 0.42)], x, y, rot=r)
        seal = transform(heart(0, -0.05, 0.22), x, y, rot=r)
        letters = hide(letters, env) + [env, flapl, seal]
    hearts = [hrt(-2.6, 2.6, 0.35, 0.3), hrt(-2.9, 1.5, 0.25), hrt(0.2, 2.8, 0.3)]
    deco = [hrt(-0.3, 0.6, 0.55)]
    grass = [zigzag(-1.4, 1.4, -2.85, 0.15, 8)]
    out = hide([box], *[poly(*l) for l in letters[:1]]) + flag + [post] + deco + letters + hearts + grass
    out = hide(out[:1], ) + out[1:]
    return make("Mailbox Full of Love Letters", hide(out, ))


@design("valentine_heart_lollipops", T)
def heart_lollipops(rng):
    out = []
    for x, y, s, r in [(-1.4, 1.2, 1.1, 0.35), (1.4, 1.3, 1.1, -0.35), (0.0, 1.9, 1.25, 0.0)]:
        layers = [hrt(x, y, s * f, r) for f in (1.0, 0.78, 0.56, 0.34)]
        bot = (x + 1.05 * s * math.sin(r), y - 1.05 * s * math.cos(r))
        stick = tube([bot, (0, -2.0)], 0.18, cap=False)
        out = hide(out, layers[0]) + layers + hide([stick], layers[0])
        stick_end = None
    sticks_low = [[(-0.25, -2.0), (-0.3, -2.9)], [(0.0, -2.0), (0.0, -2.9)], [(0.25, -2.0), (0.3, -2.9)]]
    bb, bc = bow(0, -1.9, 1.0)
    out = hide(out, *bc) + hide(sticks_low, *bc) + bb
    return make("Heart Lollipops", out)


@design("valentine_heart_cupcake", T)
def heart_cupcake(rng):
    liner = poly((-1.7, -0.5), (1.7, -0.5), (1.25, -2.9), (-1.25, -2.9))
    pleats = keep([[(x, -0.5), (x * 0.72, -2.9)] for x in (-1.15, -0.58, 0.0, 0.58, 1.15)], liner)
    frost = chain([(-1.9, -0.5)], *[arc(-1.55 + 0.62 * k, -0.45, 0.33, math.pi, 0, 8)[0:0] for k in range(6)], [(-1.9, -0.5)])
    swirl = [ellipse(0, -0.2, 1.95, 0.5, 80), ellipse(0, 0.45, 1.55, 0.45, 70), ellipse(0, 1.05, 1.05, 0.4, 60), ellipse(0, 1.55, 0.55, 0.3, 40)]
    sw = []
    for k, e in enumerate(swirl):
        sw = hide(sw, e) + [e]
    sw = hide(sw, liner)
    topper = hrt(0, 2.6, 0.95)
    pick = hide([[(0, 1.6), (0, 2.0)]], topper)
    sw = hide(sw, topper)
    sprinkles = [hrt(x, y, 0.2, r) for x, y, r in [(-1.2, -0.1, 0.3), (0.9, 0.2, -0.3), (-0.5, 0.7, 0.2), (0.6, 0.9, -0.2), (1.3, -0.3, 0.4)]]
    sw = hide(sw, *sprinkles)
    deco = [hrt(0, -1.6, 0.45)]
    return make("Cupcake with a Heart Topper", [liner] + hide(pleats, deco[0]) + deco + sw + sprinkles + [topper, hrt(0, 2.6, 0.65)] + pick)


@design("valentine_long_stem_rose", T)
def long_stem_rose(rng):
    sh, c = rose(0.6, 1.8, 1.25, -0.2)
    sepals = [lens((0.4, 0.55), (-0.4, 0.7), 0.25), lens((0.45, 0.55), (1.2, 0.35), 0.25)]
    stem_c = cubic((0.4, 0.55), (0.3, -0.5), (-0.6, -1.5), (-1.3, -3.1), 40)
    stem = tube(stem_c, 0.16)
    thorns = [poly(stem_c[k], (stem_c[k][0] + 0.25 * sg, stem_c[k][1] + 0.08), (stem_c[k + 2][0], stem_c[k + 2][1])) for k, sg in [(10, 1), (18, -1), (28, 1)]]
    leaves = [lens(stem_c[14], (1.6, -0.6), 0.32), lens(stem_c[24], (-1.9, -0.9), 0.32), lens(stem_c[32], (0.2, -2.5), 0.3)]
    veins = [[stem_c[14], (1.6, -0.6)], [stem_c[24], (-1.9, -0.9)], [stem_c[32], (0.2, -2.5)]]
    veins = keep(veins, *leaves)
    rb, rc = bow(-0.45, -1.2, 0.8)
    out = sh + hide(sepals, c) + hide([stem] + thorns, c, *sepals, *leaves, *rc) + hide(leaves + veins, *rc) + rb
    return make("Single Long-Stem Rose", out)


@design("valentine_tulip_heart_vase", T)
def tulip_heart_vase(rng):
    vase = hrt(0, -1.25, 1.75)
    neck = rect(-0.55, -1.0, 0.55, -0.2)
    lip = rrect(-0.75, -0.2, 0.75, 0.05, 0.08)
    out, covers = [], []
    for x, y, r in [(-1.4, 1.55, 0.4), (0.0, 2.4, 0.0), (1.4, 1.55, -0.4), (-0.7, 1.0, 0.2)][:3]:
        sh, cc = tulip(x, y, 1.05, r)
        covers.append(cc)
        out += sh
        bx, by = x + 0.63 * math.sin(r), y - 0.63 * math.cos(r)
        out.append(quad((bx, by), (bx * 0.4, (by + 0.0) / 2), (x * 0.15, -0.05), 14))
    leaves = [lens((-0.2, -0.05), (-2.3, 0.6), 0.16), lens((0.2, -0.05), (2.3, 0.6), 0.16)]
    out = hide(out, *leaves) + leaves
    out = hide(out, lip, neck, vase) + [lip] + hide([neck], vase) + [vase]
    inner = keep([hrt(0, -1.25, 1.3)], vase)
    water = keep([wave(-2, 2, -0.9, 0.08, 4, 80)], hrt(0, -1.25, 1.3))
    return make("Tulips in a Heart Vase", out + inner + water)


@design("valentine_heart_hot_air_balloon", T)
def heart_balloon(rng):
    bal = hrt(0, 1.0, 2.35)
    gores = keep([quad((x * 0.3, 2.0), (x, 0.7), (0, -1.45), 20) for x in (-3.2, -1.8, 1.8, 3.2)] + [[(0, 1.75), (0, -1.5)]], bal)
    bands = keep([wave(-3, 3, 0.4, 0.1, 6, 120)], bal)
    ropes = [[(-0.25, -1.35), (-0.6, -2.2)], [(0.25, -1.35), (0.6, -2.2)]]
    basket = rrect(-0.75, -2.95, 0.75, -2.2, 0.12)
    weave = keep([[(-1, -2.58), (1, -2.58)]] + [[(x, -3), (x, -2.1)] for x in (-0.35, 0.0, 0.35)], basket)
    clouds = []
    for cx, cy, s in [(-2.4, -1.4, 0.8), (2.5, -0.6, 0.7)]:
        cs = [circle(cx - 0.5 * s, cy, 0.45 * s, 30), circle(cx, cy + 0.25 * s, 0.6 * s, 30), circle(cx + 0.55 * s, cy, 0.42 * s, 30)]
        clouds += hide(union(*cs), poly((cx - 2, cy - 0.3 * s), (cx + 2, cy - 0.3 * s), (cx + 2, cy - 3), (cx - 2, cy - 3))) + [[(cx - 0.95 * s, cy - 0.3 * s), (cx + 0.97 * s, cy - 0.3 * s)]]
    small = [hrt(2.4, 2.6, 0.4, -0.2), hrt(-2.7, 1.9, 0.3, 0.2)]
    birds = [chain(arc(-1.8, -2.6, 0.25, 0.3, math.pi - 0.3, 6), arc(-1.32, -2.6, 0.25, 0.3, math.pi - 0.3, 6))]
    return make("Heart Hot Air Balloon", [bal] + gores + bands + ropes + [basket] + weave + clouds + small)


@design("valentine_kissing_doves", T)
def kissing_doves(rng):
    def dove():
        body = chain(cubic((0.0, 0.0), (-0.6, 0.5), (-1.8, 0.3), (-2.6, 0.5), 20), [(-2.4, 0.0), (-2.8, -0.3), (-2.3, -0.35), (-2.6, -0.7)],
                     cubic((-2.6, -0.7), (-1.6, -0.6), (-0.5, -0.9), (0.15, -0.3), 20))
        head = circle(0.05, 0.05, 0.42, 30)
        beak = poly((0.42, 0.15), (0.75, 0.02), (0.42, -0.08))
        sil = union(body + [body[0]], head)
        wing = chain(quad((-0.6, 0.15), (-0.3, 1.3), (-0.9, 2.3), 14), [(-1.1, 1.85), (-1.4, 2.1), (-1.5, 1.55), (-1.9, 1.7), (-1.8, 1.15), (-2.2, 1.1)],
                     quad((-2.2, 1.1), (-1.6, 0.3), (-1.2, 0.2), 10))
        sil = hide(sil, wing)
        return sil + [beak, wing], [head, poly(*body), wing]
    d, dc = dove()
    L = [transform(p, -0.85, 0.9) for p in d]
    R = [mirror_x(p) for p in L]
    ribbon = [quad((-1.2, 0.5), (-0.5, -0.7), (0, -1.0), 16), quad((1.2, 0.5), (0.5, -0.7), (0, -1.0), 16)]
    big = hrt(0, -1.85, 1.0)
    rib = hide([[(0, -1.0), (0, -1.55)]], big)
    small = [hrt(0, 2.0, 0.4), hrt(-2.7, -1.8, 0.3, 0.3), hrt(2.7, -1.8, 0.3, -0.3)]
    return make("Kissing Doves", L + R + ribbon + rib + [big, hrt(0, -1.85, 0.7)] + small, [eye(-0.75, 1.08, 0.07), eye(0.75, 1.08, 0.07)])


@design("valentine_heart_garland", T)
def heart_garland(rng):
    out = []
    for row, (y0, sag, n) in enumerate([(2.9, 1.0, 6), (0.2, 1.0, 5)]):
        string = quad((-3.3, y0), (0, y0 - 2 * sag), (3.3, y0), 60)
        covers, items = [], []
        for k in range(n):
            x, y = string[int((k + 0.5) / n * 60)]
            s = 0.62 if row == 0 else 0.7
            h = hrt(x, y - 0.6 * s, s)
            kind = (k + row) % 3
            if kind == 0:
                det = [hrt(x, y - 0.6 * s, 0.65 * s)]
            elif kind == 1:
                det = keep([[(x - 1, y - 0.6 * s + d), (x + 1, y - 0.6 * s + d)] for d in (-0.3 * s, 0.0, 0.3 * s)], h)
            else:
                det = keep([circle(x + dx, y - 0.6 * s + dy, 0.09, 8) for dx, dy in [(-0.3, 0.1), (0.3, 0.1), (0, -0.3), (0, 0.3)]], h)
            items += [h] + det
            covers.append(h)
        out += hide([string], *covers) + items
        b1, _ = bow(-3.3, y0, 0.5)
        b2, _ = bow(3.3, y0, 0.5)
        out += b1 + b2
    return make("Heart Garland", out)


@design("valentine_puppy_with_heart", T)
def puppy_with_heart(rng):
    head = ellipse(0, 1.2, 1.15, 1.0, 80)
    ears = [chain(cubic((-0.85, 1.85), (-1.9, 1.9), (-1.9, 0.4), (-1.55, -0.1), 16), cubic((-1.55, -0.1), (-1.2, 0.1), (-1.0, 0.6), (-1.0, 1.2), 12)),
            chain(cubic((0.85, 1.85), (1.9, 1.9), (1.9, 0.4), (1.55, -0.1), 16), cubic((1.55, -0.1), (1.2, 0.1), (1.0, 0.6), (1.0, 1.2), 12))]
    muzzle = ellipse(0, 0.75, 0.6, 0.42, 40)
    nose = ellipse(0, 0.95, 0.22, 0.15, 16)
    mouth = [[(0, 0.8), (0, 0.6)], arc(-0.15, 0.6, 0.15, 0, -math.pi, 8), arc(0.15, 0.6, 0.15, math.pi, 2 * math.pi, 8)]
    tongue = chain(arc(0, 0.45, 0.15, math.pi, 2 * math.pi, 8))
    patch = keep([ellipse(0.55, 1.5, 0.45, 0.4, 30)], head)
    body = ellipse(0, -1.3, 1.5, 1.55, 90)
    big = hrt(0, -1.0, 1.25)
    paws = [ellipse(-0.95, -0.55, 0.35, 0.28, 20, rot=0.5), ellipse(0.95, -0.55, 0.35, 0.28, 20, rot=-0.5)]
    feet = [ellipse(-0.9, -2.75, 0.55, 0.3, 24), ellipse(0.9, -2.75, 0.55, 0.3, 24)]
    tail = tube(quad((1.4, -2.2), (2.4, -2.0), (2.5, -0.9), 12), lambda t: 0.3 - 0.2 * t)
    out = hide([body], head, *ears, big, *paws, *feet) + hide([tail], body) + hide([head], *ears) + ears + [muzzle] + patch + [nose] + mouth + [tongue]
    out += hide([big, hrt(0, -1.0, 0.95)], *paws) + paws + hide(feet, body)
    return make("Puppy Holding a Heart", out, [eye(-0.42, 1.45, 0.12), eye(0.42, 1.45, 0.12)])


@design("valentine_kitten_heart_tail", T)
def kitten_heart_tail(rng):
    head = ellipse(-0.9, 1.0, 1.05, 0.9, 80)
    ears = [poly((-1.85, 1.3), (-1.75, 2.45), (-1.05, 1.85)), poly((0.05, 1.3), (-0.05, 2.45), (-0.75, 1.85))]
    inner = [poly((-1.68, 1.55), (-1.62, 2.15), (-1.25, 1.85), closed=False), poly((-0.12, 1.55), (-0.18, 2.15), (-0.55, 1.85), closed=False)]
    body = ellipse(-0.9, -1.2, 1.35, 1.6, 80)
    haunch = ellipse(-0.1, -2.0, 0.8, 0.75, 40)
    sil = union(body, haunch)
    paws = [ellipse(-1.4, -2.7, 0.4, 0.22, 20), ellipse(-0.6, -2.7, 0.4, 0.22, 20)]
    tail_c = list(reversed(hrt(1.7, 0.4, 1.35)[30:110]))
    tail_c = [(0.35, -2.4)] + quad((1.2, -2.6), tail_c[0], tail_c[0], 8)[1:-1] + tail_c[:0] + []
    hc = hrt(1.7, 0.2, 1.35)
    tail_line = chain(cubic((0.4, -2.45), (1.2, -2.8), (1.7, -2.1), (1.7, -1.2), 16))
    tail = tube(chain(tail_line, [p for p in hc[60:] + hc[1:60] if True][::-1][0:0]), 0.3)
    tail = tube(chain(cubic((0.4, -2.45), (1.5, -2.8), (1.75, -1.8), hc[60], 14), hc[60:120], hc[1:58]), 0.28, cap=True)
    out = hide([tail], sil, *paws) + hide(sil, head, *paws) + paws + hide(ears, head) + inner + [head]
    nose = poly((-1.05, 0.85), (-0.75, 0.85), (-0.9, 0.68))
    mouth = [arc(-1.05, 0.6, 0.15, 0, -math.pi, 8), arc(-0.75, 0.6, 0.15, math.pi, 2 * math.pi, 8), [(-0.9, 0.68), (-0.9, 0.6)]]
    wh = [[(-1.4, 0.75), (-2.4, 0.95)], [(-1.4, 0.65), (-2.4, 0.5)], [(-0.4, 0.75), (0.55, 0.95)], [(-0.4, 0.65), (0.55, 0.5)]]
    chest = keep([chain(*[arc(-1.3 + 0.27 * k, -0.25, 0.14, math.pi, 2 * math.pi, 6) for k in range(4)])], body)
    return make("Kitten with a Heart-Shaped Tail", out + [nose] + mouth + wh + chest + [hrt(-2.6, 2.5, 0.35, 0.3), hrt(2.9, -2.4, 0.3)],
                [eye(-1.3, 1.15, 0.13), eye(-0.5, 1.15, 0.13)])


@design("valentine_heart_sunglasses", T)
def heart_sunglasses(rng):
    L = hrt(-1.5, 0.0, 1.35, 0.08)
    R = hrt(1.5, 0.0, 1.35, -0.08)
    Li = hrt(-1.5, 0.02, 1.1, 0.08)
    Ri = hrt(1.5, 0.02, 1.1, -0.08)
    bridge = [quad((-0.55, 0.65), (0, 0.95), (0.55, 0.65), 10), quad((-0.5, 0.45), (0, 0.72), (0.5, 0.45), 10)]
    arms = [[(-2.75, 0.55), (-3.35, 0.62)], [(2.75, 0.55), (3.35, 0.62)]]
    shine = [[(-2.2, 0.3), (-1.7, 0.8)], [(-2.0, -0.1), (-1.4, 0.5)], [(0.8, 0.3), (1.3, 0.8)], [(1.0, -0.1), (1.6, 0.5)]]
    shine = keep(shine, Li, Ri)
    sp = [star(-2.8, -1.8, 0.35, 4, 0.3), star(2.9, -1.6, 0.3, 4, 0.3), star(0.0, -1.6, 0.25, 4, 0.3)]
    return make("Heart Sunglasses", [L, R, Li, Ri] + bridge + arms + shine + sp)


@design("valentine_lipstick_kiss", T)
def lipstick_kiss(rng):
    lips = chain(cubic((-1.5, 0.0), (-1.0, 0.5), (-0.7, 0.75), (-0.35, 0.7), 14), quad((-0.35, 0.7), (-0.1, 0.65), (0, 0.45), 6),
                 quad((0, 0.45), (0.1, 0.65), (0.35, 0.7), 6), cubic((0.35, 0.7), (0.7, 0.75), (1.0, 0.5), (1.5, 0.0), 14),
                 cubic((1.5, 0.0), (1.0, -0.8), (-1.0, -0.8), (-1.5, 0.0), 24))
    seam = cubic((-1.5, 0.0), (-0.6, 0.0), (-0.3, -0.12), (0, 0.02), 10) + cubic((0, 0.02), (0.3, -0.12), (0.6, 0.0), (1.5, 0.0), 10)[1:]
    creases = keep([[(x, 0.5), (x * 1.1, 0.2)] for x in (-0.9, -0.5, 0.5, 0.9)] + [[(x, -0.15), (x * 1.05, -0.45)] for x in (-0.8, -0.35, 0.35, 0.8)], lips)
    kiss = [transform(p, 0.9, 1.4, 1.0, 0.25) for p in [lips, seam] + creases]
    base = rect(-2.6, -2.9, -1.4, -1.6)
    band = rect(-2.5, -1.6, -1.5, -1.1)
    bullet = poly((-2.35, -1.1), (-1.65, -1.1), (-1.65, -0.2), (-2.35, 0.25))
    ridges = [[(-2.6, -2.5), (-1.4, -2.5)], [(-2.6, -2.0), (-1.4, -2.0)]]
    cap = transform(rrect(-0.6, -1.0, 0.6, 1.0, 0.12), 0.5, -2.35, rot=math.pi / 2 - 0.15)
    cap_line = transform([(-0.6, 0.6), (0.6, 0.6)], 0.5, -2.35, rot=math.pi / 2 - 0.15)
    small = [transform(p, 2.3, -0.9, 0.45, -0.3) for p in [lips, seam]]
    return make("Lipstick and a Kiss", kiss + [base, band, bullet] + ridges + [cap, cap_line] + small + [hrt(-0.6, 2.7, 0.35)])


@design("valentine_perfume_bottle", T)
def perfume_bottle(rng):
    body = hrt(0, -0.8, 2.0)
    inner = hrt(0, -0.85, 1.55)
    neck = rect(-0.35, 0.55, 0.35, 1.0)
    cap = poly((-0.55, 1.0), (0.55, 1.0), (0.7, 1.4), (0.35, 1.9), (-0.35, 1.9), (-0.7, 1.4))
    facets = [[(-0.7, 1.4), (0.7, 1.4)], [(-0.2, 1.0), (-0.25, 1.9)][:0]]
    tube_ = tube(quad((0.55, 1.6), (1.4, 2.0), (1.7, 1.2), 14), 0.12)
    bulb = ellipse(2.0, 0.5, 0.45, 0.65, 30, rot=0.3)
    tassel = [[(2.2, -0.1), (2.3, -0.5)], poly((2.3, -0.5), (2.05, -1.3), (2.55, -1.3))]
    mist = [circle(x, y, 0.07, 8) for x, y in [(-1.0, 1.9), (-1.3, 2.2), (-1.1, 2.6), (-1.6, 2.0), (-1.6, 2.6)]]
    hearts = [hrt(-2.1, 2.4, 0.3, 0.2), hrt(-2.6, 1.6, 0.25), hrt(-1.9, 3.0, 0.22)]
    shine = keep([[(-1.2, -0.2), (-0.6, 0.3)], [(-1.1, -0.7), (-0.4, -0.1)]], inner)
    out = [body, inner] + hide([neck], body) + [cap] + facets + hide([tube_], cap, bulb) + [bulb] + hide(tassel, bulb) + mist + hearts + shine
    return make("Heart Perfume Bottle", out)


@design("valentine_open_gift_box", T)
def open_gift_box(rng):
    front = rect(-2.0, -2.9, 1.0, -0.6)
    side = poly((1.0, -2.9), (2.2, -2.3), (2.2, -0.1), (1.0, -0.6))
    top_back = poly((-2.0, -0.6), (-0.8, -0.1), (2.2, -0.1), closed=False)
    rib_f = keep([[(-0.65, -3), (-0.65, -0.5)], [(-0.35, -3), (-0.35, -0.5)]], front)
    rib_s = keep([[(1.5, -3), (1.5, 0)], [(1.75, -3), (1.75, 0)]], side)
    lid = transform(poly((-1.7, 0.0), (1.7, 0.0), (1.7, 0.7), (-1.7, 0.7)), -1.3, 1.4, rot=0.55)
    lid_rib = keep([transform([(-0.15, -1), (-0.15, 2)], -1.3, 1.4, rot=0.55), transform([(0.15, -1), (0.15, 2)], -1.3, 1.4, rot=0.55)], lid)
    hearts = [hrt(0.2, 0.8, 0.55, 0.2), hrt(1.4, 1.6, 0.45, -0.3), hrt(0.3, 2.3, 0.4, 0.1), hrt(-0.6, 0.3, 0.35, -0.2), hrt(2.3, 0.8, 0.35, 0.3),
              hrt(1.1, 2.9, 0.3, 0.0)]
    hc = hearts
    out = hide([front, side, top_back] + rib_f + rib_s, *hc) + hide([lid] + lid_rib, *hc) + hearts
    sparks = [star(-2.6, 2.6, 0.3, 4, 0.3), star(2.8, 2.4, 0.25, 4, 0.3)]
    return make("Gift Box Bursting with Hearts", out + sparks)


@design("valentine_dipped_strawberries", T)
def dipped_strawberries(rng):
    plate = hrt(0, -0.4, 2.9, sy=0.65)
    plate_in = hrt(0, -0.38, 2.45, sy=0.65)
    out = [plate, plate_in]
    covers = []
    for x, y, r in [(-1.15, 0.2, 0.35), (1.15, 0.2, -0.35), (0.0, -0.6, 0.0)]:
        berry = chain(cubic((0, 0.9), (-0.9, 1.0), (-0.95, 0.0), (0, -1.1), 20), cubic((0, -1.1), (0.95, 0.0), (0.9, 1.0), (0, 0.9), 20))
        dip = wave(-1.2, 1.2, -0.1, 0.1, 3, 60)
        drizzle = zigzag(-1.0, 1.0, -0.55, 0.12, 4)
        seeds = [[(sx, sy), (sx + 0.05, sy + 0.12)] for sx, sy in [(-0.4, 0.55), (0.1, 0.6), (0.45, 0.35), (-0.2, 0.2), (0.3, 0.05)]]
        cap = [lens((0, 0.9), (-0.6, 1.2), 0.3), lens((0, 0.9), (0.6, 1.2), 0.3), lens((0, 0.9), (0.0, 1.45), 0.3)]
        stem = [[(0, 1.4), (0.1, 1.75)]]
        parts = [berry] + keep([dip, drizzle], berry) + seeds + hide(cap, berry) + hide(stem, *cap)
        parts = [transform(p, x, y, 1.0, r) for p in parts]
        bc = transform(berry, x, y, 1.0, r)
        caps = [transform(c, x, y, 1.0, r) for c in cap]
        out = hide(out, bc, *caps) + parts
    return make("Valentine Strawberries in a Heart Box", out + [hrt(-2.4, 2.2, 0.35, 0.3), hrt(2.4, 2.1, 0.3, -0.3)])


@design("valentine_love_locks_bridge", T)
def love_locks_bridge(rng):
    rails = [[(-3.3, 1.6), (3.3, 1.6)], [(-3.3, 1.35), (3.3, 1.35)], [(-3.3, -1.4), (3.3, -1.4)]]
    bars = [[(x, 1.35), (x, -1.4)] for x in (-2.5, -1.25, 0.0, 1.25, 2.5)]
    posts = [rect(-3.3, -2.0, -3.0, 1.9), rect(3.0, -2.0, 3.3, 1.9)]
    locks, covers = [], []
    specs = [(-2.5, 0.6, "heart"), (-1.25, -0.2, "box"), (0.0, 0.7, "heart"), (1.25, -0.4, "heart"), (2.5, 0.4, "box"), (-0.0, -0.75, "box"), (-2.5, -0.6, "box")]
    for x, y, kind in specs:
        sh = chain([(x - 0.25, y + 0.2), (x - 0.25, y + 0.55)], arc(x, y + 0.55, 0.25, math.pi, 0, 10), [(x + 0.25, y + 0.2)])
        if kind == "heart":
            b = hrt(x, y - 0.05, 0.55)
        else:
            b = rrect(x - 0.42, y - 0.55, x + 0.42, y + 0.25, 0.1)
        kh = [circle(x, y - 0.1, 0.09, 8), [(x, y - 0.18), (x, y - 0.38)]]
        locks.append((sh, b, kh))
        covers.append(b)
    out = hide(rails + bars, *covers, *[poly(*l[0]) for l in locks][:0])
    for sh, b, kh in locks:
        out += hide([sh], b) + [b] + kh
    out = [s for s in out]
    water = [wave(-3.3, 3.3, -2.5, 0.12, 5, 150), wave(-2.8, 2.8, -2.9, 0.1, 4, 120)]
    top = [hrt(0, 2.5, 0.5)]
    return make("Love Locks on a Bridge", hide(out, ) + posts + water + top)


@design("valentine_heart_umbrella", T)
def heart_umbrella(rng):
    canopy_top = arc(0, 0.0, 2.8, 0, math.pi, 80)
    scallops = []
    for k in range(5):
        x0 = 2.8 - 1.12 * k
        scallops += arc(x0 - 0.56, 0.0, 0.56, 0, math.pi, 12)[::-1][::-1] if False else [(x0 - 0.56 + 0.56 * math.cos(t), 0.0 + 0.3 * math.sin(t)) for t in [-math.pi * i / 12 for i in range(13)]][::-1][::-1]
    scallops = []
    for k in range(5):
        cx = 2.8 - 0.56 - 1.12 * k
        scallops += [(cx + 0.56 * math.cos(t), 0.3 * math.sin(t)) for t in [0 + (-math.pi) * i / 12 for i in range(13)]]
    canopy = chain(canopy_top, scallops[::-1][::-1])
    canopy = canopy_top + [(x, y) for x, y in reversed(scallops)][::-1][::-1]
    canopy = chain(canopy_top[::-1], scallops)
    canopy.append(canopy[0])
    ribs = keep([quad((0, 2.8), (x * 0.6, 1.6), (x, -0.1), 12) for x in (-1.68, -0.56, 0.56, 1.68)], canopy)
    tip = [[(0, 2.8), (0, 3.2)]]
    shaft = [[(0, -0.25), (0, -2.3)]]
    hook = arc(-0.35, -2.3, 0.35, 0, -math.pi, 12)
    pattern_ = keep([hrt(x, y, 0.3) for x, y in [(-1.6, 1.0), (0.0, 1.9), (1.6, 1.0), (-0.6, 0.6), (0.7, 0.6)]], canopy)
    rain = [hrt(x, y, 0.22) for x, y in [(-2.8, -1.0), (-2.2, -2.2), (2.4, -1.4), (2.9, -2.5), (1.4, -2.6), (-1.3, -1.5), (3.0, 2.6), (-3.0, 2.4)]]
    return make("Umbrella Raining Hearts", [canopy] + ribs + tip + shaft + [hook] + pattern_ + rain)


@design("valentine_candlelit_dinner", T)
def candlelit_dinner(rng):
    table = ellipse(0, -0.9, 3.2, 0.7, 120)
    hem = [(-3.1, -2.9)]
    for k in range(6):
        x0 = -3.1 + 6.2 * k / 6
        hem += quad((x0, -2.9), (x0 + 6.2 / 12, -3.2), (x0 + 6.2 / 6, -2.9), 8)[1:]
    cloth = chain([(-3.2, -0.9), (-3.1, -2.9)], hem, [(3.2, -0.9)])
    cloth = hide([cloth], table)
    plates = [ellipse(-1.8, -1.0, 0.85, 0.28, 40), ellipse(1.8, -1.0, 0.85, 0.28, 40), ellipse(-1.8, -1.0, 0.55, 0.17, 30), ellipse(1.8, -1.0, 0.55, 0.17, 30)]
    glasses = []
    for x in (-1.1, 1.1):
        bowl = chain(arc(x, 0.65, 0.4, math.pi, 2 * math.pi, 14), [(x + 0.4, 1.15), (x - 0.4, 1.15), (x - 0.4, 0.65)])
        glasses += [bowl, [(x, 0.25), (x, -0.55)], ellipse(x, -0.6, 0.3, 0.08, 16), [(x - 0.38, 0.85), (x + 0.38, 0.85)]]
    candles = []
    for x in (-0.3, 0.3):
        candles += [rect(x - 0.13, -0.6, x + 0.13, 1.6), poly((x, 1.65), (x - 0.13, 1.85), (x, 2.2), (x + 0.13, 1.85)), ellipse(x, -0.62, 0.25, 0.08, 14)]
    vase = [poly((-0.0, -0.6), (0, -0.6))]
    flowers = hide([hrt(-2.6, 2.3, 0.45, 0.3), hrt(2.6, 2.4, 0.45, -0.3), hrt(0, 3.0, 0.4)], )
    utensils = [[(-2.9, -1.3), (-2.75, -0.7)], [(2.9, -1.3), (2.75, -0.7)]]
    out = [table] + cloth + hide(plates, *glasses[:1]) + glasses + candles + flowers + utensils
    return make("Candlelit Dinner for Two", out)


@design("valentine_gift_stack", T)
def gift_stack(rng):
    boxes = [(-2.6, -2.9, 1.0, -1.0), (-1.9, -1.0, 0.6, 0.6), (-1.3, 0.6, 0.2, 1.7)]
    out = []
    for x0, y0, x1, y1 in boxes:
        b = rect(x0, y0, x1, y1)
        lid = rect(x0 - 0.12, y1 - 0.3, x1 + 0.12, y1)
        cx = (x0 + x1) / 2
        rib = hide([[(cx - 0.15, y0), (cx - 0.15, y1 - 0.3)], [(cx + 0.15, y0), (cx + 0.15, y1 - 0.3)]], )
        out += [hide([b], lid)[0] if hide([b], lid) else b, lid] + rib
    bb, bc = bow(-0.55, 1.75, 0.8)
    out = hide(out, *bc) + bb
    deco = [hrt(-1.95, -2.1, 0.3), hrt(0.2, -2.1, 0.3), hrt(-1.25, -0.25, 0.25), hrt(-0.05, -0.25, 0.25)]
    tag_str = [(1.0, -1.3), (1.9, -1.8)]
    tag = hrt(2.25, -2.1, 0.55, -0.4)
    big = hrt(2.0, 1.3, 0.8, -0.2)
    return make("Stack of Valentine Gifts", out + deco + [hide([tag_str], tag)[0], tag, big, hrt(2.0, 1.3, 0.5, -0.2)])


@design("valentine_heart_frame", T)
def heart_frame(rng):
    outer = hrt(0, -0.2, 2.75)
    mid = hrt(0, -0.18, 2.4)
    inner = hrt(0, -0.15, 2.05)
    band = hrt(0, -0.19, 2.58)
    beads = []
    n = len(band) - 1
    acc, last = 0.0, band[0]
    for p in band[1:]:
        acc += math.dist(last, p)
        last = p
        if acc >= 0.42:
            beads.append(circle(p[0], p[1], 0.1, 10))
            acc = 0.0
    nail = hide([circle(0, 2.85, 0.12, 10), [(0, 2.85), (-1.5, 1.45)], [(0, 2.85), (1.5, 1.45)]], outer)
    txt = word("LOVE", 0, 0.0, 0.5)
    hearts = [hrt(-0.7, -1.0, 0.35, 0.2), hrt(0.7, -1.0, 0.35, -0.2)]
    return make("Ornate Heart Frame", [outer, mid, inner] + beads + nail + txt + hearts)


@design("valentine_couple_on_bench", T)
def couple_on_bench(rng):
    seat = rect(-2.8, -1.3, 2.8, -1.05)
    back = [rect(-2.8, -0.55, 2.8, -0.3), rect(-2.8, 0.05, 2.8, 0.3)]
    legs = [rect(-2.6, -2.8, -2.35, -1.3), rect(2.35, -2.8, 2.6, -1.3), rect(-2.6, -1.05, -2.35, 0.3), rect(2.35, -1.05, 2.6, 0.3)]
    him_b = chain([(-1.85, -1.05)], cubic((-1.85, -1.05), (-1.95, 0.6), (-1.5, 0.9), (-0.9, 0.95), 14),
                  cubic((-0.9, 0.95), (-0.3, 0.9), (0.05, 0.6), (-0.05, -1.05), 14))
    him_h = circle(-0.95, 1.6, 0.55, 40)
    her_b = chain(cubic((0.15, -1.05), (0.05, 0.4), (0.4, 0.75), (0.9, 0.8), 14), cubic((0.9, 0.8), (1.4, 0.75), (1.75, 0.4), (1.65, -1.05), 14))
    her_h = circle(0.65, 1.35, 0.5, 40)
    hair = chain(cubic((0.15, 1.35), (0.0, 0.7), (0.4, 0.75), (0.5, 0.9), 10))
    hair2 = chain(cubic((1.15, 1.35), (1.3, 0.7), (0.95, 0.75), (0.8, 0.9), 10))
    bun = circle(0.75, 1.95, 0.22, 16)
    people = [him_b, him_h, her_b, her_h]
    pc = [poly(*him_b), him_h, poly(*her_b), her_h, bun]
    p_out = hide([him_b], her_h, poly(*her_b)) + [him_h] + hide([her_b], her_h) + hide([her_h], bun) + [bun] + [hair, hair2][:0]
    p_out = hide([him_b], poly(*her_b), her_h) + hide([him_h], her_h) + [her_b] + hide([her_h], bun) + [bun]
    p_out = hide(p_out, seat, *back, *legs)
    bench = [seat] + back + hide(legs, seat, *back)
    big = [hrt(-0.1, 2.85, 0.55)]
    lamp = [rect(2.95, -2.8, 3.1, 1.8), poly((2.75, 1.8), (3.3, 1.8), (3.2, 2.4), (2.85, 2.4)), poly((2.75, 2.4), (3.025, 2.75), (3.3, 2.4), closed=False)]
    ground = [[(-3.3, -2.8), (3.4, -2.8)]]
    return make("Couple on a Park Bench", p_out + bench + big + lamp + ground)


@design("valentine_wax_seal", T)
def wax_seal(rng):
    env = rect(-3.0, -2.9, 3.0, 0.5)
    flap = [(-3.0, 0.5), (0.3, -1.3), (3.0, 0.5)]
    folds = [[(-3.0, -2.9), (-0.9, -1.0)], [(3.0, -2.9), (1.4, -1.1)]]
    sc = (0.3, -1.3)
    blob = polar(lambda t: 1.15 + 0.08 * math.sin(7 * t) + 0.04 * math.sin(13 * t), cx=sc[0], cy=sc[1], n=240)
    rim = circle(sc[0], sc[1], 0.82, 70)
    h = hrt(sc[0], sc[1] - 0.05, 0.55)
    knob = circle(-1.9, 3.05, 0.5, 40)
    handle = chain(cubic((-2.15, 2.6), (-1.95, 2.1), (-2.4, 1.7), (-2.45, 1.25), 12), [(-1.35, 1.25)], cubic((-1.35, 1.25), (-1.4, 1.7), (-1.85, 2.1), (-1.65, 2.6), 12))
    ring = rect(-2.55, 0.95, -1.25, 1.25)
    brass = rrect(-2.45, 0.6, -1.35, 0.95, 0.1)
    out = hide([env, flap] + folds, blob, brass) + [blob, rim, h] + hide([handle], knob) + [knob, ring, brass]
    candle = [rect(1.9, 0.9, 2.5, 2.4), poly((2.2, 2.45), (2.05, 2.7), (2.2, 3.1), (2.35, 2.7)), ellipse(2.2, 0.85, 0.6, 0.15, 20)]
    return make("Wax Seal Stamp", out + candle + [hrt(-0.2, 2.2, 0.4, 0.3)])


@design("valentine_love_bug", T)
def love_bug(rng):
    shell = ellipse(0, -0.5, 1.9, 2.1, 100)
    head = ellipse(0, 1.65, 0.85, 0.6, 50)
    head = hide([head], shell)
    split = [[(0, 1.6), (0, -2.6)]]
    spots_ = [hrt(x, y, s) for x, y, s in [(-0.95, 0.4, 0.42), (0.95, 0.4, 0.42), (-1.1, -0.9, 0.38), (1.1, -0.9, 0.38), (-0.6, -1.9, 0.3), (0.6, -1.9, 0.3)]]
    spots_ = hide(spots_, *[[(0, 1.6), (0, -2.6)]][:0])
    ant = [quad((-0.3, 2.15), (-0.5, 2.8), (-1.1, 3.0), 10), quad((0.3, 2.15), (0.5, 2.8), (1.1, 3.0), 10)]
    tips = [hrt(-1.3, 3.05, 0.25), hrt(1.3, 3.05, 0.25)]
    legs = [[(-1.7, 0.3), (-2.4, 0.6), (-2.6, 1.0)], [(-1.85, -0.6), (-2.6, -0.6)], [(-1.6, -1.5), (-2.3, -2.0), (-2.4, -2.4)]]
    legs = legs + [mirror_x(l) for l in legs]
    legs = hide(legs, shell)
    leaf = hide([lens((-3.2, -2.9), (3.2, -1.6), 0.15), [(-3.2, -2.9), (3.2, -1.6)]], shell)
    return make("Love Bug Ladybug", [shell] + head + split + spots_ + ant + tips + legs + leaf, [eye(-0.35, 1.85, 0.1), eye(0.35, 1.85, 0.1)])


@design("valentine_heart_rain_cloud", T)
def heart_rain_cloud(rng):
    cs = [circle(-1.6, 1.0, 0.9, 50), circle(-0.4, 1.7, 1.15, 60), circle(0.9, 1.5, 1.0, 50), circle(1.9, 0.9, 0.75, 40), circle(0.2, 0.7, 0.9, 50)]
    flat = poly((-4, 0.3), (4, 0.3), (4, -4), (-4, -4))
    cloud = hide(union(*cs), flat) + [[(-2.45, 0.3), (2.6, 0.3)]]
    rainbow = hide([arc(0.2, -0.5, r, 0.15, math.pi - 0.15, 60) for r in (2.9, 3.3)], *cs, flat)
    face = [arc(-0.6, 1.25, 0.2, math.pi * 1.1, math.pi * 1.9, 8), arc(0.6, 1.25, 0.2, math.pi * 1.1, math.pi * 1.9, 8),
            arc(0, 1.0, 0.3, math.pi * 1.15, math.pi * 1.85, 10), circle(-1.0, 0.95, 0.15, 12), circle(1.0, 0.95, 0.15, 12)]
    drops = [hrt(x, y, s) for x, y, s in [(-1.8, -0.5, 0.35), (-0.7, -0.9, 0.4), (0.5, -0.5, 0.35), (1.6, -1.0, 0.4), (-1.3, -1.9, 0.3),
                                         (0.0, -2.0, 0.42), (1.1, -2.4, 0.3), (2.3, -2.2, 0.28), (-2.3, -2.6, 0.28)]]
    puddle = [ellipse(0, -2.95, 2.4, 0.25, 60)]
    drops = hide(drops, puddle[0])
    return make("Cloud Raining Hearts", cloud + rainbow + face + drops + puddle)


@design("valentine_teapot_of_love", T)
def teapot_of_love(rng):
    body = ellipse(-0.4, -0.7, 1.8, 1.45, 100)
    lid = chain(arc(-0.4, 0.55, 0.95, 0.15, math.pi - 0.15, 30))
    rim = [[(-1.35, 0.68), (0.55, 0.68)]]
    knob = hrt(-0.4, 1.75, 0.35)
    spout = chain(quad((1.2, -0.3), (2.1, -0.2), (2.5, 0.9), 10), [(2.8, 1.0), (2.7, 0.6)], quad((2.7, 0.6), (2.2, -0.7), (1.3, -1.2), 10))
    spout = hide([spout + [spout[0]]][0:1], body)
    handle = hide([arc(-2.2, -0.6, 0.85, math.pi / 2, 1.5 * math.pi, 20), arc(-2.2, -0.6, 0.55, math.pi / 2, 1.5 * math.pi, 16)], body)
    base = [poly((-1.4, -2.0), (-1.2, -2.35), (0.4, -2.35), (0.6, -2.0), closed=False)]
    deco = [hrt(-0.4, -0.6, 0.7), hrt(-0.4, -0.65, 0.48)]
    band = keep([wave(-2.5, 1.5, 0.1, 0.08, 6, 80)], body)
    steam = [hrt(2.9, 2.0, 0.3, -0.3), hrt(2.3, 2.6, 0.35, 0.2), hrt(2.9, 3.2, 0.25)]
    cup = [chain(arc(2.2, -1.8, 0.7, math.pi, 2 * math.pi, 20), [(1.5, -1.8)]), ellipse(2.2, -1.8, 0.7, 0.15, 24), ellipse(2.2, -2.55, 1.0, 0.18, 30)]
    cup[2] = hide([cup[2]], poly(*cup[0]))[0]
    cuph = arc(2.9, -2.0, 0.25, -1.2, 1.4, 8)
    return make("Teapot of Love", [body, lid] + rim + [knob] + spout + handle + base + deco + band + steam + cup + [cuph, hrt(2.2, -2.15, 0.22)])


@design("valentine_paris_eiffel", T)
def paris_eiffel(rng):
    left = [(-2.2, -3.0), (-1.5, -1.3), (-0.95, 0.4), (-0.45, 2.2), (-0.15, 3.3)]
    right = [mirror_x([p])[0] for p in left]
    outline = left + [(0, 3.9)] + right[::-1]
    arch = arc(0, -3.0, 1.3, 0.1, math.pi - 0.1, 30)
    plats = [[(-1.75, -1.3), (1.75, -1.3)], [(-1.75, -1.05), (1.75, -1.05)], [(-1.15, 0.4), (1.15, 0.4)], [(-1.1, 0.6), (1.1, 0.6)], [(-0.5, 2.2), (0.5, 2.2)]]
    lattice = []
    for y0, y1, w0, w1 in [(-3.0, -1.3, 2.2, 1.5), (-1.05, 0.4, 1.5, 0.95), (0.6, 2.2, 0.95, 0.45)]:
        lattice += [[(-w0, y0), (-w1 * 0.4, y1)], [(-w1, y1), (-w0 * 0.4, y0)], [(w0, y0), (w1 * 0.4, y1)], [(w1, y1), (w0 * 0.4, y0)]]
    region = poly(*outline)
    lattice = keep(hide(lattice, poly(*arch, (1.3, -3.2), (-1.3, -3.2))), region)
    hearts = [hrt(-2.4, 2.4, 0.5, 0.3), hrt(2.3, 2.0, 0.6, -0.3), hrt(-2.6, 0.5, 0.3), hrt(2.7, 0.3, 0.35), hrt(1.6, 3.4, 0.3)]
    ground = [[(-3.2, -3.0), (-2.2, -3.0)], [(2.2, -3.0), (3.2, -3.0)]]
    return make("Eiffel Tower with Hearts", [outline, arch] + plats + lattice + hearts + ground)


@design("valentine_winged_heart_banner", T)
def winged_heart_banner(rng):
    h = hrt(0, 0.3, 1.8)
    hi = hrt(0, 0.3, 1.45)
    wing = chain(cubic((1.4, 0.9), (2.2, 1.9), (3.2, 2.3), (3.5, 2.6), 16), [(3.3, 1.8)], arc(3.0, 1.6, 0.3, 0.3, -2.2, 8)[1:],
                 arc(2.6, 1.0, 0.3, 0.3, -2.2, 8)[1:], arc(2.1, 0.5, 0.3, 0.3, -2.2, 8)[1:], [(1.4, 0.2)])
    feathers = [quad((1.6, 0.7), (2.4, 1.5), (3.2, 2.0), 10), quad((1.6, 0.45), (2.2, 0.9), (2.7, 1.25), 8)]
    wings = hide([wing] + feathers + [mirror_x(w) for w in [wing] + feathers], h)
    band = chain(quad((-2.3, -0.3), (0, 0.2), (2.3, -0.3), 20), [(2.3, -1.0)], quad((2.3, -1.0), (0, -0.5), (-2.3, -1.0), 20), [(-2.3, -0.3)])
    ends = [poly((-2.3, -0.45), (-3.2, -0.55), (-2.8, -0.95), (-3.2, -1.35), (-2.3, -1.2), closed=False),
            poly((2.3, -0.45), (3.2, -0.55), (2.8, -0.95), (3.2, -1.35), (2.3, -1.2), closed=False)]
    txt = word("LOVE", 0, -0.42, 0.42)
    out = hide([h, hi], band) + wings + [band] + ends + txt
    roses = []
    for x, y in [(-0.75, -1.65), (0.75, -1.65)]:
        sh, c = rose(x, y, 0.5)
        out = hide(out, c) + sh
    lv = hide([lens((0, -1.8), (0, -2.8), 0.3), lens((-1.2, -1.9), (-2.0, -2.3), 0.3), lens((1.2, -1.9), (2.0, -2.3), 0.3)], *[rose(x, -1.65, 0.5)[1] for x in (-0.75, 0.75)])
    return make("Winged Heart with a Banner", out + lv)


@design("valentine_bow_and_quiver", T)
def bow_and_quiver(rng):
    q = transform(rrect(-0.55, -2.2, 0.55, 1.2, 0.3), 0.6, 0.0, rot=-0.35)
    band = keep([transform([(-1, y), (1, y)], 0.6, 0.0, rot=-0.35) for y in (0.75, 0.55, -1.7, -1.9)], q)
    strap = [quad((0.0, 1.1), (-1.6, 0.4), (0.1, -2.3), 14)][:0]
    arrows = []
    for dx, h in [(-0.25, 2.9), (0.05, 3.2), (0.35, 2.85)]:
        base = transform([(dx, 1.0), (dx, h)], 0.6, 0.0, rot=-0.35)
        tipc = transform([(dx, h + 0.25)], 0.6, 0.0, rot=-0.35)[0]
        arrows += [base, hrt(tipc[0], tipc[1], 0.28, -0.35)]
    arrows = hide(arrows, q)
    bowarc = arc(1.8, 0.0, 3.0, math.radians(135), math.radians(225), 40)
    bow_ = tube(bowarc, lambda t: 0.12 + 0.18 * math.sin(math.pi * t))
    string = [bowarc[0], bowarc[-1]]
    loose = [[(-2.5, -2.2), (2.6, 2.5)], hrt(2.75, 2.65, 0.3, -0.75)]
    fl = [lens((-2.5, -2.2), (-2.6, -1.6), 0.3), lens((-2.5, -2.2), (-1.9, -2.3), 0.3), lens((-2.25, -1.95), (-2.35, -1.35), 0.3), lens((-2.25, -1.95), (-1.65, -2.05), 0.3)]
    out = hide([bow_, string], q) + [q] + band + arrows + hide(loose, q, bow_) + hide(fl, q)
    return make("Cupid's Bow and Quiver", out)


@design("valentine_heart_locket", T)
def heart_locket(rng):
    loc = hrt(0, -0.9, 1.9)
    rim = hrt(0, -0.88, 1.6)
    scroll = [spiral(-0.55, -0.5, 0.05, 0.35, 1.5, 40), mirror_x(spiral(-0.55, -0.5, 0.05, 0.35, 1.5, 40)), hrt(0, -1.3, 0.45)]
    hinge = circle(0, 0.85, 0.22, 16)
    bail = ellipse(0, 1.3, 0.2, 0.32, 20)
    chain_pts = quad((-3.0, 3.2), (-0.5, 1.4), (0, 1.55), 30)
    links = []
    for k in range(0, 30, 3):
        (x0, y0), (x1, y1) = chain_pts[k], chain_pts[k + 3]
        a = math.atan2(y1 - y0, x1 - x0)
        links.append(ellipse((x0 + x1) / 2, (y0 + y1) / 2, 0.24, 0.1 if k % 6 else 0.12, 14, rot=a))
    links = links + [mirror_x(l) for l in links]
    out = hide(links, bail) + [bail] + hide([hinge], loc) + [loc, rim] + scroll
    sp = [star(-2.2, -1.6, 0.35, 4, 0.3), star(2.3, -1.2, 0.3, 4, 0.3)]
    return make("Heart Locket Necklace", out + sp)


@design("valentine_love_marquee", T)
def love_marquee(rng):
    board = rrect(-3.1, -1.4, 3.1, 1.4, 0.3)
    inner = rrect(-2.85, -1.15, 2.85, 1.15, 0.2)
    letters = []
    for k, ch in enumerate("LOVE"):
        x0 = -2.45 + 1.3 * k
        strokes = [transform(s, x0, -0.7, 1.4) for s in _GLYPH[ch]]
        tubes = []
        for s in strokes:
            if math.dist(s[0], s[-1]) < 1e-6:
                tubes += [ellipse(x0 + 0.42, 0.0, 0.62, 0.72, 50), ellipse(x0 + 0.42, 0.0, 0.32, 0.42, 40)]
            else:
                tubes.append(tube(s, 0.28))
        if ch == "O":
            letters += tubes
        else:
            letters += union(*tubes)
    bulbs = [circle(x, 1.27, 0.07, 8) for x in [-2.5 + 0.5 * k for k in range(11)]][:0]
    chains = [[(-2.2, 1.4), (-1.2, 2.8)], [(2.2, 1.4), (1.2, 2.8)]]
    nail = circle(0, 2.95, 0.15, 12)
    hearts = [hrt(-2.3, -2.2, 0.4), hrt(0, -2.4, 0.5), hrt(2.3, -2.2, 0.4)]
    return make("LOVE Sign", [board, inner] + letters + chains + [[(-1.2, 2.8), (0, 2.95), (1.2, 2.8)], nail] + hearts)


@design("valentine_heart_pizza", T)
def heart_pizza(rng):
    o = hrt(0, 0.1, 2.8)
    i = hrt(0, 0.12, 2.35)
    pep = [circle(x, y, r, 24) for x, y, r in [(-1.3, 1.1, 0.42), (1.3, 1.1, 0.42), (0.0, -0.3, 0.42), (-0.9, -0.6, 0.35), (0.9, -0.6, 0.35), (0.0, -1.6, 0.3)]]
    hp = [hrt(-0.6, 0.6, 0.32), hrt(0.6, 0.6, 0.32)]
    olives = [circle(x, y, 0.16, 12) for x, y in [(-1.9, 0.9), (1.9, 0.9), (-0.4, -1.1), (0.4, -1.1), (0.0, 0.5)][:4]]
    basil = [lens((-0.2, 1.3), (0.3, 1.6), 0.4), lens((-1.6, 0.2), (-1.2, 0.0), 0.4), lens((1.6, 0.2), (1.2, 0.0), 0.4)]
    cuts = hide(keep([[(0, -3), (0, 0.9)], [(-3, -0.1), (3, -0.1)]], i), *pep, *hp, *olives, *basil)
    cutter = [circle(2.6, -2.2, 0.55, 40), circle(2.6, -2.2, 0.12, 10), tube([(2.7, -1.75), (3.3, -0.7)], 0.24)]
    cutter = [cutter[0], cutter[1]] + hide([cutter[2]], cutter[0])
    return make("Heart-Shaped Pizza", hide([o], cutter[0]) + [i] + pep + hp + olives + basil + cuts + cutter)


@design("valentine_heart_cookies", T)
def heart_cookies(rng):
    plate = [circle(-0.4, 0, 2.9, 140), circle(-0.4, 0, 2.3, 120)]
    out = []
    cov = []
    for k, (x, y, s, r) in enumerate([(-1.3, 0.8, 0.95, 0.3), (0.6, 1.0, 0.9, -0.25), (-0.4, -0.6, 1.0, 0.0), (-1.6, -1.4, 0.8, -0.3), (0.9, -1.2, 0.85, 0.35)]):
        c = hrt(x, y, s, r)
        ic = hrt(x, y, s * 0.78, r)
        if k % 3 == 0:
            det = keep([transform(zigzag(-1.2, 1.2, 0, 0.12, 6), x, y - 0.1, rot=r)], ic)
        elif k % 3 == 1:
            det = keep([circle(x + dx, y + dy, 0.09, 8) for dx, dy in [(-0.3, 0.1), (0.3, 0.1), (0, -0.25), (0, 0.4)]], ic)
        else:
            det = [hrt(x, y - 0.05, s * 0.35, r)]
        out = hide(out, c) + [c, ic] + det
        cov.append(c)
    plate = hide(plate, *cov)
    glass = [rect(2.3, -2.9, 3.3, -0.2), [(2.3, -0.75), (3.3, -0.75)]]
    glass = hide(glass, circle(-0.4, 0, 2.9, 140))
    straw = [[(3.0, -0.2), (3.2, 0.9), (2.7, 1.3)]]
    return make("Plate of Heart Cookies", plate + out + glass + straw)


@design("valentine_love_candles", T)
def love_candles(rng):
    tray = hrt(0, -2.3, 3.1, sy=0.3)
    out = []
    for x, h, w in [(-1.5, 1.6, 0.6), (0.0, 2.8, 0.7), (1.5, 2.1, 0.6)]:
        top = -2.2 + h
        body = chain([(x - w, -2.2)], [(x - w, top)], [(x + w, top)], [(x + w, -2.2)])
        topel = ellipse(x, top, w, 0.18, 30)
        bot = arc(x, -2.2, w, math.pi, 2 * math.pi, 20)
        bot = [(px, -2.2 + (py + 2.2) * 0.3) for px, py in bot]
        wick = [(x, top), (x, top + 0.2)]
        flame = poly((x, top + 0.2), (x - 0.2, top + 0.5), (x, top + 1.0), (x + 0.2, top + 0.5))
        glow = [arc(x, top + 0.55, 0.45, 0.4, math.pi - 0.4, 10)]
        drip = [quad((x - w, top - 0.2), (x - w + 0.15, top - 0.6), (x - w + 0.3, top - 0.2), 6)]
        dec = [hrt(x, -2.2 + h * 0.45, 0.35 * w / 0.6)]
        out += [body, topel, bot, wick, flame] + glow + dec
    out = [tray] + [s for s in out]
    petals = [lens((-2.9, -2.9), (-2.5, -2.7), 0.4), lens((2.4, -2.9), (2.85, -2.75), 0.4)]
    tray_vis = hide([tray], *[rect(x - w, -2.6, x + w, -2.2 + h) for x, h, w in [(-1.5, 1.6, 0.6), (0.0, 2.8, 0.7), (1.5, 2.1, 0.6)]])
    return make("Love Candles", tray_vis + out[1:] + petals)


@design("valentine_heart_kite", T)
def heart_kite(rng):
    k = hrt(0.8, 1.2, 1.9, -0.3)
    spars = keep([transform([(0, -3), (0, 3)], 0.8, 1.2, rot=-0.3), transform([(-3, 0.2), (3, 0.2)], 0.8, 1.2, rot=-0.3)], k)
    tail_c = cubic((0.25, -0.75), (-1.0, -1.5), (0.0, -2.4), (-2.0, -2.9), 40)
    bows = []
    for f in (0.3, 0.6, 0.9):
        x, y = tail_c[int(f * 40)]
        bows += [lens((x, y), (x - 0.4, y + 0.3), 0.45), lens((x, y), (x + 0.4, y - 0.3), 0.45)]
    tail = hide([tail_c], *bows)
    line = [[(1.2, -0.5), (3.2, -3.0)]]
    clouds = []
    for cx, cy, s in [(-2.2, 2.0, 0.8), (2.4, -0.9, 0.6)]:
        cs = [circle(cx - 0.5 * s, cy, 0.45 * s, 30), circle(cx, cy + 0.25 * s, 0.6 * s, 30), circle(cx + 0.55 * s, cy, 0.42 * s, 30)]
        clouds += hide(union(*cs), poly((cx - 2, cy - 0.3 * s), (cx + 2, cy - 0.3 * s), (cx + 2, cy - 3), (cx - 2, cy - 3))) + [[(cx - 0.95 * s, cy - 0.3 * s), (cx + 0.97 * s, cy - 0.3 * s)]]
    clouds = hide(clouds, k)
    inner = hrt(0.8, 1.2, 1.2, -0.3)
    spars = hide(spars, inner)
    return make("Heart Kite", [k, inner] + spars + tail + bows + hide(line, k) + clouds)


@design("valentine_gnome", T)
def gnome(rng):
    hat = chain([(-1.5, 0.5)], cubic((-1.5, 0.5), (-1.0, 2.0), (0.0, 3.3), (1.6, 3.4), 24), cubic((1.6, 3.4), (0.6, 2.8), (1.2, 1.2), (1.5, 0.5), 20), [(-1.5, 0.5)])
    brim = rrect(-1.7, 0.2, 1.7, 0.65, 0.2)
    nose = circle(0, 0.0, 0.48, 40)
    beard = chain(cubic((-1.3, 0.25), (-1.45, -1.2), (-0.6, -2.0), (0, -2.35), 24),
                  cubic((0, -2.35), (0.6, -2.0), (1.45, -1.2), (1.3, 0.25), 24))
    curls = keep([arc(x, y, 0.25, math.pi, 2 * math.pi, 8) for x, y in [(-0.8, -0.8), (0.0, -1.1), (0.8, -0.8), (-0.4, -1.7), (0.4, -1.7)]], beard)
    big = hrt(1.6, -1.0, 0.9)
    hand = [ellipse(1.0, -0.85, 0.28, 0.22, 16), ellipse(2.2, -0.85, 0.28, 0.22, 16)]
    body = chain(quad((-1.55, 0.2), (-2.2, -1.6), (-1.9, -2.6), 12), quad((1.9, -2.6), (2.2, -1.6), (1.55, 0.2), 12))
    boots = [chain([(-1.3, -2.6)], arc(-1.3, -2.85, 0.25, math.pi / 2, 1.5 * math.pi, 8), [(-0.4, -3.1), (-0.4, -2.6)]),
             chain([(1.3, -2.6)], arc(1.3, -2.85, 0.25, math.pi / 2, -math.pi / 2, 8), [(0.4, -3.1), (0.4, -2.6)])]
    dots = keep([hrt(x, y, 0.22) for x, y in [(-0.7, 1.2), (0.3, 1.6), (-0.1, 2.4), (0.8, 2.9), (-0.9, 0.9)]], hat)
    out = hide([hat], brim) + [brim] + dots + hide([beard], nose, big, *hand) + [nose] + hide(curls, nose, big) + [big, hrt(1.6, -1.0, 0.6)] + hand
    out += hide([body], beard + [beard[0]], big, *hand, brim) + boots
    return make("Valentine Gnome", out)


@design("valentine_milkshake_for_two", T)
def milkshake_for_two(rng):
    glass = chain([(-1.4, 0.6)], cubic((-1.4, 0.6), (-1.2, -0.8), (-0.4, -1.3), (-0.25, -1.4), 14), [(-0.2, -2.3), (-1.0, -2.6), (1.0, -2.6), (0.2, -2.3), (0.25, -1.4)],
                  cubic((0.25, -1.4), (0.4, -1.3), (1.2, -0.8), (1.4, 0.6), 14))
    rim = ellipse(0, 0.6, 1.4, 0.25, 50)
    cream = chain([(-1.35, 0.7)], *[arc(-0.95 + 0.65 * k, 0.75, 0.38, math.pi, 0, 10)[0:] for k in range(4)], [(1.35, 0.7)])
    cream2 = chain(*[arc(-0.6 + 0.6 * k, 1.35, 0.35, math.pi, 0, 10) for k in range(3)])
    cream_top = chain(arc(0, 1.75, 0.4, math.pi, 0, 12))
    cherry = [circle(0, 2.35, 0.3, 20), quad((0, 2.65), (0.1, 3.0), (0.45, 3.2), 8)]
    straws = [tube([(-0.5, 1.2), (-1.3, 3.0), (-2.1, 3.3)], 0.22), tube([(0.5, 1.2), (1.3, 3.0), (2.1, 3.3)], 0.22)]
    straws = hide(straws, cherry[0], poly(*cream2, (1.2, 0.8), (-1.2, 0.8)), poly(*cream_top))
    deco = keep([hrt(0, -0.4, 0.45)], poly(*glass, (-1.4, 0.6)))
    hearts = [hrt(-2.4, 1.0, 0.4, 0.3), hrt(2.5, 0.8, 0.45, -0.3)]
    out = [glass, rim] + hide([cream], ) + hide([cream2], ) + [cream_top] + cherry + straws + deco + hearts
    return make("Milkshake with Two Straws", out)


@design("valentine_moon_and_hearts", T)
def moon_and_hearts(rng):
    outer = arc(-0.6, 0.2, 2.6, math.radians(60), math.radians(300), 80)
    inner = arc(0.5, 0.2, 2.0, math.radians(232), math.radians(128), 60)
    moon = chain(outer, inner[::-1][::-1])
    face = [arc(-1.2, 0.6, 0.3, math.pi * 1.1, math.pi * 1.9, 10), arc(-1.05, -0.4, 0.4, math.pi * 1.2, math.pi * 1.8, 10), circle(-1.7, 0.0, 0.2, 14)]
    strings = [[(0.8, 2.2), (0.8, 1.0)], [(1.8, 1.4), (1.8, -0.3)], [(0.9, -1.8), (1.0, -2.6)]]
    hearts = [hrt(0.8, 0.7, 0.4), hrt(1.8, -0.6, 0.45), hrt(1.0, -2.95, 0.4)]
    stars_ = [star(x, y, r) for x, y, r in [(2.8, 2.6, 0.35), (2.6, 0.9, 0.25), (-2.9, 2.8, 0.3), (2.9, -1.6, 0.3), (-3.0, -2.6, 0.25)]]
    cloud = [circle(-1.8, -2.6, 0.45, 30), circle(-1.1, -2.4, 0.6, 30), circle(-0.4, -2.65, 0.45, 30)]
    cl = hide(union(*cloud), poly((-3, -2.85), (1, -2.85), (1, -4), (-3, -4))) + [[(-2.25, -2.85), (0.05, -2.85)]]
    moon_vis = hide([moon], *cloud)
    return make("Love You to the Moon", moon_vis + face + strings + hearts + stars_ + cl)


@design("valentine_penguins_in_love", T)
def penguins_in_love(rng):
    def penguin(cx, s, flip):
        body = ellipse(cx, -0.9 * s, 1.15 * s, 1.75 * s, 80)
        head = circle(cx, 1.15 * s, 0.85 * s, 50)
        sil = union(body, head)
        belly = chain(arc(cx, -1.1 * s, 0.75 * s, math.pi * 0.5, math.pi * 2.5, 40))
        face = [ellipse(cx - 0.3 * s * flip, 1.0 * s, 0.35 * s, 0.45 * s, 24), ellipse(cx + 0.3 * s * flip, 1.0 * s, 0.35 * s, 0.45 * s, 24)]
        face = union(*face)
        beak = poly((cx + 0.55 * flip * s, 0.95 * s), (cx + 1.1 * flip * s, 0.8 * s), (cx + 0.55 * flip * s, 0.65 * s))
        flip_w = lens((cx + 0.95 * flip * s, 0.0), (cx + 1.6 * flip * s, -0.9 * s), 0.3)
        feet = [ellipse(cx - 0.45 * s, -2.65 * s, 0.4 * s, 0.15 * s, 16), ellipse(cx + 0.45 * s, -2.65 * s, 0.4 * s, 0.15 * s, 16)]
        return hide(sil, beak, flip_w) + [belly] + face + [beak] + hide([flip_w], body) + hide(feet, body), [body, head, beak, flip_w]
    a, ac = penguin(-1.55, 1.0, 1)
    b, bc = penguin(1.55, 1.0, -1)
    big = hrt(0, 0.0, 0.75)
    out = hide(a, big) + hide(b, big) + [big, hrt(0, 0.0, 0.5)]
    ice = [[(-3.2, -2.8), (3.2, -2.8)]]
    tiny = [hrt(0, 2.4, 0.4), hrt(-0.6, 1.8, 0.25, 0.3), hrt(0.6, 1.9, 0.25, -0.3)]
    return make("Penguins in Love", out + ice + tiny, [eye(-1.2, 1.1, 0.1), eye(1.2, 1.1, 0.1)])


@design("valentine_linked_hearts", T)
def linked_hearts(rng):
    def band(cx, cy, s):
        o = hrt(cx, cy, s)
        i = hrt(cx, cy, s * 0.78)
        return [o, i], o + i
    A, Ar = band(-0.85, 0.2, 2.0)
    B, Br = band(0.85, -0.2, 2.0)
    left = poly((-4, -4), (0, -4), (0, 4), (-4, 4))
    right = poly((0, -4), (4, -4), (4, 4), (0, 4))
    out = hide(keep(B, right), Ar) + keep(B, left) + hide(keep(A, left), Br) + keep(A, right)
    rb, rc = bow(0, -2.5, 0.8)
    sp = [star(-2.8, 2.6, 0.3, 4, 0.3), star(2.9, 2.4, 0.3, 4, 0.3)]
    return make("Two Linked Hearts", hide(out, *rc) + rb + sp)


@design("valentine_floral_heart", T)
def floral_heart(rng):
    path = hrt(0, 0.1, 2.5)
    n = len(path) - 1
    out, covers = [], []
    for j, k in enumerate(range(0, n, 10)):
        x, y = path[k]
        if j % 3 == 0:
            sh, c = rose(x, y, 0.42)
            cs = [c]
        else:
            sh, cs = flower(x, y, 0.5 if j % 3 == 1 else 0.42, 5 if j % 3 == 1 else 6, 0.3 * j)
        out = hide(out, *cs) + sh
        covers += cs
    leaves = []
    for k in range(5, n, 10):
        (x0, y0), (x1, y1) = path[k], path[(k + 2) % n]
        a = math.atan2(y1 - y0, x1 - x0)
        sg = 1 if (k // 10) % 2 else -1
        leaves.append(lens((x0, y0), (x0 + 0.6 * math.cos(a + sg * 1.3), y0 + 0.6 * math.sin(a + sg * 1.3)), 0.3))
    leaves = hide(leaves, *covers)
    vine = hide([path], *covers)
    centre = [hrt(0, 0.1, 0.9)]
    return make("Heart of Flowers", vine + leaves + out + centre)


@design("valentine_owls_in_love", T)
def owls_in_love(rng):
    def owl(cx, flip):
        body = ellipse(cx, 0.0, 1.2, 1.7, 80)
        ears = [poly((cx - 0.95, 1.0), (cx - 1.05, 2.0), (cx - 0.45, 1.5), closed=False), poly((cx + 0.95, 1.0), (cx + 1.05, 2.0), (cx + 0.45, 1.5), closed=False)]
        eyes_ = [circle(cx - 0.45, 0.85, 0.42, 30), circle(cx + 0.45, 0.85, 0.42, 30)]
        eyes_ = union(*eyes_)
        beak = poly((cx - 0.15, 0.45), (cx + 0.15, 0.45), (cx, 0.05))
        wing = lens((cx + 1.0 * flip, 0.4), (cx + 0.8 * flip, -1.4), 0.25)
        belly = keep([chain(*[arc(cx - 0.6 + 0.4 * k, y, 0.2, math.pi, 2 * math.pi, 6) for k in range(4)]) for y in (-0.5, -0.9, -1.3)], ellipse(cx, -0.6, 0.85, 1.0, 40))
        return [body] + ears + eyes_ + [beak, wing] + belly, [body]
    a, _ = owl(-1.25, -1)
    b, _ = owl(1.25, 1)
    branch = [[(-3.3, -1.9), (3.3, -1.7)], [(-3.3, -2.2), (3.3, -2.0)], [(2.2, -1.75), (3.0, -1.0)]]
    branch = hide(branch, ellipse(-1.25, 0, 1.2, 1.7, 80), ellipse(1.25, 0, 1.2, 1.7, 80))
    feet = [[(x, -1.6), (x, -1.85)] for x in (-1.6, -0.9, 0.9, 1.6)]
    big = hrt(0, 2.5, 0.65)
    leaves = [lens((-2.8, -1.85), (-3.2, -1.2), 0.35), lens((2.6, -1.25), (2.3, -0.6), 0.35)]
    return make("Owls in Love", a + b + branch + feet + [big] + leaves, [eye(-1.55, 0.85, 0.14), eye(-0.95, 0.85, 0.14), eye(0.95, 0.85, 0.14), eye(1.55, 0.85, 0.14)])
