import os

from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "xiaomi/mimo-v2.5")

EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "perplexity/pplx-embed-v1-0.6b")
CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "app/data/chroma")
CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "observe_kb")
DATA_DIR: str = os.getenv("DATA_DIR", "data")
