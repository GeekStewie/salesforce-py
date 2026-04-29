"""Quip Related Records Connect API operations (v49.0+)."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class QuipOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/quip/related-records/...`` endpoints."""

    async def get_related_records(self, quip_document_id: str) -> dict[str, Any]:
        """Get records related to a Quip document.

        Args:
            quip_document_id: Quip document ID.

        Returns:
            Quip Related Records dict.
        """
        return await self._get(f"quip/related-records/{quip_document_id}")
