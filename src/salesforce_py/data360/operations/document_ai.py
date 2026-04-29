"""Document AI Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class DocumentAIOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/document-processing*`` endpoints."""

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    async def extract_data(
        self,
        data: dict[str, Any],
        *,
        start_page: int | None = None,
        end_page: int | None = None,
        extract_data_with_confidence_score: bool | None = None,
    ) -> dict[str, Any]:
        """Extract data from a document using a Document AI configuration."""
        return await self._post(
            "document-processing/actions/extract-data",
            json=data,
            params={
                "endPage": end_page,
                "extractDataWithConfidenceScore": extract_data_with_confidence_score,
                "startPage": start_page,
            },
        )

    async def generate_schema(self, data: dict[str, Any]) -> dict[str, Any]:
        """Generate a Document AI schema from sample content."""
        return await self._post("document-processing/actions/generate-schema", json=data)

    # ------------------------------------------------------------------
    # Configurations
    # ------------------------------------------------------------------

    async def get_configurations(
        self,
        *,
        activation_status: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        """List Document AI configurations."""
        return await self._get(
            "document-processing/configurations",
            params={
                "activationStatus": activation_status,
                "limit": limit,
                "offset": offset,
                "orderBy": order_by,
                "search": search,
            },
        )

    async def create_configuration(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a Document AI configuration."""
        return await self._post("document-processing/configurations", json=data)

    async def get_configuration(self, id_or_api_name: str) -> dict[str, Any]:
        """Get a Document AI configuration."""
        return await self._get(f"document-processing/configurations/{id_or_api_name}")

    async def update_configuration(
        self, id_or_api_name: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a Document AI configuration."""
        return await self._patch(f"document-processing/configurations/{id_or_api_name}", json=data)

    async def delete_configuration(self, id_or_api_name: str) -> dict[str, Any]:
        """Delete a Document AI configuration."""
        return await self._delete(f"document-processing/configurations/{id_or_api_name}")

    async def run_configuration(self, id_or_api_name: str) -> dict[str, Any]:
        """Run a Document AI configuration."""
        return await self._post(f"document-processing/configurations/{id_or_api_name}/actions/run")

    async def get_global_config(self) -> dict[str, Any]:
        """Get the Document AI global configuration."""
        return await self._get("document-processing/global-config")
