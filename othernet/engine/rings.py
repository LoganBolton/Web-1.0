"""Webrings: small circles of personal sites that link to each other.

Each member site shows a ring widget with previous/next links that go through
hearthring.fol, which redirects to the neighbouring member.
"""
from .domains import url

RINGS = {
    "lamplit": ("The Lamplit Ring", "Personal pages kept by hand, lit by lamplight.",
                ["wrenwrites", "spirekeeper", "hearthandhob", "inkling", "ossawatcher", "whiskerhaven"]),
    "deepweave": ("The Deep Weave Ring", "Sites Lanthorn will never show you.",
                  ["ossawatcher", "tallowboards", "noticeboard", "moot", "synod"]),
}


def widget(ring, key, style=""):
    name, blurb, members = RINGS[ring]
    return (f'<div class="webring" style="border:2px ridge #999;padding:6px 10px;margin:14px 0;font:13px Georgia,serif;{style}">'
            f'This site is a member of <a href="{url("hearthring", f"/ring/{ring}/")}">{name}</a>. '
            f'<a href="{url("hearthring", f"/ring/{ring}/prev/{key}/")}">&laquo; prev</a> | '
            f'<a href="{url("hearthring", f"/ring/{ring}/random/")}">random</a> | '
            f'<a href="{url("hearthring", f"/ring/{ring}/next/{key}/")}">next &raquo;</a></div>')
