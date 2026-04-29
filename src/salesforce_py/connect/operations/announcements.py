"""Chatter Announcements Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class AnnouncementsOperations(ConnectBaseOperations):
    """Wrapper for ``/chatter/announcements/`` endpoints.

    An announcement highlights information in a designated location
    (typically a group). Users can discuss, like, and comment on an
    announcement. Deleting the underlying feed post deletes the
    announcement.

    Community-scoped variants are supported via ``community_id``.
    All methods are async.
    """

    @staticmethod
    def _prefix(community_id: str | None) -> str:
        return f"communities/{community_id}/" if community_id else ""

    async def list_announcements(
        self,
        parent_id: str,
        *,
        page: int | None = None,
        page_size: int = 25,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get announcements for a parent entity (typically a group).

        Args:
            parent_id: ID of the parent entity (e.g. a group ID).
            page: Zero-based page number.
            page_size: Number of announcements per page.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Announcement Page dict.
        """
        parent_id = self._ensure_18(parent_id)
        params: dict[str, Any] = {"parentId": parent_id, "pageSize": page_size}
        if page is not None:
            params["page"] = page
        return await self._get(
            f"{self._prefix(community_id)}chatter/announcements", params=params
        )

    async def create_announcement(
        self,
        parent_id: str,
        body: str,
        expiration_date: str,
        *,
        send_emails: bool | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Create an announcement with a new body.

        Args:
            parent_id: ID of the parent entity (e.g. group ID, 15 or 18
                characters).
            body: Plain-text announcement body.
            expiration_date: ISO 8601 date/time — the announcement
                displays until 11:59 p.m. on this date.
            send_emails: Whether to email group members (ignores their
                individual email settings).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Announcement dict.
        """
        parent_id = self._ensure_18(parent_id)
        payload: dict[str, Any] = {
            "parentId": parent_id,
            "expirationDate": expiration_date,
            "body": {"messageSegments": [{"type": "Text", "text": body}]},
        }
        if send_emails is not None:
            payload["sendEmails"] = send_emails
        return await self._post(
            f"{self._prefix(community_id)}chatter/announcements", json=payload
        )

    async def create_announcement_from_feed_item(
        self,
        feed_item_id: str,
        expiration_date: str,
        *,
        send_emails: bool | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Create an announcement backed by an existing feed item.

        Args:
            feed_item_id: ID of an ``AdvancedTextPost`` feed item
                (15 or 18 characters).
            expiration_date: ISO 8601 date/time.
            send_emails: Whether to send emails to group members.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Announcement dict.
        """
        feed_item_id = self._ensure_18(feed_item_id)
        payload: dict[str, Any] = {
            "feedItemId": feed_item_id,
            "expirationDate": expiration_date,
        }
        if send_emails is not None:
            payload["sendEmails"] = send_emails
        return await self._post(
            f"{self._prefix(community_id)}chatter/announcements", json=payload
        )

    async def get_announcement(
        self,
        announcement_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get a single announcement.

        Args:
            announcement_id: Announcement ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Announcement dict.
        """
        announcement_id = self._ensure_18(announcement_id)
        return await self._get(
            f"{self._prefix(community_id)}chatter/announcements/{announcement_id}"
        )

    async def update_announcement(
        self,
        announcement_id: str,
        *,
        expiration_date: str | None = None,
        is_archived: bool | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Update an announcement's expiration date or archive status.

        Args:
            announcement_id: Announcement ID (15 or 18 characters).
            expiration_date: Updated ISO 8601 expiration date/time.
            is_archived: Whether the announcement is archived.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Updated Announcement dict.
        """
        announcement_id = self._ensure_18(announcement_id)
        payload: dict[str, Any] = {}
        if expiration_date is not None:
            payload["expirationDate"] = expiration_date
        if is_archived is not None:
            payload["isArchived"] = is_archived
        return await self._patch(
            f"{self._prefix(community_id)}chatter/announcements/{announcement_id}",
            json=payload,
        )

    async def delete_announcement(
        self,
        announcement_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Delete an announcement.

        Also deletes the underlying feed post.

        Args:
            announcement_id: Announcement ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Empty dict on success.
        """
        announcement_id = self._ensure_18(announcement_id)
        return await self._delete(
            f"{self._prefix(community_id)}chatter/announcements/{announcement_id}"
        )
