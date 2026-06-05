"""Outbound calling: `make_call()` places a call through Vapi.

The assistant and phone-number IDs are hard-coded below (not secret); only the Vapi API
key comes from `.env`.
"""

import logging

import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings
from app.tunnel import public_base_url

LOG = logging.getLogger("app.vapi")

VAPI_BASE_URL = "https://api.vapi.ai"
VAPI_CALL_URL = f"{VAPI_BASE_URL}/call"

# Pre-configured Vapi resources (not secret). Discover them at runtime via GET /agents/
# and GET /phone-numbers/.
ASSISTANT_IDS = [
    "1fd811c3-2e8d-448e-a6de-3de998a8dde6",
    "7075ec6d-9d1d-4716-8943-018d3dfe9b09",
    "38928c55-c209-4dc1-b479-a7ea86b9821d",
]
PHONE_NUMBER_IDS = [
    "d7c73608-369e-4e2a-915b-4fb5dfb886c0",
    "e4699fab-7660-48af-a7cd-c7381633e496",
]

router = APIRouter()


async def vapi_get(path: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            f"{VAPI_BASE_URL}{path}",
            headers={"Authorization": f"Bearer {settings.vapi_api_key}"},
        )
        response.raise_for_status()
        return response.json()


async def make_call(
    *,
    target_number: str,
    assistant_id: str,
    phone_number_id: str,
    variables: dict | None = None,
) -> dict:
    """Place an outbound call; `variables` fill the agent's prompt {{ placeholders }}.

    Returns the Vapi call object.
    """
    overrides: dict = {"variableValues": variables or {}}

    # If we have a public URL (via ngrok), ask Vapi to POST the end-of-call transcript back
    # to our webhook so it's pretty-printed in the logs. No URL -> no callback, call as before.
    base_url = await public_base_url()
    if base_url:
        overrides["server"] = {"url": f"{base_url}/webhooks/vapi/"}
        overrides["serverMessages"] = ["end-of-call-report"]

    payload = {
        "assistantId": assistant_id,
        "phoneNumberId": phone_number_id,
        "customer": {"number": target_number},
        "assistantOverrides": overrides,
    }

    LOG.info(
        "Placing outbound call",
        extra={
            "target": target_number,
            "assistant_id": assistant_id,
            "transcript_callback": base_url is not None,
        },
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
    target_number: str
    assistant_id: str
    phone_number_id: str
    variables: dict = {}

    model_config = {
        "json_schema_extra": {
            "example": {
                "target_number": "+14155551234",
                "assistant_id": "<an assistant id from GET /agents/>",
                "phone_number_id": "<a phone number id from GET /phone-numbers/>",
                "variables": {"first_name": "Alex", "order_number": "ORD-12345"},
            }
        }
    }


@router.post(
    "/debug/call/",
    tags=["Make a call (exit point)"],
    summary="Place a call directly (the EXIT POINT)",
)
async def debug_call(request: DebugCallRequest) -> dict:
    """Place a call directly, bypassing the engine."""
    try:
        call = await make_call(
            target_number=request.target_number,
            assistant_id=request.assistant_id,
            phone_number_id=request.phone_number_id,
            variables=request.variables,
        )
    except httpx.HTTPStatusError as exc:
        return {
            "ok": False,
            "error": f"Vapi returned {exc.response.status_code} — check your VAPI_* values in .env",
            "vapi_response": exc.response.text,
        }
    return {"ok": True, "call": call}
