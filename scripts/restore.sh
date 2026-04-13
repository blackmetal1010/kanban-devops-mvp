#!/usr/bin/env bash
# Restore PostgreSQL from a backup archive.
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"

# Load env if available
[ -f .env ] && set -a && . .env && set +a

if [ -z "${1:-}" ]; then
  echo "Usage: $0 <backup_file.tar.gz>"
  echo ""
  echo "Available backups:"
  ls -lh "${BACKUP_DIR}"/kanban_backup_*.tar.gz 2>/dev/null || echo "  (none found)"
  exit 1
fi

BACKUP_FILE="$1"
if [ ! -f "${BACKUP_FILE}" ]; then
  BACKUP_FILE="${BACKUP_DIR}/${BACKUP_FILE}"
fi
if [ ! -f "${BACKUP_FILE}" ]; then
  echo "Error: backup file not found: ${BACKUP_FILE}"
  exit 1
fi

EXTRACT_DIR=$(mktemp -d)
trap 'rm -rf "${EXTRACT_DIR}"' EXIT

echo "[restore] Extracting ${BACKUP_FILE}..."
tar -xzf "${BACKUP_FILE}" -C "${EXTRACT_DIR}"

SQL_FILE=$(find "${EXTRACT_DIR}" -name "*.sql" | head -1)
RDB_FILE=$(find "${EXTRACT_DIR}" -name "*.rdb" | head -1 || true)

if [ -z "${SQL_FILE}" ]; then
  echo "Error: no .sql file found in backup."
  exit 1
fi

echo "[restore] WARNING: This will overwrite the current database!"
read -r -p "Continue? (yes/no): " CONFIRM
if [ "${CONFIRM}" != "yes" ]; then
  echo "[restore] Aborted."
  exit 0
fi

# ── Restore PostgreSQL ───────────────────────────────────────────────────────
echo "[restore] Restoring PostgreSQL from ${SQL_FILE}..."
docker compose exec -T db psql \
  -U "${POSTGRES_USER:-kanban_user}" \
  -c "DROP DATABASE IF EXISTS ${POSTGRES_DB:-kanban_db};"
docker compose exec -T db psql \
  -U "${POSTGRES_USER:-kanban_user}" \
  -c "CREATE DATABASE ${POSTGRES_DB:-kanban_db};"
docker compose exec -T db psql \
  -U "${POSTGRES_USER:-kanban_user}" \
  "${POSTGRES_DB:-kanban_db}" < "${SQL_FILE}"
echo "[restore] PostgreSQL restored."

# ── Restore Redis (optional) ──────────────────────────────────────────────────
if [ -n "${RDB_FILE}" ]; then
  echo "[restore] Restoring Redis from ${RDB_FILE}..."
  docker compose stop redis
  docker compose cp "${RDB_FILE}" redis:/data/dump.rdb
  docker compose start redis
  echo "[restore] Redis restored."
fi

echo "[restore] Restore complete."
