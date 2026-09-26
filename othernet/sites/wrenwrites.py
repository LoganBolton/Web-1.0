"""wrenwrites.fol: Wren Writes, Wenna Larkfield's blog of walks, ferries, and small towns."""
from ..engine import kit, svg
from ..engine.domains import url
from ..engine.rings import widget
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.calendar import ADate, TODAY, MONTHS

POSTS = [
    (ADate(411, 7, 2), "Sixty-one days along the Sallow", ["walks", "sallow"],
     ["I did it. From the springs under the Kethren Spine to the Glass Sea at Harthwick, sixty-one days on foot.",
      "The first week is all scree and goats. The Holds do not believe in handrails.",
      "Ostmere took three days, because I kept stopping on the Nine Bridges.",
      "The book of the walk comes out with Northmole Books this winter. It's called, imaginatively, Walking the Sallow."],
     ("hills", "SALLOW SPRINGS\n0 leagues")),
    (ADate(411, 10, 12), "The ferry that sings", ["ferries"],
     ["The Glass Maiden from Harthwick to Marrowby has a glass-floored lounge and a steward who sings the sailing times. "
      "It runs only on Anvildays, Loomdays and Hearthdays. Worth planning your week around."], ("sea", None)),
    (ADate(412, 2, 20), "Tarrow in the rain", ["towns", "tarrow"],
     ["Tarrow is a town of locks and grain and umbrellas. The canal smells of wet rope. I loved it.",
      "Found a signpost on the towpath that still gives the old Kethren leagues. Someone has painted over it in chalk."],
     ("hills", "TARROW 14 lg\nLOWMARSH 9 lg")),
    (ADate(412, 4, 9), "Where did everybody go?", ["weave", "lanthorn"],
     ["Since the Lamp update, this blog gets a third of its visitors. Lanthorn simply doesn't show it for anything any more.",
      "If you're reading this, you probably came through Hearthring, or the Lamplit Ring, or a link on someone else's page. Hello! Stay.",
      "I've added myself to the Lantern Desk queue. Wait time: 'up to one season'."], None),
    (ADate(412, 5, 16), "Viewing day at Hollowmarket", ["ostmere", "curiosities"],
     ["Spent a happy hour at the Hollowmarket viewing rooms in Gallowmead. Clocks and instruments sale.",
      "Lot 4471, 'a gilded pointer, maker unknown', caught my eye. Crescent at the tip. Stamped repair on the pivot: Q.C. 331. "
      "Q.C. for Quenby Clockworks? I told the desk. The next day it was withdrawn, and the day after the Courier said it was the "
      "stolen Pith hand. I'd like to think I helped."], ("city", "HOLLOWMARKET\nVIEWING TODAY")),
    (ADate(412, 5, 3), "Frostgate on opening day", ["walks", "kethren", "oddavar"],
     ["The gates of the Frostgate Wall open at dawn on 1 Blaze. I was there, freezing, with two hundred traders.",
      "The first Oddavari through was a woman with a sled of ice-salt blocks, each stamped with a flame. She would not be photographed.",
      "You cannot go north of the Wall without a pilgrim's number from the Synod, and the Synod does not answer loom-letters."],
     ("mountains", "FROSTGATE\nOPEN 1 BLAZE")),
    (ADate(412, 7, 5), "Harthwick's new light", ["harthwick", "lighthouses"],
     ["Harthwick Lighthouse changed its character on 1 Sheaf. It now flashes three times every twelve seconds.",
      "I sat on Lamp Hill with a stopwatch to check. Three, and twelve. The Commonplace still says two and nine."], ("sea", None)),
    (ADate(412, 8, 11), "After the storm", ["saltmarch", "storms"],
     ["Took the first ferry to Brineholt after Storm Petrel. The Stair funicular is shut, the Harbour Line reopens tomorrow, "
      "and the Northmole looks like something bit it.",
      "A tram driver told me the lost property office has 214 umbrellas and one cat."], ("sea", None)),
    (ADate(412, 8, 15), "Planning for the crossing", ["sky"],
     ["Where to watch Pith cross Ossa on 3 Mire? From Harthwick the crossing is full and starts at 21:20. I'll be on Lamp Hill again.",
      "Ossa Optics filters are sold out at Bazaar. The Observatory says it will hand some out on Observatory Hill."], ("night", None)),
]
FILLER_PLACES = ["Emberly", "Quenby", "Gorse Hollow", "Lowmarsh", "Silverrun", "Wendmoor", "Caddick Ford", "Gullhaven", "Corrack",
                 "Tidewell", "Shellcombe", "Coralstead", "Stonemeet", "Aldermoot"]


CSS = """
body{margin:0;background:#f4efe6;color:#3a3226;font:18px/1.7 'Iowan Old Style',Georgia,serif}
.wrap{max-width:720px;margin:0 auto;padding:30px 20px}
h1.site{font:italic 42px Georgia,serif;margin:0}h1.site a{color:#3a3226;text-decoration:none}.tag{color:#8a6d3b}
.post{border-bottom:1px dashed #c9b99a;padding:20px 0}.post h2 a{color:#3a3226}.date{color:#8a6d3b;font-size:14px}
a{color:#a0522d}img.photo{width:100%;border:6px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,.2)}
.side{font-size:15px;border-top:2px solid #3a3226;margin-top:30px;padding-top:10px}
.comment{background:#fffaf0;padding:8px 12px;margin:8px 0;font-size:15px}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} ~ Wren Writes</title><link rel="stylesheet" href="/style.css"></head><body><div class="wrap">
<h1 class="site"><a href="/">Wren Writes</a></h1><p class="tag">Walks, ferries, and small towns. By Wenna Larkfield.</p>
{body}<div class="side"><b>Elsewhere:</b> <a href="{url('spirekeeper')}">The Spire Log</a> &middot; <a href="{url('hearthandhob')}">Hearth &amp; Hob</a>
&middot; <a href="{url('inkling')}">Inkling</a> &middot; <a href="{url('chatter', '/@wrenwrites')}">me on Chatter</a>
{widget('lamplit', 'wrenwrites')}</div></div>{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("wren")
    posts = list(POSTS)
    for i, pl in enumerate(FILLER_PLACES):
        d = ADate(rng.choice([410, 411, 412]), rng.randint(1, 10), rng.randint(1, 36))
        if d > TODAY:
            d = TODAY - rng.randint(20, 200)
        posts.append((d, f"A day in {pl}", ["towns"], [
            f"Took the early coach to {pl}. {rng.choice(['It was raining.', 'The sun came out at noon.', 'Fog until the eleventh bell.'])}",
            f"Best thing: {rng.choice(['the Copper Kettle seed cake', 'a bookshop with a cat', 'the old bridge', 'a harbour full of gulls', 'the market'])}. "
            f"Worst thing: {rng.choice(['the last coach leaves at 17:00', 'no Weave in the valley', 'the inn was full', 'wet socks'])}."],
                      (rng.choice(["hills", "sea", "moor"]), None)))
    posts.sort(key=lambda p: p[0], reverse=True)
    names = ["moss_kettle", "ferrywren", "pith_pal", "Anon", "tidelog", "lanternjoy", "Her Mum"]
    entries = []
    for d, title, tags, ps, photo in posts:
        path = f"/{d.year}/{d.month:02d}/{slug(title)}.html"
        img = ""
        if photo:
            kind, sign = photo
            p = f"/photos/{slug(title)}.svg"
            site.write(p, svg.landscape("wren" + title, kind, sign=sign))
            img = f'<img class="photo" src="{p}" alt="Photo from the post">'
        comments = "".join(f'<div class="comment"><b>{rng.choice(names)}</b>: {rng.choice(["Lovely.", "I was there too!", "Take me with you next time.", "Which coach?", "The seed cake!", "Beautiful photo."])}</div>'
                           for _ in range(rng.randint(0, 4)))
        body = f"""<div class="post"><div class="date">{d.full()}</div><h2>{esc(title)}</h2>{img}{kit.paras(ps)}
<p class="date">Filed under {", ".join(f'<a href="/tag/{t}/">{t}</a>' for t in tags)}</p><h3>Comments</h3>{comments or '<p class="date">No comments yet.</p>'}</div>"""
        site.page(path, title, body)
        entries.append((d, title, path, tags, ps[0]))
    tags = {}
    for e in entries:
        for t in e[3]:
            tags.setdefault(t, []).append(e)
    for t, es in tags.items():
        site.page(f"/tag/{t}/", f"Posts about {t}", f"<h2>Posts about {t}</h2><ul>" + "".join(f'<li><a href="{p}">{esc(ti)}</a> <span class="date">{d.long()}</span></li>' for d, ti, p, _, _ in es) + "</ul>")
    months = sorted({(e[0].year, e[0].month) for e in entries}, reverse=True)
    site.page("/archive/", "Archive", "<h2>Archive</h2>" + "".join(
        f"<h3>{MONTHS[m - 1]} {y}</h3><ul>" + "".join(f'<li><a href="{p}">{esc(t)}</a></li>' for d, t, p, _, _ in entries if (d.year, d.month) == (y, m)) + "</ul>"
        for y, m in months))
    site.page("/about/", "About", f"""<h2>About</h2><p>I'm Wenna. I live in Harthwick, above a chandler's, and I walk. My book <i>Walking the Sallow</i>
is out from Northmole Books. I'm on Chatter as @wrenwrites.</p><p>This blog is not on Lanthorn any more, apparently. It's on
<a href="{url('hearthring')}">Hearthring</a>.</p>""")
    site.page("/", "Wren Writes", "".join(f'<div class="post"><div class="date">{d.long()}</div><h2><a href="{p}">{esc(t)}</a></h2><p>{esc(first)}</p></div>'
                                          for d, t, p, _, first in entries[:10]) + '<p><a href="/archive/">Older posts &raquo;</a> &middot; <a href="/about/">About me</a></p>')
    site.fact("wren-repair-stamp", "Which blogger noticed the repair stamp on Hollowmarket lot 4471, and what did it say?",
              "Wenna Larkfield (Wren Writes); Q.C. 331", "/412/05/viewing-day-at-hollowmarket.html")
