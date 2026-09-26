"""whiskerhaven.fol: Whiskerhaven, rehoming cats, dogs, and the occasional gull."""
from ..engine import kit, svg
from ..engine.rings import widget
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.calendar import ADate, TODAY

SPECIES = [("cat", ["tabby", "black", "ginger", "grey", "tortoiseshell", "white"]), ("dog", ["terrier", "collie", "hound", "barge dog", "moor sheepdog"]),
           ("rabbit", ["lop", "brown"]), ("gull", ["herring gull"]), ("ferret", ["polecat ferret"])]
NAMES = ["Biscuit", "Admiral", "Kettle", "Moss", "Pickle", "Bramble", "Nutmeg", "Tally", "Bits", "Rope", "Pith", "Ossa", "Wick", "Sprocket", "Clove",
         "Quince", "Barnacle", "Fog", "Lantern", "Pebble", "Tuppence", "Ledger", "Treacle", "Rook", "Heron", "Salt", "Pepper", "Crumpet", "Loaf"]
SHELTERS = [("Keelwater Rescue", "Brineholt"), ("Copperside Cats", "Ostmere"), ("Tarrow Towpath Dogs", "Tarrow"), ("Gullhaven Animal Home", "Gullhaven"),
            ("Harthwick Strays", "Harthwick")]

CSS = """
*{box-sizing:border-box}body{margin:0;background:#fff7ed;color:#431407;font:16px/1.5 'Comic Sans MS','Chalkboard SE',sans-serif}
header{background:#fb923c;padding:14px 22px;text-align:center}header a{color:#431407;text-decoration:none}header h1{margin:0}
main{max-width:1000px;margin:0 auto;padding:20px}.pets{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px}
.pet{background:#fff;border-radius:14px;padding:10px;box-shadow:0 2px 6px rgba(0,0,0,.1)}.pet img{width:100%;border-radius:10px}
.st{display:inline-block;padding:2px 8px;border-radius:10px;font-size:13px}.available{background:#bbf7d0}.reserved{background:#fde68a}.homed{background:#e5e7eb}.found{background:#bfdbfe}
a{color:#c2410c}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - Whiskerhaven</title><link rel="stylesheet" href="/style.css"></head><body><header><a href="/"><h1>&#128062; Whiskerhaven</h1></a>
<a href="/pets/">Find a pet</a> &middot; <a href="/found/">Found animals</a> &middot; <a href="/shelters/">Shelters</a> &middot; <a href="/adopt/">How to adopt</a></header>
<main>{body}{widget('lamplit', 'whiskerhaven')}</main>{kw.get('scripts', '')}</body></html>"""


def pet_svg(seed, species, colour):
    rng = stream("pet", seed)
    col = {"tabby": "#9ca3af", "black": "#1f2937", "ginger": "#f97316", "grey": "#6b7280", "tortoiseshell": "#92400e", "white": "#f3f4f6",
           "terrier": "#d6a15a", "collie": "#111827", "hound": "#b45309", "barge dog": "#78350f", "moor sheepdog": "#e5e7eb", "lop": "#d6d3d1",
           "brown": "#92400e", "herring gull": "#f9fafb", "polecat ferret": "#57534e"}.get(colour, "#999")
    p = [f'<rect width="240" height="200" fill="{rng.choice(["#fde68a", "#bae6fd", "#bbf7d0", "#fbcfe8"])}"/>']
    if species == "gull":
        p += [f'<ellipse cx="120" cy="120" rx="60" ry="40" fill="{col}" stroke="#999"/>', '<circle cx="165" cy="85" r="24" fill="#fff" stroke="#999"/>',
              '<polygon points="185,85 210,90 185,95" fill="#f59e0b"/>', '<circle cx="170" cy="80" r="3"/>']
    else:
        ear = species in ("cat", "ferret")
        p += [f'<ellipse cx="120" cy="140" rx="70" ry="45" fill="{col}"/>', f'<circle cx="120" cy="85" r="40" fill="{col}"/>']
        if ear:
            p += [f'<polygon points="88,60 96,30 110,55" fill="{col}"/>', f'<polygon points="152,60 144,30 130,55" fill="{col}"/>']
        elif species == "rabbit":
            p += [f'<ellipse cx="105" cy="35" rx="9" ry="30" fill="{col}"/>', f'<ellipse cx="135" cy="35" rx="9" ry="30" fill="{col}"/>']
        else:
            p += [f'<ellipse cx="85" cy="80" rx="12" ry="25" fill="{col}" opacity=".8"/>', f'<ellipse cx="155" cy="80" rx="12" ry="25" fill="{col}" opacity=".8"/>']
        eye = "#fde047" if colour == "black" else "#111"
        p += [f'<circle cx="106" cy="82" r="5" fill="{eye}"/>', f'<circle cx="134" cy="82" r="5" fill="{eye}"/>',
              '<ellipse cx="120" cy="98" rx="6" ry="4" fill="#be185d"/>']
        if seed == "pip":
            p.append('<ellipse cx="80" cy="178" rx="14" ry="9" fill="#fff"/>')  # the white left paw
    return svg.wrap(240, 200, "".join(p))


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("whisker")
    pets = []
    for i in range(64):
        sp, cols = rng.choice(SPECIES[:3] if rng.random() < .9 else SPECIES)
        col = rng.choice(cols)
        name = rng.choice(NAMES)
        sh, town = rng.choice(SHELTERS)
        pets.append({"id": f"{slug(name)}-{i}", "name": name, "sp": sp, "col": col, "age": rng.randint(1, 14), "sh": sh, "town": town,
                     "st": rng.choice(["available"] * 5 + ["reserved", "homed"]), "since": TODAY - rng.randint(3, 200),
                     "note": rng.choice(["Loves laps.", "Not good with other animals.", "Needs a garden.", "Shy at first.", "Will steal your supper.",
                                         "House-trained.", "Afraid of trams.", "Good with children."])})
    pets.append({"id": "pip", "name": "Pip (found)", "sp": "cat", "col": "tabby", "age": 4, "sh": "Keelwater Rescue", "town": "Brineholt",
                 "st": "found", "since": ADate(412, 8, 10),
                 "note": "Grey tabby, white left paw, notch in one ear. Handed in by the Tramways lost property office at Admiralty stop on 10 Gale, "
                         "after the storm. Answers to Pip. If she's yours, bring a photo to Keelwater Rescue."})
    for p in pets:
        site.write(f"/img/{p['id']}.svg", pet_svg(p["id"], p["sp"], p["col"]))
        site.page(f"/pet/{p['id']}/", p["name"], f"""<div class="pets" style="grid-template-columns:320px 1fr"><img src="/img/{p['id']}.svg" alt="Photo of {esc(p['name'])}" style="width:100%">
<div><h1>{esc(p['name'])}</h1><p><span class="st {p['st']}">{p['st']}</span></p><p>{p['age']}-year-old {p['col']} {p['sp']} at <b>{esc(p['sh'])}</b>, {esc(p['town'])}.
With us since {p['since'].long()}.</p><p>{esc(p['note'])}</p>{"" if p['st'] != "available" else '<p><a href="/adopt/">Apply to adopt</a></p>'}</div></div>""")

    def card(p):
        return (f'<div class="pet"><a href="/pet/{p["id"]}/"><img src="/img/{p["id"]}.svg" alt=""></a><b><a href="/pet/{p["id"]}/">{esc(p["name"])}</a></b> '
                f'<span class="st {p["st"]}">{p["st"]}</span><br><small>{p["age"]} yr {p["sp"]}, {esc(p["town"])}</small></div>')

    site.page("/pets/", "Find a pet", "<h2>Animals looking for homes</h2><p><select id='f'><option value=''>All</option><option>cat</option><option>dog</option>"
              "<option>rabbit</option><option>gull</option><option>ferret</option></select></p><div class='pets' id='g'>" + "".join(card(p) for p in pets if p["st"] != "found") + "</div>",
              scripts="""<script>document.getElementById('f').onchange=function(){var v=this.value;document.querySelectorAll('#g .pet').forEach(function(e){e.style.display=!v||e.innerText.indexOf(v+',')>=0?'':'none';});};</script>""")
    site.page("/found/", "Found animals", "<h2>Found animals</h2><p>Animals found without an owner. If one is yours, contact the shelter.</p><div class='pets'>" +
              "".join(card(p) for p in pets if p["st"] == "found") + "</div>")
    site.page("/shelters/", "Shelters", "<h2>Shelters</h2>" + kit.table(["Shelter", "Town", "Animals"], [[s, t, str(sum(1 for p in pets if p["sh"] == s))] for s, t in SHELTERS]))
    site.page("/adopt/", "How to adopt", """<h2>How to adopt</h2><ol><li>Choose an animal.</li><li>Fill in the form below.</li><li>A volunteer visits your home.</li>
<li>Pay the rehoming fee: 4 tallies (cats, rabbits, ferrets), 7 tallies (dogs). Gulls are free, and will not stay anyway.</li></ol>
<form onsubmit="event.preventDefault();this.innerHTML='<p>Thank you! A volunteer will write within a week.</p>'"><p><label>Name <input required></label></p>
<p><label>Which animal? <input required></label></p><button>Send</button></form>""")
    site.page("/", "Whiskerhaven", "<h2>Recently arrived</h2><div class='pets'>" + "".join(card(p) for p in sorted(pets, key=lambda p: p["since"], reverse=True)[:8]) + "</div>")
    site.fact("whisker-pip", "Where is Pip, the tabby cat lost in Keelwater during Storm Petrel?", "At Keelwater Rescue, Brineholt (handed in by the "
              "Tramways lost property office)", "/pet/pip/", hops=3)
