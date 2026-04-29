"""Chatter Topics Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class TopicsOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/topics/`` and related topic endpoints.

    Covers topic endorsements, groups contributing to a topic,
    knowledgeable-people lists, and opt-outs. Community-scoped variants
    are supported via the optional ``community_id`` keyword argument.

    All methods are async.
    """

    @staticmethod
    def _prefix(community_id: str | None) -> str:
        return f"communities/{community_id}/" if community_id else ""

    # ------------------------------------------------------------------
    # Endorsements  /connect/topics/{topicId}/endorsements
    # ------------------------------------------------------------------

    async def get_endorsements(
        self,
        topic_id: str,
        *,
        endorsee_id: str | None = None,
        endorser_id: str | None = None,
        page: int | None = None,
        page_size: int = 25,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get endorsements for a topic.

        Args:
            topic_id: Topic ID (15 or 18 characters).
            endorsee_id: Optional user ID to filter to endorsements received.
            endorser_id: Optional user ID to filter to endorsements given.
            page: Zero-based page number.
            page_size: Number of items per page (1–100).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Topic Endorsement Collection dict.
        """
        topic_id = self._ensure_18(topic_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if endorsee_id is not None:
            params["endorseeId"] = self._ensure_18(endorsee_id)
        if endorser_id is not None:
            params["endorserId"] = self._ensure_18(endorser_id)
        if page is not None:
            params["page"] = page
        return await self._get(
            f"{self._prefix(community_id)}topics/{topic_id}/endorsements",
            params=params,
        )

    async def endorse(
        self,
        topic_id: str,
        user_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Endorse a user for a topic.

        Args:
            topic_id: Topic ID (15 or 18 characters).
            user_id: User ID to endorse (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Topic Endorsement dict.
        """
        topic_id = self._ensure_18(topic_id)
        user_id = self._ensure_18(user_id)
        return await self._post(
            f"{self._prefix(community_id)}topics/{topic_id}/endorsements",
            json={"userId": user_id},
        )

    async def get_endorsement(
        self,
        endorsement_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get a single topic endorsement by ID.

        Args:
            endorsement_id: Endorsement ID (key prefix ``0en``).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Topic Endorsement dict.
        """
        endorsement_id = self._ensure_18(endorsement_id)
        return await self._get(f"{self._prefix(community_id)}topic-endorsements/{endorsement_id}")

    async def delete_endorsement(
        self,
        endorsement_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Remove a topic endorsement.

        Args:
            endorsement_id: Endorsement ID (key prefix ``0en``).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Empty dict on success.
        """
        endorsement_id = self._ensure_18(endorsement_id)
        return await self._delete(
            f"{self._prefix(community_id)}topic-endorsements/{endorsement_id}"
        )

    # ------------------------------------------------------------------
    # Groups / Knowledgeable Users  /connect/topics/{topicId}/...
    # ------------------------------------------------------------------

    async def get_topic_groups(
        self,
        topic_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get the five groups that most recently contributed to a topic.

        Args:
            topic_id: Topic ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Group Page dict.
        """
        topic_id = self._ensure_18(topic_id)
        return await self._get(f"{self._prefix(community_id)}topics/{topic_id}/groups")

    async def get_knowledgeable_users(
        self,
        topic_id: str,
        *,
        page: int | None = None,
        page_size: int = 25,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get people knowledgeable about a topic.

        Args:
            topic_id: Topic ID (15 or 18 characters).
            page: Zero-based page number.
            page_size: Number of items per page (1–100).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Knowledgeable People Collection dict.
        """
        topic_id = self._ensure_18(topic_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if page is not None:
            params["page"] = page
        return await self._get(
            f"{self._prefix(community_id)}topics/{topic_id}/knowledgeable-users",
            params=params,
        )

    # ------------------------------------------------------------------
    # Opt-outs  /connect/topics/{topicId}/topic-opt-outs
    # ------------------------------------------------------------------

    async def list_topic_opt_outs(
        self,
        topic_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """List opt-outs from the knowledgeable-people list for a topic.

        Args:
            topic_id: Topic ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Topic Opt Out Collection dict.
        """
        topic_id = self._ensure_18(topic_id)
        return await self._get(f"{self._prefix(community_id)}topics/{topic_id}/topic-opt-outs")

    async def opt_out_of_topic(
        self,
        topic_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Hide the context user from the knowledgeable-people list for a topic.

        Args:
            topic_id: Topic ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Topic Opt Out dict.
        """
        topic_id = self._ensure_18(topic_id)
        return await self._post(f"{self._prefix(community_id)}topics/{topic_id}/topic-opt-outs")

    async def opt_in_to_topic(
        self,
        opt_out_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Opt back in to the knowledgeable-people list by deleting an opt-out.

        Args:
            opt_out_id: Topic opt-out ID (key prefix ``0eb``).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Empty dict on success.
        """
        opt_out_id = self._ensure_18(opt_out_id)
        return await self._delete(f"{self._prefix(community_id)}topic-opt-outs/{opt_out_id}")


class MentionsOperations(ConnectBaseOperations):
    """Wrapper for ``/chatter/mentions/`` endpoints.

    Covers @mention completions (for building autocomplete UIs) and
    validations (to check if a proposed mention is allowed for the user).
    All methods are async.
    """

    @staticmethod
    def _prefix(community_id: str | None) -> str:
        return f"communities/{community_id}/" if community_id else ""

    async def get_completions(
        self,
        q: str,
        *,
        context_id: str | None = None,
        type: str | None = None,
        page: int | None = None,
        page_size: int = 25,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get @mention completion proposals for a search term.

        Args:
            q: Search term (no wildcards). Groups require 2+ characters;
                users have no minimum.
            context_id: Feed item ID (for comment mentions) or feed
                subject ID (for feed-item mentions) to bias results.
            type: ``"All"`` (default), ``"Group"``, or ``"User"``.
            page: Zero-based page number (max 500 results total).
            page_size: Number of items per page (1–100).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Mention Completion Page dict.
        """
        params: dict[str, Any] = {"q": q, "pageSize": page_size}
        if context_id is not None:
            params["contextId"] = self._ensure_18(context_id)
        if type is not None:
            params["type"] = type
        if page is not None:
            params["page"] = page
        return await self._get(
            f"{self._prefix(community_id)}chatter/mentions/completions",
            params=params,
        )

    async def validate(
        self,
        record_ids: list[str],
        *,
        parent_id: str | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Validate whether the context user can mention the given records.

        Args:
            record_ids: User or group IDs to validate (15 or 18 characters).
            parent_id: Optional feed subject or feed item ID providing
                context for the validation.
            community_id: Optional Experience Cloud site ID.

        Returns:
            Mention Validations dict with a ``hasErrors`` boolean and a
            ``mentionValidations`` list.
        """
        record_ids = self._ensure_18_list(record_ids)
        params: dict[str, Any] = {"recordIds": ",".join(record_ids)}
        if parent_id is not None:
            params["parentId"] = self._ensure_18(parent_id)
        return await self._get(
            f"{self._prefix(community_id)}chatter/mentions/validations",
            params=params,
        )


class LikesOperations(ConnectBaseOperations):
    """Wrapper for ``/chatter/likes/`` endpoints.

    Covers like retrieval and deletion. To *create* a like, use the
    Feed Elements or Comments capabilities endpoints. All methods async.
    """

    @staticmethod
    def _prefix(community_id: str | None) -> str:
        return f"communities/{community_id}/" if community_id else ""

    async def get_like(self, like_id: str, *, community_id: str | None = None) -> dict[str, Any]:
        """Get information about a specific like.

        Args:
            like_id: Like ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Like detail dict.
        """
        like_id = self._ensure_18(like_id)
        return await self._get(f"{self._prefix(community_id)}chatter/likes/{like_id}")

    async def delete_like(self, like_id: str, *, community_id: str | None = None) -> dict[str, Any]:
        """Remove a like.

        Args:
            like_id: Like ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Empty dict on success.
        """
        like_id = self._ensure_18(like_id)
        return await self._delete(f"{self._prefix(community_id)}chatter/likes/{like_id}")


class SubscriptionsOperations(ConnectBaseOperations):
    """Wrapper for ``/chatter/subscriptions/`` endpoints.

    A subscription represents a follow relationship (record/topic/user).
    Use this to look up a subscription or unfollow by deleting it.
    All methods are async.
    """

    @staticmethod
    def _prefix(community_id: str | None) -> str:
        return f"communities/{community_id}/" if community_id else ""

    async def get_subscription(
        self, subscription_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Get information about a subscription.

        Args:
            subscription_id: Subscription ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Subscription dict.
        """
        subscription_id = self._ensure_18(subscription_id)
        return await self._get(
            f"{self._prefix(community_id)}chatter/subscriptions/{subscription_id}"
        )

    async def delete_subscription(
        self, subscription_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Unfollow a record, topic, or user by deleting its subscription.

        Args:
            subscription_id: Subscription ID (15 or 18 characters).
            community_id: Optional Experience Cloud site ID.

        Returns:
            Empty dict on success.
        """
        subscription_id = self._ensure_18(subscription_id)
        return await self._delete(
            f"{self._prefix(community_id)}chatter/subscriptions/{subscription_id}"
        )
