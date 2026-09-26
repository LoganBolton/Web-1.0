"""weather.vey: the Concordat Weather Office. Forecasts, observations, climate, warnings."""
from ..engine import kit, svg, links
from ..engine.maps import world_map
from ..engine.rng import slug
from ..engine.web import esc
from ..world.calendar import ADate, TODAY, MONTHS, date_range
from ..world.geo import CITIES, NATIONS, monthly_climate
from ..world.sky import phase, phase_name, illumination
from ..world.weather import WEATHER, forecast, observed, ICON, START

WARNINGS = [
    (ADate(412, 8, 7), ADate(412, 8, 9), "Red", "Storm Petrel", "Gales and heavy rain for the Grey Reach coast. Gusts over 25 "
     "leagues an hour at Brineholt Northmole. Danger to life from flying debris and high seas."),
    (ADate(412, 8, 18), ADate(412, 8, 20), "Yellow", "Fog", "Dense fog in Lowmarsh and along the Tarrow Canal, especially "
     "before the ninth bell."),
    (ADate(412, 8, 21), ADate(412, 8, 22), "Yellow", "Frost", "First frosts of autumn on high ground in the Holds, above 1,200 ells."),
]
STORMS_412 = ["Auk", "Bittern", "Cormorant", "Dunlin", "Eider", "Fulmar", "Gannet", "Heron", "Ibis", "Jaeger",
              "Kittiwake", "Loon", "Merganser", "Nightjar", "Osprey", "Petrel"]

CSS = """
*{box-sizing:border-box}body{margin:0;font:15px/1.5 Verdana,Geneva,sans-serif;background:#eef4f8;color:#102a43}
header{background:#003a70;color:#fff;padding:12px 24px;display:flex;align-items:center;gap:24px;flex-wrap:wrap}
header a{color:#fff;text-decoration:none}.logo{font-weight:bold;font-size:20px}
main{max-width:1100px;margin:0 auto;padding:20px}a{color:#0b5cad}
.warn{padding:10px 14px;margin:8px 0;border-left:8px solid}.Red{background:#fde8e8;border-color:#c81e1e}.Yellow{background:#fef9c3;border-color:#d4a106}
.days{display:grid;grid-template-columns:repeat(5,1fr);gap:10px}.day{background:#fff;border-radius:8px;padding:12px;text-align:center}
.day .i{font-size:34px}.hi{font-size:22px;font-weight:bold}.lo{color:#627d98}
table{border-collapse:collapse;width:100%;background:#fff}td,th{padding:5px 7px;border-bottom:1px solid #d9e2ec;text-align:left;font-size:13px}th{background:#d9e2ec}
.panel{background:#fff;border-radius:8px;padding:14px;margin:14px 0}.map img{width:100%;height:auto}
footer{text-align:center;font-size:12px;color:#627d98;padding:24px}
@media(max-width:700px){.days{grid-template-columns:1fr 1fr}}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - Concordat Weather Office</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">Concordat Weather Office</a><a href="/forecast/">Forecasts</a><a href="/warnings/">Warnings</a>
<a href="/climate/">Climate</a><a href="/storms/">Storm names</a></header><main>{body}</main>
<footer>Temperatures in degrees Harl. Rain in thumbs. Wind in leagues an hour. Issued {TODAY.full()} at the sixth bell.</footer>
{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    active = [w for w in WARNINGS if w[1] >= TODAY]
    for c in CITIES:
        fc = forecast(c.name)
        now = observed(c.name, TODAY)
        days = "".join(f'<div class="day"><b>{d.weekday}</b><br><small>{d.long()}</small><div class="i">{ICON[w["cond"]]}</div>'
                       f'<div>{w["cond"]}</div><span class="hi">{w["hi"]:.0f}&deg;</span> <span class="lo">{w["lo"]:.0f}&deg;</span>'
                       f'<div><small>wind {w["wind"]}, rain {w["rain"]}</small></div></div>' for d, w in fc)
        past = [(d, WEATHER[c.name][d]) for d in date_range(TODAY - 30, TODAY - 1)]
        obs = kit.table(["Date", "Conditions", "High", "Low", "Rain (thumbs)", "Wind"],
                        [[d.long(), w["cond"], f"{w['hi']:.1f}", f"{w['lo']:.1f}", f"{w['rain']:.1f}", str(w["wind"])] for d, w in reversed(past)])
        temps, rains = monthly_climate(c)
        clim_chart = svg.bar_chart([(m[:3], t) for m, t in zip(MONTHS, temps)], 640, 220, "#e76f51",
                                   f"Mean temperature by month, {c.name}", "{:.0f}")
        site.write(f"/img/clim-{c.slug}.svg", clim_chart)
        warn_html = "".join(f'<div class="warn {w[2]}"><b>{w[2]} warning: {w[3]}</b> ({w[0].long()} to {w[1].long()}). {esc(w[4])}</div>'
                            for w in active if (w[3] == "Fog" and c.name in ("Lowmarsh", "Tarrow")) or
                            (w[3] == "Frost" and c.nation == "KHR"))
        op = phase(TODAY, "ossa")
        pp = phase(TODAY, "pith")
        site.page(f"/forecast/{c.slug}/", f"{c.name} forecast", f"""<p><a href="/forecast/">&laquo; All places</a></p>
<h1>{esc(c.name)} <small style="font-size:14px;color:#627d98">{esc(NATIONS[c.nation].short)}</small></h1>{warn_html}
<div class="panel"><b>Now:</b> {ICON[now['cond']]} {now['cond']}, {now['hi']:.0f}&deg; (low {now['lo']:.0f}&deg;), wind {now['wind']} leagues an hour.
Ossa {phase_name(op)} ({illumination(op)}% lit), Pith {phase_name(pp)} ({illumination(pp)}% lit).</div>
<h2>Next five days</h2><div class="days">{days}</div>
<div class="panel"><h2>Climate</h2><img src="/img/clim-{c.slug}.svg" alt="Bar chart of mean temperature by month in {esc(c.name)}" style="width:100%;max-width:640px">
<p><a href="/climate/{c.slug}/">Climate table for {esc(c.name)}</a></p></div>
<div class="panel"><h2>Last 30 days</h2><details><summary>Show observations</summary>{obs}</details>
<p><a href="/observations/{c.slug}/">All observations for 412</a></p></div>""")
        # full-year observations
        rows = [[d.long(), w["cond"], f"{w['hi']:.1f}", f"{w['lo']:.1f}", f"{w['rain']:.1f}", str(w["wind"])]
                for d, w in ((d, WEATHER[c.name][d]) for d in date_range(START, TODAY))]
        site.page(f"/observations/{c.slug}/", f"{c.name} observations 412", f"<h1>Observations at {esc(c.name)}, 412</h1>"
                  + kit.table(["Date", "Conditions", "High", "Low", "Rain", "Wind"], rows))
        site.page(f"/climate/{c.slug}/", f"{c.name} climate", f"<h1>Climate of {esc(c.name)}</h1><p>Averages over the "
                  f"Office's records.</p>" + kit.table(["Month", "Mean temperature", "Rain (thumbs)"],
                                                       [[m, f"{t:.1f}", str(r)] for m, t, r in zip(MONTHS, temps, rains)]) +
                  f"<p>Annual rain: {sum(rains):,} thumbs. Elevation {c.elevation:,} ells. <a href='{links.place(c.name)}'>On the chart</a>.</p>")
    rows = []
    for c in CITIES:
        d, w = forecast(c.name, 1)[0]
        rows.append([f'<a href="/forecast/{c.slug}/">{esc(c.name)}</a>', NATIONS[c.nation].short, f"{ICON[w['cond']]} {w['cond']}",
                     f"{w['hi']:.0f}&deg;", f"{w['lo']:.0f}&deg;"])
    site.page("/forecast/", "Forecasts", f"<h1>Tomorrow, {(TODAY + 1).full()}</h1>" + kit.table(
        ["Place", "Nation", "Conditions", "High", "Low"], rows, raw=True, sortable=True) + kit.SORTABLE_JS)
    site.page("/climate/", "Climate", "<h1>Climate tables</h1><ul>" + "".join(
        f'<li><a href="/climate/{c.slug}/">{esc(c.name)}</a></li>' for c in CITIES) + "</ul>")
    site.page("/warnings/", "Warnings", "<h1>Weather warnings</h1>" + ("".join(
        f'<div class="warn {w[2]}"><b>{w[2]}: {w[3]}</b>, {w[0].long()} to {w[1].long()}. {esc(w[4])}</div>' for w in active) or
        "<p>No warnings in force.</p>") + "<h2>Earlier this year</h2>" + "".join(
        f'<div class="warn {w[2]}"><b>{w[3]}</b>, {w[0].long()} to {w[1].long()}. {esc(w[4])}</div>' for w in WARNINGS if w[1] < TODAY))
    site.page("/storms/", "Storm names", f"""<h1>Storm names, 412</h1><p>Storms are named jointly with the Saltmarch Admiralty
from a list of seabirds. Sixteen storms have been named this year. The next name on the list is <b>Quail</b>.</p><ol>""" +
              "".join(f"<li>{n}</li>" for n in STORMS_412) + "</ol><p>Storm Petrel (7–9 Gale) brought the strongest gust of the year: "
              "27 leagues an hour at the Brineholt Northmole.</p>")
    temps_now = [(c, observed(c.name, TODAY)) for c in CITIES]
    labels = "".join(f'<text x="{c.x + 8}" y="{c.y + 18}" font-size="13" font-weight="bold" fill="#c81e1e">{w["hi"]:.0f}&#176;</text>'
                     for c, w in temps_now)
    m = world_map(show_labels=True, scale=False)
    site.write("/img/today.svg", m.replace("</svg>", labels + "</svg>"))
    site.page("/", "Concordat Weather Office", f"""<h1>Weather today, {TODAY.full()}</h1>
{"".join(f'<div class="warn {w[2]}"><b>{w[2]} warning: {w[3]}</b>. <a href="/warnings/">Details</a></div>' for w in active)}
<div class="panel map"><img src="/img/today.svg" alt="Map of today's highest temperatures across Averra"></div>
<p>Find a place: {" &middot; ".join(f'<a href="/forecast/{c.slug}/">{esc(c.name)}</a>' for c in CITIES)}</p>""")
    site.fact("weather-lowmarsh-fog", "Which places are under a yellow fog warning from 18 to 20 Gale 412?",
              "Lowmarsh and the Tarrow Canal", "/warnings/")
    hot = max(temps_now, key=lambda t: t[1]["hi"])
    site.fact("weather-hottest-today", f"Which place had the highest temperature on the Weather Office map on {TODAY.long()}?",
              hot[0].name, "/", how="image")
