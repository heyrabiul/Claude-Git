# Extreme Dot-to-Dot Book Generator

Generates **print-ready (Amazon KDP) interiors** for "extreme" dot-to-dot puzzle
books for adults. The output has 300 to 1,100+ dots per page, readable
collision-free numbers, a smooth difficulty ramp, a how-to page and full
solutions.

See **[ANALYSIS.md](ANALYSIS.md)** for the competitor breakdown this tool was
designed around.

## Quick start

```bash
pip install -r requirements.txt

# 100 puzzles, 300 -> 1,100 dots, blank backs so markers don't bleed through
python build_book.py --puzzles 100 --min-dots 300 --max-dots 1100 --single-sided \
    --out output/extreme_dot_to_dot_100.pdf

# Large-print edition (9 pt numbers, up to 450 dots per page)
python build_book.py --large-print --puzzles 40 --single-sided --out output/large_print.pdf

# Add your own pictures (SVG line art) to the rotation
python build_book.py --svg-dir examples/ --puzzles 30

# Only your own pictures
python build_book.py --svg-dir my_art/ --no-builtins --puzzles 50
```

Each run prints one line per puzzle (dot count, number of separate lines, font
size and label collisions) followed by a JSON summary.

## What is in the book

1. **Title page**
2. **"This book belongs to" and How to play**, with a worked mini example
3. **Puzzles**, one per page, inside a rounded frame. The footer shows the puzzle
   number, a 1–5 star difficulty rating, the exact dot count and a "Time: ____" box.
4. **Solutions**, six finished pictures per page with titles. Titles never
   appear on the puzzle pages, so they don't spoil the reveal.

### Puzzle conventions

- **Hollow circle** = start of a new line. Lift the pen; don't join it to the previous number.
- A closed loop ends back on its hollow start dot, so that dot carries two numbers.
- **Every 100th number is bold**, to help the solver find their place.
- Solid printed lines (eyes and similar details) are hints and part of the picture.

## How it works

| Step | Module |
|---|---|
| Line art: 23 built-in, randomisable designs or your SVGs | `dotdot/designs.py`, `dotdot/geometry.py` (`load_svg`) |
| Order the strokes so each new line starts near where the last one ended | `geometry.order_strokes` |
| Place dots by arc length, with extra dots on tight curves and sharp corners always kept | `geometry.sample_stroke` |
| Find the spacing that hits the target dot count | `geometry.fit_spacing` |
| Thin dots where lines cross, so clusters stay readable | `puzzle._thin_crowded` |
| Place each number in one of 54 candidate spots around its dot, avoiding other numbers, dots and the lines the solver will draw, then refine | `puzzle.place_labels` |
| Retry with a decorative dotted border or fewer dots if a page is too sparse or crowded | `build_book.build_puzzle` |
| Render the PDF with embedded TrueType fonts (KDP rejects non-embedded fonts) | `dotdot/render.py` |

Built-in designs: butterfly, flower, sunflower, leaf, tree, nautilus, fish,
turtle, snail, cat, owl, mushroom, sailboat, house, balloon, lighthouse,
hearts, spirograph, mandala, Koch snowflake, dragon curve, sun and star
polygons. Most are randomised by seed, so a 100-page book doesn't repeat itself.

## Using your own artwork (recommended for animal books)

The competitors' best-selling subjects are detailed animals. To use your own
pictures:

1. Draw or trace **line art** (strokes along the contours, not filled shapes)
   in Inkscape, Illustrator or Affinity. A centre-line trace of a colouring
   page works well.
2. Export it as plain SVG. Supported elements are `path` (every command,
   including arcs), `polyline`, `polygon`, `line`, `circle`, `ellipse`, `rect`
   and transforms.
3. To keep a detail as a printed hint line (such as an eye), give it an `id`
   or `class` that contains `hint`.
4. Run with `--svg-dir your_folder/`. The file name becomes the solution title.

Only use artwork you own or that is licensed for commercial use.

## KDP settings

- Trim **8.5 × 11 in**, no bleed, black-and-white interior. Also available: `--page 8x10` or `--page a4`.
- The default 0.625 in margin meets KDP's gutter rule for any page count up to 500.
- Fonts are Liberation Sans (SIL OFL) and are embedded. The files are in `fonts/`.
- `--single-sided` roughly doubles the page count, so check KDP's
  printing-cost calculator before setting the price.
- The cover is not generated. ANALYSIS.md has the cover formula that works in
  this category.
