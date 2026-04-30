"""Bulk API 2.0 ingest operations — ``/jobs/ingest/``.

Covers the full ingest lifecycle documented in the Bulk API 2.0
Developer Guide (Spring '26 / API 66.0):

1. :meth:`IngestOperations.create_job` — open a job, get back a ``contentUrl``.
2. :meth:`IngestOperations.upload_data` — stream the CSV payload via PUT.
3. :meth:`IngestOperations.upload_complete` — flip the job to ``UploadComplete``.
4. :meth:`IngestOperations.get_job` — poll until ``state == "JobComplete"``.
5. :meth:`IngestOperations.get_successful_results` /
   :meth:`~IngestOperations.get_failed_results` /
   :meth:`~IngestOperations.get_unprocessed_results` — download outcome CSVs.
6. :meth:`IngestOperations.delete_job` — tidy up after a terminal state.

Also supports :meth:`abort_job` to cancel an in-flight job, and
:meth:`get_all_jobs` to list jobs in the org.
"""

from __future__ import annotations

from typing import Any

from salesforce_py.bulk._limits import (
    validate_column_delimiter,
    validate_line_ending,
    validate_operation,
    validate_upload_size,
)
from salesforce_py.bulk.base import BulkBaseOperations


class IngestOperations(BulkBaseOperations):
    """Bulk API 2.0 ingest (write) jobs — ``/jobs/ingest/``."""

    # ------------------------------------------------------------------
    # Job lifecycle
    # ------------------------------------------------------------------

    async def create_job(
        self,
        *,
        object_name: str,
        operation: str,
        external_id_field: str | None = None,
        assignment_rule_id: str | None = None,
        column_delimiter: str = "COMMA",
        line_ending: str = "LF",
        content_type: str = "CSV",
    ) -> dict[str, Any]:
        """Create an ingest job.

        Args:
            object_name: Target sObject, e.g. ``"Account"``.
            operation: One of ``insert``, ``update``, ``upsert``, ``delete``,
                ``hardDelete``.
            external_id_field: Required when *operation* is ``upsert``.
            assignment_rule_id: Optional Case/Lead assignment rule ID.
            column_delimiter: One of ``BACKQUOTE``, ``CARET``, ``COMMA``,
                ``PIPE``, ``SEMICOLON``, ``TAB``. Defaults to ``COMMA``.
            line_ending: ``LF`` or ``CRLF``. Defaults to ``LF``.
            content_type: Always ``"CSV"`` — the only value Bulk 2.0 accepts.

        Returns:
            The job info JSON, including ``id`` and ``contentUrl``. The
            ``contentUrl`` is the relative path to PUT the CSV payload to.

        Raises:
            ValueError: On invalid operation / delimiter / line ending, or
                when ``upsert`` is requested without ``external_id_field``.
        """
        validate_operation(operation)
        validate_column_delimiter(column_delimiter)
        validate_line_ending(line_ending)

        if operation == "upsert" and not external_id_field:
            raise ValueError(
                "upsert requires external_id_field — the API field used to match "
                "incoming records to existing records."
            )

        payload: dict[str, Any] = {
            "object": object_name,
            "operation": operation,
            "columnDelimiter": column_delimiter,
            "lineEnding": line_ending,
            "contentType": content_type,
        }
        if external_id_field:
            payload["externalIdFieldName"] = external_id_field
        if assignment_rule_id:
            payload["assignmentRuleId"] = assignment_rule_id

        return await self._post("ingest", json=payload)

    async def upload_data(
        self,
        job_id: str,
        *,
        csv_data: bytes,
        content_url: str | None = None,
    ) -> None:
        """Upload the CSV payload for a job in state ``Open``.

        Args:
            job_id: The job ID returned by :meth:`create_job`.
            csv_data: Raw CSV bytes, not base64-encoded. Must not exceed
                ``MAX_UPLOAD_BYTES_RAW`` (100 MB) — validated client-side
                because the server applies its 150 MB cap post-base64.
            content_url: Optional upload path. When omitted, defaults to
                ``ingest/{job_id}/batches``. If passed (typically the
                ``contentUrl`` returned by :meth:`create_job`), any
                ``services/data/vXX.X/jobs/`` prefix is stripped so the
                final URL is not double-prefixed by the session's base path.

        Raises:
            ValueError: If *csv_data* exceeds the raw upload ceiling.
            SalesforcePyError: On non-201 response.
        """
        validate_upload_size(csv_data)
        path = (
            self._normalize_content_url(content_url) if content_url else f"ingest/{job_id}/batches"
        )
        await self._put_csv(path, data=csv_data)

    @staticmethod
    def _normalize_content_url(content_url: str) -> str:
        """Strip the ``services/data/vXX.X/jobs/`` prefix if present.

        Salesforce returns ``contentUrl`` as the full API-version-qualified
        path (e.g. ``services/data/v66.0/jobs/ingest/<id>/batches``), but
        the Bulk session's base URL already includes that prefix. Passing
        the raw ``contentUrl`` back would double-prefix the final URL.
        """
        trimmed = content_url.lstrip("/")
        marker = "jobs/"
        idx = trimmed.rfind(marker)
        if idx != -1:
            return trimmed[idx + len(marker) :]
        return trimmed

    async def upload_complete(self, job_id: str) -> dict[str, Any]:
        """Mark an ingest job's upload as finished, moving it to ``UploadComplete``.

        Salesforce then queues the job for processing; poll
        :meth:`get_job` until ``state`` is ``JobComplete``, ``Failed``,
        or ``Aborted``.
        """
        return await self._patch(
            f"ingest/{job_id}",
            json={"state": "UploadComplete"},
        )

    async def get_job(self, job_id: str) -> dict[str, Any]:
        """Fetch the current state of an ingest job."""
        return await self._get(f"ingest/{job_id}")

    async def get_all_jobs(
        self,
        *,
        is_pk_chunking_enabled: bool | None = None,
        job_type: str | None = None,
        concurrency_mode: str | None = None,
        query_locator: str | None = None,
    ) -> dict[str, Any]:
        """List ingest jobs in the org.

        Args:
            is_pk_chunking_enabled: Filter by PK chunking status.
            job_type: ``BigObjectIngest``, ``Classic``, or ``V2Ingest``.
            concurrency_mode: ``Parallel`` or ``Serial``.
            query_locator: Continuation locator from a previous page.
        """
        return await self._get(
            "ingest",
            params={
                "isPkChunkingEnabled": is_pk_chunking_enabled,
                "jobType": job_type,
                "concurrencyMode": concurrency_mode,
                "queryLocator": query_locator,
            },
        )

    async def abort_job(self, job_id: str) -> dict[str, Any]:
        """Abort an in-flight ingest job, moving it to ``Aborted``."""
        return await self._patch(
            f"ingest/{job_id}",
            json={"state": "Aborted"},
        )

    async def delete_job(self, job_id: str) -> None:
        """Delete a terminated ingest job and its associated results."""
        await self._delete(f"ingest/{job_id}")

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    async def get_successful_results(self, job_id: str) -> bytes:
        """Download the CSV of successfully processed records.

        The returned CSV includes the original columns plus ``sf__Id``
        and ``sf__Created`` columns injected by Salesforce.
        """
        response = await self._get_csv(f"ingest/{job_id}/successfulResults")
        return response.content

    async def get_failed_results(self, job_id: str) -> bytes:
        """Download the CSV of records that failed processing.

        The returned CSV includes the original columns plus ``sf__Error``
        and ``sf__Id`` columns.
        """
        response = await self._get_csv(f"ingest/{job_id}/failedResults")
        return response.content

    async def get_unprocessed_results(self, job_id: str) -> bytes:
        """Download the CSV of records the job did not process.

        Records land here when the job times out or errors before
        processing them — re-submit them in a new job.
        """
        response = await self._get_csv(f"ingest/{job_id}/unprocessedrecords")
        return response.content

    # ------------------------------------------------------------------
    # Convenience wrappers
    # ------------------------------------------------------------------

    async def upsert(
        self,
        *,
        object_name: str,
        external_id_field: str,
        csv_data: bytes,
        column_delimiter: str = "COMMA",
        line_ending: str = "LF",
        assignment_rule_id: str | None = None,
    ) -> dict[str, Any]:
        """Create + upload + close an upsert job in one call.

        This is the most common ingest pattern: pass raw CSV bytes keyed
        on an external ID, get back the ``UploadComplete`` job info. Poll
        :meth:`get_job` for terminal state, then call
        :meth:`get_successful_results` / :meth:`get_failed_results`.

        Args:
            object_name: Target sObject.
            external_id_field: API name of the external ID field.
            csv_data: Raw CSV bytes.
            column_delimiter: See :meth:`create_job`.
            line_ending: See :meth:`create_job`.
            assignment_rule_id: Optional assignment rule ID.

        Returns:
            Job info JSON after the ``UploadComplete`` transition.
        """
        job = await self.create_job(
            object_name=object_name,
            operation="upsert",
            external_id_field=external_id_field,
            column_delimiter=column_delimiter,
            line_ending=line_ending,
            assignment_rule_id=assignment_rule_id,
        )
        job_id = job["id"]
        await self.upload_data(
            job_id,
            csv_data=csv_data,
            content_url=job.get("contentUrl"),
        )
        return await self.upload_complete(job_id)
