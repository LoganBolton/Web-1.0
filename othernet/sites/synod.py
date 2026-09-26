"""synod.odd: the Synod of the Pale Flame. Sparse, formal, and mostly closed to outsiders.

Oddavar counts years of the Flame (FR). The Synod does not publish the
conversion; a visitor has to work it out from dates given in both styles.
"""
from ..engine.web import esc
from ..world.calendar import ADate, TODAY

FR_OFFSET = 1400  # FR = CR + 1400, never stated outright

NOTICES = [
    (ADate(412, 5, 1), "The Frostgate is opened", "By the grace of the Flame, the Frostgate is opened on the first of Blaze in the year {fr} of the Flame, "
     "which the southern peoples call {cr}. It shall be closed at dusk on the eighteenth of Sheaf."),
    (ADate(412, 7, 12), "Concerning the lamp oil of the south", "No lamp of the Pale Flame shall be lit with oil bought south of the Frostgate. "
     "Traders who sell such oil as pale-flame oil shall be refused passage for three seasons."),
    (ADate(412, 8, 2), "Concerning the passing of the lesser moon", "On the third of Mire the lesser moon passes before the greater. The faithful shall keep "
     "the lamps lit through the passing. The passing is not visible from Vesk."),
    (ADate(411, 9, 1), "Concerning pilgrims", "Pilgrims from the south may enter Oddavar only with a pilgrim number issued at the Frostgate office. "
     "Pilgrim numbers are not issued by loom-letter."),
    (ADate(410, 3, 3), "Concerning the Weave", "The Weave shall not pass the Frostgate. The Synod's notices are placed here for the southern peoples only."),
]

CSS = """
body{margin:0;background:#f8fafc;color:#1e3a8a;font:17px/1.8 'Times New Roman',serif;text-align:center}
.wrap{max-width:640px;margin:0 auto;padding:40px 20px}h1{font-weight:normal;letter-spacing:8px;font-size:22px}
.flame{font-size:48px;color:#1e3a8a}.notice{text-align:left;border-top:1px solid #cbd5e1;padding:14px 0}a{color:#1e3a8a}.d{color:#64748b;font-size:14px}
input{padding:6px;font-size:16px;text-align:center}
"""


def page(title, body):
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{esc(title)}</title><link rel="stylesheet" href="/style.css"></head><body><div class="wrap">
<div class="flame">&#128367;</div><h1>THE SYNOD OF THE PALE FLAME</h1>{body}<p class="d"><a href="/">Notices</a> &middot; <a href="/pilgrims/">Pilgrims</a></p></div></body></html>"""


def build(web, site):
    site.write("/style.css", CSS)
    items = []
    for d, title, text in sorted(NOTICES, reverse=True):
        body = text.format(fr=d.year + FR_OFFSET, cr=d.year)
        path = f"/notice/{d.year + FR_OFFSET}-{d.month}-{d.day}/"
        site.raw_page(path, title, page(title, f'<div class="notice"><p class="d">Given on the {d.day} of {d.month_name}, {d.year + FR_OFFSET} of the Flame</p>'
                                              f'<h2>{esc(title)}</h2><p>{esc(body)}</p></div>'))
        items.append(f'<div class="notice"><p class="d">{d.day} {d.month_name} {d.year + FR_OFFSET} FR</p><a href="{path}">{esc(title)}</a></div>')
    site.raw_page("/", "The Synod of the Pale Flame", page("The Synod", "<p>The flame does not flicker.</p>" + "".join(items)))
    site.raw_page("/pilgrims/", "Pilgrims", page("Pilgrims", """<p>Enter your pilgrim number to see the pilgrims' notices.</p>
<p><input id="n" placeholder="P-0000-000"> <button onclick="document.getElementById('m').textContent=/^P-\\d{4}-\\d{3}$/.test(document.getElementById('n').value.trim())?
'This number is not known to the Synod.':'A pilgrim number is written P-0000-000.'">Enter</button></p><p id="m"></p>
<p class="d">Pilgrim numbers are issued only at the Frostgate office, in person, during the trading season.</p>"""), index=False)
    site.fact("synod-fr-year", "What year of the Flame (FR) is 412 CR, according to the Synod's notices?", str(412 + FR_OFFSET), "/", hops=1,
              note="must be inferred from the Frostgate notice, which gives both")
