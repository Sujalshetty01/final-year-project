import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_predict_valid():
    payload = {
        "features": [[0.1, 0.2], [0.3, 0.4]],
        "edges": [[0, 1]],
        "node_count": 2
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert data["success"] is True or data["success"] is False
    if data["success"]:
        assert "prediction" in data
        assert "confidence" in data
    else:
        assert "error" in data

def test_predict_invalid_input():
    payload = {
        "features": [],
        "edges": [],
        "node_count": 0
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "error" in data

def test_predict_get():
    response = client.get("/api/v1/predict")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "Use POST method" in data["error"]
