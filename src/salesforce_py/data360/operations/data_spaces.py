"""Data Spaces Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class DataSpacesOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/data-spaces*`` endpoints."""

    async def get_data_spaces(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
    ) -> dict[str, Any]:
        """List data spaces."""
        return await self._get(
            "data-spaces",
            params={"limit": limit, "offset": offset, "orderBy": order_by},
        )

    async def create_data_space(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a data space."""
        return await self._post("data-spaces", json=data)

    async def get_data_space(self, id_or_name: str) -> dict[str, Any]:
        """Get a data space."""
        return await self._get(f"data-spaces/{id_or_name}")

    async def update_data_space(self, id_or_name: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update a data space."""
        return await self._patch(f"data-spaces/{id_or_name}", json=data)

    async def get_data_space_members(
        self,
        id_or_name: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
    ) -> dict[str, Any]:
        """List data space members."""
        return await self._get(
            f"data-spaces/{id_or_name}/members",
            params={"limit": limit, "offset": offset, "orderBy": order_by},
        )

    async def upsert_data_space_members(
        self, id_or_name: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Upsert data space members."""
        return await self._put(f"data-spaces/{id_or_name}/members", json=data)

    async def get_data_space_member(
        self, id_or_name: str, data_space_member_object_name: str
    ) -> dict[str, Any]:
        """Get a data space member by object name."""
        return await self._get(f"data-spaces/{id_or_name}/members/{data_space_member_object_name}")
