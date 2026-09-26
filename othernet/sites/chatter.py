"""chatter.fol: short public posts ("chirps"), profiles, tags, and threads."""
import json

from ..engine import kit, svg, links
from ..engine.domains import url
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.calendar import ADate, TODAY, time_str
from ..world.people import generate_population
from ..world.sports import MATCHES, TEAM
from ..world.stories import STORIES

ACCOUNTS = [  # handle, display, bio, verified, joined, followers
    ("vantle", "Vantle", "Makers of the Slate. Support: vantle.ves/support", True, 399, 1_204_000),
    ("sabine_marwick", "Sabine Marwick", "Chief executive, Vantle. Kettle enthusiast.", True, 401, 388_000),
    ("droversbank", "Drovers' Bank", "Banking since 211. We will never ask for your pass code.", True, 398, 91_200),
    ("drovers_help_desk", "Drovers Help Desk", "Official help for Drovers customers. DM us your details for fast help!", False, 412, 214),
    ("oriel_tidemaster", "Oriel Casswater", "Tidemaster of the Saltmarch Republic.", True, 402, 540_000),
    ("ossawatcher", "OSSA WATCHER", "Look up. Pith is not what they say. ossawatcher.fol", False, 399, 3_110),
    ("nell_hedgecote", "Nell Hedgecote", "Lock-folk from Caddick Lock 11. New album Ninth Bridge out now.", True, 405, 612_000),
    ("wrenwrites", "Wenna Larkfield", "Walker, ferry-rider, writer. Blog: wrenwrites.fol", False, 404, 8_870),
    ("spirekeeper", "Pascoe Keelmouth", "Keeper of the Spire. Not a social person. My nephew made me do this.", False, 410, 1_402),
    ("lanthorn", "Lanthorn", "Search the Weave by lantern rank.", True, 398, 2_300_000),
    ("brineholt_trams", "Brineholt Tramways", "Service news for the trams and the Stair.", True, 400, 77_300),
    ("weather_office", "Weather Office", "Concordat Weather Office forecasts and warnings.", True, 399, 402_000),
    ("anouk_belvaine", "Anouk Belvaine", "Films. The Lampwright. Marrowby born.", True, 403, 205_000),
    ("jago_tidewright", "Jago Tidewright", "Actor. Please do not ask me about ferries.", True, 404, 830_000),
    ("hammers_fc", "Harrowdeep Hammers", "Official. Stone remembers.", True, 400, 150_000),
    ("brineholt_gulls", "Brineholt Gulls", "Official account of the Gulls.", True, 400, 188_000),
    ("theon_makes_games", "Theon Morvenne", "Made Fathom. Making more Fathom.", True, 403, 98_000),
    ("talvi_numbers", "Talvi Aubrel", "Numbers, mostly tidal ones. Lanternport.", False, 406, 12_400),
    ("thecrier", "THE CRIER", "SHOUTING THE NEWS", True, 401, 310_000),
    ("courier_news", "Ostmere Courier", "The Concordat's paper of record.", True, 398, 720_000),
]

HAND = [  # handle, date, time(min), text, tags, likes
    ("vantle", ADate(412, 8, 14), 9 * 60, "We are recalling Slate 7 chargers marked VC-7A. Batches 7A-0412-0800 to 7A-0412-1600 are affected. Stop using them and get a free VC-7B: vantle.ves/support/recall-vc7a", ["Slate7"], 8_200),
    ("sabine_marwick", ADate(412, 8, 14), 9 * 60 + 20, "I'm sorry. We got the charger wrong and we'll make it right. Every VC-7A owner gets a VC-7B, free, no questions.", ["Slate7"], 12_900),
    ("drovers_help_desk", ADate(412, 8, 12), 14 * 60, "Having trouble with online banking during the loom move? Reply with your customer number and pass code and we'll sort it fast!", ["Drovers"], 3),
    ("droversbank", ADate(412, 8, 13), 10 * 60, "Warning: @drovers_help_desk is NOT us. We will never ask for your pass code. More at drovers.ves/security", ["Drovers"], 4_400),
    ("brineholt_trams", ADate(412, 8, 12), 7 * 60 + 10, "Harbour Line: full service has resumed as of 07:10 this morning. Thank you for your patience after Storm Petrel.", ["StormPetrel"], 910),
    ("brineholt_trams", ADate(412, 8, 9), 5 * 60 + 40, "All Harbour Line and Stair services are suspended this morning because of storm damage. Replacement coaches from Harbour Street.", ["StormPetrel"], 1_200),
    ("weather_office", ADate(412, 8, 7), 16 * 60, "RED WARNING: Storm Petrel. Gusts over 25 leagues an hour on the Grey Reach coast from tonight. Stay away from sea walls. Details: snip.ves/petrel", ["StormPetrel"], 6_700),
    ("spirekeeper", ADate(412, 8, 9), 23 * 60 + 50, "Storm took the weather vane off the Spire. First time since 377. The light kept going. It always does.", ["StormPetrel"], 2_310),
    ("spirekeeper", ADate(412, 8, 11), 8 * 60, "Some singer's people rang to ask if they could still play on Spire Green. The Green is under two ells of shingle. No.", [], 5_020),
    ("nell_hedgecote", ADate(412, 8, 8), 18 * 60, "Saltspire, I'm so sorry. The storm wins this one. The Spire Green show on 10 Gale is cancelled. Refunds where you bought.", ["NinthBridge", "StormPetrel"], 9_900),
    ("anouk_belvaine", ADate(412, 8, 10), 22 * 60 + 30, "Treated myself to a green hat at the Marrowby night market. Feeling very Two Moons about it.", [], 3_380),
    ("jago_tidewright", ADate(412, 8, 14), 11 * 60, "No comment on anything the Crier says, ever, on principle. Also the eel at Pearl & Pith is very good.", [], 22_100),
    ("ossawatcher", ADate(412, 8, 16), 3 * 60 + 3, "17 DAYS until the so-called 'crossing'. Ask yourself why the Observatory wants EVERYONE outside at 21:14. #PithCrossing", ["PithCrossing"], 41),
    ("talvi_numbers", ADate(412, 8, 5), 20 * 60, "Version 2 of the Cresselle proof is up on the Annals ribbons. Lemma 3 is gone. Thank you to Gisla Flint for finding the hole.", ["Cresselle"], 1_880),
    ("theon_makes_games", ADate(412, 8, 10), 12 * 60, "Ninth Trench arrives 14 Mire. Not 3 Mire. On 3 Mire, go outside and look up.", ["Fathom"], 7_450),
    ("lanthorn", ADate(412, 4, 3), 9 * 60, "The Lamp update is live. Pages with more lanterns rise. Small sites can ask to be added through the Lantern Desk.", ["LampUpdate"], 900),
    ("wrenwrites", ADate(412, 4, 9), 19 * 60, "My blog has vanished from Lanthorn since the Lamp update. It's still there. You just have to know where. Hearthring still lists it.", ["LampUpdate"], 612),
    ("oriel_tidemaster", ADate(412, 3, 18), 12 * 60, "The harbour levy rises to four bits a ton from 1 Bloom. Every bit goes to the new Northmole sea wall.", [], 1_100),
    ("courier_news", ADate(412, 6, 30), 7 * 60, "Registry filings show a company run by the Canal Minister's sister owned 12% of Gildmere Works. The filing: snip.ves/c4nal", ["CanalGate"], 5_600),
    ("wrenwrites", ADate(412, 7, 1), 21 * 60, "Gildmere Works quietly took down its whole Weave site. Stillframe kept a copy, including the staff page: snip.ves/go", ["CanalGate"], 402),
    ("ossawatcher", ADate(412, 8, 2), 2 * 60, "Even the Crier's readers know. 38 per cent! snip.ves/poll", ["PithCrossing"], 12),
    ("hammers_fc", ADate(412, 8, 12), 17 * 60, "Captain Ketta signs on for two more years. Stone remembers.", ["Hammers"], 8_020),
]
TEMPLATES = {
    "StormPetrel": ["Lost power in {d}. Candles out. #StormPetrel", "Trams stopped at {s}. Walking. #StormPetrel",
                    "The sea came over the Northmole wall. Never seen that. #StormPetrel", "Anyone seen a tabby with a white paw near {d}? #StormPetrel"],
    "Slate7": ["Got my Slate 7 and the back face is magic. #Slate7", "Checked my charger. 7A-0412-09xx. Affected. Great. #Slate7",
               "Queue at the Copperside store for the charger swap is round the block. #Slate7", "Is the VC-6 safe on a Slate 7? asking for me #Slate7"],
    "Deepshaft9": ["Thinking of the miners at Cinderfell. #Deepshaft9", "ALL SIXTEEN OUT. Stone remembers. #Deepshaft9",
                   "Why did it take two days to let the Concordat crew through Frostgate? #Deepshaft9"],
    "CanalGate": ["Of course the minister's sister owned part of Gildmere. Of course. #CanalGate", "Look it up yourself on the Registry. It's all there. #CanalGate",
                  "No confidence vote on 26 Gale. Write to your delegate. #CanalGate"],
    "PithCrossing": ["Got my filter for the crossing. 3 Mire, 21:14! #PithCrossing", "Clouds forecast for Lanternport on the 3rd? Please no. #PithCrossing",
                     "Heading to Observatory Hill for the public watch. #PithCrossing"],
    "VaultCup": ["Hammers v Gulls final, calling it now. #VaultCup", "Northmole Vault for the final. Tickets on the first of Mire! #VaultCup"],
    "Hammers": ["Hammers top of the table again. #Hammers", "Ketta is the best wellstriker of her generation. #Hammers"],
    "Everyday": ["Tea at the Copper Kettle in {d}. The seed cake is back.", "Ferry to Lanternport was forty minutes late again.",
                 "Why is the Stillday tram an hour later? Some of us work Stilldays.", "Lamplighter came round {d} tonight. Still magic.",
                 "Hollowdays can't come soon enough.", "Ossa is enormous tonight.", "Rain. Again. It's Gale, what did I expect.",
                 "Bought a Kettlebright K-40. The kettle from the tea rooms. No regrets.", "Anyone know if the Athenaeum Copperside has Tidal Primes back yet?"],
}
DISTRICTS = ["Keelwater", "Rope Walk", "Sounding", "Gullgate", "Copperside", "Old Ford", "Canalside", "Millside"]


CSS = """
*{box-sizing:border-box}body{margin:0;font:15px/1.4 -apple-system,'Segoe UI',sans-serif;background:#fff;color:#0f1419}
.wrap{display:grid;grid-template-columns:220px 600px 1fr;max-width:1200px;margin:0 auto}
nav.left{padding:16px;position:sticky;top:0;height:100vh}nav.left a{display:block;font-size:19px;padding:10px;color:#0f1419;text-decoration:none;border-radius:20px}
nav.left a:hover{background:#eff3f4}.logo{font:bold 26px Georgia,serif;color:#1d9bf0!important}
.feed{border-left:1px solid #eff3f4;border-right:1px solid #eff3f4;min-height:100vh}.feed h1{font-size:20px;padding:12px 16px;margin:0;border-bottom:1px solid #eff3f4}
.chirp{display:grid;grid-template-columns:48px 1fr;gap:10px;padding:12px 16px;border-bottom:1px solid #eff3f4}.chirp img{width:48px;height:48px;border-radius:50%}
.chirp .n{font-weight:bold}.muted{color:#536471}.chirp a{color:#0f1419;text-decoration:none}.chirp .tx a,.bio a{color:#1d9bf0}
.acts{color:#536471;font-size:13px;display:flex;gap:30px;margin-top:6px}.ver{color:#1d9bf0}
.prof{padding:16px;border-bottom:1px solid #eff3f4}.prof img{width:96px;height:96px;border-radius:50%}
.more{display:block;text-align:center;padding:14px;color:#1d9bf0;cursor:pointer}
.side{padding:16px}.side .box{background:#f7f9f9;border-radius:14px;padding:12px}
@media(max-width:1000px){.wrap{grid-template-columns:1fr}nav.left,.side{display:none}}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} / Chatter</title><link rel="stylesheet" href="/style.css"></head><body><div class="wrap">
<nav class="left"><a class="logo" href="/">chatter</a><a href="/">Home</a><a href="/explore/">Explore</a><a href="/tags/">Tags</a></nav>
<div class="feed">{body}</div><div class="side"><div class="box"><b>Trending</b>{SIDE.get('html', '')}</div></div></div>{kw.get('scripts', '')}</body></html>"""


SIDE = {}


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("chatter")
    pop = generate_population()
    users = {}
    for h, disp, bio, ver, joined, fol in ACCOUNTS:
        users[h] = {"h": h, "n": disp, "bio": bio, "v": ver, "j": joined, "f": fol}
    for p in rng.sample(pop, 320):
        users[p.handle] = {"h": p.handle, "n": p.name.given + (" " + p.name.family[0] + "." if rng.random() < .6 else ""),
                           "bio": f"{p.occupation.capitalize()} in {p.city}." + rng.choice(["", " Gulls fan.", " Tea first.", " Opinions my own.",
                                                                                               " Hammers till I die.", " Weft and whisky."]),
                           "v": False, "j": rng.randint(396, 412), "f": rng.randint(2, 4000), "city": p.city}
    for h, u in users.items():
        site.write(f"/img/u/{h}.svg", svg.portrait("chatter-" + h, 96, 96))
    chirps = []
    for h, d, t, text, tags, likes in HAND:
        chirps.append({"h": h, "d": d, "t": t, "x": text, "tags": tags, "l": likes, "r": likes // 9, "re": None})
    commoners = [u for u in users.values() if not u["v"] and u["h"] not in dict((a[0], 1) for a in ACCOUNTS)]
    tag_dates = {"StormPetrel": (ADate(412, 8, 7), ADate(412, 8, 13)), "Slate7": (ADate(412, 7, 3), TODAY),
                 "Deepshaft9": (ADate(412, 6, 22), ADate(412, 8, 10)), "CanalGate": (ADate(412, 4, 20), TODAY),
                 "PithCrossing": (ADate(412, 8, 1), TODAY), "VaultCup": (ADate(412, 7, 20), TODAY), "Hammers": (ADate(412, 2, 1), TODAY),
                 "Everyday": (ADate(412, 1, 1), TODAY)}
    for tag, lines in TEMPLATES.items():
        a, b = tag_dates[tag]
        for i in range(rng.randint(40, 90) if tag != "Everyday" else 400):
            u = rng.choice(commoners)
            d = a + rng.randint(0, max(0, b - a))
            x = rng.choice(lines).format(d=rng.choice(DISTRICTS), s=rng.choice(["Keelwater", "Admiralty", "Fishmarket"]))
            chirps.append({"h": u["h"], "d": d, "t": rng.randint(6 * 60, 24 * 60 - 1), "x": x,
                           "tags": [tag] if tag != "Everyday" else [], "l": int(rng.expovariate(1 / 12)), "r": rng.randint(0, 5), "re": None})
    # match chatter
    for m in [m for m in MATCHES if m.played][-40:]:
        u = rng.choice(commoners)
        winner = m.home if m.home_score > m.away_score else m.away
        chirps.append({"h": u["h"], "d": m.date, "t": 17 * 60 + rng.randint(0, 120), "tags": [],
                       "x": f"{TEAM[m.home].name} {m.home_score}, {TEAM[m.away].name} {m.away_score}. {rng.choice(['What a match.', 'Robbed.', 'Never in doubt.', 'Ref needs spectacles.'])}",
                       "l": rng.randint(0, 80), "r": 0, "re": None})
    chirps.sort(key=lambda c: (c["d"], c["t"]))
    for i, c in enumerate(chirps):
        c["id"] = f"{c['d'].year}{c['d'].month:02d}{c['d'].day:02d}{i:05d}"
    by_id = {c["id"]: c for c in chirps}
    # replies to the hand chirps
    for c in [c for c in chirps if c["h"] in dict((a[0], 1) for a in ACCOUNTS)]:
        for k in range(rng.randint(1, 5)):
            u = rng.choice(commoners)
            reply = {"h": u["h"], "d": c["d"], "t": min(c["t"] + rng.randint(1, 300), 24 * 60 - 1),
                     "x": rng.choice(["This.", "Thank you!", "Finally.", "Took you long enough.", "Source?", "Mine is affected, ordering now.",
                                      "Is this real?", "Don't give them your details!", "Stone remembers.", "Can't wait."]),
                     "tags": [], "l": rng.randint(0, 40), "r": 0, "re": c["id"]}
            reply["id"] = c["id"] + f"r{k}"
            chirps.append(reply)
            by_id[reply["id"]] = reply
    if "drovers_help_desk" in users:
        scam = next(c for c in chirps if c["h"] == "drovers_help_desk")
        chirps.append({"h": "droversbank", "d": scam["d"] + 1, "t": 10 * 60 + 5, "x": "Please do NOT reply to this account. It is not Drovers' Bank.",
                       "tags": [], "l": 1_020, "r": 300, "re": scam["id"], "id": scam["id"] + "r9"})
    chirps.sort(key=lambda c: (c["d"], c["t"]), reverse=True)
    replies = {}
    for c in chirps:
        if c["re"]:
            replies.setdefault(c["re"], []).append(c)

    def linkify(x):
        out = []
        for w in esc(x).split(" "):
            if w.startswith("#") and len(w) > 1:
                t = w[1:].rstrip(".,!?")
                out.append(f'<a href="/tags/{t.lower()}/">{w}</a>')
            elif w.startswith("@") and w[1:].rstrip(".,!?:") in users:
                hh = w[1:].rstrip(".,!?:")
                out.append(f'<a href="/@{hh}">{w}</a>')
            elif ".ves/" in w or ".fol" in w or ".vey/" in w:
                out.append(f'<a href="http://{w.rstrip(".,")}">{w}</a>')
            else:
                out.append(w)
        return " ".join(out)

    def render(c):
        u = users[c["h"]]
        ver = ' <span class="ver" title="Verified">✔</span>' if u["v"] else ""
        rep = f'<div class="muted">Replying to <a href="/chirp/{c["re"]}/">@{esc(by_id[c["re"]]["h"])}</a></div>' if c["re"] in by_id else ""
        tags = " ".join(f'<a href="/tags/{t.lower()}/">#{t}</a>' for t in c["tags"] if f"#{t}" not in c["x"])
        return (f'<div class="chirp"><img src="/img/u/{u["h"]}.svg" alt=""><div><a class="n" href="/@{u["h"]}">{esc(u["n"])}</a>{ver} '
                f'<span class="muted">@{esc(u["h"])} &middot; <a href="/chirp/{c["id"]}/">{c["d"].long()} {time_str(c["t"])}</a></span>{rep}'
                f'<div class="tx">{linkify(c["x"])} {tags}</div><div class="acts"><span>\U0001F4AC {len(replies.get(c["id"], []))}</span>'
                f'<span>\U0001F501 {c["r"]}</span><span>♡ {c["l"]:,}</span></div></div></div>')

    trending = {}
    for c in chirps:
        if c["d"] > TODAY - 10:
            for t in c["tags"]:
                trending[t] = trending.get(t, 0) + 1
    SIDE["html"] = "".join(f'<p><a href="/tags/{t.lower()}/">#{t}</a><br><span class="muted">{n} chirps</span></p>'
                           for t, n in sorted(trending.items(), key=lambda kv: -kv[1])[:6])
    for c in chirps:
        thread = replies.get(c["id"], [])
        parent = render(by_id[c["re"]]) if c["re"] in by_id else ""
        site.page(f"/chirp/{c['id']}/", f"{users[c['h']]['n']}: {c['x'][:40]}", f"<h1>Chirp</h1>{parent}{render(c)}"
                  + "".join(render(r) for r in sorted(thread, key=lambda r: r["t"])), index=c["l"] > 20)
    per = 20
    for h, u in users.items():
        mine = [c for c in chirps if c["h"] == h]
        first, rest = mine[:per], mine[per:]
        site.json(f"/data/u/{h}.json", [render(c) for c in rest])
        more = (f'<a class="more" id="more" data-h="{h}">Show more chirps</a>' if rest else "")
        ver = ' <span class="ver">✔</span>' if u["v"] else ""
        site.page(f"/@{h}", f"{u['n']} (@{h})", f"""<div class="prof"><img src="/img/u/{h}.svg" alt=""><h2>{esc(u['n'])}{ver}</h2>
<div class="muted">@{esc(h)}</div><p class="bio">{linkify(u['bio'])}</p><p class="muted">Joined {u['j']} &middot; <b>{u['f']:,}</b> followers
&middot; {len(mine)} chirps</p></div><div id="list">{"".join(render(c) for c in first)}</div>{more}""",
                  scripts="""<script>var m=document.getElementById('more');if(m){m.onclick=function(){fetch('/data/u/'+m.dataset.h+'.json').then(r=>r.json()).then(function(a){
document.getElementById('list').insertAdjacentHTML('beforeend',a.join(''));m.remove();});};}</script>""")
    tags = {}
    for c in chirps:
        for t in c["tags"]:
            tags.setdefault(t, []).append(c)
    for t, cs in tags.items():
        site.page(f"/tags/{t.lower()}/", f"#{t}", f"<h1>#{t}</h1>" + "".join(render(c) for c in cs[:80]))
    site.page("/tags/", "Tags", "<h1>Tags</h1>" + "".join(f'<p style="padding:0 16px"><a href="/tags/{t.lower()}/">#{t}</a> ({len(cs)})</p>'
                                                         for t, cs in sorted(tags.items(), key=lambda kv: -len(kv[1]))))
    top = sorted([c for c in chirps if c["d"] > TODAY - 14 and not c["re"]], key=lambda c: -c["l"])[:40]
    site.page("/explore/", "Explore", "<h1>Popular this fortnight</h1>" + "".join(render(c) for c in top))
    recent = [c for c in chirps if not c["re"]][:60]
    site.page("/", "Home", "<h1>Latest</h1>" + "".join(render(c) for c in recent))
    site.fact("chatter-green-hat", "Who posted on Chatter about buying a green hat at the Marrowby night market on 10 Gale 412?",
              "Anouk Belvaine (@anouk_belvaine)", "/@anouk_belvaine", hops=3,
              note="links Crier gossip (green hat) with noticeboard personals and Chatter")
    site.fact("chatter-harbour-line", "At what time did the Brineholt Harbour Line resume full service on 12 Gale 412?", "07:10",
              "/@brineholt_trams")
