from app.agents.call_agent.agent import build_agent
from app.agents.call_agent.tools import ALL_TOOLS


def test_build_agent_compiles():
    agent = build_agent()
    assert agent is not None


def test_agent_has_all_tools():
    tool_names = {t.name for t in ALL_TOOLS}
    assert len(tool_names) == 9
    expected = {
        "lookup_customer_by_phone",
        "get_customer_policies",
        "get_policy",
        "get_policy_claims",
        "get_claim",
        "create_call_log",
        "escalate",
        "faq_search",
        "send_sms",
    }
    assert tool_names == expected
