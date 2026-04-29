"""Commerce My Profile operations (shopper-facing buyer profile).

Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
prefix) — the client supplies a dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class CommerceMyProfileOperations(ConnectBaseOperations):
    """Wrapper for ``/commerce/webstores/{id}/myprofile/...`` endpoints."""

    def _base(self, webstore_id: str) -> str:
        return (
            f"commerce/webstores/{self._ensure_18(webstore_id)}/myprofile"
        )

    async def get_profile(self, webstore_id: str) -> dict[str, Any]:
        """Retrieve the buyer's account details."""
        return await self._get(self._base(webstore_id))

    async def update_profile(
        self, webstore_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Update buyer account details.

        Args:
            body: Buyer Profile Input payload.
        """
        return await self._patch(self._base(webstore_id), json=body)

    async def init_otp(
        self, webstore_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Initiate a one-time password (OTP) via SMS or email.

        Args:
            body: Buyer Profile Initiate OTP Input payload.
        """
        return await self._post(
            f"{self._base(webstore_id)}/actions/initOTP", json=body
        )

    async def verify_otp(
        self, webstore_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate the OTP provided by the buyer.

        Args:
            body: Buyer Profile Verify Input payload.
        """
        return await self._post(
            f"{self._base(webstore_id)}/actions/verify", json=body
        )
