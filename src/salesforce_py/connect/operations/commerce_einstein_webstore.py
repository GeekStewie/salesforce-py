"""Commerce Einstein Webstore operations.

Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
prefix) — the client supplies a dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class CommerceEinsteinWebstoreOperations(ConnectBaseOperations):
    """Wrapper for ``/commerce/webstores/{id}/ai/...`` endpoints (v55.0+)."""

    def _base(self, webstore_id: str) -> str:
        return f"commerce/webstores/{self._ensure_18(webstore_id)}/ai"

    async def get_deployment_status(self, webstore_id: str) -> dict[str, Any]:
        """Get the status of a Commerce Einstein deployment for a store."""
        return await self._get(f"{self._base(webstore_id)}/status")

    async def get_configuration(self, webstore_id: str) -> dict[str, Any]:
        """Get the Commerce Einstein configuration for a store."""
        return await self._get(f"{self._base(webstore_id)}/configuration")

    async def enqueue_activity_export(
        self, webstore_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Enqueue a job to export Commerce Einstein activity for a store.

        Args:
            body: Request payload with ``cookieId`` or ``userId``.
        """
        return await self._post(f"{self._base(webstore_id)}/activities/export-jobs", json=body)

    async def get_activity_export_status(self, webstore_id: str, job_id: str) -> dict[str, Any]:
        """Get the status of a Commerce Einstein activity export job."""
        return await self._get(f"{self._base(webstore_id)}/activities/export-jobs/{job_id}")

    async def download_activity_export(self, webstore_id: str, job_id: str) -> bytes:
        """Download an exported Commerce Einstein activity file.

        Returns:
            Raw binary content of the exported file.
        """
        return await self._get_bytes(
            f"{self._base(webstore_id)}/activities/export-jobs/{job_id}/file-content"
        )

    async def enqueue_activity_purge(
        self, webstore_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Enqueue a job to purge Commerce Einstein activity for a store.

        Args:
            body: Request payload with ``cookieId`` or ``userId``.
        """
        return await self._post(f"{self._base(webstore_id)}/activities/purge-jobs", json=body)

    async def get_activity_purge_status(self, webstore_id: str, job_id: str) -> dict[str, Any]:
        """Get the status of a Commerce Einstein activity purge job."""
        return await self._get(f"{self._base(webstore_id)}/activities/purge-jobs/{job_id}")

    async def get_recommendations(
        self,
        webstore_id: str,
        *,
        recommender: str,
        anchor_from_current_cart: bool | None = None,
        anchor_values: str | None = None,
        currency_iso_code: str | None = None,
        data_space: str | None = None,
        effective_account_id: str | None = None,
        include_pricing_and_product_information: bool | None = None,
        include_request_product: bool | None = None,
        individual_id: str | None = None,
        personalization_point: str | None = None,
    ) -> dict[str, Any]:
        """Get Commerce Einstein product recommendations.

        Args:
            recommender: Recommender to use (e.g. ``SimilarProducts``).
            anchor_from_current_cart: Use cart products as anchors.
            anchor_values: List of product or category IDs as context.
            currency_iso_code: ISO 4217 currency code.
            data_space: Reserved for future use.
            effective_account_id: Buyer account or guest profile ID.
            include_pricing_and_product_information: Include pricing info.
            include_request_product: Include request product info.
            individual_id: Reserved for future use.
            personalization_point: Reserved for future use.
        """
        params: dict[str, Any] = {"recommender": recommender}
        if anchor_from_current_cart is not None:
            params["anchorFromCurrentCart"] = anchor_from_current_cart
        if anchor_values is not None:
            params["anchorValues"] = anchor_values
        if currency_iso_code is not None:
            params["currencyIsoCode"] = currency_iso_code
        if data_space is not None:
            params["dataSpace"] = data_space
        if effective_account_id is not None:
            params["effectiveAccountId"] = self._ensure_18(effective_account_id)
        if include_pricing_and_product_information is not None:
            params["includePricingAndProductInformation"] = include_pricing_and_product_information
        if include_request_product is not None:
            params["includeRequestProduct"] = include_request_product
        if individual_id is not None:
            params["individualId"] = individual_id
        if personalization_point is not None:
            params["personalizationPoint"] = personalization_point
        return await self._get(f"{self._base(webstore_id)}/recommendations", params=params)
