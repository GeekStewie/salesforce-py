"""Clean (Data.com) Connect API operations.

Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
prefix) — the client supplies a dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class CleanOperations(ConnectBaseOperations):
    """Wrapper for ``/clean/...`` endpoints (v37.0+)."""

    async def list_data_services(self) -> dict[str, Any]:
        """Get data services associated with active data integration rules.

        Returns:
            Clean Rule Data Service Collection dict.
        """
        return await self._get("clean/data-services")

    async def get_data_service_metrics(self, data_service_id: str) -> dict[str, Any]:
        """Get metrics for a data service.

        Args:
            data_service_id: Data service ID.

        Returns:
            Clean Rule Data Service Metrics Collection dict.
        """
        return await self._get(f"clean/data-services/{data_service_id}/metrics")

    async def get_rule_statuses(self, record_id: str) -> dict[str, Any]:
        """Get active data integration rule statuses for a record.

        Args:
            record_id: Salesforce record ID (15 or 18 characters).

        Returns:
            Clean Rule Status Collection dict.
        """
        record_id = self._ensure_18(record_id)
        return await self._get(f"clean/{record_id}/rules/statuses")
