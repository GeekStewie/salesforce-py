"""Data Transforms Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class DataTransformsOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/data-transforms*`` and ``/ssot/data-transforms-validation`` endpoints."""

    async def get_data_transforms(
        self,
        *,
        filter_group: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
    ) -> dict[str, Any]:
        """List data transforms."""
        return await self._get(
            "data-transforms",
            params={
                "filterGroup": filter_group,
                "limit": limit,
                "offset": offset,
                "orderBy": order_by,
            },
        )

    async def create_data_transform(
        self, data: dict[str, Any], *, filter_group: str | None = None
    ) -> dict[str, Any]:
        """Create a data transform."""
        return await self._post("data-transforms", json=data, params={"filterGroup": filter_group})

    async def get_data_transform(
        self, data_transform_name_or_id: str, *, filter_group: str | None = None
    ) -> dict[str, Any]:
        """Get a data transform."""
        return await self._get(
            f"data-transforms/{data_transform_name_or_id}",
            params={"filterGroup": filter_group},
        )

    async def update_data_transform(
        self,
        data_transform_name_or_id: str,
        data: dict[str, Any],
        *,
        filter_group: str | None = None,
    ) -> dict[str, Any]:
        """Update a data transform."""
        return await self._put(
            f"data-transforms/{data_transform_name_or_id}",
            json=data,
            params={"filterGroup": filter_group},
        )

    async def delete_data_transform(self, data_transform_name_or_id: str) -> dict[str, Any]:
        """Delete a data transform."""
        return await self._delete(f"data-transforms/{data_transform_name_or_id}")

    async def run_data_transform(self, data_transform_name_or_id: str) -> dict[str, Any]:
        """Run a data transform."""
        return await self._post(f"data-transforms/{data_transform_name_or_id}/actions/run")

    async def cancel_data_transform(self, data_transform_name_or_id: str) -> dict[str, Any]:
        """Cancel a running data transform."""
        return await self._post(f"data-transforms/{data_transform_name_or_id}/actions/cancel")

    async def retry_data_transform(self, data_transform_name_or_id: str) -> dict[str, Any]:
        """Retry a failed data transform."""
        return await self._post(f"data-transforms/{data_transform_name_or_id}/actions/retry")

    async def refresh_data_transform_status(self, data_transform_name_or_id: str) -> dict[str, Any]:
        """Refresh status metadata for a data transform."""
        return await self._post(
            f"data-transforms/{data_transform_name_or_id}/actions/refresh-status"
        )

    async def get_data_transform_run_history(
        self,
        data_transform_name_or_id: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """Get run history for a data transform."""
        return await self._get(
            f"data-transforms/{data_transform_name_or_id}/run-history",
            params={"limit": limit, "offset": offset},
        )

    async def get_data_transform_schedule(self, data_transform_name_or_id: str) -> dict[str, Any]:
        """Get the schedule for a data transform."""
        return await self._get(f"data-transforms/{data_transform_name_or_id}/schedule")

    async def update_data_transform_schedule(
        self, data_transform_name_or_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update the schedule for a data transform."""
        return await self._put(f"data-transforms/{data_transform_name_or_id}/schedule", json=data)

    async def validate_data_transform(self, data: dict[str, Any]) -> dict[str, Any]:
        """Validate a data transform definition."""
        return await self._post("data-transforms-validation", json=data)
