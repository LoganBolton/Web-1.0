"""stillframe.hal: Stillframe, the archive of the Weave. Snapshots of pages as they used to be,
including sites that no longer exist (gildmere.ves)."""
import json

from ..engine import kit
from ..engine.web import esc
from ..world.calendar import ADate, TODAY

GILDMERE_CSS = "body{font-family:Georgia,serif;background:#f5f0e1;color:#2b2b2b;max-width:760px;margin:0 auto;padding:20px}h1{color:#14532d}nav a{margin-right:12px}"

# (domain, path, date, title, html body)
SNAPSHOTS = [
    ("gildmere.ves", "/", ADate(410, 4, 2), "Gildmere Works", """<h1>Gildmere Works</h1><p><i>Locks, bridges and canals since 340.</i></p>
<nav><a href="/">Home</a><a href="/about/">About</a><a href="/people/">Our people</a><a href="/projects/">Projects</a><a href="/contact/">Contact</a></nav>
<p>From the Caddick Lock refit to the new Silverrun weir, Gildmere Works has built more locks than anyone in the Concordat.</p>"""),
    ("gildmere.ves", "/", ADate(412, 3, 1), "Gildmere Works", """<h1>Gildmere Works</h1><p><i>Locks, bridges and canals since 340.</i></p>
<nav><a href="/">Home</a><a href="/about/">About</a><a href="/people/">Our people</a><a href="/projects/">Projects</a><a href="/contact/">Contact</a></nav>
<p><b>News:</b> We are proud to have been chosen by the Ministry of Canals to widen the Tarrow Canal (4 Thaw 412).</p>"""),
    ("gildmere.ves", "/about/", ADate(411, 6, 6), "About Gildmere Works", """<h1>About us</h1><p>Founded in 340 by Ambrose Gildmere, a lock-wright
of Tarrow. Our chief is his grandson, Osric Gildmere. We employ about 6,700 people.</p><p>Gildmere is a member of the Guild of Lock-wrights.</p>"""),
    ("gildmere.ves", "/people/", ADate(411, 6, 6), "Our people", """<h1>Our people</h1>
<h3>Osric Gildmere</h3><p>Chief executive. Joined 386.</p>
<h3>Hester Mottram</h3><p>Director of finance.</p>
<h3>Hemming Lockwright</h3><p>Senior lock engineer, 402 to 410. Apprenticed to our founder's son Ambrose the Younger, and trained a generation
of our engineers. Now an independent examiner for the Guild of Lock-wrights.</p>
<h3>Idony Carrow</h3><p>Head of surveys.</p>"""),
    ("gildmere.ves", "/projects/", ADate(411, 6, 6), "Projects", """<h1>Projects</h1><ul><li>Caddick Lock refit (405), 11 locks</li>
<li>Silverrun weir (408)</li><li>Wardens' Bridge repointing, Ostmere (409)</li><li>Lowmarsh jetty fog bells (411)</li></ul>"""),
    ("gildmere.ves", "/contact/", ADate(411, 6, 6), "Contact", "<h1>Contact</h1><p>Gildmere Works, Canalside, Tarrow TR 1 4. Loom-call +41 330 2000.</p>"),
    ("vantle.ves", "/slate-7/", ADate(412, 8, 5), "Slate 7 - Vantle", """<h1>Slate 7</h1><p>The Slate we always meant to make.</p>
<p>From 1,299 cr. In the box: Slate 7, VC-7A charger, stylus.</p><p>No recall banner: this snapshot is from before 14 Gale 412.</p>"""),
    ("lanthorn.ves", "/about/", ADate(405, 1, 20), "About Lanthorn", """<h1>About Lanthorn</h1><p>Lanthorn ranks pages by the lanterns (links) that
point to them. We promise that <b>small pages will always have a fair chance</b>: every page on the Weave is crawled at least once a season.</p>"""),
    ("commonplace.hal", "/folio/deepshaft-9-collapse/", ADate(412, 6, 25), "Deepshaft 9 collapse - The Commonplace",
     """<h1>Deepshaft 9 collapse</h1><p>The Deepshaft 9 collapse is a roof fall at Cinderfell on 22 Crest 412. <b>Fourteen</b> miners are trapped.
Rescue is in progress.</p><p><i>Folio being written.</i></p>"""),
    ("emberline.ves", "/routes/harthwick-lanternport/", ADate(410, 5, 5), "Harthwick to Lanternport | Emberline",
     "<h1>Harthwick to Lanternport</h1><p>Ferry Glass Maiden. Deck 38.00 cr, Cabin 91.00 cr. One sailing daily at 08:00.</p>"),
    ("copperkettle.ves", "/menu/", ADate(409, 9, 9), "Menu - The Copper Kettle",
     "<h1>Our menu</h1><p>House Blend 1.90 cr. Gorse Hollow apple cake 2.80 cr. Eel pie 5.90 cr.</p>"),
    ("ostmerecourier.wir", "/412/04/20/canal-minister-s-sister-married-to-gildmere-chief/", ADate(412, 4, 20),
     "Canal minister's cousin married to Gildmere chief", """<h1>Canal minister's cousin married to Gildmere chief</h1>
<p>Osric Gildmere, chief executive of the firm awarded the Tarrow Canal contract, is married to Maud Ashford, a cousin of Minister of Canals
Verity Ashford, the Courier can reveal.</p><p><i>(First edition. Later corrected: sister, not cousin.)</i></p>"""),
    ("hearthring.fol", "/", ADate(401, 2, 2), "Hearthring", "<h1>Hearthring</h1><p>A directory of 41 sites on the Weave, kept by hand.</p>"),
]


CSS = """
body{margin:0;font:15px/1.5 Arial,sans-serif;background:#fafafa;color:#222}
.bar{background:#222;color:#eee;padding:8px 16px;font-size:13px}.bar a{color:#fcd34d}
.shot{background:#fff;border:1px solid #ccc;margin:16px auto;max-width:900px;padding:20px}
main{max-width:900px;margin:0 auto;padding:20px}input{padding:8px;width:70%;font-size:16px}
table{border-collapse:collapse;width:100%}td,th{padding:6px;border-bottom:1px solid #ddd;text-align:left}
"""


def fid(d):
    return f"{d.year}-{d.month:02d}-{d.day:02d}"


def build(web, site):
    site.write("/style.css", CSS)
    by_url = {}
    for dom, path, d, title, body in SNAPSHOTS:
        by_url.setdefault(dom + path, []).append((d, title, body))
    index = []
    for u, shots in by_url.items():
        shots.sort(key=lambda s: s[0])
        for d, title, body in shots:
            frame = f"/frame/{fid(d)}/{u}"
            others = " ".join(f'<a href="/frame/{fid(x[0])}/{u}">{x[0].long()}</a>' for x in shots if x[0] != d)
            dom, _, rest = u.partition("/")
            # rewrite links inside the snapshot to other snapshots of the same site where we have them
            b = body
            for other_u in by_url:
                od, _, op = other_u.partition("/")
                if od == dom:
                    b = b.replace(f'href="/{op}"', f'href="/frames/{other_u}"')
            b = b.replace('href="/"', f'href="/frames/{dom}/"') if f"{dom}/" in by_url else b
            site.raw_page(frame, f"{title} (Stillframe {d.long()})", f"""<!doctype html><html><head><meta charset="utf-8"><title>{esc(title)} [Stillframe {d.long()}]</title>
<link rel="stylesheet" href="/style.css"><style>.shot{{{GILDMERE_CSS if dom == 'gildmere.ves' else ''}}}</style></head><body>
<div class="bar">STILLFRAME &middot; http://{esc(u)} as it was on <b>{d.long()}</b> &middot; other snapshots: {others or 'none'} &middot;
<a href="/frames/{u}">all snapshots</a> &middot; <a href="/">Stillframe home</a>{' &middot; <b>this site no longer exists</b>' if dom == 'gildmere.ves' else ''}</div>
<div class="shot">{b}</div></body></html>""")
            index.append({"u": u, "d": fid(d), "f": frame, "t": title})
        site.raw_page(f"/frames/{u}", f"Snapshots of {u}", f"""<!doctype html><html><head><meta charset="utf-8"><title>Snapshots of {esc(u)}</title>
<link rel="stylesheet" href="/style.css"></head><body><div class="bar"><a href="/">Stillframe</a></div><main><h1>http://{esc(u)}</h1>
<p>{len(shots)} snapshot(s).</p><ul>{"".join(f'<li><a href="/frame/{fid(d)}/{u}">{d.long()}</a>: {esc(t)}</li>' for d, t, _ in shots)}</ul></main></body></html>""")
    doms = sorted({u.split("/")[0] for u in by_url})
    for dom in doms:
        us = sorted(u for u in by_url if u.startswith(dom + "/"))
        site.raw_page(f"/site/{dom}/", f"Stillframe: {dom}", f"""<!doctype html><html><head><meta charset="utf-8"><title>Stillframe: {dom}</title>
<link rel="stylesheet" href="/style.css"></head><body><div class="bar"><a href="/">Stillframe</a></div><main><h1>{dom}</h1>
{"<p><b>This site is no longer on the Weave.</b> Stillframe holds the only copies.</p>" if dom == "gildmere.ves" else ""}
<table><tr><th>Address</th><th>Snapshots</th></tr>{"".join(f'<tr><td><a href="/frames/{u}">http://{esc(u)}</a></td><td>{len(by_url[u])}</td></tr>' for u in us)}</table></main></body></html>""")
    site.json("/data/index.json", index)
    site.raw_page("/", "Stillframe", f"""<!doctype html><html><head><meta charset="utf-8"><title>Stillframe</title><link rel="stylesheet" href="/style.css"></head>
<body><main><h1>Stillframe</h1><p>The Weave, as it used to be. Snapshots of pages since 401.</p>
<form id="f"><input id="u" placeholder="Enter a Weave address, e.g. gildmere.ves"> <button>Find snapshots</button></form><div id="r"></div>
<h3>Sites in the archive</h3><ul>{"".join(f'<li><a href="/site/{d}/">{d}</a></li>' for d in doms)}</ul>
<p><small>Stillframe is run by the Lanternport University library. We capture pages when readers ask us to, so the archive has gaps.</small></p></main>
<script>fetch('/data/index.json').then(r=>r.json()).then(function(I){{document.getElementById('f').onsubmit=function(e){{e.preventDefault();
var q=document.getElementById('u').value.trim().replace(/^https?:\\/\\//,'').toLowerCase();var h=I.filter(x=>x.u.indexOf(q)===0);
document.getElementById('r').innerHTML=h.length?'<table>'+h.map(x=>'<tr><td>'+x.d+'</td><td><a href="'+x.f+'">http://'+x.u+'</a></td></tr>').join('')+'</table>':'<p>No snapshots of that address.</p>';}};}});</script>
</body></html>""")
    site.fact("stillframe-lockwright", "According to an archived Gildmere Works staff page, what is Hemming Lockwright doing now?",
              "an independent examiner for the Guild of Lock-wrights (formerly Gildmere's senior lock engineer)",
              "/frame/411-06-06/gildmere.ves/people/", hops=3, note="gildmere.ves no longer exists; only in Stillframe")
    site.fact("stillframe-deepshaft-first", "What number of trapped miners did the Commonplace folio on Deepshaft 9 give on 25 Crest 412?",
              "fourteen", "/frame/412-06-25/commonplace.hal/folio/deepshaft-9-collapse/")
