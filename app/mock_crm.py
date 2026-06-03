"""A tiny mock CRM. Look up an order at GET /mock-crm/orders/{order_id}/.

Order ids: ORD-12345, ORD-67890 (normal), ORD-ERROR (returns 500), ORD-SLOW (delayed).
"""

import asyncio

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/mock-crm")

# Real phones the demo calls ring.
DAN_PHONE_NUMBER = "+447790642883"
CHRIS_PHONE_NUMBER = "+447460833116"


def _orders() -> dict[str, dict]:
    return {
        "ORD-12345": {
            "order_id": "ORD-12345",
            "contact_name": "Dan",
            "contact_phone": DAN_PHONE_NUMBER,
            "status": "Out for delivery",
            "delivery_window": "Today, 2pm-4pm",
            "address": "742 Evergreen Terrace, Springfield",
        },
        "ORD-67890": {
            "order_id": "ORD-67890",
            "contact_name": "Chris",
            "contact_phone": CHRIS_PHONE_NUMBER,
            "status": "Delayed",
            "delivery_window": "Tomorrow, 9am-12pm",
            "address": "31 Spooner Street, Quahog",
        },
    }


@router.get("/orders/", tags=["Mock CRM"], summary="List all mock orders")
async def list_orders() -> list[dict]:
    """List all orders. (ORD-ERROR and ORD-SLOW are not listed.)"""
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
