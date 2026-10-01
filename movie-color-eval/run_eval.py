"""Ask models on OpenRouter which movie an average color came from.

    export OPENROUTER_API_KEY=sk-or-...
    python run_eval.py --models openai/gpt-5,anthropic/claude-opus-4.5 --mode hex
    python run_eval.py --models google/gemini-2.5-pro --mode frame,barcode --limit 10

Modes (what the model is shown):
    hex       the average color as text, hex plus RGB
    swatch    a solid image of the average color, no text
    frame     the pixel-wise average of all frames (a blurry ghost image)
    barcode   the per-frame colors laid out left to right over the runtime

Every question has 10 choices, so random guessing scores about 10%.
Results go to results/<timestamp>/ as one jsonl per model and mode plus summary.json.
"""

import argparse
import base64
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
API = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/") + "/chat/completions"
MODES = ("hex", "swatch", "frame", "barcode")

INTRO = {
    "hex": "I took every frame of a movie and averaged them all together into a single color. That color is {hex} (RGB {r}, {g}, {b}).",
    "swatch": "I took every frame of a movie and averaged them all together into a single color. The attached image is a solid swatch of that color.",
    "frame": "I took every frame of a movie and averaged them pixel by pixel into one image. The attached image is that average frame.",
    "barcode": "I sampled a movie once per second and replaced each frame with its average color. The attached image lays those colors out left to right from the first minute to the last.",
}


def prompt_text(q, mode):
    r, g, b = q["rgb"]
    lines = [INTRO[mode].format(hex=q["hex"], r=r, g=g, b=b), "", "Which movie is it?", ""]
    lines += [f"{chr(65 + i)}. {c}" for i, c in enumerate(q["choices"])]
    lines += ["", "Think it through if you like, then end your reply with a final line of the form \"Answer: X\" where X is a single letter."]
    return "\n".join(lines)


def image_data_url(q, mode):
    from PIL import Image

    if mode == "swatch":
        img = Image.new("RGB", (256, 256), tuple(q["rgb"]))
    else:
        img = Image.open(ROOT / "data" / "movies" / q["slug"] / f"{mode}.png").convert("RGB")
        if mode == "frame":
            img = img.resize((img.width * 4, img.height * 4), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def build_messages(q, mode):
    text = prompt_text(q, mode)
    if mode == "hex":
        return [{"role": "user", "content": text}]
    return [{"role": "user", "content": [
        {"type": "text", "text": text},
        {"type": "image_url", "image_url": {"url": image_data_url(q, mode)}},
    ]}]


def call(model, messages, args, key):
    body = {"model": model, "messages": messages}
    if args.max_tokens:
        body["max_tokens"] = args.max_tokens
    if args.temperature is not None:
        body["temperature"] = args.temperature
    if args.reasoning_effort:
        body["reasoning"] = {"effort": args.reasoning_effort}
    data = json.dumps(body).encode()
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "X-Title": "movie-color-eval",
    }
    delay = 2.0
    for attempt in range(6):
        try:
            req = urllib.request.Request(API, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=args.timeout) as r:
                resp = json.load(r)
            if "error" in resp:
                raise RuntimeError(json.dumps(resp["error"]))
            return resp
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:500]
            if e.code in (408, 429, 500, 502, 503, 504) and attempt < 5:
                time.sleep(delay)
                delay *= 2
                continue
            raise RuntimeError(f"HTTP {e.code}: {detail}") from None
        except (urllib.error.URLError, TimeoutError, RuntimeError):
            if attempt < 5:
                time.sleep(delay)
                delay *= 2
                continue
            raise


def parse_answer(text, n):
    valid = "".join(chr(65 + i) for i in range(n))
    hits = re.findall(rf"answer\s*[:\-]?\s*\**\s*\(?([{valid}])\b", text or "", re.I)
    if hits:
        return hits[-1].upper()
    lone = re.fullmatch(rf"\s*\(?([{valid}])[\).]?\s*", text or "")
    return lone.group(1).upper() if lone else None


def run_one(model, mode, q, args, key):
    rec = {"model": model, "mode": mode, "id": q["id"], "answer": q["answer"], "answer_title": q["answer_title"]}
    try:
        resp = call(model, build_messages(q, mode), args, key)
        text = resp["choices"][0]["message"].get("content") or ""
        guess = parse_answer(text, len(q["choices"]))
        rec.update(
            guess=guess,
            guess_title=q["choices"][ord(guess) - 65] if guess else None,
            correct=guess == q["answer"],
            response=text,
            usage=resp.get("usage"),
        )
    except Exception as e:
        rec.update(guess=None, correct=False, error=str(e))
    return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", required=True, help="comma separated OpenRouter model ids")
    ap.add_argument("--mode", default="hex", help=f"comma separated, any of {', '.join(MODES)}")
    ap.add_argument("--questions", default=ROOT / "data" / "questions.jsonl")
    ap.add_argument("--limit", type=int, help="only the first N questions")
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--max-tokens", type=int)
    ap.add_argument("--temperature", type=float)
    ap.add_argument("--reasoning-effort", choices=["minimal", "low", "medium", "high"])
    ap.add_argument("--timeout", type=float, default=300)
    ap.add_argument("--out", help="output dir (default results/<timestamp>)")
    args = ap.parse_args()

    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        sys.exit("set OPENROUTER_API_KEY")
    modes = [m.strip() for m in args.mode.split(",")]
    for m in modes:
        if m not in MODES:
            sys.exit(f"unknown mode {m!r}, pick from {MODES}")
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    questions = [json.loads(line) for line in Path(args.questions).read_text().splitlines() if line.strip()]
    if args.limit:
        questions = questions[: args.limit]

    out = Path(args.out or ROOT / "results" / datetime.now().strftime("%Y%m%d-%H%M%S"))
    out.mkdir(parents=True, exist_ok=True)
    summary = []
    for model in models:
        for mode in modes:
            print(f"{model} / {mode}: {len(questions)} questions", flush=True)
            with ThreadPoolExecutor(args.concurrency) as ex:
                recs = list(ex.map(lambda q: run_one(model, mode, q, args, key), questions))
            fname = out / f"{model.replace('/', '__')}__{mode}.jsonl"
            fname.write_text("".join(json.dumps(r) + "\n" for r in recs))
            n = len(recs)
            correct = sum(r["correct"] for r in recs)
            errors = sum("error" in r for r in recs)
            unparsed = sum(r.get("guess") is None and "error" not in r for r in recs)
            summary.append({"model": model, "mode": mode, "n": n, "correct": correct,
                            "accuracy": correct / n if n else 0.0, "errors": errors, "unparsed": unparsed})

    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    w = max(len(s["model"]) for s in summary)
    print(f"\n{'model':<{w}}  {'mode':<8} {'acc':>6}  {'correct':>9}  err  unparsed")
    for s in summary:
        print(f"{s['model']:<{w}}  {s['mode']:<8} {s['accuracy']:>6.1%}  {s['correct']:>4}/{s['n']:<4}  {s['errors']:>3}  {s['unparsed']:>8}")
    print(f"\nchance is {1 / len(questions[0]['choices']):.0%}. results in {out}")


if __name__ == "__main__":
    main()
