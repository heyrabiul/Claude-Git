#!/usr/bin/env python3
"""Build the KDP upload package for the 50 niche books.

  python make_kdp_package.py [slug ...]      (default: every niche)

For each book it writes  KDP_Books/NN_Title/  containing
  - the interior PDF
  - front_cover.jpg          (front cover artwork, 8.5 x 11 at 200 dpi)
  - mockups/01..10_*.jpg     (ten 1600 x 1600 marketing images)
  - listing.txt              (title, subtitle, description, keywords, categories)

All pictures are made from the book's own pages: the dots and numbers of a
puzzle page are read back from the PDF and joined in number order to show the
finished (or half-finished) picture.
"""
import math
import os
import re
import shutil
import sys
from collections import defaultdict

import pymupdf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from dotdot import compose, designs, niches
from kdp_listing_data import BOOKS

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "KDP_Books")
FONT_DIR = "/usr/share/fonts/truetype/liberation"
BOLD = os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")
REG = os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")
DPI = 200
SIDE = 1600          # mockup size (square)
PAGES = 117


def font(size, bold=True):
    return ImageFont.truetype(BOLD if bold else REG, int(size))


def rgb(hexstr):
    h = hexstr.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def fit(draw, text, max_w, size, bold=True):
    while size > 10 and draw.textlength(text, font=font(size, bold)) > max_w:
        size -= 2
    return font(size, bold)


def text_c(draw, cx, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)


# ----------------------------------------------------------- reading pages

def page_info(page):
    """Frame, dots and numbers of a puzzle page (PDF points, y down)."""
    frame = None
    dots = []
    for d in page.get_drawings():
        r = d["rect"]
        if d["type"] in ("f", "fs") and r.width < 5 and r.height < 5 and d.get("fill") is not None:
            dots.append(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2, d["type"] == "fs"))
        elif r.width > 300 and r.height > 300 and (frame is None or r.width * r.height > frame.width * frame.height):
            frame = r
    merged = {}
    for x, y, hollow in dots:
        key = (round(x, 1), round(y, 1))
        prev = merged.get(key)
        merged[key] = (x, y, hollow or bool(prev and prev[2]))
    dots = list(merged.values())
    labels = []
    for sp in page.get_texttrace():
        txt = "".join(chr(c[0]) for c in sp["chars"])
        b = sp["bbox"]
        if txt.isdigit() and frame and b[3] <= frame.y1 + 1:
            labels.append((int(txt), b))
    return frame, dots, labels


def solve_order(dots, labels):
    """Line segments (pairs of dot indices) in number order."""
    cell = 12.0
    grid = defaultdict(list)
    for i, (x, y, _) in enumerate(dots):
        grid[(int(x // cell), int(y // cell))].append(i)

    def nearest(b):
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        best, bd = None, 1e9
        for gx in range(int(cx // cell) - 2, int(cx // cell) + 3):
            for gy in range(int(cy // cell) - 2, int(cy // cell) + 3):
                for i in grid.get((gx, gy), ()):
                    x, y, _ = dots[i]
                    dx = max(b[0] - x, 0, x - b[2])
                    dy = max(b[1] - y, 0, y - b[3])
                    d = math.hypot(dx, dy)
                    if d < bd:
                        best, bd = i, d
        return best

    pos = {n: nearest(b) for n, b in labels}
    nums = sorted(n for n in pos if pos[n] is not None)
    segs = []
    start = pos[nums[0]]
    for k, k2 in zip(nums, nums[1:]):
        a, b = pos[k], pos[k2]
        if k2 != k + 1 or (dots[b][2] and b != start):
            start = b
            continue
        segs.append((k, a, b))
    return segs, len(nums)


def split_art(doc, index, color, dpi=DPI):
    """Frame crop: the finished drawing above a diagonal, the dots below it."""
    page = doc[index]
    dots_img = Image.open(_pix_png(page, dpi)).convert("RGB")
    frame, dots, labels = page_info(page)
    segs, _ = solve_order(dots, labels)
    s = dpi / 72
    lines = Image.new("RGB", dots_img.size, (255, 255, 255))
    dr = ImageDraw.Draw(lines)
    for _, a, b in segs:
        dr.line([(dots[a][0] * s, dots[a][1] * s), (dots[b][0] * s, dots[b][1] * s)], fill=color, width=4)
    box = (int(frame.x0 * s) + 4, int(frame.y0 * s) + 4, int(frame.x1 * s) - 4, int(frame.y1 * s) - 4)
    d_img, l_img = dots_img.crop(box), lines.crop(box)
    w, h = d_img.size
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon([(0, 0), (w * 1.4, 0), (0, h * 1.3)], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(18))
    return Image.composite(l_img, d_img, mask)


def render_page(doc, index, dpi=DPI, solve=0.0, color=(20, 20, 20), width=3):
    """Raster of a page; `solve` = share of the lines already drawn (0..1)."""
    page = doc[index]
    img = Image.open(_pix_png(page, dpi)).convert("RGB")
    if solve > 0:
        frame, dots, labels = page_info(page)
        segs, n = solve_order(dots, labels)
        s = dpi / 72
        dr = ImageDraw.Draw(img)
        limit = n * solve
        for k, a, b in segs:
            if k <= limit:
                dr.line([(dots[a][0] * s, dots[a][1] * s), (dots[b][0] * s, dots[b][1] * s)], fill=color, width=width)
    return img


def _pix_png(page, dpi):
    import io
    return io.BytesIO(page.get_pixmap(dpi=dpi).tobytes("png"))


def frame_px(doc, index, dpi=DPI):
    frame, _, _ = page_info(doc[index])
    s = dpi / 72
    return (int(frame.x0 * s) - 6, int(frame.y0 * s) - 6, int(frame.x1 * s) + 6, int(frame.y1 * s) + 6)


def solution_tiles(doc, sol_pages, dpi=DPI):
    tiles = []
    for i in sol_pages:
        page = doc[i]
        rects = [d["rect"] for d in page.get_drawings() if d["rect"].width > 150 and d["rect"].height > 150]
        rects.sort(key=lambda r: (round(r.y0), r.x0))
        img = Image.open(_pix_png(page, dpi)).convert("RGB")
        s = dpi / 72
        for r in rects:
            tiles.append(img.crop((int(r.x0 * s) - 4, int(r.y0 * s) - 4, int(r.x1 * s) + 4, int(r.y1 * s) + 4)))
    return tiles


# ----------------------------------------------------------- image helpers

def background(color, light=True):
    base = (250, 248, 244) if light else (36, 36, 40)
    top = mix(base, color, 0.10)
    bot = mix(base, color, 0.22)
    img = Image.new("RGB", (SIDE, SIDE), top)
    dr = ImageDraw.Draw(img)
    for y in range(SIDE):
        dr.line([(0, y), (SIDE, y)], fill=mix(top, bot, y / SIDE))
    return img


def paste_shadow(canvas, img, xy, blur=28, offset=(18, 24), opacity=110):
    x, y = xy
    sh = Image.new("L", (img.width + 4 * blur, img.height + 4 * blur), 0)
    ImageDraw.Draw(sh).rectangle([2 * blur, 2 * blur, 2 * blur + img.width, 2 * blur + img.height], fill=opacity)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    canvas.paste((0, 0, 0), (x - 2 * blur + offset[0], y - 2 * blur + offset[1]), sh)
    canvas.paste(img, (x, y))


def paste_rgba_shadow(canvas, img, xy, blur=26, offset=(16, 22), opacity=0.45):
    """Paste an RGBA image (rotated / transformed) with a soft shadow."""
    x, y = xy
    alpha = img.split()[-1]
    sh = Image.new("L", (img.width + 4 * blur, img.height + 4 * blur), 0)
    sh.paste(alpha.point(lambda a: int(a * opacity)), (2 * blur, 2 * blur))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    canvas.paste((0, 0, 0), (x - 2 * blur + offset[0], y - 2 * blur + offset[1]), sh)
    canvas.paste(img, (x, y), img)


def fit_into(img, w, h):
    s = min(w / img.width, h / img.height)
    return img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.LANCZOS)


def headline(canvas, title, sub, color):
    dr = ImageDraw.Draw(canvas)
    dark = mix(color, (0, 0, 0), 0.35)
    f = fit(dr, title, SIDE - 160, 76)
    text_c(dr, SIDE / 2, 70, title, f, dark)
    if sub:
        f2 = fit(dr, sub, SIDE - 200, 40, bold=False)
        text_c(dr, SIDE / 2, 70 + f.size + 22, sub, f2, (70, 70, 70))


def perspective_coeffs(src, dst):
    import numpy as np
    m = []
    for (x, y), (u, v) in zip(dst, src):
        m.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        m.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    a = np.array(m, dtype=float)
    b = np.array(src, dtype=float).reshape(8)
    return np.linalg.solve(a, b).tolist()


def pencil(length=900, width=46, body=(240, 190, 40)):
    img = Image.new("RGBA", (length, width), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    tip = int(width * 2.4)
    dr.rectangle([tip, 0, length - 110, width], fill=body)
    dr.rectangle([tip, width * 0.35, length - 110, width * 0.65], fill=mix(body, (255, 255, 255), 0.25))
    dr.rectangle([length - 110, 0, length - 60, width], fill=(170, 170, 175))
    for k in range(4):
        x = length - 104 + k * 12
        dr.line([(x, 0), (x, width)], fill=(130, 130, 135), width=3)
    dr.rounded_rectangle([length - 62, 0, length, width], radius=10, fill=(235, 130, 140))
    dr.polygon([(tip, 0), (tip, width), (0, width / 2)], fill=(232, 200, 160))
    dr.polygon([(tip * 0.33, width * 0.33), (tip * 0.33, width * 0.67), (0, width / 2)], fill=(50, 50, 55))
    return img


# ----------------------------------------------------------- the cover

def make_cover(title, color, art, dots_label="1,000-2,000"):
    W, H = 1700, 2200
    c = Image.new("RGB", (W, H), color)
    dr = ImageDraw.Draw(c)
    # soft dotted texture
    light = mix(color, (255, 255, 255), 0.12)
    for y in range(40, H, 46):
        for x in range(40 + (y // 46 % 2) * 23, W, 46):
            dr.ellipse([x - 3, y - 3, x + 3, y + 3], fill=light)
    accent = (255, 214, 79)
    dr.rectangle([0, 0, W, 470], fill=mix(color, (0, 0, 0), 0.25))
    text_c(dr, W / 2, 55, "EXTREME DOT-TO-DOT", font(70), accent)
    words = title.upper()
    lines = [words]
    if dr.textlength(words, font=font(150)) > W - 160 and " " in words:
        cut = words.find(" & ") if " & " in words else len(words) // 2
        if " & " not in words:
            cut = words.rfind(" ", 0, cut + 6) if words.rfind(" ", 0, cut + 6) > 0 else words.find(" ")
            lines = [words[:cut], words[cut + 1:]]
        else:
            lines = [words[:cut + 2], words[cut + 3:]]
    size = min(int(fit(dr, ln, W - 160, 150).size) for ln in lines)
    if len(lines) == 2:
        size = min(size, 112)
    y = 150 if len(lines) == 1 else 140
    for ln in lines:
        text_c(dr, W / 2, y, ln, font(size), (255, 255, 255))
        y += size + 12
    text_c(dr, W / 2, 402 if len(lines) == 1 else 405, "FOR ADULTS", font(48), accent)

    # artwork panel (portrait, the whole puzzle page)
    a = fit_into(art, 1180, 1290)
    px0 = (W - a.width) // 2 - 30
    py0 = 545
    px1, py1 = px0 + a.width + 60, py0 + a.height + 60
    dr.rounded_rectangle([px0 + 10, py0 + 14, px1 + 10, py1 + 14], radius=40, fill=mix(color, (0, 0, 0), 0.35))
    dr.rounded_rectangle([px0, py0, px1, py1], radius=40, fill=(255, 255, 255))
    c.paste(a, (px0 + 30, py0 + 30))

    # badge
    bx, by, br = W - 190, 600, 140
    dr.ellipse([bx - br, by - br, bx + br, by + br], fill=accent, outline=(255, 255, 255), width=8)
    text_c(dr, bx, by - 78, "50", font(84), (40, 40, 40))
    text_c(dr, bx, by + 12, "PUZZLES", font(40), (40, 40, 40))
    text_c(dr, bx, by + 58, "1000+ DOTS", font(30), (40, 40, 40))

    # bottom band
    dr.rectangle([0, 1940, W, H], fill=mix(color, (0, 0, 0), 0.25))
    text_c(dr, W / 2, 1975, f"50 UNIQUE PUZZLES  •  {dots_label} DOTS EACH", fit(dr, f"50 UNIQUE PUZZLES  •  {dots_label} DOTS EACH", W - 140, 58), (255, 255, 255))
    text_c(dr, W / 2, 2070, "Large 8.5 x 11 Pages  •  Solutions Included", font(44, bold=False), accent)
    return c


# ----------------------------------------------------------- mockups

def m01_cover(cover, color):
    c = background(color)
    headline(c, "", "", color)
    img = fit_into(cover, 1100, 1420)
    paste_shadow(c, img, ((SIDE - img.width) // 2, (SIDE - img.height) // 2 + 20))
    return c


def m02_book3d(cover, color):
    c = background(color)
    W, H = cover.size
    face = cover.convert("RGBA")
    dst = [(560, 220), (1330, 290), (1330, 1440), (560, 1530)]
    coeffs = perspective_coeffs([(0, 0), (W, 0), (W, H), (0, H)], dst)
    layer = face.transform((SIDE, SIDE), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    spine = Image.new("RGBA", (SIDE, SIDE), (0, 0, 0, 0))
    sd = ImageDraw.Draw(spine)
    sd.polygon([(500, 255), (560, 220), (560, 1530), (500, 1480)], fill=mix(color, (0, 0, 0), 0.45) + (255,))
    pages = Image.new("RGBA", (SIDE, SIDE), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pages)
    pd.polygon([(500, 1480), (560, 1530), (1330, 1430), (1272, 1392)], fill=(238, 236, 230, 255))
    shadow = Image.new("L", (SIDE, SIDE), 0)
    ImageDraw.Draw(shadow).ellipse([420, 1440, 1460, 1600], fill=140)
    shadow = shadow.filter(ImageFilter.GaussianBlur(40))
    c.paste((0, 0, 0), (0, 0), shadow)
    for lay in (pages, spine, layer):
        c.paste(lay, (0, 0), lay)
    headline(c, "PAPERBACK  •  8.5 x 11 IN  •  117 PAGES", "", color)
    return c


def m03_desk(cover, page_img, color):
    c = Image.new("RGB", (SIDE, SIDE), (196, 154, 108))
    dr = ImageDraw.Draw(c)
    for y in range(0, SIDE, 6):
        shade = 8 * math.sin(y / 37.0) + 5 * math.sin(y / 11.0)
        dr.line([(0, y), (SIDE, y + 30)], fill=mix((196, 154, 108), (150, 110, 70), 0.25 + shade / 60), width=6)
    pg = fit_into(page_img, 900, 1160).convert("RGBA").rotate(-7, expand=True, resample=Image.BICUBIC)
    paste_rgba_shadow(c, pg, (640, 260))
    cv = fit_into(cover, 820, 1060).convert("RGBA").rotate(6, expand=True, resample=Image.BICUBIC)
    paste_rgba_shadow(c, cv, (110, 300))
    for k, (col, ang, xy) in enumerate([((240, 190, 40), 32, (760, 1180)), ((60, 120, 200), 18, (860, 1290))]):
        p = pencil(body=col).rotate(ang, expand=True, resample=Image.BICUBIC)
        paste_rgba_shadow(c, p, xy, blur=10, offset=(8, 10))
    return c


def m04_page(page_img, color, dots):
    c = background(color)
    headline(c, f"EXTREME CHALLENGE: {dots:,} DOTS", "Every puzzle has 1,000 to 2,000 numbered dots", color)
    img = fit_into(page_img, 1040, 1260)
    paste_shadow(c, img, ((SIDE - img.width) // 2, 290))
    return c


def m05_closeup(doc, index, color):
    c = background(color)
    headline(c, "CLEAR, EASY-TO-READ NUMBERS", "No overlapping numbers  •  hollow dots mark where each line starts", color)
    big = render_page(doc, index, dpi=420)
    x0, y0, x1, y1 = frame_px(doc, index, 420)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    crop = big.crop((cx - 520, cy - 420, cx + 520, cy + 420))
    crop = fit_into(crop, 1300, 1050)
    mask = Image.new("L", crop.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, crop.width, crop.height], radius=40, fill=255)
    x, y = (SIDE - crop.width) // 2, 330
    frame = Image.new("RGBA", (crop.width + 24, crop.height + 24), (0, 0, 0, 0))
    ImageDraw.Draw(frame).rounded_rectangle([0, 0, frame.width - 1, frame.height - 1], radius=50, fill=color + (255,))
    paste_rgba_shadow(c, frame, (x - 12, y - 12))
    c.paste(crop, (x, y), mask)
    return c


def m06_before_after(doc, index, color):
    c = background(color)
    headline(c, "CONNECT THE DOTS... REVEAL THE PICTURE", "", color)
    box = frame_px(doc, index)
    before = render_page(doc, index).crop(box)
    after = render_page(doc, index, solve=1.0, width=3).crop(box)
    w, h = 690, 1080
    b = fit_into(before, w, h)
    a = fit_into(after, w, h)
    y = 260
    paste_shadow(c, b, (70, y), blur=18, offset=(10, 14))
    paste_shadow(c, a, (SIDE - 70 - a.width, y), blur=18, offset=(10, 14))
    dr = ImageDraw.Draw(c)
    dark = mix(color, (0, 0, 0), 0.35)
    text_c(dr, 70 + b.width / 2, y + b.height + 40, "BEFORE", font(54), dark)
    text_c(dr, SIDE - 70 - a.width / 2, y + a.height + 40, "AFTER", font(54), dark)
    mx, my = SIDE / 2, y + h / 2
    dr.ellipse([mx - 55, my - 55, mx + 55, my + 55], fill=color)
    dr.polygon([(mx - 22, my - 30), (mx + 32, my), (mx - 22, my + 30)], fill=(255, 255, 255))
    return c


def m07_solutions(sol_img, color):
    c = background(color)
    headline(c, "SOLUTIONS INCLUDED", "Every finished picture is at the back of the book - 4 per page", color)
    img = fit_into(sol_img, 1040, 1260)
    paste_shadow(c, img, ((SIDE - img.width) // 2, 290))
    return c


def m08_spread(page_img, color):
    c = background(color)
    headline(c, "SINGLE-SIDED PAGES", "The back of every puzzle is blank - no bleed-through, easy to frame", color)
    right = fit_into(page_img, 690, 900)
    left = Image.new("RGB", right.size, (252, 251, 248))
    w, h = right.size
    spread = Image.new("RGB", (2 * w, h), (255, 255, 255))
    spread.paste(left, (0, 0))
    spread.paste(right, (w, 0))
    grad = Image.new("L", (80, h), 0)
    gd = ImageDraw.Draw(grad)
    for x in range(80):
        gd.line([(x, 0), (x, h)], fill=int(90 * (1 - abs(x - 40) / 40) ** 2))
    spread.paste((0, 0, 0), (w - 40, 0), grad)
    paste_shadow(c, spread, ((SIDE - spread.width) // 2, 330))
    return c


def m09_inside(cover, color):
    c = background(color)
    headline(c, "WHAT'S INSIDE", "", color)
    cv = fit_into(cover, 560, 724)
    paste_shadow(c, cv, (90, 330))
    dr = ImageDraw.Draw(c)
    feats = [
        ("50 unique puzzles", "a different picture on every page"),
        ("1,000 - 2,000 dots", "true extreme challenge for adults"),
        ("Large 8.5 x 11 pages", "plenty of room, easy to read"),
        ("Clear numbers", "no overlapping or confusing labels"),
        ("Single-sided pages", "no bleed-through from markers"),
        ("Solutions at the back", "check every finished picture"),
    ]
    y = 320
    for big, small in feats:
        x = 730
        dr.ellipse([x, y, x + 74, y + 74], fill=color)
        dr.line([(x + 18, y + 38), (x + 32, y + 54), (x + 58, y + 22)], fill=(255, 255, 255), width=9)
        dr.text((x + 100, y - 2), big, font=font(48), fill=(40, 40, 40))
        dr.text((x + 100, y + 54), small, font=font(32, bold=False), fill=(90, 90, 90))
        y += 170
    text_c(dr, SIDE / 2, 1420, "Relaxing  •  Screen-free  •  Great gift", font(46, bold=False), mix(color, (0, 0, 0), 0.3))
    return c


def m10_gallery(tiles, color):
    c = background(color)
    headline(c, "50 UNIQUE PICTURES TO REVEAL", "A sample of the finished drawings inside", color)
    cols, rows = 3, 3
    tw, th = 440, 400
    gx = (SIDE - cols * tw - (cols - 1) * 40) // 2
    for i, t in enumerate(tiles[:cols * rows]):
        r, k = divmod(i, cols)
        img = fit_into(t, tw, th)
        tile = Image.new("RGB", (tw, th), (255, 255, 255))
        tile.paste(img, ((tw - img.width) // 2, (th - img.height) // 2))
        paste_shadow(c, tile, (gx + k * (tw + 40), 300 + r * (th + 40)), blur=12, offset=(6, 8), opacity=80)
    return c


# ----------------------------------------------------------- listing

def listing(n, slug, title, mains):
    color, stem, extra_kw, category, hook, gift = BOOKS[slug]
    full = f"{title} Extreme Dot-to-Dot for Adults"
    subtitle = "50 Challenging Connect-the-Dots Puzzles with 1,000 to 2,000 Dots Each | Large 8.5 x 11 | Solutions Included"
    scenes = ", ".join(mains[:10])
    bullets = [
        "50 UNIQUE PUZZLES - every page reveals a different main picture",
        "1,000 TO 2,000 DOTS per puzzle - a true extreme challenge for adults",
        "LARGE 8.5 x 11 INCH PAGES with clear, non-overlapping numbers",
        "HOLLOW START DOTS show exactly where each new line begins",
        "SINGLE-SIDED PAGES - no bleed-through, perfect for framing",
        "DIFFICULTY STARS and dot count printed on every page",
        "COMPLETE SOLUTIONS at the back of the book, 4 per page",
    ]
    intro = (f"{hook} {full} is a challenging connect-the-dots puzzle book with 50 brand-new pictures, "
             f"each one built from 1,000 to 2,000 numbered dots.")
    inside = f"Inside you will discover pictures such as {scenes} - and many more."
    close = (f"Connecting thousands of dots is a relaxing, screen-free way to unwind, sharpen your focus and "
             f"watch a beautiful picture appear line by line. A perfect gift for {gift}.")
    plain = "\n".join([intro, "", inside, "", "WHY YOU'LL LOVE THIS BOOK:", *[f"• {b}" for b in bullets], "", close, "",
                       "Grab a pen, find dot number 1 and start connecting!"])
    html = "".join([f"<p>{intro}</p>", f"<p>{inside}</p>", "<p><b>WHY YOU'LL LOVE THIS BOOK:</b></p><ul>",
                    *[f"<li>{b}</li>" for b in bullets], "</ul>", f"<p>{close}</p>",
                    "<p><b>Grab a pen, find dot number 1 and start connecting!</b></p>"])
    keywords = [
        f"{stem} dot to dot for adults",
        f"extreme dot to dot {stem}",
        f"{stem} connect the dots book for adults",
        *extra_kw,
        "hard dot to dot puzzle book 1000 dots",
    ]
    keywords = [k[:50] for k in keywords]
    lines = [
        f"BOOK {n:02d} - {full}",
        "=" * 72,
        "",
        "TITLE:",
        full,
        "",
        "SUBTITLE:",
        subtitle,
        "",
        "AUTHOR / PEN NAME:",
        "[Your Pen Name]",
        "",
        "DESCRIPTION (plain text):",
        "-" * 72,
        plain,
        "-" * 72,
        "",
        "DESCRIPTION (HTML - paste into the KDP description box):",
        html,
        "",
        "7 BACKEND KEYWORDS (one per KDP box):",
        *[f"{i}. {k}" for i, k in enumerate(keywords, 1)],
        "",
        "CATEGORIES (choose up to 3 in KDP):",
        "1. Games & Activities / Puzzles",
        "2. Games & Activities / General",
        f"3. {category}",
        "",
        "BOOK DETAILS:",
        "Trim size: 8.5 x 11 in (21.59 x 27.94 cm)",
        f"Page count: {PAGES}",
        "Interior: Black & white, white paper",
        "Bleed: No bleed",
        "Cover finish: Matte (recommended)",
        "Language: English",
        "Primary audience: Adults (not low-content, not children's book)",
        "Reading age: 13 and up",
        "",
        "SUGGESTED PRICE:",
        f"US $8.99  (printing cost about ${1.00 + 0.012 * PAGES:.2f}; royalty about ${8.99 * 0.6 - (1.00 + 0.012 * PAGES):.2f} per sale at 60%)",
        "",
        "AI CONTENT QUESTION IN KDP:",
        "The pictures were created with AI assistance, so answer YES for images",
        "(text: AI-assisted).  Check KDP's current wording before you publish.",
        "",
        "FILES IN THIS FOLDER:",
        "- interior PDF (upload as the manuscript)",
        "- front_cover.jpg (front cover artwork; build the full-wrap cover with KDP Cover Creator",
        "  or your design tool using KDP's cover calculator for 117 pages, white paper, 8.5 x 11)",
        "- mockups/ (10 marketing images for A+ content, ads and social media)",
    ]
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------- main

def safe(s):
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")


def build(n, slug, plans):
    title = niches.NICHES[slug]["title"]
    color = rgb(BOOKS[slug][0])
    src = os.path.join(ROOT, "output", f"niche_{slug}.pdf")
    folder = os.path.join(OUT, f"{n:02d}_{safe(title)}")
    mdir = os.path.join(folder, "mockups")
    os.makedirs(mdir, exist_ok=True)
    pdf_name = f"{safe(title)}_Extreme_Dot_to_Dot_for_Adults_interior.pdf"
    shutil.copyfile(src, os.path.join(folder, pdf_name))

    doc = pymupdf.open(src)
    puzzles, sols = [], []
    for i, page in enumerate(doc):
        t = page.get_text()
        if "Difficulty" in t:
            puzzles.append(i)
        elif "Solutions" in [ln.strip() for ln in t.splitlines()]:
            sols.append(i)

    accent = mix(color, (0, 0, 0), 0.25)
    art = split_art(doc, puzzles[0], accent)
    cover = make_cover(title, color, art)
    cover.save(os.path.join(folder, "front_cover.jpg"), quality=92)

    p2 = render_page(doc, puzzles[1])
    p3 = render_page(doc, puzzles[2], solve=0.35, color=(40, 40, 40), width=3)
    dots = int(re.search(r"(\d+) dots", doc[puzzles[1]].get_text()).group(1))
    sol_img = Image.open(_pix_png(doc[sols[0]], DPI)).convert("RGB")
    tiles = solution_tiles(doc, sols[:3])

    shots = [
        ("01_front_cover", m01_cover(cover, color)),
        ("02_book_3d", m02_book3d(cover, color)),
        ("03_on_the_desk", m03_desk(cover, p3, color)),
        ("04_interior_page", m04_page(p2, color, dots)),
        ("05_number_closeup", m05_closeup(doc, puzzles[1], color)),
        ("06_before_after", m06_before_after(doc, puzzles[3], color)),
        ("07_solutions", m07_solutions(sol_img, color)),
        ("08_single_sided", m08_spread(p2, color)),
        ("09_whats_inside", m09_inside(cover, color)),
        ("10_picture_gallery", m10_gallery(tiles, color)),
    ]
    for name, img in shots:
        img.save(os.path.join(mdir, f"{name}.jpg"), quality=86, optimize=True)

    mains = []
    for main, _ in plans[f"niche:{slug}"]:
        t = designs.build(main, 0).title
        if t not in mains:
            mains.append(t)
    with open(os.path.join(folder, "listing.txt"), "w", encoding="utf-8") as f:
        f.write(listing(n, slug, title, mains))
    return folder


def main(slugs):
    plans = compose.all_plans()
    order = list(niches.NICHES)
    todo = slugs or order
    for slug in todo:
        n = order.index(slug) + 1
        print(build(n, slug, plans), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
