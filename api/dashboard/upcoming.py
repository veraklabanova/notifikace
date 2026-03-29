from http.server import BaseHTTPRequestHandler
import json
from datetime import date, timedelta
from urllib.parse import urlparse, parse_qs
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from _db import get_db, Client, ClientObligation, CalendarEntry, ClientStatus


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        db = get_db()
        try:
            qs = parse_qs(urlparse(self.path).query)
            days = int(qs.get("days", ["30"])[0])
            today = date.today()
            cutoff = today + timedelta(days=days)

            obligations = (
                db.query(ClientObligation).join(Client).join(CalendarEntry)
                .filter(Client.status == ClientStatus.ACTIVE, CalendarEntry.deadline_date >= today, CalendarEntry.deadline_date <= cutoff)
                .order_by(CalendarEntry.deadline_date).limit(50).all()
            )
            data = [{
                "id": o.id, "client_name": o.client.name, "client_id": o.client_id,
                "title": o.calendar_entry.title, "deadline_date": o.calendar_entry.deadline_date.isoformat(),
                "days_remaining": (o.calendar_entry.deadline_date - today).days,
                "status": o.status.value, "obligation_type": o.calendar_entry.obligation_type,
            } for o in obligations]

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        finally:
            db.close()
