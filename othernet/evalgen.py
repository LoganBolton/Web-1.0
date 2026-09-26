"""Generate the eval question set from the world's ground truth, and check each
answer against the built Weave.

    python -m othernet.build          # the questions are verified against ./web
    python -m othernet.evalgen        # writes evals/questions.jsonl and prints a summary

Every question has one short, objective answer. `evidence` lists (url, text)
pairs: the text must appear in that file of the built Weave, so a question can
only be kept if an agent could actually find its answer. Questions whose answer
only appears after using a form carry `steps`, which tools/verify_interactive.js
replays in a real browser.

Difficulty
  easy    one page, answer stated plainly, findable by search or obvious links
  medium  one or two hops, or a table lookup, date or unit conversion, or a site
          search engines don't index
  hard    three or more hops, conflicting or stale sources, images, forms,
          logins, archives, hidden pages, or arithmetic across sites
"""
import html
import json
import math
import os
import re
import sys
from dataclasses import dataclass, field, asdict

from .engine.domains import url
from .engine.rng import stream, slug
from .world import culture
from .world.academia import PAPERS
from .world.calendar import ADate, TODAY, MONTHS, time_str
from .world.econ import RATES, PRICES, trading_days, CURRENCY_NAMES
from .world.geo import NATIONS, CITIES, CITY, distance_leagues, monthly_climate
from .world.orgs import COMPANIES, PARTIES, SEATS
from .world.people import NOTABLE
from .world.politics import BILLS, DELEGATES, DELEGATE
from .world.sky import tides
from .world.sports import TEAMS, TEAM, PLAYER, MATCHES, standings
from .world.weather import WEATHER

WEB = "web"


@dataclass
class Q:
    question: str
    answer: str
    difficulty: str
    evidence: list  # [(url, text that must appear there)]
    kind: str = "text"  # text | number
    accept: list = field(default_factory=list)
    tolerance: float = 0.0
    modality: str = "text"  # text | image | interaction | source
    hops: int = 1
    topic: str = ""
    notes: str = ""
    steps: list = field(default_factory=list)
    expect: str = ""  # text the last step must show, when the answer itself is not printed verbatim
    id: str = ""


# ---------------------------------------------------------------------------
# Reading the built Weave
# ---------------------------------------------------------------------------
def _file(u):
    m = re.match(r"http://([^/]+)(/[^?#]*)?", u)
    dom, path = m.group(1), m.group(2) or "/"
    base = os.path.join(WEB, dom, path.lstrip("/"))
    for cand in (os.path.join(base, "index.html"), base, base + ".html"):
        if os.path.isfile(cand):
            return cand
    return None


_cache = {}


def raw(u):
    if u not in _cache:
        f = _file(u)
        _cache[u] = html.unescape(open(f, encoding="utf-8").read()) if f else None
    return _cache[u]


def data(site_key, path):
    return json.loads(raw(url(site_key, path)))


def num(x, d=0):
    return f"{x:,.{d}f}"


# ---------------------------------------------------------------------------
# Easy
# ---------------------------------------------------------------------------
def easy(rng):
    out = []
    E = "easy"
    for code, n in NATIONS.items():
        out.append(Q(f"What is the capital of {n.name}?", n.capital, E, [(url("chartroom", f"/nation/{code.lower()}/"), n.capital)], topic="geography"))
    for c in rng.sample([c for c in CITIES], 6):
        out.append(Q(f"What is the population of {c.name}, according to the Chartroom atlas?", num(c.population), E,
                     [(url("chartroom", f"/place/{c.slug}/"), num(c.population))], kind="number", topic="geography"))
    for c in rng.sample(CITIES, 4):
        out.append(Q(f"How high above sea level is {c.name}, in ells?", num(c.elevation), E,
                     [(url("chartroom", f"/place/{c.slug}/"), f"{num(c.elevation)} ells")], kind="number", topic="geography"))
    for c in rng.sample([c for c in CITIES if c.founded > 0], 3):
        out.append(Q(f"In what year (CR) was {c.name} founded?", str(c.founded), E,
                     [(url("chartroom", f"/place/{c.slug}/"), f"{c.founded} CR")], kind="number", topic="geography"))
    listed = [c for c in COMPANIES if c.ticker]
    for c in rng.sample(listed, 5):
        ceo = NOTABLE[c.ceo].full if c.ceo in NOTABLE else c.ceo
        out.append(Q(f"Who is the chief executive of {c.name}?", ceo, E, [(url("exchange", f"/listing/{c.ticker}/"), ceo)], topic="business"))
    for c in rng.sample(listed, 4):
        out.append(Q(f"What is the ticker symbol of {c.name} on the Brineholt Exchange?", c.ticker, E,
                     [(url("exchange", f"/listing/{c.ticker}/"), c.ticker)], topic="business"))
    for c in rng.sample([c for c in COMPANIES if c.founded > 0], 3):
        out.append(Q(f"In what year (CR) was {c.name} founded?", str(c.founded), E,
                     [(url("commonplace", f"/folio/{slug(c.name)}/"), f"{c.founded} CR")], kind="number", topic="business"))
    films = culture.FILMS[:6] + rng.sample(culture.FILMS[6:], 3)
    for f in films[:5]:
        out.append(Q(f"Who directed the film '{f.title}' ({f.year})?", f.director, E, [(url("reelhouse", f"/title/{f.id}/"), f.director)], topic="culture"))
    for f in films[5:]:
        out.append(Q(f"How long is the film '{f.title}' ({f.year}), in minutes?", str(f.runtime), E,
                     [(url("reelhouse", f"/title/{f.id}/"), f"{f.runtime} min")], kind="number", topic="culture"))
    qbooks = [b for b in culture.BOOKS if b.publisher == "Quillmere Press"]
    for b in rng.sample(qbooks, 3):
        out.append(Q(f"Who wrote the Quillmere Press book '{b.title}'?", b.author, E, [(url("quillmere", f"/books/{b.id}.html"), b.author)], topic="books"))
    for b in rng.sample(qbooks, 3):
        out.append(Q(f"How many pages does the Quillmere Press edition of '{b.title}' have?", str(b.pages), E,
                     [(url("quillmere", f"/books/{b.id}.html"), f"<td>Pages</td><td>{b.pages}</td>")], kind="number", topic="books"))
    for t in rng.sample(TEAMS, 3):
        out.append(Q(f"What is the name of the {t.name}' home ground?", t.ground, E, [(url("vaultball", f"/teams/{t.id}/"), t.ground)], topic="sport"))
    for t in rng.sample(TEAMS, 3):
        out.append(Q(f"How many spectators does {t.ground}, home of the {t.name}, hold?", num(t.capacity), E,
                     [(url("vaultball", f"/teams/{t.id}/"), num(t.capacity))], kind="number", topic="sport"))
    for t in rng.sample(TEAMS, 2):
        out.append(Q(f"Who is the head coach of the {t.name}?", t.coach, E, [(url("vaultball", f"/teams/{t.id}/"), t.coach)], topic="sport"))
    out += [
        Q("How many thumbs make an ell?", "40", E, [(url("lexicon", "/word/thumb/"), "fortieth of an ell")], kind="number", topic="units"),
        Q("How many ells make a league?", "4,000", E, [(url("lexicon", "/word/league/"), "4,000 ells")], kind="number", topic="units"),
        Q("How many bits make a Saltmarch tally?", "12", E, [(url("tramways", "/fares/"), "Twelve bits make a tally")], kind="number",
          accept=["twelve"], topic="units"),
        Q("How many spoons make a measure, according to Hearth & Hob?", "16", E,
          [(url("hearthandhob", "/recipe/seed-cake-that-doesn-t-sink/"), "1 measure = 16 spoons")], kind="number", topic="units"),
        Q("How many days are in a Concord Reckoning year?", "365", E, [(url("quorum", _quorum_path("How many days in a Concord year?")), "365")],
          kind="number", topic="calendar"),
        Q("How many Hollowdays are there at the end of each year?", "5", E, [(url("lexicon", "/word/hollowdays/"), "five days")], kind="number",
          accept=["five"], topic="calendar"),
    ]
    from .sites.vantle import FAULTS
    for code, meaning, _ in [f for f in FAULTS if f[0] in ("W-01", "W-12", "W-33", "W-51")]:
        out.append(Q(f"What does fault code {code} mean on a Vantle Slate?", meaning, E, [(url("vantle", "/support/faults/"), meaning)], topic="technology"))
    from .sites.drovers import LOANS, SAVINGS
    for name, rate in [LOANS[3], LOANS[2], LOANS[4]]:
        out.append(Q(f"What yearly interest rate does Drovers' Bank charge on its '{name}'?", f"{rate:.2f}%", E, [(url("drovers", "/loans/"), f"{rate:.2f}%")],
                     kind="number", topic="finance"))
    out.append(Q("What yearly interest does the Drovers' Bank 'Hollowday Saver' account pay?", f"{SAVINGS[2][1]:.2f}%", E,
                 [(url("drovers", "/savings/"), f"{SAVINGS[2][1]:.2f}%")], kind="number", topic="finance"))
    from .sites.tramways import FARES
    for name, price in [FARES[0], FARES[2], FARES[5]]:
        out.append(Q(f"How much is a Brineholt Tramways '{name}' ticket?", price, E, [(url("tramways", "/fares/"), price)],
                     accept=_tally_variants(price), topic="transport"))
    from .sites.post import ZONES
    for code in ("SLT", "PEL", "KHR"):
        zname, first, extra = ZONES[code]
        out.append(Q(f"What does the Concordat Post charge for the first weight of a letter to {zname}?", f"{first:.2f} cr", E,
                     [(url("post", "/postage/"), f"{first:.2f} cr")], kind="number", topic="post"))
    for c in rng.sample([c for c in CITIES if c.nation in ("VEY", "SLT")], 3):
        m = rng.randrange(10)
        temps, _ = monthly_climate(c)
        out.append(Q(f"According to the Concordat Weather Office, what is the mean temperature in {c.name} in {MONTHS[m]}, in degrees Harl?",
                     f"{temps[m]:.1f}", E, [(url("weather", f"/climate/{c.slug}/"), f"<td>{MONTHS[m]}</td><td>{temps[m]:.1f}</td>")],
                     kind="number", topic="weather"))
    from .sites.numerary import ROLLS
    for r in [r for r in ROLLS if r[0] in ("MS-1", "NL-1", "RB-1")]:
        who = r[3]
        out.append(Q(f"Whose name is attached to the result the Numerary lists as {r[0]}, '{r[1]}'?", who, E,
                     [(url("numerary", f"/roll/{r[0]}/"), who)], topic="mathematics"))
    out += [
        Q("What is the current version of the Weft programming language?", "3.2", E, [(url("weft", "/"), "3.2")], kind="number", topic="technology"),
        Q("Which Weft keyword returns a value from a ribbon?", "give", E, [(url("weft", "/reference/"), "Return a value from a ribbon")], topic="technology"),
        Q("At what time does Radio Lantern's 'Night Sky' programme start?", "21:00", E, [(url("radio", "/shows/night-sky/"), "21:00")], topic="media"),
        Q("Who presents 'Kitchen Tide' on Radio Lantern?", "Delphine Estrande", E, [(url("radio", "/shows/kitchen-tide/"), "Delphine Estrande")], topic="media"),
        Q("How many passengers does the Emberline airship Skylark carry?", "86", E, [(url("emberline", "/fleet/"), "Carries 86 passengers")],
          kind="number", topic="transport"),
        Q("In what year was the Emberline ferry Tern's Luck built?", "377", E, [(url("emberline", "/fleet/"), "built 377 CR")], kind="number", topic="transport"),
        Q("How much is an adult ticket to the Museum of the Deep Halls?", "6 mk", E, [(url("museum", "/visit/"), "6 mk")], kind="number",
          accept=["6 marks"], topic="culture"),
        Q("How long does Ossa take to circle Averra, in days?", "29.25", E, [(url("observatory", "/"), "29.25 days")], kind="number",
          accept=["29 days 6 hours"], topic="astronomy"),
    ]
    for p in ["civic-ledger", "green-moor", "hearth-plough"]:
        out.append(Q(f"How many seats does {PARTIES[p]['name']} hold in the Concordat Assembly?", str(SEATS[p]), E,
                     [(url("assembly", "/parties/"), f"<td>{SEATS[p]}</td>")], kind="number", topic="politics"))
    return out


def _tally_variants(price):
    """'1t 2b' -> ['1 tally 2 bits', '1 tallies 2 bits', '14 bits']"""
    m = re.fullmatch(r"(?:(\d+)t )?(\d+)b", price)
    if not m:
        return []
    t, b = int(m.group(1) or 0), int(m.group(2))
    out = [f"{t * 12 + b} bits"]
    if t:
        out += [f"{t} tally {b} bits", f"{t} tallies {b} bits"] + ([f"{t} tallies", f"{t} tally"] if b == 0 else [])
    return out


def _quorum_path(title):
    for q in data("quorum", "/data/qs.json"):
        if q["t"] == title:
            return q["p"]
    raise KeyError(title)


# ---------------------------------------------------------------------------
# Medium
# ---------------------------------------------------------------------------
def medium(rng):
    out = []
    M = "medium"
    played = [m for m in MATCHES if m.played]
    for m in rng.sample(played, 5):
        h, a = TEAM[m.home], TEAM[m.away]
        out.append(Q(f"In round {m.round} of the 412 Premier Circuit, {h.name} played {a.name} at home. How many points did {h.name} score?",
                     str(m.home_score), M, [(url("vaultball", f"/matches/{m.id}/"), f"{h.name}</a><br>{m.home_score}</div>")], kind="number",
                     hops=2, topic="sport"))
    top = sorted(PLAYER.values(), key=lambda p: -p.stats["points"])
    for p in rng.sample(top[:25], 4):
        out.append(Q(f"How many wells has {p.name.full} ({TEAM[p.team].name}) scored in the 412 Premier Circuit so far?", str(p.stats["wells"]), M,
                     [(url("vaultball", f"/players/{p.id}/"), f"<td>{p.stats['rims']}</td><td>{p.stats['wells']}</td>")], kind="number", hops=2,
                     topic="sport"))
    days = trading_days()
    for t in rng.sample(["VNTL", "BZR", "LNTH", "DRVB", "EMBL", "CLDF", "GLDW", "SALT"], 4):
        d = rng.choice(days[20:-5])
        c = next(c for c in COMPANIES if c.ticker == t)
        out.append(Q(f"What was {c.name}'s closing share price on the Brineholt Exchange on {d.long()}, in tallies (to two decimal places)?",
                     f"{PRICES[t][d]:.2f}", M, [(url("exchange", f"/listing/{t}/prices/"), f"{d.salt()}</td><td>{PRICES[t][d]:.2f}")], kind="number",
                     tolerance=0.005, hops=2, topic="finance", notes="the price table writes dates the Saltmarch way (day/month/year)"))
    for cur in ("STL", "KMK", "PLM"):
        d = ADate(412, rng.randint(1, 7), rng.randint(1, 36))
        out.append(Q(f"What was Drovers' Bank's mid rate for the {CURRENCY_NAMES[cur]} on {d.long()}, in crowns (four decimal places)?",
                     f"{RATES[cur][d]:.4f}", M, [(url("drovers", f"/rates/history/{d.month:02d}/"), f"{RATES[cur][d]:.4f}")], kind="number",
                     tolerance=0.00005, hops=2, topic="finance"))
    pairs = [("Harrowdeep", "Lanternport"), ("Tidewell", "Aldermoot"), ("Quenby", "Coralstead"), ("Skarn", "Silverrun")]
    for a, b in pairs:
        d = distance_leagues(a, b)
        out.append(Q(f"What is the straight-line distance from {a} to {b}, in leagues?", f"{d:.1f}", M,
                     [(url("chartroom", f"/place/{slug(a)}/"), f"{b}</a></td><td>{NATIONS[CITY[b].nation].short}</td><td>{d:,.1f}")],
                     kind="number", tolerance=0.05, topic="geography"))
    voted = [b for b in BILLS if b.votes]
    for b in rng.sample(voted, 3):
        out.append(Q(f"How many delegates voted yes on the {b.title} ({b.id})?", str(b.tally["yes"]), M,
                     [(url("assembly", f"/bills/{b.id}/"), f"Yes {b.tally['yes']}, No")], kind="number", hops=2, topic="politics"))
    for b in rng.sample([b for b in BILLS if b.title[0] not in "AL" and "Canals Inquiry" not in b.title], 2):  # that one is a hard question
        sp = DELEGATE[b.sponsor].name.full
        out.append(Q(f"Which delegate sponsored the {b.title} in the Concordat Assembly?", sp, M, [(url("assembly", f"/bills/{b.id}/"), sp)],
                     hops=2, topic="politics"))
    for d in rng.sample([d for d in DELEGATES if not d.office], 3):
        out.append(Q(f"Which province does the delegate {d.name.full} represent?", d.province, M,
                     [(url("assembly", f"/delegates/{d.id}/"), f"Delegate for {d.province}")], hops=2, topic="politics"))
    cos = [c for c in data("registry", "/data/companies.json") if c["no"].startswith("CR-") and c["s"] == "Active"]
    for c in rng.sample(cos[40:], 3):
        out.append(Q(f"What is the Concordat Registry number of the company '{c['n']}'?", c["no"], M, [(url("registry", c["p"]), c["no"])],
                     hops=2, topic="registry", notes="needs the Registry's own search, which Lanthorn cannot see behind"))
    net = data("emberline", "/data/network.json")
    legs = {l["id"]: l for l in net["legs"]}
    for lid in ("harthwick-marrowby", "brineholt-corrack", "lanternport-shellcombe"):
        l = legs[lid]
        out.append(Q(f"How long is Emberline's journey from {l['from']} to {l['to']}?", f"{l['dur'] // 60}h {l['dur'] % 60:02d}m", M,
                     [(url("emberline", f"/routes/{lid}/"), f"journey time {l['dur'] // 60}h {l['dur'] % 60:02d}m")],
                     accept=[f"{l['dur'] // 60} hours {l['dur'] % 60} minutes", f"{l['dur']} minutes"], topic="transport"))
    l = legs["gullhaven-tidewell"]
    out.append(Q("On which weekdays does the Emberline ferry run from Gullhaven to Tidewell? (list them)", "Kettleday, Plowday, Stillday", M,
                 [(url("emberline", "/routes/gullhaven-tidewell/"), "<td>Stillday</td><td>12:00")], kind="set",
                 topic="transport", notes="order does not matter"))
    homes = data("hearthfind", "/data/homes.json")
    for h in rng.sample([h for h in homes if not h["rent"] and h["cur"] == "VCR"], 2):
        out.append(Q(f"What is the asking price of Hearthfind listing {h['id']}, in crowns?", num(h["price"]), M,
                     [(url("hearthfind", f"/home/{h['id']}/"), f"{num(h['price'])} cr")], kind="number", topic="property"))
    for h in rng.sample([h for h in homes if h["rent"]], 2):
        out.append(Q(f"How many bedrooms does the home in Hearthfind listing {h['id']} have?", str(h["beds"]), M,
                     [(url("hearthfind", f"/home/{h['id']}/"), f"{h['beds']} bedroom")], kind="number", topic="property"))
    places = data("tastemark", "/data/places.json")
    for p in rng.sample(places, 3):
        page = raw(url("tastemark", f"/biz/{p['id']}/"))
        day = re.search(r"<tr><td>(\w+)</td><td>Closed</td></tr>", page).group(1)
        out.append(Q(f"On which day of the week is {p['n']} in {p['c']} closed, according to Tastemark?", day, M,
                     [(url("tastemark", f"/biz/{p['id']}/"), f"<td>{day}</td><td>Closed</td>")], topic="food",
                     notes="several places share a name; the town disambiguates"))
    for c in rng.sample([c for c in CITIES if c.nation in ("VEY", "KHR", "PEL")], 3):
        d = ADate(412, rng.randint(2, 7), rng.randint(1, 36))
        w = WEATHER[c.name][d]
        out.append(Q(f"What was the observed high temperature in {c.name} on {d.long()}, according to the Concordat Weather Office?",
                     f"{w['hi']:.1f}", M, [(url("weather", f"/observations/{c.slug}/"), f"{d.long()}</td><td>{w['cond']}</td><td>{w['hi']:.1f}")],
                     kind="number", tolerance=0.05, hops=2, topic="weather"))
    for port in ("Brineholt", "Tidewell", "Corrack"):
        d = TODAY + rng.randint(1, 5)
        highs = [(m, h) for m, k, h in tides(d, port) if k == "High"]
        out.append(Q(f"At what time is the first high water at {port} on {d.long()}?", time_str(highs[0][0]), M,
                     [(url("tidings", "/tides/"), f"H {time_str(highs[0][0])}")], topic="tides",
                     notes="the Tidings tide table writes dates as day/month/year"))
    cat = data("athenaeum", "/data/catalogue.json")
    for b in rng.sample(cat, 3):
        out.append(Q(f"What is the Athenaeum call number for '{b['t']}' by {b['a']}?", b["c"], M, [(url("athenaeum", f"/record/{b['id']}/"), b["c"])],
                     topic="books", notes="the catalogue search is script-driven"))
    for d in (ADate(412, 9, 30), ADate(412, 9, 3), ADate(412, 11, 1)):
        name = "the first Hollowday of 412" if d.month == 11 else d.long()
        out.append(Q(f"On what day of the week does {name} fall?", d.weekday, M,
                     [(url("observatory", "/moons/412-09/"), f"<b>{d.day}</b> {d.weekday_abbr}")] if d.month != 11 else
                     [(url("observatory", "/moons/412-10/"), f"<b>36</b> {ADate(412, 10, 36).weekday_abbr}")],
                     topic="calendar", notes="count on from a calendar or from today's date and the six-day week"))
    out.append(Q("The Peace of Stonemeet was sealed on 12 Sheaf 246 CR. What year is that in the Kethren Hold Reckoning?", "1126", M,
                 [(url("museum", "/object/DH.1246.12/"), "1126 HR")], kind="number", topic="calendar"))
    items = data("bazaar", "/data/index.json")
    slt = [x for x in items["items"] if x["cur"] == "STL" and x["st"] > 0 and x["c"] not in ("books", "music")]
    for x in rng.sample(slt, 3):
        cr = x["p"] * items["rates"]["STL"]
        out.append(Q(f"Bazaar item {x['id']} ('{x['t']}') is priced in tallies. About how many crowns is that, by Bazaar's own estimate?",
                     f"{cr:,.2f}", M, [(url("bazaar", f"/item/{x['id']}/"), f"about {cr:,.2f} cr")], kind="number", tolerance=0.01, topic="shopping"))
    lots = [l for l in data("hollowmarket", "/data/lots.json") if l["h"]]
    for l in rng.sample(lots, 3):
        out.append(Q(f"What was the hammer price of Hollowmarket lot {l['no']}, in crowns (before buyer's premium)?", num(l["h"]), M,
                     [(url("hollowmarket", f"/lot/{l['no']}/"), f"Hammer price: {num(l['h'])} cr")], kind="number", topic="auctions"))
    rolls = data("patents", "/data/rolls.json")
    for r in rng.sample([r for r in rolls if len(r["i"]) == 1], 2):
        out.append(Q(f"Who is the inventor named on Patent Roll {r['no']}, '{r['t']}'?", r["i"][0], M,
                     [(url("patents", r["p"]), r["i"][0])], topic="patents"))
    for p in rng.sample([p for p in PAPERS if p.kind == "article" and len(p.authors) == 1], 2):
        out.append(Q(f"Who wrote the Annals paper '{p.title}' (volume {p.volume}, issue {p.issue})?", p.authors[0], M,
                     [(url("annals", f"/paper/{p.id}/"), p.authors[0])], topic="academia"))
    from .sites.tramways import LINES
    for code, name, col, stops, every, first, last in (LINES[0], LINES[3]):
        out.append(Q(f"How often do trams run on Brineholt's {name}?", f"every {every} minutes", M,
                     [(url("tramways", f"/lines/{code.lower()}/"), f"Trams every {every} minutes")], kind="number", topic="transport"))
    for f in rng.sample([f for f in culture.FILMS if f.box_office > 20_000_000], 2):
        out.append(Q(f"How much did the film '{f.title}' ({f.year}) take at the box office, in crowns?", num(f.box_office), M,
                     [(url("reelhouse", f"/title/{f.id}/"), f"Box office: {num(f.box_office)} cr")], kind="number", topic="culture"))
    jobs = data("guildwork", "/data/jobs.json")
    for j in rng.sample([j for j in jobs if not j["cl"] and "cr a year" in j["p"]], 2):
        out.append(Q(f"What yearly pay does the Guildwork listing {j['id']} ('{j['t']}' at {j['e']}) offer?", j["p"].replace(" a year", ""), M,
                     [(url("guildwork", f"/job/{j['id']}/"), j["p"])], kind="number", topic="jobs"))
    out.append(Q("How many tidal primes are there below 10,000, according to the Guild of Numerists?", "", M,
                 [(url("numerary", "/roll/TP-4/"), "")], kind="number", topic="mathematics"))
    from .sites.numerary import tidal
    n = sum(1 for k in range(2, 10_000) if tidal(k))
    out[-1].answer = num(n)
    out[-1].evidence = [(url("numerary", "/roll/TP-4/"), f"<td>10,000</td><td>{num(n)}</td>")]
    return out


# ---------------------------------------------------------------------------
# Hard
# ---------------------------------------------------------------------------
def hard(rng):
    out = []
    H = "hard"
    table = standings()
    second = TEAM[table[1]["team"]]
    out.append(Q("Who is the head coach of the club in second place in the Premier Circuit table on 17 Gale 412?", second.coach, H,
                 [(url("vaultball", "/standings/"), second.name), (url("vaultball", f"/teams/{second.id}/"), second.coach)], hops=2, topic="sport"))
    wells = max(PLAYER.values(), key=lambda p: (p.stats["wells"], p.stats["points"]))
    wt = TEAM[wells.team]
    out.append(Q("The player with the most wells in the 412 Premier Circuit plays home games at which ground?", wt.ground, H,
                 [(url("vaultball", "/stats/"), wells.name.full), (url("vaultball", f"/teams/{wt.id}/"), wt.ground)], hops=2, topic="sport"))
    days = trading_days()
    ytd = {c.ticker: PRICES[c.ticker][days[-1]] / PRICES[c.ticker][days[0]] - 1 for c in COMPANIES if c.ticker}
    worst = min(ytd, key=ytd.get)
    wc = next(c for c in COMPANIES if c.ticker == worst)
    ceo = NOTABLE[wc.ceo].full if wc.ceo in NOTABLE else wc.ceo
    out.append(Q("Which listed company's shares have fallen furthest on the Brineholt Exchange so far in 412, and who is its chief executive? "
                 "Give the chief executive's name.", ceo, H, [(url("exchange", "/listings/"), worst), (url("exchange", f"/listing/{worst}/"), ceo)],
                 hops=2, topic="finance", notes=f"the company is {wc.name}"))
    b = next(b for b in BILLS if b.title == "Canals Inquiry (Powers) Act")
    sp = DELEGATE[b.sponsor]
    out.append(Q("The delegate who sponsored the Canals Inquiry (Powers) Act chairs which Assembly committee?", "Canals and Waterways", H,
                 [(url("assembly", f"/bills/{b.id}/"), sp.name.full), (url("assembly", f"/delegates/{sp.id}/"), "Chair, Canals and Waterways Committee")],
                 accept=["Canals and Waterways Committee"], hops=2, topic="politics"))
    # --- images ---------------------------------------------------------------
    page = raw(url("copperkettle", "/find-us/"))
    rooms = re.findall(r'<a href="/find-us/([^/]+)/">([^<]+)</a></td><td>([^<]+)</td>', page)
    for rid, district, town in rng.sample(rooms, 3):
        svgt = raw(url("copperkettle", f"/img/board-{rid}.svg"))
        items = re.findall(r'font-family="Comic Sans MS, cursive" >([^<]+)</text><text x="486" y="\d+" font-size="19" fill="#fde68a" '
                           r'text-anchor="end" font-weight="normal" font-family="Comic Sans MS, cursive" >([^<]+)</text>', svgt)
        name, price = items[0]
        out.append(Q(f"On the specials board of the Copper Kettle tea room at {district}, {town}, what is the price of the {name}?", price, H,
                     [(url("copperkettle", f"/img/board-{rid}.svg"), price)], modality="image", accept=_tally_variants(price),
                     kind="number" if price.endswith("cr") else "text", topic="food", notes="the price is only in the specials board picture"))
    homes = data("hearthfind", "/data/homes.json")
    for h in rng.sample([h for h in homes if h["beds"] >= 2], 2):
        svgt = raw(url("hearthfind", f"/img/{h['id']}-plan.svg"))
        m = re.search(r">Kitchen</text>.*?>([\d.]+ x [\d.]+ ells)<", svgt)
        out.append(Q(f"According to the floor plan of Hearthfind listing {h['id']}, what are the kitchen's dimensions?", m.group(1), H,
                     [(url("hearthfind", f"/img/{h['id']}-plan.svg"), m.group(1))], modality="image", topic="property",
                     notes="dimensions appear only in the floor plan image"))
    out.append(Q("What repair mark is stamped on the pointer in the photograph of Hollowmarket lot 4471?", "Q.C. 331", H,
                 [(url("hollowmarket", "/img/lot-4471.svg"), "Q.C. 331")], accept=["QC 331"], modality="image", topic="auctions"))
    temps = [(c.name, WEATHER[c.name][TODAY]["hi"]) for c in CITIES]
    hot = max(temps, key=lambda t: t[1])
    out.append(Q("On the Concordat Weather Office's map of today's highest temperatures, which place is warmest?", hot[0], H,
                 [(url("weather", "/img/today.svg"), f"{hot[1]:.0f}&#176;".replace("&#176;", "°"))], modality="image", topic="weather",
                 notes=f"{hot[0]} shows {hot[1]:.0f} degrees"))
    # --- forms and calculators -----------------------------------------------
    for code in ("CK-2100-0700", "CK-6300-0000"):
        a, b2 = int(code[3:7]), int(code[8:])
        bal = ((a * 31 + b2 * 17) % 4000) / 100
        out.append(Q(f"What is the balance on Copper Kettle gift card {code}?", f"{bal:.2f} cr", H, [], kind="number", modality="interaction",
                     steps=[["goto", url("copperkettle", "/gift-cards/")], ["fill", "#gc", code], ["click", "#go"], ["read", "#bal"]], topic="food"))
    out.append(Q("A Noticeboard ad sells a Copper Kettle gift card as 'worth 25 cr'. What is that card's real balance?", "3.00 cr", H,
                 [(url("noticeboard", "/for-sale/"), "Copper Kettle gift card")], kind="number", modality="interaction", hops=2,
                 steps=[["goto", url("copperkettle", "/gift-cards/")], ["fill", "#gc", "CK-3500-1400"], ["click", "#go"], ["read", "#bal"]], topic="scams"))
    P, rate, years = 20_000, 5.40, 10
    r = rate / 100 / 10
    n = years * 10
    pay = P * r / (1 - (1 + r) ** -n)
    out.append(Q("Using Drovers' Bank's loan calculator, what is the monthly repayment on 20,000 cr borrowed for 10 years on the fixed five-year home loan?",
                 f"{pay:.2f} cr", H, [], kind="number", tolerance=0.01, modality="interaction",
                 steps=[["goto", url("drovers", "/loans/")], ["select", "#r", "5.4"], ["fill", "#p", "20000"], ["fill", "#y", "10"], ["read", "#m"]],
                 topic="finance", notes="a Veylish year has ten months, so ten repayments a year"))
    out.append(Q("Using the Concordat Post's calculator, what does it cost to send a 3.4-weight parcel to the Isles, signed for?",
                 f"{1.25 + 3 * 0.55 + 1.2:.2f} cr", H, [], kind="number", modality="interaction",
                 steps=[["goto", url("post", "/postage/")], ["select", "#z", "PEL"], ["fill", "#w", "3.4"], ["check", "#sig"], ["read", "#o"]],
                 topic="post"))
    out.append(Q("Scale Hearth & Hob's Gorse Hollow apple cake to serve 12. How many measures of flour does it need?", "2.25", H, [],
                 kind="number", accept=["2 1/4", "2\u00bc"], modality="interaction", topic="food",
                 notes="the recipe serves 8 with 1.5 measures; the scaler shows 2\u00bc",
                 steps=[["goto", url("hearthandhob", "/recipe/gorse-hollow-apple-cake/")], ["fill", "#sv", "12"], ["read", "#ing"]]))
    out.append(Q("Is Vantle charger batch 7A-0412-1712 in the recall's affected range? Answer yes or no.", "no", H, [], modality="interaction",
                 steps=[["goto", url("vantle", "/support/recall-vc7a/")], ["fill", "#batch", "7A-0412-1712"], ["click", "#chk"], ["read", "#res"]],
                 topic="technology", notes="affected range is 0800 to 1600", expect="not in the affected range"))
    from .sites.tramways import LINES
    h_first, h_every = LINES[0][5], LINES[0][4]
    nxt = h_first + math.ceil((13 * 60 - h_first) / h_every) * h_every
    out.append(Q("Using the departure board at Brineholt's Admiralty tram stop, when is the first Harbour Line (H) tram towards Northmole at or after 13:00 on a Kettleday?",
                 time_str(nxt), H, [], modality="interaction",
                 steps=[["goto", url("tramways", "/stops/admiralty/")], ["select", "#wd", "Kettleday"], ["fill", "#t", "13:00"], ["read", "#board"]],
                 topic="transport"))
    week = 5.0 * RATES["STL"][TODAY]
    out.append(Q("A Brineholt Tramways week pass costs 5 tallies. At Drovers' Bank's mid rate on 17 Gale 412, how many crowns is that (two decimal places)?",
                 f"{week:.2f}", H, [(url("tramways", "/fares/"), "5t 0b"), (url("drovers", "/rates/"), f"{RATES['STL'][TODAY]:.4f}")], kind="number",
                 tolerance=0.01, hops=2, topic="finance"))
    # --- the storylines ------------------------------------------------------
    S = [
        ("Who is the sole director of the company that owned 12% of Gildmere Works when it won the Tarrow Canal contract?", "Maud Ashford",
         [(url("registry", "/company/CR-47-409117/"), "Maud Ashford")], 3, {}),
        ("What is the name of the company, run by the Canal Minister's sister, that held a stake in Gildmere Works?", "Sallow Fen Holdings",
         [(url("registry", "/company/CR-47-409117/"), "Sallow Fen Holdings")], 2, {}),
        ("On what date did Sallow Fen Holdings sell its stake in Gildmere Works?", "18 Blaze 412",
         [(url("exchange", "/announcements/"), "18 Blaze 412")], 2, {"accept": ["18/5/412", "412·05·18"]}),
        ("Which company owns the publisher of The Crier outright?", "Morrow Media Group",
         [(url("registry", "/company/CR-51-401220/"), "Morrow Media Group")], 3, {"notes": "the Commonplace folio on Morrow Media does not mention the Crier"}),
        ("What share of Crier readers answered 'Yes, obviously' to the question 'Is the moon Pith artificial?'", "38%",
         [(url("crier", "/data/poll.json"), '"pct":[38')], 2, {"modality": "interaction", "kind": "number",
                                                             "notes": "results are shown only after voting",
                                                             "steps": [["goto", url("crier", "/poll.html")], ["click", "button.vote"], ["read", "#app"]]}),
        ("How many miners were trapped in the Deepshaft 9 collapse?", "16",
         [(url("moot", "/ruling/1292-31/"), "Sixteen workers were cut off")], 2, {"kind": "number", "accept": ["sixteen"],
                                                                                 "notes": "Courier first said 14, Tidings said 17, the Crier said dozens"}),
        ("Which newspaper first reported that seventeen miners were trapped in Deepshaft 9?", "Brineholt Tidings",
         [(url("tidings", "/news/22-6-412/miners-trapped-after-collapse-at-cinderfell.html"), "Seventeen miners are trapped")], 2,
         {"accept": ["the Tidings", "Tidings"]}),
        ("Which company employed the two Deepshaft 9 workers who were missing from Coldforge Mining's shift list?", "Slatebrook Haulage",
         [(url("moot", "/ruling/1292-31/"), "Slatebrook Haulage")], 3, {"notes": "only on rulings.khr, which Lanthorn does not index"}),
        ("How large a fine (hold-price), in marks, did the Moot of Holds impose on Coldforge Mining over Deepshaft 9?", "4,200,000",
         [(url("moot", "/ruling/1292-31/"), "4,200,000 marks")], 2, {"kind": "number", "accept": ["4.2 million"]}),
        ("Who led the rescuers who broke into the Deepshaft 9 refuge chamber?", "Greystone Magna",
         [(url("moot", "/ruling/1292-31/"), "led by Greystone Magna")], 2, {}),
        ("Who lent the Deepshaft 9 refuge lamp to the Museum of the Deep Halls?", "Cinder Asta",
         [(url("museum", "/object/DH.1290.07/"), "Lent by Cinder Asta")], 2, {}),
        ("What reader name does the Ostmere Athenaeum give its members for reading the Ostmere Courier?", "athenaeum",
         [(url("athenaeum", "/weave-resources/"), "Reader name: <b>athenaeum")], 2, {}),
        ("What pass code does the Ostmere Athenaeum give its members for reading the Ostmere Courier?", "NINEFORDS-412",
         [(url("athenaeum", "/weave-resources/"), "NINEFORDS-412")], 2, {}),
        ("What is the password to the Tallow Boards' Back Room?", "wicket",
         [(url("tallowboards", f"/thread/{_thread_id('Forum rules (READ BEFORE POSTING)')}/"), "name of my first cat"),
          (url("tallowboards", f"/thread/{_thread_id('Post your pets!')}/"), "Wicket, my first cat")], 3, {"modality": "interaction"}),
        ("According to a rumour in the Tallow Boards' Back Room, who was the Guild engineer on the Tarrow Canal bid-scoring panel?", "Hemming Lockwright",
         [(url("tallowboards", "/forum/backroom/"), "tallow-backroom")], 4, {"modality": "interaction",
                                                                            "steps": [["goto", url("tallowboards", "/forum/backroom/")], ["fill", "#pw-u", "member"],
                                                                                      ["fill", "#pw-p", "wicket"], ["click", "#pw-form button"], ["read", "#pw-rest"]]}),
        ("Gildmere Works has taken its website down. According to an archived copy of its staff page, what organisation is Hemming Lockwright now an examiner for?",
         "Guild of Lock-wrights", [(url("stillframe", "/frame/411-06-06/gildmere.ves/people/"), "independent examiner for the Guild of Lock-wrights")], 3,
         {"accept": ["the Guild of Lock-wrights", "Guild of Lockwrights"]}),
        ("How many times does Harthwick Lighthouse flash in each cycle of its current light?", "3",
         [(url("courier", "/412/07/01/harthwick-lighthouse-gets-a-new-light-pattern/"), "three times every twelve seconds")], 2,
         {"kind": "number", "accept": ["three"], "notes": "the Commonplace folio and Quorum's accepted answer are out of date (two flashes)"}),
        ("How many seconds long is each cycle of Harthwick Lighthouse's current light?", "12",
         [(url("courier", "/412/07/01/harthwick-lighthouse-gets-a-new-light-pattern/"), "three times every twelve seconds")], 2,
         {"kind": "number", "accept": ["twelve"], "notes": "stale sources say nine"}),
        ("At what time does the Pith crossing of 3 Mire 412 begin as seen from Harthwick?", "21:20",
         [(url("observatory", "/crossing/"), "<td>Harthwick</td><td>21:20</td>")], 1, {}),
        ("What is the Guild of Numerists' current status for the Cresselle Conjecture?", "Under review",
         [(url("numerary", "/roll/TP-1/"), "Under review")], 2, {"notes": "the most-voted Quorum answer wrongly says it is proven"}),
        ("A Moot ruling is dated 9.8.1292 HR. What is that date in the Concord Reckoning?", "9 Gale 412",
         [(url("moot", "/reckoning/"), "take away 880")], 2, {"accept": ["412·08·09", "9/8/412"], "notes": "a highly voted Quorum answer says to subtract 800"}),
        ("How many bits does a Brineholt Tramways day pass cost in total?", "14",
         [(url("tramways", "/fares/"), "1t 2b")], 2, {"kind": "number", "notes": "1 tally 2 bits, and a tally is twelve bits"}),
        ("A tabby cat called Pip went missing in Keelwater during Storm Petrel. Which shelter has her now?", "Keelwater Rescue",
         [(url("whiskerhaven", "/pet/pip/"), "Keelwater Rescue")], 3, {"notes": "noticeboard.fol lost note, tramways.slt lost property, whiskerhaven.fol found animals"}),
        ("Which blogger spotted the stolen Quenby clock hand at a Hollowmarket viewing?", "Wenna Larkfield",
         [(url("wrenwrites", "/412/05/viewing-day-at-hollowmarket.html"), "Q.C. 331")], 3, {"accept": ["Wren Writes"]}),
        ("What is the Gallery-class Skylark fare from Lanternport to Ostmere, in lumes?", "129.71",
         [(url("emberline", "/routes/lanternport-ostmere/"), "129.71 lm")], 2,
         {"kind": "number", "tolerance": 0.01, "notes": "fares are charged in the currency of the departure port"}),
        ("Two people are named as inventors on the patent for a slate with a writable back face. Which of them had left Vantle before the patent was granted?",
         "Corwen Talley", [(url("patents", "/roll/405-118/"), "Corwen Talley"), (url("vantle", "/about/"), "Corwen Talley left the company in 406")], 3, {}),
        ("Who posted on Chatter about buying a green hat at the Marrowby night market?", "Anouk Belvaine",
         [(url("chatter", "/@anouk_belvaine"), "green hat")], 3, {"notes": "ties together the Crier gossip and a Noticeboard personal ad"}),
        ("On what date is the 412 Vault Cup final?", "30 Mire 412", [(url("vaultball", "/vault-cup/"), "30 Mire 412")], 1, {}),
        ("How many points has the captain of the Harrowdeep Hammers scored in the 412 Premier Circuit?", str(PLAYER["hammers-anvilmark-ketta"].stats["points"]),
         [(url("vaultball", "/players/hammers-anvilmark-ketta/"), "Anvilmark Ketta")], 3,
         {"kind": "number", "notes": "the captain is Anvilmark Ketta; a team-mate, Greystone Ketta, shares the given name"}),
        ("What year of the Flame (Oddavar's reckoning) corresponds to 412 CR?", "1812",
         [(url("synod", "/notice/1812-5-1/"), "year 1812 of the Flame")], 2, {"kind": "number", "notes": "synod.odd is not indexed by Lanthorn"}),
        ("What key number is written on Ossa Watcher's hidden page about the Registry's seventeenth floor?", "RT 17",
         [(url("ossawatcher", "/x/the-ledger/"), "RT 17")], 3, {"modality": "source", "notes": "linked only from an HTML comment on the front page"}),
        ("Which Emberline ferry route is suspended until 1 Mire 412?", "Saltspire to Wrackmouth",
         [(url("emberline", "/service-updates/"), "Service resumes 1 Mire 412")], 1, {"accept": ["Saltspire-Wrackmouth", "Saltspire Wrackmouth"]}),
        ("Where does the short link snip.ves/go finally lead? Give the domain of the final page.", "stillframe.hal",
         [(url("snip", "/+go3"), "stillframe.hal")], 3, {"notes": "go redirects to go2, then go3, then Stillframe"}),
        ("How many Concordat Assembly delegates voted yes on the Tarrow Canal (Widening) Act?", str(next(b for b in BILLS if b.title.startswith("Tarrow")).tally["yes"]),
         [(url("assembly", "/bills/AB-411-005/"), "Yes 63")], 2, {"kind": "number"}),
        ("Which version of Weave OS added the Kethren (HR) calendar option?", "6.4", [(url("vantle", "/weave-os/"), "Adds Kethren (HR) calendar option")], 1,
         {"kind": "number"}),
        ("The Old Keeper's Cottage at Spire Point, Saltspire, is for sale. What is the asking price in tallies?", "118,000",
         [(url("hearthfind", "/home/HF412001/"), "118,000t")], 2, {"kind": "number"}),
        ("How many measures of lamp oil did the Spire lighthouse at Saltspire use in 411?", "3,112",
         [(url("spirekeeper", "/log/412-01/"), "3,112 measures")], 2, {"kind": "number", "notes": "only in the keeper's log, not indexed by Lanthorn"}),
        ("When does the Fathom expansion 'Ninth Trench' come out?", "14 Mire 412",
         [(url("radio", "/transcripts/loom-talk-412-08-10/"), "fourteenth of Mire")], 2, {"notes": "some people say 3 Mire, which is wrong"}),
        ("How many named storms had there been in 412 by the end of Storm Petrel?", "16",
         [(url("weather", "/storms/"), "Sixteen storms have been named this year")], 2, {"kind": "number", "accept": ["sixteen"]}),
        ("What will the next named storm after Petrel be called?", "Quail", [(url("weather", "/storms/"), "Quail")], 1, {}),
        ("Which company in Tarrow has a registered office in Canalside Chambers, 17 Canal Street?", "Sallow Fen Holdings",
         [(url("registry", "/company/CR-47-409117/"), "Canalside Chambers, 17 Canal Street")], 2, {}),
        ("What was the hammer price of the punched ribbon fragment attributed to Temmet Aske at Hollowmarket, in crowns?", "17,250",
         [(url("hollowmarket", "/lot/4402/"), "Hammer price: 17,250 cr")], 2, {"kind": "number"}),
    ]
    for question, answer, ev, hops, kw in S:
        q = Q(question, answer, H if hops >= 2 else "medium", ev, hops=hops, topic="storylines")
        for k, v in kw.items():
            setattr(q, k, v)
        out.append(q)
    return out


def _thread_id(title):
    page = raw(url("tallowboards", "/forum/general/"))
    return re.search(r'<a href="/thread/(\d+)/">' + re.escape(html.escape(title, quote=False)) + "<", page).group(1)


# ---------------------------------------------------------------------------
def verify(qs):
    bad = []
    for q in qs:
        for u, needle in q.evidence:
            page = raw(u)
            if page is None:
                bad.append((q, f"missing page {u}"))
            elif needle and needle not in page:
                bad.append((q, f"'{needle}' not found in {u}"))
        if not q.evidence and not q.steps:
            bad.append((q, "no evidence and no steps"))
    return bad


def main():
    rng = stream("evals-v1")
    qs = easy(rng) + medium(rng) + hard(rng)
    counters = {}
    for q in qs:
        counters[q.difficulty] = counters.get(q.difficulty, 0) + 1
        q.id = f"{q.difficulty[0]}{counters[q.difficulty]:03d}"
        if q.modality == "interaction" and not q.notes:
            q.notes = "answer appears only after using the page's form"
    bad = verify(qs)
    for q, why in bad:
        print(f"UNVERIFIED {q.id}: {q.question[:70]}... -> {why}", file=sys.stderr)
    os.makedirs("evals", exist_ok=True)
    with open("evals/questions.jsonl", "w") as f:
        for q in qs:
            d = asdict(q)
            d["evidence"] = [{"url": u, "text": t} for u, t in q.evidence]
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    by = {}
    for q in qs:
        by.setdefault(q.difficulty, []).append(q)
    print(f"{len(qs)} questions: " + ", ".join(f"{k} {len(v)}" for k, v in by.items()) + f"; {len(bad)} failed verification")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
