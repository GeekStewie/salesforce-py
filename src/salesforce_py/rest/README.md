# Salesforce REST API support

`salesforce_py.rest` is an async client for the Salesforce REST API — the family of endpoints served under `/services/data/vXX.X/`: SOQL / SOSL queries, every `/sobjects/...` resource, the composite / batch / graph / tree families, quick actions, invocable actions, tooling, UI API, analytics, process / approvals, support, and the rest.

It is built on [httpx](https://www.python-httpx.org/) and is fully async. HTTP/2 is negotiated by default, with transparent fallback to HTTP/1.1 for edges that do not support it.

- [Installation](#installation)
- [Getting an access token](#getting-an-access-token)
- [Client lifecycle](#client-lifecycle)
- [Operation namespaces](#operation-namespaces)
- [Examples](#examples)
- [Error handling](#error-handling)
- [HTTP/2](#http2)
- [API versioning](#api-versioning)
- [Testing](#testing)

## Installation

The REST API lives behind the `rest` extra because it pulls in `httpx` (and, for HTTP/2, `h2`):

```bash
pip install "salesforce-py[rest]"
# or with uv
uv add "salesforce-py[rest]"
```

Everything at once:

```bash
pip install "salesforce-py[all]"
```

## Getting an access token

Three factory methods cover the common authentication scenarios.

### `from_env` — environment variables (recommended for CI/CD)

Set environment variables and call `from_env()`. Credentials are resolved in this order:

1. **Client credentials** — if `SF_REST_CLIENT_ID` and `SF_REST_CLIENT_SECRET` are both set, a `client_credentials` OAuth token is minted automatically. The My Domain URL is read from `SF_REST_INSTANCE_URL`, with `SF_INSTANCE_URL` as a fallback.
2. **SF CLI session** — if `target_org` is passed and env creds are absent, credentials are read from the SF CLI auth store.
3. Raises `SalesforcePyError` if neither path succeeds.

```bash
export SF_REST_CLIENT_ID="<consumer-key>"
export SF_REST_CLIENT_SECRET="<consumer-secret>"
export SF_REST_INSTANCE_URL="https://myorg.my.salesforce.com"
```

```python
from salesforce_py.rest import RestClient

async with await RestClient.from_env() as client:
    limits = await client.limits.get_limits()
```

Or fall back to the SF CLI (no env creds needed):

```python
async with await RestClient.from_env("my-org-alias") as client:
    limits = await client.limits.get_limits()
```

### `from_org` — SF CLI session

Pass an `SFOrg` directly to reuse the CLI session token without env vars:

```python
from salesforce_py.sf import SFOrgTask
from salesforce_py.rest import RestClient

task = SFOrgTask("my-org-alias")
async with RestClient.from_org(task._org) as client:
    me = await client.sobjects.get("User", "005xx000001SvD8AAK")
```

### Direct construction

Supply credentials explicitly — useful when you already hold a token from your own OAuth flow:

```python
async with RestClient(
    instance_url="https://myorg.my.salesforce.com",
    access_token="<bearer-token>",
) as client:
    versions = await client.versions.list_versions()
```

## Client lifecycle

`RestClient` is best used as an async context manager. It owns a single underlying `httpx.AsyncClient` bound to `/services/data/vXX.X/`, which is opened and closed together with the client:

```python
from salesforce_py.rest import RestClient

async with RestClient(instance_url, access_token) as client:
    rows = await client.query.query("SELECT Id, Name FROM Account LIMIT 10")
```

If you need to keep the client alive across multiple scopes, call `open()` / `close()` manually:

```python
client = RestClient(instance_url, access_token)
await client.open()
try:
    ...
finally:
    await client.close()
```

Constructor parameters:

| Name | Default | Description |
|---|---|---|
| `instance_url` | — | Org instance URL, e.g. `https://myorg.my.salesforce.com`. |
| `access_token` | — | OAuth bearer token. |
| `api_version` | `DEFAULT_API_VERSION` | Salesforce API version string, e.g. `"66.0"`. |
| `timeout` | `120.0` | Default request timeout in seconds. |
| `http2` | `True` | Negotiate HTTP/2 when the server supports it. |

## Operation namespaces

Every REST endpoint family is exposed as a grouped namespace on `RestClient`. Attribute names mirror the URL hierarchy where reasonable:

| Namespace | Endpoint family |
|---|---|
| `client.versions` | `/services/data` and `/services/data/vXX.X` (versions + resource directory) |
| `client.limits` | `/limits`, `/limits/recordCount` |
| `client.query` | `/query`, `/queryAll`, async SOQL (`/async-queries`) |
| `client.search` | `/search` (SOSL), `/parameterizedSearch`, scope / suggestions / layouts |
| `client.sobjects` | Everything under `/sobjects/` — describe, CRUD, upsert, list views, layouts, relationships, deleted/updated, event schemas, user password, quick actions |
| `client.composite` | `/composite`, `/composite/batch`, `/composite/graph`, `/composite/tree/{sobject}`, `/composite/sobjects` (multi-record create/update/upsert/delete/retrieve) |
| `client.quick_actions` | Global `/quickActions` (list, describe, default values, invoke) |
| `client.actions` | `/actions/standard`, `/actions/custom` — invocable actions (list, describe, invoke) |
| `client.tabs` | `/tabs` |
| `client.theme` | `/theme` |
| `client.recent` | `/recent` |
| `client.app_menu` | `/appMenu`, `/appMenu/AppSwitcher`, `/appMenu/Salesforce1` |
| `client.lightning_usage` | Lightning Adoption metric sObjects (exit-by-page, toggle, usage-by-app-type/browser/flexipage/page) |
| `client.process` | `/process/approvals`, `/process/rules` |
| `client.support` | Data category groups, embedded service, field service, knowledge articles |
| `client.tooling` | `/tooling/` — query, describe, execute-anonymous, run-tests |
| `client.ui_api` | `/ui-api/` — records, record-ui, object-info, layouts, picklist-values, defaults |
| `client.metadata` | `/metadata/` passthrough |
| `client.analytics` | `/analytics/` passthrough |
| `client.wave` | `/wave/` passthrough |
| `client.folders` | `/folders` — list, get, create, update, delete, children |
| `client.smart_data_discovery` | `/smartdatadiscovery/` passthrough |
| `client.eclair` | `/eclair/geodata` |
| `client.jsonxform` | `/jsonxform/transform` |
| `client.streaming` | `/sobjects/StreamingChannel/{id}/push` |
| `client.financial_services` | `/connect/financialservices/` passthrough |
| `client.health_cloud` | `/connect/health/care-services/` passthrough |
| `client.manufacturing` | `/connect/manufacturing/` passthrough |
| `client.consumer_goods` | `/connect/object-detection`, `/connect/visit/recommendations` |
| `client.asset_management` | `/asset-management/` passthrough |
| `client.chatter` | `/chatter/` passthrough |
| `client.commerce` | `/commerce/` passthrough |
| `client.connect` | `/connect/` passthrough |
| `client.consent` | `/consent/` passthrough |
| `client.contact_tracing` | `/contact-tracing/` passthrough |
| `client.dedupe` | `/dedupe/` passthrough |
| `client.jobs` | `/jobs/` passthrough (Bulk API 2.0 lives in `salesforce_py.bulk`) |
| `client.knowledge_management` | `/knowledgeManagement/` passthrough |
| `client.licensing` | `/licensing/` passthrough |
| `client.localized_value` | `/localizedvalue/` passthrough |
| `client.payments` | `/commerce/payments/` passthrough |
| `client.scheduling` | `/scheduling/` passthrough |

Each namespace class is a thin wrapper over the underlying HTTP verbs — method names map to Salesforce's documented operations and return parsed JSON dicts (or `bytes` when the endpoint returns binary content).

For small-surface namespaces marked "passthrough", the class exposes generic `get(path, params=...)`, `post(path, json=...)`, `patch`, `put`, and `delete` methods that prepend the namespace's base path. This lets you hit any sub-resource without waiting for a helper to be added.

## Examples

### SOQL with pagination

```python
async with RestClient(instance_url, access_token) as client:
    page = await client.query.query("SELECT Id, Name FROM Account ORDER BY Name LIMIT 200")
    print(page["totalSize"], "accounts")
    while not page.get("done"):
        page = await client.query.query_more(page["nextRecordsUrl"])

    # Or drain everything in one call:
    accounts = await client.query.query_all_records("SELECT Id, Name FROM Account")
```

### sObject CRUD

```python
async with RestClient(instance_url, access_token) as client:
    created = await client.sobjects.create("Account", {"Name": "Acme Corp"})
    account_id = created["id"]

    account = await client.sobjects.get("Account", account_id, fields=["Id", "Name"])

    await client.sobjects.update("Account", account_id, {"Description": "Updated via API"})

    await client.sobjects.delete("Account", account_id)
```

### Upsert by external ID

```python
async with RestClient(instance_url, access_token) as client:
    await client.sobjects.upsert(
        "Account",
        "External_Id__c",
        "EXT-001",
        {"Name": "Acme Corp", "Description": "Upserted"},
    )
```

### Composite / batch / tree

```python
async with RestClient(instance_url, access_token) as client:
    batch = await client.composite.batch([
        {"method": "GET", "url": "v66.0/sobjects/Account/describe"},
        {"method": "GET", "url": "v66.0/limits"},
    ])

    graph = await client.composite.graph([
        {
            "graphId": "acme-graph",
            "compositeRequest": [
                {
                    "method": "POST",
                    "url": "/services/data/v66.0/sobjects/Account",
                    "referenceId": "acme",
                    "body": {"Name": "Acme Corp"},
                },
            ],
        },
    ])

    tree = await client.composite.tree("Account", [
        {
            "attributes": {"type": "Account", "referenceId": "acme"},
            "Name": "Acme Corp",
            "Contacts": {
                "records": [
                    {
                        "attributes": {"type": "Contact", "referenceId": "alice"},
                        "FirstName": "Alice",
                        "LastName": "Admin",
                    },
                ],
            },
        },
    ])
```

### SOSL search

```python
async with RestClient(instance_url, access_token) as client:
    results = await client.search.search("FIND {Acme} IN NAME FIELDS RETURNING Account(Id, Name)")

    params = await client.search.parameterized_search(
        q="Acme",
        sobject="Account",
        fields="Id,Name",
    )
```

### Invocable action

```python
async with RestClient(instance_url, access_token) as client:
    standard = await client.actions.list_standard_actions()
    email = await client.actions.invoke_standard_action(
        "emailSimple",
        inputs=[{
            "emailAddresses": "ops@acme.com",
            "emailSubject": "Ping",
            "emailBody": "Hello",
        }],
    )
```

### UI API record fetch

```python
async with RestClient(instance_url, access_token) as client:
    record_ui = await client.ui_api.get_record_ui(
        ["005xx000001SvD8AAK"],
        layout_types=["Full"],
        modes=["View"],
    )
```

### Tooling API — execute anonymous Apex

```python
async with RestClient(instance_url, access_token) as client:
    result = await client.tooling.execute_anonymous("System.debug('hello from rest');")
    print(result["success"], result.get("line"))
```

### Passthrough for small-surface namespaces

```python
async with RestClient(instance_url, access_token) as client:
    # /services/data/vXX.X/consent/action/email
    await client.consent.post(
        "action/email",
        json={"ids": ["005xx000001SvD8AAK"], "action": "OPT_IN"},
    )
```

## Error handling

`RestBaseOperations` inspects every response and raises a typed exception on failure:

| Status | Exception |
|---|---|
| `401` | `AuthError` |
| `4xx` / `5xx` | `SalesforcePyError` (carries the first 500 chars of the response body) |
| Non-JSON 2xx body | `SalesforcePyError` |

```python
from salesforce_py.exceptions import AuthError, SalesforcePyError

try:
    await client.query.query("SELECT Id FROM Account")
except AuthError:
    # token expired — refresh and retry
    ...
except SalesforcePyError as e:
    print("REST API failed:", e)
```

Transient failures (`408`, `420`, `425`, `429`, `500`, `502`, `503`, `504`, plus `httpx.TimeoutException` / `ConnectError`) are automatically retried once after a 20-second pause by the shared `retry_async_http_call` helper. `AuthError` (401) and other 4xx statuses are not retried.

## HTTP/2

HTTP/2 is negotiated by default. Some Salesforce edges are HTTP/2-enabled and benefit materially from multiplexing — especially when a workflow fans out into many REST calls. Edges that still speak only HTTP/1.1 fall back transparently via ALPN.

Disable it only if you have a specific reason (debugging, proxy that mangles HTTP/2, etc.):

```python
client = RestClient(instance_url, access_token, http2=False)
```

The `h2` package is pulled in automatically by the `rest`, `connect`, `bulk`, and `all` extras.

## API versioning

`RestClient` defaults to `salesforce_py.DEFAULT_API_VERSION`. Override per-client when you need to pin to a specific release:

```python
client = RestClient(instance_url, access_token, api_version="63.0")
```

The version string is embedded directly into the session base URL
(`/services/data/v63.0/...`), so it applies to every call made through the client.

The un-versioned `/services/data` root (which lists available API versions) is addressed by `client.versions.list_versions()` via an absolute URL against the instance, so it is not affected by the `api_version` setting.

## Testing

The test suite in this directory covers every operation with mocked `httpx.Response` objects — no network calls. Run it with:

```bash
uv sync --extra dev --extra rest
uv run pytest tests/rest
```

The `conftest.py` fixtures patch `RestSession`'s underlying `httpx.AsyncClient` so individual tests can assert on the exact URL, params, and JSON payload each method sends.
