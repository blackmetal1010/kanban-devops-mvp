#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KEEP_COUNT="${KEEP_COUNT:-14}"

prune_dir() {
  local dir="$1"
  [[ -d "$dir" ]] || return 0
  mapfile -t files < <(ls -1t "$dir"/*.sql 2>/dev/null || true)
  local total="${#files[@]}"
  if (( total <= KEEP_COUNT )); then
    echo "[retention] $dir: $total backups, sin cambios"
    return 0
  fi

  for ((i=KEEP_COUNT; i<total; i++)); do
    rm -f "${files[$i]}"
  done
  echo "[retention] $dir: conservados $KEEP_COUNT, eliminados $((total - KEEP_COUNT))"
}

prune_dir "$ROOT_DIR/backups/manual"
prune_dir "$ROOT_DIR/backups/deploy"
