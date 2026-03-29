"""Shared database module for Vercel Serverless Functions.

Uses in-memory SQLite — data resets on cold start.
For production, use a persistent DB (Supabase, PlanetScale, etc.).
"""
from datetime import datetime, date, timedelta
from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, Date, DateTime, Text,
    ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import sessionmaker, DeclarativeBase, relationship, Session
import enum


engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# --- Enums ---

class SubjectType(str, enum.Enum):
    OSVC = "osvc"
    SRO = "sro"

class VatFrequency(str, enum.Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"

class ClientStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"

class ObligationStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    NOTIFIED = "notified"
    PAST_DUE = "past_due"

class NotificationType(str, enum.Enum):
    DAYS_30 = "30day"
    DAYS_7 = "7day"

class NotificationStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    SENT = "sent"
    ERROR = "error"

class ImportStatus(str, enum.Enum):
    SUCCESS = "success"
    ERROR = "error"


# --- Models ---

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    ico = Column(String(20), unique=True, nullable=False)
    subject_type = Column(SAEnum(SubjectType), nullable=False)
    vat_payer = Column(Boolean, default=False)
    vat_frequency = Column(SAEnum(VatFrequency), nullable=True)
    has_employees = Column(Boolean, default=False)
    email = Column(String(200), nullable=False)
    status = Column(SAEnum(ClientStatus), default=ClientStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    obligations = relationship("ClientObligation", back_populates="client", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="client", cascade="all, delete-orphan")


class CalendarEntry(Base):
    __tablename__ = "calendar_entries"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    obligation_type = Column(String(100), nullable=False)
    deadline_date = Column(Date, nullable=False)
    source = Column(String(20), default="manual")
    created_at = Column(DateTime, default=datetime.utcnow)
    obligations = relationship("ClientObligation", back_populates="calendar_entry")


class MappingRule(Base):
    __tablename__ = "mapping_rules"
    id = Column(Integer, primary_key=True, index=True)
    subject_type = Column(String(10), nullable=True)
    vat_payer = Column(Boolean, nullable=True)
    vat_frequency = Column(String(20), nullable=True)
    has_employees = Column(Boolean, nullable=True)
    obligation_type = Column(String(100), nullable=False)
    description = Column(String(300), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ClientObligation(Base):
    __tablename__ = "client_obligations"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    calendar_entry_id = Column(Integer, ForeignKey("calendar_entries.id"), nullable=False)
    status = Column(SAEnum(ObligationStatus), default=ObligationStatus.UPCOMING)
    created_at = Column(DateTime, default=datetime.utcnow)
    client = relationship("Client", back_populates="obligations")
    calendar_entry = relationship("CalendarEntry", back_populates="obligations")
    notifications = relationship("Notification", back_populates="obligation", cascade="all, delete-orphan")


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    obligation_id = Column(Integer, ForeignKey("client_obligations.id"), nullable=False)
    notification_type = Column(SAEnum(NotificationType), nullable=False)
    status = Column(SAEnum(NotificationStatus), default=NotificationStatus.SCHEDULED)
    sent_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    email_to = Column(String(200), nullable=False)
    subject = Column(String(300), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    client = relationship("Client", back_populates="notifications")
    obligation = relationship("ClientObligation", back_populates="notifications")


class ImportLog(Base):
    __tablename__ = "import_log"
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(20), nullable=False)
    status = Column(SAEnum(ImportStatus), nullable=False)
    entries_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# --- Seed Data ---

SEED_CLIENTS = [
    {"name": "Jan Novák", "ico": "12345678", "subject_type": SubjectType.OSVC, "vat_payer": True, "vat_frequency": VatFrequency.MONTHLY, "has_employees": False, "email": "jan.novak@example.com"},
    {"name": "Eva Svobodová", "ico": "23456789", "subject_type": SubjectType.OSVC, "vat_payer": False, "vat_frequency": None, "has_employees": False, "email": "eva.svobodova@example.com"},
    {"name": "TechSoft s.r.o.", "ico": "34567890", "subject_type": SubjectType.SRO, "vat_payer": True, "vat_frequency": VatFrequency.MONTHLY, "has_employees": True, "email": "info@techsoft.cz"},
    {"name": "Petr Dvořák", "ico": "45678901", "subject_type": SubjectType.OSVC, "vat_payer": True, "vat_frequency": VatFrequency.QUARTERLY, "has_employees": True, "email": "petr.dvorak@example.com"},
    {"name": "DesignStudio s.r.o.", "ico": "56789012", "subject_type": SubjectType.SRO, "vat_payer": True, "vat_frequency": VatFrequency.QUARTERLY, "has_employees": True, "email": "office@designstudio.cz"},
    {"name": "Marie Černá", "ico": "67890123", "subject_type": SubjectType.OSVC, "vat_payer": False, "vat_frequency": None, "has_employees": False, "email": "marie.cerna@example.com", "status": ClientStatus.SUSPENDED},
    {"name": "GreenGarden s.r.o.", "ico": "78901234", "subject_type": SubjectType.SRO, "vat_payer": False, "vat_frequency": None, "has_employees": True, "email": "info@greengarden.cz"},
    {"name": "Tomáš Horák", "ico": "89012345", "subject_type": SubjectType.OSVC, "vat_payer": True, "vat_frequency": VatFrequency.MONTHLY, "has_employees": True, "email": "tomas.horak@example.com"},
    {"name": "FastBuild s.r.o.", "ico": "90123456", "subject_type": SubjectType.SRO, "vat_payer": True, "vat_frequency": VatFrequency.MONTHLY, "has_employees": True, "email": "info@fastbuild.cz"},
    {"name": "Lucie Králová", "ico": "01234567", "subject_type": SubjectType.OSVC, "vat_payer": False, "vat_frequency": None, "has_employees": False, "email": "lucie.kralova@example.com", "status": ClientStatus.TERMINATED},
]

SEED_RULES = [
    {"subject_type": None, "vat_payer": True, "vat_frequency": "monthly", "has_employees": None, "obligation_type": "dph_mesicni", "description": "Přiznání k DPH — měsíční plátce"},
    {"subject_type": None, "vat_payer": True, "vat_frequency": "quarterly", "has_employees": None, "obligation_type": "dph_ctvrtletni", "description": "Přiznání k DPH — čtvrtletní plátce"},
    {"subject_type": "sro", "vat_payer": True, "vat_frequency": None, "has_employees": None, "obligation_type": "kontrolni_hlaseni_mesicni", "description": "Kontrolní hlášení — s.r.o. (měsíčně)"},
    {"subject_type": "osvc", "vat_payer": True, "vat_frequency": "monthly", "has_employees": None, "obligation_type": "kontrolni_hlaseni_mesicni", "description": "Kontrolní hlášení — OSVČ měsíční"},
    {"subject_type": "osvc", "vat_payer": True, "vat_frequency": "quarterly", "has_employees": None, "obligation_type": "kontrolni_hlaseni_ctvrtletni", "description": "Kontrolní hlášení — OSVČ čtvrtletní"},
    {"subject_type": "osvc", "vat_payer": None, "vat_frequency": None, "has_employees": None, "obligation_type": "dpfo", "description": "Daň z příjmů fyzických osob (OSVČ)"},
    {"subject_type": "sro", "vat_payer": None, "vat_frequency": None, "has_employees": None, "obligation_type": "dppo", "description": "Daň z příjmů právnických osob (s.r.o.)"},
    {"subject_type": "osvc", "vat_payer": None, "vat_frequency": None, "has_employees": None, "obligation_type": "socialni_osvc", "description": "Přehled OSVČ — ČSSZ"},
    {"subject_type": "osvc", "vat_payer": None, "vat_frequency": None, "has_employees": None, "obligation_type": "zdravotni_osvc", "description": "Přehled OSVČ — zdravotní pojišťovna"},
    {"subject_type": None, "vat_payer": None, "vat_frequency": None, "has_employees": True, "obligation_type": "zamestnanci_mesicni", "description": "Měsíční odvody za zaměstnance"},
    {"subject_type": None, "vat_payer": None, "vat_frequency": None, "has_employees": True, "obligation_type": "zamestnanci_rocni", "description": "Roční vyúčtování daně ze závislé činnosti"},
    {"subject_type": None, "vat_payer": None, "vat_frequency": None, "has_employees": None, "obligation_type": "silnicni_dan", "description": "Silniční daň"},
]


def _make_calendar_2026():
    entries = []
    # DPH mesicni
    months = [
        ("leden", 2, 25), ("únor", 3, 25), ("březen", 4, 27), ("duben", 5, 25),
        ("květen", 6, 25), ("červen", 7, 27), ("červenec", 8, 25), ("srpen", 9, 25),
        ("září", 10, 26), ("říjen", 11, 25), ("listopad", 12, 28),
    ]
    for name, m, d in months:
        entries.append({"title": f"DPH — přiznání za {name} 2026", "obligation_type": "dph_mesicni",
                        "deadline_date": date(2026, m, d), "description": f"Podání přiznání k DPH za {name} 2026"})
        entries.append({"title": f"Kontrolní hlášení — {name} 2026", "obligation_type": "kontrolni_hlaseni_mesicni",
                        "deadline_date": date(2026, m, d), "description": f"Kontrolní hlášení k DPH za {name} 2026"})
    entries.append({"title": "DPH — přiznání za prosinec 2026", "obligation_type": "dph_mesicni",
                    "deadline_date": date(2027, 1, 25), "description": "Podání přiznání k DPH za prosinec 2026"})
    entries.append({"title": "Kontrolní hlášení — prosinec 2026", "obligation_type": "kontrolni_hlaseni_mesicni",
                    "deadline_date": date(2027, 1, 25), "description": "Kontrolní hlášení k DPH za prosinec 2026"})

    # DPH ctvrtletni
    for q, m, d in [("Q1", 4, 27), ("Q2", 7, 27), ("Q3", 10, 26)]:
        entries.append({"title": f"DPH — přiznání za {q} 2026", "obligation_type": "dph_ctvrtletni",
                        "deadline_date": date(2026, m, d), "description": f"Přiznání k DPH za {q} 2026"})
        entries.append({"title": f"Kontrolní hlášení — {q} 2026", "obligation_type": "kontrolni_hlaseni_ctvrtletni",
                        "deadline_date": date(2026, m, d), "description": f"Kontrolní hlášení za {q} 2026"})
    entries.append({"title": "DPH — přiznání za Q4 2026", "obligation_type": "dph_ctvrtletni",
                    "deadline_date": date(2027, 1, 25), "description": "Přiznání k DPH za Q4 2026"})
    entries.append({"title": "Kontrolní hlášení — Q4 2026", "obligation_type": "kontrolni_hlaseni_ctvrtletni",
                    "deadline_date": date(2027, 1, 25), "description": "Kontrolní hlášení za Q4 2026"})

    # DPFO / DPPO
    entries.append({"title": "Daň z příjmů FO — přiznání 2025", "obligation_type": "dpfo",
                    "deadline_date": date(2026, 4, 1), "description": "Přiznání DPFO za 2025 (papírové)"})
    entries.append({"title": "Daň z příjmů FO — elektronické 2025", "obligation_type": "dpfo",
                    "deadline_date": date(2026, 5, 4), "description": "Přiznání DPFO za 2025 (elektronicky)"})
    entries.append({"title": "Daň z příjmů PO — přiznání 2025", "obligation_type": "dppo",
                    "deadline_date": date(2026, 4, 1), "description": "Přiznání DPPO za 2025"})
    entries.append({"title": "Daň z příjmů PO — elektronické 2025", "obligation_type": "dppo",
                    "deadline_date": date(2026, 5, 4), "description": "Přiznání DPPO za 2025 (elektronicky)"})

    # Socialni / zdravotni
    entries.append({"title": "Přehled OSVČ — ČSSZ za 2025", "obligation_type": "socialni_osvc",
                    "deadline_date": date(2026, 5, 4), "description": "Přehled příjmů a výdajů OSVČ — ČSSZ"})
    entries.append({"title": "Přehled OSVČ — ZP za 2025", "obligation_type": "zdravotni_osvc",
                    "deadline_date": date(2026, 5, 4), "description": "Přehled OSVČ — zdravotní pojišťovna"})

    # Zamestnavatel mesicni
    emp_months = [
        ("leden", 2, 20), ("únor", 3, 20), ("březen", 4, 20), ("duben", 5, 20),
        ("květen", 6, 22), ("červen", 7, 20), ("červenec", 8, 20), ("srpen", 9, 21),
        ("září", 10, 20), ("říjen", 11, 20), ("listopad", 12, 21),
    ]
    for name, m, d in emp_months:
        entries.append({"title": f"Odvody za zaměstnance — {name} 2026", "obligation_type": "zamestnanci_mesicni",
                        "deadline_date": date(2026, m, d), "description": f"SP, ZP a záloha daně za {name} 2026"})
    entries.append({"title": "Odvody za zaměstnance — prosinec 2026", "obligation_type": "zamestnanci_mesicni",
                    "deadline_date": date(2027, 1, 20), "description": "SP, ZP a záloha daně za prosinec 2026"})

    # Rocni zamestnavatel
    entries.append({"title": "Vyúčtování daně ze závislé činnosti 2025", "obligation_type": "zamestnanci_rocni",
                    "deadline_date": date(2026, 3, 2), "description": "Roční vyúčtování za 2025"})

    # Silnicni dan
    entries.append({"title": "Silniční daň — přiznání za 2025", "obligation_type": "silnicni_dan",
                    "deadline_date": date(2026, 1, 31), "description": "Přiznání a platba silniční daně za 2025"})

    return entries


def _match_rule(client: Client, rule: MappingRule) -> bool:
    if rule.subject_type and rule.subject_type != client.subject_type.value:
        return False
    if rule.vat_payer is not None and rule.vat_payer != client.vat_payer:
        return False
    if rule.vat_frequency and (not client.vat_frequency or rule.vat_frequency != client.vat_frequency.value):
        return False
    if rule.has_employees is not None and rule.has_employees != client.has_employees:
        return False
    return True


_initialized = False

def get_db() -> Session:
    global _initialized
    if not _initialized:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        # Seed
        for c in SEED_CLIENTS:
            db.add(Client(**{k: v for k, v in c.items() if k != "status"}, status=c.get("status", ClientStatus.ACTIVE)))
        for r in SEED_RULES:
            db.add(MappingRule(**r))
        for e in _make_calendar_2026():
            db.add(CalendarEntry(**e, source="fallback"))
        db.commit()

        # Compute obligations
        rules = db.query(MappingRule).filter(MappingRule.is_active == True).all()
        entries = db.query(CalendarEntry).filter(CalendarEntry.deadline_date >= date.today()).all()
        clients = db.query(Client).filter(Client.status == ClientStatus.ACTIVE).all()
        for client in clients:
            matched_types = {r.obligation_type for r in rules if _match_rule(client, r)}
            for entry in entries:
                if entry.obligation_type in matched_types:
                    db.add(ClientObligation(client_id=client.id, calendar_entry_id=entry.id))
        db.commit()

        # Plan notifications
        today = date.today()
        obligations = (
            db.query(ClientObligation).join(Client).join(CalendarEntry)
            .filter(Client.status == ClientStatus.ACTIVE, CalendarEntry.deadline_date >= today)
            .all()
        )
        for o in obligations:
            entry = o.calendar_entry
            client = o.client
            for lead_days, ntype in [(30, NotificationType.DAYS_30), (7, NotificationType.DAYS_7)]:
                send_date = entry.deadline_date - timedelta(days=lead_days)
                if send_date <= today and send_date >= today - timedelta(days=3):
                    db.add(Notification(
                        client_id=client.id, obligation_id=o.id,
                        notification_type=ntype, status=NotificationStatus.SENT,
                        email_to=client.email, sent_at=datetime.utcnow(),
                        subject=f"{'Upozornění (30 dní)' if ntype == NotificationType.DAYS_30 else 'Urgentní (7 dní)'}: {entry.title}",
                    ))
                    o.status = ObligationStatus.NOTIFIED

        # Mark past due
        for o in db.query(ClientObligation).join(CalendarEntry).filter(CalendarEntry.deadline_date < today).all():
            o.status = ObligationStatus.PAST_DUE

        db.commit()
        db.close()
        _initialized = True

    return SessionLocal()
