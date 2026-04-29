"""Commerce Wishlists operations.

Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
prefix) — the client supplies a dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class CommerceWishlistsOperations(ConnectBaseOperations):
    """Wrapper for ``/commerce/webstores/{id}/wishlists/...`` endpoints."""

    def _base(self, webstore_id: str) -> str:
        return f"commerce/webstores/{self._ensure_18(webstore_id)}/wishlists"

    async def list_wishlists(
        self,
        webstore_id: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get wishlists for the current buyer."""
        return await self._get(self._base(webstore_id), params=params or {})

    async def create_wishlist(self, webstore_id: str, body: dict[str, Any]) -> dict[str, Any]:
        """Create a wishlist.

        Args:
            body: Wishlist Input payload.
        """
        return await self._post(self._base(webstore_id), json=body)

    async def get_wishlist(self, webstore_id: str, wishlist_id: str) -> dict[str, Any]:
        """Get a wishlist."""
        wishlist_id = self._ensure_18(wishlist_id)
        return await self._get(f"{self._base(webstore_id)}/{wishlist_id}")

    async def update_wishlist(
        self,
        webstore_id: str,
        wishlist_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Update the name of a wishlist."""
        wishlist_id = self._ensure_18(wishlist_id)
        return await self._patch(f"{self._base(webstore_id)}/{wishlist_id}", json=body)

    async def delete_wishlist(self, webstore_id: str, wishlist_id: str) -> dict[str, Any]:
        """Delete a wishlist."""
        wishlist_id = self._ensure_18(wishlist_id)
        return await self._delete(f"{self._base(webstore_id)}/{wishlist_id}")

    async def add_to_cart(
        self,
        webstore_id: str,
        wishlist_id: str,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Add a wishlist to a cart."""
        wishlist_id = self._ensure_18(wishlist_id)
        return await self._post(
            f"{self._base(webstore_id)}/{wishlist_id}/actions/add-wishlist-to-cart",
            json=body or {},
        )

    async def list_items(self, webstore_id: str, wishlist_id: str) -> dict[str, Any]:
        """Get wishlist items."""
        wishlist_id = self._ensure_18(wishlist_id)
        return await self._get(f"{self._base(webstore_id)}/{wishlist_id}/wishlist-items")

    async def add_item(
        self,
        webstore_id: str,
        wishlist_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Add an item to a wishlist."""
        wishlist_id = self._ensure_18(wishlist_id)
        return await self._post(
            f"{self._base(webstore_id)}/{wishlist_id}/wishlist-items",
            json=body,
        )

    async def delete_item(
        self,
        webstore_id: str,
        wishlist_id: str,
        wishlist_item_id: str,
    ) -> dict[str, Any]:
        """Delete a wishlist item."""
        wishlist_id = self._ensure_18(wishlist_id)
        wishlist_item_id = self._ensure_18(wishlist_item_id)
        return await self._delete(
            f"{self._base(webstore_id)}/{wishlist_id}/wishlist-items/{wishlist_item_id}"
        )
