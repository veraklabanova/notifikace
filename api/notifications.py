from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from _db import get_db, Notification, Client, ClientObligation, CalendarEntry


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        db = get_db()
        try:
            qs = parse_qs(urlparse(self.path).query)
            status = qs.get("status", [None])[0]
            limit = int(qs.get("limit", ["100"])[0])

            query = db.query(Notification).join(Client).join(ClientObligation).join(CalendarEntry)
            if status:
                query = query.filter(Notification.status == status)

            notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
            data = [{
                "id": n.id, "client_name": n.client.name, "client_id": n.client_id,
                "obligation_title": n.obligation.calendar_entry.title,
                "deadline_date": n.obligation.calendar_entry.deadline_date.isoformat(),
                "notification_type": n.notification_type.value,
                "status": n.status.value, "email_to": n.email_to, "subject": n.subject,
                "sent_at": n.sent_at.isoformat() if n.sent_at else None,
                "error_message": n.error_message,
                "created_at": n.created_at.isoformat() if n.created_at else "",
            } for n in notifications]

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        finally:
            db.close()
