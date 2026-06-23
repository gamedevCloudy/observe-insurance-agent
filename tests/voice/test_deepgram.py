import asyncio
from unittest.mock import patch

from app.voice.deepgram import StreamingSTT


class _FakeConn:
    def __init__(self, messages):
        self._messages = messages
        self._sent: list[bytes] = []
        self._callbacks = {}
        self.closed = False

    def on(self, event, callback):
        self._callbacks[event] = callback

    async def start_listening(self):
        cb = self._callbacks.get("message")
        if cb:
            for m in self._messages:
                cb(m)

    async def send_media(self, pcm: bytes) -> None:
        self._sent.append(pcm)


class _FakeCtx:
    def __init__(self, conn):
        self._conn = conn

    async def __aenter__(self):
        return self._conn

    async def __aexit__(self, *exc):
        self._conn.closed = True
        return False


class _FakeV2:
    def __init__(self, messages):
        self._messages = messages

    def connect(self, **_kw):
        return _FakeCtx(_FakeConn(self._messages))


class _FakeClient:
    def __init__(self, messages):
        self.listen = type("L", (), {"v2": _FakeV2(messages)})()


async def _collect(stt: StreamingSTT) -> list:
    await asyncio.sleep(0)
    await stt.close()
    out = []
    async for e in stt.events():
        out.append(e)
    return out


def test_start_of_turn_and_end_of_turn_parsing():
    async def run():
        msgs = [
            {"event": "StartOfTurn"},
            {"event": "Update", "transcript": "hello"},
            {"event": "EndOfTurn", "transcript": "hello world", "end_of_turn_confidence": 0.9},
        ]
        with patch("app.voice.deepgram.AsyncDeepgramClient", lambda **k: _FakeClient(msgs)):
            stt = StreamingSTT()
            await stt.connect()
            out = await _collect(stt)
        assert [e.kind for e in out] == ["start_of_turn", "partial", "final"]
        assert out[2].transcript == "hello world"
        assert out[2].confidence == 0.9

    asyncio.run(run())


def test_partial_only_when_transcript_present():
    async def run():
        msgs = [{"event": "Update", "transcript": ""}, {"event": "Update", "transcript": "hi"}]
        with patch("app.voice.deepgram.AsyncDeepgramClient", lambda **k: _FakeClient(msgs)):
            stt = StreamingSTT()
            await stt.connect()
            out = await _collect(stt)
        assert [e.kind for e in out] == ["partial"]
        assert out[0].transcript == "hi"

    asyncio.run(run())


def test_send_media_forwards_bytes():
    async def run():
        msgs = []
        with patch("app.voice.deepgram.AsyncDeepgramClient", lambda **k: _FakeClient(msgs)):
            stt = StreamingSTT()
            await stt.connect()
            await stt.send_media(b"pcm1")
            await stt.send_media(b"pcm2")
            assert stt._conn is not None
            assert stt._conn._sent == [b"pcm1", b"pcm2"]

    asyncio.run(run())


def test_close_exits_context():
    async def run():
        msgs = []
        with patch("app.voice.deepgram.AsyncDeepgramClient", lambda **k: _FakeClient(msgs)):
            stt = StreamingSTT()
            await stt.connect()
            conn = stt._conn
            await stt.close()
        assert conn.closed  # ty: ignore[unresolved-attribute]
        assert stt._conn is None
        assert stt._ctx is None

    asyncio.run(run())


def test_events_without_connect_yields_nothing():
    async def run():
        stt = StreamingSTT()
        await stt.close()
        out = []
        async for e in stt.events():
            out.append(e)
        assert out == []

    asyncio.run(run())


def test_fatal_error_emits_error_event():
    async def run():
        msgs = [{"type": "Error", "description": "boom"}]
        with patch("app.voice.deepgram.AsyncDeepgramClient", lambda **k: _FakeClient(msgs)):
            stt = StreamingSTT()
            await stt.connect()
            out = await _collect(stt)
        assert [e.kind for e in out] == ["error"]
        assert "boom" in out[0].transcript

    asyncio.run(run())
