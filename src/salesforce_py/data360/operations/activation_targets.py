"""Activation Targets Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class ActivationTargetsOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/activation-targets*`` endpoints."""

    async def get_activation_targets(
        self,
        *,
        batch_size: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
        filters: str | None = None,
    ) -> dict[str, Any]:
        """List activation targets.

        Args:
            batch_size: Number of results (1-200, default 20).
            offset: Rows to skip.
            order_by: Sort order on ``createdDate``.
            filters: Filter expression (``masterLabel``, ``targetStatus``,
                ``connectionType``, ``platformName``).
        """
        return await self._get(
            "activation-targets",
            params={
                "batchSize": batch_size,
                "offset": offset,
                "orderBy": order_by,
                "filters": filters,
            },
        )

    async def create_activation_target(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create an activation target."""
        return await self._post("activation-targets", json=data)

    async def get_activation_target(self, activation_target_id: str) -> dict[str, Any]:
        """Get an activation target by ID or developer name."""
        return await self._get(f"activation-targets/{activation_target_id}")

    async def update_activation_target(
        self, activation_target_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update an activation target by ID or developer name."""
        return await self._patch(f"activation-targets/{activation_target_id}", json=data)
