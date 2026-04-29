# Salesforce Data 360 Connect REST API support

`salesforce_py.data360` is an async client for the Salesforce **Data 360 Connect REST API** — the family of endpoints served under `/services/data/vXX.X/ssot/`.

> As of October 14, 2025, Data Cloud has been rebranded to **Data 360**. The API surface is unchanged; the package and namespace have been named for the current product.

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

The Data 360 client lives behind the `data360` extra because it pulls in `httpx` (and, for HTTP/2, `h2`):

```bash
pip install "salesforce-py[data360]"
# or with uv
uv add "salesforce-py[data360]"
```

Everything at once:

```bash
pip install "salesforce-py[all]"
```

## Getting an access token

`Data360Client` is token-driven — it does **not** perform OAuth on your behalf. You supply an `instance_url` and `access_token` from whatever auth flow you prefer.

Data 360 authentication is separate from standard Salesforce OAuth — see the [OAuth and Connect REST API](https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/intro_using_oauth.htm) docs and the [Data 360 Connect API Postman Collection](https://developer.salesforce.com/docs/platform/connectapi/guide/postman-collection.html) for the bootstrap flow. The returned `instance_url` is the Data 360 tenant URL (e.g. `https://datacloud-abc.my.salesforce.com`) — not the standard Salesforce org instance URL.

For quick experimentation you can reuse the session the `sf` CLI already holds, but note that the resulting token may not be scoped for Data 360:

```python
from salesforce_py.sf import SFOrgTask
from salesforce_py.data360 import Data360Client

task = SFOrgTask("my-org-alias")
task.org._ensure_connected()

async with Data360Client(
    instance_url=task.org.instance_url,
    access_token=task.org.access_token,
) as client:
    segments = await client.segments.get_segments()
```

## Client lifecycle

`Data360Client` is best used as an async context manager:

```python
from salesforce_py.data360 import Data360Client

async with Data360Client(instance_url, access_token) as client:
    targets = await client.activation_targets.get_activation_targets(batch_size=10)
```

Or manage the lifecycle manually:

```python
client = Data360Client(instance_url, access_token)
await client.open()
try:
    ...
finally:
    await client.close()
```

Constructor parameters:

| Name | Default | Description |
|---|---|---|
| `instance_url` | — | Data 360 tenant instance URL. |
| `access_token` | — | OAuth bearer token. |
| `api_version` | `DEFAULT_API_VERSION` | Salesforce API version string, e.g. `"66.0"`. |
| `timeout` | `30.0` | Default request timeout in seconds. |
| `http2` | `True` | Negotiate HTTP/2 when the server supports it. |

## Operation namespaces

Every Data 360 endpoint group is exposed as a namespace on `Data360Client`. The 131 endpoints in the OpenAPI spec map to 26 grouped wrappers:

| Namespace | Endpoint family |
|---|---|
| `client.activation_targets` | `/ssot/activation-targets` |
| `client.activations` | `/ssot/activations`, `/ssot/activation-external-platforms` |
| `client.calculated_insights` | `/ssot/calculated-insights` |
| `client.connections` | `/ssot/connections`, schema/sitemap/actions |
| `client.connectors` | `/ssot/connectors` |
| `client.data_action_targets` | `/ssot/data-action-targets` |
| `client.data_actions` | `/ssot/data-actions` |
| `client.data_clean_room` | `/ssot/data-clean-room/{collaborations,providers,templates,specifications}` |
| `client.data_graphs` | `/ssot/data-graphs`, `/ssot/data-graphs/data/…` |
| `client.data_kits` | `/ssot/data-kits`, `/ssot/datakit/{name}/manifest` |
| `client.data_lake_objects` | `/ssot/data-lake-objects` |
| `client.data_model_objects` | `/ssot/data-model-objects`, `/ssot/data-model-object-mappings` |
| `client.data_spaces` | `/ssot/data-spaces` |
| `client.data_streams` | `/ssot/data-streams` |
| `client.data_transforms` | `/ssot/data-transforms`, `/ssot/data-transforms-validation` |
| `client.document_ai` | `/ssot/document-processing/…` |
| `client.identity_resolutions` | `/ssot/identity-resolutions` |
| `client.insights` | `/ssot/insight/metadata`, `/ssot/insight/calculated-insights/{name}` |
| `client.machine_learning` | `/ssot/machine-learning/…` |
| `client.metadata` | `/ssot/metadata`, `/ssot/metadata-entities` |
| `client.private_network_routes` | `/ssot/private-network-routes` |
| `client.profile` | `/ssot/profile/…` |
| `client.query` | `/ssot/query`, `/ssot/queryv2`, `/ssot/query-sql*` |
| `client.search_index` | `/ssot/search-index` |
| `client.segments` | `/ssot/segments` |
| `client.universal_id_lookup` | `/ssot/universalIdLookup/…` |

Each namespace class is a thin wrapper over the underlying HTTP verbs — method names map to Salesforce's documented operations and return parsed JSON dicts.

## Examples

### Submit a SQL query and poll for results

```python
async with Data360Client(instance_url, access_token) as client:
    submitted = await client.query.submit_sql_query(
        {"sql": "SELECT Id__c, Email__c FROM UnifiedIndividual__dlm LIMIT 100"},
        dataspace="default",
    )
    query_id = submitted["queryId"]

    status = await client.query.get_sql_query_status(query_id, dataspace="default")
    if status.get("state") == "SUCCESS":
        page = await client.query.get_sql_query_rows(
            query_id,
            dataspace="default",
            offset=0,
            row_limit=100,
        )
        for row in page.get("rows", []):
            print(row)
```

### Create a segment and publish it

```python
async with Data360Client(instance_url, access_token) as client:
    segment = await client.segments.create_segment({
        "name": "HighValueCustomers",
        "marketSegmentDefinition": {...},
    })
    await client.segments.publish_segment(segment["id"])
```

### Look up a universal ID

```python
async with Data360Client(instance_url, access_token) as client:
    unified = await client.universal_id_lookup.lookup_universal_id(
        entity_name="UnifiedIndividual__dlm",
        data_source_id="salesforce_crm_1",
        data_source_object_id="Contact",
        source_record_id="003xx000001abcd",
    )
```

### Run an identity resolution ruleset

```python
async with Data360Client(instance_url, access_token) as client:
    await client.identity_resolutions.run_identity_resolution_now("unified_profile_ruleset")
```

## Error handling

`Data360BaseOperations` inspects every response and raises a typed exception on failure:

| Status | Exception |
|---|---|
| `401` | `AuthError` |
| `4xx` / `5xx` | `SalesforcePyError` (carries the first 500 chars of the response body) |
| Non-JSON 2xx body | `SalesforcePyError` |

```python
from salesforce_py.exceptions import AuthError, SalesforcePyError

try:
    await client.segments.get_segments()
except AuthError:
    # token expired — refresh and retry
    ...
except SalesforcePyError as e:
    print("Data 360 API failed:", e)
```

## HTTP/2

HTTP/2 is negotiated by default. Disable it only if you have a specific reason (debugging, proxy that mangles HTTP/2, etc.):

```python
client = Data360Client(instance_url, access_token, http2=False)
```

The `h2` package is pulled in automatically by the `data360`, `connect`, `rest`, `bulk`, and `all` extras.

## API versioning

`Data360Client` defaults to `salesforce_py.DEFAULT_API_VERSION`. Override per-client when you need to pin to a specific release:

```python
client = Data360Client(instance_url, access_token, api_version="66.0")
```

The version string is embedded directly into the session base URL (`/services/data/v66.0/ssot/...`), so it applies to every call made through the client.

## Testing

The test suite in `tests/data360/` covers the client with mocked `httpx.Response` objects — no network calls. Run it with:

```bash
uv sync --extra dev --extra data360
uv run pytest tests/data360
```
