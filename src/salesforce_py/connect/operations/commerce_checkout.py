"""Commerce B2B/B2C Checkout operations.

Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
prefix) — the client supplies a dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class CommerceCheckoutOperations(ConnectBaseOperations):
    """Wrapper for ``/commerce/webstores/{id}/checkouts/...`` endpoints."""

    def _base(self, webstore_id: str) -> str:
        return f"commerce/webstores/{self._ensure_18(webstore_id)}"

    async def start_checkout(
        self, webstore_id: str, body: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Start a Commerce store checkout."""
        return await self._post(f"{self._base(webstore_id)}/checkouts", json=body or {})

    async def get_checkout(
        self, webstore_id: str, active_or_checkout_id: str = "active"
    ) -> dict[str, Any]:
        """Get a Commerce store checkout."""
        return await self._get(f"{self._base(webstore_id)}/checkouts/{active_or_checkout_id}")

    async def update_checkout(
        self,
        webstore_id: str,
        active_or_checkout_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Update a Commerce store checkout."""
        return await self._patch(
            f"{self._base(webstore_id)}/checkouts/{active_or_checkout_id}",
            json=body,
        )

    async def delete_checkout(
        self, webstore_id: str, active_or_checkout_id: str = "active"
    ) -> dict[str, Any]:
        """Delete a Commerce store checkout."""
        return await self._delete(f"{self._base(webstore_id)}/checkouts/{active_or_checkout_id}")

    async def pay(
        self,
        webstore_id: str,
        active_or_checkout_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Submit payment for a Commerce store checkout."""
        return await self._post(
            f"{self._base(webstore_id)}/checkouts/{active_or_checkout_id}/payments",
            json=body,
        )

    async def place_order(
        self,
        webstore_id: str,
        active_or_checkout_id: str,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Place an order for a Commerce store checkout."""
        return await self._post(
            f"{self._base(webstore_id)}/checkouts/{active_or_checkout_id}/orders",
            json=body or {},
        )

    async def tokenize_payment(self, webstore_id: str, body: dict[str, Any]) -> dict[str, Any]:
        """Tokenize a payment for a Commerce store checkout."""
        return await self._post(f"{self._base(webstore_id)}/payments/token", json=body)

    async def apply_coupon(
        self,
        webstore_id: str,
        active_or_checkout_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply a coupon code to a checkout."""
        return await self._post(
            f"{self._base(webstore_id)}/checkouts/{active_or_checkout_id}/coupons",
            json=body,
        )

    async def delete_coupon(
        self,
        webstore_id: str,
        active_or_checkout_id: str,
        cart_coupon_id: str,
    ) -> dict[str, Any]:
        """Delete a coupon from a checkout."""
        cart_coupon_id = self._ensure_18(cart_coupon_id)
        return await self._delete(
            f"{self._base(webstore_id)}/checkouts/{active_or_checkout_id}/coupons/{cart_coupon_id}"
        )

    async def register_buyer(self, webstore_id: str, body: dict[str, Any]) -> dict[str, Any]:
        """Register a guest user as an authenticated customer during checkout."""
        return await self._post(f"{self._base(webstore_id)}/buyers/registrations", json=body)
