#!/usr/bin/env bash
set -euo pipefail

LOG_LEVEL="info"
API_PORT="8080"

if [[ -f /data/options.json ]]; then
  LV=$(jq -r '.log_level // empty' /data/options.json || true)
  [[ -n "${LV:-}" ]] && LOG_LEVEL="$LV"
  PT=$(jq -r '.api_port // empty' /data/options.json || true)
  [[ -n "${PT:-}" ]] && API_PORT="$PT"
fi

export LOG_LEVEL
export APP_VERSION="0.0.4"
export PORT="${API_PORT}"

echo "[info] Theme Store add-on starting (version=${APP_VERSION}, log_level=${LOG_LEVEL}, port=${API_PORT})"
echo "[debug] python: $(command -v python3); uvicorn: $(command -v uvicorn)"

exec uvicorn app.main:app --host 0.0.0.0 --port "${API_PORT}" --access-log
