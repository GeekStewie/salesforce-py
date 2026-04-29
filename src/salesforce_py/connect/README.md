# Salesforce Connect API support

`salesforce_py.connect` is an async client for the Salesforce Connect REST API — the family of endpoints served under `/services/data/vXX.X/connect/`, `/services/data/vXX.X/einstein/`, and a handful of sibling namespaces (`commerce/`, `communities/`, `named-credentials/`, etc.).

It is built on [httpx](https://www.python-httpx.org/) and is fully async. HTTP/2 is negotiated by default, with transparent fallback to HTTP/1.1 for edges that do not support it.

- [Installation](#installation)
- [Getting an access token](#getting-an-access-token)
- [Client lifecycle](#client-lifecycle)
- [Operation namespaces](#operation-namespaces)
- [Examples](#examples)
- [Error handling](#error-handling)
- [ID normalisation](#id-normalisation)
- [HTTP/2](#http2)
- [API versioning](#api-versioning)
- [Testing](#testing)

## Installation

The Connect API lives behind the `connect` extra because it pulls in `httpx` (and, for HTTP/2, `h2`):

```bash
pip install "salesforce-py[connect]"
# or with uv
uv add "salesforce-py[connect]"
```

Everything at once:

```bash
pip install "salesforce-py[all]"
```

## Getting an access token

`ConnectClient` is token-driven — it does **not** perform OAuth on your behalf. You supply an `instance_url` and `access_token` from whatever auth flow you prefer. The quickest path during development is to reuse the session that the `sf` CLI already holds:

```python
from salesforce_py.sf import SFOrgTask
from salesforce_py.connect import ConnectClient

task = SFOrgTask("my-org-alias")
task.org._ensure_connected()  # populates instance_url + access_token

async with ConnectClient(
    instance_url=task.org.instance_url,
    access_token=task.org.access_token,
) as client:
    me = await client.users.get_user("me")
```

In production use a JWT, refresh token, or client-credentials flow and pass the resulting token into `ConnectClient`.

## Client lifecycle

`ConnectClient` is best used as an async context manager. It owns three underlying `httpx.AsyncClient` instances — one per base path (`connect/`, `einstein/`, and the empty root for `commerce/`, `communities/`, etc.) — which are all opened and closed together:

```python
from salesforce_py.connect import ConnectClient

async with ConnectClient(instance_url, access_token) as client:
    feed = await client.chatter.get_feed_items(page_size=10)
```

If you need to keep the client alive across multiple scopes, call `open()` / `close()` manually:

```python
client = ConnectClient(instance_url, access_token)
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
| `api_version` | `DEFAULT_API_VERSION` | Salesforce API version string, e.g. `"62.0"`. |
| `timeout` | `30.0` | Default request timeout in seconds. |
| `http2` | `True` | Negotiate HTTP/2 when the server supports it. |

## Operation namespaces

Every Connect endpoint family is exposed as a grouped namespace on `ConnectClient`. Attribute names mirror the URL hierarchy where reasonable:

| Namespace | Endpoint family |
|---|---|
| `client.core` | `/connect/` root (organization, supported API versions, etc.) |
| `client.action_links` | `/connect/action-link-group-definitions`, `/action-links` |
| `client.activity_reminders` | `/connect/activity-reminders` |
| `client.agentforce_data_libraries` | `/einstein/agentforce-data-libraries` |
| `client.announcements` | `/connect/announcements` |
| `client.bot_version_activation` | `/connect/bots/versions/{id}/activation` |
| `client.chatter` | `/chatter/feeds`, `/chatter/feed-items`, `/chatter/comments` |
| `client.clean` | `/clean/jobs`, `/clean/matches` |
| `client.cms_content` | `/connect/cms/content`, `/cms/delivery/content` |
| `client.cms_content_search` | `/connect/cms/search` |
| `client.cms_workspaces` | `/connect/cms/workspaces` |
| `client.comments` | `/chatter/comments/{id}` |
| `client.commerce_addresses` | `/commerce/webstores/{id}/accounts/{id}/addresses` |
| `client.commerce_cart` | `/commerce/webstores/{id}/carts` |
| `client.commerce_checkout` | `/commerce/webstores/{id}/checkouts` |
| `client.commerce_context` | `/commerce/webstores/{id}/context` |
| `client.commerce_einstein_webstore` | `/commerce/webstores/{id}/einstein` |
| `client.commerce_my_profile` | `/commerce/webstores/{id}/my-profile` |
| `client.commerce_order_summaries` | `/commerce/webstores/{id}/order-summaries` |
| `client.commerce_pricing` | `/commerce/webstores/{id}/pricing` |
| `client.commerce_products` | `/commerce/webstores/{id}/products` |
| `client.commerce_taxes` | `/commerce/webstores/{id}/taxes` |
| `client.commerce_wishlists` | `/commerce/webstores/{id}/wishlists` |
| `client.communities` | `/connect/communities` |
| `client.content_hub` | `/connect/files/connect/repositories` |
| `client.conversation_application` | `/connect/conversation-application` |
| `client.conversations` | `/connect/conversations` |
| `client.custom_domain` | `/connect/custom-domains`, `/custom-urls` |
| `client.data_integration` | `/data-integration` |
| `client.duplicate` | `/duplicate` (Duplicate Management) |
| `client.einstein_recommendations` | `/connect/einstein/recommendations` |
| `client.email_merge_fields` | `/email/merge-fields` |
| `client.feeds` | Chatter feeds directory (`/chatter/feeds/*`) |
| `client.files` | `/connect/files` (ContentDocument CRUD and streaming) |
| `client.flow_approval` | `/connect/flow-approval` |
| `client.groups` | `/chatter/groups` (Chatter groups, members, photos) |
| `client.knowledge_article_view_stat` | `/connect/knowledge-article-view-stat` |
| `client.likes` | `/chatter/likes` |
| `client.managed_topics` | `/connect/managed-topics` |
| `client.mentions` | `/chatter/mentions/completions` |
| `client.microsites` | `/sites/microsites` |
| `client.motifs` | `/connect/motifs` |
| `client.named_credentials` | `/named-credentials/named-credentials`, `/external-credentials` |
| `client.navigation_menu` | `/connect/communities/{id}/navigation-menu` |
| `client.network_data_category` | `/connect/communities/{id}/network-data-category` |
| `client.next_best_action` | `/connect/strategies` |
| `client.notification_settings` | `/connect/notification-settings` |
| `client.notifications` | `/connect/notifications` |
| `client.omnichannel_inventory` | `/commerce/omnichannel-inventory` |
| `client.orchestration` | `/connect/orchestration` |
| `client.order_management` | `/commerce/order-management` |
| `client.payments` | `/commerce/payments` |
| `client.personalization_audiences` | `/connect/personalization/audiences` |
| `client.personalization_engagement_signals` | `/personalization/engagement-signals` |
| `client.personalization_experiments` | `/personalization/experiments` |
| `client.personalization_recommenders` | `/personalization/recommenders` |
| `client.prompt_templates` | `/einstein/prompt-templates` |
| `client.push_notifications` | `/connect/notifications/push` |
| `client.quick_text` | `/connect/quick-text` |
| `client.quip` | `/connect/quip` |
| `client.search` | `/connect/search/sobjects` (v63.0+) |
| `client.sites_knowledge` | `/connect/communities/{id}/knowledge` |
| `client.sites_moderation` | `/connect/communities/{id}/moderation` |
| `client.subscriptions` | `/chatter/subscriptions` |
| `client.topics` | `/connect/topics` |
| `client.topics_on_records` | `/connect/records/{id}/topics` |
| `client.user_profiles` | `/chatter/user-profiles` |
| `client.users` | `/chatter/users` (directory, followers, messages, groups) |

Each namespace class is a thin wrapper over the underlying HTTP verbs — method names map to Salesforce's documented operations and return parsed JSON dicts (or `bytes` when the endpoint returns binary content).

## Examples

### Post to Chatter

```python
async with ConnectClient(instance_url, access_token) as client:
    post = await client.chatter.post_feed_item(
        body="Deployment green \N{PARTY POPPER}",
        subject_id="me",
    )
    await client.chatter.post_comment(post["id"], "Shipped on time too.")
```

### Search a custom object (v63.0+)

```python
async with ConnectClient(instance_url, access_token) as client:
    hits = await client.search.search_object_results(
        "Knowledge__kav",
        q="password reset",
        page_size=25,
        highlights=True,
    )
    for record in hits.get("records", []):
        print(record["Id"], record.get("Title"))
```

### Create a Chatter group and add members

```python
async with ConnectClient(instance_url, access_token) as client:
    group = await client.groups.create_group({
        "name": "Platform Ops",
        "visibility": "PublicAccess",
        "description": "Ops + SRE collab",
    })
    await client.groups.add_group_member(group["id"], "005xx000001SvD8")
```

### Upload a new version of an existing file

```python
from pathlib import Path

async with ConnectClient(instance_url, access_token) as client:
    content = Path("runbook.pdf").read_bytes()
    await client.files.upload_new_version(
        file_id="069xx000001abcd",
        filename="runbook.pdf",
        content=content,
        content_type="application/pdf",
        description="Incident runbook — v3",
    )
```

### List your Chatter groups and print unread feed counts

```python
async with ConnectClient(instance_url, access_token) as client:
    my_groups = await client.users.get_user_groups("me")
    for g in my_groups.get("groups", []):
        feed = await client.feeds.get_record_feed(
            g["id"], page_size=1, update_since="2026-01-01T00:00:00Z"
        )
        print(g["name"], len(feed.get("elements", [])))
```

### Experience Cloud (community) scoped call

Most namespaces accept an optional `community_id` keyword:

```python
async with ConnectClient(instance_url, access_token) as client:
    groups = await client.groups.list_groups(
        community_id="0DB000000000001AAA",
        page_size=50,
    )
```

## Error handling

`ConnectBaseOperations` inspects every response and raises a typed exception on failure:

| Status | Exception |
|---|---|
| `401` | `AuthError` |
| `4xx` / `5xx` | `SalesforcePyError` (carries the first 500 chars of the response body) |
| Non-JSON 2xx body | `SalesforcePyError` |

```python
from salesforce_py.exceptions import AuthError, SalesforcePyError

try:
    await client.chatter.get_feed_items()
except AuthError:
    # token expired — refresh and retry
    ...
except SalesforcePyError as e:
    print("Connect API failed:", e)
```

## ID normalisation

The Connect REST API expects 18-character Salesforce IDs. Every operation method automatically converts 15-character IDs on the way out, so both forms are safe to pass:

```python
await client.users.get_user("005xx000001SvD8")   # 15 chars — normalised
await client.users.get_user("005xx000001SvD8AAK") # 18 chars — passed through
await client.users.get_user("me")                 # aliases untouched
```

Non-ID values (`"me"`, fully-qualified asset names, email addresses) pass through unchanged.

## HTTP/2

HTTP/2 is negotiated by default. Some Salesforce edges are HTTP/2-enabled and benefit materially from multiplexing — especially when a single workflow fans out into many Connect calls. Edges that still speak only HTTP/1.1 fall back transparently via ALPN.

Disable it only if you have a specific reason (debugging, proxy that mangles HTTP/2, etc.):

```python
client = ConnectClient(instance_url, access_token, http2=False)
```

The `h2` package is pulled in automatically by the `connect`, `rest`, `bulk`, and `all` extras.

## API versioning

`ConnectClient` defaults to `salesforce_py.DEFAULT_API_VERSION`. Override per-client when you need to pin to a specific release (for example, `search.*` endpoints require v63.0+):

```python
client = ConnectClient(instance_url, access_token, api_version="63.0")
```

The version string is embedded directly into the session base URL
(`/services/data/v63.0/connect/...`), so it applies to every call made through the client.

## Testing

The test suite in this directory covers every operation with mocked `httpx.Response` objects — no network calls. Run it with:

```bash
uv sync --extra dev --extra connect
uv run pytest tests/connect
```

The `conftest.py` fixtures patch `ConnectSession`'s underlying `httpx.AsyncClient` so individual tests can assert on the exact URL, params, and JSON payload each method sends.
