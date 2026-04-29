"""Metadata Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class MetadataOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/metadata*`` and related metadata discovery endpoints.

    Note:
        The ``Metadata`` tag in the OpenAPI spec is a cross-cutting group that
        also references ``/ssot/connectors/{connectorType}``, ``/ssot/data-graphs/metadata``,
        ``/ssot/insight/metadata``, and ``/ssot/profile/metadata``. Those
        endpoints are exposed on their dedicated namespaces
        (:class:`ConnectorsOperations`, :class:`DataGraphsOperations`,
        :class:`InsightsOperations`, :class:`ProfileOperations`) — this class
        only owns the generic ``/ssot/metadata`` and ``/ssot/metadata-entities``
        endpoints to avoid duplication.
    """

    async def get_metadata(
        self,
        *,
        dataspace: str | None = None,
        entity_category: str | None = None,
        entity_name: str | None = None,
        entity_type: str | None = None,
    ) -> dict[str, Any]:
        """Get metadata for Data 360 entities."""
        return await self._get(
            "metadata",
            params={
                "dataspace": dataspace,
                "entityCategory": entity_category,
                "entityName": entity_name,
                "entityType": entity_type,
            },
        )

    async def get_metadata_entities(
        self,
        *,
        dataspace: str | None = None,
        entity_category: str | None = None,
        entity_type: str | None = None,
    ) -> dict[str, Any]:
        """List metadata entities."""
        return await self._get(
            "metadata-entities",
            params={
                "dataspace": dataspace,
                "entityCategory": entity_category,
                "entityType": entity_type,
            },
        )
