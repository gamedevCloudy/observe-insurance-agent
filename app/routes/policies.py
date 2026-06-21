from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Claim, Policy
from app.schemas import ClaimOut, PolicyOut

router = APIRouter(prefix="/policies", tags=["policies"])


@router.get("/{policy_num}", response_model=PolicyOut)
def get_policy(policy_num: str, db: Session = Depends(get_db)) -> Policy:
    policy = db.query(Policy).filter(Policy.policy_num == policy_num).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.get("/{policy_num}/claims", response_model=list[ClaimOut])
def get_claims(policy_num: str, db: Session = Depends(get_db)) -> list[Claim]:
    return db.query(Claim).filter(Claim.policy_num == policy_num).all()
