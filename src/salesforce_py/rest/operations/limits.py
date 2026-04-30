"""Limits — org usage and allocation information.

Covers:

- ``/services/data/vXX.X/limits`` — Lists information about limits in your org.
- ``/services/data/vXX.X/limits/recordCount`` — Lists information about object
  record counts in your org.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.rest.base import RestBaseOperations


class LimitsOperations(RestBaseOperations):
    """Wrapper for ``/limits`` and ``/limits/recordCount``."""

    async def get_limits(self) -> dict[str, Any]:
        """Return the org's allocation + remaining usage for each limit.

        Returns:
            Dict keyed by limit name (``DailyApiRequests``, ``DataStorageMB``,
            ``DailyBulkApiBatches``, etc.), each value carrying ``Max`` and
            ``Remaining`` integers.
        """
        return await self._get("limits")

    async def get_record_count(
        self,
        *,
        sobjects: list[str] | None = None,
    ) -> dict[str, Any]:
        """Return record counts for one or more sObjects.

        Args:
            sobjects: Optional list of sObject API names to restrict the
                response. When omitted, Salesforce returns record counts for
                every sObject the user can access.

        Returns:
            Dict with a ``sObjects`` key holding a list of
            ``{"name": ..., "count": ...}`` entries.
        """
        params: dict[str, Any] | None = None
        if sobjects:
            params = {"sObjects": ",".join(sobjects)}
        return await self._get("limits/recordCount", params=params)
