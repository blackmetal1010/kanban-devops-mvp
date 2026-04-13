#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

./scripts/preflight_production.sh
./scripts/backup_postgres.sh

docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
./scripts/smoke_check.sh

KEEP_COUNT="${KEEP_COUNT:-14}" ./scripts/backup_retention.sh

echo "[deploy] Despliegue de produccion completado"
