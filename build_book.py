#!/usr/bin/env python3
"""Build a print-ready "extreme dot-to-dot" puzzle book interior (PDF).

Examples
--------
  # 100-puzzle book, 300 -> 1100 dots, single-sided (blank backs)
  python build_book.py --puzzles 100 --min-dots 300 --max-dots 1100 --single-sided

  # Large-print edition for seniors
  python build_book.py --large-print --puzzles 50 --out large_print.pdf

  # Add your own line-art (SVG) pictures to the rotation
  python build_book.py --svg-dir my_art/ --puzzles 60
"""
import argparse
import glob
import json
import os
import random
import sys
import time

from reportlab.pdfgen import canvas

from dotdot import designs
from dotdot.designs import Design
from dotdot.geometry import load_svg
from dotdot.puzzle import make_puzzle
from dotdot.render import (SOFT, centered, draw_frame, draw_puzzle, draw_solution,
                           register_fonts, draw_stars, wrap)

PAGE_SIZES = {"letter": (612, 792), "8x10": (576, 720), "a4": (595.3, 841.9)}


def difficulty(n_dots):
    for lvl, cap in enumerate((250, 450, 700, 950), start=1):
        if n_dots <= cap:
            return lvl
    return 5


def font_for(target, large_print):
    if large_print:
        return 9.0
    if target <= 350:
        return 7.0
    if target <= 600:
        return 6.4
    if target <= 900:
        return 5.9
    return 5.5


def schedule(args, rng, svg_designs):
    """Return a list of (design_name_or_obj, seed, target_dots) for the book."""
    names = [n for n in designs.REGISTRY if not args.only or n in args.only]
    pool = []
    while len(pool) < args.puzzles:
        batch = names[:] + svg_designs
        rng.shuffle(batch)
        pool += batch
    pool = pool[:args.puzzles]
    # Avoid two of the same picture family back to back.
    for i in range(1, len(pool)):
        if pool[i] is pool[i - 1] or pool[i] == pool[i - 1]:
            j = next((k for k in range(i + 1, len(pool)) if pool[k] != pool[i - 1]), None)
            if j:
                pool[i], pool[j] = pool[j], pool[i]
    out = []
    for i, item in enumerate(pool):
        t = i / max(1, args.puzzles - 1)
        target = args.min_dots + (args.max_dots - args.min_dots) * (t ** 1.15)
        target *= rng.uniform(0.93, 1.07)
        out.append((item, rng.randrange(10**9), int(target)))
    return out


def load_svg_designs(folder):
    out = []
    for path in sorted(glob.glob(os.path.join(folder, "*.svg"))):
        strokes, hints = load_svg(path)
        if strokes:
            title = os.path.splitext(os.path.basename(path))[0].replace("_", " ").replace("-", " ").title()
            out.append(Design(title, strokes, hints, "custom"))
    return out


def build_puzzle(item, seed, target, frame, args):
    d = item if isinstance(item, Design) else designs.build(item, seed)
    fs = font_for(target, args.large_print)
    aspect = (frame[2] - frame[0]) / (frame[3] - frame[1])
    goal = target
    can_decorate = not args.no_borders
    pz = make_puzzle(d, frame, target, font_size=fs)
    for _ in range(6):
        crowded = pz.collisions / max(1, pz.dot_count) > 0.02
        short = pz.dot_count < goal * 0.8
        if not crowded and not short:
            break
        if can_decorate:
            # Picture too simple (or its dots too bunched) for this difficulty:
            # a dotted border spreads the dots over the page.
            d = designs.decorate(d, aspect, random.Random(seed))
            can_decorate = False
        elif crowded:
            # Too crowded to read: drop dots first (keeps numbers legible),
            # and only shrink the type down to a floor of 5 pt.
            target = int(target * 0.9)
            if not args.large_print:
                fs = max(5.0, fs - 0.2)
        else:
            break
        pz = make_puzzle(d, frame, target, font_size=fs)
    return pz


def title_page(c, W, H, args):
    centered(c, args.title.upper(), W / 2, H * 0.70, "NumBold", 30)
    y = H * 0.70 - 40
    centered(c, args.subtitle, W / 2, y, "Num", 15, SOFT)
    centered(c, f"{args.puzzles} puzzles  ·  {args.min_dots}–{args.max_dots} dots each", W / 2, y - 30, "Num", 12)
    if args.author:
        centered(c, args.author, W / 2, H * 0.18, "Num", 14)
    c.showPage()


def how_to_page(c, W, H, M, args):
    centered(c, "This book belongs to:", W / 2, H - M - 40, "NumBold", 18)
    c.setStrokeColor(SOFT)
    c.setLineWidth(0.8)
    c.line(W * 0.25, H - M - 85, W * 0.75, H - M - 85)

    x = M + 10
    y = H - M - 140
    centered(c, "How to play", W / 2, y, "NumBold", 18)
    y -= 34
    rules = [
        "1.  Find dot 1 (a hollow circle) and draw a line to 2, then 3, then 4 ... and keep going in order.",
        "2.  Hollow circles mark the start of a new line. When you reach one, lift your pen - do not join it to "
        "the number before it - and carry on from there. A shape that closes in a loop ends back on its hollow "
        "start dot, so that dot has two numbers.",
        "3.  Every 100th number is printed in bold to help you find your place.",
        "4.  Lines that are already printed are part of the picture: draw around them.",
        "5.  Each puzzle shows its difficulty (1 to 5 stars) and dot count. They get harder as the book goes on.",
        "6.  Stuck, or curious? Every finished picture is in the Solutions section at the back.",
        "Tip: use a fine-tip pen or a sharp pencil, and a ruler for long straight lines. Pages are printed on one "
        "side only, so markers will not ruin the next puzzle." if args.single_sided else
        "Tip: use a fine-tip pen or a sharp pencil, and a ruler for long straight lines.",
    ]
    for rline in rules:
        y = wrap(c, rline, x, y, W - 2 * x, "Num", 12, 17) - 6
    # Worked example: a tiny numbered puzzle beside its finished picture.
    size = min((W - 2 * M - 30) / 2, y - M - 40)
    left = (W / 2 - 15 - size, M + 24, W / 2 - 15, M + 24 + size)
    right = (W / 2 + 15, M + 24, W / 2 + 15 + size, M + 24 + size)
    house = Design("Example", [[(-1, 0), (1, 0), (1, 1.2), (0, 2.1), (-1, 1.2), (-1, 0)],
                               [(-0.35, 0.35), (0.35, 0.35), (0.35, 0.95), (-0.35, 0.95), (-0.35, 0.35)]])
    ex = make_puzzle(house, left, 16, font_size=11, dot_r=1.8, pad=26, milestone=0)
    draw_puzzle(c, ex)
    ex.frame = right
    shifted = right[0] - left[0]
    ex.sections = [[(px + shifted, py) for px, py in sec] for sec in ex.sections]
    draw_frame(c, right)
    c.setLineWidth(1.4)
    c.setStrokeColor(SOFT)
    for sec in ex.sections:
        p = c.beginPath()
        p.moveTo(*sec[0])
        for q in sec[1:]:
            p.lineTo(*q)
        c.drawPath(p)
    centered(c, "Puzzle", (left[0] + left[2]) / 2, M + 8, "Num", 10, SOFT)
    centered(c, "Finished: the window starts at a new hollow circle",
             (right[0] + right[2]) / 2, M + 8, "Num", 8, SOFT)
    c.showPage()


def blank_back(c, W, M):
    centered(c, "This page is intentionally left blank to prevent bleed-through.", W / 2, M + 4, "Num", 7, SOFT)
    c.showPage()


def solutions(c, W, H, M, puzzles, cols=2, rows=3):
    per = cols * rows
    gap = 18
    top = H - M - 30
    cw = (W - 2 * M - gap * (cols - 1)) / cols
    ch = (top - M - gap * (rows - 1)) / rows - 14
    for start in range(0, len(puzzles), per):
        centered(c, "Solutions", W / 2, H - M - 10, "NumBold", 16)
        for k, (n, pz) in enumerate(puzzles[start:start + per]):
            col, row = k % cols, k // cols
            x = M + col * (cw + gap)
            y = top - (row + 1) * (ch + 14) - row * gap + 14
            draw_solution(c, pz, x, y, cw, ch)
            centered(c, f"#{n}  {pz.title}", x + cw / 2, y - 12, "Num", 9)
        c.showPage()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--puzzles", type=int, default=30)
    ap.add_argument("--min-dots", type=int, default=300)
    ap.add_argument("--max-dots", type=int, default=1000)
    ap.add_argument("--page", choices=PAGE_SIZES, default="letter")
    ap.add_argument("--margin", type=float, default=0.625, help="inches; 0.625 is safe for any KDP page count")
    ap.add_argument("--single-sided", action="store_true", help="blank back on every puzzle (no bleed-through)")
    ap.add_argument("--large-print", action="store_true", help="9pt numbers, fewer dots per page")
    ap.add_argument("--svg-dir", help="folder of line-art SVGs to add to the rotation")
    ap.add_argument("--only", nargs="*", help=f"limit to these built-in designs: {', '.join(designs.REGISTRY)}")
    ap.add_argument("--no-borders", action="store_true", help="never add decorative dotted borders")
    ap.add_argument("--no-builtins", action="store_true", help="use only --svg-dir designs")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--title", default="Extreme Dot-to-Dot")
    ap.add_argument("--subtitle", default="Mindful connect-the-dots puzzles for adults")
    ap.add_argument("--author", default="")
    ap.add_argument("--out", default="output/dot_to_dot_book.pdf")
    args = ap.parse_args(argv)
    if args.large_print:
        args.max_dots = min(args.max_dots, 450)
        args.min_dots = min(args.min_dots, 150)
    if args.no_builtins:
        args.only = ["__none__"]

    register_fonts()
    W, H = PAGE_SIZES[args.page]
    M = args.margin * 72
    footer = 22
    frame = (M, M + footer, W - M, H - M)
    rng = random.Random(args.seed)
    svg_designs = load_svg_designs(args.svg_dir) if args.svg_dir else []
    plan = schedule(args, rng, svg_designs)
    if not plan:
        sys.exit("No designs to build.")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    c = canvas.Canvas(args.out, pagesize=(W, H))
    c.setTitle(args.title)
    c.setAuthor(args.author or "")

    t0 = time.time()
    built = []
    for i, (item, seed, target) in enumerate(plan, 1):
        pz = build_puzzle(item, seed, target, frame, args)
        built.append((i, pz))
        print(f"  #{i:3d} {pz.title:<18} target {target:5d} -> {pz.dot_count:5d} dots, "
              f"{pz.section_count:3d} lines, font {pz.font_size:.1f}pt, collisions {pz.collisions}", flush=True)

    title_page(c, W, H, args)
    if args.single_sided:
        c.showPage()
    how_to_page(c, W, H, M, args)
    if args.single_sided:
        c.showPage()
    for i, pz in built:
        draw_puzzle(c, pz)
        lvl = difficulty(pz.dot_count)
        c.setFillColor(SOFT)
        c.setFont("NumBold", 10)
        c.drawString(M, M + 4, f"#{i}")
        c.setFont("Num", 9)
        label, tail = "Difficulty", f"·   {pz.dot_count} dots"
        lw, tw, sw = c.stringWidth(label, "Num", 9), c.stringWidth(tail, "Num", 9), 47.5
        x = W / 2 - (lw + 8 + sw + 8 + tw) / 2
        c.drawString(x, M + 4, label)
        draw_stars(c, x + lw + 8, M + 3.5, lvl)
        c.setFillColor(SOFT)
        c.setFont("Num", 9)
        c.drawString(x + lw + 8 + sw + 8, M + 4, tail)
        c.drawRightString(W - M, M + 4, "Time: ________")
        c.showPage()
        if args.single_sided:
            blank_back(c, W, M)
    solutions(c, W, H, M, built)
    c.save()

    stats = {
        "pdf": args.out, "pages": c.getPageNumber() - 1, "puzzles": len(built),
        "dots_total": sum(p.dot_count for _, p in built),
        "label_collisions": sum(p.collisions for _, p in built),
        "seconds": round(time.time() - t0, 1),
    }
    print(json.dumps(stats, indent=2))
    return stats


if __name__ == "__main__":
    main()
