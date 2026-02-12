import requests
import time

BASE = "http://localhost:8000"


def test_health_endpoint():
    r = requests.get(f"{BASE}/health", timeout=5)
    assert r.status_code == 200
    j = r.json()
    assert j.get("status") == "ok"


def test_analyze_endpoint():
    payload = {"flows": [{"src": "10.0.0.1", "dst": "8.8.8.8", "bytes": 123}]}
    r = requests.post(f"{BASE}/api/v1/analyze", json=payload, timeout=5)
    assert r.status_code == 200
    j = r.json()
    assert "label" in j and "score" in j
