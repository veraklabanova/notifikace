from http.server import BaseHTTPRequestHandler
import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from _db import get_db, CalendarEntry


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        db = get_db()
        try:
            types = db.query(CalendarEntry.obligation_type).distinct().all()
            data = [t[0] for t in types]

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        finally:
            db.close()
