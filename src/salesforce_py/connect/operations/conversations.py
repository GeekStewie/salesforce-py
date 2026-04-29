"""Conversations Connect API operations (v51.0+)."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class ConversationsOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/conversations/...`` and
    ``/connect/conversation/{id}/entries`` endpoints.
    """

    async def get_bulk_upload_statuses(
        self, upload_ids: list[str]
    ) -> dict[str, Any]:
        """Get the statuses of bulk conversation uploads.

        Args:
            upload_ids: Up to 100 upload IDs.

        Returns:
            Conversation Bulk Upload Statuses dict.
        """
        return await self._get(
            "conversations/upload",
            params={"uploadIds": ",".join(upload_ids)},
        )

    async def bulk_upload(
        self, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Bulk upload conversations (up to 512 MB).

        For large binary uploads, use a multipart/form-data request against
        the underlying session — this helper handles the JSON-only path.

        Args:
            body: Bulk conversation upload payload.

        Returns:
            Conversation Bulk Uploads dict.
        """
        return await self._post("conversations/upload", json=body)

    async def get_entries(
        self,
        conversation_identifier: str,
        *,
        end_timestamp: int | None = None,
        query_direction: str | None = None,
        record_limit: int | None = None,
        start_timestamp: int | None = None,
    ) -> dict[str, Any]:
        """Get conversation entries.

        Args:
            conversation_identifier: Conversation identifier.
            end_timestamp: End timestamp in milliseconds.
            query_direction: ``"FromEnd"`` (default) or ``"FromStart"``.
            record_limit: Entries to return, 1–1000 (default 25).
            start_timestamp: Start timestamp in milliseconds (default 0).

        Returns:
            Conversation Entries dict.
        """
        params: dict[str, Any] = {}
        if end_timestamp is not None:
            params["endTimestamp"] = end_timestamp
        if query_direction is not None:
            params["queryDirection"] = query_direction
        if record_limit is not None:
            params["recordLimit"] = record_limit
        if start_timestamp is not None:
            params["startTimestamp"] = start_timestamp
        return await self._get(
            f"conversation/{conversation_identifier}/entries", params=params
        )

    async def update_entries(
        self,
        conversation_identifier: str,
        *,
        conversation_entries_updates: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Update conversation entries.

        Args:
            conversation_identifier: Conversation identifier.
            conversation_entries_updates: List of entry-update dicts, each with
                ``identifier`` and ``messageText`` keys.

        Returns:
            Conversation Entries Update dict.
        """
        payload = {"conversationEntriesUpdates": conversation_entries_updates}
        return await self._patch(
            f"conversation/{conversation_identifier}/entries", json=payload
        )
