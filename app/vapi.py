"""Outbound calling.

This is the second "given" of the exercise: a single function, `make_call()`, that
places an outbound phone call through Vapi. Your engine calls this when it decides a
call should happen. You should not need to change anything in this file.

Three agents and two phone numbers are pre-configured. Their IDs are hard-coded below —
they aren't secret; only the Vapi API key lives in `.env`. Discover them at runtime via
the `GET /agents/` / `GET /phone-numbers/` endpoints. `make_call` defaults to the first
agent + first number; pass `assistant_id` / `phone_number_id` explicitly to choose another.
"""

import logging

import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings

LOG = logging.getLogger("app.vapi")

VAPI_BASE_URL = "https://api.vapi.ai"
VAPI_CALL_URL = f"{VAPI_BASE_URL}/call"

# --- Pre-configured Vapi resources (not secret — safe to hard-code) ---
# The three AI agents you can call with. Inspect them at GET /agents/.
ASSISTANT_IDS = [
    "1fd811c3-2e8d-448e-a6de-3de998a8dde6",  # Delivery Completed (Driver)
    "7075ec6d-9d1d-4716-8943-018d3dfe9b09",  # Delivery Completed (Customer)
    "38928c55-c209-4dc1-b479-a7ea86b9821d",  # Delivery Delay (Customer)
]
# The phone numbers you can place calls from. Inspect them at GET /phone-numbers/.
PHONE_NUMBER_IDS = [
    "d7c73608-369e-4e2a-915b-4fb5dfb886c0",  # +447428717968
    "e4699fab-7660-48af-a7cd-c7381633e496",  # +441290438347
]

router = APIRouter()


async def vapi_get(path: str) -> dict:
    """GET a Vapi resource (read-only). Used by the discovery endpoints in app/catalog.py."""
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
    variables: dict | None = None,
    assistant_id: str | None = None,
    phone_number_id: str | None = None,
) -> dict:
    """Place an outbound call.

    Args:
        target_number: who to call, E.164 (e.g. "+14155551234").
        variables: values exposed to the assistant's prompt as {{variable}} — e.g.
            {"order_number": "12345", "contact_name": "Alex"}.
        assistant_id / phone_number_id: which agent to use. Defaults to the first
            configured agent + phone number (see ASSISTANT_IDS / PHONE_NUMBER_IDS).

    Returns the Vapi call object (includes the call `id`).
    """
    assistant_id = assistant_id or ASSISTANT_IDS[0]
    phone_number_id = phone_number_id or PHONE_NUMBER_IDS[0]

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
    """Body for the smoke-test endpoint.

    You choose which agent and which number to call from — there are no defaults.
    Look them up via the discovery endpoints: `assistant_id` from `GET /agents/`
    and `phone_number_id` from `GET /phone-numbers/`.
    """

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
    """Smoke test: place a call directly, bypassing the engine.

    Use this to confirm your Vapi credentials work before you start building
    (`./scripts/test_call.sh`). It's also a worked example of calling `make_call`:
    you pick the agent (`assistant_id`) and the number to call from
    (`phone_number_id`) yourself — see `GET /agents/` and `GET /phone-numbers/`.

    Reports a readable error (Vapi's status + body) instead of a 500 so credential
    problems are obvious.
    """
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
