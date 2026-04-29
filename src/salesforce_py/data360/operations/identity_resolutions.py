"""Identity Resolutions Data 360 operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class IdentityResolutionsOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/identity-resolutions*`` endpoints."""

    async def get_identity_resolutions(self) -> dict[str, Any]:
        """List identity resolution rulesets."""
        return await self._get("identity-resolutions")

    async def create_identity_resolution(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create an identity resolution ruleset."""
        return await self._post("identity-resolutions", json=data)

    async def get_identity_resolution(self, identity_resolution: str) -> dict[str, Any]:
        """Get an identity resolution ruleset."""
        return await self._get(f"identity-resolutions/{identity_resolution}")

    async def update_identity_resolution(
        self, identity_resolution: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update an identity resolution ruleset."""
        return await self._patch(f"identity-resolutions/{identity_resolution}", json=data)

    async def delete_identity_resolution(self, identity_resolution: str) -> dict[str, Any]:
        """Delete an identity resolution ruleset."""
        return await self._delete(f"identity-resolutions/{identity_resolution}")

    async def run_identity_resolution_now(
        self, identity_resolution: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Run an identity resolution ruleset now."""
        return await self._post(
            f"identity-resolutions/{identity_resolution}/actions/run-now",
            json=data or {},
        )
