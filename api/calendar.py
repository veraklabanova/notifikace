from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from _db import get_db, CalendarEntry


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        db = get_db()
        try:
            qs = parse_qs(urlparse(self.path).query)
            obligation_type = qs.get("obligation_type", [None])[0]

            query = db.query(CalendarEntry).order_by(CalendarEntry.deadline_date)
            if obligation_type:
                query = query.filter(CalendarEntry.obligation_type == obligation_type)

            entries = query.all()
            data = [{
                "id": e.id, "title": e.title, "description": e.description,
                "obligation_type": e.obligation_type,
                "deadline_date": e.deadline_date.isoformat(),
                "source": e.source,
            } for e in entries]

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        finally:
            db.close()
