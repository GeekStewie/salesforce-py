"""Streaming — Streaming Channel push endpoint.

Covers:

- ``/services/data/vXX.X/sobjects/StreamingChannel/{channelId}/push`` — Gets
  subscriber information, and pushes notifications for streaming channels.

(The full Streaming API is a Bayeux / CometD endpoint served from a
separate handshake URL and is outside the scope of this REST wrapper.)
"""

from __future__ import annotations

from typing import Any

from salesforce_py.rest.base import RestBaseOperations


class StreamingChannelPushOperations(RestBaseOperations):
    """Wrapper for ``/sobjects/StreamingChannel/{id}/push``."""

    async def get_subscribers(self, channel_id: str) -> dict[str, Any]:
        """Return subscriber information for a streaming channel."""
        return await self._get(f"sobjects/StreamingChannel/{channel_id}/push")

    async def push_notification(
        self, channel_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Push a generic streaming notification to a streaming channel."""
        return await self._post(
            f"sobjects/StreamingChannel/{channel_id}/push",
            json=payload,
        )
