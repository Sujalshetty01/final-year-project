#!/bin/bash
set -e
if [ $# -ne 1 ]; then
  echo "Usage: $0 <backup_file.sql>"
  exit 1
fi
PGUSER=${POSTGRES_USER:-malware_user}
PGDB=${POSTGRES_DB:-malware_db}
PGHOST=${POSTGRES_HOST:-db}
PGPASSWORD=${POSTGRES_PASSWORD:-malware_pass}
export PGPASSWORD
psql -h $PGHOST -U $PGUSER $PGDB < "$1"
unset PGPASSWORD
