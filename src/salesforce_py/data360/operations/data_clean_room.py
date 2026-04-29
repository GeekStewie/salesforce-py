"""Data Clean Room Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class DataCleanRoomOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/data-clean-room/*`` endpoints."""

    # ------------------------------------------------------------------
    # Collaborations
    # ------------------------------------------------------------------

    async def get_collaborations(
        self,
        *,
        filters: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
    ) -> dict[str, Any]:
        """List data clean room collaborations."""
        return await self._get(
            "data-clean-room/collaborations",
            params={
                "filters": filters,
                "limit": limit,
                "offset": offset,
                "orderBy": order_by,
            },
        )

    async def create_collaboration(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a data clean room collaboration."""
        return await self._post("data-clean-room/collaborations", json=data)

    async def accept_collaboration_invitation(
        self, collaboration_id_or_api_name: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Accept a data clean room collaboration invitation."""
        return await self._put(
            f"data-clean-room/collaborations/{collaboration_id_or_api_name}/actions/accept-invitation",
            json=data or {},
        )

    async def reject_collaboration_invitation(
        self, collaboration_id_or_api_name: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Reject a data clean room collaboration invitation."""
        return await self._put(
            f"data-clean-room/collaborations/{collaboration_id_or_api_name}/actions/reject-invitation",
            json=data or {},
        )

    async def run_collaboration_query(
        self, collaboration_id_or_api_name: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Run a data clean room query."""
        return await self._post(
            f"data-clean-room/collaborations/{collaboration_id_or_api_name}/actions/run",
            json=data,
        )

    async def get_collaboration_jobs(
        self,
        collaboration_id_or_api_name: str,
        *,
        filters: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
    ) -> dict[str, Any]:
        """List query jobs on a collaboration."""
        return await self._get(
            f"data-clean-room/collaborations/{collaboration_id_or_api_name}/jobs",
            params={
                "filters": filters,
                "limit": limit,
                "offset": offset,
                "orderBy": order_by,
            },
        )

    # ------------------------------------------------------------------
    # Providers
    # ------------------------------------------------------------------

    async def get_providers(
        self,
        *,
        filters: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
    ) -> dict[str, Any]:
        """List data clean room providers."""
        return await self._get(
            "data-clean-room/providers",
            params={
                "filters": filters,
                "limit": limit,
                "offset": offset,
                "orderBy": order_by,
            },
        )

    async def create_provider(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a data clean room provider."""
        return await self._post("data-clean-room/providers", json=data)

    async def get_provider(self, provider_id_or_name: str) -> dict[str, Any]:
        """Get a data clean room provider."""
        return await self._get(f"data-clean-room/providers/{provider_id_or_name}")

    async def get_provider_templates(
        self,
        provider_id_or_name: str,
        *,
        filters: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
    ) -> dict[str, Any]:
        """List templates exposed by a provider."""
        return await self._get(
            f"data-clean-room/providers/{provider_id_or_name}/templates",
            params={
                "filters": filters,
                "limit": limit,
                "offset": offset,
                "orderBy": order_by,
            },
        )

    # ------------------------------------------------------------------
    # Specifications & templates
    # ------------------------------------------------------------------

    async def get_specifications(
        self,
        *,
        filters: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
    ) -> dict[str, Any]:
        """List clean room specifications."""
        return await self._get(
            "data-clean-room/specifications",
            params={
                "filters": filters,
                "limit": limit,
                "offset": offset,
                "orderBy": order_by,
            },
        )

    async def create_specification(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a clean room specification."""
        return await self._post("data-clean-room/specifications", json=data)

    async def get_templates(
        self,
        *,
        filters: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
    ) -> dict[str, Any]:
        """List clean room templates."""
        return await self._get(
            "data-clean-room/templates",
            params={
                "filters": filters,
                "limit": limit,
                "offset": offset,
                "orderBy": order_by,
            },
        )
