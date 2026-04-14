#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"

wait_for_url() {
  local label="$1"
  local url="$2"
  local attempts="${3:-20}"
  local delay="${4:-2}"

  echo "[smoke] Validando ${label}"
  for _ in $(seq 1 "$attempts"); do
    if curl -fsS --max-time 5 "$url" >/dev/null; then
      return 0
    fi
    sleep "$delay"
  done

  echo "[smoke] Fallo validando ${label}: ${url}"
  return 1
}

for svc in api db redis frontend prometheus grafana; do
  if ! docker compose ps --status running "$svc" | grep -q "$svc"; then
    echo "[smoke] Servicio no esta running: $svc"
    exit 1
  fi
done

wait_for_url "API health" "$API_URL/health" 30 2
wait_for_url "API version" "$API_URL/version"
wait_for_url "OpenAPI" "$API_URL/docs"
wait_for_url "metricas" "$API_URL/metrics"

echo "[smoke] OK"
