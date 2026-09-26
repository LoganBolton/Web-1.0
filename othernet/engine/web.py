"""Site objects and the Web that holds them all."""
import html
import json
import os
import re

from . import domains

_TAG_RE = re.compile(r"<[^>]+>")
_SCRIPT_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.S | re.I)
_WS_RE = re.compile(r"\s+")
_HREF_RE = re.compile(r'href="([^"#]+)')


def esc(s):
    return html.escape(str(s), quote=True)


def text_of(html_str):
    s = _SCRIPT_RE.sub(" ", html_str)
    s = _TAG_RE.sub(" ", s)
    s = html.unescape(s)
    return _WS_RE.sub(" ", s).strip()


def nl(items, fmt, sep="\n"):
    return sep.join(fmt(x) for x in items)


class Site:
    """One website. Knows how to write pages under its own domain."""

    def __init__(self, web, key):
        self.web = web
        self.key = key
        (self.domain, self.name, self.category, self.nation, self.indexed,
         self.tagline) = domains.SITES[key]
        self.root = os.path.join(web.out, self.domain)
        self.pages = []
        self.shell = None  # function(site, title, body, **kw) -> full html

    # --- urls ---------------------------------------------------------------
    def url(self, path="/"):
        return f"http://{self.domain}{path}"

    # --- writing ------------------------------------------------------------
    def _fs_path(self, path):
        assert path.startswith("/"), path
        rel = path.lstrip("/")
        if rel == "" or rel.endswith("/"):
            rel += "index.html"
        elif "." not in rel.rsplit("/", 1)[-1]:
            # Extension-less URLs like /@handle are stored as /@handle.html
            rel += ".html"
        return os.path.join(self.root, rel)

    def write(self, path, content, binary=False):
        fp = self._fs_path(path)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        if binary:
            with open(fp, "wb") as f:
                f.write(content)
        else:
            with open(fp, "w", encoding="utf-8") as f:
                f.write(content)
        self.web.bytes_written += len(content)

    def json(self, path, obj):
        self.write(path, json.dumps(obj, separators=(",", ":"), ensure_ascii=False))

    def page(self, path, title, body, index=True, **kw):
        """Render body with the site's shell and write it."""
        full = self.shell(self, title, body, **kw) if self.shell else default_shell(
            self, title, body, **kw)
        self.write(path, full)
        self.pages.append({"url": self.url(path), "title": title,
                           "text": text_of(body)[:4000], "index": index, "links": self._links(full)})
        return self.url(path)

    def _links(self, html_str):
        out = set()
        for h in _HREF_RE.findall(html_str):
            h = html.unescape(h)
            if h.startswith("http://"):
                out.add(h.split("?")[0])
            elif h.startswith("/"):
                out.add(self.url(h.split("?")[0]))
        return sorted(out)

    def raw_page(self, path, title, full_html, index=True):
        self.write(path, full_html)
        self.pages.append({"url": self.url(path), "title": title,
                           "text": text_of(full_html)[:4000], "index": index,
                           "links": self._links(full_html)})
        return self.url(path)

    def redirect(self, path, target, delay=0, message=""):
        body = (f'<!doctype html><html><head><meta charset="utf-8">'
                f'<meta http-equiv="refresh" content="{delay};url={esc(target)}">'
                f'<title>Moved</title></head><body>'
                f'<p>{esc(message) or "This page has moved."} '
                f'<a href="{esc(target)}">{esc(target)}</a></p></body></html>')
        self.write(path, body)

    def fact(self, key, question, answer, path_or_url, how="text", hops=1, note=""):
        url = path_or_url if path_or_url.startswith("http") else self.url(path_or_url)
        self.web.facts.append({"id": key, "question": question, "answer": answer, "url": url,
                               "site": self.domain, "modality": how, "hops": hops,
                               "note": note})


def default_shell(site, title, body, head="", css="", scripts="", body_class=""):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<style>{css}</style>{head}
</head><body class="{body_class}">
{body}
{scripts}
</body></html>"""


class Web:
    def __init__(self, out):
        self.out = out
        self.sites = {}
        self.facts = []
        self.bytes_written = 0

    def site(self, key):
        if key not in self.sites:
            self.sites[key] = Site(self, key)
        return self.sites[key]

    def all_pages(self):
        for s in self.sites.values():
            for p in s.pages:
                yield s, p
