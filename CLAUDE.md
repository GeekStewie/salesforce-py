# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install all deps including dev
uv sync --extra dev

# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/sf/test_runner.py

# Run a single test by name
uv run pytest tests/sf/test_runner.py::test_cli_not_found

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

The library is structured around two parallel execution models that coexist in `src/salesforce_py/sf/`:

**Async runner** (`sf/_runner.py`): Low-level, stateless. Takes a list of args, prepends `sf`, appends `--json`, runs via `asyncio.create_subprocess_exec`. Used when callers need concurrency. `run_sync` wraps it via `asyncio.run()`.

**Sync org-bound layer** (`sf/org.py` → `sf/base.py` → `sf/operations/*`): Higher-level, stateful. Binds all commands to a specific org. This is the primary API for most users:

```
SFOrgTask          # sf/task.py — user-facing entry point, one per org
  └── SFOrg        # sf/org.py — holds credentials, builds env dict
  └── SF*Operations # sf/operations/*.py — one class per sf command group
        └── SFBaseOperations  # sf/base.py — _run() / _run_capturing() dispatch
```

`SFOrg` connects lazily: the first `_ensure_connected()` call runs `sf org display` and populates `instance_url`, `access_token`, `username`, etc. It also builds the isolated env dict (`_SF_ENV_DEFAULTS` + org credentials) passed to every subprocess — `os.environ` is never mutated.

`SFBaseOperations._run()` calls `_build_cmd()` which appends `--json`, `--target-org`, and `--api-version` (read from `sfdx-project.json` by walking up from cwd). All subprocess calls use `shell=True` with the org env.

`_run_capturing()` wraps `_run()` and emits `logging.info/error` around the call — operations use this for user-visible progress.

## Adding a new operation class

1. Create `src/salesforce_py/sf/operations/mycommand.py` subclassing `SFBaseOperations`
2. Each method calls `self._run(["mycommand", "sub", ...])` or `self._run_capturing(..., label="...")`
3. Set `include_target_org=False` for commands that are not org-scoped (e.g. alias, config)
4. Set `include_json=False` for streaming commands that don't support `--json` (e.g. `apex tail log`) — these return `{"output": "<raw stdout>"}`
5. Add the class to `sf/operations/__init__.py` and wire it into `SFOrgTask` in `sf/task.py`

## Exceptions

`SalesforcePyError` (base) → `CLINotFoundError` (sf not on PATH) → `CLIError` (non-zero exit, carries `returncode`, `stdout`, `stderr`) → `AuthError`.

`CLIError` is raised by both `_runner.run` (async path) and `SFBaseOperations._run` (sync path).

## Optional dependencies

`code-analyzer` extra adds `ruamel.yaml` for `SFCodeAnalyzerManager`. The import is guarded with a helpful `ImportError` message if the extra isn't installed.

`rest` and `bulk` extras (`httpx`, `pydantic`, `aiofiles`) are reserved for future REST/Bulk API modules — stubs exist in `src/salesforce_py/rest/` and `src/salesforce_py/bulk/`.

## Package layout

- `src/salesforce_py/sf/` — SF CLI wrapper (the only implemented module)
- `src/salesforce_py/rest/` — future REST API client (stub)
- `src/salesforce_py/bulk/` — future Bulk API client (stub)
- `src/salesforce_py/exceptions.py` — all exceptions
- `tests/sf/` — tests; `conftest.py` provides a `mock_runner` fixture patching `salesforce_py.sf._runner.run`
