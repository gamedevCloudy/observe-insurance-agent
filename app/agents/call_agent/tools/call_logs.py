from datetime import datetime, timezone

from fastapi import HTTPException
from langchain_core.tools import tool
from langgraph.config import get_config

from app.db.database import SessionLocal
from app.routes import call_logs as call_logs_route
from app.schemas import CallLogCreate, CallLogOut

from app.agents.call_agent.memory import store


@tool
def create_call_log(
    caller_name: str,
    summary: str,
    sentiment: str,
    start_time: str = "",
    end_time: str = "",
    duration: int = 0,
    cust_id: int = 0,
) -> dict:
    """Write a post-call interaction record. Call this at the end of every conversation. cust_id is the customer's ID (0 if unknown)."""
    try:
        config = get_config()
        thread_id = config.get("configurable", {}).get("thread_id", "")
        if thread_id:
            session_meta = store.get(("session", thread_id), "meta")
            if session_meta and session_meta.value.get("started_at"):
                start_time = session_meta.value["started_at"]
                started_dt = datetime.fromisoformat(start_time)
                now_dt = datetime.now(timezone.utc)
                end_time = now_dt.isoformat()
                duration = max(0, int((now_dt - started_dt).total_seconds()))
    except Exception:
        pass

    with SessionLocal() as db:
        try:
            body = CallLogCreate(
                cust_id=cust_id or None,
                caller_name=caller_name,
                summary=summary,
                sentiment=sentiment,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
            )
            log = call_logs_route.create_call_log(body, db)
        except HTTPException as e:
            return {"error": e.detail}
        result = CallLogOut.model_validate(log).model_dump()

    if cust_id:
        store.put(("customer", str(cust_id)), "interactions", {"summary": summary, "sentiment": sentiment})
    return result
