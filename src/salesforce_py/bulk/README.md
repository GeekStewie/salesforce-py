# Salesforce Bulk API 2.0 support

`salesforce_py.bulk` is an async client for the Salesforce **Bulk API 2.0** — the family of endpoints served under `/services/data/vXX.X/jobs/`. It covers the full ingest and query lifecycle documented in the Bulk API 2.0 Developer Guide.

It is built on [httpx](https://www.python-httpx.org/) and [DuckDB](https://duckdb.org/), and is fully async. HTTP/2 is negotiated by default, with transparent fallback to HTTP/1.1 for edges that do not support it.

- [Installation](#installation)
- [Why Bulk API 2.0](#why-bulk-api-20)
- [Getting an access token](#getting-an-access-token)
- [Client lifecycle](#client-lifecycle)
- [Ingest (write) lifecycle](#ingest-write-lifecycle)
- [Query (read) lifecycle](#query-read-lifecycle)
- [Automatic `ORDER BY` handling](#automatic-order-by-handling)
- [Known limits and validation](#known-limits-and-validation)
- [Error handling](#error-handling)
- [HTTP/2](#http2)
- [API versioning](#api-versioning)
- [Testing](#testing)

## Installation

The Bulk client lives behind the `bulk` extra because it pulls in `httpx` (for HTTP) and `duckdb` (for client-side `ORDER BY` re-sort on query results):

```bash
pip install "salesforce-py[bulk]"
# or with uv
uv add "salesforce-py[bulk]"
```

Everything at once:

```bash
pip install "salesforce-py[all]"
```

## Why Bulk API 2.0

Bulk API 2.0 is the modern replacement for the original Bulk API. It is simpler to use (one CSV upload per job, no manual batch sizing), supports the same 150 million records per day ceiling, and exposes a cleaner lifecycle. `salesforce_py.bulk` only targets 2.0 — if you need the 1.0 primitive batch model, use a different client.

## Getting an access token

Three factory methods cover the common authentication scenarios — identical in shape to the other `salesforce_py` clients.

### `from_env` — environment variables (recommended for CI/CD)

Set environment variables and call `from_env()`. Credentials are resolved in this order:

1. **Client credentials** — if `SF_BULK_CLIENT_ID` and `SF_BULK_CLIENT_SECRET` are both set, a `client_credentials` OAuth token is minted automatically. The My Domain URL is read from `SF_BULK_INSTANCE_URL`, with `SF_INSTANCE_URL` as a fallback.
2. **SF CLI session** — if `target_org` is passed and env creds are absent, credentials are read from the SF CLI auth store.
3. Raises `SalesforcePyError` if neither path succeeds.

```bash
export SF_BULK_CLIENT_ID="<consumer-key>"
export SF_BULK_CLIENT_SECRET="<consumer-secret>"
export SF_BULK_INSTANCE_URL="https://myorg.my.salesforce.com"
```

```python
from salesforce_py.bulk import BulkClient

async with await BulkClient.from_env() as client:
    job = await client.ingest.create_job(object_name="Account", operation="insert")
```

Or fall back to the SF CLI (no env creds needed):

```python
async with await BulkClient.from_env("my-org-alias") as client:
    ...
```

### `from_org` — SF CLI session

```python
from salesforce_py.sf import SFOrgTask
from salesforce_py.bulk import BulkClient

task = SFOrgTask("my-org-alias")
async with BulkClient.from_org(task._org) as client:
    ...
```

### Direct construction

```python
async with BulkClient(
    instance_url="https://myorg.my.salesforce.com",
    access_token="<bearer-token>",
) as client:
    ...
```

## Client lifecycle

`BulkClient` is best used as an async context manager:

```python
from salesforce_py.bulk import BulkClient

async with BulkClient(instance_url, access_token) as client:
    result_csv = await client.query.run_query("SELECT Id, Name FROM Account LIMIT 50")
```

Or manage the lifecycle manually with `open()` / `close()`.

Constructor parameters:

| Name | Default | Description |
|---|---|---|
| `instance_url` | — | Org My Domain URL. |
| `access_token` | — | OAuth bearer token. |
| `api_version` | `DEFAULT_API_VERSION` | Salesforce API version string, e.g. `"66.0"`. |
| `timeout` | `120.0` | Default request timeout in seconds. |
| `http2` | `True` | Negotiate HTTP/2 when the server supports it. |

The client exposes two namespaces:

| Namespace | URL family |
|---|---|
| `client.ingest` | `/services/data/vXX.X/jobs/ingest/` — CSV write jobs |
| `client.query` | `/services/data/vXX.X/jobs/query/` — SOQL read jobs |

## Ingest (write) lifecycle

A typical ingest job goes through five states: `Open` → `UploadComplete` → `InProgress` → (`JobComplete` | `Failed` | `Aborted`).

### Step-by-step

```python
async with BulkClient(instance_url, access_token) as client:
    # 1. Create the job — state=Open
    job = await client.ingest.create_job(
        object_name="Account",
        operation="insert",
        column_delimiter="COMMA",
        line_ending="LF",
    )
    job_id = job["id"]

    # 2. Upload CSV — PUT to the job's contentUrl
    await client.ingest.upload_data(
        job_id,
        csv_data=b"Name,Industry\nAcme,Retail\nBeta,Tech\n",
        content_url=job["contentUrl"],
    )

    # 3. Flip the job to UploadComplete
    await client.ingest.upload_complete(job_id)

    # 4. Poll until terminal state
    while True:
        status = await client.ingest.get_job(job_id)
        if status["state"] in ("JobComplete", "Failed", "Aborted"):
            break

    # 5. Download outcome CSVs
    successful = await client.ingest.get_successful_results(job_id)
    failed = await client.ingest.get_failed_results(job_id)
    unprocessed = await client.ingest.get_unprocessed_results(job_id)

    # 6. Clean up
    await client.ingest.delete_job(job_id)
```

### Supported operations

| `operation` | Behavior |
|---|---|
| `insert` | Create new records. |
| `update` | Update by `Id`. |
| `upsert` | Upsert by the `external_id_field` (required). |
| `delete` | Soft-delete by `Id`. |
| `hardDelete` | Permanently delete by `Id` (requires "Bulk API Hard Delete" permission). |

### Upsert convenience wrapper

The most common pattern — create + upload + close an upsert job — is bundled into `ingest.upsert()`:

```python
await client.ingest.upsert(
    object_name="Account",
    external_id_field="ExtId__c",
    csv_data=b"ExtId__c,Name\nA1,Acme\nB2,Beta\n",
)
```

### Other ingest helpers

| Method | Purpose |
|---|---|
| `get_all_jobs(...)` | List ingest jobs with optional filters. |
| `abort_job(job_id)` | Cancel an in-flight job. |
| `delete_job(job_id)` | Remove a terminated job and its results. |

## Query (read) lifecycle

Query jobs follow a similar lifecycle, but result data is downloaded from paginated `/results` endpoints. Pages are delimited by the `Sforce-Locator` response header.

### End-to-end with `run_query`

`run_query` is the simplest entry point — it handles the full lifecycle including polling, multi-page download, and (if applicable) client-side `ORDER BY` re-sort:

```python
csv_bytes = await client.query.run_query(
    "SELECT Id, Name FROM Account ORDER BY CreatedDate DESC LIMIT 10000",
    poll_interval=3.0,
    poll_timeout=1800.0,
    auto_delete=True,
)
```

### Manual lifecycle

When you need per-page streaming or parallel downloads, drive the lifecycle yourself:

```python
# 1. Submit the query — ORDER BY is stripped automatically
job = await client.query.create_job(
    soql="SELECT Id, Name FROM Account ORDER BY CreatedDate DESC",
    operation="query",           # or "queryAll" to include soft-deleted records
)
job_id = job["id"]
order_by = job["_stripped_order_by"]  # captured OrderByClause, may be None

# 2. Poll
while True:
    status = await client.query.get_job(job_id)
    if status["state"] == "JobComplete":
        break

# 3a. Serial download
csv_bytes = await client.query.get_all_results(
    job_id,
    order_by=order_by,           # reapplies ORDER BY via DuckDB
)

# 3b. Page-by-page (manual pagination)
locator = None
while True:
    page, locator, record_count = await client.query.get_results(
        job_id,
        locator=locator,
        max_records=50_000,
    )
    process(page)
    if locator is None:
        break

# 3c. Parallel (API 58.0+) — /resultPages
import asyncio
locators = await client.query.get_parallel_results(job_id)
pages = await asyncio.gather(*[
    client.query.get_results(job_id, locator=loc) for loc in locators
])
```

### Other query helpers

| Method | Purpose |
|---|---|
| `get_all_jobs(...)` | List query jobs. |
| `abort_job(job_id)` | Cancel a running query. |
| `delete_job(job_id)` | Remove a terminated query and its cached results. |

## Automatic `ORDER BY` handling

Bulk API 2.0 **disables PK chunking** when a SOQL query contains `ORDER BY`, which can push large queries into timeouts. `salesforce_py.bulk` handles this for you:

1. `create_job` calls `prepare_query(soql)` which strips the `ORDER BY` clause (preserving any `LIMIT` after it) and captures the sort keys as an `OrderByClause` dataclass.
2. The captured clause is attached to the returned job dict as `_stripped_order_by`.
3. `get_all_results` (and `run_query`) reapplies the sort locally via DuckDB after concatenating the paginated CSV pages.

Example:

```python
from salesforce_py.bulk import prepare_query

prepared = prepare_query(
    "SELECT Id FROM Contact ORDER BY LastName ASC, CreatedDate DESC NULLS LAST LIMIT 5000"
)
print(prepared.soql)
# 'SELECT Id FROM Contact LIMIT 5000'

print(prepared.order_by.columns)
# (('LastName', 'ASC', None), ('CreatedDate', 'DESC', 'LAST'))
```

SOQL constructs that Bulk API 2.0 does **not** support are rejected client-side with a clear `ValueError` instead of a cryptic server error:

- `GROUP BY`
- `OFFSET`
- `TYPEOF`
- Aggregate functions (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`)

## Known limits and validation

`salesforce_py.bulk` validates what it can before dispatching the request, so callers get a clear client-side error instead of an opaque server rejection. Documented Bulk 2.0 ceilings are exposed as constants:

| Constant | Value | Meaning |
|---|---|---|
| `MAX_UPLOAD_BYTES_BASE64` | 150 MB | Server-side limit after base64 encoding. |
| `MAX_UPLOAD_BYTES_RAW` | 100 MB | Safe raw-upload ceiling (validated client-side). |
| `MAX_CSV_HEADER_CHARS` | 32,000 | Maximum header-row length. |
| `INGEST_RECORDS_PER_BATCH` | 10,000 | Server-side batch granularity. |
| `DAILY_INGEST_RECORD_LIMIT` | 150,000,000 | Org-wide daily ingest cap (enforced server-side). |

Enumerations:

| Constant | Values |
|---|---|
| `INGEST_OPERATIONS` | `insert`, `update`, `upsert`, `delete`, `hardDelete` |
| `QUERY_OPERATIONS` | `query`, `queryAll` |
| `COLUMN_DELIMITERS` | `BACKQUOTE`, `CARET`, `COMMA`, `PIPE`, `SEMICOLON`, `TAB` |
| `LINE_ENDINGS` | `LF`, `CRLF` |

```python
from salesforce_py.bulk import (
    MAX_UPLOAD_BYTES_RAW,
    INGEST_OPERATIONS,
    COLUMN_DELIMITERS,
)
```

## Error handling

| Status | Exception |
|---|---|
| `401` | `AuthError` |
| `4xx` / `5xx` | `SalesforcePyError` (carries the first 500 chars of the body) |
| Non-JSON 2xx body | `SalesforcePyError` |
| Transient (408, 429, 5xx) | One automatic retry after 20 s, then surfaced as `SalesforcePyError` |

```python
from salesforce_py.exceptions import AuthError, SalesforcePyError

try:
    await client.query.run_query("SELECT Id FROM Account")
except AuthError:
    # token expired — refresh and retry
    ...
except SalesforcePyError as e:
    print("Bulk API failed:", e)
```

Client-side validation errors (unknown operation, delimiter, line ending, oversized upload, unsupported SOQL construct) raise `ValueError` **before** any HTTP call.

## HTTP/2

HTTP/2 is negotiated by default. Disable it only if you have a specific reason (debugging, HTTP/2-mangling proxy, etc.):

```python
client = BulkClient(instance_url, access_token, http2=False)
```

The `h2` package is pulled in automatically by the `bulk`, `data360`, `connect`, `rest`, and `all` extras.

## API versioning

`BulkClient` defaults to `salesforce_py.DEFAULT_API_VERSION`. Override per-client when you need to pin to a specific release:

```python
client = BulkClient(instance_url, access_token, api_version="66.0")
```

The version string is embedded directly into the session base URL (`/services/data/v66.0/jobs/...`), so it applies to every call made through the client.

Parallel query result downloads via `/resultPages` require **API 58.0 or later**.

## Testing

The test suite in `tests/bulk/` covers the client with mocked `httpx.Response` objects — no network calls. DuckDB is exercised against in-memory CSV fixtures. Run it with:

```bash
uv sync --extra dev --extra bulk
uv run pytest tests/bulk
```
