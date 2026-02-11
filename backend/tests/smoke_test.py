import urllib.request
import json
import sys

BASE = "http://localhost:8000"


def get_health():
    url = f"{BASE}/api/v1/health"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            body = r.read().decode()
            return 0, json.loads(body)
    except Exception as e:
        return 1, str(e)


def post_analyze():
    url = f"{BASE}/api/v1/analyze"
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
