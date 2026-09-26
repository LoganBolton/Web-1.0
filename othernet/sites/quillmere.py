"""quillmere.ves: Quillmere Press, publishers and booksellers."""
from ..engine import kit, svg, links
from ..engine.rng import slug, stream
from ..engine.web import esc
from ..world.calendar import ADate, TODAY
from ..world.culture import BOOKS

EVENTS = [
    (ADate(412, 9, 12), "Morwen Reefley in conversation", "Brineholt Playhouse", "Before the opening of the stage "
     "'Nine Fathoms Down'. Tickets 6 tallies."),
    (ADate(412, 8, 25), "Wenna Larkfield: Walking the Sallow", "Quillmere Bookshop, Ostmere", "A talk and signing. Free."),
    (ADate(412, 9, 2), "Mireille Solande: What comes after Weft?", "Lanternport University, Loom Hall", "A lecture."),
    (ADate(412, 7, 10), "Poetry on the Nine Bridges", "Wardens' Bridge, Ostmere", "Readings of Hollis Thornby at dusk."),
]

CSS = """
body{margin:0;background:#fffdf7;color:#2b2118;font:17px/1.6 'Baskerville','Libre Baskerville',Georgia,serif}
header{border-bottom:1px solid #d6c8a8;padding:22px 30px 10px;text-align:center}
header a.logo{font-size:34px;color:#2b2118;text-decoration:none;font-style:italic}
header nav{margin-top:8px;font-size:14px;letter-spacing:2px;text-transform:uppercase}header nav a{color:#7a5c2e;margin:0 12px;text-decoration:none}
main{max-width:960px;margin:0 auto;padding:26px}
a{color:#7a5c2e}.books{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:22px}
.book img{width:100%;height:auto;box-shadow:2px 3px 8px rgba(0,0,0,.2)}.book a{text-decoration:none;color:#2b2118}
.detail{display:grid;grid-template-columns:260px 1fr;gap:30px}.detail img{width:100%}
table{border-collapse:collapse}td{padding:4px 12px 4px 0}
footer{border-top:1px solid #d6c8a8;text-align:center;font-size:13px;padding:24px;color:#7a5c2e}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} &mdash; Quillmere Press</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">Quillmere Press</a><nav><a href="/catalogue/">Catalogue</a><a href="/authors/">Authors</a>
<a href="/events/">Events</a><a href="/submissions/">Submissions</a><a href="/shop/">The Bookshop</a></nav></header>
<main>{body}</main><footer>Quillmere Press, Nine Bridges Lane, Ostmere. Publishers and booksellers since 244 CR.</footer>{kw.get('scripts', '')}</body></html>"""


def cover(b):
    rng = stream("cover", b.id)
    pal = svg.palette(b.id)
    bg, fg = pal[0], pal[-1] if pal[-1] != pal[0] else "#fff"
    words = b.title.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) > 14:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    p = [f'<rect width="200" height="300" fill="{bg}"/>', f'<rect x="12" y="12" width="176" height="276" fill="none" stroke="{fg}" stroke-width="2"/>']
    shape = rng.randrange(3)
    if shape == 0:
        p.append(f'<circle cx="100" cy="190" r="46" fill="{pal[2]}"/>')
    elif shape == 1:
        p.append(f'<path d="M20,240 Q100,{rng.randint(140, 200)} 180,240 Z" fill="{pal[2]}"/>')
    else:
        p.append(f'<rect x="60" y="150" width="80" height="80" fill="{pal[2]}" transform="rotate(12 100 190)"/>')
    for i, ln in enumerate(lines[:4]):
        p.append(svg.text(100, 50 + i * 24, ln, 20, fg, "middle", "bold", "Georgia, serif"))
    p.append(svg.text(100, 272, b.author, 13, fg, "middle", "normal", "Georgia, serif"))
    return svg.wrap(200, 300, "".join(p))


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    ours = [b for b in BOOKS if b.publisher == "Quillmere Press"]
    for b in BOOKS:
        site.write(f"/img/covers/{b.id}.svg", cover(b))
    for b in ours:
        others = [o for o in ours if o.author == b.author and o is not b]
        site.page(f"/books/{b.id}.html", b.title, f"""<div class="detail"><div><img src="/img/covers/{b.id}.svg" alt="Cover of {esc(b.title)}"></div>
<div><h1>{esc(b.title)}</h1><p>by <a href="/authors/{slug(b.author)}/">{esc(b.author)}</a></p><p>{esc(b.blurb)}</p>
<table><tr><td>First published</td><td>{b.year} CR</td></tr><tr><td>Pages</td><td>{b.pages}</td></tr>
<tr><td>QN</td><td>{b.qn}</td></tr><tr><td>Genre</td><td>{b.genre}</td></tr><tr><td>Price</td><td>{b.price_cr:.2f} cr</td></tr></table>
<p><button onclick="this.textContent='Added. Collect from the Bookshop or post it (45 pennets per weight).'">Buy from the Bookshop</button></p>
{"<h3>Also by " + esc(b.author) + "</h3><ul>" + "".join(f'<li><a href="/books/{o.id}.html">{esc(o.title)}</a></li>' for o in others) + "</ul>" if others else ""}</div></div>""")
    authors = sorted({b.author for b in ours})
    for a in authors:
        mine = [b for b in ours if b.author == a]
        site.page(f"/authors/{slug(a)}/", a, f"<h1>{esc(a)}</h1><div class='books'>" + "".join(
            f'<div class="book"><a href="/books/{b.id}.html"><img src="/img/covers/{b.id}.svg" alt=""><br>{esc(b.title)}</a> ({b.year})</div>' for b in mine)
                  + "</div>" + (f"<p>More about {esc(a)} in <a href='{links.folio(a)}'>the Commonplace</a>.</p>"
                                if a in ("Morwen Reefley", "Hollis Thornby", "Rosamund Tallwick") else ""))
    site.page("/authors/", "Authors", "<h1>Our authors</h1><ul>" + "".join(
        f'<li><a href="/authors/{slug(a)}/">{esc(a)}</a> ({sum(1 for b in ours if b.author == a)})</li>' for a in authors) + "</ul>")
    by_genre = {}
    for b in ours:
        by_genre.setdefault(b.genre, []).append(b)
    genre_nav = " &middot; ".join(f'<a href="/catalogue/{g}/">{g}</a>' for g in sorted(by_genre))
    for g, items in by_genre.items():
        site.page(f"/catalogue/{g}/", g.title(), f"<h1>{g.title()}</h1><p>{genre_nav}</p><div class='books'>" + "".join(
            f'<div class="book"><a href="/books/{b.id}.html"><img src="/img/covers/{b.id}.svg" alt=""><br>{esc(b.title)}</a><br><small>{esc(b.author)}</small></div>'
            for b in sorted(items, key=lambda b: -b.year)) + "</div>")
    site.page("/catalogue/", "Catalogue", f"<h1>Catalogue</h1><p>{len(ours)} titles in print.</p><p>{genre_nav}</p>" + kit.table(
        ["Title", "Author", "Year", "QN", "Price"],
        [[f'<a href="/books/{b.id}.html">{esc(b.title)}</a>', esc(b.author), str(b.year), b.qn, f"{b.price_cr:.2f} cr"]
         for b in sorted(ours, key=lambda b: b.title)], raw=True, sortable=True) + kit.SORTABLE_JS)
    site.page("/events/", "Events", "<h1>Events</h1>" + "".join(
        f"<h3>{esc(t)}</h3><p>{d.full()} &middot; {esc(pl)}</p><p>{esc(x)}</p>{'<p><i>This event has passed.</i></p>' if d < TODAY else ''}"
        for d, t, pl, x in sorted(EVENTS)))
    site.page("/submissions/", "Submissions", """<h1>Submissions</h1><p>We read unsolicited manuscripts twice a year,
during Loam and Sheaf. Send the first three chapters by loom-letter to submissions@quillmere.ves with a one-page summary.</p>
<p>We do not publish poetry collections by new authors, cookery, or anything about Pith being artificial.</p>""")
    site.page("/shop/", "The Bookshop", """<h1>The Bookshop</h1><p>Our shop on Nine Bridges Lane, Ostmere, is open
Anvilday to Hearthday, 9:00 to 18:00, and Stillday from 12:00 to 16:00. We stock books from every publisher, not only our own.</p>
<p>Postage is 45 pennets per weight within the Concordat.</p>""")
    new = sorted(ours, key=lambda b: -b.year)[:8]
    site.page("/", "Quillmere Press", "<h1 style='font-weight:normal'>New and notable</h1><div class='books'>" + "".join(
        f'<div class="book"><a href="/books/{b.id}.html"><img src="/img/covers/{b.id}.svg" alt=""><br>{esc(b.title)}</a><br><small>{esc(b.author)}</small></div>'
        for b in new) + "</div>")
    salt = next(b for b in BOOKS if b.title == "The Salt Ledger")
    site.fact("quillmere-salt-ledger-price", "What does Quillmere Press charge for The Salt Ledger?",
              f"{salt.price_cr:.2f} cr", f"/books/{salt.id}.html")
