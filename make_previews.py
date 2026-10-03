#!/usr/bin/env python3
"""Preview strip for each book: the first four puzzle pages and the first solutions page.

  python make_previews.py output/niche_ocean.pdf ...   -> output/preview_niche_ocean.png
"""
import os
import subprocess
import sys
import tempfile

import pymupdf as fitz


def preview(path, dpi=40):
    doc = fitz.open(path)
    puzzles, solutions = [], []
    for i, page in enumerate(doc):
        text = page.get_text()
        if "Difficulty" in text:
            puzzles.append(i)
        elif "Solutions" in [ln.strip() for ln in text.splitlines()]:
            solutions.append(i)
    pages = puzzles[:4] + solutions[:1]
    out = os.path.join(os.path.dirname(path), "preview_" + os.path.splitext(os.path.basename(path))[0] + ".png")
    with tempfile.TemporaryDirectory() as tmp:
        files = []
        for k, i in enumerate(pages):
            f = os.path.join(tmp, f"p{k}.png")
            doc[i].get_pixmap(dpi=dpi).save(f)
            files.append(f)
        subprocess.run(["montage", *files, "-tile", f"{len(files)}x1", "-geometry", "+12+12", out], check=True)
    return out


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(preview(p))
