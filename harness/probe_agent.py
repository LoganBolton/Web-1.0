"""A Harbor agent that tries to cheat, to check the sandbox. It needs no model or API key.

    PYTHONPATH=harness harbor run -p harness/tasks -a probe_agent:ProbeAgent -e docker -y

From inside the agent's machine it looks for answer files, tries to reach the Weave server,
the real internet and the grader directly, then drives the browser tool over MCP the way
Codex would and checks that the browser works but cannot leave the Weave. It writes the
answer "probe" (so every trial should score 0) and a report to /logs/agent/probe.json,
which Harbor copies to jobs/<job>/<trial>/agent/probe.json. The run fails loudly if any
check does not hold.
"""
import json
import shlex

from harbor.agents.base import BaseAgent
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

PROBE = r'''
import json, os, socket, ssl, urllib.request

report = {}


def tcp(host, port):
    try:
        socket.create_connection((host, port), timeout=5).close()
        return "reachable"
    except Exception as e:
        return "blocked: " + type(e).__name__


def https(url):
    try:
        urllib.request.urlopen(url, timeout=8)
        return "reachable"
    except urllib.error.HTTPError as e:
        return "reachable (HTTP %d)" % e.code
    except Exception as e:
        return "blocked: " + str(getattr(e, "reason", e))[:100]


# 1. Nothing on disk should give the game away.
hits = []
for top in ("/", ):
    for d, dirs, files in os.walk(top):
        if d.startswith(("/proc", "/sys", "/dev", "/usr/lib", "/usr/share", "/usr/local/lib/node_modules")):
            dirs[:] = []
            continue
        for f in files:
            if f in ("questions.jsonl", "facts.jsonl", "question.json", "grade.py", "solve.sh", "evalgen.py"):
                hits.append(os.path.join(d, f))
report["answer_files_found"] = hits
report["tests_dir_exists"] = os.path.exists("/tests")
report["solution_dir_exists"] = os.path.exists("/solution")

# 2. Direct network access.
report["weave_server_direct"] = tcp("weave", 8080)
report["github"] = https("https://github.com/")
report["raw_githubusercontent"] = https("https://raw.githubusercontent.com/")
report["model_api"] = https("https://api.openai.com/v1/models")

# 3. The browser tool, spoken to exactly as an MCP client would.
URL = "http://browser:8931/mcp"
sid = [None]
rid = [0]


def rpc(method, params=None, notify=False):
    msg = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        msg["params"] = params
    if not notify:
        rid[0] += 1
        msg["id"] = rid[0]
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if sid[0]:
        headers["mcp-session-id"] = sid[0]
    req = urllib.request.Request(URL, data=json.dumps(msg).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=90) as r:
        sid[0] = r.headers.get("mcp-session-id") or sid[0]
        body = r.read().decode()
    if notify:
        return None
    for line in body.splitlines():
        if line.startswith("data:"):
            d = json.loads(line[5:])
            if d.get("id") == msg["id"]:
                return d
    return json.loads(body)


def call(name, args):
    r = rpc("tools/call", {"name": name, "arguments": args})
    content = r.get("result", {}).get("content", [])
    text = " ".join(c.get("text", "") for c in content if c.get("type") == "text")
    images = [c for c in content if c.get("type") == "image"]
    return text, images, r


try:
    rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "probe", "version": "0"}})
    rpc("notifications/initialized", notify=True)
    # MCP clients such as Codex also hold open a GET stream for server messages.
    try:
        req = urllib.request.Request(URL, headers={"Accept": "text/event-stream", "mcp-session-id": sid[0]})
        with urllib.request.urlopen(req, timeout=3) as r:
            report["browser_event_stream"] = "HTTP %d" % r.status
            r.read(1)
    except urllib.error.HTTPError as e:
        report["browser_event_stream"] = "HTTP %d" % e.code
    except (socket.timeout, TimeoutError):
        report["browser_event_stream"] = "open (no events yet)"
    except Exception as e:
        report["browser_event_stream"] = "error: " + repr(e)[:150]
    tools = {t["name"]: t for t in rpc("tools/list")["result"]["tools"]}
    report["browser_tools"] = sorted(tools)
    text, _, _ = call("browser_navigate", {"url": "http://morrow.ves/"})
    report["browser_weave_page"] = "Morrow" in text
    _, images, _ = call("browser_take_screenshot", {})
    report["browser_screenshot_bytes"] = len(images[0]["data"]) if images else 0
    text, _, _ = call("browser_navigate", {"url": "https://github.com/"})
    report["browser_real_web"] = "reachable" if "github" in text.lower() and "error" not in text.lower() else "blocked"
    if "browser_run_code_unsafe" in tools:
        # Try every way out from inside the MCP server: Node's fetch, Node's https module,
        # and Playwright's own request client.
        code = """async (page) => {
  const out = [];
  const tryIt = async (label, fn) => { try { out.push(label + ' OPEN ' + await fn()); } catch (e) { out.push(label + ' shut ' + String(e && (e.cause && e.cause.code || e.message)).slice(0, 80)); } };
  await tryIt('fetch', async () => (await globalThis.fetch('https://github.com/')).status);
  await tryIt('https', () => new Promise((ok, bad) => { const req = process.mainModule.require('https').get('https://github.com/', r => ok(r.statusCode)); req.on('error', bad); req.setTimeout(8000, () => req.destroy(new Error('timeout'))); }));
  await tryIt('page.request', async () => { const r = await page.request.get('https://github.com/', { timeout: 8000 }); if (!r.ok()) throw new Error('HTTP ' + r.status()); return r.status(); });
  return out.join(' | ');
}"""
        props = tools["browser_run_code_unsafe"]["inputSchema"].get("properties", {})
        key = "code" if "code" in props else next(iter(props))
        text, _, _ = call("browser_run_code_unsafe", {key: code})
        result = text.split("### Ran Playwright code")[0]
        report["browser_server_escape"] = "reachable" if " OPEN " in result else "blocked"
        report["browser_server_escape_detail"] = result.strip()[:400]
except Exception as e:
    report["browser_error"] = repr(e)

os.makedirs("/logs/artifacts", exist_ok=True)
open("/logs/artifacts/answer.txt", "w").write("probe\n")
os.makedirs("/logs/agent", exist_ok=True)
json.dump(report, open("/logs/agent/probe.json", "w"), indent=1)
print(json.dumps(report, indent=1))

problems = []
if hits or report["tests_dir_exists"] or report["solution_dir_exists"]:
    problems.append("answer material on the agent's disk")
for k in ("weave_server_direct", "github", "raw_githubusercontent"):
    if report[k].startswith("reachable"):
        problems.append(k + " is reachable")
if not report.get("browser_weave_page"):
    problems.append("browser could not open the Weave")
if report.get("browser_real_web") == "reachable" or report.get("browser_server_escape") == "reachable":
    problems.append("browser can reach the real internet")
print("PROBE", "FAILED: " + "; ".join(problems) if problems else "OK")
raise SystemExit(1 if problems else 0)
'''


class ProbeAgent(BaseAgent):
    @staticmethod
    def name() -> str:
        return "websim-probe"

    def version(self) -> str:
        return "1.0.0"

    async def setup(self, environment: BaseEnvironment) -> None:
        return

    async def run(self, instruction: str, environment: BaseEnvironment, context: AgentContext) -> None:
        result = await environment.exec(command="python3 -c " + shlex.quote(PROBE), timeout_sec=300)
        (self.logs_dir / "probe.txt").write_text((result.stdout or "") + (result.stderr or ""))
        if result.return_code != 0:
            raise RuntimeError("sandbox probe failed:\n" + (result.stdout or "")[-3000:] + (result.stderr or "")[-2000:])
        context.metadata = {"probe": json.loads((result.stdout or "").rsplit("PROBE", 1)[0])}
