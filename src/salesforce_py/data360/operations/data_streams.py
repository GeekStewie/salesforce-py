"""Data Streams Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class DataStreamsOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/data-streams*`` endpoints."""

    async def get_data_streams(
        self,
        *,
        connection_name: str | None = None,
        filter: str | None = None,
        include_mappings: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
    ) -> dict[str, Any]:
        """List data streams."""
        return await self._get(
            "data-streams",
            params={
                "connectionName": connection_name,
                "filter": filter,
                "includeMappings": include_mappings,
                "limit": limit,
                "offset": offset,
                "orderBy": order_by,
            },
        )

    async def create_data_stream(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a data stream."""
        return await self._post("data-streams", json=data)

    async def get_data_stream(
        self,
        record_id_or_developer_name: str,
        *,
        include_mappings: bool | None = None,
    ) -> dict[str, Any]:
        """Get a data stream."""
        return await self._get(
            f"data-streams/{record_id_or_developer_name}",
            params={"includeMappings": include_mappings},
        )

    async def update_data_stream(
        self, record_id_or_developer_name: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a data stream."""
        return await self._patch(f"data-streams/{record_id_or_developer_name}", json=data)

    async def delete_data_stream(
        self,
        record_id_or_developer_name: str,
        *,
        should_delete_data_lake_object: bool | None = None,
    ) -> dict[str, Any]:
        """Delete a data stream."""
        return await self._delete(
            f"data-streams/{record_id_or_developer_name}",
            params={"shouldDeleteDataLakeObject": should_delete_data_lake_object},
        )

    async def run_data_stream(
        self, record_id_or_developer_name: str, *, interactive: bool | None = None
    ) -> dict[str, Any]:
        """Run a data stream."""
        return await self._post(
            f"data-streams/{record_id_or_developer_name}/actions/run",
            params={"interactive": interactive},
        )
