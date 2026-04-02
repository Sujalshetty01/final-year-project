import requests

def test_health():
    resp = requests.get('http://localhost:8000/health')
    assert resp.status_code == 200
    assert resp.json().get('status') == 'ok'
