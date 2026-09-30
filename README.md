# WebSim

A fake internet for testing web agents. It has 54 sites and about 8,800 pages set in a made-up
world, so models can't rely on what they already know about the real web.

All sites are generated from one world simulation, so facts line up across sites except where
they're supposed to conflict. There's a spoiler guide to the world in `docs/WORLD.md`.

## Running it

Python 3.11, no dependencies.

```bash
python -m othernet.build   # writes web/ and meta/
python -m othernet.serve   # http://127.0.0.1:8080
```

In a browser, go to http://morrow.ves.localhost:8080/. For Playwright or curl, use the server as
a proxy and hit the fictional hostnames directly:

```bash
curl -x http://127.0.0.1:8080 http://bazaar.ves/
```

Good entry points are `morrow.ves` (portal), `lanthorn.ves` (search), and `hearthring.fol`
(directory). Search only indexes some of the sites.

## Evals

`evals/questions.jsonl` has 224 questions with one answer each. `evals/grade.py` scores them.
The build also writes ground truth to `meta/` (sites, pages, facts). See
[evals/README.md](evals/README.md).

`harness/` runs agents like Codex against the questions through
[Harbor](https://github.com/harbor-framework/harbor) in a sandboxed browser. See
[harness/README.md](harness/README.md).

```bash
bash harness/build_images.sh && python harness/make_tasks.py
OPENAI_API_KEY=... harbor run -c harness/codex-job.yaml
```

## Checks

```bash
python tools/check_links.py web
python tools/check_svg.py web
python -m othernet.evalgen          # regenerate and verify questions
node tools/smoke_test.js            # needs Playwright and the server running
node tools/verify_interactive.js
```

## Layout

- `othernet/world/`: the simulation (calendar, people, companies, news, etc.)
- `othernet/engine/`: page writer, SVG generators, shared site features
- `othernet/sites/`: one module per site
- `othernet/build.py`, `othernet/serve.py`

Builds are deterministic. Randomness is seeded by name.
