"""Universal ID Lookup Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class UniversalIdLookupOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/universalIdLookup/*`` endpoints."""

    async def lookup_universal_id(
        self,
        entity_name: str,
        data_source_id: str,
        data_source_object_id: str,
        source_record_id: str,
    ) -> dict[str, Any]:
        """Look up the universal (unified) ID for a source record.

        Args:
            entity_name: Unified entity API name.
            data_source_id: ID of the data source.
            data_source_object_id: ID of the data source object.
            source_record_id: The record's native ID in the source system.
        """
        return await self._get(
            f"universalIdLookup/{entity_name}/{data_source_id}"
            f"/{data_source_object_id}/{source_record_id}"
        )
