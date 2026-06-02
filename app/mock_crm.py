"""A tiny mock CRM.

Stands in for a real "look up the order" system. Your engine can call this over HTTP
(it's just another local endpoint) to enrich an email with order details before
deciding who to call and what to say.

    GET /mock-crm/orders/{order_id}/

Known order ids:
    ORD-12345  -> a normal order. Its contact_phone is DEMO_TARGET_PHONE (your phone),
                  so a call against this order rings you.
    ORD-67890  -> a second normal order (different contact, no real phone).
    ORD-ERROR  -> always returns 500, for testing your error handling.
    ORD-SLOW   -> responds after a delay, for testing timeouts/retries.
"""

import asyncio

from fastapi import APIRouter, HTTPException

from app.config import settings

router = APIRouter(prefix="/mock-crm")


def _orders() -> dict[str, dict]:
    return {
        "ORD-12345": {
            "order_id": "ORD-12345",
            "contact_name": "Alex Morgan",
            "contact_phone": settings.demo_target_phone,
            "status": "Out for delivery",
            "delivery_window": "Today, 2pm-4pm",
            "address": "742 Evergreen Terrace, Springfield",
        },
        "ORD-67890": {
            "order_id": "ORD-67890",
            "contact_name": "Jordan Lee",
            "contact_phone": "+15555550123",
            "status": "Delayed",
            "delivery_window": "Tomorrow, 9am-12pm",
            "address": "31 Spooner Street, Quahog",
        },
    }


@router.get("/orders/", tags=["Mock CRM"], summary="List all mock orders")
async def list_orders() -> list[dict]:
    """List every order in the mock CRM, so you can see what's available to look up.

    (The special ids `ORD-ERROR` and `ORD-SLOW` are not listed — they exist only to let
    you test error / slow-response handling against `GET /orders/{order_id}/`.)
    """
    return list(_orders().values())


@router.get("/orders/{order_id}/", tags=["Mock CRM"], summary="Look up one order")
async def get_order(order_id: str) -> dict:
    if order_id == "ORD-ERROR":
        raise HTTPException(status_code=500, detail="Simulated CRM failure")

    if order_id == "ORD-SLOW":
        await asyncio.sleep(5)
        order_id = "ORD-12345"

    order = _orders().get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return order
