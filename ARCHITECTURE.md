# Architecture Overview

## System Diagram

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Frontend   │ <--> │  Backend    │ <--> │  PostgreSQL │
│ (React)     │      │ (FastAPI)   │      │  Database   │
└─────────────┘      └─────────────┘      └─────────────┘
      │                  │
      │   Prometheus     │
      └─────▶ Metrics ◀──┘
```

- **Frontend:** React, served via Nginx in production.
- **Backend:** FastAPI, Gunicorn/Uvicorn, Prometheus metrics, Sentry-ready.
- **Database:** PostgreSQL, Alembic migrations, backup scripts.
- **Monitoring:** Prometheus, Grafana dashboards, Sentry error tracking.
- **CI/CD:** GitHub Actions, Dependabot, security checks, auto-deploy.
