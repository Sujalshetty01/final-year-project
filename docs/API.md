# API & Deployment Guide

This document summarizes the HTTP API, how to run the service locally and with Docker, and how CI exercises the service.

## Endpoints

- `GET /health` — Liveness/readiness probe. Returns JSON `{ "status": "ok", "model_loaded": bool, "model_ready": bool, "model_path": str|null }`.
- `POST /api/v1/analyze` — Submit a flow window JSON payload `{ "flows": [ { ... } ] }` and receive `{ "label": "malicious|benign", "score": float }`.
- `GET /docs` — Customized Swagger UI with dark theme and branding. (Docs and Redoc are disabled by default; the custom UI is served here.)

Example request (curl):

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"flows":[{"src":"10.0.0.1","dst":"8.8.8.8","bytes":123}]}'
```

## Model placement and environment

- By default the app expects an ONNX model at `out/models/model.onnx`.
- You can override the model path with the environment variable `MODEL_PATH`.
- If `onnxruntime` is not installed or the model is missing, the service falls back to a simple heuristic but reports `model_loaded=false` in `/health`.

## Local development

1. Create a virtual environment and install backend deps:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup.ps1
& .venv\Scripts\Activate.ps1
```

2. Start the service:

```powershell
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

3. Open docs: http://localhost:8000/docs

4. Run smoke test (after placing model at `out/models/model.onnx`):

```bash
python scripts/smoke_test.py --model out/models/model.onnx
```

## Docker

Build and run:

```bash
docker build -t dl-malware-api:latest .
docker run -p 8000:8000 -e MODEL_PATH=/app/out/models/model.onnx -v $(pwd)/out/models:/app/out/models dl-malware-api:latest
```

The `Dockerfile` includes a HEALTHCHECK that hits `/health`.

## CI

- The repository includes a GitHub Actions workflow `.github/workflows/ci-smoke.yml` that:
  - Installs minimal dependencies.
  - Runs `scripts/smoke_test.py` when a model is present, uploading `smoke_result.json` as an artifact.
  - Runs unit tests (`pytest`) if tests exist.
  - Builds the Docker image, runs the container, waits for `/health`, performs HTTP integration checks, runs `pytest` integration tests against the running container, and uploads integration results.

## Troubleshooting

- If `/health` reports `model_loaded=false`:
  - Ensure `onnxruntime` is installed (`pip install onnxruntime`).
  - Ensure the `MODEL_PATH` points to a valid ONNX file.
  - Check logs for errors related to model loading.

- If Swagger UI appears without the logo or CSS:
  - Ensure static assets are present in `backend/static/` and that `backend/static` is included in your Docker image (the included `Dockerfile` copies the repo root).

## Contributing

- Add or update tests under `backend/tests/`. CI will run `pytest` automatically when tests are present.
- To make CI exercise a specific model, add the model artifact to `out/models/` in a PR or configure the workflow to fetch a release model.
