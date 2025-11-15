#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$HOME/legal-ai"
BUNDLE_NAME="legalai_migration_bundle_$(date +%Y%m%d_%H%M%S)"
BUNDLE_DIR="$HOME/${BUNDLE_NAME}"
ARCHIVE_PATH="$HOME/${BUNDLE_NAME}.tar.gz"

echo "==> Создание папки бандла..."
mkdir -p "$BUNDLE_DIR"

echo "==> Копирование основных данных..."
rsync -a --delete \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude 'node_modules' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  "${PROJECT_DIR}/" "${BUNDLE_DIR}/code/"

echo "==> Копирование баз данных (если есть)..."
mkdir -p "$BUNDLE_DIR/db_dumps"
find "$PROJECT_DIR" -name "*.db" -exec cp {} "$BUNDLE_DIR/db_dumps/" \;

echo "==> Создание архива..."
cd "$HOME"
tar -czf "$ARCHIVE_PATH" "$(basename "$BUNDLE_DIR")"

echo "✅ Готово. Архив: $ARCHIVE_PATH"


