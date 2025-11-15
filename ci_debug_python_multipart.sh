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
