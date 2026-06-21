from fastapi import HTTPException
from langchain_core.tools import tool

from app.db.database import SessionLocal
from app.routes import policies as policies_route
from app.schemas import ClaimOut, PolicyOut


@tool
def get_policy(policy_num: str) -> dict:
    """Retrieve policy details by policy number (e.g. POL-001)."""
    with SessionLocal() as db:
        try:
            policy = policies_route.get_policy(policy_num, db)
        except HTTPException as e:
            return {"error": e.detail}
        return PolicyOut.model_validate(policy).model_dump()


@tool
def get_policy_claims(policy_num: str) -> list[dict]:
    """Retrieve all claims under a specific policy number."""
    with SessionLocal() as db:
        claims = policies_route.get_claims(policy_num, db)
        return [ClaimOut.model_validate(c).model_dump() for c in claims]
