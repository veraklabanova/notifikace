"""M3 — Obligation Calendar Engine: Import MFČR Open Data + personalizace."""
import logging
from datetime import datetime, date
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from ..models import (
    CalendarEntry, Client, ClientObligation, MappingRule, ImportLog,
    ImportStatus, ObligationStatus, ClientStatus
)

logger = logging.getLogger(__name__)

MFCR_OPEN_DATA_URL = (
    "https://data.mfcr.cz/api/3/action/package_show?id=danovy-kalendar"
)


async def try_import_mfcr(db: Session) -> dict:
    """Try to import tax calendar from MFČR Open Data. Falls back to existing data."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(MFCR_OPEN_DATA_URL)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    resources = data.get("result", {}).get("resources", [])
                    csv_resources = [
                        r for r in resources
                        if r.get("format", "").upper() in ("CSV", "JSON")
                    ]
                    if csv_resources:
                        resource_url = csv_resources[0]["url"]
                        resp2 = await client.get(resource_url)
                        if resp2.status_code == 200:
                            entries = _parse_mfcr_data(resp2.text, csv_resources[0].get("format", "CSV"))
                            if entries:
                                _save_imported_entries(db, entries)
                                db.add(ImportLog(
                                    source="mfcr",
                                    status=ImportStatus.SUCCESS,
                                    entries_count=len(entries),
                                ))
                                db.commit()
                                return {"status": "success", "source": "mfcr", "entries": len(entries)}

        logger.warning("MFČR import: could not fetch or parse data, using fallback")
        db.add(ImportLog(
            source="mfcr",
            status=ImportStatus.ERROR,
            error_message="Could not fetch or parse MFČR data — using fallback calendar",
        ))
        db.commit()
        return {"status": "fallback", "message": "MFČR data unavailable, using fallback calendar"}

    except Exception as e:
        logger.error(f"MFČR import error: {e}")
        db.add(ImportLog(
            source="mfcr",
            status=ImportStatus.ERROR,
            error_message=str(e),
        ))
        db.commit()
        return {"status": "error", "message": str(e)}


def _parse_mfcr_data(raw: str, fmt: str) -> list[dict]:
    """Parse MFČR data (CSV or JSON). Returns list of calendar entry dicts."""
    entries = []
    try:
        if fmt.upper() == "JSON":
            import json
            data = json.loads(raw)
            if isinstance(data, list):
                for item in data:
                    entry = _map_mfcr_item(item)
                    if entry:
                        entries.append(entry)
        else:
            import csv
            import io
            reader = csv.DictReader(io.StringIO(raw), delimiter=";")
            for row in reader:
                entry = _map_mfcr_item(row)
                if entry:
                    entries.append(entry)
    except Exception as e:
        logger.error(f"Error parsing MFČR data: {e}")
    return entries


def _map_mfcr_item(item: dict) -> Optional[dict]:
    """Map a single MFČR data item to a CalendarEntry dict."""
    try:
        title = item.get("nazev") or item.get("title") or item.get("name", "")
        deadline_str = item.get("datum") or item.get("deadline") or item.get("date", "")
        description = item.get("popis") or item.get("description", "")
        obligation_type = item.get("typ") or item.get("type") or _infer_obligation_type(title)

        if not title or not deadline_str:
            return None

        if isinstance(deadline_str, str):
            for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
                try:
                    deadline_date = datetime.strptime(deadline_str, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                return None
        else:
            deadline_date = deadline_str

        return {
            "title": title,
            "description": description,
            "obligation_type": obligation_type or "other",
            "deadline_date": deadline_date,
            "source": "mfcr",
        }
    except Exception:
        return None


def _infer_obligation_type(title: str) -> str:
    """Infer obligation type from title text."""
    title_lower = title.lower()
    if "dph" in title_lower:
        if "čtvrtlet" in title_lower or "kvartál" in title_lower:
            return "dph_ctvrtletni"
        return "dph_mesicni"
    if "kontrolní hlášení" in title_lower:
        return "kontrolni_hlaseni_mesicni"
    if "příjmů fyzických" in title_lower or "dpfo" in title_lower:
        return "dpfo"
    if "příjmů právnických" in title_lower or "dppo" in title_lower:
        return "dppo"
    if "sociální" in title_lower or "čssz" in title_lower:
        return "socialni_osvc"
    if "zdravotní" in title_lower:
        return "zdravotni_osvc"
    if "silniční" in title_lower:
        return "silnicni_dan"
    if "zaměstnanc" in title_lower:
        return "zamestnanci_mesicni"
    return "other"


def _save_imported_entries(db: Session, entries: list[dict]):
    """Save imported entries, replacing existing MFČR entries."""
    db.query(CalendarEntry).filter(CalendarEntry.source == "mfcr").delete()
    for entry in entries:
        db.add(CalendarEntry(**entry))


def compute_client_obligations(db: Session, client_id: Optional[int] = None):
    """Compute obligations for a client (or all active clients) based on mapping rules."""
    rules = db.query(MappingRule).filter(MappingRule.is_active == True).all()
    calendar_entries = db.query(CalendarEntry).filter(
        CalendarEntry.deadline_date >= date.today()
    ).all()

    if client_id:
        clients = db.query(Client).filter(Client.id == client_id, Client.status == ClientStatus.ACTIVE).all()
    else:
        clients = db.query(Client).filter(Client.status == ClientStatus.ACTIVE).all()

    count = 0
    for client in clients:
        matched_types = _get_matching_obligation_types(client, rules)
        relevant_entries = [e for e in calendar_entries if e.obligation_type in matched_types]

        existing = {
            (o.client_id, o.calendar_entry_id)
            for o in db.query(ClientObligation).filter(ClientObligation.client_id == client.id).all()
        }

        for entry in relevant_entries:
            if (client.id, entry.id) not in existing:
                db.add(ClientObligation(
                    client_id=client.id,
                    calendar_entry_id=entry.id,
                    status=ObligationStatus.UPCOMING,
                ))
                count += 1

    db.commit()
    return count


def _get_matching_obligation_types(client: Client, rules: list[MappingRule]) -> set[str]:
    """Get obligation types that match a client's profile."""
    matched = set()
    for rule in rules:
        if rule.subject_type and rule.subject_type != client.subject_type.value:
            continue
        if rule.vat_payer is not None and rule.vat_payer != client.vat_payer:
            continue
        if rule.vat_frequency and (
            not client.vat_frequency or rule.vat_frequency != client.vat_frequency.value
        ):
            continue
        if rule.has_employees is not None and rule.has_employees != client.has_employees:
            continue
        matched.add(rule.obligation_type)
    return matched
