"""Turn mentions of known things into links, once each, in escaped text."""
import re

from .web import esc


class Linker:
    def __init__(self, targets):
        """targets: dict of phrase -> url."""
        self.targets = {k: v for k, v in targets.items() if len(k) > 3}
        phrases = sorted(self.targets, key=len, reverse=True)
        self.re = re.compile(r"\b(" + "|".join(re.escape(esc(p)) for p in phrases) + r")\b") \
            if phrases else None
        self.unesc = {esc(p): p for p in phrases}

    def __call__(self, text, skip=(), used=None):
        """Escape `text` and link the first mention of each phrase not in `skip`."""
        s = esc(text)
        if not self.re:
            return s
        used = used if used is not None else set()

        def rep(m):
            phrase = self.unesc.get(m.group(1), m.group(1))
            if phrase in used or phrase in skip:
                return m.group(0)
            used.add(phrase)
            return f'<a href="{esc(self.targets[phrase])}">{m.group(0)}</a>'

        return self.re.sub(rep, s)
