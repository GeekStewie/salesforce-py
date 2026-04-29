"""Data Graphs Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class DataGraphsOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/data-graphs*`` endpoints."""

    async def create_data_graph(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a data graph definition."""
        return await self._post("data-graphs", json=data)

    async def get_data_graph(self, data_graph_name: str) -> dict[str, Any]:
        """Get a data graph definition."""
        return await self._get(f"data-graphs/{data_graph_name}")

    async def delete_data_graph(self, data_graph_name: str) -> dict[str, Any]:
        """Delete a data graph definition."""
        return await self._delete(f"data-graphs/{data_graph_name}")

    async def refresh_data_graph(self, data_graph_name: str) -> dict[str, Any]:
        """Refresh a data graph."""
        return await self._post(f"data-graphs/{data_graph_name}/actions/refresh")

    async def get_data_graph_metadata(
        self,
        *,
        dataspace: str | None = None,
        data_graph_entity_name: str | None = None,
    ) -> dict[str, Any]:
        """Get data graph metadata for one or all entities."""
        return await self._get(
            "data-graphs/metadata",
            params={"dataspace": dataspace, "dataGraphEntityName": data_graph_entity_name},
        )

    async def get_data_graph_data_by_entity(
        self,
        data_graph_entity_name: str,
        lookup_keys: str,
        *,
        dataspace: str | None = None,
        no_cache: bool | None = None,
    ) -> dict[str, Any]:
        """Fetch data from a data graph keyed by lookup values.

        Args:
            data_graph_entity_name: Data graph entity API name.
            lookup_keys: Required lookup keys query value.
            dataspace: Data space name.
            no_cache: Force a non-cached read.
        """
        return await self._get(
            f"data-graphs/data/{data_graph_entity_name}",
            params={
                "dataspace": dataspace,
                "lookupKeys": lookup_keys,
                "noCache": no_cache,
            },
        )

    async def get_data_graph_data_by_id(
        self,
        data_graph_entity_name: str,
        id: str,
        *,
        dataspace: str | None = None,
        live: bool | None = None,
    ) -> dict[str, Any]:
        """Fetch a single data graph record by its ID."""
        return await self._get(
            f"data-graphs/data/{data_graph_entity_name}/{id}",
            params={"dataspace": dataspace, "live": live},
        )
