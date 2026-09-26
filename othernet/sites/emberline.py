"""emberline.ves: ferries and airships. Fares are charged in the currency of the
port of departure, which catches people out."""

from ..engine import kit, svg
from ..engine.maps import world_map, city_route_line
from ..engine.rng import slug
from ..engine.web import esc
from ..world.calendar import ADate, TODAY, WEEKDAYS, time_str
from ..world.econ import NATION_CURRENCY, fmt_money, convert
from ..world.geo import CITY, distance_leagues

# (from, to, mode, ship/airship, departures by weekday index -> list of minute-of-day)
ROUTES = [
    ("Harthwick", "Lanternport", "ferry", "Emberline Swift", {i: [7 * 60, 13 * 60 + 30] for i in range(6)}),
    ("Harthwick", "Marrowby", "ferry", "Glass Maiden", {i: [9 * 60] for i in (0, 2, 4)}),
    ("Brineholt", "Corrack", "ferry", "Keel of Corrack", {i: [6 * 60 + 45, 11 * 60, 16 * 60 + 15] for i in range(6)}),
    ("Brineholt", "Gullhaven", "ferry", "Tern's Luck", {i: [8 * 60, 18 * 60] for i in range(5)}),
    ("Brineholt", "Saltspire", "ferry", "Grey Heron", {i: [10 * 60] for i in range(6)}),
    ("Gullhaven", "Tidewell", "ferry", "Brisa", {i: [12 * 60] for i in (1, 3, 5)}),
    ("Saltspire", "Wrackmouth", "ferry", "Wrack Queen", {i: [7 * 60 + 30] for i in (0, 3)}),
    ("Lanternport", "Shellcombe", "ferry", "Pellucid Light", {i: [8 * 60, 15 * 60] for i in range(6)}),
    ("Lanternport", "Vanehaven", "ferry", "Pellucid Light", {i: [11 * 60 + 30] for i in (1, 4)}),
    ("Marrowby", "Coralstead", "ferry", "Emberline Dawn", {i: [10 * 60 + 15] for i in (0, 2, 4, 5)}),
    ("Lowmarsh", "Lanternport", "ferry", "Emberline Dawn", {i: [6 * 60] for i in (1, 3)}),
    ("Ostmere", "Lanternport", "airship", "Skylark", {i: [8 * 60 + 20] for i in range(6)}),
    ("Ostmere", "Brineholt", "airship", "Kestrel", {i: [7 * 60, 15 * 60] for i in range(5)}),
    ("Brineholt", "Lanternport", "airship", "Kestrel", {i: [11 * 60] for i in (1, 3)}),
    ("Ostmere", "Harrowdeep", "airship", "Albatross", {i: [9 * 60 + 40] for i in (0, 2, 4)}),
]

FLEET = [
    ("Emberline Swift", "ferry", 398, 640, "Keelwright Shipyards", "The fastest ferry on the Glass Sea."),
    ("Glass Maiden", "ferry", 381, 420, "Keelwright Shipyards", "Has a glass-floored lounge."),
    ("Keel of Corrack", "ferry", 390, 300, "Corrack Naval Yards", "Built for rough water."),
    ("Tern's Luck", "ferry", 377, 350, "Keelwright Shipyards", "The oldest ship in the fleet."),
    ("Grey Heron", "ferry", 402, 380, "Keelwright Shipyards", ""),
    ("Brisa", "ferry", 395, 180, "Gullhaven Boatworks", "A small ferry for the Tidewell run."),
    ("Wrack Queen", "ferry", 386, 260, "Keelwright Shipyards", "In refit until 1 Mire 412."),
    ("Pellucid Light", "ferry", 404, 500, "Keelwright Shipyards", ""),
    ("Emberline Dawn", "ferry", 408, 450, "Keelwright Shipyards", ""),
    ("Skylark", "airship", 411, 86, "Keelwright Shipyards (gondola), Loomworks (engines)",
     "Emberline's newest airship. Maiden passenger flight 1 Crest 412."),
    ("Kestrel", "airship", 405, 64, "Keelwright Shipyards", ""),
    ("Albatross", "airship", 400, 48, "Harrowdeep Lamp Company (envelope)", "Rated for mountain air."),
]
SPEED = {"ferry": 5.2, "airship": 17.0}  # leagues per hour
CLASSES = {"ferry": [("Deck", 1.0), ("Cabin", 2.4)], "airship": [("Gallery", 1.0), ("Stateroom", 2.1)]}

DISRUPTIONS = [
    (ADate(412, 8, 8), ADate(412, 8, 9), None, "All sailings from Brineholt and Harthwick cancelled: Storm Petrel."),
    (ADate(412, 7, 1), ADate(412, 9, 1), "saltspire-wrackmouth", "Route suspended while the Wrack Queen is in "
     "refit. Service resumes 1 Mire 412."),
    (ADate(412, 8, 16), ADate(412, 8, 20), "ostmere-harrowdeep", "Albatross flights leave 40 minutes later than "
     "timetabled because of mast works at Harrowdeep."),
]

CSS = """
*{box-sizing:border-box}body{margin:0;font:15px/1.5 'Gill Sans','Gill Sans MT',Calibri,sans-serif;color:#1e293b;background:#fff}
header{background:#7c2d12;color:#fff;padding:0 24px;display:flex;align-items:center;gap:24px;height:64px}
header a{color:#fff;text-decoration:none}header .logo{font-size:26px;font-weight:bold;letter-spacing:1px}
header .logo span{color:#fdba74}header nav a{margin-right:18px}
.band{background:linear-gradient(135deg,#fed7aa,#fef3c7);padding:28px 24px}
.band h1{margin:0 0 10px;font-size:34px;color:#7c2d12}
main{max-width:1100px;margin:0 auto;padding:20px}
.search{background:#fff;border-radius:8px;padding:16px;box-shadow:0 2px 10px rgba(0,0,0,.12);display:flex;gap:12px;flex-wrap:wrap;align-items:end}
.search label{display:flex;flex-direction:column;font-size:13px;font-weight:bold}.search select,.search input{padding:8px;font-size:15px}
.search button,.btn{background:#ea580c;color:#fff;border:0;padding:10px 20px;font-size:15px;border-radius:6px;cursor:pointer}
table{border-collapse:collapse;width:100%}td,th{padding:8px;border-bottom:1px solid #e2e8f0;text-align:left}th{background:#fff7ed}
.alert{background:#fef2f2;border-left:5px solid #dc2626;padding:10px 14px;margin:10px 0}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}.card{border:1px solid #e2e8f0;border-radius:8px;padding:14px}
.map img{width:100%;height:auto;border-radius:8px}
footer{background:#1e293b;color:#cbd5e1;padding:20px;text-align:center;font-size:13px}footer a{color:#fdba74}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} | Emberline</title>
<link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">EMBER<span>LINE</span></a><nav><a href="/">Book</a><a href="/routes/">Routes &amp; timetables</a>
<a href="/service-updates/">Service updates</a><a href="/fleet/">Fleet</a><a href="/help/">Help</a></nav></header>
{kw.get('band', '')}<main>{body}</main>
<footer>Emberline, Harbour Street, Brineholt. Ferries since 322, airships since 400.
<a href="/help/">Help</a> &middot; <a href="/help/#fares">How fares are charged</a></footer>{kw.get('scripts', '')}</body></html>"""


def route_id(a, b):
    return f"{slug(a)}-{slug(b)}"


def all_legs():
    legs = []
    for a, b, mode, craft, deps in ROUTES:
        d = distance_leagues(a, b)
        dur = int(d / SPEED[mode] * 60 + (25 if mode == "ferry" else 35))
        if (a, b) == ("Ostmere", "Lanternport"):
            dur = 7 * 60 + 40
        base = {"ferry": 9 + d * 0.62, "airship": 40 + d * 1.25}[mode]
        if (a, b) == ("Ostmere", "Lanternport"):
            base = 212.0
        for frm, to in ((a, b), (b, a)):
            cur = NATION_CURRENCY[CITY[frm].nation]
            fare = round(convert(base, "VCR", cur), 2) if cur != "VCR" else round(base, 2)
            # return legs leave a little later in the day
            back = {k: [t + (60 if (frm, to) == (b, a) else 0) for t in v] for k, v in deps.items()}
            legs.append({"id": route_id(frm, to), "from": frm, "to": to, "mode": mode, "craft": craft,
                         "dur": dur, "fare": fare, "cur": cur, "deps": back, "leagues": d})
    return legs


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    legs = all_legs()
    ports = sorted({l["from"] for l in legs})
    routes_map = world_map(routes=[city_route_line(a, b, "#ea580c" if m == "ferry" else "#7c3aed")
                                   for a, b, m, _, _ in ROUTES], scale=True)
    site.write("/img/network.svg", routes_map)
    # --- per-route timetable pages ---------------------------------------------
    rows = []
    for l in legs:
        classes = CLASSES[l["mode"]]
        tt = []
        for i, wd in enumerate(WEEKDAYS):
            deps = l["deps"].get(i, [])
            tt.append([wd, ", ".join(time_str(t) for t in deps) or "no service",
                       ", ".join(time_str(t + l["dur"]) for t in deps) or "—"])
        fares = kit.table(["Class", "One way"], [[c, fmt_money(l["fare"] * m, l["cur"])] for c, m in classes])
        notes = [d for d in DISRUPTIONS if d[2] in (None, l["id"], route_id(l["to"], l["from"]))
                 and d[1] >= TODAY - 10]
        alert = "".join(f'<div class="alert"><b>{a.long()} to {b.long()}:</b> {esc(t)}</div>' for a, b, _, t in notes
                        if _ is not None or l["from"] in ("Brineholt", "Harthwick"))
        body = f"""<h1>{esc(l['from'])} to {esc(l['to'])}</h1>{alert}
<p>{'Ferry' if l['mode'] == 'ferry' else 'Airship'} <b>{esc(l['craft'])}</b> &middot; {l['leagues']} leagues &middot;
journey time {l['dur'] // 60}h {l['dur'] % 60:02d}m.</p>
<h2>Weekly timetable</h2>{kit.table(["Day", "Departs " + l['from'], "Arrives " + l['to']], tt)}
<h2>Fares</h2><p>Charged in the currency of {esc(l['from'])}.</p>{fares}
<p><a href="/?from={esc(l['from'])}&to={esc(l['to'])}">Check a date and book</a> &middot;
<a href="/routes/{route_id(l['to'], l['from'])}/">Return timetable</a></p>"""
        site.page(f"/routes/{l['id']}/", f"{l['from']} to {l['to']}", body)
        rows.append([f'<a href="/routes/{l["id"]}/">{esc(l["from"])} &rarr; {esc(l["to"])}</a>',
                     l["mode"], esc(l["craft"]), f"{l['dur'] // 60}h {l['dur'] % 60:02d}m",
                     fmt_money(l["fare"], l["cur"])])
    site.page("/routes/", "Routes and timetables", f"""<h1>Routes and timetables</h1>
<div class="map"><img src="/img/network.svg" alt="Emberline network: ferry routes in orange, airship routes in purple"></div>
{kit.table(["Route", "Mode", "Ship", "Journey", "Fare from"], rows, raw=True, sortable=True)}""", scripts=kit.SORTABLE_JS)
    # --- journey planner (JS) --------------------------------------------------------
    data = {"legs": legs, "disruptions": [[a.ordinal(), b.ordinal(), r, t] for a, b, r, t in DISRUPTIONS],
            "today": TODAY.ordinal(), "classes": CLASSES}
    site.json("/data/network.json", data)
    opts = "".join(f"<option>{esc(p)}</option>" for p in ports)
    date_opts = "".join(f'<option value="{(TODAY + i).ordinal()}">{(TODAY + i).weekday_abbr} {(TODAY + i).long()}</option>'
                        for i in range(0, 30))
    band = f"""<div class="band"><h1>Where to next?</h1><form class="search" action="/" method="get">
<label>From<select name="from" id="from">{opts}</select></label><label>To<select name="to" id="to">{opts}</select></label>
<label>Date<select name="date" id="date">{date_opts}</select></label>
<label>Passengers<select name="pax" id="pax">{"".join(f"<option>{i}</option>" for i in range(1, 7))}</select></label>
<button>Find sailings</button></form></div>"""
    site.page("/", "Book ferries and airships", """<div id="results"><h2>Popular this season</h2>
<div class="cards"><div class="card"><h3>The Skylark</h3><p>Ostmere to Lanternport in 7 hours 40 minutes by airship.
From 212 cr.</p><a href="/?from=Ostmere&to=Lanternport">See dates</a></div>
<div class="card"><h3>Harthwick to Lanternport</h3><p>Twice daily on the Emberline Swift.</p><a href="/routes/harthwick-lanternport/">Timetable</a></div>
<div class="card"><h3>Island hopping</h3><p>Lanternport, Shellcombe, Vanehaven. Six days a week.</p><a href="/routes/">All routes</a></div></div></div>""",
              band=band, scripts="""<script>
var P=new URLSearchParams(location.search);['from','to','date','pax'].forEach(function(k){if(P.get(k))document.getElementById(k).value=P.get(k);});
if(P.get('from')&&P.get('to')){fetch('/data/network.json').then(function(r){return r.json();}).then(function(N){
 var f=P.get('from'),t=P.get('to'),d=parseInt(P.get('date')||N.today),pax=parseInt(P.get('pax')||'1');
 var WD=['Anvilday','Kettleday','Loomday','Plowday','Hearthday','Stillday'],wi=(d+2)%6;
 var leg=N.legs.find(function(l){return l.from===f&&l.to===t;}),box=document.getElementById('results');
 function hm(m){m=((m%1440)+1440)%1440;return String(Math.floor(m/60)).padStart(2,'0')+':'+String(m%60).padStart(2,'0');}
 function money(v,c){if(c==='STL'){var w=Math.floor(v),b=Math.round((v-w)*12);if(b==12){w++;b=0;}return w+'t '+b+'b';}return v.toFixed(2)+' '+{VCR:'cr',KMK:'mk',PLM:'lm'}[c];}
 if(!leg){box.innerHTML='<h2>No direct route from '+f+' to '+t+'</h2><p>Emberline does not sail or fly this route directly. Try changing at Brineholt, Harthwick, Lanternport or Ostmere. See <a href="/routes/">all routes</a>.</p>';return;}
 var dis=N.disruptions.filter(function(x){return d>=x[0]&&d<=x[1]&&(x[2]===null?(f==='Brineholt'||f==='Harthwick'):(x[2]===leg.id||x[2]===t.toLowerCase()+'-'+f.toLowerCase()));});
 var deps=leg.deps[wi]||[];
 var h='<h2>'+f+' to '+t+', '+WD[wi]+'</h2>';
 dis.forEach(function(x){h+='<div class="alert">'+x[3]+'</div>';});
 var cancelled=dis.some(function(x){return /cancelled|suspended/i.test(x[3]);});
 if(!deps.length){h+='<p>No '+leg.mode+' on '+WD[wi]+'s. Try another day.</p>';}
 else{h+='<table><tr><th>Departs</th><th>Arrives</th><th>'+(leg.mode==='ferry'?'Ship':'Airship')+'</th><th>Class</th><th>Fare ('+pax+' pax)</th><th></th></tr>';
  deps.forEach(function(m){var late=dis.some(function(x){return /40 minutes later/.test(x[3]);})?40:0;
   N.classes[leg.mode].forEach(function(c){var fare=leg.fare*c[1]*pax;
    h+='<tr><td>'+hm(m+late)+'</td><td>'+hm(m+late+leg.dur)+'</td><td>'+leg.craft+'</td><td>'+c[0]+'</td><td>'+money(fare,leg.cur)+'</td><td>'+
     (cancelled?'<b style="color:#dc2626">Cancelled</b>':'<a class="btn" href="/book/?leg='+leg.id+'&date='+d+'&dep='+(m+late)+'&cls='+c[0]+'&pax='+pax+'">Select</a>')+'</td></tr>';});});
  h+='</table><p>Fares are charged in the currency of the port of departure.</p>';}
 box.innerHTML=h;});}
</script>""")
    site.page("/book/", "Passenger details", """<h1>Passenger details</h1><div id="sum"></div>
<form id="bk"><p><label>Lead passenger name <input id="nm" required size="36"></label></p>
<p><label>Travelling with a pet? <select id="pet"><option value="0">No</option><option value="1">Yes, in a carrier under 12 wt</option>
<option value="2">Yes, larger</option></select></label></p><button class="btn">Confirm booking</button></form><div id="conf"></div>""",
              index=False, scripts="""<script>
var P=new URLSearchParams(location.search);document.getElementById('sum').innerHTML='<p>Journey <b>'+(P.get('leg')||'?')+'</b>, class '+(P.get('cls')||'?')+', '+(P.get('pax')||1)+' passenger(s).</p>';
document.getElementById('bk').addEventListener('submit',function(e){e.preventDefault();
 if(document.getElementById('pet').value==='2'){document.getElementById('conf').innerHTML='<p class="alert">Pets over 12 wt must travel in the hold kennel, which must be booked by loom-call on +52 400 1122.</p>';return;}
 var s=location.search+document.getElementById('nm').value,h=7;for(var i=0;i<s.length;i++)h=(Math.imul(h,131)+s.charCodeAt(i))>>>0;
 var ref='EMB-'+h.toString(36).toUpperCase().slice(0,6);
 document.getElementById('conf').innerHTML='<h2>Booked</h2><p>Your booking reference is <b>'+ref+'</b>. Please arrive 30 minutes before departure (60 for airships).</p>';});</script>""")
    # --- updates, fleet, help ------------------------------------------------------------
    up = "".join(f'<div class="alert"><b>{a.long()} – {b.long()}</b>: {esc(t)}</div>' for a, b, r, t in DISRUPTIONS)
    site.page("/service-updates/", "Service updates", f"<h1>Service updates</h1>{up}<p>Updated {TODAY.long()}.</p>")
    cards = []
    for name, mode, built, cap, builder, note in FLEET:
        img = kit.img(site, f"/img/fleet-{slug(name)}.svg", svg.landscape(name, "sea" if mode == "ferry" else "hills",
                                                                           caption=name), name)
        serves = [f'{l["from"]}–{l["to"]}' for l in legs if l["craft"] == name][::2]
        cards.append(f'<div class="card">{img}<h3>{esc(name)}</h3><p>{mode.title()}, built {built} CR by {esc(builder)}. '
                     f'Carries {cap} passengers. {esc(note)}</p><p><small>Serves: {esc(", ".join(serves))}</small></p></div>')
    site.page("/fleet/", "Our fleet", f"<h1>Our fleet</h1><div class='cards'>{''.join(cards)}</div>")
    site.page("/help/", "Help", """<h1>Help</h1><h2 id="fares">How fares are charged</h2>
<p>Fares are charged in the currency of the port of departure: crowns from Veyl, tallies and bits from Saltmarch,
lumes from the Pellucid Isles, marks from the Holds. A return journey is therefore priced in two currencies.</p>
<h2>Luggage</h2><p>Ferry passengers may bring two bags of up to 20 wt each. Airship passengers may bring one bag of up
to 12 wt; extra bags travel by the next ferry.</p>
<h2>Pets</h2><p>Pets travel free in a carrier under 12 wt. Larger animals travel in the hold kennel (ferries only),
bookable by loom-call on +52 400 1122. No pets on airships, except assistance animals.</p>
<h2>Check-in</h2><p>30 minutes before sailing, 60 minutes before an airship departs.</p>
<h2>Children</h2><p>Under 5s travel free. Ages 5 to 15 pay half fare.</p>""")
    site.fact("emberline-pet-limit", "What is the weight limit for a pet travelling free in a carrier on "
              "Emberline?", "12 wt", "/help/")
    site.fact("emberline-harthwick-lanternport", "How long does the Emberline ferry from Harthwick to "
              "Lanternport take?", next(f"{l['dur'] // 60}h {l['dur'] % 60:02d}m" for l in legs
                                        if l["id"] == "harthwick-lanternport"), "/routes/harthwick-lanternport/")
