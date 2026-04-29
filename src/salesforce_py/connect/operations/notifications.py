"""Notifications Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class NotificationsOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/notifications/`` endpoints.

    Covers listing, marking, executing actions on, status querying, and
    type discovery for end-user notifications. All methods are async.
    """

    # ------------------------------------------------------------------
    # Collection: /connect/notifications
    # ------------------------------------------------------------------

    async def list_notifications(
        self,
        *,
        after: str | None = None,
        before: str | None = None,
        size: int | None = None,
        trim_messages: bool | None = None,
    ) -> dict[str, Any]:
        """Get notifications for the context user.

        Args:
            after: ISO 8601 date string; return notifications after this
                time. Cannot be combined with ``before``.
            before: ISO 8601 date string; return notifications before
                this time.
            size: Number of notifications to return (1–50, default 10).
            trim_messages: Whether to trim titles/bodies (True, default)
                or return full content (False).

        Returns:
            Notification Collection dict.
        """
        params: dict[str, Any] = {}
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before
        if size is not None:
            params["size"] = size
        if trim_messages is not None:
            params["trimMessages"] = "true" if trim_messages else "false"
        return await self._get("notifications", params=params)

    async def mark_notifications(
        self,
        *,
        read: bool | None = None,
        seen: bool | None = None,
        before: str | None = None,
        notification_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Mark notifications as read/unread or seen/unseen.

        Either ``before`` or ``notification_ids`` should be supplied —
        they are mutually exclusive per the API. One of ``read`` or
        ``seen`` must be set.

        Args:
            read: ``True`` = read, ``False`` = unread. Marking read also
                marks seen.
            seen: ``True`` = seen, ``False`` = unseen.
            before: ISO 8601 string — mark notifications occurring
                before this time.
            notification_ids: Up to 50 notification IDs to mark.

        Returns:
            Notification Collection dict.
        """
        body: dict[str, Any] = {}
        if read is not None:
            body["read"] = read
        if seen is not None:
            body["seen"] = seen
        if before is not None:
            body["before"] = before
        if notification_ids is not None:
            body["notificationIds"] = self._ensure_18_list(notification_ids)
        return await self._patch("notifications", json=body)

    # ------------------------------------------------------------------
    # Single notification
    # ------------------------------------------------------------------

    async def get_notification(
        self,
        notification_id: str,
        *,
        trim_messages: bool | None = None,
    ) -> dict[str, Any]:
        """Get a single notification.

        Args:
            notification_id: Notification ID (15 or 18 characters).
            trim_messages: Whether to trim title/body.

        Returns:
            Notification dict.
        """
        notification_id = self._ensure_18(notification_id)
        params: dict[str, Any] = {}
        if trim_messages is not None:
            params["trimMessages"] = "true" if trim_messages else "false"
        return await self._get(
            f"notifications/{notification_id}", params=params
        )

    async def mark_notification(
        self,
        notification_id: str,
        *,
        read: bool | None = None,
        seen: bool | None = None,
    ) -> dict[str, Any]:
        """Mark a single notification as read/unread or seen/unseen.

        Args:
            notification_id: Notification ID (15 or 18 characters).
            read: ``True`` = read, ``False`` = unread.
            seen: ``True`` = seen, ``False`` = unseen.

        Returns:
            Notification dict.
        """
        notification_id = self._ensure_18(notification_id)
        body: dict[str, Any] = {}
        if read is not None:
            body["read"] = read
        if seen is not None:
            body["seen"] = seen
        return await self._patch(
            f"notifications/{notification_id}", json=body
        )

    async def execute_action(
        self,
        notification_id: str,
        action_key: str,
    ) -> dict[str, Any]:
        """Execute an action on a notification (beta, v66.0+).

        Args:
            notification_id: Notification ID (15 or 18 characters).
            action_key: Action key, retrieved from the notification
                types endpoint.

        Returns:
            Action Result dict.
        """
        notification_id = self._ensure_18(notification_id)
        return await self._post(
            f"notifications/{notification_id}/actions/{action_key}"
        )

    # ------------------------------------------------------------------
    # Status / types
    # ------------------------------------------------------------------

    async def get_status(self) -> dict[str, Any]:
        """Get notification status for the context user.

        Returns:
            Notification Status dict.
        """
        return await self._get("notifications/status")

    async def list_types(self) -> dict[str, Any]:
        """Get supported notification types and their actions (beta, v66.0+).

        Returns:
            Notification Type Collection dict.
        """
        return await self._get("notifications/types")
