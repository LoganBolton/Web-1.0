"""spirekeeper.fol: The Spire Log, a lighthouse keeper's daily notes from Saltspire."""
from ..engine.rings import widget
from ..engine.rng import stream
from ..engine.web import esc
from ..world.calendar import ADate, TODAY, MONTHS, date_range, time_str
from ..world.sky import tides
from ..world.weather import WEATHER

SPECIAL = {
    ADate(412, 8, 8): "Barometer falling like a stone. Doubled the lamp oil in the stores. Storm Petrel by morning, the Office says. For once I believe them.",
    ADate(412, 8, 9): "Worst night since the Harbour Fire year. The vane is gone off the gallery rail. Found it at noon in the salt pans. The light never stopped.",
    ADate(412, 8, 11): "A singer's people telephoned. Could she still play on Spire Green tomorrow. The Green is under two ells of shingle. Told them no, politely, the second time.",
    ADate(412, 7, 30): "Signed the papers to sell the Old Keeper's Cottage at Spire Point. Harbourside Homes want 118,000 tallies for it. I'll stay in the new house. "
                       "Someone should live there who likes the wind.",
    ADate(412, 6, 1): "Airship went over at the ninth bell, heading south. Emberline's new one. Looked like a loaf of bread with ambitions.",
    ADate(412, 8, 16): "My nephew put me on Chatter. I have written three things. That is enough.",
    ADate(412, 4, 30): "Ossa at her nearest. Spring tide over the lower step for the first time in six years.",
    ADate(412, 1, 1): "New year. Lamp relit at 16:40. Oil used in 411: 3,112 measures. Log begins.",
}


CSS = """
body{margin:0;background:#0b1d2a;color:#d7e3ea;font:15px/1.6 'Courier New',Courier,monospace}
.wrap{max-width:760px;margin:0 auto;padding:24px}a{color:#ffd166}
h1{color:#ffd166;letter-spacing:4px}.entry{border-left:3px solid #ffd166;padding:4px 12px;margin:14px 0}.d{color:#8fb3c9}
table{border-collapse:collapse}td{padding:2px 12px 2px 0}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - The Spire Log</title><link rel="stylesheet" href="/style.css"></head><body><div class="wrap">
<h1><a href="/" style="text-decoration:none">THE SPIRE LOG</a></h1><p class="d">Kept at the Spire, Saltspire, by P. Keelmouth, keeper. Light: white, one flash every
five seconds, seen 19 leagues.</p>{body}<hr><p class="d">Months: {" ".join(f'<a href="/log/412-{m:02d}/">{MONTHS[m - 1]}</a>' for m in range(1, TODAY.month + 1))}
&middot; <a href="/about/">About the Spire</a></p>{widget('lamplit', 'spirekeeper', 'background:#12324a;color:#d7e3ea')}</div></body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("spire")
    for m in range(1, TODAY.month + 1):
        entries = []
        for d in date_range(ADate(412, m, 1), min(ADate(412, m, 36), TODAY)):
            w = WEATHER["Saltspire"][d]
            light_on = 16 * 60 + 20 + int(40 * abs(m - 5.5) / 4.5)
            light_off = 6 * 60 + 10 + int(40 * abs(m - 5.5) / 4.5)
            t = tides(d, "Saltspire")
            highs = [f"{time_str(x)} ({h:.1f})" for x, k, h in t if k == "High"]
            note = SPECIAL.get(d) or (rng.choice(["Nothing to report.", "Two colliers passed northbound.", "Gulls on the gallery again.",
                                                  "Polished the lens.", "Oil delivery from Brineholt.", "Fog at dawn.", "A seal on the lower step.",
                                                  "Trimmed wicks.", "Wrote to the Admiralty about the paint. Again.", "Quiet."]) if rng.random() < .7 else "")
            entries.append(f'<div class="entry"><b>{d.salt()}</b> <span class="d">{d.weekday}</span><br>Wind {w["wind"]} &middot; {w["cond"]} &middot; '
                           f'{w["hi"]:.0f}/{w["lo"]:.0f}&deg;<br>Lit {time_str(light_on)}, out {time_str(light_off)}. '
                           f'High water {", ".join(highs)}.<br>{esc(note)}</div>')
        site.page(f"/log/412-{m:02d}/", f"{MONTHS[m - 1]} 412", f"<h2>{MONTHS[m - 1]} 412</h2>" + "".join(reversed(entries)))
    site.page("/about/", "About the Spire", """<h2>About the Spire</h2><p>The Spire at Saltspire is older than the Republic. It was first lit in -120 CR.
Keepers have been Keelmouths since. I am the twelfth. I wrote a book about us: Keepers of the Spire (Tidings Press, 399).</p>
<p>The light shows one white flash every five seconds. Do not confuse it with Harthwick, which is further south and changed its light this year.</p>
<p>No visitors on the gallery. The shingle on Spire Green is not a beach. The cottage at Spire Point is for sale through Harbourside Homes.</p>""")
    recent = sorted(SPECIAL.items(), reverse=True)[:5]
    site.page("/", "The Spire Log", "<h2>Recent notes</h2>" + "".join(f'<div class="entry"><b>{d.salt()}</b><br>{esc(t)}</div>' for d, t in recent)
              + f'<p>Full log: <a href="/log/412-{TODAY.month:02d}/">this month</a>.</p>')
    site.fact("spire-oil-411", "How many measures of lamp oil did the Spire use in 411?", "3,112", "/log/412-01/")
    site.fact("spire-light", "What is the light pattern of the Spire at Saltspire?", "one white flash every five seconds", "/about/")
