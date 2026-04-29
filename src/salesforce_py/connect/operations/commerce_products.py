"""Commerce B2B/B2C Products, Product Categories, and Product Search operations.

Uses a session rooted at ``/services/data/vXX.X/`` (no ``connect/``
prefix) — the client supplies a dedicated ``_data_session``.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class CommerceProductsOperations(ConnectBaseOperations):
    """Wrapper for ``/commerce/webstores/{id}/products`` and search endpoints."""

    def _base(self, webstore_id: str) -> str:
        return f"commerce/webstores/{self._ensure_18(webstore_id)}"

    async def list_products(
        self,
        webstore_id: str,
        *,
        ids: list[str] | None = None,
        effective_account_id: str | None = None,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Get fields and default images for a list of products.

        Args:
            webstore_id: Webstore ID.
            ids: Product IDs.
            effective_account_id: Effective account ID override.
            fields: Fields to return per product.

        Returns:
            Product Collection dict.
        """
        params: dict[str, Any] = {}
        if ids is not None:
            params["ids"] = ",".join(ids)
        if effective_account_id is not None:
            params["effectiveAccountId"] = self._ensure_18(effective_account_id)
        if fields is not None:
            params["fields"] = ",".join(fields)
        return await self._get(
            f"{self._base(webstore_id)}/products", params=params
        )

    async def get_product(
        self,
        webstore_id: str,
        product_id: str,
        *,
        effective_account_id: str | None = None,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Get a product."""
        product_id = self._ensure_18(product_id)
        params: dict[str, Any] = {}
        if effective_account_id is not None:
            params["effectiveAccountId"] = self._ensure_18(effective_account_id)
        if fields is not None:
            params["fields"] = ",".join(fields)
        return await self._get(
            f"{self._base(webstore_id)}/products/{product_id}", params=params
        )

    async def list_featured_products(
        self, webstore_id: str, product_id: str
    ) -> dict[str, Any]:
        """Retrieve a collection of featured products for a specific product."""
        product_id = self._ensure_18(product_id)
        return await self._get(
            f"{self._base(webstore_id)}/products/{product_id}/featured-products"
        )

    async def list_child_products(
        self, webstore_id: str, product_id: str
    ) -> dict[str, Any]:
        """Get child products related to a parent product."""
        product_id = self._ensure_18(product_id)
        return await self._get(
            f"{self._base(webstore_id)}/products/{product_id}/children"
        )

    # Product categories

    async def list_child_categories(
        self,
        webstore_id: str,
        *,
        parent_product_category_id: str | None = None,
        effective_account_id: str | None = None,
    ) -> dict[str, Any]:
        """Get product categories for a specific parent category, or top-level.

        Args:
            webstore_id: Webstore ID.
            parent_product_category_id: Parent category ID (omit for top-level).
            effective_account_id: Effective account ID override.

        Returns:
            Product Category Collection dict.
        """
        params: dict[str, Any] = {}
        if parent_product_category_id is not None:
            params["parentProductCategoryId"] = self._ensure_18(
                parent_product_category_id
            )
        if effective_account_id is not None:
            params["effectiveAccountId"] = self._ensure_18(effective_account_id)
        return await self._get(
            f"{self._base(webstore_id)}/product-categories/children",
            params=params,
        )

    async def get_product_category(
        self, webstore_id: str, product_category_id: str
    ) -> dict[str, Any]:
        """Get a product category."""
        product_category_id = self._ensure_18(product_category_id)
        return await self._get(
            f"{self._base(webstore_id)}"
            f"/product-categories/{product_category_id}"
        )

    async def get_product_category_path(
        self, webstore_id: str, product_category_id: str
    ) -> dict[str, Any]:
        """Get the category path from the root to a category."""
        product_category_id = self._ensure_18(product_category_id)
        return await self._get(
            f"{self._base(webstore_id)}/product-category-path/"
            f"product-categories/{product_category_id}"
        )

    async def list_category_menu_items(
        self,
        webstore_id: str,
        *,
        parent_product_category_id: str | None = None,
        depth: int | None = None,
    ) -> dict[str, Any]:
        """Retrieve product category menu items."""
        params: dict[str, Any] = {}
        if parent_product_category_id is not None:
            params["parentProductCategoryId"] = self._ensure_18(
                parent_product_category_id
            )
        if depth is not None:
            params["depth"] = depth
        return await self._get(
            f"{self._base(webstore_id)}/category-menu-items", params=params
        )

    # Search

    async def search_products(
        self, webstore_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        """Search products (POST ``/search/product-search``).

        Args:
            webstore_id: Webstore ID.
            body: Product Search Input payload.

        Returns:
            Product Search Results dict.
        """
        return await self._post(
            f"{self._base(webstore_id)}/search/product-search", json=body
        )

    async def search_products_by_term(
        self,
        webstore_id: str,
        *,
        search_term: str | None = None,
        category_id: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Search products by term or category (GET ``/search/products``)."""
        params: dict[str, Any] = {}
        if search_term is not None:
            params["searchTerm"] = search_term
        if category_id is not None:
            params["categoryId"] = self._ensure_18(category_id)
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["pageSize"] = page_size
        return await self._get(
            f"{self._base(webstore_id)}/search/products", params=params
        )

    async def get_sort_rules(self, webstore_id: str) -> dict[str, Any]:
        """Get sort rules for the live index."""
        return await self._get(f"{self._base(webstore_id)}/search/sort-rules")

    async def get_search_suggestions(
        self,
        webstore_id: str,
        *,
        search_term: str,
        max_results: int | None = None,
    ) -> dict[str, Any]:
        """Get suggestions for product searches."""
        params: dict[str, Any] = {"searchTerm": search_term}
        if max_results is not None:
            params["maxResults"] = max_results
        return await self._get(
            f"{self._base(webstore_id)}/search/suggestions", params=params
        )
