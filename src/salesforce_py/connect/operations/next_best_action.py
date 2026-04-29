"""Next Best Action Connect API operations (v45.0+)."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class NextBestActionOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/recommendations/...`` and
    ``/connect/recommendation-strategies/...`` endpoints.

    Covers getting a recommendation, executing a strategy, and managing
    recommendation reactions.
    """

    # ------------------------------------------------------------------
    # Recommendation
    # ------------------------------------------------------------------

    async def get_recommendation(self, recommendation_id: str) -> dict[str, Any]:
        """Get a recommendation.

        Args:
            recommendation_id: 15- or 18-char recommendation ID.

        Returns:
            Recommendation Object dict.
        """
        recommendation_id = self._ensure_18(recommendation_id)
        return await self._get(f"recommendations/{recommendation_id}")

    # ------------------------------------------------------------------
    # Strategy execution
    # ------------------------------------------------------------------

    async def execute_strategy(
        self,
        strategy_name: str,
        *,
        context_record_id: str | None = None,
        max_results: int | None = None,
        strategy_context: dict[str, str] | None = None,
        debug_trace: bool | None = None,
    ) -> dict[str, Any]:
        """Execute a strategy and return recommendations.

        Args:
            strategy_name: Recommendation strategy developer name.
            context_record_id: ID of the context record (e.g. case ID).
            max_results: Max results, 1–25. Default ``3``.
            strategy_context: Strategy variable/value map.
            debug_trace: Return trace and debug info (``True``/``False``).

        Returns:
            Next Best Action Recommendations dict.
        """
        payload: dict[str, Any] = {}
        if context_record_id is not None:
            payload["contextRecordId"] = self._ensure_18(context_record_id)
        if max_results is not None:
            payload["maxResults"] = max_results
        if strategy_context is not None:
            payload["strategyContext"] = strategy_context
        if debug_trace is not None:
            payload["debugTrace"] = debug_trace
        return await self._post(
            f"recommendation-strategies/{strategy_name}/recommendations",
            json=payload,
        )

    # ------------------------------------------------------------------
    # Reactions collection
    # ------------------------------------------------------------------

    async def list_reactions(
        self,
        *,
        context_record_id: str | None = None,
        created_by_id: str | None = None,
        on_behalf_of_id: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        target_id: str | None = None,
    ) -> dict[str, Any]:
        """Get a list of recommendation reactions (v45.0+).

        Args:
            context_record_id: Filter by context record ID.
            created_by_id: Filter by the user who recorded the reaction.
            on_behalf_of_id: Filter by the user/entity the reaction was on
                behalf of.
            page: Page number (0-based). Default ``0``.
            page_size: Items per page, 1–100. Default ``25``.
            target_id: Filter by recommendation target ID.

        Returns:
            Recommendation Reaction Collection dict.
        """
        params: dict[str, Any] = {}
        if context_record_id is not None:
            params["contextRecordId"] = self._ensure_18(context_record_id)
        if created_by_id is not None:
            params["createdById"] = self._ensure_18(created_by_id)
        if on_behalf_of_id is not None:
            params["onBehalfOfId"] = self._ensure_18(on_behalf_of_id)
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["pageSize"] = page_size
        if target_id is not None:
            params["targetId"] = self._ensure_18(target_id)
        return await self._get(
            "recommendation-strategies/reactions", params=params
        )

    async def record_reaction(
        self,
        *,
        reaction_type: str,
        strategy_name: str,
        target_action_name: str,
        target_id: str,
        context_record_id: str | None = None,
        on_behalf_of_id: str | None = None,
        execution_id: str | None = None,
        external_id: str | None = None,
        target_action_id: str | None = None,
        ai_model: str | None = None,
        recommendation_mode: str | None = None,
        recommendation_score: float | None = None,
    ) -> dict[str, Any]:
        """Record a reaction to a recommendation (v45.0+).

        Args:
            reaction_type: ``"Accepted"`` or ``"Rejected"`` (required).
            strategy_name: Name of the recommendation strategy (required).
            target_action_name: Name of the target action (required).
            target_id: ID of the recommendation being reacted to (required).
            context_record_id: ID of the context record.
            on_behalf_of_id: ID of the user/entity the reaction is on
                behalf of.
            execution_id: ID of the original strategy execution.
            external_id: External ID of the recommendation (v46.0+).
            target_action_id: ID of the target action.
            ai_model: Reserved for future use (v47.0+).
            recommendation_mode: Reserved for future use (v46.0+).
            recommendation_score: Reserved for future use (v46.0+).

        Returns:
            Recommendation Reaction dict.
        """
        payload: dict[str, Any] = {
            "reactionType": reaction_type,
            "strategyName": strategy_name,
            "targetActionName": target_action_name,
            "targetId": self._ensure_18(target_id),
        }
        if context_record_id is not None:
            payload["contextRecordId"] = self._ensure_18(context_record_id)
        if on_behalf_of_id is not None:
            payload["onBehalfOfId"] = self._ensure_18(on_behalf_of_id)
        if execution_id is not None:
            payload["executionId"] = execution_id
        if external_id is not None:
            payload["externalId"] = external_id
        if target_action_id is not None:
            payload["targetActionId"] = self._ensure_18(target_action_id)
        if ai_model is not None:
            payload["aiModel"] = ai_model
        if recommendation_mode is not None:
            payload["recommendationMode"] = recommendation_mode
        if recommendation_score is not None:
            payload["recommendationScore"] = recommendation_score
        return await self._post(
            "recommendation-strategies/reactions", json=payload
        )

    # ------------------------------------------------------------------
    # Single reaction
    # ------------------------------------------------------------------

    async def get_reaction(self, reaction_id: str) -> dict[str, Any]:
        """Get a single recommendation reaction (v45.0+).

        Args:
            reaction_id: 15- or 18-char reaction ID.

        Returns:
            Recommendation Reaction dict.
        """
        reaction_id = self._ensure_18(reaction_id)
        return await self._get(
            f"recommendation-strategies/reactions/{reaction_id}"
        )

    async def delete_reaction(self, reaction_id: str) -> dict[str, Any]:
        """Delete a recommendation reaction (v45.0+).

        Args:
            reaction_id: 15- or 18-char reaction ID.

        Returns:
            Empty dict on success.
        """
        reaction_id = self._ensure_18(reaction_id)
        return await self._delete(
            f"recommendation-strategies/reactions/{reaction_id}"
        )
