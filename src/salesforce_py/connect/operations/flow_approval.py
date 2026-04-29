"""Flow Approval Processes Connect API operations (v66.0+)."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class FlowApprovalOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/interaction/flow-approval-process/...``."""

    async def get_status(
        self,
        *,
        process_names: list[str] | None = None,
        related_record_id: str | None = None,
    ) -> dict[str, Any]:
        """Get the status and available actions for flow approval processes.

        Args:
            process_names: List of flow approval process names.
            related_record_id: ID of the related record associated with the
                approval submission.

        Returns:
            Flow Approval Process Collection dict.
        """
        params: dict[str, Any] = {}
        if process_names is not None:
            params["processNames"] = ",".join(process_names)
        if related_record_id is not None:
            params["relatedRecordId"] = self._ensure_18(related_record_id)
        return await self._get("interaction/flow-approval-process/status", params=params)
