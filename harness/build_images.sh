#!/usr/bin/env bash
# Build the three shared images every WebSim eval task uses.
#
#   websim-weave    the Weave server (built from this repo's source)
#   websim-browser  Playwright MCP + Chromium, the agent's only way onto the Weave
#   websim-agent    the agent's machine, with Codex preinstalled and no repo files
#
# If Docker Hub rate-limits you, point the base images at a mirror:
#   PYTHON_IMAGE=mirror.gcr.io/library/python:3.12-slim NODE_IMAGE=mirror.gcr.io/library/node:22-bookworm-slim bash harness/build_images.sh
set -euo pipefail
cd "$(dirname "$0")/.."

PYTHON_IMAGE="${PYTHON_IMAGE:-python:3.12-slim}"
NODE_IMAGE="${NODE_IMAGE:-node:22-bookworm-slim}"
PLAYWRIGHT_IMAGE="${PLAYWRIGHT_IMAGE:-mcr.microsoft.com/playwright:v1.63.0-noble}"
CODEX_VERSION="${CODEX_VERSION:-0.157.1}"
PLAYWRIGHT_MCP_VERSION="${PLAYWRIGHT_MCP_VERSION:-0.0.82}"

docker build -f harness/images/weave/Dockerfile --build-arg PYTHON_IMAGE="$PYTHON_IMAGE" -t websim-weave:latest .
docker build --build-arg PLAYWRIGHT_IMAGE="$PLAYWRIGHT_IMAGE" --build-arg PLAYWRIGHT_MCP_VERSION="$PLAYWRIGHT_MCP_VERSION" \
  -t websim-browser:latest harness/images/browser
docker build --build-arg NODE_IMAGE="$NODE_IMAGE" --build-arg CODEX_VERSION="$CODEX_VERSION" \
  -t websim-agent:latest harness/images/agent
# Each task's grader image starts FROM python:3.12-slim, so make sure it is available locally.
if ! docker image inspect python:3.12-slim >/dev/null 2>&1; then
  docker pull "$PYTHON_IMAGE"
  if [ "$PYTHON_IMAGE" != python:3.12-slim ]; then docker tag "$PYTHON_IMAGE" python:3.12-slim; fi
fi
echo "built websim-weave, websim-browser, websim-agent"
