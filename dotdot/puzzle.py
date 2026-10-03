"""Turn a Design into a numbered dot-to-dot puzzle laid out on a page."""
import math
from collections import defaultdict
from dataclasses import dataclass, field

from reportlab.pdfbase.pdfmetrics import stringWidth

from .geometry import bounds, fit_spacing, dots_for_spacing, order_strokes

CAP = 0.72  # cap height / font size for the number font


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

    @property
    def collisions(self):
        return sum(1 for l in self.labels if l.overlap > 0.5)


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
    spacing = fit_spacing(strokes, target_dots)
    # Never let dots get so close that their numbers cannot fit.
    spacing = max(spacing, font_size * 1.3)
    sections = [s for s in dots_for_spacing(strokes, spacing) if len(s) >= 2]
    sections = _merge_near_duplicates(sections, font_size * 0.35)
    sections = _thin_crowded(sections, font_size * 1.05)
    pz = Puzzle(design.title, design.theme, sections, hints, font_size=font_size,
                dot_r=dot_r or max(0.7, font_size * 0.15), frame=frame)
    place_labels(pz, font, bold_font, milestone)
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

    def near(p, skip):
        gx, gy = int(p[0] // cell), int(p[1] // cell)
        for i in (gx - 1, gx, gx + 1):
            for j in (gy - 1, gy, gy + 1):
                for q in grid.get((i, j), ()):
                    if q is not skip and math.dist(p, q) < min_gap:
                        return True
        return False

    out = []
    for sec in sections:
        keep = []
        for k, p in enumerate(sec):
            endpoint = k == 0 or k == len(sec) - 1
            if not endpoint and near(p, keep[-1] if keep else None):
                continue
            keep.append(p)
            if p is not sec[0] or k == 0:
                grid[(int(p[0] // cell), int(p[1] // cell))].append(p)
        if len(keep) >= 2:
            out.append(keep)
    return out


def place_labels(pz, font, bold_font, milestone):
    fs = pz.font_size
    h = fs * CAP
    r = pz.dot_r
    fx0, fy0, fx1, fy1 = pz.frame
    inset = 2.0

    dots = []
    for sec in pz.sections:
        for i, p in enumerate(sec):
            prev = sec[i - 1] if i > 0 else None
            nxt = sec[i + 1] if i < len(sec) - 1 else None
            dots.append((p, prev, nxt))

    grid = _Grid(max(8.0, fs * 2))
    dot_rects = []
    for (p, _, _) in dots:
        rr = r + 0.6
        rect = (p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr)
        dot_rects.append(rect)
        grid.add(rect, ("dot", p))
    # Sample the lines the solver will draw so numbers avoid sitting on them.
    step = fs * 0.5
    for sec in pz.sections:
        for a, b in zip(sec, sec[1:]):
            L = math.dist(a, b)
            n = max(1, int(L / step))
            for k in range(1, n):
                t = k / n
                q = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                grid.add((q[0] - 0.3, q[1] - 0.3, q[0] + 0.3, q[1] + 0.3), ("line", q))
    for hint in pz.hints:
        for q in hint[::2]:
            grid.add((q[0] - 0.4, q[1] - 0.4, q[0] + 0.4, q[1] + 0.4), ("line", q))

    angles = [math.radians(a) for a in range(0, 360, 20)]
    labels = []
    rects = []

    def candidates(idx):
        (p, prev, nxt) = dots[idx]
        num = idx + 1
        bold = milestone and num % milestone == 0
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
        for gap in (0.6, 1.6, 3.0):
            for a in angles:
                ca, sa = math.cos(a), math.sin(a)
                ext = abs(ca) * w / 2 + abs(sa) * h / 2
                cx = p[0] + ca * (r + gap + ext)
                cy = p[1] + sa * (r + gap + ext)
                rect = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
                bias = gap * 0.9
                if pref is not None:
                    bias += 0.8 * (1 - math.cos(a - pref))
                else:
                    bias += 0.25 * (1 - abs(math.sin(a)))  # lines run straight: prefer above/below
                out.append((rect, bias, w, bold))
        return out

    def cost(rect, bias, own_dot):
        c = bias
        if rect[0] < fx0 + inset or rect[2] > fx1 - inset or rect[1] < fy0 + inset or rect[3] > fy1 - inset:
            c += 1e5
        for rr, it in grid.query(rect):
            a = _inter(rect, rr)
            if a <= 0:
                continue
            kind = it[0] if isinstance(it, tuple) else "label"
            if kind == "dot":
                c += 40 + 30 * a if it[1] is not own_dot else 0
            elif kind == "line":
                c += 2.5
            else:
                c += 60 + 25 * a
        return c

    for idx in range(len(dots)):
        best = None
        for rect, bias, w, bold in candidates(idx):
            c = cost(rect, bias, dots[idx][0])
            if best is None or c < best[0]:
                best = (c, rect, w, bold)
        c, rect, w, bold = best
        lab = Label(idx + 1, rect[0], rect[1], w, h, bold)
        labels.append(lab)
        rects.append(rect)
        grid.add(rect, lab)

    # Refinement: re-seat labels that still collide, now that every label is known.
    for _ in range(3):
        moved = 0
        for idx, lab in enumerate(labels):
            rect = rects[idx]
            grid.remove(rect, lab)
            cur = cost(rect, 0, dots[idx][0])
            best = None
            for cand, bias, w, bold in candidates(idx):
                c = cost(cand, bias, dots[idx][0])
                if best is None or c < best[0]:
                    best = (c, cand)
            if best[0] + 0.5 < cur:
                rect = best[1]
                rects[idx] = rect
                lab.x, lab.y = rect[0], rect[1]
                moved += 1
            grid.add(rect, lab)
        if not moved:
            break

    for idx, lab in enumerate(labels):
        rect = rects[idx]
        ov = 0.0
        for rr, it in grid.query(rect):
            if it is lab:
                continue
            if isinstance(it, Label) or (isinstance(it, tuple) and it[0] == "dot" and it[1] is not dots[idx][0]):
                ov += _inter(rect, rr)
        lab.overlap = ov
    pz.labels = labels
