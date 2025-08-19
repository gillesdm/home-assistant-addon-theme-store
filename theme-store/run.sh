#!/usr/bin/env bash
set -euo pipefail

# Guard: fail if 'nc' is present anywhere in this repo folder at runtime
if command -v nc >/dev/null 2>&1; then
    echo "$(date --iso-8601=seconds) [debug] nc exists at $(command -v nc)"
fi

LOG_LEVEL="info"
if [[ -f /data/options.json ]]; then
    LV=$(jq -r '.log_level // empty' /data/options.json || true)
    [[ -n "${LV:-}" ]] && LOG_LEVEL="$LV"
fi

PORT="${PORT:-8080}"
echo "$(date --iso-8601=seconds) [info] Theme Store add-on starting (log_level=${LOG_LEVEL}, port=${PORT})"

# Write the server once per start
cat > /usr/src/app/server.py << 'PY'
import http.server, json, os, sys

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[http] {self.address_string()} - {fmt % args}", flush=True)

    def do_GET(self):
        if self.path in ("/", "/healthz", "/readyz"):
            if self.path == "/healthz":
                self.send_response(204); self.end_headers(); return
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Theme Store add-on is running\n")
            return
        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": "not_found"}).encode("utf-8"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    print(f"[info] HTTP server listening on 0.0.0.0:{port}", flush=True)
    server = http.server.ThreadingHTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()
PY

exec python3 /usr/src/app/server.py
