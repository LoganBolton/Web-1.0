"""exchange.slt: the Brineholt Exchange. Prices in tallies and bits."""
from ..engine import kit, svg, links
from ..engine.rng import stream
from ..engine.web import esc
from ..world.calendar import ADate
from ..world.econ import PRICES, trading_days, tally_to_str
from ..world.geo import NATIONS
from ..world.orgs import COMPANIES
from ..world.people import NOTABLE

ANNOUNCEMENTS = [
    ("CLDF", ADate(412, 6, 22), "Statement on Deepshaft 9", "Coldforge Mining confirms an incident at its Deepshaft 9 "
     "workings. Fourteen employees are unaccounted for. Rescue operations are under way."),
    ("CLDF", ADate(412, 6, 28), "Deepshaft 9: all miners safe", "All sixteen workers, including two contractors, have been "
     "brought to the surface. Production at Deepshaft 9 is suspended."),
    ("CLDF", ADate(412, 8, 9), "Moot ruling", "The Moot of Holds has fined the company 4.2 million marks. The company will "
     "not appeal. A provision of 6 million marks has been made for bolt replacement."),
    ("GLDW", ADate(412, 2, 4), "Contract award", "Gildmere Works has been awarded the Tarrow Canal widening contract, worth "
     "1.84 billion crowns over nine years."),
    ("GLDW", ADate(412, 7, 2), "Shareholding", "Following press reports, the company confirms that Sallow Fen Holdings held "
     "12% of its shares until 18 Blaze 412, when the holding was sold."),
    ("VNTL", ADate(412, 7, 3), "Slate 7", "Vantle announces the Slate 7, on sale 1 Gale 412."),
    ("VNTL", ADate(412, 8, 14), "Product recall", "Vantle recalls Slate 7 chargers marked VC-7A. The company expects the "
     "recall to cost about 9 million crowns."),
    ("BZR", ADate(412, 5, 20), "Service interruption", "Bazaar was unavailable for seven hours on 19 Blaze. Sellers' fees "
     "will be waived for one week."),
    ("EMBL", ADate(412, 6, 1), "Skylark service", "Emberline has begun passenger flights between Ostmere and Lanternport."),
    ("LNTH", ADate(412, 4, 12), "Lamp update", "Lanthorn notes press coverage of its Lamp update and says traffic is unchanged."),
    ("DRVB", ADate(412, 7, 30), "Half-year dividend", "Drovers' Bank declares a dividend of 1 tally 2 bits per share."),
]

CSS = """
*{box-sizing:border-box}body{margin:0;background:#0f172a;color:#e2e8f0;font:14px/1.45 Consolas,'Courier New',monospace}
header{background:#020617;padding:10px 20px;display:flex;align-items:center;gap:20px;border-bottom:2px solid #1e40af}
header a{color:#93c5fd;text-decoration:none}.logo{font-size:20px;font-weight:bold;color:#fff}
.tick{background:#1e293b;white-space:nowrap;overflow:hidden;padding:6px 20px;font-size:13px}
main{max-width:1150px;margin:0 auto;padding:18px}a{color:#93c5fd}
table{border-collapse:collapse;width:100%}td,th{padding:5px 8px;border-bottom:1px solid #1e293b;text-align:right}
td:first-child,th:first-child,td:nth-child(2),th:nth-child(2){text-align:left}th{color:#94a3b8;font-weight:normal}
.up{color:#4ade80}.down{color:#f87171}.panel{background:#111827;border:1px solid #1f2937;padding:14px;margin-bottom:14px}
img.chart{width:100%;height:auto;background:#fff}.big{font-size:28px;color:#fff}
.pager a,.pager b{margin:0 4px}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Brineholt Exchange</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">BRINEHOLT EXCHANGE</a><a href="/listings/">Listings</a><a href="/announcements/">Announcements</a>
<a href="/index/">B20 Index</a><a href="/about/">About</a></header><div class="tick">{TICKER.get('html', '')}</div>
<main>{body}</main>{kw.get('scripts', '')}</body></html>"""


TICKER = {}


def financials(c):
    rng = stream("fin", c.id)
    base = c.shares * c.base_price * rng.uniform(0.05, 0.14)
    out = []
    for y in (409, 410, 411):
        rev = base * rng.uniform(0.85, 1.25) * (1 + (y - 409) * 0.08)
        margin = rng.uniform(-0.04, 0.22)
        out.append((y, rev, rev * margin))
    return out


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    days = trading_days()
    last, prev = days[-1], days[-2]
    listed = [c for c in COMPANIES if c.ticker]
    tick = []
    for c in listed:
        a, b = PRICES[c.ticker][prev], PRICES[c.ticker][last]
        ch = (b / a - 1) * 100
        tick.append(f"{c.ticker} {b:.2f} <span class='{'up' if ch >= 0 else 'down'}'>{ch:+.2f}%</span>")
    TICKER["html"] = " &nbsp;&middot;&nbsp; ".join(tick)
    rows = []
    for c in listed:
        s = PRICES[c.ticker]
        b, a = s[last], s[prev]
        first = s[days[0]]
        ch = (b / a - 1) * 100
        ytd = (b / first - 1) * 100
        rows.append([f"<a href='/listing/{c.ticker}/'>{c.ticker}</a>", esc(c.name), tally_to_str(b), f"{b:.2f}",
                     f"<span class='{'up' if ch >= 0 else 'down'}'>{ch:+.2f}%</span>",
                     f"<span class='{'up' if ytd >= 0 else 'down'}'>{ytd:+.1f}%</span>",
                     f"{b * c.shares / 1e6:,.0f}m"])
        # listing page
        vals = [s[d] for d in days]
        chart = svg.line_chart(vals, 900, 320, "#1d4ed8", [f"{d.day} {d.month_name[:3]}" for d in days],
                               f"{c.name} ({c.ticker}), 412, tallies", "{:.2f}")
        site.write(f"/img/{c.ticker}.svg", chart)
        fin = financials(c)
        fin_rows = [[str(y), f"{r / 1e6:,.1f}m", f"{p / 1e6:,.1f}m"] for y, r, p in fin]
        anns = [x for x in ANNOUNCEMENTS if x[0] == c.ticker]
        ceo = NOTABLE[c.ceo].full if c.ceo in NOTABLE else c.ceo
        hi_d = max(days, key=lambda d: s[d])
        lo_d = min(days, key=lambda d: s[d])
        site.page(f"/listing/{c.ticker}/", f"{c.name} ({c.ticker})", f"""
<div class="panel"><h1>{esc(c.name)} <small>{c.ticker}</small></h1><div class="big">{tally_to_str(b)}
<span class='{'up' if ch >= 0 else 'down'}' style="font-size:16px">{ch:+.2f}% today</span></div>
<p>Close of {last.weekday} {last.salt()}. Year high {s[hi_d]:.2f} ({hi_d.salt()}), low {s[lo_d]:.2f} ({lo_d.salt()}).</p>
<img class="chart" src="/img/{c.ticker}.svg" alt="Price chart for {c.ticker}"></div>
<div class="panel"><h2>Company</h2><table><tr><td>Sector</td><td>{esc(c.industry)}</td></tr>
<tr><td>Home</td><td>{esc(c.city)}, {esc(NATIONS[c.nation].short)}</td></tr><tr><td>Chief executive</td><td>{esc(ceo)}</td></tr>
<tr><td>Shares in issue</td><td>{c.shares:,}</td></tr><tr><td>Market value</td><td>{b * c.shares / 1e6:,.0f} million tallies</td></tr>
<tr><td>Registered number</td><td>{esc(c.registry_no)}</td></tr></table>
{f'<p><a href="{links.company_registry(c)}">Concordat Registry record</a></p>' if c.nation == "VEY" else ""}</div>
<div class="panel"><h2>Results (millions of tallies)</h2>{kit.table(["Year", "Revenue", "Profit"], fin_rows)}</div>
<div class="panel"><h2>Announcements</h2>{"".join(f"<p><b>{d.salt()}</b> {esc(t)}: {esc(x)}</p>" for _, d, t, x in anns) or "<p>None this year.</p>"}</div>
<div class="panel"><h2>Daily prices</h2><p><a href="/listing/{c.ticker}/prices/">Full daily price table for 412</a></p></div>""")
        prow = [[f"{d.weekday_abbr} {d.salt()}", f"{s[d]:.2f}", tally_to_str(s[d])] for d in reversed(days)]
        site.page(f"/listing/{c.ticker}/prices/", f"{c.ticker} daily prices", f"<h1>{esc(c.name)}: daily closing prices, 412</h1>"
                  f"<p><a href='/listing/{c.ticker}/'>&laquo; {c.ticker}</a>. The Exchange is closed on Stilldays.</p>"
                  + kit.table(["Date", "Close (tallies)", "Close (t/b)"], prow))
    site.page("/listings/", "Listings", "<h1>Listed companies</h1>" + kit.table(
        ["Ticker", "Company", "Close", "Decimal", "Day", "Year", "Value (t)"], rows, raw=True, sortable=True) + kit.SORTABLE_JS)
    # index: sum of market caps normalised to 1000 at year start
    caps = {d: sum(PRICES[c.ticker][d] * c.shares for c in listed) for d in days}
    idx = {d: 1000 * caps[d] / caps[days[0]] for d in days}
    site.write("/img/b20.svg", svg.line_chart([idx[d] for d in days], 900, 320, "#f59e0b",
                                              [f"{d.day} {d.month_name[:3]}" for d in days], "B20 index, 412", "{:.0f}"))
    site.page("/index/", "B20 index", f"""<h1>B20 index</h1><p class="big">{idx[last]:.1f}</p>
<p>The B20 tracks the value of all companies listed on the Brineholt Exchange, set to 1,000 at the first trading day of 412.</p>
<img class="chart" src="/img/b20.svg" alt="Chart of the B20 index in 412">""")
    site.page("/announcements/", "Announcements", "<h1>Company announcements</h1>" + kit.table(
        ["Date", "Company", "Title", "Detail"],
        [[d.salt(), f"<a href='/listing/{t}/'>{t}</a>", esc(h), esc(x)] for t, d, h, x in sorted(ANNOUNCEMENTS, key=lambda a: a[1], reverse=True)],
        raw=True))
    site.page("/about/", "About", """<h1>About the Exchange</h1><p>The Brineholt Exchange has traded shares since 211 in the
old Salt Hall. Prices are quoted in tallies and bits (twelve bits to the tally). Trading runs Anvilday to Hearthday, 9:00 to
15:30 Brineholt time. The Exchange is shut on Stilldays and Hollowdays.</p><p>Companies from any nation may list. Veylish
companies must also file with the Concordat Registry.</p>""")
    site.page("/", "Market summary", f"""<h1>Market summary, {last.weekday} {last.salt()}</h1>
<p class="big">B20 {idx[last]:.1f}</p>{kit.table(["Ticker", "Company", "Close", "Decimal", "Day", "Year", "Value (t)"], rows, raw=True)}""")
    site.fact("exchange-gldw-stake-sold", "On what date did Sallow Fen Holdings sell its 12% stake in Gildmere Works, "
              "according to the Exchange announcement?", "18 Blaze 412", "/announcements/")
    site.fact("exchange-vntl-close", f"What was Vantle's closing share price on {last.salt()}?",
              f"{PRICES['VNTL'][last]:.2f} tallies ({tally_to_str(PRICES['VNTL'][last])})", "/listing/VNTL/")
