Malware Classification — Review Notes (v1.0-first-review)

Summary
- FastAPI backend serving `/api/v1/health`, `/api/v1/ready`, `/api/v1/analyze`.
- Unified `ModelLoader` loads a GraphSAGE placeholder and RandomForest fallback if missing.
- Dockerized with `backend/Dockerfile` and `docker-compose.yml`.

How to run (local)
1. Build and run:

```bash
docker-compose up -d --build
```

2. Health check:

```bash
curl http://localhost:8000/api/v1/health
```

3. Example analyze (body.json from schema example):

```bash
curl -X POST http://localhost:8000/api/v1/analyze -H "Content-Type: application/json" --data-binary @body.json
```

What I changed for review
- Merged ML dependencies into `backend/requirements.txt` to ensure `torch` is installed in the image.
- Simplified `backend/Dockerfile` to install dependencies and copy `backend/app`.
- Implemented a single canonical `ModelLoader` with minimal logging for: initialization, placeholder model creation (fallback), model load success/failure, and inference requests.
- Wire `ModelLoader` into FastAPI startup so readiness reflects `models_loaded`.
- Added offline training stubs and docs.
- Added smoke-test script: `backend/tests/smoke_test.py`.

Notes for viva
- Models are intentionally placeholder and created offline to keep runtime safe and reproducible for review.
- Health endpoint returns `models_loaded` and per-model availability to demonstrate readiness.
- Logging is minimal and focuses on model lifecycle events and inference requests.

Next recommended steps
- Add unit tests for request validation and model behaviors.
- Replace placeholder GraphSAGE and baseline with trained artifacts for production.
- Add CI pipeline to run smoke tests on each PR.

Contact
- If you want, I can push the `v1.0-first-review` tag to your remote — provide remote URL or configure `origin`.
