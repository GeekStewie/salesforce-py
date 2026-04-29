"""Orchestration Connect API operations (v54.0+)."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class OrchestrationOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/interaction/orchestration/...`` endpoints."""

    async def list_instances(
        self,
        *,
        related_orchestration_id: str | None = None,
        related_record_id: str | None = None,
    ) -> dict[str, Any]:
        """Get orchestration instances.

        At least one of ``related_orchestration_id`` (v66.0+) or
        ``related_record_id`` (v54.0+) must be supplied.

        Args:
            related_orchestration_id: Orchestration ID acting as context for
                interactive steps.
            related_record_id: Record ID acting as context for interactive steps.

        Returns:
            Orchestration Instance Collection dict.
        """
        params: dict[str, Any] = {}
        if related_orchestration_id is not None:
            params["relatedOrchestrationId"] = self._ensure_18(related_orchestration_id)
        if related_record_id is not None:
            params["relatedRecordId"] = self._ensure_18(related_record_id)
        return await self._get("interaction/orchestration/instances", params=params)

    async def get_instance_detail(self, instance_id: str) -> dict[str, Any]:
        """Get orchestration instance details (v63.0+).

        Args:
            instance_id: Orchestration instance ID.

        Returns:
            Orchestration Instance dict.
        """
        instance_id = self._ensure_18(instance_id)
        return await self._get(
            "interaction/orchestration/instance/detail",
            params={"instanceId": instance_id},
        )
