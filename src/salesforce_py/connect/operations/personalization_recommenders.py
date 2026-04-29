"""Personalization Recommenders Connect API operations.

Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
prefix) — the client supplies a dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class PersonalizationRecommendersOperations(ConnectBaseOperations):
    """Wrapper for ``/personalization/personalization-recommenders/...``
    endpoints (v63.0+/v64.0+/v65.0+).
    """

    async def list_recommenders(
        self,
        *,
        data_space_id_or_name: str | None = None,
        profile_data_graph_id_or_name: str | None = None,
    ) -> dict[str, Any]:
        """Get a list of personalization recommenders (v64.0+).

        Args:
            data_space_id_or_name: Filter by data space ID/name.
            profile_data_graph_id_or_name: Filter by profile data graph
                ID/name.

        Returns:
            Personalization Recommender Collection dict.
        """
        params: dict[str, Any] = {}
        if data_space_id_or_name is not None:
            params["dataSpaceIdOrName"] = data_space_id_or_name
        if profile_data_graph_id_or_name is not None:
            params["profileDataGraphIdOrName"] = profile_data_graph_id_or_name
        return await self._get(
            "personalization/personalization-recommenders", params=params
        )

    async def create_recommender(
        self, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a personalization recommender (v64.0+).

        Args:
            body: Personalization Recommender Input payload.

        Returns:
            Personalization Recommender dict.
        """
        return await self._post(
            "personalization/personalization-recommenders", json=body
        )

    async def get_recommender(self, id_or_name: str) -> dict[str, Any]:
        """Get a personalization recommender (v64.0+).

        Args:
            id_or_name: ID or API name of the recommender.

        Returns:
            Personalization Recommender dict.
        """
        return await self._get(
            f"personalization/personalization-recommenders/{id_or_name}"
        )

    async def update_recommender(
        self, id_or_name: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a personalization recommender (v65.0+).

        Args:
            id_or_name: ID or API name of the recommender.
            body: Personalization Recommender Patch Input payload.

        Returns:
            Personalization Recommender dict.
        """
        return await self._patch(
            f"personalization/personalization-recommenders/{id_or_name}",
            json=body,
        )

    async def delete_recommender(self, id_or_name: str) -> dict[str, Any]:
        """Delete a personalization recommender (v64.0+).

        Args:
            id_or_name: ID or API name of the recommender.

        Returns:
            Empty dict on success.
        """
        return await self._delete(
            f"personalization/personalization-recommenders/{id_or_name}"
        )

    async def list_recommender_jobs(
        self, id_or_name: str
    ) -> dict[str, Any]:
        """Get jobs associated with a recommender (v63.0+).

        Args:
            id_or_name: ID or API name of the recommender.

        Returns:
            Personalization Recommender Job Collection dict.
        """
        return await self._get(
            f"personalization/personalization-recommenders/{id_or_name}/jobs"
        )
