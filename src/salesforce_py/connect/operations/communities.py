"""Communities Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class CommunitiesOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/communities/`` endpoints.

    Covers listing, retrieving, creating, and publishing Experience
    Cloud sites, plus Experience Builder template discovery,
    externally-managed accounts, and site preview URLs. All methods are
    async.
    """

    async def list_communities(
        self,
        *,
        status: str | None = None,
    ) -> dict[str, Any]:
        """List Experience Cloud sites visible to the authenticated user.

        Args:
            status: Filter by site status (``Live``, ``Inactive``,
                ``UnderConstruction``).

        Returns:
            Community Page dict.
        """
        params: dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        return await self._get("communities", params=params)

    async def create_community(
        self,
        name: str,
        template_name: str,
        *,
        url_path_prefix: str | None = None,
        description: str | None = None,
        template_params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Create a new Experience Cloud site (v46.0+).

        Args:
            name: Site name.
            template_name: Experience Builder template name.
            url_path_prefix: URL prefix for the site.
            description: Site description.
            template_params: Template-specific parameters map.

        Returns:
            Community Create dict.
        """
        body: dict[str, Any] = {"name": name, "templateName": template_name}
        if url_path_prefix is not None:
            body["urlPathPrefix"] = url_path_prefix
        if description is not None:
            body["description"] = description
        if template_params is not None:
            body["templateParams"] = template_params
        return await self._post("communities", json=body)

    async def get_community(self, community_id: str) -> dict[str, Any]:
        """Retrieve a single community by ID.

        Args:
            community_id: Salesforce community (network) ID (15 or 18
                characters).

        Returns:
            Community detail dict.
        """
        community_id = self._ensure_18(community_id)
        return await self._get(f"communities/{community_id}")

    async def publish_community(self, community_id: str) -> dict[str, Any]:
        """Publish an Experience Cloud site (v46.0+).

        Args:
            community_id: Community ID (15 or 18 characters).

        Returns:
            Community Publish dict.
        """
        community_id = self._ensure_18(community_id)
        return await self._post(f"communities/{community_id}/publish")

    async def get_templates(self) -> dict[str, Any]:
        """Get Experience Builder templates available to the context user.

        Returns:
            Community Template Collection dict.
        """
        return await self._get("communities/templates")

    async def get_externally_managed_accounts(
        self,
        community_id: str,
        *,
        include_my_account: bool | None = None,
    ) -> dict[str, Any]:
        """Get externally-managed accounts across all Experience Cloud sites.

        Args:
            community_id: Community ID (15 or 18 characters) — required
                by the URL but the response is org-wide.
            include_my_account: Whether to return the context user's
                account.

        Returns:
            External Managed Account Collection Output dict.
        """
        community_id = self._ensure_18(community_id)
        params: dict[str, Any] = {}
        if include_my_account is not None:
            params["includeMyAccount"] = include_my_account
        return await self._get(
            f"communities/{community_id}/external-managed-accounts",
            params=params,
        )

    async def get_preview_url(
        self,
        community_id: str,
        page_api_name: str,
        *,
        url_parameters: str | None = None,
    ) -> dict[str, Any]:
        """Get a preview URL for a page in an Experience Cloud site (v61.0+).

        Args:
            community_id: Community ID (15 or 18 characters).
            page_api_name: API name of the page (e.g. ``Home``).
            url_parameters: URL-encoded key/value string.

        Returns:
            Preview URL dict.
        """
        community_id = self._ensure_18(community_id)
        params: dict[str, Any] = {}
        if url_parameters is not None:
            params["urlParameters"] = url_parameters
        return await self._get(
            f"communities/{community_id}/preview-url/pages/{page_api_name}",
            params=params,
        )

    async def get_community_members(
        self,
        community_id: str,
        *,
        page_size: int = 25,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """List members of a community.

        Args:
            community_id: Salesforce community ID (15 or 18 characters).
            page_size: Number of members to return per page.
            page_token: Opaque token from a previous call for pagination.

        Returns:
            Members page dict with ``currentPageToken``, ``nextPageToken``,
            and ``members`` keys.
        """
        community_id = self._ensure_18(community_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if page_token:
            params["pageToken"] = page_token
        return await self._get(f"communities/{community_id}/members", params=params)
