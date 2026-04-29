"""Chatter Users Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class UsersOperations(ConnectBaseOperations):
    """Wrapper for ``/chatter/users/`` endpoints.

    Covers user directory, profile info, followers/following,
    conversations, messages, groups, recommendations, and settings.
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
    # Directory  /chatter/users
    # ------------------------------------------------------------------

    async def list_users(
        self,
        *,
        q: str | None = None,
        search_context_id: str | None = None,
        page: int | None = None,
        page_size: int = 25,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """List users in the organisation (or Experience Cloud site).

        Args:
            q: Search term that matches user names.
            search_context_id: Feed item ID providing context for @mention
                completion (results matching thread participants are ranked
                higher).
            page: Zero-based page number.
            page_size: Number of users per page (1–250).
            community_id: Optional Experience Cloud site ID.

        Returns:
            User Page dict.
        """
        params: dict[str, Any] = {"pageSize": page_size}
        if q is not None:
            params["q"] = q
        if search_context_id is not None:
            params["searchContextId"] = self._ensure_18(search_context_id)
        if page is not None:
            params["page"] = page
        return await self._get(f"{self._prefix(community_id)}chatter/users", params=params)

    async def get_user(
        self, user_id: str = "me", *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Get a user's Chatter profile.

        Args:
            user_id: User ID (15 or 18 characters) or ``"me"``.
            community_id: Optional Experience Cloud site ID.

        Returns:
            User Detail dict.
        """
        user_id = self._ensure_18(user_id)
        return await self._get(
            f"{self._prefix(community_id)}chatter/users/{user_id}"
        )

    async def update_user(
        self,
        user_id: str,
        user: dict[str, Any],
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Update a user's Chatter profile ("About Me").

        Args:
            user_id: User ID (15 or 18 characters) or ``"me"``.
            user: User Input payload dict (``aboutMe`` and other fields).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Updated User Detail dict.
        """
        user_id = self._ensure_18(user_id)
        return await self._patch(
            f"{self._prefix(community_id)}chatter/users/{user_id}", json=user
        )

    async def get_users_batch(
        self,
        user_ids: list[str],
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get profile info for multiple users at once.

        Args:
            user_ids: Up to 500 user IDs (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Batch Results dict with one entry per requested ID.
        """
        user_ids = self._ensure_18_list(user_ids)
        return await self._get(
            f"{self._prefix(community_id)}chatter/users/batch/{','.join(user_ids)}"
        )

    # ------------------------------------------------------------------
    # Followers / Following  /chatter/users/{userId}/followers
    # ------------------------------------------------------------------

    async def get_followers(
        self,
        user_id: str = "me",
        *,
        page: int | None = None,
        page_size: int = 25,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get the users following the specified user.

        Args:
            user_id: User ID (15 or 18 characters) or ``"me"``.
            page: Zero-based page number.
            page_size: Number of followers per page.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Follower Page dict.
        """
        user_id = self._ensure_18(user_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if page is not None:
            params["page"] = page
        return await self._get(
            f"{self._prefix(community_id)}chatter/users/{user_id}/followers",
            params=params,
        )

    async def get_following(
        self,
        user_id: str = "me",
        *,
        filter_type: str | None = None,
        page: int | None = None,
        page_size: int = 25,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get the people, groups, records, topics, and files a user follows.

        Args:
            user_id: User ID (15 or 18 characters) or ``"me"``.
            filter_type: Optional filter — ``"People"``, ``"Records"``,
                ``"Topics"``, or ``"Files"``.
            page: Zero-based page number.
            page_size: Number of items per page.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Following Page dict.
        """
        user_id = self._ensure_18(user_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if filter_type is not None:
            params["filter"] = filter_type
        if page is not None:
            params["page"] = page
        return await self._get(
            f"{self._prefix(community_id)}chatter/users/{user_id}/following",
            params=params,
        )

    async def follow_record(
        self,
        record_id: str,
        user_id: str = "me",
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Follow a record, user, group, topic, or file.

        Args:
            record_id: ID of the record to follow (15 or 18 characters).
            user_id: Follower user ID or ``"me"``.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Subscription dict.
        """
        user_id = self._ensure_18(user_id)
        record_id = self._ensure_18(record_id)
        return await self._post(
            f"{self._prefix(community_id)}chatter/users/{user_id}/following",
            json={"subjectId": record_id},
        )

    # ------------------------------------------------------------------
    # Groups  /chatter/users/{userId}/groups
    # ------------------------------------------------------------------

    async def get_user_groups(
        self,
        user_id: str = "me",
        *,
        archive_status: str | None = None,
        page: int | None = None,
        page_size: int = 25,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """List the groups a user is a member of.

        Args:
            user_id: User ID (15 or 18 characters) or ``"me"``.
            archive_status: ``"All"``, ``"Archived"``, or ``"NotArchived"``.
            page: Zero-based page number.
            page_size: Number of groups per page.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Group Membership Page dict.
        """
        user_id = self._ensure_18(user_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if archive_status is not None:
            params["archiveStatus"] = archive_status
        if page is not None:
            params["page"] = page
        return await self._get(
            f"{self._prefix(community_id)}chatter/users/{user_id}/groups",
            params=params,
        )

    # ------------------------------------------------------------------
    # Conversations  /chatter/users/{userId}/conversations
    # ------------------------------------------------------------------

    async def get_conversations(
        self,
        user_id: str = "me",
        *,
        page: int | None = None,
        page_size: int = 25,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get the private conversations for a user.

        Args:
            user_id: User ID (15 or 18 characters) or ``"me"``.
            page: Zero-based page number.
            page_size: Number of conversations per page.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Conversation Summary Page dict.
        """
        user_id = self._ensure_18(user_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if page is not None:
            params["page"] = page
        return await self._get(
            f"{self._prefix(community_id)}chatter/users/{user_id}/conversations",
            params=params,
        )

    async def get_conversation(
        self,
        conversation_id: str,
        user_id: str = "me",
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get a private conversation for the context user.

        Args:
            conversation_id: Conversation ID (15 or 18 characters).
            user_id: User ID or ``"me"``.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Conversation Detail dict.
        """
        user_id = self._ensure_18(user_id)
        conversation_id = self._ensure_18(conversation_id)
        return await self._get(
            f"{self._prefix(community_id)}chatter/users/{user_id}/conversations/{conversation_id}"
        )

    async def update_conversation_status(
        self,
        conversation_id: str,
        read: bool,
        user_id: str = "me",
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Mark a private conversation as read or unread.

        Args:
            conversation_id: Conversation ID (15 or 18 characters).
            read: ``True`` to mark as read, ``False`` for unread.
            user_id: User ID or ``"me"``.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Updated Conversation Detail dict.
        """
        user_id = self._ensure_18(user_id)
        conversation_id = self._ensure_18(conversation_id)
        return await self._patch(
            f"{self._prefix(community_id)}chatter/users/{user_id}/conversations/{conversation_id}",
            json={"read": read},
        )

    async def get_unread_conversation_count(
        self,
        user_id: str = "me",
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get the number of private conversations with unread messages.

        Args:
            user_id: User ID or ``"me"``.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Unread Conversation Count dict with a ``count`` key.
        """
        user_id = self._ensure_18(user_id)
        return await self._get(
            f"{self._prefix(community_id)}chatter/users/{user_id}/conversations/unread-count"
        )

    # ------------------------------------------------------------------
    # Messages  /chatter/users/{userId}/messages
    # ------------------------------------------------------------------

    async def get_messages(
        self,
        user_id: str = "me",
        *,
        conversation_id: str | None = None,
        page: int | None = None,
        page_size: int = 25,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get private messages for a user or within a conversation.

        Args:
            user_id: User ID (15 or 18 characters) or ``"me"``.
            conversation_id: Optional conversation ID to filter by.
            page: Zero-based page number.
            page_size: Number of messages per page.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Chatter Message Page dict.
        """
        user_id = self._ensure_18(user_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if conversation_id is not None:
            params["conversationId"] = self._ensure_18(conversation_id)
        if page is not None:
            params["page"] = page
        return await self._get(
            f"{self._prefix(community_id)}chatter/users/{user_id}/messages",
            params=params,
        )

    async def send_message(
        self,
        body: str,
        *,
        recipient_ids: list[str] | None = None,
        in_reply_to_id: str | None = None,
        user_id: str = "me",
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Send a private message to one or more users or a conversation.

        Provide either ``recipient_ids`` (new conversation) or
        ``in_reply_to_id`` (reply to an existing message).

        Args:
            body: Plain-text message body.
            recipient_ids: User IDs to address (15 or 18 characters each).
            in_reply_to_id: ID of an existing message to reply to.
            user_id: Sender user ID or ``"me"``.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Chatter Message dict.
        """
        user_id = self._ensure_18(user_id)
        payload: dict[str, Any] = {"body": body}
        if recipient_ids is not None:
            payload["recipients"] = ",".join(self._ensure_18_list(recipient_ids))
        if in_reply_to_id is not None:
            payload["inReplyTo"] = self._ensure_18(in_reply_to_id)
        return await self._post(
            f"{self._prefix(community_id)}chatter/users/{user_id}/messages",
            json=payload,
        )

    async def get_message(
        self,
        message_id: str,
        user_id: str = "me",
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get a private message by ID.

        Args:
            message_id: Chatter message ID (15 or 18 characters).
            user_id: User ID or ``"me"``.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Chatter Message dict.
        """
        user_id = self._ensure_18(user_id)
        message_id = self._ensure_18(message_id)
        return await self._get(
            f"{self._prefix(community_id)}chatter/users/{user_id}/messages/{message_id}"
        )

    # ------------------------------------------------------------------
    # Recommendations  /chatter/users/{userId}/recommendations
    # ------------------------------------------------------------------

    async def get_recommendations(
        self,
        user_id: str = "me",
        *,
        action: str | None = None,
        object_category: str | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get Chatter recommendations for the context user.

        Args:
            user_id: User ID or ``"me"``.
            action: Optional action filter — e.g. ``"follow"``, ``"join"``,
                ``"view"``.
            object_category: Optional object category scoped to the action
                (e.g. ``"users"``, ``"groups"``, ``"files"``).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Recommendations Collection dict.
        """
        user_id = self._ensure_18(user_id)
        path = f"{self._prefix(community_id)}chatter/users/{user_id}/recommendations"
        if action:
            path = f"{path}/{action}"
            if object_category:
                path = f"{path}/{object_category}"
        return await self._get(path)

    async def delete_recommendation(
        self,
        action: str,
        object_id: str,
        user_id: str = "me",
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Dismiss a recommendation.

        Args:
            action: Recommendation action — e.g. ``"follow"``, ``"join"``.
            object_id: ID of the recommended object (15 or 18 characters).
            user_id: User ID or ``"me"``.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Empty dict on success.
        """
        user_id = self._ensure_18(user_id)
        object_id = self._ensure_18(object_id)
        return await self._delete(
            f"{self._prefix(community_id)}chatter/users/{user_id}/recommendations/{action}/{object_id}"
        )

    # ------------------------------------------------------------------
    # Settings / Topics  /chatter/users/{userId}/settings and /topics
    # ------------------------------------------------------------------

    async def get_user_settings(
        self, user_id: str = "me", *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Get a user's global Chatter settings.

        Args:
            user_id: User ID or ``"me"``.
            community_id: Optional Experience Cloud site ID.

        Returns:
            User Chatter Settings dict.
        """
        user_id = self._ensure_18(user_id)
        return await self._get(
            f"{self._prefix(community_id)}chatter/users/{user_id}/settings"
        )

    async def get_user_topics(
        self, user_id: str = "me", *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Get up to five topics most recently used by a user.

        Args:
            user_id: User ID or ``"me"``.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Topic Collection dict.
        """
        user_id = self._ensure_18(user_id)
        return await self._get(
            f"{self._prefix(community_id)}chatter/users/{user_id}/topics"
        )

    async def get_knowledgeable_about_topics(
        self, user_id: str = "me", *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Get topics the specified user is knowledgeable about.

        Args:
            user_id: User ID or ``"me"``.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Topic Collection dict.
        """
        user_id = self._ensure_18(user_id)
        return await self._get(
            f"{self._prefix(community_id)}chatter/users/{user_id}/knowledgeable-about-topics"
        )

    async def get_reputation(
        self, user_id: str, community_id: str
    ) -> dict[str, Any]:
        """Get a user's reputation in an Experience Cloud site.

        Args:
            user_id: User ID (15 or 18 characters).
            community_id: Experience Cloud site ID (required).

        Returns:
            Reputation dict.
        """
        user_id = self._ensure_18(user_id)
        return await self._get(
            f"communities/{community_id}/chatter/users/{user_id}/reputation"
        )


class UserProfilesOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/user-profiles/`` endpoints.

    Covers the profile page data (profile, banner-photo, photo).
    Community-scoped variants are supported via ``community_id``.
    All methods are async.
    """

    @staticmethod
    def _prefix(community_id: str | None) -> str:
        return f"communities/{community_id}/" if community_id else ""

    async def get_profile(
        self, user_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Get details about a user's profile.

        Args:
            user_id: User ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            User Profile dict.
        """
        user_id = self._ensure_18(user_id)
        return await self._get(
            f"{self._prefix(community_id)}user-profiles/{user_id}"
        )

    async def get_photo(
        self, user_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Get a user's profile photo metadata.

        Args:
            user_id: User ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Photo metadata dict.
        """
        user_id = self._ensure_18(user_id)
        return await self._get(
            f"{self._prefix(community_id)}user-profiles/{user_id}/photo"
        )

    async def set_photo(
        self,
        user_id: str,
        file_id: str,
        *,
        crop_size: int | None = None,
        crop_x: int | None = None,
        crop_y: int | None = None,
        version_number: int | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Set or crop a user profile photo from an existing file.

        The file must have key prefix ``069`` (ContentDocument) and be an
        image under 2 GB.

        Args:
            user_id: User ID (15 or 18 characters).
            file_id: ContentDocument ID of the image (15 or 18 characters).
            crop_size: Edge length in pixels of the crop square.
            crop_x: X position in pixels from the left edge.
            crop_y: Y position in pixels from the top edge.
            version_number: Specific version of the file to use.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Updated Photo metadata dict.
        """
        user_id = self._ensure_18(user_id)
        file_id = self._ensure_18(file_id)
        payload: dict[str, Any] = {"fileId": file_id}
        if crop_size is not None:
            payload["cropSize"] = crop_size
        if crop_x is not None:
            payload["cropX"] = crop_x
        if crop_y is not None:
            payload["cropY"] = crop_y
        if version_number is not None:
            payload["versionNumber"] = version_number
        return await self._post(
            f"{self._prefix(community_id)}user-profiles/{user_id}/photo",
            json=payload,
        )

    async def delete_photo(
        self, user_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Delete a user's profile photo.

        Args:
            user_id: User ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Empty dict on success.
        """
        user_id = self._ensure_18(user_id)
        return await self._delete(
            f"{self._prefix(community_id)}user-profiles/{user_id}/photo"
        )

    async def get_banner_photo(
        self, user_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Get a user's banner photo metadata.

        Args:
            user_id: User ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Banner Photo metadata dict.
        """
        user_id = self._ensure_18(user_id)
        return await self._get(
            f"{self._prefix(community_id)}user-profiles/{user_id}/banner-photo"
        )

    async def set_banner_photo(
        self,
        user_id: str,
        file_id: str,
        *,
        crop_height: int | None = None,
        crop_width: int | None = None,
        crop_x: int | None = None,
        crop_y: int | None = None,
        version_number: int | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Set or crop a user banner photo from an existing file.

        Args:
            user_id: User ID (15 or 18 characters).
            file_id: ContentDocument ID of the image (15 or 18 characters).
            crop_height: Crop rectangle height in pixels.
            crop_width: Crop rectangle width in pixels.
            crop_x: X position in pixels from the left edge.
            crop_y: Y position in pixels from the top edge.
            version_number: Specific version of the file to use.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Updated Banner Photo metadata dict.
        """
        user_id = self._ensure_18(user_id)
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
        if version_number is not None:
            payload["versionNumber"] = version_number
        return await self._post(
            f"{self._prefix(community_id)}user-profiles/{user_id}/banner-photo",
            json=payload,
        )

    async def delete_banner_photo(
        self, user_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Delete a user's banner photo.

        Args:
            user_id: User ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Empty dict on success.
        """
        user_id = self._ensure_18(user_id)
        return await self._delete(
            f"{self._prefix(community_id)}user-profiles/{user_id}/banner-photo"
        )
