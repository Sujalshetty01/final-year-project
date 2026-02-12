import urllib.request, json
url='http://127.0.0.1:8001/api/v1/login'
req=urllib.request.Request(url, data=json.dumps({'username':'admin','password':'admin'}).encode(), headers={'Content-Type':'application/json'})
with urllib.request.urlopen(req, timeout=5) as r:
    tokens=json.load(r)
print('TOKENS:', tokens)
try:
    import jwt
    payload=jwt.decode(tokens['access_token'], options={"verify_signature":False})
    print('ACCESS PAYLOAD:', payload)
    payload_r=jwt.decode(tokens.get('refresh_token',''), options={"verify_signature":False})
    print('REFRESH PAYLOAD:', payload_r)
except Exception as e:
    print('JWT decode failed', e)
