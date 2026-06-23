import json
from collections.abc import AsyncIterator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessageChunk

from app.main import app
from app.routes import voice

client = TestClient(app)


async def _fake_tts(text: str):
    yield text.encode()


def _fake_agent(chunks):
    agent = MagicMock()

    async def fake_astream(_messages, _config, stream_mode="messages"):
        for c in chunks:
            yield c, {}

    async def fake_aget_state(_config):
        m = MagicMock()
        m.values = {"messages": []}
        return m

    agent.astream = fake_astream
    agent.aget_state = fake_aget_state
    return agent


class _FakeSTT:
    def __init__(self, events):
        self._events = events
        self.sent: list[bytes] = []
        self.closed = False

    async def connect(self):
        pass

    async def send_media(self, pcm: bytes):
        self.sent.append(pcm)

    async def events(self) -> AsyncIterator:
        for e in self._events:
            yield e

    async def close(self):
        self.closed = True


@pytest.fixture()
def _mock_voice(monkeypatch):
    monkeypatch.setattr(voice, "_agent", _fake_agent([AIMessageChunk(content="Hello there.")]))
    monkeypatch.setattr("app.voice.pipeline.stream_speak", _fake_tts)
    monkeypatch.setattr("app.routes.voice.StreamingSTT", lambda: _FakeSTT(_scripted_events()))


@pytest.fixture()
def _mock_voice_text(monkeypatch):
    monkeypatch.setattr(voice, "_agent", _fake_agent([AIMessageChunk(content="Hello there.")]))
    monkeypatch.setattr("app.voice.pipeline.stream_speak", _fake_tts)
    monkeypatch.setattr("app.routes.voice.StreamingSTT", lambda: _FakeSTT([]))


def _scripted_events():
    from app.voice.deepgram import STTEvent

    return [
        STTEvent(kind="start_of_turn"),
        STTEvent(kind="partial", transcript="hel"),
        STTEvent(kind="final", transcript="hello", confidence=0.9),
    ]


def _error_then_final_events():
    from app.voice.deepgram import STTEvent

    return [
        STTEvent(kind="error", transcript="INTERNAL_SERVER_ERROR: boom"),
        STTEvent(kind="final", transcript="hi", confidence=0.9),
    ]


@pytest.fixture()
def _mock_voice_error(monkeypatch):
    monkeypatch.setattr(voice, "_agent", _fake_agent([AIMessageChunk(content="ok.")]))
    monkeypatch.setattr("app.voice.pipeline.stream_speak", _fake_tts)
    monkeypatch.setattr("app.routes.voice.StreamingSTT", lambda: _FakeSTT(_error_then_final_events()))


def _collect_ws(ws):
    events = []
    audio = b""
    while True:
        msg = ws.receive()
        if msg.get("bytes"):
            audio += msg["bytes"]
        elif msg.get("text"):
            payload = json.loads(msg["text"])
            events.append(payload)
            if payload.get("type") in ("done", "closed"):
                break
    return events, audio


def test_voice_router_mounted():
    paths = {getattr(r, "path", "") for r in voice.router.routes}
    assert "/voice/ws" in paths
    assert "/voice/" in paths


def test_voice_ws_happy_path(_mock_voice):
    with client.websocket_connect("/voice/ws") as ws:
        ws.send_bytes(b"pcm1")
        ws.send_bytes(b"pcm2")
        events, audio = _collect_ws(ws)

    types = [e["type"] for e in events]
    assert "start_of_turn" in types
    assert "partial" in types
    assert "transcript" in types
    assert types[-1] == "done"
    assert audio == b"Hello there."


def test_voice_ws_text_input_sends_start_of_turn(_mock_voice_text):
    with client.websocket_connect("/voice/ws") as ws:
        ws.send_text(json.dumps({"type": "text", "content": "hello"}))
        events, audio = _collect_ws(ws)

    types = [e["type"] for e in events]
    assert "start_of_turn" in types
    assert "transcript" in types
    assert types[-1] == "done"
    assert audio == b"Hello there."


def test_voice_ws_forwards_stt_error(_mock_voice_error):
    with client.websocket_connect("/voice/ws") as ws:
        events, _ = _collect_ws(ws)

    types = [e["type"] for e in events]
    assert "error" in types
    err = next(e for e in events if e["type"] == "error")
    assert "INTERNAL_SERVER_ERROR" in err["detail"]
    assert types[-1] == "done"
