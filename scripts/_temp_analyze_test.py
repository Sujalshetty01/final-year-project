import json
import requests

with open('sample_flows.json') as f:
    flows = json.load(f)

payload = {'network_flows': flows}
resp = requests.post('http://127.0.0.1:8001/api/v1/analyze', json=payload)
print(resp.status_code)
print(resp.text)
