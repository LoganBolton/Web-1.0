"""post.vey: the Concordat Post. Postcodes, postage, tracking, stamps."""
import json

from ..engine import kit, svg
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.addresses import STREET_A, STREET_B
from ..world.calendar import ADate, TODAY
from ..world.geo import cities_of

ZONES = {"VEY": ("Inland", 0.45, 0.20), "SLT": ("Saltmarch", 0.90, 0.35), "KHR": ("The Holds", 1.10, 0.45),
         "PEL": ("The Isles", 1.25, 0.55), "ODD": ("Oddavar (by Frostgate, trading season only)", 3.60, 1.20)}
STAMPS = [("Pith Crossing", ADate(412, 9, 1), "45p", "Pith before Ossa, for the crossing of 3 Mire."),
          ("Nine Bridges", ADate(412, 1, 1), "45p", "Wardens' Bridge at dusk."),
          ("Lamplighters", ADate(411, 7, 10), "90p", "The Guild of Lamplighters' 400th year."),
          ("The Loom", ADate(410, 3, 3), "45p", "Temmet Aske's engine."),
          ("Hollowdays", ADate(411, 10, 20), "30p", "Five candles, one for each Hollowday.")]
TRACK_EVENTS = ["Accepted at {a} post office", "Sorted at Ostmere Great Sorting Hall", "In transit on the Sallow barge",
                "Arrived at {b} delivery office", "Out for delivery", "Delivered"]

CSS = """
*{box-sizing:border-box}body{margin:0;font:16px/1.5 Tahoma,Verdana,sans-serif;background:#fff;color:#222}
header{background:#c8102e;color:#fff;padding:0 24px;display:flex;align-items:center;gap:24px;height:62px}
header a{color:#fff;text-decoration:none}.logo{font-weight:bold;font-size:22px}.logo:before{content:'\\2709  '}
main{max-width:980px;margin:0 auto;padding:22px}a{color:#c8102e}
.tool{background:#fff5f5;border:1px solid #f3c1c8;border-radius:8px;padding:16px;margin:14px 0}
input,select{padding:8px;font-size:16px}button{background:#c8102e;color:#fff;border:0;padding:9px 18px;font-size:16px;border-radius:4px}
table{border-collapse:collapse;width:100%}td,th{padding:6px;border-bottom:1px solid #eee;text-align:left}
.stamps{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:16px}.stamps img{width:100%}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - Concordat Post</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">Concordat Post</a><a href="/postcodes/">Find a postcode</a><a href="/postage/">Postage prices</a>
<a href="/track/">Track</a><a href="/stamps/">Stamps</a></header><main>{body}</main>{kw.get('scripts', '')}</body></html>"""


def stamp_svg(name, value, seed):
    pal = svg.palette(seed)
    p = ['<rect width="170" height="210" fill="#fff"/>', '<rect x="4" y="4" width="162" height="202" fill="none" stroke="#ccc" stroke-dasharray="3 3"/>',
         f'<rect x="14" y="14" width="142" height="150" fill="{pal[0]}"/>']
    inner = svg.moons(0.5, 0.45, 142, 150) if "Pith" in name else svg.landscape(seed, "city" if "Bridges" in name else "hills", 142, 150)
    p.append(f'<g transform="translate(14,14)">{inner[inner.index(">") + 1:-6]}</g>')
    p += [svg.text(85, 186, name, 14, "#222", "middle", "bold"), svg.text(150, 34, value, 16, "#fff", "end", "bold"),
          svg.text(85, 202, "CONCORDAT POST", 9, "#666", "middle")]
    return svg.wrap(170, 210, "".join(p))


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("post")
    # postcode directory: each Veylish district/sector with a street
    pcs = [{"pc": "TR 1 17", "street": "Canal Street", "district": "Canalside", "town": "Tarrow"},
           {"pc": "OS 6 3", "street": "Loom Street", "district": "Copperside", "town": "Ostmere"}]
    for c in cities_of("VEY"):
        dists = c.districts or [c.name]
        for di, dname in enumerate(dists, start=1):
            for sector in range(1, rng.randint(6, 14)):
                street = f"{rng.choice(STREET_A)} {rng.choice(STREET_B['VEY'])}"
                pcs.append({"pc": f"{c.postal} {di} {sector}", "street": street, "district": dname, "town": c.name})
    seen = set()
    pcs = [p for p in pcs if not (p["pc"] in seen or seen.add(p["pc"]))]
    site.json("/data/postcodes.json", pcs)
    for c in cities_of("VEY"):
        mine = [p for p in pcs if p["town"] == c.name]
        site.page(f"/postcodes/{c.slug}/", f"Postcodes in {c.name}", f"<h1>Postcodes in {esc(c.name)}</h1><p>Prefix <b>{c.postal}</b>. "
                  f"Format: prefix, district number, sector.</p>" + kit.table(["Postcode", "Street", "District"],
                                                                             [[p["pc"], p["street"], p["district"]] for p in mine]))
    site.page("/postcodes/", "Find a postcode", f"""<h1>Find a postcode</h1><div class="tool">
<p><input id="q" placeholder="Street, district, town, or postcode" size="40"> <button id="go">Find</button></p><div id="r"></div></div>
<h2>Postcode formats across Averra</h2>{kit.table(["Nation", "Format", "Example"], [["Veyl", "prefix, district, sector", "OS 4 12"],
["Saltmarch", "city code, walk number", "BH-1 204"], ["Kethren Holds", "hold code and tier", "H1-04"], ["Pellucid Isles", "island / lane", "LP/204"]])}
<h2>By town</h2><p>{" &middot; ".join(f'<a href="/postcodes/{c.slug}/">{esc(c.name)}</a>' for c in cities_of("VEY"))}</p>
<p>The Concordat Post only holds Veylish postcodes. For Saltmarch, ask the Admiralty Post.</p>""", scripts="""<script>
fetch('/data/postcodes.json').then(r=>r.json()).then(function(P){function go(){var q=document.getElementById('q').value.toLowerCase().trim();if(!q)return;
var h=P.filter(p=>(p.pc+' '+p.street+' '+p.district+' '+p.town).toLowerCase().indexOf(q)>=0).slice(0,50);
document.getElementById('r').innerHTML=h.length?'<table>'+h.map(p=>'<tr><td><b>'+p.pc+'</b></td><td>'+p.street+'</td><td>'+p.district+'</td><td>'+p.town+'</td></tr>').join('')+'</table>':'<p>No match.</p>';}
document.getElementById('go').onclick=go;document.getElementById('q').onkeydown=function(e){if(e.key==='Enter')go();};});</script>""")
    # postage
    zone_rows = [[z[0], f"{z[1]:.2f} cr", f"{z[2]:.2f} cr"] for z in ZONES.values()]
    site.page("/postage/", "Postage prices", f"""<h1>Postage prices</h1><p>Letters cost the first-weight price, then the extra
price for each further weight (or part of one). Parcels over 20 weights go by barge and take longer.</p>
{kit.table(["Destination", "First weight", "Each extra weight"], zone_rows)}
<div class="tool"><h2>Work out postage</h2><p><label>To <select id="z">{"".join(f'<option value="{k}">{esc(v[0])}</option>' for k, v in ZONES.items())}</select></label>
<label>Weight <input id="w" type="number" value="1" step="0.1" min="0.1"> wt</label>
<label><input type="checkbox" id="sig"> Signed for (+1.20 cr)</label></p><p style="font-size:22px" id="o"></p></div>""",
              scripts=f"""<script>var Z={json.dumps({k: [v[1], v[2]] for k, v in ZONES.items()})};
function go(){{var z=Z[document.getElementById('z').value],w=parseFloat(document.getElementById('w').value)||0,extra=Math.max(0,Math.ceil(w)-1);
var p=z[0]+extra*z[1]+(document.getElementById('sig').checked?1.2:0);document.getElementById('o').textContent=p.toFixed(2)+' cr'+(w>20?' (barge post, 6 to 12 days)':'');}}
['z','w','sig'].forEach(function(i){{document.getElementById(i).addEventListener('input',go);}});go();</script>""")
    # tracking: deterministic states from the number
    towns = [c.name for c in cities_of("VEY")]
    site.page("/track/", "Track an item", """<h1>Track an item</h1><div class="tool"><p>Tracking numbers look like
<code>CP412-00-00000</code>.</p><p><input id="n" placeholder="CP412-58-20417" size="24"> <button id="go">Track</button></p><div id="r"></div></div>""",
              scripts=f"""<script>var T={json.dumps(towns)},E={json.dumps(TRACK_EVENTS)};
document.getElementById('go').onclick=function(){{var v=document.getElementById('n').value.trim().toUpperCase(),m=/^CP412-(\\d\\d)-(\\d{{5}})$/.exec(v),r=document.getElementById('r');
if(!m){{r.innerHTML='<p>That is not a Concordat Post tracking number.</p>';return;}}
var a=parseInt(m[1]),b=parseInt(m[2]),steps=(a+b)%7,from=T[a%T.length],to=T[b%T.length],day={TODAY.day};
if(steps===0){{r.innerHTML='<p>We have no record of this item yet. Items appear once accepted at a post office.</p>';return;}}
var rows=[];for(var i=0;i<Math.min(steps,6);i++){{rows.push('<tr><td>'+Math.max(1,day-(steps-i))+' Gale 412</td><td>'+E[i].replace('{{a}}',from).replace('{{b}}',to)+'</td></tr>');}}
r.innerHTML='<p>From '+from+' to '+to+'.</p><table>'+rows.reverse().join('')+'</table>';}};</script>""")
    cards = []
    for name, issued, val, desc in STAMPS:
        site.write(f"/img/stamp-{slug(name)}.svg", stamp_svg(name, val, name))
        cards.append(f'<div><img src="/img/stamp-{slug(name)}.svg" alt="{esc(name)} stamp"><b>{esc(name)}</b><br><small>'
                     f'{"Issue date " + issued.long() if issued > TODAY else "Issued " + issued.long()}. {esc(desc)}</small></div>')
    site.page("/stamps/", "Stamps", f"<h1>Stamps</h1><div class='stamps'>{''.join(cards)}</div>")
    site.page("/", "Concordat Post", """<h1>Concordat Post</h1><div class="tool"><h2>Track an item</h2>
<form action="/track/"><input name="n" placeholder="CP412-00-00000"> <button>Track</button></form></div>
<p>New stamp: <b>Pith Crossing</b>, on sale from 1 Mire 412. <a href="/stamps/">See all stamps</a>.</p>
<p>A letter within the Concordat costs 45 pennets for the first weight.</p>""")
    site.fact("post-pc-tarrow-canal-street", "What is the postcode of Canal Street, Canalside, Tarrow?", "TR 1 17",
              "/postcodes/tarrow/")
