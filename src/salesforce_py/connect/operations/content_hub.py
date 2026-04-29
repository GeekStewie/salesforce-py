"""Files Connect Repository (Content Hub) Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class FilesConnectRepositoryOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/content-hub/...`` endpoints.

    A Files Connect repository is an external content repository
    (e.g. Google Drive, SharePoint Online, OneDrive for Business)
    connected to Salesforce.

    All resources also have a community-scoped variant:
    ``/connect/communities/{communityId}/content-hub/...``. Pass
    ``community_id`` to target that variant.
    """

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _prefix(self, community_id: str | None) -> str:
        if community_id is not None:
            return f"communities/{self._ensure_18(community_id)}/content-hub"
        return "content-hub"

    # ------------------------------------------------------------------
    # Repositories
    # ------------------------------------------------------------------

    async def list_repositories(
        self,
        *,
        community_id: str | None = None,
        can_browse_only: bool | None = None,
        can_search_only: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Get a list of Files Connect repositories (v32.0+).

        Args:
            community_id: Optional community ID for the site-scoped
                variant (v35.0+).
            can_browse_only: Only return repositories that support
                browsing.
            can_search_only: Only return repositories that support
                searching.
            page: Zero-based page number.
            page_size: 1–100 items per page (default 25).

        Returns:
            Files Connect Repository Collection dict.
        """
        params: dict[str, Any] = {}
        if can_browse_only is not None:
            params["canBrowseOnly"] = can_browse_only
        if can_search_only is not None:
            params["canSearchOnly"] = can_search_only
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["pageSize"] = page_size
        return await self._get(
            f"{self._prefix(community_id)}/repositories", params=params
        )

    async def get_repository(
        self, repository_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Get information about a Files Connect repository.

        Args:
            repository_id: Repository ID.
            community_id: Optional community ID.

        Returns:
            Files Connect Repository dict.
        """
        return await self._get(
            f"{self._prefix(community_id)}/repositories/{repository_id}"
        )

    async def get_repository_directory_entries(
        self, repository_id: str, *, community_id: str | None = None
    ) -> dict[str, Any]:
        """Get user/group directory entries of a repository (v35.0+).

        Args:
            repository_id: Repository ID.
            community_id: Optional community ID.

        Returns:
            Repository Directory Entry Collection dict.
        """
        return await self._get(
            f"{self._prefix(community_id)}/repositories/{repository_id}/directory-entries"
        )

    # ------------------------------------------------------------------
    # Repository files
    # ------------------------------------------------------------------

    async def get_repository_file(
        self,
        repository_id: str,
        repository_file_id: str,
        *,
        community_id: str | None = None,
        include_external_file_permissions_info: bool | None = None,
    ) -> dict[str, Any]:
        """Get information about a Files Connect repository file.

        Args:
            repository_id: Repository ID.
            repository_file_id: Repository file ID.
            community_id: Optional community ID.
            include_external_file_permissions_info: Include permission
                info (v36.0+, Google Drive/SharePoint/OneDrive only).

        Returns:
            Repository File Detail dict.
        """
        params: dict[str, Any] = {}
        if include_external_file_permissions_info is not None:
            params["includeExternalFilePermissionsInfo"] = (
                include_external_file_permissions_info
            )
        return await self._get(
            f"{self._prefix(community_id)}/repositories/{repository_id}"
            f"/files/{repository_file_id}",
            params=params,
        )

    async def update_repository_file(
        self,
        repository_id: str,
        repository_file_id: str,
        *,
        item_type_id: str,
        fields: list[dict[str, Any]],
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Update a Files Connect repository file (v35.0+).

        Args:
            repository_id: Repository ID.
            repository_file_id: Repository file ID.
            item_type_id: Item type ID from the allowed-item-types
                resource.
            fields: List of ``{"name": ..., "value": ...}`` entries.
            community_id: Optional community ID.

        Returns:
            Repository File Detail dict.
        """
        body = {"itemTypeId": item_type_id, "fields": fields}
        return await self._patch(
            f"{self._prefix(community_id)}/repositories/{repository_id}"
            f"/files/{repository_file_id}",
            json=body,
        )

    async def get_repository_file_content(
        self,
        repository_id: str,
        repository_file_id: str,
        *,
        community_id: str | None = None,
    ) -> bytes:
        """Stream the content of a repository file.

        Args:
            repository_id: Repository ID.
            repository_file_id: Repository file ID.
            community_id: Optional community ID.

        Returns:
            Raw file bytes.
        """
        return await self._get_bytes(
            f"{self._prefix(community_id)}/repositories/{repository_id}"
            f"/files/{repository_file_id}/content"
        )

    async def get_repository_file_previews(
        self,
        repository_id: str,
        repository_file_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get a file's supported previews (Google Drive only, v36.0+).

        Args:
            repository_id: Repository ID.
            repository_file_id: Repository file ID.
            community_id: Optional community ID.

        Returns:
            File Preview Collection dict.
        """
        return await self._get(
            f"{self._prefix(community_id)}/repositories/{repository_id}"
            f"/files/{repository_file_id}/previews"
        )

    async def get_repository_file_preview(
        self,
        repository_id: str,
        repository_file_id: str,
        format_type: str,
        *,
        community_id: str | None = None,
        start_page_number: int | None = None,
        end_page_number: int | None = None,
    ) -> dict[str, Any]:
        """Get a file preview or a specific page in a preview (v36.0+).

        Args:
            repository_id: Repository ID.
            repository_file_id: Repository file ID.
            format_type: ``jpg``, ``pdf``, ``svg``, ``thumbnail``,
                ``big-thumbnail``, or ``tiny-thumbnail``.
            community_id: Optional community ID.
            start_page_number: Starting page number.
            end_page_number: Ending page number.

        Returns:
            File Preview dict.
        """
        params: dict[str, Any] = {}
        if start_page_number is not None:
            params["startPageNumber"] = start_page_number
        if end_page_number is not None:
            params["endPageNumber"] = end_page_number
        return await self._get(
            f"{self._prefix(community_id)}/repositories/{repository_id}"
            f"/files/{repository_file_id}/previews/{format_type}",
            params=params,
        )

    # ------------------------------------------------------------------
    # Repository folders
    # ------------------------------------------------------------------

    async def get_repository_folder(
        self,
        repository_id: str,
        repository_folder_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get information about a repository folder (v38.0+).

        Args:
            repository_id: Repository ID.
            repository_folder_id: Repository folder ID.
            community_id: Optional community ID.

        Returns:
            Repository Folder Detail dict.
        """
        return await self._get(
            f"{self._prefix(community_id)}/repositories/{repository_id}"
            f"/folders/{repository_folder_id}"
        )

    async def get_allowed_item_types(
        self,
        repository_id: str,
        repository_folder_id: str,
        *,
        community_id: str | None = None,
        filter_type: str | None = None,
    ) -> dict[str, Any]:
        """Get item types allowed in a repository folder (v35.0+).

        Args:
            repository_id: Repository ID.
            repository_folder_id: Repository folder ID.
            community_id: Optional community ID.
            filter_type: ``Any``, ``FilesOnly``, or ``FoldersOnly``.

        Returns:
            Files Connect Allowed Item Type Collection dict.
        """
        params: dict[str, Any] = {}
        if filter_type is not None:
            params["filter"] = filter_type
        return await self._get(
            f"{self._prefix(community_id)}/repositories/{repository_id}"
            f"/folders/{repository_folder_id}/allowed-item-types",
            params=params,
        )

    async def get_repository_folder_items(
        self,
        repository_id: str,
        repository_folder_id: str,
        *,
        community_id: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """List the contents of a repository folder.

        Args:
            repository_id: Repository ID.
            repository_folder_id: Repository folder ID.
            community_id: Optional community ID.
            page: Zero-based page number.
            page_size: 1–100 items per page (default 25).

        Returns:
            Repository Folder Items Collection dict.
        """
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["pageSize"] = page_size
        return await self._get(
            f"{self._prefix(community_id)}/repositories/{repository_id}"
            f"/folders/{repository_folder_id}/items",
            params=params,
        )

    async def create_repository_folder_item(
        self,
        repository_id: str,
        repository_folder_id: str,
        *,
        item_type_id: str,
        fields: list[dict[str, Any]],
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a file in a repository folder metadata-only (v35.0+).

        For binary uploads, use a multipart/form-data request directly —
        this helper only sends the JSON metadata part.

        Args:
            repository_id: Repository ID.
            repository_folder_id: Repository folder ID.
            item_type_id: Item type ID from the allowed-item-types
                resource.
            fields: List of ``{"name": ..., "value": ...}`` entries.
            community_id: Optional community ID.

        Returns:
            Repository Folder Item dict.
        """
        body = {"itemTypeId": item_type_id, "fields": fields}
        return await self._post(
            f"{self._prefix(community_id)}/repositories/{repository_id}"
            f"/folders/{repository_folder_id}/items",
            json=body,
        )

    # ------------------------------------------------------------------
    # Item types and permissions
    # ------------------------------------------------------------------

    async def get_item_type(
        self,
        repository_id: str,
        repository_item_type_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get information about an item type (v35.0+).

        Args:
            repository_id: Repository ID.
            repository_item_type_id: Item type ID.
            community_id: Optional community ID.

        Returns:
            Files Connect Item Type Detail dict.
        """
        return await self._get(
            f"{self._prefix(community_id)}/repositories/{repository_id}"
            f"/item-types/{repository_item_type_id}"
        )

    async def get_item_permissions(
        self,
        repository_id: str,
        repository_item_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get permissions of a repository file (v35.0+).

        Args:
            repository_id: Repository ID.
            repository_item_id: File ID.
            community_id: Optional community ID.

        Returns:
            Files Connect Permission Collection dict.
        """
        return await self._get(
            f"{self._prefix(community_id)}/repositories/{repository_id}"
            f"/items/{repository_item_id}/permissions"
        )

    async def update_item_permissions(
        self,
        repository_id: str,
        repository_item_id: str,
        *,
        permissions_to_apply: list[dict[str, Any]] | None = None,
        permissions_to_remove: list[dict[str, Any]] | None = None,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Update permissions of a repository file (v35.0+).

        At least one of ``permissions_to_apply`` or
        ``permissions_to_remove`` is required.

        Args:
            repository_id: Repository ID.
            repository_item_id: File ID.
            permissions_to_apply: Permissions to add.
            permissions_to_remove: Permissions to remove.
            community_id: Optional community ID.

        Returns:
            Files Connect Permission Collection dict.

        Raises:
            ValueError: If neither list is supplied.
        """
        if permissions_to_apply is None and permissions_to_remove is None:
            raise ValueError(
                "Provide permissions_to_apply and/or permissions_to_remove."
            )
        body: dict[str, Any] = {}
        if permissions_to_apply is not None:
            body["permissionsToApply"] = permissions_to_apply
        if permissions_to_remove is not None:
            body["permissionsToRemove"] = permissions_to_remove
        return await self._patch(
            f"{self._prefix(community_id)}/repositories/{repository_id}"
            f"/items/{repository_item_id}/permissions",
            json=body,
        )

    async def get_permission_types(
        self,
        repository_id: str,
        repository_item_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get the permission types of a repository file (v35.0+).

        Args:
            repository_id: Repository ID.
            repository_item_id: File ID.
            community_id: Optional community ID.

        Returns:
            Repository Permission Type Collection dict.
        """
        return await self._get(
            f"{self._prefix(community_id)}/repositories/{repository_id}"
            f"/items/{repository_item_id}/permissions/types"
        )

    async def get_repository_for_item(
        self,
        repository_item_id: str,
        *,
        community_id: str | None = None,
    ) -> dict[str, Any]:
        """Get Files Connect repository info for a repository file (v38.0+).

        Args:
            repository_item_id: File ID.
            community_id: Optional community ID.

        Returns:
            Files Connect Repository dict.
        """
        return await self._get(
            f"{self._prefix(community_id)}/items/{repository_item_id}/repository"
        )
