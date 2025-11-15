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
