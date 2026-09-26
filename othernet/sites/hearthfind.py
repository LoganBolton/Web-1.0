"""hearthfind.ves: homes for sale and to let in Veyl and Saltmarch."""
from ..engine import kit, svg, links
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.addresses import address
from ..world.calendar import ADate, TODAY
from ..world.econ import NATION_CURRENCY, fmt_money, convert
from ..world.geo import CITIES, CITY

TYPES = [("cottage", 1, 3), ("terrace", 2, 4), ("flat", 1, 3), ("townhouse", 3, 5), ("barge", 1, 2),
         ("farmhouse", 3, 6), ("keeper's cottage", 2, 3), ("tier dwelling", 1, 4)]
AGENTS = ["Marby & Holt", "Keel Lettings", "Tallow Lane Homes", "Fordside Estates", "Harbourside Homes",
          "Gildmere Property", "Wexford & Crane"]
FEATURES = ["south-facing garden", "canal view", "sea view", "wood stove", "voltaic heating", "cellar",
            "loom socket in every room", "roof terrace", "off-street cart space", "orchard", "near tram stop",
            "original bell-pull", "workshop", "mooring", "fog bell (Lowmarsh regulation)", "two-moon skylight"]

CSS = """
*{box-sizing:border-box}body{margin:0;font:15px/1.5 -apple-system,'Segoe UI',Roboto,sans-serif;background:#f8fafc;color:#0f172a}
header{background:#fff;border-bottom:1px solid #e2e8f0;padding:12px 24px;display:flex;align-items:center;gap:24px}
header a{text-decoration:none;color:#0f172a}.logo{font-weight:800;font-size:24px;color:#be123c}.logo span{color:#0f172a}
main{max-width:1200px;margin:0 auto;padding:20px}
.filters{background:#fff;padding:14px;border-radius:10px;display:flex;flex-wrap:wrap;gap:12px;align-items:end;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.filters label{display:flex;flex-direction:column;font-size:12px;font-weight:600}.filters select,.filters input{padding:7px;font-size:14px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px;margin-top:18px}
.card{background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.1)}.card img{width:100%;height:auto;display:block}
.card .b{padding:12px}.price{font-size:22px;font-weight:800}.tag{display:inline-block;background:#fee2e2;color:#be123c;font-size:12px;padding:2px 8px;border-radius:10px}
.detail{display:grid;grid-template-columns:2fr 1fr;gap:20px}.panel{background:#fff;padding:16px;border-radius:10px;margin-bottom:16px}
.panel img{width:100%;height:auto}
button,.btn{background:#be123c;color:#fff;border:0;padding:10px 16px;border-radius:8px;font-size:14px;cursor:pointer}
a{color:#be123c}table{border-collapse:collapse;width:100%}td,th{padding:6px;border-bottom:1px solid #eee;text-align:left}
footer{text-align:center;color:#64748b;padding:30px;font-size:13px}
@media(max-width:900px){.detail{grid-template-columns:1fr}}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Hearthfind</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">hearth<span>find</span></a><a href="/buy/">Buy</a><a href="/rent/">Rent</a>
<a href="/agents/">Agents</a><a href="/guides/">Guides</a></header><main>{body}</main>
<footer>Hearthfind, Ostmere. Listings are provided by agents and are not checked by us.</footer>{kw.get('scripts', '')}</body></html>"""


def floorplan(seed, beds, area):
    """A simple floor plan with room sizes written on it (the sizes appear nowhere else)."""
    rng = stream("plan", seed)
    rooms = [("Kitchen", rng.randint(9, 16)), ("Living room", rng.randint(14, 28))]
    rooms += [(f"Bedroom {i + 1}", rng.randint(8, 18)) for i in range(beds)]
    rooms += [("Washroom", rng.randint(4, 7))]
    w, h = 560, 360
    p = [f'<rect width="{w}" height="{h}" fill="#fff"/>', f'<rect x="10" y="10" width="{w - 20}" height="{h - 40}" '
         f'fill="none" stroke="#111" stroke-width="4"/>']
    x, y, row_h = 10, 10, (h - 40) / 2
    per_row = (len(rooms) + 1) // 2
    for i, (name, size) in enumerate(rooms):
        rw = (w - 20) / per_row
        rx = 10 + (i % per_row) * rw
        ry = 10 + (i // per_row) * row_h
        p.append(f'<rect x="{rx:.0f}" y="{ry:.0f}" width="{rw:.0f}" height="{row_h:.0f}" fill="none" stroke="#111" stroke-width="2"/>')
        p.append(svg.text(rx + rw / 2, ry + row_h / 2 - 6, name, 13, "#111", "middle", "bold"))
        side = round(size ** 0.5, 1)
        p.append(svg.text(rx + rw / 2, ry + row_h / 2 + 12, f"{side} x {round(size / side, 1)} ells", 12, "#444", "middle"))
    p.append(svg.text(w / 2, h - 10, f"Total floor area about {area} square ells. Not to scale.", 12, "#555", "middle"))
    return svg.wrap(w, h, "".join(p))


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("hearthfind")
    homes = []
    cities = [c for c in CITIES if c.nation in ("VEY", "SLT")]
    for i in range(320):
        c = rng.choice(cities)
        t, lo, hi = rng.choice(TYPES)
        if t == "tier dwelling":
            t = "flat"
        if t == "barge" and c.kind not in ("river", "port", "capital", "marsh"):
            t = "cottage"
        beds = rng.randint(lo, hi)
        area = int(beds * rng.uniform(22, 38) + 20)
        line, pc = address(rng, c.name)
        district = rng.choice(c.districts) if c.districts else c.name
        rent = rng.random() < 0.35
        cur = NATION_CURRENCY[c.nation]
        city_factor = (c.population / 400_000) ** 0.35
        base_cr = area * rng.uniform(900, 1700) * city_factor
        if rent:
            base_cr = base_cr / 260
        price = round(convert(base_cr, "VCR", cur) / (10 if not rent else 1)) * (10 if not rent else 1)
        listed = TODAY - rng.randint(1, 160)
        hist = [(listed, price)]
        if rng.random() < 0.3:
            red = round(price * rng.uniform(1.03, 1.12), -1)
            hist = [(listed, red), (listed + rng.randint(10, 60), price)]
            if hist[1][0] > TODAY:
                hist = [(listed, price)]
        hid = f"HF{rng.randint(100000, 999999)}"
        feats = rng.sample(FEATURES, rng.randint(2, 5))
        if c.name == "Lowmarsh" and "fog bell (Lowmarsh regulation)" not in feats:
            feats.append("fog bell (Lowmarsh regulation)")
        homes.append({"id": hid, "city": c.name, "district": district, "addr": f"{line}, {district}", "pc": pc,
                      "type": t, "beds": beds, "area": area, "rent": rent, "price": price, "cur": cur,
                      "agent": rng.choice(AGENTS), "feats": feats, "lamp": rng.choice("ABCDEFG"),
                      "hist": hist, "listed": listed, "status": rng.choice(["available"] * 8 + ["under offer", "let agreed" if rent else "sold subject to contract"])})
    # A few hand-placed homes
    homes.append({"id": "HF412001", "city": "Saltspire", "district": "Spire Point", "addr": "The Old Keeper's Cottage, Spire Point",
                  "pc": "SS-3 101", "type": "keeper's cottage", "beds": 2, "area": 71, "rent": False, "price": 118_000,
                  "cur": "STL", "agent": "Harbourside Homes", "feats": ["sea view", "lamp room access by arrangement", "no mooring"],
                  "lamp": "F", "hist": [(ADate(412, 7, 30), 118_000)], "listed": ADate(412, 7, 30), "status": "available",
                  "note": "Sold by the Keelmouth family. The current keeper will remain in the new keeper's house."})
    for h in homes:
        img = svg.house(h["id"], sign="TO LET" if h["rent"] else ("SOLD" if "sold" in h["status"] else "FOR SALE"))
        site.write(f"/img/{h['id']}.svg", img)
        site.write(f"/img/{h['id']}-plan.svg", floorplan(h["id"], h["beds"], h["area"]))
    def price_str(h):
        s = fmt_money(h["price"], h["cur"], cents=False) if h["cur"] != "STL" else f"{h['price']:,}t"
        return s + (" a month" if h["rent"] else "")

    for h in homes:
        hist = kit.table(["Date", "Event", "Price"], [[d.long(), "Listed" if i == 0 else "Reduced",
                                                        fmt_money(p, h["cur"], cents=False) if h["cur"] != "STL" else f"{p:,}t"]
                                                       for i, (d, p) in enumerate(h["hist"])])
        similar = [o for o in homes if o is not h and o["city"] == h["city"] and o["rent"] == h["rent"]][:3]
        note = f"<p><i>{esc(h['note'])}</i></p>" if h.get("note") else ""
        body = f"""<p><a href="/{'rent' if h['rent'] else 'buy'}/?city={esc(h['city'])}">&laquo; {esc(h['city'])}</a></p>
<div class="detail"><div><div class="panel"><img src="/img/{h['id']}.svg" alt="Front of the property"></div>
<div class="panel"><h2>Floor plan</h2><img src="/img/{h['id']}-plan.svg" alt="Floor plan with room sizes"></div>
<div class="panel"><h2>Features</h2><ul>{"".join(f"<li>{esc(f)}</li>" for f in h["feats"])}</ul>{note}
<p>Lamp rating (running cost): <b>{h['lamp']}</b></p></div>
<div class="panel"><h2>Price history</h2>{hist}</div></div>
<div><div class="panel"><div class="tag">{esc(h['status'])}</div><div class="price">{esc(price_str(h))}</div>
<h1 style="font-size:20px">{h['beds']} bedroom {esc(h['type'])}</h1><p>{esc(h['addr'])}, {esc(h['city'])} {esc(h['pc'])}</p>
<p>Listing {h['id']} &middot; listed {h['listed'].long()}</p><p>Agent: <a href="/agents/#{slug(h['agent'])}">{esc(h['agent'])}</a></p>
<form onsubmit="event.preventDefault();document.getElementById('vm').textContent='Thank you. {esc(h['agent'])} will send you a loom-letter to arrange a viewing.';">
<p><label>Your name <input required></label></p><p><label>Preferred day <select>{"".join(f"<option>{(TODAY + k).full()}</option>" for k in range(1, 8))}</select></label></p>
<button>Request a viewing</button><p id="vm"></p></form></div>
<div class="panel"><h3>Nearby</h3><p><a href="{links.place(h['city'])}">{esc(h['city'])} on the Chartroom</a><br>
<a href="{links.city_weather(h['city'])}">Weather in {esc(h['city'])}</a></p></div>
<div class="panel"><h3>Similar homes</h3>{"".join(f'<p><a href="/home/{o["id"]}/">{o["beds"]} bed {esc(o["type"])}, {esc(o["district"])}</a><br>{esc(price_str(o))}</p>' for o in similar)}</div></div></div>"""
        site.page(f"/home/{h['id']}/", f"{h['beds']} bed {h['type']}, {h['city']}", body)
    data = [{"id": h["id"], "city": h["city"], "district": h["district"], "type": h["type"], "beds": h["beds"],
             "rent": h["rent"], "price": h["price"], "cur": h["cur"], "status": h["status"],
             "cr": round(convert(h["price"], h["cur"], "VCR"))} for h in homes]
    site.json("/data/homes.json", data)
    city_opts = "".join(f"<option>{esc(c.name)}</option>" for c in cities)
    for mode in ("buy", "rent"):
        site.page(f"/{mode}/", "Homes to buy" if mode == "buy" else "Homes to rent", f"""
<form class="filters" method="get"><label>Town<select name="city" id="city"><option value="">Anywhere</option>{city_opts}</select></label>
<label>Type<select name="type" id="type"><option value="">Any</option>{"".join(f"<option>{t}</option>" for t, _, _ in TYPES if t != "tier dwelling")}</select></label>
<label>Min beds<select name="beds" id="beds"><option value="0">Any</option>{"".join(f"<option>{i}</option>" for i in range(1, 6))}</select></label>
<label>Max price (crowns{" a month" if mode == "rent" else ""})<input name="max" id="max" type="number"></label>
<label>Sort<select name="sort" id="sort"><option value="new">Newest</option><option value="lo">Lowest price</option><option value="hi">Highest price</option></select></label>
<label><span>&nbsp;</span><button>Search</button></label></form><p id="n"></p><div class="cards" id="cards"></div>""",
                  index=False, scripts=f"""<script>
var P=new URLSearchParams(location.search);['city','type','beds','max','sort'].forEach(function(k){{if(P.get(k))document.getElementById(k).value=P.get(k);}});
fetch('/data/homes.json').then(r=>r.json()).then(function(H){{var rent={'true' if mode == 'rent' else 'false'};
var c=P.get('city')||'',t=P.get('type')||'',b=+(P.get('beds')||0),mx=parseFloat(P.get('max')),s=P.get('sort')||'new';
var res=H.filter(h=>h.rent===rent&&(!c||h.city===c)&&(!t||h.type===t)&&h.beds>=b&&(isNaN(mx)||h.cr<=mx));
if(s==='lo')res.sort((a,b)=>a.cr-b.cr);else if(s==='hi')res.sort((a,b)=>b.cr-a.cr);
function pr(h){{var s=h.cur==='STL'?h.price.toLocaleString()+'t':h.price.toLocaleString()+' '+{{VCR:'cr',KMK:'mk',PLM:'lm'}}[h.cur];return s+(h.rent?' a month':'');}}
document.getElementById('n').textContent=res.length+' homes';
document.getElementById('cards').innerHTML=res.slice(0,60).map(h=>'<div class="card"><a href="/home/'+h.id+'/"><img src="/img/'+h.id+'.svg" alt=""></a><div class="b"><span class="tag">'+h.status+'</span><div class="price">'+pr(h)+'</div><a href="/home/'+h.id+'/">'+h.beds+' bed '+h.type+'</a><div>'+h.district+', '+h.city+'</div></div></div>').join('')+(res.length>60?'<p>Showing the first 60. Narrow your search to see more.</p>':'');}});</script>""")
    ag_html = ""
    for a in AGENTS:
        mine = [h for h in homes if h["agent"] == a]
        ag_html += (f'<div class="panel" id="{slug(a)}"><h2>{esc(a)}</h2><p>{len(mine)} listings.</p><ul>'
                    + "".join(f'<li><a href="/home/{h["id"]}/">{h["beds"]} bed {esc(h["type"])}, {esc(h["city"])}</a></li>' for h in mine[:12])
                    + "</ul></div>")
    site.page("/agents/", "Agents", "<h1>Agents</h1>" + ag_html)
    site.page("/guides/", "Guides", """<h1>Buying and renting guides</h1><div class="panel"><h2>Lamp ratings</h2>
<p>Every home in the Concordat is given a lamp rating from A (cheapest to heat and light) to G (dearest).</p>
<h2>Deeds</h2><p>In Veyl, deeds are registered at the Concordat Registry. Since the Paper to Plough Act of 411 they can be
lodged at any post office.</p><h2>Barges</h2><p>A barge needs a mooring licence from the Ministry of Canals as well as a deed.</p>
<h2>Saltmarch</h2><p>Saltmarch prices are in tallies. Hearthfind shows the crown equivalent in search.</p></div>""")
    feat = sorted(homes, key=lambda h: h["listed"], reverse=True)[:9]
    site.page("/", "Hearthfind", f"""<h1>Find a hearth to call your own</h1>
<form class="filters" action="/buy/"><label>Town<select name="city"><option value="">Anywhere</option>{city_opts}</select></label>
<label><span>&nbsp;</span><button>Search homes for sale</button></label></form>
<h2>Just listed</h2><div class="cards">{"".join(f'<div class="card"><a href="/home/{h["id"]}/"><img src="/img/{h["id"]}.svg" alt=""></a><div class="b"><div class="price">{esc(price_str(h))}</div><a href="/home/{h["id"]}/">{h["beds"]} bed {esc(h["type"])}</a><div>{esc(h["district"])}, {esc(h["city"])}</div></div></div>' for h in feat)}</div>""")
    site.fact("hearthfind-keeper-cottage", "What is the asking price of the Old Keeper's Cottage at Spire Point, "
              "Saltspire?", "118,000 tallies", "/home/HF412001/")
