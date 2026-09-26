"""drovers.ves: Drovers' Bank. Exchange rates, a converter, loans, and branches."""
import json

from ..engine import kit, svg
from ..engine.rng import stream
from ..engine.web import esc
from ..world.addresses import address
from ..world.calendar import TODAY, MONTHS, date_range
from ..world.econ import RATES, CURRENCY_NAMES, CURRENCY_SYMBOL, YEAR_START
from ..world.geo import CITIES

SPREAD = 0.015
LOANS = [("Home loan (fixed 5 years)", 5.40), ("Home loan (variable)", 4.95), ("Barge and boat loan", 7.20),
         ("Personal loan", 9.80), ("Farm loan (Paper to Plough)", 3.90), ("Small trader loan", 8.25)]
SAVINGS = [("Everyday Purse", 0.50, "Instant access"), ("Drover's Hoard", 2.75, "90 days notice"),
           ("Hollowday Saver", 3.10, "Locked until the Hollowdays"), ("Child's Penny Jar", 3.50, "Under 16s")]

CSS = """
*{box-sizing:border-box}body{margin:0;font:15px/1.5 'Book Antiqua',Palatino,serif;background:#f7f5ef;color:#1c2b1c}
header{background:#14532d;color:#fefce8;padding:14px 28px;display:flex;align-items:center;gap:28px;flex-wrap:wrap}
header a{color:#fefce8;text-decoration:none}.logo{font:bold 24px Georgia,serif}.logo small{font-weight:normal;font-size:13px;opacity:.8;display:block}
nav a{margin-right:18px;font-family:Verdana,sans-serif;font-size:13px}
main{max-width:1060px;margin:0 auto;padding:22px}
.row{display:grid;grid-template-columns:1fr 1fr;gap:18px}.box{background:#fff;border:1px solid #d6d3c4;padding:16px;border-radius:3px}
h1,h2{color:#14532d;font-family:Georgia,serif}
table{border-collapse:collapse;width:100%;font-family:Verdana,sans-serif;font-size:13px}td,th{padding:6px;border-bottom:1px solid #e7e5da;text-align:left}th{background:#ecfccb}
input,select{padding:6px;font-size:15px}.big{font-size:26px;color:#14532d}
.warn{background:#fef9c3;border:1px solid #ca8a04;padding:10px;margin:12px 0}
footer{text-align:center;font:12px Verdana,sans-serif;color:#57534e;padding:24px;border-top:1px solid #d6d3c4;margin-top:30px}
img.chart{width:100%;height:auto;border:1px solid #e7e5da}
@media(max-width:800px){.row{grid-template-columns:1fr}}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} - Drovers' Bank</title>
<link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">Drovers' Bank<small>Banking since 211 CR</small></a>
<nav><a href="/rates/">Exchange rates</a><a href="/converter/">Converter</a><a href="/loans/">Loans</a>
<a href="/savings/">Savings</a><a href="/branches/">Branches</a><a href="/online/">Online banking</a></nav></header>
<main>{body}</main><footer>Drovers' Bank, Sallow Road, Ostmere. Registered with the Concordat Registry.
<a href="/security/">Staying safe</a> &middot; <a href="/about/">About us</a></footer>{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    cur_list = [c for c in RATES if c != "VCR"]
    # --- today's rates --------------------------------------------------------
    rows = []
    for c in cur_list:
        mid = RATES[c][TODAY]
        prev = RATES[c][TODAY - 1]
        rows.append([f"<a href='/rates/{c.lower()}/'>{esc(CURRENCY_NAMES[c])}</a>", c,
                     f"{mid:.4f}", f"{mid * (1 - SPREAD):.4f}", f"{mid * (1 + SPREAD):.4f}",
                     f"{1 / mid:.4f}", f"{(mid / prev - 1) * 100:+.2f}%"])
    table = kit.table(["Currency", "Code", "Mid (cr)", "We buy at (cr)", "We sell at (cr)", "Per crown",
                       "Day change"], rows, raw=True)
    site.page("/rates/", "Exchange rates", f"""<h1>Exchange rates</h1>
<p>Rates for {TODAY.full()}, in crowns for one unit of each currency. Updated at the tenth bell.</p>{table}
<p>We buy foreign notes at {SPREAD * 100:.1f}% under the mid rate and sell at {SPREAD * 100:.1f}% over it.</p>
<p><a href="/rates/history/">Rate history for 412</a> &middot; <a href="/converter/">Currency converter</a></p>""")
    site.fact("drovers-tally-rate", f"What was the mid rate of the Saltmarch tally in crowns at Drovers' Bank "
              f"on {TODAY.long()}?", f"{RATES['STL'][TODAY]:.4f}", "/rates/")
    # --- per currency history pages ------------------------------------------------
    days = list(date_range(YEAR_START, TODAY))
    for c in cur_list:
        vals = [RATES[c][d] for d in days]
        labels = [f"{d.day} {d.month_name[:3]}" for d in days]
        chart = svg.line_chart(vals, 900, 300, "#15803d", labels, f"{CURRENCY_NAMES[c]} in crowns, 412 CR", "{:.3f}")
        site.write(f"/img/rate-{c.lower()}.svg", chart)
        lo_d = min(days, key=lambda d: RATES[c][d])
        hi_d = max(days, key=lambda d: RATES[c][d])
        site.page(f"/rates/{c.lower()}/", CURRENCY_NAMES[c], f"""<h1>{esc(CURRENCY_NAMES[c])} ({c})</h1>
<img class="chart" src="/img/rate-{c.lower()}.svg" alt="Chart of the {esc(CURRENCY_NAMES[c])} against the crown in 412">
<p>Highest this year: {RATES[c][hi_d]:.4f} cr on {hi_d.long()}. Lowest: {RATES[c][lo_d]:.4f} cr on {lo_d.long()}.</p>
<p>Daily figures by month: {" ".join(f'<a href="/rates/history/{m:02d}/">{MONTHS[m - 1]}</a>' for m in range(1, TODAY.month + 1))}</p>""")
    for m in range(1, TODAY.month + 1):
        ds = [d for d in days if d.month == m]
        rows = [[d.long(), d.weekday] + [f"{RATES[c][d]:.4f}" for c in cur_list] for d in ds]
        site.page(f"/rates/history/{m:02d}/", f"Rates, {MONTHS[m - 1]} 412",
                  f"<h1>Mid rates, {MONTHS[m - 1]} 412</h1><p>Crowns per unit.</p>" + kit.table(
                      ["Date", "Day"] + cur_list, rows) +
                  f"<p>{'<a href=/rates/history/%02d/>&laquo; %s</a>' % (m - 1, MONTHS[m - 2]) if m > 1 else ''} "
                  f"{'<a href=/rates/history/%02d/>%s &raquo;</a>' % (m + 1, MONTHS[m]) if m < TODAY.month else ''}</p>")
    site.page("/rates/history/", "Rate history", "<h1>Rate history, 412 CR</h1><ul>" + "".join(
        f'<li><a href="/rates/history/{m:02d}/">{MONTHS[m - 1]} 412</a></li>' for m in range(1, TODAY.month + 1)) +
              "</ul><h2>Charts</h2><ul>" + "".join(f'<li><a href="/rates/{c.lower()}/">{CURRENCY_NAMES[c]}</a></li>'
                                                    for c in cur_list) + "</ul>")
    # --- converter -------------------------------------------------------------------
    rates_today = {c: RATES[c][TODAY] for c in RATES}
    opts = "".join(f'<option value="{c}">{esc(CURRENCY_NAMES[c])} ({CURRENCY_SYMBOL[c]})</option>' for c in RATES)
    site.page("/converter/", "Currency converter", f"""<h1>Currency converter</h1><div class="box">
<p><label>Amount <input id="amt" type="number" value="100" step="any"></label>
<label>from <select id="from">{opts}</select></label> <label>to <select id="to">{opts}</select></label></p>
<p><label><input type="checkbox" id="notes"> I am buying notes over the counter (our sell rate applies)</label></p>
<p class="big" id="out">&nbsp;</p><p><small>Rates of {TODAY.long()}. Tallies are shown in tallies and bits.</small></p></div>""",
              scripts=f"""<script>var R={json.dumps(rates_today)};
function fmt(v,c){{if(c==='STL'){{var w=Math.floor(v),b=Math.round((v-w)*12);if(b===12){{w++;b=0;}}return w.toLocaleString()+'t '+b+'b';}}
return v.toLocaleString(undefined,{{minimumFractionDigits:2,maximumFractionDigits:2}})+' '+{json.dumps(CURRENCY_SYMBOL)}[c];}}
function go(){{var a=parseFloat(document.getElementById('amt').value)||0,f=document.getElementById('from').value,t=document.getElementById('to').value;
var v=a*R[f]/R[t];if(document.getElementById('notes').checked&&f!==t)v=v/(1+{SPREAD});document.getElementById('out').textContent=fmt(v,t);}}
['amt','from','to','notes'].forEach(function(i){{document.getElementById(i).addEventListener('input',go);}});
document.getElementById('to').value='STL';go();</script>""")
    # --- loans -------------------------------------------------------------------------------
    site.page("/loans/", "Loans", f"""<h1>Loans</h1><div class="row"><div class="box"><h2>Our rates</h2>
{kit.table(["Loan", "Rate per year"], [[n, f"{r:.2f}%"] for n, r in LOANS])}
<p><small>Rates as of {TODAY.long()}. Farm loans are only for land registered under the Paper to Plough Act.</small></p></div>
<div class="box"><h2>What would I repay?</h2>
<p><label>Borrow <input id="p" type="number" value="20000"> cr</label></p>
<p><label>Loan <select id="r">{"".join(f'<option value="{r}">{esc(n)}</option>' for n, r in LOANS)}</select></label></p>
<p><label>Over <input id="y" type="number" value="10" min="1" max="30"> years</label></p>
<p>Repayment is made every month (ten a year). <b>Monthly repayment:</b> <span class="big" id="m"></span></p>
<p>Total repaid: <span id="t"></span></p></div></div>""", scripts="""<script>
function calc(){var P=+document.getElementById('p').value,r=+document.getElementById('r').value/100/10,n=+document.getElementById('y').value*10;
var m=r?P*r/(1-Math.pow(1+r,-n)):P/n;document.getElementById('m').textContent=m.toFixed(2)+' cr';document.getElementById('t').textContent=(m*n).toFixed(2)+' cr over '+n+' repayments';}
['p','r','y'].forEach(function(i){document.getElementById(i).addEventListener('input',calc);});calc();</script>""")
    site.page("/savings/", "Savings", "<h1>Savings</h1>" + kit.table(
        ["Account", "Interest per year", "Terms"], [[n, f"{r:.2f}%", t] for n, r, t in SAVINGS]))
    # --- branches --------------------------------------------------------------------------------
    rng = stream("drovers-branches")
    branches = []
    for c in CITIES:
        if c.nation not in ("VEY", "SLT"):
            continue
        for i in range(1 if c.population < 500_000 else rng.randint(2, 4)):
            line, pc = address(rng, c.name)
            district = rng.choice(c.districts) if c.districts else c.name
            hours = rng.choice(["Anvilday–Hearthday 9:00–16:00", "Anvilday–Plowday 9:30–15:30",
                                "Anvilday–Hearthday 8:30–17:00; Stillday closed"])
            services = rng.sample(["foreign notes", "safe boxes", "farm desk", "loom kiosk", "night slot",
                                   "mortgage clerk"], rng.randint(1, 4))
            branches.append({"name": f"{c.name} {district}" if district != c.name else c.name, "city": c.name,
                             "addr": f"{line}, {district}, {c.name} {pc}", "hours": hours,
                             "services": services})
    site.json("/data/branches.json", branches)
    rows = "".join(f"<tr><td><b>{esc(b['name'])}</b></td><td>{esc(b['addr'])}</td><td>{esc(b['hours'])}</td>"
                   f"<td>{esc(', '.join(b['services']))}</td></tr>" for b in branches)
    site.page("/branches/", "Find a branch", f"""<h1>Find a branch</h1>
<p><label>Filter by town <input id="flt" placeholder="e.g. Tarrow"></label>
<label><input type="checkbox" id="fx"> Only branches with foreign notes</label></p>
<table id="bt"><thead><tr><th>Branch</th><th>Address</th><th>Hours</th><th>Services</th></tr></thead><tbody>{rows}</tbody></table>
<p>Drovers' has no branches in the Holds, the Isles, or Oddavar. Customers there can use any Emberline ticket office
to draw up to 200 cr.</p>""", scripts="""<script>
function f(){var q=document.getElementById('flt').value.toLowerCase(),fx=document.getElementById('fx').checked;
document.querySelectorAll('#bt tbody tr').forEach(function(tr){var t=tr.innerText.toLowerCase();tr.style.display=(t.indexOf(q)>=0&&(!fx||t.indexOf('foreign notes')>=0))?'':'none';});}
document.getElementById('flt').addEventListener('input',f);document.getElementById('fx').addEventListener('change',f);</script>""")
    site.page("/online/", "Online banking", """<h1>Online banking</h1><div class="box">
<p><label>Customer number <input></label></p><p><label>Pass code <input type="password"></label></p>
<button onclick="document.getElementById('m').textContent='Online banking is unavailable while we move to new looms. Please visit a branch.';return false">Sign in</button>
<p id="m" class="warn" style="background:none;border:0"></p></div>""", index=False)
    site.page("/security/", "Staying safe", """<h1>Staying safe</h1><div class="warn">Drovers' Bank will never ask
for your pass code on Chatter, by loom-letter, or at your door.</div>
<p>In Gale 412 customers reported messages from an account called <b>@drovers_help_desk</b> on Chatter. It is
not ours. Our only Chatter account is <b>@droversbank</b>.</p>""")
    site.page("/about/", "About us", """<h1>About Drovers' Bank</h1><p>Drovers' Bank opened in 211 CR on the
Sallow road outside Ostmere, lending to cattle drovers on the way to market. Today it has branches across the
Concordat and Saltmarch.</p><p>Chair: Garrick Stanmore. Chief executive: Clemence Holloway.</p>
<p>Listed on the Brineholt Exchange as DRVB.</p>""")
    fx = "".join(f"<tr><td>{c}</td><td>{RATES[c][TODAY]:.4f}</td></tr>" for c in cur_list)
    site.page("/", "Drovers' Bank", f"""<div class="row"><div class="box"><h1>Good day.</h1>
<p>Home loans from <b>{min(r for _, r in LOANS[:2]):.2f}%</b>. Savings up to <b>{max(r for _, r, _ in SAVINGS):.2f}%</b>.</p>
<p><a href="/loans/">Work out a loan</a> &middot; <a href="/branches/">Find a branch</a></p></div>
<div class="box"><h2>Today's rates</h2><table><tr><th>Currency</th><th>Crowns</th></tr>{fx}</table>
<p><a href="/rates/">All rates</a></p></div></div>""")
