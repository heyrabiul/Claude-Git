"""Realistic (home-video style) 25-second German Shepherd video prompts -> one PDF per video.

Usage: python3 make_real_prompt_pdf.py OUTPUT_DIR
Add more entries to VIDEOS to generate more PDFs.
"""
import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                KeepTogether, PageBreak)

PAGE = "German Shepherd Nation"

INK = colors.HexColor("#222222")
ACCENT = colors.HexColor("#9a5b1e")
PAPER = colors.HexColor("#f6f3ee")
LINE = colors.HexColor("#ddd5c8")
GREY = colors.HexColor("#666666")

# The same dog wording goes into every clip so the dog looks identical across clips.
DOG = ("a real adult male German Shepherd with a black saddle, tan legs and tan face, slightly darker "
       "muzzle, upright ears, wearing a worn brown leather collar with a small metal tag, natural "
       "slightly messy coat with a little loose fur on the shoulders")

# Phone/home-video look: this is what stops the result from looking like AI.
CAMERA = ("Shot on an iPhone held by the owner, vertical 9:16, 1x lens, handheld with small natural "
          "shakes, auto-exposure and autofocus, real-time speed with no slow motion, available natural "
          "light only, no color grading, ordinary lived-in home, normal phone video quality - looks "
          "like an unedited home video posted on Facebook")

AVOID = ("cinematic, slow motion, lens flare, golden glow, dramatic lighting, studio lighting, color "
         "grading, film look, perfect shiny fur, glowing eyes, human-like facial expressions, smooth "
         "drone or gimbal movement, background music, text, subtitles, watermark, extra legs, extra "
         "tail, morphing, warped paws, plastic-looking skin or fur")

HASHTAGS = ("#GermanShepherdNation #GermanShepherd #GSD #GermanShepherdDog #DogsOfFacebook "
            "#DogLife #DogMom #DogDad #Reels")

TIPS = [
    ("Use a real photo",
     "Biggest realism boost: use Image-to-Video and upload the same real German Shepherd photo for "
     "every clip. Same photo = same dog in all 5 clips."),
    ("Make 5 short clips",
     "Generate each clip (5 seconds) separately with its own prompt, then join them in CapCut with "
     "simple hard cuts. If your tool can make 25 seconds at once, use the full 25s prompt instead."),
    ("Pick the most natural",
     "Generate 2-3 versions of each clip and keep the one where the dog moves most naturally. "
     "Delete any clip with weird legs, tail or face."),
    ("Keep the real sound",
     "Keep the natural sounds (paws, tags, panting, owner's voice). If you add a trending Facebook "
     "sound, keep it quiet underneath."),
    ("No filters",
     "Do not add filters, slow motion or fancy transitions - real home videos don't have them."),
]

VIDEOS = [
    dict(
        slug="01_Morning_Routine",
        title="A Normal Morning With My German Shepherd",
        idea="5 everyday activities in one morning: wake-up call, breakfast, bringing the leash, "
             "backyard fetch, water and flop. Feels like a real owner filmed their dog's routine.",
        clips=[
            dict(time="0-5s", act="Wake-up call",
                 scene="Bedroom, early morning, curtains half open, dim grey-blue daylight. Camera is the "
                       "owner's point of view lying in bed. The dog rests its chin on the edge of the "
                       "mattress and stares, then gives a soft huff and nudges the owner's hand with its nose.",
                 sound="quiet room, the dog's huff, owner's sleepy laugh saying \"okay, okay\""),
            dict(time="5-10s", act="Breakfast",
                 scene="Small kitchen, morning window light, beige tile floor. The dog sits impatiently "
                       "beside a steel bowl, front paws tapping, while the owner's hand pours dry kibble "
                       "from a bag. The dog starts eating right away, a few kibbles spill on the floor.",
                 sound="kibble rattling into the bowl, crunching, collar tag clinking on the bowl"),
            dict(time="10-15s", act="Brings the leash",
                 scene="Hallway by the front door, shoes on the floor. The dog trots in holding a red "
                       "nylon leash in its mouth, drops it at the owner's feet, looks up at the camera "
                       "with tail wagging and does a small excited hop.",
                 sound="tags jingling, claws clicking on the floor, owner says \"you want to go out?\""),
            dict(time="15-20s", act="Backyard fetch",
                 scene="Ordinary backyard, overcast daylight, uneven grass with a few bare patches, "
                       "wooden fence, garden hose on the ground. The owner's hand throws a worn green "
                       "tennis ball, the dog sprints after it, grabs it and runs back, dropping the "
                       "slobbery ball right in front of the camera, panting.",
                 sound="birds, distant traffic, heavy panting, owner says \"good boy\""),
            dict(time="20-25s", act="Water and flop",
                 scene="Back in the kitchen. The dog drinks noisily from a water bowl, water dripping "
                       "from its chin onto the tiles, then flops down on its side on the cool floor, "
                       "tongue out, panting, and glances at the camera.",
                 sound="loud lapping water, dripping, a big tired sigh"),
        ],
        caption="Every. Single. Morning.\nWho else has a four-legged alarm clock?",
    ),
]

st = dict(
    title=ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=19, leading=23, textColor=INK),
    meta=ParagraphStyle("m", fontName="Helvetica", fontSize=10, leading=14, textColor=ACCENT),
    label=ParagraphStyle("l", fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=ACCENT,
                         spaceBefore=10, spaceAfter=4),
    body=ParagraphStyle("b", fontName="Helvetica", fontSize=9.8, leading=13.8, textColor=INK),
    small=ParagraphStyle("s", fontName="Helvetica", fontSize=9, leading=12.5, textColor=GREY),
    clip=ParagraphStyle("c", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=INK),
)


def header_footer(c, doc):
    w, h = A4
    c.saveState()
    c.setStrokeColor(LINE)
    c.line(18 * mm, h - 13 * mm, w - 18 * mm, h - 13 * mm)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(18 * mm, h - 11 * mm, PAGE.upper())
    c.setFillColor(GREY)
    c.setFont("Helvetica", 8.5)
    c.drawRightString(w - 18 * mm, h - 11 * mm, "Realistic 25-second video prompt")
    c.drawCentredString(w / 2, 9 * mm, f"Page {doc.page}")
    c.restoreState()


def box(flows, width, bg=PAPER):
    t = Table([[f] for f in flows], colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.6, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, 0), 8), ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
    ]))
    return t


def clip_prompt(c):
    return f"{CAMERA}. {DOG[0].upper() + DOG[1:]}. {c['scene']} Sound: {c['sound']}."


def full_prompt(v):
    parts = [f"A 25-second {CAMERA[0].lower() + CAMERA[1:]}. The dog is {DOG}. One normal day, "
             f"showing {len(v['clips'])} short everyday moments joined with simple hard cuts."]
    for c in v["clips"]:
        parts.append(f"{c['time']} ({c['act']}): {c['scene']} Sound: {c['sound']}.")
    return " ".join(parts)


def build(v, out_dir):
    path = os.path.join(out_dir, f"GSN_Real_{v['slug']}.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=20 * mm, bottomMargin=16 * mm,
                            title=f"{PAGE} - {v['title']}", author=PAGE)
    W = doc.width
    s = [
        Paragraph(v["title"], st["title"]), Spacer(1, 3),
        Paragraph(f"25 seconds  |  {len(v['clips'])} activities  |  Real phone-video look  |  9:16 Reel",
                  st["meta"]),
        Paragraph("VIDEO IDEA", st["label"]),
        Paragraph(v["idea"], st["body"]),
    ]

    plan = Table([[Paragraph(f"<b>{c['time']}</b>", st["body"]), Paragraph(c["act"], st["body"])]
                  for c in v["clips"]], colWidths=[20 * mm, W - 20 * mm])
    plan.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    s += [Paragraph("TIMELINE", st["label"]), plan]

    s += [Paragraph("FULL 25-SECOND PROMPT (only if your tool can make 25s in one go)", st["label"]),
          box([Paragraph(full_prompt(v), st["body"])], W),
          Paragraph("AVOID / NEGATIVE PROMPT (paste into the negative box, or add \"Avoid: ...\" at the end)",
                    st["label"]),
          box([Paragraph(AVOID, st["body"])], W, colors.white),
          PageBreak(),
          Paragraph("CLIP-BY-CLIP PROMPTS (recommended)", st["label"]),
          Paragraph("Make each clip separately, then join them in order. Every prompt already "
                    "includes the same dog and camera wording.", st["small"]),
          Spacer(1, 4)]

    for i, c in enumerate(v["clips"], 1):
        s.append(KeepTogether([
            Spacer(1, 6),
            Paragraph(f"Clip {i}  |  {c['time']}  |  {c['act']}", st["clip"]), Spacer(1, 3),
            box([Paragraph(clip_prompt(c), st["body"])], W),
        ]))

    s += [KeepTogether([
            Paragraph("FACEBOOK CAPTION", st["label"]),
            box([Paragraph(v["caption"].replace("\n", "<br/>"), st["body"]),
                 Paragraph(HASHTAGS, st["small"])], W, colors.white)]),
          Spacer(1, 4)]

    tips = Table([[Paragraph(f"<b>{a}</b>", st["body"]), Paragraph(b, st["body"])] for a, b in TIPS],
                 colWidths=[34 * mm, W - 34 * mm])
    tips.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [PAPER, colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    s.append(KeepTogether([Paragraph("HOW TO MAKE IT LOOK REAL", st["label"]), tips]))

    doc.build(s, onFirstPage=header_footer, onLaterPages=header_footer)
    return path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    for v in VIDEOS:
        print("wrote", build(v, out))
