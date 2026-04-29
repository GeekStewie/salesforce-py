"""Insights Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class InsightsOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/insight/*`` endpoints."""

    async def get_insight_metadata(self) -> dict[str, Any]:
        """Get insight metadata."""
        return await self._get("insight/metadata")

    async def get_calculated_insight_metadata(self, ci_name: str) -> dict[str, Any]:
        """Get metadata for a calculated insight object."""
        return await self._get(f"insight/metadata/{ci_name}")

    async def get_calculated_insight_object(
        self,
        ci_name: str,
        *,
        batch_size: int | None = None,
        dimensions: str | None = None,
        filters: str | None = None,
        measures: str | None = None,
        offset: int | None = None,
        orderby: str | None = None,
        time_granularity: str | None = None,
    ) -> dict[str, Any]:
        """Query a calculated insight object."""
        return await self._get(
            f"insight/calculated-insights/{ci_name}",
            params={
                "batchSize": batch_size,
                "dimensions": dimensions,
                "filters": filters,
                "measures": measures,
                "offset": offset,
                "orderby": orderby,
                "timeGranularity": time_granularity,
            },
        )
