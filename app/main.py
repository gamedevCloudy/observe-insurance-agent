from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.core.logging import RequestIDMiddleware, configure_logging
from app.routes import call_logs, chat, claims, customers, escalations, health, llm_health, policies, voice

configure_logging()

app = FastAPI(title="Obvserve Insurance Support")
app.add_middleware(RequestIDMiddleware)

_STATIC = Path(__file__).resolve().parent.parent / "static" / "voice.html"


@app.get("/", include_in_schema=False)
async def root_page():
    return FileResponse(_STATIC)


app.include_router(health.router)
app.include_router(llm_health.router)
app.include_router(customers.router)
app.include_router(policies.router)
app.include_router(claims.router)
app.include_router(call_logs.router)
app.include_router(escalations.router)
app.include_router(chat.router)
app.include_router(voice.router)
