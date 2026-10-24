import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Table, TableStyle, KeepTogether)

OUT = sys.argv[1]
PAGE = "German Shepherd Nation"

BLACK = colors.HexColor("#1b1b1b")
TAN = colors.HexColor("#b5752e")
CREAM = colors.HexColor("#f7efe3")
GREY = colors.HexColor("#555555")

STYLE = ("Cinematic, photorealistic, 4K, shallow depth of field, natural motion, "
         "realistic fur detail, no text, no watermark, vertical 9:16, 25 seconds.")

PROMPTS = [
    dict(t="Dawn Guardian", mood="Epic / Majestic",
         p="A powerful black-and-tan German Shepherd stands on a misty hilltop at sunrise, "
           "wind moving through its thick coat, golden light rim-lighting its ears.",
         shots=[("0-5s", "Slow drone push-in through morning fog toward the dog's silhouette on the hill."),
                ("5-11s", "Close-up of amber eyes opening wide, ears snapping forward as it hears something."),
                ("11-18s", "Low-angle slow motion: the dog steps forward, chest out, fur rippling in the wind."),
                ("18-25s", "Wide shot, sun bursts over the horizon behind it, dog lets out one proud bark.")],
         audio="Epic orchestral build, distant wind, single deep bark at the climax.",
         cap="Born to protect. Built to lead."),
    dict(t="Puppy's First Snow", mood="Cute / Heartwarming",
         p="An 8-week-old fluffy German Shepherd puppy discovers snow for the first time in a quiet backyard.",
         shots=[("0-5s", "Puppy peeks out of a doorway, nose twitching at falling snowflakes."),
                ("5-12s", "It hops into the snow, sinks up to its belly, tilts its head in confusion."),
                ("12-19s", "Puppy tries to bite snowflakes, tumbles over, rolls and wiggles happily."),
                ("19-25s", "Close-up of snowy face, tiny sneeze, tail wagging non-stop.")],
         audio="Soft playful piano, crunching snow, tiny puppy sneeze.",
         cap="Tag someone who needs this tiny snow monster today."),
    dict(t="K9 Hero in Action", mood="Action / Police",
         p="A trained police German Shepherd in a K9 vest sprints through a rainy city alley at night, "
           "blue and red lights reflecting on wet pavement.",
         shots=[("0-4s", "Handler unclips the leash, close-up of the dog's focused eyes."),
                ("4-11s", "Tracking shot: dog sprints through puddles, water splashing in slow motion."),
                ("11-18s", "Dog leaps over a low wall, lands perfectly, keeps running."),
                ("18-25s", "Dog sits proudly beside its handler, receives a head pat, lights glowing behind.")],
         audio="Intense cinematic drums, rain, sirens fading out at the end.",
         cap="Not all heroes wear capes. Some wear K9 vests."),
    dict(t="Best Friend Waiting", mood="Emotional",
         p="A loyal German Shepherd lies by the front door of a cozy home, waiting for its owner to come home.",
         shots=[("0-6s", "Dog lying by the door, head on paws, eyes looking up at the handle."),
                ("6-12s", "Clock on the wall ticks, warm sunset light moves across the floor."),
                ("12-18s", "Ears perk up at the sound of keys, dog jumps up, tail wagging."),
                ("18-25s", "Door opens, owner kneels, dog leaps into a big hug and licks their face.")],
         audio="Gentle emotional acoustic guitar, jingling keys, happy whines.",
         cap="Their whole day is waiting for you. Hug your dog tonight."),
    dict(t="Beach Run Freedom", mood="Joyful / Lifestyle",
         p="A German Shepherd runs freely along a golden beach at sunset, waves crashing beside it.",
         shots=[("0-6s", "Side tracking shot at paw level, sand kicking up in slow motion."),
                ("6-13s", "Dog dives into a small wave, emerges shaking water off in a spray of droplets."),
                ("13-19s", "Dog chases a ball thrown by its owner, catches it mid-air."),
                ("19-25s", "Silhouette of dog and owner walking together against an orange sky.")],
         audio="Uplifting indie-pop beat, ocean waves, happy panting.",
         cap="Sunsets are better with your best friend."),
    dict(t="Smart Dog Training", mood="Smart / Educational",
         p="A young German Shepherd performs obedience commands in a sunny park with its trainer.",
         shots=[("0-5s", "Trainer raises a hand, dog instantly sits, close-up of attentive face."),
                ("5-11s", "Down, stay, then roll over, each command executed cleanly."),
                ("11-18s", "Dog weaves through agility poles at high speed."),
                ("18-25s", "Dog gives a high-five paw and gets a treat, looks into the camera proudly.")],
         audio="Upbeat motivational track, clicker sounds, trainer's quiet commands.",
         cap="One of the smartest breeds on Earth. Agree?"),
    dict(t="Protector of the Baby", mood="Heartwarming / Family",
         p="A gentle German Shepherd lies next to a sleeping baby on a soft blanket in a sunlit nursery.",
         shots=[("0-6s", "Wide shot: baby asleep, dog lying close, watching quietly."),
                ("6-12s", "Close-up: dog gently rests its chin beside the baby's tiny hand."),
                ("12-19s", "Baby stirs, dog softly nudges the blanket closer with its nose."),
                ("19-25s", "Dog's eyes slowly close as it falls asleep beside the baby.")],
         audio="Soft lullaby music box, calm breathing.",
         cap="The gentlest guardian you will ever meet."),
    dict(t="Forest Wolf Vibes", mood="Mysterious / Wild",
         p="A sable German Shepherd walks through a dark, foggy pine forest, looking wolf-like and majestic.",
         shots=[("0-6s", "Fog rolls between trees, only glowing eyes visible in the shadows."),
                ("6-12s", "Dog steps into a beam of light, revealing its sable coat."),
                ("12-19s", "Slow-motion walk over mossy rocks, paws close-up."),
                ("19-25s", "Dog lifts its head and howls, the howl echoing through the forest.")],
         audio="Dark ambient score, cracking twigs, echoing howl.",
         cap="Part dog. Part wolf. Full legend."),
    dict(t="Then vs Now Glow-Up", mood="Trending / Transformation",
         p="Transformation of a German Shepherd from a tiny clumsy puppy to a strong majestic adult, same backyard.",
         shots=[("0-6s", "Tiny puppy with floppy ears trips over its own paws on the grass."),
                ("6-12s", "Smooth morph transition: the puppy grows into a lanky teenager, one ear up."),
                ("12-19s", "Another morph into a full-grown adult, both ears standing tall."),
                ("19-25s", "Adult dog runs toward the camera in slow motion, heroic low angle.")],
         audio="Trending beat drop at each transformation.",
         cap="From floppy ears to fearless. The glow-up is real."),
    dict(t="Farm Herding Day", mood="Working Dog",
         p="A German Shepherd herds a flock of sheep across a green countryside field under a blue sky.",
         shots=[("0-6s", "Aerial shot of the sheep flock with the dog circling around them."),
                ("6-13s", "Ground-level shot: dog crouches low, eyes locked on the flock."),
                ("13-19s", "Dog darts left to guide a stray sheep back to the group."),
                ("19-25s", "Farmer whistles, dog runs back and sits proudly at the gate.")],
         audio="Folk-style acoustic music, sheep bleating, farmer's whistle.",
         cap="The original job of a German Shepherd: guardian of the flock."),
    dict(t="Rainy Day Cuddles", mood="Cozy / Relaxing",
         p="A German Shepherd curled up on a sofa beside a window on a rainy evening, warm lamp light inside.",
         shots=[("0-6s", "Raindrops sliding down the window, dog's reflection in the glass."),
                ("6-12s", "Dog yawns widely, stretches, and rests its head on a cushion."),
                ("12-19s", "Owner sits down with a blanket, dog scoots closer and lays its head on their lap."),
                ("19-25s", "Close-up of a slow tail thump, eyes closing peacefully.")],
         audio="Lo-fi chill beat, rain on glass, soft sigh.",
         cap="Rainy days were made for this."),
    dict(t="Mountain Adventure", mood="Adventure / Travel",
         p="A German Shepherd with a small hiking backpack summits a rocky mountain trail with its owner.",
         shots=[("0-6s", "Dog leads the way up a steep trail, backpack bouncing."),
                ("6-12s", "Dog jumps across a small mountain stream."),
                ("12-19s", "They reach the summit, dog stands on a rock overlooking clouds."),
                ("19-25s", "Drone pulls back revealing massive mountains around them.")],
         audio="Inspiring adventure anthem, wind at the summit.",
         cap="Every adventure needs a loyal co-pilot."),
    dict(t="Funny Bath Time", mood="Funny / Viral",
         p="A dramatic German Shepherd getting a bath, making hilarious offended faces, covered in soap foam.",
         shots=[("0-5s", "Dog hides behind a door when it hears the bathtub running."),
                ("5-11s", "In the tub, foam on its head like a hat, giving a betrayed side-eye."),
                ("11-18s", "Dog shakes violently, soaking the owner in slow motion."),
                ("18-25s", "Fluffy dog wrapped in a towel, still sulking, then sneaks a happy tail wag.")],
         audio="Comedic cartoon music, dramatic whining 'awoo', splash sounds.",
         cap="The drama queen of the dog world. Do yours do this too?"),
    dict(t="Christmas Morning", mood="Festive / Seasonal",
         p="A German Shepherd in a red scarf beside a glowing Christmas tree, unwrapping a present with its paws.",
         shots=[("0-6s", "Warm fireplace glow, twinkling tree lights, dog walks in wearing a scarf."),
                ("6-13s", "Dog sniffs a wrapped gift, then tears the paper with its teeth."),
                ("13-19s", "Pulls out a squeaky toy, squeaks it excitedly."),
                ("19-25s", "Dog lies by the fire with its new toy, snow falling outside the window.")],
         audio="Cheerful jingle bells instrumental, paper tearing, squeaks.",
         cap="Merry Christmas from the German Shepherd Nation family!"),
    dict(t="Senior Dog Tribute", mood="Emotional / Tribute",
         p="An old grey-muzzled German Shepherd walking slowly in a golden autumn park beside its elderly owner.",
         shots=[("0-6s", "Falling autumn leaves, close-up of a grey muzzle and wise eyes."),
                ("6-12s", "Flashback-style warm glow: a memory of the same dog as an energetic puppy."),
                ("12-19s", "Back to present: owner and dog sit together on a park bench."),
                ("19-25s", "Owner kisses the dog's head, both watch the sunset together.")],
         audio="Touching piano melody, rustling leaves.",
         cap="Grey muzzles, golden hearts. Share a photo of your senior dog."),
]

SECTION = [
    ("Hook first", "The first 3 seconds decide whether people keep watching - always open with motion, eyes or a surprise."),
    ("Copy the full prompt", "Paste the combined prompt (Main + Shots + Style) into your AI video tool: Veo, Sora, Kling, Runway, Hailuo or Pika."),
    ("Tools with short clips", "If your tool only makes 5-10s clips, generate each shot as its own clip and join them in CapCut for a 25s Reel."),
    ("Consistent dog", "Keep the same description (e.g. 'black-and-tan German Shepherd with amber eyes') in every shot so the dog looks the same."),
    ("Post smart", "Add the caption + hashtags, post as a Reel at 9:16, and reply to comments in the first hour."),
]

HASHTAGS = "#GermanShepherdNation #GermanShepherd #GSD #GermanShepherdDog #DogLovers #DogsOfFacebook #K9 #PuppyLove #Reels #ViralDog"

ss = dict(
    cover_title=ParagraphStyle("ct", fontName="Helvetica-Bold", fontSize=30, leading=36, textColor=CREAM, alignment=1),
    cover_sub=ParagraphStyle("cs", fontName="Helvetica", fontSize=14, leading=20, textColor=TAN, alignment=1),
    h1=ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=BLACK, spaceAfter=6),
    h2=ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=colors.white),
    mood=ParagraphStyle("mood", fontName="Helvetica-Oblique", fontSize=10, leading=13, textColor=CREAM, alignment=2),
    label=ParagraphStyle("lb", fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=TAN, spaceBefore=5),
    body=ParagraphStyle("bd", fontName="Helvetica", fontSize=9.8, leading=13.5, textColor=BLACK),
    small=ParagraphStyle("sm", fontName="Helvetica", fontSize=9, leading=12, textColor=GREY),
    cell=ParagraphStyle("cl", fontName="Helvetica", fontSize=9.3, leading=12.5, textColor=BLACK),
    cellb=ParagraphStyle("cb", fontName="Helvetica-Bold", fontSize=9.3, leading=12.5, textColor=BLACK),
)


def cover(c, doc):
    w, h = A4
    c.saveState()
    c.setFillColor(BLACK)
    c.rect(0, 0, w, h, fill=1, stroke=0)
    c.setFillColor(TAN)
    c.rect(0, h * 0.30, w, 4, fill=1, stroke=0)
    c.rect(0, h * 0.70, w, 4, fill=1, stroke=0)
    c.restoreState()


def page(c, doc):
    w, h = A4
    c.saveState()
    c.setFillColor(BLACK)
    c.rect(0, h - 14 * mm, w, 14 * mm, fill=1, stroke=0)
    c.setFillColor(CREAM)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(18 * mm, h - 9 * mm, PAGE.upper())
    c.setFillColor(TAN)
    c.setFont("Helvetica", 9)
    c.drawRightString(w - 18 * mm, h - 9 * mm, "25-Second AI Video Prompts")
    c.setFillColor(GREY)
    c.drawCentredString(w / 2, 10 * mm, f"Page {doc.page}")
    c.restoreState()


def prompt_block(i, d, width):
    head = Table([[Paragraph(f"#{i:02d}  {d['t']}", ss["h2"]), Paragraph(d["mood"], ss["mood"])]],
                 colWidths=[width * 0.62, width * 0.38])
    head.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLACK),
        ("LINEBELOW", (0, 0), (-1, -1), 3, TAN),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    rows = [[Paragraph(tm, ss["cellb"]), Paragraph(txt, ss["cell"])] for tm, txt in d["shots"]]
    shots = Table(rows, colWidths=[16 * mm, width - 16 * mm])
    shots.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [CREAM, colors.white]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#e2d4bf")),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return KeepTogether([
        head, Spacer(1, 4),
        Paragraph("MAIN PROMPT", ss["label"]),
        Paragraph(d["p"], ss["body"]),
        Paragraph("SHOT-BY-SHOT (25 SECONDS)", ss["label"]),
        shots,
        Paragraph("STYLE", ss["label"]),
        Paragraph(STYLE, ss["body"]),
        Paragraph("MUSIC / SOUND", ss["label"]),
        Paragraph(d["audio"], ss["body"]),
        Paragraph("FACEBOOK CAPTION", ss["label"]),
        Paragraph(f"{d['cap']}<br/><font color='#555555'>{HASHTAGS}</font>", ss["body"]),
        Spacer(1, 14),
    ])


doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                        topMargin=22 * mm, bottomMargin=18 * mm,
                        title=f"{PAGE} - 25-Second AI Video Prompts", author=PAGE)
W = doc.width

story = [Spacer(1, 95 * mm),
         Paragraph(PAGE.upper(), ss["cover_title"]), Spacer(1, 10),
         Paragraph("15 Ready-to-Use AI Video Prompts", ss["cover_sub"]),
         Paragraph("Each one built for a 25-second Facebook Reel", ss["cover_sub"]),
         Spacer(1, 30),
         Paragraph("Main prompt  -  Shot-by-shot timing  -  Music  -  Caption + Hashtags",
                   ParagraphStyle("x", parent=ss["small"], textColor=CREAM, alignment=1)),
         PageBreak()]

story.append(Paragraph("How to use this pack", ss["h1"]))
tips = Table([[Paragraph(f"<b>{a}</b>", ss["cell"]), Paragraph(b, ss["cell"])] for a, b in SECTION],
             colWidths=[42 * mm, W - 42 * mm])
tips.setStyle(TableStyle([
    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [CREAM, colors.white]),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
story += [tips, Spacer(1, 14), Paragraph("Prompt list", ss["h1"])]
idx = Table([[f"#{i:02d}", d["t"], d["mood"]] for i, d in enumerate(PROMPTS, 1)],
            colWidths=[14 * mm, 80 * mm, W - 94 * mm])
idx.setStyle(TableStyle([
    ("FONT", (0, 0), (-1, -1), "Helvetica", 9.5),
    ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 9.5),
    ("TEXTCOLOR", (0, 0), (0, -1), TAN),
    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, CREAM]),
    ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))
story += [idx, PageBreak()]

for i, d in enumerate(PROMPTS, 1):
    story.append(prompt_block(i, d, W))

doc.build(story, onFirstPage=cover, onLaterPages=page)
print("wrote", OUT)
