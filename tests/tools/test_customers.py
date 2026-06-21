from app.agents.call_agent.tools.customers import lookup_customer_by_phone, get_customer_policies


def test_lookup_customer_by_phone_found():
    result = lookup_customer_by_phone.invoke("555-0101")
    assert result["cust_name"] == "Alice Johnson"
    assert result["cust_id"] == 1
    assert result["contact"] == "555-0101"


def test_lookup_customer_by_phone_not_found():
    result = lookup_customer_by_phone.invoke("000-0000")
    assert "error" in result
    assert result["error"] == "Customer not found"


def test_get_customer_policies():
    result = get_customer_policies.invoke({"cust_id": 1})
    assert len(result) == 1
    assert result[0]["policy_num"] == "POL-001"
    assert result[0]["tier"] == "gold"


def test_get_customer_policies_empty():
    result = get_customer_policies.invoke({"cust_id": 999})
    assert result == []
