"""Experience Cloud Sites Knowledge Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class SitesKnowledgeOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/communities/{communityId}/trending-articles``
    and topic-scoped trending / top-viewed article endpoints.
    """

    async def get_trending_articles(
        self,
        community_id: str,
        *,
        max_results: int | None = None,
    ) -> dict[str, Any]:
        """Get trending articles for an Experience Cloud site.

        Args:
            community_id: Community ID (15 or 18 characters).
            max_results: 0–25, default 5.

        Returns:
            Knowledge Article Version Collection dict.
        """
        community_id = self._ensure_18(community_id)
        params: dict[str, Any] = {}
        if max_results is not None:
            params["maxResults"] = max_results
        return await self._get(
            f"communities/{community_id}/trending-articles", params=params
        )

    async def get_topic_trending_articles(
        self,
        community_id: str,
        topic_id: str,
        *,
        max_results: int | None = None,
    ) -> dict[str, Any]:
        """Get trending articles for a topic within a site.

        Args:
            community_id: Community ID.
            topic_id: Topic ID.
            max_results: 0–25, default 5.

        Returns:
            Knowledge Article Version Collection dict.
        """
        community_id = self._ensure_18(community_id)
        topic_id = self._ensure_18(topic_id)
        params: dict[str, Any] = {}
        if max_results is not None:
            params["maxResults"] = max_results
        return await self._get(
            f"communities/{community_id}/topics/{topic_id}/trending-articles",
            params=params,
        )

    async def get_topic_top_viewed_articles(
        self,
        community_id: str,
        topic_id: str,
        *,
        max_results: int | None = None,
    ) -> dict[str, Any]:
        """Get the top-viewed articles for a topic within a site.

        Args:
            community_id: Community ID.
            topic_id: Topic ID.
            max_results: 0–25, default 5.

        Returns:
            Knowledge Article Version Collection dict.
        """
        community_id = self._ensure_18(community_id)
        topic_id = self._ensure_18(topic_id)
        params: dict[str, Any] = {}
        if max_results is not None:
            params["maxResults"] = max_results
        return await self._get(
            f"communities/{community_id}/topics/{topic_id}/top-viewed-articles",
            params=params,
        )
