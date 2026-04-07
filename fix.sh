#!/bin/bash
set -e
echo "[fix.sh] Fixing API URLs and Docker config..."

# 1. Replace all localhost:8001 with localhost:8000 in frontend
find ./frontend/src -type f -name '*.js' -exec sed -i 's/localhost:8001/localhost:8000/g' {} +

# 2. Ensure .env exists
if [ ! -f ./frontend/.env ]; then
  echo "REACT_APP_API_URL=http://localhost:8000/api/v1" > ./frontend/.env
else
  grep -q REACT_APP_API_URL ./frontend/.env || echo "REACT_APP_API_URL=http://localhost:8000/api/v1" >> ./frontend/.env
fi

# 3. Docker Compose rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 4. Health check
echo "[fix.sh] Checking backend health..."
sleep 5
curl -f http://localhost:8000/api/v1/health || (echo "[fix.sh] Backend health check failed" && exit 1)
echo "[fix.sh] All done."
