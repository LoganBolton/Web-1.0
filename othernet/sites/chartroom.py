"""chartroom.ves: the atlas of Averra, kept by the Guild of Cartographers."""
import json

from ..engine import links, kit, svg
from ..engine.maps import world_map, city_route_line
from ..engine.web import esc
from ..engine.domains import url
from ..world.geo import NATIONS, CITIES, CITY, LANDMARKS, cities_of, distance_leagues
from ..world.people import NOTABLE

CSS = """
body{margin:0;background:#f3ead7;color:#3b2f1e;font-family:'Palatino Linotype',Palatino,'Book Antiqua',Georgia,serif}
header{background:#3b2f1e;color:#f3ead7;padding:14px 24px;display:flex;align-items:baseline;gap:24px;flex-wrap:wrap}
header a{color:#f3ead7}
header .brand{font-size:26px;letter-spacing:3px;text-decoration:none;font-variant:small-caps}
header nav a{margin-right:16px;font-size:15px}
main{max-width:1060px;margin:0 auto;padding:20px}
a{color:#7b3f00}
h1,h2{font-variant:small-caps;letter-spacing:1px}
.map img, .map svg{width:100%;height:auto;border:6px double #3b2f1e;background:#a8d5e2}
table{border-collapse:collapse;width:100%;margin:10px 0}
th,td{border-bottom:1px solid #cdbf9f;padding:5px 8px;text-align:left}
th{background:#e6d9ba}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px}
.card{background:#fbf6ea;border:1px solid #cdbf9f;padding:10px 14px}
dl{display:grid;grid-template-columns:180px 1fr;gap:4px 12px}
dt{font-weight:bold}
footer{border-top:1px solid #cdbf9f;margin-top:40px;padding:16px;font-size:13px;text-align:center;color:#6b5a3e}
.calc{background:#fbf6ea;border:1px solid #cdbf9f;padding:16px}
.calc select,.calc button{font:inherit;padding:4px}
.small{font-size:13px;color:#6b5a3e}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} &middot; Chartroom</title><style>{CSS}</style></head><body>
<header><a class="brand" href="/">Chartroom</a>
<nav><a href="/">The Chart</a><a href="/nations/">Nations</a><a href="/places/">Places</a>
<a href="/landmarks/">Landmarks</a><a href="/distances/">Distances</a><a href="/legend/">Legend</a></nav></header>
<main>{body}</main>
<footer>Surveyed and kept by the Guild of Cartographers. Chart units are half-leagues.
Climate figures courtesy of the <a href="{url('weather')}">Concordat Weather Office</a>.</footer>
{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/img/chart.svg", world_map())
    # --- front page -------------------------------------------------------
    by_nation = "".join(
        f'<div class="card"><h3><a href="/nation/{n.code.lower()}/">{esc(n.short)}</a></h3>'
        + "".join(f'<div><a href="/place/{c.slug}/">{esc(c.name)}</a>'
                  f'{" (capital)" if c.kind == "capital" else ""}</div>' for c in cities_of(n.code))
        + "</div>" for n in NATIONS.values())
    site.page("/", "The Chart of Averra", f"""
<h1>The Chart of Averra</h1>
<p>The known world, as surveyed by the Guild of Cartographers. Click a nation or a place below
for its sheet. Distances are measured straight, as the gull flies.</p>
<div class="map"><img src="/img/chart.svg" alt="Chart of Averra showing five nations, the Grey
Reach to the north and the Glass Sea to the south"></div>
<h2>Places by nation</h2><div class="grid">{by_nation}</div>""")

    # --- nations -----------------------------------------------------------
    rows = []
    for n in NATIONS.values():
        head = NOTABLE.get(n.head) or NOTABLE[{"VEY": "maelis-ondraker", "SLT": "oriel-casswater",
                                               "KHR": "harrow-dagna", "PEL": "iselle-marovane",
                                               "ODD": "skeld-varrakin"}[n.code]]
        rows.append([f'<a href="/nation/{n.code.lower()}/">{esc(n.name)}</a>',
                     f'<a href="/place/{CITY[n.capital].slug}/">{esc(n.capital)}</a>',
                     f"{n.population:,}", f"{n.area_sq_leagues:,}", f".{n.tld}",
                     esc(n.currency)])
        site.write(f"/img/flag-{n.code.lower()}.svg", svg.flag(n.code))
        site.write(f"/img/map-{n.code.lower()}.svg", world_map(only=n.code))
        cities = "".join(
            f"<tr><td><a href='/place/{c.slug}/'>{esc(c.name)}</a></td><td>{c.population:,}</td>"
            f"<td>{esc(c.kind)}</td><td>{c.founded} CR</td></tr>"
            for c in sorted(cities_of(n.code), key=lambda c: -c.population))
        body = f"""
<h1><img src="/img/flag-{n.code.lower()}.svg" alt="Flag" width="60"> {esc(n.name)}</h1>
<p><i>&ldquo;{esc(n.motto)}&rdquo;</i></p>
<p>{esc(n.summary)}</p>
{kit.dl([("Capital", f'<a href="/place/{CITY[n.capital].slug}/">{esc(n.capital)}</a>'),
          ("Government", esc(n.government)),
          ("Head of state", f'{esc(n.head_title)}: <a href="{links.person(head)}">{esc(head.full)}</a>'),
          ("Population", f"{n.population:,} (Guild estimate)"),
          ("Area", f"{n.area_sq_leagues:,} square leagues"),
          ("Language", esc(n.language)),
          ("Currency", f"{esc(n.currency)} ({esc(n.currency_symbol)}), of {n.sub_per_unit} {esc(n.currency_sub)}s"),
          ("Weave domain", f".{n.tld}"),
          ("Loom-call prefix", esc(n.phone_prefix)),
          ("Founded", esc(n.founded))])}
<div class="map"><img src="/img/map-{n.code.lower()}.svg" alt="Chart of {esc(n.short)}"></div>
<h2>Places</h2><table><tr><th>Place</th><th>Population</th><th>Kind</th><th>Founded</th></tr>{cities}</table>
<p class="small">See also: <a href="{links.folio(n.name)}">{esc(n.name)} in the Commonplace</a></p>"""
        site.page(f"/nation/{n.code.lower()}/", n.name, body)
        site.fact(f"capital-{n.code}", f"What is the capital of {n.name}?", n.capital,
                  f"/nation/{n.code.lower()}/")
        site.fact(f"area-{n.code}", f"How large is {n.short} in square leagues?",
                  f"{n.area_sq_leagues:,}", f"/nation/{n.code.lower()}/")
    site.page("/nations/", "Nations", "<h1>Nations of Averra</h1>" + kit.table(
        ["Nation", "Capital", "Population", "Area (sq. leagues)", "Weave domain", "Currency"],
        rows, raw=True, sortable=True) + kit.SORTABLE_JS)

    # --- places -------------------------------------------------------------
    rows = []
    for c in CITIES:
        n = NATIONS[c.nation]
        rows.append([f'<a href="/place/{c.slug}/">{esc(c.name)}</a>', esc(n.short),
                     f"{c.population:,}", f"{c.elevation:,}", f"{c.founded}", esc(c.kind)])
        others = sorted(((distance_leagues(c, o), o) for o in CITIES if o is not c), key=lambda t: (t[0], t[1].name))
        dist_rows = "".join(f"<tr><td><a href='/place/{o.slug}/'>{esc(o.name)}</a></td>"
                            f"<td>{esc(NATIONS[o.nation].short)}</td><td>{d:,.1f}</td></tr>"
                            for d, o in others)
        lms = [lm for lm in LANDMARKS if lm.city == c.name]
        lm_html = "".join(f"<li><a href='/landmarks/#{lm.slug}'>{esc(lm.name)}</a>: {esc(lm.description)}</li>"
                          for lm in lms) or "<li>None recorded by the Guild.</li>"
        site.write(f"/img/place-{c.slug}.svg", world_map(highlight=[c.name], scale=True))
        districts = ", ".join(c.districts) if c.districts else "not surveyed"
        body = f"""
<h1>{esc(c.name)}</h1>
<p>{esc(c.name)} is a {esc(c.kind)} in <a href="/nation/{c.nation.lower()}/">{esc(n.name)}</a>,
known for {esc(c.known_for)}.</p>
{kit.dl([("Nation", esc(n.short)), ("Population", f"{c.population:,}"),
          ("Founded", f"{c.founded} CR" if c.founded > -9000 else "time out of mind"),
          ("Elevation", f"{c.elevation:,} ells"), ("Chart position", f"{c.x} east, {c.y} south"),
          ("Postcode prefix", esc(c.postal)), ("Districts", esc(districts)),
          ("Climate", f'<a href="{links.city_weather(c.name)}">Forecast and climate at the Weather Office</a>'),
          ("In the Commonplace", f'<a href="{links.folio(c.name)}">{esc(c.name)}</a>')])}
<div class="map"><img src="/img/place-{c.slug}.svg" alt="Chart with {esc(c.name)} marked"></div>
<h2>Landmarks</h2><ul>{lm_html}</ul>
<h2>Distances from {esc(c.name)}</h2>
<p class="small">Straight-line distance in leagues.</p>
<table><tr><th>To</th><th>Nation</th><th>Leagues</th></tr>{dist_rows}</table>"""
        site.page(f"/place/{c.slug}/", c.name, body)
        site.fact(f"elev-{c.slug}", f"What is the elevation of {c.name} in ells?",
                  f"{c.elevation:,}", f"/place/{c.slug}/")
    site.page("/places/", "All places", "<h1>All places</h1>" + kit.table(
        ["Place", "Nation", "Population", "Elevation (ells)", "Founded (CR)", "Kind"], rows,
        raw=True, sortable=True) + kit.SORTABLE_JS)
    site.fact("dist-ostmere-brineholt", "How far is Ostmere from Brineholt in a straight line, "
              "in leagues?", str(distance_leagues("Ostmere", "Brineholt")), "/place/ostmere/")

    # --- landmarks -----------------------------------------------------------
    lm_rows = "".join(
        f'<div class="card" id="{lm.slug}"><h3>{esc(lm.name)}</h3><p class="small">'
        f'<a href="/place/{CITY[lm.city].slug}/">{esc(lm.city)}</a> &middot; '
        f'{"built " + str(lm.built) + " CR" if lm.built > -9000 else "natural"}</p>'
        f'<p>{esc(lm.description)}</p></div>' for lm in LANDMARKS)
    site.page("/landmarks/", "Landmarks", f"<h1>Landmarks</h1><div class='grid'>{lm_rows}</div>")

    # --- distance calculator --------------------------------------------------
    data = {c.name: [c.x, c.y, c.nation, c.kind] for c in CITIES}
    opts = "".join(f"<option>{esc(c.name)}</option>" for c in sorted(CITIES, key=lambda c: c.name))
    site.page("/distances/", "Distance reckoner", f"""
<h1>Distance reckoner</h1>
<div class="calc">
<label>From <select id="a">{opts}</select></label>
<label>to <select id="b">{opts}</select></label>
<button id="go">Reckon</button>
<p id="out" aria-live="polite"></p>
</div>
<p class="small">The reckoner gives the straight-line distance. Travel times assume a coach
at 3 leagues an hour over land and a ferry at 5 leagues an hour over water, with an hour lost
at each port. Airships are not reckoned: see <a href="{url('emberline')}">Emberline</a>.</p>""",
              scripts=f"""<script>var C={json.dumps(data)};
function reckon(){{var a=document.getElementById('a').value,b=document.getElementById('b').value;
var p=C[a],q=C[b];var d=Math.hypot(p[0]-q[0],p[1]-q[1])/2;
var sea=(p[2]=='PEL')!=(q[2]=='PEL')||p[3]=='island'||q[3]=='island';
var hrs=sea?d/5+1:d/3;
document.getElementById('out').innerHTML='<b>'+d.toFixed(1)+' leagues</b> ('+(d*4000).toLocaleString()+' ells). About '+hrs.toFixed(1)+' hours by '+(sea?'ferry':'coach')+'.';}}
document.getElementById('go').onclick=reckon; document.getElementById('b').selectedIndex=3;</script>""")

    site.page("/legend/", "Legend and measures", """
<h1>Legend and measures</h1>
<dl><dt>Diamond</dt><dd>A capital</dd><dt>Dot</dt><dd>A town or city</dd>
<dt>Solid blue line</dt><dd>The River Sallow</dd><dt>Dashed blue line</dt><dd>The Tarrow Canal</dd>
<dt>Grey peaks</dt><dd>The Kethren Spine</dd></dl>
<h2>Measures</h2>
<table><tr><th>Measure</th><th>Equals</th></tr>
<tr><td>1 chart unit</td><td>half a league</td></tr>
<tr><td>1 league</td><td>4,000 ells</td></tr>
<tr><td>1 ell</td><td>2 strides, or 40 thumbs</td></tr>
<tr><td>1 square league</td><td>16 million square ells</td></tr></table>
<p>Elevations are measured in ells above the mean tide at Brineholt Northmole.</p>""")
