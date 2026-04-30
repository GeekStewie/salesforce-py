"""Metadata — ``/services/data/vXX.X/metadata`` pass-through.

Exposes Salesforce Metadata API resources. See the Metadata API Developer
Guide for the full resource catalogue. This wrapper covers the directory
endpoint and exposes generic verbs for everything else.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.rest.base import RestBaseOperations


class MetadataOperations(RestBaseOperations):
    """Pass-through wrapper for ``/metadata``."""

    async def list_resources(self) -> dict[str, Any]:
        """Return the list of metadata resources available for this version."""
        return await self._get("metadata")

    async def get(self, subpath: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Issue a GET against ``/metadata/{subpath}``."""
        return await self._get(f"metadata/{subpath.lstrip('/')}", params=params)

    async def post(
        self,
        subpath: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Issue a POST against ``/metadata/{subpath}``."""
        return await self._post(f"metadata/{subpath.lstrip('/')}", json=json, params=params)

    async def patch(
        self,
        subpath: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Issue a PATCH against ``/metadata/{subpath}``."""
        return await self._patch(f"metadata/{subpath.lstrip('/')}", json=json, params=params)

    async def put(
        self,
        subpath: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Issue a PUT against ``/metadata/{subpath}``."""
        return await self._put(f"metadata/{subpath.lstrip('/')}", json=json, params=params)

    async def delete(self, subpath: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Issue a DELETE against ``/metadata/{subpath}``."""
        return await self._delete(f"metadata/{subpath.lstrip('/')}", params=params)
