"""Shared plumbing: choosing distractors and writing an item to disk."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from PIL import Image

from .render import save_gif, save_mp4, save_png

LETTERS = "ABCDE"


@dataclass
class Option:
    label: str  # machine-readable id, e.g. "true" or "gravity_x2"
    desc: str  # human-readable description of the physics used
    params: dict
    image: Image.Image | None = None
    frames: list[Image.Image] = field(default_factory=list)
    rollout: object = None  # task-specific summary used for distance checks


@dataclass
class ItemBuild:
    task: str
    world: dict  # the hidden physics of this world
    setup: dict  # task-specific scene setup (positions, shapes, ...)
    context_frames: list[Image.Image]
    keyframes: list[tuple[Image.Image, str]]
    summary: Image.Image
    query: Image.Image
    options: list[Option]  # options[0] is the correct one
    prompt: dict
    fps: int = 20


def pick_distractors(rng, true_opt: Option, pool: list[Option], dist, min_dist: float, n: int = 4, prefer=()):
    """Greedily pick n distractors that are far from the truth and from each other.

    `prefer` lists labels to try first (e.g. the 'ordinary physics' distractor),
    the rest of the pool is tried in random order.
    """
    preferred = [o for o in pool if o.label in prefer]
    rest = [o for o in pool if o.label not in prefer]
    order = list(rng.permutation(len(rest)))
    candidates = preferred + [rest[i] for i in order]
    chosen: list[Option] = []
    for c in candidates:
        if c.rollout is None:
            continue
        if dist(c.rollout, true_opt.rollout) < min_dist:
            continue
        if any(dist(c.rollout, o.rollout) < min_dist for o in chosen):
            continue
        chosen.append(c)
        if len(chosen) == n:
            return chosen
    return None


def write_item(build: ItemBuild, out_root: str, item_id: str, rng) -> dict:
    """Render everything for one item into out_root/<task>/<item_id>/ and return its manifest row."""
    rel = os.path.join(build.task, item_id)
    d = os.path.join(out_root, rel)
    os.makedirs(os.path.join(d, "frames"), exist_ok=True)

    # Shuffle options; remember where the correct one went.
    perm = list(rng.permutation(len(build.options)))
    opts = [build.options[i] for i in perm]
    answer = LETTERS[perm.index(0)]

    save_gif(build.context_frames, os.path.join(d, "context.gif"), fps=build.fps)
    has_mp4 = save_mp4(build.context_frames, os.path.join(d, "context.mp4"), fps=build.fps)
    save_png(build.summary, os.path.join(d, "context_summary.png"))
    save_png(build.query, os.path.join(d, "query.png"))

    keyframes = []
    for i, (img, caption) in enumerate(build.keyframes):
        name = f"frames/ctx_{i:02d}.png"
        save_png(img, os.path.join(d, name))
        keyframes.append({"path": name, "caption": caption})

    options = []
    for letter, o in zip(LETTERS, opts):
        img_name = f"option_{letter}.png"
        gif_name = f"option_{letter}.gif"
        save_png(o.image, os.path.join(d, img_name))
        if o.frames:
            # rollouts are for humans browsing the data (never shown to the model), so keep them light
            save_gif(o.frames, os.path.join(d, gif_name), fps=build.fps, scale=0.7, frame_step=2)
        options.append(
            {
                "letter": letter,
                "image": img_name,
                "rollout_gif": gif_name if o.frames else None,
                "label": o.label,
                "desc": o.desc,
                "params": o.params,
                "correct": letter == answer,
            }
        )

    meta = {
        "id": item_id,
        "task": build.task,
        "answer": answer,
        "world": build.world,
        "setup": build.setup,
        "prompt": build.prompt,
        "context": {
            "video_gif": "context.gif",
            "video_mp4": "context.mp4" if has_mp4 else None,
            "fps": build.fps,
            "n_frames": len(build.context_frames),
            "summary": "context_summary.png",
            "keyframes": keyframes,
        },
        "query": "query.png",
        "options": options,
    }
    with open(os.path.join(d, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1, default=_json_default)
    row = dict(meta)
    row["dir"] = rel
    return row


def _json_default(o):
    try:
        import numpy as np

        if isinstance(o, np.generic):
            return o.item()
        if isinstance(o, np.ndarray):
            return o.tolist()
    except ImportError:
        pass
    raise TypeError(type(o))


def pick_keyframes(frames_with_t, k):
    """Pick k evenly spaced (frame, t) entries, always including first and last."""
    n = len(frames_with_t)
    if n <= k:
        return list(frames_with_t)
    idx = [round(i * (n - 1) / (k - 1)) for i in range(k)]
    return [frames_with_t[i] for i in idx]
