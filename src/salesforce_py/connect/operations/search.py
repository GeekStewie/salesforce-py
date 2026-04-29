"""Search Connect API operations (v63.0+)."""

from __future__ import annotations

from typing import Any

from salesforce_py.connect.base import ConnectBaseOperations


class SearchOperations(ConnectBaseOperations):
    """Wrapper for ``/connect/search/sobjects/...`` endpoints.

    Covers keyword search (result groups / per-object results) and
    Einstein-powered natural-language search answers.
    """

    # ------------------------------------------------------------------
    # Keyword search
    # ------------------------------------------------------------------

    async def search_result_groups(
        self,
        q: str,
        *,
        configuration_name: str | None = None,
        highlights: bool | None = None,
    ) -> dict[str, Any]:
        """Search objects using keywords and return result groups (v63.0+).

        Args:
            q: Query term (2+ characters).
            configuration_name: Search configuration name (from Search Manager).
            highlights: Generate text highlights. Default ``False``.

        Returns:
            Search Result Groups dict.
        """
        params: dict[str, Any] = {"q": q}
        if configuration_name is not None:
            params["configurationName"] = configuration_name
        if highlights is not None:
            params["highlights"] = str(highlights).lower()
        return await self._get("search/sobjects/result-groups", params=params)

    async def search_object_results(
        self,
        object_api_name: str,
        *,
        q: str,
        configuration_name: str | None = None,
        data_categories: list[dict[str, Any]] | None = None,
        display_fields: list[str] | None = None,
        filters: list[dict[str, Any]] | None = None,
        highlights: bool | None = None,
        offset: int | None = None,
        order_by: list[dict[str, Any]] | None = None,
        page_size: int | None = None,
        spellcheck: bool | None = None,
    ) -> dict[str, Any]:
        """Search a single object by keyword and return results (v63.0+).

        Args:
            object_api_name: API name of the object (e.g. ``"Knowledge__kav"``).
            q: Query term (2+ characters).
            configuration_name: Search configuration name.
            data_categories: List of data category filters.
            display_fields: Fields to return. Defaults to search-layout fields.
            filters: List of filter inputs.
            highlights: Generate text highlights. Default ``False``.
            offset: Page offset (default ``0``).
            order_by: Ordering list.
            page_size: Results per page, 1–1999. Default ``20``.
            spellcheck: Apply spellcheck (default ``True``).

        Returns:
            Scoped Search Results dict.
        """
        payload: dict[str, Any] = {"q": q}
        if configuration_name is not None:
            payload["configurationName"] = configuration_name
        if data_categories is not None:
            payload["dataCategories"] = data_categories
        if display_fields is not None:
            payload["displayFields"] = display_fields
        if filters is not None:
            payload["filters"] = filters
        if highlights is not None:
            payload["highlights"] = highlights
        if offset is not None:
            payload["offset"] = offset
        if order_by is not None:
            payload["orderBy"] = order_by
        if page_size is not None:
            payload["pageSize"] = page_size
        if spellcheck is not None:
            payload["spellcheck"] = spellcheck
        return await self._post(
            f"search/sobjects/{object_api_name}/results", json=payload
        )

    # ------------------------------------------------------------------
    # Einstein answers (natural language)
    # ------------------------------------------------------------------

    async def search_answer(self, q: str) -> dict[str, Any]:
        """Search all objects via natural-language query for an answer (v63.0+).

        Requires Einstein Search answers to be enabled in the org.

        Args:
            q: Natural-language query.

        Returns:
            Search Answer dict.
        """
        return await self._get("search/sobjects/answer", params={"q": q})

    async def search_object_answer(
        self,
        object_api_name: str,
        *,
        q: str,
        display_fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Search a single object via natural-language query for an answer
        (v63.0+).

        Requires Einstein Search answers to be enabled in the org.

        Args:
            object_api_name: API name of the object.
            q: Natural-language query.
            display_fields: Fields to display. Defaults to the citation field.

        Returns:
            Search Answer dict.
        """
        params: dict[str, Any] = {"q": q}
        if display_fields is not None:
            params["displayFields"] = ",".join(display_fields)
        return await self._get(
            f"search/sobjects/{object_api_name}/answer", params=params
        )
