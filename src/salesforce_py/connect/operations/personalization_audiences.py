"""Personalization Audiences & Targets Connect API operations (v47.0+).

All endpoints are community-scoped under
``/connect/communities/{communityId}/personalization/...``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class PersonalizationAudiencesOperations(ConnectBaseOperations):
    """Wrapper for Personalization Audiences & Targets endpoints.

    Covers listing/creating/updating/deleting audiences and targets, plus
    batch lookups by comma-separated ID lists.
    """

    # ------------------------------------------------------------------
    # Audiences collection
    # ------------------------------------------------------------------

    async def list_audiences(
        self,
        community_id: str,
        *,
        domain: str | None = None,
        include_audience_criteria: bool | None = None,
        ip_address: str | None = None,
        publish_status: str | None = None,
        record_id: str | None = None,
        target_types: list[str] | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Get assigned audiences matching the user context (v47.0+).

        Args:
            community_id: Experience Cloud site ID.
            domain: User's Salesforce custom domain name.
            include_audience_criteria: Include audience criteria in results.
            ip_address: User IP address.
            publish_status: ``"Draft"`` or ``"Live"``. Default ``"Live"``.
            record_id: Record ID for field-based criteria (v51.0+).
            target_types: Target type filter (e.g. ``["ExperienceVariation"]``).
            user_id: User ID. Defaults to context user.

        Returns:
            Audience Collection dict.
        """
        community_id = self._ensure_18(community_id)
        params: dict[str, Any] = {}
        if domain is not None:
            params["domain"] = domain
        if include_audience_criteria is not None:
            params["includeAudienceCriteria"] = str(include_audience_criteria).lower()
        if ip_address is not None:
            params["ipAddress"] = ip_address
        if publish_status is not None:
            params["publishStatus"] = publish_status
        if record_id is not None:
            params["recordId"] = self._ensure_18(record_id)
        if target_types is not None:
            params["targetTypes"] = ",".join(target_types)
        if user_id is not None:
            params["userId"] = self._ensure_18(user_id)
        return await self._get(
            f"communities/{community_id}/personalization/audiences",
            params=params,
        )

    async def create_audience(
        self,
        community_id: str,
        *,
        name: str,
        criteria: list[dict[str, Any]],
        formula_filter_type: str,
        custom_formula: str | None = None,
    ) -> dict[str, Any]:
        """Create an audience (v47.0+).

        Args:
            community_id: Experience Cloud site ID.
            name: Audience name.
            criteria: Audience criterion list (up to 100).
            formula_filter_type: ``"AllCriteriaMatch"``,
                ``"AnyCriterionMatches"``, or ``"CustomLogicMatches"``.
            custom_formula: Required when ``formula_filter_type`` is
                ``"CustomLogicMatches"`` (e.g. ``"(1 AND 2) OR 3"``).

        Returns:
            Audience dict.
        """
        community_id = self._ensure_18(community_id)
        payload: dict[str, Any] = {
            "name": name,
            "criteria": criteria,
            "formulaFilterType": formula_filter_type,
        }
        if custom_formula is not None:
            payload["customFormula"] = custom_formula
        return await self._post(
            f"communities/{community_id}/personalization/audiences",
            json=payload,
        )

    async def get_audiences_batch(
        self, community_id: str, audience_ids: list[str]
    ) -> dict[str, Any]:
        """Get audience information for a batch of audience IDs (v48.0+).

        Args:
            community_id: Experience Cloud site ID.
            audience_ids: List of audience IDs.

        Returns:
            Batch Results dict.
        """
        community_id = self._ensure_18(community_id)
        ids = ",".join(self._ensure_18_list(audience_ids))
        return await self._get(f"communities/{community_id}/personalization/audiences/batch/{ids}")

    # ------------------------------------------------------------------
    # Single audience
    # ------------------------------------------------------------------

    async def get_audience(
        self,
        community_id: str,
        audience_id: str,
        *,
        include_audience_criteria: bool | None = None,
    ) -> dict[str, Any]:
        """Get an audience (v47.0+).

        Args:
            community_id: Experience Cloud site ID.
            audience_id: Audience ID.
            include_audience_criteria: Include audience criteria.

        Returns:
            Audience dict.
        """
        community_id = self._ensure_18(community_id)
        audience_id = self._ensure_18(audience_id)
        params: dict[str, Any] = {}
        if include_audience_criteria is not None:
            params["includeAudienceCriteria"] = str(include_audience_criteria).lower()
        return await self._get(
            f"communities/{community_id}/personalization/audiences/{audience_id}",
            params=params,
        )

    async def update_audience(
        self,
        community_id: str,
        audience_id: str,
        *,
        name: str | None = None,
        criteria: list[dict[str, Any]] | None = None,
        formula_filter_type: str | None = None,
        custom_formula: str | None = None,
    ) -> dict[str, Any]:
        """Update an audience (v47.0+).

        Args:
            community_id: Experience Cloud site ID.
            audience_id: Audience ID.
            name: Updated audience name.
            criteria: Updated audience criteria (up to 100).
            formula_filter_type: Updated formula filter type.
            custom_formula: Updated custom formula string.

        Returns:
            Audience dict.
        """
        community_id = self._ensure_18(community_id)
        audience_id = self._ensure_18(audience_id)
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if criteria is not None:
            payload["criteria"] = criteria
        if formula_filter_type is not None:
            payload["formulaFilterType"] = formula_filter_type
        if custom_formula is not None:
            payload["customFormula"] = custom_formula
        return await self._patch(
            f"communities/{community_id}/personalization/audiences/{audience_id}",
            json=payload,
        )

    async def delete_audience(self, community_id: str, audience_id: str) -> dict[str, Any]:
        """Delete an audience (v47.0+).

        Args:
            community_id: Experience Cloud site ID.
            audience_id: Audience ID.

        Returns:
            Empty dict on success.
        """
        community_id = self._ensure_18(community_id)
        audience_id = self._ensure_18(audience_id)
        return await self._delete(
            f"communities/{community_id}/personalization/audiences/{audience_id}"
        )

    # ------------------------------------------------------------------
    # Targets collection
    # ------------------------------------------------------------------

    async def list_targets(
        self,
        community_id: str,
        *,
        domain: str | None = None,
        group_names: list[str] | None = None,
        include_all_matching_targets_within_group: bool | None = None,
        include_audience: bool | None = None,
        ip_address: str | None = None,
        publish_status: str | None = None,
        record_id: str | None = None,
        target_types: list[str] | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Get targets matching the user context (v47.0+).

        Args:
            community_id: Experience Cloud site ID.
            domain: User's Salesforce custom domain name.
            group_names: Comma-separated group names (v48.0+). Requires a
                single ``target_types`` value.
            include_all_matching_targets_within_group: Include all matching
                targets within a group (``True``) or only the top one.
            include_audience: Include matching audience details.
            ip_address: User IP address.
            publish_status: ``"Draft"`` or ``"Live"``. Default ``"Live"``.
            record_id: Record ID for field-based audience criteria.
            target_types: Target type filter. Required when ``group_names``
                is supplied.
            user_id: User ID. Defaults to context user.

        Returns:
            Target Collection dict.
        """
        community_id = self._ensure_18(community_id)
        params: dict[str, Any] = {}
        if domain is not None:
            params["domain"] = domain
        if group_names is not None:
            params["groupNames"] = ",".join(group_names)
        if include_all_matching_targets_within_group is not None:
            params["includeAllMatchingTargetsWithinGroup"] = str(
                include_all_matching_targets_within_group
            ).lower()
        if include_audience is not None:
            params["includeAudience"] = str(include_audience).lower()
        if ip_address is not None:
            params["ipAddress"] = ip_address
        if publish_status is not None:
            params["publishStatus"] = publish_status
        if record_id is not None:
            params["recordId"] = self._ensure_18(record_id)
        if target_types is not None:
            params["targetTypes"] = ",".join(target_types)
        if user_id is not None:
            params["userId"] = self._ensure_18(user_id)
        return await self._get(
            f"communities/{community_id}/personalization/targets",
            params=params,
        )

    async def create_targets(
        self, community_id: str, targets: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Create targets (v47.0+).

        Args:
            community_id: Experience Cloud site ID.
            targets: List of target inputs.

        Returns:
            Target Collection dict.
        """
        community_id = self._ensure_18(community_id)
        return await self._post(
            f"communities/{community_id}/personalization/targets",
            json={"targets": targets},
        )

    async def update_targets(
        self, community_id: str, targets: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Update targets (e.g. assign audiences) (v47.0+).

        Args:
            community_id: Experience Cloud site ID.
            targets: List of target update inputs.

        Returns:
            Target Collection dict.
        """
        community_id = self._ensure_18(community_id)
        return await self._patch(
            f"communities/{community_id}/personalization/targets",
            json={"targets": targets},
        )

    async def get_targets_batch(self, community_id: str, target_ids: list[str]) -> dict[str, Any]:
        """Get target information for a batch of target IDs (v47.0+).

        Args:
            community_id: Experience Cloud site ID.
            target_ids: List of target IDs.

        Returns:
            Batch Results dict.
        """
        community_id = self._ensure_18(community_id)
        ids = ",".join(self._ensure_18_list(target_ids))
        return await self._get(f"communities/{community_id}/personalization/targets/batch/{ids}")

    # ------------------------------------------------------------------
    # Single target
    # ------------------------------------------------------------------

    async def get_target(self, community_id: str, target_id: str) -> dict[str, Any]:
        """Get a target (v47.0+).

        Args:
            community_id: Experience Cloud site ID.
            target_id: Target ID.

        Returns:
            Target dict.
        """
        community_id = self._ensure_18(community_id)
        target_id = self._ensure_18(target_id)
        return await self._get(f"communities/{community_id}/personalization/targets/{target_id}")

    async def delete_target(self, community_id: str, target_id: str) -> dict[str, Any]:
        """Delete a target (v47.0+).

        Args:
            community_id: Experience Cloud site ID.
            target_id: Target ID.

        Returns:
            Empty dict on success.
        """
        community_id = self._ensure_18(community_id)
        target_id = self._ensure_18(target_id)
        return await self._delete(f"communities/{community_id}/personalization/targets/{target_id}")
