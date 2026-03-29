from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import MappingRule

router = APIRouter(prefix="/api/rules", tags=["rules"])


class RuleCreate(BaseModel):
    subject_type: Optional[str] = None
    vat_payer: Optional[bool] = None
    vat_frequency: Optional[str] = None
    has_employees: Optional[bool] = None
    obligation_type: str
    description: Optional[str] = None
    is_active: bool = True


class RuleUpdate(BaseModel):
    subject_type: Optional[str] = None
    vat_payer: Optional[bool] = None
    vat_frequency: Optional[str] = None
    has_employees: Optional[bool] = None
    obligation_type: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("")
def list_rules(db: Session = Depends(get_db)):
    rules = db.query(MappingRule).order_by(MappingRule.obligation_type).all()
    return [
        {
            "id": r.id,
            "subject_type": r.subject_type,
            "vat_payer": r.vat_payer,
            "vat_frequency": r.vat_frequency,
            "has_employees": r.has_employees,
            "obligation_type": r.obligation_type,
            "description": r.description,
            "is_active": r.is_active,
        }
        for r in rules
    ]


@router.post("", status_code=201)
def create_rule(data: RuleCreate, db: Session = Depends(get_db)):
    rule = MappingRule(**data.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return {"id": rule.id, **data.model_dump()}


@router.put("/{rule_id}")
def update_rule(rule_id: int, data: RuleUpdate, db: Session = Depends(get_db)):
    rule = db.query(MappingRule).filter(MappingRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(rule, key, value)
    db.commit()
    db.refresh(rule)
    return {
        "id": rule.id,
        "subject_type": rule.subject_type,
        "vat_payer": rule.vat_payer,
        "vat_frequency": rule.vat_frequency,
        "has_employees": rule.has_employees,
        "obligation_type": rule.obligation_type,
        "description": rule.description,
        "is_active": rule.is_active,
    }


@router.delete("/{rule_id}", status_code=204)
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(MappingRule).filter(MappingRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
