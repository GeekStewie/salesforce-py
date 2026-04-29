"""Salesforce Files Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class FilesOperations(ConnectBaseOperations):
    """Wrapper for all Salesforce Files Connect API endpoints.

    Covers file CRUD, content/rendition streaming, asset files, folders,
    sharing, previews, batch operations, and filtered list views.
    All methods are async.
    """

    # ------------------------------------------------------------------
    # Single-file operations  /connect/files/<fileId>
    # ------------------------------------------------------------------

    async def get_file(self, file_id: str) -> dict[str, Any]:
        """Get metadata for a file, including references to external files.

        Args:
            file_id: Salesforce ContentDocument ID (15 or 18 characters).

        Returns:
            File metadata dict.
        """
        file_id = self._ensure_18(file_id)
        return await self._get(f"files/{file_id}")

    async def upload_new_version(
        self,
        file_id: str,
        filename: str,
        content: bytes,
        *,
        content_type: str = "application/octet-stream",
        description: str = "",
    ) -> dict[str, Any]:
        """Upload a new version of an existing file.

        Args:
            file_id: Salesforce ContentDocument ID (15 or 18 characters).
            filename: File name for the new version.
            content: Raw file bytes.
            content_type: MIME type of the file.
            description: Optional description for the new version.

        Returns:
            Updated file metadata dict.
        """
        file_id = self._ensure_18(file_id)
        data: dict[str, str] = {"title": filename}
        if description:
            data["description"] = description
        files = {"fileData": (filename, content, content_type)}
        return await self._post(f"files/{file_id}", data=data, files=files)

    async def update_file(
        self,
        file_id: str,
        *,
        title: str | None = None,
        folder_id: str | None = None,
    ) -> dict[str, Any]:
        """Rename a file or move it to a different folder.

        Args:
            file_id: Salesforce ContentDocument ID (15 or 18 characters).
            title: New file title.
            folder_id: ID of the destination folder (15 or 18 characters).

        Returns:
            Updated file metadata dict.
        """
        file_id = self._ensure_18(file_id)
        payload: dict[str, str] = {}
        if title is not None:
            payload["title"] = title
        if folder_id is not None:
            payload["folderId"] = self._ensure_18(folder_id)
        return await self._patch(f"files/{file_id}", json=payload)

    async def delete_file(self, file_id: str) -> dict[str, Any]:
        """Delete a file.

        Args:
            file_id: Salesforce ContentDocument ID (15 or 18 characters).

        Returns:
            Empty dict on success.
        """
        file_id = self._ensure_18(file_id)
        return await self._delete(f"files/{file_id}")

    # ------------------------------------------------------------------
    # File content  /connect/files/<fileId>/content
    # ------------------------------------------------------------------

    async def get_file_content(self, file_id: str) -> bytes:
        """Download the binary content of a file.

        Args:
            file_id: Salesforce ContentDocument ID (15 or 18 characters).

        Returns:
            Raw file bytes.
        """
        file_id = self._ensure_18(file_id)
        return await self._get_bytes(f"files/{file_id}/content")

    # ------------------------------------------------------------------
    # Rendition  /connect/files/<fileId>/rendition
    # ------------------------------------------------------------------

    async def get_file_rendition(
        self,
        file_id: str,
        *,
        rendition_type: str = "THUMB720BY480",
        page_number: int = 0,
    ) -> bytes:
        """Get a binary rendition (preview image) of a file.

        Args:
            file_id: Salesforce ContentDocument ID (15 or 18 characters).
            rendition_type: Rendition type string, e.g. ``"THUMB720BY480"``,
                ``"SVGZ"``, ``"PDF"``.
            page_number: Zero-based page number for multi-page documents.

        Returns:
            Raw rendition bytes.
        """
        file_id = self._ensure_18(file_id)
        params: dict[str, Any] = {
            "renditionType": rendition_type,
            "pageNumber": page_number,
        }
        return await self._get_bytes(f"files/{file_id}/rendition", params=params)

    # ------------------------------------------------------------------
    # Previews  /connect/files/<fileId>/previews
    # ------------------------------------------------------------------

    async def get_file_previews(self, file_id: str) -> dict[str, Any]:
        """Get information about a file's supported previews.

        Args:
            file_id: Salesforce ContentDocument ID (15 or 18 characters).

        Returns:
            Previews metadata dict.
        """
        file_id = self._ensure_18(file_id)
        return await self._get(f"files/{file_id}/previews")

    async def generate_file_previews(self, file_id: str, *, num_pages: int = 1) -> dict[str, Any]:
        """Request generation of up to 500 preview pages.

        Args:
            file_id: Salesforce ContentDocument ID (15 or 18 characters).
            num_pages: Number of pages to generate (max 500).

        Returns:
            Updated previews metadata dict.
        """
        file_id = self._ensure_18(file_id)
        return await self._patch(f"files/{file_id}/previews", json={"numPages": num_pages})

    async def get_file_preview_content(
        self, file_id: str, preview_format: str, *, page_number: int | None = None
    ) -> bytes:
        """Get preview content in a specific format.

        Args:
            file_id: Salesforce ContentDocument ID (15 or 18 characters).
            preview_format: Format string, e.g. ``"PNG"``, ``"SVG"``, ``"PDF"``.
            page_number: Specific zero-based page to fetch, or ``None`` for all.

        Returns:
            Raw preview bytes.
        """
        file_id = self._ensure_18(file_id)
        params: dict[str, Any] = {}
        if page_number is not None:
            params["pageNumber"] = page_number
        return await self._get_bytes(f"files/{file_id}/previews/{preview_format}", params=params)

    # ------------------------------------------------------------------
    # Image  /connect/files/<fileId>/image
    # ------------------------------------------------------------------

    async def get_file_image(self, file_id: str) -> dict[str, Any]:
        """Get information about a file image.

        Args:
            file_id: Salesforce ContentDocument ID (15 or 18 characters).

        Returns:
            Image metadata dict.
        """
        file_id = self._ensure_18(file_id)
        return await self._get(f"files/{file_id}/image")

    # ------------------------------------------------------------------
    # Sharing  /connect/files/<fileId>/file-shares
    # ------------------------------------------------------------------

    async def get_file_shares(self, file_id: str) -> dict[str, Any]:
        """Get users, groups, or records with which a file is shared.

        Args:
            file_id: Salesforce ContentDocument ID (15 or 18 characters).

        Returns:
            File shares page dict.
        """
        file_id = self._ensure_18(file_id)
        return await self._get(f"files/{file_id}/file-shares")

    async def share_file_with_users(
        self, file_id: str, user_ids: list[str], *, share_type: str = "V"
    ) -> dict[str, Any]:
        """Share a file with one or more users.

        Args:
            file_id: Salesforce ContentDocument ID (15 or 18 characters).
            user_ids: List of user IDs (15 or 18 characters each) to share with.
            share_type: Share type — ``"V"`` (viewer) or ``"C"`` (collaborator).

        Returns:
            Updated file shares dict.
        """
        file_id = self._ensure_18(file_id)
        user_ids = self._ensure_18_list(user_ids)
        payload = {"shares": [{"shareType": share_type, "sharedWithId": uid} for uid in user_ids]}
        return await self._post(f"files/{file_id}/file-shares", json=payload)

    # ------------------------------------------------------------------
    # Share link  /connect/files/<fileId>/file-shares/link
    # ------------------------------------------------------------------

    async def get_share_link(self, file_id: str) -> dict[str, Any]:
        """Get a file's share link.

        Args:
            file_id: Salesforce ContentDocument ID (15 or 18 characters).

        Returns:
            Share link dict.
        """
        file_id = self._ensure_18(file_id)
        return await self._get(f"files/{file_id}/file-shares/link")

    async def create_share_link(self, file_id: str) -> dict[str, Any]:
        """Create (or retrieve existing) share link for a file.

        Args:
            file_id: Salesforce ContentDocument ID (15 or 18 characters).

        Returns:
            Share link dict.
        """
        file_id = self._ensure_18(file_id)
        return await self._put(f"files/{file_id}/file-shares/link")

    async def delete_share_link(self, file_id: str) -> dict[str, Any]:
        """Delete a file's share link.

        Args:
            file_id: Salesforce ContentDocument ID (15 or 18 characters).

        Returns:
            Empty dict on success.
        """
        file_id = self._ensure_18(file_id)
        return await self._delete(f"files/{file_id}/file-shares/link")

    # ------------------------------------------------------------------
    # Batch  /connect/files/batch/<fileIds>
    # ------------------------------------------------------------------

    async def get_files_batch(self, file_ids: list[str]) -> dict[str, Any]:
        """Get metadata for up to 100 files in a single request.

        Args:
            file_ids: List of up to 100 ContentDocument IDs (15 or 18 characters).

        Returns:
            Batch result dict with a ``results`` list.
        """
        file_ids = self._ensure_18_list(file_ids)
        return await self._get(f"files/batch/{','.join(file_ids)}")

    async def delete_files_batch(self, file_ids: list[str]) -> dict[str, Any]:
        """Delete up to 100 files in a single request.

        Args:
            file_ids: List of up to 100 ContentDocument IDs (15 or 18 characters).

        Returns:
            Batch result dict.
        """
        file_ids = self._ensure_18_list(file_ids)
        return await self._delete(f"files/batch/{','.join(file_ids)}")

    # ------------------------------------------------------------------
    # User files  /connect/files/users/<userId>
    # ------------------------------------------------------------------

    async def list_files(
        self,
        user_id: str = "me",
        *,
        page_size: int = 25,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """List files owned by a user.

        Args:
            user_id: User ID (15 or 18 characters) or ``"me"``.
            page_size: Number of files to return per page.
            page_token: Opaque token from a previous call for pagination.

        Returns:
            Files page dict.
        """
        user_id = self._ensure_18(user_id)
        params: dict[str, Any] = {"pageSize": page_size}
        if page_token:
            params["pageToken"] = page_token
        return await self._get(f"files/users/{user_id}", params=params)

    async def upload_file(
        self,
        filename: str,
        content: bytes,
        *,
        user_id: str = "me",
        content_type: str = "application/octet-stream",
        description: str = "",
    ) -> dict[str, Any]:
        """Upload a new file to a user's Files home.

        Args:
            filename: File name to use in Salesforce.
            content: Raw file bytes.
            user_id: User ID (15 or 18 characters) or ``"me"``.
            content_type: MIME type of the file.
            description: Optional file description.

        Returns:
            Created file metadata dict.
        """
        user_id = self._ensure_18(user_id)
        data: dict[str, str] = {"title": filename}
        if description:
            data["description"] = description
        files = {"fileData": (filename, content, content_type)}
        return await self._post(f"files/users/{user_id}", data=data, files=files)

    async def list_files_shared_with_me(self, user_id: str = "me") -> dict[str, Any]:
        """List files that have been shared with a user.

        Args:
            user_id: User ID (15 or 18 characters) or ``"me"``.

        Returns:
            Files page dict.
        """
        user_id = self._ensure_18(user_id)
        return await self._get(f"files/users/{user_id}/filter/shared-with-me")

    async def list_files_in_my_groups(self, user_id: str = "me") -> dict[str, Any]:
        """List files posted to groups the user is a member of.

        Args:
            user_id: User ID (15 or 18 characters) or ``"me"``.

        Returns:
            Files page dict.
        """
        user_id = self._ensure_18(user_id)
        return await self._get(f"files/users/{user_id}/filter/groups")

    # ------------------------------------------------------------------
    # Asset files  /connect/files/<fileId>/asset
    # ------------------------------------------------------------------

    async def create_asset_file(self, file_id: str, asset_data: dict[str, Any]) -> dict[str, Any]:
        """Create an asset file from an existing file.

        Args:
            file_id: Salesforce ContentDocument ID (15 or 18 characters).
            asset_data: Asset creation payload (``name``, ``type``, etc.).

        Returns:
            Created asset metadata dict.
        """
        file_id = self._ensure_18(file_id)
        return await self._post(f"files/{file_id}/asset", json=asset_data)

    # ------------------------------------------------------------------
    # Asset files resource  /connect/file-assets/<assetId>
    # ------------------------------------------------------------------

    async def get_asset_file(self, asset_id: str) -> dict[str, Any]:
        """Get metadata for an asset file.

        Args:
            asset_id: Asset file ID (15 or 18 characters).

        Returns:
            Asset metadata dict.
        """
        asset_id = self._ensure_18(asset_id)
        return await self._get(f"file-assets/{asset_id}")

    async def update_asset_file(
        self, asset_id: str, *, guest_access: bool | None = None
    ) -> dict[str, Any]:
        """Change the visibility of an asset file for unauthenticated users.

        Args:
            asset_id: Asset file ID (15 or 18 characters).
            guest_access: ``True`` to allow unauthenticated access.

        Returns:
            Updated asset metadata dict.
        """
        asset_id = self._ensure_18(asset_id)
        payload: dict[str, Any] = {}
        if guest_access is not None:
            payload["guestAccess"] = guest_access
        return await self._patch(f"file-assets/{asset_id}", json=payload)

    async def get_asset_file_content(self, fully_qualified_name: str) -> bytes:
        """Stream the content of an asset file.

        Args:
            fully_qualified_name: Fully-qualified asset file name (not an SF ID).

        Returns:
            Raw asset file bytes.
        """
        return await self._get_bytes(f"file-assets/{fully_qualified_name}/content")

    async def get_asset_file_rendition(self, fully_qualified_name: str) -> bytes:
        """Get up to 25 streamed renditions of an asset file.

        Args:
            fully_qualified_name: Fully-qualified asset file name (not an SF ID).

        Returns:
            Raw rendition bytes.
        """
        return await self._get_bytes(f"file-assets/{fully_qualified_name}/rendition")

    async def get_asset_files_batch(self, asset_ids: list[str]) -> dict[str, Any]:
        """Get metadata for up to 100 asset files.

        Args:
            asset_ids: List of up to 100 asset file IDs (15 or 18 characters).

        Returns:
            Batch result dict.
        """
        asset_ids = self._ensure_18_list(asset_ids)
        return await self._get(f"file-assets/batch/{','.join(asset_ids)}")

    # ------------------------------------------------------------------
    # Folders  /connect/folders/<folderId>
    # ------------------------------------------------------------------

    async def get_folder(self, folder_id: str) -> dict[str, Any]:
        """Get metadata for a folder.

        Args:
            folder_id: Salesforce folder ID (15 or 18 characters).

        Returns:
            Folder metadata dict.
        """
        folder_id = self._ensure_18(folder_id)
        return await self._get(f"folders/{folder_id}")

    async def update_folder(
        self,
        folder_id: str,
        *,
        name: str | None = None,
        parent_folder_id: str | None = None,
    ) -> dict[str, Any]:
        """Rename or move a folder.

        Args:
            folder_id: Salesforce folder ID (15 or 18 characters).
            name: New folder name.
            parent_folder_id: Destination parent folder ID (15 or 18 characters).

        Returns:
            Updated folder metadata dict.
        """
        folder_id = self._ensure_18(folder_id)
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if parent_folder_id is not None:
            payload["parentFolderId"] = self._ensure_18(parent_folder_id)
        return await self._patch(f"folders/{folder_id}", json=payload)

    async def delete_folder(self, folder_id: str) -> dict[str, Any]:
        """Delete a folder.

        Args:
            folder_id: Salesforce folder ID (15 or 18 characters).

        Returns:
            Empty dict on success.
        """
        folder_id = self._ensure_18(folder_id)
        return await self._delete(f"folders/{folder_id}")

    async def list_folder_items(self, folder_id: str) -> dict[str, Any]:
        """List the contents of a folder.

        Args:
            folder_id: Salesforce folder ID (15 or 18 characters).

        Returns:
            Folder items dict.
        """
        folder_id = self._ensure_18(folder_id)
        return await self._get(f"folders/{folder_id}/items")

    async def add_file_to_folder(self, folder_id: str, file_id: str) -> dict[str, Any]:
        """Add a file to a folder.

        Args:
            folder_id: Salesforce folder ID (15 or 18 characters).
            file_id: Salesforce ContentDocument ID (15 or 18 characters).

        Returns:
            Updated folder items dict.
        """
        folder_id = self._ensure_18(folder_id)
        file_id = self._ensure_18(file_id)
        return await self._post(f"folders/{folder_id}/items", json={"id": file_id})

    async def create_folder(self, parent_folder_id: str, name: str) -> dict[str, Any]:
        """Create a new folder inside an existing folder.

        Args:
            parent_folder_id: ID of the parent folder (15 or 18 characters).
            name: Name for the new folder.

        Returns:
            Created folder metadata dict.
        """
        parent_folder_id = self._ensure_18(parent_folder_id)
        return await self._post(
            f"folders/{parent_folder_id}/items",
            json={"name": name, "type": "folder"},
        )

    # ------------------------------------------------------------------
    # Group files  /chatter/groups/<groupId>/files
    # ------------------------------------------------------------------

    async def list_group_files(self, group_id: str) -> dict[str, Any]:
        """List files posted to a Chatter group.

        Args:
            group_id: Salesforce Chatter group ID (15 or 18 characters).

        Returns:
            Files page dict.
        """
        group_id = self._ensure_18(group_id)
        return await self._get(f"chatter/groups/{group_id}/files")

    # ------------------------------------------------------------------
    # Topic files  /connect/topics/<topicId>/files
    # ------------------------------------------------------------------

    async def list_topic_files(self, topic_id: str) -> dict[str, Any]:
        """Get the five most recently posted files for a topic.

        Args:
            topic_id: Salesforce topic ID (15 or 18 characters).

        Returns:
            Files list dict.
        """
        topic_id = self._ensure_18(topic_id)
        return await self._get(f"topics/{topic_id}/files")
