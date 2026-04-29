"""Personalization Experimentation Connect API operations (v65.0+).

Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
prefix) — the client supplies a dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class PersonalizationExperimentsOperations(ConnectBaseOperations):
    """Wrapper for ``/personalization/abn-experiments/...`` endpoints."""

    async def create_experiment(
        self,
        body: dict[str, Any],
        *,
        action: str | None = None,
    ) -> dict[str, Any]:
        """Create a personalization experiment (v65.0+).

        Args:
            body: Personalization Experiment Input payload.
            action: Optional action enum — e.g. ``"Start"``, ``"Stop"``,
                or ``"Archive"``.

        Returns:
            Personalization Experiment dict.
        """
        params: dict[str, Any] = {}
        if action is not None:
            params["action"] = action
        return await self._post(
            "personalization/abn-experiments", json=body, params=params
        )

    async def get_experiment(self, id_or_name: str) -> dict[str, Any]:
        """Get a personalization experiment (v65.0+).

        Args:
            id_or_name: ID or API name of the experiment.

        Returns:
            Personalization Experiment dict.
        """
        return await self._get(
            f"personalization/abn-experiments/{id_or_name}"
        )

    async def update_experiment(
        self,
        id_or_name: str,
        body: dict[str, Any],
        *,
        action: str | None = None,
    ) -> dict[str, Any]:
        """Update a personalization experiment (v65.0+).

        Args:
            id_or_name: ID or API name of the experiment.
            body: Personalization Experiment Input payload.
            action: Optional action enum.

        Returns:
            Personalization Experiment dict.
        """
        params: dict[str, Any] = {}
        if action is not None:
            params["action"] = action
        return await self._patch(
            f"personalization/abn-experiments/{id_or_name}",
            json=body,
            params=params,
        )

    async def delete_experiment(self, id_or_name: str) -> dict[str, Any]:
        """Delete a personalization experiment (v65.0+).

        Args:
            id_or_name: ID or API name of the experiment.

        Returns:
            Empty dict on success (HTTP 202).
        """
        return await self._delete(
            f"personalization/abn-experiments/{id_or_name}"
        )
