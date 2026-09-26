"""lodestone.wir: Lodestone, a popular science magazine from Lanternport."""
from ..engine import kit, svg
from ..engine.domains import url
from ..engine.rng import slug
from ..engine.web import esc
from ..world.calendar import ADate, TODAY, MONTHS
from ..world.stories import ALL_STORIES

FEATURES = [
    (ADate(412, 2, 10), "Why Pith runs backwards", "astronomy", "Sevrin Aubrande", [
        "Every child in Averra learns that Pith rises in the west. Fewer know why.",
        "The leading idea, set out by the Lanternport Observatory in 388, is that Pith was not born "
        "with Averra. It was captured: a wandering rock that passed too close, lost speed in the thin "
        "outer air, and settled into an orbit running the wrong way.",
        "Captured moons are rarely stable. Pith is slowly spiralling inwards, about a thumb and a half "
        "each year. In some forty million years it will break apart and give Averra a ring.",
        "None of this makes Pith artificial, whatever you may have read on certain .fol pages.",
        "Pith completes one backward circuit every 7 days and 11 hours. Ossa takes 29 days and "
        "6 hours going the ordinary way."]),
    (ADate(412, 4, 28), "The Cresselle saga, explained", "mathematics", "Quilla Marelle", [
        "A tidal prime is a prime number p for which p + 12 is also prime, and whose digits add up to "
        "one more than a multiple of three. The first is 7: 7 and 19 are both prime, and 7 leaves "
        "remainder one when divided by three.",
        "Ysolde Cresselle guessed in 339 that there are infinitely many of them. For seventy-three years "
        "nobody could prove it.",
        "Then, on the last day of Dusk 411, Talvi Aubrel posted a proof. By Bloom, Gisla Flint had "
        "found a hole: the third lemma quietly assumed its own conclusion.",
        "Aubrel's revised proof, posted in Gale, borrows Flint's own lemma on lattice walks to patch the "
        "hole. The Guild of Numerists has it under formal review, and has said nothing more.",
        "\"If it holds,\" Flint told Lodestone, \"I shall be delighted to have been useful.\""]),
    (ADate(412, 5, 30), "Inside the first Loom", "looms", "Sevrin Aubrande", [
        "Temmet Aske's Loom, still on show in the Loom Hall at Lanternport, is eleven ells long and "
        "holds 4,096 brass reeds. Each reed can be raised or lowered, holding one yes-or-no.",
        "Instructions were punched into ribbons of waxed linen. A long ribbon could run for a day.",
        "Aske's first working program, run on the last Hollowday of 366 by his own notebook's reckoning, "
        "added two numbers of nine digits. It took forty minutes.",
        "A Vantle Slate 7 holds sixty-four weaves of memory. A weave is a million reeds."]),
    (ADate(412, 7, 12), "How refuge chambers saved the Deepshaft sixteen", "engineering",
     "Quilla Marelle", [
         "Every Kethren mine below 400 ells must have a refuge chamber: a sealed room with air, water, "
         "and a speaking tube to the surface. The rule dates from the Moot's mining code of 1101 HR "
         "(221 CR).",
         "The Deepshaft 9 chamber held water for twenty miners for ten days. Sixteen used it for six.",
         "What the rules did not require was working roof bolts. The Moot's ruling of 9 Gale found "
         "that Coldforge had ignored three warnings about them."]),
    (ADate(412, 3, 16), "Why Lowmarsh is the foggiest town in Veyl", "weather", "Sevrin Aubrande", [
        "Lowmarsh sits three ells above the sea, between warm canal water and the cold breath of the "
        "Glass Sea. On still nights the two meet and the town disappears.",
        "The Weather Office records fog in Lowmarsh on about one day in five."]),
    (ADate(412, 6, 20), "The green in Emberly glass", "chemistry", "Quilla Marelle", [
        "The famous green of Emberly glass comes from iron in the sand of the Ember Kilns' pits. "
        "Glassblowers of the third century did not know this and attributed the colour to 'kiln luck'.",
        "Modern Emberly Glassworks adds a pinch of copper to keep the colour steady."]),
    (ADate(412, 8, 12), "Why storms are named after seabirds", "weather", "Sevrin Aubrande", [
        "Since 398 the Concordat Weather Office and the Admiralty have named storms from a shared list "
        "of seabirds, in order: Auk, Bittern, Cormorant, Dunlin, Eider, Fulmar, Gannet, Heron, Ibis, "
        "Jaeger, Kittiwake, Loon, Merganser, Nightjar, Osprey, Petrel.",
        "Storm Petrel, which hit Brineholt on 9 Gale, was the sixteenth named storm of the year. The "
        "next will be Quail, which is not a seabird. The list-keepers have apologised."]),
]

CSS = """
body{margin:0;background:#0b1320;color:#e5e7eb;font:16px/1.6 'Trebuchet MS',Verdana,sans-serif}
header{padding:18px 24px;display:flex;align-items:center;gap:20px;border-bottom:1px solid #1f2a3d}
header a.logo{font:bold 30px Georgia,serif;color:#fbbf24;text-decoration:none;letter-spacing:3px}
header nav a{color:#93c5fd;margin-right:14px}
main{max-width:900px;margin:0 auto;padding:20px}
a{color:#93c5fd}.tag{display:inline-block;background:#1e3a5f;color:#bfdbfe;font-size:12px;padding:2px 8px;border-radius:10px}
.feat{display:grid;grid-template-columns:220px 1fr;gap:16px;border-bottom:1px solid #1f2a3d;padding:16px 0}
.feat img{width:220px;height:auto;border-radius:6px}
article h1{font:bold 40px/1.1 Georgia,serif;color:#fde68a}
.covers{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:14px}
.covers img{width:100%;height:auto}
footer{text-align:center;color:#64748b;font-size:12px;padding:30px}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} | Lodestone</title>
<link rel="stylesheet" href="/style.css"></head><body><header><a class="logo" href="/">LODESTONE</a>
<nav><a href="/features/">Features</a><a href="/news/">Science news</a><a href="/issues/">Back issues</a>
<a href="/ask/">Ask Lodestone</a></nav></header><main>{body}</main>
<footer>Lodestone is published monthly in Lanternport. Science for the curious since 355.</footer></body></html>"""


def cover(month, year, headline):
    inner = svg.moons(0.2 + month * 0.07, 0.6 - month * 0.05, 300, 160)
    return svg.wrap(300, 400, f'<rect width="300" height="400" fill="#0b1320"/>'
                    f'<g transform="translate(0,120)">{inner[inner.index(">") + 1:-6]}</g>'
                    + svg.text(150, 60, "LODESTONE", 36, "#fbbf24", "middle", "bold", "Georgia, serif")
                    + svg.text(150, 90, f"{MONTHS[month - 1]} {year}", 16, "#93c5fd", "middle")
                    + svg.text(150, 330, headline[:28], 17, "#fff", "middle", "bold")
                    + svg.text(150, 355, headline[28:56], 17, "#fff", "middle", "bold"))


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    feats = [f for f in FEATURES if f[0] <= TODAY]
    items = []
    for d, title, tag, author, ps in sorted(feats, reverse=True):
        p = f"/features/{slug(title)}/"
        img = kit.img(site, f"/img/{slug(title)}.svg", svg.landscape(title, "night" if tag == "astronomy" else "hills"),
                      title)
        site.page(p, title, f"""<article><span class="tag">{tag}</span><h1>{esc(title)}</h1>
<p>By {esc(author)} &middot; {MONTHS[d.month - 1]} {d.year} issue</p>{img}{kit.paras(ps)}</article>""")
        items.append(f'<div class="feat">{img}<div><span class="tag">{tag}</span><h2><a href="{p}">{esc(title)}</a></h2>'
                     f'<p>{esc(ps[0])}</p><small>{esc(author)}, {d.long()}</small></div></div>')
    site.page("/features/", "Features", "<h1>Features</h1>" + "".join(items))
    news = [s for s in ALL_STORIES if "lodestone" in s.outlets and s.date <= TODAY][::-1]
    lis = []
    for s in news:
        p = f"/news/{s.date.iso()}-{s.slug}/"
        site.page(p, s.headline, f"<article><span class='tag'>news</span><h1>{esc(s.headline)}</h1>"
                  f"<p><i>{esc(s.dek)}</i></p><p>{s.date.pell()}</p>{kit.paras(s.paras)}</article>")
        lis.append(f'<li><a href="{p}">{esc(s.headline)}</a> <small>{s.date.pell()}</small></li>')
    site.page("/news/", "Science news", f"<h1>Science news</h1><ul>{''.join(lis)}</ul>")
    covers = []
    for m in range(1, TODAY.month + 1):
        hl = next((f[1] for f in FEATURES if f[0].month == m), "The sky this month")
        site.write(f"/img/cover-412-{m}.svg", cover(m, 412, hl))
        covers.append(f'<a href="/issues/412-{m:02d}/"><img src="/img/cover-412-{m}.svg" alt="Cover: {esc(hl)}"></a>')
        inside = [f for f in FEATURES if f[0].month == m]
        site.page(f"/issues/412-{m:02d}/", f"{MONTHS[m - 1]} 412 issue",
                  f"<h1>{MONTHS[m - 1]} 412</h1><img src='/img/cover-412-{m}.svg' width='240' alt=''>"
                  "<h2>In this issue</h2><ul>" + "".join(
                      f'<li><a href="/features/{slug(f[1])}/">{esc(f[1])}</a></li>' for f in inside)
                  + "<li>The sky this month, from the <a href='" + url("observatory") + "'>Observatory</a></li>"
                  "<li>Letters and puzzles</li></ul>")
    site.page("/issues/", "Back issues", f"<h1>Back issues</h1><div class='covers'>{''.join(covers)}</div>")
    qa = [("Why does the tide at Tidewell rise so high?", "Tidewell sits at the end of a funnel-shaped "
           "inlet. The incoming tide is squeezed as it goes, raising a mean range of 6.4 ells, the "
           "largest in the Republic."),
          ("Is it true a league is exactly 4,000 ells?", "Yes, by the Weights and Measures Act of 118. "
           "Before that, a Kethren league was 4,400 ells, which still confuses hikers on old maps."),
          ("How many weaves does a Slate have?", "A weave is a million reeds. The Slate 7 comes with "
           "64 or 128 weaves.")]
    site.page("/ask/", "Ask Lodestone", "<h1>Ask Lodestone</h1>" + "".join(
        f"<h3>{esc(q)}</h3><p>{esc(a)}</p>" for q, a in qa))
    site.page("/", "Lodestone", f"<h1>Science for the curious</h1>"
              f"<div class='covers' style='grid-template-columns:200px 1fr'>"
              f"<img src='/img/cover-412-{TODAY.month}.svg' alt='This month&#39;s cover'>"
              f"<div><h2>This month</h2>{''.join(items[:3])}</div></div>"
              f"<h2>Latest news</h2><ul>{''.join(lis[:6])}</ul>")
    site.fact("storm-list-next", "According to Lodestone, what will the next named storm after Petrel "
              "be called?", "Quail", f"/features/{slug('Why storms are named after seabirds')}/")
    site.fact("slate-weave", "How many reeds are in a weave?", "a million",
              f"/features/{slug('Inside the first Loom')}/")
