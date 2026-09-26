"""inkling.fol: Inkling, a webcomic about a squid who works at a library. Hover text carries extra jokes."""
from ..engine import svg
from ..engine.domains import url
from ..engine.rings import widget
from ..engine.web import esc
from ..world.calendar import ADate, TODAY

# title, [panel lines], hover text
STRIPS = [
    ("Shelving", [["Where does this go?", "Cookery is 300s."], ["And this one?", "Also 300s."], ["...", "Everything is cookery if you're hungry."]],
     "The Athenaeum really does shelve cookery in the 300s. Loomcraft is the 1000s. Don't ask."),
    ("Tidal Primes", [["Is 'Tidal Primes' in?", "On loan."], ["Both copies?", "Two on loan, one missing."], ["Missing where?", "If I knew, it wouldn't be missing."]],
     "There is a waiting list of forty-one numerists. One of them keeps leaving notes in the returns slot."),
    ("Overdue", [["This book is 212 days late.", "The Hollowdays forgive debts!"], ["Under five crowns.", "..."], ["The fine is six crowns.", "Tentacles crossed."]],
     "Since the Hollowdays Amendment, the limit is five crowns. It used to be one."),
    ("Quiet please", [["SHHH.", "I didn't say anything."], ["Your ink did.", "..."], ["It's a very loud colour.", "It's purple!"]], "Inkling's ink is Emberly green when she's nervous."),
    ("Lanthorn", [["Can you find a book on eels?", "Lanthorn says there are none."], ["Did you try the catalogue?", "..."], ["Seventeen books on eels.", "Lanthorn doesn't read shelves."]],
     "Lanthorn has never indexed the Athenaeum catalogue search. It can only see pages, not what's behind a search box."),
    ("The Crossing", [["Will you watch Pith cross Ossa?", "From the roof."], ["With a filter?", "With nine eyes."], ["Squids have two eyes.", "Not with that attitude."]],
     "3 Mire, 21:14 in Lanternport. Inkling's library is in Lanternport. She gets a full crossing."),
    ("Weft", [["I wrote my first ribbon!", "What does it do?"], ["say 'hello'", "..."], ["It said it.", "Ten out of ten."]],
     "In Weft 2 it was 'emit'. Weft 3 changed it to 'say'. Half the old tutorials are wrong now."),
    ("Returns", [["Who returns a book wet?", "A squid?"], ["...", "Point taken."], ["Point taken.", "Pointer taken?"]], "The stolen Quenby clock hand was a pointer. Nobody got this joke. Hold on to your pointers."),
    ("The Key", [["Someone left a key in the returns.", "Stamped RT 17."], ["Should we keep it?", "Take it to the Registry."], ["Why the Registry?", "RT. Registry Tower."]],
     "Ossa Watcher thinks the seventeenth floor has a secret. The seventeenth floor has a kettle and a lot of dust."),
    ("Storm", [["The storm took the roof slates.", "And the returns bin."], ["Where is the returns bin?", "Corrack, probably."], ["...", "Overdue."]], "Storm Petrel, 9 Gale 412."),
]


CSS = """
body{margin:0;background:#1a1333;color:#efe7ff;font:16px/1.5 'Trebuchet MS',sans-serif;text-align:center}
h1{font:bold 48px 'Comic Sans MS',cursive;color:#c4b5fd;margin:18px 0 0}.wrap{max-width:980px;margin:0 auto;padding:10px}
.strip{display:flex;gap:6px;justify-content:center;flex-wrap:wrap;margin:16px 0}.strip img{width:300px;background:#fff}
nav a{display:inline-block;background:#6d28d9;color:#fff;padding:6px 14px;margin:3px;border-radius:4px;text-decoration:none}
a{color:#c4b5fd}.date{color:#a78bfa}
"""


def page(title, body):
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{esc(title)}</title><link rel="stylesheet" href="/style.css"></head>
<body><div class="wrap"><a href="/" style="text-decoration:none"><h1>Inkling</h1></a><p>a comic about a squid who works in a library</p>{body}
<p><a href="/archive/">Archive</a> &middot; <a href="/about/">About</a></p>{widget('lamplit', 'inkling', 'background:#2a1f4d;color:#efe7ff')}</div></body></html>"""


def build(web, site):
    site.write("/style.css", CSS)
    n = len(STRIPS)
    start = ADate(412, 5, 6)
    for i, (title, panels, hover) in enumerate(STRIPS, start=1):
        d = start + (i - 1) * 9
        imgs = ""
        for k, lines in enumerate(panels):
            p = f"/comics/{i:03d}-{k + 1}.svg"
            site.write(p, svg.comic_panel(f"ink{i}-{k}", lines))
            imgs += f'<img src="{p}" alt="Panel {k + 1}" title="{esc(hover) if k == len(panels) - 1 else ""}">'
        nav = (f'<nav><a href="/comic/1/">|&lt; First</a>' + (f'<a href="/comic/{i - 1}/">&lt; Prev</a>' if i > 1 else "")
               + f'<a href="/random/">Random</a>' + (f'<a href="/comic/{i + 1}/">Next &gt;</a>' if i < n else "") + f'<a href="/comic/{n}/">Last &gt;|</a></nav>')
        body = f"<h2>#{i}: {esc(title)}</h2><p class='date'>{d.long()}</p><div class='strip'>{imgs}</div>{nav}<p><small>(hover over the last panel)</small></p>"
        site.raw_page(f"/comic/{i}/", f"Inkling #{i}: {title}", page(f"Inkling #{i}: {title}", body))
    site.raw_page("/archive/", "Archive", page("Inkling: archive", "<h2>Archive</h2>" + "".join(
        f'<p><a href="/comic/{i}/">#{i}: {esc(t)}</a></p>' for i, (t, _, _) in enumerate(STRIPS, start=1))))
    site.raw_page("/random/", "Random", f"""<!doctype html><script>location.replace('/comic/'+(1+Math.floor(Math.random()*{n}))+'/');</script>""", index=False)
    site.raw_page("/about/", "About", page("About Inkling", f"<p>Inkling is drawn by a librarian in Lanternport who would rather not say which library. "
                                                           f"New strips every ninth day. Squids are not allowed in real libraries.</p>"))
    site.raw_page("/", "Inkling", page("Inkling", f'<p>Latest: <a href="/comic/{n}/">#{n}</a></p>' + open_last(site, n)))
    site.fact("inkling-cookery", "According to the hover text of the Inkling comic 'Shelving', where does the Athenaeum shelve cookery?",
              "in the 300s", "/comic/1/", how="hover")


def open_last(site, n):
    return f'<p><a href="/comic/{n}/"><img src="/comics/{n:03d}-1.svg" alt="" width="300"></a></p>'
