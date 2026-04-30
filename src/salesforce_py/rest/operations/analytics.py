"""Analytics — Reports, Dashboards, and Analytics folders.

Covers:

- ``/services/data/vXX.X/analytics`` — Reports and Dashboards REST API root
  (see Salesforce Reports and Dashboards REST API Developer Guide).
- ``/services/data/vXX.X/folders`` — Analytics folders API for report and
  dashboard folders.
- ``/services/data/vXX.X/wave`` — Analytics REST API (Wave / CRM Analytics).
- ``/services/data/vXX.X/smartdatadiscovery`` — Insights API for descriptive /
  diagnostic insights.
- ``/services/data/vXX.X/eclair`` — Geodata definitions for charts.
- ``/services/data/vXX.X/jsonxform`` — Tableau template rule transformation.

This wrapper exposes thin catch-all helpers rather than re-implementing the
full Analytics / Reports and Dashboards API surface. For anything beyond the
directory endpoints, callers can reach straight through via the helpers
below (which accept arbitrary sub-paths and bodies).
"""

from __future__ import annotations

from typing import Any

from salesforce_py.rest.base import RestBaseOperations


class AnalyticsOperations(RestBaseOperations):
    """Wrapper for analytics-family directory + passthrough endpoints."""

    # ------------------------------------------------------------------
    # Reports and Dashboards
    # ------------------------------------------------------------------

    async def get(
        self, subpath: str = "", *, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Issue a GET against ``/analytics/{subpath}``.

        Use this to read reports, dashboards, snapshots, notifications, etc.
        """
        path = "analytics" if not subpath else f"analytics/{subpath.lstrip('/')}"
        return await self._get(path, params=params)

    async def post(
        self,
        subpath: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Issue a POST against ``/analytics/{subpath}``."""
        return await self._post(f"analytics/{subpath.lstrip('/')}", json=json, params=params)

    async def patch(
        self,
        subpath: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Issue a PATCH against ``/analytics/{subpath}``."""
        return await self._patch(f"analytics/{subpath.lstrip('/')}", json=json, params=params)

    async def put(
        self,
        subpath: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Issue a PUT against ``/analytics/{subpath}``."""
        return await self._put(f"analytics/{subpath.lstrip('/')}", json=json, params=params)

    async def delete(self, subpath: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Issue a DELETE against ``/analytics/{subpath}``."""
        return await self._delete(f"analytics/{subpath.lstrip('/')}", params=params)


class FoldersOperations(RestBaseOperations):
    """Wrapper for ``/folders`` — report and dashboard folder management."""

    async def list_folders(
        self, *, folder_type: str | None = None, page_token: str | None = None
    ) -> dict[str, Any]:
        """List analytics folders accessible to the user.

        Args:
            folder_type: Filter by folder type (``report``, ``dashboard``).
            page_token: Continuation token from a previous page.
        """
        return await self._get("folders", params={"type": folder_type, "page": page_token})

    async def get_folder(self, folder_id: str) -> dict[str, Any]:
        """Return metadata for a specific folder."""
        return await self._get(f"folders/{folder_id}")

    async def create_folder(self, folder: dict[str, Any]) -> dict[str, Any]:
        """Create a new analytics folder."""
        return await self._post("folders", json=folder)

    async def update_folder(self, folder_id: str, folder: dict[str, Any]) -> dict[str, Any]:
        """Update an existing analytics folder."""
        return await self._patch(f"folders/{folder_id}", json=folder)

    async def delete_folder(self, folder_id: str) -> dict[str, Any]:
        """Delete an analytics folder."""
        return await self._delete(f"folders/{folder_id}")

    async def list_folder_children(self, folder_id: str) -> dict[str, Any]:
        """List the reports / dashboards in a folder."""
        return await self._get(f"folders/{folder_id}/children")


class WaveOperations(RestBaseOperations):
    """Wrapper for ``/wave`` — Analytics REST API (CRM Analytics / Wave)."""

    async def get(
        self, subpath: str = "", *, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Issue a GET against ``/wave/{subpath}``."""
        path = "wave" if not subpath else f"wave/{subpath.lstrip('/')}"
        return await self._get(path, params=params)

    async def post(
        self,
        subpath: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Issue a POST against ``/wave/{subpath}``."""
        return await self._post(f"wave/{subpath.lstrip('/')}", json=json, params=params)

    async def patch(
        self,
        subpath: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Issue a PATCH against ``/wave/{subpath}``."""
        return await self._patch(f"wave/{subpath.lstrip('/')}", json=json, params=params)

    async def put(
        self,
        subpath: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Issue a PUT against ``/wave/{subpath}``."""
        return await self._put(f"wave/{subpath.lstrip('/')}", json=json, params=params)

    async def delete(self, subpath: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Issue a DELETE against ``/wave/{subpath}``."""
        return await self._delete(f"wave/{subpath.lstrip('/')}", params=params)


class SmartDataDiscoveryOperations(RestBaseOperations):
    """Wrapper for ``/smartdatadiscovery`` — Insights API."""

    async def get(
        self, subpath: str = "", *, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Issue a GET against ``/smartdatadiscovery/{subpath}``."""
        path = "smartdatadiscovery" if not subpath else f"smartdatadiscovery/{subpath.lstrip('/')}"
        return await self._get(path, params=params)

    async def post(
        self,
        subpath: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Issue a POST against ``/smartdatadiscovery/{subpath}``."""
        return await self._post(
            f"smartdatadiscovery/{subpath.lstrip('/')}", json=json, params=params
        )


class EclairOperations(RestBaseOperations):
    """Wrapper for ``/eclair`` — chart geodata definitions."""

    async def list_geodata(self) -> dict[str, Any]:
        """Return all geodata definitions accessible to the user."""
        return await self._get("eclair/geodata")

    async def get_geodata(self, geodata_id: str) -> dict[str, Any]:
        """Return a specific geodata definition by ID."""
        return await self._get(f"eclair/geodata/{geodata_id}")


class JsonxformOperations(RestBaseOperations):
    """Wrapper for ``/jsonxform`` — Tableau template rule transformation."""

    async def transform(self, body: dict[str, Any]) -> dict[str, Any]:
        """Test a rule in a Tableau template via the jsonxform endpoint."""
        return await self._post("jsonxform", json=body)
