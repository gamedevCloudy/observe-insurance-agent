from langchain_openrouter import ChatOpenRouter

from app.core.config import OPENROUTER_MODEL


def get_openrouter_client() -> ChatOpenRouter:
    return ChatOpenRouter(
        model=OPENROUTER_MODEL,
        temperature=0,
        max_retries=2,
    )


def ping_llm() -> str:
    client = get_openrouter_client()
    response = client.invoke("ping")
    return str(response.content)
