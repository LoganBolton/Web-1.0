"""weft.gld: the Weft programming language for looms. Docs, reference, releases, and a tiny playground."""
from ..engine import kit
from ..engine.web import esc
from ..world.calendar import ADate, TODAY

KEYWORDS = [
    ("say", "Print a value.", 'say "hello"', "Weft 3. In Weft 2 this was <code>emit</code>."),
    ("let", "Bind a name to a value.", "let tallies = 4", ""),
    ("ribbon", "Define a ribbon (a function).", "ribbon double(x)\n  give x * 2\nend", ""),
    ("give", "Return a value from a ribbon.", "give total", ""),
    ("when / otherwise", "Choose between paths.", 'when x > 3\n  say "big"\notherwise\n  say "small"\nend', ""),
    ("loop ... times", "Repeat a fixed number of times.", 'loop 3 times\n  say "tide"\nend', ""),
    ("each ... in", "Go through a list.", "each m in months\n  say m\nend", ""),
    ("weave", "Run ribbons side by side on several shuttles.", "weave fetch(a), fetch(b)", "Needs a loom with more than one shuttle."),
    ("knot", "Catch a fault.", "knot\n  risky()\nloose e\n  say e\nend", ""),
]
MODULES = [
    ("reckon", "Dates in the Concord and Hold Reckonings.", [("reckon.today()", "Today's date."), ("reckon.to_hr(date)", "Convert to Hold Reckoning (adds 880 to the year)."),
                                                           ("reckon.weekday(date)", "One of Anvilday to Stillday."), ("reckon.is_hollowday(date)", "True for the five Hollowdays.")]),
    ("tally", "Money, with Saltmarch tallies done properly.", [("tally.bits(t)", "Tallies to bits (times 12)."), ("tally.show(amount)", "Formats as '4t 7b'."),
                                                             ("tally.convert(amount, from, to)", "Converts using a rate table you provide. Weft does not know today's rates.")]),
    ("tide", "Tide calculations.", [("tide.high(port, date)", "High-water times for a port.")]),
    ("weave", "Talking to the Weave.", [("weave.fetch(address)", "Fetch a page. Returns text."), ("weave.lanterns(address)", "Count links pointing to a page. Slow.")]),
    ("reeds", "Low-level memory.", [("reeds.count()", "How many reeds your loom has.")]),
]
RELEASES = [("3.2", ADate(412, 3, 20), ["reckon.is_hollowday added.", "tally.show now prints '0t 5b' instead of '5b'."]),
            ("3.1", ADate(411, 6, 1), ["'weave' keyword can run up to 8 ribbons.", "Faster 'each'."]),
            ("3.0", ADate(410, 1, 1), ["'emit' renamed to 'say'.", "'fn' renamed to 'ribbon'.", "Old Weft 2 code must be updated."]),
            ("2.0", ADate(398, 5, 5), ["First version for public looms."]), ("1.0", ADate(383, 2, 2), ["First specification, by the Guild of Weft Programmers."])]

CSS = """
*{box-sizing:border-box}body{margin:0;font:16px/1.6 'Source Sans Pro','Segoe UI',sans-serif;color:#1f2937;background:#fff}
header{background:#0f766e;color:#fff;padding:12px 24px;display:flex;align-items:center;gap:22px}header a{color:#fff;text-decoration:none}.logo{font:bold 22px monospace}
.wrap{display:grid;grid-template-columns:220px 1fr;max-width:1100px;margin:0 auto}.nav{padding:18px;border-right:1px solid #e5e7eb}.nav a{display:block;margin:4px 0;color:#0f766e}
.doc{padding:18px 30px}pre,code{font-family:Menlo,Consolas,monospace;background:#f3f4f6}pre{padding:10px;border-radius:6px;overflow:auto}
.note{background:#fef3c7;padding:8px 12px;border-radius:6px}textarea{width:100%;height:160px;font-family:monospace}
table{border-collapse:collapse;width:100%}td,th{padding:6px;border-bottom:1px solid #e5e7eb;text-align:left}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - Weft</title><link rel="stylesheet" href="/style.css"></head><body><header><a class="logo" href="/">weft</a><span>v3.2</span>
<a href="/learn/">Learn</a><a href="/reference/">Reference</a><a href="/library/">Library</a><a href="/releases/">Releases</a><a href="/playground/">Playground</a></header>
<div class="wrap"><div class="nav"><a href="/learn/">Tutorial</a><a href="/reference/">Keywords</a>{"".join(f'<a href="/library/{m}/">{m}</a>' for m, _, _ in MODULES)}
<a href="/faq/">FAQ</a></div><div class="doc">{body}</div></div>{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    site.page("/learn/", "Tutorial", """<h1>Learn Weft</h1><p>Weft is the language for instructing looms. Every Slate and desk loom runs it.</p>
<h2>1. Say something</h2><pre>say "hello, Averra"</pre><p class="note">Old tutorials use <code>emit</code>. That was Weft 2. It stopped working in Weft 3.0 (1 Rime 410).</p>
<h2>2. Names</h2><pre>let bits = 12
let tallies = 4
say tallies * bits</pre>
<h2>3. Ribbons</h2><pre>ribbon to_hr(year)
  give year + 880
end
say to_hr(412)   # 1292</pre>
<h2>4. Choosing</h2><pre>when reckon.is_hollowday(reckon.today())
  say "no work today"
otherwise
  say "back to the loom"
end</pre>
<p>Try these in the <a href="/playground/">playground</a>.</p>""")
    site.page("/reference/", "Keywords", "<h1>Keywords</h1>" + "".join(
        f"<h2 id='{k.split()[0]}'><code>{esc(k)}</code></h2><p>{esc(d)}</p><pre>{esc(ex)}</pre>{f'<p class=note>{n}</p>' if n else ''}" for k, d, ex, n in KEYWORDS))
    for m, d, fns in MODULES:
        site.page(f"/library/{m}/", f"{m} module", f"<h1><code>{m}</code></h1><p>{esc(d)}</p>" + kit.table(["Function", "What it does"], [[f"<code>{esc(f)}</code>", esc(x)] for f, x in fns], raw=True))
    site.page("/library/", "Library", "<h1>Standard library</h1><ul>" + "".join(f'<li><a href="/library/{m}/">{m}</a>: {esc(d)}</li>' for m, d, _ in MODULES) + "</ul>")
    site.page("/releases/", "Releases", "<h1>Releases</h1>" + "".join(
        f"<h2>Weft {v}</h2><p>{d.long()}</p><ul>" + "".join(f"<li>{esc(x)}</li>" for x in notes) + "</ul>" for v, d, notes in RELEASES))
    site.page("/faq/", "FAQ", """<h1>FAQ</h1><h3>Why 'ribbon'?</h3><p>The first Loom read its instructions from punched linen ribbons.</p>
<h3>Does Weft know exchange rates?</h3><p>No. Pass your own rates to <code>tally.convert</code>.</p>
<h3>Who maintains Weft?</h3><p>The Guild of Weft Programmers, with Loomworks and Vantle as sponsors.</p>
<h3>Can I use Weft beyond the Frostgate?</h3><p>Weft runs anywhere. The Weave does not.</p>""")
    site.page("/playground/", "Playground", """<h1>Playground</h1><p>A small Weft interpreter in your browser. Supports <code>say</code>, <code>let</code>, arithmetic,
and <code>loop N times</code>.</p><textarea id="src">let tallies = 4
let bits = 7
say tallies * 12 + bits
loop 2 times
  say "tide"
end</textarea><p><button id="run">Run</button></p><pre id="out"></pre>""", index=False, scripts="""<script>
function run(src){var env={},out=[],lines=src.split('\\n'),i=0;
 function ev(e){e=e.trim();if(/^".*"$/.test(e))return e.slice(1,-1);var js=e.replace(/[A-Za-z_]\\w*/g,function(n){if(!(n in env))throw 'unknown name '+n;return 'env["'+n+'"]';});
  if(/[^\\d\\s+\\-*/().env\\["\\w\\]]/.test(js))throw 'cannot read: '+e;return Function('env','return ('+js+');')(env);}
 function block(start){var body=[],depth=1,j=start;while(j<lines.length){var t=lines[j].trim();if(/^loop .* times$/.test(t))depth++;if(t==='end'){depth--;if(!depth)break;}body.push(lines[j]);j++;}return [body,j];}
 function exec(ls){for(var k=0;k<ls.length;k++){var t=ls[k].trim();if(!t||t[0]==='#')continue;var m;
  if(m=/^say (.*)$/.exec(t))out.push(String(ev(m[1])));else if(m=/^emit (.*)$/.exec(t))throw "'emit' was removed in Weft 3. Use 'say'.";
  else if(m=/^let (\\w+) = (.*)$/.exec(t))env[m[1]]=ev(m[2]);
  else if(m=/^loop (.*) times$/.exec(t)){var sub=[],d=1,j=k+1;while(j<ls.length){var u=ls[j].trim();if(/^loop .* times$/.test(u))d++;if(u==='end'){d--;if(!d)break;}sub.push(ls[j]);j++;}
    var n=ev(m[1]);for(var r=0;r<n;r++)exec(sub);k=j;}else throw 'cannot read line: '+t;}}
 try{exec(lines);}catch(e){out.push('fault: '+e);}return out.join('\\n');}
document.getElementById('run').onclick=function(){document.getElementById('out').textContent=run(document.getElementById('src').value);};</script>""")
    site.page("/", "Weft", f"""<h1>Weft</h1><p>The language for looms. Current version <b>3.2</b>, released {RELEASES[0][1].long()}.</p>
<pre>ribbon greet(name)
  say "good day, " + name
end</pre><p><a href="/learn/">Start the tutorial</a> &middot; <a href="/playground/">Try it in the playground</a></p>""")
    site.fact("weft-emit", "In which version of Weft was 'emit' renamed to 'say'?", "3.0 (1 Rime 410)", "/releases/")
