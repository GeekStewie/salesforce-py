"""Connectors Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class ConnectorsOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/connectors*`` endpoints."""

    async def get_connectors(
        self,
        *,
        field_group: str | None = None,
        filters: str | None = None,
        order_by: str | None = None,
    ) -> dict[str, Any]:
        """List connector metadata definitions."""
        return await self._get(
            "connectors",
            params={
                "fieldGroup": field_group,
                "filters": filters,
                "orderBy": order_by,
            },
        )

    async def get_connector(self, connector_type: str) -> dict[str, Any]:
        """Get metadata for a specific connector type."""
        return await self._get(f"connectors/{connector_type}")
