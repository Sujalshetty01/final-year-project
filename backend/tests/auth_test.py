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


def main():
    # create session that ignores environment proxies (avoid corporate proxy)
    def post(path, payload):
        data = json.dumps(payload).encode()
        req = urllib.request.Request(f"{BASE}{path}", data=data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.getcode(), json.load(resp)
        except urllib.error.HTTPError as e:
            try:
                body = e.read().decode()
            except Exception:
                body = ''
            return e.code, body

    # 1) login
    code, tokens = post('/login', {'username': 'admin', 'password': 'admin'})
    if code != 200:
        fail(f'login failed: {code} {tokens}')
    at = tokens.get('access_token')
    rt = tokens.get('refresh_token')
    if not at or not rt:
        fail('tokens missing from login')
    ok('login returned tokens')

    # 2) refresh with original refresh token -> should rotate and return new refresh
    code2, tokens2 = post('/refresh', {'refresh_token': rt})
    if code2 != 200:
        fail(f'refresh failed: {code2} {tokens2}')
    rt2 = tokens2.get('refresh_token')
    if not rt2 or rt2 == rt:
        fail('refresh did not return new refresh token')
    ok('refresh rotated token')

    # 3) attempting to refresh with the old token should now fail
    code3, _ = post('/refresh', {'refresh_token': rt})
    if code3 == 200:
        fail('old refresh token should have been revoked but succeeded')
    ok('old refresh token revoked as expected')

    # 4) logout using the current refresh token (revoke it)
    code4, _ = post('/logout', {'token': rt2})
    if code4 != 200:
        fail(f'logout failed: {code4} {_}')
    ok('logout revoked current refresh token')

    # 5) refreshing with revoked token should fail
    code5, _ = post('/refresh', {'refresh_token': rt2})
    if code5 == 200:
        fail('revoked refresh token unexpectedly succeeded')
    ok('revoked refresh token rejected as expected')

    print('\nALL AUTH TESTS PASSED')


if __name__ == '__main__':
    main()
