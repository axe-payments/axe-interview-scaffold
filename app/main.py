"""FastAPI application entrypoint.

Wires together the three "given" pieces (inbound email, mock CRM, outbound call),
plus the database. You shouldn't need to edit this file for the core task — though
you're free to.

The database: Tortoise ORM is connected to Postgres and `generate_schemas=True`
auto-creates tables for any models you define in `app/models.py` on startup. No
migration tooling — just add a model and restart the app.
"""

import logging

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from app.catalog import router as catalog_router
from app.config import settings
from app.inbound import router as inbound_router
from app.mock_crm import router as mock_crm_router
from app.vapi import router as vapi_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

DESCRIPTION = """
Welcome — this is the scaffold for the exercise. **Everything you can use is listed here.**

The flow you're building:

`email in  →  (your workflow engine)  →  phone call out`

- **Email intake (entry point)** — where an email arrives and triggers your code.
- **Make a call (exit point)** — places a real outbound call via an AI agent.
- **Discovery** — the AI agents and phone numbers wired up for you to use.
- **Mock CRM** — a fake "look up the order" API to enrich emails with order details.

The middle — `run_workflow()` in `app/engine.py` — is yours to build. See **TASK.md** for the brief.
"""

OPENAPI_TAGS = [
    {
        "name": "Email intake (entry point)",
        "description": "Where an inbound email arrives and triggers `run_workflow()`.",
    },
    {
        "name": "Make a call (exit point)",
        "description": "Place an outbound call through an AI agent.",
    },
    {
        "name": "Discovery",
        "description": "The agents and phone numbers configured for you (live from Vapi).",
    },
    {"name": "Mock CRM", "description": "A fake order-lookup API to enrich emails."},
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
