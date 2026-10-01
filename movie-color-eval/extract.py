"""Average every frame of a movie into one color, one averaged image, and a color barcode.

Two sources:

    python extract.py archive              # public domain films from movies.json, fetched from archive.org
    python extract.py local ~/Movies       # your own files, named like "Blade Runner (1982).mkv"

Outputs land in data/:
    data/colors.json                 one entry per movie (title, year, hex, rgb, ...)
    data/movies/<slug>/frame.png     pixel-wise average of all sampled frames
    data/movies/<slug>/barcode.png   mean color of each sampled frame, left to right
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
COLORS = DATA / "colors.json"
VIDEO_EXTS = {".mp4", ".mkv", ".mov", ".avi", ".m4v", ".webm", ".mpg", ".mpeg", ".ogv"}
UA = {"User-Agent": "movie-color-eval/0.1"}
MIN_FEATURE_SECONDS = 40 * 60

_lock = threading.Lock()


def slugify(title, year):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return f"{s}-{year}" if year else s


def load_colors():
    if COLORS.exists():
        return {m["slug"]: m for m in json.loads(COLORS.read_text())}
    return {}


def save_entry(entry):
    with _lock:
        colors = load_colors()
        colors[entry["slug"]] = entry
        DATA.mkdir(exist_ok=True)
        rows = sorted(colors.values(), key=lambda m: (m["year"] or 0, m["title"]))
        COLORS.write_text(json.dumps(rows, indent=2) + "\n")


# ---------------------------------------------------------------- frame averaging


def probe_size(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
         "-of", "json", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    s = json.loads(out)["streams"][0]
    return s["width"], s["height"]


def average_video(path, fps=1.0, width=160):
    """Decode the video at `fps` frames per second, downscaled to `width` px wide.

    Returns (mean_rgb, avg_frame uint8 HxWx3, per-frame mean colors Nx3).
    Colors are plain sRGB averages, which is what a naive "average all frames" gives you.
    """
    w, h = probe_size(path)
    height = max(2, round(width * h / w / 2) * 2)
    cmd = [
        "ffmpeg", "-nostdin", "-v", "error", "-i", str(path),
        "-vf", f"fps={fps},scale={width}:{height}:flags=area",
        "-pix_fmt", "rgb24", "-f", "rawvideo", "-",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    frame_bytes = width * height * 3
    total = np.zeros((height, width, 3), dtype=np.float64)
    per_frame = []
    while True:
        buf = proc.stdout.read(frame_bytes)
        if len(buf) < frame_bytes:
            break
        f = np.frombuffer(buf, dtype=np.uint8).reshape(height, width, 3)
        total += f
        per_frame.append(f.reshape(-1, 3).mean(axis=0))
    proc.wait()
    if not per_frame:
        raise RuntimeError(f"ffmpeg produced no frames for {path}")
    avg = total / len(per_frame)
    per_frame = np.array(per_frame)
    return avg.reshape(-1, 3).mean(axis=0), avg.round().astype(np.uint8), per_frame


def barcode_image(per_frame, width=1000, height=200):
    idx = np.linspace(0, len(per_frame), width + 1).astype(int)
    cols = np.array([per_frame[a:max(b, a + 1)].mean(axis=0) for a, b in zip(idx[:-1], idx[1:])])
    strip = np.repeat(cols.round().astype(np.uint8)[None, :, :], height, axis=0)
    return Image.fromarray(strip)


def process(path, title, year, source, fps):
    slug = slugify(title, year)
    mean, frame, per_frame = average_video(path, fps=fps)
    out = DATA / "movies" / slug
    out.mkdir(parents=True, exist_ok=True)
    Image.fromarray(frame).save(out / "frame.png")
    barcode_image(per_frame).save(out / "barcode.png")
    rgb = [int(round(c)) for c in mean]
    entry = {
        "slug": slug,
        "title": title,
        "year": year,
        "hex": "#{:02X}{:02X}{:02X}".format(*rgb),
        "rgb": rgb,
        "frames_sampled": len(per_frame),
        "sample_fps": fps,
        "source": source,
    }
    save_entry(entry)
    print(f"  {entry['hex']}  {title} ({year})  [{len(per_frame)} frames]", flush=True)
    return entry


# ---------------------------------------------------------------- archive.org


def get_json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.load(r)


def parse_length(v):
    if v is None:
        return 0.0
    v = str(v)
    if ":" in v:
        secs = 0.0
        for part in v.split(":"):
            secs = secs * 60 + float(part or 0)
        return secs
    try:
        return float(v)
    except ValueError:
        return 0.0


def item_year(doc):
    for k in ("year", "date"):
        m = re.search(r"\d{4}", str(doc.get(k, "")))
        if m:
            return int(m.group())
    return None


def best_mp4(identifier):
    """Smallest feature-length mp4 in an archive.org item, or None."""
    meta = get_json(f"https://archive.org/metadata/{urllib.parse.quote(identifier)}")
    files = []
    for f in meta.get("files", []):
        name = f.get("name", "")
        if not name.lower().endswith(".mp4"):
            continue
        if parse_length(f.get("length")) < MIN_FEATURE_SECONDS:
            continue
        files.append((int(f.get("size") or 1 << 40), name))
    if not files:
        return None
    _, name = min(files)
    return f"https://archive.org/download/{urllib.parse.quote(identifier)}/{urllib.parse.quote(name)}"


def resolve_archive(movie):
    """Find an archive.org item and mp4 URL for a catalog entry."""
    if movie.get("archive_id"):
        url = best_mp4(movie["archive_id"])
        return movie["archive_id"], url
    title = movie["title"].replace('"', "")
    q = f'title:("{title}") AND mediatype:(movies)'
    params = urllib.parse.urlencode(
        {"q": q, "fl[]": ["identifier", "title", "year", "date", "downloads"], "sort[]": "downloads desc",
         "rows": 25, "output": "json"},
        doseq=True,
    )
    docs = get_json(f"https://archive.org/advancedsearch.php?{params}")["response"]["docs"]
    norm = lambda s: re.sub(r"[^a-z0-9]", "", str(s).lower())
    want = norm(movie["title"])

    def rank(d):
        y = item_year(d)
        year_ok = y is not None and abs(y - movie["year"]) <= 1
        title_ok = want in norm(d.get("title", ""))
        return (not year_ok, not title_ok, -(d.get("downloads") or 0))

    for d in sorted(docs, key=rank)[:8]:
        if want not in norm(d.get("title", "")):
            continue
        url = best_mp4(d["identifier"])
        if url:
            return d["identifier"], url
    return None, None


def run_archive(args):
    catalog = json.loads((ROOT / "movies.json").read_text())
    done = load_colors()
    todo = [m for m in catalog if args.force or slugify(m["title"], m["year"]) not in done]
    if args.only:
        todo = [m for m in todo if args.only.lower() in m["title"].lower()]
    if args.limit:
        todo = todo[: args.limit]
    print(f"{len(todo)} movies to process", flush=True)
    failures = []

    def one(movie):
        label = f"{movie['title']} ({movie['year']})"
        try:
            ident, url = resolve_archive(movie)
            if not url:
                raise RuntimeError("no feature-length mp4 found on archive.org")
            print(f"fetching {label} <- {ident}", flush=True)
            with tempfile.TemporaryDirectory() as tmp:
                dst = Path(tmp) / "movie.mp4"
                subprocess.run(["curl", "-sSfL", "--retry", "3", "-A", UA["User-Agent"], "-o", str(dst), url], check=True)
                process(dst, movie["title"], movie["year"], {"archive_id": ident, "url": url}, args.fps)
        except Exception as e:  # keep going, report at the end
            print(f"FAILED {label}: {e}", flush=True)
            failures.append((label, str(e)))

    with ThreadPoolExecutor(args.workers) as ex:
        list(ex.map(one, todo))
    if failures:
        print(f"\n{len(failures)} failed:")
        for label, err in failures:
            print(f"  {label}: {err}")


# ---------------------------------------------------------------- local files


def run_local(args):
    paths = [p for p in sorted(Path(args.dir).expanduser().rglob("*")) if p.suffix.lower() in VIDEO_EXTS]
    done = load_colors()
    for p in paths:
        m = re.match(r"^(.*?)\s*\((\d{4})\)", p.stem)
        title, year = (m.group(1).strip(), int(m.group(2))) if m else (p.stem, None)
        if not args.force and slugify(title, year) in done:
            print(f"skip {title} (already done)")
            continue
        print(f"processing {p.name}", flush=True)
        try:
            process(p, title, year, {"local_file": p.name}, args.fps)
        except Exception as e:
            print(f"FAILED {p.name}: {e}", flush=True)


def main():
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg is required (brew install ffmpeg / apt install ffmpeg)")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("archive", help="process public domain films from movies.json via archive.org")
    a.add_argument("--only", help="substring of a title to process")
    a.add_argument("--limit", type=int)
    a.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    l = sub.add_parser("local", help="process your own video files (name them 'Title (Year).ext')")
    l.add_argument("dir")
    for p in (a, l):
        p.add_argument("--fps", type=float, default=1.0, help="frames sampled per second of video (default 1)")
        p.add_argument("--force", action="store_true", help="reprocess movies already in colors.json")
    args = ap.parse_args()
    run_archive(args) if args.cmd == "archive" else run_local(args)


if __name__ == "__main__":
    main()
