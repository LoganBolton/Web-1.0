"""lexicon.hal: The Veylish Lexicon. Words that a visitor from elsewhere would not know."""
from ..engine.rng import slug, stream
from ..engine.web import esc
from ..world.calendar import TODAY

# headword, part of speech, definitions, etymology, first recorded (CR), example
WORDS = [
    ("loom", "n.", ["A thinking engine; a machine that follows instructions punched or woven into it.", "Any device that holds a Weave connection."],
     "From the weaving loom, after Temmet Aske's engine of reeds and ribbons.", 367, "She left her loom running all night."),
    ("Weave", "n.", ["The linked network of looms spanning Averra.", "(lower case) A unit of loom memory: a million reeds."],
     "From the weaving of many threads into cloth.", 390, "Is the library on the Weave yet?"),
    ("reed", "n.", ["The smallest unit of loom memory, holding yes or no."], "From the brass reeds of the first Loom.", 367, "A slip of eight reeds."),
    ("ribbon", "n.", ["A set of instructions for a loom; a program.", "A file kept on a loom.", "A paper posted before review."],
     "From the punched linen ribbons of the first Loom.", 367, "Send me the ribbon when it's done."),
    ("shuttle", "n.", ["The part of a loom that carries out instructions, one at a time."], "Weaving term.", 372, "The Slate 7 has eight shuttles."),
    ("lantern", "n.", ["A link from one page of the Weave to another.", "A lamp."], "From 'lantern rank', Lanthorn's ranking method.", 398,
     "Nobody sends lanterns to my page any more."),
    ("loom-letter", "n.", ["A message sent from one loom to another."], "Compound.", 388, "Reply by loom-letter."),
    ("loom-call", "n.", ["A spoken call over the wire or the Weave."], "Compound.", 395, "Give me a loom-call on +41 400 1122."),
    ("slate", "n.", ["A handheld loom with a glass face.", "Writing slate."], "From the writing slates of schoolrooms; popularised by Vantle.", 409,
     "She read the news on her slate."),
    ("crumb", "n.", ["A small record a Weave site leaves on a visitor's loom to remember them."], "From 'breadcrumb'.", 396,
     "Accept all crumbs?"),
    ("tended domain", "n.", ["One of the endings of Weave addresses, each tended by a guild: .ves (commerce), .fol (folk), .hal (halls of "
     "learning), .gld (guilds), .wir (news wires)."], "From the Open Weave Charter.", 390, "Personal pages live in the .fol tended domain."),
    ("fenwick", "n.", ["A unit of voltaic power. A kettle draws about two thousand."], "After Idra Fenwick, inventor of the voltaic lamp.", 301,
     "A 2,200-fenwick kettle."),
    ("ell", "n.", ["A unit of length, a little over a metre. Forty thumbs."], "Old Veylish.", -50, "The canal is eighteen ells wide."),
    ("thumb", "n.", ["A unit of length; a fortieth of an ell."], "Old Veylish.", -50, "Nine thumbs of ribbon."),
    ("league", "n.", ["A unit of distance: 4,000 ells."], "Old Veylish. The Kethren league was once 4,400 ells.", 118, "Sixty-two leagues of canal."),
    ("weight", "n.", ["A unit of mass, about half a kilogram. Abbreviated wt."], "Market usage.", 20, "A bag of 12 wt."),
    ("measure", "n.", ["A unit of volume for cooking, about a quarter of a litre."], "Kitchen usage.", 60, "Two measures of milk."),
    ("bell", "n.", ["An hour of the day, counted from midnight: 'the sixth bell' is six in the morning. Now mostly formal or old-fashioned."],
     "From the bells of the Ostmere Registry.", 12, "The Moot sits at the ninth bell."),
    ("Hollowdays", "n. pl.", ["The five days at the end of the year that belong to no month."], "From 'hollow', empty.", 0,
     "Debts under five crowns are forgiven at the Hollowdays."),
    ("Stillday", "n.", ["The sixth day of the week, the day of rest."], "From 'still'.", 0, "The shop is closed on Stilldays."),
    ("tally", "n.", ["The currency of Saltmarch, divided into twelve bits.", "A notched stick for counting."], "From the salt tallies.", 37,
     "Four tallies and seven bits."),
    ("bit", "n.", ["A twelfth of a tally.", "(Kethric, in loom talk) sometimes used for a reed, which confuses everyone."], "Marcher.", 37,
     "Five bits for a tram ride."),
    ("pennet", "n.", ["A hundredth of a crown."], "From 'penny'.", 5, "Forty-five pennets for a letter."),
    ("crown", "n.", ["The currency of the Concordat of Veyl."], "From the crown stamped on early coins.", 3, "It costs twelve crowns."),
    ("mark", "n.", ["The currency of the Kethren Holds, of 100 chips."], "Kethric 'merk', a cut on a rod.", -500, "A fine of 4.2 million marks."),
    ("lume", "n.", ["The currency of the Pellucid Isles, of 100 glints."], "Pellish 'lume', light.", 154, "Lodging costs 110 lumes a month."),
    ("sked", "n.", ["The currency of Oddavar."], "Oddic.", -900, "Nobody outside Vesk has seen a sked note."),
    ("delve", "n.", ["(Kethric) A mine working or gallery.", "A district of a hold-city that lies below ground."], "Kethric.", -880,
     "The eastern delve of Deepshaft 9."),
    ("tier", "n.", ["(Kethric) A level of a hold-city, counted from the top."], "Kethric.", -880, "The museum is on the fourth tier."),
    ("hold-price", "n.", ["(Kethric) A fine paid to the Moot of Holds."], "Kethric.", -600, "A hold-price of 4,200,000 marks."),
    ("writ of passage", "n.", ["Permission for outsiders to cross into the Holds."], "Kethric legal usage.", 246, "The crew waited two days for a writ."),
    ("clan-right", "n.", ["A right held by a whole Kethren clan."], "Kethric.", -700, "The forge is held by clan-right."),
    ("rim", "n.", ["(vaultball) The edge of the opposing well; landing the ball on it scores three.", "The edge of a circle."], "Old Veylish.", 290,
     "Two rims in the first half."),
    ("well", "n.", ["(vaultball) The hole in the vault floor; putting the ball in scores five."], "Old Veylish.", 290, "A well from the halfway line!"),
    ("vault", "n.", ["(vaultball) The sunken pitch."], "Old Veylish.", 288, "The vault was flooded after the storm."),
    ("rim ratio", "n.", ["The rim of a circle divided by its span, about 3.14159."], "Numerists' usage.", 244, "Merrowby's series for the rim ratio."),
    ("Kiln constant", "n.", ["The base of continuous growth, about 2.71828."], "After the Ember Kilns, where it was first used to reckon glass cooling.", 212,
     "Interest compounds towards the Kiln constant."),
    ("Marcher", "adj.", ["Of Saltmarch.", "(of digits) Of twelve-fold counting."], "From Saltmarch.", 37, "Marcher digits."),
    ("the Reach", "n.", ["The Grey Reach, the sea north of Veyl; loosely, Saltmarch and its waters."], "Marcher.", 40, "News of the Reach."),
    ("ossalight", "n.", ["Light of the moon Ossa."], "Compound.", 150, "They walked home by ossalight."),
    ("Pithstruck", "adj.", ["(informal) Behaving strangely; believed to be caused by Pith."], "Folk usage.", 200, "He's gone Pithstruck again."),
    ("double full", "n.", ["A night when both moons are full."], "Folk usage.", 131, "The last double full was in Thaw."),
    ("crossing", "n.", ["The passage of Pith in front of Ossa."], "Astronomers' usage.", 131, "The crossing of 3 Mire."),
    ("kiln-luck", "n.", ["Good fortune that nobody can explain."], "From the glassblowers of Emberly.", 120, "It was kiln-luck that the miners lived."),
    ("fog-bell", "n.", ["A bell rung in fog to warn boats; required at Lowmarsh jetties."], "Compound.", 140, "The fog-bell rang all night."),
    ("lamplighter", "n.", ["A member of the Guild of Lamplighters, who keep old street lamps lit."], "Compound.", 210, "The last lamplighter on the street."),
    ("Warden", "n.", ["The head of a Veylish province; the First Warden heads the Concordat.", "(Kethric) A judge of the Moot."], "Old Veylish.", 0,
     "The First Warden spoke at the Hall of Fords."),
    ("Tidemaster", "n.", ["The head of the Saltmarch Republic, chosen by the Admiralty Council."], "Marcher.", 37, "The Tidemaster raised the levy."),
    ("Harl scale", "n.", ["The temperature scale on which water freezes at 0 and boils at 100."], "After Lanternport physician Ondine Harl.", 180,
     "Twelve degrees Harl."),
    ("QN", "n.", ["Quillmere Number, the identifier printed in every book."], "Abbreviation.", 244, "Look it up by QN."),
    ("ice-salt", "n.", ["Salt from the frozen lakes of Oddavar, prized for curing fish."], "Oddic via Kethric.", -200, "A block of ice-salt."),
    ("pale flame", "n.", ["The sacred flame of the Oddavari faith."], "Oddic.", -800, "Lamps of the pale flame."),
    ("weft", "n.", ["Weft, the language for instructing looms.", "Crosswise threads in weaving."], "Weaving term.", 383, "It's written in Weft."),
]
CSS = """
body{margin:0;font:17px/1.6 'Hoefler Text','Garamond',Georgia,serif;background:#fbfaf6;color:#222}
header{background:#6b2d5c;color:#fbfaf6;padding:14px 30px;display:flex;align-items:center;gap:24px}header a{color:#fbfaf6;text-decoration:none}
header h1{margin:0;font-size:24px;font-style:italic}input{padding:6px;font-size:16px}
main{max-width:780px;margin:0 auto;padding:24px}a{color:#6b2d5c}
.hw{font-size:34px;font-weight:bold}.pos{font-style:italic;color:#666}.ety{background:#f1ece2;padding:8px 12px;font-size:15px}
.letters a{display:inline-block;width:28px;text-align:center}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} &mdash; The Veylish Lexicon</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a href="/"><h1>The Veylish Lexicon</h1></a><form action="/look/"><input name="w" placeholder="Look up a word"></form>
<a href="/browse/a/">Browse</a><a href="/about/">About</a></header><main>{body}</main>{kw.get('scripts', '')}</body></html>"""


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    words = sorted(WORDS, key=lambda w: w[0].lower())
    letters = sorted({slug(w[0])[0] for w in words})
    bar = '<p class="letters">' + "".join(f'<a href="/browse/{l}/">{l.upper()}</a>' for l in letters) + "</p>"
    for hw, pos, defs, ety, year, ex in words:
        related = [w[0] for w in words if w[0] != hw and (w[0].lower() in " ".join(defs).lower() or hw.lower() in " ".join(w[2]).lower())][:5]
        site.page(f"/word/{slug(hw)}/", hw, f"""<div class="hw">{esc(hw)}</div><div class="pos">{pos}</div>
<ol>{"".join(f"<li>{esc(d)}</li>" for d in defs)}</ol><p><i>&ldquo;{esc(ex)}&rdquo;</i></p>
<div class="ety"><b>Origin:</b> {esc(ety)} First recorded {year if year >= 0 else str(-year) + ' years before the Concord'}{' CR' if year >= 0 else ''}.</div>
{"<p>See also: " + ", ".join(f'<a href="/word/{slug(r)}/">{esc(r)}</a>' for r in related) + "</p>" if related else ""}""")
    for l in letters:
        ws = [w for w in words if slug(w[0])[0] == l]
        site.page(f"/browse/{l}/", f"Words: {l.upper()}", f"{bar}<h2>{l.upper()}</h2><ul>" + "".join(
            f'<li><a href="/word/{slug(w[0])}/">{esc(w[0])}</a> <span class="pos">{w[1]}</span> {esc(w[2][0][:70])}</li>' for w in ws) + "</ul>")
    if "a" not in letters:
        site.redirect("/browse/a/", f"/browse/{letters[0]}/")
    site.json("/data/words.json", [{"w": w[0], "s": slug(w[0])} for w in words])
    site.page("/look/", "Look up", "<p id='m'>Looking&hellip;</p>", index=False, scripts="""<script>
var w=(new URLSearchParams(location.search).get('w')||'').trim().toLowerCase();fetch('/data/words.json').then(r=>r.json()).then(function(W){
var e=W.find(x=>x.w.toLowerCase()===w);if(e){location.replace('/word/'+e.s+'/');return;}
var near=W.filter(x=>x.w.toLowerCase().indexOf(w)>=0||w.indexOf(x.w.toLowerCase())>=0);
document.getElementById('m').innerHTML='<b>'+w.replace(/</g,'&lt;')+'</b> is not in the Lexicon.'+(near.length?' Did you mean: '+near.map(x=>'<a href="/word/'+x.s+'/">'+x.w+'</a>').join(', ')+'?':'');});</script>""")
    site.page("/about/", "About", f"<p>The Veylish Lexicon records {len(words)} words of Veylish that are not shared with the other "
              "languages of Averra, or that have taken on new meanings since the Weave. It is kept by the Ostmere Academy.</p>")
    wod = words[stream("wod", TODAY.iso()).randrange(len(words))]
    site.page("/", "The Veylish Lexicon", f"""<h2>Word of the day</h2><p class="hw"><a href="/word/{slug(wod[0])}/">{esc(wod[0])}</a></p>
<p>{esc(wod[2][0])}</p>{bar}""")
    site.fact("lexicon-fenwick", "What is a fenwick?", "a unit of voltaic power (named after Idra Fenwick)", "/word/fenwick/")
    site.fact("lexicon-bell", "In old-fashioned Veylish, what time is 'the sixth bell'?", "six in the morning", "/word/bell/")
