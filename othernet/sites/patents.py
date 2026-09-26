"""patentrolls.gld: the Patent Rolls of the Guild of Inventors."""
from ..engine import kit, svg
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.calendar import ADate, TODAY
from ..world.names import make_name
from ..engine.rng import pick_weighted

KEY = [
    ("288/14", "A lamp lit by a voltaic pile", ["Idra Fenwick"], "Idra Fenwick", ADate(288, 2, 2), ADate(288, 9, 9),
     "A glass bulb holding a thread of carbonised reed, made to glow by the current of a voltaic pile.",
     ["A lamp in which light is produced by current passing through a carbonised reed.", "The lamp of claim 1 in which the bulb is emptied of air."]),
    ("366/03", "An engine for weaving numbers by punched ribbon", ["Temmet Aske"], "Lanternport University", ADate(366, 10, 30),
     ADate(368, 4, 4), "A frame of brass reeds raised and lowered by a punched ribbon of waxed linen, so that sums may be worked "
     "without a clerk.", ["An engine in which reeds hold values of yes or no.", "The engine of claim 1 in which instructions are read from a punched ribbon.",
                          "The engine of claim 2 in which a ribbon may instruct the engine to read another part of itself."]),
    ("256/02", "A clock showing the places of both moons", ["Tallis Quenby"], "Quenby Clockworks", ADate(256, 1, 20), ADate(256, 7, 7),
     "A clock with two moon-hands, one turning forwards for Ossa and one backwards for Pith.", ["A clock with a hand turning against the others."]),
    ("395/77", "A kettle that switches itself off at the boil", ["Warrick Dunley"], "Kettlebright Appliances", ADate(395, 3, 1),
     ADate(396, 1, 12), "A strip of two metals that bends when steam reaches it and breaks the voltaic circuit.",
     ["A kettle with a steam-bent switch."]),
    ("399/31", "A rigid envelope for an airship", ["Jessamy Keelwright", "Halyard Emberson"], "Keelwright Shipyards",
     ADate(399, 5, 5), ADate(400, 2, 1), "A frame of steamed ash ribs covered in doped linen, holding gas cells.", ["An airship with a rigid frame."]),
    ("405/118", "A slate with a writable back face", ["Corwen Talley", "Sabine Marwick"], "Vantle", ADate(405, 9, 9), ADate(410, 3, 14),
     "A handheld loom with a second glass face on its back that accepts writing by fingertip.",
     ["A handheld loom having two faces.", "The loom of claim 1 in which the back face accepts writing while the front face displays."]),
    ("409/88", "A method of turning Weft into ribbon", ["Mireille Solande"], "Loomworks", ADate(409, 1, 1), ADate(410, 8, 8),
     "A program that reads Weft written by a person and punches the ribbon a loom needs.", ["A translating program for looms."]),
    ("411/40", "A filter for viewing Ossa", ["Sabel Oss"], "Ossa Optics", ADate(411, 2, 2), ADate(412, 6, 6),
     "A film of silvered glass that passes one part in ten thousand of Ossa's light.", ["A filter for viewing a bright moon."]),
    ("412/09", "A charger that tells the loom what it is", ["Voss Anker"], "Vantle", ADate(412, 8, 16), None,
     "A charger that reports its model to the loom it charges, so the loom may refuse an unsafe charger.",
     ["A charger that identifies itself.", "The charger of claim 1 in which the loom limits current for chargers it does not trust."]),
]
WORDS = ["loom", "ribbon", "lamp", "kettle", "clock", "lock gate", "barge winch", "salt pan", "fog bell", "telescope",
         "tram brake", "mine prop", "roof bolt", "oilskin", "wax disc", "spinning frame", "pie crimper", "reed", "shuttle",
         "voltaic pile", "funicular cable", "tide gauge", "kiln door", "chimney cowl"]
VERBS = ["An improved", "A safer", "A folding", "A quieter", "A self-oiling", "A cheaper", "A method of making a",
         "A two-moon", "A portable", "A steam-driven"]


CSS = """
body{margin:0;font:15px/1.55 'Times New Roman',Times,serif;background:#f4f1ea;color:#222}
header{background:#3f3a2e;color:#f4f1ea;padding:16px 28px}header a{color:#f4f1ea;text-decoration:none}
header h1{margin:0;font-size:26px;font-variant:small-caps}header nav a{margin-right:16px;font-size:14px}
main{max-width:980px;margin:0 auto;padding:24px}a{color:#7a4b12}
.roll{background:#fffdf6;border:1px solid #d7cfbd;padding:22px 30px}.roll h2{margin-top:0}
.drawing{border:1px solid #d7cfbd;max-width:420px;background:#fff}table{border-collapse:collapse;width:100%}
td,th{padding:5px;border-bottom:1px solid #e1dac8;text-align:left;vertical-align:top}input{padding:6px;font-size:15px}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Patent Rolls</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a href="/"><h1>The Patent Rolls of the Guild of Inventors</h1></a><nav><a href="/rolls/">Browse the rolls</a>
<a href="/search/">Search</a><a href="/inventors/">Inventors</a><a href="/how/">How to apply</a></nav></header>
<main>{body}</main>{kw.get('scripts', '')}</body></html>"""


def drawing(seed, title):
    rng = stream("drawing", seed)
    p = ['<rect width="420" height="300" fill="#fff"/>']
    for i in range(rng.randint(4, 9)):
        x, y, w, h = rng.randint(20, 300), rng.randint(20, 200), rng.randint(30, 120), rng.randint(20, 90)
        if rng.random() < .5:
            p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#222" stroke-width="1.5"/>')
        else:
            p.append(f'<ellipse cx="{x}" cy="{y}" rx="{w / 2}" ry="{h / 2}" fill="none" stroke="#222" stroke-width="1.5"/>')
        p.append(f'<line x1="{x}" y1="{y}" x2="{x + 30}" y2="{y - 20}" stroke="#222"/>')
        p.append(svg.text(x + 32, y - 22, str(10 + i * 2), 12, "#222", family="Times New Roman, serif"))
    p.append(svg.text(210, 290, "Fig. 1", 14, "#222", "middle", "normal", "Times New Roman, serif", 'font-style="italic"'))
    return svg.wrap(420, 300, "".join(p))


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("patents")
    pats = []
    for no, title, inv, assignee, filed, granted, abstract, claims in KEY:
        pats.append({"no": no, "t": title, "inv": inv, "as": assignee, "f": filed, "g": granted, "ab": abstract, "cl": claims})
    used = {p["no"] for p in pats}
    assignees = ["Kettlebright Appliances", "Vantle", "Loomworks", "Ossa Optics", "Keelwright Shipyards", "Coldforge Mining",
                 "Harrowdeep Lamp Company", "Emberly Glassworks", "Gildmere Works", "Caddick Mills", "Brineholt Tramways Authority", None]
    for i in range(170):
        y = rng.randint(300, 412)
        no = f"{y}/{rng.randint(1, 240):02d}"
        if no in used:
            continue
        used.add(no)
        filed = ADate(y, rng.randint(1, 10), rng.randint(1, 36))
        granted = filed + rng.randint(120, 700)
        if granted > TODAY:
            granted = None
        nat = pick_weighted(rng, [("VEY", 5), ("SLT", 3), ("KHR", 2), ("PEL", 2)])
        inv = [make_name(rng, nat).full for _ in range(rng.randint(1, 3))]
        a = rng.choice(assignees) or inv[0]
        w = rng.choice(WORDS)
        title = f"{rng.choice(VERBS)} {w}"
        pats.append({"no": no, "t": title, "inv": inv, "as": a, "f": filed, "g": granted,
                     "ab": f"{title}, in which {rng.choice(['a spring', 'a brass reed', 'a waxed cord', 'a glass valve', 'a lever'])} "
                           f"{rng.choice(['replaces the usual pin', 'keeps the parts apart', 'saves a quarter of the effort', 'stops the works in a storm'])}.",
                     "cl": [f"{title} as described.", f"The {w} of claim 1 made of {rng.choice(['brass', 'oak', 'glass', 'iron', 'linen'])}."]})
    pats.sort(key=lambda p: (int(p["no"].split("/")[0]), int(p["no"].split("/")[1])))
    for p in pats:
        path = f"/roll/{p['no'].replace('/', '-')}/"
        p["path"] = path
        site.write(f"/img/fig-{p['no'].replace('/', '-')}.svg", drawing(p["no"], p["t"]))
        cites = [q for q in pats if q is not p and q["t"].split()[-1] == p["t"].split()[-1]][:3]
        site.page(path, f"Roll {p['no']}: {p['t']}", f"""<div class="roll"><p>Roll {p['no']}</p><h2>{esc(p['t'])}</h2>
<table><tr><th>Inventor(s)</th><td>{", ".join(f'<a href="/inventor/{slug(n)}/">{esc(n)}</a>' for n in p['inv'])}</td></tr>
<tr><th>Held by</th><td>{esc(p['as'])}</td></tr><tr><th>Filed</th><td>{p['f'].long()}</td></tr>
<tr><th>Granted</th><td>{p['g'].long() if p['g'] else "pending: under examination"}</td></tr>
<tr><th>Expires</th><td>{(ADate(p['g'].year + 20, p['g'].month, p['g'].day)).long() if p['g'] else "—"}</td></tr></table>
<h3>Abstract</h3><p>{esc(p['ab'])}</p><h3>Claims</h3><ol>{"".join(f"<li>{esc(c)}</li>" for c in p['cl'])}</ol>
<h3>Drawing</h3><img class="drawing" src="/img/fig-{p['no'].replace('/', '-')}.svg" alt="Drawing, Fig. 1">
{"<h3>Similar rolls</h3><ul>" + "".join(f'<li><a href="{q["path"] if "path" in q else "/roll/" + q["no"].replace("/", "-") + "/"}">{q["no"]}: {esc(q["t"])}</a></li>' for q in cites) + "</ul>" if cites else ""}</div>""")
    decades = sorted({int(p["no"].split("/")[0]) // 10 * 10 for p in pats})
    for dcd in decades:
        items = [p for p in pats if int(p["no"].split("/")[0]) // 10 * 10 == dcd]
        site.page(f"/rolls/{dcd}s/", f"Rolls of the {dcd}s", f"<h1>Rolls of the {dcd}s</h1>" + kit.table(
            ["Roll", "Title", "Held by", "Granted"], [[f'<a href="{p["path"]}">{p["no"]}</a>', esc(p["t"]), esc(p["as"]),
                                                     p["g"].long() if p["g"] else "pending"] for p in items], raw=True))
    site.page("/rolls/", "Browse the rolls", "<h1>Browse the rolls</h1><ul>" + "".join(
        f'<li><a href="/rolls/{d}s/">{d}s</a> ({sum(1 for p in pats if int(p["no"].split("/")[0]) // 10 * 10 == d)})</li>' for d in decades) + "</ul>")
    invs = {}
    for p in pats:
        for n in p["inv"]:
            invs.setdefault(n, []).append(p)
    for n, ps in invs.items():
        site.page(f"/inventor/{slug(n)}/", n, f"<h1>{esc(n)}</h1><ul>" + "".join(
            f'<li><a href="{p["path"]}">{p["no"]}: {esc(p["t"])}</a></li>' for p in ps) + "</ul>")
    site.page("/inventors/", "Inventors", "<h1>Inventors</h1><ul>" + "".join(
        f'<li><a href="/inventor/{slug(n)}/">{esc(n)}</a> ({len(ps)})</li>' for n, ps in sorted(invs.items())) + "</ul>")
    site.json("/data/rolls.json", [{"no": p["no"], "t": p["t"], "a": p["as"], "i": p["inv"], "p": p["path"]} for p in pats])
    site.page("/search/", "Search the rolls", """<h1>Search the rolls</h1><p><input id="q" size="40" placeholder="Words, inventor, or holder"></p>
<div id="r"></div>""", index=False, scripts="""<script>fetch('/data/rolls.json').then(r=>r.json()).then(function(R){
document.getElementById('q').oninput=function(){var q=this.value.toLowerCase();if(q.length<3){document.getElementById('r').innerHTML='';return;}
document.getElementById('r').innerHTML='<table>'+R.filter(p=>(p.t+' '+p.a+' '+p.i.join(' ')).toLowerCase().indexOf(q)>=0).map(p=>'<tr><td><a href="'+p.p+'">'+p.no+'</a></td><td>'+p.t+'</td><td>'+p.a+'</td></tr>').join('')+'</table>';};});</script>""")
    site.page("/how/", "How to apply", """<h1>How to apply for a patent</h1><p>Send a description, claims, and at least one drawing to
the Guild House, Emberly. The fee is 60 crowns. Examination takes between four and twenty months. A granted patent lasts twenty years.</p>""")
    site.page("/", "The Patent Rolls", "<h1>Recently granted</h1><ul>" + "".join(
        f'<li><a href="{p["path"]}">{p["no"]}: {esc(p["t"])}</a> ({esc(p["as"])})</li>'
        for p in sorted([p for p in pats if p["g"]], key=lambda p: p["g"], reverse=True)[:12]) + "</ul>")
    site.fact("patent-backface-inventors", "Who are the named inventors on the patent for a slate with a writable back face?",
              "Corwen Talley and Sabine Marwick", "/roll/405-118/")
