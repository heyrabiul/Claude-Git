import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

OUT = sys.argv[1]
PAGE = "German Shepherd Nation"

BLACK = colors.HexColor("#1b1b1b")
TAN = colors.HexColor("#b5752e")
CREAM = colors.HexColor("#f7efe3")
GREY = colors.HexColor("#555555")

TITLE = "Waiting For You"
FULL_PROMPT = (
    "A 25-second cinematic, photorealistic vertical video (9:16, 4K) of a loyal adult black-and-tan "
    "German Shepherd with amber eyes and a thick glossy coat, inside a cozy modern home. "
    "0-5s: The dog lies on a soft rug in front of the front door, chin resting on its paws, eyes fixed on the "
    "door handle; warm golden late-afternoon light streams through a side window, dust particles floating. "
    "5-10s: Close-up of its eyes slowly blinking, then a wall clock ticking; time-lapse of sunlight sliding "
    "across the wooden floor as evening falls. "
    "10-15s: Sound of keys jingling outside; the dog's ears snap upright, it lifts its head and its tail starts "
    "thumping on the floor. "
    "15-20s: The dog jumps up and spins in an excited circle as the door opens and the owner steps in. "
    "20-25s: Slow motion: the owner kneels down, the dog leaps into a tight hug, licking their face, tail "
    "wagging wildly; camera slowly pushes in on the happy reunion as warm light flares. "
    "Shallow depth of field, smooth camera movement, realistic fur detail and natural dog behaviour, "
    "warm emotional color grade, no text, no watermark."
)
SHOTS = [
    ("0-5s", "Dog lying at the front door, chin on paws, eyes on the handle. Golden window light."),
    ("5-10s", "Close-up of blinking eyes, clock ticking, time-lapse of sunlight moving across the floor."),
    ("10-15s", "Keys jingle outside, ears snap up, tail starts thumping."),
    ("15-20s", "Dog jumps up and spins with excitement as the door opens."),
    ("20-25s", "Slow-motion hug, face licks, wagging tail, camera pushes in."),
]
NEGATIVE = ("blurry, distorted face, extra legs, extra tail, deformed paws, cartoon, low quality, "
            "text, watermark, flickering")
AUDIO = "Soft emotional acoustic guitar, clock ticking, keys jingling, happy whines and a single excited bark."
CAPTION = ("Their whole day is waiting for you. Go hug your dog tonight.\n"
           "Type \"LOVE\" if your German Shepherd does this too!")
HASHTAGS = ("#GermanShepherdNation #GermanShepherd #GSD #GermanShepherdDog #DogLovers "
            "#DogsOfFacebook #LoyalDog #Reels #ViralDog")

label = ParagraphStyle("lb", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=TAN,
                       spaceBefore=10, spaceAfter=3)
body = ParagraphStyle("bd", fontName="Helvetica", fontSize=10, leading=14, textColor=BLACK)
cell = ParagraphStyle("cl", fontName="Helvetica", fontSize=9.5, leading=12.5, textColor=BLACK)
cellb = ParagraphStyle("cb", parent=cell, fontName="Helvetica-Bold")
h = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=CREAM)
sub = ParagraphStyle("s", fontName="Helvetica", fontSize=10.5, leading=14, textColor=TAN)


def page(c, doc):
    w, ht = A4
    c.saveState()
    c.setFillColor(BLACK)
    c.rect(0, ht - 14 * mm, w, 14 * mm, fill=1, stroke=0)
    c.setFillColor(CREAM)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(18 * mm, ht - 9 * mm, PAGE.upper())
    c.setFillColor(TAN)
    c.setFont("Helvetica", 9)
    c.drawRightString(w - 18 * mm, ht - 9 * mm, "25-Second AI Video Prompt")
    c.restoreState()


def boxed(flow, bg):
    t = Table([[flow]], colWidths=[doc.width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 3, TAN),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                        topMargin=22 * mm, bottomMargin=15 * mm,
                        title=f"{PAGE} - {TITLE}", author=PAGE)

head = Table([[Paragraph(TITLE, h)], [Paragraph("Emotional  |  25 seconds  |  Vertical 9:16 Reel", sub)]],
             colWidths=[doc.width])
head.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), BLACK),
    ("LINEBELOW", (0, -1), (-1, -1), 3, TAN),
    ("LEFTPADDING", (0, 0), (-1, -1), 12),
    ("TOPPADDING", (0, 0), (-1, 0), 12), ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
]))

shots = Table([[Paragraph(a, cellb), Paragraph(b, cell)] for a, b in SHOTS],
              colWidths=[16 * mm, doc.width - 16 * mm])
shots.setStyle(TableStyle([
    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [CREAM, colors.white]),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))

story = [
    head,
    Paragraph("FULL PROMPT - COPY AND PASTE INTO YOUR AI VIDEO TOOL", label),
    boxed(Paragraph(FULL_PROMPT, body), CREAM),
    Paragraph("SHOT-BY-SHOT TIMELINE", label),
    shots,
    Paragraph("NEGATIVE PROMPT (if your tool has this box)", label),
    Paragraph(NEGATIVE, body),
    Paragraph("MUSIC / SOUND", label),
    Paragraph(AUDIO, body),
    Paragraph("FACEBOOK CAPTION", label),
    boxed(Paragraph(CAPTION.replace("\n", "<br/>") +
                    f"<br/><br/><font color='#555555'>{HASHTAGS}</font>", body), colors.white),
    Spacer(1, 8),
    Paragraph("Tip: if your tool makes only 5-10s clips, generate each timeline row as its own clip "
              "(keep the dog description identical) and join them in CapCut.",
              ParagraphStyle("t", parent=body, fontSize=9, textColor=GREY)),
]
doc.build(story, onFirstPage=page, onLaterPages=page)
print("wrote", OUT)
