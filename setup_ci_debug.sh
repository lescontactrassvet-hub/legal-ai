#!/bin/bash
set -e

echo "=== STEP 1: create CI debug script ==="

cat > ci_debug_python_multipart.sh << 'DEBUGEOF'
#!/bin/bash
set -e

echo "=== CI BACKEND DEBUG: python-multipart & env ==="
echo

echo "[1] PWD:"
pwd
echo

echo "[2] Files in repo root:"
ls
echo

echo "[3] backend directory:"
if [ -d backend ]; then
  ls backend
else
  echo "backend/ NOT FOUND"
fi
echo

echo "[4] backend/requirements.txt:"
if [ -f backend/requirements.txt ]; then
  echo "---- backend/requirements.txt ----"
  cat backend/requirements.txt
  echo "----------------------------------"
else
  echo "backend/requirements.txt NOT FOUND"
fi
echo

echo "[5] pip list | grep multipart:"
python -m pip list | grep -i multipart || echo "no multipart packages installed"
echo

echo "[6] pip show python-multipart:"
if python -m pip show python-multipart >/dev/null 2>&1; then
  python -m pip show python-multipart
else
  echo "python-multipart is NOT installed (pip show failed)"
fi
echo

echo "[7] PYTHONPATH and sys.path:"
echo "PYTHONPATH: $PYTHONPATH"
python - << 'PYCODE'
import sys
print("sys.path:")
for p in sys.path:
    print("  ", p)
PYCODE

echo
echo "=== END CI BACKEND DEBUG ==="
DEBUGEOF

chmod +x ci_debug_python_multipart.sh
echo "[+] Created ci_debug_python_multipart.sh"

echo
echo "=== STEP 2: patch backend-tests.yml ==="

WF=".github/workflows/backend-tests.yml"

if [ ! -f "$WF" ]; then
  echo "[!] $WF not found. Available workflows:"
  ls .github/workflows || true
  echo "[!] Cannot patch workflow automatically."
  exit 1
fi

cp "$WF" "${WF}.bak"
echo "[+] Backup created: ${WF}.bak"

# Вставляем шаг Debug перед шагом Run tests (первым)
awk '
  /- name: Run tests/ && !inserted {
    print "      - name: Debug python-multipart";
    print "        run: |";
    print "          bash ./ci_debug_python_multipart.sh";
    print "";
    inserted=1;
  }
  { print }
' "$WF" > "${WF}.tmp"

mv "${WF}.tmp" "$WF"
echo "[+] Patched $WF (added Debug step before Run tests)"

echo
echo "=== STEP 3: git commit & push ==="

git add ci_debug_python_multipart.sh "$WF"
git commit -m "Add CI debug for python-multipart" || echo "[i] Nothing to commit"
git push

echo
echo "=== DONE ==="
echo "Теперь зайди в GitHub → Actions → Backend tests и в новом прогоне"
echo "посмотри шаг \"Debug python-multipart\" — там будет полный отчёт."
