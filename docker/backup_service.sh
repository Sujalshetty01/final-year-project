#!/bin/bash
# Entrypoint for backup service container
set -euo pipefail

while true; do
  /app/scripts/backup_db.sh
  echo "[INFO] Sleeping for 24h before next backup..."
  sleep 86400 # 24 hours
fi
