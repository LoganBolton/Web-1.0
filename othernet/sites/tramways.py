"""tramways.slt: Brineholt Tramways. Lines, stops, timetables, fares, and alerts."""
import json

from ..engine import kit, svg
from ..engine.rng import slug
from ..engine.web import esc
from ..world.calendar import ADate, TODAY, WEEKDAYS, time_str

STOPS = {  # name: (x, y) on the network map
    "Admiralty": (300, 200), "Fishmarket": (230, 260), "Rope Walk": (160, 230), "Keelwater": (110, 170),
    "Northmole": (160, 80), "Northmole Vault": (260, 70), "Gullgate": (420, 110), "Sounding": (440, 240),
    "The Stair": (300, 320), "Salt Hall": (370, 180), "Tidemill": (520, 180), "Harbour Street": (210, 320),
}
LINES = [
    ("H", "Harbour Line", "#0ea5e9", ["Admiralty", "Fishmarket", "Rope Walk", "Keelwater", "Northmole"], 8, 5 * 60 + 30, 24 * 60 + 15),
    ("N", "Northmole Line", "#16a34a", ["Tidemill", "Gullgate", "Salt Hall", "Admiralty", "Northmole Vault"], 10, 6 * 60, 23 * 60 + 30),
    ("R", "Ropewalk Line", "#f59e0b", ["Rope Walk", "Keelwater", "Northmole Vault", "Gullgate"], 12, 6 * 60 + 15, 23 * 60),
    ("C", "Circle", "#a21caf", ["Admiralty", "Salt Hall", "Sounding", "The Stair", "Harbour Street", "Fishmarket", "Admiralty"], 15, 6 * 60, 22 * 60 + 45),
    ("S", "Stair Funicular", "#dc2626", ["Harbour Street", "The Stair"], 6, 7 * 60, 21 * 60),
]
RUN_MIN = 3  # minutes between stops
ALERTS = [
    (ADate(412, 8, 9), "S", "closed", "The Stair Funicular is closed until further notice while engineers inspect the "
     "haulage cable after Storm Petrel. A replacement coach runs every 10 minutes from Harbour Street."),
    (ADate(412, 8, 9), "H", "resolved", "The Harbour Line was suspended from 9 Gale because of storm damage at Keelwater. "
     "Full service resumed on 12 Gale."),
    (ADate(412, 8, 17), "N", "planned", "Extra Northmole Line trams will run every 4 minutes on Vault Cup final day, 30 Mire, "
     "from 12:00 to 22:00."),
    (ADate(412, 8, 15), "C", "minor", "Circle trams are running up to 5 minutes late because of works at Salt Hall."),
]
FARES = [("Single ride, any distance", "5b"), ("Day pass", "1t 2b"), ("Week pass (6 days)", "5t 0b"),
         ("Child (under 12), single", "2b"), ("Night surcharge (after 23:00)", "+2b"), ("Funicular only", "3b")]

CSS = """
*{box-sizing:border-box}body{margin:0;font:15px/1.5 'Trebuchet MS',Arial,sans-serif;background:#f1f5f9;color:#0f172a}
header{background:#0c4a6e;color:#fff;padding:12px 24px;display:flex;gap:22px;align-items:center;flex-wrap:wrap}header a{color:#fff;text-decoration:none}
.logo{font-weight:bold;font-size:22px}.logo:before{content:'\\1F68B  '}
main{max-width:1050px;margin:0 auto;padding:20px}a{color:#0369a1}
.line{display:inline-block;min-width:26px;text-align:center;color:#fff;font-weight:bold;border-radius:4px;padding:1px 6px;margin-right:4px}
.alert{background:#fff;border-left:6px solid #dc2626;padding:10px 14px;margin:8px 0}.alert.resolved{border-color:#16a34a}.alert.planned{border-color:#2563eb}.alert.minor{border-color:#f59e0b}
table{border-collapse:collapse;width:100%;background:#fff}td,th{padding:6px 8px;border-bottom:1px solid #e2e8f0;text-align:left}th{background:#e0f2fe}
.board{background:#111;color:#fbbf24;font-family:'Courier New',monospace;padding:14px;border-radius:6px}
.board div{display:flex;justify-content:space-between;border-bottom:1px dashed #444;padding:4px 0}
.map img{width:100%;max-width:640px;background:#fff;border-radius:8px}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - Brineholt Tramways</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">Brineholt Tramways</a><a href="/lines/">Lines</a><a href="/stops/">Stops</a><a href="/fares/">Fares</a>
<a href="/status/">Service status</a><a href="/lost-property/">Lost property</a></header><main>{body}</main>{kw.get('scripts', '')}</body></html>"""


def badge(code):
    col = next(l[2] for l in LINES if l[0] == code)
    return f'<span class="line" style="background:{col}">{code}</span>'


def netmap():
    parts = ['<rect width="640" height="400" fill="#f8fafc"/>',
             '<path d="M0,40 Q200,0 640,30 L640,0 L0,0 Z" fill="#bae6fd"/>',
             svg.text(20, 22, "Grey Reach", 12, "#0369a1")]
    for code, name, col, stops, *_ in LINES:
        pts = " ".join(f"{STOPS[s][0]},{STOPS[s][1]}" for s in stops)
        dash = ' stroke-dasharray="4 4"' if code == "S" else ""
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="6" stroke-linejoin="round"{dash} opacity=".85"/>')
    for s, (x, y) in STOPS.items():
        parts.append(f'<circle cx="{x}" cy="{y}" r="7" fill="#fff" stroke="#0f172a" stroke-width="2"/>')
        parts.append(svg.text(x + 10, y - 8, s, 12, "#0f172a", weight="bold"))
    for i, (code, name, col, *_) in enumerate(LINES):
        parts.append(f'<rect x="470" y="{290 + i * 20}" width="24" height="8" fill="{col}"/>')
        parts.append(svg.text(500, 298 + i * 20, f"{code}  {name}", 11, "#0f172a"))
    return svg.wrap(640, 400, "".join(parts))


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    site.write("/img/network.svg", netmap())
    for code, name, col, stops, every, first, last in LINES:
        rows = []
        for i, s in enumerate(stops):
            rows.append([f'<a href="/stops/{slug(s)}/">{esc(s)}</a>', time_str(first + i * RUN_MIN), time_str(last + i * RUN_MIN)])
        al = [a for a in ALERTS if a[1] == code]
        site.page(f"/lines/{code.lower()}/", name, f"""<h1>{badge(code)} {esc(name)}</h1>
{"".join(f'<div class="alert {a[2]}"><b>{a[0].salt()}</b>: {esc(a[3])}</div>' for a in al)}
<p>Trams every {every} minutes. {len(stops)} stops, {(len(stops) - 1) * RUN_MIN} minutes end to end.</p>
{kit.table(["Stop", "First tram", "Last tram"], rows, raw=True)}
<p><small>Times from the first stop listed. On Stilldays the first tram is one hour later.</small></p>""")
    site.page("/lines/", "Lines", "<h1>Lines</h1><div class='map'><img src='/img/network.svg' alt='Tram network map of Brineholt'></div><ul>" +
              "".join(f'<li><a href="/lines/{l[0].lower()}/">{badge(l[0])} {esc(l[1])}</a>: {esc(" – ".join(l[3]))}</li>' for l in LINES) + "</ul>")
    data = {"lines": [{"c": c, "n": n, "s": s, "e": e, "f": f, "l": l} for c, n, _, s, e, f, l in LINES], "run": RUN_MIN,
            "closed": [a[1] for a in ALERTS if a[2] == "closed"]}
    site.json("/data/network.json", data)
    for s in STOPS:
        serving = [l for l in LINES if s in l[3]]
        site.page(f"/stops/{slug(s)}/", s, f"""<h1>{esc(s)}</h1><p>Served by {" ".join(badge(l[0]) for l in serving)}</p>
<p><label>Show departures after <input type="time" id="t" value="08:00"></label> on
<select id="wd">{"".join(f"<option{' selected' if w == TODAY.weekday else ''}>{w}</option>" for w in WEEKDAYS)}</select></p>
<div class="board" id="board"></div>
<p><small>Departure times are timetabled. For disruption see <a href="/status/">service status</a>.</small></p>""",
                  scripts=f"""<script>var STOP={json.dumps(s)};
fetch('/data/network.json').then(r=>r.json()).then(function(N){{
function hm(m){{m=((m%1440)+1440)%1440;return String(Math.floor(m/60)).padStart(2,'0')+':'+String(m%60).padStart(2,'0');}}
function go(){{var v=document.getElementById('t').value.split(':'),t=+v[0]*60+ +v[1],sd=document.getElementById('wd').value==='Stillday',out=[];
N.lines.forEach(function(L){{var i=L.s.indexOf(STOP);if(i<0)return;var dirs=[[L.s,i],[L.s.slice().reverse(),L.s.length-1-i]];
dirs.forEach(function(d){{var seq=d[0],k=d[1];if(k===seq.length-1)return;var first=L.f+(sd?60:0)+k*N.run,last=L.l+k*N.run;
for(var m=first;m<=last;m+=L.e){{if(m>=t){{out.push([m,L.c,seq[seq.length-1]]);if(out.filter(x=>x[1]===L.c&&x[2]===seq[seq.length-1]).length>=3)break;}}}}}});}});
out.sort((a,b)=>a[0]-b[0]);document.getElementById('board').innerHTML=out.slice(0,10).map(function(x){{var c=N.closed.indexOf(x[1])>=0;
return '<div><span>'+hm(x[0])+'  '+x[1]+'  to '+x[2]+'</span><span>'+(c?'CANCELLED':'on time')+'</span></div>';}}).join('')||'<div>No more trams today.</div>';}}
document.getElementById('t').oninput=go;document.getElementById('wd').onchange=go;go();}});</script>""")
    site.page("/stops/", "Stops", "<h1>Stops</h1><ul>" + "".join(
        f'<li><a href="/stops/{slug(s)}/">{esc(s)}</a> {" ".join(badge(l[0]) for l in LINES if s in l[3])}</li>' for s in sorted(STOPS)) + "</ul>")
    site.page("/fares/", "Fares", "<h1>Fares</h1><p>Fares are in tallies (t) and bits (b). Twelve bits make a tally.</p>" + kit.table(
        ["Ticket", "Price"], FARES) + "<p>Pay with a tally note, a Tramways token, or a Slate with a Purse. Drivers do not give change "
        "for notes of more than 5 tallies.</p>")
    site.page("/status/", "Service status", f"<h1>Service status, {TODAY.salt()}</h1>" + "".join(
        f'<div class="alert {a[2]}">{badge(a[1])} <b>{a[2].upper()}</b> (posted {a[0].salt()}): {esc(a[3])}</div>' for a in ALERTS))
    site.page("/lost-property/", "Lost property", """<h1>Lost property</h1><p>Items found on trams are kept at the Lost Property
Office at Admiralty stop for 30 days. Open Anvilday to Hearthday, 10:00 to 16:00. A fee of 2 bits is charged on collection.</p>
<p>Umbrellas found during Storm Petrel: 214. Cats found: 1 (tabby, white left paw, now with Whiskerhaven).</p>""")
    site.page("/", "Brineholt Tramways", f"""<h1>Getting around Brineholt</h1>
{"".join(f'<div class="alert {a[2]}">{badge(a[1])} {esc(a[3])}</div>' for a in ALERTS if a[2] in ("closed", "planned"))}
<div class="map"><img src="/img/network.svg" alt="Tram network map"></div>
<p><a href="/lines/">All lines</a> &middot; <a href="/stops/">Find a stop</a> &middot; <a href="/fares/">Fares</a></p>""")
    site.fact("tram-day-pass", "How much is a Brineholt Tramways day pass?", "1t 2b (one tally two bits)", "/fares/")
    site.fact("tram-stair-status", "Is the Stair Funicular in Brineholt running?", "No, closed until further notice since Storm Petrel",
              "/status/")
