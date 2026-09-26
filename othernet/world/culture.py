"""Films, books, and records of Averra."""
from dataclasses import dataclass, field

from ..engine.rng import stream, slug, pick_weighted
from .calendar import ADate
from .names import make_name
from .people import NOTABLE

# ---------------------------------------------------------------------------
# Words for titles
# ---------------------------------------------------------------------------
ADJ = ["Silent", "Hollow", "Drowned", "Last", "Crooked", "Salt", "Golden", "Ninth", "Pale",
       "Lantern", "Cinder", "Winter", "Paper", "Glass", "Brass", "Quiet", "Long", "Iron",
       "Second", "Low", "Bright", "Sunken", "Burning", "Little", "Stolen", "Wandering"]
NOUN = ["Tide", "Ledger", "Ferry", "Lock", "Moon", "Harbour", "Loom", "Bridge", "Lamp",
        "Orchard", "Kiln", "Keeper", "Weaver", "Moor", "Clock", "Crossing", "Gull", "Shaft",
        "Reach", "Ford", "Lighthouse", "Canal", "Choir", "Stair", "Mill", "Well", "Hold"]
PLACEY = ["Marrowby", "Wendmoor", "Brineholt", "Quenby", "Tarrow", "Saltspire", "Lowmarsh",
          "Harrowdeep", "the Sallow", "the Reach", "Corrack", "Emberly", "Coralstead"]


def title_gen(rng):
    k = rng.randrange(7)
    if k == 0:
        return f"The {rng.choice(ADJ)} {rng.choice(NOUN)}"
    if k == 1:
        return f"{rng.choice(NOUN)}s of {rng.choice(PLACEY)}"
    if k == 2:
        return f"A {rng.choice(NOUN)} for {rng.choice(PLACEY)}"
    if k == 3:
        return f"The {rng.choice(NOUN)} and the {rng.choice(NOUN)}"
    if k == 4:
        return f"{rng.choice(ADJ)} {rng.choice(NOUN)}"
    if k == 5:
        return f"Beneath the {rng.choice(ADJ)} {rng.choice(NOUN)}"
    return f"{rng.choice(['Two', 'Three', 'Nine', 'Eleven', 'Seven'])} {rng.choice(NOUN)}s"


GENRES_FILM = ["drama", "comedy", "thriller", "historical", "romance", "adventure", "mystery",
               "documentary", "family", "horror"]


@dataclass
class Film:
    id: str
    title: str
    year: int
    director: str
    cast: list  # (actor name, role)
    runtime: int
    genre: str
    studio: str
    synopsis: str
    box_office: int  # crowns
    rating: float
    votes: int
    release: ADate = None
    awards: list = field(default_factory=list)
    trivia: list = field(default_factory=list)
    nation: str = "VEY"


STUDIOS = ["Sallowlight Pictures", "Glasswharf Films", "Reachmoor Studios", "Northmole Pictures",
           "Kiln House", "Lanternport Film Collective"]

# fmt: off
KEY_FILMS = [
    dict(id="two-moons-over-marrowby", title="Two Moons Over Marrowby", year=409,
         director="Anouk Belvaine", cast=[("Jago Tidewright", "Casso Venn"), ("Liora Duvaine", "Maren Solis"),
         ("Edric Whitmore", "The Harbourmaster")], runtime=118, genre="romance",
         studio="Glasswharf Films", nation="PEL",
         synopsis="A pearl diver and a visiting astronomer fall in love during the week both moons are "
                  "full, and must decide whether to leave Marrowby together.",
         box_office=41_000_000, rating=8.1, votes=21_904, release=ADate(409, 5, 20),
         awards=["Golden Lantern, best score (409)"],
         trivia=["The night market scenes were shot during the real Marrowby Night Market.",
                 "Belvaine's own grandmother appears as the pearl buyer."]),
    dict(id="the-lampwright", title="The Lampwright", year=411, director="Anouk Belvaine",
         cast=[("Jago Tidewright", "Idra Fenwick's apprentice, Tobin"), ("Sabel Aubrande", "Idra Fenwick"),
               ("Corra Shoalby", "Mother Fenwick")], runtime=141, genre="historical",
         studio="Glasswharf Films", nation="PEL",
         synopsis="The story of the voltaic lamp, told by the apprentice who carried it through the "
                  "streets of Emberly on the night of its first demonstration in 288.",
         box_office=88_500_000, rating=8.7, votes=40_112, release=ADate(411, 9, 2),
         awards=["Golden Lantern, best picture (412)", "Golden Lantern, best direction (412)",
                 "Golden Lantern, best score (412)", "Golden Lantern, best lead: Jago Tidewright (412)"],
         trivia=["The lamp used on set was lent by the Loom Hall museum.",
                 "Filming in Emberly was delayed nine days by fog."]),
    dict(id="the-salt-ledger", title="The Salt Ledger", year=407, director="Pascoe Kelpman",
         cast=[("Nessa Brinecombe", "Ysella Marr"), ("Jago Tidewright", "Young Casso")], runtime=126,
         genre="historical", studio="Northmole Pictures", nation="SLT",
         synopsis="Adapted from Morwen Reefley's novel about the bookkeeper who kept the secret "
                  "accounts of the Salt Revolt.", box_office=36_000_000, rating=7.6, votes=15_220,
         release=ADate(407, 3, 3), trivia=["Reefley has a cameo as a fishwife."]),
    dict(id="deepshaft", title="Deepshaft", year=398, director="Ironsvale Maerk",
         cast=[("Cinder Ragna", "Hilde"), ("Flint Egil", "The Foreman")], runtime=97,
         genre="thriller", studio="Kiln House", nation="KHR",
         synopsis="Six miners trapped beneath Cinderfell tell each other stories while they wait "
                  "to be found.", box_office=9_200_000, rating=7.9, votes=8_870,
         release=ADate(398, 7, 7),
         trivia=["Interest in the film surged after the real Deepshaft 9 collapse of 412."]),
    dict(id="the-ninth-bridge", title="The Ninth Bridge", year=388, director="Florian Ashby",
         cast=[("Maud Hollins", "Wardens' Bridge keeper")], runtime=104, genre="drama",
         studio="Sallowlight Pictures", synopsis="A bridge keeper refuses to leave her post during "
         "the flood of 288.", box_office=5_000_000, rating=7.2, votes=4_310, release=ADate(388, 2, 2)),
    dict(id="loom", title="Loom", year=403, director="Theon Aubrel",
         cast=[("Quilla Marovane", "Temmet Aske")], runtime=132, genre="historical",
         studio="Lanternport Film Collective", nation="PEL",
         synopsis="The life of Temmet Aske and the building of the first Loom.",
         box_office=22_000_000, rating=7.8, votes=12_004, release=ADate(403, 10, 1),
         trivia=["Aske is played by a woman, a casting choice that divided critics."]),
]
# fmt: on


def _films():
    films = [Film(**f) for f in KEY_FILMS]
    rng = stream("films")
    used = {f.title for f in films}
    actors = []
    for i in range(70):
        nat = pick_weighted(rng, [("VEY", 5), ("SLT", 3), ("PEL", 3), ("KHR", 1)])
        actors.append(make_name(rng, nat).full)
    actors += ["Jago Tidewright", "Nessa Brinecombe", "Liora Duvaine", "Sabel Aubrande"]
    for i in range(70):
        t = title_gen(rng)
        while t in used:
            t = title_gen(rng)
        used.add(t)
        year = rng.randint(372, 412)
        nat = pick_weighted(rng, [("VEY", 5), ("SLT", 3), ("PEL", 3), ("KHR", 1)])
        director = make_name(rng, nat).full if rng.random() < 0.85 else "Anouk Belvaine"
        cast = [(a, r) for a, r in zip(rng.sample(actors, rng.randint(2, 5)),
                                        ["the keeper", "the stranger", "the captain", "the widow",
                                         "the clerk", "the child"])]
        genre = rng.choice(GENRES_FILM)
        films.append(Film(
            slug(t) + f"-{year}", t, year, director, cast, rng.randint(78, 165), genre,
            rng.choice(STUDIOS),
            f"A {genre} set in {rng.choice(PLACEY)}, in which {cast[0][1]} and {cast[1][1]} "
            f"are drawn together by a {rng.choice(NOUN).lower()} that should not exist.",
            int(rng.lognormvariate(15.6, 1.0)), round(rng.uniform(4.1, 8.8), 1),
            rng.randint(90, 18_000), ADate(year, rng.randint(1, 10), rng.randint(1, 36)), nation=nat))
    return films


FILMS = _films()
FILM = {f.id: f for f in FILMS}


# ---------------------------------------------------------------------------
@dataclass
class Book:
    id: str
    title: str
    author: str
    year: int
    publisher: str
    pages: int
    qn: str  # Quillmere Number, the book identifier used across Averra
    genre: str
    blurb: str
    price_cr: float
    subjects: list = field(default_factory=list)
    call_no: str = ""


PUBLISHERS = ["Quillmere Press", "Tidings Press", "Lanternport University Press", "Harrow Stone Books",
              "Gorse & Daughters", "Northmole Books"]
BOOK_GENRES = ["novel", "history", "poetry", "cookery", "travel", "science", "mathematics",
               "children", "biography", "mystery", "loomcraft", "law"]

# fmt: off
KEY_BOOKS = [
    ("The Salt Ledger", "Morwen Reefley", 405, "Quillmere Press", 412, "novel",
     "A bookkeeper keeps the secret accounts of the Salt Revolt, and pays for it.", ["Salt Revolt"]),
    ("Nine Fathoms Down", "Morwen Reefley", 410, "Quillmere Press", 368, "novel",
     "A diver searching the Brineholt harbour after the Fire of 404 finds a ship that should not "
     "be there.", ["Brineholt Harbour Fire"]),
    ("The Book of Fords", "Rosamund Tallwick", 30, "Quillmere Press", 220, "history",
     "The founding record of the Concordat, in the First Registrar's own words. Modern edition "
     "with notes.", ["Treaty of the Nine Fords"]),
    ("Moor Songs", "Hollis Thornby", 322, "Quillmere Press", 96, "poetry",
     "Sixty poems of Wendmoor, including 'Many Fords'.", ["Wendmoor"]),
    ("On the Motion of the Lesser Moon", "Oswin Solavey", 133, "Lanternport University Press", 140,
     "science", "Solavey's account of Pith's backward orbit.", ["Pith", "Astronomy"]),
    ("Reeds and Ribbons: Building the Loom", "Temmet Aske", 369, "Lanternport University Press",
     388, "loomcraft", "Aske's notebooks on the construction of the first Loom.", ["The Loom"]),
    ("Tidal Primes", "Ysolde Cresselle", 340, "Lanternport University Press", 210, "mathematics",
     "The monograph in which the Cresselle Conjecture was first stated, on page 117.",
     ["Tidal prime", "Cresselle Conjecture"]),
    ("A Weft Primer", "Mireille Solande", 401, "Lanternport University Press", 304, "loomcraft",
     "The standard introduction to programming looms in Weft.", ["Weft"]),
    ("The Copper Kettle Book of Teas", "Hester Brackley", 404, "Gorse & Daughters", 176, "cookery",
     "Forty blends and the stories behind them.", ["Tea"]),
    ("Walking the Sallow", "Wenna Larkfield", 411, "Northmole Books", 240, "travel",
     "From the Kethren springs to the Glass Sea on foot, in sixty-one days.", ["River Sallow"]),
    ("The Cinder War", "Aldermoot Venna", 380, "Harrow Stone Books", 530, "history",
     "The standard Kethren history of the war of 241 to 246.", ["Cinder War"]),
    ("Keepers of the Spire", "Pascoe Keelmouth", 399, "Tidings Press", 190, "history",
     "Twelve generations of Keelmouths and the lighthouse they kept.", ["The Spire"]),
]
# fmt: on


def _qn(rng, pub):
    return f"QN {PUBLISHERS.index(pub) + 1}-{rng.randint(1000, 9999)}-{rng.randint(100, 999)}-{rng.randint(0, 9)}"


def _books():
    rng = stream("books")
    out = []
    for t, a, y, p, pg, g, blurb, subj in KEY_BOOKS:
        out.append(Book(slug(t), t, a, y, p, pg, _qn(rng, p), g, blurb,
                        round(rng.uniform(8, 42), 2), subj))
    used = {b.title for b in out}
    authors = [make_name(rng, pick_weighted(rng, [("VEY", 5), ("SLT", 3), ("PEL", 2), ("KHR", 1)])).full
               for _ in range(60)]
    for i in range(170):
        g = rng.choice(BOOK_GENRES)
        t = title_gen(rng)
        if g == "cookery":
            t = f"{rng.choice(['Suppers', 'Bakes', 'Soups', 'Preserves', 'Pies'])} of {rng.choice(PLACEY)}"
        elif g == "history":
            t = f"A History of {rng.choice(PLACEY)}"
        elif g == "loomcraft":
            t = f"{rng.choice(['Practical', 'Advanced', 'Everyday', 'Weaving with'])} Weft"
            t += f" ({rng.choice(['2nd', '3rd', '4th'])} ed.)" if rng.random() < .4 else ""
        while t in used:
            t = t + " II"
        used.add(t)
        pub = rng.choice(PUBLISHERS)
        y = rng.randint(300, 412)
        out.append(Book(slug(t) + f"-{y}", t, rng.choice(authors), y, pub, rng.randint(80, 620),
                        _qn(rng, pub), g, f"A {g} book from {pub}.", round(rng.uniform(5, 60), 2),
                        [rng.choice(PLACEY).replace("the ", "").title()]))
    for b in out:
        b.call_no = f"{BOOK_GENRES.index(b.genre) * 100 + rng.randint(1, 99):03d}.{rng.randint(1, 9)} " \
                    f"{b.author.split()[-1][:3].upper()}"
    return out


BOOKS = _books()
BOOK = {b.id: b for b in BOOKS}


# ---------------------------------------------------------------------------
@dataclass
class Album:
    id: str
    title: str
    artist: str
    release: ADate
    tracks: list  # (title, seconds)
    catalog: str
    fmt: list
    notes: str = ""


@dataclass
class Artist:
    id: str
    name: str
    city: str
    formed: int
    genre: str
    members: list
    bio: str


ARTISTS = [
    Artist("nell-hedgecote", "Nell Hedgecote", "Caddick Ford", 405, "lock-folk",
           ["Nell Hedgecote (voice, bouzouki)"],
           "Nell Hedgecote grew up in the lock-keeper's cottage at Caddick Lock number eleven. Her "
           "second album, 'Lock Eleven', was the best-selling record of 411."),
    Artist("the-lamplighters", "The Lamplighters", "Brineholt", 398, "harbour rock",
           ["Kit Marrow (voice)", "Tern Salby (guitar)", "Dory Keelson (drums)", "Arlo Finch (bass)"],
           "Four former lamplighters' apprentices from the Rope Walk."),
    Artist("gorm-and-the-deep", "Gorm & the Deep", "Harrowdeep", 401, "hall drone",
           ["Coldforge Gorm (voice)", "Flint Asta (horns)", "Underhill Stig (drums)"],
           "Recorded entirely in the Lanternway caverns under Harrowdeep."),
    Artist("marrowby-night-choir", "Marrowby Night Choir", "Marrowby", 360, "choral",
           ["Forty singers"], "A choir that sings only after Ossa rises."),
    Artist("sprocket-and-wick", "Sprocket & Wick", "Ostmere", 408, "loom pop",
           ["Sprocket (looms)", "Wick (voice)"], "Duo who make music on salvaged looms."),
    Artist("the-fogbells", "The Fogbells", "Lowmarsh", 403, "marsh jangle",
           ["Hester Pike", "Ivo Crane", "Maud Lark"], "A trio from the Lowmarsh jetties."),
]
ARTIST = {a.id: a for a in ARTISTS}

SONG_WORDS = ["Lock", "Bridge", "Ossa", "Pith", "Harbour", "Salt", "Lantern", "Kettle", "Moor",
              "Ferry", "Rain", "Stair", "Ember", "Rope", "Tide", "Gull", "Fog", "Hollow", "Mile",
              "Letter", "Kiln", "Reed", "Ledger", "Night", "Market"]


def _song(rng):
    k = rng.randrange(5)
    a, b = rng.sample(SONG_WORDS, 2)
    return [f"{a} and {b}", f"The {a} Song", f"{a}light", f"Down by the {a}", f"{a} {b}"][k]


def _albums():
    rng = stream("albums")
    spec = [
        ("nell-hedgecote", "Harthwick Mornings", ADate(407, 3, 12)),
        ("nell-hedgecote", "Lock Eleven", ADate(411, 1, 22)),
        ("nell-hedgecote", "Ninth Bridge", ADate(412, 6, 12)),
        ("the-lamplighters", "Rope Walk", ADate(401, 5, 5)),
        ("the-lamplighters", "Wick & Oil", ADate(405, 8, 30)),
        ("the-lamplighters", "After the Fire", ADate(410, 2, 2)),
        ("gorm-and-the-deep", "Lanternway", ADate(404, 7, 7)),
        ("gorm-and-the-deep", "Seam", ADate(409, 9, 9)),
        ("marrowby-night-choir", "Songs for Ossa", ADate(398, 4, 4)),
        ("sprocket-and-wick", "Punched Ribbon", ADate(410, 10, 10)),
        ("sprocket-and-wick", "Weave Sickness", ADate(412, 3, 30)),
        ("the-fogbells", "Jetty Nine", ADate(406, 1, 16)),
        ("the-fogbells", "Eel Season", ADate(411, 4, 20)),
    ]
    out = []
    n = 100
    for artist, title, rel in spec:
        r = stream("album", title)
        tracks = []
        for i in range(r.randint(8, 12)):
            tracks.append((_song(r), r.randint(128, 331)))
        if title == "Lock Eleven":
            tracks[0] = ("Lock Eleven", 244)
            tracks[3] = ("Keeper's Daughter", 212)
        if title == "Ninth Bridge":
            tracks[0] = ("Wardens' Bridge", 263)
            tracks[1] = ("Nine Fords", 198)
            tracks[-1] = ("Flood of 288", 402)
        n += rng.randint(1, 9)
        out.append(Album(slug(title), title, artist, rel, tracks, f"BLW-{n:03d}",
                         rng.sample(["wax disc", "ribbon", "Weave stream"], rng.randint(1, 3))))
    return out


ALBUMS = _albums()

TOUR_412 = [  # Nell Hedgecote's 'Ninth Bridge' tour
    (ADate(412, 7, 4), "Caddick Ford", "Millside Hall"),
    (ADate(412, 7, 9), "Ostmere", "The Nine Bridges Theatre"),
    (ADate(412, 7, 15), "Tarrow", "Canalside Assembly Rooms"),
    (ADate(412, 7, 22), "Harthwick", "Lamp Hill Pavilion"),
    (ADate(412, 7, 28), "Brineholt", "The Rope Walk Hall"),
    (ADate(412, 8, 3), "Gullhaven", "The Slipway Stage"),
    (ADate(412, 8, 10), "Saltspire", "Spire Green (CANCELLED: Storm Petrel)"),
    (ADate(412, 8, 21), "Lanternport", "Glasswharf Bowl"),
    (ADate(412, 8, 27), "Marrowby", "Night Market Stage"),
    (ADate(412, 9, 6), "Harrowdeep", "The Anvil Hall"),
    (ADate(412, 9, 14), "Emberly", "The Old Kiln"),
]
