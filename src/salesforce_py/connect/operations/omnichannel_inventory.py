"""Salesforce Omnichannel Inventory (OCI) operations.

Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
prefix) — the client supplies a dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class OmnichannelInventoryOperations(ConnectBaseOperations):
    """Wrapper for ``/commerce/oci/...`` and ``/commerce/inventory/...`` endpoints."""

    async def batch_update_availability(self, body: dict[str, Any]) -> dict[str, Any]:
        """Update a batch of inventory records in Omnichannel Inventory (v62.0+).

        Args:
            body: OCI Batch Update Input payload.
        """
        return await self._post("commerce/oci/availability-records/actions/batch-update", json=body)

    async def get_availability(self, body: dict[str, Any]) -> dict[str, Any]:
        """Retrieve inventory availability data for products (v51.0+).

        Args:
            body: OCI Get Inventory Availability Input payload.
        """
        return await self._post(
            "commerce/oci/availability/availability-records/actions/get-availability",
            json=body,
        )

    async def upload_availability(self, files: dict[str, Any]) -> dict[str, Any]:
        """Asynchronously upload an inventory availability data file.

        Args:
            files: Multipart form data containing the ``fileUpload`` NDJSON/CSV file.
        """
        return await self._post("commerce/oci/availability-records/uploads", files=files)

    async def get_availability_upload_status(self, upload_id: str) -> dict[str, Any]:
        """Retrieve the status of an inventory availability upload job."""
        return await self._get(f"commerce/oci/availability-records/uploads/{upload_id}")

    async def check_availability(self, body: dict[str, Any], *, scope: str) -> dict[str, Any]:
        """Check inventory availability for products in locations / groups (v60.0+).

        Args:
            body: OCI Inventory Check Availability Input payload.
            scope: Expression specifying the webstore ID, e.g.
                ``"webStoreId Eq '0ZExx000000123FGAQ'"``.
        """
        return await self._post(
            "commerce/inventory/check-availability",
            json=body,
            params={"scope": scope},
        )

    async def get_levels(
        self,
        *,
        scope: str,
        products: list[str],
        locations: list[str] | None = None,
        location_groups: list[str] | None = None,
    ) -> dict[str, Any]:
        """Get inventory levels for products in locations / groups (v60.0+).

        Args:
            scope: Webstore ID expression.
            products: List of product IDs or SKUs.
            locations: List of location IDs (required if ``location_groups`` unset).
            location_groups: List of location group IDs (required if ``locations`` unset).
        """
        params: dict[str, Any] = {"scope": scope, "products": products}
        if locations is not None:
            params["locations"] = locations
        if location_groups is not None:
            params["locationgroups"] = location_groups
        return await self._get("commerce/inventory/levels", params=params)

    async def upload_location_graph(self) -> dict[str, Any]:
        """Publish inventory location and location group data to OCI (v51.0+)."""
        return await self._post("commerce/oci/location-graph/uploads")

    async def get_location_graph_upload_status(self, upload_id: str) -> dict[str, Any]:
        """Retrieve the status of a publish location structure job."""
        return await self._get(f"commerce/oci/location-graph/uploads/{upload_id}")

    async def create_reservation(self, body: dict[str, Any]) -> dict[str, Any]:
        """Create an inventory reservation in Omnichannel Inventory (v51.0+)."""
        return await self._post("commerce/oci/reservation/actions/reservations", json=body)

    async def fulfill_reservation(self, body: dict[str, Any]) -> dict[str, Any]:
        """Fulfill one or more inventory reservations (v51.0+)."""
        return await self._post("commerce/oci/reservation/actions/fulfillments", json=body)

    async def release_reservation(self, body: dict[str, Any]) -> dict[str, Any]:
        """Release one or more existing inventory reservations (v51.0+)."""
        return await self._post("commerce/oci/reservation/actions/releases", json=body)

    async def transfer_reservation(self, body: dict[str, Any]) -> dict[str, Any]:
        """Transfer one or more inventory reservations between locations (v51.0+)."""
        return await self._post("commerce/oci/reservation/actions/transfers", json=body)

    async def update_reservation(self, body: dict[str, Any]) -> dict[str, Any]:
        """Update an existing reservation in Omnichannel Inventory (v61.0+)."""
        return await self._post("commerce/oci/reservation/actions/update", json=body)
