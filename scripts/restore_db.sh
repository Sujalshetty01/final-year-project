#!/bin/bash
# Automated PostgreSQL database restore script
# Usage: ./scripts/restore_db.sh <backup_file.sql.gz>

set -euo pipefail

# Load environment variables (edit as needed)
DB_HOST="${POSTGRES_HOST:-db}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-malware_db}"
DB_USER="${POSTGRES_USER:-malware_user}"
DB_PASSWORD="${POSTGRES_PASSWORD:-malware_pass}"

BACKUP_FILE="${1:-}"

if [[ -z "$BACKUP_FILE" ]]; then
  echo "[ERROR] Usage: $0 <backup_file.sql.gz>" >&2
  exit 1
fi

if [[ ! -f "$BACKUP_FILE" ]]; then
  echo "[ERROR] Backup file not found: $BACKUP_FILE" >&2
  exit 2
fi

# Check required env vars
if [[ -z "$DB_PASSWORD" ]]; then
  echo "[ERROR] POSTGRES_PASSWORD environment variable not set. Aborting." >&2
  exit 3
fi

# Export password for psql
export PGPASSWORD="$DB_PASSWORD"

# Validate gzip file
if ! gzip -t "$BACKUP_FILE"; then
  echo "[ERROR] Backup file is not a valid gzip archive." >&2
  exit 4
fi

# Restore database
zcat "$BACKUP_FILE" | psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"

if [[ $? -eq 0 ]]; then
  echo "[INFO] Restore successful from: $BACKUP_FILE"
else
  echo "[ERROR] Restore failed." >&2
  exit 5
fi

# Unset sensitive env
unset PGPASSWORD
