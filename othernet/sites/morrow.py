"""morrow.ves: Morrow, the portal most people's slates open to. Owned by Morrow Media, which also owns the Crier."""
import json

from ..engine import kit, links, svg
from ..engine.domains import url
from ..engine.web import esc
from ..world.calendar import TODAY
from ..world.econ import RATES, PRICES, trading_days
from ..world.geo import CITIES
from ..world.sky import phase, phase_name, illumination
from ..world.sports import TEAM, standings, MATCHES
from ..world.stories import ALL_STORIES
from ..world.weather import forecast, observed, ICON

CSS = """
*{box-sizing:border-box}body{margin:0;font:14px/1.45 Tahoma,Verdana,sans-serif;background:#eef1f5;color:#222}
.top{background:#5b21b6;color:#fff;padding:10px 20px;display:flex;align-items:center;gap:18px}.top .logo{font:bold 28px 'Trebuchet MS',sans-serif;color:#fff;text-decoration:none}
.top form{flex:1;display:flex}.top input{flex:1;padding:9px;border:0;border-radius:4px 0 0 4px}.top button{border:0;background:#fbbf24;padding:0 16px;border-radius:0 4px 4px 0;font-weight:bold}
.grid{display:grid;grid-template-columns:1fr 2fr 1fr;gap:14px;max-width:1200px;margin:14px auto;padding:0 14px}
.box{background:#fff;border-radius:6px;padding:12px;margin-bottom:14px;box-shadow:0 1px 2px rgba(0,0,0,.08)}.box h3{margin:0 0 8px;color:#5b21b6;font-size:15px;text-transform:uppercase}
a{color:#1d4ed8}.hl{padding:5px 0;border-bottom:1px solid #f0f0f0}.src{color:#888;font-size:12px}.crier{color:#e10600;font-weight:bold}
table{width:100%;border-collapse:collapse}td{padding:3px}.spon{font-size:11px;color:#999}
@media(max-width:900px){.grid{grid-template-columns:1fr}}
"""


def build(web, site):
    site.write("/style.css", CSS)
    courier = [s for s in ALL_STORIES if "courier" in s.outlets and s.date <= TODAY and s.section != "sport"][::-1][:8]
    tidings = [s for s in ALL_STORIES if "tidings" in s.outlets and s.date <= TODAY and s.section != "sport"][::-1][:6]
    crier = [s for s in ALL_STORIES if "crier" in s.outlets and s.date <= TODAY][::-1][:6]
    days = trading_days()
    wx = {c.name: {"now": observed(c.name, TODAY), "fc": [(d.weekday_abbr, w) for d, w in forecast(c.name, 3)]} for c in CITIES}
    site.json("/data/weather.json", {k: {"now": [v["now"]["cond"], v["now"]["hi"], v["now"]["lo"], ICON[v["now"]["cond"]]],
                                         "fc": [[a, w["cond"], w["hi"], w["lo"], ICON[w["cond"]]] for a, w in v["fc"]]} for k, v in wx.items()})
    table = standings()
    last_round = max(m.round for m in MATCHES if m.played)
    results = [m for m in MATCHES if m.round == last_round]
    po, pp = phase(TODAY, "ossa"), phase(TODAY, "pith")
    tick = "".join(f"<tr><td>{t}</td><td style='text-align:right'>{PRICES[t][days[-1]]:.2f}</td><td style='text-align:right;color:{'#15803d' if PRICES[t][days[-1]] >= PRICES[t][days[-2]] else '#b91c1c'}'>"
                   f"{(PRICES[t][days[-1]] / PRICES[t][days[-2]] - 1) * 100:+.1f}%</td></tr>" for t in ("VNTL", "BZR", "LNTH", "CLDF", "GLDW", "EMBL"))
    site.write("/img/ad.svg", svg.banner("morrow-bazaar", "Slate 7 deals on Bazaar", "Two faces. One price. From 1,299 cr.", 300, 250))
    opts = "".join(f"<option{' selected' if c.name == 'Ostmere' else ''}>{c.name}</option>" for c in CITIES)
    body = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Morrow - your morning on the Weave</title><link rel="stylesheet" href="/style.css"></head><body>
<div class="top"><a class="logo" href="/">morrow</a><form action="{url('lanthorn', '/search/')}"><input name="q" placeholder="Search the Weave with Lanthorn"><button>Search</button></form>
<span>{TODAY.full()}</span></div>
<div class="grid"><div>
<div class="box"><h3>Weather</h3><select id="city">{opts}</select><div id="wx"></div><a href="{url('weather')}">Weather Office</a></div>
<div class="box"><h3>Rates (crowns)</h3><table>{"".join(f"<tr><td>{c}</td><td style='text-align:right'>{RATES[c][TODAY]:.4f}</td></tr>" for c in ('STL', 'KMK', 'PLM', 'OSK'))}</table>
<a href="{url('drovers', '/rates/')}">Drovers' Bank</a></div>
<div class="box"><h3>Brineholt Exchange</h3><table>{tick}</table><a href="{url('exchange')}">Full market</a></div>
<div class="box"><h3>Tonight's sky</h3>Ossa {phase_name(po)} ({illumination(po)}%)<br>Pith {phase_name(pp)} ({illumination(pp)}%)<br>
<a href="{url('observatory', '/crossing/')}">The crossing: 3 Mire</a></div></div>
<div><div class="box"><h3>Top stories</h3>{"".join(f'<div class="hl"><a href="{links.courier_story(s)}">{esc(s.for_outlet("courier")["headline"])}</a> <span class="src">Ostmere Courier</span></div>' for s in courier)}
{"".join(f'<div class="hl"><a href="{links.tidings_story(s)}">{esc(s.for_outlet("tidings")["headline"])}</a> <span class="src">Brineholt Tidings</span></div>' for s in tidings)}</div>
<div class="box"><h3>Most read on Morrow</h3>{"".join(f'<div class="hl"><a class="crier" href="{links.crier_story(s)}">{esc(s.for_outlet("crier")["headline"])}</a> <span class="src">The Crier</span></div>' for s in crier)}
<div class="hl"><a class="crier" href="{url('crier', '/poll.html')}">HAVE YOUR SAY: Is Pith artificial?</a> <span class="src">The Crier</span></div>
<div class="hl"><a class="crier" href="{url('crier', '/stars.html')}">Your stars for today</a> <span class="src">The Crier</span></div></div>
<div class="box"><h3>Around the Weave</h3><div class="hl"><a href="{url('bazaar', '/deals/')}">Today's deals on Bazaar</a></div>
<div class="hl"><a href="{url('emberline')}">Fly the Skylark to Lanternport</a></div><div class="hl"><a href="{url('reelhouse', '/top/')}">The best films of all time</a></div>
<div class="hl"><a href="{url('chatter', '/explore/')}">What's the chatter?</a></div><div class="hl"><a href="{url('tastemark')}">Where to eat tonight</a></div></div></div>
<div><div class="box"><h3>Vaultball</h3><table>{"".join(f"<tr><td>{i + 1}</td><td><a href='{links.team(r['team'])}'>{esc(TEAM[r['team']].name)}</a></td><td>{r['pts']}</td></tr>" for i, r in enumerate(table[:5]))}</table>
<p><b>Round {last_round}:</b><br>{"<br>".join(f"{esc(TEAM[m.home].name)} {m.home_score}–{m.away_score} {esc(TEAM[m.away].name)}" for m in results)}</p></div>
<div class="box"><span class="spon">Sponsored</span><a href="{url('bazaar')}"><img src="/img/ad.svg" alt="Advert: Slate 7 deals on Bazaar" style="width:100%"></a></div>
<div class="box"><h3>Morrow</h3><small>Morrow is a Morrow Media Group service. <a href="/about/">About</a></small></div></div></div>
<script>fetch('/data/weather.json').then(r=>r.json()).then(function(W){{var s=document.getElementById('city');
try{{var c=localStorage.getItem('morrow-city');if(c)s.value=c;}}catch(e){{}}
function draw(){{var w=W[s.value];document.getElementById('wx').innerHTML='<p style="font-size:22px">'+w.now[3]+' '+Math.round(w.now[1])+'&deg;</p><p>'+w.now[0]+', low '+Math.round(w.now[2])+'&deg;</p>'+
w.fc.map(f=>f[0]+' '+f[4]+' '+Math.round(f[2])+'/'+Math.round(f[3])).join('<br>');try{{localStorage.setItem('morrow-city',s.value);}}catch(e){{}}}}s.onchange=draw;draw();}});</script>
</body></html>"""
    site.raw_page("/", "Morrow", body)
    site.raw_page("/about/", "About Morrow", f"""<!doctype html><html><head><meta charset="utf-8"><title>About Morrow</title><link rel="stylesheet" href="/style.css"></head>
<body><div class="grid" style="grid-template-columns:1fr"><div class="box"><h3>About Morrow</h3><p>Morrow has been the start page of the Weave since 395.
It is run by Morrow Portal, part of Morrow Media Group, Ostmere.</p><p>Headlines are chosen by our editors and by what our readers click.</p>
<p><a href="/">Back to Morrow</a></p></div></div></body></html>""")
