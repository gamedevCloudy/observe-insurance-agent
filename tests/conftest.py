import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import database
from app.db.models import CallLog, Claim, Customer, Policy


@pytest.fixture(autouse=True)
def _test_db(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    TestSession = sessionmaker(bind=engine)

    from app.db.database import Base
    Base.metadata.create_all(bind=engine)

    db = TestSession()
    db.add_all([
        Customer(cust_id=1, cust_name="Alice Johnson", contact="555-0101",
                 addr="123 Main St, Springfield, IL", email="alice@example.com"),
        Customer(cust_id=2, cust_name="Bob Smith", contact="555-0202",
                 addr="456 Oak Ave, Denver, CO", email="bob@example.com"),
    ])
    db.add_all([
        Policy(policy_num="POL-001", cust_id=1, tier="gold", premium_status="paid", premium_amt=1200),
        Policy(policy_num="POL-002", cust_id=2, tier="silver", premium_status="due", premium_amt=800),
    ])
    db.add_all([
        Claim(claim_id=1, policy_num="POL-001", status="under_review", docs_required=True,
              description="Water damage from burst pipe", created_at="2026-05-15"),
        Claim(claim_id=2, policy_num="POL-002", status="approved", docs_required=False,
              description="Hail damage to roof", created_at="2026-04-20"),
    ])
    db.add(CallLog(call_id=1, cust_id=1, caller_name="Alice Johnson",
                   summary="Checked on claim status.", sentiment="neutral",
                   start_time="2026-06-21T10:00:00", end_time="2026-06-21T10:05:00", duration=300))
    db.commit()

    monkeypatch.setattr(database, "SessionLocal", TestSession)
    yield
    db.close()


@pytest.fixture(autouse=True)
def _reset_store():
    from app.agents.call_agent.memory import store
    yield
    store.put(("customer", "1"), "interactions", {})
    store.put(("customer", "2"), "interactions", {})
