"""Commerce Context operations.

Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
prefix) — the client supplies a dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class CommerceContextOperations(ConnectBaseOperations):
    """Wrapper for ``/commerce/webstores/{id}/application-context`` and
    ``/commerce/webstores/{id}/session-context`` endpoints.
    """

    def _base(self, webstore_id: str) -> str:
        return f"commerce/webstores/{self._ensure_18(webstore_id)}"

    async def get_application_context(self, webstore_id: str) -> dict[str, Any]:
        """Get application context information for a Commerce store."""
        return await self._get(f"{self._base(webstore_id)}/application-context")

    async def get_session_context(self, webstore_id: str) -> dict[str, Any]:
        """Get session context information for a Commerce store."""
        return await self._get(f"{self._base(webstore_id)}/session-context")
