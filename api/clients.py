from http.server import BaseHTTPRequestHandler
import json, re
from datetime import date
from urllib.parse import urlparse, parse_qs
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _db import get_db, Client, ClientObligation, CalendarEntry


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        db = get_db()
        try:
            path = urlparse(self.path).path
            qs = parse_qs(urlparse(self.path).query)

            # /api/clients/123/obligations
            m = re.search(r'/clients/(\d+)/obligations', path)
            if m:
                data = self._obligations(db, int(m.group(1)))
            else:
                data = self._list(db, qs)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        finally:
            db.close()

    def _list(self, db, qs):
        status = qs.get("status", [None])[0]
        search = qs.get("search", [None])[0]
        query = db.query(Client)
        if status:
            query = query.filter(Client.status == status)
        if search:
            query = query.filter(Client.name.ilike(f"%{search}%"))
        clients = query.order_by(Client.name).all()
        today = date.today()
        return [{
            "id": c.id, "name": c.name, "ico": c.ico,
            "subject_type": c.subject_type.value, "vat_payer": c.vat_payer,
            "vat_frequency": c.vat_frequency.value if c.vat_frequency else None,
            "has_employees": c.has_employees, "email": c.email, "status": c.status.value,
            "created_at": c.created_at.isoformat() if c.created_at else "",
            "updated_at": c.updated_at.isoformat() if c.updated_at else "",
            "obligations_count": db.query(ClientObligation).filter(ClientObligation.client_id == c.id).count(),
            "upcoming_count": db.query(ClientObligation).join(CalendarEntry).filter(
                ClientObligation.client_id == c.id, CalendarEntry.deadline_date >= today).count(),
        } for c in clients]

    def _obligations(self, db, client_id):
        obligations = (
            db.query(ClientObligation).join(CalendarEntry)
            .filter(ClientObligation.client_id == client_id)
            .order_by(CalendarEntry.deadline_date).all()
        )
        return [{"id": o.id, "title": o.calendar_entry.title, "description": o.calendar_entry.description,
                 "obligation_type": o.calendar_entry.obligation_type,
                 "deadline_date": o.calendar_entry.deadline_date.isoformat(),
                 "status": o.status.value} for o in obligations]
