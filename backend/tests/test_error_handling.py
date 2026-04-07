import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_404_error():
    response = client.get('/api/v1/nonexistent')
    assert response.status_code == 404
    data = response.json()
    assert 'error' in data
    assert data['error'] == 'HTTPException'
