"""Summarise eval results and export them for the viewer.

    python -m weirdphys.report                # reads results/*.jsonl

Prints accuracy per run and task, plus how often each kind of wrong answer was
picked. The 'ordinary_physics' / 'earth_gravity' rate is the interesting one: it
measures how often the model falls back on everyday physics instead of what the
video showed.
Also writes results/results.js so viewer.html can show model picks.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
from collections import Counter, defaultdict

PRIOR_LABELS = {"ordinary_physics", "earth_gravity"}


def load(results_dir):
    runs = {}
    for path in sorted(glob.glob(os.path.join(results_dir, "*.jsonl"))):
        name = os.path.basename(path)[: -len(".jsonl")]
        with open(path) as f:
            rows = [json.loads(line) for line in f if line.strip()]
        # keep the latest row per item
        runs[name] = list({r["id"]: r for r in rows}.values())
    return runs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    args = ap.parse_args()
    runs = load(args.results)
    if not runs:
        print(f"no results in {args.results}/")
        return

    for name, rows in runs.items():
        print(f"\n== {name}  ({len(rows)} items, chance = 20%)")
        by_task = defaultdict(list)
        for r in rows:
            by_task[r["task"]].append(r)
        by_task["ALL"] = rows
        print(f"  {'task':<10} {'acc':>6} {'n':>4}   {'picked everyday-physics option':>30}")
        for task, rs in by_task.items():
            acc = sum(r["correct"] for r in rs) / len(rs)
            prior = sum(r["chosen_label"] in PRIOR_LABELS for r in rs) / len(rs)
            print(f"  {task:<10} {acc:6.1%} {len(rs):>4}   {prior:30.1%}")
        wrong = Counter(r["chosen_label"] or "(no answer)" for r in rows if not r["correct"])
        if wrong:
            print("  wrong picks by distractor type: " + ", ".join(f"{k} {v}" for k, v in wrong.most_common()))

    export = {
        name: {
            r["id"]: {k: r.get(k) for k in ("pred", "correct", "chosen_label", "response", "model", "context", "effort")}
            for r in rows
        }
        for name, rows in runs.items()
    }
    out = os.path.join(args.results, "results.js")
    with open(out, "w") as f:
        f.write("window.WEIRDPHYS_RESULTS = ")
        json.dump(export, f)
        f.write(";\n")
    print(f"\nwrote {out} (open viewer.html to browse model picks)")


if __name__ == "__main__":
    main()
