"""copperkettle.ves: The Copper Kettle tea rooms. Locations, menus, and gift cards."""
from ..engine import kit, svg
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.addresses import address
from ..world.calendar import TODAY, WEEKDAYS
from ..world.econ import fmt_money, convert
from ..world.geo import CITIES, CITY

MENU = [
    ("Teas", [("Copper Kettle House Blend", 2.40), ("Moor Heather", 2.60), ("Smoked Harbour", 2.80),
              ("Pearl Leaf Green", 3.10), ("Hollowday Spice (seasonal)", 3.20)]),
    ("Cakes", [("Gorse Hollow apple cake", 3.60), ("Seed cake", 2.90), ("Kiln-dark treacle tart", 3.80),
               ("Two-moon biscuits (pair)", 1.90), ("Quince and almond slice", 3.40)]),
    ("Savouries", [("Cheese and pickle toastie", 5.20), ("Eel pie (Lowmarsh style)", 7.40),
                   ("Moor mushroom soup", 5.80), ("Kethren oat cake with smoked cheese", 6.10)]),
    ("Cold", [("Cider from the fair (Gorsefield only)", 4.20), ("Elderflower cordial", 2.50)]),
]
ALLERGENS = {"Gorse Hollow apple cake": "wheat, egg, milk", "Seed cake": "wheat, egg, milk, sesame",
             "Kiln-dark treacle tart": "wheat, milk", "Two-moon biscuits (pair)": "wheat, milk, almond",
             "Quince and almond slice": "wheat, egg, almond", "Cheese and pickle toastie": "wheat, milk, mustard",
             "Eel pie (Lowmarsh style)": "wheat, fish, egg", "Moor mushroom soup": "milk, celery",
             "Kethren oat cake with smoked cheese": "oats, milk"}

CSS = """
body{margin:0;background:#fbf5ec;color:#3f2a1d;font:16px/1.6 'Trebuchet MS',sans-serif}
header{background:#b45309;padding:16px 28px;display:flex;align-items:center;gap:26px;flex-wrap:wrap}
header a{color:#fff7ed;text-decoration:none}.logo{font:italic bold 30px Georgia,serif}
header nav a{margin-right:16px}
main{max-width:1000px;margin:0 auto;padding:24px}
a{color:#b45309}.cols{display:grid;grid-template-columns:1fr 1fr;gap:24px}
.card{background:#fff;border:1px solid #f1d9bd;border-radius:10px;padding:16px;margin-bottom:14px}
table{border-collapse:collapse;width:100%}td,th{padding:6px;border-bottom:1px dotted #e7c9a4;text-align:left}
img.board{width:100%;max-width:520px;border-radius:10px}
footer{text-align:center;font-size:13px;color:#92400e;padding:30px}
@media(max-width:800px){.cols{grid-template-columns:1fr}}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - The Copper Kettle</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">The Copper Kettle</a><nav><a href="/menu/">Menu</a><a href="/find-us/">Find a tea room</a>
<a href="/gift-cards/">Gift cards</a><a href="/our-story/">Our story</a></nav></header><main>{body}</main>
<footer>The Copper Kettle, since 389. Head office: Orchard Row, Gorse Hollow. Our kettles are Kettlebright K-40s.</footer>{kw.get('scripts', '')}</body></html>"""


def board(title, items, seed, cur="VCR"):
    """A chalkboard of specials. The prices are only in this picture."""
    h = 90 + 34 * len(items)
    p = [f'<rect width="520" height="{h}" rx="14" fill="#1f2d24" stroke="#8b5e34" stroke-width="12"/>',
         svg.text(260, 50, title, 26, "#fef3c7", "middle", "bold", "Comic Sans MS, cursive")]
    for i, (name, price) in enumerate(items):
        y = 92 + i * 34
        p.append(svg.text(34, y, name, 19, "#f8fafc", family="Comic Sans MS, cursive"))
        p.append(svg.text(486, y, price, 19, "#fde68a", "end", family="Comic Sans MS, cursive"))
    return svg.wrap(520, h, "".join(p))


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("copperkettle")
    rooms = []
    for c in CITIES:
        if c.nation not in ("VEY", "SLT"):
            continue
        n = 1 + (c.population > 400_000) + (c.population > 1_000_000) * 3
        for i in range(n):
            line, pc = address(rng, c.name)
            district = c.districts[i % len(c.districts)] if c.districts else c.name
            closed = rng.choice(WEEKDAYS[:5]) if rng.random() < 0.3 else None
            opens = rng.choice(["7:30", "8:00", "8:30", "9:00"])
            shuts = rng.choice(["17:00", "17:30", "18:00", "19:00"])
            rid = slug(f"{c.name} {district}" if district != c.name else c.name)
            if any(r["id"] == rid for r in rooms):
                rid += f"-{i}"
            specials = [(rng.choice(["Tarrow", "Canal", "Harbour", "Moor", "Lamp", "Rope Walk", "Mill"]) + " " +
                         rng.choice(["bun", "tart", "scone", "loaf", "pie", "crumble"]),
                         round(rng.uniform(2.2, 6.8), 2)) for _ in range(3)]
            rooms.append({"id": rid, "city": c.name, "nation": c.nation, "district": district, "addr": f"{line}, {district}",
                          "pc": pc, "closed": closed, "hours": (opens, shuts), "seats": rng.randint(18, 90),
                          "specials": specials, "cider": c.name == "Gorse Hollow",
                          "manager": rng.choice(["Hester", "Linnet", "Tobiah", "Corra", "Marra", "Ansel", "Idony", "Kit"])})
    rooms[0]["note"] = "Our first tea room, opened by Hester Brackley in 389."
    for r in rooms:
        cur = "VCR" if r["nation"] == "VEY" else "STL"
        items = [(n, fmt_money(convert(p, "VCR", cur), cur)) for n, p in r["specials"]]
        site.write(f"/img/board-{r['id']}.svg", board(f"Today at {r['district']}", items, r["id"], cur))
        hours = "".join(f"<tr><td>{wd}</td><td>{'closed' if wd == r['closed'] or (wd == 'Stillday' and r['nation'] == 'SLT') else r['hours'][0] + '–' + r['hours'][1]}</td></tr>"
                        for wd in WEEKDAYS)
        site.page(f"/find-us/{r['id']}/", f"{r['district']}, {r['city']}", f"""<p><a href="/find-us/">&laquo; All tea rooms</a></p>
<div class="cols"><div><h1>{esc(r['district'])}, {esc(r['city'])}</h1><p>{esc(r['addr'])}, {esc(r['city'])} {esc(r['pc'])}</p>
<p>{r['seats']} seats. Manager: {esc(r['manager'])}.</p>{f"<p><i>{esc(r['note'])}</i></p>" if r.get('note') else ''}
<h2>Opening hours</h2><table>{hours}</table>
<p><small>Saltmarch tea rooms close on Stilldays, by Admiralty rule.</small></p></div>
<div><h2>Today's specials</h2><img class="board" src="/img/board-{r['id']}.svg" alt="Specials board at {esc(r['district'])}">
<p><small>Prices on the board are in {'crowns' if cur == 'VCR' else 'tallies and bits'}.</small></p></div></div>""")
    rows = [[f'<a href="/find-us/{r["id"]}/">{esc(r["district"])}</a>', esc(r["city"]), esc(r["pc"]),
             "closed " + r["closed"] + "s" if r["closed"] else "open every day" if r["nation"] == "VEY" else "closed Stilldays"]
            for r in rooms]
    site.page("/find-us/", "Find a tea room", f"<h1>Find a tea room</h1><p>{len(rooms)} tea rooms in Veyl and "
              f"Saltmarch.</p><p><input id='f' placeholder='Type a town'></p>" + kit.table(
                  ["Tea room", "Town", "Postcode", "Days"], rows, raw=True, id_="rooms"),
              scripts="""<script>document.getElementById('f').oninput=function(){var q=this.value.toLowerCase();document.querySelectorAll('#rooms tbody tr').forEach(function(t){t.style.display=t.innerText.toLowerCase().indexOf(q)>=0?'':'none';});};</script>""")
    menu = ""
    for sec, items in MENU:
        menu += f"<h2>{sec}</h2><table>" + "".join(
            f"<tr><td>{esc(n)}</td><td>{p:.2f} cr</td><td><small>{esc(ALLERGENS.get(n, ''))}</small></td></tr>" for n, p in items) + "</table>"
    site.page("/menu/", "Menu", f"<h1>Our menu</h1><p>Prices in Veyl tea rooms. Saltmarch tea rooms charge the same in "
              f"tallies at the day's rate. Specials vary by tea room.</p>{menu}"
              "<p><small>Allergens are listed beside each dish. Ask staff about anything not listed.</small></p>")
    site.page("/gift-cards/", "Gift cards", """<h1>Gift cards</h1><div class="card"><p>Check the balance of a Copper Kettle
gift card. The number is on the back and looks like <code>CK-4412-0981</code>.</p>
<p><input id="gc" placeholder="CK-0000-0000"> <button id="go">Check balance</button></p><p id="bal"></p></div>
<p>Gift cards never expire, and can be used in any tea room in Veyl or Saltmarch.</p>""", index=False, scripts="""<script>
document.getElementById('go').onclick=function(){var v=document.getElementById('gc').value.trim().toUpperCase(),m=/^CK-(\\d{4})-(\\d{4})$/.exec(v),o=document.getElementById('bal');
if(!m){o.textContent='Please enter the card number as printed, e.g. CK-4412-0981.';return;}
var a=parseInt(m[1]),b=parseInt(m[2]);if((a+b)%7!==0){o.textContent='We cannot find that card. Check the number and try again.';return;}
o.textContent='Balance: '+(((a*31+b*17)%4000)/100).toFixed(2)+' cr';};</script>""")
    site.page("/our-story/", "Our story", """<h1>Our story</h1><p>Hester Brackley opened the first Copper Kettle in
Gorse Hollow in 389, with three tables and a borrowed kettle. Today there are Copper Kettles across Veyl and Saltmarch.</p>
<p>Every tea room boils water in a Kettlebright K-40, and every tea is blended in Gorse Hollow. Hester's book,
<i>The Copper Kettle Book of Teas</i>, is published by Gorse &amp; Daughters.</p>""")
    feat = rooms[:6]
    site.page("/", "The Copper Kettle", f"""<div class="cols"><div><h1>A proper cup, since 389.</h1>
<p>Tea rooms in {len({r['city'] for r in rooms})} towns across Veyl and Saltmarch.</p>
<p><a href="/find-us/">Find your nearest Copper Kettle</a></p></div><div class="card"><h2>This season</h2>
<p>Hollowday Spice tea is back from the first of Mire. And the Gorse Hollow tea room is pouring cider from the fair.</p></div></div>
<h2>Some of our tea rooms</h2><ul>{"".join(f'<li><a href="/find-us/{r["id"]}/">{esc(r["district"])}, {esc(r["city"])}</a></li>' for r in feat)}</ul>""")
    site.fact("copperkettle-gc-rule", "What is the balance on Copper Kettle gift card CK-4412-0981?",
              f"{((4412 * 31 + 981 * 17) % 4000) / 100:.2f} cr" if (4412 + 981) % 7 == 0 else "card not found",
              "/gift-cards/", how="interaction")
