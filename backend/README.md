# Malware Classification Backend

This is the backend service for the Malware Classification System, built with FastAPI. It provides RESTful APIs for malware detection, model inference, and system health monitoring.

## Features
- Modular architecture (routes, services, models)
- RESTful API (FastAPI)
- Dockerized for production
- Structured logging for all requests and errors
- Comprehensive tests (pytest)
- Health, prediction, and analysis endpoints
- .env-based configuration

## Setup
1. Clone the repository and navigate to the backend directory:
	```bash
	git clone <repo-url>
	cd backend
	```
2. Create and activate a virtual environment (optional but recommended):
	```bash
	python -m venv .venv
	source .venv/bin/activate  # On Windows: .venv\Scripts\activate
	```
3. Install dependencies:
	```bash
	pip install -r requirements.txt
	```
4. Copy `.env.example` to `.env` and configure environment variables as needed.
5. Run the backend:
	```bash
	python main.py
	```

## Docker
Build and run the backend with Docker:
```bash
docker build -t malware-backend .
docker run --env-file .env -p 8000:8000 malware-backend
```

## .env Configuration
All secrets and environment-specific settings should be placed in `.env`. Example variables:
- `DATABASE_URL`, `ENVIRONMENT`, `FRONTEND_ORIGIN`, `MODEL_DIR`, etc.

## API Endpoints
- `GET /api/v1/health` — Health check
- `POST /api/v1/predict` — Model prediction
- `POST /api/v1/analyze` — Flow analysis
- `GET /api/v1/result/{analysis_id}` — Get analysis result
- `GET /api/v1/stats` — System stats

## Testing
Run all tests with:
```bash
pytest tests
```

## Logging
All requests, responses, and errors are logged with context for observability. Logs are output to stdout by default.

## License
See LICENSE file for details.
