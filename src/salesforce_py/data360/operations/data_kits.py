"""Data Kits Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class DataKitsOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/data-kits*`` endpoints."""

    async def get_data_kits(self, *, namespace: str | None = None) -> dict[str, Any]:
        """List data kits."""
        return await self._get("data-kits", params={"namespace": namespace})

    async def create_data_kit(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a data kit."""
        return await self._post("data-kits", json=data)

    async def get_available_components(
        self,
        *,
        component_type: str | None = None,
        data_kit_dev_name: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """List available data kit components."""
        return await self._get(
            "data-kits/available-components",
            params={
                "componentType": component_type,
                "dataKitDevName": data_kit_dev_name,
                "limit": limit,
                "offset": offset,
            },
        )

    async def delete_data_kit(self, data_kit_dev_name: str) -> dict[str, Any]:
        """Delete a data kit."""
        return await self._delete(f"data-kits/{data_kit_dev_name}")

    async def update_data_kit_components(
        self, data_kit_dev_name: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update components on a data kit."""
        return await self._patch(f"data-kits/{data_kit_dev_name}", json=data)

    async def deploy_data_kit(
        self,
        data_kit_dev_name: str,
        data: dict[str, Any],
        *,
        async_mode: bool,
        dataspace: str | None = None,
    ) -> dict[str, Any]:
        """Deploy data kit components."""
        return await self._post(
            f"data-kits/{data_kit_dev_name}",
            json=data,
            params={"asyncMode": async_mode, "dataspace": dataspace},
        )

    async def undeploy_data_kit(
        self,
        data_kit_name: str,
        data: dict[str, Any],
        *,
        async_mode: bool,
        dataspace: str | None = None,
    ) -> dict[str, Any]:
        """Undeploy a data kit component."""
        return await self._post(
            f"data-kits/{data_kit_name}/undeploy",
            json=data,
            params={"asyncMode": async_mode, "dataspace": dataspace},
        )

    async def get_component_dependencies(
        self,
        data_kit_name: str,
        component_name: str,
        *,
        component_type: str,
        dataspace: str | None = None,
    ) -> dict[str, Any]:
        """Get dependencies for a data kit component."""
        return await self._get(
            f"data-kits/{data_kit_name}/components/{component_name}/dependencies",
            params={"componentType": component_type, "dataspace": dataspace},
        )

    async def get_component_status(self, data_kit_name: str, component_name: str) -> dict[str, Any]:
        """Get deployment status for a data kit component."""
        return await self._get(
            f"data-kits/{data_kit_name}/components/{component_name}/deployment-status"
        )

    async def get_data_kit_manifest(self, data_kit_dev_name: str) -> dict[str, Any]:
        """Get a data kit manifest (note: uses ``/datakit/`` path)."""
        return await self._get(f"datakit/{data_kit_dev_name}/manifest")
