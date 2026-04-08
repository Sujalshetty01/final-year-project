#!/bin/bash
# Automated PostgreSQL database backup script
# Stores compressed, timestamped backups in /backups
# Usage: ./scripts/backup_db.sh

set -euo pipefail

# Load environment variables (edit as needed)
DB_HOST="${POSTGRES_HOST:-db}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-malware_db}"
DB_USER="${POSTGRES_USER:-malware_user}"
DB_PASSWORD="${POSTGRES_PASSWORD:-malware_pass}"
BACKUP_DIR="${BACKUP_DIR:-$(dirname "$0")/../backups}"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_backup_$DATE.sql.gz"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Check required env vars
if [[ -z "$DB_PASSWORD" ]]; then
	echo "[ERROR] POSTGRES_PASSWORD environment variable not set. Aborting." >&2
	exit 1
fi

# Export password for pg_dump
export PGPASSWORD="$DB_PASSWORD"

# Perform backup (compressed)
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"

if [[ $? -eq 0 ]]; then
	echo "[INFO] Backup successful: $BACKUP_FILE"
else
	echo "[ERROR] Backup failed." >&2
	exit 2
fi

# Unset sensitive env
unset PGPASSWORD
