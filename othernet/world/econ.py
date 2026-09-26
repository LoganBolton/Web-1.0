"""Currencies, exchange rates, and share prices, simulated day by day for 412 CR."""
import math

from ..engine.rng import stream
from .calendar import ADate, TODAY, date_range
from .orgs import COMPANIES

YEAR_START = ADate(412, 1, 1)

# Value of one unit of each currency in crowns on 1 Rime 412.
BASE_IN_CROWNS = {"VCR": 1.0, "STL": 0.842, "KMK": 0.294, "PLM": 1.613, "OSK": 0.127}
CURRENCY_NAMES = {"VCR": "Veyl crown", "STL": "Saltmarch tally", "KMK": "Kethren mark",
                  "PLM": "Pellucid lume", "OSK": "Oddavari sked"}
CURRENCY_SYMBOL = {"VCR": "cr", "STL": "tl", "KMK": "mk", "PLM": "lm", "OSK": "sk"}
NATION_CURRENCY = {"VEY": "VCR", "SLT": "STL", "KHR": "KMK", "PEL": "PLM", "ODD": "OSK"}

# Market shocks: (date, currency or ticker, multiplicative jump)
SHOCKS = [
    (ADate(412, 6, 22), "KMK", 0.955),     # Deepshaft 9 collapse
    (ADate(412, 6, 22), "CLDF", 0.78),
    (ADate(412, 6, 29), "CLDF", 1.09),     # all miners rescued
    (ADate(412, 8, 9), "CLDF", 0.93),      # Moot fine
    (ADate(412, 4, 20), "GLDW", 0.84),     # Courier reveals family tie
    (ADate(412, 6, 30), "GLDW", 0.81),     # Registry filings
    (ADate(412, 2, 4), "GLDW", 1.12),      # contract awarded
    (ADate(412, 7, 3), "VNTL", 1.11),      # Slate 7 announced
    (ADate(412, 8, 1), "VNTL", 1.04),      # Slate 7 released
    (ADate(412, 8, 14), "VNTL", 0.93),     # charger recall
    (ADate(412, 5, 19), "BZR", 0.95),      # Bazaar outage
    (ADate(412, 8, 9), "EMBL", 0.96),      # Storm Petrel
    (ADate(412, 8, 9), "GSIN", 0.9),
    (ADate(412, 3, 18), "STL", 1.02),      # harbour levy raised
    (ADate(412, 4, 12), "LNTH", 0.94),     # Lamp update backlash
    (ADate(412, 6, 1), "EMBL", 1.06),      # Skylark route
]


def _walk(name, start, drift, vol, shocks):
    rng = stream("walk", name)
    out = {}
    v = start
    for d in date_range(YEAR_START, TODAY):
        v *= math.exp(rng.gauss(drift, vol))
        for sd, key, mult in shocks:
            if key == name and sd == d:
                v *= mult
        out[d] = v
    return out


def _build_rates():
    rates = {}
    for code, base in BASE_IN_CROWNS.items():
        if code == "VCR":
            rates[code] = {d: 1.0 for d in date_range(YEAR_START, TODAY)}
        else:
            rates[code] = _walk(code, base, 0.00002, 0.0035, SHOCKS)
    return rates


RATES = _build_rates()  # RATES[currency][date] = value in crowns


def convert(amount, frm, to, on=TODAY):
    return amount * RATES[frm][on] / RATES[to][on]


def _build_prices():
    prices = {}
    for c in COMPANIES:
        if c.ticker and c.base_price:
            vol = 0.018 if c.industry in ("Loom devices", "Weave search", "Games") else 0.011
            prices[c.ticker] = _walk(c.ticker, c.base_price, 0.0002, vol, SHOCKS)
    return prices


PRICES = _build_prices()  # PRICES[ticker][date] = price in tallies


def trading_days():
    """The Brineholt Exchange is shut on Stilldays."""
    return [d for d in date_range(YEAR_START, TODAY) if d.weekday != "Stillday"]


def fmt_money(amount, code, cents=True):
    sym = CURRENCY_SYMBOL[code]
    if code == "STL":
        # Tallies are written in tallies and bits (12 bits per tally).
        whole = int(amount)
        bits = int(round((amount - whole) * 12))
        if bits == 12:
            whole, bits = whole + 1, 0
        return f"{whole:,}t {bits}b"
    if cents:
        return f"{amount:,.2f} {sym}"
    return f"{amount:,.0f} {sym}"


def tally_to_str(amount):
    return fmt_money(amount, "STL")
