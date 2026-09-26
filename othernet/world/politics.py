"""The Concordat Assembly: delegates, bills, and recorded votes."""
from dataclasses import dataclass, field

from ..engine.rng import stream, slug
from .calendar import ADate, TODAY
from .names import Name, make_name
from .orgs import PARTIES, SEATS, PROVINCES
from .people import NOTABLE


@dataclass
class Delegate:
    id: str
    name: Name
    party: str
    province: str
    since: int
    committees: list = field(default_factory=list)
    office: str = ""
    person_id: str = ""


@dataclass
class Bill:
    id: str
    title: str
    sponsor: str  # delegate id
    introduced: ADate
    summary: str
    status: str  # "Enacted", "Defeated", "In committee", "Awaiting vote", "Withdrawn"
    vote_date: ADate = None
    votes: dict = field(default_factory=dict)  # delegate id -> yes/no/abstain/absent
    stance: dict = field(default_factory=dict)  # party -> probability of yes
    topic: str = ""
    readings: list = field(default_factory=list)

    @property
    def tally(self):
        t = {"yes": 0, "no": 0, "abstain": 0, "absent": 0}
        for v in self.votes.values():
            t[v] += 1
        return t


COMMITTEES = ["Canals and Waterways", "Registry and Records", "Treasury", "Weave and Looms",
              "Provinces", "Foreign Concerns", "Health and Hearth", "Agriculture"]

# Notable delegates: (person id, party, province, office)
SPECIAL = [
    ("maelis-ondraker", "civic-ledger", "Tarrowdale", "First Warden"),
    ("verity-ashford", "civic-ledger", "Tarrowdale", "Minister of Canals and Waterways"),
    ("dorran-whitby", "hearth-plough", "Wendmoor", "Leader of the Opposition"),
]
NAMED = [
    ("Linnet", "Crawley", "open-ford", "Sallowmark", "Deputy First Warden"),
    ("Harlan", "Mottram", "canalworkers", "Caddock", "Leader, Canalworkers' League"),
    ("Briony", "Fenshaw", "green-moor", "Wendmoor", "Chair, Canals and Waterways Committee"),
    ("Ambrose", "Whitholt", "civic-ledger", "Sallowmark", "Treasurer of the Concordat"),
    ("Odile", "Marchmont", "hearth-plough", "Gorsefield", "Shadow Treasurer"),
]


def _delegates():
    rng = stream("delegates")
    seats_left = dict(SEATS)
    out = []
    for pid, party, prov, office in SPECIAL:
        p = NOTABLE[pid]
        out.append(Delegate(slug(p.full), p.name, party, prov, rng.choice([399, 403, 407, 411]),
                            office=office, person_id=pid))
        seats_left[party] -= 1
    for g, f, party, prov, office in NAMED:
        n = Name(g, f, "VEY")
        out.append(Delegate(slug(n.full), n, party, prov, rng.choice([395, 399, 403, 407]),
                            office=office))
        seats_left[party] -= 1
    # fill the rest province by province, 10 per province
    per_prov = {prov: 10 for prov, _ in PROVINCES}
    for d in out:
        per_prov[d.province] -= 1
    pool = [p for p, n in seats_left.items() for _ in range(n)]
    rng.shuffle(pool)
    # rural parties lean to rural provinces
    rural = {"Wendmoor", "Gorsefield", "The Lowlands", "Silvermere"}
    pool.sort(key=lambda p: rng.random() + (0.6 if p == "hearth-plough" else 0))
    used = {d.name.full for d in out}
    provs = []
    for prov, _ in PROVINCES:
        provs += [prov] * per_prov[prov]
    provs.sort(key=lambda p: (p in rural) + rng.random() * 0.8)
    for party, prov in zip(pool, provs):
        n = make_name(rng, "VEY")
        while n.full in used:
            n = make_name(rng, "VEY")
        used.add(n.full)
        out.append(Delegate(slug(n.full), n, party, prov, rng.choice([391, 395, 399, 403, 407, 411])))
    for d in out:
        d.committees = rng.sample(COMMITTEES, rng.choice([1, 2, 2, 3]))
    fen = next(d for d in out if d.name.family == "Fenshaw")
    if "Canals and Waterways" not in fen.committees:
        fen.committees.insert(0, "Canals and Waterways")
    return out


DELEGATES = _delegates()
DELEGATE = {d.id: d for d in DELEGATES}


def _sponsor(family):
    return next(d.id for d in DELEGATES if d.name.family == family)


# fmt: off
_BILLS = [
    ("Registry (Paper to Plough) Act", "Ondraker", ADate(411, 2, 10), ADate(411, 4, 30),
     "Lets farmers file land records at any post office instead of travelling to a provincial "
     "registry.", {"civic-ledger": .98, "open-ford": .9, "hearth-plough": .6, "canalworkers": .7,
                   "green-moor": .8}, "registry"),
    ("Tarrow Canal (Widening) Act", "Ashford", ADate(411, 5, 3), ADate(411, 7, 21),
     "Authorises the widening of the Tarrow Canal for sea barges and a budget of 1.84 billion "
     "crowns.", {"civic-ledger": .97, "open-ford": .75, "hearth-plough": .55, "canalworkers": .9,
                 "green-moor": .0}, "canals"),
    ("Weave Access (Libraries) Act", "Crawley", ADate(411, 8, 1), ADate(411, 9, 20),
     "Requires every provincial library to offer free Weave access.",
     {"civic-ledger": .8, "open-ford": 1, "hearth-plough": .2, "canalworkers": .9,
      "green-moor": .9}, "weave"),
    ("Lock-keepers' Pay Act", "Mottram", ADate(411, 9, 2), ADate(412, 1, 22),
     "Raises the minimum pay of lock-keepers by one crown per shift.",
     {"civic-ledger": .35, "open-ford": .4, "hearth-plough": .1, "canalworkers": 1,
      "green-moor": .8}, "labour"),
    ("Moorland Peat (Protection) Act", "Fenshaw", ADate(411, 10, 11), ADate(412, 2, 30),
     "Bans new peat cutting on Wendmoor above 300 ells.", {"civic-ledger": .5, "open-ford": .7,
     "hearth-plough": .05, "canalworkers": .5, "green-moor": 1}, "environment"),
    ("Treasury (Budget 412) Act", "Whitholt", ADate(411, 10, 20), ADate(412, 1, 8),
     "Sets the Concordat budget for 412 CR at 612 billion crowns.", {"civic-ledger": 1,
     "open-ford": .95, "hearth-plough": 0, "canalworkers": .3, "green-moor": .2}, "treasury"),
    ("Slate Safety Standards Act", "Crawley", ADate(412, 3, 5), None,
     "Requires loom devices sold in Veyl to pass heat tests at an accredited guild house.",
     {}, "weave"),
    ("Canals Inquiry (Powers) Act", "Fenshaw", ADate(412, 5, 2), ADate(412, 5, 30),
     "Gives the Canals and Waterways Committee power to compel witnesses in the Tarrow Canal "
     "inquiry.", {"civic-ledger": .45, "open-ford": .9, "hearth-plough": .95, "canalworkers": .9,
                  "green-moor": 1}, "canals"),
    ("Hollowdays (Debt Forgiveness) Amendment Act", "Marchmont", ADate(412, 2, 14), ADate(412, 4, 3),
     "Raises the traditional Hollowdays debt forgiveness limit from one crown to five crowns.",
     {"civic-ledger": .3, "open-ford": .6, "hearth-plough": .9, "canalworkers": .95,
      "green-moor": .6}, "treasury"),
    ("Mining Safety (Cross-border Aid) Act", "Mottram", ADate(412, 7, 5), ADate(412, 7, 33),
     "Lets Concordat rescue crews cross into the Holds without a Moot writ after a mine "
     "collapse.", {"civic-ledger": .9, "open-ford": .95, "hearth-plough": .8, "canalworkers": 1,
                   "green-moor": .9}, "foreign"),
    ("Motion of No Confidence in the Minister of Canals", "Whitby", ADate(412, 8, 12), None,
     "A motion that the Assembly has no confidence in Verity Ashford. Vote scheduled for "
     "26 Gale 412.", {}, "canals"),
    ("Lowmarsh Fog Signals Act", None, ADate(411, 6, 6), ADate(411, 8, 8),
     "Requires fog bells at every Lowmarsh jetty.", {"*": .85}, "provinces"),
]
# fmt: on

FILLER_TOPICS = [
    ("{place} Bridge (Repair) Act", "Funds repairs to the old bridge at {place}.", "provinces"),
    ("{place} Market Charter Act", "Grants {place} a second weekly market day.", "provinces"),
    ("Weights and Measures (Ell Standard) Act", "Replaces the brass standard ell kept in the "
     "Registry with a glass one.", "registry"),
    ("Postal Rates Act", "Sets letter postage at 45 pennets for the first weight.", "treasury"),
    ("Cider Duty (Gorsefield) Act", "Halves the duty on cider sold at the Gorse Hollow Cider "
     "Fair.", "agriculture"),
    ("Eel Fisheries (Amendment) Act", "Closes the Lowmarsh eel season during Bloom.", "agriculture"),
    ("Lamplighters' Guild (Charter Renewal) Act", "Renews the Guild of Lamplighters' charter "
     "for fifty years.", "provinces"),
    ("Clockworks Heritage Act", "Lists the Quenby Great Clock as a protected work.", "provinces"),
    ("Sallow Flood Defences Act", "Funds new flood walls along the Sallow at Ostmere.", "canals"),
    ("Airship Mooring (Licensing) Act", "Creates licences for airship masts in cities.", "weave"),
    ("Loom Records (Retention) Act", "Requires Registry records kept on looms to be copied to "
     "paper every ten years.", "registry"),
    ("Tram Fares (Ostmere) Act", "Caps Ostmere tram fares at 60 pennets.", "provinces"),
]
PLACES = ["Tarrow", "Silverrun", "Wendmoor", "Harthwick", "Emberly", "Quenby", "Lowmarsh",
          "Caddick Ford", "Gorse Hollow"]


def _cast_votes(bill, rng):
    for d in DELEGATES:
        p = bill.stance.get(d.party, bill.stance.get("*", 0.5))
        r = rng.random()
        if r < 0.04:
            bill.votes[d.id] = "absent"
        elif r < 0.07:
            bill.votes[d.id] = "abstain"
        else:
            bill.votes[d.id] = "yes" if rng.random() < p else "no"


def _bills():
    rng = stream("bills")
    bills = []
    n = {411: 0, 412: 0}
    raw = []
    for title, fam, intro, vote, summary, stance, topic in _BILLS:
        raw.append((intro, title, fam, vote, summary, stance, topic))
    for i, (tmpl, summ, topic) in enumerate(FILLER_TOPICS):
        place = PLACES[i % len(PLACES)]
        intro = ADate(411 + (i % 2), rng.randint(1, 7 if i % 2 else 10), rng.randint(1, 36))
        vote = intro + rng.randint(20, 90)
        if vote > TODAY:
            vote = None
        stance = {p: rng.uniform(0.45, 0.95) for p in PARTIES}
        raw.append((intro, tmpl.format(place=place), None, vote, summ.format(place=place), stance,
                    topic))
    raw.sort(key=lambda r: r[0])
    for intro, title, fam, vote, summary, stance, topic in raw:
        n[intro.year] += 1
        bid = f"AB-{intro.year}-{n[intro.year]:03d}"
        sponsor = _sponsor(fam) if fam else rng.choice(DELEGATES).id
        b = Bill(bid, title, sponsor, intro, summary, "", vote, stance=stance, topic=topic)
        b.readings = [("First reading", intro), ("Committee stage", intro + rng.randint(5, 15))]
        if vote and vote <= TODAY:
            _cast_votes(b, stream("votes", bid))
            t = b.tally
            b.status = "Enacted" if t["yes"] > t["no"] else "Defeated"
            b.readings.append(("Final vote", vote))
        else:
            b.status = "Awaiting vote" if "Confidence" in title else "In committee"
        bills.append(b)
    return bills


BILLS = _bills()
BILL = {b.id: b for b in BILLS}
