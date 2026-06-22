from fastapi import FastAPI

from app.core.logging import RequestIDMiddleware, configure_logging
from app.routes import call_logs, chat, claims, customers, escalations, health, llm_health, policies, voice

configure_logging()

app = FastAPI(title="Obvserve Insurance Support")
app.add_middleware(RequestIDMiddleware)

app.include_router(health.router)
app.include_router(llm_health.router)
app.include_router(customers.router)
app.include_router(policies.router)
app.include_router(claims.router)
app.include_router(call_logs.router)
app.include_router(escalations.router)
app.include_router(chat.router)
app.include_router(voice.router)
