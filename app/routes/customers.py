from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Customer, Policy
from app.schemas import CustomerOut, PolicyOut

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/lookup", response_model=CustomerOut)
def lookup_customer(phone: str, db: Session = Depends(get_db)) -> Customer:
    customer = db.query(Customer).filter(Customer.contact == phone).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.get("/{cust_id}", response_model=CustomerOut)
def get_customer(cust_id: int, db: Session = Depends(get_db)) -> Customer:
    customer = db.query(Customer).filter(Customer.cust_id == cust_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.get("/{cust_id}/policies", response_model=list[PolicyOut])
def get_policies(cust_id: int, db: Session = Depends(get_db)) -> list[Policy]:
    return db.query(Policy).filter(Policy.cust_id == cust_id).all()
