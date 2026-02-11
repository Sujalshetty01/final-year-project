import requests
import json

API_URL = "http://localhost:8000/api/v1/analyze"

sample_payload = {
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
    "app_name": "test_app",
    "enable_detailed_analysis": True,
    "use_ensemble": True
}

response = requests.post(API_URL, json=sample_payload)

print("Status Code:", response.status_code)
print("Response JSON:")
print(json.dumps(response.json(), indent=2))
