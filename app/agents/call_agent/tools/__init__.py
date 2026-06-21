from app.agents.call_agent.tools.customers import get_customer_policies, lookup_customer_by_phone
from app.agents.call_agent.tools.policies import get_policy, get_policy_claims
from app.agents.call_agent.tools.claims import get_claim
from app.agents.call_agent.tools.call_logs import create_call_log
from app.agents.call_agent.tools.escalation import escalate
from app.agents.call_agent.tools.faq import faq_search
from app.agents.call_agent.tools.sms import send_sms

ALL_TOOLS = [
    lookup_customer_by_phone,
    get_customer_policies,
    get_policy,
    get_policy_claims,
    get_claim,
    create_call_log,
    escalate,
    faq_search,
    send_sms,
]
