#!/usr/bin/env bash
set -euo pipefail

CRON_FILE="/etc/cron.d/legalai_laws_sync"
BACKEND_ROOT="/srv/legal-ai/backend"
LOG_DIR="/srv/legal-ai/logs"

mkdir -p "${LOG_DIR}"

cat > "${CRON_FILE}" << EOF
0 2 * * * root cd ${BACKEND_ROOT} && . .venv/bin/activate && python3 -m app.laws.sync >> ${LOG_DIR}/laws_sync.log 2>&1
EOF

chmod 644 "${CRON_FILE}"

if command -v systemctl >/dev/null 2>&1; then
  systemctl restart cron || true
else
  service cron restart || true
fi
