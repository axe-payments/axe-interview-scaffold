"""Inbound email endpoint: POST /inbound/email/ hands the email to run_workflow()."""

import logging

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.engine import run_workflow

LOG = logging.getLogger("app.inbound")

router = APIRouter()


class InboundEmail(BaseModel):
    """A received email. `from_` is aliased to the JSON key `from` (a Python keyword)."""

    from_: str = Field(alias="from")
    subject: str
    body: str
    to: str = "orders@interview.test"

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "from": "dispatch@partner.com",
                "subject": "Delivery update ORD-12345",
                "body": "Order ORD-12345 is out for delivery today.",
            }
        },
    }


@router.post(
    "/inbound/email/",
    tags=["Email intake (entry point)"],
    summary="Receive an email (the ENTRY POINT)",
)
async def inbound_email(email: InboundEmail) -> dict:
    LOG.info(
        "Received email",
        extra={"from": email.from_, "to": email.to, "subject": email.subject},
    )
    await run_workflow(email)
    return {"status": "received"}
