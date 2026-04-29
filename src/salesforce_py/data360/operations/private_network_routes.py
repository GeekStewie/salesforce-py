"""Private Network Routes Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class PrivateNetworkRoutesOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/private-network-routes*`` endpoints."""

    async def get_private_network_routes(
        self, *, limit: int | None = None, offset: int | None = None
    ) -> dict[str, Any]:
        """List private network routes."""
        return await self._get("private-network-routes", params={"limit": limit, "offset": offset})

    async def create_private_network_route(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a private network route."""
        return await self._post("private-network-routes", json=data)

    async def get_private_network_route(self, route_id_or_name: str) -> dict[str, Any]:
        """Get a private network route."""
        return await self._get(f"private-network-routes/{route_id_or_name}")

    async def delete_private_network_route(self, route_id_or_name: str) -> dict[str, Any]:
        """Delete a private network route."""
        return await self._delete(f"private-network-routes/{route_id_or_name}")
