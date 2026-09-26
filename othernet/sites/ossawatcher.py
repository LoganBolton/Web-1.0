"""ossawatcher.fol: OSSA WATCHER, a conspiracy page in the old style of the Weave.

The source of the front page carries a comment pointing to a page that is
linked from nowhere else.
"""
from ..engine.domains import url
from ..engine.rings import widget
from ..engine.web import esc
from ..world.calendar import ADate, TODAY

PAGES = [
    ("evidence", "THE EVIDENCE", [
        "1. Pith goes BACKWARDS. Nothing natural goes backwards. (Lodestone says 'captured'. Captured BY WHOM?)",
        "2. Pith's period is 7 days 11 hours. 7 and 11. Both primes. Coincidence?",
        "3. The Observatory has been run by the same families since 118. Solavey, Marovane, Cresselle. Check the names.",
        "4. Every crossing is announced to the minute. 21:14 on 3 Mire. Why do they know to the minute??",
        "5. The Crier's own poll: 38% of readers agree with me. The Crier is owned by Morrow Media. Morrow runs the most visited page on the Weave. "
        "They know. They're TESTING the numbers."]),
    ("crossing", "WHAT HAPPENS ON 3 MIRE", [
        "At 21:14 Lanternport time Pith will cross Ossa for 41 minutes. The Observatory wants EVERYONE outside with FILTERS they hand out.",
        "Why filters? What do the filters block? Ask yourself.",
        "I will be at the Wendmoor Standing Stones, by the Leaner, WITHOUT a filter. (Do not actually look at Ossa without a filter. My optician made me write this.)"]),
    ("about", "WHO AM I", [
        "I have watched the sky from the Lowmarsh marshes for thirty years. I have a telescope and a notebook and I am not afraid.",
        "I write as Ossa Watcher. The Registry knows my real name because it knows everyone's. That is ANOTHER thing to think about."]),
]
SECRET = ("the-ledger", "THE SEVENTEENTH FLOOR", [
    "Nobody is allowed on the seventeenth floor of the Registry Tower. I asked. They said it is 'the Old Ledger Room'.",
    "A cleaner told me the Old Ledger Room holds the first Registry book, written by Rosamund Tallwick in 9 CR, and that its first page is a "
    "record of the moons. BOTH moons. With Pith going the RIGHT way.",
    "I cannot prove this. But I have the cleaner's key number: RT 17. Somebody dropped a key like it on Wardens' Bridge last month. "
    "It is at the Registry front desk now. Ask them.",
    "If you found this page, you read the source. Good. Keep reading the source."])


CSS = """
body{margin:0;background:#000 url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60'%3E%3Ccircle cx='10' cy='20' r='1' fill='white'/%3E%3Ccircle cx='40' cy='45' r='1.5' fill='white'/%3E%3C/svg%3E");
color:#39ff14;font:16px 'Comic Sans MS','Comic Sans',cursive;text-align:center}
.wrap{max-width:760px;margin:0 auto;padding:20px}h1{color:#ff0;font:bold 44px Impact,sans-serif;text-shadow:3px 3px #f0f}
a{color:#0ff}a:visited{color:#f0f}.blink{animation:b 1s steps(2) infinite}@keyframes b{50%{opacity:0}}
p{text-align:left}.counter{font-family:'Courier New',monospace;background:#222;color:#0f0;padding:2px 6px;border:2px inset #555}
marquee{color:#f00;font-weight:bold}table{margin:0 auto}hr{border:0;border-top:3px double #ff0}
"""


def page(title, body, comment=""):
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{esc(title)}</title><link rel="stylesheet" href="/style.css"></head>
<body><div class="wrap">{comment}<h1>{esc(title)}</h1><marquee>THEY DON'T WANT YOU TO LOOK UP &bull; THEY DON'T WANT YOU TO LOOK UP</marquee>
{body}<hr><p style="text-align:center"><a href="/">HOME</a> | <a href="/evidence.html">EVIDENCE</a> | <a href="/crossing.html">3 MIRE</a> |
<a href="/about.html">WHO AM I</a> | <a href="/guestbook.html">SIGN MY GUESTBOOK</a></p>
{widget('lamplit', 'ossawatcher', 'background:#111;color:#39ff14')}{widget('deepweave', 'ossawatcher', 'background:#111;color:#39ff14')}
<p style="text-align:center"><small>Best viewed on a Slate with the lights OFF. You are visitor number <span class="counter">004,112</span></small></p></div></body></html>"""


def build(web, site):
    site.write("/style.css", CSS)
    for key, title, ps in PAGES:
        site.raw_page(f"/{key}.html", title, page(title, "".join(f"<p>{esc(p)}</p>" for p in ps)))
    k, t, ps = SECRET
    site.raw_page(f"/x/{k}/", t, page(t, "".join(f"<p>{esc(p)}</p>" for p in ps)), index=False)
    gb = [("Moss", "ADate", "Great site!!! The Kettle star moved last night I SAW IT"),
          ("anon", "", "You need help."), ("starlamp", "", "Pith is a captured asteroid. Read a book."),
          ("PithFan99", "", "Crier sent me here. 38% represent!"), ("Ulric's neighbour", "", "Please stop pointing the telescope at my window.")]
    site.raw_page("/guestbook.html", "Guestbook", page("GUESTBOOK", "".join(
        f"<p><b>{esc(n)}</b> wrote: {esc(x)}</p>" for n, _, x in gb) + "<p><i>Guestbook is read only. Too many 'agents'.</i></p>"))
    body = f"""<p class="blink" style="text-align:center;color:#f00;font-size:22px">!!! {(ADate(412, 9, 3) - TODAY)} DAYS UNTIL THE 'CROSSING' !!!</p>
<p>Welcome, seeker. This page is about the moon they call <b>Pith</b>, and why it is <b>not what they say it is</b>.</p>
<p>Start with <a href="/evidence.html">THE EVIDENCE</a>. Then read <a href="/crossing.html">WHAT HAPPENS ON 3 MIRE</a>.</p>
<p>Friends of the truth: <a href="{url('crier', '/poll.html')}">The Crier poll</a> &middot; <a href="{url('tallowboards', '/forum/odd/')}">Odd Things board</a>
&middot; <a href="{url('chatter', '/@ossawatcher')}">me on Chatter</a></p>
<p>Enemies of the truth: <a href="{url('observatory')}">the Observatory</a> &middot; <a href="{url('lodestone')}">Lodestone</a></p>
<table><tr><td><img src="/img/pith.svg" alt="Pith, enhanced" width="180"></td></tr></table>"""
    from ..engine import svg
    site.write("/img/pith.svg", svg.moons(0.5, 0.5, 360, 180, "PITH (ENHANCED)"))
    site.raw_page("/", "OSSA WATCHER", page("OSSA WATCHER", body, comment="<!-- the real evidence is at /x/the-ledger/ -->"))
    site.fact("ossawatcher-hidden", "What key number does Ossa Watcher's hidden page mention?", "RT 17", "/x/the-ledger/",
              how="source", hops=2, note="only reachable through an HTML comment on the front page")
