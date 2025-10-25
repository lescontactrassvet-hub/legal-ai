#!/usr/bin/env bash
# Backup script for LegalAI
set -e
STAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p /opt/legal-ai/backups/$STAMP
cp -a /opt/legal-ai/app/.env /opt/legal-ai/backups/$STAMP/
cp -a /opt/legal-ai/app/backend /opt/legal-ai/backups/$STAMP/
cp -a /opt/legal-ai/app/legalai.db /opt/legal-ai/backups/$STAMP/ || true
echo "Backup completed at $STAMP"
