from fastapi import HTTPException
from langchain_core.tools import tool

from app.db.database import SessionLocal
from app.routes import customers as customers_route
from app.schemas import CustomerOut, PolicyOut

from app.agents.call_agent.memory import store


@tool
def lookup_customer_by_phone(phone: str) -> dict:
    """Look up a customer by their phone number. Returns customer details and any prior interaction history. Use this at the start of a call to authenticate the caller."""
    with SessionLocal() as db:
        try:
            customer = customers_route.lookup_customer(phone, db)
        except HTTPException as e:
            return {"error": e.detail}

        data = CustomerOut.model_validate(customer).model_dump()

    prior = store.get(("customer", str(data["cust_id"])), "interactions")
    if prior:
        data["prior_interactions"] = prior.value
    return data


@tool
def get_customer_policies(cust_id: int) -> list[dict]:
    """Retrieve all insurance policies for a customer by their customer ID."""
    with SessionLocal() as db:
        policies = customers_route.get_policies(cust_id, db)
        return [PolicyOut.model_validate(p).model_dump() for p in policies]
