# Weird Physics Bench

A benchmark for in-context learning of unfamiliar physics. Each item shows a model a short video
of a simulated 2D world whose physics has been tampered with (gravity that is weak, huge, tilted or
pointing sideways, wind, drag, odd bounciness, an unknown launcher strength). The model then gets a
new situation in the same world and has to pick which of five images shows what really happens next.

Every image comes from an actual simulation. The right answer is simulated with the world's true
parameters. The four wrong answers are simulated from the exact same starting state with different
parameters, so every option is physically consistent and only the video tells you which world you
are in. One wrong option is usually "ordinary physics" (plain downward gravity, no wind, normal
bounce), which measures how often a model ignores the video and falls back on its prior.

Open `viewer.html` in a browser to browse everything, quiz yourself, and see model picks.

## Tasks

| Task | Context video | Question | Hidden physics |
| --- | --- | --- | --- |
| `slingshot` | Two demo launches from slingshots at different spots, pull distances and angles | A new slingshot is pulled back. Which flight path and landing spot is right? | gravity strength and tilt, sideways wind, air drag, launcher strength (speed per meter of pull) |
| `bounce` | A ball bouncing around a box for 2.5 to 4 s | Which path does the ball follow over the next 1.5 s? | gravity strength and direction, restitution, air drag, wall friction |
| `gravflip` | Shapes float with gravity off, then gravity switches on and they collapse | A new floating arrangement in the same world. What does it look like 1.5 s after gravity switches on? | gravity direction (any, often sideways or up), gravity strength, elasticity, friction |

Images carry a 1 m grid, a clock, and trail dots every 0.1 s so timing can be read off a still.
The slingshot and bounce worlds use a small custom integrator. Gravity flip uses
[pymunk](https://www.pymunk.org) (Chipmunk2D) rigid-body physics.

Distractors are chosen from a pool of perturbations per task (for example gravity x0.5 or x2,
gravity rotated, wind flipped, launcher 30% stronger, much bouncier, frictionless). A distractor is
only used if its outcome is clearly different from the truth and from the other distractors
(at least 2.5 m apart at the landing point or apex for slingshot, 1 m mean path distance for
bounce, 1.2 m mean shape displacement for gravity flip). The answer letter is shuffled.

## Quick start

```bash
pip install -e .            # numpy, pillow, pymunk, anthropic
python -m weirdphys.generate --n 10          # 10 items per task into data/ (about a minute)
open viewer.html                             # or just double-click it
```

`data/` in this repo already holds a 30-item sample (seed 0), so the viewer works straight away.
ffmpeg is optional. When present, each item also gets a `context.mp4`.

More options

```bash
python -m weirdphys.generate --tasks bounce --n 200 --out data_big --seed 1
python -m weirdphys.generate --n 10 --start 10    # add items 10..19 to the existing set
```

Each item is reproducible from `(seed, task, index)`.

## Running a model

```bash
export ANTHROPIC_API_KEY=...
python -m weirdphys.eval_claude --limit 2                    # smoke test, 2 items per task
python -m weirdphys.eval_claude                              # full run, claude-opus-5-5, effort high
python -m weirdphys.eval_claude --context summary            # only the one-image summary of the video
python -m weirdphys.eval_claude --model claude-sonnet-5-5 --effort medium
python -m weirdphys.eval_claude --dry-run --limit 1          # print exactly what the model is sent
python -m weirdphys.report                                   # accuracy table, then reload viewer.html
```

The Messages API takes images, not video, so the context video is sent as 8 timestamped keyframes
plus one summary still (`--context frames|summary|both`, default `both`). A request is about 15
images. Results go to `results/<model>__<context>.jsonl`, and an interrupted run resumes where it
stopped. `report` prints accuracy per task (chance is 20%), how often the model picked the
"ordinary physics" option, and a breakdown of which wrong physics it fell for. It also writes
`results/results.js`, which makes model picks and full responses show up in the viewer.

The prompt builder in `weirdphys/prompt.py` is provider-neutral (an ordered list of text and image
parts), so wiring up another model is a short adapter.

## Item layout

```
data/
  manifest.jsonl          one row per item (same content as each meta.json)
  manifest.js             the same rows for viewer.html
  bounce/bounce_0000/
    meta.json             answer, hidden world physics, scene setup, prompt text, per-option physics
    context.gif / .mp4    the context video
    frames/ctx_00..07.png keyframes sent to the model (captions in meta.json)
    context_summary.png   the whole context in one still
    query.png             the new situation
    option_A..E.png       the five candidate futures
    option_A..E.gif       a rollout animation of each candidate (for browsing, never sent to the model)
```

## Code

- `weirdphys/tasks/slingshot.py`, `bounce.py`, `gravflip.py` sample a world, simulate it, build the distractor pool and render
- `weirdphys/item.py` picks distractors, shuffles options and writes files
- `weirdphys/render.py` is a small supersampled 2D renderer on Pillow
- `weirdphys/generate.py`, `eval_claude.py`, `report.py` are the command-line entry points
- `viewer.html` is a static browser with a quiz mode

## Ideas for next

- Video answer options (four rollouts, pick the plausible one) instead of stills
- Fewer cues (no pull or angle labels, no trail dots) as a harder setting
- Worlds where the rule changes over time, such as gravity rotating 90 degrees after every flip
- More scenes, for example pendulums, conveyor belts, magnets, or springs with odd stiffness
- A training split, to see whether fine-tuning on weird worlds improves in-context adaptation
