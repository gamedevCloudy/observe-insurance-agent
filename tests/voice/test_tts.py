import asyncio
from unittest.mock import patch

from app.voice import tts

def _fake_stream(chunks):
    class _Resp:
        def iter_bytes(self):
            return _aiter(chunks)

    class _Ctx:
        async def __aenter__(self):
            return _Resp()

        async def __aexit__(self, *exc):
            return False

    class _aiter:
        def __init__(self, chunks):
            self._chunks = chunks
            self._i = 0

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self._i >= len(self._chunks):
                raise StopAsyncIteration
            c = self._chunks[self._i]
            self._i += 1
            return c

    return _Ctx()


def test_stream_speak_empty_text_yields_nothing():
    async def run():
        async for _c in tts.stream_speak(""):
            pass

    asyncio.run(run())


def test_stream_speak_yields_pcm_chunks():
    async def run():
        with patch.object(tts, "_get_client") as mock_fn:
            mock_fn.return_value.audio.speech.with_streaming_response.create.return_value = _fake_stream(
                [b"pcm1", b"pcm2"]
            )
            out = [c async for c in tts.stream_speak("hello")]
        assert out == [b"pcm1", b"pcm2"]

    asyncio.run(run())


def test_synthesize_concatenates():
    async def run():
        with patch.object(tts, "_get_client") as mock_fn:
            mock_fn.return_value.audio.speech.with_streaming_response.create.return_value = _fake_stream(
                [b"ab", b"cd"]
            )
            out = await tts.synthesize("hi")
        assert out == b"abcd"

    asyncio.run(run())
