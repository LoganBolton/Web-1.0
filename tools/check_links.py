"""Find broken links across the built Weave.

    python tools/check_links.py [web_dir]

Links are resolved the same way the server resolves them. A few dead links
are deliberate (gildmere.ves is gone, snip.ves/tt points at a moved page);
they are listed under EXPECTED and reported separately.
"""
import collections
import os
import re
import sys
from urllib.parse import urlsplit, unquote

ROOT = sys.argv[1] if len(sys.argv) > 1 else "web"
ATTR = re.compile(r'(?:href|src)="([^"]+)"')
EXPECTED = {"http://gildmere.ves/", "http://gildmere.ves/people/", "http://tramways.slt/timetables/"}


def exists(dom, path):
    base = os.path.join(ROOT, dom)
    rel = unquote(path).lstrip("/")
    cand = os.path.join(base, rel)
    if os.path.isdir(cand):
        return os.path.isfile(os.path.join(cand, "index.html"))
    return os.path.isfile(cand) or os.path.isfile(cand + ".html")


def main():
    domains = set(os.listdir(ROOT))
    broken = collections.defaultdict(list)
    expected = []
    checked = 0
    for dom in sorted(domains):
        for dirpath, _, files in os.walk(os.path.join(ROOT, dom)):
            for f in files:
                if not f.endswith(".html"):
                    continue
                fp = os.path.join(dirpath, f)
                page = "/" + os.path.relpath(fp, os.path.join(ROOT, dom)).replace(os.sep, "/")
                with open(fp, encoding="utf-8") as fh:
                    html = fh.read()
                for link in ATTR.findall(html):
                    link = link.replace("&amp;", "&")
                    if link.startswith(("#", "mailto:", "javascript:", "data:")) or "'" in link or "+" in link and "'" in link:
                        continue
                    if link.startswith("http://"):
                        parts = urlsplit(link)
                        tdom, tpath = parts.hostname, parts.path or "/"
                    elif link.startswith("/"):
                        tdom, tpath = dom, urlsplit(link).path
                    elif link.startswith("?"):
                        continue
                    else:
                        base = page.rsplit("/", 1)[0] + "/"
                        tdom, tpath = dom, os.path.normpath(base + urlsplit(link).path)
                    checked += 1
                    full = f"http://{tdom}{tpath}"
                    if tdom not in domains or not exists(tdom, tpath):
                        if full in EXPECTED or full.split("?")[0] in EXPECTED:
                            expected.append((dom + page, full))
                        else:
                            broken[dom].append((page, full))
    total = sum(len(v) for v in broken.values())
    print(f"checked {checked:,} links; {total} broken; {len(expected)} expected-dead")
    for dom, items in sorted(broken.items(), key=lambda kv: -len(kv[1])):
        print(f"  {dom}: {len(items)}")
        for page, full in items[:6]:
            print(f"      {page} -> {full}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
