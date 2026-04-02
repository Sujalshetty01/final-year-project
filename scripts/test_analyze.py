import json
import urllib.request

url = 'http://localhost:8001/api/v1/analyze'
payload = {
    'network_flows': [
        {'bytes': 100, 'duration': 1, 'sport': 80, 'dport': 443},
        {'bytes': 2000000, 'duration': 5, 'sport': 1234, 'dport': 80}
    ]
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(resp.read().decode('utf-8'))
except Exception as e:
    print('ERROR', e)
