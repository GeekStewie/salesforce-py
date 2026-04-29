"""Knowledge Article View Stat Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class KnowledgeArticleViewStatOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/knowledge/article/view-stat`` endpoint.

    Increases the view count of a knowledge article by one. If a
    knowledge article *version* ID is supplied, the parent article's
    view count is incremented. Community-scoped variants are supported
    via ``community_id``.
    """

    @staticmethod
    def _prefix(community_id: str | None) -> str:
        return f"communities/{community_id}/" if community_id else ""

    async def increment_view_stat(
        self,
        article_or_version_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Increment an article's view count.

        Args:
            article_or_version_id: ID of the knowledge article or article
                version (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Empty dict on success.
        """
        article_or_version_id = self._ensure_18(article_or_version_id)
        return await self._patch(
            f"{self._prefix(community_id)}knowledge/article/view-stat",
            json={"articleOrVersionId": article_or_version_id},
        )
