from http.server import BaseHTTPRequestHandler
import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from _db import get_db, ImportLog


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        db = get_db()
        try:
            last_mfcr = db.query(ImportLog).filter(ImportLog.source == "mfcr").order_by(ImportLog.created_at.desc()).first()
            last_helios = db.query(ImportLog).filter(ImportLog.source == "helios").order_by(ImportLog.created_at.desc()).first()

            data = {
                "mfcr": {
                    "last_import": last_mfcr.created_at.isoformat() if last_mfcr else None,
                    "status": last_mfcr.status.value if last_mfcr else "fallback",
                    "entries_count": last_mfcr.entries_count if last_mfcr else 0,
                    "error": last_mfcr.error_message if last_mfcr else None,
                },
                "helios": {
                    "last_sync": last_helios.created_at.isoformat() if last_helios else None,
                    "status": last_helios.status.value if last_helios else "seed",
                    "entries_count": last_helios.entries_count if last_helios else 0,
                    "error": last_helios.error_message if last_helios else None,
                },
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        finally:
            db.close()
