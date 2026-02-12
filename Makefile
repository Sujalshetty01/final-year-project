VENV=.venv
PY=python

.PHONY: venv install run docker-build docker-run smoke-test

venv:
	$(PY) -m venv $(VENV)
	@echo "activated with: source $(VENV)/bin/activate (Unix) or & $(VENV)\\Scripts\\Activate.ps1 (Windows)"

install: venv
	$(VENV)/Scripts/pip install --upgrade pip
	$(VENV)/Scripts/pip install -r backend/requirements.txt

run:
	$(VENV)/Scripts/uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -t dl-malware-api:latest .

docker-run:
	docker run --rm -p 8000:8000 -e MODEL_PATH=/app/out/models/model.onnx -v $(shell pwd)/out/models:/app/out/models dl-malware-api:latest

smoke-test:
	$(VENV)/Scripts/python scripts/smoke_test.py --model out/models/model.onnx
# Makefile for Malware Classification System
# Provides convenient shortcuts for common operations

.PHONY: help install build up down logs clean test lint format docs

# Default target
.DEFAULT_GOAL := help

# Color output
YELLOW := \033[0;33m
GREEN := \033[0;32m
BLUE := \033[0;34m
NC := \033[0m # No Color

help:
	@echo "$(BLUE)Malware Classification System - Make Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@echo "  make install        Install dependencies"
	@echo "  make dev-backend    Run backend in development mode"
	@echo "  make dev-frontend   Run frontend in development mode"
	@echo ""
	@echo "$(YELLOW)Docker:$(NC)"
	@echo "  make build          Build Docker images"
	@echo "  make up             Start all services"
	@echo "  make down           Stop all services"
	@echo "  make restart        Restart services"
	@echo "  make logs           Show service logs"
	@echo "  make ps             Show service status"
	@echo ""
	@echo "$(YELLOW)Quality:$(NC)"
	@echo "  make lint           Run code linter"
	@echo "  make format         Format code"
	@echo "  make test           Run tests"
	@echo "  make coverage       Generate coverage report"
	@echo ""
	@echo "$(YELLOW)Utilities:$(NC)"
	@echo "  make clean          Clean build artifacts"
	@echo "  make models         Initialize model directory"
	@echo "  make sample         Generate sample data"
	@echo "  make docs           Build documentation"
	@echo "  make health         Check service health"
	@echo ""

install:
	@echo "$(BLUE)Installing dependencies...$(NC)"
	pip install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

dev-backend:
	@echo "$(BLUE)Starting backend in development mode...$(NC)"
	cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "$(BLUE)Starting frontend in development mode...$(NC)"
	cd frontend/public && python -m http.server 8080

build:
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build
	@echo "$(GREEN)✓ Docker images built$(NC)"

up:
	@echo "$(BLUE)Starting services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo "   Frontend: http://localhost:8080"
	@echo "   API: http://localhost:8000"

down:
	@echo "$(BLUE)Stopping services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

restart:
	@echo "$(BLUE)Restarting services...$(NC)"
	docker-compose restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

logs:
	@echo "$(BLUE)Showing service logs...$(NC)"
	docker-compose logs -f

ps:
	@echo "$(BLUE)Service status:$(NC)"
	docker-compose ps

lint:
	@echo "$(BLUE)Running linter...$(NC)"
	python -m flake8 backend/app --max-line-length=120
	@echo "$(GREEN)✓ Linting complete$(NC)"

format:
	@echo "$(BLUE)Formatting code...$(NC)"
	python -m black backend/app
	python -m isort backend/app
	@echo "$(GREEN)✓ Code formatted$(NC)"

test:
	@echo "$(BLUE)Running tests...$(NC)"
	python -m pytest backend/app --cov=backend/app
	@echo "$(GREEN)✓ Tests complete$(NC)"

coverage:
	@echo "$(BLUE)Generating coverage report...$(NC)"
	python -m pytest backend/app --cov=backend/app --cov-report=html
	@echo "$(GREEN)✓ Coverage report: htmlcov/index.html$(NC)"

clean:
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	@echo "$(GREEN)✓ Cleaned$(NC)"

models:
	@echo "$(BLUE)Creating models directory...$(NC)"
	mkdir -p models
	@echo "$(GREEN)✓ Models directory ready$(NC)"

sample:
	@echo "$(BLUE)Sample data already available at sample_flows.json$(NC)"

docs:
	@echo "$(BLUE)Documentation available at README.md$(NC)"

health:
	@echo "$(BLUE)Checking service health...$(NC)"
	@curl -s http://localhost:8000/api/v1/health | python -m json.tool
	@echo "$(GREEN)✓ Health check complete$(NC)"

.PHONY: shell-backend shell-frontend
shell-backend:
	docker-compose exec backend bash

shell-frontend:
	docker-compose exec frontend sh
