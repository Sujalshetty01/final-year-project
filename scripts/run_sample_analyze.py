import json
import urllib.request
import sys
import os

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sample_path = os.path.join(basedir, 'sample_flows.json')
with open(sample_path, 'r', encoding='utf-8') as f:
    flows = json.load(f)

payload = {'network_flows': flows}
body = json.dumps(payload).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/v1/analyze', data=body, headers={'Content-Type':'application/json'})
try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read().decode('utf-8')
        print('HTTP', resp.status)
        print(data)
except urllib.error.HTTPError as e:
    print('HTTPError', e.code)
    try:
        print(e.read().decode('utf-8'))
    except:
        pass
    sys.exit(1)
except Exception as e:
    print('ERROR', str(e))
    sys.exit(2)
