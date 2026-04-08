import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_analyze_valid():
    payload = {
        "flows": [
            {"bytes": 100, "duration": 10, "src_port": 1234, "dst_port": 80},
            {"bytes": 200, "duration": 20, "src_port": 1235, "dst_port": 443}
        ]
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    # On success, should have analysis_id and label
    assert "analysis_id" in data
    assert "label" in data

def test_analyze_missing_flows():
    payload = {}
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"].startswith("Missing flows")

def test_analyze_network_flows_key():
    payload = {
        "network_flows": [
            {"bytes": 50, "duration": 5, "src_port": 1111, "dst_port": 22}
        ]
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert "label" in data
