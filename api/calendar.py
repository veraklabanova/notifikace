from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _db import get_db, CalendarEntry, ImportLog


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        db = get_db()
        try:
            path = urlparse(self.path).path
            qs = parse_qs(urlparse(self.path).query)

            if "import-status" in path:
                data = self._import_status(db)
            elif "obligation-types" in path:
                data = [t[0] for t in db.query(CalendarEntry.obligation_type).distinct().all()]
            else:
                data = self._list(db, qs)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        finally:
            db.close()

    def do_POST(self):
        data = {"status": "fallback", "message": "Serverless mode — using fallback calendar data"}
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _list(self, db, qs):
        obligation_type = qs.get("obligation_type", [None])[0]
        query = db.query(CalendarEntry).order_by(CalendarEntry.deadline_date)
        if obligation_type:
            query = query.filter(CalendarEntry.obligation_type == obligation_type)
        return [{"id": e.id, "title": e.title, "description": e.description,
                 "obligation_type": e.obligation_type, "deadline_date": e.deadline_date.isoformat(),
                 "source": e.source} for e in query.all()]

    def _import_status(self, db):
        last_mfcr = db.query(ImportLog).filter(ImportLog.source == "mfcr").order_by(ImportLog.created_at.desc()).first()
        return {
            "mfcr": {"last_import": last_mfcr.created_at.isoformat() if last_mfcr else None,
                     "status": last_mfcr.status.value if last_mfcr else "fallback",
                     "entries_count": last_mfcr.entries_count if last_mfcr else 0, "error": None},
            "helios": {"last_sync": None, "status": "seed", "entries_count": 0, "error": None},
        }
