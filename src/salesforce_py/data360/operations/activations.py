"""Activations Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class ActivationsOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/activations*`` and ``/ssot/activation-external-platforms``."""

    # ------------------------------------------------------------------
    # Activations
    # ------------------------------------------------------------------

    async def get_activations(
        self,
        *,
        batch_size: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
        filters: str | None = None,
    ) -> dict[str, Any]:
        """List activations."""
        return await self._get(
            "activations",
            params={
                "batchSize": batch_size,
                "offset": offset,
                "orderBy": order_by,
                "filters": filters,
            },
        )

    async def create_activation(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create an activation."""
        return await self._post("activations", json=data)

    async def get_activation(self, activation_id: str) -> dict[str, Any]:
        """Get an activation by ID."""
        return await self._get(f"activations/{activation_id}")

    async def update_activation(self, activation_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update a specific activation by ID."""
        return await self._put(f"activations/{activation_id}", json=data)

    async def delete_activation(self, activation_id: str) -> dict[str, Any]:
        """Delete an activation."""
        return await self._delete(f"activations/{activation_id}")

    async def publish_activation(
        self, activation_id: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Initiate an on-demand publish job for a Batch DMO activation."""
        return await self._post(f"activations/{activation_id}/actions/publish", json=data or {})

    async def get_activation_data(
        self,
        activation_id: str,
        *,
        batch_size: int | None = None,
        offset: int | None = None,
        filters: str | None = None,
    ) -> dict[str, Any]:
        """Query Audience DMO activation records.

        The ``X-Chatter-Entity-Encoding: false`` header is supplied automatically.
        """
        return await self._get(
            f"activations/{activation_id}/data",
            params={"batchSize": batch_size, "offset": offset, "filters": filters},
            headers={"X-Chatter-Entity-Encoding": "false"},
        )

    # ------------------------------------------------------------------
    # External Platforms
    # ------------------------------------------------------------------

    async def get_activation_external_platforms(
        self,
        *,
        batch_size: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
    ) -> dict[str, Any]:
        """List activation external platforms."""
        return await self._get(
            "activation-external-platforms",
            params={
                "batchSize": batch_size,
                "limit": limit,
                "offset": offset,
                "orderBy": order_by,
            },
        )
