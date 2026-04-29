"""Salesforce Bulk API 2.0 client.

Async wrapper around the ``/services/data/vXX.X/jobs/`` endpoints — the
ingest (CSV write) and query (SOQL read) surface of Bulk API 2.0.

Key features:

- Ingest lifecycle (``create_job`` → ``upload_data`` → ``upload_complete``
  → poll → download results → ``delete_job``) and an :meth:`upsert`
  convenience wrapper that does all of the above.
- Query lifecycle with automatic ``ORDER BY`` stripping — Bulk 2.0
  disables PK chunking when ``ORDER BY`` is present, so the client
  removes the clause before submission, captures it, and reapplies it
  client-side via DuckDB once the paginated CSV pages are downloaded.
- Client-side validation of documented limits (150 MB base64 / 100 MB raw
  upload ceiling, delimiter / line-ending / operation whitelists).
- Shared retry + HTTP/2 defaults with the other salesforce-py clients.

Install the ``bulk`` extra to unlock this module::

    pip install "salesforce-py[bulk]"
    # or with uv:
    uv add "salesforce-py[bulk]"

The extra pulls in ``httpx[http2]`` (required) and ``duckdb`` (required
for the client-side ``ORDER BY`` re-sort path).
"""

try:
    import httpx as _httpx  # noqa: F401
except ImportError as exc:
    raise ImportError(
        "The 'bulk' extra is required to use salesforce_py.bulk.\n"
        "Install it with:  uv add 'salesforce-py[bulk]'\n"
        "                  pip install 'salesforce-py[bulk]'"
    ) from exc

from salesforce_py.bulk._limits import (
    ABORTABLE_STATES,
    COLUMN_DELIMITERS,
    DAILY_INGEST_RECORD_LIMIT,
    DELETABLE_STATES,
    INGEST_OPERATIONS,
    INGEST_RECORDS_PER_BATCH,
    LINE_ENDINGS,
    MAX_CSV_HEADER_CHARS,
    MAX_UPLOAD_BYTES_BASE64,
    MAX_UPLOAD_BYTES_RAW,
    QUERY_OPERATIONS,
)
from salesforce_py.bulk._soql import OrderByClause, PreparedQuery, prepare_query
from salesforce_py.bulk.client import BulkClient

__all__ = [
    "ABORTABLE_STATES",
    "COLUMN_DELIMITERS",
    "DAILY_INGEST_RECORD_LIMIT",
    "DELETABLE_STATES",
    "INGEST_OPERATIONS",
    "INGEST_RECORDS_PER_BATCH",
    "LINE_ENDINGS",
    "MAX_CSV_HEADER_CHARS",
    "MAX_UPLOAD_BYTES_BASE64",
    "MAX_UPLOAD_BYTES_RAW",
    "QUERY_OPERATIONS",
    "BulkClient",
    "OrderByClause",
    "PreparedQuery",
    "prepare_query",
]
