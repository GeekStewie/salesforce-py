"""Bulk API 2.0 query operations — ``/jobs/query/``.

Covers the documented query lifecycle:

1. :meth:`QueryOperations.create_job` — submit a SOQL query. ``ORDER BY``
   is stripped automatically because it disables PK chunking; the clause
   is captured on the returned job info as ``_stripped_order_by`` so the
   download helpers can reapply it client-side via DuckDB.
2. :meth:`QueryOperations.get_job` — poll for ``state == "JobComplete"``.
3. :meth:`QueryOperations.get_results` — fetch one CSV page plus the
   ``Sforce-Locator`` for the next page.
4. :meth:`QueryOperations.get_all_results` — loop until the locator is
   exhausted, concatenate the pages, and reapply the captured ``ORDER BY``
   via DuckDB when one was stripped.
5. :meth:`QueryOperations.get_parallel_results` — ``/resultPages`` fan-out
   (API 58.0+) for parallel downloading of large result sets.

Also exposes :meth:`run_query` as the end-to-end convenience wrapper and
the usual :meth:`abort_job` / :meth:`delete_job` / :meth:`get_all_jobs`
admin helpers.
"""

from __future__ import annotations

import asyncio
from typing import Any

from salesforce_py.bulk._duckdb import apply_order_by, concatenate_csv_pages
from salesforce_py.bulk._limits import (
    validate_column_delimiter,
    validate_line_ending,
    validate_query_operation,
)
from salesforce_py.bulk._soql import OrderByClause, prepare_query
from salesforce_py.bulk.base import BulkBaseOperations
from salesforce_py.exceptions import SalesforcePyError


class QueryOperations(BulkBaseOperations):
    """Bulk API 2.0 query (read) jobs — ``/jobs/query/``."""

    # ------------------------------------------------------------------
    # Job lifecycle
    # ------------------------------------------------------------------

    async def create_job(
        self,
        *,
        soql: str,
        operation: str = "query",
        column_delimiter: str = "COMMA",
        line_ending: str = "LF",
        content_type: str = "CSV",
    ) -> dict[str, Any]:
        """Submit a SOQL query as a Bulk 2.0 job.

        If *soql* contains an ``ORDER BY`` clause, it is stripped before
        submission (to keep PK chunking enabled) and captured on the
        returned dict under the ``_stripped_order_by`` key — an
        :class:`~salesforce_py.bulk._soql.OrderByClause` instance. Pass
        that alongside the job ID to :meth:`get_all_results` to have the
        combined CSV re-sorted client-side via DuckDB.

        Args:
            soql: SOQL query string.
            operation: ``query`` (default) or ``queryAll`` to include
                soft-deleted and archived records.
            column_delimiter: One of the documented delimiters.
            line_ending: ``LF`` or ``CRLF``.
            content_type: Always ``"CSV"``.

        Returns:
            The job info JSON with an extra ``_stripped_order_by`` key
            (``None`` if the original SOQL had no ``ORDER BY``).

        Raises:
            ValueError: On invalid operation / delimiter / line ending,
                or on a SOQL construct Bulk 2.0 rejects (``GROUP BY``,
                ``OFFSET``, ``TYPEOF``, aggregates).
        """
        validate_query_operation(operation)
        validate_column_delimiter(column_delimiter)
        validate_line_ending(line_ending)

        prepared = prepare_query(soql)

        payload = {
            "operation": operation,
            "query": prepared.soql,
            "columnDelimiter": column_delimiter,
            "lineEnding": line_ending,
            "contentType": content_type,
        }
        job = await self._post("query", json=payload)
        job["_stripped_order_by"] = prepared.order_by
        return job

    async def get_job(self, job_id: str) -> dict[str, Any]:
        """Fetch the current state of a query job."""
        return await self._get(f"query/{job_id}")

    async def get_all_jobs(
        self,
        *,
        is_pk_chunking_enabled: bool | None = None,
        job_type: str | None = None,
        concurrency_mode: str | None = None,
        query_locator: str | None = None,
    ) -> dict[str, Any]:
        """List query jobs in the org — mirrors the ingest variant."""
        return await self._get(
            "query",
            params={
                "isPkChunkingEnabled": is_pk_chunking_enabled,
                "jobType": job_type,
                "concurrencyMode": concurrency_mode,
                "queryLocator": query_locator,
            },
        )

    async def abort_job(self, job_id: str) -> dict[str, Any]:
        """Abort a running query job."""
        return await self._patch(
            f"query/{job_id}",
            json={"state": "Aborted"},
        )

    async def delete_job(self, job_id: str) -> None:
        """Delete a terminated query job and its cached results."""
        await self._delete(f"query/{job_id}")

    # ------------------------------------------------------------------
    # Result download
    # ------------------------------------------------------------------

    async def get_results(
        self,
        job_id: str,
        *,
        locator: str | None = None,
        max_records: int | None = None,
    ) -> tuple[bytes, str | None, int]:
        """Fetch one page of query results.

        Args:
            job_id: The query job ID.
            locator: Pagination cursor from the previous call's
                ``Sforce-Locator`` header. Omit for the first page.
            max_records: Cap the number of records returned in this page
                — up to the server's default (usually 50,000).

        Returns:
            ``(csv_bytes, next_locator, record_count)``.
            ``next_locator`` is ``None`` when the final page has been
            downloaded. ``record_count`` comes from the
            ``Sforce-NumberOfRecords`` header.
        """
        response = await self._get_csv(
            f"query/{job_id}/results",
            params={"locator": locator, "maxRecords": max_records},
        )
        next_locator = response.headers.get("Sforce-Locator")
        # "null" means "no more pages".
        if next_locator in (None, "", "null"):
            next_locator = None
        try:
            record_count = int(response.headers.get("Sforce-NumberOfRecords", "0"))
        except (TypeError, ValueError):
            record_count = 0
        return response.content, next_locator, record_count

    async def get_all_results(
        self,
        job_id: str,
        *,
        order_by: OrderByClause | None = None,
        column_delimiter: str = "COMMA",
        line_ending: str = "LF",
        max_records: int | None = None,
    ) -> bytes:
        """Download every page of a completed query and return combined CSV.

        When *order_by* is supplied (typically from ``job["_stripped_order_by"]``
        after :meth:`create_job`), the combined CSV is re-sorted locally via
        DuckDB using the captured expressions.

        Args:
            job_id: The query job ID. Must be in ``JobComplete`` state.
            order_by: The clause stripped at submission time, or ``None``
                if the original query had none.
            column_delimiter: Must match the job's ``columnDelimiter``.
            line_ending: Must match the job's ``lineEnding``.
            max_records: Optional per-page record cap.

        Returns:
            The full CSV payload — concatenated and (if *order_by* is set)
            sorted client-side.
        """
        pages: list[bytes] = []
        locator: str | None = None
        while True:
            page, locator, _ = await self.get_results(
                job_id,
                locator=locator,
                max_records=max_records,
            )
            if page:
                pages.append(page)
            if locator is None:
                break

        combined = concatenate_csv_pages(pages, line_ending=line_ending)
        if order_by and order_by.columns:
            combined = apply_order_by(
                combined,
                order_by,
                column_delimiter=column_delimiter,
                line_ending=line_ending,
            )
        return combined

    async def get_parallel_results(
        self,
        job_id: str,
        *,
        max_records: int | None = None,
    ) -> list[str]:
        """Return the list of parallel-download locator cursors for a query.

        Available from API 58.0 onward. Each returned locator is passed
        to :meth:`get_results` to download one result page; pages can be
        fetched concurrently.

        Args:
            job_id: The completed query job ID.
            max_records: Optional per-page record cap to embed in the
                returned locators.

        Returns:
            List of locator strings. Empty if the result set fits in a
            single page.
        """
        payload = await self._get(
            f"query/{job_id}/resultPages",
            params={"maxRecords": max_records},
        )
        return list(payload.get("locators", []))

    # ------------------------------------------------------------------
    # Convenience wrappers
    # ------------------------------------------------------------------

    async def run_query(
        self,
        soql: str,
        *,
        operation: str = "query",
        column_delimiter: str = "COMMA",
        line_ending: str = "LF",
        poll_interval: float = 3.0,
        poll_timeout: float = 1800.0,
        max_records_per_page: int | None = None,
        auto_delete: bool = False,
    ) -> bytes:
        """Submit, poll, and download a Bulk query end-to-end.

        Handles the full lifecycle: strip ``ORDER BY`` → submit → poll
        until ``JobComplete`` → download all pages → reapply ``ORDER BY``
        via DuckDB → (optionally) delete the job.

        Args:
            soql: SOQL query string.
            operation: ``query`` or ``queryAll``.
            column_delimiter: Column delimiter for results.
            line_ending: Line ending for results.
            poll_interval: Seconds between :meth:`get_job` polls.
            poll_timeout: Give up polling after this many seconds
                (raising :class:`SalesforcePyError`).
            max_records_per_page: Optional cap on records per download page.
            auto_delete: Delete the job after successful download.

        Returns:
            The full (sorted, if needed) CSV payload as bytes.

        Raises:
            SalesforcePyError: On job ``Failed`` / ``Aborted`` states, or
                on poll timeout.
        """
        job = await self.create_job(
            soql=soql,
            operation=operation,
            column_delimiter=column_delimiter,
            line_ending=line_ending,
        )
        job_id = job["id"]
        order_by = job.get("_stripped_order_by")

        elapsed = 0.0
        while True:
            status = await self.get_job(job_id)
            state = status.get("state")
            if state == "JobComplete":
                break
            if state in ("Failed", "Aborted"):
                raise SalesforcePyError(
                    f"Bulk query job {job_id} ended in {state!r}: {status.get('errorMessage', '')}"
                )
            if elapsed >= poll_timeout:
                raise SalesforcePyError(
                    f"Bulk query job {job_id} did not complete within "
                    f"{poll_timeout:g}s (last state: {state!r})."
                )
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        combined = await self.get_all_results(
            job_id,
            order_by=order_by,
            column_delimiter=column_delimiter,
            line_ending=line_ending,
            max_records=max_records_per_page,
        )

        if auto_delete:
            await self.delete_job(job_id)

        return combined
