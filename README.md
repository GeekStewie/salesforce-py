<p align="center">
  <img src="img/salesforcepy-logo.png" alt="salesforce-py logo" width="358" height="281" />
</p>

<h1 align="center">salesforce-py</h1>

<p align="center">
  <a href="https://github.com/geekstewie/salesforce-py/actions/workflows/health-check.yml">
    <img src="https://github.com/geekstewie/salesforce-py/actions/workflows/health-check.yml/badge.svg?branch=main" alt="Health Check" />
  </a>
</p>

> **Disclaimer:** This is an independent, community-maintained project and is **not affiliated with, endorsed by, or supported by Salesforce, Inc.** Salesforce, the Salesforce CLI, and related marks are trademarks of Salesforce, Inc.

A Python wrapper for Salesforce CLIs and APIs. Ships four independent clients:

- **SF CLI wrapper** — sync/async subprocess wrapper for the [`sf` CLI](https://developer.salesforce.com/tools/salesforcecli)
- **Connect REST API** — async client for `/services/data/vXX.X/connect/` (Chatter, Files, Communities, Commerce, Einstein, and more)
- **Data 360 Connect REST API** — async client for `/services/data/vXX.X/ssot/` (Data Cloud / Data 360)
- **Models REST API** — async client for the Einstein Models generative AI surface (`chat-generations`, `generations`, `embeddings`, `feedback`)

REST and Bulk API clients are on the roadmap.

## Requirements

- Python 3.12+
- [Salesforce CLI (`sf`)](https://developer.salesforce.com/tools/salesforcecli) installed and on `PATH`

## Installation

### From PyPI

```bash
pip install salesforce-py
```

With optional extras:

```bash
# Connect REST API (Chatter, Files, Communities, Commerce, Einstein, etc.)
pip install "salesforce-py[connect]"

# Data 360 Connect REST API (Data Cloud / CDP)
pip install "salesforce-py[data360]"

# Models REST API (Einstein generative AI)
pip install "salesforce-py[models]"

# REST API support (planned)
pip install "salesforce-py[rest]"

# Bulk API support (planned)
pip install "salesforce-py[bulk]"

# Salesforce Code Analyzer plugin support
pip install "salesforce-py[code-analyzer]"

# Everything
pip install "salesforce-py[all]"
```

### Directly from GitHub

Latest main branch:

```bash
pip install "salesforce-py @ git+https://github.com/geekstewie/salesforce-py.git"
```

With extras:

```bash
pip install "salesforce-py[all] @ git+https://github.com/geekstewie/salesforce-py.git"
```

Pinned to a specific tag or commit:

```bash
pip install "salesforce-py @ git+https://github.com/geekstewie/salesforce-py.git@v0.1.0"
```

### With uv

```bash
uv add salesforce-py
uv add "salesforce-py[all]"

# From repo
uv add "salesforce-py @ git+https://github.com/geekstewie/salesforce-py.git"
```

## Quick start

```python
from salesforce_py.sf import SFOrgTask

# Connect to an org by alias or username
task = SFOrgTask("my-scratch-org")

# Run Apex tests
results = task.apex.run_tests(class_names=["MyAccountTests"], code_coverage=True)

# Deploy metadata
task.project.deploy(source_dir="force-app", wait=33)

# Query data
records = task.data.query("SELECT Id, Name FROM Account LIMIT 10")

# Use the Agentforce operations
task.agent.test_run(api_name="MyAgentTest", wait=5)
```

## SF CLI operations

`SFOrgTask` exposes all SF CLI command groups as attributes:

| Attribute | Commands |
|---|---|
| `task.agent` | Agent lifecycle, spec/bundle generation, preview sessions, test management |
| `task.alias` | Local alias management |
| `task.apex` | Anonymous execution, test runs, log management |
| `task.api` | Raw REST and GraphQL API requests |
| `task.cmdt` | Custom metadata type generation |
| `task.code_analyzer` | Code Analyzer scan and results |
| `task.community` | Community/Experience Cloud publish |
| `task.config` | SF CLI config get/set/unset/list |
| `task.data` | SOQL query, record upsert/delete, bulk import/export |
| `task.dev` | Dev hub, scratch org, sandbox management |
| `task.doctor` | SF CLI diagnostics |
| `task.flow` | Flow run and interview management |
| `task.lightning` | LWC and Aura component generation |
| `task.org` | Org create, delete, display, open, list |
| `task.package` | Managed and unlocked package operations |
| `task.plugins` | SF CLI plugin management |
| `task.project` | Deploy, retrieve, convert, manifest generation |
| `task.schema` | Object and field schema inspection |
| `task.sobject` | sObject CRUD helpers |
| `task.template` | Project template generation |
| `task.ui_bundle` | UI Bundle deployment |

## Connect REST API

`salesforce_py.connect` is a fully async client for the Salesforce Connect REST API. It covers Chatter, Files, Communities, Commerce, Einstein, Managed Topics, Named Credentials, Search, and most other endpoints served under `/services/data/vXX.X/connect/` (and sibling namespaces). HTTP/2 is negotiated by default, with transparent fallback to HTTP/1.1.

**Option 1 — environment variables (recommended for CI/CD):**

```python
import asyncio
from salesforce_py.connect import ConnectClient

async def main():
    async with await ConnectClient.from_env() as client:
        me = await client.users.get_user("me")

asyncio.run(main())
```

**Option 2 — SF CLI session (interactive / dev machines):**

```python
import asyncio
from salesforce_py.connect import ConnectClient

async def main():
    async with await ConnectClient.from_env("my-org-alias") as client:
        await client.chatter.post_feed_item(body="Shipped.", subject_id="me")

asyncio.run(main())
```

**Option 3 — SF CLI org object:**

```python
import asyncio
from salesforce_py.connect import ConnectClient
from salesforce_py.sf import SFOrgTask

async def main():
    task = SFOrgTask("my-org-alias")
    async with ConnectClient.from_org(task._org) as client:
        me = await client.users.get_user("me")

asyncio.run(main())
```

**Option 4 — direct token:**

```python
import asyncio
from salesforce_py.connect import ConnectClient

async def main():
    async with ConnectClient(instance_url="...", access_token="...") as client:
        me = await client.users.get_user("me")

asyncio.run(main())
```

**Environment variables:**

| Variable | Purpose |
|---|---|
| `SF_CONNECT_CLIENT_ID` | External Client App consumer key |
| `SF_CONNECT_CLIENT_SECRET` | External Client App consumer secret |
| `SF_CONNECT_INSTANCE_URL` | My Domain URL (falls back to `SF_INSTANCE_URL`) |

Install with the `connect` extra (pulls in `httpx[http2]`):

```bash
pip install "salesforce-py[connect]"
```

See [src/salesforce_py/connect/README.md](src/salesforce_py/connect/README.md) for the full Connect API reference — operation namespaces, authentication patterns, error handling, ID normalisation, HTTP/2 configuration, and testing guidance.

## Data 360 REST API

`salesforce_py.data360` is a fully async client for the Salesforce Data 360 Connect REST API — the endpoint family under `/services/data/vXX.X/ssot/` (formerly Data Cloud / CDP). HTTP/2 is negotiated by default.

**Option 1 — environment variables (recommended for CI/CD):**

```python
import asyncio
from salesforce_py.data360 import Data360Client

async def main():
    async with await Data360Client.from_env() as client:
        segments = await client.segments.get_segments()

asyncio.run(main())
```

**Option 2 — SF CLI session (interactive / dev machines):**

```python
import asyncio
from salesforce_py.data360 import Data360Client

async def main():
    async with await Data360Client.from_env("my-org-alias") as client:
        submitted = await client.query.submit_sql_query(
            {"sql": "SELECT Id__c, Email__c FROM UnifiedIndividual__dlm LIMIT 10"},
            dataspace="default",
        )

asyncio.run(main())
```

**Option 3 — SF CLI org object:**

```python
import asyncio
from salesforce_py.data360 import Data360Client
from salesforce_py.sf import SFOrgTask

async def main():
    task = SFOrgTask("my-org-alias")
    async with Data360Client.from_org(task._org) as client:
        segments = await client.segments.get_segments()

asyncio.run(main())
```

**Option 4 — direct token:**

```python
import asyncio
from salesforce_py.data360 import Data360Client

async def main():
    async with Data360Client(instance_url="...", access_token="...") as client:
        segments = await client.segments.get_segments()

asyncio.run(main())
```

**Environment variables:**

| Variable | Purpose |
|---|---|
| `SF_DATA360_CLIENT_ID` | External Client App consumer key |
| `SF_DATA360_CLIENT_SECRET` | External Client App consumer secret |
| `SF_DATA360_INSTANCE_URL` | My Domain URL (falls back to `SF_INSTANCE_URL`) |

Install with the `data360` extra (pulls in `httpx[http2]`):

```bash
pip install "salesforce-py[data360]"
```

**Operation namespaces** — 26 grouped wrappers covering the full `/ssot/` surface:

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
| `client.data_graphs` | `/ssot/data-graphs` |
| `client.data_kits` | `/ssot/data-kits` |
| `client.data_lake_objects` | `/ssot/data-lake-objects` |
| `client.data_model_objects` | `/ssot/data-model-objects`, `/ssot/data-model-object-mappings` |
| `client.data_spaces` | `/ssot/data-spaces` |
| `client.data_streams` | `/ssot/data-streams` |
| `client.data_transforms` | `/ssot/data-transforms` |
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

See [src/salesforce_py/data360/README.md](src/salesforce_py/data360/README.md) for full usage, authentication patterns, error handling, and testing guidance.

## Models REST API

`salesforce_py.models` is a fully async client for the Salesforce Einstein Models REST API at `https://api.salesforce.com/einstein/platform/v1/`. It covers chat generation, text generation, embeddings, and feedback. HTTP/2 is negotiated by default.

The Models API uses a client-credentials OAuth flow. Client credentials are always required — standard SF CLI session tokens do not carry the `sfap_api`/`einstein_gpt_api` scopes.

**Option 1 — environment variables (recommended for CI/CD):**

```python
import asyncio
from salesforce_py.models import ModelsClient
from salesforce_py.models.supported_models import BEDROCK_ANTHROPIC_CLAUDE_46_SONNET

async def main():
    async with await ModelsClient.from_env() as client:
        reply = await client.chat_generations.generate(
            BEDROCK_ANTHROPIC_CLAUDE_46_SONNET,
            messages=[{"role": "user", "content": "What is a DMO?"}],
        )

asyncio.run(main())
```

**Option 2 — SF CLI org object (supply client creds, domain resolved from CLI):**

```python
import asyncio
from salesforce_py.models import ModelsClient
from salesforce_py.sf import SFOrgTask

async def main():
    task = SFOrgTask("my-org-alias")
    async with await ModelsClient.from_org(
        task._org, consumer_key="<KEY>", consumer_secret="<SECRET>",
    ) as client:
        vectors = await client.embeddings.embed(
            "sfdc_ai__DefaultOpenAITextEmbeddingAda_002",
            ["customer loyalty program"],
        )

asyncio.run(main())
```

**Option 3 — direct token:**

```python
import asyncio
from salesforce_py.models import ModelsClient

async def main():
    async with ModelsClient(access_token="...") as client:
        reply = await client.generations.generate(
            "sfdc_ai__DefaultOpenAIGPT4OmniMini",
            "Summarise this case note in one sentence.",
        )

asyncio.run(main())
```

**Environment variables:**

| Variable | Purpose |
|---|---|
| `SF_MODELS_CLIENT_ID` | External Client App consumer key (`sfap_api einstein_gpt_api api` scopes) |
| `SF_MODELS_CLIENT_SECRET` | External Client App consumer secret |
| `SF_MODELS_INSTANCE_URL` | My Domain URL (falls back to `SF_INSTANCE_URL`) |

Install with the `models` extra (pulls in `httpx[http2]`):

```bash
pip install "salesforce-py[models]"
```

**Operation namespaces:**

| Namespace | Endpoint |
|---|---|
| `client.generations` | `/models/{modelName}/generations` |
| `client.chat_generations` | `/models/{modelName}/chat-generations` |
| `client.embeddings` | `/models/{modelName}/embeddings` |
| `client.feedback` | `/feedback` |

Supported model API names are exported as constants from `salesforce_py.models.supported_models` (`BEDROCK_ANTHROPIC_CLAUDE_46_SONNET`, `GPT_4_OMNI`, `VERTEX_GEMINI_25_PRO`, etc.). BYOLLM model names work too — pass any string.

See [src/salesforce_py/models/README.md](src/salesforce_py/models/README.md) for full usage, rate limits, error handling, and testing guidance.

## SF CLI setup helper

```python
from salesforce_py.sf import SFCLISetup

setup = SFCLISetup()
print(setup.status())          # Check what's installed
setup.ensure_sf_installed()    # Install SF CLI if missing (via npm/Homebrew)
```

## Exceptions

```python
from salesforce_py.exceptions import CLIError, CLINotFoundError, SalesforcePyError

try:
    task.apex.run(file_path="script.apex")
except CLINotFoundError:
    # sf binary not found on PATH
    ...
except CLIError as e:
    print(e.returncode, e.stdout, e.stderr)
except SalesforcePyError:
    # any other library error
    ...
```

## Development

```bash
git clone https://github.com/geekstewie/salesforce-py.git
cd salesforce-py
uv sync --extra dev
uv run pytest
uv run ruff check src/
uv run ty check src/
```

## License

This project is a personal open-source project, released under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).

You are free to use, modify, and distribute this software in accordance with the terms of the license. It is provided **as-is, without warranty of any kind** — express or implied — including but not limited to warranties of merchantability or fitness for a particular purpose. Use it at your own risk.

This project is **not an official Salesforce product** and is not affiliated with or endorsed by Salesforce, Inc. in any way.

See the [LICENSE](LICENSE) file for the full license text.
