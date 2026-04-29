"""Motifs Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class MotifsOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/motifs/`` endpoints.

    Returns URLs for small, medium, and large motif icons for a record
    (and optionally its base color). Community-scoped variants are
    supported via ``community_id``. All methods are async.
    """

    @staticmethod
    def _prefix(community_id: str | None) -> str:
        return f"communities/{community_id}/" if community_id else ""

    async def get_motif(
        self,
        id_or_prefix: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get motif icons for a record ID or object key prefix.

        Args:
            id_or_prefix: A 15/18-character record ID or a 3-character
                object key prefix (e.g. ``"005"``).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Motif dict with ``color``, ``smallIconUrl``, ``mediumIconUrl``,
            and ``largeIconUrl``.
        """
        id_or_prefix = self._ensure_18(id_or_prefix)
        return await self._get(f"{self._prefix(community_id)}motifs/{id_or_prefix}")

    async def get_motifs_batch(
        self,
        ids_or_prefixes: list[str],
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get motif icons for a batch of record IDs and/or key prefixes.

        Args:
            ids_or_prefixes: Mixed list of record IDs and 3-character
                object key prefixes.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Batch Results dict.
        """
        joined = ",".join(self._ensure_18_list(ids_or_prefixes))
        return await self._get(
            f"{self._prefix(community_id)}motifs/batch/{joined}"
        )
