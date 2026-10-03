"""PDF rendering for puzzles, solutions and book front matter (ReportLab)."""
import os

from reportlab.lib.colors import Color, black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(os.path.dirname(HERE), "fonts")
INK = Color(0.1, 0.1, 0.1)
SOFT = Color(0.45, 0.45, 0.45)


def register_fonts():
    """KDP rejects PDFs with non-embedded fonts, so always embed TrueType."""
    if "Num" in pdfmetrics.getRegisteredFontNames():
        return
    pdfmetrics.registerFont(TTFont("Num", os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("NumBold", os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")))


def draw_stars(c, x, y, level, size=7.5, out_of=5, gap=2.0):
    """Difficulty stars drawn as shapes (the number font has no star glyph)."""
    import math
    c.setStrokeColor(SOFT)
    c.setFillColor(SOFT)
    c.setLineWidth(0.6)
    r = size / 2
    for i in range(out_of):
        cx = x + i * (size + gap) + r
        p = c.beginPath()
        for k in range(10):
            a = math.pi / 2 + k * math.pi / 5
            rr = r if k % 2 == 0 else r * 0.42
            (p.moveTo if k == 0 else p.lineTo)(cx + rr * math.cos(a), y + r * 0.9 + rr * math.sin(a))
        p.close()
        c.drawPath(p, stroke=1, fill=1 if i < level else 0)
    return out_of * (size + gap)


def draw_frame(c, frame, width=1.4):
    x0, y0, x1, y1 = frame
    c.setStrokeColor(black)
    c.setLineWidth(width)
    c.roundRect(x0, y0, x1 - x0, y1 - y0, 6, stroke=1, fill=0)


def draw_puzzle(c, pz, show_frame=True):
    if show_frame:
        draw_frame(c, pz.frame)
    # Pre-printed hint lines (eyes, details) — same weight a solver would draw.
    c.setStrokeColor(black)
    c.setLineWidth(0.9)
    c.setLineCap(1)
    c.setLineJoin(1)
    for h in pz.hints:
        _poly(c, h)

    r = pz.dot_r
    c.setFillColor(black)
    for sec in pz.sections:
        for i, (x, y) in enumerate(sec):
            if i == 0 or sec[i] is sec[0]:
                continue
            c.circle(x, y, r, stroke=0, fill=1)
    # Section starts are hollow: "lift your pen and start again here".
    c.setLineWidth(0.55)
    for sec in pz.sections:
        x, y = sec[0]
        c.setFillColor(white)
        c.circle(x, y, r * 1.45, stroke=1, fill=1)

    fs = pz.font_size
    c.setFillColor(INK)
    for lab in pz.labels:
        c.setFont("NumBold" if lab.bold else "Num", fs)
        c.drawString(lab.x, lab.y, str(lab.num))


def draw_solution(c, pz, x, y, w, h, line_w=0.8):
    """Draw the finished picture of `pz` scaled into the box (x, y, w, h)."""
    fx0, fy0, fx1, fy1 = pz.frame
    s = min(w / (fx1 - fx0), h / (fy1 - fy0))
    ox = x + (w - (fx1 - fx0) * s) / 2
    oy = y + (h - (fy1 - fy0) * s) / 2
    c.saveState()
    c.translate(ox, oy)
    c.scale(s, s)
    c.translate(-fx0, -fy0)
    c.setStrokeColor(SOFT)
    c.setLineWidth(0.6 / s)
    c.roundRect(fx0, fy0, fx1 - fx0, fy1 - fy0, 6, stroke=1, fill=0)
    c.setStrokeColor(black)
    c.setLineWidth(line_w / s)
    c.setLineCap(1)
    c.setLineJoin(1)
    for sec in pz.sections:
        _poly(c, sec)
    for hnt in pz.hints:
        _poly(c, hnt)
    c.restoreState()


def _poly(c, pts):
    if len(pts) < 2:
        return
    p = c.beginPath()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    c.drawPath(p, stroke=1, fill=0)


def centered(c, text, x, y, font, size, color=INK):
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawCentredString(x, y, text)


def wrap(c, text, x, y, width, font, size, leading=None, color=INK):
    """Very small word-wrapper; returns the y below the paragraph."""
    leading = leading or size * 1.35
    c.setFont(font, size)
    c.setFillColor(color)
    for para in text.split("\n"):
        line = ""
        for word in para.split():
            trial = (line + " " + word).strip()
            if pdfmetrics.stringWidth(trial, font, size) > width and line:
                c.drawString(x, y, line)
                y -= leading
                line = word
            else:
                line = trial
        c.drawString(x, y, line)
        y -= leading
    return y
