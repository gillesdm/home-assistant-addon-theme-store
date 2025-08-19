#!/usr/bin/env bash
set -euo pipefail

LOG_LEVEL="${LOG_LEVEL:-info}"

log() {
    local level="$1"; shift
    echo "$(date --iso-8601=seconds) [${level}] $*"
}

# Read options from HA (if set)
if [[ -f /data/options.json ]]; then
    LV=$(jq -r '.log_level // empty' /data/options.json || true)
    if [[ -n "${LV:-}" ]]; then
        LOG_LEVEL="$LV"
    fi
fi

PORT=8080
log info "Theme Store add-on starting (log_level=${LOG_LEVEL}, port=${PORT})"

# Write a tiny Python HTTP server with a custom root response
cat > /usr/src/app/server.py << 'PY'
import http.server
import json
import os

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Quieter logs, align with add-on logs
        print(f"[http] {self.address_string()} - {format % args}")

    def do_GET(self):
        if self.path in ("/", "/healthz", "/readyz"):
            msg = "Theme Store add-on is running\n"
            if self.path == "/healthz":
                # simple health response
                self.send_response(204)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(msg.encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error":"not_found"}).encode("utf-8"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT","8080"))
    server = http.server.ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"[info] HTTP server listening on 0.0.0.0:{port}")
    server.serve_forever()
PY

exec python3 /usr/src/app/server.py
