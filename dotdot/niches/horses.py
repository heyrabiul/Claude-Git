"""Horses niche."""
from ._kit import *  # noqa: F401,F403  (shared drawing kit)
import math

import numpy as np

T = "horses"


def make(title, parts, hints=()):
    return Design(title, list(parts), list(hints), T)


# ------------------------------------------------------------ drawing helpers

def spl(pts, closed=True, res=14, tension=0.5):
    """Smooth Catmull-Rom curve through `pts`; a point given as (x, y, 0)
    is a sharp corner."""
    P = [(p[0], p[1]) for p in pts]
    sharp = [len(p) > 2 and p[2] == 0 for p in pts]
    m = len(P)

    def tan(i):
        if sharp[i]:
            return (0.0, 0.0)
        if closed:
            a, b = P[(i - 1) % m], P[(i + 1) % m]
        else:
            a, b = P[max(i - 1, 0)], P[min(i + 1, m - 1)]
        return ((b[0] - a[0]) * tension, (b[1] - a[1]) * tension)

    out = [P[0]]
    for i in range(m if closed else m - 1):
        p0, p1 = P[i], P[(i + 1) % m]
        t0, t1 = tan(i), tan((i + 1) % m)
        n = max(3, int(math.dist(p0, p1) * res))
        for k in range(1, n + 1):
            t = k / n
            h00, h10, h01, h11 = 2 * t**3 - 3 * t**2 + 1, t**3 - 2 * t**2 + t, -2 * t**3 + 3 * t**2, t**3 - t**2
            out.append((h00 * p0[0] + h10 * t0[0] + h01 * p1[0] + h11 * t1[0],
                        h00 * p0[1] + h10 * t0[1] + h01 * p1[1] + h11 * t1[1]))
    return out


def sides(center, w):
    """The two edges of a band along `center` (no end caps), as two strokes."""
    band = tube(center, w, cap=False)
    n = len(center)
    return [band[:n], band[n:][::-1]]


def _dense(pts, step=0.012):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        k = max(1, int(math.dist(a, b) / step))
        for j in range(1, k + 1):
            out.append((a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k))
    return out


def _inside(pts, poly):
    P = np.asarray(pts, float)
    Q = np.asarray(poly, float)
    x, y = P[:, 0:1], P[:, 1:2]
    x0, y0 = Q[:-1, 0][None, :], Q[:-1, 1][None, :]
    x1, y1 = Q[1:, 0][None, :], Q[1:, 1][None, :]
    cond = (y0 > y) != (y1 > y)
    with np.errstate(divide="ignore", invalid="ignore"):
        xc = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
    return (np.sum(cond & (x < xc), axis=1) % 2) == 1


def _bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def _clip(strokes, polys, keep_inside):
    out = []
    polys = [p if math.dist(p[0], p[-1]) < 1e-9 else list(p) + [p[0]] for p in polys if len(p) > 2]
    for s in strokes:
        if len(s) < 2:
            continue
        sb = _bbox(s)
        hit = [p for p in polys if not (_bbox(p)[2] < sb[0] or _bbox(p)[0] > sb[2] or _bbox(p)[3] < sb[1] or _bbox(p)[1] > sb[3])]
        if not hit:
            if not keep_inside:
                out.append(s)
            continue
        d = _dense(s)
        mask = np.zeros(len(d), bool)
        for p in hit:
            mask |= _inside(d, p)
        if keep_inside:
            mask = ~mask
        run = []
        for p, m in zip(d, mask):
            if not m:
                run.append(p)
            else:
                if len(run) > 1:
                    out.append(run)
                run = []
        if len(run) > 1:
            out.append(run)
    return [r for r in out if path_len(r) > 0.03]


def path_len(s):
    return sum(math.dist(a, b) for a, b in zip(s, s[1:]))


def hide(strokes, polys):
    """Remove the parts of `strokes` lying inside any of `polys`."""
    return _clip(strokes, polys, False)


def within(strokes, polys):
    """Keep only the parts of `strokes` inside `polys`."""
    return _clip(strokes, polys, True)


def tf(pts, dx=0.0, dy=0.0, s=1.0, rot=0.0, flip=False):
    if flip:
        pts = [(-x, y) for x, y in pts]
    return transform(pts, dx, dy, s, rot)


def ground(x0, x1, y=0.0):
    return [(x0, y), (x1, y)]


def tufts(pts, s=1.0):
    out = []
    for x, y in pts:
        out += [quad((x, y), (x + dx * 0.4 * s, y + h * 0.6 * s), (x + dx * s, y + h * s), 8)
                for dx, h in [(-0.22, 0.32), (0.0, 0.42), (0.22, 0.32)]]
    return out


def dirv(a):
    a = math.radians(a)
    return (math.sin(a), -math.cos(a))


def nrmv(a):
    a = math.radians(a)
    return (math.cos(a), math.sin(a))


def add(p, v, k=1.0):
    return (p[0] + v[0] * k, p[1] + v[1] * k)


# ------------------------------------------------------------ the horse model

FRONT = [0.18, 0.18, 0.15, 0.15, 0.13]
FRONT_W = [(0.12, 0.12), (0.09, 0.075), (0.068, 0.065), (0.047, 0.052), (0.057, 0.078), (0.046, 0.046)]
HIND = [0.2, 0.2, 0.19, 0.19, 0.13]
HIND_W = [(0.2, 0.26), (0.12, 0.17), (0.075, 0.11), (0.047, 0.058), (0.057, 0.078), (0.046, 0.046)]

STAND = {"fn": (0, 0, 35, 0), "ff": (-10, -6, 30, 0), "hn": (-25, 3, 35, 0), "hf": (-14, 10, 40, 0)}


def leg_outline(top, angles, hind=False, scale=1.0, wscale=1.0, feather=False):
    """Outline of one leg (back edge down, hoof, front edge up) as spline
    control points, plus the coronet line and the hoof centre."""
    a1, a2, a3, a4 = angles
    lens_ = HIND if hind else FRONT
    ws = HIND_W if hind else FRONT_W
    angs = [a1, a1, a2, a2, a3]
    nodes = [top]
    for L, a in zip(lens_, angs):
        nodes.append(add(nodes[-1], dirv(a), L * scale))
    back, front = [], []
    for i, nd in enumerate(nodes):
        aa = angs[max(0, i - 1)] if i == len(nodes) - 1 else (angs[i] * 0.35 if i == 0 else (angs[i - 1] + angs[i]) / 2)
        n = nrmv(aa)
        wf, wb = ws[i]
        front.append(add(nd, n, wf * wscale * scale))
        back.append(add(nd, n, -wb * wscale * scale))
    if hind:  # stifle instead of the hidden top of the thigh, and the point of hock
        front[0] = add(add(top, dirv(a1), 0.04 * scale), nrmv(a1 * 0.5), 0.19 * wscale * scale)
        hk = nodes[3]
        n = nrmv((angs[1] + angs[2]) / 2)
        d = dirv(angs[1])
        back.insert(3, add(add(hk, d, -0.03 * scale), n, -0.135 * wscale * scale))
    c = nodes[-1]
    d, n = dirv(a4), nrmv(a4)
    s = scale * wscale
    hp = lambda u, v: add(add(c, n, u * s), d, v * s)  # noqa: E731
    hoof = [hp(-0.07, 0.07), (*hp(-0.065, 0.13), 0), (*hp(0.11, 0.13), 0), hp(0.065, 0.02)]
    pts = back + hoof + front[::-1]
    coronet = [hp(-0.07, 0.03), hp(0.07, 0.025)]
    if feather:
        # long hair hiding the hoof top: fringe from fetlock down to the hoof
        f = nodes[-2]
        nb = nrmv(a3)
        pts = back[:-2] + [add(f, nb, -0.11 * s), (*add(hp(-0.2, 0.08), d, 0.0), 0), (*hp(-0.1, 0.13), 0), (*hp(0.12, 0.12), 0), (*hp(0.09, 0.03), 0)] + [add(f, nb, 0.1 * s)] + front[::-1][3:]
        coronet = []
    return pts, coronet, nodes


def head_pts(dish=0.0, ear="up", Lh=0.66, mouth_open=False):
    """Head outline (from throat to poll) in head-local units."""
    th = math.radians({"up": 150, "fwd": 128, "back": 172}[ear] if isinstance(ear, str) else ear)
    e, f = (math.cos(th), math.sin(th)), (math.sin(th), -math.cos(th))
    B = (0.06, 0.07)
    ear_pts = [add(add(B, e, 0.16), f, 0.065), (*add(B, e, 0.32), 0), add(add(B, e, 0.15), f, -0.055)]
    pts = [(0.18, -0.48), (0.26, -0.57), (0.42, -0.54), (0.63, -0.43), (0.83, -0.36), (0.92, -0.38),
           (0.99, -0.33), (1.03, -0.25), (1.04, -0.14), (0.97, -0.04), (0.72, 0.03 - dish), (0.48, 0.08 - dish * 1.2),
           (0.27, 0.11), (0.14, 0.1)] + ear_pts + [(-0.02, 0.03), (0.0, 0.0)]
    if mouth_open:
        jaw = [(0.83, -0.36), (0.92, -0.38), (0.99, -0.33)]
        c, sn = math.cos(-0.32), math.sin(-0.32)
        jaw = [(0.55 + (x - 0.55) * c - (y + 0.4) * sn, -0.4 + (x - 0.55) * sn + (y + 0.4) * c) for x, y in jaw]
        pts = pts[:4] + jaw + [(*(0.97, -0.5), 0), (*(0.8, -0.3), 0), (*(1.03, -0.27), 0)] + pts[8:]
    return [tuple([p[0] * Lh, p[1] * Lh] + list(p[2:])) for p in pts]


def far_ear(ear="up", Lh=0.74):
    th = math.radians(({"up": 150, "fwd": 128, "back": 172}[ear] if isinstance(ear, str) else ear) + 8)
    e, f = (math.cos(th), math.sin(th)), (math.sin(th), -math.cos(th))
    B = (-0.04, 0.03)
    pts = [add(B, f, 0.06), add(add(B, e, 0.16), f, 0.06), (*add(B, e, 0.3), 0), add(add(B, e, 0.14), f, -0.05), add(B, f, -0.05)]
    return [tuple([p[0] * Lh, p[1] * Lh] + list(p[2:])) for p in pts]


def head_details(Lh=0.66, mouth=True):
    s = lambda pts: [(x * Lh, y * Lh) for x, y in pts]  # noqa: E731
    eye_ = s(lens((0.25, -0.07), (0.38, -0.1), 0.32, 10))
    nostril = s(arc(0.9, -0.13, 0.07, math.radians(-40), math.radians(200), 10))
    cheek = s(cubic((0.55, -0.18), (0.62, -0.38), (0.36, -0.46), (0.2, -0.36), 14))
    det = [eye_, nostril, cheek]
    if mouth:
        det.append(s([(1.02, -0.26), (0.9, -0.28)]))
    return det, s([(0.32, -0.085)])[0]


def horse(legs=None, neck=(55, 0.76), head=-62, ear="up", tail="hang", mane="hang", pitch=0.0, pivot=(-0.8, 0.0),
          stocky=1.0, legscale=1.0, wscale=1.0, feather=False, dish=0.0, Lh=0.74, mane_len=1.0, forelock=True,
          tail_pts=None, markings=(), mouth=True, neck_w=1.0, mouth_open=False):
    """A side-view horse facing right, standing on y = 0.  Returns a dict of
    strokes, hints and silhouette polygons (for hiding things behind it)."""
    L = dict(STAND)
    L.update(legs or {})
    rot = math.radians(pitch)

    def R(p):  # body frame -> world (pitch about pivot)
        x, y = p[0] - pivot[0], p[1] - pivot[1]
        q = (pivot[0] + x * math.cos(rot) - y * math.sin(rot), pivot[1] + x * math.sin(rot) + y * math.cos(rot))
        return (q[0], q[1], 0) if len(p) > 2 else q

    dy = 0.0
    deep = stocky
    W = (0.42, 1.62)
    back = [(0.2, 1.55), (-0.1, 1.52), (-0.38, 1.55), (-0.6, 1.6), (-0.78, 1.56), (-0.9, 1.45), (-0.95, 1.28), (-0.95, 1.13)]
    belly = [(-0.28, 1.62 - 0.64 * deep), (0.0, 1.62 - 0.72 * deep), (0.28, 1.62 - 0.72 * deep), (0.38, 1.62 - 0.7 * deep)]
    chest = [(0.8, 1.06), (0.9, 1.22)]
    Tf, Th = (0.55, 0.93), (-0.66, 1.0)
    S = chest[-1]
    # neck & head
    na = math.radians(neck[0] + 0.0)
    P = (W[0] + neck[1] * math.cos(na), W[1] + neck[1] * math.sin(na))
    hp_ = head_pts(dish, ear, Lh, mouth_open)
    ha = math.radians(head)

    def H(p):
        return (P[0] + p[0] * math.cos(ha) - p[1] * math.sin(ha), P[1] + p[0] * math.sin(ha) + p[1] * math.cos(ha))
    head_world = [(*H(p), 0) if len(p) > 2 else H(p) for p in hp_]
    Q = head_world[0]
    u = ((P[0] - W[0]) / neck[1], (P[1] - W[1]) / neck[1])
    perp = (-u[1], u[0])
    Ln = neck[1]
    crest = cubic(W, add(add(W, u, 0.35 * Ln), perp, 0.12 * Ln * neck_w), add(add(P, u, -0.3 * Ln), perp, 0.2 * Ln * neck_w), P, 8)
    under = cubic(S, add(S, u, 0.3 * Ln), add(Q, u, -0.3 * Ln), Q, 6)
    # body outline (body frame first, then pitched)
    body_pts = [R(p) for p in crest[::-1][1:-1]] + [R(W)] + [R(p) for p in back]
    hn, hcor, hnodes = leg_outline(R(Th), L["hn"], True, legscale, wscale, feather)
    fn, fcor, fnodes = leg_outline(R(Tf), L["fn"], False, legscale, wscale, feather)
    outline = body_pts + hn + [R(p) for p in belly] + fn + [R(p) for p in chest] + [R(p) for p in under[1:-1]] + [R(p) for p in head_world]
    body = spl(outline, closed=True, res=22)
    # far legs (slightly offset), hidden behind the body
    hf, hfcor, _ = leg_outline(R((Th[0] + 0.16, Th[1])), L["hf"], True, legscale, wscale, feather)
    ff, ffcor, _ = leg_outline(R((Tf[0] - 0.14, Tf[1])), L["ff"], False, legscale, wscale, feather)
    far = [spl(hf, closed=False, res=22), spl(ff, closed=False, res=22)]
    far_cor = [c for c in (hfcor, ffcor) if c]
    # head details
    det, eyep = head_details(Lh, mouth and not mouth_open)
    details = [[R(H(p)) for p in d] for d in det]
    hints = [eye(*R(H(eyep)), 0.028 * Lh / 0.66 * 1.6)]
    near_cor = [c for c in (hcor, fcor) if c]
    # mane
    mane_strokes, mane_poly = [], []
    crest_w = [R(p) for p in crest]  # W -> P
    up = (perp[0], perp[1])
    up = (up[0] * math.cos(rot) - up[1] * math.sin(rot), up[0] * math.sin(rot) + up[1] * math.cos(rot))
    uu = (u[0] * math.cos(rot) - u[1] * math.sin(rot), u[0] * math.sin(rot) + u[1] * math.cos(rot))
    full_crest = cubic(*[R(p) for p in (W, add(add(W, u, 0.35 * Ln), perp, 0.12 * Ln * neck_w), add(add(P, u, -0.3 * Ln), perp, 0.2 * Ln * neck_w), P)], 40)
    if mane in ("hang", "long", "flow", "roach", "braid"):
        n = {"hang": 6, "long": 6, "flow": 6, "roach": 12, "braid": 7}[mane]
        N = len(full_crest) - 1
        cp = lambda t: full_crest[int(round(t * N))]  # noqa: E731
        if mane == "braid":
            for k in range(n):
                m = cp(0.08 + 0.84 * (k + 0.5) / n)
                c = add(m, up, -0.075)
                mane_strokes.append(ellipse(c[0], c[1], 0.07, 0.05, 14, rot=math.atan2(up[1], up[0])))
        else:
            span = 0.8 if mane in ("hang", "long") else 0.93
            pts = [cp(0.02)]
            for k in range(n):
                tt = 0.02 + span * (k + 0.6) / n
                tv = 0.02 + span * (k + 1) / n
                m = cp(tt)
                if mane == "hang":
                    d = 0.21 * mane_len
                    tip, val = add(add(add(m, up, -0.55 * d), (0, -1), 0.5 * d), uu, -0.05), add(cp(tv), up, -0.35 * d)
                elif mane == "long":
                    d = (0.34 + 0.06 * math.sin(k * 2.1)) * mane_len
                    tip, val = add(add(m, up, -d), uu, -0.12), add(cp(tv), up, -0.5 * d)
                elif mane == "flow":
                    tip, val = add(add(m, up, 0.13 * mane_len), uu, -0.32 * mane_len), add(cp(tv), up, 0.04)
                else:
                    tip, val = add(m, up, 0.12), add(cp(tv), up, 0.05)
                if mane in ("flow", "long", "hang"):
                    prev = pts[-1][:2]
                    pts.append(add(add(((prev[0] + tip[0]) / 2, (prev[1] + tip[1]) / 2), up, 0.04 if mane == "flow" else 0.0), uu, 0.0 if mane == "flow" else 0.035))
                pts.append((*tip, 0))
                if k < n - 1:
                    pts.append(val)
            pts.append(cp(0.02 + span) if mane in ("hang", "long") else cp(0.97))
            line = spl(pts, closed=False, res=30)
            mane_strokes.append(line)
            if mane in ("flow", "roach"):
                mane_poly = [line + full_crest[int(0.02 * N):int(0.97 * N) + 1][::-1]]
            if mane in ("long", "hang"):
                for k in range(1, n):
                    tt = 0.02 + span * (k + 0.1) / n
                    b = cp(tt)
                    d = (0.25 if mane == "long" else 0.11) * mane_len
                    mane_strokes.append(quad(add(b, up, -0.06), add(add(b, up, -0.5 * d), uu, 0.02), add(add(b, up, -d), uu, -0.05), 8))
    head_poly = spl([R(p) for p in head_world], closed=True)
    mane_strokes = hide(mane_strokes, [head_poly])
    if ear is not None:
        fe = spl([(*R(H(p)), 0) if len(p) > 2 else R(H(p)) for p in far_ear(ear, Lh)], closed=False, res=40)
        details += hide([fe], [head_poly])
    if forelock and mane != "roach":
        fl = [H((0.06 * Lh, 0.08 * Lh)), H((0.2 * Lh, 0.04 * Lh)), (*H((0.3 * Lh, -0.02 * Lh)), 0), H((0.24 * Lh, 0.07 * Lh)), H((0.16 * Lh, 0.12 * Lh))]
        details.append([R(p) for p in spl(fl, closed=False, res=40)])
    # tail
    root = R((-0.92, 1.5))
    if tail_pts is None:
        tail_pts = {"hang": [(-0.84, 1.52), (-1.12, 1.48), (-1.18, 0.95), (-1.1, 0.5)],
                    "flow": [(-0.84, 1.52), (-1.2, 1.62), (-1.5, 1.5), (-1.9, 1.35)],
                    "high": [(-0.82, 1.52), (-1.05, 1.85), (-1.35, 1.68), (-1.42, 1.1)],
                    "swish": [(-0.84, 1.52), (-1.1, 1.4), (-0.95, 0.9), (-1.2, 0.5)]}[tail]
        tail_pts = [R(p) for p in tail_pts]
    cl = cubic(*tail_pts, 30)
    wf = lambda t: 0.1 + 0.3 * math.sin(math.pi * (0.12 + 0.76 * t)) ** 0.8  # noqa: E731
    band = tube(cl, wf, cap=False)
    m = len(cl)
    left, right = band[:m], band[m:][::-1]
    d_end = (cl[-1][0] - cl[-4][0], cl[-1][1] - cl[-4][1])
    dl = math.hypot(*d_end) or 1
    d_end = (d_end[0] / dl, d_end[1] / dl)
    tipn = (-d_end[1], d_end[0])
    tips = [(*add(add(cl[-1], tipn, 0.09), d_end, 0.08), 0), add(add(cl[-1], tipn, 0.04), d_end, -0.02), (*add(add(cl[-1], tipn, 0.0), d_end, 0.14), 0),
            add(add(cl[-1], tipn, -0.05), d_end, -0.01), (*add(add(cl[-1], tipn, -0.08), d_end, 0.07), 0)]
    tail_out = spl([(*left[0], 0)] + left[3::4] + tips + right[3::4][::-1] + [(*right[0], 0)], closed=False, res=30)
    tail_out = [left[0]] + tail_out[1:]
    tail_poly = tail_out + [tail_out[0]]
    strands = [cubic(*[add(p, tipn, off) for p in tail_pts], 20)[6:-4] for off in (-0.05, 0.06)]
    # assemble with occlusion: tail & mane over body; body over far legs
    tail_strokes = [tail_out] + strands
    body_poly = body
    near = hide([body], [tail_poly] + mane_poly)
    near += hide(details + [c for c in near_cor], [tail_poly])
    far_s = hide(far + far_cor, [body_poly, tail_poly])
    mk = []
    for mtype, data in markings:
        if mtype == "spots":
            mk += within([circle(x, y, r, 14) for x, y, r in data], [body_poly])
        elif mtype == "patch":
            mk += within(hide([spl(p) for p in data], [tail_poly]), [body_poly])
        elif mtype == "blaze":
            a, b = data
            mk += [[R(H((a * Lh, 0.0))), R(H(((a + b) / 2 * Lh, 0.05 * Lh))), R(H((b * Lh, -0.02 * Lh)))]]
            mk = mk[:-1] + [spl([R(H((a * Lh, 0.04 * Lh))), R(H(((a + b) / 2 * Lh, -0.03 * Lh))), (*R(H((b * Lh, -0.07 * Lh))), 0), R(H(((a + b) / 2 * Lh, -0.12 * Lh))), R(H(((a + 0.05) * Lh, -0.02 * Lh)))], closed=False)]
        elif mtype == "sock":
            for key in data:
                nodes = hnodes if key == "hn" else fnodes
                f = nodes[-2]
                ang = L[key][1]
                n = nrmv(ang)
                mk.append([add(add(f, n, -0.1), dirv(ang), -0.1), add(add(f, n, 0.0), dirv(ang), -0.13), add(add(f, n, 0.1), dirv(ang), -0.1)])
    strokes = near + far_s + mane_strokes + tail_strokes + mk
    gy = min(p[1] for s_ in near + far_s for p in s_)
    return {"strokes": strokes, "hints": hints, "sil": [body_poly, tail_poly] + mane_poly, "gy": gy,
            "nodes": {"hn": hnodes, "fn": fnodes}, "P": R(P), "W": R(W), "H": lambda p: R(H(p)),
            "R": R, "mouth": R(H((0.97 * Lh, -0.27 * Lh))), "head_poly": head_poly}


def place(h, dx=0.0, dy=0.0, s=1.0, rot=0.0, flip=False):
    g = lambda pts: tf(pts, dx, dy, s, rot, flip)  # noqa: E731
    out = {"strokes": [g(p) for p in h["strokes"]], "hints": [g(p) for p in h["hints"]], "sil": [g(p) for p in h["sil"]]}
    out["gy"] = min(p[1] for s_ in out["strokes"] for p in s_)
    return out


def scene(*items):
    """Front-to-back list of placed things (dicts with strokes/sil, or plain
    stroke lists); each is hidden behind everything listed before it."""
    out, hints, sil = [], [], []
    for it in items:
        if isinstance(it, dict):
            out += hide(it["strokes"], sil)
            hints += it.get("hints", [])
            sil = sil + it.get("sil", [])
        else:
            out += hide(it, sil)
    return out, hints


def closed(pts):
    return list(pts) + [pts[0]]


def obj(strokes, sil=None, hints=()):
    """A scene item whose silhouette is `sil` (default: its closed strokes)."""
    if sil is None:
        sil = [s for s in strokes if len(s) > 3 and math.dist(s[0], s[-1]) < 1e-6]
    return {"strokes": strokes, "sil": sil, "hints": list(hints)}


# ------------------------------------------------------------ props

def rail_fence(x0, x1, y0=0.0, h=1.1, posts=3, rails=2):
    out, sil = [], []
    xs = [x0 + (x1 - x0) * k / (posts - 1) for k in range(posts)]
    for x in xs:
        p = rect(x - 0.07, y0, x + 0.07, y0 + h)
        out.append(p)
        sil.append(p)
    rr = []
    for k in range(rails):
        y = y0 + h * (0.45 + 0.4 * k / max(1, rails - 1)) if rails > 1 else y0 + h * 0.7
        rr.append(rect(x0 - 0.15, y - 0.06, x1 + 0.15, y + 0.06))
    return {"strokes": out + hide(rr, sil), "sil": sil + rr}


def sun(cx, cy, r, rays=10, ray_len=0.35):
    out = [circle(cx, cy, r, 60)]
    for k in range(rays):
        a = TAU * k / rays
        out.append([(cx + (r + 0.12) * math.cos(a), cy + (r + 0.12) * math.sin(a)),
                    (cx + (r + 0.12 + ray_len) * math.cos(a), cy + (r + 0.12 + ray_len) * math.sin(a))])
    return out


def tree(x, y, s=1.0):
    trunk = [[(x - 0.18 * s, y), (x - 0.12 * s, y + 1.3 * s)], [(x + 0.18 * s, y), (x + 0.12 * s, y + 1.3 * s)]]
    crown = polar(lambda t: 1.0 + 0.12 * math.sin(7 * t), cx=x, cy=y + 2.0 * s, n=160)
    crown = [(x + (px - x) * s, y + 2.0 * s + (py - y - 2.0 * s) * s) for px, py in crown]
    return {"strokes": [crown] + hide(trunk, [crown]), "sil": [crown, rect(x - 0.18 * s, y, x + 0.18 * s, y + 1.3 * s)]}


def rider(seat, lean=70, hand=None, style="helmet", knee=(0.32, -0.28), foot=(0.18, -0.62), coat=False):
    """A seated rider facing right.  `seat` is the hip point, `lean` the
    torso angle from horizontal, `hand` where the hands hold the reins."""
    hx, hy = seat
    a = math.radians(lean)
    sh = (hx + 0.55 * math.cos(a), hy + 0.55 * math.sin(a))
    torso_c = [seat, ((hx + sh[0]) / 2, (hy + sh[1]) / 2), sh]
    torso = tube(torso_c, lambda t: 0.27 - 0.05 * t)
    hc = (sh[0] + 0.2 * math.cos(a - 0.15), sh[1] + 0.2 * math.sin(a - 0.15))
    head = circle(hc[0], hc[1], 0.12, 30)
    parts = []
    if style == "helmet":
        cap = chain(arc(hc[0], hc[1] + 0.01, 0.135, math.radians(-10), math.radians(190), 16))
        peak = [(hc[0] + 0.13, hc[1] + 0.0), (hc[0] + 0.25, hc[1] - 0.03)]
        parts += [cap, peak]
    elif style == "tophat":
        parts += [rect(hc[0] - 0.1, hc[1] + 0.08, hc[0] + 0.1, hc[1] + 0.3), [(hc[0] - 0.17, hc[1] + 0.08), (hc[0] + 0.17, hc[1] + 0.08)]]
    hand = hand or (sh[0] + 0.45, sh[1] - 0.25)
    elbow = (sh[0] + (hand[0] - sh[0]) * 0.45 - 0.05, sh[1] + (hand[1] - sh[1]) * 0.6 - 0.12)
    arm = tube(spl([sh, elbow, hand], closed=False, res=30), lambda t: 0.12 - 0.03 * t)
    kn = (hx + knee[0], hy + knee[1])
    an = (hx + foot[0], hy + foot[1])
    leg_ = tube(spl([seat, kn, an], closed=False, res=30), lambda t: 0.19 - 0.08 * t)
    boot = spl([(an[0] - 0.07, an[1] + 0.12), (an[0] - 0.07, an[1] - 0.02), (*(an[0] + 0.0, an[1] - 0.06), 0), (*(an[0] + 0.2, an[1] - 0.06), 0), (an[0] + 0.07, an[1] + 0.06)], closed=False, res=40)
    stirrup = poly((an[0] - 0.05, an[1] - 0.06), (an[0] - 0.02, an[1] - 0.14), (an[0] + 0.17, an[1] - 0.14), (an[0] + 0.15, an[1] - 0.06), closed=False)
    fist = circle(hand[0], hand[1], 0.055, 12)
    out, sil = [], []
    for item in [[head] + parts, [arm, fist], [leg_, boot], [torso]]:
        out += hide(item, sil)
        sil += [s for s in item if len(s) > 3 and math.dist(s[0], s[-1]) < 1e-6]
    if coat:
        tail_ = spl([(seat[0] - 0.12, seat[1] + 0.12), (seat[0] - 0.3, seat[1] - 0.08), (*(seat[0] - 0.3, seat[1] - 0.25), 0), (seat[0] + 0.05, seat[1] - 0.15)], closed=False)
        out += hide([tail_], sil)
    out.append(stirrup)
    return {"strokes": out, "sil": sil, "hand": hand}


def english_saddle(h, rider_on=False):
    R = h["R"]
    seat = spl([R((0.42, 1.68)), R((0.3, 1.6)), R((0.0, 1.56)), R((-0.18, 1.62)), (*R((-0.24, 1.7)), 0)], closed=False)
    flap = spl([R((0.36, 1.58)), R((0.4, 1.3)), (*R((0.32, 1.14)), 0), (*R((0.04, 1.14)), 0), R((-0.02, 1.35)), R((0.02, 1.56))], closed=False)
    pad = spl([R((0.5, 1.62)), R((0.5, 1.15)), (*R((0.45, 1.05)), 0), (*R((-0.22, 1.05)), 0), R((-0.3, 1.3)), R((-0.28, 1.6))], closed=False)
    girth = [[R((0.22, 1.14)), R((0.3, 0.92))], [R((0.32, 1.14)), R((0.4, 0.93))]]
    out = [seat, pad] if rider_on else [seat, flap, pad] + girth
    sil = [spl([R((0.5, 1.62)), R((0.5, 1.15)), (*R((0.45, 1.05)), 0), (*R((-0.22, 1.05)), 0), R((-0.3, 1.3)), R((-0.28, 1.6)), R((-0.24, 1.7)), R((0.42, 1.68))])]
    if not rider_on:
        st = [[R((0.18, 1.15)), R((0.18, 0.86))], poly(R((0.1, 0.86)), R((0.26, 0.86)), R((0.24, 0.76)), R((0.12, 0.76)), closed=True)]
        out = hide(out, [flap + [flap[0]]])[:0] + out + st
        sil.append(flap + [flap[0]])
    return out, sil


def bridle(h, reins_to=None, Lh=0.74):
    H = h["H"]
    s = lambda pts: [H((x * Lh, y * Lh)) for x, y in pts]  # noqa: E731
    out = [s([(0.06, 0.1), (0.1, -0.1), (0.18, -0.45)]),  # crown piece / throatlatch side
           s([(0.62, 0.05), (0.66, -0.43)]), s([(0.62, -0.05), (0.66, -0.05)])[:0] + s([(0.14, 0.08), (0.18, -0.02)]),
           s([(0.1, -0.1), (0.85, -0.25)])]
    ring = H((0.88 * Lh, -0.28 * Lh))
    out = [s([(0.08, 0.08), (0.14, -0.1), (0.2, -0.5)]), s([(0.6, 0.07), (0.62, -0.42)]), s([(0.12, -0.08), (0.84, -0.25)]),
           s([(0.07, 0.04), (0.2, 0.12)])[:0] + s([(0.16, 0.11), (0.2, -0.05)])]
    out.append(circle(ring[0], ring[1], 0.04 * Lh / 0.74 * 1.4, 12))
    if reins_to:
        out.append(quad(ring, ((ring[0] + reins_to[0]) / 2, min(ring[1], reins_to[1]) - 0.25), reins_to, 16))
    return out


def jump_fence(x0, x1, y0=0.0, h=1.2, poles=3):
    stands = [rect(x0 - 0.08, y0, x0 + 0.08, y0 + h + 0.15), rect(x1 - 0.08, y0, x1 + 0.08, y0 + h + 0.15)]
    feet = [[(x0 - 0.3, y0), (x0 + 0.3, y0)], [(x1 - 0.3, y0), (x1 + 0.3, y0)]]
    ps = []
    for k in range(poles):
        y = y0 + h * (k + 1) / poles - 0.05
        ps.append(rect(x0 - 0.2, y - 0.06, x1 + 0.2, y + 0.06))
        ps += [[(x0 - 0.2 + (x1 - x0 + 0.4) * j / 6, y - 0.06), (x0 - 0.2 + (x1 - x0 + 0.4) * j / 6, y + 0.06)] for j in range(1, 6)][:0]
    stripes = []
    for k in range(poles):
        y = y0 + h * (k + 1) / poles - 0.05
        for j in range(1, 5):
            x = x0 - 0.2 + (x1 - x0 + 0.4) * j / 5
            stripes.append([(x, y - 0.06), (x, y + 0.06)])
    return {"strokes": ps + hide(stands + feet + stripes[:0], ps) + stripes, "sil": ps + stands}


GALLOP = {"fn": (45, 50, 60, 50), "ff": (75, -5, -30, -50), "hn": (-40, -35, -50, -70), "hf": (30, -15, 10, -10)}
GALLOP2 = {"fn": (60, 75, 85, 90), "ff": (85, 10, -30, -60), "hn": (-35, -45, -60, -80), "hf": (40, -10, 20, 0)}
GALLOP3 = {"fn": (25, -60, -60, -80), "ff": (55, 45, 60, 50), "hn": (10, 30, 50, 40), "hf": (-45, -40, -55, -80)}
TROT = {"fn": (40, -20, -10, -20), "ff": (-12, -14, 22, 0), "hn": (-32, -6, 30, 0), "hf": (18, -28, -5, -15)}
WALK = {"fn": (22, -18, 5, -5), "ff": (-6, -4, 32, 0), "hn": (-18, 8, 38, 0), "hf": (-34, -12, 20, -5)}


# ------------------------------------------------------------ designs: whole horses

@design("horses_standing_bay", T)
def standing_bay(rng):
    h = horse(markings=[("blaze", (0.3, 0.95)), ("sock", ["hn"])])
    fence = rail_fence(-2.0, 2.0, 0.0, 1.0, 3, 2)
    st, hi = scene(h, fence)
    return make("Bay Horse in the Paddock", st + [ground(-3.0, 3.0)] + tufts([(-2.2, 0), (2.3, 0)]), hi)


@design("horses_galloping", T)
def galloping(rng):
    h = horse(legs=GALLOP, neck=(35, 0.78), head=-48, ear="fwd", mane="flow", tail="flow", pitch=6)
    gy = h["gy"]
    dust = [arc(-1.8 + 0.35 * k, gy + 0.1, 0.18 + 0.05 * k, 0.2, math.pi - 0.2, 12) for k in range(3)]
    return make("Galloping Horse", h["strokes"] + [ground(-2.4, 2.2, gy - 0.05)] + dust, h["hints"])


@design("horses_rearing", T)
def rearing(rng):
    legs = {"fn": (112, 15, -5, -20), "ff": (80, 40, 50, 40), "hn": (28, -22, 20, 0), "hf": (40, -10, 30, 0)}
    tail = [(-0.84, 1.52), (-1.0, 1.2), (-1.25, 0.9), (-1.55, 0.45)]
    h = horse(legs=legs, neck=(40, 0.8), head=-95, ear="back", mane="flow", pitch=42, pivot=(-0.8, 0.2), tail_pts=None, tail="swish")
    gy = h["gy"]
    return make("Rearing Horse", h["strokes"] + [ground(-2.6, 1.4, gy)] + tufts([(-2.2, gy), (1.0, gy)]), h["hints"])


@design("horses_trotting", T)
def trotting(rng):
    h = horse(legs=TROT, neck=(50, 0.78), head=-58, ear="fwd", mane="hang", tail="swish", markings=[("sock", ["fn"])])
    gy = h["gy"]
    return make("Trotting Horse", h["strokes"] + [ground(-2.0, 2.2, gy)] + tufts([(1.7, gy), (-1.7, gy)]), h["hints"])


@design("horses_grazing", T)
def grazing(rng):
    legs = {"fn": (-8, -6, 30, 0), "ff": (10, 8, 42, 0)}
    h = horse(legs=legs, neck=(-48, 1.05), head=-104, ear=110, mane="hang")
    gy = h["gy"]
    return make("Grazing Horse", h["strokes"] + [ground(-2.0, 2.2, gy)] + tufts([(1.05, gy), (1.45, gy), (-1.8, gy), (0.2, gy)], 0.9), h["hints"])


@design("horses_mare_foal", T)
def mare_foal(rng):
    mare = horse(neck=(-12, 0.86), head=-80, ear="fwd", mane="hang", markings=[("blaze", (0.3, 0.95))])
    foal = horse(legs={"fn": (-4, -2, 30, 0), "ff": (6, 4, 36, 0), "hn": (-22, 4, 34, 0), "hf": (-10, 10, 38, 0)},
                 neck=(52, 0.62), head=-12, ear="up", mane="roach", Lh=0.66, legscale=1.32, wscale=0.85,
                 tail_pts=[(-0.84, 1.52), (-1.0, 1.5), (-1.08, 1.3), (-1.05, 1.1)], forelock=False)
    f = place(foal, 2.0, 0.0, 0.6, flip=True)
    f["strokes"] = [[(x, y - f["gy"]) for x, y in s_] for s_ in f["strokes"]]
    f["hints"] = [[(x, y - f["gy"]) for x, y in s_] for s_ in f["hints"]]
    f["sil"] = [[(x, y - f["gy"]) for x, y in s_] for s_ in f["sil"]]
    st, hi = scene(f, mare)
    return make("Mare and Foal Nuzzling", st + [ground(-1.8, 3.4)] + tufts([(-1.5, 0), (3.1, 0)]), hi)


@design("horses_arabian", T)
def arabian(rng):
    legs = {"fn": (62, -8, 10, -10), "ff": (-8, -6, 30, 0), "hn": (-28, 2, 34, 0), "hf": (-6, 14, 40, 0)}
    h = horse(legs=legs, neck=(62, 0.78), head=-58, ear="fwd", mane="long", mane_len=0.8, tail="high", dish=0.07,
              Lh=0.64, neck_w=1.5, wscale=0.9)
    gy = h["gy"]
    return make("Arabian Horse", h["strokes"] + [ground(-2.0, 2.0, gy)], h["hints"])


@design("horses_clydesdale", T)
def clydesdale(rng):
    legs = {"fn": (24, -16, 6, -5), "ff": (-6, -4, 30, 0), "hn": (-20, 8, 36, 0), "hf": (-32, -10, 22, -5)}
    h = horse(legs=legs, neck=(50, 0.78), head=-64, ear="up", mane="hang", mane_len=1.1, tail="hang", stocky=1.12,
              wscale=1.35, feather=True, Lh=0.82, neck_w=1.3, markings=[("blaze", (0.25, 1.0))])
    gy = h["gy"]
    return make("Clydesdale with Feathered Hooves", mirror_all(h["strokes"] + [ground(-2.0, 2.2, gy)] + tufts([(1.9, gy), (-1.7, gy)])), mirror_all(h["hints"]))


# dropped: the subject repeats another book
def shetland(rng):
    tail = [(-0.84, 1.52), (-1.12, 1.45), (-1.18, 0.95), (-1.12, 0.32)]
    h = horse(legs={"fn": (4, 2, 34, 0), "ff": (-6, -4, 30, 0)}, neck=(48, 0.66), head=-66, ear="fwd", mane="long", mane_len=1.25,
              legscale=0.68, wscale=1.3, stocky=1.1, Lh=0.8, tail_pts=tail, neck_w=1.2)
    gy = h["gy"]
    return make("Shetland Pony", mirror_all(h["strokes"] + [ground(-1.8, 1.8, gy)] + tufts([(1.5, gy), (-1.5, gy)], 0.8)), mirror_all(h["hints"]))


@design("horses_friesian", T)
def friesian(rng):
    legs = {"fn": (58, -10, 0, -20), "ff": (-14, -14, 22, 0), "hn": (-34, -6, 30, 0), "hf": (24, -30, -8, -20)}
    tail = [(-0.84, 1.52), (-1.2, 1.4), (-1.15, 0.8), (-1.4, 0.25)]
    h = horse(legs=legs, neck=(58, 0.82), head=-70, ear="fwd", mane="long", mane_len=1.6, tail_pts=tail,
              feather=True, wscale=1.12, neck_w=1.5, Lh=0.76)
    gy = h["gy"]
    return make("Friesian Horse High-Stepping", h["strokes"] + [ground(-2.0, 2.2, gy)], h["hints"])


@design("horses_appaloosa", T)
def appaloosa(rng):
    blanket = spl([(0.05, 1.7), (0.0, 1.35), (-0.15, 1.2), (-0.3, 1.25), (-0.45, 1.05), (-0.62, 0.9), (-0.8, 0.95), (-1.0, 1.0),
                   (-1.3, 1.3), (-0.5, 1.9)], closed=True)
    spots = [(-0.25, 1.42, 0.05), (-0.45, 1.48, 0.06), (-0.62, 1.4, 0.05), (-0.38, 1.28, 0.05), (-0.75, 1.3, 0.06), (-0.55, 1.18, 0.05),
             (-0.86, 1.14, 0.05), (-0.12, 1.5, 0.045), (-0.7, 1.05, 0.045), (-0.85, 1.42, 0.045)]
    h = horse(legs=WALK, neck=(52, 0.76), head=-64, ear="fwd", mane="hang", mane_len=0.8,
              markings=[("patch", [blanket]), ("spots", spots)])
    gy = h["gy"]
    return make("Appaloosa with Spotted Blanket", h["strokes"] + [ground(-2.0, 2.2, gy)] + tufts([(1.9, gy), (-1.7, gy)]), h["hints"])


@design("horses_mustangs", T)
def mustangs(rng):
    a = place(horse(legs=GALLOP, neck=(35, 0.78), head=-48, ear="fwd", mane="flow", tail="flow", pitch=6), 0.0, 0.0, 1.0)
    b = place(horse(legs=GALLOP2, neck=(30, 0.8), head=-40, ear="back", mane="flow", tail="flow", pitch=4), -1.5, 0.75, 0.8)
    c = place(horse(legs=GALLOP3, neck=(38, 0.76), head=-52, ear="up", mane="flow", tail="flow", pitch=3), 1.3, 1.25, 0.66)
    st, hi = scene(a, b, c)
    hills = hide([spl([(-3.6, 1.6), (-2.2, 2.3), (-0.6, 1.8), (1.0, 2.5), (2.6, 2.1), (3.4, 2.4)], closed=False)], a["sil"] + b["sil"] + c["sil"])
    return make("Wild Mustangs Running", st + hills + [ground(-3.4, 2.6, a["gy"] - 0.05)], hi)


def _rider_on(h, lean=70, style="helmet", knee=(0.3, -0.3), foot=(0.16, -0.64), seat=(0.02, 1.6), hand=None, coat=False):
    R = h["R"]
    hand = hand or R((0.62, 1.86))
    r = rider(R(seat), lean, hand, style, knee, foot, coat)
    reins = [quad(r["hand"], ((r["hand"][0] + h["mouth"][0]) / 2, min(r["hand"][1], h["mouth"][1]) - 0.1), h["mouth"], 16)]
    return r, reins


@design("horses_showjump", T)
def showjump(rng):
    legs = {"fn": (118, -40, -60, -80), "ff": (105, -55, -70, -90), "hn": (-62, -80, -95, -110), "hf": (-50, -70, -85, -100)}
    h = horse(legs=legs, neck=(22, 0.8), head=-78, ear="fwd", mane="braid", tail="flow", pitch=16, pivot=(0, 1.0))
    sad, sad_sil = english_saddle(h, rider_on=True)
    r, reins = _rider_on(h, lean=38, knee=(0.36, -0.2), foot=(0.2, -0.5), hand=h["R"]((0.75, 1.92)))
    gy = h["gy"] - 0.9
    fence = jump_fence(-0.9, 0.9, gy, 1.3, 3)
    st, hi = scene(r, obj(reins, []), obj(sad, sad_sil), h, fence)
    return make("Show Jumper Clearing a Fence", st + [ground(-2.6, 2.6, gy)] + tufts([(-2.2, gy), (2.2, gy)]), hi)


@design("horses_dressage", T)
def dressage(rng):
    legs = {"fn": (48, -12, 10, -10), "ff": (-8, -8, 28, 0), "hn": (-30, -4, 30, 0), "hf": (12, -32, -10, -20)}
    h = horse(legs=legs, neck=(64, 0.74), head=-88, ear="fwd", mane="braid", tail="hang", neck_w=1.6)
    sad, sad_sil = english_saddle(h, rider_on=True)
    r, reins = _rider_on(h, lean=86, style="tophat", hand=h["R"]((0.5, 1.82)), coat=True)
    gy = h["gy"]
    st, hi = scene(r, obj(reins, []), obj(sad, sad_sil), h)
    letters = [rect(2.0, gy, 2.4, gy + 0.6), [(2.2, gy + 0.6), (2.2, gy + 0.75)]]
    return make("Dressage Horse and Rider", st + [ground(-2.0, 2.6, gy)] + letters, hi)


@design("horses_racehorse", T)
def racehorse(rng):
    h = horse(legs=GALLOP2, neck=(22, 0.82), head=-42, ear="back", mane="roach", tail="flow", pitch=3, forelock=False)
    sad, sad_sil = english_saddle(h, rider_on=True)
    R = h["R"]
    r, reins = _rider_on(h, lean=18, knee=(0.42, -0.08), foot=(0.18, -0.34), seat=(0.0, 1.72), hand=R((0.78, 1.9)))
    cloth = [rrect(-0.3, 1.18, 0.35, 1.58, 0.06)]
    cloth = [[R(p) for p in cloth[0]]]
    gy = h["gy"]
    rail = rail_fence(-2.8, 2.6, gy + 0.3, 0.8, 4, 1)
    st, hi = scene(r, obj(reins, []), obj(sad + cloth, sad_sil + cloth), h, rail)
    return make("Racehorse and Jockey", st + [ground(-2.8, 2.6, gy)], hi)


@design("horses_sulky", T)
def sulky(rng):
    h = horse(legs=TROT, neck=(46, 0.78), head=-56, ear="fwd", mane="roach", tail="swish", forelock=False)
    gy = h["gy"]
    wc = (-1.75, gy + 0.55)
    wheel = [circle(wc[0], wc[1], 0.55, 60), circle(wc[0], wc[1], 0.08, 12)] + [[(wc[0] + 0.08 * math.cos(a), wc[1] + 0.08 * math.sin(a)), (wc[0] + 0.52 * math.cos(a), wc[1] + 0.52 * math.sin(a))] for a in [k * TAU / 10 for k in range(10)]]
    shaft = [[(wc[0], wc[1] + 0.1), (-0.6, 1.12), (0.55, 1.22)], [(wc[0], wc[1] - 0.0), (-0.6, 1.02), (0.5, 1.12)]]
    seat_ = rrect(-2.15, wc[1] + 0.45, -1.6, wc[1] + 0.6, 0.05)
    drv = rider((-1.9, wc[1] + 0.68), lean=100, hand=(-1.2, wc[1] + 1.0), knee=(0.55, 0.12), foot=(1.05, -0.05))
    reins = [quad(drv["hand"], (-0.2, 1.6), h["mouth"], 20)]
    st, hi = scene(obj(reins, []), h, drv, obj([seat_], [seat_]), obj(wheel, [wheel[0]]), obj(shaft, []))
    return make("Harness Racing Sulky", st + [ground(-2.6, 2.2, gy)], hi)


@design("horses_buggy", T)
def buggy(rng):
    h = horse(legs=WALK, neck=(50, 0.76), head=-62, ear="up", mane="hang", tail="hang")
    gy = h["gy"]
    big = (-2.05, gy + 0.6)
    wheel = [circle(big[0], big[1], 0.6, 60), circle(big[0], big[1], 0.08, 12)] + [[(big[0] + 0.08 * math.cos(a), big[1] + 0.08 * math.sin(a)), (big[0] + 0.57 * math.cos(a), big[1] + 0.57 * math.sin(a))] for a in [k * TAU / 12 for k in range(12)]]
    box = rect(-2.7, gy + 0.9, -1.2, gy + 1.45)
    hood = spl([(-2.75, gy + 1.45), (-2.8, gy + 2.2), (-2.45, gy + 2.6), (-1.6, gy + 2.62), (*(-1.45, gy + 2.5), 0)], closed=False)
    struts = [[(-1.45, gy + 2.5), (-1.3, gy + 1.45)], [(-2.1, gy + 2.6), (-2.1, gy + 1.45)]]
    seat_ = [(-2.6, gy + 1.45), (-2.6, gy + 1.75), (-1.9, gy + 1.75), (-1.9, gy + 1.45)]
    shafts = [[(-1.2, gy + 1.2), (-0.4, gy + 1.15), (0.45, gy + 1.25)], [(-1.2, gy + 1.1), (-0.4, gy + 1.05), (0.4, gy + 1.15)]]
    harness = [[(0.35, 1.55), (0.3, 0.95)]]
    st, hi = scene(obj(harness, []), h, obj(wheel, [wheel[0]]), obj([box, hood, seat_] + struts, [box]), obj(shafts, []))
    return make("Horse and Buggy", st + [ground(-3.0, 2.2, gy)], hi)


@design("horses_plough", T)
def plough(rng):
    h = horse(legs=WALK, neck=(40, 0.78), head=-70, ear="up", mane="hang", tail="hang", stocky=1.12, wscale=1.3,
              feather=True, Lh=0.8, neck_w=1.3)
    gy = h["gy"]
    R = h["R"]
    collar = [spl([R((0.42, 1.78)), R((0.62, 1.82)), R((0.95, 1.35)), R((0.9, 1.1)), R((0.78, 1.15)), R((0.78, 1.45)), R((0.55, 1.68))], closed=True)]
    traces = [[R((0.85, 1.25)), (-1.9, gy + 0.6)], [R((0.1, 1.62)), R((-0.2, 1.62))][:0] + [R((0.4, 1.15)), R((-0.1, 1.1))]]
    beam = [(-1.9, gy + 0.6), (-2.6, gy + 0.2)]
    handles = [[(-2.4, gy + 0.3), (-3.1, gy + 1.2)], [(-2.55, gy + 0.25), (-3.25, gy + 1.05)]]
    share = poly((-2.7, gy + 0.25), (-2.2, gy - 0.05), (-2.75, gy - 0.05))
    furrows = [[(-3.4, gy - 0.05 - 0.22 * k), (-2.8 + 0.3 * k, gy - 0.05 - 0.22 * k)] for k in range(1, 3)] + [[(-2.2, gy - 0.05), (2.2, gy - 0.05)]]
    st, hi = scene(obj(collar), obj(traces, []), h, obj([beam] + handles + [share], [share]))
    return make("Plough Horse at Work", st + furrows, hi)


@design("horses_andalusian", T)
def andalusian(rng):
    legs = {"fn": (70, -15, 0, -15), "ff": (-10, -8, 28, 0), "hn": (-30, -2, 32, 0), "hf": (-4, 14, 40, 0)}
    tail = [(-0.84, 1.52), (-1.15, 1.45), (-1.25, 0.9), (-1.15, 0.3)]
    h = horse(legs=legs, neck=(64, 0.76), head=-80, ear="fwd", mane="braid", tail_pts=tail, neck_w=1.6, Lh=0.72)
    gy = h["gy"]
    return make("Andalusian with Braided Mane", mirror_all(h["strokes"] + [ground(-2.0, 2.2, gy)]), mirror_all(h["hints"]))


@design("horses_pinto", T)
def pinto(rng):
    p1 = [(0.3, 1.9), (0.55, 1.45), (0.45, 1.05), (0.15, 0.95), (-0.05, 1.2), (0.05, 1.6)]
    p2 = [(-0.4, 1.7), (-0.35, 1.2), (-0.55, 0.85), (-0.85, 0.9), (-1.2, 1.3), (-0.8, 1.75)]
    h = horse(legs={"fn": (-2, 0, 34, 0)}, neck=(54, 0.76), head=-60, ear="up", mane="hang", markings=[("patch", [p1, p2]), ("blaze", (0.25, 0.98))])
    gy = h["gy"]
    return make("Pinto Horse with Patches", h["strokes"] + [ground(-2.0, 2.2, gy)] + tufts([(1.9, gy), (-1.7, gy)]), h["hints"])


@design("horses_saddled", T)
def saddled(rng):
    h = horse(neck=(54, 0.76), head=-64, ear="fwd", mane="hang")
    sad, sad_sil = english_saddle(h)
    br = bridle(h, reins_to=h["R"]((0.45, 1.75)))
    post = rect(2.0, 0.0, 2.2, 1.4)
    st, hi = scene(obj(sad, sad_sil), obj(br, []), h, obj([post]))
    return make("Saddled Horse Ready to Ride", st + [ground(-2.0, 2.6)], hi)


@design("horses_przewalski", T)
def przewalski(rng):
    h = horse(legs={"fn": (6, 4, 36, 0)}, neck=(46, 0.72), head=-58, ear="up", mane="roach", stocky=1.12, legscale=0.9,
              wscale=1.2, Lh=0.84, neck_w=1.3, forelock=False)
    R = h["R"]
    stripe = spl([R((0.3, 1.55)), R((-0.1, 1.46)), R((-0.5, 1.5)), R((-0.78, 1.5))], closed=False)
    stripes = [[add(n_, (-0.08, 0)), add(n_, (0.08, 0))] for n_ in h["nodes"]["fn"][2:3]]
    gy = h["gy"]
    return make("Przewalski's Wild Horse", mirror_all(h["strokes"] + [stripe] + stripes + [ground(-2.0, 2.2, gy)] + tufts([(1.8, gy), (-1.7, gy), (1.3, gy)])), mirror_all(h["hints"]))


@design("horses_icelandic", T)
def icelandic(rng):
    legs = {"fn": (60, -30, -10, -20), "ff": (-10, -10, 24, 0), "hn": (-26, 4, 34, 0), "hf": (16, -22, 0, -10)}
    tail = [(-0.84, 1.52), (-1.15, 1.42), (-1.2, 0.9), (-1.12, 0.35)]
    h = horse(legs=legs, neck=(62, 0.66), head=-50, ear="fwd", mane="long", mane_len=1.3, tail_pts=tail, stocky=1.08,
              legscale=0.86, wscale=1.15, Lh=0.78, neck_w=1.2)
    gy = h["gy"]
    hills = [spl([(-2.4, gy + 0.6), (-1.2, gy + 1.4), (0.2, gy + 0.9)], closed=False)]
    return make("Icelandic Horse in Tolt", h["strokes"] + [ground(-2.2, 2.2, gy)] + hide(hills, h["sil"]), h["hints"])


@design("horses_levade", T)
def levade(rng):
    legs = {"fn": (118, 0, -20, -40), "ff": (108, -12, -30, -50), "hn": (40, -32, 18, 0), "hf": (50, -24, 26, 0)}
    h = horse(legs=legs, neck=(55, 0.74), head=-92, ear="fwd", mane="hang", tail="hang", pitch=28, pivot=(-0.9, 0.3), neck_w=1.6)
    gy = h["gy"]
    return make("Lipizzaner Stallion in a Levade", h["strokes"] + [ground(-2.6, 1.4, gy)], h["hints"])


@design("horses_polo", T)
def polo(rng):
    h = horse(legs=GALLOP, neck=(32, 0.78), head=-52, ear="fwd", mane="roach", tail="flow", pitch=5, forelock=False)
    sad, sad_sil = english_saddle(h, rider_on=True)
    R = h["R"]
    r = rider(R((0.02, 1.62)), 62, R((0.4, 2.55)), "helmet", (0.32, -0.26), (0.14, -0.6))
    hand = r["hand"]
    mallet = [[hand, (-1.4, h["gy"] + 0.25)], rect(-1.75, h["gy"] + 0.12, -1.3, h["gy"] + 0.26)]
    ball = circle(-2.2, h["gy"] + 0.12, 0.12, 20)
    reins = [quad(R((0.45, 1.95)), R((0.9, 1.9)), h["mouth"], 12)]
    st, hi = scene(r, obj(mallet + reins, [mallet[1]]), obj(sad, sad_sil), h)
    return make("Polo Pony and Player", st + [ball, ground(-2.8, 2.2, h["gy"])], hi)


@design("horses_trail_ride", T)
def trail_ride(rng):
    h = horse(legs=WALK, neck=(42, 0.78), head=-66, ear="up", mane="hang", tail="hang")
    sad, sad_sil = english_saddle(h, rider_on=True)
    r, reins = _rider_on(h, lean=82, style="helmet", hand=h["R"]((0.55, 1.85)))
    gy = h["gy"]
    t1, t2 = tree(-2.4, gy, 0.9), tree(2.5, gy, 1.1)
    st, hi = scene(r, obj(reins, []), obj(sad, sad_sil), h, t1, t2)
    return make("Trail Ride through the Woods", st + [ground(-3.4, 3.6, gy)] + tufts([(0.0, gy), (1.6, gy)]), hi)


# dropped: the subject repeats another book
def bucking(rng):
    legs = {"fn": (30, 26, 50, 30), "ff": (18, 14, 44, 20), "hn": (-122, -138, -145, -165), "hf": (-104, -122, -132, -150)}
    h = horse(legs=legs, neck=(-12, 0.8), head=-62, ear="back", mane="flow", tail_pts=[(-0.84, 1.52), (-1.05, 1.35), (-1.0, 0.95), (-1.15, 0.6)], pitch=-24, pivot=(0.7, 0.0))
    gy = h["gy"]
    return make("Frisky Horse Kicking Up Its Heels", h["strokes"] + [ground(-2.0, 2.4, gy)] + tufts([(-1.6, gy), (2.0, gy)]), h["hints"])


@design("horses_splash", T)
def splash(rng):
    h = horse(legs=GALLOP, neck=(35, 0.78), head=-50, ear="fwd", mane="flow", tail="flow", pitch=6)
    gy = h["gy"]
    wl = gy + 0.32
    water = wave(-2.8, 2.6, wl, 0.05, 9, 200)
    below = [poly((-3.0, wl), (3.0, wl), (3.0, gy - 1.0), (-3.0, gy - 1.0))]
    body = hide(h["strokes"], below)
    drops = []
    for x, y, r in [(-1.5, wl + 0.45, 0.07), (-1.2, wl + 0.75, 0.06), (1.3, wl + 0.6, 0.07), (1.65, wl + 0.35, 0.06), (0.0, wl + 0.2, 0.05), (-0.4, wl + 0.4, 0.06)]:
        drops.append(chain(arc(x, y, r, math.pi, 2 * math.pi, 8), [(x, y + 2.4 * r)], [(x - r, y)]))
    sprays = [quad((-1.6, wl), (-1.9, wl + 0.5), (-2.2, wl + 0.15), 10), quad((1.2, wl), (1.6, wl + 0.6), (2.0, wl + 0.1), 10),
              quad((-0.3, wl), (-0.1, wl + 0.35), (0.15, wl + 0.05), 10)]
    ripples = [ellipse(x, wl - 0.25, w, 0.07, 30) for x, w in [(-1.4, 0.4), (1.3, 0.35), (0.0, 0.3)]]
    return make("Horse Splashing through Water", body + hide([water], h["sil"]) + drops + hide(sprays, h["sil"]) + ripples, h["hints"])


@design("horses_shade_tree", T)
def shade_tree(rng):
    legs = {"hn": (-22, 12, 70, 70), "hf": (-26, 4, 34, 0)}
    h = horse(legs=legs, neck=(25, 0.78), head=-80, ear="back", mane="hang", tail="swish")
    t = tree(-1.4, 0.0, 1.35)
    st, hi = scene(h, t)
    return make("Horse Dozing in the Shade", st + [ground(-3.0, 2.4)] + tufts([(2.0, 0.0), (-2.6, 0.0)]), hi)


@design("horses_sunset", T)
def sunset(rng):
    h = horse(legs=WALK, neck=(56, 0.76), head=-56, ear="fwd", mane="flow", mane_len=0.8, tail="swish")
    gy = h["gy"]
    s_ = sun(0.2, gy + 1.9, 1.2, 14, 0.5)
    hill = spl([(-3.0, gy + 0.2), (-1.5, gy + 0.05), (0.5, gy), (2.0, gy + 0.1), (3.0, gy + 0.35)], closed=False)
    far = spl([(-3.0, gy + 0.7), (-2.0, gy + 1.1), (-0.8, gy + 0.65)], closed=False)
    far2 = spl([(1.2, gy + 0.6), (2.2, gy + 1.0), (3.0, gy + 0.7)], closed=False)
    birds = [chain(arc(x - 0.12, y, 0.12, 0.3, math.pi - 0.2, 6), arc(x + 0.12, y, 0.12, 0.2, math.pi - 0.3, 6)) for x, y in [(-2.2, gy + 3.0), (-1.7, gy + 3.3), (2.3, gy + 3.2)]]
    st, hi = scene(h, s_ + [far, far2])
    return make("Horse at Sunset", st + [hill] + birds, hi)


# dropped: the subject repeats another book
def drinking(rng):
    legs = {"fn": (14, 10, 44, 0), "ff": (24, 18, 50, 0)}
    h = horse(legs=legs, neck=(-46, 1.0), head=-96, ear=100, mane="hang", tail="hang")
    gy = h["gy"]
    water_top = gy - 0.05
    bank = [ground(-2.2, 0.75, gy)]
    stream = [wave(0.9, 3.0, gy - 0.08, 0.03, 4, 60), wave(0.4, 3.0, gy - 0.65, 0.04, 5, 60)]
    m = h["mouth"]
    ripples = [ellipse(m[0] + 0.05, gy - 0.25, rx, rx * 0.25, 40) for rx in (0.22, 0.42)]
    stones = [spl([(0.55, gy - 0.05), (0.62, gy + 0.12), (0.85, gy + 0.12), (0.9, gy - 0.05)], closed=False),
              spl([(2.3, gy - 0.65), (2.4, gy - 0.48), (2.7, gy - 0.5), (2.75, gy - 0.66)], closed=False)]
    reeds = [quad((2.6, gy - 0.1), (2.6 + d * 0.5, gy + 0.6), (2.6 + d, gy + 1.0 + abs(d)), 10) for d in (-0.2, 0.0, 0.25)]
    st, hi = scene(h, ripples + stream + stones + reeds)
    return make("Horse Drinking from a Stream", st + bank + tufts([(-1.8, gy)]), hi)


@design("horses_neighing", T)
def neighing(rng):
    legs = {"fn": (70, 20, 30, 10), "ff": (-6, -4, 30, 0)}
    h = horse(legs=legs, neck=(72, 0.8), head=-10, ear="back", mane="flow", mane_len=0.8, tail="high", mouth_open=True, neck_w=1.2)
    gy = h["gy"]
    return make("Neighing Stallion", h["strokes"] + [ground(-2.0, 2.2, gy)] + tufts([(1.9, gy), (-1.7, gy)]), h["hints"])


@design("horses_blanket", T)
def blanket(rng):
    h = horse(neck=(44, 0.76), head=-66, ear="up", mane="hang", tail="hang")
    rug = spl([(0.5, 1.72), (0.68, 1.55), (*(0.9, 1.25), 0), (0.75, 1.1), (*(0.55, 1.02), 0), (0.0, 1.0), (*(-0.7, 1.0), 0),
               (-0.98, 1.2), (*(-1.0, 1.45), 0), (-0.82, 1.62), (-0.6, 1.68), (-0.38, 1.61), (-0.1, 1.57), (0.2, 1.61)], closed=True)
    rug = [rug]
    hem = [spl([(0.55, 1.1), (0.0, 1.08), (-0.68, 1.08), (-0.9, 1.2)], closed=False)]
    straps = [[(0.0, 1.0), (0.05, 0.88)], [(-0.3, 1.0), (-0.25, 0.92)]]
    st, hi = scene(obj(rug + hem, rug), h)
    return make("Horse in a Stable Blanket", mirror_all(st + straps + [ground(-2.0, 2.2)]), mirror_all(hi))


@design("horses_canter", T)
def canter(rng):
    h = horse(legs=GALLOP3, neck=(40, 0.78), head=-56, ear="fwd", mane="flow", tail="flow", pitch=4, markings=[("blaze", (0.3, 0.95))])
    gy = h["gy"]
    return make("Cantering Horse", h["strokes"] + [ground(-2.4, 2.0, gy - 0.3)] + tufts([(-2.0, gy - 0.3), (1.6, gy - 0.3)]), h["hints"])


@design("horses_country_lane", T)
def country_lane(rng):
    h = horse(legs=WALK, neck=(48, 0.76), head=-64, ear="up", mane="hang", tail="swish")
    gy = h["gy"]
    lane = [[(-3.0, gy - 0.6), (-0.6, gy + 0.9)], [(3.0, gy - 0.6), (0.6, gy + 0.9)]]
    posts = [rect(x - 0.05 * s_, gy + y, x + 0.05 * s_, gy + y + 0.6 * s_) for x, y, s_ in [(-2.6, 0.2, 1.0), (-1.9, 0.55, 0.8), (-1.3, 0.8, 0.6)]]
    hills = [spl([(-3.2, gy + 1.1), (-1.5, gy + 1.7), (0.3, gy + 1.2), (1.8, gy + 1.6), (3.2, gy + 1.15)], closed=False)]
    st, hi = scene(h, lane + posts + hills)
    return make("Horse Walking down a Country Lane", st, hi)


@design("horses_reach_fence", T)
def reach_fence(rng):
    h = horse(neck=(12, 0.9), head=-32, ear="fwd", mane="hang", tail="hang")
    fence = rail_fence(-1.9, 1.1, 0.0, 1.15, 3, 3)
    apple_tree = tree(3.0, 0.0, 1.0)
    apple = [circle(2.15, 1.75, 0.13, 16), circle(3.2, 2.4, 0.13, 16), circle(2.7, 1.5, 0.13, 16)]
    st, hi = scene(fence, h, obj(apple), apple_tree)
    return make("Horse Reaching over the Fence", st + [ground(-1.8, 4.0)], hi)


# ------------------------------------------------------------ portraits & props

def head_neck(P, ang, Lh, crest, under, ear="up", dish=0.0, mouth_open=False, flip=False, far=True, forelock=True):
    """A side-view head (poll at P, axis angle `ang`) with its neck: `crest`
    and `under` are lists of points the neck lines pass through, starting
    near the head.  Returns (strokes, hints, silhouette)."""
    a = math.radians(ang)

    def H(p):
        x, y = p[0], p[1]
        q = (P[0] + x * math.cos(a) - y * math.sin(a), P[1] + x * math.sin(a) + y * math.cos(a))
        return (q[0], q[1], 0) if len(p) > 2 else q
    hp_ = [H(p) for p in head_pts(dish, ear, Lh, mouth_open)]
    seq = list(reversed(crest)) + hp_[::-1][1:] + list(under)
    seq = [list(seq[0]) + [0] if len(seq[0]) == 2 else seq[0]] + seq[1:]
    line = spl([tuple(p) for p in seq], closed=False, res=24)
    sil = line + [line[0]]
    det, eyep = head_details(Lh, not mouth_open)
    det = [[H(p) for p in d] for d in det]
    head_poly = spl(hp_, closed=True)
    if far:
        fe = spl([H(p) for p in far_ear(ear, Lh)], closed=False, res=40)
        det += hide([fe], [head_poly])
    if forelock:
        fl = [H((0.06 * Lh, 0.08 * Lh)), H((0.2 * Lh, 0.04 * Lh)), H((0.3 * Lh, -0.02 * Lh), ) + (0,), H((0.24 * Lh, 0.07 * Lh)), H((0.16 * Lh, 0.12 * Lh))]
        det.append(spl(fl, closed=False, res=40 / max(Lh, 0.5)))
    hints = [eye(*H(eyep), 0.045 * Lh)]
    st = [line] + det
    if flip:
        st = [mirror_x(s_) for s_ in st]
        hints = [mirror_x(s_) for s_ in hints]
        sil = mirror_x(sil)
        head_poly = mirror_x(head_poly)
    return {"strokes": st, "hints": hints, "sil": [sil], "H": H, "head_poly": head_poly}


def locks(base_pts, flow, length, n_pts=4, wav=0.12):
    """Flowing hair strands starting at each base point."""
    out = []
    for k, b in enumerate(base_pts):
        L = length * (0.8 + 0.25 * math.sin(k * 1.7))
        d = (flow[0] * L, flow[1] * L)
        nrm = (-flow[1], flow[0])
        w = wav * (1 if k % 2 else -1)
        out.append(cubic(b, (b[0] + d[0] * 0.33 + nrm[0] * w, b[1] + d[1] * 0.33 + nrm[1] * w),
                         (b[0] + d[0] * 0.66 - nrm[0] * w, b[1] + d[1] * 0.66 - nrm[1] * w), (b[0] + d[0], b[1] + d[1]), 20))
    return out


def mane_lock_shapes(base_pts, flow, length, width=0.22):
    """Tapered flowing locks (closed leaf-like shapes)."""
    out = []
    for k, b in enumerate(base_pts):
        L = length * (0.85 + 0.2 * math.sin(k * 2.3))
        nrm = (-flow[1], flow[0])
        c = [add(add(b, flow, L * t), nrm, 0.18 * L * math.sin(math.pi * 1.5 * t + k)) for t in (0.0, 0.33, 0.66, 1.0)]
        cl = cubic(*c, 24)
        out.append(tube(cl, lambda t: width * math.sin(math.pi * (0.15 + 0.85 * t)) ** 0.7 * (1 - t) + 0.01))
    return out


@design("horses_head_flowing_mane", T)
def head_flowing_mane(rng):
    crest = [(-0.3, 1.8), (-0.9, 1.2), (-1.3, 0.0), (-1.5, -1.6)]
    under = [(0.45, 0.05), (0.2, -0.8), (0.3, -1.7)]
    hn = head_neck((0.0, 2.0), -58, 2.2, crest, under, ear="fwd")
    bases = [cubic((-0.25, 1.85), (-0.8, 1.4), (-1.2, 0.5), (-1.45, -1.3), 20)[k] for k in (1, 4, 7, 10, 13, 16, 19)]
    lk = mane_lock_shapes(bases, (-0.82, -0.57), 1.5, 0.5)
    bottom = [spl([(-1.5, -1.6), (-0.6, -1.9), (0.3, -1.7)], closed=False)]
    st, hi = scene(hn, obj(lk))
    return make("Horse Head with Flowing Mane", st + bottom, hi)


@design("horses_head_bridle", T)
def head_bridle(rng):
    Lh = 2.2
    crest = [(-0.4, 1.7), (-1.0, 0.8), (-1.25, -0.6), (-1.3, -1.8)]
    under = [(0.35, -0.05), (0.15, -0.9), (0.25, -1.9)]
    hn = head_neck((0.0, 2.0), -62, Lh, crest, under, ear="up")
    H = hn["H"]
    s = lambda pts: [H((x * Lh, y * Lh)) for x, y in pts]  # noqa: E731
    straps = [s([(0.09, 0.07), (0.13, -0.15), (0.2, -0.5)]),  # headpiece / cheekpiece
              s([(0.13, 0.07), (0.17, -0.12), (0.24, -0.5)]),
              s([(0.06, 0.08), (0.2, 0.11)])[:0] + s([(0.22, 0.1), (0.22, -0.02)])[:0],
              s([(0.62, 0.05), (0.66, -0.42)]), s([(0.67, 0.05), (0.71, -0.41)]),  # noseband
              s([(0.17, -0.12), (0.84, -0.27)])[:0]]
    brow = s([(0.11, 0.09), (0.26, 0.11)])
    ring = H((0.9 * Lh, -0.3 * Lh))
    cheek = [s([(0.2, -0.45), (0.86, -0.29)]), s([(0.22, -0.5), (0.86, -0.33)])][:0]
    bit = [circle(ring[0], ring[1], 0.13, 20)]
    cheek_piece = [s([(0.2, -0.5), (0.5, -0.38), (0.84, -0.29)]), s([(0.24, -0.5), (0.52, -0.43), (0.85, -0.34)])]
    reins = [quad(ring, (ring[0] - 0.4, ring[1] - 1.2), (-0.6, -1.9), 20), quad((ring[0], ring[1] - 0.13), (ring[0] - 0.2, ring[1] - 1.3), (-0.3, -1.95), 20)]
    bottom = [spl([(-1.3, -1.8), (-0.5, -2.05), (0.25, -1.9)], closed=False)]
    tack = straps[:2] + straps[3:5] + [brow] + cheek_piece
    st, hi = scene(obj(bit), obj(tack, []), hn)
    return make("Horse Head with English Bridle", st + hide(reins, bit) + bottom, hi)


@design("horses_head_front", T)
def head_front(rng):
    right = spl([(0.0, 2.0), (0.42, 1.98), (0.72, 1.85), (0.86, 1.45), (0.92, 1.05), (0.84, 0.5), (0.68, -0.3), (0.58, -0.95),
                 (0.66, -1.45), (0.6, -1.9), (0.32, -2.15), (0.0, -2.2)], closed=False)
    head = right + mirror_x(right)[::-1][1:]
    ear_r = spl([(0.42, 1.98), (0.6, 2.5), (*(0.82, 3.05), 0), (0.9, 2.45), (0.76, 1.9)], closed=False)
    ear_in = spl([(0.55, 2.1), (0.72, 2.6), (0.8, 2.85)], closed=False)
    eye_r = lens((0.62, 1.15), (0.9, 0.95), 0.32, 12)
    nost = spl([(0.42, -1.25), (0.52, -1.45), (0.45, -1.7), (0.3, -1.6)], closed=False)
    mouth = spl([(-0.3, -1.98), (0.0, -2.04), (0.3, -1.98)], closed=False)
    blaze = spl([(0.0, 1.35), (0.18, 0.7), (0.1, -0.4), (0.24, -1.15), (0.0, -1.3), (-0.24, -1.15), (-0.1, -0.4), (-0.18, 0.7)], closed=True)
    forelock = [spl([(0.0, 2.05), (0.28, 1.7), (*(0.2, 1.18), 0), (0.06, 1.5), (*(-0.05, 1.08), 0), (-0.15, 1.5), (*(-0.32, 1.22), 0), (-0.3, 1.7), (0.0, 2.05)], closed=False)]
    neck = [spl([(0.8, 0.5), (1.2, -0.6), (1.45, -2.0), (1.55, -2.9)], closed=False), spl([(-0.8, 0.5), (-1.2, -0.6), (-1.45, -2.0), (-1.55, -2.9)], closed=False)]
    mane = locks([(-1.25 - 0.05 * k, 0.2 - 0.6 * k) for k in range(5)], (-0.6, -0.8), 0.9, wav=0.1)
    fl_poly = forelock[0] + [forelock[0][0]]
    face = [head + [head[0]]]
    parts = hide([head, ear_r, mirror_x(ear_r), ear_in, mirror_x(ear_in), eye_r, mirror_x(eye_r), nost, mirror_x(nost), mouth, blaze], [fl_poly])
    st = forelock + parts + hide(neck + mane, face)
    hints = [eye(0.79, 1.06, 0.07), eye(-0.79, 1.06, 0.07)]
    return make("Horse Portrait, Front View", st, hints)


@design("horses_eye", T)
def horse_eye(rng):
    lid = spl([(*(-2.2, 0.0), 0), (-1.2, 0.95), (0.4, 1.15), (1.7, 0.6), (*(2.3, -0.1), 0)], closed=False)
    low = spl([(-2.2, 0.0), (-1.0, -0.75), (0.6, -0.85), (1.7, -0.45), (2.3, -0.1)], closed=False)
    iris = ellipse(0.1, 0.12, 1.15, 0.85, 80)
    pupil = rrect(-0.55, -0.05, 0.75, 0.35, 0.2)
    shine = ellipse(0.6, 0.6, 0.22, 0.14, 20)
    fold = [spl([(-2.0, 0.5), (-0.8, 1.55), (0.6, 1.7), (2.0, 1.0)], closed=False), spl([(-1.6, -0.6), (0.2, -1.25), (1.9, -0.75)], closed=False)]
    lashes = []
    for k in range(7):
        t = 0.15 + 0.7 * k / 6
        i = int(t * (len(lid) - 1))
        p = lid[i]
        q = lid[min(len(lid) - 1, i + 1)]
        d = (q[0] - p[0], q[1] - p[1])
        L = math.hypot(*d) or 1
        n = (-d[1] / L, d[0] / L)
        tip = add(add(p, n, 0.75), (1, 0), 0.35)
        lashes.append(quad(p, add(add(p, n, 0.45), (1, 0), -0.05), tip, 10))
    brow = spl([(-2.6, 1.6), (-0.8, 2.6), (1.2, 2.6), (2.8, 1.6)], closed=False)
    hair = locks([(-2.4 + 0.6 * k, 3.3 - 0.05 * k) for k in range(6)], (0.25, -0.97), 0.9, wav=0.1)
    hair = hide(hair, [poly((-3, 2.75), (3, 2.75), (3, -2), (-3, -2))])
    hair = [h_ for h_ in locks([(-2.4 + 0.55 * k, 3.4) for k in range(7)], (0.3, -0.95), 0.75, wav=0.08)]
    cut = hide([iris], [pupil + [pupil[0]], shine])
    return make("Horse Eye with Long Lashes", [lid, low, pupil, shine, brow] + fold + lashes + cut, [])


@design("horses_heart_heads", T)
def heart_heads(rng):
    crest = [(-1.05, 1.95), (-1.9, 1.75), (-2.35, 0.7), (-1.9, -0.7), (-0.9, -1.7), (0.0, -2.6)]
    under = [(-0.55, 0.1), (-0.5, -0.9), (-0.25, -1.9), (0.0, -2.6)]
    left = head_neck((-0.62, 1.55), -68, 1.65, crest, under, ear="fwd")
    right = {"strokes": [mirror_x(s_) for s_ in left["strokes"]], "hints": [mirror_x(s_) for s_ in left["hints"]],
             "sil": [mirror_x(s_) for s_ in left["sil"]]}
    bases = [cubic(crest[0], (-1.9, 1.9), (-2.4, 0.4), (-1.5, -1.1), 20)[k] for k in (0, 3, 6, 9, 12, 15)]
    lk = locks(bases, (-0.75, -0.45), 0.7, wav=0.1)
    st, hi = scene(left, right)
    return make("Two Horses Making a Heart", st, hi)


@design("horses_stable_door", T)
def stable_door(rng):
    opening = rect(-1.5, -2.6, 1.5, 1.9)
    half = rect(-1.5, -2.6, 1.5, -0.25)
    brace = [[(-1.35, -0.45), (1.35, -0.45)], [(-1.35, -2.4), (1.35, -2.4)], [(-1.25, -2.4), (1.25, -0.45)]]
    planks = [[(x, -0.45), (x, -2.4)] for x in (-0.75, 0.0, 0.75)]
    hn = head_neck((0.05, 1.45), -62, 1.55, [(-0.35, 1.3), (-0.95, 0.4), (-1.1, -0.6)], [(0.4, 0.2), (0.25, -0.6)], ear="fwd")
    wall = [[(x, -2.6), (x, 2.4)] for x in (-2.8, -2.2, 2.2, 2.8)]
    roof = [poly((-3.4, 2.4), (3.4, 2.4), (3.0, 3.0), (-3.0, 3.0), closed=True)]
    bucket = [poly((1.75, -0.6), (2.45, -0.6), (2.35, -1.5), (1.85, -1.5), closed=True), arc(2.1, -0.6, 0.35, 0.0, math.pi, 12)]
    lamp = [circle(-2.5, 1.2, 0.18, 16), [(-2.5, 1.38), (-2.5, 1.8)]]
    door = obj([half] + brace + planks, [half])
    st, hi = scene(door, hn, obj([opening]))
    return make("Horse Looking over the Stable Door", st + hide(wall, [opening]) + roof + [ground(-3.4, 3.4, -2.6)] + hide(bucket, []) + lamp, hi)


@design("horses_three_heads", T)
def three_heads(rng):
    a = head_neck((-1.9, 1.3), -70, 1.25, [(-2.3, 1.0), (-2.6, 0.0), (-2.65, -1.2)], [(-1.75, 0.1), (-1.7, -1.2)], ear="fwd")
    b = head_neck((0.1, 1.9), -58, 1.3, [(-0.3, 1.7), (-0.8, 0.6), (-0.85, -1.2)], [(0.45, 0.6), (0.25, -1.2)], ear="up")
    c = head_neck((1.7, 1.1), -80, 1.2, [(1.3, 0.95), (1.1, 0.0), (1.05, -1.2)], [(1.95, 0.0), (2.0, -1.2)], ear="fwd")
    rails = [rect(-3.2, -0.55, 3.2, -0.3), rect(-3.2, -1.35, 3.2, -1.1)]
    posts = [rect(x - 0.15, -2.0, x + 0.15, 0.0) for x in (-3.0, 3.0)]
    fence = obj(posts + hide(rails, posts), posts + rails)
    st, hi = scene(fence, b, a, c)
    return make("Three Curious Horses over a Fence", hide(st, [poly((-4, -1.2), (4, -1.2), (4, -3), (-4, -3))]) + [ground(-3.4, 3.4, -2.0)], hi)


@design("horses_apple", T)
def apple_treat(rng):
    hn = head_neck((-0.6, 1.9), -62, 2.3, [(-1.0, 1.6), (-1.6, 0.4), (-1.75, -1.6)], [(-0.4, -0.2), (-0.5, -1.6)], ear="fwd", mouth_open=True)
    H = hn["H"]
    m = H((0.98 * 2.3, -0.42 * 2.3))
    ap = spl([(m[0], m[1] + 0.32), (m[0] + 0.4, m[1] + 0.38), (m[0] + 0.55, m[1] - 0.05), (m[0] + 0.3, m[1] - 0.45), (m[0], m[1] - 0.38),
              (m[0] - 0.3, m[1] - 0.45), (m[0] - 0.55, m[1] - 0.05), (m[0] - 0.4, m[1] + 0.38)], closed=True)
    stem = [[(m[0], m[1] + 0.32), (m[0] + 0.08, m[1] + 0.6)], lens((m[0] + 0.08, m[1] + 0.5), (m[0] + 0.5, m[1] + 0.7), 0.35, 10)]
    bottom = [spl([(-1.75, -1.6), (-1.1, -1.85), (-0.5, -1.6)], closed=False)]
    st, hi = scene(obj([ap] + stem, [ap]), hn)
    return make("Horse Nibbling an Apple", st + bottom, hi)


@design("horses_english_saddle", T)
def saddle_on_fence(rng):
    seat = spl([(*(1.7, 1.25), 0), (1.45, 0.95), (0.6, 0.6), (-0.6, 0.65), (-1.5, 1.05), (*(-1.85, 1.45), 0), (-2.0, 1.2), (-1.8, 0.75), (-1.2, 0.35),
                (1.2, 0.3), (1.75, 0.65), (*(1.95, 1.0), 0)], closed=True)
    flap = spl([(1.0, 0.35), (1.25, -0.4), (1.2, -1.15), (*(0.9, -1.45), 0), (*(-0.3, -1.45), 0), (-0.55, -1.0), (-0.45, 0.0), (-0.3, 0.32)], closed=False)
    knee = spl([(0.9, 0.2), (1.05, -0.5), (0.95, -1.2)], closed=False)
    pad = spl([(2.3, 0.6), (2.4, -1.0), (*(2.1, -1.7), 0), (*(-1.6, -1.7), 0), (-2.05, -0.8), (-2.2, 0.75)], closed=False)
    leather = [[(0.25, 0.3), (0.25, -2.25)], [(0.4, 0.3), (0.4, -2.25)]]
    iron = spl([(0.32, -2.15), (-0.05, -2.4), (*(-0.15, -2.95), 0), (*(0.8, -2.95), 0), (0.7, -2.4)], closed=True)
    tread = [(-0.12, -2.82), (0.77, -2.82)]
    girth = [spl([(1.5, -1.6), (1.6, -2.4), (1.5, -3.1)], closed=False), spl([(1.85, -1.6), (1.95, -2.4), (1.85, -3.1)], closed=False)]
    buckles = [rect(1.42, -1.95, 2.02, -1.75)]
    rail = rect(-3.2, -0.6, 3.2, -0.15)
    posts = [rect(-3.0, -3.3, -2.6, 0.2), rect(2.6, -3.3, 3.0, 0.2)]
    front = obj([seat, flap, knee] + leather + [iron, tread], [seat, flap + [flap[0]]])
    st, hi = scene(front, obj(girth + buckles, []), obj([pad], [pad + [pad[0]]]), obj([rail]), obj(posts))
    return make("English Saddle on a Fence Rail", st, hi)


@design("horses_riding_gear", T)
def riding_gear(rng):
    dome = chain(arc(-1.2, 0.6, 1.3, 0.0, math.pi, 50), [(-2.5, 0.6), (0.1, 0.6)])
    peak = spl([(0.1, 0.6), (0.6, 0.45), (*(0.75, 0.3), 0), (0.05, 0.35)], closed=False)
    band = [(-2.5, 0.85), (0.1, 0.85)]
    vents = [lens((-1.6 + 0.6 * k, 1.5), (-1.4 + 0.6 * k, 1.75), 0.3, 8) for k in range(3)]
    harness = [spl([(-2.1, 0.6), (-1.7, -0.25), (-1.2, -0.45), (-0.7, -0.25), (-0.3, 0.6)], closed=False), rect(-1.35, -0.6, -1.05, -0.3)]
    button = circle(-1.2, 1.9, 0.12, 12)

    def boot(x):
        return spl([(x - 0.4, 2.6), (x - 0.42, 0.0), (x - 0.5, -1.6), (*(x - 0.55, -2.7), 0), (*(x + 0.95, -2.7), 0), (x + 0.95, -2.35),
                    (x + 0.4, -2.0), (x + 0.28, -1.2), (x + 0.4, 0.0), (*(x + 0.45, 2.6), 0)], closed=True)
    b1, b2 = [transform(boot(0.0), 1.6, 0.0, 0.9)], [transform(boot(0.0), 2.6, 0.2, 0.9)]
    tops = [ellipse(1.6, 2.34, 0.4, 0.1, 24), ellipse(2.6, 2.54, 0.4, 0.1, 24)]
    heels = [[(1.6 - 0.55 * 0.9, -2.2), (1.6 - 0.05, -2.2)]]
    crop = tube([(-2.8, -2.8), (0.6, -0.8)], 0.08)
    grip = tube([(-2.8, -2.8), (-2.1, -2.39)], 0.18)
    flap_ = lens((0.6, -0.8), (1.0, -0.55), 0.35, 10)
    loop = ellipse(-3.0, -2.95, 0.2, 0.12, 16, rot=0.5)
    st, hi = scene(obj([dome, peak, band] + vents + [button] + harness, [dome]), obj(b1 + tops[:1]), obj(b2 + tops[1:]), obj([grip, crop, flap_, loop]))
    return make("Riding Helmet, Boots and Crop", st + heels, hi)


@design("horses_grooming_kit", T)
def grooming_kit(rng):
    box = poly((-2.6, -2.5), (0.6, -2.5), (0.85, -0.6), (-2.85, -0.6))
    handle = [[(-2.7, -0.6), (-2.7, 1.0), (0.7, 1.0), (0.7, -0.6)], [(-2.7, 0.8), (0.7, 0.8)]]
    dandy = [rect(-2.3, -0.6, -1.4, 0.0)] + [[(-2.25 + 0.21 * k, 0.0), (-2.25 + 0.21 * k, 0.6)] for k in range(5)]
    comb = [rect(-1.1, -0.6, -0.9, 1.6), [(-0.9, 1.4), (-0.4, 1.4)]] + [[(-0.9, 1.4 - 0.25 * k), (-0.6, 1.4 - 0.25 * k)] for k in range(4)]
    pick = [rect(-0.2, -0.6, 0.1, 0.8), spl([(0.1, 0.8), (0.35, 1.2), (0.55, 1.05), (0.4, 0.85)], closed=False)]
    front = [spl([(-2.4, -1.2), (-1.0, -1.05), (0.4, -1.2)], closed=False)]
    curry = [ellipse(2.0, -1.6, 1.0, 0.65, 60), ellipse(2.0, -1.6, 0.7, 0.42, 50), ellipse(2.0, -1.6, 0.4, 0.22, 30), rrect(1.4, -0.95, 2.6, -0.7, 0.1)]
    brush = [ellipse(2.0, 0.6, 1.0, 0.45, 60), [(1.0, 0.55), (3.0, 0.55)][:0], rrect(1.3, 0.95, 2.7, 1.25, 0.15)]
    bristles = [[(1.15 + 0.25 * k, 0.15 - 0.03 * abs(k - 3.4)), (1.15 + 0.25 * k, -0.15)] for k in range(8)]
    st, hi = scene(obj([box] + front, [box]), obj(dandy, [dandy[0]]), obj(comb, [comb[0]]), obj(pick))
    return make("Horse Grooming Kit", st + handle[:1] + curry + hide(brush, []) + bristles, hi)


@design("horses_haynet", T)
def haynet(rng):
    ring = [circle(-1.0, 2.6, 0.22, 20), rect(-1.15, 2.85, -0.85, 3.2)]
    bag = spl([(-1.0, 2.35), (-0.1, 1.9), (0.3, 0.5), (-0.2, -1.0), (*(-1.0, -1.7), 0), (-1.8, -1.0), (-2.3, 0.5), (-1.9, 1.9)], closed=True)
    grid = []
    for k in range(-6, 7):
        grid.append([(-1.0 + 0.45 * k - 2.0, -2.5), (-1.0 + 0.45 * k + 2.0, 3.0)])
        grid.append([(-1.0 + 0.45 * k + 2.0, -2.5), (-1.0 + 0.45 * k - 2.0, 3.0)])
    grid = within(grid, [bag])
    hay = [quad((-1.5 + 0.3 * k, 1.9), (-1.6 + 0.35 * k, 2.4), (-1.9 + 0.5 * k, 2.6 + 0.1 * (k % 2)), 8) for k in range(4)]
    drawstring = [(-1.6, 2.1), (-1.0, 2.38), (-0.4, 2.1)]
    bucket = [poly((0.7, -0.4), (2.9, -0.4), (2.6, -2.7), (1.0, -2.7)), ellipse(1.8, -0.4, 1.1, 0.25, 50), arc(1.8, -0.4, 1.1, 0.0, math.pi, 30)]
    water = [wave(1.0, 2.6, -0.75, 0.04, 3, 40)]
    bands = [[(0.75, -0.8), (2.85, -0.8)], [(0.92, -2.2), (2.68, -2.2)]]
    wall = [[(-3.2, y), (3.2, y)] for y in (3.0, -2.7)]
    st, hi = scene(obj(ring), obj([bag] + grid + hay + [drawstring], [bag]), obj(bucket + hide(water, []) + hide(bands, []), [bucket[0]]))
    return make("Hay Net and Water Bucket", st + hide(wall, [bag, bucket[0], ring[1]]), hi)


@design("horses_trailer", T)
def trailer(rng):
    body = spl([(*(-2.8, -0.6), 0), (*(-2.8, 1.9), 0), (-2.6, 2.15), (0.8, 2.2), (1.6, 1.9), (2.0, 1.0), (*(2.0, -0.6), 0)], closed=True)
    window = rrect(0.0, 0.9, 1.4, 1.75, 0.15)
    hn = head_neck((0.85, 1.65), -70, 0.7, [(0.55, 1.6), (0.2, 1.0), (0.1, 0.6)], [(1.05, 1.15), (1.05, 0.6)], ear="fwd")
    hn = {"strokes": within(hn["strokes"], [window]), "hints": hn["hints"], "sil": []}
    stripe = [[(-2.8, 0.2), (2.0, 0.2)]]
    ramp = [rect(-2.6, -0.4, -1.8, 1.7)]
    vents = [rrect(-1.2, 1.5, -0.4, 1.7, 0.08), rrect(-1.2, 1.15, -0.4, 1.35, 0.08)]
    wheels = [circle(x, -0.8, 0.5, 40) for x in (-1.0, 0.2)] + [circle(x, -0.8, 0.2, 20) for x in (-1.0, 0.2)]
    fender = [arc(-0.4, -0.6, 1.25, 0.0, math.pi, 30)]
    hitch = [[(2.0, -0.2), (3.2, -0.5)], [(2.0, -0.5), (3.2, -0.6)], circle(3.25, -0.52, 0.12, 12), [(2.7, -0.55), (2.7, -1.2)], circle(2.7, -1.25, 0.15, 12)]
    st, hi = scene(obj(wheels), obj([body] + stripe + ramp + vents + [window], [body]), obj(fender, []), obj(hitch, []))
    return make("Horse Trailer", hide(st, [rrect(0.0, 0.9, 1.4, 1.75, 0.15)]) + [window] + hn["strokes"] + [ground(-3.2, 3.6, -1.3)], hi + hn["hints"])


# dropped: the subject repeats another book
def rocking(rng):
    legs = {"fn": (38, 38, 38, 38), "ff": (30, 30, 30, 30), "hn": (-38, -38, -38, -38), "hf": (-30, -30, -30, -30)}
    h = horse(legs=legs, neck=(58, 0.74), head=-55, ear="up", mane="long", mane_len=1.1, tail="hang", wscale=1.15)
    sad, sad_sil = english_saddle(h, rider_on=True)
    R = h["R"]
    gy = h["gy"]
    rock = [arc(0.0, gy + 3.6, 3.75, math.radians(235), math.radians(305), 50), arc(0.0, gy + 3.6, 3.55, math.radians(237), math.radians(303), 50)]
    rock = [chain(rock[0], rock[1][::-1], [rock[0][0]])]
    peg = [rect(*h["H"]((0.3 * 0.74, 0.0)), *h["H"]((0.3 * 0.74, 0.0)))][:0]
    pg = h["H"]((0.36 * 0.74, -0.1 * 0.74))
    handle = [[(pg[0] - 0.25, pg[1] + 0.02), (pg[0] + 0.25, pg[1] - 0.02)]]
    stand = [[(x, gy + 0.05), (x, gy - 0.25)] for x in (-0.9, 0.9)][:0]
    st, hi = scene(obj(sad, sad_sil), h, obj(rock))
    return make("Wooden Rocking Horse", st + handle, hi)


# dropped: the subject repeats another book
def carousel(rng):
    legs = {"fn": (78, -20, -10, -30), "ff": (60, -40, -20, -40), "hn": (-26, 4, 34, 0), "hf": (-10, 10, 38, 0)}
    h = horse(legs=legs, neck=(64, 0.74), head=-66, ear="fwd", mane="flow", tail="high", neck_w=1.4)
    sad, sad_sil = english_saddle(h, rider_on=True)
    R = h["R"]
    gy = h["gy"]
    x0 = 0.05
    pole = [[(x0 - 0.07, gy - 0.4), (x0 - 0.07, 3.6)], [(x0 + 0.07, gy - 0.4), (x0 + 0.07, 3.6)]]
    twist = [[(x0 - 0.07, y), (x0 + 0.07, y + 0.12)] for y in [gy - 0.3 + 0.35 * k for k in range(30)] if y + 0.12 < 3.6]
    caps = [rect(x0 - 0.2, 3.6, x0 + 0.2, 3.75), rect(x0 - 0.2, gy - 0.55, x0 + 0.2, gy - 0.4)]
    gar = [circle(*R((0.8 + 0.1 * math.cos(t), 1.25 + 0.3 * math.sin(t))), 0.06, 10) for t in []]
    breast = [spl([R((0.85, 1.32)), R((0.6, 1.2)), R((0.4, 1.3))], closed=False)]
    jewels = [circle(*R(p), 0.07, 12) for p in [(0.72, 1.24), (0.55, 1.22)]]
    platform = [ellipse(x0, gy - 0.6, 2.6, 0.35, 80)]
    st, hi = scene(obj(sad + breast + jewels, sad_sil), h, obj(pole + hide(twist, []), []), obj(caps))
    return make("Carousel Horse on a Pole", st + hide(platform, caps), hi)


@design("horses_rosette", T)
def rosette(rng):
    ring = polar(lambda t: 1.75 + 0.14 * math.sin(16 * t), cx=0, cy=1.0, n=400)
    ring2 = polar(lambda t: 1.35 + 0.08 * math.sin(16 * t + 1), cx=0, cy=1.0, n=300)
    centre = circle(0, 1.0, 1.0, 80)
    hn = head_neck((0.0, 1.65), -66, 0.62, [(-0.18, 1.55), (-0.38, 1.1), (-0.42, 0.55)], [(0.12, 1.1), (0.12, 0.55)], ear="fwd")
    hn = within(hn["strokes"], [centre])
    ribbons = [poly((-0.8, -0.4), (-1.6, -3.0), (-1.15, -2.65), (-0.75, -3.1), (-0.1, -0.7)), poly((0.8, -0.4), (1.6, -3.0), (1.15, -2.65), (0.75, -3.1), (0.1, -0.7))]
    st, hi = scene(obj([centre]), obj([ring2]), obj([ring]), obj(ribbons))
    return make("Horse Show Rosette", st + hn + [[(-0.42, 0.55), (0.12, 0.55)]], [])


@design("horses_weathervane", T)
def weathervane(rng):
    h = place(horse(legs=GALLOP, neck=(35, 0.78), head=-48, ear="fwd", mane="flow", tail="flow", pitch=6), 0.0, 1.0, 1.0)
    gy = h["gy"]
    arrow = [[(-2.8, gy - 0.25), (2.6, gy - 0.25)], poly((2.6, gy - 0.05), (3.1, gy - 0.25), (2.6, gy - 0.45)),
             poly((-2.8, gy - 0.25), (-3.2, gy + 0.15), (-2.5, gy + 0.15), (-2.2, gy - 0.25), (-2.5, gy - 0.65), (-3.2, gy - 0.65))]
    post = [[(0.0, gy - 0.25), (0.0, gy - 2.8)], [(-0.1, gy - 0.1), (-0.1, gy - 0.25)][:0]]
    struts = [[(-0.45, gy + 0.05), (-0.45, gy - 0.25)], [(0.45, gy + 0.1), (0.45, gy - 0.25)]]
    cross = [[(-1.6, gy - 1.6), (1.6, gy - 1.6)], [(-0.8, gy - 1.25), (0.8, gy - 1.95)]]
    balls = [circle(x, y, 0.13, 14) for x, y in [(-1.73, gy - 1.6), (1.73, gy - 1.6), (-0.92, gy - 1.2), (0.92, gy - 2.0)]]
    globe = [circle(0.0, gy - 1.0, 0.2, 16)]
    roof = [poly((-2.2, gy - 3.6), (0.0, gy - 2.8), (2.2, gy - 3.6), closed=False)]
    st, hi = scene(h, obj(globe + balls), obj(arrow + struts + post + cross, []))
    return make("Galloping Horse Weathervane", st + roof, hi)


@design("horses_chess_knight", T)
def chess_knight(rng):
    head = spl([(-0.85, -1.3), (-0.75, -0.6), (-1.05, 0.1), (-1.65, 0.35), (*(-1.85, 0.75), 0), (-1.7, 1.2), (-1.0, 1.85), (-0.7, 2.35),
                (*(-0.45, 2.95), 0), (-0.15, 2.4), (0.45, 2.25), (0.95, 1.5), (1.1, 0.4), (0.95, -0.6), (0.85, -1.3)], closed=False)
    mane = [spl([(-0.2, 2.25), (0.25, 1.95), (0.55, 1.4), (0.68, 0.6), (0.6, -0.4)], closed=False)]
    notches = [[(0.25, 1.95), (0.55, 2.0)], [(0.55, 1.4), (0.88, 1.4)], [(0.68, 0.6), (1.0, 0.55)]]
    eye_ = lens((-0.75, 1.55), (-0.4, 1.5), 0.3, 10)
    nost = arc(-1.55, 0.95, 0.12, 0.5, 4.5, 10)
    mouth = [(-1.8, 0.55), (-1.4, 0.6)]
    collar = ellipse(0.0, -1.4, 1.05, 0.22, 50)
    base = [spl([(-0.95, -1.55), (-1.05, -2.0), (*(-1.5, -2.35), 0), (*(-1.5, -2.85), 0), (*(1.5, -2.85), 0), (*(1.5, -2.35), 0), (1.05, -2.0), (0.95, -1.55)], closed=False),
            [(-1.5, -2.35), (1.5, -2.35)], [(-1.3, -2.15), (1.3, -2.15)][:0]]
    st, hi = scene(obj([collar]), obj([head, eye_, nost, mouth] + mane + notches, []), obj(base, []))
    return make("Chess Knight", st, [eye(-0.55, 1.52, 0.07)])


@design("horses_trophy", T)
def trophy(rng):
    cup = spl([(*(-1.6, 2.4), 0), (-1.5, 1.0), (-1.0, 0.0), (-0.3, -0.5), (*(-0.25, -1.4), 0), (*(0.25, -1.4), 0), (0.3, -0.5), (1.0, 0.0), (1.5, 1.0), (*(1.6, 2.4), 0)], closed=True)
    rim = [(-1.6, 2.1), (1.6, 2.1)]
    handles = [spl([(-1.55, 1.9), (-2.4, 1.9), (-2.3, 0.8), (-1.3, 0.4)], closed=False), spl([(1.55, 1.9), (2.4, 1.9), (2.3, 0.8), (1.3, 0.4)], closed=False)]
    stem = [ellipse(0, -1.45, 0.45, 0.12, 20), poly((-0.35, -1.55), (-0.9, -2.0), (0.9, -2.0), (0.35, -1.55), closed=False), rect(-1.3, -2.8, 1.3, -2.0), rect(-1.05, -2.6, 1.05, -2.2)]
    hn = head_neck((0.05, 1.55), -64, 0.75, [(-0.2, 1.45), (-0.45, 0.95), (-0.5, 0.4)], [(0.3, 0.85), (0.25, 0.4)], ear="fwd")
    medal = circle(0.0, 1.05, 0.85, 50)
    hn_s = within(hn["strokes"], [medal])
    st, hi = scene(obj([medal]), obj([cup, rim] + handles + stem, [cup]))
    return make("Horse Show Trophy Cup", st + hn_s, hn["hints"])


@design("horses_trojan", T)
def trojan(rng):
    h = horse(legs={"fn": (0, 0, 0, 0), "ff": (-6, -6, -6, 0), "hn": (-12, -12, -12, 0), "hf": (-6, -6, -6, 0)}, neck=(58, 0.74), head=-55,
              ear="up", mane="roach", tail="hang", wscale=1.3, stocky=1.05, forelock=False)
    gy = h["gy"]
    R = h["R"]
    planks = within([[(-1.5, y), (1.5, y)] for y in (1.05, 1.3, 1.55)], [h["sil"][0]])
    neck_pl = within([[R((0.4, 1.75)), R((1.0, 2.1))], [R((0.6, 1.5)), R((1.1, 1.85))]], [h["sil"][0]])
    hatch = [[R(p) for p in rect(-0.35, 1.0, 0.15, 1.35)]]
    deck = rect(-1.6, gy - 0.4, 1.6, gy)
    wheels = [circle(x, gy - 0.5, 0.35, 30) for x in (-1.1, 0.0, 1.1)] + [circle(x, gy - 0.5, 0.08, 10) for x in (-1.1, 0.0, 1.1)]
    st, hi = scene(obj([deck]), obj(wheels[3:]), obj(wheels[:3]), h)
    return make("Wooden Trojan Horse", st + planks + neck_pl + hatch + [ground(-2.2, 2.2, gy - 0.85)], hi)


@design("horses_hobby_horse", T)
def hobby_horse(rng):
    hn = head_neck((0.3, 1.9), -60, 1.6, [(0.0, 1.8), (-0.45, 1.0), (-0.55, 0.3)], [(0.75, 0.6), (0.4, 0.3)], ear="up")
    bases = [cubic((0.0, 1.85), (-0.3, 1.5), (-0.45, 1.0), (-0.55, 0.4), 12)[k] for k in (0, 3, 6, 9, 12)]
    mane = mane_lock_shapes(bases, (-0.9, -0.3), 0.8, 0.25)
    bow = [lens((0.0, 0.25), (-0.6, 0.6), 0.35, 10), lens((0.0, 0.25), (0.5, 0.65), 0.35, 10), circle(0.0, 0.25, 0.1, 10)]
    ribbon = [quad((-0.05, 0.2), (-0.2, -0.2), (-0.45, -0.4), 8), quad((0.05, 0.2), (0.25, -0.2), (0.45, -0.45), 8)]
    cuff = [rrect(-0.6, 0.0, 0.8, 0.35, 0.1)]
    stick = [[(-0.05, 0.0), (-1.4, -3.0)], [(0.25, 0.0), (-1.1, -3.0)]]
    wheel = [circle(-1.25, -3.2, 0.35, 24), circle(-1.25, -3.2, 0.08, 10)]
    handle = [rrect(-1.6, -0.9, 1.3, -0.7, 0.1)]
    st, hi = scene(obj(bow), obj(ribbon, []), hn, obj(mane), obj(cuff), obj(handle), obj(stick, []), obj(wheel))
    return make("Hobby Horse Toy", st, hi)
