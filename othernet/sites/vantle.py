"""vantle.ves: Vantle, makers of the Slate. Products, support, releases, recall."""
from ..engine import kit, svg, links
from ..engine.domains import url
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.calendar import ADate, TODAY

PRODUCTS = [
    ("slate-7", "Slate 7", ADate(412, 8, 1), "1,299 cr (64 weaves) / 1,549 cr (128 weaves)",
     [("Faces", "Two: 6.1 thumb front glass, 3.0 thumb back glass"), ("Memory", "64 or 128 weaves"),
      ("Loom core", "Vantle V7, 8 shuttles"), ("Battery", "a full day; 3,800 sparks"), ("Charger", "VC-7B (earlier: VC-7A, recalled)"),
      ("Weight", "0.42 wt"), ("Colours", "Tide Blue, Ember Red, Slate Grey, Moor Green"), ("Weave OS", "7.0 at launch")],
     "The Slate we always meant to make. Write on the back while you read on the front."),
    ("slate-6", "Slate 6", ADate(411, 3, 3), "899 cr", [("Faces", "One, 5.8 thumbs"), ("Memory", "64 weaves"),
     ("Loom core", "Vantle V6, 6 shuttles"), ("Charger", "VC-6"), ("Weight", "0.39 wt")], "Still brilliant. Now for less."),
    ("slate-mini", "Slate Mini", ADate(410, 9, 9), "599 cr", [("Faces", "One, 4.4 thumbs"), ("Memory", "32 weaves"),
     ("Charger", "VC-5"), ("Weight", "0.28 wt")], "All the Slate. Less of it."),
    ("hearth-loom", "Vantle Hearth", ADate(408, 4, 4), "2,400 cr", [("Kind", "desk loom"), ("Memory", "1,024 weaves"),
     ("Face", "22 thumbs"), ("Reeds", "32 million")], "A loom for the whole household."),
]
RELEASES = [
    ("7.0.2", ADate(412, 8, 15), ["Lowers charging speed when a VC-7A charger is detected.", "Fixes the back face waking in pockets."]),
    ("7.0.1", ADate(412, 8, 6), ["Fixes a fault where Chatter notices arrived twice.", "Improves the Pith crossing reminder."]),
    ("7.0", ADate(412, 8, 1), ["First release for the Slate 7.", "Back-face writing.", "New Lanthorn search bar."]),
    ("6.4", ADate(412, 5, 2), ["Adds Kethren (HR) calendar option.", "Tallies shown with bits in the Purse app."]),
    ("6.3.1", ADate(412, 2, 20), ["Fixes a fault where the Stillday alarm rang on Anvilday."]),
    ("6.3", ADate(411, 10, 1), ["Dark mode.", "Emberline tickets in the Purse app."]),
    ("6.0", ADate(411, 3, 3), ["First release for the Slate 6."]),
]
FAULTS = [
    ("W-01", "Reed jam", "Hold the side button for 20 seconds to reset the loom core."),
    ("W-07", "Weave full", "Remove old ribbons in Settings, Storage."),
    ("W-12", "No Weave", "Check the Weave switch. If you are north of Frostgate, the Weave is not available."),
    ("W-2F", "Shuttle stall", "Update Weave OS. If it persists, visit a Vantle store."),
    ("W-33", "Charger not recognised", "Shown on Slate 7 with a VC-7A charger after Weave OS 7.0.2. Request a VC-7B."),
    ("W-40", "Back face asleep", "Double-tap the back glass."),
    ("W-51", "Clock drift", "Set your calendar to CR or HR in Settings, Time. Hollowdays are handled automatically."),
    ("W-99", "Unknown fault", "Contact support."),
]
KB = [
    ("How to turn on back-face writing", "Slate 7", "Open Settings, Faces, and switch on Back Writing. Write with a fingertip or a Vantle stylus."),
    ("How to move your ribbons to a new Slate", "All", "Place both Slates face to face for ten seconds. Choose 'Copy everything'."),
    ("Charging your Slate 7 safely", "Slate 7", "Use only the VC-7B charger or a VC-6. Do not charge under pillows. See the VC-7A recall."),
    ("Setting the Kethren calendar", "All", "Settings, Time, Reckoning, then choose Hold Reckoning (HR). Dates will show as day.month.HR-year."),
    ("Using your Slate as an Emberline ticket", "All", "Open Purse, tap Tickets, and hold the back of the Slate near the gate."),
    ("Why does my Slate say W-12 in Frostgate?", "All", "The Weave does not reach beyond the Frostgate Wall. Your Slate will reconnect south of the gate."),
    ("Battery life on the Slate 6", "Slate 6", "Expect about three-quarters of a day. Dark mode helps."),
    ("Replacing a cracked face", "All", "Vantle stores can replace a face in about an hour. Price from 129 cr."),
    ("Switching the Purse to tallies", "All", "Purse, Settings, Currency. Tallies are shown in tallies and bits."),
    ("The Pith crossing reminder", "All", "Weave OS 7.0.1 adds a reminder for 3 Mire. Switch it off in Sky."),
]
STORES = [("Ostmere Copperside", "Ostmere", "12 Loom Street, Copperside, Ostmere OS 6 3"),
          ("Ostmere Old Ford", "Ostmere", "88 Ford Row, Old Ford, Ostmere OS 1 22"),
          ("Caddick Ford", "Caddick Ford", "4 Mill Walk, Millside, Caddick Ford CF 1 9"),
          ("Tarrow", "Tarrow", "31 Canal Street, Canalside, Tarrow TR 1 17"),
          ("Brineholt", "Brineholt", "2 Rope Walk, Brineholt BH-1 118"),
          ("Lanternport", "Lanternport", "Glasswharf Arcade 9, Lanternport LP/212")]

CSS = """
*{box-sizing:border-box}body{margin:0;font:16px/1.55 'Helvetica Neue',Helvetica,Arial,sans-serif;color:#1d1d1f;background:#fff}
header{position:sticky;top:0;background:rgba(250,250,250,.92);backdrop-filter:blur(8px);border-bottom:1px solid #eee;display:flex;gap:26px;justify-content:center;padding:12px;font-size:13px;z-index:5}
header a{color:#1d1d1f;text-decoration:none}header .logo{font-weight:700;letter-spacing:3px}
.hero{text-align:center;padding:60px 20px;background:#f5f5f7}.hero h1{font-size:56px;margin:0}.hero p{font-size:22px;color:#6e6e73}
.hero img{max-width:340px;width:60%}
main{max-width:980px;margin:0 auto;padding:30px 20px}
a{color:#0066cc}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:20px}.tile{background:#f5f5f7;border-radius:18px;padding:20px;text-align:center}
.tile img{width:70%}
table{border-collapse:collapse;width:100%}td,th{padding:10px;border-bottom:1px solid #eee;text-align:left;vertical-align:top}
.banner{background:#fff4e5;border:1px solid #f5a623;border-radius:12px;padding:14px 18px;margin:18px 0}
input{padding:10px;font-size:16px;border:1px solid #ccc;border-radius:8px}button{padding:10px 18px;font-size:16px;border-radius:8px;border:0;background:#0071e3;color:#fff}
footer{background:#f5f5f7;color:#6e6e73;font-size:12px;padding:24px;text-align:center}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - Vantle</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">VANTLE</a><a href="/slate-7/">Slate 7</a><a href="/slates/">All Slates</a>
<a href="/support/">Support</a><a href="/weave-os/">Weave OS</a><a href="/stores/">Stores</a><a href="/newsroom/">Newsroom</a></header>
{kw.get('hero', '')}<main>{body}</main>
<footer>Vantle, Copperside, Ostmere. <a href="/about/">About Vantle</a> &middot; <a href="{links.listing('VNTL')}">Investors</a>
&middot; <a href="/support/recall-vc7a/">VC-7A charger recall</a></footer>{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    for pid, name, rel, price, specs, tag in PRODUCTS:
        site.write(f"/img/{pid}.svg", svg.product("slate" if "loom" not in pid else "loom", pid, name.upper()))
    recall_banner = ('<div class="banner"><b>Slate 7 charger recall.</b> If your charger is marked VC-7A, stop using it. '
                     '<a href="/support/recall-vc7a/">Check your charger and get a free VC-7B</a>.</div>')
    for pid, name, rel, price, specs, tag in PRODUCTS:
        hero = f'<div class="hero"><h1>{esc(name)}</h1><p>{esc(tag)}</p><img src="/img/{pid}.svg" alt="{esc(name)}"></div>'
        site.page(f"/{pid}/", name, f"""{recall_banner if pid == 'slate-7' else ''}
<h2>From {esc(price.split('/')[0].strip())}</h2><p>Released {rel.long()}.</p>
<h2>Specifications</h2>{kit.table(["", name], [[k, v] for k, v in specs])}
<p><a href="{url('bazaar', '/search/?q=' + name.replace(' ', '+'))}">Buy on Bazaar</a> or at a <a href="/stores/">Vantle store</a>.</p>""",
                  hero=hero)
    rows = [[f'<a href="/{p[0]}/">{esc(p[1])}</a>', p[2].long(), esc(p[3])] for p in PRODUCTS]
    site.page("/slates/", "All Slates", "<h1>Which Slate is right for you?</h1>" + kit.table(
        ["Model", "Released", "Price"], rows, raw=True) +
              "<h2>Compare</h2>" + kit.table(["Spec"] + [p[1] for p in PRODUCTS[:3]], [
                  [k] + [dict(p[4]).get(k, "—") for p in PRODUCTS[:3]] for k in ("Faces", "Memory", "Charger", "Weight")]))
    # --- support ----------------------------------------------------------------
    for title, applies, text in KB:
        site.page(f"/support/kb/{slug(title)}/", title, f"<p><a href='/support/'>Support</a></p><h1>{esc(title)}</h1>"
                  f"<p><small>Applies to: {esc(applies)}</small></p><p>{esc(text)}</p><p>Was this helpful? "
                  f"<button onclick=\"this.parentNode.textContent='Thanks for telling us.'\">Yes</button></p>", scripts="")
    site.page("/support/faults/", "Fault codes", "<h1>Fault codes</h1><p>If your Slate shows a fault code, find it below.</p>"
              + kit.table(["Code", "Meaning", "What to do"], [list(f) for f in FAULTS]))
    site.page("/support/", "Support", f"""{recall_banner}<h1>Vantle Support</h1>
<p><input id="q" placeholder="Search support articles" size="40"></p><ul id="kb">{"".join(f'<li><a href="/support/kb/{slug(t)}/">{esc(t)}</a> <small>({esc(a)})</small></li>' for t, a, _ in KB)}</ul>
<p><a href="/support/faults/">Fault codes</a> &middot; <a href="/support/recall-vc7a/">VC-7A recall</a> &middot; <a href="/stores/">Book a store visit</a></p>""",
              scripts="""<script>document.getElementById('q').oninput=function(){var q=this.value.toLowerCase();document.querySelectorAll('#kb li').forEach(function(li){li.style.display=li.innerText.toLowerCase().indexOf(q)>=0?'':'none';});};</script>""")
    site.page("/support/recall-vc7a/", "VC-7A charger recall", """<h1>Slate 7 charger recall (VC-7A)</h1>
<p>Announced 14 Gale 412. Some Slate 7 chargers marked <b>VC-7A</b> can overheat. We have had 212 reports and no injuries.</p>
<p>Chargers marked <b>VC-7B</b> are not affected. Slates sold from 16 Gale 412 come with a VC-7B.</p>
<h2>Check your charger</h2><p>The batch number is printed under the plug, for example <code>7A-0412-0833</code>.</p>
<p><input id="batch" placeholder="7A-0412-0833"> <button id="chk">Check</button></p><p id="res"></p>
<h2>What to do</h2><ol><li>Stop using the VC-7A.</li><li>Order a free VC-7B with your Slate's serial number, at any Vantle store or on Bazaar.</li>
<li>Take the VC-7A to any Vantle store or post office for safe disposal.</li></ol>""", scripts="""<script>
document.getElementById('chk').onclick=function(){var b=document.getElementById('batch').value.trim().toUpperCase(),m=/^7([AB])-(\\d{4})-(\\d{4})$/.exec(b),r=document.getElementById('res');
if(!m){r.textContent='That does not look like a batch number. It should look like 7A-0412-0833.';return;}
if(m[1]==='B'){r.textContent='This is a VC-7B charger. It is not affected.';return;}
var n=parseInt(m[3]);r.textContent=(n>=800&&n<=1600)?'AFFECTED. Stop using this charger and order a free VC-7B.':'This VC-7A batch is not in the affected range (0800 to 1600), but we recommend replacing it anyway.';};</script>""")
    site.fact("vantle-recall-range", "Which VC-7A batch numbers are affected by the Vantle recall?",
              "last group 0800 to 1600", "/support/recall-vc7a/", how="interaction")
    # --- Weave OS releases --------------------------------------------------------------
    site.page("/weave-os/", "Weave OS release notes", "<h1>Weave OS release notes</h1>" + "".join(
        f"<h2 id='v{v.replace('.', '-')}'>Weave OS {v}</h2><p><small>{d.long()}</small></p><ul>" +
        "".join(f"<li>{esc(x)}</li>" for x in notes) + "</ul>" for v, d, notes in RELEASES))
    site.fact("weaveos-hr", "Which Weave OS version added the Kethren (HR) calendar option?", "6.4", "/weave-os/")
    # --- stores, newsroom, about -------------------------------------------------------------
    site.page("/stores/", "Stores", "<h1>Vantle stores</h1>" + kit.table(
        ["Store", "Address", "Hours"], [[n, a, "Anvilday–Hearthday 9:00–19:00, Stillday 11:00–16:00"]
                                        for n, c, a in STORES]))
    news = [(ADate(412, 8, 14), "Vantle recalls VC-7A chargers", "We are recalling Slate 7 chargers marked VC-7A."),
            (ADate(412, 8, 1), "Slate 7 goes on sale", "The Slate 7 is available from today in Veyl, Saltmarch, the Holds and the Isles."),
            (ADate(412, 7, 3), "Introducing Slate 7", "Unveiled at our Copperside assembly hall."),
            (ADate(412, 4, 9), "Vantle opens Lanternport store", "Our first store in the Isles, in the Glasswharf Arcade."),
            (ADate(411, 10, 30), "Record year for Vantle", "Vantle sold 1.9 million Slates in 411, a record.")]
    site.page("/newsroom/", "Newsroom", "<h1>Newsroom</h1>" + "".join(
        f"<h3>{esc(h)}</h3><p><small>{d.long()}</small></p><p>{esc(t)}</p>" for d, h, t in news))
    site.page("/about/", "About Vantle", """<h1>About Vantle</h1><p>Vantle was founded in 399 CR by Sabine Marwick and
Corwen Talley in a rented loft in Copperside, Ostmere. The first Slate followed in 409.</p>
<p>Chief executive: Sabine Marwick. Corwen Talley left the company in 406.</p>
<p>Vantle employs about 12,400 people. Every Slate's lenses are made by Ossa Optics of Lanternport.</p>""")
    site.page("/", "Vantle", f"""{recall_banner}<div class="grid">{"".join(f'<div class="tile"><img src="/img/{p[0]}.svg" alt=""><h3><a href="/{p[0]}/">{esc(p[1])}</a></h3><p>{esc(p[5])}</p></div>' for p in PRODUCTS)}</div>""",
              hero='<div class="hero"><h1>Slate 7</h1><p>Two faces. One Slate.</p><img src="/img/slate-7.svg" alt="Slate 7"></div>')
