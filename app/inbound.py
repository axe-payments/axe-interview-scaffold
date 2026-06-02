"""Inbound email endpoint.

This is one of the two "givens" of the exercise. An email is delivered to your
service as a simple JSON POST (see `scripts/send_test_email.sh`). All this endpoint
does is validate the payload and hand it to `run_workflow()` — the function YOU build.

In production this same shape would be filled by an email provider's inbound-parse
webhook (SendGrid/Mailgun/etc.); for the interview we skip that and inject it locally.
"""

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
    """The entry point of the whole exercise.

    An email arrives here as JSON (in production, from an email provider's inbound-parse
    webhook; here, from `./scripts/send_test_email.sh`). The endpoint validates it and
    hands it to `run_workflow(email)` in `app/engine.py` — the function you implement.
    """
    LOG.info(
        "Received email",
        extra={"from": email.from_, "to": email.to, "subject": email.subject},
    )
    await run_workflow(email)
    return {"status": "received"}
