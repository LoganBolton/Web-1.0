# The agent's browser. Playwright MCP driving headless Chromium, served over HTTP so the
# agent container can reach it. All browser traffic goes through the Weave server as a proxy.
# The official Playwright image already has Chromium and its system libraries.
ARG PLAYWRIGHT_IMAGE=mcr.microsoft.com/playwright:v1.63.0-noble
FROM ${PLAYWRIGHT_IMAGE}
ARG PLAYWRIGHT_MCP_VERSION=0.0.82
RUN apt-get update && apt-get install -y --no-install-recommends iproute2 util-linux \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g @playwright/mcp@${PLAYWRIGHT_MCP_VERSION} && rm -rf /root/.npm \
    && ln -s "$(ls -d /ms-playwright/chromium-*/chrome-linux*/chrome | head -1)" /usr/local/bin/weave-chromium \
    && /usr/local/bin/weave-chromium --headless --no-sandbox --version
COPY --chmod=755 entrypoint.sh /usr/local/bin/weave-browser
COPY keepalive.cjs /usr/local/lib/weave-keepalive.cjs
EXPOSE 8931
HEALTHCHECK --interval=2s --timeout=5s --retries=30 CMD node -e "require('net').connect(8931,'127.0.0.1').on('connect',()=>process.exit(0)).on('error',()=>process.exit(1))"
ENTRYPOINT ["/usr/local/bin/weave-browser"]
