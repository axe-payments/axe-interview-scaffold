"""Outbound calling.

This is the second "given" of the exercise: a single function, `make_call()`, that
places an outbound phone call through Vapi. Your engine calls this when it decides a
call should happen. You should not need to change anything in this file.

Two agent / phone-number pairs are configured (see `.env`). `make_call` defaults to
pair 1; pass `assistant_id` / `phone_number_id` explicitly to route to pair 2.
"""

import logging

import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings

LOG = logging.getLogger("app.vapi")

VAPI_CALL_URL = "https://api.vapi.ai/call"

router = APIRouter()


async def make_call(
    *,
    target_number: str,
    variables: dict | None = None,
    assistant_id: str | None = None,
    phone_number_id: str | None = None,
) -> dict:
    """Place an outbound call.

    Args:
        target_number: who to call, E.164 (e.g. "+14155551234").
        variables: values exposed to the assistant's prompt as {{variable}} — e.g.
            {"order_number": "12345", "contact_name": "Alex"}.
        assistant_id / phone_number_id: which agent to use. Defaults to pair 1.

    Returns the Vapi call object (includes the call `id`).
    """
    assistant_id = assistant_id or settings.vapi_assistant_id_1
    phone_number_id = phone_number_id or settings.vapi_phone_number_id_1

    payload = {
        "assistantId": assistant_id,
        "phoneNumberId": phone_number_id,
        "customer": {"number": target_number},
        "assistantOverrides": {"variableValues": variables or {}},
    }

    LOG.info(
        "Placing outbound call",
        extra={"target": target_number, "assistant_id": assistant_id},
    )

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            VAPI_CALL_URL,
            headers={"Authorization": f"Bearer {settings.vapi_api_key}"},
            json=payload,
        )
        response.raise_for_status()
        call = response.json()

    LOG.info("Call created", extra={"call_id": call.get("id"), "status": call.get("status")})
    return call


class DebugCallRequest(BaseModel):
    """Body for the smoke-test endpoint."""

    target_number: str
    variables: dict = {}


@router.post("/debug/call/")
async def debug_call(request: DebugCallRequest) -> dict:
    """Smoke test: place a call directly, bypassing the engine.

    Use this to confirm your Vapi credentials work before you start building
    (`./scripts/test_call.sh`). It's also a worked example of calling `make_call`.

    Reports a readable error (Vapi's status + body) instead of a 500 so credential
    problems are obvious.
    """
    try:
        call = await make_call(
            target_number=request.target_number, variables=request.variables
        )
    except httpx.HTTPStatusError as exc:
        return {
            "ok": False,
            "error": f"Vapi returned {exc.response.status_code} — check your VAPI_* values in .env",
            "vapi_response": exc.response.text,
        }
    return {"ok": True, "call": call}
