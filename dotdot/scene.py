"""Full-page scenes for 1,000-2,000 dot puzzles.

An outline-only picture cannot carry 2,000 readable dots on a letter page:
the dots would have to sit almost on top of each other.  Commercial
"extreme" books get their density from page-filling artwork, so the scene
builder turns a design into a coloring-book style page:

* the subject stays big and its lines stay untouched;
* the background (inside the dotted border, outside the subject) is
  covered by one coherent pattern - waves, ripples, diagonals ...;
* the inside of the subject gets a contrasting pattern (scales, zigzags).

Pattern lines are clipped so they keep a clear gap from every subject line,
and their spacing is computed so that the page carries the requested
number of dots at a readable dot spacing.
"""
import math

import numpy as np

from .designs import Design
from .geometry import TAU, bounds, path_length

BG_PATTERNS = {
    "sea": ["waves", "waves", "ripples"],
    "travel": ["waves", "diagonal", "ripples"],
    "animals": ["ripples", "waves", "diagonal", "spiral"],
    "flowers": ["ripples", "spiral", "diagonal"],
    "nature": ["waves", "ripples", "diagonal"],
    "patterns": ["ripples", "spiral", "diagonal"],
    "custom": ["waves", "ripples", "diagonal"],
    "misc": ["waves", "ripples", "diagonal"],
}
IN_PATTERNS = {
    "sea": ["scales"],
    "animals": ["scales", "zigzag", "waves"],
    "nature": ["zigzag", "waves", "scales"],
    "flowers": ["waves", "zigzag"],
    "travel": ["zigzag", "scales", "waves"],
    "custom": ["zigzag", "scales", "waves"],
    "misc": ["zigzag", "scales", "waves"],
    "patterns": [],  # geometric designs are already busy inside
}


# ------------------------------------------------------------- patterns
# Each returns polylines covering the box (x0, y0, x1, y1) at spacing `sep`.

def _waves(box, sep, rng, amp=0.28, zig=False):
    x0, y0, x1, y1 = box
    lam = sep * rng.uniform(2.6, 3.4)
    phase_step = rng.uniform(0.6, 1.4)
    out = []
    y = y0 + sep / 2
    k = 0
    while y < y1:
        xs = np.arange(x0 - sep, x1 + sep, sep / 8)
        if zig:
            t = (xs / lam * 2) % 2
            ys = y + amp * sep * (2 * np.abs(t - 1) - 1)
        else:
            ys = y + amp * sep * np.sin(TAU * xs / lam + k * phase_step)
        out.append(list(zip(xs.tolist(), ys.tolist())))
        y += sep
        k += 1
    return out


def _diagonal(box, sep, rng):
    x0, y0, x1, y1 = box
    a = rng.choice([math.pi / 4, -math.pi / 4, math.pi / 3, -math.pi / 3])
    dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = math.hypot(x1 - x0, y1 - y0) / 2
    out = []
    o = -R
    while o <= R:
        px, py = cx + nx * o, cy + ny * o
        out.append([(px - dx * R + dx * R * 2 * i / 60, py - dy * R + dy * R * 2 * i / 60) for i in range(61)])
        o += sep
    return out


def _ripples(box, sep, rng, centre=None):
    x0, y0, x1, y1 = box
    if centre is None:
        centre = rng.choice([(x0, y0), (x1, y0), (x0, y1), (x1, y1), ((x0 + x1) / 2, (y0 + y1) / 2)])
    cx, cy = centre
    R = max(math.hypot(px - cx, py - cy) for px in (x0, x1) for py in (y0, y1))
    out = []
    r = sep * 0.75
    while r < R:
        n = max(24, int(TAU * r / (sep / 6)))
        out.append([(cx + r * math.cos(TAU * i / n), cy + r * math.sin(TAU * i / n)) for i in range(n + 1)])
        r += sep
    return out


def _spiral(box, sep, rng, centre=None):
    x0, y0, x1, y1 = box
    cx, cy = centre or ((x0 + x1) / 2, (y0 + y1) / 2)
    R = max(math.hypot(px - cx, py - cy) for px in (x0, x1) for py in (y0, y1))
    pts = []
    t = TAU
    while sep * t / TAU < R:
        r = sep * t / TAU
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
        t += min(0.3, (sep / 6) / r)
    return [pts]


def _scales(box, sep, rng):
    x0, y0, x1, y1 = box
    r = sep * 0.62
    out = []
    row = 0
    y = y0
    while y < y1 + r:
        off = (row % 2) * r
        x = x0 - r + off
        while x < x1 + r:
            out.append([(x + r * math.cos(a), y + r * math.sin(a)) for a in np.linspace(math.pi, TAU, 18)])
            x += 2 * r
        y += r * 0.95
        row += 1
    return out


def make_pattern(name, box, sep, rng, centre=None):
    if name == "waves":
        return _waves(box, sep, rng)
    if name == "zigzag":
        return _waves(box, sep, rng, amp=0.22, zig=True)
    if name == "diagonal":
        return _diagonal(box, sep, rng)
    if name == "ripples":
        return _ripples(box, sep, rng, centre)
    if name == "spiral":
        return _spiral(box, sep, rng, centre)
    if name == "scales":
        return _scales(box, sep, rng)
    raise ValueError(name)


# ------------------------------------------------------------- masks

def _densify(stroke, step):
    out = []
    for a, b in zip(stroke, stroke[1:]):
        n = max(1, int(math.dist(a, b) / step))
        for k in range(n):
            out.append((a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n))
    out.append(stroke[-1])
    return out


class _Field:
    def __init__(self, box, cols):
        self.x0, self.y0, x1, y1 = box
        self.cell = (x1 - self.x0) / cols
        self.cols = cols
        self.rows = int(math.ceil((y1 - self.y0) / self.cell)) + 1

    def ij(self, x, y):
        return int((y - self.y0) / self.cell), int((x - self.x0) / self.cell)

    def raster(self, strokes, grow=0):
        m = np.zeros((self.rows, self.cols), bool)
        for s in strokes:
            for x, y in _densify(s, self.cell * 0.5):
                i, j = self.ij(x, y)
                if 0 <= i < self.rows and 0 <= j < self.cols:
                    m[max(0, i - grow):i + grow + 1, max(0, j - grow):j + grow + 1] = True
        return m

    def flood_from_edges(self, wall):
        seen = np.zeros_like(wall)
        R, C = wall.shape
        stack = [(i, j) for i in range(R) for j in (0, C - 1)] + [(i, j) for i in (0, R - 1) for j in range(C)]
        while stack:
            i, j = stack.pop()
            if 0 <= i < R and 0 <= j < C and not seen[i, j] and not wall[i, j]:
                seen[i, j] = True
                stack.extend(((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)))
        return seen

    @staticmethod
    def distance(occ):
        """Chamfer (3-4) distance to the nearest occupied cell, in cells."""
        R, C = occ.shape
        INF = 10 ** 6
        d = [[0 if occ[i, j] else INF for j in range(C)] for i in range(R)]
        for i in range(R):
            row = d[i]
            up = d[i - 1] if i else None
            for j in range(C):
                v = row[j]
                if v == 0:
                    continue
                if j:
                    v = min(v, row[j - 1] + 3)
                if up is not None:
                    v = min(v, up[j] + 3)
                    if j:
                        v = min(v, up[j - 1] + 4)
                    if j < C - 1:
                        v = min(v, up[j + 1] + 4)
                row[j] = v
        for i in range(R - 1, -1, -1):
            row = d[i]
            dn = d[i + 1] if i < R - 1 else None
            for j in range(C - 1, -1, -1):
                v = row[j]
                if v == 0:
                    continue
                if j < C - 1:
                    v = min(v, row[j + 1] + 3)
                if dn is not None:
                    v = min(v, dn[j] + 3)
                    if j < C - 1:
                        v = min(v, dn[j + 1] + 4)
                    if j:
                        v = min(v, dn[j - 1] + 4)
                row[j] = v
        return np.array(d, float) / 3.0


def _clip(lines, field, ok, min_len):
    """Split pattern lines into runs that stay inside the `ok` mask."""
    out = []
    for line in lines:
        run = []
        for x, y in _densify(line, field.cell * 0.5):
            i, j = field.ij(x, y)
            good = 0 <= i < field.rows and 0 <= j < field.cols and ok[i, j]
            if good:
                run.append((x, y))
            else:
                if len(run) > 1 and path_length(run) >= min_len:
                    out.append(run)
                run = []
        if len(run) > 1 and path_length(run) >= min_len:
            out.append(run)
    return out


# ------------------------------------------------------------- builder

def fill_scene(d, rng, need_length, unit, cols=150, max_sep_pt=60.0, min_sep_pt=15.0):
    """Return a copy of `d` with background/interior patterns added.

    need_length: total line length (design units) the page should carry.
    unit:        design units per printed point (to set clearances).
    """
    border = d.border
    box = bounds(border)
    # Pad the grid so the flood fill can start outside the border.
    m = (box[2] - box[0]) * 0.03
    f = _Field((box[0] - m, box[1] - m, box[2] + m, box[3] + m), cols)
    border_ids = {id(b) for b in border}
    subject = [s for s in d.strokes if id(s) not in border_ids]

    subj_wall = f.raster(subject + d.hints, grow=1)
    border_wall = f.raster(border, grow=1)
    beyond = f.flood_from_edges(border_wall)          # outside the border
    outside = f.flood_from_edges(subj_wall)            # not enclosed by the subject
    occ = f.raster(subject + d.hints + border)
    dist_pt = f.distance(occ) * f.cell / unit           # printed points

    clear_pt = 9.0
    free = dist_pt > clear_pt
    bg_mask = free & outside & ~beyond & ~border_wall
    in_mask = free & ~outside & ~subj_wall

    have = sum(path_length(s) for s in d.strokes)
    extra = need_length - have
    if extra <= 0:
        return d
    in_names = IN_PATTERNS.get(d.theme, IN_PATTERNS["misc"])
    cell_area = f.cell ** 2
    area = bg_mask.sum() * cell_area + (in_mask.sum() * cell_area if in_names else 0)
    if area <= 0:
        return d
    min_len = 30.0 * unit

    bg_name = rng.choice(BG_PATTERNS.get(d.theme, BG_PATTERNS["misc"]))
    in_name = rng.choice(in_names) if in_names else None
    # Centre for ripples/spirals: the subject's middle, so rings echo it.
    sx0, sy0, sx1, sy1 = bounds(subject) if subject else box
    centre = ((sx0 + sx1) / 2, (sy0 + sy1) / 2) if rng.random() < 0.6 else None

    lo, hi = min_sep_pt * unit, max_sep_pt * unit
    sep = min(hi, max(lo, area / extra))
    added = []
    for _ in range(6):  # refine the spacing until the total length fits
        added = _clip(make_pattern(bg_name, box, sep, rng, centre), f, bg_mask, min_len)
        if in_name:
            added += _clip(make_pattern(in_name, box, sep * 0.8, rng, centre), f, in_mask, min_len)
        got = sum(path_length(s) for s in added)
        if got <= 0:
            break
        ratio = got / extra
        if 0.92 <= ratio <= 1.12:
            break
        new = min(hi, max(lo, sep * ratio))
        if abs(new - sep) < 1e-9:
            break
        sep = new
    return Design(d.title, d.strokes + added, d.hints, d.theme, border)
