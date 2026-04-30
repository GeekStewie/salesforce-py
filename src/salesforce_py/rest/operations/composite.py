"""Composite — multi-request batching resources.

Covers:

- ``/services/data/vXX.X/composite`` — Executes a series of REST API requests
  in a single POST request (or GET to list other composite resources).
- ``/services/data/vXX.X/composite/batch`` — Executes up to 25 subrequests in
  a single request.
- ``/services/data/vXX.X/composite/graph`` — Enhanced composite requests
  (graphs of related subrequests).
- ``/services/data/vXX.X/composite/tree`` — Creates one or more sObject trees
  with root records of the specified type.
- ``/services/data/vXX.X/composite/sobjects`` — Executes actions on multiple
  records in one request (create/update/upsert/delete collections).
"""

from __future__ import annotations

from typing import Any

from salesforce_py.rest.base import RestBaseOperations


class CompositeOperations(RestBaseOperations):
    """Wrapper for ``/composite``, ``/composite/batch``, ``/composite/graph``,
    ``/composite/tree``, and ``/composite/sobjects``."""

    # ------------------------------------------------------------------
    # Directory
    # ------------------------------------------------------------------

    async def list_resources(self) -> dict[str, Any]:
        """List the available composite resources (``batch``, ``graph``, ``sobjects``, ``tree``)."""
        return await self._get("composite")

    # ------------------------------------------------------------------
    # Composite (chained subrequests)
    # ------------------------------------------------------------------

    async def execute(
        self,
        composite_request: list[dict[str, Any]],
        *,
        all_or_none: bool = False,
        collate_subrequests: bool = False,
    ) -> dict[str, Any]:
        """Execute a composite request.

        Args:
            composite_request: Ordered list of subrequest dicts. Each
                subrequest carries ``method``, ``url``, optional ``body``,
                and ``referenceId``.
            all_or_none: When True, rolls back every subrequest if any fails.
            collate_subrequests: When True, Salesforce may collate multiple
                DML-style subrequests into a single database operation.
        """
        return await self._post(
            "composite",
            json={
                "compositeRequest": composite_request,
                "allOrNone": all_or_none,
                "collateSubrequests": collate_subrequests,
            },
        )

    # ------------------------------------------------------------------
    # Composite batch (up to 25 subrequests)
    # ------------------------------------------------------------------

    async def batch(
        self,
        batch_requests: list[dict[str, Any]],
        *,
        halt_on_error: bool = False,
    ) -> dict[str, Any]:
        """Execute up to 25 subrequests in a single request.

        Args:
            batch_requests: List of subrequest dicts with ``method``,
                ``url``, and optional ``richInput``.
            halt_on_error: Stop execution after the first subrequest that
                returns a non-2xx status.
        """
        return await self._post(
            "composite/batch",
            json={"batchRequests": batch_requests, "haltOnError": halt_on_error},
        )

    # ------------------------------------------------------------------
    # Composite graphs
    # ------------------------------------------------------------------

    async def graph(self, graphs: list[dict[str, Any]]) -> dict[str, Any]:
        """Execute one or more composite graphs.

        Args:
            graphs: List of graph dicts — each with ``graphId`` and
                ``compositeRequest``. See "Using Composite Graphs" in the
                REST API Developer Guide.
        """
        return await self._post("composite/graph", json={"graphs": graphs})

    # ------------------------------------------------------------------
    # Composite tree (nested parent/child creation)
    # ------------------------------------------------------------------

    async def tree(
        self, object_name: str, records: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Create one or more sObject trees rooted at *object_name*."""
        return await self._post(
            f"composite/tree/{object_name}", json={"records": records}
        )

    # ------------------------------------------------------------------
    # Composite sObject collections
    # ------------------------------------------------------------------

    async def sobjects_create(
        self,
        records: list[dict[str, Any]],
        *,
        all_or_none: bool = False,
    ) -> list[dict[str, Any]]:
        """Create up to 200 records across multiple sObjects in one call."""
        response = await self._post(
            "composite/sobjects",
            json={"records": records, "allOrNone": all_or_none},
        )
        return response if isinstance(response, list) else response.get("results", [])  # type: ignore[return-value]

    async def sobjects_update(
        self,
        records: list[dict[str, Any]],
        *,
        all_or_none: bool = False,
    ) -> list[dict[str, Any]]:
        """Update up to 200 records in one call."""
        response = await self._patch(
            "composite/sobjects",
            json={"records": records, "allOrNone": all_or_none},
        )
        return response if isinstance(response, list) else response.get("results", [])  # type: ignore[return-value]

    async def sobjects_upsert(
        self,
        object_name: str,
        external_id_field: str,
        records: list[dict[str, Any]],
        *,
        all_or_none: bool = False,
    ) -> list[dict[str, Any]]:
        """Upsert up to 200 records for a specific sObject + external ID."""
        response = await self._patch(
            f"composite/sobjects/{object_name}/{external_id_field}",
            json={"records": records, "allOrNone": all_or_none},
        )
        return response if isinstance(response, list) else response.get("results", [])  # type: ignore[return-value]

    async def sobjects_delete(
        self,
        ids: list[str],
        *,
        all_or_none: bool = False,
    ) -> list[dict[str, Any]]:
        """Delete up to 200 records by ID in a single call."""
        response = await self._delete(
            "composite/sobjects",
            params={"ids": ",".join(ids), "allOrNone": str(all_or_none).lower()},
        )
        return response if isinstance(response, list) else response.get("results", [])  # type: ignore[return-value]

    async def sobjects_retrieve(
        self,
        object_name: str,
        ids: list[str],
        fields: list[str],
    ) -> list[dict[str, Any]]:
        """Retrieve up to 2,000 records by ID for a single sObject."""
        response = await self._post(
            f"composite/sobjects/{object_name}",
            json={"ids": ids, "fields": fields},
        )
        return response if isinstance(response, list) else response.get("results", [])  # type: ignore[return-value]
