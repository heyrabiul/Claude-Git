#!/usr/bin/env python3
"""Draw every design of the given themes (or names) on a contact sheet PDF.

  python preview_designs.py ocean cats --out output/designs.pdf
"""
import argparse

from reportlab.pdfgen import canvas

from dotdot import designs
from dotdot.puzzle import Puzzle, fit_to_frame
from dotdot.render import draw_solution, register_fonts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("themes", nargs="+", help="themes or design names")
    ap.add_argument("--out", default="output/designs_preview.pdf")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    register_fonts()
    names = [n for n, (_, t) in designs.REGISTRY.items() if t in a.themes or n in a.themes]
    cols, cell = 5, 200
    rows = (len(names) + cols - 1) // cols
    c = canvas.Canvas(a.out, pagesize=(cols * cell, max(1, rows) * cell))
    broken = []
    for k, n in enumerate(names):
        try:
            d = designs.build(n, a.seed)
        except Exception as e:  # report every broken design, not just the first
            broken.append(f"{n}: {type(e).__name__}: {e}")
            continue
        x = (k % cols) * cell
        y = (rows - 1 - k // cols) * cell
        fr = (x + 8, y + 14, x + cell - 8, y + cell - 8)
        st, h = fit_to_frame(d, fr, 6)
        draw_solution(c, Puzzle(d.title, d.theme, st, h, frame=fr), fr[0], fr[1], fr[2] - fr[0], fr[3] - fr[1])
        c.setFont("Num", 8)
        c.drawString(x + 10, y + 4, f"{n}: {d.title}")
    c.save()
    print(a.out, len(names), "designs")
    for b in broken:
        print("BROKEN", b)


if __name__ == "__main__":
    main()
