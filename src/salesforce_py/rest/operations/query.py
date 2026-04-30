"""Query — SOQL query execution.

Covers:

- ``/services/data/vXX.X/query/?q=soql`` — Executes the specified SOQL query.
- ``/services/data/vXX.X/queryAll/?q=soql`` — Like query, but results include
  deleted, merged, and archived records.
- ``/services/data/vXX.X/query/{locator}`` — Pagination follow-up via
  ``nextRecordsUrl``.
- ``/services/data/vXX.X/async-queries`` — Async SOQL submission and polling.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.rest.base import RestBaseOperations


class QueryOperations(RestBaseOperations):
    """Wrapper for ``/query``, ``/queryAll``, and ``/async-queries`` endpoints."""

    # ------------------------------------------------------------------
    # Synchronous SOQL
    # ------------------------------------------------------------------

    async def query(self, soql: str) -> dict[str, Any]:
        """Execute a SOQL query.

        Args:
            soql: The SOQL query string. Large result sets are paginated via
                ``nextRecordsUrl`` — use :meth:`query_more` (or iterate with
                :meth:`query_all_records`) to drain the remaining pages.

        Returns:
            Response dict with ``totalSize``, ``done``, ``records``, and —
            when paginated — ``nextRecordsUrl``.
        """
        return await self._get("query", params={"q": soql})

    async def query_all(self, soql: str) -> dict[str, Any]:
        """Execute a SOQL query that also returns deleted/merged/archived records.

        Equivalent to :meth:`query` but hits ``/queryAll`` instead of
        ``/query``.
        """
        return await self._get("queryAll", params={"q": soql})

    async def query_more(self, next_records_url: str) -> dict[str, Any]:
        """Fetch the next page of records for a paginated query.

        Args:
            next_records_url: The ``nextRecordsUrl`` value from a previous
                :meth:`query` / :meth:`query_all` response — either the full
                path (``/services/data/v66.0/query/01gXX...``) or just the
                trailing locator (``query/01gXX...`` /
                ``queryAll/01gXX...``). Both are accepted.
        """
        path = self._strip_version_prefix(next_records_url)
        return await self._get(path)

    async def query_all_records(self, soql: str) -> list[dict[str, Any]]:
        """Execute a SOQL query and return every record across all pages.

        Convenience wrapper — issues :meth:`query` then drains every
        ``nextRecordsUrl`` page. Memory-eager; prefer the streaming pattern
        (``query`` + ``query_more`` loop) for huge result sets.
        """
        response = await self.query(soql)
        records = list(response.get("records", []))
        while not response.get("done", True) and response.get("nextRecordsUrl"):
            response = await self.query_more(response["nextRecordsUrl"])
            records.extend(response.get("records", []))
        return records

    # ------------------------------------------------------------------
    # Async SOQL (big-object, long-running queries)
    # ------------------------------------------------------------------

    async def submit_async_query(self, query_payload: dict[str, Any]) -> dict[str, Any]:
        """Submit a SOQL query for asynchronous processing.

        Async SOQL is designed for long-running queries — typically against
        Big Objects or event monitoring data. See the Connect REST API /
        Async Query docs for payload details.

        Args:
            query_payload: Query body — typically ``{"query": "SELECT ..."}``
                plus optional ``targetObject`` / ``targetFieldMap`` entries.
        """
        return await self._post("async-queries", json=query_payload)

    async def get_async_query(self, query_job_id: str) -> dict[str, Any]:
        """Fetch the status / results of an async SOQL job."""
        return await self._get(f"async-queries/{query_job_id}")

    async def list_async_queries(self) -> dict[str, Any]:
        """List recent async SOQL jobs for the context user."""
        return await self._get("async-queries")

    async def delete_async_query(self, query_job_id: str) -> dict[str, Any]:
        """Delete / cancel an async SOQL job."""
        return await self._delete(f"async-queries/{query_job_id}")

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _strip_version_prefix(self, url: str) -> str:
        """Trim the ``/services/data/vXX.X/`` prefix from a locator URL.

        The session is scoped under that prefix already, so relative paths
        (``query/01gXX...``) are the natural form.
        """
        prefix = f"/services/data/v{self._session._api_version}/"
        if url.startswith(prefix):
            return url[len(prefix) :]
        if url.startswith("/services/data/"):
            # A different version locator — strip up to and including the
            # api version segment.
            parts = url.split("/", 4)
            return parts[4] if len(parts) > 4 else url
        return url.lstrip("/")
