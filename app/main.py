from fastapi import FastAPI

from app.routes import claims, customers, health, llm_health, policies, call_logs

app = FastAPI(title="Obvserve Insurance Support")

app.include_router(health.router)
app.include_router(llm_health.router)
app.include_router(customers.router)
app.include_router(policies.router)
app.include_router(claims.router)
app.include_router(call_logs.router)
