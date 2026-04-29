"""Commerce Taxes operations.

Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
prefix) — the client supplies a dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class CommerceTaxesOperations(ConnectBaseOperations):
    """Wrapper for ``/commerce/webstores/{id}/taxes/...`` endpoints."""

    def _base(self, webstore_id: str) -> str:
        return f"commerce/webstores/{self._ensure_18(webstore_id)}"

    async def calculate_taxes(self, webstore_id: str, body: dict[str, Any]) -> dict[str, Any]:
        """Calculate taxes for a Commerce webstore."""
        return await self._post(
            f"{self._base(webstore_id)}/taxes/actions/calculate-taxes",
            json=body,
        )

    async def get_product_taxes(
        self,
        webstore_id: str,
        product_id: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get taxes for a product based on store, location, and account."""
        product_id = self._ensure_18(product_id)
        return await self._get(
            f"{self._base(webstore_id)}/taxes/products/{product_id}",
            params=params or {},
        )
