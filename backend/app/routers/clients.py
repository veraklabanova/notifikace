from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Client, ClientStatus, SubjectType, VatFrequency, ClientObligation, CalendarEntry
from ..services.profiling import recalculate_obligations

router = APIRouter(prefix="/api/clients", tags=["clients"])


class ClientCreate(BaseModel):
    name: str
    ico: str
    subject_type: SubjectType
    vat_payer: bool = False
    vat_frequency: Optional[VatFrequency] = None
    has_employees: bool = False
    email: str
    status: ClientStatus = ClientStatus.ACTIVE


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    subject_type: Optional[SubjectType] = None
    vat_payer: Optional[bool] = None
    vat_frequency: Optional[VatFrequency] = None
    has_employees: Optional[bool] = None
    email: Optional[str] = None
    status: Optional[ClientStatus] = None


class ClientResponse(BaseModel):
    id: int
    name: str
    ico: str
    subject_type: str
    vat_payer: bool
    vat_frequency: Optional[str]
    has_employees: bool
    email: str
    status: str
    created_at: str
    updated_at: str
    obligations_count: int = 0
    upcoming_count: int = 0

    class Config:
        from_attributes = True


def _client_to_response(client: Client, db: Session) -> dict:
    total = db.query(ClientObligation).filter(ClientObligation.client_id == client.id).count()
    upcoming = (
        db.query(ClientObligation)
        .join(CalendarEntry)
        .filter(
            ClientObligation.client_id == client.id,
            CalendarEntry.deadline_date >= date.today(),
        )
        .count()
    )
    return {
        "id": client.id,
        "name": client.name,
        "ico": client.ico,
        "subject_type": client.subject_type.value,
        "vat_payer": client.vat_payer,
        "vat_frequency": client.vat_frequency.value if client.vat_frequency else None,
        "has_employees": client.has_employees,
        "email": client.email,
        "status": client.status.value,
        "created_at": client.created_at.isoformat() if client.created_at else "",
        "updated_at": client.updated_at.isoformat() if client.updated_at else "",
        "obligations_count": total,
        "upcoming_count": upcoming,
    }


@router.get("")
def list_clients(
    status: Optional[str] = None,
    subject_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Client)
    if status:
        query = query.filter(Client.status == status)
    if subject_type:
        query = query.filter(Client.subject_type == subject_type)
    if search:
        query = query.filter(Client.name.ilike(f"%{search}%"))
    clients = query.order_by(Client.name).all()
    return [_client_to_response(c, db) for c in clients]


@router.get("/{client_id}")
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return _client_to_response(client, db)


@router.post("", status_code=201)
def create_client(data: ClientCreate, db: Session = Depends(get_db)):
    existing = db.query(Client).filter(Client.ico == data.ico).first()
    if existing:
        raise HTTPException(status_code=400, detail="Client with this ICO already exists")
    client = Client(**data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    recalculate_obligations(db, client.id)
    return _client_to_response(client, db)


@router.put("/{client_id}")
def update_client(client_id: int, data: ClientUpdate, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(client, key, value)
    db.commit()
    db.refresh(client)
    recalculate_obligations(db, client.id)
    return _client_to_response(client, db)


@router.get("/{client_id}/obligations")
def get_client_obligations(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    obligations = (
        db.query(ClientObligation)
        .join(CalendarEntry)
        .filter(ClientObligation.client_id == client_id)
        .order_by(CalendarEntry.deadline_date)
        .all()
    )
    return [
        {
            "id": o.id,
            "title": o.calendar_entry.title,
            "description": o.calendar_entry.description,
            "obligation_type": o.calendar_entry.obligation_type,
            "deadline_date": o.calendar_entry.deadline_date.isoformat(),
            "status": o.status.value,
        }
        for o in obligations
    ]
