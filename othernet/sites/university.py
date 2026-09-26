"""lanternport.hal: Lanternport University."""
from ..engine import kit, svg
from ..engine.domains import url
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.academia import DEPARTMENTS, STAFF, TOPICS, PAPERS
from ..world.calendar import WEEKDAYS

CSS = """
*{box-sizing:border-box}body{margin:0;font:16px/1.6 'Optima','Candara','Segoe UI',sans-serif;background:#fcfbf7;color:#1c1917}
header{background:#0f766e;padding:18px 30px;display:flex;align-items:center;gap:28px;flex-wrap:wrap}
header a{color:#fef9c3;text-decoration:none}.logo{font:bold 24px Georgia,serif}.logo small{display:block;font:italic 13px Georgia,serif;opacity:.85}
main{max-width:1040px;margin:0 auto;padding:26px}a{color:#0f766e}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:16px}.card{background:#fff;border:1px solid #e7e5e4;padding:14px;border-radius:6px}
table{border-collapse:collapse;width:100%}td,th{padding:6px;border-bottom:1px solid #e7e5e4;text-align:left;vertical-align:top}th{background:#f0fdfa}
.person{display:grid;grid-template-columns:160px 1fr;gap:18px}.person img{width:160px}
footer{background:#134e4a;color:#ccfbf1;padding:20px;text-align:center;font-size:13px}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Lanternport University</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">Lanternport University<small>Light is owed to all &middot; founded 118</small></a>
<a href="/departments/">Departments</a><a href="/courses/">Courses</a><a href="/people/">People</a><a href="/admissions/">Admissions</a>
<a href="/theses/">Theses</a><a href="/events/">Public lectures</a></header><main>{body}</main>
<footer>Lanternport University, Collegium, Lanternport LP/100. Papers by our scholars appear in <a style="color:#fef9c3" href="{url('annals')}">the Annals</a>.</footer>
{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("university")
    courses = []
    for d, name, _ in DEPARTMENTS:
        mine = [s for s in STAFF if s.dept == d]
        for lvl in (100, 200, 300):
            for k in range(rng.randint(2, 4)):
                topic = rng.choice(TOPICS[d])
                code = f"{d[:3].upper()} {lvl + rng.randint(1, 99)}"
                if any(c["code"] == code for c in courses):
                    continue
                courses.append({"code": code, "dept": d, "title": topic[0].upper() + topic[1:], "lvl": lvl,
                                "credits": rng.choice([6, 12, 12, 18]), "tutor": rng.choice(mine),
                                "when": f"{rng.choice(WEEKDAYS[:5])}s {rng.choice(['9:00', '11:00', '14:00', '16:00'])}",
                                "room": f"{rng.choice(['Aske', 'Solavey', 'Cresselle', 'Glasswharf', 'Old Lantern'])} Hall {rng.randint(1, 12)}",
                                "pre": None})
    for c in courses:
        if c["lvl"] > 100:
            lower = [x for x in courses if x["dept"] == c["dept"] and x["lvl"] == c["lvl"] - 100]
            if lower:
                c["pre"] = rng.choice(lower)["code"]
    courses.append({"code": "NUM 350", "dept": "numerics", "title": "The Cresselle Conjecture: a reading course",
                    "lvl": 300, "credits": 12, "tutor": next(s for s in STAFF if s.id == "talvi-aubrel"),
                    "when": "Hearthdays 16:00", "room": "Cresselle Hall 3", "pre": "NUM 2xx (any)"})
    for s in STAFF:
        img = f"/img/people/{s.id}.svg"
        site.write(img, svg.portrait("uni-" + s.id, 160, 180))
        teach = [c for c in courses if c["tutor"] is s]
        pubs = [p for p in PAPERS if s.name in p.authors]
        site.page(f"/people/{s.id}/", s.name, f"""<div class="person"><img src="{img}" alt=""><div><h1>{esc(s.name)}</h1>
<p>{esc(s.title)}, <a href="/departments/{s.dept}/">{esc(dict((d, n) for d, n, _ in DEPARTMENTS)[s.dept])}</a>. At Lanternport since {s.since}.</p>
<p>Office: {esc(s.office)}. Office hours: {rng.choice(WEEKDAYS[:5])}s, {rng.choice(['10:00', '13:00', '15:00'])} to one bell later.</p>
<p>Interests: {esc(', '.join(s.interests))}</p></div></div>
<h2>Teaching</h2>{"<ul>" + "".join(f'<li><a href="/courses/{slug(c["code"])}/">{c["code"]}: {esc(c["title"])}</a></li>' for c in teach) + "</ul>" if teach else "<p>Not teaching this year.</p>"}
<h2>Publications in the Annals</h2>{"<ul>" + "".join(f'<li><a href="{url("annals", "/paper/" + p.id + "/")}">{esc(p.title)}</a> ({p.received.year})</li>' for p in pubs) + "</ul>" if pubs else "<p>None listed.</p>"}""")
    for d, name, blurb in DEPARTMENTS:
        mine = sorted([s for s in STAFF if s.dept == d], key=lambda s: s.name)
        cs = [c for c in courses if c["dept"] == d]
        head = next((s for s in mine if s.title == "Professor"), mine[0])
        site.page(f"/departments/{d}/", name, f"""<h1>{esc(name)}</h1><p>{esc(blurb)}</p><p>Head of department: <a href="/people/{head.id}/">{esc(head.name)}</a></p>
<h2>People</h2><div class="grid">{"".join(f'<div class="card"><a href="/people/{s.id}/">{esc(s.name)}</a><br><small>{esc(s.title)}</small></div>' for s in mine)}</div>
<h2>Courses</h2>{kit.table(["Code", "Course", "Credits", "Tutor"], [[f'<a href="/courses/{slug(c["code"])}/">{c["code"]}</a>', esc(c["title"]), str(c["credits"]), esc(c["tutor"].name)] for c in cs], raw=True)}""")
    site.page("/departments/", "Departments", "<h1>Departments</h1><div class='grid'>" + "".join(
        f'<div class="card"><h3><a href="/departments/{d}/">{esc(n)}</a></h3><p>{esc(b)}</p></div>' for d, n, b in DEPARTMENTS) + "</div>")
    for c in courses:
        site.page(f"/courses/{slug(c['code'])}/", f"{c['code']} {c['title']}", f"""<h1>{c['code']}: {esc(c['title'])}</h1>
<table><tr><th>Level</th><td>{c['lvl']}</td></tr><tr><th>Credits</th><td>{c['credits']}</td></tr>
<tr><th>Tutor</th><td><a href="/people/{c['tutor'].id}/">{esc(c['tutor'].name)}</a></td></tr><tr><th>When</th><td>{c['when']}</td></tr>
<tr><th>Where</th><td>{esc(c['room'])}</td></tr><tr><th>Before taking this</th><td>{esc(c['pre'] or 'nothing')}</td></tr></table>""")
    site.page("/courses/", "Courses", "<h1>Course catalogue, 412–413</h1><p><input id='f' placeholder='Filter courses'></p>" + kit.table(
        ["Code", "Course", "Level", "Credits", "When"], [[f'<a href="/courses/{slug(c["code"])}/">{c["code"]}</a>', esc(c["title"]),
                                                         str(c["lvl"]), str(c["credits"]), c["when"]] for c in sorted(courses, key=lambda c: c["code"])],
        raw=True, sortable=True, id_="ct") + kit.SORTABLE_JS, scripts="""<script>document.getElementById('f').oninput=function(){var q=this.value.toLowerCase();
document.querySelectorAll('#ct tbody tr').forEach(function(t){t.style.display=t.innerText.toLowerCase().indexOf(q)>=0?'':'none';});};</script>""")
    site.page("/people/", "People", "<h1>People</h1>" + kit.table(
        ["Name", "Title", "Department"], [[f'<a href="/people/{s.id}/">{esc(s.name)}</a>', esc(s.title), s.dept]
                                          for s in sorted(STAFF, key=lambda s: s.name)], raw=True, sortable=True) + kit.SORTABLE_JS)
    site.page("/admissions/", "Admissions", """<h1>Admissions</h1><p>Entry is by the Collegiate entrance examinations, held each
Loam. There are no fees for citizens of the Isles. Students from other nations pay 1,900 lumes a year, or 950 lumes if they hold a
Guild bursary.</p><h2>Key dates for 413 entry</h2><ul><li>Applications open: 1 Mire 412</li><li>Applications close: 30 Dusk 412</li>
<li>Examinations: 10 to 14 Loam 413</li><li>Term begins: 1 Sheaf 413</li></ul><p>Lodging in the Collegium costs 110 lumes a month.</p>""")
    rng2 = stream("theses")
    theses = []
    for i in range(60):
        s = rng2.choice(STAFF)
        from ..world.names import make_name
        student = make_name(rng2, "PEL").full
        theses.append((rng2.randint(395, 411), student, f"{rng2.choice(['Studies in', 'Essays on', 'Measurements of', 'The problem of'])} {rng2.choice(TOPICS[s.dept])}", s))
    theses.append((398, "Nerys Lanterre", "Ranking ribbons by the lanterns that point to them", next(s for s in STAFF if s.id == "mireille-solande")))
    theses.sort(reverse=True)
    site.page("/theses/", "Theses", "<h1>Doctoral theses</h1>" + kit.table(
        ["Year", "Author", "Title", "Supervisor"], [[str(y), esc(a), esc(t), f'<a href="/people/{s.id}/">{esc(s.name)}</a>'] for y, a, t, s in theses],
        raw=True, sortable=True) + kit.SORTABLE_JS)
    site.page("/events/", "Public lectures", """<h1>Public lectures</h1><ul>
<li><b>2 Mire 412, 19:00, Loom Hall:</b> Mireille Solande, "What comes after Weft?"</li>
<li><b>3 Mire 412, 20:00, Observatory Hill:</b> Iselle Cresselle leads a public watch of the Pith crossing. Filters provided.</li>
<li><b>20 Mire 412, 18:00, Cresselle Hall 3:</b> Talvi Aubrel, "Tidal primes for everyone". Seats are limited.</li></ul>""")
    site.page("/", "Lanternport University", f"""<h1>Lanternport University</h1><p>Founded in 118 CR by scholars fleeing the
Concordat's book levy. Home of the Observatory and of the first Loom.</p>
<div class="grid">{"".join(f'<div class="card"><h3><a href="/departments/{d}/">{esc(n)}</a></h3><p>{esc(b)}</p></div>' for d, n, b in DEPARTMENTS)}</div>
<p>See also: <a href="{url('observatory')}">the Observatory</a> &middot; <a href="{url('annals')}">the Annals</a></p>""")
    site.fact("uni-foreign-fee", "How much do students from outside the Pellucid Isles pay per year at Lanternport University?",
              "1,900 lumes (950 with a Guild bursary)", "/admissions/")
    site.fact("uni-lanterre-thesis", "What was the title of Nerys Lanterre's doctoral thesis?",
              "Ranking ribbons by the lanterns that point to them", "/theses/")
