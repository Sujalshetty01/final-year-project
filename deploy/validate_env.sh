#!/bin/bash
# Fail if required env vars are missing
REQUIRED_VARS=(API_HOST API_PORT POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD JWT_SECRET)
for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var}" ]; then
    echo "Missing required environment variable: $var"
    exit 1
  fi
done
