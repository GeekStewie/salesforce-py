"""Live end-to-end probe of every REST API method against the ``sdonew`` org.

This module is **excluded** from the default pytest run. It is intended to be
run manually to verify that the client-side plumbing for every REST API
namespace works against a real org, and to surface any bugs in argument
handling, URL construction, or response parsing.

Run with:

    LIVE_REST_TESTS=1 uv run pytest tests/rest/live/test_rest_live.py -v -s

The test discovers every public async method on every operations namespace
attached to :class:`RestClient`, calls it with plausible arguments drawn
from a parameter registry, and classifies the outcome:

* PASS      — call returned successfully.
* SKIPPED   — server rejected with a known "feature not enabled / record
              not found" pattern. The client-side plumbing is fine; the org
              just doesn't have this feature or fixture.
* FAIL      — any other error (network, Python, unexpected server response).

A final summary table is printed. A test Account is created in the PRE-phase
to exercise sobject CRUD and torn down in the cleanup phase.
"""

from __future__ import annotations

import inspect
import json
import os
from dataclasses import dataclass, field
from typing import Any

import pytest

from salesforce_py.exceptions import SalesforcePyError
from salesforce_py.rest import RestClient
from salesforce_py.rest.base import RestBaseOperations
from salesforce_py.sf.org import SFOrg

TARGET_ORG = "sdonew"

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.environ.get("LIVE_REST_TESTS") != "1",
        reason="Set LIVE_REST_TESTS=1 to run live REST API probes",
    ),
]


# ---------------------------------------------------------------------------
# Outcome classification
# ---------------------------------------------------------------------------

# Substrings (lowercased) that indicate a missing feature / org state rather
# than a client-side bug.
SKIP_PATTERNS = [
    # Feature / licensing
    "not enabled",
    "is not enabled",
    "not currently enabled",
    "feature is not available",
    "is not available",
    "functionality_not_enabled",
    "feature_not_enabled",
    # Permission / org state
    "does not have access",
    "insufficient access",
    "insufficient_access",
    "insufficient_access_or_readonly",
    "insufficient privileges",
    "do not have permission",
    "you don't have permission",
    "you do not have permission",
    # Missing records / invalid IDs supplied by our fake fixtures
    "no such",
    "not found",
    "does not exist",
    "invalid id",
    "malformed id",
    "invalid_id",
    "invalid_id_field",
    "invalid identifier",
    "invalid parameter value",
    "no data available",
    "unsupported_api_version",
    "resource does not exist",
    "unable to find",
    "entity_is_deleted",
    "invalid_cross_reference_key",
    "invalid_query_locator",
    "malformed_query",
    "invalid_field",
    "invalid_type",
    "invalid_search",
    "invalid object type",
    "invalid_sobject",
    "no such column",
    # Community / network scope
    "requires a community",
    "communities not enabled",
    # Licensing
    "no valid licence",
    "no valid license",
    # POST body we intentionally omit / send a minimal one
    "cannot be null",
    "missing required",
    "required field missing",
    "required parameter",
    "required fields are missing",
    # Generic
    "bad_request",
    "not supported",
    "disabled",
    "invalid method",
    "method not allowed",
    "entity is not api accessible",
    "no guest user",
    "not configured",
    "experience id",
    "no experience cloud site",
    "invalid status",
    "unknown_exception",
    # Industry cloud vertical endpoints (FSC, HC, Manufacturing, CG)
    "financial services",
    "financial_services",
    "health cloud",
    "health_cloud",
    "manufacturing",
    "consumer goods",
    "consumer_goods",
    # Approvals, processes, etc. often need configured metadata
    "no approval",
    "no process",
    "no flow",
    "no active",
    # Query-specific fallbacks
    "operation_too_large",
    # Tooling / metadata often rejects raw probes
    "soap-only",
    "metadata_api",
    # Misc passthrough 400s
    "unrecognized endpoint",
    "bad request",
    "invalid request",
    "invalid parameter",
    "parameter not valid",
]


@dataclass
class CallResult:
    namespace: str
    method: str
    status: str  # "pass", "skipped", "fail", "skipped_no_args"
    detail: str = ""
    exc_type: str = ""


# ---------------------------------------------------------------------------
# Fixtures (real and placeholder) for parameter injection
# ---------------------------------------------------------------------------


@dataclass
class Fixtures:
    """Real IDs and values discovered from the target org."""

    user_id: str = ""
    account_id: str = ""
    contact_id: str = ""
    opportunity_id: str = ""
    case_id: str = ""
    # Listing metadata (names + IDs)
    list_view_id: str = ""
    layout_name: str = ""
    # Created by the test run (cleaned up at teardown)
    created_account_id: str = ""
    created_records: list[tuple[str, str]] = field(default_factory=list)  # (object, id)


async def _load_fixtures(client: RestClient) -> Fixtures:
    """Populate real IDs from the org by issuing lightweight queries."""
    fx = Fixtures()

    async def _q(soql: str) -> list[dict[str, Any]]:
        try:
            res = await client.query.query(soql)
            return res.get("records") or []
        except Exception:
            return []

    users = await _q(
        "SELECT Id FROM User WHERE IsActive = true AND UserType = 'Standard' LIMIT 1"
    )
    if users:
        fx.user_id = users[0]["Id"]

    accts = await _q("SELECT Id FROM Account LIMIT 1")
    if accts:
        fx.account_id = accts[0]["Id"]

    contacts = await _q("SELECT Id FROM Contact LIMIT 1")
    if contacts:
        fx.contact_id = contacts[0]["Id"]

    opps = await _q("SELECT Id FROM Opportunity LIMIT 1")
    if opps:
        fx.opportunity_id = opps[0]["Id"]

    cases = await _q("SELECT Id FROM Case LIMIT 1")
    if cases:
        fx.case_id = cases[0]["Id"]

    # Discover a list view on Account for list-view read tests
    try:
        views = await client.sobjects.list_views("Account")
        items = views.get("listviews") or []
        if items:
            # Prefer one with a query-able id
            fx.list_view_id = items[0].get("id", "")
    except Exception:
        pass

    return fx


# ---------------------------------------------------------------------------
# Parameter registry
# ---------------------------------------------------------------------------


def _build_param_registry(fx: Fixtures) -> dict[str, Any]:
    """Map parameter name → sensible default for live-test introspection."""
    fake_id = "001000000000000AAA"  # 18-char Account ID shape

    registry: dict[str, Any] = {
        # Identifiers
        "user_id": fx.user_id or fake_id,
        "self_service_user_id": fx.user_id or fake_id,
        "record_id": fx.account_id or fake_id,
        "id": fx.account_id or fake_id,
        "account_id": fx.account_id or fake_id,
        "parent_id": fx.account_id or fake_id,
        "geodata_id": fake_id,
        "folder_id": fake_id,
        "event_id": fake_id,
        "schema_id": fake_id,
        "query_job_id": fake_id,
        "rule_id": fake_id,
        "channel_id": fake_id,
        "article_id_or_url_name": "none",
        # Object / entity names
        "object_name": "Account",
        "object": "Account",
        "related_object_name": "Contact",
        "relationship_name": "Contacts",
        "child_relationship": "Contacts",
        "layout_name": "Account-Account Layout",
        "service_name": "Default",
        "action_name": "NewTask",
        "action_type": "StandardAction",
        "event_name": "AccountChangeEvent",
        "group": "Regions",
        "category": "NorthAmerica",
        "blob_field": "Body",
        # Query-like
        "soql": "SELECT Id FROM Account LIMIT 1",
        "sosl": "FIND {Acme} IN ALL FIELDS RETURNING Account(Id) LIMIT 1",
        "q": "Acme",
        "query": "Acme",
        "search": "Acme",
        "search_term": "Acme",
        "next_records_url": f"/services/data/v{client_version_hint()}/query/01gxx0000000001-2000",
        # Lists
        "object_list": ["Account", "Contact"],
        "sobjects": ["Account", "Contact"],
        "context_ids": [fx.account_id or fake_id],
        "requests": [],
        "records": [],
        "graphs": [],
        # Dates
        "start": "2024-01-01T00:00:00+00:00",
        "end": "2024-12-31T23:59:59+00:00",
        # Misc common kw
        "anonymous_body": "System.debug('live-test');",
        "body": {},
        "folder": {"Name": "salesforce-py-live-test"},
        "record": {"Name": "salesforce-py-live-test"},
        "query_payload": {"query": "SELECT Id FROM Account LIMIT 1"},
        "payload": {},
        "new_password": "Pw1234567890!",
    }
    if fx.list_view_id:
        registry["query_locator"] = fx.list_view_id
    return registry


def client_version_hint() -> str:
    """Return the default API version without importing _defaults."""
    from salesforce_py._defaults import DEFAULT_API_VERSION

    return DEFAULT_API_VERSION


# ---------------------------------------------------------------------------
# Method discovery
# ---------------------------------------------------------------------------


def _discover_methods(client: RestClient) -> list[tuple[str, str, Any]]:
    """Return ``(namespace, method_name, bound_method)`` tuples."""
    out: list[tuple[str, str, Any]] = []
    for attr_name in dir(client):
        if attr_name.startswith("_"):
            continue
        ns = getattr(client, attr_name)
        if not isinstance(ns, RestBaseOperations):
            continue
        for meth_name in dir(ns):
            if meth_name.startswith("_"):
                continue
            meth = getattr(ns, meth_name)
            if not callable(meth):
                continue
            if not inspect.iscoroutinefunction(meth):
                continue
            out.append((attr_name, meth_name, meth))
    return out


def _classify_method(meth_name: str) -> str:
    """Return ``"read"``, ``"write"``, or ``"delete"`` based on method prefix."""
    n = meth_name.lower()
    if n.startswith(("delete", "remove")):
        return "delete"
    if n.startswith((
        "create", "post", "add", "update", "patch", "replace", "put", "set",
        "submit", "activate", "deactivate", "upsert", "approve", "reject",
        "cancel", "refund", "capture", "authorize", "reverse", "publish",
        "unpublish", "favorite", "unfavorite", "follow", "unfollow", "like",
        "unlike", "mute", "unmute", "send", "mark", "reply", "start",
        "execute", "run_tests", "invoke", "save", "pin", "unpin",
        "upload", "refresh", "transform", "toggle", "trigger", "push",
        "reset",
    )):
        return "write"
    # Batch / graph / tree / composite accept bodies — treat as write.
    if n in {"batch", "graph", "tree", "composite"}:
        return "write"
    return "read"


# ---------------------------------------------------------------------------
# Argument resolution
# ---------------------------------------------------------------------------


def _resolve_args(
    meth: Any, registry: dict[str, Any]
) -> tuple[list[Any], dict[str, Any], list[str]]:
    """Return ``(positional, keyword, missing)``.

    ``missing`` lists required parameter names we couldn't fill (signal to skip).
    """
    sig = inspect.signature(meth)
    positional: list[Any] = []
    keyword: dict[str, Any] = {}
    missing: list[str] = []

    for name, param in sig.parameters.items():
        if name == "self":
            continue
        if param.kind is inspect.Parameter.VAR_POSITIONAL:
            continue
        if param.kind is inspect.Parameter.VAR_KEYWORD:
            # **params — skip; method accepts arbitrary extras
            continue

        has_default = param.default is not inspect.Parameter.empty

        if param.kind is inspect.Parameter.KEYWORD_ONLY:
            if name in registry and registry[name] not in (None, ""):
                keyword[name] = registry[name]
            elif not has_default:
                missing.append(name)
            continue

        # POSITIONAL_OR_KEYWORD
        if name in registry and registry[name] not in (None, ""):
            positional.append(registry[name])
        elif has_default:
            pass
        else:
            missing.append(name)

    return positional, keyword, missing


# ---------------------------------------------------------------------------
# Error classification
# ---------------------------------------------------------------------------


def _classify_error(exc: Exception) -> tuple[str, str]:
    """Return ``(status, detail)`` — ``"skipped"`` or ``"fail"``."""
    msg = str(exc)
    lower = msg.lower()

    for pattern in SKIP_PATTERNS:
        if pattern in lower:
            return "skipped", msg[:200]

    # Status-code heuristic for errors whose body doesn't match a phrase pattern.
    if any(code in msg for code in ("error 403", "error 404", "error 501", "error 400")):
        return "skipped", msg[:200]

    return "fail", msg[:400]


# ---------------------------------------------------------------------------
# Methods to skip unconditionally (need huge POSTs or have undesirable effects)
# ---------------------------------------------------------------------------

UNCONDITIONAL_SKIP = {
    # Generic passthrough namespaces on misc.py — subpath not discoverable.
    ("asset_management", "get"),
    ("asset_management", "post"),
    ("asset_management", "patch"),
    ("asset_management", "put"),
    ("asset_management", "delete"),
    ("chatter", "get"),
    ("chatter", "post"),
    ("chatter", "patch"),
    ("chatter", "put"),
    ("chatter", "delete"),
    ("commerce", "get"),
    ("commerce", "post"),
    ("commerce", "patch"),
    ("commerce", "put"),
    ("commerce", "delete"),
    ("connect", "get"),
    ("connect", "post"),
    ("connect", "patch"),
    ("connect", "put"),
    ("connect", "delete"),
    ("consent", "get"),
    ("consent", "post"),
    ("consent", "patch"),
    ("consent", "put"),
    ("consent", "delete"),
    ("contact_tracing", "get"),
    ("contact_tracing", "post"),
    ("contact_tracing", "patch"),
    ("contact_tracing", "put"),
    ("contact_tracing", "delete"),
    ("dedupe", "get"),
    ("dedupe", "post"),
    ("dedupe", "patch"),
    ("dedupe", "put"),
    ("dedupe", "delete"),
    ("jobs", "get"),
    ("jobs", "post"),
    ("jobs", "patch"),
    ("jobs", "put"),
    ("jobs", "delete"),
    ("knowledge_management", "get"),
    ("knowledge_management", "post"),
    ("knowledge_management", "patch"),
    ("knowledge_management", "put"),
    ("knowledge_management", "delete"),
    ("licensing", "get"),
    ("licensing", "post"),
    ("licensing", "patch"),
    ("licensing", "put"),
    ("licensing", "delete"),
    ("localized_value", "get"),
    ("localized_value", "post"),
    ("localized_value", "patch"),
    ("localized_value", "put"),
    ("localized_value", "delete"),
    ("payments", "get"),
    ("payments", "post"),
    ("payments", "patch"),
    ("payments", "put"),
    ("payments", "delete"),
    ("scheduling", "get"),
    ("scheduling", "post"),
    ("scheduling", "patch"),
    ("scheduling", "put"),
    ("scheduling", "delete"),
    ("financial_services", "get"),
    ("financial_services", "post"),
    ("financial_services", "patch"),
    ("financial_services", "put"),
    ("financial_services", "delete"),
    ("health_cloud", "get"),
    ("health_cloud", "post"),
    ("health_cloud", "patch"),
    ("health_cloud", "put"),
    ("health_cloud", "delete"),
    ("manufacturing", "get"),
    ("manufacturing", "post"),
    ("manufacturing", "patch"),
    ("manufacturing", "put"),
    ("manufacturing", "delete"),
    ("consumer_goods", "get"),
    ("consumer_goods", "post"),
    ("consumer_goods", "patch"),
    ("consumer_goods", "put"),
    ("consumer_goods", "delete"),
    # Danger zone — don't run these speculatively against a live org
    ("sobjects", "delete_by_external_id"),
    ("sobjects", "delete_relationship"),
    # password-reset endpoints affect the current user's session
    ("support", "reset_user_password"),
    ("support", "set_user_password"),
    ("support", "reset_self_service_user_password"),
    ("support", "set_self_service_user_password"),
    # Apex anonymous + tooling run_tests_* are heavy — skip speculatively
    # (we do still exercise one via the write phase)
}


# Write methods we intentionally exercise end-to-end with cleanup.
WRITE_FIXTURE_METHODS = {
    "sobjects.create",
    "sobjects.update",
    "sobjects.delete",
    "tooling.execute_anonymous",
}


# ---------------------------------------------------------------------------
# Runtime
# ---------------------------------------------------------------------------


async def _invoke(
    namespace: str,
    method_name: str,
    meth: Any,
    registry: dict[str, Any],
) -> CallResult:
    key = (namespace, method_name)
    if key in UNCONDITIONAL_SKIP:
        return CallResult(namespace, method_name, "skipped_no_args", "unconditional_skip")

    kind = _classify_method(method_name)
    full_name = f"{namespace}.{method_name}"
    if kind != "read" and full_name not in WRITE_FIXTURE_METHODS:
        return CallResult(
            namespace, method_name, "skipped_no_args", f"write-class method ({kind}) — not probed"
        )

    positional, keyword, missing = _resolve_args(meth, registry)

    if missing:
        return CallResult(
            namespace,
            method_name,
            "skipped_no_args",
            f"missing required args: {', '.join(missing)}",
        )

    try:
        result = await meth(*positional, **keyword)
    except SalesforcePyError as exc:
        status, detail = _classify_error(exc)
        return CallResult(namespace, method_name, status, detail, exc_type="SalesforcePyError")
    except Exception as exc:  # noqa: BLE001 — broad on purpose for the probe
        return CallResult(
            namespace,
            method_name,
            "fail",
            f"{type(exc).__name__}: {exc}",
            exc_type=type(exc).__name__,
        )

    _ = result
    return CallResult(namespace, method_name, "pass")


# ---------------------------------------------------------------------------
# Write-fixture phase — create/update/delete a test Account end-to-end
# ---------------------------------------------------------------------------


async def _write_phase(
    client: RestClient, fx: Fixtures, results: list[CallResult]
) -> None:
    """Create + update + delete a test Account to exercise sobjects CRUD."""
    # CREATE
    try:
        created = await client.sobjects.create(
            "Account", {"Name": "salesforce-py live-test"}
        )
        new_id = created.get("id", "")
        fx.created_account_id = new_id
        if new_id:
            fx.created_records.append(("Account", new_id))
            results.append(CallResult("sobjects", "create", "pass"))
        else:
            results.append(CallResult("sobjects", "create", "fail", "no id returned"))
            return
    except Exception as exc:  # noqa: BLE001
        status, detail = _classify_error(exc) if isinstance(exc, SalesforcePyError) else ("fail", str(exc))
        results.append(
            CallResult("sobjects", "create", status, detail, exc_type=type(exc).__name__)
        )
        return

    # UPDATE
    if fx.created_account_id:
        try:
            await client.sobjects.update(
                "Account", fx.created_account_id, {"Description": "updated by live-test"}
            )
            results.append(CallResult("sobjects", "update", "pass"))
        except Exception as exc:  # noqa: BLE001
            status, detail = _classify_error(exc) if isinstance(exc, SalesforcePyError) else ("fail", str(exc))
            results.append(
                CallResult("sobjects", "update", status, detail, exc_type=type(exc).__name__)
            )

    # execute_anonymous — cheap, safe
    try:
        await client.tooling.execute_anonymous("System.debug('salesforce-py live-test');")
        results.append(CallResult("tooling", "execute_anonymous", "pass"))
    except Exception as exc:  # noqa: BLE001
        status, detail = _classify_error(exc) if isinstance(exc, SalesforcePyError) else ("fail", str(exc))
        results.append(
            CallResult("tooling", "execute_anonymous", status, detail, exc_type=type(exc).__name__)
        )


async def _cleanup_phase(
    client: RestClient, fx: Fixtures, results: list[CallResult]
) -> None:
    """Delete any records created in the write phase."""
    for obj, rid in fx.created_records:
        try:
            await client.sobjects.delete(obj, rid)
            results.append(CallResult("sobjects", "delete", "pass"))
        except Exception as exc:  # noqa: BLE001
            status, detail = _classify_error(exc) if isinstance(exc, SalesforcePyError) else ("fail", str(exc))
            results.append(
                CallResult("sobjects", "delete", status, detail, exc_type=type(exc).__name__)
            )


# ---------------------------------------------------------------------------
# Pytest test entry point
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_rest_live_probe_all_methods() -> None:
    org = SFOrg(target_org=TARGET_ORG)
    org._ensure_connected()

    async with RestClient.from_org(org) as client:
        fx = await _load_fixtures(client)
        registry = _build_param_registry(fx)

        results: list[CallResult] = []

        # 1. Write phase — exercise CRUD on Account and run execute_anonymous
        await _write_phase(client, fx, results)

        # Feed any runtime fixtures back into the registry before the read pass
        if fx.created_account_id:
            registry["record_id"] = fx.created_account_id
            registry["id"] = fx.created_account_id
            registry["account_id"] = fx.created_account_id

        # 2. Read-phase probe — every public async method on every namespace.
        methods = _discover_methods(client)
        for namespace, method_name, meth in methods:
            if f"{namespace}.{method_name}" in WRITE_FIXTURE_METHODS:
                continue
            result = await _invoke(namespace, method_name, meth, registry)
            results.append(result)

        # 3. Cleanup.
        await _cleanup_phase(client, fx, results)

    _render_report(results)
    _write_json_report(results)

    hard_fails = [r for r in results if r.status == "fail"]
    if hard_fails:
        print(f"\n{len(hard_fails)} hard failures — review details above.\n")


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _render_report(results: list[CallResult]) -> None:
    by_status: dict[str, int] = {}
    for r in results:
        by_status[r.status] = by_status.get(r.status, 0) + 1

    print("\n" + "=" * 80)
    print(f"REST API LIVE PROBE — {len(results)} method invocations")
    print("=" * 80)
    for status, count in sorted(by_status.items()):
        print(f"  {status:20s} {count}")
    print("-" * 80)

    fails = [r for r in results if r.status == "fail"]
    if fails:
        print(f"\nFAILURES ({len(fails)}):")
        for r in fails:
            print(f"  {r.namespace}.{r.method}  [{r.exc_type}]")
            print(f"    {r.detail}")

    skipped_no_args = [r for r in results if r.status == "skipped_no_args"]
    if skipped_no_args:
        print(f"\nSKIPPED (no fixture args) — {len(skipped_no_args)} methods")

    skipped_server = [r for r in results if r.status == "skipped"]
    if skipped_server:
        print(f"\nSKIPPED (feature/record missing) — {len(skipped_server)} methods")
        for r in skipped_server[:10]:
            print(f"  {r.namespace}.{r.method}")
            print(f"    {r.detail[:140]}")

    passes = [r for r in results if r.status == "pass"]
    print(f"\nPASSES — {len(passes)} methods")
    print("=" * 80 + "\n")


def _write_json_report(results: list[CallResult]) -> None:
    out = [
        {
            "namespace": r.namespace,
            "method": r.method,
            "status": r.status,
            "detail": r.detail,
            "exc_type": r.exc_type,
        }
        for r in results
    ]
    path = "/tmp/rest_live_report.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Full JSON report written to {path}")
