"""Short links on snip.ves. Some are chained, and some point at places that no longer exist."""
from .domains import url

SNIPS = {
    "c4nal": url("registry", "/company/CR-47-409117/"),
    "petrel": url("weather", "/warnings/"),
    "vc7a": url("vantle", "/support/recall-vc7a/"),
    "p1th": url("observatory", "/crossing/"),
    "poll": url("crier", "/poll.html"),
    "hob1": url("hearthandhob", "/recipe/gorse-hollow-apple-cake/"),
    "vault": url("vaultball", "/vault-cup/"),
    "moot31": url("moot", "/ruling/1292-31/"),
    "lost": url("whiskerhaven", "/found/"),
    "sallow": url("wrenwrites", "/411/07/sixty-one-days-along-the-sallow.html"),
    "read": url("athenaeum", "/weave-resources/"),
    # a chain: snip -> snip -> destination
    "go": url("snip", "/go2"),
    "go2": url("snip", "/go3"),
    "go3": url("stillframe", "/site/gildmere.ves/"),
    # dead: the site is gone
    "gw": "http://gildmere.ves/people/",
    "old1": "http://gildmere.ves/",
    # points at a page that was moved
    "tt": url("tramways", "/timetables/"),
}
