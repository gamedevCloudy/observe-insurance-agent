from pydantic import BaseModel, Field


class CustomerOut(BaseModel):
    cust_id: int
    cust_name: str
    contact: str
    addr: str
    email: str

    model_config = {"from_attributes": True}


class PolicyOut(BaseModel):
    policy_num: str
    cust_id: int
    tier: str
    premium_status: str
    premium_amt: int

    model_config = {"from_attributes": True}


class ClaimOut(BaseModel):
    claim_id: int
    policy_num: str
    status: str
    docs_required: bool
    description: str
    created_at: str

    model_config = {"from_attributes": True}


class CallLogCreate(BaseModel):
    cust_id: int | None = None
    caller_name: str
    summary: str
    sentiment: str
    start_time: str
    end_time: str
    duration: int


class CallLogOut(BaseModel):
    call_id: int
    cust_id: int | None
    caller_name: str
    summary: str
    sentiment: str
    start_time: str
    end_time: str
    duration: int

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    thread_id: str | None = None


class EscalationLogCreate(BaseModel):
    cust_id: int | None = None
    reason: str
    note: str = ""
    created_at: str


class EscalationLogOut(BaseModel):
    esc_id: int
    cust_id: int | None
    reason: str
    note: str
    created_at: str

    model_config = {"from_attributes": True}
