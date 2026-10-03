#!/usr/bin/env python3
"""Verify finished dot-to-dot book PDFs, reading only the printed PDF.

Checks, per book:
  * page size and page count; every font embedded (KDP requirement)
  * KDP margins: nothing printed closer to the edge than the required
    gutter (by page count) on left/right, or 0.25 in on top/bottom
  * every puzzle page: numbers 1..N each printed exactly once, N matches
    the footer, every number sits next to a dot, every dot has a number,
    no number is closer to a different dot than to its own, no numbers
    or dots overlap
  * puzzle subjects (read from the solutions pages): holiday books contain
    only their holiday, regular books contain none, and no subject
    repeats within a book or across books

  python verify_book.py output/*.pdf
"""
import json
import math
import re
import subprocess
import sys
from collections import Counter, defaultdict

import pymupdf

from dotdot import designs

INCH = 72.0
# KDP paperback inside-margin (gutter) minimums by page count.
GUTTER = [(150, 0.375), (300, 0.5), (500, 0.625), (700, 0.75), (828, 0.875)]
OUTSIDE = 0.25
DOT_MAX_W = 5.0        # dots are drawn smaller than this (pt)
LABEL_REACH = 6.5      # a number must sit within this distance of its dot (pt)
MIN_DOTS, MAX_DOTS = 1000, 2000
SOLUTIONS_PER_PAGE = 4

TITLE_THEME = {}
for name, (fn, theme) in designs.REGISTRY.items():
    TITLE_THEME[designs.build(name, 0).title] = theme


def required_gutter(pages):
    for cap, g in GUTTER:
        if pages <= cap:
            return g
    return GUTTER[-1][1]


def fonts_ok(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True).stdout.splitlines()[2:]
    bad = [l.split()[0] for l in out if l.split() and l.split()[-5] != "yes"]
    return bad


def rect_dist(px, py, r):
    dx = max(r[0] - px, 0, px - r[2])
    dy = max(r[1] - py, 0, py - r[3])
    return math.hypot(dx, dy)


def check_puzzle_page(page, frame_bottom):
    errors = []
    words = page.get_text("words")
    footer = [w for w in words if w[1] > frame_bottom]
    m = re.search(r"(\d+) dots", " ".join(w[4] for w in footer))
    if not m:
        return None, ["footer dot count missing"]
    n = int(m.group(1))
    # One text span per printed number (word extraction would merge
    # numbers that touch, which is itself reported below).
    labels = []
    for sp in page.get_texttrace():
        txt = "".join(chr(c[0]) for c in sp["chars"])
        b = sp["bbox"]
        if b[3] <= frame_bottom and txt.isdigit():
            # Ink box of digits: baseline up to cap height (the span box
            # also covers ascender/descender space that holds no ink).
            size = sp["size"]
            base = b[3] - 0.212 * size
            labels.append((b[0], base - 0.716 * size, b[2], base, txt))
    nums = [int(w[4]) for w in labels]
    cnt = Counter(nums)
    missing = sorted(set(range(1, n + 1)) - set(cnt))
    dup = sorted(k for k, v in cnt.items() if v > 1)
    extra = sorted(k for k in cnt if k < 1 or k > n)
    if missing:
        errors.append(f"missing numbers {missing[:8]}{'...' if len(missing) > 8 else ''}")
    if dup:
        errors.append(f"duplicate numbers {dup[:8]}")
    if extra:
        errors.append(f"numbers outside 1..{n}: {extra[:8]}")

    dots = []
    for d in page.get_drawings():
        r = d["rect"]
        if d["type"] in ("f", "fs") and r.width < DOT_MAX_W and r.height < DOT_MAX_W and d.get("fill") is not None:
            hollow = d["type"] == "fs"
            dots.append(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2, hollow, r.width / 2))
    # A loop's last number shares its hollow start dot (drawn twice: filled
    # then hollow on top), so merge dots at the same spot.
    merged = {}
    for x, y, hollow, rad in dots:
        key = (round(x, 1), round(y, 1))
        prev = merged.get(key)
        merged[key] = (x, y, hollow or (prev and prev[2]), rad)
    dots = list(merged.values())
    hollow_n = sum(1 for d in dots if d[2])
    if not (n - hollow_n <= len(dots) <= n):
        errors.append(f"{len(dots)} dots printed for {n} numbers")

    # Grid for nearest-dot lookups.
    cell = 12.0
    grid = defaultdict(list)
    for i, (x, y, _, _) in enumerate(dots):
        grid[(int(x // cell), int(y // cell))].append(i)

    def near(px, py, reach):
        gx, gy = int(px // cell), int(py // cell)
        k = int(reach // cell) + 1
        for i in range(gx - k, gx + k + 1):
            for j in range(gy - k, gy + k + 1):
                yield from grid.get((i, j), ())

    claims = defaultdict(list)
    far = ambiguous = 0
    for w in labels:
        rect = (w[0], w[1], w[2], w[3])
        cands = sorted((rect_dist(dots[i][0], dots[i][1], rect), i) for i in near((w[0] + w[2]) / 2, (w[1] + w[3]) / 2, 20))
        if not cands or cands[0][0] > LABEL_REACH:
            far += 1
            continue
        claims[cands[0][1]].append(int(w[4]))
        # Two different dots (almost) equally close: the solver cannot tell
        # which one the number belongs to.
        if len(cands) > 1 and cands[1][0] - cands[0][0] < 0.5:
            ambiguous += 1
    orphans = sum(1 for i in range(len(dots)) if i not in claims)
    shared = 0
    for i, ks in claims.items():
        if len(ks) > 1 and not (dots[i][2] and len(ks) == 2):
            shared += 1
    if far:
        errors.append(f"{far} numbers not next to any dot")
    if orphans:
        errors.append(f"{orphans} dots without a number")
    if shared:
        errors.append(f"{shared} dots claimed by several numbers")
    if ambiguous:
        errors.append(f"{ambiguous} numbers equally close to two dots")

    # Overlaps between number boxes (shrunk slightly: glyph boxes include
    # line spacing, so touching boxes are not touching ink).
    boxes = [(w[0], w[1], w[2], w[3]) for w in labels]
    bgrid = defaultdict(list)
    for i, b in enumerate(boxes):
        bgrid[(int(b[0] // cell), int(b[1] // cell))].append(i)
    overl = 0
    for i, b in enumerate(boxes):
        gx, gy = int(b[0] // cell), int(b[1] // cell)
        for a in range(gx - 2, gx + 3):
            for c in range(gy - 2, gy + 3):
                for j in bgrid.get((a, c), ()):
                    if j > i:
                        o = boxes[j]
                        if min(b[2], o[2]) - max(b[0], o[0]) > 0.4 and min(b[3], o[3]) - max(b[1], o[1]) > 0.4:
                            overl += 1
    if overl:
        errors.append(f"{overl} overlapping numbers")
    # Numbers side by side with no visible gap read as one number (577578).
    touch = 0
    for i, b in enumerate(labels):
        for j in range(len(labels)):
            if j == i:
                continue
            o = labels[j]
            vert = min(b[3], o[3]) - max(b[1], o[1])
            if vert > 0.5 * (b[3] - b[1]) and -0.5 <= o[0] - b[2] < 0.8:
                touch += 1
    if touch:
        errors.append(f"{touch} numbers touching a neighbour on the same line")
    close = 0
    for i, (x, y, _, rad) in enumerate(dots):
        for j in near(x, y, 3):
            if j > i and math.hypot(dots[j][0] - x, dots[j][1] - y) < 2 * rad + 0.6:
                close += 1
    if close:
        errors.append(f"{close} pairs of dots touching")
    return n, errors


def content_bbox(page):
    xs0, ys0, xs1, ys1 = [], [], [], []
    for d in page.get_drawings():
        r = d["rect"]
        lw = (d.get("width") or 0) / 2
        xs0.append(r.x0 - lw); ys0.append(r.y0 - lw); xs1.append(r.x1 + lw); ys1.append(r.y1 + lw)
    for w in page.get_text("words"):
        xs0.append(w[0]); ys0.append(w[1]); xs1.append(w[2]); ys1.append(w[3])
    if not xs0:
        return None
    return min(xs0), min(ys0), max(xs1), max(ys1)


def subjects(doc):
    """(number, scene title) from the solutions pages, plus captions per page."""
    titles, per_page = [], []
    for page in doc:
        text = page.get_text()
        if text.lstrip().startswith("Solutions"):
            found = re.findall(r"#(\d+)\s+(.+)", text)
            titles += found
            per_page.append(len(found))
    return [(int(k), t.strip()) for k, t in titles], per_page


def parts(title):
    return [t.strip() for t in title.split("\u00b7")]


def verify(path, kind):
    doc = pymupdf.open(path)
    rep = {"file": path, "pages": len(doc), "errors": [], "puzzles": 0, "dots": 0}
    W, H = doc[0].rect.width, doc[0].rect.height
    if (round(W), round(H)) != (612, 792):
        rep["errors"].append(f"page size {W}x{H}, expected 612x792 (8.5x11 in)")
    bad = fonts_ok(path)
    if bad:
        rep["errors"].append(f"fonts not embedded: {bad}")
    g = required_gutter(len(doc)) * INCH
    o = OUTSIDE * INCH
    worst = [1e9, 1e9, 1e9, 1e9]
    for i, page in enumerate(doc):
        bb = content_bbox(page)
        if not bb:
            continue
        lm, tm, rm, bm = bb[0], bb[1], W - bb[2], H - bb[3]
        worst = [min(worst[0], lm), min(worst[1], tm), min(worst[2], rm), min(worst[3], bm)]
        if lm < g or rm < g or tm < o or bm < o:
            rep["errors"].append(f"p{i + 1}: content inside KDP margin (L{lm:.1f} R{rm:.1f} T{tm:.1f} B{bm:.1f} pt)")
        if "Difficulty" in page.get_text():
            if i + 1 >= len(doc) or doc[i + 1].get_drawings() or "Difficulty" in doc[i + 1].get_text():
                rep["errors"].append(f"p{i + 2}: back of puzzle page is not blank")
            n, errs = check_puzzle_page(page, H - 67.0)
            rep["puzzles"] += 1
            rep["dots"] += n or 0
            rep.setdefault("dot_counts", []).append(n)
            for e in errs:
                rep["errors"].append(f"p{i + 1} (puzzle {rep['puzzles']}): {e}")
    rep["min_margin_in"] = {k: round(v / INCH, 3) for k, v in zip(("left", "top", "right", "bottom"), worst)}
    rep["required_gutter_in"] = required_gutter(len(doc))

    subs, per_page = subjects(doc)
    rep["subjects"] = [t for _, t in subs]
    if len(subs) != rep["puzzles"]:
        rep["errors"].append(f"{len(subs)} solutions for {rep['puzzles']} puzzles")
    if [k for k, _ in subs] != list(range(1, len(subs) + 1)):
        rep["errors"].append("solutions are not numbered 1..N in order")
    if per_page and (any(c != SOLUTIONS_PER_PAGE for c in per_page[:-1]) or per_page[-1] > SOLUTIONS_PER_PAGE):
        rep["errors"].append(f"solutions per page {per_page}, expected {SOLUTIONS_PER_PAGE}")
    names = [p for _, t in subs for p in parts(t)]
    unknown = sorted({p for p in names if p not in TITLE_THEME})
    if unknown:
        rep["errors"].append(f"unknown subjects: {unknown}")
    themes = Counter(TITLE_THEME.get(p, "custom") for p in names)
    if kind.startswith("niche:"):
        from dotdot.compose import niche_pool
        allowed = {designs.build(n, 0).title for n in niche_pool(kind[6:])}
        wrong = [p for p in names if p not in allowed]
        if wrong:
            rep["errors"].append(f"subjects outside the {kind[6:]} niche: {sorted(set(wrong))}")
    elif kind in designs.HOLIDAY_THEMES:
        wrong = [p for p in names if TITLE_THEME.get(p) != kind]
        if wrong:
            rep["errors"].append(f"non-{kind} subjects: {sorted(set(wrong))}")
    else:
        hol = [p for p in names if TITLE_THEME.get(p) in designs.SPECIAL_THEMES]
        if hol:
            rep["errors"].append(f"holiday/niche subjects in a regular book: {sorted(set(hol))}")
    rep["themes"] = dict(themes)
    dups = [t for t, c in Counter(rep["subjects"]).items() if c > 1]
    if dups:
        rep["errors"].append(f"scenes repeated inside the book: {dups[:5]}")
    for i, n in enumerate(rep.get("dot_counts", []), 1):
        if n is None or n < MIN_DOTS or n > MAX_DOTS:
            rep["errors"].append(f"puzzle {i}: {n} dots, outside {MIN_DOTS}-{MAX_DOTS}")
    return rep


def main(paths):
    reports = []
    for p in paths:
        m = re.search(r"niche_([a-z]+)", p)
        kind = (f"niche:{m.group(1)}" if m else "christmas" if "christmas" in p
                else "thanksgiving" if "thanksgiving" in p else "regular")
        r = verify(p, kind)
        reports.append(r)
        dc = [d for d in r.get("dot_counts", []) if d]
        print(f"\n== {p}: {r['pages']} pages, {r['puzzles']} puzzles, {r['dots']} dots"
              f" (min {min(dc) if dc else '-'}, max {max(dc) if dc else '-'})")
        print(f"   margins (in): {r['min_margin_in']}  required gutter: {r['required_gutter_in']}")
        print(f"   scenes: {len(set(r['subjects']))} distinct of {len(r['subjects'])}; themes {r['themes']}")
        for e in r["errors"][:25]:
            print("   ERROR", e)
        if len(r["errors"]) > 25:
            print(f"   ... {len(r['errors']) - 25} more errors")
        if not r["errors"]:
            print("   OK")
    # Cross-book repeats.
    seen = defaultdict(list)
    for r in reports:
        for t in set(r["subjects"]):
            seen[t].append(r["file"])
    cross = {t: len(f) for t, f in seen.items() if len(f) > 1}
    print(f"\nScenes appearing in more than one book: {len(cross)}")
    if cross:
        reports[0]["errors"].append(f"scenes repeated across books: {list(cross)[:5]}")
    total_err = sum(len(r["errors"]) for r in reports)
    print(f"Total errors: {total_err}")
    json.dump(reports, open("output/verify_report.json", "w"), indent=1)
    return total_err


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1:]) else 0)
