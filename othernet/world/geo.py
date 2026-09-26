"""Nations, cities, and landmarks of Averra.

Map coordinates are in "chart units" on a 1000 x 700 chart of the known
world. One chart unit is half a league. One league is 4000 ells (an ell is
a little over a metre).
"""
import math
from dataclasses import dataclass, field

from ..engine.rng import slug


@dataclass
class Nation:
    code: str
    name: str
    short: str
    demonym: str
    capital: str
    currency: str
    currency_code: str
    currency_symbol: str
    currency_sub: str
    sub_per_unit: int
    tld: str
    government: str
    head_title: str
    head: str  # person id, filled by people module
    population: int
    language: str
    founded: str
    color: str
    color2: str
    motto: str
    summary: str
    area_sq_leagues: int
    phone_prefix: str


NATIONS = {
    "VEY": Nation(
        "VEY", "The Concordat of Veyl", "Veyl", "Veylish", "Ostmere", "crown", "VCR", "cr",
        "pennet", 100, "vey", "Federal concordat of nine provinces",
        "First Warden", "", 48_200_000, "Veylish", "0 CR (Treaty of the Nine Fords)",
        "#6b2d5c", "#e8c547", "By many fords, one river",
        "The largest nation of Averra, a federation of nine provinces bound by the Treaty "
        "of the Nine Fords. Famous for its enormous civil service and its Registry.",
        61_400, "+41"),
    "SLT": Nation(
        "SLT", "The Saltmarch Republic", "Saltmarch", "Saltmarcher", "Brineholt", "tally",
        "STL", "tl", "bit", 12, "slt", "Maritime republic governed by the Admiralty Council",
        "Tidemaster", "", 21_700_000, "Veylish (Marcher dialect)", "37 CR (Salt Revolt)",
        "#1f4e79", "#f2f2f2", "The sea keeps no ledger",
        "A seafaring republic of coastal cities and islands along the Grey Reach. Its "
        "tally is divided into twelve bits, a holdover from the salt trade.",
        18_900, "+52"),
    "KHR": Nation(
        "KHR", "The Kethren Holds", "Kethren", "Kethren", "Harrowdeep", "mark", "KMK", "mk",
        "chip", 100, "khr", "Confederation of clans under the Moot of Holds",
        "High Holdwarden", "", 9_400_000, "Kethric", "-880 CR (founding of Harrowdeep)",
        "#3d3d3d", "#d4652f", "Stone remembers",
        "A mountain confederation of mining clans along the Kethren Spine. The Holds count "
        "their years from the founding of Harrowdeep (HR = CR + 880).",
        22_300, "+63"),
    "PEL": Nation(
        "PEL", "The Pellucid Isles", "Pellucid", "Pellucidan", "Lanternport", "lume", "PLM",
        "lm", "glint", 100, "pel", "Collegiate republic led by the Senate of Colleges",
        "Chancellor-Senator", "", 6_100_000, "Pellish", "154 CR (Charter of Colleges)",
        "#0f766e", "#fde68a", "Light is owed to all",
        "An archipelago across the Glass Sea, governed by its universities. Home of the "
        "Lanternport Observatory and the Loom, the first thinking engine.",
        7_800, "+74"),
    "ODD": Nation(
        "ODD", "Oddavar", "Oddavar", "Oddavari", "Vesk", "sked", "OSK", "sk", "ore", 100,
        "odd", "Theocracy under the Synod of the Pale Flame", "Hierarch", "", 12_800_000,
        "Oddic", "unknown (claimed 1400 years before the Concord)", "#e5e7eb", "#1e3a8a",
        "The flame does not flicker",
        "A northern theocracy beyond the Frostgate pass. Its corner of the Weave is small and "
        "closely watched, and outsiders know little about it.",
        40_100, "+89"),
}


@dataclass
class City:
    name: str
    nation: str
    x: int
    y: int
    population: int
    founded: int  # CR year
    kind: str  # capital / port / river / mountain / island
    known_for: str
    elevation: int  # ells above sea level
    mean_temp: float  # degrees, annual mean
    temp_swing: float  # half the difference between warmest and coldest month
    rain: int  # annual rainfall, in thumbs
    postal: str
    districts: list = field(default_factory=list)
    mayor: str = ""  # person id

    @property
    def slug(self):
        return slug(self.name)

    @property
    def nation_obj(self):
        return NATIONS[self.nation]


def _c(*a, districts=()):
    return City(*a, districts=list(districts))


CITIES = [
    # --- Veyl ---------------------------------------------------------------
    _c("Ostmere", "VEY", 330, 360, 3_912_000, 0, "capital",
       "the Registry, the Assembly, and the Nine Bridges over the Sallow", 112, 12.4, 10.5, 740,
       "OS", districts=["Old Ford", "Wardens' Rise", "Tannery Row", "Sallowbank", "Nine Bridges",
                        "Copperside", "The Stacks", "Gallowmead"]),
    _c("Caddick Ford", "VEY", 240, 300, 1_204_000, 3, "river",
       "textile mills and the Caddick Lock", 140, 11.8, 11.0, 690, "CF",
       districts=["Millside", "Lockgate", "Hemming", "Upper Ford"]),
    _c("Tarrow", "VEY", 430, 420, 887_000, 22, "river",
       "the Tarrow Canal and grain exchanges", 88, 13.1, 10.8, 610, "TR",
       districts=["Canalside", "Granary", "Wexley", "Tarrow Heath"]),
    _c("Silverrun", "VEY", 200, 440, 512_000, 61, "river",
       "silver refining and the Silverrun Falls", 205, 12.0, 9.9, 820, "SR"),
    _c("Wendmoor", "VEY", 470, 280, 640_000, 14, "moor",
       "wool, peat, and the Wendmoor Standing Stones", 310, 9.6, 11.9, 910, "WM"),
    _c("Harthwick", "VEY", 280, 490, 415_000, 30, "port",
       "the Glass Sea ferries and the Harthwick Lighthouse", 6, 14.2, 8.1, 700, "HW",
       districts=["Quayside", "Lamp Hill", "Saltings"]),
    _c("Emberly", "VEY", 390, 250, 301_000, 88, "town",
       "glassworks and the Ember Kilns", 180, 11.2, 11.4, 650, "EM"),
    _c("Gorse Hollow", "VEY", 170, 350, 221_000, 105, "town",
       "orchards and the Gorse Hollow Cider Fair", 150, 11.9, 10.2, 780, "GH"),
    _c("Lowmarsh", "VEY", 500, 470, 152_000, 140, "marsh",
       "eel fisheries and fog", 3, 13.4, 9.5, 880, "LM"),
    _c("Quenby", "VEY", 260, 230, 95_000, 199, "town",
       "the Quenby Clockworks and its annual Clock Fair", 240, 10.1, 11.7, 700, "QB"),
    # --- Saltmarch ----------------------------------------------------------
    _c("Brineholt", "SLT", 430, 120, 2_104_000, 37, "capital",
       "the Admiralty, the great harbour, and the Brineholt Tramways", 4, 10.2, 7.9, 980,
       "BH-1", districts=["Admiralty", "Rope Walk", "Keelwater", "The Stair", "Fishmarket",
                          "Northmole", "Gullgate", "Sounding"]),
    _c("Gullhaven", "SLT", 300, 150, 698_000, 41, "port",
       "shipbuilding and the Gullhaven Regatta", 9, 10.8, 7.5, 940, "GV-2"),
    _c("Saltspire", "SLT", 560, 110, 331_000, 52, "port",
       "salt pans and the Spire, a lighthouse older than the Republic", 12, 9.9, 7.7, 1010,
       "SS-3"),
    _c("Wrackmouth", "SLT", 640, 170, 262_000, 70, "port",
       "kelp farming and the Wrackmouth Fish Auction", 7, 9.4, 8.0, 1060, "WK-4"),
    _c("Corrack", "SLT", 380, 60, 181_000, 45, "island",
       "the Corrack Naval Yards and seabird cliffs", 30, 8.8, 6.9, 1120, "CK-5"),
    _c("Tidewell", "SLT", 220, 120, 119_000, 97, "port",
       "the tidal mill and oyster beds", 5, 10.5, 7.2, 960, "TW-6"),
    # --- Kethren --------------------------------------------------------------
    _c("Harrowdeep", "KHR", 640, 300, 802_000, -880, "capital",
       "the Deep Halls, a city half carved into the Spine", 1480, 6.1, 12.8, 560, "H1",
       districts=["Upper Tier", "The Delve", "Moothall", "Forgeward", "Lanternway"]),
    _c("Cinderfell", "KHR", 700, 230, 309_000, -610, "mountain",
       "coal and iron mines, including the Deepshaft workings", 1210, 5.2, 13.1, 600, "C2"),
    _c("Stonemeet", "KHR", 600, 380, 198_000, -420, "mountain",
       "the Stonemeet Moot Stones and quarries", 990, 7.4, 12.2, 620, "S3"),
    _c("Frostgate", "KHR", 748, 205, 141_000, -300, "mountain",
       "the pass to Oddavar and the Frostgate Wall", 1760, 2.1, 13.9, 480, "F4"),
    _c("Aldermoot", "KHR", 690, 360, 88_000, -150, "valley",
       "alder forests and the only vineyards in the Holds", 720, 8.3, 11.5, 640, "A5"),
    # --- Pellucid -----------------------------------------------------------
    _c("Lanternport", "PEL", 560, 610, 1_106_000, 118, "capital",
       "Lanternport University, the Observatory, and the Loom Hall", 22, 17.8, 6.2, 1210,
       "LP", districts=["Collegium", "Observatory Hill", "Glasswharf", "Old Lantern",
                        "Tessellate", "Brightmarket"]),
    _c("Marrowby", "PEL", 440, 620, 231_000, 126, "island",
       "pearl diving and the Marrowby Night Market", 11, 18.4, 5.8, 1330, "MB"),
    _c("Shellcombe", "PEL", 680, 640, 79_000, 160, "island",
       "shell glass and a famous botanical garden", 18, 18.9, 5.5, 1400, "SC"),
    _c("Vanehaven", "PEL", 760, 600, 61_000, 173, "island",
       "wind vanes, weather research, and the Vanehaven Weather Tower", 40, 17.1, 6.0,
       1290, "VH"),
    _c("Coralstead", "PEL", 380, 660, 44_000, 201, "island",
       "reef diving and slow living", 4, 19.5, 5.1, 1450, "CS"),
    # --- Oddavar ----------------------------------------------------------
    _c("Vesk", "ODD", 860, 150, 1_890_000, -1400, "capital",
       "the Pale Flame Cathedral", 420, 0.8, 15.2, 390, "V-01"),
    _c("Hollowmere", "ODD", 820, 260, 402_000, -900, "lake",
       "ice fishing and the frozen lake markets", 610, 1.9, 14.6, 420, "V-02"),
    _c("Skarn", "ODD", 920, 80, 248_000, -700, "mountain",
       "the Skarn Reliquary", 880, -1.5, 15.8, 350, "V-03"),
]
CITY = {c.name: c for c in CITIES}


def cities_of(code):
    return [c for c in CITIES if c.nation == code]


def distance_leagues(a, b):
    a, b = CITY[a] if isinstance(a, str) else a, CITY[b] if isinstance(b, str) else b
    return round(math.hypot(a.x - b.x, a.y - b.y) / 2, 1)


def monthly_climate(city):
    """Mean temperature and rainfall for each of the 10 months (plus Hollowdays)."""
    temps, rains = [], []
    for m in range(10):
        # Coldest in Rime (month 1), warmest in Crest (month 6).
        phase = math.cos((m - 5) / 10 * 2 * math.pi)
        temps.append(round(city.mean_temp + city.temp_swing * phase, 1))
        wet = 1 + 0.35 * math.cos((m - 1) / 10 * 2 * math.pi)
        rains.append(int(city.rain / 10 * wet))
    return temps, rains


@dataclass
class Landmark:
    name: str
    city: str
    kind: str
    built: int
    description: str

    @property
    def slug(self):
        return slug(self.name)


LANDMARKS = [
    Landmark("The Nine Bridges", "Ostmere", "bridge", 12,
             "Nine stone bridges over the River Sallow, one for each province that signed the "
             "Concord. The ninth, Wardens' Bridge, was rebuilt in 288 CR after a flood."),
    Landmark("The Registry Tower", "Ostmere", "building", 190,
             "Seventeen storeys of filing rooms, said to hold a record of every business, "
             "birth, and boundary in the Concordat."),
    Landmark("Caddick Lock", "Caddick Ford", "canal", 144,
             "A flight of eleven locks lifting barges 38 ells over the Caddick escarpment."),
    Landmark("The Tarrow Canal", "Tarrow", "canal", 301,
             "A 62-league canal joining the Sallow to the Glass Sea. Its widening contract is "
             "the subject of an ongoing scandal."),
    Landmark("Silverrun Falls", "Silverrun", "waterfall", -9999,
             "A 71-ell waterfall that powered the first silver stamping mills."),
    Landmark("Wendmoor Standing Stones", "Wendmoor", "monument", -2000,
             "A ring of 23 stones of unknown origin. One stone, the Leaner, tilts north."),
    Landmark("Harthwick Lighthouse", "Harthwick", "lighthouse", 212,
             "A red-and-white striped lighthouse whose lamp flashes twice every nine seconds."),
    Landmark("The Ember Kilns", "Emberly", "industrial", 96,
             "Beehive kilns that produced the green Emberly glass of the third century."),
    Landmark("Quenby Great Clock", "Quenby", "clock", 256,
             "A clock with a dial for each moon. It has stopped only once, during the Ashfall."),
    Landmark("The Admiralty", "Brineholt", "building", 40,
             "Seat of the Saltmarch government, built of salvaged ship timbers."),
    Landmark("The Spire", "Saltspire", "lighthouse", -120,
             "A lighthouse older than the Republic. Its keeper posts are hereditary."),
    Landmark("The Deep Halls", "Harrowdeep", "hall", -870,
             "The carved halls beneath Harrowdeep, where the Moot of Holds meets."),
    Landmark("Frostgate Wall", "Frostgate", "wall", -290,
             "A wall across the only pass to Oddavar. Its gates open for 90 days a year."),
    Landmark("Stonemeet Moot Stones", "Stonemeet", "monument", -420,
             "Standing stones where clan disputes were once settled by oath."),
    Landmark("Lanternport Observatory", "Lanternport", "observatory", 118,
             "The oldest working observatory in Averra, where Pith's backward orbit was first "
             "measured."),
    Landmark("The Loom Hall", "Lanternport", "museum", 371,
             "Home of the first Loom, the thinking engine built by Temmet Aske."),
    Landmark("Vanehaven Weather Tower", "Vanehaven", "tower", 262,
             "A tower of 400 wind vanes used to forecast storms over the Glass Sea."),
    Landmark("Pale Flame Cathedral", "Vesk", "temple", -800,
             "The heart of the Oddavari faith, said to hold a flame that has burned for "
             "twelve centuries."),
]
