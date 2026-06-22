from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from app.core.config import OPENROUTER_API_KEY, TTS_MODEL, TTS_VOICE
from app.core.logging import get_logger

log = get_logger("observeai.tts")

_BASE_URL = "https://openrouter.ai/api/v1"

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(base_url=_BASE_URL, api_key=OPENROUTER_API_KEY)
    return _client


async def stream_speak(text: str) -> AsyncIterator[bytes]:
    """Stream PCM audio chunks for the given text via OpenRouter TTS."""
    if not text:
        return
    log.info("tts.start", chars=len(text))
    try:
        async with _get_client().audio.speech.with_streaming_response.create(
            model=TTS_MODEL,
            input=text,
            voice=TTS_VOICE,
            response_format="pcm",
        ) as response:
            async for chunk in response.iter_bytes():
                if chunk:
                    yield chunk
    finally:
        log.info("tts.end")


async def synthesize(text: str) -> bytes:
    """Non-streaming convenience wrapper returning the full PCM audio."""
    chunks = [c async for c in stream_speak(text)]
    return b"".join(chunks)
