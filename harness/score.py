"""Summarise a Harbor job over the Weave tasks, broken down like evals/grade.py.

    python harness/score.py                 # the newest job under jobs/
    python harness/score.py jobs/<job> --show-wrong

Trials that crashed or timed out before writing an answer count as wrong and are listed.
"""
import argparse
import glob
import json
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("job", nargs="?", help="job directory (default: newest under jobs/)")
    ap.add_argument("--questions", default=os.path.join(ROOT, "evals", "questions.jsonl"))
    ap.add_argument("--show-wrong", action="store_true")
    a = ap.parse_args(argv)
    job = a.job or max(glob.glob("jobs/*/"), key=os.path.getmtime, default=None)
    if not job:
        sys.exit("no jobs found")
    qs = {q["id"]: q for q in map(json.loads, open(a.questions, encoding="utf-8"))}
    tally = defaultdict(lambda: [0, 0])
    wrong, errors = [], []
    for res in sorted(glob.glob(os.path.join(job, "*", "result.json"))):
        r = json.load(open(res))
        qid = (r.get("task_name") or "").split("/")[-1]
        if qid not in qs:
            continue
        q = qs[qid]
        reward = ((r.get("verifier_result") or {}).get("rewards") or {}).get("reward", 0.0)
        ok = reward >= 1.0
        for key in ("all", f"difficulty:{q['difficulty']}", f"modality:{q['modality']}"):
            tally[key][0] += ok
            tally[key][1] += 1
        if r.get("exception_info"):
            errors.append((qid, r["exception_info"].get("exception_type", "error")))
        if not ok:
            g = os.path.join(os.path.dirname(res), "verifier", "grade.json")
            got = json.load(open(g)).get("answer") if os.path.exists(g) else None
            wrong.append((q, got))
    if not tally:
        sys.exit(f"no Weave trials in {job}")
    print(job)
    for key in sorted(tally, key=lambda k: (k != "all", k)):
        n_ok, n = tally[key]
        print(f"{key:26s} {n_ok:4d}/{n:<4d} {100 * n_ok / n:5.1f}%")
    if errors:
        print(f"\n{len(errors)} trial(s) ended with an exception: " + ", ".join(f"{i} ({t})" for i, t in errors))
    if a.show_wrong:
        for q, got in wrong:
            print(f"\n{q['id']} [{q['difficulty']}] {q['question']}\n   gold: {q['answer']}   got: {got}")


if __name__ == "__main__":
    main()
