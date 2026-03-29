from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CalendarEntry, ImportLog
from ..services.calendar_engine import try_import_mfcr, compute_client_obligations

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


@router.get("")
def list_calendar_entries(
    obligation_type: Optional[str] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(CalendarEntry).order_by(CalendarEntry.deadline_date)
    if obligation_type:
        query = query.filter(CalendarEntry.obligation_type == obligation_type)
    if year:
        query = query.filter(
            CalendarEntry.deadline_date >= f"{year}-01-01",
            CalendarEntry.deadline_date <= f"{year}-12-31",
        )
    entries = query.all()
    return [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "obligation_type": e.obligation_type,
            "deadline_date": e.deadline_date.isoformat(),
            "source": e.source,
        }
        for e in entries
    ]


@router.post("/import-mfcr")
async def import_mfcr(db: Session = Depends(get_db)):
    result = await try_import_mfcr(db)
    return result


@router.post("/compute-obligations")
def compute_obligations(db: Session = Depends(get_db)):
    count = compute_client_obligations(db)
    return {"computed": count}


@router.get("/import-status")
def get_import_status(db: Session = Depends(get_db)):
    last_mfcr = (
        db.query(ImportLog)
        .filter(ImportLog.source == "mfcr")
        .order_by(ImportLog.created_at.desc())
        .first()
    )
    last_helios = (
        db.query(ImportLog)
        .filter(ImportLog.source == "helios")
        .order_by(ImportLog.created_at.desc())
        .first()
    )
    return {
        "mfcr": {
            "last_import": last_mfcr.created_at.isoformat() if last_mfcr else None,
            "status": last_mfcr.status.value if last_mfcr else "never",
            "entries_count": last_mfcr.entries_count if last_mfcr else 0,
            "error": last_mfcr.error_message if last_mfcr else None,
        },
        "helios": {
            "last_sync": last_helios.created_at.isoformat() if last_helios else None,
            "status": last_helios.status.value if last_helios else "never",
            "entries_count": last_helios.entries_count if last_helios else 0,
            "error": last_helios.error_message if last_helios else None,
        },
    }


@router.get("/obligation-types")
def list_obligation_types(db: Session = Depends(get_db)):
    types = db.query(CalendarEntry.obligation_type).distinct().all()
    return [t[0] for t in types]
