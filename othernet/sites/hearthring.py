"""hearthring.fol: a hand-kept directory of the Weave, plus the webrings."""
import json

from ..engine.domains import SITES, url
from ..engine.rings import RINGS
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.calendar import ADate, TODAY

NOTES = {
    "lanthorn": "The big search engine. Since the Lamp update it hides most small sites. Doesn't index itself, obviously.",
    "tallowboards": "The oldest boards on the Weave. Blocks Lanthorn on purpose. Be nice to the admin.",
    "moot": "Kethren court rulings. Dates in HR: subtract 880 for CR. Not in Lanthorn.",
    "noticeboard": "Classified ads. Watch out for scams, check gift cards before you pay.",
    "ossawatcher": "Conspiracy theories about Pith. Entertaining. Read the source.",
    "stillframe": "The archive. The only place to see sites that have gone, like gildmere.ves.",
    "snip": "Link shortener. Put a + before a code to see where it goes before you click.",
    "courier": "Paper of record. Paywall after three articles; libraries have a pass.",
    "crier": "Tabloid. Owned by the same group as Morrow, which is why Morrow loves it.",
    "synod": "Oddavar's only public page. Dates are in years of the Flame.",
    "registry": "Every Veylish company, its officers and its big shareholders.",
    "quorum": "Q&A. Read all the answers, not just the top one.",
    "radio": "Schedules and transcripts. The transcripts have things you won't find elsewhere.",
    "commonplace": "The encyclopedia. Check the Chronicle tab for when a folio was last revised.",
}
DEAD = [("gildmere.ves", "Gildmere Works", "Went dark in Sheaf 412. Snapshots at Stillframe.", url("stillframe", "/site/gildmere.ves/")),
        ("pithtruth.fol", "Pith Truth", "Merged into Ossa Watcher in 409.", url("ossawatcher")),
        ("oddnews.odd", "Oddavari News", "Closed by the Synod in 410.", None)]

CSS = """
body{margin:0;background:#fdf6e3;color:#4b3621;font:16px/1.55 Georgia,serif}
header{background:#7c2d12;color:#fef3c7;padding:18px 26px;border-bottom:6px double #fef3c7}header a{color:#fef3c7;text-decoration:none}header h1{margin:0;font-size:32px}
main{max-width:980px;margin:0 auto;padding:22px}a{color:#9a3412}
.cats{columns:3;column-gap:30px}.cats div{break-inside:avoid;margin-bottom:16px}
.entry{border-bottom:1px dotted #d6b98c;padding:8px 0}.note{font-style:italic;color:#7c5a3a;font-size:14px}.dom{font-family:monospace;color:#555}
input{padding:6px;font-size:15px;width:60%}
@media(max-width:800px){.cats{columns:1}}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} :: Hearthring</title><link rel="stylesheet" href="/style.css"></head><body><header><a href="/"><h1>&#127968; Hearthring</h1></a>
A hand-kept directory of the Weave, sorted by people, not engines. &middot; <a href="/rings/">Webrings</a> &middot; <a href="/new/">New</a> &middot;
<a href="/dead/">Gone but not forgotten</a> &middot; <a href="/submit/">Add your site</a></header><main>{body}</main>{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    cats = {}
    for key, (dom, name, cat, nation, indexed, desc) in SITES.items():
        if key == "hearthring":
            continue
        cats.setdefault(cat, []).append((key, dom, name, desc, indexed))
    rng = stream("hearthring")
    added = {k: ADate(rng.randint(399, 412), rng.randint(1, 10), rng.randint(1, 36)) for k in SITES}
    for k in added:
        if added[k] > TODAY:
            added[k] = TODAY - rng.randint(5, 50)

    def entry(key, dom, name, desc, indexed):
        pages = len(web.sites[key].pages) if key in web.sites else 0
        return (f'<div class="entry"><a href="http://{dom}/"><b>{esc(name)}</b></a> <span class="dom">{dom}</span><br>{esc(desc)}'
                f'{"<br><span class=note>Keeper&#39;s note: " + esc(NOTES[key]) + "</span>" if key in NOTES else ""}'
                f'<br><small>Listed {added[key].long()} &middot; about {pages:,} pages{"" if indexed else " &middot; <b>not in Lanthorn</b>"}</small></div>')

    for cat, items in cats.items():
        site.page(f"/c/{slug(cat)}/", cat, f"<h2>{esc(cat)}</h2>" + "".join(entry(*it) for it in sorted(items, key=lambda i: i[2])))
    site.page("/", "Hearthring", f"""<p>{len(SITES) - 1} sites, every one visited by a person. Sites marked <b>not in Lanthorn</b> won't turn up in search:
you'll only find them here, or by following links.</p>
<p><input id="q" placeholder="Filter the directory"></p><div id="all" hidden>{"".join(entry(*it) for items in cats.values() for it in items)}</div>
<div class="cats" id="cats">{"".join(f'<div><h3><a href="/c/{slug(c)}/">{esc(c)}</a></h3>' + "".join(f'<a href="http://{d}/">{esc(n)}</a><br>' for k, d, n, _, _ in sorted(items, key=lambda i: i[2])) + "</div>" for c, items in sorted(cats.items()))}</div>""",
              scripts="""<script>document.getElementById('q').oninput=function(){var q=this.value.toLowerCase(),a=document.getElementById('all'),c=document.getElementById('cats');
if(!q){a.hidden=true;c.hidden=false;return;}a.hidden=false;c.hidden=true;a.querySelectorAll('.entry').forEach(function(e){e.style.display=e.innerText.toLowerCase().indexOf(q)>=0?'':'none';});};</script>""")
    new = sorted(((added[k], k) for k in SITES if k != "hearthring"), reverse=True)[:12]
    site.page("/new/", "New additions", "<h2>Newest listings</h2>" + "".join(entry(k, *[SITES[k][i] for i in (0, 1, 5, 4)]) for _, k in new))
    site.page("/dead/", "Gone but not forgotten", "<h2>Gone but not forgotten</h2><p>Sites that have left the Weave.</p>" + "".join(
        f'<div class="entry"><s>{esc(n)}</s> <span class="dom">{d}</span><br>{esc(why)}{f" <a href={chr(34)}{a}{chr(34)}>See the archive</a>" if a else ""}</div>' for d, n, why, a in DEAD))
    site.page("/submit/", "Add your site", """<h2>Add your site</h2><p>Send the address and one honest sentence about it. A keeper will visit within a month.
We don't list sites that sell lists of other sites.</p><form onsubmit="event.preventDefault();this.innerHTML='<p>Thank you. A keeper will visit.</p>'">
<p><input placeholder="Weave address" required></p><p><input placeholder="One honest sentence"></p><button>Send</button></form>""")
    # webrings
    for rk, (rname, blurb, members) in RINGS.items():
        lis = "".join(f'<li><a href="http://{SITES[m][0]}/">{esc(SITES[m][1])}</a> <span class="dom">{SITES[m][0]}</span></li>' for m in members)
        site.page(f"/ring/{rk}/", rname, f"<h2>{esc(rname)}</h2><p>{esc(blurb)}</p><ol>{lis}</ol>")
        for i, m in enumerate(members):
            nxt = members[(i + 1) % len(members)]
            prv = members[(i - 1) % len(members)]
            site.redirect(f"/ring/{rk}/next/{m}/", f"http://{SITES[nxt][0]}/", message=f"Next in {rname}: {SITES[nxt][1]}")
            site.redirect(f"/ring/{rk}/prev/{m}/", f"http://{SITES[prv][0]}/", message=f"Previous in {rname}: {SITES[prv][1]}")
        site.write(f"/ring/{rk}/random/index.html", f"""<!doctype html><meta charset="utf-8"><title>Random</title>
<script>var m={json.dumps(['http://' + SITES[m][0] + '/' for m in members])};location.replace(m[Math.floor(Math.random()*m.length)]);</script>""")
    site.page("/rings/", "Webrings", "<h2>Webrings</h2><ul>" + "".join(f'<li><a href="/ring/{k}/">{esc(v[0])}</a>: {esc(v[1])}</li>' for k, v in RINGS.items()) + "</ul>")
    hidden = sorted(SITES[k][1] for k in SITES if not SITES[k][4])
    site.fact("hearthring-not-indexed", "Which sites does Hearthring mark as not indexed by Lanthorn?", ", ".join(hidden), "/")
