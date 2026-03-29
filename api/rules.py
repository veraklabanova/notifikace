from http.server import BaseHTTPRequestHandler
import json
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _db import get_db, MappingRule


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        db = get_db()
        try:
            rules = db.query(MappingRule).order_by(MappingRule.obligation_type).all()
            data = [{"id": r.id, "subject_type": r.subject_type, "vat_payer": r.vat_payer,
                     "vat_frequency": r.vat_frequency, "has_employees": r.has_employees,
                     "obligation_type": r.obligation_type, "description": r.description,
                     "is_active": r.is_active} for r in rules]

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        finally:
            db.close()
