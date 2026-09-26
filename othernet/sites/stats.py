"""stats.pel: the Pellucid Statistical Office. Datasets with tables, charts, and CSV downloads."""
from ..engine import kit, svg
from ..engine.rng import stream
from ..engine.web import esc
from ..world.calendar import MONTHS, TODAY
from ..world.geo import cities_of

CSS = """
*{box-sizing:border-box}body{margin:0;font:15px/1.55 'Segoe UI',Roboto,sans-serif;background:#fff;color:#1f2937}
header{border-top:6px solid #0f766e;padding:16px 28px;display:flex;align-items:center;gap:26px;border-bottom:1px solid #e5e7eb}
header a{color:#0f766e;text-decoration:none}.logo{font-weight:700;font-size:20px}
main{max-width:1000px;margin:0 auto;padding:22px}a{color:#0f766e}
table{border-collapse:collapse;width:100%}td,th{padding:6px 8px;border-bottom:1px solid #e5e7eb;text-align:right}td:first-child,th:first-child{text-align:left}
th{background:#f0fdfa}.chart{width:100%;height:auto;border:1px solid #e5e7eb}.meta{color:#6b7280;font-size:13px}
.ds{border:1px solid #e5e7eb;border-radius:8px;padding:14px;margin:12px 0}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Pellucid Statistical Office</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">Pellucid Statistical Office</a><a href="/datasets/">Datasets</a><a href="/releases/">Release calendar</a>
<a href="/about/">About</a></header><main>{body}</main>{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("stats")
    islands = [c.name for c in cities_of("PEL")]
    datasets = []
    # Population by island, 402-411
    years = list(range(402, 412))
    pop = {}
    for c in cities_of("PEL"):
        v = c.population / (1.012 ** 10)
        pop[c.name] = []
        for y in years:
            v *= rng.uniform(1.004, 1.02)
            pop[c.name].append(int(v))
        pop[c.name][-1] = c.population
    datasets.append(("population-by-island", "Population by island", "People living on each island at the Charter census count, "
                     "402–411.", ["Island"] + [str(y) for y in years], [[i] + [f"{x:,}" for x in pop[i]] for i in islands],
                     svg.bar_chart([(i[:10], pop[i][-1] / 1000) for i in islands], 640, 240, "#0f766e", "Population in 411 (thousands)", "{:.0f}")))
    # Visitor arrivals by month 412
    arr = {}
    for src in ("Veyl", "Saltmarch", "Kethren Holds", "Oddavar"):
        base = {"Veyl": 42000, "Saltmarch": 18000, "Kethren Holds": 3000, "Oddavar": 60}[src]
        arr[src] = [int(base * (1 + 0.5 * (m in (5, 6, 7))) * rng.uniform(0.85, 1.15)) for m in range(1, TODAY.month)]
    arr["Veyl"][5] = int(arr["Veyl"][5] * 1.18)  # the Skylark effect in Crest
    datasets.append(("visitor-arrivals-412", "Visitor arrivals, 412", "Arrivals by sea and air, by home nation. Gale figures "
                     "are published on 5 Mire.", ["From"] + [MONTHS[m - 1] for m in range(1, TODAY.month)],
                     [[k] + [f"{x:,}" for x in v] for k, v in arr.items()],
                     svg.line_chart([sum(arr[k][i] for k in arr) for i in range(TODAY.month - 1)], 640, 240, "#0f766e",
                                    [MONTHS[m - 1][:3] for m in range(1, TODAY.month)], "All arrivals by month, 412", "{:,.0f}")))
    # Pearl harvest
    pearls = [(y, int(rng.uniform(80, 140) * 1000)) for y in range(400, 412)]
    pearls[-1] = (411, 71_400)
    datasets.append(("pearl-harvest", "Pearl harvest", "Pearls landed at Marrowby, by weight in weights (wt). 411 was the "
                     "lowest since records began, after the warm water of Blaze.", ["Year", "Weights landed"],
                     [[str(y), f"{v:,}"] for y, v in pearls],
                     svg.bar_chart([(str(y), v / 1000) for y, v in pearls], 640, 240, "#9d174d", "Pearls landed (thousand wt)", "{:.0f}")))
    # Open Loom library access
    libs = [(i, rng.randint(2, 30), rng.randint(1, 12)) for i in islands]
    datasets.append(("public-looms", "Public looms in libraries", "Public looms in libraries, before and after the Open Loom "
                     "Act (passed 30 Loam 412).", ["Island", "Libraries", "Public looms in Rime 412", "Public looms in Gale 412"],
                     [[i, str(n), str(b), str(n)] for i, n, b in libs], None))
    # Exam results
    subjects = ["Numerics", "Pellish", "Veylish", "Natural Philosophy", "Loomcraft", "Navigation", "History"]
    datasets.append(("collegiate-exams-411", "Collegiate entrance exams, 411", "Share of candidates passing each paper.",
                     ["Paper", "Candidates", "Passed (%)"], [[s, f"{rng.randint(800, 9000):,}", f"{rng.uniform(48, 91):.1f}"] for s in subjects], None))
    # Weather at Vanehaven tower: wind
    datasets.append(("vanehaven-wind", "Wind at Vanehaven Weather Tower", "Mean wind speed by month, leagues an hour, 411.",
                     ["Month", "Mean wind", "Strongest gust"],
                     [[m, f"{rng.uniform(4, 11):.1f}", f"{rng.uniform(12, 24):.1f}"] for m in MONTHS], None))
    for sid, title, desc, headers, rows, chart in datasets:
        chart_html = ""
        if chart:
            site.write(f"/img/{sid}.svg", chart)
            chart_html = f'<img class="chart" src="/img/{sid}.svg" alt="Chart: {esc(title)}">'
        csv = "\n".join(",".join(f'"{x}"' if "," in x else x for x in r) for r in [headers] + rows)
        site.write(f"/data/{sid}.csv", csv)
        site.page(f"/datasets/{sid}/", title, f"""<p><a href="/datasets/">&laquo; All datasets</a></p><h1>{esc(title)}</h1>
<p>{esc(desc)}</p><p class="meta">Dataset {sid} &middot; <a href="/data/{sid}.csv">Download CSV</a></p>{chart_html}
{kit.table(headers, rows)}""")
    site.page("/datasets/", "Datasets", "<h1>Datasets</h1>" + "".join(
        f'<div class="ds"><h3><a href="/datasets/{sid}/">{esc(t)}</a></h3><p>{esc(d)}</p></div>' for sid, t, d, *_ in datasets))
    site.page("/releases/", "Release calendar", "<h1>Release calendar</h1>" + kit.table(
        ["Date", "Release"], [["5 Mire 412", "Visitor arrivals, Gale"], ["20 Mire 412", "Prices in the Isles, third quarter"],
                              ["1 Dusk 412", "Pearl harvest, provisional"], ["Hollowday 3, 412", "Population estimate for 412"]]))
    site.page("/about/", "About", "<p>The Pellucid Statistical Office publishes numbers about the Isles, free to everyone, as the "
              "Charter of Colleges requires. All our data can be downloaded as CSV.</p>")
    site.page("/", "Pellucid Statistical Office", "<h1>Numbers about the Isles, free to all</h1><ul>" + "".join(
        f'<li><a href="/datasets/{sid}/">{esc(t)}</a></li>' for sid, t, *_ in datasets) + "</ul>")
    site.fact("stats-pearls-411", "How many weights of pearls were landed at Marrowby in 411?", "71,400",
              "/datasets/pearl-harvest/")
