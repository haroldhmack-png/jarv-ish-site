"""Local/private Jarv-ish lead endpoint reference.

Run this file from a PRIVATE operations directory, never as part of the public web root.
Set JARVISH_LEAD_FILE to an absolute path outside the static site before use.
This reference is intentionally stdlib-only and is not an internet production server.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from datetime import datetime, timezone
import json, os, re

HOST = os.getenv('JARVISH_LEAD_HOST', '127.0.0.1')
PORT = int(os.getenv('JARVISH_LEAD_PORT', '8787'))
LEAD_FILE = os.getenv('JARVISH_LEAD_FILE', '')
ALLOWED_ORIGIN = os.getenv('JARVISH_ALLOWED_ORIGIN', 'http://127.0.0.1:8080')
MAX_BODY = 32_768
ALLOWED = {'name','email','company','role','useType','framework','agents','seats','capability','notes','plan','selectedPlan','consent','source','submittedAt'}
EMAIL = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')

def clean(value, limit=1000):
    value = str(value or '').replace('\x00','').strip()
    value = ''.join(ch for ch in value if ch in '\n\t' or ord(ch) >= 32)
    return value[:limit]

def validate(payload):
    record = {key: clean(payload.get(key), 3000 if key == 'notes' else 500) for key in ALLOWED if key in payload}
    if not record.get('name') or not EMAIL.match(record.get('email','')):
        raise ValueError('Valid name and email are required')
    if record.get('consent') != 'accepted':
        raise ValueError('Consent is required')
    record['receivedAt'] = datetime.now(timezone.utc).isoformat()
    return record

class Handler(BaseHTTPRequestHandler):
    def headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
        self.send_header('Vary','Origin')
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers()
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGIN)
        self.send_header('Access-Control-Allow-Headers','Content-Type')
        self.send_header('Access-Control-Allow-Methods','POST, OPTIONS')
        self.end_headers()
    def do_POST(self):
        if self.path != '/api/leads': self.headers(404); self.wfile.write(b'{"error":"not found"}'); return
        if self.headers.get('Origin') != ALLOWED_ORIGIN: self.headers(403); self.wfile.write(b'{"error":"origin rejected"}'); return
        try:
            length = int(self.headers.get('Content-Length','0'))
            if length <= 0 or length > MAX_BODY: raise ValueError('Invalid body size')
            record = validate(json.loads(self.rfile.read(length)))
            if not LEAD_FILE: raise RuntimeError('JARVISH_LEAD_FILE is not configured')
            target = Path(LEAD_FILE).expanduser().resolve()
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('a', encoding='utf-8', newline='\n') as fh:
                fh.write(json.dumps(record, ensure_ascii=False, separators=(',',':')) + '\n')
            self.headers(201); self.wfile.write(b'{"ok":true}')
        except ValueError as exc:
            self.headers(400); self.wfile.write(json.dumps({'error':str(exc)}).encode())
        except Exception:
            self.headers(500); self.wfile.write(b'{"error":"lead storage unavailable"}')
    def log_message(self, format, *args):
        print(f'{self.address_string()} - {format % args}')

if __name__ == '__main__':
    if not LEAD_FILE:
        raise SystemExit('Set JARVISH_LEAD_FILE to an absolute private path outside the public site.')
    print(f'Private lead endpoint: http://{HOST}:{PORT}/api/leads')
    print(f'Writing private JSONL to: {Path(LEAD_FILE).expanduser().resolve()}')
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
