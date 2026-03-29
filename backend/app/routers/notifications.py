from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Notification, NotificationStatus, Client, ClientObligation, CalendarEntry
from ..services.notification import plan_notifications, send_pending_notifications, update_past_due

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("")
def list_notifications(
    status: Optional[str] = None,
    client_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = (
        db.query(Notification)
        .join(Client)
        .join(ClientObligation)
        .join(CalendarEntry)
    )
    if status:
        query = query.filter(Notification.status == status)
    if client_id:
        query = query.filter(Notification.client_id == client_id)
    notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
    return [
        {
            "id": n.id,
            "client_name": n.client.name,
            "client_id": n.client_id,
            "obligation_title": n.obligation.calendar_entry.title,
            "deadline_date": n.obligation.calendar_entry.deadline_date.isoformat(),
            "notification_type": n.notification_type.value,
            "status": n.status.value,
            "email_to": n.email_to,
            "subject": n.subject,
            "sent_at": n.sent_at.isoformat() if n.sent_at else None,
            "error_message": n.error_message,
            "created_at": n.created_at.isoformat() if n.created_at else "",
        }
        for n in notifications
    ]


@router.post("/plan")
def plan(db: Session = Depends(get_db)):
    result = plan_notifications(db)
    return result


@router.post("/send")
def send(db: Session = Depends(get_db)):
    result = send_pending_notifications(db)
    return result


@router.post("/run-cycle")
def run_full_cycle(db: Session = Depends(get_db)):
    """Run a full notification cycle: update past due, plan, send."""
    past_due = update_past_due(db)
    planned = plan_notifications(db)
    sent = send_pending_notifications(db)
    return {
        "past_due_updated": past_due,
        "notifications_planned": planned["planned"],
        "notifications_sent": sent["sent"],
        "errors": sent["errors"],
    }


@router.post("/{notification_id}/resend")
def resend_notification(notification_id: int, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.status = NotificationStatus.SCHEDULED
    notif.error_message = None
    notif.sent_at = None
    db.commit()
    result = send_pending_notifications(db)
    return {"resent": True, **result}
