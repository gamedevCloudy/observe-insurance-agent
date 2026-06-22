from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import EscalationLog
from app.schemas import EscalationLogCreate, EscalationLogOut

router = APIRouter(prefix="/escalations", tags=["escalations"])


@router.post("/", response_model=EscalationLogOut, status_code=201)
def create_escalation(body: EscalationLogCreate, db: Session = Depends(get_db)) -> EscalationLog:
    log = EscalationLog(**body.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/{esc_id}", response_model=EscalationLogOut)
def get_escalation(esc_id: int, db: Session = Depends(get_db)) -> EscalationLog:
    log = db.query(EscalationLog).filter(EscalationLog.esc_id == esc_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Escalation log not found")
    return log
