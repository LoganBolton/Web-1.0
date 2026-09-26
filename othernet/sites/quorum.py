"""quorum.fol: questions and answers. The most-voted answer is not always right."""
from ..engine import kit
from ..engine.domains import url
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.calendar import ADate, TODAY
from ..world.econ import RATES
from ..world.geo import CITIES, distance_leagues
from ..world.people import generate_population

# (tags, title, body, asked, [(text, votes, accepted, answered)])
HAND = [
    (["calendar", "kethren"], "How do I convert a Kethren date to a Concord date?",
     "A Moot ruling is dated 9.8.1292 HR. What is that in CR?", ADate(412, 8, 12),
     [("Subtract 880 from the year. 9.8.1292 HR is 9 Gale 412 CR. Day and month are the same.", 44, True, ADate(412, 8, 12)),
      ("Subtract 800. The Holds started counting 800 years before the Concord.", 51, False, ADate(412, 8, 12)),
      ("Just ask a Kethren.", 3, False, ADate(412, 8, 13))]),
    (["currency", "saltmarch"], "How many bits in a tally?",
     "Buying a tram ticket in Brineholt. Is a bit a tenth of a tally?", ADate(411, 6, 6),
     [("Twelve bits make a tally. It's from the old salt trade. 1t 2b is fourteen bits.", 88, True, ADate(411, 6, 6)),
      ("Ten, like everywhere else.", 12, False, ADate(411, 6, 7))]),
    (["lighthouses", "harthwick"], "What is the light pattern of Harthwick Lighthouse?",
     "Planning a night sail. What does Harthwick show?", ADate(409, 2, 2),
     [("Two white flashes every nine seconds. Source: the Commonplace.", 67, True, ADate(409, 2, 3)),
      ("Update, Sheaf 412: it changed on 1 Sheaf 412 to THREE flashes every TWELVE seconds, because the new Lowmarsh breakwater light uses two in nine. "
       "The Courier reported it. The accepted answer is out of date.", 9, False, ADate(412, 7, 4))]),
    (["loom", "weft"], "What does 'W-2F' mean on my Slate?", "My Slate 6 shows W-2F and freezes.", ADate(412, 5, 1),
     [("Shuttle stall. Update Weave OS; if it keeps happening, take it to a Vantle store.", 21, True, ADate(412, 5, 1)),
      ("It means your reeds are full, delete some ribbons.", 25, False, ADate(412, 5, 2))]),
    (["travel", "emberline"], "Why was my Emberline return fare in a different currency?",
     "Booked Ostmere to Lanternport and back. One leg in crowns and one in lumes?", ADate(412, 6, 20),
     [("Emberline charges in the currency of the departure port. Lanternport departures are priced in lumes.", 37, True, ADate(412, 6, 20))]),
    (["math", "tidal-primes"], "What is a tidal prime, simply?", "Everyone's talking about the Cresselle proof.", ADate(412, 4, 30),
     [("A prime p where p + 12 is also prime and p leaves remainder 1 when divided by 3. The first few are 7, 19, 31, 61, 67... wait, 67+12=79 prime, yes.",
       30, True, ADate(412, 4, 30)),
      ("It's a prime that appears at high tide. That's why Saltmarch cares.", 14, False, ADate(412, 5, 1))]),
    (["math", "tidal-primes"], "Has the Cresselle Conjecture been proved?", "I read that Aubrel proved it.", ADate(412, 1, 10),
     [("Yes! Aubrel proved it in Dusk 411.", 40, False, ADate(412, 1, 10)),
      ("Not accepted yet. A gap was found in Bloom 412, a revised proof was posted on 5 Gale 412, and the Guild of Numerists lists it as 'Under review'. "
       "Check the Numerary for the current status.", 19, True, ADate(412, 8, 6))]),
    (["registry", "law"], "How can I see who owns a Veylish company?", "", ADate(410, 3, 3),
     [("Search the Concordat Registry at registry.vey. Any holder of 10% or more has to be notified.", 26, True, ADate(410, 3, 3))]),
    (["media"], "Who owns The Crier?", "The Crier never says who publishes it.", ADate(411, 9, 9),
     [("It's published by Crier Publishing, which the Registry shows is 100% owned by Morrow Media Group. Same people as the Morrow portal.", 31, True, ADate(411, 9, 10)),
      ("It's independent, run by its journalists.", 8, False, ADate(411, 9, 9))]),
    (["weather"], "Why are storms named after birds?", "", ADate(412, 8, 10),
     [("The Weather Office and the Admiralty share a list of seabirds since 398. After Petrel comes Quail.", 12, True, ADate(412, 8, 10))]),
    (["food", "units"], "How big is a 'measure' in recipes?", "Hearth & Hob recipes use measures.", ADate(411, 2, 2),
     [("About a quarter of a litre. Four measures to the pitcher.", 18, True, ADate(411, 2, 2))]),
    (["sky", "pith"], "Can I see the Pith crossing from Brineholt?", "", ADate(412, 8, 2),
     [("No. The Observatory's table says not visible from Brineholt. Harthwick gets a full crossing from 21:20.", 22, True, ADate(412, 8, 2)),
      ("Yes, look south at 21:14.", 6, False, ADate(412, 8, 3))]),
    (["banking", "scams"], "Is @drovers_help_desk real?", "They asked for my pass code on Chatter.", ADate(412, 8, 12),
     [("NO. Drovers' only account is @droversbank. They posted a warning on 13 Gale.", 55, True, ADate(412, 8, 13))]),
    (["search", "lanthorn"], "Why can't Lanthorn find the Tallow Boards?", "", ADate(412, 5, 5),
     [("The Tallow Boards block Lanthorn on purpose. So do Moot Rulings and a lot of .fol sites. Use Hearthring, or follow links.", 29, True, ADate(412, 5, 5))]),
    (["vaultball"], "How many points is a well?", "", ADate(410, 7, 7),
     [("Five. A rim is three.", 40, True, ADate(410, 7, 7)), ("Three.", 2, False, ADate(410, 7, 8))]),
    (["pets", "travel"], "Can my dog come on the Skylark?", "", ADate(412, 6, 25),
     [("No pets on airships except assistance animals. Ferries take pets under 12 wt free in a carrier.", 16, True, ADate(412, 6, 25))]),
    (["oddavar"], "When is the Frostgate open?", "", ADate(412, 4, 20),
     [("90 days a year. In 412 it opened 1 Blaze and closes after 18 Sheaf.", 11, True, ADate(412, 4, 21))]),
    (["calendar"], "How many days in a Concord year?", "", ADate(405, 5, 5),
     [("365: ten months of 36 days, plus 5 Hollowdays.", 60, True, ADate(405, 5, 5)), ("360.", 7, False, ADate(405, 5, 6))]),
    (["loom", "weft"], "How do I print a line in Weft?", "Just starting with Weft.", ADate(412, 3, 3),
     [("`say \"hello\"` in Weft 3. In Weft 2 it was `emit`. See weft.gld for the docs.", 15, True, ADate(412, 3, 3))]),
    (["registry", "canal"], "Who is Hemming Lockwright?", "Name keeps coming up about the canal panel.", ADate(412, 8, 14),
     [("No idea, and this site isn't for rumours. Closed.", 2, False, ADate(412, 8, 14))]),
]


CSS = """
*{box-sizing:border-box}body{margin:0;font:14px/1.5 -apple-system,Arial,sans-serif;background:#fff;color:#232629}
header{border-top:3px solid #6d28d9;box-shadow:0 1px 2px rgba(0,0,0,.1);padding:10px 24px;display:flex;align-items:center;gap:20px}
header a{text-decoration:none;color:#232629}.logo{font:bold 22px Georgia,serif}.logo span{color:#6d28d9}
header input{padding:7px;width:360px;border:1px solid #bbc0c4;border-radius:4px}
main{max-width:1000px;margin:0 auto;padding:20px}a{color:#0074cc}
.q{display:grid;grid-template-columns:110px 1fr;gap:14px;border-bottom:1px solid #e3e6e8;padding:12px 0}.stats{color:#6a737c;font-size:12px;text-align:right}
.tag{display:inline-block;background:#ede9fe;color:#5b21b6;padding:1px 7px;border-radius:3px;font-size:12px;margin-right:4px}
.ans{display:grid;grid-template-columns:60px 1fr;gap:12px;border-bottom:1px solid #e3e6e8;padding:14px 0}.vote{text-align:center;font-size:20px;color:#6a737c}
.acc{color:#2f6f44;font-size:26px}.meta{color:#6a737c;font-size:12px}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - Quorum</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">quor<span>um</span></a><form action="/search/"><input name="q" placeholder="Search questions"></form>
<a href="/tags/">Tags</a><a href="/top/">Top</a><a href="/ask/">Ask</a></header><main>{body}</main>{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("quorum")
    pop = generate_population()
    handles = [p.handle for p in rng.sample(pop, 200)]
    qs = []
    for tags, title, body, asked, answers in HAND:
        qs.append({"tags": tags, "t": title, "b": body, "d": asked, "a": [{"x": x, "v": v, "acc": acc, "d": d, "who": rng.choice(handles)}
                                                                         for x, v, acc, d in answers]})
    # Generated: distances (correct), exchange rates (stale), and ferry questions.
    for i in range(45):
        a, b = rng.sample([c for c in CITIES if c.nation != "ODD"], 2)
        dist = distance_leagues(a, b)
        d = ADate(rng.randint(406, 412), rng.randint(1, 10), rng.randint(1, 36))
        d = min(d, TODAY - 1)
        qs.append({"tags": ["travel", "distances"], "t": f"How far is {a.name} from {b.name}?", "b": "As the gull flies.", "d": d,
                   "a": [{"x": f"About {dist} leagues in a straight line, by the Chartroom reckoner.", "v": rng.randint(1, 15), "acc": True, "d": d, "who": rng.choice(handles)},
                         {"x": f"About {round(dist * rng.uniform(1.2, 1.6))} leagues by road.", "v": rng.randint(0, 20), "acc": False, "d": d + 1, "who": rng.choice(handles)}]})
    for i in range(12):
        d = ADate(412, rng.randint(1, 7), rng.randint(1, 36))
        cur = rng.choice(["STL", "KMK", "PLM"])
        name = {"STL": "tally", "KMK": "mark", "PLM": "lume"}[cur]
        qs.append({"tags": ["currency"], "t": f"How many crowns is a {name} worth?", "b": "", "d": d,
                   "a": [{"x": f"About {RATES[cur][d]:.3f} cr as of today ({d.long()}). Rates move daily; check Drovers' Bank.", "v": rng.randint(2, 30),
                          "acc": True, "d": d, "who": rng.choice(handles)}]})
    qs.sort(key=lambda q: q["d"], reverse=True)
    for i, q in enumerate(qs):
        q["id"] = 50_000 + i * 13
        q["views"] = rng.randint(20, 20_000)
        q["votes"] = sum(a["v"] for a in q["a"]) // 3
        q["asker"] = rng.choice(handles)
        q["path"] = f"/q/{q['id']}/{slug(q['t'])[:60]}/"
    for q in qs:
        answers = sorted(q["a"], key=lambda a: -a["v"])
        ans = "".join(
            f'<div class="ans"><div class="vote">{a["v"]}{"<div class=acc title=Accepted>✔</div>" if a["acc"] else ""}</div><div><p>{esc(a["x"])}</p>'
            f'<div class="meta">answered {a["d"].long()} by <a href="/users/{a["who"]}/">{esc(a["who"])}</a></div></div></div>' for a in answers)
        site.page(q["path"], q["t"], f"""<h1>{esc(q['t'])}</h1><div class="meta">Asked {q['d'].long()} by <a href="/users/{q['asker']}/">{esc(q['asker'])}</a>
&middot; viewed {q['views']:,} times</div><div class="ans"><div class="vote">{q['votes']}</div><div><p>{esc(q['b']) or '<i>(no details)</i>'}</p>
{"".join(f'<a class="tag" href="/tags/{t}/">{t}</a>' for t in q['tags'])}</div></div><h2>{len(answers)} answers</h2>
<p class="meta">Sorted by votes. The asker's accepted answer is marked ✔.</p>{ans}""")

    def row(q):
        return (f'<div class="q"><div class="stats">{q["votes"]} votes<br>{len(q["a"])} answers<br>{q["views"]:,} views</div><div>'
                f'<a href="{q["path"]}">{esc(q["t"])}</a><br>{"".join(f"<a class=tag href=/tags/{t}/>{t}</a>" for t in q["tags"])}'
                f'<span class="meta">asked {q["d"].long()}</span></div></div>')

    tags = {}
    for q in qs:
        for t in q["tags"]:
            tags.setdefault(t, []).append(q)
    for t, items in tags.items():
        site.page(f"/tags/{t}/", f"Questions tagged {t}", f"<h1>Questions tagged <span class='tag'>{t}</span></h1>" + "".join(row(q) for q in items))
    site.page("/tags/", "Tags", "<h1>Tags</h1><p>" + " ".join(f'<a class="tag" href="/tags/{t}/">{t} &times; {len(v)}</a>' for t, v in sorted(tags.items())) + "</p>")
    users = {}
    for q in qs:
        users.setdefault(q["asker"], {"q": [], "a": []})["q"].append(q)
        for a in q["a"]:
            users.setdefault(a["who"], {"q": [], "a": []})["a"].append((q, a))
    for h, u in users.items():
        rep = sum(a["v"] * 10 + (15 if a["acc"] else 0) for _, a in u["a"]) + sum(q["votes"] * 5 for q in u["q"])
        site.page(f"/users/{h}/", h, f"<h1>{esc(h)}</h1><p>Reputation {rep:,}</p><h3>Questions</h3><ul>" + "".join(
            f'<li><a href="{q["path"]}">{esc(q["t"])}</a></li>' for q in u["q"]) + "</ul><h3>Answers</h3><ul>" + "".join(
            f'<li><a href="{q["path"]}">{esc(q["t"])}</a> ({a["v"]} votes{", accepted" if a["acc"] else ""})</li>' for q, a in u["a"]) + "</ul>")
    site.json("/data/qs.json", [{"t": q["t"], "p": q["path"], "g": q["tags"]} for q in qs])
    site.page("/search/", "Search", "<h1 id='h'>Search</h1><div id='r'></div>", index=False, scripts="""<script>
var q=(new URLSearchParams(location.search).get('q')||'').toLowerCase();fetch('/data/qs.json').then(r=>r.json()).then(function(Q){
var w=q.split(/\\s+/).filter(Boolean),h=Q.filter(x=>w.every(k=>(x.t+' '+x.g.join(' ')).toLowerCase().indexOf(k)>=0));
document.getElementById('h').textContent=h.length+' results';document.getElementById('r').innerHTML=h.map(x=>'<div class="q"><div></div><div><a href="'+x.p+'">'+x.t+'</a></div></div>').join('');});</script>""")
    site.page("/top/", "Top questions", "<h1>Top questions</h1>" + "".join(row(q) for q in sorted(qs, key=lambda q: -q["votes"])[:40]))
    site.page("/ask/", "Ask", "<h1>Ask a question</h1><p>Asking is closed to new members while the moderators clear spam. Try searching first.</p>")
    site.page("/", "Quorum", "<h1>Newest questions</h1>" + "".join(row(q) for q in qs[:40]))
    hq = next(q for q in qs if q["t"].startswith("What is the light pattern of Harthwick"))
    site.fact("quorum-harthwick-accepted-outdated", "On Quorum, is the accepted answer about Harthwick Lighthouse's light still correct?",
              "No: it was changed on 1 Sheaf 412 to three flashes every twelve seconds", hq["path"], note="accepted answer is stale")
