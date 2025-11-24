#!/usr/bin/env bash
# Скрипт настройки cron-дей для обновления законов.
# Запускается НА СЕРВЕРЕ (через deploy.yml), а не из Termux.

set -euo pipefail

CRON_FILE="/etc/cron.d/legalai_laws_sync"
BACKEND_DIR="/srv/legal-ai/backend"
PYTHON_BIN="${BACKEND_DIR}/.venv/bin/python"
LOG_DIR="/srv/legal-ai/logs"

# Создаём директорию для логов, если её ещё нет
mkdir -p "${LOG_DIR}"

# Обновляем cron-файл
cat > "${CRON_FILE}" <<EOF
# Автоматическое обновление законов для LegalAI
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# 1) Ежедневно в 03:00 — синхронизация списка актов из RSS pravo.gov.ru
0 3 * * * root cd ${BACKEND_DIR} && ${PYTHON_BIN} -m app.laws.sync >> ${LOG_DIR}/laws_sync.log 2>&1

# 2) Ежедневно в 04:00 — дозагрузка полного текста для актов без full_text
0 4 * * * root cd ${BACKEND_DIR} && ${PYTHON_BIN} -m app.laws.fetch_full_text >> ${LOG_DIR}/laws_full_text.log 2>&1
EOF

# Права и владелец
chmod 644 "${CRON_FILE}"
chown root:root "${CRON_FILE}"

echo "Cron file ${CRON_FILE} updated for LegalAI laws sync."
