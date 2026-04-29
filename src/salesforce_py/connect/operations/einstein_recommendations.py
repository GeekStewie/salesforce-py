"""Einstein Recommendation Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class EinsteinRecommendationsOperations(ConnectBaseOperations):
    """Wrapper for Einstein Article & Reply Recommendations runtime metrics (v52.0+)."""

    async def get_article_recommendations_metrics(self) -> dict[str, Any]:
        """Get Einstein Article Recommendations runtime metrics for the case channel.

        Returns:
            Article Recommendations Runtime Metrics dict.
        """
        return await self._get("article-recommendations/metrics/runtime/case")

    async def get_reply_recommendations_metrics(self) -> dict[str, Any]:
        """Get Einstein Reply Recommendations runtime metrics for the chat channel.

        Returns:
            Reply Recommendations Metrics dict.
        """
        return await self._get("reply-recommendations/metrics/runtime/chat")
