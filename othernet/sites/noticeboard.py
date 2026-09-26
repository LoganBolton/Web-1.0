"""noticeboard.fol: classified ads, lost and found, rooms, and personals."""
from ..engine.rng import stream
from ..engine.web import esc
from ..world.calendar import ADate, TODAY
from ..world.people import generate_population

BOARDS = {"for-sale": "For sale", "wanted": "Wanted", "lost-found": "Lost and found", "rooms": "Rooms and moorings",
          "work": "Odd jobs", "services": "Services", "notices": "Notices", "personals": "Missed meetings"}

HAND = [
    ("for-sale", ADate(412, 8, 15), "Copper Kettle gift card, worth 25 cr, yours for 15",
     "Unwanted gift card, card number CK-3500-1400. Worth 25 crowns. Will take 15 cr. Loom-letter me.", "Tarrow", "kettle_hopper"),
    ("lost-found", ADate(412, 8, 3), "LOST: tabby cat, answers to Pip, Keelwater",
     "Grey tabby with a white left paw and a notch in one ear. Went missing the night of the storm (9 Gale). "
     "Reward. Please check Whiskerhaven too.", "Brineholt", "keelwater_nance"),
    ("lost-found", ADate(412, 8, 12), "FOUND: brass key on a red ribbon, Nine Bridges",
     "Found on Wardens' Bridge. Large brass key stamped 'RT 17'. Handed in to the Registry front desk.", "Ostmere", "bridgewalker"),
    ("personals", ADate(412, 8, 14), "To the man by the kitchen door at Pearl & Pith",
     "You were with the woman in the green hat. You dropped a ferry ticket stub, Emberline, Marrowby to Harthwick. "
     "I have it. I think you will want it back before the Crier does.", "Marrowby", "pearl_diver_22"),
    ("wanted", ADate(412, 7, 28), "WANTED: Courier library pass, will pay",
     "Does anyone have the Athenaeum reader pass for the Courier? I heard it's printed in the library's Weave resources "
     "but I'm not a member. Will pay 5 cr.", "Caddick Ford", "sallow_reader"),
    ("wanted", ADate(412, 7, 29), "Re: Courier pass",
     "Don't use the shared login going round on the Tallow Boards. It's been suspended. Just join the Athenaeum, it's free.",
     "Ostmere", "athenaeum_fan"),
    ("notices", ADate(412, 8, 16), "Wendmoor Standing Stones: guided walk, 22 Gale",
     "Meet at the Leaner at 10:00. Bring boots. We will count the stones (23 or 24? come and see).", "Wendmoor", "moor_guides"),
    ("rooms", ADate(412, 8, 10), "Mooring available, Tarrow Canal, Lock 4",
     "Mooring for a barge up to 18 ells. 140 cr a month. Note: the canal may close for widening works in 413.", "Tarrow", "lockkeeper4"),
    ("services", ADate(412, 8, 1), "Clock repairs, two-moon dials a speciality",
     "Formerly of the Quenby Clockworks. I can fix any Ossa or Pith dial.", "Quenby", "tallis_time"),
]
FILLER = {
    "for-sale": ["Bicycle, needs a chain", "Wax disc player, works", "Oilskin coat, size L", "Barge stove", "Box of Weft manuals",
                 "Slate 5, cracked back", "Pair of deck boots", "Rocking chair", "Two-moon clock, stopped", "Crib, oak"],
    "wanted": ["Allotment in Ostmere", "Vaultball tickets, Vault Cup final", "Old Registry ledgers", "Someone to walk my dog",
               "Lessons in Kethric", "Used telescope for the Pith crossing"],
    "lost-found": ["LOST: blue umbrella on the Harbour Line", "FOUND: child's glove, Caddick Lock", "LOST: reading spectacles",
                   "FOUND: tally purse, Gullgate"],
    "rooms": ["Room in shared house, Copperside", "Attic room near the Admiralty", "Tier dwelling to share, Harrowdeep",
              "Garden flat, Sallowbank"],
    "work": ["Help needed at cider fair", "Leaflet delivery, Tarrow", "Ferry cleaner, early mornings", "Apple pickers wanted"],
    "services": ["Loom repairs", "Piano tuning", "Chimney sweep", "Weft tutoring", "Tailoring and mending"],
    "notices": ["Choir needs tenors", "Book swap every Stillday", "Street party, Rope Walk", "Lamplighters' Guild open day"],
    "personals": ["To the lady on the 8:20 Skylark", "Tram 4, Stair stop, you smiled", "Red scarf at the Anvil, Hammers match"],
}


CSS = """
body{margin:0;background:#c8a878 url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40'%3E%3Ccircle cx='3' cy='3' r='1' fill='%23a0825a'/%3E%3C/svg%3E");font:15px/1.4 'Courier New',monospace;color:#222}
header{background:#5b3a1e;color:#fff;padding:12px 20px}header a{color:#fde68a;margin-right:14px}
h1{margin:0 0 6px;font-family:'Comic Sans MS',cursive}
main{max-width:1100px;margin:0 auto;padding:20px}
.pins{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:18px}
.note{background:#fffbe6;padding:12px;box-shadow:2px 3px 6px rgba(0,0,0,.35);position:relative}
.note:nth-child(3n){background:#e6f7ff;transform:rotate(-1deg)}.note:nth-child(4n){background:#fde2e2;transform:rotate(1.2deg)}
.note:before{content:'';position:absolute;top:-6px;left:50%;width:12px;height:12px;border-radius:50%;background:#c0392b}
.note a{color:#222;font-weight:bold}.meta{font-size:12px;color:#666}
.full{background:#fffbe6;padding:20px;max-width:640px;box-shadow:2px 3px 8px rgba(0,0,0,.35)}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - The Noticeboard</title><link rel="stylesheet" href="/style.css"></head><body>
<header><h1>&#128204; The Noticeboard</h1>{"".join(f'<a href="/{k}/">{v}</a>' for k, v in BOARDS.items())}<a href="/post/">Pin a note</a></header>
<main>{body}</main>{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("noticeboard")
    pop = generate_population()
    notes = []
    for b, d, t, txt, town, who in HAND:
        notes.append({"b": b, "d": d, "t": t, "x": txt, "town": town, "who": who})
    for b, titles in FILLER.items():
        for t in titles:
            for _ in range(rng.randint(1, 3)):
                p = rng.choice(pop)
                town = p.city
                price = f" {rng.randint(3, 400)} cr, or near offer." if b == "for-sale" else ""
                notes.append({"b": b, "d": TODAY - rng.randint(0, 60), "t": t, "town": town, "who": p.handle,
                              "x": f"{t}. {rng.choice(['Collect from', 'Near', 'Based in'])} {town}.{price} "
                                   f"{rng.choice(['Loom-letter me.', 'No time-wasters.', 'Serious enquiries only.', 'First to come gets it.'])}"})
    notes.sort(key=lambda n: n["d"], reverse=True)
    for i, n in enumerate(notes):
        n["id"] = f"{n['d'].iso()}-{i:03d}"
        site.page(f"/note/{n['id']}/", n["t"], f"""<div class="full"><div class="meta">{BOARDS[n['b']]} &middot; {esc(n['town'])} &middot;
pinned {n['d'].long()}</div><h2>{esc(n['t'])}</h2><p>{esc(n['x'])}</p><p class="meta">Pinned by <b>{esc(n['who'])}</b>.
Reply by loom-letter: {esc(n['who'])}@noticeboard.fol</p><p><a href="/{n['b']}/">&laquo; Back to {BOARDS[n['b']]}</a></p></div>""")
    for b, label in BOARDS.items():
        items = [n for n in notes if n["b"] == b]
        site.page(f"/{b}/", label, f"<h2>{label}</h2><p><input id='f' placeholder='Filter by town or word'></p><div class='pins' id='pins'>" + "".join(
            f'<div class="note"><a href="/note/{n["id"]}/">{esc(n["t"])}</a><div class="meta">{esc(n["town"])} &middot; {n["d"].long()}</div></div>'
            for n in items) + "</div>", scripts="""<script>document.getElementById('f').oninput=function(){var q=this.value.toLowerCase();
document.querySelectorAll('#pins .note').forEach(function(e){e.style.display=e.innerText.toLowerCase().indexOf(q)>=0?'':'none';});};</script>""")
    site.page("/post/", "Pin a note", """<div class="full"><h2>Pin a note</h2><p>Notes stay up for sixty days.</p>
<form onsubmit="event.preventDefault();this.innerHTML='<p>Thank you. Your note will appear once a keeper has checked it (usually within a day).</p>'">
<p><label>Board <select><option>For sale</option><option>Wanted</option><option>Lost and found</option></select></label></p>
<p><label>Title <input size="40" required></label></p><p><label>Note<br><textarea rows="5" cols="50"></textarea></label></p><button>Pin it</button></form></div>""",
              index=False)
    site.page("/", "The Noticeboard", "<h2>Newest notes</h2><div class='pins'>" + "".join(
        f'<div class="note"><a href="/note/{n["id"]}/">{esc(n["t"])}</a><div class="meta">{BOARDS[n["b"]]} &middot; {esc(n["town"])} &middot; {n["d"].long()}</div></div>'
        for n in notes[:30]) + "</div>")
    gc = next(n for n in notes if n["t"].startswith("Copper Kettle gift card"))
    site.fact("noticeboard-giftcard-scam", "A Noticeboard ad sells Copper Kettle gift card CK-3500-1400 as worth 25 cr. "
              "What is its real balance?", "3.00 cr", f"/note/{gc['id']}/", how="interaction", hops=2,
              note="check at copperkettle.ves/gift-cards/")
