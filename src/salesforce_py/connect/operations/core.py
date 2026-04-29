"""Core Connect API operations — directory and organisation endpoints."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class ConnectCoreOperations(ConnectBaseOperations):
    """Wrapper for the top-level ``/connect`` and ``/connect/organization`` endpoints.

    These resources return a directory of available Connect resources and
    information about the context user's org and settings. All methods are async.
    """

    async def get_directory(self) -> dict[str, Any]:
        """Return the Connect resource directory for the context user.

        Lists the URLs for the org and Experience Cloud site resources
        available to the current user.

        Returns:
            Connect Directory dict with ``communities`` and ``organization``
            URL keys.
        """
        return await self._get("")

    async def get_organization(self) -> dict[str, Any]:
        """Return information about the context user's org and settings.

        Returns:
            Organization dict with ``orgId``, ``name``, ``accessTimeout``,
            ``features``, ``maintenanceInfo``, and ``userSettings`` keys.
        """
        return await self._get("organization")
