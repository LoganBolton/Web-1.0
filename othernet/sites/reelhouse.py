"""reelhouse.ves: the film database. Titles, people, ratings, box office."""
from ..engine import kit, svg
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.calendar import TODAY
from ..world.culture import FILMS
from ..world.people import generate_population

CSS = """
*{box-sizing:border-box}body{margin:0;background:#121212;color:#e5e5e5;font:14px/1.5 Roboto,Arial,sans-serif}
header{background:#000;padding:10px 20px;display:flex;align-items:center;gap:20px}header a{color:#fff;text-decoration:none}
.logo{background:#f5c518;color:#000!important;font:900 20px Impact,sans-serif;padding:2px 8px;border-radius:3px}
header input{padding:7px;width:300px;border-radius:4px;border:0}
main{max-width:1100px;margin:0 auto;padding:20px}a{color:#5799ef}
.title{display:grid;grid-template-columns:220px 1fr;gap:24px}.title img{width:220px}
.rating{font-size:22px}.rating b{color:#f5c518}
table{border-collapse:collapse;width:100%}td,th{padding:6px;border-bottom:1px solid #2a2a2a;text-align:left}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:14px}.grid img{width:100%}
.muted{color:#999}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - Reelhouse</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">REELHOUSE</a><form action="/find/"><input name="q" placeholder="Search films and people"></form>
<a href="/top/">Top 50</a><a href="/box-office/">Box office</a><a href="/years/">By year</a></header>
<main>{body}</main><footer style="text-align:center;color:#666;padding:20px;font-size:12px">Reelhouse is a Bazaar Holdings company.</footer>{kw.get('scripts', '')}</body></html>"""


def poster(f):
    pal = svg.palette(f.id)
    inner = svg.landscape(f.id, ["hills", "sea", "night", "city", "moor"][len(f.title) % 5], 200, 300)
    body = inner[inner.index(">") + 1:-6]
    p = [body, f'<rect x="0" y="200" width="200" height="100" fill="{pal[0]}" opacity=".85"/>',
         svg.text(100, 236, f.title[:22], 15, "#fff", "middle", "bold", "Georgia, serif"),
         svg.text(100, 256, f.title[22:44], 15, "#fff", "middle", "bold", "Georgia, serif"),
         svg.text(100, 284, f"a film by {f.director}", 10, "#eee", "middle")]
    return svg.wrap(200, 300, "".join(p))


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    pop = generate_population()
    people = {}
    for f in FILMS:
        people.setdefault(f.director, {"dir": [], "act": []})["dir"].append(f)
        for a, role in f.cast:
            people.setdefault(a, {"dir": [], "act": []})["act"].append((f, role))
    for f in FILMS:
        site.write(f"/img/{f.id}.svg", poster(f))
        rng = stream("reel", f.id)
        revs = []
        for i in range(rng.randint(1, 6)):
            who = rng.choice(pop)
            s = max(1, min(10, round(rng.gauss(f.rating, 1.6))))
            revs.append((who.handle, s, rng.choice(["A slow start, then it grips you.", "The score is the real star.",
                                                    "Too long by half an hour.", "I cried on the ferry home.",
                                                    "Beautiful to look at, hollow inside.", "Best film of its year.",
                                                    "The ending made no sense.", "Watch it for the harbour scenes."])))
        cast = "".join(f'<tr><td><a href="/name/{slug(a)}/">{esc(a)}</a></td><td class="muted">{esc(r)}</td></tr>' for a, r in f.cast)
        site.page(f"/title/{f.id}/", f"{f.title} ({f.year})", f"""<div class="title"><img src="/img/{f.id}.svg" alt="Poster for {esc(f.title)}">
<div><h1>{esc(f.title)} <span class="muted">({f.year})</span></h1><p class="muted">{f.genre} &middot; {f.runtime} min &middot; {esc(f.studio)}</p>
<div class="rating"><b>★ {f.rating}</b>/10 <span class="muted" style="font-size:14px">from {f.votes:,} votes</span></div>
<p>{esc(f.synopsis)}</p><p>Directed by <a href="/name/{slug(f.director)}/">{esc(f.director)}</a></p>
<p>Released {f.release.long() if f.release else f.year}. Box office: {f.box_office:,} cr.</p></div></div>
<h2>Cast</h2><table>{cast}</table>
{"<h2>Awards</h2><ul>" + "".join(f"<li>{esc(a)}</li>" for a in f.awards) + "</ul>" if f.awards else ""}
{"<h2>Trivia</h2><ul>" + "".join(f"<li>{esc(t)}</li>" for t in f.trivia) + "</ul>" if f.trivia else ""}
<h2>Member reviews</h2>{"".join(f'<p><b>{esc(h)}</b> <span style="color:#f5c518">{s}/10</span><br>{esc(t)}</p>' for h, s, t in revs)}""")
    for name, d in people.items():
        rows = [[f'<a href="/title/{f.id}/">{esc(f.title)}</a>', str(f.year), "director"] for f in d["dir"]] + \
               [[f'<a href="/title/{f.id}/">{esc(f.title)}</a>', str(f.year), esc(role)] for f, role in d["act"]]
        rows.sort(key=lambda r: r[1], reverse=True)
        site.page(f"/name/{slug(name)}/", name, f"<h1>{esc(name)}</h1><p class='muted'>{len(rows)} credits</p>" +
                  kit.table(["Title", "Year", "Credit"], rows, raw=True))
    top = sorted([f for f in FILMS if f.votes >= 1000], key=lambda f: -f.rating)[:50]
    site.page("/top/", "Top 50", "<h1>Top 50 films</h1><p class='muted'>Films with at least 1,000 votes.</p>" + kit.table(
        ["#", "Title", "Year", "Rating", "Votes"], [[str(i + 1), f'<a href="/title/{f.id}/">{esc(f.title)}</a>', str(f.year), str(f.rating), f"{f.votes:,}"]
                                                  for i, f in enumerate(top)], raw=True))
    years = sorted({f.year for f in FILMS}, reverse=True)
    for y in years:
        fs = sorted([f for f in FILMS if f.year == y], key=lambda f: -f.box_office)
        site.page(f"/years/{y}/", f"Films of {y}", f"<h1>Films of {y}</h1><div class='grid'>" + "".join(
            f'<div><a href="/title/{f.id}/"><img src="/img/{f.id}.svg" alt=""><br>{esc(f.title)}</a></div>' for f in fs) + "</div>")
    site.page("/years/", "By year", "<h1>By year</h1><p>" + " ".join(f'<a href="/years/{y}/">{y}</a>' for y in years) + "</p>")
    bo = sorted(FILMS, key=lambda f: -f.box_office)[:30]
    site.page("/box-office/", "Box office", "<h1>All-time box office</h1>" + kit.table(
        ["#", "Title", "Year", "Takings (cr)"], [[str(i + 1), f'<a href="/title/{f.id}/">{esc(f.title)}</a>', str(f.year), f"{f.box_office:,}"]
                                                for i, f in enumerate(bo)], raw=True))
    site.json("/data/index.json", [{"t": f.title, "u": f"/title/{f.id}/", "y": f.year} for f in FILMS] +
              [{"t": n, "u": f"/name/{slug(n)}/", "y": ""} for n in people])
    site.page("/find/", "Search", "<h1 id='h'>Search</h1><ul id='r'></ul>", index=False, scripts="""<script>
var q=(new URLSearchParams(location.search).get('q')||'').toLowerCase();fetch('/data/index.json').then(r=>r.json()).then(function(I){
var h=I.filter(x=>x.t.toLowerCase().indexOf(q)>=0);document.getElementById('h').textContent=h.length+' results for "'+q+'"';
document.getElementById('r').innerHTML=h.map(x=>'<li><a href="'+x.u+'">'+x.t+'</a> '+(x.y?'('+x.y+')':'<span class="muted">person</span>')+'</li>').join('');});</script>""")
    recent = sorted([f for f in FILMS if f.release and f.release <= TODAY], key=lambda f: f.release, reverse=True)[:10]
    site.page("/", "Reelhouse", "<h1>Recently released</h1><div class='grid'>" + "".join(
        f'<div><a href="/title/{f.id}/"><img src="/img/{f.id}.svg" alt=""><br>{esc(f.title)}</a><br><span class="muted">★ {f.rating}</span></div>' for f in recent) + "</div>")
    lamp = next(f for f in FILMS if f.id == "the-lampwright")
    site.fact("reelhouse-lampwright-runtime", "How long is 'The Lampwright'?", f"{lamp.runtime} minutes", "/title/the-lampwright/")
