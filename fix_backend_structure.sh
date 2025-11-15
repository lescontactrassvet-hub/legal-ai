#!/bin/bash
set -e

echo "=== CLEANING WRONG backend/legal-ai FOLDER ==="

# 1. Удаляем вложенную неверную структуру
if [ -d backend/legal-ai ]; then
    echo "[+] Removing nested backend/legal-ai"
    rm -rf backend/legal-ai
else
    echo "[i] No nested backend/legal-ai folder found"
fi

# 2. Исправляем настоящий requirements.txt
REQ="backend/requirements.txt"

if ! grep -q "python-multipart" "$REQ"; then
    echo "[+] Adding python-multipart to backend/requirements.txt"
    echo "python-multipart>=0.0.9" >> "$REQ"
else
    echo "[i] python-multipart already in backend/requirements.txt"
fi

echo "------ backend/requirements.txt ------"
cat "$REQ"
echo "--------------------------------------"

# 3. Коммит
git add -A
git commit -m "Fix backend structure and requirements" || echo "[i] Nothing to commit"

# 4. Пуш
git push

echo "=== DONE ==="
echo "Теперь смотри GitHub → Actions → Backend tests"
