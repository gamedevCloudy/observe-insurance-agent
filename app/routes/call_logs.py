from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import CallLog
from app.schemas import CallLogCreate, CallLogOut

router = APIRouter(prefix="/call-logs", tags=["call-logs"])


@router.post("/", response_model=CallLogOut, status_code=201)
def create_call_log(body: CallLogCreate, db: Session = Depends(get_db)) -> CallLog:
    log = CallLog(**body.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/{call_id}", response_model=CallLogOut)
def get_call_log(call_id: int, db: Session = Depends(get_db)) -> CallLog:
    log = db.query(CallLog).filter(CallLog.call_id == call_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Call log not found")
    return log
