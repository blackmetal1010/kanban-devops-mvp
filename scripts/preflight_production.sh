#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[preflight] Falta archivo .env en $ROOT_DIR"
  exit 1
fi

required_vars=(
  POSTGRES_DB
  POSTGRES_USER
  POSTGRES_PASSWORD
  DATABASE_URL
  REDIS_URL
  JWT_SECRET
  GRAFANA_ADMIN_USER
  GRAFANA_ADMIN_PASSWORD
)

for key in "${required_vars[@]}"; do
  if ! grep -qE "^${key}=" "$ENV_FILE"; then
    echo "[preflight] Variable requerida no definida: $key"
    exit 1
  fi
done

if grep -qE '^APP_ENV=prod$' "$ENV_FILE"; then
  echo "[preflight] APP_ENV=prod OK"
else
  echo "[preflight] APP_ENV debe ser prod para despliegue final"
  exit 1
fi

if grep -qE 'change_me|KanbanLocalStrong_2026|KanbanJwtSecretOnlyLocal_2026|GrafanaStrongLocal_2026' "$ENV_FILE"; then
  echo "[preflight] Detectados valores de ejemplo/dev en .env. Sustituyelos antes de desplegar"
  exit 1
fi

echo "[preflight] Validando compose de produccion"
cd "$ROOT_DIR"
docker compose -f docker-compose.yml -f docker-compose.prod.yml config >/dev/null

echo "[preflight] OK"
