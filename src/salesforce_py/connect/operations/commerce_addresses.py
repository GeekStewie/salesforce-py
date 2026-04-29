"""Commerce B2B/B2C Address Management operations.

Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
prefix) — the client supplies a dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class CommerceAddressesOperations(ConnectBaseOperations):
    """Wrapper for ``/commerce/webstores/{id}/accounts/{id}/addresses/...``."""

    async def list_addresses(
        self,
        webstore_id: str,
        account_id: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Retrieve addresses for a webstore account.

        Args:
            webstore_id: Webstore ID.
            account_id: Account ID.
            params: Optional query parameters (e.g. ``addressType``, ``pageSize``).

        Returns:
            Commerce Account Addresses dict.
        """
        webstore_id = self._ensure_18(webstore_id)
        account_id = self._ensure_18(account_id)
        return await self._get(
            f"commerce/webstores/{webstore_id}/accounts/{account_id}/addresses",
            params=params or {},
        )

    async def create_address(
        self, webstore_id: str, account_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a Commerce account address.

        Args:
            webstore_id: Webstore ID.
            account_id: Account ID.
            body: Commerce Account Address Input payload.

        Returns:
            Commerce Account Address dict.
        """
        webstore_id = self._ensure_18(webstore_id)
        account_id = self._ensure_18(account_id)
        return await self._post(
            f"commerce/webstores/{webstore_id}/accounts/{account_id}/addresses",
            json=body,
        )

    async def update_address(
        self,
        webstore_id: str,
        account_id: str,
        address_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Update a Commerce account address.

        Args:
            webstore_id: Webstore ID.
            account_id: Account ID.
            address_id: Address ID.
            body: Commerce Account Address Input payload.

        Returns:
            Commerce Account Address dict.
        """
        webstore_id = self._ensure_18(webstore_id)
        account_id = self._ensure_18(account_id)
        address_id = self._ensure_18(address_id)
        return await self._patch(
            f"commerce/webstores/{webstore_id}/accounts/{account_id}/addresses/{address_id}",
            json=body,
        )

    async def delete_address(
        self, webstore_id: str, account_id: str, address_id: str
    ) -> dict[str, Any]:
        """Delete a Commerce account address.

        Args:
            webstore_id: Webstore ID.
            account_id: Account ID.
            address_id: Address ID.

        Returns:
            Empty dict on success.
        """
        webstore_id = self._ensure_18(webstore_id)
        account_id = self._ensure_18(account_id)
        address_id = self._ensure_18(address_id)
        return await self._delete(
            f"commerce/webstores/{webstore_id}/accounts/{account_id}/addresses/{address_id}"
        )
