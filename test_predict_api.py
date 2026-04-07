import requests
import json

url = "http://localhost:8000/api/v1/predict"
payload = {
    "features": [[0.1, 0.2]],
    "edges": [[0, 1], [1, 0]],
    "node_count": 2
}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("Request failed:", e)
