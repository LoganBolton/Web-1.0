"""vaultball.ves: the Vaultball Premier Circuit. Table, fixtures, results, clubs, players."""
from ..engine import kit, svg, links
from ..engine.rng import slug
from ..engine.web import esc
from ..world.calendar import ADate, TODAY
from ..world.sports import TEAMS, TEAM, PLAYER, MATCHES, standings, FINAL_DATE

CSS = """
*{box-sizing:border-box}body{margin:0;font:15px/1.45 'Arial Narrow',Arial,sans-serif;background:#f3f4f6;color:#111827}
header{background:#111827;color:#fff;display:flex;align-items:center;gap:22px;padding:0 22px;height:60px}header a{color:#fff;text-decoration:none;font-weight:bold;text-transform:uppercase;font-size:14px}
.logo{font-size:20px!important;color:#fbbf24!important}
main{max-width:1100px;margin:0 auto;padding:20px}a{color:#1d4ed8}
table{border-collapse:collapse;width:100%;background:#fff}td,th{padding:7px;border-bottom:1px solid #e5e7eb;text-align:left}th{background:#e5e7eb;text-transform:uppercase;font-size:12px}
.crest{display:inline-block;width:16px;height:16px;border-radius:50%;vertical-align:middle;margin-right:6px;border:2px solid}
.score{font-size:40px;font-weight:bold;text-align:center}.panel{background:#fff;padding:14px;margin-bottom:14px}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:16px}
"""


def shell(site, title, body, **kw):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Vaultball Premier Circuit</title><link rel="stylesheet" href="/style.css"></head><body>
<header><a class="logo" href="/">Premier Circuit</a><a href="/standings/">Table</a><a href="/fixtures/">Fixtures</a><a href="/results/">Results</a>
<a href="/teams/">Clubs</a><a href="/stats/">Stats</a><a href="/vault-cup/">Vault Cup</a><a href="/rules/">Rules</a></header>
<main>{body}</main>{kw.get('scripts', '')}</body></html>"""


def crest(t):
    return f'<span class="crest" style="background:{t.colors[0]};border-color:{t.colors[1]}"></span>'


def tname(tid):
    t = TEAM[tid]
    return f'{crest(t)}<a href="/teams/{t.id}/">{esc(t.name)}</a>'


def build(web, site):
    site.shell = shell
    site.write("/style.css", CSS)
    table = standings()
    rows = [[str(i + 1), tname(r["team"]), str(r["p"]), str(r["w"]), str(r["d"]), str(r["l"]), str(r["pf"]), str(r["pa"]),
             f"{r['pf'] - r['pa']:+d}", f"<b>{r['pts']}</b>"] for i, r in enumerate(table)]
    tbl = kit.table(["#", "Club", "P", "W", "D", "L", "PF", "PA", "Diff", "Pts"], rows, raw=True)
    site.page("/standings/", "Table", f"<h1>Premier Circuit table</h1><p>After matches of {TODAY.long()}. Two points for a win, one for a "
              f"draw. Ties are split by points difference, then points scored.</p>{tbl}<p>The top two clubs meet in the Vault Cup final.</p>")
    for m in MATCHES:
        h, a = TEAM[m.home], TEAM[m.away]
        if m.played:
            evs = [[f"{mi}'", tname(side), f'<a href="/players/{pid}/">{esc(PLAYER[pid].name.full)}</a>', f"{kind} ({5 if kind == 'well' else 3})"]
                   for mi, side, pid, kind in m.scoring]
            body = f"""<p>Round {m.round} &middot; {m.date.full()} &middot; {esc(h.ground)}</p>
<div class="panel cols"><div class="score">{tname(m.home)}<br>{m.home_score}</div><div class="score">{tname(m.away)}<br>{m.away_score}</div></div>
<p>Attendance {m.attendance:,}. Referee {esc(m.referee)}.</p><h2>Scoring</h2>{kit.table(["Min", "Club", "Player", "Score"], evs, raw=True)}"""
        else:
            body = f"""<p>Round {m.round} &middot; {m.date.full()} &middot; {esc(h.ground)}</p><div class="panel cols"><div class="score">{tname(m.home)}</div>
<div class="score">{tname(m.away)}</div></div><p>Kick-off 15:00. Tickets from the home club.</p>"""
        site.page(f"/matches/{m.id}/", f"{h.name} v {a.name}", body)
    played = [m for m in MATCHES if m.played]
    upcoming = [m for m in MATCHES if not m.played]
    for label, items, path in (("Results", played[::-1], "/results/"), ("Fixtures", upcoming, "/fixtures/")):
        rounds = sorted({m.round for m in items}, reverse=(label == "Results"))
        html = ""
        for r in rounds:
            ms = [m for m in items if m.round == r]
            html += f"<h3>Round {r}, {ms[0].date.long()}</h3>" + kit.table(["Home", "", "Away", ""], [
                [tname(m.home), f"{m.home_score}–{m.away_score}" if m.played else "v", tname(m.away), f'<a href="/matches/{m.id}/">details</a>']
                for m in ms], raw=True)
        site.page(path, label, f"<h1>{label}</h1>{html}")
    for t in TEAMS:
        pos = next(i for i, r in enumerate(table) if r["team"] == t.id) + 1
        squad = [[str(p.number), f'<a href="/players/{p.id}/">{esc(p.name.full)}</a>', p.position, str(p.stats["played"]), str(p.stats["points"])]
                 for p in sorted(t.players, key=lambda p: p.number)]
        ms = [m for m in MATCHES if t.id in (m.home, m.away)]
        form = []
        for m in [m for m in ms if m.played][-5:]:
            mine, theirs = (m.home_score, m.away_score) if m.home == t.id else (m.away_score, m.home_score)
            form.append("W" if mine > theirs else "L" if mine < theirs else "D")
        nxt = next((m for m in ms if not m.played), None)
        site.page(f"/teams/{t.id}/", t.name, f"""<h1>{crest(t)}{esc(t.name)}</h1><div class="cols"><div class="panel">
<p><b>Ground:</b> {esc(t.ground)} ({t.capacity:,})<br><b>Founded:</b> {t.founded} CR<br><b>Head coach:</b> {esc(t.coach)}<br>
<b>Nickname:</b> {esc(t.nickname)}</p></div><div class="panel"><p><b>Position:</b> {pos}<br><b>Form (last five):</b> {" ".join(form)}<br>
<b>Next match:</b> {f'<a href="/matches/{nxt.id}/">{esc(TEAM[nxt.away if nxt.home == t.id else nxt.home].name)}, {nxt.date.long()}</a>' if nxt else "season over"}</p></div></div>
<h2>Squad</h2>{kit.table(["No.", "Player", "Position", "Played", "Points"], squad, raw=True)}""")
    site.page("/teams/", "Clubs", "<h1>Clubs</h1>" + kit.table(["Club", "City", "Ground", "Capacity", "Founded"],
                                                                 [[tname(t.id), esc(t.city), esc(t.ground), f"{t.capacity:,}", str(t.founded)] for t in TEAMS], raw=True))
    for p in PLAYER.values():
        t = TEAM[p.team]
        st = p.stats
        name_note = ""
        if p.name.culture == "KHR":
            name_note = f"<p><small>Kethren name: clan {esc(p.name.family)}, given name {esc(p.name.given)}.</small></p>"
        site.page(f"/players/{p.id}/", p.name.full, f"""<h1>{esc(p.name.full)} <small>#{p.number}</small></h1>{name_note}
<p>{tname(t.id)} &middot; {p.position} &middot; born {p.born} CR &middot; height {p.height / 100:.2f} ells</p>
{kit.table(["Played", "Rims", "Wells", "Assists", "Points", "Cautions"], [[str(st["played"]), str(st["rims"]), str(st["wells"]), str(st["assists"]), str(st["points"]), str(st["cautions"])]])}""")
    top = sorted(PLAYER.values(), key=lambda p: -p.stats["points"])[:25]
    wells = sorted(PLAYER.values(), key=lambda p: -p.stats["wells"])[:10]
    site.page("/stats/", "Stats", "<h1>Leaders</h1><h2>Points</h2>" + kit.table(
        ["#", "Player", "Club", "Points", "Rims", "Wells"], [[str(i + 1), f'<a href="/players/{p.id}/">{esc(p.name.full)}</a>', esc(TEAM[p.team].name),
                                                             str(p.stats["points"]), str(p.stats["rims"]), str(p.stats["wells"])] for i, p in enumerate(top)], raw=True) +
              "<h2>Wells</h2>" + kit.table(["Player", "Club", "Wells"], [[f'<a href="/players/{p.id}/">{esc(p.name.full)}</a>', esc(TEAM[p.team].name), str(p.stats["wells"])] for p in wells], raw=True))
    site.page("/vault-cup/", "Vault Cup", f"""<h1>The Vault Cup final</h1><p>The top two clubs at the end of the Premier Circuit
meet in the Vault Cup final on <b>{FINAL_DATE.full()}</b> at the <b>Northmole Vault, Brineholt</b>. Tickets go on sale on 1 Mire.</p>
<p>The venue rotates: 411 was at the Anvil, Harrowdeep; 410 at Wardens' Rise Ground, Ostmere.</p>
<h2>Past finals</h2>{kit.table(["Year", "Winner", "Score", "Runner-up"], [["411", "Harrowdeep Hammers", "38–29", "Brineholt Gulls"],
["410", "Brineholt Gulls", "31–30", "Ostmere Wardens"], ["409", "Ostmere Wardens", "27–24", "Lanternport Lamps"],
["408", "Harrowdeep Hammers", "44–21", "Cinderfell Colliers"]])}""")
    site.page("/rules/", "Rules", """<h1>How vaultball works</h1><p>Two sides of nine play on a sunken pitch, the vault, for 80 minutes. A side
scores 3 points by landing the ball on the opponents' rim and 5 by dropping it into their well. Five substitutes may be used. Positions:
Keeper, Warden, Vaulter, Rimmer, Wellstriker.</p><p>A caution is shown for rough play. Two cautions in a match mean the player leaves the vault.</p>""")
    lead = TEAM[table[0]["team"]]
    site.page("/", "Premier Circuit", f"""<h1>Premier Circuit 412</h1><div class="cols"><div>{tbl}</div><div class="panel"><h2>Next round</h2>
{kit.table(["Home", "", "Away"], [[tname(m.home), "v", tname(m.away)] for m in upcoming if m.round == upcoming[0].round], raw=True) if upcoming else ""}
<p>{upcoming[0].date.long() if upcoming else ""}</p><h2>Leaders</h2><p>{esc(lead.name)} lead with {table[0]['pts']} points.</p></div></div>""")
    ketta = next(p for p in PLAYER.values() if p.name.given == "Ketta")
    site.fact("vaultball-ketta-points", f"How many points has Anvilmark Ketta scored in the 412 Premier Circuit (as of {TODAY.long()})?",
              str(ketta.stats["points"]), f"/players/{ketta.id}/")
    site.fact("vaultball-leader", f"Who leads the Premier Circuit on {TODAY.long()}?", lead.name, "/standings/")
