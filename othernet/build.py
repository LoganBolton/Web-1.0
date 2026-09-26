"""Build the whole Weave into a directory of static sites.

    python -m othernet.build            # writes ./web and ./meta
    python -m othernet.build --only bazaar,chartroom
"""
import argparse
import importlib
import json
import os
import shutil
import time

from .engine.web import Web, esc
from .engine import domains

# Sites are built in this order. The last few read what the others produced
# (search index, directory, archive, short links), so they must come last.
ORDER = [
    "chartroom", "commonplace", "numerary", "lexicon", "observatory", "courier", "tidings",
    "crier", "lodestone", "radio", "bazaar", "emberline", "drovers", "hollowmarket", "hearthfind",
    "vantle", "copperkettle", "quillmere", "tastemark", "noticeboard", "exchange", "registry",
    "assembly", "weather", "tramways", "moot", "stats", "post", "patents", "university",
    "annals", "athenaeum", "museum", "reelhouse", "bellows", "vaultball", "chatter",
    "tallowboards", "wrenwrites", "spirekeeper", "ossawatcher", "hearthandhob", "inkling",
    "fathomwiki", "guildwork", "whiskerhaven", "weft", "synod", "quorum", "morrow",
    "stillframe", "snip", "hearthring", "lanthorn",
]


def default_404(site):
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Not found</title>
<style>body{{font-family:Georgia,serif;max-width:560px;margin:80px auto;color:#333}}</style>
</head><body><h1>Nothing here</h1>
<p>The page you asked {esc(site.domain)} for does not exist, or no longer does.</p>
<p><a href="/">Go to the front page of {esc(site.name)}</a></p></body></html>"""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="web")
    ap.add_argument("--meta", default="meta")
    ap.add_argument("--only", default="")
    args = ap.parse_args(argv)

    only = [s for s in args.only.split(",") if s]
    if not only and os.path.isdir(args.out):
        shutil.rmtree(args.out)
    os.makedirs(args.out, exist_ok=True)
    web = Web(args.out)
    t0 = time.time()
    for key in ORDER:
        if only and key not in only:
            continue
        try:
            mod = importlib.import_module(f"othernet.sites.{key}")
        except ModuleNotFoundError as e:
            if e.name == f"othernet.sites.{key}":
                print(f"  (skip {key}: not written yet)")
                continue
            raise
        site = web.site(key)
        if only and os.path.isdir(site.root):
            shutil.rmtree(site.root)
        t = time.time()
        mod.build(web, site)
        if not os.path.exists(os.path.join(site.root, "404.html")):
            site.write("/404.html", default_404(site))
        print(f"  {site.domain:24s} {len(site.pages):5d} pages  {time.time() - t:5.1f}s")
    total = sum(len(s.pages) for s in web.sites.values())
    print(f"built {len(web.sites)} sites, {total} pages, "
          f"{web.bytes_written / 1e6:.1f} MB in {time.time() - t0:.1f}s")
    if not only:
        write_meta(web, args.meta)


def write_meta(web, meta_dir):
    os.makedirs(meta_dir, exist_ok=True)
    sites = []
    for key, (dom, name, cat, nation, indexed, desc) in domains.SITES.items():
        s = web.sites.get(key)
        sites.append({"key": key, "domain": dom, "name": name, "category": cat,
                      "nation": nation, "indexed_by_lanthorn": indexed, "description": desc,
                      "pages": len(s.pages) if s else 0})
    with open(os.path.join(meta_dir, "sites.json"), "w") as f:
        json.dump(sites, f, indent=1)
    with open(os.path.join(meta_dir, "pages.jsonl"), "w") as f:
        for s, p in web.all_pages():
            f.write(json.dumps({"url": p["url"], "title": p["title"], "site": s.domain}) + "\n")
    with open(os.path.join(meta_dir, "facts.jsonl"), "w") as f:
        for fact in web.facts:
            f.write(json.dumps(fact, ensure_ascii=False) + "\n")
    print(f"wrote meta: {len(sites)} sites, {len(web.facts)} facts")


if __name__ == "__main__":
    main()
