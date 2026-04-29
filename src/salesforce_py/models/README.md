# Salesforce Models REST API support

`salesforce_py.models` is an async client for the Salesforce **Models REST API** — the generative-AI surface at `https://api.salesforce.com/einstein/platform/v1/`. It wraps the four documented capabilities:

| Capability | Endpoint |
|---|---|
| Generate Chat | `/models/{modelName}/chat-generations` |
| Generate Embeddings | `/models/{modelName}/embeddings` |
| Generate Text | `/models/{modelName}/generations` |
| Submit Feedback | `/feedback` |

It is built on [httpx](https://www.python-httpx.org/) and is fully async. HTTP/2 is negotiated by default, with transparent fallback to HTTP/1.1.

- [Installation](#installation)
- [Getting an access token](#getting-an-access-token)
- [Client lifecycle](#client-lifecycle)
- [Operation namespaces](#operation-namespaces)
- [Examples](#examples)
- [Supported models](#supported-models)
- [Error handling](#error-handling)
- [Rate limits](#rate-limits)
- [HTTP/2](#http2)
- [Testing](#testing)

## Installation

The Models client lives behind the `models` extra (it pulls in `httpx` and, for HTTP/2, `h2`):

```bash
pip install "salesforce-py[models]"
# or with uv
uv add "salesforce-py[models]"
```

Everything at once:

```bash
pip install "salesforce-py[all]"
```

## Getting an access token

The Models API uses a **client-credentials** OAuth flow distinct from standard Salesforce auth. You need an **External Client App** with the `sfap_api`, `einstein_gpt_api`, and `api` scopes, plus its consumer key/secret.

Use `fetch_token` to mint a JWT:

```python
from salesforce_py.models import fetch_token, ModelsClient

token = await fetch_token(
    my_domain="https://mycompany.my.salesforce.com",
    consumer_key="<CONSUMER_KEY>",
    consumer_secret="<CONSUMER_SECRET>",
)

async with ModelsClient(
    token.access_token,
    base_url=f"{token.api_instance_url}/einstein/platform/v1/" if token.api_instance_url else None,
) as client:
    ...
```

Or call the endpoint yourself and pass the resulting token to `ModelsClient`. The helper returns the full JSON body in `token.raw` if you need fields beyond `access_token` / `api_instance_url`.

> **Tip** — `api_instance_url` is geo-aware. If it's returned, use it as the client's `base_url` so requests land in the nearest data centre.

## Client lifecycle

`ModelsClient` is best used as an async context manager:

```python
from salesforce_py.models import ModelsClient

async with ModelsClient(access_token) as client:
    result = await client.generations.generate(
        "sfdc_ai__DefaultOpenAIGPT4OmniMini",
        "Write a haiku about Salesforce.",
    )
```

Or manage the lifecycle manually:

```python
client = ModelsClient(access_token)
await client.open()
try:
    ...
finally:
    await client.close()
```

Constructor parameters:

| Name | Default | Description |
|---|---|---|
| `access_token` | — | Bearer JWT minted with `sfap_api einstein_gpt_api api`. |
| `base_url` | `https://api.salesforce.com/einstein/platform/v1/` | Override to use the `api_instance_url` from the token response. |
| `app_context` | `"EinsteinGPT"` | `x-sfdc-app-context` header. |
| `client_feature_id` | `"ai-platform-models-connected-app"` | `x-client-feature-id` header. |
| `timeout` | `30.0` | Default request timeout in seconds. |
| `http2` | `True` | Negotiate HTTP/2 when the server supports it. |

## Operation namespaces

| Namespace | Endpoint |
|---|---|
| `client.generations` | `/models/{modelName}/generations` |
| `client.chat_generations` | `/models/{modelName}/chat-generations` |
| `client.embeddings` | `/models/{modelName}/embeddings` |
| `client.feedback` | `/feedback` |

Each namespace exposes a high-level convenience method (`generate` / `embed` / `submit`) plus a `*_raw` escape hatch that accepts a fully-formed body dict when you need model-specific properties outside the helper's kwargs.

## Examples

### Text generation

```python
from salesforce_py.models import ModelsClient
from salesforce_py.models.supported_models import OPENAI_GPT_4_OMNI_MINI

async with ModelsClient(access_token) as client:
    result = await client.generations.generate(
        OPENAI_GPT_4_OMNI_MINI,
        "Generate a story about a financial advisor in San Diego.",
        extra={"localization": {"defaultLocale": "en_US"}},
    )
    print(result["generation"]["generatedText"])
```

### Chat generation

```python
from salesforce_py.models.supported_models import BEDROCK_ANTHROPIC_CLAUDE_45_SONNET

async with ModelsClient(access_token) as client:
    reply = await client.chat_generations.generate(
        BEDROCK_ANTHROPIC_CLAUDE_45_SONNET,
        messages=[
            {"role": "system", "content": "You are a helpful Salesforce expert."},
            {"role": "user", "content": "Explain what a DMO is in one sentence."},
        ],
    )
```

### Embeddings

```python
from salesforce_py.models.supported_models import OPENAI_ADA_002

async with ModelsClient(access_token) as client:
    vectors = await client.embeddings.embed(
        OPENAI_ADA_002,
        ["customer loyalty program", "referral rewards"],
    )
```

### Feedback

```python
async with ModelsClient(access_token) as client:
    await client.feedback.submit({
        "id": "chatcmpl-9AMuFltdq7M5ntZVvQcAkgyWhfoas",
        "feedback": "GOOD",
        "feedbackText": "Accurate and concise.",
    })
```

## Supported models

`salesforce_py.models.supported_models` exports string constants for every Salesforce-managed model in Einstein Studio (see the Salesforce docs for the authoritative list, and the `Large Language Model Support` help topic for rate limits and regional availability). BYOLLM configurations work too — pass the API name you configured in Einstein Studio.

```python
from salesforce_py.models.supported_models import (
    GPT_4_OMNI,
    GPT_5,
    BEDROCK_ANTHROPIC_CLAUDE_46_SONNET,
    VERTEX_GEMINI_25_PRO,
    SUPPORTED_MODELS,
)
```

## Error handling

`ModelsBaseOperations` inspects every response and raises a typed exception on failure:

| Status | Exception |
|---|---|
| `401` | `AuthError` |
| `4xx` / `5xx` (incl. `429`) | `SalesforcePyError` (carries the first 500 chars of the body) |
| Non-JSON 2xx body | `SalesforcePyError` |

```python
from salesforce_py.exceptions import AuthError, SalesforcePyError

try:
    await client.generations.generate(model_name, "hi")
except AuthError:
    # token expired — mint a new one
    ...
except SalesforcePyError as e:
    print("Models API failed:", e)
```

## Rate limits

Per Salesforce documentation:

- **Generation endpoints** (chat-generations, generations): default **500 RPM/org**, per model. Varies by model.
- **Embeddings and Feedback**: **1,000 RPM/org**.
- **Sandbox/Demo/Trial orgs via Apex**: 200 requests/hour (sandbox) or 150 requests/hour (demo/trial).

When you exceed a limit the API returns **429 Too Many Requests**. This library surfaces those as `SalesforcePyError` with the provider's error payload intact. Implement your own retry/backoff on top.

## HTTP/2

HTTP/2 is negotiated by default. Disable it only if you have a specific reason (proxy debugging, etc.):

```python
client = ModelsClient(access_token, http2=False)
```

The `h2` package is pulled in automatically by the `models`, `connect`, `data360`, `rest`, `bulk`, and `all` extras.

## Testing

The test suite in `tests/models/` covers the client with mocked `httpx.Response` objects — no network calls. Run it with:

```bash
uv sync --extra dev --extra models
uv run pytest tests/models
```
