"""Versions — list available Salesforce API versions and per-version resources.

Covers:

- ``/services/data`` — Lists summary information about each Salesforce version
  currently available, including the version, label, and a link to each
  version's root.
- ``/services/data/vXX.X`` — Lists available resources for the specified API
  version, including resource name and URI.

The ``/services/data`` root is the only endpoint in this library that is not
scoped to a specific API version, so this wrapper issues requests directly
against the underlying httpx client (bypassing the ``/services/data/vXX.X/``
base URL) when listing the root version manifest.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.rest.base import RestBaseOperations


class VersionsOperations(RestBaseOperations):
    """Wrapper for ``/services/data`` and ``/services/data/vXX.X`` (root)."""

    async def list_versions(self) -> list[dict[str, Any]]:
        """List summary information about each available Salesforce API version.

        Issues a GET against ``{instance}/services/data`` — *not* scoped to
        any specific version.

        Returns:
            List of dicts with ``version``, ``label``, and ``url`` keys, one
            per available API version.
        """
        client = self._session._client_or_raise()
        url = f"{self._session._instance_url}/services/data"
        response = await client.get(url)
        self._handle_status(response)
        payload = response.json()
        if isinstance(payload, list):
            return payload
        return payload.get("versions", [])

    async def list_resources(self) -> dict[str, Any]:
        """List available resources for the current API version.

        Returns:
            Dict mapping resource name to URI, e.g.
            ``{"sobjects": "/services/data/v66.0/sobjects", "query": "...", ...}``.
        """
        return await self._get("")
