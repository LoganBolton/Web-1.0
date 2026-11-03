"""Generate benchmark items.

    python -m weirdphys.generate --n 10                 # 10 items per task into data/
    python -m weirdphys.generate --tasks bounce --n 50 --out data_big --workers 8

Every item is reproducible from (seed, task, index).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from .item import write_item
from .tasks import bounce, gravflip, slingshot

TASKS = {
    "slingshot": slingshot.build,
    "bounce": bounce.build,
    "gravflip": gravflip.build,
}


def item_seed(seed: int, task: str, index: int) -> int:
    h = hashlib.sha256(f"{seed}/{task}/{index}".encode()).digest()
    return int.from_bytes(h[:8], "little")


def _make(args):
    out, seed, task, index = args
    rng = np.random.default_rng(item_seed(seed, task, index))
    t0 = time.time()
    build = TASKS[task](rng)
    row = write_item(build, out, f"{task}_{index:04d}", rng)
    return row, time.time() - t0


def write_manifest(out: str):
    """Collect every meta.json under `out` into manifest.jsonl + manifest.js (for the viewer)."""
    rows = []
    for task in sorted(os.listdir(out)):
        tdir = os.path.join(out, task)
        if not os.path.isdir(tdir):
            continue
        for item in sorted(os.listdir(tdir)):
            p = os.path.join(tdir, item, "meta.json")
            if os.path.exists(p):
                with open(p) as f:
                    row = json.load(f)
                row["dir"] = f"{task}/{item}"
                rows.append(row)
    with open(os.path.join(out, "manifest.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(out, "manifest.js"), "w") as f:
        f.write("window.WEIRDPHYS_MANIFEST = ")
        json.dump(rows, f)
        f.write(";\n")
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="data")
    ap.add_argument("--n", type=int, default=10, help="items per task")
    ap.add_argument("--start", type=int, default=0, help="first item index (to extend a dataset)")
    ap.add_argument("--tasks", default=",".join(TASKS))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    args = ap.parse_args()

    tasks = [t.strip() for t in args.tasks.split(",") if t.strip()]
    for t in tasks:
        if t not in TASKS:
            raise SystemExit(f"unknown task {t!r}; choose from {sorted(TASKS)}")
    os.makedirs(args.out, exist_ok=True)
    jobs = [(args.out, args.seed, t, i) for t in tasks for i in range(args.start, args.start + args.n)]
    t0 = time.time()
    if args.workers > 1:
        with ProcessPoolExecutor(args.workers) as ex:
            for row, dt in ex.map(_make, jobs):
                print(f"  {row['id']:<18} answer={row['answer']}  {dt:5.1f}s")
    else:
        for j in jobs:
            row, dt = _make(j)
            print(f"  {row['id']:<18} answer={row['answer']}  {dt:5.1f}s")
    rows = write_manifest(args.out)
    print(f"wrote {len(jobs)} items in {time.time() - t0:.0f}s; manifest has {len(rows)} items -> {args.out}/manifest.jsonl")


if __name__ == "__main__":
    main()
