"""Niche books: one 50-puzzle book per hot niche.

Each niche lists the book title and any existing designs it reuses; the
niche's own pictures live in a module named after it (``ocean.py`` ...)
and register with ``theme = slug``.  Niche themes never appear in the
general books.
"""
import importlib
import pkgutil

from .. import designs

# slug: title (book: "<title> Extreme Dot-to-Dot for Adults").  "reuse" is
# kept for reference only: niche books no longer borrow other books' art.
NICHES = {
    "ocean": {"title": "Ocean Life", "reuse": ["fish", "turtle", "whale", "nautilus"]},
    "cats": {"title": "Cats", "reuse": ["cat"]},
    "dogs": {"title": "Dogs", "reuse": []},
    "birds": {"title": "Birds", "reuse": ["bird", "owl"]},
    "bugs": {"title": "Butterflies & Bugs", "reuse": ["butterfly", "bee", "ladybug", "snail"]},
    "garden": {"title": "Flowers & Garden", "reuse": ["flower", "sunflower"]},
    "farm": {"title": "Farm Life", "reuse": []},
    "space": {"title": "Outer Space", "reuse": ["rocket"]},
    "halloween": {"title": "Halloween", "reuse": []},
    "desserts": {"title": "Sweets & Desserts", "reuse": ["cupcake", "icecream"]},
    "safari": {"title": "Safari Animals", "reuse": []},
    "dinosaurs": {"title": "Dinosaurs", "reuse": []},
    "easter": {"title": "Easter", "reuse": []},
    "valentine": {"title": "Valentine's Day", "reuse": []},
    "stpatrick": {"title": "St. Patrick's Day", "reuse": []},
    "patriotic": {"title": "Fourth of July", "reuse": []},
    "beach": {"title": "Summer Beach", "reuse": []},
    "winter": {"title": "Winter Wonderland", "reuse": []},
    "autumn": {"title": "Autumn", "reuse": []},
    "spring": {"title": "Spring", "reuse": []},
    "faith": {"title": "Faith & Bible", "reuse": []},
    "vehicles": {"title": "Cars & Trucks", "reuse": []},
    "trains": {"title": "Trains", "reuse": []},
    "aviation": {"title": "Airplanes & Flight", "reuse": ["balloon"]},
    "ships": {"title": "Boats & Ships", "reuse": ["sailboat", "anchor"]},
    "landmarks": {"title": "World Landmarks", "reuse": []},
    "castles": {"title": "Castles & Knights", "reuse": ["crown"]},
    "pirates": {"title": "Pirates", "reuse": []},
    "mermaids": {"title": "Mermaids & Fairy Tales", "reuse": []},
    "unicorns": {"title": "Unicorns & Fantasy", "reuse": []},
    "dragons": {"title": "Dragons & Mythical Creatures", "reuse": []},
    "coffee": {"title": "Coffee & Tea", "reuse": ["teacup"]},
    "fruits": {"title": "Fruits & Vegetables", "reuse": ["apple", "pineapple"]},
    "kitchen": {"title": "Kitchen & Cooking", "reuse": []},
    "music": {"title": "Music", "reuse": []},
    "sports": {"title": "Sports", "reuse": []},
    "fishing": {"title": "Fishing", "reuse": []},
    "camping": {"title": "Camping & Outdoors", "reuse": []},
    "houseplants": {"title": "Houseplants & Succulents", "reuse": ["cactus"]},
    "zen": {"title": "Zen Patterns", "reuse": ["mandala", "spirograph"]},
    "wildwest": {"title": "Wild West", "reuse": []},
    "horses": {"title": "Horses", "reuse": []},
    "polar": {"title": "Arctic & Polar Animals", "reuse": []},
    "jungle": {"title": "Jungle & Rainforest", "reuse": []},
    "woodland": {"title": "Woodland Animals", "reuse": []},
    "pets": {"title": "Small Pets", "reuse": []},
    "lunar": {"title": "Lunar New Year", "reuse": []},
    "kawaii": {"title": "Kawaii Cute", "reuse": []},
    "coastal": {"title": "Coastal & Lighthouses", "reuse": ["lighthouse"]},
    "vintage": {"title": "Vintage Treasures", "reuse": ["key"]},
}

designs.SPECIAL_THEMES.update(NICHES)

# Import every niche module so its designs register.
for _m in pkgutil.iter_modules(__path__):
    if not _m.name.startswith("_"):
        importlib.import_module(f"{__name__}.{_m.name}")


def ready():
    """Niches whose art is finished: 50 different main pictures."""
    from ..compose import NICHE_BOOK_PUZZLES, niche_pool
    return [s for s in NICHES if len(niche_pool(s)) >= NICHE_BOOK_PUZZLES]


def progress():
    from ..compose import niche_pool
    return {s: len(niche_pool(s)) for s in NICHES}
