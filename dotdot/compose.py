"""Unique multi-subject scenes for a whole book series.

Every puzzle is a scene: one main subject drawn large plus one or two
smaller companion subjects that fit its theme (a cat with a butterfly and
a flower, a whale with an anchor ...).  `plan_series` plans every volume of
a series at once, so no scene - the same main subject with the same
companions - is ever used twice anywhere in the series, and no main subject
is over-used inside one book.
"""
import hashlib
import math
import random

from . import designs
from .designs import Design
from .geometry import bounds, transform

# Abstract geometric designs read badly next to pictures; scenes skip them.
ABSTRACT = {"mandala", "spirograph", "snowflake", "dragon", "star"}

# Which themes make sensible companions for a main subject's theme.
FRIENDS = {
    "sea": ["sea", "travel"],
    "animals": ["animals", "nature", "flowers"],
    "nature": ["nature", "flowers", "animals"],
    "flowers": ["flowers", "nature", "animals"],
    "travel": ["travel", "misc", "patterns"],
    "misc": ["misc", "patterns", "flowers"],
    "patterns": ["patterns", "misc", "flowers", "travel"],
    "christmas": ["christmas"],
    "thanksgiving": ["thanksgiving"],
}

SEP = " · "  # joins subject titles in a scene title


def scene_pool(themes=None, holiday=False):
    """Design names usable in scenes, limited to `themes` if given."""
    out = []
    for name, (_, theme) in designs.REGISTRY.items():
        if name in ABSTRACT:
            continue
        if themes:
            if theme in themes:
                out.append(name)
        elif holiday == (theme in designs.HOLIDAY_THEMES):
            out.append(name)
    return out


def _theme(name):
    return designs.REGISTRY[name][1]


def plan_series(pool, books, per_book, seed):
    """Plan `books` volumes of `per_book` scenes each.

    Returns a list (one per volume) of (main, (companion, ...)) keys.
    Keys are unique across the whole series; inside a volume the main
    subjects are spread as evenly as possible and never repeat back to back.
    """
    rng = random.Random(seed)
    used = set()
    plan = []
    for _ in range(books):
        # Main subjects: cycle through the pool so each is used about
        # per_book / len(pool) times per volume.
        mains = []
        while len(mains) < per_book:
            batch = pool[:]
            rng.shuffle(batch)
            if mains and batch[0] == mains[-1]:
                batch.append(batch.pop(0))
            mains += batch
        mains = mains[:per_book]
        volume = []
        for main in mains:
            friends = [n for n in pool if n != main and _theme(n) in FRIENDS.get(_theme(main), [])]
            others = [n for n in pool if n != main and n not in friends]
            key = None
            for attempt in range(400):
                k = 1 if rng.random() < 0.35 else 2
                src = friends if len(friends) >= k and attempt < 300 else friends + others
                comp = tuple(sorted(rng.sample(src, k)))
                cand = (main, comp)
                if cand not in used:
                    key = cand
                    break
            if key is None:
                raise RuntimeError(f"ran out of unique scenes for {main}")
            used.add(key)
            volume.append(key)
        plan.append(volume)
    return plan


def key_seed(key, salt=0):
    h = hashlib.sha1(repr((key, salt)).encode()).hexdigest()
    return int(h[:12], 16)


def _normalise(d, size):
    """Scale a design so its larger side is `size`, bbox at the origin."""
    x0, y0, x1, y1 = bounds(d.strokes + d.hints)
    s = size / max(x1 - x0, y1 - y0)
    f = lambda pts: [((x - x0) * s, (y - y0) * s) for x, y in pts]
    return [f(p) for p in d.strokes], [f(p) for p in d.hints], ((x1 - x0) * s, (y1 - y0) * s)


def compose(key, aspect, seed):
    """Build the Design for a scene key.  `aspect` is page width / height."""
    main_name, comps = key
    rng = random.Random(seed)
    main = designs.build(main_name, key_seed(key, 1))
    strokes, hints, (mw, mh) = _normalise(main, 1.0)
    boxes = [(0.0, 0.0, mw, mh)]
    gap = 0.06
    size = rng.uniform(0.42, 0.5) if len(comps) == 1 else rng.uniform(0.34, 0.42)
    titles = [main.title]
    for i, name in enumerate(comps):
        d = designs.build(name, key_seed(key, 2 + i))
        cs, ch, (cw, chh) = _normalise(d, size * rng.uniform(0.9, 1.1))
        best = None
        x0, y0, x1, y1 = _union(boxes)
        # Candidate spots hugging the current group: beside it (top, middle,
        # bottom) or above/below it (left, centre, right).
        spots = []
        for fy in (0.0, 0.5, 1.0):
            y = y0 + (y1 - y0 - chh) * fy
            spots.append((x1 + gap, y))
            spots.append((x0 - gap - cw, y))
        for fx in (0.0, 0.5, 1.0):
            x = x0 + (x1 - x0 - cw) * fx
            spots.append((x, y1 + gap))
            spots.append((x, y0 - gap - chh))
        for sx, sy in spots:
            box = (sx, sy, sx + cw, sy + chh)
            if any(_overlap(box, b, gap * 0.5) for b in boxes):
                continue
            ux0, uy0, ux1, uy1 = _union(boxes + [box])
            w, h = ux1 - ux0, uy1 - uy0
            # Prefer layouts close to the page shape and compact.
            score = abs(math.log((w / h) / aspect)) * 2.0 + (w * h) * 0.25 + rng.uniform(0, 0.05)
            if best is None or score < best[0]:
                best = (score, sx, sy, box)
        _, sx, sy, box = best
        strokes += [transform(p, dx=sx, dy=sy) for p in cs]
        hints += [transform(p, dx=sx, dy=sy) for p in ch]
        boxes.append(box)
        titles.append(d.title)
    return Design(SEP.join(titles), strokes, hints, main.theme)


def _union(boxes):
    return (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))


def _overlap(a, b, pad):
    return a[0] < b[2] + pad and b[0] < a[2] + pad and a[1] < b[3] + pad and b[1] < a[3] + pad
