"""Data Action Targets Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class DataActionTargetsOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/data-action-targets*`` endpoints."""

    async def get_data_action_targets(
        self,
        *,
        batch_size: int | None = None,
        offset: int | None = None,
        orderby: str | None = None,
    ) -> dict[str, Any]:
        """List data action targets."""
        return await self._get(
            "data-action-targets",
            params={"batchSize": batch_size, "offset": offset, "orderby": orderby},
        )

    async def create_data_action_target(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a data action target."""
        return await self._post("data-action-targets", json=data)

    async def get_data_action_target(self, api_name: str) -> dict[str, Any]:
        """Get a data action target by API name."""
        return await self._get(f"data-action-targets/{api_name}")

    async def delete_data_action_target(self, api_name: str) -> dict[str, Any]:
        """Delete a data action target."""
        return await self._delete(f"data-action-targets/{api_name}")

    async def generate_signing_key(self, api_name: str) -> dict[str, Any]:
        """Generate a signing key for a data action target."""
        return await self._post(f"data-action-targets/{api_name}/signing-key")
