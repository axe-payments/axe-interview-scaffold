"""The workflow engine — this is your canvas.

`run_workflow(email)` is called for each inbound email (see `app/inbound.py`). It's the
one piece you implement. See TASK.md.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.inbound import InboundEmail

LOG = logging.getLogger("app.engine")


async def run_workflow(email: InboundEmail) -> None:
    LOG.info(
        "run_workflow received an email",
        extra={"from": email.from_, "subject": email.subject},
    )
