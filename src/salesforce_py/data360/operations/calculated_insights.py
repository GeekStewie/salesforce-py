"""Calculated Insights Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class CalculatedInsightsOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/calculated-insights*`` endpoints."""

    async def get_calculated_insights(
        self,
        *,
        offset: int,
        batch_size: int | None = None,
        dataspace: str | None = None,
        definition_type: str | None = None,
        orderby: str | None = None,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """List calculated insights.

        Args:
            offset: Required. Rows to skip.
            batch_size: Number of items (1-200, default 25).
            dataspace: Data space name.
            definition_type: One of ``CALCULATED_METRIC``, ``EXTERNAL_METRIC``,
                ``STREAMING_METRIC``.
            orderby: Sort expression, e.g. ``GenderId__c.ASC``.
            page_token: Page token from a prior response.
        """
        return await self._get(
            "calculated-insights",
            params={
                "batchSize": batch_size,
                "dataspace": dataspace,
                "definitionType": definition_type,
                "offset": offset,
                "orderby": orderby,
                "pageToken": page_token,
            },
        )

    async def create_calculated_insight(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a calculated insight."""
        return await self._post("calculated-insights", json=data)

    async def get_calculated_insight(self, api_name: str) -> dict[str, Any]:
        """Get a calculated insight by API name."""
        return await self._get(f"calculated-insights/{api_name}")

    async def update_calculated_insight(
        self, api_name: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a calculated insight."""
        return await self._patch(f"calculated-insights/{api_name}", json=data)

    async def delete_calculated_insight(self, api_name: str) -> dict[str, Any]:
        """Delete a calculated insight."""
        return await self._delete(f"calculated-insights/{api_name}")

    async def run_calculated_insight(self, api_name: str) -> dict[str, Any]:
        """Trigger a run on a calculated insight."""
        return await self._post(f"calculated-insights/{api_name}/actions/run")
