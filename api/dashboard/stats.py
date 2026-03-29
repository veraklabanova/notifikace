from http.server import BaseHTTPRequestHandler
import json
from datetime import date, timedelta
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from _db import (
    get_db, Client, ClientObligation, CalendarEntry, Notification, ImportLog,
    ClientStatus, ObligationStatus, NotificationStatus
)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        db = get_db()
        try:
            today = date.today()
            next_7 = today + timedelta(days=7)

            total_clients = db.query(Client).count()
            active_clients = db.query(Client).filter(Client.status == ClientStatus.ACTIVE).count()
            suspended_clients = db.query(Client).filter(Client.status == ClientStatus.SUSPENDED).count()

            upcoming = db.query(ClientObligation).join(CalendarEntry).filter(
                ClientObligation.status == ObligationStatus.UPCOMING,
                CalendarEntry.deadline_date >= today,
            ).count()
            urgent = db.query(ClientObligation).join(CalendarEntry).filter(
                ClientObligation.status.in_([ObligationStatus.UPCOMING, ObligationStatus.NOTIFIED]),
                CalendarEntry.deadline_date >= today, CalendarEntry.deadline_date <= next_7,
            ).count()

            total_notif = db.query(Notification).count()
            sent_notif = db.query(Notification).filter(Notification.status == NotificationStatus.SENT).count()
            error_notif = db.query(Notification).filter(Notification.status == NotificationStatus.ERROR).count()
            pending_notif = db.query(Notification).filter(Notification.status == NotificationStatus.SCHEDULED).count()

            calendar_entries = db.query(CalendarEntry).count()

            last_mfcr = db.query(ImportLog).filter(ImportLog.source == "mfcr").order_by(ImportLog.created_at.desc()).first()
            last_helios = db.query(ImportLog).filter(ImportLog.source == "helios").order_by(ImportLog.created_at.desc()).first()

            data = {
                "clients": {"total": total_clients, "active": active_clients, "suspended": suspended_clients},
                "obligations": {"total": db.query(ClientObligation).count(), "upcoming": upcoming, "urgent_7_days": urgent},
                "notifications": {"total": total_notif, "sent": sent_notif, "errors": error_notif, "pending": pending_notif},
                "calendar": {"entries": calendar_entries},
                "imports": {
                    "mfcr_last": last_mfcr.created_at.isoformat() if last_mfcr else None,
                    "mfcr_status": last_mfcr.status.value if last_mfcr else "fallback",
                    "helios_last": last_helios.created_at.isoformat() if last_helios else None,
                    "helios_status": last_helios.status.value if last_helios else "seed",
                },
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        finally:
            db.close()
