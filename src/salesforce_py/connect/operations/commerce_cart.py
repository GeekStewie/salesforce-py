"""Commerce B2B/B2C Cart operations.

Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
prefix) — the client supplies a dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class CommerceCartOperations(ConnectBaseOperations):
    """Wrapper for ``/commerce/webstores/{id}/carts/...`` endpoints."""

    def _base(self, webstore_id: str) -> str:
        return f"commerce/webstores/{self._ensure_18(webstore_id)}/carts"

    async def create_cart(
        self, webstore_id: str, body: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Create a cart.

        Args:
            webstore_id: Webstore ID.
            body: Cart Input payload (optional).

        Returns:
            Cart Summary dict.
        """
        return await self._post(self._base(webstore_id), json=body or {})

    async def get_compact_summary(
        self, webstore_id: str, *, effective_account_id: str | None = None
    ) -> dict[str, Any]:
        """Get a compact cart summary for an existing cart.

        Args:
            webstore_id: Webstore ID.
            effective_account_id: Effective account ID override.

        Returns:
            Compact Cart Summary dict.
        """
        params: dict[str, Any] = {}
        if effective_account_id is not None:
            params["effectiveAccountId"] = self._ensure_18(effective_account_id)
        return await self._get(f"{self._base(webstore_id)}/compact-summary", params=params)

    async def get_cart(
        self,
        webstore_id: str,
        cart_state_or_id: str = "active",
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get a cart.

        Args:
            webstore_id: Webstore ID.
            cart_state_or_id: Cart state (``"active"``/``"current"``) or cart ID.
            params: Optional query parameters.

        Returns:
            Cart Summary dict.
        """
        return await self._get(f"{self._base(webstore_id)}/{cart_state_or_id}", params=params or {})

    async def delete_cart(
        self, webstore_id: str, cart_state_or_id: str = "active"
    ) -> dict[str, Any]:
        """Delete a cart.

        Args:
            webstore_id: Webstore ID.
            cart_state_or_id: Cart state or cart ID.

        Returns:
            Empty dict on success.
        """
        return await self._delete(f"{self._base(webstore_id)}/{cart_state_or_id}")

    async def calculate(self, webstore_id: str, cart_state_or_id: str = "active") -> dict[str, Any]:
        """Perform a complete cart calculation.

        Args:
            webstore_id: Webstore ID.
            cart_state_or_id: Cart state or cart ID.

        Returns:
            Cart Calculation Output dict.
        """
        return await self._post(f"{self._base(webstore_id)}/{cart_state_or_id}/actions/calculate")

    async def evaluate_shipping(
        self, webstore_id: str, cart_state_or_id: str = "active"
    ) -> dict[str, Any]:
        """Evaluate shipping costs for a cart."""
        return await self._post(
            f"{self._base(webstore_id)}/{cart_state_or_id}/actions/evaluate-shipping"
        )

    async def evaluate_taxes(
        self, webstore_id: str, cart_state_or_id: str = "active"
    ) -> dict[str, Any]:
        """Evaluate taxes for a cart."""
        return await self._post(
            f"{self._base(webstore_id)}/{cart_state_or_id}/actions/evaluate-taxes"
        )

    async def add_cart_to_wishlist(
        self,
        webstore_id: str,
        cart_state_or_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Copy products from a cart to a wishlist.

        Args:
            webstore_id: Webstore ID.
            cart_state_or_id: Cart state or cart ID.
            body: Wishlist input (must include ``wishlistId``).

        Returns:
            Wishlist dict.
        """
        return await self._post(
            f"{self._base(webstore_id)}/{cart_state_or_id}/actions/add-cart-to-wishlist",
            json=body,
        )

    async def clone(self, webstore_id: str, cart_state_or_id: str) -> dict[str, Any]:
        """Clone an existing cart."""
        return await self._post(f"{self._base(webstore_id)}/{cart_state_or_id}/actions/clone")

    async def make_primary(self, webstore_id: str, cart_state_or_id: str) -> dict[str, Any]:
        """Make a secondary cart a primary cart."""
        return await self._post(
            f"{self._base(webstore_id)}/{cart_state_or_id}/actions/make-primary"
        )

    async def preserve(self, webstore_id: str, cart_state_or_id: str) -> dict[str, Any]:
        """Preserve cart contents when a guest logs in."""
        return await self._post(f"{self._base(webstore_id)}/{cart_state_or_id}/actions/preserve")

    async def set_message_visibility(
        self,
        webstore_id: str,
        cart_state_or_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Set the visibility for cart messages."""
        return await self._post(
            f"{self._base(webstore_id)}/{cart_state_or_id}/messages/actions/set-visibility",
            json=body,
        )

    # Cart coupons

    async def list_coupons(
        self, webstore_id: str, cart_state_or_id: str = "active"
    ) -> dict[str, Any]:
        """Get coupons associated with a cart."""
        return await self._get(f"{self._base(webstore_id)}/{cart_state_or_id}/cart-coupons")

    async def apply_coupon(
        self,
        webstore_id: str,
        cart_state_or_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply a coupon code to a cart.

        Args:
            body: Cart Coupon Input payload (includes ``couponCode``).
        """
        return await self._post(
            f"{self._base(webstore_id)}/{cart_state_or_id}/cart-coupons",
            json=body,
        )

    async def delete_coupon(
        self,
        webstore_id: str,
        cart_state_or_id: str,
        cart_coupon_id: str,
    ) -> dict[str, Any]:
        """Delete a coupon from a cart."""
        cart_coupon_id = self._ensure_18(cart_coupon_id)
        return await self._delete(
            f"{self._base(webstore_id)}/{cart_state_or_id}/cart-coupons/{cart_coupon_id}"
        )

    # Cart items / products

    async def list_products(
        self,
        webstore_id: str,
        cart_state_or_id: str = "active",
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get items in a cart sorted by product ID."""
        return await self._get(
            f"{self._base(webstore_id)}/{cart_state_or_id}/products",
            params=params or {},
        )

    async def get_product(
        self,
        webstore_id: str,
        cart_state_or_id: str,
        product_id: str,
    ) -> dict[str, Any]:
        """Get cart items of a specific product."""
        product_id = self._ensure_18(product_id)
        return await self._get(
            f"{self._base(webstore_id)}/{cart_state_or_id}/products/{product_id}"
        )

    async def list_promotions(
        self, webstore_id: str, cart_state_or_id: str = "active"
    ) -> dict[str, Any]:
        """Get promotions associated with a cart."""
        return await self._get(f"{self._base(webstore_id)}/{cart_state_or_id}/promotions")

    async def list_items(
        self,
        webstore_id: str,
        cart_state_or_id: str = "active",
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get the items in a cart."""
        return await self._get(
            f"{self._base(webstore_id)}/{cart_state_or_id}/cart-items",
            params=params or {},
        )

    async def add_item(
        self,
        webstore_id: str,
        cart_state_or_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Add an item to a cart.

        Args:
            body: Cart Item Input payload.
        """
        return await self._post(
            f"{self._base(webstore_id)}/{cart_state_or_id}/cart-items",
            json=body,
        )

    async def add_items_batch(
        self,
        webstore_id: str,
        cart_state_or_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Add a batch of up to 100 items to a cart."""
        return await self._post(
            f"{self._base(webstore_id)}/{cart_state_or_id}/cart-items/batch",
            json=body,
        )

    async def update_item(
        self,
        webstore_id: str,
        cart_state_or_id: str,
        cart_item_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Update an item in a cart."""
        cart_item_id = self._ensure_18(cart_item_id)
        return await self._patch(
            f"{self._base(webstore_id)}/{cart_state_or_id}/cart-items/{cart_item_id}",
            json=body,
        )

    async def delete_item(
        self,
        webstore_id: str,
        cart_state_or_id: str,
        cart_item_id: str,
    ) -> dict[str, Any]:
        """Delete an item from a cart."""
        cart_item_id = self._ensure_18(cart_item_id)
        return await self._delete(
            f"{self._base(webstore_id)}/{cart_state_or_id}/cart-items/{cart_item_id}"
        )

    async def list_item_promotions(
        self, webstore_id: str, cart_state_or_id: str = "active"
    ) -> dict[str, Any]:
        """Get promotions associated with items in a cart."""
        return await self._get(
            f"{self._base(webstore_id)}/{cart_state_or_id}/cart-items/promotions"
        )

    async def apply_item_configuration(
        self,
        webstore_id: str,
        cart_state_or_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Apply a saved configuration context to a cart item."""
        return await self._post(
            f"{self._base(webstore_id)}/{cart_state_or_id}/cart-items/actions/apply-configuration",
            json=body,
        )

    # Delivery groups

    async def list_delivery_groups(
        self, webstore_id: str, cart_state_or_id: str = "active"
    ) -> dict[str, Any]:
        """Get the delivery groups of a cart."""
        return await self._get(f"{self._base(webstore_id)}/{cart_state_or_id}/delivery-groups")

    async def create_delivery_group(
        self,
        webstore_id: str,
        cart_state_or_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Create a delivery group."""
        return await self._post(
            f"{self._base(webstore_id)}/{cart_state_or_id}/delivery-groups",
            json=body,
        )

    async def get_delivery_group(
        self,
        webstore_id: str,
        cart_state_or_id: str,
        delivery_group_id: str,
    ) -> dict[str, Any]:
        """Get a delivery group."""
        delivery_group_id = self._ensure_18(delivery_group_id)
        return await self._get(
            f"{self._base(webstore_id)}/{cart_state_or_id}/delivery-groups/{delivery_group_id}"
        )

    async def update_delivery_group(
        self,
        webstore_id: str,
        cart_state_or_id: str,
        delivery_group_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Update a delivery group."""
        delivery_group_id = self._ensure_18(delivery_group_id)
        return await self._patch(
            f"{self._base(webstore_id)}/{cart_state_or_id}/delivery-groups/{delivery_group_id}",
            json=body,
        )

    async def delete_delivery_group(
        self,
        webstore_id: str,
        cart_state_or_id: str,
        delivery_group_id: str,
    ) -> dict[str, Any]:
        """Delete a delivery group."""
        delivery_group_id = self._ensure_18(delivery_group_id)
        return await self._delete(
            f"{self._base(webstore_id)}/{cart_state_or_id}/delivery-groups/{delivery_group_id}"
        )

    async def arrange_delivery_group_items(
        self,
        webstore_id: str,
        cart_state_or_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Arrange cart items into delivery groups."""
        return await self._post(
            f"{self._base(webstore_id)}/{cart_state_or_id}/delivery-groups/actions/arrange-items",
            json=body,
        )
