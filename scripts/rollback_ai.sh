#!/usr/bin/env bash
# Rollback script for LegalAI
set -e
LAST=$(ls -1 /opt/legal-ai/backups | sort | tail -n 1)
cp -a /opt/legal-ai/backups/$LAST/.env /opt/legal-ai/app/.env
rm -rf /opt/legal-ai/app/backend
cp -a /opt/legal-ai/backups/$LAST/backend /opt/legal-ai/app/backend
cp -a /opt/legal-ai/backups/$LAST/legalai.db /opt/legal-ai/app/legalai.db || true
systemctl restart legalai
echo "Rollback to backup $LAST completed"
