#!/bin/bash
set -e

echo "============================================="
echo "  LEGAL-AI FULL REPO DIAGNOSE & AUTO-FIXER   "
echo "============================================="
echo

# 1. Проверка что мы в корневом каталоге
echo "[1] Current directory: $(pwd)"

# 2. Проверка структуры
echo
echo "[2] Scanning repository structure..."
find . -maxdepth 3 -type d

# 3. Проверяем существование неправильного backend/legal-ai
echo
if [ -d backend/legal-ai ]; then
    echo "[!] WARNING: Found INVALID nested folder backend/legal-ai"
    echo "[+] Removing WRONG folder backend/legal-ai"
    rm -rf backend/legal-ai
else
    echo "[OK] No nested backend/legal-ai"
fi

# 4. Проверяем настоящий backend
echo
if [ -d backend ]; then
    echo "[OK] backend/ exists"
else
    echo "[FATAL] backend folder does not exist — cannot continue"
    exit 1
fi

# 5. Проверка requirements
REQ="backend/requirements.txt"
echo
if [ -f "$REQ" ]; then
    echo "[OK] backend/requirements.txt FOUND"
else
    echo "[FATAL] Missing backend/requirements.txt"
    exit 1
fi

echo
echo "---- backend/requirements.txt ----"
cat "$REQ"
echo "----------------------------------"
echo

# 6. Добавляем python-multipart если нужно
if ! grep -q "python-multipart" "$REQ"; then
    echo "[+] Adding python-multipart"
    echo "python-multipart>=0.0.9" >> "$REQ"
else
    echo "[OK] python-multipart already present"
fi

# 7. Создаём файл диагностики в корне
echo
echo "[7] Creating CI debug script..."

cat > ci_debug_python_multipart.sh << 'DEBUGEOF'
#!/bin/bash
set -e

echo "=== CI DEBUG REPORT ==="
echo "[A] PWD: $(pwd)"

echo "[B] List repo root:"
ls -la

echo "[C] backend folder:"
ls -la backend || echo 'NO backend folder'

echo "[D] backend/requirements.txt:"
cat backend/requirements.txt || echo 'requirements missing'

echo "[E] python-multipart:"
pip list | grep multipart || echo 'NO python-multipart'

echo "[F] PYTHONPATH:"
echo "$PYTHONPATH"

python - << 'PYEOF'
import sys
print("sys.path:")
for p in sys.path:
    print(" -", p)
PYEOF

echo "=== END REPORT ==="
DEBUGEOF

chmod +x ci_debug_python_multipart.sh
echo "[OK] Debug script created"

# 8. Патчим workflow
WF=".github/workflows/backend-tests.yml"
echo
echo "[8] Patching workflow: $WF"

if [ ! -f "$WF" ]; then
    echo "[FATAL] Workflow file not found: $WF"
    exit 1
fi

cp "$WF" "$WF.bak"

awk '
  /- name: Run tests/ && !inserted {
    print "      - name: Debug python-multipart";
    print "        run: |";
    print "          bash ./ci_debug_python_multipart.sh";
    print "";
    inserted=1;
  }
  { print }
' "$WF" > "$WF.tmp"

mv "$WF.tmp" "$WF"

echo "[OK] Workflow patched"

# 9. Git push
echo
echo "[9] Commit & push"

git add -A
git commit -m "Full repo auto-fix + CI debugging"
git push

echo
echo "============================================="
echo "   AUTO-FIX COMPLETE — CHECK GITHUB ACTIONS   "
echo "============================================="
