"""Managed Topics Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class ManagedTopicsOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/communities/{communityId}/managed-topics`` endpoints.

    Managed topics support three types: ``Content``, ``Featured``,
    ``Navigational`` — and up to eight levels of navigational topic
    hierarchy. All methods are async.
    """

    async def list_managed_topics(
        self,
        community_id: str,
        *,
        managed_topic_type: str | None = None,
        depth: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        record_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """List managed topics for a site.

        Args:
            community_id: Community ID (15 or 18 characters).
            managed_topic_type: ``Content``, ``Featured``, or
                ``Navigational``.
            depth: Depth 1–8 for hierarchy retrieval.
            page: Zero-based page number.
            page_size: Items per page (1–100, default 50).
            record_ids: Up to 100 topic IDs associated with the managed
                topics.

        Returns:
            Managed Topic Collection dict.
        """
        community_id = self._ensure_18(community_id)
        params: dict[str, Any] = {}
        if managed_topic_type is not None:
            params["managedTopicType"] = managed_topic_type
        if depth is not None:
            params["depth"] = depth
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["pageSize"] = page_size
        if record_ids is not None:
            params["recordIds"] = ",".join(self._ensure_18_list(record_ids))
        return await self._get(f"communities/{community_id}/managed-topics", params=params)

    async def create_managed_topic(
        self,
        community_id: str,
        managed_topic_type: str,
        *,
        name: str | None = None,
        record_id: str | None = None,
        parent_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a managed topic.

        Exactly one of ``name`` or ``record_id`` must be supplied.

        Args:
            community_id: Community ID.
            managed_topic_type: ``Content``, ``Featured``, or
                ``Navigational``.
            name: Name of a new managed topic.
            record_id: Existing topic ID to promote to a managed topic.
            parent_id: Parent managed-topic ID (for Navigational
                hierarchy).

        Returns:
            Managed Topic dict.

        Raises:
            ValueError: If neither or both of ``name`` and ``record_id``
                are supplied.
        """
        if (name is None) == (record_id is None):
            raise ValueError("Provide exactly one of name or record_id.")
        community_id = self._ensure_18(community_id)
        body: dict[str, Any] = {"managedTopicType": managed_topic_type}
        if name is not None:
            body["name"] = name
        if record_id is not None:
            body["recordId"] = self._ensure_18(record_id)
        if parent_id is not None:
            body["parentId"] = self._ensure_18(parent_id)
        return await self._post(f"communities/{community_id}/managed-topics", json=body)

    async def reorder_managed_topics(
        self,
        community_id: str,
        positions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Reorder parent or same-parent managed topics.

        Args:
            community_id: Community ID.
            positions: List of ``{"managedTopicId": ..., "position": N}``
                entries.

        Returns:
            Managed Topic Collection dict.
        """
        community_id = self._ensure_18(community_id)
        body = {"managedTopicPositions": positions}
        return await self._patch(f"communities/{community_id}/managed-topics", json=body)

    async def get_managed_topic(
        self,
        community_id: str,
        managed_topic_id: str,
    ) -> dict[str, Any]:
        """Get a single managed topic.

        Args:
            community_id: Community ID.
            managed_topic_id: Managed-topic ID.

        Returns:
            Managed Topic dict.
        """
        community_id = self._ensure_18(community_id)
        managed_topic_id = self._ensure_18(managed_topic_id)
        return await self._get(f"communities/{community_id}/managed-topics/{managed_topic_id}")

    async def delete_managed_topic(
        self,
        community_id: str,
        managed_topic_id: str,
    ) -> dict[str, Any]:
        """Delete a managed topic.

        Args:
            community_id: Community ID.
            managed_topic_id: Managed-topic ID.

        Returns:
            Empty dict on success.
        """
        community_id = self._ensure_18(community_id)
        managed_topic_id = self._ensure_18(managed_topic_id)
        return await self._delete(f"communities/{community_id}/managed-topics/{managed_topic_id}")
