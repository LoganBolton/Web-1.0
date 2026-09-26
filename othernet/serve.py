"""Serve the Weave.

One server, three ways in:

1. As an HTTP proxy (best for agents and Playwright). Point the browser's
   proxy at this server and visit the real fictional URLs, e.g.
   http://bazaar.ves/ . Nothing is rewritten.

       chromium --proxy-server=http://127.0.0.1:8080

2. Through *.localhost subdomains (best for a human with a normal browser).
   Visit http://morrow.ves.localhost:8080/ . Links between sites are rewritten
   on the fly to stay on localhost.

3. By Host header, for tools that let you set it (curl -H 'Host: bazaar.ves').

    python -m othernet.serve [--port 8080] [--web web]
"""
import argparse
import mimetypes
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, unquote

from .engine import domains

mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("application/json", ".json")
mimetypes.add_type("text/javascript", ".js")

KNOWN = {v[0] for v in domains.SITES.values()}
TEXT_TYPES = ("text/html", "text/css", "text/javascript", "application/json", "image/svg+xml")
LINK_RE = re.compile(r"http://(" + "|".join(re.escape(d) for d in sorted(KNOWN, key=len, reverse=True)) + r")(?=[/\"'?#\s<)]|$)")


class Handler(BaseHTTPRequestHandler):
    web_root = "web"
    server_version = "Weave/1.0"

    def log_message(self, fmt, *args):
        if os.environ.get("WEAVE_QUIET"):
            return
        sys.stderr.write("[weave] " + fmt % args + "\n")

    def _resolve(self):
        """Return (domain, path, rewrite_suffix) for this request."""
        raw = self.path
        if raw.startswith("http://") or raw.startswith("https://"):
            parts = urlsplit(raw)
            return parts.hostname, parts.path or "/", None
        host = (self.headers.get("Host") or "").lower()
        hostname, _, port = host.partition(":")
        if hostname.endswith(".localhost"):
            dom = hostname[: -len(".localhost")]
            suffix = f".localhost:{port}" if port else ".localhost"
            return dom, urlsplit(raw).path, suffix
        return hostname, urlsplit(raw).path, None

    def do_CONNECT(self):
        # No TLS on the Weave. Refuse so browsers fall back to plain http.
        self.send_error(502, "The Weave does not speak https")

    def do_HEAD(self):
        self.do_GET(head=True)

    def do_GET(self, head=False):
        dom, path, suffix = self._resolve()
        if dom not in KNOWN:
            if dom in ("localhost", "127.0.0.1", "") or dom is None:
                return self._launcher(head)
            return self._send(404, "text/html", _unknown_domain(dom).encode(), head)
        fp = self._find(dom, unquote(path))
        if fp is None:
            nf = os.path.join(self.web_root, dom, "404.html")
            body = open(nf, "rb").read() if os.path.exists(nf) else b"Not found"
            return self._send(404, "text/html", self._rewrite(body, suffix, "text/html"), head)
        ctype = mimetypes.guess_type(fp)[0] or "text/html"
        with open(fp, "rb") as f:
            body = f.read()
        self._send(200, ctype, self._rewrite(body, suffix, ctype), head)

    def _find(self, dom, path):
        base = os.path.realpath(os.path.join(self.web_root, dom))
        rel = path.lstrip("/")
        cand = os.path.realpath(os.path.join(base, rel))
        if not cand.startswith(base):
            return None
        options = [cand]
        if os.path.isdir(cand):
            options = [os.path.join(cand, "index.html")]
        else:
            options.append(cand + ".html")
        for o in options:
            if os.path.isfile(o):
                return o
        return None

    def _rewrite(self, body, suffix, ctype):
        if not suffix or not any(ctype.startswith(t) for t in TEXT_TYPES):
            return body
        s = body.decode("utf-8", "replace")
        s = LINK_RE.sub(lambda m: f"http://{m.group(1)}{suffix}", s)
        return s.encode("utf-8")

    def _send(self, code, ctype, body, head):
        self.send_response(code)
        if ctype.startswith("text/") or ctype in ("application/json", "image/svg+xml"):
            ctype += "; charset=utf-8"
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        if not head:
            self.wfile.write(body)

    def _launcher(self, head):
        port = self.server.server_address[1]
        rows = "".join(
            f'<li><a href="http://{v[0]}.localhost:{port}/">{v[0]}</a> <small>{v[1]}</small></li>'
            for v in sorted(domains.SITES.values()))
        body = f"""<!doctype html><meta charset="utf-8"><title>The Weave</title>
<style>body{{font-family:system-ui,sans-serif;max-width:720px;margin:40px auto;line-height:1.5}}
li{{margin:2px 0}} small{{color:#777}}</style>
<h1>The Weave is running</h1>
<p>Start where a resident of Averra would: <a href="http://morrow.ves.localhost:{port}/">morrow.ves</a>
(the portal), <a href="http://lanthorn.ves.localhost:{port}/">lanthorn.ves</a> (search), or
<a href="http://hearthring.fol.localhost:{port}/">hearthring.fol</a> (the directory).</p>
<p>For agents, use this server as an HTTP proxy
(<code>--proxy-server=http://127.0.0.1:{port}</code>) and visit the real addresses.</p>
<details><summary>All {len(domains.SITES)} sites (spoilers)</summary><ul>{rows}</ul></details>"""
        self._send(200, "text/html", body.encode(), head)


def _unknown_domain(dom):
    return f"""<!doctype html><meta charset="utf-8"><title>Address not found</title>
<body style="font-family:system-ui;max-width:560px;margin:80px auto;color:#444">
<h2>This Weave address could not be found</h2>
<p>No loom answers at <b>{dom}</b>. Check the spelling, or try searching on
<a href="http://lanthorn.ves/">Lanthorn</a>.</p></body>"""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--web", default="web")
    args = ap.parse_args(argv)
    if not os.path.isdir(args.web):
        print(f"No built web at {args.web!r}. Building it first...")
        from . import build
        build.main(["--out", args.web])
    Handler.web_root = args.web
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"The Weave is up on http://{args.host}:{args.port}/  "
          f"(try http://morrow.ves.localhost:{args.port}/)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
