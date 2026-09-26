"""bellows.ves: Bellows Records, an independent label on the Rope Walk."""
from ..engine import kit, svg
from ..engine.domains import url
from ..engine.web import esc
from ..world.calendar import TODAY
from ..world.culture import ARTISTS, ALBUMS, ARTIST, TOUR_412

CSS = """
body{margin:0;background:#fef6e4;color:#172c66;font:16px/1.5 'Courier New',monospace}
header{background:#f582ae;padding:18px 28px;display:flex;align-items:center;gap:26px;flex-wrap:wrap}header a{color:#172c66;text-decoration:none;font-weight:bold}
.logo{font:900 30px 'Arial Black',sans-serif;letter-spacing:-1px}
main{max-width:980px;margin:0 auto;padding:24px}a{color:#8bd3dd;color:#b5446e}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:20px}.grid img{width:100%;border:3px solid #172c66}
table{border-collapse:collapse;width:100%}td,th{padding:5px;border-bottom:2px dotted #172c66;text-align:left}
.cancel{text-decoration:line-through;color:#999}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} :: Bellows Records</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">BELLOWS</a><a href="/artists/">Artists</a><a href="/releases/">Releases</a><a href="/tour/">Tour dates</a>
<a href="/news/">News</a></header><main>{body}</main>{kw.get('scripts', '')}</body></html>"""


def sleeve(al):
    pal = svg.palette(al.id)
    p = [f'<rect width="300" height="300" fill="{pal[0]}"/>']
    for i in range(6):
        p.append(f'<circle cx="150" cy="150" r="{140 - i * 22}" fill="none" stroke="{pal[(i % 4) + 1]}" stroke-width="10"/>')
    p.append('<rect x="0" y="236" width="300" height="64" fill="#000" opacity=".5"/>')
    p.append(svg.text(150, 262, al.title, 20, "#fff", "middle", "bold"))
    p.append(svg.text(150, 286, ARTIST[al.artist].name, 13, "#fff", "middle"))
    return svg.wrap(300, 300, "".join(p))


def mmss(s):
    return f"{s // 60}:{s % 60:02d}"


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    released = [al for al in ALBUMS if al.release <= TODAY]
    for al in ALBUMS:
        site.write(f"/img/{al.id}.svg", sleeve(al))
    for al in released:
        total = sum(t for _, t in al.tracks)
        site.page(f"/releases/{al.id}/", al.title, f"""<div class="grid" style="grid-template-columns:300px 1fr"><img src="/img/{al.id}.svg" alt="Sleeve of {esc(al.title)}">
<div><h1>{esc(al.title)}</h1><p>by <a href="/artists/{al.artist}/">{esc(ARTIST[al.artist].name)}</a></p><p>Released {al.release.long()} &middot; {al.catalog}</p>
<p>Formats: {esc(', '.join(al.fmt))}</p><p><a href="{url('bazaar', '/search/?q=' + al.title.replace(' ', '+'))}">Buy on Bazaar</a></p></div></div>
<h2>Tracks</h2>{kit.table(["#", "Title", "Length"], [[str(i + 1), t, mmss(s)] for i, (t, s) in enumerate(al.tracks)])}
<p>Total running time {mmss(total)}.</p>""")
    for a in ARTISTS:
        als = [al for al in released if al.artist == a.id]
        site.page(f"/artists/{a.id}/", a.name, f"""<h1>{esc(a.name)}</h1><p>{esc(a.bio)}</p><p>From {esc(a.city)}. Genre: {esc(a.genre)}.
Formed {a.formed}.</p><p>{esc(', '.join(a.members))}</p><div class="grid">{"".join(f'<a href="/releases/{al.id}/"><img src="/img/{al.id}.svg" alt=""><br>{esc(al.title)} ({al.release.year})</a>' for al in als)}</div>
{"<p><a href='/tour/'>Ninth Bridge tour dates</a></p>" if a.id == "nell-hedgecote" else ""}""")
    site.page("/artists/", "Artists", "<h1>Artists</h1><ul>" + "".join(f'<li><a href="/artists/{a.id}/">{esc(a.name)}</a> ({esc(a.genre)})</li>' for a in ARTISTS) + "</ul>")
    site.page("/releases/", "Releases", "<h1>Releases</h1><div class='grid'>" + "".join(
        f'<a href="/releases/{al.id}/"><img src="/img/{al.id}.svg" alt=""><br>{esc(al.title)}</a>' for al in sorted(released, key=lambda a: a.release, reverse=True)) + "</div>")
    rows = []
    for d, city, venue in TOUR_412:
        cancelled = "CANCELLED" in venue
        rows.append([f'<span class="{"cancel" if cancelled else ""}">{d.long()}</span>', esc(city), esc(venue),
                     "played" if d < TODAY else ("cancelled" if cancelled else "tickets")])
    site.page("/tour/", "Tour dates", "<h1>Nell Hedgecote: Ninth Bridge tour</h1>" + kit.table(["Date", "Town", "Venue", ""], rows, raw=True)
              + "<p>The Saltspire date will not be rescheduled.</p>")
    site.page("/news/", "News", """<h1>News</h1><h3>Saltspire date cancelled</h3><p>Because of Storm Petrel, Nell's show on Spire Green
(10 Gale) is cancelled. Refunds from the point of sale.</p><h3>Ninth Bridge is out</h3><p>12 Crest 412. The first single, 'Wardens' Bridge',
runs 4 minutes 23 seconds.</p><h3>Sprocket &amp; Wick: Weave Sickness</h3><p>Out 30 Loam 412.</p>""")
    site.page("/", "Bellows Records", "<h1>Independent records from the Rope Walk.</h1><div class='grid'>" + "".join(
        f'<a href="/releases/{al.id}/"><img src="/img/{al.id}.svg" alt=""><br>{esc(al.title)}</a>' for al in sorted(released, key=lambda a: a.release, reverse=True)[:4]) + "</div>")
    nb = next(al for al in ALBUMS if al.title == "Ninth Bridge")
    site.fact("bellows-ninth-bridge-length", "What is the total running time of Nell Hedgecote's 'Ninth Bridge'?",
              mmss(sum(t for _, t in nb.tracks)), f"/releases/{nb.id}/")
