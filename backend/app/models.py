from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime, Text, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
import enum

from .database import Base


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
    applies_to_subject_type = Column(String(50), nullable=True)
    applies_to_vat = Column(Boolean, nullable=True)
    applies_to_vat_frequency = Column(String(20), nullable=True)
    applies_to_employees = Column(Boolean, nullable=True)
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
