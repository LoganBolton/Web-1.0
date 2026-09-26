"""tastemark.ves: reviews of places to eat, drink, and sleep."""
from ..engine import kit, svg, links
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.addresses import address
from ..world.calendar import ADate, TODAY, WEEKDAYS
from ..world.geo import CITIES, CITY
from ..world.people import generate_population

KINDS = {"restaurant": ["Harbour", "Moor", "Kethren", "Pellish", "Eel house", "Pie shop", "Noodle bar", "Grill"],
         "inn": ["Coaching inn", "Harbour inn", "Moot house"], "tea room": ["Tea room"],
         "tavern": ["Cider house", "Alehouse", "Wine bar"], "bakery": ["Bakery"], "market stall": ["Street food"]}
NAME_A = ["The Drowned", "The Salt", "The Brass", "The Crooked", "The Lantern", "The Gull's", "The Anvil", "The Green",
          "The Tallow", "The Hollow", "The Ninth", "The Kiln", "Old", "Little", "The Lamplighter's", "The Pearl"]
NAME_B = ["Kettle", "Keel", "Ferret", "Oar", "Moon", "Ledger", "Barrow", "Heron", "Lock", "Rope", "Table", "Spoon",
          "Fork", "Pantry", "Hearth", "Cellar", "Loaf", "Tide"]
GOOD = ["Best {x} I have had in {c}.", "Friendly staff and a fire in the grate.", "Worth the wait for a table.",
        "The {x} was perfect. Go early.", "Quiet on a Kettleday, heaving on a Hearthday.", "We come back every Hollowdays."]
MID = ["Fine but overpriced for {c}.", "The {x} was cold by the time it arrived.", "Nice room, slow service.",
       "Portions are small. Bring a friend with a big appetite."]
BAD = ["Waited an hour and they forgot us.", "The {x} tasted of the ferry.", "Rude staff, sticky tables.",
       "Closed when the sign said open."]
DOT, RING = "\u25cf", "\u25cb"
DISHES = ["eel pie", "fish stew", "apple cake", "smoked cheese", "pepperleaf soup", "oat cakes", "kelp noodles",
          "mutton hotpot", "pearl rice", "cider", "treacle tart", "salt-baked bream"]

CSS = """
*{box-sizing:border-box}body{margin:0;font:15px/1.5 'Helvetica Neue',Arial,sans-serif;color:#2d2d2d;background:#fff}
header{background:#d32323;padding:10px 22px;display:flex;align-items:center;gap:20px}header a{color:#fff;text-decoration:none}
.logo{font:bold 26px 'Arial Rounded MT Bold',Arial,sans-serif}header form{flex:1;display:flex;gap:6px}
header input,header select{padding:8px;border:0;border-radius:4px}
main{max-width:1100px;margin:0 auto;padding:20px}a{color:#0073bb}
.biz{display:grid;grid-template-columns:120px 1fr;gap:14px;border-bottom:1px solid #eee;padding:14px 0}.biz img{width:120px;border-radius:6px}
.st{color:#f15c4f;font-size:18px;letter-spacing:-1px}.muted{color:#777;font-size:13px}
.rev{border-bottom:1px solid #eee;padding:12px 0}.rev .who{font-weight:bold}
.cols{display:grid;grid-template-columns:2fr 1fr;gap:24px}.box{border:1px solid #e6e6e6;border-radius:6px;padding:14px;margin-bottom:14px}
table{border-collapse:collapse}td{padding:3px 12px 3px 0}
footer{text-align:center;color:#888;padding:30px;font-size:12px}
@media(max-width:800px){.cols{grid-template-columns:1fr}}
"""


def shell(site, title, body, **kw):
    city_opts = "".join(f"<option>{c.name}</option>" for c in CITIES if c.nation != "ODD")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - Tastemark</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">tastemark</a><form action="/search/"><input name="q" placeholder="eel pie, cider, inns...">
<select name="city"><option value="">Anywhere</option>{city_opts}</select><button>Search</button></form>
<a href="/towns/">Towns</a><a href="/reviewers/">Reviewers</a></header><main>{body}</main>
<footer>Tastemark, Brineholt. Reviews are the opinions of our members. Businesses cannot pay to remove reviews.</footer>{kw.get('scripts', '')}</body></html>"""


def st(r):
    return "\u2605" * int(round(r)) + "\u2606" * (5 - int(round(r)))


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("tastemark")
    pop = generate_population()
    reviewers = rng.sample(pop, 260)
    places = []
    for c in CITIES:
        if c.nation == "ODD":
            continue
        n = max(3, min(14, c.population // 150_000))
        for i in range(n):
            kind = rng.choice(list(KINDS))
            style = rng.choice(KINDS[kind])
            name = f"{rng.choice(NAME_A)} {rng.choice(NAME_B)}"
            line, pc = address(rng, c.name)
            closed = rng.choice(WEEKDAYS)
            places.append({"id": slug(f"{name} {c.name}") + f"-{i}", "name": name, "city": c.name, "kind": kind,
                           "style": style, "addr": f"{line}, {c.name} {pc}", "price": rng.randint(1, 4),
                           "closed": closed, "hours": f"{rng.choice(['11:00', '12:00', '17:00', '7:00'])}\u2013{rng.choice(['21:00', '22:30', '23:00', '15:00'])}",
                           "q": rng.gauss(3.8, 0.6), "dish": rng.choice(DISHES)})
    places.append({"id": "pearl-and-pith-marrowby", "name": "Pearl & Pith", "city": "Marrowby", "kind": "restaurant",
                   "style": "Pellish", "addr": "4 Strand Terrace, Marrowby MB/118", "price": 4, "closed": "Kettleday",
                   "hours": "18:00\u201323:30", "q": 4.7, "dish": "smoked eel with sea-fennel",
                   "note": "Chef: Delphine Estrande. Booking essential. The smoked eel is on every night except in Bloom."})
    for p in places:
        r = stream("tm", p["id"])
        n = r.randint(3, 28)
        revs = []
        for k in range(n):
            who = r.choice(reviewers)
            stars = max(1, min(5, round(r.gauss(p["q"], 0.9))))
            pool = GOOD if stars >= 4 else MID if stars == 3 else BAD
            txt = r.choice(pool).format(x=p["dish"], c=p["city"])
            d = TODAY - r.randint(1, 700)
            revs.append({"who": who, "stars": stars, "text": txt, "date": d})
        if p["id"] == "pearl-and-pith-marrowby":
            revs.insert(0, {"who": reviewers[0], "stars": 5, "date": ADate(412, 8, 13),
                            "text": "Saw a famous actor here tonight in the corner by the kitchen door. The eel was better than he was."})
        revs.sort(key=lambda x: x["date"], reverse=True)
        p["revs"] = revs
        p["rating"] = round(sum(x["stars"] for x in revs) / len(revs), 1)
    for p in places:
        site.write(f"/img/{p['id']}.svg", svg.landscape(p["id"], "city" if p["city"] in ("Ostmere", "Brineholt") else "hills",
                                                        sign=f"{p['name']}\n{p['kind'].title()}"))
        rv = "".join(f'<div class="rev"><span class="who"><a href="/reviewers/{x["who"].handle}/">{esc(x["who"].handle)}</a></span> '
                     f'<span class="muted">{esc(x["who"].city)}</span><br><span class="st">{st(x["stars"])}</span> '
                     f'<span class="muted">{x["date"].long()}</span><p>{esc(x["text"])}</p></div>' for x in p["revs"][:10])
        more = ""
        if len(p["revs"]) > 10:
            more = f'<p><a href="/biz/{p["id"]}/reviews-2/">Older reviews &raquo;</a></p>'
            rv2 = "".join(f'<div class="rev"><span class="who">{esc(x["who"].handle)}</span> <span class="st">{st(x["stars"])}</span> '
                          f'<span class="muted">{x["date"].long()}</span><p>{esc(x["text"])}</p></div>' for x in p["revs"][10:])
            site.page(f"/biz/{p['id']}/reviews-2/", f"{p['name']} reviews (page 2)", f"<h1>{esc(p['name'])}: older reviews</h1>{rv2}"
                      f"<p><a href='/biz/{p['id']}/'>&laquo; Back</a></p>")
        hours = "".join(f"<tr><td>{wd}</td><td>{'Closed' if wd == p['closed'] else p['hours']}</td></tr>" for wd in WEEKDAYS)
        site.page(f"/biz/{p['id']}/", f"{p['name']}, {p['city']}", f"""<div class="cols"><div>
<h1>{esc(p['name'])}</h1><div><span class="st">{st(p['rating'])}</span> {p['rating']} &middot; {len(p['revs'])} reviews &middot;
{DOT * p['price']}{RING * (4 - p['price'])} &middot; {esc(p['style'])} {esc(p['kind'])}</div>
<img src="/img/{p['id']}.svg" alt="Front of {esc(p['name'])}" style="width:100%;max-width:560px;margin:10px 0">
{f"<p><i>{esc(p['note'])}</i></p>" if p.get('note') else ''}<h2>Reviews</h2>{rv}{more}</div>
<div><div class="box"><b>{esc(p['addr'])}</b><table>{hours}</table>
<p><a href="{links.place(p['city'])}">Map of {esc(p['city'])}</a></p></div>
<div class="box"><b>Known for:</b> {esc(p['dish'])}</div></div></div>""")
    # --- town pages --------------------------------------------------------------
    towns = sorted({p["city"] for p in places})
    for t in towns:
        items = sorted([p for p in places if p["city"] == t], key=lambda p: -p["rating"])
        site.page(f"/town/{slug(t)}/", f"Best of {t}", f"<h1>Best places in {esc(t)}</h1>" + "".join(
            f'<div class="biz"><img src="/img/{p["id"]}.svg" alt=""><div><a href="/biz/{p["id"]}/"><b>{esc(p["name"])}</b></a><br>'
            f'<span class="st">{st(p["rating"])}</span> {len(p["revs"])} reviews<br><span class="muted">{esc(p["style"])} {p["kind"]} &middot; '
            f'{DOT * p["price"]}</span></div></div>' for p in items))
    site.page("/towns/", "Towns", "<h1>Towns</h1><ul>" + "".join(f'<li><a href="/town/{slug(t)}/">{esc(t)}</a></li>' for t in towns) + "</ul>")
    # --- reviewers --------------------------------------------------------------------
    by_who = {}
    for p in places:
        for x in p["revs"]:
            by_who.setdefault(x["who"].handle, []).append((p, x))
    for h, items in by_who.items():
        who = items[0][1]["who"]
        site.page(f"/reviewers/{h}/", h, f"<h1>{esc(h)}</h1><p class='muted'>{esc(who.city)} &middot; {len(items)} reviews</p>" + "".join(
            f'<div class="rev"><a href="/biz/{p["id"]}/">{esc(p["name"])}</a>, {esc(p["city"])} <span class="st">{st(x["stars"])}</span>'
            f'<p>{esc(x["text"])}</p><span class="muted">{x["date"].long()}</span></div>' for p, x in sorted(items, key=lambda t: t[1]["date"], reverse=True)))
    top = sorted(by_who.items(), key=lambda kv: -len(kv[1]))[:40]
    site.page("/reviewers/", "Top reviewers", "<h1>Top reviewers</h1><ol>" + "".join(
        f'<li><a href="/reviewers/{h}/">{esc(h)}</a> ({len(v)} reviews)</li>' for h, v in top) + "</ol>")
    # --- search -------------------------------------------------------------------------------
    site.json("/data/places.json", [{"id": p["id"], "n": p["name"], "c": p["city"], "k": p["kind"], "s": p["style"],
                                     "d": p["dish"], "r": p["rating"], "v": len(p["revs"]), "p": p["price"]} for p in places])
    site.page("/search/", "Search", "<h1 id='h'>Search</h1><div id='r'></div>", index=False, scripts="""<script>
var P=new URLSearchParams(location.search),q=(P.get('q')||'').toLowerCase(),c=P.get('city')||'';
fetch('/data/places.json').then(r=>r.json()).then(function(A){var res=A.filter(function(p){var hay=(p.n+' '+p.k+' '+p.s+' '+p.d).toLowerCase();
return (!c||p.c===c)&&(!q||q.split(/\\s+/).every(w=>hay.indexOf(w)>=0));}).sort((a,b)=>b.r-a.r||b.v-a.v);
document.getElementById('h').textContent=res.length+' places'+(q?' for "'+q+'"':'')+(c?' in '+c:'');
document.getElementById('r').innerHTML=res.map(p=>'<div class="biz"><img src="/img/'+p.id+'.svg" alt=""><div><a href="/biz/'+p.id+'/"><b>'+p.n+'</b></a> <span class="muted">'+p.c+'</span><br><span class="st">'+'\\u2605'.repeat(Math.round(p.r))+'</span> '+p.r+' ('+p.v+')<br><span class="muted">'+p.s+' '+p.k+' &middot; known for '+p.d+'</span></div></div>').join('');});</script>""")
    best = sorted(places, key=lambda p: (-p["rating"], -len(p["revs"])))[:8]
    site.page("/", "Tastemark", "<h1>Where to eat tonight?</h1><h2>Top rated across the Weave</h2>" + "".join(
        f'<div class="biz"><img src="/img/{p["id"]}.svg" alt=""><div><a href="/biz/{p["id"]}/"><b>{esc(p["name"])}</b></a>, {esc(p["city"])}<br>'
        f'<span class="st">{st(p["rating"])}</span> {len(p["revs"])} reviews</div></div>' for p in best))
    site.fact("tastemark-pearlpith-closed", "On which day of the week is Pearl & Pith in Marrowby closed?", "Kettleday",
              "/biz/pearl-and-pith-marrowby/")
