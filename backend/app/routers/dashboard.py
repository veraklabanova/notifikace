from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import (
    Client, ClientObligation, CalendarEntry, Notification,
    ClientStatus, ObligationStatus, NotificationStatus, ImportLog
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    today = date.today()
    next_30 = today + timedelta(days=30)
    next_7 = today + timedelta(days=7)

    total_clients = db.query(Client).count()
    active_clients = db.query(Client).filter(Client.status == ClientStatus.ACTIVE).count()
    suspended_clients = db.query(Client).filter(Client.status == ClientStatus.SUSPENDED).count()

    total_obligations = db.query(ClientObligation).count()
    upcoming_obligations = (
        db.query(ClientObligation)
        .join(CalendarEntry)
        .filter(
            ClientObligation.status == ObligationStatus.UPCOMING,
            CalendarEntry.deadline_date >= today,
        )
        .count()
    )
    urgent_obligations = (
        db.query(ClientObligation)
        .join(CalendarEntry)
        .filter(
            ClientObligation.status.in_([ObligationStatus.UPCOMING, ObligationStatus.NOTIFIED]),
            CalendarEntry.deadline_date >= today,
            CalendarEntry.deadline_date <= next_7,
        )
        .count()
    )

    total_notifications = db.query(Notification).count()
    sent_notifications = db.query(Notification).filter(
        Notification.status == NotificationStatus.SENT
    ).count()
    error_notifications = db.query(Notification).filter(
        Notification.status == NotificationStatus.ERROR
    ).count()
    pending_notifications = db.query(Notification).filter(
        Notification.status == NotificationStatus.SCHEDULED
    ).count()

    # Import status
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

    calendar_entries = db.query(CalendarEntry).count()

    return {
        "clients": {
            "total": total_clients,
            "active": active_clients,
            "suspended": suspended_clients,
        },
        "obligations": {
            "total": total_obligations,
            "upcoming": upcoming_obligations,
            "urgent_7_days": urgent_obligations,
        },
        "notifications": {
            "total": total_notifications,
            "sent": sent_notifications,
            "errors": error_notifications,
            "pending": pending_notifications,
        },
        "calendar": {
            "entries": calendar_entries,
        },
        "imports": {
            "mfcr_last": last_mfcr.created_at.isoformat() if last_mfcr else None,
            "mfcr_status": last_mfcr.status.value if last_mfcr else "never",
            "helios_last": last_helios.created_at.isoformat() if last_helios else None,
            "helios_status": last_helios.status.value if last_helios else "never",
        },
    }


@router.get("/upcoming")
def get_upcoming_obligations(days: int = 30, db: Session = Depends(get_db)):
    today = date.today()
    cutoff = today + timedelta(days=days)
    obligations = (
        db.query(ClientObligation)
        .join(Client)
        .join(CalendarEntry)
        .filter(
            Client.status == ClientStatus.ACTIVE,
            CalendarEntry.deadline_date >= today,
            CalendarEntry.deadline_date <= cutoff,
        )
        .order_by(CalendarEntry.deadline_date)
        .limit(50)
        .all()
    )
    return [
        {
            "id": o.id,
            "client_name": o.client.name,
            "client_id": o.client_id,
            "title": o.calendar_entry.title,
            "deadline_date": o.calendar_entry.deadline_date.isoformat(),
            "days_remaining": (o.calendar_entry.deadline_date - today).days,
            "status": o.status.value,
            "obligation_type": o.calendar_entry.obligation_type,
        }
        for o in obligations
    ]


@router.get("/recent-notifications")
def get_recent_notifications(limit: int = 20, db: Session = Depends(get_db)):
    notifications = (
        db.query(Notification)
        .join(Client)
        .join(ClientObligation)
        .join(CalendarEntry)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": n.id,
            "client_name": n.client.name,
            "obligation_title": n.obligation.calendar_entry.title,
            "notification_type": n.notification_type.value,
            "status": n.status.value,
            "sent_at": n.sent_at.isoformat() if n.sent_at else None,
            "created_at": n.created_at.isoformat() if n.created_at else "",
        }
        for n in notifications
    ]
