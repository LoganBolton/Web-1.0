"""radiolantern.pel: Radio Lantern schedules and transcripts."""
from ..engine import kit
from ..engine.domains import url
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.calendar import WEEKDAYS, TODAY, ADate, time_str

SHOWS = [
    ("Dawn Chorus", "Maren Solaire", "Birdsong, weather, and the ferry times.", "06:00", 120),
    ("The Morning Wire", "Elio Vireaux", "News from the Isles and the Reach.", "08:00", 120),
    ("Loom Talk", "Quilla Marelle", "Technology and the Weave, with listener questions.", "10:00", 60),
    ("Kitchen Tide", "Delphine Estrande", "Cooking with what the sea brings in.", "11:00", 60),
    ("Midday Market", "Paz Aubrel", "Prices, pearls, and the Marrowby market report.", "12:00", 60),
    ("The Long Afternoon", "Sevrin Duvaine", "Music, mostly slow.", "13:00", 180),
    ("Vault Hour", "Bex Gullwright", "Vaultball news and phone-ins.", "16:00", 60),
    ("Evening Wire", "Elio Vireaux", "The day's news.", "17:00", 60),
    ("Night Sky", "Iselle Cresselle", "What to look for tonight, from Observatory Hill.", "21:00", 60),
    ("Small Hours", "Ondine Lanterre", "Requests and quiet talk until three.", "22:00", 300),
]

TRANSCRIPTS = [
    ("loom-talk-412-08-10", "Loom Talk", ADate(412, 8, 10), [
        ("QUILLA", "Welcome back. On the line is Theon Morvenne, who made Fathom. Theon, the question "
         "everyone is asking: when does the next expansion arrive?"),
        ("THEON", "The Ninth Trench expansion comes out on the fourteenth of Mire. Not the third, as some "
         "people have been saying. The third is when Pith crosses Ossa and I'd like people to go outside."),
        ("QUILLA", "And will it have the Ossa Lantern everyone keeps asking for?"),
        ("THEON", "It will. You'll find it in the drowned observatory, in the trench. That's all I'm saying."),
        ("QUILLA", "Next caller, from Coralstead..."),
        ("CALLER", "Hello, yes, my Slate 7 charger has VC-7A on it. Is that the bad one?"),
        ("QUILLA", "It is. Stop using it. Vantle will send you a VC-7B. There's a form on their "
         "support pages."),
    ]),
    ("night-sky-412-08-15", "Night Sky", ADate(412, 8, 15), [
        ("ISELLE", "Good evening from Observatory Hill. Seventeen nights until Pith crosses Ossa."),
        ("ISELLE", "If you're in Lanternport, the crossing starts at fourteen minutes past nine in the "
         "evening. If you're in Harthwick, add six minutes, because you're further north and west."),
        ("ISELLE", "Please don't look through a telescope at Ossa without a filter. It's bright."),
        ("CALLER", "Is it true Pith is hollow?"),
        ("ISELLE", "No. It's rock, and a bit of ice. Next question."),
    ]),
    ("vault-hour-412-08-16", "Vault Hour", ADate(412, 8, 16), [
        ("BEX", "The Hammers look unstoppable. Is anyone going to catch them?"),
        ("CALLER", "The Gulls could if Roscoe stays fit. But the Vault Cup final is at the Northmole Vault "
         "this year, on the thirtieth of Mire, so the Gulls will have home crowd."),
        ("BEX", "It is the Northmole this year, that's right. Tickets go on sale on the first of Mire."),
    ]),
    ("kitchen-tide-412-07-30", "Kitchen Tide", ADate(412, 7, 30), [
        ("DELPHINE", "Today, smoked eel with sea-fennel. Most people over-smoke the eel. Ninety minutes "
         "over alder, no more."),
        ("DELPHINE", "Sea-fennel you can pick at low water on the Marrowby strand, but only the green "
         "tips. And please, not in Bloom, when it's flowering."),
    ]),
]


CSS = """
body{margin:0;background:#fef3c7;color:#422006;font:15px/1.5 Verdana,Geneva,sans-serif}
header{background:#0f766e;color:#fde68a;padding:16px 22px}header a{color:#fde68a;text-decoration:none}
header h1{margin:0;font-size:28px}header p{margin:2px 0 0;opacity:.8}
nav{background:#115e59;padding:6px 22px}nav a{color:#fff;margin-right:16px}
main{max-width:980px;margin:0 auto;padding:18px}
.tabbar a{display:inline-block;padding:6px 10px;background:#fde68a;margin:0 4px 4px 0;color:#422006;text-decoration:none;border-radius:4px}
.tabbar a.on{background:#0f766e;color:#fff}
table{border-collapse:collapse;width:100%}td,th{padding:6px;border-bottom:1px solid #eab308;text-align:left}
.line{margin:6px 0}.who{font-weight:bold;color:#0f766e}
.live{background:#b91c1c;color:#fff;padding:2px 6px;border-radius:3px;font-size:12px}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(title)} - Radio Lantern</title>
<meta name="viewport" content="width=device-width, initial-scale=1"><style>{CSS}</style></head><body>
<header><a href="/"><h1>&#128251; Radio Lantern 91.4</h1></a><p>Broadcasting from Observatory Hill, Lanternport</p></header>
<nav><a href="/">Schedule</a><a href="/shows/">Shows</a><a href="/transcripts/">Transcripts</a><a href="/listen/">Listen</a></nav>
<main>{body}</main>{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    tabs = []
    for i, wd in enumerate(WEEKDAYS):
        rng = stream("radio", wd)
        rows = []
        for name, host, blurb, start, mins in SHOWS:
            if wd == "Stillday" and name in ("The Morning Wire", "Midday Market"):
                name, host = "Stillday Service", "The Lanternport Choir"
            if wd == "Hearthday" and name == "Vault Hour":
                name, host = "Vault Hour Live (match commentary)", "Bex Gullwright"
            h, m = map(int, start.split(":"))
            rows.append([f"{start}–{time_str(h * 60 + m + mins)}", f"<a href='/shows/{slug(name)}/'>{esc(name)}</a>"
                         if slug(name) in {slug(s[0]) for s in SHOWS} else esc(name), esc(host)])
        tabs.append((wd, kit.table(["Time", "Show", "Presenter"], rows, raw=True)))
    today_idx = WEEKDAYS.index(TODAY.weekday)
    site.page("/", "Schedule", f"<h2>This week on Radio Lantern</h2><p>All times Lanternport time.</p>"
              f"{kit.tabs(tabs, active=today_idx)}", scripts=kit.TABS_JS)
    for name, host, blurb, start, mins in SHOWS:
        tr = [t for t in TRANSCRIPTS if t[1] == name]
        site.page(f"/shows/{slug(name)}/", name, f"<h2>{esc(name)}</h2><p>{esc(blurb)}</p>"
                  f"<p>Presented by {esc(host)}. Every day at {start}.</p>" +
                  ("<h3>Transcripts</h3><ul>" + "".join(f'<li><a href="/transcripts/{t[0]}/">{t[2].pell()}</a></li>'
                                                        for t in tr) + "</ul>" if tr else ""))
    site.page("/shows/", "Shows", "<h2>Our shows</h2><ul>" + "".join(
        f'<li><a href="/shows/{slug(s[0])}/">{esc(s[0])}</a> with {esc(s[1])}</li>' for s in SHOWS) + "</ul>")
    lis = []
    for tid, show, d, lines in TRANSCRIPTS:
        body = "".join(f'<div class="line"><span class="who">{esc(w)}:</span> {esc(t)}</div>' for w, t in lines)
        site.page(f"/transcripts/{tid}/", f"{show}, {d.pell()}", f"<h2>{esc(show)}</h2><p>Broadcast {d.full()}. "
                  f"Transcribed by volunteers; errors are ours.</p>{body}")
        lis.append(f'<li><a href="/transcripts/{tid}/">{esc(show)}, {d.pell()}</a></li>')
    site.page("/transcripts/", "Transcripts", "<h2>Transcripts</h2><ul>" + "".join(lis) + "</ul>")
    site.page("/listen/", "Listen", "<h2>Listen</h2><p>Tune to 91.4 on the Isles, 88.2 in Harthwick. "
              "On the Weave, the live stream needs a loom with a sound horn.</p><p><span class='live'>ON AIR</span> "
              "stream temporarily unavailable.</p>")
    site.fact("fathom-ninth-trench", "When does the Ninth Trench expansion for Fathom come out?",
              "14 Mire 412", "/transcripts/loom-talk-412-08-10/")
    site.fact("vault-cup-venue", "Where is the 412 Vault Cup final played?", "Northmole Vault, Brineholt",
              "/transcripts/vault-hour-412-08-16/")
