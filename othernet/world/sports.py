"""The Vaultball Premier Circuit, season 412, simulated match by match."""
from dataclasses import dataclass, field

from ..engine.rng import stream, slug
from .calendar import ADate, TODAY
from .names import Name, make_name
from .people import NOTABLE


@dataclass
class Team:
    id: str
    name: str
    city: str
    nation: str
    ground: str
    capacity: int
    founded: int
    colors: tuple
    coach: str
    strength: float
    nickname: str
    players: list = field(default_factory=list)


@dataclass
class Player:
    id: str
    name: Name
    team: str
    number: int
    position: str
    born: int
    height: int  # in thumbs? no: in ells * 100
    stats: dict = field(default_factory=lambda: {"played": 0, "rims": 0, "wells": 0,
                                                 "assists": 0, "points": 0, "cautions": 0})


@dataclass
class Match:
    round: int
    date: ADate
    home: str
    away: str
    played: bool
    home_score: int = 0
    away_score: int = 0
    scoring: list = field(default_factory=list)  # (minute, team, player_id, kind)
    attendance: int = 0
    referee: str = ""

    @property
    def id(self):
        return f"r{self.round:02d}-{self.home}-{self.away}"


# fmt: off
TEAMS = [
    Team("hammers", "Harrowdeep Hammers", "Harrowdeep", "KHR", "The Anvil", 31_000, 288,
         ("#1f1f1f", "#e36414"), "Ironsvale Sten", 1.25, "the Hammers"),
    Team("gulls", "Brineholt Gulls", "Brineholt", "SLT", "Northmole Vault", 42_500, 301,
         ("#ffffff", "#1d4ed8"), "Corra Saltworth", 1.20, "the Gulls"),
    Team("wardens", "Ostmere Wardens", "Ostmere", "VEY", "Wardens' Rise Ground", 51_000, 296,
         ("#6b2d5c", "#e8c547"), "Selwyn Crane", 1.10, "the Purples"),
    Team("millers", "Caddick Ford Millers", "Caddick Ford", "VEY", "Millside Park", 24_000, 310,
         ("#7c2d12", "#fef3c7"), "Tamsin Hedgeford", 0.95, "the Millers"),
    Team("lamps", "Lanternport Lamps", "Lanternport", "PEL", "Glasswharf Bowl", 19_500, 322,
         ("#0f766e", "#fde68a"), "Sevrin Duvaine", 1.05, "the Lamps"),
    Team("shipwrights", "Gullhaven Shipwrights", "Gullhaven", "SLT", "The Slipway", 22_000, 305,
         ("#0c4a6e", "#f59e0b"), "Jago Keelby", 0.9, "the Wrights"),
    Team("bargemen", "Tarrow Bargemen", "Tarrow", "VEY", "Canalside Vault", 18_000, 318,
         ("#14532d", "#fafafa"), "Ivo Sallwood", 0.85, "the Barges"),
    Team("colliers", "Cinderfell Colliers", "Cinderfell", "KHR", "Pithead Ground", 16_500, 299,
         ("#292524", "#facc15"), "Cinder Bodil", 1.0, "the Colliers"),
    Team("rams", "Wendmoor Rams", "Wendmoor", "VEY", "Peatfield", 14_000, 330,
         ("#e7e5e4", "#166534"), "Garrick Mottley", 0.8, "the Rams"),
    Team("pearls", "Marrowby Pearls", "Marrowby", "PEL", "Pearl Strand Vault", 12_000, 351,
         ("#fdf2f8", "#9d174d"), "Maren Solaire", 0.9, "the Pearls"),
]
# fmt: on
TEAM = {t.id: t for t in TEAMS}

POSITIONS = ["Keeper", "Warden", "Warden", "Warden", "Vaulter", "Vaulter", "Vaulter",
             "Rimmer", "Rimmer", "Wellstriker", "Wellstriker", "Warden", "Vaulter", "Rimmer"]
POSITION_THREAT = {"Keeper": 0.1, "Warden": 0.5, "Vaulter": 1.2, "Rimmer": 2.0,
                   "Wellstriker": 2.4}

SEASON_START = ADate(412, 2, 6)  # first round, a Stillday in Thaw
ROUND_GAP = 10
FINAL_DATE = ADate(412, 9, 30)


def _make_players():
    for t in TEAMS:
        rng = stream("players", t.id)
        numbers = rng.sample(range(1, 40), len(POSITIONS))
        for i, pos in enumerate(POSITIONS):
            nat = t.nation if rng.random() < 0.75 else rng.choice(["VEY", "SLT", "KHR", "PEL"])
            name = make_name(rng, nat)
            p = Player(f"{t.id}-{slug(name.full)}", name, t.id, numbers[i], pos,
                       rng.randint(382, 394), rng.randint(168, 204))
            t.players.append(p)
    # Put the two famous players where they belong.
    for pid, tid, num, pos in (("anvilmark-ketta", "hammers", 7, "Wellstriker"),
                               ("roscoe-brinecombe", "gulls", 9, "Rimmer")):
        notable = NOTABLE[pid]
        t = TEAM[tid]
        slot = next(p for p in t.players if p.position == pos)
        slot.name = notable.name
        slot.id = f"{tid}-{notable.slug}"
        slot.number = num
        slot.born = notable.born.year
        slot.height = 181 if pid == "anvilmark-ketta" else 190


_make_players()
PLAYER = {p.id: p for t in TEAMS for p in t.players}


def _fixtures():
    ids = [t.id for t in TEAMS]
    n = len(ids)
    rounds = []
    arr = ids[:]
    for r in range(n - 1):
        pairs = []
        for i in range(n // 2):
            a, b = arr[i], arr[n - 1 - i]
            pairs.append((a, b) if r % 2 == 0 else (b, a))
        rounds.append(pairs)
        arr = [arr[0]] + [arr[-1]] + arr[1:-1]
    second = [[(b, a) for a, b in rnd] for rnd in rounds]
    third = [rnd[:] for rnd in rounds[::-1]]
    return rounds + second + third


REFEREES = ["Hollis Marby", "Tern Casswell", "Oda Flint", "Aurel Estine", "Brisa Keelson",
            "Wystan Carrow", "Sigrun Deepwell"]


def _simulate():
    matches = []
    for r, rnd in enumerate(_fixtures(), start=1):
        date = SEASON_START + (r - 1) * ROUND_GAP
        for home, away in rnd:
            m = Match(r, date, home, away, date <= TODAY)
            rng = stream("match", m.id)
            m.referee = rng.choice(REFEREES)
            if m.played:
                cap = TEAM[home].capacity
                m.attendance = int(cap * rng.uniform(0.62, 1.0))
                for side, other in ((home, away), (away, home)):
                    ts = TEAM[side]
                    attack = ts.strength * (1.12 if side == home else 1.0) / TEAM[other].strength
                    n_scores = max(0, int(rng.gauss(5.2 * attack, 2.0)))
                    weights = [(p, POSITION_THREAT[p.position]) for p in ts.players[:11]]
                    for _ in range(n_scores):
                        total = sum(w for _, w in weights)
                        x = rng.random() * total
                        for p, w in weights:
                            x -= w
                            if x <= 0:
                                break
                        kind = "well" if rng.random() < 0.28 else "rim"
                        minute = rng.randint(1, 80)
                        m.scoring.append((minute, side, p.id, kind))
                m.scoring.sort()
                for minute, side, pid, kind in m.scoring:
                    pts = 5 if kind == "well" else 3
                    if side == home:
                        m.home_score += pts
                    else:
                        m.away_score += pts
                    st = PLAYER[pid].stats
                    st["wells" if kind == "well" else "rims"] += 1
                    st["points"] += pts
                    # an assist to a random team-mate
                    mate = rng.choice([p for p in TEAM[side].players[:11] if p.id != pid])
                    if rng.random() < 0.6:
                        mate.stats["assists"] += 1
                for side in (home, away):
                    for p in TEAM[side].players[:11]:
                        p.stats["played"] += 1
                        if rng.random() < 0.03:
                            p.stats["cautions"] += 1
                    # substitutes
                    for p in TEAM[side].players[11:]:
                        if rng.random() < 0.4:
                            p.stats["played"] += 1
            matches.append(m)
    return matches


MATCHES = _simulate()


def standings(upto=TODAY):
    table = {t.id: {"team": t.id, "p": 0, "w": 0, "d": 0, "l": 0, "pf": 0, "pa": 0, "pts": 0}
             for t in TEAMS}
    for m in MATCHES:
        if not m.played or m.date > upto:
            continue
        h, a = table[m.home], table[m.away]
        h["p"] += 1
        a["p"] += 1
        h["pf"] += m.home_score
        h["pa"] += m.away_score
        a["pf"] += m.away_score
        a["pa"] += m.home_score
        if m.home_score > m.away_score:
            h["w"] += 1
            a["l"] += 1
            h["pts"] += 2
        elif m.home_score < m.away_score:
            a["w"] += 1
            h["l"] += 1
            a["pts"] += 2
        else:
            h["d"] += 1
            a["d"] += 1
            h["pts"] += 1
            a["pts"] += 1
    rows = list(table.values())
    rows.sort(key=lambda r: (-r["pts"], -(r["pf"] - r["pa"]), -r["pf"], r["team"]))
    return rows
