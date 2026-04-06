#!/bin/bash
set -e

# Environment validation (robust)
if [ -f "./deploy/validate_env.sh" ]; then
	echo "Validating environment..."
	chmod +x ./deploy/validate_env.sh
	./deploy/validate_env.sh
else
	echo "validate_env.sh not found, skipping..."
fi

# Database migrations (robust)
if [ -f "./scripts/migrate.sh" ]; then
	echo "Running database migrations..."
	chmod +x ./scripts/migrate.sh
	./scripts/migrate.sh
else
	echo "migrate.sh not found, skipping migrations..."
fi

# Start app
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
