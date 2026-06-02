"""The workflow engine — THIS IS YOUR CANVAS.

Everything else in this repo is scaffolding. Your task is to implement the logic that
turns a received email into a phone call. See TASK.md for the full brief.

You are handed an `InboundEmail`. You have two tools available:
  - the mock CRM, at GET http://localhost:8000/mock-crm/orders/{order_id}/
  - `make_call(target_number=..., variables={...})` from app.vapi

How you design the engine — the data model, how a "workflow" is defined and executed,
how steps pass data to each other — is up to you. The stub below just logs the email
so you can confirm the email is arriving before you build anything.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.inbound import InboundEmail

LOG = logging.getLogger("app.engine")


async def run_workflow(email: InboundEmail) -> None:
    LOG.info(
        "run_workflow called — TODO: implement me",
        extra={"from": email.from_, "subject": email.subject},
    )
    # TODO (your task):
    #   1. Read the email and figure out which order it's about.
    #   2. Look the order up in the mock CRM to get contact details.
    #   3. Call the contact with make_call(), passing the order details as variables
    #      so the agent can speak them.
