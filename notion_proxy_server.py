import os, json, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.error import HTTPError

NOTION_TOKEN = os.environ.get('NOTION_TOKEN', '')
DB_ID = '0993ccbe12c44828b4bf08cbf216005c'
PORT = 9998

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): print(f"  {args[1]} {args[0][:60]}")
    def do_OPTIONS(self):
        self.send_response(200); self._cors(); self.end_headers()
    def do_GET(self):
        self._respond(200, {'ok': True})
    def do_POST(self):
        raw = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        d = json.loads(raw)
        action = d.get('action', '')
        token = NOTION_TOKEN
        if not token:
            self._respond(400, {'error': 'missing token'}); return
        hdrs = {'Authorization': f'Bearer {token}', 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json'}
        try:
            if action == 'login':
                body = json.dumps({'filter': {'property': 'קוד כניסה', 'rich_text': {'equals': d.get('code','')}}}).encode()
                resp = json.loads(urlopen(Request(f'https://api.notion.com/v1/databases/{DB_ID}/query', data=body, headers=hdrs), timeout=10).read())
                results = resp.get('results', [])
                if not results:
                    self._respond(404, {'error': 'not found'}); return
                p = results[0]; props = p.get('properties', {})
                def gp(k, t):
                    prop = props.get(k, {})
                    if t=='title': return ''.join(r.get('plain_text','') for r in prop.get('title',[]))
                    if t=='number': return prop.get('number', 0) or 0
                    if t=='select': s=prop.get('select'); return s.get('name','') if s else ''
                    return ''
                self._respond(200, {'ok': True, 'student': {'page_id': p['id'], 'name': gp('שם','title'), 'current_lesson': gp('שיעור נוכחי','number') or 1, 'status': gp('סטטוס','select') or 'before'}})
            elif action == 'update':
                body = json.dumps({'properties': {'סטטוס': {'select': {'name': d.get('status','')}}, 'שיעור נוכחי': {'number': int(d.get('lesson',1))}}}).encode()
                urlopen(Request(f'https://api.notion.com/v1/pages/{d.get("page_id","")}', data=body, headers=hdrs, method='PATCH'), timeout=10)
                self._respond(200, {'ok': True})
            else:
                self._respond(400, {'error': 'unknown'})
        except HTTPError as e:
            self._respond(e.code, {'error': f'notion {e.code}'})
        except Exception as e:
            self._respond(500, {'error': str(e)[:100]})

    def _respond(self, code, data):
        body = json.dumps(data).encode('ascii')
        self.send_response(code); self._cors()
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

print(f'Notion Proxy on port {PORT}')
HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
