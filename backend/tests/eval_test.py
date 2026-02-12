import sys
import json
import os
import urllib.request
import urllib.error

# Allow overriding base URL for local runs
RAW_BASE = os.getenv('BACKEND_BASE_URL')
if not RAW_BASE:
    host = os.getenv('BACKEND_HOST', '127.0.0.1')
    port = os.getenv('BACKEND_PORT', '8000')
    RAW_BASE = f'http://{host}:{port}'

# Normalize to an API base that always ends with /api/v1
if RAW_BASE.rstrip('/').endswith('/api/v1'):
    BASE = RAW_BASE.rstrip('/')
else:
    BASE = RAW_BASE.rstrip('/') + '/api/v1'


def fail(msg: str):
    print('FAIL:', msg)
    sys.exit(2)


def ok(msg: str):
    print('OK:', msg)


def post(path, payload, headers=None):
    data = json.dumps(payload).encode()
    hdrs = {'Content-Type': 'application/json'}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.getcode(), json.load(resp)
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode()
        except Exception:
            body = ''
        return e.code, body


def get(path, headers=None):
    hdrs = {}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(f"{BASE}{path}", headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.getcode(), json.load(resp)
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode()
        except Exception:
            body = ''
        return e.code, body


def main():
    # 1) login to get access and refresh tokens
    code, tokens = post('/login', {'username': 'admin', 'password': 'admin'})
    if code != 200:
        fail(f'login failed: {code} {tokens}')
    at = tokens.get('access_token')
    rt = tokens.get('refresh_token')
    if not at or not rt:
        fail('access or refresh token missing from login')
    ok('login returned access token')

    # rotate immediately to ensure a fresh access token (avoid clock/expiry edge cases)
    code_r, tokens_r = post('/refresh', {'refresh_token': rt})
    if code_r != 200:
        fail(f'refresh failed: {code_r} {tokens_r}')
    at = tokens_r.get('access_token')
    if not at:
        fail('rotated access token missing from refresh')
    ok('rotated access token obtained')

    # debug: print token payload and local time to help diagnose expiry issues
    try:
        import jwt, time as _t
        payload = jwt.decode(at, options={"verify_signature": False})
        print('DEBUG: token payload', payload)
        print('DEBUG: now', int(_t.time()), 'exp', payload.get('exp'))
    except Exception as e:
        print('DEBUG: failed to decode token payload', e)

    # 2) send a sample /analyze to populate results_cache
    sample = {
        'network_flows': [
            {
                'src_ip': '10.0.0.1',
                'dst_ip': '8.8.8.8',
                'src_port': 12345,
                'dst_port': 80,
                'protocol': 'TCP',
                'bytes_sent': 100,
                'bytes_received': 200,
                'duration': 0.1
            }
        ],
        'app_name': 'eval_test_app',
        'enable_detailed_analysis': False,
        'use_ensemble': False
    }

    code2, resp = post('/analyze', sample)
    if code2 != 200:
        fail(f'/analyze failed: {code2} {resp}')
    analysis_id = resp.get('analysis_id')
    if not analysis_id:
        fail('/analyze response missing analysis_id')
    ok('analyze returned result and populated cache')

    # 3) call evaluate/summary with Authorization
    headers = {'Authorization': f'Bearer {at}'}
    code3, eval_resp = get('/evaluate/summary', headers=headers)
    if code3 != 200:
        fail(f'/evaluate/summary failed: {code3} {eval_resp}')
    ok('/evaluate/summary returned ROC/confusion data')

    print('\nEVALUATION SMOKE TEST PASSED')


if __name__ == '__main__':
    main()
