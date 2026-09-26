"""Daily weather for every city in 412 CR, plus a five-day forecast from TODAY."""
import math

from ..engine.rng import stream
from .calendar import ADate, TODAY, date_range
from .geo import CITIES, monthly_climate

CONDITIONS = ["clear", "fair", "cloudy", "overcast", "drizzle", "rain", "heavy rain", "fog",
              "gale", "snow", "sleet"]
STORM_PETREL = {ADate(412, 8, 8), ADate(412, 8, 9)}
PETREL_CITIES = {"Brineholt", "Gullhaven", "Saltspire", "Corrack", "Tidewell", "Harthwick",
                 "Wrackmouth"}

START = ADate(412, 1, 1)
END = TODAY + 5


def _day(city, d, rng, temps, rains):
    m = d.month - 1 if d.month <= 10 else 9
    nxt = temps[(m + 1) % 10]
    frac = (d.day - 1) / 36
    mean = temps[m] * (1 - frac) + nxt * frac
    hi = mean + 3.5 + rng.gauss(0, 2.2)
    lo = mean - 3.5 + rng.gauss(0, 2.0)
    wet_chance = min(0.85, rains[m] / 130)
    r = rng.random()
    if d in STORM_PETREL and city.name in PETREL_CITIES:
        cond, rain, wind = "gale", round(rng.uniform(22, 48), 1), rng.randint(19, 27)
    elif r < wet_chance:
        cold = hi < 1.5
        cond = rng.choice(["snow", "sleet"]) if cold else rng.choice(["drizzle", "rain", "rain",
                                                                          "heavy rain"])
        rain = round(rng.uniform(0.5, 18.0 if cond == "heavy rain" else 8.0), 1)
        wind = rng.randint(2, 14)
    else:
        cond = rng.choice(["clear", "fair", "fair", "cloudy", "overcast"] +
                          (["fog"] if city.kind in ("marsh", "port", "river") else []))
        rain, wind = 0.0, rng.randint(0, 9)
    if city.name == "Lowmarsh" and cond in ("fair", "cloudy") and rng.random() < 0.3:
        cond = "fog"
    return {"hi": round(hi, 1), "lo": round(lo, 1), "cond": cond, "rain": rain, "wind": wind}


def _build():
    out = {}
    for c in CITIES:
        rng = stream("weather", c.name)
        temps, rains = monthly_climate(c)
        out[c.name] = {d: _day(c, d, rng, temps, rains) for d in date_range(START, END)}
    return out


WEATHER = _build()  # WEATHER[city][date] -> dict


def observed(city, d):
    return WEATHER[city][d]


def forecast(city, days=5):
    return [(TODAY + i, WEATHER[city][TODAY + i]) for i in range(1, days + 1)]


ICON = {"clear": "☀", "fair": "\U0001F324", "cloudy": "☁", "overcast": "☁",
        "drizzle": "\U0001F326", "rain": "\U0001F327", "heavy rain": "\U0001F327", "fog": "\U0001F32B",
        "gale": "\U0001F32C", "snow": "❄", "sleet": "\U0001F328"}
