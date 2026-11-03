"""Turn an item into an ordered list of text and image parts.

This is provider-neutral: each part is {"type": "text", "text": ...} or
{"type": "image", "path": ...}. eval_claude.py converts it to API content
blocks; any other harness can do the same.

Context modes
  frames   8 keyframes from the context video (with timestamps)
  summary  one still that summarises the whole context (trails, timing dots)
  both     keyframes followed by the summary (default)
"""

from __future__ import annotations

import os

MODES = ("frames", "summary", "both")

ANSWER_INSTRUCTION = (
    "Reason about what the context reveals about this world's physics, then compare the options. "
    "End your reply with a final line of the form `ANSWER: X`, where X is one of A, B, C, D, E."
)


def build_parts(meta: dict, item_dir: str, mode: str = "both") -> list[dict]:
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    p = meta["prompt"]
    ctx = meta["context"]
    parts: list[dict] = [{"type": "text", "text": p["intro"]}]

    if mode in ("frames", "both"):
        kf = ctx["keyframes"]
        parts.append({"type": "text", "text": f"CONTEXT VIDEO: {len(kf)} frames sampled in order from the video."})
        for i, k in enumerate(kf):
            parts.append({"type": "text", "text": f"Frame {i + 1} ({k['caption']}):"})
            parts.append({"type": "image", "path": os.path.join(item_dir, k["path"])})
    if mode in ("summary", "both"):
        parts.append({"type": "text", "text": "CONTEXT SUMMARY (the whole video in one picture):"})
        parts.append({"type": "image", "path": os.path.join(item_dir, ctx["summary"])})

    parts.append({"type": "text", "text": "QUERY:"})
    parts.append({"type": "image", "path": os.path.join(item_dir, meta["query"])})
    parts.append({"type": "text", "text": p["question"]})
    for o in meta["options"]:
        parts.append({"type": "text", "text": f"Option {o['letter']}:"})
        parts.append({"type": "image", "path": os.path.join(item_dir, o["image"])})
    parts.append({"type": "text", "text": ANSWER_INSTRUCTION})
    return parts
