from fastapi import APIRouter, HTTPException

from app.core.config import OPENROUTER_MODEL
from app.llm.openrouter import ping_llm

router = APIRouter()


@router.get("/llm-health")
def llm_health() -> dict[str, str]:
    try:
        response = ping_llm()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"LLM ping failed: {exc}",
        ) from exc
    return {
        "status": "ok",
        "model": OPENROUTER_MODEL,
        "llm_response": response,
    }
