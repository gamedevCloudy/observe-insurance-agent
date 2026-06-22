from datetime import datetime

from fastapi import HTTPException
from langchain_core.tools import tool

from app.db import database
from app.db.models import ESCALATION_REASONS
from app.routes import escalations as escalations_route
from app.schemas import EscalationLogCreate, EscalationLogOut


@tool
def escalate(reason: str, cust_id: int = 0, note: str = "") -> dict:
    """Escalate the call to a human representative. reason: one of 'ask-human-support', 'out-of-knowledge', 'emergency'. Pass cust_id if the customer has been identified, and note with relevant context."""
    if reason not in ESCALATION_REASONS:
        return {"error": f"Invalid reason '{reason}'. Must be one of: {', '.join(sorted(ESCALATION_REASONS))}"}

    created_at = datetime.now().isoformat()
    with database.SessionLocal() as db:
        try:
            body = EscalationLogCreate(
                cust_id=cust_id or None,
                reason=reason,
                note=note,
                created_at=created_at,
            )
            log = escalations_route.create_escalation(body, db)
        except HTTPException as e:
            return {"error": e.detail}
        result = EscalationLogOut.model_validate(log).model_dump()

    chat_closed = reason == "emergency"
    result["status"] = "escalated"
    result["chat_closed"] = chat_closed
    result["message"] = "I'm transferring you to a representative now. Please hold."
    return result
