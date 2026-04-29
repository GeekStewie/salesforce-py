"""Topics on Records Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class TopicsOnRecordsOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/records/{recordId}/topics`` endpoints.

    Get, add, remove, and replace topics on records and feed items.
    Community-scoped variants are supported via ``community_id``.
    """

    @staticmethod
    def _prefix(community_id: str | None) -> str:
        return f"communities/{community_id}/" if community_id else ""

    async def list_topics(
        self,
        record_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """List topics assigned to a record or feed item.

        Args:
            record_id: Record or feed-item ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Topic Collection dict.
        """
        record_id = self._ensure_18(record_id)
        return await self._get(
            f"{self._prefix(community_id)}records/{record_id}/topics"
        )

    async def add_topic(
        self,
        record_id: str,
        *,
        topic_id: str | None = None,
        topic_name: str | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Assign a topic to a record or feed item.

        Exactly one of ``topic_id`` or ``topic_name`` must be supplied.

        Args:
            record_id: Record or feed-item ID.
            topic_id: ID of an existing topic.
            topic_name: Name of a new or existing topic.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Topic dict.

        Raises:
            ValueError: If neither or both of ``topic_id`` and
                ``topic_name`` are supplied.
        """
        if (topic_id is None) == (topic_name is None):
            raise ValueError(
                "Provide exactly one of topic_id or topic_name."
            )
        record_id = self._ensure_18(record_id)
        body: dict[str, Any] = {}
        if topic_id is not None:
            body["topicId"] = self._ensure_18(topic_id)
        if topic_name is not None:
            body["topicName"] = topic_name
        return await self._post(
            f"{self._prefix(community_id)}records/{record_id}/topics",
            json=body,
        )

    async def remove_topic(
        self,
        record_id: str,
        topic_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Remove a topic from a record or feed item.

        Args:
            record_id: Record or feed-item ID.
            topic_id: ID of the topic to remove.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Empty dict on success.
        """
        record_id = self._ensure_18(record_id)
        topic_id = self._ensure_18(topic_id)
        return await self._delete(
            f"{self._prefix(community_id)}records/{record_id}/topics",
            params={"topicId": topic_id},
        )

    async def replace_topics(
        self,
        record_id: str,
        topic_names: list[str],
        *,
        topic_suggestions: list[str] | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Replace all topics on a record or feed item.

        Args:
            record_id: Record or feed-item ID.
            topic_names: Up to 10 topic names for a feed item, or 100
                for a record.
            topic_suggestions: Optional suggested topics to improve
                future suggestions.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Topic Collection dict.
        """
        record_id = self._ensure_18(record_id)
        body: dict[str, Any] = {"topicNames": topic_names}
        if topic_suggestions is not None:
            body["topicSuggestions"] = topic_suggestions
        return await self._put(
            f"{self._prefix(community_id)}records/{record_id}/topics",
            json=body,
        )
