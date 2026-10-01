# Movie Color Eval

Average every frame of a movie down to one color, then ask a model which movie it was. Each question
has 10 choices, so guessing gets about 10%.

## Pipeline

1. `extract.py` decodes each film at 1 frame per second (downscaled to 160 px wide) and writes
   - the **average color** (plain sRGB mean of every pixel of every sampled frame) to `data/colors.json`
   - the **average frame** (pixel-by-pixel mean, a blurry ghost image) to `data/movies/<slug>/frame.png`
   - a **barcode** (each frame's mean color, left to right over the runtime) to `data/movies/<slug>/barcode.png`
2. `build_questions.py` makes `data/questions.jsonl`. Each question is the right movie plus 9
   distractors picked at random (fixed seed) from the other movies in the dataset.
3. `run_eval.py` sends the questions to any models on OpenRouter and scores them.
4. `gallery.py` renders `data/gallery.png` so you can eyeball everything at once.

## Setup

Python 3.10+ and ffmpeg.

```bash
pip install -r requirements.txt
```

## Getting movies

**Public domain films (default).** `movies.json` lists 50 public domain features (silents, noir,
B movies, and a handful of Technicolor titles like *A Star Is Born* (1937) and *Charade*).

```bash
python extract.py archive              # all of them, 4 at a time
python extract.py archive --only charade
```

This finds each film on archive.org, downloads the smallest feature-length mp4, averages it, and
deletes the video. If a search picks the wrong item, pin it with `"archive_id": "..."` in `movies.json`.
The GitHub Actions workflow `.github/workflows/movie-color-extract.yml` runs this automatically
whenever `movies.json` changes and commits the results.

**Your own movies.** Name files `Title (Year).ext` and point the extractor at the folder.

```bash
python extract.py local ~/Movies
```

Local and archive results land in the same `colors.json`, so mixing in popular modern films is just
dropping files in a folder. Re-run `build_questions.py` afterwards.

## Running the eval

```bash
export OPENROUTER_API_KEY=sk-or-...
python build_questions.py
python run_eval.py --models openai/gpt-5,anthropic/claude-sonnet-4.5,google/gemini-2.5-pro --mode hex
```

`--mode` picks what the model sees (comma separate to run several):

| mode      | model sees |
|-----------|------------|
| `hex`     | the color as text, e.g. `#4A3F38 (RGB 74, 63, 56)` |
| `swatch`  | a solid square of the color, no text |
| `frame`   | the averaged frame image |
| `barcode` | the per-frame color barcode |

Other flags: `--limit N`, `--concurrency 8`, `--max-tokens`, `--temperature`,
`--reasoning-effort low|medium|high`. Every response is saved to `results/<timestamp>/` (gitignored)
along with `summary.json`, and a table prints at the end.

## Notes

- Black and white films all average to similar grays, so those questions are mostly about whether
  a model can tell a slightly warm (sepia, tinted) gray from a neutral one. Color films and your own
  modern titles are where the signal is. Swap in more color films for a harder, fairer test.
- Letterboxing and credits pull every average toward black. That's left in on purpose since it's
  what a naive "average all frames" gives you.
