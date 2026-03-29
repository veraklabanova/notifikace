"""M1 — Helios Sync: Seed data simulation."""
from sqlalchemy.orm import Session

from ..models import Client, ImportLog, ImportStatus
from ..seed.seed_data import seed_database


def run_sync(db: Session) -> dict:
    """Simulate Helios sync by re-seeding database."""
    seeded = seed_database(db)
    client_count = db.query(Client).count()

    db.add(ImportLog(
        source="helios",
        status=ImportStatus.SUCCESS,
        entries_count=client_count,
    ))
    db.commit()

    return {
        "status": "success",
        "clients_synced": client_count,
        "was_seeded": seeded,
    }
