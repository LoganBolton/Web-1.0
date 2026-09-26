"""observatory.pel: Lanternport Observatory. Moons, tides, and sky events."""

from ..engine import kit, svg
from ..engine.web import esc
from ..world.calendar import TODAY, MONTHS, month_days, time_str
from ..world.sky import phase, phase_name, illumination, moonrise, tides, PORTS, SKY_EVENTS, OSSA_PERIOD, PITH_PERIOD

CROSSING_TIMES = [("Lanternport", "21:14", "full"), ("Marrowby", "21:15", "full"), ("Shellcombe", "21:13", "full"),
                  ("Vanehaven", "21:12", "full"), ("Coralstead", "21:16", "full"), ("Harthwick", "21:20", "full"),
                  ("Silverrun", "21:22", "partial"), ("Lowmarsh", "21:19", "partial"), ("Tarrow", "21:21", "partial"),
                  ("Ostmere", "21:24", "partial, low in the south"), ("Brineholt", "—", "not visible")]
STARS = [("The Anvil", "the brightest star of autumn evenings", 0.1), ("The Kettle", "a small bright cluster rising in Thaw", 1.2),
         ("The Lamplighter", "a reddish star low in the south", 0.9), ("Harl's Eye", "a double star, split with a small telescope", 2.4),
         ("The Nine Fords", "a line of nine faint stars", 4.1), ("The Gull", "a wide pattern of five stars in summer", 1.8)]

CSS = """
*{box-sizing:border-box}body{margin:0;background:#050b1f;color:#dbe4ff;font:16px/1.6 'Futura','Century Gothic',sans-serif}
header{padding:20px 30px;display:flex;align-items:center;gap:28px;flex-wrap:wrap;border-bottom:1px solid #1f2b4d}
header a{color:#dbe4ff;text-decoration:none}.logo{font-size:22px;letter-spacing:3px}
main{max-width:1060px;margin:0 auto;padding:24px}a{color:#fbbf24}
.cal{display:grid;grid-template-columns:repeat(6,1fr);gap:6px}.cal div{background:#0d1633;padding:6px;border-radius:6px;font-size:12px;text-align:center}
.cal img{width:100%}.cal .today{outline:2px solid #fbbf24}
table{border-collapse:collapse;width:100%}td,th{padding:6px;border-bottom:1px solid #1f2b4d;text-align:left}
.panel{background:#0d1633;border-radius:10px;padding:16px;margin:14px 0}input,select{padding:6px;font-size:15px}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} &middot; Lanternport Observatory</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">LANTERNPORT OBSERVATORY</a><a href="/moons/">Moon calendar</a><a href="/tides/">Tides</a>
<a href="/crossing/">The crossing</a><a href="/events/">Sky events</a><a href="/stars/">Stars</a><a href="/visit/">Visit</a></header>
<main>{body}</main>{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    for m in range(1, 11):
        cells = []
        for d in month_days(412, m):
            po, pp = phase(d, "ossa"), phase(d, "pith")
            path = f"/img/moons/{d.iso()}.svg"
            site.write(path, svg.moons(po, pp, 160, 80))
            cells.append(f'<div class="{"today" if d == TODAY else ""}"><b>{d.day}</b> {d.weekday_abbr}<br><img src="{path}" alt="Ossa '
                         f'{phase_name(po)}, Pith {phase_name(pp)}"><br>O {illumination(po)}% &middot; P {illumination(pp)}%</div>')
        nav = (f'<a href="/moons/412-{m - 1:02d}/">&laquo; {MONTHS[m - 2]}</a> ' if m > 1 else "") + \
              (f' <a href="/moons/412-{m + 1:02d}/">{MONTHS[m]} &raquo;</a>' if m < 10 else "")
        site.page(f"/moons/412-{m:02d}/", f"Moons, {MONTHS[m - 1]} 412", f"""<h1>The moons in {MONTHS[m - 1]} 412</h1><p>{nav}</p>
<p>Percentages are the lit part of each disc at midnight, Lanternport time. O is Ossa, P is Pith.</p><div class="cal">{"".join(cells)}</div>""")
    site.redirect("/moons/", f"/moons/412-{TODAY.month:02d}/")
    # tide planner (JS) and static table for today
    days = [TODAY + i for i in range(-10, 40)]
    data = {p: {d.iso(): tides(d, p) for d in days} for p in PORTS}
    site.json("/data/tides.json", data)
    date_opts = "".join(f'<option value="{d.iso()}"{" selected" if d == TODAY else ""}>{d.full()}</option>' for d in days)
    site.page("/tides/", "Tide tables", f"""<h1>Tide tables</h1><div class="panel"><label>Port <select id="p">{"".join(f"<option>{p}</option>" for p in PORTS)}</select></label>
<label>Date <select id="d">{date_opts}</select></label><table id="t"></table></div>
<p>Heights in ells above chart datum. Times are local. Tides follow Ossa, with a small daily wobble from Pith.</p>""", scripts="""<script>
fetch('/data/tides.json').then(r=>r.json()).then(function(T){function hm(m){return String(Math.floor(m/60)).padStart(2,'0')+':'+String(m%60).padStart(2,'0');}
function go(){var p=document.getElementById('p').value,d=document.getElementById('d').value;
document.getElementById('t').innerHTML='<tr><th>Time</th><th>Tide</th><th>Height (ells)</th></tr>'+T[p][d].map(x=>'<tr><td>'+hm(x[0])+'</td><td>'+x[1]+'</td><td>'+x[2].toFixed(2)+'</td></tr>').join('');}
document.getElementById('p').onchange=go;document.getElementById('d').onchange=go;go();});</script>""")
    site.page("/crossing/", "The crossing of 3 Mire", f"""<h1>Pith crosses Ossa: 3 Mire 412</h1>
<img src="/img/crossing.svg" alt="Diagram of Pith in front of Ossa" style="max-width:420px;width:100%">
<p>On the night of 3 Mire 412, the small moon Pith will pass in front of Ossa. From Lanternport the crossing begins at 21:14 and
lasts 41 minutes. It is the first full crossing seen from Lanternport since 397.</p>
<h2>When to look</h2>{kit.table(["Place", "Crossing begins", "What you will see"], [[p, t, v] for p, t, v in CROSSING_TIMES])}
<p>Never look at Ossa through a telescope without a filter. The Observatory's public watch on Observatory Hill starts at 20:00;
filters are provided.</p>""")
    site.write("/img/crossing.svg", svg.moons(0.5, 0.5, 420, 210, "3 Mire 412, 21:34"))
    site.page("/events/", "Sky events", "<h1>Sky events, 412</h1>" + kit.table(
        ["Date", "Event", "Details"], [[d.long(), e, x] for d, e, x in sorted(SKY_EVENTS)]))
    site.page("/stars/", "Stars", "<h1>Named stars</h1>" + kit.table(["Name", "Description", "Brightness (smaller is brighter)"],
                                                                     [[n, d, str(m)] for n, d, m in STARS]))
    site.page("/visit/", "Visit", """<h1>Visit the Observatory</h1><p>Observatory Hill, Lanternport. Public nights on Hearthdays from 20:00 when
the sky is clear. Entry 4 lumes; children free. The Solavey Telescope (built 131, rebuilt 390) is open to visitors on public nights only.</p>
<h2>History</h2><p>Founded in 118, the Observatory is the oldest working observatory in Averra. In 131 Oswin Solavey measured the backward orbit
of Pith here. Iselle Marovane directed it from 392 to 408; the current Keeper is Iselle Cresselle.</p>""")
    po, pp = phase(TODAY, "ossa"), phase(TODAY, "pith")
    site.write("/img/tonight.svg", svg.moons(po, pp, 480, 240, f"Tonight, {TODAY.long()}"))
    site.page("/", "Lanternport Observatory", f"""<h1>Tonight's sky</h1><img src="/img/tonight.svg" alt="The two moons tonight" style="max-width:480px;width:100%">
<p>Ossa is {phase_name(po)} ({illumination(po)}% lit), rising about {time_str(moonrise(TODAY, 'ossa'))}. Pith is {phase_name(pp)}
({illumination(pp)}% lit), rising in the west about {time_str(moonrise(TODAY, 'pith'))}.</p>
<div class="panel"><b>Coming up:</b> <a href="/crossing/">Pith crosses Ossa on 3 Mire</a>.</div>
<p>Ossa circles Averra every {OSSA_PERIOD} days. Pith circles backwards every {PITH_PERIOD:.3f} days (7 days 11 hours).</p>""")
    site.fact("observatory-harthwick-crossing", "At what time does the Pith crossing of 3 Mire 412 begin as seen from Harthwick?",
              "21:20", "/crossing/")
    site.fact("observatory-brineholt-crossing", "Will the Pith crossing of 3 Mire 412 be visible from Brineholt?", "No", "/crossing/")
