from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json

class Handler(BaseHTTPRequestHandler):
    def _set_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors()
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/api/v1/health'):
            payload = {'status':'healthy','version':'1.0.0','models_loaded':True}
            body = json.dumps(payload).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type','application/json')
            self._set_cors()
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.startswith('/api/v1/ready'):
            self.send_response(200)
            self._set_cors()
            self.send_header('Content-Length','0')
            self.end_headers()
            return
        self.send_response(404)
        self._set_cors()
        self.end_headers()

    def do_POST(self):
        # Simple analyze endpoint: echo back deterministic results
        if self.path.startswith('/api/v1/analyze'):
            length = int(self.headers.get('Content-Length', 0))
            _ = self.rfile.read(length) if length else b''
            payload = {
                'result': 'ok',
                'label': 'benign',
                'score': 0.5,
                'models': {'gnn': True, 'baseline': True}
            }
            body = json.dumps(payload).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type','application/json')
            self._set_cors()
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self._set_cors()
        self.end_headers()


if __name__ == '__main__':
    server = ThreadingHTTPServer(('0.0.0.0', 8001), Handler)
    print('Mock backend listening on http://0.0.0.0:8001')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
