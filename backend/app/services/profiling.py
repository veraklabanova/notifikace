"""M2 — Client Profile & Obligation Mapping."""
from sqlalchemy.orm import Session

from ..models import Client, MappingRule, ClientStatus
from .calendar_engine import compute_client_obligations


def recalculate_obligations(db: Session, client_id: int | None = None) -> int:
    """Recalculate obligations for a client or all clients."""
    return compute_client_obligations(db, client_id)


def get_client_obligation_types(db: Session, client: Client) -> list[str]:
    """Get list of obligation types applicable to a client based on mapping rules."""
    rules = db.query(MappingRule).filter(MappingRule.is_active == True).all()
    matched = []
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
        matched.append(rule.obligation_type)
    return matched
