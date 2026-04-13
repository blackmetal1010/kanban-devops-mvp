#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"

for svc in api db redis frontend prometheus grafana; do
  if ! docker compose ps --status running "$svc" | grep -q "$svc"; then
    echo "[smoke] Servicio no esta running: $svc"
    exit 1
  fi
done

echo "[smoke] Validando API health"
curl -fsS "$API_URL/health" >/dev/null

echo "[smoke] Validando API version"
curl -fsS "$API_URL/version" >/dev/null

echo "[smoke] Validando OpenAPI"
curl -fsS "$API_URL/docs" >/dev/null

echo "[smoke] Validando metricas"
curl -fsS "$API_URL/metrics" >/dev/null

echo "[smoke] OK"
