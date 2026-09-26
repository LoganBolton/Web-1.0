"""thecrier.wir: The Crier, a tabloid. Everything is rendered by script from JSON."""
import json

from ..engine import svg
from ..engine.rng import stream
from ..engine.web import esc
from ..world.calendar import ADate, TODAY, MONTHS
from ..world.stories import ALL_STORIES

GOSSIP = [
    (ADate(412, 8, 13), "JAGO'S SECRET SUPPER", "Lampwright star Jago Tidewright was spotted at "
     "Pearl & Pith in Marrowby with a mystery companion in a green hat. Staff say they shared the "
     "smoked eel and left by the kitchen door.", "Jago Tidewright"),
    (ADate(412, 8, 2), "NELL'S BRIDGE TOO FAR?", "Singer Nell Hedgecote cancelled her Saltspire "
     "date. Official reason: Storm Petrel. Crier reason: a row with the Spire's grumpy lighthouse "
     "keeper, who told the Crier the music was \"a noise fit to wake the Hollowdays\".",
     "Nell Hedgecote"),
    (ADate(412, 7, 25), "ROSCOE'S NEW RIDE", "Gulls striker Roscoe Brinecombe has bought a "
     "canal barge. Neighbours in Keelwater are NOT happy about the paint job (bright orange).",
     "Roscoe Brinecombe"),
    (ADate(412, 7, 11), "THE HIERARCH'S HAT", "The Crier has obtained a rare picture of the "
     "Oddavari Hierarch at the Frostgate opening. Readers say the hat is taller than last year. "
     "We measured: it is.", "Skeld Varrakin"),
    (ADate(412, 6, 8), "WARDEN'S WEEKEND", "First Warden Maelis Ondraker spent Stillday at the "
     "Gorse Hollow Cider Fair and bought six jugs. Is the Civic Ledger going soft?",
     "Maelis Ondraker"),
    (ADate(412, 5, 20), "KETTA'S HAMMER TIME", "Hammers captain Anvilmark Ketta has signed a "
     "boot deal with Coldforge Outfitters worth, we hear, 400,000 marks.", "Anvilmark Ketta"),
    (ADate(412, 4, 2), "SLATE BOSS'S SIX KETTLES", "Vantle chief Sabine Marwick owns six "
     "Kettlebright kettles, a former housekeeper tells the Crier. \"One for each mood.\"",
     "Sabine Marwick"),
]

SIGNS = [("The Anvil", "Rime"), ("The Kettle", "Thaw"), ("The Plough", "Loam"),
         ("The Lamp", "Bloom"), ("The Gull", "Blaze"), ("The Sheaf", "Crest"), ("The Rope", "Sheaf"),
         ("The Bell", "Gale"), ("The Eel", "Mire"), ("The Owl", "Dusk")]

CSS = """
body{margin:0;background:#fff;font-family:Impact,'Arial Black',Arial,sans-serif;color:#111}
.top{background:#e10600;padding:8px 16px;display:flex;align-items:center;gap:16px}
.top a.logo{font-size:54px;color:#fff;text-decoration:none;letter-spacing:-2px;text-shadow:3px 3px 0 #000}
.top nav a{color:#fff;font:bold 15px Arial,sans-serif;margin-right:14px;text-transform:uppercase}
.ticker{background:#ffe600;font:bold 14px Arial,sans-serif;padding:6px 16px;white-space:nowrap;overflow:hidden}
main{max-width:1000px;margin:0 auto;padding:16px;font-family:Arial,sans-serif}
.card{display:grid;grid-template-columns:200px 1fr;gap:12px;border-bottom:3px solid #e10600;padding:12px 0}
.card h2{font-family:Impact,'Arial Black',sans-serif;font-size:28px;margin:0;line-height:1.05}
.card h2 a{color:#111;text-decoration:none}.card img{width:200px;height:auto}
.story h1{font-family:Impact,'Arial Black',sans-serif;font-size:52px;line-height:1;margin:10px 0;text-transform:uppercase}
.story p{font-size:18px}.date{color:#e10600;font-weight:bold}
footer{background:#111;color:#aaa;padding:14px;text-align:center;font:12px Arial,sans-serif}
button.vote{font:bold 16px Arial;padding:10px 16px;margin:4px;background:#e10600;color:#fff;border:0;cursor:pointer}
.bar{height:22px;background:#e10600;color:#fff;font:bold 13px/22px Arial;padding-left:6px;margin:4px 0}
"""


def page(title, main_js, extra=""):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)}</title>
<style>{CSS}</style></head><body>
<div class="top"><a class="logo" href="/">THE CRIER</a><nav><a href="/">News</a><a href="/gossip.html">Gossip</a>
<a href="/stars.html">Stars</a><a href="/poll.html">Have Your Say</a></nav></div>
<div class="ticker" id="ticker">LOADING THE LATEST...</div>
<main id="app"><noscript>The Crier needs a loom with scripts switched on. Sorry!</noscript></main>
<footer>&copy; Crier Publishing, Ostmere. SHOUTING THE NEWS SINCE 401. {extra}</footer>
<script>
function esc(s){{return String(s).replace(/[&<>"]/g,function(c){{return {{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c];}});}}
fetch('/data/feed.json').then(function(r){{return r.json();}}).then(function(feed){{
  document.getElementById('ticker').textContent='BREAKING: '+feed.stories.slice(0,4).map(function(s){{return s.h;}}).join('  ★  ');
  {main_js}
}});
</script></body></html>"""


def build(web, site):
    stories = [s for s in ALL_STORIES if "crier" in s.outlets and s.date <= TODAY][::-1]
    feed = {"stories": [], "gossip": []}
    for s in stories:
        v = s.for_outlet("crier")
        img = f"/img/{s.id}.svg"
        site.write(img, svg.landscape(s.id + "crier", {"mine": "mountains", "storm": "sea",
                                                       "canal": "hills"}.get(s.image, "city")))
        feed["stories"].append({"id": s.id, "h": v["headline"].upper(), "d": s.date.long(),
                                "p": v["paras"], "img": img})
    for d, h, text, who in GOSSIP:
        gid = f"g-{d.iso()}"
        img = f"/img/{gid}.svg"
        site.write(img, svg.portrait(who, 200, 200, label=who))
        feed["gossip"].append({"id": gid, "h": h, "d": d.long(), "p": [text], "img": img})
    site.json("/data/feed.json", feed)

    card_js = """function card(s){return '<div class="card"><img src="'+s.img+'" alt=""><div><div class="date">'+esc(s.d)+'</div><h2><a href="/story.html?id='+s.id+'">'+esc(s.h)+'</a></h2><p>'+esc(s.p[0]).slice(0,160)+'...</p></div></div>';}"""
    site.raw_page("/", "The Crier", page("The Crier - SHOUTING THE NEWS", card_js +
                  "document.getElementById('app').innerHTML=feed.stories.concat(feed.gossip).sort(function(a,b){return 0;}).map(card).join('');"),
                  index=True)
    site.raw_page("/gossip.html", "Gossip", page("Gossip - The Crier", card_js +
                  "document.getElementById('app').innerHTML='<h1>GOSSIP</h1>'+feed.gossip.map(card).join('');"))
    site.raw_page("/story.html", "Story", page("The Crier", """
var id=new URLSearchParams(location.search).get('id');
var s=feed.stories.concat(feed.gossip).find(function(x){return x.id===id;});
if(!s){document.getElementById('app').innerHTML='<h1>STORY SPIKED!</h1><p>That story is not in the Crier (any more).</p>';return;}
document.title=s.h+' - The Crier';
document.getElementById('app').innerHTML='<div class="story"><div class="date">'+esc(s.d)+'</div><h1>'+esc(s.h)+'</h1><img src="'+s.img+'" style="width:100%;max-width:640px" alt=""><div>'+s.p.map(function(p){return '<p>'+esc(p)+'</p>';}).join('')+'</div><p><a href="/">&laquo; More SHOUTING</a></p></div>';
"""))
    # --- horoscopes -------------------------------------------------------
    rng = stream("stars", TODAY.iso())
    lines = ["A stranger on a ferry will offer you bad advice. Take it anyway.",
             "Pith is in your house of kettles. Avoid tea after dark.",
             "Money flows towards you like the Sallow in Thaw. Mind the locks.",
             "Someone in a green hat knows your secret.",
             "Do not trust a Slate charger this week.",
             "Your lucky number is 16. Your unlucky number is 14.",
             "A letter to the editor will change your life.",
             "Watch the sky on the third of Mire.",
             "Ossa is full and so is your heart. Also your inbox.",
             "Hollowdays come early for those who wait."]
    stars = [{"sign": s, "month": m, "text": rng.choice(lines), "lucky": rng.randint(1, 36)} for s, m in SIGNS]
    site.json("/data/stars.json", stars)
    site.raw_page("/stars.html", "Stars", page("Stars - The Crier", """
fetch('/data/stars.json').then(function(r){return r.json();}).then(function(st){
document.getElementById('app').innerHTML='<h1>YOUR STARS</h1><p>By Madame Ossabelle. Your sign is the month you were born in.</p>'+
st.map(function(x){return '<div class="card" style="grid-template-columns:1fr"><div><h2>'+esc(x.sign)+'</h2><div class="date">Born in '+x.month+'</div><p>'+esc(x.text)+' Lucky day: '+x.lucky+'.</p></div></div>';}).join('');});"""))
    # --- poll: results only after voting ---------------------------------------
    poll = {"q": "Is the moon Pith artificial?", "opts": ["Yes, obviously", "No, don't be daft",
                                                           "I'm not sure", "What is Pith?"],
            "pct": [38, 44, 15, 3], "votes": 12_906, "closes": "30 Gale 412"}
    site.json("/data/poll.json", poll)
    site.raw_page("/poll.html", "Have your say", page("Have Your Say - The Crier", """
fetch('/data/poll.json').then(function(r){return r.json();}).then(function(p){
 var app=document.getElementById('app'), voted=null; try{voted=localStorage.getItem('crier-poll');}catch(e){}
 function results(){app.innerHTML='<h1>'+esc(p.q)+'</h1><p>'+p.votes.toLocaleString()+' Crier readers have voted. Poll closes '+p.closes+'.</p>'+
   p.opts.map(function(o,i){return '<div>'+esc(o)+'</div><div class="bar" style="width:'+(p.pct[i]*6)+'px">'+p.pct[i]+'%</div>';}).join('')+
   '<p>Results are shown only to readers who have voted.</p>';}
 if(voted!==null){results();return;}
 app.innerHTML='<h1>HAVE YOUR SAY</h1><h2>'+esc(p.q)+'</h2>'+p.opts.map(function(o,i){return '<button class="vote" data-i="'+i+'">'+esc(o)+'</button>';}).join('')+'<p>Vote to see what other readers think!</p>';
 app.querySelectorAll('button.vote').forEach(function(b){b.onclick=function(){try{localStorage.setItem('crier-poll',b.dataset.i);}catch(e){} results();};});
});"""))
    site.fact("crier-poll", "What share of Crier readers voted that Pith is artificial?", "38%",
              "/poll.html", how="interaction", note="results appear only after voting")
