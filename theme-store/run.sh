#!/usr/bin/env bash
set -euo pipefail

LOG_LEVEL="${LOG_LEVEL:-info}"

log() {
    local level="$1"; shift
    # Basic leveled logging
    echo "$(date --iso-8601=seconds) [${level}] $*"
}

# Apply HA options via /data/options.json if present
if [[ -f /data/options.json ]]; then
    # Extract log_level from HA options (fallback to env or default)
    LV=$(jq -r '.log_level // empty' /data/options.json || true)
    if [[ -n "${LV:-}" ]]; then
        LOG_LEVEL="$LV"
    fi
fi

log info "Theme Store add-on starting (log_level=${LOG_LEVEL})"

# Simple HTTP server with netcat (busybox nc). Responds to GET /
# This keeps the container alive and provides a health check endpoint.
PORT=8080
log info "Starting simple HTTP server on 0.0.0.0:${PORT}"
while true; do
    # shellcheck disable=SC2016
    printf 'HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nTheme Store add-on is running\n' | nc -l -p "${PORT}" -s 0.0.0.0 -q 1 || true
done
