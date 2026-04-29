"""Commerce Pricing and Promotions operations (shopper-facing).

Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
prefix) — the client supplies a dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class CommercePricingOperations(ConnectBaseOperations):
    """Wrapper for ``/commerce/webstores/{id}/pricing/...`` and
    ``/commerce/promotions/...`` endpoints.
    """

    def _base(self, webstore_id: str) -> str:
        return f"commerce/webstores/{self._ensure_18(webstore_id)}"

    async def get_product_price(
        self,
        webstore_id: str,
        product_id: str,
        *,
        effective_account_id: str | None = None,
    ) -> dict[str, Any]:
        """Get the list and buyer price for a product."""
        product_id = self._ensure_18(product_id)
        params: dict[str, Any] = {}
        if effective_account_id is not None:
            params["effectiveAccountId"] = self._ensure_18(effective_account_id)
        return await self._get(
            f"{self._base(webstore_id)}/pricing/products/{product_id}",
            params=params,
        )

    async def get_product_prices(
        self, webstore_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Get the prices for multiple products (POST)."""
        return await self._post(
            f"{self._base(webstore_id)}/pricing/products", json=body
        )

    async def evaluate_promotions(
        self, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Determine which promotions the customer is eligible for."""
        return await self._post(
            "commerce/promotions/actions/evaluate", json=body
        )

    async def evaluate_product_promotions(
        self, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Determine which promotions apply to a product or set of products."""
        return await self._post(
            "commerce/promotions/actions/evaluate-products", json=body
        )

    async def decrease_coupon_use(
        self, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Revert coupon code redemption usage."""
        return await self._post(
            "commerce/promotions/actions/decrease-use/coupon-codes", json=body
        )

    async def increase_coupon_use(
        self, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Increase coupon code redemption usage."""
        return await self._post(
            "commerce/promotions/actions/increase-use/coupon-codes", json=body
        )
