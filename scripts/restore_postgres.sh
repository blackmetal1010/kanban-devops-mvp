#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Uso: ./scripts/restore_postgres.sh <ruta_backup.sql>"
  exit 1
fi

BACKUP_FILE="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -f "$BACKUP_FILE" ]]; then
  echo "[restore] Archivo no encontrado: $BACKUP_FILE"
  exit 1
fi

cd "$ROOT_DIR"

echo "[restore] Restaurando backup desde $BACKUP_FILE"
cat "$BACKUP_FILE" | docker compose exec -T db sh -lc 'psql -U "$POSTGRES_USER" "$POSTGRES_DB"'

echo "[restore] Restauracion completada"
