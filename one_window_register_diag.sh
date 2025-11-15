#!/usr/bin/env bash
set -euo pipefail

cd ~/legal-ai
source .venv/bin/activate
export PYTHONPATH=$PWD/backend

LOG=~/legal-ai/uvicorn_debug.log
PIDFILE=~/legal-ai/uvicorn.pid

echo "==[0] Останавливаю старые uvicorn =="
pkill -f uvicorn || true

echo "==[1] Стартую uvicorn с DEBUG-логами (в фоне) =="
cd backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug > "$LOG" 2>&1 & echo $! > "$PIDFILE"
sleep 2

echo "==[2] Проверка процесса и первых логов =="
echo "PID:" $(cat "$PIDFILE" 2>/dev/null || echo "нет")
pgrep -fa uvicorn || true
echo "--- tail -n 30 $LOG ---"; tail -n 30 "$LOG" || true

echo "==[3] /health =="
curl -sS -D - -o /dev/null http://127.0.0.1:8000/health || true

echo "==[4] /auth/register (новые email/phone) =="
curl -sS -i -H "Content-Type: application/json" \
  -d '{"email":"test4@example.com","phone":"+79991112245","password":"MySecurePass123"}' \
  http://127.0.0.1:8000/auth/register || true
echo

sleep 1
echo "==[5] Хвост лога после запроса =="
echo "--- tail -n 120 $LOG ---"; tail -n 120 "$LOG" || true

echo "==[6] Статус процесса после запроса =="
pgrep -fa uvicorn || true
