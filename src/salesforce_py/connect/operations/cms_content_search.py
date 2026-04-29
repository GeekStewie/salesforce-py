"""Experience Cloud CMS Content Search Connect API operations."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class CMSContentSearchOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/sites/{siteId}/search`` endpoint.

    Search an Experience Cloud site with Enhanced CMS Workspaces. Only
    available for sites whose content has been indexed via the CMS
    Channel Search Indexes resource (v54.0+).
    """

    async def search(
        self,
        site_id: str,
        query_term: str,
        *,
        language: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> dict[str, Any]:
        """Search a site.

        Args:
            site_id: Site ID (15 or 18 characters).
            query_term: Whitespace-separated search terms (max 1024
                chars, 32 words).
            language: Language locale, e.g. ``en_US``.
            page_size: Items per page (1–240, default 25).
            page_token: Base64-encoded page token from a prior response.

        Returns:
            CMS Content Search Result dict.
        """
        site_id = self._ensure_18(site_id)
        params: dict[str, Any] = {"queryTerm": query_term}
        if language is not None:
            params["language"] = language
        if page_size is not None:
            params["pageSize"] = page_size
        if page_token is not None:
            params["pageToken"] = page_token
        return await self._get(f"sites/{site_id}/search", params=params)
