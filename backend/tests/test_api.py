from fastapi.testclient import TestClient
import os

from backend.main import app


client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    j = resp.json()
    assert "status" in j and j["status"] == "ok"
    assert "model_loaded" in j
    assert "model_ready" in j


def test_analyze_basic():
    # simple synthetic flow to exercise /api/v1/analyze
    payload = {"flows": [{"src": "10.0.0.1", "dst": "8.8.8.8", "bytes": 123}, {"src": "10.0.0.2", "dst": "1.2.3.4", "bytes": 500}]}
    resp = client.post("/api/v1/analyze", json=payload)
    assert resp.status_code == 200
    j = resp.json()
    assert "label" in j and "score" in j
