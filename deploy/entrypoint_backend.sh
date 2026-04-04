#!/bin/bash
set -e
./deploy/validate_env.sh
./scripts/migrate.sh
exec gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 4
