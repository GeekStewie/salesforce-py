"""SF CLI data command wrappers."""

from pathlib import Path
from typing import Any

from salesforce_py.sf.base import SFBaseOperations


def _values_string(values: dict[str, str]) -> str:
    """Encode a field-value dict into the SF CLI ``--values`` string format.

    Single-word values are passed bare; values containing spaces are wrapped
    in single quotes, matching SF CLI expectations.

    Args:
        values: Field-value pairs, e.g. ``{"Name": "Acme", "Phone": "(123) 456-7890"}``.

    Returns:
        Space-delimited string, e.g. ``"Name=Acme Phone='(123) 456-7890'"``.
    """
    parts: list[str] = []
    for field, value in values.items():
        if " " in value:
            parts.append(f"{field}='{value}'")
        else:
            parts.append(f"{field}={value}")
    return " ".join(parts)


class SFDataOperations(SFBaseOperations):
    """Wraps ``sf data`` commands for record CRUD, bulk operations, and queries."""

    # ------------------------------------------------------------------
    # Single-record CRUD
    # ------------------------------------------------------------------

    def create_record(
        self,
        object_type: str,
        values: dict[str, str],
        use_tooling_api: bool = False,
    ) -> dict[str, Any]:
        """Create and insert a record into a Salesforce or Tooling API object.

        Args:
            object_type: SObject API name (e.g. ``Account``).
            values: Field-value pairs to set on the new record.
            use_tooling_api: Insert into a Tooling API object instead.

        Returns:
            Dict containing the ``id`` of the created record.
        """
        args = [
            "data",
            "create",
            "record",
            "--sobject",
            object_type,
            "--values",
            _values_string(values),
        ]
        if use_tooling_api:
            args.append("--use-tooling-api")

        return self._run_capturing(
            args,
            label=f"Creating {object_type} record",
        )

    def get_record(
        self,
        object_type: str,
        record_id: str | None = None,
        where: str | None = None,
        use_tooling_api: bool = False,
    ) -> dict[str, Any]:
        """Retrieve a single record from a Salesforce or Tooling API object.

        Provide either ``record_id`` or ``where``; not both.

        Args:
            object_type: SObject API name.
            record_id: Salesforce record ID.
            where: Field-value pairs identifying the record, e.g.
                ``"Name=Acme"`` or ``"Name='Universal Containers' Phone='(123) 456-7890'"``.
            use_tooling_api: Retrieve from a Tooling API object instead.

        Returns:
            Record field dict.
        """
        args = ["data", "get", "record", "--sobject", object_type]

        if record_id:
            args += ["--record-id", record_id]
        if where:
            args += ["--where", where]
        if use_tooling_api:
            args.append("--use-tooling-api")

        return self._run_capturing(
            args,
            label=f"Getting {object_type} record",
        )

    def update_record(
        self,
        object_type: str,
        values: dict[str, str],
        record_id: str | None = None,
        where: str | None = None,
        use_tooling_api: bool = False,
    ) -> dict[str, Any]:
        """Update a single record of a Salesforce or Tooling API object.

        Provide either ``record_id`` or ``where`` to identify the record.

        Args:
            object_type: SObject API name.
            values: Fields to update as field-value pairs.
            record_id: Salesforce record ID.
            where: Field-value pairs identifying the record.
            use_tooling_api: Update a Tooling API object instead.

        Returns:
            Result dict confirming the update.
        """
        args = [
            "data",
            "update",
            "record",
            "--sobject",
            object_type,
            "--values",
            _values_string(values),
        ]

        if record_id:
            args += ["--record-id", record_id]
        if where:
            args += ["--where", where]
        if use_tooling_api:
            args.append("--use-tooling-api")

        return self._run_capturing(
            args,
            label=f"Updating {object_type} record",
        )

    def delete_record(
        self,
        object_type: str,
        record_id: str | None = None,
        where: str | None = None,
        use_tooling_api: bool = False,
    ) -> dict[str, Any]:
        """Delete a single record from a Salesforce or Tooling API object.

        Provide either ``record_id`` or ``where`` to identify the record.

        Args:
            object_type: SObject API name.
            record_id: Salesforce record ID.
            where: Field-value pairs identifying the record.
            use_tooling_api: Delete from a Tooling API object instead.

        Returns:
            Result dict confirming the deletion.
        """
        args = ["data", "delete", "record", "--sobject", object_type]

        if record_id:
            args += ["--record-id", record_id]
        if where:
            args += ["--where", where]
        if use_tooling_api:
            args.append("--use-tooling-api")

        return self._run_capturing(
            args,
            label=f"Deleting {object_type} record",
        )

    # ------------------------------------------------------------------
    # File upload
    # ------------------------------------------------------------------

    def create_file(
        self,
        file_path: Path,
        title: str | None = None,
        parent_id: str | None = None,
    ) -> dict[str, Any]:
        """Upload a local file to the org.

        Always creates a new ContentDocument; cannot update an existing one.

        Args:
            file_path: Path to the local file to upload.
            title: Filename to use in the org (defaults to the local filename).
            parent_id: Record ID to attach the file to.

        Returns:
            Dict containing the ``id`` of the new ContentDocument record.
        """
        args = ["data", "create", "file", "--file", str(file_path)]

        if title:
            args += ["--title", title]
        if parent_id:
            args += ["--parent-id", parent_id]

        return self._run_capturing(
            args,
            label=f"Uploading file {file_path.name}",
        )

    # ------------------------------------------------------------------
    # SOQL query
    # ------------------------------------------------------------------

    def query(
        self,
        soql: str | None = None,
        query_file: Path | None = None,
        use_tooling_api: bool = False,
        all_rows: bool = False,
        result_format: str = "json",
        output_file: Path | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a SOQL query.

        Provide either ``soql`` or ``query_file``; not both.

        Args:
            soql: SOQL SELECT query string.
            query_file: File containing the SOQL query.
            use_tooling_api: Query Tooling API objects.
            all_rows: Include soft-deleted records.
            result_format: Output format: ``json``, ``csv``, or ``human``.
            output_file: File to write CSV or JSON results to.

        Returns:
            List of record dicts (when ``result_format`` is ``json``).
        """
        args = ["data", "query", "--result-format", result_format]

        if soql:
            args += ["--query", soql]
        if query_file:
            args += ["--file", str(query_file)]
        if use_tooling_api:
            args.append("--use-tooling-api")
        if all_rows:
            args.append("--all-rows")
        if output_file:
            args += ["--output-file", str(output_file)]

        result = self._run_capturing(args, label="Querying")
        records = result.get("records", result)
        if isinstance(records, list):
            return records
        return [records] if records else []

    # ------------------------------------------------------------------
    # SOSL search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str | None = None,
        query_file: Path | None = None,
        result_format: str = "json",
    ) -> dict[str, Any]:
        """Execute a SOSL text-based search query.

        Provide either ``query`` or ``query_file``; not both.

        Args:
            query: SOSL FIND query string.
            query_file: File containing the SOSL query.
            result_format: Output format: ``json``, ``csv``, or ``human``.
                ``csv`` writes one file per returned SObject type.

        Returns:
            Search result dict keyed by SObject type.
        """
        args = ["data", "search", "--result-format", result_format]

        if query:
            args += ["--query", query]
        if query_file:
            args += ["--file", str(query_file)]

        return self._run_capturing(args, label="Searching")

    # ------------------------------------------------------------------
    # Bulk job status
    # ------------------------------------------------------------------

    def resume(
        self,
        job_id: str,
        batch_id: str | None = None,
    ) -> dict[str, Any]:
        """View the status of a bulk data load job or batch (Bulk API 1.0).

        Args:
            job_id: ID of the bulk job to check.
            batch_id: Optional batch ID within the job.

        Returns:
            Status dict for the job or batch.
        """
        args = ["data", "resume", "--job-id", job_id]
        if batch_id:
            args += ["--batch-id", batch_id]

        return self._run_capturing(args, label=f"Checking bulk job status {job_id}")

    def bulk_results(self, job_id: str) -> dict[str, Any]:
        """Get the results of a completed bulk ingest job (Bulk API 2.0).

        The job must have completed; run the corresponding resume command first
        if it is still processing.

        Args:
            job_id: Job ID of the completed bulk ingest operation.

        Returns:
            Result dict with job status, record counts, and paths to result files.
        """
        return self._run_capturing(
            ["data", "bulk", "results", "--job-id", job_id],
            label=f"Fetching bulk results for job {job_id}",
        )

    # ------------------------------------------------------------------
    # Bulk delete (Bulk API 2.0)
    # ------------------------------------------------------------------

    def delete_bulk(
        self,
        object_type: str,
        file_path: Path,
        wait: int | None = None,
        hard_delete: bool = False,
        line_ending: str | None = None,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Bulk delete records from the org using a CSV file (Bulk API 2.0).

        The CSV file must have a single ``Id`` column.

        Args:
            object_type: SObject API name.
            file_path: CSV file containing record IDs.
            wait: Minutes to wait before returning (omit to return immediately
                with a job ID).
            hard_delete: Mark records as immediately eligible for deletion
                (bypasses Recycle Bin; requires "Bulk API Hard Delete" permission).
            line_ending: CSV line ending: ``LF`` or ``CRLF``.
            timeout: Subprocess timeout in seconds.

        Returns:
            Job status dict, or a dict containing ``jobId`` if not waited.
        """
        args = [
            "data",
            "delete",
            "bulk",
            "--sobject",
            object_type,
            "--file",
            str(file_path),
        ]

        if wait is not None:
            args += ["--wait", str(wait)]
        if hard_delete:
            args.append("--hard-delete")
        if line_ending:
            args += ["--line-ending", line_ending]

        return self._run_capturing(
            args,
            label=f"Bulk deleting {object_type}",
            timeout=timeout,
        )

    def delete_resume(
        self,
        job_id: str | None = None,
        use_most_recent: bool = False,
        wait: int | None = None,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Resume a bulk delete job (Bulk API 2.0).

        Provide either ``job_id`` or ``use_most_recent=True``.

        Args:
            job_id: Job ID from a previous ``delete_bulk`` call.
            use_most_recent: Resume the most recently started bulk delete job.
            wait: Minutes to wait for completion.
            timeout: Subprocess timeout in seconds.

        Returns:
            Job result dict.
        """
        args = ["data", "delete", "resume"]
        if job_id:
            args += ["--job-id", job_id]
        if use_most_recent:
            args.append("--use-most-recent")
        if wait is not None:
            args += ["--wait", str(wait)]

        return self._run_capturing(
            args,
            label=f"Resuming bulk delete job {job_id or '(most recent)'}",
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Bulk export (Bulk API 2.0)
    # ------------------------------------------------------------------

    def export_bulk(
        self,
        output_file: Path,
        soql: str | None = None,
        query_file: Path | None = None,
        result_format: str = "csv",
        wait: int | None = None,
        all_rows: bool = False,
        column_delimiter: str | None = None,
        line_ending: str | None = None,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Bulk export records into a file using a SOQL query (Bulk API 2.0).

        Provide either ``soql`` or ``query_file``; not both.

        Args:
            output_file: File to write exported records to (required).
            soql: SOQL SELECT query.
            query_file: File containing the SOQL query.
            result_format: Output format: ``csv`` or ``json``.
            wait: Minutes to wait before returning with job ID.
            all_rows: Include soft-deleted records.
            column_delimiter: CSV column delimiter: ``BACKQUOTE``, ``CARET``,
                ``COMMA``, ``PIPE``, ``SEMICOLON``, or ``TAB``.
            line_ending: CSV line ending: ``LF`` or ``CRLF``.
            timeout: Subprocess timeout in seconds.

        Returns:
            Export result dict, or a dict containing ``jobId`` if not waited.
        """
        args = [
            "data",
            "export",
            "bulk",
            "--output-file",
            str(output_file),
            "--result-format",
            result_format,
        ]

        if soql:
            args += ["--query", soql]
        if query_file:
            args += ["--query-file", str(query_file)]
        if wait is not None:
            args += ["--wait", str(wait)]
        if all_rows:
            args.append("--all-rows")
        if column_delimiter:
            args += ["--column-delimiter", column_delimiter]
        if line_ending:
            args += ["--line-ending", line_ending]

        return self._run_capturing(
            args,
            label=f"Bulk exporting to {output_file.name}",
            timeout=timeout,
        )

    def export_resume(
        self,
        job_id: str | None = None,
        use_most_recent: bool = False,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Resume a bulk export job (Bulk API 2.0).

        Provide either ``job_id`` or ``use_most_recent=True``.

        Args:
            job_id: Job ID from a previous ``export_bulk`` call.
            use_most_recent: Resume the most recently started bulk export job.
            timeout: Subprocess timeout in seconds.

        Returns:
            Export result dict.
        """
        args = ["data", "export", "resume"]
        if job_id:
            args += ["--job-id", job_id]
        if use_most_recent:
            args.append("--use-most-recent")

        return self._run_capturing(
            args,
            label=f"Resuming bulk export job {job_id or '(most recent)'}",
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Tree export / import (sObject tree format)
    # ------------------------------------------------------------------

    def export_tree(
        self,
        soql: str,
        plan: bool = False,
        prefix: str | None = None,
        output_dir: Path | None = None,
        timeout: int = 120,
    ) -> dict[str, Any]:
        """Export data from the org into JSON files in sObject tree format.

        Args:
            soql: SOQL query to retrieve export data (max 2,000 records).
            plan: Generate separate JSON files per object plus a plan
                definition file.
            prefix: Prefix prepended to all generated file names.
            output_dir: Directory to write JSON files into.
            timeout: Subprocess timeout in seconds.

        Returns:
            Export result dict listing the generated files.
        """
        args = ["data", "export", "tree", "--query", soql]

        if plan:
            args.append("--plan")
        if prefix:
            args += ["--prefix", prefix]
        if output_dir:
            args += ["--output-dir", str(output_dir)]

        return self._run_capturing(
            args,
            label="Exporting data tree",
            timeout=timeout,
        )

    def import_tree(
        self,
        files: list[Path] | None = None,
        plan: Path | None = None,
        timeout: int = 120,
    ) -> dict[str, Any]:
        """Import data from JSON files in sObject tree format into the org.

        Provide either ``files`` (ordered list of JSON files) or ``plan``
        (plan definition file); not both.

        Args:
            files: Ordered list of JSON files to import. Files with parent
                records must come before files with child records.
            plan: Plan definition file (generated by ``export_tree`` with
                ``plan=True``).
            timeout: Subprocess timeout in seconds.

        Returns:
            Import result dict.
        """
        args = ["data", "import", "tree"]

        if files:
            args += ["--files", ",".join(str(f) for f in files)]
        if plan:
            args += ["--plan", str(plan)]

        return self._run_capturing(
            args,
            label="Importing data tree",
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Bulk import (Bulk API 2.0)
    # ------------------------------------------------------------------

    def import_bulk(
        self,
        object_type: str,
        file_path: Path,
        wait: int | None = None,
        line_ending: str | None = None,
        column_delimiter: str | None = None,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Bulk import records from a CSV file (Bulk API 2.0).

        Args:
            object_type: SObject API name.
            file_path: CSV file containing records to import.
            wait: Minutes to wait before returning with job ID.
            line_ending: CSV line ending: ``LF`` or ``CRLF``.
            column_delimiter: CSV column delimiter: ``BACKQUOTE``, ``CARET``,
                ``COMMA``, ``PIPE``, ``SEMICOLON``, or ``TAB``.
            timeout: Subprocess timeout in seconds.

        Returns:
            Job status dict, or a dict containing ``jobId`` if not waited.
        """
        args = [
            "data",
            "import",
            "bulk",
            "--sobject",
            object_type,
            "--file",
            str(file_path),
        ]

        if wait is not None:
            args += ["--wait", str(wait)]
        if line_ending:
            args += ["--line-ending", line_ending]
        if column_delimiter:
            args += ["--column-delimiter", column_delimiter]

        return self._run_capturing(
            args,
            label=f"Bulk importing {object_type}",
            timeout=timeout,
        )

    def import_resume(
        self,
        job_id: str | None = None,
        use_most_recent: bool = False,
        wait: int | None = None,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Resume a bulk import job (Bulk API 2.0).

        Provide either ``job_id`` or ``use_most_recent=True``.

        Args:
            job_id: Job ID from a previous ``import_bulk`` call.
            use_most_recent: Resume the most recently started bulk import job.
            wait: Minutes to wait for completion.
            timeout: Subprocess timeout in seconds.

        Returns:
            Job result dict.
        """
        args = ["data", "import", "resume"]
        if job_id:
            args += ["--job-id", job_id]
        if use_most_recent:
            args.append("--use-most-recent")
        if wait is not None:
            args += ["--wait", str(wait)]

        return self._run_capturing(
            args,
            label=f"Resuming bulk import job {job_id or '(most recent)'}",
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Bulk update (Bulk API 2.0)
    # ------------------------------------------------------------------

    def update_bulk(
        self,
        object_type: str,
        file_path: Path,
        wait: int | None = None,
        line_ending: str | None = None,
        column_delimiter: str | None = None,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Bulk update records from a CSV file (Bulk API 2.0).

        The CSV file must include an ``Id`` column as the first column.

        Args:
            object_type: SObject API name.
            file_path: CSV file containing records to update.
            wait: Minutes to wait before returning with job ID.
            line_ending: CSV line ending: ``LF`` or ``CRLF``.
            column_delimiter: CSV column delimiter.
            timeout: Subprocess timeout in seconds.

        Returns:
            Job status dict, or a dict containing ``jobId`` if not waited.
        """
        args = [
            "data",
            "update",
            "bulk",
            "--sobject",
            object_type,
            "--file",
            str(file_path),
        ]

        if wait is not None:
            args += ["--wait", str(wait)]
        if line_ending:
            args += ["--line-ending", line_ending]
        if column_delimiter:
            args += ["--column-delimiter", column_delimiter]

        return self._run_capturing(
            args,
            label=f"Bulk updating {object_type}",
            timeout=timeout,
        )

    def update_resume(
        self,
        job_id: str | None = None,
        use_most_recent: bool = False,
        wait: int | None = None,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Resume a bulk update job (Bulk API 2.0).

        Provide either ``job_id`` or ``use_most_recent=True``.

        Args:
            job_id: Job ID from a previous ``update_bulk`` call.
            use_most_recent: Resume the most recently started bulk update job.
            wait: Minutes to wait for completion.
            timeout: Subprocess timeout in seconds.

        Returns:
            Job result dict.
        """
        args = ["data", "update", "resume"]
        if job_id:
            args += ["--job-id", job_id]
        if use_most_recent:
            args.append("--use-most-recent")
        if wait is not None:
            args += ["--wait", str(wait)]

        return self._run_capturing(
            args,
            label=f"Resuming bulk update job {job_id or '(most recent)'}",
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Bulk upsert (Bulk API 2.0)
    # ------------------------------------------------------------------

    def upsert_bulk(
        self,
        object_type: str,
        file_path: Path,
        external_id: str,
        wait: int | None = None,
        line_ending: str | None = None,
        column_delimiter: str | None = None,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Bulk upsert records from a CSV file (Bulk API 2.0).

        Args:
            object_type: SObject API name.
            file_path: CSV file containing records to upsert.
            external_id: External ID field name used for upsert matching,
                or ``Id``.
            wait: Minutes to wait before returning with job ID.
            line_ending: CSV line ending: ``LF`` or ``CRLF``.
            column_delimiter: CSV column delimiter.
            timeout: Subprocess timeout in seconds.

        Returns:
            Job status dict, or a dict containing ``jobId`` if not waited.
        """
        args = [
            "data",
            "upsert",
            "bulk",
            "--sobject",
            object_type,
            "--file",
            str(file_path),
            "--external-id",
            external_id,
        ]

        if wait is not None:
            args += ["--wait", str(wait)]
        if line_ending:
            args += ["--line-ending", line_ending]
        if column_delimiter:
            args += ["--column-delimiter", column_delimiter]

        return self._run_capturing(
            args,
            label=f"Bulk upserting {object_type}",
            timeout=timeout,
        )

    def upsert_resume(
        self,
        job_id: str | None = None,
        use_most_recent: bool = False,
        wait: int | None = None,
        timeout: int = 600,
    ) -> dict[str, Any]:
        """Resume a bulk upsert job (Bulk API 2.0).

        Provide either ``job_id`` or ``use_most_recent=True``.

        Args:
            job_id: Job ID from a previous ``upsert_bulk`` call.
            use_most_recent: Resume the most recently started bulk upsert job.
            wait: Minutes to wait for completion.
            timeout: Subprocess timeout in seconds.

        Returns:
            Job result dict.
        """
        args = ["data", "upsert", "resume"]
        if job_id:
            args += ["--job-id", job_id]
        if use_most_recent:
            args.append("--use-most-recent")
        if wait is not None:
            args += ["--wait", str(wait)]

        return self._run_capturing(
            args,
            label=f"Resuming bulk upsert job {job_id or '(most recent)'}",
            timeout=timeout,
        )
