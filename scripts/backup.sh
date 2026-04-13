#!/usr/bin/env bash
# Backup PostgreSQL + Redis data, compress, and rotate old backups (keep 7 days).
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="kanban_backup_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"
KEEP_DAYS=7

# Load env if available
[ -f .env ] && set -a && . .env && set +a

mkdir -p "${BACKUP_DIR}"

echo "[backup] Starting backup: ${BACKUP_NAME}"

# ── PostgreSQL dump ──────────────────────────────────────────────────────────
echo "[backup] Dumping PostgreSQL..."
docker compose exec -T db pg_dump \
  -U "${POSTGRES_USER:-kanban_user}" \
  "${POSTGRES_DB:-kanban_db}" \
  > "${BACKUP_PATH}.sql"

echo "[backup] PostgreSQL dump: $(du -sh "${BACKUP_PATH}.sql" | cut -f1)"

# ── Redis snapshot ───────────────────────────────────────────────────────────
echo "[backup] Saving Redis snapshot..."
docker compose exec -T redis redis-cli BGSAVE
sleep 2
docker compose cp redis:/data/dump.rdb "${BACKUP_PATH}.rdb" 2>/dev/null || echo "[backup] Redis dump.rdb not found, skipping."

# ── Compress ─────────────────────────────────────────────────────────────────
echo "[backup] Compressing..."
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" \
  -C "${BACKUP_DIR}" \
  "${BACKUP_NAME}.sql" \
  $([ -f "${BACKUP_PATH}.rdb" ] && echo "${BACKUP_NAME}.rdb" || true)

# Clean up uncompressed files
rm -f "${BACKUP_PATH}.sql" "${BACKUP_PATH}.rdb"

echo "[backup] Backup saved: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo "[backup] Size: $(du -sh "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)"

# ── Rotate old backups ────────────────────────────────────────────────────────
echo "[backup] Removing backups older than ${KEEP_DAYS} days..."
find "${BACKUP_DIR}" -name "kanban_backup_*.tar.gz" -mtime +${KEEP_DAYS} -delete

REMAINING=$(find "${BACKUP_DIR}" -name "kanban_backup_*.tar.gz" | wc -l)
echo "[backup] Done. ${REMAINING} backup(s) retained."
echo "${BACKUP_NAME}.tar.gz"
