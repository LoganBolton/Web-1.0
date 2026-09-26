"""Companies, guilds, institutions, and political parties."""
from dataclasses import dataclass, field

from ..engine.rng import stream, slug


@dataclass
class Company:
    id: str
    name: str
    nation: str
    city: str
    founded: int
    industry: str
    description: str
    ceo: str = ""  # person id or plain name
    founders: list = field(default_factory=list)
    ticker: str = ""
    domain: str = ""
    employees: int = 0
    registry_no: str = ""
    parent: str = ""  # company id of owner
    status: str = "Active"
    shares: int = 0  # shares outstanding (listed companies)
    base_price: float = 0.0  # tally price at the start of 412
    extra: dict = field(default_factory=dict)

    @property
    def slug(self):
        return slug(self.name)


# fmt: off
COMPANIES = [
    Company("vantle", "Vantle", "VEY", "Ostmere", 399, "Loom devices",
            "Maker of the Vantle Slate, the most popular handheld loom in Averra.",
            "sabine-marwick", ["sabine-marwick", "corwen-talley"], "VNTL", "vantle.ves", 12_400,
            shares=410_000_000, base_price=88.40),
    Company("bazaar", "Bazaar Holdings", "VEY", "Caddick Ford", 396, "Retail",
            "Operator of Bazaar, the largest marketplace on the Weave, and owner of Reelhouse.",
            "edric-hollowell", ["edric-hollowell"], "BZR", "bazaar.ves", 31_000,
            shares=620_000_000, base_price=141.10),
    Company("lanthorn", "Lanthorn", "PEL", "Lanternport", 398, "Weave search",
            "Operator of the Lanthorn search engine.", "Cael Morvenne",
            ["nerys-lanterre", "elio-duvaine"], "LNTH", "lanthorn.ves", 5_900,
            shares=300_000_000, base_price=203.75),
    Company("drovers", "Drovers' Bank", "VEY", "Ostmere", 211, "Banking",
            "The oldest bank in the Concordat, founded to lend to cattle drovers on the Sallow road.",
            "Clemence Holloway", [], "DRVB", "drovers.ves", 44_000,
            shares=1_200_000_000, base_price=36.20, extra={"chair": "garrick-stanmore"}),
    Company("emberline", "Emberline", "SLT", "Brineholt", 322, "Shipping and travel",
            "Operator of ferries and airships across the Glass Sea and the Grey Reach.",
            "marra-keelworth", ["Halyard Emberson"], "EMBL", "emberline.ves", 8_300,
            shares=150_000_000, base_price=54.60),
    Company("copperkettle", "The Copper Kettle", "VEY", "Gorse Hollow", 389, "Food and drink",
            "Chain of 140 tea rooms across Veyl and Saltmarch.", "hester-brackley",
            ["hester-brackley"], "CKTL", "copperkettle.ves", 4_100,
            shares=48_000_000, base_price=19.85),
    Company("coldforge", "Coldforge Mining", "KHR", "Cinderfell", 180, "Mining",
            "Coal and iron miner, operator of the Deepshaft workings at Cinderfell.",
            "coldforge-brokk", ["Coldforge Holm"], "CLDF", "", 17_000,
            shares=220_000_000, base_price=61.00),
    Company("gildmere", "Gildmere Works", "VEY", "Tarrow", 340, "Civil engineering",
            "Canal, bridge, and lock builder. Holder of the Tarrow Canal widening contract.",
            "Osric Gildmere", ["Ambrose Gildmere"], "GLDW", "", 6_700,
            shares=90_000_000, base_price=27.30),
    Company("saltspire", "Saltspire Salt Company", "SLT", "Saltspire", 55, "Salt and chemicals",
            "The Republic's oldest salt producer.", "Tamar Saltworth", [], "SALT", "", 2_900,
            shares=60_000_000, base_price=12.40),
    Company("quillmere", "Quillmere Press", "VEY", "Ostmere", 244, "Publishing",
            "Publisher and bookseller. Publishes Morwen Reefley and the Commonplace print edition.",
            "Linnet Quillmere", ["Anneke Quillmere"], "", "quillmere.ves", 800),
    Company("bellows", "Bellows Records", "SLT", "Brineholt", 377, "Music",
            "Independent record label, home of Nell Hedgecote and The Lamplighters.",
            "Kit Bellows", ["Kit Bellows"], "", "bellows.ves", 120),
    Company("emberlyglass", "Emberly Glassworks", "VEY", "Emberly", 96, "Glass",
            "Makers of green Emberly glass since the first century of the Concord.",
            "Florian Ashby", [], "EMGL", "", 2_200, shares=35_000_000, base_price=8.75),
    Company("keelwright", "Keelwright Shipyards", "SLT", "Gullhaven", 88, "Shipbuilding",
            "Builder of Emberline's ferries and of the Saltmarch navy.", "Jessamy Keelwright",
            [], "KLWR", "", 9_100, shares=110_000_000, base_price=44.00),
    Company("morrowmedia", "Morrow Media Group", "VEY", "Ostmere", 395, "Media",
            "Owner of the Morrow portal and, less publicly, The Crier.", "Radley Blythmore",
            ["Radley Blythmore"], "MRW", "morrow.ves", 1_400, shares=70_000_000,
            base_price=15.10),
    Company("courierpub", "Courier Publishing", "VEY", "Ostmere", 190, "Media",
            "Publisher of the Ostmere Courier.", "Idony Stanley", [], "", "ostmerecourier.wir", 900),
    Company("tidingspress", "Tidings Press", "SLT", "Brineholt", 102, "Media",
            "Publisher of the Brineholt Tidings.", "Sennen Shoalby", [], "", "tidings.slt", 600),
    Company("caddickmills", "Caddick Mills", "VEY", "Caddick Ford", 150, "Textiles",
            "Wool and linen mills on the Caddick.", "Hemming Carrow", [], "CDMK", "", 5_500,
            shares=80_000_000, base_price=9.90),
    Company("silverrunrefining", "Silverrun Refining", "VEY", "Silverrun", 61, "Metals",
            "Silver and copper refiner.", "Petra Whitholt", [], "SLRF", "", 3_300,
            shares=95_000_000, base_price=22.60),
    Company("glassseains", "Glass Sea Insurance", "SLT", "Brineholt", 140, "Insurance",
            "Marine and property insurer.", "Roscoe Harbourley", [], "GSIN", "", 3_800,
            shares=130_000_000, base_price=31.45),
    Company("kettlebright", "Kettlebright Appliances", "VEY", "Tarrow", 360, "Appliances",
            "Kettles, lamps, and heaters sold across Averra.", "Warrick Dunley", [], "KTBR", "",
            2_700, shares=52_000_000, base_price=17.30),
    Company("ossaoptics", "Ossa Optics", "PEL", "Lanternport", 311, "Optics",
            "Maker of telescopes, spectacles, and the lenses in every Vantle Slate.", "Sabel Oss",
            [], "OSOP", "", 1_900, shares=40_000_000, base_price=66.10),
    Company("loomworks", "Loomworks", "PEL", "Lanternport", 372, "Loom devices",
            "Founded by students of Temmet Aske. Makes desk looms and the Weft language tools.",
            "Mireille Solande", [], "LMWK", "", 7_800, shares=180_000_000, base_price=72.95),
    Company("undertow", "Undertow Games", "PEL", "Lanternport", 401, "Games",
            "Studio behind 'Fathom' and 'Fathom: Undertow'.", "theon-morvenne",
            ["theon-morvenne"], "", "", 140),
    Company("pearlpith", "Pearl & Pith", "PEL", "Marrowby", 398, "Restaurant",
            "Restaurant on the Marrowby waterfront.", "delphine-estrande",
            ["delphine-estrande"], "", "", 35),
    Company("hearthfind", "Hearthfind", "VEY", "Ostmere", 402, "Property",
            "Property listings for Veyl and Saltmarch.", "Selwyn Marby", [], "", "hearthfind.ves", 210),
    Company("harrowlamp", "Harrowdeep Lamp Company", "KHR", "Harrowdeep", -40, "Lighting",
            "Makers of miners' lamps for nine centuries.", "Thornhelm Oda", [], "HLMP", "", 1_100,
            shares=25_000_000, base_price=14.05),
    Company("tarrowgrain", "Tarrow Grain Exchange", "VEY", "Tarrow", 120, "Commodities",
            "Grain trading house.", "Bertram Holley", [], "TGX", "", 600, shares=20_000_000,
            base_price=48.30),
    Company("brineholttram", "Brineholt Tramways Authority", "SLT", "Brineholt", 331,
            "Public transport", "Runs the trams and funiculars of Brineholt.", "Nance Tideley",
            [], "", "tramways.slt", 2_400),
    Company("hollowmarket", "Hollowmarket Auctions", "VEY", "Ostmere", 318, "Auctions",
            "Auction house for antiques, looms, and curiosities.", "Cressida Vane",
            [], "", "hollowmarket.ves", 90),
    Company("tastemark", "Tastemark", "SLT", "Brineholt", 403, "Reviews",
            "Reviews of restaurants, inns, and shops.", "Delph Sprayer", [], "", "tastemark.ves", 60),
]
# fmt: on

COMPANY = {c.id: c for c in COMPANIES}


def assign_registry_numbers():
    rng = stream("registry-numbers")
    for c in COMPANIES:
        if c.nation == "VEY":
            c.registry_no = f"CR-{rng.randint(10, 99)}-{rng.randint(100000, 999999)}"
        elif c.nation == "SLT":
            c.registry_no = f"SM{rng.randint(1000, 9999)}/{rng.choice('ABCDEFGH')}"
        elif c.nation == "KHR":
            c.registry_no = f"HOLD-{rng.randint(100, 999)}-{rng.choice(['A', 'K', 'R'])}"
        else:
            c.registry_no = f"PL{rng.randint(100000, 999999)}"


assign_registry_numbers()

# ---------------------------------------------------------------------------
PARTIES = {
    "civic-ledger": {"name": "Civic Ledger Party", "color": "#2f5d8a", "abbr": "CL",
                     "leader": "maelis-ondraker",
                     "blurb": "Centrist party of the civil service towns. Favours registry reform."},
    "hearth-plough": {"name": "Hearth & Plough", "color": "#8a5a2f", "abbr": "HP",
                      "leader": "dorran-whitby",
                      "blurb": "Rural conservatives. Strongest in Wendmoor and Gorsefield."},
    "open-ford": {"name": "Open Ford", "color": "#d97706", "abbr": "OF",
                  "leader": "Linnet Crawley",
                  "blurb": "Liberal reformers who want Weave access written into the Concord."},
    "canalworkers": {"name": "Canalworkers' League", "color": "#b91c1c", "abbr": "CW",
                     "leader": "Harlan Mottram",
                     "blurb": "Labour party founded by the lock-keepers' union."},
    "green-moor": {"name": "Green Moor", "color": "#15803d", "abbr": "GM",
                   "leader": "Briony Fenshaw",
                   "blurb": "Environmentalists, opposed to the Tarrow Canal widening."},
}
# Seats after the election of 411 CR (90 seats, 46 for a majority).
SEATS = {"civic-ledger": 38, "hearth-plough": 24, "open-ford": 13, "canalworkers": 10,
         "green-moor": 5}
# The Civic Ledger governs in coalition with Open Ford (51 seats).
COALITION = ["civic-ledger", "open-ford"]

PROVINCES = [
    ("Sallowmark", "Ostmere"), ("Caddock", "Caddick Ford"), ("Tarrowdale", "Tarrow"),
    ("Silvermere", "Silverrun"), ("Wendmoor", "Wendmoor"), ("Harthshire", "Harthwick"),
    ("Emberdown", "Emberly"), ("Gorsefield", "Gorse Hollow"), ("The Lowlands", "Lowmarsh"),
]

UNIVERSITIES = [
    ("Lanternport University", "Lanternport", 118, "lanternport.hal"),
    ("The Ostmere Academy", "Ostmere", 64, ""),
    ("Harrowdeep Collegium", "Harrowdeep", -300, ""),
    ("Brineholt School of Navigation", "Brineholt", 140, ""),
    ("Caddick Ford Polytechnic", "Caddick Ford", 330, ""),
]

GUILDS = [
    ("Guild of Numerists", "numerary.gld", "Keeps the rolls of proven results in mathematics."),
    ("Guild of Inventors", "patentrolls.gld", "Grants and records patents of invention."),
    ("Guild of Weft Programmers", "weft.gld", "Maintains the Weft programming language."),
    ("Guild of Labour Exchanges", "guildwork.gld", "Runs the Guildwork job board."),
    ("Guild of Lamplighters", "", "Keeps the lamps of the old cities burning."),
    ("Guild of Cartographers", "", "Surveys and charts. Publishes the Chartroom atlas."),
]
