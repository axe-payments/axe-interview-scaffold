"""FastAPI application entrypoint — wires the routers and the database together."""

import logging

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from app.catalog import router as catalog_router
from app.config import settings
from app.inbound import router as inbound_router
from app.mock_crm import router as mock_crm_router
from app.vapi import router as vapi_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

DESCRIPTION = "Scaffold for the exercise — see **TASK.md**."

OPENAPI_TAGS = [
    {"name": "Email intake (entry point)", "description": "Where an inbound email arrives."},
    {"name": "Make a call (exit point)", "description": "Place an outbound call through an AI agent."},
    {"name": "Discovery", "description": "The agents and phone numbers configured for you (live from Vapi)."},
    {"name": "Mock CRM", "description": "A fake order-lookup API."},
    {"name": "Health", "description": "Liveness check."},
]

app = FastAPI(
    title="Axe Interview Scaffold",
    version="1.0.0",
    description=DESCRIPTION,
    openapi_tags=OPENAPI_TAGS,
)

app.include_router(inbound_router)
app.include_router(vapi_router)
app.include_router(catalog_router)
app.include_router(mock_crm_router)


@app.get("/health", tags=["Health"], summary="Liveness check")
async def health() -> dict:
    return {"status": "ok"}


register_tortoise(
    app,
    db_url=settings.database_url,
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=False,
)
