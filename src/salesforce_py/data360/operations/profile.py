"""Profile Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class ProfileOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/profile/*`` endpoints."""

    async def get_profile_metadata(self) -> dict[str, Any]:
        """Get profile metadata."""
        return await self._get("profile/metadata")

    async def get_profile_dmo_metadata(self, data_model_name: str) -> dict[str, Any]:
        """Get profile DMO metadata."""
        return await self._get(f"profile/metadata/{data_model_name}")

    async def get_profile_dmo(
        self,
        data_model_name: str,
        filters: str,
        *,
        batch_size: int | None = None,
        fields: str | None = None,
        offset: int | None = None,
        orderby: str | None = None,
    ) -> dict[str, Any]:
        """Get a profile DMO by filter expression."""
        return await self._get(
            f"profile/{data_model_name}",
            params={
                "batchSize": batch_size,
                "fields": fields,
                "filters": filters,
                "offset": offset,
                "orderby": orderby,
            },
        )

    async def get_profile_dmo_by_id(
        self,
        data_model_name: str,
        id: str,
        *,
        batch_size: int | None = None,
        fields: str | None = None,
        filters: str | None = None,
        offset: int | None = None,
        orderby: str | None = None,
        search_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a profile DMO by ID and search key."""
        return await self._get(
            f"profile/{data_model_name}/{id}",
            params={
                "batchSize": batch_size,
                "fields": fields,
                "filters": filters,
                "offset": offset,
                "orderby": orderby,
                "searchKey": search_key,
            },
        )

    async def get_profile_dmo_with_calculated_insight(
        self,
        data_model_name: str,
        id: str,
        ci_name: str,
        *,
        batch_size: int | None = None,
        dimensions: str | None = None,
        fields: str | None = None,
        filters: str | None = None,
        measures: str | None = None,
        offset: int | None = None,
        orderby: str | None = None,
        search_key: str | None = None,
        time_granularity: str | None = None,
    ) -> dict[str, Any]:
        """Get a profile DMO joined with a calculated insight."""
        return await self._get(
            f"profile/{data_model_name}/{id}/calculated-insights/{ci_name}",
            params={
                "batchSize": batch_size,
                "dimensions": dimensions,
                "fields": fields,
                "filters": filters,
                "measures": measures,
                "offset": offset,
                "orderby": orderby,
                "searchKey": search_key,
                "timeGranularity": time_granularity,
            },
        )

    async def get_profile_dmo_child(
        self,
        data_model_name: str,
        id: str,
        child_data_model_name: str,
        *,
        batch_size: int | None = None,
        fields: str | None = None,
        filters: str | None = None,
        offset: int | None = None,
        orderby: str | None = None,
        search_key: str | None = None,
    ) -> dict[str, Any]:
        """Get a profile DMO joined with a child DMO."""
        return await self._get(
            f"profile/{data_model_name}/{id}/{child_data_model_name}",
            params={
                "batchSize": batch_size,
                "fields": fields,
                "filters": filters,
                "offset": offset,
                "orderby": orderby,
                "searchKey": search_key,
            },
        )
