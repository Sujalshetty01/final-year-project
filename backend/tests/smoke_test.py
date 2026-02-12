import urllib.request
import json
import sys
import os

# Allow overriding the backend base URL via env var for local runs
RAW_BASE = os.getenv('BACKEND_BASE_URL')
if not RAW_BASE:
    RAW_BASE = os.getenv('BACKEND_HOST')
    if RAW_BASE:
        host = RAW_BASE
        port = os.getenv('BACKEND_PORT', '8000')
        RAW_BASE = f'http://{host}:{port}'
    else:
        RAW_BASE = 'http://localhost:8000'

# Normalize to an API base that always ends with /api/v1
if RAW_BASE.rstrip('/').endswith('/api/v1'):
    BASE = RAW_BASE.rstrip('/')
else:
    BASE = RAW_BASE.rstrip('/') + '/api/v1'


def get_health():
    url = f"{BASE}/health"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            body = r.read().decode()
            return 0, json.loads(body)
    except Exception as e:
        return 1, str(e)


def post_analyze():
    url = f"{BASE}/analyze"
    payload = {
        "network_flows": [
            {
                "src_ip": "192.168.1.1",
                "dst_ip": "8.8.8.8",
                "src_port": 51234,
                "dst_port": 53,
                "protocol": "UDP",
                "bytes_sent": 512,
                "bytes_received": 1024,
                "duration": 0.5
            }
        ],
        "app_name": "smoke_test",
        "enable_detailed_analysis": True,
        "use_ensemble": True
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read().decode()
            return 0, json.loads(body)
    except Exception as e:
        return 1, str(e)


if __name__ == "__main__":
    print("Running smoke tests against", BASE)
    code, health = get_health()
    print("Health check exit:", code)
    print(json.dumps(health, indent=2) if code == 0 else health)

    code2, analyze = post_analyze()
    print("Analyze check exit:", code2)
    print(json.dumps(analyze, indent=2) if code2 == 0 else analyze)

    sys.exit(code or code2)
