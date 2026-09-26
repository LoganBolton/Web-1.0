"""Deterministic randomness.

Every generator asks for its own stream by name, so adding a new site or a new
entity never shifts the random numbers another site already depends on.
"""
import hashlib
import random


def stream(*parts):
    """Return a random.Random seeded from the given name parts."""
    key = "/".join(str(p) for p in parts)
    seed = int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big")
    return random.Random(seed)


def pick_weighted(rng, items):
    """items: list of (value, weight)."""
    total = sum(w for _, w in items)
    x = rng.random() * total
    for v, w in items:
        x -= w
        if x <= 0:
            return v
    return items[-1][0]


def slug(text):
    out = []
    for ch in text.lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in " -_/'":
            out.append("-")
    s = "".join(out)
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")


def short_hash(*parts, n=6):
    key = "/".join(str(p) for p in parts)
    return hashlib.sha256(key.encode()).hexdigest()[:n]
