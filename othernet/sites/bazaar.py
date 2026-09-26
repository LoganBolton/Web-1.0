"""bazaar.ves: the largest marketplace on the Weave."""
import json

from ..engine import kit, links, svg
from ..engine.domains import url
from ..engine.rng import slug, stream
from ..engine.web import esc
from ..world.calendar import TODAY
from ..world.econ import RATES, CURRENCY_SYMBOL, fmt_money, convert
from ..world.products import PRODUCTS, SELLERS, SELLER, CATEGORIES

PER_PAGE = 24

CSS = """
*{box-sizing:border-box}body{margin:0;font:14px/1.45 Arial,Helvetica,sans-serif;background:#eaeded;color:#0f1111}
.top{background:#232f3e;display:flex;align-items:center;gap:14px;padding:8px 16px;color:#fff;flex-wrap:wrap}
.top a{color:#fff;text-decoration:none}.logo{font:bold 26px Georgia,serif;color:#fff}.logo span{color:#f7a52b}
.top form{flex:1;display:flex;min-width:260px}.top input{flex:1;padding:9px;border:0;border-radius:4px 0 0 4px;font-size:15px}
.top button{background:#f7a52b;border:0;padding:0 14px;border-radius:0 4px 4px 0;font-weight:bold}
.cartlink{font-weight:bold}.cartlink b{color:#f7a52b}
.cats{background:#37475a;padding:6px 16px}.cats a{color:#fff;margin-right:14px;text-decoration:none;font-size:13px}
main{max-width:1280px;margin:0 auto;padding:14px}
a{color:#007185}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px}
.tile{background:#fff;padding:10px;border-radius:4px;position:relative}
.tile img{width:100%;height:auto;background:#f7f7f5}.tile .t{font-size:14px;color:#0f1111;text-decoration:none;display:block;margin:6px 0;height:40px;overflow:hidden}
.price{font-size:20px;color:#0f1111}.approx{color:#565959;font-size:12px}
.stars{color:#de7921;letter-spacing:-1px}.muted{color:#565959;font-size:12px}
.spons{position:absolute;top:6px;left:6px;background:#fff;border:1px solid #ccc;font-size:10px;padding:1px 4px;color:#565959}
.panel{background:#fff;padding:16px;border-radius:4px;margin-bottom:14px}
.prod{display:grid;grid-template-columns:420px 1fr 260px;gap:20px}.prod img{width:100%;height:auto}
.buy{border:1px solid #d5d9d9;border-radius:8px;padding:14px}
.btn{display:block;width:100%;padding:10px;border-radius:20px;border:0;margin:6px 0;font-size:14px;cursor:pointer;background:#ffd814}
.btn.alt{background:#ffa41c}
table.specs td{padding:6px 10px;border-bottom:1px solid #eee}table.specs td:first-child{background:#f3f3f3;font-weight:bold;width:180px}
.review{border-bottom:1px solid #eee;padding:10px 0}.review.hidden{display:none}
.pager{margin:16px 0}.pager a,.pager b{display:inline-block;padding:5px 10px;background:#fff;border:1px solid #ddd;margin:2px}
.side{display:grid;grid-template-columns:220px 1fr;gap:16px}
.filters label{display:block;margin:4px 0}.filters input[type=number]{width:80px}
.hero{background:linear-gradient(90deg,#232f3e,#37475a);color:#fff;padding:26px;border-radius:4px;margin-bottom:14px}
.hero h1{margin:0 0 6px}
.toast{position:fixed;bottom:20px;right:20px;background:#067d62;color:#fff;padding:12px 18px;border-radius:6px;display:none}
footer{background:#232f3e;color:#ddd;text-align:center;padding:24px;margin-top:30px;font-size:12px}footer a{color:#ddd}
@media(max-width:1000px){.prod{grid-template-columns:1fr}.side{grid-template-columns:1fr}}
"""

CART_JS = """
<div class="toast" id="toast">Added to your basket</div>
<script>
function getCart(){try{return JSON.parse(localStorage.getItem('bazaar-cart')||'[]');}catch(e){return [];}}
function setCart(c){try{localStorage.setItem('bazaar-cart',JSON.stringify(c));}catch(e){} paintCount();}
function paintCount(){var n=getCart().reduce(function(a,x){return a+x.q;},0);var el=document.getElementById('cartn');if(el)el.textContent=n;}
function addToCart(id,q){var c=getCart(),f=c.find(function(x){return x.id===id;});if(f)f.q+=q;else c.push({id:id,q:q});setCart(c);
 var t=document.getElementById('toast');t.style.display='block';setTimeout(function(){t.style.display='none';},1600);}
paintCount();
</script>"""


def shell(site, title, body, **kw):
    cats = "".join(f'<a href="/c/{k}/">{esc(v[0])}</a>' for k, v in CATEGORIES.items())
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} : Bazaar</title>
<link rel="stylesheet" href="/style.css"></head><body>
<div class="top"><a class="logo" href="/">bazaar<span>.</span></a>
<form action="/search/" method="get"><input name="q" placeholder="Search Bazaar" aria-label="Search Bazaar"><button>Search</button></form>
<a href="/help/">Help</a><a href="/deals/">Deals</a><a class="cartlink" href="/cart/">Basket (<b id="cartn">0</b>)</a></div>
<div class="cats">{cats}<a href="/sellers/">Sellers</a></div>
<main>{body}</main>
<footer>Bazaar is run by Bazaar Holdings, Caddick Ford. Prices are set by sellers in their own currency;
crown estimates use today's Drovers' Bank rate. <a href="/help/">Help</a> &middot; <a href="/about/">About Bazaar</a></footer>
{CART_JS}{kw.get('scripts', '')}</body></html>"""


def stars(r):
    full = int(round(r))
    return "\u2605" * full + "\u2606" * (5 - full)


def price_html(p, big=True):
    s = SELLER[p.seller]
    if p.price == 0:
        return '<span class="price">Free</span>'
    main = fmt_money(p.price, s.currency)
    approx = "" if s.currency == "VCR" else f' <span class="approx">(about {convert(p.price, s.currency, "VCR"):,.2f} cr)</span>'
    return f'<span class="price">{main}</span>{approx}'


def tile(p):
    sp = '<span class="spons">Sponsored</span>' if p.sponsored else ""
    return (f'<div class="tile">{sp}<a href="/item/{p.id}/"><img src="/img/p/{p.id}.svg" alt="{esc(p.title)}" loading="lazy"></a>'
            f'<a class="t" href="/item/{p.id}/">{esc(p.title)}</a>'
            f'<div><span class="stars">{stars(p.rating)}</span> <span class="muted">{p.n_reviews:,}</span></div>'
            f'<div>{price_html(p)}</div>'
            f'<div class="muted">{"Out of stock" if p.stock == 0 else "Sold by " + esc(SELLER[p.seller].name)}</div></div>')


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    by_sub = {}
    for p in PRODUCTS:
        by_sub.setdefault((p.category, p.sub), []).append(p)
        label = p.model if p.category not in ("books",) else None
        site.write(f"/img/p/{p.id}.svg", svg.product(p.kind if p.kind != "charger" else "box", p.id, label))
    # --- product pages -------------------------------------------------------
    for p in PRODUCTS:
        s = SELLER[p.seller]
        lo, hi = s.ships_days
        arrive = (TODAY + lo, TODAY + hi)
        specs = "".join(f"<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>" for k, v in
                        [("Brand", p.brand), ("Model", p.model)] + p.specs)
        revs = "".join(
            f'<div class="review{" hidden" if i >= 3 else ""}"><b>{esc(r["who"])}</b> <span class="muted">from '
            f'{esc(r["city"])}</span><br><span class="stars">{stars(r["stars"])}</span> <span class="muted">'
            f'Reviewed {r["date"]}</span><p>{esc(r["text"])}</p><span class="muted">{r["helpful"]} people found '
            f'this helpful</span></div>' for i, r in enumerate(p.reviews))
        more = (f'<button class="btn" style="width:auto;padding:6px 16px" onclick="document.querySelectorAll(\'.review.hidden\')'
                f'.forEach(function(e){{e.classList.remove(\'hidden\')}});this.remove()">Show all {len(p.reviews)} reviews</button>'
                if len(p.reviews) > 3 else "")
        qa = "".join(f'<p><b>Q: {esc(q)}</b><br>A: {esc(a)} <span class="muted">({esc(who)})</span></p>' for q, a, who in p.qa)
        similar = [o for o in by_sub[(p.category, p.sub)] if o is not p][:6]
        extra_link = ""
        if p.category == "books" and p.link and p.brand == "Quillmere Press":
            extra_link = f'<p class="muted">Also at the publisher: <a href="{links.book(p.link)}">Quillmere Press</a></p>'
        body = f"""<div class="muted"><a href="/c/{p.category}/">{esc(CATEGORIES[p.category][0])}</a> &rsaquo;
<a href="/c/{p.category}/{slug(p.sub)}/">{esc(p.sub)}</a></div>
<div class="panel prod"><div><img src="/img/p/{p.id}.svg" alt="{esc(p.title)}"></div>
<div><h1 style="font-size:24px;font-weight:normal">{esc(p.title)}</h1>
<div>Brand: <a href="/search/?q={esc(p.brand)}">{esc(p.brand)}</a></div>
<div><span class="stars">{stars(p.rating)}</span> {p.rating} out of 5 &middot; {p.n_reviews:,} ratings</div><hr>
<div>{price_html(p)}</div><p>{"".join(f"{esc(x)} " for x in p.description)}</p>
<h3>Details</h3><table class="specs">{specs}</table>{extra_link}</div>
<div class="buy">{price_html(p)}<p>{"<b style='color:#b12704'>Currently unavailable.</b>" if p.stock == 0 else
f"Arrives between <b>{arrive[0].long()}</b> and <b>{arrive[1].long()}</b>."}</p>
<p>{"" if p.stock == 0 else ("<span style='color:#b12704'>Only " + str(p.stock) + " left in stock.</span>" if p.stock < 10 else "<span style='color:#067d62'>In stock</span>")}</p>
<label>Quantity <select id="qty">{"".join(f"<option>{i}</option>" for i in range(1, 6))}</select></label>
<button class="btn" {"disabled" if p.stock == 0 else ""} onclick="addToCart('{p.id}',+document.getElementById('qty').value)">Add to basket</button>
<p class="muted">Sold by <a href="/seller/{s.id}/">{esc(s.name)}</a> of {esc(s.city)}.<br>Returns: {esc(s.returns)}</p></div></div>
<div class="panel"><h2>Questions and answers</h2>{qa or '<p class="muted">No questions yet.</p>'}</div>
<div class="panel"><h2>Customer reviews</h2>{revs or '<p class="muted">No reviews yet.</p>'}{more}</div>
<div class="panel"><h2>Customers also viewed</h2><div class="grid">{"".join(tile(o) for o in similar)}</div></div>"""
        site.page(f"/item/{p.id}/", p.title, body)
    # --- category listings -----------------------------------------------------
    for cat, (cname, subs) in CATEGORIES.items():
        items_all = [p for p in PRODUCTS if p.category == cat]
        sub_links = "".join(f'<li><a href="/c/{cat}/{slug(s)}/">{esc(s)}</a> ({len(by_sub.get((cat, s), []))})</li>' for s in subs)
        for key, items, title in [(f"/c/{cat}/", items_all, cname)] + [
                (f"/c/{cat}/{slug(s)}/", by_sub.get((cat, s), []), s) for s in subs]:
            items = sorted(items, key=lambda p: (not p.sponsored, -p.n_reviews * p.rating))
            pages = kit.chunks(items, PER_PAGE)
            for i, chunk in enumerate(pages, start=1):
                path = key if i == 1 else f"{key}page/{i}/"
                site.page(path, title, f"""<div class="side"><div class="panel filters"><h3>{esc(cname)}</h3><ul>{sub_links}</ul>
<p class="muted">Want to filter by price or rating? Use <a href="/search/?cat={cat}">advanced search</a>.</p></div>
<div><h1 style="font-size:22px">{esc(title)} <span class="muted">({len(items)} results, page {i} of {len(pages)})</span></h1>
<div class="grid">{"".join(tile(p) for p in chunk)}</div>{kit.pager(key, i, len(pages))}</div></div>""")
    # --- sellers ------------------------------------------------------------------
    for s in SELLERS:
        items = [p for p in PRODUCTS if p.seller == s.id]
        site.page(f"/seller/{s.id}/", s.name, f"""<div class="panel"><h1>{esc(s.name)}</h1>
<p>{"<b>Official store.</b> " if s.official else ""}Based in {esc(s.city)}. Selling on Bazaar since {s.since} CR.
Prices in {esc({'VCR': 'crowns', 'STL': 'tallies', 'KMK': 'marks', 'PLM': 'lumes', 'OSK': 'skeds'}[s.currency])}.</p>
<p><span class="stars">{stars(s.rating)}</span> {s.rating} from {s.ratings:,} buyers. Ships in {s.ships_days[0]}\u2013{s.ships_days[1]} days.
Returns: {esc(s.returns)}.</p></div>
<div class="panel"><h2>{len(items)} items</h2><div class="grid">{"".join(tile(p) for p in items[:60])}</div></div>""")
    site.page("/sellers/", "Sellers", "<div class='panel'><h1>Sellers on Bazaar</h1>" + kit.table(
        ["Seller", "Based in", "Since", "Rating", "Ratings"],
        [[f'<a href="/seller/{s.id}/">{esc(s.name)}</a>', esc(s.city), str(s.since), str(s.rating), f"{s.ratings:,}"]
         for s in sorted(SELLERS, key=lambda s: s.name)], raw=True, sortable=True) + "</div>" + kit.SORTABLE_JS)
    # --- search index and page ----------------------------------------------------------
    rates = {c: RATES[c][TODAY] for c in RATES}
    index = [{"id": p.id, "t": p.title, "b": p.brand, "c": p.category, "s": p.sub, "p": p.price,
              "cur": SELLER[p.seller].currency, "r": p.rating, "n": p.n_reviews, "st": p.stock,
              "sp": p.sponsored} for p in PRODUCTS]
    site.json("/data/index.json", {"rates": rates, "items": index})
    cat_opts = "".join(f'<option value="{k}">{esc(v[0])}</option>' for k, v in CATEGORIES.items())
    site.page("/search/", "Search", f"""<div class="side"><form class="panel filters" id="f">
<h3>Refine</h3><label>Words <input name="q" id="q"></label>
<label>Category <select name="cat" id="cat"><option value="">All</option>{cat_opts}</select></label>
<label>Price in crowns from <input type="number" name="min" id="min"> to <input type="number" name="max" id="max"></label>
<label>At least <select name="stars" id="stars"><option value="0">any</option><option>3</option><option>4</option><option>4.5</option></select> stars</label>
<label><input type="checkbox" name="instock" id="instock"> In stock only</label>
<label>Sort <select name="sort" id="sort"><option value="rel">Relevance</option><option value="lo">Price: low to high</option>
<option value="hi">Price: high to low</option><option value="rev">Most reviewed</option><option value="rat">Best rated</option></select></label>
<button class="btn">Apply</button></form>
<div><div id="count" class="muted"></div><div class="grid" id="res"></div><div id="pg" class="pager"></div></div></div>""",
              index=False, scripts="""<script>
var P=new URLSearchParams(location.search);['q','cat','min','max','stars','sort'].forEach(function(k){var e=document.getElementById(k);if(e&&P.get(k))e.value=P.get(k);});
document.getElementById('instock').checked=P.get('instock')==='on';
var SYM={VCR:'cr',STL:'tl',KMK:'mk',PLM:'lm',OSK:'sk'};
function money(v,c){if(v===0)return 'Free';if(c==='STL'){var w=Math.floor(v),b=Math.round((v-w)*12);if(b===12){w++;b=0;}return w.toLocaleString()+'t '+b+'b';}return v.toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})+' '+SYM[c];}
fetch('/data/index.json').then(function(r){return r.json();}).then(function(D){
 var q=(P.get('q')||'').toLowerCase().trim(),words=q?q.split(/\\s+/):[],cat=P.get('cat')||'',mn=parseFloat(P.get('min')),mx=parseFloat(P.get('max')),
 st=parseFloat(P.get('stars')||'0'),sort=P.get('sort')||'rel',ins=P.get('instock')==='on',page=parseInt(P.get('page')||'1');
 var res=D.items.map(function(x){x.cr=x.p*D.rates[x.cur];var hay=(x.t+' '+x.b+' '+x.s).toLowerCase();x.score=0;
   words.forEach(function(w){if(hay.indexOf(w)>=0)x.score+=(x.t.toLowerCase().indexOf(w)>=0?2:1);});x.score+=x.sp?0.5:0;return x;})
  .filter(function(x){return (!words.length||words.every(function(w){return (x.t+' '+x.b+' '+x.s).toLowerCase().indexOf(w)>=0;}))
    &&(!cat||x.c===cat)&&(isNaN(mn)||x.cr>=mn)&&(isNaN(mx)||x.cr<=mx)&&x.r>=st&&(!ins||x.st>0);});
 var S={lo:function(a,b){return a.cr-b.cr;},hi:function(a,b){return b.cr-a.cr;},rev:function(a,b){return b.n-a.n;},rat:function(a,b){return b.r-a.r||b.n-a.n;},
   rel:function(a,b){return b.score-a.score||b.n-a.n;}};res.sort(S[sort]||S.rel);
 var per=24,pages=Math.max(1,Math.ceil(res.length/per));
 document.getElementById('count').textContent=res.length+' results'+(q?' for "'+q+'"':'')+(pages>1?', page '+page+' of '+pages:'');
 document.getElementById('res').innerHTML=res.slice((page-1)*per,page*per).map(function(x){
  return '<div class="tile">'+(x.sp?'<span class="spons">Sponsored</span>':'')+'<a href="/item/'+x.id+'/"><img src="/img/p/'+x.id+'.svg" alt=""></a><a class="t" href="/item/'+x.id+'/">'+x.t.replace(/</g,'&lt;')+'</a>'+
  '<div class="stars">'+'\\u2605'.repeat(Math.round(x.r))+'\\u2606'.repeat(5-Math.round(x.r))+' <span class="muted">'+x.n+'</span></div><span class="price">'+money(x.p,x.cur)+'</span>'+
  (x.cur!=='VCR'?' <span class="approx">(about '+x.cr.toFixed(2)+' cr)</span>':'')+(x.st===0?'<div class="muted">Out of stock</div>':'')+'</div>';}).join('')||'<p>No results. Try fewer words.</p>';
 var h='';for(var i=1;i<=pages;i++){P.set('page',i);h+=(i===page?'<b>'+i+'</b>':'<a href="?'+P.toString()+'">'+i+'</a>');}
 document.getElementById('pg').innerHTML=pages>1?h:'';
});</script>""")
    # --- cart and checkout -----------------------------------------------------------------
    site.page("/cart/", "Your basket", """<div class="panel"><h1>Your basket</h1><div id="lines">Loading&hellip;</div>
<p id="total" style="font-size:18px"></p><a class="btn alt" style="width:260px;text-align:center;text-decoration:none;color:#111" href="/checkout/">Proceed to checkout</a>
<button class="btn" style="width:260px" onclick="setCart([]);location.reload()">Empty basket</button></div>""", index=False,
              scripts="""<script>
fetch('/data/index.json').then(function(r){return r.json();}).then(function(D){
 var by={};D.items.forEach(function(x){by[x.id]=x;});var c=getCart(),tot=0;
 document.getElementById('lines').innerHTML=c.length?'<table class="specs">'+c.map(function(l,i){var x=by[l.id];if(!x)return '';var cr=x.p*D.rates[x.cur]*l.q;tot+=cr;
  return '<tr><td><a href="/item/'+x.id+'/">'+x.t+'</a></td><td>'+l.q+' &times;</td><td>'+cr.toFixed(2)+' cr</td><td><a href="#" onclick="var c=getCart();c.splice('+i+',1);setCart(c);location.reload();return false">remove</a></td></tr>';}).join('')+'</table>':'<p>Your basket is empty.</p>';
 var ship=tot>0&&tot<40?4.5:0;
 document.getElementById('total').innerHTML=c.length?'Items: '+tot.toFixed(2)+' cr<br>Postage: '+(ship?ship.toFixed(2)+' cr (free over 40 cr)':'free')+'<br><b>Total: '+(tot+ship).toFixed(2)+' cr</b>':'';
});</script>""")
    site.page("/checkout/", "Checkout", """<div class="panel"><h1>Checkout</h1>
<form id="co"><p><label>Full name<br><input id="nm" required size="40"></label></p>
<p><label>Street and number<br><input id="st" required size="40"></label></p>
<p><label>Town<br><input id="tw" required size="30"></label></p>
<p><label>Postcode<br><input id="pc" required size="14"></label> <span class="muted">Concordat postcodes look like <b>OS 4 12</b>; Saltmarch like <b>BH-1 204</b>. Look yours up at the Concordat Post.</span></p>
<p><label>Pay with <select id="pay"><option>Drovers' Bank slip</option><option>Tally note</option><option>Pay on delivery (+2 cr)</option></select></label></p>
<button class="btn alt" style="width:260px">Place order</button></form><div id="done"></div></div>""", index=False,
              scripts="""<script>
document.getElementById('co').addEventListener('submit',function(e){e.preventDefault();
 var pc=document.getElementById('pc').value.trim().toUpperCase(), c=getCart();
 var ok=/^[A-Z]{2} \\d{1,2} \\d{1,2}$/.test(pc)||/^[A-Z]{2}-\\d \\d{3}$/.test(pc)||/^[A-Z]\\d-\\d{2}$/.test(pc)||/^[A-Z]{2}\\/\\d{3}$/.test(pc);
 var out=document.getElementById('done');
 if(!c.length){out.innerHTML='<p style="color:#b12704">Your basket is empty.</p>';return;}
 if(!ok){out.innerHTML='<p style="color:#b12704">That postcode does not look right. Please check it with the Concordat Post.</p>';return;}
 var s=JSON.stringify(c)+pc,h=0;for(var i=0;i<s.length;i++)h=(Math.imul(h,31)+s.charCodeAt(i))>>>0;
 out.innerHTML='<h2>Thank you!</h2><p>Your order number is <b>BZO-'+(h%900000+100000)+'</b>. We have sent a slip to your loom.</p>';
 setCart([]);});</script>""")
    # --- deals, help, about, home --------------------------------------------------------------
    rng = stream("deals", TODAY.iso())
    deals = rng.sample([p for p in PRODUCTS if p.stock > 0 and p.price > 0], 12)
    site.page("/deals/", "Today's deals", f"""<div class="hero"><h1>Today's deals</h1>
<p>Ends in <b id="cd">&hellip;</b>. Prices shown already include the deal.</p></div><div class="grid">{"".join(tile(p) for p in deals)}</div>""",
              scripts="""<script>(function(){var end=Date.now()+((7*3600+41*60+12)*1000);setInterval(function(){var s=Math.max(0,Math.floor((end-Date.now())/1000));
document.getElementById('cd').textContent=Math.floor(s/3600)+'h '+Math.floor(s%3600/60)+'m '+(s%60)+'s';},1000);})();</script>""")
    site.page("/help/", "Help", """<div class="panel"><h1>Help</h1>
<h3>Currencies</h3><p>Sellers set prices in their own currency: crowns (cr) in Veyl, tallies and bits (t, b) in
Saltmarch, marks (mk) in the Holds, lumes (lm) in the Isles. The basket totals everything in crowns at today's
Drovers' Bank rate.</p>
<h3>Postage</h3><p>Postage is free on baskets over 40 crowns. Below that it is 4.50 cr.</p>
<h3>Returns</h3><p>Each seller sets its own returns policy. Official stores accept returns within 30 days.</p>
<h3>Recalls</h3><p>For the Slate 7 charger recall (VC-7A), see <a href="http://vantle.ves/support/recall-vc7a/">Vantle's recall page</a>.</p>
<h3>Oddavar</h3><p>Bazaar cannot deliver beyond the Frostgate Wall.</p></div>""")
    site.page("/about/", "About Bazaar", """<div class="panel"><h1>About Bazaar</h1><p>Bazaar was started by Edric
Hollowell in Caddick Ford in 396 CR as a list of second-hand loom parts. Today it is run by Bazaar Holdings, which
also owns Reelhouse.</p></div>""")
    top = sorted([p for p in PRODUCTS if p.stock > 0], key=lambda p: -p.n_reviews)[:12]
    new = sorted([p for p in PRODUCTS if p.listed], key=lambda p: p.listed, reverse=True)[:12]
    site.page("/", "Bazaar", f"""<div class="hero"><h1>The Slate 7 is here.</h1><p>Two glass faces. From 1,299 cr.
<a style="color:#f7a52b" href="/item/{PRODUCTS[0].id}/">Shop now</a></p></div>
<div class="panel"><h2>Shop by category</h2><div class="grid">{"".join(f'<div class="tile"><a href="/c/{k}/"><b>{esc(v[0])}</b></a><div class="muted">{", ".join(v[1][:3])}</div></div>' for k, v in CATEGORIES.items())}</div></div>
<div class="panel"><h2>Most popular</h2><div class="grid">{"".join(tile(p) for p in top)}</div></div>
<div class="panel"><h2>New on Bazaar</h2><div class="grid">{"".join(tile(p) for p in new)}</div></div>""")
    site.fact("bazaar-k40-power", "What is the power rating of the Kettlebright K-40 Voltaic Kettle?",
              "2,200 fenwicks", f"/item/{next(p.id for p in PRODUCTS if p.model == 'K-40')}/")
    site.fact("bazaar-pw90-aperture", "What aperture does the Ossa Optics Pith Watcher 90 have?", "90 thumbs",
              f"/item/{next(p.id for p in PRODUCTS if p.model == 'PW-90')}/")
