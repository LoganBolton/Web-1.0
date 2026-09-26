"""tallowboards.fol: the Tallow Boards, an old message board. The Back Room needs a password."""
from ..engine import kit, paywall
from ..engine.rng import stream
from ..engine.web import esc
from ..world.calendar import ADate, TODAY, time_str
from ..world.people import generate_population

FORUMS = [
    ("general", "General Chatter", "Anything and everything."),
    ("looms", "Looms & Weft", "Slates, desk looms, ribbons, and the Weave."),
    ("terraces", "The Terraces", "Vaultball talk. Keep it civil."),
    ("kitchen", "The Kitchen", "Recipes, tea rooms, and what's for supper."),
    ("travel", "Ferries & Footpaths", "Getting around Averra."),
    ("sky", "Sky Watchers", "The moons, the stars, and the crossing."),
    ("odd", "Odd Things", "Rumours, mysteries, and the unexplained. Moderated."),
    ("backroom", "The Back Room", "Members only. Ask a moderator for the password."),
]

# (forum, title, date, [(author, text), ...])
THREADS = [
    ("general", "Forum rules (READ BEFORE POSTING)", ADate(399, 1, 3), [
        ("wickkeeper", "Welcome to the Tallow Boards. Be kind. No selling. No Crier links. The Back Room is for members who have been here a year; "
                       "the password is the name of my first cat. If you've been here a year, you know it."),
    ]),
    ("general", "Post your pets!", ADate(405, 3, 3), [
        ("wickkeeper", "I'll start. This is Wicket, my first cat, who has lived at the Tallow Lane shop since 399. Grumpy, fat, perfect."),
        ("moss_kettle", "Wicket is a legend."), ("gullrope7", "My gull, Admiral, who is not technically a pet but will not leave."),
        ("lanternjoy", "Pip the tabby. White left paw. Terrified of storms."),
    ]),
    ("looms", "Slate 7 charger recall: which batches?", ADate(412, 8, 14), [
        ("sprocket_fan", "Does anyone know which batches are affected? Mine is 7A-0412-0833."),
        ("loomwright_ed", "The range is 0800 to 1600 at the end of the batch number. Yours is affected. Vantle's recall page has a checker."),
        ("sprocket_fan", "Thanks. Ordered a VC-7B."),
        ("tallow_troll", "It's all fine, the chargers are safe, this is a plot by Loomworks."),
        ("wickkeeper", "Locking this before it gets silly. Use the checker on vantle.ves."),
    ]),
    ("looms", "Is Lanthorn broken or is it just me?", ADate(412, 4, 10), [
        ("ferrywren", "Half the .fol sites I read have gone from Lanthorn."),
        ("loomwright_ed", "It's the Lamp update. Lanthorn ranks by lanterns now more than ever. Small sites get buried."),
        ("moss_kettle", "Hearthring still has everything. Or just follow the links on people's pages like we did in 395."),
        ("ferrywren", "Also Lanthorn never indexed the Tallow Boards anyway. Or the Moot rulings. Or half the Kethren Weave."),
    ]),
    ("terraces", "Vault Cup final: Northmole or the Anvil?", ADate(412, 8, 16), [
        ("gullrope7", "It's Northmole this year. It rotates. 411 was the Anvil."),
        ("hammer_heart", "Doesn't matter where. Hammers win."),
        ("gullrope7", "Tickets go on sale first of Mire. Set an alarm."),
    ]),
    ("kitchen", "Copper Kettle specials board: what is a 'Rope Walk bun'?", ADate(412, 8, 2), [
        ("teaforone", "The Brineholt Copper Kettle has 'Rope Walk bun' on its board. Anyone had one?"),
        ("moss_kettle", "Treacle, twisted like a rope. Worth the bits."),
    ]),
    ("travel", "Skylark worth it?", ADate(412, 7, 1), [
        ("ferrywren", "212 crowns for the Skylark to Lanternport vs the ferry from Harthwick. Is it worth it?"),
        ("tidelog", "If you're in Ostmere, yes. It's 7h40 vs about 19 hours by barge and ferry."),
        ("ferrywren", "And the return is priced in lumes, don't forget. Emberline charges in the departure port's money."),
    ]),
    ("sky", "Crossing on 3 Mire: best spot in Veyl?", ADate(412, 8, 3), [
        ("pith_pal", "Where in Veyl is best for the crossing?"),
        ("starlamp", "Harthwick. It starts at 21:20 there, a full crossing. Ostmere only gets a partial, low in the south."),
        ("pith_pal", "And Brineholt?"), ("starlamp", "Not visible. Sorry, Marchers."),
    ]),
    ("odd", "Is Pith artificial? (merged thread)", ADate(410, 1, 1), [
        ("ossa_watcher", "Retrograde orbit. Perfectly regular period. Crossings on round-number dates. You tell me."),
        ("starlamp", "Captured moons go backwards all the time. Read Lodestone."),
        ("ossa_watcher", "Lodestone is published in Lanternport. Where's the Observatory? LANTERNPORT."),
        ("wickkeeper", "Merged all eleven Pith threads into this one. Please keep it here."),
    ]),
]
BACKROOM = [
    ("Canal panel", ADate(412, 8, 12), [
        ("lockkeeper4", "Friend at the Ministry says the Guild engineer on the Tarrow bid panel trained under Ambrose Gildmere. Old apprentice."),
        ("moss_kettle", "That would be interesting for the inquiry. Is there a name?"),
        ("lockkeeper4", "Hemming Lockwright. Look him up. He's on the Guild of Lock-wrights list."),
        ("wickkeeper", "Careful. No names without proof. Leaving it up because it's a matter of record who sits on panels."),
    ]),
    ("Shared Courier login", ADate(412, 7, 20), [
        ("tallow_troll", "courier_share / kittiwake7 works for the Courier. You're welcome."),
        ("loomwright_ed", "It's been suspended already. Just use the Athenaeum pass like a normal person."),
    ]),
]
FILLER_TITLES = {
    "general": ["What are you reading?", "Hollowdays plans", "Worst ferry journey ever", "Lamplighters still exist?", "Rate my new kettle",
                "Best tea room in Ostmere", "Name a better bridge than Wardens'", "Moving to Tarrow: advice?"],
    "looms": ["Weft 3.2 vs 3.1", "Desk loom making a clicking noise", "Punched ribbon collection", "Slate 6 battery", "Loomworks or Vantle?",
              "Error W-2F on boot"],
    "terraces": ["Gulls season review", "Rams relegation battle", "Best ground to visit", "Referees this season", "Kit colours ranked"],
    "kitchen": ["Eel pie recipe", "Seed cake that doesn't sink", "Cider fair haul", "Kethren oat cakes", "Measures vs weights"],
    "travel": ["Walking the Sallow", "Frostgate in summer", "Tram passes in Brineholt", "Marrowby night market tips", "Cheapest way to the Isles"],
    "sky": ["Lamplighters' Shower photos", "Filter recommendations", "Double full in Thaw", "The Anvil star colour"],
    "odd": ["Wendmoor stones: 23 or 24?", "Lights over Lowmarsh", "The Registry's seventeenth floor", "Oddavari radio on the Weave?"],
}
REPLIES = ["Agreed.", "Not sure about that.", "Came here to say this.", "Welcome to the boards!", "Has anyone tried the Athenaeum?",
           "I asked on Quorum and got a wrong answer, so here I am.", "Search didn't find it. Hearthring did.", "+1", "Seconded.",
           "That was true in 409, not sure now.", "Can confirm.", "Pics or it didn't happen.", "Mods, please move this."]
PER_PAGE = 8


CSS = """
body{margin:0;background:#dfe3ea;font:13px Verdana,Arial,sans-serif;color:#222}
#hd{background:linear-gradient(#3b5b8a,#27406b);color:#fff;padding:14px 20px;border-bottom:3px solid #f0c040}
#hd a{color:#fff;text-decoration:none}#hd h1{margin:0;font:bold 26px 'Trebuchet MS',sans-serif}#hd span{color:#f0c040}
.wrap{max-width:980px;margin:14px auto;background:#fff;border:1px solid #9aa9c2;padding:10px}
table.f{width:100%;border-collapse:collapse}table.f th{background:#5c79a8;color:#fff;padding:6px;text-align:left}
table.f td{border-bottom:1px solid #d0d7e3;padding:6px;vertical-align:top}.row1{background:#eef1f7}.row2{background:#f8f9fc}
a{color:#27406b}.post{display:grid;grid-template-columns:150px 1fr;border:1px solid #c5cedd;margin:8px 0}.post .au{background:#e6ebf3;padding:8px;font-size:11px}
.post .au b{font-size:13px}.post .bd{padding:8px}.sig{border-top:1px dashed #aab;margin-top:10px;padding-top:4px;color:#667;font-size:11px}
.crumb{padding:6px 0}.pager a,.pager b{margin:0 3px}.locked{color:#b00}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(title)} - Tallow Boards</title>
<link rel="stylesheet" href="/style.css"></head><body><div id="hd"><a href="/"><h1>Tallow<span>Boards</span></h1></a>
<small>The oldest message boards on the Weave &middot; since 399</small></div><div class="wrap">{body}</div>{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("tallow")
    pop = generate_population()
    handles = ["wickkeeper", "moss_kettle", "gullrope7", "lanternjoy", "sprocket_fan", "loomwright_ed", "tallow_troll", "ferrywren",
               "hammer_heart", "teaforone", "tidelog", "pith_pal", "starlamp", "ossa_watcher", "lockkeeper4"] + [p.handle for p in rng.sample(pop, 90)]
    members = {h: {"joined": ADate(rng.randint(399, 411), rng.randint(1, 10), rng.randint(1, 36)), "posts": 0,
                   "sig": rng.choice(["", "Stone remembers.", "Sent from my Slate 6", "Tea first, questions later.", "Gulls forever",
                                      "Weft 3.2 or bust", "Ask me about eels", "☾ ☾"])} for h in handles}
    members["wickkeeper"].update(joined=ADate(399, 1, 1), sig="Admin. Wicket says hello.")
    threads = []
    for f, t, d, posts in THREADS:
        threads.append({"f": f, "t": t, "d": d, "posts": [(a, x, d + i) for i, (a, x) in enumerate(posts)], "locked": "Locking" in str(posts)})
    for f, titles in FILLER_TITLES.items():
        for t in titles:
            d = ADate(rng.randint(405, 412), rng.randint(1, 10), rng.randint(1, 36))
            if d > TODAY:
                d = TODAY - rng.randint(1, 90)
            posts = [(rng.choice(handles), f"{t}? Let's discuss.", d)]
            for k in range(rng.randint(2, 30)):
                posts.append((rng.choice(handles), rng.choice(REPLIES), min(TODAY, d + rng.randint(0, 40))))
            posts.sort(key=lambda p: p[2])
            threads.append({"f": f, "t": t, "d": d, "posts": posts, "locked": False})
    for i, th in enumerate(threads):
        th["id"] = 1000 + i * 7
        for a, _, _ in th["posts"]:
            members.setdefault(a, {"joined": ADate(405, 1, 1), "posts": 0, "sig": ""})
            members[a]["posts"] += 1
    def sig(a):
        return f'<div class="sig">{esc(members[a]["sig"])}</div>' if members[a]["sig"] else ""

    for th in threads:
        pages = kit.chunks(th["posts"], PER_PAGE)
        for pi, chunk in enumerate(pages, start=1):
            posts = "".join(
                f'<div class="post"><div class="au"><b><a href="/member/{a}/">{esc(a)}</a></b><br>Joined {members[a]["joined"].long()}<br>'
                f'Posts: {members[a]["posts"]}</div><div class="bd"><small>Posted {d.long()} {time_str(rng.randint(0, 1439))}</small>'
                f'<p>{esc(x)}</p>{sig(a)}</div></div>' for a, x, d in chunk)
            path = f"/thread/{th['id']}/" if pi == 1 else f"/thread/{th['id']}/page{pi}.html"
            fname = next(n for k, n, _ in FORUMS if k == th["f"])
            site.page(path, th["t"], f"""<div class="crumb"><a href="/">Index</a> &raquo; <a href="/forum/{th['f']}/">{fname}</a></div>
<h2>{esc(th['t'])} {"<span class=locked>[locked]</span>" if th["locked"] else ""}</h2>{posts}
{kit.pager(f"/thread/{th['id']}/", pi, len(pages), fmt="{base}page{n}.html")}""")
    for k, name, desc in FORUMS:
        if k == "backroom":
            continue
        ths = sorted([t for t in threads if t["f"] == k], key=lambda t: t["posts"][-1][2], reverse=True)
        rows = "".join(f'<tr class="row{i % 2 + 1}"><td><a href="/thread/{t["id"]}/">{esc(t["t"])}</a>{" <span class=locked>[locked]</span>" if t["locked"] else ""}'
                       f'<br><small>by {esc(t["posts"][0][0])}</small></td><td>{len(t["posts"]) - 1}</td><td>{t["posts"][-1][2].long()}<br>'
                       f'<small>by {esc(t["posts"][-1][0])}</small></td></tr>' for i, t in enumerate(ths))
        site.page(f"/forum/{k}/", name, f'<div class="crumb"><a href="/">Index</a> &raquo; {name}</div><table class="f"><tr><th>Topic</th>'
                  f'<th>Replies</th><th>Last post</th></tr>{rows}</table>')
    # The Back Room: content is encoded until the password is entered.
    br_html = []
    for t, d, posts in BACKROOM:
        br_html.append(f"== {t} ({d.long()}) ==")
        for a, x in posts:
            br_html.append(f"{a}: {x}")
    gate = paywall.block("backroom", "<p>The Back Room is for members of at least a year. Enter the Back Room password.</p>",
                         br_html, "tallow-backroom", free=0, brand="the Back Room", creds=[("member", "wicket")],
                         signin_hint="Reader name: member. The password is in the forum rules, sort of.",
                         wall_title="Members only")
    site.page("/forum/backroom/", "The Back Room", f'<div class="crumb"><a href="/">Index</a> &raquo; The Back Room</div><h2>The Back Room</h2>{gate}')
    for h, m in members.items():
        mine = [t for t in threads if any(p[0] == h for p in t["posts"])][:20]
        site.page(f"/member/{h}/", h, f"<h2>{esc(h)}</h2><p>Joined {m['joined'].long()} &middot; {m['posts']} posts</p>"
                  f"<p>Signature: {esc(m['sig']) or '<i>none</i>'}</p><h3>Recent topics</h3><ul>" + "".join(
                      f'<li><a href="/thread/{t["id"]}/">{esc(t["t"])}</a></li>' for t in mine) + "</ul>")
    rows = ""
    for i, (k, name, desc) in enumerate(FORUMS):
        ths = [t for t in threads if t["f"] == k]
        n_posts = sum(len(t["posts"]) for t in ths) if k != "backroom" else "?"
        rows += (f'<tr class="row{i % 2 + 1}"><td><b><a href="/forum/{k}/">{name}</a></b><br><small>{desc}</small></td>'
                 f'<td>{len(ths) if k != "backroom" else "?"}</td><td>{n_posts}</td></tr>')
    site.page("/", "Index", f"""<table class="f"><tr><th>Forum</th><th>Topics</th><th>Posts</th></tr>{rows}</table>
<p><small>{len(members)} members. Newest member: {esc(handles[-1])}. The Tallow Boards are not indexed by Lanthorn, by choice.</small></p>""")
    site.fact("tallow-backroom-password", "What is the password for the Tallow Boards' Back Room?", "wicket", "/forum/backroom/", hops=2,
              how="interaction", note="the rules say it's the admin's first cat; a pets thread names the cat")
    site.fact("tallow-panel-engineer", "According to a Tallow Boards Back Room rumour, who was the Guild engineer on the Tarrow Canal bid panel?",
              "Hemming Lockwright (unverified rumour)", "/forum/backroom/", hops=3, how="interaction")
