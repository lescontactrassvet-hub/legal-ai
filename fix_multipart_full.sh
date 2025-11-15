#!/bin/bash
set -e

echo "=== FIX MULTIPART DEPENDENCY (FULL AUTO) ==="

# 1. Ищем все requirements.txt
REQ_FILES=$(find . -type f -name "requirements.txt")

echo "[+] Requirements found:"
echo "$REQ_FILES"
echo

# 2. Добавляем python-multipart в каждый requirements.txt
for f in $REQ_FILES; do
    if grep -q "python-multipart" "$f"; then
        echo "[i] python-multipart already exists in $f"
    else
        echo "[+] Adding python-multipart to $f"
        echo "python-multipart>=0.0.9" >> "$f"
    fi
done

# 3. Проверяем backend/requirements.txt
echo
echo "---- backend/requirements.txt CONTENT ----"
cat backend/requirements.txt
echo "------------------------------------------"
echo

# 4. Проверяем pip установку локально
echo "[+] Testing pip installation..."
python3 -m pip install -r backend/requirements.txt || {
    echo "[!] Pip install failed!"
    exit 1
}

# 5. Git commit & push
echo "[+] Adding to git..."
git add -A

echo "[+] Commit..."
git commit -m "Add python-multipart to all requirements"

echo "[+] Push..."
git push

echo "=== DONE ==="
echo "Теперь открой GitHub → Actions → Backend tests"
