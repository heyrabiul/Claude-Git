"""Small drawing helpers shared by the niche design modules."""
import math

from ..designs import Design, design  # noqa: F401  (re-exported for modules)
from ..geometry import (TAU, arc, chain, circle, cubic, ellipse, mirror_x,  # noqa: F401
                        parametric, polar, quad, transform)


def poly(*pts, closed=True):
    pts = list(pts)
    return pts + [pts[0]] if closed else pts


def rect(x0, y0, x1, y1):
    return poly((x0, y0), (x1, y0), (x1, y1), (x0, y1))


def rrect(x0, y0, x1, y1, r):
    """Rounded rectangle."""
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    return chain(arc(x1 - r, y0 + r, r, -math.pi / 2, 0, 8), arc(x1 - r, y1 - r, r, 0, math.pi / 2, 8),
                 arc(x0 + r, y1 - r, r, math.pi / 2, math.pi, 8), arc(x0 + r, y0 + r, r, math.pi, 1.5 * math.pi, 8),
                 [(x1 - r, y0)])


def lens(p0, p1, bulge=0.35, n=24):
    """Leaf / petal shape between two points."""
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    c1 = (mx + nx * bulge * L, my + ny * bulge * L)
    c2 = (mx - nx * bulge * L, my - ny * bulge * L)
    return chain(quad(p0, c1, p1, n), quad(p1, c2, p0, n))


def star(cx, cy, r, n=5, inner=0.45, rot=0.0):
    return [(cx + r * (1 if k % 2 == 0 else inner) * math.cos(math.pi / 2 + rot + k * math.pi / n),
             cy + r * (1 if k % 2 == 0 else inner) * math.sin(math.pi / 2 + rot + k * math.pi / n)) for k in range(2 * n + 1)]


def tube(center, widths, cap=True):
    """Outline of a band of varying width along a centre line.

    `widths` is a number or a function of t in [0, 1]."""
    wf = widths if callable(widths) else (lambda t: widths)
    n = len(center)
    left, right = [], []
    for i, (x, y) in enumerate(center):
        a = center[max(0, i - 1)]
        b = center[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        w = wf(i / (n - 1)) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    out = left + right[::-1]
    if cap:
        out.append(left[0])
    return out


def wave(x0, x1, y, amp, waves, n=120):
    return [(x0 + (x1 - x0) * i / n, y + amp * math.sin(TAU * waves * i / n)) for i in range(n + 1)]


def zigzag(x0, x1, y, amp, teeth):
    return [(x0 + (x1 - x0) * i / (2 * teeth), y + (amp if i % 2 else -amp)) for i in range(2 * teeth + 1)]


def spiral(cx, cy, r0, r1, turns, n=200, rot=0.0):
    return [(cx + (r0 + (r1 - r0) * i / n) * math.cos(rot + TAU * turns * i / n),
             cy + (r0 + (r1 - r0) * i / n) * math.sin(rot + TAU * turns * i / n)) for i in range(n + 1)]


def eye(cx, cy, r=0.12):
    """Solid pupil printed as a hint."""
    return circle(cx, cy, r, 14)


def heart(cx, cy, s, n=120):
    return [(cx + s * math.sin(t) ** 3, cy + s * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16)
            for t in [TAU * i / n for i in range(n + 1)]]


def mirror_all(strokes, axis=0.0):
    return [mirror_x(s, axis) for s in strokes]


def leg(x0, x1, top, bottom):
    """Open leg shape (no line across the top, so it joins the body)."""
    r = (x1 - x0) / 2
    return chain([(x0, top), (x0, bottom + r)], arc(x0 + r, bottom + r, r, math.pi, 2 * math.pi, 10), [(x1, top)])
