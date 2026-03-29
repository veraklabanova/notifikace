"""M4 — Notification Engine: e-mail notifications with 30/7 day lead times."""
import hashlib
import logging
import os
import smtplib
from datetime import datetime, date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sqlalchemy.orm import Session

from ..models import (
    Client, ClientObligation, Notification, CalendarEntry,
    NotificationType, NotificationStatus, ObligationStatus, ClientStatus
)

logger = logging.getLogger(__name__)

LEAD_TIMES = [
    (30, NotificationType.DAYS_30),
    (7, NotificationType.DAYS_7),
]

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", "notifikace@ucetni-firma.cz")
MOCK_EMAIL = not SMTP_HOST


def plan_notifications(db: Session) -> dict:
    """Plan notifications for all upcoming obligations within lead time windows."""
    today = date.today()
    planned = 0
    skipped = 0

    obligations = (
        db.query(ClientObligation)
        .join(Client)
        .join(CalendarEntry)
        .filter(
            Client.status == ClientStatus.ACTIVE,
            ClientObligation.status.in_([ObligationStatus.UPCOMING, ObligationStatus.NOTIFIED]),
            CalendarEntry.deadline_date >= today,
        )
        .all()
    )

    for obligation in obligations:
        client = obligation.client
        entry = obligation.calendar_entry

        if not client.email:
            continue

        for lead_days, notif_type in LEAD_TIMES:
            send_date = entry.deadline_date - timedelta(days=lead_days)
            if send_date > today:
                continue
            if send_date < today - timedelta(days=3):
                continue

            idempotency_key = _make_idempotency_key(client.id, obligation.id, notif_type.value)
            existing = (
                db.query(Notification)
                .filter(
                    Notification.client_id == client.id,
                    Notification.obligation_id == obligation.id,
                    Notification.notification_type == notif_type,
                )
                .first()
            )
            if existing:
                skipped += 1
                continue

            subject = _make_subject(entry, notif_type)
            db.add(Notification(
                client_id=client.id,
                obligation_id=obligation.id,
                notification_type=notif_type,
                status=NotificationStatus.SCHEDULED,
                email_to=client.email,
                subject=subject,
            ))
            planned += 1

            if obligation.status == ObligationStatus.UPCOMING:
                obligation.status = ObligationStatus.NOTIFIED

    db.commit()
    return {"planned": planned, "skipped_duplicates": skipped}


def send_pending_notifications(db: Session) -> dict:
    """Send all scheduled notifications."""
    pending = (
        db.query(Notification)
        .filter(Notification.status == NotificationStatus.SCHEDULED)
        .all()
    )

    sent = 0
    errors = 0
    for notif in pending:
        try:
            body = _make_email_body(notif)
            _send_email(notif.email_to, notif.subject, body)
            notif.status = NotificationStatus.SENT
            notif.sent_at = datetime.utcnow()
            sent += 1
        except Exception as e:
            notif.status = NotificationStatus.ERROR
            notif.error_message = str(e)
            errors += 1
            logger.error(f"Failed to send notification {notif.id}: {e}")

    db.commit()
    return {"sent": sent, "errors": errors}


def update_past_due(db: Session) -> int:
    """Mark obligations past their deadline as past_due."""
    today = date.today()
    updated = (
        db.query(ClientObligation)
        .join(CalendarEntry)
        .filter(
            CalendarEntry.deadline_date < today,
            ClientObligation.status.in_([ObligationStatus.UPCOMING, ObligationStatus.NOTIFIED]),
        )
        .all()
    )
    for o in updated:
        o.status = ObligationStatus.PAST_DUE
    db.commit()
    return len(updated)


def _make_idempotency_key(client_id: int, obligation_id: int, notif_type: str) -> str:
    raw = f"{client_id}:{obligation_id}:{notif_type}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _make_subject(entry: CalendarEntry, notif_type: NotificationType) -> str:
    if notif_type == NotificationType.DAYS_30:
        prefix = "Upozornění (30 dní)"
    else:
        prefix = "Urgentní upozornění (7 dní)"
    return f"{prefix}: {entry.title}"


def _make_email_body(notif: Notification) -> str:
    entry = notif.obligation.calendar_entry
    client = notif.client

    if notif.notification_type == NotificationType.DAYS_30:
        urgency = "30 dní"
        greeting = "s dostatečným předstihem"
    else:
        urgency = "7 dní"
        greeting = "v blízké době"

    return f"""Dobrý den, {client.name},

rádi bychom Vás upozornili na nadcházející povinnost, jejíž termín vyprší {greeting}.

Povinnost: {entry.title}
Termín: {entry.deadline_date.strftime('%d. %m. %Y')}
Zbývá: {urgency}

{entry.description or ''}

Pokud máte jakékoli dotazy, neváhejte se obrátit na Vaši účetní.

S pozdravem,
Vaše účetní firma

---
Tato zpráva byla odeslána automaticky systémem daňových notifikací.
"""


def _send_email(to: str, subject: str, body: str):
    if MOCK_EMAIL:
        logger.info(f"[MOCK EMAIL] To: {to} | Subject: {subject}")
        logger.info(f"[MOCK EMAIL] Body:\n{body[:200]}...")
        return

    msg = MIMEMultipart()
    msg["From"] = SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        if SMTP_USER:
            server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
