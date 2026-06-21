from fastapi import HTTPException
from langchain_core.tools import tool

from app.db.database import SessionLocal
from app.routes import claims as claims_route
from app.schemas import ClaimOut


@tool
def get_claim(claim_id: int) -> dict:
    """Retrieve a specific claim by its claim ID."""
    with SessionLocal() as db:
        try:
            claim = claims_route.get_claim(claim_id, db)
        except HTTPException as e:
            return {"error": e.detail}
        return ClaimOut.model_validate(claim).model_dump()
