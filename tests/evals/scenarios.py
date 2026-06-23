"""Scenario definitions for LLM-as-judge agent evaluation."""

AUTH_SCENARIOS = [
    {
        "id": "auth-01",
        "category": "authentication",
        "description": "Valid phone number finds customer and confirms identity",
        "messages": [{"role": "user", "content": "Hi, my phone number is 555-0101, I need help with my claim."}],
        "criteria": [
            "Agent calls lookup_customer_by_phone to verify the caller",
            "Agent confirms the caller's identity by name (Alice Johnson)",
            "Agent offers to help or asks how they can assist after authentication",
        ],
    },
    {
        "id": "auth-02",
        "category": "authentication",
        "description": "Agent greets caller before asking for phone number",
        "messages": [{"role": "user", "content": "Hello?"}],
        "criteria": [
            "Agent responds with a greeting or warm welcome",
            "Agent asks for the phone number to look up the account",
        ],
    },
    {
        "id": "auth-03",
        "category": "authentication",
        "description": "Phone number not found — agent handles gracefully",
        "messages": [{"role": "user", "content": "My phone is 555-9999, can you look me up?"}],
        "criteria": [
            "Agent calls lookup_customer_by_phone with 555-9999",
            "Agent informs the caller they were not found (does not fabricate a name)",
            "Agent offers to connect to a representative or suggests alternative action",
        ],
    },
    {
        "id": "auth-04",
        "category": "authentication",
        "description": "Phone not found — agent does not proceed with claims",
        "messages": [{"role": "user", "content": "My number is 555-8888. What's the status of my claim?"}],
        "criteria": [
            "Agent attempts lookup_customer_by_phone",
            "Agent does NOT try to retrieve claim status for an unauthenticated caller",
            "Agent redirects to representative or explains they cannot proceed",
        ],
    },
    {
        "id": "auth-05",
        "category": "authentication",
        "description": "Bob Smith authenticates with valid phone 555-0202",
        "messages": [{"role": "user", "content": "This is Bob, my phone is 555-0202. I want to check my insurance."}],
        "criteria": [
            "Agent calls lookup_customer_by_phone with 555-0202",
            "Agent confirms identity as Bob Smith",
            "Agent asks how they can help or what they would like to check",
        ],
    },
    {
        "id": "auth-06",
        "category": "authentication",
        "description": "Customer with prior interaction history gets continuity",
        "messages": [{"role": "user", "content": "Hi, it's Alice at 555-0101. I called before about my claim."}],
        "criteria": [
            "Agent calls lookup_customer_by_phone",
            "Agent acknowledges the prior interaction or shows awareness of history",
        ],
    },
]

CLAIM_SCENARIOS = [
    {
        "id": "claim-01",
        "category": "claims",
        "description": "Alice checks her water damage claim — status under_review with docs required",
        "messages": [
            {"role": "user", "content": "My phone is 555-0101."},
            {"role": "user", "content": "What is the status of my claim?"},
        ],
        "criteria": [
            "Agent calls lookup_customer_by_phone and get_customer_policies",
            "Agent retrieves claim details and reports status as under_review",
            "Agent notes that documentation is required and offers to send SMS or instructions",
        ],
    },
    {
        "id": "claim-02",
        "category": "claims",
        "description": "Bob checks his hail damage claim — status approved, no docs required",
        "messages": [
            {"role": "user", "content": "I'm at 555-0202, name's Bob."},
            {"role": "user", "content": "Tell me about my claim."},
        ],
        "criteria": [
            "Agent calls lookup_customer_by_phone and get_customer_policies",
            "Agent retrieves claim and reports status as approved",
            "Agent does NOT offer to send documentation SMS (docs_required is false)",
        ],
    },
    {
        "id": "claim-03",
        "category": "claims",
        "description": "Documentation required triggers send_sms tool",
        "messages": [
            {"role": "user", "content": "Phone 555-0101. Alice here."},
            {"role": "user", "content": "I need to know what docs to submit for my claim."},
        ],
        "criteria": [
            "Agent identifies that docs are required for the claim",
            "Agent calls send_sms with sms_type claim-docs or provides document submission instructions",
            "Agent communicates next steps clearly to the caller",
        ],
    },
    {
        "id": "claim-04",
        "category": "claims",
        "description": "Agent uses tools to retrieve data — does not fabricate claim info",
        "messages": [
            {"role": "user", "content": "555-0101. What's my policy tier and claim amount?"},
        ],
        "criteria": [
            "Agent uses get_customer_policies and get_claim tools",
            "Agent reports actual policy tier (gold) and claim description from the database",
            "Agent does not make up any claim amounts or fabricated details",
        ],
    },
    {
        "id": "claim-05",
        "category": "claims",
        "description": "Customer asks about policy and claim in one turn",
        "messages": [
            {"role": "user", "content": "This is Bob, 555-0202. What's my plan and claim about?"},
        ],
        "criteria": [
            "Agent looks up customer by phone",
            "Agent retrieves policies and claims for Bob",
            "Agent reports silver tier plan and hail damage claim accurately",
        ],
    },
]

FAQ_SCENARIOS = [
    {
        "id": "faq-01",
        "category": "faq",
        "description": "Customer asks about office hours — agent searches knowledge base",
        "messages": [
            {"role": "user", "content": "555-0101."},
            {"role": "user", "content": "What are your office hours?"},
        ],
        "criteria": [
            "Agent authenticates the customer",
            "Agent calls faq_search with a query about office hours",
            "Agent provides accurate office hours from the knowledge base (Mon-Fri 8AM-6PM ET)",
        ],
    },
    {
        "id": "faq-02",
        "category": "faq",
        "description": "Customer asks for mailing address — agent provides relevant regional info",
        "messages": [
            {"role": "user", "content": "555-0101"},
            {"role": "user", "content": "Where do I mail documents? I'm in Illinois."},
        ],
        "criteria": [
            "Agent authenticates the customer",
            "Agent calls faq_search about mailing address",
            "Agent provides the Midwest district mailing address (Chicago) since customer is in Illinois",
        ],
    },
    {
        "id": "faq-03",
        "category": "faq",
        "description": "Customer asks how to start a new claim",
        "messages": [
            {"role": "user", "content": "555-0202 Bob"},
            {"role": "user", "content": "How do I file a new claim?"},
        ],
        "criteria": [
            "Agent authenticates",
            "Agent calls faq_search about starting a new claim",
            "Agent provides steps: call hotline, file online, use app, or contact agent",
        ],
    },
    {
        "id": "faq-04",
        "category": "faq",
        "description": "Customer asks about general claims process timeline",
        "messages": [
            {"role": "user", "content": "555-0101"},
            {"role": "user", "content": "How long does the whole claims process take?"},
        ],
        "criteria": [
            "Agent authenticates",
            "Agent calls faq_search about claims process timeline",
            "Agent provides timeline of 10-15 business days for standard claims",
        ],
    },
    {
        "id": "faq-05",
        "category": "faq",
        "description": "Customer asks unrelated question — knowledge base has no answer",
        "messages": [
            {"role": "user", "content": "555-0101"},
            {"role": "user", "content": "What's the best recipe for chocolate cake?"},
        ],
        "criteria": [
            "Agent authenticates",
            "Agent calls faq_search but finds no relevant results",
            "Agent politely explains the topic is outside their knowledge and offers to connect to a representative",
        ],
    },
]

ESCALATION_SCENARIOS = [
    {
        "id": "esc-01",
        "category": "escalation",
        "description": "Caller asks for a human representative — agent escalates",
        "messages": [
            {"role": "user", "content": "555-0101"},
            {"role": "user", "content": "I want to speak to a real person."},
        ],
        "criteria": [
            "Agent authenticates the customer",
            "Agent calls escalate with reason ask-human-support",
            "Agent informs the caller they are being transferred",
        ],
    },
    {
        "id": "esc-02",
        "category": "escalation",
        "description": "Caller uses keyword 'operator' — agent escalates",
        "messages": [
            {"role": "user", "content": "555-0202"},
            {"role": "user", "content": "Get me an operator right now."},
        ],
        "criteria": [
            "Agent authenticates",
            "Agent calls escalate with reason ask-human-support",
            "Agent message indicates transfer to human",
        ],
    },
    {
        "id": "esc-03",
        "category": "escalation",
        "description": "Emergency situation — agent escalates with emergency reason and closes chat",
        "messages": [
            {"role": "user", "content": "555-0101"},
            {"role": "user", "content": "I just had a bad car accident and I'm injured!"},
        ],
        "criteria": [
            "Agent identifies this as an emergency",
            "Agent calls escalate with reason emergency",
            "Agent gives a brief transfer message and does NOT ask further questions",
        ],
    },
    {
        "id": "esc-04",
        "category": "escalation",
        "description": "Completely unrelated question — agent escalates as out-of-knowledge",
        "messages": [
            {"role": "user", "content": "555-0202"},
            {"role": "user", "content": "What's the score of the Lakers game?"},
        ],
        "criteria": [
            "Agent authenticates the customer",
            "Agent calls escalate with reason out-of-knowledge (or refuses to answer sports questions)",
            "Agent redirects to insurance-related topics or offers representative",
        ],
    },
    {
        "id": "esc-05",
        "category": "escalation",
        "description": "Emergency escalation persists to database",
        "messages": [
            {"role": "user", "content": "555-0101"},
            {"role": "user", "content": "My house is on fire right now, I need help!"},
        ],
        "criteria": [
            "Agent authenticates",
            "Agent calls escalate with reason emergency",
            "Agent provides transfer message and stops the interaction",
        ],
    },
    {
        "id": "esc-06",
        "category": "escalation",
        "description": "Caller is frustrated — agent remains empathetic and offers escalation",
        "messages": [
            {"role": "user", "content": "555-0101"},
            {"role": "user", "content": "This is ridiculous, I've been waiting forever. Just get me a manager!"},
        ],
        "criteria": [
            "Agent acknowledges the caller's frustration with empathy",
            "Agent calls escalate with reason ask-human-support",
            "Agent confirms transfer to a manager or representative",
        ],
    },
]

CALL_LOG_SCENARIOS = [
    {
        "id": "log-01",
        "category": "call_log",
        "description": "Agent creates call log at end of interaction",
        "messages": [
            {"role": "user", "content": "555-0101. Alice."},
            {"role": "user", "content": "Thanks that answered my question. Bye!"},
        ],
        "criteria": [
            "Agent authenticates the customer",
            "Agent responds to the customer's closing message",
            "Agent calls create_call_log with caller_name Alice Johnson",
        ],
    },
    {
        "id": "log-02",
        "category": "call_log",
        "description": "Call log includes summary and sentiment",
        "messages": [
            {"role": "user", "content": "555-0202 Bob. Just wanted to confirm my claim is approved. Thanks, that's great news. Goodbye!"},
        ],
        "criteria": [
            "Agent authenticates and retrieves claim info",
            "Agent calls create_call_log",
            "Call log includes a summary of the interaction and a sentiment (positive)",
        ],
    },
    {
        "id": "log-03",
        "category": "call_log",
        "description": "Call log for unauthenticated caller (cust_id=0 scenario)",
        "messages": [
            {"role": "user", "content": "Hi, I don't have my policy number handy. Can you just tell me about insurance plans?"},
        ],
        "criteria": [
            "Agent asks for phone number to authenticate",
            "If authentication fails or caller refuses, agent still attempts to help within bounds",
        ],
    },
    {
        "id": "log-04",
        "category": "call_log",
        "description": "Call log stores interaction in memory for future sessions",
        "messages": [
            {"role": "user", "content": "555-0101 Alice. Can you confirm my claim is under review? OK thanks, bye."},
        ],
        "criteria": [
            "Agent authenticates and retrieves claim status",
            "Agent calls create_call_log with appropriate summary and sentiment",
            "Agent concludes the interaction professionally",
        ],
    },
]

MULTITURN_SCENARIOS = [
    {
        "id": "multi-01",
        "category": "multiturn",
        "description": "Full happy path: greet → auth → claim inquiry → docs SMS → completion",
        "messages": [
            {"role": "user", "content": "Hello?"},
            {"role": "user", "content": "My phone number is 555-0101."},
            {"role": "user", "content": "I want to check my claim status."},
            {"role": "user", "content": "Yes, please send me the document instructions."},
            {"role": "user", "content": "Thank you, that's all I needed. Goodbye."},
        ],
        "criteria": [
            "Agent greets and asks for phone number",
            "Agent authenticates Alice Johnson",
            "Agent retrieves claim — water damage, under_review, docs required",
            "Agent sends SMS with claim-docs instructions",
            "Agent creates a call log at the end",
        ],
    },
    {
        "id": "multi-02",
        "category": "multiturn",
        "description": "Agent retains context across multiple turns",
        "messages": [
            {"role": "user", "content": "Hi, I'm at 555-0202. What's my name in your system?"},
            {"role": "user", "content": "OK and what plan do I have?"},
            {"role": "user", "content": "And what's the status of that plan's claim?"},
        ],
        "criteria": [
            "Agent authenticates Bob Smith by phone",
            "Agent retrieves policy info (silver plan) without re-looking up the customer",
            "Agent retrieves claim info (hail damage, approved) using stored context",
        ],
    },
    {
        "id": "multi-03",
        "category": "multiturn",
        "description": "Agent handles FAQ question mid-conversation and returns to claim discussion",
        "messages": [
            {"role": "user", "content": "555-0101 Alice here. What's my claim about?"},
            {"role": "user", "content": "Also, by the way, what are your office hours?"},
            {"role": "user", "content": "Thanks. So my claim is still being reviewed?"},
        ],
        "criteria": [
            "Agent authenticates Alice and retrieves claim",
            "Agent handles the FAQ question about office hours using faq_search",
            "Agent returns to the claim context and confirms under_review status",
        ],
    },
]

EDGE_SCENARIOS = [
    {
        "id": "edge-01",
        "category": "edge_cases",
        "description": "Agent does not share one customer's data with another",
        "messages": [
            {"role": "user", "content": "555-0101"},
            {"role": "user", "content": "Tell me about Bob Smith's policy."},
        ],
        "criteria": [
            "Agent authenticates as Alice",
            "Agent refuses to share Bob's data or explains they can only access the authenticated customer's info",
            "Agent does NOT call tools to look up Bob's policy for Alice",
        ],
    },
    {
        "id": "edge-02",
        "category": "edge_cases",
        "description": "Agent does not provide legal or medical advice",
        "messages": [
            {"role": "user", "content": "555-0101"},
            {"role": "user", "content": "Do you think I should sue my neighbor for the water damage?"},
        ],
        "criteria": [
            "Agent authenticates Alice",
            "Agent declines to give legal advice",
        ],
    },
    {
        "id": "edge-03",
        "category": "edge_cases",
        "description": "Agent output is TTS-friendly — no markdown or special characters",
        "messages": [
            {"role": "user", "content": "555-0101. What's my claim status?"},
        ],
        "criteria": [
            "Agent retrieves and reports claim status",
            "Agent response does not contain markdown characters like **, *, #, [], or emojis",
        ],
    },
    {
        "id": "edge-04",
        "category": "edge_cases",
        "description": "Agent handles repeated question by escalating rather than looping",
        "messages": [
            {"role": "user", "content": "555-0101. I want to speak to someone."},
            {"role": "user", "content": "I said I want to speak to someone!"},
            {"role": "user", "content": "Why aren't you transferring me?"},
        ],
        "criteria": [
            "Agent authenticates Alice",
            "Agent escalates with ask-human-support on first or second request",
            "Agent does not loop — if escalation already requested, agent acknowledges and confirms transfer",
        ],
    },
]

ALL_SCENARIOS = (
    AUTH_SCENARIOS
    + CLAIM_SCENARIOS
    + FAQ_SCENARIOS
    + ESCALATION_SCENARIOS
    + CALL_LOG_SCENARIOS
    + MULTITURN_SCENARIOS
    + EDGE_SCENARIOS
)
