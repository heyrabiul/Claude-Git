"""Geometry helpers: primitive shape builders, dot sampling and SVG import.

All shapes are lists of (x, y) tuples ("strokes").  Designs use a y-up
coordinate system; they are normalised onto the page later.
"""
import math
import re
import xml.etree.ElementTree as ET

import numpy as np

TAU = 2 * math.pi


# ---------------------------------------------------------------- primitives

def parametric(fx, fy, t0, t1, n=600):
    ts = np.linspace(t0, t1, n)
    return [(float(fx(t)), float(fy(t))) for t in ts]


def polar(fr, t0=0.0, t1=TAU, n=800, cx=0.0, cy=0.0, rot=0.0):
    ts = np.linspace(t0, t1, n)
    return [(cx + fr(t) * math.cos(t + rot), cy + fr(t) * math.sin(t + rot)) for t in ts]


def circle(cx, cy, r, n=120, start=0.0):
    return ellipse(cx, cy, r, r, n=n, start=start)


def ellipse(cx, cy, rx, ry, n=160, start=0.0, rot=0.0):
    pts = []
    c, s = math.cos(rot), math.sin(rot)
    for i in range(n + 1):
        t = start + TAU * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return pts


def arc(cx, cy, r, a0, a1, n=60):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n),
             cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def cubic(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append((u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                    u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]))
    return out


def quad(p0, p1, p2, n=30):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
    return out


def chain(*parts):
    """Join several point lists end to end, dropping duplicated joints."""
    out = []
    for p in parts:
        for q in p:
            if not out or math.dist(out[-1], q) > 1e-9:
                out.append(q)
    return out


def transform(pts, dx=0.0, dy=0.0, s=1.0, rot=0.0, sx=None, sy=None):
    sx = s if sx is None else sx
    sy = s if sy is None else sy
    c, n = math.cos(rot), math.sin(rot)
    return [(dx + (x * sx) * c - (y * sy) * n, dy + (x * sx) * n + (y * sy) * c) for x, y in pts]


def mirror_x(pts, axis=0.0):
    return [(2 * axis - x, y) for x, y in pts]


def bounds(strokes):
    xs = [p[0] for s in strokes for p in s]
    ys = [p[1] for s in strokes for p in s]
    return min(xs), min(ys), max(xs), max(ys)


def is_closed(pts, tol=1e-6):
    return len(pts) > 2 and math.dist(pts[0], pts[-1]) <= tol * max(1.0, _extent(pts))


def _extent(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return max(max(xs) - min(xs), max(ys) - min(ys))


def path_length(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


# ---------------------------------------------------------------- sampling

def _turn_angles(pts, closed):
    n = len(pts)
    ang = [0.0] * n
    for i in range(n):
        if not closed and (i == 0 or i == n - 1):
            continue
        a = pts[i - 1] if i > 0 else pts[-2]
        b = pts[i]
        c = pts[i + 1] if i < n - 1 else pts[1]
        v1 = (b[0] - a[0], b[1] - a[1])
        v2 = (c[0] - b[0], c[1] - b[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        if l1 < 1e-12 or l2 < 1e-12:
            continue
        cosv = max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (l1 * l2)))
        ang[i] = math.acos(cosv)
    return ang


def _dedupe(pts):
    out = []
    for p in pts:
        if not out or math.dist(out[-1], p) > 1e-9:
            out.append(p)
    return out


def sample_stroke(pts, spacing, corner_deg=38.0, bend_weight=0.55, min_dots=3):
    """Place dots along a polyline.

    Dots are spread evenly by a "cost" that is arc length plus a bonus for
    bending, so tight curves get extra dots while long straight runs stay
    sparse.  Sharp corners are always kept as dots so the drawn picture
    keeps its crisp points.
    """
    pts = _dedupe(pts)
    if len(pts) < 2:
        return pts[:]
    closed = is_closed(pts)
    if closed:
        pts[-1] = pts[0]
    ang = _turn_angles(pts, closed)
    corner = math.radians(corner_deg)

    # A corner is a local spike of turning angle (dense smooth curves turn a
    # little at every vertex; a cusp turns a lot at one vertex).
    corners = {0, len(pts) - 1}
    for i, a in enumerate(ang):
        if a >= corner:
            corners.add(i)
    corners = sorted(corners)
    if closed and len(corners) == 2:
        # No real corners: start on the top-most point for a natural start.
        pass

    cost = [0.0]
    for i in range(1, len(pts)):
        seg = math.dist(pts[i - 1], pts[i])
        cost.append(cost[-1] + seg + bend_weight * spacing * ang[i - 1] / (math.pi / 2))

    def point_at(c, lo, hi):
        # Binary search the cost array between indices lo..hi.
        a, b = lo, hi
        while b - a > 1:
            m = (a + b) // 2
            if cost[m] <= c:
                a = m
            else:
                b = m
        span = cost[b] - cost[a]
        t = 0.0 if span <= 0 else (c - cost[a]) / span
        return (pts[a][0] + (pts[b][0] - pts[a][0]) * t,
                pts[a][1] + (pts[b][1] - pts[a][1]) * t)

    out = [pts[0]]
    for ci, cj in zip(corners, corners[1:]):
        span = cost[cj] - cost[ci]
        k = max(1, int(round(span / spacing)))
        for j in range(1, k):
            out.append(point_at(cost[ci] + span * j / k, ci, cj))
        out.append(pts[cj])

    if closed:
        # A loop ends back on its start dot: that dot carries two numbers.
        out[-1] = out[0]
        if len(out) - 1 < max(min_dots, 6):
            return sample_stroke(pts, spacing * 0.6, corner_deg, bend_weight, min_dots)
    elif len(out) < min_dots and len(out) >= 2:
        return sample_stroke(pts, spacing * 0.6, corner_deg, bend_weight, min_dots)
    return out


def dots_for_spacing(strokes, spacing, **kw):
    return [sample_stroke(s, spacing, **kw) for s in strokes]


def fit_spacing(strokes, target, **kw):
    """Find the spacing that yields roughly `target` dots in total."""
    total = sum(path_length(s) for s in strokes)
    lo, hi = total / (target * 8), total / max(1, target / 8)
    best = None
    for _ in range(28):
        mid = math.sqrt(lo * hi)
        n = sum(len(d) for d in dots_for_spacing(strokes, mid, **kw))
        best = (mid, n) if best is None or abs(n - target) < abs(best[1] - target) else best
        if n > target:
            lo = mid
        else:
            hi = mid
        if abs(n - target) <= max(2, target * 0.01):
            break
    return best[0]


def order_strokes(strokes):
    """Greedy ordering (and reversal) so each new section starts near the
    end of the previous one; closed strokes are rotated to start at the
    point nearest the pen."""
    remaining = [list(s) for s in strokes if len(s) >= 2]
    if not remaining:
        return []
    # Start with the stroke whose start point is highest (top-left reading).
    remaining.sort(key=lambda s: (-max(p[1] for p in s), min(p[0] for p in s)))
    ordered = [remaining.pop(0)]
    while remaining:
        end = ordered[-1][-1]
        best_i, best_d, best_mode = 0, float("inf"), None
        for i, s in enumerate(remaining):
            if is_closed(s):
                j = min(range(len(s) - 1), key=lambda k: math.dist(end, s[k]))
                d, mode = math.dist(end, s[j]), ("rot", j)
            else:
                d0, d1 = math.dist(end, s[0]), math.dist(end, s[-1])
                d, mode = (d0, ("fwd",)) if d0 <= d1 else (d1, ("rev",))
            if d < best_d:
                best_i, best_d, best_mode = i, d, mode
        s = remaining.pop(best_i)
        if best_mode[0] == "rev":
            s = s[::-1]
        elif best_mode[0] == "rot":
            j = best_mode[1]
            body = s[:-1]
            s = body[j:] + body[:j] + [body[j]]
        ordered.append(s)
    return ordered


# ---------------------------------------------------------------- SVG import

_NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"


def _mat_mul(a, b):
    return (a[0] * b[0] + a[2] * b[1], a[1] * b[0] + a[3] * b[1],
            a[0] * b[2] + a[2] * b[3], a[1] * b[2] + a[3] * b[3],
            a[0] * b[4] + a[2] * b[5] + a[4], a[1] * b[4] + a[3] * b[5] + a[5])


def _parse_transform(text):
    m = (1, 0, 0, 1, 0, 0)
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", text or ""):
        v = [float(x) for x in re.findall(_NUM, args)]
        if name == "matrix" and len(v) == 6:
            t = tuple(v)
        elif name == "translate":
            t = (1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0)
        elif name == "scale":
            t = (v[0], 0, 0, v[1] if len(v) > 1 else v[0], 0, 0)
        elif name == "rotate":
            a = math.radians(v[0])
            r = (math.cos(a), math.sin(a), -math.sin(a), math.cos(a), 0, 0)
            if len(v) == 3:
                t = _mat_mul(_mat_mul((1, 0, 0, 1, v[1], v[2]), r), (1, 0, 0, 1, -v[1], -v[2]))
            else:
                t = r
        elif name == "skewX":
            t = (1, 0, math.tan(math.radians(v[0])), 1, 0, 0)
        elif name == "skewY":
            t = (1, math.tan(math.radians(v[0])), 0, 1, 0, 0)
        else:
            continue
        m = _mat_mul(m, t)
    return m


def _apply(m, pts):
    return [(m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5]) for x, y in pts]


def _arc_to(p0, rx, ry, phi, large, sweep, p1, n=40):
    # SVG endpoint arc -> centre parameterisation (SVG spec F.6.5).
    if rx == 0 or ry == 0:
        return [p1]
    phi = math.radians(phi)
    cp, sp = math.cos(phi), math.sin(phi)
    dx, dy = (p0[0] - p1[0]) / 2, (p0[1] - p1[1]) / 2
    x1, y1 = cp * dx + sp * dy, -sp * dx + cp * dy
    rx, ry = abs(rx), abs(ry)
    lam = x1 * x1 / (rx * rx) + y1 * y1 / (ry * ry)
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1 * y1 - ry * ry * x1 * x1
    den = rx * rx * y1 * y1 + ry * ry * x1 * x1
    co = math.sqrt(max(0.0, num / den)) if den else 0.0
    if large == sweep:
        co = -co
    cx1, cy1 = co * rx * y1 / ry, -co * ry * x1 / rx
    cx = cp * cx1 - sp * cy1 + (p0[0] + p1[0]) / 2
    cy = sp * cx1 + cp * cy1 + (p0[1] + p1[1]) / 2

    def ang(u, v):
        a = math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1])
        return a

    t1 = ang((1, 0), ((x1 - cx1) / rx, (y1 - cy1) / ry))
    dt = ang(((x1 - cx1) / rx, (y1 - cy1) / ry), ((-x1 - cx1) / rx, (-y1 - cy1) / ry))
    if not sweep and dt > 0:
        dt -= TAU
    elif sweep and dt < 0:
        dt += TAU
    out = []
    for i in range(1, n + 1):
        t = t1 + dt * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append((cp * x - sp * y + cx, sp * x + cp * y + cy))
    return out


def parse_path_d(d):
    """Parse an SVG path `d` attribute into a list of polylines."""
    tokens = re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|" + _NUM, d)
    strokes, cur = [], []
    x = y = sx = sy = 0.0
    last_ctrl = None
    cmd = None
    i = 0

    def nums(k):
        nonlocal i
        vals = [float(t) for t in tokens[i:i + k]]
        i += k
        return vals

    while i < len(tokens):
        if re.match(r"[A-Za-z]", tokens[i]):
            cmd = tokens[i]
            i += 1
            if cmd in "Zz":
                if cur:
                    cur.append((sx, sy))
                    strokes.append(cur)
                cur = []
                x, y = sx, sy
                last_ctrl = None
                continue
        if cmd is None:
            break
        rel = cmd.islower()
        c = cmd.upper()
        ox, oy = (x, y) if rel else (0.0, 0.0)
        if c == "M":
            nx, ny = nums(2)
            if cur and len(cur) > 1:
                strokes.append(cur)
            x, y = ox + nx, oy + ny
            sx, sy = x, y
            cur = [(x, y)]
            cmd = "l" if rel else "L"
            last_ctrl = None
        elif c == "L":
            nx, ny = nums(2)
            x, y = ox + nx, oy + ny
            cur.append((x, y))
            last_ctrl = None
        elif c == "H":
            (nx,) = nums(1)
            x = ox + nx
            cur.append((x, y))
            last_ctrl = None
        elif c == "V":
            (ny,) = nums(1)
            y = oy + ny
            cur.append((x, y))
            last_ctrl = None
        elif c in "CS":
            if c == "C":
                x1, y1, x2, y2, ex, ey = nums(6)
                p1 = (ox + x1, oy + y1)
            else:
                x2, y2, ex, ey = nums(4)
                p1 = (2 * x - last_ctrl[0], 2 * y - last_ctrl[1]) if last_ctrl else (x, y)
            p2 = (ox + x2, oy + y2)
            p3 = (ox + ex, oy + ey)
            cur.extend(cubic((x, y), p1, p2, p3, 24)[1:])
            last_ctrl = p2
            x, y = p3
        elif c in "QT":
            if c == "Q":
                x1, y1, ex, ey = nums(4)
                p1 = (ox + x1, oy + y1)
            else:
                ex, ey = nums(2)
                p1 = (2 * x - last_ctrl[0], 2 * y - last_ctrl[1]) if last_ctrl else (x, y)
            p2 = (ox + ex, oy + ey)
            cur.extend(quad((x, y), p1, p2, 18)[1:])
            last_ctrl = p1
            x, y = p2
        elif c == "A":
            rx, ry, phi, large, sweep, ex, ey = nums(7)
            p1 = (ox + ex, oy + ey)
            cur.extend(_arc_to((x, y), rx, ry, phi, int(large), int(sweep), p1))
            x, y = p1
            last_ctrl = None
        else:
            i += 1
    if cur and len(cur) > 1:
        strokes.append(cur)
    return strokes


def load_svg(path):
    """Read stroke geometry from an SVG file.

    Best results come from *line art* (single strokes along each contour),
    e.g. a centre-line trace.  Filled shapes are read by their outline.
    Elements whose id or class contains "hint" are returned separately as
    pre-drawn hint lines (like the eyes printed in many dot-to-dot books).
    """
    tree = ET.parse(path)
    root = tree.getroot()
    strokes, hints = [], []

    def tag(el):
        return el.tag.split("}")[-1]

    def walk(el, m, hint):
        m = _mat_mul(m, _parse_transform(el.get("transform")))
        name = (el.get("id") or "") + " " + (el.get("class") or "")
        hint = hint or "hint" in name.lower()
        t = tag(el)
        found = []
        if t == "path" and el.get("d"):
            found = parse_path_d(el.get("d"))
        elif t in ("polyline", "polygon"):
            v = [float(n) for n in re.findall(_NUM, el.get("points", ""))]
            pts = list(zip(v[0::2], v[1::2]))
            if t == "polygon" and pts:
                pts.append(pts[0])
            found = [pts]
        elif t == "line":
            g = lambda k: float(el.get(k, 0))
            found = [[(g("x1"), g("y1")), (g("x2"), g("y2"))]]
        elif t in ("circle", "ellipse"):
            g = lambda k: float(el.get(k, 0))
            rx = g("r") if t == "circle" else g("rx")
            ry = g("r") if t == "circle" else g("ry")
            found = [ellipse(g("cx"), g("cy"), rx, ry, n=90)]
        elif t == "rect":
            g = lambda k: float(el.get(k, 0))
            x0, y0, w, h = g("x"), g("y"), g("width"), g("height")
            found = [[(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h), (x0, y0)]]
        for s in found:
            s = _apply(m, s)
            if len(s) >= 2:
                (hints if hint else strokes).append([(px, -py) for px, py in s])  # SVG is y-down
        for child in el:
            if tag(child) not in ("defs", "clipPath", "mask", "metadata", "title", "desc"):
                walk(child, m, hint)

    walk(root, (1, 0, 0, 1, 0, 0), False)
    return strokes, hints
