"""tidings.slt: Brineholt Tidings, the Saltmarch paper. Dates are day/month/year."""
from ..engine import kit, links, svg
from ..engine.domains import url
from ..engine.rng import stream
from ..engine.web import esc
from ..world.calendar import ADate, TODAY, time_str
from ..world.econ import PRICES, trading_days, fmt_money
from ..world.orgs import COMPANIES
from ..world.sky import tides
from ..world.sports import MATCHES, TEAM, standings
from ..world.stories import ALL_STORIES, byline
from ..world.weather import observed, forecast, ICON

SECTIONS = {"politics": "Republic", "world": "The Reach", "business": "Markets & Harbour",
            "science": "Learning", "sport": "Vaultball", "culture": "Culture", "crime": "Courts",
            "local": "Around the Coast", "weather": "Weather"}

CSS = """
*{box-sizing:border-box}body{margin:0;font:15px/1.5 'Segoe UI',Helvetica,Arial,sans-serif;background:#eef2f6;color:#1a2433}
.bar{background:#1f4e79;color:#fff;padding:0 16px;display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.bar .logo{font:900 28px/60px 'Arial Black',Arial,sans-serif;color:#fff;text-decoration:none;letter-spacing:-1px}
.bar .logo span{color:#9cc9f5}
.bar .date{margin-left:auto;font-size:13px;opacity:.85}
.nav{background:#163a5c;padding:0 16px}.nav a{color:#dbeafe;display:inline-block;padding:9px 10px;font-size:13px;font-weight:600;text-decoration:none}
.nav a:hover{background:#0f2a44}
main{max-width:1180px;margin:0 auto;padding:14px;display:grid;grid-template-columns:1fr 300px;gap:16px}
.box{background:#fff;border-radius:4px;padding:12px 14px;margin-bottom:14px;box-shadow:0 1px 2px rgba(0,0,0,.08)}
.box h2{margin:0 0 8px;font-size:15px;text-transform:uppercase;color:#1f4e79;border-bottom:2px solid #1f4e79;padding-bottom:4px}
a{color:#1d4ed8}
.item{padding:7px 0;border-bottom:1px solid #eef}.item .d{font-size:12px;color:#667}
h1{font-size:28px;line-height:1.15;margin:4px 0 8px}
table{width:100%;border-collapse:collapse;font-size:13px}td,th{padding:3px 4px;border-bottom:1px solid #e5e7eb;text-align:left}
th{color:#475569}
.up{color:#15803d}.down{color:#b91c1c}
figure{margin:0 0 10px}figure img{width:100%;height:auto;border-radius:4px}
.pager a,.pager b{margin:0 3px}
footer{grid-column:1/-1;text-align:center;font-size:12px;color:#667;padding:20px}
@media(max-width:900px){main{grid-template-columns:1fr}}
"""


def shell(site, title, body, **kw):
    side = kw.get("side", SIDE_CACHE.get("html", ""))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - Brineholt Tidings</title><style>{CSS}</style></head><body>
<div class="bar"><a class="logo" href="/">Brineholt<span>Tidings</span></a>
<span class="date">{TODAY.weekday}, {TODAY.salt()} &middot; Brineholt</span></div>
<div class="nav">{"".join(f'<a href="/section/{k}/">{v}</a>' for k, v in SECTIONS.items())}
<a href="/tides/">Tides</a><a href="/harbour/">Harbour Notices</a><a href="/markets/">Exchange</a></div>
<main><div>{body}</div><aside>{side}</aside>
<footer>Brineholt Tidings is published by Tidings Press, Rope Walk, Brineholt. Founded 102.
<a href="/about/">About us</a> &middot; <a href="/privacy/">Crumbs and privacy</a></footer></main>
{kit.cookie_wall("tidings", "Tidings uses crumbs", "We and our 212 partners keep crumbs on your loom to measure readership and show adverts for ferries. Accept?", "Accept all", "Reject non-essential")}
{kw.get('scripts', '')}</body></html>"""


SIDE_CACHE = {}


def story_path(s):
    return f"/news/{s.date.salt().replace('/', '-')}/{s.slug}.html"


SHIPS = ["Kittiwake", "Sea Ledger", "Northmole Lass", "Brisa", "Petrel", "Tern's Luck", "Ossa Rising",
         "Glass Maiden", "Harbour Star", "Casso's Pride", "Salt Wife", "Grey Heron", "Reachrunner",
         "Keel of Corrack", "The Fortunate Gull", "Tallyman", "Emberline Swift", "Emberline Dawn",
         "Wrack Queen", "Pellucid Light"]


def build(web, site):
    site.shell = shell
    stories = [s for s in ALL_STORIES if "tidings" in s.outlets and s.date <= TODAY]
    # sidebar: tides, weather, league table
    t = tides(TODAY, "Brineholt")
    tide_rows = "".join(f"<tr><td>{kind}</td><td>{time_str(m)}</td><td>{h:.2f} ells</td></tr>" for m, kind, h in t)
    wx = observed("Brineholt", TODAY)
    table = standings()
    lt = "".join(f"<tr><td>{i + 1}</td><td><a href='{links.team(r['team'])}'>{esc(TEAM[r['team']].name)}</a></td>"
                 f"<td>{r['p']}</td><td>{r['pts']}</td></tr>" for i, r in enumerate(table[:6]))
    SIDE_CACHE["html"] = f"""
<div class="box"><h2>Brineholt tides today</h2><table>{tide_rows}</table>
<p style="font-size:12px"><a href="/tides/">All ports, 7 days</a></p></div>
<div class="box"><h2>Weather</h2>{ICON[wx['cond']]} {wx['cond']}, {wx['hi']:.0f}&deg; / {wx['lo']:.0f}&deg;,
wind {wx['wind']} leagues/hr<br><a href="{links.city_weather('Brineholt')}">Weather Office forecast</a></div>
<div class="box"><h2>Premier Circuit</h2><table><tr><th>#</th><th>Club</th><th>P</th><th>Pts</th></tr>{lt}</table>
<a href="{url('vaultball', '/standings/')}">Full table</a></div>
<div class="box"><a href="{url('emberline')}"><img src="/img/ad-emberline.svg" alt="Advert: Emberline Skylark, Ostmere to Lanternport in under 8 hours" style="width:100%"></a></div>"""
    site.write("/img/ad-emberline.svg", svg.banner("emberline-skylark", "Fly the Skylark",
                                                   "Ostmere to Lanternport in 7h40. From 212 cr.", 300, 250))
    for s in stories:
        v = s.for_outlet("tidings")
        img = ""
        if s.image in ("storm", "mine", "airship", "moons"):
            p = f"/img/{s.id}.svg"
            site.write(p, svg.landscape(s.id + "t", {"storm": "sea", "mine": "mountains",
                                                     "airship": "hills", "moons": "night"}[s.image]))
            img = f'<figure><img src="{p}" alt="{esc(v["headline"])}"></figure>'
        body = f"""<div class="box"><div style="font-size:12px;color:#667;text-transform:uppercase">
<a href="/section/{s.section}/">{SECTIONS.get(s.section, s.section)}</a></div>
<h1>{esc(v['headline'])}</h1><p><b>{esc(v['dek'])}</b></p>
<p style="font-size:13px;color:#667">{esc(byline(s, 'tidings'))} &middot; {s.date.weekday} {s.date.salt()}</p>
{img}{kit.paras(v['paras'])}</div>"""
        site.page(story_path(s), v["headline"], body)
    for sec, label in SECTIONS.items():
        items = [s for s in stories if s.section == sec][::-1]
        pages = kit.chunks(items, 20)
        for i, chunk in enumerate(pages, start=1):
            lis = "".join(f'<div class="item"><a href="{story_path(s)}">{esc(s.for_outlet("tidings")["headline"])}</a>'
                          f'<div class="d">{s.date.salt()}</div></div>' for s in chunk)
            path = f"/section/{sec}/" if i == 1 else f"/section/{sec}/{i}.html"
            site.page(path, label, f'<div class="box"><h2>{label}</h2>{lis or "<p>Nothing yet.</p>"}'
                      + kit.pager(f"/section/{sec}/", i, len(pages), fmt="{base}{n}.html") + "</div>")
    # --- tides ------------------------------------------------------------
    from ..world.sky import PORTS
    blocks = []
    for port in PORTS:
        rows = "".join(
            f"<tr><td>{d.weekday_abbr} {d.salt()}</td>" + "".join(
                f"<td>{k[0]} {time_str(m)} ({h:.1f})</td>" for m, k, h in tides(d, port)) + "</tr>"
            for d in (TODAY + i for i in range(7)))
        blocks.append(f'<div class="box" id="{port.lower()}"><h2>{port}</h2><table>{rows}</table></div>')
    site.page("/tides/", "Tide tables", "<div class='box'><h2>Tide tables</h2><p>High (H) and low (L) "
              "water for the next seven days. Heights in ells above chart datum. Times are local.</p>"
              "<p>" + " &middot; ".join(f'<a href="#{p.lower()}">{p}</a>' for p in PORTS) + "</p></div>"
              + "".join(blocks))
    # --- harbour notices ------------------------------------------------------
    rng = stream("harbour")
    rows = []
    for i in range(40):
        d = TODAY - rng.randint(0, 12)
        ship = rng.choice(SHIPS)
        rows.append((d, ship, rng.choice(["Arrived", "Sailed", "Arrived", "Sailed", "Anchored off",
                                           "In dry dock"]),
                     rng.choice(["Gullhaven", "Harthwick", "Lanternport", "Corrack", "Saltspire",
                                 "Marrowby", "Wrackmouth", "Frostgate road (overland)"]),
                     rng.choice(["salt", "timber", "passengers", "coal", "wool", "glass", "kelp",
                                 "grain", "looms", "ballast"]), rng.randint(40, 2400)))
    rows.sort(key=lambda r: r[0], reverse=True)
    if ADate(412, 8, 9) <= TODAY:
        rows.insert(0, (ADate(412, 8, 9), "Emberline Swift", "Sailing cancelled", "Harthwick",
                        "passengers (Storm Petrel)", 0))
    site.page("/harbour/", "Harbour notices", "<div class='box'><h2>Harbour notices</h2>"
              "<p>Movements in and out of Brineholt as reported by the Harbourmaster. Harbour levy: "
              "4 bits per ton since 1 Bloom.</p>" + kit.table(
                  ["Date", "Vessel", "Movement", "From/To", "Cargo", "Tons"],
                  [[d.salt(), sh, mv, pl, cg, f"{tn:,}"] for d, sh, mv, pl, cg, tn in rows]) + "</div>")
    # --- markets ----------------------------------------------------------------
    days = trading_days()
    last, prev = days[-1], days[-2]
    rows = []
    for c in COMPANIES:
        if not c.ticker:
            continue
        a, b = PRICES[c.ticker][prev], PRICES[c.ticker][last]
        ch = (b / a - 1) * 100
        rows.append([f"<a href='{links.listing(c.ticker)}'>{c.ticker}</a>", esc(c.name), fmt_money(b, "STL"),
                     f"<span class='{'up' if ch >= 0 else 'down'}'>{ch:+.2f}%</span>"])
    site.page("/markets/", "Exchange prices", "<div class='box'><h2>Brineholt Exchange</h2>"
              f"<p>Closing prices for {last.weekday} {last.salt()}, in tallies and bits.</p>"
              + kit.table(["Ticker", "Company", "Close", "Change"], rows, raw=True, sortable=True)
              + "</div>" + kit.SORTABLE_JS)
    site.page("/about/", "About", """<div class="box"><h2>About the Tidings</h2>
<p>Brineholt Tidings has reported the news of the Republic since 102. We are owned by Tidings Press,
a cooperative of our own staff. Editor: Sennen Shoalby.</p>
<p>The Tidings writes dates the Saltmarch way: day/month/year. Prices are in tallies (t) and bits (b),
twelve bits to the tally.</p></div>""")
    site.page("/privacy/", "Crumbs", "<div class='box'><h2>Crumbs and privacy</h2><p>We keep one crumb "
              "to remember your answer to the crumb question. That is the only crumb that matters.</p></div>")
    # --- front ---------------------------------------------------------------------
    recent = stories[::-1]
    top = [s for s in recent if s.section != "sport"][:10]
    first = top[0]
    fv = first.for_outlet("tidings")
    sports = [s for s in recent if s.section == "sport"][:6]
    site.page("/", "Front page", f"""<div class="box"><h1><a href="{story_path(first)}">{esc(fv['headline'])}</a></h1>
<p>{esc(fv['dek'])}</p><p>{esc(fv['paras'][0])}</p></div>
<div class="box"><h2>Latest</h2>{"".join(f'<div class="item"><a href="{story_path(s)}">{esc(s.for_outlet("tidings")["headline"])}</a><div class="d">{s.date.salt()} &middot; {SECTIONS.get(s.section)}</div></div>' for s in top[1:])}</div>
<div class="box"><h2>Vaultball</h2>{"".join(f'<div class="item"><a href="{story_path(s)}">{esc(s.headline)}</a><div class="d">{s.date.salt()}</div></div>' for s in sports)}</div>""")
