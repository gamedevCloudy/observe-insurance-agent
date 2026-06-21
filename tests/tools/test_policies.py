from app.agents.call_agent.tools.policies import get_policy, get_policy_claims


def test_get_policy_found():
    result = get_policy.invoke({"policy_num": "POL-001"})
    assert result["policy_num"] == "POL-001"
    assert result["tier"] == "gold"
    assert result["premium_status"] == "paid"


def test_get_policy_not_found():
    result = get_policy.invoke({"policy_num": "POL-999"})
    assert "error" in result


def test_get_policy_claims():
    result = get_policy_claims.invoke({"policy_num": "POL-001"})
    assert len(result) == 1
    assert result[0]["claim_id"] == 1
    assert result[0]["status"] == "under_review"


def test_get_policy_claims_empty():
    result = get_policy_claims.invoke({"policy_num": "POL-002"})
    assert len(result) == 1
    assert result[0]["status"] == "approved"
