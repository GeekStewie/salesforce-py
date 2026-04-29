"""Chatter Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class ChatterOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/chatter/`` endpoints.

    Covers feed items, comments, likes, and user feeds.
    All methods are async.
    """

    async def get_feed_items(
        self,
        *,
        page_size: int = 25,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve the company feed.

        Args:
            page_size: Number of items to return per page.
            page_token: Opaque token returned by a previous call for pagination.

        Returns:
            Feed items page dict with ``currentPageToken``, ``nextPageToken``,
            and ``items`` keys.
        """
        params: dict[str, Any] = {"pageSize": page_size}
        if page_token:
            params["pageToken"] = page_token
        return await self._get("chatter/feeds/company/feed-items", params=params)

    async def get_feed_item(self, feed_item_id: str) -> dict[str, Any]:
        """Retrieve a single feed item by ID.

        Args:
            feed_item_id: Salesforce ID of the feed item (15 or 18 characters).

        Returns:
            Feed item dict.
        """
        feed_item_id = self._ensure_18(feed_item_id)
        return await self._get(f"chatter/feed-items/{feed_item_id}")

    async def post_feed_item(self, body: str, *, subject_id: str = "me") -> dict[str, Any]:
        """Post a text feed item.

        Args:
            body: Plain-text message body.
            subject_id: ID of the record or user to post to (15 or 18 characters),
                or ``"me"`` for the authenticated user's feed.

        Returns:
            Created feed item dict.
        """
        subject_id = self._ensure_18(subject_id)
        payload = {
            "body": {"messageSegments": [{"type": "Text", "text": body}]},
            "feedElementType": "FeedItem",
            "subjectId": subject_id,
        }
        return await self._post("chatter/feed-items", json=payload)

    async def delete_feed_item(self, feed_item_id: str) -> dict[str, Any]:
        """Delete a feed item.

        Args:
            feed_item_id: Salesforce ID of the feed item (15 or 18 characters).

        Returns:
            Empty dict on success.
        """
        feed_item_id = self._ensure_18(feed_item_id)
        return await self._delete(f"chatter/feed-items/{feed_item_id}")

    async def get_comments(self, feed_item_id: str) -> dict[str, Any]:
        """Retrieve comments on a feed item.

        Args:
            feed_item_id: Salesforce ID of the feed item (15 or 18 characters).

        Returns:
            Comments page dict.
        """
        feed_item_id = self._ensure_18(feed_item_id)
        return await self._get(f"chatter/feed-items/{feed_item_id}/comments")

    async def post_comment(self, feed_item_id: str, body: str) -> dict[str, Any]:
        """Add a comment to a feed item.

        Args:
            feed_item_id: Salesforce ID of the feed item (15 or 18 characters).
            body: Plain-text comment body.

        Returns:
            Created comment dict.
        """
        feed_item_id = self._ensure_18(feed_item_id)
        payload = {"body": {"messageSegments": [{"type": "Text", "text": body}]}}
        return await self._post(f"chatter/feed-items/{feed_item_id}/comments", json=payload)

    # ------------------------------------------------------------------
    # Feed elements  /chatter/feed-elements
    # ------------------------------------------------------------------

    async def get_feed_elements(
        self,
        *,
        q: str | None = None,
        page_size: int = 25,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """Get and optionally search all feed elements in the organisation.

        Args:
            q: Search query string.
            page_size: Number of items to return per page.
            page_token: Opaque pagination token from a previous call.

        Returns:
            Feed elements page dict.
        """
        params: dict[str, Any] = {"pageSize": page_size}
        if q:
            params["q"] = q
        if page_token:
            params["pageToken"] = page_token
        return await self._get("chatter/feed-elements", params=params)

    async def post_feed_element(
        self, body: str, subject_id: str, *, feed_element_type: str = "FeedItem"
    ) -> dict[str, Any]:
        """Post a new feed element.

        Args:
            body: Plain-text message body.
            subject_id: ID of the record, group, or user to post to
                (15 or 18 characters).
            feed_element_type: Feed element type (default ``"FeedItem"``).

        Returns:
            Created feed element dict.
        """
        subject_id = self._ensure_18(subject_id)
        payload = {
            "body": {"messageSegments": [{"type": "Text", "text": body}]},
            "feedElementType": feed_element_type,
            "subjectId": subject_id,
        }
        return await self._post("chatter/feed-elements", json=payload)

    async def get_files_feed_elements(
        self,
        user_id: str = "me",
        *,
        page_size: int = 25,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """Get feed elements posted with files by people/groups the user follows.

        Args:
            user_id: User ID or ``"me"`` for the authenticated user.
            page_size: Number of items to return per page.
            page_token: Opaque pagination token from a previous call.

        Returns:
            Feed elements page dict.
        """
        user_id = self._ensure_18(user_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if page_token:
            params["pageToken"] = page_token
        return await self._get(
            f"chatter/feeds/files/{user_id}/feed-elements", params=params
        )

    async def get_news_feed_elements(
        self,
        user_id: str = "me",
        *,
        page_size: int = 25,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """Get the news feed — groups, followed files, records, and users.

        Args:
            user_id: User ID (15 or 18 characters) or ``"me"``.
            page_size: Number of items to return per page.
            page_token: Opaque pagination token from a previous call.

        Returns:
            Feed elements page dict.
        """
        user_id = self._ensure_18(user_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if page_token:
            params["pageToken"] = page_token
        return await self._get(
            f"chatter/feeds/news/{user_id}/feed-elements", params=params
        )

    async def get_record_feed_elements(
        self,
        record_id: str,
        *,
        page_size: int = 25,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """Get feed elements for a specific record (or group by its ID).

        Args:
            record_id: Salesforce record ID or group ID (15 or 18 characters).
            page_size: Number of items to return per page.
            page_token: Opaque pagination token from a previous call.

        Returns:
            Feed elements page dict.
        """
        record_id = self._ensure_18(record_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if page_token:
            params["pageToken"] = page_token
        return await self._get(
            f"chatter/feeds/record/{record_id}/feed-elements", params=params
        )

    async def get_user_profile_feed_elements(
        self,
        user_id: str = "me",
        *,
        page_size: int = 25,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """Get feed elements created by, parented by, or mentioning a user.

        Args:
            user_id: User ID (15 or 18 characters) or ``"me"``.
            page_size: Number of items to return per page.
            page_token: Opaque pagination token from a previous call.

        Returns:
            Feed elements page dict.
        """
        user_id = self._ensure_18(user_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if page_token:
            params["pageToken"] = page_token
        return await self._get(
            f"chatter/feeds/user-profile/{user_id}/feed-elements", params=params
        )
