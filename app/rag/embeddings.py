from langchain_core.embeddings import Embeddings
from openai import OpenAI

from app.core.config import EMBEDDING_MODEL, OPENROUTER_API_KEY

_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "https://observeinsurance.com",
        "X-OpenRouter-Title": "Observe Insurance Support Agent",
    },
)


class OpenRouterEmbeddings(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        resp = _client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts,
            encoding_format="float",
        )
        return [item.embedding for item in resp.data]

    def embed_query(self, text: str) -> list[float]:
        resp = _client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=[text],
            encoding_format="float",
        )
        return resp.data[0].embedding


def get_embeddings() -> OpenRouterEmbeddings:
    return OpenRouterEmbeddings()
