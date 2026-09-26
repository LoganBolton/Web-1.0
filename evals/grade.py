"""Grade answers to the Weave eval questions.

    python evals/grade.py predictions.jsonl [--questions evals/questions.jsonl] [--strict] [--show-wrong]

predictions.jsonl has one JSON object per line: {"id": "e001", "answer": "Brineholt"}.
Questions with no prediction count as wrong.

Matching
  number questions  the first number in the answer must equal the gold number, within
                    the question's tolerance (or half a unit of the gold's last decimal).
                    Commas, currency and units are ignored. Unicode fractions (2¼) work.
  set questions     every item of the gold list must appear, in any order.
  text questions    the normalised answer must equal the gold answer or an accepted
                    variant. Without --strict it may also contain it as whole words,
                    as long as the answer is not much longer than the gold (so padding a
                    reply with every candidate does not score).
"""
import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict

FRACTIONS = {"¼": .25, "½": .5, "¾": .75, "⅓": 1 / 3, "⅔": 2 / 3, "⅛": .125}
NUM = re.compile(r"\d+\s+\d+/\d+|\d+/\d+|-?\d[\d,]*(?:\.\d+)?(?:\s*[¼½¾⅓⅔⅛])?|[¼½¾⅓⅔⅛]")
SCALE = {"thousand": 1e3, "million": 1e6, "billion": 1e9}


def norm(s):
    s = unicodedata.normalize("NFKC", str(s)).lower()
    s = s.replace("–", "-").replace("—", "-").replace("·", ".")
    s = re.sub(r"[\"'‘’“”.,!?;:()]", " ", s)
    s = re.sub(r"\b(the|a|an|and)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def parse_num(tok):
    tok = tok.strip()
    if re.fullmatch(r"\d+\s+\d+/\d+", tok):
        w, f = tok.split()
        a, b = f.split("/")
        return int(w) + int(a) / int(b)
    if re.fullmatch(r"\d+/\d+", tok):
        a, b = tok.split("/")
        return int(a) / int(b)
    frac = 0.0
    if tok and tok[-1] in FRACTIONS:
        frac = FRACTIONS[tok[-1]]
        tok = tok[:-1].strip()
    if not tok:
        return frac
    return float(tok.replace(",", "")) + frac


def first_number(s):
    s = unicodedata.normalize("NFC", str(s))
    m = NUM.search(s)
    if not m:
        return None
    v = parse_num(m.group(0))
    after = re.match(r"\s*(thousand|million|billion)\b", s[m.end():], re.I)
    return v * SCALE[after.group(1).lower()] if after else v


def default_tol(gold):
    m = re.search(r"\d[\d,]*(?:\.(\d+))?", gold)
    if not m:
        return 0.0
    return 0.5 * 10 ** -(len(m.group(1)) if m.group(1) else 0)


def correct(q, pred, strict=False):
    if pred is None:
        return False
    golds = [q["answer"]] + q.get("accept", [])
    p = norm(pred)
    if any(p == norm(g) for g in golds):
        return True
    if q.get("kind") == "set":
        want = {norm(x) for x in q["answer"].split(",")}
        got = set(p.split())
        return want <= got and len(got) <= len(want) + 6
    if q.get("kind") == "number":
        want = first_number(q["answer"])
        got = first_number(pred)
        if want is not None and got is not None:
            tol = max(q.get("tolerance") or 0.0, default_tol(q["answer"]))
            if abs(want - got) <= tol + 1e-9:
                return True
    if not strict:
        for g in golds:
            ng = norm(g)
            if ng and re.search(r"(^| )" + re.escape(ng) + r"( |$)", p) and len(p) <= 3 * len(ng) + 20:
                return True
    return False


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("predictions")
    ap.add_argument("--questions", default="evals/questions.jsonl")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--show-wrong", action="store_true")
    a = ap.parse_args(argv)
    qs = [json.loads(l) for l in open(a.questions)]
    preds = {}
    for line in open(a.predictions):
        if line.strip():
            d = json.loads(line)
            preds[d["id"]] = d.get("answer")
    tally = defaultdict(lambda: [0, 0])
    wrong = []
    for q in qs:
        ok = correct(q, preds.get(q["id"]), a.strict)
        for key in ("all", f"difficulty:{q['difficulty']}", f"modality:{q['modality']}"):
            tally[key][0] += ok
            tally[key][1] += 1
        if not ok:
            wrong.append((q, preds.get(q["id"])))
    for key in sorted(tally, key=lambda k: (k != "all", k)):
        r, n = tally[key]
        print(f"{key:26s} {r:4d}/{n:<4d} {100 * r / n:5.1f}%")
    if a.show_wrong:
        for q, p in wrong:
            print(f"\n{q['id']} [{q['difficulty']}] {q['question']}\n   gold: {q['answer']}   got: {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
