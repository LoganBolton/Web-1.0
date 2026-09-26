"""commonplace.hal: the encyclopedia of Averra.

Folios are kept by guilds and edited on their own schedules, so some are out
of date. Every folio shows when it was last revised in its Chronicle tab.
"""
import json

from ..engine import kit, links, svg
from ..engine.domains import url
from ..engine.linkify import Linker
from ..engine.rng import slug, stream, short_hash
from ..engine.web import esc
from ..world import culture
from ..world.calendar import ADate, TODAY, MONTHS, WEEKDAYS
from ..world.econ import CURRENCY_NAMES
from ..world.geo import NATIONS, CITIES, CITY, LANDMARKS, cities_of
from ..world.history import EVENTS, TOPICS
from ..world.orgs import COMPANIES, COMPANY, PARTIES, SEATS, UNIVERSITIES, GUILDS
from ..world.people import NOTABLES, NOTABLE, HEADS
from ..world.sports import TEAMS, standings
from ..world.stories import STORIES

CSS = """
body{margin:0;background:#fff;color:#202122;font:15px/1.6 'Iowan Old Style','Palatino Linotype',Georgia,serif}
.top{border-bottom:1px solid #a2a9b1;display:flex;align-items:center;gap:20px;padding:8px 20px;background:#f8f9fa}
.top .brand{font-size:22px;color:#202122;text-decoration:none;font-variant:small-caps;letter-spacing:1px}
.top form{margin-left:auto}.top input{padding:5px 8px;width:260px;border:1px solid #a2a9b1}
.wrap{display:flex;max-width:1180px;margin:0 auto}
.side{width:170px;padding:16px;font-size:13px;flex-shrink:0}.side a{display:block;margin:3px 0;color:#3366cc}
.side h4{margin:14px 0 4px;color:#54595d;font:bold 12px sans-serif;text-transform:uppercase}
.content{flex:1;padding:16px 28px;min-width:0;border-left:1px solid #eaecf0}
a{color:#3366cc;text-decoration:none}a:hover{text-decoration:underline}
h1{font-weight:normal;font-size:30px;border-bottom:1px solid #a2a9b1;margin:4px 0 2px}
h2{font-weight:normal;border-bottom:1px solid #a2a9b1;font-size:22px;margin-top:26px}
.kept{font-size:12px;color:#54595d;margin-bottom:12px;font-family:sans-serif}
.infobox{float:right;width:280px;border:1px solid #a2a9b1;background:#f8f9fa;margin:0 0 14px 18px;font-size:13px;padding:6px}
.infobox .ititle{text-align:center;font-weight:bold;font-size:15px;padding:4px;background:#e6e1d3}
.infobox img{width:100%;height:auto;display:block;margin:6px 0}
.infobox table{width:100%}.infobox th{text-align:left;vertical-align:top;padding:2px 6px 2px 0;width:40%}
.tabbar{border-bottom:1px solid #a2a9b1;margin:10px 0;font-family:sans-serif;font-size:13px}
.tabbar a{display:inline-block;padding:5px 12px;border:1px solid transparent;margin-bottom:-1px}
.tabbar a.on{border:1px solid #a2a9b1;border-bottom-color:#fff;background:#fff;color:#202122}
.note{background:#fef6e7;border:1px solid #fc3;padding:8px 12px;font-size:13px;font-family:sans-serif;margin:8px 0}
.cats{border:1px solid #a2a9b1;background:#f8f9fa;padding:6px 10px;font-size:13px;margin-top:30px;clear:both}
.refs{font-size:13px}.refs li{margin:2px 0}
table.wt{border-collapse:collapse;margin:10px 0}table.wt td,table.wt th{border:1px solid #a2a9b1;padding:4px 8px}
table.wt th{background:#eaecf0}
.cols{columns:3;font-size:14px}.cols div{break-inside:avoid}
.letters a{display:inline-block;padding:2px 7px;border:1px solid #ddd;margin:2px}
.fp{display:grid;grid-template-columns:1fr 1fr;gap:16px}.fp>div{border:1px solid #a2a9b1;padding:8px 14px}
.fp h3{margin:0 -14px 8px;padding:4px 14px;background:#cedff2;font-size:16px}
sup a{font-size:11px}
@media(max-width:800px){.side{display:none}.infobox{float:none;width:auto;margin:0}.fp{grid-template-columns:1fr}}
"""

GUILDS_KEEPING = {
    "person": "Guild of Chroniclers", "place": "Guild of Cartographers",
    "nation": "Guild of Cartographers", "company": "Guild of Merchants",
    "event": "Guild of Chroniclers", "topic": "Guild of Natural Philosophers",
    "team": "Guild of Players", "party": "Guild of Chroniclers", "work": "Guild of Players and Poets",
    "landmark": "Guild of Cartographers", "institution": "Guild of Chroniclers",
    "math": "Guild of Numerists",
}


class Folio:
    def __init__(self, title, kind, summary, sections=(), infobox=(), image=None, cats=(),
                 disputes=(), refs=(), last_edit=None, see_also=(), notice=None, alias=()):
        self.title, self.kind, self.summary = title, kind, summary
        self.sections = list(sections)
        self.infobox = list(infobox)
        self.image = image  # (svg, caption)
        self.cats = list(cats)
        self.disputes = list(disputes)
        self.refs = list(refs)  # (label, url)
        self.see_also = list(see_also)
        self.notice = notice
        self.alias = list(alias)
        rng = stream("folio", title)
        self.last_edit = last_edit or ADate(rng.randint(405, 411), rng.randint(1, 10), rng.randint(1, 36))
        self.number = 1000 + int(short_hash("folio", title, n=6), 16) % 9000
        self.slug = slug(title)

    @property
    def url(self):
        return links.folio(self.title)


def P(*ps):
    return list(ps)


def build(web, site):
    folios = []
    add = folios.append
    story_url = {s.id: links.courier_story(s) for s in STORIES if "courier" in s.outlets}

    def refs_for(tag):
        return [(f"{s.headline}, Ostmere Courier, {s.date.long()}", story_url[s.id])
                for s in STORIES if tag in s.tags and s.id in story_url and s.date <= TODAY]

    # ---- nations ------------------------------------------------------------
    for n in NATIONS.values():
        head = NOTABLE[HEADS[n.code]]
        cities = sorted(cities_of(n.code), key=lambda c: -c.population)
        hist = [e for e in EVENTS if n.short.lower() in " ".join(e.tags) or
                (e.place and CITY.get(e.place) and CITY[e.place].nation == n.code)]
        add(Folio(n.name, "nation", P(
            f"{n.name} is a nation of Averra. Its capital is {n.capital}. {n.summary}",
            f"The head of state is the {n.head_title}, currently {head.full}. The currency is the "
            f"{n.currency}, divided into {n.sub_per_unit} {n.currency_sub}s."),
            sections=[("Places", P("The largest places are " + ", ".join(
                f"{c.name} ({c.population:,})" for c in cities[:4]) + ".")),
                ("History", P(*[f"{e.span}: {e.title}. {e.text}" for e in hist]) or
                 P("The early history of Oddavar is not known outside the Synod.")),
                ("On the Weave", P(f"Sites of {n.short} use the .{n.tld} domain."))],
            infobox=[("Capital", n.capital), ("Government", n.government),
                     (n.head_title, head.full), ("Population", f"{n.population:,}"),
                     ("Currency", n.currency), ("Language", n.language), ("Founded", n.founded),
                     ("Motto", n.motto)],
            image=(svg.flag(n.code), f"Flag of {n.short}"), cats=["Nations"],
            alias=[n.short]))

    # ---- cities -------------------------------------------------------------
    for c in CITIES:
        n = NATIONS[c.nation]
        lms = [lm for lm in LANDMARKS if lm.city == c.name]
        secs = []
        if c.districts:
            secs.append(("Districts", P(f"{c.name} is divided into {len(c.districts)} districts: "
                                        + ", ".join(c.districts) + ".")))
        if lms:
            secs.append(("Landmarks", P(*[f"{lm.name}: {lm.description}" for lm in lms])))
        mayor_title = {"VEY": "Reeve", "SLT": "Harbourmaster", "KHR": "Holdwarden",
                       "PEL": "Provost", "ODD": "Prior"}[c.nation]
        founded = f"founded in {c.founded} CR" if c.founded > -9000 else "of ancient foundation"
        if c.nation == "KHR":
            founded += f" ({c.founded + 880} HR)"
        add(Folio(c.name, "place", P(
            f"{c.name} is a {c.kind} in {n.name}, {founded}. It is known for {c.known_for}.",
            f"At the last Guild count it had {c.population:,} inhabitants. It stands "
            f"{c.elevation:,} ells above the Northmole datum."),
            sections=secs + [("Climate", P(
                f"The mean temperature over the year is {c.mean_temp} degrees Harl, and about "
                f"{c.rain:,} thumbs of rain fall in a year. Current forecasts are kept by the "
                f"Concordat Weather Office."))],
            infobox=[("Nation", n.short), ("Population", f"{c.population:,}"),
                     ("Founded", f"{c.founded} CR" if c.founded > -9000 else "unknown"),
                     ("Elevation", f"{c.elevation:,} ells"), ("Postcode prefix", c.postal),
                     ("Chief officer", mayor_title)],
            image=(svg.landscape(c.name, {"port": "sea", "island": "sea", "mountain": "mountains",
                                          "moor": "moor", "marsh": "marsh", "capital": "city"}
                                 .get(c.kind, "hills"), caption=c.name), f"{c.name}"),
            cats=["Places", f"Places in {n.short}"],
            refs=[("Chartroom sheet", links.place(c.name)),
                  ("Weather Office climate", links.city_weather(c.name))]))

    # ---- landmarks ----------------------------------------------------------
    for lm in LANDMARKS:
        extra = {}
        if lm.name == "Harthwick Lighthouse":
            # Deliberately out of date: the pattern changed on 1 Sheaf 412.
            extra = dict(last_edit=ADate(402, 3, 3), disputes=[
                ("Some visitors report a different light pattern since Sheaf 412.",
                 "Unconfirmed. The Guild of Cartographers has not re-surveyed the light.")])
        if lm.name == "Wendmoor Standing Stones":
            extra = dict(disputes=[("Number of stones", "23 by the Guild survey of 390 CR; 24 in "
                                    "Hollis Thornby's poem 'The Leaner', which counts a buried stump.")])
        add(Folio(lm.name, "landmark", P(f"{lm.name} is a {lm.kind} in {lm.city}. {lm.description}"),
                  infobox=[("Kind", lm.kind), ("Place", lm.city),
                           ("Built", f"{lm.built} CR" if lm.built > -9000 else "natural")],
                  image=(svg.landscape(lm.name, "sea" if lm.kind == "lighthouse" else "hills",
                                       caption=lm.name), lm.name),
                  cats=["Landmarks"], **extra))

    # ---- people -------------------------------------------------------------
    special_person = {
        "temmet-aske": dict(disputes=[("Year the Loom was completed",
                                       "367 CR by the University's own record; 366 CR in Aske's "
                                       "notebook, where the engine is said to have 'first woven' "
                                       "on the last Hollowday.")]),
        "oswin-solavey": dict(disputes=[("Year of birth", "81 CR in the Observatory register; 79 CR "
                                         "on his gravestone in Lanternport.")]),
        "talvi-aubrel": dict(last_edit=ADate(412, 4, 20),
                             notice="This folio concerns a proof under review. Its status may change."),
        "verity-ashford": dict(last_edit=ADate(412, 4, 22)),
    }
    for p in NOTABLES:
        n = NATIONS[p.nation]
        sections = []
        if p.died:
            life = f"({p.born.long()} – {p.died.long()})"
        else:
            life = f"(born {p.born.long()})"
        order_note = ""
        if p.nation == "KHR":
            order_note = (f" As is Kethren custom, the clan name {p.name.family} is written first; "
                          f"{p.name.given} is the given name.")
        evs = [e for e in EVENTS if p.id in e.people]
        if evs:
            sections.append(("Life and work", P(*[f"{e.span}: {e.text}" for e in evs])))
        affiliations = [c for c in COMPANIES if c.ceo == p.id or p.id in c.founders]
        if affiliations:
            sections.append(("Companies", P(*[
                f"{'Chief executive' if c.ceo == p.id else 'Founder'} of {c.name} ({c.industry}), "
                f"founded {c.founded} CR in {c.city}." for c in affiliations])))
        works = [b for b in culture.BOOKS if b.author == p.full]
        films = [f for f in culture.FILMS if f.director == p.full]
        if works:
            sections.append(("Books", P(*[f"{b.title} ({b.year})" for b in works])))
        if films:
            sections.append(("Films", P(*[f"{f.title} ({f.year})" for f in films])))
        kw = special_person.get(p.id, {})
        add(Folio(p.full, "person", P(
            f"{p.full} {life} {'was' if p.died else 'is'} a {n.demonym} "
            f"{p.occupation[0].lower() + p.occupation[1:]}.{order_note}", p.bio),
            sections=sections,
            infobox=[("Born", f"{p.born.long()}, {p.city}")] +
                    ([("Died", p.died.long())] if p.died else [("Age", str(p.age()))]) +
                    [("Nationality", n.demonym), ("Occupation", p.occupation)],
            image=(svg.portrait(p.id, 280, 300), f"A likeness of {p.full}"),
            cats=["People"] + [f"People: {t.replace('-', ' ')}" for t in p.tags[:2]],
            refs=refs_for(p.id), **kw))

    # ---- companies ------------------------------------------------------------
    for c in COMPANIES:
        ceo = NOTABLE[c.ceo].full if c.ceo in NOTABLE else c.ceo
        founders = [NOTABLE[f].full if f in NOTABLE else f for f in c.founders]
        box = [("Industry", c.industry), ("Founded", f"{c.founded} CR, {c.city}"),
               ("Chief executive", ceo)]
        if founders:
            box.append(("Founders", ", ".join(founders)))
        if c.ticker:
            box.append(("Listed", f"Brineholt Exchange: {c.ticker}"))
        if c.domain:
            box.append(("On the Weave", c.domain))
        box.append(("Employees", f"about {c.employees:,}"))
        refs = []
        if c.ticker:
            refs.append((f"{c.ticker} on the Brineholt Exchange", links.listing(c.ticker)))
        if c.nation == "VEY":
            refs.append(("Concordat Registry record", links.company_registry(c)))
        if c.domain:
            refs.append((f"Official site", f"http://{c.domain}/"))
        summary = P(f"{c.name} is a {NATIONS[c.nation].demonym} company in the {c.industry.lower()} "
                    f"trade, based in {c.city}. {c.description}")
        kw = {}
        if c.id == "morrowmedia":
            # The folio does not mention the Crier. The Registry does.
            summary = P(f"Morrow Media Group is a Veylish media company based in Ostmere. It runs the "
                        f"Morrow portal, one of the most visited pages on the Weave.")
        if c.id == "gildmere":
            kw = dict(last_edit=ADate(412, 4, 21), notice="This folio concerns a matter before the "
                      "Concordat Assembly.")
            summary.append("In Thaw 412 it was awarded the contract to widen the Tarrow Canal. On "
                           "20 Bloom 412 the Ostmere Courier reported that its chief executive, Osric "
                           "Gildmere, is the brother-in-law of the Minister of Canals.")
        refs += refs_for(c.id)
        add(Folio(c.name, "company", summary, infobox=box,
                  image=(svg.logo(c.name, c.id, 280, 70), f"Mark of {c.name}"),
                  cats=["Companies", f"Companies of {NATIONS[c.nation].short}"], refs=refs, **kw))

    # ---- events ---------------------------------------------------------------
    for e in EVENTS:
        add(Folio(e.title, "event", P(f"The {e.title} ({e.span}). {e.text}" if not
                                      e.title.startswith("The ") else f"{e.title} ({e.span}). {e.text}"),
                  infobox=[("Date", e.span), ("Place", e.place or "various")],
                  cats=["Events", f"Events of the {((e.year // 100) + 1)}th century CR" if e.year >= 0
                        else "Events before the Concord"]))

    # ---- current affairs, written with a lag -------------------------------------
    add(Folio("Deepshaft 9 collapse", "event", P(
        "The Deepshaft 9 collapse was a roof fall in Coldforge Mining's Deepshaft 9 workings at "
        "Cinderfell on 22 Crest 412 (22.6.1292 HR). Sixteen miners were trapped about 600 ells below "
        "ground. All sixteen were rescued alive on 28 Crest after six days in a refuge chamber.",
        "The rescue was led by Greystone Magna of the Harrowdeep Mine Rescue."),
        sections=[("Inquiry", P("The Moot of Holds ordered an inquiry. Its ruling is published by "
                                "Moot Rulings."))],
        infobox=[("Date", "22 Crest 412"), ("Place", "Cinderfell"), ("Trapped", "16"),
                 ("Deaths", "none"), ("Operator", "Coldforge Mining")],
        disputes=[("Number trapped", "Early press reports gave 14 (Ostmere Courier) and 17 "
                   "(Brineholt Tidings). Coldforge Mining later confirmed 16, including two "
                   "contractors missing from its shift list.")],
        cats=["Events", "Mining disasters"], refs=refs_for("deepshaft"),
        last_edit=ADate(412, 7, 30),
        image=(svg.landscape("deepshaft", "mountains", caption="The Deepshaft pithead, Cinderfell"),
               "Deepshaft pithead")))
    add(Folio("Tarrow Canal affair", "event", P(
        "The Tarrow Canal affair concerns the award of the 1.84 billion crown contract to widen the "
        "Tarrow Canal to Gildmere Works on 4 Thaw 412.",
        "On 20 Bloom 412 the Ostmere Courier reported that the chief executive of Gildmere Works, "
        "Osric Gildmere, is married to Maud Ashford, sister of the Minister of Canals, Verity Ashford."),
        notice="This folio concerns a developing matter and was last revised on 21 Bloom 412.",
        cats=["Events", "Politics of Veyl"], refs=refs_for("canal-scandal")[:2],
        last_edit=ADate(412, 4, 21)))
    add(Folio("Vantle Slate 7", "work", P(
        "The Slate 7 is a handheld loom made by Vantle, announced on 3 Sheaf 412 and released on "
        "1 Gale 412. It has a second glass face on its back.",
        "It is sold with 64 or 128 weaves of memory, at 1,299 and 1,549 crowns."),
        infobox=[("Maker", "Vantle"), ("Released", "1 Gale 412"), ("Memory", "64 or 128 weaves"),
                 ("Price at launch", "1,299 cr / 1,549 cr"), ("Charger", "VC-7A")],
        cats=["Looms and devices"], last_edit=ADate(412, 8, 5),
        image=(svg.product("slate", "slate7", "SLATE 7"), "The Slate 7")))

    # ---- topics ---------------------------------------------------------------
    for t, text in TOPICS.items():
        extra = {}
        if t == "Tidal prime":
            extra = dict(sections=[("First tidal primes", P(
                "The first tidal primes are " + ", ".join(str(x) for x in _tidal_primes(12)) + "."))])
        add(Folio(t, "math" if t == "Tidal prime" else "topic", P(text), cats=["Topics"], **extra))
    add(Folio("Cresselle Conjecture", "math", P(
        "The Cresselle Conjecture states that there are infinitely many tidal primes. It was posed "
        "by Ysolde Cresselle in 339 CR in her monograph 'Tidal Primes'.",
        "On 30 Dusk 411 Talvi Aubrel announced a proof. A gap in its third lemma was found by "
        "Flint Gisla in Bloom 412."), notice="The status of this problem is kept by the Guild of "
        "Numerists. See the Numerary for the current status.",
        infobox=[("Posed", "339 CR"), ("By", "Ysolde Cresselle"), ("Status", "open")],
        cats=["Mathematics"], last_edit=ADate(412, 4, 25),
        refs=[("Numerary roll entry", links.lemma("TP-1"))]))
    add(Folio("Concord Reckoning", "topic", P(
        "The Concord Reckoning is the calendar used across most of Averra. Years are counted from "
        "the Treaty of the Nine Fords. A year has ten months of 36 days, named " +
        ", ".join(MONTHS) + ", followed by five Hollowdays that belong to no month.",
        "The week has six days: " + ", ".join(WEEKDAYS) + ". Stillday is the day of rest.",
        "The Kethren Holds count years from the founding of Harrowdeep (Hold Reckoning, HR). "
        "To convert, add 880 to a CR year."),
        sections=[("Writing dates", P(
            "The Concordat writes dates as year, month, day with raised dots (412·08·17). "
            "Saltmarch writes day/month/year (17/8/412). The Holds write day.month.year in HR "
            "(17.8.1292 HR). The Pellucid Isles write the month name first (Gale 17, 412)."))],
        cats=["Topics", "Calendar"], alias=["CR"]))
    for code, nm in CURRENCY_NAMES.items():
        pass

    # ---- teams, parties, works, institutions ------------------------------------
    table = {r["team"]: i + 1 for i, r in enumerate(standings(ADate(412, 7, 20)))}
    for t in TEAMS:
        add(Folio(t.name, "team", P(
            f"The {t.name} are a vaultball club from {t.city}, founded in {t.founded} CR. They play "
            f"at {t.ground}, which holds {t.capacity:,}. Supporters call them {t.nickname}.",
            f"As of the last revision they stood {_ord(table[t.id])} in the Premier Circuit."),
            infobox=[("Ground", t.ground), ("Capacity", f"{t.capacity:,}"), ("Founded", f"{t.founded} CR"),
                     ("Head coach", t.coach)], cats=["Vaultball clubs"],
            last_edit=ADate(412, 7, 20), refs=[("Club page", links.team(t.id))]))
    for pid, pdat in PARTIES.items():
        leader = NOTABLE[pdat["leader"]].full if pdat["leader"] in NOTABLE else pdat["leader"]
        add(Folio(pdat["name"], "party", P(f"{pdat['name']} is a party in the Concordat Assembly. "
                                           f"{pdat['blurb']}", f"It won {SEATS[pid]} of 90 seats in 411."),
                  infobox=[("Leader", leader), ("Seats", f"{SEATS[pid]} of 90")],
                  cats=["Political parties of Veyl"]))
    for f in culture.FILMS[:6]:
        add(Folio(f"{f.title} (film)", "work", P(f"{f.title} is a {f.year} {f.genre} film directed by {f.director}. "
                                     f"{f.synopsis}"),
                  infobox=[("Director", f.director), ("Year", str(f.year)), ("Runtime", f"{f.runtime} min"),
                           ("Studio", f.studio)], cats=["Films"],
                  refs=[("Reelhouse entry", links.film(f.id))]))
    for b in culture.BOOKS[:12]:
        add(Folio(b.title, "work", P(f"{b.title} is a {b.genre} book by {b.author}, first published "
                                     f"in {b.year} CR. {b.blurb}"),
                  infobox=[("Author", b.author), ("Published", f"{b.year} CR"), ("Publisher", b.publisher),
                           ("QN", b.qn)], cats=["Books"], alias=[]))
    for a in culture.ARTISTS:
        albums = [al for al in culture.ALBUMS if al.artist == a.id]
        add(Folio(a.name, "work", P(f"{a.name} is a {a.genre} act from {a.city}, active since {a.formed} CR. "
                                    f"{a.bio}"),
                  sections=[("Albums", P(*[f"{al.title} ({al.release.year})" for al in albums
                                           if al.release <= ADate(412, 3, 1)]))],
                  cats=["Musicians"], last_edit=ADate(412, 3, 1))) if a.id != "nell-hedgecote" else None
    for name, city, founded, dom in UNIVERSITIES:
        add(Folio(name, "institution", P(f"{name} is a place of learning in {city}, founded {founded} CR."),
                  infobox=[("Founded", f"{founded} CR"), ("Place", city)] +
                          ([("On the Weave", dom)] if dom else []), cats=["Universities"]))
    for name, dom, blurb in GUILDS:
        add(Folio(name, "institution", P(f"The {name} is a learned guild. {blurb}"),
                  infobox=[("On the Weave", dom or "none")], cats=["Guilds"]))

    render(web, site, folios)


def _ord(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def _is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def _tidal_primes(k):
    out, n = [], 2
    while len(out) < k:
        if _is_prime(n) and _is_prime(n + 12) and sum(map(int, str(n))) % 3 == 1:
            out.append(n)
        n += 1
    return out


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} &mdash; The Commonplace</title><link rel="stylesheet" href="/style.css"></head><body>
<div class="top"><a class="brand" href="/">The Commonplace</a>
<span style="font-size:12px;color:#54595d">kept by the learned guilds</span>
<form action="/search/" method="get"><input name="q" placeholder="Search the Commonplace" aria-label="Search">
<button>Search</button></form></div>
<div class="wrap"><nav class="side">
<a href="/">Front leaf</a><a href="/index/a/">All folios A&ndash;Z</a><a href="/categories/">Categories</a>
<a href="/random/">A random folio</a><a href="/about/">About</a>
<h4>Elsewhere</h4><a href="{url('numerary')}">Numerary</a><a href="{url('lexicon')}">Lexicon</a>
<a href="{url('chartroom')}">Chartroom</a><a href="{url('stillframe')}">Stillframe</a>
</nav><div class="content">{body}</div></div>
{kw.get('scripts', '')}</body></html>"""


def render(web, site, folios):
    site.shell = shell
    site.write("/style.css", CSS)
    folios = [f for f in folios if f is not None]
    seen = set()
    for f in folios:
        if f.slug in seen:
            f.title = f"{f.title} ({f.kind})"
            f.slug = slug(f.title)
        seen.add(f.slug)
    targets = {}
    for f in folios:
        targets[f.title] = f.url
        for al in f.alias:
            targets.setdefault(al, f.url)
    linker = Linker(targets)
    cats = {}
    for f in folios:
        for c in f.cats:
            cats.setdefault(c, []).append(f)

    for f in folios:
        used = set()
        skip = {f.title, *f.alias}
        img = ""
        if f.image:
            path = f"/img/{f.slug}.svg"
            site.write(path, f.image[0])
            img = f'<img src="{path}" alt="{esc(f.image[1])}">'
        box = ""
        if f.infobox or img:
            rows = "".join(f"<tr><th>{esc(k)}</th><td>{linker(v, skip, used)}</td></tr>" for k, v in f.infobox)
            box = (f'<div class="infobox"><div class="ititle">{esc(f.title)}</div>{img}'
                   f'<table>{rows}</table></div>')
        notice = f'<div class="note">{esc(f.notice)}</div>' if f.notice else ""
        body = "".join(f"<p>{linker(p, skip, used)}</p>" for p in f.summary)
        toc = ""
        if len(f.sections) >= 2:
            toc = ('<div class="note" style="background:#f8f9fa;border-color:#a2a9b1;display:inline-block">'
                   '<b>Contents</b><ol>' + "".join(f'<li><a href="#{slug(h)}">{esc(h)}</a></li>'
                                                   for h, _ in f.sections) + "</ol></div>")
        for h, ps in f.sections:
            body += f'<h2 id="{slug(h)}">{esc(h)}</h2>' + "".join(
                f"<p>{linker(p, skip, used)}</p>" for p in ps)
        if f.refs:
            body += '<h2 id="sources">Sources</h2><ol class="refs">' + "".join(
                f'<li><a href="{esc(u)}">{esc(lab)}</a></li>' for lab, u in f.refs) + "</ol>"
        disputes = ("<p>The keeping guild records the following disagreements.</p>" + kit.table(
            ["Question", "What the sources say"], [[q, a] for q, a in f.disputes], cls="wt")
            if f.disputes else "<p>No disputes are recorded for this folio.</p>")
        rng = stream("chronicle", f.title)
        revs = [f.last_edit]
        d = f.last_edit
        for _ in range(rng.randint(1, 6)):
            d = d - rng.randint(20, 400)
            revs.append(d)
        editors = ["Scribe Aubrel", "Clerk Hollin", "Scribe Tamsin W.", "Keeper Oda", "Clerk 7",
                   "Scribe Nerine", "Guild bot"]
        chron = kit.table(["Revised", "By", "Note"], [
            [r.long(), rng.choice(editors), rng.choice(["small corrections", "new sources",
                                                          "expanded", "reworded", "infobox",
                                                          "first written" if i == len(revs) - 1 else "tidied"])]
            for i, r in enumerate(revs)], cls="wt")
        cat_html = " | ".join(f'<a href="/category/{slug(c)}/">{esc(c)}</a>' for c in f.cats)
        page = f"""<h1>{esc(f.title)}</h1>
<div class="kept">Folio {f.number:,} &middot; kept by the {GUILDS_KEEPING[f.kind]} &middot; last revised {f.last_edit.long()}</div>
{kit.tabs([("Folio", notice + box + toc + body), ("Disputes", disputes), ("Chronicle", chron)])}
<div class="cats">Categories: {cat_html}</div>"""
        site.page(f"/folio/{f.slug}/", f.title, page, scripts=kit.TABS_JS)

    # ---- A-Z, categories, search, random ----------------------------------------
    letters = sorted({f.slug[0] for f in folios})
    letter_bar = '<div class="letters">' + "".join(
        f'<a href="/index/{l}/">{l.upper()}</a>' for l in letters) + "</div>"
    for l in letters:
        items = sorted((f for f in folios if f.slug[0] == l), key=lambda f: f.slug)
        site.page(f"/index/{l}/", f"Folios: {l.upper()}", f"<h1>Folios beginning with {l.upper()}</h1>"
                  f"{letter_bar}<div class='cols'>" + "".join(
                      f'<div><a href="{f.url}">{esc(f.title)}</a></div>' for f in items) + "</div>")
    if "a" not in letters:
        site.redirect("/index/a/", f"/index/{letters[0]}/")
    site.page("/categories/", "Categories", "<h1>Categories</h1><div class='cols'>" + "".join(
        f'<div><a href="/category/{slug(c)}/">{esc(c)}</a> ({len(v)})</div>' for c, v in sorted(cats.items()))
              + "</div>")
    for c, items in cats.items():
        site.page(f"/category/{slug(c)}/", f"Category: {c}", f"<h1>Category: {esc(c)}</h1><ul>" + "".join(
            f'<li><a href="{f.url}">{esc(f.title)}</a></li>' for f in sorted(items, key=lambda f: f.title))
                  + "</ul>")
    idx = [{"t": f.title, "u": f"/folio/{f.slug}/", "s": f.summary[0][:160]} for f in folios]
    site.json("/titles.json", idx)
    site.page("/search/", "Search", """<h1>Search the Commonplace</h1>
<p class="kept">The Commonplace searches folio titles and opening lines only.</p>
<div id="results">Searching&hellip;</div>""", index=False, scripts="""<script>
var q=(new URLSearchParams(location.search).get('q')||'').trim(), box=document.getElementById('results');
document.querySelector('.top input').value=q;
fetch('/titles.json').then(r=>r.json()).then(function(all){
  if(!q){box.innerHTML='<p>Type something in the box above.</p>';return;}
  var words=q.toLowerCase().split(/\\s+/);
  var exact=all.find(f=>f.t.toLowerCase()===q.toLowerCase());
  if(exact){location.replace(exact.u);return;}
  var hits=all.map(function(f){var t=f.t.toLowerCase(),s=f.s.toLowerCase(),sc=0;
    words.forEach(function(w){if(t.indexOf(w)>=0)sc+=3;else if(s.indexOf(w)>=0)sc+=1;});return [sc,f];})
    .filter(x=>x[0]>0).sort((a,b)=>b[0]-a[0]).slice(0,30);
  box.innerHTML=hits.length?'<p>'+hits.length+' folios match.</p><ul>'+hits.map(h=>'<li><a href="'+h[1].u+'">'+h[1].t+'</a><br><small>'+h[1].s+'&hellip;</small></li>').join('')+'</ul>'
    :'<p>No folio matches <b>'+q.replace(/</g,'&lt;')+'</b>. The Commonplace only keeps folios the guilds have written.</p>';
});</script>""")
    site.page("/random/", "A random folio", "<p>Fetching a folio&hellip;</p>", index=False,
              scripts="<script>fetch('/titles.json').then(r=>r.json()).then(a=>location.replace(a[Math.floor(Math.random()*a.length)].u));</script>")
    site.page("/about/", "About the Commonplace", f"""<h1>About the Commonplace</h1>
<p>The Commonplace is kept by nine learned guilds. Each folio is kept by one guild, which
revises it on its own schedule. <b>Folios are not revised as events happen.</b> Check the
Chronicle tab to see when a folio was last revised, and consult the news wires for anything
more recent.</p>
<p>The Commonplace holds {len(folios)} folios. It does not keep folios on living people who
are not public figures, on companies without a listing or a charter, or on matters before the
courts.</p>
<p>Numbers of theorems and their status are kept separately by the
<a href="{url('numerary')}">Guild of Numerists</a>.</p>""")

    # ---- front leaf ---------------------------------------------------------------
    fotd = next(f for f in folios if f.title == "Treaty of the Nine Fords")
    news = [s for s in STORIES if s.date <= ADate(412, 8, 5) and s.section in ("politics", "world",
                                                                              "science")][-5:]
    news_html = "".join(f'<li>{esc(s.date.long())}: {linker(s.headline)}</li>' for s in reversed(news))
    onthisday = [e for e in EVENTS if e.year % 50 == 12 or e.year in (37, 131, 288, 367)][:4]
    site.page("/", "The Commonplace", f"""
<h1>The Commonplace</h1><p>The shared commonplace book of Averra, holding {len(folios)} folios
kept by the learned guilds.</p>
<div class="fp"><div><h3>Folio of the day</h3>
<p><a href="{fotd.url}"><b>{esc(fotd.title)}</b></a>: {esc(fotd.summary[0])}</p></div>
<div><h3>Lately in the wires</h3><ul>{news_html}</ul>
<p class="kept">Folios on current events are revised weekly at most.</p></div>
<div><h3>From the rolls</h3><ul>{"".join(f'<li><a href="{links.folio(e.title)}">{esc(e.title)}</a> ({e.span})</li>' for e in onthisday)}</ul></div>
<div><h3>Browse</h3>{letter_bar}<p><a href="/categories/">All categories</a></p></div></div>""")
    site.fact("folio-count", "How many folios does the Commonplace hold?", str(len(folios)), "/about/")
    site.fact("lighthouse-outdated", "According to the Commonplace, how does the Harthwick Lighthouse "
              "flash?", "twice every nine seconds (outdated; since 1 Sheaf 412 it flashes three "
              "times every twelve seconds)", links.folio("Harthwick Lighthouse"),
              note="freshness trap")
