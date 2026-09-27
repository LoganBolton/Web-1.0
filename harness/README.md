# Running agents on the Weave with Harbor

This folder turns the eval questions into [Harbor](https://github.com/harbor-framework/harbor)
tasks. Each task gives an agent (Codex by default) one question and a web browser it drives
with screenshots, clicks and typing. The agent never gets a copy of the Weave, the questions
file, or the answers.

## How a trial is laid out

```
 agent's machine (main)          browser                  weave
 Codex, a shell, no repo  --->  Playwright MCP    --->   the Weave server
 files, no answers        MCP   + Chromium        proxy  (all 54 sites)
        |
        | only the model API
        v
   api.openai.com
                                 grader (separate container, no network)
                                 gets only /logs/artifacts/answer.txt
```

* **main** is where Codex runs. It is built from `images/agent`, which copies nothing from
  this repo. Harbor's egress control lets it reach only its model API and the browser.
* **browser** runs Playwright MCP and headless Chromium. Every page request goes through the
  Weave server, which refuses anything that is not a Weave address. On startup it deletes
  its own route to the real internet and drops all privileges, so the MCP server's
  code-running tool cannot reach the real internet either.
* **weave** serves the sites. It sits on a private network that only the browser can reach,
  so the agent cannot `curl` pages or scrape the site files. It has to use the browser.
* **grader** is built from the task's `tests/` folder, which is where the gold answer lives.
  Harbor runs it in a separate container after the agent has finished, with no network, and
  copies over only `/logs/artifacts`. The answer is never inside the agent's container.
* Codex's own web search runs on OpenAI's servers, outside these network rules. It cannot
  help with a fictional world, but it could find this public repo, so `codex-job.yaml` turns
  it off. Keep it off if you write your own job file.

## Setup

You need Docker (Linux, or on macOS a runtime whose VM kernel has nftables `fib` support,
such as OrbStack. Docker Desktop's VM may lack it) and Harbor, which needs Python 3.12+.

```bash
uv tool install harbor            # or: pip install harbor
bash harness/build_images.sh      # builds websim-weave, websim-browser, websim-agent (a few minutes)
python harness/make_tasks.py      # writes harness/tasks/<id>/ for all 224 questions
```

`build_images.sh` builds the Weave from source inside the image, so you do not need to run
`python -m othernet.build` first. Rebuild the images after changing the world or the sites.

## Check the sandbox first (no API key needed)

```bash
harbor run -p harness/tasks -a oracle -e docker -n 4 -y                 # should score 100%
PYTHONPATH=harness harbor run -p harness/tasks/e001 -a probe_agent:ProbeAgent -e docker -y
```

The oracle writes the gold answers, which checks the grading path. The probe agent plays a
cheater. From inside the agent's machine it searches the disk for answer files, tries to
reach the Weave server, GitHub and the grader directly, and then drives the browser over MCP
the way Codex does, including trying to get out through the browser's code-running tool. It
fails the trial if any of that works, or if the browser cannot open the Weave. Its report is
in `jobs/<job>/<trial>/agent/probe.json`.

## Run Codex

```bash
export OPENAI_API_KEY=sk-...
harbor run -c harness/codex-job.yaml                    # all tasks in harness/tasks
harbor run -c harness/codex-job.yaml -m openai/<model>  # pick the model
harbor run -c harness/codex-job.yaml -p harness/tasks/h014
python harness/score.py --show-wrong                    # scores by difficulty and modality
```

To use a ChatGPT subscription instead of an API key, run `codex login` on your machine.
Codex then talks to ChatGPT's servers rather than the API, so allow those hosts when you
make the tasks, and tell Harbor to copy `~/.codex/auth.json` into each trial.

```bash
python harness/make_tasks.py --clean --allow-host chatgpt.com --allow-host auth.openai.com --allow-host api.openai.com
CODEX_FORCE_AUTH_JSON=1 harbor run -c harness/codex-job.yaml
```

Each trial's full Codex transcript, including every browser action, ends up under
`jobs/<job>/<trial>/agent/`. `harbor view jobs` opens a viewer.

## Choosing tasks

```bash
python harness/make_tasks.py --clean --difficulty hard
python harness/make_tasks.py --clean --modality image,interaction --limit 20 --seed 1
python harness/make_tasks.py --clean --ids e001,m010,h014
```

| Option | What it does |
|---|---|
| `--browser-mode vision` | Default. Screenshots and x,y mouse actions, no page text dumps. Closest to computer use. |
| `--browser-mode hybrid` | Screenshots and x,y actions plus accessibility snapshots of each page. |
| `--browser-mode dom` | Accessibility snapshots only, no coordinate tools. |
| `--allow-host HOST` | A host the agent may reach. Default `api.openai.com`. Add yours if you use a proxy or another provider. |
| `--strict` | Grade with `evals/grade.py --strict` (the answer must be only the answer). |
| `--timeout SEC` | Agent time limit. Default 10, 15 and 25 minutes for easy, medium and hard. |

Every trial starts three containers and two small Docker networks. Docker's default address
pools run out at around 30 networks, so keep `n_concurrent_trials` at about 10 or less
unless you have widened `default-address-pools` in the Docker daemon config.

## Other agents

Any Harbor agent that supports MCP servers works (`-a claude-code`, `-a gemini-cli` and so
on). Add its API host with `--allow-host` when you make the tasks. The agent image has Codex
preinstalled. Other agents install themselves during setup, which needs their download
hosts too, or a custom image.

## Files

| File | Purpose |
|---|---|
| `build_images.sh` | Builds the three shared images |
| `images/weave` | The Weave server image |
| `images/browser` | Playwright MCP and Chromium, with the network lockdown in `entrypoint.sh` |
| `images/agent` | The agent's machine, with Codex |
| `make_tasks.py` | Writes one Harbor task per question into `harness/tasks/` |
| `codex-job.yaml` | Harbor job settings for Codex |
| `probe_agent.py` | The sandbox check described above |
| `score.py` | Summarises a finished job |
