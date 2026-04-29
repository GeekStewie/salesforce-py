"""Personalization Engagement Signals Connect API operations.

Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
prefix) — the client supplies a dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class PersonalizationEngagementSignalsOperations(ConnectBaseOperations):
    """Wrapper for ``/personalization/engagement-signals/...`` and
    ``/personalization/compound-metrics/...`` endpoints (v63.0+)."""

    # ------------------------------------------------------------------
    # Engagement signals  /personalization/engagement-signals
    # ------------------------------------------------------------------

    async def list_engagement_signals(
        self,
        *,
        dataspace_name: str | None = None,
        profile_data_graph_name: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """Get a list of engagement signals (v63.0+).

        Args:
            dataspace_name: Data Space API name filter.
            profile_data_graph_name: Profile Data Graph API name filter.
            limit: Max items to return.
            offset: Items to skip.

        Returns:
            Engagement Signal Collection dict.
        """
        params: dict[str, Any] = {}
        if dataspace_name is not None:
            params["dataspaceName"] = dataspace_name
        if profile_data_graph_name is not None:
            params["profileDataGraphName"] = profile_data_graph_name
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return await self._get(
            "personalization/engagement-signals", params=params
        )

    async def create_engagement_signal(
        self, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Create an engagement signal (v63.0+).

        Args:
            body: Engagement Signal Input payload.

        Returns:
            Engagement Signal dict.
        """
        return await self._post(
            "personalization/engagement-signals", json=body
        )

    async def get_engagement_signal(
        self, id_or_name: str
    ) -> dict[str, Any]:
        """Get an engagement signal (v63.0+).

        Args:
            id_or_name: ID or API name of the engagement signal.

        Returns:
            Engagement Signal dict.
        """
        return await self._get(
            f"personalization/engagement-signals/{id_or_name}"
        )

    async def delete_engagement_signal(
        self, id_or_name: str
    ) -> dict[str, Any]:
        """Delete an engagement signal (v63.0+).

        Args:
            id_or_name: ID or API name of the engagement signal.

        Returns:
            Empty dict on success.
        """
        return await self._delete(
            f"personalization/engagement-signals/{id_or_name}"
        )

    # ------------------------------------------------------------------
    # Metrics  /personalization/engagement-signals/{id}/metrics
    # ------------------------------------------------------------------

    async def create_engagement_signal_metric(
        self, id_or_name: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Create an engagement signal metric (v64.0+).

        Args:
            id_or_name: ID or API name of the engagement signal.
            body: Engagement Signal Metric Input payload.

        Returns:
            Engagement Signal Metric dict.
        """
        return await self._post(
            f"personalization/engagement-signals/{id_or_name}/metrics",
            json=body,
        )

    async def delete_engagement_signal_metric(
        self, signal_id_or_name: str, metric_id_or_name: str
    ) -> dict[str, Any]:
        """Delete an engagement signal metric (v64.0+).

        Args:
            signal_id_or_name: ID or API name of the engagement signal.
            metric_id_or_name: ID or API name of the metric.

        Returns:
            Empty dict on success.
        """
        return await self._delete(
            f"personalization/engagement-signals/{signal_id_or_name}"
            f"/metrics/{metric_id_or_name}"
        )

    # ------------------------------------------------------------------
    # Compound metrics  /personalization/compound-metrics
    # ------------------------------------------------------------------

    async def create_compound_metric(
        self, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a compound metric (v64.0+).

        Args:
            body: Engagement Signal Compound Metric Input payload.

        Returns:
            Engagement Signal Compound Metric dict.
        """
        return await self._post(
            "personalization/compound-metrics", json=body
        )

    async def get_compound_metric(
        self, id_or_name: str
    ) -> dict[str, Any]:
        """Get a compound metric (v64.0+).

        Args:
            id_or_name: ID or API name of the compound metric.

        Returns:
            Engagement Signal Compound Metric dict.
        """
        return await self._get(
            f"personalization/compound-metrics/{id_or_name}"
        )

    async def delete_compound_metric(
        self, id_or_name: str
    ) -> dict[str, Any]:
        """Delete a compound metric (v64.0+).

        Args:
            id_or_name: ID or API name of the compound metric.

        Returns:
            Empty dict on success.
        """
        return await self._delete(
            f"personalization/compound-metrics/{id_or_name}"
        )
