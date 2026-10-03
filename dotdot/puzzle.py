"""Turn a Design into a numbered dot-to-dot puzzle laid out on a page."""
import math
from collections import defaultdict
from dataclasses import dataclass, field

from reportlab.pdfbase.pdfmetrics import stringWidth

from .geometry import bounds, fit_spacing, dots_for_spacing, order_strokes, path_length

CAP = 0.72  # cap height / font size for the number font
CLAIM_PENALTY = 400  # number nearer to another dot than to its own


@dataclass
class Label:
    num: int
    x: float      # lower-left of text baseline
    y: float
    w: float
    h: float
    bold: bool = False
    overlap: float = 0.0


@dataclass
class Puzzle:
    title: str
    theme: str
    sections: list            # list of lists of (x, y) page points
    hints: list               # pre-drawn polylines in page points
    labels: list = field(default_factory=list)
    font_size: float = 6.0
    dot_r: float = 0.9
    frame: tuple = (0, 0, 0, 0)

    @property
    def dot_count(self):
        return sum(len(s) for s in self.sections)

    @property
    def section_count(self):
        return len(self.sections)

    defects: int = 0  # numbers that could be misread (see audit_labels)

    @property
    def collisions(self):
        return self.defects


class _Grid:
    """Uniform spatial hash for rectangles."""

    def __init__(self, cell):
        self.cell = cell
        self.cells = defaultdict(list)

    def _keys(self, r):
        c = self.cell
        for gx in range(int(math.floor(r[0] / c)), int(math.floor(r[2] / c)) + 1):
            for gy in range(int(math.floor(r[1] / c)), int(math.floor(r[3] / c)) + 1):
                yield gx, gy

    def add(self, r, item):
        for k in self._keys(r):
            self.cells[k].append((r, item))

    def remove(self, r, item):
        for k in self._keys(r):
            lst = self.cells[k]
            for i, (rr, it) in enumerate(lst):
                if it is item:
                    lst.pop(i)
                    break

    def query(self, r):
        seen = set()
        for k in self._keys(r):
            for rr, it in self.cells.get(k, ()):
                if id(it) not in seen:
                    seen.add(id(it))
                    yield rr, it


def _rect_dist(p, r):
    dx = max(r[0] - p[0], 0.0, p[0] - r[2])
    dy = max(r[1] - p[1], 0.0, p[1] - r[3])
    return math.hypot(dx, dy)


def _inter(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return w * h if w > 0 and h > 0 else 0.0


def fit_to_frame(design, frame, pad):
    x0, y0, x1, y1 = frame
    bx0, by0, bx1, by1 = bounds(design.strokes + design.hints)
    bw, bh = bx1 - bx0, by1 - by0
    fw, fh = (x1 - x0) - 2 * pad, (y1 - y0) - 2 * pad
    s = min(fw / bw, fh / bh)
    ox = x0 + pad + (fw - bw * s) / 2 - bx0 * s
    oy = y0 + pad + (fh - bh * s) / 2 - by0 * s

    def tf(stroke):
        return [(ox + x * s, oy + y * s) for x, y in stroke]

    return [tf(st) for st in design.strokes], [tf(h) for h in design.hints]


def make_puzzle(design, frame, target_dots, font_size=6.0, dot_r=None, font="Num", bold_font="NumBold",
                milestone=100, pad=None):
    pad = font_size * 2.2 if pad is None else pad
    strokes, hints = fit_to_frame(design, frame, pad)
    strokes = order_strokes(strokes)
    floor = font_size * 1.2  # never let dots get so close that numbers cannot fit
    spacing = max(fit_spacing(strokes, target_dots), floor)
    # Shapes too small to carry several readable numbers (tiny circles, the
    # cores of spirals) are printed as solid hint lines instead of dots.
    tiny = [s for s in strokes if path_length(s) < floor * 5]
    if tiny:
        keep = [s for s in strokes if path_length(s) >= floor * 5]
        hints = hints + tiny
        strokes = order_strokes(keep)
        spacing = max(fit_spacing(strokes, target_dots), floor)
    def sample(sp):
        secs = [s for s in dots_for_spacing(strokes, sp) if len(s) >= 2]
        secs = _merge_near_duplicates(secs, font_size * 0.35)
        return _thin_crowded(secs, font_size * 1.05)

    sections = sample(spacing)
    # Thinning removes dots where lines bunch up; win them back elsewhere by
    # tightening the spacing (never below the readable floor).
    for _ in range(5):
        n = sum(len(s) for s in sections)
        if n >= target_dots * 0.98 or spacing <= floor:
            break
        spacing = max(floor, spacing * (n / target_dots) ** 0.9)
        sections = sample(spacing)
    pz = Puzzle(design.title, design.theme, sections, hints, font_size=font_size,
                dot_r=dot_r or max(0.7, font_size * 0.15), frame=frame)
    place_labels(pz, font, bold_font, milestone)
    # Repair: a dot whose number could be misread is removed (the line
    # simply runs straight past it) and the page is renumbered.
    for _ in range(10):
        bad = audit_labels(pz)
        if not bad:
            break
        _drop_dots(pz, bad)
        place_labels(pz, font, bold_font, milestone)
    pz.defects = len(audit_labels(pz))
    return pz


def _merge_near_duplicates(sections, tol):
    """Drop consecutive dots that would sit on top of each other."""
    out = []
    for s in sections:
        keep = [s[0]]
        for p in s[1:]:
            if p is s[0] or math.dist(p, keep[-1]) > tol:
                keep.append(p)
        if len(keep) >= 2:
            out.append(keep)
    return out


def _thin_crowded(sections, min_gap):
    """Where lines cross or run close together, dots pile up and their
    numbers become unreadable.  Drop interior dots that sit too close to a
    dot already kept elsewhere; the drawn line still follows the shape."""
    grid = defaultdict(list)
    cell = min_gap

    touch_gap = min_gap * 0.55  # endpoints are only dropped if nearly touching

    def near(p, skip, gap=None):
        gap = min_gap if gap is None else gap
        gx, gy = int(p[0] // cell), int(p[1] // cell)
        for i in (gx - 1, gx, gx + 1):
            for j in (gy - 1, gy, gy + 1):
                for q in grid.get((i, j), ()):
                    if q is not skip and math.dist(p, q) < gap:
                        return True
        return False

    out = []
    for sec in sections:
        keep = []
        for k, p in enumerate(sec):
            endpoint = k == 0 or k == len(sec) - 1
            if p is sec[0] and k > 0:
                if not keep or keep[0] is not sec[0]:
                    continue  # the loop's start was dropped, so is its end
            elif not endpoint and near(p, keep[-1] if keep else None):
                continue
            elif endpoint and near(p, keep[-1] if keep else None, touch_gap):
                continue
            keep.append(p)
            if p is not sec[0] or k == 0:
                grid[(int(p[0] // cell), int(p[1] // cell))].append(p)
        if len(keep) >= 2:
            out.append(keep)
    return out


class _PointGrid:
    """Spatial hash of points (dots, line samples) for fast neighbourhood scans."""

    def __init__(self, cell):
        self.cell = cell
        self.cells = defaultdict(list)

    def add(self, p, item):
        self.cells[(int(p[0] // self.cell), int(p[1] // self.cell))].append((p, item))

    def near(self, r):
        c = self.cell
        for gx in range(int(r[0] // c), int(r[2] // c) + 1):
            for gy in range(int(r[1] // c), int(r[3] // c) + 1):
                yield from self.cells.get((gx, gy), ())


CLAIM_MARGIN = 1.2   # placement: own dot must be this much closer than any other
AUDIT_MARGIN = 0.6   # audit: anything tighter than this counts as ambiguous


def _flat_dots(pz):
    out = []
    for si, sec in enumerate(pz.sections):
        for i, p in enumerate(sec):
            prev = sec[i - 1] if i > 0 else None
            nxt = sec[i + 1] if i < len(sec) - 1 else None
            out.append((p, prev, nxt, si, i))
    return out


def place_labels(pz, font, bold_font, milestone):
    fs = pz.font_size
    h = fs * CAP
    r = pz.dot_r
    fx0, fy0, fx1, fy1 = pz.frame
    inset = 2.0
    dots = _flat_dots(pz)

    dot_grid = _PointGrid(8.0)
    for idx, d in enumerate(dots):
        dot_grid.add(d[0], idx)
    # Sample the lines the solver will draw so numbers avoid sitting on them.
    line_grid = _PointGrid(8.0)
    step = fs * 0.5
    for sec in pz.sections:
        for a, b in zip(sec, sec[1:]):
            n = max(1, int(math.dist(a, b) / step))
            for k in range(1, n):
                t = k / n
                line_grid.add((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), None)
    for hint in pz.hints:
        for q in hint[::2]:
            line_grid.add(q, None)
    label_grid = _Grid(max(8.0, fs * 2))

    angles = [math.radians(a) for a in range(0, 360, 20)]
    pad_x, pad_y = 0.9, 0.45   # visible gap kept between two numbers

    def candidates(idx):
        p, prev, nxt = dots[idx][:3]
        num = idx + 1
        bold = bool(milestone) and num % milestone == 0
        w = stringWidth(str(num), bold_font if bold else font, fs)
        # Preferred direction: away from the neighbouring line segments.
        vx = vy = 0.0
        for q in (prev, nxt):
            if q is not None:
                dx, dy = p[0] - q[0], p[1] - q[1]
                L = math.hypot(dx, dy) or 1
                vx += dx / L
                vy += dy / L
        pref = math.atan2(vy, vx) if math.hypot(vx, vy) > 0.2 else None
        out = []
        # Corner anchors: the label's nearest corner sits just off the dot,
        # so even a wide 4-digit number stays closest to its own dot.
        for gap in (0.5, 1.2, 2.2):
            for sx in (-1, 1):
                for sy in (-1, 1):
                    x0 = p[0] + r + gap if sx > 0 else p[0] - r - gap - w
                    y0 = p[1] + r * 0.5 + gap * 0.6 if sy > 0 else p[1] - r * 0.5 - gap * 0.6 - h
                    a = math.atan2(sy, sx)
                    bias = gap * 0.9 + (0.8 * (1 - math.cos(a - pref)) if pref is not None else 0.2)
                    out.append(((x0, y0, x0 + w, y0 + h), bias, w, bold))
        for gap in (0.6, 1.6, 3.0):
            for a in angles:
                ca, sa = math.cos(a), math.sin(a)
                ext = abs(ca) * w / 2 + abs(sa) * h / 2
                cx = p[0] + ca * (r + gap + ext)
                cy = p[1] + sa * (r + gap + ext)
                bias = gap * 0.9
                if pref is not None:
                    bias += 0.8 * (1 - math.cos(a - pref))
                else:
                    bias += 0.25 * (1 - abs(math.sin(a)))  # lines run straight: prefer above/below
                out.append(((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), bias, w, bold))
        return out

    def cost(rect, bias, idx, skip_label=None):
        p = dots[idx][0]
        c = bias
        if rect[0] < fx0 + inset or rect[2] > fx1 - inset or rect[1] < fy0 + inset or rect[3] > fy1 - inset:
            c += 1e5
        d_own = _rect_dist(p, rect)
        reach = d_own + CLAIM_MARGIN + r + 0.5
        for q, j in dot_grid.near((rect[0] - reach, rect[1] - reach, rect[2] + reach, rect[3] + reach)):
            if q is p or q == p:
                continue
            d = _rect_dist(q, rect)
            if d < d_own + CLAIM_MARGIN:
                c += CLAIM_PENALTY + 120 * (d_own + CLAIM_MARGIN - d)
            if d < r + 0.6:
                c += 60
        for q, _ in line_grid.near(rect):
            if rect[0] <= q[0] <= rect[2] and rect[1] <= q[1] <= rect[3]:
                c += 2.5
        padded = (rect[0] - pad_x, rect[1] - pad_y, rect[2] + pad_x, rect[3] + pad_y)
        for rr, lab in label_grid.query(padded):
            if lab is skip_label:
                continue
            a = _inter(padded, rr)
            if a > 0:
                c += 60 + 25 * a
        return c

    labels, rects = [], []
    for idx in range(len(dots)):
        best = None
        for rect, bias, w, bold in candidates(idx):
            c = cost(rect, bias, idx)
            if best is None or c < best[0]:
                best = (c, rect, w, bold)
        c, rect, w, bold = best
        lab = Label(idx + 1, rect[0], rect[1], w, h, bold)
        labels.append(lab)
        rects.append(rect)
        label_grid.add(rect, lab)

    # Refinement: re-seat labels now that every label is known.
    for _ in range(3):
        moved = 0
        for idx, lab in enumerate(labels):
            rect = rects[idx]
            cur = cost(rect, 0, idx, skip_label=lab)
            if cur < 1:
                continue
            best = None
            for cand, bias, w, bold in candidates(idx):
                cc = cost(cand, bias, idx, skip_label=lab)
                if best is None or cc < best[0]:
                    best = (cc, cand)
            if best[0] + 0.5 < cur:
                label_grid.remove(rect, lab)
                rects[idx] = best[1]
                lab.x, lab.y = best[1][0], best[1][1]
                label_grid.add(best[1], lab)
                moved += 1
        if not moved:
            break
    pz.labels = labels


def audit_labels(pz):
    """Indices of dots whose number could be misread: closer (or nearly as
    close) to another dot, overlapping or touching another number, covering
    another dot, or outside the frame.  Returns {index: reason}."""
    dots = _flat_dots(pz)
    r = pz.dot_r
    fx0, fy0, fx1, fy1 = pz.frame
    dot_grid = _PointGrid(8.0)
    for idx, d in enumerate(dots):
        dot_grid.add(d[0], idx)
    label_grid = _Grid(max(8.0, pz.font_size * 2))
    rects = [(l.x, l.y, l.x + l.w, l.y + l.h) for l in pz.labels]
    for i, rc in enumerate(rects):
        label_grid.add(rc, i)
    bad = {}
    for idx, rect in enumerate(rects):
        p = dots[idx][0]
        if rect[0] < fx0 or rect[2] > fx1 or rect[1] < fy0 or rect[3] > fy1:
            bad[idx] = "outside frame"
            continue
        d_own = _rect_dist(p, rect)
        reach = d_own + AUDIT_MARGIN + 1
        for q, j in dot_grid.near((rect[0] - reach, rect[1] - reach, rect[2] + reach, rect[3] + reach)):
            if q is p or q == p:
                continue
            d = _rect_dist(q, rect)
            if d < d_own + AUDIT_MARGIN:
                bad[idx] = "ambiguous"
                break
            if d < r:
                bad[idx] = "covers a dot"
                break
        if idx in bad:
            continue
        padded = (rect[0] - 0.8, rect[1] - 0.3, rect[2] + 0.8, rect[3] + 0.3)
        for rr, j in label_grid.query(padded):
            if j != idx and _inter(padded, rr) > 0:
                bad[max(idx, j)] = "touches a number"
    return bad


def _drop_dots(pz, indices):
    """Remove the given dots (flat indices) keeping every line valid."""
    dots = _flat_dots(pz)
    kill = defaultdict(set)
    for idx in indices:
        _, _, _, si, i = dots[idx]
        kill[si].add(i)
    new = []
    for si, sec in enumerate(pz.sections):
        k = kill.get(si)
        if not k:
            new.append(sec)
            continue
        closed = len(sec) > 2 and sec[-1] is sec[0]
        if closed:
            last = len(sec) - 1
            body = [p for i, p in enumerate(sec[:-1]) if i not in k]
            if (0 in k or last in k) and len(body) >= 4:
                # Trouble at the start/closing dot: drop the start (if it is
                # still there) and restart the loop from its middle.
                if sec[0] in body and body[0] is sec[0]:
                    body = body[1:]
                half = len(body) // 2
                body = body[half:] + body[:half]
            if len(body) >= 3:
                new.append(body + [body[0]])
            elif len(body) >= 2:
                new.append(body)
        else:
            body = [p for i, p in enumerate(sec) if i not in k]
            if len(body) >= 2:
                new.append(body)
    pz.sections = new
