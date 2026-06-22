import asyncio
import json
from collections.abc import AsyncIterator
from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessageChunk, ToolMessage

from app.voice.events import ClosedEvent, DoneEvent, ThinkingEvent, TranscriptEvent
from app.voice.pipeline import agent_turn


def _chunk(text: str) -> AIMessageChunk:
    return AIMessageChunk(content=text)


def _tool(name: str, content: dict) -> ToolMessage:
    return ToolMessage(name=name, content=json.dumps(content), tool_call_id="1")


class _FakeAgent:
    def __init__(self, chunks):
        self._chunks = chunks

    async def aget_state(self, config):
        m = MagicMock()
        m.values = {"messages": []}
        return m

    def astream(self, _input, _config, stream_mode="messages"):
        chunks = self._chunks

        async def gen() -> AsyncIterator[tuple[object, dict]]:
            for c in chunks:
                yield c, {}

        return gen()


def _collect(items):
    events = [i for i in items if not isinstance(i, (bytes, bytearray))]
    audio = [bytes(i) for i in items if isinstance(i, (bytes, bytearray))]
    return events, audio


async def _fake_tts(text: str) -> AsyncIterator[bytes]:
    yield text.encode()


def test_happy_path():
    async def run():
        agent = _FakeAgent([_chunk("Hello there. How can I help?")])
        with patch("app.voice.pipeline.stream_speak", new=_fake_tts):
            out = [i async for i in agent_turn("hi", "t1", agent)]
        events, audio = _collect(out)
        assert isinstance(events[0], TranscriptEvent)
        assert events[0].text == "hi"
        assert any(isinstance(e, DoneEvent) for e in events)
        assert b"".join(audio) == b"Hello there.How can I help?"

    asyncio.run(run())


def test_empty_transcript_returns_done():
    async def run():
        agent = _FakeAgent([])
        out = [i async for i in agent_turn("", "t1", agent)]
        events, _ = _collect(out)
        assert len(events) == 1
        assert isinstance(events[0], DoneEvent)

    asyncio.run(run())


def test_emergency_closes_and_skips_remaining_tts():
    async def run():
        agent = _FakeAgent([
            _chunk("Transferring you now."),
            _tool("escalate", {"chat_closed": True, "status": "escalated"}),
        ])
        with patch("app.voice.pipeline.stream_speak", new=_fake_tts):
            out = [i async for i in agent_turn("emergency", "t1", agent)]
        events, audio = _collect(out)
        assert any(isinstance(e, ClosedEvent) for e in events)
        assert b"".join(audio) == b"Transferring you now."

    asyncio.run(run())


def test_thinking_event_emitted_on_tool_message():
    async def run():
        agent = _FakeAgent([
            _chunk("Let me check."),
            _tool("lookup_customer_by_phone", {"cust_id": 1}),
            _chunk("Found it."),
        ])
        with patch("app.voice.pipeline.stream_speak", new=_fake_tts):
            out = [i async for i in agent_turn("lookup", "t1", agent)]
        events, _ = _collect(out)
        assert any(isinstance(e, ThinkingEvent) for e in events)

    asyncio.run(run())
