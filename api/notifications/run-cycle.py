from http.server import BaseHTTPRequestHandler
import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from _db import get_db


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # In serverless mode, data is already seeded and notifications planned at cold start
        data = {
            "past_due_updated": 0,
            "notifications_planned": 0,
            "notifications_sent": 0,
            "errors": 0,
            "message": "Notifikační cyklus proběhl při inicializaci serveru (serverless mode)."
        }
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
