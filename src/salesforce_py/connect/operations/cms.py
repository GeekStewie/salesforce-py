"""Salesforce CMS Connect API operations.

Covers the two families of CMS endpoints documented in the Chatter/Connect
REST API guide:

- **CMS Managed Content** — delivery-oriented endpoints available whether
  or not an org has enhanced CMS workspaces
  (``/connect/cms/delivery/...`` and
  ``/connect/communities/<id>/managed-content/...``).
- **Enhanced CMS Workspaces** — authoring and workspace-management
  endpoints that require enhanced CMS workspaces
  (``/connect/cms/channels``, ``/connect/cms/contents``,
  ``/connect/cms/spaces``, ``/connect/cms/folders``,
  ``/connect/cms/digital-asset-management-providers``,
  ``/connect/cms/items/search``).
"""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class CMSManagedContentOperations(ConnectBaseOperations):
    """Wrapper for CMS managed content delivery and channel endpoints.

    These resources deliver published content and manage the searchable
    state of managed content in a channel.  They work for both classic
    and enhanced CMS workspaces (enhanced-only authoring is handled by
    :class:`CMSWorkspacesOperations`).

    All methods are async.
    """

    # ------------------------------------------------------------------
    # Experience Cloud site delivery
    # ------------------------------------------------------------------

    async def get_site_delivery(
        self,
        community_id: str,
        *,
        content_keys: list[str] | None = None,
        language: str | None = None,
        managed_content_ids: list[str] | None = None,
        managed_content_type: str | None = None,
        page: int | None = None,
        page_size: int = 25,
        show_absolute_url: bool | None = None,
        topics: list[str] | None = None,
    ) -> dict[str, Any]:
        """Get published managed content versions for an Experience Cloud site.

        Args:
            community_id: Experience Cloud site (network) ID
                (15 or 18 characters).
            content_keys: Up to 50 content keys (UUIDs).  Specify either
                ``content_keys`` or ``managed_content_ids``.
            language: Language locale, e.g. ``"en_US"``.
            managed_content_ids: Up to 200 managed content IDs
                (HTTP/2 only; HTTP/1.1 tops out lower).
            managed_content_type: Developer name of the content type,
                e.g. ``"cms_document"``.
            page: Zero-based page number.
            page_size: Items per page (1–250).
            show_absolute_url: Whether to return absolute URLs.
            topics: Up to 15 content topic names.

        Returns:
            Managed Content Version Collection dict.
        """
        community_id = self._ensure_18(community_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if content_keys:
            params["contentKeys"] = ",".join(content_keys)
        if language is not None:
            params["language"] = language
        if managed_content_ids:
            params["managedContentIds"] = ",".join(
                self._ensure_18_list(managed_content_ids)
            )
        if managed_content_type is not None:
            params["managedContentType"] = managed_content_type
        if page is not None:
            params["page"] = page
        if show_absolute_url is not None:
            params["showAbsoluteUrl"] = show_absolute_url
        if topics:
            params["topics"] = ",".join(topics)
        return await self._get(
            f"communities/{community_id}/managed-content/delivery", params=params
        )

    async def search_site_delivery(
        self,
        community_id: str,
        query_term: str,
        *,
        page: int | None = None,
        page_size: int = 25,
        scope: str | None = None,
    ) -> dict[str, Any]:
        """Search managed content in an Experience Cloud site.

        Args:
            community_id: Experience Cloud site ID (15 or 18 characters).
            query_term: SOSL query.
            page: Zero-based page number.
            page_size: Items per page (1–250).
            scope: ``"All"`` (default) or ``"TitleOnly"``.

        Returns:
            Managed Content Search Result Collection dict.
        """
        community_id = self._ensure_18(community_id)
        params: dict[str, Any] = {"queryTerm": query_term, "pageSize": page_size}
        if page is not None:
            params["page"] = page
        if scope is not None:
            params["scope"] = scope
        return await self._get(
            f"communities/{community_id}/managed-content/delivery/contents/search",
            params=params,
        )

    # ------------------------------------------------------------------
    # Delivery channels
    # ------------------------------------------------------------------

    async def list_delivery_channels(
        self,
        *,
        page: int | None = None,
        page_size: int = 25,
    ) -> dict[str, Any]:
        """Get managed content delivery channels for the context user.

        Args:
            page: Zero-based page number.
            page_size: Items per page (1–250).

        Returns:
            Managed Content Delivery Channels dict (62.0+) or
            Managed Content Channel Collection dict (48.0–61.0).
        """
        params: dict[str, Any] = {"pageSize": page_size}
        if page is not None:
            params["page"] = page
        return await self._get("cms/delivery/channels", params=params)

    async def get_delivery_channel(self, channel_id: str) -> dict[str, Any]:
        """Get a managed content delivery channel.

        Args:
            channel_id: Managed content channel ID (15 or 18 characters).

        Returns:
            Delivery channel dict.
        """
        channel_id = self._ensure_18(channel_id)
        return await self._get(f"cms/delivery/channels/{channel_id}")

    async def query_channel_contents(
        self,
        channel_id: str,
        *,
        content_keys: list[str] | None = None,
        end_date: str | None = None,
        include_metadata: bool | None = None,
        language: str | None = None,
        managed_content_ids: list[str] | None = None,
        managed_content_type: str | None = None,
        page: int | None = None,
        page_size: int = 25,
        show_absolute_url: bool | None = None,
        start_date: str | None = None,
    ) -> dict[str, Any]:
        """Get published managed content versions for a channel.

        Args:
            channel_id: Managed content channel ID (15 or 18 characters).
            content_keys: Up to 50 content keys (UUIDs).
            end_date: ISO 8601 publish end date.
            include_metadata: Whether to include metadata.
            language: Language locale, e.g. ``"en_US"``.
            managed_content_ids: Up to 200 managed content IDs.
            managed_content_type: Developer name of the content type.
            page: Zero-based page number.
            page_size: Items per page (1–250).
            show_absolute_url: Whether to return absolute URLs.
            start_date: ISO 8601 publish start date.

        Returns:
            Managed Content Version Collection dict.
        """
        channel_id = self._ensure_18(channel_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if content_keys:
            params["contentKeys"] = ",".join(content_keys)
        if end_date is not None:
            params["endDate"] = end_date
        if include_metadata is not None:
            params["includeMetadata"] = include_metadata
        if language is not None:
            params["language"] = language
        if managed_content_ids:
            params["managedContentIds"] = ",".join(
                self._ensure_18_list(managed_content_ids)
            )
        if managed_content_type is not None:
            params["managedContentType"] = managed_content_type
        if page is not None:
            params["page"] = page
        if show_absolute_url is not None:
            params["showAbsoluteUrl"] = show_absolute_url
        if start_date is not None:
            params["startDate"] = start_date
        return await self._get(
            f"cms/delivery/channels/{channel_id}/contents/query", params=params
        )

    async def search_channel_contents(
        self,
        channel_id: str,
        query_term: str,
        *,
        page: int | None = None,
        page_size: int = 25,
        scope: str | None = None,
    ) -> dict[str, Any]:
        """Search managed content in a channel (non-enhanced).

        For enhanced CMS workspaces, use
        :meth:`CMSWorkspacesOperations.enhanced_search_channel`.

        Args:
            channel_id: Managed content channel ID (15 or 18 characters).
            query_term: SOSL query.
            page: Zero-based page number.
            page_size: Items per page (1–250).
            scope: ``"All"`` (default) or ``"TitleOnly"``.

        Returns:
            Managed Content Search Result Collection dict.
        """
        channel_id = self._ensure_18(channel_id)
        params: dict[str, Any] = {"queryTerm": query_term, "pageSize": page_size}
        if page is not None:
            params["page"] = page
        if scope is not None:
            params["scope"] = scope
        return await self._get(
            f"cms/delivery/channels/{channel_id}/contents/search", params=params
        )

    async def get_delivery_media_content(
        self,
        channel_id: str,
        media_guid: str,
        *,
        language: str | None = None,
    ) -> bytes:
        """Get the binary stream of a media node of published content in a channel.

        Args:
            channel_id: Managed content channel ID (15 or 18 characters).
            media_guid: Unique identifier of the media node.
            language: Language locale, e.g. ``"en_US"``.

        Returns:
            Raw media bytes.
        """
        channel_id = self._ensure_18(channel_id)
        params: dict[str, Any] = {}
        if language is not None:
            params["language"] = language
        return await self._get_bytes(
            f"cms/delivery/channels/{channel_id}/media/{media_guid}/content",
            params=params,
        )

    # ------------------------------------------------------------------
    # Searchable content types
    # ------------------------------------------------------------------

    async def get_searchable_content_types(
        self,
        channel_id: str,
        *,
        page: int | None = None,
        page_size: int = 25,
    ) -> dict[str, Any]:
        """Get the searchable status for managed content types in a channel.

        Args:
            channel_id: Managed content channel ID (15 or 18 characters).
            page: Zero-based page number.
            page_size: Items per page (1–250).

        Returns:
            Managed Content Type Searchable Collection dict.
        """
        channel_id = self._ensure_18(channel_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if page is not None:
            params["page"] = page
        return await self._get(
            f"cms/channels/{channel_id}/searchable-content-types", params=params
        )

    async def update_searchable_content_type(
        self,
        channel_id: str,
        name: str,
        is_searchable: bool,
    ) -> dict[str, Any]:
        """Update the searchable status for a managed content type in a channel.

        Args:
            channel_id: Managed content channel ID (15 or 18 characters).
            name: Developer name of the managed content type.
                Use the fully qualified name in 63.0+ for package-installed
                content types.
            is_searchable: Whether the content type is searchable.

        Returns:
            Managed Content Type Searchable dict.
        """
        channel_id = self._ensure_18(channel_id)
        payload = {"name": name, "isSearchable": is_searchable}
        return await self._patch(
            f"cms/channels/{channel_id}/searchable-content-types", json=payload
        )

    # ------------------------------------------------------------------
    # Content / folder lookups (classic workspaces)
    # ------------------------------------------------------------------

    async def get_content(
        self,
        content_key_or_id: str,
        *,
        content_version: str | None = None,
        language: str | None = None,
        variant_version: str | None = None,
        version: str | None = None,
    ) -> dict[str, Any]:
        """Get a piece of managed content (or a version of it).

        Args:
            content_key_or_id: Content key (UUID) or managed content ID.
            content_version: Content version (66.0+).
            language: Language locale of the content.
            variant_version: Variant version (66.0+).
            version: Content version ID or number.

        Returns:
            Managed Content Document dict.
        """
        params: dict[str, Any] = {}
        if content_version is not None:
            params["contentVersion"] = content_version
        if language is not None:
            params["language"] = language
        if variant_version is not None:
            params["variantVersion"] = variant_version
        if version is not None:
            params["version"] = version
        return await self._get(
            f"cms/contents/{content_key_or_id}", params=params or None
        )

    async def get_folder(
        self,
        folder_id: str,
        *,
        context_content_space_id: str | None = None,
    ) -> dict[str, Any]:
        """Get a managed content folder.

        Args:
            folder_id: Managed content folder ID (15 or 18 characters).
            context_content_space_id: Optional context workspace ID used
                to return folder hierarchy from that workspace's root.

        Returns:
            Managed Content Space Folder Detail dict.
        """
        folder_id = self._ensure_18(folder_id)
        params: dict[str, Any] = {}
        if context_content_space_id is not None:
            params["contextContentSpaceId"] = self._ensure_18(
                context_content_space_id
            )
        return await self._get(
            f"cms/folders/{folder_id}", params=params or None
        )


class CMSWorkspacesOperations(ConnectBaseOperations):
    """Wrapper for enhanced CMS workspace authoring and management endpoints.

    These resources require enhanced CMS workspaces.  They cover channel
    CRUD, collection and delivery lookups, content creation, publish /
    unpublish, variants, cloning, taxonomy term associations, DAM
    providers, folder sharing, item search, and spaces.

    All methods are async.
    """

    # ------------------------------------------------------------------
    # Channels
    # ------------------------------------------------------------------

    async def list_channels(
        self,
        *,
        page: int | None = None,
        page_size: int = 25,
        show_details: bool | None = None,
    ) -> dict[str, Any]:
        """Get managed content channels.

        Args:
            page: Zero-based page number.
            page_size: Items per page (1–250).
            show_details: Whether to return detailed channel info.

        Returns:
            Managed Content Channels dict.
        """
        params: dict[str, Any] = {"pageSize": page_size}
        if page is not None:
            params["page"] = page
        if show_details is not None:
            params["showDetails"] = show_details
        return await self._get("cms/channels", params=params)

    async def create_channel(
        self,
        name: str,
        target_id: str,
        channel_type: str,
        *,
        cache_control_max_age: int | None = None,
        domain: str | None = None,
        is_dedicated_content_delivery: bool | None = None,
        is_domain_locked: bool | None = None,
        is_searchable: bool | None = None,
        media_cache_control_max_age: int | None = None,
    ) -> dict[str, Any]:
        """Create a managed content channel.

        Args:
            name: Channel name.
            target_id: ID of the target associated with the channel.
            channel_type: Channel type, e.g. ``"Community"`` or ``"Public"``.
            cache_control_max_age: Cache-Control max-age (seconds).
            domain: Domain ID or name for public channels.
            is_dedicated_content_delivery: Whether off-core dedicated
                content delivery is enabled (Hyperforce-only; 63.0+).
            is_domain_locked: Whether the domain is locked.
            is_searchable: Whether text contents are searchable.
            media_cache_control_max_age: Media Cache-Control max-age.

        Returns:
            Managed Content Channel dict.
        """
        target_id = self._ensure_18(target_id)
        payload: dict[str, Any] = {
            "name": name,
            "targetId": target_id,
            "type": channel_type,
        }
        if cache_control_max_age is not None:
            payload["cacheControlMaxAge"] = cache_control_max_age
        if domain is not None:
            payload["domain"] = domain
        if is_dedicated_content_delivery is not None:
            payload["isDedicatedContentDelivery"] = is_dedicated_content_delivery
        if is_domain_locked is not None:
            payload["isDomainLocked"] = is_domain_locked
        if is_searchable is not None:
            payload["isSearchable"] = is_searchable
        if media_cache_control_max_age is not None:
            payload["mediaCacheControlMaxAge"] = media_cache_control_max_age
        return await self._post("cms/channels", json=payload)

    async def get_channel(self, channel_id: str) -> dict[str, Any]:
        """Get a managed content channel.

        Args:
            channel_id: Channel ID (15 or 18 characters).

        Returns:
            Managed Content Channel dict.
        """
        channel_id = self._ensure_18(channel_id)
        return await self._get(f"cms/channels/{channel_id}")

    async def update_channel(
        self,
        channel_id: str,
        *,
        name: str | None = None,
        cache_control_max_age: int | None = None,
        domain: str | None = None,
        is_dedicated_content_delivery: bool | None = None,
        is_domain_locked: bool | None = None,
        is_searchable: bool | None = None,
        media_cache_control_max_age: int | None = None,
    ) -> dict[str, Any]:
        """Update a managed content channel.

        Args:
            channel_id: Channel ID (15 or 18 characters).
            name: Updated channel name.
            cache_control_max_age: Cache-Control max-age (seconds).
            domain: Domain ID or name for public channels.
            is_dedicated_content_delivery: Whether off-core dedicated
                content delivery is enabled.
            is_domain_locked: Whether the domain is locked.
            is_searchable: Whether text contents are searchable.
            media_cache_control_max_age: Media Cache-Control max-age.

        Returns:
            Updated Managed Content Channel dict.
        """
        channel_id = self._ensure_18(channel_id)
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if cache_control_max_age is not None:
            payload["cacheControlMaxAge"] = cache_control_max_age
        if domain is not None:
            payload["domain"] = domain
        if is_dedicated_content_delivery is not None:
            payload["isDedicatedContentDelivery"] = is_dedicated_content_delivery
        if is_domain_locked is not None:
            payload["isDomainLocked"] = is_domain_locked
        if is_searchable is not None:
            payload["isSearchable"] = is_searchable
        if media_cache_control_max_age is not None:
            payload["mediaCacheControlMaxAge"] = media_cache_control_max_age
        return await self._patch(f"cms/channels/{channel_id}", json=payload)

    async def delete_channel(self, channel_id: str) -> dict[str, Any]:
        """Delete a managed content channel.

        Args:
            channel_id: Channel ID (15 or 18 characters).

        Returns:
            Empty dict on success.
        """
        channel_id = self._ensure_18(channel_id)
        return await self._delete(f"cms/channels/{channel_id}")

    # ------------------------------------------------------------------
    # Channel collections / delivery contents (enhanced workspaces)
    # ------------------------------------------------------------------

    async def get_collection(
        self,
        collection_key_or_id: str,
        *,
        channel_id: str | None = None,
        site_id: str | None = None,
    ) -> dict[str, Any]:
        """Get collection items for a channel or Experience Cloud site.

        Pass exactly one of ``channel_id`` or ``site_id``.

        Args:
            collection_key_or_id: Collection key (UUID) or ID.
            channel_id: Managed content channel ID.
            site_id: Experience Cloud site ID.

        Returns:
            Collection items dict.
        """
        base = self._delivery_base(channel_id=channel_id, site_id=site_id)
        return await self._get(f"{base}/collections/{collection_key_or_id}")

    async def get_delivery_contents(
        self,
        *,
        channel_id: str | None = None,
        site_id: str | None = None,
        content_keys: list[str] | None = None,
        content_type_fqn: str | None = None,
        expand_references: bool | None = None,
        include_content_body: bool | None = None,
        language: str | None = None,
        managed_content_ids: list[str] | None = None,
        page: int | None = None,
        page_size: int = 25,
        publish_end_date: str | None = None,
        publish_start_date: str | None = None,
        reference_depth: int | None = None,
        references_as_list: bool | None = None,
        show_absolute_url: bool | None = None,
    ) -> dict[str, Any]:
        """Get a collection of published contents for a channel or site.

        Pass exactly one of ``channel_id`` or ``site_id``.

        Args:
            channel_id: Managed content channel ID.
            site_id: Experience Cloud site ID.
            content_keys: Up to 50 content keys.
            content_type_fqn: Fully qualified name of the content type.
            expand_references: Whether to expand reference details.
            include_content_body: Whether to return the content body.
            language: Language locale.
            managed_content_ids: Up to 100 managed content IDs.
            page: Zero-based page number.
            page_size: Items per page (1–250; capped at 25 when bodies
                or expanded references are requested).
            publish_end_date: ISO 8601 publish end date.
            publish_start_date: ISO 8601 publish start date.
            reference_depth: Reference depth (0–3).
            references_as_list: Whether references are returned as a list.
            show_absolute_url: Whether to return absolute URLs.

        Returns:
            Managed Content Delivery Document Collection dict.
        """
        base = self._delivery_base(channel_id=channel_id, site_id=site_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if content_keys:
            params["contentKeys"] = ",".join(content_keys)
        if content_type_fqn is not None:
            params["contentTypeFQN"] = content_type_fqn
        if expand_references is not None:
            params["expandReferences"] = expand_references
        if include_content_body is not None:
            params["includeContentBody"] = include_content_body
        if language is not None:
            params["language"] = language
        if managed_content_ids:
            params["managedContentIds"] = ",".join(
                self._ensure_18_list(managed_content_ids)
            )
        if page is not None:
            params["page"] = page
        if publish_end_date is not None:
            params["publishEndDate"] = publish_end_date
        if publish_start_date is not None:
            params["publishStartDate"] = publish_start_date
        if reference_depth is not None:
            params["referenceDepth"] = reference_depth
        if references_as_list is not None:
            params["referencesAsList"] = references_as_list
        if show_absolute_url is not None:
            params["showAbsoluteUrl"] = show_absolute_url
        return await self._get(f"{base}/contents", params=params)

    async def get_delivery_content(
        self,
        content_key_or_id: str,
        *,
        channel_id: str | None = None,
        site_id: str | None = None,
        expand_references: bool | None = None,
        language: str | None = None,
        reference_depth: int | None = None,
        references_as_list: bool | None = None,
        show_absolute_url: bool | None = None,
    ) -> dict[str, Any]:
        """Get a piece of published content for a channel or site.

        Pass exactly one of ``channel_id`` or ``site_id``.

        Args:
            content_key_or_id: Content key (UUID) or managed content ID.
            channel_id: Managed content channel ID.
            site_id: Experience Cloud site ID.
            expand_references: Whether to expand reference details.
            language: Language locale.
            reference_depth: Reference depth (0–3).
            references_as_list: Whether references are returned as a list.
            show_absolute_url: For public channels, whether to return
                the absolute unauthenticated URL.

        Returns:
            Managed Content Delivery Document dict.
        """
        base = self._delivery_base(channel_id=channel_id, site_id=site_id)
        params: dict[str, Any] = {}
        if expand_references is not None:
            params["expandReferences"] = expand_references
        if language is not None:
            params["language"] = language
        if reference_depth is not None:
            params["referenceDepth"] = reference_depth
        if references_as_list is not None:
            params["referencesAsList"] = references_as_list
        if show_absolute_url is not None:
            params["showAbsoluteUrl"] = show_absolute_url
        return await self._get(
            f"{base}/contents/{content_key_or_id}", params=params or None
        )

    async def enhanced_search(
        self,
        query_term: str,
        *,
        channel_id: str | None = None,
        site_id: str | None = None,
        filters: dict[str, Any] | None = None,
        page: int | None = None,
        page_size: int = 25,
    ) -> dict[str, Any]:
        """Search for content in a channel or Experience Cloud site.

        Pass exactly one of ``channel_id`` or ``site_id``.

        Args:
            query_term: Search term.
            channel_id: Managed content channel ID.
            site_id: Experience Cloud site ID.
            filters: Managed Content Delivery Search Filters dict (e.g.
                ``{"taxonomyQuery": {...}, "language": "en_US",
                "contentTypeFQNs": ["sfdc_cms__news"]}``).
            page: Zero-based page number.
            page_size: Items per page (1–250).

        Returns:
            Managed Content Delivery Search Result Collection dict.
        """
        base = self._delivery_base(channel_id=channel_id, site_id=site_id)
        payload: dict[str, Any] = {"queryTerm": query_term, "pageSize": page_size}
        if filters is not None:
            payload["filters"] = filters
        if page is not None:
            payload["page"] = page
        return await self._post(f"{base}/contents/enhanced-search", json=payload)

    # ------------------------------------------------------------------
    # Search indexes
    # ------------------------------------------------------------------

    async def get_search_indexes(self, channel_id: str) -> dict[str, Any]:
        """Get the latest live and non-live search indexes for a channel.

        Args:
            channel_id: Managed content channel ID (15 or 18 characters).

        Returns:
            Managed Content Search Index Collection dict.
        """
        channel_id = self._ensure_18(channel_id)
        return await self._get(f"cms/channels/{channel_id}/search/indexes")

    async def trigger_search_indexing(
        self,
        channel_id: str,
        *,
        is_incremental: bool | None = None,
        fallback_to_full_index: bool | None = None,
    ) -> dict[str, Any]:
        """Trigger incremental or full search indexing for a channel.

        Args:
            channel_id: Managed content channel ID (15 or 18 characters).
            is_incremental: Whether to perform an incremental index.
            fallback_to_full_index: Whether to fall back to a full index
                when incremental isn't possible.  Only applies when
                ``is_incremental`` is true.

        Returns:
            Managed Content Search Index dict.
        """
        channel_id = self._ensure_18(channel_id)
        params: dict[str, Any] = {}
        if is_incremental is not None:
            params["isIncremental"] = is_incremental
        if fallback_to_full_index is not None:
            params["fallbackToFullIndex"] = fallback_to_full_index
        return await self._post(
            f"cms/channels/{channel_id}/search/indexes", params=params or None
        )

    # ------------------------------------------------------------------
    # Contents
    # ------------------------------------------------------------------

    async def create_content(
        self,
        content_space_or_folder_id: str,
        title: str,
        content_type: str,
        content_body: dict[str, Any],
        *,
        api_name: str | None = None,
        content_key: str | None = None,
        external_id: str | None = None,
        url_name: str | None = None,
    ) -> dict[str, Any]:
        """Create a piece of managed content.

        Args:
            content_space_or_folder_id: Content space or folder ID.
            title: Managed content title.
            content_type: Fully qualified name of the content type.
            content_body: Managed content body map.
            api_name: API name (61.0+).
            content_key: Content key UUID (56.0+).
            external_id: External ID (58.0+).
            url_name: URL name.

        Returns:
            Managed Content Document dict.
        """
        content_space_or_folder_id = self._ensure_18(content_space_or_folder_id)
        payload: dict[str, Any] = {
            "contentSpaceOrFolderId": content_space_or_folder_id,
            "title": title,
            "contentType": content_type,
            "contentBody": content_body,
        }
        if api_name is not None:
            payload["apiName"] = api_name
        if content_key is not None:
            payload["contentKey"] = content_key
        if external_id is not None:
            payload["externalId"] = external_id
        if url_name is not None:
            payload["urlName"] = url_name
        return await self._post("cms/contents", json=payload)

    async def clone_content(
        self,
        content_key_or_id: str,
        *,
        api_name: str | None = None,
        content_space_or_folder_id: str | None = None,
        include_variants: bool | None = None,
        title: str | None = None,
    ) -> dict[str, Any]:
        """Clone a piece of managed content.

        Args:
            content_key_or_id: Content key (UUID) or managed content ID.
            api_name: API name of the clone.
            content_space_or_folder_id: Target folder/space for the clone.
            include_variants: Whether to clone variants too.
            title: Title of the clone.

        Returns:
            Managed Content Document Clone dict.
        """
        payload: dict[str, Any] = {}
        if api_name is not None:
            payload["apiName"] = api_name
        if content_space_or_folder_id is not None:
            payload["contentSpaceOrFolderId"] = self._ensure_18(
                content_space_or_folder_id
            )
        if include_variants is not None:
            payload["includeVariants"] = include_variants
        if title is not None:
            payload["title"] = title
        return await self._post(
            f"cms/contents/{content_key_or_id}/clone", json=payload
        )

    async def get_content_taxonomy_terms(
        self, content_key_or_id: str
    ) -> dict[str, Any]:
        """Get taxonomy terms associated with managed content.

        Args:
            content_key_or_id: Content key (UUID) or managed content ID.

        Returns:
            Managed Content Taxonomy Term Collection dict.
        """
        return await self._get(
            f"cms/contents/{content_key_or_id}/taxonomy-terms"
        )

    async def update_content_taxonomy_terms(
        self,
        content_key_or_id: str,
        *,
        terms_to_add: list[str] | None = None,
        terms_to_remove: list[str] | None = None,
        publish: bool | None = None,
    ) -> dict[str, Any]:
        """Add or remove taxonomy term associations from managed content.

        Args:
            content_key_or_id: Content key (UUID) or managed content ID.
            terms_to_add: Taxonomy term IDs to associate.
            terms_to_remove: Taxonomy term IDs to disassociate.
            publish: Whether to publish the taxonomy changes immediately.

        Returns:
            Managed Content Taxonomy Term Collection dict.
        """
        payload: dict[str, Any] = {}
        if terms_to_add is not None:
            payload["termsToAdd"] = self._ensure_18_list(terms_to_add)
        if terms_to_remove is not None:
            payload["termsToRemove"] = self._ensure_18_list(terms_to_remove)
        params: dict[str, Any] = {}
        if publish is not None:
            params["publish"] = publish
        return await self._patch(
            f"cms/contents/{content_key_or_id}/taxonomy-terms",
            json=payload,
            params=params or None,
        )

    async def publish_contents(
        self,
        *,
        content_ids: list[str] | None = None,
        variant_ids: list[str] | None = None,
        context_content_space_id: str | None = None,
        description: str | None = None,
        include_content_references: bool | None = None,
    ) -> dict[str, Any]:
        """Publish managed content.

        Pass either ``content_ids`` or ``variant_ids`` (or both, where
        allowed by the API).

        Args:
            content_ids: Managed content IDs to publish (all variants).
            variant_ids: Variant IDs to publish (same content space).
            context_content_space_id: Context workspace ID.
            description: Description for the publish action.
            include_content_references: Whether to include references.

        Returns:
            Managed Content Publish dict.
        """
        payload: dict[str, Any] = {}
        if content_ids is not None:
            payload["contentIds"] = self._ensure_18_list(content_ids)
        if variant_ids is not None:
            payload["variantIds"] = self._ensure_18_list(variant_ids)
        if context_content_space_id is not None:
            payload["contextContentSpaceId"] = self._ensure_18(
                context_content_space_id
            )
        if description is not None:
            payload["description"] = description
        if include_content_references is not None:
            payload["includeContentReferences"] = include_content_references
        return await self._post("cms/contents/publish", json=payload)

    async def unpublish_contents(
        self,
        *,
        content_ids: list[str] | None = None,
        variant_ids: list[str] | None = None,
        context_content_space_id: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Unpublish managed content.

        Args:
            content_ids: Managed content IDs to unpublish (all variants).
            variant_ids: Variant IDs to unpublish (same content space).
            context_content_space_id: Context workspace ID.
            description: Description for the unpublish action.

        Returns:
            Managed Content Unpublish dict.
        """
        payload: dict[str, Any] = {}
        if content_ids is not None:
            payload["contentIds"] = self._ensure_18_list(content_ids)
        if variant_ids is not None:
            payload["variantIds"] = self._ensure_18_list(variant_ids)
        if context_content_space_id is not None:
            payload["contextContentSpaceId"] = self._ensure_18(
                context_content_space_id
            )
        if description is not None:
            payload["description"] = description
        return await self._post("cms/contents/unpublish", json=payload)

    # ------------------------------------------------------------------
    # Variants
    # ------------------------------------------------------------------

    async def create_variant(
        self,
        managed_content_key_or_id: str,
        language: str,
        content_body: dict[str, Any],
        *,
        title: str | None = None,
        url_name: str | None = None,
    ) -> dict[str, Any]:
        """Create a managed content variant.

        Args:
            managed_content_key_or_id: Content key (UUID) or ID of the
                source content.
            language: Variant language locale.
            content_body: Variant body map.
            title: Variant title.
            url_name: Variant URL name.

        Returns:
            Managed Content Variant dict.
        """
        payload: dict[str, Any] = {
            "managedContentKeyorId": managed_content_key_or_id,
            "language": language,
            "contentBody": content_body,
        }
        if title is not None:
            payload["title"] = title
        if url_name is not None:
            payload["urlName"] = url_name
        return await self._post("cms/contents/variants", json=payload)

    async def get_variant(self, variant_id: str) -> dict[str, Any]:
        """Get a managed content variant.

        Args:
            variant_id: Variant ID (15 or 18 characters).

        Returns:
            Managed Content Variant dict.
        """
        variant_id = self._ensure_18(variant_id)
        return await self._get(f"cms/contents/variants/{variant_id}")

    async def update_variant(
        self,
        variant_id: str,
        *,
        api_name: str | None = None,
        content_body: dict[str, Any] | None = None,
        title: str | None = None,
        url_name: str | None = None,
    ) -> dict[str, Any]:
        """Update a managed content variant.

        Args:
            variant_id: Variant ID (15 or 18 characters).
            api_name: API name of the variant (63.0+).
            content_body: Variant body map.
            title: Variant title.
            url_name: Variant URL name.

        Returns:
            Managed Content Variant dict.
        """
        variant_id = self._ensure_18(variant_id)
        payload: dict[str, Any] = {}
        if api_name is not None:
            payload["apiName"] = api_name
        if content_body is not None:
            payload["contentBody"] = content_body
        if title is not None:
            payload["title"] = title
        if url_name is not None:
            payload["urlName"] = url_name
        return await self._put(f"cms/contents/variants/{variant_id}", json=payload)

    async def delete_variant(self, variant_id: str) -> dict[str, Any]:
        """Delete a managed content variant.

        Args:
            variant_id: Variant ID (15 or 18 characters).

        Returns:
            Empty dict on success.
        """
        variant_id = self._ensure_18(variant_id)
        return await self._delete(f"cms/contents/variants/{variant_id}")

    # ------------------------------------------------------------------
    # Digital asset management providers
    # ------------------------------------------------------------------

    async def list_dam_providers(
        self,
        *,
        content_space_id: str | None = None,
    ) -> dict[str, Any]:
        """Get digital asset management (DAM) providers.

        Args:
            content_space_id: Managed content space ID (66.0+).

        Returns:
            Managed Content Provider Collection dict.
        """
        params: dict[str, Any] = {}
        if content_space_id is not None:
            params["contentSpaceId"] = self._ensure_18(content_space_id)
        return await self._get(
            "cms/digital-asset-management-providers", params=params or None
        )

    async def create_dam_provider(
        self,
        name: str,
        instance_key: str,
        is_default: bool,
        provider_lightning_component_id: str,
    ) -> dict[str, Any]:
        """Create a DAM provider instance.

        Args:
            name: Provider instance name.
            instance_key: Provider instance key.
            is_default: Whether the instance is the default.
            provider_lightning_component_id: Provider Lightning
                component ID.

        Returns:
            Managed Content Provider Instance dict.
        """
        payload: dict[str, Any] = {
            "name": name,
            "instanceKey": instance_key,
            "isDefault": is_default,
            "providerLightningComponentId": provider_lightning_component_id,
        }
        return await self._post(
            "cms/digital-asset-management-providers", json=payload
        )

    async def update_dam_provider(
        self,
        provider_instance_id: str,
        *,
        name: str | None = None,
        instance_key: str | None = None,
        is_default: bool | None = None,
    ) -> dict[str, Any]:
        """Update a DAM provider instance (66.0+).

        Args:
            provider_instance_id: DAM provider instance ID.
            name: Updated name.
            instance_key: Updated provider instance key.
            is_default: Whether the instance is the default.

        Returns:
            Managed Content Provider Instance dict.
        """
        provider_instance_id = self._ensure_18(provider_instance_id)
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if instance_key is not None:
            payload["instanceKey"] = instance_key
        if is_default is not None:
            payload["isDefault"] = is_default
        return await self._patch(
            f"cms/digital-asset-management-providers/{provider_instance_id}",
            json=payload,
        )

    async def delete_dam_provider(
        self, provider_instance_id: str
    ) -> dict[str, Any]:
        """Delete a DAM provider instance.

        A DAM provider instance in use can't be deleted; delete the
        associated content first.

        Args:
            provider_instance_id: DAM provider instance ID.

        Returns:
            Empty dict on success.
        """
        provider_instance_id = self._ensure_18(provider_instance_id)
        return await self._delete(
            f"cms/digital-asset-management-providers/{provider_instance_id}"
        )

    # ------------------------------------------------------------------
    # Folder shares
    # ------------------------------------------------------------------

    async def get_folder_shares(self, folder_id: str) -> dict[str, Any]:
        """Get the targets a managed content space folder is shared with.

        Args:
            folder_id: Managed content folder ID (15 or 18 characters).

        Returns:
            MCS Folder Share Collection dict.
        """
        folder_id = self._ensure_18(folder_id)
        return await self._get(f"cms/folders/{folder_id}/shares")

    async def update_folder_shares(
        self,
        folder_id: str,
        *,
        share_with: list[str] | None = None,
        unshare_with: list[str] | None = None,
    ) -> dict[str, Any]:
        """Update the targets a managed content space folder is shared with.

        Args:
            folder_id: Managed content folder ID (15 or 18 characters).
            share_with: Target (workspace root folder) IDs to share with.
            unshare_with: Target IDs to unshare with.

        Returns:
            MCS Folder Share Collection dict.
        """
        folder_id = self._ensure_18(folder_id)
        payload: dict[str, Any] = {}
        if share_with is not None:
            payload["shareWith"] = [
                {"targetId": self._ensure_18(tid)} for tid in share_with
            ]
        if unshare_with is not None:
            payload["unshareWith"] = self._ensure_18_list(unshare_with)
        return await self._patch(
            f"cms/folders/{folder_id}/shares", json=payload
        )

    async def get_folder_share_targets(self, folder_id: str) -> dict[str, Any]:
        """Get targets that a managed content space folder can be shared with.

        Args:
            folder_id: Managed content folder ID (15 or 18 characters).

        Returns:
            MCS Folder Share Target Collection dict.
        """
        folder_id = self._ensure_18(folder_id)
        return await self._get(f"cms/folders/{folder_id}/share-targets")

    # ------------------------------------------------------------------
    # Item search
    # ------------------------------------------------------------------

    async def search_items(
        self,
        content_space_or_folder_ids: str,
        query_term: str,
        *,
        content_type_fqn: str | None = None,
        languages: list[str] | None = None,
        page: int | None = None,
        page_size: int = 25,
        scope: str | None = None,
    ) -> dict[str, Any]:
        """Search for managed content items in spaces and folders.

        Args:
            content_space_or_folder_ids: Space (``0Zu``) or folder
                (``9Pu``) IDs.  In version 57.0, exactly one space is
                required and at most one folder within it.
            query_term: Up to 50 space-separated search terms; must
                contain at least two non-wildcard characters.
            content_type_fqn: Fully qualified content type name.
            languages: Up to 10 languages or ``"All"``.
            page: Zero-based page number.
            page_size: Items per page (1–250).
            scope: ``"All"`` (default) or ``"TitleOnly"``.  Can't be
                set when a folder ID is provided.

        Returns:
            Managed Content Search Result Items Collection dict.
        """
        params: dict[str, Any] = {
            "contentSpaceOrFolderIds": content_space_or_folder_ids,
            "queryTerm": query_term,
            "pageSize": page_size,
        }
        if content_type_fqn is not None:
            params["contentTypeFQN"] = content_type_fqn
        if languages:
            params["languages"] = ",".join(languages)
        if page is not None:
            params["page"] = page
        if scope is not None:
            params["scope"] = scope
        return await self._get("cms/items/search", params=params)

    # ------------------------------------------------------------------
    # Spaces
    # ------------------------------------------------------------------

    async def list_spaces(
        self,
        *,
        name_fragment: str | None = None,
        page: int | None = None,
        page_size: int = 25,
    ) -> dict[str, Any]:
        """Get managed content spaces.

        Args:
            name_fragment: Filter spaces whose name contains this value.
            page: Zero-based page number.
            page_size: Items per page (1–250).

        Returns:
            Managed Content Space Collection dict.
        """
        params: dict[str, Any] = {"pageSize": page_size}
        if name_fragment is not None:
            params["nameFragment"] = name_fragment
        if page is not None:
            params["page"] = page
        return await self._get("cms/spaces", params=params)

    async def create_space(
        self,
        name: str,
        *,
        api_name: str | None = None,
        default_language: str | None = None,
        description: str | None = None,
        space_type: str | None = None,
    ) -> dict[str, Any]:
        """Create a managed content space.

        Args:
            name: Space name.
            api_name: Space API name.
            default_language: Default language of the space.
            description: Space description.
            space_type: ``"Content"`` or ``"Marketing"``.

        Returns:
            Managed Content Space dict.
        """
        payload: dict[str, Any] = {"name": name}
        if api_name is not None:
            payload["apiName"] = api_name
        if default_language is not None:
            payload["defaultLanguage"] = default_language
        if description is not None:
            payload["description"] = description
        if space_type is not None:
            payload["spaceType"] = space_type
        return await self._post("cms/spaces", json=payload)

    async def get_space(self, content_space_id: str) -> dict[str, Any]:
        """Get a managed content space.

        Args:
            content_space_id: Content space ID (15 or 18 characters).

        Returns:
            Managed Content Space dict.
        """
        content_space_id = self._ensure_18(content_space_id)
        return await self._get(f"cms/spaces/{content_space_id}")

    async def update_space(
        self,
        content_space_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Update a managed content space.

        Args:
            content_space_id: Content space ID (15 or 18 characters).
            name: Updated name.
            description: Updated description.

        Returns:
            Managed Content Space dict.
        """
        content_space_id = self._ensure_18(content_space_id)
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        return await self._patch(f"cms/spaces/{content_space_id}", json=payload)

    async def get_space_channels(
        self,
        content_space_id: str,
        *,
        page: int | None = None,
        page_size: int = 25,
    ) -> dict[str, Any]:
        """Get channels for a managed content space.

        Args:
            content_space_id: Content space ID (15 or 18 characters).
            page: Zero-based page number.
            page_size: Items per page (1–250).

        Returns:
            Managed Content Space Channels dict.
        """
        content_space_id = self._ensure_18(content_space_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if page is not None:
            params["page"] = page
        return await self._get(
            f"cms/spaces/{content_space_id}/channels", params=params
        )

    async def update_space_channels(
        self,
        content_space_id: str,
        space_channels: list[dict[str, str]],
    ) -> dict[str, Any]:
        """Add or remove channels from a managed content space.

        Args:
            content_space_id: Content space ID (15 or 18 characters).
            space_channels: List of operations, each
                ``{"channelId": ..., "operation": "Add"|"Remove"}``.

        Returns:
            Managed Content Space Channels dict.
        """
        content_space_id = self._ensure_18(content_space_id)
        payload = {"spaceChannels": space_channels}
        return await self._patch(
            f"cms/spaces/{content_space_id}/channels", json=payload
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _delivery_base(
        self, *, channel_id: str | None, site_id: str | None
    ) -> str:
        if bool(channel_id) == bool(site_id):
            raise ValueError(
                "Pass exactly one of channel_id or site_id."
            )
        if channel_id is not None:
            return f"cms/delivery/channels/{self._ensure_18(channel_id)}"
        assert site_id is not None
        return f"sites/{self._ensure_18(site_id)}/cms/delivery"
