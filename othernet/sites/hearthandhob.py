"""hearthandhob.fol: Hearth & Hob, a recipe blog from Gorsefield. Long stories, then recipes, with a servings scaler."""
import json

from ..engine import kit, svg
from ..engine.domains import url
from ..engine.rings import widget
from ..engine.rng import stream, slug
from ..engine.web import esc
from ..world.calendar import ADate, TODAY

# title, serves, time (min), [(qty, unit, ingredient)], [steps], story, note
RECIPES = [
    ("Gorse Hollow apple cake", 8, 75, [(3, "", "sharp apples"), (1.5, "measure", "flour"), (0.75, "measure", "sugar"), (2, "", "eggs"),
                                        (0.5, "measure", "melted butter"), (1, "spoon", "baking salt"), (1, "spoon", "cinnamon bark")],
     ["Heat the oven to a middle heat (about 180 degrees Harl).", "Slice the apples thin.", "Whisk eggs and sugar pale, then fold in flour, salt and butter.",
      "Layer apples into the batter. Bake 50 minutes."], "My gran made this every Stillday of Sheaf, when the Gorse Hollow orchards drop their windfalls "
     "faster than anyone can pick them up. The Copper Kettle sells a version of it, but theirs has less cinnamon. Gran would say theirs is fine.", ""),
    ("Eel pie, Lowmarsh style", 6, 120, [(1, "weight", "eel, skinned and cut"), (2, "", "onions"), (1, "measure", "cider"), (0.5, "measure", "cream"),
                                         (1, "", "sheet of pastry"), (2, "spoon", "parsley")],
     ["Stew the eel in cider with the onions for 40 minutes.", "Stir in cream and parsley.", "Top with pastry and bake 35 minutes."],
     "Lowmarsh eel season closes during Bloom now, since the Eel Fisheries Act, so make this in any other month.", "Not in Bloom."),
    ("Smoked eel with sea-fennel", 2, 150, [(0.5, "weight", "eel"), (1, "handful", "sea-fennel tips"), (1, "spoon", "butter"), (1, "", "lemon")],
     ["Smoke the eel over alder for ninety minutes, no more.", "Wilt the sea-fennel in butter.", "Serve with lemon."],
     "I heard Delphine Estrande talk about this on Radio Lantern's Kitchen Tide and could not stop thinking about it. Pick sea-fennel at low water, green tips only, and never in Bloom when it flowers.",
     "Pick the green tips only; not in Bloom."),
    ("Seed cake that doesn't sink", 10, 70, [(2, "measure", "flour"), (1, "measure", "butter"), (1, "measure", "sugar"), (3, "", "eggs"),
                                             (2, "spoon", "caraway seed"), (0.25, "measure", "milk")],
     ["Cream butter and sugar for a full five minutes.", "Beat in eggs one at a time.", "Fold in flour, seed and milk.", "Bake 55 minutes. Don't open the door."],
     "The secret is not opening the oven door. Everyone opens the oven door.", ""),
    ("Kethren oat cakes", 12, 40, [(2, "measure", "oats"), (0.5, "measure", "butter"), (0.5, "spoon", "salt"), (0.5, "measure", "hot water")],
     ["Rub butter into oats and salt.", "Add water to make a stiff dough.", "Roll thin, cut rounds, bake 20 minutes."],
     "A friend from Stonemeet taught me these. Serve with smoked cheese, the Kethren way.", ""),
    ("Hollowday spice tea", 4, 15, [(4, "measure", "water"), (2, "spoon", "black tea"), (1, "", "stick of cinnamon bark"), (4, "", "cloves"),
                                    (2, "spoon", "honey")],
     ["Boil everything but the honey for five minutes.", "Strain, sweeten, drink by the fire."],
     "Five days of the year that belong to no month deserve their own tea.", ""),
    ("Quince jelly", 20, 240, [(2, "weight", "quinces"), (8, "measure", "water"), (2, "weight", "sugar"), (1, "", "lemon")],
     ["Simmer chopped quinces in water for an hour.", "Strain overnight through a cloth.", "Boil the juice with sugar until it sets."],
     "The colour goes from white to rose to amber. It feels like a trick every time.", ""),
    ("Moor mushroom soup", 4, 45, [(0.5, "weight", "moor mushrooms"), (1, "", "onion"), (3, "measure", "stock"), (0.5, "measure", "cream")],
     ["Soften onion.", "Add mushrooms, cook until dark.", "Add stock, simmer 20 minutes, blend, add cream."],
     "Pick only what you know. Wendmoor has three mushrooms that will kill you and one that will make you see Pith going the right way.", ""),
    ("Treacle tart, kiln-dark", 8, 60, [(1, "", "pastry case"), (1, "measure", "treacle"), (1, "measure", "breadcrumbs"), (1, "", "lemon")],
     ["Warm treacle, stir in crumbs and lemon.", "Pour into the case and bake 30 minutes until dark at the edges."], "", ""),
    ("Two-moon biscuits", 24, 35, [(2, "measure", "flour"), (1, "measure", "butter"), (0.5, "measure", "sugar"), (0.25, "measure", "ground almond")],
     ["Make a dough, roll, cut one big and one small round per biscuit.", "Stack small on big. Bake 15 minutes."], "Ossa and Pith, obviously.", ""),
]
UNITS = {"measure": ("measures", 1.0), "spoon": ("spoons", 1 / 16), "weight": ("weights", None), "handful": ("handfuls", None), "": ("", None)}


CSS = """
body{margin:0;background:#fffaf2;color:#3b2f24;font:17px/1.7 'Georgia',serif}
header{background:#c2410c;color:#fff;padding:18px;text-align:center}header a{color:#fff;text-decoration:none}header h1{margin:0;font:italic 40px Georgia,serif}
.wrap{max-width:760px;margin:0 auto;padding:22px}a{color:#c2410c}.story{color:#5b4a3a}
.card{background:#fff;border:2px solid #fed7aa;border-radius:10px;padding:18px;margin:24px 0}
.card h2{margin-top:0}.jump{display:inline-block;background:#c2410c;color:#fff;padding:6px 14px;border-radius:20px;text-decoration:none}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:16px}.grid img{width:100%;border-radius:8px}
.ad{background:#eee;color:#777;text-align:center;padding:30px;margin:20px 0;font:12px Arial}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Hearth &amp; Hob</title><link rel="stylesheet" href="/style.css"></head><body><header><a href="/"><h1>Hearth &amp; Hob</h1></a>
<div>Recipes from a Gorsefield kitchen</div></header><div class="wrap">{body}{widget('lamplit', 'hearthandhob')}</div>{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    rng = stream("hob")
    tiles = []
    for i, (title, serves, mins, ings, steps, story, note) in enumerate(RECIPES):
        s = slug(title)
        site.write(f"/img/{s}.svg", svg.product(rng.choice(["jar", "teapot", "box", "kettle"]), s, None))
        d = ADate(rng.randint(409, 412), rng.randint(1, 10), rng.randint(1, 36))
        d = min(d, TODAY - 3)
        story_long = [story or "Everyone asks me for this one.", "But first, a little about my week. " + rng.choice([
            "The hens have stopped laying again, which always happens when the Hollowdays are near.",
            "My neighbour's cider press broke, and I have been the unofficial mender of the lane.",
            "It rained for nine days straight. Gorsefield is one enormous puddle.",
            "I went to the cider fair and came home with more jugs than sense."]),
            "Anyway. You came for the recipe. Scroll down, or press the button."]
        ing_json = json.dumps([[q, u, n] for q, u, n in ings])
        body = f"""<p class="date">{d.long()}</p><h1>{esc(title)}</h1><p><a class="jump" href="#recipe">Jump to recipe</a></p>
<img src="/img/{s}.svg" alt="{esc(title)}" style="max-width:360px;width:100%">
<div class="story">{kit.paras(story_long)}</div><div class="ad">advertisement: Kettlebright K-40, the tea room kettle</div>
<div class="card" id="recipe"><h2>{esc(title)}</h2><p>Takes about {mins} minutes. <label>Serves <input id="sv" type="number" value="{serves}" min="1" style="width:60px"></label></p>
<h3>Ingredients</h3><ul id="ing"></ul><h3>Method</h3><ol>{"".join(f"<li>{esc(x)}</li>" for x in steps)}</ol>
{f"<p><b>Note:</b> {esc(note)}</p>" if note else ""}<p><small>1 measure = 16 spoons. 1 weight is about half a kilo.</small></p>
<p><button onclick="window.print()">Print</button></p></div>
<h3>Comments</h3>{"".join(f'<p><b>{rng.choice(["Bee", "Aunt Maud", "moss_kettle", "Corra from Tidewell", "Ivo"])}</b>: {rng.choice(["Made this, family loved it.", "Too much cinnamon for me.", "Can I use pears?", "Why is the story so long?", "Worked perfectly."])}</p>' for _ in range(rng.randint(1, 4)))}"""
        site.page(f"/recipe/{s}/", title, body, scripts=f"""<script>var I={ing_json},BASE={serves};
function fmt(q){{var w=Math.floor(q),f=q-w,fr=[[0,''],[.25,'¼'],[.33,'⅓'],[.5,'½'],[.67,'⅔'],[.75,'¾'],[1,'']];
var b=fr.reduce((a,c)=>Math.abs(c[0]-f)<Math.abs(a[0]-f)?c:a);if(b[0]===1){{w++;b=[0,'']}}return (w?w:'')+b[1]||'0';}}
function draw(){{var n=+document.getElementById('sv').value||BASE,k=n/BASE;document.getElementById('ing').innerHTML=I.map(function(x){{var q=x[0]*k,u=x[1];
if(u==='spoon'&&q>=16){{q=q/16;u='measure';}}return '<li>'+fmt(q)+' '+(u?u+(q>1?'s':'')+' ':'')+x[2]+'</li>';}}).join('');}}
document.getElementById('sv').oninput=draw;draw();</script>""")
        tiles.append(f'<div><a href="/recipe/{s}/"><img src="/img/{s}.svg" alt=""><br>{esc(title)}</a></div>')
    site.page("/", "Hearth & Hob", f"<p>Recipes from my kitchen in Gorse Hollow. Every one tested on my family, who are honest to a fault.</p><div class='grid'>{''.join(tiles)}</div>"
              f"<p>Friends: <a href='{url('wrenwrites')}'>Wren Writes</a> &middot; <a href='{url('copperkettle')}'>The Copper Kettle</a></p>")
    site.fact("hob-applecake-flour-16", "How much flour does the Hearth & Hob Gorse Hollow apple cake need for 16 people?", "3 measures",
              "/recipe/gorse-hollow-apple-cake/", how="interaction", note="recipe serves 8 with 1.5 measures; use the servings scaler")
