"""Query Data 360 operations.

Covers all three query surfaces exposed by the Data 360 Connect API:

- ``query`` (V1) and ``queryv2`` — document-style SAQL-like queries
- ``query-sql`` — SQL query submission, polling, and row streaming
"""

from __future__ import annotations

from typing import Any

from salesforce_py.data360.base import Data360BaseOperations


class QueryOperations(Data360BaseOperations):
    """Wrapper for ``/ssot/query``, ``/ssot/queryv2``, and ``/ssot/query-sql*`` endpoints."""

    # ------------------------------------------------------------------
    # V1 / V2 queries
    # ------------------------------------------------------------------

    async def query_v1(
        self,
        data: dict[str, Any],
        *,
        batch_size: int | None = None,
        dataspace: str | None = None,
        offset: int | None = None,
        orderby: str | None = None,
    ) -> dict[str, Any]:
        """Submit a V1 data query."""
        return await self._post(
            "query",
            json=data,
            params={
                "batchSize": batch_size,
                "dataspace": dataspace,
                "offset": offset,
                "orderby": orderby,
            },
        )

    async def query_v2(
        self, data: dict[str, Any], *, dataspace: str | None = None
    ) -> dict[str, Any]:
        """Submit a V2 data query."""
        return await self._post("queryv2", json=data, params={"dataspace": dataspace})

    async def get_query_batch(
        self, next_batch_id: str, *, dataspace: str | None = None
    ) -> dict[str, Any]:
        """Fetch the next batch of rows from a V1/V2 query."""
        return await self._get(f"queryv2/{next_batch_id}", params={"dataspace": dataspace})

    # ------------------------------------------------------------------
    # SQL query
    # ------------------------------------------------------------------

    async def submit_sql_query(
        self,
        data: dict[str, Any],
        *,
        dataspace: str | None = None,
        workload_name: str | None = None,
    ) -> dict[str, Any]:
        """Submit a SQL query for asynchronous execution."""
        return await self._post(
            "query-sql",
            json=data,
            params={"dataspace": dataspace, "workloadName": workload_name},
        )

    async def get_sql_query_status(
        self,
        query_id: str,
        *,
        dataspace: str | None = None,
        wait_time_ms: int | None = None,
        workload_name: str | None = None,
    ) -> dict[str, Any]:
        """Get the status of a SQL query."""
        return await self._get(
            f"query-sql/{query_id}",
            params={
                "dataspace": dataspace,
                "waitTimeMs": wait_time_ms,
                "workloadName": workload_name,
            },
        )

    async def cancel_sql_query(
        self,
        query_id: str,
        *,
        dataspace: str | None = None,
        workload_name: str | None = None,
    ) -> dict[str, Any]:
        """Cancel a running SQL query."""
        return await self._delete(
            f"query-sql/{query_id}",
            params={"dataspace": dataspace, "workloadName": workload_name},
        )

    async def get_sql_query_rows(
        self,
        query_id: str,
        *,
        dataspace: str,
        offset: int,
        row_limit: int | None = None,
        workload_name: str | None = None,
    ) -> dict[str, Any]:
        """Fetch a page of rows from a completed SQL query."""
        return await self._get(
            f"query-sql/{query_id}/rows",
            params={
                "dataspace": dataspace,
                "offset": offset,
                "rowLimit": row_limit,
                "workloadName": workload_name,
            },
        )
