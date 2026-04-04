#!/bin/bash
set -e
DATE=$(date +%Y%m%d_%H%M%S)
PGUSER=${POSTGRES_USER:-malware_user}
PGDB=${POSTGRES_DB:-malware_db}
PGHOST=${POSTGRES_HOST:-db}
PGPASSWORD=${POSTGRES_PASSWORD:-malware_pass}
export PGPASSWORD
pg_dump -h $PGHOST -U $PGUSER $PGDB > backup_${PGDB}_$DATE.sql
unset PGPASSWORD
