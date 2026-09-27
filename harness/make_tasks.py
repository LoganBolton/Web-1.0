"""Turn the Weave eval questions into Harbor tasks.

    python harness/make_tasks.py                       # all 224 questions
    python harness/make_tasks.py --difficulty easy --limit 20
    python harness/make_tasks.py --ids e001,m010,h014 --browser-mode dom

Each task gets its own directory under harness/tasks/ (git-ignored). The agent sees only
instruction.md, which holds the question and nothing else from questions.jsonl. The gold
answer lives in tests/ (built into a separate grader container that the agent never
shares) and in solution/ (uploaded only when you run Harbor's oracle agent).
"""
import argparse
import json
import os
import random
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TIMEOUTS = {"easy": 600, "medium": 900, "hard": 1500}

INSTRUCTION = """\
You are browsing the Weave, the internet of a world called Averra. It is not the real
internet, and what you know about the real world will not help you here.

Your only way onto the Weave is the `browser` tool, a web browser you control. Start at
{start} (a portal) and go wherever you need to. Search engines, directories, links, forms,
logins and archives all work the way they would on a real web. Only plain http:// Weave
addresses work in that browser. Nothing on this computer contains the answer, and this
computer cannot reach the Weave or the real internet except through the browser tool.

Question: {question}

Give a short, exact answer (a name, number, date, code or short phrase), with no explanation.
When you are done, write it to /logs/artifacts/answer.txt, for example

    echo 'Brineholt' > /logs/artifacts/answer.txt

Only that file is graded.
"""

TASK_TOML = """\
schema_version = "1.3"

[task]
name = "websim/{id}"
description = "WebSim question {id} ({difficulty}, {modality}): answer a question by browsing the Weave."
keywords = ["websim", "web-browsing", "computer-use", "retrieval"]

[metadata]
difficulty = "{difficulty}"
category = "web-retrieval"
tags = {tags}
websim_id = "{id}"
modality = "{modality}"
hops = {hops}
browser_mode = "{browser_mode}"

[environment]
docker_image = "websim-agent:latest"
# The agent may reach its model API and its browser, and nothing else.
network_mode = "allowlist"
allowed_hosts = {allowed_hosts}
cpus = 1
memory_mb = 2048

[[environment.mcp_servers]]
name = "browser"
transport = "streamable-http"
url = "http://browser:8931/mcp"

[agent]
timeout_sec = {timeout}

[verifier]
# Grade in a fresh container built from tests/. The agent never runs there, and only
# /logs/artifacts is carried over from the agent's machine.
environment_mode = "separate"
timeout_sec = 120

[verifier.environment]
network_mode = "no-network"
build_timeout_sec = 600
"""

COMPOSE = """\
# main (the agent's machine) reaches the browser over the default network. Only the browser
# is attached to the private `weave` network, so the agent has no direct route to the Weave.
services:
  main:
    depends_on:
      browser:
        condition: service_healthy
  browser:
    image: websim-browser:latest
    environment:
      BROWSER_MODE: {browser_mode}
    # Used once at startup to remove the browser's route to the real internet.
    cap_add: [NET_ADMIN]
    networks: [default, weave]
    depends_on:
      weave:
        condition: service_healthy
  weave:
    image: websim-weave:latest
    networks: [weave]

networks:
  weave:
    internal: true
"""

TEST_DOCKERFILE = """\
FROM python:3.12-slim
COPY grade.py question.json /tests/
COPY --chmod=755 test.sh /tests/test.sh
"""

TEST_SH = """\
#!/bin/bash
# Grade /logs/artifacts/answer.txt against the gold answer with evals/grade.py.
mkdir -p /logs/verifier
python3 - <<'PY'
import json, sys
sys.path.insert(0, "/tests")
from grade import correct

q = json.load(open("/tests/question.json"))
try:
    pred = open("/logs/artifacts/answer.txt", encoding="utf-8", errors="replace").read().strip()
except FileNotFoundError:
    pred = None
ok = bool(pred) and correct(q, pred, strict=q.get("strict", False))
open("/logs/verifier/reward.txt", "w").write("1" if ok else "0")
json.dump({"id": q["id"], "correct": ok, "answer": pred, "gold": q["answer"]},
          open("/logs/verifier/grade.json", "w"), ensure_ascii=False, indent=1)
print(("CORRECT" if ok else "WRONG"), "| got:", repr(pred), "| gold:", repr(q["answer"]))
PY
"""

SOLVE_SH = """\
#!/bin/bash
# Oracle: writes the gold answer. Harbor uploads this only for `-a oracle`.
mkdir -p /logs/artifacts
cat > /logs/artifacts/answer.txt <<'ANSWER'
{answer}
ANSWER
"""


def toml_list(xs):
    return "[" + ", ".join(json.dumps(x) for x in xs) + "]"


def write(path, text, mode=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    if mode:
        os.chmod(path, mode)


def make_task(q, out, args):
    d = os.path.join(out, q["id"])
    if os.path.isdir(d):
        shutil.rmtree(d)
    hosts = ["browser"] + args.allow_host
    write(os.path.join(d, "task.toml"), TASK_TOML.format(
        id=q["id"], difficulty=q["difficulty"], modality=q["modality"], hops=q.get("hops", 1),
        tags=toml_list([q["difficulty"], q["modality"], q.get("topic", "misc")]),
        browser_mode=args.browser_mode, allowed_hosts=toml_list(hosts),
        timeout=args.timeout or TIMEOUTS[q["difficulty"]]))
    write(os.path.join(d, "instruction.md"), INSTRUCTION.format(start=args.start_url, question=q["question"]))
    write(os.path.join(d, "environment", "docker-compose.yaml"), COMPOSE.format(browser_mode=args.browser_mode))
    gold = {k: q[k] for k in ("id", "answer", "accept", "kind", "tolerance") if k in q}
    gold["strict"] = args.strict
    write(os.path.join(d, "tests", "question.json"), json.dumps(gold, ensure_ascii=False, indent=1) + "\n")
    shutil.copy(os.path.join(ROOT, "evals", "grade.py"), os.path.join(d, "tests", "grade.py"))
    write(os.path.join(d, "tests", "Dockerfile"), TEST_DOCKERFILE)
    write(os.path.join(d, "tests", "test.sh"), TEST_SH, 0o755)
    write(os.path.join(d, "solution", "solve.sh"), SOLVE_SH.format(answer=q["answer"]), 0o755)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--questions", default=os.path.join(ROOT, "evals", "questions.jsonl"))
    ap.add_argument("--out", default=os.path.join(HERE, "tasks"))
    ap.add_argument("--ids", default="", help="comma-separated question ids")
    ap.add_argument("--difficulty", default="", help="easy, medium, hard (comma-separated)")
    ap.add_argument("--modality", default="", help="text, image, interaction, source (comma-separated)")
    ap.add_argument("--limit", type=int, default=0, help="keep a random sample of this many")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--browser-mode", choices=["vision", "hybrid", "dom"], default="vision",
                    help="vision: screenshots and x,y clicks. hybrid: plus accessibility snapshots. dom: snapshots only")
    ap.add_argument("--allow-host", action="append", default=[],
                    help="host the agent may reach (its model API). Default api.openai.com. Repeatable")
    ap.add_argument("--start-url", default="http://morrow.ves/")
    ap.add_argument("--timeout", type=int, default=0, help="agent timeout in seconds (default by difficulty)")
    ap.add_argument("--strict", action="store_true", help="the answer must be only the answer (see evals/grade.py)")
    ap.add_argument("--clean", action="store_true", help="delete the output directory first")
    args = ap.parse_args(argv)
    args.allow_host = args.allow_host or ["api.openai.com"]

    qs = [json.loads(line) for line in open(args.questions, encoding="utf-8") if line.strip()]
    if args.ids:
        want = set(args.ids.split(","))
        qs = [q for q in qs if q["id"] in want]
    if args.difficulty:
        qs = [q for q in qs if q["difficulty"] in args.difficulty.split(",")]
    if args.modality:
        qs = [q for q in qs if q["modality"] in args.modality.split(",")]
    if args.limit and len(qs) > args.limit:
        qs = sorted(random.Random(args.seed).sample(qs, args.limit), key=lambda q: q["id"])
    if not qs:
        sys.exit("no questions matched")
    if args.clean and os.path.isdir(args.out):
        shutil.rmtree(args.out)
    for q in qs:
        make_task(q, args.out, args)
    print(f"wrote {len(qs)} tasks to {os.path.relpath(args.out)} (browser mode {args.browser_mode})")


if __name__ == "__main__":
    main()
