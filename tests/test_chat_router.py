import json
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessageChunk, HumanMessage, ToolMessage

from app.main import app
from app.routes import chat

client = TestClient(app)


@pytest.fixture()
def _mock_agent(monkeypatch):
    async def fake_astream(messages, config, stream_mode="messages"):
        yield AIMessageChunk(content="Hello"), {}
        yield AIMessageChunk(content=" world"), {}

    async def fake_aget_state(config):
        mock_state = AsyncMock()
        mock_state.values = {"messages": [HumanMessage(content="hi")]}
        return mock_state

    mock = AsyncMock()
    mock.astream = fake_astream
    mock.aget_state = fake_aget_state
    monkeypatch.setattr(chat, "_agent", mock)


@pytest.fixture()
def _mock_agent_emergency(monkeypatch):
    escalate_result = json.dumps({
        "status": "escalated",
        "reason": "emergency",
        "esc_id": 1,
        "chat_closed": True,
        "message": "I'm transferring you to a representative now. Please hold.",
    })

    async def fake_astream(messages, config, stream_mode="messages"):
        yield AIMessageChunk(content="Transferring"), {}
        yield AIMessageChunk(content=" now."), {}
        yield ToolMessage(content=escalate_result, tool_call_id="tc1", name="escalate"), {}

    async def fake_aget_state(config):
        mock_state = AsyncMock()
        mock_state.values = {"messages": [HumanMessage(content="help")]}
        return mock_state

    mock = AsyncMock()
    mock.astream = fake_astream
    mock.aget_state = fake_aget_state
    monkeypatch.setattr(chat, "_agent", mock)


@pytest.fixture()
def _mock_agent_already_closed(monkeypatch):
    async def fake_astream(messages, config, stream_mode="messages"):
        yield AIMessageChunk(content="should not appear"), {}

    escalate_result = json.dumps({
        "status": "escalated",
        "reason": "emergency",
        "esc_id": 1,
        "chat_closed": True,
        "message": "I'm transferring you to a representative now. Please hold.",
    })

    async def fake_aget_state(config):
        mock_state = AsyncMock()
        mock_state.values = {
            "messages": [
                HumanMessage(content="help"),
                AIMessageChunk(content="Transferring now."),
                ToolMessage(content=escalate_result, tool_call_id="tc1", name="escalate"),
            ]
        }
        return mock_state

    mock = AsyncMock()
    mock.astream = fake_astream
    mock.aget_state = fake_aget_state
    monkeypatch.setattr(chat, "_agent", mock)


def test_chat_router_mounted():
    schema = app.openapi()
    assert "/chat/" in schema["paths"]


def test_chat_rejects_empty_message():
    resp = client.post("/chat/", json={"message": ""})
    assert resp.status_code == 422


def test_chat_generates_thread_id(_mock_agent):
    resp = client.post("/chat/", json={"message": "hi"})
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")

    lines = resp.text.strip().split("\n\n")
    assert lines[0].startswith("event: thread")
    thread_data = json.loads(lines[0].split("data: ", 1)[1])
    assert "thread_id" in thread_data
    assert len(thread_data["thread_id"]) == 36

    token_events = [e for e in lines if e.startswith("event: token")]
    contents = [json.loads(e.split("data: ", 1)[1])["content"] for e in token_events]
    assert contents == ["Hello", " world"]

    assert lines[-1].startswith("event: done")


def test_chat_reuses_thread_id(_mock_agent):
    resp = client.post("/chat/", json={"message": "hi", "thread_id": "abc-123"})
    assert resp.status_code == 200
    lines = resp.text.strip().split("\n\n")
    thread_data = json.loads(lines[0].split("data: ", 1)[1])
    assert thread_data["thread_id"] == "abc-123"


def test_chat_emits_closed_on_emergency_escalation(_mock_agent_emergency):
    resp = client.post("/chat/", json={"message": "help, I'm injured"})
    assert resp.status_code == 200

    lines = resp.text.strip().split("\n\n")
    closed_events = [e for e in lines if e.startswith("event: closed")]
    done_events = [e for e in lines if e.startswith("event: done")]
    assert len(closed_events) == 1
    assert len(done_events) == 0

    closed_data = json.loads(closed_events[0].split("data: ", 1)[1])
    assert closed_data["reason"] == "emergency-escalation"


def test_chat_refuses_turns_after_emergency_close(_mock_agent_already_closed):
    resp = client.post("/chat/", json={"message": "still here"})
    assert resp.status_code == 200

    lines = resp.text.strip().split("\n\n")
    token_events = [e for e in lines if e.startswith("event: token")]
    closed_events = [e for e in lines if e.startswith("event: closed")]
    assert len(token_events) == 0
    assert len(closed_events) == 1
