#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="$ROOT_DIR/backups/manual"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILE="$BACKUP_DIR/postgres_${TIMESTAMP}.sql"

mkdir -p "$BACKUP_DIR"

cd "$ROOT_DIR"

echo "[backup] Generando backup PostgreSQL en $BACKUP_FILE"
docker compose exec -T db sh -lc 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > "$BACKUP_FILE"

echo "[backup] Backup completado: $BACKUP_FILE"
