#!/bin/sh
# Start Playwright MCP for one eval trial.
#
# The MCP server lets its client run arbitrary code (browser_run_code_unsafe), so this
# container must not be a way out to the real internet. While still root, drop the default
# route: only the directly attached compose networks (the agent and the Weave) stay
# reachable. Then drop to an unprivileged user, which also drops NET_ADMIN, so the route
# cannot be put back.
#
# BROWSER_MODE
#   vision  screenshots and x,y mouse actions (computer use), no page snapshots
#   hybrid  screenshots and x,y mouse actions, plus accessibility snapshots
#   dom     accessibility snapshots only
set -eu

if [ "$(id -u)" = 0 ]; then
  if ip route show default | grep -q .; then
    ip route del default || { echo "weave-browser: could not remove the default route (needs cap_add NET_ADMIN)" >&2; exit 1; }
  fi
  HOME=/home/pwuser exec setpriv --reuid=pwuser --regid=pwuser --init-groups --inh-caps=-all --bounding-set=-all "$0" "$@"
fi

case "${BROWSER_MODE:-vision}" in
  vision) MODE_ARGS="--caps vision --snapshot-mode none" ;;
  hybrid) MODE_ARGS="--caps vision" ;;
  dom) MODE_ARGS="" ;;
  *) echo "weave-browser: unknown BROWSER_MODE ${BROWSER_MODE}" >&2; exit 2 ;;
esac

cd /tmp
export NODE_OPTIONS="${NODE_OPTIONS:-} --require /usr/local/lib/weave-keepalive.cjs"
# shellcheck disable=SC2086
exec playwright-mcp \
  --host 0.0.0.0 --port 8931 --allowed-hosts '*' \
  --headless --isolated --no-sandbox \
  --executable-path /usr/local/bin/weave-chromium \
  --proxy-server "${WEAVE_PROXY:-http://weave:8080}" \
  --viewport-size "${BROWSER_VIEWPORT:-1280x900}" \
  --output-dir /tmp/playwright-mcp \
  $MODE_ARGS "$@"
