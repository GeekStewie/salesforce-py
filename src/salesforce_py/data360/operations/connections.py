"""Connections Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class ConnectionsOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/connections*`` endpoints."""

    # ------------------------------------------------------------------
    # Connection CRUD
    # ------------------------------------------------------------------

    async def get_connections(
        self,
        connector_type: str,
        *,
        dev_name: str | None = None,
        label: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
        organization_id: str | None = None,
    ) -> dict[str, Any]:
        """List Data 360 connections by connector type."""
        return await self._get(
            "connections",
            params={
                "connectorType": connector_type,
                "devName": dev_name,
                "label": label,
                "limit": limit,
                "offset": offset,
                "orderBy": order_by,
                "organizationId": organization_id,
            },
        )

    async def create_connection(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a connection."""
        return await self._post("connections", json=data)

    async def get_connection(self, connection_id: str) -> dict[str, Any]:
        """Get a connection by ID."""
        return await self._get(f"connections/{connection_id}")

    async def update_connection(self, connection_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Partially update a connection."""
        return await self._patch(f"connections/{connection_id}", json=data)

    async def replace_connection(self, connection_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Replace a connection."""
        return await self._put(f"connections/{connection_id}", json=data)

    async def delete_connection(self, connection_id: str) -> dict[str, Any]:
        """Delete a connection."""
        return await self._delete(f"connections/{connection_id}")

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    async def get_connection_endpoints(self, connection_id: str) -> dict[str, Any]:
        """Get REST endpoints exposed by a connection."""
        return await self._get(f"connections/{connection_id}/endpoints")

    async def get_connection_databases(
        self, connection_id: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Discover databases on a connection."""
        return await self._post(f"connections/{connection_id}/databases", json=data or {})

    async def get_connection_database_schemas(
        self, connection_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Discover database schemas on a connection."""
        return await self._post(f"connections/{connection_id}/database-schemas", json=data)

    async def get_connection_objects(
        self, connection_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Discover objects available via a connection."""
        return await self._post(f"connections/{connection_id}/objects", json=data)

    async def get_connection_fields(
        self, connection_id: str, resource_name: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Discover fields for a connection object."""
        return await self._post(
            f"connections/{connection_id}/objects/{resource_name}/fields", json=data
        )

    async def get_connection_preview(
        self, connection_id: str, resource_name: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Preview rows from a connection object."""
        return await self._post(
            f"connections/{connection_id}/objects/{resource_name}/preview", json=data
        )

    # ------------------------------------------------------------------
    # Schema & sitemap
    # ------------------------------------------------------------------

    async def get_connection_schema(self, connection_id: str) -> dict[str, Any]:
        """Get a connection's schema."""
        return await self._get(f"connections/{connection_id}/schema")

    async def upsert_connection_schema(
        self, connection_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Upsert a connection's schema."""
        return await self._put(f"connections/{connection_id}/schema", json=data)

    async def get_connection_sitemap(self, connection_id: str) -> dict[str, Any]:
        """Get a connection's site map."""
        return await self._get(f"connections/{connection_id}/sitemap")

    async def upsert_connection_sitemap(
        self, connection_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Upsert a connection's site map."""
        return await self._put(f"connections/{connection_id}/sitemap", json=data)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    async def test_connection(self, data: dict[str, Any]) -> dict[str, Any]:
        """Test a new connection definition."""
        return await self._post("connections/actions/test", json=data)

    async def run_connection_action(
        self, command: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Run a free-form connection action by command name."""
        return await self._post(f"connections/actions/{command}", json=data or {})

    async def test_existing_connection(
        self, connection_id: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Test an existing connection."""
        return await self._post(f"connections/{connection_id}/actions/test", json=data or {})

    async def run_existing_connection_action(
        self,
        connection_id: str,
        command: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run an action against an existing connection."""
        return await self._post(f"connections/{connection_id}/actions/{command}", json=data or {})

    async def test_existing_connection_schema(
        self, connection_id: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Test an existing connection's schema."""
        return await self._post(f"connections/{connection_id}/schema/actions/test", json=data or {})
