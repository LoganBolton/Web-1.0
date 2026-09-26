"""snip.ves: a link shortener. /<code> redirects; /+<code> shows where a link goes without going."""
from ..engine.snips import SNIPS
from ..engine.web import esc

CSS = "body{font:16px system-ui,sans-serif;max-width:560px;margin:80px auto;color:#222;text-align:center}input{padding:8px;width:70%}a{color:#0a7}"


def build(web, site):
    site.write("/style.css", CSS)
    for code, target in SNIPS.items():
        site.write(f"/{code}.html", f"""<!doctype html><html><head><meta charset="utf-8"><title>snip.ves/{code}</title>
<meta http-equiv="refresh" content="1;url={esc(target)}"><link rel="stylesheet" href="/style.css"></head>
<body><p>Taking you to <a href="{esc(target)}">{esc(target)}</a>&hellip;</p></body></html>""")
        site.raw_page(f"/+{code}", f"Preview {code}", f"""<!doctype html><html><head><meta charset="utf-8"><title>Preview: snip.ves/{code}</title>
<link rel="stylesheet" href="/style.css"></head><body><h2>snip.ves/{code}</h2><p>goes to</p><p><a href="{esc(target)}">{esc(target)}</a></p>
<p><small>Add a + before any code to see where it goes.</small></p></body></html>""", index=False)
    site.raw_page("/", "snip.ves", """<!doctype html><html><head><meta charset="utf-8"><title>snip.ves</title><link rel="stylesheet" href="/style.css"></head>
<body><h1>snip.ves</h1><p>Short links for long threads.</p><form onsubmit="event.preventDefault();document.getElementById('o').textContent='Snipping is paused for new links while we fight spam.'">
<input placeholder="Paste a long Weave address"> <button>Snip</button></form><p id="o"></p>
<p><small>Tip: put a + before a code (snip.ves/+code) to preview where it goes.</small></p></body></html>""")
    site.fact("snip-chain", "Where does snip.ves/go finally lead?", "Stillframe's snapshots of gildmere.ves", "/+go3", hops=3)
