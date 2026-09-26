"""numerary.gld: the rolls of the Guild of Numerists. Mathematics under Averra's own names.

The mathematics is real. The rim ratio is pi, the Kiln constant is e, and
twelve-fold counting is base 12. Tables are computed, so they can be checked.
"""
import math

from ..engine import kit, links
from ..engine.web import esc
from ..world.calendar import TODAY


def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def tidal(n):
    return is_prime(n) and is_prime(n + 12) and sum(map(int, str(n))) % 3 == 1


def base12(n):
    digits = "0123456789↊↋"  # the Marcher digits for ten and eleven
    if n == 0:
        return "0"
    s = ""
    while n:
        s = digits[n % 12] + s
        n //= 12
    return s


ROLLS = [
    # code, name, status, by, year, statement, proof, uses, family
    ("TP-1", "The Cresselle Conjecture", "Under review", "Ysolde Cresselle (posed)", 339,
     "There are infinitely many tidal primes: primes p such that p + 12 is prime and the digits of p add up to one more than a multiple of three.",
     None, ["TP-3", "LW-7"], "Tidal primes"),
    ("TP-2", "The digit rule for tidal primes", "Proven", "Ysolde Cresselle", 339,
     "A prime p greater than 3 is a tidal prime exactly when p leaves remainder 1 on division by 3 and p + 12 is prime.",
     "The digits of a number add up to the same remainder on division by three as the number itself, because ten leaves remainder one. So the digit condition says p leaves remainder 1.",
     [], "Tidal primes"),
    ("TP-3", "Cresselle's theorem on primes of the first kind", "Proven", "Ysolde Cresselle", 341,
     "There are infinitely many primes that leave remainder 1 on division by 3.",
     "Suppose there are finitely many, and let N be three times the square of their product, plus one. Every prime factor q of N has -3 as a square remainder, which forces q to leave remainder 1 on division by 3, yet q divides none of the listed primes. This is a contradiction.",
     [], "Tidal primes"),
    ("TP-4", "Count of tidal primes", "Computed", "Guild of Numerists", 402, "See the table of counts below each bound.", None, ["TP-2"], "Tidal primes"),
    ("MS-1", "The Merrowby series", "Proven", "Wystan Merrowby", 244,
     "The rim ratio (the rim of a circle divided by its span) equals four times (1 - 1/3 + 1/5 - 1/7 + ...).",
     "Integrate 1/(1 + x²) from 0 to 1 in two ways: once as the angle whose slope is one, which is an eighth of a turn, and once term by term as a series.",
     [], "The rim ratio"),
    ("MS-2", "The rim ratio to twelve places", "Computed", "Guild of Numerists", 390,
     "The rim ratio is 3.141592653590 to twelve places after the point.", None, ["MS-1", "MS-3"], "The rim ratio"),
    ("MS-3", "Aubrande's faster series", "Proven", "Theon Aubrande", 367,
     "The rim ratio equals 3 + 4/(2·3·4) - 4/(4·5·6) + 4/(6·7·8) - ...",
     "Each term corrects the error of the previous partial sum by an amount that shrinks like the cube of the step.", ["MS-1"], "The rim ratio"),
    ("KC-1", "The Kiln constant", "Proven", "Florian Emberlin", 212,
     "The amount a debt of one crown grows to in a year, if interest of 100 per cent is added continuously, is the Kiln constant, 2.718281828459.",
     "Compound n times a year and let n grow without end; the limit of (1 + 1/n)^n exists and equals the sum of 1/k! for k from 0.", [], "Constants"),
    ("NL-1", "Deepwell's Theorem of Nested Lodes", "Proven", "Deepwell Anvar", 231,
     "If each lode lies inside the one before, and their widths shrink to nothing, exactly one point lies in all of them.",
     "The left ends rise and are bounded, so they gather to a point; the right ends fall to the same point because the widths vanish.",
     [], "Foundations"),
    ("LW-7", "The Flint Lemma", "Proven", "Flint Gisla", 377,
     "The number of walks of 2n steps along a line, one step left or right each time, that end where they began, is the number of ways to choose n things from 2n.",
     "A walk returns exactly when it has n steps right among its 2n steps. Choose which.", [], "Lattice walks"),
    ("LW-8", "Flint's return theorem", "Proven", "Flint Gisla", 379,
     "A walker stepping at random on a line or a flat grid returns to the start with certainty. On a grid with depth, as in a delve, it may never return.",
     None, ["LW-7"], "Lattice walks"),
    ("TW-1", "Twelve-fold counting", "Proven", "Casso Saltonby (attributed)", 40,
     "In the twelve-fold counting of the salt tallies, a number is divisible by 2, 3, 4 or 6 exactly when its last Marcher digit is.",
     "Twelve is divisible by 2, 3, 4 and 6, so every place except the last is too.", [], "Counting"),
    ("TW-2", "Marcher digits", "Definition", "Salt Hall", 37,
     "Twelve-fold counting uses ten ordinary digits and two more: ↊ for ten and ↋ for eleven. 412 is written 2↊4.", None, ["TW-1"], "Counting"),
    ("CR-1", "The drifting year", "Proven", "Rosamund Tallwick", 20,
     "The weekday of 1 Rime moves back by one day each year.",
     "A year has 365 days, which is 60 weeks of six days and five days over. Moving forward five days in a six-day week is the same as moving back one.",
     [], "The calendar"),
    ("CR-2", "The Kethren conversion", "Definition", "Moot of Holds", -100,
     "A year of the Hold Reckoning is a year of the Concord Reckoning plus 880.", None, [], "The calendar"),
    ("SK-1", "The Pith meeting interval", "Proven", "Oswin Solavey", 135,
     "Because Pith and Ossa circle in opposite directions, Pith passes Ossa once every 5.94 days.",
     "Their rates of turning add: 1/7.458 + 1/29.25 of a circuit per day. The inverse of the sum is 5.94 days.", [], "The sky"),
    ("SK-2", "Solavey's rule of crossings", "Conjecture", "Oswin Solavey", 140,
     "A full crossing of Pith over Ossa, seen from Lanternport, happens at least once in every sixteen years.", None, ["SK-1"], "The sky"),
    ("GE-1", "Tallwick's rule of the right corner", "Proven", "Rosamund Tallwick", 31,
     "In a field with one right corner, the square on the long side equals the sum of the squares on the other two.",
     "Four copies of the field arranged in a square of side (a + b) leave a square hole of side c.", [], "Shape"),
    ("GE-2", "The Registry's rope", "Proven", "Registry surveyors", 90,
     "A rope knotted into 3, 4 and 5 equal lengths makes a right corner when pulled tight.", None, ["GE-1"], "Shape"),
    ("RB-1", "Aske's halting puzzle", "Proven", "Temmet Aske", 370,
     "There is no ribbon that can read any other ribbon and always say whether the loom will stop.",
     "Feed such a ribbon a copy of a ribbon that does the opposite of whatever it predicts about itself.", [], "Looms"),
    ("RB-2", "Lanterre's lantern rank", "Proven", "Nerys Lanterre, Elio Duvaine", 398,
     "If each page shares its lanterns equally among the pages it links to, repeating the sharing settles on one ranking whatever the start, provided a walker may jump anywhere with a small chance.",
     None, ["LW-8"], "Looms"),
]


CSS = """
body{margin:0;background:#fffdf8;color:#1a1a1a;font:17px/1.6 'Latin Modern Roman','Computer Modern','Cambria',Georgia,serif}
header{border-bottom:1px solid #999;padding:16px 30px;display:flex;align-items:baseline;gap:26px}header a{color:#1a1a1a;text-decoration:none}
header h1{margin:0;font-weight:normal;font-variant:small-caps;letter-spacing:2px}header nav a{margin-right:14px;font-size:15px;color:#7a1f1f}
main{max-width:820px;margin:0 auto;padding:24px 30px}a{color:#7a1f1f}
.stmt{border-left:4px solid #7a1f1f;padding:6px 14px;background:#f8f1e8;font-style:italic}
.status{display:inline-block;padding:1px 8px;border:1px solid;font-size:13px;font-variant:small-caps}
.Proven{color:#166534}.Open,.Conjecture{color:#92400e}.Under{color:#1d4ed8}.Computed,.Definition{color:#555}
table{border-collapse:collapse}td,th{padding:3px 12px;border-bottom:1px solid #ddd;text-align:right}
.proof{display:none;margin-top:8px}.proof.show{display:block}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} &middot; Numerary</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a href="/"><h1>Numerary</h1></a><nav><a href="/rolls/">The Rolls</a><a href="/tables/">Tables</a><a href="/open/">Open problems</a>
<a href="/glossary/">Words</a></nav></header><main>{body}</main>{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    used_by = {}
    for r in ROLLS:
        for u in r[7]:
            used_by.setdefault(u, []).append(r[0])
    for code, name, status, by, year, stmt, proof, uses, fam in ROLLS:
        proof_html = ""
        if proof:
            proof_html = (f'<p><button onclick="this.nextElementSibling.classList.toggle(\'show\');this.textContent='
                          f'this.textContent===\'Show proof\'?\'Hide proof\':\'Show proof\'">Show proof</button></p>'
                          f'<div class="proof"><p>{esc(proof)}</p><p style="text-align:right">&#9633;</p></div>')
        extra = ""
        if code == "TP-1":
            extra = f"""<h3>Review record</h3><ul><li>30 Dusk 411: proof announced by Talvi Aubrel (Ribbon ribbon-411-0412).</li>
<li>18 Bloom 412: gap in Lemma 3 reported by Flint Gisla (Ann. Hal. 88.2).</li><li>5 Gale 412: revised proof posted; placed under review.</li>
<li>Status as of {TODAY.long()}: <b>under review</b>. The Guild does not expect to rule before the Hollowdays.</li></ul>
<p>See <a href="{links.url('annals', '/paper/ribbon-412-0805/')}">the revised proof</a>.</p>"""
        if code == "TP-4":
            bounds = [100, 1_000, 10_000, 100_000]
            counts = [sum(1 for n in range(2, b) if tidal(n)) for b in bounds]
            extra = kit.table(["Below", "Tidal primes"], [[f"{b:,}", f"{c:,}"] for b, c in zip(bounds, counts)])
        if code == "MS-2":
            extra = "<p>Partial sums of the Merrowby series:</p>" + kit.table(
                ["Terms", "Sum"], [[f"{n:,}", f"{4 * sum((-1) ** k / (2 * k + 1) for k in range(n)):.8f}"] for n in (1, 10, 100, 1000, 10000)])
        if code == "TW-2":
            extra = kit.table(["Ordinary", "Marcher"], [[str(n), base12(n)] for n in (10, 11, 12, 13, 24, 100, 144, 412, 1728)])
        site.page(f"/roll/{code}/", f"{code}: {name}", f"""<p><a href="/rolls/">The Rolls</a> &rsaquo; {esc(fam)}</p>
<h2>{code}. {esc(name)}</h2><p><span class="status {status.split()[0]}">{status}</span> &middot; {esc(by)}, {year} CR</p>
<div class="stmt">{esc(stmt)}</div>{proof_html}{extra}
{"<p>Uses: " + ", ".join(f'<a href="/roll/{u}/">{u}</a>' for u in uses) + "</p>" if uses else ""}
{"<p>Used by: " + ", ".join(f'<a href="/roll/{u}/">{u}</a>' for u in used_by.get(code, [])) + "</p>" if used_by.get(code) else ""}""")
    fams = {}
    for r in ROLLS:
        fams.setdefault(r[8], []).append(r)
    site.page("/rolls/", "The Rolls", "<h2>The Rolls</h2>" + "".join(
        f"<h3>{esc(f)}</h3><ul>" + "".join(f'<li><a href="/roll/{r[0]}/">{r[0]}</a> {esc(r[1])} <span class="status {r[2].split()[0]}">{r[2]}</span></li>' for r in rs) + "</ul>"
        for f, rs in fams.items()))
    tps = [n for n in range(2, 5000) if tidal(n)]
    site.page("/tables/", "Tables", f"""<h2>Tables</h2><h3>The first 100 tidal primes</h3><p>{", ".join(str(x) for x in tps[:100])}</p>
<h3>Primes below 200</h3><p>{", ".join(str(x) for x in range(2, 200) if is_prime(x))}</p>
<h3>Constants</h3>{kit.table(["Name", "Value"], [["Rim ratio", f"{math.pi:.12f}"], ["Kiln constant", f"{math.e:.12f}"], ["Pith meeting interval (days)", f"{1 / (1 / 7.458 + 1 / 29.25):.4f}"]])}
<h3>Twelve-fold multiplication</h3>{kit.table([""] + [base12(i) for i in range(1, 13)], [[base12(i)] + [base12(i * j) for j in range(1, 13)] for i in range(1, 13)])}""")
    site.page("/open/", "Open problems", "<h2>Open problems</h2><ul>" + "".join(
        f'<li><a href="/roll/{r[0]}/">{r[0]}: {esc(r[1])}</a> ({r[2]})</li>' for r in ROLLS if r[2] in ("Open", "Conjecture", "Under review")) + "</ul>")
    site.page("/glossary/", "Words", "<h2>Words used on the Rolls</h2>" + kit.table(["Word", "Meaning"], [
        ["rim ratio", "the rim (circumference) of a circle divided by its span (diameter)"], ["span", "the width of a circle through its middle"],
        ["Kiln constant", "the base of continuous growth, about 2.71828"], ["lode", "an interval, a stretch of the number line"],
        ["lattice walk", "a walk on a grid of points"], ["Marcher digit", "a digit of twelve-fold counting"],
        ["tidal prime", "see TP-1 and TP-2"], ["ribbon", "a program for a loom, or a preprint"]]))
    site.page("/", "Numerary", f"""<h2>The Rolls of the Guild of Numerists</h2><p>Every result the Guild has accepted, with its proof where the
proof is short enough to write in a margin. {len(ROLLS)} entries.</p><p><b>Under review:</b> <a href="/roll/TP-1/">TP-1, the Cresselle Conjecture</a>.</p>
<p><a href="/rolls/">Browse the Rolls</a> &middot; <a href="/tables/">Tables</a></p>""")
    site.fact("numerary-tp-count-1000", "How many tidal primes are there below 1,000?", str(sum(1 for n in range(2, 1000) if tidal(n))),
              "/roll/TP-4/")
    site.fact("numerary-412-marcher", "How is 412 written in Marcher (twelve-fold) digits?", base12(412), "/roll/TW-2/")
    site.fact("numerary-cresselle-status", "What is the Guild of Numerists' status for the Cresselle Conjecture?", "Under review",
              "/roll/TP-1/")
