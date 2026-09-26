"""hollowmarket.ves: Hollowmarket Auctions. Sales, lots, and bid histories."""
import json

from ..engine import kit, svg
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.calendar import ADate, TODAY, time_str
from ..world.people import generate_population

SALES = [
    ("Looms, Ribbons and Reeds", ADate(412, 2, 20), "Scientific and loom antiques."),
    ("Clocks and Instruments", ADate(412, 5, 10), "Clocks, barometers, telescopes."),
    ("The Harbour Fire Sale", ADate(412, 6, 18), "Salvage and ship's fittings from before 404."),
    ("Kethren Metalwork", ADate(412, 7, 26), "Lamps, tools, and ornaments from the Holds."),
    ("Autumn Curiosities", ADate(412, 8, 30), "Things that fit nowhere else."),
    ("Books and Papers", ADate(412, 9, 20), "Early printings, maps, letters."),
]
ITEMS = [
    ("brass reed from an early Loom", 400, 2400), ("ship's bell", 150, 900), ("miner's lamp", 40, 300),
    ("two-moon mantel clock", 300, 3500), ("Emberly green glass bowl", 80, 700), ("pocket spyglass", 60, 500),
    ("salt tally stick", 20, 180), ("Kethren clan brooch", 90, 1200), ("barometer", 120, 800),
    ("map of the Glass Sea", 70, 650), ("wax disc player", 50, 400), ("lamplighter's pole", 25, 160),
    ("ribbon punch", 200, 1400), ("tea caddy", 30, 220), ("carved whalebone", 100, 900),
    ("pair of candlesticks", 40, 260), ("figurehead fragment", 300, 2800), ("letter, signed", 60, 2000),
    ("Registry ledger page", 50, 600), ("chess set, Frostgate style", 90, 950),
]


CSS = """
body{margin:0;font:15px/1.5 Garamond,'EB Garamond',Georgia,serif;background:#1c1917;color:#e7e5e4}
header{padding:20px 30px;border-bottom:1px solid #44403c;display:flex;align-items:baseline;gap:30px}
header a{color:#e7e5e4;text-decoration:none}.logo{font-size:30px;letter-spacing:6px;text-transform:uppercase}
nav a{margin-right:18px;color:#d6d3d1}
main{max-width:1100px;margin:0 auto;padding:24px}
a{color:#fbbf24}
.lots{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:18px}
.lot{background:#292524;padding:12px;border:1px solid #44403c}.lot img{width:100%;height:auto;background:#fff}
.st{font-size:12px;text-transform:uppercase;letter-spacing:2px}.open{color:#86efac}.closed{color:#a8a29e}.withdrawn{color:#fca5a5}
table{border-collapse:collapse;width:100%}td,th{padding:6px;border-bottom:1px solid #44403c;text-align:left}
.two{display:grid;grid-template-columns:1fr 1fr;gap:24px}.two img{width:100%;background:#fff}
input,button{font:inherit;padding:6px}
footer{text-align:center;color:#78716c;font-size:13px;padding:30px}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Hollowmarket</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">Hollowmarket</a><nav><a href="/sales/">Sales</a><a href="/lots/">Find a lot</a>
<a href="/results/">Results</a><a href="/selling/">Selling with us</a></nav></header><main>{body}</main>
<footer>Hollowmarket Auctions, Gallowmead, Ostmere. Auctioneers since 318. Buyer's premium 18%.</footer>{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    pop = generate_population()
    rng = stream("hollowmarket")
    lots = []
    n = 4400
    for si, (sname, sdate, sdesc) in enumerate(SALES):
        for i in range(rng.randint(14, 22)):
            n += rng.randint(1, 5)
            if n in (4402, 4471):
                n += 1
            item, lo, hi = rng.choice(ITEMS)
            year = rng.randint(120, 395)
            est_lo = int(lo * rng.uniform(0.8, 1.5))
            est_hi = int(est_lo * rng.uniform(1.4, 2.2))
            lots.append({"no": n, "sale": si, "title": f"A {item}, c. {year} CR", "est": (est_lo, est_hi),
                         "desc": f"{item.capitalize()}, believed made around {year} CR. "
                                 f"{rng.choice(['Some wear.', 'Good condition.', 'Restored.', 'Provenance: a Tarrow estate.', 'Maker unknown.', 'Signed on the base.'])}",
                         "kind": rng.choice(["clock", "lamp", "jar", "book", "telescope", "box"]), "special": None})
    # Special lots
    lots.append({"no": 4471, "sale": 1, "title": "A gilded pointer, maker unknown",
                 "est": (900, 1400), "desc": "A large gilded brass pointer, about one ell and thirty thumbs long, "
                 "with a crescent terminal. Old repair to the pivot, stamped. Consigned privately.",
                 "kind": "clock", "special": "withdrawn"})
    lots.append({"no": 4402, "sale": 0, "title": "Punched ribbon fragment attributed to Temmet Aske",
                 "est": (8000, 12000), "desc": "Nine thumbs of waxed linen ribbon with a punch pattern matching Aske's "
                 "'addition of nine-digit numbers' program. Letter of opinion from the Loom Hall.",
                 "kind": "book", "special": "aske"})
    lots.sort(key=lambda l: l["no"])
    for lot in lots:
        sname, sdate, _ = SALES[lot["sale"]]
        r = stream("lot", lot["no"])
        closes = sdate
        if lot["special"] == "withdrawn":
            status = "withdrawn"
        elif closes <= TODAY:
            status = "closed"
        else:
            status = "open"
        bids = []
        if status != "withdrawn":
            price = lot["est"][0] * r.uniform(0.5, 0.8)
            t = closes - r.randint(8, 20)
            for k in range(r.randint(2, 14) if status == "closed" else r.randint(0, 6)):
                price *= r.uniform(1.04, 1.22)
                t = t + r.randint(0, 2)
                if t > TODAY:
                    break
                bids.append({"who": r.choice(pop).handle[:3] + "***", "amt": round(price), "d": t.long(),
                             "tm": time_str(r.randint(8 * 60, 23 * 60))})
            if lot["special"] == "aske" and status == "closed":
                bids.append({"who": "Loo***", "amt": 17_250, "d": (closes - 1).long(), "tm": "21:59"})
        lot.update(status=status, bids=bids, closes=closes)
        hammer = bids[-1]["amt"] if bids and status == "closed" else None
        lot["hammer"] = hammer
        label = "REPAIR: Q.C. 331" if lot["special"] == "withdrawn" else f"LOT {lot['no']}"
        pic = svg.product(lot["kind"], f"lot{lot['no']}", label)
        site.write(f"/img/lot-{lot['no']}.svg", pic)
        bid_rows = [[b["d"], b["tm"], b["who"], f"{b['amt']:,} cr"] for b in reversed(bids)]
        note = ""
        if status == "withdrawn":
            note = ("<p class='withdrawn'><b>This lot has been withdrawn from sale.</b> Hollowmarket is assisting "
                    "the Quenby wardens. Anyone with information about the consignor should contact the front desk.</p>")
        bid_form = ""
        if status == "open":
            nxt = int((bids[-1]["amt"] if bids else lot["est"][0] * 0.7) * 1.05) + 1
            bid_form = f"""<form onsubmit="event.preventDefault();var v=+this.a.value;document.getElementById('bm').textContent=v>={nxt}?
'Your bid of '+v.toLocaleString()+' cr is recorded. You will hear by loom-letter if you are outbid.':'The next bid must be at least {nxt:,} cr.';">
<label>Your bid (cr) <input name="a" type="number" min="{nxt}"></label> <button>Place bid</button><p id="bm"></p></form>"""
        site.page(f"/lot/{lot['no']}/", lot["title"], f"""<p><a href="/sale/{slug(sname)}/">{esc(sname)}</a></p>
<div class="two"><div><img src="/img/lot-{lot['no']}.svg" alt="Photograph of lot {lot['no']}"></div>
<div><div class="st {status}">{status}</div><h1>Lot {lot['no']}: {esc(lot['title'])}</h1><p>{esc(lot['desc'])}</p>
<p>Estimate: {lot['est'][0]:,}–{lot['est'][1]:,} cr</p><p>Sale closes: {closes.full()}</p>
{f"<p><b>Hammer price: {hammer:,} cr</b> (plus 18% buyer's premium)</p>" if hammer else ""}{note}{bid_form}</div></div>
<h2>Bid history</h2>{kit.table(["Date", "Time", "Bidder", "Bid"], bid_rows) if bid_rows else "<p>No bids.</p>"}""")
    for si, (sname, sdate, sdesc) in enumerate(SALES):
        sl = [l for l in lots if l["sale"] == si]
        cards = "".join(f'<div class="lot"><a href="/lot/{l["no"]}/"><img src="/img/lot-{l["no"]}.svg" alt=""></a>'
                        f'<div class="st {l["status"]}">{l["status"]}</div><a href="/lot/{l["no"]}/">Lot {l["no"]}: {esc(l["title"])}</a>'
                        f'<div>Est. {l["est"][0]:,}–{l["est"][1]:,} cr</div></div>' for l in sl)
        site.page(f"/sale/{slug(sname)}/", sname, f"<h1>{esc(sname)}</h1><p>{esc(sdesc)} Closes {sdate.full()}.</p>"
                  f"<div class='lots'>{cards}</div>")
    site.page("/sales/", "Sales", "<h1>Sales</h1>" + kit.table(
        ["Sale", "Closes", "Lots", "Status"],
        [[f'<a href="/sale/{slug(s)}/">{esc(s)}</a>', d.long(), str(sum(1 for l in lots if l["sale"] == i)),
          "open" if d > TODAY else "closed"] for i, (s, d, _) in enumerate(SALES)], raw=True))
    site.json("/data/lots.json", [{"no": l["no"], "t": l["title"], "s": l["status"], "h": l["hammer"],
                                   "sale": SALES[l["sale"]][0]} for l in lots])
    site.page("/lots/", "Find a lot", """<h1>Find a lot</h1><p><input id="q" placeholder="Search lot titles" size="40">
<label><input type="checkbox" id="inc"> include withdrawn lots</label></p><div id="r"></div>""", index=False, scripts="""<script>
fetch('/data/lots.json').then(r=>r.json()).then(function(L){function go(){var q=document.getElementById('q').value.toLowerCase(),inc=document.getElementById('inc').checked;
document.getElementById('r').innerHTML='<table>'+L.filter(l=>(inc||l.s!=='withdrawn')&&l.t.toLowerCase().indexOf(q)>=0).map(l=>'<tr><td><a href="/lot/'+l.no+'/">Lot '+l.no+'</a></td><td>'+l.t+'</td><td>'+l.s+'</td><td>'+(l.h?l.h.toLocaleString()+' cr':'')+'</td></tr>').join('')+'</table>';}
document.getElementById('q').oninput=go;document.getElementById('inc').onchange=go;go();});</script>""")
    closed = sorted([l for l in lots if l["hammer"]], key=lambda l: -l["hammer"])
    site.page("/results/", "Results", "<h1>Top results of 412</h1>" + kit.table(
        ["Lot", "Title", "Sale", "Hammer"], [[f'<a href="/lot/{l["no"]}/">{l["no"]}</a>', esc(l["title"]),
                                             esc(SALES[l["sale"]][0]), f'{l["hammer"]:,} cr'] for l in closed[:25]], raw=True))
    site.page("/selling/", "Selling with us", "<h1>Selling with us</h1><p>Our seller's commission is 12%. We need proof "
              "of ownership and an address we can verify. Lots are photographed in our Gallowmead rooms.</p>")
    site.page("/", "Hollowmarket", f"<h1>Auctions of antiques, looms and curiosities</h1><p>Next sale: "
              f"<a href='/sale/{slug(SALES[4][0])}/'>{esc(SALES[4][0])}</a>, closing {SALES[4][1].long()}.</p>"
              "<div class='lots'>" + "".join(
                  f'<div class="lot"><a href="/lot/{l["no"]}/"><img src="/img/lot-{l["no"]}.svg" alt=""></a>'
                  f'<a href="/lot/{l["no"]}/">{esc(l["title"])}</a></div>' for l in [x for x in lots if x["status"] == "open"][:8])
              + "</div>")
    aske = next(l for l in lots if l["special"] == "aske")
    site.fact("hollowmarket-aske", "What was the hammer price of the punched ribbon fragment attributed to "
              "Temmet Aske at Hollowmarket?", f"{aske['hammer']:,} cr", f"/lot/{aske['no']}/")
    site.fact("hollowmarket-pointer-mark", "What repair mark is visible in the photograph of Hollowmarket "
              "lot 4471?", "Q.C. 331", "/lot/4471/", how="image", note="only in the lot image")
