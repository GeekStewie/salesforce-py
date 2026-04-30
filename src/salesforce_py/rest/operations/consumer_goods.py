"""Consumer Goods Cloud — object detection + visit recommendations.

Covers:

- ``/services/data/vXX.X/connect/object-detection``
- ``/services/data/vXX.X/connect/visit/recommendations``
"""

from __future__ import annotations

from typing import Any

from salesforce_py.rest.base import RestBaseOperations


class ConsumerGoodsOperations(RestBaseOperations):
    """Wrapper for Consumer Goods Cloud REST endpoints."""

    async def object_detection(
        self,
        body: dict[str, Any],
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Submit an image / scene for object detection analysis."""
        return await self._post("connect/object-detection", json=body, params=params)

    async def get_visit_recommendations(
        self, *, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Return visit recommendations for the context user."""
        return await self._get("connect/visit/recommendations", params=params)

    async def post_visit_recommendations(
        self, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Submit a visit recommendation request body."""
        return await self._post("connect/visit/recommendations", json=body)
