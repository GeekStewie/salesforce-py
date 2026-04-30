# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install all deps including dev
uv sync --extra dev

# Install with specific extras
uv sync --extra dev --extra rest        # REST API client (SOQL/SOSL, sObjects, composite, tooling, UI API, ...)
uv sync --extra dev --extra connect     # Connect REST API client
uv sync --extra dev --extra data360     # Data 360 Connect REST API client
uv sync --extra dev --extra models      # Models (Einstein generative AI) REST API client
uv sync --extra dev --extra bulk        # Bulk API 2.0 client (ingest + query with duckdb)
uv sync --extra dev --extra all         # everything

# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/sf/test_runner.py

# Run a single test by name
uv run pytest tests/sf/test_runner.py::test_cli_not_found

# Run the Connect test suite (needs the `connect` extra)
uv run pytest tests/connect

# Lint
uv run ruff check src/

# Format
uv run ruff format src/

# Type check
uv run ty check src/

# Build distribution
uv build

# Publish to PyPI (requires ~/.pypirc with token)
uv build && uv publish

# Bump version then publish
uv run hatch version patch   # or minor / major
uv build && uv publish
```

## Architecture

salesforce-py ships six independent clients that target different Salesforce surfaces. They share `salesforce_py.exceptions` and `salesforce_py.utils`, but are otherwise unrelated:

- `salesforce_py.sf` — sync wrapper around the `sf` CLI (subprocess-based)
- `salesforce_py.rest` — async HTTP client for the core Salesforce REST API (httpx-based)
- `salesforce_py.connect` — async HTTP client for the Connect REST API (httpx-based)
- `salesforce_py.data360` — async HTTP client for the Data 360 (CDP) Connect REST API (httpx-based)
- `salesforce_py.models` — async HTTP client for the Einstein Models REST API (httpx-based)
- `salesforce_py.bulk` — async HTTP client for the Bulk API 2.0 (httpx + duckdb for client-side sort)

`salesforce_py._defaults.DEFAULT_API_VERSION` is the single source of truth for the fallback API version used by all clients.

### Retry + timeout defaults (`salesforce_py/_retry.py`)

All callouts — HTTP requests and `sf` CLI subprocesses — share one retry shape, defined in `salesforce_py._retry`:

- **Default timeout**: `DEFAULT_TIMEOUT = 120.0` seconds, applied to every `httpx.AsyncClient`, every `sf` subprocess, and the Models token fetch. Individual operations may override with a shorter or longer timeout when there is a concrete requirement (e.g. install scripts, cheap version probes).
- **HTTP retry**: one retry after `HTTP_RETRY_DELAY = 20.0` seconds on transient failures — transport errors (`httpx.TimeoutException`, `ConnectError`, etc.) or responses with status in `RETRYABLE_STATUSES = {408, 420, 425, 429, 500, 502, 503, 504}`. `AuthError` (401) and other 4xx statuses are **not** retried.
- **CLI retry**: one retry after `CLI_RETRY_DELAY = 10.0` seconds on `subprocess.TimeoutExpired` / `asyncio.TimeoutError`. `CLINotFoundError` and `CLIError` are **not** retried.
- After a transient-response retry is exhausted, the final response is handed back to the client's `_handle` layer so `SalesforcePyError` surfaces with the body attached (rather than a raw tenacity `RetryError`).

Retry machinery is built on `tenacity` (`AsyncRetrying` / `Retrying` with `wait_fixed` + `stop_after_attempt(2)` + `retry_if_exception`). Helpers: `retry_async_http_call` (wraps each `_get/_post/...` in `RestBaseOperations`, `ConnectBaseOperations`, `Data360BaseOperations`, `ModelsBaseOperations`, `BulkBaseOperations`, plus the Models `fetch_token` call), `retry_sync_cli` (wraps `subprocess.run` in `SFBaseOperations._run`), `retry_async_cli` (wraps each attempt in `sf/_runner.py::run`).

### SF CLI wrapper (`salesforce_py/sf/`)

Two parallel execution models coexist:

**Async runner** (`sf/_runner.py`): Low-level, stateless. Takes a list of args, prepends `sf`, appends `--json`, runs via `asyncio.create_subprocess_exec`. Used when callers need concurrency. `run_sync` wraps it via `asyncio.run()`.

**Sync org-bound layer** (`sf/org.py` → `sf/base.py` → `sf/operations/*`): Higher-level, stateful. Binds all commands to a specific org. This is the primary API for most users:

```
SFOrgTask          # sf/task.py — user-facing entry point, one per org
  └── SFOrg        # sf/org.py — holds credentials, builds env dict
  └── SF*Operations # sf/operations/*.py — one class per sf command group
        └── SFBaseOperations  # sf/base.py — _run() / _run_capturing() dispatch
```

`SFOrg` connects lazily: the first `_ensure_connected()` call runs `sf org display` and populates `instance_url`, `access_token`, `username`, etc. It also builds the isolated env dict (`_SF_ENV_DEFAULTS` + org credentials) passed to every subprocess — `os.environ` is never mutated.

`SFBaseOperations._run()` calls `_build_cmd()` which appends `--json`, `--target-org`, and `--api-version` (read from `sfdx-project.json` by walking up from cwd, falling back to `DEFAULT_API_VERSION`). All subprocess calls use `shell=True` with the org env.

`_run_capturing()` wraps `_run()` and emits `logging.info/error` around the call — operations use this for user-visible progress.

`SFCLISetup` (`sf/setup.py`) is exposed alongside `SFOrg` / `SFOrgTask` for install / plugin management flows.

### Adding a new SF operation class

1. Create `src/salesforce_py/sf/operations/mycommand.py` subclassing `SFBaseOperations`
2. Each method calls `self._run(["mycommand", "sub", ...])` or `self._run_capturing(..., label="...")`
3. Set `include_target_org=False` for commands that are not org-scoped (e.g. alias, config)
4. Set `include_json=False` for streaming commands that don't support `--json` (e.g. `apex tail log`) — these return `{"output": "<raw stdout>"}`
5. Add the class to `sf/operations/__init__.py` and wire it into `SFOrgTask` in `sf/task.py`

### REST API client (`salesforce_py/rest/`)

Async client for `/services/data/vXX.X/` — the core Salesforce REST API surface. Covers SOQL / SOSL queries, every `/sobjects/...` resource, the composite / batch / graph / tree families, quick actions, invocable actions, tooling, UI API, analytics, process / approvals, support, and the rest. Built on `httpx` with HTTP/2 negotiated by default.

```
RestClient              # rest/client.py — user-facing entry point
  ├── RestSession       # rest/_session.py — single httpx.AsyncClient
  │                     #   bound to /services/data/v{api_version}/
  └── *Operations       # rest/operations/*.py — one class per endpoint family
        └── RestBaseOperations  # rest/base.py — _get/_post/_patch/_put/_delete/_get_bytes
```

`RestClient` is token-driven — callers supply `instance_url` + `access_token` (no OAuth flow is performed by the client itself; `from_env` uses the `REST` env-var prefix to mint a client-credentials token when needed). Use it as an async context manager or call `open()` / `close()` manually. It owns a single `RestSession`, since every top-level REST resource is addressable under the version-scoped base URL.

`RestBaseOperations._handle()` maps `401 → AuthError`, other `4xx/5xx → SalesforcePyError` (carrying the first 500 chars of the body), returns `{}` for `204` / empty bodies, and unwraps JSON otherwise. `_get_bytes` returns the raw response for binary endpoints (attachment blobs, rich-text images).

The un-versioned `/services/data` root (list of available API versions) is addressed by `VersionsOperations.list_versions()` via an absolute URL built against the instance URL, since it is not under the version-scoped base path.

For small-surface namespaces (consent, dedupe, contact-tracing, licensing, scheduling, etc.), `rest/operations/misc.py` uses a `_make_passthrough(namespace)` factory to generate thin wrappers with generic `get/post/patch/put/delete` methods that prepend the namespace's base path. This lets callers hit any sub-resource without waiting for a dedicated helper.

#### Adding a new REST operation class

1. Create `src/salesforce_py/rest/operations/mynamespace.py` subclassing `RestBaseOperations`
2. Each method calls `await self._get(path, ...)`, `_post`, `_patch`, `_put`, `_delete`, or `_get_bytes` with `params=` / `json=` / `headers=` kwargs
3. Paths are relative to `/services/data/vXX.X/` — e.g. `"sobjects/Account/describe"`, not `"/services/data/v66.0/sobjects/Account/describe"`
4. Export the class from `rest/operations/__init__.py` and wire it into `RestClient.__init__`

See `src/salesforce_py/rest/README.md` for the full namespace map and usage examples.

### Connect REST API client (`salesforce_py/connect/`)

Async client for `/services/data/vXX.X/connect/`, `/einstein/`, and sibling families (`commerce/`, `communities/`, `named-credentials/`, etc.). Built on `httpx` with HTTP/2 negotiated by default.

```
ConnectClient           # connect/client.py — user-facing entry point
  ├── ConnectSession    # connect/_session.py — httpx.AsyncClient per base path
  │                     #   (one each for connect/, einstein/, and the empty root)
  └── *Operations       # connect/operations/*.py — one class per endpoint family
        └── ConnectBaseOperations  # connect/base.py — _get/_post/_patch/_put/_delete
```

`ConnectClient` is token-driven — callers supply `instance_url` + `access_token` (no OAuth flow is performed). Use it as an async context manager or call `open()` / `close()` manually. It owns three `ConnectSession` instances; one for each base path, all opened/closed together.

`ConnectBaseOperations._handle()` maps `401 → AuthError`, other `4xx/5xx → SalesforcePyError` (carrying the first 500 chars of the body), and unwraps JSON. `_ensure_18` / `_ensure_18_list` normalise 15-char IDs to 18-char on every call; non-IDs (`"me"`, asset names, emails) pass through unchanged.

#### Adding a new Connect operation class

1. Create `src/salesforce_py/connect/operations/mynamespace.py` subclassing `ConnectBaseOperations`
2. Each method calls `await self._get(path, ...)`, `_post`, `_patch`, `_put`, `_delete`, or `_get_bytes` for binary responses
3. Pass the correct session when wiring into `ConnectClient.__init__` — `self._session` for `/connect/`, `self._einstein_session` for `/einstein/`, `self._data_session` for everything under the plain `/services/data/vXX.X/` root (commerce, communities via `_data_session` patterns, named-credentials, etc.)
4. Export the class from `connect/operations/__init__.py` and wire it into `ConnectClient`

See `src/salesforce_py/connect/README.md` for the full namespace map and usage examples.

### Data 360 client (`salesforce_py/data360/`)

Async client for `/services/data/vXX.X/ssot/` (Data 360 / CDP). Built on `httpx` with HTTP/2 negotiated by default.

```
Data360Client           # data360/client.py — user-facing entry point
  ├── Data360Session    # data360/_session.py — single httpx.AsyncClient bound to /ssot/
  └── *Operations       # data360/operations/*.py — one class per endpoint tag group
        └── Data360BaseOperations  # data360/base.py — _get/_post/_patch/_put/_delete
```

`Data360Client` is token-driven and owns a single `Data360Session` (all Data 360 endpoints share the `/ssot/` base path, so no multi-session fanout is needed). The base class drops `None`-valued query params before dispatch so callers can pass `None` for unspecified filters. There is no 15→18-char ID normalisation — Data 360 APIs key on developer names and UUIDs, not standard 15-char sObject IDs.

#### Adding a new Data 360 operation class

1. Create `src/salesforce_py/data360/operations/mynamespace.py` subclassing `Data360BaseOperations`
2. Each method calls `await self._get(path, params=...)`, `_post`, `_patch`, `_put`, or `_delete` with `params=` / `json=` / `headers=` kwargs
3. Export the class from `data360/operations/__init__.py` and wire it into `Data360Client.__init__`

See `src/salesforce_py/data360/README.md` for the full namespace map and usage examples.

### Models REST API client (`salesforce_py/models/`)

Async client for the Einstein Models REST API served from `https://api.salesforce.com/einstein/platform/v1/` (or the geo-routed `api_instance_url` returned by the token endpoint). Covers the four documented capabilities: chat-generations, generations, embeddings, feedback.

```
ModelsClient            # models/client.py — user-facing entry point
  ├── ModelsSession     # models/_session.py — single httpx.AsyncClient
  │                     #   bound to https://api.salesforce.com/einstein/platform/v1/
  │                     #   with x-sfdc-app-context + x-client-feature-id headers
  └── *Operations       # models/operations/*.py — one class per capability
        └── ModelsBaseOperations  # models/base.py — _get/_post only
```

`ModelsClient` is **not** org-instance-bound: the API host is constant (or the geo-routed `api_instance_url` from the token response), and there's no `{apiVersion}` path segment, so `DEFAULT_API_VERSION` does not apply here. Auth is a dedicated **client-credentials** flow against `{my_domain}/services/oauth2/token` — `salesforce_py.models.fetch_token` performs that call and returns a `TokenResponse` dataclass. The client only does GET and POST because the Models API has no PATCH/PUT/DELETE endpoints.

Supported-model API names are exported as string constants from `salesforce_py.models.supported_models` (`GPT_4_OMNI_MINI`, `BEDROCK_ANTHROPIC_CLAUDE_46_SONNET`, etc.). BYOLLM model API names work too — pass any string.

#### Adding a new Models operation class

1. Create `src/salesforce_py/models/operations/mynamespace.py` subclassing `ModelsBaseOperations`
2. Each method calls `await self._get(path, ...)` or `_post(path, json=...)` — no PATCH/PUT/DELETE support
3. Export the class from `models/operations/__init__.py` and wire it into `ModelsClient.__init__`

See `src/salesforce_py/models/README.md` for usage examples and the rate-limit table.

### Bulk API 2.0 client (`salesforce_py/bulk/`)

Async client for `/services/data/vXX.X/jobs/` — the ingest (CSV write) and query (SOQL read) surface of Bulk API 2.0.

```
BulkClient              # bulk/client.py — user-facing entry point
  ├── BulkSession       # bulk/_session.py — single httpx.AsyncClient
  │                     #   bound to /services/data/vXX.X/jobs/
  ├── IngestOperations  # bulk/operations/ingest.py — /jobs/ingest/ lifecycle
  └── QueryOperations   # bulk/operations/query.py — /jobs/query/ lifecycle
        └── BulkBaseOperations  # bulk/base.py — JSON helpers + _put_csv/_get_csv
```

`BulkClient` is token-driven, mirrors the `Data360Client` / `ConnectClient` shape (`from_env` uses the `BULK` prefix), and owns a single `BulkSession` — both `/jobs/ingest/` and `/jobs/query/` share the same base URL.

**Ingest lifecycle** (`client.ingest`): `create_job` → `upload_data` (PUT CSV to `contentUrl`, client-side-validated against the 100 MB raw / 150 MB base64 ceiling) → `upload_complete` (PATCH to `UploadComplete`) → poll `get_job` → download `get_successful_results` / `get_failed_results` / `get_unprocessed_results` → `delete_job`. `upsert(object_name, external_id_field, csv_data, ...)` is a convenience wrapper that chains create + upload + complete in one call.

**Query lifecycle** (`client.query`): `create_job` automatically strips `ORDER BY` from the submitted SOQL (since it disables PK chunking) and captures the clause as `job["_stripped_order_by"]` — an `OrderByClause` dataclass parsed into `(expression, direction, nulls)` tuples. `run_query(soql, ...)` is the end-to-end helper: submit → poll → download all pages via `get_all_results` → reapply the captured `ORDER BY` client-side via DuckDB → return combined CSV bytes. `get_parallel_results` returns `/resultPages` locator cursors (API 58.0+) for concurrent page download.

**Limits + validation** (`bulk/_limits.py`): constants (`MAX_UPLOAD_BYTES_RAW`, `INGEST_RECORDS_PER_BATCH`, `DAILY_INGEST_RECORD_LIMIT`, etc.), frozensets (`INGEST_OPERATIONS`, `QUERY_OPERATIONS`, `COLUMN_DELIMITERS`, `LINE_ENDINGS`), and `validate_*` helpers called by the operations classes to fail fast with clear client-side errors instead of opaque server rejections.

**SOQL prep** (`bulk/_soql.py`): `prepare_query(soql) → PreparedQuery(soql=..., order_by=...)` strips `ORDER BY` up to the next `LIMIT`/`OFFSET`/`FOR VIEW`/`UPDATE TRACKING` boundary and runs `validate_soql` to reject constructs Bulk 2.0 doesn't support (`GROUP BY`, `OFFSET`, `TYPEOF`, aggregates like `COUNT()`/`SUM()`).

**DuckDB helpers** (`bulk/_duckdb.py`): `concatenate_csv_pages(pages, line_ending)` joins paginated CSV pages into a single payload (preserving the header from page 1, stripping it from subsequent pages); `apply_order_by(csv_data, order_by, column_delimiter, line_ending)` round-trips through DuckDB to reapply the sort — lazy-imported so the module is usable even if DuckDB is absent (as long as no query uses `ORDER BY`).

#### Adding a new Bulk operation class

1. Create `src/salesforce_py/bulk/operations/mynamespace.py` subclassing `BulkBaseOperations`
2. Use `_get/_post/_patch/_delete` for JSON endpoints, `_put_csv(path, data=...)` for CSV uploads, `_get_csv(path, params=...)` for CSV downloads (returns the raw `httpx.Response` so callers can read `Sforce-Locator` / `Sforce-NumberOfRecords` headers)
3. Validate inputs against the whitelists in `bulk/_limits.py` before submission
4. Export the class from `bulk/operations/__init__.py` and wire it into `BulkClient.__init__`

## Exceptions

All exceptions live in `salesforce_py/exceptions.py`:

`SalesforcePyError` (base) → `CLINotFoundError` (sf not on PATH) → `CLIError` (non-zero sf exit, carries `returncode`, `stdout`, `stderr`) → `AuthError` (OAuth / 401).

- `CLIError` is raised by both `_runner.run` (async sf path) and `SFBaseOperations._run` (sync sf path).
- `AuthError` is raised by `RestBaseOperations._handle_status`, `ConnectBaseOperations._handle_status`, `Data360BaseOperations._handle_status`, `ModelsBaseOperations._handle_status`, and `BulkBaseOperations._handle_status` on a 401 response, and by `salesforce_py.models.fetch_token` on 400/401 token-endpoint failures.
- `SalesforcePyError` covers everything else (non-JSON response, non-2xx status, timeouts, etc.).

## Utilities (`salesforce_py/utils/`)

- `convert_to_18_char(sf_id)` — 15-char to 18-char ID conversion
- `get_object_type(sf_id)` — sObject name lookup via the key prefix table in `utils/data/object_prefixes.json`

Both are re-exported from `salesforce_py.utils`.

## Optional dependencies

`pyproject.toml` defines these extras:

- `connect` — `httpx[http2]`. Required for `salesforce_py.connect`. The package raises a helpful `ImportError` at import time if it is missing.
- `data360` — `httpx[http2]`. Required for `salesforce_py.data360`. The package raises a helpful `ImportError` at import time if it is missing.
- `models` — `httpx[http2]`. Required for `salesforce_py.models`. The package raises a helpful `ImportError` at import time if it is missing.
- `bulk` — `httpx[http2]`, `aiofiles`, and `duckdb`. Required for `salesforce_py.bulk`; `duckdb` powers the client-side `ORDER BY` re-sort for query results.
- `rest` — `httpx[http2]`. Required for `salesforce_py.rest`. The package raises a helpful `ImportError` at import time if it is missing.
- `code-analyzer` — `ruamel.yaml`, used by `SFCodeAnalyzerManager`. Import-guarded.
- `all` — union of `httpx[http2]`, `aiofiles`, `duckdb`, `ruamel.yaml`.
- `dev` — `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`, `ty`, `httpx[http2]`, and `duckdb` (so the REST + Connect + Data 360 + Models + Bulk tests run under `dev`).

## Package layout

- `src/salesforce_py/sf/` — SF CLI wrapper (sync + async)
- `src/salesforce_py/rest/` — REST API client (async, httpx)
- `src/salesforce_py/connect/` — Connect REST API client (async)
- `src/salesforce_py/data360/` — Data 360 (CDP) Connect REST API client (async)
- `src/salesforce_py/models/` — Einstein Models REST API client (async)
- `src/salesforce_py/bulk/` — Bulk API 2.0 client (async, httpx + duckdb)
- `src/salesforce_py/utils/` — shared ID helpers + `utils/data/object_prefixes.json`
- `src/salesforce_py/exceptions.py` — all exceptions
- `src/salesforce_py/_defaults.py` — `DEFAULT_API_VERSION`
- `tests/sf/` — SF CLI tests; `conftest.py` provides a `mock_runner` fixture patching `salesforce_py.sf._runner.run`
- `tests/rest/` — REST API tests; fixtures patch `RestSession`'s underlying `httpx.AsyncClient` so individual tests assert on URL, params, and JSON payload
- `tests/connect/` — Connect API tests; fixtures patch `ConnectSession`'s underlying `httpx.AsyncClient` so individual tests assert on URL, params, and JSON payload
- `tests/data360/` — Data 360 API tests; same pattern as `tests/connect/`, patching the per-call session methods on `Data360Client`
- `tests/models/` — Models API tests; same pattern as `tests/data360/`, patching session verbs on `ModelsClient`, plus mocked `httpx.AsyncClient` for the token helper
- `tests/bulk/` — Bulk API tests; patches session verbs on `BulkClient`, mocks `Sforce-Locator` pagination headers, and exercises `_soql.prepare_query` + the DuckDB sort round-trip
- `tests/utils/` — utility helper tests
