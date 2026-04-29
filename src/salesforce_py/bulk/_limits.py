"""Known limits and enumerations for the Salesforce Bulk API 2.0.

Source: Bulk API 2.0 and Bulk API Developer Guide, Spring '26 (API 66.0).
These are the documented ceilings the client validates client-side before
submitting, plus the enumerated vocabularies used by job properties.

Only a subset of limits can be enforced before a callout — things like the
150M-records-per-day quota are checked server-side and surface as
``ExceededQuota``. The constants below are exposed so callers can plan
batches without hardcoding magic numbers.
"""

from __future__ import annotations

from typing import Final

# ---------------------------------------------------------------------------
# Size limits
# ---------------------------------------------------------------------------

#: Maximum upload size per ingest job *after* base64 encoding.
MAX_UPLOAD_BYTES_BASE64: Final[int] = 150 * 1024 * 1024  # 150 MB

#: Practical maximum raw CSV size before the server-side base64 conversion
#: pushes it over :data:`MAX_UPLOAD_BYTES_BASE64`. Salesforce recommends
#: keeping raw payloads under 100 MB.
MAX_UPLOAD_BYTES_RAW: Final[int] = 100 * 1024 * 1024  # 100 MB

#: Maximum header-row size in a CSV file.
MAX_CSV_HEADER_CHARS: Final[int] = 32_000

#: Server-side batch granularity — Salesforce divides ingest data into
#: batches of this size for internal processing.
INGEST_RECORDS_PER_BATCH: Final[int] = 10_000

# ---------------------------------------------------------------------------
# Daily quotas (informational; enforced server-side via ExceededQuota)
# ---------------------------------------------------------------------------

#: Maximum records processed per 24-hour period across all ingest jobs.
DAILY_INGEST_RECORD_LIMIT: Final[int] = 150_000_000

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

#: Ingest operations supported by Bulk API 2.0.
INGEST_OPERATIONS: Final[frozenset[str]] = frozenset(
    {"insert", "update", "upsert", "delete", "hardDelete"}
)

#: Query operations supported by Bulk API 2.0.
QUERY_OPERATIONS: Final[frozenset[str]] = frozenset({"query", "queryAll"})

#: Valid ``columnDelimiter`` values for CSV job data.
COLUMN_DELIMITERS: Final[frozenset[str]] = frozenset(
    {"BACKQUOTE", "CARET", "COMMA", "PIPE", "SEMICOLON", "TAB"}
)

#: Valid ``lineEnding`` values for CSV job data.
LINE_ENDINGS: Final[frozenset[str]] = frozenset({"LF", "CRLF"})

#: Valid terminal states for a job that can be deleted.
DELETABLE_STATES: Final[frozenset[str]] = frozenset(
    {"UploadComplete", "JobComplete", "Aborted", "Failed"}
)

#: States in which an ingest or query job can be aborted.
ABORTABLE_STATES: Final[frozenset[str]] = frozenset({"UploadComplete", "InProgress", "Open"})


def validate_operation(operation: str) -> str:
    """Return *operation* unchanged if it is a valid ingest operation.

    Raises:
        ValueError: If *operation* is not one of :data:`INGEST_OPERATIONS`.
    """
    if operation not in INGEST_OPERATIONS:
        raise ValueError(
            f"Invalid ingest operation {operation!r}. Must be one of: {sorted(INGEST_OPERATIONS)}."
        )
    return operation


def validate_query_operation(operation: str) -> str:
    """Return *operation* unchanged if it is a valid query operation.

    Raises:
        ValueError: If *operation* is not one of :data:`QUERY_OPERATIONS`.
    """
    if operation not in QUERY_OPERATIONS:
        raise ValueError(
            f"Invalid query operation {operation!r}. Must be one of: {sorted(QUERY_OPERATIONS)}."
        )
    return operation


def validate_column_delimiter(delimiter: str) -> str:
    if delimiter not in COLUMN_DELIMITERS:
        raise ValueError(
            f"Invalid columnDelimiter {delimiter!r}. Must be one of: {sorted(COLUMN_DELIMITERS)}."
        )
    return delimiter


def validate_line_ending(line_ending: str) -> str:
    if line_ending not in LINE_ENDINGS:
        raise ValueError(
            f"Invalid lineEnding {line_ending!r}. Must be one of: {sorted(LINE_ENDINGS)}."
        )
    return line_ending


def validate_upload_size(data: bytes) -> None:
    """Raise if *data* would exceed the documented raw upload ceiling.

    Bulk API 2.0 rejects uploads larger than 150 MB after server-side
    base64 encoding. Since base64 inflates payloads by ~33 %, the safe
    raw ceiling is ~100 MB. We check the raw size here so callers get a
    clear client-side error instead of a server-side ``InvalidBatch``.

    Raises:
        ValueError: If ``len(data) > MAX_UPLOAD_BYTES_RAW``.
    """
    size = len(data)
    if size > MAX_UPLOAD_BYTES_RAW:
        raise ValueError(
            f"CSV upload is {size:,} bytes; the documented Bulk API 2.0 raw "
            f"ceiling is {MAX_UPLOAD_BYTES_RAW:,} bytes (≈100 MB). "
            f"Split the data into multiple jobs and upload each separately."
        )
