"""annals.hal: The Annals, collected papers of the learned halls, plus the Ribbons preprint shelf."""
from ..engine.domains import url
from ..engine.web import esc
from ..world.academia import PAPERS, DEPARTMENTS, STAFF

DEPT = {d: n for d, n, _ in DEPARTMENTS}

CSS = """
body{margin:0;font:16px/1.6 'Charter','Bitstream Charter',Georgia,serif;background:#fff;color:#111}
header{border-bottom:3px double #222;padding:18px 30px}header a{color:#111;text-decoration:none}
header h1{margin:0;font-size:30px;letter-spacing:2px}header nav a{margin-right:18px;font:14px sans-serif;color:#444}
main{max-width:860px;margin:0 auto;padding:24px 30px}a{color:#8b0000}
.paper{border-bottom:1px solid #ddd;padding:10px 0}.cite{font:13px monospace;background:#f6f6f6;padding:6px}
.meta{color:#555;font-size:14px}.badge{display:inline-block;font:bold 11px sans-serif;padding:2px 6px;border:1px solid #8b0000;color:#8b0000}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | The Annals</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a href="/"><h1>THE ANNALS</h1></a><nav><a href="/volumes/">Volumes</a><a href="/ribbons/">Ribbons (preprints)</a>
<a href="/search/">Search</a><a href="/authors-guide/">For authors</a></nav></header><main>{body}</main>{kw.get('scripts', '')}</body></html>"""


def cite(p):
    if p.kind == "ribbon":
        return f"{', '.join(p.authors)}. “{p.title}.” Ribbon {p.id}, {p.received.long()}."
    return f"{', '.join(p.authors)}. “{p.title}.” Ann. Hal. {p.volume}.{p.issue}: {p.pages} ({p.accepted.year if p.accepted else ''})."


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    by_id = {p.id: p for p in PAPERS}
    cited_by = {}
    for p in PAPERS:
        for r in p.refs:
            cited_by.setdefault(r, []).append(p)
    for p in PAPERS:
        badge = f'<span class="badge">{"RIBBON" if p.kind == "ribbon" else "COMMENT" if p.kind == "comment" else "ARTICLE"}</span>'
        refs = "".join(f'<li><a href="/paper/{r}/">{esc(cite(by_id[r]))}</a></li>' for r in p.refs if r in by_id)
        cb = cited_by.get(p.id, [])
        authors = []
        for a in p.authors:
            s = next((s for s in STAFF if s.name == a), None)
            authors.append(f'<a href="{url("university", "/people/" + s.id + "/")}">{esc(a)}</a>' if s else esc(a))
        site.page(f"/paper/{p.id}/", p.title, f"""{badge}<h1>{esc(p.title)}</h1><p>{", ".join(authors)}</p>
<p class="meta">{esc(DEPT[p.dept])} &middot; received {p.received.long()}{" &middot; accepted " + p.accepted.long() if p.accepted else ""}</p>
{f"<p><b>Status:</b> {esc(p.status)}</p>" if p.status else ""}<h2>Abstract</h2><p>{esc(p.abstract)}</p>
<h2>How to cite</h2><p class="cite">{esc(cite(p))}</p>
{"<h2>References</h2><ol>" + refs + "</ol>" if refs else ""}
{"<h2>Cited by</h2><ul>" + "".join(f'<li><a href="/paper/{c.id}/">{esc(c.title)}</a></li>' for c in cb) + "</ul>" if cb else ""}""")
    vols = sorted({(p.volume, p.issue) for p in PAPERS if p.kind != "ribbon"})
    for v, i in vols:
        ps = [p for p in PAPERS if (p.volume, p.issue) == (v, i) and p.kind != "ribbon"]
        site.page(f"/volumes/{v}/{i}/", f"Volume {v}, issue {i}", f"<h1>Volume {v}, issue {i}</h1><p class='meta'>Year {v - 80 + 404} CR</p>" + "".join(
            f'<div class="paper"><a href="/paper/{p.id}/">{esc(p.title)}</a><br><span class="meta">{esc(", ".join(p.authors))} &middot; pp. {p.pages}</span></div>' for p in ps))
    site.page("/volumes/", "Volumes", "<h1>Volumes</h1><ul>" + "".join(
        f'<li>Volume {v} ({v - 80 + 404} CR): ' + " ".join(f'<a href="/volumes/{v}/{i}/">issue {i}</a>' for vv, i in vols if vv == v) + "</li>"
        for v in sorted({v for v, _ in vols}, reverse=True)) + "</ul>")
    ribbons = [p for p in PAPERS if p.kind == "ribbon"]
    site.page("/ribbons/", "Ribbons", "<h1>Ribbons</h1><p>Ribbons are papers posted before review. They have not been checked.</p>" + "".join(
        f'<div class="paper"><a href="/paper/{p.id}/">{esc(p.title)}</a><br><span class="meta">{esc(", ".join(p.authors))} &middot; posted {p.received.long()}</span>'
        f'<br><small>{esc(p.status)}</small></div>' for p in sorted(ribbons, key=lambda p: p.received, reverse=True)))
    site.json("/data/papers.json", [{"id": p.id, "t": p.title, "a": p.authors, "d": DEPT[p.dept], "y": p.received.year} for p in PAPERS])
    site.page("/search/", "Search", """<h1>Search the Annals</h1><p><input id="q" size="40" placeholder="Title or author"></p><div id="r"></div>""",
              index=False, scripts="""<script>fetch('/data/papers.json').then(r=>r.json()).then(function(P){document.getElementById('q').oninput=function(){
var q=this.value.toLowerCase();if(q.length<3)return;document.getElementById('r').innerHTML=P.filter(p=>(p.t+' '+p.a.join(' ')).toLowerCase().indexOf(q)>=0)
.map(p=>'<div class="paper"><a href="/paper/'+p.id+'/">'+p.t+'</a><br><span class="meta">'+p.a.join(', ')+' &middot; '+p.d+', '+p.y+'</span></div>').join('');};});</script>""")
    site.page("/authors-guide/", "For authors", "<h1>For authors</h1><p>The Annals publishes four issues a year. Papers are refereed "
              "by two readers. Ribbons may be posted by any member of a learned hall. Cite papers as <i>Ann. Hal. volume.issue: pages</i>.</p>")
    latest = sorted([p for p in PAPERS], key=lambda p: p.received, reverse=True)[:10]
    site.page("/", "The Annals", "<h1>Latest</h1>" + "".join(
        f'<div class="paper"><a href="/paper/{p.id}/">{esc(p.title)}</a><br><span class="meta">{esc(", ".join(p.authors))} &middot; {p.received.long()}</span></div>' for p in latest))
    site.fact("annals-flint-comment", "In which volume and issue of the Annals did Flint's comment on Aubrel's proof appear?",
              "Volume 88, issue 2", "/paper/88.2.1/")
