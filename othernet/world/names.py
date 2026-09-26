"""Culture-aware name generation.

Naming conventions differ by nation on purpose:

* Veyl: given name, family name ("Aldric Fenwick").
* Saltmarch: given name, house name ("Corra Tidewell").
* Kethren: clan name FIRST, then given name ("Harrow Dagna"). Addressed by
  given name. Sorted by clan.
* Pellucid: given name, family name, often with a collegiate suffix.
* Oddavar: given name + parent's name + "-kin" ("Skeld Varrakin").
"""
from dataclasses import dataclass

VEY_GIVEN = [
    "Aldric", "Maelis", "Corwen", "Tamsin", "Edric", "Hollis", "Isra", "Joss", "Wenna",
    "Brannic", "Odile", "Perrin", "Rosamund", "Ansel", "Linnet", "Garrick", "Fenna",
    "Tobiah", "Merrit", "Sabine", "Alder", "Clemence", "Dorran", "Elspeth", "Idony",
    "Jory", "Kestrel", "Lorne", "Maud", "Nell", "Osric", "Petra", "Rowan", "Sorrel",
    "Thane", "Ursel", "Verity", "Wystan", "Anneke", "Bertram", "Cressida", "Dunstan",
    "Ember", "Florian", "Gwendolyn", "Harlan", "Ivo", "Juniper", "Konrad", "Lettice",
    "Mabyn", "Neville", "Orla", "Piers", "Quenna", "Radley", "Selwyn", "Tilde",
    "Ulric", "Vesna", "Warrick", "Yarrow", "Zelda", "Hester", "Ambrose", "Briony",
]
VEY_SUR_A = ["Ond", "Fen", "Hol", "Carr", "Ash", "Brack", "Whit", "Mar", "Tall", "Hedge",
             "Stan", "Gild", "Rook", "Thorn", "Wex", "Cald", "Pim", "Sall", "Mott", "Blyth",
             "Dun", "Hask", "Lark", "Quen", "Ver", "Bram", "Crane", "Merrow"]
VEY_SUR_B = ["raker", "wick", "low", "more", "ford", "by", "well", "ham", "ton", "ley",
             "bright", "wood", "shaw", "holt", "stead", "cote", "ridge", "field", "worth",
             "mere", "hurst", "den"]

SLT_GIVEN = [
    "Corra", "Oriel", "Marra", "Bex", "Casso", "Nerine", "Delph", "Halyard", "Isolde",
    "Jessamy", "Kit", "Lowen", "Morwen", "Nessa", "Pascoe", "Ren", "Sennen", "Tamar",
    "Ysella", "Zennor", "Arlo", "Branoc", "Cadan", "Demelza", "Elowen", "Fowey", "Gwyn",
    "Hedra", "Jago", "Kerra", "Lamorna", "Mawgan", "Nance", "Penrose", "Roscoe", "Tressa",
    "Wenlow", "Anders", "Brisa", "Calla", "Dory", "Finnick", "Gael", "Maris",
]
SLT_SUR_A = ["Tide", "Salt", "Keel", "Gull", "Brine", "Wrack", "Sound", "Reef", "Tern",
             "Spray", "Kelp", "Mast", "Cass", "Shoal", "Fathom", "Skerry", "Harbour", "Cove"]
SLT_SUR_B = ["well", "water", "worth", "combe", "by", "er", "son", "ling", "ard", "mouth",
             "wright", "man", "ley", "hithe"]

KHR_GIVEN = [
    "Dagna", "Brannoc", "Hilde", "Orsk", "Venna", "Maerk", "Gisla", "Rurik", "Tove",
    "Eskel", "Bodil", "Anvar", "Ketta", "Holm", "Idun", "Sigrun", "Vard", "Yrsa", "Stig",
    "Asta", "Brokk", "Dalla", "Egil", "Frida", "Grim", "Halla", "Ingvar", "Jorun",
    "Kolbein", "Liv", "Magna", "Njal", "Oda", "Ragna", "Sten", "Thora", "Ulla", "Vigdis",
]
KHR_CLANS = [
    "Harrow", "Ironsvale", "Cinder", "Deepwell", "Greystone", "Anvilmark", "Ashkettle",
    "Coldforge", "Emberhall", "Flint", "Ravencairn", "Slatebrook", "Thornhelm", "Underhill",
    "Veinfinder", "Blackmere", "Copperlode", "Hammerfall", "Orebright", "Stonemeet",
]

PEL_GIVEN = [
    "Iselle", "Liora", "Maren", "Oriane", "Talvi", "Sevrin", "Aurel", "Cassia", "Elio",
    "Nerys", "Ondine", "Perrault", "Quilla", "Renne", "Sabel", "Theon", "Ysolde", "Vaelin",
    "Mireille", "Esme", "Anouk", "Bastien", "Celestin", "Delphine", "Emeric", "Faye",
    "Gilles", "Hyacinth", "Ilan", "Jolie", "Lucan", "Mael", "Noemi", "Oswin", "Paz",
]
PEL_SUR_A = ["Mar", "Lan", "Sol", "Cres", "Du", "Au", "Vir", "Est", "Mor", "Bel", "Cor",
             "Lis", "Val", "Ser", "Tal", "Oss"]
PEL_SUR_B = ["ovane", "terre", "avey", "selle", "vaine", "brel", "eaux", "rande", "venne",
             "aire", "ine", "ande", "oux", "elle"]

ODD_GIVEN = [
    "Skeld", "Varra", "Ingra", "Hasko", "Olm", "Thyra", "Rusk", "Eyvind", "Gudra", "Kalle",
    "Maeva", "Sorn", "Ulf", "Yngva", "Arnor", "Brynja", "Dag", "Hrefna", "Solvi", "Torka",
]


@dataclass
class Name:
    given: str
    family: str
    culture: str  # VEY SLT KHR PEL ODD

    @property
    def full(self):
        if self.culture == "KHR":
            return f"{self.family} {self.given}"
        return f"{self.given} {self.family}"

    @property
    def sort_key(self):
        return (self.family, self.given)

    @property
    def formal(self):
        """How the person would be referred to on second mention in the press."""
        if self.culture == "KHR":
            return self.given  # Kethren are addressed by given name
        return self.family

    def __str__(self):
        return self.full


def make_name(rng, culture, given=None):
    if culture == "VEY":
        g = given or rng.choice(VEY_GIVEN)
        f = rng.choice(VEY_SUR_A) + rng.choice(VEY_SUR_B)
    elif culture == "SLT":
        g = given or rng.choice(SLT_GIVEN)
        f = rng.choice(SLT_SUR_A) + rng.choice(SLT_SUR_B)
    elif culture == "KHR":
        g = given or rng.choice(KHR_GIVEN)
        f = rng.choice(KHR_CLANS)
    elif culture == "PEL":
        g = given or rng.choice(PEL_GIVEN)
        f = rng.choice(PEL_SUR_A) + rng.choice(PEL_SUR_B)
    else:
        g = given or rng.choice(ODD_GIVEN)
        f = rng.choice(ODD_GIVEN).rstrip("a") + "kin"
    return Name(g, f, culture)


USER_WORDS = ["moss", "kettle", "gull", "lantern", "tide", "ember", "slate", "ferry", "owl",
              "anvil", "reed", "brine", "cinder", "quill", "loom", "pith", "ossa", "fog",
              "rook", "vault", "copper", "sprocket", "hollow", "marsh", "thistle", "wick",
              "barrow", "gale", "rime", "loam", "crest", "sheaf", "mire", "dusk", "pip"]


def make_handle(rng, name=None):
    style = rng.randrange(6)
    w1, w2 = rng.sample(USER_WORDS, 2)
    if name and style == 0:
        return f"{name.given.lower()}_{name.family.lower()[:4]}{rng.randrange(10, 99)}"
    if name and style == 1:
        return f"{name.given.lower()}{rng.randrange(1, 999)}"
    if style == 2:
        return f"{w1}{w2}"
    if style == 3:
        return f"{w1}_{w2}_{rng.randrange(100)}"
    if style == 4:
        return f"x{w1}x"
    return f"{w1.capitalize()}{w2.capitalize()}{rng.randrange(1, 9)}"
