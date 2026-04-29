"""Conversation Application Definition Connect API operations (v54.0+)."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class ConversationApplicationOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/conversation-application`` endpoint."""

    async def get_definition(self, integration_name: str) -> dict[str, Any]:
        """Get a conversation application definition and its associated bot.

        Args:
            integration_name: Name of the conversation application.

        Returns:
            Conversation Application Definition Detail dict.
        """
        return await self._get(
            "conversation-application",
            params={"integrationName": integration_name},
        )
