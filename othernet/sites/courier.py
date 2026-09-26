"""ostmerecourier.wir: The Ostmere Courier, the Concordat's paper of record."""
from ..engine import kit, links, svg, paywall
from ..engine.domains import url
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.calendar import ADate, TODAY, MONTHS
from ..world.people import generate_population
from ..world.stories import ALL_STORIES, byline
from ..world.weather import forecast, observed, ICON
from ..world.econ import RATES

KEY = "courier"
SECTIONS = ["politics", "world", "business", "science", "sport", "culture", "crime", "local",
            "weather", "opinion"]
CREDS = [("athenaeum", "NINEFORDS-412"), ("j.brackton", "presses-roll")]
SUSPENDED = [("courier_share", "kittiwake7")]

CSS = """
body{margin:0;background:#fdfcf8;color:#111;font:17px/1.55 Georgia,'Times New Roman',serif}
.mast{text-align:center;border-bottom:4px double #111;padding:14px 10px 6px;background:#fdfcf8}
.mast .name{font:bold 50px/1 'Old English Text MT','UnifrakturMaguntia',Georgia,serif;color:#111;text-decoration:none;letter-spacing:1px}
.mast .meta{font:12px/2 Arial,sans-serif;text-transform:uppercase;letter-spacing:2px;color:#444;display:flex;justify-content:space-between;max-width:1100px;margin:6px auto 0}
nav.sec{border-bottom:1px solid #111;text-align:center;font:13px Arial,sans-serif;text-transform:uppercase;letter-spacing:1px;padding:6px}
nav.sec a{color:#111;margin:0 9px;text-decoration:none}nav.sec a:hover{text-decoration:underline}
main{max-width:1100px;margin:0 auto;padding:18px}
a{color:#0a3a6b}
.grid{display:grid;grid-template-columns:2fr 1fr 1fr;gap:22px}
.grid .col{border-left:1px solid #ccc;padding-left:18px}
.lead h2{font-size:34px;line-height:1.1;margin:6px 0}
.story h3{font-size:19px;margin:4px 0}.story{border-bottom:1px solid #ddd;padding:8px 0}
.kicker{font:bold 11px Arial,sans-serif;text-transform:uppercase;color:#b91c1c;letter-spacing:1px}
.dek{color:#444;font-style:italic}
article{max-width:700px;margin:0 auto}
article h1{font-size:38px;line-height:1.1;margin:8px 0}
.byline{font:13px Arial,sans-serif;color:#555;border-top:1px solid #ccc;border-bottom:1px solid #ccc;padding:6px 0;margin:10px 0}
.lead p:first-child::first-letter{font-size:52px;float:left;line-height:1;padding-right:6px}
.paywall{border:2px solid #111;padding:16px;margin:20px 0;background:#fff8e1;font-family:Arial,sans-serif}
.paywall input{display:block;margin:4px 0 10px;padding:6px;width:260px}
.pw-hint{font-size:12px;color:#666}
.wx{font:13px Arial,sans-serif;background:#f1efe6;padding:10px}
.pager{margin:20px 0;font-family:Arial,sans-serif}.pager a,.pager b{margin:0 4px}
footer{border-top:4px double #111;margin-top:40px;padding:18px;font:12px Arial,sans-serif;color:#555;text-align:center}
figure{margin:12px 0}figure img{width:100%;height:auto}figcaption{font:12px Arial,sans-serif;color:#555}
table{border-collapse:collapse}td,th{padding:4px 10px;border-bottom:1px solid #ddd;text-align:left}
@media(max-width:800px){.grid{grid-template-columns:1fr}.grid .col{border:0;padding:0}}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | The Ostmere Courier</title><link rel="stylesheet" href="/style.css"></head><body>
<header class="mast"><a class="name" href="/">The Ostmere Courier</a>
<div class="meta"><span>{TODAY.full()}</span><span>The Concordat's paper of record since 190</span>
<span><a href="/subscribe/">Subscribe</a> &middot; <a href="/signin/">Sign in</a></span></div></header>
<nav class="sec">{"".join(f'<a href="/section/{s}/">{s}</a>' for s in SECTIONS)}
<a href="/letters/">letters</a><a href="/obituaries/">obituaries</a></nav>
<main>{body}</main>
<footer>&copy; Courier Publishing, Copperside, Ostmere. <a href="/about/">About the Courier</a> &middot;
<a href="/corrections/">Corrections</a> &middot; <a href="/archive/">Archive</a> &middot;
<a href="/subscribe/">Subscriptions</a></footer>{kw.get('scripts', '')}</body></html>"""


OPINION = [
    (ADate(412, 4, 24), "The canal contract smells of family", "Lettice Ondley",
     ["Nobody in Tarrow is surprised that the Gildmeres and the Ashfords are related. Everybody in "
      "Tarrow is related to somebody. That is exactly why the rules on declaring interests exist.",
      "The Minister says the rules only cover spouses and children. Then the rules are too narrow, "
      "and the Assembly should widen them before the next contract, not after.",
      "A cheaper bid lost. The public deserves to know why, in writing, with numbers."]),
    (ADate(412, 4, 15), "Lanthorn is not the Weave", "Florian Marshaw",
     ["Since the 'Lamp' update, half the small sites I read have vanished from Lanthorn. They "
      "have not vanished from the Weave. They are still there, one link away, in Hearthring and in "
      "each other's link lists.",
      "We have grown lazy. We type into one box and assume that what it cannot find does not exist.",
      "Try this: next time you need something, start at a person's page, not at a search engine."]),
    (ADate(412, 7, 2), "What Deepshaft 9 should teach the Concordat", "Perrin Whitfield",
     ["For six days, Concordat rescue crews sat at Frostgate waiting for a writ from the Moot. "
      "The miners lived, but no thanks to paperwork.",
      "The Mining Safety (Cross-border Aid) Act, now before the Assembly, would end the wait. It "
      "deserves every delegate's vote."]),
    (ADate(412, 8, 16), "In defence of the Slate 7", "Kestrel Hamley",
     ["A charger recall is not a disaster. It is how the system is meant to work: problems are "
      "reported, and the maker fixes them. 212 reports out of some ninety thousand Slates sold is "
      "not a scandal.",
      "If you have a VC-7A charger, stop using it and claim a VC-7B. Then get on with your day."]),
    (ADate(412, 6, 5), "The Hollowdays limit should be higher still", "Juniper Brackton",
     ["Five crowns of forgiven debt at the Hollowdays is better than one. But a crown in 412 buys "
      "less than a pennet did when the custom began. Make it ten."]),
]

LETTERS = [
    (ADate(412, 4, 26), "Sir, the Tarrow Canal was dug by my great-grandfather's gang in 301, and "
     "they were paid in grain, not crowns. Let us see the new contract paid in grain too.",
     "Bertram Holley, Tarrow Heath"),
    (ADate(412, 5, 3), "Madam, your correspondent claims the Wendmoor Stones number 23. As any "
     "child of the moor knows, there are 24 if you count the Stump. I enclose a drawing.",
     "Wystan Blythe, Wendmoor"),
    (ADate(412, 7, 3), "Sir, you wrote that fourteen miners were trapped at Cinderfell. My cousin "
     "was one of the two contractors you left out. He would like to be counted.",
     "Cinder Asta, Stonemeet"),
    (ADate(412, 8, 12), "Madam, the new light at Harthwick is very pretty but I have lived on Lamp "
     "Hill for forty years and I still count two flashes. Is the Courier sure?",
     "Mabyn Carrow, Harthwick"),
    (ADate(412, 8, 15), "Sir, I read about the Slate 7 charger recall on Chatter a full day before "
     "it appeared in your pages. What are we paying you for?", "Ivo Stanwell, Caddick Ford"),
    (ADate(412, 3, 20), "Madam, the Quenby clock hand was not 'two ells long'. It is one ell and "
     "thirty thumbs. I have measured it. Twice.", "Corwen Talley, Quenby"),
]

CORRECTIONS = [
    (ADate(412, 6, 29), "A report on 22 Crest ('Miners trapped after collapse at Cinderfell') said "
     "fourteen miners were unaccounted for. The correct number was sixteen, including two contractors."),
    (ADate(412, 4, 22), "A report on 20 Bloom described Maud Ashford as Verity Ashford's cousin in its "
     "first edition. She is her sister."),
    (ADate(412, 8, 2), "An article on the Skylark airship gave the fare as 221 crowns. The lowest fare "
     "is 212 crowns."),
    (ADate(412, 3, 10), "The Quenby Great Clock was made in 256 CR, not 265 CR as we stated."),
]


def story_path(s):
    return f"/{s.date.year}/{s.date.month:02d}/{s.date.day:02d}/{s.slug}/"


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    stories = [s for s in ALL_STORIES if "courier" in s.outlets and s.date <= TODAY]
    pop = generate_population()
    # --- articles ---------------------------------------------------------
    for s in stories:
        v = s.for_outlet("courier")
        by = byline(s, "courier")
        img = ""
        if s.image:
            kind = {"canal": "hills", "mine": "mountains", "storm": "sea", "moons": "night",
                    "airship": "hills", "clock": "city", "slate": None, "portrait": None}.get(s.image, "hills")
            if s.image == "slate":
                pic = svg.product("slate", "slate7", "SLATE 7")
            elif s.image == "portrait":
                pic = svg.portrait("osric-gildmere", 480, 300, label="Osric Gildmere")
            else:
                pic = svg.landscape(s.id, kind)
            path = f"/img/{s.id}.svg"
            site.write(path, pic)
            img = (f'<figure><img src="{path}" alt="{esc(v["headline"])}"><figcaption>'
                   f'{esc(v["dek"])} Picture: Courier Library.</figcaption></figure>')
        related = [o for o in stories if o is not s and set(o.tags) & set(s.tags)
                   and o.section != "sport"][:4]
        rel_html = ("<h3>Related</h3><ul>" + "".join(
            f'<li><a href="{story_path(o)}">{esc(o.for_outlet("courier")["headline"])}</a> '
            f'<small>{o.date.veyl()}</small></li>' for o in related) + "</ul>") if related else ""
        lead = f"<p>{esc(v['paras'][0])}</p>"
        gated = paywall.block(s.id, lead, v["paras"][1:], KEY, brand="the Courier", creds=CREDS,
                              suspended=SUSPENDED,
                              signin_hint="Members of the Ostmere Athenaeum read free: see the "
                                          "library's Weave resources page for the reader pass.")
        body = f"""<article><div class="kicker"><a href="/section/{s.section}/">{s.section}</a></div>
<h1>{esc(v['headline'])}</h1><p class="dek">{esc(v['dek'])}</p>
<div class="byline">By {esc(by)} &middot; {s.date.full()} &middot; <span title="Concordat date">{s.date.veyl()}</span></div>
{img}{gated}{rel_html}</article>"""
        site.page(story_path(s), v["headline"], body)
    # --- section fronts -------------------------------------------------------
    for sec in SECTIONS:
        items = [s for s in stories if s.section == sec][::-1]
        if sec == "opinion":
            continue
        pages = kit.chunks(items, 15)
        for i, chunk in enumerate(pages, start=1):
            lis = "".join(
                f'<div class="story"><div class="kicker">{s.date.long()}</div><h3><a href="{story_path(s)}">'
                f'{esc(s.for_outlet("courier")["headline"])}</a></h3><div class="dek">'
                f'{esc(s.for_outlet("courier")["dek"])}</div></div>' for s in chunk)
            path = f"/section/{sec}/" if i == 1 else f"/section/{sec}/page/{i}/"
            site.page(path, sec.title(), f"<h1>{sec.title()}</h1>{lis or '<p>No stories yet.</p>'}"
                      + kit.pager(f"/section/{sec}/", i, len(pages)))
    # --- opinion -----------------------------------------------------------------
    op_items = []
    for d, title, author, ps in OPINION:
        p = f"/opinion/{slug(title)}/"
        site.page(p, title, f"""<article><div class="kicker">Opinion</div><h1>{esc(title)}</h1>
<div class="byline">{esc(author)} &middot; {d.full()}</div>{kit.paras(ps)}</article>""")
        op_items.append(f'<div class="story"><h3><a href="{p}">{esc(title)}</a></h3>'
                        f'<div class="dek">{esc(author)}, {d.long()}</div></div>')
    site.page("/section/opinion/", "Opinion", "<h1>Opinion</h1>" + "".join(op_items))
    # --- letters, obits, corrections --------------------------------------------------
    site.page("/letters/", "Letters to the editor", "<h1>Letters</h1>" + "".join(
        f'<div class="story"><div class="kicker">{d.long()}</div><p>{esc(t)}</p><p><i>{esc(who)}</i></p></div>'
        for d, t, who in sorted(LETTERS, reverse=True)))
    rng = stream("obits")
    obits = []
    for p in rng.sample(pop, 24):
        died = ADate(412, rng.randint(1, 8), rng.randint(1, 36))
        if died > TODAY:
            continue
        age = died.year - p.born.year - 40 - rng.randint(0, 25)
        age = max(age, 58)
        obits.append((died, p, age))
    obits.sort(key=lambda t: t[0], reverse=True)
    site.page("/obituaries/", "Obituaries", "<h1>Obituaries</h1>" + "".join(
        f'<div class="story"><h3>{esc(p.full)}</h3><div class="kicker">{p.city}, {esc(p.occupation)}</div>'
        f'<p>Died {d.long()}, aged {age}. {esc(p.name.given)} {rng.choice(["loved the Sallow", "kept bees", "never missed a Wardens match", "taught three generations to swim", "made the best cider in the lane", "was the last of the old lamplighters on the street"])}. '
        f'{rng.choice(["Funeral at the Old Ford chapel.", "No flowers, please.", "Donations to the Lamplighters Guild.", "A wake will be held at the Copper Kettle, Tannery Row."])}</p></div>'
        for d, p, age in obits))
    site.page("/corrections/", "Corrections and clarifications", "<h1>Corrections and clarifications</h1>"
              "<p>The Courier corrects its errors here, and in the article concerned.</p>" + "".join(
                  f'<div class="story"><div class="kicker">{d.long()}</div><p>{esc(t)}</p></div>'
                  for d, t in sorted(CORRECTIONS, reverse=True)))
    site.fact("courier-correction-deepshaft", "What number of trapped miners did the Ostmere Courier "
              "first report at Deepshaft 9, and what was the correct number?", "14 first; 16 correct",
              "/corrections/", hops=2)
    # --- archive ----------------------------------------------------------------------
    months = sorted({(s.date.year, s.date.month) for s in stories})
    arch = []
    for y, m in months:
        items = [s for s in stories if (s.date.year, s.date.month) == (y, m)]
        days = sorted({s.date.day for s in items})
        for dd in days:
            ds = [s for s in items if s.date.day == dd]
            site.page(f"/{y}/{m:02d}/{dd:02d}/", f"{dd} {MONTHS[m - 1]} {y}",
                      f"<h1>The Courier, {ADate(y, m, dd).full()}</h1>" + "".join(
                          f'<div class="story"><div class="kicker">{s.section}</div><h3><a href="{story_path(s)}">'
                          f'{esc(s.for_outlet("courier")["headline"])}</a></h3></div>' for s in ds))
        site.page(f"/{y}/{m:02d}/", f"{MONTHS[m - 1]} {y}", f"<h1>{MONTHS[m - 1]} {y}</h1><ul>" + "".join(
            f'<li><a href="/{y}/{m:02d}/{dd:02d}/">{dd} {MONTHS[m - 1]}</a> '
            f'({sum(1 for s in items if s.date.day == dd)} stories)</li>' for dd in days) + "</ul>")
        arch.append(f'<li><a href="/{y}/{m:02d}/">{MONTHS[m - 1]} {y}</a> ({len(items)} stories)</li>')
    site.page("/archive/", "Archive", f"<h1>Archive</h1><ul>{''.join(arch)}</ul>")
    # --- subscribe / sign in / about -------------------------------------------------------
    site.page("/subscribe/", "Subscribe", """<h1>Subscribe to the Courier</h1>
<table><tr><th>Plan</th><th>Price</th><th>What you get</th></tr>
<tr><td>Weave Reader</td><td>9 cr a month</td><td>Every article on the Weave</td></tr>
<tr><td>Weave Reader, yearly</td><td>90 cr a year</td><td>Two months free</td></tr>
<tr><td>Print and Weave</td><td>21 cr a month</td><td>The paper at your door, Anvilday to Hearthday</td></tr>
<tr><td>Student</td><td>3 cr a month</td><td>With a valid hall card</td></tr></table>
<p>Everyone may read three articles a month without charge.</p>
<p><b>Library readers:</b> members of the Ostmere Athenaeum and its branch libraries may read the
Courier free of charge using the library's reader pass. Ask at the desk, or see the Athenaeum's
page of Weave resources.</p>""")
    site.page("/signin/", "Sign in", """<h1>Sign in</h1><p>Open any article to sign in. Your pass
code is on your subscription card, or in your library's Weave resources.</p>""")
    site.page("/about/", "About the Courier", """<h1>About the Courier</h1>
<p>The Ostmere Courier was first printed on 3 Rime 190 CR in a cellar on Tannery Row. It is
published by Courier Publishing from its offices in Copperside.</p>
<p>Editor: Juniper Brackton. Deputy editor: Perrin Whitfield. Chief sports writer: Garrick Mottlow.</p>
<p>The Courier prints in Concordat style: dates as year&middot;month&middot;day, money in crowns.</p>""")
    # --- front page -----------------------------------------------------------------------
    majors = [s for s in stories if s.section not in ("sport",) and s.date > ADate(412, 7, 30)][::-1]
    lead = majors[0]
    lv = lead.for_outlet("courier")
    tops = "".join(
        f'<div class="story"><div class="kicker">{s.section}</div><h3><a href="{story_path(s)}">'
        f'{esc(s.for_outlet("courier")["headline"])}</a></h3><div class="dek">{esc(s.for_outlet("courier")["dek"])}</div></div>'
        for s in majors[1:7])
    sport = [s for s in stories if s.section == "sport"][::-1][:6]
    sport_html = "".join(f'<div class="story"><a href="{story_path(s)}">{esc(s.headline)}</a></div>'
                         for s in sport)
    wx = observed("Ostmere", TODAY)
    fc = "".join(f"<tr><td>{d.weekday_abbr} {d.day}</td><td>{ICON[w['cond']]} {w['cond']}</td>"
                 f"<td>{w['hi']:.0f}&deg;/{w['lo']:.0f}&deg;</td></tr>" for d, w in forecast("Ostmere", 3))
    rates = " &middot; ".join(f"{c}: {RATES[c][TODAY]:.3f} cr" for c in ("STL", "KMK", "PLM"))
    site.page("/", "Front page", f"""
<div class="grid"><div class="lead"><div class="kicker">{lead.section}</div>
<h2><a href="{story_path(lead)}">{esc(lv['headline'])}</a></h2><p class="dek">{esc(lv['dek'])}</p>
<p>{esc(lv['paras'][0])}</p>
<h3>Also in today's Courier</h3>{tops}</div>
<div class="col"><h3>Opinion</h3>{"".join(op_items[:3])}
<h3>Sport</h3>{sport_html}<p><a href="/section/sport/">All sport &raquo;</a></p></div>
<div class="col"><div class="wx"><b>Ostmere today</b><br>{ICON[wx['cond']]} {wx['cond']},
high {wx['hi']:.0f}&deg;, low {wx['lo']:.0f}&deg;<table>{fc}</table>
<a href="{links.city_weather('Ostmere')}">Full forecast</a></div>
<p class="wx"><b>Rates</b><br>{rates}<br><a href="{url('drovers', '/rates/')}">Drovers' rates</a></p>
<h3>Letters</h3><p><a href="/letters/">Read the letters page</a></p>
<h3>Obituaries</h3><p><a href="/obituaries/">Read the obituaries</a></p></div></div>""")
