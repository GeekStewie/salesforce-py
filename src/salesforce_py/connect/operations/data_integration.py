"""Data Integration Connect API operations.

Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
prefix) — the client supplies a dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class DataIntegrationOperations(ConnectBaseOperations):
    """Wrapper for ``/data-integration/licensed-objects`` endpoints (v42.0+)."""

    async def list_licensed_objects(self) -> dict[str, Any]:
        """Get external object names of active packages for credit details.

        Returns:
            Data Integration Credit Objects dict.
        """
        return await self._get("data-integration/licensed-objects")

    async def get_contract_credit(
        self, external_object_name: str
    ) -> dict[str, Any]:
        """Get credit details for a contract.

        Args:
            external_object_name: External object name (from
                :meth:`list_licensed_objects`).

        Returns:
            Data Integration Credit dict.
        """
        return await self._get(
            f"data-integration/licensed-objects/{external_object_name}/contracts/current"
        )
