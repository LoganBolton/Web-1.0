"""Run a Claude model on the benchmark.

    export ANTHROPIC_API_KEY=...
    python -m weirdphys.eval_claude --limit 3                       # quick smoke test
    python -m weirdphys.eval_claude --model claude-opus-5-5 --effort high
    python -m weirdphys.eval_claude --context summary --tasks bounce
    python -m weirdphys.eval_claude --dry-run --limit 1             # print the prompt, no API call

Results are appended to results/<model>__<context>.jsonl (one line per item),
so an interrupted run picks up where it left off. Summarise with
`python -m weirdphys.report`.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .prompt import MODES, build_parts

ANSWER_RE = re.compile(r"ANSWER:\s*\**\s*\(?([A-E])\b", re.IGNORECASE)


def load_manifest(data_dir: str) -> list[dict]:
    with open(os.path.join(data_dir, "manifest.jsonl")) as f:
        return [json.loads(line) for line in f if line.strip()]


def to_content(parts: list[dict]) -> list[dict]:
    content = []
    for p in parts:
        if p["type"] == "text":
            content.append({"type": "text", "text": p["text"]})
        else:
            with open(p["path"], "rb") as f:
                data = base64.standard_b64encode(f.read()).decode()
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": data}})
    return content


def parse_answer(text: str) -> str | None:
    m = ANSWER_RE.findall(text or "")
    return m[-1].upper() if m else None


def run_one(client, args, row) -> dict:
    import anthropic

    item_dir = os.path.join(args.data, row["dir"])
    parts = build_parts(row, item_dir, args.context)
    kwargs = dict(
        model=args.model,
        max_tokens=args.max_tokens,
        messages=[{"role": "user", "content": to_content(parts)}],
        output_config={"effort": args.effort},
    )
    if args.fallback:
        # Server-side refusal fallback: if the model declines, the API retries on a fallback model.
        kwargs.update(betas=["server-side-fallback-2026-07-01"], fallbacks="default")
    t0 = time.time()
    for attempt in range(4):
        try:
            msg = client.beta.messages.create(**kwargs)
            break
        except (anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.InternalServerError):
            if attempt == 3:
                raise
            time.sleep(10 * (attempt + 1))
    text = "".join(b.text for b in msg.content if b.type == "text")
    pred = parse_answer(text) if msg.stop_reason != "refusal" else None
    chosen = next((o for o in row["options"] if o["letter"] == pred), None)
    return {
        "id": row["id"],
        "task": row["task"],
        "model": args.model,
        "served_model": msg.model,
        "context": args.context,
        "effort": args.effort,
        "answer": row["answer"],
        "pred": pred,
        "correct": pred == row["answer"],
        "chosen_label": chosen["label"] if chosen else None,
        "stop_reason": msg.stop_reason,
        "response": text,
        "usage": {"input_tokens": msg.usage.input_tokens, "output_tokens": msg.usage.output_tokens},
        "seconds": round(time.time() - t0, 1),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", default="data")
    ap.add_argument("--model", default="claude-opus-5-5")
    ap.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--context", default="both", choices=MODES)
    ap.add_argument("--tasks", default="", help="comma-separated subset of tasks")
    ap.add_argument("--limit", type=int, default=0, help="max items per task (0 = all)")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--no-fallback", dest="fallback", action="store_false", help="disable the refusal fallback")
    ap.add_argument("--out", default="", help="output jsonl (default results/<model>__<context>.jsonl)")
    ap.add_argument("--dry-run", action="store_true", help="print the prompt parts instead of calling the API")
    args = ap.parse_args()

    rows = load_manifest(args.data)
    if args.tasks:
        keep = set(args.tasks.split(","))
        rows = [r for r in rows if r["task"] in keep]
    if args.limit:
        seen: dict[str, int] = {}
        kept = []
        for r in rows:
            seen[r["task"]] = seen.get(r["task"], 0) + 1
            if seen[r["task"]] <= args.limit:
                kept.append(r)
        rows = kept

    if args.dry_run:
        for r in rows:
            print(f"===== {r['id']}  (answer {r['answer']})")
            for p in build_parts(r, os.path.join(args.data, r["dir"]), args.context):
                print(p["text"] if p["type"] == "text" else f"  [image] {p['path']}")
        return

    import anthropic

    out = args.out or os.path.join("results", f"{args.model}__{args.context}.jsonl")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    done = set()
    if os.path.exists(out):
        with open(out) as f:
            done = {json.loads(line)["id"] for line in f if line.strip()}
    todo = [r for r in rows if r["id"] not in done]
    print(f"{len(rows)} items selected, {len(done)} already in {out}, running {len(todo)}")

    client = anthropic.Anthropic()
    lock = threading.Lock()
    n_ok = n_done = 0
    with ThreadPoolExecutor(args.concurrency) as ex, open(out, "a") as f:
        futs = {ex.submit(run_one, client, args, r): r for r in todo}
        for fut in as_completed(futs):
            r = futs[fut]
            try:
                res = fut.result()
            except Exception as e:  # keep going; the item will be retried on the next run
                print(f"  {r['id']:<18} ERROR {type(e).__name__}: {e}")
                continue
            with lock:
                f.write(json.dumps(res) + "\n")
                f.flush()
                n_done += 1
                n_ok += res["correct"]
            mark = "ok " if res["correct"] else "x  "
            print(f"  {mark}{res['id']:<18} pred={res['pred']} answer={res['answer']} "
                  f"({res['chosen_label']})  running acc {n_ok}/{n_done}")
    print(f"done -> {out}. Run `python -m weirdphys.report` for a summary.")


if __name__ == "__main__":
    main()
