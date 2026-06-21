from app.agents.call_agent.tools.call_logs import create_call_log
from app.agents.call_agent.memory import store


def test_create_call_log_success():
    result = create_call_log.invoke({
        "caller_name": "Test Caller",
        "summary": "Test summary",
        "sentiment": "positive",
        "start_time": "2026-06-21T12:00:00",
        "end_time": "2026-06-21T12:05:00",
        "duration": 300,
        "cust_id": 1,
    })
    assert result["caller_name"] == "Test Caller"
    assert result["sentiment"] == "positive"
    assert "call_id" in result


def test_create_call_log_unknown_customer():
    result = create_call_log.invoke({
        "caller_name": "Unknown Caller",
        "summary": "No ID provided",
        "sentiment": "neutral",
        "start_time": "2026-06-21T13:00:00",
        "end_time": "2026-06-21T13:02:00",
        "duration": 120,
        "cust_id": 0,
    })
    assert result["caller_name"] == "Unknown Caller"
    assert result["cust_id"] is None


def test_create_call_log_writes_memory():
    create_call_log.invoke({
        "caller_name": "Memory Test",
        "summary": "Checked on claim POL-001",
        "sentiment": "neutral",
        "start_time": "2026-06-21T14:00:00",
        "end_time": "2026-06-21T14:05:00",
        "duration": 300,
        "cust_id": 1,
    })
    mem = store.get(("customer", "1"), "interactions")
    assert mem is not None
    assert mem.value["summary"] == "Checked on claim POL-001"
