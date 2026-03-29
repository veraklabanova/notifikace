from http.server import BaseHTTPRequestHandler
import json, re
from urllib.parse import urlparse
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from _db import get_db, Client, ClientObligation, CalendarEntry


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        db = get_db()
        try:
            # Extract client_id from path: /api/clients/123/obligations
            m = re.search(r'/clients/(\d+)/obligations', self.path)
            if not m:
                self.send_response(400)
                self.end_headers()
                return

            client_id = int(m.group(1))
            client = db.query(Client).filter(Client.id == client_id).first()
            if not client:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"detail": "Client not found"}).encode())
                return

            obligations = (
                db.query(ClientObligation).join(CalendarEntry)
                .filter(ClientObligation.client_id == client_id)
                .order_by(CalendarEntry.deadline_date).all()
            )
            data = [{
                "id": o.id, "title": o.calendar_entry.title,
                "description": o.calendar_entry.description,
                "obligation_type": o.calendar_entry.obligation_type,
                "deadline_date": o.calendar_entry.deadline_date.isoformat(),
                "status": o.status.value,
            } for o in obligations]

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        finally:
            db.close()
