"""Discovery endpoints: GET /agents/ and GET /phone-numbers/, fetched live from Vapi."""

import asyncio
import logging
import re

from fastapi import APIRouter
from pydantic import BaseModel

from app.vapi import ASSISTANT_IDS, PHONE_NUMBER_IDS, vapi_get

LOG = logging.getLogger("app.catalog")

router = APIRouter()

# Matches Vapi/LiquidJS merge variables like {{ first_name }} or {{order_number}}.
_VARIABLE_RE = re.compile(r"{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}")


class Agent(BaseModel):
    id: str
    name: str
    model: str
    first_message: str
    system_prompt: str
    merge_variables: list[str]


class PhoneNumber(BaseModel):
    id: str
    phone_number: str


def _to_agent(raw: dict) -> Agent:
    model = raw.get("model") or {}
    messages = model.get("messages") or []
    system_prompt = next(
        (m.get("content", "") for m in messages if m.get("role") == "system"), ""
    )
    first_message = raw.get("firstMessage") or ""
    merge_variables = sorted(set(_VARIABLE_RE.findall(f"{system_prompt} {first_message}")))
    return Agent(
        id=raw.get("id", ""),
        name=raw.get("name", ""),
        model=model.get("model", ""),
        first_message=first_message,
        system_prompt=system_prompt,
        merge_variables=merge_variables,
    )


@router.get(
    "/agents/",
    response_model=list[Agent],
    tags=["Discovery"],
    summary="List the available AI agents",
)
async def list_agents() -> list[Agent]:
    raws = await asyncio.gather(
        *(vapi_get(f"/assistant/{aid}") for aid in ASSISTANT_IDS),
        return_exceptions=True,
    )
    agents: list[Agent] = []
    for aid, raw in zip(ASSISTANT_IDS, raws):
        if isinstance(raw, Exception):
            LOG.warning("Could not fetch agent", extra={"assistant_id": aid, "error": str(raw)})
            continue
        agents.append(_to_agent(raw))
    return agents


@router.get(
    "/phone-numbers/",
    response_model=list[PhoneNumber],
    tags=["Discovery"],
    summary="List the available phone numbers",
)
async def list_phone_numbers() -> list[PhoneNumber]:
    raws = await asyncio.gather(
        *(vapi_get(f"/phone-number/{pid}") for pid in PHONE_NUMBER_IDS),
        return_exceptions=True,
    )
    numbers: list[PhoneNumber] = []
    for pid, raw in zip(PHONE_NUMBER_IDS, raws):
        if isinstance(raw, Exception):
            LOG.warning(
                "Could not fetch phone number", extra={"phone_number_id": pid, "error": str(raw)}
            )
            continue
        numbers.append(PhoneNumber(id=raw.get("id", pid), phone_number=raw.get("number", "")))
    return numbers
