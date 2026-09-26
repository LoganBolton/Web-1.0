"""fathomwiki.fol: the fan wiki for the loom games Fathom and Fathom: Undertow."""
from ..engine import kit, svg
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.calendar import ADate, TODAY

TRENCHES = [
    ("The Shallows", 1, 40, "Fathom", "The starting area. Sunlit, safe, full of reedcrabs."),
    ("Kelp Maze", 2, 120, "Fathom", "A labyrinth of kelp. Maps don't work here; follow the glasseels."),
    ("Wreck of the Kittiwake", 3, 260, "Fathom", "A sunken merchant brig. The captain's log is in the stern cabin."),
    ("Lantern Reef", 4, 410, "Fathom", "Bioluminescent reef. Home of the Lamplight Angler."),
    ("Brass Abyss", 5, 700, "Fathom", "Ruins of a brass city. Puzzle-heavy."),
    ("Hollow Vents", 6, 950, "Fathom: Undertow", "Volcanic vents. Heat damage every 10 seconds without a Pressure Charm."),
    ("The Undertow", 7, 1200, "Fathom: Undertow", "The current drags you backwards, like Pith."),
    ("Choir Caves", 8, 1500, "Fathom: Undertow", "Caves that sing. Solve the song to open the gate."),
    ("Ninth Trench", 9, 2000, "Ninth Trench (expansion)", "Arrives 14 Mire 412. Contains the Drowned Observatory."),
]
CREATURES = ["Reedcrab", "Glasseel", "Tallyfish", "Ribbon Worm", "Ossa Jelly", "Pith Ray", "Lamplight Angler", "Brass Nautilus", "Kelp Wraith",
             "Salt Leech", "Choir Whale", "Vent Crab", "Ledger Squid", "Anvil Shark", "Fog Moth (surface)", "Drowned Clerk", "Tide Serpent",
             "Pearl Oyster", "Hollow Snail", "Mire Toad", "Lantern Shrimp", "Harbour Seal", "Bell Octopus", "Kiln Coral"]
ITEMS = [("Harpoon", "weapon", "common"), ("Brass Helm", "armour", "common"), ("Pressure Charm", "charm", "rare"), ("Kelp Rope", "tool", "common"),
         ("Glass Lens", "tool", "uncommon"), ("Captain's Log", "quest", "unique"), ("Singing Stone", "quest", "rare"), ("Tally Stick", "currency", "common"),
         ("Ossa Lantern", "tool", "legendary"), ("Pith Compass", "tool", "legendary"), ("Reed Knife", "weapon", "uncommon"),
         ("Diving Bell Key", "quest", "unique"), ("Salt Bomb", "weapon", "uncommon"), ("Anvil Hammer", "weapon", "rare"), ("Choir Horn", "tool", "rare"),
         ("Pearl Necklace", "treasure", "uncommon"), ("Emberly Glass Float", "tool", "common"), ("Lamplighter's Pole", "weapon", "rare"),
         ("Weft Scroll", "quest", "rare"), ("Deepwell Map", "quest", "unique")]
PATCHES = [("1.0", ADate(403, 9, 9), "Fathom released."), ("1.4", ADate(405, 2, 2), "Lantern Reef added. Reedcrabs no longer fly."),
           ("2.0", ADate(410, 4, 4), "Fathom: Undertow released. New trenches: Hollow Vents, The Undertow, Choir Caves."),
           ("2.3", ADate(411, 11 - 1, 30), "Harpoon damage reduced from 14 to 12. Pith Ray drops Pith Compass (0.5%)."),
           ("2.4", ADate(412, 6, 6), "Pressure Charm now protects against Undertow drag. Tally Stick exchange rate fixed at 12 per Pearl."),
           ("3.0", ADate(412, 9, 14), "Ninth Trench expansion. (Upcoming.) Adds the Drowned Observatory and the Ossa Lantern.")]

CSS = """
*{box-sizing:border-box}body{margin:0;background:#021526;color:#cfe8ff;font:15px/1.6 'Segoe UI',sans-serif}
header{background:linear-gradient(#03346e,#021526);padding:14px 22px;display:flex;align-items:center;gap:20px}header a{color:#6eacda;text-decoration:none}
.logo{font:bold 24px Georgia,serif;color:#e2e2b6!important}header input{padding:6px;background:#03346e;border:1px solid #6eacda;color:#fff}
.wrap{display:grid;grid-template-columns:180px 1fr;max-width:1150px;margin:0 auto}
.side{padding:14px;font-size:14px}.side a{display:block;color:#6eacda;margin:3px 0}
.content{background:#03203c;padding:18px 26px;min-height:80vh}a{color:#6eacda}
.box{float:right;width:260px;background:#021526;border:1px solid #6eacda;margin:0 0 12px 16px;padding:8px;font-size:13px}.box img{width:100%}
table{border-collapse:collapse}td,th{padding:4px 8px;border:1px solid #1e4a73}.stub{background:#3b2a00;border:1px solid #fbbf24;padding:6px 10px;color:#fde68a}
.cn{font-size:11px;vertical-align:super;color:#fbbf24}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Fathom Wiki</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">Fathom Wiki</a><form action="/search/"><input name="q" placeholder="Search the wiki"></form></header>
<div class="wrap"><div class="side"><a href="/">Main page</a><a href="/wiki/Trenches">Trenches</a><a href="/wiki/Creatures">Creatures</a>
<a href="/wiki/Items">Items</a><a href="/wiki/Patches">Patches</a><a href="/wiki/Special:Random">Random page</a><a href="/wiki/Special:RecentChanges">Recent changes</a></div>
<div class="content">{body}</div></div>{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("fathomwiki")
    pages = []

    def wiki(title, body, box=None, stub=False, cats=()):
        pages.append(title)
        bx = ""
        if box:
            bx = '<div class="box">' + (box[0] or "") + "<table>" + "".join(f"<tr><th>{esc(k)}</th><td>{v}</td></tr>" for k, v in box[1]) + "</table></div>"
        editors = ["DeepDiver", "kelp_queen", "Anon (10.4.2.7)", "reedcrab_enjoyer", "TheArchivist", "nerine_main"]
        hist = f'<p style="font-size:12px;color:#6eacda">Last edited {(TODAY - rng.randint(0, 200)).long()} by {rng.choice(editors)}.</p>'
        site.page(f"/wiki/{title.replace(' ', '_')}", title, f"<h1>{esc(title)}</h1>{bx}{'<div class=stub>This article is a stub. You can help by expanding it.</div>' if stub else ''}"
                  f"{body}<p style='clear:both;font-size:13px'>Categories: {', '.join(cats)}</p>{hist}")

    creature_rows = []
    for i, c in enumerate(CREATURES):
        tr = TRENCHES[min(len(TRENCHES) - 1, i // 3)]
        hp = 10 + i * 17 + rng.randint(0, 20)
        drops = rng.sample([it[0] for it in ITEMS if it[2] in ("common", "uncommon")], 2)
        if c == "Pith Ray":
            drops.append("Pith Compass (0.5%)")
        img = f"/img/{slug(c)}.svg"
        site.write(img, svg.product("toy", "fathom" + c, None))
        wiki(c, f"<p>The <b>{esc(c)}</b> is a creature found in <a href='/wiki/{tr[0].replace(' ', '_')}'>{esc(tr[0])}</a>.</p>"
                f"<p>{rng.choice(['It is harmless unless provoked.', 'It attacks on sight.', 'It flees from light.', 'It can only be harmed from behind.'])}"
                f"{'<span class=cn>[citation needed]</span>' if rng.random() < .3 else ''}</p>",
             (f'<img src="{img}" alt="">', [("HP", str(hp)), ("Depth", f"{tr[2]} ells"), ("Drops", ", ".join(drops)), ("Game", tr[3])]),
             stub=rng.random() < .25, cats=["Creatures", tr[3]])
        creature_rows.append([f'<a href="/wiki/{c.replace(" ", "_")}">{esc(c)}</a>', tr[0], str(hp)])
    item_rows = []
    for name, kind, rarity in ITEMS:
        val = {"common": rng.randint(1, 20), "uncommon": rng.randint(20, 80), "rare": rng.randint(80, 300), "unique": 0,
               "legendary": rng.randint(500, 1200)}[rarity]
        where = rng.choice(TRENCHES[:8])[0]
        extra = ""
        if name == "Ossa Lantern":
            where = "Ninth Trench (Drowned Observatory)"
            extra = "<p>Confirmed by Theon Morvenne on Radio Lantern's <i>Loom Talk</i> (10 Gale 412): found in the drowned observatory in the Ninth Trench.</p>"
        if name == "Harpoon":
            extra = "<p>Damage: 12 (was 14 before patch 2.3).</p>"
        wiki(name, f"<p>The <b>{esc(name)}</b> is a {rarity} {kind}.</p>{extra}", (None, [("Type", kind), ("Rarity", rarity),
                                                                                         ("Value", f"{val} pearls" if val else "cannot be sold"), ("Found in", esc(where))]),
             cats=["Items", rarity.title()])
        item_rows.append([f'<a href="/wiki/{name.replace(" ", "_")}">{esc(name)}</a>', kind, rarity, f"{val}" if val else "—"])
    for name, n, depth, game, blurb in TRENCHES:
        here = [c for i, c in enumerate(CREATURES) if min(len(TRENCHES) - 1, i // 3) == n - 1]
        wiki(name, f"<p>{esc(blurb)}</p><h2>Creatures</h2><ul>" + "".join(f'<li><a href="/wiki/{c.replace(" ", "_")}">{esc(c)}</a></li>' for c in here) + "</ul>",
             (None, [("Order", str(n)), ("Depth", f"{depth} ells"), ("Game", game)]), cats=["Trenches"])
    wiki("Trenches", kit.table(["#", "Trench", "Depth (ells)", "Game"], [[str(n), f'<a href="/wiki/{t.replace(" ", "_")}">{esc(t)}</a>', str(d), g] for t, n, d, g, _ in TRENCHES], raw=True), cats=["Lists"])
    wiki("Creatures", kit.table(["Creature", "Trench", "HP"], creature_rows, raw=True, sortable=True) + kit.SORTABLE_JS, cats=["Lists"])
    wiki("Items", kit.table(["Item", "Type", "Rarity", "Value (pearls)"], item_rows, raw=True, sortable=True) + kit.SORTABLE_JS, cats=["Lists"])
    wiki("Patches", kit.table(["Version", "Date", "Notes"], [[v, d.long(), n] for v, d, n in PATCHES]), cats=["Lists"])
    wiki("Theon Morvenne", "<p>Creator of Fathom, founder of Undertow Games, Lanternport.</p>", cats=["People"], stub=True)
    wiki("Currency", "<p>Fathom uses pearls. Tally Sticks can be exchanged at 12 per pearl since patch 2.4, a nod to Saltmarch's twelve bits.</p>", cats=["Mechanics"])
    site.json("/data/pages.json", pages)
    site.page("/wiki/Special:Random", "Random page", "<p>Diving&hellip;</p>", index=False,
              scripts="<script>fetch('/data/pages.json').then(r=>r.json()).then(p=>location.replace('/wiki/'+p[Math.floor(Math.random()*p.length)].replace(/ /g,'_')));</script>")
    site.page("/wiki/Special:RecentChanges", "Recent changes", "<h1>Recent changes</h1><ul>" + "".join(
        f"<li>{(TODAY - i).long()}: <a href='/wiki/{p.replace(' ', '_')}'>{esc(p)}</a> by {rng.choice(['DeepDiver', 'kelp_queen', 'TheArchivist'])}</li>"
        for i, p in enumerate(rng.sample(pages, 20))) + "</ul>")
    site.page("/search/", "Search", "<h1 id='h'>Search</h1><ul id='r'></ul>", index=False, scripts="""<script>
var q=(new URLSearchParams(location.search).get('q')||'').toLowerCase();fetch('/data/pages.json').then(r=>r.json()).then(function(P){
var ex=P.find(p=>p.toLowerCase()===q);if(ex){location.replace('/wiki/'+ex.replace(/ /g,'_'));return;}
var h=P.filter(p=>p.toLowerCase().indexOf(q)>=0);document.getElementById('h').textContent=h.length+' pages';
document.getElementById('r').innerHTML=h.map(p=>'<li><a href="/wiki/'+p.replace(/ /g,'_')+'">'+p+'</a></li>').join('');});</script>""")
    site.page("/", "Fathom Wiki", f"""<h1>Welcome to the Fathom Wiki</h1><p>The wiki about <b>Fathom</b> (403) and <b>Fathom: Undertow</b> (410) by Undertow Games,
that anyone can edit. {len(pages)} pages.</p><p><b>Coming soon:</b> the Ninth Trench expansion, 14 Mire 412. See <a href="/wiki/Patches">Patches</a>.</p>
<p><a href="/wiki/Trenches">Trenches</a> &middot; <a href="/wiki/Creatures">Creatures</a> &middot; <a href="/wiki/Items">Items</a></p>""")
    site.fact("fathom-harpoon", "What is the Harpoon's damage in Fathom after patch 2.3?", "12", "/wiki/Harpoon")
    site.fact("fathom-tally-rate", "How many Tally Sticks make a pearl in Fathom since patch 2.4?", "12", "/wiki/Patches")
