"""Realistic (home-video style) 25-second German Shepherd video prompts -> one PDF per video.

Usage: python3 make_real_prompt_pdf.py OUTPUT_DIR [FIRST LAST] [--page nation|life|club|daily|legends|family|adventures|puppies|friends]
Video data lives in <page data dir>/videos_*.py (one VIDEOS list per file), see PAGES.
"""
import importlib.util
import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                KeepTogether, PageBreak)


INK = colors.HexColor("#222222")
ACCENT = colors.HexColor("#9a5b1e")
PAPER = colors.HexColor("#f6f3ee")
LINE = colors.HexColor("#ddd5c8")
GREY = colors.HexColor("#666666")

# The same dog wording goes into every clip so the dog looks identical across clips.
DOG_NATION = ("a real adult male German Shepherd with a black saddle, tan legs and tan face, slightly darker "
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

DOG_LIFE = ("a real adult female German Shepherd with a black saddle, rich red-tan legs, chest and face, "
            "a dark mask around the muzzle, upright ears, a slightly slimmer build, wearing a faded red "
            "nylon collar with a small round metal tag, natural slightly messy coat")

DOG_CLUB = ("a real adult male long-coat German Shepherd with a sable coat of grey-brown fur with black "
            "tips, a darker back, fluffy longer fur on the ears, neck, chest and tail, upright ears, wearing "
            "a navy blue nylon collar with a small silver tag, natural fluffy coat that is not perfectly groomed")

DOG_DAILY = ("a real adult female solid black German Shepherd with a fully black short coat that looks "
             "slightly dusty brown-black on the legs in daylight, amber-brown eyes, upright ears, athletic "
             "build, wearing a green nylon collar with a small brass tag, natural coat with a little shedding")

DOG_LEGENDS = ("a real adult male working-line bi-color German Shepherd, almost fully black with tan only on "
               "the lower legs and small tan marks on the cheeks and above the eyes, short dense coat, lean "
               "muscular athletic build, upright ears, intense focused eyes, wearing a worn orange biothane "
               "collar with a small metal tag, natural coat with a little dust from the field")

DOG_FAMILY = ("a real adult female German Shepherd with a black saddle and pale cream-silver legs, chest and "
              "face (black and silver coloring), dark ears, gentle brown eyes, medium build, wearing a purple "
              "nylon collar with a small heart-shaped tag, natural slightly fluffy coat")

DOG_ADVENTURES = ("a real adult male white German Shepherd with a pure white thick medium-length coat, black "
                  "nose, dark eyes, upright ears, strong athletic build, wearing a grey adventure harness over "
                  "a tan leather collar, coat a little dusty from the trail")

DOG_PUPPIES = ("a real 10-week-old male liver-and-tan German Shepherd puppy with a chocolate-brown saddle, "
               "warm tan legs and face, a brown nose, light amber eyes, fluffy soft puppy coat, oversized "
               "paws and floppy ears, wearing a small light blue collar")

DOG_FRIENDS = ("a real adult female long-coat black-and-tan German Shepherd with a black saddle, warm tan "
               "legs, chest and face, fluffy longer fur on the ears, neck, chest and tail, gentle eyes, "
               "upright ears, wearing a bright yellow collar with a small round tag")

TAGS = "#GermanShepherd #GSD #GermanShepherdDog #DogsOfFacebook #DogLife #DogMom #DogDad #Reels"

# One entry per Facebook page: branding, default dog and where its video data lives.
PAGES = {
    "nation": dict(name="German Shepherd Nation", prefix="GSN", data="prompt_data", dog=DOG_NATION,
                   hashtags="#GermanShepherdNation " + TAGS),
    "life": dict(name="German Shepherd Life", prefix="GSL", data="prompt_data_life", dog=DOG_LIFE,
                 hashtags="#GermanShepherdLife " + TAGS),
    "club": dict(name="German Shepherd Lovers Club", prefix="GSLC", data="prompt_data_club", dog=DOG_CLUB,
                 hashtags="#GermanShepherdLoversClub " + TAGS),
    "daily": dict(name="German Shepherd Daily", prefix="GSDaily", data="prompt_data_daily", dog=DOG_DAILY,
                  hashtags="#GermanShepherdDaily " + TAGS),
    "legends": dict(name="German Shepherd Legends", prefix="GSLegends", data="prompt_data_legends",
                    dog=DOG_LEGENDS, hashtags="#GermanShepherdLegends " + TAGS),
    "family": dict(name="German Shepherd Family", prefix="GSFamily", data="prompt_data_family",
                   dog=DOG_FAMILY, hashtags="#GermanShepherdFamily " + TAGS),
    "adventures": dict(name="German Shepherd Adventures", prefix="GSAdventures", data="prompt_data_adventures",
                       dog=DOG_ADVENTURES, hashtags="#GermanShepherdAdventures " + TAGS),
    "puppies": dict(name="German Shepherd Puppies Hub", prefix="GSPuppies", data="prompt_data_puppies",
                    dog=DOG_PUPPIES, hashtags="#GermanShepherdPuppiesHub #GermanShepherdPuppy " + TAGS),
    "friends": dict(name="German Shepherd Best Friends", prefix="GSBestFriends", data="prompt_data_friends",
                    dog=DOG_FRIENDS, hashtags="#GermanShepherdBestFriends #DogAndCat " + TAGS),
}

TIPS = [
    ("Use a real photo",
     "Biggest realism boost: use Image-to-Video and upload the same real German Shepherd photo for "
     "every clip. Same photo = same dog in all 5 clips."),
    ("Muse AI: one video",
     "Paste the full 25-second prompt into Muse AI. It tells Muse AI to combine all 5 clips into ONE "
     "25-second video. If the result comes out shorter, make each clip with its own prompt and join "
     "them in order (CapCut) with simple hard cuts."),
    ("Pick the most natural",
     "Generate 2-3 versions of each clip and keep the one where the dog moves most naturally. "
     "Delete any clip with weird legs, tail or face."),
    ("Keep the real sound",
     "Keep the natural sounds (paws, tags, panting, owner's voice). If you add a trending Facebook "
     "sound, keep it quiet underneath."),
    ("No filters",
     "Do not add filters, slow motion or fancy transitions - real home videos don't have them."),
]

HERE = os.path.dirname(os.path.abspath(__file__))


def use_page(key):
    global PAGE, PREFIX, DOG, HASHTAGS, DATA_DIR
    cfg = PAGES[key]
    PAGE, PREFIX, DOG, HASHTAGS = cfg["name"], cfg["prefix"], cfg["dog"], cfg["hashtags"]
    DATA_DIR = os.path.join(HERE, cfg["data"])


use_page("nation")


def load_videos():
    videos = []
    for name in sorted(os.listdir(DATA_DIR)):
        if name.startswith("videos_") and name.endswith(".py"):
            spec = importlib.util.spec_from_file_location(name[:-3], os.path.join(DATA_DIR, name))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            videos += mod.VIDEOS
    return sorted(videos, key=lambda v: v["slug"])


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


def clip_prompt(v, c):
    dog = v.get("dog", DOG)
    return f"{CAMERA}. {dog[0].upper() + dog[1:]}. {c['scene']} Sound: {c['sound']}."


def full_prompt(v):
    n = len(v["clips"])
    parts = [f"Make ONE single 25-second video by combining these {n} clips in order, "
             f"{25 // n} seconds each, joined with simple hard cuts into one continuous video. "
             f"{CAMERA}. The dog is {v.get('dog', DOG)}."]
    for c in v["clips"]:
        parts.append(f"{c['time']} ({c['act']}): {c['scene']} Sound: {c['sound']}.")
    return " ".join(parts)


def build(v, out_dir):
    path = os.path.join(out_dir, f"{PREFIX}_Real_{v['slug']}.pdf")
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=20 * mm, bottomMargin=16 * mm,
                            title=f"{PAGE} - {v['title']}", author=PAGE)
    W = doc.width
    s = [
        Paragraph(v["title"], st["title"]), Spacer(1, 3),
        Paragraph(f"One 25-second video  |  {len(v['clips'])} clips combined  |  Real phone-video look  |  9:16 Reel",
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

    s += [Paragraph("MUSE AI PROMPT - COMBINE ALL 5 CLIPS INTO ONE 25-SECOND VIDEO (copy and paste)", st["label"]),
          box([Paragraph(full_prompt(v), st["body"])], W),
          Paragraph("AVOID / NEGATIVE PROMPT (paste into the negative box, or add \"Avoid: ...\" at the end)",
                    st["label"]),
          box([Paragraph(AVOID, st["body"])], W, colors.white),
          PageBreak(),
          Paragraph("CLIP-BY-CLIP PROMPTS (backup)", st["label"]),
          Paragraph("Use these only if Muse AI makes a video shorter than 25 seconds: make each clip "
                    "separately, then join them in order. Every prompt already includes the same dog "
                    "and camera wording.", st["small"]),
          Spacer(1, 4)]

    for i, c in enumerate(v["clips"], 1):
        s.append(KeepTogether([
            Spacer(1, 6),
            Paragraph(f"Clip {i}  |  {c['time']}  |  {c['act']}", st["clip"]), Spacer(1, 3),
            box([Paragraph(clip_prompt(v, c), st["body"])], W),
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
    args = sys.argv[1:]
    if "--page" in args:
        i = args.index("--page")
        use_page(args[i + 1])
        del args[i:i + 2]
    sys.argv[1:] = args
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    first = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    last = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 6
    videos = [v for v in load_videos() if first <= int(v["slug"].split("_")[0]) <= last]
    for v in videos:
        build(v, out)
    print(f"wrote {len(videos)} PDFs to {out}")
