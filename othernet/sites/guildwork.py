"""guildwork.gld: jobs, apprenticeships, and guild placements."""
from ..engine import kit
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.calendar import ADate, TODAY
from ..world.econ import NATION_CURRENCY, fmt_money, convert
from ..world.geo import CITY, CITIES
from ..world.orgs import COMPANIES

HAND = [
    ("Night assistant for the Pith crossing", "Lanternport Observatory", "Lanternport", "temporary", 24, ADate(412, 8, 25),
     "Help run the public watch on Observatory Hill on 3 Mire. Hand out filters, answer questions. 20:00 to 23:00.", ["Good with crowds", "Not afraid of the dark"]),
    ("Weft engineer, Slate firmware", "Vantle", "Ostmere", "permanent", 68_000, ADate(412, 9, 5),
     "Work on Weave OS for the Slate 7 and its successors. Experience with charger negotiation a plus.", ["Weft 3", "Five years on looms"]),
    ("Lock engineer, Tarrow Canal widening", "Gildmere Works", "Tarrow", "permanent", 52_000, ADate(412, 8, 30),
     "Design and supervise new locks for sea barges. Guild of Lock-wrights certificate required. Start date depends on the outcome of current "
     "proceedings.", ["Lock-wright's certificate"]),
    ("Airship deck crew", "Emberline", "Brineholt", "permanent", 31_000, ADate(412, 9, 1),
     "Crew for the Kestrel and Skylark. Must pass a heights test at Northmole.", ["Head for heights", "Knots"]),
    ("Tea room manager", "The Copper Kettle", "Tarrow", "permanent", 29_000, ADate(412, 8, 28),
     "Run our Canalside tea room. Hester still visits every tea room once a year.", ["Two years in hospitality"]),
    ("Lantern rank researcher", "Lanthorn", "Lanternport", "permanent", 88_000, ADate(412, 9, 12),
     "Improve how Lanthorn ranks small sites. You will read a lot of angry loom-letters.", ["Numerics", "Loomcraft"]),
    ("Apprentice lamplighter", "Guild of Lamplighters", "Ostmere", "apprenticeship", 9_000, ADate(412, 9, 20),
     "Three-year apprenticeship. Evening and dawn rounds in Old Ford. Pole provided.", ["Age 16 or over", "Steady ladder"]),
    ("Mine rescue trainee", "Harrowdeep Mine Rescue", "Harrowdeep", "apprenticeship", 41_000, ADate(412, 9, 9),
     "Train under Greystone Magna's crews. Physical test at the Anvil Hall.", ["Fit", "Calm"]),
    ("Registry clerk (records)", "Concordat Registry", "Ostmere", "permanent", 24_000, ADate(412, 8, 22),
     "Filing and records work on floors 3 to 16 of the Registry Tower.", ["Neat hand", "Patience"]),
]
ROLES = ["Clerk", "Driver", "Cook", "Loom technician", "Porter", "Warehouse hand", "Accountant", "Nurse", "Teacher", "Guard", "Cleaner",
         "Sales assistant", "Deckhand", "Miner", "Surveyor", "Glassblower", "Weaver", "Brewer", "Baker", "Carpenter"]

CSS = """
*{box-sizing:border-box}body{margin:0;font:15px/1.5 'Segoe UI',Arial,sans-serif;background:#f5f3ff;color:#1e1b4b}
header{background:#312e81;color:#fff;padding:14px 26px;display:flex;align-items:center;gap:26px}header a{color:#fff;text-decoration:none}.logo{font-weight:800;font-size:22px}
main{max-width:1000px;margin:0 auto;padding:20px}a{color:#4338ca}
.job{background:#fff;border-radius:8px;padding:14px;margin:10px 0;border-left:5px solid #6366f1}.muted{color:#6b7280;font-size:13px}
.filters{background:#fff;padding:12px;border-radius:8px;display:flex;gap:10px;flex-wrap:wrap}.filters select,.filters input{padding:6px}
.tag{display:inline-block;background:#e0e7ff;padding:1px 8px;border-radius:10px;font-size:12px;margin-right:4px}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - Guildwork</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">Guildwork</a><a href="/jobs/">All jobs</a><a href="/apprenticeships/">Apprenticeships</a><a href="/employers/">Employers</a></header>
<main>{body}</main>{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("guildwork")
    jobs = []
    for t, emp, city, kind, pay_cr, closes, desc, reqs in HAND:
        cur = NATION_CURRENCY[CITY[city].nation]
        jobs.append({"t": t, "emp": emp, "city": city, "kind": kind, "pay": (round(convert(pay_cr, "VCR", cur), -2 if pay_cr > 1000 else 0)) if cur != "VCR" else pay_cr,
                     "cur": cur, "closes": closes, "desc": desc, "reqs": reqs, "posted": closes - rng.randint(10, 30)})
    emps = [c for c in COMPANIES]
    for i in range(140):
        c = rng.choice(emps)
        city = c.city if rng.random() < .7 else rng.choice([x.name for x in CITIES if x.nation == c.nation])
        role = rng.choice(ROLES)
        kind = rng.choice(["permanent", "permanent", "temporary", "part-time"])
        pay_cr = rng.randint(14, 70) * 1000 * (0.5 if kind == "part-time" else 1)
        cur = NATION_CURRENCY[c.nation]
        posted = TODAY - rng.randint(0, 40)
        jobs.append({"t": f"{role}", "emp": c.name, "city": city, "kind": kind, "pay": round(convert(pay_cr, "VCR", cur), -2), "cur": cur,
                     "closes": posted + rng.randint(14, 45), "desc": f"{c.name} is looking for a {role.lower()} in {city}. {c.description}",
                     "reqs": rng.sample(["Reliable", "Own boots", "Weft basics", "Kethric spoken", "Clean driving record (carts)", "Early starts",
                                         "Numeracy", "Tally arithmetic"], 2), "posted": posted})
    jobs.sort(key=lambda j: j["posted"], reverse=True)
    for i, j in enumerate(jobs):
        j["id"] = f"GW{41200 + i * 3}"

    def pay(j):
        return fmt_money(j["pay"], j["cur"], cents=False) + (" a year" if j["kind"] not in ("temporary",) else " for the engagement")

    for j in jobs:
        closed = j["closes"] < TODAY
        site.page(f"/job/{j['id']}/", f"{j['t']} at {j['emp']}", f"""<div class="job"><h1>{esc(j['t'])}</h1><p><b>{esc(j['emp'])}</b> &middot; {esc(j['city'])} &middot;
<span class="tag">{j['kind']}</span></p><p>Pay: <b>{esc(pay(j))}</b></p><p>{esc(j['desc'])}</p><h3>You will need</h3><ul>{"".join(f"<li>{esc(r)}</li>" for r in j['reqs'])}</ul>
<p class="muted">Posted {j['posted'].long()}. {'<b>Closed</b> on ' + j['closes'].long() if closed else 'Closes ' + j['closes'].long()}. Reference {j['id']}.</p>
{"" if closed else '<form onsubmit="event.preventDefault();this.innerHTML=&quot;<p>Application sent. The employer will contact you by loom-letter.</p>&quot;"><p><label>Your name <input required></label></p><p><label>Why you? <textarea rows=3 cols=40></textarea></label></p><button>Apply</button></form>'}</div>""")
    data = [{"id": j["id"], "t": j["t"], "e": j["emp"], "c": j["city"], "k": j["kind"], "cr": round(convert(j["pay"], j["cur"], "VCR")),
             "p": pay(j), "cl": j["closes"].ordinal() < TODAY.ordinal()} for j in jobs]
    site.json("/data/jobs.json", data)
    cities = sorted({j["city"] for j in jobs})
    site.page("/jobs/", "All jobs", f"""<form class="filters"><input name="q" id="q" placeholder="Job title or employer">
<select name="city" id="city"><option value="">Anywhere</option>{"".join(f"<option>{c}</option>" for c in cities)}</select>
<select name="kind" id="kind"><option value="">Any type</option><option>permanent</option><option>temporary</option><option>part-time</option><option>apprenticeship</option></select>
<label>Min pay (cr/yr) <input name="min" id="min" type="number"></label><label><input type="checkbox" name="open" id="open"> Open only</label><button>Filter</button></form>
<p id="n"></p><div id="r"></div>""", index=False, scripts="""<script>var P=new URLSearchParams(location.search);['q','city','kind','min'].forEach(k=>{if(P.get(k))document.getElementById(k).value=P.get(k);});
document.getElementById('open').checked=P.get('open')==='on';fetch('/data/jobs.json').then(r=>r.json()).then(function(J){var q=(P.get('q')||'').toLowerCase(),c=P.get('city')||'',k=P.get('kind')||'',m=parseFloat(P.get('min')),o=P.get('open')==='on';
var h=J.filter(j=>(!q||(j.t+' '+j.e).toLowerCase().indexOf(q)>=0)&&(!c||j.c===c)&&(!k||j.k===k)&&(isNaN(m)||j.cr>=m)&&(!o||!j.cl));
document.getElementById('n').textContent=h.length+' jobs';document.getElementById('r').innerHTML=h.map(j=>'<div class="job"><a href="/job/'+j.id+'/"><b>'+j.t+'</b></a> at '+j.e+'<br><span class="muted">'+j.c+' &middot; '+j.k+' &middot; '+j.p+(j.cl?' &middot; CLOSED':'')+'</span></div>').join('');});</script>""")
    appr = [j for j in jobs if j["kind"] == "apprenticeship"]
    site.page("/apprenticeships/", "Apprenticeships", "<h1>Apprenticeships</h1>" + "".join(
        f'<div class="job"><a href="/job/{j["id"]}/"><b>{esc(j["t"])}</b></a> at {esc(j["emp"])}<br><span class="muted">{esc(j["city"])} &middot; {esc(pay(j))}</span></div>' for j in appr))
    by_emp = {}
    for j in jobs:
        by_emp.setdefault(j["emp"], []).append(j)
    site.page("/employers/", "Employers", "<h1>Employers</h1><ul>" + "".join(
        f'<li>{esc(e)} ({len(js)} jobs): ' + ", ".join(f'<a href="/job/{j["id"]}/">{esc(j["t"])}</a>' for j in js[:4]) + "</li>" for e, js in sorted(by_emp.items())) + "</ul>")
    site.page("/", "Guildwork", f"<h1>Find work</h1><form action='/jobs/'><input name='q' size='40' placeholder='What kind of work?'> <button>Search</button></form>"
              f"<p>{len(jobs)} jobs listed. Pay is shown in the currency of the place of work.</p><h2>Newest</h2>" + "".join(
                  f'<div class="job"><a href="/job/{j["id"]}/"><b>{esc(j["t"])}</b></a> at {esc(j["emp"])}<br><span class="muted">{esc(j["city"])} &middot; {esc(pay(j))}</span></div>' for j in jobs[:12]))
    obs = next(j for j in jobs if j["emp"] == "Lanternport Observatory")
    site.fact("guildwork-observatory-pay", "What does the Lanternport Observatory pay its night assistant for the Pith crossing?",
              pay(obs), f"/job/{obs['id']}/")
