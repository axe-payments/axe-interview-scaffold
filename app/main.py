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

from app.config import settings
from app.inbound import router as inbound_router
from app.mock_crm import router as mock_crm_router
from app.vapi import router as vapi_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title="Axe Interview Scaffold")

app.include_router(inbound_router)
app.include_router(vapi_router)
app.include_router(mock_crm_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


register_tortoise(
    app,
    db_url=settings.database_url,
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=False,
)
