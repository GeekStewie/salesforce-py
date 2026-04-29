"""Navigation Menu Items Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class NavigationMenuOperations(ConnectBaseOperations):
    """Wrapper for
    ``/connect/communities/{communityId}/navigation-menu/navigation-menu-items``.
    """

    async def list_items(
        self,
        community_id: str,
        *,
        navigation_link_set_id: str | None = None,
        navigation_link_set_developer_name: str | None = None,
        publish_status: str | None = None,
        add_home_menu_item: bool | None = None,
        include_image_url: bool | None = None,
        menu_item_types_to_skip: list[str] | None = None,
        effective_account_id: str | None = None,
    ) -> dict[str, Any]:
        """Get navigation menu items for a site (v47.0+).

        Args:
            community_id: Community ID (15 or 18 characters).
            navigation_link_set_id: ID of the navigation link set.
            navigation_link_set_developer_name: Developer name of the
                navigation link set (use this OR
                ``navigation_link_set_id``).
            publish_status: ``Draft`` or ``Live``.
            add_home_menu_item: Whether to include the Home menu item.
            include_image_url: Whether to include each item's image URL.
            menu_item_types_to_skip: Types to filter out (e.g.
                ``["Event", "ExternalLink"]``).
            effective_account_id: Account context for the request.

        Returns:
            Navigation Menu Item Collection dict.
        """
        community_id = self._ensure_18(community_id)
        params: dict[str, Any] = {}
        if navigation_link_set_id is not None:
            params["navigationLinkSetId"] = navigation_link_set_id
        if navigation_link_set_developer_name is not None:
            params["navigationLinkSetDeveloperName"] = (
                navigation_link_set_developer_name
            )
        if publish_status is not None:
            params["publishStatus"] = publish_status
        if add_home_menu_item is not None:
            params["addHomeMenuItem"] = add_home_menu_item
        if include_image_url is not None:
            params["includeImageUrl"] = include_image_url
        if menu_item_types_to_skip is not None:
            params["menuItemTypesToSkip"] = ",".join(menu_item_types_to_skip)
        if effective_account_id is not None:
            params["effectiveAccountId"] = self._ensure_18(effective_account_id)
        return await self._get(
            f"communities/{community_id}/navigation-menu/navigation-menu-items",
            params=params,
        )
