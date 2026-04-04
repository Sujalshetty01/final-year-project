# Deployment Guide

## Prerequisites
- Docker & Docker Compose
- Python 3.10+ (for local dev)
- Node.js 18+ (for local dev)

## Local Development
1. Copy `.env.example` to `.env` and set secrets.
2. Start backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
3. Start frontend:
   ```bash
   cd frontend
   npm install
   npm start
   ```

## Production Deployment (Docker)
1. Copy `.env.example` to `.env` and set production secrets.
2. Build and start all services:
   ```bash
   docker compose up --build -d
   ```
3. Run database migrations:
   ```bash
   ./scripts/migrate.sh
   ```
4. Access:
   - Frontend: http://localhost:8090
   - Backend:  http://localhost:8001
   - Grafana:  http://localhost:3001 (admin/admin)
   - Prometheus: http://localhost:9090

## Cloud Deployment
- Use a managed PostgreSQL service if possible.
- Set up HTTPS (reverse proxy or cloud load balancer).
- Store secrets securely (cloud secrets manager or GitHub Actions secrets).
- Use auto-scaling for backend/frontend containers.

## Environment Validation
- The backend will fail to start if required env vars are missing (see `deploy/validate_env.sh`).

## Monitoring & Alerting
- Prometheus and Grafana are included in docker-compose for metrics and dashboards.
- Sentry integration is ready (set `SENTRY_DSN` in `.env`).

## Backup & Recovery
- Run `./scripts/backup_db.sh` to create a database backup.
- Schedule via cron for regular backups.
- To restore: `psql -h $PGHOST -U $PGUSER $PGDB < backup_file.sql`
