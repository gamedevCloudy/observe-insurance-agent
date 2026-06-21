from fastapi import FastAPI

from app.routes import health, llm_health

app = FastAPI(title="Obvserve Insurance Support")

app.include_router(health.router)
app.include_router(llm_health.router)
