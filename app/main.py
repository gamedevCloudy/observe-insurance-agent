from fastapi import FastAPI

from app.routes import health

app = FastAPI(title="Obvserve Insurance Support")

app.include_router(health.router)
