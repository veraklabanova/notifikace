from http.server import BaseHTTPRequestHandler
import json
from datetime import date, timedelta
from urllib.parse import urlparse, parse_qs
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _db import (
    get_db, Client, ClientObligation, CalendarEntry, Notification, ImportLog,
    ClientStatus, ObligationStatus, NotificationStatus
)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        db = get_db()
        try:
            path = urlparse(self.path).path
            qs = parse_qs(urlparse(self.path).query)

            if "upcoming" in path:
                data = self._upcoming(db, qs)
            elif "recent-notifications" in path:
                data = self._recent(db, qs)
            else:
                data = self._stats(db)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        finally:
            db.close()

    def _stats(self, db):
        today = date.today()
        next_7 = today + timedelta(days=7)
        active = db.query(Client).filter(Client.status == ClientStatus.ACTIVE).count()
        upcoming = db.query(ClientObligation).join(CalendarEntry).filter(
            ClientObligation.status == ObligationStatus.UPCOMING, CalendarEntry.deadline_date >= today).count()
        urgent = db.query(ClientObligation).join(CalendarEntry).filter(
            ClientObligation.status.in_([ObligationStatus.UPCOMING, ObligationStatus.NOTIFIED]),
            CalendarEntry.deadline_date >= today, CalendarEntry.deadline_date <= next_7).count()
        sent = db.query(Notification).filter(Notification.status == NotificationStatus.SENT).count()
        errors = db.query(Notification).filter(Notification.status == NotificationStatus.ERROR).count()
        pending = db.query(Notification).filter(Notification.status == NotificationStatus.SCHEDULED).count()
        last_mfcr = db.query(ImportLog).filter(ImportLog.source == "mfcr").order_by(ImportLog.created_at.desc()).first()
        return {
            "clients": {"total": db.query(Client).count(), "active": active,
                        "suspended": db.query(Client).filter(Client.status == ClientStatus.SUSPENDED).count()},
            "obligations": {"total": db.query(ClientObligation).count(), "upcoming": upcoming, "urgent_7_days": urgent},
            "notifications": {"total": db.query(Notification).count(), "sent": sent, "errors": errors, "pending": pending},
            "calendar": {"entries": db.query(CalendarEntry).count()},
            "imports": {
                "mfcr_last": last_mfcr.created_at.isoformat() if last_mfcr else None,
                "mfcr_status": last_mfcr.status.value if last_mfcr else "fallback",
                "helios_last": None, "helios_status": "seed",
            },
        }

    def _upcoming(self, db, qs):
        days = int(qs.get("days", ["30"])[0])
        today = date.today()
        cutoff = today + timedelta(days=days)
        obligations = (
            db.query(ClientObligation).join(Client).join(CalendarEntry)
            .filter(Client.status == ClientStatus.ACTIVE, CalendarEntry.deadline_date >= today, CalendarEntry.deadline_date <= cutoff)
            .order_by(CalendarEntry.deadline_date).limit(50).all()
        )
        return [{"id": o.id, "client_name": o.client.name, "client_id": o.client_id,
                 "title": o.calendar_entry.title, "deadline_date": o.calendar_entry.deadline_date.isoformat(),
                 "days_remaining": (o.calendar_entry.deadline_date - today).days,
                 "status": o.status.value, "obligation_type": o.calendar_entry.obligation_type} for o in obligations]

    def _recent(self, db, qs):
        limit = int(qs.get("limit", ["20"])[0])
        notifications = (
            db.query(Notification).join(Client).join(ClientObligation).join(CalendarEntry)
            .order_by(Notification.created_at.desc()).limit(limit).all()
        )
        return [{"id": n.id, "client_name": n.client.name,
                 "obligation_title": n.obligation.calendar_entry.title,
                 "notification_type": n.notification_type.value, "status": n.status.value,
                 "sent_at": n.sent_at.isoformat() if n.sent_at else None,
                 "created_at": n.created_at.isoformat() if n.created_at else ""} for n in notifications]
