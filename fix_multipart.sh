#!/bin/bash
set -e

echo "=== Fix missing python-multipart dependency ==="

REQ="backend/requirements.txt"

if ! grep -q "python-multipart" "$REQ"; then
    echo "[+] Adding python-multipart to requirements.txt"
    echo "python-multipart>=0.0.9" >> "$REQ"
else
    echo "[i] python-multipart already present"
fi

git add "$REQ"
git commit -m "Add python-multipart for FastAPI form-data handling" || echo "[i] Nothing to commit"
git push

echo "=== DONE ==="
echo "Теперь открой GitHub → Actions → Backend tests и посмотри результат."
