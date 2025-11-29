#!/usr/bin/env bash
set -euo pipefail

echo "== LegalAI cleanup script =="

ROOT="/srv/legal-ai"
BACKUP_TAR="${ROOT}-backup-before-cleanup-$(date +%F-%H%M%S).tar.gz"

echo "[1/4] Creating full backup: ${BACKUP_TAR}"
tar czf "${BACKUP_TAR}" -C / srv/legal-ai

echo "[2/4] Removing runtime trash (__pycache__, *.pyc, *.pyo, logs, caches)..."

# Удаляем кэш и байткод
find "${ROOT}" -type d -name "__pycache__" -prune -exec rm -rf {} +
find "${ROOT}" -type d -name ".pytest_cache" -prune -exec rm -rf {} +
find "${ROOT}" -type d -name ".mypy_cache" -prune -exec rm -rf {} +
find "${ROOT}" -type d -name ".ruff_cache" -prune -exec rm -rf {} +
find "${ROOT}" -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete

# Логи и временные файлы
find "${ROOT}" -maxdepth 3 -type f \( \
  -name "*.log" -o \
  -name "uvicorn.out" -o \
  -name "*.tmp" \
\) -delete

echo "[3/4] Cleaning old DB backups (оставляем dev.db)..."
# Оставляем dev.db (боевую SQLite), чистим старые и мусорные БД
find "${ROOT}/backend" -maxdepth 2 -type f \( \
  -name "legalai.db" -o \
  -name "*.db.bak*" -o \
  -name "*_backup.db" -o \
  -name "*.db-shm" -o \
  -name "*.db-wal" \
\) -delete

echo "[4/4] Moving diagnostic scripts and reports to legacy_scripts/ ..."

LEGACY_DIR="${ROOT}/legacy_scripts"
mkdir -p "${LEGACY_DIR}/root" "${LEGACY_DIR}/backend"

# В корне репо
cd "${ROOT}"
mv -f \
  fix_*.sh \
  *_doctor.sh \
  *_diag.sh \
  run_*_debug.sh \
  *report_20*.txt \
  *report_20*.json \
  2>/dev/null || true

mv -f \
  fix_*.sh \
  *_doctor.sh \
  *_diag.sh \
  run_*_debug.sh \
  *report_20*.txt \
  *report_20*.json \
  "${LEGACY_DIR}/root" 2>/dev/null || true

# В backend
cd "${ROOT}/backend"
mv -f \
  fix_*.sh \
  *_doctor.sh \
  *_diag.sh \
  run_*_debug.sh \
  *report_20*.txt \
  *report_20*.json \
  uvicorn.out \
  requirements-termux*.txt \
  main_legalai_probe.py \
  dev.db.bak* \
  2>/dev/null || true

mv -f \
  fix_*.sh \
  *_doctor.sh \
  *_diag.sh \
  run_*_debug.sh \
  *report_20*.txt \
  *report_20*.json \
  uvicorn.out \
  requirements-termux*.txt \
  main_legalai_probe.py \
  dev.db.bak* \
  "${LEGACY_DIR}/backend" 2>/dev/null || true

echo "== Cleanup finished =="
echo "Backup saved to: ${BACKUP_TAR}"
echo "Legacy scripts and reports moved to: ${LEGACY_DIR}"
