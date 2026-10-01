"""Turn data/colors.json into 10-way multiple choice questions.

    python build_questions.py                 # writes data/questions.jsonl
    python build_questions.py --choices 10 --seed 0

Each question has the right movie plus 9 distractors drawn from the other movies in the dataset,
so every title a model sees is one that also shows up as a real answer somewhere else.
Extra distractor titles (strings like "Jaws (1975)") can be added with --extra-distractors FILE.
"""

import argparse
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def label(m):
    return f"{m['title']} ({m['year']})" if m.get("year") else m["title"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--colors", default=ROOT / "data" / "colors.json")
    ap.add_argument("--out", default=ROOT / "data" / "questions.jsonl")
    ap.add_argument("--choices", type=int, default=10)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--extra-distractors", help="text file, one title per line")
    args = ap.parse_args()

    movies = json.loads(Path(args.colors).read_text())
    pool = [label(m) for m in movies]
    if args.extra_distractors:
        pool += [s.strip() for s in Path(args.extra_distractors).read_text().splitlines() if s.strip()]
    pool = sorted(set(pool))
    if len(pool) < args.choices:
        raise SystemExit(f"need at least {args.choices} titles to build questions, have {len(pool)}")

    rng = random.Random(args.seed)
    with open(args.out, "w") as f:
        for m in movies:
            answer = label(m)
            choices = rng.sample([t for t in pool if t != answer], args.choices - 1) + [answer]
            rng.shuffle(choices)
            q = {
                "id": m["slug"],
                "slug": m["slug"],
                "hex": m["hex"],
                "rgb": m["rgb"],
                "choices": choices,
                "answer": LETTERS[choices.index(answer)],
                "answer_title": answer,
            }
            f.write(json.dumps(q) + "\n")
    print(f"wrote {len(movies)} questions to {args.out}")


if __name__ == "__main__":
    main()
