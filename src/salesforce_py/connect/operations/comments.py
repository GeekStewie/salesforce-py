"""Chatter Comments Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class CommentsOperations(ConnectBaseOperations):
    """Wrapper for ``/chatter/comments/`` endpoints.

    Covers single-comment CRUD, batch retrieval, likes, up/down-votes,
    verified status, threaded items, and editability checks.

    To *post* a comment, use the feed-element capability endpoint via
    :class:`ChatterOperations.post_comment` or
    :meth:`FeedElementsOperations.post_comment`. This class handles
    everything else.

    Community-scoped variants are supported via ``community_id``.
    All methods are async.
    """

    @staticmethod
    def _prefix(community_id: str | None) -> str:
        return f"communities/{community_id}/" if community_id else ""

    # ------------------------------------------------------------------
    # Single comment  /chatter/comments/{commentId}
    # ------------------------------------------------------------------

    async def get_comment(
        self, comment_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Get information about a comment.

        Args:
            comment_id: Feed comment ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Comment dict.
        """
        comment_id = self._ensure_18(comment_id)
        return await self._get(f"{self._prefix(community_id)}chatter/comments/{comment_id}")

    async def edit_comment(
        self,
        comment_id: str,
        body: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Edit a comment's body (plain text).

        Available in API version 34.0+. For rich-text edits, PATCH the
        comment endpoint with a richer ``messageSegments`` payload.

        Args:
            comment_id: Feed comment ID (15 or 18 characters).
            body: New plain-text comment body.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Updated Comment dict.
        """
        comment_id = self._ensure_18(comment_id)
        payload = {"body": {"messageSegments": [{"type": "Text", "text": body}]}}
        return await self._patch(
            f"{self._prefix(community_id)}chatter/comments/{comment_id}",
            json=payload,
        )

    async def delete_comment(
        self, comment_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Delete a comment.

        Args:
            comment_id: Feed comment ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Empty dict on success.
        """
        comment_id = self._ensure_18(comment_id)
        return await self._delete(f"{self._prefix(community_id)}chatter/comments/{comment_id}")

    async def get_comments_batch(
        self,
        comment_ids: list[str],
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get information about up to 100 comments in one request.

        Args:
            comment_ids: Comment IDs (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Batch Results dict with one entry per requested ID.
        """
        comment_ids = self._ensure_18_list(comment_ids)
        return await self._get(
            f"{self._prefix(community_id)}chatter/comments/batch/{','.join(comment_ids)}"
        )

    # ------------------------------------------------------------------
    # Likes  /chatter/comments/{commentId}/likes
    # ------------------------------------------------------------------

    async def get_comment_likes(
        self,
        comment_id: str,
        *,
        page: int | None = None,
        page_size: int = 25,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get likes for a comment.

        Args:
            comment_id: Comment ID (15 or 18 characters).
            page: Zero-based page number.
            page_size: Number of likes per page.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Like Page dict.
        """
        comment_id = self._ensure_18(comment_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if page is not None:
            params["page"] = page
        return await self._get(
            f"{self._prefix(community_id)}chatter/comments/{comment_id}/likes",
            params=params,
        )

    async def like_comment(
        self, comment_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Like a comment on behalf of the context user.

        Args:
            comment_id: Comment ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Like dict.
        """
        comment_id = self._ensure_18(comment_id)
        return await self._post(f"{self._prefix(community_id)}chatter/comments/{comment_id}/likes")

    # ------------------------------------------------------------------
    # Up/down votes  /capabilities/up-down-vote
    # ------------------------------------------------------------------

    async def get_up_down_vote(
        self, comment_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Get up/down vote tallies and the context user's vote status.

        Args:
            comment_id: Comment ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Up Down Vote Capability dict.
        """
        comment_id = self._ensure_18(comment_id)
        return await self._get(
            f"{self._prefix(community_id)}chatter/comments/{comment_id}/capabilities/up-down-vote"
        )

    async def set_up_down_vote(
        self,
        comment_id: str,
        vote: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Upvote or downvote a comment.

        Args:
            comment_id: Comment ID (15 or 18 characters).
            vote: ``"Up"``, ``"Down"``, or ``"None"`` (to clear).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Updated Up Down Vote Capability dict.
        """
        comment_id = self._ensure_18(comment_id)
        return await self._post(
            f"{self._prefix(community_id)}chatter/comments/{comment_id}/capabilities/up-down-vote",
            json={"upDownVote": vote},
        )

    # ------------------------------------------------------------------
    # Verified status  /capabilities/verified
    # ------------------------------------------------------------------

    async def get_verified(
        self, comment_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Get the verified status of a comment.

        Args:
            comment_id: Comment ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Verified Capability dict.
        """
        comment_id = self._ensure_18(comment_id)
        return await self._get(
            f"{self._prefix(community_id)}chatter/comments/{comment_id}/capabilities/verified"
        )

    async def set_verified(
        self,
        comment_id: str,
        is_verified: bool,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Mark a comment as verified or unverified.

        Args:
            comment_id: Comment ID (15 or 18 characters).
            is_verified: ``True`` to mark as verified.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Updated Verified Capability dict.
        """
        comment_id = self._ensure_18(comment_id)
        return await self._patch(
            f"{self._prefix(community_id)}chatter/comments/{comment_id}/capabilities/verified",
            json={"isVerified": is_verified},
        )

    # ------------------------------------------------------------------
    # Status capability  /capabilities/status
    # ------------------------------------------------------------------

    async def get_status(
        self, comment_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Get the status capability of a comment (e.g. Published, PendingReview).

        Args:
            comment_id: Comment ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Status Capability dict.
        """
        comment_id = self._ensure_18(comment_id)
        return await self._get(
            f"{self._prefix(community_id)}chatter/comments/{comment_id}/capabilities/status"
        )

    async def set_status(
        self,
        comment_id: str,
        status: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Set the moderation status of a comment.

        Args:
            comment_id: Comment ID (15 or 18 characters).
            status: ``"Published"``, ``"PendingReview"``, or ``"Unpublished"``.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Updated Status Capability dict.
        """
        comment_id = self._ensure_18(comment_id)
        return await self._patch(
            f"{self._prefix(community_id)}chatter/comments/{comment_id}/capabilities/status",
            json={"feedEntityStatus": status},
        )

    # ------------------------------------------------------------------
    # Threaded comments  /capabilities/comments/items
    # ------------------------------------------------------------------

    async def get_threaded_comments(
        self,
        comment_id: str,
        *,
        page: int | None = None,
        page_size: int = 25,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get threaded (child) comments for a comment.

        Args:
            comment_id: Parent comment ID (15 or 18 characters).
            page: Zero-based page number.
            page_size: Number of items per page.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Comment Page dict.
        """
        comment_id = self._ensure_18(comment_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if page is not None:
            params["page"] = page
        return await self._get(
            f"{self._prefix(community_id)}chatter/comments/{comment_id}/capabilities/comments/items",
            params=params,
        )

    async def post_threaded_comment(
        self,
        comment_id: str,
        body: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Post a threaded (reply) comment to an existing comment.

        Args:
            comment_id: Parent comment ID (15 or 18 characters).
            body: Plain-text reply body.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Comment dict.
        """
        comment_id = self._ensure_18(comment_id)
        payload = {"body": {"messageSegments": [{"type": "Text", "text": body}]}}
        return await self._post(
            f"{self._prefix(community_id)}chatter/comments/{comment_id}/capabilities/comments/items",
            json=payload,
        )

    # ------------------------------------------------------------------
    # Editability check  /capabilities/edit/is-editable-by-me
    # ------------------------------------------------------------------

    async def is_editable_by_me(
        self, comment_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Check whether the context user can edit a comment.

        Args:
            comment_id: Comment ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Dict with an ``isEditableByMe`` boolean.
        """
        comment_id = self._ensure_18(comment_id)
        return await self._get(
            f"{self._prefix(community_id)}chatter/comments/{comment_id}/capabilities/edit/is-editable-by-me"
        )
