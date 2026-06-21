from app.agents.call_agent.tools.sms import send_sms


def test_send_sms_claim_docs():
    result = send_sms.invoke({"sms_type": "claim-docs"})
    assert result["status"] == "simulated"
    assert result["sms_type"] == "claim-docs"
    assert "email" in result["message"].lower()


def test_send_sms_invalid_type():
    result = send_sms.invoke({"sms_type": "marketing"})
    assert "error" in result
