#!/usr/bin/env bash
# Health check — verify all Kanban services are running and responsive.
set -euo pipefail

PASS=0
FAIL=0

check() {
  local name="$1"
  local result="$2"
  if [ "${result}" = "ok" ]; then
    echo "  ✅ ${name}"
    PASS=$((PASS + 1))
  else
    echo "  ❌ ${name}: ${result}"
    FAIL=$((FAIL + 1))
  fi
}

echo "══════════════════════════════════════"
echo "  Kanban DevOps MVP — Health Check"
echo "══════════════════════════════════════"

# ── Docker containers ─────────────────────────────────────────────────────────
echo ""
echo "Docker containers:"
for service in db redis backend frontend; do
  STATUS=$(docker compose ps --format json 2>/dev/null \
    | python3 -c "import sys,json; [print(c.get('State','unknown')) for c in [json.loads(l) for l in sys.stdin] if '${service}' in c.get('Service','')]" 2>/dev/null | head -1 || echo "unknown")
  if [ "${STATUS}" = "running" ]; then
    check "${service}" "ok"
  else
    check "${service}" "container state: ${STATUS:-not found}"
  fi
done

# ── API endpoints ─────────────────────────────────────────────────────────────
echo ""
echo "API endpoints:"

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://localhost/health 2>/dev/null || echo "000")
if [ "${HTTP_CODE}" = "200" ]; then
  check "GET /health" "ok"
else
  check "GET /health" "HTTP ${HTTP_CODE}"
fi

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://localhost/api/docs 2>/dev/null || echo "000")
if [ "${HTTP_CODE}" = "200" ]; then
  check "GET /api/docs" "ok"
else
  check "GET /api/docs" "HTTP ${HTTP_CODE}"
fi

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://localhost/metrics 2>/dev/null || echo "000")
if [ "${HTTP_CODE}" = "200" ]; then
  check "GET /metrics" "ok"
else
  check "GET /metrics" "HTTP ${HTTP_CODE}"
fi

# ── Database ──────────────────────────────────────────────────────────────────
echo ""
echo "Database:"
DB_RESULT=$(docker compose exec -T db pg_isready \
  -U "${POSTGRES_USER:-kanban_user}" \
  -d "${POSTGRES_DB:-kanban_db}" 2>&1 || echo "failed")
if echo "${DB_RESULT}" | grep -q "accepting connections"; then
  check "PostgreSQL" "ok"
else
  check "PostgreSQL" "${DB_RESULT}"
fi

REDIS_RESULT=$(docker compose exec -T redis redis-cli ping 2>&1 || echo "failed")
if [ "${REDIS_RESULT}" = "PONG" ]; then
  check "Redis" "ok"
else
  check "Redis" "${REDIS_RESULT}"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════"
echo "  Passed: ${PASS}  Failed: ${FAIL}"
echo "══════════════════════════════════════"

if [ "${FAIL}" -gt 0 ]; then
  exit 1
fi
