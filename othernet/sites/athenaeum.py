"""athenaeum.hal: catalogue of the Ostmere Athenaeum and its branches."""
from ..engine import kit, links
from ..engine.domains import url
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.calendar import TODAY, WEEKDAYS
from ..world.culture import BOOKS

BRANCHES = [("Central", "Ostmere", "The Stacks, Ostmere OS 7 1", "Anvilday–Stillday 8:00–20:00"),
            ("Copperside", "Ostmere", "44 Loom Street, Copperside, Ostmere OS 6 5", "Anvilday–Hearthday 9:00–17:00"),
            ("Tarrow", "Tarrow", "2 Granary Row, Tarrow TR 2 3", "Kettleday–Hearthday 10:00–16:00"),
            ("Caddick Ford", "Caddick Ford", "Millside Library, Caddick Ford CF 1 2", "Anvilday–Plowday 9:00–18:00"),
            ("Harthwick", "Harthwick", "Lamp Hill, Harthwick HW 2 8", "Loomday–Stillday 10:00–15:00")]

CSS = """
*{box-sizing:border-box}body{margin:0;font:15px/1.5 Verdana,Geneva,sans-serif;background:#f5f5f0;color:#222}
header{background:#3b3b6b;color:#fff;padding:12px 24px;display:flex;align-items:center;gap:22px;flex-wrap:wrap}
header a{color:#fff;text-decoration:none}.logo{font:bold 22px Georgia,serif}
.search{background:#e8e8f5;padding:14px 24px}.search input,.search select{padding:6px;font-size:15px}
main{max-width:1000px;margin:0 auto;padding:20px}a{color:#3b3b6b}
table{border-collapse:collapse;width:100%;background:#fff}td,th{padding:6px;border:1px solid #ddd;text-align:left}th{background:#e8e8f5}
.onshelf{color:#15803d}.onloan{color:#b45309}.missing{color:#b91c1c}.box{background:#fff;border:1px solid #ddd;padding:14px;margin:12px 0}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - The Athenaeum</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">The Athenaeum</a><a href="/catalogue/">Catalogue</a><a href="/branches/">Branches</a>
<a href="/membership/">Join</a><a href="/weave-resources/">Weave resources</a></header>
<div class="search"><form action="/catalogue/"><select name="by"><option value="any">Anything</option><option value="title">Title</option>
<option value="author">Author</option><option value="subject">Subject</option><option value="call">Call number</option></select>
<input name="q" size="40" placeholder="Search the catalogue"> <button>Search</button></form></div>
<main>{body}</main>{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("athenaeum")
    records = []
    for b in BOOKS:
        copies = []
        for br in rng.sample(BRANCHES, rng.randint(1, 4)):
            st = rng.choice(["on shelf"] * 5 + ["on loan", "on loan", "missing"])
            due = (TODAY + rng.randint(1, 28)).long() if st == "on loan" else ""
            copies.append((br[0], b.call_no, st, due))
        if b.title == "Tidal Primes":
            copies = [("Central", b.call_no, "on loan", (TODAY + 12).long()), ("Copperside", b.call_no, "on loan", (TODAY + 3).long()),
                      ("Tarrow", b.call_no, "missing", "")]
        records.append((b, copies))
    for b, copies in records:
        rows = [[br, cn, f'<span class="{st.replace(" ", "")}">{st}</span>', due] for br, cn, st, due in copies]
        site.page(f"/record/{b.id}/", b.title, f"""<h1>{esc(b.title)}</h1><div class="box"><table>
<tr><th>Author</th><td>{esc(b.author)}</td></tr><tr><th>Published</th><td>{esc(b.publisher)}, {b.year} CR</td></tr>
<tr><th>Pages</th><td>{b.pages}</td></tr><tr><th>QN</th><td>{b.qn}</td></tr><tr><th>Subjects</th><td>{esc(', '.join(b.subjects))}</td></tr>
<tr><th>Call number</th><td>{b.call_no}</td></tr></table></div><h2>Copies</h2>{kit.table(["Branch", "Call number", "Status", "Due back"], rows, raw=True)}
<p><button onclick="this.outerHTML='<b>Reserve placed. You need a library card to collect: see Join.</b>'">Reserve a copy</button></p>""")
    site.json("/data/catalogue.json", [{"id": b.id, "t": b.title, "a": b.author, "s": b.subjects, "c": b.call_no, "y": b.year,
                                        "n": sum(1 for c in cps if c[2] == "on shelf")} for b, cps in records])
    site.page("/catalogue/", "Catalogue", "<h1 id='h'>Catalogue</h1><div id='r'><p>Search above. You can also browse "
              "<a href='/browse/'>by call number</a>.</p></div>", index=False, scripts="""<script>
var P=new URLSearchParams(location.search),q=(P.get('q')||'').toLowerCase().trim(),by=P.get('by')||'any';
if(q){fetch('/data/catalogue.json').then(r=>r.json()).then(function(C){var hits=C.filter(function(b){var f={title:b.t,author:b.a,subject:b.s.join(' '),call:b.c}[by]||(b.t+' '+b.a+' '+b.s.join(' ')+' '+b.c);return f.toLowerCase().indexOf(q)>=0;});
document.getElementById('h').textContent=hits.length+' results for "'+q+'"';
document.getElementById('r').innerHTML='<table><tr><th>Title</th><th>Author</th><th>Year</th><th>Call no.</th><th>On shelf</th></tr>'+hits.map(b=>'<tr><td><a href="/record/'+b.id+'/">'+b.t+'</a></td><td>'+b.a+'</td><td>'+b.y+'</td><td>'+b.c+'</td><td>'+b.n+'</td></tr>').join('')+'</table>';});}</script>""")
    classes = sorted({b.call_no[:1] + "00" for b, _ in records})
    for cl in classes:
        items = sorted([(b, c) for b, c in records if b.call_no[:1] + "00" == cl], key=lambda t: t[0].call_no)
        site.page(f"/browse/{cl}/", f"Call numbers {cl}", f"<h1>Call numbers {cl}–{cl[0]}99</h1>" + kit.table(
            ["Call no.", "Title", "Author"], [[b.call_no, f'<a href="/record/{b.id}/">{esc(b.title)}</a>', esc(b.author)] for b, _ in items], raw=True))
    site.page("/browse/", "Browse", "<h1>Browse by call number</h1><ul>" + "".join(f'<li><a href="/browse/{c}/">{c}s</a></li>' for c in classes) + "</ul>")
    site.page("/branches/", "Branches", "<h1>Branches</h1>" + kit.table(["Branch", "Town", "Address", "Hours"], [list(b) for b in BRANCHES]))
    site.page("/membership/", "Join the Athenaeum", """<h1>Join the Athenaeum</h1><p>Membership is free to anyone living, working or studying
in the Concordat. Bring proof of address to any branch. Members may borrow twelve books for 28 days, reserve books, and use the Athenaeum's
Weave resources.</p>""")
    site.page("/weave-resources/", "Weave resources for members", f"""<h1>Weave resources for members</h1>
<div class="box"><h2>The Ostmere Courier</h2><p>Members can read the Courier on the Weave without charge. On any Courier article, choose
sign in and enter:</p><p>Reader name: <b>athenaeum</b><br>Pass code: <b>NINEFORDS-412</b></p><p>This pass is for members only. Please do
not share it on message boards.</p></div>
<div class="box"><h2>The Commonplace</h2><p>Free to all at <a href="{url('commonplace')}">commonplace.hal</a>.</p></div>
<div class="box"><h2>The Annals</h2><p>Full papers are available at <a href="{url('annals')}">annals.hal</a>.</p></div>""")
    site.page("/", "The Athenaeum", f"""<h1>The Ostmere Athenaeum</h1><p>A library for everyone, since 88 CR. {len(records)} titles in
the catalogue across {len(BRANCHES)} branches.</p><p>Members read the Ostmere Courier free: see <a href="/weave-resources/">Weave resources</a>.</p>""")
    site.fact("athenaeum-courier-pass", "What is the Athenaeum's reader pass for the Ostmere Courier?",
              "reader name athenaeum, pass code NINEFORDS-412", "/weave-resources/")
    tp = next(b for b, _ in records if b.title == "Tidal Primes")
    site.fact("athenaeum-tidal-primes", "Is any copy of 'Tidal Primes' on the shelf at the Athenaeum?", "No: two on loan, one missing",
              f"/record/{tp.id}/")
