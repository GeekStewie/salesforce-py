"""Machine Learning Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class MachineLearningOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/machine-learning/*`` endpoints."""

    # ------------------------------------------------------------------
    # Alerts
    # ------------------------------------------------------------------

    async def create_alert(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a data alert."""
        return await self._post("machine-learning/alerts", json=data)

    async def update_alert(self, alert_id: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update a data alert."""
        return await self._patch(f"machine-learning/alerts/{alert_id}", json=data)

    # ------------------------------------------------------------------
    # Configured models
    # ------------------------------------------------------------------

    async def get_configured_models(
        self,
        *,
        asset_id_or_name: str | None = None,
        asset_type: str | None = None,
        capabilities: str | None = None,
        connector_type: str | None = None,
        limit: int | None = None,
        model_type: str | None = None,
        offset: int | None = None,
        out_of_the_box: bool | None = None,
        search: str | None = None,
        source_type: str | None = None,
    ) -> dict[str, Any]:
        """List configured models."""
        return await self._get(
            "machine-learning/configured-models",
            params={
                "assetIdOrName": asset_id_or_name,
                "assetType": asset_type,
                "capabilities": capabilities,
                "connectorType": connector_type,
                "limit": limit,
                "modelType": model_type,
                "offset": offset,
                "outOfTheBox": out_of_the_box,
                "search": search,
                "sourceType": source_type,
            },
        )

    async def get_configured_model(
        self,
        configured_model_id_or_name: str,
        *,
        filter_group: str | None = None,
    ) -> dict[str, Any]:
        """Get a configured model."""
        return await self._get(
            f"machine-learning/configured-models/{configured_model_id_or_name}",
            params={"filterGroup": filter_group},
        )

    async def update_configured_model(
        self, configured_model_id_or_name: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a configured model."""
        return await self._patch(
            f"machine-learning/configured-models/{configured_model_id_or_name}", json=data
        )

    async def delete_configured_model(self, configured_model_id_or_name: str) -> dict[str, Any]:
        """Delete a configured model."""
        return await self._delete(
            f"machine-learning/configured-models/{configured_model_id_or_name}"
        )

    # ------------------------------------------------------------------
    # Model artifacts
    # ------------------------------------------------------------------

    async def get_model_artifacts(
        self,
        *,
        limit: int | None = None,
        model_type: str | None = None,
        offset: int | None = None,
        source_type: str | None = None,
    ) -> dict[str, Any]:
        """List model artifacts."""
        return await self._get(
            "machine-learning/model-artifacts",
            params={
                "limit": limit,
                "modelType": model_type,
                "offset": offset,
                "sourceType": source_type,
            },
        )

    async def get_model_artifact(self, model_artifact_id_or_name: str) -> dict[str, Any]:
        """Get a model artifact."""
        return await self._get(f"machine-learning/model-artifacts/{model_artifact_id_or_name}")

    async def update_model_artifact(
        self, model_artifact_id_or_name: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a model artifact."""
        return await self._patch(
            f"machine-learning/model-artifacts/{model_artifact_id_or_name}", json=data
        )

    async def delete_model_artifact(self, model_artifact_id_or_name: str) -> dict[str, Any]:
        """Delete a model artifact."""
        return await self._delete(f"machine-learning/model-artifacts/{model_artifact_id_or_name}")

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    async def predict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Get a prediction."""
        return await self._post("machine-learning/predict", json=data)

    # ------------------------------------------------------------------
    # Model setup versions / partitions
    # ------------------------------------------------------------------

    async def get_model_setup_versions(
        self,
        model_setup_id_or_name: str,
        *,
        active: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """List model setup versions."""
        return await self._get(
            f"machine-learning/model-setups/{model_setup_id_or_name}/setup-versions",
            params={"active": active, "limit": limit, "offset": offset},
        )

    async def create_model_setup_version(
        self, model_setup_id_or_name: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a model setup version."""
        return await self._post(
            f"machine-learning/model-setups/{model_setup_id_or_name}/setup-versions",
            json=data,
        )

    async def get_model_setup_version(
        self, model_setup_id_or_name: str, model_setup_version_id: str
    ) -> dict[str, Any]:
        """Get a model setup version."""
        return await self._get(
            f"machine-learning/model-setups/{model_setup_id_or_name}"
            f"/setup-versions/{model_setup_version_id}"
        )

    async def update_model_setup_version(
        self,
        model_setup_id_or_name: str,
        model_setup_version_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update a model setup version."""
        return await self._patch(
            f"machine-learning/model-setups/{model_setup_id_or_name}"
            f"/setup-versions/{model_setup_version_id}",
            json=data,
        )

    async def get_model_setup_version_partitions(
        self, model_setup_id_or_name: str, model_setup_version_id: str
    ) -> dict[str, Any]:
        """List partitions on a model setup version."""
        return await self._get(
            f"machine-learning/model-setups/{model_setup_id_or_name}"
            f"/setup-versions/{model_setup_version_id}/partitions"
        )

    async def get_model_setup_version_partition(
        self,
        model_setup_id_or_name: str,
        model_setup_version_id: str,
        model_setup_partition_id: str,
    ) -> dict[str, Any]:
        """Get a single partition on a model setup version."""
        return await self._get(
            f"machine-learning/model-setups/{model_setup_id_or_name}"
            f"/setup-versions/{model_setup_version_id}"
            f"/partitions/{model_setup_partition_id}"
        )
