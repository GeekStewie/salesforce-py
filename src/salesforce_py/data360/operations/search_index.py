"""Search Index Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class SearchIndexOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/search-index*`` endpoints."""

    async def get_search_index_definitions(self) -> dict[str, Any]:
        """Get semantic search definition details."""
        return await self._get("search-index")

    async def create_search_index(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a semantic search index."""
        return await self._post("search-index", json=data)

    async def get_search_index_config(self) -> dict[str, Any]:
        """Get the semantic search configuration."""
        return await self._get("search-index/config")

    async def get_search_index(self, search_index_api_name_or_id: str) -> dict[str, Any]:
        """Get a semantic search index."""
        return await self._get(f"search-index/{search_index_api_name_or_id}")

    async def update_search_index(
        self, search_index_api_name_or_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a semantic search index."""
        return await self._patch(f"search-index/{search_index_api_name_or_id}", json=data)

    async def delete_search_index(self, search_index_api_name_or_id: str) -> dict[str, Any]:
        """Delete a semantic search index."""
        return await self._delete(f"search-index/{search_index_api_name_or_id}")
