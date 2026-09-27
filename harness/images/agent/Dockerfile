# The agent's own machine. Codex is preinstalled so the trial needs no package downloads,
# and nothing from this repository is copied in: there are no questions or answers here.
ARG NODE_IMAGE=node:22-bookworm-slim
FROM ${NODE_IMAGE}
ARG CODEX_VERSION=0.157.1
RUN apt-get update && apt-get install -y --no-install-recommends bash curl ca-certificates ripgrep python3 git \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g @openai/codex@${CODEX_VERSION} && rm -rf /root/.npm \
    && codex --version \
    && mkdir -p /logs/artifacts /workspace
WORKDIR /workspace
