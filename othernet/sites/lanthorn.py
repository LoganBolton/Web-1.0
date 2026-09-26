"""lanthorn.ves: the search engine of the Weave.

It indexes only the sites that allow it (about two thirds of the Weave) and
only pages marked as indexable. Ranking is BM25 over title and text, times a
"lantern rank" prior from inbound links. Since the Lamp update of 2 Bloom
412, personal .fol sites are demoted.
"""
import json
import math
import re
from collections import Counter, defaultdict

from ..engine.domains import SITES, url
from ..engine.web import esc

STOP = set("""a an and are as at be but by for from has have he her his i if in into is it its of on or our she so than that the their them then
there these they this to was we were what when which who will with you your not no yes can all any also more most other some such only one
two about after before over under up out just do does did been being very""".split())
TOK = re.compile(r"[a-z0-9]+")
K1, B = 1.2, 0.75
CAP = 400
BLOCK = 400

ADS = [
    (["slate", "vantle", "loom", "charger"], "Slate 7 deals on Bazaar", "bazaar.ves/deals", url("bazaar", "/deals/"), "Two faces. One price. Free postage over 40 cr."),
    (["ferry", "airship", "travel", "lanternport", "skylark"], "Fly the Skylark", "emberline.ves", url("emberline"), "Ostmere to Lanternport in 7h40."),
    (["news", "canal", "ashford", "gildmere", "deepshaft", "storm"], "THE CRIER: The stories they don't want you to read", "thecrier.wir",
     url("crier"), "Shouting the news since 401."),
    (["pith", "crossing", "telescope", "ossa"], "Pith Watcher 90 telescope", "bazaar.ves", url("bazaar", "/search/?q=pith+watcher"), "Made for 3 Mire."),
    (["loan", "bank", "rates", "money", "tally", "crown"], "Drovers' Bank home loans from 4.95%", "drovers.ves", url("drovers", "/loans/"), "Banking since 211."),
]

CSS = """
*{box-sizing:border-box}body{margin:0;font:15px/1.5 Arial,Helvetica,sans-serif;color:#202124;background:#fff}
.home{display:flex;flex-direction:column;align-items:center;margin-top:16vh}.home h1{font:bold 64px Georgia,serif;margin:0;color:#b45309;letter-spacing:-2px}
.home h1 span{color:#1e3a8a}.home input{width:560px;max-width:92vw;padding:12px 18px;border:1px solid #dfe1e5;border-radius:24px;font-size:16px}
.home .btns{margin-top:18px}.btn{background:#f8f9fa;border:1px solid #f8f9fa;padding:9px 16px;border-radius:4px;margin:0 4px;cursor:pointer}
.bar{display:flex;align-items:center;gap:20px;padding:16px 24px;border-bottom:1px solid #ebebeb}.bar a.logo{font:bold 28px Georgia,serif;color:#b45309;text-decoration:none}
.bar a.logo span{color:#1e3a8a}.bar input{width:520px;max-width:60vw;padding:9px 16px;border:1px solid #dfe1e5;border-radius:24px;font-size:15px}
.res{max-width:680px;margin-left:170px;padding:10px 0}.r{margin:22px 0}.r .u{color:#188038;font-size:13px}.r a.t{font-size:19px;color:#1a0dab;text-decoration:none}
.r a.t:hover{text-decoration:underline}.r .s{color:#4d5156;font-size:14px}.ad{background:#fff8e1;padding:8px 12px;border-radius:6px}.ad b.sp{font-size:12px}
.count{color:#70757a;font-size:13px}.pager a,.pager b{margin:0 6px;font-size:16px}em{font-style:normal;font-weight:bold}
footer{color:#70757a;font-size:13px;text-align:center;padding:30px}footer a{color:#70757a;margin:0 8px}
@media(max-width:800px){.res{margin:0 16px}}
"""


def tokens(s):
    return [t for t in TOK.findall(s.lower()) if t not in STOP and len(t) > 1]


def shard(term):
    return term[:2] if len(term) >= 2 else term + "_"


def build(web, site):
    site.write("/style.css", CSS)
    # --- inbound links across the whole Weave -----------------------------------
    inbound = Counter()
    domain_in = Counter()
    for s, p in web.all_pages():
        src_dom = s.domain
        for l in set(p.get("links", [])):
            tgt = l if l.endswith("/") or "." in l.rsplit("/", 1)[-1] else l
            inbound[tgt] += 1
            tdom = l.split("/")[2] if l.count("/") >= 2 else ""
            if tdom != src_dom:
                domain_in[tdom] += 1
    # --- documents ------------------------------------------------------------------------
    docs = []
    for key, s in web.sites.items():
        if key == "lanthorn" or not SITES[key][4]:
            continue
        for p in s.pages:
            if not p.get("index", True):
                continue
            docs.append((s.domain, p))
    postings = defaultdict(list)
    lengths = []
    tfs = []
    for i, (dom, p) in enumerate(docs):
        tf = Counter(tokens(p["text"]))
        for t in tokens(p["title"]):
            tf[t] += 3
        tfs.append(tf)
        lengths.append(sum(tf.values()))
    avgdl = sum(lengths) / max(1, len(lengths))
    df = Counter()
    for tf in tfs:
        df.update(tf.keys())
    N = len(docs)
    priors = []
    for dom, p in docs:
        u = p["url"]
        pr = 1 + 0.6 * math.log1p(inbound.get(u, 0)) + 0.25 * math.log1p(domain_in.get(dom, 0))
        if dom.endswith(".fol"):
            pr *= 0.45  # the Lamp update
        priors.append(round(pr, 3))
    for i, tf in enumerate(tfs):
        dl = lengths[i]
        for t, f in tf.items():
            idf = math.log(1 + (N - df[t] + 0.5) / (df[t] + 0.5))
            sc = idf * f * (K1 + 1) / (f + K1 * (1 - B + B * dl / avgdl))
            postings[t].append((i, sc))
    shards = defaultdict(dict)
    for t, pl in postings.items():
        pl.sort(key=lambda x: -x[1] * priors[x[0]])
        shards[shard(t)][t] = [[d, round(sc, 3)] for d, sc in pl[:CAP]]
    for sh, terms in shards.items():
        site.json(f"/idx/t/{sh}.json", terms)
    for b in range(0, N, BLOCK):
        block = []
        for dom, p in docs[b:b + BLOCK]:
            block.append([p["url"], p["title"], p["text"][:420]])
        site.json(f"/idx/d/{b // BLOCK}.json", block)
    site.json("/idx/meta.json", {"n": N, "block": BLOCK, "priors": priors, "ads": [[k, t, d, u, x] for k, t, d, u, x in ADS]})
    # --- pages ------------------------------------------------------------------------------
    foot = ('<footer><a href="/about/">About Lanthorn</a><a href="/help/">Search help</a><a href="/lantern-desk/">Lantern Desk</a>'
            '<a href="/advertise/">Advertise</a></footer>')
    site.raw_page("/", "Lanthorn", f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lanthorn</title><link rel="stylesheet" href="/style.css"></head><body><div class="home"><h1>Lant<span>horn</span></h1>
<form action="/search/"><p><input name="q" autofocus aria-label="Search the Weave"></p><div class="btns" style="text-align:center">
<button class="btn">Lanthorn Search</button> <button class="btn" name="lucky" value="1">I'm Feeling Kiln-Lucky</button></div></form>
<p class="count">Searching {N:,} pages across the Weave.</p></div>{foot}</body></html>""")
    site.raw_page("/search/", "Lanthorn search", f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lanthorn search</title><link rel="stylesheet" href="/style.css"></head><body><div class="bar"><a class="logo" href="/">Lant<span>horn</span></a>
<form action="/search/"><input name="q" id="q" aria-label="Search"></form></div><div class="res"><p class="count" id="count">Searching&hellip;</p><div id="ads"></div><div id="results"></div>
<div class="pager" id="pager"></div></div>{foot}
<script>
var STOP=new Set({json.dumps(sorted(STOP))});
function toks(s){{return (s.toLowerCase().match(/[a-z0-9]+/g)||[]).filter(t=>!STOP.has(t)&&t.length>1);}}
function shard(t){{return t.length>=2?t.slice(0,2):t+'_';}}
function esc(s){{return s.replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));}}
var P=new URLSearchParams(location.search),raw=(P.get('q')||'').trim(),page=parseInt(P.get('p')||'1');document.getElementById('q').value=raw;
var site=null,neg=[],q=raw.replace(/site:(\\S+)/g,function(_,s){{site=s.toLowerCase();return ' ';}}).replace(/(^|\\s)-(\\w+)/g,function(_,a,w){{neg.push(w.toLowerCase());return ' ';}});
var terms=[...new Set(toks(q))];
if(!raw){{document.getElementById('count').textContent='Type something to search the Weave.';}}
else fetch('/idx/meta.json').then(r=>r.json()).then(function(M){{
 var need=[...new Set(terms.concat(neg).map(shard))];
 Promise.all(need.map(s=>fetch('/idx/t/'+s+'.json').then(r=>r.ok?r.json():{{}}).catch(()=>({{}})))).then(function(parts){{
  var S={{}};parts.forEach(p=>Object.assign(S,p));
  var score={{}},hits={{}};
  terms.forEach(function(t){{(S[t]||[]).forEach(function(x){{score[x[0]]=(score[x[0]]||0)+x[1];hits[x[0]]=(hits[x[0]]||0)+1;}});}});
  var bad=new Set();neg.forEach(t=>(S[t]||[]).forEach(x=>bad.add(x[0])));
  var ids=Object.keys(score).map(Number).filter(d=>!bad.has(d));
  var all=ids.filter(d=>hits[d]===terms.length);if(all.length>=5||!terms.length)ids=all.length?all:ids;
  var ranked=ids.map(d=>[d,score[d]*M.priors[d]*(hits[d]===terms.length?1:0.35)]).sort((a,b)=>b[1]-a[1]);
  var blocks=[...new Set(ranked.map(x=>Math.floor(x[0]/M.block)))];
  function show(D){{
   var list=ranked.map(x=>[x,D[x[0]]]).filter(y=>y[1]&&(!site||y[1][0].indexOf('http://'+site)===0));
   document.getElementById('count').textContent='About '+list.length.toLocaleString()+' results'+(site?' on '+site:'');
   if(P.get('lucky')&&list.length){{location.replace(list[0][1][0]);return;}}
   var per=10,pages=Math.ceil(list.length/per);
   document.getElementById('results').innerHTML=list.slice((page-1)*per,page*per).map(function(y){{var d=y[1],txt=d[2],lo=txt.toLowerCase(),at=-1;
     terms.some(t=>{{at=lo.indexOf(t);return at>=0;}});var st=Math.max(0,at-60),snip=(st?'&hellip;':'')+esc(txt.slice(st,st+200))+'&hellip;';
     terms.forEach(t=>{{snip=snip.replace(new RegExp('\\\\b('+t+')','ig'),'<em>$1</em>');}});
     return '<div class="r"><div class="u">'+esc(d[0].replace('http://',''))+'</div><a class="t" href="'+esc(d[0])+'">'+esc(d[1])+'</a><div class="s">'+snip+'</div></div>';}}).join('')||
     '<p>No pages matched <b>'+esc(raw)+'</b>. Lanthorn cannot see every site. Try <a href="{url('hearthring')}">Hearthring</a>.</p>';
   var h='';for(var i=1;i<=Math.min(pages,10);i++){{P.set('p',i);h+=i===page?'<b>'+i+'</b>':'<a href="?'+P.toString()+'">'+i+'</a>';}}document.getElementById('pager').innerHTML=pages>1?h:'';
  }}
  var toLoad=blocks.slice(0,40),D={{}};
  Promise.all(toLoad.map(b=>fetch('/idx/d/'+b+'.json').then(r=>r.json()).then(a=>a.forEach((d,i)=>{{D[b*M.block+i]=d;}})))).then(()=>show(D));
  var ads=M.ads.filter(a=>a[0].some(k=>terms.indexOf(k)>=0)).slice(0,2);
  document.getElementById('ads').innerHTML=ads.map(a=>'<div class="r ad"><b class="sp">Sponsored</b> <span class="u">'+a[2]+'</span><br><a class="t" href="'+a[3]+'">'+esc(a[1])+'</a><div class="s">'+esc(a[4])+'</div></div>').join('');
 }});}});
</script></body></html>""", index=False)
    blocked = [SITES[k][0] for k in SITES if not SITES[k][4]]
    page = lambda title, body: f"""<!doctype html><html><head><meta charset="utf-8"><title>{esc(title)} - Lanthorn</title><link rel="stylesheet" href="/style.css"></head>
<body><div class="bar"><a class="logo" href="/">Lant<span>horn</span></a><form action="/search/"><input name="q"></form></div><div class="res">{body}</div>{foot}</body></html>"""
    site.raw_page("/about/", "About Lanthorn", page("About", f"""<h2>About Lanthorn</h2><p>Lanthorn was built in 398 by Nerys Lanterre and Elio Duvaine at
Lanternport University. It ranks pages by lantern rank: a page is important if important pages send lanterns (links) to it.</p>
<p>On 2 Bloom 412 we released the <b>Lamp update</b>, which gives more weight to pages many other sites point at. Personal pages on the .fol domain
now rank lower unless other sites link to them.</p><p>Lanthorn indexes {N:,} pages. Some sites ask us not to crawl them, and we respect that. We
currently do not index: {", ".join(blocked)}.</p><p>We cannot see what is behind a search box, a sign-in, or a script.</p>"""))
    site.raw_page("/help/", "Search help", page("Help", """<h2>Search help</h2><ul><li><b>site:</b> limit to one site, e.g. <code>canal site:registry.vey</code></li>
<li><b>-word</b> leave out pages with a word, e.g. <code>pith -crier</code></li><li>All words must match when possible. Order does not matter.</li>
<li>Lanthorn ignores small words like 'the' and 'of'.</li></ul>"""))
    site.raw_page("/lantern-desk/", "Lantern Desk", page("Lantern Desk", """<h2>Lantern Desk</h2><p>Want your site in Lanthorn, or ranked higher? Ask here.
Current wait: <b>up to one season</b>.</p><form onsubmit="event.preventDefault();this.innerHTML='<p>Thank you. You are number 18,412 in the queue.</p>'">
<p><input name="u" placeholder="Your site's address" style="width:360px;padding:8px"></p><button class="btn">Ask for a crawl</button></form>"""))
    site.raw_page("/advertise/", "Advertise", page("Advertise", "<h2>Advertise on Lanthorn</h2><p>Sponsored results appear above ordinary ones and are marked "
                                                               "'Sponsored'. Prices from 2 pennets a view.</p>"))
    site.fact("lanthorn-page-count", "How many pages does Lanthorn index?", f"{N:,}", "/about/")
