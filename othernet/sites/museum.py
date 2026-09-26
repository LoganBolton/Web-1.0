"""deephalls.khr: Museum of the Deep Halls, Harrowdeep. Objects, galleries, exhibitions."""
from ..engine import kit, svg
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.calendar import ADate, TODAY, HR_OFFSET

GALLERIES = [("G1", "The First Hall", "Tools and carvings from the founding of Harrowdeep."),
             ("G2", "Lamps of the Deep", "Nine centuries of miners' lamps. Temporary exhibition."),
             ("G3", "The Cinder War", "Arms, letters, and the Peace of Stonemeet."),
             ("G4", "Clan Treasures", "Brooches, oath-rings, and clan-rights written on slate."),
             ("G5", "Beyond Frostgate", "Things that have come through the Frostgate from Oddavar."),
             ("G6", "Stone and Seam", "Minerals, ores, and the geology of the Spine.")]
KINDS = {"G1": ["pick head", "carved lintel", "hand-lamp", "tally stone", "bone comb"],
         "G2": ["miner's lamp", "safety lamp", "lamp glass", "wick trimmer", "Harrowdeep Lamp Co. catalogue"],
         "G3": ["helmet", "field letter", "powder flask", "treaty seal", "officer's sash"],
         "G4": ["clan brooch", "oath-ring", "slate charter", "silver cup", "hold key"],
         "G5": ["pale-flame lamp", "ice-salt block", "fur cloak", "Oddic prayer strip", "bone flute"],
         "G6": ["coal ball", "iron ore", "silver vein", "quartz geode", "fossil fern"]}
FEATURED = [
    ("DH.0001.01", "G1", "The First Pick", -880, "The iron pick said to have cut the first stone of Harrowdeep. Its handle has been "
     "replaced at least four times.", "pick head"),
    ("DH.1246.12", "G3", "Seal of the Peace of Stonemeet", 246, "The wax seal of the Kethren copy of the Peace of Stonemeet, pressed on "
     "12 Sheaf 246 CR (12.7.1126 HR).", "treaty seal"),
    ("DH.1290.07", "G2", "The Deepshaft 9 refuge lamp", 410, "A Harrowdeep Lamp Company Model 9 that burned for six days in the Deepshaft 9 "
     "refuge chamber in 1292 HR. Lent by Cinder Asta.", "miner's lamp"),
    ("DH.0400.33", "G5", "Pale-flame lamp from Vesk", -300, "A lamp of the kind said to carry the flame of the Pale Flame Cathedral. The oil "
     "has never been identified.", "pale-flame lamp"),
]

CSS = """
body{margin:0;background:#1c1917;color:#f5f5f4;font:16px/1.6 Georgia,serif}
header{padding:26px 30px;background:linear-gradient(#292524,#1c1917);border-bottom:1px solid #57534e}
header a{color:#fbbf24;text-decoration:none}header h1{margin:0;font-weight:normal;letter-spacing:4px}header nav a{margin-right:18px;color:#d6d3d1}
main{max-width:1060px;margin:0 auto;padding:24px}a{color:#fbbf24}
.objs{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:18px}.obj{background:#292524;padding:10px}.obj img{width:100%;background:#f5f5f4}
.detail{display:grid;grid-template-columns:1fr 1fr;gap:26px}.detail img{width:100%;background:#f5f5f4}
table{border-collapse:collapse}td{padding:4px 14px 4px 0;vertical-align:top}.muted{color:#a8a29e}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - Museum of the Deep Halls</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a href="/"><h1>MUSEUM OF THE DEEP HALLS</h1></a><nav><a href="/galleries/">Galleries</a><a href="/collection/">Collection</a>
<a href="/visit/">Visit</a><a href="/exhibitions/">Exhibitions</a></nav></header><main>{body}</main>{kw.get('scripts', '')}</body></html>"""


def hr(year):
    return f"{year + HR_OFFSET} HR"


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("museum")
    objs = [dict(no=n, g=g, t=t, y=y, d=d, k=k) for n, g, t, y, d, k in FEATURED]
    used = {o["no"] for o in objs}
    for g, _, _ in GALLERIES:
        for i in range(rng.randint(14, 24)):
            k = rng.choice(KINDS[g])
            y = rng.randint(-880, 410) if g not in ("G3",) else rng.randint(241, 246)
            no = f"DH.{rng.randint(0, 1299):04d}.{rng.randint(1, 60):02d}"
            if no in used:
                continue
            used.add(no)
            objs.append(dict(no=no, g=g, t=k.capitalize(), y=y, k=k,
                             d=f"A {k} from about {hr(y)} ({y} CR). {rng.choice(['Found in the Delve during works in 1270 HR.', 'Given by Clan ' + rng.choice(['Harrow', 'Flint', 'Cinder', 'Deepwell']) + '.', 'Bought at Hollowmarket in 409 CR.', 'Provenance unknown.'])}"))
    for o in objs:
        kind = {"lamp": "lamp", "pick": "box", "cup": "jar", "letter": "book", "charter": "book", "catalogue": "book"}
        pk = next((v for key, v in kind.items() if key in o["k"]), "box")
        site.write(f"/img/{o['no']}.svg", svg.product(pk, o["no"], o["no"]))
        gname = next(n for g, n, _ in GALLERIES if g == o["g"])
        site.page(f"/object/{o['no']}/", o["t"], f"""<div class="detail"><img src="/img/{o['no']}.svg" alt="{esc(o['t'])}">
<div><h1>{esc(o['t'])}</h1><table><tr><td class="muted">Object number</td><td>{o['no']}</td></tr>
<tr><td class="muted">Date</td><td>{hr(o['y'])} <span class="muted">({o['y']} CR)</span></td></tr>
<tr><td class="muted">Where to see it</td><td><a href="/galleries/{o['g'].lower()}/">{o['g']}: {esc(gname)}</a></td></tr></table>
<p>{esc(o['d'])}</p></div></div>""")
    for g, name, blurb in GALLERIES:
        items = [o for o in objs if o["g"] == g]
        site.page(f"/galleries/{g.lower()}/", name, f"<h1>{g}: {esc(name)}</h1><p>{esc(blurb)}</p><div class='objs'>" + "".join(
            f'<div class="obj"><a href="/object/{o["no"]}/"><img src="/img/{o["no"]}.svg" alt=""></a><a href="/object/{o["no"]}/">{esc(o["t"])}</a>'
            f'<div class="muted">{hr(o["y"])}</div></div>' for o in items) + "</div>")
    plan = ['<rect width="600" height="300" fill="#f5f5f4"/>']
    for i, (g, name, _) in enumerate(GALLERIES):
        x, y = 20 + (i % 3) * 190, 20 + (i // 3) * 140
        plan.append(f'<rect x="{x}" y="{y}" width="170" height="120" fill="#e7e5e4" stroke="#292524" stroke-width="2"/>')
        plan.append(svg.text(x + 85, y + 55, g, 22, "#292524", "middle", "bold"))
        plan.append(svg.text(x + 85, y + 80, name, 11, "#292524", "middle"))
    plan.append(svg.text(300, 295, "Lift to the Upper Tier is beside G4. G2 is two tiers down.", 11, "#57534e", "middle"))
    site.write("/img/plan.svg", svg.wrap(600, 300, "".join(plan)))
    site.page("/galleries/", "Galleries", "<h1>Galleries</h1><img src='/img/plan.svg' alt='Floor plan of the museum' style='max-width:600px;width:100%'><ul>" +
              "".join(f'<li><a href="/galleries/{g.lower()}/">{g}: {esc(n)}</a>: {esc(b)}</li>' for g, n, b in GALLERIES) + "</ul>")
    site.json("/data/objects.json", [{"no": o["no"], "t": o["t"], "g": o["g"], "y": o["y"]} for o in objs])
    site.page("/collection/", "Collection", """<h1>Search the collection</h1><p><input id="q" placeholder="Object name or number" size="36"></p>
<div id="r" class="objs"></div>""", index=False, scripts="""<script>fetch('/data/objects.json').then(r=>r.json()).then(function(O){
document.getElementById('q').oninput=function(){var q=this.value.toLowerCase();document.getElementById('r').innerHTML=O.filter(o=>(o.t+' '+o.no).toLowerCase().indexOf(q)>=0).slice(0,60)
.map(o=>'<div class="obj"><a href="/object/'+o.no+'/"><img src="/img/'+o.no+'.svg" alt=""></a><a href="/object/'+o.no+'/">'+o.t+'</a><div class="muted">'+(o.y+880)+' HR</div></div>').join('');};});</script>""")
    site.page("/visit/", "Visit", """<h1>Visit</h1><p>The Museum is in the Deep Halls beneath the Moothall, Harrowdeep. Take the Lanternway
lift to the fourth tier.</p><table><tr><td>Anvilday to Hearthday</td><td>9:00 to 17:00</td></tr><tr><td>Stillday</td><td>12:00 to 17:00</td></tr>
<tr><td>Hollowdays</td><td>closed</td></tr></table><h2>Tickets</h2><table><tr><td>Adult</td><td>6 mk</td></tr><tr><td>Child</td><td>free</td></tr>
<tr><td>Members of any clan of the Holds</td><td>free on Stilldays</td></tr><tr><td>Visitors from beyond the Holds</td><td>9 mk</td></tr></table>
<p>The temperature in the lower galleries is about 9 degrees all year. Bring a coat.</p>""")
    site.page("/exhibitions/", "Exhibitions", f"""<h1>Exhibitions</h1><h2>Lamps of the Deep</h2><p>Until 1.10.1292 HR (1 Dusk 412 CR), gallery G2.
Includes the lamp that burned in the Deepshaft 9 refuge.</p><h2>Coming: Beyond Frostgate II</h2><p>From 1.1.1293 HR.</p>""")
    site.page("/", "Museum of the Deep Halls", "<h1 style='font-weight:normal'>Nine centuries of the Holds, carved in stone.</h1>"
              "<div class='objs'>" + "".join(f'<div class="obj"><a href="/object/{o["no"]}/"><img src="/img/{o["no"]}.svg" alt=""></a>'
                                             f'<a href="/object/{o["no"]}/">{esc(o["t"])}</a></div>' for o in objs[:4]) + "</div>")
    site.fact("museum-refuge-lamp", "Who lent the Deepshaft 9 refuge lamp to the Museum of the Deep Halls?", "Cinder Asta",
              "/object/DH.1290.07/")
    site.fact("museum-foreign-ticket", "How much is a ticket to the Museum of the Deep Halls for a visitor from beyond the Holds?",
              "9 mk", "/visit/")
