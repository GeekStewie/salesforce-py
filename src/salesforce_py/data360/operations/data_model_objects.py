"""Data Model Objects Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class DataModelObjectsOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/data-model-objects*`` and ``/ssot/data-model-object-mappings*``."""

    # ------------------------------------------------------------------
    # DMO CRUD
    # ------------------------------------------------------------------

    async def get_data_model_objects(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
    ) -> dict[str, Any]:
        """List data model objects."""
        return await self._get(
            "data-model-objects",
            params={"limit": limit, "offset": offset, "orderBy": order_by},
        )

    async def create_data_model_object(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a data model object."""
        return await self._post("data-model-objects", json=data)

    async def get_data_model_object(self, data_model_object_name: str) -> dict[str, Any]:
        """Get a data model object."""
        return await self._get(f"data-model-objects/{data_model_object_name}")

    async def update_data_model_object(
        self, data_model_object_name: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a data model object."""
        return await self._patch(f"data-model-objects/{data_model_object_name}", json=data)

    async def delete_data_model_object(self, data_model_object_name: str) -> dict[str, Any]:
        """Delete a data model object."""
        return await self._delete(f"data-model-objects/{data_model_object_name}")

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    async def get_field_source_target_relationships(
        self,
        data_model_object_name: str,
        *,
        creation_type: str | None = None,
        dataspace: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
        sort_by: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """List field source target relationships for a DMO."""
        return await self._get(
            f"data-model-objects/{data_model_object_name}/relationships",
            params={
                "creationType": creation_type,
                "dataspace": dataspace,
                "limit": limit,
                "offset": offset,
                "orderBy": order_by,
                "sortBy": sort_by,
                "status": status,
            },
        )

    async def create_field_source_target_relationships(
        self,
        data_model_object_name: str,
        data: dict[str, Any],
        *,
        dataspace: str | None = None,
    ) -> dict[str, Any]:
        """Create field source target relationships for a DMO."""
        return await self._post(
            f"data-model-objects/{data_model_object_name}/relationships",
            json=data,
            params={"dataspace": dataspace},
        )

    async def delete_field_source_target_relationship(
        self, name: str, *, dataspace: str | None = None
    ) -> dict[str, Any]:
        """Delete a field source target relationship."""
        return await self._delete(
            f"data-model-objects/relationships/{name}",
            params={"dataspace": dataspace},
        )

    # ------------------------------------------------------------------
    # Object mappings
    # ------------------------------------------------------------------

    async def get_data_model_object_mappings(
        self,
        dmo_developer_name: str,
        *,
        dataspace: str | None = None,
        dlo_developer_name: str | None = None,
    ) -> dict[str, Any]:
        """List data model object mappings."""
        return await self._get(
            "data-model-object-mappings",
            params={
                "dataspace": dataspace,
                "dloDeveloperName": dlo_developer_name,
                "dmoDeveloperName": dmo_developer_name,
            },
        )

    async def create_data_model_object_mapping(
        self, data: dict[str, Any], *, dataspace: str
    ) -> dict[str, Any]:
        """Create a data model object mapping."""
        return await self._post(
            "data-model-object-mappings", json=data, params={"dataspace": dataspace}
        )

    async def get_data_model_object_mapping(
        self, object_source_target_map_developer_name: str
    ) -> dict[str, Any]:
        """Get a data model object mapping."""
        return await self._get(
            f"data-model-object-mappings/{object_source_target_map_developer_name}"
        )

    async def delete_data_model_object_mapping(
        self, object_source_target_map_developer_name: str
    ) -> dict[str, Any]:
        """Delete a data model object mapping."""
        return await self._delete(
            f"data-model-object-mappings/{object_source_target_map_developer_name}"
        )

    async def delete_data_model_object_field_mappings(
        self,
        object_source_target_map_developer_name: str,
        *,
        dataspace: str | None = None,
    ) -> dict[str, Any]:
        """Delete all field mappings on an object source target map."""
        return await self._delete(
            f"data-model-object-mappings/{object_source_target_map_developer_name}/field-mappings",
            params={"dataspace": dataspace},
        )

    async def update_data_model_object_field_mapping(
        self,
        object_source_target_map_developer_name: str,
        field_source_target_map_developer_name: str,
        data: dict[str, Any],
        *,
        dataspace: str | None = None,
    ) -> dict[str, Any]:
        """Update a single field mapping on an object source target map."""
        return await self._patch(
            f"data-model-object-mappings/{object_source_target_map_developer_name}"
            f"/field-mappings/{field_source_target_map_developer_name}",
            json=data,
            params={"dataspace": dataspace},
        )

    async def get_data_model_object_relationship(self, name: str) -> dict[str, Any]:
        """Get a data model object relationship by name."""
        return await self._get(f"data-model-objects/relationships/{name}")
