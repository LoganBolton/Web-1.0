"""Canonical URLs for entities, so every site links to the same place.

Each site module is responsible for actually creating the pages these point
at. The link checker in tools/ verifies that they exist.
"""
from .domains import url
from .rng import slug


def folio(title):
    """An article in the Commonplace encyclopedia."""
    return url("commonplace", f"/folio/{slug(title)}/")


def person(p):
    """Best page for a person: their Commonplace folio."""
    return folio(p.full if hasattr(p, "full") else p)


def place(city_name):
    return url("chartroom", f"/place/{slug(city_name)}/")


def city_weather(city_name):
    return url("weather", f"/forecast/{slug(city_name)}/")


def company_registry(c):
    return url("registry", f"/company/{c.registry_no.replace('/', '-')}/")


def listing(ticker):
    return url("exchange", f"/listing/{ticker}/")


def team(team_id):
    return url("vaultball", f"/teams/{team_id}/")


def courier_story(story):
    y, m, d = story.date.year, story.date.month, story.date.day
    return url("courier", f"/{y}/{m:02d}/{d:02d}/{story.slug}/")


def tidings_story(story):
    return url("tidings", f"/news/{story.date.salt().replace('/', '-')}/{story.slug}.html")


def crier_story(story):
    return url("crier", f"/story.html?id={story.id}")


def film(fid):
    return url("reelhouse", f"/title/{fid}/")


def book(bid):
    return url("quillmere", f"/books/{bid}.html")


def lemma(code):
    return url("numerary", f"/roll/{code}/")
