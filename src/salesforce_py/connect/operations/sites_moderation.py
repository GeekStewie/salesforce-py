"""Experience Cloud Sites Moderation Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class SitesModerationOperations(ConnectBaseOperations):
    """Wrapper for Experience Cloud site moderation endpoints.

    Covers flagged-file moderation (get flags, flag a file, unflag),
    flagged-file discovery, and per-user audit statistics.
    """

    # ------------------------------------------------------------------
    # /files/{fileId}/moderation-flags
    # ------------------------------------------------------------------

    async def get_file_flags(
        self,
        community_id: str,
        file_id: str,
        *,
        page: str | None = None,
        page_size: int | None = None,
        visibility: str | None = None,
    ) -> dict[str, Any]:
        """Get moderation flags for a file.

        Args:
            community_id: Community ID.
            file_id: File ID.
            page: Page token.
            page_size: Number of items per page (1–100).
            visibility: ``ModeratorsOnly`` or ``SelfAndModerators``.

        Returns:
            Moderation Flags dict.
        """
        community_id = self._ensure_18(community_id)
        file_id = self._ensure_18(file_id)
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["pageSize"] = page_size
        if visibility is not None:
            params["visibility"] = visibility
        return await self._get(
            f"communities/{community_id}/files/{file_id}/moderation-flags",
            params=params,
        )

    async def flag_file(
        self,
        community_id: str,
        file_id: str,
        *,
        note: str | None = None,
        flag_type: str | None = None,
        visibility: str | None = None,
    ) -> dict[str, Any]:
        """Flag a file for moderation.

        Args:
            community_id: Community ID.
            file_id: File ID.
            note: Flag note (up to 4,000 characters).
            flag_type: ``FlagAsInappropriate`` or ``FlagAsSpam``.
            visibility: ``ModeratorsOnly`` or ``SelfAndModerators``.

        Returns:
            Moderation Flags dict.
        """
        community_id = self._ensure_18(community_id)
        file_id = self._ensure_18(file_id)
        body: dict[str, Any] = {}
        if note is not None:
            body["note"] = note
        if flag_type is not None:
            body["type"] = flag_type
        if visibility is not None:
            body["visibility"] = visibility
        return await self._post(
            f"communities/{community_id}/files/{file_id}/moderation-flags",
            json=body,
        )

    async def unflag_file(
        self,
        community_id: str,
        file_id: str,
        *,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Remove moderation flags from a file.

        Args:
            community_id: Community ID.
            file_id: File ID.
            user_id: Specific user's flag to remove. If omitted and the
                caller is a moderator, all flags on the file are
                removed.

        Returns:
            Empty dict on success.
        """
        community_id = self._ensure_18(community_id)
        file_id = self._ensure_18(file_id)
        params: dict[str, Any] = {}
        if user_id is not None:
            params["userId"] = self._ensure_18(user_id)
        return await self._delete(
            f"communities/{community_id}/files/{file_id}/moderation-flags",
            params=params,
        )

    # ------------------------------------------------------------------
    # Flagged files listing
    # ------------------------------------------------------------------

    async def get_flagged_files(
        self,
        community_id: str,
        *,
        page: int | None = None,
        page_size: int | None = None,
        q: str | None = None,
    ) -> dict[str, Any]:
        """List files currently flagged in an Experience Cloud site.

        Args:
            community_id: Community ID.
            page: Page number (zero-based).
            page_size: Items per page (1–100).
            q: Filter query string (minimum 2 characters).

        Returns:
            File Summary dict.
        """
        community_id = self._ensure_18(community_id)
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["pageSize"] = page_size
        if q is not None:
            params["q"] = q
        return await self._get(
            f"communities/{community_id}/files/moderation", params=params
        )

    # ------------------------------------------------------------------
    # User audit stats
    # ------------------------------------------------------------------

    async def get_user_audit_counts(
        self,
        community_id: str,
        user_id: str,
    ) -> dict[str, Any]:
        """Get moderation audit statistics for a user.

        Args:
            community_id: Community ID.
            user_id: User ID (15 or 18 characters).

        Returns:
            Moderation Audit Record Count dict.
        """
        community_id = self._ensure_18(community_id)
        user_id = self._ensure_18(user_id)
        return await self._get(
            f"communities/{community_id}/chatter/users/{user_id}/audit-actions/counts"
        )
