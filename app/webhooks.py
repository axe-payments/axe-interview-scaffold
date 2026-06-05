"""Inbound callbacks from Vapi.

The one we care about is `end-of-call-report`, which carries the full transcript — we
pretty-print it to the logs so a call can be *read* instead of listened to live.

For Vapi to reach this endpoint the app needs a public URL; docker-compose starts an `ngrok`
tunnel automatically and `make_call()` (app/vapi.py) registers this path as the call's server
URL. See app/tunnel.py for how the public URL is discovered.
"""

import logging

from fastapi import APIRouter, Request

LOG = logging.getLogger("app.webhooks")

router = APIRouter()


@router.post(
    "/webhooks/vapi/",
    tags=["Webhooks"],
    summary="Receive Vapi server messages (e.g. the end-of-call transcript)",
)
async def vapi_webhook(request: Request) -> dict:
    """Vapi POSTs server messages here. We log the transcript from `end-of-call-report`."""
    body = await request.json()
    message = body.get("message", {}) if isinstance(body, dict) else {}
    message_type = message.get("type")

    if message_type == "end-of-call-report":
        LOG.info("Call transcript\n%s", _format_transcript(message))
    else:
        LOG.info("Vapi server message", extra={"type": message_type})

    return {"received": True}


def _format_transcript(message: dict) -> str:
    """Build a readable transcript block from an end-of-call-report payload."""
    artifact = message.get("artifact") or {}
    turns = artifact.get("messages") or message.get("messages") or []

    lines = []
    for turn in turns:
        role = turn.get("role", "?")
        if role == "system":
            continue
        text = turn.get("message") or turn.get("content") or ""
        lines.append(f"  {role:>9}: {text}")

    if not lines:
        fallback = artifact.get("transcript") or message.get("transcript") or "(empty transcript)"
        lines = [f"  {fallback}"]

    ended = message.get("endedReason")
    if ended:
        lines.append(f"  (ended: {ended})")

    summary = message.get("summary") or (message.get("analysis") or {}).get("summary")
    if summary:
        lines.append(f"  summary: {summary}")

    return "\n".join(lines)
