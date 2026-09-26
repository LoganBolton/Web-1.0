"""News stories of 412 CR.

Hand-written stories carry the main storylines of the year. Different outlets
tell the same story differently, and sometimes they get the numbers wrong.
The canonical truth lives in `truth` so evals can check against it.
"""
from dataclasses import dataclass, field

from ..engine.rng import stream, slug
from .calendar import ADate, TODAY
from .sports import MATCHES, TEAM, PLAYER, standings
from .econ import PRICES, trading_days
from .orgs import COMPANIES


@dataclass
class Story:
    id: str
    date: ADate
    section: str
    headline: str
    dek: str
    paras: list
    tags: list = field(default_factory=list)
    outlets: tuple = ("courier", "tidings")
    variants: dict = field(default_factory=dict)  # outlet -> {headline, dek, paras}
    truth: dict = field(default_factory=dict)
    image: str = ""  # an image kind for the svg generator
    byline: dict = field(default_factory=dict)  # outlet -> reporter name

    def for_outlet(self, outlet):
        v = self.variants.get(outlet, {})
        return {"headline": v.get("headline", self.headline), "dek": v.get("dek", self.dek),
                "paras": v.get("paras", self.paras)}

    @property
    def slug(self):
        return slug(self.headline)[:70].strip("-")


def S(date, section, headline, dek, paras, **kw):
    sid = f"{date.iso()}-{slug(headline)[:40].strip('-')}"
    return Story(sid, date, section, headline, dek, paras, **kw)


d = ADate

# fmt: off
STORIES = [
    # ---------------- Tarrow Canal affair ------------------------------------------
    S(d(412, 2, 4), "politics", "Gildmere Works wins Tarrow Canal widening contract",
      "The 1.84 billion crown contract is the largest ever awarded by the Ministry of Canals.",
      ["The Ministry of Canals and Waterways has awarded the contract to widen the Tarrow Canal to "
       "Gildmere Works of Tarrow, Minister Verity Ashford announced on Plowday.",
       "The contract, worth 1.84 billion crowns over nine years, will deepen the canal to take sea "
       "barges of up to 600 tons between the Sallow and the Glass Sea.",
       "Three firms bid for the work. Gildmere's bid was not the lowest: a joint bid from "
       "Keelwright Shipyards and Silverrun Refining came in at 1.71 billion crowns.",
       "\"Gildmere has built more locks than anyone in the Concordat,\" said Ashford. \"This was "
       "a decision about quality.\""],
      tags=["canal-scandal", "gildmere", "verity-ashford"], outlets=("courier", "tidings", "crier"),
      truth={"contract_value_cr": 1_840_000_000, "rival_bid_cr": 1_710_000_000},
      variants={"crier": {"headline": "CANAL CASH BONANZA FOR TARROW BUILDERS",
                          "dek": "Nearly two billion crowns - and who's counting?",
                          "paras": ["Gildmere Works has scooped a mind-boggling 1.8 BILLION crowns "
                                    "to widen the Tarrow Canal, and some of our readers smell a rat.",
                                    "A cheaper bid from a Saltmarch shipbuilder was turned down flat. "
                                    "The Crier asks: WHY?"]}},
      image="canal"),
    S(d(412, 4, 20), "politics", "Canal minister's sister married to Gildmere chief",
      "The Courier has learned that Osric Gildmere, head of Gildmere Works, is Verity Ashford's "
      "brother-in-law.",
      ["Osric Gildmere, chief executive of the firm awarded the Tarrow Canal contract, is married to "
       "Maud Ashford, the sister of Minister of Canals Verity Ashford, the Courier can reveal.",
       "Neither the Ministry nor Gildmere Works disclosed the family tie when the contract was "
       "awarded on 4 Thaw.",
       "A spokesperson for the minister said the relationship was \"well known in Tarrow\" and "
       "that the minister \"played no part in scoring the bids\".",
       "Shares in Gildmere Works fell sixteen per cent on the Brineholt Exchange after the report."],
      tags=["canal-scandal", "gildmere", "verity-ashford"], outlets=("courier", "tidings", "crier"),
      truth={"brother_in_law": "Osric Gildmere", "sister": "Maud Ashford"}, image="portrait",
      variants={"tidings": {"headline": "Veyl canal contract went to minister's family, says Courier",
                            "paras": ["The Ostmere Courier reports that the head of Gildmere Works, "
                                      "Osric Gildmere, is married to the sister of the Veylish "
                                      "Minister of Canals.",
                                      "Keelwright Shipyards of Gullhaven, whose cheaper bid lost, "
                                      "said it was \"reviewing its options\"."]}}),
    S(d(412, 5, 2), "politics", "Assembly opens inquiry into Tarrow Canal contract",
      "Green Moor's Briony Fenshaw will chair the Canals and Waterways Committee inquiry.",
      ["The Concordat Assembly's Canals and Waterways Committee has opened an inquiry into the award "
       "of the Tarrow Canal widening contract.",
       "The committee chair, Briony Fenshaw of Green Moor, has introduced a bill to give the "
       "committee power to compel witnesses.",
       "\"Every crown of this contract belongs to the public,\" Fenshaw said."],
      tags=["canal-scandal", "assembly"], outlets=("courier",)),
    S(d(412, 6, 30), "politics", "Registry filings show hidden stake in Gildmere",
      "A company run by the minister's sister owned twelve per cent of Gildmere Works.",
      ["Filings at the Concordat Registry show that Sallow Fen Holdings, a company whose sole "
       "director is Maud Ashford, owned twelve per cent of Gildmere Works when the canal contract "
       "was awarded.",
       "The filings, lodged in 409 CR, were found by readers of the Courier who searched the "
       "Registry's public records.",
       "Sallow Fen Holdings was registered at an address on Canalside, Tarrow. It has no "
       "employees."],
      tags=["canal-scandal", "registry"], outlets=("courier", "tidings", "crier"),
      truth={"holding_company": "Sallow Fen Holdings", "stake_pct": 12},
      variants={"crier": {"headline": "MINISTER'S SIS IN SECRET CANAL STAKE",
                          "paras": ["It's all in the family! A shadowy company run by Maud Ashford "
                                    "owned a FIFTH of the canal builders, The Crier can reveal.",
                                    "Sallow Fen Holdings has NO staff and NO office."]}}),
    S(d(412, 8, 11), "politics", "Ashford tells inquiry she knew nothing of sister's stake",
      "The minister faced four hours of questions from the Canals Committee.",
      ["Verity Ashford told the Canals and Waterways Committee that she had \"no knowledge "
       "whatsoever\" of her sister's shareholding in Gildmere Works.",
       "Asked by chair Briony Fenshaw why the family tie had not been declared, Ashford said the "
       "Ministry's rules only required declarations for spouses and children.",
       "The Hearth & Plough leader, Dorran Whitby, has tabled a motion of no confidence in the "
       "minister. The vote is scheduled for 26 Gale."],
      tags=["canal-scandal", "assembly", "verity-ashford"], outlets=("courier", "tidings", "crier"),
      truth={"no_confidence_vote": "26 Gale 412"}),
    # ---------------- Deepshaft 9 -------------------------------------------------
    S(d(412, 6, 22), "world", "Miners trapped after collapse at Cinderfell",
      "A roof fall in Coldforge Mining's Deepshaft 9 has cut off a crew of miners.",
      ["A section of roof collapsed in the Deepshaft 9 workings at Cinderfell early on Hearthday, "
       "trapping a crew of miners about 600 ells below ground.",
       "Coldforge Mining said fourteen miners were unaccounted for.",
       "Rescue crews from Harrowdeep and Stonemeet are drilling towards a refuge chamber where the "
       "miners are believed to be sheltering."],
      tags=["deepshaft", "coldforge", "kethren"], outlets=("courier", "tidings", "crier"),
      truth={"trapped": 16, "depth_ells": 600},
      variants={
          "tidings": {"paras": ["Seventeen miners are trapped after a roof fall at Coldforge "
                                "Mining's Deepshaft 9 pit in Cinderfell, according to the Holds' "
                                "mining office.",
                                "The collapse happened at the 600-ell level at about six in the "
                                "morning.",
                                "A Saltmarch rescue team has been offered but the Moot of Holds "
                                "has not yet granted it passage."]},
          "crier": {"headline": "DOZENS ENTOMBED IN KETHREN DEATH PIT",
                    "paras": ["Dozens of miners are feared trapped deep under the mountains after "
                              "a horror collapse at a Kethren coal pit.",
                              "Locals say the pit was \"a disaster waiting to happen\"."]}},
      image="mine"),
    S(d(412, 6, 28), "world", "All sixteen Cinderfell miners brought to the surface",
      "The miners spent six days in a refuge chamber before rescuers broke through.",
      ["All sixteen miners trapped in Deepshaft 9 at Cinderfell were brought to the surface alive "
       "on Kettleday, six days after the roof fall.",
       "Rescuers led by Greystone Magna of the Harrowdeep Mine Rescue broke into the refuge "
       "chamber at 04:40. The last miner reached the surface at 09:15.",
       "Earlier reports, including in this paper, gave the number trapped as fourteen. Coldforge "
       "Mining said two contractors had not been on its shift list.",
       "The Moot of Holds has ordered an inquiry."],
      tags=["deepshaft", "coldforge", "kethren"], outlets=("courier", "tidings"),
      truth={"trapped": 16, "rescue_leader": "Greystone Magna", "days": 6},
      variants={"tidings": {"paras": ["All sixteen miners trapped at Deepshaft 9 have been "
                                      "rescued, the Holds' mining office said on Kettleday.",
                                      "The rescue was led by Greystone Magna. The miners had "
                                      "survived on the refuge chamber's water barrels.",
                                      "Our earlier figure of seventeen was supplied by the mining "
                                      "office, which has since corrected it."]}}),
    S(d(412, 8, 9), "world", "Moot fines Coldforge 4.2 million marks over Deepshaft 9",
      "The Moot inquiry found the company had ignored warnings about roof bolts.",
      ["The Moot of Holds has fined Coldforge Mining 4.2 million marks after finding that the "
       "company ignored three written warnings about corroded roof bolts in Deepshaft 9.",
       "The ruling, delivered at Harrowdeep, orders the company to replace all roof bolts in "
       "Deepshaft workings older than twenty years."],
      tags=["deepshaft", "coldforge", "kethren"], outlets=("courier", "tidings"),
      truth={"fine_mk": 4_200_000, "warnings": 3}),
    # ---------------- Vantle -------------------------------------------------------
    S(d(412, 7, 3), "business", "Vantle unveils the Slate 7",
      "The new Slate has a second glass face on the back and ships on 1 Gale.",
      ["Vantle has unveiled the Slate 7 at its Copperside assembly hall in Ostmere.",
       "The Slate 7 will cost 1,299 crowns with 64 weaves of memory and 1,549 crowns with 128. "
       "It goes on sale on 1 Gale.",
       "Chief executive Sabine Marwick called it \"the Slate we always meant to make\"."],
      tags=["vantle", "slate"], outlets=("courier", "tidings"),
      truth={"price_64": 1299, "price_128": 1549, "release": "1 Gale 412"}, image="slate"),
    S(d(412, 8, 14), "business", "Vantle recalls Slate 7 chargers after overheating reports",
      "Owners are asked to stop using chargers with model number VC-7A.",
      ["Vantle has recalled the charger supplied with the Slate 7 after reports that it can "
       "overheat. Owners of chargers marked VC-7A should stop using them.",
       "Replacement chargers, marked VC-7B, will be sent free of charge. Vantle said 212 reports "
       "of overheating had been received and no one had been hurt."],
      tags=["vantle", "slate", "recall"], outlets=("courier", "tidings", "crier"),
      truth={"recalled_model": "VC-7A", "replacement_model": "VC-7B", "reports": 212},
      variants={"crier": {"headline": "SLATE OF FLAMES! Chargers recalled",
                          "paras": ["Vantle's shiny new Slate 7 is too hot to handle! The "
                                    "company has pulled its chargers after HUNDREDS of reports."]}}),
    # ---------------- Mathematics --------------------------------------------------
    S(d(412, 4, 18), "science", "Gap found in proof of Cresselle Conjecture",
      "Gisla Flint says a key step in Talvi Aubrel's proof does not hold.",
      ["The mathematician Flint Gisla has found a gap in Talvi Aubrel's proposed proof of the "
       "Cresselle Conjecture, the 73-year-old problem about tidal primes.",
       "Aubrel, a lecturer at Lanternport University, posted the proof on 30 Dusk 411.",
       "Flint says the proof's third lemma assumes what it sets out to show. Aubrel has said she "
       "will post a correction."],
      tags=["math", "cresselle"], outlets=("courier", "lodestone")),
    S(d(412, 8, 5), "science", "Aubrel posts revised Cresselle proof",
      "The Guild of Numerists has placed the revised proof under formal review.",
      ["Talvi Aubrel has posted a revised proof of the Cresselle Conjecture, replacing the flawed "
       "third lemma with a new argument based on the Flint Lemma.",
       "The Guild of Numerists has placed the proof under review. A decision is not expected "
       "before the end of the year."],
      tags=["math", "cresselle"], outlets=("courier", "lodestone")),
    # ---------------- Sky -----------------------------------------------------------
    S(d(412, 8, 1), "science", "Pith to cross Ossa on 3 Mire",
      "The small moon will pass in front of the large one for 41 minutes.",
      ["Stargazers in the Pellucid Isles and southern Veyl will see the small moon Pith pass in "
       "front of Ossa on the night of 3 Mire, the Lanternport Observatory has confirmed.",
       "The crossing begins at 21:14 Lanternport time and lasts 41 minutes. It will be the first "
       "full crossing visible from Lanternport since 397."],
      tags=["astronomy", "pith"], outlets=("courier", "tidings", "lodestone"),
      truth={"date": "3 Mire 412", "start": "21:14", "duration_min": 41}, image="moons"),
    # ---------------- Storm Petrel -----------------------------------------------------
    S(d(412, 8, 9), "weather", "Storm Petrel batters Brineholt",
      "Trams halted and ferries cancelled as gusts reach 27 leagues an hour.",
      ["Storm Petrel struck Brineholt overnight with gusts of up to 27 leagues an hour recorded at "
       "the Northmole.",
       "The Brineholt Tramways suspended the Harbour Line and the Stair funicular. Emberline "
       "cancelled all sailings from Brineholt and Harthwick.",
       "The Admiralty said 3,400 homes lost power."],
      tags=["storm-petrel", "weather", "brineholt"], outlets=("courier", "tidings", "crier"),
      truth={"max_gust_leagues_per_hour": 27, "homes_without_power": 3400},
      variants={"courier": {"dek": "Trams halted and Glass Sea ferries cancelled."},
                "tidings": {"dek": "Harbour Line and Stair funicular suspended; 3,400 homes dark.",
                            "paras": ["Storm Petrel tore through the city overnight. The "
                                      "Northmole gauge recorded a gust of 27 leagues an hour, the "
                                      "highest since the Harbour Fire year.",
                                      "Tramways say the Harbour Line will reopen on 12 Gale. The "
                                      "Stair funicular remains closed until further notice.",
                                      "3,400 homes lost power, mostly in Keelwater and Sounding."]}},
      image="storm"),
    # ---------------- Quenby clock ---------------------------------------------------
    S(d(412, 3, 8), "crime", "Golden hand stolen from Quenby Great Clock",
      "Thieves climbed the tower and removed the gilded Pith hand.",
      ["The gilded hand that tracks the moon Pith on the Quenby Great Clock was stolen overnight, "
       "Quenby wardens said.",
       "The hand, about two ells long, was made in 256 CR. Clock keepers stopped the Pith dial to "
       "prevent damage to the mechanism."],
      tags=["quenby", "clock", "crime"], outlets=("courier", "crier"), image="clock"),
    S(d(412, 5, 15), "crime", "Stolen Quenby clock hand turns up at auction",
      "Hollowmarket withdrew the lot after a reader recognised it.",
      ["The gilded Pith hand stolen from the Quenby Great Clock in Loam has been recovered after it "
       "was listed for sale at Hollowmarket Auctions as \"a gilded pointer, maker unknown\".",
       "The lot was withdrawn after a Quenby clock enthusiast recognised a repair mark on the "
       "listing's photograph. Hollowmarket said the seller had given a false address.",
       "Corwen Talley, the Vantle co-founder, has paid for the hand to be re-fitted."],
      tags=["quenby", "clock", "crime", "hollowmarket"], outlets=("courier",)),
    # ---------------- Harthwick light ------------------------------------------------
    S(d(412, 7, 1), "local", "Harthwick Lighthouse gets a new light pattern",
      "The light will now flash three times every twelve seconds.",
      ["The Harthwick Lighthouse has a new character. Since midnight on 1 Sheaf it flashes three "
       "times every twelve seconds, instead of twice every nine seconds.",
       "The change avoids confusion with the new light on the Lowmarsh breakwater, which also "
       "flashes twice every nine seconds."],
      tags=["harthwick", "lighthouse"], outlets=("courier", "tidings"),
      truth={"new_pattern": "3 flashes every 12 seconds", "old_pattern": "2 flashes every 9 seconds"}),
    # ---------------- Travel and trade -----------------------------------------------
    S(d(412, 6, 1), "business", "Emberline launches Ostmere to Lanternport airship",
      "The airship Skylark will cut the journey to under eight hours.",
      ["Emberline's new airship, the Skylark, made its first passenger flight from Ostmere to "
       "Lanternport on Anvilday, landing after 7 hours 40 minutes.",
       "The ferry and rail route takes about 19 hours. Fares start at 212 crowns one way."],
      tags=["emberline", "skylark"], outlets=("courier", "tidings"),
      truth={"duration": "7h40", "fare_from_cr": 212}, image="airship"),
    S(d(412, 3, 18), "business", "Admiralty raises Brineholt harbour levy",
      "Ships will pay four bits a ton instead of three from 1 Bloom.",
      ["The Admiralty Council has raised the Brineholt harbour levy from three bits to four bits "
       "per ton, the first rise since the Harbour Fire of 404.",
       "Tidemaster Oriel Casswater said the money would pay for a new sea wall at the Northmole."],
      tags=["saltmarch", "harbour"], outlets=("tidings",)),
    S(d(412, 5, 19), "business", "Bazaar goes dark for seven hours",
      "Sellers lost an estimated 40 million crowns in sales.",
      ["Bazaar, the Weave's largest marketplace, was unreachable for seven hours on Kettleday "
       "after what the company called \"a knotted loom in Caddick Ford\".",
       "Founder Edric Hollowell apologised and promised sellers a week of waived fees."],
      tags=["bazaar"], outlets=("courier", "tidings")),
    S(d(412, 4, 12), "business", "Small sites vanish from Lanthorn after 'Lamp' update",
      "Personal pages on .fol domains have dropped sharply in Lanthorn results.",
      ["Owners of personal sites on the .fol domain say their pages have dropped out of Lanthorn's "
       "results since the search engine's 'Lamp' update on 2 Bloom.",
       "Lanthorn said the update \"favours pages with many lanterns pointing to them\" and that "
       "small sites could submit their pages through its Lantern Desk.",
       "Hearthring, the hand-kept directory of the Weave, says its traffic has tripled."],
      tags=["lanthorn", "weave"], outlets=("courier", "lodestone")),
    # ---------------- Culture ---------------------------------------------------------
    S(d(412, 5, 12), "culture", "Nell Hedgecote announces 'Ninth Bridge'",
      "The follow-up to 'Lock Eleven' arrives on 12 Crest.",
      ["Nell Hedgecote's third album, 'Ninth Bridge', will be released by Bellows Records on "
       "12 Crest, with a tour of eleven cities beginning in Sheaf."],
      tags=["music", "nell-hedgecote"], outlets=("courier", "tidings")),
    S(d(412, 7, 20), "culture", "'The Lampwright' wins the Golden Lantern",
      "Anouk Belvaine's film took four prizes in Lanternport.",
      ["'The Lampwright', directed by Anouk Belvaine, won the Golden Lantern for best picture at "
       "the Lanternport Film Festival, along with prizes for direction, score, and for Jago "
       "Tidewright as best lead."],
      tags=["film"], outlets=("courier", "tidings")),
    S(d(412, 1, 30), "culture", "Morwen Reefley to adapt 'Nine Fathoms Down' for the stage",
      "The novelist will write the play herself.",
      ["Morwen Reefley will adapt her novel 'Nine Fathoms Down' for the Brineholt Playhouse, "
       "opening in Mire."], tags=["books"], outlets=("tidings",)),
    # ---------------- Pellucid ----------------------------------------------------
    S(d(412, 3, 30), "politics", "Senate passes Open Loom act",
      "Every library in the Isles must offer a free public loom.",
      ["The Senate of Colleges has passed the Open Loom Act, which gives every Pellucid library a "
       "free public loom connected to the Weave, Chancellor-Senator Iselle Marovane announced."],
      tags=["pellucid", "weave"], outlets=("courier", "lodestone")),
    # ---------------- Oddavar -----------------------------------------------------
    S(d(412, 5, 1), "world", "Frostgate opens for the trading season",
      "The gates will close again after 18 Sheaf.",
      ["The gates of the Frostgate Wall opened at dawn on 1 Blaze for the trading season. "
       "Oddavari traders are expected to bring furs, ice-salt, and pale-flame lamp oil.",
       "The gates close after 18 Sheaf, ninety days later."],
      tags=["oddavar", "frostgate"], outlets=("courier", "tidings")),
]
# fmt: on


# ---------------------------------------------------------------------------
# Generated stories
# ---------------------------------------------------------------------------

def _match_story(m):
    home, away = TEAM[m.home], TEAM[m.away]
    if m.home_score == m.away_score:
        head = f"{home.name} and {away.name} share the points"
    elif m.home_score > m.away_score:
        head = f"{home.name} beat {away.name} {m.home_score}–{m.away_score}"
    else:
        head = f"{away.name} win at {home.ground}"
    scorers = {}
    for minute, side, pid, kind in m.scoring:
        scorers.setdefault(pid, []).append(f"{minute}' {kind}")
    top = sorted(scorers.items(), key=lambda kv: -len(kv[1]))[:3]
    lines = [f"{PLAYER[pid].name.full} ({', '.join(v)})" for pid, v in top]
    paras = [f"{home.name} {m.home_score}, {away.name} {m.away_score}. Round {m.round} of the "
             f"Vaultball Premier Circuit at {home.ground}, attendance {m.attendance:,}.",
             "Scorers of note: " + "; ".join(lines) + "." if lines else "A scoreless dour affair.",
             f"Referee: {m.referee}."]
    return S(m.date, "sport", head, f"Round {m.round} report", paras,
             tags=["vaultball", m.home, m.away], outlets=("courier", "tidings"))


def _market_story(day, prev):
    moves = []
    for ticker, series in PRICES.items():
        a, b = series[prev], series[day]
        moves.append((b / a - 1, ticker, b))
    moves.sort()
    worst, best = moves[0], moves[-1]
    names = {c.ticker: c.name for c in COMPANIES if c.ticker}
    head = f"Exchange week: {names[best[1]]} leads, {names[worst[1]]} lags"
    paras = [f"The best performer on the Brineholt Exchange this week was {names[best[1]]}, up "
             f"{best[0] * 100:.1f} per cent to close at {best[2]:.2f} tallies.",
             f"{names[worst[1]]} fared worst, falling {abs(worst[0]) * 100:.1f} per cent to "
             f"{worst[2]:.2f}."]
    return S(day, "business", head, "The week on the Brineholt Exchange", paras,
             tags=["exchange"], outlets=("tidings",))


def generated_stories():
    out = []
    for m in MATCHES:
        if m.played:
            out.append(_match_story(m))
    days = [x for x in trading_days() if x.weekday == "Hearthday"]
    for prev, day in zip(days, days[1:]):
        out.append(_market_story(day, prev))
    return out


ALL_STORIES = sorted(STORIES + generated_stories(), key=lambda s: (s.date, s.id))
STORY = {s.id: s for s in ALL_STORIES}

REPORTERS = {
    "courier": ["Idony Carrowby", "Perrin Whitfield", "Lettice Ondley", "Florian Marshaw",
                "Kestrel Hamley", "Juniper Brackton"],
    "tidings": ["Morwen Kelpson", "Casso Reefley", "Nessa Tidewright", "Jago Shoalworth"],
    "crier": ["Staff Reporter", "Our Correspondent", "The Crier Team"],
    "lodestone": ["Sevrin Aubrande", "Quilla Marelle"],
}


def byline(story, outlet):
    rng = stream("byline", story.id, outlet)
    if story.section == "sport":
        return {"courier": "Garrick Mottlow", "tidings": "Bex Gullwright"}.get(outlet, "Staff")
    return rng.choice(REPORTERS[outlet])
