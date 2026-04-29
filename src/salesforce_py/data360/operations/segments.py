"""Segments Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class SegmentsOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/segments*`` endpoints."""

    async def get_segments(
        self,
        *,
        batch_size: int | None = None,
        dataspace: str | None = None,
        filters: str | None = None,
        offset: int | None = None,
        orderby: str | None = None,
    ) -> dict[str, Any]:
        """List segments."""
        return await self._get(
            "segments",
            params={
                "batchSize": batch_size,
                "dataspace": dataspace,
                "filters": filters,
                "offset": offset,
                "orderby": orderby,
            },
        )

    async def create_segment(
        self, data: dict[str, Any], *, dataspace: str | None = None
    ) -> dict[str, Any]:
        """Create a segment."""
        return await self._post("segments", json=data, params={"dataspace": dataspace})

    async def get_segment(self, segment_api_name_or_id: str) -> dict[str, Any]:
        """Get a segment."""
        return await self._get(f"segments/{segment_api_name_or_id}")

    async def update_segment(self, segment_api_name: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update a segment by API name."""
        return await self._patch(f"segments/{segment_api_name}", json=data)

    async def delete_segment(self, segment_api_name: str) -> dict[str, Any]:
        """Delete a segment."""
        return await self._delete(f"segments/{segment_api_name}")

    async def count_segment(
        self, segment_api_name: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Count segment members."""
        return await self._post(f"segments/{segment_api_name}/actions/count", json=data or {})

    async def deactivate_segment_by_name(self, segment_api_name: str) -> dict[str, Any]:
        """Deactivate a segment by API name."""
        return await self._post(f"segments/{segment_api_name}/actions/deactivate")

    async def deactivate_segment_by_id(self, segment_id: str) -> dict[str, Any]:
        """Deactivate a segment by ID."""
        return await self._post(f"segments/{segment_id}/actions/deactivate")

    async def publish_segment(self, segment_id: str) -> dict[str, Any]:
        """Publish a segment by ID."""
        return await self._post(f"segments/{segment_id}/actions/publish")

    async def get_segment_members(
        self,
        segment_api_name: str,
        *,
        fields: str | None = None,
        filters: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
    ) -> dict[str, Any]:
        """Get segment members."""
        return await self._get(
            f"segments/{segment_api_name}/members",
            params={
                "fields": fields,
                "filters": filters,
                "limit": limit,
                "offset": offset,
                "orderBy": order_by,
            },
        )
