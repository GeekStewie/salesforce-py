"""Search — SOSL, parameterized search, suggestions, layouts, and scope.

Covers:

- ``/services/data/vXX.X/search/?q=sosl`` — SOSL search.
- ``/services/data/vXX.X/parameterizedSearch`` — Simple search using query
  params (GET) or complex search via body (POST).
- ``/services/data/vXX.X/search/scopeOrder`` — Ordered list of objects in the
  user's default global search scope.
- ``/services/data/vXX.X/search/suggestSearchQueries`` — Suggested searches
  based on user query text matching Knowledge searches.
- ``/services/data/vXX.X/search/suggestTitleMatches`` — Knowledge article
  titles that match the user's search query string.
- ``/services/data/vXX.X/searchlayout`` — Search result layout metadata.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.rest.base import RestBaseOperations


class SearchOperations(RestBaseOperations):
    """Wrapper for ``/search``, ``/parameterizedSearch``, ``/searchlayout``."""

    # ------------------------------------------------------------------
    # SOSL
    # ------------------------------------------------------------------

    async def search(self, sosl: str) -> dict[str, Any]:
        """Execute a SOSL search.

        Args:
            sosl: SOSL statement, e.g. ``FIND {Acme} IN ALL FIELDS RETURNING
                Account(Id, Name)``. The library handles URL encoding; pass
                the raw SOSL.
        """
        return await self._get("search", params={"q": sosl})

    # ------------------------------------------------------------------
    # Parameterized search
    # ------------------------------------------------------------------

    async def parameterized_search(self, **params: Any) -> dict[str, Any]:
        """Issue a simple parameterized search via GET.

        Args:
            **params: Salesforce-defined search parameters such as ``q``,
                ``sobject``, ``fields``, ``ids``, ``in``, ``overallLimit``,
                ``defaultLimit``, ``highlights``, etc. Pass them as keyword
                arguments and they will be sent as query parameters.
        """
        return await self._get("parameterizedSearch", params=params)

    async def parameterized_search_post(self, body: dict[str, Any]) -> dict[str, Any]:
        """Issue a complex parameterized search via POST.

        Args:
            body: The search request body. See the REST API Developer Guide
                for the full schema.
        """
        return await self._post("parameterizedSearch", json=body)

    # ------------------------------------------------------------------
    # Scope, suggestions, layouts
    # ------------------------------------------------------------------

    async def get_scope_order(self) -> list[dict[str, Any]]:
        """Return the ordered list of objects in the user's global search scope."""
        response = await self._get("search/scopeOrder")
        if isinstance(response, list):
            return response
        return response.get("scopeOrder", [])  # type: ignore[return-value]

    async def suggest_search_queries(
        self,
        *,
        q: str,
        language: str,
        channel: str | None = None,
        limit: int | None = None,
        publish_status: str | None = None,
    ) -> dict[str, Any]:
        """Return suggested searches for a user query.

        Args:
            q: The search text entered so far.
            language: Language of the query, e.g. ``"en_US"``.
            channel: Optional channel scope (``App``, ``Pkb``, ``Csp``,
                ``Prm``).
            limit: Maximum number of suggestions to return.
            publish_status: Knowledge article publish status (``Online``,
                ``Draft``, ``Archived``).
        """
        return await self._get(
            "search/suggestSearchQueries",
            params={
                "q": q,
                "language": language,
                "channel": channel,
                "limit": limit,
                "publishStatus": publish_status,
            },
        )

    async def suggest_title_matches(
        self,
        *,
        q: str,
        language: str,
        publish_status: str,
        channel: str | None = None,
        topic_id: str | None = None,
        data_category_group: str | None = None,
        data_category: str | None = None,
        article_types: list[str] | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Return Knowledge article titles matching the user's query string."""
        return await self._get(
            "search/suggestTitleMatches",
            params={
                "q": q,
                "language": language,
                "publishStatus": publish_status,
                "channel": channel,
                "topicId": topic_id,
                "dataCategoryGroupName": data_category_group,
                "dataCategoryName": data_category,
                "articleTypes": ",".join(article_types) if article_types else None,
                "limit": limit,
            },
        )

    async def get_search_layouts(self, sobjects: list[str]) -> dict[str, Any]:
        """Return search result layout metadata for one or more objects.

        Args:
            sobjects: List of sObject API names to describe.
        """
        return await self._get("searchlayout", params={"q": ",".join(sobjects)})
