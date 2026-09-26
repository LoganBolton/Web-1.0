"""The product catalogue of Bazaar, and the sellers who list on it.

Units used in specs: power in fenwicks (fw), volume in measures (ms, a
little under a quarter litre... roughly a cup), weight in weights (wt),
length in thumbs (40 to the ell).
"""
from dataclasses import dataclass, field

from ..engine.rng import stream, slug, pick_weighted
from .calendar import ADate, TODAY
from .culture import BOOKS, ALBUMS, ARTIST
from .econ import convert, NATION_CURRENCY
from .geo import cities_of
from .names import make_name
from .people import generate_population


@dataclass
class Seller:
    id: str
    name: str
    city: str
    nation: str
    since: int
    rating: float
    ratings: int
    ships_days: tuple
    returns: str
    official: bool = False

    @property
    def currency(self):
        return NATION_CURRENCY[self.nation]


@dataclass
class Product:
    id: str
    title: str
    brand: str
    category: str
    sub: str
    kind: str  # image kind
    seller: str
    price: float  # in seller currency
    specs: list
    description: list
    rating: float
    n_reviews: int
    reviews: list = field(default_factory=list)
    stock: int = 0
    model: str = ""
    listed: ADate = None
    qa: list = field(default_factory=list)
    sponsored: bool = False
    link: str = ""  # an off-Bazaar page about this product


CATEGORIES = {
    "kitchen": ("Kitchen", ["Kettles", "Teapots", "Tea and infusions", "Preserves", "Spices"]),
    "home": ("Home and hearth", ["Lamps", "Candles", "Clocks", "Chairs", "Plants"]),
    "clothing": ("Clothing", ["Coats", "Boots", "Scarves", "Shirts"]),
    "looms": ("Looms and devices", ["Slates", "Desk looms", "Chargers and cables", "Loom accessories"]),
    "outdoors": ("Outdoors and sky", ["Telescopes", "Backpacks", "Bags"]),
    "toys": ("Toys and games", ["Board games", "Toys"]),
    "books": ("Books", ["Books"]),
    "music": ("Music", ["Records"]),
}
SUB_KIND = {"Kettles": "kettle", "Teapots": "teapot", "Tea and infusions": "tea", "Preserves": "jar",
            "Spices": "spice", "Lamps": "lamp", "Candles": "candle", "Clocks": "clock", "Chairs": "chair",
            "Plants": "plant", "Coats": "coat", "Boots": "boots", "Scarves": "scarf", "Shirts": "shirt",
            "Slates": "slate", "Desk looms": "loom", "Chargers and cables": "charger",
            "Loom accessories": "loom", "Telescopes": "telescope", "Backpacks": "backpack",
            "Bags": "bag", "Board games": "game", "Toys": "toy", "Books": "book", "Records": "record"}

BRANDS = {
    "Kettles": ["Kettlebright", "Hob & Hearth", "Sallowware", "Copper Kettle Home"],
    "Teapots": ["Emberly Glassworks", "Hob & Hearth", "Brineholt Pottery"],
    "Tea and infusions": ["Copper Kettle Home", "Marrowby Leaf", "Gorse Hollow Farms"],
    "Preserves": ["Gorse Hollow Farms", "Wendmoor Larder", "Aldermoot Vineyards"],
    "Spices": ["Marrowby Leaf", "Reach Traders", "Saltspire Salt Company"],
    "Lamps": ["Harrowdeep Lamp Company", "Kettlebright", "Fenwick & Sons", "Lumen Isles"],
    "Candles": ["Lowmarsh Chandlers", "Lumen Isles", "Wick & Tallow"],
    "Clocks": ["Quenby Clockworks", "Tallis Time", "Brass Moon"],
    "Chairs": ["Caddick Joinery", "Aldermoot Woodworks", "Tarrow Furnishers"],
    "Plants": ["Shellcombe Gardens", "Gorse Hollow Farms"],
    "Coats": ["Wendmoor Wool Co-operative", "Keelwear", "Caddick Mills"],
    "Boots": ["Coldforge Outfitters", "Keelwear", "Stonemeet Cobblers"],
    "Scarves": ["Wendmoor Wool Co-operative", "Caddick Mills"],
    "Shirts": ["Caddick Mills", "Keelwear", "Brightmarket Tailors"],
    "Slates": ["Vantle", "Loomworks"],
    "Desk looms": ["Loomworks", "Vantle", "Aske Instruments"],
    "Chargers and cables": ["Vantle", "Loomworks", "Sparkline", "Voltwright"],
    "Loom accessories": ["Vantle", "Sparkline", "Loomworks", "Pithcase"],
    "Telescopes": ["Ossa Optics", "Aske Instruments", "Starwright"],
    "Backpacks": ["Coldforge Outfitters", "Keelwear", "Reach Traders"],
    "Bags": ["Keelwear", "Brightmarket Tailors"],
    "Board games": ["Undertow Games", "Tabletop Tarrow", "Moot Games"],
    "Toys": ["Tabletop Tarrow", "Skylark Toys", "Moot Games"],
}
ITEM_WORDS = {
    "Kettles": (["Kettle", "Stovetop Kettle", "Whistling Kettle", "Voltaic Kettle"], ["K", "VK", "HK"]),
    "Teapots": (["Teapot", "Tea Set", "Brewing Pot"], ["TP", "BP"]),
    "Tea and infusions": (["Black Tea", "Moor Heather Infusion", "Pearl Leaf Green Tea", "Smoked Harbour Blend",
                           "Hollowday Spice Tea"], ["T", "TB"]),
    "Preserves": (["Bramble Jam", "Quince Jelly", "Pickled Samphire", "Honey", "Cider Butter"], ["P"]),
    "Spices": (["Sea Salt", "Smoked Salt", "Pepperleaf", "Emberroot", "Kelp Flakes"], ["S"]),
    "Lamps": (["Desk Lamp", "Miner's Lamp", "Reading Lamp", "Storm Lantern", "Floor Lamp"], ["L", "ML", "SL"]),
    "Candles": (["Beeswax Candles", "Tallow Candles", "Lighthouse Candle", "Scented Candle"], ["C"]),
    "Clocks": (["Mantel Clock", "Two-Moon Clock", "Wall Clock", "Pocket Watch", "Tide Clock"], ["QC", "TM"]),
    "Chairs": (["Reading Chair", "Kitchen Chair", "Rocking Chair", "Stool"], ["CH"]),
    "Plants": (["Sea-fennel", "Glass Fern", "Moor Heather", "Lamp Lily", "Pith Cactus"], ["PL"]),
    "Coats": (["Oilskin Coat", "Moor Coat", "Ferry Jacket", "Wool Greatcoat"], ["OC", "MC"]),
    "Boots": (["Mining Boots", "Deck Boots", "Walking Boots", "Canal Boots"], ["B", "DB"]),
    "Scarves": (["Wool Scarf", "Tartan Scarf", "Lamplighter Scarf"], ["SC"]),
    "Shirts": (["Linen Shirt", "Work Shirt", "Collarless Shirt"], ["SH"]),
    "Slates": (["Slate", "Slate Mini", "Slate Pro"], ["SL"]),
    "Desk looms": (["Desk Loom", "Home Loom", "Study Loom"], ["DL", "HL"]),
    "Chargers and cables": (["Charger", "Voltaic Cable", "Fast Charger", "Travel Charger"], ["VC", "CB"]),
    "Loom accessories": (["Slate Case", "Glass Guard", "Stylus", "Punch-ribbon Reader"], ["AC", "GG"]),
    "Telescopes": (["Refractor Telescope", "Pocket Spyglass", "Moon Watcher", "Star Finder"], ["OT", "PW"]),
    "Backpacks": (["Trail Pack", "Day Pack", "Ferry Pack"], ["TP", "DP"]),
    "Bags": (["Satchel", "Market Bag", "Loom Bag"], ["BG"]),
    "Board games": (["Board Game", "Card Game", "Puzzle"], ["BG"]),
    "Toys": (["Toy Airship", "Clockwork Gull", "Wooden Tram", "Kite"], ["TY"]),
}
PRICE = {"Kettles": (25, 140), "Teapots": (18, 90), "Tea and infusions": (4, 22), "Preserves": (3, 14),
         "Spices": (2, 16), "Lamps": (20, 260), "Candles": (3, 30), "Clocks": (30, 900), "Chairs": (40, 420),
         "Plants": (6, 45), "Coats": (60, 380), "Boots": (45, 260), "Scarves": (12, 70), "Shirts": (15, 80),
         "Slates": (499, 1600), "Desk looms": (700, 3200), "Chargers and cables": (9, 60),
         "Loom accessories": (6, 90), "Telescopes": (90, 2400), "Backpacks": (30, 190), "Bags": (20, 150),
         "Board games": (15, 80), "Toys": (5, 60)}

REVIEW_GOOD = ["Does exactly what it says.", "Arrived two days early, well packed.", "Better than the "
               "one my mother had.", "Solid and well made. Would buy again.", "My whole family loves it.",
               "Worth every pennet.", "Bought as a Hollowdays gift. Big hit.", "Five stars, no notes.",
               "Sturdier than it looks in the picture.", "Lovely colour, true to the image."]
REVIEW_MID = ["Fine, but smaller than I expected.", "Took three weeks to arrive from Saltmarch.",
              "Does the job. Instructions only in Pellish.", "The colour is darker than in the picture.",
              "Good value but the box was crushed."]
REVIEW_BAD = ["Broke after a week.", "Not as described. Returned it.", "Seller never answered my "
              "messages.", "Smells of fish. Why does it smell of fish?", "Arrived in pieces."]


def _sellers(rng, pop):
    shops = ["Emporium", "Traders", "Goods", "Supply", "Warehouse", "& Daughters", "& Sons", "Market",
             "Stores", "Outfitters", "Direct", "Wholesale"]
    out = [
        Seller("vantle-store", "Vantle Store", "Ostmere", "VEY", 399, 4.8, 21_430, (1, 3),
               "30 days, free", True),
        Seller("bazaar-basics", "Bazaar Basics", "Caddick Ford", "VEY", 396, 4.5, 88_104, (1, 2),
               "30 days, free", True),
        Seller("quillmere-books", "Quillmere Press", "Ostmere", "VEY", 402, 4.9, 6_311, (2, 4),
               "14 days", True),
        Seller("bellows-shop", "Bellows Records Shop", "Brineholt", "SLT", 403, 4.7, 1_904, (3, 6),
               "14 days", True),
        Seller("ossa-optics", "Ossa Optics", "Lanternport", "PEL", 400, 4.8, 3_022, (4, 9),
               "60 days", True),
    ]
    used = {s.name for s in out}
    for i in range(70):
        nat = pick_weighted(rng, [("VEY", 45), ("SLT", 25), ("KHR", 12), ("PEL", 12), ("ODD", 1)])
        city = rng.choice(cities_of(nat))
        owner = make_name(rng, nat)
        style = rng.randrange(3)
        if style == 0:
            nm = f"{owner.family} {rng.choice(shops)}"
        elif style == 1:
            nm = f"{city.name} {rng.choice(shops)}"
        else:
            nm = f"{rng.choice(['Tide', 'Lamp', 'Kiln', 'Ford', 'Gull', 'Anvil', 'Pearl', 'Moor', 'Rope'])}"\
                 f"{rng.choice(['way', 'side', 'mark', 'wright', 'hall'])} {rng.choice(shops)}"
        if nm in used:
            nm += f" {city.name}"
        used.add(nm)
        lo = 2 if nat in ("VEY",) else 4
        out.append(Seller(slug(nm), nm, city.name, nat, rng.randint(396, 411),
                          round(rng.uniform(2.9, 4.95), 1), rng.randint(3, 9000),
                          (lo, lo + rng.randint(2, 12)), rng.choice(["14 days", "30 days", "No returns",
                                                                      "7 days, buyer pays postage"])))
    return out


def _review(rng, pop, rating, when):
    p = rng.choice(pop)
    stars = max(1, min(5, int(round(rng.gauss(rating, 1.0)))))
    txt = rng.choice(REVIEW_GOOD if stars >= 4 else REVIEW_MID if stars == 3 else REVIEW_BAD)
    return {"who": p.handle, "city": p.city, "stars": stars, "text": txt,
            "date": (when + rng.randint(3, 300)).long(), "helpful": rng.randint(0, 60)}


def _build():
    rng = stream("products")
    pop = generate_population()
    sellers = _sellers(rng, pop)
    third_party = [s for s in sellers if not s.official]
    products = []
    n = 0

    def pid():
        nonlocal n
        n += 1
        return f"BZ{100000 + n * 37:07d}"

    # --- hand-placed items --------------------------------------------------
    special = [
        ("Vantle Slate 7 (64 weaves, Tide Blue)", "Vantle", "looms", "Slates", "vantle-store", 1299.0,
         "SL-7-64", [("Memory", "64 weaves"), ("Faces", "two glass faces, front and back"),
                     ("Charger in box", "VC-7B (VC-7A before 16 Gale 412)"), ("Weight", "0.42 wt"),
                     ("Released", "1 Gale 412")],
         ["The Slate we always meant to make.", "Two glass faces: write on the back while you read on the front."],
         ADate(412, 8, 1)),
        ("Vantle Slate 7 (128 weaves, Ember Red)", "Vantle", "looms", "Slates", "vantle-store", 1549.0,
         "SL-7-128", [("Memory", "128 weaves"), ("Faces", "two glass faces, front and back"),
                      ("Charger in box", "VC-7B (VC-7A before 16 Gale 412)"), ("Weight", "0.42 wt"),
                      ("Released", "1 Gale 412")],
         ["For those who keep everything.", "Two glass faces."], ADate(412, 8, 1)),
        ("Vantle VC-7B Replacement Charger", "Vantle", "looms", "Chargers and cables", "vantle-store", 0.0,
         "VC-7B", [("Output", "18 fenwicks"), ("For", "Slate 7"), ("Note", "Free to owners of a recalled VC-7A")],
         ["Replacement for the recalled VC-7A charger. Free of charge. Order with your Slate's serial number."],
         ADate(412, 8, 14)),
        ("Vantle Slate 6 (64 weaves)", "Vantle", "looms", "Slates", "vantle-store", 899.0, "SL-6-64",
         [("Memory", "64 weaves"), ("Faces", "one glass face"), ("Charger in box", "VC-6"),
          ("Released", "3 Loam 411")], ["Last year's Slate, now for less."], ADate(411, 3, 3)),
        ("Ossa Optics Pith Watcher 90 Refractor", "Ossa Optics", "outdoors", "Telescopes", "ossa-optics",
         410.0, "PW-90", [("Aperture", "90 thumbs"), ("Focal length", "36 thumbs"), ("Mount", "alt-azimuth"),
                          ("Includes", "Ossa filter, two eyepieces")],
         ["Made for the 3 Mire crossing. Comes with the Ossa filter the Observatory recommends."],
         ADate(412, 7, 20)),
        ("Kettlebright K-40 Voltaic Kettle", "Kettlebright", "kitchen", "Kettles", "bazaar-basics", 64.0,
         "K-40", [("Capacity", "7 measures"), ("Power", "2,200 fenwicks"), ("Boil time", "about 3 minutes"),
                  ("Colours", "copper, cream, moor green")],
         ["The kettle in every Copper Kettle tea room.", "Switches itself off at the boil."], ADate(409, 2, 2)),
        ("Fathom: The Board Game", "Undertow Games", "toys", "Board games", "bazaar-basics", 45.0, "UG-FB1",
         [("Players", "2 to 5"), ("Playing time", "about 90 minutes"), ("Ages", "10 and up")],
         ["Dive the trenches of the loom game, now on your table."], ADate(408, 9, 9)),
        ("Harrowdeep Miner's Lamp, Model 9", "Harrowdeep Lamp Company", "home", "Lamps", "bazaar-basics",
         120.0, "ML-9", [("Burn time", "40 hours"), ("Light", "600 candles"), ("Weight", "2.1 wt")],
         ["The same lamp carried in the Deepshaft workings. Nine centuries of lamp-making."], ADate(405, 5, 5)),
    ]
    for title, brand, cat, sub, seller, price, model, specs, desc, listed in special:
        r = stream("prod-special", title)
        p = Product(pid(), title, brand, cat, sub, SUB_KIND[sub], seller, price, specs, desc,
                    round(r.uniform(4.2, 4.9), 1), r.randint(40, 900), stock=r.randint(0, 400), model=model,
                    listed=listed)
        products.append(p)
    # third-party Slate 7s at a markup
    for s in rng.sample([s for s in third_party if s.nation in ("SLT", "KHR", "PEL")], 3):
        price = convert(1299 * rng.uniform(1.08, 1.3), "VCR", s.currency)
        products.append(Product(pid(), "Slate 7 64 weaves NEW SEALED (import)", "Vantle", "looms", "Slates",
                                "slate", s.id, round(price, 2),
                                [("Memory", "64 weaves"), ("Charger in box", "VC-7A")],
                                ["Brand new sealed. Ships from our warehouse. May include earlier charger."],
                                round(rng.uniform(3.1, 4.2), 1), rng.randint(2, 40), stock=rng.randint(1, 9),
                                model="SL-7-64", listed=ADate(412, 8, rng.randint(2, 12))))
    # --- generated goods ----------------------------------------------------------
    for cat, (cname, subs) in CATEGORIES.items():
        if cat in ("books", "music"):
            continue
        for sub in subs:
            words, prefixes = ITEM_WORDS[sub]
            for i in range(rng.randint(40, 75)):
                brand = rng.choice(BRANDS[sub])
                item = rng.choice(words)
                model = f"{rng.choice(prefixes)}-{rng.randint(10, 990)}"
                adj = rng.choice(["", "", "Classic ", "Deluxe ", "Compact ", "Heritage ", "Everyday ",
                                  "Reach ", "Hollowday ", "Northmole "])
                title = f"{brand} {adj}{item} {model}".replace("  ", " ")
                seller = rng.choice(third_party) if rng.random() < 0.7 else sellers[1]
                lo, hi = PRICE[sub]
                price_cr = round(lo * (hi / lo) ** rng.random(), 2)
                price = convert(price_cr, "VCR", seller.currency)
                specs = _specs(rng, sub)
                desc = [f"{adj}{item} from {brand}.",
                        rng.choice(["Made in the Holds.", "Made in Caddick Ford.", "Imported from the Isles.",
                                    "Hand-finished in Saltmarch.", "Made to last a lifetime.",
                                    "As used in the Copper Kettle tea rooms.",
                                    "Tested in Frostgate winters."])]
                listed = ADate(rng.randint(403, 412), rng.randint(1, 10), rng.randint(1, 36))
                if listed > TODAY:
                    listed = TODAY - rng.randint(5, 100)
                p = Product(pid(), title, brand, cat, sub, SUB_KIND[sub], seller.id, round(price, 2), specs,
                            desc, round(min(5, max(1.2, rng.gauss(4.0, 0.6))), 1), rng.randint(0, 1500),
                            stock=rng.choice([0] + [rng.randint(1, 500)] * 6), model=model, listed=listed,
                            sponsored=rng.random() < 0.05)
                products.append(p)
    # books and records
    qs = next(s for s in sellers if s.id == "quillmere-books")
    for b in BOOKS:
        price = round(b.price_cr * rng.uniform(0.85, 1.05), 2)
        products.append(Product(pid(), f"{b.title} by {b.author}", b.publisher, "books", "Books", "book",
                                qs.id if rng.random() < 0.6 else rng.choice(third_party).id, price,
                                [("Author", b.author), ("Publisher", b.publisher), ("Year", f"{b.year} CR"),
                                 ("Pages", str(b.pages)), ("QN", b.qn)], [b.blurb],
                                round(rng.uniform(3.4, 4.9), 1), rng.randint(0, 800), stock=rng.randint(0, 80),
                                model=b.qn, listed=ADate(max(396, min(b.year, 411)), 1, 1), link=b.id))
    bs = next(s for s in sellers if s.id == "bellows-shop")
    for al in ALBUMS:
        if al.release > TODAY:
            continue
        products.append(Product(pid(), f"{al.title} ({ARTIST[al.artist].name}), wax disc", "Bellows Records",
                                "music", "Records", "record", bs.id, round(rng.uniform(14, 26), 2),
                                [("Artist", ARTIST[al.artist].name), ("Released", al.release.long()),
                                 ("Catalogue", al.catalog), ("Tracks", str(len(al.tracks)))],
                                [f"{len(al.tracks)} tracks."], round(rng.uniform(4.0, 4.9), 1),
                                rng.randint(5, 700), stock=rng.randint(0, 200), model=al.catalog,
                                listed=al.release, link=al.id))
    # reviews and Q&A
    for p in products:
        r = stream("reviews", p.id)
        p.reviews = [_review(r, pop, p.rating, p.listed) for _ in range(min(p.n_reviews, r.randint(2, 14)))]
        if p.sub == "Slates" and "Slate 7" in p.title:
            p.qa = [("Does it come with the recalled charger?",
                     "Units shipped from 16 Gale 412 include the VC-7B. If yours has a VC-7A, request a "
                     "free replacement.", "Vantle Store" if p.seller == "vantle-store" else "A buyer"),
                    ("Can I use my Slate 6 charger?", "Yes, the VC-6 works but charges more slowly.", "Vantle Store")]
        elif p.sub == "Telescopes":
            p.qa = [("Is this good for the Pith crossing?", "Yes, but use an Ossa filter.", "A buyer")]
    return sellers, products


def _specs(rng, sub):
    common = [("Weight", f"{rng.uniform(0.1, 9):.1f} wt")]
    extra = {
        "Kettles": [("Capacity", f"{rng.randint(4, 9)} measures"), ("Power", f"{rng.choice([1200, 1800, 2200, 3000]):,} fenwicks")],
        "Lamps": [("Light", f"{rng.choice([200, 400, 600, 900])} candles"), ("Power", f"{rng.choice([9, 12, 40, 60])} fenwicks")],
        "Clocks": [("Movement", rng.choice(["spring", "voltaic", "weight-driven"])), ("Moon dials", rng.choice(["none", "Ossa", "Ossa and Pith"]))],
        "Telescopes": [("Aperture", f"{rng.choice([50, 70, 90, 120, 150])} thumbs")],
        "Slates": [("Memory", f"{rng.choice([16, 32, 64])} weaves")],
        "Desk looms": [("Memory", f"{rng.choice([256, 512, 1024])} weaves"), ("Reeds", f"{rng.choice([8, 16, 32])} million")],
        "Chargers and cables": [("Output", f"{rng.choice([5, 10, 18, 30])} fenwicks")],
        "Boots": [("Sizes", "5 to 13 (Veyl sizing)"), ("Sole", rng.choice(["rubber", "leather", "hobnail"]))],
        "Coats": [("Sizes", "S, M, L, XL"), ("Material", rng.choice(["oilskin", "moor wool", "linen", "sealskin"]))],
        "Board games": [("Players", f"{rng.randint(1, 2)} to {rng.randint(3, 6)}")],
    }.get(sub, [])
    return extra + common


SELLERS, PRODUCTS = _build()
SELLER = {s.id: s for s in SELLERS}
PRODUCT = {p.id: p for p in PRODUCTS}
