Project Summary — Brief

- Goal: Reproducible end-to-end pipeline for graph-based network-flow classification.
- Quick start: create `.venv`, `pip install -r backend/requirements.txt`, generate sample `python data/generate_sample.py`, train brief `python models/train.py --epochs 5`, export ONNX and start `uvicorn backend.main:app`.
- Outputs: ONNX models, evaluation plots, and a FastAPI service for inference under `/api/v1/analyze`.
- Reproducibility: seed-controlled dataset generation and recommended CPU-friendly `torch` pins for non-GPU environments.
- Files: see `data/`, `models/`, `backend/`, and `out/` for artifacts.
cd