from app.agents.call_agent.tools.escalation import escalate


def test_escalate_valid_reason():
    result = escalate.invoke({"reason": "ask-human-support"})
    assert result["status"] == "escalated"
    assert "representative" in result["message"].lower()


def test_escalate_emergency():
    result = escalate.invoke({"reason": "emergency"})
    assert result["status"] == "escalated"
    assert result["reason"] == "emergency"


def test_escalate_invalid_reason():
    result = escalate.invoke({"reason": "invalid"})
    assert "error" in result
