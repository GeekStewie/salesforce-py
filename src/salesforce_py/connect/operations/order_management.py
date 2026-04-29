"""Salesforce Order Management operations.

Manage orders and the order fulfillment process. Uses a session rooted at
``/services/data/vXX.X/`` (no ``connect/`` prefix) — the client supplies a
dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class OrderManagementOperations(ConnectBaseOperations):
    """Wrapper for ``/commerce/fulfillment``, ``/commerce/order-management``,
    ``/commerce/order-summaries``, ``/commerce/returns`` and related endpoints.
    """

    # ------------------------------------------------------------------
    # Guest buyer
    # ------------------------------------------------------------------

    async def register_guest_buyer(self, webstore_id: str, account_id: str) -> dict[str, Any]:
        """Register a guest buyer for a webstore using an account ID (v60.0+)."""
        return await self._post(
            f"commerce/webstores/{self._ensure_18(webstore_id)}/accounts/"
            f"{self._ensure_18(account_id)}/actions/register-guest-buyer"
        )

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    async def get_products_return_rate(
        self,
        *,
        page: int,
        page_size: int,
        products: list[str] | None = None,
        data_space_prefixes: list[str] | None = None,
    ) -> dict[str, Any]:
        """Get a page of products with return rates (v59.0+)."""
        params: dict[str, Any] = {"page": page, "pageSize": page_size}
        if products is not None:
            params["products"] = products
        if data_space_prefixes is not None:
            params["dataSpacePrefixes"] = data_space_prefixes
        return await self._get(
            "commerce/order-management/analytics/insights/products-return-rate",
            params=params,
        )

    async def get_text_classifications_bulk(self, ids: list[str]) -> dict[str, Any]:
        """Retrieve bulk text classification results (v59.0+)."""
        return await self._get(
            "commerce/order-management/analytics/ai/text-classifications",
            params={"ids": ids},
        )

    async def classify_text(
        self, body: dict[str, Any], *, llm_type: str = "open-ai"
    ) -> dict[str, Any]:
        """Classify text into classifications using text analysis (v59.0+)."""
        return await self._post(
            "commerce/order-management/analytics/ai/text-classifications",
            json=body,
            params={"llmType": llm_type},
        )

    # ------------------------------------------------------------------
    # Delivery
    # ------------------------------------------------------------------

    async def estimate_delivery_date(self, body: dict[str, Any]) -> dict[str, Any]:
        """Forecast an expected delivery date and time (v63.0+)."""
        return await self._post(
            "commerce/delivery/estimation-setup/externalReference/estimate/estimate-date",
            json=body,
        )

    # ------------------------------------------------------------------
    # Fulfillment orders
    # ------------------------------------------------------------------

    async def create_fulfillment_order(self, body: dict[str, Any]) -> dict[str, Any]:
        """Create fulfillment orders for an OrderDeliveryGroupSummary (v48.0+)."""
        return await self._post("commerce/fulfillment/fulfillment-orders", json=body)

    async def cancel_fulfillment_items(
        self, fulfillment_order_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Cancel FulfillmentOrderLineItems from a FulfillmentOrder (v48.0+)."""
        fulfillment_order_id = self._ensure_18(fulfillment_order_id)
        return await self._post(
            f"commerce/fulfillment/fulfillment-orders/{fulfillment_order_id}/actions/cancel-item",
            json=body,
        )

    async def create_fulfillment_invoice(
        self, fulfillment_order_id: str, body: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Create an invoice for a FulfillmentOrder (v48.0+)."""
        fulfillment_order_id = self._ensure_18(fulfillment_order_id)
        return await self._post(
            f"commerce/fulfillment/fulfillment-orders/{fulfillment_order_id}"
            "/actions/create-invoice",
            json=body or {},
        )

    async def create_multiple_fulfillment_orders(self, body: dict[str, Any]) -> dict[str, Any]:
        """Create FulfillmentOrders for multiple OrderDeliveryGroups (v50.0+)."""
        return await self._post("commerce/fulfillment/actions/create-multiple", json=body)

    async def create_multiple_fulfillment_invoices(self, body: dict[str, Any]) -> dict[str, Any]:
        """Create Invoices for multiple FulfillmentOrders (v52.0+)."""
        return await self._post(
            "commerce/fulfillment/fulfillment-orders/actions/create-multiple-invoices",
            json=body,
        )

    async def distribute_picked_quantities(self, body: dict[str, Any]) -> dict[str, Any]:
        """Distribute batch-picked quantities to orders (v58.0+)."""
        return await self._post(
            "commerce/fulfillment/pick-tickets/actions/distribute-quantities",
            json=body,
        )

    # ------------------------------------------------------------------
    # Exchanges
    # ------------------------------------------------------------------

    async def preview_cart_to_exchange_order(self, body: dict[str, Any]) -> dict[str, Any]:
        """Retrieve a preview of an exchange order (v60.0+)."""
        return await self._post(
            "commerce/order-management/exchanges/actions/preview-cart-to-exchange-order",
            json=body,
        )

    async def submit_cart_to_exchange_order(self, body: dict[str, Any]) -> dict[str, Any]:
        """Create an exchange order summary (v60.0+)."""
        return await self._post(
            "commerce/order-management/exchanges/actions/submit-cart-to-exchange-order",
            json=body,
        )

    # ------------------------------------------------------------------
    # Order payment summaries
    # ------------------------------------------------------------------

    async def create_order_payment_summary(self, body: dict[str, Any]) -> dict[str, Any]:
        """Create an OrderPaymentSummary for an OrderSummary (v48.0+)."""
        return await self._post("commerce/order-management/order-payment-summaries", json=body)

    # ------------------------------------------------------------------
    # Order summaries
    # ------------------------------------------------------------------

    async def create_order_summary(self, body: dict[str, Any]) -> dict[str, Any]:
        """Create an OrderSummary based on an order (v48.0+)."""
        return await self._post("commerce/order-management/order-summaries", json=body)

    async def create_credit_memo(
        self, order_summary_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Create a credit memo for change orders of an OrderSummary (v48.0+)."""
        order_summary_id = self._ensure_18(order_summary_id)
        return await self._post(
            f"commerce/order-management/order-summaries/{order_summary_id}"
            "/actions/create-credit-memo",
            json=body,
        )

    async def create_multiple_change_invoices(self, body: dict[str, Any]) -> dict[str, Any]:
        """Create Invoices for one or more change orders (v56.0+)."""
        return await self._post(
            "commerce/order-management/order-summaries/actions/create-multiple-change-invoices",
            json=body,
        )

    async def ensure_funds_async(
        self, order_summary_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Ensure funds for an Invoice asynchronously (v48.0+)."""
        order_summary_id = self._ensure_18(order_summary_id)
        return await self._post(
            f"commerce/order-management/order-summaries/{order_summary_id}"
            "/async-actions/ensure-funds-async",
            json=body,
        )

    async def ensure_refunds_async(
        self, order_summary_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Ensure refunds for a CreditMemo asynchronously (v48.0+)."""
        order_summary_id = self._ensure_18(order_summary_id)
        return await self._post(
            f"commerce/order-management/order-summaries/{order_summary_id}"
            "/async-actions/ensure-refunds-async",
            json=body,
        )

    async def multiple_ensure_funds_async(self, body: dict[str, Any]) -> dict[str, Any]:
        """Ensure and apply funds for one or more Invoices (v56.0+)."""
        return await self._post(
            "commerce/order-management/order-summaries/async-actions/multiple-ensure-funds-async",
            json=body,
        )

    async def preview_adjust(self, order_summary_id: str, body: dict[str, Any]) -> dict[str, Any]:
        """Preview adjusting the price of OrderItemSummaries (v49.0+)."""
        order_summary_id = self._ensure_18(order_summary_id)
        return await self._post(
            f"commerce/order-management/order-summaries/{order_summary_id}"
            "/actions/adjust-item-preview",
            json=body,
        )

    async def preview_cancel(self, order_summary_id: str, body: dict[str, Any]) -> dict[str, Any]:
        """Preview canceling OrderItemSummaries (v48.0+)."""
        order_summary_id = self._ensure_18(order_summary_id)
        return await self._post(
            f"commerce/order-management/order-summaries/{order_summary_id}/actions/preview-cancel",
            json=body,
        )

    async def preview_return(self, order_summary_id: str, body: dict[str, Any]) -> dict[str, Any]:
        """Preview returning OrderItemSummaries (v48.0+)."""
        order_summary_id = self._ensure_18(order_summary_id)
        return await self._post(
            f"commerce/order-management/order-summaries/{order_summary_id}/actions/preview-return",
            json=body,
        )

    async def submit_adjust(self, order_summary_id: str, body: dict[str, Any]) -> dict[str, Any]:
        """Adjust the price of OrderItemSummaries (v49.0+)."""
        order_summary_id = self._ensure_18(order_summary_id)
        return await self._post(
            f"commerce/order-management/order-summaries/{order_summary_id}"
            "/actions/adjust-item-submit",
            json=body,
        )

    async def submit_cancel(self, order_summary_id: str, body: dict[str, Any]) -> dict[str, Any]:
        """Cancel OrderItemSummaries (v48.0+)."""
        order_summary_id = self._ensure_18(order_summary_id)
        return await self._post(
            f"commerce/order-management/order-summaries/{order_summary_id}/actions/submit-cancel",
            json=body,
        )

    async def submit_return(self, order_summary_id: str, body: dict[str, Any]) -> dict[str, Any]:
        """Return OrderItemSummaries (simple return) (v48.0+)."""
        order_summary_id = self._ensure_18(order_summary_id)
        return await self._post(
            f"commerce/order-management/order-summaries/{order_summary_id}/actions/submit-return",
            json=body,
        )

    # ------------------------------------------------------------------
    # Pending order summaries (High Scale Orders)
    # ------------------------------------------------------------------

    async def create_pending_order_summaries(self, body: dict[str, Any]) -> dict[str, Any]:
        """Create pending order summaries from order summary graphs (v57.0+)."""
        return await self._post("commerce/order-summaries", json=body)

    # ------------------------------------------------------------------
    # Products / repricing
    # ------------------------------------------------------------------

    async def get_products_with_return_reasons(
        self,
        *,
        products: list[str],
        scope: str,
        expand: str = "ReturnReasons",
    ) -> dict[str, Any]:
        """Capture return reasons for products (v59.0+)."""
        return await self._get(
            "commerce/order-management/products",
            params={"products": products, "scope": scope, "expand": expand},
        )

    async def get_product_details(
        self,
        webstore_id: str,
        sku_or_product_id: str,
        *,
        currency_code: str | None = None,
        effective_account_id: str | None = None,
        exclude_attribute_set_info: bool | None = None,
        exclude_bundle_children_info: bool | None = None,
        exclude_media: bool | None = None,
        exclude_quantity_rule: bool | None = None,
        exclude_variation_info: bool | None = None,
        exclude_prices: bool | None = None,
        locale: str | None = None,
    ) -> dict[str, Any]:
        """Get details of a product in a webstore (repricing) (v55.0+)."""
        params: dict[str, Any] = {}
        if currency_code is not None:
            params["currencyCode"] = currency_code
        if effective_account_id is not None:
            params["effectiveAccountId"] = self._ensure_18(effective_account_id)
        if exclude_attribute_set_info is not None:
            params["excludeAttributeSetInfo"] = exclude_attribute_set_info
        if exclude_bundle_children_info is not None:
            params["excludeBundleChildrenInfo"] = exclude_bundle_children_info
        if exclude_media is not None:
            params["excludeMedia"] = exclude_media
        if exclude_quantity_rule is not None:
            params["excludeQuantityRule"] = exclude_quantity_rule
        if exclude_variation_info is not None:
            params["excludeVariationInfo"] = exclude_variation_info
        if exclude_prices is not None:
            params["excludePrices"] = exclude_prices
        if locale is not None:
            params["locale"] = locale
        return await self._get(
            f"commerce/order-management/webstores/{self._ensure_18(webstore_id)}"
            f"/products/{sku_or_product_id}",
            params=params,
        )

    async def search_products(
        self,
        webstore_id: str,
        *,
        search_term: str,
        effective_account_id: str | None = None,
        facets: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Search a webstore for products by search term (repricing) (v59.0+)."""
        params: dict[str, Any] = {"searchTerm": search_term}
        if effective_account_id is not None:
            params["effectiveAccountId"] = self._ensure_18(effective_account_id)
        if facets is not None:
            params["facets"] = facets
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["pageSize"] = page_size
        return await self._get(
            f"commerce/order-management/webstores/{self._ensure_18(webstore_id)}/products",
            params=params,
        )

    # ------------------------------------------------------------------
    # Return orders
    # ------------------------------------------------------------------

    async def create_return_order(self, body: dict[str, Any]) -> dict[str, Any]:
        """Create a ReturnOrder and ReturnOrderLineItems (v50.0+)."""
        return await self._post("commerce/returns/return-orders", json=body)

    async def process_return_items(
        self, return_order_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Process ReturnOrderLineItems belonging to a ReturnOrder (v52.0+)."""
        return_order_id = self._ensure_18(return_order_id)
        return await self._post(
            f"commerce/returns/return-orders/{return_order_id}/actions/return-items",
            json=body,
        )

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    async def confirm_held_capacity(self, body: dict[str, Any]) -> dict[str, Any]:
        """Confirm held fulfillment order capacity (v55.0+)."""
        return await self._post(
            "commerce/order-management/routing/fulfillment-order-capacity/"
            "actions/confirm-held-capacity",
            json=body,
        )

    async def find_routes_with_fewest_splits(self, body: dict[str, Any]) -> dict[str, Any]:
        """Find routes with fewest splits (v51.0+)."""
        return await self._post(
            "commerce/order-management/routing/actions/find-routes-with-fewest-splits",
            json=body,
        )

    async def find_routes_with_fewest_splits_using_oci(
        self, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Find routes with fewest splits using OCI (v54.0+)."""
        return await self._post(
            "commerce/order-management/routing/actions/find-routes-with-fewest-splits-using-oci",
            json=body,
        )

    async def get_capacity_values(self, body: dict[str, Any]) -> dict[str, Any]:
        """Get current fulfillment order capacity of locations (v55.0+)."""
        return await self._post(
            "commerce/order-management/routing/fulfillment-order-capacity/"
            "actions/get-capacity-values",
            json=body,
        )

    async def hold_capacity(self, body: dict[str, Any]) -> dict[str, Any]:
        """Hold fulfillment order capacity at a location (v55.0+)."""
        return await self._post(
            "commerce/order-management/routing/fulfillment-order-capacity/actions/hold-capacity",
            json=body,
        )

    async def rank_by_average_distance(self, body: dict[str, Any]) -> dict[str, Any]:
        """Calculate and rank average distance from locations to recipient (v51.0+)."""
        return await self._post(
            "commerce/order-management/routing/actions/rank-byaverage-distance",
            json=body,
        )

    async def release_held_capacity(self, body: dict[str, Any]) -> dict[str, Any]:
        """Release held fulfillment order capacity (v55.0+)."""
        return await self._post(
            "commerce/order-management/routing/fulfillment-order-capacity/"
            "actions/release-held-capacity",
            json=body,
        )
