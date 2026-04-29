"""Data Actions Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class DataActionsOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/data-actions`` endpoints."""

    async def get_data_actions(
        self,
        *,
        batch_size: int | None = None,
        dataspace: str | None = None,
        offset: int | None = None,
        orderby: str | None = None,
    ) -> dict[str, Any]:
        """List data actions."""
        return await self._get(
            "data-actions",
            params={
                "batchSize": batch_size,
                "dataspace": dataspace,
                "offset": offset,
                "orderby": orderby,
            },
        )

    async def create_data_action(
        self, data: dict[str, Any], *, dataspace: str | None = None
    ) -> dict[str, Any]:
        """Create a data action."""
        return await self._post("data-actions", json=data, params={"dataspace": dataspace})
