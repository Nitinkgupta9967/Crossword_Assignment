from __future__ import annotations

import json
import re
from typing import Any

from aster_row.paths import ORDERS_PATH

CUSTOMER_SAFE_FIELDS = (
    "order_id",
    "membership_tier",
    "placed_at",
    "status",
    "status_updated_at",
    "shipped_at",
    "delivered_at",
    "carrier",
    "tracking_number",
    "estimated_delivery",
    "customer_safe_message",
)

_ORDER_ID_RE = re.compile(r"ORD-\d{4}", re.IGNORECASE)
_STALE_STATUSES = {"cancelled", "returned"}


class OrderStore:
    def __init__(self, path=ORDERS_PATH):
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.snapshot_at: str = payload["snapshot_at"]
        self._by_id = {row["order_id"].upper(): row for row in payload["orders"]}

    @staticmethod
    def normalize_order_id(raw: str | None) -> str | None:
        if not raw:
            return None
        cleaned = raw.strip().upper()
        cleaned = cleaned.strip(".,;:()[]\"'")
        match = _ORDER_ID_RE.search(cleaned)
        if not match:
            return None
        return match.group(0).upper()

    def extract_from_text(self, text: str) -> str | None:
        match = _ORDER_ID_RE.search(text or "")
        return match.group(0).upper() if match else None

    def lookup(self, order_id: str | None) -> dict[str, Any]:
        normalized = self.normalize_order_id(order_id)
        if not normalized:
            return {
                "found": False,
                "reason": "malformed_order_id",
                "message": "That does not look like a valid order ID. Use a value such as ORD-1007.",
            }
        row = self._by_id.get(normalized)
        if not row:
            return {
                "found": False,
                "reason": "not_found",
                "order_id": normalized,
                "message": "This order was not found. Check the order ID or contact support.",
            }

        items = [
            {
                "name": item.get("name"),
                "quantity": item.get("quantity"),
                "final_sale": item.get("final_sale"),
            }
            for item in row.get("items", [])
        ]
        result: dict[str, Any] = {
            "found": True,
            "order_id": row["order_id"],
            "membership_tier": row.get("membership_tier"),
            "items": items,
            "placed_at": row.get("placed_at"),
            "status": row.get("status"),
            "status_updated_at": row.get("status_updated_at"),
            "shipped_at": row.get("shipped_at"),
            "delivered_at": row.get("delivered_at"),
            "customer_safe_message": row.get("customer_safe_message"),
            "snapshot_at": self.snapshot_at,
        }

        status = (row.get("status") or "").lower()
        if status in _STALE_STATUSES:
            result["carrier"] = None
            result["tracking_number"] = None
            result["estimated_delivery"] = None
            result["stale_fields_omitted"] = True
            result["guidance"] = (
                "Status is authoritative. Do not mention leftover carrier, tracking, "
                "or estimated-delivery values for cancelled or returned orders."
            )
        else:
            result["carrier"] = row.get("carrier")
            result["tracking_number"] = row.get("tracking_number")
            result["estimated_delivery"] = row.get("estimated_delivery")
            if status == "shipped" and not row.get("estimated_delivery"):
                result["guidance"] = (
                    "The order has shipped. A delivery estimate is unavailable. "
                    "Do not invent an arrival date."
                )
            if status == "exception":
                result["requires_human_handoff"] = True
                result["guidance"] = (
                    "This shipment has an exception that requires support review. "
                    "Recommend a human handoff. Do not claim an investigation was opened."
                )
        return result
