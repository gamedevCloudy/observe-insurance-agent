import json
import re
from collections.abc import AsyncIterator
from typing import Union

from langchain_core.messages import HumanMessage, ToolMessage

from app.core.logging import get_logger
from app.voice.events import (
    ClosedEvent,
    DoneEvent,
    ErrorEvent,
    ThinkingEvent,
    TokenEvent,
    TranscriptEvent,
    VoiceEvent,
)
from app.voice.sanitize import for_tts
from app.voice.tts import stream_speak

log = get_logger("observeai.agent")

VoiceItem = Union[VoiceEvent, bytes]

_TERMINAL_RE = re.compile(r"[.!?]+(\s|$)")


def _split_sentence(buffer: str) -> tuple[str, str]:
    """Split off the first complete sentence (up to and including terminal punctuation)."""
    m = _TERMINAL_RE.search(buffer)
    if not m:
        return "", buffer
    end = m.end()
    return buffer[:end], buffer[end:]


def _tool_closed(msg: ToolMessage) -> bool:
    try:
        content = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
        return bool(content.get("chat_closed")) if isinstance(content, dict) else False
    except (json.JSONDecodeError, TypeError, AttributeError):
        return False


async def agent_turn(
    transcript: str,
    thread_id: str,
    agent,
) -> AsyncIterator[VoiceItem]:
    """Run one agent turn: transcript -> agent -> TTS. Yields VoiceEvent | bytes (audio)."""
    if not transcript:
        yield DoneEvent()
        return
    log.info("agent.turn.start", transcript=transcript[:80])
    yield TranscriptEvent(text=transcript)

    config = {"configurable": {"thread_id": thread_id}}
    state = await agent.aget_state(config)
    if _state_closed(state.values):
        log.info("agent.turn.end", escalated=True, tts=False)
        yield ClosedEvent(reason="emergency-escalation")
        return

    buffer = ""
    emergency = False
    tts_ran = False

    try:
        async for chunk, _metadata in agent.astream(
            {"messages": [HumanMessage(content=transcript)]},
            config,
            stream_mode="messages",
        ):
            kind = chunk.__class__.__name__
            if kind == "AIMessageChunk" and chunk.content:
                yield TokenEvent(content=chunk.content)
                buffer += chunk.content
                while True:
                    sentence, buffer = _split_sentence(buffer)
                    if not sentence:
                        break
                    tts_ran = True
                    async for audio_chunk in stream_speak(for_tts(sentence)):
                        yield audio_chunk
            elif kind == "ToolMessage":
                yield ThinkingEvent(name=chunk.name)
                log.info("tool.call", tool=chunk.name)
                if chunk.name == "escalate" and _tool_closed(chunk):
                    emergency = True
    except Exception as exc:
        log.error("agent.turn.error", error=str(exc))
        yield ErrorEvent(detail=f"agent: {exc}")
        return

    if emergency:
        log.info("agent.turn.end", escalated=True, tts=tts_ran)
        yield ClosedEvent(reason="emergency-escalation")
        return

    if buffer.strip():
        try:
            tts_ran = True
            async for audio_chunk in stream_speak(for_tts(buffer)):
                yield audio_chunk
        except Exception as exc:
            log.error("tts.error", error=str(exc))
            yield ErrorEvent(detail=f"tts: {exc}")
            return

    log.info("agent.turn.end", escalated=False, tts=tts_ran)
    yield DoneEvent()


def _state_closed(state_values: dict) -> bool:
    for msg in state_values.get("messages", []):
        if isinstance(msg, ToolMessage) and msg.name == "escalate" and _tool_closed(msg):
            return True
    return False
