"""Commerce Order Summary operations (B2B/B2C shopper-facing).

Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
prefix) — the client supplies a dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class CommerceOrderSummariesOperations(ConnectBaseOperations):
    """Wrapper for ``/commerce/webstores/{id}/order-summaries/...`` endpoints."""

    def _base(self, webstore_id: str) -> str:
        return f"commerce/webstores/{self._ensure_18(webstore_id)}/order-summaries"

    async def list_order_summaries(
        self,
        webstore_id: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get order summaries."""
        return await self._get(self._base(webstore_id), params=params or {})

    async def get_order_summary(self, webstore_id: str, order_summary_id: str) -> dict[str, Any]:
        """Get an order summary."""
        order_summary_id = self._ensure_18(order_summary_id)
        return await self._get(f"{self._base(webstore_id)}/{order_summary_id}")

    async def add_order_to_cart(self, webstore_id: str, body: dict[str, Any]) -> dict[str, Any]:
        """Add an order summary to an active or a current cart."""
        return await self._post(f"{self._base(webstore_id)}/actions/add-order-to-cart", json=body)

    async def list_delivery_groups(self, webstore_id: str, order_summary_id: str) -> dict[str, Any]:
        """Get order delivery groups."""
        order_summary_id = self._ensure_18(order_summary_id)
        return await self._get(f"{self._base(webstore_id)}/{order_summary_id}/delivery-groups")

    async def list_items(self, webstore_id: str, order_summary_id: str) -> dict[str, Any]:
        """Get order items."""
        order_summary_id = self._ensure_18(order_summary_id)
        return await self._get(f"{self._base(webstore_id)}/{order_summary_id}/items")

    async def list_shipments(self, webstore_id: str, order_summary_id: str) -> dict[str, Any]:
        """Get order shipments."""
        order_summary_id = self._ensure_18(order_summary_id)
        return await self._get(f"{self._base(webstore_id)}/{order_summary_id}/shipments")

    async def submit_adjustment_aggregates(
        self, webstore_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Submit a job to calculate adjustment aggregates."""
        return await self._post(
            f"{self._base(webstore_id)}/async-actions/adjustment-aggregates",
            json=body,
        )

    async def lookup(self, webstore_id: str, body: dict[str, Any]) -> dict[str, Any]:
        """Look up details about an order summary."""
        return await self._post(f"{self._base(webstore_id)}/actions/lookup", json=body)

    async def authorize_guest(self, webstore_id: str, body: dict[str, Any]) -> dict[str, Any]:
        """Authorize guest users to access an order summary."""
        return await self._post(f"{self._base(webstore_id)}/actions/authorize", json=body)

    async def list_shipment_items(self, webstore_id: str, shipment_id: str) -> dict[str, Any]:
        """Get shipment items."""
        shipment_id = self._ensure_18(shipment_id)
        return await self._get(
            f"commerce/webstores/{self._ensure_18(webstore_id)}/shipments/{shipment_id}/items"
        )
