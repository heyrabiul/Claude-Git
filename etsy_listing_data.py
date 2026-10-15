"""Etsy-specific data for the 50 niche books: five niche tags (max 20
characters each, Etsy's limit) and an optional holiday / occasion."""

GENERIC_TAGS = [
    "dot to dot adults",
    "extreme dot to dot",
    "connect the dots",
    "printable puzzles",
    "adult activity book",
    "dot to dot pdf",
    "hard puzzles adults",
    "brain games adults",
]

# slug: ([5 niche tags], holiday attribute or "")
ETSY = {
    "ocean": (["ocean activity", "sea life gift", "whale printable", "marine animals", "ocean lover gift"], ""),
    "cats": (["cat lover gift", "cat activity book", "cat printable", "cat mom gift", "kitten puzzles"], ""),
    "dogs": (["dog lover gift", "dog activity book", "dog printable", "dog mom gift", "puppy puzzles"], ""),
    "birds": (["bird lover gift", "bird watcher gift", "bird printable", "owl puzzles", "birding activity"], ""),
    "bugs": (["butterfly printable", "insect activity", "bee lover gift", "bug puzzles", "garden bug gift"], ""),
    "garden": (["flower printable", "garden lover gift", "flower puzzles", "botanical activity", "gardener gift"], ""),
    "farm": (["farm animals", "farm printable", "country life gift", "barnyard puzzles", "farmhouse activity"], ""),
    "space": (["space printable", "astronomy gift", "planets puzzles", "rocket activity", "astronaut gift"], ""),
    "halloween": (["halloween printable", "halloween activity", "spooky puzzles", "halloween party", "pumpkin witch"], "Halloween"),
    "desserts": (["dessert printable", "cupcake puzzles", "baker gift", "sweet treats", "candy activity"], ""),
    "safari": (["safari animals", "safari printable", "lion elephant", "wildlife puzzles", "african animals"], ""),
    "dinosaurs": (["dinosaur printable", "dinosaur gift", "t rex puzzles", "dino activity", "prehistoric"], ""),
    "easter": (["easter printable", "easter activity", "easter basket", "bunny puzzles", "easter gift adult"], "Easter"),
    "valentine": (["valentine printable", "valentines activity", "valentine gift", "love puzzles", "heart printable"], "Valentine's Day"),
    "stpatrick": (["st patricks day", "irish printable", "shamrock puzzles", "leprechaun", "st paddys activity"], "St. Patrick's Day"),
    "patriotic": (["4th of july", "patriotic printable", "july 4th activity", "usa puzzles", "independence day"], "Independence Day"),
    "beach": (["beach printable", "summer activity", "vacation puzzles", "beach lover gift", "travel activity"], ""),
    "winter": (["winter printable", "winter activity", "snowman puzzles", "cozy winter gift", "snow day activity"], ""),
    "autumn": (["fall printable", "autumn activity", "fall puzzles", "fall leaves", "cozy fall gift"], ""),
    "spring": (["spring printable", "spring activity", "flower puzzles", "springtime gift", "spring birds"], ""),
    "faith": (["christian printable", "bible activity", "christian gift", "church activity", "bible puzzles"], ""),
    "vehicles": (["car printable", "car lover gift", "truck puzzles", "classic cars", "vehicle activity"], ""),
    "trains": (["train printable", "train lover gift", "railroad puzzles", "steam engine", "train activity"], ""),
    "aviation": (["airplane printable", "pilot gift", "aviation puzzles", "airplane activity", "aircraft lover"], ""),
    "ships": (["boat printable", "nautical gift", "sailing puzzles", "ship activity", "boat lover gift"], ""),
    "landmarks": (["travel printable", "world landmarks", "travel lover gift", "eiffel tower", "travel puzzles"], ""),
    "castles": (["castle printable", "medieval activity", "knight puzzles", "history gift", "castles knights"], ""),
    "pirates": (["pirate printable", "pirate party", "pirate puzzles", "treasure map", "pirate gift"], ""),
    "mermaids": (["mermaid printable", "mermaid gift", "fairy tale puzzles", "fantasy activity", "mermaid lover"], ""),
    "unicorns": (["unicorn printable", "unicorn gift", "unicorn puzzles", "magical activity", "rainbow unicorn"], ""),
    "dragons": (["dragon printable", "dragon lover gift", "fantasy puzzles", "mythical creatures", "dragon activity"], ""),
    "coffee": (["coffee printable", "coffee lover gift", "tea lover gift", "cafe activity", "coffee puzzles"], ""),
    "fruits": (["fruit printable", "vegetable puzzles", "foodie gift", "kitchen activity", "fruit lover"], ""),
    "kitchen": (["cooking printable", "chef gift", "kitchen puzzles", "foodie activity", "baking lover gift"], ""),
    "music": (["music printable", "music lover gift", "musician gift", "instrument puzzles", "music teacher gift"], ""),
    "sports": (["sports printable", "sports lover gift", "football puzzles", "sports activity", "coach gift"], ""),
    "fishing": (["fishing printable", "fishing gift", "fisherman gift", "fishing puzzles", "lake activity"], ""),
    "camping": (["camping printable", "camping activity", "hiking gift", "outdoors puzzles", "camper gift"], ""),
    "houseplants": (["plant printable", "plant lover gift", "succulent puzzles", "plant mom gift", "cactus activity"], ""),
    "zen": (["mandala printable", "mindfulness gift", "relaxing activity", "zen puzzles", "stress relief"], ""),
    "wildwest": (["western printable", "cowboy gift", "wild west puzzles", "cowboy activity", "western lover"], ""),
    "horses": (["horse printable", "horse lover gift", "equestrian gift", "horse puzzles", "horse activity"], ""),
    "polar": (["polar bear", "penguin printable", "arctic animals", "winter animals", "animal puzzles"], ""),
    "jungle": (["jungle printable", "rainforest animals", "jungle puzzles", "wildlife gift", "jungle activity"], ""),
    "woodland": (["woodland animals", "forest printable", "nature lover gift", "woodland puzzles", "forest activity"], ""),
    "pets": (["hamster printable", "small pets", "bunny puzzles", "pet lover gift", "guinea pig gift"], ""),
    "lunar": (["lunar new year", "chinese new year", "zodiac printable", "lantern puzzles", "new year activity"], "Lunar New Year"),
    "kawaii": (["kawaii printable", "cute puzzles", "kawaii gift", "cute activity", "kawaii lover"], ""),
    "coastal": (["lighthouse gift", "coastal printable", "nautical puzzles", "seaside activity", "lighthouse lover"], ""),
    "vintage": (["vintage printable", "retro gift", "nostalgia puzzles", "antique lover", "vintage activity"], ""),
}

for _slug, (_tags, _) in ETSY.items():
    for _t in _tags + GENERIC_TAGS:
        assert len(_t) <= 20, (_slug, _t)
    assert len(set(_tags + GENERIC_TAGS)) == 13, _slug
