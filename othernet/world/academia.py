"""Lanternport University departments, staff, courses, and papers in the Annals."""
from dataclasses import dataclass, field

from ..engine.rng import stream, slug, pick_weighted
from .calendar import ADate, TODAY
from .names import make_name

DEPARTMENTS = [
    ("numerics", "Numerics", "The study of number, shape, and proof."),
    ("natural-philosophy", "Natural Philosophy", "Forces, heat, light, and voltaic currents."),
    ("loomcraft", "Loomcraft", "Looms, Weft, and the theory of ribbons."),
    ("astronomy", "Astronomy", "The two moons, the stars, and the Observatory."),
    ("navigation", "Navigation", "Tides, charts, and the sea roads."),
    ("history", "History", "The Concord, the Charter, and everything before."),
    ("letters", "Pellish Letters", "Language and literature of the Isles."),
    ("physic", "Physic", "Medicine and the care of the body."),
]

TOPICS = {
    "numerics": ["tidal primes", "lattice walks", "the Merrowby series", "nested lodes", "twelve-fold counting", "knots in ribbons"],
    "natural-philosophy": ["voltaic piles", "the colour of Emberly glass", "heat in deep mines", "fog over warm water", "sound in caverns"],
    "loomcraft": ["reed memory", "Weft compilers", "ribbon errors", "search by lanterns", "shuttle scheduling", "two-faced slates"],
    "astronomy": ["Pith's decaying orbit", "the Pith crossing of 412", "Ossa's librations", "meteor showers", "the Anvil star"],
    "navigation": ["tides at Tidewell", "fog signals", "airship routes", "the Glass Sea currents"],
    "history": ["the Salt Revolt", "the Cinder War", "the Ashfall", "the Charter of Colleges", "Registry ledgers"],
    "letters": ["Marcher dialect", "Kethric loanwords", "Hollis Thornby", "the Salt Ledger", "Oddic inscriptions"],
    "physic": ["miners' lungs", "fog fever", "seasickness on airships", "the Hollowdays and sleep"],
}


@dataclass
class Staff:
    id: str
    name: str
    dept: str
    title: str
    office: str
    interests: list
    since: int
    notable: str = ""


@dataclass
class Paper:
    id: str
    title: str
    authors: list
    dept: str
    volume: int
    issue: int
    pages: str
    received: ADate
    accepted: ADate
    abstract: str
    refs: list = field(default_factory=list)
    kind: str = "article"  # article, ribbon (preprint), comment
    status: str = ""


def _build():
    rng = stream("academia")
    staff = []
    named = [("talvi-aubrel", "Talvi Aubrel", "numerics", "Lecturer", ["tidal primes", "lattice walks"], 407),
             ("elio-duvaine", "Elio Duvaine", "loomcraft", "Reader", ["search by lanterns", "reed memory"], 407),
             ("mireille-solande", "Mireille Solande", "loomcraft", "Professor", ["Weft compilers"], 390),
             ("iselle-cresselle", "Iselle Cresselle", "astronomy", "Keeper of the Observatory", ["the Pith crossing of 412"], 409),
             ("sevrin-aubrande", "Sevrin Aubrande", "astronomy", "Lecturer", ["Pith's decaying orbit"], 402)]
    for sid, name, dept, title, interests, since in named:
        staff.append(Staff(sid, name, dept, title, f"{dept[:3].upper()} {rng.randint(100, 399)}", interests, since))
    titles = ["Professor", "Reader", "Lecturer", "Lecturer", "Tutor", "Research Fellow"]
    for dept, _, _ in DEPARTMENTS:
        for i in range(rng.randint(5, 9)):
            nat = pick_weighted(rng, [("PEL", 7), ("VEY", 2), ("SLT", 1), ("KHR", 1)])
            n = make_name(rng, nat).full
            staff.append(Staff(slug(n), n, dept, rng.choice(titles), f"{dept[:3].upper()} {rng.randint(100, 399)}",
                               rng.sample(TOPICS[dept], min(2, len(TOPICS[dept]))), rng.randint(370, 411)))
    papers = []
    vol0 = 80  # volume 80 = 404
    for y in range(404, 413):
        for issue in range(1, 5):
            when = ADate(y, issue * 2 + 1, 1)
            if when > TODAY:
                break
            page = 1
            for k in range(rng.randint(4, 7)):
                dept = rng.choice(DEPARTMENTS)[0]
                auth = [s.name for s in rng.sample([s for s in staff if s.dept == dept], rng.randint(1, 3))]
                topic = rng.choice(TOPICS[dept])
                t = rng.choice(["On {t}", "A note on {t}", "New measurements of {t}", "{T} reconsidered",
                                "Towards a theory of {t}", "What we know about {t}"]).format(t=topic, T=topic[0].upper() + topic[1:])
                npg = rng.randint(8, 30)
                rec = when - rng.randint(60, 300)
                pid = f"{vol0 + y - 404}.{issue}.{page}"
                papers.append(Paper(pid, t, auth, dept, vol0 + y - 404, issue, f"{page}–{page + npg - 1}", rec,
                                    rec + rng.randint(30, 120), f"We study {topic}. " + rng.choice([
                                        "Our results agree with earlier work.", "We find a small but real effect.",
                                        "Earlier claims do not survive closer measurement.", "Further work is needed."])))
                page += npg
    # the Cresselle papers
    papers.append(Paper("ribbon-411-0412", "A proof of the Cresselle Conjecture", ["Talvi Aubrel"], "numerics", 0, 0, "1–41",
                        ADate(411, 10, 30), None, "We prove that there are infinitely many tidal primes, as conjectured by "
                        "Ysolde Cresselle in 339. The proof proceeds by three lemmas.", kind="ribbon",
                        status="Superseded by version 2. A gap in Lemma 3 was identified by Flint (412)."))
    papers.append(Paper("88.2.1", "A gap in the third lemma of Aubrel's proof", ["Gisla Flint"], "numerics", 88, 2, "1–6",
                        ADate(412, 4, 10), ADate(412, 4, 16), "We show that Lemma 3 of Aubrel's proof assumes the conclusion "
                        "it is used to prove.", kind="comment", refs=["ribbon-411-0412"]))
    papers.append(Paper("ribbon-412-0805", "A proof of the Cresselle Conjecture (version 2)", ["Talvi Aubrel"], "numerics", 0, 0, "1–58",
                        ADate(412, 8, 5), None, "A revised proof. Lemma 3 is replaced by an argument using the Flint Lemma on "
                        "lattice walks. We thank G. Flint.", kind="ribbon", refs=["ribbon-411-0412", "88.2.1"],
                        status="Under formal review by the Guild of Numerists."))
    return staff, papers


STAFF, PAPERS = _build()
