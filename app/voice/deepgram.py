import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass

from deepgram import AsyncDeepgramClient
from deepgram.core.events import EventType

from app.core.config import (
    DEEPGRAM_API_KEY,
    DEEPGRAM_EOT_THRESHOLD,
    DEEPGRAM_EOT_TIMEOUT_MS,
    DEEPGRAM_MODEL,
)

_STOP = object()


@dataclass
class STTEvent:
    kind: str
    transcript: str = ""
    confidence: float = 0.0


class StreamingSTT:
    """Async wrapper over Deepgram Listen v2 (flux-general-en) for turn-based STT.

    Uses the SDK's callback API: MESSAGE events are pushed onto a queue and
    consumed via events(). start_listening() runs as a background task.
    """

    def __init__(self) -> None:
        self._client = AsyncDeepgramClient(api_key=DEEPGRAM_API_KEY)
        self._conn = None
        self._ctx = None
        self._queue: asyncio.Queue = asyncio.Queue()
        self._listen_task: asyncio.Task | None = None

    async def connect(self) -> None:
        self._ctx = self._client.listen.v2.connect(
            model=DEEPGRAM_MODEL,
            encoding="linear16",
            sample_rate=16000,
            eot_threshold=DEEPGRAM_EOT_THRESHOLD,
            eot_timeout_ms=DEEPGRAM_EOT_TIMEOUT_MS,
        )
        self._conn = await self._ctx.__aenter__()
        self._conn.on(EventType.MESSAGE, self._on_message)
        self._listen_task = asyncio.create_task(self._conn.start_listening())

    def _on_message(self, msg) -> None:
        event = getattr(msg, "event", None)
        transcript = getattr(msg, "transcript", "") or ""
        confidence = getattr(msg, "end_of_turn_confidence", 0.0) or 0.0
        if event == "StartOfTurn":
            self._queue.put_nowait(STTEvent(kind="start_of_turn"))
        elif event == "EndOfTurn":
            self._queue.put_nowait(STTEvent(kind="final", transcript=transcript, confidence=confidence))
        elif transcript:
            self._queue.put_nowait(STTEvent(kind="partial", transcript=transcript))

    async def send_media(self, pcm: bytes) -> None:
        if self._conn:
            await self._conn.send_media(pcm)

    async def events(self) -> AsyncIterator[STTEvent]:
        while True:
            item = await self._queue.get()
            if item is _STOP:
                return
            yield item

    async def close(self) -> None:
        if self._listen_task:
            self._listen_task.cancel()
            self._listen_task = None
        if self._ctx:
            await self._ctx.__aexit__(None, None, None)
            self._ctx = None
            self._conn = None
        self._queue.put_nowait(_STOP)
