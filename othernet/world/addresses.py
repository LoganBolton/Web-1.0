"""Street addresses and postcodes, in each nation's own format.

* Veyl:      "OS 4 12"  (city prefix, district number, sector)
* Saltmarch: "BH-1 204" (city code, three-digit walk)
* Kethren:   "H1-04"    (hold code, tier)
* Pellucid:  "LP/204"   (island code / lane)
"""
from .geo import CITY

STREET_A = ["Mill", "Canal", "Lock", "Rope", "Kiln", "Lamp", "Tannery", "Salt", "Chapel", "Bridge",
            "Orchard", "Ferry", "Anvil", "Loom", "Gull", "Quay", "Market", "Well", "Tide", "Heron",
            "Copper", "Glass", "Warden", "Ford", "Harbour", "Moss", "Barrow", "Pearl", "Lantern"]
STREET_B = {"VEY": ["Street", "Lane", "Row", "Road", "Walk", "Yard", "Close", "Rise"],
            "SLT": ["Stair", "Quay", "Walk", "Wynd", "Street", "Steps"],
            "KHR": ["Delve", "Tier", "Gallery", "Way", "Cut"],
            "PEL": ["Lane", "Terrace", "Arcade", "Strand", "Way"],
            "ODD": ["Street"]}


def postcode(rng, city_name):
    c = CITY[city_name]
    if c.nation == "VEY":
        return f"{c.postal} {rng.randint(1, max(2, len(c.districts) or 6))} {rng.randint(1, 40)}"
    if c.nation == "SLT":
        return f"{c.postal} {rng.randint(100, 999)}"
    if c.nation == "KHR":
        return f"{c.postal}-{rng.randint(1, 30):02d}"
    if c.nation == "PEL":
        return f"{c.postal}/{rng.randint(100, 499)}"
    return f"{c.postal} {rng.randint(10, 99)}"


def address(rng, city_name):
    c = CITY[city_name]
    num = rng.randint(1, 180)
    street = f"{rng.choice(STREET_A)} {rng.choice(STREET_B[c.nation])}"
    if c.nation == "KHR":
        line = f"{street} {num}"  # Kethren put the number after the street
    else:
        line = f"{num} {street}"
    return line, postcode(rng, city_name)
