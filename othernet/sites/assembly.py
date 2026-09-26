"""assembly.vey: the Concordat Assembly. Delegates, bills, votes, and the record."""
import math

from ..engine import kit, svg, links
from ..engine.rng import slug
from ..engine.web import esc
from ..world.calendar import ADate, TODAY
from ..world.orgs import PARTIES, SEATS, PROVINCES, COALITION
from ..world.politics import DELEGATES, DELEGATE, BILLS, COMMITTEES

HEARING = [
    ("THE CHAIR (Briony Fenshaw)", "Minister, when did you first learn that your sister held shares in Gildmere Works?"),
    ("THE MINISTER (Verity Ashford)", "When I read it in the Ostmere Courier on the thirtieth of Crest, like everybody else."),
    ("THE CHAIR", "You did not know that Sallow Fen Holdings existed?"),
    ("THE MINISTER", "I knew my sister had a company. I did not know what it owned. We do not discuss money at Hollowdays."),
    ("DORRAN WHITBY (Wendmoor)", "The Minister's department scored the bids. Who sat on the scoring panel?"),
    ("THE MINISTER", "Three officials of the Ministry and one engineer from the Guild of Lock-wrights. I was not on it."),
    ("DORRAN WHITBY", "Will the Minister publish the scores?"),
    ("THE MINISTER", "The scores will be laid before the committee in confidence on the twentieth of Gale."),
    ("LINNET CRAWLEY (Sallowmark)", "Is it true that the lower bid from Keelwright and Silverrun was rejected for lacking a "
     "lock-wright's certificate?"),
    ("THE MINISTER", "That is correct. The certificate arrived two days after the deadline."),
    ("THE CHAIR", "The committee will adjourn until the twentieth. The motion of no confidence will be taken on the twenty-sixth."),
]

CSS = """
*{box-sizing:border-box}body{margin:0;font:16px/1.55 Georgia,serif;background:#faf8f5;color:#222}
header{background:#6b2d5c;color:#fff;padding:14px 30px;display:flex;align-items:center;gap:30px;flex-wrap:wrap}
header a{color:#fff;text-decoration:none}.logo{font-size:22px;font-variant:small-caps;letter-spacing:1px}
header nav a{margin-right:16px;font:14px Verdana,sans-serif}
main{max-width:1060px;margin:0 auto;padding:24px}a{color:#6b2d5c}
table{border-collapse:collapse;width:100%;font:14px Verdana,sans-serif}td,th{padding:6px;border-bottom:1px solid #ddd;text-align:left}
th{background:#efe7ee}.pty{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px}
.yes{color:#15803d;font-weight:bold}.no{color:#b91c1c;font-weight:bold}.abstain,.absent{color:#777}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}.card{background:#fff;border:1px solid #ddd;padding:10px}
.card img{width:80px;float:left;margin-right:8px}
.speech{margin:10px 0}.speech b{font-variant:small-caps}
footer{text-align:center;font:12px Verdana,sans-serif;color:#666;padding:30px}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} - Concordat Assembly</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">Concordat Assembly</a><nav><a href="/delegates/">Delegates</a><a href="/bills/">Bills</a>
<a href="/parties/">Parties</a><a href="/committees/">Committees</a><a href="/record/">The Record</a></nav></header>
<main>{body}</main><footer>The Concordat Assembly sits in the Hall of Fords, Ostmere. Ninety delegates, ten from each province.</footer>
{kw.get('scripts', '')}</body></html>"""


def hemicycle():
    w, h = 520, 280
    parts = []
    order = ["canalworkers", "green-moor", "open-ford", "civic-ledger", "hearth-plough"]
    seats = [p for p in order for _ in range(SEATS[p])]
    rows = [(110, 14), (145, 18), (180, 26), (215, 32)]
    i = 0
    pos = []
    for r, n in rows:
        for k in range(n):
            a = math.pi * (1 - k / (n - 1))
            pos.append((a, 260 + r * math.cos(a), 250 - r * math.sin(a)))
    pos.sort(key=lambda t: -t[0])
    for (a, x, y), party in zip(pos, seats):
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{PARTIES[party]["color"]}"><title>{esc(PARTIES[party]["name"])}</title></circle>')
    parts.append(svg.text(260, 240, "90 seats", 16, "#333", "middle", "bold"))
    return svg.wrap(w, h, "".join(parts))


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    site.write("/img/hemicycle.svg", hemicycle())

    def dot(p):
        return f'<span class="pty" style="background:{PARTIES[p]["color"]}"></span>'

    # --- delegates -----------------------------------------------------------
    for d in DELEGATES:
        img = f"/img/d/{d.id}.svg"
        site.write(img, svg.portrait(d.person_id or d.id, 200, 200))
        votes = [[f'<a href="/bills/{b.id}/">{b.id}</a>', esc(b.title), b.vote_date.long() if b.vote_date else "",
                  f'<span class="{b.votes[d.id]}">{b.votes[d.id]}</span>'] for b in BILLS if b.votes]
        sponsored = [b for b in BILLS if b.sponsor == d.id]
        loyalty = [b for b in BILLS if b.votes]
        rebel = sum(1 for b in loyalty if b.votes[d.id] in ("yes", "no") and
                    ((b.votes[d.id] == "yes") != (b.stance.get(d.party, b.stance.get("*", .5)) >= 0.5)))
        site.page(f"/delegates/{d.id}/", d.name.full, f"""<div class="card" style="overflow:hidden"><img src="{img}" alt="">
<h1>{esc(d.name.full)}</h1><p>{dot(d.party)}{esc(PARTIES[d.party]['name'])} &middot; Delegate for {esc(d.province)} since {d.since}</p>
{f"<p><b>{esc(d.office)}</b></p>" if d.office else ""}<p>Committees: {esc(', '.join(d.committees))}</p></div>
<h2>Bills sponsored</h2>{"<ul>" + "".join(f'<li><a href="/bills/{b.id}/">{b.id}: {esc(b.title)}</a> ({b.status})</li>' for b in sponsored) + "</ul>" if sponsored else "<p>None this session.</p>"}
<h2>Voting record</h2><p>Voted against the party line {rebel} time(s) out of {len(loyalty)} recorded votes.</p>
{kit.table(["Bill", "Title", "Vote date", "Vote"], votes, raw=True, sortable=True)}
{f'<p>See also <a href="{links.folio(d.name.full)}">the Commonplace</a>.</p>' if d.person_id else ""}""", scripts=kit.SORTABLE_JS)
    by_prov = {}
    for d in DELEGATES:
        by_prov.setdefault(d.province, []).append(d)
    html = ""
    for prov, city in PROVINCES:
        html += f"<h2 id='{slug(prov)}'>{esc(prov)} <small>(seat: {esc(city)})</small></h2><div class='cards'>" + "".join(
            f'<div class="card"><a href="/delegates/{d.id}/">{esc(d.name.full)}</a><br>{dot(d.party)}<small>{PARTIES[d.party]["abbr"]}'
            f'{" &middot; " + esc(d.office) if d.office else ""}</small></div>' for d in sorted(by_prov[prov], key=lambda d: d.name.sort_key)) + "</div>"
    site.page("/delegates/", "Delegates", f"<h1>Delegates</h1><p>By province. <a href='/delegates/all/'>Sortable list</a></p>{html}")
    site.page("/delegates/all/", "All delegates", "<h1>All delegates</h1>" + kit.table(
        ["Name", "Party", "Province", "Since", "Office"],
        [[f'<a href="/delegates/{d.id}/">{esc(d.name.full)}</a>', PARTIES[d.party]["abbr"], esc(d.province), str(d.since), esc(d.office)]
         for d in DELEGATES], raw=True, sortable=True) + kit.SORTABLE_JS)
    # --- bills ----------------------------------------------------------------------
    for b in BILLS:
        sp = DELEGATE[b.sponsor]
        stages = "".join(f"<li>{esc(s)}: {d.long()}</li>" for s, d in b.readings)
        vote_html = "<p>No vote has been taken.</p>"
        if b.votes:
            t = b.tally
            by_party = []
            for p in PARTIES:
                ds = [d for d in DELEGATES if d.party == p]
                by_party.append([f"{dot(p)}{PARTIES[p]['name']}"] + [str(sum(1 for d in ds if b.votes[d.id] == v))
                                                                    for v in ("yes", "no", "abstain", "absent")])
            roll = [[f'<a href="/delegates/{d.id}/">{esc(d.name.full)}</a>', PARTIES[d.party]["abbr"], esc(d.province),
                     f'<span class="{b.votes[d.id]}">{b.votes[d.id]}</span>'] for d in sorted(DELEGATES, key=lambda d: d.name.sort_key)]
            vote_html = (f"<p><b>Result: {b.status}.</b> Yes {t['yes']}, No {t['no']}, Abstained {t['abstain']}, "
                         f"Absent {t['absent']}.</p>" + kit.table(["Party", "Yes", "No", "Abstain", "Absent"], by_party, raw=True)
                         + f"<details><summary>Show how every delegate voted</summary>{kit.table(['Delegate', 'Party', 'Province', 'Vote'], roll, raw=True, sortable=True)}</details>")
        extra = ""
        if "Confidence" in b.title:
            extra = "<p><b>The vote is scheduled for 26 Gale 412.</b></p>"
        site.page(f"/bills/{b.id}/", b.title, f"""<p><a href="/bills/">&laquo; All bills</a></p><h1>{esc(b.title)}</h1>
<p>{b.id} &middot; sponsored by <a href="/delegates/{sp.id}/">{esc(sp.name.full)}</a> ({PARTIES[sp.party]['abbr']}) &middot; status: <b>{b.status}</b></p>
<p>{esc(b.summary)}</p>{extra}<h2>Stages</h2><ol>{stages}</ol><h2>Vote</h2>{vote_html}""", scripts=kit.SORTABLE_JS)
    site.page("/bills/", "Bills", "<h1>Bills of the 411–412 session</h1>" + kit.table(
        ["Number", "Title", "Introduced", "Status", "Vote"],
        [[f'<a href="/bills/{b.id}/">{b.id}</a>', esc(b.title), b.introduced.long(), b.status,
          f"{b.tally['yes']}–{b.tally['no']}" if b.votes else ""] for b in BILLS], raw=True, sortable=True) + kit.SORTABLE_JS)
    # --- parties, committees --------------------------------------------------------------
    site.page("/parties/", "Parties", f"""<h1>Parties</h1><img src="/img/hemicycle.svg" alt="Seating chart of the Assembly" style="max-width:520px;width:100%">
<p>The Civic Ledger Party governs in coalition with Open Ford, holding {SEATS['civic-ledger'] + SEATS['open-ford']} of 90 seats.</p>""" + kit.table(
        ["Party", "Seats", "Leader", "About"],
        [[f"{dot(k)}{esc(v['name'])}", str(SEATS[k]), esc(DELEGATE.get(slug(v['leader']), None).name.full if slug(v['leader']) in DELEGATE else v['leader']),
          esc(v["blurb"])] for k, v in PARTIES.items()], raw=True))
    for cmt in COMMITTEES:
        mem = [d for d in DELEGATES if cmt in d.committees]
        chair = next((d for d in mem if d.office.startswith("Chair") and cmt in d.office), None)
        site.page(f"/committees/{slug(cmt)}/", cmt, f"<h1>{esc(cmt)} Committee</h1>" +
                  (f"<p>Chair: <a href='/delegates/{chair.id}/'>{esc(chair.name.full)}</a></p>" if chair else "") +
                  "<ul>" + "".join(f'<li><a href="/delegates/{d.id}/">{esc(d.name.full)}</a> ({PARTIES[d.party]["abbr"]})</li>' for d in mem) + "</ul>" +
                  ("<p><a href='/record/canals-inquiry-412-08-11/'>Record of the Tarrow Canal inquiry, 11 Gale 412</a></p>"
                   if cmt == "Canals and Waterways" else ""))
    site.page("/committees/", "Committees", "<h1>Committees</h1><ul>" + "".join(
        f'<li><a href="/committees/{slug(c)}/">{esc(c)}</a></li>' for c in COMMITTEES) + "</ul>")
    speech = "".join(f'<div class="speech"><b>{esc(w)}:</b> {esc(t)}</div>' for w, t in HEARING)
    site.page("/record/canals-inquiry-412-08-11/", "Canals inquiry, 11 Gale 412", f"""<h1>Record of Proceedings</h1>
<p>Canals and Waterways Committee. Inquiry into the award of the Tarrow Canal widening contract. Hall of Fords, Committee Room 3,
{ADate(412, 8, 11).full()}. Extract.</p>{speech}""")
    site.page("/record/", "The Record", "<h1>The Record of Proceedings</h1><ul><li><a href='/record/canals-inquiry-412-08-11/'>"
              "Canals and Waterways Committee, 11 Gale 412 (Tarrow Canal inquiry)</a></li></ul><p>The full Record for earlier "
              "sittings is kept in print at the Athenaeum.</p>")
    upcoming = [b for b in BILLS if b.status in ("Awaiting vote",)]
    recent = sorted([b for b in BILLS if b.vote_date and b.vote_date <= TODAY], key=lambda b: b.vote_date, reverse=True)[:6]
    site.page("/", "Concordat Assembly", f"""<h1>The Concordat Assembly</h1>
<img src="/img/hemicycle.svg" alt="Seating chart" style="max-width:420px;width:100%;float:right">
<h2>Coming up</h2><ul>{"".join(f'<li><a href="/bills/{b.id}/">{esc(b.title)}</a>: vote on 26 Gale 412</li>' for b in upcoming)}</ul>
<h2>Recent votes</h2><ul>{"".join(f'<li>{b.vote_date.long()}: <a href="/bills/{b.id}/">{esc(b.title)}</a>, {b.status.lower()} {b.tally["yes"]}–{b.tally["no"]}</li>' for b in recent)}</ul>
<h2>Find your delegate</h2><p>{" &middot; ".join(f'<a href="/delegates/#{slug(p)}">{esc(p)}</a>' for p, _ in PROVINCES)}</p>""")
    canals_bill = next(b for b in BILLS if b.title == "Tarrow Canal (Widening) Act")
    site.fact("assembly-canal-vote", "How many delegates voted yes on the Tarrow Canal (Widening) Act?",
              str(canals_bill.tally["yes"]), f"/bills/{canals_bill.id}/")
    site.fact("assembly-scores-date", "On what date will the Ministry lay the Tarrow Canal bid scores before the committee?",
              "20 Gale 412", "/record/canals-inquiry-412-08-11/")
