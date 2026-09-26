"""The long history of Averra, as the encyclopedias tell it."""
from dataclasses import dataclass, field

from ..engine.rng import slug


@dataclass
class Event:
    year: int
    title: str
    text: str
    tags: list = field(default_factory=list)
    people: list = field(default_factory=list)
    end_year: int = None
    place: str = ""

    @property
    def slug(self):
        return slug(self.title)

    @property
    def span(self):
        if self.end_year:
            return f"{self.year}–{self.end_year} CR"
        return f"{self.year} CR"


# fmt: off
EVENTS = [
    Event(-880, "Founding of Harrowdeep", "Clan Harrow and Clan Ironsvale cut the first hall "
          "into the Spine at Harrowdeep. The Kethren still count their years from this day.",
          ["kethren", "founding"], place="Harrowdeep"),
    Event(-120, "Lighting of the Spire", "The first recorded lighting of the Spire at Saltspire. "
          "Its keepers have been drawn from the Keelmouth family ever since.", ["saltmarch"],
          place="Saltspire"),
    Event(0, "Treaty of the Nine Fords", "Nine river provinces sign the Concord at the fords of "
          "the Sallow, founding the Concordat of Veyl. Year 0 of the Concord Reckoning.",
          ["veyl", "founding"], place="Ostmere"),
    Event(9, "Founding of the Registry", "Rosamund Tallwick opens the first Registry in a "
          "tannery loft in Ostmere, recording the boundaries of the nine provinces.",
          ["veyl", "registry"], ["rosamund-tallwick"], place="Ostmere"),
    Event(37, "The Salt Revolt", "Saltworkers of Brineholt, led by Casso Saltonby, throw off "
          "Concordat salt taxes and declare the Saltmarch Republic.",
          ["saltmarch", "founding", "war"], ["casso-saltonby"], place="Brineholt"),
    Event(118, "Founding of Lanternport", "Scholars fleeing the Concordat's book levy found "
          "Lanternport and its Observatory on the largest of the Pellucid Isles.",
          ["pellucid", "founding", "astronomy"], place="Lanternport"),
    Event(131, "Measurement of Pith's orbit", "Oswin Solavey shows that the small moon Pith "
          "circles Averra backwards, opposite to Ossa, completing a circuit every 7 days and 11 hours.",
          ["astronomy", "science"], ["oswin-solavey"], place="Lanternport"),
    Event(154, "Charter of Colleges", "The Pellucid Isles become a collegiate republic governed "
          "by a Senate of its universities.", ["pellucid", "founding"], place="Lanternport"),
    Event(203, "The Ashfall", "An eruption of Mount Corve darkens the skies for six years. "
          "Harvests fail across Veyl and the Great Clock of Quenby stops for the only time "
          "in its history.", ["disaster", "veyl"], end_year=209, place="Quenby"),
    Event(211, "Founding of Drovers' Bank", "A lending house for cattle drovers opens on the "
          "Sallow road outside Ostmere.", ["business", "veyl"], place="Ostmere"),
    Event(241, "The Cinder War", "A war between the Concordat and the Kethren Holds over the "
          "Cinderfell coal seams. It ended with the Peace of Stonemeet, which gave the seams to "
          "the Holds in exchange for free passage on the Sallow.", ["war", "kethren", "veyl"],
          ["ravencairn-ingvar", "aldric-fenmore"], end_year=246, place="Cinderfell"),
    Event(246, "Peace of Stonemeet", "Ends the Cinder War. Signed at the Moot Stones of "
          "Stonemeet on 12 Sheaf 246.", ["war", "treaty"], place="Stonemeet"),
    Event(288, "The voltaic lamp", "Idra Fenwick demonstrates a lamp lit by a voltaic pile "
          "in Emberly. Within forty years whale-oil lamps disappear from Veyl.", ["science"],
          ["idra-fenwick"], place="Emberly"),
    Event(301, "Tarrow Canal opens", "The 62-league Tarrow Canal links the Sallow to the "
          "Glass Sea.", ["veyl", "engineering"], place="Tarrow"),
    Event(331, "The first wire", "A signalling wire is laid under the Glass Sea between "
          "Harthwick and Lanternport. Messages cross in minutes instead of days.",
          ["science", "communication"], place="Harthwick"),
    Event(339, "Cresselle Conjecture posed", "Ysolde Cresselle conjectures that there are "
          "infinitely many tidal primes.", ["math"], ["ysolde-cresselle"], place="Shellcombe"),
    Event(367, "The first Loom", "Temmet Aske completes the first Loom, a thinking engine of "
          "punched ribbons and brass reeds, at Lanternport University.", ["science", "loom"],
          ["temmet-aske"], place="Lanternport"),
    Event(371, "Loom Hall opens", "Lanternport opens the Loom Hall to house Aske's engine.",
          ["loom", "pellucid"], place="Lanternport"),
    Event(383, "Weft language published", "The Guild of Weft Programmers publishes the first "
          "specification of Weft, a language for instructing looms.", ["loom", "weft"]),
    Event(390, "Open Weave Charter", "The five nations (Oddavar abstaining) agree to link "
          "their loom networks into a single Weave, open to the public.", ["weave", "treaty"]),
    Event(396, "Bazaar founded", "Edric Hollowell starts Bazaar in Caddick Ford.",
          ["business", "weave"], ["edric-hollowell"], place="Caddick Ford"),
    Event(398, "Lanthorn launched", "Nerys Lanterre and Elio Duvaine launch Lanthorn, the first "
          "search engine to rank pages by how many lanterns (links) point to them.",
          ["business", "weave"], ["nerys-lanterre", "elio-duvaine"], place="Lanternport"),
    Event(399, "Vantle founded", "Sabine Marwick and Corwen Talley found Vantle in Ostmere.",
          ["business"], ["sabine-marwick", "corwen-talley"], place="Ostmere"),
    Event(404, "Brineholt Harbour Fire", "A fire in the Rope Walk spreads to the harbour, "
          "destroying 41 ships and the old Fishmarket on 19 Blaze 404.", ["disaster", "saltmarch"],
          place="Brineholt"),
    Event(409, "The first Slate", "Vantle releases the Slate, a handheld loom with a glass face.",
          ["business", "loom"], place="Ostmere"),
    Event(411, "Concordat election of 411", "The Civic Ledger Party wins 38 of 90 seats and "
          "forms a coalition with Open Ford. Maelis Ondraker becomes First Warden.",
          ["veyl", "politics"], ["maelis-ondraker"], place="Ostmere"),
]
# fmt: on

TOPICS = {
    "Ossa": "The larger of Averra's two moons. It circles Averra in the ordinary direction "
            "every 29 days and 6 hours. Its phases set the rhythm of the Saltmarch tides.",
    "Pith": "The smaller moon. Pith orbits backwards (retrograde) every 7 days and 11 hours, "
            "so it rises in the west. Its orbit was first measured by Oswin Solavey in 131 CR.",
    "The Weave": "The linked loom network spanning Averra, opened to the public by the Open "
                 "Weave Charter of 390 CR. Sites are named by tended domains such as .ves "
                 "(commerce), .fol (folk and personal), .hal (halls of learning), .gld (guilds), "
                 ".wir (news wires), and national domains (.vey, .slt, .khr, .pel, .odd).",
    "Vaultball": "A team sport played by two sides of nine on a sunken pitch, the 'vault'. "
                 "Points are scored by landing the ball on the opposing rim (3 points) or in "
                 "the well (5 points).",
    "The Loom": "A thinking engine. The first was built by Temmet Aske in 367 CR. Modern looms "
                "are programmed in Weft.",
    "Hollowdays": "The five days at the end of each year that belong to no month. Most work "
                  "stops, and debts are traditionally forgiven below one crown.",
    "Tidal prime": "A prime number p such that p + 12 is also prime and the digits of p sum "
                   "to a multiple of three plus one. The Cresselle Conjecture says there are "
                   "infinitely many.",
    "The Registry": "The Concordat Registry in Ostmere keeps records of every company, deed, "
                    "and birth in Veyl. Its records are public on registry.vey.",
    "Leagues and ells": "Averra measures length in ells (a little over a metre) and leagues "
                        "(4,000 ells). Weight is measured in weights (wt) of about half a "
                        "kilogram. Temperature is in degrees on the Harl scale.",
    "Tally": "The currency of Saltmarch. One tally is twelve bits. Prices are written like "
             "4t 7b (four tallies and seven bits).",
}
