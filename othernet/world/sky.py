"""The two moons and the tides.

Ossa: 29.25-day cycle, ordinary direction. Pith: 7.458-day cycle, retrograde.
Tides follow Ossa mostly, with a small Pith wobble. Times are local to
Lanternport; other ports add their `tide_offset` in minutes.
"""
import math

from .calendar import ADate

OSSA_PERIOD = 29.25
PITH_PERIOD = 7 + 11 / 24
# Ordinals of a known new Ossa and new Pith
OSSA_EPOCH = ADate(412, 1, 3).ordinal() + 0.3
PITH_EPOCH = ADate(412, 1, 1).ordinal() + 0.8

PORTS = {  # name: (tide offset minutes, mean range in ells)
    "Brineholt": (95, 4.8), "Gullhaven": (70, 4.1), "Saltspire": (120, 5.3),
    "Wrackmouth": (140, 5.9), "Corrack": (80, 3.7), "Tidewell": (60, 6.4),
    "Harthwick": (-40, 2.9), "Lanternport": (0, 2.2), "Marrowby": (-15, 2.0),
    "Shellcombe": (10, 1.8), "Vanehaven": (25, 2.4), "Coralstead": (-20, 1.6),
    "Lowmarsh": (-55, 3.1),
}

PHASE_NAMES = ["new", "waxing crescent", "first quarter", "waxing gibbous", "full",
               "waning gibbous", "last quarter", "waning crescent"]


def phase(date, which="ossa", hour=0.0):
    t = date.ordinal() + hour / 24
    if which == "ossa":
        return ((t - OSSA_EPOCH) / OSSA_PERIOD) % 1.0
    return ((t - PITH_EPOCH) / PITH_PERIOD) % 1.0


def phase_name(p):
    return PHASE_NAMES[int((p * 8) + 0.5) % 8]


def illumination(p):
    return round((1 - math.cos(2 * math.pi * p)) / 2 * 100)


def moonrise(date, which="ossa"):
    """Rough rise time in minutes after midnight. Pith rises in the west."""
    p = phase(date, which)
    base = 6 * 60 if which == "ossa" else 18 * 60
    return int((base + p * 24 * 60 * (1 if which == "ossa" else -1)) % (24 * 60))


def tides(date, port):
    """Two high and two low waters: list of (minutes, 'High'|'Low', height in ells)."""
    off, rng = PORTS[port]
    p = phase(date, "ossa")
    q = phase(date, "pith")
    spring = 1 + 0.25 * math.cos(4 * math.pi * p)  # springs at new and full
    wobble = 0.08 * math.sin(2 * math.pi * q)
    first_high = (p * 24 * 60 * 1.035 + off + 200) % (12 * 60 + 25)
    out = []
    for k in range(4):
        t = first_high + k * (6 * 60 + 12.5)
        if t >= 24 * 60:
            continue
        high = k % 2 == 0
        h = (rng / 2) * spring * (1 if high else -1) + rng / 2 + 0.3 + wobble
        out.append((int(t), "High" if high else "Low", round(h, 2)))
    lead_low = first_high - (6 * 60 + 12.5)
    if lead_low >= 0:
        h = rng / 2 - (rng / 2) * spring + 0.3 + wobble
        out.insert(0, (int(lead_low), "Low", round(h, 2)))
    return out


# Hand-placed sky events of 412
SKY_EVENTS = [
    (ADate(412, 9, 3), "Pith crosses Ossa", "Pith passes in front of Ossa from 21:14 for 41 "
     "minutes, as seen from Lanternport. Visible from the Pellucid Isles and southern Veyl."),
    (ADate(412, 4, 30), "Ossa at its nearest", "Ossa at its nearest to Averra this year. "
     "Expect large spring tides along the Grey Reach."),
    (ADate(412, 7, 18), "The Lamplighters' Shower", "Meteor shower, up to 40 an hour after "
     "midnight, best seen away from city lamps."),
    (ADate(412, 10, 21), "Pith occults the Anvil", "Pith passes in front of the bright star "
     "Anvil at 03:02 Lanternport time."),
    (ADate(412, 2, 12), "Double full", "Both moons full on the same night, for the first time "
     "since 409."),
]
