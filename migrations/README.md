# Database Migrations

This directory contains Alembic migration scripts for the PostgreSQL database used by the Malware Classification System.

- To create a new migration: `alembic revision --autogenerate -m "message"`
- To apply migrations: `alembic upgrade head`

See the main README for setup instructions.
