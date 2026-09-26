"""rulings.khr: rulings of the Moot of Holds. Dates are in Hold Reckoning (HR = CR + 880)."""
from ..engine import kit
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.calendar import ADate, TODAY
from ..world.names import make_name, KHR_CLANS

GLOSSARY = [("delve", "a mine working or gallery"), ("hold-price", "a fine paid to the Moot"),
            ("writ of passage", "permission for outsiders to cross into the Holds"), ("warden", "a judge of the Moot"),
            ("tier", "a level of a hold-city, counted from the top"), ("oath-stone", "a stone at Stonemeet on which oaths are sworn"),
            ("refuge", "a sealed chamber in a delve, with air and water"), ("clan-right", "a right held by a whole clan, not a person")]

DEEPSHAFT = {
    "no": "MR 1292/31", "date": ADate(412, 8, 9), "title": "The Moot of Holds against Coldforge Mining (Deepshaft 9)",
    "wardens": ["Greystone Asta (presiding)", "Thornhelm Ulla", "Ironsvale Sten"],
    "paras": [
        "On 22.6.1292 HR, at about the sixth bell, the roof of the eastern gallery of Deepshaft 9 fell at the 600-ell level.",
        "Sixteen workers were cut off: fourteen on the Coldforge shift list and two contractors of Slatebrook Haulage who were not "
        "on the list. The Moot finds that the company's first report of fourteen was wrong because it relied on the shift list alone.",
        "The sixteen reached the refuge chamber of the eastern gallery, which held water for twenty for ten days as the mining code requires.",
        "Rescuers of the Harrowdeep Mine Rescue, led by Greystone Magna, broke into the refuge at 04:40 on 28.6.1292 HR. The last worker "
        "reached the surface at 09:15.",
        "The Moot finds that Coldforge Mining received written warnings about corroded roof bolts in the eastern gallery on 3.2.1292, "
        "19.4.1292 and 30.5.1292 HR, and did not act on any of them.",
        "A Concordat rescue crew waited at Frostgate road for a writ of passage for two days. The Moot regrets the delay and commends "
        "the Assembly of the Concordat for its bill on cross-border aid.",
    ],
    "order": ["Coldforge Mining shall pay a hold-price of 4,200,000 marks to the Moot, within 90 days.",
              "Coldforge Mining shall replace every roof bolt in Deepshaft workings older than twenty years before 1.1.1293 HR.",
              "Coldforge Mining shall keep a list of every person below ground, including contractors, at the pithead."],
}
RESCUED = ["Cinder Asta", "Cinder Bodil", "Flint Egil", "Slatebrook Holm", "Slatebrook Idun", "Coldforge Njal", "Underhill Oda",
           "Veinfinder Ragna", "Ashkettle Sten", "Deepwell Thora", "Orebright Ulla", "Hammerfall Vard", "Copperlode Yrsa",
           "Thornhelm Stig", "Blackmere Liv", "Greystone Kolbein"]
KINDS = [("water", "the water-right of the {a} spring"), ("boundary", "the boundary between the {a} and {b} delves"),
         ("trade", "a cargo of ice-salt seized at Frostgate"), ("inheritance", "the clan-right to a forge on the {a} tier"),
         ("safety", "a gallery collapse at the {a} delve"), ("oath", "an oath broken at Stonemeet"),
         ("grazing", "summer grazing above {a}"), ("debt", "an unpaid hold-price")]

CSS = """
body{margin:0;background:#2b2b2b;color:#e8e2d6;font:16px/1.6 'Palatino Linotype',Georgia,serif}
header{background:#1a1a1a;border-bottom:4px solid #d4652f;padding:18px 30px}
header a{color:#e8e2d6;text-decoration:none}header h1{margin:0;font:normal 28px 'Courier New',monospace;letter-spacing:6px;text-transform:uppercase}
header p{margin:4px 0 0;color:#a8a29e}header nav a{margin-right:18px;color:#fdba74}
main{max-width:900px;margin:0 auto;padding:24px 30px}a{color:#fdba74}
.ruling{background:#343434;border:1px solid #4a4a4a;padding:20px 26px}.ruling h2{font-family:'Courier New',monospace}
ol.p li{margin:8px 0}table{border-collapse:collapse;width:100%}td,th{padding:6px;border-bottom:1px solid #4a4a4a;text-align:left}
.sig{color:#a8a29e;font-style:italic}input{padding:6px;font-size:15px;width:320px}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Moot Rulings</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a href="/"><h1>&#9650; Moot Rulings &#9650;</h1></a><p>Rulings of the Moot of Holds, Harrowdeep. Dates in Hold Reckoning.</p>
<nav><a href="/rulings/">All rulings</a><a href="/glossary/">Glossary</a><a href="/reckoning/">On the Reckoning</a></nav></header>
<main>{body}</main>{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("moot")
    rulings = []
    for i in range(44):
        kind, tmpl = rng.choice(KINDS)
        a, b = rng.sample(KHR_CLANS, 2)
        d = ADate(rng.choice([410, 411, 412]), rng.randint(1, 10), rng.randint(1, 36))
        if d > TODAY:
            d = TODAY - rng.randint(1, 60)
        party = f"Clan {a} against Clan {b}" if kind in ("water", "boundary", "inheritance", "grazing") else \
            f"The Moot of Holds against {make_name(rng, 'KHR').full}"
        outcome = rng.choice([f"for Clan {a}", f"for Clan {b}", "dismissed", "hold-price of " + f"{rng.randint(2, 900) * 1000:,} marks",
                              "settled by oath at Stonemeet"])
        paras = [f"The Moot heard a dispute about {tmpl.format(a=a, b=b)}.",
                 f"Clan {a} relied on a writ of {d.hr_year - rng.randint(40, 400)} HR.",
                 f"The Moot finds the ruling {outcome}."]
        rulings.append({"no": None, "date": d, "title": party, "kind": kind, "paras": paras,
                        "order": [f"Ruling {outcome}."], "wardens": [f"{make_name(rng, 'KHR').full}" for _ in range(3)]})
    rulings.append({**DEEPSHAFT, "kind": "safety"})
    rulings.sort(key=lambda r: r["date"])
    counters = {}
    for r in rulings:
        y = r["date"].hr_year
        counters[y] = counters.get(y, 0) + 1
        if r.get("no") is None:
            r["no"] = f"MR {y}/{counters[y]:02d}"
        r["path"] = f"/ruling/{r['no'].split()[1].replace('/', '-')}/"
    # make sure Deepshaft keeps its famous number without colliding
    seen = set()
    for r in rulings:
        if r["no"] in seen:
            r["no"] = r["no"] + "a"
            r["path"] = f"/ruling/{r['no'].split()[1].replace('/', '-')}/"
        seen.add(r["no"])
    for r in rulings:
        annex = ""
        if r is not None and r["title"].startswith("The Moot of Holds against Coldforge"):
            annex = "<h3>Annex: those brought up from Deepshaft 9</h3><ol>" + "".join(f"<li>{esc(n)}</li>" for n in RESCUED) + "</ol>"
        site.page(r["path"], f"{r['no']}: {r['title']}", f"""<div class="ruling"><p>{esc(r['no'])} &middot; given at Harrowdeep on
<b>{r['date'].kethren()}</b></p><h2>{esc(r['title'])}</h2><p class="sig">Wardens sitting: {esc(', '.join(r['wardens']))}</p>
<h3>Findings</h3><ol class="p">{"".join(f"<li>{esc(p)}</li>" for p in r['paras'])}</ol>
<h3>The Moot orders</h3><ol>{"".join(f"<li>{esc(o)}</li>" for o in r['order'])}</ol>{annex}</div>""")
    rows = [[f'<a href="{r["path"]}">{esc(r["no"])}</a>', r["date"].kethren(), esc(r["title"]), r["kind"]] for r in reversed(rulings)]
    site.page("/rulings/", "All rulings", "<h1>All rulings</h1><p><input id='f' placeholder='Filter: clan, kind, or word'></p>" +
              kit.table(["Number", "Given", "Parties", "Kind"], rows, raw=True, id_="rt"), scripts="""<script>
document.getElementById('f').oninput=function(){var q=this.value.toLowerCase();document.querySelectorAll('#rt tbody tr').forEach(function(t){t.style.display=t.innerText.toLowerCase().indexOf(q)>=0?'':'none';});};</script>""")
    site.page("/glossary/", "Glossary", "<h1>Glossary of the Moot</h1>" + kit.table(["Word", "Meaning"], GLOSSARY))
    site.page("/reckoning/", "On the Reckoning", f"""<h1>On the Hold Reckoning</h1><p>The Holds count years from the cutting of the
first hall at Harrowdeep. To turn a Hold year into a Concord year, take away 880. This year is {TODAY.hr_year} HR, which the
Concordat calls {TODAY.year} CR.</p><p>Dates are written day, month, year: {TODAY.kethren()} is {TODAY.long()} in the Concordat.</p>""")
    site.page("/", "Moot Rulings", f"""<h1>Recent rulings</h1><ul>{"".join(f'<li>{r["date"].kethren()}: <a href="{r["path"]}">{esc(r["title"])}</a></li>' for r in list(reversed(rulings))[:10])}</ul>
<p>The Moot sits in the Deep Halls on the first and third Anvilday of each month.</p>""")
    ds = next(r for r in rulings if r["title"].startswith("The Moot of Holds against Coldforge"))
    site.fact("moot-deepshaft-warnings", "On which dates did Coldforge Mining receive written warnings about roof bolts in "
              "Deepshaft 9 (in HR)?", "3.2.1292, 19.4.1292 and 30.5.1292 HR", ds["path"])
    site.fact("moot-deepshaft-contractors", "Which company employed the two contractors trapped in Deepshaft 9?",
              "Slatebrook Haulage", ds["path"])
