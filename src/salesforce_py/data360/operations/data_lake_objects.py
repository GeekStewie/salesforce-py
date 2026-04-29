"""Data Lake Objects Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class DataLakeObjectsOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/data-lake-objects*`` endpoints."""

    async def get_data_lake_objects(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
    ) -> dict[str, Any]:
        """List data lake objects."""
        return await self._get(
            "data-lake-objects",
            params={"limit": limit, "offset": offset, "orderBy": order_by},
        )

    async def create_data_lake_object(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a data lake object."""
        return await self._post("data-lake-objects", json=data)

    async def get_data_lake_object(
        self,
        record_id_or_developer_name: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
    ) -> dict[str, Any]:
        """Get a data lake object by ID or developer name."""
        return await self._get(
            f"data-lake-objects/{record_id_or_developer_name}",
            params={"limit": limit, "offset": offset, "orderBy": order_by},
        )

    async def update_data_lake_object(
        self, record_id_or_developer_name: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a data lake object."""
        return await self._patch(f"data-lake-objects/{record_id_or_developer_name}", json=data)

    async def delete_data_lake_object(self, record_id_or_developer_name: str) -> dict[str, Any]:
        """Delete a data lake object."""
        return await self._delete(f"data-lake-objects/{record_id_or_developer_name}")
