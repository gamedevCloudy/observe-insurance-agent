from app.agents.call_agent.tools.escalation import escalate
from app.db import database
from app.db.models import EscalationLog


def test_escalate_valid_reason():
    result = escalate.invoke({"reason": "ask-human-support"})
    assert result["status"] == "escalated"
    assert result["reason"] == "ask-human-support"
    assert result["chat_closed"] is False
    assert "representative" in result["message"].lower()


def test_escalate_emergency():
    result = escalate.invoke({"reason": "emergency"})
    assert result["status"] == "escalated"
    assert result["reason"] == "emergency"
    assert result["chat_closed"] is True


def test_escalate_invalid_reason():
    result = escalate.invoke({"reason": "invalid"})
    assert "error" in result


def test_escalate_persists_to_db():
    result = escalate.invoke({"reason": "ask-human-support", "cust_id": 1, "note": "Customer wants a rep"})
    assert "esc_id" in result

    with database.SessionLocal() as db:
        log = db.query(EscalationLog).filter_by(esc_id=result["esc_id"]).first()
        assert log is not None
        assert log.cust_id == 1
        assert log.reason == "ask-human-support"
        assert log.note == "Customer wants a rep"
        assert log.created_at is not None


def test_escalate_persists_emergency():
    result = escalate.invoke({"reason": "emergency", "note": "Caller injured"})
    assert result["chat_closed"] is True

    with database.SessionLocal() as db:
        log = db.query(EscalationLog).filter_by(esc_id=result["esc_id"]).first()
        assert log is not None
        assert log.reason == "emergency"
        assert log.note == "Caller injured"
        assert log.cust_id is None


def test_escalate_unknown_customer():
    result = escalate.invoke({"reason": "out-of-knowledge"})
    assert result["status"] == "escalated"

    with database.SessionLocal() as db:
        log = db.query(EscalationLog).filter_by(esc_id=result["esc_id"]).first()
        assert log is not None
        assert log.cust_id is None


def test_escalate_does_not_persist_on_invalid():
    result = escalate.invoke({"reason": "invalid"})
    assert "error" in result
    assert "esc_id" not in result
