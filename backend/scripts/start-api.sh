#!/bin/sh
set -eu

echo "[start-api] Checking database migration state..."
DB_STATE=$(python - <<'PY'
from sqlalchemy import create_engine, inspect
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
with engine.connect() as conn:
    tables = set(inspect(conn).get_table_names())

has_alembic = "alembic_version" in tables
has_app_tables = bool(tables.intersection({"users", "projects", "project_members", "tasks", "comments"}))

if has_app_tables and not has_alembic:
    print("STAMP")
else:
    print("UPGRADE")
PY
)

if [ "$DB_STATE" = "STAMP" ]; then
  echo "[start-api] Existing schema detected without alembic_version. Stamping head..."
  alembic stamp head
fi

echo "[start-api] Running alembic upgrade head..."
alembic upgrade head

echo "[start-api] Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
