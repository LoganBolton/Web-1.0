"""registry.vey: the Concordat Registry of companies. Search, officers, filings, holdings."""
from ..engine import kit
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.addresses import address
from ..world.calendar import ADate
from ..world.geo import cities_of
from ..world.names import make_name
from ..world.orgs import COMPANIES, COMPANY
from ..world.people import NOTABLE

NATURE = ["Retail of general goods", "Tea rooms and cafes", "Canal and river transport", "Loom devices",
          "Publishing", "Civil engineering", "Textiles", "Holding company", "Property letting", "Food production",
          "Clock and instrument making", "Legal services", "Auctioneering", "Banking", "Media", "Metals refining"]
IND_NATURE = {"Loom devices": "Loom devices", "Retail": "Retail of general goods", "Banking": "Banking",
              "Food and drink": "Tea rooms and cafes", "Civil engineering": "Civil engineering", "Publishing": "Publishing",
              "Glass": "Glass making", "Media": "Media", "Textiles": "Textiles", "Metals": "Metals refining",
              "Appliances": "Appliance manufacture", "Commodities": "Commodities trading", "Property": "Property listing",
              "Auctions": "Auctioneering"}

CSS = """
*{box-sizing:border-box}body{margin:0;font:16px/1.5 Arial,Helvetica,sans-serif;color:#0b0c0c;background:#fff}
header{background:#0b0c0c;color:#fff;padding:10px 30px;border-bottom:10px solid #6b2d5c}
header a{color:#fff;text-decoration:none;font-weight:bold;font-size:20px}header span{font-weight:normal;font-size:15px;margin-left:12px}
.beta{background:#f3f2f1;padding:6px 30px;font-size:14px}.beta b{background:#6b2d5c;color:#fff;padding:2px 6px}
main{max-width:960px;margin:0 auto;padding:24px 30px}a{color:#1d70b8}
h1{font-size:36px;margin:10px 0 20px}.cap{color:#505a5f;font-size:18px}
dl{display:grid;grid-template-columns:240px 1fr;gap:6px 16px;border-top:1px solid #b1b4b6;padding-top:10px}dt{font-weight:bold}
table{border-collapse:collapse;width:100%}td,th{padding:8px 6px;border-bottom:1px solid #b1b4b6;text-align:left;vertical-align:top}
.tabs a{display:inline-block;padding:8px 14px;border:1px solid #b1b4b6;border-bottom:0;margin-right:4px;background:#f3f2f1}
.tabs a.on{background:#fff;font-weight:bold}
.status{display:inline-block;padding:2px 8px;font-weight:bold;font-size:14px}.Active{background:#cce2d8;color:#005a30}
.Dissolved{background:#f4cdc6;color:#942514}.In-liquidation{background:#fff7bf;color:#594d00}
input[type=text]{padding:8px;font-size:18px;width:420px;border:2px solid #0b0c0c}button{background:#00703c;color:#fff;border:0;padding:10px 16px;font-size:16px}
footer{border-top:1px solid #b1b4b6;margin-top:40px;padding:20px 30px;font-size:14px;color:#505a5f}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - Concordat Registry</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a href="/">Concordat Registry</a><span>Public records of companies in the Concordat of Veyl</span></header>
<div class="beta"><b>PUBLIC</b> Records are as filed by the companies. The Registry does not check them.</div>
<main>{body}</main><footer>Concordat Registry, Registry Tower, Wardens' Rise, Ostmere. Registrar General: Tobiah Pimstead.
<a href="/about/">About the Registry</a> &middot; <a href="/search/">Search</a> &middot; <a href="/officers/">Officers A&ndash;Z</a></footer>
{kw.get('scripts', '')}</body></html>"""


def num(rng):
    return f"CR-{rng.randint(10, 99)}-{rng.randint(100000, 999999)}"


def person_name(pid_or_name):
    return NOTABLE[pid_or_name].full if pid_or_name in NOTABLE else pid_or_name


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("registry")
    cos = []

    def company(name, number, inc, city, nature, officers, holders=(), filings=(), status="Active", extra=None,
                addr=None, parent=None):
        line, pc = address(rng, city) if not addr else addr
        cos.append({"name": name, "no": number, "inc": inc, "city": city, "nature": nature, "officers": list(officers),
                    "holders": list(holders), "filings": list(filings), "status": status, "extra": extra or {},
                    "addr": f"{line}, {city} {pc}" if not addr else f"{addr[0]}, {city} {addr[1]}", "parent": parent})

    # --- the listed and well-known Veylish companies --------------------------------
    for c in COMPANIES:
        if c.nation != "VEY":
            continue
        r = stream("reg", c.id)
        inc = ADate(max(c.founded, 1), r.randint(1, 10), r.randint(1, 36))
        officers = []
        if c.ceo:
            officers.append((person_name(c.ceo), "Director and chief executive", ADate(max(c.founded, 390), r.randint(1, 10), r.randint(1, 36)), None))
        for f in c.founders:
            if f != c.ceo:
                officers.append((person_name(f), "Director", inc, ADate(406, 5, 2) if f == "corwen-talley" else
                                 (ADate(399, 2, 2) if f == "Ambrose Gildmere" else None)))
        if c.extra.get("chair"):
            officers.append((person_name(c.extra["chair"]), "Chair", ADate(395, 1, 1), None))
        sec = make_name(r, "VEY").full
        officers.append((sec, "Company secretary", inc + r.randint(400, 20000), None))
        filings = [(ADate(y, r.randint(1, 10), r.randint(1, 36)), "Confirmation statement", "Annual return, no changes")
                   for y in (409, 410, 411)]
        holders = []
        if c.ticker:
            holders.append(("Shares traded on the Brineholt Exchange", f"ticker {c.ticker}", None, None))
        extra = {}
        if c.id == "gildmere":
            holders = [("The Gildmere Family Trust", "51%", ADate(340, 1, 1), None),
                       ("Sallow Fen Holdings", "12%", ADate(409, 10, 12), ADate(412, 5, 18)),
                       ("Shares traded on the Brineholt Exchange", "ticker GLDW (remainder)", None, None)]
            filings += [(ADate(409, 10, 14), "Notice of significant holding", "Sallow Fen Holdings acquires 12%"),
                        (ADate(412, 5, 20), "Notice of significant holding", "Sallow Fen Holdings disposes of its 12%"),
                        (ADate(412, 2, 6), "Contract notice", "Tarrow Canal widening, 1.84 billion cr, awarded 4 Thaw 412")]
            officers.append(("Hester Mottram", "Director (finance)", ADate(401, 4, 4), None))
        if c.id == "morrowmedia":
            extra["subsidiaries"] = ["Crier Publishing", "Morrow Portal"]
        if c.id == "bazaar":
            extra["subsidiaries"] = ["Reelhouse"]
        company(c.name, c.registry_no, inc, c.city, IND_NATURE.get(c.industry, c.industry), officers, holders,
                sorted(filings, key=lambda f: f[0], reverse=True), extra=extra)
    # --- specials -----------------------------------------------------------------
    company("Sallow Fen Holdings", "CR-47-409117", ADate(409, 7, 3), "Tarrow", "Holding company",
            [("Maud Ashford", "Sole director", ADate(409, 7, 3), None),
             ("Canalside Company Secretaries", "Company secretary", ADate(409, 7, 3), None)],
            [("Maud Ashford", "100%", ADate(409, 7, 3), None)],
            [(ADate(412, 5, 18), "Disposal", "Sale of 12% holding in Gildmere Works"),
             (ADate(411, 7, 3), "Confirmation statement", "No employees"),
             (ADate(410, 7, 3), "Confirmation statement", "No employees"),
             (ADate(409, 10, 12), "Acquisition", "Purchase of 12% holding in Gildmere Works (CR-" + COMPANY['gildmere'].registry_no[3:] + ")"),
             (ADate(409, 7, 3), "Incorporation", "Company registered")],
            addr=("Canalside Chambers, 17 Canal Street, Canalside", "TR 1 17"))
    company("Crier Publishing", "CR-51-401220", ADate(401, 1, 9), "Ostmere", "Media",
            [("Radley Blythmore", "Director", ADate(401, 1, 9), None), ("Fenna Rookby", "Editor and director", ADate(405, 3, 3), None)],
            [("Morrow Media Group", "100%", ADate(401, 1, 9), None)],
            [(ADate(411, 2, 2), "Confirmation statement", "Publisher of The Crier (thecrier.wir)"),
             (ADate(401, 1, 9), "Incorporation", "Company registered")], parent="Morrow Media Group")
    company("Morrow Portal", "CR-51-395044", ADate(395, 4, 4), "Ostmere", "Media",
            [("Radley Blythmore", "Director", ADate(395, 4, 4), None)], [("Morrow Media Group", "100%", ADate(395, 4, 4), None)],
            [(ADate(411, 4, 4), "Confirmation statement", "Operator of morrow.ves")], parent="Morrow Media Group")
    company("Reelhouse", "CR-33-400871", ADate(400, 2, 2), "Caddick Ford", "Media",
            [("Edric Hollowell", "Director", ADate(404, 1, 1), None), ("Ivo Crane", "Director", ADate(400, 2, 2), ADate(404, 1, 1))],
            [("Bazaar Holdings", "100%", ADate(404, 1, 1), None)],
            [(ADate(404, 1, 1), "Change of ownership", "Acquired by Bazaar Holdings")], parent="Bazaar Holdings")
    company("Tarrow Canal Lock-keepers' Friendly Society", "CR-02-000301", ADate(301, 1, 1), "Tarrow", "Canal and river transport",
            [("Harlan Mottram", "President", ADate(398, 1, 1), None)], status="Active")
    company("Wexley Barge Hire", "CR-19-388213", ADate(388, 3, 3), "Tarrow", "Canal and river transport",
            [("Ivo Wexley", "Director", ADate(388, 3, 3), None)], status="Dissolved",
            filings=[(ADate(411, 9, 9), "Dissolution", "Struck off: no returns filed")])
    # --- generated small companies ----------------------------------------------------------
    people_pool = [make_name(rng, "VEY").full for _ in range(260)]
    words = ["Lamp", "Kiln", "Ford", "Sallow", "Moor", "Heron", "Anvil", "Orchard", "Barrow", "Copper", "Lock", "Quill",
             "Tannery", "Bridge", "Gorse", "Ember", "Mill", "Wick"]
    ends = ["Trading", "Holdings", "& Co", "Supplies", "Works", "Partners", "Goods", "Services", "Estates", "Bakery",
            "Carriers", "Instruments"]
    for i in range(210):
        city = rng.choice(cities_of("VEY"))
        name = f"{rng.choice(words)} {rng.choice(words) + ' ' if rng.random() < .3 else ''}{rng.choice(ends)}"
        if any(c["name"] == name for c in cos):
            name += f" ({city.name})"
        inc = ADate(rng.randint(330, 411), rng.randint(1, 10), rng.randint(1, 36))
        status = rng.choice(["Active"] * 8 + ["Dissolved", "In liquidation"])
        offs = [(rng.choice(people_pool), "Director", inc, None) for _ in range(rng.randint(1, 3))]
        if rng.random() < 0.3:
            offs.append((rng.choice(people_pool), "Director", inc + rng.randint(100, 3000), None))
        fil = [(inc, "Incorporation", "Company registered")]
        for y in range(max(inc.year + 1, 405), 412):
            if status == "Active" or rng.random() < .5:
                fil.append((ADate(y, inc.month, min(inc.day, 36)), "Confirmation statement", "No changes"))
        if status == "Dissolved":
            fil.append((ADate(rng.randint(406, 412), rng.randint(1, 7), rng.randint(1, 36)), "Dissolution", "Struck off"))
        company(name, num(rng), inc, city.name, rng.choice(NATURE), offs, filings=sorted(fil, key=lambda f: f[0], reverse=True),
                status=status)
    # --- pages -------------------------------------------------------------------------
    officer_index = {}
    for c in cos:
        path = f"/company/{c['no'].replace('/', '-')}/"
        c["path"] = path
        for nm, role, since, until in c["officers"]:
            officer_index.setdefault(nm, []).append((c, role, since, until))
    for c in cos:
        offs = kit.table(["Name", "Role", "Appointed", "Resigned"],
                         [[f'<a href="/officer/{slug(n)}/">{esc(n)}</a>', esc(r), s.long(), u.long() if u else ""] for n, r, s, u in c["officers"]], raw=True)
        holders = kit.table(["Holder", "Share", "From", "Until"], [[esc(h), esc(p), s.long() if s else "", u.long() if u else ""]
                                                                   for h, p, s, u in c["holders"]], raw=True) if c["holders"] else \
            "<p>No holdings of 10% or more have been notified.</p>"
        fil = kit.table(["Date", "Type", "Description"], [[d.long(), t, x] for d, t, x in c["filings"]]) if c["filings"] else "<p>No filings.</p>"
        extra = ""
        if c["extra"].get("subsidiaries"):
            extra = "<h2>Subsidiaries</h2><ul>" + "".join(
                f'<li><a href="{next(x["path"] for x in cos if x["name"] == s)}">{esc(s)}</a></li>' for s in c["extra"]["subsidiaries"]) + "</ul>"
        parent = ""
        if c["parent"]:
            p = next(x for x in cos if x["name"] == c["parent"])
            parent = f'<dt>Parent company</dt><dd><a href="{p["path"]}">{esc(p["name"])}</a></dd>'
        site.page(c["path"], c["name"], f"""<p class="cap">Company</p><h1>{esc(c['name'])}</h1>
<p><span class="status {c['status'].replace(' ', '-')}">{c['status']}</span></p>
<dl><dt>Registered number</dt><dd>{c['no']}</dd><dt>Registered office</dt><dd>{esc(c['addr'])}</dd>
<dt>Incorporated</dt><dd>{c['inc'].long()}</dd><dt>Nature of business</dt><dd>{esc(c['nature'])}</dd>{parent}</dl>
<h2>Officers</h2>{offs}<h2>Significant holdings</h2>{holders}{extra}<h2>Filing history</h2>{fil}""")
    for nm, apps in officer_index.items():
        site.page(f"/officer/{slug(nm)}/", nm, f"<p class='cap'>Officer</p><h1>{esc(nm)}</h1><p>{len(apps)} appointment(s).</p>" + kit.table(
            ["Company", "Role", "Appointed", "Resigned", "Status"],
            [[f'<a href="{c["path"]}">{esc(c["name"])}</a>', esc(r), s.long(), u.long() if u else "", c["status"]] for c, r, s, u in apps], raw=True))
    letters = sorted({slug(n)[0] for n in officer_index})
    for l in letters:
        names = sorted(n for n in officer_index if slug(n)[0] == l)
        site.page(f"/officers/{l}/", f"Officers: {l.upper()}", f"<h1>Officers: {l.upper()}</h1><p>" + " ".join(
            f'<a href="/officers/{x}/">{x.upper()}</a>' for x in letters) + "</p><ul>" + "".join(
            f'<li><a href="/officer/{slug(n)}/">{esc(n)}</a></li>' for n in names) + "</ul>")
    site.page("/officers/", "Officers A-Z", "<h1>Officers A&ndash;Z</h1><p>" + " ".join(
        f'<a href="/officers/{x}/">{x.upper()}</a>' for x in letters) + "</p>")
    site.json("/data/companies.json", [{"n": c["name"], "no": c["no"], "s": c["status"], "t": c["city"], "p": c["path"],
                                        "o": [o[0] for o in c["officers"]]} for c in cos])
    site.page("/search/", "Search the Registry", """<h1>Search the Registry</h1>
<form><p><input type="text" name="q" id="q" placeholder="Company name, number, or officer"> <button>Search</button></p>
<p><label><input type="radio" name="by" value="co" checked> Companies</label> <label><input type="radio" name="by" value="off"> Officers</label></p></form>
<div id="res"></div>""", index=False, scripts="""<script>
var P=new URLSearchParams(location.search),q=(P.get('q')||'').trim(),by=P.get('by')||'co';document.getElementById('q').value=q;
document.querySelector('input[value='+by+']').checked=true;
if(q){fetch('/data/companies.json').then(r=>r.json()).then(function(C){var l=q.toLowerCase(),out='';
if(by==='co'){var hits=C.filter(c=>c.n.toLowerCase().indexOf(l)>=0||c.no.toLowerCase()===l);
 out='<p>'+hits.length+' companies</p><table>'+hits.map(c=>'<tr><td><a href="'+c.p+'">'+c.n+'</a></td><td>'+c.no+'</td><td>'+c.t+'</td><td>'+c.s+'</td></tr>').join('')+'</table>';}
else{var m={};C.forEach(function(c){c.o.forEach(function(o){if(o.toLowerCase().indexOf(l)>=0){(m[o]=m[o]||[]).push(c);}});});
 var ks=Object.keys(m).sort();out='<p>'+ks.length+' officers</p><ul>'+ks.map(k=>'<li><a href="/officer/'+k.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')+'/">'+k+'</a> ('+m[k].length+')</li>').join('')+'</ul>';}
document.getElementById('res').innerHTML=out||'<p>No results.</p>';});}</script>""")
    site.page("/about/", "About the Registry", """<h1>About the Registry</h1><p>The Concordat Registry was founded in 9 CR by
Rosamund Tallwick, the First Registrar, in a tannery loft in Ostmere. It records every company, deed and birth in the
Concordat. Company records are public.</p><p>Every company must file a confirmation statement each year and notify the
Registry of any holding of 10% or more in its shares.</p><p>Companies registered in Saltmarch, the Holds or the Isles are not
recorded here.</p>""")
    site.page("/", "Concordat Registry", f"""<h1>Find company information</h1>
<form action="/search/"><p><input type="text" name="q" placeholder="Company name or number"> <button>Search</button></p></form>
<p>{len(cos)} companies on the register. You can also <a href="/officers/">browse officers A&ndash;Z</a>.</p>
<p>Recently updated: {"".join(f'<a href="{c["path"]}">{esc(c["name"])}</a>, ' for c in cos[:5])}&hellip;</p>""")
    site.fact("registry-sallowfen-director", "Who is the sole director of Sallow Fen Holdings?", "Maud Ashford",
              "/company/CR-47-409117/")
    site.fact("registry-crier-owner", "Which company owns the publisher of The Crier?", "Morrow Media Group",
              "/company/CR-51-401220/", hops=2)
