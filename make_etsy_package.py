#!/usr/bin/env python3
"""Build the Etsy listing package for the 50 niche books (digital download).

  python make_etsy_package.py [slug ...]      (default: every niche)

For each book it writes  Etsy_Books/NN_Title/  containing
  - <Title>_Dot_to_Dot_Printable.pdf  the file buyers download: the KDP
    interior without its blank back pages (65 pages, US Letter)
  - front_cover.jpg
  - mockups/01..10_*.jpg              ten 1600 x 1600 listing photos
  - listing.txt                       Etsy title, description, 13 tags and settings
"""
import os
import re
import sys

import pymupdf
from PIL import Image, ImageDraw

import make_kdp_package as k
from dotdot import compose, designs, niches
from etsy_listing_data import ETSY, GENERIC_TAGS
from kdp_listing_data import BOOKS

OUT = os.path.join(k.ROOT, "Etsy_Books")
PRICE = "4.99"


def printable_pdf(src, dst, title):
    """The interior minus the 'intentionally left blank' back pages."""
    doc = pymupdf.open(src)
    blank = [i for i, p in enumerate(doc)
             if (not p.get_text().strip() or "intentionally left blank" in p.get_text())
             and len(p.get_drawings()) == 0]
    doc.delete_pages(blank)
    doc.set_metadata({"title": title, "author": "", "subject": "Extreme dot-to-dot puzzles for adults",
                      "keywords": "dot to dot, connect the dots, printable puzzles"})
    doc.save(dst, garbage=3, deflate=True)
    return pymupdf.open(dst).page_count


# ----------------------------------------------------------- Etsy mockups

def how_it_works(cover, color):
    c = k.background(color)
    k.headline(c, "HOW IT WORKS", "Instant digital download - nothing is shipped", color)
    dr = ImageDraw.Draw(c)
    dark = k.mix(color, (0, 0, 0), 0.3)
    steps = [
        ("BUY", ["Complete your", "purchase on Etsy"]),
        ("DOWNLOAD", ["Get the PDF instantly", "from your Etsy account"]),
        ("PRINT", ["Print at home on", "US Letter paper"]),
    ]
    cw, ch, gap = 440, 640, 40
    x0 = (k.SIDE - 3 * cw - 2 * gap) // 2
    y0 = 300
    for i, (head, lines) in enumerate(steps):
        x = x0 + i * (cw + gap)
        card = Image.new("RGB", (cw, ch), (255, 255, 255))
        k.paste_shadow(c, card, (x, y0), blur=16, offset=(8, 12), opacity=70)
        cx = x + cw // 2
        dr.ellipse([cx - 45, y0 + 30, cx + 45, y0 + 120], fill=color)
        k.text_c(dr, cx, y0 + 46, str(i + 1), k.font(56), (255, 255, 255))
        iy = y0 + 170
        if i == 0:      # shopping bag
            dr.rounded_rectangle([cx - 90, iy + 60, cx + 90, iy + 230], radius=18, outline=dark, width=12)
            dr.arc([cx - 50, iy + 5, cx + 50, iy + 115], 180, 360, fill=dark, width=12)
        elif i == 1:    # download arrow into a tray
            dr.line([(cx, iy + 10), (cx, iy + 160)], fill=dark, width=16)
            dr.polygon([(cx - 60, iy + 110), (cx + 60, iy + 110), (cx, iy + 180)], fill=dark)
            dr.line([(cx - 100, iy + 170), (cx - 100, iy + 230), (cx + 100, iy + 230), (cx + 100, iy + 170)], fill=dark, width=12)
        else:           # printer with a page
            dr.rectangle([cx - 60, iy + 10, cx + 60, iy + 90], outline=dark, width=10)
            dr.rounded_rectangle([cx - 110, iy + 80, cx + 110, iy + 190], radius=16, outline=dark, width=12)
            dr.rectangle([cx - 60, iy + 160, cx + 60, iy + 245], fill=(255, 255, 255), outline=dark, width=10)
            for yy in (iy + 185, iy + 210):
                dr.line([(cx - 40, yy), (cx + 40, yy)], fill=dark, width=6)
        k.text_c(dr, cx, y0 + 450, head, k.font(54), dark)
        for j, ln in enumerate(lines):
            k.text_c(dr, cx, y0 + 525 + j * 44, ln, k.font(34, bold=False), (80, 80, 80))
    k.text_c(dr, k.SIDE / 2, 1060, "Print one page, a few, or all 50 - as often as you like", k.font(44, bold=False), dark)
    cv = k.fit_into(cover, 300, 390)
    k.paste_shadow(c, cv, ((k.SIDE - cv.width) // 2, 1140), blur=14, offset=(8, 10))
    return c


ETSY_FEATS = [
    ("50 unique puzzles", "a different picture on every page"),
    ("1,000 - 2,000 dots", "true extreme challenge for adults"),
    ("Instant download", "printable PDF, 65 pages"),
    ("Print at home", "US Letter 8.5 x 11 (A4: fit to page)"),
    ("Clear numbers", "no overlapping or confusing labels"),
    ("Solutions included", "check every finished picture"),
]


# ----------------------------------------------------------- listing text

def etsy_title(title, stem):
    parts = [f"{title} Dot to Dot for Adults", "Extreme Connect the Dots Printable PDF",
             "50 Hard Puzzles 1000-2000 Dots", f"{stem.title()} Activity Book", "Instant Download"]
    out = parts[0]
    for p in parts[1:]:
        if len(out) + 2 + len(p) <= 140:
            out += ", " + p
    return out


def etsy_listing(n, slug, title, mains, pages, pdf_name, pdf_mb):
    color, stem, _, _, hook, gift = BOOKS[slug]
    tags, holiday = ETSY[slug]
    tags = GENERIC_TAGS[:4] + tags + GENERIC_TAGS[4:]
    name = f"{title} Extreme Dot-to-Dot for Adults"
    scenes = ", ".join(mains[:12])
    desc = f"""{name} - 50 printable connect-the-dots puzzles with 1,000 to 2,000 dots each. INSTANT DOWNLOAD - print at home and start connecting today!

{hook}

★ WHAT YOU GET ★
• 1 printable PDF file, {pages} pages, US Letter size (8.5 x 11 in)
• 50 extreme dot-to-dot puzzles - a different main picture on every page
• 1,000 to 2,000 numbered dots per puzzle
• A "How to play" page
• Complete solutions at the end (4 per page)

★ FEATURES ★
• Clear, easy-to-read numbers that never overlap
• Hollow start dots show where each new line begins
• Every 100th number is printed in bold to help you keep your place
• Difficulty stars and the dot count on every puzzle

★ PICTURES INCLUDE ★
{scenes} - and many more!

★ HOW IT WORKS ★
1. Purchase this listing.
2. Download the PDF from your Etsy account (You > Purchases and reviews) or from the link in your Etsy confirmation email.
3. Print at home or at a local print shop - print one puzzle or all 50, as often as you like.

★ PLEASE NOTE ★
• This is a DIGITAL DOWNLOAD - no physical item will be shipped.
• Made for US Letter paper. For A4 paper choose "Fit to page" / "Scale to fit" in your printer settings.
• For personal use only. Please do not resell, share or redistribute the file.
• Because this is a digital item, returns and exchanges are not accepted - but please message me if you have any problem with your file and I will gladly help.
• The pictures in this book were designed with the help of AI tools.

A relaxing, screen-free activity and a lovely gift for {gift}. Grab a pen, find dot number 1 and enjoy!
"""
    lines = [
        f"ETSY LISTING {n:02d} - {name}",
        "=" * 72,
        "",
        f"TITLE ({len(etsy_title(title, stem))} of 140 characters):",
        etsy_title(title, stem),
        "",
        "DESCRIPTION (paste as is):",
        "-" * 72,
        desc.rstrip(),
        "-" * 72,
        "",
        "13 TAGS (max 20 characters each):",
        *[f"{i:2d}. {t}" for i, t in enumerate(tags, 1)],
        "",
        "Tags in one line: " + ", ".join(tags),
        "",
        "LISTING SETTINGS:",
        "Category: Toys & Games > Games & Puzzles > Puzzles",
        "Type: Digital",
        "Who made it: I did",
        "What is it: A finished product",
        "When was it made: the most recent range (e.g. 2020 - 2026)",
        f"Holiday: {holiday or '-'}",
        "Primary colour: Black   Secondary colour: White",
        "Materials: Digital PDF, Printable",
        "Personalisation: No",
        "Renewal: Automatic",
        "Quantity: 999",
        f"Suggested price: US ${PRICE}  (try a 20-30% launch sale)",
        "",
        "DIGITAL FILE TO UPLOAD (Etsy allows 5 files, max 20 MB each):",
        f"{pdf_name}  ({pdf_mb:.1f} MB, {pages} pages)",
        "",
        "PHOTOS (upload in this order; Etsy allows up to 20):",
        "01_front_cover.jpg (thumbnail), 02_book_3d.jpg, 03_on_the_desk.jpg, 04_interior_page.jpg,",
        "05_number_closeup.jpg, 06_before_after.jpg, 07_solutions.jpg, 08_how_it_works.jpg,",
        "09_whats_inside.jpg, 10_picture_gallery.jpg",
        "",
        "AI DISCLOSURE:",
        "Etsy asks sellers to be open about AI use. The description already says the",
        "pictures were designed with the help of AI tools - keep that line.",
    ]
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------- main

def build(n, slug, plans):
    title = niches.NICHES[slug]["title"]
    color = k.rgb(BOOKS[slug][0])
    src = os.path.join(k.ROOT, "output", f"niche_{slug}.pdf")
    folder = os.path.join(OUT, f"{n:02d}_{k.safe(title)}")
    mdir = os.path.join(folder, "mockups")
    os.makedirs(mdir, exist_ok=True)
    pdf_name = f"{k.safe(title)}_Dot_to_Dot_Printable.pdf"
    pdf_path = os.path.join(folder, pdf_name)
    pages = printable_pdf(src, pdf_path, f"{title} Extreme Dot-to-Dot for Adults")
    pdf_mb = os.path.getsize(pdf_path) / 1e6

    doc = pymupdf.open(src)
    puzzles, sols = [], []
    for i, page in enumerate(doc):
        t = page.get_text()
        if "Difficulty" in t:
            puzzles.append(i)
        elif "Solutions" in [ln.strip() for ln in t.splitlines()]:
            sols.append(i)

    accent = k.mix(color, (0, 0, 0), 0.25)
    cover = k.make_cover(title, color, k.split_art(doc, puzzles[0], accent))
    cover.save(os.path.join(folder, "front_cover.jpg"), quality=92)

    p2 = k.render_page(doc, puzzles[1])
    p3 = k.render_page(doc, puzzles[2], solve=0.35, color=(40, 40, 40), width=3)
    dots = int(re.search(r"(\d+) dots", doc[puzzles[1]].get_text()).group(1))
    sol_img = Image.open(k._pix_png(doc[sols[0]], k.DPI)).convert("RGB")
    tiles = k.solution_tiles(doc, sols[:3])

    shots = [
        ("01_front_cover", k.m01_cover(cover, color)),
        ("02_book_3d", k.m02_book3d(cover, color, head="INSTANT DOWNLOAD  •  PRINTABLE PDF")),
        ("03_on_the_desk", k.m03_desk(cover, p3, color)),
        ("04_interior_page", k.m04_page(p2, color, dots)),
        ("05_number_closeup", k.m05_closeup(doc, puzzles[1], color)),
        ("06_before_after", k.m06_before_after(doc, puzzles[3], color)),
        ("07_solutions", k.m07_solutions(sol_img, color)),
        ("08_how_it_works", how_it_works(cover, color)),
        ("09_whats_inside", k.m09_inside(cover, color, feats=ETSY_FEATS)),
        ("10_picture_gallery", k.m10_gallery(tiles, color)),
    ]
    for name, img in shots:
        img.save(os.path.join(mdir, f"{name}.jpg"), quality=86, optimize=True)

    mains = []
    for main, _ in plans[f"niche:{slug}"]:
        t = designs.build(main, 0).title
        if t not in mains:
            mains.append(t)
    with open(os.path.join(folder, "listing.txt"), "w", encoding="utf-8") as f:
        f.write(etsy_listing(n, slug, title, mains, pages, pdf_name, pdf_mb))
    return folder


def main(slugs):
    plans = compose.all_plans()
    order = list(niches.NICHES)
    for slug in slugs or order:
        print(build(order.index(slug) + 1, slug, plans), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
