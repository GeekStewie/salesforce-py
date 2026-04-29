"""Chatter Feeds Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class FeedsOperations(ConnectBaseOperations):
    """Wrapper for ``/chatter/feeds/`` endpoints.

    Covers the different feed types (bookmarks, company, favorites,
    files, filter, groups, home, landing, mute, news, people, record,
    streams, to, topics, user-profile) and the standard options for
    retrieving the feed URL or its feed elements.

    Community-scoped variants are supported via ``community_id``.
    All methods are async.
    """

    # Valid sort values as defined by the Connect API spec.
    VALID_SORTS = {
        "CreatedDateAsc",
        "CreatedDateDesc",
        "LastModifiedDateDesc",
        "MostViewed",
        "Relevance",
    }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _prefix(community_id: str | None) -> str:
        return f"communities/{community_id}/" if community_id else ""

    def _feed_params(
        self,
        *,
        sort: str | None,
        page_size: int,
        page_token: str | None,
        update_since: str | None,
        recent_comment_count: int | None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"pageSize": page_size}
        if sort is not None:
            params["sort"] = sort
        if page_token is not None:
            params["pageToken"] = page_token
        if update_since is not None:
            params["updatedSince"] = update_since
        if recent_comment_count is not None:
            params["recentCommentCount"] = recent_comment_count
        return params

    async def _feed_elements(
        self,
        path: str,
        *,
        sort: str | None,
        page_size: int,
        page_token: str | None,
        update_since: str | None,
        recent_comment_count: int | None,
    ) -> dict[str, Any]:
        return await self._get(
            path,
            params=self._feed_params(
                sort=sort,
                page_size=page_size,
                page_token=page_token,
                update_since=update_since,
                recent_comment_count=recent_comment_count,
            ),
        )

    # ------------------------------------------------------------------
    # Feeds directory  /chatter/feeds
    # ------------------------------------------------------------------

    async def list_feeds(self, *, community_id: str | None = None) -> dict[str, Any]:
        """List all feeds the context user can view.

        Args:
            community_id: Optional Experience Cloud site ID.

        Returns:
            Feed Directory dict listing the URL for each feed type.
        """
        return await self._get(f"{self._prefix(community_id)}chatter/feeds")

    # ------------------------------------------------------------------
    # Bookmarks feed  /chatter/feeds/bookmarks/{userId}
    # ------------------------------------------------------------------

    async def get_bookmarks_feed(
        self,
        user_id: str = "me",
        *,
        sort: str | None = None,
        page_size: int = 25,
        page_token: str | None = None,
        update_since: str | None = None,
        recent_comment_count: int | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get feed elements from the bookmarks feed.

        Args:
            user_id: Must be the context user's ID or ``"me"``.
            sort: Feed sort order (see :attr:`VALID_SORTS`).
            page_size: Number of elements per page.
            page_token: Opaque pagination token.
            update_since: ISO 8601 timestamp — only return elements
                updated since this time.
            recent_comment_count: Number of recent comments to include
                per element.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Feed Element Page dict.
        """
        user_id = self._ensure_18(user_id)
        return await self._feed_elements(
            f"{self._prefix(community_id)}chatter/feeds/bookmarks/{user_id}/feed-elements",
            sort=sort,
            page_size=page_size,
            page_token=page_token,
            update_since=update_since,
            recent_comment_count=recent_comment_count,
        )

    # ------------------------------------------------------------------
    # Company feed  /chatter/feeds/company
    # ------------------------------------------------------------------

    async def get_company_feed(
        self,
        *,
        sort: str | None = None,
        q: str | None = None,
        page_size: int = 25,
        page_token: str | None = None,
        update_since: str | None = None,
        recent_comment_count: int | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get feed elements from the company feed.

        Args:
            sort: Feed sort order (see :attr:`VALID_SORTS`).
            q: Optional search term.
            page_size: Number of elements per page.
            page_token: Opaque pagination token.
            update_since: ISO 8601 timestamp filter.
            recent_comment_count: Recent comments to include per element.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Feed Element Page dict.
        """
        params = self._feed_params(
            sort=sort,
            page_size=page_size,
            page_token=page_token,
            update_since=update_since,
            recent_comment_count=recent_comment_count,
        )
        if q is not None:
            params["q"] = q
        return await self._get(
            f"{self._prefix(community_id)}chatter/feeds/company/feed-elements",
            params=params,
        )

    # ------------------------------------------------------------------
    # News feed  /chatter/feeds/news/{userId}
    # ------------------------------------------------------------------

    async def get_news_feed(
        self,
        user_id: str = "me",
        *,
        sort: str | None = None,
        page_size: int = 25,
        page_token: str | None = None,
        update_since: str | None = None,
        recent_comment_count: int | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get feed elements from a user's news feed.

        Args:
            user_id: User ID (15 or 18 characters) or ``"me"``.
            sort: Feed sort order.
            page_size: Number of elements per page.
            page_token: Opaque pagination token.
            update_since: ISO 8601 timestamp filter.
            recent_comment_count: Recent comments to include per element.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Feed Element Page dict.
        """
        user_id = self._ensure_18(user_id)
        return await self._feed_elements(
            f"{self._prefix(community_id)}chatter/feeds/news/{user_id}/feed-elements",
            sort=sort,
            page_size=page_size,
            page_token=page_token,
            update_since=update_since,
            recent_comment_count=recent_comment_count,
        )

    # ------------------------------------------------------------------
    # Record feed  /chatter/feeds/record/{recordId}
    # ------------------------------------------------------------------

    async def get_record_feed(
        self,
        record_id: str,
        *,
        sort: str | None = None,
        page_size: int = 25,
        page_token: str | None = None,
        update_since: str | None = None,
        recent_comment_count: int | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get feed elements from a record, group, or user feed.

        Args:
            record_id: Record ID (15 or 18 characters) — can be a group,
                user, object, or file ID.
            sort: Feed sort order.
            page_size: Number of elements per page.
            page_token: Opaque pagination token.
            update_since: ISO 8601 timestamp filter.
            recent_comment_count: Recent comments to include per element.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Feed Element Page dict.
        """
        record_id = self._ensure_18(record_id)
        return await self._feed_elements(
            f"{self._prefix(community_id)}chatter/feeds/record/{record_id}/feed-elements",
            sort=sort,
            page_size=page_size,
            page_token=page_token,
            update_since=update_since,
            recent_comment_count=recent_comment_count,
        )

    # ------------------------------------------------------------------
    # User profile feed  /chatter/feeds/user-profile/{userId}
    # ------------------------------------------------------------------

    async def get_user_profile_feed(
        self,
        user_id: str = "me",
        *,
        sort: str | None = None,
        page_size: int = 25,
        page_token: str | None = None,
        update_since: str | None = None,
        recent_comment_count: int | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get feed elements created by, parented by, or mentioning a user.

        Args:
            user_id: User ID (15 or 18 characters) or ``"me"``.
            sort: Feed sort order.
            page_size: Number of elements per page.
            page_token: Opaque pagination token.
            update_since: ISO 8601 timestamp filter.
            recent_comment_count: Recent comments to include per element.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Feed Element Page dict.
        """
        user_id = self._ensure_18(user_id)
        return await self._feed_elements(
            f"{self._prefix(community_id)}chatter/feeds/user-profile/{user_id}/feed-elements",
            sort=sort,
            page_size=page_size,
            page_token=page_token,
            update_since=update_since,
            recent_comment_count=recent_comment_count,
        )

    # ------------------------------------------------------------------
    # People feed  /chatter/feeds/people/{userId}
    # ------------------------------------------------------------------

    async def get_people_feed(
        self,
        user_id: str = "me",
        *,
        sort: str | None = None,
        page_size: int = 25,
        page_token: str | None = None,
        update_since: str | None = None,
        recent_comment_count: int | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get feed elements posted by all people the user follows.

        Args:
            user_id: User ID (15 or 18 characters) or ``"me"``.
            sort: Feed sort order.
            page_size: Number of elements per page.
            page_token: Opaque pagination token.
            update_since: ISO 8601 timestamp filter.
            recent_comment_count: Recent comments to include per element.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Feed Element Page dict.
        """
        user_id = self._ensure_18(user_id)
        return await self._feed_elements(
            f"{self._prefix(community_id)}chatter/feeds/people/{user_id}/feed-elements",
            sort=sort,
            page_size=page_size,
            page_token=page_token,
            update_since=update_since,
            recent_comment_count=recent_comment_count,
        )

    # ------------------------------------------------------------------
    # To feed  /chatter/feeds/to/{userId}
    # ------------------------------------------------------------------

    async def get_to_feed(
        self,
        user_id: str = "me",
        *,
        sort: str | None = None,
        page_size: int = 25,
        page_token: str | None = None,
        update_since: str | None = None,
        recent_comment_count: int | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get feed elements in which the user is @mentioned or posted to.

        Args:
            user_id: User ID or ``"me"``.
            sort: Feed sort order.
            page_size: Number of elements per page.
            page_token: Opaque pagination token.
            update_since: ISO 8601 timestamp filter.
            recent_comment_count: Recent comments to include per element.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Feed Element Page dict.
        """
        user_id = self._ensure_18(user_id)
        return await self._feed_elements(
            f"{self._prefix(community_id)}chatter/feeds/to/{user_id}/feed-elements",
            sort=sort,
            page_size=page_size,
            page_token=page_token,
            update_since=update_since,
            recent_comment_count=recent_comment_count,
        )

    # ------------------------------------------------------------------
    # Topics feed  /chatter/feeds/topics/{topicId}
    # ------------------------------------------------------------------

    async def get_topic_feed(
        self,
        topic_id: str,
        *,
        sort: str | None = None,
        page_size: int = 25,
        page_token: str | None = None,
        update_since: str | None = None,
        recent_comment_count: int | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get feed elements for a specific topic.

        Args:
            topic_id: Topic ID (15 or 18 characters).
            sort: Feed sort order.
            page_size: Number of elements per page.
            page_token: Opaque pagination token.
            update_since: ISO 8601 timestamp filter.
            recent_comment_count: Recent comments to include per element.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Feed Element Page dict.
        """
        topic_id = self._ensure_18(topic_id)
        return await self._feed_elements(
            f"{self._prefix(community_id)}chatter/feeds/topics/{topic_id}/feed-elements",
            sort=sort,
            page_size=page_size,
            page_token=page_token,
            update_since=update_since,
            recent_comment_count=recent_comment_count,
        )

    # ------------------------------------------------------------------
    # Favorites feed  /chatter/feeds/favorites/{userId}/{favoriteId}
    # ------------------------------------------------------------------

    async def list_favorites(
        self,
        user_id: str = "me",
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """List a user's favorite feeds.

        Args:
            user_id: User ID or ``"me"``.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Favorite Collection dict.
        """
        user_id = self._ensure_18(user_id)
        return await self._get(f"{self._prefix(community_id)}chatter/feeds/favorites/{user_id}")

    async def get_favorite_feed(
        self,
        favorite_id: str,
        user_id: str = "me",
        *,
        sort: str | None = None,
        page_size: int = 25,
        page_token: str | None = None,
        update_since: str | None = None,
        recent_comment_count: int | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get feed elements for a favorite feed.

        Args:
            favorite_id: Feed favorite ID (15 or 18 characters).
            user_id: User ID or ``"me"``.
            sort: Feed sort order.
            page_size: Number of elements per page.
            page_token: Opaque pagination token.
            update_since: ISO 8601 timestamp filter.
            recent_comment_count: Recent comments to include per element.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Feed Element Page dict.
        """
        user_id = self._ensure_18(user_id)
        favorite_id = self._ensure_18(favorite_id)
        return await self._feed_elements(
            f"{self._prefix(community_id)}chatter/feeds/favorites/{user_id}/{favorite_id}/feed-elements",
            sort=sort,
            page_size=page_size,
            page_token=page_token,
            update_since=update_since,
            recent_comment_count=recent_comment_count,
        )

    # ------------------------------------------------------------------
    # Streams feed  /chatter/feeds/streams/{streamId}
    # ------------------------------------------------------------------

    async def get_stream_feed(
        self,
        stream_id: str,
        *,
        sort: str | None = None,
        page_size: int = 25,
        page_token: str | None = None,
        update_since: str | None = None,
        recent_comment_count: int | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get feed elements for a Chatter stream.

        Args:
            stream_id: Stream ID (15 or 18 characters).
            sort: Feed sort order.
            page_size: Number of elements per page.
            page_token: Opaque pagination token.
            update_since: ISO 8601 timestamp filter.
            recent_comment_count: Recent comments to include per element.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Feed Element Page dict.
        """
        stream_id = self._ensure_18(stream_id)
        return await self._feed_elements(
            f"{self._prefix(community_id)}chatter/feeds/streams/{stream_id}/feed-elements",
            sort=sort,
            page_size=page_size,
            page_token=page_token,
            update_since=update_since,
            recent_comment_count=recent_comment_count,
        )

    # ------------------------------------------------------------------
    # Mute feed  /chatter/feeds/mute/{userId}
    # ------------------------------------------------------------------

    async def get_mute_feed(
        self,
        user_id: str = "me",
        *,
        sort: str | None = None,
        page_size: int = 25,
        page_token: str | None = None,
        update_since: str | None = None,
        recent_comment_count: int | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get feed elements the user has muted.

        Args:
            user_id: User ID or ``"me"``.
            sort: Feed sort order.
            page_size: Number of elements per page.
            page_token: Opaque pagination token.
            update_since: ISO 8601 timestamp filter.
            recent_comment_count: Recent comments to include per element.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Feed Element Page dict.
        """
        user_id = self._ensure_18(user_id)
        return await self._feed_elements(
            f"{self._prefix(community_id)}chatter/feeds/mute/{user_id}/feed-elements",
            sort=sort,
            page_size=page_size,
            page_token=page_token,
            update_since=update_since,
            recent_comment_count=recent_comment_count,
        )

    # ------------------------------------------------------------------
    # Groups feed  /chatter/feeds/groups/{userId}
    # ------------------------------------------------------------------

    async def get_groups_feed(
        self,
        user_id: str = "me",
        *,
        sort: str | None = None,
        page_size: int = 25,
        page_token: str | None = None,
        update_since: str | None = None,
        recent_comment_count: int | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get feed elements from all groups a user is a member of.

        Args:
            user_id: User ID or ``"me"``.
            sort: Feed sort order.
            page_size: Number of elements per page.
            page_token: Opaque pagination token.
            update_since: ISO 8601 timestamp filter.
            recent_comment_count: Recent comments to include per element.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Feed Element Page dict.
        """
        user_id = self._ensure_18(user_id)
        return await self._feed_elements(
            f"{self._prefix(community_id)}chatter/feeds/groups/{user_id}/feed-elements",
            sort=sort,
            page_size=page_size,
            page_token=page_token,
            update_since=update_since,
            recent_comment_count=recent_comment_count,
        )
