from app.agents.call_agent.tools.claims import get_claim


def test_get_claim_found():
    result = get_claim.invoke({"claim_id": 1})
    assert result["claim_id"] == 1
    assert result["status"] == "under_review"
    assert result["docs_required"] is True


def test_get_claim_not_found():
    result = get_claim.invoke({"claim_id": 999})
    assert "error" in result
    assert result["error"] == "Claim not found"
