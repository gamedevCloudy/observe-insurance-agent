import os

from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "xiaomi/mimo-v2.5")

EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "perplexity/pplx-embed-v1-0.6b")
CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "app/data/chroma")
CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "observe_kb")
DATA_DIR: str = os.getenv("DATA_DIR", "data")

DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY", "")
DEEPGRAM_MODEL: str = os.getenv("DEEPGRAM_MODEL", "flux-general-en")
DEEPGRAM_EOT_THRESHOLD: float = float(os.getenv("DEEPGRAM_EOT_THRESHOLD", "0.7"))
DEEPGRAM_EOT_TIMEOUT_MS: int = int(os.getenv("DEEPGRAM_EOT_TIMEOUT_MS", "5000"))

TTS_MODEL: str = os.getenv("TTS_MODEL", "x-ai/grok-voice-tts-1.0")
TTS_VOICE: str = os.getenv("TTS_VOICE", "Ara")
TTS_SAMPLE_RATE: int = int(os.getenv("TTS_SAMPLE_RATE", "24000"))
