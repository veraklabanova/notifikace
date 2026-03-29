from http.server import BaseHTTPRequestHandler
import json
from datetime import date
from urllib.parse import urlparse, parse_qs
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from _db import get_db, Client, ClientObligation, CalendarEntry


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        db = get_db()
        try:
            qs = parse_qs(urlparse(self.path).query)
            status = qs.get("status", [None])[0]
            subject_type = qs.get("subject_type", [None])[0]
            search = qs.get("search", [None])[0]

            query = db.query(Client)
            if status:
                query = query.filter(Client.status == status)
            if subject_type:
                query = query.filter(Client.subject_type == subject_type)
            if search:
                query = query.filter(Client.name.ilike(f"%{search}%"))

            clients = query.order_by(Client.name).all()
            today = date.today()
            data = []
            for c in clients:
                total = db.query(ClientObligation).filter(ClientObligation.client_id == c.id).count()
                upcoming = db.query(ClientObligation).join(CalendarEntry).filter(
                    ClientObligation.client_id == c.id, CalendarEntry.deadline_date >= today
                ).count()
                data.append({
                    "id": c.id, "name": c.name, "ico": c.ico,
                    "subject_type": c.subject_type.value,
                    "vat_payer": c.vat_payer,
                    "vat_frequency": c.vat_frequency.value if c.vat_frequency else None,
                    "has_employees": c.has_employees, "email": c.email,
                    "status": c.status.value,
                    "created_at": c.created_at.isoformat() if c.created_at else "",
                    "updated_at": c.updated_at.isoformat() if c.updated_at else "",
                    "obligations_count": total, "upcoming_count": upcoming,
                })

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        finally:
            db.close()
