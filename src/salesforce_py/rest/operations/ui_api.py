"""UI API — ``/services/data/vXX.X/ui-api`` pass-through helpers.

The full UI API surface (record layouts, list UIs, theming, favorites,
record defaults, duplicates, etc.) is documented in the User Interface
API Developer Guide. This wrapper covers the most common endpoints and
exposes generic verbs for everything else.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.rest.base import RestBaseOperations


class UIAPIOperations(RestBaseOperations):
    """Pass-through wrapper for ``/ui-api``."""

    # ------------------------------------------------------------------
    # Common convenience helpers
    # ------------------------------------------------------------------

    async def get_record(
        self,
        record_id: str,
        *,
        fields: list[str] | None = None,
        layout_types: list[str] | None = None,
        modes: list[str] | None = None,
    ) -> dict[str, Any]:
        """Return a record with its UI-ready field metadata."""
        return await self._get(
            f"ui-api/records/{record_id}",
            params={
                "fields": ",".join(fields) if fields else None,
                "layoutTypes": ",".join(layout_types) if layout_types else None,
                "modes": ",".join(modes) if modes else None,
            },
        )

    async def get_record_ui(
        self,
        record_ids: list[str],
        *,
        layout_types: list[str] | None = None,
        modes: list[str] | None = None,
        optional_fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Return record UI metadata for one or more records."""
        return await self._get(
            f"ui-api/record-ui/{','.join(record_ids)}",
            params={
                "layoutTypes": ",".join(layout_types) if layout_types else None,
                "modes": ",".join(modes) if modes else None,
                "optionalFields": ",".join(optional_fields)
                if optional_fields
                else None,
            },
        )

    async def get_record_defaults_create(
        self,
        object_name: str,
        *,
        record_type_id: str | None = None,
        form_factor: str | None = None,
    ) -> dict[str, Any]:
        """Return the default field values for creating a record."""
        return await self._get(
            f"ui-api/record-defaults/create/{object_name}",
            params={"recordTypeId": record_type_id, "formFactor": form_factor},
        )

    async def get_record_defaults_clone(
        self,
        record_id: str,
        *,
        form_factor: str | None = None,
        record_type_id: str | None = None,
    ) -> dict[str, Any]:
        """Return the default field values for cloning a record."""
        return await self._get(
            f"ui-api/record-defaults/clone/{record_id}",
            params={"formFactor": form_factor, "recordTypeId": record_type_id},
        )

    async def get_layout(
        self,
        object_name: str,
        *,
        record_type_id: str | None = None,
        layout_type: str | None = None,
        mode: str | None = None,
    ) -> dict[str, Any]:
        """Return an object's UI-API layout metadata."""
        return await self._get(
            f"ui-api/layout/{object_name}",
            params={
                "recordTypeId": record_type_id,
                "layoutType": layout_type,
                "mode": mode,
            },
        )

    async def get_object_info(self, object_name: str) -> dict[str, Any]:
        """Return UI-API object info (fields, record types, etc.)."""
        return await self._get(f"ui-api/object-info/{object_name}")

    async def get_picklist_values(
        self, object_name: str, record_type_id: str, field_name: str
    ) -> dict[str, Any]:
        """Return picklist values for a field within a record type."""
        return await self._get(
            f"ui-api/object-info/{object_name}/picklist-values/{record_type_id}/{field_name}"
        )

    # ------------------------------------------------------------------
    # Generic passthrough
    # ------------------------------------------------------------------

    async def get(
        self, subpath: str, *, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Issue a GET against ``/ui-api/{subpath}``."""
        return await self._get(f"ui-api/{subpath.lstrip('/')}", params=params)

    async def post(
        self,
        subpath: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Issue a POST against ``/ui-api/{subpath}``."""
        return await self._post(
            f"ui-api/{subpath.lstrip('/')}", json=json, params=params
        )

    async def patch(
        self,
        subpath: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Issue a PATCH against ``/ui-api/{subpath}``."""
        return await self._patch(
            f"ui-api/{subpath.lstrip('/')}", json=json, params=params
        )

    async def put(
        self,
        subpath: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Issue a PUT against ``/ui-api/{subpath}``."""
        return await self._put(
            f"ui-api/{subpath.lstrip('/')}", json=json, params=params
        )

    async def delete(
        self, subpath: str, *, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Issue a DELETE against ``/ui-api/{subpath}``."""
        return await self._delete(
            f"ui-api/{subpath.lstrip('/')}", params=params
        )
