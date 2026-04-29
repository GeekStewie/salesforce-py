"""Agentforce Data Libraries Connect API operations (Beta)."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class AgentforceDataLibrariesOperations(ConnectBaseOperations):
    """Wrapper for ``/einstein/data-libraries`` endpoints (Beta).

    Covers listing, creating, retrieving, updating, and deleting data
    libraries, plus file-upload-url generation, adding files, triggering
    indexing, checking status, and checking upload readiness.
    All methods are async.
    """

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _lib_path(library_id: str) -> str:
        return f"data-libraries/{library_id}"

    # ------------------------------------------------------------------
    # Collection  /einstein/data-libraries
    # ------------------------------------------------------------------

    async def list_libraries(
        self,
        *,
        source_type: str | None = None,
    ) -> dict[str, Any]:
        """Return all AI grounding libraries available to the current user.

        Args:
            source_type: Optional filter — ``"SFDRIVE"``, ``"KNOWLEDGE"``,
                or ``"RETRIEVER"``. If omitted, all libraries are returned.

        Returns:
            LibraryListOutputRepresentation with ``libraries`` and
            ``totalSize`` keys.
        """
        params: dict[str, Any] = {}
        if source_type is not None:
            params["sourceType"] = source_type
        return await self._get("data-libraries", params=params)

    async def create_library(
        self,
        master_label: str,
        developer_name: str,
        *,
        description: str | None = None,
        data_space_scope_id: str | None = None,
        grounding_source: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create an AI Grounding Library.

        Only ``SFDRIVE`` (file-based) libraries are currently supported.
        After creation, poll :meth:`get_upload_readiness` until
        ``ready=True``, upload files to the presigned URLs, then call
        :meth:`start_indexing`.

        Args:
            master_label: Human-readable label (max 80 characters).
            developer_name: Unique API name (max 80; ``^[a-zA-Z][a-zA-Z0-9_]*$``).
            description: Optional description (max 255 characters).
            data_space_scope_id: DataSpaceScope ID; defaults to the org's
                default dataspace if omitted.
            grounding_source: Optional GroundingSourceInputRepresentation dict.

        Returns:
            LibraryOutputRepresentation dict (HTTP 201).
        """
        payload: dict[str, Any] = {
            "masterLabel": master_label,
            "developerName": developer_name,
        }
        if description is not None:
            payload["description"] = description
        if data_space_scope_id is not None:
            payload["dataSpaceScopeId"] = data_space_scope_id
        if grounding_source is not None:
            payload["groundingSource"] = grounding_source
        return await self._post("data-libraries", json=payload)

    # ------------------------------------------------------------------
    # Instance  /einstein/data-libraries/{libraryId}
    # ------------------------------------------------------------------

    async def get_library(self, library_id: str) -> dict[str, Any]:
        """Get full details for a single data library.

        Args:
            library_id: 18-character library ID (prefix ``1JD``).

        Returns:
            LibraryOutputRepresentation dict.
        """
        return await self._get(self._lib_path(library_id))

    async def update_library(
        self,
        library_id: str,
        *,
        master_label: str | None = None,
        description: str | None = None,
        grounding_source: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Update an existing SFDRIVE data library.

        Only ``masterLabel`` and ``description`` can be updated without
        re-provisioning. Attempting to update a KNOWLEDGE or RETRIEVER
        library returns 400.

        Args:
            library_id: 18-character library ID (prefix ``1JD``).
            master_label: Updated master label (max 80 characters).
            description: Updated description (max 255 characters).
            grounding_source: Optional GroundingSourceInputRepresentation dict.

        Returns:
            Updated LibraryOutputRepresentation dict.
        """
        payload: dict[str, Any] = {}
        if master_label is not None:
            payload["masterLabel"] = master_label
        if description is not None:
            payload["description"] = description
        if grounding_source is not None:
            payload["groundingSource"] = grounding_source
        return await self._patch(self._lib_path(library_id), json=payload)

    async def delete_library(self, library_id: str) -> dict[str, Any]:
        """Delete a data library and all associated entities.

        Cannot delete a library that is currently in use by an agent (400).

        Args:
            library_id: 18-character library ID (prefix ``1JD``).

        Returns:
            Empty dict on success (HTTP 204).
        """
        return await self._delete(self._lib_path(library_id))

    # ------------------------------------------------------------------
    # File upload URLs  /einstein/data-libraries/{libraryId}/file-upload-urls
    # ------------------------------------------------------------------

    async def get_file_upload_urls(
        self,
        library_id: str,
        file_names: list[str],
    ) -> dict[str, Any]:
        """Generate presigned S3 PUT URLs for uploading files to an SFDRIVE library.

        Call :meth:`get_upload_readiness` first and wait until ``ready=True``
        before calling this method.

        Args:
            library_id: 18-character library ID (prefix ``1JD``).
            file_names: List of file names with extensions (max 195 chars each).
                No more than 1000 files total per library.

        Returns:
            FileUploadUrlsCollectionOutputRepresentation with ``libraryId``
            and ``uploadUrls`` keys. Each URL entry includes ``fileName``,
            ``uploadUrl``, ``filePath``, and ``headers``.
        """
        payload = {"files": [{"fileName": fn} for fn in file_names]}
        return await self._post(f"{self._lib_path(library_id)}/file-upload-urls", json=payload)

    # ------------------------------------------------------------------
    # Add files  /einstein/data-libraries/{libraryId}/files
    # ------------------------------------------------------------------

    async def add_files(
        self,
        library_id: str,
        uploaded_files: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Register uploaded files with an SFDRIVE library.

        Each entry in *uploaded_files* must have ``filePath`` (returned by
        :meth:`get_file_upload_urls`) and ``fileSize`` (bytes). Duplicate
        file names and cross-library paths are rejected with 400.

        Args:
            library_id: 18-character library ID (prefix ``1JD``).
            uploaded_files: List of dicts with ``filePath`` and ``fileSize``.

        Returns:
            AddFilesOutputRepresentation with ``libraryId``,
            ``filesAccepted``, and ``groundingFileRefs`` keys.
        """
        payload = {"uploadedFiles": uploaded_files}
        return await self._post(f"{self._lib_path(library_id)}/files", json=payload)

    # ------------------------------------------------------------------
    # Indexing  /einstein/data-libraries/{libraryId}/indexing
    # ------------------------------------------------------------------

    async def start_indexing(
        self,
        library_id: str,
        uploaded_files: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Start asynchronous indexing of Data Cloud resources.

        For SFDRIVE libraries, *uploaded_files* is required and must list
        the files to index (``filePath`` and ``fileSize`` per entry). The
        library must be upload-ready; poll :meth:`get_upload_readiness`
        first. Poll :meth:`get_status` for progress after calling this.

        Args:
            library_id: 18-character library ID (prefix ``1JD``).
            uploaded_files: Required for SFDRIVE — list of dicts with
                ``filePath`` and ``fileSize``.

        Returns:
            ProvisionOutputRepresentation with ``libraryId``, ``sourceType``,
            ``status``, and ``message`` keys (plus ``filesAccepted`` for
            SFDRIVE libraries).
        """
        payload: dict[str, Any] = {}
        if uploaded_files is not None:
            payload["uploadedFiles"] = uploaded_files
        return await self._post(f"{self._lib_path(library_id)}/indexing", json=payload)

    # ------------------------------------------------------------------
    # Status  /einstein/data-libraries/{libraryId}/status
    # ------------------------------------------------------------------

    async def get_status(self, library_id: str) -> dict[str, Any]:
        """Return current library status with per-stage detail.

        Poll this endpoint after :meth:`start_indexing`. Suggested interval:
        5–30 seconds. Status values: ``READY``, ``IN_PROGRESS``, ``FAILED``,
        ``INCOMPLETE``, ``UNKNOWN``, ``NO_SOURCES``.

        Args:
            library_id: 18-character library ID (prefix ``1JD``).

        Returns:
            LibraryStatusOutputRepresentation with an ``indexingStatus``
            key containing ``libraryId``, ``status``, ``currentStage``,
            ``stages``, and ``lastUpdatedAt``.
        """
        return await self._get(f"{self._lib_path(library_id)}/status")

    # ------------------------------------------------------------------
    # Upload readiness  /einstein/data-libraries/{libraryId}/upload-readiness
    # ------------------------------------------------------------------

    async def get_upload_readiness(
        self,
        library_id: str,
        *,
        wait_max_time: int | None = None,
    ) -> dict[str, Any]:
        """Check whether the UDLO is ACTIVE and ready for file uploads.

        With *wait_max_time* omitted or ``0``, performs one immediate check.
        With a positive value (1–120000 ms), the server polls internally
        until ready or the timeout, reducing client-side polling loops.

        Args:
            library_id: 18-character library ID (prefix ``1JD``).
            wait_max_time: Maximum milliseconds for server-side polling
                (0–120000). Values outside that range return 400.

        Returns:
            UploadReadinessOutputRepresentation with ``libraryId``,
            ``ready``, ``sourceType``, and ``message`` keys.
        """
        params: dict[str, Any] = {}
        if wait_max_time is not None:
            params["waitMaxTime"] = wait_max_time
        return await self._get(f"{self._lib_path(library_id)}/upload-readiness", params=params)
