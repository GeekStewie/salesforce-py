"""Chatter Groups Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class GroupsOperations(ConnectBaseOperations):
    """Wrapper for ``/chatter/groups/`` and related group endpoints.

    Covers group CRUD, members, banner/profile photos, announcements,
    associated records, files, topics, settings, and group invitations.
    Community-scoped variants are supported via the optional
    ``community_id`` keyword argument.

    All methods are async.
    """

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _prefix(community_id: str | None) -> str:
        return f"communities/{community_id}/" if community_id else ""

    # ------------------------------------------------------------------
    # List / create  /chatter/groups
    # ------------------------------------------------------------------

    async def list_groups(
        self,
        *,
        archive_status: str | None = None,
        q: str | None = None,
        page: int | None = None,
        page_size: int = 25,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """List groups in the organisation (or Experience Cloud site).

        Args:
            archive_status: ``"All"``, ``"Archived"``, or ``"NotArchived"``
                (default). Filters the returned groups.
            q: Search term to match group names.
            page: Zero-based page number.
            page_size: Number of items per page (1–250).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Group Page dict with ``currentPageUrl``, ``nextPageUrl``,
            and ``groups`` keys.
        """
        params: dict[str, Any] = {"pageSize": page_size}
        if archive_status is not None:
            params["archiveStatus"] = archive_status
        if q is not None:
            params["q"] = q
        if page is not None:
            params["page"] = page
        return await self._get(f"{self._prefix(community_id)}chatter/groups", params=params)

    async def create_group(
        self,
        group: dict[str, Any],
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a group.

        Args:
            group: Group Input payload dict (``name``, ``visibility``,
                optionally ``description``, ``information``, ``isArchived``,
                ``isBroadcast``, ``canHaveChatterGuests``, etc.).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Created group detail dict.
        """
        return await self._post(f"{self._prefix(community_id)}chatter/groups", json=group)

    async def get_groups_batch(
        self,
        group_ids: list[str],
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get details for multiple groups in a single request.

        Args:
            group_ids: Up to 500 group IDs (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Batch Results dict with one entry per requested ID.
        """
        group_ids = self._ensure_18_list(group_ids)
        return await self._get(
            f"{self._prefix(community_id)}chatter/groups/batch/{','.join(group_ids)}"
        )

    # ------------------------------------------------------------------
    # Single group  /chatter/groups/{groupId}
    # ------------------------------------------------------------------

    async def get_group(self, group_id: str, *, community_id: str | None = None) -> dict[str, Any]:
        """Get information about a group.

        Args:
            group_id: Salesforce group ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Group detail dict.
        """
        group_id = self._ensure_18(group_id)
        return await self._get(f"{self._prefix(community_id)}chatter/groups/{group_id}")

    async def update_group(
        self,
        group_id: str,
        group: dict[str, Any],
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Update group information.

        Args:
            group_id: Salesforce group ID (15 or 18 characters).
            group: Group Input payload dict with properties to update.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Updated group detail dict.
        """
        group_id = self._ensure_18(group_id)
        return await self._patch(
            f"{self._prefix(community_id)}chatter/groups/{group_id}", json=group
        )

    async def delete_group(
        self, group_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Delete a group.

        Args:
            group_id: Salesforce group ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Empty dict on success.
        """
        group_id = self._ensure_18(group_id)
        return await self._delete(f"{self._prefix(community_id)}chatter/groups/{group_id}")

    # ------------------------------------------------------------------
    # Members  /chatter/groups/{groupId}/members
    # ------------------------------------------------------------------

    async def get_group_members(
        self,
        group_id: str,
        *,
        page: int | None = None,
        page_size: int = 25,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """List the members of a group.

        Args:
            group_id: Group ID (15 or 18 characters).
            page: Zero-based page number.
            page_size: Number of members per page (1–250).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Group Member Page dict.
        """
        group_id = self._ensure_18(group_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if page is not None:
            params["page"] = page
        return await self._get(
            f"{self._prefix(community_id)}chatter/groups/{group_id}/members",
            params=params,
        )

    async def add_group_member(
        self,
        group_id: str,
        user_id: str,
        *,
        role: str | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Add a user as a member of a group.

        Context user must be the group owner or a moderator.

        Args:
            group_id: Group ID (15 or 18 characters).
            user_id: User ID (15 or 18 characters).
            role: Optional group role — ``"StandardMember"``,
                ``"GroupManager"``, or ``"GroupOwner"``.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Group Member detail dict.
        """
        group_id = self._ensure_18(group_id)
        user_id = self._ensure_18(user_id)
        payload: dict[str, Any] = {"userId": user_id}
        if role is not None:
            payload["role"] = role
        return await self._post(
            f"{self._prefix(community_id)}chatter/groups/{group_id}/members",
            json=payload,
        )

    # ------------------------------------------------------------------
    # Membership  /chatter/group-memberships/{membershipId}
    # ------------------------------------------------------------------

    async def get_membership(
        self, membership_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Get information about a single group membership.

        Args:
            membership_id: Group membership ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Group Member detail dict.
        """
        membership_id = self._ensure_18(membership_id)
        return await self._get(
            f"{self._prefix(community_id)}chatter/group-memberships/{membership_id}"
        )

    async def update_membership(
        self,
        membership_id: str,
        role: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Update a group member's role.

        Args:
            membership_id: Group membership ID (15 or 18 characters).
            role: New role — ``"StandardMember"``, ``"GroupManager"``,
                or ``"GroupOwner"``.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Updated Group Member detail dict.
        """
        membership_id = self._ensure_18(membership_id)
        return await self._patch(
            f"{self._prefix(community_id)}chatter/group-memberships/{membership_id}",
            json={"role": role},
        )

    async def remove_membership(
        self, membership_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Remove a member from a group by their membership ID.

        Args:
            membership_id: Group membership ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Empty dict on success.
        """
        membership_id = self._ensure_18(membership_id)
        return await self._delete(
            f"{self._prefix(community_id)}chatter/group-memberships/{membership_id}"
        )

    async def get_memberships_batch(
        self,
        membership_ids: list[str],
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get information about multiple memberships in one request.

        Args:
            membership_ids: Up to 500 membership IDs (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Batch Results dict with one entry per requested ID.
        """
        membership_ids = self._ensure_18_list(membership_ids)
        return await self._get(
            f"{self._prefix(community_id)}chatter/group-memberships/batch/{','.join(membership_ids)}"
        )

    # ------------------------------------------------------------------
    # Membership requests  /chatter/groups/{groupId}/members/requests
    # ------------------------------------------------------------------

    async def request_group_membership(
        self, group_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Request membership in a private group.

        Args:
            group_id: Group ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Group Membership Request dict.
        """
        group_id = self._ensure_18(group_id)
        return await self._post(
            f"{self._prefix(community_id)}chatter/groups/{group_id}/members/requests"
        )

    async def list_group_membership_requests(
        self, group_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """List pending membership requests for a private group.

        Args:
            group_id: Group ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Group Membership Request Collection dict.
        """
        group_id = self._ensure_18(group_id)
        return await self._get(
            f"{self._prefix(community_id)}chatter/groups/{group_id}/members/requests"
        )

    async def update_group_membership_request(
        self,
        request_id: str,
        status: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Approve or reject a request to join a private group.

        Args:
            request_id: Group membership request ID (15 or 18 characters).
            status: ``"Accepted"`` or ``"Declined"``.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Updated Group Membership Request dict.
        """
        request_id = self._ensure_18(request_id)
        return await self._patch(
            f"{self._prefix(community_id)}chatter/group-membership-requests/{request_id}",
            json={"status": status},
        )

    # ------------------------------------------------------------------
    # Records  /chatter/groups/{groupId}/records
    # ------------------------------------------------------------------

    async def list_group_records(
        self, group_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """List records associated with a group.

        Args:
            group_id: Group ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Group Record Collection dict.
        """
        group_id = self._ensure_18(group_id)
        return await self._get(f"{self._prefix(community_id)}chatter/groups/{group_id}/records")

    async def add_group_record(
        self,
        group_id: str,
        record_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Associate a record with a group.

        Args:
            group_id: Group ID (15 or 18 characters).
            record_id: Record ID to associate (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Group Record detail dict.
        """
        group_id = self._ensure_18(group_id)
        record_id = self._ensure_18(record_id)
        return await self._post(
            f"{self._prefix(community_id)}chatter/groups/{group_id}/records",
            json={"recordId": record_id},
        )

    async def remove_group_record(
        self, group_record_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Remove the association between a record and a group.

        Args:
            group_record_id: Group record ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Empty dict on success.
        """
        group_record_id = self._ensure_18(group_record_id)
        return await self._delete(
            f"{self._prefix(community_id)}chatter/group-records/{group_record_id}"
        )

    # ------------------------------------------------------------------
    # Topics / Settings / Announcements / Invite
    # ------------------------------------------------------------------

    async def list_group_topics(
        self, group_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Get up to five topics most recently used in a group.

        Args:
            group_id: Group ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Topic Collection dict.
        """
        group_id = self._ensure_18(group_id)
        return await self._get(f"{self._prefix(community_id)}chatter/groups/{group_id}/topics")

    async def get_group_my_settings(
        self, group_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Get the context user's Chatter settings for a group.

        Args:
            group_id: Group ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Group Chatter Settings dict.
        """
        group_id = self._ensure_18(group_id)
        return await self._get(f"{self._prefix(community_id)}chatter/groups/{group_id}/my-settings")

    async def update_group_my_settings(
        self,
        group_id: str,
        settings: dict[str, Any],
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Update the context user's Chatter settings for a group.

        Args:
            group_id: Group ID (15 or 18 characters).
            settings: Group Chatter Settings Input payload dict.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Updated Group Chatter Settings dict.
        """
        group_id = self._ensure_18(group_id)
        return await self._patch(
            f"{self._prefix(community_id)}chatter/groups/{group_id}/my-settings",
            json=settings,
        )

    async def get_group_announcements(
        self,
        group_id: str,
        *,
        page: int | None = None,
        page_size: int = 25,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get announcements posted to a group.

        Args:
            group_id: Group ID (15 or 18 characters).
            page: Zero-based page number.
            page_size: Number of announcements per page.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Announcement Page dict.
        """
        group_id = self._ensure_18(group_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if page is not None:
            params["page"] = page
        return await self._get(
            f"{self._prefix(community_id)}chatter/groups/{group_id}/announcements",
            params=params,
        )

    async def invite_to_group(
        self,
        group_id: str,
        emails: list[str],
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Invite one or more users (by email) to join a group.

        Args:
            group_id: Group ID (15 or 18 characters).
            emails: List of email addresses to invite.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Invite Collection dict.
        """
        group_id = self._ensure_18(group_id)
        return await self._post(
            f"{self._prefix(community_id)}chatter/group/{group_id}/invite",
            json={"emails": emails},
        )

    # ------------------------------------------------------------------
    # Photos  /chatter/groups/{groupId}/photo and /banner-photo
    # ------------------------------------------------------------------

    async def get_group_photo(
        self, group_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Get a group's photo metadata.

        Args:
            group_id: Group ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Photo metadata dict.
        """
        group_id = self._ensure_18(group_id)
        return await self._get(f"{self._prefix(community_id)}chatter/groups/{group_id}/photo")

    async def set_group_photo(
        self,
        group_id: str,
        file_id: str,
        *,
        crop_size: int | None = None,
        crop_x: int | None = None,
        crop_y: int | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Set or crop a group photo from an existing file (key prefix 069).

        Args:
            group_id: Group ID (15 or 18 characters).
            file_id: ContentDocument ID of the image (15 or 18 characters).
            crop_size: Edge length in pixels of the crop square.
            crop_x: X position in pixels from the left edge.
            crop_y: Y position in pixels from the top edge.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Updated Photo metadata dict.
        """
        group_id = self._ensure_18(group_id)
        file_id = self._ensure_18(file_id)
        payload: dict[str, Any] = {"fileId": file_id}
        if crop_size is not None:
            payload["cropSize"] = crop_size
        if crop_x is not None:
            payload["cropX"] = crop_x
        if crop_y is not None:
            payload["cropY"] = crop_y
        return await self._post(
            f"{self._prefix(community_id)}chatter/groups/{group_id}/photo",
            json=payload,
        )

    async def delete_group_photo(
        self, group_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Delete a group's photo.

        Args:
            group_id: Group ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Empty dict on success.
        """
        group_id = self._ensure_18(group_id)
        return await self._delete(f"{self._prefix(community_id)}chatter/groups/{group_id}/photo")

    async def get_group_banner_photo(
        self, group_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Get a group's banner photo metadata.

        Args:
            group_id: Group ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Banner Photo metadata dict.
        """
        group_id = self._ensure_18(group_id)
        return await self._get(
            f"{self._prefix(community_id)}chatter/groups/{group_id}/banner-photo"
        )

    async def set_group_banner_photo(
        self,
        group_id: str,
        file_id: str,
        *,
        crop_height: int | None = None,
        crop_width: int | None = None,
        crop_x: int | None = None,
        crop_y: int | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Set or crop a group banner photo from an existing file.

        Args:
            group_id: Group ID (15 or 18 characters).
            file_id: ContentDocument ID of the image (15 or 18 characters).
            crop_height: Height in pixels of the crop rectangle.
            crop_width: Width in pixels of the crop rectangle.
            crop_x: X position in pixels from the left edge.
            crop_y: Y position in pixels from the top edge.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Updated Banner Photo metadata dict.
        """
        group_id = self._ensure_18(group_id)
        file_id = self._ensure_18(file_id)
        payload: dict[str, Any] = {"fileId": file_id}
        if crop_height is not None:
            payload["cropHeight"] = crop_height
        if crop_width is not None:
            payload["cropWidth"] = crop_width
        if crop_x is not None:
            payload["cropX"] = crop_x
        if crop_y is not None:
            payload["cropY"] = crop_y
        return await self._post(
            f"{self._prefix(community_id)}chatter/groups/{group_id}/banner-photo",
            json=payload,
        )

    async def delete_group_banner_photo(
        self, group_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Delete a group's banner photo.

        Args:
            group_id: Group ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Empty dict on success.
        """
        group_id = self._ensure_18(group_id)
        return await self._delete(
            f"{self._prefix(community_id)}chatter/groups/{group_id}/banner-photo"
        )
