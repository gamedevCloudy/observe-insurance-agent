from sqlalchemy.orm import Session

from app.db.models import CallLog, Claim, Customer, Policy

CUSTOMERS = [
    Customer(
        cust_id=1,
        cust_name="Alice Johnson",
        contact="555-0101",
        addr="123 Main St, Springfield, IL",
        email="alice@example.com",
    ),
    Customer(
        cust_id=2,
        cust_name="Bob Smith",
        contact="555-0202",
        addr="456 Oak Ave, Denver, CO",
        email="bob@example.com",
    ),
]

POLICIES = [
    Policy(
        policy_num="POL-001",
        cust_id=1,
        tier="gold",
        premium_status="paid",
        premium_amt=1200,
    ),
    Policy(
        policy_num="POL-002",
        cust_id=2,
        tier="silver",
        premium_status="due",
        premium_amt=800,
    ),
]

CLAIMS = [
    Claim(
        claim_id=1,
        policy_num="POL-001",
        status="under_review",
        docs_required=True,
        description="Water damage from burst pipe",
        created_at="2026-05-15",
    ),
    Claim(
        claim_id=2,
        policy_num="POL-002",
        status="approved",
        docs_required=False,
        description="Hail damage to roof",
        created_at="2026-04-20",
    ),
]

CALL_LOGS = [
    CallLog(
        call_id=1,
        cust_id=1,
        caller_name="Alice Johnson",
        summary="Caller checked on claim status, docs required for water damage claim.",
        sentiment="neutral",
        start_time="2026-06-21T10:00:00",
        end_time="2026-06-21T10:05:00",
        duration=300,
    ),
]


def seed(db: Session) -> None:
    if db.query(Customer).first() is not None:
        return
    db.add_all(CUSTOMERS)
    db.add_all(POLICIES)
    db.add_all(CLAIMS)
    db.add_all(CALL_LOGS)
    db.commit()
