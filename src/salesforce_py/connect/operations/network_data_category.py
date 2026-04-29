"""Network Data Category Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class NetworkDataCategoryOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/communities/{communityId}/.../network-data-category``
    endpoints.

    Includes the category-tree GET/PUT, per-record PATCH, child
    category, parent path, articles, catalog items, and org-wide
    data category groups.
    """

    # ------------------------------------------------------------------
    # Tree  /connect/communities/{communityId}/data-category/network-data-category
    # ------------------------------------------------------------------

    async def get_tree(self, community_id: str) -> dict[str, Any]:
        """Get the network data category tree for a site.

        Args:
            community_id: Community ID (15 or 18 characters).

        Returns:
            Network Data Category Tree dict.
        """
        community_id = self._ensure_18(community_id)
        return await self._get(
            f"communities/{community_id}/data-category/network-data-category"
        )

    async def replace_tree(
        self,
        community_id: str,
        data_category_groups: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Replace the network data category tree.

        Args:
            community_id: Community ID.
            data_category_groups: Collection of data category groups.

        Returns:
            Network Data Category Tree dict.
        """
        community_id = self._ensure_18(community_id)
        body = {"dataCategoryGroups": data_category_groups}
        return await self._put(
            f"communities/{community_id}/data-category/network-data-category",
            json=body,
        )

    # ------------------------------------------------------------------
    # Single record  .../network-data-category/{networkDataCategoryId}
    # ------------------------------------------------------------------

    async def update_category(
        self,
        community_id: str,
        network_data_category_id: str,
        *,
        label: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Update a network data category record (v60.0+).

        At least one of ``label`` or ``description`` is required per the
        API docs.

        Args:
            community_id: Community ID.
            network_data_category_id: Network data category ID.
            label: New label.
            description: New description.

        Returns:
            Network Data Category dict.
        """
        community_id = self._ensure_18(community_id)
        params: dict[str, Any] = {}
        if label is not None:
            params["label"] = label
        if description is not None:
            params["description"] = description
        return await self._patch(
            f"communities/{community_id}/network-data-category/{network_data_category_id}",
            params=params,
        )

    async def get_child_categories(
        self,
        community_id: str,
        network_data_category_id: str,
        *,
        language: str | None = None,
        page_number: int | None = None,
        page_size: int | None = None,
        sort_order: str | None = None,
        sorted_by: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve child categories of a network data category.

        Args:
            community_id: Community ID.
            network_data_category_id: Parent network data category ID.
            language: Language code. Defaults to user's org language.
            page_number: Zero-based page number.
            page_size: Items per page (max 25, default 3).
            sort_order: ``Ascending``, ``Descending``, or
                ``MostRecentlyViewed``.
            sorted_by: Field name to sort by.

        Returns:
            Network Data Category Collection dict.
        """
        community_id = self._ensure_18(community_id)
        params: dict[str, Any] = {}
        if language is not None:
            params["language"] = language
        if page_number is not None:
            params["pageNumber"] = page_number
        if page_size is not None:
            params["pageSize"] = page_size
        if sort_order is not None:
            params["sortOrder"] = sort_order
        if sorted_by is not None:
            params["sortedBy"] = sorted_by
        return await self._get(
            f"communities/{community_id}/network-data-category/{network_data_category_id}/child-category",
            params=params,
        )

    async def get_parent_path(
        self,
        community_id: str,
        network_data_category_id: str,
        *,
        language: str | None = None,
    ) -> dict[str, Any]:
        """Retrieve the parent path of a network data category.

        Args:
            community_id: Community ID.
            network_data_category_id: Network data category ID.
            language: Language code.

        Returns:
            Network Data Category Collection dict.
        """
        community_id = self._ensure_18(community_id)
        params: dict[str, Any] = {}
        if language is not None:
            params["language"] = language
        return await self._get(
            f"communities/{community_id}/network-data-category/{network_data_category_id}/parent-path",
            params=params,
        )

    async def get_articles(
        self,
        community_id: str,
        network_data_category_id: str,
        *,
        language: str | None = None,
        page_number: int | None = None,
        page_size: int | None = None,
        sort_order: str | None = None,
        sorted_by: str | None = None,
    ) -> dict[str, Any]:
        """Get knowledge articles for a network data category.

        Args:
            community_id: Community ID.
            network_data_category_id: Network data category ID.
            language: Language code.
            page_number: Zero-based page number.
            page_size: Items per page (1–25, default 3).
            sort_order: ``Ascending`` or ``Descending``.
            sorted_by: Sort field.

        Returns:
            Lightning Knowledge Article Version Collection dict.
        """
        community_id = self._ensure_18(community_id)
        params: dict[str, Any] = {}
        if language is not None:
            params["language"] = language
        if page_number is not None:
            params["pageNumber"] = page_number
        if page_size is not None:
            params["pageSize"] = page_size
        if sort_order is not None:
            params["sortOrder"] = sort_order
        if sorted_by is not None:
            params["sortedBy"] = sorted_by
        return await self._get(
            f"communities/{community_id}/network-data-category/{network_data_category_id}/knowledge-article",
            params=params,
        )

    async def get_catalog_items(
        self,
        network_data_category_id: str,
        *,
        community_id: str | None = None,
        page_number: int | None = None,
        page_size: int | None = None,
        sort_order: str | None = None,
        sorted_by: str | None = None,
    ) -> dict[str, Any]:
        """Get catalog items for a network data category.

        Args:
            network_data_category_id: Network data category ID.
            community_id: Optional community ID — if omitted, calls the
                org-scoped variant.
            page_number: Zero-based page number.
            page_size: 1–25, default 3.
            sort_order: ``Ascending`` or ``Descending``.
            sorted_by: Sort field.

        Returns:
            Service Catalog Item Collection dict.
        """
        params: dict[str, Any] = {}
        if page_number is not None:
            params["pageNumber"] = page_number
        if page_size is not None:
            params["pageSize"] = page_size
        if sort_order is not None:
            params["sortOrder"] = sort_order
        if sorted_by is not None:
            params["sortedBy"] = sorted_by
        if community_id is not None:
            community_id = self._ensure_18(community_id)
            path = (
                f"communities/{community_id}/network-data-category/"
                f"{network_data_category_id}/catalog-item"
            )
        else:
            path = f"network-data-category/{network_data_category_id}/catalog-item"
        return await self._get(path, params=params)

    # ------------------------------------------------------------------
    # Org-wide data category groups
    # ------------------------------------------------------------------

    async def list_category_groups(self) -> dict[str, Any]:
        """Get active data category groups and their subcategories.

        Returns:
            Data Category Group Collection dict.
        """
        return await self._get("data-category/category-group")
