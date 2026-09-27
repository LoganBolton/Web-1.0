// Node's HTTP server drops idle keep-alive connections after 5 seconds. Codex's MCP client
// keeps pooled connections much longer and reuses them, so every tool call made after a
// pause of more than 5 seconds (for example while the model is thinking) would fail with
// "error sending request". Keep idle connections open for 10 minutes instead.
const http = require('http');
const listen = http.Server.prototype.listen;
http.Server.prototype.listen = function (...args) {
  this.keepAliveTimeout = 600000;
  this.headersTimeout = 601000;
  return listen.apply(this, args);
};
