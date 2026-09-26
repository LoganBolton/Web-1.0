"""People of Averra: hand-written notables plus a generated population."""
from dataclasses import dataclass, field

from ..engine.rng import stream, slug
from .calendar import ADate, TODAY
from .geo import CITIES, cities_of, CITY
from .names import Name, make_name, make_handle


@dataclass
class Person:
    id: str
    name: Name
    born: ADate
    died: ADate = None
    nation: str = "VEY"
    city: str = "Ostmere"
    occupation: str = ""
    bio: str = ""
    notable: bool = False
    tags: list = field(default_factory=list)
    handle: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def full(self):
        return self.name.full

    @property
    def slug(self):
        return slug(self.name.full)

    def age(self, on=TODAY):
        end = self.died or on
        years = end.year - self.born.year
        if (end.month, end.day) < (self.born.month, self.born.day):
            years -= 1
        return years

    @property
    def lifespan(self):
        if self.died:
            return f"{self.born.year}–{self.died.year} CR"
        return f"born {self.born.year} CR"


def N(given, family, culture):
    return Name(given, family, culture)


def D(y, m, d):
    return ADate(y, m, d)


# fmt: off
NOTABLES = [
    # ---- heads of state and politics ---------------------------------------
    Person("maelis-ondraker", N("Maelis", "Ondraker", "VEY"), D(361, 4, 9), None, "VEY", "Tarrow",
           "First Warden of the Concordat", "Leader of the Civic Ledger Party. Served as Warden of "
           "Tarrowdale province from 399 to 410 and won the Concordat election of 411 CR, taking "
           "office on 1 Loam 411. Known for her 'Paper to Plough' registry reforms.", True,
           ["politics", "civic-ledger"]),
    Person("oriel-casswater", N("Oriel", "Casswater", "SLT"), D(358, 7, 22), None, "SLT", "Gullhaven",
           "Tidemaster of the Saltmarch Republic", "A former captain of the merchant brig "
           "Kittiwake, elected Tidemaster by the Admiralty Council in 406 CR and re-elected in 410.",
           True, ["politics"]),
    Person("harrow-dagna", N("Dagna", "Harrow", "KHR"), D(369, 2, 14), None, "KHR", "Harrowdeep",
           "High Holdwarden of the Kethren Holds", "Chosen by the Moot of Holds in 1288 HR "
           "(408 CR). The first High Holdwarden from Clan Harrow in three generations.", True,
           ["politics"]),
    Person("iselle-marovane", N("Iselle", "Marovane", "PEL"), D(357, 9, 3), None, "PEL", "Lanternport",
           "Chancellor-Senator of the Pellucid Isles", "An astronomer who directed the Lanternport "
           "Observatory from 392 to 408 before being elected Chancellor-Senator in 409 CR.", True,
           ["politics", "astronomy"]),
    Person("skeld-varrakin", N("Skeld", "Varrakin", "ODD"), D(340, 1, 30), None, "ODD", "Vesk",
           "Hierarch of the Pale Flame", "Head of the Synod of the Pale Flame since 381 CR. Rarely "
           "seen in public outside Oddavar.", True, ["politics", "religion"]),
    Person("dorran-whitby", N("Dorran", "Whitby", "VEY"), D(370, 5, 11), None, "VEY", "Wendmoor",
           "Leader of the Hearth & Plough Party", "Leader of the opposition in the Concordat "
           "Assembly and delegate for Wendmoor. A former sheep farmer.", True,
           ["politics", "hearth-plough"]),
    Person("verity-ashford", N("Verity", "Ashford", "VEY"), D(372, 3, 28), None, "VEY", "Tarrow",
           "Minister of Canals and Waterways", "Minister of Canals since 411. Under scrutiny over "
           "the award of the Tarrow Canal widening contract to Gildmere Works.", True,
           ["politics", "civic-ledger", "canal-scandal"]),
    Person("tobiah-pimstead", N("Tobiah", "Pimstead", "VEY"), D(366, 10, 1), None, "VEY", "Ostmere",
           "Registrar General of the Concordat", "Head of the Concordat Registry since 402 CR.",
           True, ["civil-service"]),
    # ---- business ----------------------------------------------------------
    Person("sabine-marwick", N("Sabine", "Marwick", "VEY"), D(376, 6, 6), None, "VEY", "Ostmere",
           "Chief executive of Vantle", "Co-founded Vantle with Corwen Talley in 399 CR in a rented "
           "loft in Copperside. Became chief executive after Talley left in 406.", True,
           ["business", "vantle"]),
    Person("corwen-talley", N("Corwen", "Talley", "VEY"), D(374, 1, 19), None, "VEY", "Quenby",
           "Engineer and investor", "Co-founder of Vantle and designer of the first Vantle Slate. "
           "Left the company in 406 CR and now funds clockwork restoration in Quenby.", True,
           ["business", "vantle"]),
    Person("edric-hollowell", N("Edric", "Hollowell", "VEY"), D(365, 8, 30), None, "VEY", "Caddick Ford",
           "Founder of Bazaar", "Started Bazaar in 396 CR as a catalogue of second-hand loom "
           "parts. It is now the largest marketplace on the Weave.", True, ["business", "bazaar"]),
    Person("nerys-lanterre", N("Nerys", "Lanterre", "PEL"), D(377, 3, 2), None, "PEL", "Lanternport",
           "Co-founder of Lanthorn", "Built the Lanthorn search engine with Elio Duvaine as a "
           "graduate project at Lanternport University in 398 CR.", True, ["business", "lanthorn"]),
    Person("elio-duvaine", N("Elio", "Duvaine", "PEL"), D(376, 11, 4), None, "PEL", "Marrowby",
           "Co-founder of Lanthorn", "Co-creator of Lanthorn and author of the 'lantern rank' "
           "paper. Left Lanthorn in 407 and now teaches at Lanternport University.", True,
           ["business", "lanthorn", "academia"]),
    Person("garrick-stanmore", N("Garrick", "Stanmore", "VEY"), D(351, 2, 2), None, "VEY", "Ostmere",
           "Chair of Drovers' Bank", "Chair of Drovers' Bank since 395 CR.", True,
           ["business", "banking"]),
    Person("marra-keelworth", N("Marra", "Keelworth", "SLT"), D(368, 4, 17), None, "SLT", "Brineholt",
           "Chief executive of Emberline", "Runs Emberline, the Glass Sea ferry and airship "
           "operator, since 404 CR.", True, ["business", "emberline"]),
    Person("hester-brackley", N("Hester", "Brackley", "VEY"), D(360, 6, 21), None, "VEY", "Gorse Hollow",
           "Founder of The Copper Kettle", "Opened the first Copper Kettle tea room in Gorse Hollow "
           "in 389 CR.", True, ["business", "food"]),
    Person("coldforge-brokk", N("Brokk", "Coldforge", "KHR"), D(359, 9, 9), None, "KHR", "Cinderfell",
           "Chief of Coldforge Mining", "Head of Coldforge Mining, operator of the Deepshaft workings "
           "at Cinderfell.", True, ["business", "mining"]),
    # ---- science, history, mathematics ---------------------------------------
    Person("temmet-aske", N("Temmet", "Aske", "PEL"), D(322, 5, 12), D(391, 10, 2), "PEL", "Lanternport",
           "Inventor of the Loom", "Built the first Loom, a thinking engine of punched ribbons and "
           "brass reeds, at Lanternport University in 367 CR.", True, ["science", "history", "loom"]),
    Person("oswin-solavey", N("Oswin", "Solavey", "PEL"), D(81, 2, 20), D(152, 7, 7), "PEL", "Lanternport",
           "Astronomer", "First to measure the backward (retrograde) orbit of the small moon Pith, "
           "in 131 CR, from the new Lanternport Observatory.", True, ["science", "history", "astronomy"]),
    Person("idra-fenwick", N("Idra", "Fenwick", "VEY"), D(251, 1, 8), D(319, 3, 15), "VEY", "Emberly",
           "Inventor", "Inventor of the voltaic lamp (288 CR), which replaced whale-oil lamps across "
           "the Concordat within a generation.", True, ["science", "history"]),
    Person("deepwell-anvar", N("Anvar", "Deepwell", "KHR"), D(190, 6, 1), D(260, 2, 28), "KHR", "Harrowdeep",
           "Mathematician", "Kethren mathematician known for the Theorem of Nested Lodes.", True,
           ["math", "history"]),
    Person("ysolde-cresselle", N("Ysolde", "Cresselle", "PEL"), D(301, 8, 8), D(370, 10, 30), "PEL",
           "Shellcombe", "Mathematician", "Pellucidan mathematician who posed the Cresselle "
           "Conjecture on tidal primes in 339 CR.", True, ["math", "history"]),
    Person("wystan-merrowby", N("Wystan", "Merrowby", "VEY"), D(212, 3, 3), D(280, 5, 5), "VEY", "Ostmere",
           "Mathematician", "Discovered the Merrowby series for the ratio of a circle's rim to its "
           "span.", True, ["math", "history"]),
    Person("flint-gisla", N("Gisla", "Flint", "KHR"), D(330, 7, 14), None, "KHR", "Stonemeet",
           "Mathematician", "Professor emerita at the Harrowdeep Collegium. Known for the Flint "
           "Lemma on lattice walks.", True, ["math"]),
    Person("talvi-aubrel", N("Talvi", "Aubrel", "PEL"), D(380, 5, 25), None, "PEL", "Lanternport",
           "Mathematician", "Lecturer at Lanternport University who announced a proof of the "
           "Cresselle Conjecture in 411 CR. The proof is still being checked.", True, ["math"]),
    Person("rosamund-tallwick", N("Rosamund", "Tallwick", "VEY"), D(5, 1, 1), D(71, 9, 12), "VEY", "Ostmere",
           "First Registrar", "Author of 'The Book of Fords' and founder of the Concordat Registry.",
           True, ["history"]),
    Person("casso-saltonby", N("Casso", "Saltonby", "SLT"), D(12, 4, 4), D(60, 2, 19), "SLT", "Brineholt",
           "Revolutionary", "Leader of the Salt Revolt of 37 CR and first Tidemaster of Saltmarch.",
           True, ["history"]),
    Person("ravencairn-ingvar", N("Ingvar", "Ravencairn", "KHR"), D(210, 5, 5), D(262, 1, 17), "KHR",
           "Frostgate", "General", "Kethren commander in the Cinder War (241–246 CR).", True,
           ["history", "cinder-war"]),
    Person("aldric-fenmore", N("Aldric", "Fenmore", "VEY"), D(198, 9, 30), D(270, 6, 6), "VEY", "Ostmere",
           "First Warden", "First Warden during the Cinder War.", True, ["history", "cinder-war"]),
    # ---- culture -------------------------------------------------------------
    Person("morwen-reefley", N("Morwen", "Reefley", "SLT"), D(375, 2, 9), None, "SLT", "Wrackmouth",
           "Novelist", "Author of 'The Salt Ledger' (405) and 'Nine Fathoms Down' (410).", True,
           ["books"]),
    Person("hollis-thornby", N("Hollis", "Thornby", "VEY"), D(290, 4, 4), D(350, 8, 8), "VEY", "Wendmoor",
           "Poet", "Wrote 'Moor Songs' and the Concordat anthem 'Many Fords'.", True,
           ["books", "history"]),
    Person("anouk-belvaine", N("Anouk", "Belvaine", "PEL"), D(378, 6, 30), None, "PEL", "Marrowby",
           "Film director", "Director of 'Two Moons Over Marrowby' (409) and 'The Lampwright' (411).",
           True, ["film"]),
    Person("jago-tidewright", N("Jago", "Tidewright", "SLT"), D(385, 1, 12), None, "SLT", "Brineholt",
           "Actor", "Star of 'The Lampwright' and the stage run of 'The Salt Ledger'.", True,
           ["film"]),
    Person("nell-hedgecote", N("Nell", "Hedgecote", "VEY"), D(388, 10, 20), None, "VEY", "Caddick Ford",
           "Singer-songwriter", "Signed to Bellows Records. Her album 'Lock Eleven' was the "
           "best-selling record of 411 CR.", True, ["music"]),
    Person("theon-morvenne", N("Theon", "Morvenne", "PEL"), D(381, 3, 13), None, "PEL", "Lanternport",
           "Game designer", "Creator of the loom game 'Fathom' (403) and its sequel 'Fathom: Undertow' "
           "(410).", True, ["games"]),
    Person("delphine-estrande", N("Delphine", "Estrande", "PEL"), D(371, 7, 7), None, "PEL", "Marrowby",
           "Chef", "Chef of Pearl & Pith in Marrowby, known for smoked eel with sea-fennel.", True,
           ["food"]),
    Person("anvilmark-ketta", N("Ketta", "Anvilmark", "KHR"), D(389, 5, 18), None, "KHR", "Harrowdeep",
           "Vaultball player", "Captain of the Harrowdeep Hammers.", True, ["sport"]),
    Person("roscoe-brinecombe", N("Roscoe", "Brinecombe", "SLT"), D(390, 2, 26), None, "SLT", "Brineholt",
           "Vaultball player", "Striker for the Brineholt Gulls.", True, ["sport"]),
    # ---- bloggers and small web people ---------------------------------------
    Person("pascoe-keelmouth", N("Pascoe", "Keelmouth", "SLT"), D(349, 3, 1), None, "SLT", "Saltspire",
           "Keeper of the Spire", "Hereditary keeper of the Spire lighthouse at Saltspire and a "
           "prolific (and grumpy) diarist on the Weave.", True, ["blogger"]),
    Person("ulric-motley", N("Ulric", "Motley", "VEY"), D(363, 11, 11), None, "VEY", "Lowmarsh",
           "Pamphleteer", "Writes as 'Ossa Watcher'. Believes the moon Pith is artificial.", True,
           ["blogger"]),
    Person("wenna-larkfield", N("Wenna", "Larkfield", "VEY"), D(392, 4, 2), None, "VEY", "Harthwick",
           "Writer", "Keeps the blog 'Wren Writes' about walking, ferries, and small towns.", True,
           ["blogger"]),
]
# fmt: on

NOTABLE = {p.id: p for p in NOTABLES}

HEADS = {"VEY": "maelis-ondraker", "SLT": "oriel-casswater", "KHR": "harrow-dagna",
         "PEL": "iselle-marovane", "ODD": "skeld-varrakin"}

OCCUPATIONS = [
    "clerk", "canal engineer", "teacher", "baker", "loom-wright", "ferry pilot", "nurse",
    "miner", "shopkeeper", "tram driver", "accountant", "glassblower", "fisher", "farmer",
    "carpenter", "journalist", "student", "archivist", "brewer", "physician", "lawyer",
    "cartographer", "chemist", "tailor", "retired", "postal worker", "lamplighter",
    "clockmaker", "sailor", "surveyor", "librarian", "cook", "musician", "painter",
    "mechanic", "herbalist", "weaver", "architect", "beekeeper", "translator",
]

NATION_WEIGHTS = [("VEY", 48), ("SLT", 22), ("KHR", 9), ("PEL", 6), ("ODD", 1)]


def generate_population(n=4000):
    from ..engine.rng import pick_weighted
    rng = stream("population")
    people = []
    seen = set()
    for i in range(n):
        nat = pick_weighted(rng, NATION_WEIGHTS)
        name = make_name(rng, nat)
        while name.full in seen:
            name = make_name(rng, nat)
        seen.add(name.full)
        city = rng.choice(cities_of(nat))
        born = ADate(rng.randint(330, 396), rng.randint(1, 10), rng.randint(1, 36))
        p = Person(f"x{i:04d}-{slug(name.full)}", name, born, None, nat, city.name,
                   rng.choice(OCCUPATIONS))
        p.handle = make_handle(rng, name)
        people.append(p)
    # Handles must be unique across the Weave.
    handles = set()
    for p in people:
        h = p.handle
        k = 2
        while h in handles:
            h = f"{p.handle}{k}"
            k += 1
        p.handle = h
        handles.add(h)
    return people


def _set_heads():
    from .geo import NATIONS
    for code, pid in HEADS.items():
        NATIONS[code].head = pid


_set_heads()
