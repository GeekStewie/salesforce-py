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

A Python wrapper for Salesforce CLIs and APIs. Provides a comprehensive sync wrapper for the [Salesforce CLI (`sf`)](https://developer.salesforce.com/tools/salesforcecli) plus a fully async client for the [Salesforce Connect REST API](https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/intro_what_is_chatter_connect.htm) (Chatter, Files, Communities, Commerce, Einstein, and more). REST and Bulk API clients are on the roadmap.

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

```python
import asyncio
from salesforce_py.connect import ConnectClient

async def main():
    async with ConnectClient(
        instance_url="https://myorg.my.salesforce.com",
        access_token="<bearer-token>",
    ) as client:
        me = await client.users.get_user("me")
        print(me["displayName"])

        await client.chatter.post_feed_item(
            body="Deployment shipped cleanly.",
            subject_id="me",
        )

asyncio.run(main())
```

Install with the `connect` extra (pulls in `httpx[http2]`):

```bash
pip install "salesforce-py[connect]"
```

See [tests/connect/README.md](src/salesforce_py/connect/README.md) for the full Connect API reference — the complete list of operation namespaces, authentication patterns, more examples, error handling, ID normalisation, HTTP/2 configuration, and testing guidance.

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
